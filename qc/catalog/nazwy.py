"""Rozbior nazw folderow zlecen i plikow STL: kuweta, nazwisko, numer zeba (FDI)."""

import re
import unicodedata
from dataclasses import dataclass
from pathlib import PurePath

# samodzielna liczba: bez cyfr i liter tuz obok (podkreslnik, spacja, kropka, lacznik = separator)
_LICZBA = re.compile(r"(?<![^\W_])\d+(?![^\W_])")
# numer kuwety: jak wyzej, ale wolno mu przylegac z prawej do liter kodu ("1784PG"); litery przed
# cyframi ("PG1784") nadal wykluczaja liczbe
_KUWETA = re.compile(r"(?<![^\W_])\d+(?!\d)")
# granica liczba -> litery ("1784PG" -> "1784 PG")
_LICZBA_LITERY = re.compile(r"(?<=\d)(?=[^\W\d_])")
_PRYWATNE = re.compile(r"#\s*(\d+)")
_NAZWISKO = re.compile(r"[^\W\d_]+(?:-[^\W\d_]+)*")
_ZEBY = {10 * c + z for c in range(1, 5) for z in range(1, 9)}


def _nfc(tekst: str) -> str:
    """Postac NFC (OneDrive na Macu zapisuje litery z ogonkami jako znak + znak laczacy)."""
    return unicodedata.normalize("NFC", tekst)


@dataclass(frozen=True)
class Zlecenie:
    kuweta: str | None
    nazwisko: str | None
    nazwa: str
    prywatne: bool


def rozbierz(folder: str) -> Zlecenie:
    """Folder zlecenia -> kuweta (pierwsza samodzielna liczba 1-4 cyfr bez zer wiodacych, z prawej
    moze byc sklejona z kodem literowym: "Kowalski 1784PG" -> "1784"), nazwisko."""
    folder = _nfc(folder)
    prywatne = _PRYWATNE.search(folder)
    if prywatne:
        kuweta = "#" + prywatne.group(1)
    else:
        kuweta = next((str(int(m.group())) for m in _KUWETA.finditer(folder) if len(m.group()) <= 4), None)
    nazwisko = _NAZWISKO.search(folder)
    return Zlecenie(kuweta=kuweta, nazwisko=nazwisko.group() if nazwisko else None, nazwa=folder,
                    prywatne=prywatne is not None)


def znormalizuj(tekst: str) -> str:
    """Male litery, pojedyncze spacje, bez spacji na koncach, liczby bez zer wiodacych, spacja miedzy
    liczba a sklejonymi z nia z prawej literami ("1784PG" i "1784 PG" -> "1784 pg")."""
    tekst = " ".join(_LICZBA_LITERY.sub(" ", _nfc(tekst)).lower().split())
    return re.sub(r"\d+", lambda m: str(int(m.group())), tekst)


def numer_zeba(plik: str) -> int | None:
    """Pierwszy numer FDI (11-18, 21-28, 31-38, 41-48) jako samodzielna liczba w nazwie pliku."""
    for m in _LICZBA.finditer(PurePath(_nfc(plik)).stem):
        if len(m.group()) == 2 and int(m.group()) in _ZEBY:
            return int(m.group())
    return None
