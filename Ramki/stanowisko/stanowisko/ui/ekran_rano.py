"""ekran_rano - tryb "Poranek" okna programu "Stanowisko" w nowym ukladzie (paczka E3-U1b; ``etap3/nowy_interfejs/SPEC.md``
p. 3, makieta ``Rano.dc.html``): piec z plytkami porannymi, rozstrzyganie prac dwuznacznych, nieznanych i konfliktow,
rozkladanie kuwet wedlug ekranu, "Zamknij piec" z lista zlecen kompletnych i brakow, okno "Excel: wskaz wiersz".

Ekran jest strona okna ``okno.OknoStanowiska`` miedzy paskiem gornym a paskiem stanu (te same paski, ta sama klawiatura, ten
sam kontroler, ta sama lista bledow programu); okno pokazuje go, gdy ``stan.tryb == "rano"``. Uklad (jak wieczorem):
1. lewa kolumna "Piec n" (``PanelPieca``): opis pieca, kafelki plytek pieca (numer, godzina, liczba prac, ile bez
   rozstrzygniecia, liczniki klas, polecenia plytki), legenda "Na plytkach", na dole "Do zamkniecia pieca brakuje:" i "Zamknij
   piec" (oraz "Otworz piec ponownie", "Cofnij przeniesienie");
2. srodek: strefa pytan i komunikatow o STALEJ wysokosci (``czesci.StrefaKomunikatow`` - jedna pozycja naraz, "i jeszcze n"),
   zakladki "Rozkladanie kuwet" / "Kompletne i braki" / "Ostatni zamkniety piec" / "Excel", pod nimi: wiersz "Teraz
   rozkladasz" o stalej wysokosci (duzy numer biezacej kuwety, gniazda na plytkach, "Rozlozona [Enter]", "Cofnij poprzednia
   [Backspace]", pole wpisywanego numeru) i mapy plytek pieca (``mapa_rano.MapaRano``) w siatce;
3. prawa kolumna "Praca": bez otwartej pracy - lista kuwet pieca z kolejnoscia; po kliknieciu gniazda - widok pracy
   (``kandydaci.WidokPracyRano``: "Ktory to projekt?" z kandydatami, na dole "Przypisz recznie" / "Bez projektu").
MAPY NIE PRZESUWAJA SIE przy zmianie stanu: strefa pytan, pasek zakladek i wiersz "Teraz rozkladasz" maja stale wysokosci,
kolumny - stale szerokosci; uklad map zalezy tylko od zestawu plytek i rozmiaru okna.

Zasady (kontrakt ``kontroler_api``, wersja 4):
* ekran NICZEGO nie liczy - pokazuje ``stan.rano`` (``StanRano``) i wysyla polecenia przez okno (``okno._polecenie``); kolory
  i napisy statusow ze stanu i ``statusy``; wyglad z ``motyw``; bez sciezek i nazw plikow;
* ochrona 800 ms (``OCHRONA_MS``): po zmianie zestawu plytek i po wejsciu w tryb poranny mapy sa przygaszone i nie przyjmuja
  klikniec; pozycja strefy pytan zmieniona w tle - przyciski strefy nieaktywne (S3-3); kolejnosc listy kuwet zmieniona w tle -
  klikniecia listy pomijane (S3-16);
* polecenia rozkladania niosa kuwete POKAZANA na ekranie (Enter / "Rozlozona" - ``kuweta_biezaca``, Backspace / "Cofnij" -
  ``kuweta_do_cofniecia``): gdy w kontrolerze jest juz inna, odmowa bez zapisu (recenzja PR #26, B1); lista kuwet wybiera
  kuwete po NUMERZE zapisanym w wierszu, nie po indeksie (S3-16);
* "Wszystkie kuwety rozlozone - mozesz zamknac piec" tylko bez blokad (S3-16);
* panele i okno nie trzymaja sie nawzajem silnymi referencjami (``weakref``) - okno znika bez zbierania cykli przez GC
  w przypadkowym watku (recenzja PR #26, D7);
* klawiatura jak na ramce porannej: cyfry (i "#") = numer kuwety, Enter = wybierz wpisana kuwete albo potwierdz biezaca
  ("rozlozona"), Backspace = popraw numer albo cofnij ostatnie potwierdzenie, Esc = wyczysc numer albo zamknij widok pracy;
  Spacja (start skanu) obsluguje okno.
Wlasny stan ekranu to wybor osoby: pokazana praca (plytka, gniazdo), wybrana plytka, zakladka, wpisywany numer kuwety, otwarty
wybor numeru plytki, pytanie przed "Zamknij piec", przegladana pozycja strefy pytan.
"""
from __future__ import annotations

import weakref

from PySide6.QtCore import QPoint, QRect, Qt, QTimer, Signal
from PySide6.QtGui import QFontMetrics, QImage
from PySide6.QtWidgets import (QAbstractItemView, QBoxLayout, QFrame, QGridLayout, QHBoxLayout, QHeaderView, QScrollArea, QSizePolicy, QStackedLayout,
                               QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

from .. import kontroler_api as K
from .. import statusy as ST
from . import czesci as C
from . import motyw
from . import napisy as N
from . import napisy_rano as NR
from .czesci import Kropka, UkladPlynny, dzien, etykieta, godzina, guzik, przycisk_skrotu, wyczysc, znaczek
from .kandydaci import WidokPracyRano, nazwa_plytki
from .mapa import geometria_ukladu
from .mapa_rano import MapaRano
from .okno_excela import PanelExcela

OCHRONA_MS = 800  # po zmianie zestawu plytek / wejsciu w tryb klikniecia map sa pomijane (jak A-P2 wieczorem)
KOLEJNOSC_KLAS = ("pewna", "przypisana", "dwuznaczna", "nieznana", "poprawka", "konflikt", "do_powtorzenia")
MAX_BUFORA = 7
STRONY = ("rozkladanie", "wynik", "ostatni", "excel")
LOKALNE_ZAMKNIJ_MIMO_WROC = "_zamknij_mimo_wroc"  # E3-P14 (N3): odpowiedzi na pytanie ekranu przed "Zamknij piec"
LOKALNE_ZAMKNIJ_MIMO_TAK = "_zamknij_mimo_tak"
LOKALNE = (LOKALNE_ZAMKNIJ_MIMO_WROC, LOKALNE_ZAMKNIJ_MIMO_TAK)
PYTANE = {"brak_numeru_plytki": "podaj_numer_plytki", "plytka_nie_z_trybu": "pomin_skan"}  # rano: plytki nie z trybu nie dopuszcza sie (A6)
AKCJE_PLYTKI = ("podaj_numer_plytki", "cofnij_zastapienie", "cofnij_dopuszczenie", "pomin_skan", "cofnij_pominiecie")
RANGA_POZIOMU = {ST.POZIOM_BLAD: 0, ST.POZIOM_OSTRZEZENIE: 1, ST.POZIOM_INFO: 2}


def blad_programu(komunikat) -> bool:
    return komunikat.poziom == ST.POZIOM_BLAD or komunikat.trwaly


def slaba(metoda):
    """Funkcja wolajaca metode obiektu przez slaba referencje (bez cyklu widzet -> ekran -> widzet; D7). Obiekt usuniety = None."""
    ref = weakref.WeakMethod(metoda)

    def wywolaj(*argumenty, **nazwane):
        m = ref()
        return m(*argumenty, **nazwane) if m is not None else None

    return wywolaj


def tabela(nazwa: str, kolumny: tuple, u: motyw.Uklad = motyw.UKLAD_WYSOKI) -> QTableWidget:
    """Tabela ekranu porannego - ta sama co wieczorem (``czesci.tabela``), wysokosc wierszy z ukladu."""
    return C.tabela(nazwa, kolumny, u.wiersz_tabeli, u.naglowek_tabeli)


def wypelnij(t: QTableWidget, wiersze: list, u: motyw.Uklad, widocznych: int | None = 6, dane: list | None = None) -> None:
    """Wiersze tabeli (listy napisow). ``widocznych`` - wysokosc tabeli = naglowek + tyle wierszy (reszta przewijana); None -
    wysokosc z ukladu (tabela rozciagana). ``dane`` - wartosc zapisana w pierwszej komorce wiersza (``Qt.UserRole``) - po niej
    klikniecie wybiera pozycje, nie po indeksie wiersza (S3-16)."""
    t.setRowCount(len(wiersze))
    for i, komorki in enumerate(wiersze):
        for k, tekst in enumerate(komorki):
            pole = QTableWidgetItem(tekst)
            pole.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            if k == 0 and dane is not None:
                pole.setData(Qt.ItemDataRole.UserRole, dane[i])
            t.setItem(i, k, pole)
    t.verticalHeader().setDefaultSectionSize(u.wiersz_tabeli)
    t.verticalHeader().setMinimumSectionSize(u.wiersz_tabeli)
    t.horizontalHeader().setFixedHeight(u.naglowek_tabeli)
    if widocznych is not None:
        t.setFixedHeight(u.naglowek_tabeli + max(1, min(widocznych, len(wiersze))) * u.wiersz_tabeli + 4)
    t.clearSelection()


def lista_nierozstrzygnietych(prace: tuple) -> str:
    """E3-P14 (N3): "Plytka 4, gniazdo 3 (wybierz); Plytka 5, gniazdo 22 (nieznana)" z ``StanRano.nierozstrzygniete_prace``
    (najwyzej ``NIEROZSTRZYGNIETYCH_W_NAPISIE`` pozycji, potem "... i jeszcze n")."""
    pozycje = []
    for x in prace[:NR.NIEROZSTRZYGNIETYCH_W_NAPISIE]:
        napis = ST.status_rano(x.klasa).napis
        if x.gniazdo is None:
            pozycje.append(NR.NIEROZSTRZYGNIETA_POZA.format(plytka=nazwa_plytki(x.numer_plytki), napis=napis))
        else:
            pozycje.append(NR.NIEROZSTRZYGNIETA.format(plytka=nazwa_plytki(x.numer_plytki), gniazdo=x.gniazdo, napis=napis))
    reszta = len(prace) - len(pozycje)
    return NR.NIEROZSTRZYGNIETE_ODSTEP.join(pozycje) + (NR.NIEROZSTRZYGNIETE_DALEJ.format(n=reszta) if reszta > 0 else "")


def teksty_tabeli(t: QTableWidget) -> list:
    return [[t.item(i, k).text() if t.item(i, k) is not None else "" for k in range(t.columnCount())] for i in range(t.rowCount())]


def lista_gniazd(numery: list) -> str:
    """"gniazdo 9" / "gniazda 2 i 9" / "gniazda 2, 5 i 9"."""
    if len(numery) == 1:
        return NR.KUWETA_GNIAZDO.format(nr=numery[0])
    napisy = [str(n) for n in numery]
    return NR.KUWETA_GNIAZDA.format(lista=", ".join(napisy[:-1]) + NR.KUWETA_GNIAZDA_I + napisy[-1])


def miejsca_kuwety(rano, kuweta) -> list:
    """Gniazda biezacej kuwety na plytkach (z ``KuwetaRano.gniazda`` - kontroler): ["Plytka 4 - gniazda 2 i 9", ...]."""
    po_plytce: dict = {}
    for skan_id, nr in kuweta.gniazda:
        po_plytce.setdefault(skan_id, []).append(nr)
    wynik = []
    for skan_id, numery in po_plytce.items():
        p = rano.plytka(skan_id)
        wynik.append(NR.KUWETA_MIEJSCE.format(plytka=nazwa_plytki(p.numer if p is not None else None), gniazda=lista_gniazd(sorted(numery))))
    return wynik


# ----------------------------------------------------------------------------
# lewa kolumna: piec
# ----------------------------------------------------------------------------
class KafelekPlytkiRano(QFrame):
    """Plytka pieca w lewej kolumnie: numer, godzina skanu, liczba prac i ile bez rozstrzygniecia, liczniki klas (kropka, napis,
    liczba - z ``Plytka.liczniki``), polecenia plytki ze stanu (``Plytka.dozwolone``). Klikniecie kafelka = ``wybrano(skan_id)``."""

    wybrano = Signal(int)

    def __init__(self, skan_id: int):
        super().__init__()
        self.skan_id = skan_id
        self.setObjectName(f"rano_kafelek_{skan_id}")
        self.setProperty("rola", "kafelek")
        self.setProperty("wybrany", "false")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setToolTip(NR.KAFELEK_OPIS)
        u = QVBoxLayout(self)
        u.setContentsMargins(12, 10, 12, 10)
        u.setSpacing(4)
        wiersz = QHBoxLayout()
        wiersz.setSpacing(8)
        self.nazwa = etykieta("", "numer_plytki", f"rano_kafelek_{skan_id}_nazwa", zawijaj=True)
        self.godzina = etykieta("", "przygaszony", f"rano_kafelek_{skan_id}_godzina")
        wiersz.addWidget(self.nazwa, 1)
        wiersz.addWidget(self.godzina, 0, Qt.AlignmentFlag.AlignTop)
        u.addLayout(wiersz)
        self.stan = etykieta("", "tresc", f"rano_kafelek_{skan_id}_stan", zawijaj=True)
        u.addWidget(self.stan)
        self._liczniki_pole = QWidget()
        self.liczniki = UkladPlynny(self._liczniki_pole, odstep_poziomy=12, odstep_pionowy=2)
        u.addWidget(self._liczniki_pole)
        self._akcje_pole = QWidget()
        self.akcje = UkladPlynny(self._akcje_pole, odstep_poziomy=6, odstep_pionowy=4)
        u.addWidget(self._akcje_pole)
        self._podpis = None

    def ustaw(self, p, nierozstrzygnietych: int, wybrany: bool, akcje: tuple, jest_osoba: bool, przelacz_numer, polecenie) -> None:
        C.ustaw_role(self, "true" if wybrany else "false", "wybrany")
        podpis = (p.numer, p.czas, p.napis, p.aktywna, len(p.prace), nierozstrzygnietych, tuple(sorted((p.liczniki or {}).items())), akcje, jest_osoba)
        if podpis == self._podpis:
            return
        self._podpis = podpis
        self.nazwa.setText(nazwa_plytki(p.numer))
        self.godzina.setText(godzina(p.czas))
        czesci = [ST.odmiana(len(p.prace), *NR.KAFELEK_PRAC).format(n=len(p.prace))] if p.prace else []
        if p.prace:
            czesci.append(NR.KAFELEK_DO_ROZSTRZYGNIECIA.format(n=nierozstrzygnietych) if nierozstrzygnietych else NR.KAFELEK_ROZSTRZYGNIETE)
        if not p.aktywna:
            czesci.append(p.napis)
        self.stan.setText(NR.KROPKA.join(c for c in czesci if c))
        wyczysc(self.liczniki)
        for klasa in KOLEJNOSC_KLAS:
            n = (p.liczniki or {}).get(klasa, 0)
            if n:
                w = ST.status_rano(klasa)
                pole = QWidget()
                pole.setObjectName(f"rano_kafelek_{self.skan_id}_licznik_{klasa}")
                lu = QHBoxLayout(pole)
                lu.setContentsMargins(0, 0, 0, 0)
                lu.setSpacing(4)
                lu.addWidget(Kropka(w.hex, 9, obwodka=klasa == "konflikt"), 0, Qt.AlignmentFlag.AlignVCenter)
                lu.addWidget(etykieta(NR.LICZNIK.format(napis=w.napis, n=n), "pomocniczy"))
                pole.setToolTip(w.opis)
                self.liczniki.addWidget(pole)
        self._liczniki_pole.setVisible(self.liczniki.count() > 0)
        wyczysc(self.akcje)
        for akcja in akcje:
            napis = NR.ZMIEN_NUMER if akcja == "podaj_numer_plytki" and p.numer is not None else ST.PRZYCISKI[akcja]
            nazwa = f"rano_plytka_{p.skan_id}_{akcja}"
            if akcja == "podaj_numer_plytki":
                b = guzik(napis, nazwa, "lacze", lambda s=p.skan_id: przelacz_numer(s))
            else:
                b = guzik(napis, nazwa, "lacze", lambda a=akcja, s=p.skan_id: polecenie(a, s))
                b.setEnabled(jest_osoba)
            self.akcje.addWidget(b)
        self._akcje_pole.setVisible(self.akcje.count() > 0)

    def mousePressEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        if zdarzenie.button() == Qt.MouseButton.LeftButton:
            C._fokus_do_okna(self)
            self.wybrano.emit(self.skan_id)


class PanelPieca(QFrame):
    """Lewa kolumna "Piec n": naglowek, kafelki plytek, skany, ktore sie nie licza, legenda; na dole blokady i polecenia pieca."""

    def __init__(self, ekran: "EkranRano"):
        super().__init__()
        self.setObjectName("rano_piec")
        self._ekran = weakref.ref(ekran)
        self.setFixedWidth(motyw.UKLAD_WYSOKI.lewa)
        self._u = u = QVBoxLayout(self)
        u.setSpacing(8)
        self.tytul = etykieta(NR.PIEC_TYTUL_BRAK, "tytul_pracy", "rano_piec_tytul", zawijaj=True)
        u.addWidget(self.tytul)
        self.opis = etykieta("", "tresc", "rano_piec_opis", zawijaj=True)
        u.addWidget(self.opis)
        self.ostrzezenia = etykieta("", "uwaga", "rano_ostrzezenia", zawijaj=True)
        self.ostrzezenia.setVisible(False)
        u.addWidget(self.ostrzezenia)
        self.przewijanie = QScrollArea()
        self.przewijanie.setObjectName("rano_piec_przewijanie")
        self.przewijanie.setWidgetResizable(True)
        self.przewijanie.setFrameShape(QFrame.Shape.NoFrame)
        self.przewijanie.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.przewijanie.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        wnetrze = QWidget()
        wnetrze.setObjectName("rano_piec_wnetrze")
        wnetrze.setStyleSheet("QWidget#rano_piec_wnetrze { background: transparent; }")
        self._wu = wu = QVBoxLayout(wnetrze)
        wu.setContentsMargins(0, 0, 0, 0)
        wu.setSpacing(6)
        self._kafelki = QVBoxLayout()
        self._kafelki.setSpacing(6)
        wu.addLayout(self._kafelki)
        self.nieaktywne = etykieta("", "pomocniczy", "rano_nieaktywne", zawijaj=True)
        self.nieaktywne.setVisible(False)
        wu.addWidget(self.nieaktywne)
        self.legenda = QWidget()
        self.legenda.setObjectName("rano_legenda")
        lu = QVBoxLayout(self.legenda)
        lu.setContentsMargins(0, 8, 0, 0)
        lu.setSpacing(6)
        lu.addWidget(etykieta(NR.LEGENDA_NAGLOWEK, "naglowek_sekcji", "rano_legenda_naglowek"))
        self._liczniki_pole = QWidget()
        self._liczniki_pole.setObjectName("rano_liczniki")
        self.liczniki = UkladPlynny(self._liczniki_pole, odstep_poziomy=6, odstep_pionowy=4)
        lu.addWidget(self._liczniki_pole)
        self._pozycje = QVBoxLayout()
        self._pozycje.setSpacing(4)
        lu.addLayout(self._pozycje)
        self.legenda.setVisible(False)
        wu.addWidget(self.legenda)
        wu.addStretch(1)
        self.przewijanie.setWidget(wnetrze)
        u.addWidget(self.przewijanie, 1)
        self.blokady_naglowek = etykieta(NR.BLOKADY_NAGLOWEK, "tresc", "rano_blokady_naglowek")
        self.blokady = etykieta("", "tresc_glowna", "rano_blokady", zawijaj=True)
        for w in (self.blokady_naglowek, self.blokady):
            w.setVisible(False)
            u.addWidget(w)
        self.zamknij_piec = guzik(ST.PRZYCISKI["zamknij_piec"], "przycisk_zamknij_piec", "glowny", lambda: self._wyslij("_zamknij_piec"),
                                  motyw.CEL_KLIKNIECIA)
        u.addWidget(self.zamknij_piec)
        self.otworz_piec = guzik(ST.PRZYCISKI["otworz_piec_ponownie"], "przycisk_otworz_piec", None, lambda: self._wyslij("_otworz_piec"),
                                 motyw.CEL_KLIKNIECIA)
        u.addWidget(self.otworz_piec)
        self.cofnij_przeniesienie = guzik(ST.PRZYCISKI["cofnij_przeniesienie"], "przycisk_cofnij_przeniesienie", "lacze",
                                          lambda: self._wyslij("_polecenie_pieca", "cofnij_przeniesienie"))
        u.addWidget(self.cofnij_przeniesienie)
        self.ustaw_uklad(motyw.UKLAD_WYSOKI)

    def _wyslij(self, metoda: str, *argumenty) -> None:
        ekran = self._ekran()
        if ekran is not None:
            getattr(ekran, metoda)(*argumenty)

    def ustaw_uklad(self, u: motyw.Uklad) -> None:
        self.setFixedWidth(u.lewa)
        bok = 12 if u.zwarty else 16
        self._u.setContentsMargins(bok, bok, bok, bok)

    def kafelki(self) -> dict:
        return {w.skan_id: w for w in self.findChildren(KafelekPlytkiRano)}


# ----------------------------------------------------------------------------
# srodek: wiersz "Teraz rozkladasz" i mapy plytek
# ----------------------------------------------------------------------------
class WierszKuwety(QFrame):
    """"Teraz rozkladasz": duzy numer biezacej kuwety, liczba prac, gniazda na plytkach, "Rozlozona [Enter]", "Cofnij poprzednia
    [Backspace]", pole wpisywanego numeru kuwety (cyfry z klawiatury okna). STALA wysokosc (``Uklad.kuweta``) - mapy pod nim nie
    zmieniaja miejsca. W ukladzie zwartym pole numeru pokazuje sie w miejscu opisu kuwety, gdy osoba wpisuje cyfry."""

    def __init__(self, ekran: "EkranRano"):
        super().__init__()
        self.setObjectName("rano_kuweta_wiersz")
        self._ekran = weakref.ref(ekran)
        self._u = u = QHBoxLayout(self)
        u.setSpacing(16)
        lewa = QVBoxLayout()
        lewa.setSpacing(0)
        self.naglowek = etykieta(NR.TERAZ_ROZKLADASZ, "tresc", "rano_teraz_rozkladasz")
        lewa.addWidget(self.naglowek)
        self.biezaca = etykieta(NR.KUWETA_BRAK_NUMERU, "kuweta_numer", "rano_kuweta_biezaca")
        lewa.addWidget(self.biezaca)
        lewa.addStretch(1)
        u.addLayout(lewa)
        # opis kuwety albo (uklad zwarty, osoba wpisuje cyfry) pole numeru
        self._opis_stos = QStackedLayout()
        opis = QWidget()
        ou = QVBoxLayout(opis)
        ou.setContentsMargins(0, 0, 0, 0)
        ou.setSpacing(2)
        self.opis = etykieta("", "kuweta_opis", "rano_kuweta_opis", zawijaj=True)
        ou.addWidget(self.opis)
        self.miejsca = etykieta("", "tresc_glowna", "rano_kuweta_miejsca", zawijaj=True)
        ou.addWidget(self.miejsca)
        self.miejsca_krotko = C.EtykietaSkracana("tresc_glowna", "rano_kuweta_miejsca_krotko")  # uklad zwarty: jeden wiersz
        ou.addWidget(self.miejsca_krotko)
        self.na_ramce = etykieta(NR.NA_RAMCE, "pomocniczy", "rano_kuwety_podpowiedz", zawijaj=True)
        ou.addWidget(self.na_ramce)
        ou.addStretch(1)
        self._opis_stos.addWidget(opis)
        pole_male = QWidget()
        pu = QVBoxLayout(pole_male)
        pu.setContentsMargins(0, 0, 0, 0)
        pu.setSpacing(4)
        self.pole_male = etykieta("", "pole", "rano_pole_kuwety_zwarte")
        self.pole_male.setFixedHeight(motyw.CEL_KLIKNIECIA)
        pu.addWidget(self.pole_male)
        self.bufor_maly = etykieta("", "pomocniczy", "rano_bufor_zwarty", zawijaj=True)
        pu.addWidget(self.bufor_maly)
        pu.addStretch(1)
        self._opis_stos.addWidget(pole_male)
        u.addLayout(self._opis_stos, 1)
        self._przyciski = przyciski = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        przyciski.setSpacing(8)
        self.potwierdz = przycisk_skrotu(NR.POTWIERDZ_SKROT, "rano_potwierdz_kuwete", "glowny", lambda: self._wyslij("potwierdz_kuwete"),
                                         motyw.UKLAD_WYSOKI.decyzja, px=motyw.PX_PRZYCISK_DECYZJI, pogrubiony=True)
        self.cofnij = przycisk_skrotu(NR.COFNIJ_SKROT, "rano_cofnij_kuwete", None, lambda: self._wyslij("cofnij_kuwete"),
                                      motyw.UKLAD_WYSOKI.decyzja)
        for b in (self.potwierdz, self.cofnij):
            b.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            przyciski.addWidget(b)
        przyciski.addStretch(1)
        u.addLayout(przyciski)
        self.pole_blok = QWidget()
        self.pole_blok.setObjectName("rano_pole_blok")
        bu = QVBoxLayout(self.pole_blok)
        bu.setContentsMargins(0, 0, 0, 0)
        bu.setSpacing(4)
        self.pole_opis = etykieta(NR.INNA_KUWETA, "tresc", "rano_pole_opis", zawijaj=True)
        bu.addWidget(self.pole_opis)
        self.pole = etykieta("", "pole_puste", "rano_pole_kuwety")
        self.pole.setFixedHeight(motyw.CEL_KLIKNIECIA)
        bu.addWidget(self.pole)
        self.bufor = etykieta("", "pomocniczy", "rano_bufor", zawijaj=True)
        self.bufor.setVisible(False)
        bu.addWidget(self.bufor)
        bu.addStretch(1)
        self.pole_blok.setFixedWidth(220)
        u.addWidget(self.pole_blok)
        self._zwarty = False
        self._sygnatura = None
        self.ustaw_uklad(motyw.UKLAD_WYSOKI)

    def _wyslij(self, metoda: str) -> None:
        ekran = self._ekran()
        if ekran is not None:
            getattr(ekran, metoda)()

    def ustaw_uklad(self, u: motyw.Uklad) -> None:
        self._zwarty = u.zwarty
        self.setFixedHeight(u.kuweta)
        self._u.setContentsMargins(u.bok_rano, 8 if u.zwarty else 12, u.bok_rano, 0)
        self._u.setSpacing(12 if u.zwarty else 16)
        wys = motyw.CEL_KLIKNIECIA if u.zwarty else u.decyzja
        for b in (self.potwierdz, self.cofnij):
            b.setFixedHeight(wys)
        self.pole_blok.setVisible(not u.zwarty)
        self.na_ramce.setVisible(not u.zwarty)
        # uklad zwarty: "Rozlozona" i "Cofnij poprzednia" obok siebie (wiersz nizszy - wiecej miejsca na mapy plytek)
        self._przyciski.setDirection(QBoxLayout.Direction.LeftToRight if u.zwarty else QBoxLayout.Direction.TopToBottom)
        self._sygnatura = None

    def ustaw(self, stan, bufor: str) -> None:
        rano = stan.rano
        sygnatura = (rano.kuwety if rano is not None else None, rano.otwarty if rano is not None else None,
                     rano.sesja_pieca_id if rano is not None else None, rano.kuweta_do_cofniecia if rano is not None else None,
                     tuple(rano.blokady) if rano is not None else (), tuple((p.skan_id, p.numer) for p in rano.plytki) if rano is not None else (),
                     stan.operator, bufor, self._zwarty)
        if sygnatura == self._sygnatura:
            return
        self._sygnatura = sygnatura
        kuwety = rano.kuwety if rano is not None else ()
        biezaca = next((x for x in kuwety if x.biezaca), None)
        miejsca: list = []
        if rano is None or rano.sesja_pieca_id is None or (not kuwety and rano.otwarty):
            numer, opis = NR.KUWETA_BRAK_NUMERU, NR.KUWETA_BRAK_PIECA
        elif biezaca is None and not rano.otwarty:
            numer, opis = NR.KUWETA_BRAK_NUMERU, NR.PIEC_ZAMKNIETY_INFO
        elif biezaca is None:  # S3-16: "mozesz zamknac piec" tylko, gdy nic go nie trzyma
            numer = NR.KUWETA_BRAK_NUMERU
            opis = NR.KUWETA_BRAK_BLOKADY.format(lista="; ".join(rano.blokady)) if rano.blokady else NR.KUWETA_BRAK
        else:
            numer = biezaca.kuweta
            opis = NR.KUWETA_OPIS.format(prac=ST.odmiana(biezaca.prac, *NR.KUWETA_PRACE).format(n=biezaca.prac))
            miejsca = miejsca_kuwety(rano, biezaca)
        self.biezaca.setText(numer)
        # pelny opis ("Kuweta 3228" - tak numer nazywaja instrukcje) dla czytnika ekranu i w podpowiedzi
        opis_numeru = NR.KUWETA_BIEZACA.format(kuweta=numer) if biezaca is not None else ""
        self.biezaca.setAccessibleName(opis_numeru)
        self.biezaca.setToolTip(opis_numeru)
        self.opis.setText(opis)
        self.miejsca.setText("\n".join(miejsca))
        self.miejsca.setVisible(bool(miejsca) and not self._zwarty)
        self.miejsca_krotko.setText(NR.NIEROZSTRZYGNIETE_ODSTEP.join(miejsca))
        self.miejsca_krotko.setToolTip("\n".join(miejsca))
        self.miejsca_krotko.setVisible(bool(miejsca) and self._zwarty)
        jest_osoba = stan.operator is not None
        otwarty = rano is not None and rano.otwarty
        self.potwierdz.setEnabled(otwarty and biezaca is not None and jest_osoba)
        self.cofnij.setEnabled(otwarty and rano.kuweta_do_cofniecia is not None and jest_osoba)
        tekst_pola = f"{bufor}\u2581" if bufor else NR.POLE_KUWETY_PUSTE  # kursor jak w napisie ``NR.BUFOR``
        rola = "pole" if bufor else "pole_puste"
        for pole in (self.pole, self.pole_male):
            pole.setText(tekst_pola)
            C.ustaw_role(pole, rola)
        napis_bufora = NR.BUFOR.format(bufor=bufor) if bufor else ""
        self.bufor.setText(napis_bufora)
        self.bufor.setVisible(bool(bufor) and not self._zwarty)
        self.bufor_maly.setText(napis_bufora)
        self._opis_stos.setCurrentIndex(1 if bufor and self._zwarty else 0)


class KartaMapy(QFrame):
    """Mapa jednej plytki pieca w siatce srodka: wiersz tytulu o STALEJ wysokosci (numer plytki i napis skanu, godzina, prace
    poza gniazdami) i ``MapaRano``. Wybrana plytka (kafelek w lewej kolumnie) ma obwodke akcentu."""

    def __init__(self, skan_id: int, ekran: "EkranRano"):
        super().__init__()
        self.skan_id = skan_id
        self.setObjectName(f"rano_plytka_{skan_id}")
        self.setProperty("rola", "karta_mapy")
        self.setProperty("wybrany", "false")
        u = QVBoxLayout(self)
        u.setContentsMargins(1, 2, 1, 2)  # obwodka wybranej plytki 1 px; reszta szerokosci dla mapy
        u.setSpacing(2)
        wiersz = QHBoxLayout()
        wiersz.setSpacing(8)
        self.tytul = C.EtykietaSkracana("numer_plytki", f"rano_plytka_{skan_id}_tytul")
        self.godzina = etykieta("", "pomocniczy", f"rano_plytka_{skan_id}_godzina")
        self.poza = etykieta("", "pomocniczy", f"rano_plytka_{skan_id}_poza")
        wiersz.addWidget(self.tytul, 1)
        wiersz.addWidget(self.poza)
        wiersz.addWidget(self.godzina)
        naglowek = QWidget()
        naglowek.setLayout(wiersz)
        wiersz.setContentsMargins(0, 0, 0, 0)
        naglowek.setFixedHeight(24)
        u.addWidget(naglowek)
        self.mapa = MapaRano(skan_id)
        klik = slaba(ekran._klik_gniazdo)
        self.mapa.klik.connect(lambda nr: klik(skan_id, nr))
        u.addWidget(self.mapa, 1)


class PoleMap(QWidget):
    """Siatka map plytek pieca: liczba kolumn dobrana tak, zeby mapy byly jak najwieksze (zalezy tylko od liczby plytek i rozmiaru
    pola - nie od stanu)."""

    def __init__(self):
        super().__init__()
        self.setObjectName("rano_plytki")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._siatka = QGridLayout(self)
        self._siatka.setContentsMargins(0, 0, 0, 0)
        self._siatka.setSpacing(12)
        self._karty: list = []
        self._pusty: QWidget | None = None
        self._kolumn = 0

    def ustaw_odstep(self, odstep: int) -> None:
        self._siatka.setSpacing(odstep)

    def ustaw_karty(self, karty: list, pusty: QWidget | None) -> None:
        wyczysc(self._siatka)
        self._karty, self._pusty, self._kolumn = list(karty), pusty, 0
        if pusty is not None:
            self._siatka.addWidget(pusty, 0, 0)
        self._uloz()

    def _najlepsze_kolumny(self) -> int:
        n = len(self._karty)
        if n <= 1:
            return 1
        szer, wys = max(1, self.width()), max(1, self.height())
        odstep = self._siatka.spacing()
        najlepsze, kolumn = -1.0, 1
        for k in range(1, n + 1):
            wierszy = -(-n // k)
            bok = min((szer - odstep * (k - 1)) / k, (wys - odstep * (wierszy - 1)) / wierszy - 30)
            if bok > najlepsze + 0.5:
                najlepsze, kolumn = bok, k
        return kolumn

    def _uloz(self) -> None:
        if not self._karty:
            return
        kolumn = self._najlepsze_kolumny()
        if kolumn == self._kolumn:
            return
        self._kolumn = kolumn
        for karta in self._karty:
            self._siatka.removeWidget(karta)
        for i, karta in enumerate(self._karty):
            self._siatka.addWidget(karta, i // kolumn, i % kolumn)
            karta.show()
        wierszy = -(-len(self._karty) // kolumn)
        for k in range(max(kolumn, self._siatka.columnCount())):
            self._siatka.setColumnStretch(k, 1 if k < kolumn else 0)
        for w in range(max(wierszy, self._siatka.rowCount())):
            self._siatka.setRowStretch(w, 1 if w < wierszy else 0)

    def resizeEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        super().resizeEvent(zdarzenie)
        self._uloz()


# ----------------------------------------------------------------------------
# prawa kolumna: lista kuwet (bez otwartej pracy)
# ----------------------------------------------------------------------------
class PanelKuwet(QFrame):
    """"Kuwety w tym piecu": kolejnosc (od najliczniejszej / wedlug numeru) i lista kuwet pieca (klikniecie = wybor kuwety PO
    NUMERZE zapisanym w wierszu - S3-16; gdy zmiana z tla przestawila to, co widac pod punktami listy - kolejnosc, przewiniecie
    do nowej biezacej kuwety, wysokosc wierszy - klikniecia sa przez ``OCHRONA_MS`` pomijane, runda 2 P1)."""

    def __init__(self, ekran: "EkranRano"):
        super().__init__()
        self.setObjectName("rano_kuwety")
        self._ekran = weakref.ref(ekran)
        self._u = u = QVBoxLayout(self)
        u.setSpacing(8)
        self.tytul = etykieta("", "naglowek", "rano_kuwety_tytul", zawijaj=True)
        u.addWidget(self.tytul)
        kolejnosc = QHBoxLayout()
        kolejnosc.setSpacing(0)
        self.przyciski_kolejnosci = {}
        role = ("zakres_lewy", "zakres_prawy")  # jak przelacznik zakresu listy wieczorem (napis wybranej czesci nie jest pogrubiany)
        for i, k in enumerate(K.KOLEJNOSCI_KUWET):
            b = guzik(ST.NAZWY_KOLEJNOSCI[k], f"kolejnosc_{k}", role[min(i, 1)], lambda k=k: self._wyslij("_polecenie", "ustaw_kolejnosc", k))
            b.setCheckable(True)
            self.przyciski_kolejnosci[k] = b
            kolejnosc.addWidget(b)
        kolejnosc.addStretch(1)
        u.addLayout(kolejnosc)
        self.podpowiedz = etykieta(NR.KLIKNIJ_GNIAZDO, "tresc", "rano_kliknij_gniazdo", zawijaj=True)
        u.addWidget(self.podpowiedz)
        self.tabela = tabela("tabela_kuwet", NR.KOLUMNY_KUWET)
        naglowek = self.tabela.horizontalHeader()
        for kolumna, tryb in enumerate((QHeaderView.ResizeMode.ResizeToContents, QHeaderView.ResizeMode.ResizeToContents,
                                        QHeaderView.ResizeMode.Stretch, QHeaderView.ResizeMode.ResizeToContents)):
            naglowek.setSectionResizeMode(kolumna, tryb)
        self.tabela.cellClicked.connect(self._klik)
        u.addWidget(self.tabela, 1)
        self._u_ukladu = motyw.UKLAD_WYSOKI
        self._sygnatura = None
        self._kolejnosc_widziana: tuple | None = None
        self._ochrona = QTimer(self)
        self._ochrona.setSingleShot(True)
        self._ochrona.setInterval(OCHRONA_MS)
        self.ustaw_uklad(motyw.UKLAD_WYSOKI)

    def _wyslij(self, metoda: str, *argumenty) -> None:
        ekran = self._ekran()
        if ekran is not None:
            getattr(ekran, metoda)(*argumenty)

    def ustaw_uklad(self, u: motyw.Uklad) -> None:
        self._u_ukladu = u
        bok = 12 if u.zwarty else 16
        self._u.setContentsMargins(bok, bok, bok, bok)
        self._sygnatura = None

    def ochrona_aktywna(self) -> bool:
        return self._ochrona.isActive()

    def ustaw(self, stan, z_tla: bool) -> None:
        rano = stan.rano
        kuwety = rano.kuwety if rano is not None else ()
        sygnatura = (kuwety, rano.kolejnosc if rano is not None else None, self._u_ukladu)
        if sygnatura == self._sygnatura:
            return
        self._sygnatura = sygnatura
        kolejnosc = tuple(x.kuweta for x in kuwety)
        widok_przed = self.widok()
        zmiana_kolejnosci = bool(self._kolejnosc_widziana) and kolejnosc != self._kolejnosc_widziana
        self._kolejnosc_widziana = kolejnosc
        self.tytul.setText(NR.KUWETY_TYTUL.format(n=len(kuwety)))
        for k, b in self.przyciski_kolejnosci.items():
            b.setChecked(rano is not None and rano.kolejnosc == k)
        wiersze = []
        for x in kuwety:
            stan_k = (NR.KUWETA_STAN_BIEZACA if x.biezaca else NR.KUWETA_STAN_ROZLOZONA if x.potwierdzona else
                      NR.KUWETA_STAN_BRAKI if x.braki else NR.KUWETA_STAN_CZEKA)
            wiersze.append([x.kuweta, str(x.prac), ", ".join(map(str, x.plytki)), stan_k])
        wypelnij(self.tabela, wiersze, self._u_ukladu, widocznych=None, dane=list(kolejnosc))
        indeks = next((i for i, x in enumerate(kuwety) if x.biezaca), None)
        if indeks is not None:
            self.tabela.selectRow(indeks)
            self.tabela.scrollToItem(self.tabela.item(indeks, 0), QAbstractItemView.ScrollHint.EnsureVisible)
        # S3-16 (runda 2, P1): pod kursorem moze stac juz inna kuweta - po zmianie kolejnosci ALBO gdy lista przewinela sie do nowej
        # biezacej kuwety ("Rozlozona" z ramki / drugiego stanowiska) czy zmienila wysokosc wierszy; klikniecie wycelowane w poprzednia
        # kuwete nie trafia przez ``OCHRONA_MS``
        if z_tla and (zmiana_kolejnosci or (widok_przed and self.widok() != widok_przed)):
            self._ochrona.start()

    def widok(self) -> tuple:
        """Widoczne wiersze listy: (polozenie w polu, wysokosc, numer kuwety) - to, co osoba widzi pod kazdym punktem listy."""
        t = self.tabela
        wys = t.viewport().height()
        pierwszy = t.rowAt(0)
        if wys <= 0 or pierwszy < 0:
            return ()
        ostatni = t.rowAt(wys - 1)
        ostatni = t.rowCount() - 1 if ostatni < 0 else ostatni
        return tuple((t.rowViewportPosition(w), t.rowHeight(w), self.kuweta_w_wierszu(w)) for w in range(pierwszy, ostatni + 1))

    def kuweta_w_wierszu(self, wiersz: int) -> str | None:
        """Numer kuwety zapisany w wierszu listy (S3-16) albo None."""
        pole = self.tabela.item(wiersz, 0)
        return pole.data(Qt.ItemDataRole.UserRole) if pole is not None else None

    def _klik(self, wiersz: int, _kolumna: int) -> None:
        if self._ochrona.isActive():
            return
        kuweta = self.kuweta_w_wierszu(wiersz)
        if kuweta:
            self._wyslij("_polecenie", "wybierz_kuwete", kuweta)


# ----------------------------------------------------------------------------
# zakladki "Kompletne i braki" / "Ostatni zamkniety piec"
# ----------------------------------------------------------------------------
class PanelWyniku(QScrollArea):
    """Zlecenia kompletne (do odhaczenia w Excelu) i braki pieca - prowizoryczne w otwartym piecu, z zapisu "Zamknij piec"
    w zamknietym; lista brakow ze wszystkich piecow (klikniecie zlecenia = reczne zamkniecie brakujacego punktu z powodem,
    A6 runda 2; ostatnie zamkniecie mozna cofnac); poprawki (tylko log; zlecenie odhaczone i zab juz rozpoznany - osobno, Z9).
    ``ostatni`` True = zakladka "Ostatni zamkniety piec" (wynik pieca ``StanRano.ostatni_zamkniety``, bez listy brakow biezacej;
    nazwy obiektow z przedrostkiem ``ostatni_`` - P1)."""

    def __init__(self, ekran: "EkranRano | None" = None, ostatni: bool = False):
        super().__init__()
        self._ekran = weakref.ref(ekran) if ekran is not None else (lambda: None)
        self._ostatni_piec = ostatni
        n = (lambda nazwa: f"ostatni_{nazwa}") if ostatni else (lambda nazwa: nazwa)
        self._wybrane: int | None = None  # zlecenie_id z listy brakow wybrane do recznego zamkniecia
        self._ostatnie: tuple | None = None  # (projekt_id, kuweta, zab) ostatnio zamknietego recznie punktu (do cofniecia)
        self._biezace: tuple = ()
        self.setObjectName(n("rano_wynik"))
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        wnetrze = QWidget()
        wnetrze.setObjectName(n("rano_wynik_wnetrze"))
        wnetrze.setStyleSheet(f"QWidget#{n('rano_wynik_wnetrze')} {{ background: transparent; }}")
        self._u = u = QVBoxLayout(wnetrze)
        self.tytul = etykieta("", "tytul_pracy", n("rano_wynik_tytul"), zawijaj=True)
        u.addWidget(self.tytul)
        self.kompletne_tytul = etykieta("", "naglowek", n("rano_kompletne_tytul"), zawijaj=True)
        u.addWidget(self.kompletne_tytul)
        self.kompletne = tabela(n("tabela_kompletne"), NR.KOLUMNY_KOMPLETNE)
        u.addWidget(self.kompletne)
        self.przycisk_excel = guzik(NR.EXCEL_POKAZ, n("przycisk_excel"), "akcent", self._pokaz_excel, motyw.CEL_KLIKNIECIA)  # E3-A12
        self.przycisk_excel.setVisible(False)
        u.addWidget(self.przycisk_excel, 0, Qt.AlignmentFlag.AlignLeft)
        # r3 P-N3: zalegle piece Excela osiagalne z ekranu (takze gdy okno Excela jest zamkniete, a ostatni piec zalatwiony)
        self._prefiks = n("wynik_excel_zalegly")
        self.zalegle = QWidget()
        self.zalegle.setObjectName(n("wynik_excel_zalegle"))
        self._zalegle = UkladPlynny(self.zalegle, odstep_poziomy=6, odstep_pionowy=4)
        self.zalegle.setVisible(False)
        u.addWidget(self.zalegle)
        self.braki_tytul = etykieta("", "naglowek", n("rano_braki_tytul"), zawijaj=True)
        u.addWidget(self.braki_tytul)
        self.braki = tabela(n("tabela_braki"), NR.KOLUMNY_BRAKI)
        u.addWidget(self.braki)
        self.nierozstrzygniete = etykieta("", "uwaga", n("rano_nierozstrzygniete"), zawijaj=True)
        u.addWidget(self.nierozstrzygniete)
        self.poprawki = etykieta("", "informacja", n("rano_poprawki"), zawijaj=True)
        u.addWidget(self.poprawki)
        self.juz_rozpoznane = etykieta("", "uwaga", n("rano_juz_rozpoznane"), zawijaj=True)
        u.addWidget(self.juz_rozpoznane)
        self.biezace_tytul = etykieta("", "naglowek", n("rano_braki_biezace_tytul"), zawijaj=True)
        u.addWidget(self.biezace_tytul)
        self.biezace = tabela(n("tabela_braki_biezace"), NR.KOLUMNY_BRAKI_BIEZACE)
        # E3-P14 (poz. 3): 4 rowne kolumny ucinaly stan punktu ("nie wyszedl z ...") - kuweta, stan i piec wg tresci, reszta dla zebow
        naglowek = self.biezace.horizontalHeader()
        naglowek.setMinimumSectionSize(48)
        for kolumna, tryb in enumerate((QHeaderView.ResizeMode.ResizeToContents, QHeaderView.ResizeMode.Stretch,
                                        QHeaderView.ResizeMode.ResizeToContents, QHeaderView.ResizeMode.ResizeToContents)):
            naglowek.setSectionResizeMode(kolumna, tryb)
        self.biezace.cellClicked.connect(self._klik_braku)
        u.addWidget(self.biezace)
        if ostatni:  # zakladka ostatniego zamknietego pieca: bez listy brakow biezacej (jest w "Kompletne i braki")
            self.biezace_tytul.setVisible(False)
            self.biezace.setVisible(False)
        self.reczne = QWidget()
        self.reczne.setObjectName(n("rano_brak_reczny"))
        self._reczne = QVBoxLayout(self.reczne)
        self._reczne.setContentsMargins(0, 0, 0, 0)
        self._reczne.setSpacing(6)
        u.addWidget(self.reczne)
        u.addStretch(1)
        self.setWidget(wnetrze)
        self._uklad = motyw.UKLAD_WYSOKI
        self._sygnatura = None
        self._stan = None
        self.ustaw_uklad(motyw.UKLAD_WYSOKI)

    def _klik_braku(self, wiersz: int, _kolumna: int) -> None:
        pole = self.biezace.item(wiersz, 0)
        zlecenie = pole.data(Qt.ItemDataRole.UserRole) if pole is not None else None  # po identyfikatorze w wierszu (jak S3-16)
        z = next((x for x in self._biezace if x.zlecenie_id == zlecenie), None)
        if z is not None:
            self._wybrane = None if self._wybrane == z.zlecenie_id else z.zlecenie_id
            self._sygnatura = None
            if self._stan is not None:
                self.ustaw(self._stan.rano, self._stan)

    @property
    def ekran(self):
        return self._ekran()

    def _zamknij(self, z, b, powod: str) -> None:
        odpowiedz = self.ekran._polecenie("zamknij_brak_recznie", b.projekt_id, powod) if self.ekran is not None else None
        if odpowiedz is not None and odpowiedz.ok:
            self._ostatnie = (b.projekt_id, z.kuweta, b.zeby)
            self._sygnatura = None
            if self._stan is not None:
                self.ustaw(self._stan.rano, self._stan)

    def _pokaz_excel(self) -> None:
        """E3-A12: okno "Excel: wskaz wiersz" dla pokazanego zamknietego pieca."""
        rano = (self._stan.rano.ostatni_zamkniety if self._ostatni_piec else self._stan.rano) if self._stan is not None and self._stan.rano else None
        if rano is not None and rano.sesja_pieca_id is not None and self.ekran is not None:
            self.ekran.pokaz_excel(rano.sesja_pieca_id)

    def _cofnij(self) -> None:
        if self._ostatnie is None or self.ekran is None:
            return
        odpowiedz = self.ekran._polecenie("cofnij_zamkniecie_reczne", self._ostatnie[0])
        if odpowiedz is not None and odpowiedz.ok:
            self._ostatnie = None
            self._sygnatura = None
            if self._stan is not None:
                self.ustaw(self._stan.rano, self._stan)

    def _odswiez_reczne(self, stan) -> None:
        """Pod lista brakow: punkty wybranego zlecenia z przyciskami powodow i "Cofnij zamkniecie reczne" ostatniego zamkniecia."""
        wyczysc(self._reczne)
        jest_osoba = stan is not None and stan.operator is not None
        z = next((x for x in self._biezace if x.zlecenie_id == self._wybrane), None)
        if z is None:
            self._wybrane = None
        else:
            self._reczne.addWidget(etykieta(NR.RECZNE_TYTUL.format(kuweta=z.kuweta or NR.BRAK_DANYCH), "naglowek", "rano_brak_reczny_tytul", zawijaj=True))
            self._reczne.addWidget(etykieta(NR.RECZNE_OPIS, "tresc", zawijaj=True))
            for b in z.brakujace:
                self._reczne.addWidget(etykieta(NR.RECZNE_PUNKT.format(zab=b.zeby or NR.BRAK_DANYCH, stan=b.napis), "wyrozniony", zawijaj=True))
                powody = UkladPlynny(odstep_poziomy=6, odstep_pionowy=4)
                for kod, napis in ST.powody_zamkniecia(b.stan).items():
                    przycisk_ = guzik(napis, f"brak_{b.projekt_id}_{kod}", "lacze", lambda z=z, b=b, kod=kod: self._zamknij(z, b, kod))
                    przycisk_.setEnabled(jest_osoba)
                    powody.addWidget(przycisk_)
                self._reczne.addLayout(powody)
        if self._ostatnie is not None:
            projekt_id, kuweta, zab = self._ostatnie
            self._reczne.addWidget(etykieta(NR.RECZNE_ZAMKNIETO.format(kuweta=kuweta or NR.BRAK_DANYCH, zab=zab or NR.BRAK_DANYCH), "informacja",
                                            "rano_brak_zamkniety", zawijaj=True))
            b = guzik(ST.PRZYCISKI["cofnij_zamkniecie_reczne"], f"brak_cofnij_{projekt_id}", None, self._cofnij)
            b.setEnabled(jest_osoba)
            self._reczne.addWidget(b, 0, Qt.AlignmentFlag.AlignLeft)
        self.reczne.setVisible(self._reczne.count() > 0 and not self._ostatni_piec)

    def ustaw_uklad(self, u: motyw.Uklad) -> None:
        self._uklad = u
        self._u.setContentsMargins(u.bok, 12 if u.zwarty else 16, u.bok, 12 if u.zwarty else 16)
        self._u.setSpacing(6 if u.zwarty else 8)
        self._sygnatura = None

    @staticmethod
    def _brakuje(z) -> str:
        return ", ".join(b.zeby or NR.BRAK_DANYCH for b in z.brakujace) or NR.LISTA_PUSTA

    @staticmethod
    def _stany(z) -> str:
        return ", ".join(dict.fromkeys(b.napis for b in z.brakujace)) or NR.LISTA_PUSTA

    def ustaw(self, rano, stan=None) -> None:
        self._stan = stan
        excel = stan is not None and stan.excel is not None
        zalegle = stan.excel.zalegle if excel else ()
        sygnatura = (rano, self._uklad, stan.operator if stan is not None else None, self._wybrane, self._ostatnie, excel, zalegle)
        if sygnatura == self._sygnatura:
            return
        self._sygnatura = sygnatura
        u = self._uklad
        if rano is None or rano.sesja_pieca_id is None:
            self.tytul.setText(NR.WYNIK_BRAK)
        elif self._ostatni_piec:
            self.tytul.setText(NR.WYNIK_TYTUL_OSTATNI.format(nr=rano.nr_w_dniu, doba=dzien(rano.data), godzina=godzina(rano.zamknieto),
                                                             osoba=rano.zamknal or NR.BRAK_DANYCH))
        elif rano.otwarty:
            self.tytul.setText(NR.WYNIK_TYTUL_OTWARTY.format(nr=rano.nr_w_dniu))
        else:
            self.tytul.setText(NR.WYNIK_TYTUL_ZAMKNIETY.format(nr=rano.nr_w_dniu, godzina=godzina(rano.zamknieto), osoba=rano.zamknal or NR.BRAK_DANYCH))
        kompletne = rano.kompletne if rano is not None else ()
        braki = rano.braki if rano is not None else ()
        self.przycisk_excel.setVisible(excel and rano is not None and rano.sesja_pieca_id is not None and not rano.otwarty and bool(kompletne))
        self.przycisk_excel.setEnabled(stan is not None and stan.operator is not None)
        wyczysc(self._zalegle)
        if zalegle:
            self._zalegle.addWidget(etykieta(NR.EXCEL_ZALEGLE, "tresc"))
            for sid, nr, d, ile in zalegle:
                b = guzik(NR.EXCEL_ZALEGLY.format(nr=nr or "?", doba=dzien(d) if d else "?", ile=ile), f"{self._prefiks}_{sid}", "lacze",
                          lambda sid=sid: self.ekran.pokaz_excel(sid) if self.ekran is not None else None)
                b.setEnabled(stan.operator is not None)
                self._zalegle.addWidget(b)
        self.zalegle.setVisible(bool(zalegle))
        self.kompletne_tytul.setText(NR.KOMPLETNE_TYTUL.format(n=len(kompletne)))
        wypelnij(self.kompletne, [[z.kuweta or NR.BRAK_DANYCH, NR.PUNKTY.format(rozpoznane=z.rozpoznane, punktow=z.punktow),
                                   NR.UWAGA_DOFREZOWANY if z.z_dofrezowaniem else ""] for z in kompletne], u)
        self.braki_tytul.setText(NR.BRAKI_TYTUL.format(n=len(braki)))
        wypelnij(self.braki, [[z.kuweta or NR.BRAK_DANYCH, self._brakuje(z), self._stany(z)] for z in braki], u)
        # E3-P14 (N3): prace bez rozstrzygniecia NAZWANE (plytka, gniazdo, napis statusu) - takze po "Zamknij piec"
        nier = tuple(getattr(rano, "nierozstrzygniete_prace", ()) or ()) if rano is not None else ()
        tekst = ""
        if nier:
            wzor = NR.NIEROZSTRZYGNIETE if rano.otwarty else NR.NIEROZSTRZYGNIETE_ZAMKNIETY
            tekst = wzor.format(n=len(nier), lista=lista_nierozstrzygnietych(nier), brak=ST.STANY_PUNKTU["brak_po_piecu"])
        self.nierozstrzygniete.setText(tekst)
        self.nierozstrzygniete.setVisible(bool(tekst))
        poprawki = rano.poprawki if rano is not None else ()

        def lista(pozycje) -> str:
            return ", ".join(f"{x.kuweta or NR.BRAK_DANYCH} ({NR.ZAB_KROTKO.format(zab=x.zeby or NR.BRAK_DANYCH)})" for x in pozycje)

        odhaczone = [x for x in poprawki if x.zlecenie_odhaczone]  # Z9 / A6 D2: dwa znaczenia bursztynu - dwa napisy (P5)
        rozpoznane = [x for x in poprawki if not x.zlecenie_odhaczone]
        self.poprawki.setText(NR.POPRAWKI_TYTUL.format(lista=lista(odhaczone)) if odhaczone else "")
        self.poprawki.setVisible(bool(odhaczone))
        self.juz_rozpoznane.setText(NR.JUZ_ROZPOZNANE_TYTUL.format(lista=lista(rozpoznane)) if rozpoznane else "")
        self.juz_rozpoznane.setVisible(bool(rozpoznane))
        biezace = rano.braki_biezace if rano is not None and not self._ostatni_piec else ()
        self._biezace = tuple(biezace)
        self.biezace_tytul.setText(NR.BRAKI_BIEZACE_TYTUL.format(n=len(biezace)))
        wypelnij(self.biezace, [[z.kuweta or NR.BRAK_DANYCH, self._brakuje(z), self._stany(z), str(z.ostatni_piec or NR.BRAK_DANYCH)]
                                for z in biezace], u, dane=[z.zlecenie_id for z in biezace])
        indeks = next((i for i, z in enumerate(biezace) if z.zlecenie_id == self._wybrane), None)
        if indeks is not None:
            self.biezace.selectRow(indeks)
        self._odswiez_reczne(stan)


# ----------------------------------------------------------------------------
# ekran poranny
# ----------------------------------------------------------------------------
class EkranRano(QWidget):
    """Strona "Poranek" okna. ``okno`` - ``OknoStanowiska`` (kontroler, polecenia, lista bledow, osoba)."""

    def __init__(self, okno):
        super().__init__()
        self.setObjectName("ekran_rano")
        self._okno = weakref.ref(okno)  # D7: bez cyklu okno <-> ekran
        self.k = okno.k
        self._uklad = motyw.UKLAD_WYSOKI
        self._stan = None
        self._wybor: tuple | None = None  # (skan_id, gniazdo) pokazanej pracy
        self._plytka_wybrana: int | None = None  # plytka wskazana kafelkiem (obwodka karty mapy)
        self._bufor = ""
        self._strona = "rozkladanie"
        self._numer_dla: int | None = None  # skan_id plytki z otwartym wyborem numeru
        self._pytanie_zamkniecia: int | None = None  # E3-P14 (N3): piec, o ktorego zamkniecie mimo prac bez rozstrzygniecia pyta ekran
        self._piec_widziany: tuple | None = None
        self._excel_widoczne = False
        self._excel_piec: int | None = None
        self._strona_przed_excelem = "wynik"
        self._obrazy: dict = {}
        self._karty: dict[int, KartaMapy] = {}
        self._sygnatury: dict = {}
        self._klucze_uwag: tuple = ()
        self._nr_uwagi = 0
        self._ochrona = self._zegar(self._koniec_ochrony)
        self._ochrona_strefy = self._zegar(lambda: self.strefa.chron(False))
        self._zbuduj()

    def _zegar(self, po_czasie) -> QTimer:
        zegar = QTimer(self)
        zegar.setSingleShot(True)
        zegar.setInterval(OCHRONA_MS)
        zegar.timeout.connect(po_czasie)
        return zegar

    @property
    def okno(self):
        return self._okno()

    # --- budowa ------------------------------------------------------------------------------------------------------
    def _zbuduj(self) -> None:
        korzen = QHBoxLayout(self)
        korzen.setContentsMargins(0, 0, 0, 0)
        korzen.setSpacing(0)
        self.piec = PanelPieca(self)
        korzen.addWidget(self.piec)
        # zgodnosc nazw z poprzednim ukladem (testy, narzedzia)
        self.tytul, self.blokady, self.ostrzezenia = self.piec.tytul, self.piec.blokady, self.piec.ostrzezenia
        self.zamknij_piec, self.otworz_piec, self.cofnij_przeniesienie = self.piec.zamknij_piec, self.piec.otworz_piec, self.piec.cofnij_przeniesienie
        self.legenda, self.nieaktywne = self.piec.legenda, self.piec.nieaktywne

        srodek = QWidget()
        srodek.setObjectName("rano_srodek")
        su = QVBoxLayout(srodek)
        su.setContentsMargins(0, 0, 0, 0)
        su.setSpacing(0)
        self.strefa = C.StrefaKomunikatow()
        self.strefa.setObjectName("rano_strefa_komunikatow")
        self.strefa._pusta.setObjectName("rano_strefa_pusta")  # nazwy obiektow strefy wieczornej zostaja jednoznaczne
        self.strefa.polecenie.connect(slaba(self._polecenie_strefy))
        self.strefa.nastepna.connect(slaba(self._nastepna_uwaga))
        su.addWidget(self.strefa)
        self.zakladki = QFrame()
        self.zakladki.setObjectName("rano_zakladki")
        self._zakladki_uklad = zu = QHBoxLayout(self.zakladki)
        zu.setSpacing(4)
        self.przycisk_rozkladanie = guzik(NR.STRONA_ROZKLADANIE, "rano_strona_rozkladanie", "zakladka", lambda: self._pokaz_strone("rozkladanie"))
        self.przycisk_wynik = guzik(NR.STRONA_WYNIK, "rano_strona_wynik", "zakladka", lambda: self._pokaz_strone("wynik"))
        self.przycisk_ostatni = guzik(NR.STRONA_OSTATNI, "rano_strona_ostatni", "zakladka", lambda: self._pokaz_strone("ostatni"))
        self.przycisk_excel = guzik(NR.STRONA_EXCEL, "rano_strona_excel", "zakladka", lambda: self._pokaz_strone("excel"))
        self.przycisk_excel.setToolTip(NR.STRONA_EXCEL_OPIS)
        self.przyciski_stron = {"rozkladanie": self.przycisk_rozkladanie, "wynik": self.przycisk_wynik, "ostatni": self.przycisk_ostatni,
                                "excel": self.przycisk_excel}
        pogrubiona = QFontMetrics(motyw.czcionka(motyw.PX_PODSTAWOWY, True))
        for b in self.przyciski_stron.values():
            b.setCheckable(True)
            b.setMinimumWidth(pogrubiona.horizontalAdvance(b.text()) + 2 * 14 + 8)  # wybrana zakladka ma napis pogrubiony - bez ucinania
            zu.addWidget(b, 0, Qt.AlignmentFlag.AlignBottom)
        zu.addStretch(1)
        self.przycisk_ostatni.setVisible(False)
        self.przycisk_excel.setVisible(False)
        su.addWidget(self.zakladki)
        self._stos = QStackedLayout()
        strona = QWidget()
        strona.setObjectName("rano_strona_rozkladania")
        rs = QVBoxLayout(strona)
        rs.setContentsMargins(0, 0, 0, 0)
        rs.setSpacing(0)
        self.wiersz_kuwety = WierszKuwety(self)
        rs.addWidget(self.wiersz_kuwety)
        self.plytki = PoleMap()
        self._mapy_uklad = mu = QVBoxLayout()
        mu.addWidget(self.plytki, 1)
        rs.addLayout(mu, 1)
        self.bez_plytek = etykieta(NR.PIEC_BRAK, "tresc_glowna", "rano_bez_plytek", zawijaj=True)
        self.bez_plytek.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.plytki.ustaw_karty([], self.bez_plytek)
        self._stos.addWidget(strona)
        self.wynik = PanelWyniku(self)
        self._stos.addWidget(self.wynik)
        self.ostatni = PanelWyniku(self, ostatni=True)
        self._stos.addWidget(self.ostatni)
        self.excel = PanelExcela(self)  # E3-A12: okno "Excel: wskaz wiersz" - zakladka "Excel"
        self._stos.addWidget(self.excel)
        su.addLayout(self._stos, 1)
        korzen.addWidget(srodek, 1)

        self.prawa = QFrame()
        self.prawa.setObjectName("rano_prawa_kolumna")
        self.prawa.setFixedWidth(motyw.UKLAD_WYSOKI.prawa)
        self._prawa_stos = QStackedLayout(self.prawa)
        self.kuwety = PanelKuwet(self)
        self._prawa_stos.addWidget(self.kuwety)
        self.widok = WidokPracyRano(self.k.projekty_kuwety, slaba(self._obraz))
        self.widok.polecenie.connect(lambda nazwa, argumenty: self._polecenie(nazwa, *argumenty))
        self.widok.zamknij.connect(self._zamknij_prace)
        self.widok.po_zmianie(slaba(self._odswiez))
        self._prawa_stos.addWidget(self.widok)
        korzen.addWidget(self.prawa)

    def ustaw_uklad(self, u: motyw.Uklad) -> None:
        """Uklad okna (``motyw.uklad_dla``): szerokosci kolumn, stale wysokosci strefy, zakladek i wiersza kuwety, odstepy."""
        self._uklad = u
        self.piec.ustaw_uklad(u)
        self.strefa.ustaw_uklad(u)
        self.zakladki.setFixedHeight(u.zakladki)
        for b in self.przyciski_stron.values():
            b.setFixedHeight(u.zakladki - 4)
        self._zakladki_uklad.setContentsMargins(u.bok_rano, 0, u.bok_rano, 0)
        self.wiersz_kuwety.ustaw_uklad(u)
        self._mapy_uklad.setContentsMargins(u.bok_rano, 8 if u.zwarty else 12, u.bok_rano, 8 if u.zwarty else 12)
        self.plytki.ustaw_odstep(8)
        for karta in self._karty.values():
            karta.mapa.setMinimumSize(*u.mapa_rano_min)
        self.prawa.setFixedWidth(u.prawa_rano)
        self.kuwety.ustaw_uklad(u)
        self.widok.ustaw_uklad(u)
        self.wynik.ustaw_uklad(u)
        self.ostatni.ustaw_uklad(u)
        self.excel.ustaw_uklad(u)
        self._sygnatury.clear()
        if self._stan is not None:
            self._odswiez()

    # --- wejscie i wyjscie z trybu --------------------------------------------------------------------------------------
    def wejscie(self) -> None:
        """Okno przelaczylo sie na tryb poranny: mapy na miejscu mapy wieczornej - ochrona 800 ms (klikniecie wycelowane w ekran
        wieczorny nie trafia w gniazdo plytki porannej)."""
        if self._karty:
            self._wlacz_ochrone()

    def wyjscie(self) -> None:
        """Okno wraca do trybu wieczornego: strefa pytan porannych pusta (bez ukrytych przyciskow o tych samych nazwach)."""
        self.strefa.ustaw(None)
        self._klucze_uwag, self._nr_uwagi = (), 0
        self._sygnatury.pop("uwagi", None)

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
        widoczne = stan.excel is not None and stan.excel.widoczne  # E3-A12: okno Excela pokazuje sie samo, "Pozniej" je zamyka
        piec_excela = stan.excel.sesja_pieca_id if widoczne else None
        if widoczne and (not self._excel_widoczne or piec_excela != self._excel_piec):  # nowe okno Excela albo okno innego pieca
            self._strona_przed_excelem = self._strona if self._strona != "excel" else "wynik"
            self._strona = "excel"
        elif not widoczne and self._strona == "excel":
            self._strona = self._strona_przed_excelem
        self._excel_widoczne, self._excel_piec = widoczne, piec_excela
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

    def _z_tla(self) -> bool:
        okno = self.okno
        return okno is not None and getattr(okno, "_z_tla", False)

    def _odswiez(self) -> None:
        stan = self._stan
        okno = self.okno
        if stan is None or okno is None:
            return
        rano = stan.rano
        plytka, gniazdo, praca = self._wybor_pracy(rano)
        if self._wybor is not None and plytka is None:  # plytki nie ma juz w stanie (zastapiona, nowy piec): widok pracy zamkniety
            self._wybor = None
            okno._informacja = N.PRACA_ZNIKNELA
        plytki = self._plytki_widoczne(rano)
        if self._plytka_wybrana is not None and self._plytka_wybrana not in {p.skan_id for p in plytki}:
            self._plytka_wybrana = None
        self._odswiez_mapy(stan, rano, plytki)
        self._odswiez_piec(stan, rano, plytki)
        self._odswiez_uwagi(stan, rano)
        self.wiersz_kuwety.ustaw(stan, self._bufor)
        self.kuwety.ustaw(stan, self._z_tla())
        if plytka is None:
            self.widok.wyczysc()
            self._prawa_stos.setCurrentIndex(0)
        else:
            self.widok.ustaw(stan, plytka, gniazdo, praca, rano.otwarty)
            self._prawa_stos.setCurrentIndex(1)
        ostatni = rano.ostatni_zamkniety if rano is not None else None
        if self._strona == "ostatni" and ostatni is None:
            self._strona = "wynik"
        if self._strona == "excel" and not self._excel_widoczne:
            self._strona = "wynik"
        if self._strona == "wynik":  # D13: zakladka ukryta nie jest przebudowywana (dostanie stan przy pokazaniu)
            self.wynik.ustaw(rano, stan)
        elif self._strona == "ostatni":
            self.ostatni.ustaw(ostatni, stan)
        elif self._strona == "excel":
            self.excel.ustaw(stan)
        self.przycisk_ostatni.setVisible(ostatni is not None)
        self.przycisk_excel.setVisible(stan.excel is not None)
        self.przycisk_excel.setEnabled(self._excel_widoczne)
        for nazwa, b in self.przyciski_stron.items():
            b.setChecked(self._strona == nazwa)
        self._stos.setCurrentIndex(STRONY.index(self._strona))

    def _odswiez_mapy(self, stan, rano, plytki: list) -> None:
        zestaw = tuple(p.skan_id for p in plytki)
        if self._zmienione("zestaw", zestaw):
            stare = set(self._karty)
            self._karty = {}
            karty = []
            for p in plytki:
                karta = KartaMapy(p.skan_id, self)
                karta.mapa.setMinimumSize(*self._uklad.mapa_rano_min)
                self._karty[p.skan_id] = karta
                karty.append(karta)
            pusty = None
            if not plytki:
                self.bez_plytek = etykieta(NR.PIEC_BRAK if rano is None or rano.sesja_pieca_id is None else NR.PIEC_ZAMKNIETY_INFO,
                                           "tresc_glowna", "rano_bez_plytek", zawijaj=True)
                self.bez_plytek.setAlignment(Qt.AlignmentFlag.AlignCenter)
                pusty = self.bez_plytek
            self.plytki.ustaw_karty(karty, pusty)
            if stare and stare != set(self._karty):  # inny zestaw plytek: mapy przesunely sie - klikniecie moglo celowac w poprzedni obraz
                self._wlacz_ochrone()
        for p in plytki:
            karta = self._karty[p.skan_id]
            C.ustaw_role(karta, "true" if p.skan_id == self._plytka_wybrana else "false", "wybrany")
            karta.tytul.setText(nazwa_plytki(p.numer) + ("" if p.aktywna else NR.ODSTEP_NAPISU + p.napis))
            karta.godzina.setText(NR.SKAN_Z.format(godzina=godzina(p.czas)) if p.czas else "")
            karta.poza.setText(NR.POZA_GNIAZDAMI.format(n=len(p.poza_gniazdem)) if p.poza_gniazdem else "")
            karta.poza.setVisible(bool(p.poza_gniazdem))
            geometria = geometria_ukladu(self.k, p.uklad) if p.gniazda and (p.aktywna or p.prace) else None
            for pr in p.prace:
                for sha, dane in ((pr.sha16, pr.miniatura), *((k.sha16, k.miniatura) for k in pr.kandydaci)):
                    self._obraz(sha, dane)
            wybrane = self._wybor[1] if self._wybor is not None and self._wybor[0] == p.skan_id else None
            karta.mapa.ustaw_rano(p, geometria, wybrane, rano.obwodka(p.skan_id), self._obrazy)  # P4: gniazda kuwety z kontrolera
            if self._ochrona.isActive():
                karta.mapa.przygas(True)

    def _odswiez_piec(self, stan, rano, plytki: list) -> None:
        panel = self.piec
        if rano is None or rano.sesja_pieca_id is None:
            panel.tytul.setText(NR.PIEC_TYTUL_BRAK)
            panel.opis.setText(NR.PIEC_BRAK)
        elif rano.otwarty:
            panel.tytul.setText(NR.PIEC_TYTUL.format(nr=rano.nr_w_dniu))
            panel.opis.setText(NR.PIEC_OPIS_OTWARTY.format(doba=dzien(rano.data), godzina=godzina(rano.otwarto)))
        else:
            panel.tytul.setText(NR.PIEC_TYTUL.format(nr=rano.nr_w_dniu))
            panel.opis.setText(NR.PIEC_OPIS_ZAMKNIETY.format(doba=dzien(rano.data), godzina=godzina(rano.zamknieto), osoba=rano.zamknal or NR.BRAK_DANYCH))
        ostrzezenia = ((NR.PIEC_Z_WCZORAJ,) if rano is not None and rano.otwarty and rano.z_poprzedniej_doby else ()) + \
            (tuple(rano.ostrzezenia) if rano is not None else ())
        panel.ostrzezenia.setText(" ".join(dict.fromkeys(ostrzezenia)))
        panel.ostrzezenia.setVisible(bool(ostrzezenia))
        # kafelki plytek
        jest_osoba = stan.operator is not None
        pytane = {(q.skan_id, PYTANE.get(q.rodzaj)) for q in stan.pytania if not q.ukryte}
        nier: dict = {}
        for x in (getattr(rano, "nierozstrzygniete_prace", ()) or ()) if rano is not None else ():
            nier[x.skan_id] = nier.get(x.skan_id, 0) + 1
        zestaw = tuple(p.skan_id for p in plytki)
        if self._zmienione("kafelki", zestaw):
            wyczysc(panel._kafelki)
            for p in plytki:
                kafelek = KafelekPlytkiRano(p.skan_id)
                kafelek.wybrano.connect(slaba(self._klik_kafelka))
                panel._kafelki.addWidget(kafelek)
        kafelki = panel.kafelki()
        for p in plytki:
            akcje = tuple(a for a in AKCJE_PLYTKI if a in p.dozwolone and (p.skan_id, a) not in pytane)
            kafelki[p.skan_id].ustaw(p, nier.get(p.skan_id, 0), p.skan_id == self._plytka_wybrana, akcje, jest_osoba,
                                     slaba(self._przelacz_numer), slaba(self._polecenie))
        nieaktywne = [p for p in (rano.plytki if rano is not None else ()) if p.status == "zastapiony"]
        tekst = NR.PLYTKI_NIEAKTYWNE.format(lista="; ".join(NR.PLYTKA_NIEAKTYWNA.format(plytka=nazwa_plytki(p.numer), godzina=godzina(p.czas), napis=p.napis)
                                                           for p in nieaktywne)) if nieaktywne else ""
        panel.nieaktywne.setText(tekst)
        panel.nieaktywne.setVisible(bool(tekst))
        # legenda "Na plytkach": liczniki klas pieca (napis na kolorze statusu) i statusy gniazd spoza licznikow (kropka i napis)
        liczniki = tuple((k, (rano.liczniki or {}).get(k, 0)) for k in KOLEJNOSC_KLAS) if rano is not None else ()
        pozycje: dict = {}
        for p in plytki:
            for g in p.gniazda:
                if g.prace and g.status != "pusty":
                    w = ST.status(g.status)
                    pozycje.setdefault((w.napis, g.rgb), w.opis)
        if self._zmienione("legenda", (liczniki, tuple(pozycje.items()))):
            wyczysc(panel.liczniki)
            pokazane = set()
            for klasa, n in liczniki:
                if n:
                    w = ST.status_rano(klasa)
                    z = znaczek(NR.LICZNIK.format(napis=w.napis, n=n), w.hex, f"rano_licznik_{klasa}", rozmiar_px=motyw.PX_POMOCNICZY)
                    z.setToolTip(w.opis)
                    panel.liczniki.addWidget(z)
                    pokazane.add((w.napis, w.hex.lower()))
            wyczysc(panel._pozycje)
            for (napis, rgb), opis in pozycje.items():
                if (napis, (rgb or "").lower()) in pokazane:
                    continue
                pole = QWidget()
                pu = QHBoxLayout(pole)
                pu.setContentsMargins(0, 0, 0, 0)
                pu.setSpacing(6)
                pu.addWidget(Kropka(rgb, 10), 0, Qt.AlignmentFlag.AlignVCenter)
                pu.addWidget(etykieta(napis, "tresc"), 1)
                pole.setToolTip(opis)
                panel._pozycje.addWidget(pole)
            panel._liczniki_pole.setVisible(panel.liczniki.count() > 0)
            panel.legenda.setVisible(panel.liczniki.count() > 0 or panel._pozycje.count() > 0)
        # blokady i polecenia pieca
        blokady = tuple(rano.blokady) if rano is not None else ()  # z kontrolera - takze "trwa analiza / skanowanie" (D1, P3)
        panel.blokady.setText("\n".join(NR.BLOKADA_PUNKT.format(tekst=b) for b in blokady))
        panel.blokady.setVisible(bool(blokady))
        panel.blokady_naglowek.setVisible(bool(blokady) and rano is not None and rano.otwarty)
        panel.zamknij_piec.setVisible(rano is not None and rano.otwarty)
        panel.zamknij_piec.setEnabled(rano is not None and "zamknij_piec" in rano.dozwolone and jest_osoba)
        panel.zamknij_piec.setToolTip(" ".join(blokady))
        panel.otworz_piec.setVisible(rano is not None and "otworz_piec_ponownie" in rano.dozwolone)
        panel.otworz_piec.setEnabled(jest_osoba)
        panel.cofnij_przeniesienie.setVisible(rano is not None and "cofnij_przeniesienie" in rano.dozwolone)  # A6 runda 5
        panel.cofnij_przeniesienie.setEnabled(jest_osoba)

    # --- strefa pytan --------------------------------------------------------------------------------------------------
    def pozycje_strefy(self, stan, rano) -> tuple:
        """(pozycje strefy pytan w kolejnosci waznosci, bledy programu): pytanie przed "Zamknij piec", informacja ekranu, odmowa
        spoza stanu, wybor numeru plytki, pytania plytek pieca, ich komunikaty i pozostale komunikaty ogolne (od najnowszego,
        jednakowe razem). Bledy programu (poziom "blad" albo trwale) ida na liste bledow okna."""
        okno = self.okno
        pokaz_osobe = stan.wymaga_operatora or okno._zmiana_osoby  # liste osob pokazuje szkielet okna (pod paskiem gornym)
        skany_rano = {p.skan_id for p in rano.plytki} if rano is not None else set()
        wszystkie = [k for k in stan.komunikaty if not k.ukryte]
        pytania = [q for q in stan.pytania if not q.ukryte and q.skan_id in skany_rano]
        plytkowe = [k for k in wszystkie if k.skan_id is not None and k.skan_id in skany_rano]
        ogolne = [k for k in wszystkie if k.skan_id is None or stan.plytka(k.skan_id) is None and k.skan_id not in skany_rano]
        ogolne = [k for k in ogolne if not (pokaz_osobe and k.rodzaj in ("brak_operatora", "nowa_zmiana", "pusta_lista_operatorow", "osoba_spoza_listy"))]
        nr = okno._nr_komunikatow
        ogolne.sort(key=lambda k: -nr.get(k.id, 0))
        bledy = [k for k in ogolne if blad_programu(k)]
        reszta = [k for k in ogolne if not blad_programu(k)]
        jest_osoba = stan.operator is not None
        pozycje = []
        do_zamkniecia = self._prace_pytania_zamkniecia(rano)  # E3-P14 (N3): pytanie ekranu przed "Zamknij piec"
        if do_zamkniecia:  # pierwsze: pytanie, na ktore osoba wlasnie czeka
            ile = ST.odmiana(len(do_zamkniecia), *NR.ZAMKNIJ_MIMO_ILE).format(n=len(do_zamkniecia))
            pozycje.append(C.Uwaga("pytanie_zamknij_mimo", "ostrzezenie", NR.ZAMKNIJ_MIMO_TYTUL,
                                   NR.ZAMKNIJ_MIMO_TEKST.format(ile=ile, lista=lista_nierozstrzygnietych(do_zamkniecia),
                                                                brak=ST.STANY_PUNKTU["brak_po_piecu"]),
                                   (("zamknij_mimo_tak", NR.ZAMKNIJ_MIMO_TAK, LOKALNE_ZAMKNIJ_MIMO_TAK, (), jest_osoba, "wglebiony"),
                                    ("zamknij_mimo_wroc", NR.ZAMKNIJ_MIMO_WROC, LOKALNE_ZAMKNIJ_MIMO_WROC, (), True, "glowny")),
                                   klucz=("zamknij_mimo", self._pytanie_zamkniecia)))
        if okno._informacja:
            pozycje.append(C.uwaga_informacji(okno._informacja))
        if okno._odmowa:
            pozycje.append(C.uwaga_odmowy(okno._odmowa))
        if self._numer_dla is not None and rano is not None:
            p = rano.plytka(self._numer_dla)
            if p is not None and "podaj_numer_plytki" in p.dozwolone and not any(q.rodzaj == "brak_numeru_plytki" and q.skan_id == p.skan_id for q in pytania):
                geometria = geometria_ukladu(self.k, p.uklad)
                numery = tuple(geometria.numery) if geometria is not None and geometria.numery else K.NUMERY_PLYTEK_ZAPASOWE
                brak = ST.tekst_komunikatu("brak_operatora" if stan.operatorzy else "pusta_lista_operatorow")[2]
                czas = godzina(p.czas)
                nazwa = nazwa_plytki(p.numer)
                pozycje.append(C.uwaga_numeru(p.skan_id, numery, p.numer, jest_osoba, brak,
                                              N.PLYTKA_ZE_SKANEM.format(plytka=nazwa, godzina=czas) if czas else nazwa, czas))
            else:
                self._numer_dla = None
        for q in pytania:
            p = rano.plytka(q.skan_id)
            czas = godzina(p.czas) if p is not None else ""
            ze_skanem = ""
            if p is not None and p.numer is not None:
                ze_skanem = N.PLYTKA_ZE_SKANEM.format(plytka=nazwa_plytki(p.numer), godzina=czas) if czas else nazwa_plytki(p.numer)
            pozycje.append(C.uwaga_pytania(q, stan, p.typ if p is not None else None, ze_skanem, czas))
        grupy = [(k,) for k in plytkowe] + [tuple(g) for g in self._grupuj(reszta)]
        grupy.sort(key=lambda g: (RANGA_POZIOMU.get(g[0].poziom, 1), -max(nr.get(k.id, 0) for k in g)))
        for g in grupy:
            p = rano.plytka(g[0].skan_id) if rano is not None and g[0].skan_id is not None else None
            if p is not None:
                czas = godzina(p.czas)
                nazwa = nazwa_plytki(p.numer)
                tytul = (N.PLYTKA_ZE_SKANEM.format(plytka=nazwa, godzina=czas) if czas else nazwa) if p.numer is not None else C.tytul_ze_skanem(nazwa, czas)
                pozycje.append(C.uwaga_komunikatu(g, tytul))
            else:
                pozycje.append(C.uwaga_komunikatu(g))
        return tuple(pozycje), bledy

    @staticmethod
    def _grupuj(komunikaty) -> list:
        grupy: dict = {}
        for k in komunikaty:
            grupy.setdefault((k.rodzaj, k.poziom, k.tytul, k.tekst), []).append(k)
        return list(grupy.values())

    def _odswiez_uwagi(self, stan, rano) -> None:
        pozycje, bledy = self.pozycje_strefy(stan, rano)
        okno = self.okno
        okno._odswiez_bledy(stan, bledy)
        klucze = tuple(u.klucz for u in pozycje)
        if klucze != self._klucze_uwag:  # zestaw pozycji sie zmienil: strefa wraca do najwazniejszej
            self._klucze_uwag, self._nr_uwagi = klucze, 0
        nr = self._nr_uwagi % len(pozycje) if pozycje else 0
        przed = self.strefa.klucz()
        self.strefa.ustaw(pozycje[nr] if pozycje else None, max(0, len(pozycje) - 1))
        po = self.strefa.klucz()
        # S3-3: pozycja strefy zmienila sie w tle na inna - klikniecie wycelowane w poprzednia nie trafia w nowa przez OCHRONA_MS
        if self._z_tla() and przed is not None and po is not None and po != przed:
            self._ochrona_strefy.start()
            self.strefa.chron(True)

    def ochrona_strefy_aktywna(self) -> bool:
        return self._ochrona_strefy.isActive()

    def _nastepna_uwaga(self) -> None:
        self._nr_uwagi += 1
        self._odswiez()

    def _polecenie_strefy(self, nazwa: str, argumenty: tuple) -> None:
        okno = self.okno
        if okno is not None:
            okno._polecenie_panelu(nazwa, argumenty)

    def odpowiedz_lokalna(self, nazwa: str) -> None:
        """Przycisk strefy obslugiwany przez ekran poranny (``LOKALNE``): odpowiedz na pytanie przed "Zamknij piec"."""
        if nazwa in LOKALNE:
            self._odpowiedz_zamkniecia(nazwa)

    # --- piec ----------------------------------------------------------------------------------------------------------
    def _zamknij_piec(self) -> None:
        """"Zamknij piec" POKAZANEGO pieca (A6 runda 2, P3: spoznione klikniecie nie zamknie nastepnego pieca). E3-P14 (N3): gdy
        w piecu sa prace bez rozstrzygniecia (``StanRano.nierozstrzygniete_prace``), przycisk NIE zamyka - ekran pyta (ile prac,
        ktore plytki i gniazda); zamyka dopiero odpowiedz "Zamknij piec mimo to" (``_odpowiedz_zamkniecia``)."""
        rano = self._stan.rano if self._stan is not None else None
        if rano is None or rano.sesja_pieca_id is None:
            return
        if getattr(rano, "nierozstrzygniete_prace", ()):
            self._pytanie_zamkniecia = rano.sesja_pieca_id
            self._odswiez()
            return
        self._polecenie("zamknij_piec", rano.sesja_pieca_id)

    def _odpowiedz_zamkniecia(self, nazwa: str, _argumenty: tuple = ()) -> None:
        """Odpowiedz na pytanie "Zamknac piec mimo prac bez rozstrzygniecia?": "Wroc do rozstrzygania" (domyslna) - piec zostaje
        otwarty, ekran otwiera pierwsza prace bez rozstrzygniecia; "Zamknij piec mimo to" - polecenie ``zamknij_piec``."""
        piec, self._pytanie_zamkniecia = self._pytanie_zamkniecia, None
        rano = self._stan.rano if self._stan is not None else None
        if rano is None or piec is None or rano.sesja_pieca_id != piec or not rano.otwarty:
            self._odswiez()
            return
        if nazwa == LOKALNE_ZAMKNIJ_MIMO_TAK:
            self._polecenie("zamknij_piec", piec)
            return
        pierwsza = next((x for x in rano.nierozstrzygniete_prace if x.gniazdo is not None), None)
        if pierwsza is not None:
            self._wybor = (pierwsza.skan_id, pierwsza.gniazdo)
            self._strona = "rozkladanie"
        self._odswiez()

    def _prace_pytania_zamkniecia(self, rano) -> tuple:
        """Prace, o ktore pyta ekran przed "Zamknij piec" - tylko dla pokazanego, otwartego pieca; pusta krotka = pytania nie ma
        (piec zamkniety, inny piec, wszystko rozstrzygniete - wtedy pytanie samo znika)."""
        prace = tuple(getattr(rano, "nierozstrzygniete_prace", ()) or ()) if rano is not None else ()
        if self._pytanie_zamkniecia is None or rano is None or not rano.otwarty or rano.sesja_pieca_id != self._pytanie_zamkniecia or not prace:
            self._pytanie_zamkniecia = None
            return ()
        return prace

    def _otworz_piec(self) -> None:
        self._polecenie_pieca("otworz_piec_ponownie")

    def _polecenie_pieca(self, nazwa: str) -> None:
        """Polecenie dla POKAZANEGO pieca (jawny ``sesja_pieca_id``)."""
        rano = self._stan.rano if self._stan is not None else None
        if rano is not None and rano.sesja_pieca_id is not None:
            self._polecenie(nazwa, rano.sesja_pieca_id)

    # --- polecenia i wybor osoby ----------------------------------------------------------------------------------------
    def _polecenie(self, nazwa: str, *argumenty):
        okno = self.okno
        return okno._polecenie(nazwa, *argumenty) if okno is not None else None

    def potwierdz_kuwete(self) -> None:
        """Enter / "Rozlozona": polecenie z kuweta POKAZANA na ekranie (B1 - kontroler odmowi, gdy biezaca jest juz inna)."""
        rano = self._stan.rano if self._stan is not None else None
        self._polecenie("potwierdz_kuwete", (rano.kuweta_biezaca if rano is not None else None) or "")

    def cofnij_kuwete(self) -> None:
        """Backspace / "Cofnij poprzednia": cofa POKAZANA ostatnia potwierdzona kuwete; w strefie napis, co cofnieto (D3)."""
        rano = self._stan.rano if self._stan is not None else None
        kuweta = (rano.kuweta_do_cofniecia if rano is not None else None) or ""
        odpowiedz = self._polecenie("cofnij_kuwete", kuweta)
        if odpowiedz is not None and odpowiedz.ok and self.okno is not None:
            self.okno._informacja = NR.KUWETA_COFNIETA.format(kuweta=odpowiedz.dane)
            self._odswiez()

    def numer_podany(self) -> None:
        """Wybor numeru plytki zamkniety (numer podany albo "Bez zmian")."""
        self._numer_dla = None

    def pokaz_excel(self, sesja_pieca_id: int):
        """"Excel: wskaz wiersz" (wynik pieca, zalegly piec): polecenie ``excel_pokaz``; po udanym - zakladka "Excel" TAKZE wtedy,
        gdy okno Excela bylo juz otwarte dla tego pieca, a osoba przeszla na inna zakladke (runda 2, P2; ``pokaz`` przelacza
        zakladke sam tylko przy nowym oknie Excela albo innym piecu)."""
        odpowiedz = self._polecenie("excel_pokaz", sesja_pieca_id)
        if odpowiedz is not None and odpowiedz.ok and self._excel_widoczne and self._strona != "excel":
            self._strona_przed_excelem = self._strona
            self._strona = "excel"
            self._odswiez()
        return odpowiedz

    def _pokaz_strone(self, strona: str) -> None:
        if strona == "excel" and not self._excel_widoczne:
            return
        self._strona = strona
        self._odswiez()

    def _przelacz_numer(self, skan_id: int) -> None:
        self._numer_dla = None if self._numer_dla == skan_id else skan_id
        self._odswiez()

    def _klik_kafelka(self, skan_id: int) -> None:
        """Kafelek plytki: plytka wybrana (obwodka karty mapy); gdy ma prace bez rozstrzygniecia - otwiera pierwsza z nich."""
        self._plytka_wybrana = skan_id
        rano = self._stan.rano if self._stan is not None else None
        pierwsza = next((x for x in (getattr(rano, "nierozstrzygniete_prace", ()) or ()) if x.skan_id == skan_id and x.gniazdo is not None), None) \
            if rano is not None else None
        if pierwsza is not None:
            self._wybor = (skan_id, pierwsza.gniazdo)
        self._strona = "rozkladanie"
        self._odswiez()

    def _klik_gniazdo(self, skan_id: int, nr: int) -> None:
        if self.ochrona_aktywna():
            return
        self._wybor = (skan_id, nr)
        self._plytka_wybrana = skan_id
        self._strona = "rozkladanie"
        self._odswiez()

    def _zamknij_prace(self) -> None:
        self._wybor = None
        self._odswiez()

    def _wlacz_ochrone(self) -> None:
        self._ochrona.start()
        for karta in self._karty.values():
            karta.mapa.przygas(True)

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

    def miejsca_map(self) -> dict:
        """skan_id -> prostokat mapy w oknie (do testow: mapy nie zmieniaja miejsca przy zmianie stanu)."""
        okno = self.okno
        return {s: QRect(k.mapa.mapTo(okno, QPoint(0, 0)), k.mapa.size()) for s, k in self._karty.items()} if okno is not None else {}

    def bufor(self) -> str:
        return self._bufor

    def strona(self) -> str:
        return self._strona

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
        # E3-P14 runda 2 (D2): otwarte pytanie "Zamknac piec mimo prac bez rozstrzygniecia?" przejmuje Enter i Esc - Enter
        # wcisniety "na pytanie" nie zapisuje "Rozlozona" biezacej kuwety (zaden klawisz pieca nie zamyka), Esc = "Wroc do
        # rozstrzygania". Ramka poranna nie wysyla klawiszy do okna (zdarzenia ida przez kontroler) - jej Enter dziala jak dotad
        if self._pytanie_zamkniecia is not None and not self._bufor:
            if klawisz in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                return True
            if klawisz == Qt.Key.Key_Escape:
                self._odpowiedz_zamkniecia(LOKALNE_ZAMKNIJ_MIMO_WROC)
                return True
        if klawisz in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self._bufor:
                bufor, self._bufor = self._bufor, ""
                self._polecenie("wybierz_kuwete", bufor)
                self._odswiez()
            else:
                self.potwierdz_kuwete()
            return True
        if klawisz == Qt.Key.Key_Backspace:
            if self._bufor:
                self._bufor = self._bufor[:-1]
                self._odswiez()
            elif not zdarzenie.isAutoRepeat():
                self.cofnij_kuwete()
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
