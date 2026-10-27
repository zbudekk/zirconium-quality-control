"""Wyrownanie skanu plytki do ukladu plytki: plaszczyzna wierzchu, znaczniki A, B, C, Kabsch, ICP.

Uklad plytki jak w qc.uklad: srodek gornej powierzchni, X w prawo, Y do tylu, Z w gore; wierzch Z = 0.
Siatka referencyjna = model plytki stanowiska (qc.syntetyka.plytka.siatka_plytki z ukladu ramki).
"""

from __future__ import annotations

import dataclasses
import hashlib
import itertools
import math
import threading
from dataclasses import dataclass

import numpy as np
import open3d as o3d
import trimesh

from qc.syntetyka.plytka import siatka_plytki
from qc.syntetyka.skan import normalne_wierzcholkow
from qc.uklad import Uklad

# plaszczyzna wierzchu
VOXEL_PLASZCZYZNY_MM = 0.5  # probka rownomierna po powierzchni (geste prace nie dominuja)
PROG_PLASZCZYZNY_MM = 0.15
ITERACJE_PLASZCZYZNY = 3000
CO_KTORY_DO_KANDYDATOW = 2  # wykrywanie na co drugim wierzcholku; pomiar i ICP na wszystkich
CO_KTORY_DO_VOXELA = 2  # wierzcholki co drugi przed voxelem (skaner ~0,1-0,2 mm << voxel)
ZIARNA_PLASZCZYZNY = (1, 2, 3)  # staly seed RANSAC, kolejne przy za malej plaszczyznie
MIN_POLE_PLASZCZYZNY = 0.3  # x rozmiar^2: pole inlierow (liczba x voxel^2) wierzchu albo dna plytki
ITERACJE_DOPRECYZOWANIA = 3
PAS_GNIAZD_MM = (0.3, 4.5)  # zaglebienia gniazd pod wierzchem: odroznia wierzch od dna plytki
UDZIAL_DRUGIEJ_PLASZCZYZNY = 0.2

# znaczniki (wklesle stozki)
TOL_GLEBOKOSCI_ZNACZNIKA_MM = 0.6
KOMORKA_MM = 1.0
MAX_ROZMIAR_KANDYDATA_MM = 2.0
PIERSCIEN_MM = (0.4, 1.0)  # pierscien plaszczyzny poza obrysem stozka: r w (R + 0,4; R + 1,0)
MAX_ODCHYLKA_PIERSCIENIA_MM = 0.25
GLEBIEJ_NIZ_ZNACZNIK_MM = 2.0  # glebiej = kieszen magnesu od spodu (ignorowana)
TOL_BOKU_MM = 0.5
PROMIEN_POMIARU_ZNACZNIKA = 0.8  # x R: punkty stozka do pomiaru wierzcholka
ITERACJE_STOZKA = 8

# ICP
OTOCZENIE_ZNACZNIKA_MM = 6.0
PAS_KRAWEDZI_MM = (45.5, 47.4)  # |x| albo |y| w pasie: plaski wierzch poza gniazdami
MARGINES_DOLKOW_MM = 0.5
MAX_PUNKTOW_ICP = 40_000
ODLEGLOSC_ICP_MM = (0.5, 0.2)
ITERACJE_ICP = 50
MIN_ZGODNOSC_ICP = 0.5

# kontrola orientacji: wyciecie D przelotowe
ZAPAS_WYCIECIA_MM = 0.5
MAX_PUNKTOW_W_WYCIECIU = 20

KROK_REFERENCJI_MM = 0.2


class BladPlytki(Exception):
    """Nie da sie wyrownac skanu plytki (brak znacznikow, zly uklad, za duzy blad)."""


@dataclass
class Wyrownanie:
    T_skan_do_plytki: np.ndarray  # 4x4
    blad_mm: float  # RMS par ICP (inliery)
    znaczniki_xyz: np.ndarray  # (3, 3) zmierzone wierzcholki stozkow A, B, C w ukladzie skanu


# --- siatka referencyjna (cache, bezpieczny dla watkow) ---------------------------

_BLOKADA = threading.Lock()
_BLOKADA_RANSAC = threading.Lock()  # open3d.utility.random.seed jest globalny
_REFERENCJE: dict = {}


def klucz_ukladu(uklad: Uklad) -> str:
    """Skrot tresci ukladu (bez sciezki pliku): ten sam uklad = ten sam klucz, takze bez pliku."""
    return hashlib.sha1(repr(dataclasses.replace(uklad, plik=None)).encode("utf-8")).hexdigest()


def siatka_referencyjna(uklad: Uklad, numer: int | None) -> trimesh.Trimesh:
    """Model plytki numer (None = bazowy, 3 dolki) z krokiem jak skaner; liczony raz na uklad i numer."""
    klucz = (klucz_ukladu(uklad), numer)
    with _BLOKADA:
        siatka = _REFERENCJE.get(klucz)
    if siatka is None:
        siatka = siatka_plytki(uklad, numer, krok_mm=KROK_REFERENCJI_MM)
        with _BLOKADA:
            siatka = _REFERENCJE.setdefault(klucz, siatka)
    return siatka


def _cel_icp(uklad: Uklad) -> o3d.geometry.PointCloud:
    """Punkty referencji z normalnymi w obszarach uzywanych przez ICP (cache)."""
    klucz = (klucz_ukladu(uklad), "icp")
    with _BLOKADA:
        chmura = _REFERENCJE.get(klucz)
    if chmura is not None:
        return chmura
    ref = siatka_referencyjna(uklad, None)
    v = np.asarray(ref.vertices, dtype=np.float64)
    n = normalne_wierzcholkow(v, np.asarray(ref.faces, dtype=np.int64))
    maska = _maska_icp(uklad, v, zapas=0.5)
    chmura = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(v[maska]))
    chmura.normals = o3d.utility.Vector3dVector(n[maska])
    with _BLOKADA:
        return _REFERENCJE.setdefault(klucz, chmura)


def _maska_icp(uklad: Uklad, p: np.ndarray, zapas: float = 0.0) -> np.ndarray:
    """Otoczenia znacznikow i pas plaskiego wierzchu przy krawedziach, bez dolkow kodu i reliefu."""
    # wstepnie tylko pas przy krawedziach plytki (znaczniki i pas leza tam), potem dokladnie
    od_krawedzi = min(min(max(abs(m[0]), abs(m[1])) for m in uklad.znaczniki.values()) - OTOCZENIE_ZNACZNIKA_MM,
                      PAS_KRAWEDZI_MM[0]) - zapas - 1.0
    wybrane = np.flatnonzero((np.maximum(np.abs(p[:, 0]), np.abs(p[:, 1])) > od_krawedzi) &
                             (p[:, 2] > -uklad.grubosc / 2) & (p[:, 2] < 1.0 + zapas))
    maska = np.zeros(len(p), dtype=bool)
    maska[wybrane] = _maska_icp_dokladna(uklad, p[wybrane], zapas)
    return maska


def _maska_icp_dokladna(uklad: Uklad, p: np.ndarray, zapas: float) -> np.ndarray:
    x, y, z = p[:, 0], p[:, 1], p[:, 2]
    przy_znaczniku = np.zeros(len(p), dtype=bool)
    for mx, my, _, glebokosc in uklad.znaczniki.values():
        przy_znaczniku |= (np.hypot(x - mx, y - my) < OTOCZENIE_ZNACZNIKA_MM + zapas) & \
                          (z > -glebokosc - 0.5 - zapas) & (z < 0.3 + zapas)
    m = np.maximum(np.abs(x), np.abs(y))
    pas = (m >= PAS_KRAWEDZI_MM[0] - zapas) & (m <= PAS_KRAWEDZI_MM[1] + zapas) & (np.abs(z) < 0.3 + zapas)
    maska = przy_znaczniku | pas
    for bit, (dx, dy) in uklad.dolki_kodu.items():
        d, _ = uklad.wymiary_dolkow.get(bit, (2.0, 1.0))
        maska &= np.hypot(x - dx, y - dy) > d / 2 + MARGINES_DOLKOW_MM
    if uklad.relief_numeru is not None:
        rx, ry, _, _ = uklad.relief_numeru
        maska &= ~((np.abs(x - rx) < 2.0 + 1.0) & (np.abs(y - ry) < 2.5 + 1.0))
    return maska


# --- geometria pomocnicza ---------------------------------------------------------


# Duze tablice bez BLAS: wielowatkowy OpenBLAS (numpy @) rownolegle z OpenMP open3d w innym watku Pythona
# konczy sie access violation (Windows, plytka 24 + 2, 3 watki); einsum bez optimize (petla C numpy) jest
# bezpieczny.


def przenies(p: np.ndarray, T: np.ndarray) -> np.ndarray:
    """Punkty (N, 3) przez T 4x4 (bez BLAS)."""
    p = np.asarray(p, dtype=np.float64)
    T = np.asarray(T, dtype=np.float64)
    return np.einsum("ij,kj->ik", p, T[:3, :3]) + T[:3, 3]


def _iloczyn(p: np.ndarray, n: np.ndarray) -> np.ndarray:
    """p (N, 3) . n (3,) bez BLAS."""
    return np.einsum("ij,j->i", p, n)


_przenies = przenies


def _obrot_do_z(n: np.ndarray) -> np.ndarray:
    """Macierz obrotu 3x3 przenoszaca wektor jednostkowy n na +Z."""
    n = n / np.linalg.norm(n)
    z = np.array([0.0, 0.0, 1.0])
    v = np.cross(n, z)
    s, c = np.linalg.norm(v), float(n @ z)
    if s < 1e-12:
        return np.eye(3) if c > 0 else np.diag([1.0, -1.0, -1.0])
    K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + K + K @ K * ((1 - c) / s**2)


def _plaszczyzna_lsq(p: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(punkt, normalna) plaszczyzny najmniejszych kwadratow."""
    c = p.mean(axis=0)
    q = p - c
    C = np.einsum("ij,ik->jk", q, q)  # bez BLAS (einsum bez optimize)
    _, wektory = np.linalg.eigh(C)
    return c, wektory[:, 0]


def kabsch(zrodlo: np.ndarray, cel: np.ndarray) -> np.ndarray:
    """Sztywna T 4x4 (bez skali) minimalizujaca |T zrodlo - cel|^2."""
    cz, cc = zrodlo.mean(axis=0), cel.mean(axis=0)
    H = (zrodlo - cz).T @ (cel - cc)
    U, _, Vt = np.linalg.svd(H)
    D = np.diag([1.0, 1.0, np.sign(np.linalg.det(Vt.T @ U.T))])
    R = Vt.T @ D @ U.T
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = cc - R @ cz
    return T


# --- kroki ------------------------------------------------------------------------


def _plaszczyzna_ransac(probka: np.ndarray, min_inlierow: int) -> tuple[np.ndarray, float]:
    """(n, d) najwiekszej plaszczyzny n.p + d = 0: RANSAC open3d ze stalym seedem, ponowienie innym seedem."""
    chmura = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(probka))
    najlepszy, inliery = None, -1
    for ziarno in ZIARNA_PLASZCZYZNY:
        with _BLOKADA_RANSAC:
            o3d.utility.random.seed(ziarno)
            model, idx = chmura.segment_plane(PROG_PLASZCZYZNY_MM, 3, ITERACJE_PLASZCZYZNY)
        if len(idx) > inliery:
            najlepszy, inliery = model, len(idx)
        if inliery >= min_inlierow:
            break
    if inliery < min_inlierow:
        raise BladPlytki(f"brak znacznikow: brak plaszczyzny plytki w skanie (najwieksza {inliery} z "
                         f"{len(probka)} punktow)")
    n = np.asarray(najlepszy[:3], dtype=np.float64)
    dl = np.linalg.norm(n)
    return n / dl, float(najlepszy[3]) / dl


def _uklad_wstepny(v: np.ndarray, uklad: Uklad) -> np.ndarray:
    """T 4x4 skan -> uklad wstepny: wierzch plytki w z = 0, prace po stronie +Z."""
    chmura = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(v[::CO_KTORY_DO_VOXELA]))
    probka = np.asarray(chmura.voxel_down_sample(VOXEL_PLASZCZYZNY_MM).points, dtype=np.float64)
    if len(probka) < 100:
        raise BladPlytki("brak znacznikow: za malo punktow skanu")
    n, d0 = _plaszczyzna_ransac(probka, int(MIN_POLE_PLASZCZYZNY * uklad.rozmiar**2 / VOXEL_PLASZCZYZNY_MM**2))
    d = _iloczyn(probka, n) + d0
    g = float(uklad.grubosc)

    def w_pasie(h):
        return np.count_nonzero((h >= PAS_GNIAZD_MM[0]) & (h <= PAS_GNIAZD_MM[1]))

    na = np.count_nonzero(np.abs(d) < PROG_PLASZCZYZNY_MM)
    plus = np.count_nonzero(np.abs(d - g) < PROG_PLASZCZYZNY_MM)
    minus = np.count_nonzero(np.abs(d + g) < PROG_PLASZCZYZNY_MM)
    if max(plus, minus) >= UDZIAL_DRUGIEJ_PLASZCZYZNY * na:
        druga = g if plus >= minus else -g
        # wierzch = plaszczyzna, pod ktora (w strone drugiej) jest wiecej zaglebien gniazd
        znak_do_drugiej = math.copysign(1.0, druga)
        pod_ta = w_pasie(znak_do_drugiej * d)  # glebokosc pod znaleziona plaszczyzna (w strone drugiej)
        pod_druga = w_pasie(-znak_do_drugiej * (d - druga))  # glebokosc pod druga (w strone znalezionej)
        if pod_ta >= pod_druga:
            gora, przes = -znak_do_drugiej, 0.0
        else:
            gora, przes = znak_do_drugiej, druga
    else:
        # bez dna w skanie: skaner patrzy z gory (+Z skanera)
        gora, przes = (1.0 if n[2] >= 0 else -1.0), 0.0
    # dopasowanie najmniejszych kwadratow do punktow wierzchu, kilka razy (wynik nie zalezy od probki RANSAC)
    nn, p0 = gora * n, None
    h = gora * (d - przes)
    for _ in range(ITERACJE_DOPRECYZOWANIA):
        p0, nowa = _plaszczyzna_lsq(probka[np.abs(h) < PROG_PLASZCZYZNY_MM])
        nn = nowa if nowa @ nn >= 0 else -nowa
        h = _iloczyn(probka - p0, nn)
    T = np.eye(4)
    T[:3, :3] = _obrot_do_z(nn)
    T[:3, 3] = -T[:3, :3] @ p0
    return T


def _zmierz_znaczniki(v: np.ndarray, T: np.ndarray, uklad: Uklad) -> np.ndarray:
    """(3, 3) zmierzone wierzcholki (dna) stozkow A, B, C w ukladzie skanu.

    Dopasowanie stozka o znanym nachyleniu z = z0 + s r do punktow skanu wokol osi (Gauss-Newton) w ukladzie
    plytki, wynik przeniesiony odwrotnoscia T.
    """
    p = _przenies(v, T)
    od_krawedzi = min(max(abs(m[0]), abs(m[1])) - m[2] for m in uklad.znaczniki.values())
    p = p[np.maximum(np.abs(p[:, 0]), np.abs(p[:, 1])) > od_krawedzi]
    wynik = []
    for nazwa in ("A", "B", "C"):
        mx, my, d, glebokosc = uklad.znaczniki[nazwa]
        R = d / 2
        s = glebokosc / R
        r = np.hypot(p[:, 0] - mx, p[:, 1] - my)
        q = p[(r < PROMIEN_POMIARU_ZNACZNIKA * R) & (p[:, 2] > -glebokosc - 0.5) & (p[:, 2] < 0.0)]
        x = np.array([mx, my, -glebokosc], dtype=np.float64)
        if len(q) >= 6:
            for _ in range(ITERACJE_STOZKA):
                dx, dy = q[:, 0] - x[0], q[:, 1] - x[1]
                rr = np.maximum(np.hypot(dx, dy), 1e-6)
                reszta = q[:, 2] - (x[2] + s * rr)
                J = np.column_stack([-s * dx / rr, -s * dy / rr, np.ones(len(q))])
                krok, *_ = np.linalg.lstsq(J, reszta, rcond=None)
                x = x + krok
                if np.abs(krok).max() < 1e-7:
                    break
        wynik.append(x)
    return _przenies(np.array(wynik), np.linalg.inv(T))


def _kandydaci_znacznikow(p: np.ndarray, uklad: Uklad) -> list[np.ndarray]:
    """Wierzcholki wkleslych stozkow znacznikow w ukladzie wstepnym (lista punktow (3,))."""
    glebokosc = float(np.median([m[3] for m in uklad.znaczniki.values()]))
    promien = float(np.median([m[2] for m in uklad.znaczniki.values()])) / 2
    z = p[:, 2]
    dno = np.flatnonzero(np.abs(z + glebokosc) <= TOL_GLEBOKOSCI_ZNACZNIKA_MM)
    if len(dno) == 0:
        return []
    komorki = np.floor(p[dno, :2] / KOMORKA_MM).astype(np.int64)
    zbior = {tuple(k) for k in np.unique(komorki, axis=0)}
    grupy, odwiedzone = [], set()
    for start in zbior:
        if start in odwiedzone:
            continue
        stos, grupa = [start], []
        odwiedzone.add(start)
        while stos:
            k = stos.pop()
            grupa.append(k)
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    s = (k[0] + dx, k[1] + dy)
                    if s in zbior and s not in odwiedzone:
                        odwiedzone.add(s)
                        stos.append(s)
        grupy.append(np.array(grupa))
    wynik = []
    for grupa in grupy:
        rozmiar = (grupa.max(axis=0) - grupa.min(axis=0) + 1) * KOMORKA_MM
        if rozmiar.max() > MAX_ROZMIAR_KANDYDATA_MM + KOMORKA_MM:
            continue  # scianki gniazd i bokow plytki
        lo, hi = grupa.min(axis=0) * KOMORKA_MM, (grupa.max(axis=0) + 1) * KOMORKA_MM
        w = p[dno]
        w = w[np.all((w[:, :2] >= lo) & (w[:, :2] <= hi), axis=1)]
        szczyt = w[np.argmin(w[:, 2])]
        r = np.hypot(p[:, 0] - szczyt[0], p[:, 1] - szczyt[1])
        okolica = (r < promien + PIERSCIEN_MM[1]) & (p[:, 2] > -glebokosc - GLEBIEJ_NIZ_ZNACZNIK_MM)
        if not okolica.any():
            continue
        if p[okolica, 2].min() < -glebokosc - TOL_GLEBOKOSCI_ZNACZNIKA_MM:
            continue  # glebsze dno = gniazdo
        pierscien = okolica & (r > promien + PIERSCIEN_MM[0])
        if np.count_nonzero(pierscien) < 8:
            continue
        if np.abs(p[pierscien, 2]).max() > MAX_ODCHYLKA_PIERSCIENIA_MM:
            continue
        wynik.append(szczyt)
    return wynik


def _trojka(kandydaci: list[np.ndarray], uklad: Uklad) -> np.ndarray:
    """(3, 3) kandydaci w kolejnosci A, B, C pasujacy do trojkata ukladu (boki i orientacja)."""
    nazwy = ("A", "B", "C")
    ref = np.array([uklad.znaczniki[n][:2] for n in nazwy], dtype=np.float64)

    def boki(t):
        return np.array([np.linalg.norm(t[0] - t[1]), np.linalg.norm(t[1] - t[2]), np.linalg.norm(t[0] - t[2])])

    def orientacja(t):
        a, b = t[1] - t[0], t[2] - t[1]
        return math.copysign(1.0, a[0] * b[1] - a[1] * b[0])

    boki_ref, or_ref = boki(ref), orientacja(ref)
    najlepsza, blad = None, math.inf
    for kombinacja in itertools.combinations(range(len(kandydaci)), 3):
        for perm in itertools.permutations(kombinacja):
            t = np.array([kandydaci[i] for i in perm])
            roznica = np.abs(boki(t[:, :2]) - boki_ref)
            if roznica.max() > TOL_BOKU_MM or orientacja(t[:, :2]) != or_ref:
                continue
            if roznica.sum() < blad:
                najlepsza, blad = t, roznica.sum()
    if najlepsza is None:
        raise BladPlytki(f"zly uklad: {len(kandydaci)} dolkow znacznikow nie pasuje do trojkata A-B-C "
                         f"ukladu {uklad.nazwa}")
    return najlepsza


def wyrownaj(skan: trimesh.Trimesh, uklad: Uklad, ustawienia) -> Wyrownanie:
    """Macierz skan -> uklad plytki z 3 znacznikow (Kabsch) i ICP do modelu plytki."""
    v = np.asarray(skan.vertices, dtype=np.float64)
    uzyte = np.zeros(len(v), dtype=bool)
    uzyte[np.asarray(skan.faces, dtype=np.int64).ravel()] = True
    v = v[uzyte]  # tylko wierzcholki scian
    if len(v) < 100:
        raise BladPlytki("brak znacznikow: skan pusty")
    T_w = _uklad_wstepny(v, uklad)
    p = _przenies(v, T_w)
    kandydaci = _kandydaci_znacznikow(p[::CO_KTORY_DO_KANDYDATOW], uklad)
    if len(kandydaci) < 3:
        raise BladPlytki(f"brak znacznikow: znaleziono {len(kandydaci)} z 3 dolkow znacznikow A, B, C")
    t_w = _trojka(kandydaci, uklad)
    T_inv = np.linalg.inv(T_w)
    zrodlo = _przenies(t_w, T_inv)
    cel = np.array([(m[0], m[1], -m[3]) for m in (uklad.znaczniki[n] for n in "ABC")], dtype=np.float64)
    T = kabsch(zrodlo, cel)

    # ICP point-to-plane: otoczenia znacznikow i plaski wierzch przy krawedziach
    p = _przenies(v, T)
    wybrane = np.flatnonzero(_maska_icp(uklad, p))
    if len(wybrane) > MAX_PUNKTOW_ICP:
        wybrane = wybrane[:: int(math.ceil(len(wybrane) / MAX_PUNKTOW_ICP))]
    zrodlo_icp = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(v[wybrane]))
    cel_icp = _cel_icp(uklad)
    wynik = None
    for odl in ODLEGLOSC_ICP_MM:
        wynik = o3d.pipelines.registration.registration_icp(
            zrodlo_icp, cel_icp, odl, T,
            o3d.pipelines.registration.TransformationEstimationPointToPlane(),
            o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=ITERACJE_ICP))
        T = np.array(wynik.transformation, dtype=np.float64)
    if wynik.fitness < MIN_ZGODNOSC_ICP:
        raise BladPlytki(f"zly uklad: dopasowanie do modelu plytki tylko {wynik.fitness:.2f} punktow")
    blad = float(wynik.inlier_rmse)
    prog = float(ustawienia.plytka.max_blad_wyrownania_mm)
    if blad > prog:
        raise BladPlytki(f"zly uklad: blad wyrownania {blad:.3f} mm > {prog} mm")

    # kontrola orientacji: wyciecie D bez materialu
    p = _przenies(v, T)
    x_min, x_max, y_min, y_max = uklad.wyciecie
    z = ZAPAS_WYCIECIA_MM
    w_wycieciu = (p[:, 0] > x_min + z) & (p[:, 0] < x_max - z) & (p[:, 1] > y_min + z) & \
                 (p[:, 1] < y_max - z) & (p[:, 2] < -z) & (p[:, 2] > -uklad.grubosc + z)
    if np.count_nonzero(w_wycieciu) > MAX_PUNKTOW_W_WYCIECIU:
        raise BladPlytki("zly uklad: material w miejscu wyciecia D (plytka odwrocona albo inny uklad)")

    znaczniki = _zmierz_znaczniki(v, T, uklad)
    return Wyrownanie(T_skan_do_plytki=T, blad_mm=blad, znaczniki_xyz=znaczniki)
