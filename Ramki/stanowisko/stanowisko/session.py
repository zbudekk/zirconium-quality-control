"""session - stan wieczoru: skany, prace, decyzje technika, ponowny skan, lista "do dofrezowania" (E3-A1).

Wejscie: wynik analizy jednego skanu (slownik z ``porownaj.porownaj``, ten sam co w ``<skan>_wynik.json``) razem ze
zdarzeniem skanu (plik, ``sha16``, rozmiar, czas pliku) oraz decyzje technika. Wyjscie: wiersze w bazie (``baza.py``,
plan etapu 3 sekcja 3.4) i funkcje stanu dla okna: ``stan_wieczoru``, ``do_dofrezowania``, ``konflikty``.

Caly stan jest w bazie - obiekt ``Sesja`` pamieta tylko wybrana osobe (operatora) i ustawienia, wiec po restarcie
programu nowa ``Sesja`` na tym samym pliku daje ten sam stan. Poranek (sesja pieca, punkty zlecen, braki) dojdzie
w paczce A6.

Zasady (zalozenia Z3, Z4 i decyzja DW3 planu; szczegoly i granice: ``opisy_modulow/session.md``):
- wieczor = data z czasu pliku skanu (``skany.czas_pliku``; gdy go brak - z czasu analizy), tryb ``wieczor``;
- skan ma status ``przyjety``, ``do_powtorzenia`` (drgniecie, dwie prace w gniezdzie, praca poza gniazdem - zadna praca
  takiego skanu nie liczy sie jako zielona), ``niezgodny_uklad`` (bez prac), ``zastapiony`` albo ``blad``;
- ponowny skan plytki o tym samym numerze tego samego wieczoru zastepuje poprzedni dopiero po potwierdzeniu
  (``zastap_skan``); decyzje skanu zastapionego zostaja w bazie, ale nie licza sie do list i nie przechodza na nowy;
- decyzje sa tylko dopisywane; cofniecie to kolejny wiersz (``rodzaj`` = ``cofniecie``, ``wartosc`` = id cofanej decyzji);
- nazwy folderow i plikow zlecen nie sa nigdzie zapisywane ani zwracane: tylko ``sha16``, numer kuwety, zeby, krazek.

Modul korzysta tylko z biblioteki standardowej.
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import re
from collections.abc import Mapping
from pathlib import Path, PureWindowsPath
from typing import Any, Callable

from . import baza as B

TRYB_WIECZOR = "wieczor"
TRYB_RANO = "rano"

STATUS_PRZYJETY = "przyjety"
STATUS_DO_POWTORZENIA = "do_powtorzenia"
STATUS_ZASTAPIONY = "zastapiony"
STATUS_NIEZGODNY_UKLAD = "niezgodny_uklad"
STATUS_BLAD = "blad"
STATUSY_AKTYWNE = (STATUS_PRZYJETY, STATUS_DO_POWTORZENIA)  # skany, ktorych prace licza sie do stanu i list

# statusy inspect, przy ktorych plytke trzeba zeskanowac ponownie (plan: SE7)
INSPEKCJA_DO_POWTORZENIA = ("skan_ponownie", "popraw_ulozenie")
FRAGMENTY_DO_POWTORZENIA = ("podwojny", "poza_gniazdem")

DECYZJE_UKRUSZENIA = ("ukruszona", "ukruszona_niewykryta")  # praca idzie na liste "do dofrezowania"
DECYZJE_O_PRACY = DECYZJE_UKRUSZENIA + ("ok",)
RODZAJ_COFNIECIE = "cofniecie"  # nie ma go na liscie rodzajow w sekcji 3.4 - patrz raport E3-A1, "do decyzji wlasciciela"
RODZAJE_POZNIEJSZYCH_PACZEK = ("wybor_kandydata", "przypisanie_reczne", "uklad")
RODZAJE = DECYZJE_O_PRACY + (RODZAJ_COFNIECIE, "powtorz_skan", "numer_plytki") + RODZAJE_POZNIEJSZYCH_PACZEK

STAN_DO_DOFREZOWANIA = "do_dofrezowania"
STAN_OCZEKUJE = "oczekuje"

WERSJA_PROGRAMU = "etap3-A1"  # do ``skany.wersja_programu``, dopoki paczka wydania (A11) nie poda numeru wydania
KOLUMNY_LISTY = ("kuweta", "zeby", "krazek", "plytka", "gniazdo", "projekt")


class BladSesji(ValueError):
    """Operacja niemozliwa w tym stanie (brak pracy, skan zastapiony, osoba spoza listy); komunikat dla okna."""


def skrot_ustawien(ust: dict) -> str:
    """16 znakow SHA-256 ustawien (do ``skany.skrot_ustawien``: przy jakich progach liczono skan)."""
    return hashlib.sha256(json.dumps(ust, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")).hexdigest()[:16]


def katalog_wynikow(ust: dict) -> Path:
    """Katalog plikow wynikow skanow: ``[sciezki] wyniki`` (wzgledny od katalogu programu)."""
    return B.sciezka_z_ustawien(ust, "wyniki")


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
                 wersja_programu: str = WERSJA_PROGRAMU, skrot_ust: str | None = None,
                 zegar: Callable[[], dt.datetime] | None = None):
        self.baza = baza
        self.operatorzy = tuple(operatorzy)  # lista osob z [sesja] operatorzy (DW3); pusta = osoba nieobowiazkowa
        self.operator: str | None = None  # osoba wybrana na poczatku zmiany
        self.katalog_wynikow = Path(katalog_wynikow) if katalog_wynikow is not None else None
        self.wersja_programu = wersja_programu
        self.skrot_ust = skrot_ust
        self._zegar = zegar or dt.datetime.now

    @classmethod
    def z_ustawien(cls, ust: dict, baza: B.Baza | None = None, **kw: Any) -> "Sesja":
        """Sesja wg ``ustawienia.toml``: baza z ``[sciezki] baza``, wyniki z ``[sciezki] wyniki``, osoby z ``[sesja] operatorzy``."""
        if baza is None:
            baza = B.otworz(B.sciezka_bazy(ust))
        return cls(baza, operatorzy=ust["sesja"]["operatorzy"], katalog_wynikow=katalog_wynikow(ust), skrot_ust=skrot_ustawien(ust), **kw)

    # --- czas i operator ---------------------------------------------------------------------
    def teraz(self) -> str:
        return self._zegar().replace(microsecond=0).isoformat()

    def dzis(self) -> str:
        return self._zegar().date().isoformat()

    def wybierz_operatora(self, nazwa: str) -> None:
        """Wybor osoby na poczatku zmiany (DW3): jej nazwa trafia do kolumny ``operator`` kazdej decyzji."""
        self.operator = self._operator(nazwa, wymagany=True)

    def _operator(self, podany: str | None = None, wymagany: bool = False) -> str | None:
        nazwa = podany if podany is not None else self.operator
        nazwa = nazwa.strip() if isinstance(nazwa, str) else nazwa
        if not nazwa:
            if self.operatorzy or wymagany:
                raise BladSesji("nie wybrano operatora - wybierz osobe z listy" + (f": {', '.join(self.operatorzy)}" if self.operatorzy else ""))
            return None
        if self.operatorzy and nazwa not in self.operatorzy:
            raise BladSesji(f"osoby {nazwa!r} nie ma na liscie operatorow ([sesja] operatorzy: {', '.join(self.operatorzy)})")
        return nazwa

    # --- przyjecie wyniku skanu ----------------------------------------------------------------
    def przyjmij_wynik(self, zdarzenie: Any, wynik: dict, tryb: str = TRYB_WIECZOR) -> int:
        """Zapisuje skan i jego prace (jedna praca = jeden wpis ``wynik["gniazda"]``); zwraca ``skany.id``.

        ``zdarzenie``: slownik albo obiekt z polami ``plik``, ``sha16``, ``rozmiar``, ``czas_pliku`` (kontrakt
        ``ZdarzenieSkanu`` z sekcji 3.8 planu). Plik wyniku jest zapisywany w calosci do ``katalog_wynikow``.
        Niczego nie zastepuje - ponowny skan plytki wymaga potwierdzenia (``zastap_skan``).
        """
        plik = _pole(zdarzenie, "plik")
        if not plik:
            raise BladSesji("zdarzenie skanu bez nazwy pliku")
        teraz = self.teraz()
        gniazda = wynik.get("gniazda") or []
        zgodny = wynik.get("uklad_zgodny")
        if zgodny is False:
            status = STATUS_NIEZGODNY_UKLAD
        elif _do_powtorzenia(wynik):
            status = STATUS_DO_POWTORZENIA
        else:
            status = STATUS_PRZYJETY
        wybor = wynik.get("plytka_wybor")
        with self.baza.transakcja():
            przed = {k["sha16"] for k in self.konflikty(self._data_skanu(_czas_iso(_pole(zdarzenie, "czas_pliku")), teraz), tryb)}
            skan_id = self.baza.wstaw(
                "skany", plik=str(plik), sha16=_pole(zdarzenie, "sha16") or wynik.get("skan_sha16"), rozmiar=_pole(zdarzenie, "rozmiar"),
                czas_pliku=_czas_iso(_pole(zdarzenie, "czas_pliku")), czas_analizy=teraz, czas_s=(wynik.get("czas_s") or {}).get("razem"),
                tryb=tryb, uklad=wynik.get("plytka"), uklad_zrodlo=("auto" if wybor == "auto" else "reczny") if wybor else None,
                uklad_zgodny=None if zgodny is None else int(bool(zgodny)), numer_plytki=wynik.get("numer"),
                numer_zrodlo=wynik.get("numer_zrodlo"), status=status, wersja_programu=self.wersja_programu, skrot_ustawien=self.skrot_ust)
            w_gniezdzie: dict[Any, int] = {}
            for g in gniazda:
                w_gniezdzie[g.get("gniazdo")] = w_gniezdzie.get(g.get("gniazdo"), 0) + 1
                self._wstaw_prace(skan_id, g, w_gniezdzie[g.get("gniazdo")], wynik)
            if self.katalog_wynikow is not None:
                self.baza.wykonaj("UPDATE skany SET wynik_json = ? WHERE id = ?", (self._zapisz_wynik(skan_id, plik, wynik), skan_id))
            self.baza.zdarzenie("silnik", "skan_przyjety", {"status": status, "prace": len(gniazda), "czas_s": (wynik.get("czas_s") or {}).get("razem")},
                                skan_id=skan_id, czas=teraz)
            sk = self.baza.wiersz("SELECT * FROM skany WHERE id = ?", (skan_id,))
            nowe = [k["sha16"] for k in self.konflikty(self._data_skanu(sk["czas_pliku"], sk["czas_analizy"]), tryb) if k["sha16"] not in przed]
            if nowe:  # SE8: ten sam projekt w dwoch gniazdach wieczoru - zgloszenie do rozstrzygniecia
                self.baza.zdarzenie("system", "konflikt_projektu", {"sha16": nowe}, skan_id=skan_id, czas=teraz)
        return skan_id

    def przyjmij_blad(self, zdarzenie: Any, opis: str, tryb: str = TRYB_WIECZOR) -> int:
        """Analiza skanu nie dala wyniku (awaria silnika, zly plik): skan ze statusem ``blad`` i wpis w dzienniku."""
        plik = _pole(zdarzenie, "plik")
        if not plik:
            raise BladSesji("zdarzenie skanu bez nazwy pliku")
        teraz = self.teraz()
        with self.baza.transakcja():
            skan_id = self.baza.wstaw("skany", plik=str(plik), sha16=_pole(zdarzenie, "sha16"), rozmiar=_pole(zdarzenie, "rozmiar"),
                                      czas_pliku=_czas_iso(_pole(zdarzenie, "czas_pliku")), czas_analizy=teraz, tryb=tryb, status=STATUS_BLAD,
                                      wersja_programu=self.wersja_programu, skrot_ustawien=self.skrot_ust)
            self.baza.zdarzenie("silnik", "blad_analizy", {"opis": str(opis)}, skan_id=skan_id, czas=teraz)
        return skan_id

    @staticmethod
    def _data_skanu(czas_pliku: str | None, czas_analizy: str | None) -> str:
        return (czas_pliku or czas_analizy or "")[:10]

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
        """Wpis frezowania pracy: wskazany przez wynik (pula ze wspolczynnikiem per praca, A5), inaczej najnowszy dla projektu."""
        wskazany = kandydat.get("frezowanie_id")
        if wskazany is not None and self.baza.wiersz("SELECT id FROM frezowania WHERE id = ?", (wskazany,)):
            return int(wskazany)
        if projekt_id is None:
            return None
        w = self.baza.wiersz("SELECT id FROM frezowania WHERE projekt_id = ? ORDER BY data DESC, id DESC LIMIT 1", (projekt_id,))
        return w["id"] if w else None

    def _zapisz_wynik(self, skan_id: int, plik: Any, wynik: dict) -> str:
        """Zapisuje caly wynik do ``katalog_wynikow``; zwraca sciezke do kolumny ``skany.wynik_json`` (wzgledna od folderu bazy, gdy sie da)."""
        self.katalog_wynikow.mkdir(parents=True, exist_ok=True)
        rdzen = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", PureWindowsPath(str(plik)).stem) or "skan"
        cel = self.katalog_wynikow / f"skan{skan_id:06d}_{rdzen}_wynik.json"
        cel.write_text(json.dumps(wynik, ensure_ascii=False, indent=1), encoding="utf-8")
        try:
            return cel.resolve().relative_to(self.baza.plik.resolve().parent).as_posix()
        except ValueError:
            return cel.resolve().as_posix()

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
        (dla ``praca_id``) oraz ``powtorz_skan`` i ``numer_plytki`` (dla ``skan_id``). ``operator``: osoba inna niz wybrana
        na poczatku zmiany.
        """
        if rodzaj not in RODZAJE:
            raise BladSesji(f"nieznany rodzaj decyzji {rodzaj!r} (znane: {', '.join(RODZAJE)})")
        if rodzaj in RODZAJE_POZNIEJSZYCH_PACZEK:
            raise BladSesji(f"rodzaj decyzji {rodzaj!r} nie jest obslugiwany przez sesje wieczorna (dojdzie w kolejnych paczkach etapu 3)")
        if rodzaj == "powtorz_skan":
            return self._zastap(skan_id, int(wartosc) if wartosc not in (None, "") else None, operator)[0]
        if rodzaj == "numer_plytki":
            return self.podaj_numer_plytki(skan_id, wartosc, operator)
        if rodzaj == RODZAJ_COFNIECIE:
            return self.cofnij(praca_id, operator)
        osoba = self._operator(operator)
        with self.baza.transakcja():
            praca = self._praca_do_decyzji(praca_id)
            decyzja_id = self.baza.wstaw("decyzje", praca_id=praca["id"], rodzaj=rodzaj, operator=osoba, czas=self.teraz())
            self._odswiez_punkt(praca)
        return decyzja_id

    def ukruszona(self, praca_id: int, operator: str | None = None) -> int:
        """Przycisk "Ukruszona": praca idzie na liste "do dofrezowania"."""
        return self.decyzja(praca_id, "ukruszona", operator=operator)

    def ok(self, praca_id: int, operator: str | None = None) -> int:
        """Przycisk "OK": falszywy alarm programu."""
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
            self._odswiez_punkt(praca)
        return decyzja_id

    def zastap_skan(self, skan_id: int, poprzedni_id: int | None = None, operator: str | None = None) -> int:
        """Potwierdzenie "to ponowny skan tej plytki" (zalozenie Z4): poprzedni skan dostaje status ``zastapiony``.

        Bez ``poprzedni_id`` zastepowany jest skan wskazany w ``stan_wieczoru`` jako ``moze_zastapic``. Zwraca id skanu zastapionego.
        """
        return self._zastap(skan_id, poprzedni_id, operator)[1]

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
            self._skan(skan_id)
            decyzja_id = self.baza.wstaw("decyzje", skan_id=skan_id, rodzaj="numer_plytki", wartosc=str(n), operator=osoba, czas=self.teraz())
            self.baza.wykonaj("UPDATE skany SET numer_plytki = ?, numer_zrodlo = 'podany' WHERE id = ?", (n, skan_id))
        return decyzja_id

    def _skan(self, skan_id: int | None) -> dict:
        sk = self.baza.wiersz("SELECT * FROM skany WHERE id = ?", (skan_id,)) if skan_id is not None else None
        if sk is None:
            raise BladSesji(f"nie ma skanu {skan_id}")
        return sk

    def _praca_do_decyzji(self, praca_id: int | None) -> dict:
        praca = self.baza.wiersz("SELECT p.*, s.status AS status_skanu FROM prace p JOIN skany s ON s.id = p.skan_id WHERE p.id = ?", (praca_id,))
        if praca is None:
            raise BladSesji(f"nie ma pracy {praca_id}")
        if praca["status_skanu"] == STATUS_ZASTAPIONY:
            raise BladSesji(f"praca {praca_id}: skan {praca['skan_id']} jest zastapiony ponownym skanem plytki - decyzje podejmij na nowym skanie")
        return praca

    def _decyzja_pracy(self, praca_id: int) -> dict | None:
        return _obowiazujace(self.baza.wiersze("SELECT * FROM decyzje WHERE praca_id = ? ORDER BY id", (praca_id,))).get(praca_id)

    def _decyzje_skanow(self, skany_ids: list[int]) -> dict[int, dict]:
        if not skany_ids:
            return {}
        return _obowiazujace(self.baza.wiersze(
            f"SELECT d.* FROM decyzje d JOIN prace p ON p.id = d.praca_id WHERE p.skan_id IN ({_znaki(len(skany_ids))}) ORDER BY d.id", tuple(skany_ids)))

    def _poprzedni_skan(self, sk: dict) -> dict | None:
        """Skan, ktory ``sk`` moze zastapic: najnowszy wczesniejszy aktywny skan tego wieczoru o tym samym numerze plytki albo tej samej zawartosci pliku."""
        if sk["status"] not in STATUSY_AKTYWNE or (sk["numer_plytki"] is None and not sk["sha16"]):
            return None
        return self.baza.wiersz(
            f"""SELECT * FROM skany WHERE id < ? AND tryb IS ? AND substr(COALESCE(czas_pliku, czas_analizy), 1, 10) = ?
                AND status IN ({_znaki(len(STATUSY_AKTYWNE))})
                AND ((numer_plytki IS NOT NULL AND numer_plytki = ?) OR (sha16 IS NOT NULL AND sha16 = ?))
                ORDER BY id DESC LIMIT 1""",
            (sk["id"], sk["tryb"], self._data_skanu(sk["czas_pliku"], sk["czas_analizy"]), *STATUSY_AKTYWNE, sk["numer_plytki"], sk["sha16"]))

    def _zastap(self, skan_id: int | None, poprzedni_id: int | None, operator: str | None) -> tuple[int, int]:
        osoba = self._operator(operator)
        with self.baza.transakcja():
            nowy = self._skan(skan_id)
            if nowy["status"] not in STATUSY_AKTYWNE:
                raise BladSesji(f"skan {skan_id} ma status {nowy['status']!r} - nie moze zastapic innego skanu")
            if poprzedni_id is None:
                poprzedni = self._poprzedni_skan(nowy)
                if poprzedni is None:
                    raise BladSesji(f"skan {skan_id}: nie ma skanu do zastapienia (ten sam numer plytki albo ten sam plik, ten sam wieczor)")
            else:
                poprzedni = self._skan(poprzedni_id)
                ta_sama_sesja = (poprzedni["tryb"] == nowy["tryb"] and self._data_skanu(poprzedni["czas_pliku"], poprzedni["czas_analizy"])
                                 == self._data_skanu(nowy["czas_pliku"], nowy["czas_analizy"]))
                if poprzedni["id"] >= nowy["id"] or poprzedni["status"] not in STATUSY_AKTYWNE or not ta_sama_sesja:
                    raise BladSesji(f"skan {poprzedni_id} nie moze byc zastapiony skanem {skan_id} (musi byc wczesniejszy, aktywny, z tego samego wieczoru)")
            decyzja_id = self.baza.wstaw("decyzje", skan_id=nowy["id"], rodzaj="powtorz_skan", wartosc=str(poprzedni["id"]), operator=osoba, czas=self.teraz())
            self.baza.wykonaj("UPDATE skany SET status = ? WHERE id = ?", (STATUS_ZASTAPIONY, poprzedni["id"]))
            self.baza.wykonaj("UPDATE skany SET zastepuje_id = ? WHERE id = ?", (poprzedni["id"], nowy["id"]))
            for praca in self.baza.wiersze("SELECT * FROM prace WHERE skan_id = ? AND projekt_id IS NOT NULL ORDER BY id", (poprzedni["id"],)):
                self._odswiez_punkt(praca, aktywna=False)  # decyzje skanu zastapionego przestaja sie liczyc
        return decyzja_id, poprzedni["id"]

    # --- stan punktow (tylko czesc wieczorna: "do dofrezowania") ---------------------------------
    def _odswiez_punkt(self, praca: dict, aktywna: bool = True) -> None:
        """Uzgadnia ``stan_punktow`` projektu pracy z jej obowiazujaca decyzja.

        "Ukruszona" -> ``do_dofrezowania`` (wskazuje te prace). Gdy decyzja przestaje obowiazywac (cofniecie, "OK", skan
        zastapiony), a punkt wskazywal te prace: przechodzi na inna aktywna prace tego projektu oznaczona jako ukruszona,
        a gdy takiej nie ma - wraca do ``oczekuje``. Punktow w innych stanach nie rusza.
        """
        projekt_id = praca["projekt_id"]
        if projekt_id is None:
            return
        decyzja = self._decyzja_pracy(praca["id"]) if aktywna else None
        if decyzja is not None and decyzja["rodzaj"] in DECYZJE_UKRUSZENIA:
            self._ustaw_punkt(projekt_id, STAN_DO_DOFREZOWANIA, praca["id"], decyzja["czas"])
            return
        punkt = self.baza.wiersz("SELECT * FROM stan_punktow WHERE projekt_id = ?", (projekt_id,))
        if punkt is None or punkt["stan"] != STAN_DO_DOFREZOWANIA or punkt["praca_id"] != praca["id"]:
            return
        inne = self.baza.wiersze(
            f"SELECT p.id, p.skan_id FROM prace p JOIN skany s ON s.id = p.skan_id WHERE p.projekt_id = ? AND p.id <> ? "
            f"AND s.status IN ({_znaki(len(STATUSY_AKTYWNE))})", (projekt_id, praca["id"], *STATUSY_AKTYWNE))
        decyzje = self._decyzje_skanow(sorted({w["skan_id"] for w in inne}))
        ukruszone = [decyzje[w["id"]] for w in inne if w["id"] in decyzje and decyzje[w["id"]]["rodzaj"] in DECYZJE_UKRUSZENIA]
        if ukruszone:
            ostatnia = max(ukruszone, key=lambda d: d["id"])
            self._ustaw_punkt(projekt_id, STAN_DO_DOFREZOWANIA, ostatnia["praca_id"], ostatnia["czas"])
        else:
            self._ustaw_punkt(projekt_id, STAN_OCZEKUJE, None, self.teraz())

    def _ustaw_punkt(self, projekt_id: int, stan: str, praca_id: int | None, czas: str) -> None:
        self.baza.wykonaj(
            """INSERT INTO stan_punktow (projekt_id, stan, praca_id, sesja_pieca_id, czas) VALUES (?, ?, ?, NULL, ?)
               ON CONFLICT (projekt_id) DO UPDATE SET stan = excluded.stan, praca_id = excluded.praca_id, sesja_pieca_id = NULL, czas = excluded.czas""",
            (projekt_id, stan, praca_id, czas))

    # --- odczyt stanu ----------------------------------------------------------------------------
    def _skany_sesji(self, data: str, tryb: str, tylko_aktywne: bool = False) -> list[dict]:
        sql = "SELECT * FROM skany WHERE tryb = ? AND substr(COALESCE(czas_pliku, czas_analizy), 1, 10) = ?"
        parametry: tuple = (tryb, data)
        if tylko_aktywne:
            sql += f" AND status IN ({_znaki(len(STATUSY_AKTYWNE))})"
            parametry += STATUSY_AKTYWNE
        return self.baza.wiersze(sql + " ORDER BY id", parametry)

    def _prace_skanow(self, skany_ids: list[int]) -> list[dict]:
        if not skany_ids:
            return []
        return self.baza.wiersze(
            f"""SELECT p.*, pr.zeby AS zeby, z.kuweta AS kuweta, f.krazek AS krazek, sp.stan AS stan_punktu
                FROM prace p LEFT JOIN projekty pr ON pr.id = p.projekt_id LEFT JOIN zlecenia z ON z.id = pr.zlecenie_id
                LEFT JOIN frezowania f ON f.id = p.frezowanie_id LEFT JOIN stan_punktow sp ON sp.projekt_id = p.projekt_id
                WHERE p.skan_id IN ({_znaki(len(skany_ids))}) ORDER BY p.skan_id, p.id""", tuple(skany_ids))

    @staticmethod
    def _przypisany(praca: dict) -> str | None:
        """``sha16`` projektu, do ktorego praca jest przypisana (praca szara albo bez kandydata: brak przypisania)."""
        return praca["kandydat1_sha16"] if praca["kandydat1_sha16"] and praca["status_match"] != "szary" else None

    @staticmethod
    def _kolor(status_skanu: str, status_gniazda: str | None) -> str | None:
        """Kolor pracy na mapie wieczoru: skan nieaktywny - brak; skan do powtorzenia nie ma prac zielonych."""
        if status_skanu not in STATUSY_AKTYWNE:
            return None
        if status_skanu == STATUS_DO_POWTORZENIA and status_gniazda == "zielony":
            return "zolty"
        return status_gniazda

    def stan_wieczoru(self, data: str | None = None) -> dict:
        """Caly stan wieczoru ``data`` (RRRR-MM-DD, domyslnie dzis) jako zwykle dane (nadaje sie do JSON).

        ``skany``: wszystkie skany wieczoru z pracami; praca ma statusy z pliku wyniku, ``kolor`` (obowiazujacy na mapie),
        ``sha16`` / ``kuweta`` / ``zeby`` / ``krazek`` i obowiazujaca ``decyzja``. ``liczniki`` i ``prac``: tylko skany aktywne.
        ``do_potwierdzenia``: skany, ktore wygladaja na ponowny skan plytki (``zastap_skan``). Bez nazw folderow i plikow zlecen.
        """
        data = data or self.dzis()
        skany = self._skany_sesji(data, TRYB_WIECZOR)
        ids = [s["id"] for s in skany]
        decyzje = self._decyzje_skanow(ids)
        prace_skanu: dict[int, list[dict]] = {i: [] for i in ids}
        for p in self._prace_skanow(ids):
            prace_skanu[p["skan_id"]].append(p)
        wynik_skany, razem, prac, do_potwierdzenia = [], {}, 0, []
        for s in skany:
            aktywny = s["status"] in STATUSY_AKTYWNE
            poprzedni = self._poprzedni_skan(s)
            liczniki: dict[str, int] = {}
            prace = []
            for p in prace_skanu[s["id"]]:
                kolor = self._kolor(s["status"], p["status_gniazda"])
                d = decyzje.get(p["id"])
                if aktywny:
                    prac += 1
                    if kolor is not None:
                        liczniki[kolor] = liczniki.get(kolor, 0) + 1
                        razem[kolor] = razem.get(kolor, 0) + 1
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
                do_potwierdzenia.append({"skan_id": s["id"], "poprzedni_id": poprzedni["id"], "numer_plytki": s["numer_plytki"]})
            wynik_skany.append({
                "id": s["id"], "plik": s["plik"], "sha16": s["sha16"], "czas_pliku": s["czas_pliku"], "czas_analizy": s["czas_analizy"],
                "czas_s": s["czas_s"], "uklad": s["uklad"], "uklad_zrodlo": s["uklad_zrodlo"],
                "uklad_zgodny": None if s["uklad_zgodny"] is None else bool(s["uklad_zgodny"]), "numer_plytki": s["numer_plytki"],
                "numer_zrodlo": s["numer_zrodlo"], "status": s["status"], "aktywny": aktywny, "zastepuje_id": s["zastepuje_id"],
                "moze_zastapic": poprzedni["id"] if poprzedni is not None else None, "wynik_json": s["wynik_json"],
                "liczniki": liczniki, "prace": prace})
        return {"data": data, "skany": wynik_skany, "liczniki": razem, "prac": prac, "do_potwierdzenia": do_potwierdzenia,
                "do_dofrezowania": self.do_dofrezowania(data), "konflikty": self.konflikty(data)}

    def do_dofrezowania(self, data: str | None = None) -> list[dict]:
        """Lista "do dofrezowania" wieczoru: prace ze skanow aktywnych, ktorych obowiazujaca decyzja to "Ukruszona".

        Pozycja: ``kuweta``, ``zeby``, ``krazek`` (None, gdy pracy nie ma w indeksie albo nie ma wpisu frezowania), plytka,
        gniazdo, ``sha16`` projektu, kto i kiedy zdecydowal, ``stan_punktu`` (stan zlecenia w ``stan_punktow``).
        """
        data = data or self.dzis()
        numery = {s["id"]: s["numer_plytki"] for s in self._skany_sesji(data, TRYB_WIECZOR, tylko_aktywne=True)}
        decyzje = self._decyzje_skanow(list(numery))
        lista = []
        for p in self._prace_skanow(list(numery)):
            d = decyzje.get(p["id"])
            if d is None or d["rodzaj"] not in DECYZJE_UKRUSZENIA:
                continue
            lista.append({
                "praca_id": p["id"], "skan_id": p["skan_id"], "numer_plytki": numery[p["skan_id"]], "gniazdo": p["gniazdo"],
                "sha16": self._przypisany(p), "projekt_id": p["projekt_id"], "kuweta": p["kuweta"], "zeby": p["zeby"], "krazek": p["krazek"],
                "ubytki": p["ubytki"], "ubytek_max_mm": p["ubytek_max_mm"], "decyzja": d["rodzaj"], "operator": d["operator"], "czas": d["czas"],
                "stan_punktu": p["stan_punktu"] if p["projekt_id"] is not None else None})
        return lista

    def zapisz_do_dofrezowania(self, data: str | None = None, katalog: str | Path | None = None) -> Path:
        """Lista "do dofrezowania" jako plik ``do_dofrezowania_<data>.csv`` (zalozenie Z6; domyslnie w folderze bazy)."""
        data = data or self.dzis()
        katalog = Path(katalog) if katalog is not None else self.baza.plik.parent
        katalog.mkdir(parents=True, exist_ok=True)
        cel = katalog / f"do_dofrezowania_{data}.csv"
        with open(cel, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(KOLUMNY_LISTY)
            for x in self.do_dofrezowania(data):
                w.writerow(["" if v is None else v for v in (x["kuweta"], x["zeby"], x["krazek"], x["numer_plytki"], x["gniazdo"], x["sha16"])])
        return cel

    def konflikty(self, data: str | None = None, tryb: str = TRYB_WIECZOR) -> list[dict]:
        """SE8: projekty (``sha16``) przypisane do prac w wiecej niz jednym gniezdzie skanow aktywnych tego wieczoru.

        Nie licza sie prace szare ani prace oznaczone "Ukruszona" (ten sam STL drugi raz to wtedy zab dofrezowany).
        Dwa fragmenty w tym samym gniezdzie jednego skanu to jedno miejsce. Rozstrzygniecie nalezy do technika.
        """
        data = data or self.dzis()
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
