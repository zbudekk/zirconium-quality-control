"""Ranking kandydatow (pokrycie, potem rms) i pewnosc identyfikacji."""

from dataclasses import dataclass, field

import numpy as np

ROWNE_POKRYCIE = 0.005


@dataclass(eq=False)
class Kandydat:
    projekt_id: str
    wspolczynnik: float
    T_projekt_do_fragmentu: np.ndarray  # 4x4 ze skala: projekt w ukladzie CAD -> fragment
    pokrycie: float
    rms_mm: float


@dataclass(eq=False)
class WynikDopasowania:
    kandydaci: list[Kandydat] = field(default_factory=list)  # malejaco po pokryciu
    pewnosc: str = "brak"  # "pewny" | "dwuznaczny" | "brak"


def uporzadkuj(kandydaci: list[Kandydat]) -> list[Kandydat]:
    """Malejaco po pokryciu; pokrycia rowne w granicach +-0,005 rozstrzyga mniejsze rms."""
    wynik = sorted(kandydaci, key=lambda k: (-k.pokrycie, k.rms_mm))
    zmiana = True
    while zmiana:  # sortowanie babelkowe po relacji "prawie rowne pokrycie -> rms"
        zmiana = False
        for i in range(len(wynik) - 1):
            a, b = wynik[i], wynik[i + 1]
            if abs(a.pokrycie - b.pokrycie) <= ROWNE_POKRYCIE and b.rms_mm < a.rms_mm:
                wynik[i], wynik[i + 1] = b, a
                zmiana = True
    return wynik


def min_pokrycie(ustawienia, tryb: str) -> float:
    d = ustawienia.dopasowanie
    if tryb == "wieczor":
        return d.min_pokrycie_wieczor
    if tryb == "rano":
        return d.min_pokrycie_rano
    raise ValueError(f"nieznany tryb dopasowania: {tryb!r} (wieczor albo rano)")


def pewnosc(kandydaci: list[Kandydat], ustawienia, tryb: str) -> str:
    """pewny / dwuznaczny / brak wg min_pokrycie trybu i margines_pewnosci (kandydaci uporzadkowani)."""
    prog = min_pokrycie(ustawienia, tryb)
    if not kandydaci or kandydaci[0].pokrycie < prog:
        return "brak"
    if len(kandydaci) < 2:
        return "pewny"
    top1, top2 = kandydaci[0].pokrycie, kandydaci[1].pokrycie
    if top1 - top2 >= ustawienia.dopasowanie.margines_pewnosci or top2 < prog:
        return "pewny"
    return "dwuznaczny"


def wynik(kandydaci: list[Kandydat], ustawienia, tryb: str) -> WynikDopasowania:
    uporzadkowani = uporzadkuj(kandydaci)
    return WynikDopasowania(kandydaci=uporzadkowani, pewnosc=pewnosc(uporzadkowani, ustawienia, tryb))
