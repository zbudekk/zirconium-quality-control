"""ekran_rano - ekran trybu "Poranek" programu "Stanowisko" (paczka E3-A7): piec z plytkami porannymi, rozstrzyganie prac
dwuznacznych, nieznanych i konfliktow, rozkladanie kuwet wedlug ekranu, "Zamknij piec" z lista zlecen kompletnych i brakow.

Ekran jest strona okna ``okno.OknoWieczor`` (ten sam pasek stanu, ta sama klawiatura i ten sam kontroler); okno pokazuje go,
gdy ``stan.tryb == "rano"``. Zasady jak na ekranie wieczornym (kontrakt ``kontroler_api``, wersja 3):
* ekran NICZEGO nie liczy - pokazuje ``stan.rano`` (``StanRano``) i wysyla polecenia przez okno (``okno._polecenie``);
  kolory i napisy statusow ze stanu i ``statusy``; bez sciezek i nazw plikow;
* panele (wybor osoby, pytania plytek porannych, komunikaty) nad plytkami, bledy programu na wlasnym pasku; prawa kolumna
  (rozkladanie kuwet i widok pracy / kompletne i braki) ma stale miejsce;
* plytki pieca obok siebie (do 3 w wierszu), w gniezdzie kuweta, zab i miniatura (``mapa_rano.MapaRano``); gniazda biezacej
  kuwety obwiedzione; po zmianie zestawu plytek mapy sa przez ``OCHRONA_MS`` przygaszone i nie przyjmuja klikniec;
* klawiatura jak na ramce porannej: cyfry (i "#") = numer kuwety, Enter = wybierz wpisana kuwete albo potwierdz biezaca
  ("rozlozona"), Backspace = popraw numer albo cofnij ostatnie potwierdzenie, Esc = wyczysc numer albo zamknij widok pracy;
  Spacja (start skanu) obsluguje okno.
Wlasny stan ekranu to wybor osoby: pokazana praca (plytka, gniazdo), strona prawej kolumny, wpisywany numer kuwety, otwarty
panel numeru plytki.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage
from PySide6.QtWidgets import (QAbstractItemView, QFrame, QGridLayout, QHBoxLayout, QHeaderView, QScrollArea, QSizePolicy, QStackedLayout,
                               QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

from .. import kontroler_api as K
from .. import statusy as ST
from . import napisy as N
from . import napisy_rano as NR
from . import styl
from .czesci import (ObszarPaneli, PanelOsoby, UkladPlynny, dzien, etykieta, godzina, panel_informacji, panel_komunikatu, panel_numeru, panel_odmowy,
                     panel_pytania, przycisk, wyczysc, znaczek)
from .kandydaci import WidokPracyRano, nazwa_plytki
from .mapa import geometria_ukladu
from .mapa_rano import MapaRano

PANELI = 3  # tyle pytan i komunikatow naraz (jak wieczorem)
OCHRONA_MS = 800  # po zmianie zestawu plytek klikniecia map sa pomijane (jak A-P2 wieczorem)
KOLUMN_PLYTEK = 3
KOLEJNOSC_KLAS = ("pewna", "przypisana", "dwuznaczna", "nieznana", "poprawka", "konflikt", "do_powtorzenia")
MAX_BUFORA = 7
PYTANE = {"brak_numeru_plytki": "podaj_numer_plytki", "plytka_nie_z_trybu": "dopusc_plytke"}


def blad_programu(komunikat) -> bool:
    return komunikat.poziom == ST.POZIOM_BLAD or komunikat.trwaly


def tabela(nazwa: str, kolumny: tuple, r: styl.Rozmiary) -> QTableWidget:
    t = QTableWidget(0, len(kolumny))
    t.setObjectName(nazwa)
    t.setHorizontalHeaderLabels(list(kolumny))
    t.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    t.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    t.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    t.verticalHeader().setVisible(False)
    t.verticalHeader().setDefaultSectionSize(r.wiersz_tabeli)
    t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    t.horizontalHeader().setSectionsClickable(False)
    t.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    t.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    return t


def wypelnij(t: QTableWidget, wiersze: list, r: styl.Rozmiary, widocznych: int = 6) -> None:
    """Wiersze tabeli (listy napisow); wysokosc tabeli = naglowek + do ``widocznych`` wierszy (reszta przewijana)."""
    t.setRowCount(len(wiersze))
    for i, komorki in enumerate(wiersze):
        for k, tekst in enumerate(komorki):
            pole = QTableWidgetItem(tekst)
            pole.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            t.setItem(i, k, pole)
    t.verticalHeader().setDefaultSectionSize(r.wiersz_tabeli)
    naglowek = r.naglowek_tabeli + (10 if r.zwarty else 16)
    t.setFixedHeight(naglowek + max(1, min(widocznych, len(wiersze))) * r.wiersz_tabeli + 4)
    t.clearSelection()


def teksty_tabeli(t: QTableWidget) -> list:
    return [[t.item(i, k).text() if t.item(i, k) is not None else "" for k in range(t.columnCount())] for i in range(t.rowCount())]


class KartaPlytki(QFrame):
    """Jedna plytka pieca: naglowek (numer, godzina skanu, polecenia plytki) i mapa ``MapaRano``."""

    def __init__(self, skan_id: int, ekran: "EkranRano"):
        super().__init__()
        self.setObjectName(f"rano_plytka_{skan_id}")
        self.setProperty("rola", "panel")
        self.skan_id = skan_id
        self._u = QVBoxLayout(self)
        wiersz = QHBoxLayout()
        wiersz.setSpacing(8)
        self.tytul = etykieta("", "naglowek", f"rano_plytka_{skan_id}_tytul", zawijaj=True)
        self.godzina = etykieta("", "slaby", f"rano_plytka_{skan_id}_godzina")
        wiersz.addWidget(self.tytul, 1)
        wiersz.addWidget(self.godzina, 0, Qt.AlignmentFlag.AlignTop)
        self._u.addLayout(wiersz)
        self.akcje = UkladPlynny(odstep_poziomy=6, odstep_pionowy=3)
        self._u.addLayout(self.akcje)
        self.mapa = MapaRano(skan_id)
        self.mapa.klik.connect(lambda nr: ekran._klik_gniazdo(skan_id, nr))
        self._u.addWidget(self.mapa, 1)
        self.poza = etykieta("", "slaby", f"rano_plytka_{skan_id}_poza")
        self.poza.setVisible(False)
        self._u.addWidget(self.poza)
        self._akcje_podpis = None
        self.ustaw_tryb(ekran._r)

    def ustaw_tryb(self, r: styl.Rozmiary) -> None:
        self._u.setContentsMargins(*((5, 3, 5, 4) if r.zwarty else (8, 6, 8, 6)))
        self._u.setSpacing(2 if r.zwarty else 4)
        self._akcje_podpis = None


class PanelKuwet(QFrame):
    """Rozkladanie kuwet: kolejnosc (od najliczniejszej / wedlug numeru), biezaca kuweta, wpisywany numer, "Rozlozona" /
    "Cofnij", lista kuwet pieca (klikniecie = wybor kuwety)."""

    def __init__(self, ekran: "EkranRano"):
        super().__init__()
        self.setObjectName("rano_kuwety")
        self.setProperty("rola", "panel")
        self.ekran = ekran
        self._u = u = QVBoxLayout(self)
        wiersz = QHBoxLayout()
        self.tytul = etykieta("", "naglowek", "rano_kuwety_tytul")
        wiersz.addWidget(self.tytul, 1)
        u.addLayout(wiersz)
        self.kolejnosc = UkladPlynny(odstep_poziomy=6, odstep_pionowy=4)
        self.przyciski_kolejnosci = {}
        for k in K.KOLEJNOSCI_KUWET:
            b = przycisk(ST.NAZWY_KOLEJNOSCI[k], f"kolejnosc_{k}", None, lambda k=k: ekran._polecenie("ustaw_kolejnosc", k))
            b.setCheckable(True)
            self.przyciski_kolejnosci[k] = b
            self.kolejnosc.addWidget(b)
        u.addLayout(self.kolejnosc)
        self.biezaca = etykieta("", "tytul", "rano_kuweta_biezaca", zawijaj=True)
        u.addWidget(self.biezaca)
        self.opis = etykieta("", "duzy", "rano_kuweta_opis", zawijaj=True)
        u.addWidget(self.opis)
        self.bufor = etykieta("", "uwaga", "rano_bufor", zawijaj=True)
        self.bufor.setVisible(False)
        u.addWidget(self.bufor)
        self.przyciski = UkladPlynny(odstep_poziomy=8, odstep_pionowy=4)
        self.potwierdz = przycisk(NR.POTWIERDZ_SKROT, "rano_potwierdz_kuwete", "glowny", lambda: ekran._polecenie("potwierdz_kuwete"))
        self.cofnij = przycisk(NR.COFNIJ_SKROT, "rano_cofnij_kuwete", None, lambda: ekran._polecenie("cofnij_kuwete"))
        self.przyciski.addWidget(self.potwierdz)
        self.przyciski.addWidget(self.cofnij)
        u.addLayout(self.przyciski)
        self.podpowiedz = etykieta(NR.KUWETY_PODPOWIEDZ, "slaby", "rano_kuwety_podpowiedz", zawijaj=True)
        u.addWidget(self.podpowiedz)
        self.tabela = tabela("tabela_kuwet", NR.KOLUMNY_KUWET, styl.ZWYKLE)
        self.tabela.cellClicked.connect(self._klik)
        u.addWidget(self.tabela)
        self._kuwety: tuple = ()
        self._r = styl.ZWYKLE
        self.ustaw_tryb(styl.ZWYKLE)

    def ustaw_tryb(self, r: styl.Rozmiary) -> None:
        self._r = r
        self._u.setContentsMargins(*((8, 4, 8, 5) if r.zwarty else (12, 8, 12, 10)))
        self._u.setSpacing(2 if r.zwarty else 5)
        for b in (self.potwierdz, self.cofnij, *self.przyciski_kolejnosci.values()):
            b.setMinimumHeight(r.wysokosc_przycisku)
        self.podpowiedz.setVisible(not r.zwarty)  # maly ekran: podpowiedz w komunikacie ramki i na przyciskach

    def ustaw(self, stan, bufor: str) -> None:
        rano = stan.rano
        jest_osoba = stan.operator is not None
        kuwety = rano.kuwety if rano is not None else ()
        self._kuwety = kuwety
        self.tytul.setText(NR.KUWETY_TYTUL.format(n=len(kuwety)))
        for k, b in self.przyciski_kolejnosci.items():
            b.setChecked(rano is not None and rano.kolejnosc == k)
        biezaca = next((x for x in kuwety if x.biezaca), None)
        if rano is None or rano.sesja_pieca_id is None or (not kuwety and rano.otwarty):
            self.biezaca.setText(NR.KUWETA_BRAK_PIECA)
            self.opis.setText("")
        elif biezaca is None:
            self.biezaca.setText(NR.KUWETA_BRAK if rano.otwarty else NR.PIEC_ZAMKNIETY_INFO)
            self.opis.setText("")
        else:
            self.biezaca.setText(NR.KUWETA_BIEZACA.format(kuweta=biezaca.kuweta))
            self.opis.setText(NR.KUWETA_BIEZACA_OPIS.format(prac=NR.KUWETA_PRAC.format(n=biezaca.prac),
                                                            plytki=NR.KUWETA_PLYTKI.format(lista=", ".join(map(str, biezaca.plytki)))))
        self.opis.setVisible(bool(self.opis.text()))
        self.bufor.setText(NR.BUFOR.format(bufor=bufor))
        self.bufor.setVisible(bool(bufor))
        otwarty = rano is not None and rano.otwarty
        self.potwierdz.setEnabled(otwarty and biezaca is not None and jest_osoba)
        self.cofnij.setEnabled(otwarty and any(x.potwierdzona for x in kuwety) and jest_osoba)
        wiersze = []
        for x in kuwety:
            stan_k = (NR.KUWETA_STAN_BIEZACA if x.biezaca else NR.KUWETA_STAN_ROZLOZONA if x.potwierdzona else
                      NR.KUWETA_STAN_BRAKI if x.braki else NR.KUWETA_STAN_CZEKA)
            wiersze.append([x.kuweta, str(x.prac), ", ".join(map(str, x.plytki)), stan_k])
        wypelnij(self.tabela, wiersze, self._r, widocznych=3 if self._r.zwarty else 6)  # reszta przewijana: miejsce na widok pracy
        indeks = next((i for i, x in enumerate(kuwety) if x.biezaca), None)
        if indeks is not None:
            self.tabela.selectRow(indeks)

    def _klik(self, wiersz: int, _kolumna: int) -> None:
        if 0 <= wiersz < len(self._kuwety):
            self.ekran._polecenie("wybierz_kuwete", self._kuwety[wiersz].kuweta)


class PanelWyniku(QScrollArea):
    """Zlecenia kompletne (do odhaczenia w Excelu) i braki pieca - prowizoryczne w otwartym piecu, z zapisu "Zamknij piec"
    w zamknietym; lista brakow ze wszystkich piecow; poprawki (tylko log)."""

    def __init__(self):
        super().__init__()
        self.setObjectName("rano_wynik")
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        wnetrze = QFrame()
        wnetrze.setObjectName("rano_wynik_wnetrze")
        wnetrze.setProperty("rola", "panel")
        self._u = u = QVBoxLayout(wnetrze)
        self.tytul = etykieta("", "naglowek", "rano_wynik_tytul", zawijaj=True)
        u.addWidget(self.tytul)
        self.kompletne_tytul = etykieta("", "duzy", "rano_kompletne_tytul", zawijaj=True)
        u.addWidget(self.kompletne_tytul)
        self.kompletne = tabela("tabela_kompletne", NR.KOLUMNY_KOMPLETNE, styl.ZWYKLE)
        u.addWidget(self.kompletne)
        self.braki_tytul = etykieta("", "duzy", "rano_braki_tytul", zawijaj=True)
        u.addWidget(self.braki_tytul)
        self.braki = tabela("tabela_braki", NR.KOLUMNY_BRAKI, styl.ZWYKLE)
        u.addWidget(self.braki)
        self.nierozstrzygniete = etykieta("", "uwaga", "rano_nierozstrzygniete", zawijaj=True)
        u.addWidget(self.nierozstrzygniete)
        self.poprawki = etykieta("", "informacja", "rano_poprawki", zawijaj=True)
        u.addWidget(self.poprawki)
        self.biezace_tytul = etykieta("", "duzy", "rano_braki_biezace_tytul", zawijaj=True)
        u.addWidget(self.biezace_tytul)
        self.biezace = tabela("tabela_braki_biezace", NR.KOLUMNY_BRAKI_BIEZACE, styl.ZWYKLE)
        u.addWidget(self.biezace)
        u.addStretch(1)
        self.setWidget(wnetrze)
        self._r = styl.ZWYKLE
        self._sygnatura = None

    def ustaw_tryb(self, r: styl.Rozmiary) -> None:
        self._r = r
        self._u.setContentsMargins(*((8, 4, 8, 5) if r.zwarty else (12, 8, 12, 10)))
        self._u.setSpacing(2 if r.zwarty else 5)
        self._sygnatura = None

    @staticmethod
    def _brakuje(z) -> str:
        return ", ".join(b.zeby or NR.BRAK_DANYCH for b in z.brakujace) or NR.LISTA_PUSTA

    @staticmethod
    def _stany(z) -> str:
        return ", ".join(dict.fromkeys(b.napis for b in z.brakujace)) or NR.LISTA_PUSTA

    def ustaw(self, rano) -> None:
        sygnatura = (rano, self._r.zwarty)
        if sygnatura == self._sygnatura:
            return
        self._sygnatura = sygnatura
        r = self._r
        if rano is None or rano.sesja_pieca_id is None:
            self.tytul.setText(NR.WYNIK_BRAK)
        elif rano.otwarty:
            self.tytul.setText(NR.WYNIK_TYTUL_OTWARTY.format(nr=rano.nr_w_dniu))
        else:
            self.tytul.setText(NR.WYNIK_TYTUL_ZAMKNIETY.format(nr=rano.nr_w_dniu, godzina=godzina(rano.zamknieto), osoba=rano.zamknal or NR.BRAK_DANYCH))
        kompletne = rano.kompletne if rano is not None else ()
        braki = rano.braki if rano is not None else ()
        self.kompletne_tytul.setText(NR.KOMPLETNE_TYTUL.format(n=len(kompletne)))
        wypelnij(self.kompletne, [[z.kuweta or NR.BRAK_DANYCH, NR.PUNKTY.format(rozpoznane=z.rozpoznane, punktow=z.punktow),
                                   NR.UWAGA_DOFREZOWANY if z.z_dofrezowaniem else ""] for z in kompletne], r)
        self.braki_tytul.setText(NR.BRAKI_TYTUL.format(n=len(braki)))
        wypelnij(self.braki, [[z.kuweta or NR.BRAK_DANYCH, self._brakuje(z), self._stany(z)] for z in braki], r)
        nier = rano.nierozstrzygniete if rano is not None else {}
        tekst = (NR.NIEROZSTRZYGNIETE.format(dwuznaczne=nier.get("dwuznaczne", 0), nieznane=nier.get("nieznane", 0))
                 if nier and (nier.get("dwuznaczne") or nier.get("nieznane")) else "")
        self.nierozstrzygniete.setText(tekst)
        self.nierozstrzygniete.setVisible(bool(tekst))
        poprawki = rano.poprawki if rano is not None else ()
        self.poprawki.setText(NR.POPRAWKI_TYTUL.format(lista=", ".join(f"{x.kuweta or NR.BRAK_DANYCH} ({NR.ZAB_KROTKO.format(zab=x.zeby or NR.BRAK_DANYCH)})"
                                                                     for x in poprawki)) if poprawki else "")
        self.poprawki.setVisible(bool(poprawki))
        biezace = rano.braki_biezace if rano is not None else ()
        self.biezace_tytul.setText(NR.BRAKI_BIEZACE_TYTUL.format(n=len(biezace)))
        wypelnij(self.biezace, [[z.kuweta or NR.BRAK_DANYCH, self._brakuje(z), self._stany(z), str(z.ostatni_piec or NR.BRAK_DANYCH)]
                                for z in biezace], r)


class EkranRano(QWidget):
    """Strona "Poranek" okna. ``okno`` - ``OknoWieczor`` (kontroler, polecenia, panele, rozmiary)."""

    def __init__(self, okno):
        super().__init__()
        self.setObjectName("ekran_rano")
        self.okno = okno
        self.k = okno.k
        self._r = styl.ZWYKLE
        self._stan = None
        self._wybor: tuple | None = None  # (skan_id, gniazdo) pokazanej pracy
        self._bufor = ""
        self._strona = "rozkladanie"
        self._numer_dla: int | None = None  # skan_id plytki z otwartym panelem numeru
        self._piec_widziany: tuple | None = None
        self._obrazy: dict = {}
        self._karty: dict[int, KartaPlytki] = {}
        self._sygnatury: dict = {}
        self._ochrona = QTimer(self)
        self._ochrona.setSingleShot(True)
        self._ochrona.setInterval(OCHRONA_MS)
        self._ochrona.timeout.connect(self._koniec_ochrony)
        self._zbuduj()

    # --- budowa ------------------------------------------------------------------------------------------------------
    def _zbuduj(self) -> None:
        self._korzen = korzen = QHBoxLayout(self)
        korzen.setContentsMargins(0, 0, 0, 0)
        korzen.setSpacing(10)
        self._lewa = lewa = QVBoxLayout()
        lewa.setSpacing(8)
        korzen.addLayout(lewa, 1)
        self.bledy = ObszarPaneli("rano_pasek_bledow", widocznych_min=2)
        self.bledy.setVisible(False)
        lewa.addWidget(self.bledy)
        self.uwagi = ObszarPaneli("rano_uwagi", widocznych_min=1)
        self.uwagi.setVisible(False)
        lewa.addWidget(self.uwagi)
        self.naglowek = naglowek = QFrame()
        naglowek.setObjectName("rano_naglowek_pieca")
        naglowek.setProperty("rola", "panel")
        self._naglowek_uklad = u = QHBoxLayout(naglowek)
        kolumna = QVBoxLayout()
        kolumna.setSpacing(2)
        self.tytul = etykieta("", "naglowek", "rano_piec_tytul", zawijaj=True)
        kolumna.addWidget(self.tytul)
        self._liczniki_widzet = QWidget()
        self._liczniki_widzet.setObjectName("rano_liczniki")
        self.liczniki = UkladPlynny(self._liczniki_widzet, odstep_poziomy=6, odstep_pionowy=3)
        kolumna.addWidget(self._liczniki_widzet)
        self.blokady = etykieta("", "uwaga", "rano_blokady", zawijaj=True)
        self.blokady.setVisible(False)
        kolumna.addWidget(self.blokady)
        u.addLayout(kolumna, 1)
        self.zamknij_piec = przycisk(ST.PRZYCISKI["zamknij_piec"], "przycisk_zamknij_piec", "glowny", lambda: self._polecenie("zamknij_piec"),
                                     styl.ZWYKLE.wysokosc_skanuj)
        u.addWidget(self.zamknij_piec, 0, Qt.AlignmentFlag.AlignVCenter)
        lewa.addWidget(naglowek)
        self.plytki = QWidget()
        self.plytki.setObjectName("rano_plytki")
        self.plytki.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._siatka = QGridLayout(self.plytki)
        self._siatka.setContentsMargins(0, 0, 0, 0)
        self._siatka.setSpacing(8)
        self.bez_plytek = etykieta(NR.PIEC_BRAK, "duzy", "rano_bez_plytek", zawijaj=True)
        self.bez_plytek.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._siatka.addWidget(self.bez_plytek, 0, 0)
        lewa.addWidget(self.plytki, 1)
        self.nieaktywne = etykieta("", "slaby", "rano_nieaktywne", zawijaj=True)
        self.nieaktywne.setVisible(False)
        lewa.addWidget(self.nieaktywne)
        self.legenda = QWidget()
        self.legenda.setObjectName("rano_legenda")
        self._legenda = UkladPlynny(self.legenda, odstep_poziomy=8, odstep_pionowy=4)
        lewa.addWidget(self.legenda)

        self.prawa = prawa = QWidget()
        prawa.setObjectName("rano_prawa_kolumna")
        prawa.setFixedWidth(styl.ZWYKLE.szerokosc_prawej)
        self._prawa_uklad = pu = QVBoxLayout(prawa)
        pu.setContentsMargins(0, 0, 0, 0)
        pu.setSpacing(8)
        self._strony_przyciski = UkladPlynny(odstep_poziomy=6, odstep_pionowy=4)
        self.przycisk_rozkladanie = przycisk(NR.STRONA_ROZKLADANIE, "rano_strona_rozkladanie", None, lambda: self._pokaz_strone("rozkladanie"))
        self.przycisk_wynik = przycisk(NR.STRONA_WYNIK, "rano_strona_wynik", None, lambda: self._pokaz_strone("wynik"))
        for b in (self.przycisk_rozkladanie, self.przycisk_wynik):
            b.setCheckable(True)
            self._strony_przyciski.addWidget(b)
        pu.addLayout(self._strony_przyciski)
        self._stos = QStackedLayout()
        strona = QWidget()
        strona.setObjectName("rano_strona_rozkladania")
        su = QVBoxLayout(strona)
        su.setContentsMargins(0, 0, 0, 0)
        su.setSpacing(8)
        self.kuwety = PanelKuwet(self)
        su.addWidget(self.kuwety)
        self.widok = WidokPracyRano(self.k.projekty_kuwety, self._obraz)
        self.widok.polecenie.connect(lambda nazwa, argumenty: self._polecenie(nazwa, *argumenty))
        self.widok.zamknij.connect(self._zamknij_prace)
        self.widok.po_zmianie(self._odswiez)
        su.addWidget(self.widok, 1)
        self._stos.addWidget(strona)
        self.wynik = PanelWyniku()
        self._stos.addWidget(self.wynik)
        pu.addLayout(self._stos, 1)
        korzen.addWidget(prawa)

    def ustaw_tryb(self, r: styl.Rozmiary) -> None:
        self._r = r
        self._korzen.setSpacing(r.odstep_kolumn)
        self._lewa.setSpacing(r.odstep)
        self._prawa_uklad.setSpacing(r.odstep)
        self.prawa.setFixedWidth(r.szerokosc_prawej)
        self._naglowek_uklad.setContentsMargins(*((8, 3, 8, 3) if r.zwarty else (12, 6, 12, 6)))
        self._siatka.setSpacing(r.odstep)
        self.zamknij_piec.setMinimumHeight(r.wysokosc_skanuj)
        for b in (self.przycisk_rozkladanie, self.przycisk_wynik):
            b.setMinimumHeight(r.wysokosc_przycisku)
        self.uwagi.uklad.setSpacing(4 if r.zwarty else 6)
        self.bledy.uklad.setSpacing(4 if r.zwarty else 6)
        for karta in self._karty.values():
            karta.ustaw_tryb(r)
        self.kuwety.ustaw_tryb(r)
        self.widok.ustaw_tryb(r)
        self.wynik.ustaw_tryb(r)
        self._sygnatury.clear()
        if self._stan is not None:
            self._odswiez()

    # --- stan --------------------------------------------------------------------------------------------------------
    def pokaz(self, stan) -> None:
        self._stan = stan
        rano = stan.rano
        piec = (rano.sesja_pieca_id, rano.otwarty) if rano is not None else None
        if piec != self._piec_widziany:  # piec zamkniety -> kompletne i braki; nowy piec -> rozkladanie
            if self._piec_widziany is not None and piec is not None:
                if piec[0] == self._piec_widziany[0] and not piec[1]:
                    self._strona = "wynik"
                elif piec[0] != self._piec_widziany[0] and piec[1]:
                    self._strona = "rozkladanie"
            self._piec_widziany = piec
        self._odswiez()

    def _obraz(self, sha16: str | None, dane: bytes | None):
        """``QImage`` miniatury (dekodowana raz na ``sha16``)."""
        if not sha16 or not dane:
            return None
        if sha16 not in self._obrazy:
            obraz = QImage.fromData(dane)
            self._obrazy[sha16] = None if obraz.isNull() else obraz
        return self._obrazy[sha16]

    def _zmienione(self, czesc: str, sygnatura) -> bool:
        if self._sygnatury.get(czesc) == sygnatura:
            return False
        self._sygnatury[czesc] = sygnatura
        return True

    def _plytki_widoczne(self, rano) -> list:
        """Plytki z mapa: wszystkie skany pieca poza zastapionymi, najpierw wg numeru plytki."""
        if rano is None:
            return []
        widoczne = [p for p in rano.plytki if p.status != "zastapiony"]
        return sorted(widoczne, key=lambda p: (p.numer is None, p.numer or 0, p.skan_id))

    def _wybor_pracy(self, rano):
        """(plytka, gniazdo, praca) pokazanej pracy wg stanu albo (None, None, None)."""
        if self._wybor is None or rano is None:
            return None, None, None
        plytka = rano.plytka(self._wybor[0])
        if plytka is None or plytka.status == "zastapiony":
            return None, None, None
        gniazdo = plytka.gniazdo(self._wybor[1])
        if gniazdo is None:
            return None, None, None
        return plytka, gniazdo, gniazdo.prace[0] if gniazdo.prace else None

    def _odswiez(self) -> None:
        stan = self._stan
        if stan is None:
            return
        rano = stan.rano
        plytka, gniazdo, praca = self._wybor_pracy(rano)
        if self._wybor is not None and plytka is None:  # plytki nie ma juz w stanie (zastapiona, nowy piec): widok pracy zamkniety
            self._wybor = None
            self.okno._informacja = N.PRACA_ZNIKNELA
        plytki = self._plytki_widoczne(rano)
        self._odswiez_karty(stan, rano, plytki)
        self._odswiez_naglowek(stan, rano)
        self._odswiez_uwagi(stan, rano)
        if plytka is None:
            self.widok.wyczysc()
        else:
            self.widok.ustaw(stan, plytka, gniazdo, praca, rano.otwarty)
        self.kuwety.ustaw(stan, self._bufor)
        self.wynik.ustaw(rano)
        self.przycisk_rozkladanie.setChecked(self._strona == "rozkladanie")
        self.przycisk_wynik.setChecked(self._strona == "wynik")
        self._stos.setCurrentIndex(0 if self._strona == "rozkladanie" else 1)

    def _odswiez_karty(self, stan, rano, plytki: list) -> None:
        zestaw = tuple(p.skan_id for p in plytki)
        if self._zmienione("zestaw", zestaw):
            stare = set(self._karty)
            wyczysc(self._siatka)
            self._karty = {}
            if not plytki:
                self.bez_plytek = etykieta(NR.PIEC_BRAK if rano is None or rano.sesja_pieca_id is None else NR.PIEC_ZAMKNIETY_INFO,
                                           "duzy", "rano_bez_plytek", zawijaj=True)
                self.bez_plytek.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self._siatka.addWidget(self.bez_plytek, 0, 0)
            kolumn = min(KOLUMN_PLYTEK, max(1, len(plytki)))
            for i, p in enumerate(plytki):
                karta = KartaPlytki(p.skan_id, self)
                self._karty[p.skan_id] = karta
                self._siatka.addWidget(karta, i // kolumn, i % kolumn)
            for k in range(KOLUMN_PLYTEK):
                self._siatka.setColumnStretch(k, 1 if k < kolumn else 0)
            if stare and stare != set(self._karty):  # inny zestaw plytek: mapy przesunely sie - klikniecie moglo celowac w poprzedni obraz
                self._ochrona.start()
                for karta in self._karty.values():
                    karta.mapa.przygas(True)
        biezaca = rano.kuweta_biezaca if rano is not None else None
        pytane = {(q.skan_id, PYTANE.get(q.rodzaj)) for q in stan.pytania if not q.ukryte}
        for p in plytki:
            karta = self._karty[p.skan_id]
            karta.tytul.setText(nazwa_plytki(p.numer) + ("" if p.aktywna else f" — {p.napis}"))
            karta.godzina.setText(NR.SKAN_Z.format(godzina=godzina(p.czas)) if p.czas else "")
            geometria = geometria_ukladu(self.k, p.uklad) if p.gniazda and (p.aktywna or p.prace) else None
            for pr in p.prace:
                for sha, dane in ((pr.sha16, pr.miniatura), *((k.sha16, k.miniatura) for k in pr.kandydaci)):
                    self._obraz(sha, dane)
            wybrane = self._wybor[1] if self._wybor is not None and self._wybor[0] == p.skan_id else None
            karta.mapa.ustaw_rano(p, geometria, wybrane, biezaca, self._obrazy)
            akcje = tuple(a for a in ("podaj_numer_plytki", "cofnij_zastapienie", "dopusc_plytke", "cofnij_dopuszczenie")
                          if a in p.dozwolone and (p.skan_id, a) not in pytane)
            podpis = (akcje, p.numer, stan.operator, self._r.zwarty)
            if podpis != karta._akcje_podpis:
                karta._akcje_podpis = podpis
                wyczysc(karta.akcje)
                for akcja in akcje:
                    napis = NR.ZMIEN_NUMER if akcja == "podaj_numer_plytki" and p.numer is not None else ST.PRZYCISKI[akcja]
                    if akcja == "podaj_numer_plytki":
                        b = przycisk(napis, f"rano_plytka_{p.skan_id}_{akcja}", "lacze", lambda s=p.skan_id: self._przelacz_numer(s))
                    else:
                        b = przycisk(napis, f"rano_plytka_{p.skan_id}_{akcja}", "lacze", lambda a=akcja, s=p.skan_id: self._polecenie(a, s))
                        b.setEnabled(stan.operator is not None)
                    karta.akcje.addWidget(b)
            karta.poza.setText(NR.POZA_GNIAZDAMI.format(n=len(p.poza_gniazdem)) if p.poza_gniazdem else "")
            karta.poza.setVisible(bool(p.poza_gniazdem))
        nieaktywne = [p for p in (rano.plytki if rano is not None else ()) if p.status == "zastapiony"]
        tekst = NR.PLYTKI_NIEAKTYWNE.format(lista="; ".join(NR.PLYTKA_NIEAKTYWNA.format(plytka=nazwa_plytki(p.numer), godzina=godzina(p.czas), napis=p.napis)
                                                           for p in nieaktywne)) if nieaktywne else ""
        self.nieaktywne.setText(tekst)
        self.nieaktywne.setVisible(bool(tekst))
        pozycje: dict = {}
        for p in plytki:
            for g in p.gniazda:
                if g.prace and g.status != "pusty":
                    w = ST.status(g.status)
                    pozycje.setdefault((w.napis, g.rgb), w.opis)
        if self._zmienione("legenda", (tuple(pozycje), self._r.zwarty)):
            wyczysc(self._legenda)
            if pozycje:
                self._legenda.addWidget(etykieta(NR.LEGENDA, "slaby"))
            for (napis, rgb), opis in pozycje.items():
                z = znaczek(napis, rgb, rozmiar_px=self._r.znaczek)
                z.setStyleSheet(z.styleSheet() + " border: 1px solid #3a4047;")
                z.setToolTip(opis)
                self._legenda.addWidget(z)

    def _odswiez_naglowek(self, stan, rano) -> None:
        if rano is None or rano.sesja_pieca_id is None:
            self.tytul.setText(NR.PIEC_BRAK)
        elif rano.otwarty:
            tytul = NR.PIEC_OTWARTY.format(nr=rano.nr_w_dniu, doba=dzien(rano.data), godzina=godzina(rano.otwarto))
            self.tytul.setText(tytul + (f" — {NR.PIEC_Z_WCZORAJ}" if rano.z_poprzedniej_doby else ""))
        else:
            self.tytul.setText(NR.PIEC_ZAMKNIETY.format(nr=rano.nr_w_dniu, doba=dzien(rano.data), godzina=godzina(rano.zamknieto),
                                                        osoba=rano.zamknal or NR.BRAK_DANYCH))
        liczniki = tuple((k, (rano.liczniki or {}).get(k, 0)) for k in KOLEJNOSC_KLAS) if rano is not None else ()
        if self._zmienione("liczniki", (liczniki, self._r.zwarty)):
            wyczysc(self.liczniki)
            for klasa, n in liczniki:
                if n:
                    w = ST.status_rano(klasa)
                    z = znaczek(NR.LICZNIK.format(napis=w.napis, n=n), w.hex, f"rano_licznik_{klasa}", rozmiar_px=self._r.znaczek)
                    z.setStyleSheet(z.styleSheet() + " border: 1px solid #3a4047;")
                    z.setToolTip(w.opis)
                    self.liczniki.addWidget(z)
            self._liczniki_widzet.updateGeometry()
        blokady = rano.blokady if rano is not None else ()
        self.blokady.setText(NR.BLOKADY_TYTUL + " " + " ".join(blokady) if blokady else "")
        self.blokady.setVisible(bool(blokady))
        self.zamknij_piec.setVisible(rano is not None and rano.otwarty)
        self.zamknij_piec.setEnabled(rano is not None and "zamknij_piec" in rano.dozwolone and stan.operator is not None)
        self.zamknij_piec.setToolTip(" ".join(blokady))

    def _odswiez_uwagi(self, stan, rano) -> None:
        r = self._r
        okno = self.okno
        pokaz_osobe = stan.wymaga_operatora or okno._zmiana_osoby
        skany_rano = {p.skan_id for p in rano.plytki} if rano is not None else set()
        wszystkie = [k for k in stan.komunikaty if not k.ukryte]
        if not stan.operatorzy:
            teksty = [ST.tekst_komunikatu("pusta_lista_operatorow")[2]]
        elif stan.wymaga_operatora:
            teksty = [k.tekst for k in wszystkie if k.rodzaj == "nowa_zmiana"][-1:] + [ST.tekst_komunikatu("brak_operatora")[2]]
        else:
            teksty = []
        pytania = [q for q in stan.pytania if not q.ukryte and q.skan_id in skany_rano]
        plytkowe = [k for k in wszystkie if k.skan_id is not None and k.skan_id in skany_rano]
        ogolne = [k for k in wszystkie if k.skan_id is None or stan.plytka(k.skan_id) is None and k.skan_id not in skany_rano]
        ogolne = [k for k in ogolne if not (pokaz_osobe and k.rodzaj in ("brak_operatora", "nowa_zmiana", "pusta_lista_operatorow", "osoba_spoza_listy"))]
        bledy = [k for k in ogolne if blad_programu(k)]
        reszta = [k for k in ogolne if not blad_programu(k)]
        if self._zmienione("bledy", (tuple(bledy), r.zwarty)):
            wyczysc(self.bledy.uklad)
            for k in bledy:
                panel = panel_komunikatu((k,), r=r)
                panel.polecenie.connect(okno._polecenie_panelu)
                self.bledy.uklad.addWidget(panel)
            self.bledy.odswiez()
        numer = None
        if self._numer_dla is not None and rano is not None:
            p = rano.plytka(self._numer_dla)
            if p is not None and "podaj_numer_plytki" in p.dozwolone and not any(q.rodzaj == "brak_numeru_plytki" and q.skan_id == p.skan_id for q in pytania):
                numer = p
            else:
                self._numer_dla = None
        sygnatura = (pokaz_osobe, okno._zmiana_osoby, stan.operator, stan.operatorzy, tuple(teksty), okno._odmowa, okno._informacja,
                     numer.skan_id if numer is not None else None, numer.numer if numer is not None else None, tuple(pytania), tuple(plytkowe),
                     tuple(reszta), tuple((p.skan_id, p.numer, p.typ) for p in (rano.plytki if rano is not None else ())), r.zwarty)
        if not self._zmienione("uwagi", sygnatura):
            return
        wyczysc(self.uwagi.uklad)
        if pokaz_osobe:
            panel = PanelOsoby(stan.operatorzy, stan.operator, teksty, zmiana_osoby=not stan.wymaga_operatora, r=r)
            panel.wybrano.connect(okno._wybrano_osobe)
            panel.bez_zmian.connect(okno._przelacz_zmiane_osoby)
            panel.wyloguj.connect(okno._wyloguj)
            self.uwagi.uklad.addWidget(panel)
        budowa = []
        if okno._informacja:
            budowa.append(lambda: panel_informacji(okno._informacja, r))
        if okno._odmowa:
            budowa.append(lambda: panel_odmowy(okno._odmowa, r))
        if numer is not None:
            geometria = geometria_ukladu(self.k, numer.uklad)
            numery = tuple(geometria.numery) if geometria is not None and geometria.numery else K.NUMERY_PLYTEK_ZAPASOWE
            brak = ST.tekst_komunikatu("brak_operatora" if stan.operatorzy else "pusta_lista_operatorow")[2]
            budowa.append(lambda: panel_numeru(numer.skan_id, numery, numer.numer, stan.operator is not None, brak, nazwa_plytki(numer.numer), r))
        for q in pytania:
            p = rano.plytka(q.skan_id)
            nazwa = nazwa_plytki(p.numer) if p is not None and p.numer is not None else ""
            budowa.append(lambda q=q, p=p, nazwa=nazwa: panel_pytania(q, stan, p.typ if p is not None else None, nazwa, r))
        for k in plytkowe:
            p = rano.plytka(k.skan_id)
            budowa.append(lambda k=k, p=p: panel_komunikatu((k,), nazwa_plytki(p.numer) if p is not None else "", r=r))
        budowa += [lambda k=k: panel_komunikatu((k,), r=r) for k in reversed(reszta)]
        for zbuduj in budowa[:PANELI]:
            panel = zbuduj()
            panel.polecenie.connect(okno._polecenie_panelu)
            self.uwagi.uklad.addWidget(panel)
        if len(budowa) > PANELI:
            self.uwagi.uklad.addWidget(etykieta(N.JESZCZE.format(n=len(budowa) - PANELI), "uwaga", "rano_uwagi_jeszcze", zawijaj=True))
        self.uwagi.odswiez()

    # --- wybor osoby ---------------------------------------------------------------------------------------------------
    def _polecenie(self, nazwa: str, *argumenty):
        return self.okno._polecenie(nazwa, *argumenty)

    def numer_podany(self) -> None:
        """Panel numeru plytki zamkniety (numer podany albo "Bez zmian")."""
        self._numer_dla = None

    def _pokaz_strone(self, strona: str) -> None:
        self._strona = strona
        self._odswiez()

    def _przelacz_numer(self, skan_id: int) -> None:
        self._numer_dla = None if self._numer_dla == skan_id else skan_id
        self._odswiez()

    def _klik_gniazdo(self, skan_id: int, nr: int) -> None:
        if self.ochrona_aktywna():
            return
        self._wybor = (skan_id, nr)
        self._strona = "rozkladanie"
        self._odswiez()

    def _zamknij_prace(self) -> None:
        self._wybor = None
        self._odswiez()

    def ochrona_aktywna(self) -> bool:
        return self._ochrona.isActive()

    def _koniec_ochrony(self) -> None:
        for karta in self._karty.values():
            karta.mapa.przygas(False)

    def pokazana_praca(self):
        """``PracaRano`` w widoku pracy (albo None)."""
        _, _, praca = self._wybor_pracy(self._stan.rano if self._stan is not None else None)
        return praca

    def mapy(self) -> dict:
        """skan_id -> ``MapaRano`` pokazanych plytek."""
        return {s: k.mapa for s, k in self._karty.items()}

    def bufor(self) -> str:
        return self._bufor

    # --- klawiatura (jak ramka poranna) ------------------------------------------------------------------------------
    def klawisz(self, zdarzenie) -> bool:
        """True = klawisz obsluzony przez ekran poranny. Cyfry / "#" = numer kuwety; Enter = wybierz wpisana kuwete albo
        potwierdz biezaca; Backspace = popraw numer albo cofnij ostatnie potwierdzenie; Esc = wyczysc numer albo zamknij prace."""
        klawisz = zdarzenie.key()
        tekst = zdarzenie.text()
        if tekst and (tekst.isdigit() or (tekst == "#" and not self._bufor)) and tekst.isascii():
            if len(self._bufor) < MAX_BUFORA:
                self._bufor += tekst
                self._odswiez()
            return True
        if zdarzenie.isAutoRepeat() and klawisz != Qt.Key.Key_Backspace:
            return klawisz in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Escape)
        if klawisz in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self._bufor:
                bufor, self._bufor = self._bufor, ""
                self._polecenie("wybierz_kuwete", bufor)
                self._odswiez()
            else:
                self._polecenie("potwierdz_kuwete")
            return True
        if klawisz == Qt.Key.Key_Backspace:
            if self._bufor:
                self._bufor = self._bufor[:-1]
                self._odswiez()
            elif not zdarzenie.isAutoRepeat():
                self._polecenie("cofnij_kuwete")
            return True
        if klawisz == Qt.Key.Key_Escape:
            if self._bufor:
                self._bufor = ""
                self._odswiez()
                return True
            if self._wybor is not None:
                self._zamknij_prace()
                return True
            return False
        return False
