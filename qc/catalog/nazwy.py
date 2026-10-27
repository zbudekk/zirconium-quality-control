"""Rozbior nazw folderow zlecen i plikow STL: kuweta, nazwisko, numer zeba (FDI)."""

import re
from dataclasses import dataclass
from pathlib import PurePath

# samodzielna liczba: bez cyfr i liter tuz obok (podkreslnik, spacja, kropka, lacznik = separator)
_LICZBA = re.compile(r"(?<![^\W_])\d+(?![^\W_])")
_PRYWATNE = re.compile(r"#\s*(\d+)")
_NAZWISKO = re.compile(r"[^\W\d_]+(?:-[^\W\d_]+)*")
_ZEBY = {10 * c + z for c in range(1, 5) for z in range(1, 9)}


@dataclass(frozen=True)
class Zlecenie:
    kuweta: str | None
    nazwisko: str | None
    nazwa: str
    prywatne: bool


def rozbierz(folder: str) -> Zlecenie:
    """Folder zlecenia -> kuweta (pierwsza samodzielna liczba 1-4 cyfr bez zer wiodacych), nazwisko."""
    prywatne = _PRYWATNE.search(folder)
    if prywatne:
        kuweta = "#" + prywatne.group(1)
    else:
        kuweta = next((str(int(m.group())) for m in _LICZBA.finditer(folder) if len(m.group()) <= 4), None)
    nazwisko = _NAZWISKO.search(folder)
    return Zlecenie(kuweta=kuweta, nazwisko=nazwisko.group() if nazwisko else None, nazwa=folder,
                    prywatne=prywatne is not None)


def znormalizuj(tekst: str) -> str:
    """Male litery, pojedyncze spacje, bez spacji na koncach, liczby bez zer wiodacych."""
    tekst = " ".join(tekst.lower().split())
    return re.sub(r"\d+", lambda m: str(int(m.group())), tekst)


def numer_zeba(plik: str) -> int | None:
    """Pierwszy numer FDI (11-18, 21-28, 31-38, 41-48) jako samodzielna liczba w nazwie pliku."""
    for m in _LICZBA.finditer(PurePath(plik).stem):
        if len(m.group()) == 2 and int(m.group()) in _ZEBY:
            return int(m.group())
    return None
