"""okno_excela - okno "Excel: wskaz wiersz" ekranu porannego (paczka E3-A12): zlecenia kompletne zamknietego pieca i wiersze
arkusza zlecen proponowane przez ``excel`` (A9) do odhaczenia (kolor pola B).

Zasady (kontrakt ``kontroler_api`` w wersji 4):
* okno to PANEL w lewej kolumnie ekranu porannego (zamiast plytek pieca) - nie osobne okno modalne; pokazane, gdy
  ``stan.excel.widoczne`` (po "Zamknij piec" w trybie "pytaj", przycisk "Excel: wskaz wiersz");
* niczego nie liczy i nie zapisuje samo: lista pozycji ze ``stan.excel.pozycje``, kandydaci (kolumna H - DANE OSOBOWE, tylko
  na ekran laptopa) z zapytania ``kontroler.excel_szczegoly(piec, zlecenie)``; zapis koloru WYLACZNIE po kliknieciu "Zatwierdz"
  (``excel_zatwierdz``), "Pomin" = ``excel_pomin``, "Pozniej" = ``excel_zamknij``, "Odswiez z Excela" = ``excel_odswiez``;
  polecenia niosa tozsamosc pozycji (piec + zlecenie - recenzja PR #30 P4), nie numer na liscie;
* recenzja PR #30 B1: "Zatwierdz" i "Pomin" dzialaja tylko dla pozycji WYBRANEJ kliknieciem w liscie - po zapisie (albo po
  zmianie listy) przyciski sa nieaktywne do nastepnego klikniecia (podwojne klikniecie nie zatwierdza nastepnego zlecenia);
  wybor bez zgodnej nazwy (``do_sprawdzenia``) wymaga wskazania wiersza kandydata jak "wskaz wiersz";
* poprzednia proba z bledem (D9) i inne piece do odhaczenia (P5, przyciski ``excel_pokaz``) sa w panelu; bez osoby przyciski
  zapisu nieaktywne z wyjasnieniem.
Wlasny stan panelu to wybor osoby: wybrana pozycja (piec, zlecenie) i wskazany wiersz kandydata.
"""
from __future__ import annotations

import logging
import weakref

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractItemView, QFrame, QHeaderView, QSizePolicy, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from . import napisy_rano as NR
from . import styl
from .czesci import UkladPlynny, dzien, etykieta, przycisk, wyczysc

LOG = logging.getLogger(__name__)
KLASA_WSKAZ = "wskaz_wiersz"


def _tabela(nazwa: str, kolumny: tuple) -> QTableWidget:
    t = QTableWidget(0, len(kolumny))
    t.setObjectName(nazwa)
    t.setHorizontalHeaderLabels(list(kolumny))
    t.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    t.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    t.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    t.verticalHeader().setVisible(False)
    t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    t.horizontalHeader().setSectionsClickable(False)
    t.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    t.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    return t


def _wypelnij(t: QTableWidget, wiersze: list, r: styl.Rozmiary) -> None:
    t.setRowCount(len(wiersze))
    for i, komorki in enumerate(wiersze):
        for k, tekst in enumerate(komorki):
            pole = QTableWidgetItem(tekst)
            pole.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            t.setItem(i, k, pole)
    t.verticalHeader().setDefaultSectionSize(r.wiersz_tabeli)


def klucz_pozycji(p) -> tuple:
    """Tozsamosc pozycji okna (P4): (sesja_pieca_id, zlecenie_id)."""
    return (p.sesja_pieca_id, p.zlecenie_id)


def wymaga_wskazania(p) -> bool:
    """Pozycja, ktorej nie zatwierdza sie jednym przyciskiem: "wskaz wiersz" i wybor bez zgodnej nazwy (B1)."""
    return p.klasa == KLASA_WSKAZ or p.do_sprawdzenia


class PanelExcela(QFrame):
    """Panel "Excel: wskaz wiersz". ``ekran`` - ``EkranRano`` (polecenia przez okno, kontroler do zapytania o kandydatow)."""

    def __init__(self, ekran):
        super().__init__()
        self._ekran = weakref.ref(ekran)
        self._zalogowane: set = set()  # ostrzezenia Excela zapisane juz w logu w pelnym brzmieniu (E3-P14, poz. 1)
        self.setObjectName("excel_panel")
        self.setProperty("rola", "panel")
        self._r = styl.ZWYKLE
        self._klucz: tuple | None = None  # pokazana pozycja (piec, zlecenie)
        self._wybrana = False  # pozycja wybrana kliknieciem osoby - tylko wtedy "Zatwierdz" / "Pomin" sa aktywne (B1)
        self._wiersz: int | None = None  # wiersz kandydata wskazany przez osobe
        self._kandydaci: tuple = ()
        self._sygnatura = None
        self._stan = None
        self._u = u = QVBoxLayout(self)
        u.setContentsMargins(12, 8, 12, 8)
        u.setSpacing(6)
        self.tytul = etykieta("", "naglowek", "excel_tytul", zawijaj=True)
        u.addWidget(self.tytul)
        self.ostrzezenia = etykieta("", "slaby", "excel_ostrzezenia", zawijaj=True)
        u.addWidget(self.ostrzezenia)
        self.blad = etykieta("", "uwaga", "excel_blad", zawijaj=True)
        self.blad.setVisible(False)
        u.addWidget(self.blad)
        self.zalegle = QWidget()
        self.zalegle.setObjectName("excel_zalegle")
        self._zalegle = UkladPlynny(self.zalegle, odstep_poziomy=6, odstep_pionowy=3)
        self.zalegle.setVisible(False)
        u.addWidget(self.zalegle)
        self.tabela = _tabela("excel_tabela", NR.EXCEL_KOLUMNY)
        self.tabela.cellClicked.connect(self._klik_pozycji)
        u.addWidget(self.tabela, 2)
        self.wybierz = etykieta(NR.EXCEL_WYBIERZ, "informacja", "excel_wybierz", zawijaj=True)
        u.addWidget(self.wybierz)
        self.folder = etykieta("", "duzy", "excel_folder", zawijaj=True)
        u.addWidget(self.folder)
        self.powod = etykieta("", "slaby", "excel_powod", zawijaj=True)
        u.addWidget(self.powod)
        self.sprawdz = etykieta(NR.EXCEL_SPRAWDZ, "uwaga", "excel_sprawdz", zawijaj=True)
        self.sprawdz.setVisible(False)
        u.addWidget(self.sprawdz)
        self.poprzedni = etykieta("", "uwaga", "excel_poprzedni", zawijaj=True)
        self.poprzedni.setVisible(False)
        u.addWidget(self.poprzedni)
        u.addWidget(etykieta(NR.EXCEL_KANDYDACI_TYTUL, "slaby", "excel_kandydaci_tytul", zawijaj=True))
        self.kandydaci = _tabela("excel_kandydaci", NR.EXCEL_KANDYDACI_KOLUMNY)
        self.kandydaci.cellClicked.connect(self._klik_kandydata)
        u.addWidget(self.kandydaci, 2)
        self.bez_osoby = etykieta(NR.EXCEL_BEZ_OSOBY, "uwaga", "excel_bez_osoby", zawijaj=True)
        self.bez_osoby.setVisible(False)
        u.addWidget(self.bez_osoby)
        przyciski = QWidget()
        przyciski.setObjectName("excel_przyciski")
        self._przyciski = UkladPlynny(przyciski, odstep_poziomy=8, odstep_pionowy=4)
        self.zatwierdz = przycisk(NR.EXCEL_ZATWIERDZ_WYBIERZ, "excel_zatwierdz", "glowny", self._zatwierdz)
        self.pomin = przycisk(NR.EXCEL_POMIN, "excel_pomin", None, self._pomin)
        self.odswiez = przycisk(NR.EXCEL_ODSWIEZ, "excel_odswiez", "lacze", lambda: self._polecenie("excel_odswiez"))
        self.pozniej = przycisk(NR.EXCEL_POZNIEJ, "excel_pozniej", "lacze", lambda: self._polecenie("excel_zamknij"))
        for b in (self.zatwierdz, self.pomin, self.odswiez, self.pozniej):
            self._przyciski.addWidget(b)
        u.addWidget(przyciski)

    @property
    def ekran(self):
        return self._ekran()

    def _polecenie(self, nazwa: str, *argumenty):
        ekran = self.ekran
        return ekran._polecenie(nazwa, *argumenty) if ekran is not None else None

    def pokazana(self) -> tuple | None:
        """(sesja_pieca_id, zlecenie_id) pozycji pokazanej w panelu (do testow i kontroli)."""
        return self._klucz

    def wybrana(self) -> bool:
        """Czy pokazana pozycja jest wybrana kliknieciem (przyciski zapisu moga byc aktywne - B1)."""
        return self._wybrana

    def ustaw_tryb(self, r: styl.Rozmiary) -> None:
        self._r = r
        self._u.setContentsMargins(*((8, 4, 8, 4) if r.zwarty else (12, 8, 12, 8)))
        self._u.setSpacing(3 if r.zwarty else 6)
        self.zatwierdz.setMinimumHeight(r.wysokosc_przycisku)
        self.pomin.setMinimumHeight(r.wysokosc_przycisku)
        self._sygnatura = None

    # --- klikniecia -------------------------------------------------------------------------------
    def _klik_pozycji(self, wiersz: int, _kolumna: int) -> None:
        ex = self._stan.excel if self._stan is not None else None
        if ex is None or not 0 <= wiersz < len(ex.pozycje):
            return
        self._klucz, self._wiersz, self._wybrana = klucz_pozycji(ex.pozycje[wiersz]), None, True
        self._sygnatura = None
        self.ustaw(self._stan)

    def _klik_kandydata(self, wiersz: int, _kolumna: int) -> None:
        if self._wybrana and 0 <= wiersz < len(self._kandydaci):
            self._wiersz = self._kandydaci[wiersz].wiersz
            self._sygnatura = None
            self.ustaw(self._stan)

    def _pozycja(self):
        ex = self._stan.excel if self._stan is not None else None
        return next((p for p in ex.pozycje if klucz_pozycji(p) == self._klucz), None) if ex is not None else None

    def _cel(self, p) -> int | None:
        if p is None:
            return None
        if self._wiersz is not None:
            return self._wiersz
        return None if wymaga_wskazania(p) else p.wiersz

    def _rozbroj(self) -> None:
        """Po kliknieciu zapisu przyciski od razu nieaktywne - drugie klikniecie (podwojne) nie trafia w nastepna pozycje (B1)."""
        self._wybrana, self._wiersz = False, None
        self.zatwierdz.setEnabled(False)
        self.pomin.setEnabled(False)

    def _zatwierdz(self) -> None:
        p = self._pozycja()
        cel = self._cel(p)
        if not self._wybrana or p is None or p.zalatwiona or cel is None or p.zlecenie_id is None:
            return
        wiersz = self._wiersz
        self._rozbroj()
        if wiersz is None:
            self._polecenie("excel_zatwierdz", p.sesja_pieca_id, p.zlecenie_id)
        else:
            self._polecenie("excel_zatwierdz", p.sesja_pieca_id, p.zlecenie_id, wiersz)

    def _pomin(self) -> None:
        p = self._pozycja()
        if not self._wybrana or p is None or p.zalatwiona or p.zlecenie_id is None:
            return
        self._rozbroj()
        self._polecenie("excel_pomin", p.sesja_pieca_id, p.zlecenie_id)

    # --- stan -------------------------------------------------------------------------------------
    def ustaw(self, stan) -> None:
        """Panel ze stanu (``stan.excel``); przebudowa tylko po zmianie pozycji, wyboru osoby albo rozmiaru."""
        self._stan = stan
        ex = stan.excel if stan is not None else None
        if ex is None:
            return
        pozycje = ex.pozycje
        teraz = self._pozycja()
        if teraz is None or (teraz.zalatwiona and not self._wybrana):  # pokazana: pierwsza niezalatwiona - bez wyboru (B1)
            nastepna = next((p for p in pozycje if not p.zalatwiona), None) or (pozycje[0] if pozycje else None)
            klucz = klucz_pozycji(nastepna) if nastepna is not None else None
            if klucz != self._klucz:
                self._klucz, self._wiersz, self._wybrana = klucz, None, False
        elif teraz.zalatwiona:
            self._wybrana, self._wiersz = False, None
        sygnatura = (ex, stan.operator, self._klucz, self._wiersz, self._wybrana, self._r.zwarty)
        if sygnatura == self._sygnatura:
            return
        self._sygnatura = sygnatura
        r = self._r
        data = ex.data or ""
        self.tytul.setText(NR.EXCEL_TYTUL.format(nr=ex.nr_w_dniu or "?", doba=dzien(data) if data else "?"))
        teksty = ([NR.EXCEL_W_TOKU.format(n=ex.w_toku)] if ex.w_toku else []) + [NR.EXCEL_TRYB.get(ex.tryb, ""),
                                                                               NR.EXCEL_ZOSTALO.format(n=ex.do_zalatwienia, razem=len(pozycje))]
        for surowe in ex.ostrzezenia:  # E3-P14 (poz. 1): pelny tekst (sekcje ustawien, oznaczenia) do logu, raz
            if surowe not in self._zalogowane:
                self._zalogowane.add(surowe)
                LOG.info("okno Excela: ostrzezenie dla programisty: %s", surowe)
        self.ostrzezenia.setText(" ".join(t for t in teksty + [NR.dla_technika(x) for x in ex.ostrzezenia] if t))
        self.blad.setText(ex.blad or "")
        self.blad.setVisible(bool(ex.blad))
        wyczysc(self._zalegle)
        if ex.zalegle:
            self._zalegle.addWidget(etykieta(NR.EXCEL_ZALEGLE, "slaby"))
            for sid, nr, d, ile in ex.zalegle:
                self._zalegle.addWidget(przycisk(NR.EXCEL_ZALEGLY.format(nr=nr or "?", doba=dzien(d) if d else "?", ile=ile), f"excel_zalegly_{sid}",
                                                 "lacze", lambda sid=sid: self._polecenie("excel_pokaz", sid)))
        self.zalegle.setVisible(bool(ex.zalegle))
        wiersze = []
        for p in pozycje:
            propozycja = NR.EXCEL_PROPOZYCJA.get(p.klasa, p.klasa).format(wiersz=p.wiersz, n=p.kandydatow)
            uwagi = " ".join(x for x in (NR.EXCEL_UWAGA_SPRAWDZ if p.do_sprawdzenia else "", NR.EXCEL_UWAGA_BLAD if p.poprzedni_blad else "") if x)
            wiersze.append([p.kuweta or NR.LISTA_PUSTA, propozycja, uwagi,
                            NR.EXCEL_STANY.get(p.wynik, p.wynik or "") if p.zalatwiona or p.wynik else NR.EXCEL_STANY[None]])
        _wypelnij(self.tabela, wiersze, r)
        indeks = next((i for i, p in enumerate(pozycje) if klucz_pozycji(p) == self._klucz), None)
        if indeks is not None and self._wybrana:
            self.tabela.selectRow(indeks)
        else:
            self.tabela.clearSelection()
        p = self._pozycja()
        szczegoly = (self.ekran.k.excel_szczegoly(p.sesja_pieca_id, p.zlecenie_id)
                     if p is not None and p.zlecenie_id is not None and self.ekran is not None else None)
        self._kandydaci = szczegoly.kandydaci if szczegoly is not None else ()
        if self._wiersz is not None and self._wiersz not in {x.wiersz for x in self._kandydaci}:  # r3 D-N2: lista kandydatow zmieniona
            self._wiersz = None
        self.folder.setText(NR.EXCEL_FOLDER.format(kuweta=p.kuweta or NR.LISTA_PUSTA, folder=szczegoly.folder or NR.LISTA_PUSTA)
                            if p is not None and szczegoly is not None else "")
        self.powod.setText(NR.dla_technika(p.powod) if p is not None else "")  # E3-P14 (poz. 2): bez "regula N:"
        self.sprawdz.setVisible(p is not None and p.do_sprawdzenia and not p.zalatwiona)
        if p is not None and p.poprzedni_blad and not p.zalatwiona:
            w = p.poprzedni_wiersz
            self.poprzedni.setText(NR.EXCEL_POPRZEDNI_BLAD.format(od=w - 1, do=w + 1) if w else NR.EXCEL_POPRZEDNI_BLAD_BEZ_WIERSZA)
            self.poprzedni.setVisible(True)
        else:
            self.poprzedni.setVisible(False)
        kand = []
        for x in self._kandydaci:
            pole = NR.EXCEL_POLE_ZIELONE if x.zielone else (NR.EXCEL_POLE_INNE if x.kolor_b else "")
            kand.append([f"{x.wiersz}{NR.EXCEL_PROPONOWANY if p is not None and x.wiersz == p.wiersz else ''}", dzien(x.data) if x.data else "",
                         x.numer_b, x.kuweta, x.nazwa, pole])
        _wypelnij(self.kandydaci, kand, r)
        wybrany = next((i for i, x in enumerate(self._kandydaci) if x.wiersz == self._wiersz), None)
        if wybrany is not None:
            self.kandydaci.selectRow(wybrany)
        else:
            self.kandydaci.clearSelection()
        osoba = stan.operator is not None
        do_zapisu = osoba and self._wybrana and p is not None and not p.zalatwiona and p.zlecenie_id is not None
        cel = self._cel(p)
        self.wybierz.setText(NR.EXCEL_WSKAZ_WIERSZ if self._wybrana and p is not None and cel is None else NR.EXCEL_WYBIERZ)
        self.wybierz.setVisible(not self._wybrana or (p is not None and cel is None and not p.zalatwiona))
        self.zatwierdz.setText(NR.EXCEL_ZATWIERDZ.format(wiersz=cel) if cel is not None else NR.EXCEL_ZATWIERDZ_WYBIERZ)
        self.zatwierdz.setEnabled(do_zapisu and cel is not None)
        self.pomin.setEnabled(do_zapisu)
        self.odswiez.setEnabled(osoba)
        self.bez_osoby.setVisible(not osoba)
