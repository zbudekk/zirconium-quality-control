"""dzien_skanera_rdzen - logika okna "Dzien skanera - krok po kroku" bez Qt (okno: ``dzien_skanera.py``).

Cel: w dniu dostawy skanera zebrac komplet pierwszych danych tak, zeby nie zalezalo to od znajomosci programu
skanera ani od pamieci czlowieka. Zasada nadrzedna: lepiej skopiowac za duzo niz za malo; oryginalow nie zmieniamy
(pliki zrodlowe sa tylko czytane, nigdy przenoszone ani kasowane); program pisze wylacznie w folderze sesji.

Czesci:
* kroki dnia z pliku danych ``dzien_skanera_kroki.toml`` (``wczytaj_kroki``),
* ``Sesja`` - folder ``dane/dzien_skanera/<RRRR-MM-DD_GGMM>/`` z manifestem ``sesja.json`` zapisywanym atomowo
  po kazdej akcji (wznowienie po awarii: ``Sesja.wznow``),
* ``Zbieracz`` - obserwacja folderow eksportu przez odpytywanie, kopiowanie strumieniowe z SHA-256, pliki dodane
  recznie, kolejka szybkiej kontroli skanow (osobny proces - Open3D w watku pod Qt zawisa, patrz raporty/P3a_postep.md),
* szybka kontrola pliku skanu (``kontrola_pliku``; rozpoznanie ukladu plytki w JEDNEJ funkcji ``rozpoznaj_uklad``),
* zrzuty ekranu (``zrob_zrzut``), raport, sumy i archiwum ZIP (``spakuj``), sprawdzenie paczki (``sprawdz``).

Ciezkie biblioteki (numpy, trimesh, open3d, modul plate) sa importowane dopiero w funkcjach kontroli, wiec proces
okna ich nie laduje. Teksty pokazywane czlowiekowi w oknie maja polskie znaki; nazwy, komentarze i wyjscie
wiersza polecen - bez.

Wiersz polecen (z katalogu stanowisko/):
    py -3.12 -m stanowisko.dzien_skanera_rdzen --kontrola SKAN.stl [--wynik PLIK.json] [--numer N] [--ustawienia PLIK]
    py -3.12 -m stanowisko.dzien_skanera_rdzen --sprawdz FOLDER_SESJI_albo_ZIP
"""
from __future__ import annotations

import argparse
import collections
import dataclasses
import datetime as dt
import hashlib
import json
import math
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
import tomllib
import traceback
import zipfile
from pathlib import Path

from . import ustawienia as UST

FORMAT_MANIFESTU = "dzien_skanera/1"
KATALOG_SESJI = UST.KORZEN / "dane" / "dzien_skanera"
PLIK_KROKOW = Path(__file__).with_name("dzien_skanera_kroki.toml")
PLIK_MANIFESTU = "sesja.json"
PLIK_OBSERWATORA = "obserwator.json"
PLIK_LOGU = "log.txt"
PLIK_RAPORTU = "RAPORT_dzien_skanera.md"
PLIK_SUM = "SHA256SUMS.txt"
PLIK_SUM_NIEAKTUALNYCH = "SHA256SUMS.nieaktualne.txt"
KATALOG_PACZKI = "paczka"
PLIKI_ZYWE = (PLIK_MANIFESTU, PLIK_LOGU, PLIK_OBSERWATORA)  # zmieniaja sie po spakowaniu: w paczce sa ich migawki
PLIKI_ZAPISU_ATOMOWEGO = (PLIK_MANIFESTU, PLIK_OBSERWATORA, PLIK_RAPORTU, PLIK_SUM)  # w korzeniu sesji: ich .tmp / .bak to pliki robocze programu

ROZSZERZENIA_SIATEK = (".stl", ".ply", ".obj")
ROZSZERZENIA_OBRAZOW = (".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff")
ROZSZERZENIA_SPAKOWANE = (".png", ".jpg", ".jpeg", ".zip", ".7z", ".rar", ".gz", ".mp4")  # w ZIP bez ponownej kompresji
# projekty exocad (nazwiska w nazwach) nie trafiaja do paczki; wzor lapie tez nazwy NASZYCH kopii kolejnych wersji i duplikatow
# (``X_cad__zmiana2.stl``, ``X_cad__2.stl``). O wpisie manifestu decyduje ``czy_projekt_exocad`` (nazwa zrodla zapisana przy kopiowaniu).
WZOR_PROJEKTU_EXOCAD = re.compile(r"_cad(__\w+)?\.stl$", re.IGNORECASE)
WZOR_PROJEKTU_W_TEKSCIE = re.compile(r"_cad(?:__\w+)?\.stl", re.IGNORECASE)  # nazwa projektu wewnatrz tekstu (log, stan obserwatora)
ZNACZNIK_PROJEKTU = "projekt_pominiety"

BLOK_KOPII = 4 * 1024 * 1024  # bajtow: kopiowanie strumieniowe
REZERWA_DYSKU = 300 * 1024 * 1024  # bajtow: tyle ma zostac wolne po skopiowaniu pliku
OKRES_ODPYTYWANIA_S = 1.5  # co ile zbieracz oglada foldery
STABILNE_ODCZYTY = 2  # tyle kolejnych odczytow bez zmiany rozmiaru i czasu = plik gotowy
CZEKAJ_NA_PUSTY_S = 10.0  # plik o rozmiarze 0 kopiujemy dopiero po tylu sekundach bez zmian
CZEKAJ_NA_PELNY_STL_S = 30.0  # binarny STL z rozmiarem niezgodnym z naglowkiem: tyle czekamy, potem kopiujemy mimo to
LIMIT_WERSJI = 8  # tyle wersji tego samego pliku zrodlowego w jednym kroku; dalsze zmiany dopiero w nastepnym kroku
OKRES_AUTO_ZRZUTU_S = 10.0  # zrzut automatyczny przy nowym pliku nie czesciej niz co tyle
LIMIT_KONTROLI_S = 600.0  # proces kontroli dluzszy niz to jest zabijany (zbieranie trwa dalej)
NIZSZY_PRIORYTET_KONTROLI = True  # Windows: proces kontroli z priorytetem ponizej normalnego (program skanera ma pierwszenstwo)
CZEKAJ_NA_KONTROLE_PRZED_PAKOWANIEM_S = 120.0  # "Zakoncz i spakuj" czeka najwyzej tyle na trwajace kontrole; pozniejsze wyniki = "zmieniono po spakowaniu"
CZEKAJ_NA_PLIKI_PRZED_PAKOWANIEM_S = 20.0  # ... i najwyzej tyle na pliki, ktore wlasnie pojawily sie w folderach obserwowanych (jeszcze nie skopiowane)
LIMIT_ZIP = 1_900_000_000  # bajtow nieskompresowanych danych na jedna czesc archiwum
OKRES_ZAPISU_ZBIORCZEGO_S = 5.0  # seria plikow: manifest i stan obserwatora zapisywane nie czesciej niz co tyle (i zawsze na koncu serii)

# progi szybkiej kontroli - wskazowki z testow na skanach sztucznych (T10), do sprawdzenia na prawdziwym skanie
PROG_SZUMU_UWAGA_MM = 0.05  # RMS plaskiej czesci wiekszy niz to = zolte (cos sie ruszalo / podwojna powierzchnia)
PROG_SZUMU_DOBRY_MM = 0.015  # do tylu: ukruszenie 0,08 mm wykrywalne (T10)
PROG_SZUMU_SLABY_MM = 0.025  # ponad tyle: realna granica 0,12-0,15 mm (T10)
PROG_ODSTEPU_RZADKI_MM = 0.08  # sredni odstep wierzcholkow na pracach wiekszy niz to = dopisek "rzadko" (T10: za malo punktow na male ukruszenie)
MIN_TROJKATOW = 50_000  # mniej = zolte ("czy to pelna jakosc eksportu?")
PROG_PRZESUNIECIA_PRACY_MM = 0.3  # powtorka: srodek pracy przesuniety o wiecej = "praca ruszona"

RODZAJE_PLIKOW = ("siatka", "obraz", "dowolny", "brak")
KONTROLE = ("brak", "zrzuty", "plytka_pusta", "plytka_z_pracami", "powtorka", "inny_eksport", "ta_sama_plytka", "dowolny_skan", "kopia_folderu")
STANY_KROKU = ("czeka", "zrobiony", "pominiety")
KOLEJNOSC_WERDYKTOW = {"zielony": 0, "zolty": 1, "czerwony": 2}


# ----------------------------------------------------------------------------
# drobne narzedzia
# ----------------------------------------------------------------------------
def teraz_iso() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


def _io(p) -> str:
    """Sciezka do wywolan systemowych; na Windows z przedrostkiem dlugich sciezek (ponad 260 znakow)."""
    s = os.path.abspath(str(p))
    if os.name != "nt" or s.startswith("\\\\?\\"):
        return s
    if s.startswith("\\\\"):
        return "\\\\?\\UNC\\" + s[2:]
    return "\\\\?\\" + s


def skroc_sciezke(p) -> str:
    """Sciezka do zapisu w manifescie: katalog domowy uzytkownika zastapiony przez ``~`` (nazwa konta bywa nazwiskiem)."""
    s = str(p).replace("\\", "/")
    dom = str(Path.home()).replace("\\", "/")
    if dom and s.lower().startswith(dom.lower() + "/"):
        return "~" + s[len(dom):]
    return s


def rozwin_sciezke(s: str) -> Path:
    return Path(os.path.expanduser(s)) if s.startswith("~") else Path(s)


def tekst_rozmiaru(n: int | float) -> str:
    n = float(n)
    if n >= 1024**3:
        return f"{n / 1024**3:.2f} GB".replace(".", ",")
    if n >= 1024**2:
        return f"{n / 1024**2:.1f} MB".replace(".", ",")
    if n >= 1024:
        return f"{n / 1024:.0f} kB"
    return f"{int(n)} B"


def _l(x, miejsc: int = 2) -> str:
    """Liczba z przecinkiem dziesietnym (teksty dla czlowieka)."""
    if x is None:
        return "-"
    return f"{x:.{miejsc}f}".replace(".", ",")


def _czysty(o):
    """Struktura bezpieczna dla JSON: typy numpy na zwykle, NaN / inf na None."""
    if isinstance(o, dict):
        return {str(k): _czysty(v) for k, v in o.items()}
    if isinstance(o, (list, tuple, set)):
        return [_czysty(v) for v in o]
    if hasattr(o, "tolist") and not isinstance(o, (str, bytes)):
        return _czysty(o.tolist())
    if isinstance(o, bool) or o is None or isinstance(o, (str, int)):
        return o
    if isinstance(o, float):
        return o if math.isfinite(o) else None
    if hasattr(o, "item"):
        return _czysty(o.item())
    return str(o)


def zapisz_atomowo(plik: Path, dane: bytes, kopia: bool = False) -> None:
    """Zapis przez plik tymczasowy i ``os.replace``; ``kopia`` zostawia poprzednia wersje jako ``<plik>.bak``."""
    cel, tmp, bak = _io(plik), _io(str(plik) + ".tmp"), _io(str(plik) + ".bak")
    with open(tmp, "wb") as f:
        f.write(dane)
        f.flush()
        os.fsync(f.fileno())
    for proba in range(20):  # Windows: antywirus / indeksowanie potrafi na chwile zablokowac plik
        try:
            if kopia and os.path.exists(cel):
                os.replace(cel, bak)
            os.replace(tmp, cel)
            return
        except PermissionError:
            if proba == 19:
                raise
            time.sleep(0.05)


def sha256_pliku(plik, postep=None) -> str:
    h = hashlib.sha256()
    with open(_io(plik), "rb") as f:
        while True:
            blok = f.read(BLOK_KOPII)
            if not blok:
                break
            h.update(blok)
            if postep is not None:
                postep(len(blok))
    return h.hexdigest()


def nazwa_bezpieczna(s: str, dlugosc: int = 40) -> str:
    """Nazwa katalogu z dowolnego tekstu: litery ASCII, cyfry, kropka, myslnik, podkreslenie."""
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", s).strip("._")
    return (s or "folder")[:dlugosc]


# ----------------------------------------------------------------------------
# pliki zrodlowe: otwarcie bez blokowania programu skanera
# ----------------------------------------------------------------------------
_BLAD_WSPOLDZIELENIA = (32, 33)  # ERROR_SHARING_VIOLATION, ERROR_LOCK_VIOLATION


_K32 = None


def _k32():
    """kernel32 z opisanymi typami (tylko Windows)."""
    global _K32
    if _K32 is None:
        import ctypes
        from ctypes import wintypes

        k = ctypes.WinDLL("kernel32", use_last_error=True)
        k.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
        k.CreateFileW.restype = wintypes.HANDLE
        k.CloseHandle.argtypes = [wintypes.HANDLE]
        k.CloseHandle.restype = wintypes.BOOL
        _K32 = k
    return _K32


def _create_file(sciezka: str, wspoldzielenie: int, flagi: int = 0) -> tuple[int | None, int]:
    """CreateFileW do odczytu istniejacego pliku z podanym trybem wspoldzielenia: (uchwyt albo None, kod bledu)."""
    import ctypes
    from ctypes import wintypes

    uchwyt = _k32().CreateFileW(sciezka, 0x80000000, wspoldzielenie, None, 3, flagi, None)  # GENERIC_READ, OPEN_EXISTING
    if uchwyt is None or uchwyt == wintypes.HANDLE(-1).value:
        return None, ctypes.get_last_error()
    return uchwyt, 0


def otworz_zrodlo(plik):
    """Plik zrodlowy tylko do odczytu, z pelnym wspoldzieleniem (zapis, zmiana nazwy i usuniecie przez inny program
    pozostaja mozliwe) - kopiowanie nie moze przeszkodzic programowi skanera."""
    if os.name != "nt":
        return open(plik, "rb")
    import ctypes
    import msvcrt

    uchwyt, blad = _create_file(_io(plik), 1 | 2 | 4, 0x08000000)  # FILE_SHARE_READ | WRITE | DELETE, SEQUENTIAL_SCAN
    if uchwyt is None:
        raise ctypes.WinError(blad)
    return os.fdopen(msvcrt.open_osfhandle(uchwyt, os.O_RDONLY | getattr(os, "O_BINARY", 0)), "rb")


def ktos_pisze(plik) -> bool:
    """Windows: czy inny proces trzyma plik otwarty do zapisu (proba otwarcia bez zgody na zapis). Poza Windows: False."""
    if os.name != "nt":
        return False
    uchwyt, blad = _create_file(_io(plik), 1 | 4)  # FILE_SHARE_READ | DELETE: odmowa, gdy ktos ma plik otwarty do zapisu
    if uchwyt is None:
        return blad in _BLAD_WSPOLDZIELENIA
    _k32().CloseHandle(uchwyt)
    return False


def stl_binarny_kompletny(plik) -> bool | None:
    """True: rozmiar pliku zgadza sie z liczba trojkatow w naglowku binarnego STL; False: nie zgadza sie (plik
    w trakcie zapisu albo uciety); None: to nie jest binarny STL (tekstowy albo za krotki, zeby orzec)."""
    try:
        rozmiar = os.stat(_io(plik)).st_size
        with otworz_zrodlo(plik) as f:
            naglowek = f.read(84)
    except OSError:
        return None
    tekstowy = naglowek[:5].lower() == b"solid"
    if len(naglowek) < 84:
        return None if tekstowy else False
    if 84 + 50 * int.from_bytes(naglowek[80:84], "little") == rozmiar:
        return True
    return None if tekstowy else False


# ----------------------------------------------------------------------------
# miejsce na dysku i kopiowanie
# ----------------------------------------------------------------------------
class BrakMiejsca(OSError):
    """Za malo miejsca na dysku z folderem sesji - zglaszane PRZED kopiowaniem."""

    def __init__(self, potrzeba: int, wolne: int):
        self.potrzeba, self.wolne = int(potrzeba), int(wolne)
        super().__init__(
            f"Brak miejsca na dysku: potrzeba {tekst_rozmiaru(potrzeba)} i {tekst_rozmiaru(REZERWA_DYSKU)} zapasu, "
            f"wolne jest {tekst_rozmiaru(wolne)}. Zwolnij miejsce na dysku z programem stanowiska (np. opróżnij Kosz). "
            f"W programie skanera niczego nie kasuj — plik zostanie skopiowany sam, gdy miejsce się znajdzie."
        )


class ZrodloZmienione(OSError):
    """Plik zrodlowy zmienil sie w trakcie kopiowania - kopia odrzucona, proba zostanie powtorzona."""


class Przerwano(Exception):
    """Kopiowanie przerwane (zamykanie programu)."""


def wolne_miejsce(folder) -> int:
    p = Path(folder)
    while not p.exists() and p.parent != p:
        p = p.parent
    return shutil.disk_usage(p).free


def sprawdz_miejsce(folder, potrzeba: int, wolne=wolne_miejsce) -> None:
    w = wolne(folder)
    if w < potrzeba + REZERWA_DYSKU:
        raise BrakMiejsca(potrzeba, w)


def kopiuj_plik(zrodlo, cel, postep=None, przerwij=None, wolne=wolne_miejsce) -> dict:
    """Kopia strumieniowa ``zrodlo`` -> ``cel`` z SHA-256 liczonym w locie; zrodlo jest tylko czytane.

    Najpierw sprawdzenie miejsca (``BrakMiejsca`` przed pierwszym bajtem), zapis do ``<cel>.czesc`` i ``os.replace``.
    Gdy zrodlo zmieni rozmiar albo czas w trakcie kopiowania - ``ZrodloZmienione`` i brak pliku docelowego.
    """
    st0 = os.stat(_io(zrodlo))
    sprawdz_miejsce(Path(cel).parent, st0.st_size, wolne)
    os.makedirs(_io(Path(cel).parent), exist_ok=True)
    tmp = _io(str(cel) + ".czesc")
    h = hashlib.sha256()
    n = 0
    t0 = time.time()
    try:
        with otworz_zrodlo(zrodlo) as fz, open(tmp, "wb") as fc:
            while True:
                blok = fz.read(BLOK_KOPII)
                if not blok:
                    break
                fc.write(blok)
                h.update(blok)
                n += len(blok)
                if postep is not None:
                    postep(n, st0.st_size)
                if przerwij is not None and przerwij():
                    raise Przerwano()
            fc.flush()
            os.fsync(fc.fileno())
        st1 = os.stat(_io(zrodlo))
        if n != st0.st_size or (st1.st_size, st1.st_mtime_ns) != (st0.st_size, st0.st_mtime_ns):
            raise ZrodloZmienione(f"plik zmienil sie w trakcie kopiowania: {zrodlo}")
        try:
            os.utime(tmp, ns=(st0.st_atime_ns, st0.st_mtime_ns))
        except OSError:
            pass
        os.replace(tmp, _io(cel))
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    return {"rozmiar": n, "sha256": h.hexdigest(), "mtime_ns": st0.st_mtime_ns, "czas_s": round(time.time() - t0, 3)}


# ----------------------------------------------------------------------------
# kroki dnia (plik danych)
# ----------------------------------------------------------------------------
class BladKrokow(ValueError):
    """Zly plik krokow; komunikat z nazwa pliku i kroku."""


@dataclasses.dataclass(frozen=True)
class Krok:
    id: str
    tytul: str
    instrukcja: str
    wymagany: bool = True
    ile_plikow: int = 0  # ilu plikow rodzaju ``rodzaj_plikow`` sie spodziewamy (0 = krok bez plikow)
    rodzaj_plikow: str = "brak"  # siatka | obraz | dowolny | brak
    kontrola: str = "brak"  # jedno z KONTROLE: czego oczekujemy od skanu w tym kroku
    porownaj_z: str = ""  # id wczesniejszego kroku, z ktorego skanem porownujemy (powtorka, inny eksport)
    pola: tuple = ()  # pola do wypelnienia w oknie (klucze z [pola] w pliku krokow)
    wymagane_pola: tuple = ()  # pola, ktorych brak jest pokazywany jako brak kroku (nie blokuje)

    def slownik(self) -> dict:
        d = dataclasses.asdict(self)
        d["pola"], d["wymagane_pola"] = list(self.pola), list(self.wymagane_pola)
        return d

    @classmethod
    def ze_slownika(cls, d: dict) -> Krok:
        znane = {f.name for f in dataclasses.fields(cls)}
        d = {k: v for k, v in d.items() if k in znane}
        d["pola"], d["wymagane_pola"] = tuple(d.get("pola", ())), tuple(d.get("wymagane_pola", ()))
        return cls(**d)


def wczytaj_kroki(plik: Path | None = None) -> tuple[list[Krok], dict]:
    """Kroki dnia i definicje pol z pliku TOML. Zwraca (kroki, pola: klucz -> {etykieta, podpowiedz})."""
    plik = Path(plik) if plik is not None else PLIK_KROKOW
    try:
        with open(plik, "rb") as f:
            d = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise BladKrokow(f"{plik.name}: blad skladni TOML: {e}") from e
    pola = d.get("pola", {})
    for k, v in pola.items():
        if not isinstance(v, dict) or not isinstance(v.get("etykieta"), str):
            raise BladKrokow(f"{plik.name}: [pola.{k}]: brak tekstu 'etykieta'")
    kroki: list[Krok] = []
    for i, k in enumerate(d.get("krok", [])):
        gdzie = f"{plik.name}: krok {i + 1} ({k.get('id', '?')})"
        for wym, typ in (("id", str), ("tytul", str), ("instrukcja", str)):
            if not isinstance(k.get(wym), typ) or not k[wym].strip():
                raise BladKrokow(f"{gdzie}: brak pola '{wym}'")
        if not re.fullmatch(r"[a-z0-9_]{1,24}", k["id"]):
            raise BladKrokow(f"{gdzie}: id tylko z malych liter, cyfr i _ (do 24 znakow)")
        if k["id"] in {x.id for x in kroki}:
            raise BladKrokow(f"{gdzie}: id powtorzone")
        nieznane = set(k) - {f.name for f in dataclasses.fields(Krok)}
        if nieznane:
            raise BladKrokow(f"{gdzie}: nieznane pola {sorted(nieznane)}")
        krok = Krok.ze_slownika({**k, "instrukcja": k["instrukcja"].strip()})
        if krok.rodzaj_plikow not in RODZAJE_PLIKOW:
            raise BladKrokow(f"{gdzie}: rodzaj_plikow {krok.rodzaj_plikow!r} spoza {RODZAJE_PLIKOW}")
        if krok.kontrola not in KONTROLE:
            raise BladKrokow(f"{gdzie}: kontrola {krok.kontrola!r} spoza {KONTROLE}")
        if not isinstance(krok.ile_plikow, int) or isinstance(krok.ile_plikow, bool) or krok.ile_plikow < 0:
            raise BladKrokow(f"{gdzie}: ile_plikow musi byc liczba calkowita >= 0")
        if not isinstance(krok.wymagany, bool):
            raise BladKrokow(f"{gdzie}: wymagany musi byc true albo false")
        if krok.porownaj_z and krok.porownaj_z not in {x.id for x in kroki}:
            raise BladKrokow(f"{gdzie}: porownaj_z = {krok.porownaj_z!r} nie jest wczesniejszym krokiem")
        for p in (*krok.pola, *krok.wymagane_pola):
            if p not in pola:
                raise BladKrokow(f"{gdzie}: pole {p!r} nie ma definicji w [pola]")
        if not set(krok.wymagane_pola) <= set(krok.pola):
            raise BladKrokow(f"{gdzie}: wymagane_pola musza byc w 'pola'")
        kroki.append(krok)
    if not kroki:
        raise BladKrokow(f"{plik.name}: brak krokow ([[krok]])")
    return kroki, {k: {"etykieta": v["etykieta"], "podpowiedz": str(v.get("podpowiedz", ""))} for k, v in pola.items()}


# ----------------------------------------------------------------------------
# kompletnosc (czysta funkcja na manifescie - uzywa jej okno, raport i --sprawdz)
# ----------------------------------------------------------------------------
def plik_pasuje(wpis: dict, rodzaj: str) -> bool:
    roz = Path(wpis.get("cel", "")).suffix.lower()
    if rodzaj == "siatka":
        return roz in ROZSZERZENIA_SIATEK
    if rodzaj == "obraz":
        return roz in ROZSZERZENIA_OBRAZOW
    return rodzaj == "dowolny"


def stan_kopii_folderow(m: dict, krok: str | None = None) -> list[dict]:
    """Ostatnia kopia calych folderow kazdego kroku (albo tylko kroku ``krok``) z rejestru ``kopie_folderow`` manifestu:
    {krok, stan, pelna, jest, plikow, skopiowane, juz_byly, bledy, pominiete, niedostepne_katalogi, powod}.

    ``stan``: ``pelna`` | ``niepelna`` (bledy plikow / niedostepne podkatalogi) | ``przerwana`` (brak miejsca, zamkniecie programu) |
    ``w_toku`` (kopia trwa albo program zostal zabity w jej trakcie). ``jest`` = ile plikow z listy kopii jest w manifescie.
    Manifest bez rejestru (sesja zapisana wersja sprzed 17.11.2026) daje pusta liste - ocena kroku jak dawniej."""
    ostatnie: dict[str, dict] = {}
    for k in m.get("kopie_folderow", []):
        if krok is None or k.get("krok") == krok:
            ostatnie[k.get("krok", "")] = k
    wynik = []
    for id_kroku, k in ostatnie.items():
        plikow, juz = int(k.get("plikow", 0)), int(k.get("juz_byly", 0))
        stan = k.get("stan", "w_toku")
        if stan == "w_toku":  # liczby koncowe nie zostaly zapisane: liczymy wpisy plikow dodane od poczatku tej kopii
            skopiowane = sum(1 for w in m.get("pliki", []) if w.get("rodzaj") == "kopia_folderu" and w.get("id", 0) >= k.get("pierwszy_id", 0))
        else:
            skopiowane = int(k.get("skopiowane", 0))
        w_manifescie = sum(1 for w in m.get("pliki", []) if w.get("rodzaj") == "kopia_folderu")
        jest = min(juz + skopiowane, w_manifescie)  # "porownanie z lista": wpisow nie moze byc mniej, niz kopia podaje
        wynik.append({"krok": id_kroku, "stan": stan, "pelna": stan == "pelna" and jest >= plikow, "jest": jest, "plikow": plikow,
                      "skopiowane": skopiowane, "juz_byly": juz, "bledy": int(k.get("bledy", 0)),
                      "pominiete": int(k.get("pominiete", 0)) if stan != "w_toku" else max(0, plikow - juz - skopiowane),
                      "niedostepne_katalogi": int(k.get("niedostepne_katalogi", 0)), "powod": k.get("powod", "")})
    return wynik


def brak_kopii_folderow(m: dict, krok: str) -> str | None:
    """Tekst braku (dla czlowieka) dla kroku z kopia calego folderu, gdy ostatnia kopia nie jest pelna; None, gdy jest pelna albo nie bylo zadnej."""
    for k in stan_kopii_folderow(m, krok):
        if k["pelna"]:
            return None
        if k["stan"] == "w_toku":
            return f"kopia całego folderu nie została dokończona: w sesji jest {k['jest']} z {k['plikow']} plików — jeśli nic się teraz nie kopiuje, kliknij kopię jeszcze raz"
        szczegoly = [f"nie udało się: {k['bledy']}"] if k["bledy"] else []
        szczegoly += [f"nie zdążono: {k['pominiete']}"] if k["pominiete"] else []
        szczegoly += [f"niedostępne podfoldery: {k['niedostepne_katalogi']}"] if k["niedostepne_katalogi"] else []
        szczegoly += [k["powod"]] if k["powod"] else []
        return (f"kopia całego folderu NIEPEŁNA: w sesji jest {k['jest']} z {k['plikow']} plików" + (f" ({'; '.join(szczegoly)})" if szczegoly else "")
                + " — kliknij kopię jeszcze raz (skopiuje tylko brakujące pliki)")
    return None


def kompletnosc_z_manifestu(m: dict) -> list[dict]:
    """Ocena kazdego kroku: stan ``zrobiony`` | ``niepelny`` | ``pominiety`` | ``w_toku`` | ``czeka`` i lista brakow.

    Ocena jest z dowodow (pliki, pola, notatki), nie tylko z klikniecia "krok zrobiony": krok z kompletem plikow
    i pol jest zrobiony, krok zaczety bez kompletu - niepelny.
    """
    pola_def = m.get("definicje_pol", {})
    wynik = []
    for d in m.get("definicje_krokow", []):
        s = m.get("kroki", {}).get(d["id"], {})
        pliki = [w for w in m.get("pliki", []) if w.get("krok") == d["id"]]
        pasujace = [w for w in pliki if plik_pasuje(w, d.get("rodzaj_plikow", "brak"))]
        braki = []
        if d.get("ile_plikow", 0) and len(pasujace) < d["ile_plikow"]:
            co = {"siatka": "plików skanu", "obraz": "zrzutów ekranu / zdjęć", "dowolny": "plików"}.get(d.get("rodzaj_plikow"), "plików")
            braki.append(f"{co}: {len(pasujace)} z {d['ile_plikow']}")
        for p in d.get("wymagane_pola", []):
            wart = s.get("pola", {}).get(p)
            if p == "czas_skanu" and s.get("stoper"):
                continue
            if not str(wart or "").strip():
                braki.append("nie wpisano: " + pola_def.get(p, {}).get("etykieta", p))
        siatki = [w for w in pliki if plik_pasuje(w, "siatka") and w.get("kontrola")]
        if d.get("rodzaj_plikow") == "siatka" and siatki and all(w["kontrola"].get("werdykt") == "czerwony" for w in siatki):
            braki.append("żaden skan z tego kroku nie przeszedł kontroli — powtórz skan")
        brak_kopii = brak_kopii_folderow(m, d["id"]) if d.get("kontrola") == "kopia_folderu" else None
        if brak_kopii:  # krok nie jest "zrobiony" po pierwszym pliku: liczy sie wynik calej kopii zapisany w manifescie
            braki.append(brak_kopii)
        zaczety = (bool(pliki) or bool(str(s.get("notatka", "")).strip()) or any(str(v).strip() for v in s.get("pola", {}).values()) or bool(s.get("stoper"))
                   or bool(brak_kopii))
        if s.get("stan") == "pominiety":
            stan = "pominiety"
        elif not braki and (d.get("ile_plikow", 0) > 0 or s.get("stan") == "zrobiony"):
            stan = "zrobiony"
        elif zaczety or s.get("stan") == "zrobiony":
            stan = "niepelny"
        elif m.get("biezacy_krok") == d["id"]:
            stan = "w_toku"
        else:
            stan = "czeka"
        wynik.append({"id": d["id"], "tytul": d["tytul"], "wymagany": bool(d.get("wymagany", True)), "stan": stan, "braki": braki,
                      "plikow": len(pasujace), "wszystkich_plikow": len(pliki), "oczekiwane": d.get("ile_plikow", 0), "powod": s.get("powod", "")})
    return wynik


def braki_wymaganych(m: dict) -> tuple[list[str], list[str]]:
    """(braki wymaganych krokow, pominiecia wymaganych krokow z powodami) - teksty dla czlowieka."""
    braki, pominiete = [], []
    for o in kompletnosc_z_manifestu(m):
        if not o["wymagany"]:
            continue
        if o["stan"] == "pominiety":
            pominiete.append(f"{o['tytul']} — pominięty, bo: {o['powod'] or '(bez powodu)'}")
        elif o["stan"] != "zrobiony":
            braki.append(f"{o['tytul']} — " + ("; ".join(o["braki"]) if o["braki"] else "nie zrobiony"))
    return braki, pominiete


# ----------------------------------------------------------------------------
# sesja
# ----------------------------------------------------------------------------
class Sesja:
    """Folder sesji z manifestem ``sesja.json``; kazda zmiana konczy sie zapisem atomowym (z kopia ``.bak``)."""

    def __init__(self, folder: Path, manifest: dict):
        self.folder = Path(folder)
        self.m = manifest
        self._zamek = threading.RLock()
        self._zamek_logu = threading.Lock()
        self._ostatni_zapis = 0.0
        self._zalegly = False  # zmiana manifestu odlozona przez zapisz(pilne=False)
        self._pakowanie = False
        self.kroki = [Krok.ze_slownika(d) for d in manifest["definicje_krokow"]]

    # --- tworzenie i wznawianie
    @classmethod
    def nowa(cls, katalog: Path | None = None, kroki: list[Krok] | None = None, pola: dict | None = None,
             foldery: list | None = None, teraz: dt.datetime | None = None) -> Sesja:
        katalog = Path(katalog) if katalog is not None else KATALOG_SESJI
        if kroki is None:
            kroki, pola = wczytaj_kroki()
        teraz = teraz or dt.datetime.now()
        nazwa = teraz.strftime("%Y-%m-%d_%H%M")
        folder, n = katalog / nazwa, 1
        while folder.exists():
            n += 1
            folder = katalog / f"{nazwa}_{n}"
        os.makedirs(_io(folder))
        m = {
            "format": FORMAT_MANIFESTU, "nazwa": folder.name, "utworzono": teraz.isoformat(timespec="seconds"), "zakonczono": None,
            "spakowano": [], "zmieniono_po_spakowaniu": False, "foldery": [], "auto_zrzut": False, "biezacy_krok": kroki[0].id,
            "definicje_pol": pola or {}, "definicje_krokow": [k.slownik() for k in kroki],
            "kroki": {k.id: {"stan": "czeka", "powod": "", "notatka": "", "pola": {}, "rozpoczeto": None, "zakonczono": None,
                             "stoper": [], "stoper_start": None} for k in kroki},
            "pliki": [], "nastepny_id": 1, "zdarzenia": [],
        }
        s = cls(folder, m)
        for f in foldery or []:
            s.dodaj_folder(f, zapisz=False)
        s.m["kroki"][kroki[0].id]["rozpoczeto"] = m["utworzono"]
        s.zdarzenie("start sesji")
        s.log(f"start sesji {folder.name}")
        return s

    @classmethod
    def wznow(cls, folder: Path) -> Sesja:
        """Wczytuje sesje z ``sesja.json``; gdy plik jest uszkodzony (awaria w trakcie zapisu) - z kopii ``.bak``."""
        folder = Path(folder)
        bledy = []
        for nazwa in (PLIK_MANIFESTU, PLIK_MANIFESTU + ".bak", PLIK_MANIFESTU + ".tmp"):
            p = folder / nazwa
            try:
                with open(_io(p), "rb") as f:
                    m = json.loads(f.read().decode("utf-8"))
                if m.get("format") != FORMAT_MANIFESTU or "definicje_krokow" not in m:
                    raise ValueError(f"nieznany format manifestu: {m.get('format')!r}")
            except (OSError, ValueError) as e:
                bledy.append(f"{nazwa}: {e}")
                continue
            s = cls(folder, m)
            s.m["nazwa"] = folder.name
            s._domknij_przerwane_kopie()
            if nazwa != PLIK_MANIFESTU:
                s.log(f"UWAGA: {PLIK_MANIFESTU} nieczytelny, sesja wznowiona z {nazwa} ({'; '.join(bledy)})")
            s.zdarzenie("wznowienie sesji" + ("" if nazwa == PLIK_MANIFESTU else f" z {nazwa}"))
            s.log("wznowienie sesji")
            return s
        raise FileNotFoundError(f"nie da sie wczytac sesji z {folder}: {'; '.join(bledy)}")

    @staticmethod
    def lista(katalog: Path | None = None) -> list[dict]:
        """Sesje w katalogu, od najnowszej: {folder, nazwa, utworzono, zakonczono, plikow}."""
        katalog = Path(katalog) if katalog is not None else KATALOG_SESJI
        wynik = []
        if not katalog.is_dir():
            return wynik
        for p in sorted(katalog.iterdir(), reverse=True):
            if not p.is_dir():
                continue
            for nazwa in (PLIK_MANIFESTU, PLIK_MANIFESTU + ".bak"):
                try:
                    m = json.loads((p / nazwa).read_text(encoding="utf-8"))
                    wynik.append({"folder": p, "nazwa": p.name, "utworzono": m.get("utworzono"), "zakonczono": m.get("zakonczono"), "plikow": len(m.get("pliki", []))})
                    break
                except (OSError, ValueError):
                    continue
        wynik.sort(key=lambda s: s["utworzono"] or "", reverse=True)
        return wynik

    # --- zapis
    def zapisz(self, pilne: bool = True) -> None:
        """Zapis manifestu. ``pilne=False`` (seria plikow - kolejne czekaja na kopie): nie czesciej niz co
        OKRES_ZAPISU_ZBIORCZEGO_S; niezapisana zmiana zostaje oznaczona i zapisuje ja ``zapisz_zalegle`` na koncu serii."""
        with self._zamek:
            if not pilne and time.monotonic() - self._ostatni_zapis < OKRES_ZAPISU_ZBIORCZEGO_S:
                self._zalegly = True
                return
            if self.m.get("spakowano") and not self.m.get("zmieniono_po_spakowaniu") and not self._pakowanie:
                self.m["zmieniono_po_spakowaniu"] = True
                self._uniewaznij_sumy()
            dane = json.dumps(self.m, ensure_ascii=False, indent=1).encode("utf-8")
            zapisz_atomowo(self.folder / PLIK_MANIFESTU, dane, kopia=True)
            self._ostatni_zapis = time.monotonic()
            self._zalegly = False

    def zapisz_zalegle(self) -> None:
        """Zapis zmian odlozonych przez ``zapisz(pilne=False)`` (koniec serii kopiowania)."""
        with self._zamek:
            if self._zalegly:
                self.zapisz()

    def _uniewaznij_sumy(self) -> None:
        try:
            if os.path.exists(_io(self.folder / PLIK_SUM)):
                os.replace(_io(self.folder / PLIK_SUM), _io(self.folder / PLIK_SUM_NIEAKTUALNYCH))
        except OSError:
            pass

    def log(self, tekst: str) -> None:
        with self._zamek_logu:
            try:
                with open(_io(self.folder / PLIK_LOGU), "a", encoding="utf-8") as f:
                    f.write(f"{teraz_iso()} {tekst}\n")
            except OSError:
                pass

    def log_wyjatku(self, gdzie: str, e: BaseException) -> None:
        self.log(f"WYJATEK w {gdzie}: {type(e).__name__}: {e}\n" + "".join(traceback.format_exception(type(e), e, e.__traceback__)))

    def zdarzenie(self, co: str, **dane) -> None:
        with self._zamek:
            self.m["zdarzenia"].append({"czas": teraz_iso(), "co": co, **dane})
            self.zapisz()

    def sciezka(self, wzgledna: str) -> Path:
        """Sciezka w folderze sesji; kazdy zapis programu przechodzi przez te funkcje (nic poza folderem sesji)."""
        p = (self.folder / wzgledna).resolve()
        if p != self.folder.resolve() and self.folder.resolve() not in p.parents:
            raise ValueError(f"sciezka poza folderem sesji: {wzgledna}")
        return self.folder / wzgledna

    # --- foldery obserwowane
    def dodaj_folder(self, sciezka, zapisz: bool = True) -> dict | None:
        """Dopisuje folder obserwowany (bez duplikatow); zwraca wpis {etykieta, sciezka, dodano} albo None, gdy juz byl."""
        with self._zamek:
            s = skroc_sciezke(os.path.abspath(str(rozwin_sciezke(str(sciezka)))))
            if any(f["sciezka"].lower() == s.lower() for f in self.m["foldery"]):
                return None
            baza = nazwa_bezpieczna(Path(s).name or "dysk")
            etykieta, n = baza, 1
            while any(f["etykieta"].lower() == etykieta.lower() for f in self.m["foldery"]):
                n += 1
                etykieta = f"{baza}_{n}"
            wpis = {"etykieta": etykieta, "sciezka": s, "dodano": teraz_iso()}
            self.m["foldery"].append(wpis)
            if zapisz:
                self.zdarzenie("dodano folder obserwowany", folder=s, etykieta=etykieta)
            return wpis

    def foldery(self) -> list[tuple[str, Path]]:
        return [(f["etykieta"], rozwin_sciezke(f["sciezka"])) for f in self.m["foldery"]]

    # --- kroki
    def krok(self, id_: str) -> Krok:
        for k in self.kroki:
            if k.id == id_:
                return k
        raise KeyError(f"brak kroku {id_!r}")

    def numer_kroku(self, id_: str) -> int:
        return [k.id for k in self.kroki].index(id_) + 1

    def folder_kroku(self, id_: str) -> str:
        """Folder kroku wzgledem folderu sesji, np. ``kroki/k04_pusta``."""
        return f"kroki/k{self.numer_kroku(id_):02d}_{id_}"

    @property
    def biezacy(self) -> str:
        return self.m["biezacy_krok"]

    def ustaw_biezacy(self, id_: str) -> None:
        with self._zamek:
            self.krok(id_)
            if self.m["biezacy_krok"] == id_:
                return
            self.m["biezacy_krok"] = id_
            s = self.m["kroki"][id_]
            s["rozpoczeto"] = s["rozpoczeto"] or teraz_iso()
            self.zdarzenie("biezacy krok", krok=id_)

    def nastepny_krok(self, id_: str) -> str | None:
        i = self.numer_kroku(id_)
        return self.kroki[i].id if i < len(self.kroki) else None

    def zakoncz_krok(self, id_: str) -> str | None:
        """Oznacza krok jako zrobiony i przechodzi do nastepnego (zwraca jego id albo None na koncu listy)."""
        with self._zamek:
            s = self.m["kroki"][id_]
            s["stan"], s["powod"], s["zakonczono"] = "zrobiony", "", teraz_iso()
            self.zdarzenie("krok zrobiony", krok=id_)
            nast = self.nastepny_krok(id_)
            if nast is not None:
                self.ustaw_biezacy(nast)
            return nast

    def pomin_krok(self, id_: str, powod: str) -> str | None:
        """Pominiecie z powodem ("nie udalo sie / pomijam, bo ..."): zapisane, nie blokuje; przejscie do nastepnego."""
        with self._zamek:
            s = self.m["kroki"][id_]
            s["stan"], s["powod"], s["zakonczono"] = "pominiety", powod.strip(), teraz_iso()
            self.zdarzenie("krok pominiety", krok=id_, powod=powod.strip())
            nast = self.nastepny_krok(id_)
            if nast is not None:
                self.ustaw_biezacy(nast)
            return nast

    def przywroc_krok(self, id_: str) -> None:
        with self._zamek:
            s = self.m["kroki"][id_]
            if s["stan"] != "czeka":
                self.zdarzenie("krok przywrocony", krok=id_, poprzedni_stan=s["stan"], poprzedni_powod=s["powod"])
                s["stan"], s["powod"], s["zakonczono"] = "czeka", "", None
                self.zapisz()

    def ustaw_notatke(self, id_: str, tekst: str) -> None:
        with self._zamek:
            if self.m["kroki"][id_]["notatka"] != tekst:
                self.m["kroki"][id_]["notatka"] = tekst
                self.zapisz()

    def ustaw_pole(self, id_: str, pole: str, wartosc: str) -> None:
        with self._zamek:
            if self.m["kroki"][id_]["pola"].get(pole, "") != wartosc:
                self.m["kroki"][id_]["pola"][pole] = wartosc
                self.zapisz()

    def ustaw_auto_zrzut(self, wlaczony: bool) -> None:
        with self._zamek:
            if self.m["auto_zrzut"] != bool(wlaczony):
                self.m["auto_zrzut"] = bool(wlaczony)
                self.zdarzenie("zrzut automatyczny przy nowym pliku", wlaczony=bool(wlaczony))

    def stoper_start(self, id_: str) -> None:
        with self._zamek:
            self.m["kroki"][id_]["stoper_start"] = teraz_iso()
            self.zapisz()

    def stoper_stop(self, id_: str) -> float | None:
        """Konczy pomiar czasu skanu; zwraca sekundy (None, gdy stoper nie byl wlaczony)."""
        with self._zamek:
            s = self.m["kroki"][id_]
            if not s.get("stoper_start"):
                return None
            start, stop = s["stoper_start"], teraz_iso()
            sek = (dt.datetime.fromisoformat(stop) - dt.datetime.fromisoformat(start)).total_seconds()
            s["stoper"].append({"start": start, "stop": stop, "s": sek})
            s["stoper_start"] = None
            self.zapisz()
            return sek

    # --- pliki
    def wpis(self, id_pliku: int) -> dict:
        for w in self.m["pliki"]:
            if w["id"] == id_pliku:
                return w
        raise KeyError(f"brak pliku o id {id_pliku}")

    def pliki_kroku(self, id_: str) -> list[dict]:
        return [w for w in self.m["pliki"] if w["krok"] == id_]

    def cel_wolny(self, wzgledna: str) -> str:
        """``wzgledna`` albo - gdy taki plik juz jest w manifescie - ta sama nazwa z ``__2``, ``__3`` ... przed rozszerzeniem.
        Plik na dysku, ktorego nie ma w manifescie (awaria miedzy kopia a zapisem), jest zastepowany."""
        zajete = {w["cel"].lower() for w in self.m["pliki"]}
        if wzgledna.lower() not in zajete:
            return wzgledna
        p = Path(wzgledna)
        n = 2
        while True:
            kandydat = (p.parent / f"{p.stem}__{n}{p.suffix}").as_posix()
            if kandydat.lower() not in zajete:
                return kandydat
            n += 1

    def dodaj_plik(self, krok: str, rodzaj: str, cel: str, rozmiar: int, sha256: str, mtime_ns: int | None = None, zrodlo=None,
                   folder: str | None = None, wzgledna: str | None = None, czas_kopii_s: float | None = None, uwagi: list | None = None,
                   pilne: bool = True) -> dict:
        with self._zamek:
            wpis = {
                "id": self.m["nastepny_id"], "krok": krok, "rodzaj": rodzaj, "cel": cel, "rozmiar": int(rozmiar), "sha256": sha256,
                "mtime": dt.datetime.fromtimestamp(mtime_ns / 1e9).isoformat(timespec="seconds") if mtime_ns else None, "mtime_ns": mtime_ns,
                "zrodlo": skroc_sciezke(zrodlo) if zrodlo is not None else None, "folder": folder, "wzgledna": wzgledna,
                "skopiowano": teraz_iso(), "czas_kopii_s": czas_kopii_s, "uwagi": list(uwagi or []), "kontrola": None,
            }
            self.m["nastepny_id"] += 1
            self.m["pliki"].append(wpis)
            self.zapisz(pilne)
            return wpis

    def ustaw_kontrole(self, id_pliku: int, skrot: dict) -> None:
        with self._zamek:
            self.wpis(id_pliku)["kontrola"] = skrot
            self.zapisz()

    def przenies_plik(self, id_pliku: int, nowy_krok: str) -> dict:
        """Przenosi NASZA kopie pliku do folderu innego kroku (gdy plik trafil do zlego kroku); oryginalu nie dotyka."""
        with self._zamek:
            w = self.wpis(id_pliku)
            stary = w["krok"]
            if stary == nowy_krok:
                return w
            przedrostek = self.folder_kroku(stary) + "/"
            reszta = w["cel"][len(przedrostek):] if w["cel"].startswith(przedrostek) else Path(w["cel"]).name
            nowy_cel = self.cel_wolny(f"{self.folder_kroku(nowy_krok)}/{reszta}")
            os.makedirs(_io(self.sciezka(nowy_cel).parent), exist_ok=True)
            os.replace(_io(self.sciezka(w["cel"])), _io(self.sciezka(nowy_cel)))
            self.m["zdarzenia"].append({"czas": teraz_iso(), "co": "plik przeniesiony do innego kroku", "plik": id_pliku, "z": stary, "do": nowy_krok, "bylo": w["cel"]})
            w["krok"], w["cel"] = nowy_krok, nowy_cel
            self.zapisz()
            return w

    # --- rejestr kopii calych folderow (klucz ``kopie_folderow`` - dodany 17.11.2026; starsze manifesty go nie maja)
    def rozpocznij_kopie_folderow(self, krok: str, zrodla: list, plikow: int, bajtow: int, juz_byly: int, niedostepne: int) -> dict:
        """Wpis kopii calych folderow ze stanem ``w_toku``, zapisany PRZED pierwszym plikiem: po zabiciu programu w manifescie zostaje slad."""
        with self._zamek:
            rejestr = self.m.setdefault("kopie_folderow", [])
            wpis = {"nr": len(rejestr) + 1, "krok": krok, "start": teraz_iso(), "koniec": None, "stan": "w_toku", "powod": "",
                    "zrodla": [skroc_sciezke(z) for z in zrodla], "plikow": int(plikow), "bajtow": int(bajtow), "juz_byly": int(juz_byly), "skopiowane": 0,
                    "bledy": 0, "pominiete": 0, "niedostepne_katalogi": int(niedostepne), "pierwszy_id": self.m["nastepny_id"]}
            rejestr.append(wpis)
            self.zdarzenie("kopia calych folderow", krok=krok, plikow=int(plikow), bajtow=int(bajtow), juz_byly=int(juz_byly), zrodla=wpis["zrodla"])
            return wpis

    def zakoncz_kopie_folderow(self, wpis: dict, skopiowane: int, bledy: int, pominiete: int, powod: str = "") -> dict:
        """Wynik kopii calych folderow: liczby i stan ``pelna`` | ``niepelna`` (bledy, niedostepne podkatalogi) | ``przerwana`` (``powod``)."""
        with self._zamek:
            caly = not bledy and not pominiete and not wpis.get("niedostepne_katalogi")
            wpis.update({"koniec": teraz_iso(), "stan": "pelna" if caly else ("przerwana" if powod else "niepelna"), "powod": powod,
                         "skopiowane": int(skopiowane), "bledy": int(bledy), "pominiete": int(pominiete)})
            self.zdarzenie("kopia calych folderow: koniec", krok=wpis["krok"], stan=wpis["stan"], plikow=wpis["plikow"], juz_byly=wpis["juz_byly"],
                           skopiowane=int(skopiowane), bledy=int(bledy), pominiete=int(pominiete), powod=powod)
            return wpis

    def _domknij_przerwane_kopie(self) -> None:
        """Wznowienie: kopia calych folderow, ktora zostala "w toku" (program zabity w jej trakcie), dostaje stan ``przerwana`` z liczbami z manifestu."""
        for k in self.m.get("kopie_folderow", []):
            if k.get("stan") == "w_toku":
                skopiowane = sum(1 for w in self.m["pliki"] if w.get("rodzaj") == "kopia_folderu" and w["id"] >= k.get("pierwszy_id", 0))
                pominiete = max(0, int(k.get("plikow", 0)) - int(k.get("juz_byly", 0)) - skopiowane)
                self.log(f"kopia calych folderow nr {k.get('nr')} byla w toku przy zamknieciu programu: skopiowane {skopiowane}, brakuje {pominiete}")
                self.zakoncz_kopie_folderow(k, skopiowane, 0, pominiete, "program został zamknięty w trakcie kopii" if pominiete else "")

    # --- kompletnosc
    def kompletnosc(self) -> list[dict]:
        with self._zamek:
            return kompletnosc_z_manifestu(self.m)

    def braki(self) -> tuple[list[str], list[str]]:
        with self._zamek:
            return braki_wymaganych(self.m)


# ----------------------------------------------------------------------------
# zrzuty ekranu
# ----------------------------------------------------------------------------
def _zrzut_wszystkich_ekranow():
    from PIL import ImageGrab

    return ImageGrab.grab(all_screens=True)


def zrob_zrzut(sesja: Sesja, krok: str | None = None, powod: str = "", grab=None) -> dict:
    """Zrzut wszystkich monitorow do ``<folder kroku>/zrzuty/zrzut_<data>_<czas>.png``; zwraca wpis manifestu."""
    krok = krok or sesja.biezacy
    obraz = (grab or _zrzut_wszystkich_ekranow)()
    cel = sesja.cel_wolny(f"{sesja.folder_kroku(krok)}/zrzuty/zrzut_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    p = sesja.sciezka(cel)
    os.makedirs(_io(p.parent), exist_ok=True)
    tmp = _io(str(p) + ".czesc")
    with open(tmp, "wb") as f:
        obraz.save(f, format="PNG")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, _io(p))
    st = os.stat(_io(p))
    return sesja.dodaj_plik(krok, "zrzut", cel, st.st_size, sha256_pliku(p), st.st_mtime_ns, uwagi=[powod] if powod else None)


# ----------------------------------------------------------------------------
# szybka kontrola skanu
# ----------------------------------------------------------------------------
def rozpoznaj_uklad(siatka, ust: dict, numer: int | None = None) -> dict:
    """Do ktorego ukladu plytki z ``[plytki]`` pasuje siatka skanu - JEDYNA funkcja rozpoznania ukladu w tym module.

    Od 16.11.2026 wola automatyczne rozpoznanie programu (``plate.rozpoznaj_uklad``: rozstaw stozkow -> wieczorna /
    poranna i R59 / R54, numer plytki albo ksztalt brzegu -> kwadrat / kolo), to samo co ``porownaj --plytka auto``.

    Zwraca slownik:
      ``uklad``         - nazwa ukladu albo None,
      ``wyrownanie``    - ``plate.WynikWyrownania`` dla tego ukladu albo None,
      ``obiekt_ukladu`` - ``uklad.UkladPlytki`` albo None,
      ``kandydaci``     - pierwszy = wybrany; dalsze tylko przy rozpoznaniu niepewnym (pasuja rownie dobrze),
      ``pewny``         - czy rozpoznanie jest pewne (``plate.rozpoznaj_uklad``),
      ``powod``         - "" gdy rozpoznano; inaczej: ``brak_plaszczyzny`` | ``malo_stozkow`` | ``zaden_uklad`` | ``blad``,
      ``komunikat``     - tekst bledu z plate (do logu i raportu),
      ``stozki``        - liczba dopasowanych stozkow, gdy znana (inaczej None),
      ``proby``         - lista {uklad, wynik, komunikat, czas_s} dla kazdego ukladu z ustawien.
    """
    import warnings

    from . import plate as PL
    from . import porownaj as PO

    t0 = time.time()
    uklady = PO.uklady_z_ustawien(ust)
    proby = [{"uklad": n, "wynik": "blad_ukladu", "komunikat": "nie da sie wczytac ukladu", "czas_s": 0.0} for n in ust["plytki"] if n not in uklady]

    def z_kandydatow(kandydaci: list) -> list:
        out = []
        for k in kandydaci:
            odrz = k.get("odrzucony")
            wynik = "ok" if not odrz else ("pominiety" if odrz == "stozki" else "blad_wyrownania" if str(odrz).startswith("blad") else "niezgodny_" + str(odrz))
            kom = "rozstaw stozkow w skanie nie pasuje do tego ukladu" if odrz == "stozki" else ("" if not odrz else str(odrz))
            out.append({"uklad": k["uklad"], "wynik": wynik, "komunikat": kom, "czas_s": 0.0})
        return out

    if not uklady:
        return {"uklad": None, "wyrownanie": None, "obiekt_ukladu": None, "kandydaci": [], "pewny": False, "powod": "blad",
                "komunikat": "brak ukladow plytek w ustawieniach", "stozki": None, "proby": proby}
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            w, info = PL.rozpoznaj_uklad(siatka, list(uklady.values()), numer=numer)
    except PL.NierozpoznanyUklad as e:
        return {"uklad": None, "wyrownanie": None, "obiekt_ukladu": None, "kandydaci": [], "pewny": False, "powod": "zaden_uklad",
                "komunikat": str(e), "stozki": e.jakosc.get("stozki_dopasowane"), "proby": proby + z_kandydatow(e.kandydaci)}
    except PL.BladWyrownania as e:
        tekst = str(e).lower()
        powod = "malo_stozkow" if "sto" in tekst and "znacznik" in tekst else "brak_plaszczyzny" if ("wierzch" in tekst or "punkt" in tekst) else "blad"
        znal = re.search(r"znaleziono (\d+)", tekst)
        return {"uklad": None, "wyrownanie": None, "obiekt_ukladu": None, "kandydaci": [], "pewny": False, "powod": powod, "komunikat": str(e),
                "stozki": int(znal.group(1)) if znal and powod == "malo_stozkow" else None,
                "proby": proby + [{"uklad": "*", "wynik": "blad_wyrownania", "komunikat": str(e), "czas_s": round(time.time() - t0, 2)}]}
    except Exception as e:  # noqa: BLE001 - blad rozpoznania nie moze zatrzymac kontroli
        return {"uklad": None, "wyrownanie": None, "obiekt_ukladu": None, "kandydaci": [], "pewny": False, "powod": "blad",
                "komunikat": f"{type(e).__name__}: {e}", "stozki": None,
                "proby": proby + [{"uklad": "*", "wynik": "wyjatek", "komunikat": f"{type(e).__name__}: {e}", "czas_s": round(time.time() - t0, 2)}]}
    proby += z_kandydatow(info["kandydaci"])
    for pr in proby:
        if pr["uklad"] == info["wybrany"]:
            pr["czas_s"] = info["czas_s"]
    inne = [k["uklad"] for k in info["kandydaci"] if not k.get("odrzucony") and k["uklad"] != info["wybrany"]]
    return {"uklad": info["wybrany"], "wyrownanie": w, "obiekt_ukladu": uklady[info["wybrany"]],
            "kandydaci": [info["wybrany"]] + ([] if info["pewny"] else inne), "pewny": info["pewny"], "powod": "", "komunikat": "",
            "stozki": w.jakosc.get("stozki_dopasowane"), "proby": proby}


def _odstep(pole: float, wierzcholkow: int) -> float | None:
    """Sredni odstep punktow w sensie T10: liczba punktow = pole / d^2."""
    return float(math.sqrt(pole / wierzcholkow)) if wierzcholkow > 0 and pole > 0 else None


def _kontrola_siatki(plik: Path, ust: dict | None, numer: int | None, wynik: dict) -> None:
    import numpy as np
    import trimesh

    roz = plik.suffix.lower()
    if roz == ".stl":
        kompletny = stl_binarny_kompletny(plik)
        wynik["format"] = "STL tekstowy" if kompletny is None else "STL binarny"
        if kompletny is False:
            wynik["blad_kod"] = "niepelny_stl"
            return
    else:
        wynik["format"] = roz.lstrip(".").upper()
    try:
        m = trimesh.load(_io(plik), force="mesh")  # _io: takze sciezki dluzsze niz 260 znakow (gleboki folder zlecenia)
    except Exception as e:  # noqa: BLE001
        wynik["blad_kod"], wynik["blad"] = "nieczytelny", f"{type(e).__name__}: {e}"
        return
    trojkaty = len(getattr(m, "faces", ()))
    wynik["wierzcholki"] = int(len(getattr(m, "vertices", ())))
    wynik["trojkaty"] = int(trojkaty)
    if not isinstance(m, trimesh.Trimesh) or trojkaty == 0:
        wynik["blad_kod"] = "bez_trojkatow"
        return
    wynik["obrys_mm"] = [round(float(v), 2) for v in (m.bounds[1] - m.bounds[0])]
    pola = np.asarray(m.area_faces)
    wynik["pole_mm2"] = round(float(pola.sum()), 1)
    wynik["odstep_mm"] = _odstep(float(pola.sum()), len(m.vertices))
    if ust is None:
        wynik["blad_kod"] = "brak_ustawien"
        return
    r = rozpoznaj_uklad(m, ust, numer)
    wynik["proby"] = r["proby"]
    if r["uklad"] is None:
        wynik["plytka"] = {"cala": False, "powod": r["powod"], "komunikat": r["komunikat"], "stozki": r["stozki"]}
        return
    w, uk = r["wyrownanie"], r["obiekt_ukladu"]
    T = np.asarray(w.macierz, dtype=float)
    P = np.asarray(m.vertices) @ T[:3, :3].T + T[:3, 3]
    F = np.asarray(m.faces)
    plytka = {"cala": True, "uklad": r["uklad"], "kandydaci": r["kandydaci"], "ksztalt": uk.shape, "numery_ukladu": list(uk.numery),
              "numer": w.numer, "numer_zrodlo": w.numer_zrodlo, "numer_z_dolkow": w.numer_z_dolkow, "bity": list(w.bity)}
    for k in ("plaszczyzna_rms_mm", "stozki_dopasowane", "znaczniki_reszta_mm", "icp_fitness", "icp_rmse_mm",
              "uklad_zgodny", "uklad_gniazdo_nad_pelnym_mm2", "uklad_dziura_w_pelnym_mm2"):
        plytka[k] = w.jakosc.get(k)
    # odstep punktow osobno na plaskim wierzchu plytki i na pracach (lista pomiarow na dzien testu, pkt 1)
    na_wierzchu = np.abs(P[:, 2] - uk.thickness) < 0.1
    nad = P[:, 2] > uk.thickness + 0.3
    for nazwa, maska in (("odstep_wierzch_mm", na_wierzchu), ("odstep_prace_mm", nad)):
        tr = maska[F].all(axis=1)
        plytka[nazwa] = _odstep(float(pola[tr].sum()), int(np.unique(F[tr]).size)) if tr.any() else None
    prace = [f for f in w.fragmenty if f.status in ("praca", "podwojny")]
    poza = [f for f in w.fragmenty if f.status == "poza_gniazdem"]
    na_stozkach = [f for f in poza if any(math.hypot(f.srodek[0] - z.x, f.srodek[1] - z.y) < z.d / 2 + 2.0 for z in uk.markers)]
    plytka.update({
        "prace": len(prace), "gniazda_zajete": sorted({f.gniazdo for f in prace if f.gniazdo is not None}),
        "podwojne": list(w.gniazda_podwojne), "poza_gniazdem": len(poza) - len(na_stozkach), "poza_na_stozkach": len(na_stozkach),
        "drobne": sum(1 for f in w.fragmenty if f.status == "drobny"), "liczba_gniazd": len(uk.sockets),
        "fragmenty": [{"gniazdo": f.gniazdo, "status": f.status, "srodek": [round(float(v), 3) for v in f.srodek], "punkty": int(f.liczba),
                       "rozmiar_mm": [round(float(v), 2) for v in f.bbox()]} for f in w.fragmenty],
        "macierz": T.tolist(), "jakosc": w.jakosc,
    })
    wynik["plytka"] = plytka


def werdykt_pliku(w: dict) -> dict:
    """Ocena pliku prostym jezykiem: ``werdykt`` zielony | zolty | czerwony, ``uwagi``, ``zrob_tak``, ``informacje``."""
    uwagi, zrob, info = [], [], []
    kolor = "zielony"
    kod = w.get("blad_kod")
    p = w.get("plytka")
    if w.get("trojkaty"):
        info.append(f"{w['trojkaty'] / 1e6:.2f} mln trójkątów".replace(".", ",") if w["trojkaty"] >= 100000 else f"{w['trojkaty']} trójkątów")
    if w.get("obrys_mm"):
        info.append("obrys " + " × ".join(_l(v, 1) for v in w["obrys_mm"]) + " mm")
    if w.get("odstep_mm"):
        info.append(f"średni odstęp punktów {_l(w['odstep_mm'], 3)} mm")
    if kod == "niepelny_stl":
        kolor = "czerwony"
        uwagi.append("plik STL jest ucięty (rozmiar nie zgadza się z liczbą trójkątów w nagłówku) — zapis został przerwany albo program skanera jeszcze go nie skończył")
        zrob.append("poczekaj, aż program skanera skończy zapis, i wyeksportuj plik jeszcze raz (pod inną nazwą)")
    elif kod == "nieczytelny":
        kolor = "czerwony"
        uwagi.append(f"pliku nie da się wczytać ({w.get('blad', 'nieznany błąd')})")
        zrob.append("wyeksportuj skan jeszcze raz; jeśli program pozwala wybrać format, wybierz STL")
    elif kod == "bez_trojkatow":
        kolor = "czerwony"
        uwagi.append("w pliku nie ma trójkątów (sama chmura punktów albo pusty plik)")
        zrob.append("wyeksportuj skan jako siatkę (STL)")
    elif kod == "wyjatek":
        kolor = "zolty"
        uwagi.append(f"kontrola nie udała się ({w.get('blad', 'nieznany błąd')}) — plik jest zachowany, kontrolę powtórzy koordynator")
    elif kod == "brak_ustawien":
        kolor = "zolty"
        uwagi.append("nie sprawdzono, czy to cała płytka — program nie wczytał pliku ustawień (plik skanu jest zachowany)")
    elif p is not None and not p.get("cala"):
        kolor = "czerwony"
        powod = p.get("powod")
        if powod == "brak_plaszczyzny":
            uwagi.append("w pliku nie widać płaskiego wierzchu płytki — to wygląda na samą pracę albo płytkę obciętą przy eksporcie")
            zrob.append("wyeksportuj jeszcze raz CAŁĄ płytkę; płaszczyzny cięcia nie ustawiaj powyżej wierzchu płytki (ma zostać cały wierzch ze stożkami)")
        elif powod == "malo_stozkow":
            ile = p.get("stozki")
            uwagi.append("na płytce nie widać trzech stożków znaczników" + (f" (znaleziono {ile})" if ile is not None else ""))
            zrob.append("sprawdź, czy stożki w rogach płytki są czyste i niczym nie zasłonięte, czy cała płytka mieści się w polu skanera "
                        "i czy w programie skanera nie wypełniono otworów ani nie obcięto płytki; potem zeskanuj ponownie")
        elif powod == "zaden_uklad":
            uwagi.append("płytka nie pasuje do żadnego układu z ustawień (stożki są, ale w innych miejscach albo gniazda leżą inaczej)")
            zrob.append("oczyść stożki znaczników i zeskanuj ponownie; jeśli to inna płytka niż zwykle, zapisz w notatce, która")
        else:
            uwagi.append("nie udało się rozpoznać płytki w tym pliku")
            zrob.append("zeskanuj ponownie całą płytkę; jeśli znów się nie uda, zapisz w notatce, co było na płytce")
    elif p is not None:
        info.insert(0, f"cała płytka, układ {p['uklad']}")
        if p.get("numer_zrodlo") == "dolki" and p.get("numer") in p.get("numery_ukladu", []):
            info.append(f"numer płytki z dołków: {p['numer']}")
        elif p.get("numer_z_dolkow") is not None:
            info.append(f"dołki kodu odczytane jako {p['numer_z_dolkow']} — to nie jest numer płytki tego układu (wpisz numer płytki w polu kroku)")
        else:
            info.append("numeru płytki nie widać w skanie (dołki poza polem skanera) — wpisz numer płytki w polu kroku")
        if len(p.get("kandydaci", [])) > 1:
            info.append("pasuje też do: " + ", ".join(p["kandydaci"][1:]))
        info.append(f"prac na płytce: {p['prace']}" + (f" (gniazda {', '.join(map(str, p['gniazda_zajete']))})" if p["gniazda_zajete"] else ""))
        rms = p.get("plaszczyzna_rms_mm")
        if rms is not None:
            ocena = "dobry" if rms <= PROG_SZUMU_DOBRY_MM else "średni" if rms <= PROG_SZUMU_SLABY_MM else "duży"
            info.append(f"szum na płaskiej części {_l(rms, 3)} mm ({ocena})")
            if rms > PROG_SZUMU_UWAGA_MM:
                kolor = "zolty"
                uwagi.append(f"bardzo duży szum na płaskiej części płytki ({_l(rms, 3)} mm) — sprawdź, czy płytka albo skaner nie drgały; warto zeskanować jeszcze raz")
        if p.get("odstep_prace_mm"):  # gestosc to cecha skanera i ustawien, nie blad tego skanu: informacja, nie zmienia koloru
            rzadko = p["odstep_prace_mm"] > PROG_ODSTEPU_RZADKI_MM
            info.append(f"odstęp punktów na pracach {_l(p['odstep_prace_mm'], 3)} mm"
                        + (" (rzadko — jeśli program skanera ma wyższą jakość skanu albo eksportu, zrób też taki skan w kroku „zapisany inaczej”)" if rzadko else ""))
        if p.get("poza_gniazdem"):
            kolor = "zolty"
            uwagi.append(f"{p['poza_gniazdem']} obiekt(y) leżą poza gniazdami płytki — sprawdź, czy tak miało być")
        if p.get("poza_na_stozkach"):  # stozek w skanie rozni sie od modelu plytki: wazne dla programu, ale skan i tak sie przyda
            info.append(f"w miejscu {p['poza_na_stozkach']} stożka(ów) znaczników skan różni się od modelu płytki (informacja dla koordynatora, nie błąd skanu)")
        if p.get("podwojne"):
            kolor = "zolty"
            uwagi.append("dwie prace w jednym gnieździe: " + ", ".join(map(str, p["podwojne"])))
        if w.get("trojkaty", 0) < MIN_TROJKATOW:
            kolor = "zolty"
            uwagi.append("bardzo mało trójkątów jak na skan całej płytki — sprawdź, czy eksport nie był uproszczony")
    if w.get("format") == "STL tekstowy":
        info.append("STL tekstowy (większy plik, to nie błąd)")
    if kolor == "zielony":
        tytul = "Skan dobry" if p is not None else "Plik zachowany"
    elif kolor == "zolty":
        tytul = "Uwaga"
    else:
        tytul = "Ten skan się nie nada"
    return {"werdykt": kolor, "tytul": tytul, "uwagi": uwagi, "zrob_tak": zrob, "informacje": info}


def kontrola_pliku(plik, ust: dict | None, numer: int | None = None) -> dict:
    """Szybka kontrola jednego pliku siatki (STL / PLY / OBJ). Nigdy nie rzuca wyjatku - blad trafia do wyniku."""
    plik = Path(plik)
    t0 = time.time()
    wynik: dict = {"wersja_kontroli": 1, "plik": plik.name, "format": None, "trojkaty": None, "wierzcholki": None, "plytka": None}
    try:
        wynik["rozmiar"] = os.stat(_io(plik)).st_size
        _kontrola_siatki(plik, ust, numer, wynik)
    except BaseException as e:  # noqa: BLE001 - takze MemoryError: kontrola nie moze niczego zatrzymac
        if isinstance(e, (KeyboardInterrupt, SystemExit)):
            raise
        wynik["blad_kod"], wynik["blad"] = "wyjatek", f"{type(e).__name__}: {e}"
        wynik["slad"] = traceback.format_exc()
    wynik["czas_s"] = round(time.time() - t0, 2)
    wynik.update(werdykt_pliku(wynik))
    return _czysty(wynik)


def porownaj_skany(odn: dict, nowy: dict) -> dict:
    """Porownanie dwoch wynikow kontroli (odniesienie, nowy skan): czy to naprawde ten sam uklad prac.

    Liczy sie polozenie prac wzgledem plytki (srodki fragmentow w ukladzie plytki). Roznica polozenia calej plytki
    w ukladzie skanera jest tylko informacja - program skanera moze ustawiac model po swojemu przy kazdym skanie.
    """
    wynik: dict = {"z_plikiem": odn.get("plik"), "porownywalne": False}
    pa, pb = odn.get("plytka") or {}, nowy.get("plytka") or {}
    wynik["trojkaty"] = [odn.get("trojkaty"), nowy.get("trojkaty")]
    wynik["odstep_mm"] = [odn.get("odstep_mm"), nowy.get("odstep_mm")]
    if not (pa.get("cala") and pb.get("cala")):
        return wynik
    wynik["porownywalne"] = True
    wynik["ten_sam_uklad"] = pa.get("uklad") == pb.get("uklad")
    wynik["uklady"] = [pa.get("uklad"), pb.get("uklad")]

    def prace(p):
        return {f["gniazdo"]: f for f in p.get("fragmenty", []) if f.get("gniazdo") is not None and f.get("status") in ("praca", "podwojny")}

    ga, gb = prace(pa), prace(pb)
    wynik["tylko_w_odniesieniu"] = sorted(set(ga) - set(gb))
    wynik["tylko_w_nowym"] = sorted(set(gb) - set(ga))
    wspolne = sorted(set(ga) & set(gb))
    wynik["wspolne_gniazda"] = wspolne
    przes = {g: math.dist(ga[g]["srodek"], gb[g]["srodek"]) for g in wspolne}
    wynik["przesuniecia_mm"] = {str(g): round(v, 3) for g, v in przes.items()}
    wynik["przesuniecie_max_mm"] = round(max(przes.values()), 3) if przes else None
    wynik["gniazdo_max"] = max(przes, key=przes.get) if przes else None
    wynik["rms_mm"] = [pa.get("plaszczyzna_rms_mm"), pb.get("plaszczyzna_rms_mm")]
    try:
        import numpy as np

        Ta, Tb = np.array(pa["macierz"], dtype=float), np.array(pb["macierz"], dtype=float)
        M = np.linalg.inv(Tb) @ Ta  # ruch plytki w ukladzie skanera miedzy skanami
        srodek = np.linalg.inv(Ta) @ np.array([0.0, 0.0, 0.0, 1.0])
        wynik["ruch_plytki_mm"] = round(float(np.linalg.norm((M @ srodek)[:3] - srodek[:3])), 3)
        wynik["obrot_plytki_deg"] = round(math.degrees(math.acos(max(-1.0, min(1.0, (np.trace(M[:3, :3]) - 1) / 2)))), 3)
    except Exception:  # noqa: BLE001 - informacja dodatkowa
        wynik["ruch_plytki_mm"] = wynik["obrot_plytki_deg"] = None
    return wynik


def ocen_w_kroku(krok: Krok | None, wynik: dict, odniesienie: dict | None = None, sha_nowy: str | None = None, sha_odn: str | None = None) -> dict:
    """Dopisuje do wyniku kontroli oczekiwania kroku (pusta plytka, plytka z pracami, powtorka ...); zwraca skrot do manifestu."""
    kolor = wynik.get("werdykt", "zolty")
    uwagi, zrob, info = list(wynik.get("uwagi", [])), list(wynik.get("zrob_tak", [])), list(wynik.get("informacje", []))
    p = wynik.get("plytka") or {}
    porownanie = None

    def podnies(nowy: str) -> None:
        nonlocal kolor
        if KOLEJNOSC_WERDYKTOW[nowy] > KOLEJNOSC_WERDYKTOW[kolor]:
            kolor = nowy

    rodzaj = krok.kontrola if krok is not None else "brak"
    if p.get("cala"):
        if rodzaj == "plytka_pusta" and p.get("prace", 0) > 0:
            podnies("zolty")
            uwagi.append(f"to miała być PUSTA płytka, a program widzi na niej {p['prace']} obiekt(y) (gniazda {', '.join(map(str, p.get('gniazda_zajete', [])))}) — "
                         "jeśli płytka była pusta, zapisz to w notatce (to ważna informacja o skanerze)")
        if rodzaj in ("plytka_z_pracami", "powtorka", "inny_eksport", "ta_sama_plytka") and p.get("prace", 0) == 0:
            podnies("zolty")
            uwagi.append("program nie widzi na płytce żadnej pracy — sprawdź, czy prace leżały w gniazdach i czy to właściwy plik")
    if rodzaj in ("powtorka", "inny_eksport", "ta_sama_plytka") and odniesienie is not None:
        porownanie = porownaj_skany(odniesienie, wynik)
        nazwa = odniesienie.get("plik")
        if sha_nowy and sha_nowy == sha_odn:
            if rodzaj == "powtorka":
                podnies("czerwony")
                uwagi.append(f"to jest dokładnie TEN SAM plik co „{nazwa}” (identyczna zawartość), a nie drugi skan")
                zrob.append("zeskanuj płytkę jeszcze raz (bez ruszania) i zapisz wynik pod inną nazwą albo w nowym zleceniu")
            else:
                podnies("zolty")
                uwagi.append(f"plik ma identyczną zawartość jak „{nazwa}” — zmiana ustawień nic nie zmieniła albo zapisano ten sam plik")
        elif porownanie["porownywalne"]:
            if not porownanie["ten_sam_uklad"]:
                podnies("zolty")
                uwagi.append(f"inna płytka niż w skanie „{nazwa}” (układ {porownanie['uklady'][1]}, tam {porownanie['uklady'][0]})")
            elif rodzaj == "ta_sama_plytka":
                zm = porownanie["tylko_w_odniesieniu"] + porownanie["tylko_w_nowym"]
                info.append("względem skanu „%s”: " % nazwa + (f"zmiana w gniazdach {', '.join(map(str, sorted(zm)))}" if zm else "te same gniazda zajęte"))
            else:
                rozne = porownanie["tylko_w_odniesieniu"] or porownanie["tylko_w_nowym"]
                if rozne:
                    podnies("zolty")
                    uwagi.append(f"inne gniazda zajęte niż w skanie „{nazwa}” (tylko tam: {porownanie['tylko_w_odniesieniu'] or '-'}, tylko tu: "
                                 f"{porownanie['tylko_w_nowym'] or '-'}) — czy płytka na pewno nie była ruszana?")
                elif porownanie["przesuniecie_max_mm"] is not None and porownanie["przesuniecie_max_mm"] > PROG_PRZESUNIECIA_PRACY_MM:
                    podnies("zolty")
                    uwagi.append(f"praca w gnieździe {porownanie['gniazdo_max']} leży o {_l(porownanie['przesuniecie_max_mm'])} mm inaczej niż w skanie „{nazwa}” — "
                                 "chyba została ruszona; do pomiaru powtarzalności potrzebny jest skan bez ruszania")
                else:
                    info.append(f"ten sam układ prac co w skanie „{nazwa}”: {len(porownanie['wspolne_gniazda'])} prac w tych samych gniazdach"
                                + (f", największa różnica położenia {_l(porownanie['przesuniecie_max_mm'])} mm" if porownanie["przesuniecie_max_mm"] is not None else ""))
                if rodzaj == "inny_eksport" and all(porownanie["trojkaty"]):
                    info.append(f"trójkątów {porownanie['trojkaty'][1]} (tam {porownanie['trojkaty'][0]})")
            if porownanie.get("ruch_plytki_mm") is not None and rodzaj != "ta_sama_plytka":
                info.append(f"położenie płytki w układzie skanera różni się o {_l(porownanie['ruch_plytki_mm'])} mm / {_l(porownanie['obrot_plytki_deg'])}°")
        else:
            info.append(f"nie porównano ze skanem „{nazwa}” (w jednym z plików nie rozpoznano płytki)")
    elif rodzaj in ("powtorka", "inny_eksport") and odniesienie is None:
        info.append("nie ma jeszcze skanu odniesienia z wcześniejszego kroku — porównanie pominięte")
    tytul = {"zielony": "Skan dobry" if p.get("cala") else "Plik zachowany", "zolty": "Uwaga", "czerwony": "Ten skan się nie nada"}[kolor]
    return {
        "werdykt": kolor, "tytul": tytul, "uwagi": uwagi, "zrob_tak": zrob, "informacje": info, "tekst": tekst_werdyktu(kolor, tytul, uwagi, zrob, info),
        "trojkaty": wynik.get("trojkaty"), "odstep_mm": wynik.get("odstep_mm"), "obrys_mm": wynik.get("obrys_mm"), "format": wynik.get("format"),
        "cala_plytka": bool(p.get("cala")), "uklad": p.get("uklad"), "kandydaci": p.get("kandydaci"), "numer": p.get("numer"), "numer_zrodlo": p.get("numer_zrodlo"),
        "bity": p.get("bity"), "prace": p.get("prace"), "gniazda_zajete": p.get("gniazda_zajete"), "plaszczyzna_rms_mm": p.get("plaszczyzna_rms_mm"),
        "stozki_dopasowane": p.get("stozki_dopasowane") if p.get("cala") else p.get("stozki"), "znaczniki_reszta_mm": p.get("znaczniki_reszta_mm"),
        "odstep_wierzch_mm": p.get("odstep_wierzch_mm"), "odstep_prace_mm": p.get("odstep_prace_mm"), "czas_s": wynik.get("czas_s"),
        "porownanie": porownanie, "krok_kontroli": rodzaj, "kiedy": teraz_iso(),
    }


def tekst_werdyktu(kolor: str, tytul: str, uwagi: list, zrob: list, info: list) -> str:
    """Jedno-dwa zdania dla czlowieka: zielone "skan dobry", zolte "uwaga: ...", czerwone "... sie nie nada, bo ... - zrob tak: ..."."""
    if kolor == "zielony":
        return f"{tytul.upper()}: " + "; ".join(info) + "."
    if kolor == "zolty":
        return "UWAGA: " + "; ".join(uwagi) + ". Plik jest zachowany." + (" (" + "; ".join(info) + ")" if info else "")
    return ("TEN SKAN SIĘ NIE NADA, bo " + "; ".join(uwagi) + ". ZRÓB TAK: " + "; ".join(zrob) + ". Plik i tak jest zachowany — niczego nie kasuj."
            + (" (" + "; ".join(info) + ")" if info else ""))


# ----------------------------------------------------------------------------
# zbieracz: obserwacja folderow, kopiowanie, kolejka kontroli
# ----------------------------------------------------------------------------
def pliki_w_folderze(korzen: Path, pomijaj: tuple = (), niedostepne: list | None = None):
    """Wszystkie pliki pod ``korzen`` (bez podazania za dowiazaniami): (sciezka wzgledna posix, rozmiar, mtime_ns).
    Katalogi z ``pomijaj`` (sciezki bezwzgledne) sa omijane - folder sesji nigdy nie jest kopiowany do siebie.
    Katalogi i wpisy, ktorych nie da sie odczytac (brak uprawnien), sa pomijane; ich sciezki trafiaja do listy ``niedostepne``, gdy ja podano."""
    pomijaj = tuple(os.path.normcase(os.path.abspath(str(p))) for p in pomijaj)
    stos = [str(korzen)]
    baza = len(str(korzen).rstrip("\\/")) + 1
    while stos:
        kat = stos.pop()
        try:
            wpisy = list(os.scandir(kat))
        except OSError:
            if niedostepne is not None:
                niedostepne.append(kat)
            continue
        for e in wpisy:
            try:
                if e.is_dir(follow_symlinks=False):
                    if os.path.normcase(os.path.abspath(e.path)) not in pomijaj:
                        stos.append(e.path)
                elif e.is_file(follow_symlinks=False):
                    st = e.stat(follow_symlinks=False)
                    yield e.path[baza:].replace("\\", "/"), st.st_size, st.st_mtime_ns
            except OSError:
                if niedostepne is not None:
                    niedostepne.append(e.path)
                continue


class Zbieracz:
    """Zbiera pliki do sesji: odpytuje foldery obserwowane, kopiuje nowe i zmienione pliki do folderu biezacego kroku,
    obsluguje pliki dodane recznie i kolejke szybkiej kontroli. Jeden obieg = ``obieg()``; ``start()`` uruchamia obiegi
    w watku (zwykly watek Pythona - bez Open3D i bez Qt). Zdarzenia dla okna trafiaja do kolejki ``zdarzenia``.

    ``tryb_kontroli``: ``proces`` (osobny proces na kazdy skan - domyslnie), ``w_procesie`` (wywolanie wprost; testy),
    ``brak``.
    """

    def __init__(self, sesja: Sesja, ust: dict | None = None, plik_ustawien: Path | None = None, tryb_kontroli: str = "proces",
                 wolne=wolne_miejsce, grab=None, zegar=time.monotonic):
        self.sesja, self.ust, self.plik_ustawien = sesja, ust, plik_ustawien
        self.tryb_kontroli, self.wolne, self.grab, self.zegar = tryb_kontroli, wolne, grab, zegar
        self.zdarzenia: queue.Queue = queue.Queue()
        self._polecenia: queue.Queue = queue.Queue()
        self._stop = threading.Event()
        self._budzik = threading.Event()
        self._watek: threading.Thread | None = None
        self.znane: dict[str, dict[str, list]] = {}  # etykieta folderu -> sciezka wzgledna -> [rozmiar, mtime_ns] wersji juz obsluzonej
        self._kandydaci: dict[tuple, dict] = {}
        self._wersje: dict[tuple, int] = {}
        self._zglaszane: dict = {}
        self._istnieje: dict[str, bool] = {}
        self._kontrole: collections.deque = collections.deque()
        self._proces = None  # (Popen, id pliku, czas startu, plik wyniku, plik logu)
        self._ostatni_auto_zrzut = -1e9
        self._ostatni_zapis_znanych = 0.0
        self._znane_zalegle = False
        self._czas_przegladu = 0.0  # ile trwal ostatni przeglad folderow obserwowanych (bez kopiowania)
        self._po_wznowieniu = False
        self._wczytaj_znane()
        for k in stan_kopii_folderow(self.sesja.m):  # kopia calego folderu przerwana przed zamknieciem programu: okno ma o tym powiedziec
            if not k["pelna"]:
                self._zdarzenie("blad", tekst=f"Kopia całego folderu zleceń jest NIEPEŁNA (w sesji jest {k['jest']} z {k['plikow']} plików). "
                                              "Kliknij „Skopiuj cały folder zleceń skanera” jeszcze raz — skopiuję tylko brakujące pliki.")

    # --- stan obserwatora (trwaly: po wznowieniu sesji pliki, ktore pojawily sie w przerwie, sa nowe)
    def _wczytaj_znane(self) -> None:
        p = self.sesja.folder / PLIK_OBSERWATORA
        wczytane = None
        for nazwa in (p, Path(str(p) + ".bak")):
            try:
                wczytane = json.loads(Path(nazwa).read_text(encoding="utf-8"))
                break
            except (OSError, ValueError):
                continue
        juz_byla = bool(self.sesja.m["pliki"]) or len(self.sesja.m["zdarzenia"]) > 1
        if wczytane is not None:
            self.znane = {e: dict(v) for e, v in wczytane.get("znane", {}).items()}
            self._po_wznowieniu = juz_byla
        elif juz_byla:  # brak pliku stanu po awarii: znane = to, co juz jest w manifescie; reszta zostanie skopiowana
            for w in self.sesja.m["pliki"]:
                if w.get("folder") and w.get("wzgledna") and w.get("mtime_ns"):
                    self.znane.setdefault(w["folder"], {})[w["wzgledna"]] = [w["rozmiar"], w["mtime_ns"]]
            self._po_wznowieniu = True
            self.sesja.log("brak pliku stanu obserwatora - odtworzony z manifestu")
        for etykieta, sciezka in self.sesja.foldery():
            if etykieta not in self.znane:
                if juz_byla:
                    self.znane[etykieta] = {}  # sesja wznowiona bez stanu tego folderu: lepiej skopiowac za duzo
                else:
                    self._bazuj(etykieta, sciezka)
        if juz_byla:
            self._zapomnij_kopie_bez_wpisu()
        for w in self.sesja.m["pliki"]:
            if w.get("folder") and w.get("wzgledna"):
                klucz = (w["krok"], w["folder"], w["wzgledna"])
                self._wersje[klucz] = self._wersje.get(klucz, 0) + 1
            if w.get("kontrola") is None and w["rodzaj"] != "kopia_folderu" and Path(w["cel"]).suffix.lower() in ROZSZERZENIA_SIATEK:
                self._kontrole.append(w["id"])  # kontrola przerwana zamknieciem programu
        self._zapisz_znane(pilne=True)

    def _zapomnij_kopie_bez_wpisu(self) -> None:
        """Wznowienie: kopia lezaca w ``kroki/*/pliki/<folder>/`` bez wpisu w manifescie (awaria miedzy kopia a zapisem manifestu; wersja sprzed
        17.11.2026 mogla zapisac taki plik jako "znany") - zrodlo przestaje byc znane, wiec najblizszy przeglad podejmie je ponownie. Kopia bez
        wpisu jest wtedy zastepowana (``Sesja.cel_wolny``), wiec nie powstaje duplikat."""
        cele = {w["cel"].lower() for w in self.sesja.m["pliki"]}
        zapomniane = 0
        for rel, _, _ in pliki_w_folderze(self.sesja.folder / "kroki"):
            czesci = rel.split("/")
            if len(czesci) < 4 or czesci[1] != "pliki" or rel.endswith(".czesc") or f"kroki/{rel}".lower() in cele:
                continue
            wzgl = Path("/".join(czesci[3:]))
            bez_dopisku = (wzgl.parent / (re.sub(r"__(zmiana)?\d+$", "", wzgl.stem) + wzgl.suffix)).as_posix()  # kopia kolejnej wersji / duplikatu
            for kandydat in {wzgl.as_posix(), bez_dopisku}:
                if self.znane.get(czesci[2], {}).pop(kandydat, None) is not None:
                    zapomniane += 1
        if zapomniane:
            self.sesja.log(f"kopie bez wpisu w manifescie: {zapomniane} plik(ow) zrodlowych zostanie podjetych ponownie")

    def _zapisz_znane(self, pilne: bool = True) -> None:
        """Zapis stanu obserwatora. Plik moze byc "znany" na dysku dopiero wtedy, gdy jego wpis jest w ZAPISANYM manifescie - inaczej po awarii
        nie zostalby skopiowany ponownie, a w manifescie by go nie bylo. Dlatego przed kazdym zapisem stanu idzie zalegly zapis manifestu."""
        if not pilne and time.monotonic() - self._ostatni_zapis_znanych < OKRES_ZAPISU_ZBIORCZEGO_S:
            self._znane_zalegle = True
            return
        self.sesja.zapisz_zalegle()
        dane = json.dumps({"zapisano": teraz_iso(), "znane": self.znane}, ensure_ascii=False).encode("utf-8")
        zapisz_atomowo(self.sesja.folder / PLIK_OBSERWATORA, dane, kopia=True)
        self._ostatni_zapis_znanych = time.monotonic()
        self._znane_zalegle = False

    def _zapisz_zalegle(self) -> None:
        """Koniec serii: manifest i stan obserwatora odlozone w trakcie kopiowania wielu plikow trafiaja na dysk."""
        self.sesja.zapisz_zalegle()
        if self._znane_zalegle:
            self._zapisz_znane()

    def _pomijane(self) -> tuple:
        return (self.sesja.folder, self.sesja.folder.parent if self.sesja.folder.parent.name == KATALOG_SESJI.name else self.sesja.folder)

    def _bazuj(self, etykieta: str, sciezka: Path) -> int:
        """Pliki obecne w folderze w chwili dodania sa "zastane": nie sa kopiowane (dopoki sie nie zmienia)."""
        self.znane[etykieta] = {rel: [roz, mt] for rel, roz, mt in pliki_w_folderze(sciezka, self._pomijane())} if sciezka.is_dir() else {}
        return len(self.znane[etykieta])

    # --- polecenia z okna (wykonywane w watku zbieracza, zeby okno nie czekalo na kopiowanie)
    def _polecenie(self, *pol) -> None:
        self._polecenia.put(pol)
        self._budzik.set()

    def dodaj_folder(self, sciezka, skopiuj_istniejace: bool = False) -> None:
        self._polecenie("folder", str(sciezka), skopiuj_istniejace)

    def dodaj_recznie(self, sciezki: list, krok: str | None = None, rodzaj: str = "reczny") -> None:
        self._polecenie("reczne", [str(s) for s in sciezki], krok, rodzaj)

    def kopia_calych_folderow(self, krok: str | None = None) -> None:
        """Ostatni krok dnia: kopia CALEJ zawartosci wszystkich folderow obserwowanych do folderu kroku."""
        self._polecenie("kopia_folderow", krok)

    def zrzut(self, powod: str = "", krok: str | None = None) -> None:
        self._polecenie("zrzut", powod, krok)

    def spakuj(self) -> None:
        self._polecenie("spakuj")

    def powtorz_kontrole(self, id_pliku: int) -> None:
        self._polecenie("kontrola", id_pliku)

    # --- watek
    def start(self) -> None:
        if self._watek is None or not self._watek.is_alive():
            self._stop.clear()
            self._watek = threading.Thread(target=self._petla, name="zbieracz", daemon=True)
            self._watek.start()

    def stop(self, czekaj_s: float = 10.0) -> None:
        self._stop.set()
        self._budzik.set()
        if self._watek is not None:
            self._watek.join(czekaj_s)
        if self._proces is not None:
            try:
                self._proces[0].kill()
            except OSError:
                pass
            self._proces = None

    def _petla(self) -> None:
        while not self._stop.is_set():
            try:
                self.obieg()
            except BaseException as e:  # noqa: BLE001 - zaden wyjatek nie konczy zbierania
                self.sesja.log_wyjatku("zbieracz.obieg", e)
                self._zdarzenie("blad", tekst=f"Błąd wewnętrzny zbierania ({type(e).__name__}) — zapisany w log.txt, zbieranie trwa dalej.")
            # polecenie z okna (zrzut, dodanie pliku) budzi watek od razu; bardzo duzy folder (przeglad trwa dlugo) jest ogladany rzadziej
            self._budzik.wait(max(OKRES_ODPYTYWANIA_S, min(30.0, 4 * self._czas_przegladu)))
            self._budzik.clear()

    def _zdarzenie(self, typ: str, **dane) -> None:
        self.zdarzenia.put({"typ": typ, "czas": teraz_iso(), **dane})

    def _raz(self, klucz, okres_s: float = 30.0) -> bool:
        """True nie czesciej niz co ``okres_s`` dla danego klucza (zeby nie powtarzac tego samego komunikatu co obieg)."""
        t = self.zegar()
        if t - self._zglaszane.get(klucz, -1e9) >= okres_s:
            self._zglaszane[klucz] = t
            return True
        return False

    def obieg(self) -> None:
        """Jeden obieg: polecenia z okna, foldery obserwowane, kolejka kontroli."""
        self._obsluz_polecenia()
        self._odpytaj_foldery()
        self._obsluz_kontrole()

    # --- polecenia
    def _obsluz_polecenia(self) -> None:
        while True:
            try:
                pol = self._polecenia.get_nowait()
            except queue.Empty:
                return
            try:
                if pol[0] == "folder":
                    self._polecenie_folder(pol[1], pol[2])
                elif pol[0] == "reczne":
                    self._polecenie_reczne(pol[1], pol[2], pol[3])
                elif pol[0] == "kopia_folderow":
                    nazwy = {str(s): etykieta for etykieta, s in self.sesja.foldery() if s.is_dir()}  # etykiety sa rozne takze dla folderow o tej samej nazwie
                    if nazwy:
                        self._polecenie_reczne(list(nazwy), pol[1], "kopia_folderu", nazwy)
                    else:
                        self._zdarzenie("blad", tekst="Nie ma czego kopiować: żaden z obserwowanych folderów nie istnieje. Wskaż folder zleceń programu skanera.")
                elif pol[0] == "zrzut":
                    self._zrzut(pol[1], pol[2])
                elif pol[0] == "spakuj":
                    self._polecenie_spakuj()
                elif pol[0] == "kontrola":
                    self._kontrole.append(pol[1])
            except BaseException as e:  # noqa: BLE001
                self.sesja.log_wyjatku(f"polecenie {pol[0]}", e)
                self._zdarzenie("blad", tekst=f"Nie udało się: {pol[0]} ({type(e).__name__}: {e}). Szczegóły w log.txt; zbieranie trwa dalej.")

    def _polecenie_folder(self, sciezka: str, skopiuj_istniejace: bool) -> None:
        wpis = self.sesja.dodaj_folder(sciezka)
        if wpis is None:
            self._zdarzenie("info", tekst=f"Folder już jest obserwowany: {sciezka}")
            return
        p = rozwin_sciezke(wpis["sciezka"])
        if skopiuj_istniejace:
            self.znane[wpis["etykieta"]] = {}
            n = sum(1 for _ in pliki_w_folderze(p, self._pomijane())) if p.is_dir() else 0
        else:
            n = self._bazuj(wpis["etykieta"], p)
        self._zapisz_znane()
        self._zdarzenie("foldery", tekst=f"Obserwuję folder {p}" + (f" — {n} plików, które już w nim są, skopiuję teraz" if skopiuj_istniejace and n else
                                                                    f" — {n} plików sprzed dodania pomijam (trafią do kopii całego folderu na końcu)" if n else ""))

    def _polecenie_reczne(self, sciezki: list, krok: str | None, rodzaj: str, nazwy: dict | None = None) -> None:
        """Pliki i foldery wskazane recznie (takze przeciagniete na okno) oraz kopia calych folderow na koniec dnia.

        Kopia calych folderow (``rodzaj == "kopia_folderu"``) ma wpis w rejestrze ``kopie_folderow`` manifestu: ``w_toku`` przed pierwszym
        plikiem, na koncu liczby skopiowanych / bledow / pominietych i stan. Mozna ja ponowic: pliki, ktore ta sama kopia w tym kroku juz ma
        (to samo zrodlo, rozmiar i czas), nie sa kopiowane drugi raz. ``nazwy``: sciezka folderu -> nazwa katalogu w sesji (etykiety folderow
        obserwowanych); foldery o tej samej nazwie w jednej partii dostaja osobne katalogi (``<nazwa>_2``)."""
        krok = krok or self.sesja.biezacy
        kopia = rodzaj == "kopia_folderu"
        podkatalog = "kopia_folderu" if kopia else "reczne"
        lista = []  # (zrodlo, wzgledna w podkatalogu, rozmiar, mtime_ns)
        niedostepne: list[str] = []
        uzyte: set[str] = set()
        for s in sciezki:
            p = Path(s)
            if p.is_dir():
                baza = (nazwy or {}).get(s) or nazwa_bezpieczna(p.name or "dysk")
                nazwa, n = baza, 1
                while nazwa.lower() in uzyte:
                    n += 1
                    nazwa = f"{baza}_{n}"
                uzyte.add(nazwa.lower())
                for rel, roz, mtime_ns in pliki_w_folderze(p, self._pomijane(), niedostepne):
                    lista.append((p / rel, f"{nazwa}/{rel}", roz, mtime_ns))
            elif p.is_file():
                lista.append((p, p.name, p.stat().st_size, p.stat().st_mtime_ns))
            else:
                self._zdarzenie("blad", tekst=f"Nie ma takiego pliku ani folderu: {s}")
        for sciezka in niedostepne:
            self.sesja.log(f"nie da sie odczytac (pominiete w kopii): {sciezka}")
        do_kopii = lista
        if kopia:  # ponowienie / wznowienie: bez plikow, ktore kopia calego folderu w tym kroku juz ma
            mam = {(str(w.get("zrodlo") or "").lower(), w["rozmiar"], w.get("mtime_ns")) for w in self.sesja.m["pliki"] if w["rodzaj"] == rodzaj and w["krok"] == krok}
            do_kopii = [x for x in lista if (skroc_sciezke(x[0]).lower(), x[2], x[3]) not in mam]
        if not lista and not (kopia and niedostepne):
            return
        razem = sum(x[2] for x in do_kopii)
        rejestr = None
        if kopia:
            rejestr = self.sesja.rozpocznij_kopie_folderow(krok, sciezki, len(lista), sum(x[2] for x in lista), len(lista) - len(do_kopii), len(niedostepne))
        try:
            sprawdz_miejsce(self.sesja.folder, razem, self.wolne)  # komunikat PRZED kopiowaniem calej partii
        except BrakMiejsca as e:
            self.sesja.log(f"brak miejsca: reczne dodanie {len(do_kopii)} plikow, {razem} B, wolne {e.wolne} B")
            self._zdarzenie("brak_miejsca", tekst=str(e), potrzeba=e.potrzeba, wolne=e.wolne)
            if rejestr is not None:
                self.sesja.zakoncz_kopie_folderow(rejestr, 0, 0, len(do_kopii), "brak miejsca na dysku")
                self._zglos_niepelna_kopie(krok)
            return
        if not kopia:
            self.sesja.zdarzenie("dodano recznie", krok=krok, plikow=len(lista), bajtow=razem, zrodla=[skroc_sciezke(s) for s in sciezki])
        zrobione, skopiowane, bledy, powod = 0, 0, 0, ""
        for zrodlo, rel, roz, _ in do_kopii:
            if self._stop.is_set():
                powod = "zamykanie programu"
                break
            cel = self.sesja.cel_wolny(f"{self.sesja.folder_kroku(krok)}/{podkatalog}/{rel}")
            try:
                wyn = kopiuj_plik(zrodlo, self.sesja.sciezka(cel), postep=self._postep(Path(rel).name, zrobione, razem), przerwij=self._stop.is_set, wolne=self.wolne)
            except Przerwano:
                powod = "zamykanie programu"
                break
            except BrakMiejsca as e:
                powod = "brak miejsca na dysku"
                self._zdarzenie("brak_miejsca", tekst=str(e), potrzeba=e.potrzeba, wolne=e.wolne)
                break
            except OSError as e:
                bledy += 1
                self.sesja.log(f"nie skopiowano {zrodlo}: {type(e).__name__}: {e}")
                zrobione += roz
                continue
            zrobione += roz
            skopiowane += 1
            wpis = self.sesja.dodaj_plik(krok, rodzaj, cel, wyn["rozmiar"], wyn["sha256"], wyn["mtime_ns"], zrodlo=zrodlo, czas_kopii_s=wyn["czas_s"], pilne=len(do_kopii) < 20)
            self._po_skopiowaniu(wpis, kontrola=not kopia, cicho=len(do_kopii) >= 20)
        pominiete = len(do_kopii) - skopiowane - bledy
        if rejestr is not None:  # slad w manifescie takze po przerwaniu: skopiowane / bledy / pominiete (zapis na dysk)
            self.sesja.zakoncz_kopie_folderow(rejestr, skopiowane, bledy, pominiete, powod)
        elif bledy or pominiete:
            self.sesja.zdarzenie("dodano recznie: niepelne", krok=krok, plikow=len(lista), skopiowane=skopiowane, bledy=bledy, pominiete=pominiete, powod=powod)
        else:
            self.sesja.zapisz()
        juz = len(lista) - len(do_kopii)
        self._zdarzenie("partia", tekst=f"Skopiowano {skopiowane} z {len(do_kopii)} plików ({tekst_rozmiaru(razem)})" + (f"; {juz} już było w kopii" if juz else "")
                        + (f"; nie udało się: {bledy} (lista w log.txt)" if bledy else "") + (f"; nie zdążono: {pominiete} ({powod})" if pominiete else ""),
                        krok=krok, plikow=skopiowane, bledy=bledy, pominiete=pominiete)
        if rejestr is not None and rejestr["stan"] != "pelna":
            self._zglos_niepelna_kopie(krok)

    def _zglos_niepelna_kopie(self, krok: str) -> None:
        for k in stan_kopii_folderow(self.sesja.m, krok):
            self.sesja.log(f"kopia calych folderow NIEPELNA: {k}")
            self._zdarzenie("blad", tekst=f"Kopia całego folderu jest NIEPEŁNA: w sesji jest {k['jest']} z {k['plikow']} plików"
                                          + (f", nie udało się: {k['bledy']}" if k["bledy"] else "") + (f", nie zdążono: {k['pominiete']}" if k["pominiete"] else "")
                                          + (f", niedostępne podfoldery: {k['niedostepne_katalogi']}" if k["niedostepne_katalogi"] else "")
                                          + (f" ({k['powod']})" if k["powod"] else "") + ". Lista w log.txt. Gdy przeszkoda zniknie, kliknij "
                                          "„Skopiuj cały folder zleceń skanera” jeszcze raz — skopiuję tylko brakujące pliki.")

    def _postep(self, nazwa: str, przed: int = 0, razem: int | None = None):
        stan = {"t": 0.0}

        def postep(zrobione: int, rozmiar: int) -> None:
            t = time.monotonic()
            if t - stan["t"] >= 0.1 or zrobione >= rozmiar:
                stan["t"] = t
                self.zdarzenia.put({"typ": "postep", "plik": nazwa, "zrobione": przed + zrobione, "razem": razem if razem is not None else rozmiar})

        return postep

    def _po_skopiowaniu(self, wpis: dict, kontrola: bool = True, cicho: bool = False) -> None:
        if not cicho:
            self._zdarzenie("nowy_plik", wpis=wpis)
        if kontrola and Path(wpis["cel"]).suffix.lower() in ROZSZERZENIA_SIATEK:
            self._kontrole.append(wpis["id"])

    # --- foldery obserwowane
    def _odpytaj_foldery(self) -> None:
        """Jeden przeglad folderow: kopie plikow stabilnych; manifest i stan obserwatora zapisane najpozniej na koncu przegladu
        (w serii wielu plikow nie po kazdym pliku - na wolnym dysku kazdy zapis z fsync trwa)."""
        try:
            self._przeglad_folderow()
        finally:
            self._zapisz_zalegle()

    def _przeglad_folderow(self) -> None:
        teraz = self.zegar()
        widziane = set()
        czas_przegladu = 0.0
        pierwszy_po_wznowieniu, self._po_wznowieniu = self._po_wznowieniu, False
        for etykieta, korzen in self.sesja.foldery():
            istnieje = korzen.is_dir()
            if self._istnieje.get(etykieta) != istnieje:
                self._istnieje[etykieta] = istnieje
                self._zdarzenie("foldery", tekst=(f"Folder jest dostępny: {korzen}" if istnieje else f"Folder nie istnieje (jeszcze?): {korzen}"))
            if not istnieje:
                continue
            znane = self.znane.setdefault(etykieta, {})
            t0 = time.monotonic()
            lista = list(pliki_w_folderze(korzen, self._pomijane()))
            czas_przegladu += time.monotonic() - t0
            self._czas_przegladu = czas_przegladu
            for rel, rozmiar, mtime_ns in lista:
                klucz = (etykieta, rel)
                widziane.add(klucz)
                podpis = [rozmiar, mtime_ns]
                if znane.get(rel) == podpis:
                    self._kandydaci.pop(klucz, None)
                    continue
                k = self._kandydaci.get(klucz)
                if k is None or k["podpis"] != podpis:
                    # krok z chwili, gdy plik sie pojawil albo zmienil: plik trafia do tego kroku, nawet gdy czlowiek przejdzie dalej,
                    # zanim kopia sie skonczy (seria wielu plikow na wolnym dysku)
                    self._kandydaci[klucz] = {"podpis": podpis, "licznik": 1, "od": teraz, "bledy": 0, "po_wznowieniu": pierwszy_po_wznowieniu,
                                              "krok": self.sesja.biezacy}
                    continue
                k["licznik"] += 1
                if k["licznik"] >= STABILNE_ODCZYTY:
                    self._sprobuj_skopiowac(etykieta, korzen, rel, k, teraz)
                    if self._stop.is_set():
                        return
        for klucz in [k for k in self._kandydaci if k not in widziane]:
            del self._kandydaci[klucz]  # plik zniknal przed skopiowaniem (plik tymczasowy programu skanera)

    def _sprobuj_skopiowac(self, etykieta: str, korzen: Path, rel: str, k: dict, teraz: float) -> None:
        zrodlo = korzen / rel
        klucz = (etykieta, rel)
        try:
            if ktos_pisze(zrodlo):
                return  # program skanera jeszcze trzyma plik otwarty do zapisu
            st = os.stat(_io(zrodlo))
            if [st.st_size, st.st_mtime_ns] != k["podpis"]:
                self._kandydaci[klucz] = {**k, "podpis": [st.st_size, st.st_mtime_ns], "licznik": 1, "od": teraz}
                return
            if st.st_size == 0 and teraz - k["od"] < CZEKAJ_NA_PUSTY_S:
                return
            niepelny = zrodlo.suffix.lower() == ".stl" and stl_binarny_kompletny(zrodlo) is False
            if niepelny and teraz - k["od"] < CZEKAJ_NA_PELNY_STL_S:
                return
        except FileNotFoundError:
            self._kandydaci.pop(klucz, None)
            return
        except OSError as e:
            self._blad_pliku(klucz, k, zrodlo, e)
            return
        krok = k.get("krok") or self.sesja.biezacy
        nr = self._wersje.get((krok, etykieta, rel), 0)
        if nr >= LIMIT_WERSJI:
            self.znane[etykieta][rel] = k["podpis"]
            self._kandydaci.pop(klucz, None)
            if self._raz(("limit", krok, etykieta, rel), 3600.0):
                self.sesja.log(f"limit wersji ({LIMIT_WERSJI}) w kroku {krok}: {zrodlo}")
                self._zdarzenie("info", tekst=f"Plik {Path(rel).name} zmienia się raz po raz — mam już {LIMIT_WERSJI} jego wersji z tego kroku; kolejne skopiuję "
                                              "w następnym kroku i przy kopii całego folderu na końcu.")
            return
        p = Path(rel)
        wzgl = rel if nr == 0 else (p.parent / f"{p.stem}__zmiana{nr + 1}{p.suffix}").as_posix()
        cel = self.sesja.cel_wolny(f"{self.sesja.folder_kroku(krok)}/pliki/{etykieta}/{wzgl}")
        try:
            wyn = kopiuj_plik(zrodlo, self.sesja.sciezka(cel), postep=self._postep(p.name), przerwij=self._stop.is_set, wolne=self.wolne)
        except Przerwano:
            return
        except BrakMiejsca as e:
            if self._raz(("miejsce",), 20.0):
                self.sesja.log(f"brak miejsca: {zrodlo} ({e.potrzeba} B), wolne {e.wolne} B")
                self._zdarzenie("brak_miejsca", tekst=str(e), potrzeba=e.potrzeba, wolne=e.wolne, plik=p.name)
            return
        except ZrodloZmienione:
            self._kandydaci.pop(klucz, None)
            return
        except FileNotFoundError:
            self._kandydaci.pop(klucz, None)
            return
        except OSError as e:
            self._blad_pliku(klucz, k, zrodlo, e)
            return
        self.znane[etykieta][rel] = k["podpis"]
        self._kandydaci.pop(klucz, None)
        poprzednie = [w for w in self.sesja.m["pliki"] if w["krok"] == krok and w.get("folder") == etykieta and w.get("wzgledna") == rel]
        if poprzednie and poprzednie[-1]["sha256"] == wyn["sha256"]:
            try:  # ta sama tresc co poprzednia wersja w tym kroku (zmienil sie tylko czas pliku): usuwamy NASZA zbedna kopie
                os.unlink(_io(self.sesja.sciezka(cel)))
            except OSError:
                pass
            self._zapisz_znane(pilne=False)
            return
        self._wersje[(krok, etykieta, rel)] = nr + 1
        uwagi = []
        if nr:
            uwagi.append(f"zmieniona wersja pliku (nr {nr + 1} w tym kroku)")
        if k.get("po_wznowieniu"):
            uwagi.append("plik pojawil sie albo zmienil, gdy program byl zamkniety")
        if niepelny:
            uwagi.append("STL niepelny w chwili kopiowania (rozmiar niezgodny z naglowkiem)")
        wpis = self.sesja.dodaj_plik(krok, "obserwacja", cel, wyn["rozmiar"], wyn["sha256"], wyn["mtime_ns"], zrodlo=zrodlo, folder=etykieta, wzgledna=rel,
                                     czas_kopii_s=wyn["czas_s"], uwagi=uwagi, pilne=False)  # zapis najpozniej na koncu przegladu (_odpytaj_foldery)
        self._zapisz_znane(pilne=False)
        self._po_skopiowaniu(wpis)
        if self.sesja.m.get("auto_zrzut") and self.zegar() - self._ostatni_auto_zrzut >= OKRES_AUTO_ZRZUTU_S:
            self._ostatni_auto_zrzut = self.zegar()
            self._zrzut(f"automatyczny przy pliku {p.name}", krok)

    def _blad_pliku(self, klucz: tuple, k: dict, zrodlo: Path, e: OSError) -> None:
        k["bledy"] = k.get("bledy", 0) + 1
        if k["bledy"] in (3, 30, 300):
            self.sesja.log(f"nie moge odczytac {zrodlo} (proba {k['bledy']}): {type(e).__name__}: {e}")
            self._zdarzenie("blad", tekst=f"Nie mogę odczytać pliku {zrodlo.name} ({type(e).__name__}) — pewnie jest jeszcze zajęty przez program skanera. Próbuję dalej co chwilę.")

    def do_skopiowania(self) -> int:
        """Ile plikow czeka na ustabilizowanie albo skopiowanie (do paska stanu)."""
        return len(self._kandydaci)

    # --- zrzut ekranu
    def _zrzut(self, powod: str, krok: str | None) -> None:
        try:
            wpis = zrob_zrzut(self.sesja, krok, powod, self.grab)
        except BaseException as e:  # noqa: BLE001 - brak pulpitu, brak PIL itd. nie zatrzymuje zbierania
            self.sesja.log_wyjatku("zrzut ekranu", e)
            self._zdarzenie("blad", tekst=f"Zrzut ekranu nie udał się ({type(e).__name__}: {e}). Zrób zdjęcie ekranu telefonem i dodaj je przyciskiem „Dodaj plik”.")
            return
        self._zdarzenie("nowy_plik", wpis=wpis, zrzut=True)

    # --- pakowanie (w watku zbieracza: w tym czasie nic nie dopisuje sie do sesji)
    def _polecenie_spakuj(self) -> None:
        def postep(zrobione: int, razem: int, co: str) -> None:
            self.zdarzenia.put({"typ": "postep", "plik": co, "zrobione": zrobione, "razem": razem})

        # pliki "w drodze": plik, ktory pojawil sie tuz przed kliknieciem, ma trafic do paczki, a nie obok niej (przeglad, potem krotkie czekanie
        # na pliki jeszcze nieskopiowane; plik, ktory w tym czasie sie nie ustabilizuje, zostanie skopiowany po pakowaniu = "spakuj ponownie")
        t0 = time.monotonic()
        while not self._stop.is_set():
            self._odpytaj_foldery()
            if not self._kandydaci or time.monotonic() - t0 >= CZEKAJ_NA_PLIKI_PRZED_PAKOWANIEM_S:
                break
            if self._raz(("czekam_na_pliki",), 5.0):
                self._zdarzenie("info", tekst="Przed pakowaniem czekam na pliki, które właśnie pojawiły się w folderze skanera…")
            time.sleep(OKRES_ODPYTYWANIA_S)
        t0 = time.monotonic()
        while self.kontrola_w_toku() and not self._stop.is_set() and time.monotonic() - t0 < CZEKAJ_NA_KONTROLE_PRZED_PAKOWANIEM_S:
            self._obsluz_kontrole()  # raport ma miec oceny skanow; w trakcie pakowania wyniki kontroli nie sa dopisywane (ten sam watek)
            if self._raz(("czekam_na_kontrole",), 5.0):
                self._zdarzenie("info", tekst="Przed pakowaniem czekam na koniec sprawdzania skanów…")
            time.sleep(0.2)
        try:
            wynik = spakuj(self.sesja, postep=postep, wolne=self.wolne, przerwij=self._stop.is_set)
        except Przerwano:
            self.sesja.log("pakowanie przerwane: program jest zamykany")
            self._zdarzenie("spakowano", wynik=None, blad="pakowanie przerwane (zamykanie programu) — sesja nie jest oznaczona jako spakowana")
            return
        except BrakMiejsca as e:
            self._zdarzenie("brak_miejsca", tekst=str(e), potrzeba=e.potrzeba, wolne=e.wolne)
            self._zdarzenie("spakowano", wynik=None, blad=str(e))
            return
        except BaseException as e:  # noqa: BLE001
            self.sesja.log_wyjatku("spakuj", e)
            self._zdarzenie("spakowano", wynik=None, blad=f"{type(e).__name__}: {e}")
            return
        self._zdarzenie("spakowano", wynik=wynik, blad=None)

    # --- szybka kontrola
    def _obsluz_kontrole(self) -> None:
        if self.tryb_kontroli == "brak":
            self._kontrole.clear()
            return
        if self._proces is not None:
            proc, id_pliku, start, plik_wyniku, plik_logu = self._proces
            kod = proc.poll()
            if kod is None:
                if self.zegar() - start < LIMIT_KONTROLI_S:
                    return
                try:
                    proc.kill()
                except OSError:
                    pass
                wynik = self._wynik_awaryjny(id_pliku, f"kontrola trwała dłużej niż {LIMIT_KONTROLI_S:.0f} s i została przerwana")
            else:
                try:
                    wynik = json.loads(Path(plik_wyniku).read_text(encoding="utf-8"))
                except (OSError, ValueError) as e:
                    wynik = self._wynik_awaryjny(id_pliku, f"proces kontroli zakończył się kodem {kod} bez wyniku ({type(e).__name__})")
            self._proces = None
            self._zakoncz_kontrole(id_pliku, wynik)
        while self._kontrole and self._proces is None:
            id_pliku = self._kontrole.popleft()
            try:
                wpis = self.sesja.wpis(id_pliku)
            except KeyError:
                continue
            plik = self.sesja.sciezka(wpis["cel"])
            self._zdarzenie("kontrola_start", id=id_pliku, plik=Path(wpis["cel"]).name)
            if self.tryb_kontroli == "w_procesie":
                self._zakoncz_kontrole(id_pliku, kontrola_pliku(plik, self.ust, self._numer_z_pola(wpis["krok"])))
                continue
            try:
                self._uruchom_proces_kontroli(id_pliku, plik, wpis["krok"])
            except BaseException as e:  # noqa: BLE001
                self.sesja.log_wyjatku("start procesu kontroli", e)
                self._zakoncz_kontrole(id_pliku, self._wynik_awaryjny(id_pliku, f"nie udało się uruchomić kontroli ({type(e).__name__}: {e})"))

    def _numer_z_pola(self, krok: str) -> int | None:
        """Numer plytki wpisany przez czlowieka w polu kroku (kwadraty: dolki poza polem skanera)."""
        tekst = str(self.sesja.m["kroki"][krok]["pola"].get("numer_plytki", ""))
        znal = re.search(r"\d+", tekst)
        return int(znal.group()) if znal else None

    def _uruchom_proces_kontroli(self, id_pliku: int, plik: Path, krok: str) -> None:
        kat = self.sesja.sciezka("kontrole")
        os.makedirs(_io(kat), exist_ok=True)
        plik_wyniku, plik_logu = kat / f"k{id_pliku:04d}.json", kat / f"k{id_pliku:04d}.log"
        polecenie = [sys.executable, "-m", "stanowisko.dzien_skanera_rdzen", "--kontrola", str(plik), "--wynik", str(plik_wyniku)]
        if self.plik_ustawien is not None:
            polecenie += ["--ustawienia", str(self.plik_ustawien)]
        numer = self._numer_z_pola(krok)
        if numer is not None:
            polecenie += ["--numer", str(numer)]
        flagi = 0
        if os.name == "nt":
            flagi = subprocess.CREATE_NO_WINDOW  # bez okna konsoli
            if NIZSZY_PRIORYTET_KONTROLI:
                flagi |= subprocess.BELOW_NORMAL_PRIORITY_CLASS  # nie spowalnia programu skanera (gdy wszystkie rdzenie sa zajete, kontrola czeka)
        srodowisko = {**os.environ, "PYTHONUTF8": "1", "PYTHONPATH": os.pathsep.join([str(UST.KORZEN)] + [p for p in os.environ.get("PYTHONPATH", "").split(os.pathsep) if p])}
        with open(_io(plik_logu), "wb") as log:
            proc = subprocess.Popen(polecenie, cwd=str(UST.KORZEN), stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, creationflags=flagi, env=srodowisko)
        self._proces = (proc, id_pliku, self.zegar(), plik_wyniku, plik_logu)

    def _wynik_awaryjny(self, id_pliku: int, tekst: str) -> dict:
        self.sesja.log(f"kontrola pliku {id_pliku}: {tekst}")
        wynik = {"wersja_kontroli": 1, "plik": Path(self.sesja.wpis(id_pliku)["cel"]).name, "blad_kod": "wyjatek", "blad": tekst, "plytka": None, "trojkaty": None}
        wynik.update(werdykt_pliku(wynik))
        return wynik

    def _odniesienie(self, krok: Krok, id_pliku: int) -> tuple[dict | None, str | None]:
        """Pelny wynik kontroli skanu odniesienia: ostatni skan z kroku ``porownaj_z`` z rozpoznana plytka (albo ostatni w ogole)."""
        if not krok.porownaj_z:
            return None, None
        kandydaci = [w for w in self.sesja.m["pliki"] if w["krok"] == krok.porownaj_z and w["id"] != id_pliku and w.get("kontrola")
                     and Path(w["cel"]).suffix.lower() in ROZSZERZENIA_SIATEK]
        kandydaci.sort(key=lambda w: (bool(w["kontrola"].get("cala_plytka")), w["id"]))
        for w in reversed(kandydaci):
            try:
                return json.loads(self.sesja.sciezka(f"kontrole/k{w['id']:04d}.json").read_text(encoding="utf-8")), w["sha256"]
            except (OSError, ValueError):
                continue
        return None, None

    def _zakoncz_kontrole(self, id_pliku: int, wynik: dict) -> None:
        try:
            wpis = self.sesja.wpis(id_pliku)
            krok = self.sesja.krok(wpis["krok"])
            odn, sha_odn = self._odniesienie(krok, id_pliku)
            skrot = ocen_w_kroku(krok, wynik, odn, wpis["sha256"], sha_odn)
            kat = self.sesja.sciezka("kontrole")
            os.makedirs(_io(kat), exist_ok=True)
            zapisz_atomowo(kat / f"k{id_pliku:04d}.json", json.dumps(wynik, ensure_ascii=False, indent=1).encode("utf-8"))
            self.sesja.ustaw_kontrole(id_pliku, skrot)
            self.sesja.log(f"kontrola pliku {id_pliku} ({Path(wpis['cel']).name}): {skrot['werdykt']} w {wynik.get('czas_s')} s")
            self._zdarzenie("kontrola", id=id_pliku, wpis=wpis, kontrola=skrot)
        except BaseException as e:  # noqa: BLE001 - awaria kontroli nie zatrzymuje zbierania
            self.sesja.log_wyjatku("zakonczenie kontroli", e)
            self._zdarzenie("blad", tekst=f"Kontrola pliku nie udała się ({type(e).__name__}) — plik jest zachowany, zbieranie trwa dalej.")

    def kontrola_w_toku(self) -> bool:
        return self._proces is not None or bool(self._kontrole)


# ----------------------------------------------------------------------------
# szukanie plikow skanow, gdy nie wiadomo, gdzie program skanera zapisuje
# ----------------------------------------------------------------------------
KATALOGI_POMIJANE_PRZY_SZUKANIU = ("windows", "$recycle.bin", "system volume information", "$windows.~bt", "$windows.~ws", "recovery", "msocache")


def dyski() -> list[Path]:
    if os.name != "nt":
        return [Path("/")]
    return [Path(f"{litera}:\\") for litera in "CDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{litera}:\\")]


def szukaj_nowych_siatek(korzenie: list | None = None, od: float | None = None, przerwij=None, pomijaj: tuple = (), postep=None) -> list[dict]:
    """Foldery, w ktorych sa pliki STL / PLY / OBJ zmienione po czasie ``od`` (domyslnie: ostatnie 3 godziny).

    Zwraca liste {folder, plikow, najnowszy (czas), bajtow, przyklad} od najswiezszej. Tylko czyta listy plikow."""
    od = od if od is not None else time.time() - 3 * 3600
    pomin = tuple(os.path.normcase(os.path.abspath(str(p))) for p in pomijaj)
    znalezione: dict[str, dict] = {}
    stos = [str(k) for k in (korzenie if korzenie is not None else dyski())]
    przejrzane = 0
    while stos:
        if przerwij is not None and przerwij():
            break
        kat = stos.pop()
        try:
            wpisy = list(os.scandir(kat))
        except OSError:
            continue
        przejrzane += 1
        if postep is not None and przejrzane % 500 == 0:
            postep(przejrzane, kat)
        for e in wpisy:
            try:
                if e.is_dir(follow_symlinks=False):
                    if e.name.lower() in KATALOGI_POMIJANE_PRZY_SZUKANIU or os.path.normcase(os.path.abspath(e.path)) in pomin:
                        continue
                    stos.append(e.path)
                elif e.name.lower().endswith(ROZSZERZENIA_SIATEK) and e.is_file(follow_symlinks=False):
                    st = e.stat(follow_symlinks=False)
                    if st.st_mtime >= od:
                        z = znalezione.setdefault(kat, {"folder": kat, "plikow": 0, "najnowszy": 0.0, "bajtow": 0, "przyklad": e.name})
                        z["plikow"] += 1
                        z["bajtow"] += st.st_size
                        if st.st_mtime > z["najnowszy"]:
                            z["najnowszy"], z["przyklad"] = st.st_mtime, e.name
            except OSError:
                continue
    return sorted(znalezione.values(), key=lambda z: -z["najnowszy"])


# ----------------------------------------------------------------------------
# raport, sumy, archiwum
# ----------------------------------------------------------------------------
def plik_roboczy_programu(rel: str, w_manifescie=frozenset()) -> bool:
    """Czy ``rel`` (sciezka wzgledna w folderze sesji) to WLASNY plik roboczy programu, ktory nie trafia do sum ani do paczki:
    niedokonczona kopia ``*.czesc`` oraz ``.tmp`` / ``.bak`` zapisu atomowego (manifest, stan obserwatora, raport, sumy, wyniki kontroli).

    Plik obecny w manifescie nigdy nie jest roboczy: program skanera tez zapisuje ``*.bak`` i ``*.tmp``, a kopia calego folderu bierze wszystko."""
    if rel in w_manifescie:
        return False
    nazwa = rel.rsplit("/", 1)[-1]
    if nazwa.endswith(".czesc"):
        return True
    if not nazwa.endswith((".tmp", ".bak")):
        return False
    return nazwa[:-4] in PLIKI_ZAPISU_ATOMOWEGO if "/" not in rel else rel.startswith("kontrole/")


def czy_projekt_exocad(wpis: dict) -> bool:
    """Czy wpis manifestu to projekt exocad (nazwisko w nazwie pliku) - taki plik nie trafia do paczki. Decyduje nazwa ZRODLA zapisana
    przy kopiowaniu (``zrodlo``, ``wzgledna``): nie zmienia sie, gdy kopia w sesji dostaje dopisek ``__zmianaN`` (kolejna wersja) albo
    ``__N`` (duplikat). Dla pewnosci sprawdzana jest tez nazwa kopii (``cel``)."""
    return any(WZOR_PROJEKTU_EXOCAD.search(str(wpis.get(pole) or "")) for pole in ("zrodlo", "wzgledna", "cel"))


def bez_nazw_projektow(tekst: str, zamiany: dict | None = None) -> str:
    """``tekst`` (log, stan obserwatora, manifest jako JSON) bez nazw projektow exocad: nazwy z ``zamiany`` zastapione swoimi znacznikami,
    a kazda inna nazwa pliku pasujaca do wzoru projektu (np. plik zastany w folderze skanera, znany tylko obserwatorowi, albo plik,
    ktorego nie udalo sie skopiowac) - znacznikiem ogolnym. Nazwa siega wstecz do najblizszego ukosnika, cudzyslowu albo poczatku linii."""
    for nazwa, znacznik in sorted((zamiany or {}).items(), key=lambda p: -len(p[0])):
        tekst = tekst.replace(nazwa, znacznik)
    kawalki, koniec = [], 0
    for dop in WZOR_PROJEKTU_W_TEKSCIE.finditer(tekst):
        if dop.start() < koniec:
            continue
        poczatek = max(tekst.rfind(znak, koniec, dop.start()) for znak in '/\\"\n') + 1
        kawalki += [tekst[koniec:max(poczatek, koniec)], ZNACZNIK_PROJEKTU]
        koniec = dop.end()
    return "".join(kawalki) + tekst[koniec:] if kawalki else tekst


def _pliki_sesji(sesja: Sesja) -> list[tuple[str, str]]:
    """Pliki folderu sesji do sum i paczki: (sciezka wzgledna posix, sciezka do odczytu). Bez paczki i bez wlasnych plikow roboczych programu
    (``plik_roboczy_programu``); pliki ``*.bak`` / ``*.tmp`` / ``*.czesc`` skopiowane ze skanera (sa w manifescie) zostaja."""
    korzen = _io(sesja.folder)
    w_manifescie = frozenset(w["cel"] for w in sesja.m["pliki"])
    wynik = []
    for kat, katalogi, pliki in os.walk(korzen):
        rel_kat = os.path.relpath(kat, korzen).replace("\\", "/")
        if rel_kat == ".":
            katalogi[:] = [k for k in katalogi if k != KATALOG_PACZKI]
            rel_kat = ""
        for nazwa in pliki:
            rel = f"{rel_kat}/{nazwa}" if rel_kat else nazwa
            if plik_roboczy_programu(rel, w_manifescie) or rel in (PLIK_SUM, PLIK_SUM_NIEAKTUALNYCH):
                continue
            wynik.append((rel, os.path.join(kat, nazwa)))
    wynik.sort()
    return wynik


def manifest_bez_projektow(m: dict, pominiete: set) -> tuple[dict, dict]:
    """Kopia manifestu do paczki: wpisy plikow pominietych (projekty exocad) bez nazw - nazwa pliku moze byc nazwiskiem.

    Zwraca (manifest, zamiany: nazwa pliku -> znacznik ``projekt_pominiety_<SHA-16>``); nazwy sa tez usuwane z reszty
    manifestu (zdarzenia, uwagi), razem z kazda inna nazwa pasujaca do wzoru projektu (``bez_nazw_projektow``).
    Manifest w folderze sesji zostaje bez zmian."""
    zamiany: dict[str, str] = {}
    for w in m["pliki"]:
        if w["cel"] in pominiete:
            znacznik = f"{ZNACZNIK_PROJEKTU}_{w['sha256'][:16]}"
            for pole in ("cel", "zrodlo", "wzgledna"):
                if w.get(pole):
                    zamiany[Path(w[pole]).name] = znacznik
    surowy = json.dumps(m, ensure_ascii=False)
    tekst = bez_nazw_projektow(surowy, {json.dumps(nazwa, ensure_ascii=False)[1:-1]: znacznik for nazwa, znacznik in zamiany.items()})
    if tekst == surowy:
        return m, zamiany
    m2 = json.loads(tekst)
    for w, w2 in zip(m["pliki"], m2["pliki"]):
        if w["cel"] in pominiete:
            w2["pominiety_w_paczce"] = True
    return m2, zamiany


def raport_md(sesja: Sesja, dodatki: dict | None = None, manifest: dict | None = None) -> str:
    """Tresc ``RAPORT_dzien_skanera.md``: kroki, pliki, wyniki kontroli, notatki, braki, pominiecia z powodami.
    ``manifest``: manifest zamiast ``sesja.m`` (paczka: wersja bez nazw projektow)."""
    m = manifest if manifest is not None else sesja.m
    oceny = {o["id"]: o for o in kompletnosc_z_manifestu(m)}
    braki, pominiete = braki_wymaganych(m)
    pola_def = m.get("definicje_pol", {})
    L = [f"# Raport: dzien skanera, sesja {m['nazwa']}", ""]
    L += [f"- utworzono: {m['utworzono']}", f"- zakonczono: {m.get('zakonczono') or 'nie zakonczono'}", f"- raport wygenerowano: {teraz_iso()}",
          f"- plikow w sesji: {len(m['pliki'])}, razem {tekst_rozmiaru(sum(w['rozmiar'] for w in m['pliki']))}",
          "- foldery obserwowane: " + ("; ".join(f"`{f['sciezka']}` (etykieta {f['etykieta']})" for f in m["foldery"]) or "brak"),
          f"- zrzut automatyczny przy nowym pliku: {'tak' if m.get('auto_zrzut') else 'nie'}", ""]
    L += ["## Braki wymaganych krokow", ""]
    L += [f"- BRAK: {b}" for b in braki] or ["- brak brakow: wszystkie wymagane kroki sa zrobione albo swiadomie pominiete"]
    L += ["", "## Pominiecia z powodami", ""]
    wszystkie_pominiete = [o for o in oceny.values() if o["stan"] == "pominiety"]
    L += [f"- {o['tytul']} ({'wymagany' if o['wymagany'] else 'opcjonalny'}): {o['powod'] or '(bez powodu)'}" for o in wszystkie_pominiete] or ["- nic nie pominieto"]
    L += ["", "## Kompletnosc", "", "| nr | krok | wymagany | stan | pliki | braki |", "|---|---|---|---|---|---|"]
    for i, d in enumerate(m["definicje_krokow"], 1):
        o = oceny[d["id"]]
        L.append(f"| {i} | {d['tytul']} (`{d['id']}`) | {'tak' if o['wymagany'] else 'nie'} | {o['stan']} | {o['plikow']}"
                 + (f" z {o['oczekiwane']}" if o["oczekiwane"] else "") + f" (wszystkich {o['wszystkich_plikow']}) | {'; '.join(o['braki']) or '-'} |")
    L += ["", "## Wyniki kontroli skanow", "",
          "| id | krok | plik | rozmiar | trojkaty | odstep [mm] | odstep prace [mm] | uklad | numer | prace | szum RMS [mm] | stozki | werdykt |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for w in m["pliki"]:
        k = w.get("kontrola")
        if Path(w["cel"]).suffix.lower() not in ROZSZERZENIA_SIATEK:
            continue
        if not k:
            L.append(f"| {w['id']} | {w['krok']} | {Path(w['cel']).name} | {tekst_rozmiaru(w['rozmiar'])} | - | - | - | - | - | - | - | - | (bez kontroli) |")
            continue
        L.append(f"| {w['id']} | {w['krok']} | {Path(w['cel']).name} | {tekst_rozmiaru(w['rozmiar'])} | {k.get('trojkaty') or '-'} | {_l(k.get('odstep_mm'), 3)} | "
                 f"{_l(k.get('odstep_prace_mm'), 3)} | {k.get('uklad') or '-'} | {k.get('numer') if k.get('numer') is not None else '-'} ({k.get('numer_zrodlo') or '-'}) | "
                 f"{k.get('prace') if k.get('prace') is not None else '-'} | {_l(k.get('plaszczyzna_rms_mm'), 4)} | "
                 f"{k.get('stozki_dopasowane') if k.get('stozki_dopasowane') is not None else '-'} | {k.get('werdykt')} |")
    L += ["", "## Kroki szczegolowo", ""]
    for i, d in enumerate(m["definicje_krokow"], 1):
        s, o = m["kroki"][d["id"]], oceny[d["id"]]
        L += [f"### {i}. {d['tytul']} (`{d['id']}`)", "",
              f"- stan: {o['stan']}" + (f" - powod pominiecia: {s['powod']}" if o["stan"] == "pominiety" else ""),
              f"- wymagany: {'tak' if o['wymagany'] else 'nie'}; rozpoczeto: {s.get('rozpoczeto') or '-'}; zakonczono: {s.get('zakonczono') or '-'}"]
        if o["braki"]:
            L.append("- braki: " + "; ".join(o["braki"]))
        for p in d.get("pola", []):
            L.append(f"- {pola_def.get(p, {}).get('etykieta', p)}: {str(s['pola'].get(p, '')).strip() or '(nie wpisano)'}")
        for st in s.get("stoper", []):
            L.append(f"- czas zmierzony stoperem: {st['s']:.0f} s (od {st['start']} do {st['stop']})")
        if str(s.get("notatka", "")).strip():
            L += ["- notatka:", ""] + ["  > " + linia for linia in s["notatka"].strip().splitlines()] + [""]
        pliki = [w for w in m["pliki"] if w["krok"] == d["id"]]
        if pliki:
            L += ["", "| id | czas | rodzaj | plik w sesji | rozmiar | SHA-256 (16) | kontrola |", "|---|---|---|---|---|---|---|"]
            if len(pliki) > 60:
                L.append(f"| - | - | - | (pierwsze 60 z {len(pliki)} plikow; komplet w sesja.json) | - | - | - |")
            for w in pliki[:60]:
                k = w.get("kontrola")
                L.append(f"| {w['id']} | {w['skopiowano']} | {w['rodzaj']} | `{w['cel']}` | {tekst_rozmiaru(w['rozmiar'])} | {w['sha256'][:16]} | "
                         + (k["tekst"].replace("|", "/") if k else "-") + (" " + "; ".join(w["uwagi"]) if w.get("uwagi") else "") + " |")
        L.append("")
    if dodatki:
        L += ["## Paczka", ""]
        for k, v in dodatki.items():
            L.append(f"- {k}: {v}")
        L.append("")
    L += ["## Jak sprawdzic paczke", "", "`py -3.12 -m stanowisko.dzien_skanera --sprawdz <folder sesji albo plik zip>` - sumy SHA-256 i kompletnosc krokow.", ""]
    return "\n".join(L)


def spakuj(sesja: Sesja, postep=None, limit: int = LIMIT_ZIP, wolne=wolne_miejsce, przerwij=None) -> dict:
    """"Zakoncz i spakuj": raport, ``SHA256SUMS.txt`` i archiwum ZIP sesji w ``<sesja>/paczka/`` (kilka czesci, gdy dane > ``limit``).

    Pliki wygladajace na projekty exocad (``czy_projekt_exocad`` - nazwiska w nazwach) nie trafiaja do paczki ani do sum; zostaja w folderze sesji.
    Braki wymaganych krokow sa zwracane jako ostrzezenie i nie blokuja. Zwraca slownik z lista czesci, brakami i niezgodnosciami.

    Kolejnosc jest odporna na awarie: nowe archiwa powstaja pod nazwami tymczasowymi (``*.zip.czesc``), a dopiero gdy WSZYSTKIE sa gotowe,
    zastepuja stare; potem zapisywane sa raport i sumy, a na samym koncu znaczniki ``zakonczono`` / ``spakowano`` w manifescie. Nieudane
    albo przerwane pakowanie (wyjatek, brak miejsca, ``przerwij()`` = True -> ``Przerwano``, zabicie programu) zostawia wiec sesje
    NIEoznaczona jako spakowana, a poprzednia paczke - nietknieta.
    """
    def krok_postepu(zrobione: int, razem: int, co: str) -> None:
        if postep is not None:
            postep(zrobione, razem, co)

    def sprawdz_przerwanie() -> None:
        if przerwij is not None and przerwij():
            raise Przerwano()

    tymczasowe: list[str] = []
    try:
        sesja.log("pakowanie: start")
        czas = teraz_iso()
        with sesja._zamek:
            sesja.zapisz_zalegle()
            stan_przed = json.dumps(sesja.m, ensure_ascii=False, sort_keys=True)
            # manifest "po spakowaniu" tylko w pamieci (do paczki i raportu); sesja.m dostanie te znaczniki dopiero po sukcesie
            m_po = json.loads(json.dumps(sesja.m, ensure_ascii=False))
            m_po["zakonczono"] = czas
            m_po["spakowano"] = list(m_po.get("spakowano") or []) + [czas]
            m_po["zmieniono_po_spakowaniu"] = False
            m_po["zdarzenia"].append({"czas": czas, "co": "zakoncz i spakuj"})
        braki, pominiete_kroki = braki_wymaganych(m_po)
        wszystkie = _pliki_sesji(sesja)
        projekty = {w["cel"] for w in m_po["pliki"] if czy_projekt_exocad(w)}  # decyzja po nazwie zrodla z manifestu (takze __zmianaN, __N)
        pominiete = [rel for rel, _ in wszystkie if rel in projekty or WZOR_PROJEKTU_EXOCAD.search(rel)]
        ukryte_cele = projekty | set(pominiete)
        manifest_paczki, zamiany = manifest_bez_projektow(m_po, ukryte_cele)
        id_pominietych = {w["id"] for w in m_po["pliki"] if w["cel"] in ukryte_cele}
        # wynik kontroli i pomiaru szczegolowego tez niesie nazwe pliku
        ukryte = ukryte_cele | {f"kontrole/k{i:04d}{roz}" for i in id_pominietych for roz in (".json", ".log")}
        ukryte_katalogi = tuple(f"pomiary/k{i:04d}_" for i in id_pominietych)
        do_paczki = [(rel, p) for rel, p in wszystkie if rel not in ukryte and rel != PLIK_RAPORTU and not (ukryte_katalogi and rel.startswith(ukryte_katalogi))]
        razem = sum(os.path.getsize(p) for _, p in do_paczki)
        sprawdz_miejsce(sesja.folder, razem, wolne)  # ZIP moze byc tak duzy jak dane: komunikat przed pakowaniem
        # 1) sumy: migawki plikow "zywych" w pamieci, reszta liczona z dysku (i porownana z manifestem)
        sha_manifestu = {w["cel"]: w["sha256"] for w in m_po["pliki"]}
        migawki, sumy, niezgodne = {}, {}, []
        zrobione = 0
        for rel, p in do_paczki:
            sprawdz_przerwanie()
            if rel in PLIKI_ZYWE:
                if rel == PLIK_MANIFESTU:
                    migawki[rel] = json.dumps(manifest_paczki, ensure_ascii=False, indent=1).encode("utf-8")
                else:  # log i stan obserwatora: bez nazw projektow (takze zastanych w folderze skanera i nieskopiowanych)
                    with open(p, "rb") as f:
                        migawki[rel] = f.read()
                    tekst = migawki[rel].decode("utf-8", errors="replace")
                    czysty = bez_nazw_projektow(tekst, zamiany)
                    if czysty != tekst:
                        migawki[rel] = czysty.encode("utf-8")
                sumy[rel] = hashlib.sha256(migawki[rel]).hexdigest()
            else:
                sumy[rel] = sha256_pliku(p)
                if rel in sha_manifestu and sha_manifestu[rel] != sumy[rel]:
                    niezgodne.append(rel)
            zrobione += os.path.getsize(p)
            krok_postepu(zrobione, 2 * razem, "sumy kontrolne")
        # 2) podzial na czesci i raport (raport i sumy na razie tylko w pamieci)
        czesci, biezaca, rozmiar = [], [], 0
        for rel, p in do_paczki:
            r = len(migawki[rel]) if rel in migawki else os.path.getsize(p)
            if biezaca and rozmiar + r > limit:
                czesci.append(biezaca)
                biezaca, rozmiar = [], 0
            biezaca.append((rel, p))
            rozmiar += r
        czesci.append(biezaca)
        nazwa = f"dzien_skanera_{sesja.m['nazwa']}"
        nazwy_zip = [f"{nazwa}.zip"] if len(czesci) == 1 else [f"{nazwa}_cz{i}z{len(czesci)}.zip" for i in range(1, len(czesci) + 1)]
        dodatki = {"czesci archiwum": ", ".join(nazwy_zip), "plikow w paczce": len(do_paczki) + 2, "danych": tekst_rozmiaru(razem),
                   "pliki pominiete w paczce (wygladaja na projekty exocad)": len(pominiete),
                   "pliki o sumie innej niz w manifescie (zmienione po skopiowaniu!)": ", ".join(niezgodne) or "brak"}
        for k in stan_kopii_folderow(m_po):
            dodatki[f"kopia calego folderu (krok {k['krok']})"] = (("pelna" if k["pelna"] else f"NIEPELNA ({k['stan']})") + f": w sesji {k['jest']} z {k['plikow']} plikow, "
                                                                 f"bledy {k['bledy']}, pominiete {k['pominiete']}, niedostepne podfoldery {k['niedostepne_katalogi']}")
        raport = raport_md(sesja, dodatki, manifest_paczki).encode("utf-8")
        sumy[PLIK_RAPORTU] = hashlib.sha256(raport).hexdigest()
        tresc_sum = "".join(f"{sumy[rel]}  {rel}\n" for rel in sorted(sumy)).encode("utf-8")
        # 3) archiwum: wszystkie czesci pod nazwami tymczasowymi; stara paczka zostaje nietknieta, dopoki nowa nie jest cala
        kat = sesja.sciezka(KATALOG_PACZKI)
        os.makedirs(_io(kat), exist_ok=True)
        for stary in os.listdir(_io(kat)):
            if stary.startswith(nazwa) and stary.endswith(".zip.czesc"):  # pozostalosc po pakowaniu przerwanym zabiciem programu (wytwor programu)
                os.unlink(os.path.join(_io(kat), stary))
        for nazwa_zip, zawartosc in zip(nazwy_zip, czesci):
            tmp = _io(str(kat / nazwa_zip) + ".czesc")
            tymczasowe.append(tmp)
            # strict_timestamps=False: plik z data sprzed 1980 (kopia zachowuje czas zrodla) dostaje w archiwum date 1980-01-01 zamiast wyjatku
            with zipfile.ZipFile(tmp, "w", allowZip64=True, strict_timestamps=False) as zf:
                for rel_stale, tresc in ((PLIK_RAPORTU, raport), (PLIK_SUM, tresc_sum)):
                    zf.writestr(f"{sesja.m['nazwa']}/{rel_stale}", tresc, compress_type=zipfile.ZIP_DEFLATED)
                for rel in PLIKI_ZYWE:  # manifest i log w kazdej czesci: kazda czesc opisuje sie sama
                    if rel in migawki:
                        zf.writestr(f"{sesja.m['nazwa']}/{rel}", migawki[rel], compress_type=zipfile.ZIP_DEFLATED)
                for rel, p in zawartosc:
                    if rel in migawki:
                        continue
                    sprawdz_przerwanie()
                    spakowany = rel.lower().endswith(ROZSZERZENIA_SPAKOWANE)
                    zf.write(p, f"{sesja.m['nazwa']}/{rel}", compress_type=zipfile.ZIP_STORED if spakowany else zipfile.ZIP_DEFLATED, compresslevel=None if spakowany else 1)
                    zrobione += os.path.getsize(p)
                    krok_postepu(zrobione, 2 * razem, nazwa_zip)
        sprawdz_przerwanie()
        # 4) nowa paczka jest cala: zamiana (te same nazwy sa zastepowane), potem usuniecie starych czesci o innych nazwach
        wynik_czesci = []
        for tmp, nazwa_zip in zip(list(tymczasowe), nazwy_zip):
            cel = kat / nazwa_zip
            os.replace(tmp, _io(cel))
            tymczasowe.remove(tmp)
            wynik_czesci.append({"plik": f"{KATALOG_PACZKI}/{nazwa_zip}", "sciezka": str(cel), "rozmiar": os.path.getsize(_io(cel)), "sha256": sha256_pliku(cel)})
        nowe = {n.lower() for n in nazwy_zip}
        for stary in os.listdir(_io(kat)):
            if stary.startswith(nazwa) and stary.lower().endswith(".zip") and stary.lower() not in nowe:
                os.unlink(os.path.join(_io(kat), stary))
        zapisz_atomowo(sesja.folder / PLIK_RAPORTU, raport)
        zapisz_atomowo(sesja.folder / PLIK_SUM, tresc_sum)
        try:
            os.unlink(_io(sesja.folder / PLIK_SUM_NIEAKTUALNYCH))
        except OSError:
            pass
        krok_postepu(2 * razem, 2 * razem, "gotowe")
        wynik = {"sesja": sesja.m["nazwa"], "utworzono": teraz_iso(), "raport": str(sesja.folder / PLIK_RAPORTU), "sumy": str(sesja.folder / PLIK_SUM),
                 "czesci": wynik_czesci, "plikow": len(do_paczki) + 2, "bajtow": razem, "pominiete_w_paczce": pominiete, "niezgodne_z_manifestem": niezgodne,
                 "braki": braki, "pominiete_kroki": pominiete_kroki}
        zapisz_atomowo(kat / "paczka.json", json.dumps(wynik, ensure_ascii=False, indent=1).encode("utf-8"))
        sesja.log(f"pakowanie: koniec, {len(wynik_czesci)} czesci, {razem} B danych, braki wymaganych: {len(braki)}, niezgodne: {len(niezgodne)}")
        # 5) dopiero teraz znaczniki w manifescie sesji (zapis na dysk); sesja zmieniona w trakcie pakowania (np. notatka) = "spakuj ponownie"
        with sesja._zamek:
            zmieniona = json.dumps(sesja.m, ensure_ascii=False, sort_keys=True) != stan_przed
            sesja.m["zakonczono"] = czas
            sesja.m.setdefault("spakowano", []).append(czas)
            sesja.m["zmieniono_po_spakowaniu"] = zmieniona
            sesja.m["zdarzenia"].append({"czas": czas, "co": "zakoncz i spakuj"})
            if zmieniona:
                sesja._uniewaznij_sumy()
            sesja._pakowanie = True  # ten jeden zapis to znaczniki pakowania, a nie "zmiana po spakowaniu"
            try:
                sesja.zapisz()
            finally:
                sesja._pakowanie = False
        return wynik
    except BaseException as e:
        for tmp in tymczasowe:
            try:
                os.unlink(tmp)
            except OSError:
                pass
        sesja.log(f"pakowanie: {'przerwane' if isinstance(e, Przerwano) else 'nieudane'} ({type(e).__name__}) - sesja nie jest oznaczona jako spakowana, "
                  "poprzednia paczka (jesli byla) zostaje bez zmian")
        raise


# ----------------------------------------------------------------------------
# sprawdzenie paczki (dla koordynatora)
# ----------------------------------------------------------------------------
WZOR_CZESCI = re.compile(r"^(?P<baza>.+)_cz(?P<nr>\d+)z(?P<ile>\d+)\.zip$", re.IGNORECASE)


class _ZrodloFolder:
    def __init__(self, folder: Path):
        self.opis = f"folder {folder}"
        self.pliki = {rel: p for rel, p in ((os.path.relpath(os.path.join(kat, n), _io(folder)).replace("\\", "/"), os.path.join(kat, n))
                                            for kat, _, nazwy in os.walk(_io(folder)) for n in nazwy)}

    def sha256(self, rel: str) -> str:
        return sha256_pliku(self.pliki[rel])

    def czytaj(self, rel: str) -> bytes:
        with open(self.pliki[rel], "rb") as f:
            return f.read()


class _ZrodloZip:
    def __init__(self, pliki_zip: list[Path]):
        self.opis = "archiwum " + ", ".join(p.name for p in pliki_zip)
        self.zipy = []
        try:
            for p in pliki_zip:
                self.zipy.append(zipfile.ZipFile(p))
        except BaseException:
            self.zamknij()
            raise
        self.pliki = {}
        self.powtorzone_rozne = []
        for zf in self.zipy:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                rel = info.filename.split("/", 1)[1] if "/" in info.filename else info.filename
                if rel in self.pliki and self.pliki[rel][1].CRC != info.CRC:
                    self.powtorzone_rozne.append(rel)
                self.pliki.setdefault(rel, (zf, info))

    def sha256(self, rel: str) -> str:
        zf, info = self.pliki[rel]
        h = hashlib.sha256()
        with zf.open(info) as f:  # odczyt do konca sprawdza tez CRC archiwum
            while True:
                blok = f.read(BLOK_KOPII)
                if not blok:
                    break
                h.update(blok)
        return h.hexdigest()

    def czytaj(self, rel: str) -> bytes:
        zf, info = self.pliki[rel]
        return zf.read(info)

    def zamknij(self) -> None:
        for zf in self.zipy:
            zf.close()


def sprawdz(sciezka) -> tuple[int, list[str]]:
    """Sprawdzenie paczki albo folderu sesji: sumy SHA-256, zgodnosc z manifestem, kompletnosc krokow.

    Kod: 0 = sumy zgodne i komplet wymaganych krokow; 1 = blad integralnosci (brak pliku, zla suma, uszkodzone archiwum,
    brak czesci); 3 = sumy zgodne, ale sa braki albo pominiecia wymaganych krokow; 2 = nie ma czego sprawdzac.
    Niczego nie zapisuje (archiwum jest czytane strumieniowo, bez rozpakowywania na dysk).
    Folder bez manifestu, w ktorym leza archiwa kilku sesji: sprawdzana jest KAZDA paczka, a kod jest najgorszym z wynikow (1, potem 3, potem 0).
    """
    sciezka = Path(sciezka)
    cele = [sciezka]
    if sciezka.is_dir() and not (sciezka / PLIK_MANIFESTU).exists():
        zipy = sorted(sciezka.glob("dzien_skanera_*.zip")) or sorted((sciezka / KATALOG_PACZKI).glob("dzien_skanera_*.zip"))
        if not zipy:
            return 2, [f"BLAD: w {sciezka} nie ma {PLIK_MANIFESTU} ani archiwum dzien_skanera_*.zip"]
        paczki: dict[str, Path] = {}  # jedna paczka = jedno archiwum albo komplet czesci <baza>_cz<i>z<n>.zip
        for p in zipy:
            dop = WZOR_CZESCI.match(p.name)
            paczki.setdefault((dop["baza"] + "_cz").lower() if dop else p.name.lower(), p)
        cele = list(paczki.values())
    kody, linie = [], []
    for cel in cele:
        zrodla: list = []
        try:
            kod, L = _sprawdz(cel, zrodla)
        finally:
            for z in zrodla:
                if hasattr(z, "zamknij"):
                    z.zamknij()
        kody.append(kod)
        linie += ([""] if linie else []) + L
    if len(cele) > 1:
        linie += ["", f"RAZEM: {len(cele)} paczki w {sciezka}: " + ", ".join(f"{c.name} = kod {k}" for c, k in zip(cele, kody))]
    return next((k for k in (1, 3, 2) if k in kody), 0), linie


def _sprawdz(sciezka: Path, zrodla: list) -> tuple[int, list[str]]:
    L: list[str] = []
    bledy = 0
    if sciezka.is_dir():
        zrodlo = _ZrodloFolder(sciezka)
        z_folderu = True
    elif sciezka.is_file():
        z_folderu = False
        czesci = [sciezka]
        dop = WZOR_CZESCI.match(sciezka.name)
        if dop:
            ile = int(dop["ile"])
            czesci = [sciezka.with_name(f"{dop['baza']}_cz{i}z{ile}.zip") for i in range(1, ile + 1)]
            for brak in [c for c in czesci if not c.is_file()]:
                L.append(f"BLAD: brakuje czesci archiwum {brak.name}")
                bledy += 1
            czesci = [c for c in czesci if c.is_file()]
        try:
            zrodlo = _ZrodloZip(czesci)
        except (zipfile.BadZipFile, OSError) as e:
            return 1, L + [f"BLAD: archiwum nie da sie otworzyc: {type(e).__name__}: {e}"]
        for rel in zrodlo.powtorzone_rozne:
            L.append(f"BLAD: plik {rel} ma rozna tresc w roznych czesciach archiwum")
            bledy += 1
    else:
        return 2, [f"BLAD: nie ma takiego folderu ani pliku: {sciezka}"]
    zrodla.append(zrodlo)
    L.insert(0, f"Sprawdzam: {zrodlo.opis}")
    # sumy
    if PLIK_SUM not in zrodlo.pliki:
        L.append(f"BLAD: brak {PLIK_SUM}" + (f" (jest {PLIK_SUM_NIEAKTUALNYCH}: sesja zmieniona po spakowaniu - spakuj ponownie)" if PLIK_SUM_NIEAKTUALNYCH in zrodlo.pliki else
                                              " (sesja nie byla spakowana przyciskiem 'Zakoncz i spakuj')"))
        bledy += 1
        sumy = {}
    else:
        sumy = {}
        for linia in zrodlo.czytaj(PLIK_SUM).decode("utf-8").splitlines():
            if linia.strip():
                sha, _, rel = linia.partition("  ")
                sumy[rel.strip()] = sha.strip()
    zgodne = zmienione_zywe = 0
    for rel, sha in sorted(sumy.items()):
        if rel not in zrodlo.pliki:
            L.append(f"BLAD: brak pliku {rel}")
            bledy += 1
            continue
        try:
            rzeczywista = zrodlo.sha256(rel)
        except Exception as e:  # noqa: BLE001 - uszkodzone archiwum: BadZipFile, zlib.error, EOFError ...
            L.append(f"BLAD: plik {rel} nieczytelny ({type(e).__name__}: {e})")
            bledy += 1
            continue
        if rzeczywista == sha:
            zgodne += 1
        elif z_folderu and rel in PLIKI_ZYWE:
            zmienione_zywe += 1
            L.append(f"UWAGA: {rel} w folderze sesji rozni sie od migawki z paczki (zmiana po spakowaniu albo ukryte nazwy projektow; w archiwum jest migawka)")
        else:
            L.append(f"BLAD: zla suma pliku {rel} (jest {rzeczywista[:16]}..., powinno byc {sha[:16]}...)")
            bledy += 1
    # manifest (potrzebny juz do listy plikow dodatkowych: plik z manifestu nie jest plikiem roboczym programu, nawet gdy konczy sie na .bak / .tmp)
    kod_kompletnosci = 0
    blad_manifestu = None
    try:
        m = json.loads(zrodlo.czytaj(PLIK_MANIFESTU).decode("utf-8"))
    except (KeyError, ValueError, OSError, zipfile.BadZipFile) as e:
        blad_manifestu = f"BLAD: {PLIK_MANIFESTU} nieczytelny ({type(e).__name__}: {e})"
        m = None
    w_manifescie = frozenset(w.get("cel", "") for w in (m or {}).get("pliki", []))
    dodatkowe = sorted(rel for rel in zrodlo.pliki if rel not in sumy and rel not in (PLIK_SUM, PLIK_SUM_NIEAKTUALNYCH)
                       and not rel.startswith(KATALOG_PACZKI + "/") and not plik_roboczy_programu(rel, w_manifescie))
    L.append(f"SUMY: {zgodne} z {len(sumy)} plikow zgodnych" + (f", {zmienione_zywe} zmienionych po spakowaniu (manifest / log)" if zmienione_zywe else ""))
    if dodatkowe:
        L.append(f"UWAGA: {len(dodatkowe)} plikow spoza listy sum (np. projekty pominiete w paczce): " + ", ".join(dodatkowe[:5]) + (" ..." if len(dodatkowe) > 5 else ""))
    if blad_manifestu:
        L.append(blad_manifestu)
        bledy += 1
    if m is not None:
        brak_w_paczce = zla_suma = poza_sumami = 0
        for w in m.get("pliki", []):
            if w.get("pominiety_w_paczce") or czy_projekt_exocad(w):
                continue  # projekt exocad: pominiety w paczce celowo (w folderze sesji zostaje, ale nie jest objety sumami)
            if w["cel"] not in zrodlo.pliki:
                brak_w_paczce += 1
                L.append(f"BLAD: plik z manifestu nie istnieje: {w['cel']} (id {w['id']})")
            elif w["cel"] in sumy and sumy[w["cel"]] != w["sha256"]:
                zla_suma += 1
                L.append(f"BLAD: plik {w['cel']} ma inna sume niz przy kopiowaniu (zmieniony po skopiowaniu)")
            elif sumy and w["cel"] not in sumy:  # folder i archiwum maja dac ten sam wynik: w archiwum takiego pliku by nie bylo
                poza_sumami += 1
                L.append(f"BLAD: plik z manifestu nie jest objety sumami: {w['cel']} (id {w['id']}) - spakuj sesje ponownie")
        bledy += brak_w_paczce + zla_suma + poza_sumami
        L.append(f"MANIFEST: sesja {m.get('nazwa')}, utworzona {m.get('utworzono')}, zakonczona {m.get('zakonczono') or 'NIE'}, plikow {len(m.get('pliki', []))}, "
                 f"razem {tekst_rozmiaru(sum(w['rozmiar'] for w in m.get('pliki', [])))}")
        L.append("KROKI:")
        for i, o in enumerate(kompletnosc_z_manifestu(m), 1):
            L.append(f"  {i:2d}. [{o['stan']:9s}] {'wymagany  ' if o['wymagany'] else 'opcjonalny'} {o['tytul']} - plikow {o['plikow']}"
                     + (f" z {o['oczekiwane']}" if o["oczekiwane"] else "") + (f"; braki: {'; '.join(o['braki'])}" if o["braki"] else "")
                     + (f"; powod pominiecia: {o['powod']}" if o["stan"] == "pominiety" else ""))
        werdykty = collections.Counter((w.get("kontrola") or {}).get("werdykt", "bez kontroli") for w in m.get("pliki", []) if Path(w["cel"]).suffix.lower() in ROZSZERZENIA_SIATEK)
        L.append("KONTROLA SKANOW: " + (", ".join(f"{k}: {v}" for k, v in sorted(werdykty.items())) or "brak plikow skanow"))
        kopie = stan_kopii_folderow(m)  # wynik kopii calego folderu zapisany w manifescie, porownany z liczba plikow kopii w manifescie
        for k in kopie:
            L.append(f"KOPIA FOLDERU (krok {k['krok']}): " + ("pelna" if k["pelna"] else f"NIEPELNA ({k['stan']})") + f" - w sesji {k['jest']} z {k['plikow']} plikow "
                     f"(skopiowane {k['skopiowane']}, wczesniej {k['juz_byly']}, bledy {k['bledy']}, pominiete {k['pominiete']}, niedostepne podfoldery {k['niedostepne_katalogi']})")
        braki, pominiete = braki_wymaganych(m)
        if braki or pominiete or any(not k["pelna"] for k in kopie):
            kod_kompletnosci = 3
            L.append(f"KOMPLETNOSC: BRAKI - nie zrobione wymagane kroki: {len(braki)}, pominiete wymagane kroki: {len(pominiete)}"
                     + (", niepelna kopia calego folderu" if any(not k["pelna"] for k in kopie) else ""))
            L += [f"  brak: {b}" for b in braki] + [f"  pominiety: {p}" for p in pominiete]
        else:
            L.append("KOMPLETNOSC: pelna (wszystkie wymagane kroki zrobione)")
    L.append("WYNIK: " + (f"BLAD INTEGRALNOSCI ({bledy})" if bledy else "sumy zgodne" + (", ale sa braki krokow" if kod_kompletnosci else ", komplet")))
    return (1 if bledy else kod_kompletnosci), L


# ----------------------------------------------------------------------------
# ustawienia odporne na brak pliku
# ----------------------------------------------------------------------------
def wczytaj_ustawienia_bezpiecznie(plik: Path | None = None) -> tuple[dict | None, Path | None, str]:
    """(ustawienia, plik, komunikat). Gdy ``ustawienia.toml`` nie ma albo jest zly - probuje wzoru; gdy i to zawiedzie - (None, None, powod).
    Okno dnia skanera ma dzialac takze bez poprawnych ustawien (zbieranie plikow nie zalezy od nich)."""
    bledy = []
    for kandydat in ([Path(plik)] if plik is not None else []) + [UST.PLIK_USTAWIEN, UST.PLIK_PRZYKLADU]:
        try:
            return UST.wczytaj_ustawienia(kandydat), kandydat, "; ".join(bledy)
        except Exception as e:  # noqa: BLE001
            bledy.append(f"{kandydat.name}: {e}")
    return None, None, "; ".join(bledy)


# ----------------------------------------------------------------------------
# wiersz polecen
# ----------------------------------------------------------------------------
def wypisz(linie: list[str]) -> None:
    """Wynik na stdout; znaki spoza strony kodowej konsoli (tytuly krokow maja polskie litery) sa zastepowane, nie koncza programu."""
    try:
        sys.stdout.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass
    print("\n".join(linie))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Dzien skanera: szybka kontrola skanu albo sprawdzenie paczki (bez okna)")
    ap.add_argument("--kontrola", type=Path, default=None, help="plik skanu (STL / PLY / OBJ) do szybkiej kontroli")
    ap.add_argument("--wynik", type=Path, default=None, help="plik JSON na wynik kontroli (domyslnie: stdout)")
    ap.add_argument("--numer", type=int, default=None, help="numer plytki podany przez czlowieka")
    ap.add_argument("--ustawienia", type=Path, default=None)
    ap.add_argument("--sprawdz", type=Path, default=None, help="folder sesji albo archiwum ZIP do sprawdzenia")
    a = ap.parse_args(argv)
    if a.sprawdz is not None:
        kod, linie = sprawdz(a.sprawdz)
        wypisz(linie)
        return kod
    if a.kontrola is not None:
        ust, _, _ = wczytaj_ustawienia_bezpiecznie(a.ustawienia)
        wynik = kontrola_pliku(a.kontrola, ust, a.numer)
        tresc = json.dumps(wynik, ensure_ascii=False, indent=1)
        if a.wynik is not None:
            zapisz_atomowo(a.wynik, tresc.encode("utf-8"))
        else:
            print(tresc)
        return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
