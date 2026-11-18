"""wspolczynniki - wspolczynnik skurczu z pliku CSV ``plik;krazek;wspolczynnik;data`` i wpis reczny raz na krazek (E3-A4).

Decyzja wlasciciela DW6 = (c) z 17.11.2026: do czasu parsera raportow MillBox wspolczynnik pracy pochodzi z pliku CSV
wypelnianego przy frezarce ORAZ z wpisu recznego w programie raz na krazek. Oba zrodla to wiersze tabeli ``frezowania``:
- wiersz CSV: ``plik_w_raporcie`` = nazwa pliku STL (moze byc z folderem, ``Folder\\plik.stl``), ``krazek``, ``wspolczynnik``
  (moze byc pusty, gdy podano krazek - wtedy liczy sie wspolczynnik krazka), ``data``, ``zrodlo = csv``, ``raport_plik`` = nazwa
  pliku CSV; ``projekt_id`` = plik z indeksu (``indeks.IndeksPlikow``) albo NULL, gdy pliku jeszcze nie ma w indeksie;
- wpis reczny (rozstrzygniecie koordynatora): wiersz bez pliku - ``plik_w_raporcie`` i ``projekt_id`` NULL, ``krazek``,
  ``wspolczynnik``, ``data`` = doba robocza wpisu, ``zrodlo = reczny`` (``reczny_potwierdzony``, gdy wpisany z ``zmien=True``).
KRAZEK NIEPOWTARZALNY (decyzja wlasciciela A z 17.11.2026, runda 3 - P5): oznaczenie krazka sie nie powtarza, wiec krazek ma
JEDEN wspolczynnik na zawsze, wspolny dla wszystkich jego frezowan z dowolnych dob (``stan_krazkow``): wartosc z wierszy CSV
albo z wpisu recznego - bez limitu dni. Dwie rozne wartosci krazka gdziekolwiek (wiersze CSV z dowolnych dat, CSV kontra wpis
reczny) = SPRZECZNOSC: prace krazka nie dostaja wspolczynnika, az czlowiek potwierdzi jedna wartosc (``wpisz_reczny(...,
zmien=True)`` = ``reczny_potwierdzony``). Potwierdzenie dotyczy calego krazka i jest trwale: kazdy wiersz z ta sama wartoscia
(wczesniejszy i pozniejszy) jest zgodny; wiersz z inna wartoscia zmieniony / dopisany po potwierdzeniu (``wczytano``) = nowa
sprzecznosc (``StanKrazka.sprawa`` - nowa sprawa, jeden wpis w dzienniku).
"Raz na krazek" pilnuje ten modul, nie baza (unikat ``frezowania`` nie obejmuje wierszy z NULL): ta sama wartosc drugi raz =
nic nowego; inna wartosc = odmowa z komunikatem (zawsze - bez limitu dni), chyba ze ``zmien=True`` (ten sam dzien: poprawka
wiersza, inny dzien: nowy wiersz - obowiazuje najnowszy wpis krazka). Wpis z data wczesniejsza niz ostatni = odmowa (D8). Kto
wpisal: ``operator`` w dzienniku (decyzja robocza 5).
PLIK CSV prowadzony dowolnie (decyzja B, runda 3 - P6, D14): tylko rosnie, poprawiany recznie albo czyszczony o dowolnej
porze - wynik nie zalezy od pory czyszczenia. Plik wczytuje sie w calosci albo wcale: bledna linia = ``BladWspolczynnikow``
z numerami linii, w bazie nic; data nieparsowalna i data pozniejsza niz ``PRZYSZLOSC_DNI`` od dzisiaj to blad linii (literowka
roku / miesiaca); wiersz starszy niz ``OKNO_DAT_DNI`` jest POMIJANY (licznik ``stare``) - plik narastajacy nie przestaje sie
wczytywac. Ponowne wczytanie nie dubluje wierszy (klucz: plik, krazek, data). Wiersz z bazy, ktorego klucza nie ma w biezacym
pliku, staje sie ``csv_nieaktualny`` (``projekt_id`` NULL, nie jest kasowany - klucze obce z ``prace``; nie wchodzi do pul)
TYLKO wtedy, gdy plik EWIDENTNIE go poprawil: zawiera wiersz z tym samym plikiem i tym samym krazkiem albo ta sama data
(poprawiona literowka daty albo krazka). Wiersze znikajace bez takiego zastepnika (plik wyczyszczony w calosci albo czesciowo)
zostaja aktualne. Wiersz nieaktualny wraca, gdy wroci do pliku. Powiazanie wiersza z plikiem jest przeliczane przy kazdym
wczytaniu i odswiezeniu (P2) - wynik nie zalezy od kolejnosci, w jakiej pliki trafily do indeksu.

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
ZRODLO_CSV_NIEAKTUALNY = "csv_nieaktualny"  # P6: wiersz pliku CSV poprawiony w pliku (ten sam plik, inny krazek albo data)
ZRODLO_RECZNY = "reczny"
ZRODLO_RECZNY_POTWIERDZONY = "reczny_potwierdzony"  # wpis reczny z zmien=True - rozstrzyga sprzecznosc krazka (P5)
ZRODLA_RECZNE = (ZRODLO_RECZNY, ZRODLO_RECZNY_POTWIERDZONY)
OKNO_DAT_DNI = 60  # D14: wiersz z data starsza niz tyle dni = pominiety (licznik ``stare``), nie blad - plik moze tylko rosnac
PRZYSZLOSC_DNI = 2  # D14: data pozniejsza niz dzisiaj + tyle dni = blad linii (literowka roku albo miesiaca)
GRANICA_DOBY_GODZ = 6
_PORCJA = 500
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
    przywrocone: int = 0  # P3: wiersz nieaktualny, ktory wrocil do pliku
    nieaktualne: int = 0  # P6: wiersze tego pliku poprawione w pliku (ten sam plik, inny krazek albo inna data)
    stare: int = 0  # D14: wiersze z data starsza niz OKNO_DAT_DNI - pominiete (plik narastajacy), nie blad
    powiazane: int = 0  # wiersze pliku powiazane z plikiem z indeksu (po wczytaniu)
    brakujace: int = 0  # wiersze, ktorych pliku nie ma w indeksie
    niejednoznaczne: int = 0  # sama nazwa pliku pasuje do kilku plikow indeksu (wybrany najblizszy dacie)
    po_samej_nazwie: int = 0  # D4: sciezka z folderem spoza zlecen - dopasowano po nazwie pliku
    kodowanie: str = ""

    def do_slownika(self) -> dict:
        return asdict(self)


@dataclass
class RaportPowiazania:
    powiazane: int = 0
    brakujace: int = 0
    niejednoznaczne: int = 0
    zmienione: int = 0  # P2: wiersze, ktorych powiazanie sie zmienilo (tez na brak)
    po_samej_nazwie: int = 0

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


def wczytaj_csv(plik: str | Path, *, dzis: dt.date | None = None, okno_dat_dni: int = OKNO_DAT_DNI,
                przyszlosc_dni: int = PRZYSZLOSC_DNI, wspolczynnik_min: float = WSPOLCZYNNIK_MIN,
                wspolczynnik_max: float = WSPOLCZYNNIK_MAX) -> list[WierszCsv]:
    """Wiersze pliku CSV (srednik, naglowek ``plik;krazek;wspolczynnik;data`` w pierwszej niepustej linii, UTF-8 albo cp1250,
    przecinek dziesietny dozwolony, data RRRR-MM-DD albo DD.MM.RRRR nie pozniejsza niz ``dzis`` (domyslnie dzisiaj) +
    ``przyszlosc_dni``, puste linie i puste pola na koncu wiersza - srednik na koncu z Excela - pomijane). Wiersze z data
    starsza niz ``okno_dat_dni`` sa pomijane (D14 - plik narastajacy; ``wczytaj_do_bazy`` je liczy). Kazdy blad =
    ``BladWspolczynnikow`` z numerami WSZYSTKICH blednych linii (do ``BLEDOW_W_KOMUNIKACIE`` w tresci)."""
    wiersze, _, _ = _wczytaj_csv(Path(plik), wspolczynnik_min, wspolczynnik_max, dzis or dt.date.today(), okno_dat_dni,
                                 przyszlosc_dni)
    return wiersze


def _bez_pustych_na_koncu(pola: list[str]) -> list[str]:
    """Excel zapisuje srednik na koncu wiersza (puste piate pole) - puste pola za czwartym sa pomijane (D7)."""
    while len(pola) > len(NAGLOWEK) and not pola[-1].strip():
        pola = pola[:-1]
    return pola


def _wczytaj_csv(plik: Path, wspolczynnik_min: float, wspolczynnik_max: float, dzis: dt.date, okno_dat_dni: int,
                 przyszlosc_dni: int) -> tuple[list[WierszCsv], list[WierszCsv], str]:
    """(wiersze do wczytania, wiersze pominiete jako starsze niz ``okno_dat_dni``, kodowanie)."""
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
    stare: list[WierszCsv] = []
    klucze: dict[tuple, WierszCsv] = {}
    naglowek_ok = False
    for pola in czytnik:
        linia = czytnik.line_num
        pola = _bez_pustych_na_koncu(pola)
        if not naglowek_ok and not any(p.strip() for p in pola):
            continue  # pusta linia przed naglowkiem (D7)
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
        if (data - dzis).days > przyszlosc_dni:
            bledy.append((linia, f"data z przyszlosci (pozniej niz {przyszlosc_dni} dni od dzisiaj) - sprawdz rok i miesiac"))
            continue
        if wsp is None and krazek is None:
            bledy.append((linia, "pusty wspolczynnik i pusty krazek - podaj wspolczynnik albo krazek (wspolczynnik krazka "
                                 "wpisuje sie w programie)"))
            continue
        w = WierszCsv(linia, nazwa, krazek, wsp, data)
        if (dzis - data).days > okno_dat_dni:
            stare.append(w)  # D14: plik narastajacy - wiersz spoza okna pomijany (licznik), nie blad
            continue
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
    return wiersze, stare, kodowanie


def wczytaj_do_bazy(baza: B.Baza, plik: str | Path, *, teraz: dt.datetime | None = None, okno_dat_dni: int = OKNO_DAT_DNI,
                    przyszlosc_dni: int = PRZYSZLOSC_DNI, wspolczynnik_min: float = WSPOLCZYNNIK_MIN,
                    wspolczynnik_max: float = WSPOLCZYNNIK_MAX) -> RaportCsv:
    """Wczytuje plik CSV do ``frezowania`` (w jednej transakcji, calosc albo nic) i laczy wiersze z indeksem.

    Wiersz o kluczu (plik, krazek, data), ktory juz jest w bazie: bez zmian albo poprawiony wspolczynnik (wiersze z innego
    zrodla, np. raportu MillBox, nie sa nadpisywane); powiazanie z plikiem liczone od nowa (P2). Wiersz tego pliku CSV
    (``raport_plik``), ktorego klucza nie ma w pliku, = ``csv_nieaktualny`` TYLKO, gdy plik ma wiersz z tym samym plikiem
    i tym samym krazkiem albo ta sama data (P6: ewidentna poprawka literowki daty / krazka; wiersze bez zastepnika - plik
    wyczyszczony o dowolnej porze - zostaja); wiersz nieaktualny, ktory wrocil do pliku = znow ``csv``. Data pozniejsza niz
    ``przyszlosc_dni`` od ``teraz`` = blad linii; starsza niz ``okno_dat_dni`` = wiersz pominiety (``stare``, D14), ale nadal
    "w pliku" (jego wiersz w bazie nie staje sie nieaktualny). Bledny plik = ``BladWspolczynnikow``, w bazie nic.
    """
    plik = Path(plik)
    teraz = teraz or dt.datetime.now()
    wiersze, stare, kodowanie = _wczytaj_csv(plik, wspolczynnik_min, wspolczynnik_max, teraz.date(), okno_dat_dni, przyszlosc_dni)
    czas = teraz.replace(microsecond=0).isoformat()
    indeks = I.IndeksPlikow(baza)
    w_bazie = baza.wiersze("SELECT * FROM frezowania WHERE plik_w_raporcie IS NOT NULL ORDER BY id")
    istniejace = {(N.klucz_pliku(w["plik_w_raporcie"]), w["krazek"], w["data"]): w for w in w_bazie}
    w_pliku = {(N.klucz_pliku(w.plik), w.krazek, w.data.isoformat()) for w in wiersze + stare}  # DANE OSOBOWE: tylko w pamieci
    plik_krazek = {(p, k) for p, k, _ in w_pliku}
    plik_data = {(p, d) for p, _, d in w_pliku}
    dopasowane: set[int] = set()  # id wierszy bazy, ktore sa w biezacym pliku
    r = RaportCsv(wierszy=len(wiersze), stare=len(stare), kodowanie=kodowanie)
    with baza.transakcja():
        for w in wiersze:
            d = indeks.dopasuj(w.plik, w.data)
            projekt_id = d.wiersz["id"] if d.wiersz else None
            r.niejednoznaczne += d.kandydatow > 1
            r.po_samej_nazwie += d.po_nazwie
            r.powiazane += projekt_id is not None
            r.brakujace += projekt_id is None
            stary = istniejace.get((N.klucz_pliku(w.plik), w.krazek, w.data.isoformat()))
            if stary is None:
                baza.wstaw("frezowania", projekt_id=projekt_id, plik_w_raporcie=w.plik, krazek=w.krazek, wspolczynnik=w.wspolczynnik,
                           data=w.data.isoformat(), zrodlo=ZRODLO_CSV, raport_plik=plik.name, wczytano=czas)
                r.nowe += 1
                continue
            dopasowane.add(stary["id"])
            if stary["zrodlo"] == ZRODLO_CSV_NIEAKTUALNY:
                baza.wykonaj("UPDATE frezowania SET zrodlo = ?, wspolczynnik = ?, raport_plik = ?, wczytano = ?, projekt_id = ? WHERE id = ?",
                             (ZRODLO_CSV, w.wspolczynnik, plik.name, czas, projekt_id, stary["id"]))
                r.przywrocone += 1
                continue
            if stary["projekt_id"] != projekt_id:
                baza.wykonaj("UPDATE frezowania SET projekt_id = ? WHERE id = ?", (projekt_id, stary["id"]))
            if stary["zrodlo"] == ZRODLO_CSV and not _rowne(stary["wspolczynnik"], w.wspolczynnik):
                baza.wykonaj("UPDATE frezowania SET wspolczynnik = ?, wczytano = ? WHERE id = ?", (w.wspolczynnik, czas, stary["id"]))
                r.zmienione += 1
            else:
                r.bez_zmian += 1
        for s in w_bazie:  # P6: nieaktualny tylko wiersz, ktory plik ewidentnie poprawil (nie zalezy od daty ani pory czyszczenia)
            if s["zrodlo"] != ZRODLO_CSV or s["raport_plik"] != plik.name or s["id"] in dopasowane:
                continue
            p = N.klucz_pliku(s["plik_w_raporcie"])
            if (p, s["krazek"], s["data"]) in w_pliku:
                continue  # D14: wiersz nadal w pliku, tylko pominiety jako stary
            if (p, s["krazek"]) in plik_krazek or (p, s["data"]) in plik_data:
                baza.wykonaj("UPDATE frezowania SET zrodlo = ?, projekt_id = NULL WHERE id = ?", (ZRODLO_CSV_NIEAKTUALNY, s["id"]))
                r.nieaktualne += 1
        baza.zdarzenie("pula", "wspolczynniki_csv", r.do_slownika())
    return r


def pliki_frezowan(baza: B.Baza, pierwsza: str, ostatnia: str) -> set[str]:
    """Nazwy plikow z aktualnych wierszy frezowania z dat ``pierwsza``-``ostatnia`` (ISO) - do indeksu folderow starych (D3).
    DANE OSOBOWE: tylko w pamieci."""
    return {w["plik_w_raporcie"] for w in baza.wiersze(
        "SELECT plik_w_raporcie FROM frezowania WHERE plik_w_raporcie IS NOT NULL AND data >= ? AND data <= ? "
        "AND (zrodlo IS NULL OR zrodlo != ?)", (pierwsza, ostatnia, ZRODLO_CSV_NIEAKTUALNY))}


def _rowne(a: float | None, b: float | None) -> bool:
    if a is None or b is None:
        return a is None and b is None
    return abs(a - b) < 1e-9


def powiaz_frezowania(baza: B.Baza, *, okno: tuple[str, str] | None = None) -> RaportPowiazania:
    """Laczy z indeksem aktualne wiersze ``frezowania`` z plikiem. Wiersze z dat ``okno`` (pierwsza, ostatnia - okno puli
    wieczornej) sa laczone ZAWSZE od nowa (P2: wlasciwy plik mogl trafic do indeksu pozniej niz wiersz CSV - wynik jak na
    swiezej bazie); pozostale tylko, gdy nie maja projektu albo wskazuja projekt usuniety z indeksu (np. po zmianie nazwy
    folderu). Wola go odswiezenie puli po indeksowaniu (plik CSV mogl przyjsc przed plikiem STL)."""
    indeks = I.IndeksPlikow(baza)
    r = RaportPowiazania()
    zmiany = []
    for w in baza.wiersze("SELECT id, projekt_id, plik_w_raporcie, data FROM frezowania WHERE plik_w_raporcie IS NOT NULL "
                          "AND (zrodlo IS NULL OR zrodlo != ?) ORDER BY id", (ZRODLO_CSV_NIEAKTUALNY,)):
        w_oknie = okno is not None and w["data"] is not None and okno[0] <= w["data"] <= okno[1]
        if not w_oknie and w["projekt_id"] in indeks.po_id:
            continue
        data = dt.date.fromisoformat(w["data"]) if w["data"] else None
        d = indeks.dopasuj(w["plik_w_raporcie"], data)
        if d.wiersz is None:
            r.brakujace += 1
            if w_oknie and w["projekt_id"] is not None:
                zmiany.append((None, w["id"]))
                r.zmienione += 1
            continue
        r.powiazane += 1
        r.niejednoznaczne += d.kandydatow > 1
        r.po_samej_nazwie += d.po_nazwie
        if d.wiersz["id"] != w["projekt_id"]:
            zmiany.append((d.wiersz["id"], w["id"]))
            r.zmienione += 1
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


_RECZNE_SQL = f"zrodlo IN ({', '.join('?' * len(ZRODLA_RECZNE))}) AND plik_w_raporcie IS NULL"


def wspolczynnik_krazka(baza: B.Baza, krazek: str | None) -> dict | None:
    """Ostatni wpis reczny krazka (najnowsza data, potem najnowszy wiersz) albo None - obowiazuje bez limitu dni. Wspolczynnik
    krazka razem z wierszami CSV i sprzecznoscia podaje ``stan_krazkow``."""
    k = N.normalizuj_krazek(krazek) if isinstance(krazek, str) else None
    if k is None:
        return None
    return baza.wiersz(f"SELECT id, krazek, wspolczynnik, data, zrodlo, wczytano FROM frezowania WHERE {_RECZNE_SQL} "
                       f"AND krazek = ? ORDER BY data DESC, id DESC LIMIT 1", (*ZRODLA_RECZNE, k))


def wpisy_reczne(baza: B.Baza) -> dict[str, list[dict]]:
    """Krazek -> wpisy reczne rosnaco (data, id)."""
    wynik: dict[str, list[dict]] = {}
    for w in baza.wiersze(f"SELECT id, krazek, wspolczynnik, data, zrodlo, wczytano FROM frezowania WHERE {_RECZNE_SQL} "
                          f"AND krazek IS NOT NULL ORDER BY data, id", ZRODLA_RECZNE):
        wynik.setdefault(w["krazek"], []).append(w)
    return wynik


@dataclass(frozen=True)
class StanKrazka:
    """Wspolczynnik krazka w modelu "krazek niepowtarzalny" (decyzja wlasciciela A, 17.11.2026). Bez nazw plikow."""
    krazek: str
    wspolczynnik: float | None  # obowiazuje dla WSZYSTKICH frezowan krazka; None = brak wartosci albo sprzecznosc
    zrodlo: str | None  # "csv" (wartosc tylko z wierszy z plikiem), "reczny" (wpis reczny / potwierdzenie) albo None
    sprzeczny: bool  # dwie rozne wartosci (nierozstrzygniete albo nowe po potwierdzeniu)
    wartosci_csv: tuple[float, ...]  # rozne wartosci z aktualnych wierszy z plikiem, z dowolnych dat
    reczny: dict | None  # ostatni wpis reczny (id, krazek, wspolczynnik, data, zrodlo, wczytano)
    potwierdzony: dict | None  # ostatni wpis z ``zmien=True`` (rozstrzygniecie), gdy jest
    sprawa: str | None  # znacznik sprzecznosci "krazek|czas potwierdzenia" (pusty, gdy bez potwierdzenia): ta sama sprawa =
    #                     jeden wpis w dzienniku (``pula.KatalogPul.odswiez``)


_POLA_WPISU = ("id", "krazek", "wspolczynnik", "data", "zrodlo", "wczytano")


def _r6(wartosc) -> float:
    return round(float(wartosc), 6)


def _stan(krazek: str, reczne: list[dict], inne: list[dict]) -> StanKrazka:
    """Regula P5 (runda 3): jedna wartosc krazka z dowolnych dat albo sprzecznosc; potwierdzenie (``reczny_potwierdzony``)
    obowiazuje dla calego krazka i trwale - nowa sprzecznosc tworzy tylko inna wartosc zmieniona / dopisana po nim."""
    z_wartoscia = [f for f in inne if f["wspolczynnik"] is not None]
    wartosci_csv = tuple(sorted({_r6(f["wspolczynnik"]) for f in z_wartoscia}))
    reczny = reczne[-1] if reczne else None
    nr = max((i for i, r in enumerate(reczne) if r["zrodlo"] == ZRODLO_RECZNY_POTWIERDZONY), default=None)
    if nr is not None:
        potw = reczne[nr]
        c, znacznik = _r6(potw["wspolczynnik"]), potw["wczytano"] or ""
        pozniejsze = [f for f in z_wartoscia if (f["wczytano"] or "") > znacznik] + reczne[nr + 1:]
        if any(_r6(f["wspolczynnik"]) != c for f in pozniejsze):
            return StanKrazka(krazek, None, None, True, wartosci_csv, reczny, potw, f"{krazek}|{znacznik}")
        return StanKrazka(krazek, float(potw["wspolczynnik"]), ZRODLO_RECZNY, False, wartosci_csv, reczny, potw, None)
    if len(set(wartosci_csv) | {_r6(r["wspolczynnik"]) for r in reczne}) > 1:
        return StanKrazka(krazek, None, None, True, wartosci_csv, reczny, None, f"{krazek}|")
    if reczny is not None:
        return StanKrazka(krazek, float(reczny["wspolczynnik"]), ZRODLO_RECZNY, False, wartosci_csv, reczny, None, None)
    if z_wartoscia:
        return StanKrazka(krazek, float(z_wartoscia[0]["wspolczynnik"]), ZRODLO_CSV, False, wartosci_csv, None, None, None)
    return StanKrazka(krazek, None, None, False, (), None, None, None)


def stan_krazkow(baza: B.Baza, krazki=None) -> dict[str, StanKrazka]:
    """Krazek -> ``StanKrazka`` z WSZYSTKICH aktualnych wierszy krazka (CSV / raport z dowolnych dat i wpisy reczne; bez
    ``csv_nieaktualny``); ``krazki`` = ktore krazki (domyslnie wszystkie). Krazek bez zadnego wiersza nie wystepuje w wyniku."""
    sql = ("SELECT id, krazek, wspolczynnik, data, zrodlo, wczytano, plik_w_raporcie IS NULL AS bez_pliku FROM frezowania "
           "WHERE krazek IS NOT NULL AND (zrodlo IS NULL OR zrodlo != ?)")
    if krazki is None:
        wiersze = baza.wiersze(sql, (ZRODLO_CSV_NIEAKTUALNY,))
    else:
        lista, wiersze = sorted({k for k in krazki if k is not None}), []
        for i in range(0, len(lista), _PORCJA):
            czesc = lista[i:i + _PORCJA]
            wiersze += baza.wiersze(f"{sql} AND krazek IN ({', '.join('?' * len(czesc))})", (ZRODLO_CSV_NIEAKTUALNY, *czesc))
    grupy: dict[str, tuple[list, list]] = {}
    for w in sorted(wiersze, key=lambda w: (w["data"] or "", w["id"])):
        reczne, inne = grupy.setdefault(w["krazek"], ([], []))
        if w["bez_pliku"] and w["zrodlo"] in ZRODLA_RECZNE:
            reczne.append({p: w[p] for p in _POLA_WPISU})
        else:
            inne.append(w)
    return {k: _stan(k, reczne, inne) for k, (reczne, inne) in grupy.items()}


def wpisz_reczny(baza: B.Baza, krazek: str, wspolczynnik, *, operator: str, data: str | dt.date | None = None,
                 zmien: bool = False, teraz: dt.datetime | None = None, granica_doby_godz: int = GRANICA_DOBY_GODZ,
                 wspolczynnik_min: float = WSPOLCZYNNIK_MIN, wspolczynnik_max: float = WSPOLCZYNNIK_MAX) -> int:
    """Wpis reczny wspolczynnika krazka (K7, raz na krazek); zwraca id wiersza ``frezowania``.

    ``operator`` (wymagany, decyzja robocza 5): kto wpisuje - trafia do dziennika ``zdarzenia`` (schemat bez zmian).
    ``wspolczynnik``: liczba albo tekst z okna ("1,2250"). ``data``: domyslnie doba robocza chwili ``teraz`` (wpis z 02:00
    na 3. zmianie nalezy do doby poprzedniego dnia); wczesniejsza niz data ostatniego wpisu krazka = odmowa (D8). Krazek ma
    juz wpis (z dowolnego dnia - krazek niepowtarzalny, decyzja A): ta sama wartosc = nic nowego (zwraca istniejacy wpis),
    inna = ``BladWspolczynnikow`` z obecna wartoscia, chyba ze ``zmien=True``. ``zmien=True``: wpis z tego samego dnia jest
    poprawiany, z innego - powstaje nowy (historia; obowiazuje najnowszy), w obu razach ``zrodlo = reczny_potwierdzony`` -
    potwierdzona wartosc obowiazuje dla WSZYSTKICH prac krazka i rozstrzyga sprzecznosc z wierszami CSV wczytanymi przed nia
    (P5, ``stan_krazkow``). Wpis bez potwierdzenia inny niz wartosc w CSV jest przyjmowany, ale daje sprzecznosc krazka.
    """
    k = N.normalizuj_krazek(krazek) if isinstance(krazek, str) else None
    if k is None:
        raise BladWspolczynnikow("podaj oznaczenie krazka (np. K-1101)")
    kto = " ".join(operator.split()) if isinstance(operator, str) else ""
    if not kto:
        raise BladWspolczynnikow(f"krazek {k}: wybierz operatora (kto wpisuje wspolczynnik)")
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
    if ostatni is not None and dzien < dt.date.fromisoformat(ostatni["data"]):
        raise BladWspolczynnikow(f"krazek {k} ma pozniejszy wpis z {ostatni['data']} - wpis z data {dzien.isoformat()} nie "
                                 f"obowiazywalby; wpisz wspolczynnik z data dzisiejsza")
    if ostatni is not None and not zmien:
        if _rowne(ostatni["wspolczynnik"], w):
            return ostatni["id"]
        raise BladWspolczynnikow(f"krazek {k} ma juz wspolczynnik {format_wspolczynnika(ostatni['wspolczynnik'])} (wpis z "
                                 f"{ostatni['data']}) - zeby zmienic go na {format_wspolczynnika(w)}, potwierdz zmiane "
                                 f"(dotyczy wszystkich prac tego krazka)")
    zrodlo = ZRODLO_RECZNY_POTWIERDZONY if zmien else ZRODLO_RECZNY
    czas = teraz.replace(microsecond=0).isoformat()
    with baza.transakcja():
        ten_dzien = baza.wiersz(f"SELECT id FROM frezowania WHERE {_RECZNE_SQL} AND krazek = ? AND data = ? ORDER BY id DESC LIMIT 1",
                                (*ZRODLA_RECZNE, k, dzien.isoformat()))
        if ten_dzien is not None:
            baza.wykonaj("UPDATE frezowania SET wspolczynnik = ?, zrodlo = ?, wczytano = ? WHERE id = ?", (w, zrodlo, czas, ten_dzien["id"]))
            nr = ten_dzien["id"]
        else:
            nr = baza.wstaw("frezowania", projekt_id=None, plik_w_raporcie=None, krazek=k, wspolczynnik=w, data=dzien.isoformat(),
                            zrodlo=zrodlo, raport_plik=None, wczytano=czas)
        baza.zdarzenie("pula", "wspolczynnik_reczny", {"krazek": k, "wspolczynnik": w, "data": dzien.isoformat(), "frezowanie_id": nr,
                                                       "poprzedni": ostatni["wspolczynnik"] if ostatni else None, "zmien": bool(zmien),
                                                       "operator": kto})
    return nr
