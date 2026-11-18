"""okno_excela - okno "Excel: wskaz wiersz" ekranu porannego (paczka E3-A12): zlecenia kompletne zamknietego pieca i wiersze
arkusza zlecen proponowane przez ``excel`` (A9) do odhaczenia (kolor pola B).

Zasady (kontrakt ``kontroler_api`` w wersji 4):
* okno to PANEL w lewej kolumnie ekranu porannego (zamiast plytek pieca) - nie osobne okno modalne; pokazane, gdy
  ``stan.excel.widoczne`` (po "Zamknij piec" w trybie "pytaj", przycisk "Excel: wskaz wiersz");
* niczego nie liczy i nie zapisuje samo: lista pozycji ze ``stan.excel.pozycje``, kandydaci (kolumna H - DANE OSOBOWE, tylko
  na ekran laptopa) z zapytania ``kontroler.excel_szczegoly(nr)``; zapis koloru WYLACZNIE po kliknieciu "Zatwierdz"
  (``excel_zatwierdz``), "Pomin" = ``excel_pomin``, "Pozniej" = ``excel_zamknij``, "Odswiez z Excela" = ``excel_odswiez``;
* wybor bez zgodnej nazwy (``do_sprawdzenia``) oznaczony wyraznie (kolumna "Uwagi" i napis nad kandydatami); bez osoby
  przyciski zapisu nieaktywne z wyjasnieniem.
Wlasny stan panelu to wybor osoby: pokazana pozycja i wskazany wiersz kandydata.
"""
from __future__ import annotations

import weakref

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractItemView, QFrame, QHeaderView, QSizePolicy, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from . import napisy_rano as NR
from . import styl
from .czesci import UkladPlynny, dzien, etykieta, przycisk

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


class PanelExcela(QFrame):
    """Panel "Excel: wskaz wiersz". ``ekran`` - ``EkranRano`` (polecenia przez okno, kontroler do zapytania o kandydatow)."""

    def __init__(self, ekran):
        super().__init__()
        self._ekran = weakref.ref(ekran)
        self.setObjectName("excel_panel")
        self.setProperty("rola", "panel")
        self._r = styl.ZWYKLE
        self._nr: int | None = None  # pokazana pozycja (``PozycjaExcel.nr``)
        self._wiersz: int | None = None  # wiersz kandydata wskazany przez osobe
        self._reczny = False  # pozycja wybrana kliknieciem (zostaje pokazana, takze zalatwiona)
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
        self.tabela = _tabela("excel_tabela", NR.EXCEL_KOLUMNY)
        self.tabela.cellClicked.connect(self._klik_pozycji)
        u.addWidget(self.tabela, 2)
        self.folder = etykieta("", "duzy", "excel_folder", zawijaj=True)
        u.addWidget(self.folder)
        self.powod = etykieta("", "slaby", "excel_powod", zawijaj=True)
        u.addWidget(self.powod)
        self.sprawdz = etykieta(NR.EXCEL_SPRAWDZ, "uwaga", "excel_sprawdz", zawijaj=True)
        self.sprawdz.setVisible(False)
        u.addWidget(self.sprawdz)
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

    def pokazana(self) -> int | None:
        """``nr`` pozycji pokazanej w panelu (do testow i kontroli)."""
        return self._nr

    def ustaw_tryb(self, r: styl.Rozmiary) -> None:
        self._r = r
        self._u.setContentsMargins(*((8, 4, 8, 4) if r.zwarty else (12, 8, 12, 8)))
        self._u.setSpacing(3 if r.zwarty else 6)
        self.zatwierdz.setMinimumHeight(r.wysokosc_przycisku)
        self.pomin.setMinimumHeight(r.wysokosc_przycisku)
        self._sygnatura = None

    # --- klikniecia -------------------------------------------------------------------------------
    def _klik_pozycji(self, wiersz: int, _kolumna: int) -> None:
        if self._stan is None or self._stan.excel is None or not 0 <= wiersz < len(self._stan.excel.pozycje):
            return
        self._nr, self._wiersz, self._reczny = self._stan.excel.pozycje[wiersz].nr, None, True
        self._sygnatura = None
        self.ustaw(self._stan)

    def _klik_kandydata(self, wiersz: int, _kolumna: int) -> None:
        if 0 <= wiersz < len(self._kandydaci):
            self._wiersz = self._kandydaci[wiersz].wiersz
            self._sygnatura = None
            self.ustaw(self._stan)

    def _pozycja(self):
        ex = self._stan.excel if self._stan is not None else None
        return next((p for p in ex.pozycje if p.nr == self._nr), None) if ex is not None else None

    def _zatwierdz(self) -> None:
        p = self._pozycja()
        if p is None or p.zalatwiona:
            return
        wiersz = self._wiersz
        if wiersz is None and p.klasa == KLASA_WSKAZ:
            return
        self._reczny = False  # po zapisie panel przechodzi do nastepnej pozycji
        odp = self._polecenie("excel_zatwierdz", p.nr) if wiersz is None else self._polecenie("excel_zatwierdz", p.nr, wiersz)
        if odp is not None and odp.ok:
            self._wiersz = None

    def _pomin(self) -> None:
        p = self._pozycja()
        if p is not None and not p.zalatwiona:
            self._reczny = False
            if self._polecenie("excel_pomin", p.nr) is not None:
                self._wiersz = None

    # --- stan -------------------------------------------------------------------------------------
    def ustaw(self, stan) -> None:
        """Panel ze stanu (``stan.excel``); przebudowa tylko po zmianie pozycji, wyboru osoby albo rozmiaru."""
        self._stan = stan
        ex = stan.excel if stan is not None else None
        if ex is None:
            return
        pozycje = ex.pozycje
        teraz = self._pozycja()
        if teraz is None or (teraz.zalatwiona and not self._reczny):  # pierwsza (nastepna) niezalatwiona
            nastepna = next((p for p in pozycje if not p.zalatwiona), None) or (pozycje[0] if pozycje else None)
            if nastepna is None or nastepna.nr != self._nr:
                self._nr, self._wiersz = (nastepna.nr if nastepna is not None else None), None
        sygnatura = (ex, stan.operator, self._nr, self._wiersz, self._r.zwarty)
        if sygnatura == self._sygnatura:
            return
        self._sygnatura = sygnatura
        r = self._r
        data = ex.data or ""
        self.tytul.setText(NR.EXCEL_TYTUL.format(nr=ex.nr_w_dniu or "?", doba=dzien(data) if data else "?"))
        teksty = [NR.EXCEL_TRYB.get(ex.tryb, ""), NR.EXCEL_ZOSTALO.format(n=ex.do_zalatwienia, razem=len(pozycje))] + list(ex.ostrzezenia)
        self.ostrzezenia.setText(" ".join(t for t in teksty if t))
        self.blad.setText(ex.blad or "")
        self.blad.setVisible(bool(ex.blad))
        wiersze = []
        for p in pozycje:
            propozycja = NR.EXCEL_PROPOZYCJA.get(p.klasa, p.klasa).format(wiersz=p.wiersz, n=p.kandydatow)
            wiersze.append([p.kuweta or NR.LISTA_PUSTA, propozycja, NR.EXCEL_UWAGA_SPRAWDZ if p.do_sprawdzenia else "",
                            NR.EXCEL_STANY.get(p.wynik, p.wynik or "") if p.zalatwiona or p.wynik else NR.EXCEL_STANY[None]])
        _wypelnij(self.tabela, wiersze, r)
        indeks = next((i for i, p in enumerate(pozycje) if p.nr == self._nr), None)
        if indeks is not None:
            self.tabela.selectRow(indeks)
        p = self._pozycja()
        szczegoly = self.ekran.k.excel_szczegoly(p.nr) if p is not None and self.ekran is not None else None
        self._kandydaci = szczegoly.kandydaci if szczegoly is not None else ()
        self.folder.setText(NR.EXCEL_FOLDER.format(kuweta=p.kuweta or NR.LISTA_PUSTA, folder=szczegoly.folder or NR.LISTA_PUSTA)
                            if p is not None and szczegoly is not None else "")
        self.powod.setText(p.powod if p is not None else "")
        self.sprawdz.setVisible(p is not None and p.do_sprawdzenia and not p.zalatwiona)
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
        cel = self._wiersz if self._wiersz is not None else (p.wiersz if p is not None and p.klasa != KLASA_WSKAZ else None)
        self.zatwierdz.setText(NR.EXCEL_ZATWIERDZ.format(wiersz=cel) if cel is not None else NR.EXCEL_ZATWIERDZ_WYBIERZ)
        self.zatwierdz.setEnabled(osoba and p is not None and not p.zalatwiona and cel is not None)
        self.pomin.setEnabled(osoba and p is not None and not p.zalatwiona)
        self.odswiez.setEnabled(osoba)
        self.bez_osoby.setVisible(not osoba)
