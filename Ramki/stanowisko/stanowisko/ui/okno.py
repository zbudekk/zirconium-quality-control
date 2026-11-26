"""okno - okno programu "Stanowisko" zbudowane od nowa (paczka E3-U1a; ``etap3/nowy_interfejs/SPEC.md``, makieta ``Main.dc.html``):
wspolny szkielet obu trybow i caly tryb "Wieczor". Okno pokazuje ``kontroler.stan()`` i wysyla polecenia kontrolera.

Szkielet (SPEC p. 3):
1. pasek gorny (``czesci.PasekGorny``): nazwa programu, przelacznik Wieczor / Poranek, doba i zmiana, "program czeka na plik
   skanu [Spacja]", osoba z przyciskiem zmiany; lista osob (``czesci.PanelOsoby``) rozwija sie pod paskiem - nakladka okna;
2. lewa kolumna (``wieczor.ListaPlytek``): plytki tej zmiany, nowy wynik na gorze, wczesniejsze zmiany na zadanie;
3. srodek: strefa pytan i komunikatow o STALEJ wysokosci (``czesci.StrefaKomunikatow`` - jedna pozycja naraz, reszta w liczniku
   "i jeszcze n"), naglowek plytki, mapa (``mapa.MapaPlytki``) z panelem obok (``wieczor.PanelBoczny``: legenda, prace poza
   gniazdami, polecenia plytki), na dole lista "Do dofrezowania" (``wieczor.ListaDofrezowania``) o stalej wysokosci;
4. prawa kolumna "Praca" (``wieczor.WidokPracy``) z decyzjami na stalym miejscu na dole;
5. pasek stanu (``czesci.PasekStanu``): skaner, analiza i kolejka, projekty, ramki, licznik bledow programu (rozwija liste
   ``czesci.ListaBledow`` nad paskiem), wersja programu.
Tryb "Poranek" do etapu U1b to dotychczasowy ``ekran_rano.EkranRano`` osadzony w tym szkielecie jako druga strona srodka.

Zasady (kontrakt ``kontroler_api`` / ``opisy_modulow/aplikacja.md``):
* okno NICZEGO nie liczy i nie siega do ``session`` / ``baza`` / ``scanner``; kolory i napisy statusow bierze ze stanu
  i ze ``statusy``; na ekranie nie ma sciezek ani nazw plikow (folder puli i skanera nie sa pokazywane);
* kazde polecenie idzie przez ``kontroler.wykonaj``; odmowa to ``Odpowiedz`` i komunikat w stanie - okno pokazuje go jak
  kazdy inny komunikat, nic nie rzuca; zadnych okien modalnych; stan o nizszej ``wersja`` niz pokazany jest pomijany;
* MAPA NIGDY SIE NIE PRZESUWA przy zmianie stanu: strefa pytan, naglowek plytki i lista "Do dofrezowania" maja stale
  wysokosci, kolumny - stale szerokosci, a lista osob i lista bledow sa nakladkami (nie zabieraja miejsca ukladowi);
* nowa plytka (A-P2, S3-3): ekran przelacza sie sam TYLKO, gdy na pokazanej plytce nie ma pracy do obejrzenia, otwartego
  pytania ani brakujacego numeru, a technik nie ma otwartej pracy ani wyboru numeru; inaczej kafelek dostaje "NOWA", nad
  lista plytek pojawia sie "Pokaz nowy wynik", a linia paska gornego na chwile blyska;
* ochrona 800 ms (``OCHRONA_MS``): po kazdej zmianie zawartosci mapy (inna plytka, nowy stan spoza polecen technika, powrot
  z trybu "Poranek" - S3-15) klikniecia mapy, Enter, N i skroty decyzji sa pomijane, a mapa jest przygaszona; to samo dla
  strefy pytan (S3-3) i listy bledow, gdy ich zawartosc zmienila sie w tle - klikniecie wycelowane w poprzednie pytanie nie
  trafia w nowe. Decyzja idzie zawsze do pracy, ktorej dane pokazuje widok pracy; gdy tej pracy nie ma juz w stanie albo
  gniazdo pokazuje inna prace - widok sie zamyka z informacja;
* S3-14: gdy wynik nowego skanu nie jest jeszcze gotowy (analiza, kolejka), mapa na ekranie jest oznaczona "POPRZEDNIA PLYTKA";
* wszystko dzieje sie w watku okna poza obrazem odchylek (``obraz.WczytywaczObrazow``); odswiezenie po sygnale stanu
  przebudowuje tylko te czesci ekranu, ktorych dane sie zmienily;
* klawiatura nalezy do okna: Spacja = "start skanu" (raz na nacisniecie), U / O / C = decyzje przy otwartej pracy,
  N = nastepna praca do obejrzenia, Esc = zamknij liste osob / kursor / widok pracy, strzalki = kursor gniazda na mapie,
  Enter = otworz gniazdo pod kursorem; Tab przechodzi po przyciskach i kafelkach (Enter klika element z fokusem, Spacja - nigdy);
* uklad (``motyw.uklad_dla``): okno wezsze niz 1500 albo nizsze niz 860 punktow - zwarty (kolumny 240 / 320, odstepy 12);
  najmniejsze okno ``motyw.MINIMUM_OKNA``; okno startuje zmaksymalizowane (``okno_zmaksymalizowane``).

Wlasny stan okna to tylko wybor technika: pokazana plytka, wybrane gniazdo, kursor klawiatury, zakres listy, otwarta lista
osob albo bledow, wybor numeru plytki, przegladana pozycja strefy oraz tekst ostatniej odmowy / informacji ekranu.
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QPoint, QRect, Qt, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QPushButton, QStackedLayout, QVBoxLayout, QWidget

from .. import kontroler_api as K
from .. import statusy as ST
from . import czesci as C
from . import motyw
from . import napisy as N
from . import styl
from .czesci import (LOKALNE_NUMER_BEZ_ZMIAN, LOKALNE_POKAZ_NOWA, LOKALNE_ZAMKNIJ_INFORMACJE, LOKALNE_ZAMKNIJ_ODPOWIEDZ, do_obejrzenia, dzien,
                     etykieta, godzina, nazwa_plytki, sprawy_nowych_plytek, stan_obejrzenia)
from .ekran_rano import EkranRano
from .mapa import MapaPlytki, geometria_ukladu
from .obraz import WczytywaczObrazow
from .wieczor import POLECENIA_PLYTKI, KafelekPlytki, ListaDofrezowania, ListaPlytek, PanelBoczny, PoleMapy, WidokPracy

SPRAWY_OSOBY = ("brak_operatora", "nowa_zmiana", "pusta_lista_operatorow", "osoba_spoza_listy")  # komunikaty pokazywane w liscie osob
OCHRONA_MS = 800  # tyle po zmianie zawartosci mapy / strefy pytan klikniecia i skroty decyzji sa pomijane (A-P2, S3-3, S3-15)
KONFLIKTOW_W_PANELU = 2  # tyle konfliktow projektu wypisanych z gniazdami w jednym komunikacie (reszta: "...")
PLIK_WERSJI = "WERSJA"  # plik z numerem wydania w katalogu programu (kontrakt okna numeru wydania nie podaje)
PYTANE = {"brak_numeru_plytki": "podaj_numer_plytki", "plytka_nie_z_trybu": "dopusc_plytke"}  # polecenie plytki, o ktore pyta pytanie
RANGA_POZIOMU = {ST.POZIOM_BLAD: 0, ST.POZIOM_OSTRZEZENIE: 1, ST.POZIOM_INFO: 2}  # kolejnosc komunikatow w strefie (nieznany poziom: jak ostrzezenie)


def otwarte(pozycje) -> list:
    """Pytania / komunikaty do pokazania: bez pozycji zamknietych przez technika (``ukryte=True``, kontrakt w wersji 2 - D6).
    ``stan.pytania`` i ``stan.komunikaty`` sa juz otwarte; filtr chroni ekran, gdyby pozycja ukryta jednak tam trafila."""
    return [x for x in pozycje if not x.ukryte]


def okno_zmaksymalizowane(platforma: str) -> bool:
    """Czy okno startuje zmaksymalizowane: ZAWSZE na prawdziwym ekranie, niezaleznie od jego wielkosci i skalowania (decyzja
    wlasciciela 18.11.2026, E3-A1p). Tryb bez ekranu (testy i zrzuty): nie - rozmiar ustawia wolajacy."""
    return platforma != "offscreen"


def blad_programu(komunikat) -> bool:
    """Komunikat na liste bledow programu (A-P3): poziom "blad" albo trwaly (nie dotyczacy pokazanej plytki)."""
    return komunikat.poziom == ST.POZIOM_BLAD or komunikat.trwaly


def grupuj(komunikaty) -> list:
    """Jednakowe komunikaty (ten sam rodzaj, poziom, tytul i tekst) jako jedna grupa - jedna pozycja z licznikiem."""
    grupy: dict = {}
    for k in komunikaty:
        grupy.setdefault((k.rodzaj, k.poziom, k.tytul, k.tekst), []).append(k)
    return list(grupy.values())


def wersja_programu() -> str:
    """Numer wydania z pliku ``WERSJA`` w katalogu programu (np. "0.3.4"); pusty napis, gdy pliku nie ma albo nie jest
    krotkim numerem. Na ekran idzie sam numer - nigdy nazwa ani polozenie pliku."""
    try:
        tekst = (Path(__file__).resolve().parents[2] / PLIK_WERSJI).read_text(encoding="ascii").strip()
    except (OSError, UnicodeError, IndexError):
        return ""
    return tekst if 0 < len(tekst) <= 20 and all(z.isalnum() or z in ".-" for z in tekst) else ""


class OknoStanowiska(QWidget):
    def __init__(self, kontroler, lacznik):
        super().__init__()
        self.k = kontroler
        self.lacznik = lacznik
        self.setObjectName("okno_stanowiska")
        self.setWindowTitle(N.TYTUL_OKNA)
        self._uklad = motyw.UKLAD_WYSOKI
        self.setFont(motyw.czcionka(motyw.PX_PODSTAWOWY))
        self.setStyleSheet(motyw.arkusz(self._uklad))
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        # wybor technika (jedyny wlasny stan okna)
        self._stan = None
        self._plytka_id: int | None = None
        self._gniazdo: int | None = None
        self._poza: int | None = None  # praca_id pracy poza gniazdem
        self._nr_pracy = 0
        self._praca_widoku: int | None = None  # praca, ktorej dane pokazuje widok pracy (do niej idzie decyzja)
        self._kursor: int | None = None  # kursor klawiatury na mapie (strzalki)
        self._lista_wszystkie = False
        self._zmiana_osoby = False
        self._pokaz_wczesniejsze = False
        self._numer_dla: int | None = None  # S3-3: skan_id plytki, dla ktorej technik otworzyl wybor numeru (zwiazany z TYM skanem)
        self._odmowa = ""  # tekst odmowy ostatniego polecenia, gdy kontroler nie dal go w komunikatach stanu
        self._informacja = ""  # informacja samego ekranu (np. widok pracy zamkniety, bo pracy nie ma w stanie)
        self._znane: set = set()
        self._nieobejrzane: set = set()  # plytki, ktore przyszly, a ekran sie na nie nie przelaczyl (znaczek "NOWA")
        self._blysk_nowej = False
        self._pierwszy_stan = True
        self._nr_komunikatow: dict = {}
        self._obraz_dla: int | None = None
        self._sygnatury: dict = {}
        self._mapa_podpis = None
        self._tab_podpis = None
        self._klucze_uwag: tuple = ()  # pozycje strefy pytan (po kluczach); zmiana zestawu = strefa wraca do pierwszej
        self._nr_uwagi = 0  # ktora pozycje strefy przeglada technik ("i jeszcze n")
        self._bledy_zwiniete = False  # lista bledow zwinieta przez technika (do nastepnego nowego bledu)
        self._bledy_znane: frozenset = frozenset()
        self._w_poleceniu = False  # stan przychodzacy w trakcie polecenia technika = skutek jego decyzji (bez ochrony mapy)
        self._z_tla = False  # trwa pokazywanie stanu, ktory przyszedl w tle (nie z polecenia technika): ochrona strefy i listy bledow
        self._wstrzymaj = False  # seria polecen (zamkniecie grupy komunikatow): jedno odswiezenie ekranu na koniec
        self._zamkniete = False
        self._ochrona = self._zegar_ochrony(self._koniec_ochrony)  # mapa
        self._ochrona_strefy = self._zegar_ochrony(lambda: self.strefa.chron(False))
        self._ochrona_bledow = self._zegar_ochrony(lambda: self.bledy.chron(False))
        self.wczytywacz = WczytywaczObrazow(self)
        self.wczytywacz.gotowy.connect(self._obraz_gotowy)
        self._zbuduj()
        self.setMinimumSize(*motyw.MINIMUM_OKNA)
        self.resize(1600, 900)
        self._ustaw_uklad(motyw.uklad_dla(1600, 900))
        self._dopasuj_do_ekranu()
        lacznik.stan_zmieniony.connect(self._na_stan)
        lacznik.postep.connect(self._na_postep)
        lacznik.zamkniety.connect(self._na_zamkniety)
        self.pokaz_stan(kontroler.stan())

    def _zegar_ochrony(self, po_czasie) -> QTimer:
        zegar = QTimer(self)
        zegar.setSingleShot(True)
        zegar.setInterval(OCHRONA_MS)
        zegar.timeout.connect(po_czasie)
        return zegar

    def _dopasuj_do_ekranu(self) -> None:
        """Okno startuje zmaksymalizowane (``okno_zmaksymalizowane``); na mniejszym ekranie (laptop 1920 x 1080 ze skalowaniem
        125-150 %) uklad przechodzi sam na zwarty (``resizeEvent``)."""
        if okno_zmaksymalizowane(QGuiApplication.platformName()):
            self.setWindowState(self.windowState() | Qt.WindowState.WindowMaximized)

    # --- budowa ----------------------------------------------------------------------------------
    def _zbuduj(self) -> None:
        self._korzen = korzen = QVBoxLayout(self)
        korzen.setContentsMargins(0, 0, 0, 0)
        korzen.setSpacing(0)
        self.pasek_gorny = C.PasekGorny()
        self.pasek_gorny.skanuj.connect(self._start_skanu)
        self.pasek_gorny.zmien_osobe.connect(self._przelacz_zmiane_osoby)
        self.pasek_gorny.przelacz_tryb.connect(lambda tryb: self._polecenie("przelacz_tryb", tryb))
        korzen.addWidget(self.pasek_gorny)
        # dwie strony miedzy paskami: tryb wieczorny i poranny (``ekran_rano``); pokazana wg ``stan.tryb``
        self._strony = QStackedLayout()
        korzen.addLayout(self._strony, 1)
        self.strona_wieczor = QWidget()
        self.strona_wieczor.setObjectName("strona_wieczor")
        self._strony.addWidget(self.strona_wieczor)
        self._calosc = calosc = QHBoxLayout(self.strona_wieczor)
        calosc.setContentsMargins(0, 0, 0, 0)
        calosc.setSpacing(0)

        self.lista_plytek = ListaPlytek()
        self.lista_plytek.wybrano.connect(lambda skan_id: QTimer.singleShot(0, lambda: self._pokaz_plytke(skan_id)))
        self.lista_plytek.przelacz_wczesniejsze.connect(lambda: QTimer.singleShot(0, self._przelacz_wczesniejsze))
        self.lista_plytek.ponow_zapis.connect(lambda: QTimer.singleShot(0, lambda: self._polecenie("ponow_zapis")))
        self.lista_plytek.pokaz_nowa.connect(self._pokaz_nowa)
        calosc.addWidget(self.lista_plytek)

        self.srodek = srodek = QWidget()
        srodek.setObjectName("srodek")
        self._srodek_uklad = su = QVBoxLayout(srodek)
        su.setContentsMargins(0, 0, 0, 0)
        su.setSpacing(0)
        # pytania i komunikaty: strefa o STALEJ wysokosci nad mapa - mapa nie przesuwa sie, gdy cos przychodzi albo znika
        self.strefa = C.StrefaKomunikatow()
        self.strefa.polecenie.connect(self._polecenie_panelu)
        self.strefa.nastepna.connect(self._nastepna_uwaga)
        su.addWidget(self.strefa)
        self.naglowek_pole = QWidget()
        self.naglowek_pole.setObjectName("naglowek_plytki")
        self._naglowek_uklad = QGridLayout(self.naglowek_pole)
        self.naglowek = etykieta("", "tytul", "mapa_naglowek")
        self.podnaglowek = C.EtykietaSkracana("tresc", "mapa_godzina")
        # S3-14: znak "POPRZEDNIA PLYTKA" w naglowku (stala wysokosc naglowka - jego pojawienie sie nie rusza mapy, nie zaslania gniazd)
        self.znak_poprzedniej = etykieta(N.MAPA_POPRZEDNIA, "znaczek_uwaga", "mapa_poprzednia")
        self.znak_poprzedniej.setVisible(False)
        # dwa wiersze: numer plytki i (po prawej) znak poprzedniej plytki; pod nimi opis skanu na cala szerokosc
        self._naglowek_uklad.addWidget(self.naglowek, 0, 0, Qt.AlignmentFlag.AlignBottom)
        self._naglowek_uklad.addWidget(self.znak_poprzedniej, 0, 1, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        self._naglowek_uklad.addWidget(self.podnaglowek, 1, 0, 1, 2)
        self._naglowek_uklad.setColumnStretch(0, 1)
        self._naglowek_uklad.setHorizontalSpacing(12)
        self._naglowek_uklad.setVerticalSpacing(0)
        su.addWidget(self.naglowek_pole)
        self.mapa = MapaPlytki()
        self.mapa.klik.connect(self._klik_gniazdo)
        self.boczny = PanelBoczny()
        self.boczny.poza.connect(self._klik_poza)
        self.boczny.numer.connect(self._przelacz_numer)
        self.boczny.polecenie.connect(lambda nazwa, argumenty: self._polecenie(nazwa, *argumenty))
        self.legenda = self.boczny.legenda
        self.pole_mapy = PoleMapy(self.mapa, self.boczny)
        self._mapa_uklad = mu = QHBoxLayout()
        mu.addWidget(self.pole_mapy, 1)
        su.addLayout(mu, 1)
        self.lista = ListaDofrezowania()
        self.lista.filtr.connect(self._ustaw_filtr)
        self.lista.wybrano.connect(self._klik_pozycja)
        self.lista.zapisz.connect(self._zapisz_liste)
        su.addWidget(self.lista)
        calosc.addWidget(srodek, 1)

        self.widok = WidokPracy()
        self.widok.decyzja.connect(self._decyzja)
        self.widok.wybor_wpisu.connect(self._wybor_wpisu)  # E3-A5i: krazek pracy do wyboru
        self.widok.cofnij_wpis.connect(self._cofnij_wpis)
        self.widok.zamknij.connect(self._zamknij_prace)
        self.widok.nastepna.connect(self._idz_do_nastepnej)
        self.widok.inna_praca.connect(self._inna_praca)
        calosc.addWidget(self.widok)

        self.strona_rano = QWidget()
        self.strona_rano.setObjectName("strona_rano")
        self._rano_uklad = QVBoxLayout(self.strona_rano)
        self.ekran_rano = EkranRano(self)
        self._rano_uklad.addWidget(self.ekran_rano)
        self._strony.addWidget(self.strona_rano)

        self.pasek_stanu = C.PasekStanu(wersja_programu())
        self.pasek_stanu.odswiez_pule.connect(lambda: self._polecenie("odswiez_pule"))
        self.pasek_stanu.test_led.connect(lambda: self._polecenie("test_led"))  # E3-A12: ramki
        self.pasek_stanu.przejmij_ramke.connect(lambda rola: self._polecenie("przejmij_ramke", rola))
        self.pasek_stanu.przelacz_bledy.connect(self._przelacz_bledy)
        korzen.addWidget(self.pasek_stanu)

        # nakladki okna (nie sa w ukladzie - nie zabieraja miejsca mapie): lista osob pod paskiem gornym, lista bledow nad paskiem stanu
        self.panel_osoby = C.PanelOsoby(self)
        self.panel_osoby.wybrano.connect(self._wybrano_osobe)
        self.panel_osoby.bez_zmian.connect(self._przelacz_zmiane_osoby)
        self.panel_osoby.wyloguj.connect(self._wyloguj)
        self.bledy = C.ListaBledow(self)
        self.bledy.polecenie.connect(self._polecenie_panelu)

    def _ustaw_uklad(self, u: motyw.Uklad) -> None:
        """Uklad okna dla jego rozmiaru (``motyw.uklad_dla``): szerokosci kolumn, stale wysokosci strefy / naglowka / listy,
        odstepy. Ekran poranny (stary uklad) dostaje swoje rozmiary ``styl`` - zwykle albo zwarte."""
        self._uklad = u
        self.pasek_gorny.ustaw_uklad(u)
        self.pasek_stanu.ustaw_uklad(u)
        self.lista_plytek.ustaw_uklad(u)
        self.strefa.ustaw_uklad(u)
        self.setStyleSheet(motyw.arkusz(u))
        self.naglowek_pole.setFixedHeight(u.naglowek)
        self._naglowek_uklad.setContentsMargins(u.bok, 8 if u.zwarty else 12, u.bok, 0)
        self._mapa_uklad.setContentsMargins(u.bok, 4 if u.zwarty else 8, u.bok, 8 if u.zwarty else 12)
        self.mapa.setMinimumSize(*u.mapa_min)
        self.boczny.ustaw_uklad(u)
        self.pole_mapy.ustaw_odstep(u.odstep)
        self.lista.ustaw_uklad(u)
        self.widok.ustaw_uklad(u)
        r = styl.rozmiary(u.zwarty)
        self._rano_uklad.setContentsMargins(r.margines, r.margines, r.margines, r.margines)
        self.ekran_rano.setStyleSheet(styl.arkusz(r))
        self.ekran_rano.ustaw_tryb(r)
        self._sygnatury.clear()
        self._odswiez()

    def resizeEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        super().resizeEvent(zdarzenie)
        u = motyw.uklad_dla(self.width(), self.height())
        if u is not self._uklad:
            self._ustaw_uklad(u)
        self._uloz_nakladki()

    def zwarty(self) -> bool:
        """Uklad zwarty (male okno) - do testow i kontroli."""
        return self._uklad.zwarty

    def uklad(self) -> motyw.Uklad:
        return self._uklad

    def rano(self) -> bool:
        """Pokazany ekran poranny (``stan.tryb == "rano"``, E3-A7)."""
        return self._strony.currentWidget() is self.strona_rano

    def miejsce_mapy(self) -> QRect:
        """Prostokat mapy w oknie - to, co technik ma pod kursorem (do testow: mapa nie zmienia miejsca przy zmianie stanu)."""
        return QRect(self.mapa.mapTo(self, QPoint(0, 0)), self.mapa.size())

    def _uloz_nakladki(self) -> None:
        """Polozenie nakladek: lista osob pod paskiem gornym po prawej, lista bledow nad paskiem stanu po lewej (nad lista
        "Do dofrezowania" - nie zaslania mapy ani przyciskow decyzji)."""
        gora, dol = self.pasek_gorny.height(), self.height() - self.pasek_stanu.height()
        if not self.panel_osoby.isHidden():
            szer = min(C.PanelOsoby.SZEROKOSC, max(200, self.width() - 24))
            wys = self.panel_osoby.heightForWidth(szer)
            if wys <= 0:
                wys = self.panel_osoby.sizeHint().height()
            wys = min(wys, max(80, dol - gora - 12))
            self.panel_osoby.setGeometry(self.width() - szer - 12, gora + 4, szer, wys)
            self.panel_osoby.raise_()
        if not self.bledy.isHidden():
            szer = max(240, self.width() - self._uklad.prawa - 16)  # lewa kolumna i srodek; z rozmiaru okna (uklad moze byc w trakcie zmiany)
            wys = self.bledy.wysokosc_dla(szer, max(110, self._uklad.lista - 4))
            self.bledy.setGeometry(8, dol - wys - 4, szer, wys)
            self.bledy.raise_()

    # --- sygnaly kontrolera ----------------------------------------------------------------------
    def _na_stan(self, stan) -> None:
        self.pokaz_stan(stan)

    def _na_postep(self, _postep) -> None:
        """Postep analizy: zmienia sie tylko czesc "zywa" stanu - odswiezany jest sam pasek stanu (i znak poprzedniej plytki)."""
        if self._zamkniete:
            return
        stan = self.k.stan()
        if self._stan is None or stan.wersja >= self._stan.wersja:
            if self._stan is not None and stan.plytki is not self._stan.plytki:
                self.pokaz_stan(stan)
            else:  # rano: zmiane blokady "Zamknij piec" (analiza / skanowanie) kontroler podaje pelnym stanem (recenzja PR #26, D1)
                self._stan = stan
                self.pasek_stanu.ustaw(stan)
                if not self.rano():
                    self._oznacz_poprzednia(stan, self._plytka())

    def _na_zamkniety(self) -> None:
        self.setEnabled(False)

    def pokaz_stan(self, stan) -> None:
        """Pokazuje ``stan`` (``StanAplikacji``). Stan starszy niz pokazany jest pomijany (kontrakt: zagniezdzona petla okna)."""
        if stan is None or self._zamkniete or (self._stan is not None and stan.wersja < self._stan.wersja):
            return
        self._stan = stan
        for k in stan.komunikaty:  # kolejnosc pojawiania sie komunikatow (najnowsze na gorze)
            self._nr_komunikatow.setdefault(k.id, len(self._nr_komunikatow))
        self._wybierz_plytke(stan)
        if self._wstrzymaj:
            return
        rano = stan.tryb == K.TRYB_RANO
        powrot = False
        if rano != self.rano():  # zmiana trybu - druga strona srodka okna; tryb wieczorny przebudowany od nowa po powrocie
            self._strony.setCurrentWidget(self.strona_rano if rano else self.strona_wieczor)
            self._sygnatury.clear()
            self._mapa_podpis = None
            powrot = not rano
            if powrot:  # S3-15: po powrocie z trybu "Poranek" kursor gniazda jest wyzerowany
                self._kursor = None
                self.mapa.ustaw_kursor(None)
            if not self._w_poleceniu:
                self.setFocus(Qt.FocusReason.OtherFocusReason)
        poprzednio, self._z_tla = self._z_tla, not self._w_poleceniu
        try:
            self._odswiez()
        finally:
            self._z_tla = poprzednio
        if powrot and self.mapa.numery():  # S3-15: i ochrona 800 ms - klikniecie wycelowane w ekran poranny nie trafia w gniazdo
            self._wlacz_ochrone()

    def pokazana_plytka(self) -> int | None:
        """``skan_id`` plytki, ktorej mapa jest na ekranie."""
        return self._plytka_id

    def ochrona_aktywna(self) -> bool:
        """Mapa przygaszona po zmianie zawartosci (A-P2): klikniecia mapy, Enter, N i skroty decyzji sa pomijane."""
        return self._ochrona.isActive()

    def ochrona_strefy_aktywna(self) -> bool:
        """Strefa pytan przygaszona, bo jej pozycja zmienila sie w tle (S3-3): przyciski strefy nie przyjmuja klikniec."""
        return self._ochrona_strefy.isActive()

    def _wlacz_ochrone(self) -> None:
        self._ochrona.start()
        self.mapa.przygas(True)

    @staticmethod
    def _nowy_skan_w_drodze(stan) -> bool:
        """S3-14: program ma skan, ktorego wyniku jeszcze nie pokazal (analiza trwa albo skan czeka w kolejce)."""
        return stan.analiza is not None or stan.kolejka.razem > 0

    def _oznacz_poprzednia(self, stan, plytka) -> None:
        """S3-14: gdy wynik nowego skanu nie jest jeszcze gotowy, mapa na ekranie jest mapa POPRZEDNIEJ plytki - znak w naglowku
        plytki i przygaszona mapa (klikniecia dzialaja: technik moze konczyc poprzednia plytke)."""
        poprzednia = plytka is not None and self._nowy_skan_w_drodze(stan)
        self.mapa.oznacz_poprzednia(poprzednia)
        self.znak_poprzedniej.setVisible(poprzednia)

    def ochrona_nakladek_aktywna(self) -> bool:
        """Trwa ochrona strefy pytan albo listy bledow (przygaszone, klikniecia pomijane) - do zrzutow i testow."""
        return self._ochrona_strefy.isActive() or self._ochrona_bledow.isActive()

    # --- wybor plytki i pracy ----------------------------------------------------------------------
    def _wybierz_plytke(self, stan) -> None:
        numery = [p.skan_id for p in stan.plytki]
        nowe = [i for i in numery if i not in self._znane]
        self._znane.update(numery)
        self._nieobejrzane &= set(numery)
        if self._plytka_id is not None and self._plytka_id not in numery:
            if self._gniazdo is not None or self._poza is not None:
                self._informacja = N.PRACA_ZNIKNELA
            self._plytka_id, self._gniazdo, self._poza, self._numer_dla, self._praca_widoku = None, None, None, None, None
        if nowe and not self._pierwszy_stan:
            if self._mozna_przelaczyc(stan):
                self._plytka_id, self._numer_dla = nowe[-1], None
                self._nieobejrzane.update(nowe[:-1])
            else:
                self._nieobejrzane.update(nowe)  # technik oglada plytke albo prace: nie zabieramy mu ekranu
                self._blysk_nowej = True
        self._pierwszy_stan = False
        if self._plytka_id is None and numery:
            self._plytka_id = stan.biezaca_plytka if stan.biezaca_plytka in numery else numery[-1]
        self._nieobejrzane.discard(self._plytka_id)
        pokazana = stan.plytka(self._plytka_id) if self._plytka_id is not None else None
        if pokazana is not None:  # E3-P14 (N2): poprzedni skan plytki, o ktory pyta pokazana plytka, nie jest juz "nowym wynikiem"
            self._nieobejrzane.discard(pokazana.moze_zastapic)
        if self._numer_dla is not None and self._numer_dla != self._plytka_id:
            self._numer_dla = None  # S3-3: wybor numeru nalezy do jednego skanu - nie przechodzi na inna plytke
        if self._zmiana_osoby and stan.wymaga_operatora:
            self._zmiana_osoby = False

    def _mozna_przelaczyc(self, stan) -> bool:
        """Nowa plytka moze zajac ekran sama tylko wtedy, gdy technik nie ma otwartej pracy ani wyboru numeru, a na pokazanej
        plytce nie zostalo nic do zrobienia: praca do obejrzenia (czerwona / zolta bez decyzji - A-P2), otwarte pytanie ani
        brakujacy numer plytki (S3-3: przyciski pytania i wyboru numeru nie zmieniaja plytki pod reka technika)."""
        if self._gniazdo is not None or self._poza is not None or self._numer_dla is not None:
            return False
        plytka = stan.plytka(self._plytka_id) if self._plytka_id is not None else None
        if plytka is None:
            return True
        if do_obejrzenia(plytka):
            return False
        if any(q.skan_id == plytka.skan_id for q in otwarte(stan.pytania)):
            return False
        return not (plytka.numer is None and plytka.prace and "podaj_numer_plytki" in plytka.dozwolone)

    def _plytka(self):
        return self._stan.plytka(self._plytka_id) if self._stan is not None and self._plytka_id is not None else None

    def _wybor(self):
        """(gniazdo, praca) wybrane przez technika wg biezacego stanu; (None, None), gdy nic nie jest wybrane albo zniknelo."""
        plytka = self._plytka()
        if plytka is None:
            return None, None
        if self._gniazdo is not None:
            g = plytka.gniazdo(self._gniazdo)
            if g is None:
                return None, None
            self._nr_pracy = min(self._nr_pracy, max(0, len(g.prace) - 1))
            return g, (g.prace[self._nr_pracy] if g.prace else None)
        if self._poza is not None:
            return None, next((p for p in plytka.poza_gniazdem if p.praca_id == self._poza), None)
        return None, None

    def _pokaz_plytke(self, skan_id: int, gniazdo: int | None = None, poza: int | None = None, praca_id: int | None = None) -> None:
        """Pokazuje plytke ``skan_id`` (i gniazdo / prace poza gniazdem). ``praca_id`` - S3-15: gdy w gniezdzie leza dwie prace,
        otwierana jest dokladnie ta (pozycja listy "do dofrezowania" wskazuje prace, nie gniazdo)."""
        plytka = self._stan.plytka(skan_id) if self._stan is not None else None
        if plytka is None:
            return
        nr_pracy = 0
        if gniazdo is not None and praca_id is not None:
            g = plytka.gniazdo(gniazdo)
            nr_pracy = next((i for i, p in enumerate(g.prace) if p.praca_id == praca_id), 0) if g is not None else 0
        self._plytka_id, self._gniazdo, self._poza, self._nr_pracy, self._numer_dla = skan_id, gniazdo, poza, nr_pracy, None
        self._praca_widoku = None
        self._nieobejrzane.discard(skan_id)
        # E3-P14 (N2): pokazana plytka pyta "ponowny skan?" o swoj poprzedni skan - ten tez przestaje byc "nowym wynikiem"
        self._nieobejrzane.discard(plytka.moze_zastapic)
        self._odswiez()

    def _pokaz_nowa(self) -> None:
        """"Pokaz nowy wynik" nad lista plytek: najnowsza plytka, na ktora ekran sie nie przelaczyl."""
        if self._stan is None:
            return
        nowe = [p.skan_id for p in self._stan.plytki if p.skan_id in self._nieobejrzane]
        if nowe:
            self._pokaz_plytke(nowe[-1])

    def _klik_gniazdo(self, nr: int) -> None:
        self._gniazdo, self._poza, self._nr_pracy, self._praca_widoku, self._kursor = nr, None, 0, None, None
        self._odswiez()

    def _klik_poza(self, praca_id: int) -> None:
        if self.ochrona_aktywna():
            return
        self._gniazdo, self._poza, self._nr_pracy, self._praca_widoku = None, praca_id, 0, None
        self._odswiez()

    def _klik_pozycja(self, pozycja) -> None:
        """Klikniecie pozycji listy "do dofrezowania": pokazuje DOKLADNIE te prace (``praca_id`` - S3-15), jesli jej plytka jest
        w stanie tej doby; inaczej krotka informacja, skad jest ta praca (A-D9)."""
        self.setFocus(Qt.FocusReason.MouseFocusReason)
        if self._stan is None:
            return
        if self._stan.plytka(pozycja.skan_id) is None:
            self._informacja = N.POZYCJA_Z_INNEJ_DOBY.format(doba=dzien(pozycja.doba, rok=True), zmiana=pozycja.zmiana)
            self._odswiez()
            return
        skan_id, gniazdo, praca_id = pozycja.skan_id, pozycja.gniazdo, pozycja.praca_id
        poza = praca_id if gniazdo is None else None
        QTimer.singleShot(0, lambda: self._pokaz_plytke(skan_id, gniazdo, poza, praca_id))

    def _zamknij_prace(self) -> None:
        if self._gniazdo is None and self._poza is None:
            return
        self._gniazdo, self._poza, self._nr_pracy, self._praca_widoku = None, None, 0, None
        self._odswiez()

    def _inna_praca(self) -> None:
        g, _ = self._wybor()
        if g is not None and len(g.prace) > 1:
            self._nr_pracy = (self._nr_pracy + 1) % len(g.prace)
            self._praca_widoku = None
            self._odswiez()

    def _nastepna(self, plytka) -> int | None:
        """Numer nastepnego gniazda z praca do obejrzenia (``czesci.do_obejrzenia``)."""
        if plytka is None:
            return None
        do = {p.praca_id for p in do_obejrzenia(plytka)}
        numery = [g.nr for g in plytka.gniazda if g.nr != self._gniazdo and any(p.praca_id in do for p in g.prace)]
        if not numery:
            return None
        dalsze = [nr for nr in numery if self._gniazdo is None or nr > self._gniazdo]
        return (dalsze or numery)[0]

    def _idz_do_nastepnej(self) -> None:
        if self.ochrona_aktywna():  # S3-15: N tuz po zmianie mapy otworzyloby prace na innej plytce niz ta, na ktora patrzyl technik
            return
        nr = self._nastepna(self._plytka())
        if nr is not None:
            self._klik_gniazdo(nr)

    def _ruch_kursora(self, dx: int, dy: int) -> None:
        """Strzalka: kursor gniazda na mapie (pierwsze nacisniecie - gniazdo otwarte albo pierwsze do obejrzenia)."""
        numery = self.mapa.numery()
        plytka = self._plytka()
        if not numery or plytka is None:
            return
        start = self._kursor if self._kursor in numery else (self._gniazdo if self._gniazdo in numery else None)
        if start is None:
            do = {p.praca_id for p in do_obejrzenia(plytka)}
            pierwsze = [g.nr for g in plytka.gniazda if g.nr in numery and any(p.praca_id in do for p in g.prace)]
            self._kursor = (pierwsze or numery)[0]
        else:
            nr = self.mapa.sasiad(start, dx, dy)
            self._kursor = nr if nr is not None else start
        self.mapa.ustaw_kursor(self._kursor)

    def _wybierz_kursor(self) -> None:
        """Enter: otwiera prace w gniezdzie pod kursorem (jak klikniecie; pomijane, gdy mapa jest przygaszona)."""
        if self._kursor is not None and self._kursor in self.mapa.numery() and not self.ochrona_aktywna():
            self._klik_gniazdo(self._kursor)

    def _ustaw_filtr(self, wszystkie: bool) -> None:
        self._lista_wszystkie = wszystkie
        self._odswiez()

    def _przelacz_wczesniejsze(self) -> None:
        self._pokaz_wczesniejsze = not self._pokaz_wczesniejsze
        self._odswiez()

    def _przelacz_zmiane_osoby(self) -> None:
        self._zmiana_osoby = not self._zmiana_osoby
        self._odswiez()

    def _przelacz_bledy(self) -> None:
        """Licznik bledow na pasku stanu: rozwija albo zwija liste bledow programu (zwinieta zostaje do nastepnego nowego bledu)."""
        self._bledy_zwiniete = not self._bledy_zwiniete
        self._odswiez()

    def _nastepna_uwaga(self) -> None:
        """"i jeszcze n" w strefie pytan: nastepna pozycja (po ostatniej - znowu pierwsza)."""
        self._nr_uwagi += 1
        self._odswiez()

    # --- polecenia -------------------------------------------------------------------------------
    def _polecenie(self, nazwa: str, *argumenty):
        """Polecenie do kontrolera. Odmowa wraca jako ``Odpowiedz`` (nie wyjatek): zwykle jest tez komunikatem w stanie i ekran
        pokazuje go po odswiezeniu; gdy stan jej nie zawiera (np. ``zle_argumenty``), okno pokazuje tekst odpowiedzi samo.
        Stan, ktory przychodzi w trakcie polecenia, jest skutkiem decyzji technika - mapa nie jest wtedy przygaszana."""
        if self._zamkniete or self._stan is None or self._stan.zamkniety:
            return None
        poprzednio, self._w_poleceniu = self._w_poleceniu, True
        try:
            odpowiedz = self.k.wykonaj(nazwa, *argumenty)  # kontrakt: polecenia nie rzucaja wyjatkow (zle dane = odmowa ``zle_argumenty``)
            stan = self.k.stan()
            tekst = odpowiedz.tekst if not odpowiedz.ok else ""
            # odmowa, ktora jest juz w stanie jako komunikat albo pytanie (rano: "zmienic numer mimo to?"), nie jest powtarzana
            w_stanie = any(k.tekst == tekst for k in otwarte(stan.komunikaty)) or any(q.tekst == tekst for q in stan.pytania)
            self._odmowa = tekst if tekst and not w_stanie else ""
            self._informacja = ""
            if nazwa == "podaj_numer_plytki" and (odpowiedz.ok or odpowiedz.kod == "numer_nowy_wsad"):
                self._numer_dla = None  # rano "numer_nowy_wsad": wybor numeru ustepuje pytaniu "zmienic numer mimo to?" (A6 runda 4)
                self.ekran_rano.numer_podany()
            if stan.wersja == self._stan.wersja:
                if not self._wstrzymaj:
                    self._odswiez()  # polecenie bez nowego stanu (odmowa bez komunikatu): pokaz tekst odpowiedzi
            else:
                self.pokaz_stan(stan)
        finally:
            self._w_poleceniu = poprzednio
        return odpowiedz

    def _start_skanu(self) -> None:
        self._polecenie("start_skanu")

    def _praca_do_polecenia(self):
        """Praca pokazana w widoku pracy, o ile wybor technika wskazuje dokladnie ja (A-P2); inaczej None."""
        _, praca = self._wybor()
        if praca is None or self._praca_widoku is None or praca.praca_id != self._praca_widoku or self.widok.praca_id != self._praca_widoku:
            return None
        return praca

    def _decyzja(self, nazwa: str) -> None:
        """Decyzja dla pracy, ktorej dane pokazuje widok pracy (A-P2): tylko gdy wybor technika wskazuje dokladnie te prace."""
        if self.widok.aktywny(nazwa) and self._praca_do_polecenia() is not None:
            self._polecenie(nazwa, self._praca_widoku)

    def _wybor_wpisu(self, frezowanie_id: int) -> None:
        """E3-A5i: krazek wskazany przez technika dla pracy pokazanej w widoku pracy (tylko gdy widok pokazuje wybrana prace)."""
        if self._praca_do_polecenia() is not None:
            self._polecenie("wybierz_wpis", self._praca_widoku, int(frezowanie_id))

    def _cofnij_wpis(self) -> None:
        praca = self._praca_do_polecenia()
        if praca is not None and praca.wybor_wpisu_id is not None:  # runda 3 (D6): dokladnie pokazany wybor - podwojne klikniecie nie cofa drugiego
            self._polecenie("cofnij_wpis", self._praca_widoku, praca.wybor_wpisu_id)

    def _wybrano_osobe(self, osoba: str) -> None:
        self._zmiana_osoby = False
        self._polecenie("wybierz_operatora", osoba)

    def _wyloguj(self) -> None:
        self._zmiana_osoby = False
        self._polecenie("wybierz_operatora", None)

    def _zapisz_liste(self) -> None:
        self._polecenie("zapisz_liste")  # czas zapisu wraca w stanie (``lista_zapisana``); odmowa = komunikat

    def _przelacz_numer(self) -> None:
        """"Podaj numer plytki" / "Zmien numer" obok mapy: otwiera albo zamyka wybor numeru POKAZANEJ plytki (S3-3: po ``skan_id``)."""
        self._numer_dla = None if self._numer_dla is not None else self._plytka_id
        self._odswiez()

    # --- klawiatura ------------------------------------------------------------------------------
    def keyPressEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        klawisz = zdarzenie.key()
        if self.rano():  # E3-A7: klawisze ramki porannej (cyfry, Enter, Backspace, Esc) ma ekran poranny; Spacja = start skanu
            if self.ekran_rano.klawisz(zdarzenie):
                zdarzenie.accept()
            elif klawisz == Qt.Key.Key_Space:
                if not zdarzenie.isAutoRepeat():
                    self._start_skanu()
                zdarzenie.accept()
            elif klawisz == Qt.Key.Key_Escape and self._zmiana_osoby and not zdarzenie.isAutoRepeat():
                self._przelacz_zmiane_osoby()
                zdarzenie.accept()
            else:
                super().keyPressEvent(zdarzenie)
            return
        kierunek = {Qt.Key.Key_Left: (-1, 0), Qt.Key.Key_Right: (1, 0), Qt.Key.Key_Up: (0, -1), Qt.Key.Key_Down: (0, 1)}
        for k, (dx, dy) in kierunek.items():
            if klawisz == k:  # strzalki takze z autopowtarzaniem (przytrzymana strzalka przesuwa kursor dalej)
                self._ruch_kursora(dx, dy)
                zdarzenie.accept()
                return
        if zdarzenie.isAutoRepeat():  # przytrzymany klawisz to jedno nacisniecie
            zdarzenie.accept()
            return
        if klawisz == Qt.Key.Key_Space:
            self._start_skanu()
        elif klawisz in (Qt.Key.Key_U, Qt.Key.Key_O, Qt.Key.Key_C):
            if not self.ochrona_aktywna():  # A-P2: skrot tuz po zmianie mapy moze byc wycelowany w poprzedni obraz
                self._decyzja("ukruszona" if klawisz == Qt.Key.Key_U else "ok" if klawisz == Qt.Key.Key_O else "cofnij")
        elif klawisz == Qt.Key.Key_N:
            self._idz_do_nastepnej()
        elif klawisz in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._wybierz_kursor()
        elif klawisz == Qt.Key.Key_Escape:
            if self._zmiana_osoby:
                self._przelacz_zmiane_osoby()
            elif self._kursor is not None and self._gniazdo is None and self._poza is None:
                self._kursor = None
                self.mapa.ustaw_kursor(None)
            else:
                self._zamknij_prace()
        else:
            super().keyPressEvent(zdarzenie)
            return
        zdarzenie.accept()

    def showEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        super().showEvent(zdarzenie)
        self.setFocus()
        self._uloz_nakladki()

    def closeEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        """Okno odlacza sie od lacznika i konczy watek obrazow; kontroler zamyka ``aplikacja.main()``."""
        if not self._zamkniete:
            self._zamkniete = True
            for zegar in (self._ochrona, self._ochrona_strefy, self._ochrona_bledow):
                zegar.stop()
            for sygnal, odbiorca in ((self.lacznik.stan_zmieniony, self._na_stan), (self.lacznik.postep, self._na_postep),
                                     (self.lacznik.zamkniety, self._na_zamkniety)):
                try:
                    sygnal.disconnect(odbiorca)
                except (RuntimeError, TypeError):
                    pass
            self.wczytywacz.zakoncz()
        super().closeEvent(zdarzenie)

    # --- odswiezanie -----------------------------------------------------------------------------
    def _zmienione(self, czesc: str, sygnatura) -> bool:
        if self._sygnatury.get(czesc) == sygnatura:
            return False
        self._sygnatury[czesc] = sygnatura
        return True

    def _odswiez(self) -> None:
        stan = self._stan
        if stan is None:
            return
        self.pasek_gorny.ustaw(stan)
        self.pasek_stanu.ustaw(stan)
        self._odswiez_osobe(stan)
        if self.rano():  # ekran poranny pokazuje sam swoje czesci (takze bledy programu); wieczorny (niewidoczny) nie jest przebudowywany
            self.bledy.setVisible(False)
            self.pasek_stanu.ustaw_bledy(0, False)
            self.ekran_rano.pokaz(stan)
            self._uloz_nakladki()
            return
        plytka = self._plytka()
        gniazdo, praca = self._wybor()
        if self._praca_widoku is not None and (praca is None or praca.praca_id != self._praca_widoku):
            # stan zmienil sie w tle: widok pracy nie moze pokazywac (i decydowac o) innej pracy niz ta, ktora technik otworzyl
            self._informacja = N.PRACA_ZNIKNELA if stan.praca(self._praca_widoku) is None else N.PRACA_ZMIENIONA
            gniazdo, praca = None, None
        if gniazdo is None and praca is None:
            self._gniazdo, self._poza = None, None
        self._praca_widoku = praca.praca_id if praca is not None else None
        widoczne = [p for p in stan.plytki if self._pokaz_wczesniejsze or p.zmiana in (None, stan.zmiana) or p.skan_id == self._plytka_id]
        wczesniejszych = sum(1 for p in stan.plytki if p.zmiana not in (None, stan.zmiana))
        z_komunikatem = {k.skan_id for k in otwarte(stan.komunikaty) if k.skan_id is not None and k.skan_id != self._plytka_id}
        # E3-P14 (poz. 8): skan, ktory otwarte pytanie "ponowny skan?" proponuje zastapic - kafelek "poprzedni skan"
        poprzednie = {q.poprzedni_id for q in otwarte(stan.pytania) if q.rodzaj == "ponowny_skan" and q.poprzedni_id is not None}
        self.lista_plytek.ustaw(widoczne, self._plytka_id, self._nieobejrzane, {q.skan_id for q in otwarte(stan.pytania)}, wczesniejszych,
                                self._pokaz_wczesniejsze, stan.niezapisane, z_komunikatem, poprzednie)
        nowe = [p for p in stan.plytki if p.skan_id in self._nieobejrzane]
        self.lista_plytek.ustaw_nowe(nazwa_plytki(nowe[-1].numer) if nowe else None, len(nowe))
        # E3-P14 (N2): wynik nowej plytki czeka, ekran zostal na ogladanej - trwala informacja z jej pytaniami i komunikatami
        # w kolumnie plytek (nie nad mapa - mapa ogladanej plytki nie zmienia polozenia ani rozmiaru)
        sprawy = sprawy_nowych_plytek(stan, nowe)
        if self._zmienione("nowy_wynik", sprawy):
            self.lista_plytek.ustaw_panel_nowego(C.uwaga_nowego_wyniku(sprawy) if sprawy else None)
        if self._blysk_nowej and nowe:
            self.pasek_gorny.blysk()  # krotki sygnal na pasku: przyszedl wynik, ekran zostaje na pokazanej plytce
        self._blysk_nowej = False
        geometria = geometria_ukladu(self.k, plytka.uklad) if plytka is not None and plytka.gniazda and (plytka.aktywna or plytka.prace) else None
        self._sprawdz_zmiane_mapy(plytka)
        if plytka is None or self._kursor not in {g.nr for g in plytka.gniazda}:
            self._kursor = None
        self.mapa.ustaw(plytka, geometria, self._gniazdo)
        self.mapa.ustaw_kursor(self._kursor)
        self._oznacz_poprzednia(stan, plytka)
        self._odswiez_naglowek(stan, plytka)
        self._odswiez_uwagi(stan, plytka)
        jest_nastepna = self._nastepna(plytka) is not None
        if gniazdo is None and praca is None:
            self.widok.wyczysc(jest_nastepna)
            self._obraz_dla = None
        else:
            self.widok.ustaw(stan, plytka, gniazdo, praca, self._nr_pracy, jest_nastepna)
            self._odswiez_obraz(praca)
        self.lista.ustaw(stan.do_dofrezowania_biezaca if self._lista_wszystkie else stan.do_dofrezowania, self._lista_wszystkie,
                         stan.lista_zapisana)
        self._uloz_nakladki()
        self._porzadek_tabulacji()

    def _sprawdz_zmiane_mapy(self, plytka) -> None:
        """A-P2: zawartosc mapy sie zmienila (inna plytka albo nowy stan pokazanej plytki spoza polecen technika), a poprzednia
        mapa miala gniazda do klikniecia -> mapa przygaszona na ``OCHRONA_MS``, klikniecia i skroty decyzji pomijane."""
        rysowane = plytka is not None and (plytka.aktywna or plytka.prace)
        podpis = (plytka.skan_id if plytka is not None else None,
                  tuple((g.nr, g.status, g.rgb, g.podpis) for g in plytka.gniazda) if rysowane else (),
                  tuple(p.praca_id for p in plytka.poza_gniazdem) if plytka is not None else ())
        poprzedni = self._mapa_podpis
        if podpis == poprzedni:
            return
        self._mapa_podpis = podpis
        if poprzedni is None:
            return
        if poprzedni[0] != podpis[0]:
            self._kursor = None
        if (poprzedni[1] or poprzedni[2]) and (poprzedni[0] != podpis[0] or not self._w_poleceniu):
            self._wlacz_ochrone()

    def _koniec_ochrony(self) -> None:
        self.mapa.przygas(False)

    def _porzadek_tabulacji(self) -> None:
        """Kolejnosc klawisza Tab: pasek gorny, lista osob, strefa pytan, plytki, polecenia plytki, widok pracy, lista, bledy, pasek stanu."""
        kolejne = []
        for sekcja in (self.pasek_gorny, self.panel_osoby, self.strefa, self.lista_plytek, self.boczny, self.widok, self.lista, self.bledy,
                       self.pasek_stanu):
            kolejne += [w for w in sekcja.findChildren(QWidget)
                        if isinstance(w, (QPushButton, KafelekPlytki)) and w.focusPolicy() == Qt.FocusPolicy.TabFocus]
        podpis = tuple(id(w) for w in kolejne)
        if podpis == self._tab_podpis:
            return
        self._tab_podpis = podpis
        for a, b in zip(kolejne, kolejne[1:]):
            QWidget.setTabOrder(a, b)

    def _odswiez_osobe(self, stan) -> None:
        """Lista osob pod paskiem gornym: sama sie rozwija, gdy program wymaga wyboru osoby; technik rozwija ja przyciskiem "Zmien"."""
        pokaz = stan.wymaga_operatora or self._zmiana_osoby
        if not stan.operatorzy:
            teksty = [ST.tekst_komunikatu("pusta_lista_operatorow")[2]]
        elif stan.wymaga_operatora:
            teksty = [k.tekst for k in otwarte(stan.komunikaty) if k.rodzaj == "nowa_zmiana"][-1:] + [ST.tekst_komunikatu("brak_operatora")[2]]
        else:
            teksty = []
        if pokaz:
            self.panel_osoby.ustaw(stan.operatorzy, stan.operator, teksty, zmiana_osoby=not stan.wymaga_operatora)
        self.panel_osoby.setVisible(pokaz)

    def _odswiez_naglowek(self, stan, plytka) -> None:
        """Naglowek plytki (numer i opis skanu: godzina, napis ze stanu, stan obejrzenia) i panel obok mapy."""
        if plytka is None:
            self.naglowek.setText("")
            self.podnaglowek.setText("")
        else:
            self.naglowek.setText(nazwa_plytki(plytka.numer))
            napis = stan_obejrzenia(plytka)  # "do obejrzenia: n" / "sprawdzona" albo napis ze stanu
            czas = godzina(plytka.czas)
            czesci = ([N.MAPA_GODZINA.format(godzina=czas)] if czas else []) + ([plytka.napis] if napis != plytka.napis else []) + [napis]
            self.podnaglowek.setText(N.KROPKA.join(c for c in czesci if c))
        # polecenia plytki ze stanu (``Plytka.dozwolone``); te, o ktore wlasnie pyta otwarte pytanie, sa tylko w strefie pytan
        w_pytaniach = {PYTANE.get(q.rodzaj) for q in otwarte(stan.pytania) if plytka is not None and q.skan_id == plytka.skan_id}
        akcje = tuple(a for a in POLECENIA_PLYTKI if plytka is not None and a in plytka.dozwolone and a not in w_pytaniach and a in ST.PRZYCISKI)
        self.boczny.ustaw(plytka, akcje, stan.operator is not None, self._poza)

    def _dopisek_konfliktu(self, stan, grupa) -> str:
        """Gniazda konfliktu projektu ze ``stan.konflikty`` (A-P5 poz. 10): "Gniazda: Plytka 2, gniazdo 3 i Plytka 2, gniazdo 7."."""
        if grupa[0].rodzaj != "konflikt_projektu":
            return ""
        po_skrocie = {k.get("sha16"): k for k in stan.konflikty}
        opisy = []
        for komunikat in grupa:
            konflikt = po_skrocie.get(komunikat.id.split(":", 1)[-1])
            if konflikt is None:
                continue
            miejsca = []
            for m in konflikt.get("miejsca") or ():
                plytka = stan.plytka(m.get("skan_id"))  # godzina skanu odroznia dwa skany plytki o tym samym numerze
                czas = godzina(plytka.czas) if plytka is not None else ""
                miejsca.append(N.KONFLIKT_MIEJSCE.format(plytka=nazwa_plytki(m.get("numer_plytki")) + (N.KONFLIKT_GODZINA.format(godzina=czas) if czas else ""),
                                                         gniazdo=m.get("gniazdo") if m.get("gniazdo") is not None else N.BRAK_DANYCH))
            if miejsca:
                opisy.append(N.KONFLIKT_I.join(miejsca))
        if not opisy:
            return ""
        tekst = N.KONFLIKT_ODSTEP.join(opisy[:KONFLIKTOW_W_PANELU]) + (N.KONFLIKT_DALEJ if len(opisy) > KONFLIKTOW_W_PANELU else "")
        return N.KONFLIKT_MIEJSCA.format(miejsca=tekst)

    def pozycje_strefy(self, stan, plytka) -> tuple:
        """(pozycje strefy pytan w kolejnosci waznosci, bledy programu): informacja ekranu, tekst odmowy spoza stanu, wybor
        numeru plytki, otwarte pytania pokazanej plytki (``stan.pytania``), jej komunikaty i pozostale komunikaty ogolne (od
        najnowszego; jednakowe razem). Bledy programu (poziom "blad" albo trwale, nie dotyczace plytki) ida na liste bledow."""
        pokaz_osobe = stan.wymaga_operatora or self._zmiana_osoby
        wszystkie = otwarte(stan.komunikaty)  # pozycje ukryte przez technika (``ukryte``) nie wracaja na ekran
        pytania = [q for q in otwarte(stan.pytania) if plytka is not None and q.skan_id == plytka.skan_id]
        komunikaty = [k for k in wszystkie if plytka is not None and k.skan_id == plytka.skan_id]
        numer = (plytka is not None and self._numer_dla == plytka.skan_id and "podaj_numer_plytki" in plytka.dozwolone
                 and not any(q.rodzaj == "brak_numeru_plytki" for q in pytania))
        ogolne = [k for k in wszystkie
                  if (k.skan_id is None or stan.plytka(k.skan_id) is None) and not (pokaz_osobe and k.rodzaj in SPRAWY_OSOBY)]
        ogolne.sort(key=lambda k: (0 if k.poziom == ST.POZIOM_BLAD else 1, -self._nr_komunikatow.get(k.id, 0)))  # od najnowszego
        bledy = [k for k in ogolne if blad_programu(k)]
        reszta = [k for k in ogolne if not blad_programu(k)]
        pozycje = []
        if self._informacja:
            pozycje.append(C.uwaga_informacji(self._informacja))
        if self._odmowa:
            pozycje.append(C.uwaga_odmowy(self._odmowa))
        if plytka is not None:
            czas = godzina(plytka.czas)
            nazwa = nazwa_plytki(plytka.numer)
            # S3-3: tytul kazdej pozycji plytki mowi, ktorego skanu dotyczy - numer plytki i godzina skanu (bez numeru: sama godzina)
            ze_skanem = (N.PLYTKA_ZE_SKANEM.format(plytka=nazwa, godzina=czas) if czas else nazwa) if plytka.numer is not None else ""
            if numer:
                geometria = geometria_ukladu(self.k, plytka.uklad)
                numery = tuple(geometria.numery) if geometria is not None and geometria.numery else K.NUMERY_PLYTEK_ZAPASOWE
                brak = ST.tekst_komunikatu("brak_operatora" if stan.operatorzy else "pusta_lista_operatorow")[2]
                pozycje.append(C.uwaga_numeru(plytka.skan_id, numery, plytka.numer, stan.operator is not None, brak, ze_skanem, czas))
            pozycje += [C.uwaga_pytania(q, stan, plytka.typ, ze_skanem, czas) for q in pytania]
        # komunikaty pokazanej plytki i ogolne razem: najpierw wazniejszy poziom, w poziomie od najnowszego - strefa pokazuje jedna
        # pozycje naraz, wiec swiezy komunikat (np. odmowa polecenia) nie moze czekac za starszym komunikatem plytki
        grupy = [(k,) for k in komunikaty] + [tuple(g) for g in grupuj(reszta)]
        grupy.sort(key=lambda g: (RANGA_POZIOMU.get(g[0].poziom, 1), -max(self._nr_komunikatow.get(k.id, 0) for k in g)))
        for g in grupy:
            if plytka is not None and g[0].skan_id == plytka.skan_id:
                pozycje.append(C.uwaga_komunikatu(g, ze_skanem or C.tytul_ze_skanem(nazwa, czas)))
            else:
                pozycje.append(C.uwaga_komunikatu(g, dodatek=self._dopisek_konfliktu(stan, g)))
        return tuple(pozycje), bledy

    def _odswiez_uwagi(self, stan, plytka) -> None:
        """Strefa pytan i komunikatow (jedna pozycja naraz, licznik "i jeszcze n") oraz lista bledow programu."""
        pozycje, bledy = self.pozycje_strefy(stan, plytka)
        self._odswiez_bledy(stan, bledy)
        klucze = tuple(u.klucz for u in pozycje)
        if klucze != self._klucze_uwag:  # zestaw pozycji sie zmienil (cos doszlo albo zniklo): strefa wraca do najwazniejszej
            self._klucze_uwag, self._nr_uwagi = klucze, 0
        nr = self._nr_uwagi % len(pozycje) if pozycje else 0
        przed = self.strefa.klucz()
        self.strefa.ustaw(pozycje[nr] if pozycje else None, max(0, len(pozycje) - 1))
        po = self.strefa.klucz()
        # S3-3: pozycja strefy zmienila sie w tle na inna (pytanie innej plytki, nastepny komunikat) - klikniecie wycelowane
        # w poprzednia nie moze trafic w nowa: przyciski strefy nie przyjmuja klikniec przez OCHRONA_MS
        if self._z_tla and przed is not None and po is not None and po != przed:
            self._ochrona_strefy.start()
            self.strefa.chron(True)

    def _odswiez_bledy(self, stan, bledy: list) -> None:
        """Bledy programu (A-P3): licznik na pasku stanu i rozwijana lista nad paskiem - bledy pierwsze, potem trwale; jednakowe
        razem. Nowy blad sam rozwija liste (blad nie moze zostac niezauwazony); technik zwija ja licznikiem."""
        grupy = grupuj(bledy)
        uwagi = tuple(C.uwaga_komunikatu(tuple(g), dodatek=self._dopisek_konfliktu(stan, g)) for g in grupy)
        obecne = frozenset(k.id for k in bledy)
        if obecne - self._bledy_znane:
            self._bledy_zwiniete = False
        self._bledy_znane = obecne
        zmiana = self._zmienione("bledy", uwagi)
        if zmiana:
            self.bledy.ustaw(list(uwagi))
        widoczne = bool(uwagi) and not self._bledy_zwiniete
        if self._z_tla and widoczne and (zmiana or self.bledy.isHidden()):  # lista pojawila sie albo zmienila w tle pod reka technika
            self._ochrona_bledow.start()
            self.bledy.chron(True)
        self.bledy.setVisible(widoczne)
        self.pasek_stanu.ustaw_bledy(len(uwagi), widoczne)

    def _polecenie_panelu(self, nazwa: str, argumenty: tuple) -> None:
        """Przycisk pozycji strefy pytan albo listy bledow: polecenie kontrolera albo czynnosc samego okna (``LOKALNE_*``)."""
        poprzednio, self._w_poleceniu = self._w_poleceniu, True  # to czynnosc technika - zmiana strefy po niej nie wlacza ochrony
        try:
            if nazwa == LOKALNE_NUMER_BEZ_ZMIAN and self.rano():
                self.ekran_rano.numer_podany()
                self._odswiez()
            elif nazwa == LOKALNE_NUMER_BEZ_ZMIAN:
                self._numer_dla = None
                self._odswiez()
            elif nazwa == LOKALNE_ZAMKNIJ_ODPOWIEDZ:
                self._odmowa = ""
                self._odswiez()
            elif nazwa == LOKALNE_ZAMKNIJ_INFORMACJE:
                self._informacja = ""
                self._odswiez()
            elif nazwa == LOKALNE_POKAZ_NOWA:
                self._pokaz_nowa()
            elif nazwa == "zamknij_komunikat" and len(argumenty) > 1:  # grupa jednakowych komunikatow zamykana w calosci, ekran raz (A-D4)
                self._wstrzymaj = True
                try:
                    for komunikat_id in argumenty:
                        self._polecenie(nazwa, komunikat_id)
                finally:
                    self._wstrzymaj = False
                stan = self.k.stan()
                if self._stan is None or stan.wersja > self._stan.wersja:
                    self.pokaz_stan(stan)
                else:
                    self._odswiez()
            elif nazwa == "zamknij_komunikat":
                for komunikat_id in argumenty:
                    self._polecenie(nazwa, komunikat_id)
            else:
                self._polecenie(nazwa, *argumenty)
        finally:
            self._w_poleceniu = poprzednio

    # --- obraz odchylek --------------------------------------------------------------------------
    def _odswiez_obraz(self, praca) -> None:
        if praca is None:
            self._obraz_dla = None
            return
        if praca.praca_id == self._obraz_dla:
            return
        self._obraz_dla = praca.praca_id
        gotowy = self.wczytywacz.obraz(praca.praca_id)
        if gotowy is not None:
            self.widok.obraz.ustaw_obraz(gotowy)
            return
        # w watku okna: odczyt z pamieci kontrolera i jedno zapytanie do bazy; nieudany obraz jest probowany ponownie przy
        # kolejnym otwarciu pracy (A-D8)
        szczegoly = self.k.szczegoly_pracy(praca.praca_id) if praca.gniazdo is not None else None
        if szczegoly is None or szczegoly.plik_podgladu is None:
            self.widok.obraz.ustaw_napis(N.OBRAZ_BRAK)
            return
        self.widok.obraz.ustaw_napis(N.OBRAZ_WCZYTYWANIE)
        self.wczytywacz.zlec(praca.praca_id, szczegoly.plik_podgladu, praca.gniazdo, szczegoly.ubytki)

    def _obraz_gotowy(self, klucz, obraz) -> None:
        if self._zamkniete or klucz != self._obraz_dla or not self.widok.otwarty():
            return
        if obraz is None:
            self.widok.obraz.ustaw_napis(N.OBRAZ_BRAK)
        else:
            self.widok.obraz.ustaw_obraz(obraz)
