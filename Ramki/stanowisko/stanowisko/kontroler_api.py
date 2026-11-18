"""kontroler_api - KONTRAKT miedzy kontrolerem aplikacji "Stanowisko" a oknem (paczka E3-A3a; ekran buduje A3b).

Kontroler spina ``scanner`` -> ``silnik`` -> ``session`` / ``baza`` i wystawia oknu trzy rzeczy:

1. STAN - ``kontroler.stan() -> StanAplikacji``: niezmienny obraz calego ekranu wieczornego (zwykle dane, bez Qt):
   plytki doby z mapa gniazd (``Plytka`` -> ``Gniazdo`` -> ``Praca``: klasa koloru, status, podpis, kolor ekranu), lista
   "do dofrezowania", pytania do technika (``Pytanie``: ponowny skan z liczba decyzji, ktore przestana obowiazywac; plytka
   nie z trybu; brak numeru plytki), komunikaty (``Komunikat``: skan do powtorzenia, plytka niezgodna z ukladem, plik
   zajety - "czeka na zwolnienie", ``plik_niedostepny`` / ``plik_zmieniony``, blad inspekcji gniazda, odmowy), postep
   analizy, kolejka, pula projektow (liczba STL), skaner, operator, doba i zmiana.
2. POLECENIA - metody kontrolera wolane przez okno (lista: ``POLECENIA``); kazda zwraca ``Odpowiedz`` (``ok`` + tekst dla
   technika) i NIGDY nie rzuca wyjatku - ani z powodu zlego stanu (brak operatora, skan nieprzyjety), ani zlych argumentow
   (zly typ, zla liczba: ``kod="zle_argumenty"``, D1) - odmowa jest odpowiedzia i komunikatem w stanie.
   ``kontroler.wykonaj(nazwa, *argumenty)`` wola polecenie po nazwie (przyciski z ``Pytanie``).
3. SYGNALY - ``kontroler.subskrybuj(funkcja)``: funkcja dostaje ``ZdarzenieKontrolera`` (``stan`` / ``postep`` /
   ``komunikat`` / ``pytanie`` / ``zamkniety``). W oknie Qt: ``lacznik_qt(kontroler)`` - obiekt z sygnalami Qt
   ``stan_zmieniony(object)``, ``postep(object)``, ``komunikat(object)``, ``pytanie(object)``, ``zamkniety()`` i zegarem,
   ktory co 30 ms wola ``kontroler.przetworz()``.

WATEK. Kontroler zyje w watku okna: wszystkie polecenia, ``stan()`` i ``przetworz()`` wola sie z jednego watku (polaczenie
z baza jest do niego przywiazane). Zdarzenia z watkow ``scanner`` i ``silnik`` czekaja w kolejkach; ``przetworz()`` je
oproznia (najwyzej ``limit_s`` na wywolanie), zapisuje w sesji i powiadamia subskrybentow - dlatego okno musi je wolac
regularnie (``lacznik_qt`` robi to zegarem), a test bez okna wola je sam.

CZEGO OKNU NIE WOLNO: siegac do ``session`` / ``baza`` / ``scanner`` / ``silnik`` z pominieciem kontrolera (obraz odchylek:
``kontroler_api.wczytaj_podglad``, D12), trzymac wlasnych kolorow i napisow statusow (tylko ``statusy``), pokazywac sciezek
i nazw plikow (stan ich nie zawiera - poza folderem puli i folderem skanera, ktore sa ustawieniami), zmieniac obiektow stanu
(sa zamrozone, takze slowniki: ``ZamrozonySlownik``, D2), wolac kontrolera z innego watku.

PYTANIA I KOMUNIKATY (D6): okienka do pokazania = ``stan.pytania`` / ``stan.komunikaty`` (otwarte); ``Plytka.pytania`` /
``Plytka.komunikaty`` to pelny stan plytki (historia) - pozycje zamkniete przez technika maja tam ``ukryte=True``.

Zmiany kontraktu po rundzie 2 recenzji (wersja 2, wszystkie addytywne): opis w ``opisy_modulow/aplikacja.md``.

Plik zawiera tez ``KontrolerSesji`` (wspolna czesc prawdziwego kontrolera i atrapy: stan z ``session``, polecenia
o decyzjach) oraz ``AtrapaKontrolera`` - kontroler na danych sztucznych, bez skanera i silnika, do budowy i testow okna.
Modul uzywa tylko biblioteki standardowej; PySide6 jest importowane dopiero w ``lacznik_qt``.
"""
from __future__ import annotations

import collections
import dataclasses
import datetime as dt
import hashlib
import inspect
import json
import logging
import math
import os
import re
import shutil
import sqlite3
import tempfile
import time
import warnings
from pathlib import Path
from typing import Any, Callable

from . import baza as B
from . import session as SE
from . import statusy as ST

LOG = logging.getLogger(__name__)

WERSJA_KONTRAKTU = 2  # 2: zmiany addytywne po rundzie 2 recenzji PR #20 (okno zbudowane na wersji 1 dziala bez zmian)
TRYB_WIECZOR = SE.TRYB_WIECZOR
LIMIT_PRZETWARZANIA_S = 0.05  # najdluzej tyle trwa jedno ``przetworz()``, gdy czeka wiele zdarzen (petla okna: przerwy < 200 ms)
OKRES_LACZNIKA_MS = 30
PAMIEC_ODRZUCEN_DNI = 2  # z ilu dni wstecz czytane sa odrzucone propozycje ponownego skanu
LIMIT_KOMUNIKATOW = 50  # tyle komunikatow ulotnych naraz w stanie (starsze znikaja same)
NUMERY_PLYTEK_ZAPASOWE = tuple(range(1, 10))  # cyfry do wyboru, gdy ukladu plytki nie da sie wczytac
WSPOLCZYNNIK_MIN, WSPOLCZYNNIK_MAX = 0.9, 1.5  # zakres wspolczynnika skurczu przyjmowany z okna (poranna 1,0; wieczorna ok. 1,2-1,25)
STANY_PULI = ("nieustawiona", "liczenie", "gotowa", "pusta", "brak_folderu")
KOD_ZLE_ARGUMENTY = "zle_argumenty"  # D1: zly typ albo zla liczba argumentow polecenia (blad okna, nie technika)
ID_BLAD_ZAPISU = "blad_zapisu"  # P1: staly id komunikatu trwalego o bledzie zapisu wynikow (jeden na program)
PLIK_LISTY = "do_dofrezowania_biezaca.csv"  # P7: plik listy biezacej w folderze bazy (nazwa jak w session.zapisz_do_dofrezowania)
_LICZBA_MIN, _LICZBA_MAX = -(2 ** 63), 2 ** 63 - 1  # zakres liczby calkowitej SQLite (id, numer plytki)
_WZOR_DOBY = re.compile(r"\d{4}-\d{2}-\d{2}")

# polecenia okna do kontrolera (nazwy metod); ``Praca.dozwolone`` / ``Plytka.dozwolone`` podaja, ktore maja teraz sens
POLECENIA = ("wybierz_operatora", "ukruszona", "ok", "cofnij", "potwierdz_ponowny_skan", "odrzuc_ponowny_skan", "cofnij_zastapienie",
             "dopusc_plytke", "cofnij_dopuszczenie", "podaj_numer_plytki", "zamknij_pytanie", "zamknij_komunikat", "start_skanu",
             "ustaw_pule", "odswiez_pule", "zamknij",
             "zapisz_liste", "ponow_zapis")  # 17., 18.: runda 2 recenzji (P7, P1)
# sygnaly kontrolera do okna (``ZdarzenieKontrolera.typ``; w ``lacznik_qt``: stan_zmieniony, postep, komunikat, pytanie, zamkniety)
SYGNALY = ("stan", "postep", "komunikat", "pytanie", "zamkniety")
RODZAJE_PYTAN = ("ponowny_skan", "plytka_nie_z_trybu", "brak_numeru_plytki")


# ----------------------------------------------------------------------------
# slowniki tylko do odczytu w stanie (D2)
# ----------------------------------------------------------------------------
class ZamrozonySlownik(dict):
    """Slownik w stanie kontrolera (``liczniki``, ``konflikty``, ubytki i kandydaci w ``SzczegolyPracy``): czyta sie go jak
    zwykly ``dict`` (``[]``, ``get``, ``items``, porownanie z ``dict``, JSON, ``dataclasses.asdict``), a kazda proba zmiany
    konczy sie ``TypeError`` - okno nie zmieni stanu trzymanego przez kontroler (ten sam obiekt dostaja wszyscy odbiorcy
    sygnalu). Ma ``hash``, wiec caly ``StanAplikacji`` tez."""

    __slots__ = ()

    def _tylko_odczyt(self, *argumenty: Any, **nazwane: Any) -> None:
        raise TypeError("stan kontrolera jest tylko do odczytu - slownika nie wolno zmieniac")

    __setitem__ = __delitem__ = clear = pop = popitem = setdefault = update = __ior__ = _tylko_odczyt

    def __hash__(self) -> int:  # type: ignore[override]
        return hash(frozenset(self.items()))

    def __reduce__(self):
        return (type(self), (dict(self),))

    def __copy__(self) -> "ZamrozonySlownik":
        return self

    def __deepcopy__(self, pamiec: dict) -> "ZamrozonySlownik":
        return self


def zamroz(obiekt: Any) -> Any:
    """Kopia danych tylko do odczytu: slownik -> ``ZamrozonySlownik``, lista / krotka -> krotka, zbior -> ``frozenset``."""
    if isinstance(obiekt, dict):
        return ZamrozonySlownik({k: zamroz(v) for k, v in obiekt.items()})
    if isinstance(obiekt, (list, tuple)):
        return tuple(zamroz(v) for v in obiekt)
    if isinstance(obiekt, (set, frozenset)):
        return frozenset(zamroz(v) for v in obiekt)
    return obiekt


def _jest_liczba(x: Any) -> bool:
    """Liczba calkowita mieszczaca sie w SQLite (id pracy / skanu); ``bool`` to nie liczba."""
    return isinstance(x, int) and not isinstance(x, bool) and _LICZBA_MIN <= x <= _LICZBA_MAX


# ----------------------------------------------------------------------------
# typy danych stanu (wszystkie zamrozone; pola opcjonalne maja wartosci domyslne)
# ----------------------------------------------------------------------------
@dataclasses.dataclass(frozen=True)
class Odpowiedz:
    """Odpowiedz kontrolera na polecenie okna. ``ok`` False = odmowa: ``tekst`` to powod i rada dla technika, ``kod`` -
    rodzaj odmowy (klucz ``statusy.KOMUNIKATY``, np. ``brak_operatora``, ``zle_argumenty``). ``dane`` - wynik polecenia
    (np. id decyzji, stan puli, nazwa pliku listy). Przy ``ok`` True ``kod`` jest zwykle pusty; wyjatek: ``wylogowano``
    (``wybierz_operatora(None)``)."""

    ok: bool
    tekst: str = ""
    kod: str = ""
    dane: Any = None

    def __bool__(self) -> bool:
        return self.ok


@dataclasses.dataclass(frozen=True)
class Przycisk:
    """Odpowiedz na pytanie: okno pokazuje ``napis`` i po kliknieciu wola ``kontroler.wykonaj(polecenie, *argumenty)``."""

    polecenie: str
    napis: str
    argumenty: tuple = ()


@dataclasses.dataclass(frozen=True)
class NaLiscie:
    """"Ten zab jest juz na liscie do dofrezowania": pozycja listy dla projektu tej pracy. ``ta_praca`` True = pozycja to
    ta praca; False = inna praca tego samego projektu (skan ``skan_id`` z doby ``doba``, zmiana ``zmiana``)."""

    praca_id: int
    skan_id: int
    doba: str
    zmiana: int
    ta_praca: bool
    tekst: str = ""


@dataclasses.dataclass(frozen=True)
class Praca:
    """Widok jednej pracy (jeden fragment w gniezdzie jednego skanu). ``kolor`` = klasa koloru PO decyzjach technika (jak
    w ``session``: zielony / czerwony / zolty / szary / pomaranczowy / zatwierdzona_ok / None), ``status`` = klucz
    ``statusy.STATUSY``, ``rgb`` = kolor ekranu ``#rrggbb``, ``podpis`` / ``opis`` = teksty dla technika.
    ``status_programu`` = ocena programu sprzed decyzji. ``dozwolone`` = polecenia, ktore maja teraz sens dla tej pracy."""

    praca_id: int
    skan_id: int
    gniazdo: int | None
    status: str
    kolor: str | None
    rgb: str
    podpis: str
    opis: str = ""
    nr_fragmentu: int = 1
    status_programu: str | None = None
    status_inspekcji: str | None = None
    status_match: str | None = None
    decyzja: str | None = None  # ukruszona / ukruszona_niewykryta / ok / None
    operator: str | None = None
    czas_decyzji: str | None = None
    sha16: str | None = None  # skrot projektu, do ktorego praca jest przypisana
    kuweta: str | None = None
    zeby: str | None = None
    krazek: str | None = None
    pewnosc: float | None = None
    pokrycie: float | None = None
    ubytki: int | None = None
    ubytek_max_mm: float | None = None
    blad_inspekcji: bool = False
    na_liscie: NaLiscie | None = None
    dozwolone: tuple = ()


@dataclasses.dataclass(frozen=True)
class Gniazdo:
    """Jedno gniazdo na mapie plytki. Puste: ``prace`` = (), status ``pusty``. Dwie prace: status ``podwojny``."""

    nr: int
    status: str
    kolor: str | None
    rgb: str
    podpis: str
    prace: tuple = ()

    @property
    def praca(self) -> Praca | None:
        return self.prace[0] if self.prace else None


@dataclasses.dataclass(frozen=True)
class Komunikat:
    """Informacja dla technika. ``rodzaj`` = klucz ``statusy.KOMUNIKATY``; ``poziom``: info / ostrzezenie / blad.
    ``trwaly`` True = zostaje na ekranie, dopoki trwa przyczyna (stan skanu - wraca po restarcie; ``blad_zapisu`` - do
    udanego zapisu) albo technik go nie zamknie; False = informacja ulotna. ``ukryte`` True = zamkniety przez technika
    (tylko w ``Plytka.komunikaty`` - historia plytki; w ``stan.komunikaty`` sa tylko otwarte)."""

    id: str
    rodzaj: str
    poziom: str
    tytul: str
    tekst: str
    czas: str = ""
    skan_id: int | None = None
    gniazda: tuple = ()
    trwaly: bool = False
    ukryte: bool = False


@dataclasses.dataclass(frozen=True)
class Pytanie:
    """Pytanie, na ktore technik odpowiada przyciskiem z ``odpowiedzi``. ``rodzaj``: ``RODZAJE_PYTAN``.
    Ponowny skan: ``liczba_decyzji`` / ``liczba_ukruszonych`` = ile decyzji poprzedniego skanu przestanie obowiazywac.
    Brak numeru plytki: ``numery`` = numery plytek tego ukladu (okno pokazuje cyfry; ``podaj_numer_plytki(skan_id, n)``).
    ``ukryte`` True = technik kliknal "Pozniej" (tylko w ``Plytka.pytania``; okienka pokazuje sie z ``stan.pytania``)."""

    id: str
    rodzaj: str
    skan_id: int
    poziom: str
    tytul: str
    tekst: str
    odpowiedzi: tuple = ()
    poprzedni_id: int | None = None
    numer_plytki: int | None = None
    liczba_decyzji: int = 0
    liczba_ukruszonych: int = 0
    numery: tuple = ()
    ukryte: bool = False


@dataclasses.dataclass(frozen=True)
class Plytka:
    """Jeden skan plytki z doby roboczej. ``status`` = status skanu z bazy (przyjety / do_powtorzenia / zastapiony /
    niezgodny_uklad / plytka_nie_z_trybu / blad), ``aktywna`` = jej prace licza sie do stanu i list. ``gniazda`` = wszystkie
    gniazda ukladu (takze puste) w kolejnosci numerow; ``poza_gniazdem`` = prace bez gniazda. ``uklad`` = nazwa ukladu do
    ``uklad.wczytaj`` (geometria mapy). ``zielonych`` jest 0 dla kazdej plytki, ktora niczego nie potwierdza."""

    skan_id: int
    status: str
    aktywna: bool
    napis: str
    numer: int | None = None
    numer_zrodlo: str | None = None
    uklad: str | None = None
    typ: str | None = None  # wieczorna / poranna / None (uklad nieznany)
    czas: str | None = None  # chwila przyjecia skanu przez program
    zmiana: int | None = None
    czas_s: float | None = None
    sha16: str | None = None  # skrot pliku skanu
    gniazda: tuple = ()
    poza_gniazdem: tuple = ()
    liczniki: dict = dataclasses.field(default_factory=ZamrozonySlownik)  # klasa koloru -> liczba prac (tylko do odczytu)
    zielonych: int = 0
    zastepuje_id: int | None = None
    moze_zastapic: int | None = None
    dopuszczona: bool = False
    dozwolone: tuple = ()
    komunikaty: tuple = ()
    pytania: tuple = ()

    def gniazdo(self, nr: int) -> Gniazdo | None:
        return next((g for g in self.gniazda if g.nr == nr), None)

    @property
    def prace(self) -> tuple:
        return tuple(p for g in self.gniazda for p in g.prace) + tuple(self.poza_gniazdem)


@dataclasses.dataclass(frozen=True)
class PozycjaListy:
    """Pozycja listy "do dofrezowania". ``powtorzenia`` = ile innych prac tego samego projektu tez oznaczono "Ukruszona"."""

    praca_id: int
    skan_id: int
    numer_plytki: int | None
    gniazdo: int | None
    kuweta: str | None
    zeby: str | None
    krazek: str | None
    sha16: str | None
    doba: str
    zmiana: int
    operator: str | None = None
    czas: str | None = None
    decyzja: str | None = None
    ubytki: int | None = None
    ubytek_max_mm: float | None = None
    powtorzenia: int = 0


@dataclasses.dataclass(frozen=True)
class Postep:
    """Postep trwajacej analizy: ``etap`` (nazwa z ``porownaj``), ``udzial`` 0-1, ``od`` = czas startu (time.time())."""

    zadanie_id: int
    etap: str = ""
    udzial: float = 0.0
    od: float = 0.0
    sha16: str | None = None


@dataclasses.dataclass(frozen=True)
class Kolejka:
    """Skany czekajace na analize: ``w_toku`` (0 / 1), ``czeka`` (w kolejce silnika), ``wstrzymane`` (czekaja na pule
    projektow, na silnik albo na zapis wyniku), ``razem``. ``niezapisane`` (czesc ``wstrzymane``) = wyniki i bledy analizy,
    ktorych nie udalo sie jeszcze zapisac w bazie (lista: ``StanAplikacji.niezapisane``)."""

    w_toku: int = 0
    czeka: int = 0
    wstrzymane: int = 0
    silnik_gotowy: bool = False
    niezapisane: int = 0

    @property
    def razem(self) -> int:
        return self.w_toku + self.czeka + self.wstrzymane


@dataclasses.dataclass(frozen=True)
class Pula:
    """Pula projektow na poziomie 1 planu: folder + wspolczynnik wpisany recznie (None = domyslny dla typu plytki).
    ``stan`` (``STANY_PULI``): nieustawiona / liczenie / gotowa / pusta / brak_folderu; ``liczba_stl`` None = jeszcze nie
    policzono. Pula jest liczona od nowa (w tle) po kazdym nowym skanie i wyniku; gdy folder oprozniono albo zniknal, stan
    przechodzi na ``pusta`` / ``brak_folderu``, a skany czekaja (``kolejka.wstrzymane``) zamiast dostac blad analizy (P3)."""

    folder: str | None = None
    wspolczynnik: float | None = None
    liczba_stl: int | None = None
    stan: str = "nieustawiona"
    napis: str = ""
    odswiezono: str | None = None


@dataclasses.dataclass(frozen=True)
class Skaner:
    folder: str | None = None
    dostepny: bool = False
    dziala: bool = False
    zajete: int = 0  # pliki, na ktorych zwolnienie czeka obserwator
    ostatni_start_skanu: str | None = None
    startow_skanu: int = 0
    czeka_na_skan: bool = False  # po "start skanu", do pierwszego nowego pliku


@dataclasses.dataclass(frozen=True)
class Niezapisany:
    """Skan, ktorego wynik (albo blad) analizy jest policzony, ale NIE zapisany w bazie (P1, P8): skan nie przepadl - czeka
    w pamieci, program ponawia zapis sam (z rosnacym odstepem) i na polecenie ``ponow_zapis``. Okno pokazuje go jako
    pozycje "nie zapisano" (``napis``) obok plytek. ``przyczyna``: ``blad_zapisu`` (dysk pelny, blad wejscia / wyjscia,
    dysk odlaczony - komunikat trwaly ``blad_zapisu``) albo ``baza_zajeta`` (inny program trzyma baze - komunikat
    ``baza_zajeta``). ``rodzaj``: ``wynik`` / ``blad``. ``numer``, ``uklad``, ``prac`` - z wyniku analizy (None dla bledu)."""

    sha16: str
    rodzaj: str
    przyczyna: str
    napis: str
    od: str = ""
    proby: int = 0
    numer: int | None = None
    uklad: str | None = None
    prac: int | None = None


@dataclasses.dataclass(frozen=True)
class StanAplikacji:
    """Caly stan ekranu wieczornego. ``wersja`` rosnie przy kazdej zmianie. ``plytki`` - skany biezacej doby roboczej
    w kolejnosci przyjecia; ``biezaca_plytka`` - skan_id ostatniej plytki. ``komunikaty`` i ``pytania`` - wszystko, co
    wymaga uwagi technika teraz (takze przypiete do plytek; zamkniete przez technika - nie). ``niezapisane`` - skany
    policzone, ale jeszcze niezapisane w bazie (``Niezapisany``). ``lista_zapisana`` - kiedy kontroler ostatnio zapisal
    plik listy "do dofrezowania" (zapis samoczynny po kazdej zmianie listy; ``zapisz_liste``)."""

    wersja: int = 0
    czas: str = ""
    tryb: str = TRYB_WIECZOR
    doba: str = ""
    zmiana: int = 0
    operator: str | None = None
    operatorzy: tuple = ()
    wymaga_operatora: bool = True
    plytki: tuple = ()
    biezaca_plytka: int | None = None
    liczniki: dict = dataclasses.field(default_factory=ZamrozonySlownik)  # tylko do odczytu (D2)
    prac: int = 0
    do_dofrezowania: tuple = ()  # pozycje tej doby
    do_dofrezowania_biezaca: tuple = ()  # wszystkie otwarte, takze z poprzednich dob
    pytania: tuple = ()
    komunikaty: tuple = ()
    konflikty: tuple = ()  # slowniki tylko do odczytu (``ZamrozonySlownik``; ``miejsca`` - krotka)
    analiza: Postep | None = None
    kolejka: Kolejka = Kolejka()
    pula: Pula = Pula()
    skaner: Skaner = Skaner()
    zamkniety: bool = False
    niezapisane: tuple = ()
    lista_zapisana: str | None = None

    def plytka(self, skan_id: int) -> Plytka | None:
        return next((p for p in self.plytki if p.skan_id == skan_id), None)

    def praca(self, praca_id: int) -> Praca | None:
        return next((x for p in self.plytki for x in p.prace if x.praca_id == praca_id), None)


@dataclasses.dataclass(frozen=True)
class SzczegolyPracy:
    """Widok pracy po kliknieciu gniazda: ``ubytki`` (slowniki z pliku wyniku: x, y, z, srednica_mm, glebokosc_mm, metoda,
    kolor, na_krawedzi; slowniki tylko do odczytu), ``uwagi`` programu, ``kandydaci`` (sha16, zeby, typ, pokrycie) oraz
    ``plik_podgladu`` - plik ``*_podglad.npz`` (``kontroler_api.wczytaj_podglad``: gniazdo -> punkty i odchylki do obrazu
    odchylek) albo None."""

    praca: Praca
    ubytki: tuple = ()
    uwagi: tuple = ()
    kandydaci: tuple = ()
    plik_podgladu: Path | None = None


@dataclasses.dataclass(frozen=True)
class ZdarzenieKontrolera:
    """Sygnal kontrolera do okna. ``typ``: ``stan`` (nowy ``stan``), ``postep`` (``postep`` + ``stan``), ``komunikat``
    (nowy ``komunikat``), ``pytanie`` (nowe ``pytanie``), ``zamkniety``."""

    typ: str
    stan: StanAplikacji | None = None
    komunikat: Komunikat | None = None
    pytanie: Pytanie | None = None
    postep: Postep | None = None


# ----------------------------------------------------------------------------
# interfejs kontrolera
# ----------------------------------------------------------------------------
class Kontroler:
    """Interfejs, ktory widzi okno. Implementacje: ``aplikacja.Aplikacja`` (prawdziwa) i ``AtrapaKontrolera``."""

    # --- stan i sygnaly
    def stan(self) -> StanAplikacji:
        raise NotImplementedError

    def subskrybuj(self, funkcja: Callable[[ZdarzenieKontrolera], None]) -> None:
        raise NotImplementedError

    def odsubskrybuj(self, funkcja: Callable[[ZdarzenieKontrolera], None]) -> None:
        raise NotImplementedError

    def przetworz(self, limit_s: float = LIMIT_PRZETWARZANIA_S) -> int:
        """Obsluguje zdarzenia czekajace w kolejkach (skaner, silnik, zegar zmiany); zwraca liczbe obsluzonych."""
        raise NotImplementedError

    def szczegoly_pracy(self, praca_id: int) -> SzczegolyPracy | None:
        raise NotImplementedError

    # --- polecenia okna (kazde zwraca Odpowiedz)
    def wybierz_operatora(self, nazwa: str) -> Odpowiedz:
        raise NotImplementedError

    def ukruszona(self, praca_id: int) -> Odpowiedz:
        raise NotImplementedError

    def ok(self, praca_id: int) -> Odpowiedz:
        raise NotImplementedError

    def cofnij(self, praca_id: int) -> Odpowiedz:
        raise NotImplementedError

    def potwierdz_ponowny_skan(self, skan_id: int) -> Odpowiedz:
        raise NotImplementedError

    def odrzuc_ponowny_skan(self, skan_id: int) -> Odpowiedz:
        raise NotImplementedError

    def cofnij_zastapienie(self, skan_id: int) -> Odpowiedz:
        raise NotImplementedError

    def dopusc_plytke(self, skan_id: int) -> Odpowiedz:
        raise NotImplementedError

    def cofnij_dopuszczenie(self, skan_id: int) -> Odpowiedz:
        raise NotImplementedError

    def podaj_numer_plytki(self, skan_id: int, numer: int) -> Odpowiedz:
        raise NotImplementedError

    def zamknij_pytanie(self, pytanie_id: str) -> Odpowiedz:
        raise NotImplementedError

    def zamknij_komunikat(self, komunikat_id: str) -> Odpowiedz:
        raise NotImplementedError

    def start_skanu(self) -> Odpowiedz:
        raise NotImplementedError

    def ustaw_pule(self, folder: str | None, wspolczynnik: float | None = None) -> Odpowiedz:
        raise NotImplementedError

    def odswiez_pule(self) -> Odpowiedz:
        raise NotImplementedError

    def zamknij(self) -> Odpowiedz:
        raise NotImplementedError

    def zapisz_liste(self, doba: str | None = None) -> Odpowiedz:
        """17. polecenie (P7, Z6): lista "do dofrezowania" do pliku w folderze danych programu (bez nazw zlecen); bez ``doba``
        lista biezaca (``do_dofrezowania_biezaca.csv`` - ten sam plik, ktory kontroler zapisuje sam po kazdej zmianie listy),
        z ``doba`` (``RRRR-MM-DD``) pozycje tej doby. ``dane`` = nazwa pliku (bez sciezki)."""
        raise NotImplementedError

    def ponow_zapis(self) -> Odpowiedz:
        """18. polecenie (P1): od razu ponawia zapis wynikow, ktorych nie udalo sie zapisac (``stan.niezapisane``).
        ``ok`` True = nic juz nie czeka; ``dane`` = ile pozycji czeka nadal."""
        raise NotImplementedError

    def wykonaj(self, polecenie: str, *argumenty: Any) -> Odpowiedz:
        """Polecenie po nazwie (``POLECENIA``) - dla przyciskow z ``Pytanie.odpowiedzi``. Nieznana nazwa = odmowa ``odmowa``,
        zla liczba argumentow = odmowa ``zle_argumenty`` - nigdy wyjatek (D1)."""
        if not isinstance(polecenie, str) or polecenie not in POLECENIA:
            return Odpowiedz(False, f"nieznane polecenie {polecenie!r}", "odmowa")
        funkcja = getattr(self, polecenie)
        try:
            inspect.signature(funkcja).bind(*argumenty)
        except TypeError:
            return self._zle_argumenty(polecenie)
        return funkcja(*argumenty)

    def _zle_argumenty(self, polecenie: str) -> Odpowiedz:
        return Odpowiedz(False, ST.tekst_komunikatu(KOD_ZLE_ARGUMENTY, polecenie=polecenie)[2], KOD_ZLE_ARGUMENTY)


def wczytaj_podglad(plik) -> dict:
    """Obraz odchylek dla okna (D12): plik ``SzczegolyPracy.plik_podgladu`` -> {numer gniazda: (punkty N x 3 w ukladzie
    plytki, odchylka kazdego punktu w mm)}. Cienka nakladka na ``silnik.wczytaj_podglad`` - okno nie importuje ``silnik``;
    numpy jest ladowane dopiero tutaj (kontrakt nie laduje go przy imporcie)."""
    from . import silnik as SI  # noqa: PLC0415 - modul silnika sam laduje tylko biblioteke standardowa

    return SI.wczytaj_podglad(plik)


def lacznik_qt(kontroler: Kontroler, okres_ms: int = OKRES_LACZNIKA_MS, rodzic=None):
    """Obiekt Qt dla okna: sygnaly ``stan_zmieniony(object)`` (``StanAplikacji``), ``postep(object)`` (``Postep`` albo
    None), ``komunikat(object)``, ``pytanie(object)``, ``zamkniety()`` oraz zegar, ktory co ``okres_ms`` wola
    ``kontroler.przetworz()`` w watku okna. ``zatrzymaj()`` wylacza zegar. PySide6 jest importowane dopiero tutaj."""
    from PySide6.QtCore import QObject, QTimer, Signal

    class LacznikKontrolera(QObject):
        stan_zmieniony = Signal(object)
        postep = Signal(object)
        komunikat = Signal(object)
        pytanie = Signal(object)
        zamkniety = Signal()

        def __init__(self, kontroler_: Kontroler, okres_ms_: int, rodzic_=None):
            super().__init__(rodzic_)
            self.kontroler = kontroler_
            kontroler_.subskrybuj(self._odbierz)
            self._zegar = QTimer(self)
            self._zegar.setInterval(okres_ms_)
            self._zegar.timeout.connect(self._tyk)
            self._zegar.start()

        def _tyk(self) -> None:
            self.kontroler.przetworz()

        def _odbierz(self, z: ZdarzenieKontrolera) -> None:
            if z.typ == "stan":
                self.stan_zmieniony.emit(z.stan)
            elif z.typ == "postep":
                self.postep.emit(z.postep)
            elif z.typ == "komunikat":
                self.komunikat.emit(z.komunikat)
            elif z.typ == "pytanie":
                self.pytanie.emit(z.pytanie)
            elif z.typ == "zamkniety":
                self.zamkniety.emit()

        def zatrzymaj(self) -> None:
            self._zegar.stop()
            self.kontroler.odsubskrybuj(self._odbierz)

    return LacznikKontrolera(kontroler, okres_ms, rodzic)


# ----------------------------------------------------------------------------
# wspolna czesc kontrolera: stan z ``session`` i polecenia o decyzjach
# ----------------------------------------------------------------------------
class KontrolerSesji(Kontroler):
    """Kontroler na otwartej ``Sesja``: buduje ``StanAplikacji`` ze ``stan_wieczoru`` i wykonuje polecenia o decyzjach.

    Klasa pochodna dostarcza czesc "zywa": ``_stan_zywy()`` (postep, kolejka, pula, skaner), ``przetworz``,
    ``start_skanu``, ``ustaw_pule``, ``odswiez_pule``, ``zamknij``. ``ust`` - ustawienia (katalogi ukladow plytek);
    ``zegar`` - do testow (ten sam co w ``Sesja``).

    Reguly ponad ``session`` (opis: ``opisy_modulow/aplikacja.md``):
    * operator jest wybierany na ZMIANE: po zmianie numeru zmiany wybor wygasa i trzeba wskazac osobe ponownie (DW3);
      ``wybierz_operatora(None)`` = nikt nie jest wybrany (D7);
    * "Ukruszona" na pracy, ktorej program nie oznaczyl na czerwono, zapisuje sie jako ``ukruszona_niewykryta`` (SE9);
    * plytka bez numeru: prace zielone maja status ``czeka_na_numer`` (nic zielonego) do podania numeru;
    * praca zielona tylko przy inspekcji "ok" i znanym dopasowaniu (P4, ``statusy.status_pracy`` / ``kolor_pracy``);
    * odrzucenie propozycji ponownego skanu ("to nowy wsad") jest zapisywane w dzienniku i nie wraca po restarcie;
    * lista "do dofrezowania" jest zapisywana do pliku w folderze bazy po kazdej zmianie listy (P7, Z6).
    """

    def __init__(self, sesja: SE.Sesja, ust: dict | None = None, *, tryb: str = TRYB_WIECZOR, zegar: Callable[[], dt.datetime] | None = None):
        self.sesja = sesja
        self.ust = ust
        self.tryb = SE.sprawdz_tryb(tryb)
        self._zegar = zegar or dt.datetime.now
        self._subskrybenci: list = []
        self._do_wyslania: collections.deque = collections.deque()
        self._stan: StanAplikacji | None = None
        self._wersja = 0
        self._zamkniety = False
        self._komunikaty: dict[str, Komunikat] = {}  # ulotne (nie wynikaja ze stanu skanow)
        self._nr_komunikatu = 0
        self._ukryte: set[str] = set()  # komunikaty i pytania zamkniete przez technika (do konca pracy programu)
        self._ogloszone: set[str] = set()  # komunikaty trwale i pytania, o ktorych okno juz dostalo sygnal
        self._uklady: dict[str, tuple] = {}
        self._szczegoly: dict[int, dict] = {}  # skan_id -> tresc pliku wyniku (pamiec podreczna)
        self._zmiana_operatora: tuple | None = None  # (doba, zmiana), na ktora wybrano operatora
        self._ostatnia_zmiana: tuple | None = None
        self._lista_zapisana: tuple | None = None  # pozycje listy biezacej z ostatniego udanego zapisu pliku (P7)
        self._lista_czas: str | None = None
        self._lista_blad = False
        self._odrzucone = self._wczytaj_odrzucone()

    # --- sygnaly ---------------------------------------------------------------------------------
    def subskrybuj(self, funkcja: Callable[[ZdarzenieKontrolera], None]) -> None:
        if funkcja not in self._subskrybenci:
            self._subskrybenci.append(funkcja)

    def odsubskrybuj(self, funkcja: Callable[[ZdarzenieKontrolera], None]) -> None:
        if funkcja in self._subskrybenci:
            self._subskrybenci.remove(funkcja)

    def _powiadom(self, typ: str, **pola: Any) -> None:
        """Sygnal do subskrybentow. Sygnaly ida przez jedna kolejke w kolejnosci powstania - takze gdy odbiorca w trakcie
        obslugi sygnalu wywola polecenie albo ``przetworz`` (zagniezdzona petla okna): nowsze sygnaly nie wyprzedzaja starszych."""
        self._do_wyslania.append(ZdarzenieKontrolera(typ=typ, **pola))
        while self._do_wyslania:
            z = self._do_wyslania.popleft()
            for f in list(self._subskrybenci):
                try:
                    f(z)
                except Exception:  # noqa: BLE001 - blad okna nie moze zatrzymac kontrolera
                    LOG.exception("kontroler: blad odbiorcy sygnalu %s", z.typ)

    # --- stan ------------------------------------------------------------------------------------
    def stan(self) -> StanAplikacji:
        if self._stan is None:
            self._stan = self._zbuduj()
        return self._stan

    def _odswiez(self) -> StanAplikacji:
        """Stan od nowa z bazy + sygnaly: ``stan``, potem ``komunikat`` / ``pytanie`` dla kazdej nowej pozycji."""
        if self._zamkniety:
            return self.stan()
        try:
            self._stan = stan = self._zbuduj()
        except Exception as e:  # noqa: BLE001 - baza zajeta, blad dysku: zostaje poprzedni stan, nastepne odswiezenie go nadrobi
            if isinstance(e, B.BladBazy):
                LOG.warning("kontroler: baza zajeta - stan nie zostal odswiezony")
            else:
                LOG.exception("kontroler: stanu nie da sie odczytac z bazy - zostaje poprzedni")
            if self._stan is None:
                raise
            return self._stan
        self._powiadom("stan", stan=stan)
        for k in stan.komunikaty:
            if k.id not in self._ogloszone:
                self._ogloszone.add(k.id)
                self._powiadom("komunikat", komunikat=k, stan=stan)
        for p in stan.pytania:
            if p.id not in self._ogloszone:
                self._ogloszone.add(p.id)
                self._powiadom("pytanie", pytanie=p, stan=stan)
        return stan

    def _odswiez_zywe(self, sygnal: str = "stan") -> None:
        """Podmienia w stanie tylko czesc "zywa" (postep, kolejka, pula, skaner) - bez czytania bazy."""
        if self._stan is None or self._zamkniety:
            return
        self._wersja += 1
        self._stan = dataclasses.replace(self._stan, wersja=self._wersja, **self._stan_zywy())
        if sygnal == "postep":
            self._powiadom("postep", postep=self._stan.analiza, stan=self._stan)
        else:
            self._powiadom("stan", stan=self._stan)

    def _stan_zywy(self) -> dict:
        """Pola ``analiza``, ``kolejka``, ``pula``, ``skaner`` stanu - nadpisuje klasa pochodna."""
        return {}

    def _teraz(self) -> str:
        return self._zegar().replace(microsecond=0).isoformat()

    def _sprawdz_zmiane(self) -> bool:
        """Wybor operatora obowiazuje do konca zmiany; zwraca True, gdy zmienila sie doba albo zmiana."""
        biezaca = (self.sesja.doba(), self.sesja.zmiana())
        zmieniona = self._ostatnia_zmiana is not None and biezaca != self._ostatnia_zmiana
        self._ostatnia_zmiana = biezaca
        if self.sesja.operator is not None and self._zmiana_operatora is not None and self._zmiana_operatora != biezaca:
            self.sesja.operator = None
            self._zmiana_operatora = None
            self._komunikat("nowa_zmiana", zmiana=biezaca[1])
        return zmieniona

    def przetworz(self, limit_s: float = LIMIT_PRZETWARZANIA_S) -> int:
        if self._zamkniety:
            return 0
        if self._sprawdz_zmiane():
            self._odswiez()
            return 1
        return 0

    def _uklad(self, nazwa: str | None) -> tuple:
        """(numery gniazd, numery plytek) ukladu ``nazwa``; ((), ()) gdy ukladu nie da sie wczytac."""
        if not nazwa:
            return (), ()
        if nazwa not in self._uklady:
            try:
                from . import uklad as U  # numpy: Aplikacja laduje uklady w start(), atrapa - przy pierwszej plytce

                katalog = None
                if self.ust is not None and nazwa in (self.ust.get("plytki") or {}):
                    from . import ustawienia as UST

                    katalog = UST.katalog_plytki(self.ust, nazwa)
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    uk = U.wczytaj(nazwa, katalog)
                self._uklady[nazwa] = (tuple(sorted(g.id for g in uk.sockets)), tuple(sorted(uk.numery)))
            except Exception as e:  # noqa: BLE001 - mapa bez pustych gniazd jest lepsza niz brak stanu
                LOG.warning("kontroler: ukladu %s nie da sie wczytac (%s) - mapa bez pustych gniazd", nazwa, type(e).__name__)
                self._uklady[nazwa] = ((), ())
        return self._uklady[nazwa]

    def _wynik_skanu(self, skan_id: int) -> dict:
        """Tresc pliku wyniku skanu (zapisanego przez ``session``, bez sciezek i nazw z puli); {} gdy go nie ma."""
        if skan_id not in self._szczegoly:
            tresc: dict = {}
            try:
                plik = self.sesja.sciezka_wyniku(skan_id)
                if plik is not None and plik.is_file():
                    tresc = json.loads(plik.read_text(encoding="utf-8"))
            except (OSError, ValueError) as e:
                LOG.warning("kontroler: pliku wyniku skanu %s nie da sie odczytac (%s)", skan_id, type(e).__name__)
            self._szczegoly[skan_id] = tresc if isinstance(tresc, dict) else {}
        return self._szczegoly[skan_id]

    def _inspekcje(self, skan_id: int) -> dict:
        """(gniazdo, nr fragmentu w gniezdzie) -> wpis gniazda z pliku wyniku."""
        wynik: dict = {}
        licznik: dict = {}
        for g in self._wynik_skanu(skan_id).get("gniazda") or []:
            licznik[g.get("gniazdo")] = licznik.get(g.get("gniazdo"), 0) + 1
            wynik[(g.get("gniazdo"), licznik[g.get("gniazdo")])] = g
        return wynik

    def _zbuduj(self) -> StanAplikacji:
        sw = self.sesja.stan_wieczoru()
        self._wersja += 1
        self._ostatnia_zmiana = (sw["data"], sw["zmiana"])
        biezaca = sw["do_dofrezowania_biezaca"]
        lista_biezaca = tuple(self._pozycja(x) for x in biezaca)
        self._zapisz_liste_po_zmianie(lista_biezaca)  # P7: plik listy po kazdej zmianie listy (przed zebraniem komunikatow)
        po_projekcie = {x["projekt_id"]: x for x in biezaca if x["projekt_id"] is not None}
        po_pracy = {x["praca_id"]: x for x in biezaca}
        propozycje = {p["skan_id"]: p for p in sw["do_potwierdzenia"]}
        czasy = {s["id"]: s["czas_analizy"] for s in sw["skany"]}
        for skan_id in set(self._szczegoly) - set(czasy):  # D10: tresc plikow wynikow tylko dla plytek biezacej doby
            del self._szczegoly[skan_id]
        plytki, pytania, trwale = [], [], []
        for s in sw["skany"]:
            plytka = self._plytka(s, po_projekcie, po_pracy, propozycje.get(s["id"]), czasy)
            plytki.append(plytka)
            pytania += [p for p in plytka.pytania if not p.ukryte]
            trwale += [k for k in plytka.komunikaty if not k.ukryte]
        if sw["konflikty"]:
            skladowe = self._skladowe_oczekujacych([(skan_id, p["poprzedni_id"]) for skan_id, p in propozycje.items()
                                                    if (skan_id, p["poprzedni_id"]) not in self._odrzucone])
            for k in sw["konflikty"]:
                id_ = f"konflikt_projektu:{k['sha16']}"
                if id_ not in self._ukryte and not self._konflikt_ponownego_skanu(k, skladowe):
                    trwale.append(self._nowy_komunikat(id_, "konflikt_projektu", trwaly=True, czas=sw["data"], miejsc=len(k["miejsca"])))
        komunikaty = sorted(list(self._komunikaty.values()) + trwale, key=lambda k: (k.czas, k.id))
        aktywne = [p.skan_id for p in plytki]
        liczniki: dict[str, int] = {}  # po klasie koloru, tylko plytki aktywne (plytka bez numeru nie ma zielonych)
        for p in plytki:
            if p.aktywna:
                for kolor, n in p.liczniki.items():
                    liczniki[kolor] = liczniki.get(kolor, 0) + n
        return StanAplikacji(
            wersja=self._wersja, czas=self._teraz(), tryb=self.tryb, doba=sw["data"], zmiana=sw["zmiana"] or self.sesja.zmiana(),
            operator=self.sesja.operator, operatorzy=tuple(self.sesja.operatorzy), wymaga_operatora=self.sesja.operator is None,
            plytki=tuple(plytki), biezaca_plytka=aktywne[-1] if aktywne else None, liczniki=zamroz(liczniki), prac=sw["prac"],
            do_dofrezowania=tuple(self._pozycja(x) for x in sw["do_dofrezowania"]),
            do_dofrezowania_biezaca=lista_biezaca,
            pytania=tuple(pytania), komunikaty=tuple(komunikaty), konflikty=zamroz(sw["konflikty"]), zamkniety=self._zamkniety,
            lista_zapisana=self._lista_czas, **self._stan_zywy())

    @staticmethod
    def _skladowe_oczekujacych(pary: list) -> dict:
        """skan_id -> numer spojnej skladowej grafu, ktorego krawedzie to pary (skan czekajacy na odpowiedz "to ponowny skan?",
        skan, ktory proponuje zastapic). Ta sama plytka zeskanowana trzy razy bez odpowiedzi (A, B, C: pytania B -> A i C -> B)
        to jedna skladowa (recenzja PR #22 P1)."""
        sasiedzi: dict = {}
        for a, b in pary:
            sasiedzi.setdefault(a, set()).add(b)
            sasiedzi.setdefault(b, set()).add(a)
        skladowe: dict = {}
        for start in sasiedzi:
            if start in skladowe:
                continue
            stos = [start]
            while stos:
                skan = stos.pop()
                if skan not in skladowe:
                    skladowe[skan] = start
                    stos.extend(sasiedzi[skan] - skladowe.keys())
        return skladowe

    @staticmethod
    def _konflikt_ponownego_skanu(konflikt: dict, skladowe: dict) -> bool:
        """Konflikt projektu TYLKO miedzy skanami jednej plytki czekajacymi na odpowiedz "to ponowny skan?" (wszystkie skany
        konfliktu w jednej spojnej skladowej grafu par czekajacych - ``_skladowe_oczekujacych``, po jednym miejscu w kazdym) - to
        ta sama praca zeskanowana drugi raz, nie dwa gniazda wieczoru: komunikat nie trafia na pasek bledow (decyzja wlasciciela
        18.11.2026, E3-A1p; trzy skany i wiecej - recenzja PR #22 P1). Po "Nie, to nowy wsad" skan wypada ze skladowej i konflikt
        wraca, po "Tak" znika (skan zastapiony); "Pozniej" to nie odpowiedz. Konflikt z innym skanem albo w obrebie jednego skanu -
        bez zmian (komunikat). ``stan.konflikty`` podaje wszystkie konflikty jak dotad."""
        miejsca: dict = {}
        for m in konflikt["miejsca"]:
            miejsca.setdefault(m["skan_id"], set()).add(m["gniazdo"] if m["gniazdo"] is not None else f"poza-{m['praca_id']}")
        numery = {skladowe.get(skan_id) for skan_id in miejsca}
        return len(miejsca) > 1 and len(numery) == 1 and None not in numery and all(len(g) == 1 for g in miejsca.values())

    # --- lista "do dofrezowania" w pliku (P7, zalozenie Z6) ----------------------------------------
    def _katalog_listy(self) -> Path | None:
        """Folder pliku listy; None = folder bazy (``dane/``), jak ``session.zapisz_do_dofrezowania``."""
        return None

    def _zapisz_liste_po_zmianie(self, pozycje: tuple) -> None:
        """Zapis samoczynny: plik ``do_dofrezowania_biezaca.csv`` (kuweta, zeby, krazek, plytka, gniazdo, skrot projektu, doba,
        zmiana - bez nazw zlecen), gdy lista rozni sie od ostatnio zapisanej. Blad dysku: komunikat ``lista_nie_zapisana``
        (raz na serie bledow); kolejna proba przy nastepnej zmianie listy albo na polecenie ``zapisz_liste``."""
        if pozycje == self._lista_zapisana or self._zamkniety:
            return
        try:
            self.sesja.zapisz_do_dofrezowania(None, katalog=self._katalog_listy())
        except (OSError, sqlite3.Error, B.BladBazy) as e:
            LOG.warning("kontroler: listy do dofrezowania nie da sie zapisac do pliku (%s)", type(e).__name__)
            if not self._lista_blad:
                self._lista_blad = True
                self._komunikat("lista_nie_zapisana", id_="lista_nie_zapisana")
            return
        self._lista_zapisana, self._lista_czas, self._lista_blad = pozycje, self._teraz(), False
        self._usun_komunikat("lista_nie_zapisana")

    @staticmethod
    def _pozycja(x: dict) -> PozycjaListy:
        return PozycjaListy(praca_id=x["praca_id"], skan_id=x["skan_id"], numer_plytki=x["numer_plytki"], gniazdo=x["gniazdo"], kuweta=x["kuweta"],
                            zeby=x["zeby"], krazek=x["krazek"], sha16=x["sha16"], doba=x["doba"], zmiana=x["zmiana"], operator=x["operator"],
                            czas=x["czas"], decyzja=x["decyzja"], ubytki=x["ubytki"], ubytek_max_mm=x["ubytek_max_mm"],
                            powtorzenia=len(x["powtorzenia"]))

    def _praca(self, s: dict, p: dict, po_projekcie: dict, po_pracy: dict, inspekcje: dict | None, numer_znany: bool) -> Praca:
        blad = False
        if p["status_inspekcji"] == "nie_sprawdzono" and inspekcje is not None:
            wpis = inspekcje.get((p["gniazdo"], p["nr_fragmentu"])) or {}
            blad = bool((wpis.get("inspekcja") or {}).get("blad"))
        klucz = ST.status_pracy(p["kolor"], status_skanu=s["status"], status_gniazda=p["status_gniazda"], status_inspekcji=p["status_inspekcji"],
                                decyzja=p["decyzja"], blad_inspekcji=blad, numer_znany=numer_znany,
                                status_match=p["status_match"] if p["status_match"] is not None else "brak")
        st = ST.status(klucz)
        kolor = ST.kolor_pracy(p["kolor"], klucz)  # P4: zielony tylko przy statusie zielonym; plytka bez numeru: nic zielonego
        pozycja = po_projekcie.get(p["projekt_id"]) if p["projekt_id"] is not None else po_pracy.get(p["id"])
        na_liscie = None
        if pozycja is not None and s["aktywny"]:
            na_liscie = NaLiscie(praca_id=pozycja["praca_id"], skan_id=pozycja["skan_id"], doba=pozycja["doba"], zmiana=pozycja["zmiana"],
                                 ta_praca=pozycja["praca_id"] == p["id"],
                                 tekst="" if pozycja["praca_id"] == p["id"] else ST.ZAB_JUZ_NA_LISCIE.format(doba=pozycja["doba"], zmiana=pozycja["zmiana"]))
        dozwolone: tuple = ()
        if s["status"] == SE.STATUS_PRZYJETY and self.tryb == TRYB_WIECZOR:
            if p["decyzja"] is None:
                dozwolone = ("ukruszona", "ok")
            elif p["decyzja"] in ST.DECYZJE_UKRUSZENIA:
                dozwolone = ("ok", "cofnij")
            else:
                dozwolone = ("ukruszona", "cofnij")
        return Praca(
            praca_id=p["id"], skan_id=s["id"], gniazdo=p["gniazdo"], status=klucz, kolor=kolor, rgb=st.hex, podpis=st.napis, opis=st.opis,
            nr_fragmentu=p["nr_fragmentu"], status_programu=p["status_gniazda"], status_inspekcji=p["status_inspekcji"],
            status_match=p["status_match"], decyzja=p["decyzja"], operator=p["operator"], czas_decyzji=p["czas_decyzji"], sha16=p["sha16"],
            kuweta=p["kuweta"], zeby=p["zeby"], krazek=p["krazek"], pewnosc=p["pewnosc"], pokrycie=p["kandydat1_pokrycie"], ubytki=p["ubytki"],
            ubytek_max_mm=p["ubytek_max_mm"], blad_inspekcji=blad, na_liscie=na_liscie, dozwolone=dozwolone)

    def _plytka(self, s: dict, po_projekcie: dict, po_pracy: dict, propozycja: dict | None, czasy: dict) -> Plytka:
        numer_znany = s["numer_plytki"] is not None
        nie_sprawdzone = any(p["status_inspekcji"] == "nie_sprawdzono" for p in s["prace"])
        inspekcje = self._inspekcje(s["id"]) if nie_sprawdzone else None
        prace = [self._praca(s, p, po_projekcie, po_pracy, inspekcje, numer_znany) for p in s["prace"]]
        w_gniazdach: dict[int, list[Praca]] = {}
        poza = []
        for p in prace:
            if p.gniazdo is None:
                poza.append(dataclasses.replace(p, status="poza_gniazdem", rgb=ST.status("poza_gniazdem").hex,
                                                podpis=ST.status("poza_gniazdem").napis, opis=ST.status("poza_gniazdem").opis))
            else:
                w_gniazdach.setdefault(p.gniazdo, []).append(p)
        numery_gniazd, numery_plytek = self._uklad(s["uklad"])
        gniazda = []
        for nr in sorted(set(numery_gniazd) | set(w_gniazdach)):
            lista = w_gniazdach.get(nr, [])
            if not lista:
                st = ST.status("pusty")
                gniazda.append(Gniazdo(nr=nr, status="pusty", kolor=None, rgb=st.hex, podpis=st.napis))
            elif len(lista) > 1 and s["aktywny"]:
                st = ST.status("podwojny")
                gniazda.append(Gniazdo(nr=nr, status="podwojny", kolor=None, rgb=st.hex, podpis=st.napis, prace=tuple(lista)))
            else:
                p = lista[0]
                gniazda.append(Gniazdo(nr=nr, status=p.status, kolor=p.kolor, rgb=p.rgb, podpis=p.podpis, prace=tuple(lista)))
        liczniki: dict[str, int] = {}
        for p in prace:
            if p.kolor is not None:
                liczniki[p.kolor] = liczniki.get(p.kolor, 0) + 1
        typ = SE.typ_plytki(s["uklad"])
        dopuszczona = bool(s["aktywny"] and s["uklad"] and SE.powod_nie_z_trybu(s["uklad"], self.tryb) is not None)
        dozwolone = []
        if s["aktywny"]:
            dozwolone.append("podaj_numer_plytki")
        if s["moze_zastapic"] is not None:
            dozwolone += ["potwierdz_ponowny_skan", "odrzuc_ponowny_skan"]
        if s["aktywny"] and s["zastepuje_id"] is not None:
            dozwolone.append("cofnij_zastapienie")
        if s["status"] == SE.STATUS_PLYTKA_NIE_Z_TRYBU:
            dozwolone.append("dopusc_plytke")
        if dopuszczona:
            dozwolone.append("cofnij_dopuszczenie")
        komunikaty = [dataclasses.replace(k, ukryte=True) if k.id in self._ukryte else k for k in self._komunikaty_plytki(s, prace)]
        pytania = [dataclasses.replace(q, ukryte=True) if q.id in self._ukryte else q
                   for q in self._pytania_plytki(s, propozycja, czasy, typ, numery_plytek)]
        return Plytka(
            skan_id=s["id"], status=s["status"], aktywna=s["aktywny"], napis=ST.napis_plytki(s["status"]), numer=s["numer_plytki"],
            numer_zrodlo=s["numer_zrodlo"], uklad=s["uklad"], typ=typ, czas=s["czas_analizy"], zmiana=s["zmiana"], czas_s=s["czas_s"],
            sha16=s["sha16"], gniazda=tuple(gniazda), poza_gniazdem=tuple(poza), liczniki=zamroz(liczniki),
            zielonych=liczniki.get(ST.KOLOR_ZIELONY, 0), zastepuje_id=s["zastepuje_id"], moze_zastapic=s["moze_zastapic"],
            dopuszczona=dopuszczona, dozwolone=tuple(dozwolone), komunikaty=tuple(komunikaty), pytania=tuple(pytania))

    def _nowy_komunikat(self, id_: str, rodzaj: str, *, trwaly: bool = False, czas: str | None = None, skan_id: int | None = None,
                        gniazda: tuple = (), **pola: Any) -> Komunikat:
        poziom, tytul, tekst = ST.tekst_komunikatu(rodzaj, **pola)
        return Komunikat(id=id_, rodzaj=rodzaj, poziom=poziom, tytul=tytul, tekst=tekst, czas=czas or self._teraz(), skan_id=skan_id,
                         gniazda=tuple(gniazda), trwaly=trwaly)

    def _komunikaty_plytki(self, s: dict, prace: list) -> list:
        """Komunikaty wynikajace ze stanu skanu (trwale): niezgodny uklad, skan do powtorzenia, blad analizy, blad inspekcji."""
        wynik = []
        czas, skan_id = s["czas_analizy"] or "", s["id"]
        if s["status"] == SE.STATUS_NIEZGODNY_UKLAD:
            wynik.append(self._nowy_komunikat(f"niezgodny_uklad:{skan_id}", "niezgodny_uklad", trwaly=True, czas=czas, skan_id=skan_id))
        elif s["status"] == SE.STATUS_BLAD:
            rodzaj = self._rodzaj_bledu(skan_id)
            if rodzaj == "plik_niedostepny":  # pliku nie dalo sie odczytac mimo ponowien: osobny komunikat z rada
                wynik.append(self._nowy_komunikat(f"plik_niedostepny:{skan_id}", "plik_niedostepny", trwaly=True, czas=czas, skan_id=skan_id,
                                                  dalej=ST.PLIK_NIEDOSTEPNY_KONIEC))
            else:
                wynik.append(self._nowy_komunikat(f"blad_analizy:{skan_id}", "blad_analizy", trwaly=True, czas=czas, skan_id=skan_id,
                                                  powod=ST.POWODY_BLEDU_ANALIZY.get(rodzaj, ST.POWODY_BLEDU_ANALIZY["analiza"])))
        elif s["status"] == SE.STATUS_DO_POWTORZENIA:
            powody, gniazda = [], []
            for klucz, pole, wartosc in (("skan_ponownie", "status_inspekcji", "skan_ponownie"), ("popraw_ulozenie", "status_inspekcji", "popraw_ulozenie")):
                nry = sorted({p.gniazdo for p in prace if getattr(p, pole) == wartosc and p.gniazdo is not None})
                if nry:
                    powody.append(ST.POWODY_POWTORZENIA[klucz].format(gniazda=", ".join(map(str, nry))))
                    gniazda += nry
            ile_w: dict = {}
            for p in s["prace"]:
                if p["gniazdo"] is not None:
                    ile_w[p["gniazdo"]] = ile_w.get(p["gniazdo"], 0) + 1
            podwojne = sorted(g for g, n in ile_w.items() if n > 1)
            if podwojne:
                powody.append(ST.POWODY_POWTORZENIA["podwojny"].format(gniazda=", ".join(map(str, podwojne))))
                gniazda += podwojne
            ile_poza = sum(1 for p in s["prace"] if p["gniazdo"] is None or p["status_fragmentu"] == "poza_gniazdem")
            if ile_poza:
                powody.append(ST.POWODY_POWTORZENIA["poza_gniazdem"].format(ile=ile_poza))
            wynik.append(self._nowy_komunikat(f"skan_do_powtorzenia:{skan_id}", "skan_do_powtorzenia", trwaly=True, czas=czas, skan_id=skan_id,
                                              gniazda=tuple(sorted(set(gniazda))), powody="; ".join(powody) or "skan niepewny"))
        if s["aktywny"]:
            bledne = sorted({p.gniazdo for p in prace if p.blad_inspekcji and p.gniazdo is not None})
            if bledne:
                wynik.append(self._nowy_komunikat(f"blad_inspekcji:{skan_id}", "blad_inspekcji", trwaly=True, czas=czas, skan_id=skan_id,
                                                  gniazda=tuple(bledne), nr=", ".join(map(str, bledne))))
        return wynik

    def _rodzaj_bledu(self, skan_id: int) -> str | None:
        """Rodzaj bledu silnika (``silnik.RODZAJE_BLEDU``) zapisany przez kontroler w dzienniku przy skanie ``blad``."""
        w = self.sesja.baza.wiersz("SELECT dane FROM zdarzenia WHERE skan_id = ? AND typ = 'blad_analizy_rodzaj' ORDER BY id DESC LIMIT 1", (skan_id,))
        if w and w["dane"]:
            try:
                return json.loads(w["dane"]).get("rodzaj")
            except ValueError:
                return None
        return None

    def _pytania_plytki(self, s: dict, propozycja: dict | None, czasy: dict, typ: str | None, numery_plytek: tuple) -> list:
        wynik = []
        skan_id = s["id"]
        if propozycja is not None and (skan_id, propozycja["poprzedni_id"]) not in self._odrzucone:
            n, u = propozycja["liczba_decyzji"], propozycja["liczba_ukruszonych"]
            skutek = ST.SKUTEK_BEZ_DECYZJI if n == 0 else ST.SKUTEK_Z_DECYZJAMI.format(n=n, u=u, decyzji=ST.odmiana(n, "decyzja", "decyzje", "decyzji"))
            poziom, tytul, tekst = ST.tekst_pytania("ponowny_skan", numer=s["numer_plytki"] if s["numer_plytki"] is not None else "?",
                                                    minut=self._minut_od(propozycja["poprzedni_id"], s["czas_analizy"], czasy), skutek=skutek)
            wynik.append(Pytanie(
                id=f"ponowny_skan:{skan_id}:{propozycja['poprzedni_id']}", rodzaj="ponowny_skan", skan_id=skan_id, poziom=poziom, tytul=tytul,
                tekst=tekst, poprzedni_id=propozycja["poprzedni_id"], numer_plytki=s["numer_plytki"], liczba_decyzji=n, liczba_ukruszonych=u,
                odpowiedzi=(Przycisk("potwierdz_ponowny_skan", ST.PRZYCISKI["potwierdz_ponowny_skan"], (skan_id,)),
                            Przycisk("odrzuc_ponowny_skan", ST.PRZYCISKI["odrzuc_ponowny_skan"], (skan_id,)))))
        if s["status"] == SE.STATUS_PLYTKA_NIE_Z_TRYBU:
            id_ = f"plytka_nie_z_trybu:{skan_id}"
            poziom, tytul, tekst = ST.tekst_pytania("plytka_nie_z_trybu", jaka=ST.JAKA_PLYTKA.get(typ, ST.JAKA_PLYTKA[None]),
                                                    tryb=ST.NAZWY_TRYBOW.get(self.tryb, self.tryb))
            wynik.append(Pytanie(id=id_, rodzaj="plytka_nie_z_trybu", skan_id=skan_id, poziom=poziom, tytul=tytul, tekst=tekst,
                                 odpowiedzi=(Przycisk("zamknij_pytanie", ST.PRZYCISK_ZESKANUJE_WLASCIWA, (id_,)),
                                             Przycisk("dopusc_plytke", ST.PRZYCISKI["dopusc_plytke"], (skan_id,)))))
        if s["aktywny"] and s["numer_plytki"] is None:
            id_ = f"brak_numeru_plytki:{skan_id}"
            numery = tuple(numery_plytek) or NUMERY_PLYTEK_ZAPASOWE
            poziom, tytul, tekst = ST.tekst_pytania("brak_numeru_plytki")
            wynik.append(Pytanie(id=id_, rodzaj="brak_numeru_plytki", skan_id=skan_id, poziom=poziom, tytul=tytul, tekst=tekst, numery=numery,
                                 odpowiedzi=tuple(Przycisk("podaj_numer_plytki", str(n), (skan_id, n)) for n in numery)
                                 + (Przycisk("zamknij_pytanie", ST.PRZYCISKI["zamknij_pytanie"], (id_,)),)))
        return wynik

    def _minut_od(self, poprzedni_id: int, czas: str | None, czasy: dict) -> int | str:
        wczesniej = czasy.get(poprzedni_id)
        if wczesniej is None:  # poprzedni skan z poprzedniej doby roboczej (ponowny skan przez granice 6:00)
            w = self.sesja.baza.wiersz("SELECT czas_analizy FROM skany WHERE id = ?", (poprzedni_id,))
            wczesniej = w["czas_analizy"] if w else None
        try:
            return max(0, round((dt.datetime.fromisoformat(czas) - dt.datetime.fromisoformat(wczesniej)).total_seconds() / 60))
        except (TypeError, ValueError):
            return "?"

    def _wczytaj_odrzucone(self) -> set:
        """Propozycje ponownego skanu odrzucone przez technika ("to nowy wsad") - z dziennika, zeby nie wracaly po restarcie."""
        od = (self._zegar() - dt.timedelta(days=PAMIEC_ODRZUCEN_DNI)).replace(microsecond=0).isoformat()
        wynik = set()
        for w in self.sesja.baza.wiersze("SELECT skan_id, dane FROM zdarzenia WHERE zrodlo = 'ui' AND typ = 'ponowny_skan_odrzucony' AND czas >= ?", (od,)):
            try:
                wynik.add((int(w["skan_id"]), int(json.loads(w["dane"])["poprzedni_id"])))
            except (TypeError, ValueError, KeyError):
                continue
        return wynik

    # --- komunikaty ulotne i odmowy --------------------------------------------------------------
    def _komunikat(self, rodzaj: str, *, id_: str | None = None, skan_id: int | None = None, **pola: Any) -> Komunikat:
        """Dodaje komunikat ulotny (albo podmienia komunikat o tym samym ``id_``); stan odswieza wolajacy."""
        if id_ is None:
            self._nr_komunikatu += 1
            id_ = f"k{self._nr_komunikatu}:{rodzaj}"
        k = self._nowy_komunikat(id_, rodzaj, skan_id=skan_id, **pola)
        self._komunikaty.pop(id_, None)
        self._komunikaty[id_] = k
        while len(self._komunikaty) > LIMIT_KOMUNIKATOW:  # okno, ktore nie zamyka komunikatow, nie zapycha pamieci: znikaja najstarsze
            stary = next((i for i, x in self._komunikaty.items() if not x.trwaly), None)  # trwale (blad zapisu) zostaja
            if stary is None:
                break
            self._komunikaty.pop(stary)
        self._ogloszone.discard(id_)
        self._ukryte.discard(id_)
        return k

    def _usun_komunikat(self, id_: str) -> bool:
        return self._komunikaty.pop(id_, None) is not None

    def _ustaw_komunikat(self, rodzaj: str, id_: str, pokaz: bool, *, wroc: bool = True, **pola: Any) -> bool:
        """Komunikat o stalym ``id_``: ``pokaz`` False - usuwa; True - dodaje albo podmienia, gdy zmienil sie tekst (bez
        ponownego sygnalu, gdy tekst ten sam). ``wroc`` False - nie przywraca komunikatu zamknietego przez technika. Zwraca
        True, gdy cos sie zmienilo."""
        if not pokaz:
            return self._usun_komunikat(id_)
        stary = self._komunikaty.get(id_)
        if stary is None and not wroc:
            return False
        if stary is not None and stary.tekst == ST.tekst_komunikatu(rodzaj, **pola)[2]:
            return False
        self._komunikat(rodzaj, id_=id_, **pola)
        return True

    def _komunikaty_zapisu(self, niezapisane: list, nowy: bool) -> bool:
        """P1 / P8: komunikat TRWALY ``blad_zapisu`` (staly id ``ID_BLAD_ZAPISU``) dla wynikow, ktorych nie da sie zapisac
        z powodu dysku, i ``baza_zajeta`` (id ``baza_zajeta:wyniki``) dla czekajacych na zajeta baze; oba znikaja same, gdy nic
        nie czeka. Zamkniety przez technika wraca tylko z nowa pozycja (``nowy``) - nie przy kazdej nieudanej probie."""
        dysk = sum(1 for n in niezapisane if n.przyczyna == "blad_zapisu")
        zajeta = sum(1 for n in niezapisane if n.przyczyna == "baza_zajeta")
        a = self._ustaw_komunikat("blad_zapisu", ID_BLAD_ZAPISU, dysk > 0, wroc=nowy, trwaly=True, ile=dysk)
        b = self._ustaw_komunikat("baza_zajeta", "baza_zajeta:wyniki", zajeta > 0, wroc=nowy)
        return a or b

    def _odmowa(self, kod: str, **pola: Any) -> Odpowiedz:
        """Odmowa wykonania polecenia: komunikat w stanie (jeden na rodzaj odmowy) + odpowiedz z tym samym tekstem."""
        k = self._komunikat(kod if kod in ST.KOMUNIKATY else "odmowa", id_=f"odmowa:{kod}", **pola)
        try:
            self._odswiez()
        except Exception:  # noqa: BLE001 - odmowa nigdy nie konczy sie wyjatkiem (stan zostaje poprzedni)
            LOG.exception("kontroler: stanu nie da sie odswiezyc po odmowie %s", kod)
        return Odpowiedz(False, k.tekst, kod)

    def _zle_argumenty(self, polecenie: str) -> Odpowiedz:
        """D1: zly typ / zla liczba argumentow polecenia = odmowa ``zle_argumenty`` (komunikat w stanie), nigdy wyjatek."""
        LOG.warning("kontroler: polecenie %s ze zlymi argumentami (blad okna)", polecenie)
        return self._odmowa(KOD_ZLE_ARGUMENTY, polecenie=polecenie)

    def _zamkniety_odp(self) -> Odpowiedz:
        return Odpowiedz(False, ST.tekst_komunikatu("program_zamkniety")[2], "program_zamkniety")

    def _bez_operatora(self) -> Odpowiedz | None:
        self._sprawdz_zmiane()
        if not self.sesja.operatorzy:
            return self._odmowa("pusta_lista_operatorow")
        if self.sesja.operator is None:
            return self._odmowa("brak_operatora")
        return None

    def _polecenie(self, funkcja: Callable[[], Any], *, operator: bool = True, nazwa: str = "", liczby: tuple = ()) -> Odpowiedz:
        """Wspolna obsluga polecenia: zamkniety program, zle argumenty (``liczby`` - identyfikatory, ktore musza byc liczbami
        calkowitymi; D1), brak operatora, odmowa ``session``, baza zajeta, inny blad (``blad_polecenia``); potem nowy stan."""
        if self._zamkniety:
            return self._zamkniety_odp()
        if not all(_jest_liczba(x) for x in liczby):
            return self._zle_argumenty(nazwa)
        if operator:
            odmowa = self._bez_operatora()
            if odmowa is not None:
                return odmowa
        try:
            dane = funkcja()
        except SE.BladSesji as e:
            return self._odmowa("odmowa", powod=str(e))
        except B.BladBazy:
            return self._odmowa("baza_zajeta")
        except Exception:  # noqa: BLE001 - D1: polecenie okna nigdy nie konczy sie wyjatkiem w slocie Qt
            LOG.exception("kontroler: polecenie %s nie powiodlo sie", nazwa)
            return self._odmowa("blad_polecenia")
        for kod in ("brak_operatora", "pusta_lista_operatorow", "odmowa", "baza_zajeta", "osoba_spoza_listy", KOD_ZLE_ARGUMENTY, "blad_polecenia"):
            self._usun_komunikat(f"odmowa:{kod}")  # polecenie przeszlo: stare odmowy nieaktualne
        self._odswiez()
        return Odpowiedz(True, dane=dane)

    # --- polecenia -------------------------------------------------------------------------------
    def wybierz_operatora(self, nazwa: str | None) -> Odpowiedz:
        """Osoba, ktora pracuje (na zmiane - DW3). ``None`` = nikt (technik odchodzi od stanowiska, D7): decyzje niedostepne
        do ponownego wyboru osoby; odpowiedz ``ok`` z kodem ``wylogowano``."""
        if self._zamkniety:
            return self._zamkniety_odp()
        if nazwa is None:
            self.sesja.operator = None
            self._zmiana_operatora = None
            self._odswiez()
            return Odpowiedz(True, ST.tekst_komunikatu("wylogowano")[2], "wylogowano")
        if not isinstance(nazwa, str):
            return self._zle_argumenty("wybierz_operatora")
        if not self.sesja.operatorzy:
            return self._odmowa("pusta_lista_operatorow")
        try:
            self.sesja.wybierz_operatora(nazwa)
        except SE.BladSesji:
            return self._odmowa("osoba_spoza_listy")
        self._zmiana_operatora = (self.sesja.doba(), self.sesja.zmiana())
        for kod in ("brak_operatora", "osoba_spoza_listy", KOD_ZLE_ARGUMENTY):
            self._usun_komunikat(f"odmowa:{kod}")
        for id_ in [i for i, k in self._komunikaty.items() if k.rodzaj == "nowa_zmiana"]:
            self._usun_komunikat(id_)
        self._odswiez()
        return Odpowiedz(True, dane=self.sesja.operator)

    def ukruszona(self, praca_id: int) -> Odpowiedz:
        def wykonaj() -> int:
            w = self.sesja.baza.wiersz("SELECT status_gniazda FROM prace WHERE id = ?", (praca_id,))
            wykryta = w is None or w["status_gniazda"] == ST.KOLOR_CZERWONY  # nieznana praca: blad zglosi session
            return self.sesja.decyzja(praca_id, "ukruszona" if wykryta else "ukruszona_niewykryta")

        return self._polecenie(wykonaj, nazwa="ukruszona", liczby=(praca_id,))

    def ok(self, praca_id: int) -> Odpowiedz:
        return self._polecenie(lambda: self.sesja.ok(praca_id), nazwa="ok", liczby=(praca_id,))

    def cofnij(self, praca_id: int) -> Odpowiedz:
        return self._polecenie(lambda: self.sesja.cofnij(praca_id), nazwa="cofnij", liczby=(praca_id,))

    def potwierdz_ponowny_skan(self, skan_id: int) -> Odpowiedz:
        return self._polecenie(lambda: self.sesja.zastap_skan(skan_id), nazwa="potwierdz_ponowny_skan", liczby=(skan_id,))

    def odrzuc_ponowny_skan(self, skan_id: int) -> Odpowiedz:
        def wykonaj() -> int:
            plytka = self.stan().plytka(skan_id)
            if plytka is None or plytka.moze_zastapic is None:
                raise SE.BladSesji(f"skan {skan_id}: nie ma propozycji ponownego skanu do odrzucenia")
            self.sesja.baza.zdarzenie("ui", "ponowny_skan_odrzucony", {"poprzedni_id": plytka.moze_zastapic, "operator": self.sesja.operator},
                                      skan_id=skan_id, czas=self._teraz())
            self._odrzucone.add((skan_id, plytka.moze_zastapic))
            return plytka.moze_zastapic

        return self._polecenie(wykonaj, nazwa="odrzuc_ponowny_skan", liczby=(skan_id,))

    def cofnij_zastapienie(self, skan_id: int) -> Odpowiedz:
        return self._polecenie(lambda: self.sesja.cofnij_zastapienie(skan_id), nazwa="cofnij_zastapienie", liczby=(skan_id,))

    def dopusc_plytke(self, skan_id: int) -> Odpowiedz:
        return self._polecenie(lambda: self.sesja.dopusc_plytke(skan_id), nazwa="dopusc_plytke", liczby=(skan_id,))

    def cofnij_dopuszczenie(self, skan_id: int) -> Odpowiedz:
        return self._polecenie(lambda: self.sesja.cofnij_dopuszczenie(skan_id), nazwa="cofnij_dopuszczenie", liczby=(skan_id,))

    def podaj_numer_plytki(self, skan_id: int, numer: int) -> Odpowiedz:
        n = numer
        if isinstance(numer, str):  # cyfry z pola tekstowego; nie-liczbe odrzuci session (odmowa z rada)
            try:
                n = int(numer.strip())
            except ValueError:
                n = 0
        return self._polecenie(lambda: self.sesja.podaj_numer_plytki(skan_id, n), nazwa="podaj_numer_plytki", liczby=(skan_id, n))

    def zamknij_pytanie(self, pytanie_id: str) -> Odpowiedz:
        """"Pozniej": pytanie znika z ``stan.pytania`` do konca pracy programu (wraca po restarcie; przy plytce zostaje
        z ``ukryte=True``); niczego nie rozstrzyga."""
        if self._zamkniety:
            return self._zamkniety_odp()
        if not isinstance(pytanie_id, str):
            return self._zle_argumenty("zamknij_pytanie")
        self._ukryte.add(pytanie_id)
        self._odswiez()
        return Odpowiedz(True)

    def zamknij_komunikat(self, komunikat_id: str) -> Odpowiedz:
        if self._zamkniety:
            return self._zamkniety_odp()
        if not isinstance(komunikat_id, str):
            return self._zle_argumenty("zamknij_komunikat")
        if not self._usun_komunikat(komunikat_id):
            self._ukryte.add(komunikat_id)  # trwaly: ukryty do konca pracy programu, zostaje przy plytce (``ukryte=True``)
        self._odswiez()
        return Odpowiedz(True)

    def zapisz_liste(self, doba: str | None = None) -> Odpowiedz:
        if self._zamkniety:
            return self._zamkniety_odp()
        if doba is not None and not (isinstance(doba, str) and _WZOR_DOBY.fullmatch(doba)):
            return self._zle_argumenty("zapisz_liste")
        self._usun_komunikat("odmowa:lista_nie_zapisana")
        if doba is None:  # plik listy biezacej - ten sam, ktory kontroler zapisuje sam; tu zapis wymuszony
            self._lista_zapisana, self._lista_blad = None, False
            self._odswiez()
            if self._lista_zapisana is None:
                return self._odmowa("lista_nie_zapisana")
            nazwa = PLIK_LISTY
        else:
            try:
                nazwa = self.sesja.zapisz_do_dofrezowania(doba, katalog=self._katalog_listy()).name
            except (OSError, sqlite3.Error, B.BladBazy) as e:
                LOG.warning("kontroler: listy doby nie da sie zapisac do pliku (%s)", type(e).__name__)
                return self._odmowa("lista_nie_zapisana")
            self._odswiez()
        return Odpowiedz(True, ST.tekst_komunikatu("lista_zapisana", plik=nazwa)[2], dane=nazwa)

    def ponow_zapis(self) -> Odpowiedz:
        """Wspolna czesc: nic nie czeka na zapis (prawdziwy kontroler i atrapa nadpisuja)."""
        if self._zamkniety:
            return self._zamkniety_odp()
        return Odpowiedz(True, dane=0)

    # --- pula projektow: wspolna walidacja (prawdziwy kontroler i atrapa: te same odmowy i kody, P6) -----------------
    def _sprawdz_pule(self, folder: Any, wspolczynnik: Any) -> tuple | Odpowiedz:
        """Argumenty ``ustaw_pule`` -> (folder albo None, wspolczynnik albo None) albo odmowa: ``program_zamkniety``,
        ``zle_argumenty`` (folder nie jest napisem / sciezka), ``zly_wspolczynnik`` (nie liczba albo poza
        ``WSPOLCZYNNIK_MIN``-``WSPOLCZYNNIK_MAX``; przecinek dziesietny dozwolony). Pusty folder = None (pula nieustawiona)."""
        if self._zamkniety:
            return self._zamkniety_odp()
        if folder is not None and not isinstance(folder, (str, os.PathLike)):
            return self._zle_argumenty("ustaw_pule")
        folder = os.fspath(folder).strip() if folder is not None else ""
        if "\0" in folder:
            return self._zle_argumenty("ustaw_pule")
        if wspolczynnik is not None:
            try:
                if isinstance(wspolczynnik, bool):
                    raise TypeError("bool")
                w = float(wspolczynnik.replace(",", ".") if isinstance(wspolczynnik, str) else wspolczynnik)
            except (TypeError, ValueError, AttributeError):
                w = float("nan")
            if not (math.isfinite(w) and WSPOLCZYNNIK_MIN <= w <= WSPOLCZYNNIK_MAX):
                return self._odmowa("zly_wspolczynnik", od=f"{WSPOLCZYNNIK_MIN:g}", do=f"{WSPOLCZYNNIK_MAX:g}")
            wspolczynnik = w
        self._usun_komunikat("odmowa:zly_wspolczynnik")
        self._usun_komunikat(f"odmowa:{KOD_ZLE_ARGUMENTY}")
        return (folder or None, wspolczynnik)

    def _komunikat_puli(self, stan_puli: str, czeka: int) -> bool:
        """Komunikat ``pula_pusta`` / ``pula_brak_folderu`` (id ``pula``), gdy skany czekaja na pule; znika, gdy pula gotowa
        albo nic nie czeka. Zwraca True, gdy cos sie zmienilo."""
        if czeka and stan_puli in ("pusta", "brak_folderu", "nieustawiona"):
            self._komunikat("pula_pusta" if stan_puli == "pusta" else "pula_brak_folderu", id_="pula", czeka=czeka)
            return True
        if stan_puli == "gotowa" or not czeka:
            return self._usun_komunikat("pula")
        return False

    def szczegoly_pracy(self, praca_id: int) -> SzczegolyPracy | None:
        if not _jest_liczba(praca_id):
            return None
        praca = self.stan().praca(praca_id)
        if praca is None or self._zamkniety:
            return None
        wpis = self._inspekcje(praca.skan_id).get((praca.gniazdo, praca.nr_fragmentu)) or {}
        inspekcja = wpis.get("inspekcja") or {}
        ubytki = tuple({k: u.get(k) for k in ("x", "y", "z", "srednica_mm", "glebokosc_mm", "metoda", "kolor", "na_krawedzi", "filar")}
                       for u in inspekcja.get("ubytki") or [])
        uwagi = tuple(str(u) for u in (wpis.get("uwagi") or []) + (inspekcja.get("uwagi") or []))
        kandydaci = tuple({"sha16": k.get("id"), "zeby": k.get("zeby"), "typ": k.get("typ"), "pokrycie": k.get("pokrycie")}
                          for k in wpis.get("kandydaci") or [])
        return SzczegolyPracy(praca=praca, ubytki=zamroz(ubytki), uwagi=uwagi, kandydaci=zamroz(kandydaci),
                              plik_podgladu=self._plik_podgladu(praca.skan_id))

    def _plik_podgladu(self, skan_id: int) -> Path | None:
        """Plik ``*_podglad.npz`` skanu: nazwa z dziennika (wpis ``podglad`` kontrolera), katalog podaje klasa pochodna."""
        katalog = self._katalog_podgladow()
        if katalog is None:
            return None
        w = self.sesja.baza.wiersz("SELECT dane FROM zdarzenia WHERE skan_id = ? AND typ = 'podglad' ORDER BY id DESC LIMIT 1", (skan_id,))
        try:
            plik = Path(katalog) / json.loads(w["dane"])["plik"] if w and w["dane"] else None
        except (ValueError, KeyError, TypeError):
            plik = None
        return plik if plik is not None and plik.is_file() else None

    def _katalog_podgladow(self) -> Path | None:
        return None

    def _zapisz_podglad(self, skan_id: int, plik: Path | str | None) -> None:
        """Wpis w dzienniku: ktory plik podgladu nalezy do skanu (sama nazwa pliku: czas i skrot skanu, bez sciezki)."""
        if plik:
            self.sesja.baza.zdarzenie("system", "podglad", {"plik": Path(plik).name}, skan_id=skan_id, czas=self._teraz())


# ----------------------------------------------------------------------------
# dane sztuczne i atrapa kontrolera
# ----------------------------------------------------------------------------
# rodzaj pracy w ``sztuczny_wynik`` -> (status match, status inspekcji albo None, status gniazda)
_RODZAJE_PRAC = {
    "zielony": ("zielony", "ok", "zielony"),
    "czerwony": ("zielony", "ubytek", "czerwony"),
    "zolty": ("zielony", "sprawdz", "zolty"),
    "sprawdz_ulozenie": ("zielony", "sprawdz_ulozenie", "zolty"),
    "popraw_ulozenie": ("zielony", "popraw_ulozenie", "zolty"),
    "skan_ponownie": ("zielony", "skan_ponownie", "zolty"),
    "nie_sprawdzono": ("zielony", "nie_sprawdzono", "zolty"),
    "blad_inspekcji": ("zielony", "nie_sprawdzono", "zolty"),
    "pomaranczowy": ("zielony", "poprawka", "pomaranczowy"),
    "szary": ("szary", None, "szary"),
    # P4: kolor gniazda "zielony" bez inspekcji "ok" albo przy nieznanym dopasowaniu (porownaj tak dzis nie liczy, ale nowa
    # wersja analizy moze) - program NIE moze pokazac takiej pracy jako zielonej
    "zielony_bez_inspekcji": ("zielony", None, "zielony"),
    "zielony_pominieto": ("zielony", "pominieto", "zielony"),
    "zielony_nowa_inspekcja": ("zielony", "nowy_status_inspect", "zielony"),
    "zielony_nowe_dopasowanie": ("nowy_status_match", "ok", "zielony"),
}
RODZAJE_PRAC = tuple(_RODZAJE_PRAC) + ("podwojny",)


def skrot_sztuczny(tekst: str) -> str:
    """16 znakow SHA-256 napisu - sztuczne identyfikatory projektow i skanow (jak ``sha16`` prawdziwych plikow)."""
    return hashlib.sha256(tekst.encode("utf-8")).hexdigest()[:16]


def projekt_sztuczny(nr: int) -> str:
    """``sha16`` sztucznego projektu numer ``nr`` (ten sam w ``sztuczny_wynik`` i w indeksie atrapy)."""
    return skrot_sztuczny(f"projekt sztuczny {nr}")


def sztuczny_wynik(uklad: str | None = "wieczorna", numer: int | None = 1, gniazda: dict | None = None, *, uklad_zgodny: bool = True,
                   poza_gniazdem: int = 0, skan: str = "skan.stl", projekty: dict | None = None, czas_s: float = 1.0) -> dict:
    """Wynik analizy w postaci ``porownaj.porownaj`` (te pola, ktore czytaja ``session`` i kontroler) z danych sztucznych.

    ``gniazda``: numer gniazda -> rodzaj pracy z ``RODZAJE_PRAC`` (``podwojny`` = dwie prace w gniezdzie); ``projekty``:
    numer gniazda -> numer sztucznego projektu (domyslnie numer gniazda). ``uklad_zgodny`` False = skan niepasujacy do
    zadnego ukladu (bez gniazd). Funkcja jest czysta (te same argumenty = ten sam wynik) i uzywa tylko biblioteki standardowej.
    """
    if not uklad_zgodny:
        return {"skan": skan, "plytka": uklad, "plytka_wybor": "auto", "uklad_zgodny": False, "uklad_komunikat": "zaden uklad nie pasuje",
                "numer": None, "numer_zrodlo": "nieznany", "wspolczynnik": None, "gniazda": [], "gniazda_puste": [], "gniazda_podwojne": [],
                "poza_gniazdem": 0, "czas_s": {"razem": czas_s}, "statusy_gniazd": {}, "ubytki": 0}
    gniazda = dict(gniazda if gniazda is not None else {1: "zielony", 2: "czerwony", 3: "zolty"})
    projekty = projekty or {}
    wpisy, podwojne = [], []

    def wpis(nr: int | None, rodzaj: str, projekt: int, fragment: str = "praca") -> dict:
        match, inspekcja, kolor = _RODZAJE_PRAC[rodzaj]
        sha16 = projekt_sztuczny(projekt)
        ubytki = [{"x": 0.6, "y": -0.4, "z": 13.5, "srednica_mm": 0.62, "glebokosc_mm": 0.21, "metoda": "A+B", "kolor": "czerwony",
                   "punkty": 60, "odleglosc_od_brzegu_mm": 0.4, "wciecie_mm": 0.3, "na_krawedzi": True, "filar": 1}] if inspekcja == "ubytek" else []
        ins = None
        if inspekcja is not None:
            ins = {"gniazdo": nr, "projekt": sha16, "status": inspekcja, "pokrycie": 0.9, "ubytki": ubytki, "plamy": [], "wciecia": [], "uwagi": []}
            if rodzaj == "blad_inspekcji":
                ins["blad"] = "ValueError: blad sztuczny (inspect.py:1 sprawdz)"
                ins["uwagi"] = ["blad inspekcji: ValueError: blad sztuczny (inspect.py:1 sprawdz)"]
        return {"gniazdo": nr, "status_fragmentu": fragment, "punkty": 18000, "srodek": [0.0, 0.0, 12.0], "status": match, "pewnosc": 0.75,
                "uwagi": [], "kandydaci": [{"id": sha16, "zeby": [str(10 + projekt % 38)], "typ": "korona", "pokrycie": 0.91 if match != "szary" else 0.2}],
                "skala": {"poprawka_proc": -0.1, "wspolczynnik_puli": 1.225}, "inspekcja": ins, "status_gniazda": kolor}

    for nr in sorted(gniazda):
        rodzaj = gniazda[nr]
        projekt = projekty.get(nr, nr)
        if rodzaj == "podwojny":
            podwojne.append(nr)
            wpisy.append(wpis(nr, "zielony", projekt, "podwojny"))
            wpisy.append(wpis(nr, "zielony", projekt + 100, "podwojny"))
        else:
            wpisy.append(wpis(nr, rodzaj, projekt))
    for i in range(poza_gniazdem):
        wpisy.append(wpis(None, "szary", 200 + i, "poza_gniazdem"))
    statusy = {k: sum(1 for w in wpisy if w["status_gniazda"] == k) for k in ("zielony", "czerwony", "zolty", "szary", "pomaranczowy")}
    return {"skan": skan, "plytka": uklad, "plytka_wybor": "auto", "uklad_zgodny": True, "wspolczynnik": 1.225, "projekty": 16,
            "numer": numer, "numer_zrodlo": "dolki" if numer is not None else "nieznany", "gniazda": wpisy, "gniazda_puste": [],
            "gniazda_podwojne": podwojne, "poza_gniazdem": poza_gniazdem, "czas_s": {"razem": czas_s}, "statusy_gniazd": statusy,
            "ubytki": sum(len((w["inspekcja"] or {}).get("ubytki") or []) for w in wpisy)}


def kolory_oczekiwane(wynik: dict, decyzje: dict | None = None, status_skanu: str = "przyjety", numer_znany: bool = True) -> dict:
    """Prawda dla testow: (gniazdo, nr fragmentu) -> klasa koloru wg wyniku analizy po zastosowaniu decyzji technika.

    ``decyzje``: (gniazdo, nr fragmentu) -> ``ukruszona`` / ``ok``. Reguly jak w ``session``: decyzja "Ukruszona" =
    czerwony, "OK" = zatwierdzona_ok; skan do powtorzenia nie ma zielonych (zielony -> zolty); skan nieaktywny - brak koloru;
    P4: zielony tylko przy inspekcji "ok" i dopasowaniu zielonym / zoltym (inaczej zolty); plytka bez numeru
    (``numer_znany`` False) nie ma zielonych (zielony -> brak koloru, status ``czeka_na_numer``).
    """
    decyzje = decyzje or {}
    wynik_kolory, licznik = {}, {}
    for g in wynik.get("gniazda") or []:
        licznik[g.get("gniazdo")] = licznik.get(g.get("gniazdo"), 0) + 1
        klucz = (g.get("gniazdo"), licznik[g.get("gniazdo")])
        kolor = g.get("status_gniazda")
        sprawdzona = (g.get("inspekcja") or {}).get("status") == ST.INSPEKCJA_ZIELONA and g.get("status") in ST.DOPASOWANIA_ZIELONE
        if status_skanu not in SE.STATUSY_AKTYWNE:
            kolor = None
        elif decyzje.get(klucz) in ST.DECYZJE_UKRUSZENIA:
            kolor = ST.KOLOR_CZERWONY
        elif decyzje.get(klucz) == "ok":
            kolor = ST.KOLOR_ZATWIERDZONA_OK
        elif status_skanu == SE.STATUS_DO_POWTORZENIA and kolor == ST.KOLOR_ZIELONY:
            kolor = ST.KOLOR_ZOLTY
        elif kolor == ST.KOLOR_ZIELONY and not sprawdzona:
            kolor = ST.KOLOR_ZOLTY
        elif kolor == ST.KOLOR_ZIELONY and not numer_znany and not ST.ZIELONE_BEZ_NUMERU_PLYTKI:
            kolor = None
        wynik_kolory[klucz] = kolor
    return wynik_kolory


def indeks_sztuczny(baza: B.Baza, czas: str, ile: int = 30) -> None:
    """Fikcyjne zlecenia, projekty i frezowania dla sztucznych projektow 1..``ile`` (kuwety 9001.., krazek ``K-1``), jesli
    indeks w bazie jest pusty - dzieki nim lista "do dofrezowania" ma kuwete, zeby i krazek. Tylko dane sztuczne."""
    if baza.wiersz("SELECT id FROM zlecenia LIMIT 1") is not None:
        return
    with baza.transakcja():
        for nr in range(1, ile + 1):
            zlecenie = baza.wstaw("zlecenia", zrodlo="cyrkon", folder=f"{9000 + nr} Atrapa {nr}", folder_norm=f"{9000 + nr} atrapa {nr}",
                                  kuweta=str(9000 + nr), dodano=czas, usuniety=0)
            projekt = baza.wstaw("projekty", zlecenie_id=zlecenie, plik=f"atrapa-{10 + nr}-crown_cad.stl", sha16=projekt_sztuczny(nr),
                                 zeby=str(10 + nr % 38), typ="korona", usuniety=0)
            baza.wstaw("frezowania", projekt_id=projekt, plik_w_raporcie=f"atrapa-{10 + nr}-crown_cad.stl", krazek="K-1", wspolczynnik=1.225,
                       data=czas[:10], zrodlo="reczny")


RODZAJE_SKANOW_ATRAPY = ("zwykla", "czysta", "do_powtorzenia", "niezgodny_uklad", "nie_z_trybu", "bez_numeru", "blad")
OPERATORZY_ATRAPY = ("Technik A", "Technik B")


class AtrapaKontrolera(KontrolerSesji):
    """Kontroler na danych sztucznych: prawdziwa ``Sesja`` na bazie w katalogu tymczasowym, BEZ skanera i silnika.

    Do budowy i testow okna (A3b). Skany "wrzuca" test albo pokaz: ``symuluj_skan(rodzaj, ...)`` (rodzaje:
    ``RODZAJE_SKANOW_ATRAPY``), ``symuluj_postep``, ``symuluj_komunikat``, ``scenariusz_pokazowy()``. Polecenia dzialaja
    jak w prawdziwym kontrolerze (te same reguly ``session``). ``start_skanu`` niczego nie klika - zapisuje wywolanie
    w ``starty_skanu``. ``zamknij()`` usuwa katalog tymczasowy. Fikcyjne zlecenia w indeksie (``indeks_sztuczny``: kuwety
    9001-9030, krazek ``K-1``) daja kuwete, zeby i krazek na liscie "do dofrezowania".

    Czesc "zywa" jak w prawdziwym kontrolerze (P6, te same odmowy i kody - test zgodnosci w ``test_kontroler_api``):
    ``ustaw_pule`` - ta sama walidacja (``zly_wspolczynnik``, ``zle_argumenty``; ``None`` = pula ``nieustawiona``);
    ``odswiez_pule`` przechodzi przez stan ``liczenie``, a wynik liczenia przychodzi w nastepnym ``przetworz()``; nieudany
    ``start_skanu`` = odmowa ``start_skanu_nieudany``. Stany do pokazania oknu: ``symuluj_pule(stan, liczba)`` (nieustawiona /
    liczenie / gotowa / pusta / brak_folderu), ``symuluj_kolejke(czeka, wstrzymane, silnik_gotowy)``,
    ``symuluj_skaner(dostepny, zajete, start_udany)``, ``symuluj_blad_zapisu(ile, przyczyna)`` (pozycje "nie zapisano").
    """

    def __init__(self, katalog: str | Path | None = None, *, operatorzy: tuple = OPERATORZY_ATRAPY, zegar: Callable[[], dt.datetime] | None = None,
                 ust: dict | None = None, liczba_stl: int = 16):
        self._wlasny_katalog = katalog is None
        self.katalog = Path(tempfile.mkdtemp(prefix="qc_atrapa_")) if katalog is None else Path(katalog)
        self.katalog.mkdir(parents=True, exist_ok=True)
        baza = B.otworz(self.katalog / "atrapa.sqlite", zegar=zegar)
        sesja = SE.Sesja(baza, operatorzy=operatorzy, katalog_wynikow=self.katalog / "wyniki", zegar=zegar, wersja_programu="atrapa")
        super().__init__(sesja, ust, zegar=zegar)
        self.starty_skanu: list[str] = []
        self._czeka_na_skan = False
        self._nr_skanu = 0
        self._analiza: Postep | None = None
        self._czeka = 0
        self._wstrzymane = 0
        self._silnik_gotowy = True
        # pula: "prawda" sztucznego folderu (co znajdzie liczenie) i stan pokazany oknu
        self._pula_folder: str | None = "(atrapa)"
        self._pula_wspolczynnik: float | None = None
        self._pula_prawda: tuple = ("gotowa", liczba_stl) if liczba_stl > 0 else ("pusta", 0)
        self._pula_stan, self._pula_liczba = self._pula_prawda
        self._pula_czas: str | None = self._teraz()
        self._pula_do_policzenia = False
        # skaner i zapis
        self._skaner_dostepny = True
        self._zajete = 0
        self._start_udany = True
        self._niezapisane: list[Niezapisany] = []
        self._blad_zapisu_trwa = False
        indeks_sztuczny(baza, self._teraz())

    # --- czesc zywa
    def _stan_zywy(self) -> dict:
        niezapisane = tuple(self._niezapisane)
        return {"analiza": self._analiza,
                "kolejka": Kolejka(w_toku=1 if self._analiza else 0, czeka=self._czeka, wstrzymane=self._wstrzymane + len(niezapisane),
                                   silnik_gotowy=self._silnik_gotowy, niezapisane=len(niezapisane)),
                "pula": Pula(folder=self._pula_folder, wspolczynnik=self._pula_wspolczynnik, liczba_stl=self._pula_liczba, stan=self._pula_stan,
                             napis=ST.STANY_PULI.get(self._pula_stan, "").format(n=self._pula_liczba), odswiezono=self._pula_czas),
                "skaner": Skaner(folder="(atrapa)", dostepny=self._skaner_dostepny, dziala=not self._zamkniety, zajete=self._zajete,
                                 startow_skanu=len(self.starty_skanu), ostatni_start_skanu=self.starty_skanu[-1] if self.starty_skanu else None,
                                 czeka_na_skan=self._czeka_na_skan),
                "niezapisane": niezapisane}

    def _katalog_podgladow(self) -> Path | None:
        return self.katalog / "podglady"

    def przetworz(self, limit_s: float = LIMIT_PRZETWARZANIA_S) -> int:
        """Jak w prawdziwym kontrolerze: zmiana zmiany, wynik liczenia puli (po ``odswiez_pule``), zapis niezapisanych
        wynikow, gdy przyczyna ustapila (``symuluj_blad_zapisu(0)``)."""
        if self._zamkniety:
            return 0
        n = super().przetworz(limit_s)
        if self._pula_do_policzenia:
            self._pula_do_policzenia = False
            self._pula_policzona(*self._pula_prawda)
            n += 1
        if self._niezapisane and not self._blad_zapisu_trwa:
            self.ponow_zapis()
            n += 1
        return n

    # --- polecenia zywe
    def start_skanu(self) -> Odpowiedz:
        if self._zamkniety:
            return self._zamkniety_odp()
        self.starty_skanu.append(self._teraz())
        udany = self._start_udany
        self._czeka_na_skan = udany
        self.sesja.baza.zdarzenie("ui", "start_skanu", {"udany": udany}, czas=self.starty_skanu[-1])
        if not udany:
            return self._odmowa("start_skanu_nieudany")
        if self._usun_komunikat("odmowa:start_skanu_nieudany"):
            self._odswiez()  # stara odmowa znika z komunikatow
        else:
            self._odswiez_zywe()
        return Odpowiedz(True)

    def ustaw_pule(self, folder: str | None, wspolczynnik: float | None = None) -> Odpowiedz:
        wynik = self._sprawdz_pule(folder, wspolczynnik)
        if isinstance(wynik, Odpowiedz):
            return wynik
        self._pula_folder, self._pula_wspolczynnik = wynik
        self.sesja.baza.zdarzenie("pula", "pula_ustawiona", {"wspolczynnik": self._pula_wspolczynnik, "folder_ustawiony": self._pula_folder is not None,
                                                            "operator": self.sesja.operator}, czas=self._teraz())
        return self.odswiez_pule()

    def odswiez_pule(self) -> Odpowiedz:
        if self._zamkniety:
            return self._zamkniety_odp()
        self._usun_komunikat("odmowa:zly_wspolczynnik")
        if self._pula_folder is None:
            self._pula_stan, self._pula_liczba, self._pula_do_policzenia = "nieustawiona", None, False
            self._komunikat_puli("nieustawiona", self._wstrzymane)
        else:
            self._pula_stan, self._pula_do_policzenia = "liczenie", True  # wynik w nastepnym przetworz(), jak watek liczenia
        self._odswiez()
        return Odpowiedz(True, dane=self._pula_stan)

    def _pula_policzona(self, stan: str, liczba: int | None) -> None:
        self._pula_stan, self._pula_liczba, self._pula_czas = stan, liczba, self._teraz()
        if stan == "gotowa" and self._wstrzymane:  # jak w prawdziwym kontrolerze: skany czekajace na pule ida do analizy
            self._czeka, self._wstrzymane = self._czeka + self._wstrzymane, 0
        self._komunikat_puli(stan, self._wstrzymane)
        self._odswiez()

    def ponow_zapis(self) -> Odpowiedz:
        if self._zamkniety:
            return self._zamkniety_odp()
        if not self._niezapisane:
            return Odpowiedz(True, dane=0)
        if self._blad_zapisu_trwa:  # przyczyna trwa: kolejna nieudana proba
            self._niezapisane = [dataclasses.replace(n, proby=n.proby + 1) for n in self._niezapisane]
            self._komunikaty_zapisu(self._niezapisane, nowy=False)
            self._odswiez()
            przyczyna = self._niezapisane[-1].przyczyna
            return Odpowiedz(False, ST.tekst_komunikatu(przyczyna, ile=len(self._niezapisane))[2], przyczyna, dane=len(self._niezapisane))
        zapisane, self._niezapisane = self._niezapisane, []
        for n in zapisane:  # przyczyna ustapila: skany trafiaja do sesji jak zwykle wyniki (kazdy z innymi projektami)
            self.symuluj_skan("czysta", numer=n.numer if n.numer is not None else 1, projekty={g: 1000 + 10 * self._nr_skanu + g for g in range(1, 5)})
        self._komunikaty_zapisu([], nowy=False)
        self._odswiez()
        return Odpowiedz(True, dane=0)

    # --- stany do pokazania oknu (P6)
    def symuluj_pule(self, stan: str, liczba: int | None = None) -> None:
        """Stan puli jak w prawdziwym kontrolerze: ``nieustawiona`` (bez folderu), ``liczenie`` (do ``odswiez_pule`` +
        ``przetworz``), ``gotowa`` / ``pusta`` / ``brak_folderu`` (wynik liczenia; kolejne liczenia daja to samo)."""
        if stan not in STANY_PULI:
            raise ValueError(f"nieznany stan puli {stan!r} (znane: {', '.join(STANY_PULI)})")
        self._pula_do_policzenia = False
        if stan == "nieustawiona":
            self._pula_folder, self._pula_stan, self._pula_liczba = None, "nieustawiona", None
            self._komunikat_puli("nieustawiona", self._wstrzymane)
            self._odswiez()
        elif stan == "liczenie":
            self._pula_stan = "liczenie"
            self._odswiez_zywe()
        else:
            if liczba is None:
                liczba = {"gotowa": 16, "pusta": 0}.get(stan)
            self._pula_prawda = (stan, liczba)
            self._pula_folder = self._pula_folder or "(atrapa)"
            self._pula_policzona(stan, liczba)

    def symuluj_kolejke(self, czeka: int = 0, wstrzymane: int = 0, silnik_gotowy: bool = True) -> None:
        """Licznik kolejki: ``czeka`` (w kolejce silnika), ``wstrzymane`` (czekaja na pule albo silnik - przy puli innej niz
        ``gotowa`` z komunikatem ``pula_pusta`` / ``pula_brak_folderu``), ``silnik_gotowy`` False = komunikat
        ``silnik_nie_startuje`` (jak prawdziwy, gdy proces analizy nie umie wystartowac)."""
        self._czeka, self._wstrzymane, self._silnik_gotowy = int(czeka), int(wstrzymane), bool(silnik_gotowy)
        self._ustaw_komunikat("silnik_nie_startuje", "silnik", not self._silnik_gotowy)
        self._komunikat_puli(self._pula_stan, self._wstrzymane)
        self._odswiez()

    def symuluj_skaner(self, dostepny: bool = True, zajete: int = 0, start_udany: bool = True) -> None:
        """Skaner: ``dostepny`` False = brak folderu skanera (komunikat ``folder_skanera_niedostepny``), ``zajete`` = pliki
        czekajace na zwolnienie (komunikat ``plik_zajety``), ``start_udany`` False = kolejne ``start_skanu`` odmawia
        (``start_skanu_nieudany``)."""
        self._skaner_dostepny, self._zajete, self._start_udany = bool(dostepny), int(zajete), bool(start_udany)
        self._ustaw_komunikat("folder_skanera_niedostepny", "folder_skanera", not self._skaner_dostepny)
        self._ustaw_komunikat("plik_zajety", "plik_zajety:skaner", self._zajete > 0, od_s=12)
        self._odswiez()

    def symuluj_blad_zapisu(self, ile: int = 1, przyczyna: str = "blad_zapisu") -> None:
        """Skany policzone, ale niezapisane (P1 / P8): ``ile`` nowych pozycji ``stan.niezapisane`` i komunikat (``blad_zapisu``
        trwaly albo ``baza_zajeta``). Przyczyna trwa do ``symuluj_blad_zapisu(0)`` - potem ``ponow_zapis()`` / ``przetworz()``
        zapisuje je jak zwykle wyniki (plytki "czysta")."""
        if przyczyna not in ST.NAPISY_NIEZAPISANE:
            raise ValueError(f"nieznana przyczyna {przyczyna!r} (znane: {', '.join(ST.NAPISY_NIEZAPISANE)})")
        if ile <= 0:
            self._blad_zapisu_trwa = False
            return
        self._blad_zapisu_trwa = True
        for _ in range(int(ile)):
            self._nr_skanu += 1
            self._niezapisane.append(Niezapisany(sha16=skrot_sztuczny(f"niezapisany {self._nr_skanu} {time.time_ns()}"), rodzaj="wynik",
                                                 przyczyna=przyczyna, napis=ST.NAPISY_NIEZAPISANE[przyczyna], od=self._teraz(), proby=1,
                                                 numer=1, uklad="wieczorna", prac=4))
        self._komunikaty_zapisu(self._niezapisane, nowy=True)
        self._odswiez()

    def zamknij(self) -> Odpowiedz:
        if self._zamkniety:
            return Odpowiedz(True)
        stan = dataclasses.replace(self.stan(), zamkniety=True, analiza=None)
        self._zamkniety = True
        self._stan = stan
        self.sesja.baza.zamknij()
        if self._wlasny_katalog:
            shutil.rmtree(self.katalog, ignore_errors=True)
        self._powiadom("zamkniety", stan=stan)
        return Odpowiedz(True)

    # --- symulacja
    def symuluj_postep(self, etap: str = "identyfikacja i inspekcja gniazd (match + inspect)", udzial: float = 0.55, czeka: int = 0) -> None:
        """Trwajaca analiza na ekranie (bez skanu): pasek postepu i licznik kolejki. ``udzial`` None = koniec analizy."""
        self._czeka = czeka
        self._analiza = None if udzial is None else Postep(zadanie_id=self._nr_skanu + 1, etap=etap, udzial=float(udzial), od=time.time())
        self._odswiez_zywe("postep")

    def symuluj_komunikat(self, rodzaj: str, **pola: Any) -> Komunikat:
        """Komunikat ulotny dowolnego rodzaju z ``statusy.KOMUNIKATY`` (np. ``plik_zajety``, ``plik_niedostepny``, ``plik_zmieniony``)."""
        pola = {"od_s": 12, "dalej": ST.PLIK_NIEDOSTEPNY_PONOWIENIE.format(proba=1, prob=3), "powod": ST.POWODY_BLEDU_ANALIZY["analiza"],
                "czeka": 1, "ile": 1, **pola}
        k = self._komunikat(rodzaj, **pola)
        self._odswiez()
        return k

    def symuluj_skan(self, rodzaj: str = "zwykla", *, numer: int | None = 1, uklad: str | None = None, gniazda: dict | None = None,
                     poza_gniazdem: int = 0, projekty: dict | None = None) -> int:
        """"Skaner zapisal plik, silnik policzyl": przyjmuje sztuczny wynik do sesji i odswieza stan; zwraca ``skan_id``.

        ``rodzaj``: ``zwykla`` (mieszanka statusow), ``czysta`` (same zielone), ``do_powtorzenia`` (poruszony skan i dwie
        prace w gniezdzie), ``niezgodny_uklad``, ``nie_z_trybu`` (plytka poranna wieczorem), ``bez_numeru``, ``blad``
        (analiza bez wyniku). ``gniazda`` nadpisuje zestaw prac (numer gniazda -> rodzaj z ``RODZAJE_PRAC``).
        """
        if rodzaj not in RODZAJE_SKANOW_ATRAPY:
            raise ValueError(f"nieznany rodzaj skanu {rodzaj!r} (znane: {', '.join(RODZAJE_SKANOW_ATRAPY)})")
        self._nr_skanu += 1
        nazwa = f"atrapa_{self._nr_skanu:03d}.stl"
        zdarzenie = {"plik": f"atrapa/{nazwa}", "sha16": skrot_sztuczny(f"skan sztuczny {self._nr_skanu} {time.time_ns()}"),
                     "rozmiar": 48_000_000 + self._nr_skanu, "czas_pliku": self._teraz()}
        self._analiza, self._czeka_na_skan = None, False
        if rodzaj == "blad":
            skan_id = self.sesja.przyjmij_blad(zdarzenie, "analiza: blad sztuczny", self.tryb)
            self._odswiez()
            return skan_id
        domyslne = {
            "zwykla": {1: "zielony", 2: "czerwony", 3: "zolty", 4: "szary", 5: "pomaranczowy", 6: "nie_sprawdzono", 7: "blad_inspekcji", 8: "zielony",
                       9: "czerwony"},
            "czysta": {1: "zielony", 2: "zielony", 3: "zielony", 4: "zielony"},
            "do_powtorzenia": {1: "zielony", 2: "skan_ponownie", 3: "podwojny", 4: "czerwony"},
            "nie_z_trybu": {1: "zielony", 2: "zielony", 3: "czerwony"},
            "bez_numeru": {1: "zielony", 2: "czerwony", 3: "zielony"},
            "niezgodny_uklad": {},
        }[rodzaj]
        uklad = uklad or ("poranna" if rodzaj == "nie_z_trybu" else "wieczorna")
        wynik = sztuczny_wynik(uklad, None if rodzaj == "bez_numeru" else numer, gniazda if gniazda is not None else domyslne,
                               uklad_zgodny=rodzaj != "niezgodny_uklad", poza_gniazdem=poza_gniazdem, skan=nazwa, projekty=projekty)
        skan_id = self.sesja.przyjmij_wynik(zdarzenie, wynik, self.tryb)
        self._zapisz_podglad(skan_id, self._sztuczny_podglad(zdarzenie["sha16"], wynik))
        self._odswiez()
        return skan_id

    def _sztuczny_podglad(self, sha16: str, wynik: dict) -> Path | None:
        """Plik ``*_podglad.npz`` jak z silnika (``g<nr>_P`` punkty N x 3, ``g<nr>_d`` odchylki w mm) dla prac z inspekcja:
        kolko punktow wokol srodka gniazda, w pracy z ubytkiem plama pod powierzchnia. Bez numpy: brak podgladu."""
        try:
            import numpy as np
        except ImportError:
            return None
        srodki: dict = {}
        try:
            from . import uklad as U

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                srodki = {g.id: (g.x, g.y) for g in U.wczytaj(wynik["plytka"]).sockets}
        except Exception:  # noqa: BLE001 - podglad wokol (0, 0) tez wystarczy do proby okna
            srodki = {}
        rng = np.random.default_rng(int(sha16[:8], 16))
        tablice = {}
        for g in wynik.get("gniazda") or []:
            if g.get("gniazdo") is None or not g.get("inspekcja") or f"g{g['gniazdo']}_P" in tablice:
                continue
            r = 4.0 * np.sqrt(rng.random(600))
            kat = rng.random(600) * 2 * np.pi
            x0, y0 = srodki.get(g["gniazdo"], (0.0, 0.0))
            P = np.column_stack([x0 + r * np.cos(kat), y0 + r * np.sin(kat), 12.0 + 2.0 * (1 - (r / 4.0) ** 2)])
            d = rng.normal(0.0, 0.01, 600)
            for u in g["inspekcja"].get("ubytki") or []:
                blisko = np.hypot(P[:, 0] - (x0 + u["x"]), P[:, 1] - (y0 + u["y"])) < u["srednica_mm"]
                d[blisko] = -u["glebokosc_mm"]
            tablice[f"g{g['gniazdo']}_P"] = P.astype(np.float32)
            tablice[f"g{g['gniazdo']}_d"] = d.astype(np.float32)
        if not tablice:
            return None
        katalog = self._katalog_podgladow()
        katalog.mkdir(parents=True, exist_ok=True)
        plik = katalog / f"{self._zegar():%Y%m%d_%H%M%S}_{sha16}_{self._nr_skanu}_podglad.npz"
        np.savez(plik, **tablice)
        return plik

    def scenariusz_pokazowy(self) -> dict:
        """Gotowy wieczor do pokazu okna: 5 plytek (zwykla z decyzjami, czysta, do powtorzenia, nie z trybu, bez numeru),
        wybrany operator, 1 "Ukruszona" i 1 "OK". Zwraca {nazwa: skan_id}."""
        self.wybierz_operatora(self.sesja.operatorzy[0])
        skany = {"zwykla": self.symuluj_skan("zwykla", numer=1), "czysta": self.symuluj_skan("czysta", numer=2, projekty={1: 11, 2: 12, 3: 13, 4: 14})}
        zwykla = self.stan().plytka(skany["zwykla"])
        self.ukruszona(zwykla.gniazdo(2).praca.praca_id)
        self.ok(zwykla.gniazdo(9).praca.praca_id)
        skany["do_powtorzenia"] = self.symuluj_skan("do_powtorzenia", numer=3, projekty={1: 15, 2: 16, 3: 17, 4: 18})  # 3: dwie prace
        skany["nie_z_trybu"] = self.symuluj_skan("nie_z_trybu", numer=4, projekty={1: 24, 2: 25, 3: 26})
        skany["bez_numeru"] = self.symuluj_skan("bez_numeru", projekty={1: 21, 2: 22, 3: 23})
        return skany
