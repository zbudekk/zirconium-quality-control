"""excel - wybor wiersza arkusza zlecen bez Excela (reguly 1-5), log CSV (regula 6), tryby "pytaj" i "cien" (E3-A9).

Zrodlo regul: plan wdrozenia v2, "Dane i integracje" ("Excel produkcyjny", "Reguly znalezienia wiersza" 1-6); plan etapu 3:
X1-X8 (sekcja 3.3), tabela ``excel_zapisy`` (3.4), DW10 (etap 3: wylacznie "pytaj przed zapisem" i "cien" - bez zapisu
samodzielnego). Wejscie: wynik "Zamknij piec" z ``session_rano`` (``kompletne`` = lista dla Excela, ``poprawki`` = tylko log)
i nazwa folderu zlecenia z tabeli ``zlecenia`` (DW2). Wyjscie: propozycja wiersza (klasa: jeden wiersz / juz odhaczone / wskaz
wiersz z lista kandydatow), po zatwierdzeniu przez czlowieka kolor pola B jednej komorki, wpis w ``log_excel.csv``
i w ``excel_zapisy``.

Warstwy: ten modul nie zna COM - arkusz to obiekt z interfejsem ``ZrodloArkusza`` (cztery metody + nazwy skoroszytu i arkusza).
Na laptopie z Excelem dostarcza go ``excel_com.polacz`` (pywin32, Excel juz otwarty z Autozapisem); w testach - atrapa
``narzedzia/arkusz_syntetyczny.ArkuszWPamieci``. Odczyt kolumn A-I do pamieci (``IndeksArkusza``: slownik kuweta -> wiersze;
niezmienione wiersze z pamieci podrecznej poprzedniego odczytu), wyszukanie bez Excela; kolor pola B czytany na zywo tylko
dla kandydatow.

Bezpieczenstwo zapisu (zero zapisow w zlym wierszu; runda 2 po recenzji PR #27): propozycja i zatwierdzenie zawsze na swiezym
odczycie arkusza (P1); zapis tylko przez ``Excel.zatwierdz`` (czlowiek zatwierdza - tryb "pytaj"), tylko dla pozycji
z zamknietego pieca (X4); tryb "cien" nie zapisuje niczego (tylko log). Kazda proba zapisu to CALY krok: swiezy odczyt, ten
sam skoroszyt i arkusz co przy propozycji (P2), wiersz i jego sasiedzi rowni migawce, propozycja policzona od nowa rowna
pierwotnej, pole B bez koloru, dopiero wtedy kolor; odrzucone wywolanie COM = ponowienie calego kroku (B1). Po zapisie wiersze
N-1..N+1 i kolor sa czytane ponownie; roznica = wpis ``blad`` i komunikat "sprawdz recznie". Pole B juz zielone = tylko log
(regula 4); inny kolor = program go nie nadpisuje; wiersz wskazany recznie musi byc na liscie kandydatow; jedna pozycja = jeden
zapis. Bezpieczniki regul (P3): wybrany wiersz starszy niz ``[excel] maks_wiek_dni`` albo bez daty, nowszy nieodhaczony wiersz
tej kuwety - "wskaz wiersz". Zapis = wylacznie wypelnienie jednej komorki kolumny B (``ustaw_wypelnienie``).

Zalozenia o arkuszu - jedno miejsce: ``ZALOZENIA_ARKUSZA`` + klucze ``[excel]`` w ``ustawienia.toml``; struktura
prawdziwego pliku jest nieznana (plan etapu 3: D2, X8) - do potwierdzenia na kopii pliku produkcyjnego.
DANE OSOBOWE: nazwa folderu (i kolumna H w pamieci) trafia tylko do ``log_excel.csv`` (wymaga tego regula 6) i do
``excel_zapisy.folder`` (DW2); wyniki metod dla programu (``POLA_WYNIKU``), komunikaty, powody i wyjatki tego modulu nie
zawieraja nazw ani nazwisk. Tylko biblioteka standardowa (pywin32 - wylacznie w ``excel_com``). Opis i API dla A12:
``opisy_modulow/excel.md``.
"""
from __future__ import annotations

import csv
import datetime as dt
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Protocol

from . import baza as B, nazwy as N

# ===== ZALOZENIA O ARKUSZU - JEDNO MIEJSCE (plan etapu 3: D2, X8 - DO POTWIERDZENIA NA KOPII PLIKU PRODUKCYJNEGO) =========
# Litery kolumn A, B, C, H, pierwszy wiersz, arkusz, skoroszyt i limit wieku sa w [excel] ustawien (wartosci domyslne nizej
# i w ustawienia.przyklad.toml). Reszta - tutaj.
ZALOZENIA_ARKUSZA = {
    "kolumny": "program czyta kolumny A-I biezacego arkusza (plan wdrozenia: 'Excel produkcyjny'); D-G i I - znaczenie nieznane, nieuzywane",
    "A": "data zlecenia (regula 3: najnowsza data; limit wieku); komorka daty (COM: datetime), tekst dd.mm.rrrr / rrrr-mm-dd albo numer "
         "seryjny daty; data pozniejsza niz jutro = brak daty (literowka roku)",
    "B": "numer zlecenia (do logu, regula 6) i pole odhaczenia: wypelnienie [excel] kolor_rgb (198, 239, 206) = odhaczone",
    "C": "numer kuwety: rowny DOKLADNIE (regula 1), zera wiodace i spacje bez znaczenia; '13263', '3263/2' to nie kuweta 3263",
    "H": "nazwa zlecenia jak nazwa folderu (regula 2), nazwisko (regula 3), numer zlecenia prywatnego '#1234' (K12)",
    "wiersz 1": "naglowek; dane od [excel] pierwszy_wiersz (2) do ostatniego uzytego wiersza",
    "arkusz": "[excel] arkusz albo aktywny arkusz; [excel] skoroszyt albo aktywny skoroszyt (Excel otwarty z Autozapisem - X1); "
              "puste ustawienie = ostrzezenie z nazwami faktycznie uzytymi",
    "kolejnosc wierszy": "bez zalozenia - regula 3 liczy z dat; wiersz bez daty PONIZEJ wybranego = moze byc nowszy",
    "pole B w innym kolorze": "kolor inny niz zielony i bialy = cudze oznaczenie: program go nie nadpisuje (wskaz wiersz)",
    "zlecenie prywatne": "numer '#1234' szukany w kolumnie B (tylko wiersze bez kuwety w C - wiersze zlecen prywatnych) albo "
                         "'#1234' w H; jeden wiersz w limicie wieku = propozycja (K12, D5)",
    "nazwisko z folderu": "slowa (min. 2 litery) przed numerem kuwety; gdy folder zaczyna sie numerem - pierwsze slowo po nim (bez KODY_PRACY)",
    "limit wieku": "wybrany wiersz starszy niz [excel] maks_wiek_dni (60) albo bez daty = wskaz wiersz (bezpiecznik P3; 0 = bez limitu)",
    "nowszy otwarty wiersz": "nowszy wiersz tej samej kuwety bez zielonego B (takze bez daty ponizej) = wskaz wiersz (bezpiecznik P3)",
}
OSTATNIA_KOLUMNA = "I"  # zakres odczytu A..I (szerszy, gdy ktoras kolumna z ustawien lezy dalej)
MAKS_KOLUMNA = 16384  # XFD - ostatnia kolumna Excela
ZIELONY = (198, 239, 206)  # domyslny [excel] kolor_rgb
BIALY = (255, 255, 255)  # biale wypelnienie = jak brak wypelnienia
KODY_PRACY = ("zs", "zr", "kor", "pg", "ab", "zs1")  # kody literowe w nazwach folderow (nie nazwisko) - lista do uzupelnienia (D3)
DATA_SERYJNA_MIN, DATA_SERYJNA_MAX = 29221, 73050  # numer seryjny daty Excela: 1980-01-01 ... 2099-12-31
_EPOKA_EXCELA = dt.date(1899, 12, 30)
_FORMATY_DATY = ("%d.%m.%Y", "%Y-%m-%d", "%d.%m.%y", "%d-%m-%Y", "%d/%m/%Y", "%Y.%m.%d", "%d-%m-%y", "%d/%m/%y")
PONOWIENIA_ZAPISU = 3  # proby calego kroku zapisu (Excel odrzuca wywolania COM, gdy jest zajety - B1)
PRZERWA_PONOWIENIA_S = 0.5  # przerwa PRZED kolejnym swiezym odczytem (nie miedzy kontrola a zapisem)

# tryby (DW10: w etapie 3 bez zapisu samodzielnego - "auto" dopiero po audycie 50 z 50, etap 4)
TRYB_PYTAJ = "pytaj"  # domyslny: zapis dopiero po zatwierdzeniu przez czlowieka (Excel.zatwierdz)
TRYB_CIEN = "cien"  # nic nie zapisuje w Excelu; log porownawczy (co program by zaznaczyl)
TRYBY = (TRYB_PYTAJ, TRYB_CIEN)

# klasy propozycji (kryterium 1 E3-A9)
KLASA_JEDEN_WIERSZ = "jeden_wiersz"
KLASA_JUZ_ODHACZONE = "juz_odhaczone"
KLASA_WSKAZ_WIERSZ = "wskaz_wiersz"
KLASY = (KLASA_JEDEN_WIERSZ, KLASA_JUZ_ODHACZONE, KLASA_WSKAZ_WIERSZ)

# excel_zapisy.wynik (plan 3.4)
WYNIK_ZAPISANO = "zapisano"
WYNIK_JUZ_ODHACZONE = "juz_odhaczone"
WYNIK_WSKAZANO = "wskazano_recznie"
WYNIK_POMINIETO = "pominieto"
WYNIK_TYLKO_LOG = "tylko_log"
WYNIK_BLAD = "blad"
STAN_ZAPISANO_BEZ_CSV = "zapisano bez logu CSV"  # Pozycja.stan: kolor zapisany, wpis tylko w excel_zapisy (P5)

# log CSV: pola reguly 6 (w tej kolejnosci) + skoroszyt (P2) + regula, wynik, tryb (jak excel_zapisy)
POLA_REGULY_6 = ("data", "godzina", "kuweta", "folder", "numer_zlecenia_b", "arkusz", "wiersz", "kto_zatwierdzil")
POLA_LOGU = POLA_REGULY_6 + ("skoroszyt", "regula", "wynik", "tryb")
# wynik metod dla programu (A12) - BEZ nazwy folderu i nazwisk (P4); "id" = id wiersza excel_zapisy (None bez bazy)
POLA_WYNIKU = ("id", "kuweta", "wiersz", "klasa", "wynik", "regula", "tryb", "zlecenie_id", "sesja_pieca_id")

_TOKEN = re.compile(r"[^\W\d_]+|\d+")  # slowa z liter i liczby (separator: wszystko inne, takze "_", "-", ".")
_CYFRY = re.compile(r"[0-9]+")
_PRYWATNY = re.compile(r"#\s*([0-9]+)")


class BladExcela(RuntimeError):
    """Odmowa albo blad modulu Excela; komunikat dla czlowieka, bez nazw folderow i nazwisk."""


class ZrodloArkusza(Protocol):
    """Interfejs arkusza (``excel_com.ArkuszCom`` na laptopie, ``ArkuszWPamieci`` w testach). Kolumny i wiersze od 1."""

    nazwa: str  # nazwa arkusza (do logu)
    skoroszyt: str  # nazwa skoroszytu (Workbook.Name) - do logu i kontroli przed zapisem (P2)
    sciezka: str  # pelna sciezka skoroszytu (Workbook.FullName) - tylko kontrola przed zapisem, nie do logu

    def odczytaj(self, pierwszy_wiersz: int, ostatnia_kolumna: int) -> list[tuple]:
        """Wartosci wierszy od ``pierwszy_wiersz`` do ostatniego uzytego, kolumny 1..``ostatnia_kolumna``."""

    def wiersz(self, nr: int, ostatnia_kolumna: int) -> tuple:
        """Wartosci jednego wiersza (kontrola po zapisie)."""

    def wypelnienie(self, nr: int, kolumna: int) -> tuple[int, int, int] | None:
        """Kolor wypelnienia komorki (R, G, B) albo None (bez wypelnienia)."""

    def ustaw_wypelnienie(self, nr: int, kolumna: int, rgb: tuple[int, int, int]) -> None:
        """Jedyny zapis: kolor wypelnienia jednej komorki; jedna proba (blad = wyjatek, bez ponowien)."""


def numer_kolumny(litery: str) -> int:
    """Litery kolumny Excela -> numer od 1 ("A" = 1, "H" = 8, "AA" = 27, "XFD" = 16384 - ostatnia)."""
    t = str(litery).strip().upper()
    if not (t.isascii() and t.isalpha() and 1 <= len(t) <= 3):
        raise BladExcela(f"zla litera kolumny {litery!r} (oczekiwano np. C)")
    n = 0
    for z in t:
        n = n * 26 + ord(z) - 64
    if n > MAKS_KOLUMNA:
        raise BladExcela(f"zla litera kolumny {litery!r} (Excel konczy sie na XFD)")
    return n


# --- normalizacja komorek ---------------------------------------------------------------------------------------------
def norm_kuweta(v: Any) -> str | None:
    """Kolumna C -> numer kuwety do porownan (regula 1, dokladnie): 3263.0 / " 03263 " -> "3263"; "#1234" -> "#1234";
    inna tresc ("13263" -> "13263", "3263/2", "3263a") zostaje soba, wiec nie zgodzi sie z kuweta 3263; puste -> None."""
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, float):
        return N.postac_numeru(str(int(v))) if v.is_integer() and v >= 0 else str(v)
    if isinstance(v, int):
        return N.postac_numeru(str(v)) if v >= 0 else str(v)
    t = N.nfc(str(v)).strip()
    if not t:
        return None
    if _CYFRY.fullmatch(t):
        return N.postac_numeru(t)
    m = _PRYWATNY.fullmatch(t)
    if m:
        return N.PRYWATNE + m.group(1)
    return t.lower()


def norm_numer(v: Any) -> str:
    """Kolumna B (numer zlecenia) jako tekst do logu: 40123.0 (liczba z COM) -> "40123"; puste -> ""."""
    if v is None or isinstance(v, bool):
        return ""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    if isinstance(v, (int, float)):
        return str(v)
    return N.nfc(str(v)).strip()


def norm_nazwa(v: Any) -> str:
    """Kolumna H do porownan z nazwa folderu (regula 2): ``nazwy.znormalizuj`` (male litery, pojedyncze spacje, bez zer
    wiodacych w liczbach, NFC); puste -> ""."""
    if v is None or isinstance(v, bool):
        return ""
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return N.znormalizuj(str(v))


def tokeny(tekst: str) -> frozenset[str]:
    """Slowa i liczby tekstu znormalizowanego (do sprawdzenia, czy nazwisko wystepuje w H)."""
    return frozenset(_TOKEN.findall(tekst))


def data_z_komorki(v: Any) -> dt.date | None:
    """Kolumna A -> data: ``datetime``/``date`` (COM), numer seryjny Excela, tekst dd.mm.rrrr, rrrr-mm-dd, dd.mm.rr, dd/mm/rrrr."""
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, dt.datetime):
        return v.date()
    if isinstance(v, dt.date):
        return v
    if isinstance(v, (int, float)):
        return _EPOKA_EXCELA + dt.timedelta(days=int(v)) if DATA_SERYJNA_MIN <= v <= DATA_SERYJNA_MAX else None
    t = str(v).strip().split(" ")[0]
    for fmt in _FORMATY_DATY:
        try:
            return dt.datetime.strptime(t, fmt).date()
        except ValueError:
            continue
    return None


def _numer_prywatny(numer: str) -> str | None:
    """"#0123" / "0123" / "123" -> "123" (postac do porownan numerow zlecen prywatnych); inny tekst -> None."""
    m = re.fullmatch(r"#?\s*([0-9]+)", numer.strip())
    return N.postac_numeru(m.group(1)) if m else None


def nazwisko_z_folderu(folder: str, kuweta: str | None) -> tuple[str, ...]:
    """Nazwisko z nazwy folderu (do reguly 3) jako slowa znormalizowane: slowa z co najmniej 2 liter PRZED numerem kuwety
    ("Testowski J. 3263 zs" -> ("testowski",), "Nowak-Testowa 3263" -> ("nowak", "testowa")); folder zaczynajacy sie numerem
    ("3263 Testowski Jan", "#1234 Testowski") -> pierwsze slowo po numerze, ktore nie jest kodem pracy. Same inicjaly -> ()."""
    tok = _TOKEN.findall(N.znormalizuj(folder))
    numer = None
    if kuweta and not N.czy_niejednoznaczna(kuweta):
        cyfry = kuweta.lstrip(N.PRYWATNE)
        numer = N.postac_numeru(cyfry) if cyfry.isdigit() else None
    liczby = [i for i, t in enumerate(tok) if t.isdigit()]
    poz = next((i for i in liczby if numer is not None and N.postac_numeru(tok[i]) == numer), liczby[0] if liczby else len(tok))
    przed = tuple(t for t in tok[:poz] if not t.isdigit() and len(t) >= 2)
    if przed:
        return przed
    po = [t for t in tok[poz + 1:] if not t.isdigit() and len(t) >= 2 and t not in KODY_PRACY]
    return tuple(po[:1])


def _surowy(w: Any) -> tuple | None:
    """Wartosci wiersza do porownan: krotka (ta sama, gdy juz jest krotka) albo None dla wiersza pustego / nieistniejacego."""
    if w is None:
        return None
    t = w if type(w) is tuple else tuple(w)
    for v in t:
        if v is not None and v != "":
            return t
    return None


# --- konfiguracja -----------------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class Konfiguracja:
    """Ustawienia modulu (``[excel]`` + ``[sciezki] log_excel``); wartosci domyslne = plan wdrozenia i ustawienia.przyklad.toml."""
    kolumna_daty: str = "A"
    kolumna_odhaczenia: str = "B"  # numer zlecenia + pole odhaczenia (kolor)
    kolumna_kuwety: str = "C"
    kolumna_nazwy: str = "H"
    kolor: tuple[int, int, int] = ZIELONY
    tryb: str = TRYB_PYTAJ
    pierwszy_wiersz: int = 2
    skoroszyt: str = ""  # "" = aktywny skoroszyt (ostrzezenie z nazwa uzyta)
    arkusz: str = ""  # "" = aktywny arkusz (ostrzezenie z nazwa uzyta)
    odswiez_co_min: float = 5.0
    maks_wiek_dni: int = 60  # bezpiecznik P3: wybrany wiersz starszy = wskaz wiersz; 0 = bez limitu (do potwierdzenia w D2)
    log: Path | None = None  # plik log_excel.csv (wymagany do zapisu)
    ostrzezenia: tuple[str, ...] = ()

    def __post_init__(self):
        if self.tryb not in TRYBY:
            raise BladExcela(f"nieznany tryb Excela {self.tryb!r} - w etapie 3 tylko {', '.join(TRYBY)} (DW10)")
        kolumny = [numer_kolumny(k) for k in (self.kolumna_daty, self.kolumna_odhaczenia, self.kolumna_kuwety, self.kolumna_nazwy)]
        if len(set(kolumny)) != 4:
            raise BladExcela("kolumny daty, odhaczenia, kuwety i nazwy musza byc rozne")
        if len(self.kolor) != 3 or not all(isinstance(c, int) and 0 <= c <= 255 for c in self.kolor):
            raise BladExcela(f"zly kolor {self.kolor!r} (trzy liczby 0...255)")
        if self.pierwszy_wiersz < 1 or self.odswiez_co_min <= 0 or self.maks_wiek_dni < 0:
            raise BladExcela("pierwszy_wiersz musi byc >= 1, odswiez_co_min > 0, maks_wiek_dni >= 0")

    @property
    def ostatnia_kolumna(self) -> int:
        return max(numer_kolumny(OSTATNIA_KOLUMNA), *(numer_kolumny(k) for k in (self.kolumna_daty, self.kolumna_odhaczenia,
                                                                                 self.kolumna_kuwety, self.kolumna_nazwy)))

    @classmethod
    def z_ustawien(cls, ust: dict) -> "Konfiguracja":
        """Z wczytanych ustawien (``ustawienia.wczytaj_ustawienia``). ``tryb_pytaj_przed_zapisem = false`` NIE wlacza zapisu
        samodzielnego (DW10) - tryb zostaje "pytaj", a ``ostrzezenia`` to mowia. Log poza katalogiem ``dane/`` = ostrzezenie
        (zawiera nazwy folderow - T9)."""
        e = ust["excel"]
        ostrzezenia = []
        if not e.get("tryb_pytaj_przed_zapisem", True):
            ostrzezenia.append("[excel] tryb_pytaj_przed_zapisem = false nie wlacza zapisu samodzielnego: w etapie 3 (DW10) zapis "
                               "tylko po zatwierdzeniu (tryb 'pytaj') albo wcale (tryb 'cien')")
        log = B.sciezka_z_ustawien(ust, "log_excel")
        if "dane" not in [c.casefold() for c in log.parts[:-1]]:
            ostrzezenia.append("[sciezki] log_excel lezy poza katalogiem dane/ - log zawiera nazwy folderow zlecen (dane osobowe, T9): "
                               "przenies go do dane/ (poza OneDrive i repozytorium)")
        return cls(kolumna_daty=e.get("kolumna_daty", "A").upper(), kolumna_odhaczenia=e["kolumna_odhaczenia"].upper(),
                   kolumna_kuwety=e["kolumna_kuwety"].upper(), kolumna_nazwy=e["kolumna_nazwy"].upper(), kolor=tuple(e["kolor_rgb"]),
                   tryb=e.get("tryb", TRYB_PYTAJ), pierwszy_wiersz=e.get("pierwszy_wiersz", 2), skoroszyt=e.get("skoroszyt", ""),
                   arkusz=e.get("arkusz", ""), odswiez_co_min=float(e.get("odswiez_co_min", 5.0)), maks_wiek_dni=e.get("maks_wiek_dni", 60),
                   log=log, ostrzezenia=tuple(ostrzezenia))


# --- indeks arkusza (odczyt A-I do pamieci) ---------------------------------------------------------------------------
@dataclass(frozen=True)
class WierszArkusza:
    """Jeden wiersz arkusza po normalizacji. ``wartosci`` = surowe A..I. ``nazwa`` i ``tokeny`` (H) - DANE OSOBOWE: poza
    ``repr`` (tracebacki, wydruki testow - D1)."""
    nr: int
    data: dt.date | None
    numer_b: str
    kuweta: str | None
    nazwa: str = field(repr=False)
    tokeny: frozenset = field(repr=False)
    prywatne: tuple[str, ...] = ()
    wartosci: tuple = field(default=(), repr=False)


class IndeksArkusza:
    """Wiersze arkusza w pamieci z indeksami: kuweta (kolumna C) -> wiersze, numer prywatny (B wiersza bez kuwety albo "#n"
    w H) -> wiersze; ``surowy(nr)`` - wartosci wiersza (takze pustego). Skoroszyt, sciezka i arkusz - skad odczyt."""

    def __init__(self, wiersze: list[WierszArkusza], arkusz: str, czas: dt.datetime, *, skoroszyt: str = "", sciezka: str = "",
                 surowe: list | None = None, pierwszy_wiersz: int = 2):
        self.wiersze = wiersze
        self.arkusz = arkusz
        self.skoroszyt = skoroszyt
        self.sciezka = sciezka
        self.czas = czas
        self.pierwszy_wiersz = pierwszy_wiersz
        self._surowe = surowe if surowe is not None else []
        self.po_nr = {w.nr: w for w in wiersze}
        self.po_kuwecie: dict[str, list[WierszArkusza]] = {}
        self.po_prywatnym: dict[str, list[WierszArkusza]] = {}
        for w in wiersze:
            if w.kuweta:
                self.po_kuwecie.setdefault(w.kuweta, []).append(w)
            for p in w.prywatne:
                self.po_prywatnym.setdefault(p, []).append(w)

    def surowy(self, nr: int) -> tuple | None:
        i = nr - self.pierwszy_wiersz
        return self._surowe[i] if 0 <= i < len(self._surowe) else None

    @property
    def zrodlo(self) -> tuple[str, str, str]:
        return self.skoroszyt, self.sciezka, self.arkusz

    @classmethod
    def z_wartosci(cls, wartosci: list[tuple], konf: Konfiguracja, arkusz: str, czas: dt.datetime, *, skoroszyt: str = "",
                   sciezka: str = "", poprzedni: "IndeksArkusza | None" = None) -> "IndeksArkusza":
        """Indeks z wartosci odczytanych z arkusza. ``poprzedni``: wiersz niezmieniony (ten sam numer i te same wartosci) bierze
        gotowy ``WierszArkusza`` z poprzedniego indeksu (ponowny odczyt przy kazdej propozycji i zatwierdzeniu - P1; bez nowych
        obiektow na wiersz, zeby odczyt 30 tys. wierszy byl tani)."""
        n = konf.ostatnia_kolumna
        ia, ib, ic, ih = (numer_kolumny(k) - 1 for k in (konf.kolumna_daty, konf.kolumna_odhaczenia, konf.kolumna_kuwety, konf.kolumna_nazwy))
        jutro = czas.date() + dt.timedelta(days=1)
        stary = poprzedni.po_nr if poprzedni is not None and poprzedni.czas.date() == czas.date() else {}
        wiersze, surowe = [], []
        for i, wartosci_wiersza in enumerate(wartosci):
            nr = konf.pierwszy_wiersz + i
            w = wartosci_wiersza if type(wartosci_wiersza) is tuple and len(wartosci_wiersza) == n else (tuple(wartosci_wiersza) + (None,) * n)[:n]
            w = _surowy(w)
            surowe.append(w)
            if w is None:
                continue
            gotowy = stary.get(nr)
            if gotowy is not None and gotowy.wartosci != w:
                gotowy = None
            if gotowy is None:
                nazwa = norm_nazwa(w[ih])
                numer_b = norm_numer(w[ib])
                kuweta = norm_kuweta(w[ic])
                prywatne = {N.postac_numeru(m) for m in _PRYWATNY.findall(nazwa)}
                p = _numer_prywatny(numer_b) if numer_b else None
                if p and (kuweta is None or kuweta.startswith(N.PRYWATNE)):  # numer w B tylko w wierszu zlecenia prywatnego (P3)
                    prywatne.add(p)
                data = data_z_komorki(w[ia])
                if data is not None and data > jutro:  # D8: literowka roku nie moze wygrac reguly 3
                    data = None
                gotowy = WierszArkusza(nr=nr, data=data, numer_b=numer_b, kuweta=kuweta, nazwa=nazwa, tokeny=tokeny(nazwa),
                                       prywatne=tuple(sorted(prywatne)), wartosci=w)
            wiersze.append(gotowy)
        return cls(wiersze, arkusz, czas, skoroszyt=skoroszyt, sciezka=sciezka, surowe=surowe, pierwszy_wiersz=konf.pierwszy_wiersz)


# --- reguly 1-5 -------------------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class Dopasowanie:
    """Wynik regul: ``klasa`` (jeden wiersz / juz odhaczone / wskaz wiersz), ``wiersz`` (None dla "wskaz"), ``regula``
    (2, 3 - wybor; 4 - juz odhaczone; 5 - wskaz wiersz), ``kandydaci`` (numery wierszy: najpierw z nazwa jak folder, potem od
    najnowszej daty), ``powod`` (tekst bez nazwisk), ``data`` (data wiersza z kolumny A, ISO), ``do_sprawdzenia`` (wybor bez
    zgodnej nazwy - regula 3 albo zlecenie prywatne: okno pokazuje, nie zatwierdza w ciszy, takze "juz odhaczone")."""
    klasa: str
    wiersz: int | None
    regula: int
    kandydaci: tuple[int, ...]
    powod: str
    data: str | None = None
    do_sprawdzenia: bool = False


def _najnowszy(wiersze: list[WierszArkusza]) -> WierszArkusza | None:
    """Wiersz z najnowsza data w A - jedyny; None, gdy dat brak, gdy dwa wiersze maja te sama najnowsza date albo gdy wiersz
    bez daty lezy PONIZEJ najnowszego (mogl byc dopisany pozniej)."""
    z_data = [w for w in wiersze if w.data is not None]
    if not z_data:
        return None
    maks = max(w.data for w in z_data)
    naj = [w for w in z_data if w.data == maks]
    if len(naj) != 1 or any(w.data is None and w.nr > naj[0].nr for w in wiersze):
        return None
    return naj[0]


def _nowszy(x: WierszArkusza, w: WierszArkusza) -> bool:
    """Czy wiersz ``x`` moze byc nowszy niz ``w``: pozniejsza data, albo ta sama / nieznana data i wiersz nizej."""
    if x.data is not None and w.data is not None and x.data != w.data:
        return x.data > w.data
    return x.nr > w.nr


def _kolejnosc(wiersze: list[WierszArkusza], nazwa: str) -> tuple[int, ...]:
    widziane, wynik = set(), []
    for w in sorted(wiersze, key=lambda w: (0 if nazwa and w.nazwa == nazwa else 1, -(w.data.toordinal() if w.data else 0), -w.nr)):
        if w.nr not in widziane:
            widziane.add(w.nr)
            wynik.append(w.nr)
    return tuple(wynik)


def dopasuj(indeks: IndeksArkusza, kuweta: str | None, folder: str, wypelnienie: Callable[[int], tuple | None],
            kolor: tuple[int, int, int] = ZIELONY, kolumna_kuwety: str = "C", dzis: dt.date | None = None,
            maks_wiek_dni: int = 0) -> Dopasowanie:
    """Reguly 1-5 planu wdrozenia dla jednego zlecenia (``kuweta`` jak w ``zlecenia.kuweta``, ``folder`` - nazwa folderu).

    ``wypelnienie(nr)`` - kolor pola B wiersza ``nr`` (czytany na zywo tylko dla kandydatow). Funkcja niczego nie zapisuje.
    1. kandydaci: kolumna C po normalizacji == kuweta (dokladnie); 2. H po normalizacji == nazwa folderu - jeden wiersz = on;
    kilka takich wierszy (reklamacja z nowym wierszem): najnowszy, gdy jest jedynym nieodhaczonym (gdy wszystkie zielone -
    juz odhaczone; inaczej wskaz); 3. H nie pasuje nigdzie: wiersz z najnowsza data w A sposrod kandydatow, jesli nazwisko
    z folderu wystepuje w jego H albo H jest puste; 4. wybrany wiersz z zielonym B = juz odhaczone (inny kolor B = wskaz);
    5. wiecej niz jeden wiersz albo zaden = wskaz wiersz z lista kandydatow. Zlecenie prywatne "#1234": wiersz zlecenia
    prywatnego z numerem w B albo w H (jeden w limicie wieku = propozycja, regula 2). Kuweta pusta albo niejednoznaczna
    ("?46,3263") = wskaz wiersz. Bezpieczniki kazdego wyboru (P3, przed regula 4): ``maks_wiek_dni`` > 0 i wiersz starszy albo
    bez daty; nowszy nieodhaczony wiersz tej kuwety - obie sytuacje = wskaz wiersz."""
    kolor = tuple(kolor)
    dzis = dzis or dt.date.today()

    def kolor_b(nr: int) -> tuple | None:
        c = wypelnienie(nr)
        return None if c is None or tuple(c) == BIALY else tuple(c)

    def wskaz(kandydaci: tuple[int, ...], powod: str) -> Dopasowanie:
        return Dopasowanie(KLASA_WSKAZ_WIERSZ, None, 5, kandydaci, "regula 5: " + powod + " - wskaz wiersz")

    def za_stary(w: WierszArkusza) -> str | None:
        if not maks_wiek_dni:
            return None
        if w.data is None:
            return f"wiersz {w.nr} nie ma daty w kolumnie A - wieku nie da sie sprawdzic ([excel] maks_wiek_dni)"
        if (dzis - w.data).days > maks_wiek_dni:
            return f"wiersz {w.nr} jest starszy niz {maks_wiek_dni} dni ([excel] maks_wiek_dni)"
        return None

    def wybierz(w: WierszArkusza, regula: int, powod: str, kandydaci: tuple[int, ...], wiersze_grupy: list[WierszArkusza],
                do_sprawdzenia: bool) -> Dopasowanie:
        stary = za_stary(w)
        if stary:
            return wskaz(kandydaci, stary)
        nowsze = [x.nr for x in wiersze_grupy if x.nr != w.nr and _nowszy(x, w) and kolor_b(x.nr) != kolor]
        if nowsze:
            return wskaz(kandydaci, f"wiersz {w.nr} wybrany, ale jest nowszy nieodhaczony wiersz tej kuwety ({', '.join(map(str, nowsze[:3]))})")
        data = w.data.isoformat() if w.data else None
        c = kolor_b(w.nr)
        if c is None:
            return Dopasowanie(KLASA_JEDEN_WIERSZ, w.nr, regula, kandydaci, f"regula {regula}: {powod}", data, do_sprawdzenia)
        if c == kolor:
            return Dopasowanie(KLASA_JUZ_ODHACZONE, w.nr, 4, kandydaci, f"regula 4: pole B wiersza {w.nr} juz zielone - nic do zapisania, "
                               f"tylko log (wybor: regula {regula})", data, do_sprawdzenia)
        return wskaz(kandydaci, f"pole B wiersza {w.nr} ma inne wypelnienie niz zielone - program go nie nadpisuje")

    if not kuweta:
        return wskaz((), "w nazwie folderu nie ma numeru kuwety")
    if N.czy_niejednoznaczna(kuweta):
        numery = N.kandydaci_kuwety(kuweta)
        kand = [w for k in numery for w in indeks.po_kuwecie.get(norm_kuweta(k) or "", [])]
        return wskaz(_kolejnosc(kand, ""), f"kuweta niejednoznaczna w nazwie folderu ({' albo '.join(numery)})")
    if kuweta.startswith(N.PRYWATNE):
        numer = _numer_prywatny(kuweta)
        wszystkie = list({w.nr: w for w in indeks.po_prywatnym.get(numer or "", [])}.values())
        kand = _kolejnosc(wszystkie, "")
        w_limicie = [w for w in wszystkie if za_stary(w) is None]
        if len(w_limicie) == 1:
            return wybierz(w_limicie[0], 2, "zlecenie prywatne - jedyny wiersz zlecenia prywatnego z tym numerem w kolumnie B albo H "
                                            "(zalozenie K12, D5)", kand, wszystkie, True)
        return wskaz(kand, f"zlecenie prywatne - {len(w_limicie)} wierszy z tym numerem w kolumnie B albo H w limicie wieku "
                           f"(wszystkich {len(wszystkie)})")
    k = norm_kuweta(kuweta) or ""
    wiersze = indeks.po_kuwecie.get(k, [])
    if not wiersze:
        return wskaz((), f"brak wiersza z kuweta {k} w kolumnie {kolumna_kuwety}")
    nazwa = N.znormalizuj(folder)
    kand = _kolejnosc(wiersze, nazwa)
    zgodne = [w for w in wiersze if w.nazwa and w.nazwa == nazwa]
    if len(zgodne) == 1:
        return wybierz(zgodne[0], 2, f"nazwa w H zgodna z nazwa folderu (1 z {len(wiersze)} wierszy kuwety {k})", kand, wiersze, False)
    if len(zgodne) > 1:
        naj = _najnowszy(zgodne)
        if naj is None:
            return wskaz(kand, f"{len(zgodne)} wiersze z nazwa jak folder, bez jednej najnowszej daty")
        otwarte = [w for w in zgodne if kolor_b(w.nr) != kolor]
        if not otwarte:
            return wybierz(naj, 3, "kilka wierszy z nazwa jak folder, wszystkie zielone - najnowszy", kand, wiersze, False)
        if otwarte == [naj]:
            return wybierz(naj, 3, f"{len(zgodne)} wiersze z nazwa jak folder - najnowszy jest jedynym nieodhaczonym (reklamacja z nowym "
                                   "wierszem)", kand, wiersze, False)
        return wskaz(kand, f"{len(zgodne)} wiersze z nazwa jak folder, nieodhaczony nie tylko najnowszy")
    naj = _najnowszy(wiersze)
    if naj is None:
        return wskaz(kand, f"H nie pasuje, a najnowszej daty w kolumnie A wsrod {len(wiersze)} wierszy kuwety {k} nie da sie ustalic")
    nazwisko = nazwisko_z_folderu(folder, kuweta)
    if not naj.nazwa:
        return wybierz(naj, 3, f"H nie pasuje; najnowszy wiersz kuwety {k} ma puste H", kand, wiersze, True)
    if nazwisko and set(nazwisko) <= naj.tokeny:
        return wybierz(naj, 3, f"H nie pasuje; najnowszy wiersz kuwety {k} ma w H nazwisko z folderu", kand, wiersze, True)
    return wskaz(kand, f"H nie pasuje, a najnowszy wiersz kuwety {k} nie ma w H nazwiska z folderu (inna osoba albo same inicjaly)")


# --- pozycja do zatwierdzenia i modul ---------------------------------------------------------------------------------
@dataclass
class Pozycja:
    """Jedno zlecenie do odhaczenia: propozycja wiersza + migawka wierszy kandydatow i ich sasiadow (kontrola przed zapisem,
    okno A12) + skad odczyt (skoroszyt, sciezka, arkusz - P2).

    ``folder`` - DANE OSOBOWE (tylko do logu i ``excel_zapisy``); ``zalatwiona`` - po zapisie, wpisie "juz odhaczone", pominieciu
    albo zapisie z bledem po nim (drugi zapis tej samej pozycji = odmowa); ``stan`` - wynik ostatniego wpisu albo
    ``STAN_ZAPISANO_BEZ_CSV``."""
    kuweta: str | None
    folder: str = field(repr=False)
    dopasowanie: Dopasowanie
    arkusz: str
    migawka: dict = field(repr=False)
    wypelnienia: dict = field(repr=False)
    konf: Konfiguracja = field(repr=False)
    skoroszyt: str = ""
    sciezka: str = field(default="", repr=False)
    czas_odczytu: dt.datetime | None = None
    zlecenie_id: int | None = None
    sesja_pieca_id: int | None = None
    zrodlo: str | None = None
    zalatwiona: bool = False
    stan: str | None = None

    @property
    def kandydaci_do_okna(self) -> list[dict]:
        """Wiersze kandydatow do okna "Excel: wskaz wiersz" (A12), w kolejnosci ``dopasowanie.kandydaci``: ``wiersz``,
        ``data`` (ISO), ``numer_b``, ``kuweta`` (C), ``nazwa`` (H - DANE OSOBOWE: tylko na ekran laptopa, nie do logow),
        ``wypelnienie_b`` (R, G, B albo None), ``wartosci`` (surowe A..I)."""
        k = self.konf
        ia, ib, ic, ih = (numer_kolumny(x) - 1 for x in (k.kolumna_daty, k.kolumna_odhaczenia, k.kolumna_kuwety, k.kolumna_nazwy))
        wynik = []
        for nr in self.dopasowanie.kandydaci:
            w = self.migawka.get(nr) or ()
            d = data_z_komorki(w[ia]) if w else None
            wynik.append({"wiersz": nr, "data": d.isoformat() if d else None, "numer_b": norm_numer(w[ib]) if w else "",
                          "kuweta": "" if not w or w[ic] is None else str(w[ic]).strip(), "nazwa": "" if not w or w[ih] is None else str(w[ih]),
                          "wypelnienie_b": self.wypelnienia.get(nr), "wartosci": w})
        return wynik


def _tekst_bledu(e: BaseException) -> str:
    return B.bez_sciezek(f"{type(e).__name__}: {e}")[:200]


class Excel:
    """Modul Excela dla programu (A12): odczyt arkusza, propozycje, zatwierdzenie zapisu, log.

    ``zrodlo``: obiekt ``ZrodloArkusza`` albo funkcja bez argumentow, ktora go zwraca (polaczenie leniwe - brak Excela nie
    przerywa startu programu; blad dopiero przy odczycie: ``BladExcela`` "Excel niedostepny"). ``baza``: ``baza.Baza``
    (tabela ``zlecenia`` - nazwa folderu; ``sesje_pieca`` - X4; ``excel_zapisy`` - kazdy wpis logu). ``zegar``: funkcja czasu;
    ``czekaj``: funkcja przerwy przed ponowieniem kroku zapisu (testy: bez czekania). Jeden obiekt - jeden watek (COM)."""

    def __init__(self, konf: Konfiguracja, zrodlo: Any, baza: B.Baza | None = None, zegar: Callable[[], dt.datetime] | None = None,
                 czekaj: Callable[[float], None] | None = None):
        if hasattr(zrodlo, "odczytaj"):
            self._zrodlo, self._fabryka = zrodlo, None
        elif callable(zrodlo):
            self._zrodlo, self._fabryka = None, zrodlo
        else:
            raise BladExcela("zrodlo arkusza: oczekiwano obiektu z metodami odczytaj/wiersz/wypelnienie/ustaw_wypelnienie albo funkcji")
        self.konf = konf
        self.baza = baza
        self._zegar = zegar or dt.datetime.now
        self._czekaj = czekaj or time.sleep
        self._indeks: IndeksArkusza | None = None
        self._kol_b = numer_kolumny(konf.kolumna_odhaczenia)
        self._ib = self._kol_b - 1

    @classmethod
    def z_ustawien(cls, ust: dict, zrodlo: Any = None, baza: B.Baza | None = None, zegar: Callable[[], dt.datetime] | None = None) -> "Excel":
        """Z ustawien; bez ``zrodlo`` - polaczenie COM z otwartym Excelem przy pierwszym odczycie (``excel_com.polacz``)."""
        konf = Konfiguracja.z_ustawien(ust)
        if zrodlo is None:
            def zrodlo():
                from . import excel_com
                return excel_com.polacz(konf.skoroszyt, konf.arkusz)
        return cls(konf, zrodlo, baza=baza, zegar=zegar)

    @property
    def tryb(self) -> str:
        return self.konf.tryb

    @property
    def ostrzezenia(self) -> tuple[str, ...]:
        """Ostrzezenia do pokazania w oknie (A12): z ustawien + skoroszyt / arkusz nie wskazane w ustawieniach (nazwy uzyte)."""
        dodatkowe = []
        if self._indeks is not None and (not self.konf.skoroszyt or not self.konf.arkusz):
            dodatkowe.append(f"[excel] skoroszyt / arkusz nie sa wskazane w ustawieniach - program uzywa aktywnych: skoroszyt "
                             f"'{self._indeks.skoroszyt}', arkusz '{self._indeks.arkusz}'; sprawdz przed pierwszym zatwierdzeniem i wpisz "
                             f"nazwy w ustawienia.toml (D2)")
        return self.konf.ostrzezenia + tuple(dodatkowe)

    # --- polaczenie i odczyt ------------------------------------------------------------------------------------------
    def zrodlo(self) -> ZrodloArkusza:
        if self._zrodlo is None:
            try:
                self._zrodlo = self._fabryka()
            except Exception as e:
                raise BladExcela(f"Excel niedostepny: {_tekst_bledu(e)}") from e
        return self._zrodlo

    def rozlacz(self) -> None:
        """Zwalnia polaczenie z Excelem (obiekty COM) i indeks; nastepny odczyt laczy sie od nowa. A12: przy zamknieciu programu
        i po bledzie COM. Zrodlo podane jako obiekt (nie funkcja) zostaje - nie ma go skad wziac ponownie."""
        if self._fabryka is not None and self._zrodlo is not None:
            zwolnij = getattr(self._zrodlo, "zwolnij", None)
            if callable(zwolnij):
                try:
                    zwolnij()
                except Exception:
                    pass
            self._zrodlo = None
        self._indeks = None

    def _po_bledzie_com(self) -> None:
        if self._fabryka is not None:
            self.rozlacz()

    def odswiez(self) -> IndeksArkusza:
        """Odczyt kolumn A-I biezacego arkusza do pamieci (X2) - teraz."""
        z = self.zrodlo()
        try:
            wartosci = z.odczytaj(self.konf.pierwszy_wiersz, self.konf.ostatnia_kolumna)
            skoroszyt, sciezka, arkusz = str(getattr(z, "skoroszyt", "")), str(getattr(z, "sciezka", "")), str(getattr(z, "nazwa", ""))
        except Exception as e:
            self._po_bledzie_com()
            raise BladExcela(f"odczyt arkusza nie powiodl sie: {_tekst_bledu(e)}") from e
        poprzedni = self._indeks if self._indeks is not None and self._indeks.zrodlo == (skoroszyt, sciezka, arkusz) else None
        self._indeks = IndeksArkusza.z_wartosci(wartosci, self.konf, arkusz, self._zegar(), skoroszyt=skoroszyt, sciezka=sciezka,
                                                poprzedni=poprzedni)
        return self._indeks

    def indeks(self) -> IndeksArkusza:
        """Indeks arkusza; odczyt ponowny, gdy ostatni jest starszy niz ``[excel] odswiez_co_min`` minut (do ``dopasuj``)."""
        if self._indeks is None or self._zegar() - self._indeks.czas >= dt.timedelta(minutes=self.konf.odswiez_co_min):
            return self.odswiez()
        return self._indeks

    def _wypelnienie(self, nr: int) -> tuple | None:
        try:
            return self.zrodlo().wypelnienie(nr, self._kol_b)
        except BladExcela:
            raise
        except Exception as e:
            self._po_bledzie_com()
            raise BladExcela(f"odczyt koloru pola B (wiersz {nr}) nie powiodl sie: {_tekst_bledu(e)}") from e

    def _kolor_b(self, nr: int) -> tuple | None:
        c = self._wypelnienie(nr)
        return None if c is None or tuple(c) == BIALY else tuple(c)

    def _dopasuj(self, ind: IndeksArkusza, kuweta: str | None, folder: str) -> Dopasowanie:
        return dopasuj(ind, kuweta, folder, self._wypelnienie, self.konf.kolor, self.konf.kolumna_kuwety, self._zegar().date(),
                       self.konf.maks_wiek_dni)

    # --- propozycje ---------------------------------------------------------------------------------------------------
    def dopasuj(self, kuweta: str | None, folder: str) -> Dopasowanie:
        """Reguly 1-5 dla jednego zlecenia na biezacym indeksie (bez zapisu, bez logu, bez wymuszania odczytu)."""
        return self._dopasuj(self.indeks(), kuweta, folder)

    def _sprawdz_piec(self, sesja_pieca_id: int | None) -> None:
        """X4: zapis tylko dla zlecen z zamknietego pieca - z baza sprawdzane w ``sesje_pieca``."""
        if sesja_pieca_id is None or self.baza is None:
            return
        w = self.baza.wiersz("SELECT zamknieto FROM sesje_pieca WHERE id = ?", (sesja_pieca_id,))
        if w is None or not w["zamknieto"]:
            raise BladExcela(f"sesja pieca {sesja_pieca_id} nie jest zamknieta - zapis do Excela tylko po 'Zamknij piec' (X4)")

    def _pozycja(self, ind: IndeksArkusza, kuweta: str | None, folder: str, zlecenie_id: int | None, sesja_pieca_id: int | None,
                 zrodlo: str | None) -> Pozycja:
        d = self._dopasuj(ind, kuweta, folder)
        nry = set(d.kandydaci) | ({d.wiersz} if d.wiersz is not None else set())
        migawka = {r: ind.surowy(r) for nr in nry for r in (nr - 1, nr, nr + 1)}  # D6: z sasiadami
        return Pozycja(kuweta=kuweta, folder=folder, dopasowanie=d, arkusz=ind.arkusz, migawka=migawka,
                       wypelnienia={nr: self._wypelnienie(nr) for nr in nry}, konf=self.konf, skoroszyt=ind.skoroszyt,
                       sciezka=ind.sciezka, czas_odczytu=ind.czas, zlecenie_id=zlecenie_id, sesja_pieca_id=sesja_pieca_id, zrodlo=zrodlo)

    def pozycja(self, kuweta: str | None, folder: str, zlecenie_id: int | None = None, sesja_pieca_id: int | None = None,
                zrodlo: str | None = None) -> Pozycja:
        """Propozycja dla jednego zlecenia na SWIEZYM odczycie (P1) z migawka wierszy kandydatow. X4: ``sesja_pieca_id`` musi
        wskazywac zamkniety piec (sprawdzane w bazie); pozycja bez sesji pieca sluzy tylko do podgladu - ``zatwierdz`` w trybie
        "pytaj" jej nie zapisze."""
        self._sprawdz_piec(sesja_pieca_id)
        return self._pozycja(self.odswiez(), kuweta, folder, zlecenie_id, sesja_pieca_id, zrodlo)

    def _zlecenie(self, zlecenie_id: int) -> dict:
        if self.baza is None:
            raise BladExcela("brak bazy: nazwy folderu zlecenia nie ma skad wziac (tabela zlecenia)")
        w = self.baza.wiersz("SELECT folder, kuweta, zrodlo FROM zlecenia WHERE id = ?", (zlecenie_id,))
        if w is None:
            raise BladExcela(f"nie ma zlecenia id {zlecenie_id} w tabeli zlecenia")
        return w

    def propozycje(self, wynik_pieca: dict) -> list[Pozycja]:
        """Pozycje dla zlecen kompletnych z wyniku "Zamknij piec" (``SesjaRano.zamknij_piec`` / ``wynik_pieca``) - X4: tylko po
        zamknieciu pieca i tylko zlecenia kompletne; jeden swiezy odczyt arkusza na piec (P1). Kolejnosc jak w ``kompletne``.
        Blad jednego zlecenia (np. brak w bazie) = pozycja "wskaz wiersz" z powodem, reszta dalej (D5). Niczego nie zapisuje."""
        if not wynik_pieca or not wynik_pieca.get("zamknieto"):
            raise BladExcela("zapis do Excela tylko po 'Zamknij piec' (X4) - ten piec nie jest zamkniety")
        sesja = wynik_pieca.get("sesja_pieca_id")
        self._sprawdz_piec(sesja)
        ind = self.odswiez()
        pozycje = []
        for z in wynik_pieca.get("kompletne", []):
            try:
                info = self._zlecenie(z["zlecenie_id"])
                pozycje.append(self._pozycja(ind, info["kuweta"], info["folder"], z["zlecenie_id"], sesja, info["zrodlo"]))
            except BladExcela as e:
                d = Dopasowanie(KLASA_WSKAZ_WIERSZ, None, 5, (), f"blad: {e} - zlecenie do sprawdzenia recznie")
                pozycje.append(Pozycja(kuweta=z.get("kuweta"), folder="", dopasowanie=d, arkusz=ind.arkusz, migawka={}, wypelnienia={},
                                       konf=self.konf, skoroszyt=ind.skoroszyt, sciezka=ind.sciezka, czas_odczytu=ind.czas,
                                       zlecenie_id=None, sesja_pieca_id=sesja))
        return pozycje

    # --- zapis i log --------------------------------------------------------------------------------------------------
    @staticmethod
    def _osoba(operator: str | None) -> str:
        if not isinstance(operator, str) or not operator.strip():
            raise BladExcela("podaj, kto zatwierdza (osoba z listy [sesja] operatorzy) - regula 6: log zapisuje, kto zatwierdzil")
        return operator.strip()

    def _numer_b(self, pozycja: Pozycja, nr: int | None) -> str:
        w = pozycja.migawka.get(nr) if nr is not None else None
        return norm_numer(w[self._ib]) if w else ""

    def _sprawdz_log(self) -> None:
        if self.konf.log is None:
            raise BladExcela("brak pliku logu ([sciezki] log_excel) - bez logu program niczego nie zapisuje (regula 6)")
        try:
            self.konf.log.parent.mkdir(parents=True, exist_ok=True)
            with open(self.konf.log, "a", encoding="utf-8"):
                pass
        except OSError as e:
            raise BladExcela(f"plik log_excel.csv jest niedostepny (otwarty w innym programie?) - nic nie zapisano: {type(e).__name__}") from e

    def _dopisz_csv(self, wiersz: list) -> None:
        """Jeden wiersz ``log_excel.csv`` (naglowek przy nowym pliku). Blad pliku = ``OSError`` (obsluga w ``_loguj``)."""
        plik = self.konf.log
        plik.parent.mkdir(parents=True, exist_ok=True)
        nowy = not plik.exists() or plik.stat().st_size == 0
        with open(plik, "a", encoding="utf-8-sig" if nowy else "utf-8", newline="") as f:
            w = csv.writer(f, delimiter=";", lineterminator="\r\n")
            if nowy:
                w.writerow(POLA_LOGU)
            w.writerow(wiersz)

    def _loguj(self, pozycja: Pozycja, osoba: str, nr: int | None, regula: int | None, wynik: str, klasa: str | None = None) -> dict:
        """Wpis do ``log_excel.csv`` (pola reguly 6 + skoroszyt, regula, wynik, tryb) i do ``excel_zapisy`` (gdy jest baza;
        ``arkusz`` = "skoroszyt!arkusz"). Blad pliku CSV: wpis w bazie mimo to, potem ``BladExcela`` (P5). Zwraca wynik dla
        programu - ``POLA_WYNIKU``, bez nazwy folderu (P4)."""
        if self.konf.log is None:
            raise BladExcela("brak pliku logu ([sciezki] log_excel) - bez logu program niczego nie zapisuje (regula 6)")
        teraz = self._zegar().replace(microsecond=0)
        numer_b = self._numer_b(pozycja, nr)
        csv_wpis = {"data": teraz.date().isoformat(), "godzina": teraz.strftime("%H:%M:%S"), "kuweta": pozycja.kuweta or "",
                    "folder": pozycja.folder, "numer_zlecenia_b": numer_b, "arkusz": pozycja.arkusz, "wiersz": nr, "kto_zatwierdzil": osoba,
                    "skoroszyt": pozycja.skoroszyt, "regula": regula, "wynik": wynik, "tryb": self.tryb}
        blad_csv = None
        try:
            self._dopisz_csv(["" if csv_wpis[k] is None else csv_wpis[k] for k in POLA_LOGU])
        except OSError as e:
            blad_csv = e
        id_wpisu = None
        if self.baza is not None:
            try:
                id_wpisu = self.baza.wstaw("excel_zapisy", czas=teraz.isoformat(), sesja_pieca_id=pozycja.sesja_pieca_id,
                                           zlecenie_id=pozycja.zlecenie_id, kuweta=pozycja.kuweta, folder=pozycja.folder, numer_zlecenia_b=numer_b,
                                           arkusz=f"{pozycja.skoroszyt}!{pozycja.arkusz}" if pozycja.skoroszyt else pozycja.arkusz,
                                           wiersz=nr, regula=regula, wynik=wynik, tryb=self.tryb, operator=osoba)
            except Exception as e:
                tekst = "wpisu nie ma ani w log_excel.csv, ani w bazie" if blad_csv else "wpis w log_excel.csv jest, w bazie (excel_zapisy) nie"
                raise BladExcela(f"{wynik}, wiersz {nr}: {tekst}: {_tekst_bledu(e)}") from e
        if blad_csv is not None:
            gdzie = "jest w bazie (excel_zapisy)" if id_wpisu is not None else "nie ma go nigdzie - zapisz recznie"
            raise BladExcela(f"{wynik}, wiersz {nr}: wpisu w log_excel.csv brak (plik zajety?): {type(blad_csv).__name__}; wpis {gdzie}")
        pozycja.stan = wynik
        return {"id": id_wpisu, "kuweta": pozycja.kuweta, "wiersz": nr, "klasa": klasa or pozycja.dopasowanie.klasa, "wynik": wynik,
                "regula": regula, "tryb": self.tryb, "zlecenie_id": pozycja.zlecenie_id, "sesja_pieca_id": pozycja.sesja_pieca_id}

    def zatwierdz(self, pozycja: Pozycja, operator: str | None, wiersz: int | None = None) -> dict:
        """Zatwierdzenie propozycji przez czlowieka: tryb "pytaj" = kolor pola B jednej komorki + log; tryb "cien" = tylko log
        (``tylko_log``). ``wiersz``: wybor czlowieka z ``dopasowanie.kandydaci`` (wymagany dla "wskaz wiersz").

        Kazda proba (do ``PONOWIENIA_ZAPISU``) to caly krok na swiezym odczycie: ten sam skoroszyt i arkusz co przy propozycji,
        wiersz i sasiedzi rowni migawce, pole B, propozycja policzona od nowa rowna pierwotnej, kolor. Blad wywolania zapisu COM:
        najpierw odczyt koloru komorki (N, B) - zielona = zapis doszedl mimo bledu (dalej kontrola po zapisie), pusta = przerwa
        i nastepna proba od odczytu, odczyt niemozliwy albo inny kolor = "zapis mogl dojsc - sprawdz recznie" (wpis ``blad``,
        pozycja zalatwiona). Po zapisie: kontrola wierszy N-1..N+1 i koloru.
        Odmowa (``BladExcela``; wpis ``blad`` w logu, gdy doszlo do sprawdzenia arkusza): brak osoby, pozycja juz zalatwiona,
        X4 (pozycja bez zamknietego pieca), "wskaz wiersz" bez wyboru, wiersz spoza kandydatow, skoroszyt / arkusz inny, arkusz
        zmieniony, pole B w innym kolorze, nieudany zapis. Pole B juz zielone = wpis ``juz_odhaczone`` bez zapisu (regula 4).
        Zwraca wynik dla programu (``POLA_WYNIKU``, bez nazwy folderu)."""
        osoba = self._osoba(operator)
        if pozycja.zalatwiona:
            raise BladExcela("ta pozycja jest juz zalatwiona (wpis w logu) - drugi zapis odrzucony")
        d = pozycja.dopasowanie
        if wiersz is None:
            if d.klasa == KLASA_WSKAZ_WIERSZ:
                raise BladExcela("Excel: wskaz wiersz - wybierz wiersz z listy kandydatow (regula 5)")
            nr, wynik_zapisu, regula = d.wiersz, WYNIK_ZAPISANO, d.regula
        else:
            if wiersz != d.wiersz and wiersz not in d.kandydaci:
                raise BladExcela(f"wiersz {wiersz} nie jest na liscie kandydatow tej kuwety - wybierz kandydata albo zaznacz recznie w Excelu i pomin")
            nr = wiersz
            wynik_zapisu, regula = (WYNIK_ZAPISANO, d.regula) if (wiersz == d.wiersz and d.klasa != KLASA_WSKAZ_WIERSZ) else (WYNIK_WSKAZANO, 5)
        moze_zapisac = not (d.klasa == KLASA_JUZ_ODHACZONE and nr == d.wiersz)
        if self.tryb == TRYB_PYTAJ and moze_zapisac:
            if pozycja.sesja_pieca_id is None:
                raise BladExcela("zapis do Excela tylko dla zlecen z zamknietego pieca (X4) - ta pozycja nie ma sesji pieca (tylko podglad)")
            self._sprawdz_piec(pozycja.sesja_pieca_id)

        def odmowa(tekst: str, e: BaseException | None = None):
            tekst = tekst + (f": {_tekst_bledu(e)}" if e else "")
            try:
                self._loguj(pozycja, osoba, nr, regula, WYNIK_BLAD)
            except BladExcela as bl:  # D5 (runda 3): powod odmowy nie ginie, gdy wpis "blad" sie nie uda
                raise BladExcela(f"{tekst} [wpis 'blad' w logu nie powiodl sie: {bl}]") from (e or bl)
            raise BladExcela(tekst) from e

        for proba in range(PONOWIENIA_ZAPISU):
            # 1. swiezy odczyt calego arkusza - ten sam skoroszyt i arkusz (P1, P2)
            try:
                ind = self.odswiez()
                z = self.zrodlo()
            except BladExcela as e:
                odmowa("odczyt arkusza przed zapisem nie powiodl sie - nic nie zapisano", e)
            if ind.zrodlo != (pozycja.skoroszyt, pozycja.sciezka, pozycja.arkusz):
                odmowa(f"skoroszyt albo arkusz inny niz przy propozycji (teraz skoroszyt '{ind.skoroszyt}', arkusz '{ind.arkusz}'; propozycja: "
                       f"'{pozycja.skoroszyt}', '{pozycja.arkusz}') - nic nie zapisano; otworz wlasciwy plik i zaproponuj ponownie")
            # 2. wiersz i sasiedzi bez zmian (wstawione / usuniete / posortowane wiersze, wspoledycja)
            for r in (nr - 1, nr, nr + 1):
                if ind.surowy(r) != pozycja.migawka.get(r):
                    odmowa(f"arkusz zmienil sie od propozycji (wiersz {r} ma inne wartosci - wspoledycja?) - nic nie zapisano; zaproponuj ponownie")
            # 3. pole B
            c = self._kolor_b(nr)
            if d.klasa == KLASA_JUZ_ODHACZONE and nr == d.wiersz and c != self.konf.kolor:
                odmowa(f"pole B wiersza {nr} nie jest juz zielone (zmiana od propozycji) - nic nie zapisano; zaproponuj ponownie")
            if c == self.konf.kolor:
                return self._zalatw(pozycja, osoba, nr, 4, WYNIK_JUZ_ODHACZONE, KLASA_JUZ_ODHACZONE)
            if c is not None:
                odmowa(f"pole B wiersza {nr} ma inne wypelnienie niz zielone - program go nie nadpisuje; zaznacz recznie w Excelu albo pomin")
            # 4. propozycja policzona od nowa na swiezym odczycie = pierwotna (nowy wiersz kuwety, zmiana C / H innego wiersza)
            d2 = self._dopasuj(ind, pozycja.kuweta, pozycja.folder)
            if (d2.klasa, d2.wiersz, d2.kandydaci) != (d.klasa, d.wiersz, d.kandydaci):
                odmowa(f"arkusz zmienil sie od propozycji (teraz: {d2.klasa}, wiersz {d2.wiersz}, kandydatow {len(d2.kandydaci)}) - nic nie "
                       f"zapisano; zaproponuj ponownie")
            if self.tryb == TRYB_CIEN:
                return self._zalatw(pozycja, osoba, nr, regula, WYNIK_TYLKO_LOG)  # tryb cien: nic nie zapisuje w Excelu
            # 5. zapis - jedna proba COM; odrzucona = przerwa i caly krok od nowa (B1) - ale tylko, gdy kolor NA PEWNO nie doszedl
            self._sprawdz_log()  # log musi dac sie dopisac, zanim zmieni sie kolor
            try:
                z.ustaw_wypelnienie(nr, self._kol_b, self.konf.kolor)
            except Exception as e:
                # runda 3 (P1): wywolanie moglo zapisac kolor i dopiero potem zwrocic blad (zerwane polaczenie, Excel zamkniety) -
                # najpierw odczyt komorki (N, B): zielona = zapis doszedl -> kontrola po zapisie; pusta = mozna ponowic
                try:
                    po_bledzie = self._kolor_b(nr)
                except BladExcela:
                    pozycja.zalatwiona = True  # bez drugiego zapisu - stan komorki nieznany
                    odmowa(f"zapis koloru pola B (wiersz {nr}) zwrocil blad, a odczyt koloru tez sie nie udal - zapis mogl dojsc: "
                           f"sprawdz recznie wiersze {nr - 1}-{nr + 1}", e)
                if po_bledzie == self.konf.kolor:
                    break  # kolor zapisany mimo bledu wywolania - dalej jak po udanym zapisie (kontrola N-1..N+1)
                if po_bledzie is not None:
                    pozycja.zalatwiona = True
                    odmowa(f"zapis koloru pola B (wiersz {nr}) zwrocil blad, a pole ma teraz inne wypelnienie - zapis mogl dojsc: sprawdz "
                           f"recznie wiersze {nr - 1}-{nr + 1}", e)
                if proba + 1 < PONOWIENIA_ZAPISU:
                    self._czekaj(PRZERWA_PONOWIENIA_S)
                    continue
                self._po_bledzie_com()
                odmowa(f"zapis koloru pola B (wiersz {nr}) nie powiodl sie po {PONOWIENIA_ZAPISU} probach - pole B bez wypelnienia, "
                       f"kolor nie zostal zapisany", e)
            break
        # 6. po zapisie: wiersze N-1..N+1 i kolor czytane ponownie
        pozycja.zalatwiona = True  # od tej chwili zadnego drugiego zapisu tej pozycji
        try:
            po = {r: _surowy(z.wiersz(r, self.konf.ostatnia_kolumna)) for r in (nr - 1, nr, nr + 1) if r >= self.konf.pierwszy_wiersz}
            kolor_po = self._kolor_b(nr)
        except Exception as e:
            self._po_bledzie_com()
            odmowa(f"kolor wiersza {nr} zapisany, ale odczyt kontrolny nie powiodl sie - sprawdz recznie wiersze {nr - 1}-{nr + 1}", e)
        if any(po[r] != pozycja.migawka.get(r) for r in po):
            odmowa(f"kolor zapisany, ale wiersz {nr} zmienil sie w trakcie - sprawdz recznie wiersze {nr - 1}-{nr + 1}")
        if kolor_po != self.konf.kolor:
            odmowa(f"kolor zapisany w wierszu {nr}, ale Excel podaje inny (np. plik .xls z paleta 56 kolorow) - sprawdz recznie")
        return self._zalatw(pozycja, osoba, nr, regula, wynik_zapisu, zapisano_kolor=True)

    def _zalatw(self, pozycja: Pozycja, osoba: str, nr: int | None, regula: int | None, wynik: str, klasa: str | None = None,
                zapisano_kolor: bool = False) -> dict:
        try:
            wpis = self._loguj(pozycja, osoba, nr, regula, wynik, klasa)
        except BladExcela:
            if zapisano_kolor:
                pozycja.stan = STAN_ZAPISANO_BEZ_CSV  # P5: kolor jest, wpis w excel_zapisy (gdy baza), CSV brak
            pozycja.zalatwiona = pozycja.zalatwiona or zapisano_kolor
            raise
        pozycja.zalatwiona = True
        return wpis

    def zaloguj_juz_odhaczone(self, pozycja: Pozycja, operator: str | None) -> dict:
        """"Juz odhaczone" (regula 4) - tylko wpis w logu po sprawdzeniu, ze pole B nadal jest zielone; ta metoda nie ma drogi
        zapisu koloru (A12 moze ja wolac bez pytania). Pozycja ``do_sprawdzenia`` (wybor bez zgodnej nazwy) = odmowa: wtedy
        czlowiek zatwierdza ``zatwierdz`` po obejrzeniu wiersza (runda 3, D2)."""
        if pozycja.dopasowanie.klasa != KLASA_JUZ_ODHACZONE:
            raise BladExcela("zaloguj_juz_odhaczone tylko dla pozycji 'juz odhaczone' - inne zatwierdza czlowiek")
        if pozycja.dopasowanie.do_sprawdzenia:
            raise BladExcela(f"wiersz {pozycja.dopasowanie.wiersz} wybrany bez zgodnej nazwy (do sprawdzenia) - 'juz odhaczone' zatwierdza "
                             f"czlowiek po obejrzeniu wiersza (zatwierdz)")
        return self.zatwierdz(pozycja, operator)

    def pomin(self, pozycja: Pozycja, operator: str | None) -> dict:
        """Pominiecie pozycji (czlowiek nie wskazal wiersza albo zaznaczyl recznie w Excelu): wpis ``pominieto``, bez zapisu."""
        osoba = self._osoba(operator)
        if pozycja.zalatwiona:
            raise BladExcela("ta pozycja jest juz zalatwiona (wpis w logu)")
        return self._zalatw(pozycja, osoba, pozycja.dopasowanie.wiersz, pozycja.dopasowanie.regula, WYNIK_POMINIETO)

    def zapisz_cien(self, pozycje: list[Pozycja], operator: str | None) -> list[dict]:
        """Tryb "cien": log porownawczy calego pieca bez pytan (nic nie zapisuje w Excelu): jeden wiersz -> ``tylko_log``
        z wierszem, juz odhaczone -> ``juz_odhaczone``, wskaz wiersz -> ``tylko_log`` bez wiersza; blad -> wpis ``blad``
        (gdy doszlo do sprawdzenia arkusza) i pozycja wyniku z ``powod`` (D4)."""
        if self.tryb != TRYB_CIEN:
            raise BladExcela("zapisz_cien dziala tylko w trybie 'cien' - w trybie 'pytaj' kazdy zapis zatwierdza czlowiek")
        osoba = self._osoba(operator)
        wpisy = []
        for p in pozycje:
            if p.zalatwiona:
                continue
            try:
                if p.dopasowanie.klasa == KLASA_WSKAZ_WIERSZ:
                    wpisy.append(self._zalatw(p, osoba, None, p.dopasowanie.regula, WYNIK_TYLKO_LOG))
                else:
                    wpisy.append(self.zatwierdz(p, osoba))
            except BladExcela as e:
                wpisy.append({"id": None, "kuweta": p.kuweta, "wiersz": p.dopasowanie.wiersz, "klasa": p.dopasowanie.klasa, "wynik": WYNIK_BLAD,
                              "regula": p.dopasowanie.regula, "tryb": self.tryb, "zlecenie_id": p.zlecenie_id,
                              "sesja_pieca_id": p.sesja_pieca_id, "powod": str(e)})
        return wpisy

    def zaloguj_poprawki(self, wynik_pieca: dict, operator: str | None) -> list[dict]:
        """Poprawki z "Zamknij piec" (zab do zlecenia juz odhaczonego - SE5): Excel bez zmian, wpis ``tylko_log`` z wierszem
        wskazanym przez reguly (dla audytu); jeden odczyt arkusza."""
        osoba = self._osoba(operator)
        poprawki = wynik_pieca.get("poprawki", [])
        if not poprawki:
            return []
        ind = self.odswiez()
        wpisy = []
        for x in poprawki:
            info = self._zlecenie(x["zlecenie_id"])
            p = self._pozycja(ind, info["kuweta"], info["folder"], x["zlecenie_id"], wynik_pieca.get("sesja_pieca_id"), info["zrodlo"])
            wpisy.append(self._zalatw(p, osoba, p.dopasowanie.wiersz, p.dopasowanie.regula, WYNIK_TYLKO_LOG))
        return wpisy
