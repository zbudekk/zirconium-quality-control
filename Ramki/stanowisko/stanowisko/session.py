"""session - stan wieczoru: skany, prace, decyzje technika, ponowny skan, lista "do dofrezowania" (E3-A1).

Wejscie: wynik analizy jednego skanu (slownik z ``porownaj.porownaj``, ten sam co w ``<skan>_wynik.json``) razem ze
zdarzeniem skanu (plik, ``sha16``, rozmiar, czas pliku) oraz decyzje technika. Wyjscie: wiersze w bazie (``baza.py``,
plan etapu 3 sekcja 3.4) i funkcje stanu dla okna: ``stan_wieczoru``, ``do_dofrezowania``, ``konflikty``.

Caly stan jest w bazie - obiekt ``Sesja`` pamieta tylko wybrana osobe (operatora) i ustawienia, wiec po restarcie
programu nowa ``Sesja`` na tym samym pliku daje ten sam stan. Poranek (sesja pieca, punkty zlecen, braki) dojdzie
w paczce A6.

Zasady (plan: Z3, Z4, DW3; decyzje wlasciciela i koordynatora z 17.11.2026 po recenzji PR #16; szczegoly i granice:
``opisy_modulow/session.md``):
- "wieczor" = doba robocza, w ktorej program PRZYJAL skan (``skany.czas_analizy``): od godziny ``[sesja] granica_doby_godz``
  (6:00) do tej samej godziny nastepnego dnia, nazwana data POCZATKU (zmiany 1, 2 i 3 jednego dnia); data pliku skanu jest
  tylko informacja. Numer zmiany liczy ``Sesja.zmiana`` z ``[sesja] zmiany_start_godz``. Regula jest w jednym miejscu:
  ``Sesja.doba``, ``Sesja._przedzial_doby`` i ``Sesja.zmiana`` (bez kolumn w schemacie);
- skan ma status ``przyjety``, ``do_powtorzenia`` (drgniecie, dwie prace w gniezdzie, praca poza gniazdem - zadna praca
  takiego skanu nie liczy sie jako zielona), ``niezgodny_uklad``, ``zastapiony`` albo ``blad``; decyzje przyjmuje tylko
  praca skanu ``przyjety`` w trybie ``wieczor`` (skan ``rano`` jest przyjmowany do bazy, ale decyzje poranne obsluzy sesja
  poranna - A6; do tego czasu prace skanow porannych nie zmieniaja ``stan_punktow`` ani listy);
- plytka nie z tego trybu (poranna skanowana w trybie ``wieczor`` albo wieczorna w trybie ``rano``) = status
  ``plytka_nie_z_trybu``: skan nieaktywny jak ``niezgodny_uklad`` (0 zielonych, bez decyzji, poza listami, nie zastepuje
  i nie jest zastepowany), dopoki operator swiadomie go nie dopusci (``dopusc_plytke``; cofa ``cofnij_dopuszczenie``);
- decyzja technika zmienia kolor pracy w stanie wieczoru: "Ukruszona" = czerwony, "OK" = ``zatwierdzona_ok``; status
  z analizy zostaje w bazie bez zmian;
- ponowny skan: gdy ostatni niezastapiony skan tej samej plytki (numer i rodzina ukladu) przyjeto najwyzej
  ``[sesja] ponowny_skan_okno_min`` (60) minut wczesniej - takze po drugiej stronie granicy doby - i lezy na nim ten sam
  wsad (E3-A1p: |N & S| / min(|N|, |S|) >= ``[sesja] ponowny_skan_min_wspolnych``, N i S - zbiory projektow prac
  rozpoznanych nowego i poprzedniego skanu; ten sam plik skanu, mniej niz 3 projekty rozpoznane w ktoryms skanie albo prog 0 -
  bez tego warunku), program proponuje zastapienie; zastepuje dopiero potwierdzenie (``zastap_skan``), pomylke cofa
  ``cofnij_zastapienie``. Starszy skan tej samej plytki albo skan z innymi pracami to nowy wsad;
- lista "do dofrezowania" biezaca = wszystkie otwarte pozycje ze wszystkich dob (nie znika na granicy doby); widok doby to filtr;
- decyzje sa tylko dopisywane i zawsze maja operatora z listy ``[sesja] operatorzy`` (pusta lista = brak decyzji);
  cofniecie to kolejny wiersz (``rodzaj`` = ``cofniecie``, ``wartosc`` = id cofanej decyzji);
- nazwy folderow i plikow zlecen nie sa nigdzie zapisywane ani zwracane: tylko ``sha16``, numer kuwety, zeby, krazek;
  z pliku wyniku i z opisu bledu analizy wycinane sa sciezki (``baza.bez_sciezek``).

Modul korzysta tylko z biblioteki standardowej.
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import math
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Callable

from . import baza as B

TRYB_WIECZOR = "wieczor"
TRYB_RANO = "rano"
GRANICA_DOBY_GODZ = 6  # wartosci domyslne [sesja] granica_doby_godz, zmiany_start_godz, ponowny_skan_okno_min, ponowny_skan_min_wspolnych
ZMIANY_START_GODZ = (6, 14, 22)
PONOWNY_SKAN_OKNO_MIN = 60
PONOWNY_SKAN_MIN_WSPOLNYCH = 0.5  # E3-A1p: |N & S| / min(|N|, |S|) projektow rozpoznanych nowego i poprzedniego skanu plytki (0 = bez warunku)
PONOWNY_SKAN_MIN_ROZPOZNANYCH = 3  # mniej projektow rozpoznanych w nowym albo poprzednim skanie = brak podstaw do oceny wsadu: pytanie jak dawniej
# rano: skan tego samego pieca (``skany.sesja_pieca_id``) mozna zastapic bez warunku doby i okna 60 min (rozladunek pieca przez 06:00),
# o ile skany dzieli najwyzej tyle godzin - piec niezamkniety do nastepnego dnia to juz inny wsad tych samych numerow plytek
# (recenzja PR #22 runda 2, P1; rozladunek pieca trwa godziny, nie doby)
PONOWNY_SKAN_PIEC_MAX_H = 12
# podstawa propozycji "to ponowny skan?" (pole ``podstawa`` wpisu ``do_potwierdzenia``)
PODSTAWA_TEN_SAM_PLIK = "ten_sam_plik"
PODSTAWA_TE_SAME_PRACE = "te_same_prace"
PODSTAWA_ZA_MALO_ROZPOZNANYCH = "za_malo_rozpoznanych"
PODSTAWA_REGULA_WYLACZONA = "regula_wylaczona"

STATUS_PRZYJETY = "przyjety"
STATUS_DO_POWTORZENIA = "do_powtorzenia"
STATUS_ZASTAPIONY = "zastapiony"
STATUS_NIEZGODNY_UKLAD = "niezgodny_uklad"
STATUS_BLAD = "blad"
STATUS_PLYTKA_NIE_Z_TRYBU = "plytka_nie_z_trybu"  # plytka poranna skanowana w trybie wieczor albo odwrotnie: blokada (wlasciciel 17.11.2026)
STATUSY_AKTYWNE = (STATUS_PRZYJETY, STATUS_DO_POWTORZENIA)  # skany, ktorych prace licza sie do stanu i list
TYP_PLYTKI_TRYBU = {TRYB_WIECZOR: "wieczorna", TRYB_RANO: "poranna"}  # ktory typ plytki nalezy do ktorego trybu
DOPUSC_PLYTKE = "dopusc_plytke_nie_z_trybu"  # wartosc decyzji `uklad`: swiadome dopuszczenie skanu plytki nie z tego trybu

# statusy inspect, przy ktorych plytke trzeba zeskanowac ponownie (plan: SE7)
INSPEKCJA_DO_POWTORZENIA = ("skan_ponownie", "popraw_ulozenie")
FRAGMENTY_DO_POWTORZENIA = ("podwojny", "poza_gniazdem")

DECYZJE_UKRUSZENIA = ("ukruszona", "ukruszona_niewykryta")  # praca idzie na liste "do dofrezowania"
DECYZJE_O_PRACY = DECYZJE_UKRUSZENIA + ("ok",)
RODZAJ_COFNIECIE = "cofniecie"  # ponad liste z sekcji 3.4; zatwierdzone przez wlasciciela 17.11.2026
RODZAJ_COFNIJ_ZASTAPIENIE = "cofnij_zastapienie"  # ponad liste z sekcji 3.4 (recenzja PR #16, P6)
RODZAJE_POZNIEJSZYCH_PACZEK = ("wybor_kandydata", "przypisanie_reczne", "uklad")
RODZAJE = DECYZJE_O_PRACY + (RODZAJ_COFNIECIE, "powtorz_skan", RODZAJ_COFNIJ_ZASTAPIENIE, "numer_plytki") + RODZAJE_POZNIEJSZYCH_PACZEK

# kolory pracy po decyzji technika (kontrakt dla okna A3 i ramki A8; pozostale kolory to statusy gniazda z analizy)
KOLOR_UKRUSZONA = "czerwony"
KOLOR_ZATWIERDZONA_OK = "zatwierdzona_ok"

STAN_DO_DOFREZOWANIA = "do_dofrezowania"
STAN_OCZEKUJE = "oczekuje"

WERSJA_PROGRAMU = "etap3-A1"  # do ``skany.wersja_programu``, dopoki paczka wydania (A11) nie poda numeru wydania
KOLUMNY_LISTY = ("kuweta", "zeby", "krazek", "plytka", "gniazdo", "projekt", "doba", "zmiana")
SEKCJE_SKROTU = ("plytki", "match", "inspect")  # ustawienia, od ktorych zalezy wynik analizy skanu
OPIS_BLEDU_MAX = 500


class BladSesji(ValueError):
    """Operacja niemozliwa w tym stanie (brak pracy, skan nieprzyjety, brak operatora); komunikat dla okna, bez nazw osob i zlecen."""


def skrot_ustawien(ust: dict) -> str:
    """16 znakow SHA-256 ustawien analizy (``[plytki]``, ``[match]``, ``[inspect]``): przy jakich progach i ukladach liczono skan."""
    czesc = {s: ust.get(s) for s in SEKCJE_SKROTU}
    return hashlib.sha256(json.dumps(czesc, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")).hexdigest()[:16]


def katalog_wynikow(ust: dict) -> Path:
    """Katalog plikow wynikow skanow: ``[sciezki] wyniki`` (wzgledny od katalogu programu)."""
    return B.sciezka_z_ustawien(ust, "wyniki")


_WZOR_UKLADU = re.compile(r"^(?P<okragla>okragla_)?(?P<typ>wieczorna|poranna)(?P<wersja>_r\d+)?$")


def czesci_ukladu(nazwa: str | None) -> dict | None:
    """Nazwa ukladu z wyniku rozlozona na czesci: ksztalt (``okragla``), ``typ`` (wieczorna / poranna), ``wersja`` (np. ``_r54``).

    JEDYNE miejsce, w ktorym ``session`` czyta znaczenie nazwy ukladu (rodzina do ponownego skanu, typ do blokady trybu).
    None = nazwa spoza wzoru (uklad nieznany tej wersji programu).
    """
    m = _WZOR_UKLADU.match(nazwa) if nazwa else None
    return {"okragla": bool(m["okragla"]), "typ": m["typ"], "wersja": m["wersja"] or ""} if m else None


def rodzina_ukladu(nazwa: str | None) -> str | None:
    """Rodzina ukladu plytki: ten sam rozstaw stozkow i gniazd (kwadrat i kolo naleza do jednej): ``okragla_poranna_r54`` -> ``poranna_r54``."""
    c = czesci_ukladu(nazwa)
    return c["typ"] + c["wersja"] if c else nazwa


def typ_plytki(nazwa: str | None) -> str | None:
    """``wieczorna`` albo ``poranna`` dla kazdego ukladu tego typu (kwadrat, kolo, stary uklad ``_r54``); None dla nazwy nieznanej."""
    c = czesci_ukladu(nazwa)
    return c["typ"] if c else None


def sprawdz_tryb(tryb: Any) -> str:
    """Tryb pracy musi byc znany (``wieczor`` / ``rano``); literowka nie moze dac skanu przyjetego poza stanem wieczoru."""
    if tryb not in TYP_PLYTKI_TRYBU:
        raise BladSesji(f"nieznany tryb {tryb!r} (znane: {', '.join(TYP_PLYTKI_TRYBU)})")
    return tryb


def powod_nie_z_trybu(uklad: str | None, tryb: str | None) -> str | None:
    """Powod blokady skanu (np. "plytka poranna w trybie wieczor"); None = plytka pasuje do trybu.

    Blokada domyka sie na nieznanym: uklad o nazwie spoza wzoru (``czesci_ukladu`` nie zna jego typu) tez daje powod
    ("nieznany uklad plytki ..."), a nieznany tryb to ``BladSesji``.
    """
    sprawdz_tryb(tryb)
    typ = typ_plytki(uklad)
    if typ is None:
        return f"nieznany uklad plytki {uklad!r} w trybie {tryb}"
    return f"plytka {typ} w trybie {tryb}" if typ != TYP_PLYTKI_TRYBU[tryb] else None


def do_zapisu(wynik: dict) -> dict:
    """Wynik w postaci zapisywanej do pliku: bez ``foldery_projektow`` (zostaje liczba folderow) i bez sciezek w tekstach."""
    czysty = B.oczysc({k: v for k, v in wynik.items() if k != "foldery_projektow"})
    if "foldery_projektow" in wynik:
        czysty["foldery_projektow_liczba"] = len(wynik["foldery_projektow"] or [])
    return czysty


def _pole(zdarzenie: Any, nazwa: str) -> Any:
    """Pole zdarzenia skanu podanego jako slownik albo obiekt (``scanner.ZdarzenieSkanu`` powstaje w paczce A2)."""
    return zdarzenie.get(nazwa) if isinstance(zdarzenie, Mapping) else getattr(zdarzenie, nazwa, None)


def _czas_iso(v: Any) -> str | None:
    if v is None or v == "":
        return None
    if isinstance(v, (int, float)):
        v = dt.datetime.fromtimestamp(v)
    elif isinstance(v, str):
        try:
            v = dt.datetime.fromisoformat(v)
        except ValueError as e:
            raise BladSesji(f"czas {v!r} nie jest data w formacie ISO") from e
    return v.replace(microsecond=0, tzinfo=None).isoformat()


def _do_powtorzenia(wynik: dict) -> bool:
    """Czy wynik oznacza "zeskanuj plytke ponownie": drgniecie, dwie prace w gniezdzie, praca poza gniazdem."""
    if wynik.get("gniazda_podwojne") or (wynik.get("poza_gniazdem") or 0) > 0:
        return True
    for g in wynik.get("gniazda") or []:
        if g.get("status_fragmentu") in FRAGMENTY_DO_POWTORZENIA or (g.get("inspekcja") or {}).get("status") in INSPEKCJA_DO_POWTORZENIA:
            return True
    return False


def _obowiazujace(decyzje: list[dict]) -> dict[int, dict]:
    """Z wierszy ``decyzje`` (rosnaco po id): praca_id -> ostatnia niecofnieta decyzja "ukruszona" / "ok" / "ukruszona_niewykryta"."""
    cofniete = {int(d["wartosc"]) for d in decyzje if d["rodzaj"] == RODZAJ_COFNIECIE and str(d["wartosc"] or "").isdigit()}
    wynik: dict[int, dict] = {}
    for d in decyzje:
        if d["rodzaj"] in DECYZJE_O_PRACY and d["id"] not in cofniete:
            wynik[d["praca_id"]] = d
    return wynik


def _znaki(n: int) -> str:
    return ", ".join("?" * n)


class Sesja:
    """Stan wieczoru na otwartej bazie. Jedna instancja w procesie okna; nic poza operatorem nie jest trzymane w pamieci."""

    def __init__(self, baza: B.Baza, *, operatorzy: list[str] | tuple[str, ...] = (), katalog_wynikow: str | Path | None = None,
                 wersja_programu: str = WERSJA_PROGRAMU, skrot_ust: str | None = None, granica_doby_godz: int = GRANICA_DOBY_GODZ,
                 zmiany_start_godz: list[int] | tuple[int, ...] = ZMIANY_START_GODZ, ponowny_skan_okno_min: int = PONOWNY_SKAN_OKNO_MIN,
                 ponowny_skan_min_wspolnych: float = PONOWNY_SKAN_MIN_WSPOLNYCH, zegar: Callable[[], dt.datetime] | None = None):
        if not isinstance(granica_doby_godz, int) or not 0 <= granica_doby_godz <= 23:
            raise BladSesji(f"granica doby musi byc godzina 0-23 (jest {granica_doby_godz!r})")
        zmiany = tuple(zmiany_start_godz)
        if not zmiany or any(not isinstance(g, int) or not 0 <= g <= 23 for g in zmiany) or list(zmiany) != sorted(set(zmiany)):
            raise BladSesji(f"poczatki zmian musza byc rosnacymi godzinami 0-23 (jest {zmiany_start_godz!r})")
        if zmiany[0] != granica_doby_godz:
            raise BladSesji(f"pierwsza zmiana musi zaczynac sie o granicy doby ({granica_doby_godz}:00), a zaczyna sie o {zmiany[0]}:00")
        if not isinstance(ponowny_skan_okno_min, int) or ponowny_skan_okno_min < 1:
            raise BladSesji(f"okno ponownego skanu musi byc liczba minut > 0 (jest {ponowny_skan_okno_min!r})")
        prog = ponowny_skan_min_wspolnych
        if isinstance(prog, bool) or not isinstance(prog, (int, float)) or not math.isfinite(prog) or not 0 <= prog <= 1:
            raise BladSesji(f"prog wspolnych prac ponownego skanu musi byc udzialem z [0, 1] (jest {prog!r})")
        osoby = tuple(o.strip() if isinstance(o, str) else o for o in operatorzy)
        if any(not isinstance(o, str) or not o for o in osoby) or len(set(osoby)) != len(osoby):
            raise BladSesji("nazwy operatorow musza byc niepuste i rozne (po przycieciu bialych znakow)")
        self.baza = baza
        self.operatorzy = osoby  # lista osob z [sesja] operatorzy (DW3), bez bialych znakow na koncach; pusta = decyzje sa odrzucane
        self.operator: str | None = None  # osoba wybrana na poczatku zmiany
        self.katalog_wynikow = Path(katalog_wynikow) if katalog_wynikow is not None else None
        self.wersja_programu = wersja_programu
        self.skrot_ust = skrot_ust
        self.granica_doby_godz = granica_doby_godz
        self.zmiany_start_godz = zmiany
        self.ponowny_skan_okno_min = ponowny_skan_okno_min
        self.ponowny_skan_min_wspolnych = prog  # E3-A1p: 0 = pytanie o ponowny skan bez warunku zgodnosci prac (regula sprzed 18.11.2026)
        self._zegar = zegar or dt.datetime.now

    @classmethod
    def z_ustawien(cls, ust: dict, baza: B.Baza | None = None, **kw: Any) -> "Sesja":
        """Sesja wg ``ustawienia.toml``: ``[sciezki] baza`` i ``wyniki``; ``[sesja] operatorzy``, ``granica_doby_godz``,
        ``zmiany_start_godz``, ``ponowny_skan_okno_min``, ``ponowny_skan_min_wspolnych`` (brak klucza = wartosc domyslna)."""
        if baza is None:
            baza = B.otworz(B.sciezka_bazy(ust))
        return cls(baza, operatorzy=ust["sesja"]["operatorzy"], katalog_wynikow=katalog_wynikow(ust), skrot_ust=skrot_ustawien(ust),
                   granica_doby_godz=ust["sesja"]["granica_doby_godz"], zmiany_start_godz=ust["sesja"]["zmiany_start_godz"],
                   ponowny_skan_okno_min=ust["sesja"]["ponowny_skan_okno_min"],
                   ponowny_skan_min_wspolnych=ust["sesja"].get("ponowny_skan_min_wspolnych", PONOWNY_SKAN_MIN_WSPOLNYCH), **kw)

    # --- czas, doba robocza, zmiana i operator ----------------------------------------------------
    def teraz(self) -> str:
        return self._zegar().replace(microsecond=0).isoformat()

    def _chwila(self, czas: dt.datetime | str | None) -> dt.datetime:
        if czas is None:
            return self._zegar()
        return dt.datetime.fromisoformat(czas) if isinstance(czas, str) else czas

    def doba(self, czas: dt.datetime | str | None = None) -> str:
        """Data doby roboczej (RRRR-MM-DD), do ktorej nalezy chwila ``czas`` (domyslnie teraz) - tak nazywa sie "wieczor".

        Doba robocza trwa od godziny ``granica_doby_godz`` (6:00) do tej samej godziny nastepnego dnia i nosi date POCZATKU:
        skany z 06:10, 23:59 i z 05:55 nastepnego dnia to jedna doba. Zaklad pracuje na trzy zmiany, wiec doba nie ma przerwy -
        ponowny skan plytki NIE zalezy od tej granicy (``_poprzedni_skan``). Regula jest tylko tu i w ``_przedzial_doby``.
        """
        return (self._chwila(czas) - dt.timedelta(hours=self.granica_doby_godz)).date().isoformat()

    def _przedzial_doby(self, data: str) -> tuple[str, str]:
        """Poczatek (wlacznie) i koniec (bez) doby roboczej ``data`` jako czasy ISO - do porownan z ``skany.czas_analizy``."""
        try:
            od = dt.datetime.combine(dt.date.fromisoformat(data), dt.time(self.granica_doby_godz))
        except (TypeError, ValueError) as e:
            raise BladSesji(f"data doby {data!r} nie ma postaci RRRR-MM-DD") from e
        return od.isoformat(), (od + dt.timedelta(days=1)).isoformat()

    def zmiana(self, czas: dt.datetime | str | None = None) -> int:
        """Numer zmiany (1, 2, 3, ...) dla chwili ``czas`` (domyslnie teraz) wg ``zmiany_start_godz`` (6, 14, 22).

        Liczony z czasu (przyjecia skanu, decyzji) - w bazie nie ma na to kolumny. Chwila przed poczatkiem pierwszej zmiany
        nalezy do ostatniej zmiany poprzedniego dnia (05:55 = zmiana 3).
        """
        godzina = self._chwila(czas).hour
        zaczete = [i for i, start in enumerate(self.zmiany_start_godz, start=1) if start <= godzina]
        return zaczete[-1] if zaczete else len(self.zmiany_start_godz)

    def wybierz_operatora(self, nazwa: str) -> None:
        """Wybor osoby na poczatku zmiany (DW3): jej nazwa trafia do kolumny ``operator`` kazdej decyzji."""
        self.operator = self._operator(nazwa)

    def _operator(self, podany: str | None = None) -> str:
        """Osoba do kolumny ``operator``. Lista jest wymagana (decyzja wlasciciela z 17.11.2026); komunikaty nie zawieraja nazw osob."""
        if not self.operatorzy:
            raise BladSesji("lista operatorow jest pusta - dopisz osoby w ustawienia.toml ([sesja] operatorzy) i uruchom program ponownie; "
                            "bez wskazanej osoby decyzje nie sa zapisywane")
        nazwa = podany if podany is not None else self.operator
        nazwa = nazwa.strip() if isinstance(nazwa, str) else nazwa
        if not nazwa:
            raise BladSesji("nie wybrano operatora - wybierz osobe z listy; bez wskazanej osoby decyzje nie sa zapisywane")
        if nazwa not in self.operatorzy:
            raise BladSesji("wskazanej osoby nie ma na liscie operatorow ([sesja] operatorzy w ustawienia.toml)")
        return nazwa

    # --- przyjecie wyniku skanu ----------------------------------------------------------------
    def przyjmij_wynik(self, zdarzenie: Any, wynik: dict, tryb: str = TRYB_WIECZOR) -> int:
        """Zapisuje skan i jego prace (jedna praca = jeden wpis ``wynik["gniazda"]``); zwraca ``skany.id``.

        ``zdarzenie``: slownik albo obiekt z polami ``plik``, ``sha16``, ``rozmiar``, ``czas_pliku`` (kontrakt
        ``ZdarzenieSkanu`` z sekcji 3.8 planu). Skan nalezy do doby roboczej, w ktorej zostal przyjety (``czas_analizy`` = teraz).
        Wynik jest zapisywany do ``katalog_wynikow`` bez ``foldery_projektow`` i bez sciezek w tekstach (``do_zapisu``), w pliku
        ``<czas przyjecia>_<sha16 skanu>_wynik.json`` (bez nazwy pliku skanu; ta zostaje tylko w ``skany.plik``).
        Niczego nie zastepuje - ponowny skan plytki wymaga potwierdzenia (``zastap_skan``). Nie wymaga operatora.
        Plytka nie z tego trybu (poranna wieczorem albo wieczorna rano) = status ``plytka_nie_z_trybu``: skan nieaktywny,
        dopoki operator swiadomie go nie dopusci (``dopusc_plytke``).
        """
        sprawdz_tryb(tryb)
        plik = _pole(zdarzenie, "plik")
        if not plik:
            raise BladSesji("zdarzenie skanu bez nazwy pliku")
        teraz = self.teraz()
        doba = self.doba(teraz)
        gniazda = wynik.get("gniazda") or []
        zgodny = wynik.get("uklad_zgodny")
        if zgodny is False:
            status = STATUS_NIEZGODNY_UKLAD
        elif powod_nie_z_trybu(wynik.get("plytka"), tryb) is not None:  # takze uklad o nieznanej nazwie
            status = STATUS_PLYTKA_NIE_Z_TRYBU
        elif _do_powtorzenia(wynik):
            status = STATUS_DO_POWTORZENIA
        else:
            status = STATUS_PRZYJETY
        wybor = wynik.get("plytka_wybor")
        # konflikt projektu (SE8) to regula WIECZORU: skan poranny nie dostaje wpisu ``konflikt_projektu`` w dzienniku (ta sama
        # praca w dwoch piecach doby to nie konflikt; konflikty poranka liczy sesja poranna - recenzja PR #23 D6)
        wieczor = tryb == TRYB_WIECZOR
        with self.baza.transakcja():
            przed = {k["sha16"] for k in self.konflikty(doba, tryb)} if wieczor else set()
            sha16 = _pole(zdarzenie, "sha16") or wynik.get("skan_sha16")
            skan_id = self.baza.wstaw(
                "skany", plik=str(plik), sha16=sha16, rozmiar=_pole(zdarzenie, "rozmiar"),
                czas_pliku=_czas_iso(_pole(zdarzenie, "czas_pliku")), czas_analizy=teraz, czas_s=(wynik.get("czas_s") or {}).get("razem"),
                tryb=tryb, uklad=wynik.get("plytka"), uklad_zrodlo=("auto" if wybor == "auto" else "reczny") if wybor else None,
                uklad_zgodny=None if zgodny is None else int(bool(zgodny)), numer_plytki=wynik.get("numer"),
                numer_zrodlo=wynik.get("numer_zrodlo"), status=status, wersja_programu=self.wersja_programu, skrot_ustawien=self.skrot_ust)
            w_gniezdzie: dict[Any, int] = {}
            for g in gniazda:
                w_gniezdzie[g.get("gniazdo")] = w_gniezdzie.get(g.get("gniazdo"), 0) + 1
                self._wstaw_prace(skan_id, g, w_gniezdzie[g.get("gniazdo")], wynik)
            if self.katalog_wynikow is not None:
                self.baza.wykonaj("UPDATE skany SET wynik_json = ? WHERE id = ?", (self._zapisz_wynik(wynik, teraz, sha16), skan_id))
            self.baza.zdarzenie("silnik", "skan_przyjety", {"status": status, "prace": len(gniazda), "czas_s": (wynik.get("czas_s") or {}).get("razem")},
                                skan_id=skan_id, czas=teraz)
            nowe = [k["sha16"] for k in self.konflikty(doba, tryb) if k["sha16"] not in przed] if wieczor else []
            if nowe:  # SE8: ten sam projekt w dwoch gniazdach wieczoru - zgloszenie do rozstrzygniecia
                self.baza.zdarzenie("system", "konflikt_projektu", {"sha16": nowe}, skan_id=skan_id, czas=teraz)
        return skan_id

    def przyjmij_blad(self, zdarzenie: Any, blad: BaseException | str, tryb: str = TRYB_WIECZOR) -> int:
        """Analiza skanu nie dala wyniku (awaria silnika, zly plik): skan ze statusem ``blad`` i wpis w dzienniku.

        Do ``zdarzenia.dane`` ida: ``typ`` (nazwa klasy wyjatku; dla tekstu brak) i ``opis`` - tresc z wycietymi sciezkami,
        najwyzej 500 znakow. Dziennika nie da sie poprawic, wiec pelnego tekstu wyjatku (ze sciezka folderu zlecenia)
        nie wolno tu wkladac inna droga.
        """
        sprawdz_tryb(tryb)
        plik = _pole(zdarzenie, "plik")
        if not plik:
            raise BladSesji("zdarzenie skanu bez nazwy pliku")
        typ = type(blad).__name__ if isinstance(blad, BaseException) else None
        opis = B.bez_sciezek(str(blad))[:OPIS_BLEDU_MAX]
        teraz = self.teraz()
        with self.baza.transakcja():
            skan_id = self.baza.wstaw("skany", plik=str(plik), sha16=_pole(zdarzenie, "sha16"), rozmiar=_pole(zdarzenie, "rozmiar"),
                                      czas_pliku=_czas_iso(_pole(zdarzenie, "czas_pliku")), czas_analizy=teraz, tryb=tryb, status=STATUS_BLAD,
                                      wersja_programu=self.wersja_programu, skrot_ustawien=self.skrot_ust)
            self.baza.zdarzenie("silnik", "blad_analizy", {"typ": typ, "opis": opis}, skan_id=skan_id, czas=teraz)
        return skan_id

    def _wstaw_prace(self, skan_id: int, g: dict, nr_fragmentu: int, wynik: dict) -> int:
        kandydaci = g.get("kandydaci") or []
        k1 = kandydaci[0] if kandydaci else None
        k2 = kandydaci[1] if len(kandydaci) > 1 else None
        ins = g.get("inspekcja")
        skala = g.get("skala") or {}
        projekt_id = frezowanie_id = None
        if k1 is not None and g.get("status") != "szary":  # praca szara ("bez projektu") nie ma przypisania
            projekt_id = self._projekt(k1.get("id"))
            frezowanie_id = self._frezowanie(projekt_id, k1)
        ubytki = (ins.get("ubytki") or []) if ins else None
        return self.baza.wstaw(
            "prace", skan_id=skan_id, gniazdo=g.get("gniazdo"), nr_fragmentu=nr_fragmentu, status_fragmentu=g.get("status_fragmentu"),
            status_match=g.get("status"), status_inspekcji=ins.get("status") if ins else None, status_gniazda=g.get("status_gniazda"),
            kandydat1_sha16=k1.get("id") if k1 else None, kandydat1_pokrycie=k1.get("pokrycie") if k1 else None,
            kandydat2_sha16=k2.get("id") if k2 else None, kandydat2_pokrycie=k2.get("pokrycie") if k2 else None,
            pewnosc=g.get("pewnosc"), frezowanie_id=frezowanie_id,
            wspolczynnik=skala.get("wspolczynnik_puli") if skala.get("wspolczynnik_puli") is not None else wynik.get("wspolczynnik"),
            korekta_skali=skala.get("poprawka_proc"), ubytki=len(ubytki) if ubytki is not None else None,
            ubytek_max_mm=max((u.get("srednica_mm") or 0.0 for u in ubytki), default=None) if ubytki else None, projekt_id=projekt_id)

    def _projekt(self, sha16: str | None) -> int | None:
        """Punkt pracy z indeksu po ``sha16``; brak albo wiecej niz jeden (ten sam plik w dwoch zleceniach) = bez przypisania."""
        if not sha16:
            return None
        w = self.baza.wiersze("SELECT id FROM projekty WHERE sha16 = ? AND usuniety = 0 ORDER BY id LIMIT 2", (sha16,))
        return w[0]["id"] if len(w) == 1 else None

    def _frezowanie(self, projekt_id: int | None, kandydat: dict) -> int | None:
        """Wpis frezowania pracy: wskazany przez wynik (pula ze wspolczynnikiem per praca, A5); inaczej jedyny wpis projektu.

        Projekt z kilkoma wpisami (zab frezowany na dwoch krazkach, K4) bez wskazania w wyniku: brak - program nie zgaduje krazka.
        """
        wskazany = kandydat.get("frezowanie_id")
        if wskazany is not None and self.baza.wiersz("SELECT id FROM frezowania WHERE id = ?", (wskazany,)):
            return int(wskazany)
        if projekt_id is None:
            return None
        w = self.baza.wiersze("SELECT id FROM frezowania WHERE projekt_id = ? ORDER BY id LIMIT 2", (projekt_id,))
        return w[0]["id"] if len(w) == 1 else None

    def _zapisz_wynik(self, wynik: dict, czas: str, sha16: str | None) -> str:
        """Zapisuje wynik (``do_zapisu``) do ``katalog_wynikow``; zwraca sciezke do ``skany.wynik_json`` (wzgledna od folderu bazy, gdy sie da).

        Nazwa pliku nie zalezy od numeracji bazy ani od nazwy pliku skanu: ``<czas przyjecia>_<sha16 skanu>_wynik.json`` (skaner moze
        nazywac pliki wg zlecenia, a nazwa skanu wydluzala nazwe ponad 255 znakow - recenzja PR #16 runda 3, D1 i D2). Istniejacego
        pliku NIGDY nie nadpisuje ani nie usuwa (wyniki sa trzymane bezterminowo, takze po zalozeniu bazy od nowa albo przywroceniu
        jej z kopii): gdy nazwa jest zajeta, dostaje przyrostek ``_2``, ``_3``... Plik powstaje przed zatwierdzeniem transakcji
        (blad zapisu wycofuje caly skan); po zabitym procesie moze zostac plik bez wiersza w bazie - wypisuje je ``osierocone_wyniki``.
        """
        self.katalog_wynikow.mkdir(parents=True, exist_ok=True)
        skrot = re.sub(r"[^0-9A-Za-z]", "", str(sha16 or "")) or "bezskrotu"
        podstawa = f"{dt.datetime.fromisoformat(czas):%Y%m%d_%H%M%S}_{skrot}"
        tresc = json.dumps(do_zapisu(wynik), ensure_ascii=False, indent=1)
        nr = 1
        while True:
            cel = self.katalog_wynikow / (f"{podstawa}_wynik.json" if nr == 1 else f"{podstawa}_{nr}_wynik.json")
            try:
                with open(cel, "x", encoding="utf-8") as f:  # "x": odmowa nadpisania istniejacego pliku
                    f.write(tresc)
                break
            except FileExistsError:
                nr += 1
        try:
            return cel.resolve().relative_to(self.baza.plik.resolve().parent).as_posix()
        except ValueError:
            return cel.resolve().as_posix()

    def osierocone_wyniki(self) -> list[Path]:
        """Pliki ``*_wynik.json`` w ``katalog_wynikow``, do ktorych nie prowadzi zaden skan tej bazy (kontrola; niczego nie usuwa).

        Powstaja po przerwanym przyjeciu skanu, po zalozeniu bazy od nowa albo po przywroceniu jej z kopii.
        """
        if self.katalog_wynikow is None or not self.katalog_wynikow.is_dir():
            return []
        znane = set()
        for w in self.baza.wiersze("SELECT wynik_json FROM skany WHERE wynik_json IS NOT NULL"):
            sciezka = Path(w["wynik_json"])
            znane.add((sciezka if sciezka.is_absolute() else self.baza.plik.parent / sciezka).resolve())
        return sorted(x for x in self.katalog_wynikow.glob("*_wynik.json") if x.resolve() not in znane)

    def sciezka_wyniku(self, skan_id: int) -> Path | None:
        """Plik wyniku skanu (``skany.wynik_json``) jako sciezka bezwzgledna; None, gdy wyniku nie zapisano."""
        w = self.baza.wiersz("SELECT wynik_json FROM skany WHERE id = ?", (skan_id,))
        if w is None or not w["wynik_json"]:
            return None
        p = Path(w["wynik_json"])
        return p if p.is_absolute() else self.baza.plik.parent / p

    # --- decyzje ---------------------------------------------------------------------------------
    def decyzja(self, praca_id: int | None, rodzaj: str, wartosc: Any = None, operator: str | None = None, *, skan_id: int | None = None) -> int:
        """Dopisuje decyzje technika i aktualizuje stan; zwraca ``decyzje.id``.

        Rodzaje obslugiwane wieczorem: ``ukruszona``, ``ok``, ``ukruszona_niewykryta`` (tryb cienia), ``cofniecie``
        (dla ``praca_id``; tylko praca skanu ``przyjety`` w trybie ``wieczor`` - skan ``rano`` = ``BladSesji`` do A6) oraz ``powtorz_skan``, ``cofnij_zastapienie``, ``numer_plytki``,
        ``uklad`` z wartoscia ``dopusc_plytke_nie_z_trybu`` i jej ``cofniecie`` (dla ``skan_id``). Kazda decyzja wymaga operatora
        z listy; ``operator``: osoba inna niz wybrana na poczatku zmiany.
        """
        if rodzaj not in RODZAJE:
            raise BladSesji(f"nieznany rodzaj decyzji {rodzaj!r} (znane: {', '.join(RODZAJE)})")
        if rodzaj == "uklad" and wartosc == DOPUSC_PLYTKE:
            return self.dopusc_plytke(skan_id, operator)
        if rodzaj == RODZAJ_COFNIECIE and praca_id is None and skan_id is not None:
            return self.cofnij_dopuszczenie(skan_id, operator)
        if rodzaj in RODZAJE_POZNIEJSZYCH_PACZEK:
            raise BladSesji(f"rodzaj decyzji {rodzaj!r} nie jest obslugiwany przez sesje wieczorna (dojdzie w kolejnych paczkach etapu 3)")
        if rodzaj == "powtorz_skan":
            return self._zastap(skan_id, int(wartosc) if wartosc not in (None, "") else None, operator)[0]
        if rodzaj == RODZAJ_COFNIJ_ZASTAPIENIE:
            return self.cofnij_zastapienie(skan_id, operator)
        if rodzaj == "numer_plytki":
            return self.podaj_numer_plytki(skan_id, wartosc, operator)
        if rodzaj == RODZAJ_COFNIECIE:
            return self.cofnij(praca_id, operator)
        osoba = self._operator(operator)
        with self.baza.transakcja():
            praca = self._praca_do_decyzji(praca_id)
            byla = self._punkt_na_liscie(praca["projekt_id"]) if rodzaj in DECYZJE_UKRUSZENIA else None
            teraz = self.teraz()
            decyzja_id = self.baza.wstaw("decyzje", praca_id=praca["id"], rodzaj=rodzaj, operator=osoba, czas=teraz)
            self._odswiez_punkt(praca, praca["tryb_skanu"])
            if byla is not None and byla["praca_id"] != praca["id"]:  # ten zab jest juz na liscie: pozycja przechodzi na te prace, nie powstaje druga
                self.baza.zdarzenie("system", "ukruszona_powtorzona", {
                    "praca_id": praca["id"], "byla_praca_id": byla["praca_id"], "byl_skan_id": byla["skan_id"],
                    "doba": self.doba(byla["czas_analizy"]), "zmiana": self.zmiana(byla["czas_analizy"])}, skan_id=praca["skan_id"], czas=teraz)
        return decyzja_id

    def _punkt_na_liscie(self, projekt_id: int | None) -> dict | None:
        """Praca, na ktora wskazuje punkt projektu w stanie ``do_dofrezowania`` (razem ze skanem), albo None."""
        if projekt_id is None:
            return None
        return self.baza.wiersz(
            "SELECT sp.praca_id, p.skan_id, s.czas_analizy FROM stan_punktow sp JOIN prace p ON p.id = sp.praca_id JOIN skany s ON s.id = p.skan_id "
            "WHERE sp.projekt_id = ? AND sp.stan = ?", (projekt_id, STAN_DO_DOFREZOWANIA))

    def pozycja_projektu(self, praca_id: int) -> dict | None:
        """Pozycja listy "do dofrezowania" dla projektu tej pracy (None, gdy zeba nie ma na liscie).

        Dla okna: przed kliknieciem "Ukruszona" mozna pokazac "ten zab jest juz na liscie (skan X, zmiana Y)" - pola
        ``skan_id``, ``doba``, ``zmiana`` pozycji. Druga "Ukruszona" na tym samym projekcie nie tworzy drugiej pozycji.
        """
        praca = self.baza.wiersz("SELECT id, projekt_id FROM prace WHERE id = ?", (praca_id,))
        if praca is None:
            raise BladSesji(f"nie ma pracy {praca_id}")
        for x in self.do_dofrezowania():
            if (x["projekt_id"] == praca["projekt_id"]) if praca["projekt_id"] is not None else (x["praca_id"] == praca_id):
                return x
        return None

    def ukruszona(self, praca_id: int, operator: str | None = None) -> int:
        """Przycisk "Ukruszona": praca robi sie czerwona i idzie na liste "do dofrezowania"."""
        return self.decyzja(praca_id, "ukruszona", operator=operator)

    def ok(self, praca_id: int, operator: str | None = None) -> int:
        """Przycisk "OK": falszywy alarm programu; praca dostaje kolor ``zatwierdzona_ok``."""
        return self.decyzja(praca_id, "ok", operator=operator)

    def cofnij(self, praca_id: int, operator: str | None = None) -> int:
        """Cofa obowiazujaca decyzje o pracy (wraca poprzednia niecofnieta albo brak decyzji); dopisuje wiersz ``cofniecie``."""
        osoba = self._operator(operator)
        with self.baza.transakcja():
            praca = self._praca_do_decyzji(praca_id)
            obowiazujaca = self._decyzja_pracy(praca["id"])
            if obowiazujaca is None:
                raise BladSesji(f"praca {praca_id}: nie ma decyzji do cofniecia")
            decyzja_id = self.baza.wstaw("decyzje", praca_id=praca["id"], rodzaj=RODZAJ_COFNIECIE, wartosc=str(obowiazujaca["id"]),
                                         operator=osoba, czas=self.teraz())
            self._odswiez_punkt(praca, praca["tryb_skanu"])
        return decyzja_id

    def zastap_skan(self, skan_id: int, poprzedni_id: int | None = None, operator: str | None = None) -> int:
        """Potwierdzenie "to ponowny skan tej plytki" (zalozenie Z4): poprzedni skan dostaje status ``zastapiony``.

        Bez ``poprzedni_id`` zastepowany jest skan wskazany w ``stan_wieczoru`` jako ``moze_zastapic`` (ostatni skan tej plytki,
        przyjety w oknie ``ponowny_skan_okno_min``, z tymi samymi pracami - ``_propozycja_zastapienia``). Z ``poprzedni_id``:
        dowolny wczesniejszy aktywny skan z tej samej doby roboczej albo z okna, bez warunku zgodnosci prac. Odmowa, gdy skany
        maja rozne numery plytek albo rozne rodziny ukladu. Zwraca id skanu zastapionego; pomylke cofa ``cofnij_zastapienie``.
        """
        return self._zastap(skan_id, poprzedni_id, operator)[1]

    def cofnij_zastapienie(self, skan_id: int, operator: str | None = None) -> int:
        """Cofa pomylkowe "to ponowny skan": skan zastapiony przez ``skan_id`` wraca do stanu i list razem ze swoimi decyzjami.

        Dopisuje decyzje ``cofnij_zastapienie`` (``skan_id`` = nowszy skan, ``wartosc`` = id skanu przywroconego); oba skany sa
        potem aktywne, a program nie proponuje ponownie tego samego zastapienia. Zwraca ``decyzje.id``.
        """
        osoba = self._operator(operator)
        with self.baza.transakcja():
            nowy = self._skan(skan_id)
            if nowy["zastepuje_id"] is None:
                raise BladSesji(f"skan {skan_id} nie zastepuje zadnego skanu - nie ma czego cofac")
            stary = self._skan(nowy["zastepuje_id"])
            if nowy["status"] not in STATUSY_AKTYWNE or stary["status"] != STATUS_ZASTAPIONY:
                raise BladSesji(f"zastapienia skanu {stary['id']} skanem {skan_id} nie da sie cofnac: skan {skan_id} ma status {nowy['status']!r}, "
                                f"skan {stary['id']} - {stary['status']!r} (najpierw cofnij pozniejsze zastapienie)")
            decyzja_id = self.baza.wstaw("decyzje", skan_id=nowy["id"], rodzaj=RODZAJ_COFNIJ_ZASTAPIENIE, wartosc=str(stary["id"]),
                                         operator=osoba, czas=self.teraz())
            self.baza.wykonaj("UPDATE skany SET status = ? WHERE id = ?", (self._status_z_prac(stary["id"]), stary["id"]))
            self.baza.wykonaj("UPDATE skany SET zastepuje_id = NULL WHERE id = ?", (nowy["id"],))
            self._przelicz_punkty_skanu(stary, aktywny=True)  # decyzje przywroconego skanu znow sie licza
        return decyzja_id

    def dopusc_plytke(self, skan_id: int, operator: str | None = None) -> int:
        """Swiadome dopuszczenie skanu ``plytka_nie_z_trybu`` (np. proba na dniu skanera): skan przechodzi na ``przyjety``
        (albo ``do_powtorzenia``, jesli tak wynika z prac) i jest liczony normalnie.

        Dopisuje decyzje ``rodzaj`` = ``uklad``, ``wartosc`` = ``dopusc_plytke_nie_z_trybu`` (z operatorem) i wpis w dzienniku.
        Zwraca ``decyzje.id``; blokade przywraca ``cofnij_dopuszczenie``.
        """
        osoba = self._operator(operator)
        with self.baza.transakcja():
            sk = self._skan(skan_id)
            if sk["status"] != STATUS_PLYTKA_NIE_Z_TRYBU:
                raise BladSesji(f"skan {skan_id} ma status {sk['status']!r} - dopuscic mozna tylko skan plytki nie z tego trybu")
            teraz = self.teraz()
            decyzja_id = self.baza.wstaw("decyzje", skan_id=skan_id, rodzaj="uklad", wartosc=DOPUSC_PLYTKE, operator=osoba, czas=teraz)
            status = self._status_z_prac(skan_id)
            self.baza.wykonaj("UPDATE skany SET status = ? WHERE id = ?", (status, skan_id))
            self._przelicz_punkty_skanu(sk, aktywny=True)  # decyzje sprzed cofnietego dopuszczenia znow sie licza
            self.baza.zdarzenie("ui", "plytka_nie_z_trybu_dopuszczona", {"decyzja_id": decyzja_id, "status": status, "uklad": sk["uklad"], "tryb": sk["tryb"]},
                                skan_id=skan_id, czas=teraz)
        return decyzja_id

    def cofnij_dopuszczenie(self, skan_id: int, operator: str | None = None) -> int:
        """Cofa dopuszczenie skanu plytki nie z tego trybu: wraca status ``plytka_nie_z_trybu``, a decyzje o pracach tego skanu
        przestaja sie liczyc (zostaja w bazie). Dopisuje wiersz ``cofniecie`` wskazujacy decyzje dopuszczenia; zwraca ``decyzje.id``."""
        osoba = self._operator(operator)
        with self.baza.transakcja():
            sk = self._skan(skan_id)
            dopuszczenia = self.baza.wiersze("SELECT id FROM decyzje WHERE skan_id = ? AND rodzaj = 'uklad' AND wartosc = ? ORDER BY id", (skan_id, DOPUSC_PLYTKE))
            cofniete = {int(d["wartosc"]) for d in self.baza.wiersze("SELECT wartosc FROM decyzje WHERE skan_id = ? AND praca_id IS NULL AND rodzaj = ?",
                                                                     (skan_id, RODZAJ_COFNIECIE)) if str(d["wartosc"] or "").isdigit()}
            obowiazujace = [d["id"] for d in dopuszczenia if d["id"] not in cofniete]
            if not obowiazujace or sk["status"] not in STATUSY_AKTYWNE:
                raise BladSesji(f"skan {skan_id}: nie ma dopuszczenia do cofniecia (status {sk['status']!r})")
            if sk["zastepuje_id"] is not None:  # plytka nie moze po cichu zostac bez aktywnego skanu
                raise BladSesji(f"skan {skan_id} zastapil skan {sk['zastepuje_id']} - najpierw cofnij zastapienie (poprzedni skan plytki wroci do stanu), "
                                f"potem cofnij dopuszczenie")
            teraz = self.teraz()
            decyzja_id = self.baza.wstaw("decyzje", skan_id=skan_id, rodzaj=RODZAJ_COFNIECIE, wartosc=str(obowiazujace[-1]), operator=osoba, czas=teraz)
            self.baza.wykonaj("UPDATE skany SET status = ? WHERE id = ?", (STATUS_PLYTKA_NIE_Z_TRYBU, skan_id))
            self._przelicz_punkty_skanu(sk, aktywny=False)
            self.baza.zdarzenie("ui", "plytka_nie_z_trybu_blokada_przywrocona", {"decyzja_id": decyzja_id}, skan_id=skan_id, czas=teraz)
        return decyzja_id

    def _przelicz_punkty_skanu(self, sk: dict, aktywny: bool) -> None:
        """Uzgadnia ``stan_punktow`` dla wszystkich prac skanu po zmianie jego statusu (skan przestal albo zaczal sie liczyc)."""
        for praca in self.baza.wiersze("SELECT * FROM prace WHERE skan_id = ? AND projekt_id IS NOT NULL ORDER BY id", (sk["id"],)):
            self._odswiez_punkt(praca, sk["tryb"], aktywna=aktywny)

    def podaj_numer_plytki(self, skan_id: int, numer: Any, operator: str | None = None) -> int:
        """Numer plytki wskazany recznie (dolki kodu poza polem skanu, zalozenie Z3); zwraca ``decyzje.id``."""
        try:
            n = int(numer)
        except (TypeError, ValueError):
            n = 0
        if n < 1:
            raise BladSesji(f"numer plytki musi byc liczba od 1 w gore (jest {numer!r})")
        osoba = self._operator(operator)
        with self.baza.transakcja():
            sk = self._skan(skan_id)
            powiazane = self.baza.wiersze("SELECT * FROM skany WHERE zastepuje_id = ? OR id = ?", (skan_id, sk["zastepuje_id"]))
            for inny in powiazane:  # skan, ktory ten zastapil, albo skan, ktory zastapil ten
                if inny["numer_plytki"] is not None and inny["numer_plytki"] != n and not (sk["sha16"] and sk["sha16"] == inny["sha16"]):
                    raise BladSesji(f"skan {skan_id} jest powiazany zastapieniem ze skanem {inny['id']} plytki nr {inny['numer_plytki']} - "
                                    f"inny numer plytki ({n}) oznaczalby inna plytke; najpierw cofnij zastapienie")
            decyzja_id = self.baza.wstaw("decyzje", skan_id=skan_id, rodzaj="numer_plytki", wartosc=str(n), operator=osoba, czas=self.teraz())
            self.baza.wykonaj("UPDATE skany SET numer_plytki = ?, numer_zrodlo = 'podany' WHERE id = ?", (n, skan_id))
        return decyzja_id

    def _skan(self, skan_id: int | None) -> dict:
        sk = self.baza.wiersz("SELECT * FROM skany WHERE id = ?", (skan_id,)) if skan_id is not None else None
        if sk is None:
            raise BladSesji(f"nie ma skanu {skan_id}")
        return sk

    def _status_z_prac(self, skan_id: int) -> str:
        """Status skanu aktywnego odtworzony z jego prac (do przywrocenia skanu zastapionego): ``przyjety`` albo ``do_powtorzenia``."""
        n = self.baza.wiersz(
            f"SELECT count(*) AS n FROM prace WHERE skan_id = ? AND (status_inspekcji IN ({_znaki(len(INSPEKCJA_DO_POWTORZENIA))}) "
            f"OR status_fragmentu IN ({_znaki(len(FRAGMENTY_DO_POWTORZENIA))}))", (skan_id, *INSPEKCJA_DO_POWTORZENIA, *FRAGMENTY_DO_POWTORZENIA))["n"]
        return STATUS_DO_POWTORZENIA if n else STATUS_PRZYJETY

    def _praca_do_decyzji(self, praca_id: int | None) -> dict:
        """Praca, o ktorej wolno zdecydowac: tylko ze skanu ``przyjety`` (nie: do powtorzenia, niezgodny uklad, blad, zastapiony, import)
        w trybie ``wieczor``. Skan poranny (``rano``) decyzji o pracach nie przyjmuje, dopoki nie powstanie sesja poranna (A6) - inaczej
        "Ukruszona" rano przenosila punkt projektu na prace poranna i zab znikal z listy wieczoru (recenzja PR #16 runda 3, P1)."""
        praca = self.baza.wiersz("SELECT p.*, s.status AS status_skanu, s.tryb AS tryb_skanu FROM prace p JOIN skany s ON s.id = p.skan_id "
                                 "WHERE p.id = ?", (praca_id,))
        if praca is None:
            raise BladSesji(f"nie ma pracy {praca_id}")
        if praca["status_skanu"] != STATUS_PRZYJETY:
            rada = {STATUS_ZASTAPIONY: "podejmij decyzje na nowym skanie plytki", STATUS_DO_POWTORZENIA: "zeskanuj plytke ponownie",
                    STATUS_NIEZGODNY_UKLAD: "zeskanuj plytke ponownie z wlasciwym ukladem",
                    STATUS_PLYTKA_NIE_Z_TRYBU: "to plytka nie z tego trybu: zeskanuj wlasciwa plytke albo swiadomie dopusc ten skan",
                    }.get(praca["status_skanu"], "ten skan nie nalezy do wieczoru")
            raise BladSesji(f"praca {praca_id}: skan {praca['skan_id']} ma status {praca['status_skanu']!r} - decyzje mozna podejmowac "
                            f"tylko na skanie przyjetym ({rada})")
        if praca["tryb_skanu"] != TRYB_WIECZOR:
            rada = "decyzje poranne obsluzy sesja poranna (paczka A6)" if praca["tryb_skanu"] == TRYB_RANO else "ten skan nie nalezy do wieczoru"
            raise BladSesji(f"praca {praca_id}: skan {praca['skan_id']} ma tryb {praca['tryb_skanu']!r} - decyzje o pracach przyjmuje tylko skan "
                            f"wieczorny; {rada}; stan wieczoru i lista do dofrezowania bez zmian")
        return praca

    def _decyzja_pracy(self, praca_id: int) -> dict | None:
        return _obowiazujace(self.baza.wiersze("SELECT * FROM decyzje WHERE praca_id = ? ORDER BY id", (praca_id,))).get(praca_id)

    def _decyzje_skanow(self, skany_ids: list[int]) -> dict[int, dict]:
        if not skany_ids:
            return {}
        return _obowiazujace(self.baza.wiersze(
            f"SELECT d.* FROM decyzje d JOIN prace p ON p.id = d.praca_id WHERE p.skan_id IN ({_znaki(len(skany_ids))}) ORDER BY d.id", tuple(skany_ids)))

    @staticmethod
    def _niezgodnosc(nowy: dict, stary: dict) -> str | None:
        """Dlaczego ``nowy`` nie moze byc ponownym skanem plytki ze skanu ``stary`` (None = moze)."""
        if nowy["sha16"] and nowy["sha16"] == stary["sha16"]:
            return None  # ta sama zawartosc pliku skanu
        if nowy["numer_plytki"] is not None and stary["numer_plytki"] is not None and nowy["numer_plytki"] != stary["numer_plytki"]:
            return f"inny numer plytki ({nowy['numer_plytki']} i {stary['numer_plytki']})"
        a, b = rodzina_ukladu(nowy["uklad"]), rodzina_ukladu(stary["uklad"])
        if a and b and a != b:
            return f"inny uklad plytki ({nowy['uklad']} i {stary['uklad']})"
        return None

    def _w_oknie_ponownego_skanu(self, wczesniejszy: dict, pozniejszy: dict) -> bool:
        """Czy ``pozniejszy`` przyjeto najwyzej ``ponowny_skan_okno_min`` minut (wlacznie) po ``wczesniejszy``.

        Liczone z roznicy czasow lokalnych bez strefy (znana granica: przy zmianie czasu i przy cofnietym zegarze roznica
        jest przeklamana o godzine albo ujemna - wtedy brak propozycji; zastapienie wprost dziala)."""
        minut = self._minut_miedzy(wczesniejszy, pozniejszy)
        return minut is not None and 0 <= minut <= self.ponowny_skan_okno_min

    @staticmethod
    def _minut_miedzy(wczesniejszy: dict, pozniejszy: dict) -> float | None:
        """Minuty miedzy przyjeciem skanow (``czas_analizy``; ujemne przy cofnietym zegarze); None, gdy ktorys czasu nie ma."""
        if not wczesniejszy["czas_analizy"] or not pozniejszy["czas_analizy"]:
            return None
        return (dt.datetime.fromisoformat(pozniejszy["czas_analizy"]) - dt.datetime.fromisoformat(wczesniejszy["czas_analizy"])).total_seconds() / 60

    def _projekty_rozpoznane(self, skan_id: int) -> set[str]:
        """Zbior ``sha16`` projektow top-1 prac rozpoznanych skanu (jak ``_przypisany``: bez prac szarych i bez kandydata);
        projekt w kilku pracach (fragmenty, powtorzony top-1) liczy sie raz."""
        return {p["kandydat1_sha16"] for p in self.baza.wiersze("SELECT kandydat1_sha16, status_match FROM prace WHERE skan_id = ?", (skan_id,))
                if self._przypisany(p)}

    def zgodnosc_prac(self, skan_id: int, poprzedni_id: int) -> dict:
        """Zgodnosc prac dwoch skanow plytki (E3-A1p - podstawa pytania "to ponowny skan?"), na ZBIORACH projektow.

        ``projekty`` / ``projekty_poprzedniego``: liczba roznych projektow prac rozpoznanych (projekt top-1 = ``sha16`` pierwszego
        kandydata, match nie ``szary``) skanu ``skan_id`` (N) i ``poprzedni_id`` (S); ``wspolne`` = |N & S|; ``udzial`` = wspolne /
        min(|N|, |S|) - miara symetryczna (runda 3, recenzja PR #22 B1: slaby albo czesciowy pierwszy skan, ktorego prace leza
        wszystkie na drugim, daje 1.0; wczesniej udzial liczony tylko wzgledem nowego skanu gubil pytanie); None, gdy ktorys zbior
        jest pusty. Prace nieznane (szare, bez kandydata) sa pomijane po obu stronach.
        """
        nowe, stare = self._projekty_rozpoznane(skan_id), self._projekty_rozpoznane(poprzedni_id)
        wspolne = len(nowe & stare)
        mniejszy = min(len(nowe), len(stare))
        return {"projekty": len(nowe), "projekty_poprzedniego": len(stare), "wspolne": wspolne, "udzial": wspolne / mniejszy if mniejszy else None}

    def _podstawa_ponownego(self, sk: dict, kandydat: dict) -> str | None:
        """Dlaczego ``sk`` wyglada na ponowny skan plytki ze skanu ``kandydat`` (ta sama plytka, w oknie); None = nowy wsad.

        E3-A1p (decyzja wlasciciela 18.11.2026, miara z rundy 3): ten sam plik skanu - zawsze; prog ``ponowny_skan_min_wspolnych``
        = 0 - regula sprzed E3-A1p; mniej niz ``PONOWNY_SKAN_MIN_ROZPOZNANYCH`` projektow rozpoznanych w ktorymkolwiek skanie - brak
        podstaw do oceny wsadu, pytanie jak dawniej; inaczej udzial wspolnych projektow (``zgodnosc_prac``) >= prog."""
        if sk["sha16"] and sk["sha16"] == kandydat["sha16"]:
            return PODSTAWA_TEN_SAM_PLIK
        if self.ponowny_skan_min_wspolnych <= 0:
            return PODSTAWA_REGULA_WYLACZONA
        z = self.zgodnosc_prac(sk["id"], kandydat["id"])
        if min(z["projekty"], z["projekty_poprzedniego"]) < PONOWNY_SKAN_MIN_ROZPOZNANYCH:
            return PODSTAWA_ZA_MALO_ROZPOZNANYCH
        return PODSTAWA_TE_SAME_PRACE if z["udzial"] >= self.ponowny_skan_min_wspolnych else None

    def _propozycja_zastapienia(self, sk: dict) -> tuple[dict, str] | None:
        """(skan, podstawa): skan, ktorego zastapienie program proponuje dla ``sk``, i dlaczego (``_podstawa_ponownego``).

        Kandydat to OSTATNI wczesniejszy aktywny skan tej samej plytki (ten sam numer i rodzina ukladu albo ta sama zawartosc
        pliku, ten sam tryb), o ile przyjeto go najwyzej ``ponowny_skan_okno_min`` minut przed ``sk`` - niezaleznie od granicy
        doby - i lezy na nim ten sam wsad (E3-A1p). Starszy skan albo skan z innymi pracami = nowy wsad na tej samej plytce
        (bez propozycji; liczy sie tylko ostatni skan plytki). Pomijane sa skany, dla ktorych zastapienie przez ``sk`` juz cofnieto."""
        if sk["status"] not in STATUSY_AKTYWNE or not sk["czas_analizy"] or (sk["numer_plytki"] is None and not sk["sha16"]):
            return None
        cofniete = {int(d["wartosc"]) for d in self.baza.wiersze("SELECT wartosc FROM decyzje WHERE skan_id = ? AND rodzaj = ?",
                                                                 (sk["id"], RODZAJ_COFNIJ_ZASTAPIENIE)) if str(d["wartosc"] or "").isdigit()}
        kandydaci = self.baza.wiersze(
            f"""SELECT * FROM skany WHERE id < ? AND tryb IS ? AND status IN ({_znaki(len(STATUSY_AKTYWNE))})
                AND ((numer_plytki IS NOT NULL AND numer_plytki = ?) OR (sha16 IS NOT NULL AND sha16 = ?))
                ORDER BY id DESC""",
            (sk["id"], sk["tryb"], *STATUSY_AKTYWNE, sk["numer_plytki"], sk["sha16"]))
        for kandydat in kandydaci:
            if kandydat["id"] in cofniete or self._niezgodnosc(sk, kandydat) is not None:
                continue
            if not self._w_oknie_ponownego_skanu(kandydat, sk):
                return None  # liczy sie tylko ostatni skan tej plytki
            podstawa = self._podstawa_ponownego(sk, kandydat)
            return (kandydat, podstawa) if podstawa is not None else None
        return None

    def _poprzedni_skan(self, sk: dict) -> dict | None:
        """Skan, ktorego zastapienie program proponuje dla ``sk`` (``_propozycja_zastapienia``), albo None."""
        propozycja = self._propozycja_zastapienia(sk)
        return propozycja[0] if propozycja is not None else None

    def _zastap(self, skan_id: int | None, poprzedni_id: int | None, operator: str | None) -> tuple[int, int]:
        osoba = self._operator(operator)
        with self.baza.transakcja():
            nowy = self._skan(skan_id)
            if nowy["status"] not in STATUSY_AKTYWNE:
                raise BladSesji(f"skan {skan_id} ma status {nowy['status']!r} - nie moze zastapic innego skanu")
            if poprzedni_id is None:
                poprzedni = self._poprzedni_skan(nowy)
                if poprzedni is None:
                    raise BladSesji(f"skan {skan_id}: nie ma skanu do zastapienia - program nie proponuje zastapienia tego skanu "
                                    f"(ostatni skan tej samej plytki sprzed najwyzej {self.ponowny_skan_okno_min} min z tymi samymi pracami)")
            else:
                poprzedni = self._skan(poprzedni_id)
                # ten sam piec (sesja poranna): bez warunku doby i okna - tak, jak proponuje sesja poranna (piec rozladowany przez
                # granice doby 06:00, recenzja PR #23 D10), ale najwyzej PONOWNY_SKAN_PIEC_MAX_H od siebie (piec niezamkniety do
                # nastepnego dnia - recenzja PR #22 runda 2, P1); inaczej ta sama doba robocza albo okno ponownego skanu
                minut = self._minut_miedzy(poprzedni, nowy)
                ten_sam_piec = (poprzedni["sesja_pieca_id"] is not None and poprzedni["sesja_pieca_id"] == nowy["sesja_pieca_id"]
                                and minut is not None and 0 <= minut <= PONOWNY_SKAN_PIEC_MAX_H * 60)
                blisko = poprzedni["tryb"] == nowy["tryb"] and (ten_sam_piec or (
                    bool(poprzedni["czas_analizy"]) and bool(nowy["czas_analizy"])
                    and (self.doba(poprzedni["czas_analizy"]) == self.doba(nowy["czas_analizy"]) or self._w_oknie_ponownego_skanu(poprzedni, nowy))))
                if poprzedni["id"] >= nowy["id"] or poprzedni["status"] not in STATUSY_AKTYWNE or not blisko:
                    raise BladSesji(f"skan {poprzedni_id} nie moze byc zastapiony skanem {skan_id} (musi byc wczesniejszy, aktywny i z tej samej doby "
                                    f"roboczej albo sprzed najwyzej {self.ponowny_skan_okno_min} min, rano - z tego samego pieca)")
                ten_sam_plik = bool(nowy["sha16"]) and nowy["sha16"] == poprzedni["sha16"]
                if not ten_sam_plik and (nowy["numer_plytki"] is None or poprzedni["numer_plytki"] is None):
                    raise BladSesji(f"skan {skan_id} nie moze zastapic skanu {poprzedni_id}: najpierw podaj numer plytki obu skanow "
                                    f"(bez numeru nie wiadomo, czy to ta sama plytka)")
                powod = self._niezgodnosc(nowy, poprzedni)
                if powod is not None:
                    raise BladSesji(f"skan {skan_id} nie moze zastapic skanu {poprzedni_id}: {powod} - to nie jest ponowny skan tej samej plytki")
            decyzja_id = self.baza.wstaw("decyzje", skan_id=nowy["id"], rodzaj="powtorz_skan", wartosc=str(poprzedni["id"]), operator=osoba, czas=self.teraz())
            self.baza.wykonaj("UPDATE skany SET status = ? WHERE id = ?", (STATUS_ZASTAPIONY, poprzedni["id"]))
            self.baza.wykonaj("UPDATE skany SET zastepuje_id = ? WHERE id = ?", (poprzedni["id"], nowy["id"]))
            self._przelicz_punkty_skanu(poprzedni, aktywny=False)  # decyzje skanu zastapionego przestaja sie liczyc
        return decyzja_id, poprzedni["id"]

    # --- stan punktow (tylko czesc wieczorna: "do dofrezowania") ---------------------------------
    def _odswiez_punkt(self, praca: dict, tryb: str | None, aktywna: bool = True) -> None:
        """Uzgadnia ``stan_punktow`` projektu pracy z jej obowiazujaca decyzja.

        Punkt w stanie ``do_dofrezowania`` wskazuje zawsze prace z NAJNOWSZA (najwyzsze ``decyzje.id``) obowiazujaca "Ukruszona"
        projektu w skanie wieczornym aktywnym (``_najnowsza_ukruszona``) - takze po cofnieciu zastapienia, ponownym dopuszczeniu
        skanu i cofnieciu nowszej decyzji tej samej pracy (recenzja PR #16 runda 3, D5). Praca z obowiazujaca "Ukruszona" ->
        ``do_dofrezowania`` - nadpisuje KAZDY wczesniejszy stan punktu i zeruje ``sesja_pieca_id`` (cykl zycia punktu rano ustali
        paczka A6). Gdy decyzja przestaje obowiazywac (cofniecie, "OK", skan zastapiony albo zablokowany), a punkt wskazywal te
        prace: przechodzi na najnowsza inna ukruszona prace projektu, a gdy takiej nie ma - do ``oczekuje`` (poprzedni stan nie jest
        odtwarzany). W tej galezi punktow w innych stanach albo wskazujacych inna prace nie rusza.
        Prace skanow innego trybu niz ``wieczor`` (``rano`` - do A6, import okna testowego) punktow nie ruszaja (P1).
        """
        projekt_id = praca["projekt_id"]
        if projekt_id is None or tryb != TRYB_WIECZOR:
            return
        decyzja = self._decyzja_pracy(praca["id"]) if aktywna else None
        ukruszona = decyzja is not None and decyzja["rodzaj"] in DECYZJE_UKRUSZENIA
        if not ukruszona:
            punkt = self.baza.wiersz("SELECT * FROM stan_punktow WHERE projekt_id = ?", (projekt_id,))
            if punkt is None or punkt["stan"] != STAN_DO_DOFREZOWANIA or punkt["praca_id"] != praca["id"]:
                return
        ostatnia = self._najnowsza_ukruszona(projekt_id, bez=None if ukruszona else praca["id"])
        if ostatnia is not None:
            self._ustaw_punkt(projekt_id, STAN_DO_DOFREZOWANIA, ostatnia["praca_id"], ostatnia["czas"])
        else:
            self._ustaw_punkt(projekt_id, STAN_OCZEKUJE, None, self.teraz())

    def _najnowsza_ukruszona(self, projekt_id: int, bez: int | None = None) -> dict | None:
        """Najnowsza (najwyzsze ``decyzje.id``) obowiazujaca decyzja "Ukruszona" / "ukruszona_niewykryta" na pracy projektu w skanie
        wieczornym aktywnym; ``bez`` = praca pomijana. Decyzje z importu okna testowego (skany bez trybu) i skanow porannych sie nie licza."""
        prace = self.baza.wiersze(
            f"SELECT p.id, p.skan_id FROM prace p JOIN skany s ON s.id = p.skan_id WHERE p.projekt_id = ? AND p.id IS NOT ? "
            f"AND s.tryb = ? AND s.status IN ({_znaki(len(STATUSY_AKTYWNE))})", (projekt_id, bez, TRYB_WIECZOR, *STATUSY_AKTYWNE))
        decyzje = self._decyzje_skanow(sorted({w["skan_id"] for w in prace}))
        ukruszone = [decyzje[w["id"]] for w in prace if w["id"] in decyzje and decyzje[w["id"]]["rodzaj"] in DECYZJE_UKRUSZENIA]
        return max(ukruszone, key=lambda d: d["id"]) if ukruszone else None

    def _ustaw_punkt(self, projekt_id: int, stan: str, praca_id: int | None, czas: str) -> None:
        self.baza.wykonaj(
            """INSERT INTO stan_punktow (projekt_id, stan, praca_id, sesja_pieca_id, czas) VALUES (?, ?, ?, NULL, ?)
               ON CONFLICT (projekt_id) DO UPDATE SET stan = excluded.stan, praca_id = excluded.praca_id, sesja_pieca_id = NULL, czas = excluded.czas""",
            (projekt_id, stan, praca_id, czas))

    # --- odczyt stanu ----------------------------------------------------------------------------
    def _skany_sesji(self, data: str, tryb: str, tylko_aktywne: bool = False) -> list[dict]:
        od, do = self._przedzial_doby(data)
        sql = "SELECT * FROM skany WHERE tryb = ? AND czas_analizy >= ? AND czas_analizy < ?"
        parametry: tuple = (tryb, od, do)
        if tylko_aktywne:
            sql += f" AND status IN ({_znaki(len(STATUSY_AKTYWNE))})"
            parametry += STATUSY_AKTYWNE
        return self.baza.wiersze(sql + " ORDER BY id", parametry)

    def _prace_skanow(self, skany_ids: list[int]) -> list[dict]:
        if not skany_ids:
            return []
        return self.baza.wiersze(
            f"""SELECT p.*, pr.zeby AS zeby, z.kuweta AS kuweta, f.krazek AS krazek, sp.stan AS stan_punktu,
                       sp.praca_id AS punkt_praca_id
                FROM prace p LEFT JOIN projekty pr ON pr.id = p.projekt_id LEFT JOIN zlecenia z ON z.id = pr.zlecenie_id
                LEFT JOIN frezowania f ON f.id = p.frezowanie_id LEFT JOIN stan_punktow sp ON sp.projekt_id = p.projekt_id
                WHERE p.skan_id IN ({_znaki(len(skany_ids))}) ORDER BY p.skan_id, p.id""", tuple(skany_ids))

    @staticmethod
    def _przypisany(praca: dict) -> str | None:
        """``sha16`` projektu, do ktorego praca jest przypisana (praca szara albo bez kandydata: brak przypisania)."""
        return praca["kandydat1_sha16"] if praca["kandydat1_sha16"] and praca["status_match"] != "szary" else None

    @staticmethod
    def _kolor(status_skanu: str, status_gniazda: str | None, decyzja: str | None = None) -> str | None:
        """Kolor pracy na mapie wieczoru - stan PO decyzjach technika (kontrakt dla okna i ramki).

        Skan nieaktywny: brak koloru. Decyzja "Ukruszona" / "ukruszona_niewykryta": ``czerwony`` (takze gdy analiza dala
        zielony). Decyzja "OK": ``zatwierdzona_ok`` (odroznialna od zwyklego zielonego). Bez decyzji: status gniazda
        z analizy, z tym ze w skanie do powtorzenia nie ma prac zielonych (zielony -> zolty).
        """
        if status_skanu not in STATUSY_AKTYWNE:
            return None
        if decyzja in DECYZJE_UKRUSZENIA:
            return KOLOR_UKRUSZONA
        if decyzja == "ok":
            return KOLOR_ZATWIERDZONA_OK
        if status_skanu == STATUS_DO_POWTORZENIA and status_gniazda == "zielony":
            return "zolty"
        return status_gniazda

    def stan_wieczoru(self, data: str | None = None) -> dict:
        """Caly stan doby roboczej ``data`` (RRRR-MM-DD, domyslnie biezaca) jako zwykle dane (nadaje sie do JSON).

        ``data`` = data doby, ``zmiana`` = numer biezacej zmiany (None, gdy ``data`` nie jest biezaca doba).
        ``skany``: wszystkie skany wieczorne przyjete w tej dobie, z numerem zmiany i pracami; praca ma statusy z pliku wyniku
        (``status_gniazda`` = ocena programu), ``kolor`` (po decyzjach technika, patrz ``_kolor``), ``sha16`` / ``kuweta`` /
        ``zeby`` / ``krazek`` i obowiazujaca ``decyzja``. ``liczniki`` (po kolorze), ``decyzje`` (po rodzaju obowiazujacej decyzji)
        i ``prac``: tylko skany aktywne. ``do_potwierdzenia``: skany, ktore wygladaja na ponowny skan plytki (``zastap_skan``;
        regula: ``_propozycja_zastapienia``), z polem ``podstawa`` (``ten_sam_plik``, ``te_same_prace``, ``za_malo_rozpoznanych``,
        ``regula_wylaczona``). Wpis ``do_potwierdzenia`` podaje tez, ile decyzji przestanie obowiazywac po potwierdzeniu (``liczba_decyzji``,
        ``liczba_ukruszonych``, ``decyzje``) - okno ostrzega przed kliknieciem. Praca z "Ukruszona" ma ``na_liscie`` = pozycja
        listy, ktora ja reprezentuje (ta sama praca albo inna praca tego samego projektu).
        ``do_dofrezowania``: pozycje tej doby, ``do_dofrezowania_biezaca``: wszystkie otwarte (takze z poprzednich dob).
        Bez nazw folderow i plikow zlecen.
        """
        biezaca_doba = self.doba()
        data = data or biezaca_doba
        skany = self._skany_sesji(data, TRYB_WIECZOR)
        ids = [s["id"] for s in skany]
        decyzje = self._decyzje_skanow(ids)
        prace_skanu: dict[int, list[dict]] = {i: [] for i in ids}
        for p in self._prace_skanow(ids):
            prace_skanu[p["skan_id"]].append(p)
        wynik_skany, razem, razem_decyzje, prac, do_potwierdzenia = [], {}, {}, 0, []
        for s in skany:
            aktywny = s["status"] in STATUSY_AKTYWNE
            propozycja = self._propozycja_zastapienia(s)
            poprzedni, podstawa = propozycja if propozycja is not None else (None, None)
            liczniki: dict[str, int] = {}
            prace = []
            for p in prace_skanu[s["id"]]:
                d = decyzje.get(p["id"])
                kolor = self._kolor(s["status"], p["status_gniazda"], d["rodzaj"] if d else None)
                if aktywny:
                    prac += 1
                    if kolor is not None:
                        liczniki[kolor] = liczniki.get(kolor, 0) + 1
                        razem[kolor] = razem.get(kolor, 0) + 1
                    if d is not None:
                        razem_decyzje[d["rodzaj"]] = razem_decyzje.get(d["rodzaj"], 0) + 1
                prace.append({
                    "id": p["id"], "gniazdo": p["gniazdo"], "nr_fragmentu": p["nr_fragmentu"], "status_fragmentu": p["status_fragmentu"],
                    "status_match": p["status_match"], "status_inspekcji": p["status_inspekcji"], "status_gniazda": p["status_gniazda"],
                    "kolor": kolor, "sha16": self._przypisany(p), "projekt_id": p["projekt_id"], "kuweta": p["kuweta"], "zeby": p["zeby"],
                    "krazek": p["krazek"], "kandydat1_sha16": p["kandydat1_sha16"], "kandydat1_pokrycie": p["kandydat1_pokrycie"],
                    "kandydat2_sha16": p["kandydat2_sha16"], "kandydat2_pokrycie": p["kandydat2_pokrycie"], "pewnosc": p["pewnosc"],
                    "wspolczynnik": p["wspolczynnik"], "korekta_skali": p["korekta_skali"], "ubytki": p["ubytki"], "ubytek_max_mm": p["ubytek_max_mm"],
                    "decyzja": d["rodzaj"] if d else None, "decyzja_id": d["id"] if d else None, "operator": d["operator"] if d else None,
                    "czas_decyzji": d["czas"] if d else None})
            if poprzedni is not None:
                do_potwierdzenia.append({"skan_id": s["id"], "poprzedni_id": poprzedni["id"], "numer_plytki": s["numer_plytki"],
                                         "podstawa": podstawa, **self._decyzje_do_utraty(poprzedni["id"])})
            wynik_skany.append({
                "id": s["id"], "plik": s["plik"], "sha16": s["sha16"], "czas_pliku": s["czas_pliku"], "czas_analizy": s["czas_analizy"],
                "zmiana": self.zmiana(s["czas_analizy"]), "czas_s": s["czas_s"], "uklad": s["uklad"], "uklad_zrodlo": s["uklad_zrodlo"],
                "uklad_zgodny": None if s["uklad_zgodny"] is None else bool(s["uklad_zgodny"]), "numer_plytki": s["numer_plytki"],
                "numer_zrodlo": s["numer_zrodlo"], "status": s["status"], "aktywny": aktywny,
                "powod": powod_nie_z_trybu(s["uklad"], s["tryb"]) if s["status"] == STATUS_PLYTKA_NIE_Z_TRYBU else None,
                "zastepuje_id": s["zastepuje_id"],
                "moze_zastapic": poprzedni["id"] if poprzedni is not None else None, "wynik_json": s["wynik_json"],
                "liczniki": liczniki, "prace": prace})
        biezaca = self.do_dofrezowania()
        po_projekcie = {x["projekt_id"]: x for x in biezaca if x["projekt_id"] is not None}
        po_pracy = {x["praca_id"]: x for x in biezaca}
        for sk in wynik_skany:  # "ten zab jest juz na liscie (skan X, zmiana Y)": pozycja listy, ktora reprezentuje prace ukruszona
            for x in sk["prace"]:
                pozycja = None
                if sk["aktywny"] and x["decyzja"] in DECYZJE_UKRUSZENIA:
                    pozycja = po_projekcie.get(x["projekt_id"]) if x["projekt_id"] is not None else po_pracy.get(x["id"])
                x["na_liscie"] = {k: pozycja[k] for k in ("praca_id", "skan_id", "doba", "zmiana")} if pozycja else None
        return {"data": data, "zmiana": self.zmiana() if data == biezaca_doba else None, "skany": wynik_skany, "liczniki": razem,
                "decyzje": razem_decyzje, "prac": prac, "do_potwierdzenia": do_potwierdzenia,
                "do_dofrezowania": [x for x in biezaca if x["doba"] == data], "do_dofrezowania_biezaca": biezaca,
                "konflikty": self.konflikty(data)}

    def _decyzje_do_utraty(self, skan_id: int) -> dict:
        """Obowiazujace decyzje o pracach skanu, ktore przestana sie liczyc, gdy skan zostanie zastapiony (kontrakt dla okna)."""
        decyzje = self._decyzje_skanow([skan_id])
        lista = [{"praca_id": p["id"], "gniazdo": p["gniazdo"], "rodzaj": decyzje[p["id"]]["rodzaj"], "kuweta": p["kuweta"], "zeby": p["zeby"]}
                 for p in self._prace_skanow([skan_id]) if p["id"] in decyzje]
        return {"liczba_decyzji": len(lista), "liczba_ukruszonych": sum(1 for x in lista if x["rodzaj"] in DECYZJE_UKRUSZENIA), "decyzje": lista}

    def do_dofrezowania(self, data: str | None = None) -> list[dict]:
        """Lista "do dofrezowania". Bez ``data``: lista BIEZACA - wszystkie otwarte pozycje, takze z poprzednich dob roboczych
        (pozycja nie znika na granicy doby). Z ``data``: filtr "ta doba" (pozycje skanow przyjetych w tej dobie roboczej).

        Lista wynika ze ``stan_punktow``: JEDEN punkt projektu w stanie ``do_dofrezowania`` = JEDNA pozycja - praca, na ktora
        punkt wskazuje (praca z NAJNOWSZA obowiazujaca "Ukruszona" projektu w skanie wieczornym aktywnym). Inne aktywne prace tego samego projektu
        z "Ukruszona" (ta sama plytka zeskanowana jako nowy wsad, zab dofrezowany i znow ukruszony) nie tworza drugiej pozycji -
        sa w polu ``powtorzenia``. Punkt zamkniety (poranek, A6) = pozycja znika. Praca bez projektu w indeksie nie ma punktu:
        jest pozycja sama dla siebie (nie ma jeszcze czym jej zamknac).
        Pola: ``kuweta``, ``zeby``, ``krazek`` (None, gdy pracy nie ma w indeksie albo nie ma jednoznacznego wpisu frezowania),
        plytka, gniazdo, ``sha16`` projektu, kto i kiedy zdecydowal, ``doba`` i ``zmiana`` (z chwili PRZYJECIA skanu, nie
        z czasu decyzji), ``stan_punktu``, ``powtorzenia``.
        """
        aktywne = _znaki(len(STATUSY_AKTYWNE))
        decyzje = _obowiazujace(self.baza.wiersze(
            f"""SELECT d.* FROM decyzje d JOIN prace p ON p.id = d.praca_id JOIN skany s ON s.id = p.skan_id
                WHERE s.tryb = ? AND s.status IN ({aktywne}) AND p.id IN (
                    SELECT praca_id FROM decyzje WHERE rodzaj IN ({_znaki(len(DECYZJE_UKRUSZENIA))}))
                ORDER BY d.id""", (TRYB_WIECZOR, *STATUSY_AKTYWNE, *DECYZJE_UKRUSZENIA)))
        ukruszone = {praca_id: d for praca_id, d in decyzje.items() if d["rodzaj"] in DECYZJE_UKRUSZENIA}
        skany_ids = sorted({w["skan_id"] for w in self._wiersze_po_id("SELECT id, skan_id FROM prace WHERE id IN ({})", sorted(ukruszone))})
        skany = {w["id"]: w for w in self._wiersze_po_id("SELECT id, numer_plytki, czas_analizy FROM skany WHERE id IN ({})", skany_ids)}
        prace = [p for p in self._prace_skanow(skany_ids) if p["id"] in ukruszone]

        def miejsce(p: dict) -> dict:
            sk = skany[p["skan_id"]]
            return {"praca_id": p["id"], "skan_id": p["skan_id"], "numer_plytki": sk["numer_plytki"], "gniazdo": p["gniazdo"],
                    "doba": self.doba(sk["czas_analizy"]), "zmiana": self.zmiana(sk["czas_analizy"])}

        lista = []
        for p in prace:
            d = ukruszone[p["id"]]
            if p["projekt_id"] is not None and not (p["stan_punktu"] == STAN_DO_DOFREZOWANIA and p["punkt_praca_id"] == p["id"]):
                continue  # pozycja projektu to tylko praca wskazana przez punkt; punkt zamkniety = brak pozycji
            m = miejsce(p)
            if data is not None and m["doba"] != data:
                continue
            powtorzenia = [miejsce(q) for q in prace if p["projekt_id"] is not None and q["projekt_id"] == p["projekt_id"] and q["id"] != p["id"]]
            lista.append({
                **m, "sha16": self._przypisany(p), "projekt_id": p["projekt_id"], "kuweta": p["kuweta"], "zeby": p["zeby"], "krazek": p["krazek"],
                "ubytki": p["ubytki"], "ubytek_max_mm": p["ubytek_max_mm"], "decyzja": d["rodzaj"], "operator": d["operator"], "czas": d["czas"],
                "stan_punktu": p["stan_punktu"] if p["projekt_id"] is not None else None, "powtorzenia": powtorzenia})
        return lista

    def _wiersze_po_id(self, sql: str, ids: list[int], porcja: int = 500) -> list[dict]:
        """Zapytanie z lista identyfikatorow w miejscu ``{}``, w porcjach (lista biezaca rosnie z czasem)."""
        wynik: list[dict] = []
        for i in range(0, len(ids), porcja):
            czesc = ids[i:i + porcja]
            wynik += self.baza.wiersze(sql.format(_znaki(len(czesc))), tuple(czesc))
        return wynik

    def zapisz_do_dofrezowania(self, data: str | None = None, katalog: str | Path | None = None) -> Path:
        """Lista "do dofrezowania" jako plik (zalozenie Z6; domyslnie w folderze bazy): bez ``data`` lista biezaca
        ``do_dofrezowania_biezaca.csv``, z ``data`` pozycje tej doby ``do_dofrezowania_<data>.csv``."""
        katalog = Path(katalog) if katalog is not None else self.baza.plik.parent
        katalog.mkdir(parents=True, exist_ok=True)
        cel = katalog / f"do_dofrezowania_{data or 'biezaca'}.csv"
        with open(cel, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(KOLUMNY_LISTY)
            for x in self.do_dofrezowania(data):
                w.writerow(["" if v is None else v for v in (x["kuweta"], x["zeby"], x["krazek"], x["numer_plytki"], x["gniazdo"], x["sha16"],
                                                              x["doba"], x["zmiana"])])
        return cel

    def konflikty(self, data: str | None = None, tryb: str = TRYB_WIECZOR) -> list[dict]:
        """SE8: projekty (``sha16``) przypisane do prac w wiecej niz jednym gniezdzie skanow aktywnych tej doby roboczej.

        Nie licza sie prace szare ani prace oznaczone "Ukruszona" (ten sam STL drugi raz to wtedy zab dofrezowany).
        Dwa fragmenty w tym samym gniezdzie jednego skanu to jedno miejsce. Konflikt nie zmienia koloru prac;
        rozstrzygniecie nalezy do technika.
        """
        data = data or self.doba()
        skany = self._skany_sesji(data, tryb, tylko_aktywne=True)
        numery = {s["id"]: s["numer_plytki"] for s in skany}
        decyzje = self._decyzje_skanow(list(numery))
        miejsca: dict[str, list[dict]] = {}
        for p in self._prace_skanow(list(numery)):
            sha16 = self._przypisany(p)
            d = decyzje.get(p["id"])
            if sha16 is None or (d is not None and d["rodzaj"] in DECYZJE_UKRUSZENIA):
                continue
            miejsca.setdefault(sha16, []).append({"skan_id": p["skan_id"], "numer_plytki": numery[p["skan_id"]], "gniazdo": p["gniazdo"], "praca_id": p["id"]})
        wynik = []
        for sha16, lista in miejsca.items():
            rozne = {(m["skan_id"], m["gniazdo"] if m["gniazdo"] is not None else f"poza-{m['praca_id']}") for m in lista}
            if len(rozne) > 1:
                wynik.append({"sha16": sha16, "miejsca": lista})
        return sorted(wynik, key=lambda k: (k["miejsca"][0]["skan_id"], k["miejsca"][0]["praca_id"]))
