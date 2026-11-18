"""Arkusz syntetyczny zlecen (E3-A9): atrapa arkusza Excela (kolumny A-I) o FIKCYJNYCH nazwach, z pulapkami regul
wyboru wiersza, oraz zapytania o znanej odpowiedzi (oczekiwana klasa i wiersz).

Po co: modul ``stanowisko/excel.py`` wybiera wiersz zlecenia wedlug regul 1-5 planu wdrozenia ("Dane i integracje",
"Reguly znalezienia wiersza") - bez Excela i bez kopii pliku produkcyjnego (paczka D2). Prawda (klasa, wiersz) wynika
z BUDOWY scenariusza (rodzaj pulapki), a nie z uruchomienia modulu excel - test nie jest samosprawdzajacy sie.

Zalozenia o arkuszu (te same co ``excel.ZALOZENIA_ARKUSZA``, do potwierdzenia na kopii pliku - D2, X8): wiersz 1 = naglowek,
dane od wiersza 2, wiersze w kolejnosci dopisywania (rosnaco po dacie); A = data zlecenia, B = numer zlecenia (pole
odhaczenia - kolor), C = numer kuwety, H = nazwa (jak nazwa folderu), D-G i I = inne pola (tu fikcyjne: gabinet, rodzaj,
punkty, kolor, uwagi). Wartosci jak z COM (``Range.Value``): daty jako ``datetime``, liczby jako ``float``; czesc komorek
celowo inaczej (tekst daty, numer seryjny daty, kuweta tekstem z zerami wiodacymi albo spacjami).

Pulapki (``PULAPKI``: nazwa -> liczba zapytan przy 200; klasy: ``jeden_wiersz`` / ``juz_odhaczone`` / ``wskaz_wiersz``):
ta sama kuweta w roznych datach (stare wiersze innych osob - takze w calym tle arkusza), inicjaly zamiast nazwiska, puste H,
pole B juz zielone, zera wiodace, reklamacja z nowym wierszem, kuweta jako fragment innego numeru, duplikaty, brak wiersza,
zlecenia prywatne "#1234" (numer w B albo w H), kuweta niejednoznaczna, brak numeru w nazwie folderu.

Tlo: stare wiersze (ponad ``DNI_TLA_SWIEZEGO`` dni) maja losowe kuwety (takze kuwety scenariuszy - pulapka "ta sama kuweta
w roznych datach"), swieze wiersze tla - kuwety spoza scenariuszy; nazwiska tla i scenariuszy sa z rozlacznych pul, wiec tlo
nie zmienia prawdy zadnego zapytania. Nazwiska sa zlozone z wymyslonych czlonow (zadnych prawdziwych osob).

Tylko biblioteka standardowa (bez pliku xlsx: arkusz w pamieci, zapis CSV tylko do podgladu).
Uzycie (z katalogu stanowisko/):
    py -3.12 narzedzia/arkusz_syntetyczny.py [--wierszy 30000] [--zapytan 200] [--seed 0] [--csv dane/arkusz_syntetyczny.csv]
Na ekran narzedzie wypisuje tylko liczby.
"""
from __future__ import annotations

import argparse
import copy
import csv
import datetime as dt
import random
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

KOLUMNY = "ABCDEFGHI"
NAGLOWEK = ("Data", "Nr zlecenia", "Kuweta", "Gabinet", "Rodzaj", "Punkty", "Kolor", "Nazwa", "Uwagi")
PIERWSZY_WIERSZ = 2
ZIELONY = (198, 239, 206)  # wypelnienie "odhaczone" (plan wdrozenia: RGB 198, 239, 206)
ZOLTY = (255, 235, 156)  # inne wypelnienie pola B (pulapka "pole B w innym kolorze")
DZIS = dt.date(2026, 11, 18)
DNI_TLA = 1100  # tlo arkusza: wiersze z ostatnich ok. 3 lat
DNI_TLA_SWIEZEGO = 30  # swieze wiersze tla nie uzywaja kuwet scenariuszy (prawda scenariuszy nie zalezy od tla)

KLASA_JEDEN = "jeden_wiersz"
KLASA_JUZ = "juz_odhaczone"
KLASA_WSKAZ = "wskaz_wiersz"

# pulapka -> (liczba zapytan przy 200, oczekiwana klasa)
PULAPKI: dict[str, tuple[int, str]] = {
    "prosty": (14, KLASA_JEDEN),                      # H = nazwa folderu, jedyny wiersz kuwety w ostatnich dniach
    "ta_sama_kuweta_inne_daty": (14, KLASA_JEDEN),    # + 2-3 stare wiersze tej kuwety (inne osoby, czasem puste H)
    "zera_wiodace": (10, KLASA_JEDEN),                # folder "Nazwisko 0412", C tekstem "0412" / "00412"
    "kod_sklejony": (8, KLASA_JEDEN),                 # folder "Nazwisko 1784PG", H "Nazwisko 1784 PG"
    "inicjal_imienia_w_h": (10, KLASA_JEDEN),         # H "Nazwisko J. 3263" (inne niz folder) - regula 3
    "inicjaly_zamiast_nazwiska": (10, KLASA_WSKAZ),   # H "T.J. 3263 zs" - nazwiska z folderu nie ma w H
    "puste_h": (10, KLASA_JEDEN),                     # H puste, wiersz najnowszy - regula 3
    "puste_h_nowszy_inny": (8, KLASA_WSKAZ),          # H puste, ale nowszy wiersz tej kuwety ma inne nazwisko
    "pole_b_zielone": (12, KLASA_JUZ),                # poprawka / dofrezowanie zlecenia juz odhaczonego
    "reklamacja_nowy_wiersz": (10, KLASA_JEDEN),      # stary wiersz zielony + nowy (nowsza data, B puste) - nowy
    "reklamacja_oba_zielone": (6, KLASA_JUZ),         # stary i nowy wiersz zielone - juz odhaczone (najnowszy)
    "dwa_otwarte_to_samo_h": (6, KLASA_WSKAZ),        # dwa wiersze z ta sama nazwa, oba bez koloru
    "duplikat_ta_sama_data": (6, KLASA_WSKAZ),        # dwa wiersze z ta sama nazwa i data
    "brak_kuwety_w_arkuszu": (8, KLASA_WSKAZ),        # zadnego wiersza z ta kuweta w C
    "zlecenie_bez_wiersza": (8, KLASA_WSKAZ),         # kuweta jest tylko w wierszach innych osob
    "fragment_kuwety": (8, KLASA_JEDEN),              # nowsze wiersze z C "13263", "3263/2", "3263a" i ta sama nazwa
    "c_liczba_spacje": (8, KLASA_JEDEN),              # C jako " 3263 ", liczba calkowita, tekst, twarda spacja
    "data_tekstem": (6, KLASA_JEDEN),                 # A tekstem "dd.mm.rrrr", H puste - regula 3
    "nfd": (6, KLASA_JEDEN),                          # folder z literami NFD (OneDrive), H w NFC
    "wielkosc_liter_spacje": (6, KLASA_JEDEN),        # H wielkimi literami z podwojnymi spacjami
    "pole_b_inny_kolor": (4, KLASA_WSKAZ),            # B ma inne wypelnienie (zolte) - program go nie nadpisuje
    "kuweta_niejednoznaczna": (4, KLASA_WSKAZ),       # folder "Nazwisko 46 3263" -> kuweta "?46,3263"
    "brak_numeru": (2, KLASA_WSKAZ),                  # folder bez numeru kuwety
    "prywatne_numer_w_b": (6, KLASA_JEDEN),           # "#1234": numer zlecenia w kolumnie B
    "prywatne_numer_w_h": (4, KLASA_JEDEN),           # "#1234": numer w kolumnie H
    "prywatne_zielone": (3, KLASA_JUZ),
    "prywatne_brak": (3, KLASA_WSKAZ),
}
ZAPYTAN_WZOR = sum(n for n, _ in PULAPKI.values())  # 200

# Czlony nazwisk (wymyslone). Pule scenariuszy i tla sa rozlaczne (rozne rdzenie).
_RDZENIE_SC = ("Atrap", "Fikc", "Makiet", "Prob", "Szablon", "Test", "Wzorc", "Zmysl", "Pozor", "Umown")
_RDZENIE_TLA = ("Abak", "Bemol", "Cyrkl", "Dukat", "Ekran", "Fresk", "Grafit", "Hasl", "Indeks", "Jodl",
                "Kalk", "Linijk", "Modul", "Notat", "Obraz", "Pastel", "Rysik", "Sztal", "Tusz", "Wektor")
_RDZENIE_NFD = ("Źrebi", "Łąkow", "Śliwk", "Żołęd", "Ćwikł")  # Zrebi, Lakow, Sliwk, Zoled, Cwikl
_SRODKI = ("", "o", "e", "an", "el", "ur")
_KONCOWKI = ("wski", "wska", "wicz", "niak", "rek", "lska", "nski", "cka", "ny", "na")
IMIONA = ("Jan", "Anna", "Piotr", "Ewa", "Maria", "Adam")
KODY = ("zs", "kor", "PG", "AB", "ZS1")
GABINETY = tuple(f"Gabinet {i:02d}" for i in range(1, 41))
RODZAJE = ("korona", "most", "licowka", "wklad", "korona na implancie")
KOLORY_ZEBA = ("A1", "A2", "A3", "B1", "B2", "C1", "BL2")


def _pula_nazwisk(rdzenie) -> list[str]:
    return [r + s + k for r in rdzenie for s in _SRODKI for k in _KONCOWKI]


def data_seryjna(d: dt.date) -> float:
    """Numer seryjny daty Excela (system 1900): 1899-12-30 = 0."""
    return float((d - dt.date(1899, 12, 30)).days)


@dataclass
class Zapytanie:
    """Jedno zapytanie o znanej odpowiedzi: zlecenie (kuweta jak w bazie, nazwa folderu - FIKCYJNA) i prawda.

    ``wiersz``: oczekiwany wiersz dla ``jeden_wiersz`` i ``juz_odhaczone`` (None dla ``wskaz_wiersz``);
    ``prawdziwy``: wiersz tego zlecenia w arkuszu (dla ``wskaz_wiersz`` musi byc na liscie kandydatow), None = nie ma go."""
    id: int
    pulapka: str
    zrodlo: str  # cyrkon / prywatne
    kuweta: str | None
    folder: str
    klasa: str
    wiersz: int | None = None
    prawdziwy: int | None = None


class ArkuszWPamieci:
    """Atrapa arkusza (interfejs ``excel.ZrodloArkusza``): wartosci komorek i wypelnienia w pamieci + dziennik operacji.

    Wiersz 1 = naglowek. Kolumny numerowane od 1 (A = 1). ``operacje``: kazde wywolanie interfejsu (odczyt, zapis koloru),
    zeby test mogl sprawdzic, ze zapis dotyka wylacznie koloru jednej komorki."""

    def __init__(self, nazwa: str = "Zlecenia", wiersze=(), naglowek=NAGLOWEK):
        self.nazwa = nazwa
        self._komorki: list[list] = [list(naglowek)] + [list(w) for w in wiersze]
        self._wypelnienia: dict[tuple[int, int], tuple[int, int, int]] = {}
        self.operacje: list[tuple] = []

    # --- interfejs excel.ZrodloArkusza ---
    def odczytaj(self, pierwszy_wiersz: int, ostatnia_kolumna: int) -> list[tuple]:
        self.operacje.append(("odczytaj", pierwszy_wiersz, ostatnia_kolumna))
        return [self._wiersz(nr, ostatnia_kolumna) for nr in range(pierwszy_wiersz, len(self._komorki) + 1)]

    def wiersz(self, nr: int, ostatnia_kolumna: int) -> tuple:
        self.operacje.append(("wiersz", nr, ostatnia_kolumna))
        return self._wiersz(nr, ostatnia_kolumna)

    def wypelnienie(self, nr: int, kolumna: int) -> tuple[int, int, int] | None:
        self.operacje.append(("wypelnienie", nr, kolumna))
        return self._wypelnienia.get((nr, kolumna))

    def ustaw_wypelnienie(self, nr: int, kolumna: int, rgb) -> None:
        self.operacje.append(("ustaw_wypelnienie", nr, kolumna, tuple(rgb)))
        self._wypelnienia[(nr, kolumna)] = tuple(rgb)

    # --- pomocnicze (budowa i testy; poza interfejsem) ---
    def _wiersz(self, nr: int, ostatnia_kolumna: int) -> tuple:
        w = self._komorki[nr - 1] if 1 <= nr <= len(self._komorki) else []
        return tuple(w[:ostatnia_kolumna]) + (None,) * max(0, ostatnia_kolumna - len(w))

    @property
    def ostatni_wiersz(self) -> int:
        return len(self._komorki)

    def wartosc(self, nr: int, kolumna: int):
        w = self._komorki[nr - 1]
        return w[kolumna - 1] if kolumna <= len(w) else None

    def ustaw_wartosc(self, nr: int, kolumna: int, wartosc) -> None:
        """Zmiana komorki "przez kogos innego" (wspoledycja) - nie trafia do ``operacje``."""
        w = self._komorki[nr - 1]
        w.extend([None] * (kolumna - len(w)))
        w[kolumna - 1] = wartosc

    def zaznacz(self, nr: int, kolumna: int, rgb) -> None:
        """Wypelnienie ustawione "przez czlowieka" (budowa arkusza, wspoledycja) - nie trafia do ``operacje``."""
        if rgb is None:
            self._wypelnienia.pop((nr, kolumna), None)
        else:
            self._wypelnienia[(nr, kolumna)] = tuple(rgb)

    def wstaw_wiersz(self, nr: int, wartosci) -> None:
        """Wstawienie wiersza przed wierszem ``nr`` "przez kogos innego": nizsze wiersze i ich wypelnienia przesuwaja sie o 1."""
        self._komorki.insert(nr - 1, list(wartosci))
        self._wypelnienia = {((w + 1 if w >= nr else w), k): c for (w, k), c in self._wypelnienia.items()}

    def zrzut(self) -> tuple[list[list], dict]:
        """Kopia wszystkich wartosci i wypelnien (porownanie "przed" i "po")."""
        return copy.deepcopy(self._komorki), dict(self._wypelnienia)

    def kopia(self) -> "ArkuszWPamieci":
        k = ArkuszWPamieci(self.nazwa)
        k._komorki = copy.deepcopy(self._komorki)
        k._wypelnienia = dict(self._wypelnienia)
        return k

    def zapisz_csv(self, plik: str | Path) -> Path:
        """Podglad arkusza w CSV (srednik, UTF-8 z BOM): kolumny A-I + kolor pola B. DANE FIKCYJNE."""
        plik = Path(plik)
        plik.parent.mkdir(parents=True, exist_ok=True)
        with open(plik, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f, delimiter=";")
            for nr, komorki in enumerate(self._komorki, start=1):
                kolor = self._wypelnienia.get((nr, 2))
                w.writerow([("" if v is None else v.isoformat() if isinstance(v, (dt.date, dt.datetime)) else v) for v in komorki]
                           + (["B_kolor"] if nr == 1 else [",".join(map(str, kolor)) if kolor else ""]))
        return plik


@dataclass
class _Wiersz:
    data: dt.date
    a: object
    b: object
    c: object
    h: str | None
    i: str = ""
    kolor_b: tuple | None = None
    klucz: float = 0.0  # kolejnosc w obrebie dnia
    nr: int = 0
    d: str = ""
    e: str = ""
    f: int = 1
    g: str = ""


@dataclass
class Zestaw:
    """Wynik ``zbuduj``: arkusz, zapytania i liczniki budowy (do raportu)."""
    arkusz: ArkuszWPamieci
    zapytania: list[Zapytanie]
    liczniki: dict = field(default_factory=dict)


def _kolejnosc_pulapek(zapytan: int) -> list[str]:
    """Lista pulapek dlugosci ``zapytan``: przy 200 dokladnie wg ``PULAPKI``; inna liczba = proporcjonalnie (po kolei)."""
    wzor = [p for p, (n, _) in PULAPKI.items() for _ in range(n)]
    if zapytan == ZAPYTAN_WZOR:
        return wzor
    # przeplot: kolejno po jednym z kazdej pulapki, az do wyczerpania
    kolejki = {p: n for p, (n, _) in PULAPKI.items()}
    przeplot = []
    while len(przeplot) < ZAPYTAN_WZOR:
        for p in PULAPKI:
            if kolejki[p]:
                przeplot.append(p)
                kolejki[p] -= 1
    return [przeplot[i % ZAPYTAN_WZOR] for i in range(zapytan)]


def zbuduj(wierszy: int = 30000, zapytan: int = ZAPYTAN_WZOR, seed: int = 0, dzis: dt.date = DZIS) -> Zestaw:
    """Buduje arkusz ``wierszy`` wierszy danych (+ naglowek) i ``zapytan`` zapytan o znanej odpowiedzi."""
    rng = random.Random(seed)
    pulapki = _kolejnosc_pulapek(zapytan)
    nazwiska_sc = _pula_nazwisk(_RDZENIE_SC)
    nazwiska_tla = _pula_nazwisk(_RDZENIE_TLA)
    assert not set(nazwiska_sc) & set(nazwiska_tla)
    rng.shuffle(nazwiska_sc)
    nazwiska_nfd = _pula_nazwisk(_RDZENIE_NFD)
    rng.shuffle(nazwiska_nfd)
    if len(pulapki) > len(nazwiska_sc) - 50:
        raise ValueError(f"za duzo zapytan ({len(pulapki)}) - pula nazwisk scenariuszy ma {len(nazwiska_sc)}")
    # kuwety scenariuszy: rozne; male (< 1000) dla zer wiodacych, duze (>= 1000) dla fragmentow, 5000-9999 = "brak w arkuszu"
    male = rng.sample(range(1, 1000), 300)
    duze = rng.sample(range(1000, 4000), 2500)
    brak = rng.sample(range(5000, 10000), 100)
    numery_prywatne = rng.sample(range(1000, 2000), 100)
    uzyte_kuwety: set[int] = set()

    def kuweta_mala() -> int:
        k = male.pop()
        uzyte_kuwety.add(k)
        return k

    def kuweta_duza() -> int:
        k = duze.pop()
        uzyte_kuwety.add(k)
        return k

    numer_b = iter(range(40001, 40001 + 10 * wierszy))
    wiersze: list[_Wiersz] = []
    zapytania: list[Zapytanie] = []
    rola: dict[int, dict[str, _Wiersz]] = {}  # id zapytania -> {"prawdziwy": wiersz, ...}

    def dzien(od: int, do: int) -> dt.date:
        return dzis - dt.timedelta(days=rng.randint(od, do))

    def nowy(data: dt.date, c, h, kolor=None, i: str = "", b=None, a=None) -> _Wiersz:
        w = _Wiersz(data=data, a=a if a is not None else dt.datetime(data.year, data.month, data.day), b=b if b is not None else float(next(numer_b)),
                    c=c, h=h, i=i, kolor_b=kolor, klucz=rng.random(), d=rng.choice(GABINETY), e=rng.choice(RODZAJE), f=rng.randint(1, 6),
                    g=rng.choice(KOLORY_ZEBA))
        wiersze.append(w)
        return w

    def folder_wzor(nazwisko: str, k: int) -> str:
        """Nazwa folderu wg masek prawdziwych nazw (A4): "L D4 L", "L D4L", "L L. D4 L", "L D4 L L"."""
        wzor = rng.randrange(5)
        kod = rng.choice(KODY)
        if wzor == 0:
            return f"{nazwisko} {k} {kod}"
        if wzor == 1:
            return f"{nazwisko} {k}{kod.upper()}"
        if wzor == 2:
            return f"{nazwisko} {rng.choice('JAPEM')}. {k} {kod}"
        if wzor == 3:
            return f"{nazwisko} {k} {rng.choice(IMIONA)}"
        return f"{nazwisko}_{k}_{kod}"

    def inny() -> str:
        """Nazwa innej osoby (tlo) z ta sama kuweta - format jak w H."""
        return f"{rng.choice(nazwiska_tla)} {rng.randint(1, 3999)} {rng.choice(KODY)}"

    for qid, p in enumerate(pulapki):
        klasa = PULAPKI[p][1]
        nazw = nazwiska_sc.pop()
        r: dict[str, _Wiersz] = {}
        zrodlo, kuweta, folder = "cyrkon", None, ""
        if p in ("prosty", "ta_sama_kuweta_inne_daty", "pole_b_zielone", "pole_b_inny_kolor", "inicjal_imienia_w_h",
                 "inicjaly_zamiast_nazwiska", "puste_h", "puste_h_nowszy_inny", "reklamacja_nowy_wiersz", "reklamacja_oba_zielone",
                 "dwa_otwarte_to_samo_h", "duplikat_ta_sama_data", "zlecenie_bez_wiersza", "c_liczba_spacje", "data_tekstem",
                 "wielkosc_liter_spacje", "fragment_kuwety"):
            k = kuweta_duza()
            kuweta, folder = str(k), folder_wzor(nazw, k)
            c = float(k)
            if p == "prosty":
                r["prawdziwy"] = nowy(dzien(1, 9), c, folder)
            elif p == "ta_sama_kuweta_inne_daty":
                r["prawdziwy"] = nowy(dzien(1, 9), c, folder)
                for j in range(rng.randint(2, 3)):
                    nowy(dzien(60, 1000), float(k), "" if j == 2 else inny(), kolor=ZIELONY)
            elif p == "pole_b_zielone":
                r["prawdziwy"] = nowy(dzien(1, 9), c, folder, kolor=ZIELONY)
            elif p == "pole_b_inny_kolor":
                r["prawdziwy"] = nowy(dzien(1, 9), c, folder, kolor=ZOLTY)
            elif p == "inicjal_imienia_w_h":
                folder = f"{nazw} {k} {rng.choice(KODY)}"
                r["prawdziwy"] = nowy(dzien(1, 9), c, f"{nazw} {rng.choice('JAPEM')}. {k}")
            elif p == "inicjaly_zamiast_nazwiska":
                folder = f"{nazw} {k} {rng.choice(KODY)}"
                r["prawdziwy"] = nowy(dzien(1, 9), c, f"{nazw[0]}.{rng.choice('JAPEM')}. {k} {rng.choice(KODY)}")
            elif p == "puste_h":
                r["prawdziwy"] = nowy(dzien(1, 9), c, rng.choice(("", None)))
            elif p == "data_tekstem":
                d = dzien(1, 9)
                r["prawdziwy"] = nowy(d, c, "", a=d.strftime("%d.%m.%Y"))
                nowy(dzien(60, 600), float(k), inny(), kolor=ZIELONY)
            elif p == "puste_h_nowszy_inny":
                d = dzien(5, 9)
                r["prawdziwy"] = nowy(d, c, "")
                r["nowszy"] = nowy(d + dt.timedelta(days=rng.randint(1, 3)), float(k), inny())
            elif p == "reklamacja_nowy_wiersz":
                r["stary"] = nowy(dzien(15, 120), c, folder, kolor=ZIELONY)
                r["prawdziwy"] = nowy(dzien(1, 9), float(k), folder, i="reklamacja")
            elif p == "reklamacja_oba_zielone":
                r["stary"] = nowy(dzien(15, 120), c, folder, kolor=ZIELONY)
                r["prawdziwy"] = nowy(dzien(1, 9), float(k), folder, kolor=ZIELONY, i="reklamacja")
            elif p == "dwa_otwarte_to_samo_h":
                r["stary"] = nowy(dzien(10, 25), c, folder)
                r["prawdziwy"] = nowy(dzien(1, 9), float(k), folder)
            elif p == "duplikat_ta_sama_data":
                d = dzien(1, 9)
                r["prawdziwy"] = nowy(d, c, folder)
                r["drugi"] = nowy(d, float(k), folder)
            elif p == "zlecenie_bez_wiersza":
                r["inny"] = nowy(dzien(12, 29), c, inny(), kolor=rng.choice((ZIELONY, None)))
            elif p == "c_liczba_spacje":
                r["prawdziwy"] = nowy(dzien(1, 9), rng.choice((f" {k} ", k, str(k), f"{k} ")), folder)
            elif p == "wielkosc_liter_spacje":
                r["prawdziwy"] = nowy(dzien(1, 9), c, "  ".join(folder.upper().split()))
            elif p == "fragment_kuwety":
                d = dzien(5, 9)
                r["prawdziwy"] = nowy(d, c, folder)
                for wabik in (f"1{k}", f"{k}/2", f"{k}a", float(int(f"{k}1"))):
                    nowy(d + dt.timedelta(days=rng.randint(1, 4)), wabik, folder)
        elif p == "zera_wiodace":
            k = kuweta_mala()
            kuweta, folder = str(k), f"{nazw} {k:04d}"
            r["prawdziwy"] = nowy(dzien(1, 9), rng.choice((f"{k:04d}", f"{k:05d}")), rng.choice((folder, f"{nazw} {k}")))
            nowy(dzien(60, 900), float(k), inny(), kolor=ZIELONY)
        elif p == "kod_sklejony":
            k = kuweta_duza()
            kod = rng.choice(("PG", "AB", "ZS"))
            kuweta, folder = str(k), f"{nazw} {k}{kod}"
            r["prawdziwy"] = nowy(dzien(1, 9), float(k), f"{nazw} {k} {kod.lower()}")
        elif p == "nfd":
            k = kuweta_duza()
            nfc = nazwiska_nfd.pop()
            kod = rng.choice(KODY)
            kuweta, folder = str(k), unicodedata.normalize("NFD", f"{nfc} {k} {kod}")
            r["prawdziwy"] = nowy(dzien(1, 9), float(k), f"{nfc} {k} {kod}")
        elif p == "brak_kuwety_w_arkuszu":
            k = brak.pop()
            kuweta, folder = str(k), f"{nazw} {k} {rng.choice(KODY)}"
        elif p == "kuweta_niejednoznaczna":
            a, b = kuweta_duza(), kuweta_duza()
            kuweta, folder = f"?{a},{b}", f"{nazw} {a} {b}"
            r["prawdziwy"] = nowy(dzien(1, 9), float(b), folder)
        elif p == "brak_numeru":
            kuweta, folder = None, f"{nazw} {rng.choice(('zs', 'kor', 'PG', 'AB'))}"
        elif p.startswith("prywatne"):
            n = numery_prywatne.pop()
            zrodlo, kuweta = "prywatne", f"#{n}"
            folder = rng.choice((f"#{n}", f"#{n} {nazw}"))
            if p == "prywatne_numer_w_b":
                r["prawdziwy"] = nowy(dzien(1, 9), None, nazw, b=rng.choice((float(n), n, str(n))))
            elif p == "prywatne_numer_w_h":
                r["prawdziwy"] = nowy(dzien(1, 9), None, f"{nazw} #{n}")
            elif p == "prywatne_zielone":
                r["prawdziwy"] = nowy(dzien(1, 9), None, nazw, b=float(n), kolor=ZIELONY)
        else:  # pragma: no cover - nowa pulapka bez budowy
            raise ValueError(f"pulapka bez budowy: {p}")
        rola[qid] = r
        zapytania.append(Zapytanie(id=qid, pulapka=p, zrodlo=zrodlo, kuweta=kuweta, folder=folder, klasa=klasa))

    # tlo: reszta wierszy
    wolne_swieze = [k for k in range(1, 4000) if k not in uzyte_kuwety]
    tlo = wierszy - len(wiersze)
    if tlo < 0:
        raise ValueError(f"za malo wierszy ({wierszy}) na {len(wiersze)} wierszy scenariuszy")
    for _ in range(tlo):
        wiek = rng.randint(1, DNI_TLA)
        d = dzis - dt.timedelta(days=wiek)
        k = rng.choice(wolne_swieze) if wiek <= DNI_TLA_SWIEZEGO else rng.randint(1, 3999)
        los = rng.random()
        c = float(k) if los < 0.80 else str(k) if los < 0.95 else f" {k} " if los < 0.98 else f"{k:04d}"
        los = rng.random()
        nazw = rng.choice(nazwiska_tla)
        if los < 0.03:
            h = rng.choice(("", None))
        elif los < 0.05:
            h = f"{nazw[0]}.{rng.choice('JAPEM')}. {k}"
        else:
            h = folder_wzor(nazw, k)
        los = rng.random()
        a = data_seryjna(d) if los < 0.01 else d.strftime("%d.%m.%Y") if los < 0.015 else None
        kolor = ZIELONY if rng.random() < (0.97 if wiek > 10 else 0.4) else None
        los = rng.random()
        b = None if los < 0.85 else int(next(numer_b)) if los < 0.95 else str(next(numer_b))
        w = nowy(d, c, h, kolor=kolor, b=b, a=a, i=rng.choice(("",) * 30 + ("pilne", "poprawka", "reklamacja")))
        if rng.random() < 0.01:
            w.g = ""

    wiersze.sort(key=lambda w: (w.data, w.klucz))
    arkusz = ArkuszWPamieci("Zlecenia")
    for nr, w in enumerate(wiersze, start=PIERWSZY_WIERSZ):
        w.nr = nr
        arkusz._komorki.append([w.a, w.b, w.c, w.d, w.e, w.f, w.g, w.h, w.i])
        if w.kolor_b is not None:
            arkusz.zaznacz(nr, 2, w.kolor_b)
        if nr % 97 == 0:  # inne wypelnienia poza kolumna B (zakreslenia czlowieka) - program ich nie dotyka
            arkusz.zaznacz(nr, 8, ZOLTY)
    for z in zapytania:
        r = rola[z.id]
        z.prawdziwy = r["prawdziwy"].nr if "prawdziwy" in r else None
        if z.klasa in (KLASA_JEDEN, KLASA_JUZ):
            z.wiersz = z.prawdziwy
    liczniki = {"wierszy": len(wiersze), "scenariuszy_wierszy": len(wiersze) - tlo, "tlo": tlo, "zapytan": len(zapytania),
                "klasy": {k: sum(1 for z in zapytania if z.klasa == k) for k in (KLASA_JEDEN, KLASA_JUZ, KLASA_WSKAZ)},
                "zielonych_b": sum(1 for (_, kol) in arkusz._wypelnienia if kol == 2)}
    return Zestaw(arkusz=arkusz, zapytania=zapytania, liczniki=liczniki)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Arkusz syntetyczny zlecen (fikcyjne nazwy) i zapytania o znanej odpowiedzi.")
    ap.add_argument("--wierszy", type=int, default=30000)
    ap.add_argument("--zapytan", type=int, default=ZAPYTAN_WZOR)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--csv", type=Path, default=None, help="zapis podgladu arkusza (CSV, srednik)")
    a = ap.parse_args(argv)
    z = zbuduj(a.wierszy, a.zapytan, a.seed)
    print(f"wierszy {z.liczniki['wierszy']} (scenariusze {z.liczniki['scenariuszy_wierszy']}, tlo {z.liczniki['tlo']}); "
          f"zapytan {z.liczniki['zapytan']}: " + ", ".join(f"{k} {v}" for k, v in z.liczniki["klasy"].items()))
    if a.csv:
        z.arkusz.zapisz_csv(a.csv)
        print(f"CSV: {z.arkusz.ostatni_wiersz} wierszy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
