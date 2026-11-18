"""Interfejs sprzetu ramki i odbijanie odczytu czujnikow Halla.

Implementacje: `sprzet_atrapa.SprzetAtrapa` (w pamieci, do testow i pracy bez elektroniki)
i `sprzet_rpi.SprzetRpi` (Raspberry Pi 4 + RGB Matrix Bonnet + A3144 + klawiatura USB).
Program ramki rozmawia ze sprzetem tylko przez te metody.
"""
from __future__ import annotations

from .obraz import Klatka
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

    def wygas(self) -> None:
        """Awaryjne wygaszenie calej matrycy (P4) - wolane, gdy nie udalo sie pokazac klatki."""
        self.pokaz(Klatka())

    def zamknij(self) -> None:
        """Gasi matryce i zwalnia zasoby."""


class Odbijanie:
    """Odbijanie odczytu czujnikow Halla, NIESYMETRYCZNE (P7): gaszenie od razu, zapalanie po ustaleniu.

    Przy zdejmowaniu i kladzeniu plytki magnesy mijaja czujniki w roznych chwilach, wiec przez
    kilka milisekund odczyt bywa przypadkowy (np. 5 -> 1 -> 0).
    - `stabilna` - ustalony numer plytki (zdarzenia `plytka`); `pewna` - czy gniazda moga swiecic.
    - Pierwszy surowy odczyt inny niz `stabilna` (takze 0 i odczyt drgajacy): `pewna` = False od razu.
    - Nowy numer ustala sie, gdy surowy odczyt jest staly przez `stabilnosc_s` (wtedy od razu pewny).
    - Powrot do `stabilna` po zakloceniu: `pewna` dopiero po `stabilnosc_s` stalego odczytu.
    - Odczyt rozny od `stabilna` dluzej niz `stabilnosc_s`, ale nieustalony (drgania): plytka uznana
      za zdjeta (`stabilna` = 0) - gniazda ciemne przez caly czas drgan.
    - Runda 3 (drgania wolniejsze niz `stabilnosc_s`): POWROT do numeru sprzed ostatniej zmiany (A -> 0 -> A,
      A -> B -> A) ustala sie najwczesniej `odstep_powrotu_s` po tej zmianie - najwyzej 1 para zdarzen na
      odstep, gniazda ciemne do tego czasu. Zdjecie plytki (zmiana na 0) i zmiana na INNY numer (4 -> 0 -> 5)
      bez opoznienia. Bez tego drgajacy czujnik dawalby ok. 20 zdarzen na sekunde, a plan (przyjmowany
      tylko z `zdarzenia_do` = numer ostatniego zdarzenia) nie mialby szans.
    - E3-A8p (wynik niezalezny od rozstawu odczytow): przy gestym probkowaniu zdjecie (prog: pierwszy inny
      odczyt + `stabilnosc_s`) zawsze wypada przed ustaleniem nowego numeru (prog: poczatek nowego odczytu
      + `stabilnosc_s`). Przy rzadszych obiegach petli (zegar Windows ok. 15,6 ms, obciazenie) oba progi
      mijaja w jednym odczycie - wtedy tez najpierw 0, nowy numer w nastepnym odczycie. Wczesniej wygrywalo
      ustalenie: zdarzenie 0 ginelo (4 -> 5), a 5 -> 0 -> 4 po takim skoku bylo wstrzymane jak powrot (3 s).
    Wymaganie I5: zmiana ponizej 100 ms - domyslnie 30 ms.
    """

    def __init__(self, stabilnosc_s: float = 0.03, poczatkowa: int = 0, odstep_powrotu_s: float = 0.0):
        self.stabilnosc_s = float(stabilnosc_s)
        self.odstep_powrotu_s = float(odstep_powrotu_s)
        self.stabilna = poczatkowa
        self.pewna = False
        self._ostatnia = None      # ostatni surowy odczyt
        self._ostatnia_od = None   # od kiedy surowy odczyt jest staly
        self._inna_od = None       # od kiedy surowy odczyt jest (bez przerwy) rozny od stabilna
        self._poprzednia = None    # ustalony numer sprzed ostatniej zmiany
        self._zmiana_t = float("-inf")  # chwila ostatniej zmiany ustalonego numeru

    def _uplynelo(self, od, teraz: float) -> bool:
        return od is not None and teraz - od >= self.stabilnosc_s - 1e-9

    def _zmien(self, n: int, teraz: float) -> int:
        self._poprzednia = self.stabilna
        self.stabilna = n
        self._zmiana_t = teraz
        return n

    def podaj(self, surowa: int, teraz: float):
        """Zwraca nowy ustalony numer albo None (bez zmiany); `pewna` po kazdym odczycie."""
        if surowa != self._ostatnia:
            self._ostatnia = surowa
            self._ostatnia_od = teraz
        staly = self._uplynelo(self._ostatnia_od, teraz)
        if surowa == self.stabilna:
            self._inna_od = None
            self.pewna = staly
            return None
        self.pewna = False
        if self._inna_od is None:
            self._inna_od = teraz
        if self.stabilna != 0 and self._uplynelo(self._inna_od, teraz) and (
                not staly or (surowa != 0 and self._ostatnia_od > self._inna_od)):
            # plytka odeszla, a odczyt sie nie ustalil: jak brak plytki (ciemno do ustalenia odczytu).
            # E3-A8p: takze gdy w tym samym odczycie ustalil sie juz nowy numer, ale zaczal sie PO pierwszym
            # odczycie innym niz `stabilna` (4 -> 0 -> 5) - zdjecie przed nowym numerem, ktory ustala sie
            # w nastepnym odczycie (kolejnosc progow niezalezna od rozstawu obiegow petli)
            self._inna_od = None if surowa == 0 else teraz
            return self._zmien(0, teraz)
        if staly:
            if surowa != 0 and surowa == self._poprzednia and teraz - self._zmiana_t < self.odstep_powrotu_s:
                return None  # drgania: powrot do poprzedniego numeru wstrzymany (gniazda ciemne)
            self.pewna = True
            self._inna_od = None
            return self._zmien(surowa, teraz)
        return None
