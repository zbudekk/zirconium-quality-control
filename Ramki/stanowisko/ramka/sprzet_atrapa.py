"""Atrapa sprzetu ramki: wszystko w pamieci, sterowana z testow albo z narzedzia atrapa_ramki.

- `poloz_plytke(n)` / `zdejmij_plytke()` - czujniki Halla (surowy odczyt; odbija program),
- `nacisnij(klawisz)` - klawiatura ramki porannej (nazwy z protokol.KLAWISZE),
- `klatka` - ostatnia klatka wyslana do "matrycy", `historia` - (czas, plytka, klatka) kazdej
  wyslanej klatki, `zmiany_plytki` - (czas, n) kazdego polozenia / zdjecia,
- `czekaj(warunek, timeout)` - czeka, az warunek(atrapa) bedzie prawdziwy (po kazdej klatce).
Tylko biblioteka standardowa.
"""
from __future__ import annotations

import threading
import time

from .protokol import KLAWISZE
from .sprzet import Sprzet


class SprzetAtrapa(Sprzet):
    def __init__(self, zegar=time.perf_counter, max_historii: int = 20000):
        self._zegar = zegar
        self._warunek = threading.Condition()
        self._plytka = 0
        self._klawisze = []
        self.klatka = None
        self.historia = []
        self.zmiany_plytki = []
        self.max_historii = max_historii
        self.temp_c = None
        self.zamknieta = False

    # ------------------------------------------------------------ sterowanie z testow

    def poloz_plytke(self, n: int) -> None:
        if not (0 <= int(n) <= 7):
            raise ValueError("numer plytki 0..7")
        with self._warunek:
            self._plytka = int(n)
            self.zmiany_plytki.append((self._zegar(), int(n)))

    def zdejmij_plytke(self) -> None:
        self.poloz_plytke(0)

    def nacisnij(self, klawisz: str) -> None:
        if klawisz not in KLAWISZE:
            raise ValueError("nieznany klawisz")
        with self._warunek:
            self._klawisze.append(klawisz)

    @property
    def plytka(self) -> int:
        return self._plytka

    def piksel(self, x: int, y: int):
        return self.klatka.piksel(x, y) if self.klatka is not None else (0, 0, 0)

    def czekaj(self, warunek, timeout: float = 2.0) -> bool:
        """Czeka, az warunek(self) bedzie prawdziwy; sprawdza po kazdej nowej klatce."""
        koniec = self._zegar() + timeout
        with self._warunek:
            while True:
                if self.klatka is not None and warunek(self):
                    return True
                pozostalo = koniec - self._zegar()
                if pozostalo <= 0:
                    return False
                self._warunek.wait(min(pozostalo, 0.05))

    # ------------------------------------------------------------ interfejs Sprzet

    def odczytaj_plytke(self) -> int:
        return self._plytka

    def pobierz_klawisze(self) -> list:
        with self._warunek:
            k, self._klawisze = self._klawisze, []
        return k

    def pokaz(self, klatka) -> None:
        kopia = klatka.kopia()
        with self._warunek:
            self.klatka = kopia
            self.historia.append((self._zegar(), self._plytka, kopia))
            if len(self.historia) > self.max_historii:
                del self.historia[: len(self.historia) - self.max_historii]
            self._warunek.notify_all()

    def temperatura(self):
        return self.temp_c

    def zamknij(self) -> None:
        self.zamknieta = True
