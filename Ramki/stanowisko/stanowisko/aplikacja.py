"""aplikacja - program "Stanowisko": kontroler spinajacy ``scanner`` -> ``silnik`` -> ``session`` / ``baza`` (paczka E3-A3a).

Technik uklada prace na plytce, skaner zapisuje STL do folderu, a ten modul bez udzialu czlowieka: zauwaza plik
(``scanner``), zleca analize w osobnym procesie (``silnik``), przyjmuje wynik do sesji wieczornej (``session``) i wystawia
oknu stan oraz polecenia opisane w ``kontroler_api`` (kontrakt dla ekranu - paczka A3b). Sam nie rysuje niczego.

``Aplikacja`` (prawdziwy kontroler; wspolna czesc z atrapa: ``kontroler_api.KontrolerSesji``):
* start: baza i sesja z ``ustawienia.toml``, silnik, wznowienie zadan zapisanych przy zamknieciu, potem obserwator folderu
  z ``znane=ZnanePliki(...)`` - skany zapisane, gdy program nie dzialal, sa nadrabiane, a juz przyjete nie wracaja;
* kazdy skan: powtorka tej samej tresci (``sha16``) wobec skanu, ktory MA wynik w bazie, albo wobec zadania czekajacego
  w kolejce nie jest liczona drugi raz; samo zobaczenie pliku niczego nie zapisuje (awaria przed wynikiem nie gubi skanu);
* wynik: ``session.przyjmij_wynik``; blad analizy: ``session.przyjmij_blad`` + komunikat; ``plik_zmieniony`` - tylko
  informacja (nowa tresc ma wlasne zdarzenie); ``plik_niedostepny`` - ponawianie (``[silnik] ponow_plik_niedostepny``);
* pula projektow na poziomie 1 planu: jeden folder + wspolczynnik wpisany recznie (None = domyslny dla typu plytki, jak
  w oknie testowym); liczba STL liczona w tle; bez projektow skany CZEKAJA (nie dostaja bledu) do "Odswiez pule";
* zamkniecie: ``scanner.stop()``, potem ``silnik.stop()``, wyniki, ktore zdazyly przyjsc, sa przyjmowane, a zadania
  niezakonczone (w toku, w kolejce, wstrzymane) zapisywane do pliku obok bazy i zlecane ponownie po starcie;
* akcja "start skanu" (DW5): interfejs ``Scanner.start_skanu`` z atrapa - zadnego automatu klikajacego w programie skanera.

Dane osobowe: nazwy plikow i folderow (skanu, puli, zlecen) nie trafiaja do komunikatow, stanu, dziennika ani logu tego
modulu - skan jest opisywany skrotem ``sha16``. Wyjatki zamierzone: ``skany.plik`` (kolumna z planu, pisze ``session``)
i dwa pliki robocze obok bazy (``PLIK_ZADAN``: sciezki skanow czekajacych na analize; ``PLIK_PULI``: folder puli).

Plik startowy: ``python -m stanowisko.aplikacja`` (``uruchom_stanowisko.bat``). Na poziomie modulu NIE MA importu Qt -
proces roboczy silnika wykonuje ten plik ponownie (``__mp_main__``) i zaladowalby Qt obok Open3D (``silnik.md``, D8).
Wszystkie moduly PySide6 sa importowane w calosci na poczatku ``main()``, przed pierwszym uzyciem silnika.
"""
from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import json
import logging
import logging.handlers
import multiprocessing
import os
import queue
import sys
import threading
import time
from pathlib import Path
from typing import Any, Callable

from . import baza as B
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
WSPOLCZYNNIK_MIN, WSPOLCZYNNIK_MAX = 0.9, 1.5  # zakres wspolczynnika skurczu przyjmowany z okna (poranna 1,0; wieczorna ok. 1,2-1,25)
PROBY_STARTU_SILNIKA = 1  # ile razy zadanie jest zlecane ponownie, gdy proces silnika nie umie wystartowac
OKRES_KONTROLI_S = 1.0  # co ile ``przetworz`` sprawdza stan obserwatora (folder dostepny, pliki zajete) i ponawia zapis do zajetej bazy
PLIK_LOGU = "stanowisko.log"
PLIK_LOGU_SILNIKA = "silnik.log"


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

    @classmethod
    def ze_zdarzenia(cls, z: Any, tryb: str) -> "Zlecenie":
        return cls(plik=str(z.plik), sha16=z.sha16, rozmiar=z.rozmiar, mtime_ns=z.mtime_ns, trojkaty=z.trojkaty, tryb=tryb, zastany=bool(z.zastany))

    def zdarzenie(self) -> dict:
        """Zdarzenie skanu dla ``session`` (kontrakt ``ZdarzenieSkanu``: plik, sha16, rozmiar, czas_pliku w sekundach od epoki)."""
        return {"plik": self.plik, "sha16": self.sha16, "rozmiar": self.rozmiar,
                "czas_pliku": self.mtime_ns / 1e9 if self.mtime_ns is not None else None}

    def do_zapisu(self) -> dict:
        return {k: getattr(self, k) for k in ("plik", "sha16", "rozmiar", "mtime_ns", "trojkaty", "tryb", "numer")}


def pliki_stl(folder: Path) -> int:
    """Liczba plikow STL puli w ``folder`` - ta sama regula, co ``synth.pliki_projektow`` (podfoldery tak, foldery ``_*`` nie),
    bez ladowania bibliotek obliczen do procesu okna."""
    folder = Path(folder)
    return sum(1 for p in folder.rglob("*") if p.suffix.lower() == ".stl" and p.is_file()
               and not any(cz.startswith("_") for cz in p.relative_to(folder).parts[:-1]))


def katalog_z_ustawien(ust: dict, klucz: str) -> Path:
    return B.sciezka_z_ustawien(ust, klucz)


class Aplikacja(K.KontrolerSesji):
    """Prawdziwy kontroler programu "Stanowisko". Uzycie (watek okna)::

        k = Aplikacja(ust)          # otwiera baze i sesje; niczego jeszcze nie obserwuje
        k.start()                   # silnik, wznowienie zadan, obserwator folderu z nadrabianiem
        ... k.przetworz() co ok. 30 ms (``kontroler_api.lacznik_qt`` robi to zegarem Qt) ...
        k.zamknij()                 # scanner.stop(), silnik.stop(), zapis zadan niezakonczonych, zamkniecie bazy

    Parametry do testow: ``zegar``, ``funkcja_analizy`` (``"modul:funkcja"`` zamiast ``porownaj``), ``start_skanu`` (akcja
    DW5; domyslnie atrapa ze ``scanner``), ``parametry_scannera`` / ``parametry_silnika`` (nadpisuja wartosci z ustawien).
    """

    def __init__(self, ust: dict, *, tryb: str = SE.TRYB_WIECZOR, zegar: Callable[[], dt.datetime] | None = None, start_skanu=None,
                 funkcja_analizy: str = SI.FUNKCJA_ANALIZY, parametry_scannera: dict | None = None, parametry_silnika: dict | None = None):
        baza = B.otworz(B.sciezka_bazy(ust), zegar=zegar)
        try:
            sesja = SE.Sesja.z_ustawien(ust, baza, zegar=zegar, wersja_programu=WERSJA_PROGRAMU)
            super().__init__(sesja, ust, tryb=tryb, zegar=zegar)
        except BaseException:
            baza.zamknij()
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
        self._nieprzyjete: list[tuple] = []  # (zlecenie, zdarzenie silnika z wynikiem), gdy baza byla zajeta - ponawiane
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
        self._wczytaj_pule()

    # --- start -----------------------------------------------------------------------------------
    def start(self) -> None:
        """Uruchamia silnik, zleca zadania zapisane przy zamknieciu i wlacza obserwator folderu z nadrabianiem."""
        if self._uruchomiony or self._zamkniety:
            return
        s, ust = self._parametry_silnika, self.ust
        self.katalog_logow.mkdir(parents=True, exist_ok=True)
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
        self._odswiez()

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
        ``ciche``: odswiezenie liczby po skanie - stan puli zostaje ``gotowa`` do czasu nowego wyniku (skany nie czekaja)."""
        self._pula_nr += 1
        if self._pula_folder is None:
            self._pula_stan, self._pula_liczba = "nieustawiona", None
            return
        if not (ciche and self._pula_stan == "gotowa"):
            self._pula_stan = "liczenie"
        nr, folder = self._pula_nr, self._pula_folder

        def licz() -> None:
            try:
                wynik = ("pula", (nr, pliki_stl(folder) if folder.is_dir() else None))
            except OSError:
                wynik = ("pula", (nr, None))
            self._skrzynka.put(wynik)

        threading.Thread(target=licz, name="pula-liczenie", daemon=True).start()

    def _pula_policzona(self, nr: int, liczba: int | None) -> None:
        if nr != self._pula_nr:
            return
        self._pula_liczba, self._pula_czas = liczba, self._teraz()
        self._pula_stan = "brak_folderu" if liczba is None else ("gotowa" if liczba > 0 else "pusta")
        if self._pula_stan == "gotowa":
            self._usun_komunikat("pula")
            self._zwolnij_wstrzymane()
        elif self._wstrzymane:
            self._komunikat_puli()

    def _komunikat_puli(self) -> None:
        if self._pula_stan in ("pusta", "brak_folderu", "nieustawiona"):
            self._komunikat("pula_pusta" if self._pula_stan == "pusta" else "pula_brak_folderu", id_="pula", czas=self._teraz(),
                            czeka=len(self._wstrzymane))

    def ustaw_pule(self, folder: str | None, wspolczynnik: float | None = None) -> K.Odpowiedz:
        """Folder projektow i wspolczynnik skurczu wpisane recznie (None = domyslny dla rozpoznanego typu plytki)."""
        if self._zamkniety:
            return K.Odpowiedz(False, ST.tekst_komunikatu("program_zamkniety")[2], "program_zamkniety")
        if wspolczynnik is not None:
            try:
                wspolczynnik = float(wspolczynnik)
            except (TypeError, ValueError):
                wspolczynnik = float("nan")
            if not WSPOLCZYNNIK_MIN <= wspolczynnik <= WSPOLCZYNNIK_MAX:
                return self._odmowa("zly_wspolczynnik", od=f"{WSPOLCZYNNIK_MIN:g}", do=f"{WSPOLCZYNNIK_MAX:g}")
        self._pula_folder = Path(folder) if folder else None
        self._pula_wspolczynnik = wspolczynnik
        try:
            self.katalog_danych.mkdir(parents=True, exist_ok=True)
            (self.katalog_danych / PLIK_PULI).write_text(json.dumps({"folder": str(self._pula_folder) if self._pula_folder else None,
                                                                    "wspolczynnik": wspolczynnik}, ensure_ascii=False), encoding="utf-8")
        except OSError as e:
            LOG.warning("stanowisko: ustawien puli nie da sie zapisac (%s)", type(e).__name__)
        self.sesja.baza.zdarzenie("pula", "pula_ustawiona", {"wspolczynnik": wspolczynnik, "folder_ustawiony": self._pula_folder is not None},
                                  czas=self._teraz())
        return self.odswiez_pule()

    def odswiez_pule(self) -> K.Odpowiedz:
        """Liczy pule od nowa (w tle); po policzeniu skany wstrzymane z braku projektow ida do analizy."""
        if self._zamkniety:
            return K.Odpowiedz(False, ST.tekst_komunikatu("program_zamkniety")[2], "program_zamkniety")
        self._usun_komunikat("odmowa:zly_wspolczynnik")
        self._policz_pule()
        self._odswiez()
        return K.Odpowiedz(True)

    def _opis_puli(self) -> SI.OpisPuli:
        return SI.OpisPuli(foldery=(str(self._pula_folder),), wspolczynnik=self._pula_wspolczynnik)

    # --- czesc zywa stanu ----------------------------------------------------------------------------
    def _stan_zywy(self) -> dict:
        w_toku = 1 if self._w_toku is not None and self._w_toku in self._zlecone else 0
        napis = ST.STANY_PULI.get(self._pula_stan, "").format(n=self._pula_liczba)
        sc = self.scanner.stan() if self.scanner is not None else {}
        return {
            "analiza": self._analiza,
            "kolejka": K.Kolejka(w_toku=w_toku, czeka=len(self._zlecone) - w_toku, wstrzymane=len(self._wstrzymane) + len(self._nieprzyjete),
                                 silnik_gotowy=self._silnik_gotowy),
            "pula": K.Pula(folder=str(self._pula_folder) if self._pula_folder is not None else None, wspolczynnik=self._pula_wspolczynnik,
                           liczba_stl=self._pula_liczba, stan=self._pula_stan, napis=napis, odswiezono=self._pula_czas),
            "skaner": K.Skaner(folder=str(self.folder_skanera), dostepny=bool(sc.get("folder_dostepny")), dziala=bool(sc.get("dziala")),
                               zajete=int(sc.get("zajete") or 0), ostatni_start_skanu=self._ostatni_start_skanu, startow_skanu=self._starty_skanu,
                               czeka_na_skan=self._czeka_na_skan)}

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
        self.sesja.baza.zdarzenie("ui", "start_skanu", {"udany": udany}, czas=self._ostatni_start_skanu)
        if not udany:
            return self._odmowa("start_skanu_nieudany")
        self._usun_komunikat("odmowa:start_skanu_nieudany")
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
        if self._nieprzyjete and t0 - self._ostatnia_kontrola >= OKRES_KONTROLI_S:
            czekajace, self._nieprzyjete = self._nieprzyjete, []
            for z, e in czekajace:
                zmiany.add(self._przyjmij_wynik(z, e))
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
        if "stan" in zmiany:
            self._odswiez()
        elif "zywe" in zmiany:
            self._odswiez_zywe()
        elif "postep" in zmiany:
            self._odswiez_zywe("postep")
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

    def _nowy_skan(self, z: Zlecenie) -> None:
        """Skan do analizy - o ile ta sama tresc nie ma juz wyniku w bazie i nie czeka w kolejce (zaden skan liczony dwa razy)."""
        baza = self.sesja.baza
        jest = baza.wiersz("SELECT id FROM skany WHERE sha16 = ? AND status != ? ORDER BY id DESC LIMIT 1", (z.sha16, SE.STATUS_BLAD))
        if jest is not None:  # powtorka wobec skanu Z WYNIKIEM (skan ``blad`` wyniku nie ma - wolno liczyc ponownie)
            baza.zdarzenie("scanner", "skan_powtorzony", {"sha16": z.sha16, "zastany": z.zastany, "wznowiony": z.wznowiony}, skan_id=jest["id"],
                           czas=self._teraz())
            if not z.zastany and not z.wznowiony:
                self._komunikat("skan_juz_jest", skan_id=jest["id"])
            return
        if any(x.sha16 == z.sha16 for x in list(self._zlecone.values()) + self._wstrzymane + [n[0] for n in self._nieprzyjete]):
            baza.zdarzenie("scanner", "skan_powtorzony_w_kolejce", {"sha16": z.sha16, "zastany": z.zastany}, czas=self._teraz())
            return
        self._zlec(z)

    def _zlec(self, z: Zlecenie) -> None:
        if self._zamykanie or self._silnik_nie_startuje or self._pula_stan != "gotowa":
            self._wstrzymane.append(z)
            if not self._zamykanie:
                self._komunikat_puli()
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
                self._usun_komunikat("silnik")
                self._zwolnij_wstrzymane()
                return "stan"
            return "zywe"
        if e.typ == "zatrzymany":
            return ""
        z = self._zlecone.get(e.zadanie_id)
        if z is None:
            return ""  # zdarzenie zadania, ktorego kontroler juz nie prowadzi
        if e.typ == "start":
            self._w_toku = e.zadanie_id
            self._analiza = K.Postep(zadanie_id=e.zadanie_id, etap="", udzial=0.0, od=e.czas, sha16=z.sha16)
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
        pliki = e.pliki or {}
        try:
            with self.sesja.baza.transakcja():  # skan, prace i wpis o pliku podgladu: jeden zapis na dysk (krotsza przerwa petli okna)
                skan_id = self.sesja.przyjmij_wynik(z.zdarzenie(), e.wynik, z.tryb)
                self._zapisz_podglad(skan_id, pliki.get("podglad"))
        except B.BladBazy:  # baza zajeta przez inny program: wynik czeka w pamieci i jest zapisywany ponownie
            self._nieprzyjete.append((z, e))
            self._komunikat("baza_zajeta", id_="baza_zajeta:wyniki")
            return "stan"
        except Exception as blad:  # noqa: BLE001 - wynik, ktorego sesja nie umie przyjac, nie moze zatrzymac programu
            LOG.exception("stanowisko: wyniku skanu %s nie da sie przyjac do sesji", z.sha16)
            return self._zapisz_blad(z, "analiza", f"wyniku nie da sie zapisac: {type(blad).__name__}")
        self._usun_komunikat("baza_zajeta:wyniki")
        self._usun_komunikat(f"plik_niedostepny:{z.sha16}")
        if pliki.get("wynik"):  # kopia wyniku z silnika zawiera folder puli; obowiazuje plik zapisany przez sesje (bez sciezek)
            try:
                Path(pliki["wynik"]).unlink(missing_ok=True)
            except OSError:
                pass
        LOG.info("stanowisko: skan %s przyjety jako %d (%.1f s)", z.sha16, skan_id, e.czas_s or 0.0)
        if not self._zamykanie:
            self._policz_pule(ciche=True)  # liczba STL na ekranie aktualna po kazdej plytce (silnik i tak czyta folder przy kazdym zadaniu)
        return "stan"

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
        return self._zapisz_blad(z, e.rodzaj, self._bez_nazw(e.blad, z))

    def _zapisz_blad(self, z: Zlecenie, rodzaj: str, opis: str) -> str:
        try:
            with self.sesja.baza.transakcja():
                skan_id = self.sesja.przyjmij_blad(z.zdarzenie(), f"{rodzaj}: {opis}", z.tryb)
                self.sesja.baza.zdarzenie("silnik", "blad_analizy_rodzaj", {"rodzaj": rodzaj}, skan_id=skan_id, czas=self._teraz())
        except B.BladBazy:
            self._wstrzymane.append(z)  # baza zajeta: skan zostaje do ponownej analizy (nic nie ginie)
            self._komunikat("baza_zajeta", id_="baza_zajeta:wyniki")
        return "stan"

    # --- zamkniecie ------------------------------------------------------------------------------
    def zamknij(self) -> K.Odpowiedz:
        """Zamyka program: obserwator, potem silnik; wyniki, ktore zdazyly przyjsc, sa przyjmowane; zadania niezakonczone
        (w toku, w kolejce, wstrzymane, niezapisane) trafiaja do pliku ``PLIK_ZADAN`` i wracaja po starcie."""
        if self._zamkniety:
            return K.Odpowiedz(True)
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
            czekajace, self._nieprzyjete = self._nieprzyjete, []
            for z, e in czekajace:  # ostatnia proba zapisu wynikow, ktore czekaly na zajeta baze
                self._bezpiecznie(self._przyjmij_wynik, z, e)
            if {x.zadanie_id for x in z_silnika} != set(self._zlecone):
                LOG.warning("stanowisko: lista zadan z silnika (%d) rozni sie od listy kontrolera (%d) - zapisuje liste kontrolera",
                            len(z_silnika), len(self._zlecone))
            niezakonczone = [self._zlecone[nr] for nr in sorted(self._zlecone)] + [n[0] for n in self._nieprzyjete] + self._wstrzymane
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
        self.sesja.baza.zamknij()
        LOG.info("stanowisko: zamkniete, zadan niezakonczonych %d", len(niezakonczone))
        self._powiadom("zamkniety", stan=stan)
        return K.Odpowiedz(True, dane=len(niezakonczone))


# ----------------------------------------------------------------------------
# uruchomienie programu
# ----------------------------------------------------------------------------
def konfiguruj_logi(ust: dict, poziom: int = logging.INFO) -> Path:
    """Log programu w ``[sciezki] logi`` (plik ``stanowisko.log``, 5 x 2 MB). Zwraca plik logu. Ten modul nie loguje nazw
    plikow; ``scanner`` loguje nazwe pliku skanu (znana granica do rozstrzygniecia po pierwszych skanach - ``scanner.md``)."""
    katalog = katalog_z_ustawien(ust, "logi")
    katalog.mkdir(parents=True, exist_ok=True)
    plik = katalog / PLIK_LOGU
    korzen = logging.getLogger()
    if not any(isinstance(h, logging.handlers.RotatingFileHandler) and Path(h.baseFilename) == plik for h in korzen.handlers):
        uchwyt = logging.handlers.RotatingFileHandler(plik, maxBytes=2 * 1024 * 1024, backupCount=5, encoding="utf-8")
        uchwyt.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        korzen.addHandler(uchwyt)
    korzen.setLevel(min(korzen.level or poziom, poziom))
    return plik


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
    parser.add_argument("--zamknij-po", type=float, default=None, metavar="S", help="zamknij program po S sekundach (proba uruchomienia)")
    args = parser.parse_args(argv)

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv[:1])
    if args.atrapa:
        kontroler: K.Kontroler = K.AtrapaKontrolera()
        kontroler.scenariusz_pokazowy()
    else:
        try:
            ust = UST.wczytaj_ustawienia(args.ustawienia)
            konfiguruj_logi(ust)
            kontroler = Aplikacja(ust)
            kontroler.start()
        except (FileNotFoundError, UST.BladUstawien, B.BladBazy) as e:  # komunikat dla czlowieka zamiast sladu wyjatku
            if args.zamknij_po is None:
                QtWidgets.QMessageBox.critical(None, "Stanowisko", str(e))
            else:
                print(f"BLAD: {e}", file=sys.stderr)
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
