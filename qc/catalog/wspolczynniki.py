"""Wspolczynniki skali z CSV `plik;krazek;wspolczynnik;data` (plan B do czasu parsera raportow MillBox)."""

import csv
import io
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

NAGLOWEK = ["plik", "krazek", "wspolczynnik", "data"]
PODPOWIEDZ = "zapisz jako CSV UTF-8 (rozdzielany srednikami) z naglowkiem plik;krazek;wspolczynnik;data w 1. linii"


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


def _tekst(sciezka: Path) -> str:
    dane = sciezka.read_bytes()
    try:
        return dane.decode("utf-8-sig")
    except UnicodeDecodeError as e:
        linia = dane[:e.start].count(b"\n") + 1
        raise ValueError(f"linia {linia}: plik nie jest w UTF-8 ({PODPOWIEDZ})") from None


def wczytaj(sciezka_csv) -> list[Wspolczynnik]:
    """Wczytuje CSV (srednik, UTF-8, naglowek); bledny wiersz -> ValueError z numerem linii."""
    czytnik = csv.reader(io.StringIO(_tekst(Path(sciezka_csv)), newline=""), delimiter=";")
    wynik = []
    for wiersz in czytnik:
        linia = czytnik.line_num
        if linia == 1:
            if [p.strip().lower() for p in wiersz] != NAGLOWEK:
                raise ValueError(f"linia 1: brak naglowka ({PODPOWIEDZ})")
            continue
        if not any(p.strip() for p in wiersz):
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
