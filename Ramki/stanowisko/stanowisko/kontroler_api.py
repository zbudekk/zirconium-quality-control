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

PORANEK (E3-A7, wersja 3, addytywnie): ``stan.tryb`` (``wieczor`` / ``rano``) wybiera czlowiek poleceniem ``przelacz_tryb``
(tryb nie zmienia sie sam; ostatni wybor pamieta dziennik bazy, wiec wraca po restarcie). W trybie ``rano`` skany ida do sesji
porannej (``session_rano.SesjaRano``), a ``stan.rano`` (``StanRano``) opisuje piec: plytki z gniazdami w klasach pracy porannej
(``PracaRano``: kuweta, zab, miniatura, kandydaci), zlecenia kompletne i braki, kuwety do rozlozenia w wybranej kolejnosci,
blokady "Zamknij piec". Polecenia poranne: ``POLECENIA_RANO``; zapytanie ``projekty_kuwety(kuweta)`` podaje projekty zlecenia
do przypisania recznego. Bez ramki i bez Excela stan ma o tym komunikaty, program dziala dalej.

RAMKI I EXCEL (E3-A12, wersja 4, addytywnie): ``podlacz_ramki(indicate.Indicate)`` / ``podlacz_excel(excel.Excel)`` (``Aplikacja``
robi to z ustawien przy starcie). Zdarzenia ramek odbiera ``przetworz()`` (zegar okna) - kazde zapisane w dzienniku ``zdarzenia``
(zrodlo ``ramka_p`` / ``ramka_w``) z kluczem ``indicate.klucz_zdarzenia`` sprawdzanym w tej samej transakcji co skutek (po
restarcie programu historia ramki nie daje duplikatow); "Zamknij piec" z ramki zamyka TYLKO biezacy piec. Plan ramki porannej =
``SesjaRano.plan_plytek(kolejnosc z ekranu)`` po kazdej zmianie pieca; ramka wieczorna: Spacja -> "skanowanie", start analizy ->
"analiza", wynik -> kolory gniazd mapy (``ramka_protokol.kolor_ramki`` statusow ``Gniazdo``). Excel: po "Zamknij piec" w trybie
"pytaj" ``stan.excel`` (``StanExcel``) z propozycjami do okna "Excel: wskaz wiersz" (zapis koloru dopiero po ``excel_zatwierdz``
z okna), w trybie "cien" - sam log. Stan ramek: ``stan.ramki`` (``StanRamek``). Polecenia: ``POLECENIA_A12``.

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
from . import session_rano as SR
from . import statusy as ST

LOG = logging.getLogger(__name__)

WERSJA_KONTRAKTU = 4  # 2: zmiany addytywne po rundzie 2 recenzji PR #20; 3: poranek (E3-A7); 4: ramki i Excel (E3-A12) - addytywnie
TRYB_WIECZOR = SE.TRYB_WIECZOR
TRYB_RANO = SE.TRYB_RANO
TRYBY = (TRYB_WIECZOR, TRYB_RANO)
KOLEJNOSCI_KUWET = SR.KOLEJNOSCI  # "liczba" (od najliczniejszej) / "numer"; trzeci sposob (U7) - numer wpisany recznie: wybierz_kuwete
ID_RAMKA_PORANNA = "ramka_poranna"  # staly id komunikatu "ramka poranna nie jest podlaczona" (do A12)
ID_EXCEL = "excel"  # staly id komunikatu Excela po "Zamknij piec" (brak Excela, blad Excela, tryb cien)
ID_RAMKA_WIECZORNA = "ramka_wieczorna"  # staly id komunikatu "ramka wieczorna nie odpowiada" (E3-A12, tryb wieczor)
ID_TEST_LED = "ramki_test_led"
OKRES_STANU_RAMEK_S = 0.25  # co ile ``przetworz`` czyta stan klientow ramek (polaczenie, blad, plytka) - zmiana = nowy stan
CZAS_TEST_LED_S = 8.5  # ramka konczy test diod sama po 8 s (ramka.logika.CZAS_TEST_LED_S); potem plan pieca ponownie
ZDARZEN_RAMKI_W_PAMIECI = 4000  # tyle ostatnich kluczy zdarzen ramki z dziennika (dziennik ramki ma 2000 ostatnich zdarzen)
ZRODLA_RAMEK = {"W": "ramka_w", "P": "ramka_p"}  # kolumna ``zdarzenia.zrodlo`` wpisow zdarzen ramek
ZDARZENIA_KUWET_RAMKI = ("potwierdzenie", "cofniecie", "kuweta_wybrana")
CZAS_NA_POLACZENIE_RAMEK_S = 2.0  # komunikat "ramka nie odpowiada" dopiero po tylu sekundach od podlaczenia (recenzja PR #30 D7)
OKRES_PONOWIENIA_PLANU_S = 2.0  # P2: plan ramki porannej, ktorego nie dalo sie zbudowac - ponowienie co tyle sekund
OKRES_PONOWIENIA_ZDARZEN_S = 1.0  # r3 D-N1: zdarzenia ramki odlozone przy zajetej bazie - ponowienie najczesciej co tyle sekund
CZEKAJ_ZDARZENIA_MS = 150  # r3 D-N1 / r4 D-R3-1: zapis zdarzen ramki czeka na zajeta baze najwyzej tyle (ponizej progu petli okna 200 ms)
ZALEGLE_EXCELA_H = 48  # P5: piece zamkniete w ostatnich tylu godzinach z niezalatwionymi zleceniami Excela - przypomnienie przy starcie
ZALEGLE_EXCELA_PIECE = 5
MAX_PROJEKTOW_KUWETY = 60  # najwyzej tyle projektow zwraca ``projekty_kuwety``
MAX_KUWET_KOMUNIKATU = 40  # tyle numerow kuwet w komunikacie "Excel nie jest podlaczony" (reszta: "i N innych")
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
# poranek (E3-A7): przelacznik trybu, decyzje o pracach porannych, "Zamknij piec", kolejnosc i rozkladanie kuwet
POLECENIA_RANO = ("przelacz_tryb", "wybierz_kandydata", "przypisz_recznie", "cofnij_przypisanie", "zamknij_piec", "ustaw_kolejnosc",
                  "wybierz_kuwete", "potwierdz_kuwete", "cofnij_kuwete",
                  # runda 2 A6: pominiecie skanu, reczne zamkniecie braku, ponowne otwarcie pieca
                  "pomin_skan", "cofnij_pominiecie", "zamknij_brak_recznie", "cofnij_zamkniecie_reczne", "otworz_piec_ponownie",
                  # runda 4/5 A6: zapomniany "Zamknij piec" - zamkniecie i przeniesienie skanow nowego wsadu do nowego pieca i cofniecie
                  "zamknij_piec_i_przenies", "cofnij_przeniesienie")
POLECENIA = POLECENIA + POLECENIA_RANO
# ramki i Excel (E3-A12): test diod, przejecie ramki po "drugi laptop", okno "Excel: wskaz wiersz"
POLECENIA_A12 = ("test_led", "przejmij_ramke", "excel_zatwierdz", "excel_pomin", "excel_odswiez", "excel_pokaz", "excel_zamknij")
POLECENIA = POLECENIA + POLECENIA_A12
# sygnaly kontrolera do okna (``ZdarzenieKontrolera.typ``; w ``lacznik_qt``: stan_zmieniony, postep, komunikat, pytanie, zamkniety)
SYGNALY = ("stan", "postep", "komunikat", "pytanie", "zamkniety")
RODZAJE_PYTAN = ("ponowny_skan", "plytka_nie_z_trybu", "brak_numeru_plytki",
                 "nowy_wsad", "numer_nowy_wsad")  # rano (A6 runda 4): zamknac poprzedni piec i przeniesc skany? / zmienic numer mimo to?
LIMIT_SKANOWANIA_S = 180  # "start skanu" bez pliku dluzej niz tyle = skan przerwany: "Zamknij piec" znow dostepne (recenzja PR #26, P3)
# polecenia, po ktorych stan punktow zlecen (lista brakow) na pewno sie nie zmienil - bez ponownego liczenia ``braki()`` (P2);
# kazde inne udane polecenie uniewaznia pamiec brakow (polecenia plytki - tylko dla skanu wieczornego)
NIE_RUSZA_PUNKTOW = frozenset(("przelacz_tryb", "ustaw_kolejnosc", "wybierz_kuwete", "potwierdz_kuwete", "cofnij_kuwete", "wybierz_kandydata",
                               "przypisz_recznie", "cofnij_przypisanie", "pomin_skan", "cofnij_pominiecie", "odrzuc_ponowny_skan")
                              + POLECENIA_A12)


def tekst_komunikatu(rodzaj: str, **pola: Any) -> tuple:
    """(poziom, tytul, tekst) komunikatu ``rodzaj`` - ``statusy.tekst_komunikatu`` (od rundy 2 E3-A12 wszystkie teksty, takze ramek
    i Excela, sa w ``statusy`` - recenzja PR #30 D4)."""
    return ST.tekst_komunikatu(rodzaj, **pola)


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
    pominieta: bool = False  # wersja 3 (rano, A6 runda 2): skan pominiety przez osobe - nie liczy sie i nie blokuje
    na_ramce: bool = True  # wersja 3 (rano): plytka idzie do planu ramki porannej (kwadratowa poranna, numer 4-6)
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


# ----------------------------------------------------------------------------
# poranek (E3-A7): typy stanu ekranu porannego
# ----------------------------------------------------------------------------
@dataclasses.dataclass(frozen=True)
class Kandydat:
    """Kandydat pracy porannej (1. albo 2. projekt z dopasowania) - podglad do rozstrzygniecia pracy dwuznacznej. ``projekt_id``
    = punkt do wyboru poleceniem ``wybierz_kandydata(praca_id, sha16)``, gdy plik jest w indeksie dokladnie raz; None = tylko
    przypisanie reczne (``zlecen``: w ilu zleceniach jest ten plik - 0 = poza indeksem, 2+ = ten sam plik w kilku zleceniach).
    ``miniatura`` - PNG z indeksu (``cechy_stl``) albo None."""

    sha16: str
    pokrycie: float | None = None
    projekt_id: int | None = None
    zlecenie_id: int | None = None
    kuweta: str | None = None
    zeby: str | None = None
    typ: str | None = None
    zrodlo: str | None = None
    zlecen: int = 0
    miniatura: bytes | None = None


@dataclasses.dataclass(frozen=True)
class PracaRano:
    """Praca na plytce porannej (z ``session_rano.stan_pieca``). ``klasa``: pewna / przypisana / dwuznaczna / nieznana /
    poprawka / konflikt / do_powtorzenia (None = skan, ktory sie nie liczy); ``status`` - klucz ``statusy`` (wiersze poranne
    ``rano_*``, ``bialy``, ``dofrezowany``), ``kolor`` - klasa koloru z ``session_rano`` (zielony / zolty / bialy / bursztynowy /
    czerwony), ``rgb`` / ``podpis`` / ``opis`` - kolor i teksty ze ``statusy``. ``kuweta``, ``zeby``, ``miniatura`` - przypisanego
    projektu (podpis gniazda na mapie); ``kandydaci`` - do 2 (``Kandydat``); ``konflikt_z`` - inne miejsca tego samego projektu:
    krotki (numer plytki, gniazdo). ``dozwolone`` - polecenia, ktore maja teraz sens (wybierz_kandydata / przypisz_recznie /
    cofnij_przypisanie)."""

    praca_id: int
    skan_id: int
    gniazdo: int | None
    klasa: str | None
    status: str
    kolor: str | None
    rgb: str
    podpis: str
    opis: str = ""
    numer_plytki: int | None = None
    nr_fragmentu: int = 1
    liczona: bool = False
    kuweta: str | None = None
    zeby: str | None = None
    typ: str | None = None
    sha16: str | None = None
    projekt_id: int | None = None
    zlecenie_id: int | None = None
    przypisanie: str | None = None  # auto / decyzja / None
    decyzja: str | None = None  # wybor_kandydata / przypisanie_reczne / None
    decyzja_id: int | None = None  # id obowiazujacej decyzji (cofnij_przypisanie cofa dokladnie te)
    operator: str | None = None
    czas_decyzji: str | None = None
    kandydaci: tuple = ()
    miniatura: bytes | None = None
    konflikt: bool = False
    konflikt_z: tuple = ()
    zlecenie_odhaczone: bool = False
    domyka_dofrezowanie: bool = False
    kuweta_do_sprawdzenia: bool = False
    status_match: str | None = None
    dozwolone: tuple = ()


@dataclasses.dataclass(frozen=True)
class KuwetaRano:
    """Kuweta do rozlozenia (z prac rozpoznanych pieca - jak plan ramki porannej): ``prac`` na plytkach ``plytki``;
    ``potwierdzona`` = osoba potwierdzila rozlozenie (Enter), ``biezaca`` = te kuwete rozklada sie teraz (jej gniazda sa
    wyroznione na mapach), ``braki`` = zlecenie niekompletne w tym piecu (ramka pokazuje te numery osobno). ``gniazda`` -
    ((skan_id, nr gniazda), ...) prac liczonych do ``prac`` (ta sama regula; okno obwodzi dokladnie te gniazda - P4)."""

    kuweta: str
    prac: int
    plytki: tuple = ()
    potwierdzona: bool = False
    biezaca: bool = False
    braki: bool = False
    gniazda: tuple = ()


@dataclasses.dataclass(frozen=True)
class NowyWsad:
    """Skany nastepnego wsadu przy niezamknietym piecu (A6 runda 4, ``stan_pieca()["nowy_wsad"]``): numery plytek ze skanami
    o innych pracach i skany do przeniesienia poleceniem ``zamknij_piec_i_przenies``."""

    plytki: tuple = ()
    skany: tuple = ()


@dataclasses.dataclass(frozen=True)
class BrakujacyPunkt:
    """Punkt zlecenia, ktorego brakuje: ``stan`` (oczekuje / do_dofrezowania / brak_po_piecu), ``napis`` ze ``statusy``."""

    projekt_id: int
    sha16: str | None = None
    zeby: str | None = None
    typ: str | None = None
    stan: str | None = None
    napis: str = ""


@dataclasses.dataclass(frozen=True)
class ZlecenieRano:
    """Zlecenie dotkniete w piecu albo z listy brakow: kuweta, punkty, rozpoznane, ``brakujace`` (``BrakujacyPunkt``)."""

    zlecenie_id: int
    kuweta: str | None
    zrodlo: str | None = None
    punktow: int = 0
    rozpoznane: int = 0
    w_tym_piecu: int = 0
    kompletne: bool = False
    z_dofrezowaniem: bool = False
    brakujace: tuple = ()
    ostatni_piec: int | None = None


@dataclasses.dataclass(frozen=True)
class PoprawkaRano:
    """Zab dofrezowany do zlecenia juz odhaczonego (bursztyn, Z9) - tylko wpis w logu, Excel bez zmian."""

    praca_id: int
    skan_id: int
    numer_plytki: int | None
    gniazdo: int | None
    kuweta: str | None = None
    zeby: str | None = None
    zlecenie_odhaczone: bool = False


@dataclasses.dataclass(frozen=True)
class ProjektPuli:
    """Projekt (punkt zlecenia) do przypisania recznego - wynik ``projekty_kuwety(kuweta)``; bez nazw folderow i plikow."""

    projekt_id: int
    zlecenie_id: int
    kuweta: str | None
    zeby: str | None = None
    typ: str | None = None
    zrodlo: str | None = None
    sha16: str | None = None
    stan: str | None = None
    miniatura: bytes | None = None


@dataclasses.dataclass(frozen=True)
class StanRano:
    """Stan ekranu porannego: piec biezacy otwarty, a bez niego - ostatnio zamkniety piec (z jawnym ``sesja_pieca_id``, takze
    z poprzedniej doby; None = nie bylo jeszcze pieca). ``plytki`` - skany pieca (``Plytka``; gniazda ``Gniazdo`` z ``prace`` =
    ``PracaRano``; ``podpis`` gniazda = numer kuwety albo napis statusu; ``liczniki`` plytki - po klasie pracy porannej).
    ``kompletne`` / ``braki`` - zlecenia dotkniete w piecu (w otwartym piecu PROWIZORYCZNE, w zamknietym z zapisu "Zamknij piec");
    ``braki_biezace`` - trwala lista brakow ze wszystkich piecow; ``blokady`` - dlaczego "Zamknij piec" teraz odmowi (takze
    ``zajety``: "analiza_trwa" / "skanowanie_trwa" - recenzja PR #26 P3, D1); ``dozwolone`` - "zamknij_piec" /
    "zamknij_piec_i_przenies" / "otworz_piec_ponownie", gdy maja sens; ``kuwety`` w kolejnosci ``kolejnosc`` z ``kuweta_biezaca``
    (stala - zmienia ja tylko osoba: Enter, Backspace, numer, kolejnosc - B1) i ``kuweta_do_cofniecia`` (ostatnia potwierdzona);
    ``wynik`` - wynik "Zamknij piec" (piec zamkniety) albo None; ``nowy_wsad`` - ``NowyWsad`` albo None; ``ostatni_zamkniety`` -
    przy otwartym piecu: ostatnio zamkniety piec (``StanRano`` bez plytek, lista do Excela - P1) albo None. ``ramka`` / ``excel`` -
    czy podlaczone (do A12: False, program dziala wedlug ekranu)."""

    sesja_pieca_id: int | None = None
    plan_id: str | None = None
    data: str | None = None
    nr_w_dniu: int | None = None
    otwarto: str | None = None
    zamknieto: str | None = None
    zamknal: str | None = None
    otwarty: bool = False
    z_poprzedniej_doby: bool = False
    plytki: tuple = ()
    liczniki: dict = dataclasses.field(default_factory=ZamrozonySlownik)
    nierozstrzygniete: dict = dataclasses.field(default_factory=ZamrozonySlownik)
    kompletne: tuple = ()
    braki: tuple = ()
    poprawki: tuple = ()
    konflikty: tuple = ()
    blokady: tuple = ()
    dozwolone: tuple = ()
    kolejnosc: str = "liczba"
    kuwety: tuple = ()
    kuweta_biezaca: str | None = None
    braki_biezace: tuple = ()
    piece: tuple = ()
    wynik: dict | None = None
    ostrzezenia: tuple = ()  # napisy bez blokady (A6: plytka okragla poza ramka, piec niezamkniety z poprzedniej doby)
    inne_otwarte_piece: tuple = ()  # plan_id innych otwartych piecow
    ramka: bool = False
    excel: bool = False
    zajety: str | None = None
    kuweta_do_cofniecia: str | None = None
    nowy_wsad: NowyWsad | None = None
    ostatni_zamkniety: "StanRano | None" = None

    def plytka(self, skan_id: int) -> Plytka | None:
        return next((p for p in self.plytki if p.skan_id == skan_id), None)

    def obwodka(self, skan_id: int) -> frozenset:
        """Numery gniazd plytki ``skan_id`` z pracami biezacej kuwety (``KuwetaRano.gniazda``) - okno tylko je rysuje."""
        k = next((x for x in self.kuwety if x.biezaca), None)
        return frozenset(nr for s, nr in (k.gniazda if k is not None else ()) if s == skan_id)

    def praca(self, praca_id: int) -> PracaRano | None:
        return next((x for p in self.plytki for x in p.prace if x.praca_id == praca_id), None)


@dataclasses.dataclass(frozen=True)
class StanRamki:
    """Stan jednej ramki dla okna (E3-A12, z ``indicate.KlientRamki.stan()``): ``polaczona``, ``blad`` (kod: ``brak_polaczenia`` jako
    ``komunikat``, ``zly_klucz``, ``inny_laptop``, ``blad_sprzetu``, ``plan_odrzucony`` ...), ``komunikat`` (tekst roboczy indicate),
    ``plytka`` (numer plytki na ramce), ``tryb_ramki``, ``plan_przyjety``, ``wstrzymane`` (drugi laptop - plan dopiero po
    ``przejmij_ramke``), ``potwierdzone`` (liczba potwierdzen kuwet na ramce porannej), ``ostrzezenia`` (kalibracja, identyfikator)."""

    rola: str
    polaczona: bool = False
    blad: str | None = None
    komunikat: str | None = None
    plytka: int | None = None
    tryb_ramki: str | None = None
    plan_przyjety: bool = False
    wstrzymane: bool = False
    potwierdzone: int = 0
    ostrzezenia: tuple = ()
    utracone: int = 0  # zdarzenia ramki utracone (dziennik ramki przepelniony w czasie przerwy) - podpowiedz paska (D7)
    przepelnienie: int = 0


@dataclasses.dataclass(frozen=True)
class StanRamek:
    """Ramki stanowiska (``stan.ramki``; None = program bez ramek): ``wieczorna`` / ``poranna`` (``StanRamki`` albo None, gdy tej ramki
    nie ma w ustawieniach), ``test_led`` - trwa test diod."""

    wieczorna: StanRamki | None = None
    poranna: StanRamki | None = None
    test_led: bool = False


@dataclasses.dataclass(frozen=True)
class PozycjaExcel:
    """Jedno zlecenie kompletne w oknie "Excel: wskaz wiersz" (E3-A12, z ``excel.Pozycja``): ``nr`` - numer pozycji do polecen
    ``excel_zatwierdz`` / ``excel_pomin`` i zapytania ``excel_szczegoly``; ``klasa`` (``jeden_wiersz`` / ``juz_odhaczone`` /
    ``wskaz_wiersz``), ``wiersz`` proponowany (None = wskaz), ``regula``, ``powod`` (bez nazwisk), ``do_sprawdzenia`` (wybor bez
    zgodnej nazwy - okno oznacza wyraznie), ``data`` wiersza, ``kandydatow``, ``zalatwiona`` i ``wynik`` (wpis logu)."""

    nr: int
    kuweta: str | None
    klasa: str
    wiersz: int | None
    regula: int
    powod: str = ""
    do_sprawdzenia: bool = False
    data: str | None = None
    kandydatow: int = 0
    zalatwiona: bool = False
    wynik: str | None = None
    zlecenie_id: int | None = None  # P4: tozsamosc pozycji w poleceniach (z ``sesja_pieca_id``) - nie numer na liscie
    sesja_pieca_id: int | None = None
    poprzedni_blad: bool = False  # D9: poprzednia proba zapisu tego zlecenia skonczyla sie wpisem "blad" (zapis mogl dojsc)
    poprzedni_wiersz: int | None = None


@dataclasses.dataclass(frozen=True)
class KandydatExcel:
    """Wiersz arkusza - kandydat (zapytanie ``excel_szczegoly``): ``nazwa`` = kolumna H (DANE OSOBOWE - tylko na ekran laptopa,
    nigdy w stanie, dzienniku ani komunikatach), ``kolor_b`` - wypelnienie pola B (``#rrggbb`` albo None), ``zielone``."""

    wiersz: int
    data: str | None = None
    numer_b: str = ""
    kuweta: str = ""
    nazwa: str = ""
    kolor_b: str | None = None
    zielone: bool = False


@dataclasses.dataclass(frozen=True)
class SzczegolyExcel:
    """Szczegoly pozycji okna Excela (zapytanie, nie stan): ``folder`` zlecenia i ``kandydaci`` (``KandydatExcel``) - tylko na ekran."""

    nr: int
    folder: str = ""
    kandydaci: tuple = ()


@dataclasses.dataclass(frozen=True)
class StanExcel:
    """Excel (``stan.excel``; None = program bez Excela): ``tryb`` ("pytaj" / "cien"), piec, ktorego dotycza ``pozycje``
    (``PozycjaExcel``), ``widoczne`` - okno "Excel: wskaz wiersz" ma byc pokazane (sa pozycje do zalatwienia, osoba go nie zamknela),
    ``blad`` - ostatni blad Excela (np. Excel nie uruchomiony), ``ostrzezenia`` (z ustawien, skoroszyt / arkusz uzyte),
    ``do_zalatwienia`` - liczba pozycji bez wpisu w logu."""

    tryb: str = "pytaj"
    sesja_pieca_id: int | None = None
    nr_w_dniu: int | None = None
    data: str | None = None
    pozycje: tuple = ()
    widoczne: bool = False
    blad: str | None = None
    ostrzezenia: tuple = ()
    do_zalatwienia: int = 0
    w_toku: int = 0  # P1: kroki Excela czekajace na kolejne obiegi petli okna (propozycje, poprawki, "juz odhaczone")
    zalegle: tuple = ()  # P5: inne piece z niezalatwionymi zleceniami: (sesja_pieca_id, nr_w_dniu, data, ile)


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
    rano: StanRano | None = None  # wersja 3 (E3-A7): stan pieca, gdy ``tryb`` == "rano"; w trybie "wieczor" None
    ramki: StanRamek | None = None  # wersja 4 (E3-A12): ramki stanowiska (None = program bez ramek)
    excel: StanExcel | None = None  # wersja 4 (E3-A12): Excel i okno "Excel: wskaz wiersz" (None = program bez Excela)

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

    def podaj_numer_plytki(self, skan_id: int, numer: int, mimo_nowego_wsadu: bool = False) -> Odpowiedz:
        """Numer plytki podany recznie. Rano (A6 runda 4): zmiana numeru plytki ze skanami innego wsadu jest odrzucana - kontroler
        pyta (``Pytanie`` ``numer_nowy_wsad``); ``mimo_nowego_wsadu`` True tylko po jawnym potwierdzeniu osoby."""
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

    # --- poranek (wersja 3, E3-A7)
    def przelacz_tryb(self, tryb: str) -> Odpowiedz:
        """Tryb pracy programu: ``wieczor`` / ``rano`` (Z1 - wybiera czlowiek; nie wymaga osoby). Nowe skany ida do sesji
        tego trybu; skany juz w kolejce zostaja w trybie, w ktorym je zauwazono. ``dane`` = tryb."""
        raise NotImplementedError

    def wybierz_kandydata(self, praca_id: int, sha16: str) -> Odpowiedz:
        """Praca dwuznaczna rozstrzygnieta kliknieciem: ``sha16`` = 1. albo 2. kandydat (``PracaRano.kandydaci``)."""
        raise NotImplementedError

    def przypisz_recznie(self, praca_id: int, projekt_id: int | None = None) -> Odpowiedz:
        """Przypisanie reczne pracy porannej do projektu (``projekty_kuwety``); ``None`` = "bez projektu" (praca nieznana,
        rozstrzygniecie konfliktu)."""
        raise NotImplementedError

    def cofnij_przypisanie(self, praca_id: int, decyzja_id: int | None = None) -> Odpowiedz:
        """Cofa decyzje o pracy porannej; ``decyzja_id`` (``PracaRano.decyzja_id``) - dokladnie te (podwojne klikniecie nie cofa
        drugiej)."""
        raise NotImplementedError

    def zamknij_piec(self, sesja_pieca_id: int | None = None) -> Odpowiedz:
        """"Zamknij piec" pokazanego pieca (``StanRano.sesja_pieca_id``; None = piec biezacy): ``dane`` = wynik (zlecenia
        kompletne, braki, poprawki - jak ``session_rano.zamknij_piec``). Odmowa, dopoki trwa analiza skanu (``analiza_trwa``)
        albo skanowanie (``skanowanie_trwa``: od "start skanu" do przyjecia pliku, najwyzej ``LIMIT_SKANOWANIA_S``)."""
        raise NotImplementedError

    def zamknij_piec_i_przenies(self, sesja_pieca_id: int, skany: tuple) -> Odpowiedz:
        """Zapomniany "Zamknij piec" (A6 runda 4): skany nastepnego wsadu (``StanRano.nowy_wsad.skany``) wychodza z pieca, piec
        jest zamykany bez nich, skany trafiaja do nowego pieca. Te same odmowy co ``zamknij_piec`` i odmowy A6 (tylko ogon nowszych
        skanow, cala para zastapienia, piec biezacy otwarty) - jako komunikat."""
        raise NotImplementedError

    def cofnij_przeniesienie(self, sesja_pieca_id: int) -> Odpowiedz:
        """Cofa ``zamknij_piec_i_przenies`` (A6 runda 5): piec ``sesja_pieca_id`` powstal z przeniesienia (``StanRano.dozwolone``
        zawiera "cofnij_przeniesienie") - skany wracaja do poprzedniego pieca, ktory znow jest otwarty."""
        raise NotImplementedError

    def otworz_piec_ponownie(self, sesja_pieca_id: int) -> Odpowiedz:
        """Cofa "Zamknij piec" ostatniego pieca (pomylka; A6 runda 2)."""
        raise NotImplementedError

    def pomin_skan(self, skan_id: int) -> Odpowiedz:
        """Skan poranny nie nalezy do pieca (zla plytka, bez wyniku, zly numer) - nie liczy sie i nie blokuje "Zamknij piec"."""
        raise NotImplementedError

    def cofnij_pominiecie(self, skan_id: int) -> Odpowiedz:
        raise NotImplementedError

    def zamknij_brak_recznie(self, projekt_id: int, powod: str) -> Odpowiedz:
        """Reczne zamkniecie brakujacego punktu z listy brakow; ``powod`` - kod z ``session_rano.POWODY_ZAMKNIECIA``."""
        raise NotImplementedError

    def cofnij_zamkniecie_reczne(self, projekt_id: int) -> Odpowiedz:
        raise NotImplementedError

    def ustaw_kolejnosc(self, kolejnosc: str) -> Odpowiedz:
        """Kolejnosc kuwet do rozlozenia (U7): ``liczba`` (od najliczniejszej) albo ``numer``."""
        raise NotImplementedError

    def wybierz_kuwete(self, kuweta: str) -> Odpowiedz:
        """Kuweta wpisana recznie (U7, trzeci sposob) staje sie biezaca - musi lezec na plytkach pieca."""
        raise NotImplementedError

    def potwierdz_kuwete(self, kuweta: str) -> Odpowiedz:
        """Enter: kuweta ``kuweta`` (biezaca POKAZANA na ekranie - ``StanRano.kuweta_biezaca``) rozlozona - wpis w dzienniku,
        biezaca staje sie nastepna nierozlozona. Odmowa ``kuweta_zmienila_sie`` (bez wpisu), gdy biezaca jest juz inna (B1)."""
        raise NotImplementedError

    def cofnij_kuwete(self, kuweta: str) -> Odpowiedz:
        """Backspace: cofa potwierdzenie kuwety ``kuweta`` (``StanRano.kuweta_do_cofniecia`` - ostatnia potwierdzona) - ta kuweta
        znow jest biezaca. Odmowa ``kuweta_zmienila_sie``, gdy ostatnia potwierdzona jest inna."""
        raise NotImplementedError

    def projekty_kuwety(self, kuweta: str) -> tuple:
        """Zapytanie (nie polecenie): projekty zlecenia o tej kuwecie do przypisania recznego (``ProjektPuli``)."""
        raise NotImplementedError

    # --- ramki i Excel (wersja 4, E3-A12)
    def test_led(self) -> Odpowiedz:
        """"Test LED": podlaczone ramki pokazuja przez kilka sekund kolejne kolory na wszystkich diodach (potem wraca plan)."""
        raise NotImplementedError

    def przejmij_ramke(self, rola: str) -> Odpowiedz:
        """Ramka ``rola`` ("W" / "P") wstrzymana po "drugi laptop" albo "zly klucz" - decyzja osoby: ten laptop ja przejmuje."""
        raise NotImplementedError

    def excel_zatwierdz(self, sesja_pieca_id: int, zlecenie_id: int, wiersz: int | None = None) -> Odpowiedz:
        """Okno "Excel: wskaz wiersz": zatwierdzenie pozycji (piec + zlecenie z ``StanExcel.pozycje`` - P4) - wiersz proponowany albo
        ``wiersz`` wskazany z kandydatow. Tylko po kliknieciu osoby (tryb "pytaj"); ``dane`` = wpis logu (bez nazw)."""
        raise NotImplementedError

    def excel_pomin(self, sesja_pieca_id: int, zlecenie_id: int) -> Odpowiedz:
        """Pozycja (piec + zlecenie) pominieta (osoba zaznaczy w Excelu recznie) - wpis "pominieto" w logu."""
        raise NotImplementedError

    def excel_odswiez(self) -> Odpowiedz:
        """Propozycje pieca od nowa (swiezy odczyt arkusza) - po bledzie Excela albo zmianie arkusza."""
        raise NotImplementedError

    def excel_pokaz(self, sesja_pieca_id: int | None = None) -> Odpowiedz:
        """Okno Excela dla zamknietego pieca (None = ostatni): zlecenia kompletne bez wpisu w logu Excela (takze po restarcie)."""
        raise NotImplementedError

    def excel_zamknij(self) -> Odpowiedz:
        """"Pozniej": okno Excela znika (pozycje zostaja - ``excel_pokaz``)."""
        raise NotImplementedError

    def excel_szczegoly(self, sesja_pieca_id: int, zlecenie_id: int):
        """Zapytanie (nie polecenie): ``SzczegolyExcel`` pozycji (folder i kandydaci z H - tylko na ekran) albo None."""
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

    def __init__(self, sesja: SE.Sesja, ust: dict | None = None, *, tryb: str | None = None, zegar: Callable[[], dt.datetime] | None = None):
        self.sesja = sesja
        self.ust = ust
        self.tryb = SE.sprawdz_tryb(tryb if tryb is not None else self._wczytaj_tryb())  # None = ostatni wybor z dziennika (E3-A7)
        prog = ((ust or {}).get("match") or {}).get("prog_ostrzezenia_pokrycie", SR.PROG_KANDYDATA)
        self.rano = SR.SesjaRano(sesja, prog_kandydata=prog)  # sesja poranna (A6) na tej samej bazie
        self._kolejnosc = SR.KOLEJNOSCI[0]
        self._kuwety_rozlozone: dict[str, list] = {}  # plan_id pieca -> kuwety potwierdzone (stos; dziennik: kuweta_potwierdzona / cofnieta)
        self._kuweta_biezaca: dict[str, str | None] = {}  # plan_id -> kuweta biezaca (stala; zmienia ja osoba - recenzja PR #26, B1)
        self._wersja_punktow = 0  # licznik zdarzen, ktore moga zmienic stan punktow (pamiec ``braki()`` - P2)
        self._pamiec_brakow: tuple | None = None
        self._pamiec_zamknietych: dict = {}  # sesja_pieca_id -> (klucz, stan_pieca, wynik_pieca) pieca zamknietego
        self._numer_mimo: tuple | None = None  # (skan_id, numer) czekajacy na potwierdzenie "zmien numer mimo nowego wsadu"
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
        # ramki i Excel (E3-A12): podlaczane przez ``podlacz_ramki`` / ``podlacz_excel`` (Aplikacja - z ustawien przy starcie)
        self.ramki = None
        self.excel = None
        self._stan_ramek: StanRamek | None = None
        self._ramki_kontrola = 0.0
        self._klucze_ramek: dict = {}  # zrodlo -> klucze zdarzen ramki zapisanych w dzienniku (start_id:nr)
        self._klucze_od: dict = {}  # zrodlo -> najwyzszy id dziennika w chwili odczytu kluczy
        self._plan_p: str | None = None  # plan_id planu pieca wyslanego do ramki porannej
        self._plan_p_podpis: tuple | None = None
        self._plany_wyslane: set = set()
        self._test_led_do = 0.0
        self._znacznik_spacji = None  # ramka W: znacznik Spacji czekajacy na plik skanu
        self._w_ostatni = None  # ramka W: znacznik ostatniego skanu
        self._w_do_wyslania: tuple | None = None  # (znacznik, skan_id) - wynik do wyslania po zbudowaniu stanu
        self._w_aktywny: tuple | None = None  # (znacznik, skan_id, obraz wyslany) wyniku na ramce W
        self._excel_pozycje: list = []
        self._excel_piec: tuple | None = None  # (sesja_pieca_id, nr_w_dniu, data) pieca pozycji Excela
        self._excel_blad: str | None = None
        self._excel_widoczne = False
        self._excel_kolejka: collections.deque = collections.deque()  # P1: kroki Excela, jeden na obieg petli okna
        self._excel_zalegle: dict = {}  # P5: sesja_pieca_id -> (nr_w_dniu, data, ile) piecow z niezalatwionymi zleceniami
        self._excel_bledy: dict = {}  # D9: zlecenie_id -> wiersz ostatniego wpisu "blad" w excel_zapisy pokazanego pieca
        self._plan_p_dane: dict | None = None  # ostatni plan pieca wyslany do ramki (kuwety -> plytki: rozlozenie z ramki)
        self._plan_p_ponow = False  # P2: planu nie dalo sie zbudowac - ponowienie
        self._plan_p_ponow_od = 0.0
        self._plany_czekaja: dict = {}  # P7: plan_id pieca zamknietego -> wersja planu laptopa w chwili zamkniecia
        self._zdarzenia_ponow: list = []  # D2: zdarzenia ramki niezapisane (baza zajeta) - ponowienie
        self._zdarzenia_ponow_od = 0.0  # r3 D-N1: najwczesniej wtedy kolejna proba
        self._excel_jawnie = False  # r3 P-N3: okno pokazane jawnie (``excel_pokaz``) - widoczne takze bez pozycji, gdy sa zalegle piece
        self._odswiez_potrzebne = False
        self._ramki_od = 0.0
        self._ramki_po_czasie = False

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
        self._po_odswiezeniu(stan)  # E3-A12: plan ramki porannej, wynik na ramce wieczornej
        return stan

    def _odswiez_zywe(self, sygnal: str = "stan") -> None:
        """Podmienia w stanie tylko czesc "zywa" (postep, kolejka, pula, skaner) - bez czytania bazy. Rano: gdy zmienila sie
        blokada "Zamknij piec" (analiza / skanowanie - ``StanRano.zajety``), caly stan od nowa (jedno zrodlo blokady - P3, D1)."""
        if self._stan is None or self._zamkniety:
            return
        zywe = self._stan_zywy()
        if self._stan.rano is not None and self._zajety(zywe) != self._stan.rano.zajety:
            self._odswiez()
            return
        self._wersja += 1
        self._stan = dataclasses.replace(self._stan, wersja=self._wersja, ramki=self._stan_ramek, **zywe)
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
        try:
            n = self._przetworz_ramki()  # E3-A12: krok Excela, zdarzenia i stan ramek (zegar okna)
        except Exception:  # noqa: BLE001 - recenzja PR #30 D2: blad ramek / Excela nie przerywa obiegu
            LOG.exception("kontroler: blad obslugi ramek / Excela")
            n = 0
        if self._sprawdz_zmiane():
            self._odswiez()
            return n + 1
        return n + (1 if self._sprawdz_zajetosc() else 0)

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
        rano = None
        if self.tryb == TRYB_RANO:  # E3-A7: stan pieca; pytania i komunikaty plytek porannych w tych samych listach co wieczorne
            try:
                rano = self._stan_rano()
            except B.BladBazy:
                raise  # baza zajeta: caly stan zostaje poprzedni (jak wieczorem)
            except Exception:  # noqa: BLE001 - recenzja PR #26, D13: blad sesji porannej nie zatrzymuje odswiezania wieczornej czesci
                LOG.exception("kontroler: stanu pieca nie da sie odczytac - zostaje poprzedni")
                rano = self._stan.rano if self._stan is not None and self._stan.rano is not None else StanRano(kolejnosc=self._kolejnosc)
                rano = dataclasses.replace(rano, zajety=self._zajety())  # bez ponawiania przy kazdym tyknieciu (``_sprawdz_zajetosc``)
                trwale.append(self._nowy_komunikat("rano_niedostepny", "rano_niedostepny", trwaly=True, czas=sw["data"]))
            for plytka in rano.plytki:
                pytania += [p for p in plytka.pytania if not p.ukryte]
                trwale += [k for k in plytka.komunikaty if not k.ukryte]
            pytania += [q for q in self._pytania_rano(rano) if not q.ukryte]
            if not rano.ramka and ID_RAMKA_PORANNA not in self._ukryte and self._ramki_po_czasie_na_polaczenie():
                trwale.append(self._nowy_komunikat(ID_RAMKA_PORANNA, "ramka_niedostepna", czas=sw["data"]))
        if (self.tryb == TRYB_WIECZOR and self._klient("W") is not None and ID_RAMKA_WIECZORNA not in self._ukryte
                and self._ramki_po_czasie_na_polaczenie()):
            w = self._stan_ramek.wieczorna if self._stan_ramek is not None else None
            if w is None or not w.polaczona:  # E3-A12: bez ramki wieczornej program dziala wedlug ekranu
                trwale.append(self._nowy_komunikat(ID_RAMKA_WIECZORNA, "ramka_wieczorna_niedostepna", czas=sw["data"]))
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
            lista_zapisana=self._lista_czas, rano=rano, ramki=self._stan_ramek, excel=self._stan_excel(), **self._stan_zywy())

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

    # --- poranek (E3-A7): stan pieca dla ekranu porannego ---------------------------------------
    def _pytania_rano(self, rano: StanRano) -> list:
        """Pytania pieca (A6 runda 4): "Poprzedni piec nie zostal zamkniety - zamknac i przeniesc nowe skany?" (``nowy_wsad``) i
        "Zmienic numer plytki mimo to?" (``numer_nowy_wsad`` - po odrzuconej zmianie numeru plytki ze skanem innego wsadu)."""
        wynik = []
        if self._numer_mimo is not None:
            skan_id, numer = self._numer_mimo
            p = rano.plytka(skan_id)
            if p is None or not rano.otwarty or p.numer == numer or "podaj_numer_plytki" not in p.dozwolone:
                self._numer_mimo = None
            else:
                id_ = f"numer_nowy_wsad:{skan_id}:{numer}"
                poziom, tytul, tekst = ST.tekst_pytania("numer_nowy_wsad", stary=p.numer, numer=numer)
                wynik.append(Pytanie(id=id_, rodzaj="numer_nowy_wsad", skan_id=skan_id, poziom=poziom, tytul=tytul, tekst=tekst, numer_plytki=p.numer,
                                     ukryte=id_ in self._ukryte,
                                     odpowiedzi=(Przycisk("podaj_numer_plytki", ST.PRZYCISK_NUMER_MIMO.format(numer=numer), (skan_id, numer, True)),
                                                 Przycisk("zamknij_pytanie", ST.PRZYCISK_NUMER_BEZ_ZMIANY, (id_,)))))
        nw = rano.nowy_wsad
        if rano.otwarty and nw is not None and nw.skany:
            id_ = f"nowy_wsad:{rano.sesja_pieca_id}:{','.join(map(str, nw.skany))}"
            poziom, tytul, tekst = ST.tekst_pytania("nowy_wsad", plytki=", ".join(map(str, nw.plytki)), skanow=len(nw.skany))
            wynik.append(Pytanie(id=id_, rodzaj="nowy_wsad", skan_id=nw.skany[0], poziom=poziom, tytul=tytul, tekst=tekst, ukryte=id_ in self._ukryte,
                                 odpowiedzi=(Przycisk("zamknij_piec_i_przenies", ST.PRZYCISKI["zamknij_piec_i_przenies"], (rano.sesja_pieca_id, tuple(nw.skany))),
                                             Przycisk("zamknij_pytanie", ST.PRZYCISKI["zamknij_pytanie"], (id_,)))))
        return wynik

    def _wczytaj_tryb(self) -> str:
        """Ostatni tryb wybrany przez czlowieka (dziennik: ``tryb_zmieniony``, zrodlo ``ui``); bez wpisu - ``wieczor``. Tryb nie
        zmienia sie sam (Z1), wiec po restarcie programu wraca ten, ktory byl."""
        try:
            w = self.sesja.baza.wiersz("SELECT dane FROM zdarzenia WHERE zrodlo = 'ui' AND typ = 'tryb_zmieniony' ORDER BY id DESC LIMIT 1")
            tryb = json.loads(w["dane"]).get("tryb") if w and w["dane"] else None
        except (ValueError, TypeError, AttributeError, sqlite3.Error, B.BladBazy):
            tryb = None
        return tryb if tryb in TRYBY else TRYB_WIECZOR

    def _miniatury(self, shas) -> dict:
        """``sha16`` -> miniatura PNG z indeksu (``cechy_stl.miniatura``); znalezione sa pamietane (miniatura pliku sie nie zmienia)."""
        if not hasattr(self, "_pamiec_miniatur"):
            self._pamiec_miniatur: dict = {}
        brak = sorted({s for s in shas if s and s not in self._pamiec_miniatur})
        for i in range(0, len(brak), 500):
            czesc = brak[i:i + 500]
            for w in self.sesja.baza.wiersze(f"SELECT sha16, miniatura FROM cechy_stl WHERE miniatura IS NOT NULL AND sha16 IN ({', '.join('?' * len(czesc))})",
                                             tuple(czesc)):
                self._pamiec_miniatur[w["sha16"]] = bytes(w["miniatura"])
        return {s: self._pamiec_miniatur[s] for s in shas if s in self._pamiec_miniatur}

    @staticmethod
    def _norm_kuweta(kuweta: str) -> str:
        """Numer kuwety wpisany recznie: bez spacji i zer wiodacych (w indeksie kuweta jest bez zer - A4), z "#" zlecen prywatnych."""
        k = kuweta.strip().replace(" ", "")
        m = re.fullmatch(r"(#?)0*(\d+)", k)
        return f"{m[1]}{int(m[2])}" if m else k

    def _rozlozone(self, plan_id: str) -> list:
        """Kuwety pieca ``plan_id`` potwierdzone jako rozlozone (stos - Backspace cofa ostatnia); po restarcie z dziennika. Od rundy 2
        E3-A12 takze Enter / Backspace na ramce porannej (wpisy ``ramka_p`` z polem ``kuweta_rozlozona`` / ``kuweta_cofnieta``)."""
        if plan_id not in self._kuwety_rozlozone:
            stos: list = []
            for w in self.sesja.baza.wiersze("SELECT zrodlo, typ, dane FROM zdarzenia WHERE (zrodlo = 'ui' AND typ IN ('kuweta_potwierdzona', "
                                             "'kuweta_cofnieta')) OR (zrodlo = 'ramka_p' AND typ IN ('potwierdzenie', 'cofniecie')) ORDER BY id"):
                try:
                    d = json.loads(w["dane"])
                except (TypeError, ValueError):
                    continue
                if d.get("plan_id") != plan_id:
                    continue
                if w["zrodlo"] == "ramka_p":
                    if d.get("kuweta_rozlozona"):
                        stos.append(d["kuweta_rozlozona"])
                    elif d.get("kuweta_cofnieta") in stos:
                        stos.reverse()
                        stos.remove(d["kuweta_cofnieta"])
                        stos.reverse()
                    continue
                if w["typ"] == "kuweta_potwierdzona":
                    stos.append(d.get("kuweta"))
                elif d.get("kuweta") in stos:
                    stos.reverse()
                    stos.remove(d.get("kuweta"))
                    stos.reverse()
            self._kuwety_rozlozone[plan_id] = stos
        return self._kuwety_rozlozone[plan_id]

    def _kuwety_pieca(self, st: dict) -> tuple:
        """Kuwety do rozlozenia w kolejnosci ``self._kolejnosc`` - te same reguly co plan ramki (``session_rano.plan_plytek``):
        najnowszy aktywny skan kazdego numeru plytki, prace rozpoznane z kuweta zgodna z protokolem ramki, gniazdo z jedna praca.
        Zwraca (lista kuwet: (kuweta, prac, plytki, gniazda), kuweta biezaca, kuweta do cofniecia).

        Biezaca jest STALA (recenzja PR #26, B1): zostaje, dopoki lezy na plytkach pieca - nowy skan albo decyzja zmieniajaca
        liczebnosc kuwet jej nie przejmuje; zmienia ja tylko osoba (Enter, Backspace, numer kuwety, kolejnosc). Bez biezacej -
        pierwsza nierozlozona w kolejnosci."""
        po_numerze: dict = {}
        for s in st["skany"]:
            if s["aktywny"] and s["numer_plytki"] is not None and not s.get("pominiety"):
                po_numerze.setdefault(s["numer_plytki"], []).append(s)
        liczba: dict = {}
        plytki: dict = {}
        gniazda: dict = {}
        zdublowane = set(st.get("zdublowane_plytki") or ())
        for n, lista in po_numerze.items():
            if n in zdublowane or len(lista) > 1:  # dwa skany z jednym numerem: blokada (A6) - plytka czeka na rozstrzygniecie
                continue
            s = lista[0]  # plytka okragla (poza ramka) tez: rozklada sie ja wedlug ekranu (ostrzezenie A6)
            w_gniazdach: dict = {}
            for p in s["prace"]:
                if p["gniazdo"] is not None:
                    w_gniazdach.setdefault(p["gniazdo"], []).append(p)
            for prace in w_gniazdach.values():
                p = prace[0]
                if len(prace) == 1 and p["klasa"] in SR.KLASY_Z_KUWETA and p["kuweta"] and SR.WZOR_KUWETY_RAMKI.fullmatch(p["kuweta"]):
                    liczba[p["kuweta"]] = liczba.get(p["kuweta"], 0) + 1
                    plytki.setdefault(p["kuweta"], set()).add(n)
                    gniazda.setdefault(p["kuweta"], []).append((s["id"], p["gniazdo"]))
        if self._kolejnosc == "liczba":
            porzadek = sorted(liczba, key=lambda k: (-liczba[k], SR._klucz_kuwety(k)))
        else:
            porzadek = sorted(liczba, key=SR._klucz_kuwety)
        biezaca = do_cofniecia = None
        if st["otwarty"]:
            stos = self._rozlozone(st["plan_id"])
            do_cofniecia = stos[-1] if stos else None
            biezaca = self._kuweta_biezaca.get(st["plan_id"])
            if biezaca not in liczba:  # pierwsza albo poprzednia zniknela z plytek (np. prace przypisane gdzie indziej)
                biezaca = next((k for k in porzadek if k not in stos), None)
                self._kuweta_biezaca[st["plan_id"]] = biezaca
        return tuple((k, liczba[k], tuple(sorted(plytki[k])), tuple(sorted(gniazda[k]))) for k in porzadek), biezaca, do_cofniecia

    @staticmethod
    def _zlecenie_rano(z: dict) -> ZlecenieRano:
        braki = tuple(BrakujacyPunkt(projekt_id=b["projekt_id"], sha16=b.get("sha16"), zeby=b.get("zeby"), typ=b.get("typ"), stan=b.get("stan"),
                                     napis=ST.STANY_PUNKTU.get(b.get("stan"), b.get("stan") or "")) for b in z.get("brakujace") or ())
        return ZlecenieRano(zlecenie_id=z["zlecenie_id"], kuweta=z.get("kuweta"), zrodlo=z.get("zrodlo"), punktow=z.get("punktow", 0),
                            rozpoznane=z.get("rozpoznane", 0), w_tym_piecu=z.get("w_tym_piecu", 0), kompletne=bool(z.get("kompletne")),
                            z_dofrezowaniem=bool(z.get("z_dofrezowaniem")), brakujace=braki, ostatni_piec=z.get("ostatni_piec"))

    def _praca_rano(self, p: dict, s: dict, otwarty: bool, mini: dict, konflikty: dict) -> PracaRano:
        klasa = p["klasa"]
        if klasa == "poprawka" and not p["zlecenie_odhaczone"]:
            st = ST.status("rano_juz_rozpoznany")  # A6 runda 2 (D2): zab juz rozpoznany wczesniej, zlecenie wciaz z brakami
        elif klasa is not None:
            st = ST.status_rano(klasa)
        else:
            st = ST.status("plytka_nie_z_trybu" if s["status"] == SE.STATUS_PLYTKA_NIE_Z_TRYBU else "nieaktywny")
        kandydaci = []
        for k in p["kandydaci"]:
            projekty = k.get("projekty") or []
            pierwszy = projekty[0] if projekty else {}

            def wspolne(pole: str):  # plik w kilku zleceniach: kuweta / zab tylko, gdy taka sama we wszystkich (recenzja PR #26, D10)
                wartosci = {x.get(pole) for x in projekty}
                return wartosci.pop() if len(wartosci) == 1 else None

            kandydaci.append(Kandydat(sha16=k["sha16"], pokrycie=k.get("pokrycie"), projekt_id=pierwszy.get("projekt_id") if len(projekty) == 1 else None,
                                      zlecenie_id=pierwszy.get("zlecenie_id") if len(projekty) == 1 else None, kuweta=wspolne("kuweta"),
                                      zeby=wspolne("zeby"), typ=wspolne("typ"), zrodlo=wspolne("zrodlo"), zlecen=len(projekty),
                                      miniatura=mini.get(k["sha16"])))
        if klasa in ST.KLASY_RANO_Z_KUWETA and p["kuweta"]:
            podpis = p["kuweta"]
        else:
            podpis = st.napis
        dozwolone: list = []
        if otwarty and s["status"] == SE.STATUS_PRZYJETY:
            if any(k.projekt_id is not None and k.projekt_id != p["projekt_id"] for k in kandydaci):
                dozwolone.append("wybierz_kandydata")
            dozwolone.append("przypisz_recznie")
            if p["decyzja"] is not None:
                dozwolone.append("cofnij_przypisanie")
        inne = tuple((m["numer_plytki"], m["gniazdo"]) for m in konflikty.get(p["projekt_id"], ()) if m["praca_id"] != p["id"]) if p["konflikt"] else ()
        return PracaRano(
            praca_id=p["id"], skan_id=s["id"], gniazdo=p["gniazdo"], klasa=klasa, status=st.klucz, kolor=p["kolor"], rgb=st.hex, podpis=podpis,
            opis=st.opis, numer_plytki=s["numer_plytki"], nr_fragmentu=p["nr_fragmentu"], liczona=bool(p["liczona"]), kuweta=p["kuweta"],
            zeby=p["zeby"], typ=p["typ"], sha16=p["sha16"], projekt_id=p["projekt_id"], zlecenie_id=p["zlecenie_id"], przypisanie=p["przypisanie"],
            decyzja=p["decyzja"], decyzja_id=p.get("decyzja_id"), operator=p["operator"], czas_decyzji=p["czas_decyzji"], kandydaci=tuple(kandydaci),
            miniatura=mini.get(p["sha16"]),
            konflikt=bool(p["konflikt"]), konflikt_z=inne, zlecenie_odhaczone=bool(p["zlecenie_odhaczone"]),
            domyka_dofrezowanie=bool(p["domyka_dofrezowanie"]), kuweta_do_sprawdzenia=bool(p["kuweta_do_sprawdzenia"]), status_match=p["status_match"],
            dozwolone=tuple(dozwolone))

    def _plytka_rano(self, s: dict, st: dict, mini: dict, konflikty: dict, surowe: dict, propozycja: dict | None, czasy: dict) -> Plytka:
        otwarty = st["otwarty"]
        prace = [self._praca_rano(p, s, otwarty, mini, konflikty) for p in s["prace"]]
        w_gniazdach: dict[int, list] = {}
        poza = []
        for p in prace:
            if p.gniazdo is None:
                poza.append(p)
            else:
                w_gniazdach.setdefault(p.gniazdo, []).append(p)
        numery_gniazd, numery_plytek = self._uklad(s["uklad"])
        gniazda = []
        for nr in sorted(set(numery_gniazd) | set(w_gniazdach)):
            lista = w_gniazdach.get(nr, [])
            if not lista:
                pusty = ST.status("pusty")
                gniazda.append(Gniazdo(nr=nr, status="pusty", kolor=None, rgb=pusty.hex, podpis=pusty.napis))
            elif len(lista) > 1 and s["aktywny"]:
                podwojny = ST.status("podwojny")
                gniazda.append(Gniazdo(nr=nr, status="podwojny", kolor=None, rgb=podwojny.hex, podpis=podwojny.napis, prace=tuple(lista)))
            else:
                p = lista[0]
                gniazda.append(Gniazdo(nr=nr, status=p.status, kolor=p.kolor, rgb=p.rgb, podpis=p.podpis, prace=tuple(lista)))
        liczniki: dict[str, int] = {}
        if s["aktywny"]:
            for p in prace:
                if p.klasa is not None:
                    liczniki[p.klasa] = liczniki.get(p.klasa, 0) + 1
        typ = SE.typ_plytki(s["uklad"])
        pominieta = bool(s.get("pominiety"))
        dopuszczona = bool(s["aktywny"] and s["uklad"] and SE.powod_nie_z_trybu(s["uklad"], TRYB_RANO) is not None)
        moze_zastapic = propozycja["poprzedni_id"] if propozycja is not None and not pominieta else None
        dozwolone: list = []
        komunikaty: list = []
        pytania: list = []
        if otwarty and pominieta:
            dozwolone.append("cofnij_pominiecie")
        elif otwarty:
            if s["aktywny"]:
                dozwolone.append("podaj_numer_plytki")
            if moze_zastapic is not None:
                dozwolone += ["potwierdz_ponowny_skan", "odrzuc_ponowny_skan"]
            if s["aktywny"] and s["zastepuje_id"] is not None:
                dozwolone.append("cofnij_zastapienie")
            if dopuszczona:
                dozwolone.append("cofnij_dopuszczenie")
            numery = SR.numery_plytki(s["uklad"])
            blokuje = (not s["aktywny"] or s["status"] == SE.STATUS_DO_POWTORZENIA or numery is None
                       or s["numer_plytki"] in (st.get("zdublowane_plytki") or ()) or (s["numer_plytki"] is not None and s["numer_plytki"] not in numery))
            if s["status"] != SE.STATUS_ZASTAPIONY and blokuje:
                dozwolone.append("pomin_skan")  # A6 runda 2: skan, ktory blokuje "Zamknij piec" (plytki nie z trybu rano sie nie dopuszcza)
            # komunikaty i pytania skanu (jak wieczorem; zamkniety piec jest zamrozony, skan pominiety - bez pytan)
            s_wiecz = {**s, "prace": surowe.get(s["id"], [])}
            proste = [type("P", (), {"gniazdo": w["gniazdo"], "status_inspekcji": w["status_inspekcji"], "blad_inspekcji": False})()
                      for w in surowe.get(s["id"], [])]
            komunikaty = [dataclasses.replace(k, ukryte=True) if k.id in self._ukryte else k for k in self._komunikaty_plytki(s_wiecz, proste)]
            pytania = [dataclasses.replace(q, ukryte=True) if q.id in self._ukryte else q
                       for q in self._pytania_plytki(s, propozycja, czasy, typ, numery_plytek, rano=True)]
        return Plytka(
            skan_id=s["id"], status=s["status"], aktywna=s["aktywny"], napis=ST.NAPIS_POMINIETEJ if pominieta else ST.napis_plytki(s["status"]),
            numer=s["numer_plytki"], numer_zrodlo=s["numer_zrodlo"], uklad=s["uklad"], typ=typ, czas=s["czas_analizy"],
            zmiana=self.sesja.zmiana(s["czas_analizy"]) if s["czas_analizy"] else None, sha16=s["sha16"], gniazda=tuple(gniazda),
            poza_gniazdem=tuple(poza), liczniki=zamroz(liczniki), zielonych=sum(1 for p in prace if p.liczona and s["aktywny"]),
            zastepuje_id=s["zastepuje_id"], moze_zastapic=moze_zastapic, dopuszczona=dopuszczona, dozwolone=tuple(dozwolone),
            komunikaty=tuple(komunikaty), pytania=tuple(pytania), pominieta=pominieta, na_ramce=bool(s.get("na_ramce", True)))

    def _blokady_rano(self, st: dict, zajety: str | None = None) -> tuple:
        """Dlaczego "Zamknij piec" teraz odmowi - napisy dla osoby: najpierw ``zajety`` (analiza albo skanowanie trwa - recenzja
        PR #26, P3 / D1), potem blokady ``session_rano`` (brak numeru plytki, konflikt, dwa skany z jednym numerem - ponowny skan
        albo nowy wsad (A6 runda 4) - wlasnym napisem; pozostale - tekst A6 z numerem skanu zamienionym na plytke i godzine)."""
        if not st["otwarty"]:
            return ()
        wynik = [ST.tekst_komunikatu(zajety)[2]] if zajety else []
        if not st["blokady"]:
            return tuple(wynik)
        skany = {s["id"]: s for s in st["skany"]}

        def skan_po_ludzku(m: re.Match) -> str:
            s = skany.get(int(m[1]))
            if s is None:
                return m[0]
            plytka = ST.PLYTKA_W_BLOKADZIE.format(numer=s["numer_plytki"]) if s["numer_plytki"] is not None else ST.PLYTKA_BEZ_NUMERU_W_BLOKADZIE
            return f"{plytka} ({ST.SKAN_Z_GODZINY.format(godzina=(s['czas_analizy'] or '')[11:16])})"

        if st["bez_numeru"]:
            wynik.append(ST.BLOKADA_BEZ_NUMERU.format(skany=", ".join(ST.SKAN_Z_GODZINY.format(godzina=(skany[i]["czas_analizy"] or "")[11:16])
                                                                       for i in st["bez_numeru"] if i in skany)))
        nowe = set((st.get("nowy_wsad") or {}).get("plytki") or ())
        for n in st.get("zdublowane_plytki") or ():
            wynik.append((ST.BLOKADA_NOWY_WSAD if n in nowe else ST.BLOKADA_DWA_SKANY).format(numer=n))
        if st["konflikty"]:
            wynik.append(ST.BLOKADA_KONFLIKT.format(n=len(st["konflikty"])))
        znane = re.compile(r"(podaj numer plytki|rozstrzygnij konflikty|plytka \d+: dwa skany)")
        for tekst in st["blokady"]:
            if not znane.match(tekst):
                wynik.append(re.sub(r"skan (\d+)", skan_po_ludzku, tekst))
        return tuple(wynik)

    # --- pamiec podreczna poranka (recenzja PR #26, P2) --------------------------------------------
    def _klucz_punktow(self) -> tuple:
        """Wersja stanu punktow zlecen: licznik zdarzen kontrolera, ktore moga go zmienic (polecenia spoza ``NIE_RUSZA_PUNKTOW``,
        skan wieczorny), doba robocza i ``PRAGMA data_version`` (zapis innego polaczenia do bazy - np. indeks, drugi program)."""
        try:
            wersja_bazy = (self.sesja.baza.wiersz("PRAGMA data_version") or {}).get("data_version")
        except (sqlite3.Error, B.BladBazy):
            wersja_bazy = None
        return self._wersja_punktow, self.sesja.doba(), wersja_bazy

    def _uniewaznij_punkty(self) -> None:
        self._wersja_punktow += 1

    def _po_skanie(self, tryb: str | None) -> None:
        """Wynik skanu zapisany: skan wieczorny moze zmienic stan punktow (``session`` - dofrezowania), poranny nie (punkty
        zmienia dopiero "Zamknij piec")."""
        if tryb != TRYB_RANO:
            self._uniewaznij_punkty()

    def _braki_biezace(self) -> tuple:
        """Lista brakow ze wszystkich piecow (``session_rano.braki()`` czyta cala historie zlecen) - liczona od nowa tylko po
        zmianie ``_klucz_punktow``, nie przy kazdym odswiezeniu stanu."""
        klucz = self._klucz_punktow()
        if self._pamiec_brakow is None or self._pamiec_brakow[0] != klucz:
            self._pamiec_brakow = (klucz, tuple(self._zlecenie_rano(z) for z in self.rano.braki()))
        return self._pamiec_brakow[1]

    def _piec_zamkniety(self, sesja_pieca_id: int) -> tuple:
        """(stan_pieca, wynik_pieca) pieca zamknietego z pamieci: piec zamkniety jest zamrozony, a ``wynik_pieca`` A6 czyta wszystkie
        zapisy "Zamknij piec" z dziennika. Klucz: zamkniecie pieca (``zamknieto``) i ``_klucz_punktow``; pamiec - dwa ostatnie piece."""
        w = self.sesja.baza.wiersz("SELECT zamknieto FROM sesje_pieca WHERE id = ?", (sesja_pieca_id,))
        klucz = (w["zamknieto"] if w else None, self._klucz_punktow())
        jest = self._pamiec_zamknietych.get(sesja_pieca_id)
        if jest is None or jest[0] != klucz:
            jest = (klucz, self.rano.stan_pieca(sesja_pieca_id), self.rano.wynik_pieca(sesja_pieca_id))
            self._pamiec_zamknietych = {k: v for k, v in list(self._pamiec_zamknietych.items())[-1:] if k != sesja_pieca_id}
            self._pamiec_zamknietych[sesja_pieca_id] = jest
        return jest[1], jest[2]

    def _z_przeniesienia(self, sesja_pieca_id: int) -> bool:
        """Piec powstal z ``zamknij_piec_i_przenies`` (obowiazujaca decyzja ``przenies_skany`` z ``do_pieca`` = ten piec)."""
        wiersze = self.sesja.baza.wiersze("SELECT id, rodzaj, wartosc FROM decyzje WHERE praca_id IS NULL AND skan_id IS NULL AND rodzaj IN (?, ?) "
                                          "ORDER BY id", (SR.RODZAJ_PRZENIES, SE.RODZAJ_COFNIECIE))
        cofniete = {w["wartosc"] for w in wiersze if w["rodzaj"] == SE.RODZAJ_COFNIECIE}
        for w in wiersze:
            if w["rodzaj"] == SR.RODZAJ_PRZENIES and str(w["id"]) not in cofniete:
                try:
                    if json.loads(w["wartosc"]).get("do_pieca") == sesja_pieca_id:
                        return True
                except (TypeError, ValueError, AttributeError):
                    continue
        return False

    def _ostatni_zamkniety_id(self) -> int | None:
        """Ostatnio zamkniety piec (dowolnej doby) - jego wynik (lista do Excela) zostaje na ekranie z jawnym id (P1)."""
        w = self.sesja.baza.wiersz("SELECT id FROM sesje_pieca WHERE zamknieto IS NOT NULL ORDER BY zamknieto DESC, id DESC LIMIT 1")
        return w["id"] if w else None

    def _zajety(self, zywe: dict | None = None) -> str | None:
        """"analiza_trwa" (skan w analizie, w kolejce albo wynik czeka na zapis), "skanowanie_trwa" (od "start skanu" do pierwszego
        nowego pliku, najwyzej ``LIMIT_SKANOWANIA_S``, albo plik skanera w zapisie) albo None - wtedy "Zamknij piec" mozliwe.
        Wynik, ktory dojdzie po zamknieciu, otworzylby nowy piec (recenzja PR #26, P3; A6 runda 2, D11)."""
        zywe = self._stan_zywy() if zywe is None else zywe
        kolejka, skaner = zywe.get("kolejka"), zywe.get("skaner")
        if kolejka is not None and kolejka.razem > 0:
            return "analiza_trwa"
        if skaner is not None and (skaner.zajete > 0 or (skaner.czeka_na_skan and self._swiezy_start(skaner.ostatni_start_skanu))):
            return "skanowanie_trwa"
        return None

    def _swiezy_start(self, czas: str | None) -> bool:
        if not czas:
            return False
        try:
            return (self._zegar() - dt.datetime.fromisoformat(czas)).total_seconds() <= LIMIT_SKANOWANIA_S
        except (TypeError, ValueError):
            return False

    def _sprawdz_zajetosc(self) -> bool:
        """Blokada "Zamknij piec" w stanie nieaktualna (koniec analizy, start albo limit skanowania): stan od nowa. True = odswiezono."""
        if self._stan is None or self._stan.rano is None or self._zamkniety:
            return False
        if self._zajety() != self._stan.rano.zajety:
            self._odswiez()
            return True
        return False

    # --- stan ekranu porannego --------------------------------------------------------------------
    def _stan_rano(self) -> StanRano:
        """Stan ekranu porannego z ``session_rano``: piec biezacy otwarty, a bez niego ostatnio zamkniety piec - z jawnym id,
        takze z poprzedniej doby (recenzja PR #26, P1); przy otwartym piecu ``ostatni_zamkniety`` (lista do Excela nadal dostepna)."""
        piece = self.rano.piece()
        braki_biezace = self._braki_biezace()
        piece_t = zamroz([{k: p.get(k) for k in ("id", "nr_w_dniu", "plan_id", "otwarty", "skanow", "otwarto", "zamknieto")} for p in piece])
        biezacy = self.rano.otwarty_piec()
        ostatni_id = self._ostatni_zamkniety_id()
        zajety = self._zajety()
        if biezacy is not None:
            st, wynik = self.rano.stan_pieca(biezacy["id"]), None
        elif ostatni_id is not None:
            st, wynik = self._piec_zamkniety(ostatni_id)
        else:
            return StanRano(kolejnosc=self._kolejnosc, braki_biezace=braki_biezace, piece=piece_t, ramka=self._ramka_poranna_dostepna(),
                            excel=self._excel_dostepny(), zajety=zajety)
        ostatni = None
        if biezacy is not None and ostatni_id is not None:
            st_z, wynik_z = self._piec_zamkniety(ostatni_id)
            ostatni = self._stan_rano_pieca(st_z, wynik_z, plytki=False)
        return self._stan_rano_pieca(st, wynik, braki_biezace=braki_biezace, piece=piece_t, ostatni=ostatni, zajety=zajety)

    def _stan_rano_pieca(self, st: dict, wynik: dict | None, *, plytki: bool = True, braki_biezace: tuple = (), piece: tuple = (),
                         ostatni: StanRano | None = None, zajety: str | None = None) -> StanRano:
        """``StanRano`` jednego pieca ze ``stan_pieca`` A6; ``plytki`` False = bez plytek i kuwet (ostatni zamkniety piec obok
        otwartego - tylko wynik)."""
        zlecenie = self._zlecenie_rano
        poprawki = tuple(PoprawkaRano(praca_id=x["praca_id"], skan_id=x["skan_id"], numer_plytki=x["numer_plytki"], gniazdo=x["gniazdo"],
                                      kuweta=x.get("kuweta"), zeby=x.get("zeby"), zlecenie_odhaczone=bool(x.get("zlecenie_odhaczone")))
                         for x in st["poprawki"])
        wspolne = dict(
            sesja_pieca_id=st["sesja_pieca_id"], plan_id=st["plan_id"], data=st["data"], nr_w_dniu=st["nr_w_dniu"], otwarto=st["otwarto"],
            zamknieto=st["zamknieto"], zamknal=st["zamknal"], otwarty=st["otwarty"], z_poprzedniej_doby=st["otwarty_z_poprzedniej_doby"],
            liczniki=zamroz(st["liczniki"]), nierozstrzygniete=zamroz(st["nierozstrzygniete"]),
            kompletne=tuple(zlecenie(z) for z in st["kompletne"]), braki=tuple(zlecenie(z) for z in st["braki"]), poprawki=poprawki,
            kolejnosc=self._kolejnosc, wynik=zamroz(wynik) if wynik is not None else None, ramka=self._ramka_poranna_dostepna(),
            excel=self._excel_dostepny())
        if not plytki:
            return StanRano(**wspolne)
        surowe: dict = {}
        skany_ids = [s["id"] for s in st["skany"]]
        if skany_ids and st["otwarty"]:
            for w in self.sesja.baza.wiersze(f"SELECT skan_id, gniazdo, status_fragmentu, status_inspekcji FROM prace WHERE skan_id IN "
                                             f"({', '.join('?' * len(skany_ids))}) ORDER BY id", tuple(skany_ids)):
                surowe.setdefault(w["skan_id"], []).append(w)
        shas = [p["sha16"] for s in st["skany"] for p in s["prace"]] + [k["sha16"] for s in st["skany"] for p in s["prace"] for k in p["kandydaci"]]
        mini = self._miniatury(shas)
        konflikty = {k["projekt_id"]: k["miejsca"] for k in st["konflikty"]}
        propozycje = {p["skan_id"]: dict(p) for p in st["do_potwierdzenia"] if (p["skan_id"], p["poprzedni_id"]) not in self._odrzucone}
        decyzji = {s["id"]: sum(1 for p in s["prace"] if p["decyzja"] is not None) for s in st["skany"]}
        for p in propozycje.values():
            p.update(liczba_decyzji=decyzji.get(p["poprzedni_id"], 0), liczba_ukruszonych=0)
        czasy = {s["id"]: s["czas_analizy"] for s in st["skany"]}
        plytki_t = tuple(self._plytka_rano(s, st, mini, konflikty, surowe, propozycje.get(s["id"]), czasy) for s in st["skany"])
        kuwety, biezaca, do_cofniecia = self._kuwety_pieca(st)
        rozlozone = set(self._rozlozone(st["plan_id"])) if st["otwarty"] else set()
        z_brakami = {z["kuweta"] for z in st["braki"]}
        nowy = st.get("nowy_wsad") if st["otwarty"] else None
        nowy_wsad = NowyWsad(plytki=tuple(nowy.get("plytki") or ()), skany=tuple(nowy.get("skany") or ())) if nowy else None
        dozwolone: list = []
        if st["otwarty"] and zajety is None:
            if not st["blokady"]:
                dozwolone.append("zamknij_piec")
            if nowy_wsad is not None and nowy_wsad.skany:
                dozwolone.append("zamknij_piec_i_przenies")
        if st["otwarty"] and self._z_przeniesienia(st["sesja_pieca_id"]):  # A6 runda 5: pomylke "zamknij i przenies" cofa osoba
            dozwolone.append("cofnij_przeniesienie")
        elif not st["otwarty"] and not self.rano.otwarte_piece():  # A6 runda 2: pomylke cofa ponowne otwarcie (tylko ostatni piec)
            ostatni_id = self.sesja.baza.wiersz("SELECT max(id) AS id FROM sesje_pieca")["id"]
            if ostatni_id == st["sesja_pieca_id"]:
                dozwolone.append("otworz_piec_ponownie")
        ostrzezenia = tuple(re.sub(r"skan (\d+)", lambda m: ST.SKAN_Z_GODZINY.format(godzina=(czasy.get(int(m[1])) or "")[11:16]), t)
                            for t in st.get("ostrzezenia") or ())
        return StanRano(
            **wspolne, plytki=plytki_t, konflikty=zamroz(st["konflikty"]), blokady=self._blokady_rano(st, zajety), dozwolone=tuple(dozwolone),
            ostrzezenia=ostrzezenia, inne_otwarte_piece=tuple(st.get("inne_otwarte_piece") or ()),
            kuwety=tuple(KuwetaRano(kuweta=k, prac=n, plytki=pl, potwierdzona=k in rozlozone, biezaca=k == biezaca, braki=k in z_brakami, gniazda=g)
                         for k, n, pl, g in kuwety),
            kuweta_biezaca=biezaca, kuweta_do_cofniecia=do_cofniecia, braki_biezace=braki_biezace, piece=piece,
            zajety=zajety, nowy_wsad=nowy_wsad, ostatni_zamkniety=ostatni)

    def _ramka_poranna_dostepna(self) -> bool:
        """Czy ramka poranna jest podlaczona i odpowiada (E3-A12: ostatni odczyt stanu klienta ``indicate``)."""
        r = self._stan_ramek.poranna if self._stan_ramek is not None else None
        return r is not None and r.polaczona and r.blad is None

    def _excel_dostepny(self) -> bool:
        """Czy program ma Excel (E3-A12: ``podlacz_excel``); czy Excel odpowiada, wiadomo dopiero przy odczycie arkusza."""
        return self.excel is not None

    # --- ramki swietlne (E3-A12) ------------------------------------------------------------------
    def podlacz_ramki(self, ramki: Any) -> None:
        """Ramki stanowiska: ``indicate.Indicate`` (``wieczorna`` / ``poranna`` - klienci ``KlientRamki`` albo None) albo None.
        Plan pieca idzie do klienta PRZED pierwszym kontaktem z ramka (potwierdzenia z bazy, gdy ramka planu juz nie ma), potem
        klienci startuja (``uruchom``). Brak ramki = komunikat (po ``CZAS_NA_POLACZENIE_RAMEK_S``) i praca dalej (kryterium 5)."""
        if self._zamkniety:
            return
        self.ramki = ramki
        self._ramki_od = time.monotonic()
        self._ramki_po_czasie = False
        self._stan_ramek = self._odczytaj_ramki()
        self._plan_p = self._plan_p_podpis = self._plan_p_dane = None
        self._plany_wyslane = set()
        if self._stan is not None:
            self._odswiez()
        if ramki is not None:
            try:
                ramki.uruchom()
            except Exception:  # noqa: BLE001 - ramka to dodatek: program dziala dalej wedlug ekranu
                LOG.exception("kontroler: klienci ramek nie wystartowali")

    def podlacz_excel(self, excel: Any) -> None:
        """Excel: ``excel.Excel`` z ``baza`` TEGO programu (X4 sprawdzane w ``sesje_pieca`` - recenzja PR #27 D7, PR #30 D8) albo
        None. Polaczenie z arkuszem leniwe. Przy podlaczeniu: piece zamkniete w ostatnich ``ZALEGLE_EXCELA_H`` godzinach ze
        zleceniami kompletnymi bez wpisu w logu Excela - komunikat i przycisk w oknie Excela (P5)."""
        if self._zamkniety:
            return
        if excel is not None and getattr(excel, "baza", None) is not self.sesja.baza:
            LOG.error("kontroler: Excel bez bazy programu - niepodlaczony (zapis do Excela wymaga kontroli X4 w bazie)")
            excel = None
        self.excel = excel
        self._excel_pozycje, self._excel_piec, self._excel_blad, self._excel_widoczne = [], None, None, False
        self._excel_kolejka.clear()
        self._excel_zalegle = {}
        if excel is not None:
            try:
                self._excel_przelicz_zalegle()
            except Exception:  # noqa: BLE001
                LOG.exception("kontroler: zaleglych piecow Excela nie da sie policzyc")
        if self._stan is not None:
            self._odswiez()

    def _klient(self, rola: str):
        if self.ramki is None:
            return None
        return getattr(self.ramki, "wieczorna" if rola == "W" else "poranna", None)

    def _klienci(self) -> list:
        return [k for k in (self._klient("W"), self._klient("P")) if k is not None]

    def _odczytaj_ramki(self) -> StanRamek | None:
        if self.ramki is None:
            return None

        def jedna(k):
            if k is None:
                return None
            try:
                s = k.stan()
            except Exception:  # noqa: BLE001
                LOG.exception("kontroler: stanu ramki nie da sie odczytac")
                return StanRamki(rola=getattr(k, "rola", "?"))
            plytka = s.get("plytka")
            return StanRamki(rola=s.get("rola") or getattr(k, "rola", "?"), polaczona=bool(s.get("polaczona")), blad=s.get("blad"),
                             komunikat=s.get("komunikat"), plytka=plytka if _jest_liczba(plytka) else None, tryb_ramki=s.get("tryb_ramki"),
                             plan_przyjety=bool(s.get("plan_przyjety")), wstrzymane=bool(s.get("wstrzymane")),
                             potwierdzone=len(s.get("potwierdzone") or ()), ostrzezenia=tuple(s.get("ostrzezenia") or ()),
                             utracone=int(s.get("utracone") or 0), przepelnienie=int(s.get("przepelnienie") or 0))

        return StanRamek(wieczorna=jedna(self._klient("W")), poranna=jedna(self._klient("P")), test_led=time.monotonic() < self._test_led_do)

    def _ramki_po_czasie_na_polaczenie(self) -> bool:
        """Recenzja PR #30 D7: komunikaty "ramka nie odpowiada" dopiero po ``CZAS_NA_POLACZENIE_RAMEK_S`` od podlaczenia (bez migania
        przed pierwszym kontaktem)."""
        return self.ramki is None or self._ramki_po_czasie or time.monotonic() - self._ramki_od >= CZAS_NA_POLACZENIE_RAMEK_S

    @staticmethod
    def _dostepnosc_ramek(s: StanRamek | None) -> tuple:
        """Czesc stanu ramek, od ktorej zaleza komunikaty i ``StanRano.ramka`` (zmiana = pelne odswiezenie stanu)."""
        if s is None:
            return ()
        return tuple((r.rola, r.polaczona, r.blad, r.komunikat) for r in (s.wieczorna, s.poranna) if r is not None)

    def _komunikaty_ramek(self) -> None:
        """Bledy ramek inne niz brak polaczenia (zly klucz, drugi laptop, awaria sprzetu, plan odrzucony) - komunikat z tekstem
        ``statusy.BLEDY_RAMEK`` (D4)."""
        for r in (self._stan_ramek.wieczorna, self._stan_ramek.poranna) if self._stan_ramek is not None else ():
            if r is None:
                continue
            pokaz = r.blad not in (None, "brak_polaczenia")
            nazwa = ST.NAZWY_TRYBOW.get(TRYB_WIECZOR if r.rola == "W" else TRYB_RANO, r.rola)
            self._ustaw_komunikat("ramka_blad", f"ramka_blad:{r.rola}", pokaz, ramka=nazwa,
                                  powod=ST.BLEDY_RAMEK.get(r.blad or "", r.komunikat or r.blad or ""))

    def _przetworz_ramki(self) -> int:
        """Zegar okna (``przetworz``): krok Excela (najwyzej jeden odczyt arkusza na obieg - recenzja PR #30 P1), zdarzenia ramek ->
        dziennik i sesja (klucz unikalny; zdarzenia, ktorych nie dalo sie zapisac przy zajetej bazie, czekaja na ponowienie - D2),
        stan klientow co ``OKRES_STANU_RAMEK_S``, ponowienie planu pieca po bledzie (P2), koniec testu diod. Zwraca liczbe
        obsluzonych zdarzen; stan odswieza sama (pelny albo czesc "zywa")."""
        n = self._przetworz_excel()
        if self.ramki is None or self._zamkniety:
            return n
        pelne, zywe = self._odswiez_potrzebne, False
        self._odswiez_potrzebne = False
        odebrane = []
        for k in self._klienci():
            try:
                odebrane += k.odbierz_zdarzenia()
            except Exception:  # noqa: BLE001
                LOG.exception("kontroler: zdarzen ramki nie da sie odebrac")
        teraz = time.monotonic()
        if self._zdarzenia_ponow and teraz < self._zdarzenia_ponow_od:  # r3 D-N1: odlozone czekaja (kolejnosc: nowe za nimi)
            self._zdarzenia_ponow += odebrane
        elif self._zdarzenia_ponow or odebrane:
            do_zapisu, self._zdarzenia_ponow = self._zdarzenia_ponow + odebrane, []
            n += len(do_zapisu)
            with self._krotkie_czekanie_na_baze():
                wynik, self._zdarzenia_ponow = self._zdarzenia_ramki(do_zapisu)
            if self._zdarzenia_ponow:
                self._zdarzenia_ponow_od = teraz + OKRES_PONOWIENIA_ZDARZEN_S
            pelne = wynik or pelne
        if teraz >= self._ramki_kontrola:
            self._ramki_kontrola = teraz + OKRES_STANU_RAMEK_S
            if self._test_led_do and teraz >= self._test_led_do:  # koniec testu diod: plan pieca ponownie
                self._test_led_do = 0.0
                self._plan_p_podpis = None
                self._usun_komunikat(ID_TEST_LED)
                pelne = True
            if not self._ramki_po_czasie and teraz - self._ramki_od >= CZAS_NA_POLACZENIE_RAMEK_S:
                self._ramki_po_czasie = True
                pelne = True
            if self._plan_p_ponow and teraz >= self._plan_p_ponow_od and self._stan is not None:  # P2: ponowienie planu po bledzie
                self._plan_p_ponow_od = teraz + OKRES_PONOWIENIA_PLANU_S
                self._plan_p_podpis = None
                self._synchronizuj_ramke_p(self._stan)
                pelne = pelne or self._odswiez_potrzebne
                self._odswiez_potrzebne = False
            nowy = self._odczytaj_ramki()
            if nowy != self._stan_ramek:
                stary, self._stan_ramek = self._stan_ramek, nowy
                if self._dostepnosc_ramek(stary) != self._dostepnosc_ramek(nowy):
                    self._komunikaty_ramek()
                    pelne = True
                else:
                    zywe = True
        if pelne:
            self._odswiez()
        elif zywe:
            self._odswiez_zywe()
        return n

    # --- dziennik zdarzen ramek z kluczem unikalnym (wymaganie indicate.md, pkt 4 API) -------------
    def _krotkie_czekanie_na_baze(self):
        """r3 D-N1: zapis zdarzen ramki czeka na baze zajeta przez inny program najwyzej ``CZEKAJ_ZDARZENIA_MS`` (zamiast
        ``busy_timeout`` 5 s - okno nie stoi), potem zdarzenia czekaja na ponowienie co ``OKRES_PONOWIENIA_ZDARZEN_S``."""
        import contextlib  # noqa: PLC0415

        baza = self.sesja.baza

        @contextlib.contextmanager
        def czekanie():
            ustawione = False
            try:
                baza.polaczenie.execute(f"PRAGMA busy_timeout = {int(CZEKAJ_ZDARZENIA_MS)}")
                ustawione = True
            except Exception:  # noqa: BLE001 - bez krotkiego czekania zapis i tak sie uda (dluzej)
                pass
            try:
                yield
            finally:
                if ustawione:
                    try:
                        baza.polaczenie.execute(f"PRAGMA busy_timeout = {int(getattr(baza, 'czekaj_ms', B.CZEKAJ_NA_BLOKADE_MS))}")
                    except Exception:  # noqa: BLE001
                        LOG.exception("kontroler: nie da sie przywrocic czasu czekania na baze")

        return czekanie()

    def _zdarzenia_ramki(self, zdarzenia: list) -> tuple:
        """Zdarzenia jednego odbioru, w kolejnosci: kolejne zdarzenia bez skutku w sesji zapisywane w JEDNEJ transakcji (jeden zapis
        na dysk), "Zamknij piec" - osobno. Blad serii = wycofanie i zapis po jednym. Baza zajeta = to zdarzenie i nastepne czekaja
        na ponowienie w nastepnym obiegu (recenzja PR #30 D2 - nie gina do restartu). Zwraca (odswiezyc caly stan, do ponowienia)."""
        pelne, seria = False, []

        def zapisz_po_jednym(lista: list) -> list:
            nonlocal pelne
            for i, z in enumerate(lista):
                try:
                    pelne = self._zdarzenie_ramki(z) or pelne
                except B.BladBazy:
                    LOG.warning("kontroler: baza zajeta - %d zdarzen ramki czeka na ponowienie", len(lista) - i)
                    return lista[i:]
                except Exception:  # noqa: BLE001 - blad jednego zdarzenia nie zatrzymuje programu
                    LOG.exception("kontroler: blad obslugi zdarzenia ramki")
                    pelne = True
            return []

        def zapisz_serie() -> list:
            nonlocal pelne
            if len(seria) <= 1:
                return zapisz_po_jednym(seria)
            try:
                for zrodlo in {ZRODLA_RAMEK.get(z.get("rola")) for z in seria} - {None}:
                    self._klucze_zrodla(zrodlo)  # pamiec kluczy z dziennika wczytana przed seria
            except B.BladBazy:
                return list(seria)
            znane = {(ZRODLA_RAMEK.get(z.get("rola")), f"{z.get('start_id')}:{z.get('nr')}") for z in seria
                     if f"{z.get('start_id')}:{z.get('nr')}" in self._klucze_ramek.get(ZRODLA_RAMEK.get(z.get("rola")), ())}
            od = dict(self._klucze_od)
            try:
                with self.sesja.baza.transakcja():
                    wynik = False
                    for z in seria:
                        wynik = self._zdarzenie_ramki(z) or wynik
                pelne = wynik or pelne
                return []
            except Exception as e:  # noqa: BLE001 - seria wycofana: klucze tej serii z pamieci precz
                for z in seria:
                    zrodlo, klucz = ZRODLA_RAMEK.get(z.get("rola")), f"{z.get('start_id')}:{z.get('nr')}"
                    if zrodlo in self._klucze_ramek and (zrodlo, klucz) not in znane:
                        self._klucze_ramek[zrodlo].discard(klucz)
                self._klucze_od.update(od)
                self._kuwety_rozlozone.clear()  # rozlozenie kuwet z ramki - od nowa z dziennika
                if isinstance(e, B.BladBazy):
                    return list(seria)
                LOG.exception("kontroler: serii zdarzen ramki nie da sie zapisac - zapis po jednym")
                return zapisz_po_jednym(seria)

        for i, z in enumerate(zdarzenia):
            if z.get("rola") == "P" and z.get("typ") == "zamknij_piec":
                reszta = zapisz_serie()
                seria = []
                if reszta:
                    return pelne, reszta + list(zdarzenia[i:])
                reszta = zapisz_po_jednym([z])
                if reszta:
                    return pelne, reszta + list(zdarzenia[i + 1:])
            else:
                seria.append(z)
        reszta = zapisz_serie()  # najpierw zapis (ustawia pelne), potem wynik
        return pelne, reszta

    def _klucze_zrodla(self, zrodlo: str) -> set:
        """Klucze (start_id:nr) zdarzen ramki ``zrodlo`` z dziennika: ostatnie ``ZDARZEN_RAMKI_W_PAMIECI`` wpisow (ramka powtarza
        najwyzej 2000 ostatnich zdarzen), czytane raz; ``_klucze_od`` - najwyzszy id dziennika sprawdzony (D1: przesuwany po kazdym
        wlasnym wpisie - drugi program na tej bazie blokuje ``BlokadaStanowiska``)."""
        if zrodlo not in self._klucze_ramek:
            klucze = set()
            for w in self.sesja.baza.wiersze("SELECT dane FROM zdarzenia WHERE zrodlo = ? ORDER BY id DESC LIMIT ?", (zrodlo, ZDARZEN_RAMKI_W_PAMIECI)):
                try:
                    klucze.add(json.loads(w["dane"])["klucz"])
                except (TypeError, ValueError, KeyError):
                    continue
            self._klucze_od[zrodlo] = (self.sesja.baza.wiersz("SELECT max(id) AS m FROM zdarzenia") or {}).get("m") or 0
            self._klucze_ramek[zrodlo] = klucze
        return self._klucze_ramek[zrodlo]

    def _klucz_zapisany(self, zrodlo: str, klucz: str) -> bool:
        """Czy zdarzenie o tym kluczu jest juz w dzienniku - pamiec + wpisy dopisane po ostatnim sprawdzeniu (w transakcji zapisu)."""
        if klucz in self._klucze_zrodla(zrodlo):
            return True
        wzor = "%" + json.dumps({"klucz": klucz})[1:-1].replace("!", "!!").replace("%", "!%").replace("_", "!_") + "%"
        return self.sesja.baza.wiersz("SELECT 1 AS j FROM zdarzenia WHERE id > ? AND zrodlo = ? AND dane LIKE ? ESCAPE '!' LIMIT 1",
                                      (self._klucze_od[zrodlo], zrodlo, wzor)) is not None

    def _wpisz_zdarzenie_ramki(self, zrodlo: str, typ: str, dane: dict) -> int:
        id_ = self.sesja.baza.zdarzenie(zrodlo, typ, dane, czas=self._teraz())
        self._klucze_od[zrodlo] = max(self._klucze_od.get(zrodlo, 0), id_)  # D1: pamiec ma klucze tego uruchomienia
        return id_

    def _kuweta_z_ramki(self, z: dict, plan_id: str) -> tuple:
        """Decyzja wlasciciela (runda 2): Enter / Backspace na ramce porannej = takze kuweta rozlozona / cofnieta na ekranie.
        Kuweta jest rozlozona, gdy ramka ma ja potwierdzona na WSZYSTKICH plytkach, na ktorych lezy wedlug EKRANU (lista kuwet
        ``KuwetaRano.plytki``, lustro potwierdzen klienta ``potwierdzone()``); kuweta z praca na plytce poza planem ramki (okragla)
        - bez automatu, rozlozenie potwierdza osoba na ekranie (r3 P-N1). Cofniecie na ramce kuwety rozlozonej - znow do
        rozlozenia (biezaca kuweta laptopa bez zmian - r3 D-N3). Zwraca ("kuweta_rozlozona" / "kuweta_cofnieta", kuweta) albo
        (None, None)."""
        kuweta, k = z.get("kuweta"), self._klient("P")
        if not isinstance(kuweta, str) or k is None or plan_id != self._plan_p or self._plan_p_dane is None:
            return None, None
        stos = self._rozlozone(plan_id)
        if z.get("typ") == "cofniecie":
            return ("kuweta_cofnieta", kuweta) if kuweta in stos else (None, None)
        w_planie = next((set(x.get("plytki") or ()) for x in self._plan_p_dane.get("kuwety") or () if x.get("kuweta") == kuweta), None)
        rano = self._stan.rano if self._stan is not None else None
        na_ekranie = next((set(x.plytki) for x in (rano.kuwety if rano is not None else ()) if x.kuweta == kuweta), None)
        plytki = na_ekranie  # r4 P-R3-1: kuwety nie ma na liscie ekranu (tryb "wieczor", skan liczony inaczej) - bez automatu
        if not plytki or kuweta in stos or not plytki <= (w_planie or set()):
            return None, None  # r3 P-N1: praca kuwety na plytce poza ramka (okragla) - rozlozenie potwierdza osoba na ekranie
        try:
            potwierdzone = {(int(p), kw) for p, kw in k.potwierdzone()}
        except Exception:  # noqa: BLE001
            return None, None
        return ("kuweta_rozlozona", kuweta) if all((p, kuweta) in potwierdzone for p in plytki) else (None, None)

    def _zdarzenie_ramki(self, z: dict) -> bool:
        """Jedno zdarzenie ramki (watek okna): wpis w ``zdarzenia`` z kluczem ``klucz_zdarzenia`` (start_id, nr) - KAZDE zdarzenie,
        takze pominiete i odrzucone - w tej samej transakcji co skutek; klucz juz zapisany = nic (historia po restarcie programu).
        Potwierdzenia / cofniecia / wybory kuwet: dziennik ("inny_piec", gdy ``plan_id`` nie jest otwartym piecem) i rozlozenie
        kuwety na ekranie (``_kuweta_z_ramki``). "Zamknij piec": ``_zamknij_piec_z_ramki``. Zwraca True, gdy trzeba odswiezyc caly
        stan. Baza zajeta = ``BladBazy`` (wolajacy ponawia)."""
        rola = z.get("rola")
        zrodlo = ZRODLA_RAMEK.get(rola)
        if zrodlo is None or not isinstance(z.get("start_id"), str) or not _jest_liczba(z.get("nr")):
            LOG.warning("kontroler: zdarzenie ramki bez klucza (rola, start_id, nr) - pominiete")
            return False
        klucz = f"{z['start_id']}:{z['nr']}"
        typ = str(z.get("typ") or "nieznane")[:40]
        dane = {"klucz": klucz, "start_id": z["start_id"], "nr": z["nr"], "z_historii": bool(z.get("z_historii")),
                "nieaktualne": bool(z.get("nieaktualne"))}
        for pole in ("plan_id", "plytka", "poprzednia", "kuweta", "wersja", "przyczyna", "stan"):
            if isinstance(z.get(pole), (str, int)) and not isinstance(z.get(pole), bool):
                dane[pole] = z[pole] if not isinstance(z[pole], str) else z[pole][:40]
        if rola == "P" and typ == "zamknij_piec":
            return self._zamknij_piec_z_ramki(z, zrodlo, klucz, dane)
        if rola == "P" and typ == "plan_przyjety" and _jest_liczba(z.get("wersja")):  # P7: plan nowej wersji przyjety po zamknieciu
            czeka = self._plany_czekaja.get(z.get("plan_id"))
            if czeka is not None and z["wersja"] > czeka:
                del self._plany_czekaja[z["plan_id"]]
        skutek, kuweta, plan_id = "zapisano", (None, None), None
        if rola == "P" and typ in ZDARZENIA_KUWET_RAMKI:
            otwarty = self.rano.otwarty_piec()
            if otwarty is None or z.get("plan_id") != otwarty["plan_id"]:
                skutek = "inny_piec"
            elif typ in ("potwierdzenie", "cofniecie"):
                plan_id = otwarty["plan_id"]
                kuweta = self._kuweta_z_ramki(z, plan_id)
        baza = self.sesja.baza
        with baza.transakcja():
            if self._klucz_zapisany(zrodlo, klucz):
                return False
            self._wpisz_zdarzenie_ramki(zrodlo, typ, {**dane, "skutek": skutek, **({kuweta[0]: kuweta[1]} if kuweta[0] else {})})
        self._klucze_zrodla(zrodlo).add(klucz)
        if kuweta[0] == "kuweta_rozlozona":
            self._rozlozone(plan_id).append(kuweta[1])
            if self._kuweta_biezaca.get(plan_id) == kuweta[1]:
                self._kuweta_biezaca.pop(plan_id, None)  # biezaca = nastepna nierozlozona (jak Enter na ekranie)
            return True
        if kuweta[0] == "kuweta_cofnieta":
            stos = self._rozlozone(plan_id)
            del stos[len(stos) - 1 - stos[::-1].index(kuweta[1])]  # r3 D-N3: biezaca kuweta laptopa zostaje (wybor osoby przy laptopie)
            return True
        return False

    def _zamknij_piec_z_ramki(self, z: dict, zrodlo: str, klucz: str, dane: dict) -> bool:
        """"Zamknij piec" z klawiatury ramki porannej: TYLKO gdy zdarzenie nie jest z historii / innego pieca (``nieaktualne``), nie
        przyszlo sprzed przyjecia planu nowej wersji po zamknieciu / ponownym otwarciu tego pieca (P7), ``plan_id`` = otwarty piec
        biezacy, nie trwa analiza ani skanowanie (jak przycisk) i jest wybrana osoba; skutek (``session_rano.zamknij_piec``) i klucz
        w jednej transakcji. Odmowa sesji = wpis "odmowa" z powodem. Baza zajeta = ``BladBazy`` (ponowienie w nastepnym obiegu),
        inny blad = wpis "blad" i komunikat (D2). Po zapisie z pominieciem polecenia okna pamiec listy brakow jest uniewazniana
        (recenzja PR #26, D1) - takze po bledzie."""
        baza = self.sesja.baza
        skutek, powod, wynik = "nieaktualne", "", None
        try:
            otwarty = self.rano.otwarty_piec()
            with baza.transakcja():
                if self._klucz_zapisany(zrodlo, klucz):
                    return False
                if z.get("nieaktualne") or z.get("z_historii") or z.get("plan_id") in self._plany_czekaja:
                    skutek = "nieaktualne"
                elif otwarty is None or z.get("plan_id") != otwarty["plan_id"]:
                    skutek = "inny_piec"
                elif self._zajety() is not None:
                    skutek = self._zajety()
                else:
                    try:
                        wynik = self.rano.zamknij_piec(plan_id=z["plan_id"])
                        skutek = "zamknieto"
                    except SE.BladSesji as e:
                        skutek, powod = "odmowa", B.bez_sciezek(str(e))[:300]
                self._wpisz_zdarzenie_ramki(zrodlo, "zamknij_piec", {**dane, "skutek": skutek, **({"powod": powod} if powod else {})})
        except B.BladBazy:
            self._uniewaznij_punkty()
            raise
        except Exception:  # noqa: BLE001 - nic nie zapisano (transakcja wycofana): sam klucz z "blad", piec bez zmian, komunikat
            LOG.exception("kontroler: 'Zamknij piec' z ramki nie powiodl sie")
            self._uniewaznij_punkty()
            try:
                with baza.transakcja():
                    if not self._klucz_zapisany(zrodlo, klucz):
                        self._wpisz_zdarzenie_ramki(zrodlo, "zamknij_piec", {**dane, "skutek": "blad"})
                self._klucze_zrodla(zrodlo).add(klucz)
            except Exception:  # noqa: BLE001
                LOG.exception("kontroler: wpisu zdarzenia ramki nie da sie zapisac")
            self._komunikat("ramka_zamknij_odmowa", id_="ramka_zamknij_odmowa", powod=ST.NAPIS_BLAD_PROGRAMU_RAMKI)
            return True
        self._klucze_zrodla(zrodlo).add(klucz)
        self._uniewaznij_punkty()
        if skutek == "zamknieto":
            self._komunikat("ramka_piec_zamkniety", id_="ramka_piec_zamkniety", nr=(wynik or {}).get("nr_w_dniu") or "?")
            self._po_zamknieciu_pieca(wynik or {})
        elif skutek == "nieaktualne":
            self._komunikat("ramka_zamknij_nieaktualne", id_="ramka_zamknij_nieaktualne")
        else:
            tekst = powod if skutek == "odmowa" else (tekst_komunikatu(skutek)[2] if skutek in ("analiza_trwa", "skanowanie_trwa")
                                                      else tekst_komunikatu("ramka_zamknij_nieaktualne")[2])
            self._komunikat("ramka_zamknij_odmowa", id_="ramka_zamknij_odmowa", powod=tekst)
        return True

    def _potwierdzone_z_bazy(self, plan_id: str) -> list:
        """Potwierdzenia kuwet planu ``plan_id`` z dziennika zdarzen ramki porannej (lustro stanu ramki: potwierdzenie dopisuje,
        cofniecie usuwa ostatnie) - do pierwszego planu po starcie programu (ramka zgaszona przy zamknieciu nie ma juz planu)."""
        stos: dict = {}
        wiersze = self.sesja.baza.wiersze("SELECT typ, dane FROM zdarzenia WHERE zrodlo = ? ORDER BY id DESC LIMIT ?",
                                          (ZRODLA_RAMEK["P"], ZDARZEN_RAMKI_W_PAMIECI))
        for w in reversed(wiersze):
            if w["typ"] not in ("potwierdzenie", "cofniecie"):
                continue
            try:
                d = json.loads(w["dane"])
            except (TypeError, ValueError):
                continue
            if d.get("plan_id") != plan_id or d.get("skutek") != "zapisano" or not _jest_liczba(d.get("plytka")) or not isinstance(d.get("kuweta"), str):
                continue
            lista = stos.setdefault(d["plytka"], [])
            if w["typ"] == "potwierdzenie" and d["kuweta"] not in lista:
                lista.append(d["kuweta"])
            elif w["typ"] == "cofniecie" and d["kuweta"] in lista:
                del lista[len(lista) - 1 - lista[::-1].index(d["kuweta"])]
        return [[p, k] for p in sorted(stos) for k in stos[p]]

    def _zgas_ramke_p(self) -> None:
        """Ramka poranna gasnie od razu (zamkniecie pieca - takze w trybie "wieczor": recenzja PR #30 P3)."""
        k = self._klient("P")
        if k is not None and self._plan_p is not None:
            try:
                k.zgas()
            except Exception:  # noqa: BLE001
                LOG.exception("kontroler: zgaszenie ramki porannej")
        self._plan_p = self._plan_p_podpis = self._plan_p_dane = None

    def _synchronizuj_ramke_p(self, stan: StanAplikacji) -> None:
        """Plan ramki porannej = ``SesjaRano.plan_plytek(kolejnosc z ekranu)`` po kazdej zmianie pieca (plytki, prace, braki,
        kolejnosc) - liczony tylko, gdy zmienil sie stan pieca na ekranie; brak otwartego pieca = ``zgas`` (w trybie "wieczor" tez -
        P3). Blad liczenia planu (kazdy - P2) = ramka zgaszona, komunikat, ponowienie co ``OKRES_STANU_RAMEK_S``. Pierwszy plan
        danego pieca w tym uruchomieniu niesie potwierdzenia z bazy (gdy sa)."""
        k = self._klient("P")
        if k is None or time.monotonic() < self._test_led_do:
            return
        if stan.tryb != TRYB_RANO:  # wieczorem plan bez zmian (D10), ale zamkniety piec nie swieci (P3)
            if self._plan_p is not None and self.rano.otwarty_piec() is None:
                self._zgas_ramke_p()
            return
        r = stan.rano
        if r is None or not r.otwarty or r.sesja_pieca_id is None:
            if self._plan_p is not None:
                self._zgas_ramke_p()
            return
        podpis = (r.sesja_pieca_id, r.plan_id, self._kolejnosc, r.plytki, r.braki)
        if podpis == self._plan_p_podpis:
            return
        try:
            pp = self.rano.plan_plytek(r.sesja_pieca_id, kolejnosc=self._kolejnosc)
            potwierdzone = None
            if pp["plan_id"] not in self._plany_wyslane:
                potwierdzone = self._potwierdzone_z_bazy(pp["plan_id"]) or None
            k.ustaw_plan_rano(pp, potwierdzone=potwierdzone)
        except SE.BladSesji:  # piec niezamkniety z wczesniejszej doby - plytek nie ma juz na stole
            self._plan_p_podpis = podpis
            self._zgas_ramke_p()
            self._plan_p_podpis = podpis
            return
        except Exception as e:  # noqa: BLE001 - P2: stary plan nie moze swiecic (indicate.md: plan, ktorego nie da sie zbudowac = zgaszony)
            if self._plan_p_ponow:
                LOG.warning("kontroler: planu ramki porannej nadal nie da sie przygotowac (%s)", type(e).__name__)
            else:
                LOG.exception("kontroler: planu ramki porannej nie da sie przygotowac - ramka zgaszona, ponowienie")
                self._plan_p_ponow_od = time.monotonic() + OKRES_PONOWIENIA_PLANU_S
            self._zgas_ramke_p()
            self._plan_p_podpis = podpis  # nastepna proba: ponowienie co OKRES_PONOWIENIA_PLANU_S albo zmiana pieca
            self._plan_p_ponow = True
            if self._ustaw_komunikat("ramka_plan_blad", "ramka_plan_blad", True, wroc=True, powod=B.bez_sciezek(type(e).__name__)):
                self._odswiez_potrzebne = True
            return
        self._plany_wyslane.add(pp["plan_id"])
        self._plan_p, self._plan_p_podpis, self._plan_p_dane, self._plan_p_ponow = pp["plan_id"], podpis, pp, False
        if self._usun_komunikat("ramka_plan_blad"):
            self._odswiez_potrzebne = True

    # --- ramka wieczorna: Spacja, analiza, wynik = kolory mapy -------------------------------------
    def _ramka_w_spacja(self) -> None:
        """Spacja (udany "start skanu") wieczorem: ramka W w stan "skanowanie" (gasi poprzedni wynik); znacznik do wyniku skanu."""
        k = self._klient("W")
        if k is None or self.tryb != TRYB_WIECZOR:
            return
        try:
            self._znacznik_spacji = self._w_ostatni = k.skanowanie()
            self._w_aktywny = None
        except Exception:  # noqa: BLE001
            LOG.exception("kontroler: ramka wieczorna - Spacja")

    def _ramka_w_nowy_skan(self, tryb: str | None = None):
        """Nowy skan wieczorny ZLECONY do analizy (nie powtorka ani plik przemianowany - recenzja PR #30 P6): znacznik Spacji,
        a skan bez Spacji - ``znacznik()`` (dziala jak Spacja: ramka gasi poprzedni wynik). Zwraca znacznik skanu albo None."""
        k = self._klient("W")
        if k is None or (tryb or self.tryb) != TRYB_WIECZOR:
            return None
        try:
            z = self._znacznik_spacji if self._znacznik_spacji is not None else k.znacznik()
        except Exception:  # noqa: BLE001
            LOG.exception("kontroler: ramka wieczorna - znacznik skanu")
            return None
        self._znacznik_spacji = None
        self._w_ostatni, self._w_aktywny = z, None
        return z

    def _ramka_w_analiza(self, znacznik) -> None:
        """Start analizy skanu - raz na skan (wolajacy pilnuje; recenzja PR #28 D5: druga ``analiza()`` zaczelaby nowy skan) i tylko
        dla OSTATNIEGO skanu (analiza starszego skanu w kolejce nie zmienia stanu ramki)."""
        k = self._klient("W")
        if k is None or znacznik is None or znacznik != self._w_ostatni:
            return
        try:
            k.analiza()
        except Exception:  # noqa: BLE001
            LOG.exception("kontroler: ramka wieczorna - analiza")

    def _ramka_w_wynik(self, znacznik, skan_id: int) -> None:
        """Wynik skanu zapisany: kolory gniazd ida do ramki po zbudowaniu stanu (``_synchronizuj_ramke_w`` - kolory mapy)."""
        if self._klient("W") is not None and znacznik is not None and znacznik == self._w_ostatni:
            self._w_do_wyslania = (znacznik, skan_id)

    def _ramka_w_blad(self, znacznik) -> None:
        """Blad analizy ostatniego skanu: ramka W w stan "blad" (ciemna, poprzedni wynik nie wraca)."""
        k = self._klient("W")
        if k is None or znacznik is None or znacznik != self._w_ostatni:
            return
        self._w_aktywny = None
        try:
            k.blad()
        except Exception:  # noqa: BLE001
            LOG.exception("kontroler: ramka wieczorna - blad")

    def _synchronizuj_ramke_w(self, stan: StanAplikacji) -> None:
        """Wynik OSTATNIEGO skanu na ramce W: kolory = ``ramka_protokol.kolor_ramki`` statusow gniazd plytki ze stanu (ta sama mapa,
        co na ekranie), wysylane ponownie po kazdej zmianie (decyzja, numer plytki). Skan zablokowany (status inny niz przyjety) -
        ``blad()``; "niewazny" (nowy skan, zdjecie plytki, restart ramki) - koniec."""
        k = self._klient("W")
        if k is None:
            return
        if self._w_do_wyslania is not None:
            znacznik, skan_id = self._w_do_wyslania
            self._w_do_wyslania = None
            if znacznik == self._w_ostatni:
                self._w_aktywny = (znacznik, skan_id, None)
        if self._w_aktywny is None or time.monotonic() < self._test_led_do:
            return
        znacznik, skan_id, wyslane = self._w_aktywny
        if znacznik != self._w_ostatni:
            self._w_aktywny = None
            return
        plytka = stan.plytka(skan_id)
        if plytka is None:
            return
        if plytka.status != SE.STATUS_PRZYJETY or not plytka.aktywna:
            self._w_aktywny = None
            k.blad()
            return
        from . import ramka_protokol as RP  # noqa: PLC0415 - tylko z ramkami (pakiet ``ramka``)

        kolory = {g.nr: RP.kolor_ramki(g.status) for g in plytka.gniazda}
        obraz = (plytka.numer, plytka.uklad, tuple(sorted(kolory.items())))
        if obraz == wyslane:
            return
        wynik = k.wynik(plytka.numer, plytka.uklad, kolory, znacznik)
        self._w_aktywny = None if wynik == "niewazny" else (znacznik, skan_id, obraz)

    def _po_odswiezeniu(self, stan: StanAplikacji) -> None:
        """Po kazdym pelnym zbudowaniu stanu: plan ramki porannej i wynik na ramce wieczornej (bledy - tylko log)."""
        if self.ramki is None or self._zamkniety:
            return
        for funkcja in (self._synchronizuj_ramke_p, self._synchronizuj_ramke_w):
            try:
                funkcja(stan)
            except Exception:  # noqa: BLE001 - ramka to dodatek: blad nie zatrzymuje odswiezania
                LOG.exception("kontroler: blad synchronizacji ramki (%s)", funkcja.__name__)

    def _zamknij_ramki_excel(self) -> None:
        """Zamkniecie programu: obie ramki gasna (``zgas``), klienci zatrzymani (najwyzej ok. 1 s; zgaszenie, ktore nie doszlo -
        ostrzezenie w logu: ramka moze swiecic do konca waznosci planu), Excel rozlaczony (obiekty COM zwolnione)."""
        if self.ramki is not None:
            for k in self._klienci():
                try:
                    k.zgas()
                except Exception:  # noqa: BLE001
                    LOG.exception("kontroler: zgaszenie ramki przy zamknieciu")
            try:
                doszlo = self.ramki.zatrzymaj()
                for rola, ok in (doszlo or {}).items():
                    if not ok:
                        LOG.warning("kontroler: zgaszenie ramki %s przy zamknieciu nie doszlo - ramka moze swiecic do konca waznosci planu", rola)
            except Exception:  # noqa: BLE001
                LOG.exception("kontroler: zatrzymanie klientow ramek")
            self.ramki = None
        if self.excel is not None:
            try:
                self.excel.rozlacz()
            except Exception:  # noqa: BLE001
                LOG.exception("kontroler: rozlaczenie Excela")
        self._excel_kolejka.clear()

    # --- Excel po "Zamknij piec" (E3-A12) ------------------------------------------------------------
    def _po_zamknieciu_pieca(self, wynik: dict) -> None:
        """"Zamknij piec" zapisany (przycisk albo klawisz ramki, w kazdym trybie): ramka poranna gasnie OD RAZU (P3), "Zamknij piec"
        tego pieca z ramki odebrane przed przyjeciem planu nowej wersji = nieaktualne (P7); Excel ODROCZONY do nastepnych obiegow
        petli okna (P1: najpierw ramka i ekran, potem odczyty arkusza - jeden na obieg); bez Excela - komunikat z lista kuwet (A7).
        Nigdy nie rzuca wyjatku."""
        try:
            k = self._klient("P")
            if wynik.get("data") and wynik.get("nr_w_dniu") is not None:
                pid = SR.plan_id({"data": wynik["data"], "nr_w_dniu": wynik["nr_w_dniu"]})
                wersja = (k.stan().get("wersja") if k is not None else None) or 0
                self._plany_czekaja[pid] = wersja if _jest_liczba(wersja) else 0
            self._zgas_ramke_p()
            if self.excel is None:
                self._komunikat_excela(wynik)
                return
            sid = wynik.get("sesja_pieca_id")
            if not _jest_liczba(sid):
                return
            self._excel_odloz_biezacy(sid)
            self._excel_piec = (sid, wynik.get("nr_w_dniu"), wynik.get("data"))
            self._excel_pozycje, self._excel_blad, self._excel_widoczne = [], None, False
            self._excel_kolejka.append(("piec", sid, True))
        except Exception:  # noqa: BLE001 - piec jest zamkniety; ramka i Excel to dodatki
            LOG.exception("kontroler: czynnosci po 'Zamknij piec'")

    def _excel_odloz_biezacy(self, nowy_sid: int) -> None:
        """P5: niezalatwione pozycje pokazanego pieca nie znikaja po cichu, gdy pojawia sie inny piec - piec trafia do zaleglych
        (komunikat, przycisk w oknie Excela)."""
        if self._excel_piec is None or self._excel_piec[0] == nowy_sid:
            return
        ile = sum(1 for p in self._excel_pozycje if not p.zalatwiona)
        if ile:
            sid, nr, data = self._excel_piec
            self._excel_dodaj_zalegly(sid, nr, data, ile)

    def _excel_dodaj_zalegly(self, sid: int, nr, data, ile: int) -> None:
        self._excel_zalegle[sid] = (nr, data, ile)
        data = data or ""
        self._komunikat("excel_zalegle", id_=f"excel_zalegle:{sid}", nr=nr or "?", doba=f"{data[8:10]}.{data[5:7]}" if len(data) >= 10 else "?",
                        ile=f"{ile} {ST.odmiana(ile, *ST.ZLECENIA_ODMIANA)}")

    def _excel_przelicz_zalegle(self) -> None:
        """P5 przy starcie: piece zamkniete w ostatnich ``ZALEGLE_EXCELA_H`` godzinach (najwyzej ``ZALEGLE_EXCELA_PIECE``) ze zleceniami
        kompletnymi bez wpisu w ``excel_zapisy`` (poza "blad")."""
        od = (self._zegar() - dt.timedelta(hours=ZALEGLE_EXCELA_H)).replace(microsecond=0).isoformat()
        for w in self.sesja.baza.wiersze("SELECT id FROM sesje_pieca WHERE zamknieto IS NOT NULL AND zamknieto >= ? ORDER BY zamknieto DESC, id DESC "
                                         "LIMIT ?", (od, ZALEGLE_EXCELA_PIECE)):
            wynik = self.rano.wynik_pieca(w["id"]) or {}
            zalatwione = self._excel_zalatwione(w["id"])
            ile = sum(1 for z in wynik.get("kompletne") or () if z.get("zlecenie_id") not in zalatwione)
            if ile:
                self._excel_dodaj_zalegly(w["id"], wynik.get("nr_w_dniu"), wynik.get("data"), ile)

    def _excel_zalatwione(self, sid: int) -> set:
        return {w["zlecenie_id"] for w in self.sesja.baza.wiersze(
            "SELECT zlecenie_id FROM excel_zapisy WHERE sesja_pieca_id = ? AND wynik != ? AND zlecenie_id IS NOT NULL", (sid, "blad"))}

    def _przetworz_excel(self) -> int:
        """Jeden krok Excela na obieg petli okna (P1): propozycje pieca (jeden odczyt arkusza), poprawki do logu (jeden odczyt),
        "juz odhaczone" bez watpliwosci (jeden odczyt na pozycje). Kazdy blad = komunikat z lista kuwet (P8)."""
        if not self._excel_kolejka or self.excel is None or self._zamkniety:
            return 0
        krok = self._excel_kolejka.popleft()
        try:
            if krok[0] == "piec":
                self._excel_krok_piec(krok[1], poprawki=krok[2])
            elif krok[0] == "poprawki":
                self._excel_krok_poprawki(krok[1])
            elif krok[0] == "juz":
                self._excel_krok_juz(*krok[1])
        except Exception:  # noqa: BLE001 - P8: nieoczekiwany blad (np. typ komorki z pywin32) = komunikat, praca dalej
            LOG.exception("kontroler: krok Excela (%s) nie powiodl sie", krok[0])

            def piec_kroku(x: tuple) -> int:
                return x[1][0] if x[0] == "juz" else x[1]

            sid = piec_kroku(krok)
            self._excel_kolejka = collections.deque(x for x in self._excel_kolejka if piec_kroku(x) != sid)
            self._excel_blad_kroku(sid, ST.NAPIS_EXCEL_BLAD_PROGRAMU)
        self._odswiez()
        return 1

    def _excel_blad_kroku(self, sid: int, powod: str) -> None:
        try:
            self.excel.rozlacz()
        except Exception:  # noqa: BLE001
            pass
        self._excel_blad = B.bez_sciezek(powod)[:300]
        wynik = self.rano.wynik_pieca(sid) or {}
        zalatwione = self._excel_zalatwione(sid)
        self._komunikat_excela_bledu(wynik, [z for z in wynik.get("kompletne") or () if z.get("zlecenie_id") not in zalatwione])

    def _excel_krok_piec(self, sid: int, *, poprawki: bool = False) -> None:
        """Propozycje dla zamknietego pieca (swiezy odczyt): zlecenia kompletne bez wpisu w ``excel_zapisy`` tego pieca (poza
        "blad" - poprzednia proba z bledem pokazana przy pozycji, D9); takze po restarcie i ponownym zamknieciu (bez dubli w logu,
        D3). Tryb "cien": log porownawczy z TEGO odczytu (bez odczytu na pozycje - P1)."""
        from . import excel as EX  # noqa: PLC0415

        ex = self.excel
        wynik = self.rano.wynik_pieca(sid)
        if not wynik or not wynik.get("zamknieto"):  # piec otwarty ponownie w miedzyczasie
            if self._excel_piec is not None and self._excel_piec[0] == sid:
                self._excel_piec, self._excel_pozycje, self._excel_widoczne = None, [], False
            return
        zalatwione = self._excel_zalatwione(sid)
        bledy = {w["zlecenie_id"]: w["wiersz"] for w in self.sesja.baza.wiersze(
            "SELECT zlecenie_id, wiersz FROM excel_zapisy WHERE sesja_pieca_id = ? AND wynik = ? AND zlecenie_id IS NOT NULL ORDER BY id", (sid, "blad"))}
        kompletne = [z for z in (wynik.get("kompletne") or []) if z.get("zlecenie_id") not in zalatwione]
        self._excel_odloz_biezacy(sid)
        self._excel_piec = (sid, wynik.get("nr_w_dniu"), wynik.get("data"))
        self._excel_pozycje, self._excel_blad, self._excel_widoczne, self._excel_bledy = [], None, False, bledy
        self._excel_jawnie = False
        try:
            pozycje = ex.propozycje({**wynik, "kompletne": kompletne}) if kompletne else []
        except EX.BladExcela as e:
            self._excel_blad_kroku(sid, str(e))
            return
        for poz, zl in zip(pozycje, kompletne):  # r3 P-N2: pozycja z bledem jednego zlecenia (``zlecenie_id`` None) - tozsamosc
            if poz.zlecenie_id is None and _jest_liczba(zl.get("zlecenie_id")):  # z kompletne (ta sama kolejnosc): mozna ja pominac,
                poz.zlecenie_id = zl["zlecenie_id"]  # a wpis logu ma zlecenie (tryb "cien" nie dopisuje go przy kazdym pokazaniu)
        self._usun_komunikat(ID_EXCEL)
        if self._excel_zalegle.pop(sid, None) is not None:
            self._usun_komunikat(f"excel_zalegle:{sid}")
        self._excel_pozycje = pozycje
        if poprawki and [x for x in wynik.get("poprawki") or () if x.get("zlecenie_id") not in zalatwione]:
            self._excel_kolejka.appendleft(("poprawki", sid))
        operator = self.sesja.operator
        if ex.tryb == EX.TRYB_CIEN:
            if pozycje:
                wpisy = ex.zapisz_cien_bez_odczytu(pozycje, operator)
                self._komunikat("excel_cien", id_=ID_EXCEL, nr=wynik.get("nr_w_dniu") or "?",
                                ile=f"{len(wpisy)} {ST.odmiana(len(wpisy), *ST.ZLECENIA_ODMIANA)}")
            return
        for p in pozycje:  # "juz odhaczone" bez watpliwosci - tylko log, bez pytania, po jednej na obieg petli
            if p.dopasowanie.klasa == EX.KLASA_JUZ_ODHACZONE and not p.dopasowanie.do_sprawdzenia and p.zlecenie_id is not None:
                self._excel_kolejka.append(("juz", (sid, p.zlecenie_id)))
        self._excel_widoczne = any(not p.zalatwiona for p in pozycje)

    def _excel_krok_poprawki(self, sid: int) -> None:
        wynik = self.rano.wynik_pieca(sid) or {}
        zalatwione = self._excel_zalatwione(sid)
        poprawki = [x for x in wynik.get("poprawki") or () if x.get("zlecenie_id") not in zalatwione]
        if poprawki:
            self.excel.zaloguj_poprawki({**wynik, "poprawki": poprawki}, self.sesja.operator)  # SE5: tylko log

    def _excel_krok_juz(self, sid: int, zlecenie_id: int) -> None:
        from . import excel as EX  # noqa: PLC0415

        p = next((x for x in self._excel_pozycje if x.sesja_pieca_id == sid and x.zlecenie_id == zlecenie_id and not x.zalatwiona), None)
        if p is None:
            return
        try:
            self.excel.zaloguj_juz_odhaczone(p, self.sesja.operator)
        except EX.BladExcela as e:
            LOG.warning("kontroler: 'juz odhaczone' bez wpisu w logu (%s) - pozycja czeka na osobe", type(e).__name__)
        self._excel_widoczne = any(not x.zalatwiona for x in self._excel_pozycje)

    def _komunikat_excela_bledu(self, wynik: dict, kompletne: list) -> None:
        kuwety = [z.get("kuweta") or "?" for z in kompletne]
        lista = ", ".join(kuwety[:MAX_KUWET_KOMUNIKATU]) + (ST.I_INNYCH.format(n=len(kuwety) - MAX_KUWET_KOMUNIKATU)
                                                          if len(kuwety) > MAX_KUWET_KOMUNIKATU else "")
        data = wynik.get("data") or ""
        self._komunikat("excel_blad", id_=ID_EXCEL, powod=self._excel_blad or "", nr=wynik.get("nr_w_dniu") or "?",
                        doba=f"{data[8:10]}.{data[5:7]}" if len(data) >= 10 else "?",
                        ile=f"{len(kuwety)} {ST.odmiana(len(kuwety), *ST.ZLECENIA_ODMIANA)}", kuwety=lista or "-")

    def _wyczysc_excel_otwartego(self) -> None:
        """Piec pozycji Excela znow otwarty (``otworz_piec_ponownie``, ``cofnij_przeniesienie`` - D3): propozycje znikaja."""
        if self._excel_piec is None:
            return
        w = self.sesja.baza.wiersz("SELECT zamknieto FROM sesje_pieca WHERE id = ?", (self._excel_piec[0],))
        if w is None or not w["zamknieto"]:
            self._excel_pozycje, self._excel_widoczne, self._excel_piec = [], False, None
            self._excel_kolejka.clear()

    def _stan_excel(self) -> StanExcel | None:
        if self.excel is None:
            return None
        pozycje = []
        for i, p in enumerate(self._excel_pozycje):
            blad = p.zlecenie_id in self._excel_bledy
            pozycje.append(PozycjaExcel(nr=i, kuweta=p.kuweta, klasa=p.dopasowanie.klasa, wiersz=p.dopasowanie.wiersz, regula=p.dopasowanie.regula,
                                        powod=p.dopasowanie.powod, do_sprawdzenia=bool(p.dopasowanie.do_sprawdzenia), data=p.dopasowanie.data,
                                        kandydatow=len(p.dopasowanie.kandydaci), zalatwiona=bool(p.zalatwiona), wynik=p.stan,
                                        zlecenie_id=p.zlecenie_id, sesja_pieca_id=p.sesja_pieca_id, poprzedni_blad=blad,
                                        poprzedni_wiersz=self._excel_bledy.get(p.zlecenie_id) if blad else None))
        do = sum(1 for p in pozycje if not p.zalatwiona)
        sid, nr, data = self._excel_piec or (None, None, None)
        try:
            ostrzezenia = tuple(self.excel.ostrzezenia)
        except Exception:  # noqa: BLE001
            ostrzezenia = ()
        zalegle = tuple((s, n, d, ile) for s, (n, d, ile) in sorted(self._excel_zalegle.items()) if s != sid)
        return StanExcel(tryb=self.excel.tryb, sesja_pieca_id=sid, nr_w_dniu=nr, data=data, pozycje=tuple(pozycje),
                         widoczne=self._excel_widoczne and (do > 0 or (self._excel_jawnie and bool(zalegle))), blad=self._excel_blad,
                         ostrzezenia=ostrzezenia, do_zalatwienia=do,
                         w_toku=len(self._excel_kolejka), zalegle=zalegle)

    def _pozycja_excela(self, sesja_pieca_id: int, zlecenie_id: int):
        """P4: pozycja wskazana tozsamoscia (piec + zlecenie), nie numerem na liscie - lista zmienila sie = odmowa bez zapisu."""
        if self.excel is None:
            raise SE.BladSesji(ST.NAPIS_EXCEL_NIEPODLACZONY)
        p = next((x for x in self._excel_pozycje if x.sesja_pieca_id == sesja_pieca_id and x.zlecenie_id == zlecenie_id), None)
        if p is None:
            raise SE.BladSesji(ST.NAPIS_POZYCJA_EXCELA_INNA)
        return p

    # --- polecenia ramek i Excela (E3-A12) ---------------------------------------------------------
    def test_led(self) -> Odpowiedz:
        def wykonaj() -> int:
            klienci = self._klienci()
            if not klienci:
                raise SE.BladSesji(ST.NAPIS_RAMKI_NIEPODLACZONE)
            for k in klienci:
                k.tryb("test_led")
            self._test_led_do = time.monotonic() + CZAS_TEST_LED_S
            self._plan_p_podpis, self._w_aktywny, self._znacznik_spacji = None, None, None
            self._komunikat("ramki_test_led", id_=ID_TEST_LED)
            self._stan_ramek = self._odczytaj_ramki()
            return len(klienci)

        return self._polecenie(wykonaj, operator=False, nazwa="test_led", punkty=False)

    def przejmij_ramke(self, rola: str) -> Odpowiedz:
        if self._zamkniety:
            return self._zamkniety_odp()
        if not isinstance(rola, str) or rola not in ZRODLA_RAMEK:
            return self._zle_argumenty("przejmij_ramke")

        def wykonaj() -> str:
            k = self._klient(rola)
            if k is None:
                raise SE.BladSesji(ST.NAPIS_RAMKI_NIEPODLACZONE)
            k.wznow()
            self.sesja.baza.zdarzenie("ui", "ramka_przejeta", {"rola": rola}, czas=self._teraz())
            return rola

        return self._polecenie(wykonaj, operator=False, nazwa="przejmij_ramke", punkty=False)

    def excel_zatwierdz(self, sesja_pieca_id: int, zlecenie_id: int, wiersz: int | None = None) -> Odpowiedz:
        """Zatwierdzenie pozycji okna Excela (piec + zlecenie - P4) - wylacznie po kliknieciu osoby (A9, wymaganie 1); osoba =
        wybrana na zmianie."""
        from . import excel as EX  # noqa: PLC0415

        def wykonaj() -> ZamrozonySlownik:
            p = self._pozycja_excela(sesja_pieca_id, zlecenie_id)
            try:
                return zamroz(self.excel.zatwierdz(p, self.sesja.operator, wiersz=wiersz))
            except EX.BladExcela as e:
                raise SE.BladSesji(B.bez_sciezek(str(e))[:400]) from e

        liczby = (sesja_pieca_id, zlecenie_id) + (() if wiersz is None else (wiersz,))
        return self._polecenie(wykonaj, nazwa="excel_zatwierdz", liczby=liczby, punkty=False)

    def excel_pomin(self, sesja_pieca_id: int, zlecenie_id: int) -> Odpowiedz:
        from . import excel as EX  # noqa: PLC0415

        def wykonaj() -> ZamrozonySlownik:
            p = self._pozycja_excela(sesja_pieca_id, zlecenie_id)
            try:
                return zamroz(self.excel.pomin(p, self.sesja.operator))
            except EX.BladExcela as e:
                raise SE.BladSesji(B.bez_sciezek(str(e))[:400]) from e

        return self._polecenie(wykonaj, nazwa="excel_pomin", liczby=(sesja_pieca_id, zlecenie_id), punkty=False)

    def _excel_pokaz_piec(self, sid: int) -> int:
        """Okno Excela dla pieca ``sid`` (jawny wybor osoby): widoczne, gdy sa pozycje do zalatwienia ALBO inne zalegle piece
        (r3 P-N3 - przyciski zaleglych w oknie, takze gdy pokazany piec jest zalatwiony)."""
        if (self._excel_piec is not None and self._excel_piec[0] == sid and self._excel_blad is None
                and any(not p.zalatwiona for p in self._excel_pozycje)):
            pass
        else:
            self._excel_krok_piec(sid)
            if self._excel_blad:
                raise SE.BladSesji(self._excel_blad)
        self._excel_widoczne, self._excel_jawnie = True, True
        return sum(1 for p in self._excel_pozycje if not p.zalatwiona)

    def excel_odswiez(self) -> Odpowiedz:
        def wykonaj() -> int:
            if self.excel is None:
                raise SE.BladSesji(ST.NAPIS_EXCEL_NIEPODLACZONY)
            sid = self._excel_piec[0] if self._excel_piec is not None else self._ostatni_zamkniety_id()
            if sid is None:
                raise SE.BladSesji(ST.NAPIS_BRAK_PIECA_EXCELA)
            jawnie = self._excel_jawnie  # r4 D-R3-2: okno pokazane jawnie (takze tylko dla zaleglych piecow) zostaje po odswiezeniu
            self._excel_krok_piec(sid)
            if self._excel_blad:
                raise SE.BladSesji(self._excel_blad)
            self._excel_jawnie = jawnie
            self._excel_widoczne = jawnie or any(not p.zalatwiona for p in self._excel_pozycje)
            return len(self._excel_pozycje)

        return self._polecenie(wykonaj, nazwa="excel_odswiez", punkty=False)

    def excel_pokaz(self, sesja_pieca_id: int | None = None) -> Odpowiedz:
        def wykonaj() -> int:
            if self.excel is None:
                raise SE.BladSesji(ST.NAPIS_EXCEL_NIEPODLACZONY)
            sid = sesja_pieca_id if sesja_pieca_id is not None else (self._excel_piec[0] if self._excel_piec is not None
                                                                      else self._ostatni_zamkniety_id())
            if sid is None:
                raise SE.BladSesji(ST.NAPIS_BRAK_PIECA_EXCELA)
            return self._excel_pokaz_piec(sid)

        return self._polecenie(wykonaj, nazwa="excel_pokaz", liczby=() if sesja_pieca_id is None else (sesja_pieca_id,), punkty=False)

    def excel_zamknij(self) -> Odpowiedz:
        def wykonaj() -> int:
            if self.excel is None:
                raise SE.BladSesji(ST.NAPIS_EXCEL_NIEPODLACZONY)
            self._excel_widoczne = False
            return sum(1 for p in self._excel_pozycje if not p.zalatwiona)

        return self._polecenie(wykonaj, operator=False, nazwa="excel_zamknij", punkty=False)

    def excel_szczegoly(self, sesja_pieca_id: int, zlecenie_id: int) -> SzczegolyExcel | None:
        """Zapytanie okna: folder zlecenia i kandydaci (kolumna H - DANE OSOBOWE, tylko na ekran) pozycji (piec, zlecenie); None = brak."""
        if self._zamkniety or self.excel is None or not (_jest_liczba(sesja_pieca_id) and _jest_liczba(zlecenie_id)):
            return None
        i, p = next(((i, x) for i, x in enumerate(self._excel_pozycje) if x.sesja_pieca_id == sesja_pieca_id and x.zlecenie_id == zlecenie_id),
                    (None, None))
        if p is None:
            return None
        zielony = tuple(self.excel.konf.kolor)
        kandydaci = []
        try:
            for x in p.kandydaci_do_okna:
                kol = x.get("wypelnienie_b")
                kandydaci.append(KandydatExcel(wiersz=x["wiersz"], data=x.get("data"), numer_b=x.get("numer_b") or "", kuweta=x.get("kuweta") or "",
                                               nazwa=x.get("nazwa") or "", kolor_b="#%02x%02x%02x" % tuple(kol) if kol else None,
                                               zielone=bool(kol) and tuple(kol) == zielony))
        except Exception:  # noqa: BLE001 - podglad okna nie moze zatrzymac programu
            LOG.exception("kontroler: kandydatow Excela nie da sie pokazac")
        return SzczegolyExcel(nr=i, folder=p.folder or "", kandydaci=tuple(kandydaci))

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
        poziom, tytul, tekst = tekst_komunikatu(rodzaj, **pola)
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

    def _pytania_plytki(self, s: dict, propozycja: dict | None, czasy: dict, typ: str | None, numery_plytek: tuple, rano: bool = False) -> list:
        wynik = []
        skan_id = s["id"]
        if propozycja is not None and (skan_id, propozycja["poprzedni_id"]) not in self._odrzucone:
            n, u = propozycja["liczba_decyzji"], propozycja["liczba_ukruszonych"]
            wzor = ST.SKUTEK_Z_DECYZJAMI_RANO if rano else ST.SKUTEK_Z_DECYZJAMI  # rano: decyzje poranne (wybor, przypisanie)
            skutek = ST.SKUTEK_BEZ_DECYZJI if n == 0 else wzor.format(n=n, u=u, decyzji=ST.odmiana(n, "decyzja", "decyzje", "decyzji"))
            podstawa = ST.PODSTAWY_PONOWNEGO_SKANU.get(propozycja.get("podstawa")) if rano else None  # A6 runda 4: dlaczego to ponowny skan
            if podstawa:
                skutek = f"{podstawa} {skutek}"
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
            # rano plytki nie z trybu nie dopuszcza sie (A6 runda 2, P2 - ramka poranna jej nie obsluzy): skan sie pomija
            drugi = Przycisk("pomin_skan", ST.PRZYCISKI["pomin_skan"], (skan_id,)) if rano else Przycisk("dopusc_plytke", ST.PRZYCISKI["dopusc_plytke"], (skan_id,))
            wynik.append(Pytanie(id=id_, rodzaj="plytka_nie_z_trybu", skan_id=skan_id, poziom=poziom, tytul=tytul, tekst=tekst,
                                 odpowiedzi=(Przycisk("zamknij_pytanie", ST.PRZYCISK_ZESKANUJE_WLASCIWA, (id_,)), drugi)))
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
        if stary is not None and stary.tekst == tekst_komunikatu(rodzaj, **pola)[2]:
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

    def _polecenie(self, funkcja: Callable[[], Any], *, operator: bool = True, nazwa: str = "", liczby: tuple = (),
                   punkty: bool | None = None) -> Odpowiedz:
        """Wspolna obsluga polecenia: zamkniety program, zle argumenty (``liczby`` - identyfikatory, ktore musza byc liczbami
        calkowitymi; D1), brak operatora, odmowa ``session``, baza zajeta, inny blad (``blad_polecenia``); potem nowy stan.
        ``punkty`` - czy udane polecenie moze zmienic stan punktow zlecen (pamiec listy brakow, P2); None = wg ``NIE_RUSZA_PUNKTOW``."""
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
            self._uniewaznij_punkty()  # recenzja PR #26, D2: wyjatek mogl wypasc PO zapisie w bazie - lista brakow od nowa
            return self._odmowa("blad_polecenia")
        for kod in ("brak_operatora", "pusta_lista_operatorow", "odmowa", "baza_zajeta", "osoba_spoza_listy", KOD_ZLE_ARGUMENTY, "blad_polecenia",
                    "kuweta_zmienila_sie", "analiza_trwa", "skanowanie_trwa"):
            self._usun_komunikat(f"odmowa:{kod}")  # polecenie przeszlo: stare odmowy nieaktualne
        if punkty if punkty is not None else nazwa not in NIE_RUSZA_PUNKTOW:
            self._uniewaznij_punkty()
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

    def _sesja_skanu(self, skan_id: int):
        """Sesja, ktora obsluguje skan: poranna (``SesjaRano`` - kontrola, ze skan nalezy do otwartego pieca) dla skanu w trybie
        ``rano``, wieczorna dla kazdego innego (takze nieistniejacego - odmowe da ``session``)."""
        w = self.sesja.baza.wiersz("SELECT tryb FROM skany WHERE id = ?", (skan_id,))
        return self.rano if w is not None and w["tryb"] == TRYB_RANO else self.sesja

    def _plytka_dowolna(self, skan_id: int) -> Plytka | None:
        stan = self.stan()
        plytka = stan.plytka(skan_id)
        if plytka is None and stan.rano is not None:
            plytka = stan.rano.plytka(skan_id)
        return plytka

    def _wieczorny(self, skan_id: int) -> bool:
        """Polecenie plytki dla skanu wieczornego (moze zmienic stan punktow - P2); skan poranny punktow nie rusza."""
        return self._sesja_skanu(skan_id) is self.sesja

    def potwierdz_ponowny_skan(self, skan_id: int) -> Odpowiedz:
        return self._polecenie(lambda: self._sesja_skanu(skan_id).zastap_skan(skan_id), nazwa="potwierdz_ponowny_skan", liczby=(skan_id,),
                               punkty=_jest_liczba(skan_id) and self._wieczorny(skan_id))

    def odrzuc_ponowny_skan(self, skan_id: int) -> Odpowiedz:
        def wykonaj() -> int:
            plytka = self._plytka_dowolna(skan_id)
            if plytka is None or plytka.moze_zastapic is None:
                raise SE.BladSesji(f"skan {skan_id}: nie ma propozycji ponownego skanu do odrzucenia")
            self.sesja.baza.zdarzenie("ui", "ponowny_skan_odrzucony", {"poprzedni_id": plytka.moze_zastapic, "operator": self.sesja.operator},
                                      skan_id=skan_id, czas=self._teraz())
            self._odrzucone.add((skan_id, plytka.moze_zastapic))
            return plytka.moze_zastapic

        return self._polecenie(wykonaj, nazwa="odrzuc_ponowny_skan", liczby=(skan_id,))

    def cofnij_zastapienie(self, skan_id: int) -> Odpowiedz:
        return self._polecenie(lambda: self._sesja_skanu(skan_id).cofnij_zastapienie(skan_id), nazwa="cofnij_zastapienie", liczby=(skan_id,),
                               punkty=_jest_liczba(skan_id) and self._wieczorny(skan_id))

    def dopusc_plytke(self, skan_id: int) -> Odpowiedz:
        return self._polecenie(lambda: self._sesja_skanu(skan_id).dopusc_plytke(skan_id), nazwa="dopusc_plytke", liczby=(skan_id,),
                               punkty=_jest_liczba(skan_id) and self._wieczorny(skan_id))

    def cofnij_dopuszczenie(self, skan_id: int) -> Odpowiedz:
        return self._polecenie(lambda: self._sesja_skanu(skan_id).cofnij_dopuszczenie(skan_id), nazwa="cofnij_dopuszczenie", liczby=(skan_id,),
                               punkty=_jest_liczba(skan_id) and self._wieczorny(skan_id))

    def podaj_numer_plytki(self, skan_id: int, numer: int, mimo_nowego_wsadu: bool = False) -> Odpowiedz:
        """Numer plytki podany recznie. Skan poranny (A6 runda 4): zmiana numeru plytki, ktora ma drugi skan innego wsadu
        (``StanRano.nowy_wsad``), bez ``mimo_nowego_wsadu`` nie idzie do sesji - kontroler pyta osobe (``Pytanie``
        ``numer_nowy_wsad``: "Zmien numer mimo to" = to samo polecenie z ``mimo_nowego_wsadu`` True / "Nie zmieniaj")."""
        if self._zamkniety:
            return self._zamkniety_odp()
        if not isinstance(mimo_nowego_wsadu, bool):
            return self._zle_argumenty("podaj_numer_plytki")
        n = numer
        if isinstance(numer, str):  # cyfry z pola tekstowego; nie-liczbe odrzuci session (odmowa z rada)
            try:
                n = int(numer.strip())
            except ValueError:
                n = 0
        if not (_jest_liczba(skan_id) and _jest_liczba(n)):
            return self._zle_argumenty("podaj_numer_plytki")
        sesja = self._sesja_skanu(skan_id)
        if sesja is self.rano and not mimo_nowego_wsadu and self.sesja.operator is not None:
            rano = self.stan().rano
            p = rano.plytka(skan_id) if rano is not None else None
            if (p is not None and rano.nowy_wsad is not None and p.numer is not None and p.numer in rano.nowy_wsad.plytki and n != p.numer
                    and n in (SR.numery_plytki(p.uklad) or ())):
                self._numer_mimo = (skan_id, n)
                self._odswiez()
                q = next((q for q in self.stan().pytania if q.rodzaj == "numer_nowy_wsad" and q.skan_id == skan_id), None)
                return Odpowiedz(False, q.tekst if q is not None else ST.tekst_pytania("numer_nowy_wsad", stary=p.numer, numer=n)[2], "numer_nowy_wsad")

        def wykonaj() -> int:
            if sesja is self.rano:
                wynik = self.rano.podaj_numer_plytki(skan_id, n, mimo_nowego_wsadu=mimo_nowego_wsadu)
            else:
                wynik = self.sesja.podaj_numer_plytki(skan_id, n)
            if self._numer_mimo is not None and self._numer_mimo[0] == skan_id:
                self._numer_mimo = None
            return wynik

        return self._polecenie(wykonaj, nazwa="podaj_numer_plytki", liczby=(skan_id, n), punkty=sesja is self.sesja)

    # --- polecenia poranne (E3-A7) ----------------------------------------------------------------
    def przelacz_tryb(self, tryb: str) -> Odpowiedz:
        """Wieczor / Poranek (Z1: wybiera czlowiek, bez osoby). Wybor trafia do dziennika (``tryb_zmieniony``; bez nazwiska -
        jak dziennik sesji porannej, recenzja PR #26 D4) - po restarcie program wraca do tego trybu. Skany juz zauwazone zostaja
        w trybie, w ktorym je zauwazono."""
        if self._zamkniety:
            return self._zamkniety_odp()
        if not isinstance(tryb, str) or tryb not in TRYBY:
            return self._zle_argumenty("przelacz_tryb")

        def wykonaj() -> str:
            if tryb != self.tryb:
                self.sesja.baza.zdarzenie("ui", "tryb_zmieniony", {"tryb": tryb, "z": self.tryb}, czas=self._teraz())
                self.tryb = tryb
            return tryb

        return self._polecenie(wykonaj, operator=False, nazwa="przelacz_tryb")

    def wybierz_kandydata(self, praca_id: int, sha16: str) -> Odpowiedz:
        if self._zamkniety:
            return self._zamkniety_odp()
        if not isinstance(sha16, str):
            return self._zle_argumenty("wybierz_kandydata")
        return self._polecenie(lambda: self.rano.wybierz_kandydata(praca_id, sha16), nazwa="wybierz_kandydata", liczby=(praca_id,))

    def przypisz_recznie(self, praca_id: int, projekt_id: int | None = None) -> Odpowiedz:
        liczby = (praca_id,) if projekt_id is None else (praca_id, projekt_id)
        return self._polecenie(lambda: self.rano.przypisz_recznie(praca_id, projekt_id), nazwa="przypisz_recznie", liczby=liczby)

    def cofnij_przypisanie(self, praca_id: int, decyzja_id: int | None = None) -> Odpowiedz:
        liczby = (praca_id,) if decyzja_id is None else (praca_id, decyzja_id)
        return self._polecenie(lambda: self.rano.cofnij_przypisanie(praca_id, decyzja_id=decyzja_id), nazwa="cofnij_przypisanie", liczby=liczby)

    def _analiza_trwa(self) -> bool:
        """Skan w analizie albo w kolejce (czesc "zywa" stanu): wynik, ktory dojdzie po "Zamknij piec", otworzylby nowy piec."""
        return self._zajety() == "analiza_trwa"

    def _komunikat_excela(self, wynik: dict) -> None:
        """Bez Excela (do A12): komunikat z WLASNA lista kuwet zamknietego pieca (P1 - ekran moze juz pokazywac nastepny piec)."""
        kompletne = wynik.get("kompletne") or []
        if not kompletne or self._excel_dostepny():
            return
        kuwety = [z.get("kuweta") or "?" for z in kompletne]
        lista = ", ".join(kuwety[:MAX_KUWET_KOMUNIKATU]) + (ST.I_INNYCH.format(n=len(kuwety) - MAX_KUWET_KOMUNIKATU)
                                                          if len(kuwety) > MAX_KUWET_KOMUNIKATU else "")
        data = wynik.get("data") or ""
        self._komunikat("excel_niedostepny", id_=ID_EXCEL, ile=f"{len(kuwety)} {ST.odmiana(len(kuwety), *ST.ZLECENIA_ODMIANA)}",
                        nr=wynik.get("nr_w_dniu") or "?", doba=f"{data[8:10]}.{data[5:7]}" if len(data) >= 10 else "?",
                        godzina=(wynik.get("zamknieto") or "")[11:16] or "?", kuwety=lista)

    def zamknij_piec(self, sesja_pieca_id: int | None = None) -> Odpowiedz:
        """"Zamknij piec" pokazanego pieca (``session_rano.zamknij_piec(sesja_pieca_id=...)`` - spoznione klikniecie nie zamknie
        nastepnego pieca); odmowa ``analiza_trwa`` / ``skanowanie_trwa``, dopoki trwa analiza albo skanowanie (A6 runda 2 D11,
        recenzja PR #26 P3). Bez Excela (do A12) komunikat z lista kuwet do odhaczenia recznie."""
        if self._zamkniety:
            return self._zamkniety_odp()
        zajety = self._zajety()
        if zajety is not None:
            return self._odmowa(zajety)

        def wykonaj() -> ZamrozonySlownik:
            wynik = self.rano.zamknij_piec(sesja_pieca_id=sesja_pieca_id)
            self._po_zamknieciu_pieca(wynik)  # E3-A12: Excel ("pytaj" / "cien") albo komunikat z lista kuwet
            return zamroz(wynik)

        return self._polecenie(wykonaj, nazwa="zamknij_piec", liczby=() if sesja_pieca_id is None else (sesja_pieca_id,))

    def zamknij_piec_i_przenies(self, sesja_pieca_id: int, skany: tuple) -> Odpowiedz:
        """Zapomniany "Zamknij piec" (A6 runda 4, ``session_rano.zamknij_piec_i_przenies``): odpowiedz "Tak" na pytanie
        ``nowy_wsad``. Te same odmowy co ``zamknij_piec``; ``dane`` = {"zamkniety": wynik, "nowy_piec": ...}."""
        if self._zamkniety:
            return self._zamkniety_odp()
        if not isinstance(skany, (tuple, list)) or not skany or not all(_jest_liczba(x) for x in skany):
            return self._zle_argumenty("zamknij_piec_i_przenies")
        zajety = self._zajety()
        if zajety is not None:
            return self._odmowa(zajety)

        def wykonaj() -> ZamrozonySlownik:
            wynik = self.rano.zamknij_piec_i_przenies(list(skany), sesja_pieca_id=sesja_pieca_id)
            self._po_zamknieciu_pieca(wynik.get("zamkniety") or {})
            return zamroz(wynik)

        return self._polecenie(wykonaj, nazwa="zamknij_piec_i_przenies", liczby=(sesja_pieca_id,))

    def cofnij_przeniesienie(self, sesja_pieca_id: int) -> Odpowiedz:
        """Cofa "zamknij piec i przenies" (``session_rano.cofnij_przeniesienie``, A6 runda 5): skany wracaja do poprzedniego pieca,
        ktory znow jest otwarty; odmowa A6 (np. do nowego pieca doszly inne skany) - komunikat."""
        def wykonaj() -> ZamrozonySlownik:
            wynik = zamroz(self.rano.cofnij_przeniesienie(sesja_pieca_id))
            self._wyczysc_excel_otwartego()  # recenzja PR #30 D3
            return wynik

        return self._polecenie(wykonaj, nazwa="cofnij_przeniesienie", liczby=(sesja_pieca_id,))

    def otworz_piec_ponownie(self, sesja_pieca_id: int) -> Odpowiedz:
        """Cofa "Zamknij piec" ostatniego pieca (``session_rano.otworz_piec_ponownie``; odhaczen w Excelu program nie zdejmuje)."""
        def wykonaj() -> ZamrozonySlownik:
            wynik = zamroz(self.rano.otworz_piec_ponownie(sesja_pieca_id))
            self._wyczysc_excel_otwartego()  # propozycje sprzed otwarcia: X4 i tak odmowi
            return wynik

        return self._polecenie(wykonaj, nazwa="otworz_piec_ponownie", liczby=(sesja_pieca_id,))

    def pomin_skan(self, skan_id: int) -> Odpowiedz:
        return self._polecenie(lambda: self.rano.pomin_skan(skan_id), nazwa="pomin_skan", liczby=(skan_id,))

    def cofnij_pominiecie(self, skan_id: int) -> Odpowiedz:
        return self._polecenie(lambda: self.rano.cofnij_pominiecie(skan_id), nazwa="cofnij_pominiecie", liczby=(skan_id,))

    def zamknij_brak_recznie(self, projekt_id: int, powod: str) -> Odpowiedz:
        if self._zamkniety:
            return self._zamkniety_odp()
        if not isinstance(powod, str) or powod not in SR.POWODY_ZAMKNIECIA:
            return self._zle_argumenty("zamknij_brak_recznie")
        return self._polecenie(lambda: self.rano.zamknij_brak_recznie(projekt_id, powod=powod), nazwa="zamknij_brak_recznie", liczby=(projekt_id,))

    def cofnij_zamkniecie_reczne(self, projekt_id: int) -> Odpowiedz:
        return self._polecenie(lambda: self.rano.cofnij_zamkniecie_reczne(projekt_id), nazwa="cofnij_zamkniecie_reczne", liczby=(projekt_id,))

    def ustaw_kolejnosc(self, kolejnosc: str) -> Odpowiedz:
        """Kolejnosc kuwet (U7): ``liczba`` / ``numer``; wybor ekranu (bez osoby i bez wpisu w bazie). Biezaca kuweta = pierwsza
        nierozlozona w nowej kolejnosci (zmiana kolejnosci to wybor osoby - B1)."""
        if self._zamkniety:
            return self._zamkniety_odp()
        if not isinstance(kolejnosc, str) or kolejnosc not in KOLEJNOSCI_KUWET:
            return self._zle_argumenty("ustaw_kolejnosc")

        def wykonaj() -> str:
            if kolejnosc != self._kolejnosc:
                self._kolejnosc = kolejnosc
                self._kuweta_biezaca.clear()
            return kolejnosc

        return self._polecenie(wykonaj, operator=False, nazwa="ustaw_kolejnosc")

    def _piec_do_rozkladania(self) -> StanRano:
        """Pokazany stan pieca (juz zbudowany - P2: bez drugiego liczenia stanu na kazdy Enter); odmowa bez otwartego pieca."""
        r = self.stan().rano
        if r is None or r.sesja_pieca_id is None or not r.otwarty:
            raise SE.BladSesji(ST.tekst_komunikatu("brak_pieca")[2])
        return r

    def wybierz_kuwete(self, kuweta: str) -> Odpowiedz:
        """Numer kuwety wpisany recznie (U7, trzeci sposob): ta kuweta staje sie biezaca (bez osoby - to wybor widoku)."""
        if self._zamkniety:
            return self._zamkniety_odp()
        if not isinstance(kuweta, str):
            return self._zle_argumenty("wybierz_kuwete")
        k = self._norm_kuweta(kuweta)

        def wykonaj() -> str:
            r = self._piec_do_rozkladania()
            if k not in {x.kuweta for x in r.kuwety}:
                raise SE.BladSesji(ST.tekst_komunikatu("kuweta_spoza_pieca", kuweta=k or "?")[2])
            self._kuweta_biezaca[r.plan_id] = k
            return k

        return self._polecenie(wykonaj, operator=False, nazwa="wybierz_kuwete")

    def _kuweta_inna(self, podana: str, obecna: str | None) -> Odpowiedz | None:
        """B1: polecenie niesie kuwete widoczna na ekranie - gdy w kontrolerze jest juz inna, odmowa bez zapisu."""
        if self._norm_kuweta(podana) == obecna:
            return None
        if obecna is None:
            return None  # odmowe "wszystko rozlozone" / "nic do cofniecia" da polecenie
        return self._odmowa("kuweta_zmienila_sie", kuweta=obecna, podana=self._norm_kuweta(podana) or "?")

    def potwierdz_kuwete(self, kuweta: str) -> Odpowiedz:
        """Enter: kuweta ``kuweta`` (biezaca pokazana na ekranie) rozlozona - wpis ``kuweta_potwierdzona`` w dzienniku (bez nazwiska,
        jak dziennik sesji porannej - D4; operator wymagany); biezaca = nastepna nierozlozona. Odmowa ``kuweta_zmienila_sie``, gdy
        biezaca w kontrolerze jest inna niz pokazana (recenzja PR #26, B1)."""
        if self._zamkniety:
            return self._zamkniety_odp()
        if not isinstance(kuweta, str):
            return self._zle_argumenty("potwierdz_kuwete")
        if self.sesja.operator is not None:
            r = self.stan().rano
            odmowa = self._kuweta_inna(kuweta, r.kuweta_biezaca if r is not None and r.otwarty else None)
            if odmowa is not None:
                return odmowa

        def wykonaj() -> str:
            r = self._piec_do_rozkladania()
            if r.kuweta_biezaca is None:
                raise SE.BladSesji(ST.tekst_komunikatu("kuwety_rozlozone")[2])
            self.sesja.baza.zdarzenie("ui", "kuweta_potwierdzona", {"plan_id": r.plan_id, "kuweta": r.kuweta_biezaca}, czas=self._teraz())
            self._rozlozone(r.plan_id).append(r.kuweta_biezaca)
            self._kuweta_biezaca.pop(r.plan_id, None)
            return r.kuweta_biezaca

        return self._polecenie(wykonaj, nazwa="potwierdz_kuwete")

    def cofnij_kuwete(self, kuweta: str) -> Odpowiedz:
        """Backspace: cofa potwierdzenie kuwety ``kuweta`` (ostatnia potwierdzona pokazana na ekranie - ``kuweta_do_cofniecia``),
        wpis ``kuweta_cofnieta``; ta kuweta znow jest biezaca. Odmowa ``kuweta_zmienila_sie``, gdy ostatnia jest inna (B1)."""
        if self._zamkniety:
            return self._zamkniety_odp()
        if not isinstance(kuweta, str):
            return self._zle_argumenty("cofnij_kuwete")
        if self.sesja.operator is not None:
            r = self.stan().rano
            odmowa = self._kuweta_inna(kuweta, r.kuweta_do_cofniecia if r is not None and r.otwarty else None)
            if odmowa is not None:
                return odmowa

        def wykonaj() -> str:
            r = self._piec_do_rozkladania()
            stos = self._rozlozone(r.plan_id)
            if not stos:
                raise SE.BladSesji(ST.tekst_komunikatu("brak_kuwety_do_cofniecia")[2])
            k = stos[-1]
            self.sesja.baza.zdarzenie("ui", "kuweta_cofnieta", {"plan_id": r.plan_id, "kuweta": k}, czas=self._teraz())
            stos.pop()
            self._kuweta_biezaca[r.plan_id] = k
            return k

        return self._polecenie(wykonaj, nazwa="cofnij_kuwete")

    def projekty_kuwety(self, kuweta: str) -> tuple:
        """Projekty (punkty) zlecenia o kuwecie ``kuweta`` do przypisania recznego: ``ProjektPuli`` (zab, typ, stan punktu,
        miniatura) - bez nazw folderow i plikow. Zly argument, zamkniety program albo baza zajeta = pusta krotka."""
        if self._zamkniety or not isinstance(kuweta, str):
            return ()
        k = self._norm_kuweta(kuweta)
        if not k:
            return ()
        try:
            wiersze = self.sesja.baza.wiersze(
                "SELECT p.id AS projekt_id, p.zlecenie_id, p.zeby, p.typ, p.sha16, z.kuweta, z.zrodlo, sp.stan FROM projekty p "
                "JOIN zlecenia z ON z.id = p.zlecenie_id LEFT JOIN stan_punktow sp ON sp.projekt_id = p.id "
                "WHERE p.usuniety = 0 AND COALESCE(z.usuniety, 0) = 0 AND z.kuweta = ? ORDER BY p.zlecenie_id, p.id LIMIT ?", (k, MAX_PROJEKTOW_KUWETY))
            mini = self._miniatury([w["sha16"] for w in wiersze])
        except (sqlite3.Error, B.BladBazy) as e:
            LOG.warning("kontroler: projektow kuwety nie da sie odczytac (%s)", type(e).__name__)
            return ()
        return tuple(ProjektPuli(projekt_id=w["projekt_id"], zlecenie_id=w["zlecenie_id"], kuweta=w["kuweta"], zeby=w["zeby"], typ=w["typ"],
                                 zrodlo=w["zrodlo"], sha16=w["sha16"], stan=w["stan"] or SE.STAN_OCZEKUJE, miniatura=mini.get(w["sha16"]))
                     for w in wiersze)

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


# --- poranek (E3-A7): dane sztuczne plytek porannych ------------------------------------------------------------------
# rodzaj pracy porannej -> pokrycia kandydatow (1., 2.); status dopasowania liczony jak w ``match`` (progi z ustawien wzoru:
# akceptacja 0,85, ostrzezenie 0,6, przewaga 0,1). "pewna" - zielony; "zolta" - zolty (dwuznaczna); "dwuznaczna" - dwa bliskie
# kandydaty (szary, ale 1. kandydat >= prog -> dwuznaczna); "nieznana" - slaby kandydat; "brak" - bez kandydatow
_RODZAJE_PRAC_RANO = {"pewna": (0.93,), "zolta": (0.74, 0.55), "dwuznaczna": (0.82, 0.79), "nieznana": (0.35,), "brak": ()}
RODZAJE_PRAC_RANO = tuple(_RODZAJE_PRAC_RANO) + ("podwojny",)


def _status_dopasowania(pokrycia: tuple) -> tuple:
    if not pokrycia:
        return "szary", 0.0
    p1, p2 = pokrycia[0], (pokrycia[1] if len(pokrycia) > 1 else 0.0)
    pewnosc = round(p1 - p2, 4)
    if p1 >= 0.85 and pewnosc >= 0.1:
        return "zielony", pewnosc
    if p1 >= 0.6 and pewnosc >= 0.1:
        return "zolty", pewnosc
    return "szary", pewnosc


def zab_sztuczny(nr: int) -> str:
    """Numer zeba (FDI 11-48) sztucznego projektu ``nr``."""
    return f"{1 + (nr // 8) % 4}{1 + nr % 8}"


def sztuczny_wynik_rano(uklad: str | None = "poranna", numer: int | None = 4, gniazda: dict | None = None, *, projekty: dict | None = None,
                        poza_gniazdem: int = 0, uklad_zgodny: bool = True, skan: str = "skan.stl", czas_s: float = 1.0) -> dict:
    """Wynik analizy plytki porannej (pola ``porownaj``, ktore czyta ``session`` / ``session_rano``) z danych sztucznych.

    ``gniazda``: numer gniazda -> rodzaj z ``RODZAJE_PRAC_RANO``; ``projekty``: numer gniazda -> numer sztucznego projektu
    (``projekt_sztuczny``) albo para (1. kandydat, 2. kandydat); domyslnie 300 + gniazdo i drugi kandydat = 1. + 100. Rano
    wspolczynnik 1,0 (K3). Funkcja czysta, tylko biblioteka standardowa."""
    if not uklad_zgodny:
        return sztuczny_wynik(uklad, numer, {}, uklad_zgodny=False, skan=skan, czas_s=czas_s)
    gniazda = dict(gniazda if gniazda is not None else {1: "pewna", 2: "pewna", 3: "zolta", 4: "nieznana"})
    projekty = projekty or {}
    wpisy, podwojne = [], []

    def wpis(nr: int | None, rodzaj: str, projekt, fragment: str = "praca") -> dict:
        pierwszy, drugi = (projekt if isinstance(projekt, (tuple, list)) else (projekt, projekt + 100))
        pokrycia = _RODZAJE_PRAC_RANO[rodzaj]
        kandydaci = [{"id": projekt_sztuczny(p), "zeby": [zab_sztuczny(p)], "typ": "korona", "pokrycie": pok, "rms_mm": 0.02}
                     for p, pok in zip((pierwszy, drugi), pokrycia)]
        status, pewnosc = _status_dopasowania(pokrycia)
        inspekcja = None if status == "szary" else {"gniazdo": nr, "projekt": kandydaci[0]["id"], "status": "ok", "pokrycie": pokrycia[0],
                                                     "ubytki": [], "plamy": [], "wciecia": [], "uwagi": []}
        return {"gniazdo": nr, "status_fragmentu": fragment, "punkty": 15000, "srodek": [0.0, 0.0, 10.0], "status": status, "pewnosc": pewnosc,
                "uwagi": [], "kandydaci": kandydaci, "skala": {"poprawka_proc": 0.0, "wspolczynnik_puli": 1.0} if kandydaci else None,
                "inspekcja": inspekcja, "status_gniazda": {"zielony": "zielony", "zolty": "zolty"}.get(status, "szary")}

    for nr in sorted(gniazda):
        rodzaj = gniazda[nr]
        projekt = projekty.get(nr, 300 + nr)
        if rodzaj == "podwojny":
            podwojne.append(nr)
            p = projekt[0] if isinstance(projekt, (tuple, list)) else projekt
            wpisy.append(wpis(nr, "pewna", p, "podwojny"))
            wpisy.append(wpis(nr, "pewna", p + 100, "podwojny"))
        else:
            wpisy.append(wpis(nr, rodzaj, projekt))
    for i in range(poza_gniazdem):
        wpisy.append(wpis(None, "brak", 900 + i, "poza_gniazdem"))
    statusy = {k: sum(1 for w in wpisy if w["status_gniazda"] == k) for k in ("zielony", "czerwony", "zolty", "szary", "pomaranczowy")}
    return {"skan": skan, "plytka": uklad, "plytka_wybor": "auto", "uklad_zgodny": True, "wspolczynnik": 1.0, "projekty": 120, "numer": numer,
            "numer_zrodlo": "dolki" if numer is not None else "nieznany", "gniazda": wpisy, "gniazda_puste": [], "gniazda_podwojne": podwojne,
            "poza_gniazdem": poza_gniazdem, "czas_s": {"razem": czas_s}, "statusy_gniazd": statusy, "ubytki": 0}


def miniatura_sztuczna(nr: int, px: int = 64) -> bytes:
    """Miniatura PNG (``px`` x ``px``, skala szarosci, jak ``indeks.miniatura_png``) sztucznego projektu ``nr`` - zarys korony
    z guzkami, ktorych liczba i polozenie zaleza od ``nr`` (kazdy projekt wyglada inaczej). Tylko biblioteka standardowa."""
    import struct
    import zlib

    guzki = 2 + nr % 4
    obrot = (nr * 37 % 360) * math.pi / 180
    rx, ry = 0.40 + 0.06 * (nr % 3), 0.34 + 0.05 * (nr % 2)
    wiersze = []
    for y in range(px):
        wiersz = bytearray([0])  # filtr PNG "brak"
        for x in range(px):
            u, v = (x + 0.5) / px - 0.5, (y + 0.5) / px - 0.5
            kat = math.atan2(v, u)
            r = math.hypot(u / rx, v / ry) / (1 + 0.12 * math.cos(guzki * (kat - obrot)))
            wiersz.append(0 if r > 1 else int(70 + 185 * (1 - r) ** 0.6))
        wiersze.append(bytes(wiersz))

    def kawalek(typ: bytes, dane: bytes) -> bytes:
        return struct.pack(">I", len(dane)) + typ + dane + struct.pack(">I", zlib.crc32(typ + dane) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n" + kawalek(b"IHDR", struct.pack(">IIBBBBB", px, px, 8, 0, 0, 0, 0))
            + kawalek(b"IDAT", zlib.compress(b"".join(wiersze), 9)) + kawalek(b"IEND", b""))


# fikcyjne zlecenia puli porannej: (kuweta, liczba punktow); projekty numerowane kolejno od 301 (``projekt_sztuczny``)
ZLECENIA_RANO = tuple((str(3200 + 7 * i), (3, 1, 2, 4, 2, 1, 3, 2)[i % 8]) for i in range(36)) + (("#1234", 2), ("#1301", 1))
PIERWSZY_PROJEKT_RANO = 301


def projekty_zlecen_rano() -> dict:
    """Kuweta -> numery sztucznych projektow tego zlecenia (``ZLECENIA_RANO``)."""
    wynik, nr = {}, PIERWSZY_PROJEKT_RANO
    for kuweta, ile in ZLECENIA_RANO:
        wynik[kuweta] = tuple(range(nr, nr + ile))
        nr += ile
    return wynik


def indeks_rano_sztuczny(baza: B.Baza, czas: str, miniatury: bool = True) -> dict:
    """Fikcyjna pula poranna (``ZLECENIA_RANO``: 38 zlecen po 1-4 punkty, kuwety 3200-3445, "#1234", "#1301") w indeksie bazy
    wraz z miniaturami w ``cechy_stl``, jesli jej jeszcze nie ma. Zwraca kuweta -> numery projektow. Tylko dane sztuczne."""
    zlecenia = projekty_zlecen_rano()
    if baza.wiersz("SELECT id FROM projekty WHERE sha16 = ?", (projekt_sztuczny(PIERWSZY_PROJEKT_RANO),)) is not None:
        return zlecenia
    with baza.transakcja():
        for kuweta, numery in zlecenia.items():
            zrodlo = "prywatne" if kuweta.startswith("#") else "cyrkon"
            z = baza.wstaw("zlecenia", zrodlo=zrodlo, folder=f"{kuweta} Fikcja Rano", folder_norm=f"{kuweta} fikcja rano", kuweta=kuweta, dodano=czas,
                           usuniety=0)
            for nr in numery:
                baza.wstaw("projekty", zlecenie_id=z, plik=f"rano-{nr}-crown_cad.stl", sha16=projekt_sztuczny(nr), zeby=zab_sztuczny(nr), typ="korona",
                           usuniety=0)
                if miniatury:
                    baza.wykonaj("INSERT OR REPLACE INTO cechy_stl (sha16, miniatura, wersja_cech, policzono) VALUES (?, ?, ?, ?)",
                                 (projekt_sztuczny(nr), miniatura_sztuczna(nr), 0, czas))
    return zlecenia


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
                 ust: dict | None = None, liczba_stl: int = 16, tryb: str | None = None):
        self._wlasny_katalog = katalog is None
        self.katalog = Path(tempfile.mkdtemp(prefix="qc_atrapa_")) if katalog is None else Path(katalog)
        self.katalog.mkdir(parents=True, exist_ok=True)
        baza = B.otworz(self.katalog / "atrapa.sqlite", zegar=zegar)
        sesja = SE.Sesja(baza, operatorzy=operatorzy, katalog_wynikow=self.katalog / "wyniki", zegar=zegar, wersja_programu="atrapa")
        super().__init__(sesja, ust, zegar=zegar, tryb=tryb)
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
        self.sesja.baza.zdarzenie("ui", "start_skanu", {"udany": udany, "tryb": self.tryb}, czas=self.starty_skanu[-1])  # tryb: prosba A10
        if not udany:
            return self._odmowa("start_skanu_nieudany")
        self._ramka_w_spacja()  # E3-A12: ramka wieczorna w stan "skanowanie"
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
        self._zamknij_ramki_excel()  # E3-A12: ramki zgaszone, klienci zatrzymani, Excel rozlaczony
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
        znacznik = self._ramka_w_nowy_skan()  # E3-A12: ramka W - skan bez Spacji = nowy skan; start analizy
        self._ramka_w_analiza(znacznik)
        if rodzaj == "blad":
            if self.tryb == TRYB_RANO:  # jak prawdziwy kontroler: skan poranny do sesji pieca (A6)
                skan_id = self.rano.przyjmij_blad(zdarzenie, "analiza: blad sztuczny")
            else:
                skan_id = self.sesja.przyjmij_blad(zdarzenie, "analiza: blad sztuczny", self.tryb)
            self._ramka_w_blad(znacznik)
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
        wlasciwa, obca = ("poranna", "wieczorna") if self.tryb == TRYB_RANO else ("wieczorna", "poranna")
        uklad = uklad or (obca if rodzaj == "nie_z_trybu" else wlasciwa)
        wynik = sztuczny_wynik(uklad, None if rodzaj == "bez_numeru" else numer, gniazda if gniazda is not None else domyslne,
                               uklad_zgodny=rodzaj != "niezgodny_uklad", poza_gniazdem=poza_gniazdem, skan=nazwa, projekty=projekty)
        return self._przyjmij_sztuczny(zdarzenie, wynik, znacznik)

    def _przyjmij_sztuczny(self, zdarzenie: dict, wynik: dict, znacznik=None) -> int:
        """Wynik sztuczny do sesji trybu kontrolera (rano: ``SesjaRano`` - piec otwiera sie sam, jak w ``Aplikacja``); ``znacznik`` -
        skanu wieczornego na ramce W (kolory mapy ida do ramki po zbudowaniu stanu)."""
        if self.tryb == TRYB_RANO:
            skan_id = self.rano.przyjmij_wynik(zdarzenie, wynik)
        else:
            skan_id = self.sesja.przyjmij_wynik(zdarzenie, wynik, self.tryb)
        self._ramka_w_wynik(znacznik, skan_id)
        self._po_skanie(self.tryb)
        self._zapisz_podglad(skan_id, self._sztuczny_podglad(zdarzenie["sha16"], wynik))
        self._odswiez()
        return skan_id

    def symuluj_skan_rano(self, numer: int | None = 4, gniazda: dict | None = None, *, projekty: dict | None = None, uklad: str = "poranna",
                          poza_gniazdem: int = 0) -> int:
        """Skan plytki porannej z kandydatami (``sztuczny_wynik_rano``: rodzaje ``RODZAJE_PRAC_RANO``) - do sesji trybu kontrolera
        (w trybie "rano" - piec). Pula poranna: ``indeks_rano_sztuczny`` (wola ja ta metoda). Zwraca ``skan_id``."""
        indeks_rano_sztuczny(self.sesja.baza, self._teraz())
        self._nr_skanu += 1
        nazwa = f"atrapa_rano_{self._nr_skanu:03d}.stl"
        zdarzenie = {"plik": f"atrapa/{nazwa}", "sha16": skrot_sztuczny(f"skan sztuczny {self._nr_skanu} {time.time_ns()}"),
                     "rozmiar": 48_000_000 + self._nr_skanu, "czas_pliku": self._teraz()}
        self._analiza, self._czeka_na_skan = None, False
        wynik = sztuczny_wynik_rano(uklad, numer, gniazda, projekty=projekty, poza_gniazdem=poza_gniazdem, skan=nazwa)
        return self._przyjmij_sztuczny(zdarzenie, wynik)

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

    def scenariusz_poranny(self) -> dict:
        """Gotowy poranek do pokazu okna (E3-A7): tryb "rano", wybrana osoba, pula poranna (``indeks_rano_sztuczny``); piec 1 -
        plytka 4 z kompletem zlecen 3200 i 3207, zamkniety; piec 2 otwarty - plytki 4, 5, 6 po 23 prace (``plan_scenariusza_rano``:
        dwuznaczne, nieznane, konflikt, zab dofrezowany do zlecenia 3200, braki). Zwraca {"piec1" / 4 / 5 / 6: skan_id}."""
        self.przelacz_tryb(TRYB_RANO)
        if self.sesja.operator is None:
            self.wybierz_operatora(self.sesja.operatorzy[0])
        indeks_rano_sztuczny(self.sesja.baza, self._teraz())
        skany = {"piec1": self.symuluj_skan_rano(4, {1: "pewna", 2: "pewna", 3: "pewna", 5: "pewna"}, projekty={1: 301, 2: 302, 3: 303, 5: 304})}
        self.zamknij_piec()
        self.zamknij_komunikat(ID_EXCEL)
        for numer, (gniazda, projekty) in plan_scenariusza_rano().items():
            skany[numer] = self.symuluj_skan_rano(numer, gniazda, projekty=projekty)
        return skany


def plan_scenariusza_rano() -> dict:
    """Piec 2 scenariusza porannego: numer plytki -> (gniazda: rodzaj, projekty). Plytki 4, 5, 6 po 23 prace (gniazdo 24 puste)
    z kolejnych projektow puli porannej 305-385 (bez 310, 328, 346 - punkty, ktore nie wyszly z pieca: braki); dwuznaczne:
    plytka 4 gniazdo 9 (zolta) i plytka 5 gniazdo 14; nieznane: plytka 6 gniazdo 20 (slaby kandydat) i plytka 5 gniazdo 22
    (bez kandydatow); konflikt: plytka 5 gniazdo 3 i plytka 6 gniazdo 11 (ten sam projekt); zab dofrezowany (poprawka): plytka 6
    gniazdo 2 = projekt 301 zlecenia 3200 zamknietego w piecu 1. Drugi kandydat prac dwuznacznych lezy na innej plytce (wybor
    zlego = konflikt)."""
    kolejne = iter(n for n in range(305, 386) if n not in (310, 328, 346))
    plan = {}
    for numer in (4, 5, 6):
        gniazda, projekty = {}, {}
        for nr in range(1, 24):
            gniazda[nr], projekty[nr] = "pewna", next(kolejne)
        plan[numer] = (gniazda, projekty)
    (g4, p4), (g5, p5), (g6, p6) = plan[4], plan[5], plan[6]
    g4[9], p4[9] = "zolta", (p4[9], p6[5])
    g5[14], p5[14] = "dwuznaczna", (p5[14], p4[16])
    g6[20] = "nieznana"
    g5[22] = "brak"
    p6[11] = p5[3]
    p6[2] = 301
    return plan
