"""Lokalna baza SQLite katalogu (dane/qc.sqlite): projekty STL i wspolczynniki skali.

Schemat zatwierdzony przez wlasciciela (PRAGMA user_version = 1); zmiana schematu = najpierw opis dla
czlowieka. Polaczenie otwierane na kazde wywolanie (plik nie zostaje zablokowany).
"""

import sqlite3
from contextlib import closing
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

WERSJA = 1

SCHEMAT = """
CREATE TABLE IF NOT EXISTS projekty (
    id INTEGER PRIMARY KEY,
    zrodlo TEXT NOT NULL CHECK (zrodlo IN ('cyrkon', 'prywatne')),
    sciezka TEXT NOT NULL,
    folder TEXT NOT NULL,
    kuweta TEXT,
    nazwisko TEXT,
    numer_zeba INTEGER,
    mtime_ns INTEGER NOT NULL,
    rozmiar INTEGER NOT NULL,
    objetosc_mm3 REAL,
    pole_mm2 REAL,
    wym1_mm REAL,
    wym2_mm REAL,
    wym3_mm REAL,
    d2 BLOB,
    zaindeksowano TEXT NOT NULL,
    usuniety INTEGER NOT NULL DEFAULT 0,
    UNIQUE (zrodlo, sciezka)
);
CREATE TABLE IF NOT EXISTS wspolczynniki (
    id INTEGER PRIMARY KEY,
    plik_stl TEXT NOT NULL,
    krazek TEXT,
    wspolczynnik REAL NOT NULL,
    data TEXT NOT NULL,
    zrodlo TEXT NOT NULL CHECK (zrodlo IN ('csv', 'millbox'))
);
PRAGMA user_version = 1;
"""

KOLUMNY = ("zrodlo", "sciezka", "folder", "kuweta", "nazwisko", "numer_zeba", "mtime_ns", "rozmiar",
           "objetosc_mm3", "pole_mm2", "wym1_mm", "wym2_mm", "wym3_mm", "d2", "zaindeksowano", "usuniety")


def _ns(chwila: datetime) -> int:
    return int(chwila.timestamp() * 1e9)


def _wartosc(kolumna: str, wartosc):
    if kolumna == "d2" and isinstance(wartosc, np.ndarray):
        return np.asarray(wartosc, dtype=np.float32).tobytes()
    if kolumna == "sciezka":
        return str(wartosc).replace("\\", "/")
    return wartosc


class Baza:
    def __init__(self, sciezka):
        self.sciezka = Path(sciezka)

    def _polacz(self) -> sqlite3.Connection:
        pol = sqlite3.connect(self.sciezka)
        pol.row_factory = sqlite3.Row
        return pol

    def _wykonaj(self, sql: str, parametry=()) -> sqlite3.Cursor:
        with closing(self._polacz()) as pol, pol:
            return pol.execute(sql, parametry)

    def _wiersze(self, sql: str, parametry=()) -> list[dict]:
        with closing(self._polacz()) as pol:
            return [dict(w) for w in pol.execute(sql, parametry)]

    def utworz(self) -> None:
        """Tworzy tabele, jesli ich nie ma (ponowne wywolanie nic nie zmienia)."""
        self.sciezka.parent.mkdir(parents=True, exist_ok=True)
        with closing(self._polacz()) as pol:
            pol.executescript(SCHEMAT)

    def wersja(self) -> int:
        with closing(self._polacz()) as pol:
            return pol.execute("PRAGMA user_version").fetchone()[0]

    def dodaj_projekt(self, rekord: dict) -> int:
        """Dodaje rekord (dict kolumn bez id); zwraca id."""
        kolumny = [k for k in KOLUMNY if k in rekord]
        sql = (f"INSERT INTO projekty ({', '.join(kolumny)}) "
               f"VALUES ({', '.join('?' for _ in kolumny)})")
        return self._wykonaj(sql, [_wartosc(k, rekord[k]) for k in kolumny]).lastrowid

    def zmien_projekt(self, id_: int, zmiany: dict) -> None:
        kolumny = [k for k in KOLUMNY if k in zmiany]
        if not kolumny:
            return
        sql = f"UPDATE projekty SET {', '.join(f'{k} = ?' for k in kolumny)} WHERE id = ?"
        self._wykonaj(sql, [_wartosc(k, zmiany[k]) for k in kolumny] + [id_])

    def projekt(self, id_: int) -> dict | None:
        wiersze = self._wiersze("SELECT * FROM projekty WHERE id = ?", (id_,))
        return wiersze[0] if wiersze else None

    def projekty(self, zrodlo=None, od: datetime | None = None, do: datetime | None = None,
                 usuniete: bool = False) -> list[dict]:
        """Rekordy wg zrodla i zakresu mtime [od, do); usuniete=True dolacza rekordy usuniety=1."""
        warunki, parametry = [], []
        if zrodlo is not None:
            warunki.append("zrodlo = ?")
            parametry.append(zrodlo)
        if od is not None:
            warunki.append("mtime_ns >= ?")
            parametry.append(_ns(od))
        if do is not None:
            warunki.append("mtime_ns < ?")
            parametry.append(_ns(do))
        if not usuniete:
            warunki.append("usuniety = 0")
        gdzie = f" WHERE {' AND '.join(warunki)}" if warunki else ""
        return self._wiersze(f"SELECT * FROM projekty{gdzie} ORDER BY id", parametry)

    def oznacz_usuniete(self, ids) -> None:
        ids = list(ids)
        if ids:
            self._wykonaj(f"UPDATE projekty SET usuniety = 1 WHERE id IN ({', '.join('?' for _ in ids)})", ids)

    def usun_starsze_niz(self, dni: int, teraz: datetime) -> int:
        """Usuwa fizycznie rekordy usuniety=1 i starsze niz `dni` (wg mtime); zwraca liczbe usunietych."""
        granica = _ns(teraz - timedelta(days=dni))
        return self._wykonaj("DELETE FROM projekty WHERE usuniety = 1 OR mtime_ns < ?", (granica,)).rowcount
