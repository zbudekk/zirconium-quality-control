"""baza - plik SQLite stanowiska: schemat, migracje z kopia pliku, zrzut stanu (E3-A1).

Schemat = plan etapu 3, sekcja 3.4 (11 tabel, jeden plik; decyzje wlasciciela DW1 i DW2 z 17.11.2026).
Plik: ``[sciezki] baza`` (domyslnie ``dane/stanowisko.sqlite`` w katalogu programu), poza repozytorium i poza OneDrive.
Wersja schematu siedzi w ``PRAGMA user_version``; migracje ida tylko w przod, kazda w jednej transakcji, a przed
pierwsza migracja istniejacego pliku powstaje jego kopia ``<nazwa>.kopia_v<wersja>_<data>_<godzina>.sqlite``.
Baza nowsza niz program = odmowa (``BladBazy``), plik zostaje nietkniety.

DANE OSOBOWE: nazwa folderu zlecenia (z nazwiskiem) wystepuje wylacznie w tabelach ``zlecenia`` i ``excel_zapisy``
(``TABELE_Z_NAZWA_FOLDERU``). Pozostale tabele, pliki wynikow, listy i dziennik ``zdarzenia`` uzywaja skrotu ``sha16``
projektu, numeru kuwety i numerow wierszy. Statusy sa tekstem bez listy zamknietej (nowy status nie wymaga migracji).

Modul korzysta tylko z biblioteki standardowej (wczytuje go proces okna, narzedzia i raport metryk).
Opis: ``opisy_modulow/baza.md``.
"""
from __future__ import annotations

import contextlib
import datetime as dt
import json
import shutil
import sqlite3
from pathlib import Path
from typing import Any, Callable, Iterator

from .ustawienia import KORZEN

TABELE = ("zlecenia", "projekty", "cechy_stl", "frezowania", "sesje_pieca", "skany", "prace", "decyzje", "stan_punktow",
          "excel_zapisy", "zdarzenia")
TABELE_Z_NAZWA_FOLDERU = ("zlecenia", "excel_zapisy")  # jedyne miejsca na nazwe folderu zlecenia (DW2)
TABELE_TYLKO_DOPISYWANIE = ("decyzje", "zdarzenia")


def _tylko_dopisywanie(tabela: str) -> tuple[str, ...]:
    return (
        f"CREATE TRIGGER {tabela}_bez_zmiany BEFORE UPDATE ON {tabela} BEGIN "
        f"SELECT RAISE(ABORT, '{tabela}: tylko dopisywanie (wiersza nie mozna zmienic)'); END",
        f"CREATE TRIGGER {tabela}_bez_usuwania BEFORE DELETE ON {tabela} BEGIN "
        f"SELECT RAISE(ABORT, '{tabela}: tylko dopisywanie (wiersza nie mozna usunac)'); END",
    )


# Wersja 1: tabele i kolumny dokladnie wg sekcji 3.4 planu (kolejnosc kolumn jak w planie).
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
        plik TEXT NOT NULL,                -- nazwa pliku STL w folderze zlecenia
        sha16 TEXT NOT NULL,               -- 16 znakow SHA-256 zawartosci (identyfikator z match, synth, decyzje.csv)
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
        projekt_id INTEGER REFERENCES projekty (id),   -- NULL: STL z raportu nieznaleziony w indeksie
        plik_w_raporcie TEXT NOT NULL,
        krazek TEXT NOT NULL,
        wspolczynnik REAL,
        data TEXT NOT NULL,
        zrodlo TEXT,                       -- millbox_html / millbox_pdf / csv / reczny
        raport_plik TEXT,
        wczytano TEXT,
        UNIQUE (plik_w_raporcie, krazek, data))""",
    """CREATE TABLE sesje_pieca (
        id INTEGER PRIMARY KEY,
        data TEXT,
        nr_w_dniu INTEGER,
        otwarto TEXT,
        zamknieto TEXT,
        zamknal TEXT)""",
    """CREATE TABLE skany (
        id INTEGER PRIMARY KEY,
        plik TEXT,
        sha16 TEXT,
        rozmiar INTEGER,
        czas_pliku TEXT,
        czas_analizy TEXT,
        czas_s REAL,
        tryb TEXT,                         -- wieczor / rano
        uklad TEXT,
        uklad_zrodlo TEXT,                 -- auto / reczny
        uklad_zgodny INTEGER,
        numer_plytki INTEGER,
        numer_zrodlo TEXT,                 -- dolki / podany / ramka / nieznany
        sesja_pieca_id INTEGER REFERENCES sesje_pieca (id),
        status TEXT NOT NULL,              -- przyjety / do_powtorzenia / zastapiony / niezgodny_uklad / blad
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
        dane TEXT)""",                     # JSON bez nazwisk
    *_tylko_dopisywanie("decyzje"),
    *_tylko_dopisywanie("zdarzenia"),
)

# numer wersji docelowej -> polecenia SQL przejscia z wersji o jeden nizszej; kolejne paczki dopisuja nastepne numery
MIGRACJE: dict[int, tuple[str, ...]] = {1: _WERSJA_1}
WERSJA_SCHEMATU = 1


class BladBazy(RuntimeError):
    """Baza nie nadaje sie do pracy (nowsza niz program, uszkodzona, nieudana migracja); komunikat dla czlowieka."""


def sciezka_z_ustawien(ust: dict, klucz: str) -> Path:
    """Sciezka z ``[sciezki]``; wzgledna liczona od katalogu programu (jak ``[plytki]``), nie od biezacego katalogu."""
    p = Path(ust["sciezki"][klucz])
    return p if p.is_absolute() else KORZEN / p


def sciezka_bazy(ust: dict) -> Path:
    """Plik bazy z ``[sciezki] baza``."""
    return sciezka_z_ustawien(ust, "baza")


def _polacz(plik: Path, tylko_odczyt: bool = False) -> sqlite3.Connection:
    if tylko_odczyt:
        pol = sqlite3.connect(f"{plik.resolve().as_uri()}?mode=ro", uri=True, isolation_level=None)
    else:
        pol = sqlite3.connect(plik, isolation_level=None)  # transakcje jawne: BEGIN / COMMIT w ``Baza.transakcja``
    pol.row_factory = sqlite3.Row
    pol.execute("PRAGMA foreign_keys = ON")
    pol.execute("PRAGMA busy_timeout = 5000")
    return pol


def _wersja(pol: sqlite3.Connection, plik: Path) -> int:
    try:
        return int(pol.execute("PRAGMA user_version").fetchone()[0])
    except sqlite3.DatabaseError as e:
        raise BladBazy(f"{plik.name}: plik nie jest baza SQLite albo jest uszkodzony ({e}); pliku nie zmieniono: {plik}") from e


def _za_nowa(plik: Path, wersja: int, docelowa: int) -> BladBazy:
    return BladBazy(f"{plik.name}: baza ma schemat w wersji {wersja}, a ten program obsluguje wersje do {docelowa} - "
                    f"zaktualizuj program (bazy nie zmieniono): {plik}")


def _kopia_przed_migracja(plik: Path, wersja: int, teraz: dt.datetime) -> Path:
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


def otworz(plik: str | Path, *, tylko_odczyt: bool = False, zegar: Callable[[], dt.datetime] | None = None) -> "Baza":
    """Otwiera baze; nowy plik zaklada, starszy migruje (po zrobieniu kopii pliku), nowszego odmawia.

    ``tylko_odczyt``: plik musi istniec i miec biezaca wersje schematu; nic nie jest zakladane ani migrowane
    (raport metryk, kopie dla programistow).
    """
    plik = Path(plik)
    zegar = zegar or dt.datetime.now
    docelowa = max(MIGRACJE)
    if tylko_odczyt:
        if not plik.exists():
            raise BladBazy(f"brak pliku bazy: {plik}")
        pol = _polacz(plik, tylko_odczyt=True)
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
        return Baza(plik, pol, zegar)
    istnial = plik.exists() and plik.stat().st_size > 0
    plik.parent.mkdir(parents=True, exist_ok=True)
    pol = _polacz(plik)
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
                pol = _polacz(plik)
            _migruj(pol, plik, wersja, docelowa, kopia)
            zmigrowano = (wersja, docelowa)
    except BaseException:
        pol.close()
        raise
    baza = Baza(plik, pol, zegar, kopia_przed_migracja=kopia, zmigrowano=zmigrowano)
    if kopia is not None:
        baza.zdarzenie("system", "migracja", {"z": zmigrowano[0], "do": zmigrowano[1], "kopia": kopia.name})
    return baza


class Baza:
    """Otwarte polaczenie z plikiem bazy (tworzy je ``otworz``). Jeden proces piszacy: proces okna."""

    def __init__(self, plik: Path, polaczenie: sqlite3.Connection, zegar: Callable[[], dt.datetime],
                 kopia_przed_migracja: Path | None = None, zmigrowano: tuple[int, int] | None = None):
        self.plik = plik
        self.polaczenie = polaczenie
        self.kopia_przed_migracja = kopia_przed_migracja  # plik kopii, jesli to otwarcie migrowalo istniejaca baze
        self.zmigrowano = zmigrowano  # (z wersji, do wersji) albo None
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

    @contextlib.contextmanager
    def transakcja(self) -> Iterator[None]:
        """Calosc albo nic. Zagniezdzone wejscie nalezy do transakcji zewnetrznej."""
        if self.polaczenie.in_transaction:
            yield
            return
        self.polaczenie.execute("BEGIN IMMEDIATE")
        try:
            yield
        except BaseException:
            if self.polaczenie.in_transaction:
                self.polaczenie.execute("ROLLBACK")
            raise
        else:
            self.polaczenie.execute("COMMIT")

    def wykonaj(self, sql: str, parametry: tuple | dict = ()) -> sqlite3.Cursor:
        return self.polaczenie.execute(sql, parametry)

    def wiersze(self, sql: str, parametry: tuple | dict = ()) -> list[dict]:
        return [dict(w) for w in self.polaczenie.execute(sql, parametry)]

    def wiersz(self, sql: str, parametry: tuple | dict = ()) -> dict | None:
        w = self.polaczenie.execute(sql, parametry).fetchone()
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
            return self.polaczenie.execute(f"INSERT INTO {tabela} DEFAULT VALUES").lastrowid
        sql = f"INSERT INTO {tabela} ({', '.join(kolumny)}) VALUES ({', '.join('?' * len(kolumny))})"
        return self.polaczenie.execute(sql, tuple(kolumny.values())).lastrowid

    def zdarzenie(self, zrodlo: str, typ: str, dane: dict | None = None, skan_id: int | None = None, czas: str | None = None) -> int:
        """Wpis do dziennika ``zdarzenia`` (tylko dopisywanie). ``dane``: slownik -> JSON; bez nazwisk i nazw folderow zlecen."""
        tekst = json.dumps(dane, ensure_ascii=False, sort_keys=True) if dane is not None else None
        return self.wstaw("zdarzenia", czas=czas or self.teraz(), zrodlo=zrodlo, typ=typ, skan_id=skan_id, dane=tekst)

    def zrzut(self, tabele: list[str] | tuple[str, ...] | None = None) -> dict[str, list[dict]]:
        """Cala zawartosc tabel (domyslnie wszystkich 11) jako slownik tabela -> wiersze w kolejnosci wstawiania.

        Sluzy do porownania stanu przed i po restarcie programu. UWAGA: zawiera ``zlecenia.folder`` (dane osobowe) -
        nie zapisywac do logow ani raportow.
        """
        wynik = {}
        for tabela in (tabele if tabele is not None else TABELE):
            self.kolumny(tabela)  # sprawdzenie nazwy
            wynik[tabela] = self.wiersze(f"SELECT * FROM {tabela} ORDER BY rowid")
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
