# T3 - metoda C (prototyp): profil krawedzi brzegu wzgledem projektu, liczony wzdluz linii krawedzi.
# Wspolne: linie krawedzi z siatki projektu (R1), skan sztuczny wg wzorca krawedz_ref.py (bez zmiany znaczenia),
# detektor C (R2-R3). Program importowany tylko do odczytu.
import math
import warnings
import time
from pathlib import Path

import numpy as np
import open3d as o3d
import trimesh
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree

from stanowisko import match as M, inspect as I

PRACE = Path(r"<PC>\Desktop\Prace_test")
W5 = ["3d091aaa646d9c32", "91c1dea0b2060be3", "a823e3b4aff6b60e", "d8d245b4c01ae11b", "ea47d2adbe45456e"]
PROJ_STROJENIE = ["3d091aaa646d9c32", "91c1dea0b2060be3"]
PROJ_OCENA = ["a823e3b4aff6b60e", "d8d245b4c01ae11b", "ea47d2adbe45456e"]
KATY = [float(a) for a in range(0, 360, 36)]
KATY_STROJENIE = [0.0, 72.0, 144.0, 216.0, 288.0]
KATY_OCENA = [36.0, 108.0, 180.0, 252.0, 324.0]
ROZMIARY = [0.05, 0.08, 0.10, 0.12, 0.15, 0.20, 0.30, 0.40]
MIEJSCA = ("srodek", "zewn", "wewn")
KONF = {"K_a": (0.05, 0.01), "K_b": (0.05, 0.03), "K_c": (0.03, 0.03)}

# --- R1: linie krawedzi -------------------------------------------------------------------------------
KROK_KATA_DEG = 0.5      # przekroje promieniowe (polplaszczyzny zawierajace os z) co tyle
COS_GORA = 0.64          # odcinek przekroju "plaskiej krawedzi": normalna 2D w granicach ~50 st. od +z
KROK_STACJI = 0.05       # mm: stacje wzdluz linii krawedzi
SKOK_MAX = 0.4           # mm: skok linii miedzy sasiednimi przekrojami powyzej tego = przekroj nieudany


def _przekroj(sub, th):
    """Przekroj siatki polplaszczyzna pod katem th: odcinki 2D (r, z) i normalne 2D."""
    er = np.array([math.cos(th), math.sin(th), 0.0])
    npl = np.array([-math.sin(th), math.cos(th), 0.0])
    segs, fi = trimesh.intersections.mesh_plane(sub, npl, np.zeros(3), return_faces=True)
    if len(segs) == 0:
        return None
    R = segs @ er
    Z = segs[:, :, 2]
    keep = R.min(1) > 0.2
    if keep.sum() < 4:
        return None
    s2 = np.stack([R, Z], -1)[keep]
    n3 = sub.face_normals[fi[keep]]
    n2 = np.stack([n3 @ er, n3[:, 2]], -1)
    n2 /= np.maximum(np.linalg.norm(n2, axis=1, keepdims=True), 1e-12)
    return s2, n2


ANG_ROG_DEG = 25.0       # koniec plaskiej krawedzi: normalna odcinka odchylona o tyle od sredniej normalnej krawedzi
DL_SCIANY = 0.10         # mm: odcinek sciany za naroznikiem: z niego normalna sciany, jego koniec = linia O2 / I2 (0,1 mm w dol sciany)
W_NZ, W_DZ = 0.7, 0.1    # linia W (jak wzorzec brzeg(): nw) - najdalej do srodka punkt skierowany do gory (nz > 0,7) do 0,1 mm pod szczytem
MED_OKNO = 4             # filtr medianowy po przekrojach (+- tyle przekrojow)
ODST_MED = 0.15          # mm: przekroj odstajacy od mediany sasiadow o tyle = nieudany dla tej linii


def _naroza(s2, n2, slad=None):
    """Plaska krawedz w przekroju: od najwyzszego odcinka idziemy po lamanej przekroju w obie strony, dopoki normalna
    odcinka nie odchyli sie o > ANG_ROG_DEG od sredniej normalnej przebytej krawedzi (naroznik = ostre zalamanie
    albo suma lagodnych). Zwraca [O, I, (dwusieczna, kat) O, (...) I, W] w 2D albo None; O = wiekszy r.
    W = koniec ciagu odcinkow o nz > W_NZ do W_DZ pod szczytem po stronie wewnetrznej (definicja wzorca brzeg())."""
    pts = s2.reshape(-1, 2)
    klucze, inv = np.unique(np.round(pts, 5), axis=0, return_inverse=True)
    inv = inv.ravel().reshape(-1, 2)
    dl = np.linalg.norm(s2[:, 1] - s2[:, 0], axis=1)
    przy = {}
    for i, (a, b) in enumerate(inv):
        przy.setdefault(int(a), []).append(i)
        przy.setdefault(int(b), []).append(i)
    tf = n2[:, 1] > COS_GORA
    wezel0 = int(np.argmax(klucze[:, 1]))
    ztop = float(klucze[wezel0, 1])
    kand = [i for i in przy[wezel0] if tf[i]]
    if not kand:
        return None
    gora = max(kand, key=lambda i: n2[i, 1])
    cosmax = math.cos(math.radians(ANG_ROG_DEG))

    def nastepny(cur, wezel):
        nast = [i for i in przy[wezel] if i != cur]
        return nast[0] if len(nast) == 1 else None

    def drugi(seg, wezel):
        return int(inv[seg, 1] if inv[seg, 0] == wezel else inv[seg, 0])

    konce = []
    for kier in (0, 1):
        ref = n2[gora] * max(dl[gora], 1e-4)
        cur, wezel, przeb = gora, int(inv[gora, kier]), 0.0
        while True:
            nxt = nastepny(cur, wezel)
            if nxt is None or przeb > 2.0:
                nxt = None
                break
            rn = ref / np.linalg.norm(ref)
            if float(n2[nxt] @ rn) < cosmax:
                break
            ref = ref + n2[nxt] * max(dl[nxt], 1e-4)
            przeb += dl[nxt]
            cur = nxt
            if slad is not None:
                slad.append((kier, nxt))
            wezel = drugi(nxt, wezel)
        X = klucze[wezel]
        nt = ref / np.linalg.norm(ref)
        rog = None
        X2 = X
        if nxt is not None:
            sw, c2, w2, d2, s_ = np.zeros(2), cur, wezel, 0.0, nxt
            while s_ is not None and d2 < DL_SCIANY:
                sw += n2[s_] * max(dl[s_], 1e-4)
                d2 += dl[s_]
                w2 = drugi(s_, w2)
                c2 = s_
                s_ = nastepny(c2, w2)
            b = sw / max(np.linalg.norm(sw), 1e-12)
            bis = -(nt + b)
            bis /= max(np.linalg.norm(bis), 1e-9)
            alfa = math.pi - math.acos(float(np.clip(nt @ b, -1, 1)))
            rog = (bis, alfa)
            X2 = klucze[w2]
        # linia W w tym kierunku
        cur, wezel, przeb, Wmin = gora, int(inv[gora, kier]), 0.0, klucze[int(inv[gora, kier])]
        while przeb < 2.0:
            nxt = nastepny(cur, wezel)
            if nxt is None or n2[nxt, 1] <= W_NZ:
                break
            w_ = drugi(nxt, wezel)
            if klucze[w_, 1] < ztop - W_DZ:
                break
            przeb += dl[nxt]
            cur, wezel = nxt, w_
            if klucze[w_, 0] < Wmin[0]:
                Wmin = klucze[w_]
        konce.append((X, rog, Wmin, X2))
    if konce[0][0][0] >= konce[1][0][0]:
        (O, rO, _, O2), (Iw, rI, W, I2) = konce
    else:
        (Iw, rI, W, I2), (O, rO, _, O2) = konce
    W = W if W[0] <= Iw[0] + 1e-9 else Iw
    return [O, Iw, rO, rI, W, O2, I2]


def _med_kolowa(x, k):
    st = np.stack([np.roll(x, o) for o in range(-k, k + 1)], 0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return np.nanmedian(st, axis=0)


def linie_krawedzi(pr, krok_deg=KROK_KATA_DEG):
    """Linie naroznika zewnetrznego (O), wewnetrznego (I), linii W (definicja wzorca) i srodka plaskiej krawedzi
    S = (O + W) / 2 jako zamkniete lamane ze stacjami co KROK_STACJI; na stacji: punkt, styczna, dwusieczna
    do materialu (3D, tylko O i I), kat naroznika."""
    m = pr.siatka
    katy = np.radians(np.arange(0.0, 360.0, krok_deg))
    rek = np.full((len(katy), 18), np.nan)  # rO zO rI zI bOr bOz bIr bIz aO aI - szer rW zW rO2 zO2 rI2 zI2
    for i, th in enumerate(katy):
        p = _przekroj(m, th)
        if p is None:
            continue
        w = _naroza(*p)
        if w is None:
            continue
        O, Iw, iO, iI, W, O2, I2 = w
        rek[i, 0:2], rek[i, 2:4], rek[i, 12:14], rek[i, 14:16], rek[i, 16:18] = O, Iw, W, O2, I2
        if iO is not None:
            rek[i, 4:6], rek[i, 8] = iO[0], iO[1]
        if iI is not None:
            rek[i, 6:8], rek[i, 9] = iI[0], iI[1]
    ok0 = np.isfinite(rek[:, 0])
    oki = {}
    idx = np.arange(len(katy))
    R2 = rek.copy()
    for nazwa, (ir, iz, inne) in {"O": (0, 1, (4, 5, 8)), "I": (2, 3, (6, 7, 9)), "W": (12, 13, ()), "O2": (14, 15, ()), "I2": (16, 17, ())}.items():
        mr, mz = _med_kolowa(rek[:, ir], MED_OKNO), _med_kolowa(rek[:, iz], MED_OKNO)
        ok = ok0 & (np.hypot(rek[:, ir] - mr, rek[:, iz] - mz) <= ODST_MED)
        oki[nazwa] = ok
        for j in (ir, iz) + tuple(inne):
            dob = ok & np.isfinite(rek[:, j])
            if dob.sum() < 4:
                continue
            xp = np.concatenate([idx[dob] - len(katy), idx[dob], idx[dob] + len(katy)])
            R2[:, j] = np.interp(idx, xp, np.tile(rek[dob, j], 3))
    R2[:, 11] = np.hypot(R2[:, 0] - R2[:, 2], R2[:, 1] - R2[:, 3])
    linie = {}
    er = np.stack([np.cos(katy), np.sin(katy), np.zeros_like(katy)], 1)
    ez = np.array([0.0, 0.0, 1.0])
    for nazwa, (ir, iz, ibr, ibz, ia) in {"O": (0, 1, 4, 5, 8), "I": (2, 3, 6, 7, 9)}.items():
        X = er * R2[:, ir:ir + 1] + ez * R2[:, iz:iz + 1]
        B = er * R2[:, ibr:ibr + 1] + ez * R2[:, ibz:ibz + 1]
        linie[nazwa] = (X, B, R2[:, ia], oki[nazwa])
    Xw = er * R2[:, 12:13] + ez * R2[:, 13:14]
    Bd = np.tile(-ez, (len(katy), 1))  # W i S: do materialu = w dol (przyblizenie, nieuzywane przez detektor)
    linie["W"] = (Xw, Bd, np.full(len(katy), math.pi), oki["W"])
    linie["S"] = ((linie["O"][0] + Xw) / 2, Bd, np.full(len(katy), math.pi), oki["O"] & oki["W"])
    for nz_, (ir, iz) in {"O2": (14, 15), "I2": (16, 17)}.items():
        linie[nz_] = (er * R2[:, ir:ir + 1] + ez * R2[:, iz:iz + 1], Bd, np.full(len(katy), math.pi), oki[nz_])
    out = {}
    for nazwa, (X, B, A, ok) in linie.items():
        Xz = np.vstack([X, X[:1]])
        dl = np.linalg.norm(np.diff(Xz, axis=0), axis=1)
        s = np.concatenate([[0], np.cumsum(dl)])
        L = float(s[-1])
        K = max(8, int(round(L / KROK_STACJI)))
        sk = np.arange(K) * L / K
        Xk = np.stack([np.interp(sk, s, Xz[:, j]) for j in range(3)], 1)
        Bz = np.vstack([B, B[:1]])
        Bk = np.stack([np.interp(sk, s, Bz[:, j]) for j in range(3)], 1)
        Bk /= np.maximum(np.linalg.norm(Bk, axis=1, keepdims=True), 1e-9)
        Ak = np.interp(sk, s, np.concatenate([A, A[:1]]))
        okk = np.interp(sk, s, np.concatenate([ok, ok[:1]]).astype(float)) > 0.5
        Tk = np.roll(Xk, -1, 0) - np.roll(Xk, 1, 0)
        Tk /= np.maximum(np.linalg.norm(Tk, axis=1, keepdims=True), 1e-9)
        out[nazwa] = {"X": Xk, "T": Tk, "B": Bk, "alfa": Ak, "ok": okk, "s": sk, "L": L}
    out["_przekroje"] = {"udane": int(ok0.sum()), "wszystkie": int(len(katy)), "szer": R2[:, 11], "katy": katy,
                         "ok": ok0, "ok_linii": {k: int(v.sum()) for k, v in oki.items()},
                         "szerW": np.hypot(R2[:, 0] - R2[:, 12], R2[:, 1] - R2[:, 13])}
    return out


# --- skan sztuczny: wzorzec krawedz_ref.py (bez zmiany znaczenia) ---------------------------------------
def dk(a, b):
    return (a - b + 180) % 360 - 180


class Skaner:
    """P0/N0 = rownomierna probka projektu x 1,22 (uklad puli), brzeg() i skan() jak w krawedz_ref.py."""

    def __init__(self, pr, odstep, P0=None, N0=None, seed_probki=1):
        self.pr, self.odstep = pr, odstep
        m = pr.siatka
        if P0 is None:
            ile = int(m.area / odstep**2)
            P0, fid = trimesh.sample.sample_surface(m, ile, seed=seed_probki)
            P0 = np.asarray(P0)
            N0 = np.asarray(m.face_normals[fid])
        self.P0, self.N0 = P0, N0
        self.ang0 = np.degrees(np.arctan2(P0[:, 1], P0[:, 0]))
        self.R0 = np.linalg.norm(P0[:, :2], axis=1)

    def w_materiale(self, Q):
        sd = self.pr.scena.compute_signed_distance(o3d.core.Tensor(np.ascontiguousarray(Q, dtype=np.float32))).numpy()
        return sd < 0

    def brzeg(self, kat):
        P0, N0, ang0, R0 = self.P0, self.N0, self.ang0, self.R0
        rad = np.array([math.cos(math.radians(kat)), math.sin(math.radians(kat)), 0.0])
        w = np.abs(dk(ang0, kat)) < 1.5
        zt = P0[w, 2].max()
        szczyt = P0[w & (P0[:, 2] > zt - 0.03)].mean(0)
        w2 = (np.abs(dk(ang0, kat)) < 3) & (P0[:, 2] < zt - 0.15) & (P0[:, 2] > zt - 0.25)
        nr = N0[w2] @ rad
        Rz, Rw = R0[w2][nr > 0.3], R0[w2][nr < -0.3]
        grub = float(Rz.mean() - Rw.mean()) if len(Rz) and len(Rw) else float("nan")
        w3 = (np.abs(dk(ang0, kat)) < 3) & (P0[:, 2] > zt - 0.1) & (N0[:, 2] > 0.7)
        szer = float(np.ptp(R0[w3])) if w3.sum() > 3 else 0.0
        w4 = (np.abs(dk(ang0, kat)) < 1.5) & (P0[:, 2] > zt - 0.1) & (N0[:, 2] > 0.7)
        i4 = np.flatnonzero(w4)
        nz = P0[i4[np.argmax(R0[i4])]] if len(i4) else szczyt
        nw = P0[i4[np.argmin(R0[i4])]] if len(i4) else szczyt
        return szczyt, rad, grub, szer, nz, nw, int(len(i4))

    def skan(self, c, r, sigma, seed):
        """Jak krawedz_ref.skan; zwraca tez maske punktow ukruszenia."""
        P0, N0, ODSTEP = self.P0, self.N0, self.odstep
        g = np.random.default_rng(seed)
        if r is None:
            P, N, ch = P0, N0, np.zeros(len(P0), bool)
            zost = np.ones(len(P0), bool)
        else:
            zost = np.linalg.norm(P0 - c, axis=1) >= r
            k = max(60, int(4 * math.pi * r * r / ODSTEP**2 * 1.0))
            v = g.normal(size=(k * 4, 3))
            v /= np.linalg.norm(v, axis=1, keepdims=True)
            Q = c + r * v
            wm = self.w_materiale(Q)
            Q, v = Q[wm][:k * 4], v[wm][:k * 4]
            pole = 4 * math.pi * r * r * wm.mean()
            n = int(round(pole / ODSTEP**2))
            Q, v = Q[:n], v[:n]
            P = np.concatenate([P0[zost], Q])
            N = np.concatenate([N0[zost], -v])
            ch = np.concatenate([np.zeros(int(zost.sum()), bool), np.ones(len(Q), bool)])
        P = P + N * g.normal(0, sigma, (len(P), 1))
        return P, N, ch, zost


# --- detektor C -----------------------------------------------------------------------------------------
SKALE = [0.06, 0.08, 0.10, 0.13, 0.17, 0.22, 0.29, 0.38]   # promien badanego ukruszenia [mm]
RHO_K = 1.15             # kula okna = RHO_K x skala (powierzchnia czaszy ukruszenia lezy w odleglosci ~skala od srodka)
REF_OD, REF_DO = 0.3, 1.0  # mm: odniesienie lokalne = mediana stacji tej linii w odleglosci 0,3-1,0 mm po obu stronach
N_MIN = 5                # najmniej punktow w oknie
UDZIAL_DANYCH = 0.4      # okno z < 40 % oczekiwanej liczby punktow = brak danych (nigdy alarm)
F_MIN = 0.10             # minimalna srednia odchylka (po odjeciu odniesienia) jako ulamek skali - podloga fizyczna
Z_ZAPIS = 3.0            # kandydaci od tego z zapisywani (progi decyzji dobierane pozniej, na danych do strojenia)


class DetektorC:
    def __init__(self, pr, linie, skale=SKALE):
        self.pr = pr
        self.skale = list(skale)
        self.nazwy = ["O", "I", "W", "S", "O2", "I2"]
        X, lin, kk, ok = [], [], [], []
        self.K = {}
        for j, n in enumerate(self.nazwy):
            L = linie[n]
            X.append(L["X"])
            lin.append(np.full(len(L["X"]), j))
            kk.append(np.arange(len(L["X"])))
            ok.append(L["ok"])
            self.K[n] = len(L["X"])
        self.X = np.vstack(X)
        self.lin = np.concatenate(lin)
        self.kk = np.concatenate(kk)
        self.ok_geom = np.concatenate(ok)
        self.drzewo_st = cKDTree(self.X)
        self.rho = np.array(self.skale) * RHO_K
        self.rho_max = float(self.rho.max())
        # pole powierzchni projektu w kazdym oknie (gesta probka projektu blisko linii)
        m = pr.siatka
        dcen, _ = self.drzewo_st.query(m.triangles_center, distance_upper_bound=self.rho_max + 0.3)
        sub = trimesh.Trimesh(m.vertices, m.faces[np.isfinite(dcen)], process=False)
        krok = 0.015
        ile = int(sub.area / krok**2)
        Pd, _ = trimesh.sample.sample_surface(sub, ile, seed=7)
        td = cKDTree(np.asarray(Pd))
        a1 = sub.area / ile
        self.pole = np.stack([np.asarray(td.query_ball_point(self.X, r, return_length=True)) * a1 for r in self.rho], 1)  # (Kst, nskal)
        self.pole_calk = float(m.area)
        # przesuniecia stacji dla odniesienia lokalnego
        o1, o2 = int(round(REF_OD / KROK_STACJI)), int(round(REF_DO / KROK_STACJI))
        self.przes = np.array([o for o in range(-o2, o2 + 1) if abs(o) >= o1])
        self.bias = None

    def kalibruj(self, pr, odstep, sigma, n=24):
        """Kalibracja na samym projekcie (przed skanem): n sztucznych skanow calej korony z INNEJ probki punktow
        (seed_probki=2) i ziaren 900+; srednia odchylka skorygowana na stacji = obciazenie geometryczne miary
        (naroza wklesle / wypukle obcinaja szum), odejmowane potem od kazdego skanu."""
        sk = Skaner(pr, odstep, seed_probki=2)
        mk = self.maska_obszaru(sk.P0)
        acc = []
        self.bias = None
        for i in range(n):
            P, N, ch, zost = sk.skan(None, None, sigma, 900 + i)
            self._kor_ost = None
            self(P[mk], len(P))
            acc.append(self._kor_ost)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            b = np.nanmean(np.stack(acc, 0), axis=0)
        self.bias = np.nan_to_num(b, nan=0.0)

    def maska_obszaru(self, P):
        d, _ = self.drzewo_st.query(P, distance_upper_bound=self.rho_max + 0.06)
        return np.isfinite(d)

    def __call__(self, Pc, n_wszystkich, z_zapis=Z_ZAPIS):
        """Pc: punkty skanu (uklad puli) juz przyciete do obszaru linii; n_wszystkich: liczba punktow calego skanu."""
        t0 = time.time()
        dev = -I.odchylki(Pc, self.pr)          # > 0 = skan pod powierzchnia projektu (brak materialu)
        med = float(np.median(dev))
        sig = float(1.4826 * np.median(np.abs(dev - med)))
        sig = max(sig, 0.003)
        gest = n_wszystkich / self.pole_calk     # punktow skanu na mm2
        tp = cKDTree(Pc)
        pary = self.drzewo_st.sparse_distance_matrix(tp, self.rho_max, output_type="ndarray")
        ri, ci, di = pary["i"], pary["j"], pary["v"]
        Kst = len(self.X)
        ns = len(self.skale)
        nn = np.zeros((Kst, ns))
        sr = np.full((Kst, ns), np.nan)
        for a, r in enumerate(self.rho):
            w = di <= r
            n = np.bincount(ri[w], minlength=Kst).astype(float)
            s = np.bincount(ri[w], weights=dev[ci[w]], minlength=Kst)
            nn[:, a] = n
            with np.errstate(invalid="ignore", divide="ignore"):
                sr[:, a] = np.where(n > 0, s / np.maximum(n, 1), np.nan)
        n_ocz = self.pole * gest
        wazne = (nn >= N_MIN) & (nn >= UDZIAL_DANYCH * n_ocz) & self.ok_geom[:, None]
        srw = np.where(wazne, sr, np.nan)
        ref = np.full_like(sr, np.nan)
        off = 0
        for n in self.nazwy:
            K = self.K[n]
            blok = srw[off:off + K]
            stos = np.stack([np.roll(blok, -o, axis=0) for o in self.przes], 0)
            with np.errstate(all="ignore"):
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", RuntimeWarning)
                    ref[off:off + K] = np.nanmedian(stos, axis=0)
            off += K
        kor = sr - ref
        self._kor_ost = kor.copy()
        if self.bias is not None:
            kor = kor - self.bias
        z = kor * np.sqrt(nn) / sig
        podloga = kor >= F_MIN * np.array(self.skale)[None, :]
        dobre = wazne & np.isfinite(z) & podloga
        zz = np.where(dobre, z, -np.inf)
        z_max = float(zz.max()) if np.isfinite(zz).any() else 0.0
        idx = np.argwhere(zz >= z_zapis)
        wykrycia = []
        if len(idx):
            zv = zz[idx[:, 0], idx[:, 1]]
            por = np.argsort(-zv)
            idx, zv = idx[por], zv[por]
            wolne = np.ones(len(idx), bool)
            Xi = self.X[idx[:, 0]]
            for q in range(len(idx)):
                if not wolne[q]:
                    continue
                st, a = idx[q]
                rc = 0.25 + 1.2 * self.skale[a]
                dd = np.linalg.norm(Xi - Xi[q], axis=1)
                czl = wolne & (dd <= rc)
                wolne &= ~czl
                ta_linia = czl & (self.lin[idx[:, 0]] == self.lin[st])
                zasieg = float(np.ptp(self.kk[idx[ta_linia, 0]]) * KROK_STACJI) if ta_linia.sum() > 1 else 0.0
                wykrycia.append({"x": round(float(self.X[st, 0]), 4), "y": round(float(self.X[st, 1]), 4), "z": round(float(self.X[st, 2]), 4),
                                 "zst": round(float(zv[q]), 2), "skala": self.skale[a], "linia": self.nazwy[self.lin[st]],
                                 "kor": round(float(kor[st, a]), 4), "n": int(nn[st, a]), "obj": round(float(kor[st, a] * self.pole[st, a]), 6),
                                 "zasieg": round(zasieg, 3), "czlonow": int(czl.sum())})
        info = {"sigma_est": round(sig, 4), "z_max": round(z_max, 2), "punktow_obszaru": int(len(Pc)),
                "udzial_waznych": round(float(wazne[:, 1].mean()), 4), "czas_s": round(time.time() - t0, 3)}
        return wykrycia, info


def wczytaj_pule():
    return M.Pula(PRACE, 1.22)
