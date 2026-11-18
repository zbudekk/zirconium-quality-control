"""dzien_skanera - okno "Dzien skanera - krok po kroku" (PySide6): zbieranie pierwszych skanow i danych z programu skanera.

Uruchomienie: ``uruchom_dzien_skanera.bat`` (z katalogu stanowisko/) albo ``py -3.12 -m stanowisko.dzien_skanera``.
Sprawdzenie paczki bez okna (dla koordynatora): ``py -3.12 -m stanowisko.dzien_skanera --sprawdz <folder sesji albo zip>``.

Okno prowadzi czlowieka przez kroki z ``dzien_skanera_kroki.toml`` i samo kopiuje kazdy nowy albo zmieniony plik
z folderu eksportu skanera do folderu biezacego kroku sesji (``dane/dzien_skanera/<data_godzina>/``). Cala logika jest
w ``dzien_skanera_rdzen`` (bez Qt): sesja z manifestem zapisywanym po kazdej akcji, zbieracz w zwyklym watku Pythona,
szybka kontrola skanu w osobnym procesie (Open3D w watku pod Qt zawisa - raporty/P3a_postep.md), zrzuty ekranu,
raport, sumy i ZIP. Okno tylko pokazuje stan i przyjmuje polecenia; zdarzenia zbieracza odbiera zegarem (QTimer).

Odpornosc: zaden wyjatek nie zamyka okna (trafia do ``log.txt`` sesji i na liste komunikatow), okno nie uzywa sieci
i nie pisze poza folderem sesji, a po zamknieciu albo awarii wznawia ostatnia niedokonczona sesje.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import subprocess
import sys
import threading
import time
from pathlib import Path

from PySide6.QtCore import QLibraryInfo, Qt, QTimer, QTranslator
from PySide6.QtGui import QBrush, QColor, QFont
from PySide6.QtWidgets import (QApplication, QCheckBox, QFileDialog, QFormLayout, QHBoxLayout, QInputDialog, QLabel, QLineEdit, QListWidget,
                               QListWidgetItem, QMainWindow, QMessageBox, QPlainTextEdit, QProgressBar, QPushButton, QScrollArea, QSplitter,
                               QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

from . import dzien_skanera_rdzen as R
from . import ustawienia as UST

KOLORY_OCENY = {"zielony": "#c9efc9", "zolty": "#fff0a8", "czerwony": "#f8c4c4", "szary": "#e9e9e9"}
KOLORY_STANU = {"zrobiony": "#1c7a1c", "niepelny": "#b36b00", "pominiety": "#777777", "w_toku": "#0b4fb3", "czeka": "#000000"}
ZNAKI_STANU = {"zrobiony": "✔", "niepelny": "◐", "pominiety": "✖", "w_toku": "●", "czeka": "○"}
OPISY_STANU = {"zrobiony": "zrobiony", "niepelny": "niepełny", "pominiety": "pominięty", "w_toku": "w toku", "czeka": "czeka"}
OPISY_RODZAJU = {"obserwacja": "z folderu skanera", "reczny": "dodany ręcznie", "zrzut": "zrzut ekranu", "kopia_folderu": "kopia folderu"}
NARZEDZIE_POMIARU = UST.KORZEN / "narzedzia" / "pomiar_skanu" / "pomiar_skanu.py"
OPOZNIENIE_ZRZUTU_S = 3


def tekst_czasu(sekundy: float) -> str:
    s = int(round(sekundy))
    return f"{s} s" if s < 60 else f"{s} s ({s // 60} min {s % 60} s)"


class Okno(QMainWindow):
    def __init__(self, sesja: R.Sesja, ust: dict | None = None, plik_ustawien: Path | None = None, tryb_kontroli: str = "proces",
                 autostart: bool = True, grab=None, uwaga_startowa: str = ""):
        super().__init__()
        self.sesja, self.ust = sesja, ust
        self.zbieracz = R.Zbieracz(sesja, ust, plik_ustawien, tryb_kontroli, grab=grab)
        self.opoznienie_zrzutu_s = OPOZNIENIE_ZRZUTU_S
        self.otwieraj_foldery = True  # po spakowaniu otworz folder paczki w Eksploratorze (testy: False)
        self.pola: dict[str, QLineEdit] = {}
        self._pokazany: str | None = None
        self._odliczanie = 0
        self._pakowanie = False
        self._szukanie: threading.Thread | None = None
        self._przerwij_szukanie = threading.Event()
        self.wynik_paczki: dict | None = None
        self.braki_wymaganych: list[str] = []
        self.setWindowTitle(f"Dzień skanera — krok po kroku (sesja {sesja.m['nazwa']})")
        self.setAcceptDrops(True)
        self.zegar = QTimer(self)  # odbior zdarzen zbieracza
        self.zegar.setInterval(200)
        self.zegar.timeout.connect(lambda: self._bezpiecznie(self._takt))
        self.zegar_tekstow = QTimer(self)  # zapis notatki i pol chwile po ostatnim klawiszu
        self.zegar_tekstow.setSingleShot(True)
        self.zegar_tekstow.setInterval(700)
        self.zegar_tekstow.timeout.connect(lambda: self._bezpiecznie(self._zapisz_teksty))
        self.zegar_zrzutu = QTimer(self)  # odliczanie przed zrzutem ekranu
        self.zegar_zrzutu.setInterval(1000)
        self.zegar_zrzutu.timeout.connect(lambda: self._bezpiecznie(self._takt_zrzutu))
        self._zbuduj()
        self._pokaz_krok(sesja.biezacy)
        self._odswiez_wszystko()
        if uwaga_startowa:
            self._dziennik(uwaga_startowa, blad=True)
        self.zegar.start()
        if autostart:
            self.zbieracz.start()

    # ------------------------------------------------------------------ odpornosc
    def _bezpiecznie(self, f, *a):
        """Zaden wyjatek z obslugi okna nie zamyka programu: log sesji + wiersz na liscie komunikatow."""
        try:
            return f(*a)
        except Exception as e:  # noqa: BLE001
            self._wyjatek(getattr(f, "__name__", "okno"), e)
            return None

    def _wyjatek(self, gdzie: str, e: BaseException) -> None:
        try:
            self.sesja.log_wyjatku(f"okno.{gdzie}", e)
            self._dziennik(f"Błąd programu ({type(e).__name__}: {e}) — zapisany w log.txt. Zbieranie plików trwa dalej.", blad=True)
        except Exception:  # noqa: BLE001 - obsluga bledu nie moze sama zamknac okna
            pass

    def _polacz(self, sygnal, metoda) -> None:
        sygnal.connect(lambda *_: self._bezpiecznie(metoda))

    # okna dialogowe w osobnych metodach (testy je podmieniaja)
    def _pytaj_tak_nie(self, tytul: str, tekst: str, domyslnie_tak: bool = True) -> bool:
        odp = QMessageBox.question(self, tytul, tekst, QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes if domyslnie_tak else QMessageBox.No)
        return odp == QMessageBox.Yes

    def _pytaj_tekst(self, tytul: str, tekst: str, domyslny: str = "") -> str | None:
        wynik, ok = QInputDialog.getText(self, tytul, tekst, QLineEdit.Normal, domyslny)
        return wynik if ok else None

    def _pytaj_wybor(self, tytul: str, tekst: str, pozycje: list[str]) -> str | None:
        wynik, ok = QInputDialog.getItem(self, tytul, tekst, pozycje, 0, False)
        return wynik if ok else None

    def _pytaj_pliki(self) -> list[str]:
        return QFileDialog.getOpenFileNames(self, "Dodaj pliki do bieżącego kroku", "", "Wszystkie pliki (*)")[0]

    def _pytaj_folder(self, tytul: str, start: str = "") -> str:
        return QFileDialog.getExistingDirectory(self, tytul, start)

    def _komunikat(self, tytul: str, tekst: str) -> None:
        QMessageBox.information(self, tytul, tekst)

    # ------------------------------------------------------------------ uklad okna
    def _zbuduj(self) -> None:
        srodek = QWidget()
        self.setCentralWidget(srodek)
        calosc = QVBoxLayout(srodek)

        # gora: foldery obserwowane, stan, alarm
        gora = QHBoxLayout()
        self.etykieta_folderow = QLabel()
        self.etykieta_folderow.setWordWrap(True)
        self.etykieta_folderow.setTextFormat(Qt.RichText)
        gora.addWidget(self.etykieta_folderow, 1)
        self.przycisk_folder = QPushButton("Dodaj folder…")
        self.przycisk_folder.setToolTip("Folder, do którego program skanera zapisuje pliki — okno będzie kopiować z niego każdy nowy plik")
        self.przycisk_szukaj = QPushButton("Nie wiem, gdzie skaner zapisuje — szukaj")
        self.pole_auto_zrzut = QCheckBox("Zrzut ekranu przy każdym nowym pliku")
        self.pole_auto_zrzut.setChecked(bool(self.sesja.m.get("auto_zrzut")))
        for w in (self.przycisk_folder, self.przycisk_szukaj, self.pole_auto_zrzut):
            gora.addWidget(w)
        calosc.addLayout(gora)
        stan = QHBoxLayout()
        self.etykieta_stanu = QLabel("uruchamiam…")
        self.pasek = QProgressBar()
        self.pasek.setRange(0, 1000)
        self.pasek.setFixedWidth(260)
        self.pasek.setTextVisible(True)
        self.pasek.setFormat("")
        stan.addWidget(self.etykieta_stanu, 1)
        stan.addWidget(self.pasek)
        calosc.addLayout(stan)
        self.etykieta_alarmu = QLabel()
        self.etykieta_alarmu.setWordWrap(True)
        self.etykieta_alarmu.setStyleSheet("background:#d32f2f; color:white; font-weight:bold; padding:6px;")
        self.etykieta_alarmu.hide()
        calosc.addWidget(self.etykieta_alarmu)

        dzielnik = QSplitter(Qt.Horizontal)
        calosc.addWidget(dzielnik, 1)

        # lewa strona: kroki i kompletnosc (widoczne caly czas)
        lewa = QWidget()
        lu = QVBoxLayout(lewa)
        lu.setContentsMargins(0, 0, 0, 0)
        lu.addWidget(QLabel("<b>Kroki dnia</b> (klik = nowe pliki trafiają do tego kroku)"))
        self.lista_krokow = QListWidget()
        self.lista_krokow.setWordWrap(True)
        lu.addWidget(self.lista_krokow, 3)
        self.etykieta_kompletnosci = QLabel()
        self.etykieta_kompletnosci.setWordWrap(True)
        self.etykieta_kompletnosci.setTextFormat(Qt.RichText)
        self.etykieta_kompletnosci.setAlignment(Qt.AlignTop)
        przewijanie = QScrollArea()
        przewijanie.setWidgetResizable(True)
        przewijanie.setWidget(self.etykieta_kompletnosci)
        lu.addWidget(przewijanie, 2)
        self.przycisk_spakuj = QPushButton("Zakończ i spakuj")
        self.przycisk_spakuj.setStyleSheet("font-weight:bold; padding:8px;")
        self.przycisk_folder_sesji = QPushButton("Otwórz folder sesji")
        lu.addWidget(self.przycisk_spakuj)
        lu.addWidget(self.przycisk_folder_sesji)
        dzielnik.addWidget(lewa)

        # prawa strona: biezacy krok
        prawa = QWidget()
        pu = QVBoxLayout(prawa)
        pu.setContentsMargins(0, 0, 0, 0)
        self.etykieta_tytulu = QLabel()
        czcionka = QFont()
        czcionka.setPointSize(13)
        czcionka.setBold(True)
        self.etykieta_tytulu.setFont(czcionka)
        self.etykieta_tytulu.setWordWrap(True)
        pu.addWidget(self.etykieta_tytulu)
        self.pole_instrukcji = QPlainTextEdit()
        self.pole_instrukcji.setReadOnly(True)
        self.pole_instrukcji.setStyleSheet("background:#fbfbf3; font-size:11pt;")
        pu.addWidget(self.pole_instrukcji, 4)
        self.ramka_pol = QWidget()
        self.uklad_pol = QFormLayout(self.ramka_pol)
        self.uklad_pol.setContentsMargins(0, 0, 0, 0)
        pu.addWidget(self.ramka_pol)
        stoper = QHBoxLayout()
        self.przycisk_stoper_start = QPushButton("Stoper: start")
        self.przycisk_stoper_stop = QPushButton("Stoper: stop")
        self.etykieta_stopera = QLabel("")
        for w in (self.przycisk_stoper_start, self.przycisk_stoper_stop):
            stoper.addWidget(w)
        stoper.addWidget(self.etykieta_stopera, 1)
        self.ramka_stopera = QWidget()
        self.ramka_stopera.setLayout(stoper)
        stoper.setContentsMargins(0, 0, 0, 0)
        pu.addWidget(self.ramka_stopera)
        self.pole_notatki = QPlainTextEdit()
        self.pole_notatki.setPlaceholderText("Notatka do tego kroku: co było na płytce, co się nie udało, co wyglądało inaczej…")
        self.pole_notatki.setFixedHeight(64)
        pu.addWidget(self.pole_notatki)

        rzad1 = QHBoxLayout()
        self.przycisk_zrzut = QPushButton("Zrzut ekranu (za 3 s)")
        self.pole_chowaj = QCheckBox("chowaj to okno na czas zrzutu")
        self.pole_chowaj.setChecked(True)
        self.przycisk_dodaj_plik = QPushButton("Dodaj plik…")
        self.przycisk_dodaj_folder = QPushButton("Dodaj folder ręcznie…")
        self.przycisk_kopia = QPushButton("Skopiuj cały folder zleceń skanera")
        self.przycisk_kopia.setStyleSheet("font-weight:bold;")
        for w in (self.przycisk_zrzut, self.pole_chowaj, self.przycisk_dodaj_plik, self.przycisk_dodaj_folder, self.przycisk_kopia):
            rzad1.addWidget(w)
        rzad1.addStretch(1)
        pu.addLayout(rzad1)
        rzad2 = QHBoxLayout()
        self.przycisk_dalej = QPushButton("Krok zrobiony — dalej")
        self.przycisk_dalej.setStyleSheet("font-weight:bold; padding:6px 14px;")
        self.przycisk_pomin = QPushButton("Nie udało się / pomijam, bo…")
        self.przycisk_przywroc = QPushButton("Cofnij: krok jeszcze do zrobienia")
        for w in (self.przycisk_dalej, self.przycisk_pomin, self.przycisk_przywroc):
            rzad2.addWidget(w)
        rzad2.addStretch(1)
        pu.addLayout(rzad2)

        self.etykieta_oceny = QLabel("Czekam na pierwszy plik…")
        self.etykieta_oceny.setWordWrap(True)
        self.etykieta_oceny.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.etykieta_oceny.setMinimumHeight(54)
        self._kolor_oceny("szary")
        pu.addWidget(self.etykieta_oceny)

        self.tabela = QTableWidget(0, 5)
        self.tabela.setHorizontalHeaderLabels(["godzina", "plik", "rozmiar", "skąd", "ocena"])
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.horizontalHeader().setStretchLastSection(True)
        pu.addWidget(self.tabela, 3)
        rzad3 = QHBoxLayout()
        self.przycisk_przenies = QPushButton("Przenieś zaznaczony plik do innego kroku…")
        self.przycisk_pomiar = QPushButton("Pomiar szczegółowy zaznaczonego skanu (osobne okno)…")
        self.przycisk_pomiar.setEnabled(NARZEDZIE_POMIARU.exists())
        if not NARZEDZIE_POMIARU.exists():
            self.przycisk_pomiar.setToolTip("Brak narzędzia narzedzia/pomiar_skanu — zbieranie plików działa bez niego")
        rzad3.addWidget(self.przycisk_przenies)
        rzad3.addWidget(self.przycisk_pomiar)
        rzad3.addStretch(1)
        pu.addLayout(rzad3)
        self.lista_komunikatow = QListWidget()
        self.lista_komunikatow.setFixedHeight(86)
        self.lista_komunikatow.setWordWrap(True)
        pu.addWidget(self.lista_komunikatow)
        dzielnik.addWidget(prawa)
        dzielnik.setSizes([330, 820])
        ekran = QApplication.primaryScreen()
        dostepne = ekran.availableGeometry() if ekran is not None else None  # maly ekran laptopa: okno nie moze wystawac poza ekran
        self.resize(min(1180, dostepne.width() - 20) if dostepne else 1180, min(860, dostepne.height() - 40) if dostepne else 860)

        for d in self.sesja.m["definicje_krokow"]:
            el = QListWidgetItem()
            el.setData(Qt.UserRole, d["id"])
            self.lista_krokow.addItem(el)

        self.lista_krokow.currentRowChanged.connect(lambda w: self._bezpiecznie(self._wybrano_krok, w))
        self.tabela.itemSelectionChanged.connect(lambda: self._bezpiecznie(self._wybrano_plik))
        self.pole_auto_zrzut.toggled.connect(lambda wl: self._bezpiecznie(self.sesja.ustaw_auto_zrzut, wl))
        self.pole_notatki.textChanged.connect(lambda: self.zegar_tekstow.start())
        self._polacz(self.przycisk_folder.clicked, self.dodaj_folder_obserwowany)
        self._polacz(self.przycisk_szukaj.clicked, self.szukaj_skanow)
        self._polacz(self.przycisk_spakuj.clicked, self.zakoncz_i_spakuj)
        self._polacz(self.przycisk_folder_sesji.clicked, lambda: self._otworz_folder(self.sesja.folder))
        self._polacz(self.przycisk_stoper_start.clicked, self.stoper_start)
        self._polacz(self.przycisk_stoper_stop.clicked, self.stoper_stop)
        self._polacz(self.przycisk_zrzut.clicked, self.zrzut_ekranu)
        self._polacz(self.przycisk_dodaj_plik.clicked, self.dodaj_pliki)
        self._polacz(self.przycisk_dodaj_folder.clicked, self.dodaj_folder_reczny)
        self._polacz(self.przycisk_kopia.clicked, self.kopia_calego_folderu)
        self._polacz(self.przycisk_dalej.clicked, self.krok_zrobiony)
        self._polacz(self.przycisk_pomin.clicked, self.pomin_krok)
        self._polacz(self.przycisk_przywroc.clicked, self.przywroc_krok)
        self._polacz(self.przycisk_przenies.clicked, self.przenies_plik)
        self._polacz(self.przycisk_pomiar.clicked, self.pomiar_szczegolowy)

    def _kolor_oceny(self, kolor: str) -> None:
        self.etykieta_oceny.setStyleSheet(f"background:{KOLORY_OCENY[kolor]}; padding:8px; font-size:11pt; border:1px solid #999;")
        self.kolor_oceny = kolor

    def _ocena(self, kolor: str, tekst: str) -> None:
        self._kolor_oceny(kolor)
        self.etykieta_oceny.setText(tekst)

    def _dziennik(self, tekst: str, blad: bool = False) -> None:
        el = QListWidgetItem(f"{dt.datetime.now().strftime('%H:%M:%S')}  {tekst}")
        if blad:
            el.setForeground(QBrush(QColor("#b00020")))
        self.lista_komunikatow.addItem(el)
        while self.lista_komunikatow.count() > 300:
            self.lista_komunikatow.takeItem(0)
        self.lista_komunikatow.scrollToBottom()

    # ------------------------------------------------------------------ odswiezanie
    def _odswiez_wszystko(self) -> None:
        self._odswiez_kroki()
        self._odswiez_pliki()
        self._odswiez_foldery()
        self._odswiez_stan()

    def _odswiez_kroki(self) -> None:
        oceny = self.sesja.kompletnosc()
        self.lista_krokow.blockSignals(True)
        for i, o in enumerate(oceny):
            el = self.lista_krokow.item(i)
            pliki = f" [{o['plikow']}/{o['oczekiwane']}]" if o["oczekiwane"] else (f" [{o['wszystkich_plikow']}]" if o["wszystkich_plikow"] else "")
            el.setText(f"{ZNAKI_STANU[o['stan']]} {i + 1}. {o['tytul']}{'' if o['wymagany'] else ' (opcjonalny)'}{pliki}")
            el.setForeground(QBrush(QColor(KOLORY_STANU[o["stan"]])))
            czcionka = el.font()
            czcionka.setBold(o["id"] == self.sesja.biezacy)
            el.setFont(czcionka)
            el.setToolTip(OPISY_STANU[o["stan"]] + (": " + "; ".join(o["braki"]) if o["braki"] else "") + (f" — {o['powod']}" if o["stan"] == "pominiety" else ""))
            if o["id"] == self.sesja.biezacy:
                self.lista_krokow.setCurrentRow(i)
        self.lista_krokow.blockSignals(False)
        zrobione = sum(1 for o in oceny if o["stan"] == "zrobiony")
        pominiete = sum(1 for o in oceny if o["stan"] == "pominiety")
        braki, pom = self.sesja.braki()
        html = f"<b>Kompletność:</b> zrobione {zrobione} z {len(oceny)}" + (f", pominięte {pominiete}" if pominiete else "")
        if braki:
            html += "<br><span style='color:#b00020'><b>Brakuje (kroki wymagane):</b><br>" + "<br>".join("• " + b for b in braki) + "</span>"
        else:
            html += "<br><span style='color:#1c7a1c'><b>Wszystkie wymagane kroki są zrobione albo świadomie pominięte.</b></span>"
        if pom:
            html += "<br><span style='color:#777'>" + "<br>".join("• " + p for p in pom) + "</span>"
        if self.sesja.m.get("spakowano"):
            html += ("<br><b>Sesja zmieniona po spakowaniu — spakuj ponownie.</b>" if self.sesja.m.get("zmieniono_po_spakowaniu")
                     else f"<br>Spakowano: {self.sesja.m['spakowano'][-1]}")
        self.etykieta_kompletnosci.setText(html)
        self.braki_wymaganych = braki

    def _odswiez_foldery(self) -> None:
        czesci = []
        for _, sciezka in self.sesja.foldery():
            jest = sciezka.is_dir()
            czesci.append(f"<span style='color:{'#1c7a1c' if jest else '#b00020'}'>{'✔' if jest else '✖'} {sciezka}{'' if jest else ' — folder nie istnieje'}</span>")
        if not czesci:
            czesci = ["<span style='color:#b00020'><b>Żaden folder nie jest obserwowany</b> — kliknij „Dodaj folder…” i wskaż folder, do którego zapisuje program skanera</span>"]
        self.etykieta_folderow.setText("<b>Obserwuję:</b> " + " &nbsp;|&nbsp; ".join(czesci))

    def _odswiez_stan(self) -> None:
        pliki = self.sesja.m["pliki"]
        try:
            wolne = R.tekst_rozmiaru(R.wolne_miejsce(self.sesja.folder))
        except OSError:
            wolne = "?"
        czeka = self.zbieracz.do_skopiowania()
        dzialanie = "pakuję…" if self._pakowanie else ("sprawdzam skan…" if self.zbieracz.kontrola_w_toku() else "czuwam")
        self.etykieta_stanu.setText(f"Stan: {dzialanie} · w sesji {len(pliki)} plików ({R.tekst_rozmiaru(sum(w['rozmiar'] for w in pliki))})"
                                    + (f" · czekają na skopiowanie: {czeka}" if czeka else "") + f" · wolne na dysku: {wolne}"
                                    + (f" · ostatni plik: {pliki[-1]['skopiowano'][11:]}" if pliki else ""))

    def _pokaz_krok(self, id_: str) -> None:
        """Wypelnia prawa strone danymi kroku (tylko przy zmianie kroku - nie nadpisuje tego, co czlowiek wlasnie pisze)."""
        self._pokazany = None  # wstrzymanie zapisu tekstow w trakcie przebudowy
        krok = self.sesja.krok(id_)
        s = self.sesja.m["kroki"][id_]
        nr = self.sesja.numer_kroku(id_)
        self.etykieta_tytulu.setText(f"Krok {nr} z {len(self.sesja.kroki)}: {krok.tytul}" + ("" if krok.wymagany else "  (opcjonalny)"))
        self.pole_instrukcji.setPlainText(krok.instrukcja)
        while self.uklad_pol.rowCount():
            self.uklad_pol.removeRow(0)
        self.pola = {}
        definicje = self.sesja.m.get("definicje_pol", {})
        for p in krok.pola:
            pole = QLineEdit(str(s["pola"].get(p, "")))
            pole.setPlaceholderText(definicje.get(p, {}).get("podpowiedz", ""))
            pole.textEdited.connect(lambda *_: self.zegar_tekstow.start())
            self.uklad_pol.addRow(definicje.get(p, {}).get("etykieta", p) + (" *" if p in krok.wymagane_pola else "") + ":", pole)
            self.pola[p] = pole
        self.ramka_stopera.setVisible("czas_skanu" in krok.pola)
        self.pole_notatki.blockSignals(True)
        self.pole_notatki.setPlainText(s.get("notatka", ""))
        self.pole_notatki.blockSignals(False)
        self.przycisk_kopia.setVisible(krok.kontrola == "kopia_folderu")
        self.przycisk_przywroc.setVisible(s["stan"] != "czeka")
        self._pokazany = id_
        self._odswiez_pliki()

    def _odswiez_pliki(self) -> None:
        if self._pokazany is None:
            return
        pliki = self.sesja.pliki_kroku(self._pokazany)
        zaznaczony = self._id_zaznaczonego()
        self.tabela.blockSignals(True)
        self.tabela.setRowCount(len(pliki))
        for i, w in enumerate(pliki):
            k = w.get("kontrola")
            siatka = Path(w["cel"]).suffix.lower() in R.ROZSZERZENIA_SIATEK
            ocena = (k["tytul"] + (": " + "; ".join(k["uwagi"]) if k["uwagi"] else "")) if k else ("sprawdzam…" if siatka and self.zbieracz.tryb_kontroli != "brak" else "skopiowany")
            wart = [w["skopiowano"][11:], Path(w["cel"]).name, R.tekst_rozmiaru(w["rozmiar"]), OPISY_RODZAJU.get(w["rodzaj"], w["rodzaj"]), ocena]
            for j, v in enumerate(wart):
                el = QTableWidgetItem(v)
                el.setData(Qt.UserRole, w["id"])
                if k:
                    el.setBackground(QBrush(QColor(KOLORY_OCENY[k["werdykt"]])))
                el.setToolTip(w["cel"])
                self.tabela.setItem(i, j, el)
            if w["id"] == zaznaczony:
                self.tabela.selectRow(i)
        self.tabela.blockSignals(False)
        self.tabela.resizeColumnsToContents()
        self.przycisk_przywroc.setVisible(self.sesja.m["kroki"][self._pokazany]["stan"] != "czeka")

    def _id_zaznaczonego(self) -> int | None:
        w = self.tabela.currentRow()
        el = self.tabela.item(w, 0) if w >= 0 else None
        return el.data(Qt.UserRole) if el is not None else None

    # ------------------------------------------------------------------ zegar: zdarzenia zbieracza
    def _takt(self) -> None:
        zmiana = False
        for _ in range(200):
            try:
                z = self.zbieracz.zdarzenia.get_nowait()
            except Exception:  # noqa: BLE001 - pusta kolejka
                break
            zmiana = True
            self._bezpiecznie(self._zdarzenie, z)
        if zmiana:
            self._odswiez_stan()
        s = self.sesja.m["kroki"].get(self._pokazany or "", {})
        if s.get("stoper_start"):
            uplynelo = (dt.datetime.now() - dt.datetime.fromisoformat(s["stoper_start"])).total_seconds()
            self.etykieta_stopera.setText(f"stoper chodzi: {int(uplynelo) // 60}:{int(uplynelo) % 60:02d}")

    def _zdarzenie(self, z: dict) -> None:
        typ = z["typ"]
        if typ == "postep":
            razem = max(1, z["razem"])
            self.pasek.setValue(int(1000 * z["zrobione"] / razem))
            self.pasek.setFormat(f"{z['plik'][:28]}  {R.tekst_rozmiaru(z['zrobione'])} / {R.tekst_rozmiaru(razem)}")
            if z["zrobione"] >= razem:
                self.pasek.setFormat("")
                self.pasek.setValue(0)
            return
        if typ == "nowy_plik":
            w = z["wpis"]
            nazwa = Path(w["cel"]).name
            self.etykieta_alarmu.hide()
            self._dziennik(f"Skopiowano: {nazwa} ({R.tekst_rozmiaru(w['rozmiar'])}) → krok {self.sesja.numer_kroku(w['krok'])}")
            if z.get("zrzut"):
                self._ocena("zielony", f"Zrzut ekranu zapisany: {nazwa}")
                if self.pole_chowaj.isChecked() and self.isMinimized():
                    self.showNormal()
            elif Path(w["cel"]).suffix.lower() in R.ROZSZERZENIA_SIATEK and self.zbieracz.tryb_kontroli != "brak":
                self._ocena("szary", f"Plik {nazwa} skopiowany ({R.tekst_rozmiaru(w['rozmiar'])}). Sprawdzam, czy to dobry skan — chwilę…")
            else:
                self._ocena("zielony", f"Plik skopiowany: {nazwa} ({R.tekst_rozmiaru(w['rozmiar'])}).")
            self._odswiez_kroki()
            self._odswiez_pliki()
        elif typ == "kontrola":
            k = z["kontrola"]
            self._ocena(k["werdykt"], f"{Path(z['wpis']['cel']).name}: {k['tekst']}")
            self._dziennik(f"Ocena skanu {Path(z['wpis']['cel']).name}: {k['tytul']}", blad=k["werdykt"] == "czerwony")
            self._odswiez_kroki()
            self._odswiez_pliki()
        elif typ == "kontrola_start":
            self._odswiez_stan()
        elif typ == "brak_miejsca":
            self.etykieta_alarmu.setText(z["tekst"])
            self.etykieta_alarmu.show()
            self._dziennik(z["tekst"], blad=True)
        elif typ == "blad":
            self._dziennik(z["tekst"], blad=True)
            if self.isMinimized():
                self.showNormal()
        elif typ in ("info", "foldery", "partia"):
            self._dziennik(z["tekst"])
            self._odswiez_foldery()
            self._odswiez_kroki()
            self._odswiez_pliki()
        elif typ == "spakowano":
            self._po_spakowaniu(z)
        elif typ == "szukanie":
            self._po_szukaniu(z)

    # ------------------------------------------------------------------ teksty kroku
    def _zapisz_teksty(self) -> None:
        if self._pokazany is None:
            return
        for p, pole in self.pola.items():
            self.sesja.ustaw_pole(self._pokazany, p, pole.text())
        self.sesja.ustaw_notatke(self._pokazany, self.pole_notatki.toPlainText())
        self._odswiez_kroki()

    def _wybrano_krok(self, wiersz: int) -> None:
        if wiersz < 0:
            return
        id_ = self.lista_krokow.item(wiersz).data(Qt.UserRole)
        if id_ == self._pokazany:
            return
        self._zapisz_teksty()
        self.sesja.ustaw_biezacy(id_)
        self._pokaz_krok(id_)
        self._odswiez_kroki()

    def _przejdz(self, id_: str | None) -> None:
        if id_ is not None:
            self._pokaz_krok(id_)
        else:
            self._pokaz_krok(self._pokazany or self.sesja.biezacy)
            self._ocena("zielony", "To był ostatni krok. Sprawdź listę braków po lewej i kliknij „Zakończ i spakuj”.")
        self._odswiez_kroki()

    # ------------------------------------------------------------------ akcje czlowieka
    def krok_zrobiony(self) -> None:
        id_ = self._pokazany
        self._zapisz_teksty()
        ocena = next(o for o in self.sesja.kompletnosc() if o["id"] == id_)
        if ocena["braki"] and not self._pytaj_tak_nie(
                "W tym kroku czegoś brakuje",
                "W tym kroku brakuje:\n• " + "\n• ".join(ocena["braki"]) + "\n\nPrzejść dalej mimo to? (Do kroku można wrócić, klikając go na liście.)", False):
            return
        self._przejdz(self.sesja.zakoncz_krok(id_))

    def pomin_krok(self) -> None:
        id_ = self._pokazany
        self._zapisz_teksty()
        powod = self._pytaj_tekst("Nie udało się / pomijam", "Napisz jednym zdaniem, dlaczego (to też jest ważna informacja):")
        if powod is None:
            return
        self._przejdz(self.sesja.pomin_krok(id_, powod.strip() or "(bez powodu)"))

    def przywroc_krok(self) -> None:
        self.sesja.przywroc_krok(self._pokazany)
        self._pokaz_krok(self._pokazany)
        self._odswiez_kroki()

    def stoper_start(self) -> None:
        self.sesja.stoper_start(self._pokazany)
        self.etykieta_stopera.setText("stoper chodzi: 0:00")

    def stoper_stop(self) -> None:
        sek = self.sesja.stoper_stop(self._pokazany)
        if sek is None:
            self.etykieta_stopera.setText("stoper nie był włączony")
            return
        self.etykieta_stopera.setText(f"zmierzono: {tekst_czasu(sek)}")
        if "czas_skanu" in self.pola:
            stary = self.pola["czas_skanu"].text().strip()
            self.pola["czas_skanu"].setText((stary + "; " if stary else "") + tekst_czasu(sek))
            self._zapisz_teksty()

    def zrzut_ekranu(self) -> None:
        if self._odliczanie > 0:
            return
        if self.opoznienie_zrzutu_s <= 0:
            self.zbieracz.zrzut("reczny", self._pokazany)
            return
        self._odliczanie = int(self.opoznienie_zrzutu_s)
        self.przycisk_zrzut.setText(f"Zrzut za {self._odliczanie}… przełącz okno")
        if self.pole_chowaj.isChecked():
            self.showMinimized()
        self.zegar_zrzutu.start()

    def _takt_zrzutu(self) -> None:
        self._odliczanie -= 1
        if self._odliczanie > 0:
            self.przycisk_zrzut.setText(f"Zrzut za {self._odliczanie}… przełącz okno")
            return
        self.zegar_zrzutu.stop()
        self.przycisk_zrzut.setText("Zrzut ekranu (za 3 s)")
        self.zbieracz.zrzut("reczny", self._pokazany)
        if self.pole_chowaj.isChecked():
            QTimer.singleShot(2500, lambda: self.isMinimized() and self.showNormal())

    def dodaj_pliki(self) -> None:
        pliki = self._pytaj_pliki()
        if pliki:
            self.zbieracz.dodaj_recznie(pliki, self._pokazany)
            self._dziennik(f"Dodaję ręcznie {len(pliki)} plik(ów) do kroku {self.sesja.numer_kroku(self._pokazany)}…")

    def dodaj_folder_reczny(self) -> None:
        folder = self._pytaj_folder("Dodaj cały folder do bieżącego kroku (kopia jednorazowa)")
        if folder:
            self.zbieracz.dodaj_recznie([folder], self._pokazany)
            self._dziennik(f"Kopiuję folder {folder} do kroku {self.sesja.numer_kroku(self._pokazany)}…")

    def kopia_calego_folderu(self) -> None:
        self.zbieracz.kopia_calych_folderow(self._pokazany)
        self._dziennik("Kopiuję całą zawartość obserwowanych folderów — pasek pokaże postęp…")

    def dodaj_folder_obserwowany(self, folder: str | None = None, skopiuj: bool | None = None) -> None:
        folder = folder or self._pytaj_folder("Folder, do którego program skanera zapisuje pliki")
        if not folder:
            return
        if skopiuj is None:
            n, rozmiar = 0, 0
            for _, r, _ in R.pliki_w_folderze(Path(folder), (self.sesja.folder,)):
                n, rozmiar = n + 1, rozmiar + r
                if n >= 20000:
                    break
            if n >= 20000:
                if not self._pytaj_tak_nie(
                        "Bardzo duży folder",
                        f"W folderze {folder} jest ponad 20 000 plików. Obserwowanie całego dysku albo wielkiego folderu jest powolne — lepiej wskazać "
                        "sam folder programu skanera (ten z „Order Save Path”).\n\nObserwować ten folder mimo to? (Pliki, które już w nim są, nie będą kopiowane.)", False):
                    return
                self.zbieracz.dodaj_folder(folder, False)
                return
            skopiuj = bool(n) and self._pytaj_tak_nie(
                "W folderze są już pliki",
                f"W tym folderze jest już {n} plików ({R.tekst_rozmiaru(rozmiar)}).\n\nSkopiować je TERAZ do bieżącego kroku?\n"
                "Tak — jeśli to dzisiejsze skany, których okno jeszcze nie ma.\nNie — okno będzie kopiować tylko nowe pliki (stare trafią do kopii całego folderu na końcu).", True)
        self.zbieracz.dodaj_folder(folder, bool(skopiuj))

    def dragEnterEvent(self, ev) -> None:  # noqa: N802 - nazwa z Qt
        if ev.mimeData().hasUrls():
            ev.acceptProposedAction()

    def dropEvent(self, ev) -> None:  # noqa: N802
        self._bezpiecznie(self._upuszczono, [u.toLocalFile() for u in ev.mimeData().urls() if u.isLocalFile()])

    def _upuszczono(self, sciezki: list[str]) -> None:
        if sciezki:
            self.zbieracz.dodaj_recznie(sciezki, self._pokazany)
            self._dziennik(f"Przeciągnięto {len(sciezki)} plik(ów) / folder(ów) — kopiuję do kroku {self.sesja.numer_kroku(self._pokazany)}…")

    def _wybrano_plik(self) -> None:
        id_ = self._id_zaznaczonego()
        if id_ is None:
            return
        w = self.sesja.wpis(id_)
        k = w.get("kontrola")
        if k:
            self._ocena(k["werdykt"], f"{Path(w['cel']).name}: {k['tekst']}")
        else:
            self._ocena("szary", f"{Path(w['cel']).name}: {w['cel']} ({R.tekst_rozmiaru(w['rozmiar'])}, SHA-256 {w['sha256'][:16]}…)")

    def przenies_plik(self) -> None:
        id_ = self._id_zaznaczonego()
        if id_ is None:
            self._ocena("szary", "Najpierw zaznacz plik w tabeli.")
            return
        nazwy = [f"{i + 1}. {k.tytul}" for i, k in enumerate(self.sesja.kroki)]
        wybor = self._pytaj_wybor("Przenieś plik", "Do którego kroku należy ten plik? (przenoszona jest tylko kopia w sesji)", nazwy)
        if wybor is None:
            return
        self.sesja.przenies_plik(id_, self.sesja.kroki[nazwy.index(wybor)].id)
        self._odswiez_kroki()
        self._odswiez_pliki()

    def _otworz_folder(self, folder: Path) -> None:
        if self.otwieraj_foldery and hasattr(os, "startfile"):
            os.startfile(str(folder))  # noqa: S606 - Eksplorator Windows na folderze sesji

    # ------------------------------------------------------------------ szukanie plikow skanow na dyskach
    def szukaj_skanow(self) -> None:
        if self._szukanie is not None and self._szukanie.is_alive():
            self._przerwij_szukanie.set()
            return
        self._przerwij_szukanie.clear()
        self.przycisk_szukaj.setText("Szukam… (kliknij, aby przerwać)")
        self._dziennik("Szukam na dyskach plików STL / PLY / OBJ zmienionych w ostatnich 3 godzinach…")
        pomijaj = (self.sesja.folder.parent, UST.KORZEN / "modele_plytek")

        def praca() -> None:
            try:
                wynik = R.szukaj_nowych_siatek(przerwij=self._przerwij_szukanie.is_set, pomijaj=pomijaj)
                self.zbieracz.zdarzenia.put({"typ": "szukanie", "wynik": wynik, "blad": None})
            except BaseException as e:  # noqa: BLE001
                self.zbieracz.zdarzenia.put({"typ": "szukanie", "wynik": [], "blad": f"{type(e).__name__}: {e}"})

        self._szukanie = threading.Thread(target=praca, name="szukanie", daemon=True)
        self._szukanie.start()

    def _po_szukaniu(self, z: dict) -> None:
        self.przycisk_szukaj.setText("Nie wiem, gdzie skaner zapisuje — szukaj")
        obserwowane = {os.path.normcase(str(s)) for _, s in self.sesja.foldery()}
        wyniki = [w for w in z["wynik"] if not any(os.path.normcase(w["folder"]).startswith(o) for o in obserwowane)]
        if z.get("blad"):
            self._dziennik(f"Szukanie nie udało się: {z['blad']}", blad=True)
        if not wyniki:
            self._ocena("zolty", "Nie znalazłem świeżych plików STL / PLY / OBJ poza obserwowanymi folderami. Program skanera mógł jeszcze nic nie zapisać: "
                                 "poszukaj w nim przycisku „Explore” (folder zlecenia) albo eksportu („Go to Send” → „Export”), zrób zrzut ekranu i spróbuj ponownie.")
            return
        pozycje = [f"{w['folder']}   ({w['plikow']} plików, ostatni {dt.datetime.fromtimestamp(w['najnowszy']).strftime('%H:%M:%S')}: {w['przyklad']})" for w in wyniki[:30]]
        wybor = self._pytaj_wybor("Znalezione świeże pliki skanów", "Który folder jest folderem programu skanera? Okno zacznie go obserwować i skopiuje pliki, które już w nim są.", pozycje)
        if wybor is not None:
            self.zbieracz.dodaj_folder(wyniki[pozycje.index(wybor)]["folder"], True)

    # ------------------------------------------------------------------ pomiar szczegolowy (narzedzie T10, osobny proces)
    def pomiar_szczegolowy(self) -> None:
        id_ = self._id_zaznaczonego()
        siatki = [w for w in self.sesja.pliki_kroku(self._pokazany) if Path(w["cel"]).suffix.lower() in R.ROZSZERZENIA_SIATEK]
        wpis = self.sesja.wpis(id_) if id_ is not None else (siatki[-1] if siatki else None)
        if wpis is None or Path(wpis["cel"]).suffix.lower() not in R.ROZSZERZENIA_SIATEK:
            self._ocena("szary", "Zaznacz w tabeli plik skanu (STL / PLY), który ma być zmierzony.")
            return
        domyslny = re.search(r"\d+[.,]\d+", self.sesja.m["kroki"][wpis["krok"]]["pola"].get("wspolczynnik", "") or "")
        tekst = self._pytaj_tekst("Pomiar szczegółowy", "Współczynnik z etykiety bloku (z kropką, np. 1.2234; prace spieczone: 1):", domyslny.group().replace(",", ".") if domyslny else "1.22")
        if tekst is None:
            return
        try:
            wspolczynnik = float(tekst.replace(",", "."))
        except ValueError:
            self._ocena("zolty", f"„{tekst}” to nie jest liczba — pomiar nie został uruchomiony.")
            return
        projekty = self._pytaj_folder("Folder z projektami STL TYLKO tych koron, które leżą na płytce (Anuluj = pomiar samej płytki)")
        polecenie = self.polecenie_pomiaru(wpis, wspolczynnik, projekty or None)
        flagi = subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0
        srodowisko = {**os.environ, "PYTHONUTF8": "1", "PYTHONPATH": os.pathsep.join([str(UST.KORZEN)] + [p for p in os.environ.get("PYTHONPATH", "").split(os.pathsep) if p])}
        subprocess.Popen(polecenie, cwd=str(UST.KORZEN), creationflags=flagi, env=srodowisko)
        self.sesja.zdarzenie("pomiar szczegolowy uruchomiony", plik=wpis["id"], wspolczynnik=wspolczynnik, z_projektami=bool(projekty))
        self._dziennik(f"Pomiar szczegółowy uruchomiony w osobnym oknie (2–6 minut); wynik trafi do folderu sesji: pomiary/{Path(polecenie[-1]).name}")

    def polecenie_pomiaru(self, wpis: dict, wspolczynnik: float, projekty: str | None) -> list[str]:
        """Wiersz polecen narzedzia T10 dla skanu ``wpis``; przy kroku-powtorce dodaje skan odniesienia (powtarzalnosc)."""
        skan = self.sesja.sciezka(wpis["cel"])
        wyjscie = self.sesja.sciezka(f"pomiary/k{wpis['id']:04d}_{R.nazwa_bezpieczna(skan.stem)}_pomiar")
        polecenie = [sys.executable, str(NARZEDZIE_POMIARU), str(skan), "--wspolczynnik", f"{wspolczynnik:.4f}"]
        if projekty:
            polecenie += ["--projekty", projekty]
        krok = self.sesja.krok(wpis["krok"])
        if krok.kontrola == "powtorka" and krok.porownaj_z:
            odn = [w for w in self.sesja.pliki_kroku(krok.porownaj_z) if Path(w["cel"]).suffix.lower() in R.ROZSZERZENIA_SIATEK]
            if odn:
                polecenie += ["--powtorka", str(self.sesja.sciezka(odn[-1]["cel"]))]
        return polecenie + ["--wyj", str(wyjscie)]

    # ------------------------------------------------------------------ zakonczenie
    def zakoncz_i_spakuj(self) -> None:
        if self._pakowanie:
            return
        self._zapisz_teksty()
        braki, _ = self.sesja.braki()
        if braki and not self._pytaj_tak_nie(
                "Brakuje wymaganych kroków",
                "UWAGA — brakuje wymaganych kroków:\n• " + "\n• ".join(braki) + "\n\nMożna spakować mimo to (braki będą w raporcie), ale lepiej je uzupełnić, póki skaner jest pod ręką.\n\nSpakować teraz?",
                False):
            return
        self._pakowanie = True
        self.przycisk_spakuj.setEnabled(False)
        self._ocena("szary", "Pakuję sesję: raport, sumy kontrolne, archiwum ZIP… (przy kilku GB trwa to kilka minut; nowe pliki ze skanera poczekają i nie zginą)")
        self.zbieracz.spakuj()

    def _po_spakowaniu(self, z: dict) -> None:
        self._pakowanie = False
        self.przycisk_spakuj.setEnabled(True)
        self.pasek.setValue(0)
        self.pasek.setFormat("")
        wynik = z.get("wynik")
        self.wynik_paczki = wynik
        if wynik is None:
            self._ocena("czerwony", f"Pakowanie nie udało się: {z.get('blad')}. Zebrane pliki są bezpieczne w folderze sesji: {self.sesja.folder}\n"
                                    "Sesja NIE jest oznaczona jako spakowana (poprzednia paczka, jeśli była, została bez zmian). "
                                    "Usuń przyczynę i kliknij „Zakończ i spakuj” jeszcze raz.")
            self._dziennik(f"Pakowanie nie udało się: {z.get('blad')}", blad=True)
            self._odswiez_kroki()
            return
        czesci = "\n".join(f"• {c['sciezka']}  ({R.tekst_rozmiaru(c['rozmiar'])})" for c in wynik["czesci"])
        tekst = (f"Sesja spakowana: {wynik['plikow']} plików, {R.tekst_rozmiaru(wynik['bajtow'])}.\n\nDo wysłania koordynatorowi ({len(wynik['czesci'])} plik(i) ZIP):\n{czesci}\n\n"
                 f"Raport: {wynik['raport']}\n")
        if wynik["braki"]:
            tekst += "\nBRAKI wymaganych kroków (są w raporcie):\n• " + "\n• ".join(wynik["braki"]) + "\n"
        if wynik["niezgodne_z_manifestem"]:
            tekst += "\nUWAGA: pliki zmienione po skopiowaniu: " + ", ".join(wynik["niezgodne_z_manifestem"]) + "\n"
        if wynik["pominiete_w_paczce"]:
            tekst += f"\nW paczce pominięto {len(wynik['pominiete_w_paczce'])} plik(ów) wyglądających na projekty exocad (nazwiska w nazwach) — zostały w folderze sesji.\n"
        tekst += "\nPrzed wysłaniem sprawdź, czy w nazwach zleceń i plików nie ma nazwisk pacjentów. Folderu sesji nie kasuj, dopóki koordynator nie potwierdzi odbioru."
        self._ocena("zolty" if wynik["braki"] else "zielony", tekst)
        self._dziennik(f"Spakowano: {', '.join(Path(c['sciezka']).name for c in wynik['czesci'])}")
        self._odswiez_kroki()
        self._komunikat("Sesja spakowana", tekst)
        self._otworz_folder(self.sesja.folder / R.KATALOG_PACZKI)

    def closeEvent(self, ev) -> None:  # noqa: N802
        # zamkniecie w trakcie pakowania: ostrzezenie; po "Tak" pakowanie jest przerywane bezpiecznie (rdzen: nowe archiwum powstaje pod nazwa
        # tymczasowa, znaczniki "spakowano" dopiero po sukcesie - sesja zostaje niespakowana, poprzednia paczka nietknieta)
        if self._pakowanie and self._bezpiecznie(
                self._pytaj_tak_nie, "Trwa pakowanie sesji",
                "Program właśnie pakuje sesję (raport, sumy, archiwum ZIP).\n\nJeśli zamkniesz okno teraz, paczka NIE powstanie i sesja nie będzie oznaczona "
                "jako spakowana. Zebrane pliki zostają w folderze sesji; po ponownym uruchomieniu trzeba kliknąć „Zakończ i spakuj” jeszcze raz.\n\n"
                "Zamknąć okno mimo to? (Nie = poczekaj na koniec pakowania)", False) is False:
            ev.ignore()
            return
        self._bezpiecznie(self._zapisz_teksty)
        self._przerwij_szukanie.set()
        self.zegar.stop()
        self._bezpiecznie(self.zbieracz.stop)
        self._bezpiecznie(self.sesja.log, "okno zamkniete")
        ev.accept()


# ----------------------------------------------------------------------------
# start
# ----------------------------------------------------------------------------
def wybierz_sesje(a, ust: dict | None, pytaj=None) -> R.Sesja:
    """Sesja do pracy: wskazana (--sesja), nowa (--nowa) albo - domyslnie - wznowienie ostatniej niedokonczonej.
    ``pytaj(tytul, tekst) -> bool`` pyta czlowieka (okno dialogowe); None = bez pytan (wznawia niedokonczona, inaczej nowa)."""
    katalog = a.dane if a.dane is not None else R.KATALOG_SESJI
    if a.sesja is not None:
        return R.Sesja.wznow(a.sesja)
    foldery = list(a.folder or [])
    if not foldery and ust is not None and ust["sciezki"].get("folder_eksportu_skanera"):
        foldery = [ust["sciezki"]["folder_eksportu_skanera"]]
    sesje = [] if a.nowa else R.Sesja.lista(katalog)
    if sesje:
        ost = sesje[0]
        if ost["zakonczono"] is None:
            if pytaj is None or pytaj("Niedokończona sesja", f"Znaleziono niedokończoną sesję z {ost['utworzono']} ({ost['plikow']} plików).\n\n"
                                      "Wznowić ją? (Tak = dalszy ciąg tej samej sesji, nic nie ginie; Nie = zupełnie nowa sesja)"):
                return R.Sesja.wznow(ost["folder"])
        elif pytaj is not None and pytaj("Ostatnia sesja jest spakowana", f"Ostatnia sesja ({ost['utworzono']}, {ost['plikow']} plików) jest zakończona i spakowana.\n\n"
                                         "Otworzyć ją ponownie, żeby coś dodać? (Nie = nowa sesja)"):
            return R.Sesja.wznow(ost["folder"])
    return R.Sesja.nowa(katalog, foldery=foldery)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Okno 'Dzien skanera - krok po kroku' albo sprawdzenie paczki (--sprawdz)")
    ap.add_argument("--sprawdz", type=Path, default=None, help="bez okna: sprawdz folder sesji albo archiwum ZIP (sumy, kompletnosc)")
    ap.add_argument("--sesja", type=Path, default=None, help="folder sesji do wznowienia")
    ap.add_argument("--nowa", action="store_true", help="zawsze nowa sesja")
    ap.add_argument("--dane", type=Path, default=None, help="katalog sesji (domyslnie dane/dzien_skanera)")
    ap.add_argument("--folder", action="append", default=None, help="folder eksportu skanera (mozna podac kilka razy; domyslnie z ustawien)")
    ap.add_argument("--ustawienia", type=Path, default=None)
    ap.add_argument("--bez-kontroli", action="store_true", help="tylko zbieranie plikow, bez szybkiej kontroli skanow")
    a = ap.parse_args(argv)
    if a.sprawdz is not None:
        kod, linie = R.sprawdz(a.sprawdz)
        R.wypisz(linie)
        return kod
    app = QApplication.instance() or QApplication(sys.argv)
    tlumacz = QTranslator(app)  # polskie napisy przyciskow w oknach dialogowych Qt (Tak / Nie / Anuluj)
    if tlumacz.load("qtbase_pl", QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)):
        app.installTranslator(tlumacz)
    ust, plik_ust, uwaga = R.wczytaj_ustawienia_bezpiecznie(a.ustawienia)
    if ust is None:
        uwaga = f"Nie wczytano ustawień ({uwaga}) — zbieranie plików działa, ale skany nie będą sprawdzane. Wskaż folder skanera przyciskiem „Dodaj folder…”."
    elif uwaga:
        uwaga = f"Plik ustawień ma błąd ({uwaga}) — użyto {plik_ust.name}."

    def pytaj(tytul: str, tekst: str) -> bool:
        return QMessageBox.question(None, tytul, tekst, QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes) == QMessageBox.Yes

    try:
        sesja = wybierz_sesje(a, ust, pytaj)
    except Exception as e:  # noqa: BLE001 - np. zly plik krokow, brak praw zapisu w katalogu sesji
        QMessageBox.critical(None, "Dzień skanera — nie da się uruchomić", f"{type(e).__name__}: {e}\n\nZrób zdjęcie tego okna i wyślij koordynatorowi. "
                             "Pliki ze skanera możesz na razie kopiować ręcznie do osobnego folderu — niczego nie kasuj w programie skanera.")
        return 1
    okno = Okno(sesja, ust, plik_ust, "brak" if a.bez_kontroli or ust is None else "proces", uwaga_startowa=uwaga)

    def hak(typ, wartosc, slad) -> None:  # wyjatek spoza obslugi przyciskow: log sesji, okno zyje dalej
        okno._wyjatek("excepthook", wartosc)

    sys.excepthook = hak
    threading.excepthook = lambda args: okno.sesja.log_wyjatku(f"watek {args.thread.name if args.thread else '?'}", args.exc_value)
    okno.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
