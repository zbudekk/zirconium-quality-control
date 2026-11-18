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
5a. strażnik układu (R59): ten sam numer płytki ma dwa układy gniazd (R59 i poprzedni ``*_r54``), więc skan
   jest sprawdzany z wybranym układem dwa razy — rozstaw stożków (krok 4: inny rozstaw = ``NiezgodnyUklad``)
   i po wyrównaniu mapa wysokości skanu z modelem STL w miejscach jednoznacznych (dno gniazda modelu, nad
   którym skan ma pełny wierzch; pełny wierzch modelu, w którym skan ma dziurę); niezgodność =
   ``NiezgodnyUklad`` z komunikatem „płytka nie pasuje do wybranego układu”, bez cięcia na gniazda,
5b. układ nieznany z góry (``rozpoznaj_uklad``): kroki 1–3 raz, kroki 4–5a dla każdego układu o pasującym rozstawie
   stożków; kwadrat / koło tej samej rodziny rozstrzyga numer płytki (podany albo z dołków) albo kształt brzegu,
6. numer z dołków kodu (ø2 × 1: w promieniu 0,8 mm od środka dołka 5. percentyl z < z_top − 0,4),
   dołek bez punktów = niewidoczny → numer nieznany, chyba że podany (``numer``),
7. cięcie: punkty, które nie leżą na modelu płytki (odległość do STL > 0,12 mm), grupowane DBSCAN
   (0,5 mm) → fragmenty; fragment → gniazdo, nad którym leży jego środek (margines 1 mm); gniazdo
   bez fragmentu = puste, z dwoma = podwójne, fragment poza gniazdami = poza gniazdem.
"""
from __future__ import annotations

import functools
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
# strażnik układu (R59): progi dobrane na 240 skanach syntetycznych (narzedzia/straznik_R59.py, raporty/R59_2026-11-14.md),
# do sprawdzenia na prawdziwym skanie (P3b)
PX_STRAZNIKA = 0.5  # mm na piksel map wysokości skanu i modelu
MARGINES_WIERZCHU = 1.5  # mm: strefa „pełny materiał” modelu jest odsunięta o tyle od każdej krawędzi (gniazda, stożki, dołki, relief, brzeg)
MARGINES_DNA = 1.0  # mm: strefa „dno gniazda” modelu jest odsunięta o tyle od ścianki gniazda i od otworu ø3 w dnie
PROG_WIERZCHU_SKANU = 0.15  # mm: piksel skanu leży na wierzchu płytki, gdy jego najwyższy punkt jest tak blisko z = thickness
GLEBOKOSC_DZIURY_MIN = 1.5  # mm: piksel skanu jest dziurą, gdy jego najwyższy punkt leży tyle pod wierzchem (dołek kodu ma 1 mm)
PROG_GNIAZDO_NAD_PELNYM_MM2 = 150.0  # mm²: tyle dna gniazd modelu nad płaskim wierzchem skanu = płytka nie pasuje (zmierzone: zgodne ≤ 48, niezgodne ≥ 410)
PROG_DZIURA_W_PELNYM_MM2 = 50.0  # mm²: tyle pełnego wierzchu modelu nad dziurą w skanie = płytka nie pasuje (zmierzone: zgodne 0, niezgodne ≥ 54 na pełnej płytce, ≥ 180 na pustej i częściowej)
# automatyczne rozpoznanie układu (rozpoznaj_uklad): kwadrat czy koło tej samej rodziny układów
R_KSZTALTU_MIN = 47.5  # mm: dalej od środka nie ma gniazd ani stożków (wszystkie obrysy leżą w kole r 47), jest tylko brzeg płytki
R_KSZTALTU_MAX = 75.0  # mm: rogi kwadratu sięgają r 67,9
PAS_KSZTALTU_Z = 3.0  # mm: oceniana jest górna część bryły płytki (wierzch i górny pas ścianki)
PROG_KSZTALTU_ODL = 0.3  # mm: punkt skanu dalej od modelu niż to = nie należy do płytki o tym kształcie
PROG_KSZTALTU_MM2 = 40.0  # mm²: taka różnica powierzchni niewyjaśnionej między kształtami rozstrzyga (pomiar: narzedzia/auto_uklad.py)


class BladWyrownania(RuntimeError):
    """Nie udało się wyrównać skanu do układu płytki (brak płaszczyzny / znaczników)."""


class NiezgodnyUklad(BladWyrownania):
    """Skan nie pasuje do wybranego układu płytki (strażnik układu, R59); komunikat zaczyna się od „płytka nie pasuje do wybranego układu”.

    ``powod``: ``stozki`` — rozstaw stożków znaczników inny niż w układzie (wyrównania nie ma, ``macierz`` = None);
    ``gniazda`` — stożki pasują, ale gniazda leżą inaczej niż w modelu (``macierz`` = wyrównanie po stożkach i ICP).
    ``stozki``: środki dopasowanych stożków w układzie wypoziomowanego skanu (``stozki_pasuja`` sprawdza nimi inne układy);
    ``jakosc``: miary zebrane do chwili błędu, zawsze z ``uklad_zgodny`` = False.
    """

    def __init__(self, komunikat: str, powod: str, stozki: list | None = None, jakosc: dict | None = None, macierz: np.ndarray | None = None):
        super().__init__(komunikat)
        self.powod = powod
        self.stozki = list(stozki or [])
        self.jakosc = {**(jakosc or {}), "uklad_zgodny": False, "uklad_powod": powod}
        self.macierz = macierz


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


def _przypisania(srodki: list[dict], uk: U.UkladPlytki) -> list[tuple]:
    """Wszystkie uporządkowane trójki wykrytych stożków dopasowane (Kabsch 2D) do znaczników A, B, C; od najmniejszej reszty."""
    cel = np.array([[z.x, z.y] for z in uk.markers])
    pts = np.array([[s["x"], s["y"]] for s in srodki])
    wyniki = []
    for trojka in itertools.permutations(range(len(srodki)), 3):
        R, t, rms = kabsch_2d(pts[list(trojka)], cel)
        wyniki.append((rms, trojka, R, t))
    wyniki.sort(key=lambda w: w[0])
    return wyniki


def _boki(pts: np.ndarray) -> list[float]:
    """Długości boków trójkąta (rosnąco) — rozstaw trzech stożków."""
    return sorted(float(np.linalg.norm(pts[i] - pts[j])) for i, j in ((0, 1), (1, 2), (0, 2)))


def stozki_pasuja(srodki: list[dict], uk: U.UkladPlytki) -> bool:
    """Czy wśród wykrytych stożków jest trójka o rozstawie znaczników układu ``uk`` (reszta ≤ RESZTA_ZNACZNIKOW_MAX)."""
    return len(srodki) >= 3 and _przypisania(srodki, uk)[0][0] <= RESZTA_ZNACZNIKOW_MAX


def przypisz_znaczniki(srodki: list[dict], uk: U.UkladPlytki) -> tuple[np.ndarray, dict]:
    """Wybiera trójkę wykrytych stożków i ich przypisanie do A, B, C o najmniejszej reszcie Kabscha.

    Trzy dobrze dopasowane stożki o innym rozstawie niż znaczniki układu to inna płytka albo inny układ gniazd
    (R59: układ nowy i poprzedni ``*_r54`` mają te same numery płytek, ale inne pozycje stożków) → ``NiezgodnyUklad``.
    """
    if len(srodki) < 3:
        raise BladWyrownania(f"znaleziono {len(srodki)} stożki znaczników, potrzeba 3")
    pts = np.array([[s["x"], s["y"]] for s in srodki])
    wyniki = _przypisania(srodki, uk)
    rms, trojka, R, t = wyniki[0]
    druga = wyniki[1][0] if len(wyniki) > 1 else math.inf
    if rms > RESZTA_ZNACZNIKOW_MAX:
        w_skanie = _boki(pts[list(trojka)])
        w_ukladzie = _boki(np.array([[z.x, z.y] for z in uk.markers]))
        raise NiezgodnyUklad(
            f"płytka nie pasuje do wybranego układu „{uk.nazwa}”: stożki znaczników nie pasują do układu (rozstaw w skanie "
            f"{' / '.join(f'{b:.1f}' for b in w_skanie)} mm, w układzie {' / '.join(f'{b:.1f}' for b in w_ukladzie)} mm; "
            f"reszta {rms:.3f} mm > {RESZTA_ZNACZNIKOW_MAX}) — sprawdź wybór układu płytki (R59 albo poprzedni …_r54)",
            "stozki", srodki,
            {"znaczniki_reszta_mm": rms, "uklad_rozstaw_skanu_mm": [round(b, 3) for b in w_skanie], "uklad_rozstaw_modelu_mm": [round(b, 3) for b in w_ukladzie]},
        )
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
# 5a. strażnik układu (R59): skan ↔ model w miejscach jednoznacznych
# ----------------------------------------------------------------------------
def _kolo(promien_px: int) -> np.ndarray:
    k = np.arange(-promien_px, promien_px + 1)
    return (k[:, None] ** 2 + k[None, :] ** 2) <= promien_px**2


@functools.lru_cache(maxsize=16)
def _strefy_modelu(plik: str, mtime_ns: int, z_top: float, dna: tuple, px: float) -> tuple[tuple[float, float], np.ndarray, np.ndarray]:
    """Strefy pewne modelu STL widzianego z góry: (początek siatki xy, maska „pełny wierzch”, maska „dno gniazda”).

    Mapa wysokości modelu = promienie w dół w środkach pikseli (Open3D). „Pełny wierzch”: z = ``z_top``, odsunięty
    o MARGINES_WIERZCHU od wszystkiego, co wierzchem nie jest (gniazda, stożki, dołki, relief numeru, brzeg, ścięcie).
    „Dno gniazda”: z = dno któregoś gniazda (``dna``), odsunięte o MARGINES_DNA od ścianki i od otworu w dnie.
    """
    m = o3d.io.read_triangle_mesh(plik)
    V = np.asarray(m.vertices)
    x0, y0 = float(V[:, 0].min()), float(V[:, 1].min())
    nx, ny = int(math.ceil((V[:, 0].max() - x0) / px)), int(math.ceil((V[:, 1].max() - y0) / px))
    X, Y = np.meshgrid(x0 + (np.arange(nx) + 0.5) * px, y0 + (np.arange(ny) + 0.5) * px)
    z_start = float(V[:, 2].max()) + 10.0
    promienie = np.zeros((X.size, 6), dtype=np.float32)
    promienie[:, 0], promienie[:, 1], promienie[:, 2], promienie[:, 5] = X.ravel(), Y.ravel(), z_start, -1.0
    scena = o3d.t.geometry.RaycastingScene()
    scena.add_triangles(o3d.t.geometry.TriangleMesh.from_legacy(m))
    Zm = z_start - scena.cast_rays(o3d.core.Tensor(promienie))["t_hit"].numpy().reshape(ny, nx)  # brak trafienia → −inf
    wierzch = np.abs(Zm - z_top) < 0.02
    dno = np.zeros_like(wierzch)
    for zd in dna:
        dno |= np.abs(Zm - zd) < 0.02
    wierzch = ndimage.binary_erosion(wierzch, structure=_kolo(int(round(MARGINES_WIERZCHU / px))))
    dno = ndimage.binary_erosion(dno, structure=_kolo(int(round(MARGINES_DNA / px))))
    return (x0, y0), wierzch, dno


def zgodnosc_ukladu(P: np.ndarray, uk: U.UkladPlytki, plik_modelu: Path, px: float = PX_STRAZNIKA) -> dict:
    """Strażnik układu: czy skan (``P`` — punkty równomierne po powierzchni, już w układzie płytki) ma gniazda tam, gdzie model.

    Porównuje mapę wysokości skanu (najwyższy punkt w pikselu ``px``) z modelem STL tylko w strefach pewnych modelu:
    * ``uklad_gniazdo_nad_pelnym_mm2`` — pole dna gniazd modelu, nad którym skan ma płaski wierzch płytki (z = thickness
      ± PROG_WIERZCHU_SKANU): w zeskanowanej płytce jest tam pełny materiał. Prace nie zasłaniają tej cechy (leżą
      w gniazdach płytki zeskanowanej, nie na jej wierzchu), więc działa także na płytce pełnej prac;
    * ``uklad_dziura_w_pelnym_mm2`` — pole pełnego wierzchu modelu, w którym skan jest głębszy niż GLEBOKOSC_DZIURY_MIN:
      w zeskanowanej płytce jest tam gniazdo. Praca w tym gnieździe zasłania dziurę, więc na pełnej płytce ta miara maleje.
    Piksel bez punktów skanu (poza polem skanowania, dziura w danych) nie jest dowodem. Układ jest zgodny, gdy pierwsza
    miara jest mniejsza niż PROG_GNIAZDO_NAD_PELNYM_MM2, a druga niż PROG_DZIURA_W_PELNYM_MM2. Pierwsza miara nie jest
    zerem na płytce zgodnej: dno wnętrza korony leżącej brzegiem do góry bywa na wysokości wierzchu płytki (zmierzone
    1–2 mm² na pracę, najwyżej 48 mm² na pełnej płytce), stąd próg liczony w setkach mm².
    """
    plik_modelu = Path(plik_modelu)
    dna = tuple(sorted({round(g.z_dno, 6) for g in uk.sockets}))
    (x0, y0), wierzch_m, dno_m = _strefy_modelu(str(plik_modelu), plik_modelu.stat().st_mtime_ns, float(uk.thickness), dna, px)
    ny, nx = wierzch_m.shape
    i = np.floor((P[:, 0] - x0) / px).astype(np.int64)
    j = np.floor((P[:, 1] - y0) / px).astype(np.int64)
    w = (i >= 0) & (i < nx) & (j >= 0) & (j < ny)
    Z = np.full((ny, nx), -np.inf)
    np.maximum.at(Z, (j[w], i[w]), P[w, 2])
    dane = np.isfinite(Z)
    na_wierzchu = dane & (np.abs(Z - uk.thickness) <= PROG_WIERZCHU_SKANU)
    dziura = dane & (Z < uk.thickness - GLEBOKOSC_DZIURY_MIN)
    pole = px * px
    gniazdo_nad_pelnym = float((dno_m & na_wierzchu).sum() * pole)
    dziura_w_pelnym = float((wierzch_m & dziura).sum() * pole)
    return {
        "uklad_zgodny": bool(gniazdo_nad_pelnym < PROG_GNIAZDO_NAD_PELNYM_MM2 and dziura_w_pelnym < PROG_DZIURA_W_PELNYM_MM2),
        "uklad_gniazdo_nad_pelnym_mm2": round(gniazdo_nad_pelnym, 2), "uklad_dziura_w_pelnym_mm2": round(dziura_w_pelnym, 2),
        "uklad_strefa_dna_mm2": round(float((dno_m & dane).sum() * pole), 1), "uklad_strefa_wierzchu_mm2": round(float((wierzch_m & dane).sum() * pole), 1),
    }


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


@dataclass
class _Przygotowanie:
    """Część wyrównania niezależna od układu gniazd: wypoziomowany skan i dopasowane stożki znaczników (liczona raz na skan)."""

    P0: np.ndarray
    N0: np.ndarray
    Ps: np.ndarray
    Ns: np.ndarray
    T1: np.ndarray
    stozki: list
    jak: dict
    stan_rng: dict  # stan generatora po próbce i płaszczyźnie: ICP każdego układu startuje z tego samego stanu
    stan_rng_plaszczyzna: dict  # stan generatora tuż przed ``plaszczyzna_wierzchu`` (ona ustawia też ziarno generatora Open3D)
    czas_s: float
    pole_punktu: float  # mm² powierzchni skanu na jeden punkt próbki Ps
    swiezy: bool = True  # False po pierwszym ``_wyrownaj_do_ukladu``: generator Open3D został zużyty przez ICP


def _klucz_przygotowania(uk: U.UkladPlytki) -> tuple:
    """Od czego zależy ``_przygotuj``: grubość płytki i geometria stożka znacznika (dziś wspólne dla wszystkich układów)."""
    zn = uk.markers[0]
    return (float(uk.thickness), float(zn.d), float(zn.depth))


def _przygotuj(skan: trimesh.Trimesh, uk: U.UkladPlytki, seed: int = 0) -> _Przygotowanie:
    """Kroki 1–3: płaszczyzna wierzchu, wypoziomowanie, stożki znaczników (bez przypisania do układu)."""
    t0 = time.time()
    rng = np.random.default_rng(seed)
    P0 = np.asarray(skan.vertices, dtype=np.float64)
    N0 = np.asarray(skan.vertex_normals, dtype=np.float64)
    N0 = np.where(np.isfinite(N0), N0, 0.0)
    jak: dict = {"punkty": int(len(P0))}

    Ps, Ns = probka_powierzchni(skan, 1500000, rng)
    stan_plaszczyzna = rng.bit_generator.state
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
    return _Przygotowanie(P0=P0, N0=N0, Ps=Ps, Ns=Ns, T1=T1, stozki=stozki, jak=jak, stan_rng=rng.bit_generator.state,
                          stan_rng_plaszczyzna=stan_plaszczyzna, czas_s=time.time() - t0, pole_punktu=float(skan.area) / max(len(Ps), 1))


def _wyrownaj_do_ukladu(prz: _Przygotowanie, uk: U.UkladPlytki, numer: int | None, icp: bool, straznik: bool) -> tuple[WynikWyrownania, dict]:
    """Kroki 4–6 dla jednego układu na przygotowanym skanie; wynik bez cięcia + stan do ``_dotnij``."""
    t1 = time.time()
    rng = np.random.default_rng(0)
    if not prz.swiezy:
        # Kolejny układ na tym samym przygotowaniu. ICP losuje próbkę modelu generatorem Open3D (globalnym), którego ziarno
        # ustawia ``plaszczyzna_wierzchu``; poprzedni układ już go zużył. Powtórzenie płaszczyzny z tym samym stanem przywraca
        # generator Open3D do stanu, jaki ma w tym miejscu ``wyrownaj`` — wynik jest bit w bit taki sam jak przy układzie
        # wybranym ręcznie.
        rng.bit_generator.state = prz.stan_rng_plaszczyzna
        plaszczyzna_wierzchu(prz.Ps, prz.Ns, rng)
    prz.swiezy = False
    rng.bit_generator.state = prz.stan_rng
    jak: dict = dict(prz.jak)
    P0, N0, Ps, Ns = prz.P0, prz.N0, prz.Ps, prz.Ns
    try:
        T2, j = przypisz_znaczniki(prz.stozki, uk)
    except NiezgodnyUklad as e:
        e.jakosc = {**jak, **e.jakosc, "czas_s": round(prz.czas_s + time.time() - t1, 2)}
        raise
    jak.update(j)
    T = T2 @ prz.T1
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
    jak["czas_wyrownania_s"] = round(prz.czas_s + time.time() - t1, 2)

    bity = odczytaj_bity(Ps2, uk)  # próbka po powierzchni: równomierna także na płaskim wierzchu
    numer_z_dolkow = None
    if all(b is not None for b in bity):
        numer_z_dolkow = uk.numer_z_bitow(*bity)
    if numer is not None:
        zrodlo = "podany"
        if numer_z_dolkow is not None and numer_z_dolkow != numer:
            warnings.warn(f"numer płytki podany {numer}, z dołków odczytano {numer_z_dolkow} — używam podanego", stacklevel=3)
    elif numer_z_dolkow is not None:
        numer, zrodlo = numer_z_dolkow, "dolki"
        if numer not in uk.numery:
            warnings.warn(f"numer płytki z dołków {numer} nie ma modelu w {uk.katalog} (są: {uk.numery})", stacklevel=3)
    else:
        zrodlo = "nieznany"
        warnings.warn(
            f"dołki kodu poza skanem ({sum(b is None for b in bity)} z {len(bity)} niewidocznych) — podaj numer płytki (--numer)",
            stacklevel=3,
        )

    if straznik:
        jak.update(zgodnosc_ukladu(Ps2, uk, plik_modelu_plytki(uk, numer)))
        if not jak["uklad_zgodny"]:
            jak["czas_s"] = round(prz.czas_s + time.time() - t1, 2)
            raise NiezgodnyUklad(
                f"płytka nie pasuje do wybranego układu „{uk.nazwa}”: stożki znaczników pasują, ale gniazda leżą inaczej niż w modelu "
                f"(dno gniazda modelu nad pełnym wierzchem skanu: {jak['uklad_gniazdo_nad_pelnym_mm2']:.0f} mm², pełny wierzch modelu nad dziurą "
                f"w skanie: {jak['uklad_dziura_w_pelnym_mm2']:.0f} mm²; progi {PROG_GNIAZDO_NAD_PELNYM_MM2:.0f} / {PROG_DZIURA_W_PELNYM_MM2:.0f} mm²) — sprawdź wybór układu płytki",
                "gniazda", prz.stozki, jak, T,
            )
    wyr = WynikWyrownania(
        plytka=uk.nazwa, macierz=T, numer=numer, numer_zrodlo=zrodlo, bity=bity, numer_z_dolkow=numer_z_dolkow,
        fragmenty=[], gniazda_puste=[], gniazda_podwojne=[], jakosc=jak,
    )
    return wyr, {"P": P, "N": N, "Ps": Ps2, "Ns": Ns2, "t1": t1, "czas_przygotowania": prz.czas_s}


def _dotnij(wyr: WynikWyrownania, stan: dict, uk: U.UkladPlytki, ciecie: bool) -> WynikWyrownania:
    """Krok 7 (cięcie na gniazda) na wyniku ``_wyrownaj_do_ukladu``; zamyka pomiar czasu."""
    jak = wyr.jakosc
    if ciecie:
        t = time.time()
        fragmenty, j = potnij_na_fragmenty(stan["P"], stan["N"], stan["Ps"], stan["Ns"], uk, plik_modelu_plytki(uk, wyr.numer))
        jak.update(j)
        zajete = {f.gniazdo for f in fragmenty if f.gniazdo is not None and f.status in ("praca", "podwojny")}
        wyr.fragmenty = fragmenty
        wyr.gniazda_puste = [g.id for g in uk.sockets if g.id not in zajete]
        wyr.gniazda_podwojne = sorted({f.gniazdo for f in fragmenty if f.status == "podwojny"})
        jak["czas_ciecia_s"] = round(time.time() - t, 2)
    jak["czas_s"] = round(stan["czas_przygotowania"] + time.time() - stan["t1"], 2)
    return wyr


def wyrownaj(
    skan: trimesh.Trimesh, uk: U.UkladPlytki, numer: int | None = None, seed: int = 0, icp: bool = True, ciecie: bool = True,
    straznik: bool = True,
) -> WynikWyrownania:
    """Pełny przebieg plate na siatce skanu; ``numer`` podany przez użytkownika ma pierwszeństwo nad dołkami.

    Skan, który nie pasuje do układu ``uk`` (inny rozstaw stożków albo gniazda w innych miejscach), kończy się
    ``NiezgodnyUklad`` — wyniku z gniazdami nie ma. ``straznik=False`` wyłącza tylko drugie sprawdzenie (gniazda).
    """
    prz = _przygotuj(skan, uk, seed)
    wyr, stan = _wyrownaj_do_ukladu(prz, uk, numer, icp, straznik)
    return _dotnij(wyr, stan, uk, ciecie)


# ----------------------------------------------------------------------------
# automatyczne rozpoznanie układu płytki
# ----------------------------------------------------------------------------
class NierozpoznanyUklad(NiezgodnyUklad):
    """Skan nie pasuje do żadnego układu z listy (``rozpoznaj_uklad``); komunikat zaczyna się od „nie rozpoznano układu płytki”.

    ``kandydaci``: wpis dla każdego sprawdzonego układu (dlaczego odpadł).
    """

    def __init__(self, komunikat: str, powod: str, stozki: list | None = None, jakosc: dict | None = None, kandydaci: list | None = None):
        super().__init__(komunikat, powod, stozki, jakosc, None)
        self.kandydaci = list(kandydaci or [])


def ksztalt_plytki(Ps: np.ndarray, uk: U.UkladPlytki, plik_modelu: Path, pole_punktu: float) -> dict:
    """Ile powierzchni skanu przy brzegu płytki NIE leży na modelu ``uk`` — rozróżnia płytkę kwadratową i okrągłą tego samego układu gniazd.

    Kwadrat (96 × 96) i koło (ø100) mają te same gniazda i stożki; różnią się tylko poza kołem r = R_KSZTALTU_MIN (dalej nie ma
    gniazd ani stożków): koło ma tam wierzch do r = 50 i ściankę walca, kwadrat — ściankę płaską w x, y = ±48 i rogi. Liczone są
    punkty próbki skanu (``Ps`` w układzie płytki) w górnych PAS_KSZTALTU_Z mm bryły, dalsze od modelu niż PROG_KSZTALTU_ODL.
    Punkt, którego w skanie nie ma (poza polem skanera), nie jest dowodem — dlatego miara bywa zerem dla obu kształtów.
    """
    r = np.hypot(Ps[:, 0], Ps[:, 1])
    m = (r >= R_KSZTALTU_MIN) & (r <= R_KSZTALTU_MAX) & (Ps[:, 2] <= uk.thickness + PROG_WIERZCHU_SKANU) & (Ps[:, 2] >= uk.thickness - PAS_KSZTALTU_Z)
    if not m.any():
        return {"ksztalt_strefa_mm2": 0.0, "ksztalt_niewyjasnione_mm2": 0.0}
    odl = odleglosc_do_modelu(Ps[m], plik_modelu)
    return {"ksztalt_strefa_mm2": round(float(m.sum() * pole_punktu), 1),
            "ksztalt_niewyjasnione_mm2": round(float((odl > PROG_KSZTALTU_ODL).sum() * pole_punktu), 1)}


def rozpoznaj_uklad(
    skan: trimesh.Trimesh, uklady: list[U.UkladPlytki], numer: int | None = None, seed: int = 0, icp: bool = True, ciecie: bool = True,
    straznik: bool = True,
) -> tuple[WynikWyrownania, dict]:
    """Sam rozpoznaje, do którego układu z ``uklady`` należy zeskanowana płytka, i wyrównuje skan do niego.

    1. rozstaw trzech stożków znaczników wybiera rodzinę: wieczorna / poranna i układ gniazd R59 / poprzedni R54 (cztery różne
       trójkąty) — to samo sprawdzenie co pierwsza warstwa strażnika układu;
    2. każdy układ z pasującym rozstawem jest wyrównywany (ICP) i sprawdzany strażnikiem (gniazda skanu = gniazda modelu);
    3. kwadrat i koło tej samej rodziny mają te same stożki i gniazda, więc wybiera między nimi kolejno: numer podany przez
       człowieka (n1–n6 = kwadrat, n8–n9 = koło), numer odczytany z dołków kodu (na płytce okrągłej dołki leżą w polu skanowania,
       więc dają ważny numer; na kwadracie leżą poza polem ø100), kształt brzegu płytki (``ksztalt_plytki``), wykluczenie
       układu, którego dołki widać w całości, a nie dają numeru jego płytki; gdy nic nie rozstrzyga — układ, którego dołki
       są poza skanem (kwadrat), z flagą ``pewny`` = False i ostrzeżeniem. Gdy kształt brzegu wyraźnie przeczy wyborowi
       z numeru, ``pewny`` = False.

    Wynik wyrównania dla wybranego układu jest taki sam jak z ``wyrownaj(skan, uk, …)`` z tym układem podanym ręcznie.
    Zwraca też opis decyzji: ``wybrany``, ``pewny``, ``powod``, ``kandydaci`` (każdy układ: czy pasują stożki, dlaczego odpadł,
    numer z dołków, miary kształtu), ``czas_s``. Żaden układ nie pasuje → ``NierozpoznanyUklad``.
    """
    if not uklady:
        raise ValueError("rozpoznaj_uklad: pusta lista układów")
    t0 = time.time()
    przygotowania: dict[tuple, _Przygotowanie] = {}
    kandydaci: list[dict] = []
    przeszly: list[tuple] = []
    for uk in uklady:
        klucz = _klucz_przygotowania(uk)
        if klucz not in przygotowania:
            przygotowania[klucz] = _przygotuj(skan, uk, seed)
        prz = przygotowania[klucz]
        wpis: dict = {"uklad": uk.nazwa, "ksztalt": uk.shape, "numery": list(uk.numery), "stozki_pasuja": stozki_pasuja(prz.stozki, uk)}
        kandydaci.append(wpis)
        if not wpis["stozki_pasuja"]:
            wpis["odrzucony"] = "stozki"
            continue
        n = numer if numer is not None and numer in uk.numery else None
        try:
            with warnings.catch_warnings(record=True) as ostrz:
                warnings.simplefilter("always")
                wyr, stan = _wyrownaj_do_ukladu(prz, uk, n, icp, straznik)
        except NiezgodnyUklad as e:
            wpis["odrzucony"] = e.powod
            wpis.update({k: v for k, v in e.jakosc.items() if k.startswith("uklad_") and k != "uklad_powod"})
            continue
        except BladWyrownania as e:
            wpis["odrzucony"] = f"blad: {e}"
            continue
        wpis.update({k: v for k, v in wyr.jakosc.items() if k.startswith("uklad_")})
        wpis.update(ksztalt_plytki(stan["Ps"], uk, plik_modelu_plytki(uk, wyr.numer), prz.pole_punktu))
        wpis["numer_z_dolkow"] = wyr.numer_z_dolkow
        wpis["numer_z_dolkow_wazny"] = wyr.numer_z_dolkow is not None and wyr.numer_z_dolkow in uk.numery
        wpis["dolki_widoczne"] = sum(b is not None for b in wyr.bity)
        wpis["numer_podany_pasuje"] = None if numer is None else numer in uk.numery
        przeszly.append((uk, wyr, stan, wpis, [str(o.message) for o in ostrz]))

    prz0 = next(iter(przygotowania.values()))
    if not przeszly:
        jak = {**prz0.jak, "czas_s": round(time.time() - t0, 2)}
        if len(prz0.stozki) < 3:
            raise BladWyrownania(f"znaleziono {len(prz0.stozki)} stożki znaczników, potrzeba 3")
        if not any(k["stozki_pasuja"] for k in kandydaci):
            pts = np.array([[s["x"], s["y"]] for s in prz0.stozki])
            boki = _boki(pts[list(_przypisania(prz0.stozki, uklady[0])[0][1])])
            jak["uklad_rozstaw_skanu_mm"] = [round(b, 3) for b in boki]
            raise NierozpoznanyUklad(
                f"nie rozpoznano układu płytki: rozstaw stożków znaczników w skanie ({' / '.join(f'{b:.1f}' for b in boki)} mm) "
                f"nie pasuje do żadnego układu ({', '.join(u.nazwa for u in uklady)})", "stozki", prz0.stozki, jak, kandydaci)
        raise NierozpoznanyUklad(
            "nie rozpoznano układu płytki: rozstaw stożków pasuje do " + ", ".join(k["uklad"] for k in kandydaci if k["stozki_pasuja"])
            + ", ale gniazda w skanie leżą inaczej niż w tych układach", "gniazda", prz0.stozki, jak, kandydaci)

    pewny = True
    if len(przeszly) == 1:
        wybrany, powod = przeszly[0], "jedyny_pasujacy"
    else:
        wg_ksztaltu = sorted(przeszly, key=lambda c: c[3]["ksztalt_niewyjasnione_mm2"])
        ksztalt_rozstrzyga = wg_ksztaltu[1][3]["ksztalt_niewyjasnione_mm2"] - wg_ksztaltu[0][3]["ksztalt_niewyjasnione_mm2"] >= PROG_KSZTALTU_MM2
        z_podanym = [c for c in przeszly if c[3]["numer_podany_pasuje"]]
        z_dolkow = [c for c in przeszly if c[3]["numer_z_dolkow_wazny"]]
        if len(z_podanym) == 1:
            wybrany, powod = z_podanym[0], "numer_podany"
            pewny = not (ksztalt_rozstrzyga and wg_ksztaltu[0] is not wybrany)
        elif len(z_dolkow) == 1:
            wybrany, powod = z_dolkow[0], "numer_z_dolkow"
            pewny = not (ksztalt_rozstrzyga and wg_ksztaltu[0] is not wybrany)
        elif ksztalt_rozstrzyga:
            wybrany, powod = wg_ksztaltu[0], "ksztalt"
        else:
            # układ, którego wszystkie dołki kodu widać, a nie dają numeru jego płytki, odpada (kwadrat widziany jako koło:
            # w miejscach dołków płytki okrągłej jest płaski wierzch → „numer 0”)
            mozliwe = [c for c in przeszly if not (0 < len(c[1].bity) == c[3]["dolki_widoczne"] and not c[3]["numer_z_dolkow_wazny"])]
            if len(mozliwe) == 1:
                wybrany, powod = mozliwe[0], "dolki_wykluczaja"
            else:
                bez_dolkow = [c for c in przeszly if c[3]["dolki_widoczne"] == 0]
                wybrany, powod, pewny = (bez_dolkow or przeszly)[0], "domyslny", False
    uk, wyr, stan, wpis, ostrzezenia = wybrany
    for o in ostrzezenia:
        warnings.warn(o, stacklevel=2)
    if numer is not None and numer not in uk.numery:
        warnings.warn(f"podany numer płytki {numer} nie należy do rozpoznanego układu „{uk.nazwa}” (numery {uk.numery}) — pominięty", stacklevel=2)
    if not pewny:
        warnings.warn(
            f"układ płytki rozpoznany niepewnie: „{uk.nazwa}” (pasują też: {', '.join(c[0].nazwa for c in przeszly if c[0] is not uk)}) — "
            "podaj numer płytki albo wybierz układ ręcznie", stacklevel=2)
    wyr = _dotnij(wyr, stan, uk, ciecie)
    wyr.jakosc["czas_s"] = round(time.time() - t0, 2)
    info = {"wybrany": uk.nazwa, "pewny": pewny, "powod": powod, "kandydaci": kandydaci, "czas_s": round(time.time() - t0, 2),
            "czas_rozpoznania_s": round(time.time() - t0 - wyr.jakosc.get("czas_ciecia_s", 0.0), 2)}
    return wyr, info


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
