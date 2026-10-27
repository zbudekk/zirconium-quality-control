"""Wspolczynniki skali z CSV `plik;krazek;wspolczynnik;data` (plan B do czasu parsera raportow MillBox)."""

import csv
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

NAGLOWEK = ["plik", "krazek", "wspolczynnik", "data"]


@dataclass(frozen=True)
class Wspolczynnik:
    plik_stl: str
    krazek: str | None
    wspolczynnik: float
    data: date


def _liczba(tekst: str) -> float:
    k = float(tekst.strip().replace(",", "."))
    if not k > 0 or k == float("inf"):
        raise ValueError(f"wspolczynnik musi byc dodatni: {tekst}")
    return k


def _data(tekst: str) -> date:
    return datetime.fromisoformat(tekst.strip()).date()


def wczytaj(sciezka_csv) -> list[Wspolczynnik]:
    """Wczytuje CSV (srednik, UTF-8, naglowek); bledny wiersz -> ValueError z numerem linii."""
    sciezka = Path(sciezka_csv)
    wynik = []
    with sciezka.open(encoding="utf-8-sig", newline="") as f:
        czytnik = csv.reader(f, delimiter=";")
        for wiersz in czytnik:
            linia = czytnik.line_num
            if not any(p.strip() for p in wiersz):
                continue
            if linia == 1:
                if [p.strip().lower() for p in wiersz] != NAGLOWEK:
                    raise ValueError(f"linia 1: oczekiwano naglowka {';'.join(NAGLOWEK)}")
                continue
            if len(wiersz) != 4:
                raise ValueError(f"linia {linia}: oczekiwano 4 pol, jest {len(wiersz)}")
            plik, krazek, k, data = (p.strip() for p in wiersz)
            if not plik:
                raise ValueError(f"linia {linia}: pusta nazwa pliku")
            try:
                wynik.append(Wspolczynnik(plik, krazek or None, _liczba(k), _data(data)))
            except ValueError as e:
                raise ValueError(f"linia {linia}: {e}") from None
    return wynik
