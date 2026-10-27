"""Wykrywanie drgniecia skanera: podwojona powierzchnia (druga warstwa ok. 0,1 mm obok pierwszej)."""

from __future__ import annotations

import numpy as np

from .odchylki import mapa_odchylek
from .ubytki import Sasiedztwo, promien_wygladzania, sasiedztwo

# para "podwojnej powierzchni": punkty w odleglosci <= PROMIEN_PARY x drgniecie_odleglosc_mm, nie
# polaczone krawedzia siatki, z |d1 - d2| >= drgniecie_odleglosc_mm - ZAPAS_ROZNICY_MM (d wygladzone
# po 1-pierscieniu siatki: warstwy nie maja wspolnych krawedzi, wiec sie nie mieszaja). Sztywne
# przesuniecie T zmienia d lagodnie, wiec bliskie punkty jednej warstwy maja prawie rowne d.
PROMIEN_PARY = 2.0
ZAPAS_ROZNICY_MM = 0.02


def promien_sasiedztwa(mapa, ustawienia) -> float:
    """Promien wspolnego sasiedztwa dla drgniecia i wygladzania."""
    return max(PROMIEN_PARY * float(ustawienia.ubytki.drgniecie_odleglosc_mm),
               promien_wygladzania(mapa, ustawienia))


def wygladz_pierscien(d: np.ndarray, kraw: np.ndarray) -> np.ndarray:
    """Srednia d po wierzcholku i sasiadach w siatce."""
    if len(kraw) == 0:
        return d
    n = len(d)
    a, b = kraw[:, 0], kraw[:, 1]
    suma = d + np.bincount(a, weights=d[b], minlength=n) + np.bincount(b, weights=d[a], minlength=n)
    return suma / (1.0 + np.bincount(a, minlength=n) + np.bincount(b, minlength=n))


def udzial_podwojnej_powierzchni(mapa, ustawienia, s: Sasiedztwo | None = None) -> float:
    """Udzial wierzcholkow majacych pare z drugiej warstwy powierzchni."""
    n = len(mapa.punkty)
    if n == 0:
        return 0.0
    odl = float(ustawienia.ubytki.drgniecie_odleglosc_mm)
    if s is None:
        s = sasiedztwo(mapa, promien_sasiedztwa(mapa, ustawienia))
    d = wygladz_pierscien(np.asarray(mapa.odleglosci, dtype=np.float64), s.krawedzie)
    para = s.odl <= PROMIEN_PARY * odl
    i, j = s.i[para], s.j[para]
    para = np.abs(d[i] - d[j]) >= odl - ZAPAS_ROZNICY_MM
    i, j = i[para], j[para]
    if len(s.krawedzie):
        kody = s.krawedzie[:, 0] * n + s.krawedzie[:, 1]  # posortowane (krawedzie_siatki)
        szukane = i * n + j
        poz = np.minimum(np.searchsorted(kody, szukane), len(kody) - 1)
        bez_krawedzi = kody[poz] != szukane
        i, j = i[bez_krawedzi], j[bez_krawedzi]
    oznaczone = np.zeros(n, dtype=bool)
    oznaczone[i] = True
    oznaczone[j] = True
    return float(oznaczone.mean())


def drgniecie_z_mapy(mapa, ustawienia, s: Sasiedztwo | None = None) -> bool:
    return udzial_podwojnej_powierzchni(mapa, ustawienia, s) >= float(ustawienia.ubytki.drgniecie_udzial)


def wykryj_drgniecie(fragment, projekt, T, ustawienia) -> bool:
    return drgniecie_z_mapy(mapa_odchylek(fragment, projekt, T, ustawienia), ustawienia)
