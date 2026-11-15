"""ui_test — proste okno do testu skanera (PySide6) na silniku plate → match → inspect z ``porownaj``.

Uruchomienie: ``uruchom_okno.bat`` (z katalogu stanowisko/) albo ``py -3.12 -m stanowisko.ui_test [--skan …] [--projekty …]``.

Okno: wybór pliku skanu (STL), folderu projektów, płytki (domyślnie „rozpoznaj automatycznie”: program sam rozpoznaje
układ ze skanu i podpisuje go pod listą; albo ręcznie układ z ``[plytki]`` w ustawieniach: R59 i poprzedni
``*_r54`` dla starych płytek; gdy skan nie pasuje do wybranego układu, okno pokazuje komunikat strażnika układu
i przekreśloną mapę bez kolorów gniazd), współczynnika
skurczu, numeru płytki (kwadraty: dołki kodu poza polem ø100), przycisk „Porównaj” z paskiem postępu
(praca w wątku, okno nie zamarza), mapa płytki z gniazdami w kolorach (zielone = OK, czerwone = ubytek,
żółte = sprawdź / popraw ułożenie / skan ponownie, szare = bez projektu, pomarańczowe = poprawka ręczna,
fiolet = podwójne), tabela wyników, klik w gniazdo → obraz mapy odchyłek (rzut z góry, czerwone = brak
materiału) i przycisk „Podgląd 3D” (Open3D w osobnym procesie, bo okno GL Open3D i pętla Qt w jednym
procesie blokują się na Windows), zapis JSON/PNG, decyzja technika „Ukruszona” / „OK” → ``dane/decyzje.csv``
(czas, skan, gniazdo, id projektu SHA‑16, zęby, decyzja, status programu — bez nazwisk).
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import math
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from PySide6.QtCore import QObject, Qt, QThread, Signal
from PySide6.QtGui import QBrush, QColor, QImage, QPainter, QPen, QPixmap, QPolygonF
from PySide6.QtCore import QPointF
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox, QFileDialog, QGridLayout, QHBoxLayout, QLabel, QLineEdit,
                               QMainWindow, QMessageBox, QProgressBar, QPushButton, QSpinBox, QSplitter, QTableWidget, QTableWidgetItem,
                               QVBoxLayout, QWidget)

from . import match as M
from . import porownaj as PO
from . import synth as S
from . import uklad as U
from . import ustawienia as UST

PLIK_DECYZJI = UST.KORZEN / "dane" / "decyzje.csv"
KOLUMNY_DECYZJI = ("czas", "skan", "gniazdo", "projekt", "zeby", "decyzja", "status_programu", "ubytkow")


# ----------------------------------------------------------------------------
# silnik w wątku
# ----------------------------------------------------------------------------
class Robotnik(QObject):
    postep = Signal(str, float)
    gotowe = Signal(dict, dict, object)  # wynik, podgląd (gniazdo → WynikInspekcji), pula (do ponownego użycia)
    blad = Signal(str)

    def __init__(self, skan: Path, projekty: Path, plytka: str, w: float | None, numer: int | None, ust: dict, pula: M.Pula | None,
                 pula_dla=None):
        super().__init__()
        self.skan, self.projekty, self.plytka, self.w, self.numer, self.ust, self.pula = skan, projekty, plytka, w, numer, ust, pula
        self.pula_dla = pula_dla  # w → pula z pamięci okna albo None (współczynnik znany dopiero po rozpoznaniu płytki)

    def _pula(self, w: float) -> M.Pula:
        p = self.pula_dla(w) if self.pula_dla is not None else None
        if p is None:
            self.postep.emit("pula projektów (wczytanie STL)", 0.45)
            p = M.Pula([self.projekty], w)
        return p

    def uruchom(self) -> None:
        try:
            podglad: dict = {}
            kontekst: dict = {}
            if self.pula is None and self.w is not None:
                self.postep.emit("pula projektów (wczytanie STL)", 0.05)
                self.pula = M.Pula([self.projekty], self.w)
            wynik = PO.porownaj(self.skan, [self.projekty], self.plytka, self.ust, self.w, self.numer, "auto", False, self.pula,
                                podglad=podglad, postep=lambda e, u: self.postep.emit(e, u), pula_dla=self._pula, kontekst=kontekst)
            self.gotowe.emit(wynik, podglad, kontekst.get("pula") or self.pula)
        except Exception as e:  # noqa: BLE001 — każdy błąd silnika trafia do okna
            self.blad.emit(f"{type(e).__name__}: {e}\n{traceback.format_exc()}")


# ----------------------------------------------------------------------------
# mapa płytki
# ----------------------------------------------------------------------------
class MapaPlytki(QWidget):
    klik = Signal(int)

    def __init__(self):
        super().__init__()
        self.uk: U.UkladPlytki | None = None
        self.stan: dict[int, dict] = {}
        self.podwojne: list[int] = []
        self.poza: list = []
        self.wybrane: int | None = None
        self.niezgodny = False  # strażnik układu: skan nie pasuje do wybranego układu
        self.setMinimumSize(360, 360)

    def ustaw(self, uk: U.UkladPlytki | None, wynik: dict | None) -> None:
        self.uk = uk
        self.stan = {g["gniazdo"]: g for g in wynik["gniazda"] if g["gniazdo"] is not None} if wynik else {}
        self.poza = [g["srodek"] for g in wynik["gniazda"] if g["gniazdo"] is None] if wynik else []
        self.podwojne = wynik["gniazda_podwojne"] if wynik else []
        self.niezgodny = bool(wynik) and wynik.get("uklad_zgodny") is False
        self.update()

    def promien_plytki(self) -> float:
        return (self.uk.size if self.uk.shape == "square" else self.uk.d) / 2 + 4

    def skala(self) -> float:
        r = self.promien_plytki()
        return min(self.width(), self.height()) / (2 * r)

    def na_piksel(self, x: float, y: float) -> QPointF:
        s = self.skala()
        return QPointF(self.width() / 2 + x * s, self.height() / 2 - y * s)

    def na_mm(self, px: float, py: float) -> tuple[float, float]:
        s = self.skala()
        return (px - self.width() / 2) / s, (self.height() / 2 - py) / s

    def kolor_gniazda(self, gid: int) -> QColor:
        if gid in self.podwojne:
            return QColor(*PO.KOLORY["podwojny"])
        if gid in self.stan:
            return QColor(*PO.KOLORY[self.stan[gid].get("status_gniazda", self.stan[gid]["status"])])
        return QColor(*PO.KOLORY["pusty"])

    def paintEvent(self, ev) -> None:  # noqa: N802 — nazwa z Qt
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(255, 255, 255))
        if self.uk is None:
            p.drawText(self.rect(), Qt.AlignCenter, "wybierz płytkę")
            return
        p.setRenderHint(QPainter.Antialiasing)
        uk = self.uk
        p.setPen(QPen(QColor(0, 0, 0), 2))
        if uk.shape == "round":
            a, b = self.na_piksel(-uk.d / 2, uk.d / 2), self.na_piksel(uk.d / 2, -uk.d / 2)
            p.drawEllipse(a.x(), a.y(), b.x() - a.x(), b.y() - a.y())
        else:
            a, b = self.na_piksel(-uk.size / 2, uk.size / 2), self.na_piksel(uk.size / 2, -uk.size / 2)
            p.drawRect(a.x(), a.y(), b.x() - a.x(), b.y() - a.y())
        for g in uk.sockets:
            poly = QPolygonF([self.na_piksel(x, y) for x, y in g.obrys(48)])
            p.setBrush(QBrush(self.kolor_gniazda(g.id)))
            p.setPen(QPen(QColor(0, 0, 0), 3) if g.id == self.wybrane else QPen(QColor(60, 60, 60), 1))
            p.drawPolygon(poly)
            p.setPen(QPen(QColor(0, 0, 0)))
            s = self.stan.get(g.id)
            k = s["kandydaci"][0] if s and s["kandydaci"] else None
            podpis = str(g.id) + (f"\n{'-'.join(k['zeby']) or k['id'][:6]}" if k else "")
            ins = s.get("inspekcja") if s else None
            if ins and ins["status"] != "ok":
                podpis += f"\n{ins['status']}"
            c = self.na_piksel(g.x, g.y)
            p.drawText(int(c.x()) - 40, int(c.y()) - 20, 80, 44, Qt.AlignCenter, podpis)
            if ins:
                p.setPen(QPen(QColor(0, 0, 0), 2))
                p.setBrush(Qt.NoBrush)
                for u in ins["ubytki"]:
                    rr = max(0.6, u["srednica_mm"] / 2) * self.skala()
                    cu = self.na_piksel(u["x"], u["y"])
                    p.drawEllipse(cu, rr, rr)
        p.setPen(QPen(QColor(0, 0, 200), 2))
        p.setBrush(Qt.NoBrush)
        for z in uk.markers:
            c = self.na_piksel(z.x, z.y)
            p.drawEllipse(c, z.d / 2 * self.skala(), z.d / 2 * self.skala())
        p.setPen(QPen(QColor(*PO.KOLORY["poza"]), 3))
        for x, y, _ in self.poza:  # praca poza gniazdem
            c = self.na_piksel(x, y)
            p.drawEllipse(c, 3 * self.skala(), 3 * self.skala())
        if self.niezgodny:  # płytka nie pasuje do wybranego układu: mapa przekreślona, gniazda bez kolorów
            pol = (uk.size if uk.shape == "square" else uk.d) / 2
            p.setPen(QPen(QColor(*PO.KOLORY["czerwony"]), 5))
            p.drawLine(self.na_piksel(-pol, -pol), self.na_piksel(pol, pol))
            p.drawLine(self.na_piksel(-pol, pol), self.na_piksel(pol, -pol))
            p.drawText(self.rect(), Qt.AlignTop | Qt.AlignHCenter, "PŁYTKA NIE PASUJE DO WYBRANEGO UKŁADU")
        p.end()

    def mousePressEvent(self, ev) -> None:  # noqa: N802
        if self.uk is None:
            return
        x, y = self.na_mm(ev.position().x(), ev.position().y())
        g = self.uk.najblizsze_gniazdo(x, y, 1.0)
        if g is not None:
            self.wybrane = g.id
            self.update()
            self.klik.emit(g.id)


# ----------------------------------------------------------------------------
# obraz odchyłek (rzut z góry)
# ----------------------------------------------------------------------------
def obraz_odchylek(P: np.ndarray, d: np.ndarray, ubytki: list[dict], prog: float, px_na_mm: float = 28.0) -> Image.Image:
    """Rzut z góry punktów pracy: szary = w tolerancji, czerwony = pod powierzchnią projektu (brak materiału), niebieski = nad."""
    lo, hi = P[:, :2].min(0) - 1.0, P[:, :2].max(0) + 1.0
    w, h = int((hi[0] - lo[0]) * px_na_mm) + 1, int((hi[1] - lo[1]) * px_na_mm) + 1
    im = Image.new("RGB", (max(w, 50), max(h, 50)), (255, 255, 255))
    pix = im.load()
    kol = np.full((len(d), 3), 190, dtype=np.int32)
    u = np.clip(np.abs(d) / (3 * prog), 0, 1)
    pod, nad = d < -prog, d > prog
    kol[pod] = np.c_[190 + 65 * u[pod], 190 - 170 * u[pod], 190 - 170 * u[pod]].astype(int)
    kol[nad] = np.c_[190 - 170 * u[nad], 190 - 120 * u[nad], 190 + 65 * u[nad]].astype(int)
    ix = ((P[:, 0] - lo[0]) * px_na_mm).astype(int)
    iy = ((hi[1] - P[:, 1]) * px_na_mm).astype(int)
    kolej = np.argsort(P[:, 2])  # wyższe punkty rysowane później (widok z góry)
    for i in kolej:
        if 0 <= ix[i] < im.width and 0 <= iy[i] < im.height:
            pix[ix[i], iy[i]] = tuple(int(v) for v in kol[i])
    dr = ImageDraw.Draw(im)
    for ub in ubytki:
        r = max(0.5, ub["srednica_mm"] / 2) * px_na_mm
        cx, cy = (ub["x"] - lo[0]) * px_na_mm, (hi[1] - ub["y"]) * px_na_mm
        dr.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(0, 0, 0) if ub["kolor"] == "czerwony" else (90, 90, 90), width=2)
        dr.text((cx + r + 2, cy - 6), f"{ub['metoda']} ø{ub['srednica_mm']:.2f}", fill=(0, 0, 0))
    dr.text((4, 4), f"rzut z gory, {px_na_mm:.0f} px/mm; czerwone = pod powierzchnia projektu (>= {prog} mm), niebieskie = nad", fill=(0, 0, 0))
    return im


def pil_na_pixmap(im: Image.Image) -> QPixmap:
    im = im.convert("RGBA")
    q = QImage(im.tobytes("raw", "RGBA"), im.width, im.height, QImage.Format_RGBA8888)
    return QPixmap.fromImage(q.copy())


# ----------------------------------------------------------------------------
# okno
# ----------------------------------------------------------------------------
class Okno(QMainWindow):
    def __init__(self, ust: dict | None = None, plik_decyzji: Path = PLIK_DECYZJI):
        super().__init__()
        self.ust = ust if ust is not None else UST.wczytaj_ustawienia()
        self.plik_decyzji = plik_decyzji
        self.wynik: dict | None = None
        self.podglad: dict = {}
        self.uk: U.UkladPlytki | None = None
        self.pule: dict[tuple, M.Pula] = {}
        self.watek: QThread | None = None
        self.robotnik: Robotnik | None = None
        self.setWindowTitle("Stanowisko kontroli cyrkonii — porównanie skanu (test skanera)")
        self._zbuduj()

    # --- układ okna
    def _zbuduj(self) -> None:
        srodek = QWidget()
        self.setCentralWidget(srodek)
        uklad = QVBoxLayout(srodek)
        form = QGridLayout()
        self.pole_skan = QLineEdit()
        self.pole_projekty = QLineEdit(self.ust["sciezki"]["folder_cyrkon"])
        self.przycisk_skan = QPushButton("…")
        self.przycisk_projekty = QPushButton("…")
        self.przycisk_skan.clicked.connect(self.wybierz_skan)
        self.przycisk_projekty.clicked.connect(self.wybierz_projekty)
        self.lista_plytek = QComboBox()
        self.lista_plytek.addItems(list(self.ust["plytki"]))
        self.lista_plytek.currentTextChanged.connect(self.zmiana_plytki)
        self.pole_auto = QCheckBox("rozpoznaj automatycznie")
        self.pole_auto.setToolTip("Program sam rozpoznaje płytkę ze skanu: wieczorna / poranna, nowy układ gniazd (R59) / stary (R54), kwadrat / koło.")
        self.etykieta_plytki = QLabel("")
        self.pole_wspolczynnik = QDoubleSpinBox()
        self.pole_wspolczynnik.setRange(0.5, 2.0)
        self.pole_wspolczynnik.setDecimals(3)
        self.pole_wspolczynnik.setSingleStep(0.005)
        self.pole_numer = QSpinBox()
        self.pole_numer.setRange(0, 15)
        self.pole_numer.setSpecialValueText("auto (z dołków)")
        self.przycisk_porownaj = QPushButton("Porównaj")
        self.przycisk_porownaj.clicked.connect(self.porownaj)
        self.pasek = QProgressBar()
        self.pasek.setRange(0, 100)
        self.etykieta_stanu = QLabel("gotowe")
        form.addWidget(QLabel("Skan (STL):"), 0, 0)
        form.addWidget(self.pole_skan, 0, 1)
        form.addWidget(self.przycisk_skan, 0, 2)
        form.addWidget(QLabel("Folder projektów:"), 1, 0)
        form.addWidget(self.pole_projekty, 1, 1)
        form.addWidget(self.przycisk_projekty, 1, 2)
        form.addWidget(QLabel("Płytka:"), 2, 0)
        form.addWidget(self.lista_plytek, 2, 1)
        form.addWidget(self.pole_auto, 2, 2)
        form.addWidget(self.etykieta_plytki, 4, 2)
        form.addWidget(QLabel("Współczynnik skurczu:"), 3, 0)
        form.addWidget(self.pole_wspolczynnik, 3, 1)
        form.addWidget(QLabel("Numer płytki (kwadraty: dołki poza polem):"), 4, 0)
        form.addWidget(self.pole_numer, 4, 1)
        form.addWidget(self.przycisk_porownaj, 5, 0)
        form.addWidget(self.pasek, 5, 1)
        form.addWidget(self.etykieta_stanu, 5, 2)
        uklad.addLayout(form)

        dzielnik = QSplitter(Qt.Horizontal)
        self.mapa = MapaPlytki()
        self.mapa.klik.connect(self.wybierz_gniazdo)
        dzielnik.addWidget(self.mapa)
        prawa = QWidget()
        pu = QVBoxLayout(prawa)
        self.tabela = QTableWidget(0, 8)
        self.tabela.setHorizontalHeaderLabels(["gniazdo", "projekt", "zęby", "pokrycie", "pewność", "match", "inspect", "ubytki"])
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.itemSelectionChanged.connect(self.zmiana_wiersza)
        pu.addWidget(self.tabela)
        self.obraz = QLabel("klik w gniazdo → mapa odchyłek")
        self.obraz.setMinimumHeight(240)
        self.obraz.setAlignment(Qt.AlignCenter)
        pu.addWidget(self.obraz)
        przyciski = QHBoxLayout()
        self.przycisk_3d = QPushButton("Podgląd 3D (Open3D)")
        self.przycisk_3d.clicked.connect(self.podglad_3d)
        self.przycisk_zapisz = QPushButton("Zapisz JSON/PNG")
        self.przycisk_zapisz.clicked.connect(self.zapisz)
        self.przycisk_ukruszona = QPushButton("Ukruszona")
        self.przycisk_ok = QPushButton("OK")
        self.przycisk_ukruszona.clicked.connect(lambda: self.decyzja("ukruszona"))
        self.przycisk_ok.clicked.connect(lambda: self.decyzja("ok"))
        for b in (self.przycisk_3d, self.przycisk_zapisz, self.przycisk_ukruszona, self.przycisk_ok):
            przyciski.addWidget(b)
        pu.addLayout(przyciski)
        dzielnik.addWidget(prawa)
        dzielnik.setSizes([450, 650])
        uklad.addWidget(dzielnik, 1)
        self.zmiana_plytki(self.lista_plytek.currentText())
        self.pole_auto.toggled.connect(self.zmiana_auto)
        self.pole_auto.setChecked(True)  # domyślnie program sam rozpoznaje płytkę; wybór z listy wyłącza tryb automatyczny
        self.resize(1200, 820)

    # --- pola
    def wybierz_skan(self) -> None:
        p, _ = QFileDialog.getOpenFileName(self, "Plik skanu", str(Path(self.pole_skan.text()).parent if self.pole_skan.text() else self.ust["sciezki"]["folder_eksportu_skanera"]), "STL (*.stl)")
        if p:
            self.pole_skan.setText(p)

    def wybierz_projekty(self) -> None:
        p = QFileDialog.getExistingDirectory(self, "Folder projektów STL", self.pole_projekty.text())
        if p:
            self.pole_projekty.setText(p)

    def tryb_auto(self) -> bool:
        return self.pole_auto.isChecked()

    def zmiana_auto(self, wlaczone: bool) -> None:
        """Tryb automatyczny: lista układów nieaktywna, współczynnik „auto” (domyślny dla rozpoznanej płytki), numer do 15."""
        self.lista_plytek.setEnabled(not wlaczone)
        if not wlaczone:
            self.pole_wspolczynnik.setSpecialValueText("")
            self.etykieta_plytki.setText("")
            self.zmiana_plytki(self.lista_plytek.currentText())
            return
        wiecz = (self.ust["synth"]["wspolczynnik_min"] + self.ust["synth"]["wspolczynnik_max"]) / 2
        self.pole_wspolczynnik.setSpecialValueText(f"auto (wieczorna {wiecz:.3f} / poranna {S.WSPOLCZYNNIK_PORANNA[0]:.3f})")
        self.pole_wspolczynnik.setValue(self.pole_wspolczynnik.minimum())
        self.pole_numer.setMaximum(15)
        self.etykieta_plytki.setText("płytka zostanie rozpoznana ze skanu")
        self.uk = None
        self.mapa.ustaw(None, None)

    def zmiana_plytki(self, nazwa: str) -> None:
        if getattr(self, "pole_auto", None) is not None and self.pole_auto.isChecked():
            self.pole_auto.setChecked(False)  # układ wybrany z listy (także programowo) = tryb ręczny; zmiana_auto wywoła nas ponownie
            return
        try:
            self.uk = U.wczytaj(nazwa, UST.katalog_plytki(self.ust, nazwa))
        except Exception as e:  # noqa: BLE001
            self.uk = None
            self.etykieta_stanu.setText(f"płytka: {e}")
        self.pole_wspolczynnik.setValue(PO.wspolczynnik_domyslny(nazwa, self.ust))
        self.pole_numer.setMaximum(max(self.uk.numery) if self.uk else 15)
        self.mapa.ustaw(self.uk, None)

    # --- porównanie
    def porownaj(self) -> None:
        skan, projekty = Path(self.pole_skan.text()), Path(self.pole_projekty.text())
        if not skan.is_file():
            QMessageBox.warning(self, "Brak skanu", f"Nie ma pliku skanu: {skan}")
            return
        if not projekty.is_dir():
            QMessageBox.warning(self, "Brak projektów", f"Nie ma folderu projektów: {projekty}")
            return
        auto = self.tryb_auto()
        plytka = PO.AUTO if auto else self.lista_plytek.currentText()
        w_auto = auto and self.pole_wspolczynnik.value() <= self.pole_wspolczynnik.minimum() + 1e-9  # pole pokazuje „auto (…)”
        w = None if w_auto else round(self.pole_wspolczynnik.value(), 4)
        numer = self.pole_numer.value() or None
        folder = str(projekty.resolve())
        klucz = (folder, w)
        pula = self.pule.get(klucz) if w is not None else None
        self.przycisk_porownaj.setEnabled(False)
        self.pasek.setValue(0)
        self.etykieta_stanu.setText("start…")
        self.watek = QThread()
        self.robotnik = Robotnik(skan, projekty, plytka, w, numer, self.ust, pula,
                                 pula_dla=lambda w_: self.pule.get((folder, round(w_, 4))))
        self.robotnik.moveToThread(self.watek)
        self.watek.started.connect(self.robotnik.uruchom)
        self.robotnik.postep.connect(self.postep)
        self.robotnik.gotowe.connect(self.gotowe)
        self.robotnik.blad.connect(self.blad)
        self.robotnik.gotowe.connect(self.watek.quit)
        self.robotnik.blad.connect(self.watek.quit)
        self._klucz_puli = klucz
        self.watek.start()

    def postep(self, etap: str, udzial: float) -> None:
        self.pasek.setValue(int(udzial * 100))
        self.etykieta_stanu.setText(etap)

    def gotowe(self, wynik: dict, podglad: dict, pula: M.Pula) -> None:
        self.wynik, self.podglad = wynik, podglad
        if pula is not None:
            klucz = self._klucz_puli if self._klucz_puli[1] is not None else (self._klucz_puli[0], round(pula.wspolczynnik, 4))
            self.pule[klucz] = pula
        if wynik.get("plytka_wybor") == "auto":  # układ rozpoznany przez program: pokaż go i narysuj jego mapę
            ua = wynik.get("uklad_auto") or {}
            if wynik.get("uklad_zgodny") is False:
                self.uk = None
                self.etykieta_plytki.setText("nie rozpoznano płytki")
            else:
                self.uk = U.wczytaj(wynik["plytka"], UST.katalog_plytki(self.ust, wynik["plytka"]))
                self.etykieta_plytki.setText(f"rozpoznano: {wynik['plytka']} — {PO.opis_ukladu(wynik['plytka'], self.uk)}; nr {wynik['numer'] or '?'}; "
                                             f"współczynnik {wynik['wspolczynnik']:.3f}" + ("" if ua.get("pewny", True) else " — NIEPEWNE: wpisz numer płytki albo wybierz układ z listy"))
        self.pasek.setValue(100)
        self.przycisk_porownaj.setEnabled(True)
        st = wynik["statusy_gniazd"]
        self.etykieta_stanu.setText(f"gotowe: {wynik['czas_s']['razem']} s; " + ", ".join(f"{PO.OPISY_STATUSU[s]} {n}" for s, n in st.items() if n) + f"; ubytków {wynik['ubytki']}")
        self.mapa.ustaw(self.uk, wynik)
        self.wypelnij_tabele()
        if wynik.get("uklad_zgodny") is False and wynik.get("plytka_wybor") == "auto":  # żaden układ z ustawień nie pasuje do skanu
            self.etykieta_stanu.setText("NIE ROZPOZNANO UKŁADU PŁYTKI")
            QMessageBox.warning(self, "Nie rozpoznano układu płytki",
                                "Program nie rozpoznał, jaka płytka jest na skanie — żadne gniazdo nie zostało ocenione.\n\n"
                                "Sprawdź, czy skan obejmuje całą płytkę z trzema stożkami znaczników. Możesz też wyłączyć „rozpoznaj "
                                "automatycznie” i wybrać układ z listy.\n\n" + wynik["uklad_komunikat"])
        elif wynik.get("uklad_zgodny") is False:  # strażnik układu (R59): żadnych gniazd, czytelny komunikat zamiast błędu wyrównania
            self.etykieta_stanu.setText("PŁYTKA NIE PASUJE DO WYBRANEGO UKŁADU")
            pasuja = wynik.get("uklady_pasujace") or []
            # stary lokalny ustawienia.toml (bez układów *_r54) i żaden układ nie pasuje: podpowiedź, których wierszy brakuje
            podpowiedz = ("W lokalnym pliku ustawienia.toml nie ma układów …_r54 dla starych płytek fizycznych (sprzed R59) — dopisz w [plytki] "
                          "4 wiersze *_r54 z ustawienia.przyklad.toml, uruchom okno ponownie i wybierz układ …_r54.") if wynik.get("uklad_podpowiedz") else ""
            QMessageBox.warning(self, "Płytka nie pasuje do wybranego układu",
                                f"Zeskanowana płytka nie pasuje do układu „{wynik['plytka']}” wybranego na liście „Płytka”.\n\n"
                                + (f"Rozstaw stożków w skanie pasuje do: {', '.join(pasuja)} — wybierz ten układ i porównaj ponownie.\n\n" if pasuja
                                   else (podpowiedz or "Rozstaw stożków w skanie nie pasuje do żadnego układu z listy — sprawdź płytkę i skan.") + "\n\n")
                                + wynik["uklad_komunikat"])

    def blad(self, tekst: str) -> None:
        self.przycisk_porownaj.setEnabled(True)
        self.etykieta_stanu.setText("błąd")
        QMessageBox.critical(self, "Błąd porównania", tekst)

    def wypelnij_tabele(self) -> None:
        g_lista = sorted(self.wynik["gniazda"], key=lambda g: (g["gniazdo"] is None, g["gniazdo"] or 0))
        self.tabela.setRowCount(len(g_lista))
        for i, g in enumerate(g_lista):
            k = g["kandydaci"][0] if g["kandydaci"] else None
            ins = g.get("inspekcja")
            wart = ["poza" if g["gniazdo"] is None else str(g["gniazdo"]), k["id"] if k else "—", "-".join(k["zeby"]) if k else "",
                    f"{k['pokrycie']:.3f}" if k else "", f"{g['pewnosc']:.3f}", g["status"], ins["status"] if ins else "—",
                    ", ".join(f"{u['metoda']} ø{u['srednica_mm']:.2f}" for u in ins["ubytki"]) if ins else ""]
            kolor = QColor(*PO.KOLORY[g["status_gniazda"]])
            for j, v in enumerate(wart):
                it = QTableWidgetItem(v)
                it.setFlags(it.flags() & ~Qt.ItemIsEditable)
                it.setBackground(QBrush(kolor.lighter(150)))
                self.tabela.setItem(i, j, it)
        self.tabela.resizeColumnsToContents()

    # --- wybór gniazda
    def wybierz_gniazdo(self, gid: int) -> None:
        for i in range(self.tabela.rowCount()):
            if self.tabela.item(i, 0).text() == str(gid):
                self.tabela.selectRow(i)
                return
        self.obraz.setText(f"gniazdo {gid}: puste")

    def gniazdo_wybrane(self) -> int | None:
        w = self.tabela.currentRow()
        if w < 0 or self.tabela.item(w, 0) is None:
            return None
        t = self.tabela.item(w, 0).text()
        return int(t) if t.isdigit() else None

    def zmiana_wiersza(self) -> None:
        gid = self.gniazdo_wybrane()
        if gid is None:
            return
        self.mapa.wybrane = gid
        self.mapa.update()
        wi = self.podglad.get(gid)
        if wi is None or wi._P is None:
            self.obraz.setText(f"gniazdo {gid}: brak mapy odchyłek (bez projektu)")
            return
        im = obraz_odchylek(wi._P, wi._d, [u.__dict__ for u in wi.ubytki], self.ust["inspect"]["prog_glebokosci_mm"])
        self.obraz.setPixmap(pil_na_pixmap(im).scaled(self.obraz.width(), max(240, self.obraz.height()), Qt.KeepAspectRatio))

    def podglad_3d(self) -> None:
        gid = self.gniazdo_wybrane()
        wi = self.podglad.get(gid) if gid is not None else None
        if wi is None or wi._P is None:
            QMessageBox.information(self, "Podgląd 3D", "Wybierz gniazdo z rozpoznaną pracą.")
            return
        plik = Path(tempfile.gettempdir()) / f"stanowisko_podglad_g{gid}.npz"
        np.savez(plik, P=wi._P.astype(np.float32), d=wi._d.astype(np.float32), ubytki=np.array([[u.x, u.y, u.z, u.srednica_mm] for u in wi.ubytki], dtype=np.float32).reshape(-1, 4))
        subprocess.Popen([sys.executable, "-m", "stanowisko.podglad3d", str(plik), str(self.ust["inspect"]["prog_glebokosci_mm"])], cwd=str(UST.KORZEN))

    # --- zapis
    def zapisz(self) -> Path | None:
        if self.wynik is None:
            QMessageBox.information(self, "Zapis", "Najpierw „Porównaj”.")
            return None
        skan = Path(self.pole_skan.text())
        folder = Path(QFileDialog.getExistingDirectory(self, "Folder na JSON i PNG", str(skan.parent)) or "")
        if not folder.name:
            return None
        return self.zapisz_do(folder)

    def zapisz_do(self, folder: Path) -> Path:
        import json

        skan = Path(self.pole_skan.text())
        folder.mkdir(parents=True, exist_ok=True)
        p_json = folder / f"{skan.stem}_wynik.json"
        p_json.write_text(json.dumps(self.wynik, ensure_ascii=False, indent=1), encoding="utf-8")
        PO.mapa_png(self.wynik, self.uk, folder / f"{skan.stem}_mapa.png")
        self.etykieta_stanu.setText(f"zapisano {p_json.name} i PNG w {folder}")
        return p_json

    def decyzja(self, co: str) -> None:
        gid = self.gniazdo_wybrane()
        if gid is None or self.wynik is None:
            QMessageBox.information(self, "Decyzja", "Wybierz gniazdo w tabeli albo na mapie.")
            return
        g = next((x for x in self.wynik["gniazda"] if x["gniazdo"] == gid), None)
        k = g["kandydaci"][0] if g and g["kandydaci"] else None
        ins = g.get("inspekcja") if g else None
        self.plik_decyzji.parent.mkdir(parents=True, exist_ok=True)
        nowy = not self.plik_decyzji.exists()
        with open(self.plik_decyzji, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f, delimiter=";")
            if nowy:
                w.writerow(KOLUMNY_DECYZJI)
            w.writerow([dt.datetime.now().isoformat(timespec="seconds"), Path(self.pole_skan.text()).name, gid, k["id"] if k else "", "-".join(k["zeby"]) if k else "",
                        co, g["status_gniazda"] if g else "", len(ins["ubytki"]) if ins else 0])
        self.etykieta_stanu.setText(f"zapisano decyzję „{co}” dla gniazda {gid} → {self.plik_decyzji.name}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--skan", type=Path, default=None)
    ap.add_argument("--projekty", type=Path, default=None)
    ap.add_argument("--plytka", default=None, help="układ z [plytki]; bez tej opcji okno rozpoznaje płytkę automatycznie")
    ap.add_argument("--ustawienia", type=Path, default=None)
    a = ap.parse_args(argv)
    app = QApplication.instance() or QApplication(sys.argv)
    okno = Okno(UST.wczytaj_ustawienia(a.ustawienia))
    if a.skan:
        okno.pole_skan.setText(str(a.skan))
    if a.projekty:
        okno.pole_projekty.setText(str(a.projekty))
    if a.plytka:
        okno.pole_auto.setChecked(False)
        okno.lista_plytek.setCurrentText(a.plytka)
    okno.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
