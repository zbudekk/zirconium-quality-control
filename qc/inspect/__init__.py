"""qc.inspect - inspekcja ukruszen: mapa odchylek skanu od projektu, ubytki, poprawki, drgniecie."""

from .drgniecie import drgniecie_z_mapy, promien_sasiedztwa, wykryj_drgniecie
from .odchylki import Mapa, mapa_odchylek
from .ubytki import Ubytek, WynikInspekcji, sasiedztwo, szukaj_ubytkow

__all__ = ["mapa_odchylek", "szukaj_ubytkow", "wykryj_drgniecie", "sprawdz", "Mapa", "Ubytek",
           "WynikInspekcji"]


def sprawdz(fragment, projekt, T, ustawienia) -> WynikInspekcji:
    """Mapa odchylek, drgniecie i ubytki naraz; przy drgnieciu puste listy (bez falszywych alarmow)."""
    mapa = mapa_odchylek(fragment, projekt, T, ustawienia)
    s = sasiedztwo(mapa, promien_sasiedztwa(mapa, ustawienia))
    if drgniecie_z_mapy(mapa, ustawienia, s):
        return WynikInspekcji(drgniecie=True, mapa=mapa.odleglosci)
    return szukaj_ubytkow(mapa, ustawienia, s)
