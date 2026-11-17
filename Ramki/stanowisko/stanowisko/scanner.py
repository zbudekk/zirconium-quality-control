"""scanner - obserwacja folderu eksportu skanera: nowy plik STL -> zdarzenie "nowy skan" (paczka E3-A2).

Co robi: patrzy na folder (biblioteka ``watchdog`` + okresowy przeglad jako siatka bezpieczenstwa), dla kazdego pliku
pasujacego do wzorca czeka na koniec zapisu, sprawdza go (binarny STL: rozmiar = 84 + 50 x liczba trojkatow) i zglasza
``ZdarzenieSkanu`` (plik, sha16, rozmiar, liczba trojkatow, czas pliku). Plik zly (pusty, uciety, nie-STL, tekstowy,
z niezgodnym naglowkiem, za maly) nie daje zdarzenia, tylko ``Odrzucenie`` z powodem. Modul nie laduje numpy, trimesh,
Open3D ani Qt - dziala w procesie okna w zwyklym watku Pythona.

Koniec zapisu = wszystkie warunki naraz:
  1. rozmiar i czas pliku nie zmienily sie przez ``stabilizacja_ms``,
  2. rozmiar zgadza sie z liczba trojkatow w naglowku (plik w trakcie zapisu prawie nigdy tego nie spelnia),
  3. zaden program nie trzyma pliku otwartego do zapisu (Windows; ``dzien_skanera_rdzen.ktos_pisze``),
  4. po policzeniu skrotu rozmiar i czas sa nadal te same.
Plik stabilny, ale zly, jest odrzucany dopiero po ``odrzuc_po_s`` bez zmian (moze byc jeszcze dopisywany); odrzucenie
nie jest ostateczne - gdy plik sie zmieni, jest oceniany od nowa.

Plik, ktorego nie da sie otworzyc (inny program trzyma go bez zgody na odczyt: zapis przez ``File.Create`` w .NET,
podglad, antywirus, kopia zapasowa), jest "zajety" - to stan przejsciowy, nie odrzucenie. Obserwator ponawia proby coraz
rzadziej (najrzadziej co ``ODSTEP_ZAJETY_MAX_S``) BEZ limitu liczby prob, a po ``informuj_po_s`` zglasza ``Oczekiwanie``
("czeka na zwolnienie pliku"; powtarzane co ``informuj_co_s``). Po zwolnieniu plik przechodzi zwykla ocene i daje
zdarzenie. Tak samo (bez rosnacego odstepu) plik kompletny, ktory inny program trzyma jeszcze otwarty do zapisu.

Pliki zastane = obecne w folderze przy PIERWSZYM udanym przegladzie (takze gdy folder pojawil sie po starcie albo
podfolderu nie dalo sie przy starcie odczytac - wtedy przy pierwszym udanym odczycie tego podfolderu), o czasie
modyfikacji NIE pozniejszym niz start obserwatora. Plik z czasem pozniejszym niz start jest zawsze nowy, niezaleznie od
tego, kiedy folder stal sie widoczny (D-N1: nowy skan w folderze zalozonym po starcie nie przepada bez nadrabiania).
Pliki zastane nie sa nowymi skanami, chyba ze wlaczone jest nadrabianie po restarcie: ``zglos_zastane_od`` (pliki
nowsze niz podany czas) i / albo ``znane(sciezka, rozmiar, mtime_ns)`` (funkcja aplikacji: czy plik byl juz przyjety;
kontrakt w opisie ``Scanner``; gotowa wersja z rekordow bazy A1: ``ZnanePliki``) - pliki zastane, ktore przejda te
warunki, ida zwykla droga i daja zdarzenie z ``zastany=True``; skrot liczony tylko dla nich. ``zglos_zastane=True`` =
wszystkie pliki zastane. Chwilowy blad listowania folderu albo podfolderu nie kasuje wiedzy o znanych plikach: plik jest
zapominany dopiero, gdy naprawde zniknal (sprawdzenie ``os.stat`` albo zdarzenie watchdog).

Nie zakladamy nazw ani struktury plikow prawdziwego skanera: wzorzec nazwy, podfoldery i wszystkie czasy sa parametrami
konstruktora (podpiecie do ``ustawienia.toml`` robi paczka A3; proponowane klucze ``[scanner]``: ``stabilizacja_ms``,
``min_rozmiar_mb``, ``min_trojkatow``, ``wzorzec_pliku``).

Akcja "start skanu" (decyzja DW5: Spacje lapie nasze okno, ktore aktywuje okno skanera) jest tu tylko interfejsem:
``Scanner.start_skanu()`` wywoluje podana funkcje; domyslnie ``AtrapaStartuSkanu``, ktora nic nie klika.

Uzyte ponownie z okna "Dzien skanera" (``dzien_skanera_rdzen``, bez zmian w tamtym pliku): ``ktos_pisze``,
``otworz_zrodlo`` (odczyt z pelnym wspoldzieleniem - nie blokuje programu skanera), ``pliki_w_folderze``.

Uzycie:
    sc = Scanner(folder, na_skan=funkcja, na_odrzucenie=funkcja2, na_oczekiwanie=funkcja3)   # wolane w watku obserwatora
    sc.start() ... sc.stop()
Bez funkcji zwrotnych zdarzenia trafiaja do kolejki ``sc.zdarzenia``.
"""
from __future__ import annotations

import collections
import dataclasses
import datetime
import fnmatch
import hashlib
import logging
import os
import queue
import stat
import threading
import time
from pathlib import Path

from .dzien_skanera_rdzen import ktos_pisze, otworz_zrodlo, pliki_w_folderze

LOG = logging.getLogger(__name__)

# wartosci domyslne parametrow konstruktora (jedno miejsce; A3 podepnie je do ustawien)
STABILIZACJA_MS = 300  # tyle bez zmiany rozmiaru i czasu pliku = zapis sie skonczyl (lacznie z warunkami 2-4 z opisu modulu)
MIN_ROZMIAR_MB = 0.0  # 0 = bez progu rozmiaru
MIN_TROJKATOW = 1  # plik bez trojkatow nie jest skanem; prog dla prawdziwego skanera ustali B2
WZORZEC_PLIKU = "*.stl"  # wzorzec NAZWY pliku (fnmatch, bez rozrozniania wielkosci liter)
ODRZUC_PO_S = 5.0  # plik zly i niezmieniany przez tyle sekund = wpis "odrzucony" z powodem
OKRES_S = 0.05  # co ile watek oglada pliki, na ktore czeka
PRZEGLAD_S = 2.0  # co ile caly folder jest przegladany niezaleznie od watchdog (zgubione powiadomienia, dysk sieciowy)
BLOK_ODCZYTU = 4 * 1024 * 1024
LIMIT_DZIENNIKA = 1000  # tyle ostatnich odrzucen pamieta obserwator
ODSTEP_ZAJETY_MAX_S = 2.0  # plik, ktorego nie da sie otworzyc: proby co okres_s, potem 2x, 4x ... rzadziej, najrzadziej co tyle
ODSTEP_PISZE_MAX_S = 0.25  # plik kompletny, ale trzymany jeszcze do zapisu: proby najrzadziej co tyle (opoznienie S1)
INFORMUJ_PO_S = 10.0  # plik zajety dluzej niz tyle = ``Oczekiwanie`` ("czeka na zwolnienie pliku")
INFORMUJ_CO_S = 60.0  # kolejne ``Oczekiwanie`` o tym samym pliku najwczesniej po tylu sekundach
_EPS = 1e-6  # porownania czasow (zegar testow skacze o ulamki sekundy)

POWODY = {
    "poza_wzorcem": "nazwa pliku nie pasuje do wzorca skanow",
    "pusty": "plik pusty (0 bajtow)",
    "za_krotki": "plik krotszy niz naglowek binarnego STL (84 bajty) - nie-STL albo uciety",
    "stl_tekstowy": "STL tekstowy (ASCII) - program przyjmuje tylko binarny STL",
    "rozmiar_niezgodny": "rozmiar pliku nie zgadza sie z liczba trojkatow w naglowku (plik uciety, uszkodzony albo nie-STL)",
    "za_malo_trojkatow": "za malo trojkatow",
    "za_maly": "plik mniejszy niz prog rozmiaru",
    # wynik ``sprawdz_stl`` dla pliku, ktorego nie da sie otworzyc; obserwator NIE robi z tego odrzucenia (plik "zajety", B1)
    "blad_odczytu": "pliku nie da sie otworzyc (inny program trzyma go bez zgody na odczyt albo brak uprawnien)",
}


@dataclasses.dataclass(frozen=True)
class ZdarzenieSkanu:
    """Nowy skan w folderze (kontrakt z planu etapu 3, sekcja 3.8). Obiekt jest prosty - przechodzi do procesu silnika."""

    plik: Path
    sha16: str  # pierwsze 16 znakow SHA-256 zawartosci (ten sam skrot, co synth.skrot_pliku)
    rozmiar: int
    trojkaty: int
    czas_pliku: float  # czas modyfikacji pliku, sekundy od epoki
    mtime_ns: int
    czas_zdarzenia: float  # time.time() w chwili zgloszenia
    nr: int  # kolejny numer zdarzenia tego obserwatora (od 1)
    ponowny: bool = False  # ta sama sciezka byla juz zgloszona (plik zapisany ponownie pod ta sama nazwa)
    duplikat: bool = False  # ta sama zawartosc byla juz zgloszona pod INNA nazwa
    duplikat_z: str | None = None  # sciezka pierwszego pliku o tej zawartosci
    zastany: bool = False  # plik byl w folderze przy starcie i zostal zgloszony przez nadrabianie (zglos_zastane*, znane)


@dataclasses.dataclass(frozen=True)
class Oczekiwanie:
    """Plik zajety dluzej niz ``informuj_po_s``: nie da sie go otworzyc (inny program trzyma go bez zgody na odczyt) albo
    jest kompletny, ale inny program trzyma go jeszcze do zapisu. Obserwator czeka bez limitu - to informacja dla technika
    ("czeka na zwolnienie pliku"), nie odrzucenie; zdarzenie przyjdzie po zwolnieniu pliku."""

    plik: Path
    od_s: float  # od ilu sekund plik jest zajety
    opis: str
    czas: float  # time.time()


@dataclasses.dataclass(frozen=True)
class Odrzucenie:
    """Plik, ktory nie dal zdarzenia - wpis z powodem (kod z ``POWODY``) i opisem dla czlowieka."""

    plik: Path
    powod: str
    opis: str
    rozmiar: int | None
    czas: float


@dataclasses.dataclass(frozen=True)
class WynikWalidacji:
    trojkaty: int | None  # liczba trojkatow z naglowka (None, gdy nie da sie jej odczytac)
    powod: str | None  # None = plik dobry
    opis: str
    rozmiar: int | None


def sprawdz_stl(plik, min_trojkatow: int = MIN_TROJKATOW, min_rozmiar_mb: float = MIN_ROZMIAR_MB) -> WynikWalidacji:
    """Walidacja pliku skanu bez wczytywania siatki: binarny STL ma rozmiar 84 + 50 x liczba trojkatow z naglowka."""
    try:
        rozmiar = os.stat(plik).st_size
        with otworz_zrodlo(plik) as f:
            naglowek = f.read(84)
            poczatek = naglowek + f.read(428) if rozmiar > 84 else naglowek
    except OSError as e:
        return WynikWalidacji(None, "blad_odczytu", f"{POWODY['blad_odczytu']}: {type(e).__name__}", None)
    if rozmiar == 0:
        return WynikWalidacji(None, "pusty", POWODY["pusty"], 0)
    if len(naglowek) < 84:
        return WynikWalidacji(None, "za_krotki", f"{POWODY['za_krotki']}; plik ma {rozmiar} B", rozmiar)
    trojkaty = int.from_bytes(naglowek[80:84], "little")
    oczekiwany = 84 + 50 * trojkaty
    if oczekiwany != rozmiar:
        if naglowek[:5].lower() == b"solid" and _wyglada_na_tekst(poczatek):
            return WynikWalidacji(None, "stl_tekstowy", POWODY["stl_tekstowy"], rozmiar)
        co = "plik uciety" if rozmiar < oczekiwany else "plik dluzszy niz zapowiada naglowek"
        return WynikWalidacji(trojkaty, "rozmiar_niezgodny", f"{co}: naglowek zapowiada {trojkaty} trojkatow ({oczekiwany} B), plik ma {rozmiar} B", rozmiar)
    if trojkaty < min_trojkatow:
        return WynikWalidacji(trojkaty, "za_malo_trojkatow", f"{POWODY['za_malo_trojkatow']}: {trojkaty}, wymagane co najmniej {min_trojkatow}", rozmiar)
    if rozmiar < min_rozmiar_mb * 1024 * 1024:
        return WynikWalidacji(trojkaty, "za_maly", f"{POWODY['za_maly']}: {rozmiar} B, wymagane co najmniej {min_rozmiar_mb} MB", rozmiar)
    return WynikWalidacji(trojkaty, None, "", rozmiar)


def _wyglada_na_tekst(dane: bytes) -> bool:
    return bool(dane) and all(b in (9, 10, 13) or 32 <= b < 127 for b in dane)


def skrot16_pliku(plik) -> str:
    """Pierwsze 16 znakow SHA-256 zawartosci; plik czytany z pelnym wspoldzieleniem (nie blokuje programu skanera)."""
    h = hashlib.sha256()
    with otworz_zrodlo(plik) as f:
        while True:
            blok = f.read(BLOK_ODCZYTU)
            if not blok:
                break
            h.update(blok)
    return h.hexdigest()[:16]


class AtrapaStartuSkanu:
    """Atrapa akcji "start skanu": niczego nie klika, tylko zapisuje czasy wywolan (``wywolania``). Prawdziwa akcja
    (aktywuj okno programu skanera i nacisnij Spacje) powstanie po pierwszych probach na skanerze (paczka B2)."""

    def __init__(self):
        self.wywolania: list[float] = []

    def __call__(self) -> bool:
        self.wywolania.append(time.time())
        return True


def _klucz(sciezka) -> str:
    return os.path.normcase(os.path.abspath(str(sciezka)))


def czas_pliku_iso(mtime_ns: int) -> str:
    """Czas pliku w formacie bazy A1 (``skany.czas_pliku``, ``session._czas_iso`` z ``ZdarzenieSkanu.czas_pliku``): czas
    LOKALNY ISO bez strefy, uciety do sekund, np. ``2026-11-17T18:05:03``. Liczony z tej samej liczby co ``czas_pliku``
    zdarzenia (``mtime_ns / 1e9``), wiec daje dokladnie ten sam napis, ktory A1 zapisala dla tego pliku."""
    return datetime.datetime.fromtimestamp(int(mtime_ns) / 1e9).replace(microsecond=0, tzinfo=None).isoformat()


def klucz_znanego(sciezka, rozmiar: int, czas_iso: str) -> tuple:
    """Klucz porownania pliku z rekordem bazy: (sciezka po ``normcase(abspath)``, rozmiar w bajtach, czas pliku w formacie
    ``czas_pliku_iso``). Ta sama sciezka zapisana inaczej (wielkosc liter na Windows, ``..``, ``/``) daje ten sam klucz."""
    return _klucz(sciezka), int(rozmiar), str(czas_iso)


class ZnanePliki:
    """Gotowa funkcja ``znane`` dla aplikacji (D-N2): zbior plikow PRZYJETYCH skanow wczytany PRZED ``Scanner.start()``.

    ``wpisy`` - krotki (``plik``, ``rozmiar``, ``czas_pliku``) jak w tabeli ``skany`` bazy A1 (``czas_pliku`` w formacie
    ``czas_pliku_iso``); wpisy bez rozmiaru albo czasu sa pomijane. Wywolanie ``znane(sciezka, rozmiar, mtime_ns)`` porownuje
    sciezke (znormalizowana), rozmiar i czas pliku z dokladnoscia do sekundy. Zbior jest niezmienny - wywolanie jest
    bezpieczne z kazdego watku i nie dotyka bazy (polaczenia ``sqlite3`` nie wolno uzywac poza watkiem, ktory je otworzyl).
    Wystarczy stan z chwili startu: pliki zapisane po starcie obserwatora sa nowe bez pytania o ``znane`` (D-N1)."""

    def __init__(self, wpisy=()):
        self._klucze = frozenset(klucz_znanego(p, r, c) for p, r, c in wpisy if p and r is not None and c)

    def __len__(self) -> int:
        return len(self._klucze)

    def __call__(self, sciezka, rozmiar: int, mtime_ns: int) -> bool:
        return klucz_znanego(sciezka, rozmiar, czas_pliku_iso(mtime_ns)) in self._klucze


def _pod(k: str, zbior) -> bool:
    """Czy klucz sciezki ``k`` jest jednym z kluczy ``zbior`` albo lezy pod ktoryms z nich."""
    return any(k == p or k.startswith(p.rstrip("\\/") + os.sep) for p in zbior)


def _podpis(sciezka) -> tuple | None:
    """(rozmiar, mtime_ns) pliku albo None, gdy nie da sie go odczytac."""
    try:
        st = os.stat(sciezka)
    except OSError:
        return None
    return st.st_size, st.st_mtime_ns


def _identyfikator(folder):
    """(urzadzenie, numer pliku) folderu - folder usuniety i utworzony od nowa ma inny numer; None, gdy go nie ma."""
    try:
        st = os.stat(folder)
    except OSError:
        return None
    return st.st_dev, st.st_ino


class Scanner:
    """Obserwator folderu eksportu skanera. Parametry - patrz stale na gorze modulu i opis w ``opisy_modulow/scanner.md``.

    ``obserwator``: ``"watchdog"`` (domyslnie; gdy biblioteki nie da sie uzyc - samo odpytywanie) albo ``"odpytywanie"``
    (tylko przeglad folderu co ``przeglad_s``, np. dla dysku sieciowego). Pliki zastane (obecne przy pierwszym udanym
    przegladzie folderu, z czasem modyfikacji nie pozniejszym niz start obserwatora) nie sa nowymi skanami, chyba ze:
    ``zglos_zastane`` (wszystkie), ``zglos_zastane_od`` (czas w sekundach od epoki: pliki o czasie modyfikacji POZNIEJSZYM)
    albo ``znane``. Podane razem dzialaja razem (nowszy ORAZ nieznany). ``na_oczekiwanie`` dostaje ``Oczekiwanie`` (plik
    zajety dluzej niz ``informuj_po_s``). ``zegar`` - do testow.

    Kontrakt ``znane(sciezka: Path, rozmiar: int, mtime_ns: int) -> bool`` (D-N2):
    * WATEK: wolana wylacznie w watku obserwatora (``scanner``; w testach - w watku, ktory sam wola ``obieg()``), po jednym
      wywolaniu naraz, nigdy w watku wolajacym ``start()``. Nie moze uzywac obiektow przywiazanych do innego watku
      (polaczenie ``sqlite3`` otwarte w watku okna rzuca ``ProgrammingError``) - najprosciej ``ZnanePliki`` (zbior wczytany
      z bazy przed ``start()``) albo wlasne polaczenie otwierane w funkcji.
    * ARGUMENTY: ``sciezka`` = ``folder / sciezka wzgledna`` (jak ``ZdarzenieSkanu.plik``), ``rozmiar`` w bajtach,
      ``mtime_ns`` = czas modyfikacji jako LICZBA CALKOWITA nanosekund (``os.stat().st_mtime_ns``; ``ZdarzenieSkanu.czas_pliku``
      = ``mtime_ns / 1e9``). Baza A1 trzyma ``czas_pliku`` jako czas lokalny ISO uciety do sekund - porownanie przez
      ``czas_pliku_iso(mtime_ns)`` i ``klucz_znanego`` (sciezka znormalizowana, rozmiar, czas do sekundy); porownanie wprost
      z ``mtime_ns`` dawaloby zawsze "nieznany" (skrot calej historii folderu przy kazdym starcie, duplikaty do odsiania).
    * ZNACZENIE: True = dla tej sciezki, rozmiaru i czasu aplikacja ma zapisany wynik analizy (dowolny status), blad
      pokazany technikowi albo zadanie zapisane z ``Silnik.stop()`` (zleca je sama po starcie). Samo przyjete zdarzenie
      skanu bez wyniku = False (awaria miedzy zdarzeniem a wynikiem nie moze zgubic skanu).
    * Pytana raz na plik zastany (przy ustalaniu plikow zastanych), bez czytania pliku; wyjatek = plik nieznany (zgloszony
      z ``zastany=True``, aplikacja odsieje powtorke po ``sha16``). Pliki zapisane po starcie obserwatora sa nowe bez pytania.
    """

    def __init__(self, folder, na_skan=None, na_odrzucenie=None, *, na_oczekiwanie=None, wzorzec_pliku: str = WZORZEC_PLIKU,
                 rekurencyjnie: bool = True, stabilizacja_ms: float = STABILIZACJA_MS, min_rozmiar_mb: float = MIN_ROZMIAR_MB,
                 min_trojkatow: int = MIN_TROJKATOW, odrzuc_po_s: float = ODRZUC_PO_S, okres_s: float = OKRES_S, przeglad_s: float = PRZEGLAD_S,
                 zglos_zastane: bool = False, zglos_zastane_od: float | None = None, znane=None, informuj_po_s: float = INFORMUJ_PO_S,
                 informuj_co_s: float = INFORMUJ_CO_S, obserwator: str = "watchdog", start_skanu=None, zegar=time.monotonic):
        if obserwator not in ("watchdog", "odpytywanie"):
            raise ValueError(f"obserwator: {obserwator!r} (dozwolone: watchdog, odpytywanie)")
        self.folder = Path(folder)
        self.na_skan, self.na_odrzucenie, self.na_oczekiwanie = na_skan, na_odrzucenie, na_oczekiwanie
        self.wzorzec_pliku, self.rekurencyjnie = wzorzec_pliku, rekurencyjnie
        self.stabilizacja_s = stabilizacja_ms / 1000.0
        self.min_rozmiar_mb, self.min_trojkatow = min_rozmiar_mb, min_trojkatow
        self.odrzuc_po_s, self.okres_s, self.przeglad_s = odrzuc_po_s, okres_s, przeglad_s
        self.zglos_zastane, self.zglos_zastane_od, self.znane = zglos_zastane, zglos_zastane_od, znane
        self.informuj_po_s, self.informuj_co_s = informuj_po_s, informuj_co_s
        self.akcja_startu = start_skanu if start_skanu is not None else AtrapaStartuSkanu()
        self.zegar = zegar
        self.zdarzenia: queue.Queue = queue.Queue()  # ZdarzenieSkanu / Odrzucenie / Oczekiwanie, gdy nie podano funkcji zwrotnych
        self.odrzucone: collections.deque = collections.deque(maxlen=LIMIT_DZIENNIKA)
        self._tryb = obserwator
        self._watchdog = None
        self._ident_watchdog = None  # _identyfikator folderu, na ktory patrzy watchdog
        self._startow_watchdog = 0
        self._zamek_watchdog = threading.Lock()
        self._zmiany: collections.deque = collections.deque()  # (rodzaj, sciezka) z watku watchdog
        self._budzik = threading.Event()
        self._stop = threading.Event()
        self._watek: threading.Thread | None = None
        self._zamek_watku = threading.Lock()
        self._watek_konczy = False  # watek obserwatora zdecydowal o koncu (po stop())
        self._znane: dict[str, tuple] = {}  # klucz sciezki -> (rozmiar, mtime_ns) wersji juz rozstrzygnietej albo zastanej
        self._kandydaci: dict[str, dict] = {}
        self._pominiete: set[str] = set()  # pliki spoza wzorca, juz wpisane do dziennika (albo zastane)
        self._zgloszone: set[str] = set()  # sciezki, ktore daly juz zdarzenie
        self._skroty: dict[str, str] = {}  # sha16 -> sciezka pierwszego pliku o tej zawartosci
        self._poczatek_ustalony = False  # P3: pliki zastane ustalone (pierwszy udany przeglad folderu)
        self._niezbadane: set[str] = set()  # klucze katalogow / plikow, ktorych nie dalo sie odczytac przy ustalaniu zastanych
        self._start_ns: int | None = None  # D-N1: czas startu obserwatora (time.time_ns()); plik z pozniejszym czasem jest nowy
        self._do_nadrobienia: list = []  # D-N2: pliki zastane czekajace na decyzje nadrabiania (w watku obserwatora)
        self._nr = 0
        self._odrzucen = 0
        self._oczekiwan = 0
        self._ostatni_przeglad = -1e18
        self._folder_dostepny = False
        self._przygotowany = False

    # --- sterowanie
    def start(self) -> None:
        with self._zamek_watku:
            self._stop.clear()
            w = self._watek
            if w is not None and w.is_alive() and not self._watek_konczy:
                self._uruchom_watchdog()  # D11 (a): stop() nie doczekal sie konca watku - ten sam watek pracuje dalej
                return
            self._watek_konczy = False
            if self._start_ns is None:
                self._start_ns = time.time_ns()  # D-N1: przed pierwszym przegladem - plik zapisany w trakcie startu jest nowy
            self.przygotuj()  # pliki zastane ustalane tu (przed powrotem z start()); decyzje ``znane`` - w watku obserwatora
            self._uruchom_watchdog()  # po stop() i ponownym start() stan zostaje, watchdog rusza od nowa
            self._watek = threading.Thread(target=self._petla, name="scanner", daemon=True)
            self._watek.start()

    def stop(self, czekaj_s: float = 5.0) -> None:
        """Konczy obserwacje. Gdy watek nie skonczy sie w ``czekaj_s`` (np. liczy skrot duzego pliku na wolnym dysku), zostaje
        widoczny w ``dziala()``, niczego juz nie zglasza (plik, ktory ocenial, zostaje kandydatem), a ``start()`` nie
        uruchamia drugiego watku na tym samym stanie."""
        self._stop.set()
        self._budzik.set()
        w = self._watek
        if w is not None:
            w.join(czekaj_s)
            if not w.is_alive():
                self._watek = None
        self._zatrzymaj_watchdog()

    def dziala(self) -> bool:
        return self._watek is not None and self._watek.is_alive()

    def start_skanu(self) -> bool:
        """Akcja "start skanu" (DW5). Zwraca False, gdy akcja sie nie powiodla (wyjatek akcji tez = False)."""
        try:
            return bool(self.akcja_startu())
        except Exception as e:  # noqa: BLE001 - brak okna skanera nie moze wywrocic programu
            LOG.warning("start skanu nie powiodl sie: %s: %s", type(e).__name__, e)
            return False

    def stan(self) -> dict:
        """Liczniki do paska stanu okna. ``czeka`` - pliki oceniane (w tym ``zajete``: nie da sie ich otworzyc albo inny
        program trzyma je jeszcze do zapisu); ``oczekiwan`` - ile informacji ``Oczekiwanie`` wyslano."""
        kandydaci = list(self._kandydaci.values())
        return {"folder": str(self.folder), "folder_dostepny": self._folder_dostepny, "obserwator": "watchdog" if self._watchdog is not None else "odpytywanie",
                "startow_watchdog": self._startow_watchdog, "zdarzen": self._nr, "odrzucen": self._odrzucen, "oczekiwan": self._oczekiwan,
                "czeka": len(kandydaci), "zajete": sum(1 for k in kandydaci if k["zajety_od"] is not None), "dziala": self.dziala()}

    # --- stan poczatkowy i watchdog
    def przygotuj(self) -> None:
        """Stan poczatkowy: start watchdog i pliki zastane (ustalane przy PIERWSZYM udanym przegladzie folderu - tutaj albo
        pozniej, gdy folderu jeszcze nie ma). Wolane przez ``start()``; osobno tylko wtedy, gdy obiegi wywoluje test.
        Funkcji ``znane`` tu nie wola: pliki do nadrabiania czekaja na pierwszy ``obieg()`` (D-N2)."""
        if self._przygotowany:
            return
        self._przygotowany = True
        if self._start_ns is None:
            self._start_ns = time.time_ns()
        self._folder_dostepny = self.folder.is_dir()
        if self._folder_dostepny:
            self._uruchom_watchdog()
            self._ustal_zastane(self.zegar())

    def _ustal_zastane(self, teraz: float) -> bool:
        """P3: pierwszy udany przeglad folderu - jego pliki sa zastane (albo, przy nadrabianiu, kandydatami z ``zastany``).
        Katalogi i pliki, ktorych nie dalo sie odczytac, trafiaja do ``_niezbadane``: ich zawartosc tez bedzie "zastana"
        przy pierwszym udanym odczycie. False = nie udalo sie wylistowac samego folderu (sprobuje przy nastepnym przegladzie)."""
        niedostepne: list = []
        pliki = list(pliki_w_folderze(self.folder, niedostepne=niedostepne))
        nied = {_klucz(p) for p in niedostepne}
        if _klucz(self.folder) in nied:
            return False
        for rel, rozmiar, mtime_ns in pliki:
            self._zastany(rel, rozmiar, mtime_ns, teraz)
        self._niezbadane = nied
        self._poczatek_ustalony = True
        self._ostatni_przeglad = teraz
        return True

    def _zastany(self, rel: str, rozmiar: int, mtime_ns: int, teraz: float) -> None:
        if not self._w_zakresie(rel):
            return
        sciezka = self.folder / rel
        k = _klucz(sciezka)
        if k in self._kandydaci or k in self._znane:
            return
        if self._start_ns is not None and mtime_ns > self._start_ns:
            self._zglos_zmiane(sciezka, teraz)  # D-N1: zapisany po starcie obserwatora - nowy plik, nie zastany
        elif not self._pasuje(rel):
            self._pominiete.add(k)  # plik spoza wzorca zastany w folderze: bez wpisu w dzienniku
        else:
            self._znane[k] = (rozmiar, mtime_ns)
            if self._nadrabianie_wlaczone():
                self._do_nadrobienia.append((k, sciezka, rozmiar, mtime_ns))  # decyzja w watku obserwatora (D-N2)

    def _nadrabianie_wlaczone(self) -> bool:
        return bool(self.zglos_zastane or self.zglos_zastane_od is not None or self.znane is not None)

    def _nadrob(self, teraz: float) -> None:
        """P2 (a) / D-N2: pliki zastane czekajace na decyzje nadrabiania - wolane w ``obieg()``, czyli w watku obserwatora
        (funkcja ``znane`` nigdy nie jest wolana w watku okna). Plik zmieniony albo usuniety od ustalenia ocenia zwykla droga."""
        lista, self._do_nadrobienia = self._do_nadrobienia, []
        for k, sciezka, rozmiar, mtime_ns in lista:
            if self._znane.get(k) != (rozmiar, mtime_ns):
                continue
            if self._nadrabiaj(sciezka, rozmiar, mtime_ns):
                del self._znane[k]
                kand = self._kandydaci.get(k)
                if kand is not None:
                    kand["zastany"] = True  # powiadomienie watchdog zdazylo zrobic z niego kandydata
                else:
                    self._zglos_zmiane(sciezka, teraz, zastany=True)

    def _nadrabiaj(self, sciezka: Path, rozmiar: int, mtime_ns: int) -> bool:
        """P2 (a): czy plik zastany ma byc zgloszony (nadrabianie po restarcie). Bez liczenia skrotu."""
        if not self._nadrabianie_wlaczone():
            return False
        if self.zglos_zastane_od is not None and not mtime_ns / 1e9 > self.zglos_zastane_od:
            return False
        if self.znane is not None:
            try:
                if self.znane(sciezka, rozmiar, mtime_ns):
                    return False
            except Exception:  # noqa: BLE001 - lepiej zglosic skan drugi raz (aplikacja rozpozna sha16) niz go zgubic
                LOG.exception("scanner: blad funkcji znane - plik traktowany jak nieznany")
        return True

    def _uruchom_watchdog(self) -> None:
        with self._zamek_watchdog:
            self._uruchom_watchdog_bez_zamka()

    def _uruchom_watchdog_bez_zamka(self) -> None:
        if self._tryb != "watchdog" or self._watchdog is not None or not self.folder.is_dir():
            return
        try:
            from watchdog.events import FileSystemEventHandler
            from watchdog.observers import Observer
        except ImportError as e:
            LOG.warning("brak biblioteki watchdog (%s) - obserwacja folderu przez odpytywanie", e)
            self._tryb = "odpytywanie"
            return
        scanner = self

        class Odbiornik(FileSystemEventHandler):
            def on_any_event(self, event) -> None:  # watek watchdog: tylko odnotowanie i pobudka
                if event.is_directory:
                    if event.event_type in ("moved", "deleted"):
                        scanner._zmiany.append(("przeglad", ""))
                        scanner._budzik.set()
                    return
                if event.event_type in ("created", "modified", "closed"):
                    scanner._zmiany.append(("zmiana", os.fsdecode(event.src_path)))
                elif event.event_type == "moved":
                    scanner._zmiany.append(("usuniety", os.fsdecode(event.src_path)))
                    scanner._zmiany.append(("zmiana", os.fsdecode(event.dest_path)))
                elif event.event_type == "deleted":
                    scanner._zmiany.append(("usuniety", os.fsdecode(event.src_path)))
                else:
                    return
                scanner._budzik.set()

        try:
            obs = Observer()
            obs.schedule(Odbiornik(), str(self.folder), recursive=self.rekurencyjnie)
            obs.daemon = True
            obs.start()
        except Exception as e:  # noqa: BLE001 - np. folder zniknal miedzy sprawdzeniem a startem; zostaje przeglad okresowy
            LOG.warning("watchdog nie wystartowal (%s: %s) - na razie odpytywanie", type(e).__name__, e)
            return
        self._watchdog = obs
        self._ident_watchdog = _identyfikator(self.folder)
        self._startow_watchdog += 1

    def _zatrzymaj_watchdog(self) -> None:
        with self._zamek_watchdog:
            obs, self._watchdog = self._watchdog, None
        if obs is not None:
            try:
                obs.stop()
                obs.join(2.0)
            except Exception:  # noqa: BLE001
                pass

    def _sprawdz_watchdog(self) -> None:
        """D1: folder usuniety i utworzony od nowa miedzy dwoma przegladami - watchdog patrzy na folder, ktorego juz nie ma
        (jego watek konczy sie po usunieciu folderu albo numer folderu jest inny). Wtedy obserwator rusza od nowa."""
        obs = self._watchdog
        if obs is None:
            return
        try:
            emitery = list(obs.emitters)
            sprawny = obs.is_alive() and bool(emitery) and all(e.is_alive() for e in emitery)
        except Exception:  # noqa: BLE001 - inna wersja biblioteki: zostaje kontrola numeru folderu
            sprawny = True
        if sprawny and _identyfikator(self.folder) == self._ident_watchdog:
            return
        LOG.info("obserwator watchdog nie dziala albo folder %s utworzono od nowa - uruchamiam go ponownie", self.folder)
        self._zatrzymaj_watchdog()
        self._uruchom_watchdog()

    # --- watek
    def _petla(self) -> None:
        while True:
            with self._zamek_watku:
                if self._stop.is_set():
                    self._watek_konczy = True
                    return
            try:
                self.obieg()
            except Exception:  # noqa: BLE001 - zaden wyjatek nie konczy obserwacji
                LOG.exception("scanner: blad obiegu")
            if self._kandydaci:
                czekaj = self.okres_s
            elif self._watchdog is not None:
                czekaj = min(self.przeglad_s, 0.5)
            else:
                czekaj = min(self.przeglad_s, 0.5) if self.przeglad_s > 0 else self.okres_s
            self._budzik.wait(max(0.005, czekaj))
            self._budzik.clear()

    def obieg(self) -> None:
        """Jeden obieg: powiadomienia z watchdog, przeglad okresowy folderu, ocena plikow, na ktore czekamy."""
        teraz = self.zegar()
        przeglad = teraz - self._ostatni_przeglad >= self.przeglad_s
        if self._do_nadrobienia:
            self._nadrob(teraz)  # pliki zastane z start(): decyzja przed powiadomieniami watchdog
        while self._zmiany:
            rodzaj, sciezka = self._zmiany.popleft()
            if rodzaj == "przeglad":
                przeglad = True
            elif rodzaj == "usuniety":
                self._zapomnij(_klucz(sciezka))
            else:
                self._zglos_zmiane(Path(sciezka), teraz)
        if przeglad:
            self._ostatni_przeglad = teraz
            self._przeglad(teraz)
        if self._do_nadrobienia:
            self._nadrob(teraz)
        gotowe = []
        for k, kand in list(self._kandydaci.items()):
            try:
                st = os.stat(kand["sciezka"])
            except FileNotFoundError:
                self._zapomnij(k)
                continue
            except OSError:
                continue  # chwilowo zajety: nastepny obieg
            if stat.S_ISDIR(st.st_mode):
                del self._kandydaci[k]  # katalog o nazwie pasujacej do wzorca
                continue
            podpis = (st.st_size, st.st_mtime_ns)
            if self._znane.get(k) == podpis:
                del self._kandydaci[k]  # echo powiadomienia o pliku juz rozstrzygnietym
                continue
            if podpis != kand["podpis"]:
                if kand["podpis"] is not None:
                    kand["zastany"] = False  # zmienil sie po starcie: to juz nowy zapis, nie plik zastany
                kand.update(podpis=podpis, od=teraz, zajety_od=None, proby=0, nastepna=None, info_po=None)  # zapis trwa: od nowa
                continue
            if kand["nastepna"] is not None and teraz + _EPS < kand["nastepna"]:
                continue  # plik zajety: nastepna proba pozniej (odstep rosnie)
            if teraz - kand["od"] >= self.stabilizacja_s:
                gotowe.append((st.st_mtime_ns, kand["sciezka"].name, k))
        for _, _, k in sorted(gotowe):  # kilka plikow gotowych w jednym obiegu: w kolejnosci czasu zapisu
            if k in self._kandydaci and not self._stop.is_set():
                self._rozstrzygnij(k, self._kandydaci[k], teraz)

    def _w_zakresie(self, rel: str) -> bool:
        return self.rekurencyjnie or "/" not in rel

    def _pasuje(self, sciezka) -> bool:
        return fnmatch.fnmatchcase(Path(sciezka).name.lower(), self.wzorzec_pliku.lower())

    def _zapomnij(self, k: str) -> None:
        """Plik zniknal (usuniety albo przeniesiony): ta sama nazwa zapisana pozniej jest oceniana od nowa."""
        self._kandydaci.pop(k, None)
        self._znane.pop(k, None)
        self._pominiete.discard(k)

    def _zglos_zmiane(self, sciezka: Path, teraz: float, zastany: bool = False) -> None:
        k = _klucz(sciezka)
        if k in self._kandydaci:
            return
        if not self.rekurencyjnie and _klucz(sciezka.parent) != _klucz(self.folder):
            return
        poza = not self._pasuje(sciezka)
        if poza and k in self._pominiete:
            return  # plik spoza wzorca: jeden wpis w dzienniku, dopoki nie zniknie
        self._kandydaci[k] = {"sciezka": sciezka, "podpis": None, "od": teraz, "poza": poza, "zastany": zastany,
                              "zajety_od": None, "proby": 0, "nastepna": None, "info_po": None}

    def _przeglad(self, teraz: float) -> None:
        dostepny = self.folder.is_dir()
        if dostepny != self._folder_dostepny:
            self._folder_dostepny = dostepny
            LOG.info("folder eksportu skanera %s: %s", "dostepny" if dostepny else "niedostepny", self.folder)
            if not dostepny:
                self._zatrzymaj_watchdog()
        if not dostepny:
            return
        self._sprawdz_watchdog()
        self._uruchom_watchdog()
        if not self._poczatek_ustalony:
            self._ustal_zastane(teraz)  # P3: folder pojawil sie po starcie - jego zawartosc to pliki zastane, nie nowe skany
            return
        niedostepne: list = []
        widziane = set()
        for rel, rozmiar, mtime_ns in pliki_w_folderze(self.folder, niedostepne=niedostepne):
            if not self._w_zakresie(rel):
                continue
            sciezka = self.folder / rel
            k = _klucz(sciezka)
            widziane.add(k)
            if k in self._kandydaci or self._znane.get(k) == (rozmiar, mtime_ns):
                continue
            if self._niezbadane and k not in self._znane and k not in self._pominiete and _pod(k, self._niezbadane):
                self._zastany(rel, rozmiar, mtime_ns, teraz)  # pierwszy odczyt katalogu, ktorego nie dalo sie odczytac przy starcie
                continue
            self._zglos_zmiane(sciezka, teraz)
        nied = {_klucz(p) for p in niedostepne}
        if _klucz(self.folder) in nied:
            return  # samego folderu nie dalo sie wylistowac: nic nie zapominamy
        if self._niezbadane:  # odczytane teraz = zbadane; co nadal niedostepne pod nimi - nadal niezbadane
            self._niezbadane = {p for p in self._niezbadane if _pod(p, nied)} | {n for n in nied if _pod(n, self._niezbadane)}
        for k in [k for k in (*self._znane, *self._pominiete) if k not in widziane and not _pod(k, nied)]:
            try:  # P3 (b): brak na liscie to jeszcze nie usuniecie (chwilowy blad listowania) - pytamy o sam plik
                os.stat(k)
            except (FileNotFoundError, NotADirectoryError):
                self._zapomnij(k)  # naprawde zniknal: ta sama nazwa zapisana pozniej jest nowym plikiem
            except OSError:
                pass  # chwilowo niedostepny: pamietany dalej

    def _rozstrzygnij(self, k: str, kand: dict, teraz: float) -> None:
        sciezka = kand["sciezka"]
        if kand["poza"]:  # plik spoza wzorca (np. plik pomocniczy programu skanera): wpis po ustaniu zmian, bez zdarzenia
            if teraz - kand["od"] < self.odrzuc_po_s or ktos_pisze(sciezka):
                return
            del self._kandydaci[k]
            self._pominiete.add(k)
            self._odrzuc(sciezka, "poza_wzorcem", f"{POWODY['poza_wzorcem']} ({self.wzorzec_pliku})", kand["podpis"][0])
            return
        w = sprawdz_stl(sciezka, self.min_trojkatow, self.min_rozmiar_mb)
        if self._stop.is_set():
            return
        if w.powod == "blad_odczytu":
            if not os.path.exists(sciezka):
                self._zapomnij(k)
                return
            self._zajety(kand, teraz, w.opis, ODSTEP_ZAJETY_MAX_S)  # B1: zajety to nie odrzucenie - czekamy bez limitu prob
            return
        if w.powod is not None:
            if teraz - kand["od"] < self.odrzuc_po_s or ktos_pisze(sciezka):
                return  # moze byc jeszcze dopisywany
            if _podpis(sciezka) != kand["podpis"] or w.rozmiar != kand["podpis"][0]:
                return  # program dopisal reszte i zamknal plik miedzy sprawdzeniem a ktos_pisze: nastepny obieg oceni plik od nowa
            self._znane[k] = kand["podpis"]
            del self._kandydaci[k]
            self._odrzuc(sciezka, w.powod, w.opis, w.rozmiar)
            return
        if ktos_pisze(sciezka):  # caly plik juz jest, ale program skanera jeszcze go nie zamknal
            self._zajety(kand, teraz, "plik kompletny, ale inny program trzyma go jeszcze otwartego do zapisu", ODSTEP_PISZE_MAX_S)
            return
        try:
            sha16 = skrot16_pliku(sciezka)
            st = os.stat(sciezka)
        except FileNotFoundError:
            self._zapomnij(k)
            return
        except OSError as e:
            self._zajety(kand, teraz, f"{POWODY['blad_odczytu']}: {type(e).__name__}", ODSTEP_ZAJETY_MAX_S)
            return
        if self._stop.is_set():
            return  # stop() w trakcie liczenia skrotu: plik zostaje kandydatem (zdarzenie po ponownym start())
        if (st.st_size, st.st_mtime_ns) != kand["podpis"]:  # zmienil sie w trakcie liczenia skrotu
            kand.update(podpis=(st.st_size, st.st_mtime_ns), od=teraz, zajety_od=None, proby=0, nastepna=None, info_po=None)
            return
        self._znane[k] = kand["podpis"]
        del self._kandydaci[k]
        pierwszy = self._skroty.setdefault(sha16, str(sciezka))
        duplikat = _klucz(pierwszy) != k
        self._nr += 1
        z = ZdarzenieSkanu(plik=sciezka, sha16=sha16, rozmiar=st.st_size, trojkaty=w.trojkaty, czas_pliku=st.st_mtime_ns / 1e9, mtime_ns=st.st_mtime_ns,
                           czas_zdarzenia=time.time(), nr=self._nr, ponowny=k in self._zgloszone, duplikat=duplikat, duplikat_z=pierwszy if duplikat else None,
                           zastany=bool(kand["zastany"]))
        self._zgloszone.add(k)
        LOG.info("nowy skan nr %d: %s sha16=%s rozmiar=%d trojkatow=%d%s%s%s", z.nr, sciezka.name, sha16, z.rozmiar, z.trojkaty,
                 " (ponowny zapis)" if z.ponowny else "", " (duplikat zawartosci)" if duplikat else "", " (plik zastany - nadrabianie)" if z.zastany else "")
        self._wyslij(self.na_skan, z)

    def _zajety(self, kand: dict, teraz: float, opis: str, odstep_max_s: float) -> None:
        """B1: pliku nie da sie teraz ocenic, bo trzyma go inny program. Kolejna proba po rosnacym odstepie (okres_s, 2x, 4x ...,
        najwyzej ``odstep_max_s``), bez limitu liczby prob; po ``informuj_po_s`` informacja ``Oczekiwanie``, potem co
        ``informuj_co_s``. Plik nie trafia do ``_znane`` - zdarzenie przyjdzie po zwolnieniu (albo po restarcie z nadrabianiem)."""
        if kand["zajety_od"] is None:
            kand["zajety_od"], kand["proby"], kand["info_po"] = teraz, 0, teraz + self.informuj_po_s
        kand["proby"] += 1
        kand["nastepna"] = teraz + min(odstep_max_s, self.okres_s * 2 ** min(kand["proby"], 16))
        if teraz + _EPS >= kand["info_po"]:
            kand["info_po"] = teraz + self.informuj_co_s
            czeka = teraz - kand["zajety_od"]
            o = Oczekiwanie(plik=kand["sciezka"], od_s=round(czeka, 1), opis=f"czeka na zwolnienie pliku od {czeka:.0f} s: {opis}", czas=time.time())
            self._oczekiwan += 1
            LOG.info("plik zajety: %s - %s", kand["sciezka"].name, o.opis)
            self._wyslij(self.na_oczekiwanie, o)

    def _odrzuc(self, sciezka: Path, powod: str, opis: str, rozmiar: int | None) -> None:
        o = Odrzucenie(plik=sciezka, powod=powod, opis=opis, rozmiar=rozmiar, czas=time.time())
        self._odrzucen += 1
        self.odrzucone.append(o)
        LOG.info("plik pominiety: %s powod=%s (%s)", sciezka.name, powod, opis)
        self._wyslij(self.na_odrzucenie, o)

    def _wyslij(self, funkcja, obiekt) -> None:
        if funkcja is None:
            self.zdarzenia.put(obiekt)
            return
        try:
            funkcja(obiekt)
        except Exception:  # noqa: BLE001 - blad odbiorcy nie zatrzymuje obserwacji
            LOG.exception("scanner: blad funkcji odbierajacej %s", type(obiekt).__name__)
