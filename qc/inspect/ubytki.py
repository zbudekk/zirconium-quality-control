"""Wykrywanie ubytkow na mapie odchylek: wygladzanie, kandydaci, skladowe spojne, klasyfikacja."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import open3d as o3d

# sasiedztwo z siatki fragmentu (1-pierscien); bez scian: k najblizszych w promieniu
# PROMIEN_WYGLADZANIA x skaner.gestosc_mm
PROMIEN_WYGLADZANIA = 1.5
SASIEDZI_BEZ_SCIAN = 8
# minimalna liczba punktow kandydatow w skladowej (jak min_points w DBSCAN)
MIN_PUNKTOW = 4
# obszar ubytku = punkty z d <= -poziom, poziom = max(UDZIAL_POZIOMU x glebokosc szczytowa, SIGMY_SZUMU x
# sigma szumu wygladzonego d, MIN_POZIOM_MM)
UDZIAL_POZIOMU = 0.25
SIGMY_SZUMU = 3.0
MIN_POZIOM_MM = 0.02
# ostra krawedz: glebokosc / srednica >= OSTROSC (ukruszenia >= ok. 0,18, poprawki <= ok. 0,1)
OSTROSC = 0.13


@dataclass
class Ubytek:
    """Wykryty ubytek; srodek w ukladzie fragmentu."""

    srodek: np.ndarray
    srednica_mm: float
    glebokosc_mm: float
    przy_brzegu: bool


@dataclass
class WynikInspekcji:
    ubytki: list[Ubytek] = field(default_factory=list)  # ukruszenia przy brzegu
    poprawki: list[Ubytek] = field(default_factory=list)  # szerokie gladkie zaglebienia
    inne: list[Ubytek] = field(default_factory=list)  # pozostale (poza pasem brzegu, nietypowe)
    drgniecie: bool = False
    mapa: np.ndarray = field(default_factory=lambda: np.zeros(0))  # odleglosci per wierzcholek


def krawedzie(mapa, ustawienia) -> np.ndarray:
    """Unikalne krawedzie (E, 2) grafu sasiedztwa wierzcholkow fragmentu."""
    n = len(mapa.punkty)
    if mapa.sciany is not None and len(mapa.sciany):
        f = np.asarray(mapa.sciany, dtype=np.int64)
        a = np.concatenate([f[:, 0], f[:, 1], f[:, 2]])
        b = np.concatenate([f[:, 1], f[:, 2], f[:, 0]])
    else:
        punkty = o3d.core.Tensor(np.ascontiguousarray(mapa.punkty, dtype=np.float32))
        nns = o3d.core.nns.NearestNeighborSearch(punkty)
        nns.knn_index()
        ind, odl2 = nns.knn_search(punkty, SASIEDZI_BEZ_SCIAN + 1)
        ind, odl2 = ind.numpy()[:, 1:].astype(np.int64), odl2.numpy()[:, 1:]
        promien = PROMIEN_WYGLADZANIA * float(ustawienia.skaner.gestosc_mm)
        dobre = odl2 <= promien ** 2
        a = np.repeat(np.arange(n), SASIEDZI_BEZ_SCIAN)[dobre.ravel()]
        b = ind.ravel()[dobre.ravel()]
    lo, hi = np.minimum(a, b), np.maximum(a, b)
    kod = np.unique(lo[lo != hi] * n + hi[lo != hi])
    return np.stack([kod // n, kod % n], axis=1)


def wygladz(d: np.ndarray, kraw: np.ndarray) -> np.ndarray:
    """Srednia d po wierzcholku i jego sasiadach."""
    n = len(d)
    a, b = kraw[:, 0], kraw[:, 1]
    suma = d + np.bincount(a, weights=d[b], minlength=n) + np.bincount(b, weights=d[a], minlength=n)
    liczba = 1.0 + np.bincount(a, minlength=n) + np.bincount(b, minlength=n)
    return suma / liczba


def sigma_szumu(d: np.ndarray) -> float:
    return float(1.4826 * np.median(np.abs(d - np.median(d))))


def skladowe(maska: np.ndarray, kraw: np.ndarray) -> np.ndarray:
    """Etykiety skladowych spojnych podgrafu na wierzcholkach maski (-1 poza maska)."""
    etykiety = np.where(maska, np.arange(len(maska)), -1)
    k = kraw[maska[kraw[:, 0]] & maska[kraw[:, 1]]]
    if len(k) == 0:
        return etykiety
    a, b = k[:, 0], k[:, 1]
    while True:
        m = np.minimum(etykiety[a], etykiety[b])
        stare = etykiety.copy()
        np.minimum.at(etykiety, a, m)
        np.minimum.at(etykiety, b, m)
        wybrane = etykiety >= 0
        etykiety[wybrane] = etykiety[etykiety[wybrane]]  # skok wskaznikow (etykieta <= indeks)
        if np.array_equal(etykiety, stare):
            return etykiety


def _srednica(punkty: np.ndarray, srodek: np.ndarray) -> float:
    """2 x promien kola o tym samym 90. percentylu odleglosci od srodka."""
    p90 = float(np.percentile(np.linalg.norm(punkty - srodek, axis=1), 90))
    return 2.0 * p90 / np.sqrt(0.9)


def szukaj_ubytkow(mapa, ustawienia, kraw: np.ndarray | None = None,
                   d_wygladzone: np.ndarray | None = None) -> WynikInspekcji:
    """Ubytki, poprawki i inne zaglebienia na mapie odchylek (bez sprawdzania drgniecia)."""
    u = ustawienia.ubytki
    d = np.asarray(mapa.odleglosci, dtype=np.float64)
    wynik = WynikInspekcji(mapa=d)
    if len(d) == 0:
        return wynik
    if kraw is None:
        kraw = krawedzie(mapa, ustawienia)
    ds = wygladz(d, kraw) if d_wygladzone is None else d_wygladzone
    sigma = sigma_szumu(ds)

    nasiona = skladowe(ds <= -float(u.min_glebokosc_mm), kraw)
    etyk, liczby = np.unique(nasiona[nasiona >= 0], return_counts=True)
    etyk = etyk[liczby >= MIN_PUNKTOW]
    # od najglebszych; nasiona wchloniete przez obszar wczesniejszego ubytku pomijane
    etyk = sorted(etyk, key=lambda e: float(ds[nasiona == e].min()))
    zajete = np.zeros(len(d), dtype=bool)
    for e in etyk:
        czlonkowie = np.flatnonzero(nasiona == e)
        if zajete[czlonkowie].any():
            continue
        szczyt = -float(np.percentile(ds[czlonkowie], 5))
        poziom = max(UDZIAL_POZIOMU * szczyt, SIGMY_SZUMU * sigma, MIN_POZIOM_MM)
        obszar_et = skladowe(ds <= -poziom, kraw)
        etykiety_obszaru = np.unique(obszar_et[czlonkowie])
        obszar = np.flatnonzero(np.isin(obszar_et, etykiety_obszaru[etykiety_obszaru >= 0]))
        if len(obszar) < MIN_PUNKTOW:
            continue
        zajete[obszar] = True

        glebokosc = -float(np.percentile(ds[obszar], 10))
        wagi = np.clip(-ds[obszar], 1e-9, None)
        srodek = (mapa.punkty[obszar] * wagi[:, None]).sum(axis=0) / wagi.sum()
        srednica = _srednica(mapa.punkty[obszar], srodek)
        ostra = glebokosc >= OSTROSC * srednica
        if not ostra and szczyt > poziom * 1.05:
            # profil gaussowski: promien obszaru na poziomie p -> sigma; srednica poprawki = 4 sigma
            srednica = 2.0 * srednica / np.sqrt(2.0 * np.log(szczyt / poziom))
        najglebszy = obszar[int(np.argmin(ds[obszar]))]
        ubytek = Ubytek(srodek=srodek, srednica_mm=float(srednica), glebokosc_mm=glebokosc,
                        przy_brzegu=bool(mapa.przy_brzegu[najglebszy]))
        if ostra and u.min_srednica_mm <= srednica <= u.max_srednica_mm and ubytek.przy_brzegu:
            wynik.ubytki.append(ubytek)
        elif not ostra and srednica > u.poprawka_min_srednica_mm:
            wynik.poprawki.append(ubytek)
        else:
            wynik.inne.append(ubytek)
    return wynik
