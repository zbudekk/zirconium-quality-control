"""session_rano - sesja poranna: sesja pieca, punkty zlecen, kompletnosc, braki, dofrezowania, poprawki (E3-A6).

Wejscie: wyniki analizy skanow plytek porannych (slownik z ``porownaj.porownaj`` + zdarzenie skanu - jak wieczorem),
decyzje osoby rozkladajacej piec (wybor kandydata, przypisanie reczne, cofniecie), "Zamknij piec". Wyjscie: wiersze w bazie
(``baza.py``, plan etapu 3 sekcja 3.4 - schemat bez zmian) i funkcje stanu dla ekranu porannego (A7), planu ramki (A8)
i Excela (A9): ``stan_pieca``, ``plan_plytek``, ``zamknij_piec`` / ``wynik_pieca``, ``braki``, ``piece``.

Modul nie rozszerza ``session.py`` (ten plik zmienia rownolegle paczka A1p) - korzysta z jego publicznego API: skan poranny
przyjmuje ``Sesja.przyjmij_wynik(..., tryb="rano")``, ponowny skan i numer plytki obsluguja ``Sesja.zastap_skan``,
``cofnij_zastapienie``, ``podaj_numer_plytki``, ``dopusc_plytke`` (tu tylko z kontrola, ze skan nalezy do otwartego pieca).
Caly stan jest w bazie - obiekt ``SesjaRano`` niczego nie pamieta, wiec po restarcie programu nowy obiekt na tym samym pliku
daje ten sam stan (takze otwarty piec).

Zasady (szczegoly, granice i decyzje do potwierdzenia: ``opisy_modulow/session.md``, sekcja "Sesja poranna"):
- sesja pieca = wiersz ``sesje_pieca``; otwiera ja sam pierwszy skan poranny po zamknieciu poprzedniej (albo ``otworz_piec``),
  zamyka "Zamknij piec"; naraz otwarta najwyzej jedna; skan poranny dostaje ``skany.sesja_pieca_id``;
- punkt zlecenia = wiersz ``projekty`` (plik STL w folderze zlecenia, ``usuniety = 0``); zlecenie kompletne = kazdy jego punkt
  rozpoznany (w tym albo w poprzednim piecu) albo zamkniety recznie;
- klasa pracy porannej: ``pewna`` (dopasowanie zielone) i ``przypisana`` (z decyzji) licza sie do kompletu; ``dwuznaczna``
  (kandydat z pokryciem >= ``prog_kandydata``, bez pewnosci) i ``nieznana`` czekaja na decyzje; ``poprawka`` = projekt, ktorego
  punkt zamknal juz poprzedni piec (np. zab dofrezowany do zlecenia juz odhaczonego - tylko log, Excel bez zmian);
  ``konflikt`` = ten sam projekt w dwoch gniazdach jednego pieca (blokuje "Zamknij piec" do rozstrzygniecia);
- ``stan_punktow`` zmienia dopiero "Zamknij piec": prace liczone -> ``rozpoznany`` (takze punkt ``do_dofrezowania`` - zab
  dofrezowany rozpoznany po tym samym STL; pozycja znika wtedy z listy "do dofrezowania"), brakujace punkty zlecen dotknietych
  w tym piecu -> ``brak_po_piecu`` (punkt ``do_dofrezowania`` zostaje, zeby lista wieczoru sie nie zmienila);
- wynik "Zamknij piec" (kompletne, braki, poprawki) zostaje w dzienniku (``zdarzenia``, typ ``piec_zamkniety``) i po
  restarcie daje go ``wynik_pieca`` - to lista dla Excela;
- decyzje sa tylko dopisywane i zawsze maja operatora z listy ``[sesja] operatorzy``;
- nazwy folderow i plikow zlecen nie sa nigdzie zapisywane ani zwracane: tylko ``sha16``, kuweta, zeby, id.

Modul korzysta tylko z biblioteki standardowej.
"""
from __future__ import annotations

import json
import re
from typing import Any

from . import baza as B
from . import session as SE

# klasy pracy porannej (tylko w wynikach funkcji, nie w bazie)
KLASA_PEWNA = "pewna"
KLASA_PRZYPISANA = "przypisana"
KLASA_DWUZNACZNA = "dwuznaczna"
KLASA_NIEZNANA = "nieznana"
KLASA_POPRAWKA = "poprawka"
KLASA_KONFLIKT = "konflikt"
KLASA_DO_POWTORZENIA = "do_powtorzenia"
KLASY_LICZONE = (KLASA_PEWNA, KLASA_PRZYPISANA)  # tylko takie prace domykaja punkty zlecen
# kolor na ekranie (A7; "bursztynowy" = statusy.KOLOR_BURSZTYNOWY, napis "zab dofrezowany" - Z9) i kolor diod ramki (A8)
KOLOR_KLASY = {KLASA_PEWNA: "zielony", KLASA_PRZYPISANA: "zielony", KLASA_DWUZNACZNA: "zolty", KLASA_NIEZNANA: "bialy",
               KLASA_POPRAWKA: "bursztynowy", KLASA_KONFLIKT: "czerwony", KLASA_DO_POWTORZENIA: "zolty"}
KOLOR_RAMKI = {KLASA_PEWNA: "zielony", KLASA_PRZYPISANA: "zielony", KLASA_DWUZNACZNA: "zolty", KLASA_NIEZNANA: "bialy",
               KLASA_POPRAWKA: "bursztyn", KLASA_KONFLIKT: "czerwony", KLASA_DO_POWTORZENIA: "zolty"}
KLASY_Z_KUWETA = (KLASA_PEWNA, KLASA_PRZYPISANA, KLASA_POPRAWKA)  # gniazdo planu ramki z numerem kuwety
KOLOR_RAMKI_SPRAWDZ = "czerwony"  # kuweta niejednoznaczna albo pusta, dwie prace w gniezdzie: ramka swieci "sprawdz"
KOLOR_RAMKI_DWIE_PRACE = "zolty"

# stany punktow (plan 3.4; ``oczekuje`` i ``do_dofrezowania`` ustawia session)
STAN_ROZPOZNANY = "rozpoznany"
STAN_BRAK_PO_PIECU = "brak_po_piecu"
STAN_ZAMKNIETY_RECZNIE = "zamkniety_recznie"
STANY_KONCOWE = (STAN_ROZPOZNANY, STAN_ZAMKNIETY_RECZNIE)

# rodzaje decyzji porannych (plan 3.4) - cofniecie jak wieczorem: wiersz ``cofniecie`` z id cofanej decyzji
RODZAJ_WYBOR = "wybor_kandydata"  # wartosc = sha16 wybranego kandydata (1. albo 2.)
RODZAJ_PRZYPISANIE = "przypisanie_reczne"  # wartosc = id projektu albo "" (praca bez projektu - nieznana)
BEZ_PROJEKTU = ""

PROG_KANDYDATA = 0.6  # = [match] prog_ostrzezenia_pokrycie z ustawienia.przyklad.toml (z_ustawien bierze wartosc z pliku)
KOLEJNOSCI = ("liczba", "numer")  # kuwety od najliczniejszej albo wg numeru (U7); numer wpisany recznie obsluguje ramka
WZOR_KUWETY_RAMKI = re.compile(r"#?[0-9]{1,6}")  # jak ramka/protokol.py WZOR_KUWETY - inna kuweta nie idzie do ramki
MAX_BRAKOW_PLANU = 100  # ramka/protokol.py MAX_BRAKOW

TYP_OTWARTY = "piec_otwarty"
TYP_ZAMKNIETY = "piec_zamkniety"
TYP_POPRAWKA = "poprawka_rano"


def _klucz_kuwety(kuweta: str | None) -> tuple:
    """Kolejnosc kuwet "wg numeru": zwykle numery rosnaco, potem prywatne "#", na koncu niejednoznaczne i puste."""
    m = re.fullmatch(r"(#?)(\d+)", kuweta or "")
    if m:
        return (1 if m[1] else 0, int(m[2]), kuweta)
    return (2, 0, str(kuweta or ""))


def _obowiazujaca(decyzje: list[dict]) -> dict | None:
    """Z decyzji jednej pracy (rosnaco po id): ostatnia niecofnieta ``wybor_kandydata`` / ``przypisanie_reczne``."""
    cofniete = {int(d["wartosc"]) for d in decyzje if d["rodzaj"] == SE.RODZAJ_COFNIECIE and str(d["wartosc"] or "").isdigit()}
    wynik = None
    for d in decyzje:
        if d["rodzaj"] in (RODZAJ_WYBOR, RODZAJ_PRZYPISANIE) and d["id"] not in cofniete:
            wynik = d
    return wynik


def _znaki(n: int) -> str:
    return ", ".join("?" * n)


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
        """Osoba do kolumny ``operator`` - te same reguly co wieczorem (lista wymagana; decyzja wlasciciela z 17.11.2026)."""
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

    def otwarty_piec(self) -> dict | None:
        """Otwarta sesja pieca (wiersz ``sesje_pieca`` + ``plan_id``) albo None."""
        w = self.baza.wiersz("SELECT * FROM sesje_pieca WHERE zamknieto IS NULL ORDER BY id DESC LIMIT 1")
        return self._piec(w) if w else None

    def otworz_piec(self) -> int:
        """Przycisk "Nowy piec": otwiera sesje pieca; odmowa, gdy inna jest otwarta. Zwykle niepotrzebny - otwiera ja pierwszy skan."""
        with self.baza.transakcja():
            return self._otworz("ui")

    def _otworz(self, zrodlo: str) -> int:
        otwarty = self.otwarty_piec()
        if otwarty is not None:
            raise SE.BladSesji(f"piec {otwarty['nr_w_dniu']} doby {otwarty['data']} jest otwarty - najpierw 'Zamknij piec'")
        teraz = self.sesja.teraz()
        data = self.sesja.doba(teraz)
        nr = self.baza.wiersz("SELECT count(*) AS n FROM sesje_pieca WHERE data = ?", (data,))["n"] + 1
        pid = self.baza.wstaw("sesje_pieca", data=data, nr_w_dniu=nr, otwarto=teraz)
        self.baza.zdarzenie(zrodlo, TYP_OTWARTY, {"sesja_pieca_id": pid, "data": data, "nr_w_dniu": nr}, czas=teraz)
        return pid

    def _piec_po_id(self, sesja_pieca_id: int | None) -> dict:
        if sesja_pieca_id is None:
            piec = self.otwarty_piec()
            if piec is None:
                raise SE.BladSesji("nie ma otwartego pieca (piec otwiera pierwszy skan poranny)")
            return piec
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
            raise SE.BladSesji(f"{co}: piec {w['nr_w_dniu']} doby {w['data']} jest zamkniety - jego prac i skanow nie da sie juz zmienic")
        return w

    def piece(self, data: str | None = None) -> list[dict]:
        """Sesje pieca doby roboczej ``data`` (domyslnie biezacej): wiersz ``sesje_pieca`` + ``plan_id``, ``otwarty``, ``skanow``."""
        data = data or self.sesja.doba()
        wiersze = self.baza.wiersze("SELECT sp.*, (SELECT count(*) FROM skany s WHERE s.sesja_pieca_id = sp.id) AS skanow "
                                    "FROM sesje_pieca sp WHERE sp.data = ? ORDER BY sp.id", (data,))
        return [{**self._piec(w), "otwarty": w["zamknieto"] is None} for w in wiersze]

    # --- przyjecie skanu ----------------------------------------------------------------------
    def przyjmij_wynik(self, zdarzenie: Any, wynik: dict) -> int:
        """Skan plytki porannej: ``Sesja.przyjmij_wynik(..., tryb="rano")`` + przypisanie do otwartego pieca (bez otwartego -
        nowy piec) + przypisanie obowiazujace prac (``prace.projekt_id``: projekt pracy pewnej, inne puste do decyzji).
        Zwraca ``skany.id``. Nie wymaga operatora."""
        with self.baza.transakcja():
            piec = self.otwarty_piec()
            pid = piec["id"] if piec is not None else self._otworz("system")
            skan_id = self.sesja.przyjmij_wynik(zdarzenie, wynik, tryb=SE.TRYB_RANO)
            self.baza.wykonaj("UPDATE skany SET sesja_pieca_id = ? WHERE id = ?", (pid, skan_id))
            for p in self.baza.wiersze("SELECT * FROM prace WHERE skan_id = ? ORDER BY id", (skan_id,)):
                self._zapisz_przypisanie(p["id"], self._przypisanie_auto(p))
        return skan_id

    def przyjmij_blad(self, zdarzenie: Any, blad: BaseException | str) -> int:
        """Analiza skanu porannego bez wyniku: ``Sesja.przyjmij_blad(..., tryb="rano")`` + przypisanie do pieca."""
        with self.baza.transakcja():
            piec = self.otwarty_piec()
            pid = piec["id"] if piec is not None else self._otworz("system")
            skan_id = self.sesja.przyjmij_blad(zdarzenie, blad, tryb=SE.TRYB_RANO)
            self.baza.wykonaj("UPDATE skany SET sesja_pieca_id = ? WHERE id = ?", (pid, skan_id))
        return skan_id

    # --- skany otwartego pieca: ponowny skan, numer plytki, plytka nie z trybu -----------------
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
        """Numer plytki wskazany recznie (Z3: rano obowiazkowy przed "Zamknij piec") - ``Sesja.podaj_numer_plytki``."""
        with self.baza.transakcja():
            self._skan_rano(skan_id)
            return self.sesja.podaj_numer_plytki(skan_id, numer, operator)

    def dopusc_plytke(self, skan_id: int, operator: str | None = None) -> int:
        """Swiadome dopuszczenie skanu plytki nie z trybu (wieczorna rano) - ``Sesja.dopusc_plytke``."""
        with self.baza.transakcja():
            self._skan_rano(skan_id)
            return self.sesja.dopusc_plytke(skan_id, operator)

    def cofnij_dopuszczenie(self, skan_id: int, operator: str | None = None) -> int:
        with self.baza.transakcja():
            self._skan_rano(skan_id)
            return self.sesja.cofnij_dopuszczenie(skan_id, operator)

    def _propozycje(self, sesja_pieca_id: int) -> list[dict]:
        """Propozycje "to ponowny skan tej plytki?": skan aktywny i wczesniejszy skan aktywny TEGO SAMEGO pieca z tym samym numerem
        plytki i rodzina ukladu (albo ta sama zawartosc pliku). W jednym piecu numer plytki sie nie powtarza (piec = 1-3 plytki),
        wiec okno czasu nie jest potrzebne. Pomijane sa pary, dla ktorych zastapienie juz cofnieto."""
        skany = self.baza.wiersze(f"SELECT * FROM skany WHERE sesja_pieca_id = ? AND status IN ({_znaki(len(SE.STATUSY_AKTYWNE))}) ORDER BY id",
                                  (sesja_pieca_id, *SE.STATUSY_AKTYWNE))
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
                    wynik.append({"skan_id": s["id"], "poprzedni_id": t["id"], "numer_plytki": s["numer_plytki"]})
                    break
        return wynik

    # --- decyzje o pracach porannych ------------------------------------------------------------
    def _praca_rano(self, praca_id: int | None) -> dict:
        """Praca, o ktorej wolno zdecydowac rano: skan poranny ``przyjety`` w otwartym piecu."""
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
                    SE.STATUS_PLYTKA_NIE_Z_TRYBU: "to plytka nie z tego trybu: zeskanuj wlasciwa plytke albo swiadomie dopusc ten skan",
                    }.get(p["status_skanu"], "skan nie zostal przyjety")
            raise SE.BladSesji(f"praca {praca_id}: skan {p['skan_id']} ma status {p['status_skanu']!r} - decyzje mozna podejmowac tylko na skanie "
                               f"przyjetym ({rada})")
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

    def cofnij_przypisanie(self, praca_id: int, operator: str | None = None) -> int:
        """Cofa obowiazujaca decyzje przypisania (wraca poprzednia albo przypisanie automatyczne); dopisuje wiersz ``cofniecie``."""
        osoba = self._osoba(operator)
        with self.baza.transakcja():
            p = self._praca_rano(praca_id)
            ob = self._decyzja_przypisania(p["id"])
            if ob is None:
                raise SE.BladSesji(f"praca {praca_id}: nie ma decyzji do cofniecia")
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

    # --- pomocnicze zapytania -------------------------------------------------------------------
    def _wiersze_in(self, sql: str, wartosci: list, porcja: int = 500) -> list[dict]:
        """Zapytanie z lista wartosci w miejscu ``{}``, w porcjach; pusta lista = brak wierszy."""
        wynik: list[dict] = []
        for i in range(0, len(wartosci), porcja):
            czesc = wartosci[i:i + porcja]
            wynik += self.baza.wiersze(sql.format(_znaki(len(czesc))), tuple(czesc))
        return wynik

    _POLA_PROJEKTU = ("SELECT p.id AS projekt_id, p.sha16, p.zlecenie_id, p.zeby, p.typ, z.kuweta, z.zrodlo "
                      "FROM projekty p JOIN zlecenia z ON z.id = p.zlecenie_id WHERE p.usuniety = 0 AND ")

    def _projekty_sha(self, shas: list) -> dict[str, list[dict]]:
        """``sha16`` -> projekty (punkty) o tej zawartosci; bez nazw folderow i plikow."""
        wynik: dict[str, list[dict]] = {}
        for w in self._wiersze_in(self._POLA_PROJEKTU + "p.sha16 IN ({}) ORDER BY p.id", sorted({s for s in shas if s})):
            wynik.setdefault(w["sha16"], []).append(w)
        return wynik

    def _projekty_id(self, ids: list) -> dict[int, dict]:
        return {w["projekt_id"]: w for w in self._wiersze_in(self._POLA_PROJEKTU.replace("p.usuniety = 0 AND ", "") + "p.id IN ({})",
                                                              sorted({i for i in ids if i is not None}))}

    def _punkty_zlecen(self, zlecenia: list) -> dict[int, list[dict]]:
        """Zlecenie -> jego punkty (projekty ``usuniety = 0``) ze stanem punktu (brak wiersza = ``oczekuje``)."""
        wynik: dict[int, list[dict]] = {}
        for w in self._wiersze_in(
                "SELECT p.zlecenie_id, z.kuweta, z.zrodlo, p.id AS projekt_id, p.sha16, p.zeby, p.typ, sp.stan, sp.sesja_pieca_id "
                "FROM projekty p JOIN zlecenia z ON z.id = p.zlecenie_id LEFT JOIN stan_punktow sp ON sp.projekt_id = p.id "
                "WHERE p.usuniety = 0 AND p.zlecenie_id IN ({}) ORDER BY p.zlecenie_id, p.id", sorted({z for z in zlecenia if z is not None})):
            wynik.setdefault(w["zlecenie_id"], []).append(w)
        return wynik

    def _ustaw_punkt(self, projekt_id: int, stan: str, praca_id: int | None, sesja_pieca_id: int, czas: str) -> None:
        self.baza.wykonaj(
            """INSERT INTO stan_punktow (projekt_id, stan, praca_id, sesja_pieca_id, czas) VALUES (?, ?, ?, ?, ?)
               ON CONFLICT (projekt_id) DO UPDATE SET stan = excluded.stan, praca_id = excluded.praca_id,
               sesja_pieca_id = excluded.sesja_pieca_id, czas = excluded.czas""", (projekt_id, stan, praca_id, sesja_pieca_id, czas))

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
        prace = self._wiersze_in("SELECT * FROM prace WHERE skan_id IN ({}) ORDER BY skan_id, id", [s["id"] for s in skany])
        decyzje: dict[int, list[dict]] = {}
        for d in self._wiersze_in(f"SELECT * FROM decyzje WHERE rodzaj IN ('{RODZAJ_WYBOR}', '{RODZAJ_PRZYPISANIE}', '{SE.RODZAJ_COFNIECIE}') "
                                  f"AND praca_id IN ({{}}) ORDER BY id", [p["id"] for p in prace]):
            decyzje.setdefault(d["praca_id"], []).append(d)
        obow = {pid_: _obowiazujaca(lst) for pid_, lst in decyzje.items()}
        po_sha = self._projekty_sha([p["kandydat1_sha16"] for p in prace] + [p["kandydat2_sha16"] for p in prace])
        projekty = self._projekty_id([p["projekt_id"] for p in prace])
        stany = {w["projekt_id"]: w for w in self._wiersze_in("SELECT * FROM stan_punktow WHERE projekt_id IN ({})", sorted(projekty))}
        skan_po_id = {s["id"]: s for s in skany}

        def wczesniej(projekt_id: int) -> bool:  # punkt zamknal juz wczesniejszy piec
            st = stany.get(projekt_id)
            return st is not None and st["stan"] in STANY_KONCOWE and (st["sesja_pieca_id"] is None or st["sesja_pieca_id"] < pid)

        # SE8: ten sam projekt w dwoch gniazdach skanow przyjetych tego pieca (dwa fragmenty w jednym gniezdzie = jedno miejsce)
        miejsca: dict[int, list[dict]] = {}
        for p in prace:
            if p["projekt_id"] is not None and skan_po_id[p["skan_id"]]["status"] == SE.STATUS_PRZYJETY:
                miejsca.setdefault(p["projekt_id"], []).append(p)
        w_konflikcie = {pr for pr, lst in miejsca.items()
                        if len({(x["skan_id"], x["gniazdo"] if x["gniazdo"] is not None else f"poza-{x['id']}") for x in lst}) > 1}

        def kandydaci(p: dict) -> list[dict]:
            return [{"sha16": p[f"kandydat{i}_sha16"], "pokrycie": p[f"kandydat{i}_pokrycie"],
                     "projekty": [{k: q[k] for k in ("projekt_id", "zlecenie_id", "kuweta", "zeby", "typ", "zrodlo")}
                                  for q in po_sha.get(p[f"kandydat{i}_sha16"], [])]}
                    for i in (1, 2) if p[f"kandydat{i}_sha16"]]

        wynik_skany, liczniki, nierozstrzygniete, liczone = [], {}, {"dwuznaczne": 0, "nieznane": 0}, {}
        poprawki = []
        odhaczone_cache: dict[int, bool] = {}
        for s in skany:
            aktywny = s["status"] in SE.STATUSY_AKTYWNE
            lista = []
            for p in (x for x in prace if x["skan_id"] == s["id"]):
                d = obow.get(p["id"])
                kand = kandydaci(p)
                pr = p["projekt_id"]
                if not aktywny:
                    klasa = None
                elif s["status"] == SE.STATUS_DO_POWTORZENIA:
                    klasa = KLASA_DO_POWTORZENIA
                elif pr is None:
                    dwuznaczna = (d is None and (p["kandydat1_pokrycie"] or 0.0) >= self.prog_kandydata and any(k["projekty"] for k in kand))
                    klasa = KLASA_DWUZNACZNA if dwuznaczna else KLASA_NIEZNANA
                elif pr in w_konflikcie:
                    klasa = KLASA_KONFLIKT
                elif wczesniej(pr):
                    klasa = KLASA_POPRAWKA
                else:
                    klasa = KLASA_PRZYPISANA if d is not None else KLASA_PEWNA
                info = projekty.get(pr) if pr is not None else None
                kuweta = info["kuweta"] if info else None
                st = stany.get(pr) if pr is not None else None
                odhaczone = False
                if klasa == KLASA_POPRAWKA:
                    z_id = info["zlecenie_id"]
                    if z_id not in odhaczone_cache:
                        odhaczone_cache[z_id] = all(pt["stan"] in STANY_KONCOWE for pt in self._punkty_zlecen([z_id]).get(z_id, []))
                    odhaczone = odhaczone_cache[z_id]
                wpis = {
                    "id": p["id"], "skan_id": s["id"], "numer_plytki": s["numer_plytki"], "gniazdo": p["gniazdo"], "nr_fragmentu": p["nr_fragmentu"],
                    "status_fragmentu": p["status_fragmentu"], "status_match": p["status_match"], "pewnosc": p["pewnosc"],
                    "klasa": klasa, "kolor": KOLOR_KLASY.get(klasa), "kolor_ramki": KOLOR_RAMKI.get(klasa), "liczona": klasa in KLASY_LICZONE,
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
                        poprawki.append({k: wpis[k] for k in ("id", "skan_id", "numer_plytki", "gniazdo", "projekt_id", "sha16", "zlecenie_id",
                                                              "kuweta", "zeby", "zlecenie_odhaczone")})
            wynik_skany.append({
                "id": s["id"], "sha16": s["sha16"], "numer_plytki": s["numer_plytki"], "numer_zrodlo": s["numer_zrodlo"], "uklad": s["uklad"],
                "status": s["status"], "aktywny": aktywny, "czas_analizy": s["czas_analizy"], "zastepuje_id": s["zastepuje_id"],
                "powod": SE.powod_nie_z_trybu(s["uklad"], s["tryb"]) if s["status"] == SE.STATUS_PLYTKA_NIE_Z_TRYBU else None, "prace": lista})
        for x in poprawki:
            x["praca_id"] = x.pop("id")

        # zlecenia dotkniete w tym piecu (praca liczona) - stan prowizoryczny do "Zamknij piec"
        punkty = self._punkty_zlecen([w["zlecenie_id"] for w in liczone.values()])
        teraz_ids = set(liczone)
        wczesniej_pt = {pt["projekt_id"]: pt["stan"] in STANY_KONCOWE and (pt["sesja_pieca_id"] is None or pt["sesja_pieca_id"] < pid)
                        for lst in punkty.values() for pt in lst}
        zlecenia = self._sortuj_zlecenia([self._zlecenie(z_id, lst, teraz_ids, wczesniej_pt) for z_id, lst in punkty.items()])

        konflikty = []
        for pr in w_konflikcie:
            info = projekty.get(pr) or {}
            konflikty.append({"projekt_id": pr, "sha16": info.get("sha16"), "zlecenie_id": info.get("zlecenie_id"), "kuweta": info.get("kuweta"),
                              "zeby": info.get("zeby"), "miejsca": [{"skan_id": x["skan_id"], "numer_plytki": skan_po_id[x["skan_id"]]["numer_plytki"],
                                                                      "gniazdo": x["gniazdo"], "praca_id": x["id"]} for x in miejsca[pr]]})
        konflikty.sort(key=lambda k: (k["miejsca"][0]["skan_id"], k["miejsca"][0]["praca_id"]))
        aktywne = [s for s in skany if s["status"] in SE.STATUSY_AKTYWNE]
        bez_numeru = [s["id"] for s in aktywne if s["numer_plytki"] is None]
        numery: dict[int, int] = {}
        for s in aktywne:
            if s["numer_plytki"] is not None:
                numery[s["numer_plytki"]] = numery.get(s["numer_plytki"], 0) + 1
        blokady = []
        if otwarty and bez_numeru:
            blokady.append(f"podaj numer plytki dla skanow {', '.join(map(str, bez_numeru))} (rano numer jest obowiazkowy przed 'Zamknij piec' - Z3)")
        if otwarty and konflikty:
            blokady.append(f"rozstrzygnij konflikty ({len(konflikty)}): ten sam projekt w kilku gniazdach - dla jednej z prac wybierz inny "
                           f"projekt albo 'bez projektu'")
        return {
            "sesja_pieca_id": pid, "data": piec["data"], "nr_w_dniu": piec["nr_w_dniu"], "plan_id": plan_id(piec), "otwarto": piec["otwarto"],
            "zamknieto": piec["zamknieto"], "zamknal": piec["zamknal"], "otwarty": otwarty,
            "otwarty_z_poprzedniej_doby": otwarty and piec["data"] != self.sesja.doba(),
            "skany": wynik_skany, "liczniki": liczniki, "nierozstrzygniete": nierozstrzygniete, "zlecenia": zlecenia,
            "kompletne": [z for z in zlecenia if z["kompletne"]], "braki": [z for z in zlecenia if not z["kompletne"]],
            "poprawki": sorted(poprawki, key=lambda x: (x["numer_plytki"] or 0, x["gniazdo"] or 0, x["praca_id"])), "konflikty": konflikty,
            "do_potwierdzenia": self._propozycje(pid) if otwarty else [], "bez_numeru": bez_numeru,
            "do_powtorzenia": [s["id"] for s in aktywne if s["status"] == SE.STATUS_DO_POWTORZENIA],
            "zdublowane_plytki": sorted(n for n, ile in numery.items() if ile > 1), "blokady": blokady}

    def stan_pieca(self, sesja_pieca_id: int | None = None) -> dict | None:
        """Stan sesji pieca (domyslnie otwartej; None, gdy zadna nie jest otwarta) jako zwykle dane (JSON) - kontrakt dla ekranu (A7).

        Dla pieca zamknietego ``zlecenia`` / ``kompletne`` / ``braki`` / ``poprawki`` pochodza z zapisu "Zamknij piec"
        (``wynik_pieca``), a klasy prac sa liczone ze stanu bazy. Opis pol: ``opisy_modulow/session.md``, "Sesja poranna"."""
        if sesja_pieca_id is None and self.otwarty_piec() is None:
            return None
        piec = self._piec_po_id(sesja_pieca_id)
        stan = self._oblicz(piec)
        if piec["zamknieto"] is not None:
            rec = self.wynik_pieca(piec["id"]) or {}
            stan.update(kompletne=rec.get("kompletne", []), braki=rec.get("braki", []), poprawki=rec.get("poprawki", []),
                        zlecenia=self._sortuj_zlecenia(rec.get("kompletne", []) + rec.get("braki", [])))
        return stan

    # --- "Zamknij piec" -------------------------------------------------------------------------
    def zamknij_piec(self, operator: str | None = None) -> dict:
        """"Zamknij piec" (przycisk albo klawisz ramki): punkty prac liczonych -> ``rozpoznany``, brakujace punkty zlecen dotknietych
        -> ``brak_po_piecu`` (``do_dofrezowania`` zostaje), zapis wyniku w dzienniku, wpis ``poprawka_rano`` dla kazdej poprawki.

        Odmowa (``BladSesji``, nic nie zapisane): brak operatora, brak otwartego pieca, skan aktywny bez numeru plytki (Z3),
        nierozstrzygniety konflikt. Dwuznaczne i nieznane nie blokuja - nie licza sie (``nierozstrzygniete``).
        Zwraca ``wynik_pieca`` (to samo da po restarcie): ``kompletne`` (lista dla Excela), ``braki``, ``poprawki`` (tylko log),
        ``domkniete_dofrezowania``, ``nierozstrzygniete``."""
        osoba = self._osoba(operator)
        with self.baza.transakcja():
            piec = self.otwarty_piec()
            if piec is None:
                raise SE.BladSesji("nie ma otwartego pieca - nie ma czego zamykac (piec otwiera pierwszy skan poranny)")
            stan = self._oblicz(piec)
            if stan["blokady"]:
                raise SE.BladSesji("'Zamknij piec' niemozliwe: " + "; ".join(stan["blokady"]))
            teraz = self.sesja.teraz()
            liczone = [p for s in stan["skany"] for p in s["prace"] if p["liczona"] and s["aktywny"]]
            domkniete = [{k: p[k] for k in ("projekt_id", "sha16", "zlecenie_id", "kuweta", "zeby")} | {"praca_id": p["id"]}
                         for p in liczone if p["domyka_dofrezowanie"]]
            for p in liczone:
                self._ustaw_punkt(p["projekt_id"], STAN_ROZPOZNANY, p["id"], piec["id"], teraz)
            zlecenia = []
            for z in stan["zlecenia"]:
                brakujace = []
                for b in z["brakujace"]:
                    if b["stan"] == SE.STAN_OCZEKUJE:
                        self._ustaw_punkt(b["projekt_id"], STAN_BRAK_PO_PIECU, None, piec["id"], teraz)
                        b = {**b, "stan": STAN_BRAK_PO_PIECU}
                    brakujace.append(b)
                zlecenia.append({**z, "brakujace": brakujace})
            self.baza.wykonaj("UPDATE sesje_pieca SET zamknieto = ?, zamknal = ? WHERE id = ?", (teraz, osoba, piec["id"]))
            for x in stan["poprawki"]:  # "tylko log": Excel bez zmian, punkt bez zmian
                self.baza.zdarzenie("system", TYP_POPRAWKA, {**x, "sesja_pieca_id": piec["id"]}, skan_id=x["skan_id"], czas=teraz)
            wynik = {
                "sesja_pieca_id": piec["id"], "data": piec["data"], "nr_w_dniu": piec["nr_w_dniu"], "plan_id": plan_id(piec),
                "otwarto": piec["otwarto"], "zamknieto": teraz, "zamknal": osoba,
                "kompletne": [z for z in zlecenia if z["kompletne"]], "braki": [z for z in zlecenia if not z["kompletne"]],
                "poprawki": stan["poprawki"], "domkniete_dofrezowania": domkniete, "nierozstrzygniete": stan["nierozstrzygniete"],
                "prac": sum(stan["liczniki"].values()), "liczone": len(liczone)}
            self.baza.zdarzenie("ui", TYP_ZAMKNIETY, wynik, czas=teraz)
            return self.wynik_pieca(piec["id"])

    def wynik_pieca(self, sesja_pieca_id: int) -> dict | None:
        """Wynik "Zamknij piec" zapisany w dzienniku (None dla pieca niezamknietego) - lista dla Excela takze po restarcie."""
        for w in reversed(self.baza.wiersze("SELECT dane FROM zdarzenia WHERE typ = ? ORDER BY id", (TYP_ZAMKNIETY,))):
            dane = json.loads(w["dane"]) if w["dane"] else {}
            if dane.get("sesja_pieca_id") == sesja_pieca_id:
                return dane
        return None

    # --- lista brakow (trwala, miedzy piecami i dniami) ----------------------------------------
    def braki(self) -> list[dict]:
        """Lista brakow BIEZACA: zlecenia, ktorych co najmniej jeden punkt rozpoznal juz zamkniety piec, a co najmniej jeden
        nie jest rozpoznany. Brakujacy punkt ma ``stan``: ``do_dofrezowania`` (ukruszony wieczorem - nie szukac, jest
        dofrezowywany), ``brak_po_piecu`` (nie wyszedl z pieca), ``oczekuje`` (np. nowy plik w folderze). Uzupelnia sie sama,
        gdy brakujaca praca wyjdzie z kolejnego pieca. Kolejnosc wg numeru kuwety."""
        rozp = self.baza.wiersze("SELECT DISTINCT p.zlecenie_id FROM stan_punktow sp JOIN projekty p ON p.id = sp.projekt_id "
                                 "WHERE sp.stan = ? AND p.usuniety = 0", (STAN_ROZPOZNANY,))
        punkty = self._punkty_zlecen([w["zlecenie_id"] for w in rozp])
        wynik = []
        for z_id, lst in punkty.items():
            z = self._zlecenie(z_id, lst, set(), {pt["projekt_id"]: pt["stan"] in STANY_KONCOWE for pt in lst})
            if z["brakujace"]:
                z["ostatni_piec"] = max((pt["sesja_pieca_id"] or 0) for pt in lst if pt["stan"] == STAN_ROZPOZNANY)
                wynik.append(z)
        return self._sortuj_zlecenia(wynik)

    # --- plan plytek dla ramki porannej (A8) ---------------------------------------------------
    def plan_plytek(self, sesja_pieca_id: int | None = None, kolejnosc: str = "liczba") -> dict:
        """Plan plytek pieca dla ramki porannej (kontrakt dla ``indicate``, A8): numer plytki -> gniazda (``id``, ``kolor``,
        ``kuweta`` tylko dla pracy rozpoznanej z kuweta zgodna z protokolem), lista kuwet w kolejnosci ``kolejnosc``
        ("liczba" - od najliczniejszej, "numer" - wg numeru), ``braki`` (kuwety zlecen niekompletnych tego pieca).

        To NIE jest gotowa tresc ``PUT /plan``: ``indicate`` dodaje ``px`` z kalibracji (``ramka.kalibracja.gniazda_planu`` z ukladem
        z ``uklady``), ``protokol``, ``wersja``, ``start_id``, ``zdarzenia_do``, ``wazny_s``, ``potwierdzone``, ``wybrane`` i pomija
        pola pomocnicze (``sesja_pieca_id``, ``uklady``, ``skany``, ``liczba_prac``, ``pominiete``). Plytka = najnowszy aktywny skan
        o danym numerze; skan bez numeru, praca poza gniazdem i skany nieaktywne nie ida do planu (``pominiete``)."""
        if kolejnosc not in KOLEJNOSCI:
            raise SE.BladSesji(f"nieznana kolejnosc kuwet {kolejnosc!r} (znane: {', '.join(KOLEJNOSCI)})")
        piec = self._piec_po_id(sesja_pieca_id)
        stan = self.stan_pieca(piec["id"])
        po_numerze: dict[int, list[dict]] = {}
        bez_numeru = []
        for s in stan["skany"]:
            if not s["aktywny"]:
                continue
            if s["numer_plytki"] is None:
                bez_numeru.append(s["id"])
            else:
                po_numerze.setdefault(s["numer_plytki"], []).append(s)
        plytki, uklady, skany, liczba, na_plytkach, poza = {}, {}, {}, {}, {}, 0
        for n in sorted(po_numerze):
            s = max(po_numerze[n], key=lambda x: x["id"])
            gniazda: dict[int, list[dict]] = {}
            for p in s["prace"]:
                if p["gniazdo"] is None:
                    poza += 1
                else:
                    gniazda.setdefault(p["gniazdo"], []).append(p)
            lista = []
            for gid in sorted(gniazda):
                if len(gniazda[gid]) > 1:  # dwie prace w gniezdzie (skan do powtorzenia): bez kuwety
                    lista.append({"id": gid, "kolor": KOLOR_RAMKI_DWIE_PRACE})
                    continue
                p = gniazda[gid][0]
                g = {"id": gid, "kolor": p["kolor_ramki"]}
                if p["klasa"] in KLASY_Z_KUWETA:
                    if p["kuweta"] and WZOR_KUWETY_RAMKI.fullmatch(p["kuweta"]):
                        g["kuweta"] = p["kuweta"]
                        liczba[p["kuweta"]] = liczba.get(p["kuweta"], 0) + 1
                        na_plytkach.setdefault(p["kuweta"], set()).add(n)
                    else:  # kuweta niejednoznaczna albo pusta: ramka swieci "sprawdz", numer pokazuje ekran
                        g["kolor"] = KOLOR_RAMKI_SPRAWDZ
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
                "pominiete": {"bez_numeru": bez_numeru, "poza_gniazdem": poza, "zdublowane_plytki": stan["zdublowane_plytki"]}}
