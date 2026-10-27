"""Syntetyczna plytka z gniazdami: siatka plytki z ukladu ramki, rozmieszczenie prac i skan z prawda.

Uklad plytki (jak w qc.uklad): srodek gornej powierzchni, X w prawo, Y do tylu, Z w gore; wierzch
Z = 0, dno Z = -grubosc. Siatka = mapa wysokosci gornej powierzchni (regularna siatka krok_mm) + boki
z rowkiem pokrywki + dno z kieszeniami magnesow; otwory i wyciecie D to brak trojkatow. Siatka nie
jest wodoszczelna (brak scianek otworow i dolkow).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
import trimesh

from qc.syntetyka.prawda import Prawda, PrawdaPracy
from qc.syntetyka.skan import skan_pracy
from qc.uklad import Uklad, kod_numeru

PROMIEN_NAROZNIKA = 1.0
ROWEK_GLEBOKOSC = 0.8
ROWEK_Z = (-2.5, -1.5)
RELIEF_XY = (4.0, 5.0)  # prostokat zastepujacy cyfre (szerokosc x wysokosc)
KAT_SCIANKI_DEG = 15.0

KROK_PLYTKI_SKANU_MM = 0.2
ODSTEP_OD_POWIERZCHNI_MM = 0.05
MAX_Z_PRACY = 10.0
LUZ_KORONY_MM = 1.0
LUZ_MOSTU_MM = 2.0
K_WIECZOR = (1.20, 1.25)
K_RANO = 1.0
LOSOWA_OBROT_Z_DEG = 4.9
LOSOWA_PRZECHYL_DEG = 0.95
LOSOWA_PRZESUNIECIE_MM = 2.95
STANY = ("praca", "podwojne", "poza_gniazdem")


@dataclass
class Rozmieszczenie:
    """Praca w gniezdzie: projekt*k, obrot 180 st. wokol X, obrot Z, przesuniecie w gniezdzie."""

    projekt: object
    gniazdo: int
    wspolczynnik: float
    obrot_z_deg: float
    przesuniecie_xy: tuple[float, float]
    opcje: dict = field(default_factory=dict)


# --- mapa wysokosci ---------------------------------------------------------------


def _profil_scianki(r, r_dol, r_gora, glebokosc):
    """Dno plaskie -glebokosc do r_dol, liniowo do 0 na r_gora, dalej 0."""
    nachyl = -glebokosc * (r_gora - r) / max(r_gora - r_dol, 1e-9)
    return np.where(r <= r_dol, -glebokosc, np.where(r < r_gora, nachyl, 0.0))


def _odl_od_osi(g, x, y):
    (px, py), (qx, qy), _ = g.os_rynienki()
    vx, vy = qx - px, qy - py
    dl2 = vx * vx + vy * vy
    t = np.zeros_like(x) if dl2 == 0 else np.clip(((x - px) * vx + (y - py) * vy) / dl2, 0.0, 1.0)
    return np.hypot(x - px - t * vx, y - py - t * vy)


def mapa_gornej(uklad: Uklad, numer: int | None, x, y):
    """Wysokosc gornej powierzchni w punktach (x, y) i maska punktow usunietych (otwory, wyciecie D)."""
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    z = np.zeros(x.shape)
    usun = np.zeros(x.shape, dtype=bool)
    tan15 = math.tan(math.radians(KAT_SCIANKI_DEG))
    for g in uklad.gniazda:
        _, _, r_gora = g.os_rynienki()
        r_dol = g.d_dol / 2 if g.rodzaj == "stozek" else r_gora - g.glebokosc * tan15
        r = _odl_od_osi(g, x, y)
        blisko = r < r_gora
        if not blisko.any():
            continue
        z[blisko] = np.minimum(z[blisko], _profil_scianki(r[blisko], r_dol, r_gora, g.glebokosc))
        for ox, oy in g.srodki_otworow():
            usun |= np.hypot(x - ox, y - oy) < g.otwor_d / 2 - 1e-9
    for mx, my, d, glebokosc in uklad.znaczniki.values():
        r = np.hypot(x - mx, y - my)
        z = np.minimum(z, np.where(r < d / 2, -glebokosc * (1 - r / (d / 2)), 0.0))
    bity = {"A", "B", "C"} if numer is None else kod_numeru(numer)
    for bit in sorted(bity):
        dx, dy = uklad.dolki_kodu[bit]
        d, glebokosc = uklad.wymiary_dolkow.get(bit, (2.0, 1.0))
        z = np.where(np.hypot(x - dx, y - dy) <= d / 2 + 1e-9, np.minimum(z, -glebokosc), z)
    if numer is not None and uklad.relief_numeru is not None:
        rx, ry, _, wysokosc = uklad.relief_numeru
        w, h = RELIEF_XY
        prost = (np.abs(x - rx) <= w / 2 + 1e-9) & (np.abs(y - ry) <= h / 2 + 1e-9)
        z = np.where(prost, np.maximum(z, wysokosc), z)
    usun |= _w_wycieciu(uklad, x, y)
    return z, usun


def _w_wycieciu(uklad: Uklad, x, y):
    x_min, x_max, y_min, y_max = uklad.wyciecie
    return (x > x_min + 1e-9) & (x < x_max + 1e-9) & (y > y_min - 1e-9) & (y < y_max - 1e-9)


def _mapa_dolnej(uklad: Uklad, x, y):
    z = np.full(x.shape, -uklad.grubosc)
    for kx, ky, d, glebokosc in uklad.kieszenie_magnesow.values():
        z = np.where(np.hypot(x - kx, y - ky) <= d / 2 + 1e-9, -uklad.grubosc + glebokosc, z)
    return z


# --- siatka plytki ----------------------------------------------------------------


def _trojkaty_siatki(n: int, zostaw: np.ndarray, w_gore: bool) -> np.ndarray:
    """Trojkaty regularnej siatki (n+1)x(n+1) (indeks i*(n+1)+j); tylko z zostawionymi wierzcholkami."""
    m = n + 1
    i, j = np.meshgrid(np.arange(n), np.arange(n), indexing="ij")
    a = (i * m + j).ravel()
    b, c, d = a + m, a + m + 1, a + 1
    f = np.concatenate([np.column_stack([a, b, c]), np.column_stack([a, c, d])])
    f = f[zostaw[f].all(axis=1)]
    return f if w_gore else f[:, ::-1]


def _kompaktuj(v, f):
    uzyte = np.unique(f)
    mapa = np.full(len(v), -1, dtype=np.int64)
    mapa[uzyte] = np.arange(len(uzyte))
    return v[uzyte], mapa[f]


def _obrys(n: int, i_w: int, j_w: int) -> np.ndarray:
    """Indeksy (i, j) obrysu przeciwnie do zegara (z gory), z wycieciem w narozniku (n, 0)."""
    czesci = [
        [(i, 0) for i in range(0, i_w)],
        [(i_w, j) for j in range(0, j_w)],
        [(i, j_w) for i in range(i_w, n)],
        [(n, j) for j in range(j_w, n)],
        [(i, n) for i in range(n, 0, -1)],
        [(0, j) for j in range(n, 0, -1)],
    ]
    return np.array([p for c in czesci for p in c], dtype=np.int64)


def _boki(xy, z_gora, z_dol, rowek_krawedzi, rowek: bool):
    """Sciany bokow miedzy obrysem gornym a dolnym; rowek pokrywki jako wciecie na wybranych krawedziach."""
    m = len(xy)
    nast = np.roll(np.arange(m), -1)
    e = xy[nast] - xy
    dl = np.maximum(np.linalg.norm(e, axis=1), 1e-12)
    n_wew = np.column_stack([-e[:, 1], e[:, 0]]) / dl[:, None]  # do srodka (obrys CCW)
    g = rowek_krawedzi & rowek

    def wciecie(k_kraw, k_sasiad):
        """Wektor wciecia krawedzi k_kraw na wierzcholku wspolnym z krawedzia k_sasiad."""
        n1, n2 = n_wew[k_kraw], n_wew[k_sasiad]
        s = n1 + n2
        dl_s = np.linalg.norm(s, axis=1)
        mitra = s / np.maximum(dl_s, 1e-12)[:, None]
        cos = np.einsum("ij,ij->i", mitra, n1)
        mitra = mitra * (ROWEK_GLEBOKOSC / np.maximum(cos, 0.2))[:, None]
        prosto = n1 * ROWEK_GLEBOKOSC
        oba = g[k_kraw] & g[k_sasiad] & (dl_s > 1e-6)
        return np.where(oba[:, None], mitra, prosto)

    k = np.arange(m)
    w_pocz = wciecie(k, np.roll(k, 1))
    w_kon = wciecie(k, nast)

    v_list, f_list, n_v = [], [], 0

    def pas(pa, pb):
        """Pas scian miedzy kolumnami punktow pa, pb (E, L, 3) od gory do dolu."""
        nonlocal n_v
        E, L, _ = pa.shape
        v = np.concatenate([pa.reshape(-1, 3), pb.reshape(-1, 3)])
        ia = np.arange(E * L).reshape(E, L)
        ib = ia + E * L
        hi_a, lo_a, hi_b, lo_b = ia[:, :-1], ia[:, 1:], ib[:, :-1], ib[:, 1:]
        f = np.concatenate([np.stack([lo_a, lo_b, hi_b], -1).reshape(-1, 3),
                            np.stack([lo_a, hi_b, hi_a], -1).reshape(-1, 3)])
        v_list.append(v)
        f_list.append(f + n_v)
        n_v += len(v)

    def kolumny(idx, przes):
        p = xy[idx]
        zg, zd = z_gora[idx], z_dol[idx]
        if przes is None:
            return np.stack([np.column_stack([p, zg]), np.column_stack([p, zd])], axis=1)
        z1, z0 = ROWEK_Z[1], ROWEK_Z[0]
        w = p + przes
        st = lambda q, zz: np.column_stack([q, np.full(len(q), zz)])  # noqa: E731
        return np.stack([np.column_stack([p, zg]), st(p, z1), st(w, z1), st(w, z0), st(p, z0),
                         np.column_stack([p, zd])], axis=1)

    gladkie = np.flatnonzero(~g)
    if len(gladkie):
        pas(kolumny(gladkie, None), kolumny(nast[gladkie], None))
    rowkowe = np.flatnonzero(g)
    if len(rowkowe):
        pas(kolumny(rowkowe, w_pocz[rowkowe]), kolumny(nast[rowkowe], w_kon[rowkowe]))
    return np.concatenate(v_list), np.concatenate(f_list)


def siatka_plytki(uklad: Uklad, numer: int | None, krok_mm: float = 0.5, rowek: bool = True) -> trimesh.Trimesh:
    """Siatka plytki numer (None = plik bazowy: 3 dolki, bez reliefu) w ukladzie plytki."""
    if krok_mm <= 0:
        raise ValueError(f"krok_mm musi byc > 0, podano {krok_mm}")
    if numer is not None:
        kod_numeru(numer)  # numer 1-6, inaczej ValueError
    pol = uklad.rozmiar / 2
    n = max(int(round(uklad.rozmiar / krok_mm)), 8)
    os_ = np.linspace(-pol, pol, n + 1)
    gx, gy = np.meshgrid(os_, os_, indexing="ij")
    x, y = gx.ravel(), gy.ravel()
    z_gora, usun = mapa_gornej(uklad, numer, x, y)
    z_dol = _mapa_dolnej(uklad, x, y)
    # otwory przelotowe takze w dnie
    usun_dol = usun.copy()

    # zaokraglenie pionowych krawedzi R1 (narozniki bez wyciecia): rzut na luk
    c = pol - PROMIEN_NAROZNIKA
    ax, ay = np.abs(x), np.abs(y)
    wn = (ax > c) & (ay > c)
    dx, dy = ax[wn] - c, ay[wn] - c
    r = np.hypot(dx, dy)
    poza = r > PROMIEN_NAROZNIKA
    skala = np.where(poza, PROMIEN_NAROZNIKA / np.maximum(r, 1e-12), 1.0)
    x = x.copy()
    y = y.copy()
    x[wn] = np.sign(x[wn]) * (c + dx * skala)
    y[wn] = np.sign(y[wn]) * (c + dy * skala)

    x_min, _, _, y_max = uklad.wyciecie
    i_w = int(round((x_min + pol) / (uklad.rozmiar / n)))
    j_w = int(round((y_max + pol) / (uklad.rozmiar / n)))

    v_g = np.column_stack([x, y, z_gora])
    f_g = _trojkaty_siatki(n, ~usun, True)
    v_d = np.column_stack([x, y, z_dol])
    f_d = _trojkaty_siatki(n, ~usun_dol, False)

    obrys = _obrys(n, i_w, j_w)
    idx = obrys[:, 0] * (n + 1) + obrys[:, 1]
    # krawedzie w wycieciu D (x = x_min i y = y_max) bez rowka
    m = len(obrys)
    nast = np.roll(np.arange(m), -1)
    w_wycieciu = ((obrys[:, 0] == i_w) & (obrys[nast, 0] == i_w) & (obrys[:, 1] < j_w)) | \
                 ((obrys[:, 1] == j_w) & (obrys[nast, 1] == j_w) & (obrys[:, 0] >= i_w) & (obrys[nast, 0] > i_w))
    v_b, f_b = _boki(np.column_stack([x[idx], y[idx]]), z_gora[idx], z_dol[idx], ~w_wycieciu, rowek)

    v_g, f_g = _kompaktuj(v_g, f_g)
    v_d, f_d = _kompaktuj(v_d, f_d)
    v = np.concatenate([v_g, v_d, v_b])
    f = np.concatenate([f_g, f_d + len(v_g), f_b + len(v_g) + len(v_d)])
    siatka = trimesh.Trimesh(v, f, process=False)
    siatka.metadata["id"] = f"plytka-{uklad.nazwa}-{numer if numer is not None else 'baza'}"
    return siatka


# --- rozmieszczenie ---------------------------------------------------------------


def _srednica(projekt) -> float:
    return float(np.max(np.asarray(projekt.siatka.extents)[:2]))


def _jest_mostem(projekt) -> bool:
    return getattr(projekt, "rodzaj", "") == "most"


def rozmiesc(uklad: Uklad, pula, n_koron: int, n_mostow: int, ziarno: int) -> list[Rozmieszczenie]:
    """Losowe rozmieszczenie n_koron koron i n_mostow mostow z puli w gniazdach plytki.

    Wspolczynnik k (praca = projekt*k): plytka wieczorna (numery 1-3) - prace przed spiekaniem, k losowe
    1,20-1,25; plytka poranna (numery 4-6) - prace po spiekaniu, k = 1,0.
    Korony trafiaja do gniazd stozek (srednica*k + 1 <= d_top), gniazda od najmniejszych; w gniezdzie
    losowana pasujaca korona (najpierw jeszcze nieuzyte; projekty moga sie powtarzac). Mosty do rynienek
    (dlugosc*k + 2 <= l). Za duzo prac -> ValueError.
    """
    rng = np.random.default_rng(ziarno)
    stozki = [g for g in uklad.gniazda if g.rodzaj == "stozek"]
    rynienki = [g for g in uklad.gniazda if g.rodzaj == "rynienka"]
    if n_koron > len(stozki) or n_mostow > len(rynienki):
        raise ValueError(f"za duzo prac: {n_koron} koron i {n_mostow} mostow, plytka {uklad.nazwa} ma "
                         f"{len(stozki)} gniazd stozek i {len(rynienki)} gniazd rynienka")
    if n_koron < 0 or n_mostow < 0:
        raise ValueError("liczba prac nie moze byc ujemna")
    korony = [p for p in pula if not _jest_mostem(p)]
    mosty = [p for p in pula if _jest_mostem(p)]
    wieczor = min(uklad.numery) <= 3

    def losuj_k():
        return float(rng.uniform(*K_WIECZOR)) if wieczor else K_RANO

    wynik = []

    def wybierz(gniazda, kandydaci, pasuje, uzyte, rodzaj):
        for g in sorted(gniazda, key=lambda g: (g.d_gora or g.dlugosc, g.nr)):
            k = losuj_k()
            ok = [p for p in kandydaci if pasuje(p, k, g)]
            if not ok:
                raise ValueError(f"brak {rodzaj} w puli pasujacej do gniazda {g.nr} (k = {k:.3f})")
            nowe = [p for p in ok if id(p) not in uzyte]
            p = (nowe or ok)[int(rng.integers(len(nowe or ok)))]
            uzyte.add(id(p))
            yield g, p, k

    wybrane = sorted(rng.choice(len(stozki), n_koron, replace=False).tolist()) if n_koron else []
    for g, p, k in wybierz([stozki[i] for i in wybrane], korony,
                           lambda p, k, g: _srednica(p) * k + LUZ_KORONY_MM <= g.d_gora, set(), "korony"):
        r_luz = max(0.0, g.d_dol / 2 - _srednica(p) * k / 2)
        a, s = rng.uniform(0, 2 * math.pi), r_luz * math.sqrt(rng.uniform())
        wynik.append(Rozmieszczenie(p, g.nr, k, float(rng.uniform(0, 360)),
                                    (float(s * math.cos(a)), float(s * math.sin(a)))))

    def most_pasuje(p, k, g):
        ext = np.asarray(p.siatka.extents)
        return ext[0] * k + LUZ_MOSTU_MM <= g.dlugosc and ext[1] * k + LUZ_KORONY_MM <= g.szerokosc

    wybrane = sorted(rng.choice(len(rynienki), n_mostow, replace=False).tolist()) if n_mostow else []
    for g, p, k in wybierz([rynienki[i] for i in wybrane], mosty, most_pasuje, set(), "mostu"):
        luz = max(0.0, (g.dlugosc - np.asarray(p.siatka.extents)[0] * k) / 2 - LUZ_MOSTU_MM / 2)
        s = float(rng.uniform(-luz, luz))
        kat = math.radians(g.kat or 0.0)
        obrot = (g.kat or 0.0) + float(rng.choice([0.0, 180.0])) + float(rng.uniform(-2.0, 2.0))
        wynik.append(Rozmieszczenie(p, g.nr, k, obrot % 360, (s * math.cos(kat), s * math.sin(kat))))
    return sorted(wynik, key=lambda r: r.gniazdo)


# --- skan plytki ------------------------------------------------------------------


def _obrot_z(kat_deg: float) -> np.ndarray:
    a = math.radians(kat_deg)
    R = np.eye(4)
    R[:2, :2] = [[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]]
    return R


def _obrot_os(os_, kat_deg: float) -> np.ndarray:
    u = np.asarray(os_, dtype=np.float64)
    u = u / np.linalg.norm(u)
    a = math.radians(kat_deg)
    K = np.array([[0, -u[2], u[1]], [u[2], 0, -u[0]], [-u[1], u[0], 0]])
    R = np.eye(4)
    R[:3, :3] = np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * K @ K
    return R


def _T_plytki(T_plytki, rng) -> np.ndarray:
    if T_plytki is None:
        return np.eye(4)
    if isinstance(T_plytki, str):
        if T_plytki != "losowa":
            raise ValueError(f"T_plytki: None, 'losowa' albo macierz 4x4, podano '{T_plytki}'")
        a = rng.uniform(0, 2 * math.pi)
        os_ = (math.cos(a), math.sin(a), 0.0)
        T = _obrot_os(os_, rng.uniform(0, LOSOWA_PRZECHYL_DEG)) @ _obrot_z(
            rng.uniform(-LOSOWA_OBROT_Z_DEG, LOSOWA_OBROT_Z_DEG))
        b, s = rng.uniform(0, 2 * math.pi), LOSOWA_PRZESUNIECIE_MM * math.sqrt(rng.uniform())
        T[:3, 3] = [s * math.cos(b), s * math.sin(b), rng.uniform(-1.0, 1.0)]
        return T
    T = np.asarray(T_plytki, dtype=np.float64)
    if T.shape != (4, 4):
        raise ValueError(f"T_plytki musi byc macierza 4x4, ma ksztalt {T.shape}")
    return T


class _MapaMax:
    """Najwyzsze z juz polozonych prac w komorkach XY (do ukladania pracy na innej pracy)."""

    KROK = 0.5

    def __init__(self, v):
        k = self._klucze(v)
        kol = np.argsort(k)
        k, z = k[kol], v[kol, 2]
        self.klucze, start = np.unique(k, return_index=True)
        self.z = np.maximum.reduceat(z, start)

    def _klucze(self, v):
        ij = np.floor(v[:, :2] / self.KROK).astype(np.int64) + 100000
        return ij[:, 0] * 1000000 + ij[:, 1]

    def __call__(self, v):
        k = self._klucze(v)
        i = np.clip(np.searchsorted(self.klucze, k), 0, len(self.klucze) - 1)
        return np.where(self.klucze[i] == k, self.z[i], -np.inf)


def _poloz(uklad, numer, v, xy, obrot_z, podparcie=None):
    """Macierz pracy: obrot 180 st. wokol X, obrot Z, przesuniecie do xy, z oparte na powierzchni."""
    P = _obrot_z(obrot_z) @ np.diag([1.0, -1.0, -1.0, 1.0])
    P[:2, 3] = xy
    w = v @ P[:3, :3].T + P[:3, 3]
    # otwor o3 nie przepuszcza pracy: podparcie na poziomie dna gniazda (mapa ma tam -glebokosc)
    s, _ = mapa_gornej(uklad, numer, w[:, 0], w[:, 1])
    pol = uklad.rozmiar / 2
    s = np.where(_w_wycieciu(uklad, w[:, 0], w[:, 1]) | (np.abs(w[:, 0]) > pol) | (np.abs(w[:, 1]) > pol), -np.inf, s)
    if podparcie is not None:
        s = np.maximum(s, podparcie(w))
    if not np.isfinite(s).any():
        raise ValueError("praca nie ma podparcia na plytce")
    P[2, 3] = ODSTEP_OD_POWIERZCHNI_MM - float(np.min(w[:, 2] - s))
    return P


def skan_plytki(uklad: Uklad, numer: int | None, rozmieszczenia, ziarno: int, szum_mm: float = 0.02,
                T_plytki=None):
    """Skan plytki z pracami: (Trimesh, Prawda).

    Plytka bez szumu (krok 0,2 mm) + skany prac (qc.syntetyka.skan.skan_pracy z opcjami rozmieszczenia,
    poza kluczem "stan") polozone w gniazdach; wspolna transformacja T_plytki (None = tozsamosc,
    "losowa" = obrot Z <= 5 st., przechyl <= 1 st., przesuniecie <= 3 mm, albo macierz 4x4).
    Stan "podwojne" = praca polozona na innej pracy w jej gniezdzie; "poza_gniazdem" = praca na sciance.
    Zakresy scian: plytka pierwsza, potem prace w kolejnosci rozmieszczen; tasowanie tylko w zakresach.
    """
    rng = np.random.default_rng(ziarno)
    T = _T_plytki(T_plytki, rng)
    plyta = siatka_plytki(uklad, numer, krok_mm=KROK_PLYTKI_SKANU_MM)

    stany = []
    for r in rozmieszczenia:
        stan = r.opcje.get("stan", "praca")
        if stan not in STANY:
            raise ValueError(f"nieznany stan pracy '{stan}' (dozwolone: {', '.join(STANY)})")
        stany.append(stan)
    zwykle = [i for i, s in enumerate(stany) if s == "praca"]

    siatki, prawdy, macierze, gniazda = {}, {}, {}, {}
    kolejnosc = zwykle + [i for i, s in enumerate(stany) if s != "praca"]
    for i in kolejnosc:
        r = rozmieszczenia[i]
        opcje = {k: w for k, w in r.opcje.items() if k != "stan"}
        siatka, pp = skan_pracy(r.projekt, ziarno=int(ziarno) * 1000 + i, wspolczynnik=r.wspolczynnik,
                                szum_mm=szum_mm, **opcje)
        v = np.asarray(siatka.vertices, dtype=np.float64)
        stan = stany[i]
        if stan == "praca":
            g = uklad.gniazdo(r.gniazdo)
            P = _poloz(uklad, numer, v, np.add(g.xy, r.przesuniecie_xy), r.obrot_z_deg)
            gniazda[i] = g.nr
        elif stan == "podwojne":
            if not zwykle:
                raise ValueError("stan 'podwojne' wymaga innej pracy w gniezdzie")
            cel = zwykle[i % len(zwykle)]
            g = uklad.gniazdo(gniazda[cel])
            w_pod = np.asarray(siatki[cel].vertices) @ macierze[cel][:3, :3].T + macierze[cel][:3, 3]
            a = rng.uniform(0, 2 * math.pi)
            xy = np.add(g.xy, (0.8 * math.cos(a), 0.8 * math.sin(a)))
            P = _poloz(uklad, numer, v, xy, r.obrot_z_deg, podparcie=_MapaMax(w_pod))
            gniazda[i] = g.nr
        else:
            P = _poloz_poza(uklad, numer, v, r.obrot_z_deg, rng)
            gniazda[i] = None
        siatki[i], prawdy[i], macierze[i] = siatka, pp, P

    # tasowanie plytki w jej zakresie
    vp = np.asarray(plyta.vertices, dtype=np.float64)
    fp = np.asarray(plyta.faces, dtype=np.int64)
    perm = rng.permutation(len(vp))
    odwr = np.empty_like(perm)
    odwr[perm] = np.arange(len(vp))
    vp, fp = vp[perm], odwr[fp][rng.permutation(len(fp))]

    v_list, f_list, prace = [vp], [fp], []
    n_v, n_f = len(vp), len(fp)
    for i in range(len(rozmieszczenia)):
        r, siatka, pp = rozmieszczenia[i], siatki[i], prawdy[i]
        M = macierze[i]
        v = np.asarray(siatka.vertices, dtype=np.float64) @ M[:3, :3].T + M[:3, 3]
        f = np.asarray(siatka.faces, dtype=np.int64)
        v_list.append(v)
        f_list.append(f + n_v)
        prace.append(PrawdaPracy(
            id=str(getattr(r.projekt, "id", pp.id)), wspolczynnik=pp.wspolczynnik,
            T_projekt_do_skanu=T @ M @ pp.T_projekt_do_skanu, zakres_scian=[n_f, n_f + len(f)],
            gniazdo=gniazda[i], stan=stany[i], drgniecie=pp.drgniecie, pokrycie=pp.pokrycie,
            ubytki=pp.ubytki))
        n_v += len(v)
        n_f += len(f)

    v = np.concatenate(v_list)
    v = v @ T[:3, :3].T + T[:3, 3]
    siatka = trimesh.Trimesh(v, np.concatenate(f_list), process=False)
    pr = Prawda(ziarno=int(ziarno), szum_mm=float(szum_mm), gestosc_mm=KROK_PLYTKI_SKANU_MM,
                plytka={"uklad": uklad.nazwa, "numer": numer,
                        "T_skan_do_plytki": np.linalg.inv(T).tolist()},
                prace=prace)
    return siatka, pr


def _poloz_poza(uklad, numer, v, obrot_z, rng, proby=400):
    """Praca lezaca na sciance: srodek poza obrysami gniazd, najnizszy punkt >= -0,5."""
    pol = uklad.rozmiar / 2
    r = float(np.max(np.ptp(v[:, :2], axis=0))) / 2
    probka = v[:: max(1, len(v) // 3000)]
    for _ in range(proby):
        xy = rng.uniform(-(pol - r - 0.5), pol - r - 0.5, size=2)
        if uklad.gniazdo_dla_xy(*xy) is not None:
            continue
        P = _poloz(uklad, numer, probka, xy, obrot_z)
        w = probka @ P[:3, :3].T + P[:3, 3]
        c = (w.min(axis=0) + w.max(axis=0)) / 2
        if w[:, 2].min() < -0.3 or uklad.gniazdo_dla_xy(c[0], c[1]) is not None:
            continue
        P = _poloz(uklad, numer, v, xy, obrot_z)
        w = v @ P[:3, :3].T + P[:3, 3]
        c = (w.min(axis=0) + w.max(axis=0)) / 2
        if w[:, 2].min() >= -0.5 and uklad.gniazdo_dla_xy(c[0], c[1]) is None:
            return P
    raise ValueError("nie znaleziono miejsca na sciance dla pracy poza gniazdem")
