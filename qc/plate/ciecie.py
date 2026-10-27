"""Ciecie skanu wyrownanego na fragmenty gniazd: sciany dalej od modelu plytki = prace, skladowe spojne."""

from __future__ import annotations

import threading
from dataclasses import dataclass

import numpy as np
import open3d as o3d
import trimesh

from qc.uklad import Uklad

from .wyrownanie import klucz_ukladu, siatka_referencyjna

ZAPAS_NAD_PLYTKA_MM = 0.5  # sciany wyzej niz najwyzszy punkt modelu + zapas = praca bez liczenia odleglosci
SCALANIE_MM = 0.2  # mala skladowa blizej niz tyle od duzej = ta sama praca (T-junctions, przerwy siatki)
MIN_Z_W_GNIEZDZIE_MM = -1.0  # praca w gniezdzie siega glebiej niz wierzch plytki
ZAPAS_RELIEFU_MM = 1.0  # obszar reliefu numeru: kwadrat o boku wysokosci tekstu + 2 x zapas
ZAPAS_WYSOKOSCI_RELIEFU_MM = 0.2
_BLOKADA_SCENY = threading.Lock()
_SCENY: dict = {}
STANY = ("puste", "praca", "podwojne", "poza_gniazdem")


@dataclass
class Fragment:
    gniazdo: int
    siatka: trimesh.Trimesh  # uklad plytki
    stan: str  # "puste" | "praca" | "podwojne" | "poza_gniazdem"


def _pusta_siatka() -> trimesh.Trimesh:
    return trimesh.Trimesh(np.zeros((0, 3)), np.zeros((0, 3), dtype=np.int64), process=False)


def _reindeksuj(f: np.ndarray, n: int) -> tuple[np.ndarray, np.ndarray]:
    """(indeksy uzytych wierzcholkow rosnaco, sciany z nowymi indeksami) bez sortowania (O(n))."""
    uzyte = np.zeros(n, dtype=bool)
    uzyte[f.ravel()] = True
    nowe = np.cumsum(uzyte) - 1
    return np.flatnonzero(uzyte), nowe[f]


def _podsiatka(v: np.ndarray, f: np.ndarray) -> trimesh.Trimesh:
    """Siatka ze scian f tylko z uzywanymi wierzcholkami."""
    uzyte, nowe = _reindeksuj(f, len(v))
    return trimesh.Trimesh(v[uzyte], nowe, process=False)


def _pola(v: np.ndarray, f: np.ndarray) -> np.ndarray:
    a, b, c = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    return np.linalg.norm(np.cross(b - a, c - a), axis=1) / 2


def scena_plytki(uklad: Uklad):
    """RaycastingScene modelu bazowego plytki, raz na uklad (cache pod blokada).

    Pierwsze zapytanie (commit sceny Embree) wykonywane przy tworzeniu pod blokada; pozniejsze zapytania
    tylko czytaja scene, wiec mozna je wolac z wielu watkow.
    """
    klucz = (klucz_ukladu(uklad), "scena")
    with _BLOKADA_SCENY:
        scena = _SCENY.get(klucz)
        if scena is None:
            ref = siatka_referencyjna(uklad, None)
            scena = o3d.t.geometry.RaycastingScene()
            scena.add_triangles(o3d.core.Tensor(np.asarray(ref.vertices, dtype=np.float32)),
                                o3d.core.Tensor(np.asarray(ref.faces, dtype=np.uint32)))
            scena.compute_distance(o3d.core.Tensor(np.zeros((1, 3), dtype=np.float32)))
            _SCENY[klucz] = scena
    return scena


def _odleglosci_od_plytki(uklad: Uklad, punkty: np.ndarray) -> np.ndarray:
    """Odleglosc bez znaku od modelu plytki."""
    wynik = scena_plytki(uklad).compute_distance(o3d.core.Tensor(np.asarray(punkty, dtype=np.float32)))
    return wynik.numpy().astype(np.float64)


def skladowe_wierzcholkowe(f: np.ndarray, n: int) -> np.ndarray:
    """Etykieta skladowej (najmniejszy indeks wierzcholka) dla kazdego wierzcholka; sciany lacza 3 wierzcholki.

    Zaczepianie korzeni na minimum + kompresja sciezek (numpy, bez rekurencji).
    """
    rodzic = np.arange(n, dtype=np.int64)
    while True:
        rf = rodzic[f]
        m = rf.min(axis=1)
        nowy = rodzic.copy()
        for k in range(3):
            np.minimum.at(nowy, rf[:, k], m)
        while True:
            skok = nowy[nowy]
            if np.array_equal(skok, nowy):
                break
            nowy = skok
        if np.array_equal(nowy, rodzic):
            return rodzic
        rodzic = nowy


def _w_reliefie(uklad: Uklad, p: np.ndarray) -> bool:
    """Skladowa w calosci w obszarze reliefu numeru i nie wyzej niz relief = relief, nie praca."""
    if uklad.relief_numeru is None:
        return False
    rx, ry, wysokosc_tekstu, wysokosc = uklad.relief_numeru
    pol = wysokosc_tekstu / 2 + ZAPAS_RELIEFU_MM
    return bool(np.all(np.abs(p[:, 0] - rx) <= pol) and np.all(np.abs(p[:, 1] - ry) <= pol)
                and p[:, 2].max() <= wysokosc + ZAPAS_WYSOKOSCI_RELIEFU_MM)


def _stan(g, pola: list[float], min_udzial: float) -> str:
    """Stan gniazda ze skladowych: w rynience (tylko mosty) zawsze jedna praca; w stozku osobna praca
    = skladowa o polu >= min_udzial x najwieksza (mniejsze wyspy, np. przy dnie gniazda, naleza do pracy)."""
    if g.rodzaj == "rynienka":
        return "praca"
    najwieksza = max(pola)
    prace = sum(1 for p in pola if p >= min_udzial * najwieksza)
    return "praca" if prace == 1 else "podwojne"


def _odleglosc_od_obrysu(g, x: float, y: float) -> float:
    (px, py), (qx, qy), r = g.os_rynienki()
    vx, vy = qx - px, qy - py
    dl2 = vx * vx + vy * vy
    t = 0.0 if dl2 == 0 else min(1.0, max(0.0, ((x - px) * vx + (y - py) * vy) / dl2))
    return float(np.hypot(x - px - t * vx, y - py - t * vy) - r)


def najblizsze_gniazdo(uklad: Uklad, x: float, y: float) -> int:
    return min(uklad.gniazda, key=lambda g: _odleglosc_od_obrysu(g, x, y)).nr


def potnij(skan_wyrownany: trimesh.Trimesh, uklad: Uklad, ustawienia) -> list[Fragment]:
    """Fragment na kazde gniazdo (puste / praca / podwojne) + fragmenty "poza_gniazdem".

    Model plytki bazowy (3 dolki, bez reliefu) niezaleznie od numeru: wypelniony dolek kodu to wyspa
    ok. 3 mm2 (< min_pole_pracy_mm2), relief numeru pomijany regula obszaru reliefu.
    """
    ref = siatka_referencyjna(uklad, None)
    v = np.asarray(skan_wyrownany.vertices, dtype=np.float64)
    f = np.asarray(skan_wyrownany.faces, dtype=np.int64)
    margines = float(ustawienia.plytka.margines_gniazda_mm)
    min_pole = float(ustawienia.plytka.min_pole_pracy_mm2)
    prog = float(ustawienia.plytka.prog_od_plytki_mm)
    min_udzial = float(ustawienia.plytka.min_udzial_drugiej_pracy)

    fragmenty_gniazd = {g.nr: [] for g in uklad.gniazda}
    poza = []
    if len(f):
        # odleglosc wierzcholkow od modelu (2x mniej zapytan niz srodki scian); sciana = srednia z 3
        uzyte_w = np.zeros(len(v), dtype=bool)
        uzyte_w[f.ravel()] = True
        z_max = float(np.asarray(ref.vertices)[:, 2].max())
        odl = np.zeros(len(v))
        wysoko = uzyte_w & (v[:, 2] > z_max + ZAPAS_NAD_PLYTKA_MM + prog)
        odl[wysoko] = np.inf
        do_sprawdzenia = np.flatnonzero(uzyte_w & ~wysoko)
        if len(do_sprawdzenia):
            odl[do_sprawdzenia] = _odleglosci_od_plytki(uklad, v[do_sprawdzenia])
        odl_s = np.minimum(odl[f], 1e6).mean(axis=1)
        fp = f[odl_s > prog]
    else:
        fp = f
    if len(fp):
        uzyte, fl = _reindeksuj(fp, len(v))
        vl = v[uzyte]
        et_w = skladowe_wierzcholkowe(fl, len(uzyte))
        korzenie = et_w == np.arange(len(et_w))
        et_w = (np.cumsum(korzenie) - 1)[et_w]  # etykiety 0..k-1
        et_s = et_w[fl[:, 0]]
        pola_s = _pola(vl, fl)
        pola = np.bincount(et_s, weights=pola_s)
        duze = pola >= min_pole
        male = np.flatnonzero(~duze)
        if len(male) and duze.any():
            # male skladowe przy duzych (przerwy siatki) dolaczane do najblizszej duzej
            w_duzych = np.flatnonzero(duze[et_w])
            w_malych = np.flatnonzero(~duze[et_w])
            nns = o3d.core.nns.NearestNeighborSearch(o3d.core.Tensor(vl[w_duzych]))
            nns.knn_index()
            idx, d2 = nns.knn_search(o3d.core.Tensor(vl[w_malych]), 1)
            idx = idx.numpy().ravel().astype(np.int64)
            d = np.sqrt(d2.numpy().ravel())
            cel = np.full(len(pola), -1, dtype=np.int64)
            blisko = d < SCALANIE_MM
            for s, t in zip(et_w[w_malych][blisko], et_w[w_duzych][idx[blisko]]):
                if cel[s] < 0:
                    cel[s] = t
            mapa = np.where(cel >= 0, cel, np.arange(len(pola)))
            et_s = mapa[et_s]
            pola = np.bincount(et_s, weights=pola_s, minlength=len(pola))
        srodki_s = vl[fl].mean(axis=1)
        for s in np.flatnonzero(pola >= min_pole):
            maska = et_s == s
            w = pola_s[maska]
            c = (srodki_s[maska] * w[:, None]).sum(axis=0) / max(w.sum(), 1e-12)
            nr = uklad.gniazdo_dla_xy(float(c[0]), float(c[1]), margines=margines)
            sciany = fl[maska]
            if _w_reliefie(uklad, vl[sciany.ravel()]):
                continue
            if nr is not None and uklad.gniazdo_dla_xy(float(c[0]), float(c[1])) is None and \
                    vl[sciany.ravel(), 2].min() > MIN_Z_W_GNIEZDZIE_MM:
                nr = None  # srodek tylko w pasie marginesu i praca nie siega w glab gniazda = na sciance
            if nr is None:
                poza.append(Fragment(najblizsze_gniazdo(uklad, float(c[0]), float(c[1])),
                                     _podsiatka(vl, sciany), "poza_gniazdem"))
            else:
                fragmenty_gniazd[nr].append((sciany, float(pola[s])))

    wynik = []
    for g in uklad.gniazda:
        czesci = fragmenty_gniazd[g.nr]
        if not czesci:
            wynik.append(Fragment(g.nr, _pusta_siatka(), "puste"))
        else:
            stan = _stan(g, [p for _, p in czesci], min_udzial)
            wynik.append(Fragment(g.nr, _podsiatka(vl, np.concatenate([c for c, _ in czesci])), stan))
    return wynik + poza
