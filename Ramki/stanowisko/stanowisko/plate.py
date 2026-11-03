"""plate — wyrównanie skanu płytki do jej układu, numer płytki z dołków kodu, cięcie na gniazda.

Wejście: siatka skanu całej płytki (STL ze skanera albo z ``synth``) w dowolnym układzie
(skaner ma własny; zakładamy tylko, że góra płytki patrzy mniej więcej w +z skanera).
Wyjście: macierz 4×4 skan → układ płytki (STL: wierzch na z = ``thickness``), numer płytki,
lista fragmentów (punkty z normalnymi nad każdym gniazdem), gniazda puste / podwójne /
prace poza gniazdem, metryki jakości.

Kroki:
1. płaszczyzna wierzchu płytki (RANSAC na próbce, potem SVD na punktach ≤ 0,1 mm) → wypoziomowanie,
2. mapa wysokości (0,25 mm/px) → składowe wgłębień ø4–6,5 mm o głębokości ≈ 3 mm = kandydaci na stożki
   znaczników (ø5 × 3, z = z_top − 3 + 1,2·r),
3. dopasowanie stożka o znanym kącie metodą najmniejszych kwadratów do surowych punktów każdego kandydata
   (środek x, y i z wierzchołka; odrzucanie punktów > 0,15 mm),
4. przypisanie trzech środków do znaczników A, B, C z ``uklad.json`` (wszystkie uporządkowane trójki,
   Kabsch 2D bez odbicia; trójkąt jest nierównoboczny, więc najmniejsza reszta jest jednoznaczna),
5. ICP punkt–płaszczyzna (Open3D) skanu do modelu STL płytki, tylko na wierzchu i stożkach (prace
   w gniazdach nie biorą udziału) — dopracowanie i miara zgodności,
6. numer z dołków kodu (ø2 × 1: w promieniu 0,8 mm od środka dołka 5. percentyl z < z_top − 0,4),
   dołek bez punktów = niewidoczny → numer nieznany, chyba że podany (``numer``),
7. cięcie: punkty, które nie leżą na modelu płytki (odległość do STL > 0,12 mm), grupowane DBSCAN
   (0,5 mm) → fragmenty; fragment → gniazdo, nad którym leży jego środek (margines 1 mm); gniazdo
   bez fragmentu = puste, z dwoma = podwójne, fragment poza gniazdami = poza gniazdem.
"""
from __future__ import annotations

import itertools
import math
import time
import warnings
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import open3d as o3d
import trimesh
from scipy import ndimage
from scipy.optimize import least_squares
from scipy.spatial import cKDTree

from . import uklad as U

PX_MAPY = 0.25  # mm na piksel mapy wysokości
PROG_PLASZCZYZNY = 0.1  # mm: punkt należy do wierzchu płytki
NACHYLENIE_STOZKA = None  # liczone z d/depth znacznika: dz/dr = depth / (d/2)
RESZTA_STOZKA_MAX = 0.08  # mm RMS dopasowania stożka (szum skanu σ ≈ 0,03)
RESZTA_ZNACZNIKOW_MAX = 0.3  # mm: reszta Kabscha dla przyjętego przypisania
PROG_PLYTKI = 0.12  # mm: punkt bliżej modelu płytki niż to = płytka, nie praca
PROG_NORMALNEJ = -0.3  # cos kąta normalna skanu · normalna modelu; praca oparta o ściankę ma ≈ −1, szum normalnych skanu sięga ±0,3
EPS_DBSCAN = 0.5  # mm: łączenie punktów pracy w fragment
MIN_PUNKTOW_FRAGMENTU = 300
MIN_ROZMIAR_FRAGMENTU_XY = 3.0  # mm: mniejsze skupisko to okruch, nie praca (najmniejsza korona ~6 mm)
MIN_ROZMIAR_FRAGMENTU_Z = 1.5
MARGINES_GNIAZDA = 1.0  # mm: fragment „nad gniazdem” także tuż za obrysem
GLEBOKOSC_DOLKA_MIN = 0.4  # mm: dołek kodu (ø2 × 1) uznany za obecny
MIN_PUNKTOW_DOLKA = 15


class BladWyrownania(RuntimeError):
    """Nie udało się wyrównać skanu do układu płytki (brak płaszczyzny / znaczników)."""


@dataclass
class Fragment:
    gniazdo: int | None  # None = poza gniazdem
    punkty: np.ndarray  # N×3, układ płytki
    normalne: np.ndarray  # N×3
    status: str = "praca"  # praca | podwojny | poza_gniazdem | drobny
    srodek: tuple[float, float, float] = (0.0, 0.0, 0.0)
    udzial_w_gniezdzie: float = 1.0  # jaka część punktów leży nad obrysem gniazda (+ margines)

    @property
    def liczba(self) -> int:
        return len(self.punkty)

    def bbox(self) -> list[float]:
        return (self.punkty.max(0) - self.punkty.min(0)).tolist()


@dataclass
class WynikWyrownania:
    plytka: str
    macierz: np.ndarray  # 4×4 skan → układ płytki
    numer: int | None
    numer_zrodlo: str  # dolki | podany | nieznany
    bity: list  # bool albo None (dołek niewidoczny), kolejność A, B, C[, D]
    numer_z_dolkow: int | None
    fragmenty: list[Fragment]
    gniazda_puste: list[int]
    gniazda_podwojne: list[int]
    jakosc: dict = field(default_factory=dict)

    @property
    def poza_gniazdem(self) -> list[Fragment]:
        return [f for f in self.fragmenty if f.status == "poza_gniazdem"]


# ----------------------------------------------------------------------------
# 1. płaszczyzna wierzchu
# ----------------------------------------------------------------------------
def probka_powierzchni(skan: trimesh.Trimesh, ile: int, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """``ile`` punktów równomiernie po powierzchni siatki (z normalnymi trójkątów).

    Wierzchołki siatki nie są równomierne (skaner i generator zagęszczają krzywizny, płaski
    wierzch ma rzadkie wierzchołki), więc płaszczyznę liczy się z próbki po polu powierzchni.
    """
    pts, fid = trimesh.sample.sample_surface(skan, ile, seed=int(rng.integers(2**31)))
    return np.asarray(pts, dtype=np.float64), np.asarray(skan.face_normals[fid], dtype=np.float64)


def plaszczyzna_wierzchu(P: np.ndarray, N: np.ndarray, rng: np.random.Generator, prog: float = PROG_PLASZCZYZNY) -> tuple[np.ndarray, float, dict]:
    """Dominująca płaszczyzna (wierzch płytki): normalna (z > 0) i d (n·p = d).

    RANSAC (Open3D) na próbce, potem dwa razy SVD na punktach ≤ ``prog`` od płaszczyzny, których
    normalna odchyla się od niej < 8° (skośne ścianki gniazd 15° i stożki nie ciągną płaszczyzny).
    """
    if len(P) < 1000:
        raise BladWyrownania(f"za mało punktów w skanie ({len(P)})")
    o3d.utility.random.seed(int(rng.integers(2**31)))
    sel = rng.choice(len(P), min(len(P), 80000), replace=False)
    pc = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(P[sel]))
    model, _ = pc.segment_plane(distance_threshold=prog, ransac_n=3, num_iterations=3000)
    n = np.asarray(model[:3])
    d = -float(model[3])
    if n[2] < 0:
        n, d = -n, -d
    cos_max = math.cos(math.radians(8.0))
    bl = None
    for _ in range(3):
        odl = P @ n - d
        bl = (np.abs(odl) < prog) & (np.abs(N @ n) > cos_max)
        if bl.sum() < 500:
            raise BladWyrownania("nie znaleziono płaskiego wierzchu płytki w skanie")
        Q = P[bl]
        c = Q.mean(0)
        _, _, vt = np.linalg.svd(Q - c, full_matrices=False)
        n = vt[2]
        if n[2] < 0:
            n = -n
        d = float(c @ n)
    odl = P @ n - d
    rms = float(np.sqrt(np.mean(odl[bl] ** 2)))
    return n, d, {"plaszczyzna_punkty": int(bl.sum()), "plaszczyzna_rms_mm": rms, "plaszczyzna_udzial": float(bl.mean())}


def macierz_poziomowania(n: np.ndarray, d: float, z_top: float) -> np.ndarray:
    """4×4: obraca normalną ``n`` na +z i przesuwa płaszczyznę n·p = d na z = ``z_top``."""
    z = np.array([0.0, 0.0, 1.0])
    v = np.cross(n, z)
    s, c = np.linalg.norm(v), float(n @ z)
    if s < 1e-12:
        R = np.eye(3)
    else:
        K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
        R = np.eye(3) + K + K @ K * ((1 - c) / s**2)
    T = np.eye(4)
    T[:3, :3] = R
    T[2, 3] = z_top - d  # po obrocie płaszczyzna leży na z = d
    return T


# ----------------------------------------------------------------------------
# 2–3. znaczniki
# ----------------------------------------------------------------------------
def mapa_wysokosci(P: np.ndarray, px: float) -> tuple[np.ndarray, np.ndarray]:
    xy0 = P[:, :2].min(0) - px
    ij = np.floor((P[:, :2] - xy0) / px).astype(int)
    w, h = ij.max(0) + 2
    Z = np.full((h, w), -np.inf)
    np.maximum.at(Z, (ij[:, 1], ij[:, 0]), P[:, 2])
    return Z, xy0


def kandydaci_znacznikow(P: np.ndarray, z_top: float, zn: U.Znacznik, px: float = PX_MAPY) -> list[tuple[float, float]]:
    """Środki (x, y) wgłębień w mapie wysokości o rozmiarze i głębokości stożka znacznika."""
    Z, xy0 = mapa_wysokosci(P, px)
    dep = np.where(np.isfinite(Z), z_top - Z, 0.0)
    maska = dep > 0.3
    lab, n = ndimage.label(maska)
    if n == 0:
        return []
    idx = np.arange(1, n + 1)
    pola = ndimage.sum(maska, lab, idx) * px * px
    gleb = ndimage.maximum(dep, lab, idx)
    sr = ndimage.center_of_mass(maska, lab, idx)
    r = zn.d / 2
    pole_min, pole_max = math.pi * (r - 0.7) ** 2, math.pi * (r + 1.0) ** 2
    out = []
    for k in range(n):
        if pole_min <= pola[k] <= pole_max and zn.depth - 0.6 <= gleb[k] <= zn.depth + 0.4:
            cy, cx = sr[k]
            out.append((float(xy0[0] + (cx + 0.5) * px), float(xy0[1] + (cy + 0.5) * px)))
    return out


def dopasuj_stozek(P: np.ndarray, srodek0: tuple[float, float], z_top: float, zn: U.Znacznik) -> dict | None:
    """Najmniejsze kwadraty: środek (x, y) i z wierzchołka stożka o znanym kącie (z = z_a + k·r)."""
    k = zn.depth / (zn.d / 2)
    r0 = zn.d / 2
    bl = np.hypot(P[:, 0] - srodek0[0], P[:, 1] - srodek0[1]) < r0 + 1.0
    Q = P[bl]
    Q = Q[(Q[:, 2] < z_top - 0.15) & (Q[:, 2] > z_top - zn.depth - 0.3)]
    if len(Q) < 100:
        return None
    x0 = np.array([srodek0[0], srodek0[1], z_top - zn.depth])

    def reszty(p, Q=Q):
        return p[2] + k * np.hypot(Q[:, 0] - p[0], Q[:, 1] - p[1]) - Q[:, 2]

    p = x0
    for _ in range(3):  # dopasowanie z odrzucaniem punktów daleko od stożka (brzeg, wierzchołek, szum)
        res = least_squares(reszty, p, kwargs={"Q": Q}, loss="soft_l1", f_scale=0.05)
        p = res.x
        r = reszty(p, Q)
        dobre = np.abs(r) < 0.15
        rr = np.hypot(Q[:, 0] - p[0], Q[:, 1] - p[1])
        dobre &= (rr > 0.3) & (rr < r0 - 0.15)  # bez wierzchołka i bez krawędzi
        if dobre.sum() < 100:
            return None
        Q = Q[dobre]
    r = reszty(p, Q)
    return {"x": float(p[0]), "y": float(p[1]), "z_wierzcholka": float(p[2]), "rms": float(np.sqrt(np.mean(r**2))), "punkty": int(len(Q))}


def kabsch_2d(A: np.ndarray, B: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    """Obrót (bez odbicia) i przesunięcie 2D: B ≈ R·A + t; zwraca (R, t, RMS reszt)."""
    ca, cb = A.mean(0), B.mean(0)
    H = (A - ca).T @ (B - cb)
    Uu, _, Vt = np.linalg.svd(H)
    D = np.diag([1.0, np.sign(np.linalg.det(Vt.T @ Uu.T))])
    R = Vt.T @ D @ Uu.T
    t = cb - R @ ca
    r = (A @ R.T + t) - B
    return R, t, float(np.sqrt(np.mean(np.sum(r**2, 1))))


def przypisz_znaczniki(srodki: list[dict], uk: U.UkladPlytki) -> tuple[np.ndarray, dict]:
    """Wybiera trójkę wykrytych stożków i ich przypisanie do A, B, C o najmniejszej reszcie Kabscha."""
    cel = np.array([[z.x, z.y] for z in uk.markers])
    if len(srodki) < 3:
        raise BladWyrownania(f"znaleziono {len(srodki)} stożki znaczników, potrzeba 3")
    pts = np.array([[s["x"], s["y"]] for s in srodki])
    wyniki = []
    for trojka in itertools.permutations(range(len(srodki)), 3):
        R, t, rms = kabsch_2d(pts[list(trojka)], cel)
        wyniki.append((rms, trojka, R, t))
    wyniki.sort(key=lambda w: w[0])
    rms, trojka, R, t = wyniki[0]
    druga = wyniki[1][0] if len(wyniki) > 1 else math.inf
    if rms > RESZTA_ZNACZNIKOW_MAX:
        raise BladWyrownania(f"stożki nie pasują do znaczników płytki {uk.nazwa}: reszta {rms:.3f} mm > {RESZTA_ZNACZNIKOW_MAX}")
    T = np.eye(4)
    T[:2, :2] = R
    T[:2, 3] = t
    return T, {"znaczniki_reszta_mm": rms, "znaczniki_reszta_druga_mm": druga, "znaczniki_kolejnosc": list(trojka)}


# ----------------------------------------------------------------------------
# 5. ICP do modelu płytki
# ----------------------------------------------------------------------------
def _chmura(P: np.ndarray, N: np.ndarray | None = None) -> o3d.geometry.PointCloud:
    pc = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(np.ascontiguousarray(P, dtype=np.float64)))
    if N is not None:
        pc.normals = o3d.utility.Vector3dVector(np.ascontiguousarray(N, dtype=np.float64))
    return pc


def maska_plytki_do_icp(P: np.ndarray, uk: U.UkladPlytki) -> np.ndarray:
    """Punkty do ICP: wierzch płytki (±0,25 mm od z_top, poza gniazdami) i stożki znaczników."""
    zt = uk.thickness
    wierzch = np.abs(P[:, 2] - zt) < 0.25
    for g in uk.sockets:  # bez punktów nad gniazdami (prace, krawędzie otworów)
        if g.okragle:
            wierzch &= np.hypot(P[:, 0] - g.x, P[:, 1] - g.y) > g.d_top / 2 + 0.5
        else:
            a = math.radians(g.angle)
            dx, dy = P[:, 0] - g.x, P[:, 1] - g.y
            u = dx * math.cos(a) + dy * math.sin(a)
            v = -dx * math.sin(a) + dy * math.cos(a)
            wierzch &= np.hypot(np.maximum(np.abs(u) - (g.l - g.w) / 2, 0), v) - g.w / 2 > 0.5
    stozki = np.zeros(len(P), dtype=bool)
    for z in uk.markers:
        stozki |= (np.hypot(P[:, 0] - z.x, P[:, 1] - z.y) < z.d / 2 + 0.3) & (P[:, 2] < zt - 0.1) & (P[:, 2] > zt - z.depth - 0.3)
    return wierzch | stozki


def icp_do_modelu(P: np.ndarray, N: np.ndarray, uk: U.UkladPlytki, plik_modelu: Path, rng: np.random.Generator) -> tuple[np.ndarray, dict]:
    """ICP punkt–płaszczyzna skanu (wierzch + stożki) do modelu STL płytki; zwraca 4×4 poprawkę i miary."""
    m = o3d.io.read_triangle_mesh(str(plik_modelu))
    cel = m.sample_points_uniformly(number_of_points=600000, use_triangle_normal=True)
    C = np.asarray(cel.points)
    cel = cel.select_by_index(np.flatnonzero(maska_plytki_do_icp(C, uk)))
    sel = np.flatnonzero(maska_plytki_do_icp(P, uk))
    if len(sel) > 80000:
        sel = rng.choice(sel, 80000, replace=False)
    zr = _chmura(P[sel], N[sel])
    T = np.eye(4)
    wynik = None
    for prog in (0.3, 0.12):
        wynik = o3d.pipelines.registration.registration_icp(
            zr, cel, prog, T, o3d.pipelines.registration.TransformationEstimationPointToPlane(),
            o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=60),
        )
        T = np.asarray(wynik.transformation)
    kat = math.degrees(math.acos(min(1.0, (np.trace(T[:3, :3]) - 1) / 2)))
    return T, {"icp_fitness": float(wynik.fitness), "icp_rmse_mm": float(wynik.inlier_rmse), "icp_punkty": int(len(sel)),
               "icp_poprawka_mm": float(np.linalg.norm(T[:3, 3])), "icp_poprawka_deg": kat}


# ----------------------------------------------------------------------------
# 6. numer z dołków
# ----------------------------------------------------------------------------
def odczytaj_bity(P: np.ndarray, uk: U.UkladPlytki) -> list:
    """Dla każdego dołka kodu: True (wgłębienie), False (płasko), None (brak punktów = poza skanem)."""
    bity = []
    for d in uk.code_dimples:
        bl = np.hypot(P[:, 0] - d.x, P[:, 1] - d.y) < d.d / 2 - 0.2
        if bl.sum() < MIN_PUNKTOW_DOLKA:
            bity.append(None)
            continue
        z5 = np.percentile(P[bl, 2], 5)
        bity.append(bool(z5 < uk.thickness - GLEBOKOSC_DOLKA_MIN))
    return bity


# ----------------------------------------------------------------------------
# 7. cięcie na gniazda
# ----------------------------------------------------------------------------
def odleglosc_do_modelu(P: np.ndarray, plik_modelu: Path) -> np.ndarray:
    return odleglosc_i_normalna_modelu(P, plik_modelu)[0]


def odleglosc_i_normalna_modelu(P: np.ndarray, plik_modelu: Path) -> tuple[np.ndarray, np.ndarray]:
    """Odległość każdego punktu do siatki STL i normalna najbliższego trójkąta modelu."""
    m = o3d.io.read_triangle_mesh(str(plik_modelu))
    scena = o3d.t.geometry.RaycastingScene()
    scena.add_triangles(o3d.t.geometry.TriangleMesh.from_legacy(m))
    wyn = scena.compute_closest_points(o3d.core.Tensor(np.ascontiguousarray(P, dtype=np.float32)))
    bliskie = wyn["points"].numpy()
    nm = wyn["primitive_normals"].numpy().astype(np.float64)
    nm /= np.maximum(np.linalg.norm(nm, axis=1, keepdims=True), 1e-12)  # Open3D zwraca normalne nieznormalizowane
    return np.linalg.norm(bliskie - P, axis=1), nm


def punkty_plytki(P: np.ndarray, N: np.ndarray, plik_modelu: Path, prog: float = PROG_PLYTKI) -> np.ndarray:
    """Maska punktów leżących na płytce: blisko modelu STL (≤ ``prog``) i z normalną zgodną z modelem.

    Praca oparta o ściankę stożka ma punkty tak samo blisko ścianki, ale jej normalna jest
    przeciwna do normalnej ścianki (dwie powierzchnie stykają się „plecami”) — te punkty zostają pracą.
    """
    odl, nm = odleglosc_i_normalna_modelu(P, plik_modelu)
    zgodne = np.einsum("ij,ij->i", N, nm)
    brak_normalnej = np.linalg.norm(N, axis=1) < 0.5
    return (odl <= prog) & ((zgodne > PROG_NORMALNEJ) | brak_normalnej)


def _maska_pracy(P: np.ndarray, N: np.ndarray, zt: float, plik_modelu: Path) -> np.ndarray:
    nisko = P[:, 2] < zt + 0.7  # nad tym nie ma płytki (relief numeru 0,6)
    plytka = np.zeros(len(P), dtype=bool)
    plytka[nisko] = punkty_plytki(P[nisko], N[nisko], plik_modelu)
    return ~plytka


def potnij_na_fragmenty(
    P: np.ndarray, N: np.ndarray, Ps: np.ndarray, Ns: np.ndarray, uk: U.UkladPlytki, plik_modelu: Path
) -> tuple[list[Fragment], dict]:
    """Punkty poza modelem płytki → DBSCAN → fragmenty przypisane do gniazd.

    Grupowanie liczy się na punktach próbkowanych równomiernie po powierzchni (``Ps``), nie na
    wierzchołkach: w siatce z projektu kanał śruby ma pierścień gęstych wierzchołków i długie
    trójkąty bez wierzchołków obok, więc DBSCAN na wierzchołkach odcinał go jako osobną wyspę.
    Fragment dostaje wierzchołki skanu (``P``, z normalnymi) przypisane do najbliższego punktu próbki.
    """
    praca = _maska_pracy(P, N, uk.thickness, plik_modelu)
    W, WN = P[praca], N[praca]
    Ws = Ps[_maska_pracy(Ps, Ns, uk.thickness, plik_modelu)]
    if len(W) == 0 or len(Ws) == 0:
        return [], {"punkty_prac": 0, "punkty_plytki": int((~praca).sum()), "fragmenty_drobne": 0, "skupiska_pominiete": 0}
    pcd = _chmura(Ws).voxel_down_sample(0.2)
    etyk_d = np.asarray(pcd.cluster_dbscan(eps=EPS_DBSCAN, min_points=6))
    D = np.asarray(pcd.points)
    odl, naj = cKDTree(D).query(W, k=1)
    etyk = np.where(odl < 1.0, etyk_d[naj], -1)
    plytka = ~praca
    fragmenty = []
    for e in np.unique(etyk):
        if e < 0:
            continue
        sel = etyk == e
        if sel.sum() < MIN_PUNKTOW_FRAGMENTU:
            continue
        Q, QN = W[sel], WN[sel]
        rozm = Q.max(0) - Q.min(0)
        drobny = max(rozm[0], rozm[1]) < MIN_ROZMIAR_FRAGMENTU_XY or rozm[2] < MIN_ROZMIAR_FRAGMENTU_Z
        cx, cy = float(np.median(Q[:, 0])), float(np.median(Q[:, 1]))
        g = uk.najblizsze_gniazdo(cx, cy, MARGINES_GNIAZDA)
        udzial = 0.0
        if g is not None:
            udzial = float(np.mean([g.zawiera(x, y, MARGINES_GNIAZDA + 0.5) for x, y in Q[:: max(1, len(Q) // 500), :2]]))
        f = Fragment(gniazdo=g.id if g is not None else None, punkty=Q, normalne=QN, srodek=(cx, cy, float(Q[:, 2].mean())), udzial_w_gniezdzie=udzial)
        if drobny:
            f.status = "drobny"  # okruch / szum: nie liczy się jako praca ani jako „podwójne”
        elif g is None or udzial < 0.6:
            f.status = "poza_gniazdem"
            f.gniazdo = None
        fragmenty.append(f)
    fragmenty.sort(key=lambda f: (f.gniazdo is None, f.gniazdo or 0, -f.liczba))
    licznik: dict[int, int] = {}
    for f in fragmenty:
        if f.gniazdo is not None and f.status == "praca":
            licznik[f.gniazdo] = licznik.get(f.gniazdo, 0) + 1
    for f in fragmenty:
        if f.status == "praca" and licznik[f.gniazdo] > 1:
            f.status = "podwojny"
    return fragmenty, {"punkty_prac": int(len(W)), "punkty_plytki": int(plytka.sum()), "fragmenty_drobne": int(sum(1 for f in fragmenty if f.status == "drobny")),
                       "skupiska_pominiete": int(sum(1 for e in np.unique(etyk) if e >= 0 and (etyk == e).sum() < MIN_PUNKTOW_FRAGMENTU))}


# ----------------------------------------------------------------------------
# całość
# ----------------------------------------------------------------------------
def plik_modelu_plytki(uk: U.UkladPlytki, numer: int | None) -> Path:
    if numer is not None and numer in uk.numery:
        return uk.plik_stl(numer)
    return uk.plik_stl(uk.numery[0])


def wyrownaj(
    skan: trimesh.Trimesh, uk: U.UkladPlytki, numer: int | None = None, seed: int = 0, icp: bool = True, ciecie: bool = True
) -> WynikWyrownania:
    """Pełny przebieg plate na siatce skanu; ``numer`` podany przez użytkownika ma pierwszeństwo nad dołkami."""
    t0 = time.time()
    rng = np.random.default_rng(seed)
    P0 = np.asarray(skan.vertices, dtype=np.float64)
    N0 = np.asarray(skan.vertex_normals, dtype=np.float64)
    N0 = np.where(np.isfinite(N0), N0, 0.0)
    jak: dict = {"punkty": int(len(P0))}

    Ps, Ns = probka_powierzchni(skan, 1500000, rng)
    n, d, j = plaszczyzna_wierzchu(Ps, Ns, rng)
    jak.update(j)
    T1 = macierz_poziomowania(n, d, uk.thickness)
    P1 = P0 @ T1[:3, :3].T + T1[:3, 3]
    Ps1 = Ps @ T1[:3, :3].T + T1[:3, 3]
    zn = uk.markers[0]
    kand = kandydaci_znacznikow(np.vstack([P1, Ps1]), uk.thickness, zn)  # wierzchołki + próbka (płaski wierzch ma rzadkie wierzchołki)
    stozki = []
    for k in kand:
        s = dopasuj_stozek(P1, k, uk.thickness, zn)
        if s is not None and s["rms"] <= RESZTA_STOZKA_MAX and abs(s["z_wierzcholka"] - (uk.thickness - zn.depth)) < 0.3:
            stozki.append(s)
    jak["stozki_kandydaci"] = len(kand)
    jak["stozki_dopasowane"] = len(stozki)
    jak["stozki_rms_mm"] = [round(s["rms"], 4) for s in stozki]
    T2, j = przypisz_znaczniki(stozki, uk)
    jak.update(j)
    T = T2 @ T1
    if icp:
        N1 = N0 @ T[:3, :3].T
        P2 = P0 @ T[:3, :3].T + T[:3, 3]
        T3, j = icp_do_modelu(P2, N1, uk, plik_modelu_plytki(uk, numer), rng)
        jak.update(j)
        T = T3 @ T
    P = P0 @ T[:3, :3].T + T[:3, 3]
    N = N0 @ T[:3, :3].T
    Ps2 = Ps @ T[:3, :3].T + T[:3, 3]
    Ns2 = Ns @ T[:3, :3].T
    jak["czas_wyrownania_s"] = round(time.time() - t0, 2)

    bity = odczytaj_bity(Ps2, uk)  # próbka po powierzchni: równomierna także na płaskim wierzchu
    numer_z_dolkow = None
    if all(b is not None for b in bity):
        numer_z_dolkow = uk.numer_z_bitow(*bity)
    if numer is not None:
        zrodlo = "podany"
        if numer_z_dolkow is not None and numer_z_dolkow != numer:
            warnings.warn(f"numer płytki podany {numer}, z dołków odczytano {numer_z_dolkow} — używam podanego", stacklevel=2)
    elif numer_z_dolkow is not None:
        numer, zrodlo = numer_z_dolkow, "dolki"
        if numer not in uk.numery:
            warnings.warn(f"numer płytki z dołków {numer} nie ma modelu w {uk.katalog} (są: {uk.numery})", stacklevel=2)
    else:
        zrodlo = "nieznany"
        warnings.warn(
            f"dołki kodu poza skanem ({sum(b is None for b in bity)} z {len(bity)} niewidocznych) — podaj numer płytki (--numer)",
            stacklevel=2,
        )

    fragmenty: list[Fragment] = []
    puste, podwojne = [], []
    if ciecie:
        t1 = time.time()
        fragmenty, j = potnij_na_fragmenty(P, N, Ps2, Ns2, uk, plik_modelu_plytki(uk, numer))
        jak.update(j)
        zajete = {f.gniazdo for f in fragmenty if f.gniazdo is not None and f.status in ("praca", "podwojny")}
        puste = [g.id for g in uk.sockets if g.id not in zajete]
        podwojne = sorted({f.gniazdo for f in fragmenty if f.status == "podwojny"})
        jak["czas_ciecia_s"] = round(time.time() - t1, 2)
    jak["czas_s"] = round(time.time() - t0, 2)
    return WynikWyrownania(
        plytka=uk.nazwa, macierz=T, numer=numer, numer_zrodlo=zrodlo, bity=bity, numer_z_dolkow=numer_z_dolkow,
        fragmenty=fragmenty, gniazda_puste=puste, gniazda_podwojne=podwojne, jakosc=jak,
    )


def blad_wyrownania(T: np.ndarray, poza_skanu: np.ndarray | None, promien: float = 50.0) -> dict:
    """Błąd macierzy skan → płytka wobec prawdy (``poza_skanu``: płytka → skan): translacja, obrót, max przesunięcie na kole."""
    P = np.eye(4) if poza_skanu is None else np.asarray(poza_skanu)
    E = T @ P  # powinno być tożsamością
    R = E[:3, :3]
    kat = math.degrees(math.acos(min(1.0, max(-1.0, (np.trace(R) - 1) / 2))))
    t = np.linalg.norm(E[:3, 3])
    th = np.linspace(0, 2 * math.pi, 72, endpoint=False)
    okrag = np.c_[promien * np.cos(th), promien * np.sin(th), np.full(72, 8.0)]
    przes = np.linalg.norm(okrag @ R.T + E[:3, 3] - okrag, axis=1)
    return {"translacja_mm": float(t), "obrot_deg": float(kat), "max_przesuniecie_mm": float(przes.max()), "przesuniecie_srodka_mm": float(np.linalg.norm(E[:3, :3] @ [0, 0, 8] + E[:3, 3] - [0, 0, 8]))}
