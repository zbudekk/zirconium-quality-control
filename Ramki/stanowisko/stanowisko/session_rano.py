"""session_rano - sesja poranna: sesja pieca, punkty zlecen, kompletnosc, braki, dofrezowania, poprawki (E3-A6).

Wejscie: wyniki analizy skanow plytek porannych (slownik z ``porownaj.porownaj`` + zdarzenie skanu - jak wieczorem),
decyzje osoby rozkladajacej piec (wybor kandydata, przypisanie reczne, pominiecie skanu, cofniecie), "Zamknij piec". Wyjscie:
wiersze w bazie (``baza.py``, plan etapu 3 sekcja 3.4 - schemat bez zmian) i funkcje stanu dla ekranu porannego (A7), planu
ramki (A8) i Excela (A9): ``stan_pieca``, ``plan_plytek``, ``zamknij_piec`` / ``wynik_pieca``, ``braki``, ``piece``.

Modul nie rozszerza ``session.py`` (ten plik zmienia rownolegle paczka A1p) - korzysta z jego publicznego API: skan poranny
przyjmuje ``Sesja.przyjmij_wynik(..., tryb="rano")``, ponowny skan i numer plytki obsluguja ``Sesja.zastap_skan``,
``cofnij_zastapienie``, ``podaj_numer_plytki`` (tu tylko z kontrola, ze skan nalezy do otwartego pieca i numer do plytek
porannych). Kolory i klucze statusow bierze z ``statusy.py`` (zalozenie Z8). Caly stan jest w bazie - obiekt ``SesjaRano``
niczego nie pamieta, wiec po restarcie programu nowy obiekt na tym samym pliku daje ten sam stan (takze otwarty piec).

Zasady (szczegoly, granice i decyzje do potwierdzenia: ``opisy_modulow/session.md``, sekcja "Sesja poranna"):
- sesja pieca = wiersz ``sesje_pieca``; otwiera ja sam pierwszy skan poranny po zamknieciu poprzedniej (albo ``otworz_piec``),
  zamyka "Zamknij piec"; naraz otwarta najwyzej jedna; skan poranny dostaje ``skany.sesja_pieca_id``;
- punkt zlecenia = wiersz ``projekty`` (plik STL w folderze zlecenia, ``usuniety = 0``); punkt bez wlasnego stanu dziedziczy
  stan usunietego projektu o tej samej zawartosci (``sha16``) z tego samego zlecenia albo zlecenia o tej samej kuwecie (zmiana
  nazwy folderu albo pliku w indeksie nie gubi stanu); zlecenie kompletne = kazdy punkt rozpoznany albo zamkniety recznie;
- klasa pracy porannej: ``pewna`` i ``przypisana`` licza sie do kompletu; ``dwuznaczna`` i ``nieznana`` czekaja na decyzje;
  ``poprawka`` = projekt, ktorego punkt zamknal juz poprzedni piec (tylko log, Excel bez zmian); ``konflikt`` = ten sam projekt
  w dwoch gniazdach jednego pieca;
- "Zamknij piec" odmawia, dopoki jakas plytka pieca sie nie liczy (brak numeru, ten sam numer na dwoch skanach, skan do
  powtorzenia, skan bez wyniku albo niezgodny bez ponownego skanu, plytka spoza ramki porannej) albo jest konflikt;
- ``stan_punktow`` zmienia dopiero "Zamknij piec" (prace liczone -> ``rozpoznany``, brakujace punkty zlecen dotknietych ->
  ``brak_po_piecu``, punkt ``do_dofrezowania`` zostaje); wynik i stan sprzed zamkniecia zostaja w dzienniku (``piec_zamkniety``),
  wiec ``wynik_pieca`` dziala po restarcie, a ``otworz_piec_ponownie`` cofa zamkniecie ostatniego pieca;
- decyzje sa tylko dopisywane, z operatorem z listy ``[sesja] operatorzy``; kazda ma cofniecie;
- nazwy folderow i plikow zlecen nie sa nigdzie zapisywane ani zwracane: tylko ``sha16``, kuweta, zeby, id.

Modul korzysta tylko z biblioteki standardowej.
"""
from __future__ import annotations

import datetime as dt
import json
import re
from typing import Any

from . import baza as B
from . import session as SE
from . import statusy as ST

# klasy pracy porannej (tylko w wynikach funkcji, nie w bazie)
KLASA_PEWNA = "pewna"
KLASA_PRZYPISANA = "przypisana"
KLASA_DWUZNACZNA = "dwuznaczna"
KLASA_NIEZNANA = "nieznana"
KLASA_POPRAWKA = "poprawka"
KLASA_KONFLIKT = "konflikt"
KLASA_DO_POWTORZENIA = "do_powtorzenia"
KLASY_LICZONE = (KLASA_PEWNA, KLASA_PRZYPISANA)  # tylko takie prace domykaja punkty zlecen
KLASY_Z_KUWETA = (KLASA_PEWNA, KLASA_PRZYPISANA, KLASA_POPRAWKA)  # gniazdo planu ramki z numerem kuwety
# klasa -> klucz ``statusy.STATUSY`` (Z8: kolory ekranu i diod tylko z tej tabeli). "nieznana_rano" dopisuje A7; do tego czasu
# kolory z ``STATUSY_ZAPASOWE`` (jedyny wyjatek, usunac po scaleniu A7)
STATUS_KLASY = {KLASA_PEWNA: "zielony", KLASA_PRZYPISANA: "zielony", KLASA_DWUZNACZNA: "zolty", KLASA_NIEZNANA: "nieznana_rano",
                KLASA_POPRAWKA: "dofrezowany", KLASA_KONFLIKT: "czerwony", KLASA_DO_POWTORZENIA: "skan_do_powtorzenia"}
STATUSY_ZAPASOWE = {"nieznana_rano": ("bialy", "bialy")}  # (kolor, ramka) - praca nieznana rano: biel (PW, I2)
STATUS_DWIE_PRACE = "podwojny"  # dwie prace w jednym gniezdzie planu ramki
STATUS_SPRAWDZ = "czerwony"  # kuweta pusta albo niejednoznaczna: ramka swieci "sprawdz", numer pokazuje ekran

# stany punktow (plan 3.4; ``oczekuje`` i ``do_dofrezowania`` ustawia session)
STAN_ROZPOZNANY = "rozpoznany"
STAN_BRAK_PO_PIECU = "brak_po_piecu"
STAN_ZAMKNIETY_RECZNIE = "zamkniety_recznie"
STANY_KONCOWE = (STAN_ROZPOZNANY, STAN_ZAMKNIETY_RECZNIE)

# rodzaje decyzji porannych - cofniecie jak wieczorem: wiersz ``cofniecie`` z id cofanej decyzji
RODZAJ_WYBOR = "wybor_kandydata"  # praca; wartosc = sha16 wybranego kandydata (1. albo 2.)
RODZAJ_PRZYPISANIE = "przypisanie_reczne"  # praca; wartosc = id projektu albo "" (praca bez projektu - nieznana)
RODZAJ_POMIN_SKAN = "pomin_skan"  # skan: nie nalezy do pieca / zastapiony skanem, ktorego Sesja nie przyjmie - nie liczy sie i nie blokuje
RODZAJ_ZAMKNIECIE_RECZNE = "zamkniecie_reczne"  # bez pracy i skanu; wartosc = JSON (projekt_id, powod, stan sprzed)
RODZAJ_OTWORZ_PIEC = "otworz_piec_ponownie"  # bez pracy i skanu; wartosc = id sesji pieca
BEZ_PROJEKTU = ""
POWODY_ZAMKNIECIA = ("nie_praca_z_cyrkonu", "zaginiona", "wydana_bez_skanu", "inny", "nie_bedzie_dofrezowany")  # kody (dziennik bez nazwisk)
POWOD_DOFREZOWANIE = "nie_bedzie_dofrezowany"  # JEDYNY kod zamykajacy punkt do_dofrezowania (zab ukruszony - frezarka traci zadanie)

PROG_KANDYDATA = 0.6  # = [match] prog_ostrzezenia_pokrycie z ustawienia.przyklad.toml (z_ustawien bierze wartosc z pliku)
KOLEJNOSCI = ("liczba", "numer")  # kuwety od najliczniejszej albo wg numeru (U7); numer wpisany recznie obsluguje ramka
WZOR_KUWETY_RAMKI = re.compile(r"#?[0-9]{1,6}")  # = ramka/protokol.py WZOR_KUWETY - inna kuweta nie idzie do ramki
MAX_BRAKOW_PLANU = 100  # = ramka/protokol.py MAX_BRAKOW
# numery plytek porannych wg ukladu (= modele_plytek/<uklad>/plytka_n*.stl; kwadratowe = ramka/protokol.py RODZINY["P"])
NUMERY_PLYTEK_PORANNYCH = (4, 5, 6)
NUMERY_PLYTEK_OKRAGLYCH_PORANNYCH = (9,)
TYPY_BEZ_PUNKTU: tuple[str, ...] = ()  # typy plikow (indeks: projekty.typ, np. "waxup"), ktore nie sa punktem pracy - do decyzji

OKNO_CIAGLOSCI_MIN = 90  # skan dolacza do otwartego pieca z poprzedniej doby, gdy jego ostatni skan byl najwyzej tyle minut temu (koordynator)

TYP_OTWARTY = "piec_otwarty"
TYP_ZAMKNIETY = "piec_zamkniety"
TYP_OTWARTY_PONOWNIE = "piec_otwarty_ponownie"
TYP_POPRAWKA = "poprawka_rano"
TYP_POMINIETY = "skan_pominiety_rano"
TYP_ZAMKNIETY_RECZNIE = "brak_zamkniety_recznie"


def kolory_statusu(klucz: str) -> tuple[str | None, str | None]:
    """(kolor ekranu, kolor diod ramki) statusu z ``statusy.STATUSY``; klucz, ktorego tabela jeszcze nie ma - ``STATUSY_ZAPASOWE``."""
    w = ST.STATUSY.get(klucz)
    return (w.kolor, w.ramka) if w is not None else STATUSY_ZAPASOWE.get(klucz, (None, None))


def numery_plytki(uklad: str | None) -> tuple[int, ...] | None:
    """Dozwolone numery plytki porannej danego ukladu; None = uklad nie jest poranny (albo nieznany)."""
    c = SE.czesci_ukladu(uklad)
    if c is None or c["typ"] != SE.TYP_PLYTKI_TRYBU[SE.TRYB_RANO]:
        return None
    return NUMERY_PLYTEK_OKRAGLYCH_PORANNYCH if c["okragla"] else NUMERY_PLYTEK_PORANNYCH


def na_ramce(uklad: str | None) -> bool:
    """Czy plytka tego ukladu lezy na ramce porannej (kwadratowa poranna; okragle nie pasuja do wkladki - R58)."""
    c = SE.czesci_ukladu(uklad)
    return c is not None and c["typ"] == SE.TYP_PLYTKI_TRYBU[SE.TRYB_RANO] and not c["okragla"]


def _klucz_kuwety(kuweta: str | None) -> tuple:
    """Kolejnosc kuwet "wg numeru": zwykle numery rosnaco, potem prywatne "#", na koncu niejednoznaczne i puste."""
    m = re.fullmatch(r"(#?)(\d+)", kuweta or "")
    if m:
        return (1 if m[1] else 0, int(m[2]), kuweta)
    return (2, 0, str(kuweta or ""))


def _obowiazujace(decyzje: list[dict], rodzaje: tuple[str, ...]) -> list[dict]:
    """Z decyzji (rosnaco po id): niecofniete decyzje podanych rodzajow (cofniecie = wiersz ``cofniecie`` z id decyzji)."""
    cofniete = {int(d["wartosc"]) for d in decyzje if d["rodzaj"] == SE.RODZAJ_COFNIECIE and str(d["wartosc"] or "").isdigit()}
    return [d for d in decyzje if d["rodzaj"] in rodzaje and d["id"] not in cofniete]


def _obowiazujaca(decyzje: list[dict]) -> dict | None:
    """Ostatnia niecofnieta ``wybor_kandydata`` / ``przypisanie_reczne`` jednej pracy."""
    lista = _obowiazujace(decyzje, (RODZAJ_WYBOR, RODZAJ_PRZYPISANIE))
    return lista[-1] if lista else None


def _znaki(n: int) -> str:
    return ", ".join("?" * n)


def _wiersz_stanu(w: dict | None) -> dict | None:
    """Wiersz ``stan_punktow`` bez klucza - do zapisu "stanu sprzed" w dzienniku i odtworzenia."""
    return None if w is None else {k: w[k] for k in ("stan", "praca_id", "sesja_pieca_id", "czas")}


def plan_id(piec: dict) -> str:
    """Identyfikator planu ramki dla sesji pieca: ``<doba>-p<nr w dniu>`` (wzor protokolu ramki ``[A-Za-z0-9._-]{1,40}``)."""
    return f"{piec['data']}-p{piec['nr_w_dniu']}"


class SesjaRano:
    """Poranek na otwartej bazie, nad obiektem ``session.Sesja`` (operator, zegar, przyjecie skanu, ponowny skan)."""

    def __init__(self, sesja: SE.Sesja, *, prog_kandydata: float = PROG_KANDYDATA):
        try:
            prog = float(prog_kandydata)
        except (TypeError, ValueError):
            prog = -1.0
        if not 0.0 < prog <= 1.0:
            raise SE.BladSesji(f"prog kandydata musi byc liczba z przedzialu (0, 1] (jest {prog_kandydata!r})")
        self.sesja = sesja
        self.baza: B.Baza = sesja.baza
        self.prog_kandydata = prog

    @classmethod
    def z_ustawien(cls, ust: dict, sesja: SE.Sesja | None = None, **kw: Any) -> "SesjaRano":
        """Sesja poranna wg ``ustawienia.toml``: prog dwuznacznej = ``[match] prog_ostrzezenia_pokrycie`` (bez nowego klucza)."""
        return cls(sesja if sesja is not None else SE.Sesja.z_ustawien(ust), prog_kandydata=ust["match"]["prog_ostrzezenia_pokrycie"], **kw)

    # --- operator -----------------------------------------------------------------------------
    def _osoba(self, podany: str | None = None) -> str:
        """Osoba do kolumny ``operator`` - te same reguly co ``Sesja._operator`` (kopia: prywatnej metody A1p nie wolamy)."""
        if not self.sesja.operatorzy:
            raise SE.BladSesji("lista operatorow jest pusta - dopisz osoby w ustawienia.toml ([sesja] operatorzy) i uruchom program ponownie; "
                               "bez wskazanej osoby decyzje nie sa zapisywane")
        nazwa = podany if podany is not None else self.sesja.operator
        nazwa = nazwa.strip() if isinstance(nazwa, str) else nazwa
        if not nazwa:
            raise SE.BladSesji("nie wybrano operatora - wybierz osobe z listy; bez wskazanej osoby decyzje nie sa zapisywane")
        if nazwa not in self.sesja.operatorzy:
            raise SE.BladSesji("wskazanej osoby nie ma na liscie operatorow ([sesja] operatorzy w ustawienia.toml)")
        return nazwa

    # --- sesja pieca --------------------------------------------------------------------------
    @staticmethod
    def _piec(w: dict) -> dict:
        return {**w, "plan_id": plan_id(w)}

    def _ostatnia_aktywnosc(self, piec: dict) -> str:
        """Czas ostatniego skanu pieca (``skany.czas_analizy``), a bez skanow - czas otwarcia."""
        w = self.baza.wiersz("SELECT max(czas_analizy) AS t FROM skany WHERE sesja_pieca_id = ?", (piec["id"],))
        return max(x for x in (w["t"], piec["otwarto"]) if x)

    def _biezacy(self, piec: dict, teraz: str) -> bool:
        """Czy otwarty piec jest piecem BIEZACYM: z biezacej doby roboczej albo z poprzedniej, gdy jego ostatni skan (albo otwarcie)
        byl najwyzej ``OKNO_CIAGLOSCI_MIN`` minut temu (wsad rozkladany przez granice doby 06:00 - jeden piec)."""
        if piec["data"] == self.sesja.doba(teraz):
            return True
        minut = (dt.datetime.fromisoformat(teraz) - dt.datetime.fromisoformat(self._ostatnia_aktywnosc(piec))).total_seconds() / 60
        return 0 <= minut <= OKNO_CIAGLOSCI_MIN

    def otwarty_piec(self) -> dict | None:
        """Otwarty piec BIEZACY (``_biezacy``; wiersz ``sesje_pieca`` + ``plan_id``) albo None. Piec niezamkniety od wczesniejszej
        doby (stary) nigdy nie jest zwracany - jest tylko w ``otwarte_piece`` i w ostrzezeniu ``stan_pieca``."""
        teraz = self.sesja.teraz()
        for w in self.baza.wiersze("SELECT * FROM sesje_pieca WHERE zamknieto IS NULL ORDER BY id DESC"):
            if self._biezacy(w, teraz):
                return self._piec(w)
        return None

    def otwarte_piece(self) -> list[dict]:
        """Wszystkie otwarte sesje pieca (rosnaco po id) z polami ``biezacy`` i ``z_poprzedniej_doby`` (``data`` inna niz biezaca doba).
        Otwarty piec, ktory nie jest biezacy = niezamkniety stary piec (zamyka sie go ``zamknij_piec(plan_id=...)``)."""
        teraz = self.sesja.teraz()
        doba = self.sesja.doba(teraz)
        return [{**self._piec(w), "biezacy": self._biezacy(w, teraz), "z_poprzedniej_doby": w["data"] != doba}
                for w in self.baza.wiersze("SELECT * FROM sesje_pieca WHERE zamknieto IS NULL ORDER BY id")]

    def _ostatni_zamkniety_w_dobie(self) -> dict | None:
        """Ostatnio zamkniety piec, jesli zamknieto go w biezacej dobie roboczej (domyslny widok po "Zamknij piec")."""
        w = self.baza.wiersz("SELECT * FROM sesje_pieca WHERE zamknieto IS NOT NULL ORDER BY zamknieto DESC, id DESC LIMIT 1")
        return self._piec(w) if w is not None and self.sesja.doba(w["zamknieto"]) == self.sesja.doba() else None

    def otworz_piec(self) -> int:
        """Przycisk "Nowy piec": otwiera sesje pieca; odmowa, gdy jest otwarty piec biezacy. Zwykle niepotrzebny - otwiera ja
        pierwszy skan."""
        with self.baza.transakcja():
            return self._otworz("ui")

    def _otworz(self, zrodlo: str) -> int:
        otwarty = self.otwarty_piec()
        if otwarty is not None:
            raise SE.BladSesji(f"piec {otwarty['plan_id']} jest otwarty - najpierw 'Zamknij piec'")
        teraz = self.sesja.teraz()
        data = self.sesja.doba(teraz)
        nr = self.baza.wiersz("SELECT count(*) AS n FROM sesje_pieca WHERE data = ?", (data,))["n"] + 1
        pid = self.baza.wstaw("sesje_pieca", data=data, nr_w_dniu=nr, otwarto=teraz)
        self.baza.zdarzenie(zrodlo, TYP_OTWARTY, {"sesja_pieca_id": pid, "data": data, "nr_w_dniu": nr}, czas=teraz)
        return pid

    def _piec_po_id(self, sesja_pieca_id: int) -> dict:
        w = self.baza.wiersz("SELECT * FROM sesje_pieca WHERE id = ?", (sesja_pieca_id,))
        if w is None:
            raise SE.BladSesji(f"nie ma sesji pieca {sesja_pieca_id}")
        return self._piec(w)

    def _piec_otwarty_dla(self, sesja_pieca_id: int | None, co: str) -> dict:
        """Piec, do ktorego nalezy skan albo praca - musi byc otwarty (zamknietego pieca nie zmienia sie)."""
        w = self.baza.wiersz("SELECT * FROM sesje_pieca WHERE id = ?", (sesja_pieca_id,)) if sesja_pieca_id is not None else None
        if w is None:
            raise SE.BladSesji(f"{co}: skan nie nalezy do zadnego pieca - skany poranne przyjmuje sesja poranna (SesjaRano.przyjmij_wynik)")
        if w["zamknieto"] is not None:
            raise SE.BladSesji(f"{co}: piec {w['nr_w_dniu']} doby {w['data']} jest zamkniety - jego prac i skanow nie da sie zmienic "
                               f"(pomylke cofa otworz_piec_ponownie)")
        return w

    def piece(self, data: str | None = None) -> list[dict]:
        """Sesje pieca doby roboczej ``data`` (domyslnie biezacej): wiersz ``sesje_pieca`` + ``plan_id``, ``otwarty``, ``skanow``."""
        data = data or self.sesja.doba()
        wiersze = self.baza.wiersze("SELECT sp.*, (SELECT count(*) FROM skany s WHERE s.sesja_pieca_id = sp.id) AS skanow "
                                    "FROM sesje_pieca sp WHERE sp.data = ? ORDER BY sp.id", (data,))
        teraz = self.sesja.teraz()
        biezaca = self.sesja.doba(teraz)
        return [{**self._piec(w), "otwarty": w["zamknieto"] is None, "z_poprzedniej_doby": w["zamknieto"] is None and w["data"] != biezaca,
                 "biezacy": w["zamknieto"] is None and self._biezacy(w, teraz)} for w in wiersze]

    # --- przyjecie skanu ----------------------------------------------------------------------
    def przyjmij_wynik(self, zdarzenie: Any, wynik: dict) -> int:
        """Skan plytki porannej: ``Sesja.przyjmij_wynik(..., tryb="rano")`` + przypisanie do otwartego pieca (bez otwartego -
        nowy piec) + przypisanie obowiazujace prac (``prace.projekt_id``: projekt pracy pewnej, inne puste do decyzji).
        Skan trafia do otwartego pieca biezacego (``otwarty_piec``): z biezacej doby albo z poprzedniej, gdy ostatni skan tego pieca byl
        najwyzej ``OKNO_CIAGLOSCI_MIN`` (90) minut temu; inaczej otwiera nowy, a stary zostaje otwarty z ostrzezeniem.
        Zwraca ``skany.id``. Nie wymaga operatora."""
        with self.baza.transakcja():
            pid = self._piec_do_skanu()
            skan_id = self.sesja.przyjmij_wynik(zdarzenie, wynik, tryb=SE.TRYB_RANO)
            self.baza.wykonaj("UPDATE skany SET sesja_pieca_id = ? WHERE id = ?", (pid, skan_id))
            for p in self.baza.wiersze("SELECT * FROM prace WHERE skan_id = ? ORDER BY id", (skan_id,)):
                self._zapisz_przypisanie(p["id"], self._przypisanie_auto(p))
        return skan_id

    def przyjmij_blad(self, zdarzenie: Any, blad: BaseException | str) -> int:
        """Analiza skanu porannego bez wyniku: ``Sesja.przyjmij_blad(..., tryb="rano")`` + przypisanie do pieca (blokuje
        "Zamknij piec", dopoki skan nie zostanie pominiety - plytke trzeba zeskanowac ponownie)."""
        with self.baza.transakcja():
            pid = self._piec_do_skanu()
            skan_id = self.sesja.przyjmij_blad(zdarzenie, blad, tryb=SE.TRYB_RANO)
            self.baza.wykonaj("UPDATE skany SET sesja_pieca_id = ? WHERE id = ?", (pid, skan_id))
        return skan_id

    def _piec_do_skanu(self) -> int:
        """Piec dla nowego skanu porannego: otwarty piec biezacy albo nowy (recenzje PR #22 r2 P1 i PR #23 r2 P2)."""
        piec = self.otwarty_piec()
        return piec["id"] if piec is not None else self._otworz("system")

    # --- skany otwartego pieca: ponowny skan, numer plytki, pominiecie ---------------------------
    def _skan_rano(self, skan_id: int | None) -> dict:
        sk = self.baza.wiersz("SELECT * FROM skany WHERE id = ?", (skan_id,)) if skan_id is not None else None
        if sk is None:
            raise SE.BladSesji(f"nie ma skanu {skan_id}")
        if sk["tryb"] != SE.TRYB_RANO:
            raise SE.BladSesji(f"skan {skan_id} ma tryb {sk['tryb']!r} - sesja poranna obsluguje tylko skany poranne")
        self._piec_otwarty_dla(sk["sesja_pieca_id"], f"skan {skan_id}")
        return sk

    def zastap_skan(self, skan_id: int, poprzedni_id: int | None = None, operator: str | None = None) -> int:
        """Potwierdzenie "to ponowny skan tej plytki" (Z4) - tylko w obrebie jednego otwartego pieca. Bez ``poprzedni_id``:
        skan z propozycji ``stan_pieca()["do_potwierdzenia"]``. Decyzje skanu zastapionego przestaja sie liczyc (nie przechodza).
        Zwraca id skanu zastapionego (``Sesja.zastap_skan``)."""
        self._osoba(operator)
        with self.baza.transakcja():
            nowy = self._skan_rano(skan_id)
            if poprzedni_id is None:
                prop = next((x for x in self._propozycje(nowy["sesja_pieca_id"]) if x["skan_id"] == nowy["id"]), None)
                if prop is None:
                    raise SE.BladSesji(f"skan {skan_id}: w tym piecu nie ma wczesniejszego skanu tej samej plytki - skan do zastapienia wskaz wprost")
                poprzedni_id = prop["poprzedni_id"]
            else:
                stary = self.baza.wiersz("SELECT * FROM skany WHERE id = ?", (poprzedni_id,))
                if stary is None:
                    raise SE.BladSesji(f"nie ma skanu {poprzedni_id}")
                if stary["sesja_pieca_id"] != nowy["sesja_pieca_id"]:
                    raise SE.BladSesji(f"skan {poprzedni_id} nalezy do innego pieca niz skan {skan_id} - zastapic mozna tylko skan "
                                       f"z tego samego, otwartego pieca")
            return self.sesja.zastap_skan(skan_id, poprzedni_id, operator)

    def cofnij_zastapienie(self, skan_id: int, operator: str | None = None) -> int:
        """Cofa pomylkowe zastapienie skanu porannego (``Sesja.cofnij_zastapienie``) - tylko w otwartym piecu."""
        with self.baza.transakcja():
            self._skan_rano(skan_id)
            return self.sesja.cofnij_zastapienie(skan_id, operator)

    def podaj_numer_plytki(self, skan_id: int, numer: Any, operator: str | None = None) -> int:
        """Numer plytki wskazany recznie (Z3: rano obowiazkowy przed "Zamknij piec") - tylko numer plytki porannej tego ukladu
        (kwadratowe 4-6 = plytki ramki porannej, okragle 9); potem ``Sesja.podaj_numer_plytki``."""
        with self.baza.transakcja():
            sk = self._skan_rano(skan_id)
            dozwolone = numery_plytki(sk["uklad"])
            if dozwolone is None:
                raise SE.BladSesji(f"skan {skan_id}: uklad {sk['uklad']!r} nie jest plytka poranna - numeru nie podaje sie; zeskanuj plytke "
                                   f"poranna albo pomin ten skan")
            try:
                n = int(numer)
            except (TypeError, ValueError):
                n = None
            if n not in dozwolone:
                raise SE.BladSesji(f"skan {skan_id}: numer plytki {numer!r} spoza plytek porannych tego ukladu "
                                   f"({', '.join(map(str, dozwolone))}) - sprawdz numer na plytce")
            return self.sesja.podaj_numer_plytki(skan_id, n, operator)

    def dopusc_plytke(self, skan_id: int, operator: str | None = None) -> int:
        """Rano plytki nie z trybu NIE dopuszcza sie (P2 recenzji PR #23): ramka poranna nie zna jej ukladu, plan bylby odrzucony.
        Prace trzeba przelozyc na plytke poranna i zeskanowac; skan zablokowany usuwa z blokad ``pomin_skan``."""
        sk = self._skan_rano(skan_id)
        raise SE.BladSesji(f"skan {skan_id}: plytki {sk['uklad']!r} nie mozna dopuscic rano - ramka poranna jej nie obsluzy; przeloz prace "
                           f"na plytke poranna i zeskanuj ja, a ten skan pomin")

    def cofnij_dopuszczenie(self, skan_id: int, operator: str | None = None) -> int:
        """Cofa dopuszczenie (zrobione wprost przez ``Sesja``) skanu porannego w otwartym piecu - ``Sesja.cofnij_dopuszczenie``."""
        with self.baza.transakcja():
            self._skan_rano(skan_id)
            return self.sesja.cofnij_dopuszczenie(skan_id, operator)

    def pomin_skan(self, skan_id: int, operator: str | None = None) -> int:
        """Skan nie nalezy do pieca (bez wyniku, niezgodny uklad, plytka nie z trybu, zly numer, plytka zeskanowana ponownie, gdy
        zastapienia nie da sie potwierdzic): jego prace nie licza sie, nie ida do planu ramki i skan nie blokuje "Zamknij piec".
        Decyzja ``pomin_skan`` (z operatorem; cofa ``cofnij_pominiecie``). Zwraca ``decyzje.id``."""
        osoba = self._osoba(operator)
        with self.baza.transakcja():
            sk = self._skan_rano(skan_id)
            if sk["status"] == SE.STATUS_ZASTAPIONY:
                raise SE.BladSesji(f"skan {skan_id} jest juz zastapiony - nie liczy sie i nie blokuje")
            if sk["id"] in self._pominiete([sk["id"]]):
                raise SE.BladSesji(f"skan {skan_id} jest juz pominiety")
            if sk["zastepuje_id"] is not None:  # plytka zostalaby bez skanu, ktory sie liczy
                raise SE.BladSesji(f"skan {skan_id} zastapil skan {sk['zastepuje_id']} - najpierw cofnij zastapienie (poprzedni skan plytki "
                                   f"wroci), potem pomin wlasciwy skan")
            teraz = self.sesja.teraz()
            d = self.baza.wstaw("decyzje", skan_id=sk["id"], rodzaj=RODZAJ_POMIN_SKAN, operator=osoba, czas=teraz)
            self.baza.zdarzenie("ui", TYP_POMINIETY, {"decyzja_id": d, "status": sk["status"], "sesja_pieca_id": sk["sesja_pieca_id"]},
                                skan_id=sk["id"], czas=teraz)
        return d

    def cofnij_pominiecie(self, skan_id: int, operator: str | None = None) -> int:
        """Cofa ``pomin_skan`` (wiersz ``cofniecie``): skan znow sie liczy albo blokuje."""
        osoba = self._osoba(operator)
        with self.baza.transakcja():
            sk = self._skan_rano(skan_id)
            ob = _obowiazujace(self._decyzje_skanow([sk["id"]]).get(sk["id"], []), (RODZAJ_POMIN_SKAN,))
            if not ob:
                raise SE.BladSesji(f"skan {skan_id} nie jest pominiety - nie ma czego cofac")
            return self.baza.wstaw("decyzje", skan_id=sk["id"], rodzaj=SE.RODZAJ_COFNIECIE, wartosc=str(ob[-1]["id"]), operator=osoba,
                                   czas=self.sesja.teraz())

    def _decyzje_skanow(self, skany_ids: list) -> dict[int, list[dict]]:
        """Decyzje o skanach (bez pracy): ``pomin_skan`` i ``cofniecie``, rosnaco po id."""
        wynik: dict[int, list[dict]] = {}
        for d in self._wiersze_in(f"SELECT * FROM decyzje WHERE praca_id IS NULL AND rodzaj IN ('{RODZAJ_POMIN_SKAN}', '{SE.RODZAJ_COFNIECIE}') "
                                  f"AND skan_id IN ({{}}) ORDER BY id", list(skany_ids)):
            wynik.setdefault(d["skan_id"], []).append(d)
        return wynik

    def _pominiete(self, skany_ids: list) -> set[int]:
        return {s for s, lst in self._decyzje_skanow(skany_ids).items() if _obowiazujace(lst, (RODZAJ_POMIN_SKAN,))}

    def _propozycje(self, sesja_pieca_id: int) -> list[dict]:
        """Propozycje "to ponowny skan tej plytki?": skan aktywny i wczesniejszy skan aktywny TEGO SAMEGO pieca z tym samym numerem
        plytki i rodzina ukladu (albo ta sama zawartosc pliku); skany pominiete i pary z cofnietym zastapieniem sa pomijane."""
        skany = self.baza.wiersze(f"SELECT * FROM skany WHERE sesja_pieca_id = ? AND status IN ({_znaki(len(SE.STATUSY_AKTYWNE))}) ORDER BY id",
                                  (sesja_pieca_id, *SE.STATUSY_AKTYWNE))
        pominiete = self._pominiete([s["id"] for s in skany])
        skany = [s for s in skany if s["id"] not in pominiete]
        cofniete = {(d["skan_id"], int(d["wartosc"])) for d in self._wiersze_in(
            f"SELECT skan_id, wartosc FROM decyzje WHERE rodzaj = '{SE.RODZAJ_COFNIJ_ZASTAPIENIE}' AND skan_id IN ({{}})", [s["id"] for s in skany])
            if str(d["wartosc"] or "").isdigit()}
        wynik = []
        for i, s in enumerate(skany):
            for t in reversed(skany[:i]):
                if (s["id"], t["id"]) in cofniete:
                    continue
                ten_sam_plik = bool(s["sha16"]) and s["sha16"] == t["sha16"]
                ta_sama_plytka = (s["numer_plytki"] is not None and s["numer_plytki"] == t["numer_plytki"]
                                  and SE.rodzina_ukladu(s["uklad"]) == SE.rodzina_ukladu(t["uklad"]))
                if ten_sam_plik or ta_sama_plytka:
                    wynik.append({"skan_id": s["id"], "poprzedni_id": t["id"], "numer_plytki": s["numer_plytki"],
                                  "wspolnych_prac": len(self._wspolne_prace([s["id"], t["id"]]))})
                    break
        return wynik

    def _wspolne_prace(self, skany_ids: list) -> set:
        """``sha16`` 1. kandydatow wspolne dla prac wszystkich skanow (ten sam projekt na obu = ta sama praca; 0 = rozne plytki)."""
        zbiory: dict[int, set] = {i: set() for i in skany_ids}
        for w in self._wiersze_in("SELECT skan_id, kandydat1_sha16 FROM prace WHERE kandydat1_sha16 IS NOT NULL AND skan_id IN ({})", list(skany_ids)):
            zbiory[w["skan_id"]].add(w["kandydat1_sha16"])
        return set.intersection(*zbiory.values()) if zbiory else set()

    # --- decyzje o pracach porannych ------------------------------------------------------------
    def _praca_rano(self, praca_id: int | None) -> dict:
        """Praca, o ktorej wolno zdecydowac rano: skan poranny ``przyjety``, niepominiety, w otwartym piecu."""
        p = self.baza.wiersz("SELECT p.*, s.status AS status_skanu, s.tryb AS tryb_skanu, s.sesja_pieca_id FROM prace p "
                             "JOIN skany s ON s.id = p.skan_id WHERE p.id = ?", (praca_id,)) if praca_id is not None else None
        if p is None:
            raise SE.BladSesji(f"nie ma pracy {praca_id}")
        if p["tryb_skanu"] != SE.TRYB_RANO:
            raise SE.BladSesji(f"praca {praca_id} nalezy do skanu w trybie {p['tryb_skanu']!r} - sesja poranna przyjmuje decyzje tylko o pracach "
                               f"skanow porannych (decyzje wieczorne obsluguje session)")
        self._piec_otwarty_dla(p["sesja_pieca_id"], f"praca {praca_id}")
        if p["status_skanu"] != SE.STATUS_PRZYJETY:
            rada = {SE.STATUS_ZASTAPIONY: "podejmij decyzje na nowym skanie plytki", SE.STATUS_DO_POWTORZENIA: "zeskanuj plytke ponownie",
                    SE.STATUS_NIEZGODNY_UKLAD: "zeskanuj plytke ponownie z wlasciwym ukladem",
                    SE.STATUS_PLYTKA_NIE_Z_TRYBU: "to plytka nie z tego trybu: przeloz prace na plytke poranna i zeskanuj ja",
                    }.get(p["status_skanu"], "skan nie zostal przyjety")
            raise SE.BladSesji(f"praca {praca_id}: skan {p['skan_id']} ma status {p['status_skanu']!r} - decyzje mozna podejmowac tylko na skanie "
                               f"przyjetym ({rada})")
        if p["skan_id"] in self._pominiete([p["skan_id"]]):
            raise SE.BladSesji(f"praca {praca_id}: skan {p['skan_id']} jest pominiety - cofnij pominiecie albo zdecyduj na nowym skanie")
        return p

    def _decyzja_przypisania(self, praca_id: int) -> dict | None:
        return _obowiazujaca(self.baza.wiersze("SELECT * FROM decyzje WHERE praca_id = ? AND rodzaj IN (?, ?, ?) ORDER BY id",
                                               (praca_id, RODZAJ_WYBOR, RODZAJ_PRZYPISANIE, SE.RODZAJ_COFNIECIE)))

    def wybierz_kandydata(self, praca_id: int, sha16: str, operator: str | None = None) -> int:
        """Rozstrzygniecie pracy dwuznacznej kliknieciem: ``sha16`` = 1. albo 2. kandydat pracy. Zwraca ``decyzje.id``.
        Kandydat w kilku zleceniach (ten sam plik w "Cyrkon" i "Prywatne") albo spoza indeksu - odmowa, rada: przypisanie reczne."""
        osoba = self._osoba(operator)
        with self.baza.transakcja():
            p = self._praca_rano(praca_id)
            kandydaci = [k for k in (p["kandydat1_sha16"], p["kandydat2_sha16"]) if k]
            if not sha16 or sha16 not in kandydaci:
                raise SE.BladSesji(f"praca {praca_id}: wskazany projekt nie jest kandydatem tej pracy (kandydaci: {', '.join(kandydaci) or 'brak'}) - "
                                   f"inny projekt wskaz przypisaniem recznym")
            projekty = self._projekty_sha([sha16]).get(sha16, [])
            if len(projekty) != 1:
                powod = "nie ma projektu w indeksie" if not projekty else f"jest w {len(projekty)} zleceniach naraz"
                raise SE.BladSesji(f"praca {praca_id}: kandydat {sha16} {powod} - wskaz projekt przypisaniem recznym")
            d = self.baza.wstaw("decyzje", praca_id=p["id"], skan_id=p["skan_id"], rodzaj=RODZAJ_WYBOR, wartosc=sha16, operator=osoba,
                                czas=self.sesja.teraz())
            self._zapisz_przypisanie(p["id"], projekty[0]["projekt_id"])
        return d

    def przypisz_recznie(self, praca_id: int, projekt_id: int | None, operator: str | None = None) -> int:
        """Przypisanie reczne pracy do projektu (praca nieznana, konflikt, kandydat w dwoch zleceniach). ``projekt_id`` = None:
        praca "bez projektu" (nieznana - przymiarka na modelach; tak rozstrzyga sie tez konflikt). Zwraca ``decyzje.id``."""
        osoba = self._osoba(operator)
        with self.baza.transakcja():
            p = self._praca_rano(praca_id)
            if projekt_id is not None:
                if isinstance(projekt_id, bool) or not str(projekt_id).isdigit():
                    raise SE.BladSesji(f"id projektu musi byc liczba (jest {projekt_id!r})")
                projekt_id = int(projekt_id)
                if self.baza.wiersz("SELECT id FROM projekty WHERE id = ? AND usuniety = 0", (projekt_id,)) is None:
                    raise SE.BladSesji(f"nie ma projektu {projekt_id} w indeksie (albo jego plik usunieto) - wybierz projekt z puli porannej")
            d = self.baza.wstaw("decyzje", praca_id=p["id"], skan_id=p["skan_id"], rodzaj=RODZAJ_PRZYPISANIE,
                                wartosc=BEZ_PROJEKTU if projekt_id is None else str(projekt_id), operator=osoba, czas=self.sesja.teraz())
            self._zapisz_przypisanie(p["id"], projekt_id)
        return d

    def cofnij_przypisanie(self, praca_id: int, operator: str | None = None, *, decyzja_id: int | None = None) -> int:
        """Cofa obowiazujaca decyzje przypisania (wraca poprzednia albo przypisanie automatyczne); dopisuje wiersz ``cofniecie``.
        ``decyzja_id`` (zalecane dla okna): cofnij dokladnie te decyzje - inna obowiazujaca = odmowa (podwojne klikniecie)."""
        osoba = self._osoba(operator)
        with self.baza.transakcja():
            p = self._praca_rano(praca_id)
            ob = self._decyzja_przypisania(p["id"])
            if ob is None:
                raise SE.BladSesji(f"praca {praca_id}: nie ma decyzji do cofniecia")
            if decyzja_id is not None and ob["id"] != decyzja_id:
                raise SE.BladSesji(f"praca {praca_id}: obowiazuje decyzja {ob['id']}, nie {decyzja_id} - odswiez widok (decyzja juz cofnieta?)")
            d = self.baza.wstaw("decyzje", praca_id=p["id"], skan_id=p["skan_id"], rodzaj=SE.RODZAJ_COFNIECIE, wartosc=str(ob["id"]),
                                operator=osoba, czas=self.sesja.teraz())
            nowa = self._decyzja_przypisania(p["id"])
            self._zapisz_przypisanie(p["id"], self._projekt_z_decyzji(nowa) if nowa is not None else self._przypisanie_auto(p))
        return d

    def _przypisanie_auto(self, praca: dict) -> int | None:
        """Przypisanie automatyczne rano: projekt 1. kandydata tylko przy dopasowaniu zielonym i jednym projekcie o tym ``sha16``."""
        sha = praca["kandydat1_sha16"]
        if praca["status_match"] != "zielony" or not sha:
            return None
        projekty = self._projekty_sha([sha]).get(sha, [])
        return projekty[0]["projekt_id"] if len(projekty) == 1 else None

    def _projekt_z_decyzji(self, d: dict) -> int | None:
        if d["rodzaj"] == RODZAJ_WYBOR:
            projekty = self._projekty_sha([d["wartosc"]]).get(d["wartosc"], [])
            return projekty[0]["projekt_id"] if len(projekty) == 1 else None
        return int(d["wartosc"]) if str(d["wartosc"] or "").isdigit() else None

    def _zapisz_przypisanie(self, praca_id: int, projekt_id: int | None) -> None:
        """``prace.projekt_id`` = przypisanie obowiazujace (plan 3.4: automatyczne albo z decyzji)."""
        self.baza.wykonaj("UPDATE prace SET projekt_id = ? WHERE id = ?", (projekt_id, praca_id))

    # --- punkty i ich stan ----------------------------------------------------------------------
    def _wiersze_in(self, sql: str, wartosci: list, porcja: int = 500) -> list[dict]:
        """Zapytanie z lista wartosci w miejscu ``{}``, w porcjach; pusta lista = brak wierszy."""
        wynik: list[dict] = []
        for i in range(0, len(wartosci), porcja):
            czesc = wartosci[i:i + porcja]
            wynik += self.baza.wiersze(sql.format(_znaki(len(czesc))), tuple(czesc))
        return wynik

    _POLA_PROJEKTU = ("SELECT p.id AS projekt_id, p.sha16, p.zlecenie_id, p.zeby, p.typ, p.usuniety, z.kuweta, z.zrodlo "
                      "FROM projekty p JOIN zlecenia z ON z.id = p.zlecenie_id WHERE ")

    def _projekty_sha(self, shas: list) -> dict[str, list[dict]]:
        """``sha16`` -> projekty (punkty, ``usuniety = 0``) o tej zawartosci; bez nazw folderow i plikow."""
        wynik: dict[str, list[dict]] = {}
        for w in self._wiersze_in(self._POLA_PROJEKTU + "p.usuniety = 0 AND p.sha16 IN ({}) ORDER BY p.id", sorted({s for s in shas if s})):
            wynik.setdefault(w["sha16"], []).append(w)
        return wynik

    def _projekty_id(self, ids: list) -> dict[int, dict]:
        return {w["projekt_id"]: w for w in self._wiersze_in(self._POLA_PROJEKTU + "p.id IN ({})", sorted({i for i in ids if i is not None}))}

    def _poprzednicy(self, info: dict[int, dict]) -> dict[int, list[dict]]:
        """Punkt (projekt ``usuniety = 0``) -> usuniete projekty z wierszem ``stan_punktow`` o tej samej zawartosci (``sha16``)
        z tego samego zlecenia albo ze zlecenia o tej samej (niepustej) kuwecie - ten sam plik po zmianie nazwy pliku albo
        folderu w indeksie (A4 zaklada wtedy nowe ``projekt_id``). Najnowszy (czas stanu, id) na koncu listy."""
        zywe = {i: p for i, p in info.items() if not p["usuniety"] and p["sha16"]}
        if not zywe:
            return {}
        wiersze = self._wiersze_in(
            "SELECT p.id AS projekt_id, p.sha16, p.zlecenie_id, z.kuweta, sp.stan, sp.praca_id, sp.sesja_pieca_id, sp.czas "
            "FROM projekty p JOIN zlecenia z ON z.id = p.zlecenie_id JOIN stan_punktow sp ON sp.projekt_id = p.id "
            "WHERE p.usuniety = 1 AND p.sha16 IN ({})", sorted({p["sha16"] for p in zywe.values()}))
        wynik: dict[int, list[dict]] = {}
        for i, p in zywe.items():
            lista = [w for w in wiersze if w["sha16"] == p["sha16"] and w["projekt_id"] != i
                     and (w["zlecenie_id"] == p["zlecenie_id"] or (p["kuweta"] and w["kuweta"] == p["kuweta"]))]
            if lista:
                wynik[i] = sorted(lista, key=lambda w: (w["czas"] or "", w["projekt_id"]))
        return wynik

    def _nastepcy(self, usuniete: dict[int, dict]) -> dict[int, int]:
        """Usuniety projekt -> JEDYNY zywy projekt o tym samym ``sha16`` z tego samego zlecenia albo zlecenia o tej samej kuwecie
        (odwrotnosc ``_poprzednicy``): praca przypisana przed zmiana nazwy folderu / pliku w trakcie otwartego pieca."""
        stare = {i: q for i, q in usuniete.items() if q["sha16"]}
        if not stare:
            return {}
        zywe = self._wiersze_in(self._POLA_PROJEKTU + "p.usuniety = 0 AND p.sha16 IN ({})", sorted({q["sha16"] for q in stare.values()}))
        wynik = {}
        for i, q in stare.items():
            lista = [w for w in zywe if w["sha16"] == q["sha16"] and (w["zlecenie_id"] == q["zlecenie_id"] or (q["kuweta"] and w["kuweta"] == q["kuweta"]))]
            if len(lista) == 1:
                wynik[i] = lista[0]["projekt_id"]
        return wynik

    def _stany(self, info: dict[int, dict]) -> dict[int, dict]:
        """Projekt -> obowiazujacy stan punktu: wlasny wiersz ``stan_punktow`` albo (bez wlasnego) stan najnowszego poprzednika
        (``_poprzednicy``; pole ``odziedziczony_z``). Brak w slowniku = ``oczekuje``."""
        wlasne = {w["projekt_id"]: {**w, "odziedziczony_z": None}
                  for w in self._wiersze_in("SELECT * FROM stan_punktow WHERE projekt_id IN ({})", sorted(info))}
        bez = {i: p for i, p in info.items() if i not in wlasne}
        for i, lista in self._poprzednicy(bez).items():
            w = lista[-1]
            wlasne[i] = {"projekt_id": i, "stan": w["stan"], "praca_id": w["praca_id"], "sesja_pieca_id": w["sesja_pieca_id"],
                         "czas": w["czas"], "odziedziczony_z": w["projekt_id"]}
        return wlasne

    def _punkty_zlecen(self, zlecenia: list) -> dict[int, list[dict]]:
        """Zlecenie -> jego punkty (projekty ``usuniety = 0``, bez ``TYPY_BEZ_PUNKTU``) z obowiazujacym stanem (``_stany``)."""
        info = {w["projekt_id"]: w for w in self._wiersze_in(self._POLA_PROJEKTU + "p.usuniety = 0 AND p.zlecenie_id IN ({}) ORDER BY p.id",
                                                             sorted({z for z in zlecenia if z is not None}))
                if w["typ"] not in TYPY_BEZ_PUNKTU}
        stany = self._stany(info)
        wynik: dict[int, list[dict]] = {}
        for i, p in info.items():
            st = stany.get(i) or {}
            wynik.setdefault(p["zlecenie_id"], []).append({**p, "stan": st.get("stan"), "sesja_pieca_id": st.get("sesja_pieca_id"),
                                                           "odziedziczony_z": st.get("odziedziczony_z")})
        return wynik

    def _wlasny_stan(self, projekt_id: int) -> dict | None:
        return _wiersz_stanu(self.baza.wiersz("SELECT * FROM stan_punktow WHERE projekt_id = ?", (projekt_id,)))

    def _ustaw_punkt(self, projekt_id: int, stan: str, praca_id: int | None, sesja_pieca_id: int | None, czas: str) -> None:
        self.baza.wykonaj(
            """INSERT INTO stan_punktow (projekt_id, stan, praca_id, sesja_pieca_id, czas) VALUES (?, ?, ?, ?, ?)
               ON CONFLICT (projekt_id) DO UPDATE SET stan = excluded.stan, praca_id = excluded.praca_id,
               sesja_pieca_id = excluded.sesja_pieca_id, czas = excluded.czas""", (projekt_id, stan, praca_id, sesja_pieca_id, czas))

    def _przywroc_punkt(self, projekt_id: int, wiersz: dict | None) -> None:
        """Stan punktu sprzed zmiany (None = punkt bez wiersza: ``oczekuje`` albo stan odziedziczony)."""
        if wiersz is None:
            self.baza.wykonaj("DELETE FROM stan_punktow WHERE projekt_id = ?", (projekt_id,))
        else:
            self._ustaw_punkt(projekt_id, wiersz["stan"], wiersz["praca_id"], wiersz["sesja_pieca_id"], wiersz["czas"])

    @staticmethod
    def _zlecenie(z_id: int, punkty: list[dict], teraz_ids: set, wczesniej: dict) -> dict:
        """Wpis zlecenia: punkty rozpoznane (w tym piecu = ``teraz_ids``, wczesniej = stan koncowy) i brakujace ze stanem."""
        brakujace, w_tym, z_dofrez = [], 0, False
        for pt in punkty:
            if pt["projekt_id"] in teraz_ids:
                w_tym += 1
                z_dofrez = z_dofrez or pt["stan"] == SE.STAN_DO_DOFREZOWANIA
            elif not wczesniej.get(pt["projekt_id"], False):
                brakujace.append({"projekt_id": pt["projekt_id"], "sha16": pt["sha16"], "zeby": pt["zeby"], "typ": pt["typ"],
                                  "stan": pt["stan"] or SE.STAN_OCZEKUJE})
        pierwszy = punkty[0]
        return {"zlecenie_id": z_id, "kuweta": pierwszy["kuweta"], "zrodlo": pierwszy["zrodlo"], "punktow": len(punkty),
                "rozpoznane": len(punkty) - len(brakujace), "w_tym_piecu": w_tym, "kompletne": not brakujace, "z_dofrezowaniem": z_dofrez,
                "brakujace": brakujace}

    @staticmethod
    def _sortuj_zlecenia(lista: list[dict]) -> list[dict]:
        return sorted(lista, key=lambda z: (_klucz_kuwety(z["kuweta"]), z["zlecenie_id"]))

    # --- stan pieca -----------------------------------------------------------------------------
    def _oblicz(self, piec: dict) -> dict:
        """Stan pieca z bazy: skany i prace z klasa, konflikty, zlecenia dotkniete (prowizorycznie), propozycje, blokady."""
        pid = piec["id"]
        otwarty = piec["zamknieto"] is None
        skany = self.baza.wiersze("SELECT * FROM skany WHERE sesja_pieca_id = ? ORDER BY id", (pid,))
        pominiete = self._pominiete([s["id"] for s in skany])
        aktywne = [s for s in skany if s["status"] in SE.STATUSY_AKTYWNE and s["id"] not in pominiete]
        aktywne_ids = {s["id"] for s in aktywne}
        prace = self._wiersze_in("SELECT * FROM prace WHERE skan_id IN ({}) ORDER BY skan_id, id", [s["id"] for s in skany])
        decyzje: dict[int, list[dict]] = {}
        for d in self._wiersze_in(f"SELECT * FROM decyzje WHERE rodzaj IN ('{RODZAJ_WYBOR}', '{RODZAJ_PRZYPISANIE}', '{SE.RODZAJ_COFNIECIE}') "
                                  f"AND praca_id IN ({{}}) ORDER BY id", [p["id"] for p in prace]):
            decyzje.setdefault(d["praca_id"], []).append(d)
        obow = {pid_: _obowiazujaca(lst) for pid_, lst in decyzje.items()}
        po_sha = self._projekty_sha([p["kandydat1_sha16"] for p in prace] + [p["kandydat2_sha16"] for p in prace])
        projekty = self._projekty_id([p["projekt_id"] for p in prace])
        nastepcy = self._nastepcy({i: q for i, q in projekty.items() if q["usuniety"]})  # zmiana nazwy w trakcie pieca (r2 P3)
        if nastepcy:
            projekty.update(self._projekty_id(list(nastepcy.values())))
        stany = self._stany(projekty)
        skan_po_id = {s["id"]: s for s in skany}

        def wczesniej(st: dict | None) -> bool:  # punkt zamknal juz inny piec (otwarty: kazdy inny; zamkniety: wczesniejszy) albo reka
            return st is not None and st["stan"] in STANY_KONCOWE and (
                st["sesja_pieca_id"] is None or (st["sesja_pieca_id"] != pid if otwarty else st["sesja_pieca_id"] < pid))

        # SE8: ten sam projekt w dwoch gniazdach skanow przyjetych tego pieca (dwa fragmenty w jednym gniezdzie = jedno miejsce)
        miejsca: dict[int, list[dict]] = {}
        for p in prace:
            if p["projekt_id"] is not None and p["skan_id"] in aktywne_ids and skan_po_id[p["skan_id"]]["status"] == SE.STATUS_PRZYJETY:
                miejsca.setdefault(nastepcy.get(p["projekt_id"], p["projekt_id"]), []).append(p)
        w_konflikcie = {pr for pr, lst in miejsca.items()
                        if len({(x["skan_id"], x["gniazdo"] if x["gniazdo"] is not None else f"poza-{x['id']}") for x in lst}) > 1}

        def kandydaci(p: dict) -> list[dict]:
            return [{"sha16": p[f"kandydat{i}_sha16"], "pokrycie": p[f"kandydat{i}_pokrycie"],
                     "projekty": [{k: q[k] for k in ("projekt_id", "zlecenie_id", "kuweta", "zeby", "typ", "zrodlo")}
                                  for q in po_sha.get(p[f"kandydat{i}_sha16"], [])]}
                    for i in (1, 2) if p[f"kandydat{i}_sha16"]]

        wynik_skany, liczniki, nierozstrzygniete, liczone, poprawki = [], {}, {"dwuznaczne": 0, "nieznane": 0}, {}, []
        odhaczone_cache: dict[int, bool] = {}
        for s in skany:
            aktywny = s["id"] in aktywne_ids
            lista = []
            for p in (x for x in prace if x["skan_id"] == s["id"]):
                d = obow.get(p["id"])
                kand = kandydaci(p)
                pr = nastepcy.get(p["projekt_id"], p["projekt_id"])
                st = stany.get(pr) if pr is not None else None
                if not aktywny:
                    klasa = None
                elif s["status"] == SE.STATUS_DO_POWTORZENIA:
                    klasa = KLASA_DO_POWTORZENIA
                elif pr is None:
                    dwuznaczna = (d is None and (p["kandydat1_pokrycie"] or 0.0) >= self.prog_kandydata and any(k["projekty"] for k in kand))
                    klasa = KLASA_DWUZNACZNA if dwuznaczna else KLASA_NIEZNANA
                elif pr in w_konflikcie:
                    klasa = KLASA_KONFLIKT
                elif wczesniej(st):
                    klasa = KLASA_POPRAWKA
                else:
                    klasa = KLASA_PRZYPISANA if d is not None else KLASA_PEWNA
                info = projekty.get(pr) if pr is not None else None
                kuweta = info["kuweta"] if info else None
                odhaczone = False
                if klasa == KLASA_POPRAWKA:
                    z_id = info["zlecenie_id"]
                    if z_id not in odhaczone_cache:
                        odhaczone_cache[z_id] = all(pt["stan"] in STANY_KONCOWE for pt in self._punkty_zlecen([z_id]).get(z_id, []))
                    odhaczone = odhaczone_cache[z_id]
                status = STATUS_KLASY.get(klasa) if klasa else None
                kolor, kolor_ramki = kolory_statusu(status) if status else (None, None)
                wpis = {
                    "id": p["id"], "skan_id": s["id"], "numer_plytki": s["numer_plytki"], "gniazdo": p["gniazdo"], "nr_fragmentu": p["nr_fragmentu"],
                    "status_fragmentu": p["status_fragmentu"], "status_match": p["status_match"], "pewnosc": p["pewnosc"],
                    "klasa": klasa, "status": status, "kolor": kolor, "kolor_ramki": kolor_ramki, "liczona": klasa in KLASY_LICZONE,
                    "projekt_id": pr, "sha16": info["sha16"] if info else None, "zlecenie_id": info["zlecenie_id"] if info else None,
                    "kuweta": kuweta, "zeby": info["zeby"] if info else None, "typ": info["typ"] if info else None,
                    "przypisanie": None if pr is None else ("decyzja" if d is not None else "auto"),
                    "decyzja": d["rodzaj"] if d else None, "decyzja_id": d["id"] if d else None, "operator": d["operator"] if d else None,
                    "czas_decyzji": d["czas"] if d else None, "kandydaci": kand, "konflikt": klasa == KLASA_KONFLIKT,
                    "domyka_dofrezowanie": klasa in KLASY_LICZONE and st is not None and st["stan"] == SE.STAN_DO_DOFREZOWANIA,
                    "zlecenie_odhaczone": odhaczone,
                    "kuweta_do_sprawdzenia": pr is not None and not (kuweta and WZOR_KUWETY_RAMKI.fullmatch(kuweta))}
                lista.append(wpis)
                if aktywny:
                    liczniki[klasa] = liczniki.get(klasa, 0) + 1
                    if klasa == KLASA_DWUZNACZNA:
                        nierozstrzygniete["dwuznaczne"] += 1
                    elif klasa == KLASA_NIEZNANA:
                        nierozstrzygniete["nieznane"] += 1
                    elif klasa in KLASY_LICZONE:
                        liczone[pr] = wpis
                    elif klasa == KLASA_POPRAWKA:
                        poprawki.append({"praca_id": p["id"], **{k: wpis[k] for k in (
                            "skan_id", "numer_plytki", "gniazdo", "projekt_id", "sha16", "zlecenie_id", "kuweta", "zeby", "zlecenie_odhaczone")}})
            dozwolone = numery_plytki(s["uklad"])
            wynik_skany.append({
                "id": s["id"], "sha16": s["sha16"], "numer_plytki": s["numer_plytki"], "numer_zrodlo": s["numer_zrodlo"], "uklad": s["uklad"],
                "status": s["status"], "aktywny": aktywny, "pominiety": s["id"] in pominiete, "czas_analizy": s["czas_analizy"],
                "zastepuje_id": s["zastepuje_id"], "na_ramce": na_ramce(s["uklad"]) and s["numer_plytki"] in (dozwolone or ()),
                "powod": SE.powod_nie_z_trybu(s["uklad"], s["tryb"]) if s["status"] == SE.STATUS_PLYTKA_NIE_Z_TRYBU else None, "prace": lista})

        # zlecenia dotkniete w tym piecu (praca liczona) - stan prowizoryczny do "Zamknij piec"
        punkty = self._punkty_zlecen([w["zlecenie_id"] for w in liczone.values()])
        wczesniej_pt = {pt["projekt_id"]: wczesniej(pt) for lst in punkty.values() for pt in lst}
        zlecenia = self._sortuj_zlecenia([self._zlecenie(z_id, lst, set(liczone), wczesniej_pt) for z_id, lst in punkty.items()])

        konflikty = []
        for pr in w_konflikcie:
            info = projekty.get(pr) or {}
            konflikty.append({"projekt_id": pr, "sha16": info.get("sha16"), "zlecenie_id": info.get("zlecenie_id"), "kuweta": info.get("kuweta"),
                              "zeby": info.get("zeby"), "miejsca": [{"skan_id": x["skan_id"], "numer_plytki": skan_po_id[x["skan_id"]]["numer_plytki"],
                                                                      "gniazdo": x["gniazdo"], "praca_id": x["id"]} for x in miejsca[pr]]})
        konflikty.sort(key=lambda k: (k["miejsca"][0]["skan_id"], k["miejsca"][0]["praca_id"]))
        # numer plytki blokuje tylko plytki ramki (kwadratowe poranne); okragle poranne (poza ramka) - ostrzezenie (r2 D7)
        kwadratowe = [s for s in aktywne if na_ramce(s["uklad"])]
        okragle = [s for s in aktywne if numery_plytki(s["uklad"]) is not None and not na_ramce(s["uklad"])]
        bez_numeru = [s["id"] for s in kwadratowe if s["numer_plytki"] is None]
        po_numerze: dict[int, list[int]] = {}
        for s in kwadratowe:
            if s["numer_plytki"] is not None:
                po_numerze.setdefault(s["numer_plytki"], []).append(s["id"])
        zdublowane = sorted(n for n, ids in po_numerze.items() if len(ids) > 1)
        wspolne = {n: (len(self._wspolne_prace(po_numerze[n])), [sum(1 for x in prace if x["skan_id"] == i) for i in po_numerze[n]])
                   for n in zdublowane}
        blokady, ostrzezenia = (self._blokady(skany, aktywne, pominiete, bez_numeru, po_numerze, zdublowane, konflikty, wspolne) if otwarty else ([], []))
        if otwarty:
            okragle_po_numerze: dict[tuple, list[int]] = {}
            for s in okragle:
                if s["numer_plytki"] is None:
                    ostrzezenia.append(f"skan {s['id']}: plytka okragla bez numeru - ramka jej nie pokazuje, rozloz prace wg ekranu")
                else:
                    okragle_po_numerze.setdefault((s["numer_plytki"], SE.rodzina_ukladu(s["uklad"])), []).append(s["id"])
            for (n, _), ids in okragle_po_numerze.items():
                if len(ids) > 1:
                    ostrzezenia.append(f"plytka okragla {n}: kilka skanow z tym samym numerem (skany {', '.join(map(str, ids))}) - jesli to "
                                       f"ponowny skan, potwierdz go; prace wszystkich licza sie")
        otwarte = self.otwarte_piece() if otwarty else []
        biezacy = any(p["id"] == pid and p["biezacy"] for p in otwarte)
        inne_otwarte = [p for p in otwarte if p["id"] != pid and not p["biezacy"]]
        for p in inne_otwarte:
            ostrzezenia.append(f"piec {p['plan_id']} (doba {p['data']}) nie zostal zamkniety - zamknij go ('Zamknij piec' z jego numerem); "
                               f"nowe skany ida do pieca biezacego")
        if otwarty and not biezacy:
            ostrzezenia.append(f"piec {plan_id(piec)} nie jest biezacy (otwarty od doby {piec['data']}, ostatni skan dawniej niz "
                               f"{OKNO_CIAGLOSCI_MIN} min) - nowe skany go nie dostaja; zamknij go wskazujac jego numer")
        return {
            "sesja_pieca_id": pid, "data": piec["data"], "nr_w_dniu": piec["nr_w_dniu"], "plan_id": plan_id(piec), "otwarto": piec["otwarto"],
            "zamknieto": piec["zamknieto"], "zamknal": piec["zamknal"], "otwarty": otwarty,
            "otwarty_z_poprzedniej_doby": otwarty and piec["data"] != self.sesja.doba(), "biezacy": biezacy,
            "skany": wynik_skany, "liczniki": liczniki, "nierozstrzygniete": nierozstrzygniete, "zlecenia": zlecenia,
            "kompletne": [z for z in zlecenia if z["kompletne"]], "braki": [z for z in zlecenia if not z["kompletne"]],
            "poprawki": sorted(poprawki, key=lambda x: (x["numer_plytki"] or 0, x["gniazdo"] or 0, x["praca_id"])), "konflikty": konflikty,
            "do_potwierdzenia": self._propozycje(pid) if otwarty else [], "bez_numeru": bez_numeru,
            "do_powtorzenia": [s["id"] for s in aktywne if s["status"] == SE.STATUS_DO_POWTORZENIA], "pominiete_skany": sorted(pominiete),
            "zdublowane_plytki": zdublowane, "blokady": blokady, "ostrzezenia": ostrzezenia,
            "inne_otwarte_piece": [p["plan_id"] for p in inne_otwarte]}

    @staticmethod
    def _blokady(skany: list[dict], aktywne: list[dict], pominiete: set, bez_numeru: list, po_numerze: dict, zdublowane: list,
                 konflikty: list, wspolne: dict) -> tuple[list[str], list[str]]:
        """Powody, dla ktorych "Zamknij piec" teraz odmowi (kazda plytka pieca musi sie liczyc), i ostrzezenia bez blokady."""
        blokady, ostrzezenia = [], []
        aktywne_ids = {s["id"] for s in aktywne}
        for s in skany:
            if s["id"] in pominiete or s["status"] == SE.STATUS_ZASTAPIONY:
                continue
            if s["id"] not in aktywne_ids:  # blad, niezgodny uklad, plytka nie z trybu - liczy sie dopiero ponowny skan tej plytki
                ponowny = s["numer_plytki"] is not None and any(t["id"] > s["id"] and t["numer_plytki"] == s["numer_plytki"] for t in aktywne)
                if not ponowny:
                    powod = {SE.STATUS_BLAD: "analiza skanu nie dala wyniku", SE.STATUS_NIEZGODNY_UKLAD: "uklad plytki niezgodny",
                             SE.STATUS_PLYTKA_NIE_Z_TRYBU: SE.powod_nie_z_trybu(s["uklad"], s["tryb"]) or "plytka nie z tego trybu"
                             }.get(s["status"], f"status {s['status']}")
                    blokady.append(f"skan {s['id']}: {powod} - zeskanuj plytke poranna ponownie (prace tej plytki inaczej sie nie licza), "
                                   f"a ten skan pomin")
                continue
            if s["status"] == SE.STATUS_DO_POWTORZENIA:
                blokady.append(f"skan {s['id']} (plytka {s['numer_plytki']}): skan do powtorzenia (dwie prace w gniezdzie, praca poza gniazdem "
                               f"albo drgniecie) - popraw ulozenie, zeskanuj plytke ponownie i potwierdz ponowny skan")
            dozwolone = numery_plytki(s["uklad"])
            if dozwolone is None:
                blokady.append(f"skan {s['id']}: plytka {s['uklad']!r} nie jest plytka poranna - ramka poranna jej nie obsluzy; przeloz prace "
                               f"na plytke poranna i zeskanuj ja, a ten skan pomin")
            elif not na_ramce(s["uklad"]):  # okragla poranna: numer nie blokuje (ramka jej nie pokazuje)
                if s["numer_plytki"] is not None:
                    zly = "" if s["numer_plytki"] in dozwolone else f" (numer spoza {', '.join(map(str, dozwolone))} - sprawdz)"
                    ostrzezenia.append(f"skan {s['id']}: plytka okragla nr {s['numer_plytki']}{zly} - ramka poranna jej nie pokazuje, "
                                       f"rozloz prace wg ekranu")
            elif s["numer_plytki"] is not None and s["numer_plytki"] not in dozwolone:
                blokady.append(f"skan {s['id']}: numer plytki {s['numer_plytki']} spoza plytek porannych tego ukladu "
                               f"({', '.join(map(str, dozwolone))}) - popraw numer")
        if bez_numeru:
            blokady.append(f"podaj numer plytki dla skanow {', '.join(map(str, bez_numeru))} (rano numer jest obowiazkowy przed "
                           f"'Zamknij piec' - Z3)")
        for n in zdublowane:
            ile, prac = wspolne[n]
            rada = ("to raczej rozne plytki - popraw numer jednej z nich" if ile == 0 else
                    "to ponowny skan tej plytki - potwierdz go" if ile >= max(prac) else "sprawdz prace obu skanow, potem potwierdz albo popraw numer")
            blokady.append(f"plytka {n}: dwa skany z tym samym numerem (skany {', '.join(map(str, po_numerze[n]))}; wspolnych prac: {ile}, "
                           f"prac w skanach: {', '.join(map(str, prac))}) - {rada}; do tego czasu ramka tej plytki nie dostaje")
        if konflikty:
            blokady.append(f"rozstrzygnij konflikty ({len(konflikty)}): ten sam projekt w kilku gniazdach - dla jednej z prac wybierz inny "
                           f"projekt albo 'bez projektu'")
        return blokady, ostrzezenia

    def stan_pieca(self, sesja_pieca_id: int | None = None) -> dict | None:
        """Stan sesji pieca jako zwykle dane (JSON) - kontrakt dla ekranu (A7). Domyslnie piec BIEZACY (``otwarty_piec``), a bez
        niego ostatni zamkniety w biezacej dobie roboczej; None, gdy zadnego. Piec niezamkniety od wczesniejszej doby - tylko
        z jawnym ``sesja_pieca_id`` (recenzja PR #23 r2, P1).

        Dla pieca zamknietego ``zlecenia`` / ``kompletne`` / ``braki`` / ``poprawki`` pochodza z zapisu "Zamknij piec"
        (``wynik_pieca``), a klasy prac sa liczone ze stanu bazy. Opis pol: ``opisy_modulow/session.md``, "Sesja poranna"."""
        if sesja_pieca_id is None:
            piec = self.otwarty_piec() or self._ostatni_zamkniety_w_dobie()
            if piec is None:
                return None
        else:
            piec = self._piec_po_id(sesja_pieca_id)
        stan = self._oblicz(piec)
        if piec["zamknieto"] is not None:
            rec = self.wynik_pieca(piec["id"]) or {}
            stan.update(kompletne=rec.get("kompletne", []), braki=rec.get("braki", []), poprawki=rec.get("poprawki", []),
                        zlecenia=self._sortuj_zlecenia(rec.get("kompletne", []) + rec.get("braki", [])))
        return stan

    # --- "Zamknij piec" i jego cofniecie --------------------------------------------------------
    def zamknij_piec(self, operator: str | None = None, *, plan_id: str | None = None, sesja_pieca_id: int | None = None) -> dict:
        """"Zamknij piec" (przycisk albo klawisz ramki): punkty prac liczonych -> ``rozpoznany`` (takze stary punkt ``do_dofrezowania``
        przed zmiana nazwy), brakujace punkty zlecen dotknietych -> ``brak_po_piecu`` (``do_dofrezowania`` zostaje), zapis wyniku
        i stanu sprzed zamkniecia w dzienniku, wpis ``poprawka_rano`` dla kazdej poprawki.

        ``plan_id`` (zdarzenie ``zamknij_piec`` ramki) albo ``sesja_pieca_id`` (piec pokazany w oknie): gdy nie wskazuja otwartego
        pieca - odmowa (spoznione zdarzenie nie zamyka nastepnego pieca). Odmowa (``BladSesji``, nic nie zapisane) takze: brak
        operatora, brak otwartego pieca, kazdy powod z ``stan_pieca()["blokady"]``. Dwuznaczne i nieznane nie blokuja - nie licza
        sie (``nierozstrzygniete``). Zwraca ``wynik_pieca``: ``kompletne`` (lista dla Excela), ``braki``, ``poprawki`` (tylko log),
        ``domkniete_dofrezowania``, ``nierozstrzygniete``, ``zamknal``."""
        osoba = self._osoba(operator)
        with self.baza.transakcja():
            otwarte = self.otwarte_piece()
            if plan_id is None and sesja_pieca_id is None:
                piec = next((p for p in reversed(otwarte) if p["biezacy"]), None)
                if piec is None:
                    stare = ", ".join(p["plan_id"] for p in otwarte)
                    raise SE.BladSesji("nie ma otwartego pieca biezacego - nie ma czego zamykac" + (
                        f" (niezamkniete piece z wczesniejszej doby: {stare} - zamknij je wskazujac numer pieca)" if stare else ""))
            else:
                piec = next((p for p in otwarte if (plan_id is None or p["plan_id"] == plan_id)
                             and (sesja_pieca_id is None or p["id"] == sesja_pieca_id)), None)
                if piec is None:
                    raise SE.BladSesji(f"'Zamknij piec' dotyczy pieca {plan_id or sesja_pieca_id}, ktory nie jest otwarty (otwarte: "
                                       f"{', '.join(p['plan_id'] for p in otwarte)}) - polecenie spoznione albo dla innego pieca, nic nie zamknieto")
            piec = {k: v for k, v in piec.items() if k not in ("z_poprzedniej_doby", "biezacy")}
            stan = self._oblicz(piec)
            if stan["blokady"]:
                raise SE.BladSesji("'Zamknij piec' niemozliwe: " + "; ".join(stan["blokady"]))
            teraz = self.sesja.teraz()
            liczone = [p for s in stan["skany"] for p in s["prace"] if p["liczona"] and s["aktywny"]]
            punkty_przed = []  # stan sprzed zamkniecia kazdego zmienionego wiersza - do otworz_piec_ponownie

            def ustaw(projekt_id: int, stan_: str, praca_id: int | None) -> None:
                punkty_przed.append({"projekt_id": projekt_id, "przed": self._wlasny_stan(projekt_id),
                                     "po": {"stan": stan_, "praca_id": praca_id, "sesja_pieca_id": piec["id"]}})
                self._ustaw_punkt(projekt_id, stan_, praca_id, piec["id"], teraz)

            domkniete = []
            info = self._projekty_id([p["projekt_id"] for p in liczone])
            poprzednicy = self._poprzednicy(info)
            for p in liczone:
                self._zapisz_przypisanie(p["id"], p["projekt_id"])  # nastepca po zmianie nazwy w trakcie pieca (r2 P3)
                if p["domyka_dofrezowanie"]:
                    domkniete.append({"praca_id": p["id"], **{k: p[k] for k in ("projekt_id", "sha16", "zlecenie_id", "kuweta", "zeby")}})
                ustaw(p["projekt_id"], STAN_ROZPOZNANY, p["id"])
                for q in poprzednicy.get(p["projekt_id"], []):  # stary punkt po zmianie nazwy: pozycja znika z listy "do dofrezowania"
                    if q["stan"] == SE.STAN_DO_DOFREZOWANIA:
                        ustaw(q["projekt_id"], STAN_ROZPOZNANY, p["id"])
            zlecenia = []
            for z in stan["zlecenia"]:
                brakujace = []
                for b in z["brakujace"]:
                    if b["stan"] == SE.STAN_OCZEKUJE:
                        ustaw(b["projekt_id"], STAN_BRAK_PO_PIECU, None)
                        b = {**b, "stan": STAN_BRAK_PO_PIECU}
                    brakujace.append(b)
                zlecenia.append({**z, "brakujace": brakujace})
            self.baza.wykonaj("UPDATE sesje_pieca SET zamknieto = ?, zamknal = ? WHERE id = ?", (teraz, osoba, piec["id"]))
            juz = {d.get("praca_id") for d in (json.loads(w["dane"]) for w in self.baza.wiersze(
                "SELECT dane FROM zdarzenia WHERE typ = ? AND skan_id IN (SELECT id FROM skany WHERE sesja_pieca_id = ?)", (TYP_POPRAWKA, piec["id"])))}
            for x in (x for x in stan["poprawki"] if x["praca_id"] not in juz):  # "tylko log", raz na prace (takze po ponownym otwarciu)
                self.baza.zdarzenie("system", TYP_POPRAWKA, {**x, "sesja_pieca_id": piec["id"]}, skan_id=x["skan_id"], czas=teraz)
            zapis = {
                "sesja_pieca_id": piec["id"], "data": piec["data"], "nr_w_dniu": piec["nr_w_dniu"], "plan_id": piec["plan_id"],
                "otwarto": piec["otwarto"], "zamknieto": teraz,
                "kompletne": [z for z in zlecenia if z["kompletne"]], "braki": [z for z in zlecenia if not z["kompletne"]],
                "poprawki": stan["poprawki"], "domkniete_dofrezowania": domkniete, "nierozstrzygniete": stan["nierozstrzygniete"],
                "pominiete_skany": stan["pominiete_skany"], "prac": sum(stan["liczniki"].values()), "liczone": len(liczone),
                "punkty_przed": punkty_przed}
            self.baza.zdarzenie("ui", TYP_ZAMKNIETY, zapis, czas=teraz)
            return self.wynik_pieca(piec["id"])

    def _zapis_zamkniecia(self, sesja_pieca_id: int) -> dict | None:
        for w in reversed(self.baza.wiersze("SELECT dane FROM zdarzenia WHERE typ = ? ORDER BY id", (TYP_ZAMKNIETY,))):
            dane = json.loads(w["dane"]) if w["dane"] else {}
            if dane.get("sesja_pieca_id") == sesja_pieca_id:
                return dane
        return None

    def wynik_pieca(self, sesja_pieca_id: int) -> dict | None:
        """Wynik ostatniego "Zamknij piec" tego pieca z dziennika + ``zamknal`` z ``sesje_pieca`` (None dla pieca otwartego albo
        niezamknietego) - lista dla Excela takze po restarcie."""
        piec = self.baza.wiersz("SELECT * FROM sesje_pieca WHERE id = ?", (sesja_pieca_id,))
        if piec is None or piec["zamknieto"] is None:
            return None
        zapis = self._zapis_zamkniecia(sesja_pieca_id)
        if zapis is None:
            return None
        return {**{k: v for k, v in zapis.items() if k != "punkty_przed"}, "zamknal": piec["zamknal"]}

    def otworz_piec_ponownie(self, sesja_pieca_id: int, operator: str | None = None) -> dict:
        """Cofa "Zamknij piec" OSTATNIEGO pieca (pomylka): przywraca stan punktow sprzed zamkniecia (poza punktami, ktore pozniej
        zmienil wieczor - te zostaja i sa wypisane w ``zmienione_pozniej``) i otwiera piec. Odmowa: inny piec otwarty, piec nie jest
        ostatni albo nie jest zamkniety. Decyzja ``otworz_piec_ponownie`` (operator) i wpis w dzienniku; cofniecie = ponowne
        "Zamknij piec". Uwaga dla A9: odhaczen juz zapisanych w Excelu program nie zdejmuje."""
        osoba = self._osoba(operator)
        with self.baza.transakcja():
            piec = self.baza.wiersz("SELECT * FROM sesje_pieca WHERE id = ?", (sesja_pieca_id,))
            if piec is None:
                raise SE.BladSesji(f"nie ma sesji pieca {sesja_pieca_id}")
            if piec["zamknieto"] is None:
                raise SE.BladSesji(f"piec {plan_id(piec)} jest otwarty - nie ma czego otwierac")
            otwarte = self.otwarte_piece()
            if otwarte:
                raise SE.BladSesji(f"otwarty jest piec {otwarte[-1]['plan_id']} - najpierw go zamknij")
            ostatni = self.baza.wiersz("SELECT max(id) AS id FROM sesje_pieca")["id"]
            if piec["id"] != ostatni:
                raise SE.BladSesji(f"otworzyc ponownie mozna tylko ostatni piec (piec {plan_id(piec)} nie jest ostatni)")
            zapis = self._zapis_zamkniecia(piec["id"]) or {}
            przywrocone, zmienione = 0, []
            for z in reversed(zapis.get("punkty_przed", [])):
                teraz_w = self._wlasny_stan(z["projekt_id"])
                po = z["po"]
                if teraz_w is not None and all(teraz_w[k] == po[k] for k in ("stan", "praca_id", "sesja_pieca_id")):
                    self._przywroc_punkt(z["projekt_id"], z["przed"])
                    przywrocone += 1
                else:
                    zmienione.append(z["projekt_id"])
            teraz = self.sesja.teraz()
            self.baza.wykonaj("UPDATE sesje_pieca SET zamknieto = NULL, zamknal = NULL WHERE id = ?", (piec["id"],))
            d = self.baza.wstaw("decyzje", rodzaj=RODZAJ_OTWORZ_PIEC, wartosc=str(piec["id"]), operator=osoba, czas=teraz)
            wynik = {"sesja_pieca_id": piec["id"], "plan_id": plan_id(piec), "decyzja_id": d, "przywrocone": przywrocone,
                     "zmienione_pozniej": sorted(zmienione)}
            self.baza.zdarzenie("ui", TYP_OTWARTY_PONOWNIE, wynik, czas=teraz)
        return wynik

    # --- lista brakow (trwala, miedzy piecami i dniami) i jej reczne zamkniecie --------------------
    def braki(self) -> list[dict]:
        """Lista brakow BIEZACA: zlecenia, ktorych co najmniej jeden punkt rozpoznal juz zamkniety piec, a co najmniej jeden
        nie jest rozpoznany ani zamkniety recznie. Brakujacy punkt ma ``stan``: ``do_dofrezowania`` (ukruszony wieczorem - nie
        szukac, jest dofrezowywany), ``brak_po_piecu`` (nie wyszedl z pieca), ``oczekuje`` (np. nowy plik w folderze). Uzupelnia
        sie sama, gdy brakujaca praca wyjdzie z kolejnego pieca. Kolejnosc wg numeru kuwety."""
        kandydaci = self.baza.wiersze(
            "SELECT DISTINCT p.zlecenie_id FROM projekty p WHERE p.usuniety = 0 AND (p.id IN (SELECT projekt_id FROM stan_punktow WHERE stan = ?) "
            "OR p.sha16 IN (SELECT q.sha16 FROM projekty q JOIN stan_punktow s ON s.projekt_id = q.id WHERE q.usuniety = 1 AND s.stan = ? "
            "AND q.sha16 IS NOT NULL))", (STAN_ROZPOZNANY, STAN_ROZPOZNANY))
        punkty = self._punkty_zlecen([w["zlecenie_id"] for w in kandydaci])
        wynik = []
        for z_id, lst in punkty.items():
            if not any(pt["stan"] == STAN_ROZPOZNANY for pt in lst):
                continue
            z = self._zlecenie(z_id, lst, set(), {pt["projekt_id"]: pt["stan"] in STANY_KONCOWE for pt in lst})
            if z["brakujace"]:
                z["ostatni_piec"] = max((pt["sesja_pieca_id"] or 0) for pt in lst if pt["stan"] == STAN_ROZPOZNANY)
                wynik.append(z)
        return self._sortuj_zlecenia(wynik)

    def zamknij_brak_recznie(self, projekt_id: int, operator: str | None = None, *, powod: str) -> int:
        """Reczne zamkniecie brakujacego punktu (plik, ktory nie jest praca, praca zaginiona albo wydana bez skanu): stan
        ``zamkniety_recznie`` (takze starego punktu ``do_dofrezowania`` po zmianie nazwy - znika z listy "do dofrezowania").
        ``powod`` - kod z ``POWODY_ZAMKNIECIA`` (bez tekstu wolnego). Decyzja ``zamkniecie_reczne`` (operator, stan sprzed w
        ``wartosc``) i wpis w dzienniku; cofa ``cofnij_zamkniecie_reczne``. Zlecenie, ktore stalo sie przez to kompletne, NIE
        idzie samo do Excela (do decyzji wlasciciela). Zwraca ``decyzje.id``."""
        osoba = self._osoba(operator)
        if powod not in POWODY_ZAMKNIECIA:
            raise SE.BladSesji(f"nieznany powod {powod!r} (znane: {', '.join(POWODY_ZAMKNIECIA)})")
        with self.baza.transakcja():
            info = self._projekty_id([projekt_id]) if isinstance(projekt_id, int) and not isinstance(projekt_id, bool) else {}
            p = info.get(projekt_id)
            if p is None or p["usuniety"]:
                raise SE.BladSesji(f"nie ma punktu {projekt_id} (projekt usuniety z indeksu albo nieznany)")
            st = self._stany(info).get(projekt_id)
            if st is not None and st["stan"] in STANY_KONCOWE:
                raise SE.BladSesji(f"punkt {projekt_id} jest juz zamkniety (stan {st['stan']!r}) - nie ma czego zamykac")
            dofrez = st is not None and st["stan"] == SE.STAN_DO_DOFREZOWANIA
            if dofrez != (powod == POWOD_DOFREZOWANIE):
                raise SE.BladSesji(f"punkt {projekt_id}: " + (
                    f"zab jest do dofrezowania (ukruszony wieczorem) - zamknac go mozna tylko powodem {POWOD_DOFREZOWANIE!r} "
                    f"(frezarka traci zadanie)" if dofrez else f"powod {POWOD_DOFREZOWANIE!r} dotyczy tylko zeba do dofrezowania"))
            zmiany = [{"projekt_id": projekt_id, "przed": self._wlasny_stan(projekt_id)}]
            zmiany += [{"projekt_id": q["projekt_id"], "przed": _wiersz_stanu(q)} for q in self._poprzednicy(info).get(projekt_id, [])
                       if q["stan"] == SE.STAN_DO_DOFREZOWANIA]
            teraz = self.sesja.teraz()
            d = self.baza.wstaw("decyzje", rodzaj=RODZAJ_ZAMKNIECIE_RECZNE, operator=osoba, czas=teraz,
                                wartosc=json.dumps({"projekt_id": projekt_id, "powod": powod, "zmiany": zmiany}, sort_keys=True))
            for z in zmiany:
                self._ustaw_punkt(z["projekt_id"], STAN_ZAMKNIETY_RECZNIE, None, None, teraz)
            kompletne = all(pt["stan"] in STANY_KONCOWE for pt in self._punkty_zlecen([p["zlecenie_id"]]).get(p["zlecenie_id"], []))
            self.baza.zdarzenie("ui", TYP_ZAMKNIETY_RECZNIE, {"decyzja_id": d, "projekt_id": projekt_id, "sha16": p["sha16"], "kuweta": p["kuweta"],
                                                              "zeby": p["zeby"], "powod": powod, "stan_przed": (st or {}).get("stan") or SE.STAN_OCZEKUJE,
                                                              "zlecenie_id": p["zlecenie_id"], "zlecenie_kompletne": kompletne}, czas=teraz)
        return d

    def cofnij_zamkniecie_reczne(self, projekt_id: int, operator: str | None = None) -> int:
        """Cofa ostatnie niecofniete ``zamkniecie_reczne`` punktu: przywraca stan sprzed (wiersz ``cofniecie``). Odmowa, gdy punkt
        zmienil potem stan (np. wieczorna "Ukruszona")."""
        osoba = self._osoba(operator)
        with self.baza.transakcja():
            wiersze = self.baza.wiersze("SELECT * FROM decyzje WHERE praca_id IS NULL AND skan_id IS NULL AND rodzaj IN (?, ?) ORDER BY id",
                                        (RODZAJ_ZAMKNIECIE_RECZNE, SE.RODZAJ_COFNIECIE))
            ob = [d for d in _obowiazujace(wiersze, (RODZAJ_ZAMKNIECIE_RECZNE,)) if json.loads(d["wartosc"]).get("projekt_id") == projekt_id]
            if not ob:
                raise SE.BladSesji(f"punkt {projekt_id}: nie ma recznego zamkniecia do cofniecia")
            dane = json.loads(ob[-1]["wartosc"])
            teraz_w = self._wlasny_stan(projekt_id)
            if teraz_w is None or teraz_w["stan"] != STAN_ZAMKNIETY_RECZNIE:
                raise SE.BladSesji(f"punkt {projekt_id} zmienil stan po recznym zamknieciu ({(teraz_w or {}).get('stan')!r}) - nie cofam")
            for z in dane["zmiany"]:
                w = self._wlasny_stan(z["projekt_id"])
                if w is not None and w["stan"] == STAN_ZAMKNIETY_RECZNIE:
                    self._przywroc_punkt(z["projekt_id"], z["przed"])
            teraz = self.sesja.teraz()
            d = self.baza.wstaw("decyzje", rodzaj=SE.RODZAJ_COFNIECIE, wartosc=str(ob[-1]["id"]), operator=osoba, czas=teraz)
            self.baza.zdarzenie("ui", TYP_ZAMKNIETY_RECZNIE + "_cofniete", {"decyzja_id": d, "projekt_id": projekt_id}, czas=teraz)
        return d

    # --- plan plytek dla ramki porannej (A8) ---------------------------------------------------
    def plan_plytek(self, sesja_pieca_id: int | None = None, kolejnosc: str = "liczba") -> dict:
        """Plan plytek pieca dla ramki porannej (kontrakt dla ``indicate``, A8): numer plytki -> gniazda (``id``, ``kolor``,
        ``kuweta`` tylko dla pracy rozpoznanej z kuweta zgodna z protokolem), lista kuwet w kolejnosci ``kolejnosc``
        ("liczba" - od najliczniejszej, "numer" - wg numeru), ``braki`` (kuwety zlecen niekompletnych tego pieca).

        Do planu idzie tylko plytka, ktora ramka przyjmie: aktywny, niepominiety skan kwadratowej plytki porannej o numerze 4-6,
        numer jedyny w piecu (dwa skany z tym samym numerem = ``pominiete.zdublowane_plytki``, plytka bez obrazu). Reszta trafia do
        ``pominiete`` (``bez_numeru``, ``zdublowane_plytki``, ``poza_ramka``, ``poza_gniazdem``). To NIE jest gotowa tresc
        ``PUT /plan``: ``indicate`` dodaje ``px`` z kalibracji (uklad z ``uklady``), ``protokol``, ``wersja``, ``start_id``,
        ``zdarzenia_do``, ``wazny_s``, ``potwierdzone``, ``wybrane`` i pomija pola pomocnicze."""
        if kolejnosc not in KOLEJNOSCI:
            raise SE.BladSesji(f"nieznana kolejnosc kuwet {kolejnosc!r} (znane: {', '.join(KOLEJNOSCI)})")
        biezacy = self.otwarty_piec()
        if biezacy is None:
            raise SE.BladSesji("nie ma otwartego pieca biezacego - planu ramki nie wysyla sie (indicate: DELETE /plan)")
        if sesja_pieca_id is not None and sesja_pieca_id != biezacy["id"]:
            raise SE.BladSesji(f"plan ramki tylko dla pieca biezacego ({biezacy['plan_id']}) - piec {sesja_pieca_id} jest zamkniety albo "
                               f"niezamkniety z wczesniejszej doby (jego plytki rozladowano wczesniej)")
        piec = biezacy
        stan = self.stan_pieca(piec["id"])
        po_numerze: dict[int, list[dict]] = {}
        bez_numeru, poza_ramka = [], []
        for s in stan["skany"]:
            if not s["aktywny"]:
                continue
            if s["numer_plytki"] is None:
                bez_numeru.append(s["id"])
            elif not s["na_ramce"]:
                poza_ramka.append(s["id"])
            else:
                po_numerze.setdefault(s["numer_plytki"], []).append(s)
        zdublowane = sorted(set(stan["zdublowane_plytki"]))
        kolor_dwie, kolor_sprawdz = kolory_statusu(STATUS_DWIE_PRACE)[1], kolory_statusu(STATUS_SPRAWDZ)[1]
        plytki, uklady, skany, liczba, na_plytkach, poza = {}, {}, {}, {}, {}, 0
        for n in sorted(po_numerze):
            if n in zdublowane or len(po_numerze[n]) > 1:
                continue
            s = po_numerze[n][0]
            gniazda: dict[int, list[dict]] = {}
            for p in s["prace"]:
                if p["gniazdo"] is None:
                    poza += 1
                else:
                    gniazda.setdefault(p["gniazdo"], []).append(p)
            lista = []
            for gid in sorted(gniazda):
                if len(gniazda[gid]) > 1:  # dwie prace w gniezdzie (skan do powtorzenia): bez kuwety
                    lista.append({"id": gid, "kolor": kolor_dwie})
                    continue
                p = gniazda[gid][0]
                g = {"id": gid, "kolor": p["kolor_ramki"]}
                if p["klasa"] in KLASY_Z_KUWETA:
                    if p["kuweta"] and WZOR_KUWETY_RAMKI.fullmatch(p["kuweta"]):
                        g["kuweta"] = p["kuweta"]
                        liczba[p["kuweta"]] = liczba.get(p["kuweta"], 0) + 1
                        na_plytkach.setdefault(p["kuweta"], set()).add(n)
                    else:  # kuweta niejednoznaczna albo pusta: ramka swieci "sprawdz", numer pokazuje ekran
                        g["kolor"] = kolor_sprawdz
                lista.append(g)
            plytki[str(n)] = {"gniazda": lista}
            uklady[str(n)] = s["uklad"]
            skany[str(n)] = s["id"]
        if kolejnosc == "liczba":
            porzadek = sorted(liczba, key=lambda k: (-liczba[k], _klucz_kuwety(k)))
        else:
            porzadek = sorted(liczba, key=_klucz_kuwety)
        braki = sorted({z["kuweta"] for z in stan["braki"] if z["kuweta"] and WZOR_KUWETY_RAMKI.fullmatch(z["kuweta"])}, key=_klucz_kuwety)
        return {"plan_id": plan_id(piec), "tryb": SE.TRYB_RANO, "sesja_pieca_id": piec["id"], "plytki": plytki,
                "kuwety": [{"kuweta": k, "plytki": sorted(na_plytkach[k])} for k in porzadek], "braki": braki[:MAX_BRAKOW_PLANU],
                "uklady": uklady, "skany": skany, "liczba_prac": {k: liczba[k] for k in porzadek},
                "pominiete": {"bez_numeru": bez_numeru, "poza_gniazdem": poza, "zdublowane_plytki": zdublowane, "poza_ramka": poza_ramka}}
