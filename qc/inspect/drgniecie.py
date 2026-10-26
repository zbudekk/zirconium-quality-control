"""Wykrywanie drgniecia skanera: podwojona powierzchnia przesunieta o ok. 0,1 mm."""

from __future__ import annotations

import numpy as np

from .odchylki import mapa_odchylek
from .ubytki import krawedzie, wygladz

# dolna granica pasma = drgniecie_odleglosc_mm - ZAPAS_PASMA_MM (kopia platu przesunieta o ok. 0,1 mm
# wzdluz sredniej normalnej; wierzcholki o normalnej odchylonej od niej daja mniejsze |d|)
ZAPAS_PASMA_MM = 0.04
GORA_PASMA_MM = 0.16


def udzial_w_pasmie(d_wygladzone: np.ndarray, ustawienia) -> float:
    """Udzial wierzcholkow z |d| (wygladzonym po sasiadach w siatce) w pasmie drgniecia."""
    if len(d_wygladzone) == 0:
        return 0.0
    dol = float(ustawienia.ubytki.drgniecie_odleglosc_mm) - ZAPAS_PASMA_MM
    a = np.abs(d_wygladzone)
    return float(np.mean((a >= dol) & (a <= GORA_PASMA_MM)))


def drgniecie_z_mapy(d_wygladzone: np.ndarray, ustawienia) -> bool:
    return udzial_w_pasmie(d_wygladzone, ustawienia) >= float(ustawienia.ubytki.drgniecie_udzial)


def wykryj_drgniecie(fragment, projekt, T, ustawienia) -> bool:
    mapa = mapa_odchylek(fragment, projekt, T, ustawienia)
    d = np.asarray(mapa.odleglosci, dtype=np.float64)
    return drgniecie_z_mapy(wygladz(d, krawedzie(mapa, ustawienia)), ustawienia)
