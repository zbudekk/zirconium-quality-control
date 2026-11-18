"""baza - plik SQLite stanowiska: schemat, migracje z kopia pliku, zrzut stanu (E3-A1).

Schemat = plan etapu 3, sekcja 3.4 (11 tabel, jeden plik; decyzje wlasciciela DW1 i DW2 z 17.11.2026): te same tabele,
kolumny, klucze, unikaty i indeksy. Ponad plan schemat ma 15 ograniczen NOT NULL, 2 wartosci domyslne i 4 wyzwalacze
"tylko dopisywanie" - wszystkie wypisane z uzasadnieniem w ``OGRANICZENIA_PONAD_3_4`` i w ``opisy_modulow/baza.md``.
Plik: ``[sciezki] baza`` (domyslnie ``dane/stanowisko.sqlite`` w katalogu programu), poza repozytorium i poza OneDrive.
Wersja schematu siedzi w ``PRAGMA user_version``; migracje ida tylko w przod, kazda w jednej transakcji, a przed
migracja istniejacego pliku powstaje jego kopia ``<nazwa>.kopia_v<wersja>_<data>_<godzina>.sqlite``.
Baza nowsza niz program = odmowa (``BladBazy``), plik zostaje nietkniety.

DANE OSOBOWE (DW2 po decyzji z 17.11.2026): nazwy folderow i plikow zlecen (z nazwiskami) wolno trzymac wylacznie
w czterech tabelach - ``zlecenia``, ``projekty``, ``frezowania``, ``excel_zapisy`` (``KOLUMNY_Z_NAZWAMI``). Pozostale
tabele, pliki wynikow, listy i dziennik ``zdarzenia`` uzywaja skrotu ``sha16`` projektu, numeru kuwety i numerow wierszy;
``Baza.zdarzenie`` wycina sciezki z kazdego tekstu (``bez_sciezek``). Statusy sa tekstem bez listy zamknietej.

Do bazy wchodzi sie tylko przez ``otworz`` (wlacza klucze obce i czas czekania na blokade).
Modul korzysta tylko z biblioteki standardowej (wczytuje go proces okna, narzedzia i raport metryk).
Opis: ``opisy_modulow/baza.md``.
"""
from __future__ import annotations

import contextlib
import datetime as dt
import filecmp
import json
import re
import shutil
import sqlite3
from pathlib import Path
from typing import Any, Callable, Iterator

from .ustawienia import KORZEN

TABELE = ("zlecenia", "projekty", "cechy_stl", "frezowania", "sesje_pieca", "skany", "prace", "decyzje", "stan_punktow",
          "excel_zapisy", "zdarzenia")
# Jedyne kolumny, w ktorych wolno trzymac nazwe folderu albo pliku zlecenia (dane osobowe). Uzywaja tego testy kryterium 8,
# ``Baza.zrzut(bez_nazw=True)`` i przyszla kopia bazy dla programistow.
KOLUMNY_Z_NAZWAMI = {
    "zlecenia": ("folder", "folder_norm"),
    "projekty": ("plik",),
    "frezowania": ("plik_w_raporcie", "raport_plik"),
    "excel_zapisy": ("folder",),
}
TABELE_Z_NAZWAMI = tuple(KOLUMNY_Z_NAZWAMI)
TABELE_TYLKO_DOPISYWANIE = ("decyzje", "zdarzenia")
CZEKAJ_NA_BLOKADE_MS = 5000

# Ograniczenia NOT NULL, ktorych sekcja 3.4 planu nie podaje (decyzja koordynatora po recenzji PR #16: kazde wypisane
# z uzasadnieniem; zadne nie blokuje zapisu przewidzianego planem w paczkach A4-A9). Wartosci domyslne: tylko `usuniety` = 0.
OGRANICZENIA_PONAD_3_4 = {
    "zlecenia.zrodlo": "czesc unikatu (zrodlo, folder): przy pustej wartosci SQLite nie pilnowalby unikatu zlecenia",
    "zlecenia.folder": "czesc unikatu (zrodlo, folder): zlecenie to folder, bez nazwy folderu wiersz nic nie znaczy",
    "zlecenia.usuniety": "flaga 0 / 1 z wartoscia domyslna 0: zapytania filtruja `usuniety = 0`, pusta wartosc gubilaby zlecenie",
    "projekty.zlecenie_id": "czesc unikatu (zlecenie_id, plik): punkt pracy zawsze nalezy do zlecenia",
    "projekty.plik": "czesc unikatu (zlecenie_id, plik): punkt pracy to plik STL w folderze zlecenia",
    "projekty.usuniety": "flaga 0 / 1 z wartoscia domyslna 0: `session` szuka punktu po `sha16` wsrod `usuniety = 0`",
    "skany.status": "logika wieczoru wybiera skany po statusie (aktywne, zastapione); skan bez statusu znikalby ze stanu po cichu",
    "prace.skan_id": "praca istnieje tylko jako gniazdo konkretnego skanu (klucz obcy i czesc unikatu)",
    "prace.nr_fragmentu": "czesc unikatu (skan_id, gniazdo, nr_fragmentu): rozroznia dwie prace w jednym gniezdzie",
    "decyzje.rodzaj": "wiersz dziennika decyzji bez rodzaju nie daje sie zinterpretowac ani cofnac",
    "decyzje.czas": "kolejnosc i metryki (M1) licza sie z czasu decyzji; dziennik jest tylko do dopisywania, wiec brak nie da sie uzupelnic",
    "stan_punktow.stan": "tabela istnieje po to, zeby trzymac stan punktu; listy to zapytania po tej kolumnie",
    "zdarzenia.czas": "dziennik bez czasu jest bezuzyteczny dla metryk (M1) i nie da sie go poprawic (tylko dopisywanie)",
    "zdarzenia.zrodlo": "kazdy wpis dziennika ma nadawce (scanner, silnik, ui, ...); wpisuje go zawsze `Baza.zdarzenie`",
    "zdarzenia.typ": "wpis dziennika bez typu nie daje sie zliczyc ani odfiltrowac; wpisuje go zawsze `Baza.zdarzenie`",
}


def _tylko_dopisywanie(tabela: str) -> tuple[str, ...]:
    return (
        f"CREATE TRIGGER {tabela}_bez_zmiany BEFORE UPDATE ON {tabela} BEGIN "
        f"SELECT RAISE(ABORT, '{tabela}: tylko dopisywanie (wiersza nie mozna zmienic)'); END",
        f"CREATE TRIGGER {tabela}_bez_usuwania BEFORE DELETE ON {tabela} BEGIN "
        f"SELECT RAISE(ABORT, '{tabela}: tylko dopisywanie (wiersza nie mozna usunac)'); END",
    )


# Wersja 1: tabele, kolumny, klucze, unikaty i indeksy wg sekcji 3.4 planu (kolejnosc kolumn jak w planie).
# NOT NULL i DEFAULT ponad plan: tylko te z ``OGRANICZENIA_PONAD_3_4``.
_WERSJA_1 = (
    """CREATE TABLE zlecenia (
        id INTEGER PRIMARY KEY,
        zrodlo TEXT NOT NULL,              -- cyrkon / prywatne
        folder TEXT NOT NULL,              -- nazwa folderu doslownie: DANE OSOBOWE
        folder_norm TEXT,
        kuweta TEXT,                       -- tekst: 3263 albo #1234
        mtime REAL,
        dodano TEXT,
        usuniety INTEGER NOT NULL DEFAULT 0,
        UNIQUE (zrodlo, folder))""",
    "CREATE INDEX zlecenia_kuweta ON zlecenia (kuweta)",
    """CREATE TABLE projekty (
        id INTEGER PRIMARY KEY,
        zlecenie_id INTEGER NOT NULL REFERENCES zlecenia (id),
        plik TEXT NOT NULL,                -- nazwa pliku STL w folderze zlecenia: DANE OSOBOWE
        sha16 TEXT,                        -- 16 znakow SHA-256 zawartosci (identyfikator z match, synth, decyzje.csv)
        zeby TEXT,
        typ TEXT,
        mtime_ns INTEGER,
        rozmiar INTEGER,
        zaindeksowano TEXT,
        usuniety INTEGER NOT NULL DEFAULT 0,
        UNIQUE (zlecenie_id, plik))""",
    "CREATE INDEX projekty_sha16 ON projekty (sha16)",
    """CREATE TABLE cechy_stl (
        sha16 TEXT PRIMARY KEY,
        trojkaty INTEGER,
        szczelny INTEGER,
        objetosc_mm3 REAL,
        hull_mm3 REAL,
        pole_mm2 REAL,
        obrys_a_mm REAL,
        obrys_b_mm REAL,
        wysokosc_mm REAL,
        miniatura BLOB,                    -- PNG
        wersja_cech INTEGER,
        policzono TEXT)""",
    """CREATE TABLE frezowania (
        id INTEGER PRIMARY KEY,
        projekt_id INTEGER REFERENCES projekty (id),   -- NULL: STL z raportu nieznaleziony w indeksie albo wpis na krazek
        plik_w_raporcie TEXT,              -- nazwa pliku z raportu: DANE OSOBOWE; NULL: wpis reczny wspolczynnika na krazek (K7)
        krazek TEXT,
        wspolczynnik REAL,
        data TEXT,
        zrodlo TEXT,                       -- millbox_html / millbox_pdf / csv / reczny
        raport_plik TEXT,                  -- DANE OSOBOWE (nazwa pliku raportu)
        wczytano TEXT,
        UNIQUE (plik_w_raporcie, krazek, data))""",   # unikat nie obejmuje wierszy z pusta wartoscia (NULL) w ktorejs z trzech kolumn
    """CREATE TABLE sesje_pieca (
        id INTEGER PRIMARY KEY,
        data TEXT,
        nr_w_dniu INTEGER,
        otwarto TEXT,
        zamknieto TEXT,
        zamknal TEXT)""",
    """CREATE TABLE skany (
        id INTEGER PRIMARY KEY,
        plik TEXT,                         -- plik skanu ze skanera (nie plik zlecenia)
        sha16 TEXT,
        rozmiar INTEGER,
        czas_pliku TEXT,
        czas_analizy TEXT,                 -- chwila przyjecia wyniku przez program: z niej wynika wieczor (doba robocza)
        czas_s REAL,
        tryb TEXT,                         -- wieczor / rano
        uklad TEXT,
        uklad_zrodlo TEXT,                 -- auto / reczny
        uklad_zgodny INTEGER,
        numer_plytki INTEGER,
        numer_zrodlo TEXT,                 -- dolki / podany / ramka / nieznany
        sesja_pieca_id INTEGER REFERENCES sesje_pieca (id),
        status TEXT NOT NULL,              -- przyjety / do_powtorzenia / zastapiony / niezgodny_uklad / blad / import
        zastepuje_id INTEGER REFERENCES skany (id),
        wynik_json TEXT,                   -- sciezka pliku wyniku
        wersja_programu TEXT,
        skrot_ustawien TEXT)""",
    """CREATE TABLE prace (
        id INTEGER PRIMARY KEY,
        skan_id INTEGER NOT NULL REFERENCES skany (id),
        gniazdo INTEGER,                   -- NULL: praca poza gniazdem
        nr_fragmentu INTEGER NOT NULL,
        status_fragmentu TEXT,
        status_match TEXT,
        status_inspekcji TEXT,
        status_gniazda TEXT,
        kandydat1_sha16 TEXT,
        kandydat1_pokrycie REAL,
        kandydat2_sha16 TEXT,
        kandydat2_pokrycie REAL,
        pewnosc REAL,
        frezowanie_id INTEGER REFERENCES frezowania (id),
        wspolczynnik REAL,
        korekta_skali REAL,
        ubytki INTEGER,                    -- liczba; szczegoly w pliku wyniku JSON
        ubytek_max_mm REAL,
        projekt_id INTEGER REFERENCES projekty (id),   -- przypisanie obowiazujace
        UNIQUE (skan_id, gniazdo, nr_fragmentu))""",
    """CREATE TABLE decyzje (
        id INTEGER PRIMARY KEY,
        praca_id INTEGER REFERENCES prace (id),
        skan_id INTEGER REFERENCES skany (id),
        rodzaj TEXT NOT NULL,
        wartosc TEXT,
        operator TEXT,
        czas TEXT NOT NULL)""",
    """CREATE TABLE stan_punktow (
        projekt_id INTEGER PRIMARY KEY REFERENCES projekty (id),
        stan TEXT NOT NULL,                -- oczekuje / rozpoznany / do_dofrezowania / brak_po_piecu / zamkniety_recznie
        praca_id INTEGER REFERENCES prace (id),
        sesja_pieca_id INTEGER REFERENCES sesje_pieca (id),
        czas TEXT)""",
    """CREATE TABLE excel_zapisy (
        id INTEGER PRIMARY KEY,
        czas TEXT,
        sesja_pieca_id INTEGER REFERENCES sesje_pieca (id),
        zlecenie_id INTEGER REFERENCES zlecenia (id),
        kuweta TEXT,
        folder TEXT,                       -- DANE OSOBOWE (wymaga tego format logu Excela)
        numer_zlecenia_b TEXT,
        arkusz TEXT,
        wiersz INTEGER,
        regula INTEGER,
        wynik TEXT,
        tryb TEXT,
        operator TEXT)""",
    """CREATE TABLE zdarzenia (
        id INTEGER PRIMARY KEY,
        czas TEXT NOT NULL,
        zrodlo TEXT NOT NULL,              -- scanner / silnik / ui / ramka_w / ramka_p / excel / pula / system
        typ TEXT NOT NULL,
        skan_id INTEGER,
        dane TEXT)""",                     # JSON bez nazwisk i bez sciezek
    *_tylko_dopisywanie("decyzje"),
    *_tylko_dopisywanie("zdarzenia"),
)

# numer wersji docelowej -> polecenia SQL przejscia z wersji o jeden nizszej; kolejne paczki dopisuja nastepne numery
MIGRACJE: dict[int, tuple[str, ...]] = {1: _WERSJA_1}
WERSJA_SCHEMATU = 1


class BladBazy(RuntimeError):
    """Baza nie nadaje sie do pracy (nowsza niz program, uszkodzona, nieudana migracja, zajeta); komunikat dla czlowieka."""


# --- sciezki w tekstach: poza cztery tabele z nazwami nie moze wyjsc nazwa folderu zlecenia ---------------------------
ZNACZNIK_SCIEZKI = "<sciezka>"
# Poczatek sciezki BEZWZGLEDNEJ: litera dysku (C:\ albo C:/), zasob sieciowy (\\serwer albo //serwer), zmienna srodowiskowa
# (%USERPROFILE%\, $HOME/), katalog domowy (~/) albo /katalog/ na poczatku slowa.
_SCIEZKA_BEZWZGLEDNA = (r"[A-Za-z]:[\\/]|\\\\[^\\\s]|(?<![\w:/])//(?=[^/\s])|%\w+%[\\/]|\$\w+[\\/]|(?<![\w.])~[\\/]"
                        r"|(?<![\w.:/<])/(?=[\w.~-]+/)")
# Sciezka WZGLEDNA z separatorem: slowo\slowo; slowo/.../slowo (co najmniej dwa ukosniki); slowo/plik.roz (ukosnik i rozszerzenie
# pliku). Pojedyncze "A/B", "km/h", "0.91/0.95", "17/11" sciezka nie sa.
_SCIEZKA_WZGLEDNA = r"[\w.~#-]+\\(?=[\w.~#-])|[\w.~#-]+/[\w .~#-]*?/(?=[\w.~#-])|[\w.~#-]+/[\w .~#-]*?\.[A-Za-z]\w{1,3}\b"
_POCZATEK_SCIEZKI = re.compile(f"(?P<bezwzgledna>{_SCIEZKA_BEZWZGLEDNA})|(?P<wzgledna>{_SCIEZKA_WZGLEDNA})")
_CUDZYSLOWY = "'\""
_OGRANICZNIKI = ":;,=([{\n" + _CUDZYSLOWY  # przed sciezka wzgledna: od tego znaku zaczyna sie wycinany kawalek


def bez_sciezek(tekst: str) -> str:
    """Zastepuje sciezki znacznikiem ``<sciezka>`` (nazwy folderow i plikow zlecen zawieraja nazwiska).

    Rozpoznaje sciezki bezwzgledne (dysk, zasob sieciowy w obu zapisach, zmienne srodowiskowe, katalog domowy) i wzgledne
    z separatorem. Nazwy folderow maja spacje, wiec granic sciezki nie da sie zgadnac - funkcja wycina z zapasem:
    - koniec: sciezka w cudzyslowie albo apostrofach konczy sie na zamykajacym znaku, kazda inna na koncu wiersza
      (reszta wiersza przepada razem z nia);
    - poczatek sciezki wzglednej: od poprzedniego ogranicznika (``: ; , = ( [ {``, cudzyslow) albo od poczatku wiersza,
      bo pierwsza czesc sciezki moze miec spacje ("9911 Nazwisko Imie\\plik.stl").
    ZNANA GRANICA: nazwa folderu albo pliku podana bez separatora sciezki nie jest rozpoznawana - wywolujacy (A2, A3)
    nie moze podawac nazw zlecen w tekstach przekazywanych do ``session`` i do dziennika.
    """
    czesci, i = [], 0
    while True:
        m = _POCZATEK_SCIEZKI.search(tekst, i)
        if m is None:
            czesci.append(tekst[i:])
            return "".join(czesci)
        start = m.start()
        if m.lastgroup == "wzgledna":
            while start > i and tekst[start - 1] not in _OGRANICZNIKI:
                start -= 1
            if not (start > i and tekst[start - 1] in _CUDZYSLOWY):
                while start < m.start() and tekst[start] == " ":
                    start += 1
        cudzyslow = tekst[start - 1] if start > i and tekst[start - 1] in _CUDZYSLOWY else None
        czesci.append(tekst[i:start])
        czesci.append(ZNACZNIK_SCIEZKI)
        koniec = tekst.find(cudzyslow, max(start, m.end())) if cudzyslow else -1
        if koniec < 0:
            koniec = tekst.find("\n", start)
        i = koniec if koniec >= 0 else len(tekst)


def oczysc(obiekt: Any) -> Any:
    """Kopia danych (slowniki, listy, wartosci proste) z wycietymi sciezkami w kazdym tekscie; kluczy slownikow nie zmienia."""
    if isinstance(obiekt, str):
        return bez_sciezek(obiekt)
    if isinstance(obiekt, dict):
        return {k: oczysc(v) for k, v in obiekt.items()}
    if isinstance(obiekt, (list, tuple)):
        return [oczysc(v) for v in obiekt]
    return obiekt


def sciezka_z_ustawien(ust: dict, klucz: str) -> Path:
    """Sciezka z ``[sciezki]``; wzgledna liczona od katalogu programu (jak ``[plytki]``), nie od biezacego katalogu."""
    p = Path(ust["sciezki"][klucz])
    return p if p.is_absolute() else KORZEN / p


def sciezka_bazy(ust: dict) -> Path:
    """Plik bazy z ``[sciezki] baza``."""
    return sciezka_z_ustawien(ust, "baza")


def _polacz(plik: Path, tylko_odczyt: bool = False, czekaj_ms: int = CZEKAJ_NA_BLOKADE_MS) -> sqlite3.Connection:
    if tylko_odczyt:
        pol = sqlite3.connect(f"{plik.resolve().as_uri()}?mode=ro", uri=True, isolation_level=None)
    else:
        pol = sqlite3.connect(plik, isolation_level=None)  # transakcje jawne: BEGIN / COMMIT w ``Baza.transakcja``
    pol.row_factory = sqlite3.Row
    pol.execute("PRAGMA foreign_keys = ON")
    pol.execute(f"PRAGMA busy_timeout = {int(czekaj_ms)}")
    return pol


def _zajeta(e: sqlite3.Error) -> bool:
    """Czy blad SQLite oznacza blokade trzymana przez inne polaczenie (SQLITE_BUSY / SQLITE_LOCKED)."""
    kod = getattr(e, "sqlite_errorcode", None)
    return (kod is not None and kod & 0xFF in (5, 6)) or "database is locked" in str(e) or "database is busy" in str(e)


def _wersja(pol: sqlite3.Connection, plik: Path) -> int:
    try:
        return int(pol.execute("PRAGMA user_version").fetchone()[0])
    except sqlite3.DatabaseError as e:
        raise BladBazy(f"{plik.name}: plik nie jest baza SQLite albo jest uszkodzony ({e}); pliku nie zmieniono: {plik}") from e


def _za_nowa(plik: Path, wersja: int, docelowa: int) -> BladBazy:
    return BladBazy(f"{plik.name}: baza ma schemat w wersji {wersja}, a ten program obsluguje wersje do {docelowa} - "
                    f"zaktualizuj program (bazy nie zmieniono): {plik}")


def _kopia_przed_migracja(plik: Path, wersja: int, teraz: dt.datetime) -> Path:
    """Kopia pliku bazy przed migracja; gdy identyczna kopia tej wersji juz jest (poprzednia nieudana proba), zwraca ja."""
    for istniejaca in sorted(plik.parent.glob(f"{plik.stem}.kopia_v{wersja}_*.sqlite")):
        if filecmp.cmp(istniejaca, plik, shallow=False):
            return istniejaca
    znacznik = teraz.strftime("%Y%m%d_%H%M%S")
    cel = plik.with_name(f"{plik.stem}.kopia_v{wersja}_{znacznik}.sqlite")
    n = 1
    while cel.exists():
        n += 1
        cel = plik.with_name(f"{plik.stem}.kopia_v{wersja}_{znacznik}_{n}.sqlite")
    shutil.copy2(plik, cel)
    return cel


def _migruj(pol: sqlite3.Connection, plik: Path, od: int, do: int, kopia: Path | None) -> None:
    for wersja in range(od + 1, do + 1):
        try:
            pol.execute("BEGIN IMMEDIATE")
            for sql in MIGRACJE[wersja]:
                pol.execute(sql)
            pol.execute(f"PRAGMA user_version = {int(wersja)}")
            pol.execute("COMMIT")
        except (sqlite3.Error, KeyError) as e:
            if pol.in_transaction:
                pol.execute("ROLLBACK")
            raise BladBazy(f"{plik.name}: migracja do wersji {wersja} nie powiodla sie ({e!r}); baza zostala w wersji {wersja - 1}"
                           + (f"; kopia sprzed migracji: {kopia}" if kopia is not None else "")) from e


def otworz(plik: str | Path, *, tylko_odczyt: bool = False, zegar: Callable[[], dt.datetime] | None = None,
           czekaj_ms: int = CZEKAJ_NA_BLOKADE_MS) -> "Baza":
    """Otwiera baze; nowy plik zaklada, starszy migruje (po zrobieniu kopii pliku), nowszego odmawia.

    ``tylko_odczyt``: plik musi istniec i miec biezaca wersje schematu; nic nie jest zakladane ani migrowane
    (raport metryk, kopie dla programistow). ``czekaj_ms``: ile czekac na baze zajeta przez inny program.
    """
    plik = Path(plik)
    zegar = zegar or dt.datetime.now
    docelowa = max(MIGRACJE)
    if tylko_odczyt:
        if not plik.exists():
            raise BladBazy(f"brak pliku bazy: {plik}")
        pol = _polacz(plik, tylko_odczyt=True, czekaj_ms=czekaj_ms)
        try:
            wersja = _wersja(pol, plik)
            if wersja > docelowa:
                raise _za_nowa(plik, wersja, docelowa)
            if wersja < docelowa:
                raise BladBazy(f"{plik.name}: baza w wersji {wersja} wymaga migracji do wersji {docelowa} - otworz ja najpierw "
                               f"programem stanowiska (odczyt niczego nie zmienia): {plik}")
        except BaseException:
            pol.close()
            raise
        return Baza(plik, pol, zegar, czekaj_ms=czekaj_ms)
    istnial = plik.exists() and plik.stat().st_size > 0
    plik.parent.mkdir(parents=True, exist_ok=True)
    pol = _polacz(plik, czekaj_ms=czekaj_ms)
    kopia = None
    zmigrowano = None
    try:
        wersja = _wersja(pol, plik)
        if wersja > docelowa:
            raise _za_nowa(plik, wersja, docelowa)
        if wersja < docelowa:
            if istnial:  # kopia calego pliku przed jakakolwiek zmiana
                pol.close()
                kopia = _kopia_przed_migracja(plik, wersja, zegar())
                pol = _polacz(plik, czekaj_ms=czekaj_ms)
            _migruj(pol, plik, wersja, docelowa, kopia)
            zmigrowano = (wersja, docelowa)
    except BaseException:
        pol.close()
        raise
    baza = Baza(plik, pol, zegar, kopia_przed_migracja=kopia, zmigrowano=zmigrowano, czekaj_ms=czekaj_ms)
    if kopia is not None:
        baza.zdarzenie("system", "migracja", {"z": zmigrowano[0], "do": zmigrowano[1], "kopia": kopia.name})
    return baza


class Baza:
    """Otwarte polaczenie z plikiem bazy (tworzy je ``otworz``). Jeden proces piszacy: proces okna."""

    def __init__(self, plik: Path, polaczenie: sqlite3.Connection, zegar: Callable[[], dt.datetime],
                 kopia_przed_migracja: Path | None = None, zmigrowano: tuple[int, int] | None = None,
                 czekaj_ms: int = CZEKAJ_NA_BLOKADE_MS):
        self.plik = plik
        self.polaczenie = polaczenie
        self.kopia_przed_migracja = kopia_przed_migracja  # plik kopii, jesli to otwarcie migrowalo istniejaca baze
        self.zmigrowano = zmigrowano  # (z wersji, do wersji) albo None
        self.czekaj_ms = czekaj_ms
        self._zegar = zegar
        self._kolumny: dict[str, tuple[str, ...]] = {}

    def __enter__(self) -> "Baza":
        return self

    def __exit__(self, *exc) -> None:
        self.zamknij()

    def zamknij(self) -> None:
        if self.polaczenie is not None:
            self.polaczenie.close()
            self.polaczenie = None

    def teraz(self) -> str:
        """Czas lokalny ISO z dokladnoscia do sekundy (format wszystkich kolumn czasu w bazie)."""
        return self._zegar().replace(microsecond=0).isoformat()

    def wersja(self) -> int:
        return int(self.polaczenie.execute("PRAGMA user_version").fetchone()[0])

    def _wykonaj(self, sql: str, parametry: tuple | dict = ()) -> sqlite3.Cursor:
        """Jedno polecenie; blokada trzymana przez inny program = ``BladBazy`` z komunikatem dla czlowieka (nie surowy blad SQLite)."""
        try:
            return self.polaczenie.execute(sql, parametry)
        except sqlite3.OperationalError as e:
            if _zajeta(e):
                raise BladBazy(f"{self.plik.name}: baza jest zajeta przez inny program (czekano {self.czekaj_ms / 1000:g} s) - zamknij go albo "
                               f"sprobuj ponownie za chwile; niczego nie zapisano") from e
            raise

    @contextlib.contextmanager
    def transakcja(self) -> Iterator[None]:
        """Calosc albo nic. Zagniezdzone wejscie nalezy do transakcji zewnetrznej. Baza zajeta = ``BladBazy``, bez zmian."""
        if self.polaczenie.in_transaction:
            yield
            return
        self._wykonaj("BEGIN IMMEDIATE")
        try:
            yield
            self._wykonaj("COMMIT")
        except BaseException:
            if self.polaczenie.in_transaction:
                self.polaczenie.execute("ROLLBACK")
            raise

    def wykonaj(self, sql: str, parametry: tuple | dict = ()) -> sqlite3.Cursor:
        return self._wykonaj(sql, parametry)

    def wiersze(self, sql: str, parametry: tuple | dict = ()) -> list[dict]:
        return [dict(w) for w in self._wykonaj(sql, parametry)]

    def wiersz(self, sql: str, parametry: tuple | dict = ()) -> dict | None:
        w = self._wykonaj(sql, parametry).fetchone()
        return dict(w) if w is not None else None

    def kolumny(self, tabela: str) -> tuple[str, ...]:
        if tabela not in TABELE:
            raise BladBazy(f"nieznana tabela {tabela!r} (znane: {', '.join(TABELE)})")
        if tabela not in self._kolumny:
            self._kolumny[tabela] = tuple(w[1] for w in self.polaczenie.execute(f"PRAGMA table_info({tabela})"))
        return self._kolumny[tabela]

    def wstaw(self, tabela: str, **kolumny: Any) -> int:
        """Dopisuje wiersz; nazwa tabeli i kolumn jest sprawdzana ze schematem. Zwraca ``id`` (rowid) wiersza."""
        znane = self.kolumny(tabela)
        for k in kolumny:
            if k not in znane:
                raise BladBazy(f"{tabela}: nieznana kolumna {k!r} (sa: {', '.join(znane)})")
        if not kolumny:
            return self._wykonaj(f"INSERT INTO {tabela} DEFAULT VALUES").lastrowid
        sql = f"INSERT INTO {tabela} ({', '.join(kolumny)}) VALUES ({', '.join('?' * len(kolumny))})"
        return self._wykonaj(sql, tuple(kolumny.values())).lastrowid

    def zdarzenie(self, zrodlo: str, typ: str, dane: dict | None = None, skan_id: int | None = None, czas: str | None = None) -> int:
        """Wpis do dziennika ``zdarzenia`` (tylko dopisywanie - wpisu nie da sie potem poprawic ani usunac).

        ``dane``: slownik -> JSON. Sciezki bezwzgledne w kazdym tekscie sa zastepowane znacznikiem ``<sciezka>``
        (``bez_sciezek``); nazwisk i nazw zlecen podanych inaczej niz sciezka piszacy nie moze tu wkladac.
        """
        tekst = json.dumps(oczysc(dane), ensure_ascii=False, sort_keys=True) if dane is not None else None
        return self.wstaw("zdarzenia", czas=czas or self.teraz(), zrodlo=zrodlo, typ=typ, skan_id=skan_id, dane=tekst)

    def zrzut(self, tabele: list[str] | tuple[str, ...] | None = None, bez_nazw: bool = False) -> dict[str, list[dict]]:
        """Cala zawartosc tabel (domyslnie wszystkich 11) jako slownik tabela -> wiersze w kolejnosci wstawiania.

        Sluzy do porownania stanu przed i po restarcie programu. UWAGA: pelny zrzut zawiera nazwy folderow i plikow zlecen
        (dane osobowe, ``KOLUMNY_Z_NAZWAMI``) - do logow, raportow i dla programistow tylko ``bez_nazw=True`` (te kolumny puste).
        """
        wynik = {}
        for tabela in (tabele if tabele is not None else TABELE):
            self.kolumny(tabela)  # sprawdzenie nazwy
            wiersze = self.wiersze(f"SELECT * FROM {tabela} ORDER BY rowid")
            if bez_nazw:
                for w in wiersze:
                    for kolumna in KOLUMNY_Z_NAZWAMI.get(tabela, ()):
                        w[kolumna] = None
            wynik[tabela] = wiersze
        return wynik

    def kopia(self, cel: str | Path) -> Path:
        """Spojna kopia calej bazy do nowego pliku (mechanizm kopii SQLite; dziala przy otwartym polaczeniu)."""
        cel = Path(cel)
        if cel.exists():
            raise BladBazy(f"plik kopii juz istnieje: {cel}")
        cel.parent.mkdir(parents=True, exist_ok=True)
        docelowe = sqlite3.connect(cel)
        try:
            self.polaczenie.backup(docelowe)
        finally:
            docelowe.close()
        return cel
