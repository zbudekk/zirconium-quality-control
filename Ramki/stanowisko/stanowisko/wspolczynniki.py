"""wspolczynniki - wspolczynnik skurczu z pliku CSV ``plik;krazek;wspolczynnik;data`` i wpis reczny raz na krazek (E3-A4).

Decyzja wlasciciela DW6 = (c) z 17.11.2026: do czasu parsera raportow MillBox wspolczynnik pracy pochodzi z pliku CSV
wypelnianego przy frezarce ORAZ z wpisu recznego w programie raz na krazek. Oba zrodla to wiersze tabeli ``frezowania``:
- wiersz CSV: ``plik_w_raporcie`` = nazwa pliku STL (moze byc z folderem, ``Folder\\plik.stl``), ``krazek``, ``wspolczynnik``
  (moze byc pusty, gdy podano krazek - wtedy liczy sie wpis reczny krazka), ``data``, ``zrodlo = csv``, ``raport_plik`` = nazwa
  pliku CSV; ``projekt_id`` = plik z indeksu (``indeks.IndeksPlikow``) albo NULL, gdy pliku jeszcze nie ma w indeksie;
- wpis reczny (rozstrzygniecie koordynatora): wiersz bez pliku - ``plik_w_raporcie`` i ``projekt_id`` NULL, ``krazek``,
  ``wspolczynnik``, ``data`` = doba robocza wpisu, ``zrodlo = reczny``.
"Raz na krazek" pilnuje ten modul, nie baza (unikat ``frezowania`` nie obejmuje wierszy z NULL): ta sama wartosc drugi raz =
nic nowego; inna wartosc = odmowa z komunikatem, chyba ze ``zmien=True`` (ten sam dzien: poprawka wiersza, inny dzien: nowy
wiersz - obowiazuje najnowszy wpis krazka). Plik CSV wczytuje sie w calosci albo wcale: bledna linia = ``BladWspolczynnikow``
z numerami linii, w bazie nic. Ponowne wczytanie tego samego pliku nie dubluje wierszy (klucz: plik, krazek, data); wiersz
usuniety z pliku zostaje w bazie (plik moze byc czyszczony co dzien, a pula wieczorna siega wczoraj).

DANE OSOBOWE: nazwy plikow STL z CSV (z nazwiskami) trafiaja tylko do ``frezowania.plik_w_raporcie``; komunikaty bledow
podaja numery linii i opis, nigdy tresci pol ani sciezki pliku. Tylko biblioteka standardowa. Opis: ``opisy_modulow/pula.md``.
"""
from __future__ import annotations

import csv
import datetime as dt
import io
import math
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from . import baza as B
from . import indeks as I
from . import nazwy as N

NAGLOWEK = ("plik", "krazek", "wspolczynnik", "data")
WSPOLCZYNNIK_MIN = 1.0  # zakres sensownego wspolczynnika skurczu cyrkonii (literowka "12,2" albo "0,122" = blad linii)
WSPOLCZYNNIK_MAX = 1.6
ZRODLO_CSV = "csv"
ZRODLO_RECZNY = "reczny"
GRANICA_DOBY_GODZ = 6
KODOWANIA = ("utf-8-sig", "cp1250")  # CSV UTF-8 albo "CSV (rozdzielany srednikami)" z polskiego Excela
PODPOWIEDZ = "zapisz jako CSV rozdzielany srednikami; pierwsza linia: plik;krazek;wspolczynnik;data"
BLEDOW_W_KOMUNIKACIE = 10
_DATA_PL = re.compile(r"^(\d{1,2})\.(\d{1,2})\.(\d{4})$")
_DATA_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class BladWspolczynnikow(ValueError):
    """Zly plik CSV albo zly wpis reczny; komunikat dla czlowieka (bez nazw plikow), ``linie`` = numery blednych linii."""

    def __init__(self, komunikat: str, linie: list[int] | tuple[int, ...] = ()):
        super().__init__(komunikat)
        self.linie = list(linie)


@dataclass(frozen=True)
class WierszCsv:
    linia: int
    plik: str  # DANE OSOBOWE
    krazek: str | None
    wspolczynnik: float | None
    data: dt.date


@dataclass
class RaportCsv:
    wierszy: int = 0
    nowe: int = 0
    zmienione: int = 0
    bez_zmian: int = 0
    powiazane: int = 0  # wiersze pliku powiazane z plikiem z indeksu (po wczytaniu)
    brakujace: int = 0  # wiersze, ktorych pliku nie ma w indeksie
    niejednoznaczne: int = 0  # sama nazwa pliku pasuje do kilku plikow indeksu (wybrany najblizszy dacie)
    kodowanie: str = ""

    def do_slownika(self) -> dict:
        return asdict(self)


@dataclass
class RaportPowiazania:
    powiazane: int = 0
    brakujace: int = 0
    niejednoznaczne: int = 0

    def do_slownika(self) -> dict:
        return asdict(self)


def format_wspolczynnika(w: float) -> str:
    """1.23 -> "1,2300" (zapis w komunikatach)."""
    return f"{w:.4f}".replace(".", ",")


def _dekoduj(dane: bytes) -> tuple[str, str]:
    for kodowanie in KODOWANIA:
        try:
            return dane.decode(kodowanie), kodowanie
        except UnicodeDecodeError:
            continue
    raise BladWspolczynnikow(f"plik CSV wspolczynnikow: nieznane kodowanie znakow ({PODPOWIEDZ})", [1])


def wspolczynnik_z_tekstu(wartosc, wspolczynnik_min: float = WSPOLCZYNNIK_MIN, wspolczynnik_max: float = WSPOLCZYNNIK_MAX) -> float:
    """Liczba z tekstu ("1,2250" albo "1.2250") albo z liczby; ``ValueError`` z opisem (bez powtarzania wartosci)."""
    if isinstance(wartosc, bool) or wartosc is None:
        raise ValueError("wspolczynnik nie jest liczba (np. 1,2250)")
    if isinstance(wartosc, str):
        try:
            w = float(wartosc.strip().replace(",", "."))
        except ValueError:
            raise ValueError("wspolczynnik nie jest liczba (np. 1,2250)") from None
    elif isinstance(wartosc, (int, float)):
        w = float(wartosc)
    else:
        raise ValueError("wspolczynnik nie jest liczba (np. 1,2250)")
    if not math.isfinite(w):
        raise ValueError("wspolczynnik nie jest liczba (np. 1,2250)")
    if not wspolczynnik_min <= w <= wspolczynnik_max:
        raise ValueError(f"wspolczynnik poza zakresem {format_wspolczynnika(wspolczynnik_min)}-{format_wspolczynnika(wspolczynnik_max)}")
    return w


def data_z_tekstu(tekst: str) -> dt.date:
    """Data RRRR-MM-DD albo DD.MM.RRRR; ``ValueError`` z opisem (bez powtarzania wartosci)."""
    t = tekst.strip()
    try:
        if _DATA_ISO.match(t):
            return dt.date.fromisoformat(t)
        m = _DATA_PL.match(t)
        if m:
            return dt.date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
    except ValueError:
        pass
    raise ValueError("data nie ma postaci RRRR-MM-DD ani DD.MM.RRRR (albo nie istnieje)")


def _bledne(n: int) -> str:
    return f"{n} bledne linie" if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14 else f"{n} blednych linii"


def wczytaj_csv(plik: str | Path, *, wspolczynnik_min: float = WSPOLCZYNNIK_MIN,
                wspolczynnik_max: float = WSPOLCZYNNIK_MAX) -> list[WierszCsv]:
    """Wiersze pliku CSV (srednik, naglowek ``plik;krazek;wspolczynnik;data`` w 1. linii, UTF-8 albo cp1250, przecinek
    dziesietny dozwolony, data RRRR-MM-DD albo DD.MM.RRRR, puste linie pomijane). Kazdy blad = ``BladWspolczynnikow``
    z numerami WSZYSTKICH blednych linii (do ``BLEDOW_W_KOMUNIKACIE`` w tresci)."""
    wiersze, _ = _wczytaj_csv(Path(plik), wspolczynnik_min, wspolczynnik_max)
    return wiersze


def _wczytaj_csv(plik: Path, wspolczynnik_min: float, wspolczynnik_max: float) -> tuple[list[WierszCsv], str]:
    try:
        dane = plik.read_bytes()
    except FileNotFoundError:
        raise BladWspolczynnikow("brak pliku CSV wspolczynnikow (sprawdz [sciezki] folder_millbox)") from None
    except OSError as e:
        raise BladWspolczynnikow(f"nie mozna odczytac pliku CSV wspolczynnikow ({type(e).__name__}) - zamknij go w innym "
                                 "programie i sprobuj ponownie") from None
    tekst, kodowanie = _dekoduj(dane)
    czytnik = csv.reader(io.StringIO(tekst, newline=""), delimiter=";")
    bledy: list[tuple[int, str]] = []
    wiersze: list[WierszCsv] = []
    klucze: dict[tuple, WierszCsv] = {}
    naglowek_ok = False
    for pola in czytnik:
        linia = czytnik.line_num
        if not naglowek_ok:
            if tuple(p.strip().lower() for p in pola) == NAGLOWEK:
                naglowek_ok = True
                continue
            if len(pola) == 1 and pola[0].count(",") >= 3:
                raise BladWspolczynnikow(f"plik CSV wspolczynnikow: linia {linia}: pola rozdzielone przecinkiem - rozdzielaj "
                                         f"srednikiem ({PODPOWIEDZ})", [linia])
            raise BladWspolczynnikow(f"plik CSV wspolczynnikow: linia {linia}: brak naglowka plik;krazek;wspolczynnik;data "
                                     f"({PODPOWIEDZ})", [linia])
        if not any(p.strip() for p in pola):
            continue
        if len(pola) != 4:
            bledy.append((linia, f"oczekiwano 4 pola, jest {len(pola)}"))
            continue
        nazwa, krazek_t, wsp_t, data_t = (p.strip() for p in pola)
        nazwa = N.nfc(nazwa)
        krazek = N.normalizuj_krazek(krazek_t)
        if not nazwa:
            bledy.append((linia, "pusta nazwa pliku"))
            continue
        if not nazwa.lower().endswith(".stl"):
            bledy.append((linia, "nazwa pliku bez rozszerzenia .stl - sprawdz kolejnosc kolumn (plik;krazek;wspolczynnik;data)"))
            continue
        if krazek is not None and krazek.endswith(".STL"):
            bledy.append((linia, "krazek wyglada na nazwe pliku - sprawdz kolejnosc kolumn (plik;krazek;wspolczynnik;data)"))
            continue
        try:
            wsp = wspolczynnik_z_tekstu(wsp_t, wspolczynnik_min, wspolczynnik_max) if wsp_t else None
            data = data_z_tekstu(data_t)
        except ValueError as e:
            bledy.append((linia, str(e)))
            continue
        if wsp is None and krazek is None:
            bledy.append((linia, "pusty wspolczynnik i pusty krazek - podaj wspolczynnik albo krazek (wspolczynnik krazka "
                                 "wpisuje sie w programie)"))
            continue
        w = WierszCsv(linia, nazwa, krazek, wsp, data)
        klucz = (N.klucz_pliku(nazwa), krazek, data)
        poprzedni = klucze.get(klucz)
        if poprzedni is not None:
            if poprzedni.wspolczynnik != w.wspolczynnik:
                bledy.append((linia, f"ten sam plik, krazek i data co w linii {poprzedni.linia}, a inny wspolczynnik"))
            continue  # wiersz powtorzony bez zmian: liczy sie raz
        klucze[klucz] = w
        wiersze.append(w)
    if not naglowek_ok:
        raise BladWspolczynnikow(f"plik CSV wspolczynnikow: linia 1: brak naglowka plik;krazek;wspolczynnik;data ({PODPOWIEDZ})", [1])
    if bledy:
        opis = "; ".join(f"linia {n}: {t}" for n, t in bledy[:BLEDOW_W_KOMUNIKACIE])
        if len(bledy) > BLEDOW_W_KOMUNIKACIE:
            opis += f"; ... i {len(bledy) - BLEDOW_W_KOMUNIKACIE} wiecej"
        naglowek = "plik CSV wspolczynnikow, nic nie wczytano" if len(bledy) == 1 else \
            f"plik CSV wspolczynnikow: {_bledne(len(bledy))}, nic nie wczytano"
        raise BladWspolczynnikow(f"{naglowek} - {opis}", [n for n, _ in bledy])
    return wiersze, kodowanie


def wczytaj_do_bazy(baza: B.Baza, plik: str | Path, *, teraz: dt.datetime | None = None,
                    wspolczynnik_min: float = WSPOLCZYNNIK_MIN, wspolczynnik_max: float = WSPOLCZYNNIK_MAX) -> RaportCsv:
    """Wczytuje plik CSV do ``frezowania`` (w jednej transakcji, calosc albo nic) i laczy wiersze z indeksem.

    Wiersz o kluczu (plik, krazek, data), ktory juz jest w bazie: bez zmian albo poprawiony wspolczynnik (wiersze z innego
    zrodla, np. raportu MillBox, nie sa nadpisywane). Bledny plik = ``BladWspolczynnikow``, w bazie nic.
    """
    plik = Path(plik)
    wiersze, kodowanie = _wczytaj_csv(plik, wspolczynnik_min, wspolczynnik_max)
    czas = (teraz or dt.datetime.now()).replace(microsecond=0).isoformat()
    indeks = I.IndeksPlikow(baza)
    istniejace = {(N.klucz_pliku(w["plik_w_raporcie"]), w["krazek"], w["data"]): w
                  for w in baza.wiersze("SELECT * FROM frezowania WHERE plik_w_raporcie IS NOT NULL ORDER BY id")}
    r = RaportCsv(wierszy=len(wiersze), kodowanie=kodowanie)
    with baza.transakcja():
        for w in wiersze:
            projekt, kandydatow = indeks.znajdz(w.plik, w.data)
            r.niejednoznaczne += kandydatow > 1
            stary = istniejace.get((N.klucz_pliku(w.plik), w.krazek, w.data.isoformat()))
            if stary is not None:
                powiazany = stary["projekt_id"] if stary["projekt_id"] in indeks.po_id else None
                if powiazany is None and projekt is not None:
                    baza.wykonaj("UPDATE frezowania SET projekt_id = ? WHERE id = ?", (projekt["id"], stary["id"]))
                    powiazany = projekt["id"]
                r.powiazane += powiazany is not None
                r.brakujace += powiazany is None
                if stary["zrodlo"] == ZRODLO_CSV and not _rowne(stary["wspolczynnik"], w.wspolczynnik):
                    baza.wykonaj("UPDATE frezowania SET wspolczynnik = ?, wczytano = ? WHERE id = ?", (w.wspolczynnik, czas, stary["id"]))
                    r.zmienione += 1
                else:
                    r.bez_zmian += 1
                continue
            baza.wstaw("frezowania", projekt_id=projekt["id"] if projekt else None, plik_w_raporcie=w.plik, krazek=w.krazek,
                       wspolczynnik=w.wspolczynnik, data=w.data.isoformat(), zrodlo=ZRODLO_CSV, raport_plik=plik.name, wczytano=czas)
            r.nowe += 1
            r.powiazane += projekt is not None
            r.brakujace += projekt is None
        baza.zdarzenie("pula", "wspolczynniki_csv", r.do_slownika())
    return r


def _rowne(a: float | None, b: float | None) -> bool:
    if a is None or b is None:
        return a is None and b is None
    return abs(a - b) < 1e-9


def powiaz_frezowania(baza: B.Baza) -> RaportPowiazania:
    """Laczy z indeksem wiersze ``frezowania`` z plikiem, ktore nie maja projektu (albo wskazuja projekt usuniety z indeksu,
    np. po zmianie nazwy folderu). Wola go odswiezenie puli po indeksowaniu (plik CSV mogl przyjsc przed plikiem STL)."""
    indeks = I.IndeksPlikow(baza)
    r = RaportPowiazania()
    zmiany = []
    for w in baza.wiersze("SELECT id, projekt_id, plik_w_raporcie, data FROM frezowania WHERE plik_w_raporcie IS NOT NULL ORDER BY id"):
        if w["projekt_id"] in indeks.po_id:
            continue
        data = dt.date.fromisoformat(w["data"]) if w["data"] else None
        projekt, kandydatow = indeks.znajdz(w["plik_w_raporcie"], data)
        if projekt is None:
            r.brakujace += 1
            continue
        zmiany.append((projekt["id"], w["id"]))
        r.powiazane += 1
        r.niejednoznaczne += kandydatow > 1
    if zmiany:
        with baza.transakcja():
            for projekt_id, frezowanie_id in zmiany:
                baza.wykonaj("UPDATE frezowania SET projekt_id = ? WHERE id = ?", (projekt_id, frezowanie_id))
            baza.zdarzenie("pula", "powiazanie_frezowan", r.do_slownika())
    return r


def doba_robocza(teraz: dt.datetime, granica_doby_godz: int = GRANICA_DOBY_GODZ) -> dt.date:
    """Data doby roboczej chwili ``teraz`` (doba od ``granica_doby_godz`` do tej samej godziny nastepnego dnia, nazwana data
    poczatku) - ta sama regula co ``session.Sesja.doba`` (sprawdza to test)."""
    return (teraz - dt.timedelta(hours=granica_doby_godz)).date()


def wspolczynnik_krazka(baza: B.Baza, krazek: str | None) -> dict | None:
    """Obowiazujacy wpis reczny krazka (najnowsza data, potem najnowszy wiersz) albo None."""
    k = N.normalizuj_krazek(krazek) if isinstance(krazek, str) else None
    if k is None:
        return None
    return baza.wiersz(f"SELECT id, krazek, wspolczynnik, data FROM frezowania WHERE zrodlo = ? AND plik_w_raporcie IS NULL "
                       f"AND krazek = ? ORDER BY data DESC, id DESC LIMIT 1", (ZRODLO_RECZNY, k))


def wpisz_reczny(baza: B.Baza, krazek: str, wspolczynnik, *, data: str | dt.date | None = None, zmien: bool = False,
                 teraz: dt.datetime | None = None, granica_doby_godz: int = GRANICA_DOBY_GODZ,
                 wspolczynnik_min: float = WSPOLCZYNNIK_MIN, wspolczynnik_max: float = WSPOLCZYNNIK_MAX) -> int:
    """Wpis reczny wspolczynnika krazka (K7, raz na krazek); zwraca id wiersza ``frezowania``.

    ``wspolczynnik``: liczba albo tekst z okna ("1,2250"). ``data``: domyslnie doba robocza chwili ``teraz`` (wpis z 02:00
    na 3. zmianie nalezy do doby poprzedniego dnia). Ta sama wartosc co obowiazujaca = nic nowego (zwraca istniejacy wpis);
    inna = ``BladWspolczynnikow``, chyba ze ``zmien=True``: wpis z tego samego dnia jest poprawiany, z innego - powstaje
    nowy (historia; obowiazuje najnowszy). Wpis trafia do dziennika (krazek, wspolczynnik, data - bez osob).
    """
    k = N.normalizuj_krazek(krazek) if isinstance(krazek, str) else None
    if k is None:
        raise BladWspolczynnikow("podaj oznaczenie krazka (np. K-1101)")
    try:
        w = wspolczynnik_z_tekstu(wspolczynnik, wspolczynnik_min, wspolczynnik_max)
    except ValueError as e:
        raise BladWspolczynnikow(f"krazek {k}: {e}") from None
    teraz = teraz or dt.datetime.now()
    if data is None:
        dzien = doba_robocza(teraz, granica_doby_godz)
    else:
        try:
            dzien = data if isinstance(data, dt.date) else dt.date.fromisoformat(str(data))
        except ValueError:
            raise BladWspolczynnikow(f"krazek {k}: data wpisu nie ma postaci RRRR-MM-DD") from None
    ostatni = wspolczynnik_krazka(baza, k)
    if ostatni is not None and _rowne(ostatni["wspolczynnik"], w):
        return ostatni["id"]
    if ostatni is not None and not zmien:
        raise BladWspolczynnikow(f"krazek {k} ma juz wspolczynnik {format_wspolczynnika(ostatni['wspolczynnik'])} (wpis z "
                                 f"{ostatni['data']}) - zeby zmienic go na {format_wspolczynnika(w)}, potwierdz zmiane")
    czas = teraz.replace(microsecond=0).isoformat()
    with baza.transakcja():
        ten_dzien = baza.wiersz("SELECT id FROM frezowania WHERE zrodlo = ? AND plik_w_raporcie IS NULL AND krazek = ? AND data = ? "
                                "ORDER BY id DESC LIMIT 1", (ZRODLO_RECZNY, k, dzien.isoformat()))
        if ten_dzien is not None:
            baza.wykonaj("UPDATE frezowania SET wspolczynnik = ?, wczytano = ? WHERE id = ?", (w, czas, ten_dzien["id"]))
            nr = ten_dzien["id"]
        else:
            nr = baza.wstaw("frezowania", projekt_id=None, plik_w_raporcie=None, krazek=k, wspolczynnik=w, data=dzien.isoformat(),
                            zrodlo=ZRODLO_RECZNY, raport_plik=None, wczytano=czas)
        baza.zdarzenie("pula", "wspolczynnik_reczny", {"krazek": k, "wspolczynnik": w, "data": dzien.isoformat(), "frezowanie_id": nr,
                                                       "poprzedni": ostatni["wspolczynnik"] if ostatni else None})
    return nr
