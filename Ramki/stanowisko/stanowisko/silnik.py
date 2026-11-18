"""silnik - analiza skanu (``porownaj.porownaj``) w OSOBNYM PROCESIE: kolejka zadan, postep, obsluga awarii (paczka E3-A2).

Po co: Open3D uruchomione w watku pod Qt zawisa (okno testowe: 195 s bez wyniku, raporty/P3a_przekazanie.md pkt 5.1),
wiec proces okna nie moze liczyc. ``Silnik`` trzyma jeden proces roboczy (``multiprocessing``, metoda ``spawn``), wysyla mu
zadania po jednym, odbiera postep i wynik, a po awarii (wyjatek analizy, zabity proces, przekroczony limit czasu) zglasza
blad tego zadania, w razie potrzeby uruchamia proces od nowa i bierze nastepne zadanie. Ten modul na poziomie importu
uzywa tylko biblioteki standardowej - numpy, trimesh i Open3D laduje wylacznie proces roboczy.

Kontrakty (plan etapu 3, sekcja 3.8):
* ``ZadanieAnalizy`` - skan, tryb (wieczor / rano), uklad (``auto`` = rozpoznaj; zalozenie Z2), numer plytki albo brak,
  opis puli (``OpisPuli``: foldery projektow, wspolczynnik albo None = domyslny dla rozpoznanej plytki);
* wynik - slownik zwracany przez ``porownaj.porownaj`` w postaci z pliku ``<skan>_wynik.json`` (lacznie z ``ostrzezenia``,
  jak w wierszu polecen) + ``zadanie_id`` + ``skan_sha16`` (skrot tresci FAKTYCZNIE analizowanej);
* ``ZdarzenieSilnika`` - ``gotowy`` / ``start`` / ``postep`` / ``wynik`` / ``blad`` (``rodzaj``: ``analiza``, ``proces``,
  ``limit_czasu``, ``start``, ``plik_zmieniony``, ``plik_niedostepny``) / ``zatrzymany`` (``niezakonczone``: zadania
  przerwane przez ``stop()``).

Kopia robocza (N1, recenzja PR #17 runda 2): proces roboczy kopiuje skan do ``katalog_roboczy`` (odczyt z pelnym
wspoldzieleniem - program skanera moze w tym czasie pisac, przenosic i usuwac plik), liczy skrot KOPII i analizuje kopie.
Skrot kopii inny niz ``skan_sha16`` zdarzenia = plik nadpisany, zanim analiza ruszyla: ``blad`` ``plik_zmieniony`` bez
analizy (nowa tresc ma wlasne zdarzenie ze ``scanner``). Pozniejsza blokada, przeniesienie albo usuniecie pliku skanu
nie uniewaznia wyniku. Pliku nie da sie skopiowac (inny program trzyma go bez zgody na odczyt): ponawianie z rosnacym
odstepem (postep ``ETAP_OCZEKIWANIA``), po ``czekaj_na_plik_s`` ``blad`` ``plik_niedostepny``. Teksty wychodzace
z procesu roboczego (ostrzezenia, uwagi, bledy - tylko pola z tekstem wolnym, N2) sa czyszczone z nazw plikow i folderow
puli projektow (``CzyscicielNazw``: nazwiska). Proces roboczy pilnuje sie sam (``Straznik``): konczy sie w ok. 1 s po
zniknieciu procesu okna i po przekroczeniu limitu zadania z zapasem, o ile analiza nie trzyma GIL; niezaleznie od tego na
Windows jest w obiekcie zadania (Job Object) procesu okna, ktory system konczy razem z procesem okna (D-N5).

Uzycie:
    s = Silnik(na_zdarzenie=funkcja)      # funkcja wolana w watku nadzorcy (zwykly watek Pythona, bez Open3D i bez Qt)
    s.start()
    nr = s.zlec(ZadanieAnalizy(skan=plik, pula=OpisPuli(foldery=(folder,))))   # albo s.zlec_skan(zdarzenie_skanu, pula)
    ... niezakonczone = s.stop()          # zadania w toku i w kolejce - do ponownego zlecenia po starcie programu
W oknie: najpierw ``scanner.stop()``, potem ``silnik.stop()`` (zadne nowe zlecenie w trakcie zatrzymania; ``zlec`` po
rozpoczeciu ``stop()`` odmawia wyjatkiem ``SilnikZatrzymany``). ``na_zdarzenie`` nie moze czekac na watek wolajacy ``stop()``.
Bez ``na_zdarzenie`` zdarzenia trafiaja do kolejki ``s.zdarzenia``. W oknie Qt: ``lacznik_qt(s)`` zamienia je na sygnaly
emitowane w watku okna (zegar Qt oproznia kolejke). Program uruchamiajacy silnik musi miec glowny modul chroniony przez
``if __name__ == "__main__":`` (wymaganie ``multiprocessing`` na Windows), a ten plik startowy nie moze importowac Qt na
poziomie modulu: proces roboczy wykonuje go ponownie (jako ``__mp_main__``) i zaladowalby Qt obok Open3D (D8).

Pula projektow zostaje w pamieci procesu roboczego miedzy zadaniami (``PamiecPul``): budowana raz na (foldery,
wspolczynnik, orientacja, lista plikow w folderach), od nowa po zmianie plikow w folderze.

Start procesu roboczego (E3-A2p): ``Process.start()`` (metoda spawn na Windows) tworzy proces potomny i zapisuje mu do
lacza dane startowe (ok. 5 KB, wiecej niz bufor lacza 4 KB); gdy potomek ich nie czyta (zawisl albo zginal przed
odczytem), zapis czeka bez konca - uchwyt odczytu lacza trzyma tez proces okna (``popen_spawn_win32``, bpo-33929), wiec
smierc potomka zapisu nie konczy. Dlatego ``Process.start()`` biegnie w watku pomocniczym ``silnik-start``: gdy potomek
zginie (sprawdzane co ``SPRAWDZ_POTOMKA_S``) albo minie ``limit_uruchomienia_s``, nadzorca zabija potomka, anuluje
zawieszony zapis (``CancelSynchronousIo``), zamyka lacze i probuje od nowa; po ``proby_uruchomienia`` nieudanych probach -
``blad`` ``start`` pierwszego zadania z kolejki (aplikacja: komunikat "silnik nie startuje"). Stan potomka (kod wyjscia,
czas CPU, zaladowane moduly) trafia do logu. Proces roboczy dostaje wlasna, niewidoczna konsole (``CREATE_NO_WINDOW``,
``FLAGI_PROCESU_ROBOCZEGO``) zamiast konsoli procesu okna: na PC potomkowie podlaczani do konsoli procesu okna ginely
przy starcie z 0xC0000142 (przyczyna zawieszen D7 z raportu E3-A7, raport E3-A2p).
"""
from __future__ import annotations

import collections
import dataclasses
import hashlib
import importlib
import json
import logging
import multiprocessing
import os
import queue
import re
import shutil
import sys
import tempfile
import threading
import time
import traceback
import warnings
from pathlib import Path

LOG = logging.getLogger(__name__)

FUNKCJA_ANALIZY = "stanowisko.porownaj:porownaj"  # "modul:funkcja" o sygnaturze porownaj.porownaj
LIMIT_ZADANIA_S = 600.0  # analiza dluzsza niz to = proces zabity, blad "limit_czasu", nastepne zadanie
LIMIT_STARTU_S = 180.0  # proces roboczy, ktory nie zglosi gotowosci w tym czasie (liczac od Process.start()), jest zabijany
LIMIT_URUCHOMIENIA_S = 30.0  # E3-A2p: Process.start() dluzszy niz to = proba przerwana (potomek zabity, zapis do lacza anulowany)
PROBY_URUCHOMIENIA = 3  # E3-A2p: tyle prob Process.start() z limitem, potem blad "start" pierwszego zadania z kolejki
ODSTEP_PROB_URUCHOMIENIA_S = 0.5  # przerwa miedzy probami uruchomienia
CZEKAJ_NA_PRZERWANIE_S = 3.0  # jak dlugo nadzorca odblokowuje zawieszony Process.start(), zanim zostawi watek pomocniczy
SPRAWDZ_POTOMKA_S = 0.5  # co ile nadzorca sprawdza, czy proces potomny trwajacego Process.start() juz nie zginal
# E3-A2p: proces roboczy z WLASNA, niewidoczna konsola (CREATE_NO_WINDOW), a nie podlaczony do konsoli procesu okna. Na PC
# (D7) proces okna po kilkudziesieciu testach z oknami tracil mozliwosc podlaczania nowych procesow do swojej konsoli: kazdy
# taki potomek (python.exe, cmd.exe) ginal przy starcie z 0xC0000142, a potomkowie bez tej konsoli startowali (raport E3-A2p).
FLAGI_PROCESU_ROBOCZEGO = 0x08000000 if os.name == "nt" else 0
PUL_W_PAMIECI = 2  # np. pula wieczorna (wspolczynnik krazka) i poranna (1,0)
OKRES_S = 0.02  # co ile nadzorca zaglada do lacza z procesem
RODZAJE_BLEDU = ("analiza", "proces", "limit_czasu", "start", "plik_zmieniony", "plik_niedostepny")
ZNACZNIK_PULI = "<projekt>"  # w miejsce sciezki albo nazwy z puli projektow; nazwa pliku z puli -> "<projekt sha16>"
# N2: CzyscicielNazw.oczysc zmienia TYLKO wartosci tekstowe pod tymi kluczami (takze listy tekstow pod nimi) i pod kluczami
# konczacymi sie na "_" + jeden z nich (np. "uklad_komunikat"); statusy, typy, identyfikatory, nazwa skanu i liczby - nigdy
POLA_TEKSTU_WOLNEGO = ("ostrzezenia", "uwagi", "uwaga", "blad", "bledy", "komunikat", "podpowiedz", "powod", "powod_filtru", "opis", "szczegoly")
ZAPAS_LIMITU_S = 30.0  # proces roboczy konczy sie sam po limit_zadania_s + tyle (nadzorcy moze juz nie byc)
KATALOG_ROBOCZY = "qc_silnik"  # domyslny katalog kopii roboczych skanow: <katalog tymczasowy systemu>/qc_silnik
CZEKAJ_NA_PLIK_S = 60.0  # pliku skanu nie da sie skopiowac (zajety): ponawianie najwyzej tyle, potem blad plik_niedostepny
ODSTEP_KOPII_MAX_S = 2.0  # ponawianie kopiowania: co 0,1 s, potem 2x, 4x ... rzadziej, najrzadziej co tyle (jak scanner B1)
ZAPAS_DYSKU_B = 256 * 1024 * 1024  # kopia robocza tylko, gdy po niej zostanie tyle wolnego miejsca w katalogu roboczym
ETAP_OCZEKIWANIA = "oczekiwanie na zwolnienie pliku skanu"  # postep (udzial 0), gdy pliku nie da sie jeszcze skopiowac
BLOK_ODCZYTU = 4 * 1024 * 1024
OKRES_STRAZNIKA_S = 0.5  # co ile straznik w procesie roboczym sprawdza proces okna i czas zadania
KOD_BEZ_PROCESU_OKNA = 91  # kod wyjscia procesu roboczego: zniknal proces okna
KOD_LIMIT_ZADANIA = 92  # kod wyjscia procesu roboczego: zadanie przekroczylo limit (z zapasem)


@dataclasses.dataclass(frozen=True)
class OpisPuli:
    """Z czego silnik buduje pule projektow. ``wspolczynnik`` None = domyslny dla rozpoznanego typu plytki (jak w wierszu
    polecen). ``wspolczynniki`` (opcjonalnie): skrot projektu -> wspolczynnik pojedynczej pracy (``match.Pula``)."""

    foldery: tuple
    wspolczynnik: float | None = None
    orientacja: str = "auto"
    wspolczynniki: dict | None = None


@dataclasses.dataclass(frozen=True)
class ZadanieAnalizy:
    skan: Path
    pula: OpisPuli
    tryb: str = "wieczor"  # wieczor / rano - dla odbiorcy wyniku (sesja); analiza od trybu nie zalezy
    uklad: str = "auto"  # "auto" albo "rozpoznaj" = program rozpoznaje uklad; inaczej nazwa ukladu z [plytki]
    numer: int | None = None  # numer plytki, gdy dolki kodu sa poza skanem
    skan_sha16: str | None = None  # z ZdarzenieSkanu: porownywany ze skrotem kopii roboczej; None = silnik policzy sam
    inspekcja: bool = True
    bez_filtru: bool = False
    straznik: bool = True
    wyjscie: Path | None = None  # folder na <czas>_<sha16>[_n]_wynik.json i ..._podglad.npz (punkty i odchylki gniazd); bez nazwy skanu
    zadanie_id: int = 0  # nadaje Silnik.zlec
    przyjete: float | None = None  # czas przyjecia zadania (time.time()) - nadaje Silnik.zlec; poczatek nazw plikow w wyjscie


@dataclasses.dataclass(frozen=True)
class ZdarzenieSilnika:
    typ: str  # gotowy | start | postep | wynik | blad | zatrzymany
    czas: float  # time.time()
    zadanie_id: int | None = None
    zadanie: ZadanieAnalizy | None = None
    etap: str = ""  # postep: nazwa etapu z porownaj
    udzial: float = 0.0  # postep: 0-1
    wynik: dict | None = None
    pliki: dict | None = None  # wynik: sciezki plikow zapisanych w ``wyjscie`` (klucze: wynik, podglad)
    rodzaj: str = ""  # blad: jeden z RODZAJE_BLEDU
    blad: str = ""  # blad: komunikat jednym zdaniem
    szczegoly: str = ""  # blad: slad wyjatku z procesu roboczego (do logu, nie dla technika)
    czas_s: float | None = None  # wynik / blad: ile trwalo zadanie od wyslania do procesu
    niezakonczone: tuple = ()  # zatrzymany: zadania niezakonczone (w toku pierwsze, potem kolejka) - do ponownego zlecenia


# ----------------------------------------------------------------------------
# proces roboczy
# ----------------------------------------------------------------------------
def bez_nazw_z_puli(tekst: str, foldery) -> str:
    """Usuwa z komunikatu sciezki plikow lezacych w folderach puli (nazwy folderow zlecen i plikow zawieraja nazwiska -
    nie moga wyjsc do logow ani na ekran; plan etapu 3, wymaganie K10): sciezka -> ``<projekt>``. Sama sciezka folderu
    puli zostaje. Gole nazwy plikow i folderow (bez sciezki) czysci ``CzyscicielNazw``."""
    for f in foldery:
        f = str(f).rstrip("\\/")
        if not f:
            continue
        warianty = {f, f.replace("\\", "/"), f.replace("/", "\\"), f.replace("\\", "\\\\"), f.replace("/", "\\\\")}
        for w in sorted(warianty, key=len, reverse=True):
            tekst = re.sub(re.escape(w) + r"[\\/]+[^'\"\n;|<>]*", lambda m: ZNACZNIK_PULI, tekst, flags=re.IGNORECASE)
    return tekst


def _liter(s: str) -> int:
    return sum(1 for c in s if c.isalpha())


class CzyscicielNazw:
    """Czysci teksty wychodzace z procesu roboczego z nazw z puli projektow (P5, wymaganie K10 - nazwy plikow i folderow
    zlecen zawieraja nazwiska; poza baza tylko sha16).

    * pelna sciezka pod folderem puli -> ``<projekt>`` (``bez_nazw_z_puli``);
    * sama nazwa pliku z puli (z rozszerzeniem albo bez) -> ``<projekt sha16>`` (skrot zawartosci, jak ``synth.skrot_pliku``;
      liczony dopiero, gdy nazwa wystapi w tekscie); nazwa wspolna dla kilku plikow -> ``<projekt>``;
    * nazwa folderu w puli -> ``<projekt>``.
    Nazwy dopasowywane bez rozrozniania wielkosci liter i tylko w calosci (granice slowa i separatory: nie jako czesc
    dluzszej nazwy ani slowa), najdluzsza najpierw. Zostaja: sam folder puli z zadania, nazwy folderow z mniej niz 2 literami
    (np. numer kuwety ``12``) i rdzenie nazw plikow krotsze niz 3 znaki albo z mniej niz 2 literami (nie sa danymi
    osobowymi, a ich zamiana psulaby liczby i zwykle slowa). ``pomin`` - pliki, ktorych nazw nie ruszac (skan zadania, gdy
    lezy w folderze puli). Wywolanie ``czysciciel(tekst)`` - jeden tekst (komunikat bledu, slad wyjatku);
    ``czysciciel.oczysc(struktura_json)`` - kopia, w ktorej zmienione sa TYLKO teksty wolne (N2: klucze z
    ``POLA_TEKSTU_WOLNEGO``); pola decyzji (``status``, ``typ``, ``id``, ``skan``, kolory gniazd ...), klucze i liczby -
    bez zmian, nawet gdy folder w puli nazywa sie ``OK`` albo plik ``korona.stl``."""

    def __init__(self, foldery, pomin=()):
        self.foldery: list[str] = []
        self._mapa: dict[str, Path | None] = {}  # nazwa malymi literami -> plik (None = folder albo nazwa niejednoznaczna)
        self._skroty: dict[Path, str] = {}
        self._wzor = None
        try:
            self.foldery = [str(f) for f in foldery if str(f)]
            pomijane = {os.path.normcase(os.path.abspath(str(p))) for p in pomin}
            for f in self.foldery:
                korzen = Path(f)
                try:
                    wpisy = list(korzen.rglob("*")) if korzen.is_dir() else []
                except OSError:
                    wpisy = []
                for p in wpisy:
                    try:
                        plik = p.is_file()
                    except OSError:
                        continue
                    if plik:
                        if os.path.normcase(os.path.abspath(str(p))) in pomijane:
                            continue
                        self._dodaj(p.name, p)
                        if len(p.stem) >= 3 and _liter(p.stem) >= 2:
                            self._dodaj(p.stem, p)
                    elif _liter(p.name) >= 2:
                        self._dodaj(p.name, None)
            if self._mapa:
                nazwy = sorted(self._mapa, key=len, reverse=True)
                self._wzor = re.compile(r"(?<![\w\-.])(?:" + "|".join(re.escape(n) for n in nazwy) + r")(?![\w\-]|\.\w)", re.IGNORECASE)
        except Exception:  # noqa: BLE001 - zostaje samo czyszczenie sciezek; analiza nie moze sie o to wywrocic
            self._mapa, self._wzor = {}, None

    def _dodaj(self, nazwa: str, cel: Path | None) -> None:
        k = nazwa.lower()
        self._mapa[k] = None if (k in self._mapa and self._mapa[k] != cel) else cel

    def _zamien(self, m) -> str:
        cel = self._mapa.get(m.group(0).lower())
        if cel is None:
            return ZNACZNIK_PULI
        s = self._skroty.get(cel)
        if s is None:
            try:
                s = _skrot16(cel)
            except OSError:
                s = ""
            self._skroty[cel] = s
        return f"<projekt {s}>" if s else ZNACZNIK_PULI

    def __call__(self, tekst):
        if not isinstance(tekst, str) or not tekst:
            return tekst
        tekst = bez_nazw_z_puli(tekst, self.foldery)
        return self._wzor.sub(self._zamien, tekst) if self._wzor is not None else tekst

    def oczysc(self, o, klucz: str | None = None):
        """Kopia struktury JSON z oczyszczonymi tekstami wolnymi. ``klucz`` - klucz slownika, pod ktorym lezy ``o`` (lista
        dziedziczy klucz; slownik w liscie zaczyna od nowa); tekst bez klucza (sam napis, lista napisow) = tekst wolny."""
        if isinstance(o, str):
            return self(o) if klucz is None or tekst_wolny(klucz) else o
        if isinstance(o, dict):
            return {k: self.oczysc(v, k) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [self.oczysc(v, klucz) for v in o]
        return o


def tekst_wolny(klucz) -> bool:
    """N2: czy pole o tym kluczu jest tekstem wolnym (komunikat, uwaga, ostrzezenie, tresc bledu), ktory ``CzyscicielNazw``
    moze zmienic. Pola statusow, typow, identyfikatorow i liczb - nigdy."""
    k = str(klucz)
    return k in POLA_TEKSTU_WOLNEGO or any(k.endswith("_" + p) for p in POLA_TEKSTU_WOLNEGO)


class PlikNiedostepny(Exception):
    """Pliku skanu nie da sie skopiowac przez ``czekaj_na_plik_s`` (inny program trzyma go bez zgody na odczyt albo brak
    uprawnien) - ``blad`` rodzaju ``plik_niedostepny`` z prawdziwym komunikatem (N1). Zadanie trzeba zlecic ponownie."""


class SilnikZatrzymany(RuntimeError):
    """``zlec`` po rozpoczeciu ``stop()`` (D-N4): zadanie NIE zostalo przyjete do analizy. ``zadanie`` - to zadanie;
    ``na_liscie`` - True, gdy ``stop()`` jeszcze nie zebral listy: zadanie jest na liscie niezakonczonych (wynik ``stop()``
    i zdarzenie ``zatrzymany``), wiec aplikacja zapisze je razem z innymi; False - lista juz oddana, zadanie trzeba zapisac
    samemu (albo wroci przez nadrabianie ``scanner``)."""

    def __init__(self, komunikat: str, zadanie, na_liscie: bool):
        super().__init__(komunikat)
        self.zadanie, self.na_liscie = zadanie, na_liscie


class PlikZmieniony(Exception):
    """Tresc pliku skanu nie jest ta, ktorej dotyczy zadanie (P1) - wynik nie moze dostac cudzego skrotu."""


def _zakoncz_proces(kod: int) -> None:
    """Natychmiastowy koniec procesu roboczego, bez sprzatania bibliotek (watek analizy moze byc w srodku Open3D)."""
    try:
        sys.stderr.write(f"silnik: proces roboczy konczy sie sam (kod {kod})\n")
        sys.stderr.flush()
    except Exception:  # noqa: BLE001
        pass
    if os.name == "nt":
        try:
            import ctypes

            k32 = ctypes.WinDLL("kernel32", use_last_error=True)
            k32.GetCurrentProcess.restype = ctypes.c_void_p
            k32.TerminateProcess.argtypes = [ctypes.c_void_p, ctypes.c_uint]
            k32.TerminateProcess(k32.GetCurrentProcess(), kod)
        except Exception:  # noqa: BLE001
            pass
    os._exit(kod)


class Straznik:
    """Pilnuje procesu roboczego od srodka (P6). Proces okna zabity twardo (Menedzer zadan, awaria Qt) nie zamyka lacza
    w trakcie analizy, a limitu czasu pilnuje nadzorca, ktorego juz nie ma - wiec proces roboczy sam: konczy sie, gdy
    zniknie proces okna (``rodzic_zyje()`` False) albo gdy zadanie trwa dluzej niz ``limit_zadania_s`` + ``ZAPAS_LIMITU_S``.
    ``sprawdz()`` - jedno sprawdzenie; ``uruchom()`` - watek sprawdzajacy co ``OKRES_STRAZNIKA_S``.
    Granica (D-N5): to watek Pythona - nie dostaje czasu, gdy analiza stoi w wywolaniu natywnym trzymajacym GIL
    (zmierzone: ``segment_plane``, ``estimate_normals`` w Open3D). Dlatego na Windows proces roboczy jest dodatkowo
    w obiekcie zadania procesu okna (``_dolacz_do_obiektu_zadania``) - system konczy go razem z procesem okna."""

    def __init__(self, rodzic_zyje, limit_zadania_s: float | None = LIMIT_ZADANIA_S, zakoncz=_zakoncz_proces, zegar=time.monotonic):
        self.rodzic_zyje, self.limit_zadania_s, self.zakoncz, self.zegar = rodzic_zyje, limit_zadania_s, zakoncz, zegar
        self._od: float | None = None

    def poczatek_zadania(self) -> None:
        self._od = self.zegar()

    def koniec_zadania(self) -> None:
        self._od = None

    def sprawdz(self) -> None:
        if not self.rodzic_zyje():
            self.zakoncz(KOD_BEZ_PROCESU_OKNA)
            return
        od, limit = self._od, self.limit_zadania_s
        if od is not None and limit is not None and self.zegar() - od > limit + ZAPAS_LIMITU_S:
            self.zakoncz(KOD_LIMIT_ZADANIA)

    def uruchom(self, okres_s: float = OKRES_STRAZNIKA_S) -> threading.Thread:
        def petla() -> None:
            while True:
                try:
                    self.sprawdz()
                except Exception:  # noqa: BLE001 - straznik nie moze sie skonczyc
                    pass
                time.sleep(okres_s)

        w = threading.Thread(target=petla, name="silnik-straznik", daemon=True)
        w.start()
        return w


class PamiecPul:
    """Pule projektow trzymane w procesie roboczym miedzy zadaniami (budowa puli to sekundy, plytek jest kilkanascie dziennie)."""

    def __init__(self, limit: int = PUL_W_PAMIECI):
        self.limit = max(1, limit)
        self._pule: collections.OrderedDict = collections.OrderedDict()

    def __len__(self) -> int:
        return len(self._pule)

    def dla(self, opis: OpisPuli):
        """Funkcja ``pula_dla(wspolczynnik) -> match.Pula`` dla ``porownaj``."""

        def pula_dla(w: float):
            from . import match as M
            from . import synth as S

            foldery = [Path(f) for f in opis.foldery]
            h = hashlib.sha256()
            for f in foldery:  # lista plikow projektow: zmiana w folderze = nowa pula
                for p in S.pliki_projektow(f):
                    st = p.stat()
                    h.update(f"{p.relative_to(f).as_posix()}|{st.st_size}|{st.st_mtime_ns}\n".encode("utf-8"))
            klucz = (tuple(str(f) for f in foldery), round(float(w), 9), opis.orientacja,
                     tuple(sorted((opis.wspolczynniki or {}).items())), h.hexdigest())
            if klucz in self._pule:
                self._pule.move_to_end(klucz)
                return self._pule[klucz]
            pula = M.Pula(foldery, w, opis.orientacja, opis.wspolczynniki) if opis.wspolczynniki else M.Pula(foldery, w, opis.orientacja)
            self._pule[klucz] = pula
            while len(self._pule) > self.limit:
                self._pule.popitem(last=False)
            return pula

        return pula_dla


def _wczytaj_funkcje(nazwa: str):
    modul, _, funkcja = nazwa.partition(":")
    return getattr(importlib.import_module(modul), funkcja)


def _skrot16(plik: Path) -> str:
    h = hashlib.sha256()
    with open(plik, "rb") as f:
        for blok in iter(lambda: f.read(BLOK_ODCZYTU), b""):
            h.update(blok)
    return h.hexdigest()[:16]


# --- kopia robocza skanu (N1) i sprzatanie
def _pid_zyje(pid: int) -> bool:
    """Czy proces o tym numerze jeszcze dziala. Proces innego konta (brak dostepu) liczy sie jako zyjacy - jego plikow nie
    ruszamy. Numer uzyty ponownie przez inny proces = "zyje" (resztki zostaja do nastepnego sprzatania)."""
    if pid <= 0:
        return False
    if os.name == "nt":
        import ctypes

        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.OpenProcess.restype = ctypes.c_void_p
        k32.OpenProcess.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32]
        k32.GetExitCodeProcess.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32)]
        k32.CloseHandle.argtypes = [ctypes.c_void_p]
        uchwyt = k32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not uchwyt:
            return ctypes.get_last_error() == 5  # ERROR_ACCESS_DENIED: proces jest, tylko nie nasz
        try:
            kod = ctypes.c_uint32()
            return not k32.GetExitCodeProcess(uchwyt, ctypes.byref(kod)) or kod.value == 259  # STILL_ACTIVE
        finally:
            k32.CloseHandle(uchwyt)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except OSError:
        return True
    return True


def _sprzataj_katalog_roboczy(katalog: Path) -> None:
    """Usuwa z katalogu roboczego kopie skanow (``<pid>_<zadanie>``) procesow, ktorych juz nie ma (zabitych w trakcie
    zadania), i resztki tego procesu; kopie zyjacych procesow (inny silnik, inny program) zostaja. Wolane przy starcie
    procesu roboczego i przed kazda kopia - na dysku jest najwyzej jedna kopia na proces roboczy."""
    try:
        wpisy = list(os.scandir(katalog))
    except OSError:
        return
    for e in wpisy:
        m = re.match(r"(\d+)_", e.name)
        if not m:
            continue
        pid = int(m.group(1))
        if pid != os.getpid() and _pid_zyje(pid):
            continue
        try:
            if e.is_dir(follow_symlinks=False):
                shutil.rmtree(e.path, ignore_errors=True)
            else:
                os.unlink(e.path)
        except OSError:
            pass


def _sprzataj_tmp(folder: Path) -> None:
    """D-N6: pliki tymczasowe zapisu (``<plik>.<pid>.tmp``) po procesach, ktorych juz nie ma (zabitych w trakcie zapisu)."""
    try:
        wpisy = list(os.scandir(folder))
    except OSError:
        return
    for e in wpisy:
        m = re.search(r"\.(\d+)\.tmp$", e.name)
        if m and (int(m.group(1)) == os.getpid() or not _pid_zyje(int(m.group(1)))):
            try:
                os.unlink(e.path)
            except OSError:
                pass


def _kopiuj_skan(skan: Path, cel: Path, czekaj_s: float, na_oczekiwanie=None) -> str:
    """N1: kopia robocza skanu w ``cel``; zwraca sha16 KOPII (liczony przy kopiowaniu - tresc analizowana i skrot sa z definicji
    te same). Odczyt przez ``otworz_zrodlo`` (pelne wspoldzielenie: program skanera moze w tym czasie pisac, przenosic i
    usuwac plik). Pliku nie da sie otworzyc (zajety) albo zmienil sie w trakcie kopiowania: ponawianie z rosnacym odstepem
    (``na_oczekiwanie()`` raz, przy pierwszej przeszkodzie), po ``czekaj_s`` ``PlikNiedostepny``. Pliku nie ma = ``FileNotFoundError``."""
    from .dzien_skanera_rdzen import otworz_zrodlo

    t0, proba, zgloszone, powod = time.monotonic(), 0, False, ""
    while True:
        try:
            zrodlo = otworz_zrodlo(skan)
        except FileNotFoundError:
            raise FileNotFoundError(f"brak pliku skanu {skan.name} (przeniesiony albo usuniety, zanim analiza ruszyla)") from None
        except OSError as e:
            powod = f"{type(e).__name__}: {e}"
        else:
            with zrodlo:
                przed = os.fstat(zrodlo.fileno())
                wolne = shutil.disk_usage(cel.parent).free
                if wolne < przed.st_size + ZAPAS_DYSKU_B:
                    raise OSError(f"za malo miejsca na dysku na kopie robocza skanu: wolne {wolne // 2**20} MB, potrzeba "
                                  f"{(przed.st_size + ZAPAS_DYSKU_B) // 2**20} MB (katalog roboczy {cel.parent.parent})")
                h = hashlib.sha256()
                with open(cel, "wb") as f:
                    for blok in iter(lambda: zrodlo.read(BLOK_ODCZYTU), b""):
                        h.update(blok)
                        f.write(blok)
                po = os.fstat(zrodlo.fileno())
            if (po.st_size, po.st_mtime_ns) == (przed.st_size, przed.st_mtime_ns):
                return h.hexdigest()[:16]
            powod = "plik zmienial sie w trakcie kopiowania (program skanera jeszcze go zapisuje)"
        if time.monotonic() - t0 >= czekaj_s:
            raise PlikNiedostepny(f"nie da sie odczytac pliku skanu {skan.name} przez {czekaj_s:.0f} s ({powod}) - inny program trzyma go "
                                  "bez zgody na odczyt albo brak uprawnien; analiza pominieta, zlec ja ponownie po zwolnieniu pliku")
        if not zgloszone and na_oczekiwanie is not None:
            zgloszone = True
            na_oczekiwanie()
        proba += 1
        time.sleep(min(ODSTEP_KOPII_MAX_S, 0.05 * 2 ** min(proba, 16), max(0.0, czekaj_s - (time.monotonic() - t0)) + 0.01))


# --- obiekt zadania Windows (D-N5)
_OBIEKT_ZADANIA = None  # uchwyt obiektu zadania procesu okna: jeden na proces, NIGDY nie zamykany (zamkniecie = koniec procesow roboczych)
_ZAMEK_OBIEKTU = threading.Lock()


def _utworz_obiekt_zadania():
    """Obiekt zadania Windows z ``JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE``: gdy proces okna sie konczy (takze zabity), system
    zamyka jego uchwyty, a z ostatnim uchwytem konczy wszystkie procesy w obiekcie. Uchwyt nie jest dziedziczony."""
    import ctypes

    class LimityPodstawowe(ctypes.Structure):  # JOBOBJECT_BASIC_LIMIT_INFORMATION
        _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64), ("PerJobUserTimeLimit", ctypes.c_int64), ("LimitFlags", ctypes.c_uint32),
                    ("MinimumWorkingSetSize", ctypes.c_size_t), ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", ctypes.c_uint32),
                    ("Affinity", ctypes.c_size_t), ("PriorityClass", ctypes.c_uint32), ("SchedulingClass", ctypes.c_uint32)]

    class Liczniki(ctypes.Structure):  # IO_COUNTERS
        _fields_ = [(n, ctypes.c_uint64) for n in ("ReadOperationCount", "WriteOperationCount", "OtherOperationCount", "ReadTransferCount",
                                                    "WriteTransferCount", "OtherTransferCount")]

    class LimityRozszerzone(ctypes.Structure):  # JOBOBJECT_EXTENDED_LIMIT_INFORMATION
        _fields_ = [("BasicLimitInformation", LimityPodstawowe), ("IoInfo", Liczniki), ("ProcessMemoryLimit", ctypes.c_size_t),
                    ("JobMemoryLimit", ctypes.c_size_t), ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t)]

    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.CreateJobObjectW.restype = ctypes.c_void_p
    k32.CreateJobObjectW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p]
    k32.SetInformationJobObject.restype = ctypes.c_int
    k32.SetInformationJobObject.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32]
    k32.CloseHandle.argtypes = [ctypes.c_void_p]
    uchwyt = k32.CreateJobObjectW(None, None)
    if not uchwyt:
        raise ctypes.WinError(ctypes.get_last_error())
    info = LimityRozszerzone()
    info.BasicLimitInformation.LimitFlags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    if not k32.SetInformationJobObject(uchwyt, 9, ctypes.byref(info), ctypes.sizeof(info)):  # JobObjectExtendedLimitInformation
        blad = ctypes.WinError(ctypes.get_last_error())
        k32.CloseHandle(uchwyt)
        raise blad
    return uchwyt


def _dolacz_do_obiektu_zadania(pid: int) -> bool:
    """D-N5: wklada proces roboczy do obiektu zadania procesu okna - system konczy go razem z procesem okna niezaleznie od
    tego, co proces roboczy robi (takze w wywolaniu natywnym trzymajacym GIL, gdy ``Straznik`` nie dziala). True = w obiekcie;
    False = nie Windows. ``OSError`` = nie udalo sie (zostaje sam ``Straznik``)."""
    global _OBIEKT_ZADANIA
    if os.name != "nt":
        return False
    import ctypes

    with _ZAMEK_OBIEKTU:
        if _OBIEKT_ZADANIA is None:
            _OBIEKT_ZADANIA = _utworz_obiekt_zadania()
        obiekt = _OBIEKT_ZADANIA
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.OpenProcess.restype = ctypes.c_void_p
    k32.OpenProcess.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32]
    k32.AssignProcessToJobObject.restype = ctypes.c_int
    k32.AssignProcessToJobObject.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    k32.CloseHandle.argtypes = [ctypes.c_void_p]
    proces = k32.OpenProcess(0x0100 | 0x0001, False, pid)  # PROCESS_SET_QUOTA | PROCESS_TERMINATE
    if not proces:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        if not k32.AssignProcessToJobObject(obiekt, proces):
            raise ctypes.WinError(ctypes.get_last_error())
    finally:
        k32.CloseHandle(proces)
    return True


# --- start procesu roboczego bez konsoli procesu okna i z limitem czasu (E3-A2p)
_FLAGI_STARTU = threading.local()  # .flagi: dodatkowe flagi CreateProcess dla Process.start() w tym watku (watek silnik-start)
_ZAMEK_WINAPI = threading.Lock()


class _WinapiZFlagami:
    """Pelnomocnik modulu ``_winapi`` w ``multiprocessing.popen_spawn_win32``: ``CreateProcess`` dostaje dodatkowe flagi
    z ``_FLAGI_STARTU`` watku wolajacego (watek ``silnik-start``: ``FLAGI_PROCESU_ROBOCZEGO``); inne watki i pozostale
    funkcje ``_winapi`` - bez zmian. Biblioteka standardowa wola ``CreateProcess`` zawsze z flagami 0 i nie daje ich podac."""

    def __init__(self, winapi):
        self._winapi = winapi

    def __getattr__(self, nazwa):
        return getattr(self._winapi, nazwa)

    def CreateProcess(self, *argumenty):  # noqa: N802 - nazwa jak w _winapi
        argumenty = list(argumenty)
        argumenty[5] = int(argumenty[5]) | getattr(_FLAGI_STARTU, "flagi", 0)  # creation_flags
        return self._winapi.CreateProcess(*argumenty)


def _flagi_startu_dostepne() -> bool:
    """Windows: wstawia ``_WinapiZFlagami`` do ``multiprocessing.popen_spawn_win32`` (raz na proces). False poza Windows."""
    if os.name != "nt":
        return False
    from multiprocessing import popen_spawn_win32

    with _ZAMEK_WINAPI:
        if not isinstance(popen_spawn_win32._winapi, _WinapiZFlagami):
            popen_spawn_win32._winapi = _WinapiZFlagami(popen_spawn_win32._winapi)
    return True


def _popen_w_watku(watek: threading.Thread):
    """Obiekt ``Popen`` z konstruktora, w ktorym stoi ``Process.start()`` watku ``watek`` (ramki stosu tego watku), albo None.
    ``Process`` dostaje go dopiero po powrocie z konstruktora, a ten czeka na zapis danych startowych do lacza; ``pid``
    i uchwyt procesu potomnego sa w nim juz od ``CreateProcess``."""
    ramka = sys._current_frames().get(watek.ident)
    while ramka is not None:
        if ramka.f_code.co_name == "__init__":
            kandydat = ramka.f_locals.get("self")
            if type(kandydat).__name__ == "Popen" and getattr(kandydat, "pid", None) is not None:
                return kandydat
        ramka = ramka.f_back
    return None


def _kod_martwego_potomka(watek: threading.Thread) -> int | None:
    """Kod wyjscia procesu potomnego zawieszonego ``Process.start()`` w watku ``watek``, gdy ten proces juz sie zakonczyl
    (np. 0xC0000142 - blad inicjalizacji DLL przy starcie); None, gdy dziala albo jeszcze go nie ma. Potomek, ktory zginal
    przed odczytem danych startowych, juz ich nie przeczyta - nie ma po co czekac do konca limitu."""
    popen = _popen_w_watku(watek)
    uchwyt = getattr(popen, "_handle", None)
    if os.name != "nt" or uchwyt is None:
        return None
    try:
        import _winapi

        kod = _winapi.GetExitCodeProcess(int(uchwyt))
    except OSError:
        return None
    return None if kod == 259 else kod & 0xFFFFFFFF  # 259 = STILL_ACTIVE


def _opis_potomka(popen) -> str:
    """Stan procesu potomnego zawieszonego startu - do logu (przyczyna zawieszenia): kod wyjscia albo "dziala", czas CPU,
    liczba uchwytow i zaladowane moduly (potomek, ktory nie doszedl do odczytu lacza, ma ich malo)."""
    opis = f"proces potomny pid {popen.pid}"
    uchwyt = getattr(popen, "_handle", None)
    if os.name != "nt" or uchwyt is None:
        return opis
    try:
        import ctypes
        from ctypes import wintypes

        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        h = ctypes.c_void_p(int(uchwyt))
        kod = wintypes.DWORD()
        k32.GetExitCodeProcess.argtypes = [ctypes.c_void_p, ctypes.POINTER(wintypes.DWORD)]
        if k32.GetExitCodeProcess(h, ctypes.byref(kod)):
            opis += ": dziala" if kod.value == 259 else f": zakonczony, kod wyjscia 0x{kod.value:08X}"
        czasy = [wintypes.FILETIME() for _ in range(4)]
        k32.GetProcessTimes.argtypes = [ctypes.c_void_p] + [ctypes.POINTER(wintypes.FILETIME)] * 4
        if k32.GetProcessTimes(h, *[ctypes.byref(c) for c in czasy]):
            cpu = sum((c.dwHighDateTime << 32 | c.dwLowDateTime) for c in czasy[2:]) / 1e7
            opis += f", czas CPU {cpu:.2f} s"
        liczba = wintypes.DWORD()
        k32.GetProcessHandleCount.argtypes = [ctypes.c_void_p, ctypes.POINTER(wintypes.DWORD)]
        if k32.GetProcessHandleCount(h, ctypes.byref(liczba)):
            opis += f", uchwytow {liczba.value}"
        moduly = (ctypes.c_void_p * 512)()
        bajty = wintypes.DWORD()
        psapi.EnumProcessModulesEx.argtypes = [ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD), wintypes.DWORD]
        psapi.GetModuleBaseNameW.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_wchar_p, wintypes.DWORD]
        if psapi.EnumProcessModulesEx(h, moduly, ctypes.sizeof(moduly), ctypes.byref(bajty), 0x03):  # LIST_MODULES_ALL
            nazwy = []
            for m in moduly[: min(512, bajty.value // ctypes.sizeof(ctypes.c_void_p))]:
                bufor = ctypes.create_unicode_buffer(260)
                if psapi.GetModuleBaseNameW(h, ctypes.c_void_p(m), bufor, 260):
                    nazwy.append(bufor.value)
            opis += f", modulow {len(nazwy)}: {', '.join(nazwy[:40])}{' ...' if len(nazwy) > 40 else ''}"
        else:
            opis += f", modulow nie da sie odczytac (blad {ctypes.get_last_error()})"
    except Exception as e:  # noqa: BLE001 - diagnostyka nie moze zatrzymac przerwania startu
        opis += f" (diagnostyka niedostepna: {type(e).__name__}: {e})"
    return opis


def _anuluj_zapis(uchwyt_watku) -> None:
    """Windows: anuluje synchroniczne wejscie / wyjscie watku (zawieszony zapis danych startowych do lacza konczy sie bledem)."""
    import ctypes

    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.CancelSynchronousIo.argtypes = [ctypes.c_void_p]
    k32.CancelSynchronousIo(uchwyt_watku)


def _przerwij_start(watek: threading.Thread, czekaj_s: float = CZEKAJ_NA_PRZERWANIE_S) -> str:
    """Odblokowuje zawieszony ``Process.start()`` w watku ``watek``: zabija proces potomny (jesli juz powstal) i anuluje
    zapis do lacza (Windows: ``CancelSynchronousIo`` na uchwycie watku otwartym raz, wiec numer watku nie moze trafic do
    innego) - sama smierc potomka zapisu nie konczy, bo uchwyt odczytu lacza trzyma tez proces okna. Czeka najwyzej
    ``czekaj_s`` na koniec watku. Zwraca opis potomka (stan sprzed zabicia) do logu."""
    popen = _popen_w_watku(watek)
    opis = _opis_potomka(popen) if popen is not None else "proces potomny jeszcze nie utworzony"
    if popen is not None:
        try:
            popen.kill()
        except Exception:  # noqa: BLE001 - proces juz nie zyje
            pass
    del popen  # bez referencji z nadzorcy: po wyjatku w konstruktorze Popen jego finalizator zamyka uchwyty
    uchwyt_watku = None
    if os.name == "nt" and watek.is_alive() and watek.native_id is not None:
        import ctypes

        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.OpenThread.restype = ctypes.c_void_p
        k32.OpenThread.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32]
        uchwyt_watku = k32.OpenThread(0x0001, False, watek.native_id)  # THREAD_TERMINATE - wymagane przez CancelSynchronousIo
    try:
        t0 = time.monotonic()
        while watek.is_alive() and time.monotonic() - t0 < czekaj_s:
            if uchwyt_watku:
                _anuluj_zapis(uchwyt_watku)  # powtarzane: watek mogl jeszcze nie wejsc w zapis (CreateProcess, pickle)
            watek.join(0.05)
    finally:
        if uchwyt_watku:
            import ctypes

            k32 = ctypes.WinDLL("kernel32", use_last_error=True)
            k32.CloseHandle.argtypes = [ctypes.c_void_p]
            k32.CloseHandle(uchwyt_watku)
    if watek.is_alive():
        opis += f"; watek startu nie zakonczyl sie w {czekaj_s:g} s po przerwaniu - zostawiony (zabije proces, jesli start sie skonczy)"
    return opis


def _zamknij_porzucony(p) -> None:
    """Proces, ktorego ``Process.start()`` skonczyl sie po przerwaniu proby - bez nadzoru, wiec zabity."""
    try:
        p.kill()
        p.join(5.0)
        p.close()
    except Exception:  # noqa: BLE001
        pass


def wczytaj_podglad(plik) -> dict:
    """Plik ``..._podglad.npz`` z silnika -> {numer gniazda: (punkty N x 3 w ukladzie plytki, odchylka kazdego punktu w mm)}."""
    import numpy as np

    with np.load(plik) as z:
        return {int(k[1:-2]): (z[k], z[k[:-2] + "_d"]) for k in z.files if k.endswith("_P")}


def _zapisz_bez_nadpisania(cel: Path, zapisz) -> None:
    """Zapis przez plik tymczasowy i zmiane nazwy, ktora NIE nadpisuje istniejacego pliku (wtedy ``FileExistsError``):
    urwany zapis nie zostawia polowy pliku pod docelowa nazwa, a plik innego zadania nie moze zostac zastapiony."""
    tmp = cel.with_name(f"{cel.name}.{os.getpid()}.tmp")
    try:
        with open(tmp, "wb") as f:
            zapisz(f)
        if os.name == "nt":
            os.rename(tmp, cel)  # Windows: zmiana nazwy nigdy nie nadpisuje istniejacego pliku
        else:
            os.link(tmp, cel)
            os.unlink(tmp)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _zapisz_wyjscie(zadanie: ZadanieAnalizy, wynik: dict, podglad: dict) -> dict:
    """P4 / D-N6: pliki unikalne na zadanie, BEZ nazwy skanu (jak w A1: program skanera moze nazywac pliki nazwiskiem ze
    zlecenia) - ``<czas przyjecia>_<sha16>[_n]_wynik.json`` i ``..._podglad.npz`` (ten sam rdzen). Najpierw podglad, potem
    wynik: plik wyniku oznacza komplet. Istniejacy plik nigdy nie jest nadpisywany (kolejny wolny numer ``_n``). Pliki
    tymczasowe po procesach zabitych w trakcie zapisu sa usuwane przed zapisem."""
    import numpy as np

    wyj = Path(zadanie.wyjscie)
    wyj.mkdir(parents=True, exist_ok=True)
    _sprzataj_tmp(wyj)
    czas = time.strftime("%Y%m%d_%H%M%S", time.localtime(zadanie.przyjete if zadanie.przyjete is not None else time.time()))
    baza = f"{czas}_{wynik['skan_sha16']}"
    tablice = {}
    for gniazdo, wi in podglad.items():
        P, d = getattr(wi, "_P", None), getattr(wi, "_d", None)
        if gniazdo is None or P is None or d is None:
            continue
        tablice[f"g{int(gniazdo)}_P"] = np.asarray(P, dtype=np.float32)
        tablice[f"g{int(gniazdo)}_d"] = np.asarray(d, dtype=np.float32)
    dane = json.dumps(wynik, ensure_ascii=False, indent=1).encode("utf-8")
    for n in range(1, 10000):
        rdzen = baza if n == 1 else f"{baza}_{n}"
        p_json, p_npz = wyj / f"{rdzen}_wynik.json", wyj / f"{rdzen}_podglad.npz"
        if p_json.exists() or p_npz.exists():
            continue
        if tablice:
            try:
                _zapisz_bez_nadpisania(p_npz, lambda f: np.savez(f, **tablice))
            except FileExistsError:
                continue
        try:
            _zapisz_bez_nadpisania(p_json, lambda f: f.write(dane))
        except FileExistsError:
            if tablice:
                try:
                    os.unlink(p_npz)
                except OSError:
                    pass
            continue
        pliki = {"wynik": str(p_json)}
        if tablice:
            pliki["podglad"] = str(p_npz)
        return pliki
    raise FileExistsError(f"brak wolnej nazwy pliku wyniku {baza} w folderze wyjscia")


def _folder_kopii(katalog: Path, zadanie: ZadanieAnalizy) -> Path:
    """Folder kopii roboczej zadania: ``<katalog roboczy>/<pid procesu roboczego>_<zadanie_id>`` (w nim plik o nazwie skanu)."""
    return Path(katalog) / f"{os.getpid()}_{zadanie.zadanie_id}"


def _wykonaj(zadanie: ZadanieAnalizy, funkcja, ust: dict, pamiec: PamiecPul, lacze, czysc: CzyscicielNazw, katalog: Path,
             czekaj_na_plik_s: float = CZEKAJ_NA_PLIK_S) -> tuple[dict, dict | None]:
    skan = Path(zadanie.skan)
    if not skan.is_file():
        raise FileNotFoundError(f"brak pliku skanu {skan.name}")
    uklad = "auto" if zadanie.uklad in (None, "", "auto", "rozpoznaj") else zadanie.uklad
    foldery = [Path(f) for f in zadanie.pula.foldery]
    podglad: dict | None = {} if zadanie.wyjscie is not None else None

    def postep(etap, udzial) -> None:
        lacze.send(("postep", zadanie.zadanie_id, str(etap), float(udzial)))

    _sprzataj_katalog_roboczy(katalog)  # kopia jedna naraz: resztki poprzednich zadan i procesow zabitych
    folder = _folder_kopii(katalog, zadanie)
    try:
        folder.mkdir(parents=True, exist_ok=True)
        kopia = folder / skan.name  # ta sama nazwa pliku: wynik["skan"] jak w wierszu polecen
        sha16 = _kopiuj_skan(skan, kopia, czekaj_na_plik_s, lambda: postep(ETAP_OCZEKIWANIA, 0.0))  # N1: skrot = tresc analizowana
        if zadanie.skan_sha16 and sha16 != zadanie.skan_sha16:
            raise PlikZmieniony(f"plik skanu zmienil sie, zanim analiza ruszyla (zdarzenie: sha16 {zadanie.skan_sha16}, plik teraz: sha16 {sha16}) - "
                                "analiza pominieta; nowa tresc ma wlasne zdarzenie skanu")
        with warnings.catch_warnings(record=True) as ostrz:  # jak w wierszu polecen: ostrzezenia trafiaja do wyniku
            warnings.simplefilter("always")
            wynik = funkcja(kopia, foldery, uklad, ust, zadanie.pula.wspolczynnik, zadanie.numer, zadanie.pula.orientacja, zadanie.bez_filtru, None,
                            inspekcja=zadanie.inspekcja, podglad=podglad, postep=postep, straznik=zadanie.straznik,
                            pula_dla=pamiec.dla(zadanie.pula), kontekst={})
    finally:
        shutil.rmtree(folder, ignore_errors=True)  # blokada, przeniesienie albo usuniecie pliku skanu po kopii nie szkodzi wynikowi
    if not isinstance(wynik, dict):
        raise TypeError(f"funkcja analizy zwrocila {type(wynik).__name__}, oczekiwany slownik")
    wynik = dict(wynik)
    wynik["ostrzezenia"] = [str(o.message) for o in ostrz]
    wynik = json.loads(json.dumps(wynik, ensure_ascii=False))  # postac jak w <skan>_wynik.json: same typy JSON
    wynik = czysc.oczysc(wynik)  # P5 / N2: teksty wolne bez nazw z puli ("pomijam projekt ...", uwagi, bledy inspekcji); decyzje bez zmian
    wynik["zadanie_id"] = zadanie.zadanie_id
    wynik["skan_sha16"] = sha16
    pliki = _zapisz_wyjscie(zadanie, wynik, podglad or {}) if zadanie.wyjscie is not None else None
    return wynik, pliki


def _robotnik(lacze, ust: dict | None, plik_ustawien, funkcja: str, pul_w_pamieci: int, plik_logu, pamiec_linii=None,
              limit_zadania_s: float | None = LIMIT_ZADANIA_S, katalog_roboczy=None, czekaj_na_plik_s: float = CZEKAJ_NA_PLIK_S) -> None:
    """Cialo procesu roboczego: laduje ustawienia i funkcje analizy, potem wykonuje zadania z lacza, jedno naraz."""
    rodzic = multiprocessing.parent_process()
    straznik = Straznik(rodzic.is_alive if rodzic is not None else (lambda: True), limit_zadania_s)
    straznik.uruchom()  # P6: od pierwszej chwili - takze w trakcie ladowania bibliotek i w trakcie analizy
    if plik_logu is not None:
        try:  # wszystko, co biblioteki wypisuja (takze z C++), trafia do pliku; bez pliku zostaje wyjscie odziedziczone
            log = open(plik_logu, "ab", buffering=0)
            os.dup2(log.fileno(), 1)
            os.dup2(log.fileno(), 2)
            sys.stdout = open(1, "w", encoding="utf-8", errors="replace", closefd=False, buffering=1)
            sys.stderr = open(2, "w", encoding="utf-8", errors="replace", closefd=False, buffering=1)
        except OSError:
            pass
    if sys.stdout is None or sys.stderr is None:  # pythonw: brak konsoli
        sys.stdout = sys.stderr = open(os.devnull, "w")
    try:
        f = _wczytaj_funkcje(funkcja)
        if ust is None:
            from . import ustawienia as UST

            ust = UST.wczytaj_ustawienia(Path(plik_ustawien) if plik_ustawien is not None else None)
        if pamiec_linii is not None:  # linie brzegu projektow (P2) takze na dysku: przezywaja restart procesu i programu
            from . import krawedz as KR

            Path(pamiec_linii).mkdir(parents=True, exist_ok=True)
            KR.ustaw_katalog_pamieci(pamiec_linii)
        pamiec = PamiecPul(pul_w_pamieci)
    except BaseException as e:  # noqa: BLE001 - brak pakietu, zly plik ustawien: nadzorca dostaje komunikat
        try:
            lacze.send(("blad_startu", f"{type(e).__name__}: {e}", traceback.format_exc()))
        except OSError:
            pass
        return
    katalog = Path(katalog_roboczy) if katalog_roboczy is not None else Path(tempfile.gettempdir()) / KATALOG_ROBOCZY
    try:  # N1 / D-N6: kopie po procesach roboczych zabitych w trakcie zadania (Straznik, limit czasu, awaria)
        katalog.mkdir(parents=True, exist_ok=True)
        _sprzataj_katalog_roboczy(katalog)
    except OSError:
        pass  # katalog niedostepny: kazde zadanie dostanie blad z powodem przy probie kopii
    lacze.send(("gotowy", os.getpid()))
    while True:
        try:
            wiadomosc = lacze.recv()
        except (EOFError, OSError):
            return  # proces okna zniknal
        if wiadomosc[0] == "koniec":
            return
        zadanie: ZadanieAnalizy = wiadomosc[1]
        straznik.poczatek_zadania()
        czysc = CzyscicielNazw(zadanie.pula.foldery, pomin=(zadanie.skan,))  # lista plikow puli: nazwy do usuniecia z tekstow
        kopia, oryginal = str(_folder_kopii(katalog, zadanie) / Path(zadanie.skan).name), str(zadanie.skan)

        def tekst(t: str) -> str:  # sciezka kopii roboczej w komunikacie -> plik skanu (technik zna plik skanu, nie kopie)
            return czysc(t.replace(kopia, oryginal).replace(kopia.replace("\\", "\\\\"), oryginal.replace("\\", "\\\\")))

        try:
            wynik, pliki = _wykonaj(zadanie, f, ust, pamiec, lacze, czysc, katalog, czekaj_na_plik_s)
            odpowiedz = ("wynik", zadanie.zadanie_id, wynik, pliki)
        except KeyboardInterrupt:
            return
        except PlikZmieniony as e:
            odpowiedz = ("blad", zadanie.zadanie_id, tekst(str(e)), "", "plik_zmieniony")
        except PlikNiedostepny as e:
            odpowiedz = ("blad", zadanie.zadanie_id, tekst(str(e)), "", "plik_niedostepny")
        except BaseException as e:  # noqa: BLE001 - takze SystemExit z porownaj ("brak projektow STL"); proces pracuje dalej
            odpowiedz = ("blad", zadanie.zadanie_id, tekst(f"{type(e).__name__}: {e}"), tekst(traceback.format_exc()), "analiza")
        finally:
            straznik.koniec_zadania()
        try:
            lacze.send(odpowiedz)
        except OSError:
            return


# ----------------------------------------------------------------------------
# nadzorca w procesie okna
# ----------------------------------------------------------------------------
class Silnik:
    """Kolejka analiz wykonywanych w jednym procesie roboczym, jedna naraz, w kolejnosci zlecen.

    ``ust`` - slownik ustawien przekazany do procesu; None = proces sam wczyta ``plik_ustawien`` (None = ``ustawienia.toml``
    programu, jak wiersz polecen). ``funkcja`` - ``"modul:funkcja"`` analizy (domyslnie ``porownaj.porownaj``).
    ``limit_zadania_s`` - najdluzszy czas jednej analizy. ``plik_logu`` - dokad proces roboczy wypisuje to, co biblioteki
    drukuja na ekran. ``pamiec_linii`` - katalog pamieci podrecznej linii brzegu projektow (``krawedz.ustaw_katalog_pamieci``;
    None = tylko pamiec procesu, na dysk nic nie trafia). ``katalog_roboczy`` - katalog kopii roboczych skanow (N1; None =
    ``<katalog tymczasowy systemu>/qc_silnik``; jedna kopia 45-55 MB naraz na proces roboczy). ``czekaj_na_plik_s`` - jak
    dlugo ponawiac kopiowanie pliku skanu, ktory trzyma inny program. ``na_zdarzenie`` - funkcja wolana z kazdym
    ``ZdarzenieSilnika`` w watku nadzorcy; nie moze czekac na watek, ktory wola ``stop()`` (D-N3). ``limit_startu_s`` -
    czas od ``Process.start()`` do zgloszenia gotowosci przez proces roboczy (ladowanie bibliotek). ``limit_uruchomienia_s``
    i ``proby_uruchomienia`` - limit samego ``Process.start()`` i liczba prob (E3-A2p).
    """

    def __init__(self, ust: dict | None = None, plik_ustawien=None, *, funkcja: str = FUNKCJA_ANALIZY, limit_zadania_s: float = LIMIT_ZADANIA_S,
                 limit_startu_s: float = LIMIT_STARTU_S, pul_w_pamieci: int = PUL_W_PAMIECI, plik_logu=None, pamiec_linii=None,
                 katalog_roboczy=None, czekaj_na_plik_s: float = CZEKAJ_NA_PLIK_S, na_zdarzenie=None,
                 limit_uruchomienia_s: float = LIMIT_URUCHOMIENIA_S, proby_uruchomienia: int = PROBY_URUCHOMIENIA):
        self.ust, self.plik_ustawien, self.funkcja = ust, plik_ustawien, funkcja
        self.limit_zadania_s, self.limit_startu_s, self.pul_w_pamieci, self.plik_logu = limit_zadania_s, limit_startu_s, pul_w_pamieci, plik_logu
        self.limit_uruchomienia_s, self.proby_uruchomienia = float(limit_uruchomienia_s), max(1, int(proby_uruchomienia))
        self.pamiec_linii = str(pamiec_linii) if pamiec_linii is not None else None
        self.katalog_roboczy = str(katalog_roboczy) if katalog_roboczy is not None else os.path.join(tempfile.gettempdir(), KATALOG_ROBOCZY)
        self.czekaj_na_plik_s = float(czekaj_na_plik_s)
        self.na_zdarzenie = na_zdarzenie
        self.zdarzenia: queue.Queue = queue.Queue()  # ZdarzenieSilnika, gdy nie podano ``na_zdarzenie``
        self._ctx = multiprocessing.get_context("spawn")
        self._kolejka: collections.deque = collections.deque()
        self._zamek = threading.Lock()
        self._stop = threading.Event()
        self._watek: threading.Thread | None = None
        self._zatrzymany = False
        self._proces = None
        self._lacze = None
        self._gotowy = False
        self._start_procesu = 0.0
        self._biezace: ZadanieAnalizy | None = None
        self._biezace_od = 0.0
        self._nastepny_id = 1
        self._starty = 0
        self._nieudany_start: tuple | None = None  # (tekst, szczegoly) ostatniego nieudanego startu procesu
        self._po_stopie = False
        self._lista_zebrana = False  # stop() zebral juz liste niezakonczonych (D-N4)
        self._zglaszane: ZadanieAnalizy | None = None  # zadanie, ktorego zdarzenie koncowe wlasnie idzie do odbiorcy (D-N3)
        self._w_obiekcie_zadania = False  # D-N5: proces roboczy jest w obiekcie zadania Windows procesu okna
        self._przerwane_uruchomienia = 0  # E3-A2p: proby Process.start() przerwane po limicie albo zakonczone wyjatkiem

    # --- sterowanie
    def start(self) -> None:
        if self._zatrzymany:
            raise RuntimeError("silnik zatrzymany - utworz nowy obiekt Silnik")
        if self._watek is None or not self._watek.is_alive():
            self._watek = threading.Thread(target=self._petla, name="silnik-nadzorca", daemon=True)
            self._watek.start()

    def stop(self, czekaj_s: float = 5.0) -> list:
        """Konczy prace: trwajaca analiza jest przerywana razem z procesem, kolejka oprozniana. Zwraca liste zadan
        niezakonczonych (``ZadanieAnalizy``: w toku pierwsze, potem kolejka) i zglasza ja zdarzeniem ``zatrzymany``
        (P2) - aplikacja zapisuje je i zleca ponownie po starcie. Zwraca [] przy kolejnym wywolaniu.

        Gwarancja (D-N3, D-N4): kazde przyjete zadanie albo dostaje dokladnie jedno zdarzenie ``wynik`` / ``blad``, albo jest
        na tej liscie - nigdy oba. Po rozpoczeciu ``stop()`` zadne zadanie nie dostaje juz ``wynik`` ani ``blad`` (spoznione
        sa odrzucane); wyjatek: zadanie, ktorego zdarzenie koncowe nadzorca WLASNIE przekazuje (``na_zdarzenie`` blokuje sie
        dluzej niz ``czekaj_s``) - nie ma go na liscie, a zdarzenie dojdzie po ``zatrzymany``. ``zlec`` po rozpoczeciu
        ``stop()`` odmawia (``SilnikZatrzymany``); zadanie odrzucone, zanim lista zostala zebrana, jest na liscie.
        Zdarzenie ``zatrzymany`` jest wolane w watku wywolujacym ``stop()``."""
        with self._zamek:
            if self._po_stopie:
                return []
            self._po_stopie = self._zatrzymany = True
        self._stop.set()
        w = self._watek
        if w is not None and w is not threading.current_thread():
            w.join(czekaj_s)
            if w.is_alive():
                LOG.warning("silnik: nadzorca nie zakonczyl sie w %.1f s (funkcja na_zdarzenie czeka?) - jego spoznione zdarzenia "
                            "koncowe sa odrzucane", czekaj_s)
        self._watek = None
        with self._zamek:
            biezace = self._biezace if self._biezace is not self._zglaszane else None
            niezakonczone = ([biezace] if biezace is not None else []) + list(self._kolejka)
            self._kolejka.clear()
            self._biezace = None
            self._lista_zebrana = True
        self._zamknij_proces(grzecznie=biezace is None)
        self._zglos("zatrzymany", niezakonczone=tuple(niezakonczone))
        return niezakonczone

    def __enter__(self) -> Silnik:
        self.start()
        return self

    def __exit__(self, *exc) -> None:
        self.stop()

    def dziala(self) -> bool:
        return self._watek is not None and self._watek.is_alive()

    @property
    def pid(self) -> int | None:
        """Numer procesu roboczego (None, gdy go nie ma)."""
        p = self._proces
        try:
            return p.pid if p is not None and p.is_alive() else None
        except ValueError:  # proces wlasnie zamkniety przez nadzorce
            return None

    def zlec(self, zadanie: ZadanieAnalizy) -> int:
        """Dodaje zadanie na koniec kolejki; zwraca ``zadanie_id`` (rosnace od 1 w kazdym obiekcie ``Silnik``) i ustawia
        ``przyjete`` (czas przyjecia). Zadanie z ``stop()`` innego obiektu mozna zlecic ponownie - dostanie nowy numer.
        Po rozpoczeciu ``stop()`` - wyjatek ``SilnikZatrzymany`` (podklasa ``RuntimeError``; D-N4): zadanie nie ruszy, a gdy
        ``stop()`` jeszcze nie zebral listy, trafia na liste niezakonczonych (``na_liscie`` True, ``zadanie_id`` bez zmian)."""
        with self._zamek:  # D-N4: sprawdzenie i dopisanie pod jednym zamkiem ze stop()
            if self._po_stopie:
                z = dataclasses.replace(zadanie, przyjete=time.time())
                if not self._lista_zebrana:
                    self._kolejka.append(z)  # nadzorca juz nic nie bierze z kolejki; stop() odda ja w liscie niezakonczonych
                    raise SilnikZatrzymany("silnik sie zatrzymuje - zadanie nie zostalo przyjete do analizy; jest na liscie "
                                           "niezakonczonych z stop()", z, True)
                raise SilnikZatrzymany("silnik zatrzymany - zadanie nie zostalo przyjete", z, False)
            nr = self._nastepny_id
            self._nastepny_id += 1
            self._kolejka.append(dataclasses.replace(zadanie, zadanie_id=nr, przyjete=time.time()))
        return nr

    def zlec_skan(self, zdarzenie, pula: OpisPuli, **pola) -> int:
        """Zadanie z ``scanner.ZdarzenieSkanu``: sciezka i skrot skanu ze zdarzenia, reszta pol jak w ``ZadanieAnalizy``.
        Skrot ze zdarzenia jest porownywany ze skrotem kopii roboczej (P1 / N1: plik nadpisany, zanim analiza ruszyla =
        ``blad`` ``plik_zmieniony``; plik zmieniony, przeniesiony albo zablokowany PO zrobieniu kopii - wynik zostaje)."""
        return self.zlec(ZadanieAnalizy(skan=Path(zdarzenie.plik), pula=pula, skan_sha16=zdarzenie.sha16, **pola))

    def anuluj(self, zadanie_id: int) -> bool:
        """Usuwa z kolejki zadanie, ktore jeszcze nie ruszylo. Zadania w toku nie da sie anulowac."""
        with self._zamek:
            for z in self._kolejka:
                if z.zadanie_id == zadanie_id:
                    self._kolejka.remove(z)
                    return True
        return False

    def w_kolejce(self) -> int:
        return len(self._kolejka)

    def zajety(self) -> bool:
        return self._biezace is not None

    def czekaj_na_pusta_kolejke(self, limit_s: float) -> bool:
        """True, gdy kolejka jest pusta, a ostatnie zadanie zakonczone i zgloszone (D3); False po ``limit_s``."""
        t0 = time.monotonic()
        while True:
            with self._zamek:
                pusto = not self._kolejka and self._biezace is None and self._zglaszane is None
            if pusto:
                return True
            if time.monotonic() - t0 > limit_s:
                return False
            time.sleep(0.02)

    def stan(self) -> dict:
        b = self._biezace
        return {"dziala": self.dziala(), "proces_gotowy": self._gotowy, "pid": self.pid, "w_kolejce": len(self._kolejka),
                "biezace": b.zadanie_id if b is not None else None, "starty_procesu": self._starty, "obiekt_zadania": self._w_obiekcie_zadania,
                "nieudane_uruchomienia": self._przerwane_uruchomienia}

    # --- nadzorca
    def _zglos(self, typ: str, **pola) -> None:
        z = ZdarzenieSilnika(typ=typ, czas=time.time(), **pola)
        if self.na_zdarzenie is None:
            self.zdarzenia.put(z)
            return
        try:
            self.na_zdarzenie(z)
        except Exception:  # noqa: BLE001 - blad odbiorcy nie zatrzymuje silnika
            LOG.exception("silnik: blad funkcji odbierajacej zdarzenie %s", typ)

    def _petla(self) -> None:
        while not self._stop.is_set():
            try:
                self._krok()
            except Exception:  # noqa: BLE001 - nadzorca nie moze sie skonczyc
                LOG.exception("silnik: blad nadzorcy")
                time.sleep(0.2)

    def _uruchom_proces(self) -> None:
        """Uruchamia proces roboczy: najwyzej ``proby_uruchomienia`` prob ``Process.start()`` z limitem ``limit_uruchomienia_s``
        kazda (E3-A2p). Wszystkie nieudane = ``_nieudany_start_procesu`` (blad ``start`` pierwszego zadania z kolejki, kolejna
        proba dopiero przy nastepnym zadaniu - jak po procesie, ktory nie zglosil gotowosci)."""
        powody = []
        for proba in range(1, self.proby_uruchomienia + 1):
            if proba > 1 and self._stop.wait(ODSTEP_PROB_URUCHOMIENIA_S):
                return
            if self._stop.is_set():
                return
            powod = self._proba_uruchomienia(proba)
            if powod is None:
                return
            powody.append(powod)
        if self._stop.is_set():
            return
        n = self.proby_uruchomienia
        self._nieudany_start_procesu(f"proces silnika nie wystartowal: {n} {'proba' if n == 1 else 'proby' if n < 5 else 'prob'} uruchomienia nieudane "
                                     f"(ostatnia: {powody[-1][0]})",
                                     "\n".join(f"proba {i}: {a}" + (f" ({b})" if b else "") for i, (a, b) in enumerate(powody, 1)))

    def _start_z_limitem(self, p) -> tuple | None:
        """``p.start()`` w watku pomocniczym ``silnik-start``; nadzorca czeka najwyzej ``limit_uruchomienia_s`` (krocej po
        ``stop()``). None = proces uruchomiony; inaczej (przyczyna, opis potomka) nieudanej proby (zawieszony start jest
        przerywany: ``_przerwij_start``). Start, ktory skonczy sie dopiero po przerwaniu proby, zabija swoj proces sam."""
        stan: dict = {}
        zamek = threading.Lock()
        try:
            flagi = FLAGI_PROCESU_ROBOCZEGO if FLAGI_PROCESU_ROBOCZEGO and _flagi_startu_dostepne() else 0
        except Exception as e:  # noqa: BLE001 - bez flag proces roboczy startuje jak przed E3-A2p (konsola procesu okna)
            flagi = 0
            LOG.warning("silnik: flag CreateProcess dla procesu roboczego nie da sie ustawic (%s: %s)", type(e).__name__, e)

        def cel() -> None:
            _FLAGI_STARTU.flagi = flagi  # tylko ten watek: wlasna konsola procesu roboczego (CREATE_NO_WINDOW)
            try:
                p.start()
            except BaseException as e:  # noqa: BLE001 - takze blad CreateProcess i zapis anulowany przez _przerwij_start
                with zamek:
                    stan["blad"] = f"{type(e).__name__}: {e}"  # sam tekst: wyjatek trzymalby ramki z obiektem Popen
                return
            with zamek:
                porzucony = stan.get("porzucony", False)
                stan["uruchomiony"] = not porzucony
            if porzucony:
                _zamknij_porzucony(p)

        w = threading.Thread(target=cel, name="silnik-start", daemon=True)
        t0 = time.monotonic()
        w.start()
        kod_potomka, nastepne_sprawdzenie = None, t0 + SPRAWDZ_POTOMKA_S
        while w.is_alive() and not self._stop.is_set() and time.monotonic() - t0 < self.limit_uruchomienia_s:
            w.join(0.05)
            if w.is_alive() and time.monotonic() >= nastepne_sprawdzenie:
                nastepne_sprawdzenie = time.monotonic() + SPRAWDZ_POTOMKA_S
                kod_potomka = _kod_martwego_potomka(w)
                if kod_potomka is not None:
                    break
        if not w.is_alive():
            return None if stan.get("uruchomiony") else (f"Process.start() zakonczyl sie bledem {stan.get('blad', '?')}", "")
        if self._stop.is_set():
            przyczyna = "przerwany przez stop()"
        elif kod_potomka is not None:
            przyczyna = (f"proces potomny zakonczyl sie przed odczytem danych startowych (kod wyjscia 0x{kod_potomka:08X}"
                         f"{' - blad inicjalizacji DLL' if kod_potomka == 0xC0000142 else ''}), Process.start() czekal {time.monotonic() - t0:.1f} s")
        else:
            przyczyna = f"Process.start() nie zakonczyl sie w {self.limit_uruchomienia_s:g} s"
        opis = _przerwij_start(w, CZEKAJ_NA_PRZERWANIE_S)
        with zamek:
            uruchomiony = stan.get("uruchomiony", False)
            stan["porzucony"] = True
        if uruchomiony:  # start skonczyl sie w trakcie przerywania (potomek moze juz byc zabity): proces nie zostaje
            _zamknij_porzucony(p)
        return przyczyna, opis

    def _proba_uruchomienia(self, proba: int) -> tuple | None:
        """Jedna proba uruchomienia procesu roboczego. None = proces dziala (albo ``stop()`` w trakcie - wtedy zabity);
        inaczej (przyczyna, szczegoly) nieudanej proby - lacze zamkniete po obu stronach, proces potomny zabity."""
        rodzic, dziecko = self._ctx.Pipe()
        p = self._ctx.Process(target=_robotnik, name="silnik-analiza", daemon=True,
                              args=(dziecko, self.ust, self.plik_ustawien, self.funkcja, self.pul_w_pamieci, self.plik_logu, self.pamiec_linii,
                                    self.limit_zadania_s, self.katalog_roboczy, self.czekaj_na_plik_s))
        t0 = time.monotonic()
        powod = self._start_z_limitem(p)
        if powod is not None:
            for koniec in (rodzic, dziecko):
                try:
                    koniec.close()
                except OSError:
                    pass
            if self._stop.is_set():
                return None
            self._przerwane_uruchomienia += 1
            LOG.warning("silnik: proba %d z %d uruchomienia procesu roboczego nieudana: %s%s", proba, self.proby_uruchomienia, powod[0],
                        f" ({powod[1]})" if powod[1] else "")
            return powod
        dziecko.close()  # koniec lacza po stronie procesu roboczego zostaje tylko u niego: jego smierc = koniec danych
        try:  # D-N5: system konczy proces roboczy razem z procesem okna (takze, gdy Straznik nie dostaje czasu - kod natywny z GIL)
            w_obiekcie = _dolacz_do_obiektu_zadania(p.pid)
        except Exception as e:  # noqa: BLE001 - bez obiektu zadania zostaje Straznik (jak do rundy 3)
            w_obiekcie = False
            LOG.warning("silnik: procesu roboczego nie dalo sie wlozyc do obiektu zadania Windows (%s: %s) - zostaje straznik w procesie",
                        type(e).__name__, e)
        with self._zamek:
            if not self._po_stopie:
                self._proces, self._lacze, self._gotowy, self._start_procesu = p, rodzic, False, t0  # limit_startu_s liczony od Process.start()
                self._w_obiekcie_zadania = bool(w_obiekcie)
                self._starty += 1
                return None
        p.kill()  # D-N3: stop() ruszyl w trakcie startu procesu (wolny p.start()) - proces nie moze zostac bez nadzoru
        p.join(5.0)
        rodzic.close()
        return None

    def _zamknij_proces(self, grzecznie: bool = False) -> int | None:
        with self._zamek:  # stop() i nadzorca (po przekroczeniu czasu join) nie zamykaja tego samego procesu dwa razy
            p, lacze = self._proces, self._lacze
            self._proces, self._lacze, self._gotowy = None, None, False
        kod = None
        if p is not None:
            if grzecznie and p.is_alive() and lacze is not None:
                try:
                    lacze.send(("koniec",))
                    p.join(2.0)
                except OSError:
                    pass
            if p.is_alive():
                p.kill()
            p.join(5.0)
            kod = p.exitcode
            try:
                p.close()
            except ValueError:
                pass
        if lacze is not None:
            try:
                lacze.close()
            except OSError:
                pass
        return kod

    def _krok(self) -> None:
        if self._proces is None:
            if self._nieudany_start is not None and not self._kolejka:
                time.sleep(0.05)  # po nieudanym starcie kolejna proba dopiero, gdy jest dla kogo
                return
            self._uruchom_proces()
        p, lacze = self._proces, self._lacze
        if p is None or lacze is None:
            return  # stop() w trakcie startu procesu albo zamknal proces
        try:
            if lacze.poll(OKRES_S):
                self._odbierz(lacze.recv())
                self._sprawdz_limit()  # D4 (a): zadanie, ktore stale przysyla postep, tez ma limit czasu
                return
        except (EOFError, OSError):
            self._po_smierci_procesu()
            return
        teraz = time.monotonic()
        if not p.is_alive():
            self._po_smierci_procesu()
        elif self._biezace is not None:
            self._sprawdz_limit()
        elif not self._gotowy:
            if teraz - self._start_procesu > self.limit_startu_s:
                self._zamknij_proces()
                self._nieudany_start_procesu(f"proces silnika nie zglosil gotowosci w {self.limit_startu_s:.0f} s", "")
        else:
            with self._zamek:  # D3: zdjecie z kolejki i "w toku" razem - czekaj_na_pusta_kolejke nie widzi luki
                if self._po_stopie:
                    return  # D-N4: po rozpoczeciu stop() kolejka nalezy do listy niezakonczonych
                zadanie = self._kolejka.popleft() if self._kolejka else None
                if zadanie is not None:
                    self._biezace, self._biezace_od = zadanie, teraz
            if zadanie is not None:
                self._zglos("start", zadanie_id=zadanie.zadanie_id, zadanie=zadanie)
                try:
                    lacze.send(("zadanie", zadanie))
                except OSError:
                    self._po_smierci_procesu()

    def _zakoncz(self, zadanie: ZadanieAnalizy, typ: str, **pola) -> None:
        """Zdarzenie koncowe zadania (``wynik`` / ``blad``) - jedyna droga (D-N3). Po rozpoczeciu ``stop()`` zdarzenie jest
        odrzucane: zadanie zostaje w ``_biezace`` i trafia na liste niezakonczonych. Zadanie w trakcie przekazywania
        (``_zglaszane``) ``stop()`` pomija - dostaje to zdarzenie. ``_biezace`` = None dopiero po zgloszeniu (D3)."""
        with self._zamek:
            if self._po_stopie:
                LOG.info("silnik: zdarzenie %s zadania %s po rozpoczeciu stop() odrzucone - zadanie jest na liscie niezakonczonych",
                         typ, zadanie.zadanie_id)
                return
            self._zglaszane = zadanie
        try:
            self._zglos(typ, zadanie_id=zadanie.zadanie_id, zadanie=zadanie, **pola)
        finally:
            with self._zamek:
                self._zglaszane = None
                if self._biezace is zadanie:
                    self._biezace = None

    def _sprawdz_limit(self) -> None:
        zadanie = self._biezace
        if zadanie is None or self._proces is None:
            return
        czas = time.monotonic() - self._biezace_od
        if czas <= self.limit_zadania_s:
            return
        self._zamknij_proces()
        self._zakoncz(zadanie, "blad", rodzaj="limit_czasu", czas_s=round(czas, 3),
                      blad=f"analiza trwala dluzej niz {self.limit_zadania_s:.0f} s i zostala przerwana")

    def _odbierz(self, w: tuple) -> None:
        rodzaj = w[0]
        if rodzaj == "gotowy":
            self._gotowy, self._nieudany_start = True, None
            self._zglos("gotowy", czas_s=round(time.monotonic() - self._start_procesu, 3))
            return
        if rodzaj == "blad_startu":
            self._zamknij_proces()
            self._nieudany_start_procesu(f"proces silnika nie wystartowal: {w[1]}", w[2])
            return
        zadanie = self._biezace
        if zadanie is None or w[1] != zadanie.zadanie_id:
            return  # spozniona wiadomosc zadania juz zamknietego
        if rodzaj == "postep":
            if not self._po_stopie:  # zadanie z listy stop() nie dostaje juz zdarzen
                self._zglos("postep", zadanie_id=zadanie.zadanie_id, zadanie=zadanie, etap=w[2], udzial=w[3])
            return
        czas_s = round(time.monotonic() - self._biezace_od, 3)
        if rodzaj == "wynik":
            self._zakoncz(zadanie, "wynik", wynik=w[2], pliki=w[3], czas_s=czas_s)
        elif rodzaj == "blad":
            self._zakoncz(zadanie, "blad", rodzaj=w[4] if len(w) > 4 else "analiza", blad=w[2], szczegoly=w[3], czas_s=czas_s)

    def _po_smierci_procesu(self) -> None:
        """Proces roboczy zniknal (zabity, awaria biblioteki): blad biezacego zadania; nowy proces ruszy w nastepnym kroku."""
        gotowy, zadanie, od = self._gotowy, self._biezace, self._biezace_od
        kod = self._zamknij_proces()
        if zadanie is not None:
            self._zakoncz(zadanie, "blad", rodzaj="proces", czas_s=round(time.monotonic() - od, 3),
                          blad=f"proces silnika zakonczyl sie w trakcie analizy (kod wyjscia {kod}); analiza przerwana")
        elif not gotowy:
            self._nieudany_start_procesu(f"proces silnika zakonczyl sie przy starcie (kod wyjscia {kod})", "")

    def _nieudany_start_procesu(self, tekst: str, szczegoly: str) -> None:
        """Proces nie wystartowal: blad dostaje pierwsze zadanie z kolejki (kazde zadanie = najwyzej jedna nieudana proba)."""
        LOG.error("%s", tekst)
        self._nieudany_start = (tekst, szczegoly)
        with self._zamek:
            if self._po_stopie or not self._kolejka:
                return  # po rozpoczeciu stop() kolejka nalezy do listy niezakonczonych
            zadanie = self._kolejka.popleft()
            self._zglaszane = zadanie
        try:
            self._zglos("blad", zadanie_id=zadanie.zadanie_id, zadanie=zadanie, rodzaj="start", blad=tekst, szczegoly=szczegoly, czas_s=0.0)
        finally:
            with self._zamek:
                self._zglaszane = None


# ----------------------------------------------------------------------------
# lacznik z petla Qt (PySide6 importowane dopiero tutaj)
# ----------------------------------------------------------------------------
_KLASA_LACZNIKA = None


def lacznik_qt(silnik: Silnik, okres_ms: int = 30, rodzic=None):
    """Obiekt Qt z sygnalami silnika emitowanymi w watku okna: ``gotowy()``, ``start(int)``, ``postep(int, str, float)``,
    ``wynik(int, object)`` (slownik wyniku), ``blad(int, str, str)`` (numer, rodzaj, komunikat) i ``zdarzenie(object)``
    (kazde ``ZdarzenieSilnika``). Zegar Qt co ``okres_ms`` oproznia kolejke ``silnik.zdarzenia`` - silnik nie moze miec
    wtedy wlasnego ``na_zdarzenie``. ``zatrzymaj()`` wylacza zegar."""
    global _KLASA_LACZNIKA
    if silnik.na_zdarzenie is not None:
        raise ValueError("lacznik_qt: silnik ma juz funkcje na_zdarzenie")
    if _KLASA_LACZNIKA is None:
        from PySide6.QtCore import QObject, QTimer, Signal

        class LacznikQt(QObject):
            gotowy = Signal()
            start = Signal(int)
            postep = Signal(int, str, float)
            wynik = Signal(int, object)
            blad = Signal(int, str, str)
            zdarzenie = Signal(object)

            def __init__(self, silnik_: Silnik, okres_ms_: int, rodzic_=None):
                super().__init__(rodzic_)
                self.silnik = silnik_
                self._zegar = QTimer(self)
                self._zegar.setInterval(okres_ms_)
                self._zegar.timeout.connect(self.oproznij)
                self._zegar.start()

            def oproznij(self) -> None:
                for _ in range(200):  # najwyzej tyle zdarzen na jedno tykniecie - petla okna nie czeka
                    try:
                        z = self.silnik.zdarzenia.get_nowait()
                    except queue.Empty:
                        return
                    self.zdarzenie.emit(z)
                    if z.typ == "gotowy":
                        self.gotowy.emit()
                    elif z.typ == "start":
                        self.start.emit(z.zadanie_id)
                    elif z.typ == "postep":
                        self.postep.emit(z.zadanie_id, z.etap, z.udzial)
                    elif z.typ == "wynik":
                        self.wynik.emit(z.zadanie_id, z.wynik)
                    elif z.typ == "blad":
                        self.blad.emit(z.zadanie_id, z.rodzaj, z.blad)

            def zatrzymaj(self) -> None:
                self._zegar.stop()

        _KLASA_LACZNIKA = LacznikQt
    return _KLASA_LACZNIKA(silnik, okres_ms, rodzic)
