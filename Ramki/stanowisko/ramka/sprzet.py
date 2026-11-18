"""Interfejs sprzetu ramki i odbijanie odczytu czujnikow Halla.

Implementacje: `sprzet_atrapa.SprzetAtrapa` (w pamieci, do testow i pracy bez elektroniki)
i `sprzet_rpi.SprzetRpi` (Raspberry Pi 4 + RGB Matrix Bonnet + A3144 + klawiatura USB).
Program ramki rozmawia ze sprzetem tylko przez te metody.
"""
from __future__ import annotations

from .protokol import KLAWISZE  # noqa: F401  (logiczne nazwy klawiszy - te same w calym pakiecie)


class BladSprzetu(Exception):
    """Sprzet niedostepny albo zle skonfigurowany (np. brak biblioteki matrycy)."""


class Sprzet:
    """Sprzet ramki. Metody wolane z jednego watku petli programu."""

    def odczytaj_plytke(self) -> int:
        """Chwilowy (surowy) numer plytki z czujnikow: n = A + 2B + 4C, 0 = brak plytki."""
        raise NotImplementedError

    def pobierz_klawisze(self) -> list:
        """Klawisze nacisniete od ostatniego wywolania (nazwy z protokol.KLAWISZE), w kolejnosci."""
        raise NotImplementedError

    def pokaz(self, klatka) -> None:
        """Wyswietla klatke 64 x 64 (obraz.Klatka)."""
        raise NotImplementedError

    def temperatura(self):
        """Temperatura procesora w stopniach C albo None."""
        return None

    def zamknij(self) -> None:
        """Gasi matryce i zwalnia zasoby."""


class Odbijanie:
    """Numer plytki uznany dopiero, gdy surowy odczyt jest staly przez `stabilnosc_s`.

    Przy zdejmowaniu i kladzeniu plytki magnesy mijaja czujniki w roznych chwilach, wiec przez
    kilka milisekund odczyt bywa przypadkowy (np. 5 -> 1 -> 0). Zaklocenie krotsze niz
    `stabilnosc_s` nie daje zdarzenia. Wymaganie I5: zmiana ponizej 100 ms - domyslnie 30 ms.
    """

    def __init__(self, stabilnosc_s: float = 0.03, poczatkowa: int = 0):
        self.stabilnosc_s = float(stabilnosc_s)
        self.stabilna = poczatkowa
        self._kandydat = poczatkowa
        self._od = None

    def podaj(self, surowa: int, teraz: float):
        """Zwraca nowy ustalony numer albo None (bez zmiany)."""
        if surowa != self._kandydat:
            self._kandydat = surowa
            self._od = teraz
            return None
        if surowa == self.stabilna:
            self._od = None
            return None
        if self._od is None:
            self._od = teraz
            return None
        if teraz - self._od >= self.stabilnosc_s - 1e-9:
            self.stabilna = surowa
            self._od = None
            return surowa
        return None
