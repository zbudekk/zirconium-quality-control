"""aplikacja - program "Stanowisko": kontroler spinajacy ``scanner`` -> ``silnik`` -> ``session`` / ``baza`` (paczka E3-A3a).

Technik uklada prace na plytce, skaner zapisuje STL do folderu, a ten modul bez udzialu czlowieka: zauwaza plik
(``scanner``), zleca analize w osobnym procesie (``silnik``), przyjmuje wynik do sesji wieczornej (``session``) i wystawia
oknu stan oraz polecenia opisane w ``kontroler_api`` (kontrakt dla ekranu - paczka A3b). Sam nie rysuje niczego.

``Aplikacja`` (prawdziwy kontroler; wspolna czesc z atrapa: ``kontroler_api.KontrolerSesji``):
* start: baza i sesja z ``ustawienia.toml``, silnik, wznowienie zadan zapisanych przy zamknieciu, potem obserwator folderu
  z ``znane=ZnanePliki(...)`` - skany zapisane, gdy program nie dzialal, sa nadrabiane, a juz przyjete nie wracaja;
* kazdy skan: powtorka tej samej tresci (``sha16``) wobec skanu, ktory MA wynik w bazie, albo wobec zadania czekajacego
  w kolejce nie jest liczona drugi raz; samo zobaczenie pliku niczego nie zapisuje (awaria przed wynikiem nie gubi skanu);
* wynik: ``session.przyjmij_wynik`` (tryb "rano" - E3-A7: ``session_rano.SesjaRano.przyjmij_wynik``, piec otwiera sie sam);
  blad analizy: ``session.przyjmij_blad`` (rano: ``SesjaRano.przyjmij_blad``) + komunikat; ``plik_zmieniony`` - tylko
  informacja (nowa tresc ma wlasne zdarzenie); ``plik_niedostepny`` - ponawianie (``[silnik] ponow_plik_niedostepny``);
* pula projektow na poziomie 1 planu: jeden folder + wspolczynnik wpisany recznie (None = domyslny dla typu plytki, jak
  w oknie testowym); liczba STL liczona w tle; bez projektow skany CZEKAJA (nie dostaja bledu) do "Odswiez pule";
* zamkniecie: ``scanner.stop()``, potem ``silnik.stop()``, wyniki, ktore zdazyly przyjsc, sa przyjmowane, a zadania
  niezakonczone (w toku, w kolejce, wstrzymane) zapisywane do pliku obok bazy i zlecane ponownie po starcie;
* akcja "start skanu" (DW5): interfejs ``Scanner.start_skanu`` z atrapa - zadnego automatu klikajacego w programie skanera;
* ramki i Excel (E3-A12): ``Aplikacja(ust, ramki=True, excel=True)`` (``main``) - klienci ramek z ``[ramki]`` (``utworz_ramki``) i Excel
  z ``[excel]`` (``utworz_excel``, polaczenie COM leniwe) przy starcie; brak ramki albo Excela = komunikat, praca dalej. Ramka W:
  Spacja, skan bez Spacji (``znacznik``), start analizy raz na skan, wynik = kolory mapy; zamkniecie: zgaszenie, zatrzymanie, rozlaczenie.

Runda 2 recenzji PR #20: jeden egzemplarz programu na plik bazy (``BlokadaStanowiska``, B1) i twarde odsiewanie wyniku
o ``sha16`` juz przyjetym w tej samej transakcji co zapis; wynik / blad, ktorego nie da sie zapisac (baza zajeta, dysk),
czeka w pamieci jako pozycja "nie zapisano" i jest zapisywany ponownie z rosnacym odstepem (P1, P8); plik przemianowany
w kolejce przejmuje zadanie (P2); po bledzie analizy pula jest liczona od nowa - pusta albo zniknieta = skan czeka (P3);
log bez nazw plikow (``FiltrNazw``, P5); kopie wynikow silnika nie zostaja w ``dane/podglady`` (P9).

Dane osobowe: nazwy plikow i folderow (skanu, puli, zlecen) nie trafiaja do komunikatow, stanu, dziennika ani logu tego
modulu - skan jest opisywany skrotem ``sha16``. Wyjatki zamierzone: ``skany.plik`` (kolumna z planu, pisze ``session``)
i dwa pliki robocze obok bazy (``PLIK_ZADAN``: sciezki skanow czekajacych na analize; ``PLIK_PULI``: folder puli). Pole
``skan`` wyniku (nazwa pliku skanu wpisywana przez ``porownaj``) jest przed zapisem w sesji zastepowane skrotem ``sha16``.

Plik startowy: ``python -m stanowisko.aplikacja`` (``uruchom_stanowisko.bat``). Na poziomie modulu NIE MA importu Qt -
proces roboczy silnika wykonuje ten plik ponownie (``__mp_main__``) i zaladowalby Qt obok Open3D (``silnik.md``, D8).
Wszystkie moduly PySide6 sa importowane w calosci na poczatku ``main()``, przed pierwszym uzyciem silnika.
"""
from __future__ import annotations

import argparse
import collections
import dataclasses
import datetime as dt
import json
import logging
import logging.handlers
import multiprocessing
import os
import queue
import re
import sqlite3
import sys
import threading
import time
from pathlib import Path
from typing import Any, Callable

from . import baza as B
from . import excel as EX
from . import kontroler_api as K
from . import scanner as SC
from . import session as SE
from . import silnik as SI
from . import statusy as ST
from . import ustawienia as UST

LOG = logging.getLogger(__name__)

WERSJA_PROGRAMU = "etap3-A3a"  # do ``skany.wersja_programu``, dopoki paczka wydania (A11) nie poda numeru wydania
PLIK_ZADAN = "zadania_niezakonczone.json"  # obok bazy: zadania przerwane zamknieciem programu (do zlecenia po starcie)
PLIK_PULI = "stanowisko_pula.json"  # obok bazy: folder puli i wspolczynnik wpisane przez technika (poziom 1 planu)
WSPOLCZYNNIK_MIN, WSPOLCZYNNIK_MAX = K.WSPOLCZYNNIK_MIN, K.WSPOLCZYNNIK_MAX  # walidacja wspolna z atrapa (KontrolerSesji._sprawdz_pule)
PROBY_STARTU_SILNIKA = 1  # ile razy zadanie jest zlecane ponownie, gdy proces silnika nie umie wystartowac
OKRES_KONTROLI_S = 1.0  # co ile ``przetworz`` sprawdza stan obserwatora (folder dostepny, pliki zajete); pierwszy odstep ponowienia zapisu
ODSTEP_ZAPISU_MAX_S = 30.0  # P1 / P8: ponowienia zapisu wyniku co OKRES_KONTROLI_S, potem 2x, 4x ... rzadziej, najrzadziej co tyle
PLIK_LOGU = "stanowisko.log"
PLIK_LOGU_SILNIKA = "silnik.log"
KOD_PROGRAM_JUZ_DZIALA = 3  # kod wyjscia main(), gdy inny egzemplarz pracuje na tej bazie (B1)
PRZYCZYNA_BAZA_ZAJETA, PRZYCZYNA_BLAD_ZAPISU = "baza_zajeta", "blad_zapisu"  # ``Niezapisany.przyczyna``


def _istnieje(plik: str | Path) -> bool:
    try:
        return Path(plik).is_file()
    except (OSError, ValueError):
        return False


def _klucz_sciezki(plik: str | Path) -> str:
    return os.path.normcase(os.path.abspath(str(plik)))


def _blad_zapisu(blad: BaseException) -> bool:
    """Blad zapisu, ktory moze minac (P1): pelny dysk, blad wejscia / wyjscia, dysk odlaczony, brak uprawnien do pliku -
    ``OSError`` albo blad operacyjny SQLite (``database or disk is full``, ``disk I/O error``). Blad danych (ograniczenie
    bazy, zly wynik) - nie: ponowienie nic by nie dalo."""
    return isinstance(blad, (OSError, sqlite3.OperationalError)) or type(blad) is sqlite3.DatabaseError


@dataclasses.dataclass
class Zlecenie:
    """Skan czekajacy na analize: to, co trzeba wiedziec, zeby zlecic go silnikowi i przyjac wynik do sesji (takze po restarcie)."""

    plik: str
    sha16: str
    rozmiar: int | None = None
    mtime_ns: int | None = None
    trojkaty: int | None = None
    tryb: str = SE.TRYB_WIECZOR
    numer: int | None = None
    zastany: bool = False  # plik zapisany, gdy program nie dzialal (nadrabianie)
    wznowiony: bool = False  # zadanie zapisane przy zamknieciu programu
    proby: int = 0  # ile razy silnik oddal blad ``plik_niedostepny``
    proby_startu: int = 0  # ile razy silnik oddal blad ``start``
    zastepcze: list = dataclasses.field(default_factory=list)  # P2: (plik, mtime_ns) tej samej tresci pod inna nazwa (przemianowany)
    znacznik_w: Any = None  # E3-A12: znacznik skanu na ramce wieczornej (``indicate.Znacznik``) albo None
    analiza_w: bool = False  # E3-A12: "analiza" wyslana do ramki W (raz na skan - recenzja PR #28 D5)

    @classmethod
    def ze_zdarzenia(cls, z: Any, tryb: str) -> "Zlecenie":
        return cls(plik=str(z.plik), sha16=z.sha16, rozmiar=z.rozmiar, mtime_ns=z.mtime_ns, trojkaty=z.trojkaty, tryb=tryb, zastany=bool(z.zastany))

    def sciezka_aktualna(self) -> tuple:
        """(plik, mtime_ns) pod ktorymi skan lezy teraz: pierwsza istniejaca sciezka z ``plik`` i ``zastepcze`` (P2 - plik
        przemianowany w kolejce); gdy zadnej nie ma - ``plik``."""
        for plik, mtime_ns in [(self.plik, self.mtime_ns)] + list(self.zastepcze):
            if _istnieje(plik):
                return plik, mtime_ns
        return self.plik, self.mtime_ns

    def przejmij_zastepcza(self) -> bool:
        """P2: pliku pod ``plik`` nie ma - zlecenie przechodzi na pierwsza istniejaca sciezke zastepcza (zuzywa ja). False = brak."""
        while self.zastepcze:
            plik, mtime_ns = self.zastepcze.pop(0)
            if _istnieje(plik):
                self.plik, self.mtime_ns = plik, mtime_ns
                return True
        return False

    def zdarzenie(self) -> dict:
        """Zdarzenie skanu dla ``session`` (kontrakt ``ZdarzenieSkanu``: plik, sha16, rozmiar, czas_pliku w sekundach od epoki)."""
        plik, mtime_ns = self.sciezka_aktualna()
        return {"plik": plik, "sha16": self.sha16, "rozmiar": self.rozmiar, "czas_pliku": mtime_ns / 1e9 if mtime_ns is not None else None}

    def do_zapisu(self) -> dict:
        plik, mtime_ns = self.sciezka_aktualna()
        return {"plik": plik, "sha16": self.sha16, "rozmiar": self.rozmiar, "mtime_ns": mtime_ns, "trojkaty": self.trojkaty, "tryb": self.tryb,
                "numer": self.numer}


@dataclasses.dataclass(eq=False)
class DoZapisu:
    """Wynik (``rodzaj`` wynik, ``zdarzenie`` silnika) albo blad analizy (``rodzaj`` blad, ``blad_rodzaj`` / ``blad_opis``),
    ktorego nie udalo sie zapisac w bazie (P1, P8): czeka w pamieci, ponowienie po ``nastepna`` (time.monotonic())."""

    zlecenie: Zlecenie
    rodzaj: str
    zdarzenie: Any = None
    blad_rodzaj: str = ""
    blad_opis: str = ""
    przyczyna: str = PRZYCZYNA_BAZA_ZAJETA
    proby: int = 0
    od: str = ""
    nastepna: float = 0.0


def odstep_ponowienia(proby: int) -> float:
    """Odstep przed kolejna proba zapisu po ``proby`` nieudanych: OKRES_KONTROLI_S, 2x, 4x ..., najwyzej ODSTEP_ZAPISU_MAX_S."""
    return min(ODSTEP_ZAPISU_MAX_S, OKRES_KONTROLI_S * 2 ** max(0, min(proby, 16) - 1))


class ProgramJuzDziala(RuntimeError):
    """Inny egzemplarz programu pracuje juz na tym pliku bazy (B1). Drugi egzemplarz nie dotyka bazy ani folderu skanera."""


class BlokadaStanowiska:
    """B1: jeden egzemplarz programu na dany plik bazy. Plik ``<baza>.blokada`` obok bazy jest otwarty i zablokowany przez caly
    czas pracy (Windows: ``msvcrt.locking``, inne systemy: ``fcntl.flock``). Blokade trzyma system: znika razem z procesem -
    takze po awarii, zabiciu procesu albo wylaczeniu pradu - wiec nie ma "wiszacej" blokady do recznego usuwania."""

    def __init__(self, plik_bazy: str | Path):
        plik_bazy = Path(plik_bazy)
        self.plik = plik_bazy.with_name(plik_bazy.name + ".blokada")
        self._fd: int | None = None

    def zajmij(self) -> "BlokadaStanowiska":
        """Zajmuje blokade albo rzuca ``ProgramJuzDziala`` (od razu, bez czekania)."""
        if self._fd is not None:
            return self
        self.plik.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(self.plik, os.O_RDWR | os.O_CREAT, 0o644)
        try:
            if os.name == "nt":
                import msvcrt  # noqa: PLC0415

                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            else:
                import fcntl  # noqa: PLC0415

                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            os.close(fd)
            raise ProgramJuzDziala("Program \"Stanowisko\" juz dziala na tym komputerze (ta sama baza stanowiska) - przejdz do otwartego "
                                   "okna programu. Drugi egzemplarz liczylby kazdy skan dwa razy, dlatego nie zostal uruchomiony.") from None
        self._fd = fd
        return self

    @property
    def zajeta(self) -> bool:
        return self._fd is not None

    def zwolnij(self) -> None:
        fd, self._fd = self._fd, None
        if fd is None:
            return
        try:
            if os.name == "nt":
                import msvcrt  # noqa: PLC0415

                os.lseek(fd, 0, os.SEEK_SET)
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        except OSError:
            pass
        finally:
            os.close(fd)


_SHA16 = re.compile(r"[0-9a-f]{16}")
_NAZWA_PLIKU = re.compile(r"\.[A-Za-z][A-Za-z0-9]{0,4}$")
_SLAD_MODULU = re.compile(r'File "(?:[^"\n]*[\\/])?([^"\\/\n]+\.py)"')
ZNACZNIK_PLIKU = "<plik>"
LOGGERY_Z_FILTREM = ("__main__", "stanowisko", "stanowisko.aplikacja", "stanowisko.kontroler_api", "stanowisko.scanner", "stanowisko.silnik",
                     "stanowisko.session", "stanowisko.baza", "stanowisko.uklad", "stanowisko.ustawienia", "stanowisko.dzien_skanera_rdzen")


class FiltrNazw(logging.Filter):
    """P5: wpisy logu bez nazw plikow skanow i projektow (nazwy zlecen bywaja nazwiskami) - takze z modulow ``scanner``
    i ``silnik``, ktorych kodu ta paczka nie zmienia. Argument wpisu, ktory jest sciezka albo nazwa pliku, staje sie skrotem
    ``sha16`` skanu (gdy znany: z ``zapamietaj`` albo z tego samego wpisu, np. "nowy skan nr 3: <nazwa> sha16=...") albo
    znacznikiem ``<plik>``; w calym tekscie (takze slad wyjatku) znane nazwy -> ``sha16``, sciezki -> ``<sciezka>``
    (``baza.bez_sciezek``), sciezki modulow programu w sladzie wyjatku -> sama nazwa modulu. Zmienia sam wpis, wiec dziala
    dla kazdego odbiorcy (plik logu, konsola, ``caplog``), gdy jest filtrem loggera (``konfiguruj_logi``)."""

    LIMIT = 4000  # tyle ostatnich nazw plikow pamietanych do zamiany na sha16

    def __init__(self) -> None:
        super().__init__()
        self._znane: collections.OrderedDict = collections.OrderedDict()
        self._zamek = threading.Lock()

    def zapamietaj(self, plik: Any, sha16: str | None) -> None:
        if not plik or not sha16:
            return
        p = Path(os.fspath(plik))
        with self._zamek:
            for nazwa in {str(plik), p.as_posix(), p.name, p.stem}:
                if len(nazwa) >= 3:
                    self._znane[nazwa] = sha16
                    self._znane.move_to_end(nazwa)
            while len(self._znane) > self.LIMIT:
                self._znane.popitem(last=False)

    @staticmethod
    def _jak_plik(a: Any) -> bool:
        return isinstance(a, os.PathLike) or (isinstance(a, str) and ("/" in a or "\\" in a or bool(_NAZWA_PLIKU.search(a))))

    def _argument(self, a: Any, sha16: str | None) -> Any:
        if not self._jak_plik(a):
            return a
        tekst = os.fspath(a) if isinstance(a, os.PathLike) else a
        with self._zamek:
            znany = self._znane.get(str(tekst)) or self._znane.get(Path(str(tekst)).name)
        return znany or sha16 or ZNACZNIK_PLIKU

    def oczysc(self, tekst: str) -> str:
        with self._zamek:
            nazwy = sorted(self._znane.items(), key=lambda kv: len(kv[0]), reverse=True)
        for nazwa, sha16 in nazwy:
            if nazwa in tekst:
                tekst = tekst.replace(nazwa, sha16)
        return B.bez_sciezek(_SLAD_MODULU.sub(r'File "\1"', tekst))

    def filter(self, record: logging.LogRecord) -> bool:
        if getattr(record, "bez_nazw", False):
            return True
        try:
            args = record.args
            if isinstance(args, dict):
                record.args = {k: self._argument(v, None) for k, v in args.items()}
            elif args:
                sha16 = next((a for a in args if isinstance(a, str) and _SHA16.fullmatch(a)), None)
                if sha16 is not None:
                    for a in args:
                        if self._jak_plik(a):
                            self.zapamietaj(a, sha16)
                record.args = tuple(self._argument(a, sha16) for a in args)
            record.msg, record.args = self.oczysc(record.getMessage()), None
            if record.exc_info and not record.exc_text:
                record.exc_text = logging.Formatter().formatException(record.exc_info)
            if record.exc_text:
                record.exc_text = self.oczysc(record.exc_text)
            if record.stack_info:
                record.stack_info = self.oczysc(record.stack_info)
        except Exception:  # noqa: BLE001 - filtr logu nie moze zatrzymac programu; wpis bez tresci zamiast nazwy
            record.msg, record.args, record.exc_info, record.exc_text = f"{record.levelname}: wpis logu pominiety (blad filtra nazw)", None, None, None
        record.bez_nazw = True
        return True


FILTR_NAZW = FiltrNazw()  # jeden na proces: Aplikacja dopisuje nazwy plikow skanow, konfiguruj_logi wlacza go w loggerach


def pliki_stl(folder: Path) -> int:
    """Liczba plikow STL puli w ``folder`` - ta sama regula, co ``synth.pliki_projektow`` (podfoldery tak, foldery ``_*`` nie),
    bez ladowania bibliotek obliczen do procesu okna."""
    folder = Path(folder)
    return sum(1 for p in folder.rglob("*") if p.suffix.lower() == ".stl" and p.is_file()
               and not any(cz.startswith("_") for cz in p.relative_to(folder).parts[:-1]))


def katalog_z_ustawien(ust: dict, klucz: str) -> Path:
    return B.sciezka_z_ustawien(ust, klucz)


def utworz_ramki(ust: dict, katalog_danych: str | Path) -> tuple:
    """E3-A12: klienci ramek z ``[ramki]`` (``indicate.Indicate.z_ustawien``; identyfikator laptopa w ``katalog_danych`` - folder
    bazy, nie katalog programu). Zwraca (Indicate albo None, ostrzezenia); zle ustawienia ramek = None + ostrzezenie (program
    dziala bez ramek). Watki klientow startuja dopiero w ``KontrolerSesji.podlacz_ramki``."""
    from . import indicate as IND  # noqa: PLC0415 - biblioteka standardowa + pakiet ``ramka``

    try:
        ind = IND.Indicate.z_ustawien(ust, katalog_danych=katalog_danych)
    except Exception as e:  # noqa: BLE001 - zly klucz, zly host, brak pakietu ramka: praca bez ramek
        return None, [f"ramki niepodlaczone ({type(e).__name__}): {B.bez_sciezek(str(e))[:200]}"]
    ostrzezenia: list = []
    for k in ind.klienci():
        ostrzezenia += [o for o in k.stan().get("ostrzezenia") or () if o not in ostrzezenia]
    return ind, ostrzezenia


def utworz_excel(ust: dict, baza: B.Baza) -> tuple:
    """E3-A12: Excel z ``[excel]`` (``excel.Excel.z_ustawien`` z ``baza`` - X4 sprawdzane w ``sesje_pieca``); polaczenie COM dopiero
    przy pierwszym odczycie arkusza (brak Excela nie przerywa startu). Zwraca (Excel albo None, ostrzezenia)."""
    try:
        ex = EX.Excel.z_ustawien(ust, baza=baza)
    except Exception as e:  # noqa: BLE001
        return None, [f"Excel niepodlaczony ({type(e).__name__}): {B.bez_sciezek(str(e))[:200]}"]
    return ex, list(ex.ostrzezenia)


class Aplikacja(K.KontrolerSesji):
    """Prawdziwy kontroler programu "Stanowisko". Uzycie (watek okna)::

        k = Aplikacja(ust)          # otwiera baze i sesje; niczego jeszcze nie obserwuje
        k.start()                   # silnik, wznowienie zadan, obserwator folderu z nadrabianiem
        ... k.przetworz() co ok. 30 ms (``kontroler_api.lacznik_qt`` robi to zegarem Qt) ...
        k.zamknij()                 # scanner.stop(), silnik.stop(), zapis zadan niezakonczonych, zamkniecie bazy

    Parametry do testow: ``zegar``, ``funkcja_analizy`` (``"modul:funkcja"`` zamiast ``porownaj``), ``start_skanu`` (akcja
    DW5; domyslnie atrapa ze ``scanner``), ``parametry_scannera`` / ``parametry_silnika`` (nadpisuja wartosci z ustawien).
    E3-A12: ``ramki`` - True = klienci ramek z ustawien (``main``), obiekt ``indicate.Indicate`` (testy), False / None = bez ramek;
    ``excel`` - True = Excel z ustawien (COM), ``excel.Excel`` albo zrodlo arkusza (obiekt / funkcja - testy), False / None = bez.
    ``blokada`` - zajeta wczesniej ``BlokadaStanowiska`` (``main``); bez niej konstruktor zajmuje ja sam, ZANIM otworzy baze
    (drugi egzemplarz na tej samej bazie = ``ProgramJuzDziala``, B1), a ``zamknij`` ja zwalnia.
    """

    def __init__(self, ust: dict, *, tryb: str | None = None, zegar: Callable[[], dt.datetime] | None = None, start_skanu=None,
                 funkcja_analizy: str = SI.FUNKCJA_ANALIZY, parametry_scannera: dict | None = None, parametry_silnika: dict | None = None,
                 blokada: BlokadaStanowiska | None = None, ramki: Any = False, excel: Any = False):
        self._ramki_param, self._excel_param = ramki, excel
        self._blokada = blokada if blokada is not None else BlokadaStanowiska(B.sciezka_bazy(ust))
        self._blokada.zajmij()  # B1: przed otwarciem bazy i obserwacja folderu
        try:
            baza = B.otworz(B.sciezka_bazy(ust), zegar=zegar)
        except BaseException:
            self._blokada.zwolnij()
            raise
        try:
            sesja = SE.Sesja.z_ustawien(ust, baza, zegar=zegar, wersja_programu=WERSJA_PROGRAMU)
            super().__init__(sesja, ust, tryb=tryb, zegar=zegar)
        except BaseException:
            baza.zamknij()
            self._blokada.zwolnij()
            raise
        self.katalog_danych = baza.plik.parent
        self.folder_skanera = katalog_z_ustawien(ust, "folder_eksportu_skanera")
        self.katalog_podgladow = katalog_z_ustawien(ust, "podglady")
        self.katalog_logow = katalog_z_ustawien(ust, "logi")
        self.pula_cache = katalog_z_ustawien(ust, "pula_cache")
        self._akcja_startu = start_skanu if start_skanu is not None else SC.AtrapaStartuSkanu()
        self._funkcja_analizy = funkcja_analizy
        self._parametry_scannera = dict(parametry_scannera or {})
        self._parametry_silnika = dict(parametry_silnika or {})
        self.ponow_plik_niedostepny = int(ust["silnik"]["ponow_plik_niedostepny"])
        self.scanner: SC.Scanner | None = None
        self.silnik: SI.Silnik | None = None
        self._uruchomiony = False
        self._zamykanie = False
        self._skrzynka: queue.Queue = queue.Queue()  # z watkow obserwatora i liczenia puli: (rodzaj, dane)
        self._zlecone: dict[int, Zlecenie] = {}  # zadanie_id silnika -> zlecenie (w toku albo w kolejce silnika)
        self._wstrzymane: list[Zlecenie] = []  # czekaja na pule projektow albo na silnik
        self._do_zapisu: list[DoZapisu] = []  # P1 / P8: wyniki i bledy, ktorych nie udalo sie zapisac - ponawiane z rosnacym odstepem
        self._do_sprawdzenia: list[tuple] = []  # P3: (zlecenie, zdarzenie bledu, nr liczenia puli) - blad analizy czeka na liczenie puli
        self._w_toku: int | None = None
        self._analiza: K.Postep | None = None
        self._silnik_gotowy = False
        self._silnik_nie_startuje = False
        self._starty_skanu = 0
        self._ostatni_start_skanu: str | None = None
        self._czeka_na_skan = False
        self._nadrobione = 0  # skany zapisane, gdy program nie dzialal, zlecone do analizy (nadrabianie)
        self._wznowione = 0  # zadania zapisane przy zamknieciu, zlecone ponownie
        self._ostatnia_kontrola = 0.0
        self._obraz_skanera: tuple | None = None
        # pula projektow (poziom 1): folder + wspolczynnik reczny
        self._pula_folder: Path | None = katalog_z_ustawien(ust, "folder_cyrkon")
        self._pula_wspolczynnik: float | None = None
        self._pula_liczba: int | None = None
        self._pula_stan = "liczenie"
        self._pula_czas: str | None = None
        self._pula_nr = 0  # numer liczenia: wynik starszego liczenia jest pomijany
        self._liczenie_puli = False  # trwa liczenie o numerze _pula_nr (D4: nie uruchamiac drugiego cichego)
        self._pula_ponownie = False  # po biezacym liczeniu policzyc jeszcze raz (zmiana w trakcie liczenia)
        self._wczytaj_pule()

    # --- start -----------------------------------------------------------------------------------
    def start(self) -> None:
        """Uruchamia silnik, zleca zadania zapisane przy zamknieciu i wlacza obserwator folderu z nadrabianiem."""
        if self._uruchomiony or self._zamkniety:
            return
        s, ust = self._parametry_silnika, self.ust
        self.katalog_logow.mkdir(parents=True, exist_ok=True)
        self._sprzatnij_podglady()  # P9: przed silnikiem - zaden nowy plik nie zostanie usuniety
        self.silnik = SI.Silnik(**{
            "ust": ust, "funkcja": self._funkcja_analizy, "limit_zadania_s": float(ust["silnik"]["limit_zadania_s"]),
            "czekaj_na_plik_s": float(ust["silnik"]["czekaj_na_plik_s"]), "pamiec_linii": self.pula_cache if ust["silnik"]["pamiec_linii"] else None,
            "plik_logu": self.katalog_logow / PLIK_LOGU_SILNIKA, **s})
        self.silnik.start()
        self._uruchomiony = True
        for nazwa in ust.get("plytki") or {}:  # uklady plytek (i numpy) wczytane teraz, a nie w petli okna przy pierwszej plytce
            self._uklad(nazwa)
        self._policz_pule()
        wznowione = self._wczytaj_zadania()
        self._wznowione = len(wznowione)
        znane = [(w["plik"], w["rozmiar"], w["czas_pliku"]) for w in self.sesja.baza.wiersze("SELECT plik, rozmiar, czas_pliku FROM skany")]
        znane += [(z.plik, z.rozmiar, SC.czas_pliku_iso(z.mtime_ns)) for z in wznowione if z.mtime_ns is not None]
        for z in wznowione:  # przed obserwatorem: powtorka z nadrabiania zostanie odsiana po sha16 zadania w kolejce
            FILTR_NAZW.zapamietaj(z.plik, z.sha16)
            self._nowy_skan(z)
        sc, p = ust["scanner"], self._parametry_scannera
        self.scanner = SC.Scanner(
            self.folder_skanera, na_skan=lambda z: self._skrzynka.put(("skan", z)), na_odrzucenie=lambda o: self._skrzynka.put(("odrzucenie", o)),
            na_oczekiwanie=lambda o: self._skrzynka.put(("oczekiwanie", o)), znane=SC.ZnanePliki(znane), start_skanu=self._akcja_startu,
            **{"wzorzec_pliku": sc["wzorzec_pliku"], "rekurencyjnie": sc["rekurencyjnie"], "stabilizacja_ms": sc["stabilizacja_ms"],
               "min_rozmiar_mb": sc["min_rozmiar_mb"], "min_trojkatow": sc["min_trojkatow"], "obserwator": sc["obserwator"], **p})
        self.scanner.start()
        (self.katalog_danych / PLIK_ZADAN).unlink(missing_ok=True)  # zadania sa juz w kolejce; po awarii wroca przez nadrabianie
        self.sesja.baza.zdarzenie("system", "program_start", {"wersja": WERSJA_PROGRAMU, "wznowione": len(wznowione), "znane_pliki": len(znane)},
                                  czas=self._teraz())
        if wznowione:
            self._komunikat("wznowiono", id_="wznowiono", ile=len(wznowione))
        LOG.info("stanowisko: start, zadan wznowionych %d, plikow znanych %d", len(wznowione), len(znane))
        self._podlacz_ramki_i_excel()
        self._odswiez()

    def _podlacz_ramki_i_excel(self) -> None:
        """E3-A12: ramki i Excel wg parametrow konstruktora. Blad = ostrzezenie (log + komunikat), program dziala dalej."""
        ramki, excel = self._ramki_param, self._excel_param
        try:
            if ramki is True:
                ramki, ostrzezenia = utworz_ramki(self.ust, self.katalog_danych)
                for o in ostrzezenia:
                    LOG.warning("stanowisko: ramki - %s", o)
                if ramki is None:
                    self._komunikat("ramka_blad", id_="ramka_blad:ustawienia", ramka="W / P", powod="; ".join(ostrzezenia))
            if ramki not in (None, False):
                self.stan()  # stan gotowy: plan pieca idzie do klienta przed pierwszym kontaktem z ramka
                self.podlacz_ramki(ramki)
        except Exception:  # noqa: BLE001
            LOG.exception("stanowisko: ramek nie da sie podlaczyc")
        try:
            if excel is True:
                excel, ostrzezenia = utworz_excel(self.ust, self.sesja.baza)
                for o in ostrzezenia:
                    LOG.warning("stanowisko: excel - %s", o)
            elif excel not in (None, False) and not isinstance(excel, EX.Excel):
                excel = EX.Excel.z_ustawien(self.ust, zrodlo=excel, baza=self.sesja.baza)
            if excel not in (None, False):
                self.podlacz_excel(excel)
        except Exception:  # noqa: BLE001
            LOG.exception("stanowisko: Excela nie da sie podlaczyc")

    def _sprzatnij_podglady(self) -> int:
        """P9: przy starcie usuwa z ``dane/podglady`` kopie wynikow silnika (``*_wynik.json`` - zawieraja folder puli; zadna
        nie jest potrzebna, obowiazuje plik sesji bez sciezek) i pliki ``*_podglad.npz``, do ktorych nie prowadzi wpis
        ``podglad`` w dzienniku (po awarii, odrzuconym wyniku, zamknieciu z wynikiem niezapisanym). Zwraca liczbe usunietych."""
        katalog = self.katalog_podgladow
        if not katalog.is_dir():
            return 0
        znane = set()
        for w in self.sesja.baza.wiersze("SELECT dane FROM zdarzenia WHERE typ = 'podglad'"):
            try:
                znane.add(json.loads(w["dane"])["plik"])
            except (TypeError, ValueError, KeyError):
                continue
        usuniete = 0
        for p in katalog.iterdir():
            if p.name.endswith("_wynik.json") or (p.name.endswith("_podglad.npz") and p.name not in znane):
                try:
                    p.unlink()
                    usuniete += 1
                except OSError as e:
                    LOG.warning("stanowisko: osieroconego pliku podgladu nie da sie usunac (%s)", type(e).__name__)
        if usuniete:
            LOG.info("stanowisko: usuniete osierocone pliki w katalogu podgladow: %d", usuniete)
        return usuniete

    @staticmethod
    def _usun_pliki_wyniku(e: Any, podglad: bool) -> None:
        """P9: kopia wyniku z silnika (zawiera folder puli) zawsze; plik podgladu - gdy nie zostal powiazany ze skanem."""
        pliki = (getattr(e, "pliki", None) or {}) if e is not None else {}
        for klucz in ("wynik", "podglad") if podglad else ("wynik",):
            if pliki.get(klucz):
                try:
                    Path(pliki[klucz]).unlink(missing_ok=True)
                except OSError:
                    pass

    def _wczytaj_zadania(self) -> list[Zlecenie]:
        plik = self.katalog_danych / PLIK_ZADAN
        if not plik.is_file():
            return []
        try:
            dane = json.loads(plik.read_text(encoding="utf-8"))
            return [Zlecenie(plik=str(z["plik"]), sha16=str(z["sha16"]), rozmiar=z.get("rozmiar"), mtime_ns=z.get("mtime_ns"),
                             trojkaty=z.get("trojkaty"), tryb=SE.sprawdz_tryb(z.get("tryb") or self.tryb), numer=z.get("numer"), wznowiony=True)
                    for z in dane["zadania"]]
        except (OSError, ValueError, KeyError, TypeError) as e:
            LOG.warning("stanowisko: pliku zadan niezakonczonych nie da sie odczytac (%s) - zalegle skany wroca przez nadrabianie folderu",
                        type(e).__name__)
            return []

    def _zapisz_zadania(self, zadania: list[Zlecenie]) -> None:
        plik = self.katalog_danych / PLIK_ZADAN
        if not zadania:
            plik.unlink(missing_ok=True)
            return
        tmp = plik.with_suffix(".tmp")
        tmp.write_text(json.dumps({"wersja": 1, "zapisano": self._teraz(), "zadania": [z.do_zapisu() for z in zadania]}, ensure_ascii=False, indent=1),
                       encoding="utf-8")
        os.replace(tmp, plik)

    # --- pula projektow (poziom 1 planu) -----------------------------------------------------------
    def _wczytaj_pule(self) -> None:
        try:
            dane = json.loads((self.katalog_danych / PLIK_PULI).read_text(encoding="utf-8"))
            self._pula_folder = Path(dane["folder"]) if dane.get("folder") else None
            w = dane.get("wspolczynnik")
            self._pula_wspolczynnik = float(w) if w is not None else None
        except FileNotFoundError:
            return
        except (OSError, ValueError, KeyError, TypeError) as e:
            LOG.warning("stanowisko: pliku ustawien puli nie da sie odczytac (%s) - pula z ustawienia.toml", type(e).__name__)

    def _policz_pule(self, ciche: bool = False) -> None:
        """Liczy pliki STL puli w watku pomocniczym (folder sieciowy moze odpowiadac dlugo); wynik wraca przez skrzynke.
        ``ciche``: odswiezenie po skanie, wyniku albo bledzie analizy (P3) - stan puli zostaje do czasu nowego wyniku (skany
        nie czekaja na liczenie); gdy liczenie juz trwa, nie startuje drugiego watku, tylko zamawia kolejne liczenie po nim
        (D4: folder sieciowy, ktory nie odpowiada, nie mnozy wiszacych watkow)."""
        if ciche and self._liczenie_puli:
            self._pula_ponownie = True
            return
        self._pula_nr += 1
        if self._pula_folder is None:
            self._pula_stan, self._pula_liczba, self._liczenie_puli = "nieustawiona", None, False
            self._rozstrzygnij_sprawdzenia(self._pula_nr)
            self._komunikat_puli("nieustawiona", self._czeka_na_pule())
            return
        if not ciche:
            self._pula_stan = "liczenie"
        nr, folder = self._pula_nr, self._pula_folder
        self._liczenie_puli = True

        def licz() -> None:
            try:
                wynik = ("pula", (nr, pliki_stl(folder) if folder.is_dir() else None))
            except Exception:  # noqa: BLE001 - D4: kazdy blad (takze ValueError dla zlej sciezki) = brak folderu, nigdy wiszace "liczenie"
                wynik = ("pula", (nr, None))
            self._skrzynka.put(wynik)

        threading.Thread(target=licz, name="pula-liczenie", daemon=True).start()

    def _pula_policzona(self, nr: int, liczba: int | None) -> None:
        if nr != self._pula_nr:
            return
        self._liczenie_puli = False
        self._pula_liczba, self._pula_czas = liczba, self._teraz()
        self._pula_stan = "brak_folderu" if liczba is None else ("gotowa" if liczba > 0 else "pusta")
        self._rozstrzygnij_sprawdzenia(nr)
        if self._pula_stan == "gotowa":
            if not self._do_sprawdzenia:
                self._zwolnij_wstrzymane()
        else:
            self._wstrzymaj_kolejke_silnika()
        self._komunikat_puli(self._pula_stan, self._czeka_na_pule())
        if self._pula_ponownie:
            self._pula_ponownie = False
            self._policz_pule(ciche=True)

    def _czeka_na_pule(self) -> int:
        return len(self._wstrzymane) + len(self._do_sprawdzenia)

    def _sprawdz_pule_po_bledzie(self, z: Zlecenie, e: Any) -> None:
        """P3: blad analizy moze wynikac z puli oproznionej albo znikajacej po policzeniu. Zanim skan dostanie ``blad``, pula
        jest liczona od nowa; wynik liczenia rozstrzyga: pula niepusta = blad analizy, pusta / brak folderu = skan czeka."""
        nr_min = self._pula_nr + 1  # nastepne liczenie: uruchamiane teraz albo zaraz po biezacym
        self._do_sprawdzenia.append((z, e, nr_min))
        self._policz_pule(ciche=True)

    def _rozstrzygnij_sprawdzenia(self, nr: int) -> None:
        gotowe = [x for x in self._do_sprawdzenia if x[2] <= nr]
        self._do_sprawdzenia = [x for x in self._do_sprawdzenia if x[2] > nr]
        for z, e, _ in gotowe:
            if self._pula_stan == "gotowa":
                self._zapisz_blad(z, e.rodzaj, self._bez_nazw(e.blad, z))
            else:  # pula pusta / brak folderu / nieustawiona: skan czeka na pule (zamiast "blad analizy")
                self.sesja.baza.zdarzenie("silnik", "skan_czeka_na_pule", {"sha16": z.sha16, "pula": self._pula_stan}, czas=self._teraz())
                self._wstrzymane.append(z)

    def _wstrzymaj_kolejke_silnika(self) -> None:
        """P3: pula okazala sie pusta / bez folderu - zadania czekajace w kolejce silnika (jeszcze nie ruszyly) wracaja do
        wstrzymanych, zamiast po kolei konczyc sie bledem analizy."""
        for nr in sorted(self._zlecone):
            if nr != self._w_toku and self.silnik is not None and self.silnik.anuluj(nr):
                self._wstrzymane.append(self._zlecone.pop(nr))

    def ustaw_pule(self, folder: str | None, wspolczynnik: float | None = None) -> K.Odpowiedz:
        """Folder projektow i wspolczynnik skurczu wpisane recznie (None = domyslny dla rozpoznanego typu plytki). Walidacja
        wspolna z atrapa (``_sprawdz_pule``): ``zly_wspolczynnik``, ``zle_argumenty``; folder None = pula ``nieustawiona``.
        ``dane`` = stan puli po poleceniu (``liczenie`` / ``nieustawiona``)."""
        wynik = self._sprawdz_pule(folder, wspolczynnik)
        if isinstance(wynik, K.Odpowiedz):
            return wynik
        folder, wspolczynnik = wynik
        self._pula_folder = Path(folder) if folder else None
        self._pula_wspolczynnik = wspolczynnik
        try:
            self.katalog_danych.mkdir(parents=True, exist_ok=True)
            (self.katalog_danych / PLIK_PULI).write_text(json.dumps({"folder": str(self._pula_folder) if self._pula_folder else None,
                                                                    "wspolczynnik": wspolczynnik}, ensure_ascii=False), encoding="utf-8")
        except OSError as e:
            LOG.warning("stanowisko: ustawien puli nie da sie zapisac (%s)", type(e).__name__)
        self.sesja.baza.zdarzenie("pula", "pula_ustawiona", {"wspolczynnik": wspolczynnik, "folder_ustawiony": self._pula_folder is not None,
                                                            "operator": self.sesja.operator}, czas=self._teraz())  # D8: kto zmienil
        return self.odswiez_pule()

    def odswiez_pule(self) -> K.Odpowiedz:
        """Liczy pule od nowa (w tle); po policzeniu skany wstrzymane z braku projektow ida do analizy. ``dane`` = stan puli
        po poleceniu (``liczenie``, a bez folderu ``nieustawiona``)."""
        if self._zamkniety:
            return self._zamkniety_odp()
        self._usun_komunikat("odmowa:zly_wspolczynnik")
        self._policz_pule()
        self._odswiez()
        return K.Odpowiedz(True, dane=self._pula_stan)

    def _opis_puli(self) -> SI.OpisPuli:
        return SI.OpisPuli(foldery=(str(self._pula_folder),), wspolczynnik=self._pula_wspolczynnik)

    # --- czesc zywa stanu ----------------------------------------------------------------------------
    def _stan_zywy(self) -> dict:
        w_toku = 1 if self._w_toku is not None and self._w_toku in self._zlecone else 0
        napis = ST.STANY_PULI.get(self._pula_stan, "").format(n=self._pula_liczba)
        sc = self.scanner.stan() if self.scanner is not None else {}
        niezapisane = self._niezapisane()
        return {
            "analiza": self._analiza,
            "kolejka": K.Kolejka(w_toku=w_toku, czeka=len(self._zlecone) - w_toku,
                                 wstrzymane=len(self._wstrzymane) + len(self._do_zapisu) + len(self._do_sprawdzenia),
                                 silnik_gotowy=self._silnik_gotowy, niezapisane=len(niezapisane)),
            "pula": K.Pula(folder=str(self._pula_folder) if self._pula_folder is not None else None, wspolczynnik=self._pula_wspolczynnik,
                           liczba_stl=self._pula_liczba, stan=self._pula_stan, napis=napis, odswiezono=self._pula_czas),
            "skaner": K.Skaner(folder=str(self.folder_skanera), dostepny=bool(sc.get("folder_dostepny")), dziala=bool(sc.get("dziala")),
                               zajete=int(sc.get("zajete") or 0), ostatni_start_skanu=self._ostatni_start_skanu, startow_skanu=self._starty_skanu,
                               czeka_na_skan=self._czeka_na_skan),
            "niezapisane": niezapisane}

    def _niezapisane(self) -> tuple:
        """Pozycje "nie zapisano" dla okna (``kontroler_api.Niezapisany``) z wynikow i bledow czekajacych na zapis."""
        wynik = []
        for d in self._do_zapisu:
            w = (getattr(d.zdarzenie, "wynik", None) or {}) if d.rodzaj == "wynik" else {}
            wynik.append(K.Niezapisany(sha16=d.zlecenie.sha16, rodzaj=d.rodzaj, przyczyna=d.przyczyna, napis=ST.NAPISY_NIEZAPISANE.get(d.przyczyna, ""),
                                       od=d.od, proby=d.proby, numer=w.get("numer"), uklad=w.get("plytka"),
                                       prac=len(w.get("gniazda") or []) if d.rodzaj == "wynik" else None))
        return tuple(wynik)

    def _katalog_podgladow(self) -> Path | None:
        return self.katalog_podgladow

    # --- start skanu (DW5) -------------------------------------------------------------------------
    def start_skanu(self) -> K.Odpowiedz:
        """Akcja "start skanu": wola funkcje podana obserwatorowi (domyslnie atrapa) dokladnie raz."""
        if self._zamkniety or self.scanner is None:
            return K.Odpowiedz(False, ST.tekst_komunikatu("program_zamkniety")[2], "program_zamkniety")
        udany = self.scanner.start_skanu()
        self._starty_skanu += 1
        self._ostatni_start_skanu = self._teraz()
        self._czeka_na_skan = udany
        self.sesja.baza.zdarzenie("ui", "start_skanu", {"udany": udany, "tryb": self.tryb}, czas=self._ostatni_start_skanu)  # tryb: prosba A10
        if not udany:
            return self._odmowa("start_skanu_nieudany")
        self._ramka_w_spacja()  # E3-A12: ramka wieczorna w stan "skanowanie" (gasi poprzedni wynik)
        if self._usun_komunikat("odmowa:start_skanu_nieudany"):
            self._odswiez()  # stara odmowa znika z komunikatow
        else:
            self._odswiez_zywe()
        return K.Odpowiedz(True)

    # --- zdarzenia z watkow ---------------------------------------------------------------------------
    def przetworz(self, limit_s: float = K.LIMIT_PRZETWARZANIA_S) -> int:
        """Obsluguje zdarzenia obserwatora, silnika i liczenia puli (najwyzej ``limit_s`` naraz); wolac w watku okna."""
        if self._zamkniety or not self._uruchomiony:
            return 0
        t0 = time.monotonic()
        obsluzone = 0
        zmiany: set[str] = set()
        if self._sprawdz_zmiane():
            zmiany.add("stan")
        for d in [x for x in self._do_zapisu if x.nastepna <= t0]:  # P1 / P8: ponowienie zapisu z rosnacym odstepem
            d.nastepna = t0 + odstep_ponowienia(d.proby + 1)  # takze gdy proba skonczy sie nieoczekiwanym wyjatkiem
            zmiany.add(self._bezpiecznie(self._zapisz, d, False))  # pozycja zostaje na liscie, dopoki zapis sie nie uda
        while True:
            bylo = False
            try:
                e = self.silnik.zdarzenia.get_nowait()
            except queue.Empty:
                pass
            else:
                bylo = True
                zmiany.add(self._bezpiecznie(self._zdarzenie_silnika, e))
            try:
                rodzaj, dane = self._skrzynka.get_nowait()
            except queue.Empty:
                pass
            else:
                bylo = True
                zmiany.add(self._bezpiecznie(self._zdarzenie_skrzynki, rodzaj, dane))
            if not bylo:
                break
            obsluzone += 1
            if time.monotonic() - t0 > limit_s:
                break
        if t0 - self._ostatnia_kontrola >= OKRES_KONTROLI_S:
            self._ostatnia_kontrola = t0
            zmiany.add(self._kontrola_skanera())
        try:
            obsluzone += self._przetworz_ramki()  # E3-A12: krok Excela, zdarzenia i stan ramek (odswieza stan sama, gdy trzeba)
        except Exception:  # noqa: BLE001 - recenzja PR #30 D2: blad ramek / Excela nie przerywa obiegu
            LOG.exception("stanowisko: blad obslugi ramek / Excela")
        if "stan" in zmiany:
            self._odswiez()
        elif "zywe" in zmiany:
            self._odswiez_zywe()
        elif "postep" in zmiany:
            self._odswiez_zywe("postep")
        else:
            self._sprawdz_zajetosc()  # rano: limit czasu skanowania minal - "Zamknij piec" znow dostepne (P3)
        return obsluzone

    def _bezpiecznie(self, funkcja: Callable[..., str], *argumenty: Any) -> str:
        """Blad obslugi jednego zdarzenia nie zatrzymuje programu: wpis w logu i nastepne zdarzenie. Skan, ktorego zdarzenia
        nie udalo sie obsluzyc, nie ma wyniku w bazie, wiec wroci przez nadrabianie po nastepnym starcie."""
        try:
            return funkcja(*argumenty)
        except Exception:  # noqa: BLE001
            LOG.exception("stanowisko: blad obslugi zdarzenia (%s)", funkcja.__name__)
            return "stan"

    def _kontrola_skanera(self) -> str:
        """Zmiany stanu obserwatora, o ktorych nie ma zdarzen: folder zniknal / wrocil, pliki zajete zostaly zwolnione."""
        sc = self.scanner.stan()
        obraz = (sc["folder_dostepny"], sc["dziala"], sc["zajete"])
        zmiana = obraz != self._obraz_skanera
        self._obraz_skanera = obraz
        if sc["zajete"] == 0 and self._usun_komunikat("plik_zajety:skaner"):
            zmiana = True
        if sc["folder_dostepny"]:
            zmiana = self._usun_komunikat("folder_skanera") or zmiana
        elif "folder_skanera" not in self._komunikaty:
            self._komunikat("folder_skanera_niedostepny", id_="folder_skanera")
            zmiana = True
        return "stan" if zmiana else ""

    def _zdarzenie_skrzynki(self, rodzaj: str, dane: Any) -> str:
        if rodzaj == "pula":
            self._pula_policzona(*dane)
            return "stan"
        if rodzaj == "skan":
            self._czeka_na_skan = False
            self._usun_komunikat("plik_zajety:skaner")
            z = Zlecenie.ze_zdarzenia(dane, self.tryb)
            FILTR_NAZW.zapamietaj(z.plik, z.sha16)  # P5: dalsze wpisy logu z ta nazwa pliku -> sha16
            self.sesja.baza.zdarzenie("scanner", "nowy_skan", {"sha16": z.sha16, "rozmiar": z.rozmiar, "trojkaty": z.trojkaty, "zastany": z.zastany,
                                                               "ponowny": bool(dane.ponowny), "duplikat": bool(dane.duplikat)}, czas=self._teraz())
            self._nowy_skan(z)
            return "stan"
        if rodzaj == "odrzucenie":
            if dane.powod == "poza_wzorcem":
                return ""  # inne pliki w folderze skanera to nie awaria
            self.sesja.baza.zdarzenie("scanner", "plik_odrzucony", {"powod": dane.powod, "rozmiar": dane.rozmiar}, czas=self._teraz())
            self._komunikat("plik_odrzucony", powod=ST.POWODY_ODRZUCENIA.get(dane.powod, dane.powod))
            return "stan"
        if rodzaj == "oczekiwanie":
            self._komunikat("plik_zajety", id_="plik_zajety:skaner", od_s=int(dane.od_s))
            return "stan"
        return ""

    def _skan_z_wynikiem(self, sha16: str) -> dict | None:
        """Skan tej samej tresci, ktory MA wynik w bazie (kazdy status poza ``blad``) - wtedy skanu nie liczy sie drugi raz."""
        return self.sesja.baza.wiersz("SELECT id, plik FROM skany WHERE sha16 = ? AND status != ? ORDER BY id DESC LIMIT 1", (sha16, SE.STATUS_BLAD))

    def _w_kolejce(self) -> list:
        """Wszystkie skany prowadzone przez kontroler, ktore nie maja jeszcze zapisu w bazie."""
        return (list(self._zlecone.values()) + self._wstrzymane + [d.zlecenie for d in self._do_zapisu]
                + [x[0] for x in self._do_sprawdzenia])

    def _nowy_skan(self, z: Zlecenie) -> None:
        """Skan do analizy - o ile ta sama tresc nie ma juz wyniku w bazie i nie czeka w kolejce (zaden skan liczony dwa razy).
        Ta sama tresc pod INNA sciezka, gdy skan czeka w kolejce = plik przemianowany: zadanie przejmuje nowa sciezke (P2)."""
        baza = self.sesja.baza
        jest = self._skan_z_wynikiem(z.sha16)
        if jest is not None:  # powtorka wobec skanu Z WYNIKIEM (skan ``blad`` wyniku nie ma - wolno liczyc ponownie)
            przemianowany = bool(jest["plik"]) and _klucz_sciezki(jest["plik"]) != _klucz_sciezki(z.plik) and not _istnieje(jest["plik"])
            baza.zdarzenie("scanner", "skan_powtorzony", {"sha16": z.sha16, "zastany": z.zastany, "wznowiony": z.wznowiony,
                                                          "przemianowany": przemianowany}, skan_id=jest["id"], czas=self._teraz())
            if not z.zastany and not z.wznowiony and not przemianowany:  # zmiana nazwy pliku to nie drugi skan
                self._komunikat("skan_juz_jest", skan_id=jest["id"])
            return
        x = next((x for x in self._w_kolejce() if x.sha16 == z.sha16), None)
        if x is not None:
            inna = _klucz_sciezki(x.plik) != _klucz_sciezki(z.plik)
            baza.zdarzenie("scanner", "skan_powtorzony_w_kolejce", {"sha16": z.sha16, "zastany": z.zastany, "inna_sciezka": inna}, czas=self._teraz())
            if inna:
                if all(_klucz_sciezki(p) != _klucz_sciezki(z.plik) for p, _ in x.zastepcze):
                    x.zastepcze.append((z.plik, z.mtime_ns))
                self._przejmij_przemianowany(x)
            return
        z.znacznik_w = self._ramka_w_nowy_skan(z.tryb)  # E3-A12: znacznik dopiero dla skanu zleconego (recenzja PR #30 P6)
        self._zlec(z)
        self._policz_pule(ciche=True)  # P3: pula sprawdzana przy kazdym nowym skanie (w tle; pusta = kolejne skany czekaja)

    def _przejmij_przemianowany(self, x: Zlecenie) -> None:
        """P2: plik skanu czekajacego w kolejce zmienil nazwe (stara sciezka zniknela) - zadanie przechodzi na nowa sciezke:
        wstrzymane od razu, czekajace w kolejce silnika (jeszcze nie ruszylo) - anulowane i zlecone ponownie. Zadanie w toku
        nie jest ruszane: silnik analizuje kopie, a gdy nie zdazyl jej zrobic ("brak pliku"), ``_blad_analizy`` zleca ponownie."""
        if _istnieje(x.plik) or not any(_istnieje(p) for p, _ in x.zastepcze):
            return
        nr = next((n for n, v in self._zlecone.items() if v is x), None)
        if nr is None:  # wstrzymane, czeka na zapis albo na liczenie puli: sama zmiana sciezki
            x.przejmij_zastepcza()
            self.sesja.baza.zdarzenie("scanner", "skan_przemianowany", {"sha16": x.sha16}, czas=self._teraz())
            return
        if nr != self._w_toku and self.silnik is not None and self.silnik.anuluj(nr):
            del self._zlecone[nr]
            x.przejmij_zastepcza()
            self.sesja.baza.zdarzenie("scanner", "skan_przemianowany", {"sha16": x.sha16}, czas=self._teraz())
            self._zlec(x)

    def _zlec(self, z: Zlecenie) -> None:
        if self._zamykanie or self._silnik_nie_startuje or self._pula_stan != "gotowa" or self._do_sprawdzenia:
            self._wstrzymane.append(z)  # pula niegotowa albo sprawdzana po bledzie analizy (P3): skan czeka
            if not self._zamykanie:
                self._komunikat_puli(self._pula_stan, self._czeka_na_pule())
            return
        try:
            nr = self.silnik.zlec(SI.ZadanieAnalizy(skan=Path(z.plik), pula=self._opis_puli(), tryb=z.tryb, numer=z.numer, skan_sha16=z.sha16,
                                                    wyjscie=self.katalog_podgladow))
        except SI.SilnikZatrzymany:
            self._wstrzymane.append(z)  # silnik sie zatrzymuje: zadanie zostanie zapisane jako niezakonczone
            return
        self._zlecone[nr] = z
        if z.zastany and not z.wznowiony:  # skan zapisany, gdy program nie dzialal: technik widzi, ze program go dokancza
            self._nadrobione += 1
            self._komunikat("wznowiono", id_="wznowiono", ile=self._wznowione + self._nadrobione)

    def _zwolnij_wstrzymane(self) -> None:
        czekajace, self._wstrzymane = self._wstrzymane, []
        for z in czekajace:
            self._zlec(z)

    def _zdarzenie_silnika(self, e: Any) -> str:
        if e.typ == "gotowy":
            self._silnik_gotowy = True
            if self._silnik_nie_startuje:  # proces jednak wystartowal: skany wstrzymane ida do analizy
                self._silnik_nie_startuje = False
                self.sesja.baza.zdarzenie("silnik", "silnik_wrocil", {"wstrzymane": len(self._wstrzymane)}, czas=self._teraz())  # A10 D-R2
                self._usun_komunikat("silnik")
                self._zwolnij_wstrzymane()
                return "stan"
            return "zywe"
        if e.typ == "zatrzymany":
            return ""
        z = self._zlecone.get(e.zadanie_id)
        if z is None:  # zdarzenie zadania, ktorego kontroler juz nie prowadzi
            if e.typ == "wynik":
                self._usun_pliki_wyniku(e, podglad=True)  # P9: pliki silnika bez skanu nie zostaja w dane/podglady
            return ""
        if e.typ == "start":
            self._w_toku = e.zadanie_id
            self._analiza = K.Postep(zadanie_id=e.zadanie_id, etap="", udzial=0.0, od=e.czas, sha16=z.sha16)
            if z.znacznik_w is not None and not z.analiza_w:  # E3-A12: raz na skan (ponowna analiza tego skanu - bez drugiego "analiza")
                z.analiza_w = True
                self._ramka_w_analiza(z.znacznik_w)
            return "postep"
        if e.typ == "postep":
            poczatek = self._analiza.od if self._analiza is not None and self._analiza.zadanie_id == e.zadanie_id else e.czas
            self._analiza = K.Postep(zadanie_id=e.zadanie_id, etap=e.etap, udzial=float(e.udzial), od=poczatek, sha16=z.sha16)
            if e.etap == SI.ETAP_OCZEKIWANIA:
                if f"plik_zajety:{z.sha16}" not in self._komunikaty:
                    self._komunikat("plik_zajety", id_=f"plik_zajety:{z.sha16}", od_s=int(max(0.0, e.czas - poczatek)))
                    return "stan"
            elif self._usun_komunikat(f"plik_zajety:{z.sha16}"):
                return "stan"
            return "postep"
        if e.typ not in ("wynik", "blad"):
            return ""
        del self._zlecone[e.zadanie_id]
        if self._w_toku == e.zadanie_id:
            self._w_toku, self._analiza = None, None
        self._usun_komunikat(f"plik_zajety:{z.sha16}")
        if e.typ == "wynik":
            return self._przyjmij_wynik(z, e)
        return self._blad_analizy(z, e)

    def _przyjmij_wynik(self, z: Zlecenie, e: Any) -> str:
        """Wynik silnika -> sesja (``_zapisz``); nieudany zapis = pozycja "nie zapisano", ponawiana (P1, P8). Kopia wyniku
        zapisana przez silnik (zawiera folder puli) jest usuwana od razu - wynik jest w pamieci, a obowiazuje plik sesji (P9)."""
        self._usun_pliki_wyniku(e, podglad=False)
        return self._zapisz(DoZapisu(zlecenie=z, rodzaj="wynik", zdarzenie=e, od=self._teraz()), True)

    def _zapisz_blad(self, z: Zlecenie, rodzaj: str, opis: str) -> str:
        """Skan ``blad`` w sesji (``_zapisz``); baza zajeta / blad dysku = blad czeka w pamieci i jest zapisywany ponownie bez
        ponownej analizy (P8 - dawniej skan czekal na "Odswiez pule" i liczyl sie od nowa)."""
        return self._zapisz(DoZapisu(zlecenie=z, rodzaj="blad", blad_rodzaj=rodzaj, blad_opis=opis, od=self._teraz()), True)

    def _zapisz(self, d: DoZapisu, nowy: bool) -> str:
        """Jedna proba zapisu wyniku albo bledu. Baza zajeta (``BladBazy``) albo blad zapisu (pelny dysk, blad wejscia / wyjscia:
        ``_blad_zapisu``) = pozycja zostaje w ``_do_zapisu`` z terminem kolejnej proby (rosnacy odstep) i komunikatem
        (``baza_zajeta`` / trwaly ``blad_zapisu``) - skan nie znika z ekranu (P1, P8). Blad danych (wynik, ktorego sesja nie
        umie przyjac) = skan ``blad`` z komunikatem (ponowienie nic by nie dalo)."""
        z = d.zlecenie
        d.proby += 1
        try:
            self._zapis_w_bazie(d)
        except Exception as blad:  # noqa: BLE001 - zaden blad zapisu nie zatrzymuje programu ani nie gubi skanu
            przyczyna = PRZYCZYNA_BAZA_ZAJETA if isinstance(blad, B.BladBazy) else (PRZYCZYNA_BLAD_ZAPISU if _blad_zapisu(blad) else None)
            if przyczyna is not None:
                if nowy:
                    self._do_zapisu.append(d)
                    LOG.warning("stanowisko: %s skanu %s czeka na zapis (%s: %s)", d.rodzaj, z.sha16, przyczyna, type(blad).__name__)
                d.przyczyna, d.nastepna = przyczyna, time.monotonic() + odstep_ponowienia(d.proby)
                self._komunikaty_zapisu(list(self._niezapisane()), nowy=nowy)
                return "stan"
            if d in self._do_zapisu:
                self._do_zapisu.remove(d)
            self._komunikaty_zapisu(list(self._niezapisane()), nowy=False)
            if d.rodzaj != "wynik":  # blad, ktorego nie da sie zapisac z powodu danych - skan wroci przez nadrabianie po restarcie
                LOG.exception("stanowisko: bledu analizy skanu %s nie da sie zapisac", z.sha16)
                return "stan"
            LOG.exception("stanowisko: wyniku skanu %s nie da sie przyjac do sesji", z.sha16)
            self._usun_pliki_wyniku(d.zdarzenie, podglad=True)
            return self._zapisz_blad(z, "analiza", f"wyniku nie da sie zapisac: {type(blad).__name__}")
        if d in self._do_zapisu:
            self._do_zapisu.remove(d)
        self._komunikaty_zapisu(list(self._niezapisane()), nowy=False)  # baza_zajeta / blad_zapisu znikaja, gdy nic nie czeka
        return "stan"

    def _wynik_do_sesji(self, wynik: dict, z: Zlecenie) -> dict:
        """Kopia wyniku dla sesji: pole ``skan`` (nazwa pliku skanu wpisana przez ``porownaj``) -> ``sha16`` skanu - nazwa pliku
        (moze byc nazwiskiem ze zlecenia) zostaje tylko w ``skany.plik``. Slownik z silnika nie jest zmieniany."""
        return {**wynik, "skan": z.sha16} if "skan" in wynik else wynik

    def _zapis_w_bazie(self, d: DoZapisu) -> None:
        """Zapis w JEDNEJ transakcji (``BEGIN IMMEDIATE`` - wylacznosc na zapis): sprawdzenie, czy skan tej samej tresci nie
        ma juz wyniku (B1: twarde zabezpieczenie - drugi egzemplarz programu albo ten sam skan dwa razy nie da dwoch skanow),
        skan z pracami albo skan ``blad`` i wpis w dzienniku. Wyjatek = nic nie zapisano."""
        z, baza = d.zlecenie, self.sesja.baza
        zdarzenie = z.zdarzenie()  # sciezka aktualna (P2: plik przemianowany w kolejce)
        with baza.transakcja():
            jest = self._skan_z_wynikiem(z.sha16)
            if jest is not None:
                baza.zdarzenie("silnik", "wynik_powtorzony", {"sha16": z.sha16, "rodzaj": d.rodzaj}, skan_id=jest["id"], czas=self._teraz())
            elif d.rodzaj == "wynik":
                if z.tryb == SE.TRYB_RANO:  # E3-A7: skan poranny do sesji pieca (A6) - piec otwiera sie sam
                    skan_id = self.rano.przyjmij_wynik(zdarzenie, self._wynik_do_sesji(d.zdarzenie.wynik, z))
                else:
                    skan_id = self.sesja.przyjmij_wynik(zdarzenie, self._wynik_do_sesji(d.zdarzenie.wynik, z), z.tryb)
                self._zapisz_podglad(skan_id, (d.zdarzenie.pliki or {}).get("podglad"))
            else:
                if z.tryb == SE.TRYB_RANO:
                    skan_id = self.rano.przyjmij_blad(zdarzenie, f"{d.blad_rodzaj}: {d.blad_opis}")
                else:
                    skan_id = self.sesja.przyjmij_blad(zdarzenie, f"{d.blad_rodzaj}: {d.blad_opis}", z.tryb)
                # rodzaj bledu takze dla skanu porannego (recenzja PR #26, D5: metryki A10, komunikat z rada)
                baza.zdarzenie("silnik", "blad_analizy_rodzaj", {"rodzaj": d.blad_rodzaj}, skan_id=skan_id, czas=self._teraz())
        if jest is None:
            self._po_skanie(z.tryb)  # P2: skan wieczorny moze zmienic stan punktow (lista brakow liczona od nowa)
            if d.rodzaj == "wynik":  # E3-A12: wynik ostatniego skanu na ramce W (kolory mapy - po zbudowaniu stanu)
                self._ramka_w_wynik(z.znacznik_w, skan_id)
            else:
                self._ramka_w_blad(z.znacznik_w)
        self._usun_komunikat(f"plik_niedostepny:{z.sha16}")
        if d.rodzaj != "wynik":
            return
        if jest is not None:
            self._usun_pliki_wyniku(d.zdarzenie, podglad=True)  # P9: podglad wyniku odrzuconego jako powtorka nie zostaje
            LOG.warning("stanowisko: wynik skanu %s pominiety - ta sama tresc ma juz wynik (skan %d)", z.sha16, jest["id"])
            return
        LOG.info("stanowisko: skan %s przyjety jako %d (%.1f s)", z.sha16, skan_id, d.zdarzenie.czas_s or 0.0)
        if not self._zamykanie:
            self._policz_pule(ciche=True)  # liczba STL na ekranie aktualna po kazdej plytce (silnik i tak czyta folder przy kazdym zadaniu)

    def ponow_zapis(self) -> K.Odpowiedz:
        """18. polecenie (P1): od razu ponawia zapis wszystkich pozycji "nie zapisano"."""
        if self._zamkniety:
            return self._zamkniety_odp()
        for d in list(self._do_zapisu):
            self._bezpiecznie(self._zapisz, d, False)
        self._odswiez()
        if not self._do_zapisu:
            return K.Odpowiedz(True, dane=0)
        przyczyna = self._do_zapisu[-1].przyczyna
        return K.Odpowiedz(False, ST.tekst_komunikatu(przyczyna, ile=len(self._do_zapisu))[2], przyczyna, dane=len(self._do_zapisu))

    def _bez_nazw(self, tekst: str, z: Zlecenie) -> str:
        """Tekst bledu bez nazwy i sciezki pliku skanu oraz bez sciezek (nazwy z puli wycina juz ``silnik``)."""
        plik = Path(z.plik)
        for nazwa in sorted({str(plik), plik.as_posix(), plik.name, plik.stem, plik.parent.name}, key=len, reverse=True):
            if len(nazwa) >= 3:
                tekst = tekst.replace(nazwa, "<skan>")
        return B.bez_sciezek(tekst)

    def _blad_analizy(self, z: Zlecenie, e: Any) -> str:
        LOG.warning("stanowisko: analiza skanu %s nie dala wyniku (%s)", z.sha16, e.rodzaj)
        if e.rodzaj == "plik_zmieniony":  # plik zapisany ponownie przed analiza: nowa tresc ma wlasne zdarzenie, tej juz nie ma
            self.sesja.baza.zdarzenie("silnik", "plik_zmieniony", {"sha16": z.sha16}, czas=self._teraz())
            self._komunikat("plik_zmieniony")
            return "stan"
        if e.rodzaj == "plik_niedostepny" and z.proby < self.ponow_plik_niedostepny:
            z.proby += 1
            self._komunikat("plik_niedostepny", id_=f"plik_niedostepny:{z.sha16}",
                            dalej=ST.PLIK_NIEDOSTEPNY_PONOWIENIE.format(proba=z.proby + 1, prob=self.ponow_plik_niedostepny + 1))
            self._zlec(z)
            return "stan"
        if e.rodzaj == "start":  # proces silnika nie umie wystartowac: skan NIE dostaje bledu - czeka (takze na nastepny start programu)
            if z.proby_startu < PROBY_STARTU_SILNIKA and not self._silnik_nie_startuje:
                z.proby_startu += 1
                self._zlec(z)
                return "zywe"
            self._silnik_nie_startuje = True
            self._wstrzymane.append(z)
            self._komunikat("silnik_nie_startuje", id_="silnik")
            self.sesja.baza.zdarzenie("silnik", "silnik_nie_startuje", {"opis": self._bez_nazw(e.blad, z)[:SE.OPIS_BLEDU_MAX]}, czas=self._teraz())
            return "stan"
        self._usun_komunikat(f"plik_niedostepny:{z.sha16}")
        if e.rodzaj == "analiza":
            if not _istnieje(z.plik) and z.przejmij_zastepcza():  # P2: plik przemianowany, zanim silnik zrobil kopie - nowa sciezka
                self.sesja.baza.zdarzenie("silnik", "skan_przemianowany", {"sha16": z.sha16}, czas=self._teraz())
                self._zlec(z)
                return "zywe"
            self._sprawdz_pule_po_bledzie(z, e)  # P3: blad zapisany dopiero, gdy pula okaze sie niepusta
            return "zywe"
        return self._zapisz_blad(z, e.rodzaj, self._bez_nazw(e.blad, z))

    # --- zamkniecie ------------------------------------------------------------------------------
    def zamknij(self) -> K.Odpowiedz:
        """Zamyka program: obserwator, potem silnik; wyniki, ktore zdazyly przyjsc, sa przyjmowane; zadania niezakonczone
        (w toku, w kolejce, wstrzymane, niezapisane) trafiaja do pliku ``PLIK_ZADAN`` i wracaja po starcie."""
        if self._zamkniety:
            return K.Odpowiedz(True)
        self._zamknij_ramki_excel()  # E3-A12: ramki zgaszone i zatrzymane (najwyzej ok. 1 s), Excel rozlaczony
        niezakonczone: list[Zlecenie] = []
        if self._uruchomiony:
            self._zamykanie = True
            try:
                self.scanner.stop()
            except Exception:  # noqa: BLE001 - zamkniecie musi dojsc do konca (zapis zadan, zamkniecie bazy)
                LOG.exception("stanowisko: blad zatrzymania obserwatora folderu")
            while True:  # skany zgloszone przed zatrzymaniem obserwatora, jeszcze nieobsluzone: do zadan niezakonczonych
                try:
                    rodzaj, dane = self._skrzynka.get_nowait()
                except queue.Empty:
                    break
                if rodzaj == "skan":
                    self._bezpiecznie(self._zdarzenie_skrzynki, rodzaj, dane)
            try:
                z_silnika = self.silnik.stop()
            except Exception:  # noqa: BLE001
                LOG.exception("stanowisko: blad zatrzymania silnika")
                z_silnika = []
            while True:  # wyniki i bledy, ktore silnik oddal przed zatrzymaniem (kazde zadanie: wynik albo lista stop(), nigdy oba)
                try:
                    e = self.silnik.zdarzenia.get_nowait()
                except queue.Empty:
                    break
                if e.typ in ("wynik", "blad"):
                    self._bezpiecznie(self._zdarzenie_silnika, e)
            for d in list(self._do_zapisu):  # ostatnia proba zapisu wynikow i bledow, ktore czekaly na baze / dysk
                self._bezpiecznie(self._zapisz, d, False)
            if {x.zadanie_id for x in z_silnika} != set(self._zlecone):
                LOG.warning("stanowisko: lista zadan z silnika (%d) rozni sie od listy kontrolera (%d) - zapisuje liste kontrolera",
                            len(z_silnika), len(self._zlecone))
            for d in self._do_zapisu:  # wynik niezapisany: zadanie liczy sie od nowa po starcie (nowy komplet plikow) - P9
                if d.rodzaj == "wynik":
                    self._usun_pliki_wyniku(d.zdarzenie, podglad=True)
            niezakonczone = ([self._zlecone[nr] for nr in sorted(self._zlecone)] + [d.zlecenie for d in self._do_zapisu]
                             + [x[0] for x in self._do_sprawdzenia] + self._wstrzymane)
            try:
                self._zapisz_zadania(niezakonczone)
            except OSError as e:
                LOG.error("stanowisko: zadan niezakonczonych nie da sie zapisac (%s) - skany wroca przez nadrabianie folderu", type(e).__name__)
        self._analiza, self._w_toku = None, None
        try:
            self.sesja.baza.zdarzenie("system", "program_stop", {"niezakonczone": len(niezakonczone)}, czas=self._teraz())
            stan = dataclasses.replace(self._zbuduj(), zamkniety=True, analiza=None)
        except Exception:  # noqa: BLE001 - np. baza zajeta: zostaje ostatni znany stan
            LOG.exception("stanowisko: stanu koncowego nie da sie odczytac z bazy")
            stan = dataclasses.replace(self._stan, zamkniety=True, analiza=None) if self._stan is not None else K.StanAplikacji(zamkniety=True)
        self._zamkniety = True
        self._stan = stan
        try:
            self.sesja.baza.zamknij()
        finally:
            self._blokada.zwolnij()  # B1: nastepny start (takze drugi egzemplarz) moze juz pracowac na tej bazie
        LOG.info("stanowisko: zamkniete, zadan niezakonczonych %d", len(niezakonczone))
        self._powiadom("zamkniety", stan=stan)
        return K.Odpowiedz(True, dane=len(niezakonczone))


# ----------------------------------------------------------------------------
# uruchomienie programu
# ----------------------------------------------------------------------------
def konfiguruj_logi(ust: dict, poziom: int = logging.INFO) -> Path:
    """Log programu w ``[sciezki] logi`` (plik ``stanowisko.log``, 5 x 2 MB). Zwraca plik logu. P5: ``FILTR_NAZW`` w loggerach
    programu (takze ``scanner`` i ``silnik``, ktore loguja nazwy plikow skanu) i na uchwycie pliku (wpisy innych bibliotek) -
    w logu zamiast nazwy pliku skanu jest jego ``sha16`` (albo ``<plik>``), zamiast sciezek ``<sciezka>``."""
    katalog = katalog_z_ustawien(ust, "logi")
    katalog.mkdir(parents=True, exist_ok=True)
    plik = katalog / PLIK_LOGU
    korzen = logging.getLogger()
    for nazwa in LOGGERY_Z_FILTREM:
        logger = logging.getLogger(nazwa)
        if FILTR_NAZW not in logger.filters:
            logger.addFilter(FILTR_NAZW)
    if not any(isinstance(h, logging.handlers.RotatingFileHandler) and Path(h.baseFilename) == plik for h in korzen.handlers):
        uchwyt = logging.handlers.RotatingFileHandler(plik, maxBytes=2 * 1024 * 1024, backupCount=5, encoding="utf-8")
        uchwyt.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        uchwyt.addFilter(FILTR_NAZW)
        korzen.addHandler(uchwyt)
    korzen.setLevel(min(korzen.level or poziom, poziom))
    return plik


def odlacz_logi(plik: Path | None = None) -> None:
    """Odwrotnosc ``konfiguruj_logi`` (testy, osadzenie w innym programie): zdejmuje uchwyt pliku logu ``plik`` (None = kazdy
    uchwyt z ``FILTR_NAZW``) i filtr nazw z loggerow programu."""
    korzen = logging.getLogger()
    for h in list(korzen.handlers):
        if isinstance(h, logging.handlers.RotatingFileHandler) and FILTR_NAZW in h.filters and (plik is None or Path(h.baseFilename) == Path(plik)):
            korzen.removeHandler(h)
            h.close()
    for nazwa in LOGGERY_Z_FILTREM:
        logging.getLogger(nazwa).removeFilter(FILTR_NAZW)


def utworz_okno(kontroler: K.Kontroler, lacznik: Any):
    """MIEJSCE NA EKRAN WIECZORNY (paczka A3b): pakiet ``stanowisko.ui`` z funkcja ``utworz_okno(kontroler, lacznik)``
    zwracajaca okno Qt (jeszcze niepokazane). Dopoki pakietu nie ma - okno zastepcze z tekstowym podsumowaniem stanu.
    Wolane z ``main()`` po zaimportowaniu Qt."""
    try:
        from . import ui  # noqa: PLC0415 - pakiet ekranu (A3b); import dopiero tutaj, po Qt w main()
    except ImportError:
        return _okno_zastepcze(kontroler, lacznik)
    return ui.utworz_okno(kontroler, lacznik)


def _okno_zastepcze(kontroler: K.Kontroler, lacznik: Any):
    """Najprostsze okno do czasu ekranu A3b: tekst stanu (operator, pula, kolejka, plytki, pytania, komunikaty) i Spacja =
    start skanu. Bez wlasnych kolorow i napisow statusow - wszystko ze stanu kontrolera."""
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QPlainTextEdit

    class OknoZastepcze(QPlainTextEdit):
        def __init__(self) -> None:
            super().__init__()
            self.setReadOnly(True)
            self.setWindowTitle("Stanowisko")
            self.resize(900, 600)
            lacznik.stan_zmieniony.connect(self.pokaz)
            self.pokaz(kontroler.stan())

        def pokaz(self, s: K.StanAplikacji) -> None:
            linie = [f"Stanowisko - doba {s.doba}, zmiana {s.zmiana}, operator: {s.operator or '(nie wybrano)'}",
                     f"Pula: {s.pula.napis}   Kolejka: {s.kolejka.razem}   Analiza: {s.analiza.etap if s.analiza else '-'}", ""]
            for p in s.plytki:
                linie.append(f"Plytka nr {p.numer if p.numer is not None else '?'} ({p.czas}): {p.napis}; "
                             + ", ".join(f"{g.nr}: {g.podpis}" for g in p.gniazda if g.prace))
            linie += [""] + [f"PYTANIE: {q.tytul} - {q.tekst}" for q in s.pytania] + [f"{k.tytul}: {k.tekst}" for k in s.komunikaty]
            linie += ["", f"Do dofrezowania: {len(s.do_dofrezowania_biezaca)}"]
            self.setPlainText("\n".join(linie))

        def keyPressEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
            if zdarzenie.key() == Qt.Key.Key_Space and not zdarzenie.isAutoRepeat():
                kontroler.start_skanu()
            else:
                super().keyPressEvent(zdarzenie)

    return OknoZastepcze()


def main(argv: list[str] | None = None) -> int:
    multiprocessing.freeze_support()  # wersja zamrozona (DY1): proces roboczy silnika startuje z tego samego pliku
    # Qt W CALOSCI na poczatku main(), przed pierwszym uzyciem silnika (silnik.md: "DLL load failed while importing Shiboken"
    # przy imporcie Qt po analizach) i NIGDY na poziomie modulu (proces roboczy wykonuje ten plik jako __mp_main__).
    from PySide6 import QtCore, QtGui, QtWidgets  # noqa: F401, PLC0415

    parser = argparse.ArgumentParser(prog="stanowisko.aplikacja", description='Program "Stanowisko": kontrola prac z cyrkonu po skanie plytki.')
    parser.add_argument("--ustawienia", type=Path, default=None, help="plik ustawien (domyslnie ustawienia.toml w katalogu programu)")
    parser.add_argument("--atrapa", action="store_true", help="dane sztuczne bez skanera i silnika (pokaz okna)")
    parser.add_argument("--rano", action="store_true", help="z --atrapa: pokaz trybu Poranek (piec z trzema plytkami porannymi)")
    parser.add_argument("--zamknij-po", type=float, default=None, metavar="S", help="zamknij program po S sekundach (proba uruchomienia)")
    args = parser.parse_args(argv)

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv[:1])

    def pokaz_blad(tekst: str) -> None:  # komunikat dla czlowieka zamiast sladu wyjatku w oknie konsoli
        if args.zamknij_po is None:
            QtWidgets.QMessageBox.critical(None, "Stanowisko", tekst)
        else:
            print(f"BLAD: {tekst}", file=sys.stderr)

    if args.atrapa:
        kontroler: K.Kontroler = K.AtrapaKontrolera()
        if args.rano:
            kontroler.scenariusz_poranny()
        else:
            kontroler.scenariusz_pokazowy()
    else:
        try:
            ust = UST.wczytaj_ustawienia(args.ustawienia)
        except (FileNotFoundError, UST.BladUstawien) as e:
            pokaz_blad(str(e))
            return 2
        blokada = BlokadaStanowiska(B.sciezka_bazy(ust))
        try:
            blokada.zajmij()  # B1: zanim program dotknie logu, bazy i folderu skanera
        except ProgramJuzDziala as e:
            pokaz_blad(str(e))
            return KOD_PROGRAM_JUZ_DZIALA
        except OSError as e:  # katalogu bazy nie da sie utworzyc / otworzyc pliku blokady
            pokaz_blad(f"Nie mozna przygotowac folderu danych programu ({type(e).__name__}): {B.bez_sciezek(str(e))}")
            return 2
        kontroler = None
        try:
            konfiguruj_logi(ust)
            kontroler = Aplikacja(ust, blokada=blokada, ramki=True, excel=True)  # E3-A12: ramki i Excel z ustawien
            kontroler.start()
        except Exception as e:  # noqa: BLE001 - D9: kazdy blad startu = komunikat dla czlowieka i wpis w logu
            LOG.exception("stanowisko: program nie wystartowal")
            if kontroler is not None:
                try:
                    kontroler.zamknij()
                except Exception:  # noqa: BLE001
                    LOG.exception("stanowisko: blad zamykania po nieudanym starcie")
            blokada.zwolnij()
            pokaz_blad(str(e) if isinstance(e, (B.BladBazy, OSError)) else f"Program nie wystartowal ({type(e).__name__}): {B.bez_sciezek(str(e))}")
            return 2
    lacznik = K.lacznik_qt(kontroler)
    okno = utworz_okno(kontroler, lacznik)
    app.aboutToQuit.connect(kontroler.zamknij)  # najpierw scanner.stop(), potem silnik.stop() - w Aplikacja.zamknij
    okno.show()
    if args.zamknij_po is not None:
        QtCore.QTimer.singleShot(int(args.zamknij_po * 1000), app.quit)
    kod = app.exec()
    lacznik.zatrzymaj()
    kontroler.zamknij()
    return int(kod)


if __name__ == "__main__":
    raise SystemExit(main())
