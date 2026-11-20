"""samokontrola - sprawdzenie, czy program "Stanowisko" ma na tym komputerze wszystko, czego potrzebuje (paczka E3-A11s).

Umowa wywolania (styk z instalatorem A11i i instrukcjami A11d - nie zmieniac bez uzgodnienia)::

    python -m stanowisko.samokontrola [--ustawienia PLIK] [--sumy PLIK] [--json] [--bez-sieci]

* wyjscie tekstowe: jeden wiersz na sprawdzenie - ``OK <kod>: <opis>``, ``OSTRZEZENIE <kod>: <opis>; <co zrobic>`` albo
  ``BLAD <kod>: <opis>; <co zrobic>`` (opis nie zawiera srednika: pierwszy "; " w wierszu oddziela opis od rady); ostatni
  wiersz ``SAMOKONTROLA: ZIELONA (ok N, ostrzezenia M)`` albo ``SAMOKONTROLA: CZERWONA (ok N, ostrzezenia M, bledy K)``;
  ``--json``: to samo jako jeden obiekt JSON (``Wynik.do_slownika``);
* kod wyjscia: 0 = brak bledow (takze z ostrzezeniami), 1 = co najmniej jeden BLAD, 2 = samokontroli nie dalo sie wykonac
  (brak albo blad pliku ustawien: wiersz ``BLAD ustawienia: ...; ...`` i ``SAMOKONTROLA: NIEWYKONANA (...)``, bez sladu wyjatku);
* ``--sumy PLIK``: plik w formacie ``sha256sum`` (``<64 znaki hex>  <sciezka wzgledna od katalogu programu>``); bez opcji
  sprawdzany jest ``SUMY_PROGRAMU.sha256`` z katalogu programu, a gdy go nie ma - OSTRZEZENIE "kopia robocza bez pliku sum";
* jako funkcja: ``wykonaj(ust, ...) -> Wynik`` (``Wynik.sprawdzenia``: lista ``Sprawdzenie`` z polami kod, poziom, opis, rada).

Samokontrola niczego nie naprawia i nie zmienia: baze otwiera tylko do odczytu (nie zaklada, nie migruje), nie tworzy
folderow, do ramek wysyla wylacznie ``GET /stan`` bez identyfikatora laptopa (ramka nie zapisuje kontaktu), do Excela
podlacza sie tak jak ``excel_com`` (Excel juz uruchomiony) i nie otwiera arkusza. Jedyny zapis: plik probny w ISTNIEJACYM
folderze danych, usuwany od razu po probie.

Tylko biblioteka standardowa i moduly programu. Ciezkie moduly (PySide6, Open3D i reszta listy ``aplikacja.MODULY_DLL``)
sa importowane wylacznie w sprawdzeniu ``moduly`` - blad importu jest wynikiem BLAD, a nie awaria samokontroli.

Dane osobowe: w wyjsciu sa tylko sciezki wpisane w ``[sciezki]`` pliku ustawien (foldery glowne) i liczniki; nazwy
podfolderow i plikow zlecen, nazwy osob z ``[sesja] operatorzy`` ani klucz ramek nie sa wypisywane (z bledow systemu
trafia do wyjscia sam typ wyjatku). Opis, tabela sprawdzen i poziomow: ``opisy_modulow/samokontrola.md``.
"""
from __future__ import annotations

import argparse
import dataclasses
import hashlib
import importlib.metadata
import json
import os
import re
import shutil
import sqlite3
import sys
import tempfile
import threading
import time
import tomllib
import warnings
from pathlib import Path
from typing import Any, Callable, Iterator

from . import baza as B
from . import ustawienia as UST

OK, OSTRZEZENIE, BLAD = "OK", "OSTRZEZENIE", "BLAD"
ZIELONA, CZERWONA, NIEWYKONANA = "ZIELONA", "CZERWONA", "NIEWYKONANA"
KOD_BEZ_BLEDOW, KOD_BLEDY, KOD_NIEWYKONANA = 0, 1, 2  # kody wyjscia (umowa)

PLIK_SUM = "SUMY_PROGRAMU.sha256"  # w katalogu programu wersji zainstalowanej z paczki wydania (umowa z A11i)
PLIK_WYMAGAN = "requirements.txt"
PLIK_PULI = "stanowisko_pula.json"  # = aplikacja.PLIK_PULI (obok bazy: folder puli wybrany w programie); rownosc pilnuje test
PLIK_WSPOLCZYNNIKOW = "wspolczynniki.csv"  # = aplikacja.PLIK_WSPOLCZYNNIKOW (w [sciezki] folder_millbox); rownosc pilnuje test
NAGLOWEK_KLUCZA = "X-Ramka-Klucz"  # = indicate.NAGLOWEK_KLUCZA (ramka/README.md, "Protokol v1"); rownosc pilnuje test

WERSJA_PYTHONA = (3, 12)
# Pakiety z requirements.txt: pytest nie jest potrzebny na stanowisku (brak i inna wersja nie sa zglaszane).
PAKIETY_POZA_STANOWISKIEM = ("pytest",)
# Pakiety, bez ktorych program pracuje (brak = OSTRZEZENIE): pywin32 - tylko polaczenie z Excelem (aplikacja.zaladuj_moduly_dll:
# "brak pakietu, np. pywin32 poza laptopem stanowiska - nie blad programu"); rtree - tylko narzedzia pomiarowe (trimesh.proximity
# w narzedzia/metryki_krawedz.py); beautifulsoup4 i pypdf - raporty MillBox, ktorych program jeszcze nie czyta (zaden import w stanowisko/).
PAKIETY_DODATKOWE = {"pywin32": "polaczenie z Excelem", "rtree": "narzedzia pomiarowe", "beautifulsoup4": "raporty MillBox",
                     "pypdf": "raporty MillBox w PDF"}
# Pakiety potrzebne w pracy (brak = BLAD) - lista awaryjna, gdy w katalogu programu nie ma requirements.txt; test pilnuje,
# ze jest rowna requirements.txt bez dwoch grup powyzej.
PAKIETY_W_PRACY = ("numpy", "scipy", "trimesh", "pillow", "open3d", "PySide6", "watchdog")

# Moduly ladowane w sprawdzeniu "moduly" w kolejnosci startu programu (aplikacja.main): najpierw Qt w calosci, potem
# aplikacja.MODULY_DLL i MODULY_DLL_PULI (Open3D i scipy laduje tez proces analizy - potrzebne zawsze), na koncu lancuch analizy.
MODULY_QT = ("PySide6.QtCore", "PySide6.QtGui", "PySide6.QtWidgets")
MODUL_ANALIZY = "stanowisko.porownaj"  # = modul z silnik.FUNKCJA_ANALIZY (plate, match, inspect, krawedz)
MODULY_NIEOBOWIAZKOWE = ("pythoncom", "win32com.client")  # pywin32: bez nich nie dziala tylko Excel (OSTRZEZENIE)

# Wolne miejsce na dysku folderu danych. W folderze danych rosna: pamiec puli (ok. 5 MB na wpis, pula 400 wpisow = ok. 2 GB),
# podglady i wyniki skanow, logi (5 x 2 MB), baza i jej kopia przed migracja. Ponizej 1 GB zapis wyniku skanu albo kopia bazy
# moze sie nie udac (program pokazalby "nie zapisano") - BLAD; ponizej 10 GB miejsce skonczy sie w ciagu tygodni - OSTRZEZENIE.
MIEJSCE_BLAD_GB = 1.0
MIEJSCE_OSTRZEZENIE_GB = 10.0

LIMIT_RAMKI_S = 3.0  # najdluzsza proba polaczenia z jedna ramka (obie proby rownolegle); nazwa .local bywa rozwiazywana kilka sekund
LIMIT_FOLDERU_S = 5.0  # folder pracy, ktory nie odpowiada tyle sekund (udzial sieciowy), jest zglaszany jako niedostepny
LIMIT_LICZENIA_S = 5.0  # liczenie plikow STL puli: po tylu sekundach wynik "co najmniej N"
# PRAGMA quick_check przerywany po tylu sekundach (duza baza) - OSTRZEZENIE "nie sprawdzono". Krocej niz program czeka na
# baze zajeta (baza.CZEKAJ_NA_BLOKADE_MS = 5 s; test): samokontrola uruchomiona obok pracujacego programu nie wywola w nim "nie zapisano".
LIMIT_QUICK_CHECK_S = 4.0
KROK_QUICK_CHECK = 20000  # co tyle krokow maszyny SQLite sprawdzany jest limit czasu
CZEKAJ_NA_BAZE_MS = 1000  # tyle czekania na baze zajeta przez inny program, potem OSTRZEZENIE "zajeta"
MAKS_ROZNIC = 10  # tyle pierwszych roznic sum jest wypisywanych
NAZWY_SYNCHRONIZOWANE = ("onedrive", "sharepoint")  # czesc sciezki zaczynajaca sie od "OneDrive" albo zawierajaca "SharePoint"
# [sciezki]: pliki i foldery danych programu, ktore nie moga lezec w folderze synchronizowanym (baza i log Excela zawieraja
# nazwy folderow zlecen; plik bazy synchronizowany w trakcie pracy ulega uszkodzeniu)
KLUCZE_DANYCH = ("baza", "log_excel", "wyniki", "podglady", "pula_cache", "logi", "kalibracja_ramek")
ROZSZERZENIA_KODU = (".py", ".pyw", ".pyd", ".pth", ".dll")  # plik nadmiarowy w katalogu glownym programu: tylko taki, ktory Python zaladuje
RADA_PACZKA = "zainstaluj program ponownie z paczki wydania"
RADA_PROGRAMISTA = "zglos ten wiersz osobie, ktora instaluje program"


class BladSum(ValueError):
    """Niepoprawny plik sum (komunikat bez sciezek spoza pliku)."""


# ----------------------------------------------------------------------------- wynik

@dataclasses.dataclass(frozen=True)
class Sprawdzenie:
    """Wynik jednego sprawdzenia: ``kod`` (staly identyfikator, male litery), ``poziom`` (OK / OSTRZEZENIE / BLAD), ``opis``
    (jedna linia bez srednika), ``rada`` (co zrobic; pusta dokladnie wtedy, gdy poziom to OK)."""

    kod: str
    poziom: str
    opis: str
    rada: str = ""

    def wiersz(self) -> str:
        return f"{self.poziom} {self.kod}: {self.opis}" + (f"; {self.rada}" if self.rada else "")

    def do_slownika(self) -> dict:
        return dataclasses.asdict(self)


def _linia(tekst: Any) -> str:
    return " ".join(str(tekst).split())


def _sprawdzenie(kod: str, poziom: str, opis: str, rada: str = "") -> Sprawdzenie:
    opis = _linia(opis).replace(";", ",") or "(brak opisu)"
    rada = "" if poziom == OK else (_linia(rada) or RADA_PROGRAMISTA)
    return Sprawdzenie(kod, poziom, opis, rada)


def _ok(kod: str, opis: str) -> Sprawdzenie:
    return _sprawdzenie(kod, OK, opis)


def _ostrzezenie(kod: str, opis: str, rada: str) -> Sprawdzenie:
    return _sprawdzenie(kod, OSTRZEZENIE, opis, rada)


def _blad(kod: str, opis: str, rada: str) -> Sprawdzenie:
    return _sprawdzenie(kod, BLAD, opis, rada)


@dataclasses.dataclass
class Wynik:
    """Wynik samokontroli: ``sprawdzenia`` w stalej kolejnosci (``KODY``) i czas wykonania. Mozna po nim iterowac."""

    sprawdzenia: list
    czas_s: float = 0.0
    stan: str | None = None  # NIEWYKONANA przy kodzie 2; inaczej wynika z liczby bledow

    def __iter__(self) -> Iterator[Sprawdzenie]:
        return iter(self.sprawdzenia)

    def __len__(self) -> int:
        return len(self.sprawdzenia)

    def sprawdzenie(self, kod: str) -> Sprawdzenie:
        for s in self.sprawdzenia:
            if s.kod == kod:
                return s
        raise KeyError(kod)

    def _ile(self, poziom: str) -> int:
        return sum(1 for s in self.sprawdzenia if s.poziom == poziom)

    @property
    def ok(self) -> int:
        return self._ile(OK)

    @property
    def ostrzezenia(self) -> int:
        return self._ile(OSTRZEZENIE)

    @property
    def bledy(self) -> int:
        return self._ile(BLAD)

    @property
    def zielona(self) -> bool:
        return self.stan is None and self.bledy == 0

    @property
    def kod_wyjscia(self) -> int:
        if self.stan == NIEWYKONANA:
            return KOD_NIEWYKONANA
        return KOD_BEZ_BLEDOW if self.bledy == 0 else KOD_BLEDY

    def podsumowanie(self) -> str:
        if self.stan == NIEWYKONANA:
            return f"SAMOKONTROLA: {NIEWYKONANA} (blad ustawien - zadnego sprawdzenia nie wykonano)"
        if self.bledy == 0:
            return f"SAMOKONTROLA: {ZIELONA} (ok {self.ok}, ostrzezenia {self.ostrzezenia})"
        return f"SAMOKONTROLA: {CZERWONA} (ok {self.ok}, ostrzezenia {self.ostrzezenia}, bledy {self.bledy})"

    def wiersze(self) -> list[str]:
        return [s.wiersz() for s in self.sprawdzenia] + [self.podsumowanie()]

    def tekst(self) -> str:
        return "\n".join(self.wiersze())

    def do_slownika(self) -> dict:
        stan = self.stan or (ZIELONA if self.bledy == 0 else CZERWONA)
        return {"samokontrola": stan, "kod_wyjscia": self.kod_wyjscia, "ok": self.ok, "ostrzezenia": self.ostrzezenia,
                "bledy": self.bledy, "podsumowanie": self.podsumowanie(), "czas_s": round(self.czas_s, 1),
                "sprawdzenia": [s.do_slownika() for s in self.sprawdzenia]}


# ----------------------------------------------------------------------------- pomocnicze

@dataclasses.dataclass
class _Kontekst:
    ust: dict
    korzen: Path
    plik_ustawien: Path | None
    sumy: Path | None
    bez_sieci: bool
    limit_ramki_s: float
    foldery: dict = dataclasses.field(default_factory=dict)  # klucz [sciezki] -> "ok" / "brak" / "nie_folder" / "blad" / "limit"
    baza_jest: bool = False  # plik bazy istnieje i nie jest pusty
    baza_czytelna: bool = False  # plik bazy dal sie otworzyc do odczytu (indeks puli mozna policzyc)
    baza_zajeta: bool = False

    def sciezka(self, klucz: str) -> Path:
        """Sciezka z ``[sciezki]``; wzgledna liczona od katalogu programu (jak ``baza.sciezka_z_ustawien``)."""
        return self.wzgledna(self.ust["sciezki"][klucz])

    def wzgledna(self, wartosc: str) -> Path:
        p = Path(wartosc)
        return p if p.is_absolute() else self.korzen / p

    def folder_danych(self) -> Path:
        """Folder danych programu = folder pliku bazy (``Aplikacja.katalog_danych``)."""
        return self.sciezka("baza").parent


def odmiana(n: int, jeden: str, kilka: str, wiele: str) -> str:
    """Polska odmiana po liczbie: 1 plik, 2 pliki, 5 plikow."""
    if n == 1:
        return jeden
    return kilka if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14) else wiele


# polskie litery, myslniki, wielokropek i cudzyslowy z komunikatow modulu ustawienia -> ASCII
_OGONKI = str.maketrans("\u0105\u0107\u0119\u0142\u0144\u00f3\u015b\u017a\u017c\u0104\u0106\u0118\u0141\u0143\u00d3\u015a\u0179\u017b\u2014\u2013\u2026\u201e\u201d",
                        "acelnoszzACELNOSZZ--.\"\"")


def _bez_ogonkow(tekst: str) -> str:
    return tekst.translate(_OGONKI)


def _z_limitem(zadania: dict, limit_s: float) -> dict:
    """Wykonuje funkcje rownolegle w watkach pomocniczych i czeka lacznie najwyzej ``limit_s``. Zwraca klucz ->
    ("wynik", wartosc) / ("blad", wyjatek) / ("limit", None). Watek, ktory nie zdazyl (folder sieciowy bez odpowiedzi,
    nazwa hosta bez odpowiedzi), zostaje w tle i konczy sie razem z procesem."""
    wyniki: dict = {}

    def uruchom(klucz: str, funkcja: Callable[[], Any]) -> None:
        try:
            wyniki[klucz] = ("wynik", funkcja())
        except Exception as e:  # noqa: BLE001 - kazdy blad jest wynikiem sprawdzenia
            wyniki[klucz] = ("blad", e)

    watki = []
    for klucz, funkcja in zadania.items():
        w = threading.Thread(target=uruchom, args=(klucz, funkcja), daemon=True, name=f"samokontrola-{klucz}")
        w.start()
        watki.append(w)
    koniec = time.monotonic() + limit_s
    for w in watki:
        w.join(max(0.0, koniec - time.monotonic()))
    return {klucz: wyniki.get(klucz, ("limit", None)) for klucz in zadania}


def _wewnatrz(sciezka: str | Path, folder: str | Path) -> bool:
    a, b = (os.path.normcase(os.path.abspath(str(x))) for x in (sciezka, folder))
    return a == b or a.startswith(b.rstrip("\\/") + os.sep)


def _istniejacy_przodek(p: Path) -> Path:
    p = Path(os.path.abspath(p))
    while not p.exists() and p.parent != p:
        p = p.parent
    return p


# ----------------------------------------------------------------------------- 1. Python i pakiety

def _wersja_pythona() -> tuple:
    return tuple(sys.version_info[:3])


def _python(k: _Kontekst) -> list:
    w = _wersja_pythona()
    napis = ".".join(str(x) for x in w)
    if tuple(w[:2]) == WERSJA_PYTHONA:
        return [_ok("python", f"Python {napis}")]
    return [_blad("python", f"program uruchomiony Pythonem {napis}, a jest sprawdzony tylko z Pythonem 3.12",
                  "zainstaluj Python 3.12 i " + RADA_PACZKA)]


_WZOR_WYMAGANIA = re.compile(r"\s*([A-Za-z0-9][A-Za-z0-9._-]*)\s*==\s*([^\s;#]+)\s*(?:;([^#]*))?(?:#.*)?")
_WZOR_ZNACZNIKA = re.compile(r"""\s*sys_platform\s*(==|!=)\s*["']([^"']+)["']\s*""")


def czytaj_wymagania(plik: str | Path) -> list:
    """Pakiety przypiete w ``requirements.txt`` dla tego systemu: lista (nazwa, wersja). Wiersze bez ``==`` sa pomijane;
    znacznik ``sys_platform == "..."`` jest stosowany, inne znaczniki przyjmowane jako spelnione."""
    wynik = []
    for linia in Path(plik).read_text(encoding="utf-8").splitlines():
        m = _WZOR_WYMAGANIA.fullmatch(linia)
        if m is None:
            continue
        znacznik = _WZOR_ZNACZNIKA.fullmatch(m.group(3) or "")
        if znacznik is not None and (sys.platform == znacznik.group(2)) != (znacznik.group(1) == "=="):
            continue
        wynik.append((m.group(1), m.group(2)))
    return wynik


def _wersja_pakietu(nazwa: str) -> str | None:
    """Wersja zainstalowanego pakietu z jego metadanych (bez importu pakietu) albo None, gdy pakietu nie ma."""
    try:
        return importlib.metadata.version(nazwa)
    except Exception:  # noqa: BLE001 - brak pakietu albo uszkodzone metadane = "nie ma"
        return None


def _nazwa_pakietu(nazwa: str) -> str:
    return re.sub(r"[-_.]+", "-", nazwa).lower()


def _pakiety(k: _Kontekst) -> list:
    try:
        wymagania = czytaj_wymagania(k.korzen / PLIK_WYMAGAN)
    except (OSError, UnicodeDecodeError):
        wymagania = None
    poza = {_nazwa_pakietu(n) for n in PAKIETY_POZA_STANOWISKIEM}
    dodatkowe = {_nazwa_pakietu(n): po_co for n, po_co in PAKIETY_DODATKOWE.items()}
    lista = [(n, w) for n, w in wymagania or [] if _nazwa_pakietu(n) not in poza]
    znane = {_nazwa_pakietu(n) for n, _ in lista}
    lista += [(n, None) for n in PAKIETY_W_PRACY if _nazwa_pakietu(n) not in znane]  # potrzebne w pracy sa sprawdzane zawsze
    zgodne, rozne, brak_potrzebnych, brak_dodatkowych = 0, [], [], []
    for nazwa, wymagana in lista:
        jest = _wersja_pakietu(nazwa)
        if jest is None:
            if _nazwa_pakietu(nazwa) in dodatkowe:
                brak_dodatkowych.append(f"brak {nazwa} ({dodatkowe[_nazwa_pakietu(nazwa)]})")
            else:
                brak_potrzebnych.append(f"brak {nazwa}")
        elif wymagana is None or jest == wymagana:
            zgodne += 1
        else:
            rozne.append(f"{nazwa} {jest} (wymagana {wymagana})")
    if wymagania:
        opis = f"wersje pakietow zgodne {zgodne} z {len(lista)} z {PLIK_WYMAGAN}"
    else:
        opis = f"brak pliku {PLIK_WYMAGAN} w katalogu programu - wersji nie porownano, pakiety potrzebne w pracy: obecne {zgodne} z {len(lista)}"
    uwagi = brak_potrzebnych + brak_dodatkowych + rozne
    if uwagi:
        opis += " - " + ", ".join(uwagi)
    if brak_potrzebnych:
        return [_blad("pakiety", opis, RADA_PACZKA + " (pakiety instaluje instalator, bez internetu)")]
    if uwagi or not wymagania:
        return [_ostrzezenie("pakiety", opis, "program dziala, ale nie w zestawie pakietow, z ktorym byl sprawdzany - "
                             + RADA_PACZKA + ", gdy cos dziala inaczej niz zwykle")]
    return [_ok("pakiety", opis + f" (bez {', '.join(PAKIETY_POZA_STANOWISKIEM)})")]


# ----------------------------------------------------------------------------- 2. moduly z DLL

def _zaladuj(moduly: tuple) -> dict:
    """Importuje moduly ta sama funkcja, ktorej program uzywa przy starcie; zwraca nazwa -> True albo opis bledu."""
    from . import aplikacja as A  # noqa: PLC0415 - modul okna bez Qt na poziomie modulu (tylko biblioteka standardowa)

    return A.zaladuj_moduly_dll(tuple(moduly))


def _moduly(k: _Kontekst) -> list:
    rada = RADA_PACZKA + ", gdy blad wraca - " + RADA_PROGRAMISTA
    try:
        from . import aplikacja as A  # noqa: PLC0415

        moduly = tuple(dict.fromkeys(MODULY_QT + tuple(A.MODULY_DLL) + tuple(A.MODULY_DLL_PULI) + (MODUL_ANALIZY,)))
        wynik = _zaladuj(moduly)
    except Exception as e:  # noqa: BLE001 - blad importu to wynik BLAD, nie awaria samokontroli
        return [_blad("moduly", f"modulow programu nie da sie zaladowac ({type(e).__name__}: {B.bez_sciezek(str(e))[:120]})", rada)]
    zle = {n: w for n, w in wynik.items() if w is not True}
    opis = f"moduly programu z bibliotekami DLL: zaladowane {len(wynik) - len(zle)} z {len(wynik)}"
    if not zle:
        return [_ok("moduly", opis + " (Qt, Open3D, scipy, trimesh, lancuch analizy, ramki, Excel)")]
    opis += " - nie laduja sie: " + ", ".join(f"{n} ({w})" for n, w in zle.items())
    if set(zle) <= set(MODULY_NIEOBOWIAZKOWE):
        return [_ostrzezenie("moduly", opis, "bez pywin32 nie dziala tylko polaczenie z Excelem - " + RADA_PACZKA
                             + ", jesli Excel ma byc odhaczany przez program")]
    return [_blad("moduly", opis, rada)]


# ----------------------------------------------------------------------------- 3. ustawienia

def klucze_domyslne(plik: str | Path) -> list:
    """Klucze, ktorych nie ma w pliku ustawien i ktore program uzupelnia wartoscia domyslna: ``[sekcja] klucz``."""
    with open(plik, "rb") as f:
        d = tomllib.load(f)
    dopisane = list(UST.uzupelnij_domyslne(d))
    if isinstance(d.get("plytki"), dict):
        dopisane += [f"[plytki] {n}" for n in UST.uzupelnij_uklady_wbudowane(d)]
    return dopisane


def _ustawienia(k: _Kontekst) -> list:
    if k.plik_ustawien is None:
        return [_ok("ustawienia", "ustawienia przekazane przez program sa wczytane i poprawne (plik nie byl czytany ponownie)")]
    try:
        dopisane = klucze_domyslne(k.plik_ustawien)
    except (OSError, ValueError):
        return [_ok("ustawienia", f"plik ustawien wczytany i poprawny: {k.plik_ustawien} (listy kluczy domyslnych nie ustalono)")]
    n = len(dopisane)
    opis = f"plik ustawien wczytany i poprawny: {k.plik_ustawien} - {n} {odmiana(n, 'klucz', 'klucze', 'kluczy')} z wartoscia domyslna"
    return [_ok("ustawienia", opis + (" (" + ", ".join(dopisane) + ")" if dopisane else ""))]


def _operatorzy(k: _Kontekst) -> list:
    n = len(k.ust["sesja"]["operatorzy"])
    if n == 0:
        return [_ostrzezenie("operatorzy", "lista osob jest pusta - program przyjmuje skany, ale nie zapisuje decyzji Ukruszona / OK",
                             "wpisz osoby w pliku ustawien: [sesja] operatorzy = [\"...\", \"...\"]")]
    return [_ok("operatorzy", f"osoby do wyboru na poczatku zmiany: {n}")]


# ----------------------------------------------------------------------------- 4. foldery pracy

# kod, klucz w [sciezki], poziom braku, nazwa dla czlowieka, skutek braku. Uzasadnienie poziomow: opisy_modulow/samokontrola.md.
FOLDERY_PRACY = (
    ("folder_skanera", "folder_eksportu_skanera", BLAD, "eksportu skanera", "zaden skan nie trafi do programu"),
    ("folder_cyrkon", "folder_cyrkon", BLAD, "projektow Cyrkon", "pula projektow jest pusta i skany czekaja bez wyniku"),
    ("folder_prywatne", "folder_prywatne", OSTRZEZENIE, "projektow Prywatne", "prace prywatne nie wejda do puli i zostana szare"),
    ("folder_millbox", "folder_millbox", BLAD, "MillBox", f"bez pliku {PLIK_WSPOLCZYNNIKOW} pula wieczorna nie dostaje nowych prac i skany wieczorne czekaja"),
)
# Foldery czytane tylko przy puli per praca ([silnik] pula_wpisow = true): przy pula_wpisow = false ich brak niczego nie zatrzymuje (OSTRZEZENIE).
FOLDERY_PULI_WPISOW = ("folder_prywatne", "folder_millbox")
NIEUZYWANY = "przy pula_wpisow = false program z niego nie korzysta (bedzie potrzebny po wlaczeniu puli per praca)"


def _czytaj_folder(folder: str | Path) -> str:
    """"ok" (istnieje i daje sie czytac), "brak" albo "nie_folder"; blad odczytu = wyjatek ``OSError``."""
    p = Path(folder)
    if not p.exists():
        return "brak"
    if not p.is_dir():
        return "nie_folder"
    with os.scandir(p) as wpisy:
        next(wpisy, None)
    return "ok"


def _foldery(k: _Kontekst) -> list:
    zadania = {}
    for _, klucz, *_reszta in FOLDERY_PRACY:
        if k.ust["sciezki"][klucz].strip():
            zadania[klucz] = (lambda p=k.sciezka(klucz): _czytaj_folder(p))
    stany = _z_limitem(zadania, LIMIT_FOLDERU_S)
    wynik = []
    for kod, klucz, poziom, nazwa, skutek in FOLDERY_PRACY:
        if klucz in FOLDERY_PULI_WPISOW and not k.ust["silnik"].get("pula_wpisow"):
            poziom, skutek = OSTRZEZENIE, NIEUZYWANY
        wartosc = k.ust["sciezki"][klucz]
        rodzaj, dane = stany.get(klucz, ("wynik", "pusty"))
        stan = dane if rodzaj == "wynik" else rodzaj
        k.foldery[klucz] = stan
        if stan == "ok":
            wynik.append(_ok(kod, f"folder {nazwa} istnieje i daje sie czytac: {wartosc}"))
            continue
        opis = {"pusty": f"folder {nazwa} nie jest wpisany w ustawieniach",
                "brak": f"brak folderu {nazwa}: {wartosc}",
                "nie_folder": f"sciezka folderu {nazwa} nie jest folderem: {wartosc}",
                "limit": f"folder {nazwa} nie odpowiada w {LIMIT_FOLDERU_S:g} s: {wartosc}",
                "blad": f"folderu {nazwa} nie da sie czytac ({type(dane).__name__}): {wartosc}"}[stan]
        rada = f"utworz albo podlacz ten folder, albo popraw [sciezki] {klucz} w pliku ustawien"
        wynik.append(_sprawdzenie(kod, poziom, f"{opis} - {skutek}", rada))
    return wynik


# ----------------------------------------------------------------------------- 5. folder danych

def _proba_zapisu(folder: Path) -> None:
    """Zapisuje i usuwa plik probny w ``folder`` (jedyny zapis samokontroli); blad = wyjatek ``OSError``."""
    uchwyt, nazwa = tempfile.mkstemp(prefix="samokontrola_", suffix=".tmp", dir=folder)
    try:
        os.write(uchwyt, b"samokontrola")
    finally:
        os.close(uchwyt)
        os.unlink(nazwa)


def _wolne_miejsce(folder: Path) -> int:
    return shutil.disk_usage(folder).free


def _dane_folder(k: _Kontekst) -> list:
    folder = k.folder_danych()
    rada = "nadaj prawo zapisu do folderu danych albo popraw [sciezki] baza w pliku ustawien"
    if folder.is_dir():
        try:
            _proba_zapisu(folder)
        except OSError as e:
            return [_blad("dane_folder", f"w folderze danych nie udal sie zapis pliku probnego ({type(e).__name__}): {folder}", rada)]
        return [_ok("dane_folder", f"folder danych istnieje, zapis mozliwy: {folder}")]
    przodek = _istniejacy_przodek(folder)
    if folder.exists() or not przodek.is_dir() or not os.access(przodek, os.W_OK):
        return [_blad("dane_folder", f"folderu danych nie da sie utworzyc (na sciezce lezy plik albo brak prawa zapisu): {folder}", rada)]
    return [_ostrzezenie("dane_folder", f"folder danych nie istnieje - zostanie zalozony przy pierwszym starcie programu (zapisu nie sprawdzono): {folder}",
                         "nic nie rob - po pierwszym uruchomieniu programu uruchom samokontrole jeszcze raz")]


def _dane_miejsce(k: _Kontekst) -> list:
    try:
        gb = _wolne_miejsce(_istniejacy_przodek(k.folder_danych())) / 2**30
    except OSError as e:
        return [_ostrzezenie("dane_miejsce", f"nie da sie odczytac wolnego miejsca na dysku folderu danych ({type(e).__name__})",
                             "sprawdz dysk folderu danych ([sciezki] baza w pliku ustawien)")]
    opis = f"wolne miejsce na dysku folderu danych: {gb:.1f} GB"
    if gb < MIEJSCE_BLAD_GB:
        return [_blad("dane_miejsce", f"{opis} (ponizej {MIEJSCE_BLAD_GB:g} GB wynik skanu moze sie nie zapisac)",
                      f"zwolnij miejsce na dysku - potrzeba co najmniej {MIEJSCE_OSTRZEZENIE_GB:g} GB")]
    if gb < MIEJSCE_OSTRZEZENIE_GB:
        return [_ostrzezenie("dane_miejsce", f"{opis} (ponizej {MIEJSCE_OSTRZEZENIE_GB:g} GB)",
                             f"zwolnij miejsce na dysku - zalecane co najmniej {MIEJSCE_OSTRZEZENIE_GB:g} GB")]
    return [_ok("dane_miejsce", opis)]


def _foldery_z_rejestru() -> list:
    """Foldery synchronizowane przez OneDrive (takze biblioteki SharePoint) z rejestru uzytkownika - tylko odczyt."""
    if os.name != "nt":
        return []
    wynik = []
    try:
        import winreg  # noqa: PLC0415

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\SyncEngines\Providers\OneDrive") as dostawcy:
            for i in range(winreg.QueryInfoKey(dostawcy)[0]):
                try:
                    with winreg.OpenKey(dostawcy, winreg.EnumKey(dostawcy, i)) as wpis:
                        wartosc = winreg.QueryValueEx(wpis, "MountPoint")[0]
                except OSError:
                    continue
                if isinstance(wartosc, str) and wartosc.strip():
                    wynik.append(wartosc)
    except (ImportError, OSError):
        pass
    return wynik


def _powod_synchronizacji(sciezka: Path, zmienne: list, rejestr: list) -> str | None:
    for nazwa, folder in zmienne:
        if _wewnatrz(sciezka, folder):
            return f"zmienna {nazwa}"
    if any(_wewnatrz(sciezka, folder) for folder in rejestr):
        return "folder synchronizowany przez OneDrive"
    for czesc in Path(os.path.abspath(sciezka)).parts:
        c = czesc.casefold()
        if c.startswith(NAZWY_SYNCHRONIZOWANE[0]) or NAZWY_SYNCHRONIZOWANE[1] in c:
            return f"katalog {czesc}"
    return None


def _dane_polozenie(k: _Kontekst) -> list:
    zmienne = [(n, v) for n, v in sorted(os.environ.items()) if n.upper().startswith("ONEDRIVE") and v.strip()]
    rejestr = _foldery_z_rejestru()
    klucze = [x for x in KLUCZE_DANYCH if str(k.ust["sciezki"].get(x, "")).strip()]
    zle = []
    for klucz in klucze:
        powod = _powod_synchronizacji(k.sciezka(klucz), zmienne, rejestr)
        if powod is not None:
            zle.append(f"[sciezki] {klucz} ({powod})")
    if zle:
        return [_blad("dane_polozenie", "dane programu leza w folderze synchronizowanym OneDrive / SharePoint: " + ", ".join(zle),
                      "przenies dane poza folder synchronizowany i popraw te sciezki w pliku ustawien - synchronizacja uszkadza plik bazy "
                      "i wysyla nazwy zlecen poza komputer")]
    if (k.korzen / PLIK_SUM).is_file() and _wewnatrz(k.folder_danych(), k.korzen):
        return [_ostrzezenie("dane_polozenie", "folder danych lezy w katalogu programu zainstalowanego z paczki wydania - po aktualizacji "
                             "nowa wersja programu nie zobaczy tej bazy",
                             "ustaw [sciezki] baza i pozostale sciezki danych poza katalogiem wersji programu (robi to instalator)")]
    return [_ok("dane_polozenie", f"dane programu poza folderami synchronizowanymi OneDrive / SharePoint (sprawdzone sciezki: {len(klucze)}, "
                f"znane foldery synchronizowane: {len(zmienne) + len(rejestr)})")]


# ----------------------------------------------------------------------------- 6. baza i 11. drugi egzemplarz

def _polacz_do_odczytu(plik: Path) -> sqlite3.Connection:
    """Polaczenie tylko do odczytu (``mode=ro``): niczego nie zaklada, nie migruje i nie zapisuje."""
    pol = sqlite3.connect(f"{Path(os.path.abspath(plik)).as_uri()}?mode=ro", uri=True, isolation_level=None,
                          timeout=CZEKAJ_NA_BAZE_MS / 1000)
    pol.execute(f"PRAGMA busy_timeout = {int(CZEKAJ_NA_BAZE_MS)}")
    return pol


def _zajeta(e: sqlite3.Error) -> bool:
    kod = getattr(e, "sqlite_errorcode", None)
    return (kod is not None and kod & 0xFF in (5, 6)) or "database is locked" in str(e) or "database is busy" in str(e)


def _quick_check(pol: sqlite3.Connection) -> list:
    """``PRAGMA quick_check`` z limitem czasu; ["ok"] = baza spojna. Przekroczenie limitu = ``sqlite3.OperationalError`` (interrupted)."""
    koniec = time.monotonic() + LIMIT_QUICK_CHECK_S
    pol.set_progress_handler(lambda: 1 if time.monotonic() > koniec else 0, KROK_QUICK_CHECK)
    try:
        return [str(w[0]) for w in pol.execute("PRAGMA quick_check(5)")]
    finally:
        pol.set_progress_handler(None, 0)


def _baza(k: _Kontekst) -> list:
    plik = k.sciezka("baza")
    rada_kopia = ("zamknij program i przywroc baze z kopii (plik kopii obok bazy albo kopia zrobiona przez instalator) - "
                  "samokontrola bazy nie naprawia, " + RADA_PROGRAMISTA)
    try:
        if not plik.exists() or (plik.is_file() and plik.stat().st_size == 0):
            return [_ostrzezenie("baza", f"brak pliku bazy - zostanie zalozona przy pierwszym starcie programu: {plik}",
                                 "nic nie rob - baza powstanie sama przy pierwszym uruchomieniu programu")]
        if not plik.is_file():
            return [_blad("baza", f"sciezka bazy nie jest plikiem: {plik}", "popraw [sciezki] baza w pliku ustawien")]
        rozmiar_mb = plik.stat().st_size / 2**20
    except OSError as e:
        return [_blad("baza", f"pliku bazy nie da sie odczytac ({type(e).__name__}): {plik}", "sprawdz dostep do folderu danych")]
    program = max(B.MIGRACJE)
    k.baza_jest = True
    etap, pol = "otwarcie", None
    try:
        pol = _polacz_do_odczytu(plik)
        wersja = int(pol.execute("PRAGMA user_version").fetchone()[0])
        pol.execute("SELECT COUNT(*) FROM sqlite_master").fetchone()  # pierwszy odczyt stron bazy: plik niebedacy baza zawodzi tutaj
        k.baza_czytelna = True
        if wersja > program:
            return [_blad("baza", f"baza nowsza niz program: wersja schematu {wersja}, a program obsluguje do {program} - bazy nie zmieniono",
                          "zainstaluj wersje programu, ktora zalozyla te baze, albo nowsza - nie uruchamiaj na niej starszego programu")]
        etap = "quick_check"
        problemy = _quick_check(pol)
    except sqlite3.Error as e:
        if _zajeta(e):
            k.baza_zajeta = True
            return [_ostrzezenie("baza", f"baza zajeta przez inny program (czekano {CZEKAJ_NA_BAZE_MS / 1000:g} s) - wersji schematu i spojnosci nie sprawdzono",
                                 "to nie blad - uruchom samokontrole ponownie za chwile albo po zamknieciu programu")]
        if (getattr(e, "sqlite_errorcode", None) or 0) & 0xFF == 8:  # SQLITE_READONLY_ROLLBACK: obok bazy lezy dziennik przerwanego zapisu
            return [_ostrzezenie("baza", "baza ma niedokonczony zapis po przerwanej pracy (plik dziennika obok bazy) - program cofnie go sam przy starcie, "
                                 "wersji schematu i spojnosci nie sprawdzono",
                                 "uruchom program, zamknij go i uruchom samokontrole ponownie - pliku z koncowka -journal nie usuwaj i nie kopiuj bazy bez niego")]
        if etap == "quick_check" and "interrupt" in str(e).lower():
            return [_ostrzezenie("baza", f"wersja schematu {wersja}, quick_check nie zakonczyl sie w {LIMIT_QUICK_CHECK_S:g} s (duza baza: "
                                 f"{rozmiar_mb:.0f} MB) - spojnosci nie sprawdzono", "to nie blad - baza jest duza, program jej uzywa bez przeszkod")]
        if etap == "quick_check":
            return [_blad("baza", f"baza uszkodzona: quick_check przerwany bledem ({type(e).__name__})", rada_kopia)]
        return [_blad("baza", f"plik nie jest baza SQLite albo jest uszkodzony ({type(e).__name__}) - pliku nie zmieniono: {plik}", rada_kopia)]
    finally:
        if pol is not None:
            pol.close()
    if problemy != ["ok"]:
        return [_blad("baza", f"baza uszkodzona: quick_check zglasza problemy ({len(problemy)}), pierwszy: {problemy[0][:80] if problemy else '-'}", rada_kopia)]
    if wersja < program:
        return [_ostrzezenie("baza", f"baza starsza niz program: wersja schematu {wersja}, program ma {program} - migracja z kopia przy starcie programu, quick_check ok",
                             "nic nie rob - program przy starcie sam zrobi kopie pliku bazy i ja zaktualizuje")]
    return [_ok("baza", f"baza otwiera sie do odczytu, wersja schematu {wersja} zgodna z programem, quick_check ok, {rozmiar_mb:.1f} MB")]


def _blokada_trzymana(plik_blokady: Path) -> bool | None:
    """Czy inny proces trzyma blokade programu (``aplikacja.BlokadaStanowiska``: plik ``<baza>.blokada``). True / False albo
    None, gdy nie da sie sprawdzic. Proba zajmuje blokade na ulamek milisekundy i zwalnia ja; pliku nie tworzy i nie zmienia."""
    if not plik_blokady.is_file():
        return False
    try:
        uchwyt = os.open(plik_blokady, os.O_RDWR)
    except OSError:
        return None
    try:
        if os.name == "nt":
            import msvcrt  # noqa: PLC0415

            try:
                msvcrt.locking(uchwyt, msvcrt.LK_NBLCK, 1)
            except OSError:
                return True
            os.lseek(uchwyt, 0, os.SEEK_SET)
            msvcrt.locking(uchwyt, msvcrt.LK_UNLCK, 1)
        else:
            import fcntl  # noqa: PLC0415

            try:
                fcntl.flock(uchwyt, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                return True
            fcntl.flock(uchwyt, fcntl.LOCK_UN)
        return False
    finally:
        os.close(uchwyt)


def _egzemplarz(k: _Kontekst) -> list:
    plik = k.sciezka("baza")
    trzymana = _blokada_trzymana(plik.with_name(plik.name + ".blokada"))
    rada = "to nie blad - przed aktualizacja programu albo powrotem do poprzedniej wersji zamknij program"
    if trzymana:
        return [_ostrzezenie("egzemplarz", "program Stanowisko jest teraz uruchomiony na tej bazie (drugi egzemplarz nie wystartuje)"
                             + (", baza zajeta w chwili sprawdzenia" if k.baza_zajeta else ""), rada)]
    if k.baza_zajeta:
        return [_ostrzezenie("egzemplarz", "baza zajeta przez inny program niz uruchomiony program Stanowisko (np. przegladarka bazy, kopia)",
                             "to nie blad - zamknij program, ktory trzyma plik bazy, zanim uruchomisz program Stanowisko")]
    if trzymana is None:
        return [_ostrzezenie("egzemplarz", "nie da sie sprawdzic pliku blokady programu obok bazy", "sprawdz dostep do folderu danych")]
    return [_ok("egzemplarz", "program Stanowisko nie jest teraz uruchomiony na tej bazie")]


# ----------------------------------------------------------------------------- 7. modele plytek

_WZOR_PLYTKI = re.compile(r"plytka_n(\d+)\.stl")
_KLUCZE_UKLADU = ("plate", "thickness", "markers", "code_dimples", "sockets")


def _wada_ukladu(nazwa: str, katalog: Path) -> str | None:
    """Co jest nie tak z ukladem plytki (None = w porzadku): katalog, ``uklad.json`` sprawdzony funkcja programu
    (``uklad.wczytaj``), co najmniej jeden model ``plytka_n<numer>.stl`` (z nich program bierze numery plytek ukladu)."""
    if not katalog.is_dir():
        return "brak katalogu"
    plik = katalog / "uklad.json"
    if not plik.is_file():
        return "brak pliku uklad.json"
    try:
        from . import uklad as U  # noqa: PLC0415 - potrzebuje numpy; gdy numpy sie nie laduje (BLAD w "moduly"), kontrola uproszczona
    except Exception:  # noqa: BLE001
        U = None
    try:
        if U is not None:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                numery = list(U.wczytaj(nazwa, katalog).numery)
        else:
            d = json.loads(plik.read_text(encoding="utf-8"))
            if not isinstance(d, dict) or any(x not in d for x in _KLUCZE_UKLADU):
                raise ValueError("brak kluczy ukladu")
            numery = [p.name for p in katalog.iterdir() if _WZOR_PLYTKI.fullmatch(p.name)]
    except Exception as e:  # noqa: BLE001 - kazdy blad wczytania ukladu to wada ukladu
        return f"zly plik uklad.json ({type(e).__name__})"
    if not numery:
        return "brak modeli plytka_n<numer>.stl"
    return None


def _modele(k: _Kontekst) -> list:
    plytki = k.ust["plytki"]
    wady = []
    for nazwa, wartosc in plytki.items():
        wada = _wada_ukladu(nazwa, k.wzgledna(wartosc))
        if wada is not None:
            wady.append(f"{nazwa}: {wada}")
    opis = f"uklady plytek z [plytki]: poprawne {len(plytki) - len(wady)} z {len(plytki)}"
    if wady:
        return [_blad("modele", opis + " - " + ", ".join(wady),
                      RADA_PACZKA + " (katalog modele_plytek) albo popraw [plytki] w pliku ustawien")]
    return [_ok("modele", opis + " (uklad.json i modele plytka_n*.stl)")]


# ----------------------------------------------------------------------------- 8. pula projektow

def _licz_stl(folder: Path, limit_s: float) -> tuple:
    """(liczba plikow STL puli, czy policzono do konca). Regula jak ``aplikacja.pliki_stl``: podfoldery tak, foldery ``_*`` nie."""
    koniec = time.monotonic() + limit_s
    n = 0
    for _, podfoldery, pliki in os.walk(folder):
        podfoldery[:] = [d for d in podfoldery if not d.startswith("_")]
        n += sum(1 for p in pliki if p.lower().endswith(".stl"))
        if time.monotonic() > koniec:
            return n, False
    return n, True


def _folder_puli(k: _Kontekst) -> tuple:
    """(folder puli albo None, czy wybrany w programie): jak ``Aplikacja._wczytaj_pule`` - plik ``PLIK_PULI`` obok bazy
    ma pierwszenstwo przed ``[sciezki] folder_cyrkon``."""
    domyslny = k.sciezka("folder_cyrkon")
    try:
        dane = json.loads((k.folder_danych() / PLIK_PULI).read_text(encoding="utf-8"))
        folder = Path(dane["folder"]) if dane.get("folder") else None
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return domyslny, False
    if folder is not None and os.path.normcase(os.path.abspath(folder)) == os.path.normcase(os.path.abspath(domyslny)):
        return domyslny, False
    return folder, True


def _pula_z_folderu(k: _Kontekst) -> Sprawdzenie:
    tryb = "pula z jednego folderu (pula_wpisow = false)"
    rada = "skopiuj projekty STL do folderu puli i uzyj w programie Odswiez pule - bez projektow skany czekaja"
    folder, wybrany = _folder_puli(k)
    skad = "folder wybrany w programie" if wybrany else "[sciezki] folder_cyrkon"
    if folder is None:
        return _ostrzezenie("pula", f"{tryb}: folder puli nie jest ustawiony w programie", "wskaz folder puli w programie")
    if not wybrany and k.foldery.get("folder_cyrkon") != "ok":
        return _ostrzezenie("pula", f"{tryb}: {skad} niedostepny - pula pusta, skany beda czekac", "popraw folder (wiersz folder_cyrkon)")
    rodzaj, dane = _z_limitem({"pula": lambda: _licz_stl(folder, LIMIT_LICZENIA_S) if folder.is_dir() else None},
                              LIMIT_LICZENIA_S + 1.0)["pula"]
    if rodzaj != "wynik" or dane is None:
        return _ostrzezenie("pula", f"{tryb}: {skad} niedostepny - pula pusta, skany beda czekac", rada)
    n, do_konca = dane
    opis = f"{tryb}: {n} {odmiana(n, 'plik', 'pliki', 'plikow')} STL, {skad}"
    if not do_konca:
        opis += f" (co najmniej - liczenie przerwane po {LIMIT_LICZENIA_S:g} s)"
    if n == 0:
        return _ostrzezenie("pula", opis + " - skany beda czekac na projekty", rada)
    return _ok("pula", opis)


def _pula_wpisow(k: _Kontekst) -> Sprawdzenie:
    tryb = "pula per praca (pula_wpisow = true)"
    if not k.baza_czytelna:
        powod = ("baza zajeta - indeksu zlecen nie odczytano" if k.baza_zajeta else
                 "bazy nie da sie teraz odczytac (wiersz baza) - indeksu zlecen nie odczytano" if k.baza_jest else
                 "brak bazy - indeks zlecen powstanie przy pierwszym starcie programu")
        return _ostrzezenie("pula", f"{tryb}: {powod}", "uruchom program i poczekaj na zbudowanie puli, potem uruchom samokontrole ponownie")
    try:
        pol = _polacz_do_odczytu(k.sciezka("baza"))
        try:
            zlecen, projektow, frezowan = (int(pol.execute(sql).fetchone()[0]) for sql in (
                "SELECT COUNT(*) FROM zlecenia WHERE usuniety = 0", "SELECT COUNT(*) FROM projekty WHERE usuniety = 0",
                "SELECT COUNT(*) FROM frezowania"))
        finally:
            pol.close()
    except sqlite3.Error as e:
        return _ostrzezenie("pula", f"{tryb}: indeksu zlecen w bazie nie da sie odczytac ({type(e).__name__})",
                            "uruchom program (zaktualizuje baze) i samokontrole ponownie")
    jest_csv = False
    if k.foldery.get("folder_millbox") == "ok":
        rodzaj, dane = _z_limitem({"csv": lambda: (k.sciezka("folder_millbox") / PLIK_WSPOLCZYNNIKOW).is_file()}, LIMIT_FOLDERU_S)["csv"]
        jest_csv = rodzaj == "wynik" and bool(dane)
    opis = (f"{tryb}: indeks w bazie - zlecen {zlecen}, projektow {projektow}, frezowan {frezowan}, "
            f"plik {PLIK_WSPOLCZYNNIKOW} w folderze MillBox: {'jest' if jest_csv else 'brak'}")
    if projektow == 0:
        return _ostrzezenie("pula", opis + " - pula pusta, skany beda czekac",
                            "sprawdz foldery Cyrkon i Prywatne i uzyj w programie Odswiez pule")
    if not jest_csv:
        return _ostrzezenie("pula", opis, f"zapisz plik {PLIK_WSPOLCZYNNIKOW} w [sciezki] folder_millbox albo wpisuj wspolczynnik krazka recznie w programie")
    return _ok("pula", opis)


def _pula(k: _Kontekst) -> list:
    return [_pula_wpisow(k) if k.ust["silnik"].get("pula_wpisow") else _pula_z_folderu(k)]


def _pamiec_puli(k: _Kontekst) -> list:
    katalog = k.sciezka("pula_cache")
    dni = k.ust["silnik"].get("pamiec_puli_dni", 0)
    if katalog.exists() and not katalog.is_dir():
        return [_ostrzezenie("pamiec_puli", f"sciezka pamieci puli nie jest folderem: {katalog}",
                             "usun ten plik albo popraw [sciezki] pula_cache w pliku ustawien")]
    projekty = katalog / "projekty"  # = pamiec_puli.PODKATALOG
    n, bajty = 0, 0
    if projekty.is_dir():
        with os.scandir(projekty) as wpisy:
            for w in wpisy:
                if w.name.endswith(".npz") and ".tmp" not in w.name:
                    n += 1
                    bajty += w.stat().st_size
    opis = f"pamiec puli na dysku: {n} {odmiana(n, 'wpis', 'wpisy', 'wpisow')}, {bajty / 2**20:.0f} MB, sprzatanie wpisow nieuzywanych od {dni} dni"
    return [_ok("pamiec_puli", opis + ("" if katalog.is_dir() else " (folder powstanie przy pierwszej budowie puli)"))]


# ----------------------------------------------------------------------------- 9. ramki

RAMKI = (("ramka_wieczorna", "wieczorna_host", "W", "wieczorna"), ("ramka_poranna", "poranna_host", "P", "poranna"))


def _zapytaj_ramke(host: str, port: int, klucz: str, limit_s: float) -> tuple:
    """Jedno ``GET /stan`` (tylko odczyt; bez ``X-Laptop-Id``, wiec ramka nie zapisuje kontaktu laptopa). Zwraca
    (status HTTP, slownik odpowiedzi albo None). Brak polaczenia = wyjatek ``OSError``."""
    import http.client  # noqa: PLC0415

    pol = http.client.HTTPConnection(host, int(port), timeout=limit_s)
    try:
        naglowki = {"Connection": "close", "Accept": "application/json"}
        if klucz:
            naglowki[NAGLOWEK_KLUCZA] = klucz
        pol.request("GET", "/stan", headers=naglowki)
        odpowiedz = pol.getresponse()
        tresc = odpowiedz.read(1 << 20)
        try:
            dane = json.loads(tresc.decode("utf-8")) if tresc else None
        except ValueError:
            dane = None
        return odpowiedz.status, dane if isinstance(dane, dict) else None
    finally:
        pol.close()


def _ramki(k: _Kontekst) -> list:
    r = k.ust["ramki"]
    port, klucz, limit = r["port"], r.get("klucz", ""), k.limit_ramki_s
    bez_ramek = "bez ramek program dziala - rozkladanie wedlug podpisow na ekranie"
    if k.bez_sieci:
        return [_ostrzezenie(kod, f"proby polaczenia z ramka {nazwa} nie bylo - pominieto (--bez-sieci)",
                             f"gdy ramka jest wlaczona, uruchom samokontrole bez --bez-sieci, {bez_ramek}") for kod, _, _, nazwa in RAMKI]
    proby = _z_limitem({kod: (lambda h=r[klucz_hosta]: _zapytaj_ramke(h, port, klucz, limit)) for kod, klucz_hosta, _, _ in RAMKI}, limit + 0.5)
    wynik = []
    for kod, klucz_hosta, rola, nazwa in RAMKI:
        adres = f"{r[klucz_hosta]}:{port}"
        rodzaj, dane = proby[kod]
        rada = f"wlacz ramke, sprawdz Wi-Fi i [ramki] {klucz_hosta} w pliku ustawien, {bez_ramek}"
        if rodzaj == "limit":
            wynik.append(_ostrzezenie(kod, f"ramka {nazwa} nieobecna: brak odpowiedzi w {limit:g} s ({adres})", rada))
            continue
        if rodzaj == "blad":
            wynik.append(_ostrzezenie(kod, f"ramka {nazwa} nieobecna: brak polaczenia z {adres} ({type(dane).__name__})", rada))
            continue
        status, stan = dane if isinstance(dane, tuple) and len(dane) == 2 else (None, None)
        if status == 401:
            wynik.append(_ostrzezenie(kod, f"ramka {nazwa} odpowiada pod {adres}, ale odrzuca klucz laptopa",
                                      f"wpisz w [ramki] klucz ten sam klucz, ktory ma ramka w swoim pliku konfiguracji, {bez_ramek}"))
        elif status != 200 or stan is None or "rola" not in stan:
            wynik.append(_ostrzezenie(kod, f"pod adresem ramki {nazwa} ({adres}) odpowiada inny program (status {status})",
                                      f"popraw [ramki] {klucz_hosta} i port w pliku ustawien, {bez_ramek}"))
        elif stan["rola"] != rola:
            wynik.append(_ostrzezenie(kod, f"pod adresem ramki {nazwa} ({adres}) odpowiada ramka o innej roli: rola {_linia(stan['rola'])[:8]}",
                                      f"popraw [ramki] {klucz_hosta} w pliku ustawien (hosty ramek zamienione?) albo role w konfiguracji ramki"))
        elif stan.get("blad_sprzetu"):
            wynik.append(_ostrzezenie(kod, f"ramka {nazwa} odpowiada ({adres}, rola {rola}), ale zglasza blad sprzetu",
                                      f"wylacz i wlacz zasilanie ramki, {bez_ramek}"))
        else:
            wynik.append(_ok(kod, f"ramka {nazwa} odpowiada ({adres}, rola {rola}, program {_linia(stan.get('program', '?'))[:40]})"))
    return wynik


# ----------------------------------------------------------------------------- 10. Excel

def _excel(k: _Kontekst) -> list:
    bez_excela = "bez Excela program dziala - zlecenia odhacza sie wtedy recznie"
    uwagi = []
    try:
        from . import excel as EX  # noqa: PLC0415 - tylko biblioteka standardowa

        uwagi = [str(u) for u in EX.Konfiguracja.z_ustawien(k.ust).ostrzezenia]
        tryb = k.ust["excel"].get("tryb", "pytaj")
    except Exception as e:  # noqa: BLE001
        return [_ostrzezenie("excel", f"ustawien [excel] nie da sie zastosowac ({type(e).__name__})", "popraw sekcje [excel] w pliku ustawien, " + bez_excela)]
    from . import excel_com  # noqa: PLC0415 - pywin32 importuje dopiero _win32com_client()

    try:
        klient = excel_com._win32com_client()  # ta sama droga, co excel_com.polacz
    except ImportError:
        return [_ostrzezenie("excel", "brak pakietu pywin32 - polaczenie z Excelem nie dziala", RADA_PACZKA + ", " + bez_excela)]
    uruchomiony = False
    com = None
    try:
        try:
            import pythoncom as com  # noqa: PLC0415

            com.CoInitialize()
        except Exception:  # noqa: BLE001 - atrapa klienta w testach, COM juz gotowy
            com = None
        try:
            obiekt = klient.GetActiveObject("Excel.Application")  # Excel JUZ uruchomiony; niczego nie otwiera
            uruchomiony = obiekt is not None
            del obiekt
        finally:
            if com is not None:
                com.CoUninitialize()
    except Exception:  # noqa: BLE001 - excel_com.polacz: kazdy blad GetActiveObject = "Excel nie jest uruchomiony"
        uruchomiony = False
    if not uruchomiony:
        return [_ostrzezenie("excel", "Excel nie jest uruchomiony w tej sesji uzytkownika" + (f" (uwagi do ustawien: {len(uwagi)})" if uwagi else ""),
                             "przed poranna praca otworz plik zlecen w Excelu na tym laptopie (z Autozapisem), " + bez_excela)]
    if uwagi:
        return [_ostrzezenie("excel", "Excel uruchomiony, uwaga do ustawien: " + uwagi[0], "popraw wskazane ustawienie w pliku ustawien")]
    return [_ok("excel", f"Excel uruchomiony, pywin32 jest (tryb {tryb}, arkusza nie otwierano)")]


# ----------------------------------------------------------------------------- 12. sumy plikow programu

_WZOR_SUMY = re.compile(r"([0-9A-Fa-f]{64}) [ *](.+)")


def czytaj_sumy(plik: str | Path) -> dict:
    """Plik w formacie ``sha256sum`` -> {sciezka wzgledna z ukosnikami /: suma malymi literami}. Zly plik = ``BladSum``."""
    try:
        tekst = Path(plik).read_bytes().decode("utf-8-sig")
    except UnicodeDecodeError as e:
        raise BladSum("plik sum nie jest tekstem UTF-8") from e
    sumy: dict = {}
    for nr, linia in enumerate(tekst.splitlines(), 1):
        if not linia.strip():
            continue
        m = _WZOR_SUMY.fullmatch(linia.rstrip())
        if m is None:
            raise BladSum(f"wiersz {nr} nie ma postaci <64 znaki hex><dwie spacje><sciezka>")
        rel = m.group(2).strip().replace("\\", "/")
        while rel.startswith("./"):
            rel = rel[2:]
        czesci = rel.split("/")
        if not rel or rel.startswith("/") or re.match(r"[A-Za-z]:", rel) or ".." in czesci or "" in czesci or "." in czesci:
            raise BladSum(f"wiersz {nr}: sciezka musi byc wzgledna od katalogu programu")
        if rel in sumy:
            raise BladSum(f"wiersz {nr}: sciezka powtorzona")
        sumy[rel] = m.group(1).lower()
    if not sumy:
        raise BladSum("plik sum jest pusty")
    return sumy


def _sha256(plik: Path) -> str:
    h = hashlib.sha256()
    with open(plik, "rb") as f:
        for kawalek in iter(lambda: f.read(1 << 20), b""):
            h.update(kawalek)
    return h.hexdigest()


def _klucz_pliku(rel: str) -> str:
    return rel.casefold() if os.name == "nt" else rel


def nadmiarowe(korzen: Path, sumy: dict, plik_sum: Path | None = None) -> list:
    """Pliki nadmiarowe = pliki w strefie programu, ktorych nie ma na liscie sum. Strefa: (1) katalogi najwyzszego poziomu
    wymienione na liscie (np. ``stanowisko``, ``ramka``, ``modele_plytek``) z podkatalogami, bez ``__pycache__`` i ``*.pyc``;
    (2) w katalogu glownym programu pliki, ktore Python moze zaladowac zamiast wlasciwego modulu (``ROZSZERZENIA_KODU``),
    i katalogi z ``__init__.py`` spoza listy. Pliki lokalne (``ustawienia.toml``, ``dane/``, srodowisko wersji) nie sa nadmiarowe."""
    znane = {_klucz_pliku(r) for r in sumy}
    strefy = sorted({r.split("/")[0] for r in sumy if "/" in r})
    wynik = []
    for strefa in strefy:
        for katalog, podkatalogi, pliki in os.walk(korzen / strefa):
            podkatalogi[:] = sorted(d for d in podkatalogi if d != "__pycache__")
            for nazwa in sorted(pliki):
                rel = (Path(katalog) / nazwa).relative_to(korzen).as_posix()
                if not nazwa.endswith((".pyc", ".pyo")) and _klucz_pliku(rel) not in znane:
                    wynik.append(rel)
    klucze_stref = {_klucz_pliku(s) for s in strefy}
    try:
        wpisy = sorted(os.scandir(korzen), key=lambda w: w.name)
    except OSError:
        wpisy = []
    for w in wpisy:
        if w.is_dir():
            if _klucz_pliku(w.name) not in klucze_stref and (Path(w.path) / "__init__.py").is_file():
                wynik.append(f"{w.name}/__init__.py")
        elif (w.name.lower().endswith(ROZSZERZENIA_KODU) and _klucz_pliku(w.name) not in znane
              and (plik_sum is None or os.path.abspath(w.path) != os.path.abspath(plik_sum))):
            wynik.append(w.name)
    return wynik


def _sumy(k: _Kontekst) -> list:
    rada = RADA_PACZKA + " - katalog programu rozni sie od wydania (pliki zmienione, brakujace albo nadmiarowe)"
    plik = k.sumy
    if plik is None:
        plik = k.korzen / PLIK_SUM
        if not plik.is_file():
            return [_ostrzezenie("sumy", f"kopia robocza bez pliku sum - plikow programu nie porownano z wydaniem (brak {PLIK_SUM} w katalogu programu)",
                                 "na stanowisku instaluj program z paczki wydania - w kopii roboczej programisty to nie blad")]
    plik = Path(plik)
    if not plik.is_file():
        return [_blad("sumy", f"brak pliku sum: {plik}", f"podaj w --sumy plik {PLIK_SUM} z paczki wydania")]
    try:
        sumy = czytaj_sumy(plik)
    except (BladSum, OSError) as e:
        powod = str(e) if isinstance(e, BladSum) else f"nie da sie go odczytac ({type(e).__name__})"
        return [_blad("sumy", f"plik sum niepoprawny: {powod} ({plik.name})", f"wez plik {PLIK_SUM} z paczki wydania - " + RADA_PACZKA)]
    zgodne, roznice = 0, []
    for rel, suma in sorted(sumy.items()):
        p = k.korzen / rel
        try:
            if not p.is_file():
                roznice.append(f"brak {rel}")
            elif _sha256(p) != suma:
                roznice.append(f"zmieniony {rel}")
            else:
                zgodne += 1
        except OSError:
            roznice.append(f"nieczytelny {rel}")
    roznice += [f"nadmiarowy {rel}" for rel in nadmiarowe(k.korzen, sumy, plik)]
    opis = f"sumy SHA-256 plikow programu zgodne {zgodne} z {len(sumy)} ({plik.name})"
    if not roznice:
        return [_ok("sumy", opis + ", plikow nadmiarowych 0")]
    reszta = len(roznice) - MAKS_ROZNIC
    opis += " - roznice: " + ", ".join(roznice[:MAKS_ROZNIC])
    if reszta > 0:
        opis += f" i {reszta} {odmiana(reszta, 'kolejna', 'kolejne', 'kolejnych')}"
    return [_blad("sumy", opis, rada)]


# ----------------------------------------------------------------------------- wykonanie

# (kody wierszy, funkcja) w kolejnosci wyjscia; funkcja zwraca po jednym ``Sprawdzenie`` na kod
SPRAWDZENIA = (
    (("python",), _python),
    (("pakiety",), _pakiety),
    (("moduly",), _moduly),
    (("ustawienia",), _ustawienia),
    (("operatorzy",), _operatorzy),
    (tuple(f[0] for f in FOLDERY_PRACY), _foldery),
    (("dane_folder",), _dane_folder),
    (("dane_miejsce",), _dane_miejsce),
    (("dane_polozenie",), _dane_polozenie),
    (("baza",), _baza),
    (("modele",), _modele),
    (("pula",), _pula),
    (("pamiec_puli",), _pamiec_puli),
    (tuple(r[0] for r in RAMKI), _ramki),
    (("excel",), _excel),
    (("egzemplarz",), _egzemplarz),
    (("sumy",), _sumy),
)
KODY = tuple(kod for kody, _ in SPRAWDZENIA for kod in kody)


def wykonaj(ust: dict, *, plik_ustawien: str | Path | None = None, sumy: str | Path | None = None, bez_sieci: bool = False,
            korzen: str | Path | None = None, limit_ramki_s: float | None = None) -> Wynik:
    """Wykonuje wszystkie sprawdzenia na wczytanych ustawieniach ``ust`` (``ustawienia.wczytaj_ustawienia``) i zwraca ``Wynik``.

    ``plik_ustawien`` - plik, z ktorego wczytano ``ust`` (do listy kluczy domyslnych; None = wywolanie z programu);
    ``sumy`` - plik sum (None = ``SUMY_PROGRAMU.sha256`` z katalogu programu, jesli jest); ``bez_sieci`` - bez proby ramek;
    ``korzen`` - katalog programu (domyslnie ten, z ktorego dziala modul); ``limit_ramki_s`` - limit proby jednej ramki.
    Nigdy nie rzuca wyjatku z powodu stanu komputera: sprawdzenie przerwane bledem ma poziom BLAD.
    """
    start = time.monotonic()
    k = _Kontekst(ust=ust, korzen=Path(korzen) if korzen is not None else UST.KORZEN,
                  plik_ustawien=Path(plik_ustawien) if plik_ustawien is not None else None,
                  sumy=Path(sumy) if sumy is not None else None, bez_sieci=bool(bez_sieci),
                  limit_ramki_s=float(limit_ramki_s) if limit_ramki_s is not None else LIMIT_RAMKI_S)
    sprawdzenia = []
    for kody, funkcja in SPRAWDZENIA:
        powod = "brak wyniku"
        try:
            gotowe = {s.kod: s for s in funkcja(k)}
        except Exception as e:  # noqa: BLE001 - samokontrola ma dojsc do konca i pokazac, co sie nie udalo
            gotowe, powod = {}, f"{type(e).__name__}: {B.bez_sciezek(str(e))[:120]}"
        for kod in kody:
            sprawdzenia.append(gotowe.get(kod) or _blad(kod, f"sprawdzenie przerwane bledem programu ({powod})", RADA_PROGRAMISTA))
    return Wynik(sprawdzenia, czas_s=time.monotonic() - start)


def _niewykonana(opis: str, rada: str) -> Wynik:
    return Wynik([_blad("ustawienia", opis, rada)], stan=NIEWYKONANA)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="stanowisko.samokontrola",
        description='Samokontrola programu "Stanowisko": srodowisko, ustawienia, foldery, baza, pula, ramki, Excel, sumy plikow. '
                    "Niczego nie naprawia i nie zmienia. Kod wyjscia: 0 = bez bledow, 1 = sa bledy, 2 = samokontroli nie wykonano.")
    parser.add_argument("--ustawienia", type=Path, default=None, metavar="PLIK", help="plik ustawien (domyslnie ustawienia.toml w katalogu programu)")
    parser.add_argument("--sumy", type=Path, default=None, metavar="PLIK",
                        help=f"plik sum SHA-256 plikow programu w formacie sha256sum (domyslnie {PLIK_SUM} w katalogu programu, jesli jest)")
    parser.add_argument("--json", action="store_true", help="wynik jako jeden obiekt JSON")
    parser.add_argument("--bez-sieci", action="store_true", help="bez proby polaczenia z ramkami (ramki = OSTRZEZENIE pominieto)")
    args = parser.parse_args(argv)
    for strumien in (sys.stdout, sys.stderr):  # sciezka ze znakiem spoza strony kodowej konsoli nie moze przerwac wypisywania
        try:
            strumien.reconfigure(errors="backslashreplace")
        except Exception:  # noqa: BLE001
            pass
    plik = args.ustawienia if args.ustawienia is not None else UST.PLIK_USTAWIEN
    rada = f"popraw plik ustawien (wzor: {UST.PLIK_PRZYKLADU.name}) albo podaj wlasciwy plik w --ustawienia"
    try:
        ust = UST.wczytaj_ustawienia(plik)
        wynik = wykonaj(ust, plik_ustawien=plik, sumy=args.sumy, bez_sieci=args.bez_sieci)
    except FileNotFoundError:
        wynik = _niewykonana(f"brak pliku ustawien: {plik}",
                             f"skopiuj {UST.PLIK_PRZYKLADU.name} jako {UST.PLIK_USTAWIEN.name} i uzupelnij sciezki albo podaj plik w --ustawienia")
    except UST.BladUstawien as e:
        wynik = _niewykonana("plik ustawien niepoprawny - " + _bez_ogonkow(str(e)), rada)
    except OSError as e:
        wynik = _niewykonana(f"pliku ustawien nie da sie odczytac ({type(e).__name__}): {plik}", rada)
    except Exception as e:  # noqa: BLE001 - komunikat dla czlowieka zamiast sladu wyjatku
        wynik = _niewykonana(f"samokontrola przerwana bledem programu ({type(e).__name__}: {B.bez_sciezek(str(e))[:120]})", RADA_PROGRAMISTA)
    print(json.dumps(wynik.do_slownika(), ensure_ascii=True, indent=2) if args.json else wynik.tekst())
    return wynik.kod_wyjscia


if __name__ == "__main__":
    raise SystemExit(main())
