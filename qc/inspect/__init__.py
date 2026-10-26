"""qc.inspect - inspekcja ukruszen: mapa odchylek skanu od projektu, ubytki, poprawki, drgniecie."""

import numpy as np

from .drgniecie import drgniecie_z_mapy, wykryj_drgniecie
from .odchylki import Mapa, mapa_odchylek
from .ubytki import Ubytek, WynikInspekcji, krawedzie, szukaj_ubytkow, wygladz

__all__ = ["mapa_odchylek", "szukaj_ubytkow", "wykryj_drgniecie", "sprawdz", "Mapa", "Ubytek",
           "WynikInspekcji"]


def sprawdz(fragment, projekt, T, ustawienia) -> WynikInspekcji:
    """Mapa odchylek, drgniecie i ubytki naraz; przy drgnieciu puste listy (bez falszywych alarmow)."""
    mapa = mapa_odchylek(fragment, projekt, T, ustawienia)
    d = np.asarray(mapa.odleglosci, dtype=np.float64)
    kraw = krawedzie(mapa, ustawienia)
    ds = wygladz(d, kraw)
    if drgniecie_z_mapy(ds, ustawienia):
        return WynikInspekcji(drgniecie=True, mapa=d)
    return szukaj_ubytkow(mapa, ustawienia, kraw=kraw, d_wygladzone=ds)
