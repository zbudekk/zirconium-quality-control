"""okno - okno trybu "Wieczor": sklada elementy ekranu, pokazuje ``kontroler.stan()`` i wysyla polecenia kontrolera.

Zasady (kontrakt ``kontroler_api`` / ``opisy_modulow/aplikacja.md``):
* okno NICZEGO nie liczy i nie siega do ``session`` / ``baza`` / ``scanner``; kolory i napisy statusow bierze ze stanu
  i ze ``statusy``; na ekranie nie ma sciezek ani nazw plikow (folder puli i skanera nie sa pokazywane);
* kazde polecenie idzie przez ``kontroler.wykonaj``; odmowa to ``Odpowiedz`` i komunikat w stanie - okno pokazuje go jak
  kazdy inny komunikat, nic nie rzuca;
* pytania i komunikaty sa panelami w oknie (nad mapa; prawa kolumna z przyciskami decyzji ma stale miejsce) - zadnych okien
  modalnych; stan o nizszej ``wersja`` niz pokazany jest pomijany;
* bledy programu (A-P3 recenzji PR #21): komunikaty poziomu "blad" i trwale, ktore nie dotycza plytki (``blad_zapisu``,
  ``folder_skanera_niedostepny``, pula, analiza ...), stoja na wlasnym pasku nad lista plytek i mapa, poza limitem
  ``PANELI`` (nie nad prawa kolumna - przyciski decyzji nie przesuwaja sie, gdy przychodzi blad);
* nowa plytka (A-P2): ekran przelacza sie sam TYLKO, gdy na pokazanej plytce nie ma pracy do obejrzenia (czerwonej / zoltej
  bez decyzji), nie ma otwartej pracy ani panelu numeru; inaczej kafelek dostaje "NOWA", nad lista plytek pojawia sie
  "Pokaz nowy wynik", a pasek stanu na chwile blyska (przelacza technik). Po kazdej zmianie zawartosci mapy (inna plytka,
  nowy stan spoza polecen technika) klikniecia mapy, Enter i skroty decyzji sa pomijane przez ``OCHRONA_MS`` (mapa
  przygaszona). Decyzja idzie zawsze do
  pracy, ktorej dane pokazuje widok pracy; gdy tej pracy nie ma juz w stanie albo gniazdo pokazuje inna prace - widok sie
  zamyka z informacja;
* wszystko dzieje sie w watku okna poza obrazem odchylek (``obraz.WczytywaczObrazow``); odswiezenie po sygnale stanu
  przebudowuje tylko te czesci ekranu, ktorych dane sie zmienily;
* klawiatura nalezy do okna: Spacja = "start skanu" (raz na nacisniecie), U / O / C = decyzje przy otwartej pracy,
  N = nastepna praca do obejrzenia, Esc = zamknij widok pracy, strzalki = kursor gniazda na mapie, Enter = otworz gniazdo
  pod kursorem; Tab przechodzi po przyciskach i kafelkach (Enter klika element z fokusem, Spacja - nigdy);
* uklad (A-P1): od ``styl.PROG_ZWARTEGO`` w dol uklad zwarty (``styl.ZWARTE``); najmniejsze okno ``styl.MINIMUM_OKNA``;
  okno startuje zawsze zmaksymalizowane (E3-A1p, ``okno_zmaksymalizowane``);
  przewijane sa tylko listy (plytki, "do dofrezowania") i obszary paneli, gdy paneli jest wiecej, niz sie miesci.

Wlasny stan okna to tylko wybor technika: pokazana plytka, wybrane gniazdo, kursor klawiatury, filtr listy, otwarty panel
numeru plytki albo zmiany osoby oraz tekst ostatniej odmowy / informacji ekranu, ktorej nie ma w komunikatach stanu.
"""
from __future__ import annotations

from PySide6.QtCore import QPoint, QRect, Qt, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QStackedLayout, QVBoxLayout, QWidget

from .. import kontroler_api as K
from .. import statusy as ST
from . import napisy as N
from . import styl
from .czesci import (LOKALNE_NUMER_BEZ_ZMIAN, LOKALNE_POKAZ_NOWA, LOKALNE_ZAMKNIJ_INFORMACJE, LOKALNE_ZAMKNIJ_ODPOWIEDZ, KafelekPlytki, Legenda,
                     ListaDofrezowania, ListaPlytek, ObszarPaneli, PanelOsoby, PasekStanu, UkladPlynny, WidokPracy, do_obejrzenia, dzien, etykieta,
                     godzina, napis_dopuszczenia, nazwa_plytki, panel_informacji, panel_komunikatu, panel_nowego_wyniku, panel_numeru, panel_odmowy,
                     panel_pytania, przycisk, sprawy_nowych_plytek, stan_obejrzenia, styl_znaczka_poziomu, wyczysc)
from .ekran_rano import EkranRano
from .mapa import MapaPlytki, geometria_ukladu
from .obraz import WczytywaczObrazow

SPRAWY_OSOBY = ("brak_operatora", "nowa_zmiana", "pusta_lista_operatorow", "osoba_spoza_listy")  # komunikaty pokazywane w panelu wyboru osoby
PANELI = 3  # tyle pytan i komunikatow naraz (pierwsze: pokazana plytka, potem ogolne od najnowszego); reszta czeka na zamkniecie
OCHRONA_MS = 800  # A-P2: tyle po zmianie zawartosci mapy klikniecia mapy i skroty decyzji sa pomijane
KONFLIKTOW_W_PANELU = 2  # tyle konfliktow projektu wypisanych z gniazdami w jednym panelu (reszta: "...")
UDZIAL_BLEDOW = 0.25  # pasek bledow programu zajmuje "na pewno" (dwa pierwsze bledy) najwyzej taka czesc wysokosci okna


def otwarte(pozycje) -> list:
    """Pytania / komunikaty do pokazania: bez pozycji zamknietych przez technika (``ukryte=True``, kontrakt w wersji 2 - D6).
    ``stan.pytania`` i ``stan.komunikaty`` sa juz otwarte; filtr chroni ekran, gdyby pozycja ukryta jednak tam trafila."""
    return [x for x in pozycje if not x.ukryte]


def okno_zmaksymalizowane(platforma: str) -> bool:
    """Czy okno startuje zmaksymalizowane: ZAWSZE na prawdziwym ekranie, niezaleznie od jego wielkosci i skalowania (decyzja
    wlasciciela 18.11.2026, E3-A1p: wczesniej tylko ekran mniejszy niz 1640 x 960 punktow, przy 100 % okno mialo 1600 x 900).
    Tryb offscreen (testy i zrzuty): nie - rozmiar ustawia wolajacy."""
    return platforma != "offscreen"


def blad_programu(komunikat) -> bool:
    """Komunikat na pasek bledow programu (A-P3): poziom "blad" albo trwaly (nie dotyczacy pokazanej plytki)."""
    return komunikat.poziom == ST.POZIOM_BLAD or komunikat.trwaly


def grupuj(komunikaty) -> list:
    """Jednakowe komunikaty (ten sam rodzaj, poziom, tytul i tekst) jako jedna grupa - jeden panel z licznikiem."""
    grupy: dict = {}
    for k in komunikaty:
        grupy.setdefault((k.rodzaj, k.poziom, k.tytul, k.tekst), []).append(k)
    return list(grupy.values())


class OknoWieczor(QWidget):
    def __init__(self, kontroler, lacznik):
        super().__init__()
        self.k = kontroler
        self.lacznik = lacznik
        self.setObjectName("okno_wieczor")
        self.setWindowTitle(N.TYTUL_OKNA)
        self._r = styl.ZWYKLE
        self.setStyleSheet(styl.arkusz(self._r))
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
        self._podaj_numer = False  # otwarty panel recznego numeru plytki
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
        self._w_poleceniu = False  # stan przychodzacy w trakcie polecenia technika = skutek jego decyzji (bez ochrony mapy)
        self._wstrzymaj = False  # seria polecen (zamkniecie grupy komunikatow): jedno odswiezenie ekranu na koniec
        self._zamkniete = False
        self._ochrona = QTimer(self)
        self._ochrona.setSingleShot(True)
        self._ochrona.setInterval(OCHRONA_MS)
        self._ochrona.timeout.connect(self._koniec_ochrony)
        self.wczytywacz = WczytywaczObrazow(self)
        self.wczytywacz.gotowy.connect(self._obraz_gotowy)
        self._zbuduj()
        self.setMinimumSize(*styl.MINIMUM_OKNA)
        self.resize(1600, 900)
        self._dopasuj_do_ekranu()
        lacznik.stan_zmieniony.connect(self._na_stan)
        lacznik.postep.connect(self._na_postep)
        lacznik.zamkniety.connect(self._na_zamkniety)
        self.pokaz_stan(kontroler.stan())

    def _dopasuj_do_ekranu(self) -> None:
        """Okno startuje zmaksymalizowane (``okno_zmaksymalizowane``); na mniejszym ekranie (laptop 1920 x 1080 ze skalowaniem
        125-150 %) uklad przechodzi sam na zwarty (``resizeEvent``)."""
        if okno_zmaksymalizowane(QGuiApplication.platformName()):
            self.setWindowState(self.windowState() | Qt.WindowState.WindowMaximized)

    # --- budowa ----------------------------------------------------------------------------------
    def _zbuduj(self) -> None:
        self._korzen = korzen = QVBoxLayout(self)
        korzen.setContentsMargins(10, 10, 10, 10)
        korzen.setSpacing(8)
        self.pasek = PasekStanu()
        self.pasek.skanuj.connect(self._start_skanu)
        self.pasek.odswiez_pule.connect(lambda: self._polecenie("odswiez_pule"))
        self.pasek.zmien_osobe.connect(self._przelacz_zmiane_osoby)
        self.pasek.przelacz_tryb.connect(self._przelacz_tryb)
        self.pasek.test_led.connect(lambda: self._polecenie("test_led"))  # E3-A12: ramki
        self.pasek.przejmij_ramke.connect(lambda rola: self._polecenie("przejmij_ramke", rola))
        korzen.addWidget(self.pasek)
        # E3-A7: dwie strony pod wspolnym paskiem - ekran wieczorny i poranny (``ekran_rano``); pokazana wg ``stan.tryb``
        self._strony = QStackedLayout()
        korzen.addLayout(self._strony, 1)
        self.strona_wieczor = QWidget()
        self.strona_wieczor.setObjectName("strona_wieczor")
        self._strony.addWidget(self.strona_wieczor)
        self._calosc = calosc = QHBoxLayout(self.strona_wieczor)
        calosc.setContentsMargins(0, 0, 0, 0)
        calosc.setSpacing(10)
        self._lewa = lewa = QVBoxLayout()
        lewa.setSpacing(8)
        calosc.addLayout(lewa, 1)
        # bledy programu: wlasny pasek nad lista plytek i mapa (A-P3), poza limitem paneli; co najmniej dwa pierwsze zawsze
        # w calosci, reszta przewijana. Nie nad prawa kolumna: przyciski decyzji nie przesuwaja sie, gdy przychodzi blad
        self.bledy = ObszarPaneli("pasek_bledow", widocznych_min=2)
        self.bledy.setVisible(False)
        lewa.addWidget(self.bledy)
        # wybor osoby, pytania i komunikaty: panele nad lista plytek i mapa; prawa kolumna (widok pracy z przyciskami decyzji
        # i lista) ma stale miejsce - przyciski nie przesuwaja sie, gdy przychodzi komunikat
        self.uwagi = ObszarPaneli("uwagi", widocznych_min=1)
        self.uwagi.setVisible(False)
        self._uwagi = self.uwagi.uklad
        lewa.addWidget(self.uwagi)
        self._srodek = srodek = QHBoxLayout()
        srodek.setSpacing(10)
        lewa.addLayout(srodek, 1)

        self.lista_plytek = ListaPlytek()
        self.lista_plytek.wybrano.connect(lambda skan_id: QTimer.singleShot(0, lambda: self._pokaz_plytke(skan_id)))
        self.lista_plytek.przelacz_wczesniejsze.connect(lambda: QTimer.singleShot(0, self._przelacz_wczesniejsze))
        self.lista_plytek.ponow_zapis.connect(lambda: QTimer.singleShot(0, lambda: self._polecenie("ponow_zapis")))
        self.lista_plytek.pokaz_nowa.connect(self._pokaz_nowa)
        srodek.addWidget(self.lista_plytek)

        self.kolumna = kolumna = QFrame()
        kolumna.setProperty("rola", "panel")
        kolumna.setObjectName("kolumna_mapy")
        self._kolumna_uklad = u = QVBoxLayout(kolumna)
        u.setContentsMargins(12, 8, 12, 8)
        u.setSpacing(6)
        wiersz = QHBoxLayout()
        wiersz.setSpacing(10)
        naglowek = QVBoxLayout()
        naglowek.setSpacing(0)
        self.naglowek = etykieta("", "tytul", "mapa_naglowek", zawijaj=True)
        naglowek.addWidget(self.naglowek)
        pod = UkladPlynny(odstep_poziomy=8, odstep_pionowy=2)  # napis i godzina skanu, znacznik dopuszczenia - w razie potrzeby w 2 wierszach
        self.podnaglowek = etykieta("", "slaby", "mapa_godzina")
        self.dopuszczenie = etykieta("", nazwa="plytka_dopuszczona")
        self.dopuszczenie.setStyleSheet(styl_znaczka_poziomu("ostrzezenie", self._r.znaczek))
        self.dopuszczenie.setVisible(False)
        pod.addWidget(self.podnaglowek)
        pod.addWidget(self.dopuszczenie)
        naglowek.addLayout(pod)
        wiersz.addLayout(naglowek, 1)
        self._akcje_plytki = UkladPlynny(odstep_poziomy=8, odstep_pionowy=4)
        wiersz.addLayout(self._akcje_plytki)
        u.addLayout(wiersz)
        self.mapa = MapaPlytki()
        self.mapa.klik.connect(self._klik_gniazdo)
        u.addWidget(self.mapa, 1)
        self.poza = QWidget()
        self.poza.setObjectName("poza_gniazdem")
        self._poza_uklad = UkladPlynny(self.poza, odstep_poziomy=8, odstep_pionowy=4)
        u.addWidget(self.poza)
        self.legenda = Legenda()
        u.addWidget(self.legenda)
        srodek.addWidget(kolumna, 1)

        self.prawa = prawa = QWidget()
        prawa.setObjectName("prawa_kolumna")
        prawa.setFixedWidth(styl.ZWYKLE.szerokosc_prawej)
        self._prawa_uklad = u = QVBoxLayout(prawa)
        u.setContentsMargins(0, 0, 0, 0)
        u.setSpacing(10)
        self.widok = WidokPracy()
        self.widok.decyzja.connect(self._decyzja)
        self.widok.wybor_wpisu.connect(self._wybor_wpisu)  # E3-A5i: krazek pracy do wyboru
        self.widok.cofnij_wpis.connect(self._cofnij_wpis)
        self.widok.zamknij.connect(self._zamknij_prace)
        self.widok.nastepna.connect(self._idz_do_nastepnej)
        self.widok.inna_praca.connect(self._inna_praca)
        u.addWidget(self.widok, 9)
        self.lista = ListaDofrezowania()
        self.lista.filtr.connect(self._ustaw_filtr)
        self.lista.wybrano.connect(self._klik_pozycja)
        self.lista.zapisz.connect(self._zapisz_liste)
        u.addWidget(self.lista, 4)
        calosc.addWidget(prawa)
        self.ekran_rano = EkranRano(self)
        self._strony.addWidget(self.ekran_rano)

    def _ustaw_tryb(self, zwarty: bool) -> None:
        """Uklad zwykly / zwarty (A-P1): czcionki pomocnicze, odstepy, wysokosci przyciskow, szerokosci kolumn, minimum mapy."""
        r = styl.rozmiary(zwarty)
        self._r = r
        self.setStyleSheet(styl.arkusz(r))
        self._korzen.setContentsMargins(r.margines, r.margines, r.margines, r.margines)
        self._korzen.setSpacing(r.odstep)
        self._calosc.setSpacing(r.odstep_kolumn)
        self._lewa.setSpacing(r.odstep)
        self._srodek.setSpacing(r.odstep_kolumn)
        self._prawa_uklad.setSpacing(r.odstep)
        self.uwagi.uklad.setSpacing(4 if zwarty else 6)
        self.bledy.uklad.setSpacing(4 if zwarty else 6)
        self._kolumna_uklad.setContentsMargins(*((8, 4, 8, 4) if zwarty else (12, 8, 12, 8)))
        self._kolumna_uklad.setSpacing(3 if zwarty else 6)
        self.prawa.setFixedWidth(r.szerokosc_prawej)
        self.mapa.setMinimumSize(*r.mapa_min)
        self.dopuszczenie.setStyleSheet(styl_znaczka_poziomu("ostrzezenie", r.znaczek))
        for czesc in (self.pasek, self.lista_plytek, self.widok, self.lista, self.legenda):
            czesc.ustaw_tryb(r)
        self.ekran_rano.ustaw_tryb(r)
        self._sygnatury.clear()
        self._odswiez()

    def resizeEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        super().resizeEvent(zdarzenie)
        self.bledy.ustaw_limit_minimum(int(self.height() * UDZIAL_BLEDOW))
        zwarty = self.width() < styl.PROG_ZWARTEGO[0] or self.height() < styl.PROG_ZWARTEGO[1]
        if zwarty != self._r.zwarty:
            self._ustaw_tryb(zwarty)

    def zwarty(self) -> bool:
        """Uklad zwarty (male okno) - do testow i kontroli."""
        return self._r.zwarty

    def rano(self) -> bool:
        """Pokazany ekran poranny (``stan.tryb == "rano"``, E3-A7)."""
        return self._strony.currentWidget() is self.ekran_rano

    def _przelacz_tryb(self) -> None:
        """Przelacznik trybu na pasku stanu: wieczor <-> rano (polecenie ``przelacz_tryb``; ekran zmienia sie ze stanem)."""
        if self._stan is not None:
            self._polecenie("przelacz_tryb", K.TRYB_WIECZOR if self._stan.tryb == K.TRYB_RANO else K.TRYB_RANO)

    # --- sygnaly kontrolera ----------------------------------------------------------------------
    def _na_stan(self, stan) -> None:
        self.pokaz_stan(stan)

    def _na_postep(self, _postep) -> None:
        """Postep analizy: zmienia sie tylko czesc "zywa" stanu - odswiezany jest sam pasek."""
        if self._zamkniete:
            return
        stan = self.k.stan()
        if self._stan is None or stan.wersja >= self._stan.wersja:
            if self._stan is not None and stan.plytki is not self._stan.plytki:
                self.pokaz_stan(stan)
            else:  # rano: zmiane blokady "Zamknij piec" (analiza / skanowanie) kontroler podaje pelnym stanem (recenzja PR #26, D1)
                self._stan = stan
                self.pasek.ustaw(stan)

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
        if rano != self.rano():  # E3-A7: zmiana trybu - druga strona okna; ekran wieczorny przebudowany od nowa po powrocie
            self._strony.setCurrentWidget(self.ekran_rano if rano else self.strona_wieczor)
            self._sygnatury.clear()
            self._mapa_podpis = None
            if not self._w_poleceniu:
                self.setFocus(Qt.FocusReason.OtherFocusReason)
        # E3-P15: stan, po ktorym mapa zmienia miejsce pod kursorem (komunikat nad mapa doszedl, urosl albo zniknal) - ta sama
        # ochrona klikniec co po zmianie zawartosci mapy (A-P2). Miara to RUCH mapy (runda 2, P1): jej prostokat w oknie
        # przed i po ulozeniu ukladu, nie wysokosc paneli - komunikat, ktory mapy nie rusza (sama zmiana tekstu, np. "plik
        # zajety od 13 s"; obszar paneli juz ograniczony i przewijany), mapy nie przygasza. Stan bedacy skutkiem polecenia
        # technika (runda 2, P2): ochrona tylko, gdy kolumna mapy zjechala w dol - nad mapa doszlo cos, o co nie prosil (np.
        # nieudany zapis listy po decyzji); komunikat zamkniety jego kliknieciem (mapa idzie w gore) zostaje bez przygaszenia
        klikalna = self._mapa_podpis is not None and bool(self._mapa_podpis[1] or self._mapa_podpis[2])
        przed = self._miejsce_mapy() if klikalna else None
        self._odswiez()
        if klikalna:
            self._calosc.activate()  # uklad policzony od razu (bez czekania na obieg petli okna): miejsce mapy po wymianie paneli
            po = self._miejsce_mapy()
            if po[1] > przed[1] if self._w_poleceniu else po[0] != przed[0]:
                self._ochrona.start()
                self.mapa.przygas(True)

    def _miejsce_mapy(self) -> tuple:
        """(prostokat mapy w oknie, gorna krawedz kolumny mapy) - to, co technik ma pod kursorem."""
        return QRect(self.mapa.mapTo(self, QPoint(0, 0)), self.mapa.size()), self.kolumna.y()

    def pokazana_plytka(self) -> int | None:
        """``skan_id`` plytki, ktorej mapa jest na ekranie."""
        return self._plytka_id

    def ochrona_aktywna(self) -> bool:
        """Mapa przygaszona po zmianie zawartosci (A-P2): klikniecia mapy, Enter i skroty decyzji sa pomijane."""
        return self._ochrona.isActive()

    # --- wybor plytki i pracy ----------------------------------------------------------------------
    def _wybierz_plytke(self, stan) -> None:
        numery = [p.skan_id for p in stan.plytki]
        nowe = [i for i in numery if i not in self._znane]
        self._znane.update(numery)
        self._nieobejrzane &= set(numery)
        if self._plytka_id is not None and self._plytka_id not in numery:
            if self._gniazdo is not None or self._poza is not None:
                self._informacja = N.PRACA_ZNIKNELA
            self._plytka_id, self._gniazdo, self._poza, self._podaj_numer, self._praca_widoku = None, None, None, False, None
        if nowe and not self._pierwszy_stan:
            if self._mozna_przelaczyc(stan):
                self._plytka_id, self._podaj_numer = nowe[-1], False
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
        if self._zmiana_osoby and stan.wymaga_operatora:
            self._zmiana_osoby = False

    def _mozna_przelaczyc(self, stan) -> bool:
        """Nowa plytka moze zajac ekran sama tylko wtedy, gdy technik nie ma otwartej pracy ani panelu numeru, a na pokazanej
        plytce nie zostala praca do obejrzenia (czerwona / zolta bez decyzji) - A-P2."""
        if self._gniazdo is not None or self._poza is not None or self._podaj_numer:
            return False
        plytka = stan.plytka(self._plytka_id) if self._plytka_id is not None else None
        return plytka is None or not do_obejrzenia(plytka)

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

    def _pokaz_plytke(self, skan_id: int, gniazdo: int | None = None, poza: int | None = None) -> None:
        if self._stan is None or self._stan.plytka(skan_id) is None:
            return
        self._plytka_id, self._gniazdo, self._poza, self._nr_pracy, self._podaj_numer = skan_id, gniazdo, poza, 0, False
        self._praca_widoku = None
        self._nieobejrzane.discard(skan_id)
        # E3-P14 (N2): pokazana plytka pyta "ponowny skan?" o swoj poprzedni skan - ten tez przestaje byc "nowym wynikiem"
        self._nieobejrzane.discard(self._stan.plytka(skan_id).moze_zastapic)
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
        """Klikniecie pozycji listy "do dofrezowania": pokazuje te prace, jesli jej plytka jest w stanie tej doby; inaczej
        krotka informacja, skad jest ta praca (A-D9)."""
        self.setFocus(Qt.FocusReason.MouseFocusReason)
        if self._stan is None:
            return
        if self._stan.plytka(pozycja.skan_id) is None:
            self._informacja = N.POZYCJA_Z_INNEJ_DOBY.format(doba=dzien(pozycja.doba, rok=True), zmiana=pozycja.zmiana)
            self._odswiez()
            return
        skan_id, gniazdo = pozycja.skan_id, pozycja.gniazdo
        poza = pozycja.praca_id if gniazdo is None else None
        QTimer.singleShot(0, lambda: self._pokaz_plytke(skan_id, gniazdo, poza))

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

    # --- polecenia -------------------------------------------------------------------------------
    def _polecenie(self, nazwa: str, *argumenty):
        """Polecenie do kontrolera. Odmowa wraca jako ``Odpowiedz`` (nie wyjatek): zwykle jest tez komunikatem w stanie i ekran
        pokazuje go po odswiezeniu; gdy stan jej nie zawiera (np. ``zle_argumenty``), okno pokazuje tekst odpowiedzi samo.
        Stan, ktory przychodzi w trakcie polecenia, jest skutkiem decyzji technika - mapa nie jest wtedy przygaszana."""
        if self._zamkniete or self._stan is None or self._stan.zamkniety:
            return None
        self._w_poleceniu = True
        try:
            odpowiedz = self.k.wykonaj(nazwa, *argumenty)  # kontrakt: polecenia nie rzucaja wyjatkow (zle dane = odmowa ``zle_argumenty``)
            stan = self.k.stan()
            tekst = odpowiedz.tekst if not odpowiedz.ok else ""
            # odmowa, ktora jest juz w stanie jako komunikat albo pytanie (rano: "zmienic numer mimo to?"), nie jest powtarzana
            w_stanie = any(k.tekst == tekst for k in otwarte(stan.komunikaty)) or any(q.tekst == tekst for q in stan.pytania)
            self._odmowa = tekst if tekst and not w_stanie else ""
            self._informacja = ""
            if nazwa == "podaj_numer_plytki" and (odpowiedz.ok or odpowiedz.kod == "numer_nowy_wsad"):
                self._podaj_numer = False  # rano "numer_nowy_wsad": panel numeru ustepuje pytaniu "zmienic numer mimo to?" (A6 runda 4)
                self.ekran_rano.numer_podany()
            if stan.wersja == self._stan.wersja:
                if not self._wstrzymaj:
                    self._odswiez()  # polecenie bez nowego stanu (odmowa bez komunikatu): pokaz tekst odpowiedzi
            else:
                self.pokaz_stan(stan)
        finally:
            self._w_poleceniu = False
        return odpowiedz

    def _start_skanu(self) -> None:
        self._polecenie("start_skanu")

    def _decyzja(self, nazwa: str) -> None:
        """Decyzja dla pracy, ktorej dane pokazuje widok pracy (A-P2): tylko gdy wybor technika wskazuje dokladnie te prace."""
        if not self.widok.aktywny(nazwa):
            return
        _, praca = self._wybor()
        if praca is None or self._praca_widoku is None or praca.praca_id != self._praca_widoku or self.widok.praca_id != self._praca_widoku:
            return
        self._polecenie(nazwa, self._praca_widoku)

    def _wybor_wpisu(self, frezowanie_id: int) -> None:
        """E3-A5i: krazek wskazany przez technika dla pracy pokazanej w widoku pracy (tylko gdy widok pokazuje wybrana prace)."""
        _, praca = self._wybor()
        if praca is None or self._praca_widoku is None or praca.praca_id != self._praca_widoku or self.widok.praca_id != self._praca_widoku:
            return
        self._polecenie("wybierz_wpis", self._praca_widoku, int(frezowanie_id))

    def _cofnij_wpis(self) -> None:
        _, praca = self._wybor()
        if praca is None or self._praca_widoku is None or praca.praca_id != self._praca_widoku or self.widok.praca_id != self._praca_widoku:
            return
        if praca.wybor_wpisu_id is not None:  # runda 3 (D6): dokladnie pokazany wybor - podwojne klikniecie nie cofa drugiego
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
        self._podaj_numer = not self._podaj_numer
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
            else:
                super().keyPressEvent(zdarzenie)
            return
        kierunek ={Qt.Key.Key_Left: (-1, 0), Qt.Key.Key_Right: (1, 0), Qt.Key.Key_Up: (0, -1), Qt.Key.Key_Down: (0, 1)}
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

    def closeEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        """Okno odlacza sie od lacznika i konczy watek obrazow; kontroler zamyka ``aplikacja.main()``."""
        if not self._zamkniete:
            self._zamkniete = True
            self._ochrona.stop()
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
        self.pasek.ustaw(stan)
        if self.rano():  # E3-A7: ekran poranny pokazuje sam swoje czesci; wieczorny (niewidoczny) nie jest przebudowywany
            self.ekran_rano.pokaz(stan)
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
        # E3-P14 (poz. 8): skan, ktory otwarte pytanie "ponowny skan?" proponuje zastapic - kafelek "poprzedni skan tej plytki"
        poprzednie = {q.poprzedni_id for q in otwarte(stan.pytania) if q.rodzaj == "ponowny_skan" and q.poprzedni_id is not None}
        self.lista_plytek.ustaw(widoczne, self._plytka_id, self._nieobejrzane, {q.skan_id for q in otwarte(stan.pytania)}, wczesniejszych,
                                self._pokaz_wczesniejsze, stan.niezapisane, z_komunikatem, poprzednie)
        nowe = [p for p in stan.plytki if p.skan_id in self._nieobejrzane]
        self.lista_plytek.ustaw_nowe(nazwa_plytki(nowe[-1].numer) if nowe else None, len(nowe))
        # E3-P14 (N2): wynik nowej plytki czeka, ekran zostal na ogladanej - trwaly panel z jej pytaniami i komunikatami.
        # Runda 2 (P3): w kolumnie plytek, nie nad mapa - mapa ogladanej plytki nie zmienia polozenia ani rozmiaru
        sprawy = sprawy_nowych_plytek(stan, nowe)
        if self._zmienione("nowy_wynik", (sprawy, self._r.zwarty)):
            self.lista_plytek.ustaw_panel_nowego(panel_nowego_wyniku(sprawy, self._r) if sprawy else None)
        if self._blysk_nowej and nowe:
            self.pasek.blysk()  # krotki sygnal na pasku: przyszedl wynik, ekran zostaje na pokazanej plytce
        self._blysk_nowej = False
        geometria = geometria_ukladu(self.k, plytka.uklad) if plytka is not None and plytka.gniazda and (plytka.aktywna or plytka.prace) else None
        self._sprawdz_zmiane_mapy(plytka)
        if plytka is None or self._kursor not in {g.nr for g in plytka.gniazda}:
            self._kursor = None
        self.mapa.ustaw(plytka, geometria, self._gniazdo)
        self.mapa.ustaw_kursor(self._kursor)
        self._odswiez_naglowek(stan, plytka)
        self.legenda.ustaw(plytka)
        self._odswiez_uwagi(stan, plytka)
        if gniazdo is None and praca is None:
            self.widok.wyczysc()
            self._obraz_dla = None
        else:
            self.widok.ustaw(stan, plytka, gniazdo, praca, self._nr_pracy, self._nastepna(plytka) is not None)
            self._odswiez_obraz(praca)
        self.lista.ustaw(stan.do_dofrezowania_biezaca if self._lista_wszystkie else stan.do_dofrezowania, self._lista_wszystkie,
                         stan.lista_zapisana)
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
            self._ochrona.start()
            self.mapa.przygas(True)

    def _koniec_ochrony(self) -> None:
        self.mapa.przygas(False)

    def _porzadek_tabulacji(self) -> None:
        """Kolejnosc klawisza Tab: pasek, bledy programu, panele, plytki, przyciski plytki i mapy, widok pracy, lista."""
        kolejne = []
        for sekcja in (self.pasek, self.bledy, self.uwagi, self.lista_plytek, self.kolumna, self.widok, self.lista):
            kolejne += [w for w in sekcja.findChildren(QWidget)
                        if isinstance(w, (QPushButton, KafelekPlytki)) and w.focusPolicy() == Qt.FocusPolicy.TabFocus]
        podpis = tuple(id(w) for w in kolejne)
        if podpis == self._tab_podpis:
            return
        self._tab_podpis = podpis
        for a, b in zip(kolejne, kolejne[1:]):
            QWidget.setTabOrder(a, b)

    def _odswiez_naglowek(self, stan, plytka) -> None:
        if plytka is None:
            self.naglowek.setText("")
            self.podnaglowek.setText("")
            self.dopuszczenie.setVisible(False)
        else:
            napis = stan_obejrzenia(plytka)  # "do obejrzenia: n" / "sprawdzona" albo napis ze stanu
            self.naglowek.setText(N.MAPA_NAGLOWEK.format(plytka=nazwa_plytki(plytka.numer), napis=napis))
            czas = godzina(plytka.czas)
            if napis != plytka.napis:
                self.podnaglowek.setText(N.MAPA_NAPIS_I_GODZINA.format(napis=plytka.napis, godzina=czas) if czas else plytka.napis)
            else:
                self.podnaglowek.setText(N.MAPA_GODZINA.format(godzina=czas) if czas else "")
            dopuszczenie = napis_dopuszczenia(plytka)  # plytka poranna dopuszczona swiadomie: staly znacznik (A-P5 poz. 5)
            self.dopuszczenie.setText(dopuszczenie)
            self.dopuszczenie.setVisible(bool(dopuszczenie))
        # polecenia plytki ze stanu (``Plytka.dozwolone``); te, o ktore wlasnie pyta otwarte pytanie, sa tylko w panelu pytania
        pytane = {"brak_numeru_plytki": "podaj_numer_plytki", "plytka_nie_z_trybu": "dopusc_plytke"}
        w_pytaniach = {pytane.get(q.rodzaj) for q in otwarte(stan.pytania) if plytka is not None and q.skan_id == plytka.skan_id}
        akcje = tuple(a for a in ("podaj_numer_plytki", "dopusc_plytke", "cofnij_zastapienie", "cofnij_dopuszczenie")
                      if plytka is not None and a in plytka.dozwolone and a not in w_pytaniach and a in ST.PRZYCISKI)
        if self._zmienione("akcje", (plytka.skan_id if plytka else None, plytka.numer if plytka else None, akcje, stan.operator)):
            wyczysc(self._akcje_plytki)
            for akcja in akcje:
                if akcja == "podaj_numer_plytki" and plytka.numer is None:  # numer wybiera sie w panelu z cyframi
                    b = przycisk(ST.PRZYCISKI[akcja], f"plytka_{akcja}", "lacze", self._przelacz_numer)
                elif akcja == "podaj_numer_plytki":  # plytka ma numer: maly przycisk "Zmien numer" (A-P5 poz. 2)
                    b = przycisk(N.ZMIEN_NUMER, f"plytka_{akcja}", "lacze", self._przelacz_numer)
                    b.setStyleSheet(f"font-size: {self._r.slaby}px; font-weight: 600; padding: 1px 6px;")
                else:
                    b = przycisk(ST.PRZYCISKI[akcja], f"plytka_{akcja}", "lacze", lambda a=akcja, s=plytka.skan_id: self._polecenie(a, s))
                    b.setEnabled(stan.operator is not None)
                self._akcje_plytki.addWidget(b)
        poza = plytka.poza_gniazdem if plytka is not None else ()
        if self._zmienione("poza", (poza, self._poza)):
            wyczysc(self._poza_uklad)
            if poza:
                self._poza_uklad.addWidget(etykieta(N.POZA_GNIAZDEM.format(n=len(poza)), "slaby"))
                for i, p in enumerate(poza):
                    b = przycisk(p.podpis, f"poza_{i}", None, lambda praca_id=p.praca_id: self._klik_poza(praca_id))
                    b.setStyleSheet(f"background: {p.rgb}; color: {styl.tekst_na(p.rgb)}; border: {'4' if p.praca_id == self._poza else '1'}px solid #101418; "
                                    f"border-radius: 6px; padding: {'2px 8px' if self._r.zwarty else '4px 12px'}; font-size: {self._r.lacze}px; "
                                    "font-weight: 700;")
                    self._poza_uklad.addWidget(b)
        self.poza.setVisible(bool(poza))

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

    def _odswiez_uwagi(self, stan, plytka) -> None:
        """Nad lista plytek i mapa: pasek bledow programu (A-P3, wlasne miejsce poza limitem) i pod nim panele: wybor osoby, informacja
        ekranu, tekst odmowy spoza stanu, reczny numer plytki, otwarte pytania pokazanej plytki (``stan.pytania``), jej
        komunikaty i pozostale komunikaty ogolne (od najnowszego; jednakowe razem; najwyzej ``PANELI``)."""
        r = self._r
        pokaz_osobe = stan.wymaga_operatora or self._zmiana_osoby
        wszystkie = otwarte(stan.komunikaty)  # pozycje ukryte przez technika (``ukryte``) nie wracaja na ekran
        if not stan.operatorzy:
            teksty = [ST.tekst_komunikatu("pusta_lista_operatorow")[2]]
        elif stan.wymaga_operatora:
            teksty = [k.tekst for k in wszystkie if k.rodzaj == "nowa_zmiana"][-1:] + [ST.tekst_komunikatu("brak_operatora")[2]]
        else:
            teksty = []
        pytania = [q for q in otwarte(stan.pytania) if plytka is not None and q.skan_id == plytka.skan_id]
        komunikaty = [k for k in wszystkie if plytka is not None and k.skan_id == plytka.skan_id]
        numer = (plytka is not None and self._podaj_numer and "podaj_numer_plytki" in plytka.dozwolone
                 and not any(q.rodzaj == "brak_numeru_plytki" for q in pytania))
        ogolne = [k for k in wszystkie
                  if (k.skan_id is None or stan.plytka(k.skan_id) is None) and not (pokaz_osobe and k.rodzaj in SPRAWY_OSOBY)]
        ogolne.sort(key=lambda k: (0 if k.poziom == ST.POZIOM_BLAD else 1, -self._nr_komunikatow.get(k.id, 0)))  # od najnowszego
        self._odswiez_bledy(stan, [k for k in ogolne if blad_programu(k)])
        reszta = [k for k in ogolne if not blad_programu(k)]
        sygnatura = (pokaz_osobe, self._zmiana_osoby, stan.operator, stan.operatorzy, tuple(teksty), self._odmowa, self._informacja, numer,
                     plytka.skan_id if plytka else None, plytka.numer if plytka else None, plytka.typ if plytka else None,
                     tuple(pytania), tuple(komunikaty), tuple(reszta))
        if not self._zmienione("uwagi", sygnatura):
            return
        wyczysc(self.uwagi.uklad)
        if pokaz_osobe:
            panel = PanelOsoby(stan.operatorzy, stan.operator, teksty, zmiana_osoby=not stan.wymaga_operatora, r=r)
            panel.wybrano.connect(self._wybrano_osobe)
            panel.bez_zmian.connect(self._przelacz_zmiane_osoby)
            panel.wyloguj.connect(self._wyloguj)
            self.uwagi.uklad.addWidget(panel)
        nazwa = nazwa_plytki(plytka.numer) if plytka is not None else ""
        nazwa_pytan = nazwa if plytka is not None and plytka.numer is not None else ""  # "Plytka bez numeru: Podaj numer..." - bez przedrostka
        budowa = []  # funkcje budujace panele, w kolejnosci waznosci
        if self._informacja:
            budowa.append(lambda: panel_informacji(self._informacja, r))
        if self._odmowa:
            budowa.append(lambda: panel_odmowy(self._odmowa, r))
        if numer:
            geometria = geometria_ukladu(self.k, plytka.uklad)
            numery = tuple(geometria.numery) if geometria is not None and geometria.numery else K.NUMERY_PLYTEK_ZAPASOWE
            brak = ST.tekst_komunikatu("brak_operatora" if stan.operatorzy else "pusta_lista_operatorow")[2]
            budowa.append(lambda: panel_numeru(plytka.skan_id, numery, plytka.numer, stan.operator is not None, brak, nazwa, r))
        budowa += [lambda q=q: panel_pytania(q, stan, plytka.typ, nazwa if q.rodzaj != "brak_numeru_plytki" else nazwa_pytan, r) for q in pytania]
        budowa += [lambda k=k: panel_komunikatu((k,), nazwa, r=r) for k in komunikaty]
        budowa += [lambda g=g: panel_komunikatu(tuple(g), dodatek=self._dopisek_konfliktu(stan, g), r=r) for g in grupuj(reszta)]
        for zbuduj in budowa[:PANELI]:
            panel = zbuduj()
            panel.polecenie.connect(self._polecenie_panelu)
            self.uwagi.uklad.addWidget(panel)
        if len(budowa) > PANELI:
            self.uwagi.uklad.addWidget(etykieta(N.JESZCZE.format(n=len(budowa) - PANELI), "uwaga", "uwagi_jeszcze", zawijaj=True))
        self.uwagi.odswiez()

    def _odswiez_bledy(self, stan, bledy: list) -> None:
        """Pasek bledow programu nad calym ekranem (A-P3): bledy pierwsze, potem trwale; jednakowe razem; bez limitu paneli."""
        grupy = grupuj(bledy)
        dopiski = tuple(self._dopisek_konfliktu(stan, g) for g in grupy)
        if not self._zmienione("bledy", (tuple(bledy), dopiski)):
            return
        wyczysc(self.bledy.uklad)
        for grupa, dopisek in zip(grupy, dopiski):
            panel = panel_komunikatu(tuple(grupa), dodatek=dopisek, r=self._r)
            panel.polecenie.connect(self._polecenie_panelu)
            self.bledy.uklad.addWidget(panel)
        self.bledy.odswiez()

    def _polecenie_panelu(self, nazwa: str, argumenty: tuple) -> None:
        if nazwa == LOKALNE_NUMER_BEZ_ZMIAN and self.rano():
            self.ekran_rano.numer_podany()
            self._odswiez()
        elif nazwa == LOKALNE_NUMER_BEZ_ZMIAN:
            self._przelacz_numer()
        elif nazwa == LOKALNE_ZAMKNIJ_ODPOWIEDZ:
            self._odmowa = ""
            self._odswiez()
        elif nazwa == LOKALNE_ZAMKNIJ_INFORMACJE:
            self._informacja = ""
            self._odswiez()
        elif nazwa == LOKALNE_POKAZ_NOWA:
            self._pokaz_nowa()
        elif nazwa == "zamknij_komunikat" and len(argumenty) > 1:  # panel jednakowych komunikatow zamyka je wszystkie, ekran raz (A-D4)
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
