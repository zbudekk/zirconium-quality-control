"""nazwy - nazwa folderu zlecenia -> numer kuwety; normalizacja nazw; zeby i typ pracy z nazwy pliku STL (E3-A4).

Regula kuwety (plan wdrozenia v2, "Dane i integracje"; przeniesione z wczesniejszej linii ``qc/catalog/nazwy.py``, H):
numer kuwety to pierwsza samodzielna liczba 1-4 cyfr w nazwie folderu, zera wiodace normalizowane (3 = 03 = 003 -> "3").
Liczba moze byc z prawej sklejona z kodem literowym ("Nazwisko 1784PG" -> "1784"), ale nie z cyframi ("12345" -> nie
kuweta) ani z literami z lewej ("PG1784" -> nie kuweta). Kropka i podkreslnik sa separatorami ("J.3263", "_88_").
Daty w nazwie (2026-11-16, 16.11.2026, 2026_11_16) nie sa kuweta. "#1234" = zlecenie prywatne, kuweta "#1234" (numer
zlecenia z maila - cyfry bez zmian). Nazwy porownywane sa w postaci Unicode NFC (OneDrive zapisuje czasem litery
z ogonkami jako litera + znak laczacy, NFD).

DANE OSOBOWE: nazwy folderow i plikow zawieraja nazwiska. Funkcje tego modulu nie wyciagaja nazwiska (zwracaja tylko kuwete,
postac znormalizowana do porownan z kolumna H Excela, zeby i typ); wynik ``znormalizuj`` i ``klucz_pliku`` to nadal nazwa
- wolno go trzymac tylko w kolumnach z nazwami (``baza.KOLUMNY_Z_NAZWAMI``). Tylko biblioteka standardowa (typ i zeby
z nazwy exocad bierze ``katalog.typ_i_zeby_z_nazwy``, importowany dopiero przy wywolaniu). Opis: ``opisy_modulow/pula.md``.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import PurePath

# samodzielna liczba: bez liter i cyfr tuz obok (spacja, kropka, podkreslnik, lacznik = separator)
_LICZBA = re.compile(r"(?<![^\W_])\d+(?![^\W_])")
# kandydat na numer kuwety: jak wyzej, ale z prawej wolno przylegac literom kodu ("1784PG")
_KUWETA = re.compile(r"(?<![^\W_])\d+(?!\d)")
# granica liczba -> litery ("1784PG" -> "1784 PG") w postaci do porownan
_LICZBA_LITERY = re.compile(r"(?<=\d)(?=[^\W\d_])")
_PRYWATNE = re.compile(r"#\s*(\d+)")
# daty w nazwie folderu: RRRR-MM-DD (tez z "_" albo "."), DD.MM.RRRR, DD-MM-RR
_DATA = re.compile(r"(?<!\d)(?:\d{4}[-_.]\d{1,2}[-_.]\d{1,2}|\d{1,2}[-_.]\d{1,2}[-_.]\d{2,4})(?!\d)")
_ZEBY_FDI = {f"{c}{z}" for c in range(1, 5) for z in range(1, 9)}
TYP_NIEZNANY = "nieznany"


def nfc(tekst: str) -> str:
    """Postac NFC (litera z ogonkiem jako jeden znak)."""
    return unicodedata.normalize("NFC", tekst)


@dataclass(frozen=True)
class Zlecenie:
    """Wynik rozbioru nazwy folderu zlecenia: kuweta, czy prywatne, postac do porownan (bez wydzielonego nazwiska)."""
    kuweta: str | None
    prywatne: bool
    folder_norm: str


def kuweta(folder: str) -> str | None:
    """Numer kuwety z nazwy folderu (tekst: "3263", "41", "#1234") albo None."""
    tekst = nfc(folder)
    prywatne = _PRYWATNE.search(tekst)
    if prywatne:
        return "#" + prywatne.group(1)
    tekst = _DATA.sub(" ", tekst)
    for m in _KUWETA.finditer(tekst):
        if len(m.group()) <= 4:
            return str(int(m.group()))
    return None


def znormalizuj(tekst: str) -> str:
    """Postac do porownan (kolumna H Excela): NFC, male litery, pojedyncze spacje, liczby bez zer wiodacych, spacja miedzy
    liczba a sklejonymi z nia z prawej literami ("Nazwisko 1784PG" i "nazwisko 1784 pg" -> "nazwisko 1784 pg")."""
    tekst = " ".join(_LICZBA_LITERY.sub(" ", nfc(tekst)).lower().split())
    return re.sub(r"\d+", lambda m: str(int(m.group())), tekst)


def rozbierz(folder: str) -> Zlecenie:
    """Folder zlecenia -> ``Zlecenie(kuweta, prywatne, folder_norm)``."""
    k = kuweta(folder)
    return Zlecenie(kuweta=k, prywatne=k is not None and k.startswith("#"), folder_norm=znormalizuj(folder))


def numer_zeba(plik: str) -> str | None:
    """Pierwszy numer FDI (11-18, 21-28, 31-38, 41-48) jako samodzielna liczba w nazwie pliku (bez rozszerzenia)."""
    for m in _LICZBA.finditer(PurePath(nfc(plik)).stem):
        if m.group() in _ZEBY_FDI:
            return m.group()
    return None


def zeby_i_typ(plik: str) -> tuple[str | None, str]:
    """(zeby "24-25-26" albo None, typ pracy) z nazwy pliku STL.

    Nazwa exocad (``...-24-25-26-bridge_cad.stl``): zeby i typ jak w ``katalog`` (korona, most, waxup, bez_lacznika);
    inna nazwa: typ "nieznany", zab = pierwszy samodzielny numer FDI ("zab 46.stl" -> "46").
    """
    from . import katalog as K  # ciezkie zaleznosci katalogu (numpy, trimesh) dopiero tutaj

    typ, zeby = K.typ_i_zeby_z_nazwy(nfc(PurePath(plik).name))
    if zeby:
        return "-".join(zeby), typ
    return numer_zeba(plik), TYP_NIEZNANY


def klucz_pliku(nazwa: str) -> str:
    """Postac nazwy pliku (albo sciezki "folder/plik") do porownan: NFC, ``\\`` -> ``/``, bez ``/`` i spacji na koncach,
    bez wielkosci liter. Uzywana do laczenia wierszy CSV / raportu z plikami indeksu."""
    return "/".join(c.strip() for c in nfc(nazwa).replace("\\", "/").strip().strip("/").split("/")).casefold()


def normalizuj_krazek(krazek: str | None) -> str | None:
    """Oznaczenie krazka: bez spacji na koncach, pojedyncze spacje, wielkie litery ("k-1101" -> "K-1101"); puste -> None."""
    if krazek is None:
        return None
    k = " ".join(nfc(str(krazek)).split()).upper()
    return k or None
