"""kontroler_api - KONTRAKT miedzy kontrolerem aplikacji "Stanowisko" a oknem (paczka E3-A3a; ekran buduje A3b).

Kontroler spina ``scanner`` -> ``silnik`` -> ``session`` / ``baza`` i wystawia oknu trzy rzeczy:

1. STAN - ``kontroler.stan() -> StanAplikacji``: niezmienny obraz calego ekranu wieczornego (zwykle dane, bez Qt):
   plytki doby z mapa gniazd (``Plytka`` -> ``Gniazdo`` -> ``Praca``: klasa koloru, status, podpis, kolor ekranu), lista
   "do dofrezowania", pytania do technika (``Pytanie``: ponowny skan z liczba decyzji, ktore przestana obowiazywac; plytka
   nie z trybu; brak numeru plytki), komunikaty (``Komunikat``: skan do powtorzenia, plytka niezgodna z ukladem, plik
   zajety - "czeka na zwolnienie", ``plik_niedostepny`` / ``plik_zmieniony``, blad inspekcji gniazda, odmowy), postep
   analizy, kolejka, pula projektow (liczba STL), skaner, operator, doba i zmiana.
2. POLECENIA - metody kontrolera wolane przez okno (lista: ``POLECENIA``); kazda zwraca ``Odpowiedz`` (``ok`` + tekst dla
   technika) i NIGDY nie rzuca wyjatku z powodu zlego stanu (brak operatora, skan nieprzyjety) - odmowa jest odpowiedzia
   i komunikatem w stanie. ``kontroler.wykonaj(nazwa, *argumenty)`` wola polecenie po nazwie (przyciski z ``Pytanie``).
3. SYGNALY - ``kontroler.subskrybuj(funkcja)``: funkcja dostaje ``ZdarzenieKontrolera`` (``stan`` / ``postep`` /
   ``komunikat`` / ``pytanie`` / ``zamkniety``). W oknie Qt: ``lacznik_qt(kontroler)`` - obiekt z sygnalami Qt
   ``stan_zmieniony(object)``, ``postep(object)``, ``komunikat(object)``, ``pytanie(object)``, ``zamkniety()`` i zegarem,
   ktory co 30 ms wola ``kontroler.przetworz()``.

WATEK. Kontroler zyje w watku okna: wszystkie polecenia, ``stan()`` i ``przetworz()`` wola sie z jednego watku (polaczenie
z baza jest do niego przywiazane). Zdarzenia z watkow ``scanner`` i ``silnik`` czekaja w kolejkach; ``przetworz()`` je
oproznia (najwyzej ``limit_s`` na wywolanie), zapisuje w sesji i powiadamia subskrybentow - dlatego okno musi je wolac
regularnie (``lacznik_qt`` robi to zegarem), a test bez okna wola je sam.

CZEGO OKNU NIE WOLNO: siegac do ``session`` / ``baza`` / ``scanner`` / ``silnik`` z pominieciem kontrolera, trzymac wlasnych
kolorow i napisow statusow (tylko ``statusy``), pokazywac sciezek i nazw plikow (stan ich nie zawiera - poza folderem puli
i folderem skanera, ktore sa ustawieniami), zmieniac obiektow stanu (sa zamrozone), wolac kontrolera z innego watku.

Plik zawiera tez ``KontrolerSesji`` (wspolna czesc prawdziwego kontrolera i atrapy: stan z ``session``, polecenia
o decyzjach) oraz ``AtrapaKontrolera`` - kontroler na danych sztucznych, bez skanera i silnika, do budowy i testow okna.
Modul uzywa tylko biblioteki standardowej; PySide6 jest importowane dopiero w ``lacznik_qt``.
"""
from __future__ import annotations

import dataclasses
import datetime as dt
import hashlib
import json
import logging
import shutil
import tempfile
import time
import warnings
from pathlib import Path
from typing import Any, Callable

from . import baza as B
from . import session as SE
from . import statusy as ST

LOG = logging.getLogger(__name__)

WERSJA_KONTRAKTU = 1
TRYB_WIECZOR = SE.TRYB_WIECZOR
LIMIT_PRZETWARZANIA_S = 0.05  # najdluzej tyle trwa jedno ``przetworz()``, gdy czeka wiele zdarzen (petla okna: przerwy < 200 ms)
OKRES_LACZNIKA_MS = 30
PAMIEC_ODRZUCEN_DNI = 2  # z ilu dni wstecz czytane sa odrzucone propozycje ponownego skanu
NUMERY_PLYTEK_ZAPASOWE = tuple(range(1, 10))  # cyfry do wyboru, gdy ukladu plytki nie da sie wczytac

# polecenia okna do kontrolera (nazwy metod); ``Praca.dozwolone`` / ``Plytka.dozwolone`` podaja, ktore maja teraz sens
POLECENIA = ("wybierz_operatora", "ukruszona", "ok", "cofnij", "potwierdz_ponowny_skan", "odrzuc_ponowny_skan", "cofnij_zastapienie",
             "dopusc_plytke", "cofnij_dopuszczenie", "podaj_numer_plytki", "zamknij_pytanie", "zamknij_komunikat", "start_skanu",
             "ustaw_pule", "odswiez_pule", "zamknij")
# sygnaly kontrolera do okna (``ZdarzenieKontrolera.typ``; w ``lacznik_qt``: stan_zmieniony, postep, komunikat, pytanie, zamkniety)
SYGNALY = ("stan", "postep", "komunikat", "pytanie", "zamkniety")
RODZAJE_PYTAN = ("ponowny_skan", "plytka_nie_z_trybu", "brak_numeru_plytki")


# ----------------------------------------------------------------------------
# typy danych stanu (wszystkie zamrozone; pola opcjonalne maja wartosci domyslne)
# ----------------------------------------------------------------------------
@dataclasses.dataclass(frozen=True)
class Odpowiedz:
    """Odpowiedz kontrolera na polecenie okna. ``ok`` False = odmowa: ``tekst`` to powod i rada dla technika, ``kod`` -
    rodzaj odmowy (klucz ``statusy.KOMUNIKATY``, np. ``brak_operatora``). ``dane`` - wynik polecenia (np. id decyzji)."""

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
    ``trwaly`` True = wynika ze stanu skanu (wraca po restarcie, znika, gdy skan przestaje tego wymagac)."""

    id: str
    rodzaj: str
    poziom: str
    tytul: str
    tekst: str
    czas: str = ""
    skan_id: int | None = None
    gniazda: tuple = ()
    trwaly: bool = False


@dataclasses.dataclass(frozen=True)
class Pytanie:
    """Pytanie, na ktore technik odpowiada przyciskiem z ``odpowiedzi``. ``rodzaj``: ``RODZAJE_PYTAN``.
    Ponowny skan: ``liczba_decyzji`` / ``liczba_ukruszonych`` = ile decyzji poprzedniego skanu przestanie obowiazywac.
    Brak numeru plytki: ``numery`` = numery plytek tego ukladu (okno pokazuje cyfry; ``podaj_numer_plytki(skan_id, n)``)."""

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
    liczniki: dict = dataclasses.field(default_factory=dict)  # klasa koloru -> liczba prac
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
    projektow albo na silnik), ``razem``."""

    w_toku: int = 0
    czeka: int = 0
    wstrzymane: int = 0
    silnik_gotowy: bool = False

    @property
    def razem(self) -> int:
        return self.w_toku + self.czeka + self.wstrzymane


@dataclasses.dataclass(frozen=True)
class Pula:
    """Pula projektow na poziomie 1 planu: folder + wspolczynnik wpisany recznie (None = domyslny dla typu plytki).
    ``stan``: nieustawiona / liczenie / gotowa / pusta / brak_folderu; ``liczba_stl`` None = jeszcze nie policzono."""

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
class StanAplikacji:
    """Caly stan ekranu wieczornego. ``wersja`` rosnie przy kazdej zmianie. ``plytki`` - skany biezacej doby roboczej
    w kolejnosci przyjecia; ``biezaca_plytka`` - skan_id ostatniej plytki. ``komunikaty`` i ``pytania`` - wszystko, co
    wymaga uwagi technika teraz (takze przypiete do plytek)."""

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
    liczniki: dict = dataclasses.field(default_factory=dict)
    prac: int = 0
    do_dofrezowania: tuple = ()  # pozycje tej doby
    do_dofrezowania_biezaca: tuple = ()  # wszystkie otwarte, takze z poprzednich dob
    pytania: tuple = ()
    komunikaty: tuple = ()
    konflikty: tuple = ()
    analiza: Postep | None = None
    kolejka: Kolejka = Kolejka()
    pula: Pula = Pula()
    skaner: Skaner = Skaner()
    zamkniety: bool = False

    def plytka(self, skan_id: int) -> Plytka | None:
        return next((p for p in self.plytki if p.skan_id == skan_id), None)

    def praca(self, praca_id: int) -> Praca | None:
        return next((x for p in self.plytki for x in p.prace if x.praca_id == praca_id), None)


@dataclasses.dataclass(frozen=True)
class SzczegolyPracy:
    """Widok pracy po kliknieciu gniazda: ``ubytki`` (slowniki z pliku wyniku: x, y, z, srednica_mm, glebokosc_mm, metoda,
    kolor, na_krawedzi), ``uwagi`` programu, ``kandydaci`` (sha16, zeby, typ, pokrycie) oraz ``plik_podgladu`` - plik
    ``*_podglad.npz`` (``silnik.wczytaj_podglad``: gniazdo -> punkty i odchylki do obrazu odchylek) albo None."""

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

    def wykonaj(self, polecenie: str, *argumenty: Any) -> Odpowiedz:
        """Polecenie po nazwie (``POLECENIA``) - dla przyciskow z ``Pytanie.odpowiedzi``."""
        if polecenie not in POLECENIA:
            return Odpowiedz(False, f"nieznane polecenie {polecenie!r}", "odmowa")
        return getattr(self, polecenie)(*argumenty)


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
    * "Ukruszona" na pracy, ktorej program nie oznaczyl na czerwono, zapisuje sie jako ``ukruszona_niewykryta`` (SE9);
    * plytka bez numeru: prace zielone maja status ``czeka_na_numer`` (nic zielonego) do podania numeru;
    * odrzucenie propozycji ponownego skanu ("to nowy wsad") jest zapisywane w dzienniku i nie wraca po restarcie.
    """

    def __init__(self, sesja: SE.Sesja, ust: dict | None = None, *, tryb: str = TRYB_WIECZOR, zegar: Callable[[], dt.datetime] | None = None):
        self.sesja = sesja
        self.ust = ust
        self.tryb = SE.sprawdz_tryb(tryb)
        self._zegar = zegar or dt.datetime.now
        self._subskrybenci: list = []
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
        self._odrzucone = self._wczytaj_odrzucone()

    # --- sygnaly ---------------------------------------------------------------------------------
    def subskrybuj(self, funkcja: Callable[[ZdarzenieKontrolera], None]) -> None:
        if funkcja not in self._subskrybenci:
            self._subskrybenci.append(funkcja)

    def odsubskrybuj(self, funkcja: Callable[[ZdarzenieKontrolera], None]) -> None:
        if funkcja in self._subskrybenci:
            self._subskrybenci.remove(funkcja)

    def _powiadom(self, typ: str, **pola: Any) -> None:
        z = ZdarzenieKontrolera(typ=typ, **pola)
        for f in list(self._subskrybenci):
            try:
                f(z)
            except Exception:  # noqa: BLE001 - blad okna nie moze zatrzymac kontrolera
                LOG.exception("kontroler: blad odbiorcy sygnalu %s", typ)

    # --- stan ------------------------------------------------------------------------------------
    def stan(self) -> StanAplikacji:
        if self._stan is None:
            self._stan = self._zbuduj()
        return self._stan

    def _odswiez(self) -> StanAplikacji:
        """Stan od nowa z bazy + sygnaly: ``stan``, potem ``komunikat`` / ``pytanie`` dla kazdej nowej pozycji."""
        if self._zamkniety:
            return self.stan()
        self._stan = stan = self._zbuduj()
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
                from . import uklad as U  # numpy: ladowane dopiero przy pierwszej plytce

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
        po_projekcie = {x["projekt_id"]: x for x in biezaca if x["projekt_id"] is not None}
        po_pracy = {x["praca_id"]: x for x in biezaca}
        propozycje = {p["skan_id"]: p for p in sw["do_potwierdzenia"]}
        czasy = {s["id"]: s["czas_analizy"] for s in sw["skany"]}
        plytki, pytania, trwale = [], [], []
        for s in sw["skany"]:
            plytka = self._plytka(s, po_projekcie, po_pracy, propozycje.get(s["id"]), czasy)
            plytki.append(plytka)
            pytania += [p for p in plytka.pytania if p.id not in self._ukryte]
            trwale += [k for k in plytka.komunikaty if k.id not in self._ukryte]
        if sw["konflikty"]:
            for k in sw["konflikty"]:
                id_ = f"konflikt_projektu:{k['sha16']}"
                if id_ not in self._ukryte:
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
            plytki=tuple(plytki), biezaca_plytka=aktywne[-1] if aktywne else None, liczniki=liczniki, prac=sw["prac"],
            do_dofrezowania=tuple(self._pozycja(x) for x in sw["do_dofrezowania"]),
            do_dofrezowania_biezaca=tuple(self._pozycja(x) for x in biezaca),
            pytania=tuple(pytania), komunikaty=tuple(komunikaty), konflikty=tuple(sw["konflikty"]), zamkniety=self._zamkniety,
            **self._stan_zywy())

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
                                decyzja=p["decyzja"], blad_inspekcji=blad, numer_znany=numer_znany)
        st = ST.status(klucz)
        kolor = p["kolor"] if klucz != "czeka_na_numer" else None  # plytka bez numeru: nic zielonego
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
        komunikaty = self._komunikaty_plytki(s, prace)
        pytania = self._pytania_plytki(s, propozycja, czasy, typ, numery_plytek)
        return Plytka(
            skan_id=s["id"], status=s["status"], aktywna=s["aktywny"], napis=ST.napis_plytki(s["status"]), numer=s["numer_plytki"],
            numer_zrodlo=s["numer_zrodlo"], uklad=s["uklad"], typ=typ, czas=s["czas_analizy"], zmiana=s["zmiana"], czas_s=s["czas_s"],
            sha16=s["sha16"], gniazda=tuple(gniazda), poza_gniazdem=tuple(poza), liczniki=liczniki,
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
            wynik.append(self._nowy_komunikat(f"blad_analizy:{skan_id}", "blad_analizy", trwaly=True, czas=czas, skan_id=skan_id,
                                              powod=self._powod_bledu(skan_id)))
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

    def _powod_bledu(self, skan_id: int) -> str:
        """Powod bledu analizy z dziennika (rodzaj bledu silnika zapisany przez kontroler) jako tekst dla technika."""
        w = self.sesja.baza.wiersz("SELECT dane FROM zdarzenia WHERE skan_id = ? AND typ = 'blad_analizy_rodzaj' ORDER BY id DESC LIMIT 1", (skan_id,))
        rodzaj = None
        if w and w["dane"]:
            try:
                rodzaj = json.loads(w["dane"]).get("rodzaj")
            except ValueError:
                rodzaj = None
        return ST.POWODY_BLEDU_ANALIZY.get(rodzaj, ST.POWODY_BLEDU_ANALIZY["analiza"])

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
        self._komunikaty[id_] = k
        self._ogloszone.discard(id_)
        self._ukryte.discard(id_)
        return k

    def _usun_komunikat(self, id_: str) -> bool:
        return self._komunikaty.pop(id_, None) is not None

    def _odmowa(self, kod: str, **pola: Any) -> Odpowiedz:
        """Odmowa wykonania polecenia: komunikat w stanie (jeden na rodzaj odmowy) + odpowiedz z tym samym tekstem."""
        k = self._komunikat(kod if kod in ST.KOMUNIKATY else "odmowa", id_=f"odmowa:{kod}", **pola)
        self._odswiez()
        return Odpowiedz(False, k.tekst, kod)

    def _bez_operatora(self) -> Odpowiedz | None:
        self._sprawdz_zmiane()
        if not self.sesja.operatorzy:
            return self._odmowa("pusta_lista_operatorow")
        if self.sesja.operator is None:
            return self._odmowa("brak_operatora")
        return None

    def _polecenie(self, funkcja: Callable[[], Any], *, operator: bool = True) -> Odpowiedz:
        """Wspolna obsluga polecenia: zamkniety program, brak operatora, odmowa ``session``, baza zajeta; potem nowy stan."""
        if self._zamkniety:
            return Odpowiedz(False, ST.tekst_komunikatu("program_zamkniety")[2], "program_zamkniety")
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
        for kod in ("brak_operatora", "pusta_lista_operatorow", "odmowa", "baza_zajeta", "osoba_spoza_listy"):
            self._usun_komunikat(f"odmowa:{kod}")  # polecenie przeszlo: stare odmowy nieaktualne
        self._odswiez()
        return Odpowiedz(True, dane=dane)

    # --- polecenia -------------------------------------------------------------------------------
    def wybierz_operatora(self, nazwa: str) -> Odpowiedz:
        if self._zamkniety:
            return Odpowiedz(False, ST.tekst_komunikatu("program_zamkniety")[2], "program_zamkniety")
        if not self.sesja.operatorzy:
            return self._odmowa("pusta_lista_operatorow")
        try:
            self.sesja.wybierz_operatora(nazwa)
        except SE.BladSesji:
            return self._odmowa("osoba_spoza_listy")
        self._zmiana_operatora = (self.sesja.doba(), self.sesja.zmiana())
        for kod in ("brak_operatora", "osoba_spoza_listy"):
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

        return self._polecenie(wykonaj)

    def ok(self, praca_id: int) -> Odpowiedz:
        return self._polecenie(lambda: self.sesja.ok(praca_id))

    def cofnij(self, praca_id: int) -> Odpowiedz:
        return self._polecenie(lambda: self.sesja.cofnij(praca_id))

    def potwierdz_ponowny_skan(self, skan_id: int) -> Odpowiedz:
        return self._polecenie(lambda: self.sesja.zastap_skan(skan_id))

    def odrzuc_ponowny_skan(self, skan_id: int) -> Odpowiedz:
        def wykonaj() -> int:
            plytka = self.stan().plytka(skan_id)
            if plytka is None or plytka.moze_zastapic is None:
                raise SE.BladSesji(f"skan {skan_id}: nie ma propozycji ponownego skanu do odrzucenia")
            self.sesja.baza.zdarzenie("ui", "ponowny_skan_odrzucony", {"poprzedni_id": plytka.moze_zastapic, "operator": self.sesja.operator},
                                      skan_id=skan_id, czas=self._teraz())
            self._odrzucone.add((skan_id, plytka.moze_zastapic))
            return plytka.moze_zastapic

        return self._polecenie(wykonaj)

    def cofnij_zastapienie(self, skan_id: int) -> Odpowiedz:
        return self._polecenie(lambda: self.sesja.cofnij_zastapienie(skan_id))

    def dopusc_plytke(self, skan_id: int) -> Odpowiedz:
        return self._polecenie(lambda: self.sesja.dopusc_plytke(skan_id))

    def cofnij_dopuszczenie(self, skan_id: int) -> Odpowiedz:
        return self._polecenie(lambda: self.sesja.cofnij_dopuszczenie(skan_id))

    def podaj_numer_plytki(self, skan_id: int, numer: int) -> Odpowiedz:
        return self._polecenie(lambda: self.sesja.podaj_numer_plytki(skan_id, numer))

    def zamknij_pytanie(self, pytanie_id: str) -> Odpowiedz:
        """"Pozniej": pytanie znika z listy do konca pracy programu (wraca po restarcie); niczego nie rozstrzyga."""
        self._ukryte.add(str(pytanie_id))
        self._odswiez()
        return Odpowiedz(True)

    def zamknij_komunikat(self, komunikat_id: str) -> Odpowiedz:
        if not self._usun_komunikat(str(komunikat_id)):
            self._ukryte.add(str(komunikat_id))  # trwaly: ukryty do konca pracy programu, zostaje przy plytce
        self._odswiez()
        return Odpowiedz(True)

    def szczegoly_pracy(self, praca_id: int) -> SzczegolyPracy | None:
        praca = self.stan().praca(praca_id)
        if praca is None:
            return None
        wpis = self._inspekcje(praca.skan_id).get((praca.gniazdo, praca.nr_fragmentu)) or {}
        inspekcja = wpis.get("inspekcja") or {}
        ubytki = tuple({k: u.get(k) for k in ("x", "y", "z", "srednica_mm", "glebokosc_mm", "metoda", "kolor", "na_krawedzi", "filar")}
                       for u in inspekcja.get("ubytki") or [])
        uwagi = tuple(str(u) for u in (wpis.get("uwagi") or []) + (inspekcja.get("uwagi") or []))
        kandydaci = tuple({"sha16": k.get("id"), "zeby": k.get("zeby"), "typ": k.get("typ"), "pokrycie": k.get("pokrycie")}
                          for k in wpis.get("kandydaci") or [])
        return SzczegolyPracy(praca=praca, ubytki=ubytki, uwagi=uwagi, kandydaci=kandydaci, plik_podgladu=self._plik_podgladu(praca.skan_id))

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
    plytka bez numeru (``numer_znany`` False) nie ma zielonych (zielony -> brak koloru, status ``czeka_na_numer``).
    """
    decyzje = decyzje or {}
    wynik_kolory, licznik = {}, {}
    for g in wynik.get("gniazda") or []:
        licznik[g.get("gniazdo")] = licznik.get(g.get("gniazdo"), 0) + 1
        klucz = (g.get("gniazdo"), licznik[g.get("gniazdo")])
        kolor = g.get("status_gniazda")
        if status_skanu not in SE.STATUSY_AKTYWNE:
            kolor = None
        elif decyzje.get(klucz) in ST.DECYZJE_UKRUSZENIA:
            kolor = ST.KOLOR_CZERWONY
        elif decyzje.get(klucz) == "ok":
            kolor = ST.KOLOR_ZATWIERDZONA_OK
        elif status_skanu == SE.STATUS_DO_POWTORZENIA and kolor == ST.KOLOR_ZIELONY:
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
        self._pula = Pula(folder="(atrapa)", wspolczynnik=None, liczba_stl=liczba_stl, stan="gotowa",
                          napis=ST.STANY_PULI["gotowa"].format(n=liczba_stl), odswiezono=self._teraz())
        self._liczba_stl = liczba_stl
        indeks_sztuczny(baza, self._teraz())

    # --- czesc zywa
    def _stan_zywy(self) -> dict:
        return {"analiza": self._analiza, "kolejka": Kolejka(w_toku=1 if self._analiza else 0, czeka=self._czeka, silnik_gotowy=True),
                "pula": self._pula,
                "skaner": Skaner(folder="(atrapa)", dostepny=True, dziala=not self._zamkniety, startow_skanu=len(self.starty_skanu),
                                 ostatni_start_skanu=self.starty_skanu[-1] if self.starty_skanu else None,
                                 czeka_na_skan=self._czeka_na_skan)}

    def _katalog_podgladow(self) -> Path | None:
        return self.katalog / "podglady"

    # --- polecenia zywe
    def start_skanu(self) -> Odpowiedz:
        if self._zamkniety:
            return Odpowiedz(False, ST.tekst_komunikatu("program_zamkniety")[2], "program_zamkniety")
        self.starty_skanu.append(self._teraz())
        self._czeka_na_skan = True
        self._odswiez_zywe()
        return Odpowiedz(True)

    def ustaw_pule(self, folder: str | None, wspolczynnik: float | None = None) -> Odpowiedz:
        self._pula = dataclasses.replace(self._pula, folder=folder, wspolczynnik=wspolczynnik)
        return self.odswiez_pule()

    def odswiez_pule(self) -> Odpowiedz:
        self._pula = dataclasses.replace(self._pula, liczba_stl=self._liczba_stl, stan="gotowa" if self._liczba_stl else "pusta",
                                         napis=ST.STANY_PULI["gotowa" if self._liczba_stl else "pusta"].format(n=self._liczba_stl),
                                         odswiezono=self._teraz())
        self._odswiez_zywe()
        return Odpowiedz(True, dane=self._liczba_stl)

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
        pola = {"od_s": 12, "proba": 1, "prob": 3, "powod": ST.POWODY_BLEDU_ANALIZY["analiza"], "czeka": 1, "ile": 1, **pola}
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
