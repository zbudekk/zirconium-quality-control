"""Ciecie skanu wyrownanego na fragmenty gniazd: sciany dalej od modelu plytki = prace, skladowe spojne."""

from __future__ import annotations

import itertools
from dataclasses import dataclass

import numpy as np
import open3d as o3d
import trimesh

from qc.uklad import Uklad

from .kod import numer_plytki
from .wyrownanie import siatka_referencyjna

PROG_OD_PLYTKI_MM = 0.25  # srodek sciany dalej od modelu plytki = praca
ZAPAS_NAD_PLYTKA_MM = 0.5  # sciany wyzej niz najwyzszy punkt modelu + zapas = praca bez liczenia odleglosci
SCALANIE_MM = 0.2  # mala skladowa blizej niz tyle od duzej = ta sama praca (T-junctions, przerwy siatki)
ZAPAS_PRZECIECIA_MM = 0.3
MIN_PRZECIEC = 30  # krawedzi przebijajacych druga skladowa (most: setki; prace na sobie: 0)
MIN_Z_W_GNIEZDZIE_MM = -1.0  # praca w gniezdzie siega glebiej niz wierzch plytki
STANY = ("puste", "praca", "podwojne", "poza_gniazdem")
_BRAK = object()


@dataclass
class Fragment:
    gniazdo: int
    siatka: trimesh.Trimesh  # uklad plytki
    stan: str  # "puste" | "praca" | "podwojne" | "poza_gniazdem"


def _pusta_siatka() -> trimesh.Trimesh:
    return trimesh.Trimesh(np.zeros((0, 3)), np.zeros((0, 3), dtype=np.int64), process=False)


def _podsiatka(v: np.ndarray, f: np.ndarray) -> trimesh.Trimesh:
    """Siatka ze scian f tylko z uzywanymi wierzcholkami."""
    uzyte, nowe = np.unique(f, return_inverse=True)
    return trimesh.Trimesh(v[uzyte], nowe.reshape(f.shape), process=False)


def _pola(v: np.ndarray, f: np.ndarray) -> np.ndarray:
    a, b, c = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    return np.linalg.norm(np.cross(b - a, c - a), axis=1) / 2


def _odleglosci_od_plytki(ref: trimesh.Trimesh, punkty: np.ndarray) -> np.ndarray:
    """Odleglosc bez znaku od modelu plytki; jedna RaycastingScene na wywolanie."""
    scena = o3d.t.geometry.RaycastingScene()
    scena.add_triangles(o3d.core.Tensor(np.asarray(ref.vertices, dtype=np.float32)),
                        o3d.core.Tensor(np.asarray(ref.faces, dtype=np.uint32)))
    wynik = scena.compute_distance(o3d.core.Tensor(np.asarray(punkty, dtype=np.float32)))
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


def _scal_przecinajace(vl: np.ndarray, fl: np.ndarray, et_s: np.ndarray, duze: np.ndarray) -> np.ndarray:
    """Duze skladowe, ktorych powierzchnie sie przecinaja (most z czesci bez boolean), w jedna etykiete.

    Przeciecie = krawedzie jednej skladowej przebijaja trojkaty drugiej (>= MIN_PRZECIEC); prace lezace
    na sobie (stan podwojne) sie nie przecinaja.
    """
    if len(duze) < 2:
        return et_s
    sciany = {s: fl[et_s == s] for s in duze}
    pudla = {}
    for s, f in sciany.items():
        p = vl[np.unique(f)]
        pudla[s] = (p.min(axis=0) - ZAPAS_PRZECIECIA_MM, p.max(axis=0) + ZAPAS_PRZECIECIA_MM)
    rodzic = {s: s for s in duze}

    def korzen(s):
        while rodzic[s] != s:
            rodzic[s] = rodzic[rodzic[s]]
            s = rodzic[s]
        return s

    sceny = {}
    for a, b in itertools.combinations(duze, 2):
        (amin, amax), (bmin, bmax) = pudla[a], pudla[b]
        if np.any(amin > bmax) or np.any(bmin > amax) or korzen(a) == korzen(b):
            continue
        # krawedzie mniejszej skladowej w pudle wiekszej
        a, b = (a, b) if len(sciany[a]) <= len(sciany[b]) else (b, a)
        bmin, bmax = pudla[b]
        f = sciany[a]
        w_pudle = np.all((vl[f] >= bmin) & (vl[f] <= bmax), axis=2).any(axis=1)
        if not w_pudle.any():
            continue
        f = f[w_pudle]
        kraw = np.unique(np.sort(np.concatenate([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]]), axis=1), axis=0)
        p0, p1 = vl[kraw[:, 0]], vl[kraw[:, 1]]
        dl = np.linalg.norm(p1 - p0, axis=1)
        if b not in sceny:
            scena = o3d.t.geometry.RaycastingScene()
            scena.add_triangles(o3d.core.Tensor(vl.astype(np.float32)),
                                o3d.core.Tensor(sciany[b].astype(np.uint32)))
            sceny[b] = scena
        promienie = np.concatenate([p0, (p1 - p0) / np.maximum(dl, 1e-12)[:, None]], axis=1)
        t = sceny[b].cast_rays(o3d.core.Tensor(promienie.astype(np.float32)))["t_hit"].numpy()
        if np.count_nonzero(t <= dl) >= MIN_PRZECIEC:
            rodzic[korzen(a)] = korzen(b)
    mapa = np.arange(et_s.max() + 1)
    for s in duze:
        mapa[s] = korzen(s)
    return mapa[et_s]


def _odleglosc_od_obrysu(g, x: float, y: float) -> float:
    (px, py), (qx, qy), r = g.os_rynienki()
    vx, vy = qx - px, qy - py
    dl2 = vx * vx + vy * vy
    t = 0.0 if dl2 == 0 else min(1.0, max(0.0, ((x - px) * vx + (y - py) * vy) / dl2))
    return float(np.hypot(x - px - t * vx, y - py - t * vy) - r)


def najblizsze_gniazdo(uklad: Uklad, x: float, y: float) -> int:
    return min(uklad.gniazda, key=lambda g: _odleglosc_od_obrysu(g, x, y)).nr


def potnij(skan_wyrownany: trimesh.Trimesh, uklad: Uklad, ustawienia, numer=_BRAK) -> list[Fragment]:
    """Fragment na kazde gniazdo (puste / praca / podwojne) + fragmenty "poza_gniazdem".

    numer = numer plytki (do modelu z reliefem i dolkami); domyslnie liczony z dolkow kodu.
    """
    if numer is _BRAK:
        numer = numer_plytki(skan_wyrownany, uklad)
    ref = siatka_referencyjna(uklad, numer)
    v = np.asarray(skan_wyrownany.vertices, dtype=np.float64)
    f = np.asarray(skan_wyrownany.faces, dtype=np.int64)
    margines = float(ustawienia.plytka.margines_gniazda_mm)
    min_pole = float(ustawienia.plytka.min_pole_pracy_mm2)

    fragmenty_gniazd = {g.nr: [] for g in uklad.gniazda}
    poza = []
    if len(f):
        srodki = v[f].mean(axis=1)
        z_max = float(np.asarray(ref.vertices)[:, 2].max())
        praca = srodki[:, 2] > z_max + ZAPAS_NAD_PLYTKA_MM
        do_sprawdzenia = np.flatnonzero(~praca)
        if len(do_sprawdzenia):
            praca[do_sprawdzenia] = _odleglosci_od_plytki(ref, srodki[do_sprawdzenia]) > PROG_OD_PLYTKI_MM
        fp = f[praca]
    else:
        fp = f
    if len(fp):
        uzyte, fl = np.unique(fp, return_inverse=True)
        fl = fl.reshape(fp.shape)
        vl = v[uzyte]
        et_w = skladowe_wierzcholkowe(fl, len(uzyte))
        _, et_w = np.unique(et_w, return_inverse=True)
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
        et_s = _scal_przecinajace(vl, fl, et_s, np.flatnonzero(pola >= min_pole))
        pola = np.bincount(et_s, weights=pola_s, minlength=len(pola))
        srodki_s = vl[fl].mean(axis=1)
        for s in np.flatnonzero(pola >= min_pole):
            maska = et_s == s
            w = pola_s[maska]
            c = (srodki_s[maska] * w[:, None]).sum(axis=0) / max(w.sum(), 1e-12)
            nr = uklad.gniazdo_dla_xy(float(c[0]), float(c[1]), margines=margines)
            sciany = fl[maska]
            if nr is not None and uklad.gniazdo_dla_xy(float(c[0]), float(c[1])) is None and \
                    vl[np.unique(sciany), 2].min() > MIN_Z_W_GNIEZDZIE_MM:
                nr = None  # srodek tylko w pasie marginesu i praca nie siega w glab gniazda = na sciance
            if nr is None:
                poza.append(Fragment(najblizsze_gniazdo(uklad, float(c[0]), float(c[1])),
                                     _podsiatka(vl, sciany), "poza_gniazdem"))
            else:
                fragmenty_gniazd[nr].append(sciany)

    wynik = []
    for g in uklad.gniazda:
        czesci = fragmenty_gniazd[g.nr]
        if not czesci:
            wynik.append(Fragment(g.nr, _pusta_siatka(), "puste"))
        else:
            stan = "praca" if len(czesci) == 1 else "podwojne"
            wynik.append(Fragment(g.nr, _podsiatka(vl, np.concatenate(czesci)), stan))
    return wynik + poza
