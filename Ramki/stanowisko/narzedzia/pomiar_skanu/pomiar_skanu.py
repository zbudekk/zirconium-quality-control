r"""pomiar_skanu - T10: wlasciwosci prawdziwego skanu (STL / PLY ze skanera) na dzien testu skanera.

Osobny skrypt poza programem (program `stanowisko` importowany tylko do odczytu: match.Projekt / Pula / dopasuj).

Wejscie: siatka skanu (STL albo PLY; wierzcholki + trojkaty, normalne pliku ignorowane) - najlepiej cala plytka
z 1-3 koronami, ktorych projekty leza w podanym folderze; dziala tez sama plytka (bez koron) albo sama korona.
Wyjscie: raport tekstowy (ekran + <wyj>\raport.txt) i <wyj>\pomiar.json:
  1. plaska czesc plytki: sredni odstep punktow (d = sqrt(pole / liczba wierzcholkow)), sigma szumu,
     funkcja autokorelacji i dlugosc korelacji szumu (model: sigma_n^2 [h=0] + sigma_k^2 exp(-h^2/L^2)),
  2. kazda korona: projekt z puli (dopasowanie programu), blad skali wzgledem projektu x wspolczynnik
     (ICP ze skala; izotropowo, osobno xy i z, z przesunieciem powierzchni d0), odstep punktow na scianie i na krawedzi,
     sigma na scianie i na krawedzi, cofniecie naroznikow krawedzi brzegu (-> rownowazny promien zaokraglenia),
     udzial dlugosci krawedzi brzegu bez danych i dlugosci przerw,
  3. (opcja --powtorka SKAN2) powtarzalnosc: drugi skan tej samej plytki bez ruszania.

Uzycie (PC / laptop z programem):  pomiar_skanu.py SKAN.stl [--projekty FOLDER] [--wspolczynnik 1.22] [--wyj KATALOG]
                                     [--powtorka SKAN2.stl] [--bez-plytki]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import open3d as o3d
import trimesh
from scipy.optimize import curve_fit
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import c_wspolne as CW  # noqa: E402  (linie krawedzi z projektu, kopia z T3)
from stanowisko import match as M, ustawienia as U  # noqa: E402

PROG_PLASZCZYZNY = 0.12   # mm: wierzcholek nalezy do plaszczyzny plytki
KAT_PLASZCZYZNY = 30.0    # st.: normalna trojkata plaszczyzny (luzno: drobne trojkaty skanu maja zaszumione normalne)
MARGINES_PLASKI = 0.4     # mm: wierzcholki plaskie blizej niz tyle od nieplaskich - pominiete (zaokraglone brzegi otworow)
KOMORKA = 4.0             # mm: komorka do odjecia ksztaltu plytki (wielomian 2. stopnia)
H_MAX = 1.0               # mm: zasieg autokorelacji
KROK_H = 0.02             # mm: przedzial autokorelacji
NAD_PLYTKA = 0.3          # mm: wierzcholki wyzej niz tyle nad plytka = prace
EPS_PRACY = 0.5           # mm: laczenie wierzcholkow pracy w fragment (jak plate.EPS_DBSCAN)
OKNO_PROMIENIA = (-0.10, 0.30)  # mm: dopuszczalne cofniecie naroznika (promien z zewnatrz wzdluz dwusiecznej)
START_PROMIENIA = 0.25    # mm: start promienia przed naroznikiem
R_GESTOSCI = 0.12         # mm: promien zliczania wierzcholkow wokol stacji krawedzi
PROG_GESTOSCI = 0.3       # stacja bez danych: wierzcholkow < tyle x mediana stacji tej linii (albo brak powierzchni)
PROMIENIE_BPA = (0.8, 1.2, 1.6, 2.4, 3.2)  # x odstep: promienie ball pivoting (siatka skanu idealnego, walidacja)
ALFA_MAX_DEG = 150.0     # stacje z katem naroznika powyzej tego nie licza sie do promienia (prawie brak naroznika)


# ---------------------------------------------------------------------------------------------------------
def wczytaj_siatke(sciezka: Path) -> trimesh.Trimesh:
    m = trimesh.load(str(sciezka), force="mesh", process=True)  # process: scala zdublowane wierzcholki STL
    m.remove_unreferenced_vertices()
    return m


def pole_wierzcholkow(m: trimesh.Trimesh, V: np.ndarray | None = None) -> np.ndarray:
    """Pole przypadajace na wierzcholek (1/3 pol trojkatow przyleglych). ``V`` = wierzcholki odszumione (te same
    trojkaty): pole szumnej siatki jest zawyzone przez szorstkosc (szum 0,02 przy odstepie 0,03: +60 %)."""
    if V is None:
        af = m.area_faces
    else:
        T = V[m.faces]
        af = 0.5 * np.linalg.norm(np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]), axis=1)
    a = np.zeros(len(m.vertices))
    for k in range(3):
        np.add.at(a, m.faces[:, k], af / 3.0)
    return a


def odstep(pole_w: np.ndarray, maska: np.ndarray) -> float:
    """Sredni odstep punktow w sensie protokolu: liczba punktow = pole / d^2."""
    n = int(maska.sum())
    return float(math.sqrt(pole_w[maska].sum() / n)) if n else float("nan")


def robust_std(x: np.ndarray) -> float:
    x = np.asarray(x)
    if len(x) == 0:
        return float("nan")
    return float(1.4826 * np.median(np.abs(x - np.median(x))))


# ---------------------------------------------------------------------------------------------------------
# 1. plaszczyzna plytki
# ---------------------------------------------------------------------------------------------------------
def poziomowanie(m: trimesh.Trimesh, rng) -> tuple[np.ndarray | None, dict]:
    """4x4 obracajaca plaszczyzne plytki na z = 0 (normalna do skanera = +z). None, gdy brak plaskiej czesci."""
    P, fid = trimesh.sample.sample_surface(m, 400000, seed=int(rng.integers(2**31)))
    P = np.asarray(P)
    NF = np.asarray(m.face_normals[fid])
    pc = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(P))
    o3d.utility.random.seed(int(rng.integers(2**31)))
    model, inl = pc.segment_plane(distance_threshold=0.1, ransac_n=3, num_iterations=3000)
    n = np.asarray(model[:3], dtype=float)
    d = -float(model[3])
    cmax = math.cos(math.radians(KAT_PLASZCZYZNY))
    for _ in range(3):
        bl = (np.abs(P @ n - d) < 0.1) & (np.abs(NF @ n) > cmax)
        if bl.sum() < 1000:
            return None, {"plaszczyzna": "brak", "udzial_pola": float(bl.mean())}
        Q = P[bl]
        c = Q.mean(0)
        _, _, vt = np.linalg.svd(Q - c, full_matrices=False)
        n = vt[2]
        d = float(c @ n)
    udzial = float((np.abs(P @ n - d) < 0.1).mean())
    if udzial < 0.05 or m.area * udzial < 20.0:
        return None, {"plaszczyzna": "za_mala", "udzial_pola": udzial}
    # strona: normalne trojkatow plaszczyzny patrza do skanera (siatka skanu jest powierzchnia widziana z kamery)
    if float((NF[bl] @ n).mean()) < 0:
        n, d = -n, -d
    z = np.array([0.0, 0.0, 1.0])
    v = np.cross(n, z)
    s, cc = np.linalg.norm(v), float(n @ z)
    R = np.eye(3)
    if s > 1e-12:
        K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
        R = np.eye(3) + K + K @ K * ((1 - cc) / s**2)
    T = np.eye(4)
    T[:3, :3] = R
    T[2, 3] = -d
    return T, {"plaszczyzna": "ok", "udzial_pola": round(udzial, 4), "pole_plaskie_mm2": round(float(m.area * udzial), 1)}


def _wielomian2(x, y):
    return np.stack([np.ones_like(x), x, y, x * x, x * y, y * y], 1)


def autokorelacja(P: np.ndarray, r: np.ndarray, komorki: np.ndarray, rng, d_eq: float = 0.05, par_max: float = 8e6) -> dict:
    """Empiryczna autokorelacja reszt r (w obrebie komorek) w przedzialach odleglosci co KROK_H do H_MAX.
    Liczba par ograniczona do ok. ``par_max`` (losowe centra w kazdej komorce)."""
    kraw = np.arange(0.0, H_MAX + KROK_H, KROK_H)
    s = np.zeros(len(kraw) - 1)
    n = np.zeros(len(kraw) - 1)
    uk = np.unique(komorki)
    if len(uk) > 60:
        uk = rng.choice(uk, 60, replace=False)
    sasiadow = math.pi * H_MAX**2 / d_eq**2
    centrow = max(50, int(par_max / (len(uk) * sasiadow)))
    for k in uk:
        idx = np.flatnonzero(komorki == k)
        if len(idx) < 200:
            continue
        Q, rq = P[idx, :2], r[idx]
        dr = cKDTree(Q)
        c = rng.choice(len(idx), min(centrow, len(idx)), replace=False)
        sas = dr.query_ball_point(Q[c], H_MAX)
        ii = np.repeat(c, [len(x) for x in sas])
        jj = np.concatenate([np.asarray(x, dtype=int) for x in sas])
        w = ii != jj
        ii, jj = ii[w], jj[w]
        h = np.linalg.norm(Q[ii] - Q[jj], axis=1)
        b = np.minimum((h / KROK_H).astype(int), len(s) - 1)
        s += np.bincount(b, weights=rq[ii] * rq[jj], minlength=len(s))
        n += np.bincount(b, minlength=len(s))
    var = float(np.mean(r**2))
    h_sr = (kraw[:-1] + kraw[1:]) / 2
    with np.errstate(invalid="ignore", divide="ignore"):
        C = np.where(n > 0, s / np.maximum(n, 1) / var, np.nan)
    return {"h": h_sr, "C": C, "n": n}


def model_korelacji(h, a, L):
    return a * np.exp(-(h / L) ** 2)


def dopasuj_korelacje(ak: dict, d_eq: float) -> dict:
    h, C, n = ak["h"], ak["C"], ak["n"]
    w = np.isfinite(C) & (n > 50) & (h >= 0.8 * d_eq)
    if w.sum() < 5:
        return {"udzial_skorelowany": None, "L_mm": None}
    blisko = w & (h <= 0.3)
    if not blisko.any() or float(np.nanmax(C[blisko])) < 0.05:
        # brak mierzalnej korelacji od odleglosci ~ odstepu punktow: szum niezalezny (albo korelacja krotsza niz odstep)
        return {"udzial_skorelowany": 0.0, "L_mm": None, "h_1e_bez_modelu_mm": None, "uwaga": "brak korelacji powyzej odstepu punktow"}
    try:
        (a, L), _ = curve_fit(model_korelacji, h[w], C[w], p0=(0.5, 0.15), bounds=([0.0, 0.005], [1.0, 3.0]), sigma=1 / np.sqrt(n[w]))
    except RuntimeError:
        return {"udzial_skorelowany": None, "L_mm": None}
    # bez modelu: pierwsza odleglosc, gdzie C spada ponizej C(pierwszy przedzial)/e
    c0 = C[w][0]
    pon = np.flatnonzero(C[w] < c0 / math.e)
    out = {"udzial_skorelowany": float(a), "L_mm": float(L), "h_1e_bez_modelu_mm": float(h[w][pon[0]]) if len(pon) else None}
    if L < d_eq:
        out["uwaga"] = "L krotsze niz odstep punktow - korelacja niepewna (np. z budowy siatki)"
    return out


def plaska_czesc(m: trimesh.Trimesh, rng) -> dict:
    """m wypoziomowana (plytka na z = 0). Odstep, sigma, autokorelacja."""
    V = np.asarray(m.vertices)
    VN = np.array(m.vertex_normals)
    Vrz = V.copy()
    Vrz[:, 2] = 0.0  # pole rzutu na plaszczyzne plytki (bez szorstkosci szumu)
    pw = pole_wierzcholkow(m, Vrz)
    plaski = np.abs(V[:, 2]) < PROG_PLASZCZYZNY  # normalne wierzcholkow pominiete (szum drobnych trojkatow)
    inne = np.abs(V[:, 2]) >= PROG_PLASZCZYZNY
    if inne.any():
        dd, _ = cKDTree(V[inne]).query(V[plaski], distance_upper_bound=MARGINES_PLASKI)
        idx = np.flatnonzero(plaski)
        plaski[idx[np.isfinite(dd)]] = False
    wyn = {"wierzcholkow_plaskich": int(plaski.sum())}
    if plaski.sum() < 2000:
        wyn["uwaga"] = "za malo plaskich wierzcholkow"
        return wyn
    P = V[plaski]
    d_eq = odstep(pw, plaski)
    e = m.edges_unique
    pl_e = plaski[e[:, 0]] & plaski[e[:, 1]]
    wyn["odstep_mm"] = round(d_eq, 4)
    wyn["krawedz_trojkata_mediana_mm"] = round(float(np.median(m.edges_unique_length[pl_e])), 4)
    # reszty wzgledem wielomianu 2. stopnia w komorkach KOMORKA x KOMORKA (ksztalt / krzywizna plytki odjete)
    ij = np.floor(P[:, :2] / KOMORKA).astype(np.int64)
    _, kom = np.unique(ij, axis=0, return_inverse=True)
    kom = kom.ravel()
    r = np.full(len(P), np.nan)
    for k in np.unique(kom):
        idx = np.flatnonzero(kom == k)
        if len(idx) < 200:
            continue
        x, y = P[idx, 0] - P[idx, 0].mean(), P[idx, 1] - P[idx, 1].mean()
        A = _wielomian2(x, y)
        ok = np.ones(len(idx), bool)
        for _ in range(3):
            c, *_ = np.linalg.lstsq(A[ok], P[idx[ok], 2], rcond=None)
            rr = P[idx, 2] - A @ c
            ok = np.abs(rr - np.median(rr)) < 5 * max(robust_std(rr[ok]), 1e-4)
        r[idx] = rr
    w = np.isfinite(r)
    P, r, kom = P[w], r[w], kom[w]
    ok = np.abs(r) < 6 * robust_std(r)
    wyn["sigma_mm"] = round(robust_std(r), 4)
    wyn["sigma_std_mm"] = round(float(np.std(r[ok])), 4)
    wyn["odstajacych_udzial"] = round(float(1 - ok.mean()), 5)
    wyn["komorek"] = int(len(np.unique(kom)))
    ak = autokorelacja(P[ok], r[ok], kom[ok], rng, d_eq)
    kor = dopasuj_korelacje(ak, d_eq)
    s = wyn["sigma_std_mm"]
    if kor["udzial_skorelowany"] is not None:
        a = kor["udzial_skorelowany"]
        kor["sigma_skorelowana_mm"] = round(s * math.sqrt(a), 4)
        kor["sigma_niezalezna_mm"] = round(s * math.sqrt(max(0.0, 1 - a)), 4)
        kor["udzial_skorelowany"] = round(a, 3)
        kor["L_mm"] = round(kor["L_mm"], 4) if kor["L_mm"] is not None else None
    wyn["korelacja"] = kor
    wyb = [0.05, 0.1, 0.2, 0.3, 0.5]
    wyn["autokorelacja"] = {f"{h:.2f}": (round(float(ak["C"][int(h / KROK_H)]), 3) if np.isfinite(ak["C"][int(h / KROK_H)]) else None) for h in wyb}
    return wyn


# ---------------------------------------------------------------------------------------------------------
# 2. prace (korony)
# ---------------------------------------------------------------------------------------------------------
def fragmenty(m: trimesh.Trimesh, plytka: bool) -> list[np.ndarray]:
    """Indeksy wierzcholkow kazdej pracy (nad plytka). Bez plytki: cala siatka = jedna praca."""
    V = np.asarray(m.vertices)
    if not plytka:
        return [np.arange(len(V))]
    nad = np.flatnonzero(V[:, 2] > NAD_PLYTKA)
    if len(nad) < 300:
        return []
    pary = cKDTree(V[nad]).query_pairs(EPS_PRACY, output_type="ndarray")
    A = coo_matrix((np.ones(len(pary)), (pary[:, 0], pary[:, 1])), shape=(len(nad), len(nad)))
    _, et = connected_components(A, directed=False)
    out = []
    for e in np.unique(et):
        idx = nad[et == e]
        if len(idx) < 300:
            continue
        ext = V[idx].max(0) - V[idx].min(0)
        if max(ext[0], ext[1]) < 3.0 or ext[2] < 1.5:
            continue
        out.append(idx)
    return sorted(out, key=len, reverse=True)


def podsiatka(m: trimesh.Trimesh, idx: np.ndarray) -> trimesh.Trimesh:
    w = np.zeros(len(m.vertices), bool)
    w[idx] = True
    f = m.faces[w[m.faces].all(axis=1)]
    s = trimesh.Trimesh(m.vertices, f, process=False)
    s.remove_unreferenced_vertices()
    return s


def dopasuj_ze_skala(P: np.ndarray, pr, T: np.ndarray, rng, iteracje=25, model="iso_d") -> dict:
    """ICP punkt-plaszczyzna ze skala: P (uklad zrodla) -> uklad puli projektu; T = poczatek (zrodlo -> pula, sztywna).
    Model 'iso': skala izotropowa; 'iso_d': + przesuniecie powierzchni d0 wzdluz normalnej (naddatek / ubytek
    frezowania, rozne od skali na skorupie korony); 'xyz_d': skala xy i z osobno + d0.
    Zwraca skale skanu wzgledem projektu (eps > 0 = skan wiekszy), d0 i transformacje (z korekta skali)."""
    if len(P) > 40000:
        P = P[rng.choice(len(P), 40000, replace=False)]
    A_tot = np.eye(4)
    A_tot[:] = T
    S_xy, S_z, d0 = 1.0, 1.0, 0.0
    prog = 0.3
    for it in range(iteracje):
        X = P @ A_tot[:3, :3].T + A_tot[:3, 3]
        r_ = pr.scena.compute_closest_points(o3d.core.Tensor(np.ascontiguousarray(X, dtype=np.float32)))
        Q = r_["points"].numpy().astype(np.float64)
        Nq = r_["primitive_normals"].numpy().astype(np.float64)
        e = np.einsum("ij,ij->i", X - Q, Nq)
        dist = np.linalg.norm(X - Q, axis=1)
        sig = robust_std(e - d0)
        prog = max(0.03, min(prog, 4 * sig)) if it > 2 else prog
        ok = (dist < 0.5) & (np.abs(e - d0) < prog)
        Xo, No, eo = X[ok], Nq[ok], e[ok]
        c = Xo.mean(0)
        Y = Xo - c
        kol = [np.cross(Y, No), No]  # obrot (3), przesuniecie (3)
        if model == "xyz_d":
            kol += [(No[:, 0] * Y[:, 0] + No[:, 1] * Y[:, 1])[:, None], (No[:, 2] * Y[:, 2])[:, None], -np.ones((len(Y), 1))]
        elif model == "iso_d":
            kol += [np.einsum("ij,ij->i", No, Y)[:, None], -np.ones((len(Y), 1))]
        else:
            kol += [np.einsum("ij,ij->i", No, Y)[:, None]]
        A = np.hstack(kol)
        b = -(eo - d0)
        x, *_ = np.linalg.lstsq(A, b, rcond=None)
        om, t = x[:3], x[3:6]
        if model == "xyz_d":
            kxy, kz, dd = x[6], x[7], x[8]
        elif model == "iso_d":
            kxy = kz = x[6]
            dd = x[7]
        else:
            kxy = kz = x[6]
            dd = 0.0
        d0 += dd
        R = trimesh.transformations.rotation_matrix(np.linalg.norm(om), om / max(np.linalg.norm(om), 1e-12))[:3, :3] if np.linalg.norm(om) > 1e-12 else np.eye(3)
        Sk = np.diag([1 + kxy, 1 + kxy, 1 + kz])
        B = np.eye(4)
        B[:3, :3] = R @ Sk
        B[:3, 3] = c - (R @ Sk) @ c + t
        A_tot = B @ A_tot
        S_xy *= 1 + kxy
        S_z *= 1 + kz
        if np.abs(x[:6]).max() < 1e-6 and abs(kxy) < 1e-6 and abs(kz) < 1e-6:
            break
    X = P @ A_tot[:3, :3].T + A_tot[:3, 3]
    dd = pr.odleglosci(X)
    return {"eps_xy": 1 / S_xy - 1, "eps_z": 1 / S_z - 1, "eps": 1 / math.sqrt(S_xy * S_xy * S_z) ** (2 / 3) - 1 if model == "xyz_d" else 1 / S_xy - 1,
            "d0_mm": d0, "T": A_tot, "pokrycie_005": float((dd <= 0.05).mean()), "iteracji": it + 1, "punktow": int(ok.sum())}


def krawedz(sub_pula: trimesh.Trimesh, linie: dict, pw_ref: float) -> dict:
    """Cofniecie naroznikow i braki danych wzdluz linii krawedzi brzegu (O, I, S) projektu; siatka w ukladzie puli."""
    sc = o3d.t.geometry.RaycastingScene()
    sc.add_triangles(o3d.t.geometry.TriangleMesh(o3d.core.Tensor(np.asarray(sub_pula.vertices, dtype=np.float32)),
                                                 o3d.core.Tensor(np.asarray(sub_pula.faces, dtype=np.int32))))
    V = np.asarray(sub_pula.vertices)
    dr = cKDTree(V)
    wyn = {}
    braki_wsz, n_wsz = 0, 0
    for nazwa in ("O", "I", "S"):
        L = linie[nazwa]
        ok = L["ok"].copy()
        X, B, alfa = L["X"], L["B"], L["alfa"]
        if nazwa == "S":
            B = np.tile(np.array([0.0, 0.0, -1.0]), (len(X), 1))  # srodek plaskiej krawedzi: promien z gory w dol
        org = X - START_PROMIENIA * B
        ray = np.concatenate([org, B], 1).astype(np.float32)
        th = sc.cast_rays(o3d.core.Tensor(ray))["t_hit"].numpy().astype(float)
        cof = th - START_PROMIENIA
        traf = np.isfinite(cof) & (cof >= OKNO_PROMIENIA[0]) & (cof <= OKNO_PROMIENIA[1])
        licz = np.asarray(dr.query_ball_point(X, R_GESTOSCI, return_length=True), dtype=float)
        med = float(np.median(licz[ok])) if ok.any() else 0.0
        brak = ok & (licz < PROG_GESTOSCI * med)  # brak danych = malo wierzcholkow (wypelniona dziura ma duze trojkaty)
        braki_wsz += int(brak.sum())
        n_wsz += int(ok.sum())
        w = {"stacji": int(ok.sum()), "bez_danych": int(brak.sum()), "udzial_bez_danych": round(float(brak.sum() / max(1, ok.sum())), 4),
             "wierzcholkow_na_stacje_mediana": med, "promien_nie_trafil_udzial": round(float((ok & ~traf & ~brak).sum() / max(1, ok.sum())), 4)}
        # przerwy: ciagi kolejnych stacji bez danych (linia zamknieta), dlugosc = liczba stacji x krok
        krok = L["L"] / len(X)
        b = brak.astype(int)
        if b.any() and not b.all():
            sh = np.argmin(b)  # zaczynamy od stacji z danymi
            bb = np.roll(b, -sh)
            dl, cur = [], 0
            for v in bb:
                if v:
                    cur += 1
                elif cur:
                    dl.append(cur * krok)
                    cur = 0
            if cur:
                dl.append(cur * krok)
            dl = np.array(dl)
            w["przerwy"] = {">=0.1": int((dl >= 0.1).sum()), ">=0.2": int((dl >= 0.2).sum()), ">=0.5": int((dl >= 0.5).sum()), ">=1.0": int((dl >= 1.0).sum()),
                            "najdluzsza_mm": round(float(dl.max()), 3)}
        if nazwa in ("O", "I"):
            uz = ok & traf & ~brak & (alfa < math.radians(ALFA_MAX_DEG))
            if uz.sum() >= 10:
                c = float(np.median(cof[uz]))
                k = 1.0 / np.sin(alfa[uz] / 2) - 1.0
                rho = float(np.median(cof[uz] / np.maximum(k, 0.05)))
                w.update({"cofniecie_mm": round(c, 4), "cofniecie_rozrzut_mm": round(robust_std(cof[uz]), 4),
                          "kat_naroznika_deg": round(float(np.degrees(np.median(alfa[uz]))), 1), "rho_rownowazne_mm": round(rho, 4), "stacji_promienia": int(uz.sum())})
        else:
            uz = ok & traf & ~brak
            if uz.sum() >= 10:
                w["przesuniecie_srodka_mm"] = round(float(np.median(cof[uz])), 4)
        wyn[nazwa] = w
    wyn["udzial_bez_danych_OIS"] = round(braki_wsz / max(1, n_wsz), 4)
    return wyn


def korona(m_lev: trimesh.Trimesh, idx: np.ndarray, pula, wsp: float, ust: dict, rng, linie_cache: dict) -> dict:
    sub = podsiatka(m_lev, idx)
    P = np.array(sub.vertices)
    N = np.array(sub.vertex_normals)
    wyn = {"wierzcholkow": int(len(P)), "obrys_mm": [round(float(x), 2) for x in (P.max(0) - P.min(0))]}
    t0 = time.time()
    dop = M.dopasuj(P, N, pula, ust)
    naj = dop.najlepszy
    if naj is None or naj.pokrycie < 0.6:
        # filtr wymiarow programu odrzuca wlasciwy projekt, gdy czesc korony jest schowana w gniezdzie (nizej niz plytka)
        # albo skala jest bledna - powtorka bez filtru (jak match.dopasuj, gdy zaden projekt nie przejdzie filtru)
        m_ = ust["match"]
        dop = M.dopasuj(P, N, pula, {**ust, "match": {**m_, "filtr_wymiar_mm": 1e9, "filtr_objetosc_udzial": 1e9}})
        naj = dop.najlepszy
        wyn["filtr_wymiarow_wylaczony"] = True
    if naj is None or naj.transformacja is None:
        wyn["uwaga"] = "brak dopasowania do projektu"
        return wyn
    pr = pula.projekty[naj.id]
    wyn.update({"projekt": naj.id, "pokrycie_programu": round(naj.pokrycie, 4), "status_dopasowania": dop.status,
                "drugi_kandydat_pokrycie": round(dop.kandydaci[1].pokrycie, 4) if len(dop.kandydaci) > 1 else None, "czas_dopasowania_s": round(time.time() - t0, 1)})
    T0 = pr.T0 @ np.linalg.inv(np.asarray(naj.transformacja))  # zrodlo (plytka) -> pula
    modele = {}
    for mod in ("iso", "iso_d", "xyz_d"):
        f = dopasuj_ze_skala(P, pr, T0, rng, model=mod)
        modele[mod] = f
    glow = modele["iso_d"]
    wyn["skala"] = {mod: {"eps_proc": round(100 * f["eps"], 4), "eps_xy_proc": round(100 * f["eps_xy"], 4), "eps_z_proc": round(100 * f["eps_z"], 4),
                          "d0_mm": round(f["d0_mm"], 4), "pokrycie_005": round(f["pokrycie_005"], 4)} for mod, f in modele.items()}
    wyn["skala"]["wspolczynnik_podany"] = wsp
    wyn["skala"]["wspolczynnik_najlepszy"] = round(wsp * (1 + glow["eps"]), 5)
    T = glow["T"]
    subp = sub.copy()
    subp.apply_transform(T)
    # odchylki od projektu po korekcie skali
    Pp = np.asarray(subp.vertices)
    r_ = pr.scena.compute_closest_points(o3d.core.Tensor(np.ascontiguousarray(Pp, dtype=np.float32)))
    dev = np.einsum("ij,ij->i", Pp - r_["points"].numpy(), r_["primitive_normals"].numpy()) - glow["d0_mm"]
    if pr.id not in linie_cache:
        linie_cache[pr.id] = CW.linie_krawedzi(pr)
    linie = linie_cache[pr.id]
    Xk = np.vstack([linie[n]["X"][linie[n]["ok"]] for n in ("O", "I")])
    dk_, _ = cKDTree(Xk).query(Pp)
    pas = Pp[:, 2] > -1.5
    kraw = dk_ < 0.1
    sciana = pas & (dk_ > 0.3)
    # odstep = sqrt(pole projektu pokryte skanem w strefie / liczba wierzcholkow w strefie); pole z gestej probki projektu
    # (odporne na szorstkosc szumu i na brakujace trojkaty siatki)
    if ("probka", pr.id) not in linie_cache:
        Qp, _ = trimesh.sample.sample_surface(pr.siatka, int(pr.siatka.area / 0.02**2), seed=5)
        Qp = np.asarray(Qp)
        linie_cache[("probka", pr.id)] = (Qp, cKDTree(Xk).query(Qp)[0])
    Qp, dQ = linie_cache[("probka", pr.id)]
    pokr = np.isfinite(cKDTree(Pp).query(Qp, distance_upper_bound=0.15)[0])
    a1 = pr.siatka.area / len(Qp)
    for nazwa, mq, mv in (("sciana", (Qp[:, 2] > -1.5) & (dQ > 0.3) & pokr, sciana), ("krawedz", (dQ < 0.1) & pokr, kraw)):
        wyn[f"odstep_{nazwa}_mm"] = round(math.sqrt(mq.sum() * a1 / max(1, mv.sum())), 4)
    wyn["sigma_sciana_mm"] = round(robust_std(dev[sciana]), 4)
    wyn["sigma_krawedz_mm"] = round(robust_std(dev[kraw]), 4)
    wyn["mediana_odchylki_krawedz_mm"] = round(float(np.median(dev[kraw])), 4) if kraw.any() else None
    kr = krawedz(subp, linie, 0.0)
    # odniesienie: idealny skan (bez szumu i zaokraglenia) tej samej gestosci - siatka trojkatow tez scina naroznik
    d_ref = wyn["odstep_sciana_mm"]
    klucz = (pr.id, round(d_ref, 3))
    if klucz not in linie_cache:
        linie_cache[klucz] = krawedz(siatka_idealna(pr, d_ref), linie, 0.0)
    ref = linie_cache[klucz]
    for n in ("O", "I"):
        if "cofniecie_mm" in kr[n] and "cofniecie_mm" in ref[n]:
            c = math.sqrt(max(0.0, kr[n]["cofniecie_mm"] ** 2 - ref[n]["cofniecie_mm"] ** 2))  # odjecie kwadratowe (empirycznie, walidacja R2)
            k = 1.0 / math.sin(math.radians(kr[n]["kat_naroznika_deg"]) / 2) - 1.0
            kr[n]["cofniecie_idealnego_mm"] = ref[n]["cofniecie_mm"]
            kr[n]["cofniecie_ponad_idealny_mm"] = round(c, 4)
            kr[n]["rho_rownowazne_mm"] = round(max(0.0, c) / max(k, 0.05), 4)
    kr["udzial_bez_danych_idealnego"] = ref["udzial_bez_danych_OIS"]
    wyn["krawedz"] = kr
    return wyn


def siatka_idealna(pr, d: float, seed: int = 3) -> trimesh.Trimesh:
    """Skan idealny projektu: rownomierna losowa probka co d, siatka ball pivoting (wierzcholki = punkty)."""
    m = pr.siatka
    P, fid = trimesh.sample.sample_surface(m, int(m.area / d**2), seed=seed)
    pc = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(np.asarray(P)))
    pc.normals = o3d.utility.Vector3dVector(np.asarray(m.face_normals[fid]))
    bp = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(pc, o3d.utility.DoubleVector([f * d for f in PROMIENIE_BPA]))
    return trimesh.Trimesh(np.asarray(bp.vertices), np.asarray(bp.triangles), process=False)


# ---------------------------------------------------------------------------------------------------------
def powtarzalnosc(m1: trimesh.Trimesh, m2: trimesh.Trimesh, rng) -> dict:
    """Drugi skan bez ruszania plytki (obie siatki wypoziomowane ta sama macierza): ICP 2 -> 1 na calosci, potem na
    plaskiej czesci plytki roznica wysokosci wzdluz z (promien z gory na siatke 1). Odleglosc do najblizszego punktu
    na szorstkiej siatce zanizala roznice (walidacja: -34 %), dlatego pion. Sigma pojedynczego skanu = sigma roznicy /
    sqrt(1,75): interpolacja trojkatow skanu 1 polowi wariancje szumu niezaleznego (sqrt 1,5), skorelowanego nie (sqrt 2).
    Roznica ksztaltu = rozrzut median roznicy w komorkach 4 mm (wygiecie / dryf miedzy skanami, nie szum)."""
    P1, fid = trimesh.sample.sample_surface(m1, 300000, seed=1)
    pc1 = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(np.asarray(P1)))
    pc1.normals = o3d.utility.Vector3dVector(np.asarray(m1.face_normals[fid]))
    V2 = np.asarray(m2.vertices)
    pc2 = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(V2[rng.choice(len(V2), min(len(V2), 200000), replace=False)]))
    T = np.eye(4)
    for prog in (0.5, 0.2, 0.08):
        T = np.asarray(o3d.pipelines.registration.registration_icp(pc2, pc1, prog, T, o3d.pipelines.registration.TransformationEstimationPointToPlane()).transformation)
    X = V2 @ T[:3, :3].T + T[:3, 3]
    plaski = np.abs(X[:, 2]) < PROG_PLASZCZYZNY
    inne = np.abs(X[:, 2]) >= PROG_PLASZCZYZNY
    if inne.any() and plaski.any():
        dd, _ = cKDTree(X[inne]).query(X[plaski], distance_upper_bound=MARGINES_PLASKI)
        idx = np.flatnonzero(plaski)
        plaski[idx[np.isfinite(dd)]] = False
    Xp = X[plaski]
    if len(Xp) > 400000:
        Xp = Xp[rng.choice(len(Xp), 400000, replace=False)]
    sc = o3d.t.geometry.RaycastingScene()
    sc.add_triangles(o3d.t.geometry.TriangleMesh(o3d.core.Tensor(np.asarray(m1.vertices, dtype=np.float32)), o3d.core.Tensor(np.asarray(m1.faces, dtype=np.int32))))
    org = Xp.copy()
    org[:, 2] = 0.5
    ray = np.concatenate([org, np.tile([0.0, 0.0, -1.0], (len(org), 1))], 1).astype(np.float32)
    th = sc.cast_rays(o3d.core.Tensor(ray))["t_hit"].numpy().astype(float)
    ok = np.isfinite(th) & (th < 1.0)
    dz = Xp[ok, 2] - (0.5 - th[ok])
    s = robust_std(dz)
    ij = np.floor(Xp[ok, :2] / KOMORKA).astype(np.int64)
    _, kom = np.unique(ij, axis=0, return_inverse=True)
    kom = kom.ravel()
    med = [float(np.median(dz[kom == k])) for k in np.unique(kom) if (kom == k).sum() >= 200]
    return {"przesuniecie_icp_mm": round(float(np.linalg.norm(T[:3, 3])), 4), "punktow_plaskich": int(ok.sum()),
            "sigma_roznicy_mm": round(s, 4), "sigma_pojedynczego_mm": round(s / math.sqrt(1.75), 4),
            "roznica_ksztaltu_mm": round(float(np.std(med)), 4) if len(med) > 2 else None}


def ocena_wg_fali1(w: dict) -> list[str]:
    """Orientacyjne odczytanie wynikow wg fali 1 testow krawedzi (06.11.2026) - nie decyzja."""
    out = []
    pl = w.get("plytka", {})
    s = pl.get("sigma_mm")
    if s is not None:
        if s <= 0.015:
            out.append(f"szum {s:.3f} mm <= 0,015: wg fali 1 ukruszenie 0,08 mm na krawedzi jest wykrywalne (metoda C, K_a)")
        elif s <= 0.025:
            out.append(f"szum {s:.3f} mm: miedzy K_a (0,01) a K_b (0,03) - granica wykrywania ok. 0,10-0,12 mm (do sprawdzenia)")
        else:
            out.append(f"szum {s:.3f} mm > 0,025: wg fali 1 realna granica 0,12-0,15 mm, 0,08 mm niewykrywalne")
    k = pl.get("korelacja", {})
    if k.get("L_mm") and k.get("udzial_skorelowany") and k["udzial_skorelowany"] > 0.3:
        if 0.05 <= k["L_mm"] <= 0.25:
            out.append(f"szum skorelowany L {k['L_mm']:.2f} mm ({100*k['udzial_skorelowany']:.0f} % wariancji): wg T5 grozi falszywymi alarmami")
        else:
            out.append(f"szum skorelowany L {k['L_mm']:.2f} mm ({100*k['udzial_skorelowany']:.0f} % wariancji)")
    for kor in w.get("korony", []):
        if "skala" not in kor:
            continue
        e = kor["skala"]["iso_d"]["eps_proc"]
        if abs(e) >= 0.1:
            out.append(f"korona {kor['projekt']}: blad skali {e:+.2f} % - wg T5 juz 0,1-0,2 % daje falszywe alarmy (potrzebny wspolczynnik pracy)")
        bd = kor["krawedz"]["udzial_bez_danych_OIS"]
        if bd >= 0.1:
            out.append(f"korona {kor['projekt']}: {100*bd:.0f} % krawedzi bez danych - wg T5 dziury 30 % zabieraja ok. polowe wykryc 0,10-0,15")
    return out


def zmierz(m: trimesh.Trimesh, pula, wsp: float, ust: dict, bez_plytki=False, seed=0, linie_cache=None, m2=None) -> dict:
    rng = np.random.default_rng(seed)
    t0 = time.time()
    linie_cache = {} if linie_cache is None else linie_cache
    wyn = {"wierzcholkow": int(len(m.vertices)), "trojkatow": int(len(m.faces)), "pole_mm2": round(float(m.area), 1),
           "odstep_calosc_mm": round(math.sqrt(m.area / len(m.vertices)), 4)}
    T, info = (None, {"plaszczyzna": "pominieta"}) if bez_plytki else poziomowanie(m, rng)
    wyn["plaszczyzna"] = info
    ml = m.copy()
    if T is not None:
        ml.apply_transform(T)
        wyn["plytka"] = plaska_czesc(ml, rng)
    wyn["korony"] = []
    if pula is not None and len(pula):
        for idx in fragmenty(ml, T is not None)[:6]:
            wyn["korony"].append(korona(ml, idx, pula, wsp, ust, rng, linie_cache))
    if m2 is not None:
        if T is not None:
            m2l = m2.copy()
            m2l.apply_transform(T)
            wyn["powtarzalnosc"] = powtarzalnosc(ml, m2l, rng)
        else:
            wyn["powtarzalnosc"] = {"uwaga": "bez plaskiej czesci plytki - nie liczone"}
    wyn["ocena_wg_fali1"] = ocena_wg_fali1(wyn)
    wyn["czas_s"] = round(time.time() - t0, 1)
    return wyn


def raport_tekstowy(w: dict, nazwa: str) -> str:
    L = [f"POMIAR SKANU: {nazwa}", f"siatka: {w['wierzcholkow']} wierzcholkow, {w['trojkatow']} trojkatow, pole {w['pole_mm2']} mm2, czas {w['czas_s']} s", ""]
    pl = w.get("plytka")
    if pl and "sigma_mm" in pl:
        k = pl.get("korelacja", {})
        L += ["PLASKA CZESC PLYTKI",
              f"  odstep punktow d         {pl['odstep_mm']:.4f} mm   (bok trojkata mediana {pl['krawedz_trojkata_mediana_mm']:.4f})",
              f"  szum sigma               {pl['sigma_mm']:.4f} mm   (std {pl['sigma_std_mm']:.4f})",
              f"  szum skorelowany         udzial {k.get('udzial_skorelowany')}  dlugosc L {k.get('L_mm')} mm  (sigma skorel. {k.get('sigma_skorelowana_mm')}, niezal. {k.get('sigma_niezalezna_mm')})",
              f"  autokorelacja C(h)       {pl['autokorelacja']}", ""]
    else:
        L += [f"PLASKA CZESC PLYTKI: brak ({w['plaszczyzna']})", ""]
    for i, kr in enumerate(w.get("korony", []), 1):
        if "skala" not in kr:
            L += [f"KORONA {i}: {kr.get('uwaga')}", ""]
            continue
        s, k = kr["skala"], kr["krawedz"]
        L += [f"KORONA {i}: projekt {kr['projekt']}, pokrycie {kr['pokrycie_programu']:.3f} (drugi kandydat {kr['drugi_kandydat_pokrycie']})",
              f"  blad skali (skan wzgl. projekt x {s['wspolczynnik_podany']}): {s['iso_d']['eps_proc']:+.3f} %  (xy {s['xyz_d']['eps_xy_proc']:+.3f} %, z {s['xyz_d']['eps_z_proc']:+.3f} %)  -> wspolczynnik najlepszy {s['wspolczynnik_najlepszy']}",
              f"  przesuniecie powierzchni d0 {s['iso_d']['d0_mm']:+.4f} mm, pokrycie po korekcie {s['iso_d']['pokrycie_005']:.3f}",
              f"  odstep punktow: sciana {kr['odstep_sciana_mm']:.4f} mm, krawedz {kr['odstep_krawedz_mm']:.4f} mm",
              f"  sigma: sciana {kr['sigma_sciana_mm']:.4f} mm, krawedz {kr['sigma_krawedz_mm']:.4f} mm (mediana odchylki krawedzi {kr['mediana_odchylki_krawedz_mm']})",
              f"  naroznik zewn.: cofniecie {k['O'].get('cofniecie_mm')} mm (idealny skan tej gestosci {k['O'].get('cofniecie_idealnego_mm')}, ponad {k['O'].get('cofniecie_ponad_idealny_mm')}) -> promien rownowazny {k['O'].get('rho_rownowazne_mm')} mm (kat {k['O'].get('kat_naroznika_deg')} st.)",
              f"  naroznik wewn.: cofniecie {k['I'].get('cofniecie_mm')} mm (idealny skan tej gestosci {k['I'].get('cofniecie_idealnego_mm')}, ponad {k['I'].get('cofniecie_ponad_idealny_mm')}) -> promien rownowazny {k['I'].get('rho_rownowazne_mm')} mm (kat {k['I'].get('kat_naroznika_deg')} st.)",
              f"  krawedz bez danych: {100*k['udzial_bez_danych_OIS']:.1f} %  (zewn {100*k['O']['udzial_bez_danych']:.1f}, wewn {100*k['I']['udzial_bez_danych']:.1f}, srodek {100*k['S']['udzial_bez_danych']:.1f}); przerwy zewn {k['O'].get('przerwy')}", ""]
    if "powtarzalnosc" in w:
        p = w["powtarzalnosc"]
        L += ["POWTARZALNOSC (drugi skan)", f"  sigma roznicy {p.get('sigma_roznicy_mm')} mm -> sigma pojedynczego skanu {p.get('sigma_pojedynczego_mm')} mm (szacunek +-10 %), roznica ksztaltu plytki miedzy skanami {p.get('roznica_ksztaltu_mm')} mm {p.get('uwaga', '')}", ""]
    L += ["ODCZYT ORIENTACYJNY (wg testow fali 1, nie decyzja):"] + ["  - " + x for x in w["ocena_wg_fali1"]]
    return "\n".join(L)


def _json(o):
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    raise TypeError(type(o))


def main():
    ap = argparse.ArgumentParser(description="Pomiar wlasciwosci skanu (T10)")
    ap.add_argument("skan")
    ap.add_argument("--projekty", default=None, help="folder z projektami STL koron, ktore sa na plytce")
    ap.add_argument("--wspolczynnik", type=float, default=1.22)
    ap.add_argument("--wyj", default=None)
    ap.add_argument("--powtorka", default=None)
    ap.add_argument("--bez-plytki", action="store_true")
    a = ap.parse_args()
    sk = Path(a.skan)
    wyj = Path(a.wyj) if a.wyj else sk.parent / (sk.stem + "_pomiar")
    wyj.mkdir(parents=True, exist_ok=True)
    print("wczytuje", sk.name, flush=True)
    m = wczytaj_siatke(sk)
    m2 = wczytaj_siatke(Path(a.powtorka)) if a.powtorka else None
    ust = U.wczytaj_ustawienia()
    pula = None
    if a.projekty:
        sciezki = [Path(x) for x in a.projekty.split(";")]
        if len(sciezki) == 1 and sciezki[0].is_dir():
            pula = M.Pula(sciezki[0], a.wspolczynnik)
        else:  # lista plikow STL rozdzielona srednikami
            pula = M.Pula([], a.wspolczynnik)
            for p in sciezki:
                pr = M.Projekt(p, a.wspolczynnik)
                pula.projekty[pr.id] = pr
    if pula is not None:
        print("projektow w folderze:", len(pula), flush=True)
    w = zmierz(m, pula, a.wspolczynnik, ust, a.bez_plytki, m2=m2)
    txt = raport_tekstowy(w, sk.name)
    print(txt)
    (wyj / "raport.txt").write_text(txt, encoding="utf-8")
    w2 = {k: v for k, v in w.items()}
    for kr in w2.get("korony", []):
        kr.pop("T", None)
    (wyj / "pomiar.json").write_text(json.dumps(w2, indent=1, ensure_ascii=False, default=_json), encoding="utf-8")
    print("\nzapisano:", wyj / "raport.txt", "i", wyj / "pomiar.json")


if __name__ == "__main__":
    main()
