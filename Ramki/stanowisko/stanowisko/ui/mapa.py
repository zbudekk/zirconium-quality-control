"""mapa - mapa plytki ekranu wieczornego: wszystkie gniazda ukladu w kolorach i z podpisami WYLACZNIE ze stanu.

``MapaPlytki.ustaw(plytka, geometria, wybrane)``: ``plytka`` to ``kontroler_api.Plytka`` (kolor ``Gniazdo.rgb`` i podpis
``Gniazdo.podpis`` policzyl kontroler ze ``statusy``), ``geometria`` - ``uklad.UkladPlytki`` (ksztalt plytki i gniazd)
albo None (wtedy gniazda sa rysowane jako kratka). Widzet niczego nie liczy i nie zna statusow; klikniecie gniazda =
sygnal ``klik(nr)``. Do testow i kontroli: ``kolory()``, ``podpisy()``, ``numery()``, ``srodek_gniazda(nr)``,
``punkt_probny(nr)``, ``teksty_rysowane()``.
"""
from __future__ import annotations

import logging
import math
import warnings

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath, QPen, QPolygonF
from PySide6.QtWidgets import QSizePolicy, QWidget

from . import napisy as N
from . import styl

LOG = logging.getLogger(__name__)
MARGINES_PX = 14
MIEJSCE_NA_PODPIS_PX = 26  # pas pod plytka na napis "przod plytki"
KOLUMN_KRATKI = 5
_GEOMETRIE: dict = {}


def geometria_ukladu(kontroler, nazwa: str | None):
    """``uklad.UkladPlytki`` ukladu ``nazwa`` (ksztalt mapy) albo None, gdy ukladu nie da sie wczytac. Katalog ukladu jak
    w kontrolerze: z ustawien (``[plytki]``), gdy kontroler je ma; inaczej katalog domyslny programu. Wynik pamietany."""
    if not nazwa:
        return None
    ust = getattr(kontroler, "ust", None)
    klucz = (nazwa, id(ust))
    if klucz not in _GEOMETRIE:
        try:
            from .. import uklad as U  # noqa: PLC0415 - numpy; kontroler laduje ten modul przy starcie

            katalog = None
            if ust is not None and nazwa in (ust.get("plytki") or {}):
                from .. import ustawienia as UST  # noqa: PLC0415

                katalog = UST.katalog_plytki(ust, nazwa)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                _GEOMETRIE[klucz] = U.wczytaj(nazwa, katalog)
        except Exception as e:  # noqa: BLE001 - mapa w kratke jest lepsza niz brak mapy
            LOG.warning("mapa: ukladu plytki nie da sie wczytac (%s) - gniazda w kratke", type(e).__name__)
            _GEOMETRIE[klucz] = None
    return _GEOMETRIE[klucz]


class MapaPlytki(QWidget):
    klik = Signal(int)  # numer kliknietego gniazda

    def __init__(self, rodzic=None):
        super().__init__(rodzic)
        self.setObjectName("mapa")
        self.setMinimumSize(380, 340)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._plytka = None
        self._gniazda: tuple = ()  # gniazda rysowane (ze stanu)
        self._geometria = None
        self._wybrane: int | None = None
        self._ksztalty: dict = {}  # nr -> (QPainterPath, QPointF srodek, promien px, szerokosc px)
        self._rozmiar_ksztaltow = None
        self._obrys = None  # (ksztalt, prostokat plytki, skala px na mm, funkcja mm -> px, uklad)
        self._napis: str = N.MAPA_BRAK_PLYTKI

    # --- dane ------------------------------------------------------------------------------------
    def ustaw(self, plytka, geometria, wybrane: int | None = None) -> None:
        if plytka == self._plytka and geometria is self._geometria and wybrane == self._wybrane:
            return
        # plytka, ktorej skan sie nie liczy i na ktorej program nie znalazl prac (nie pasuje do ukladu, blad analizy): napis zamiast gniazd
        gniazda = tuple(plytka.gniazda) if plytka is not None and (plytka.aktywna or plytka.prace) else ()
        zmiana_ukladu = geometria is not self._geometria or [g.nr for g in gniazda] != [g.nr for g in self._gniazda]
        self._plytka, self._geometria, self._wybrane, self._gniazda = plytka, geometria, wybrane, gniazda
        if plytka is None:
            self._napis = N.MAPA_BRAK_PLYTKI
        elif not gniazda:
            self._napis = N.MAPA_BEZ_GNIAZD.format(napis=plytka.napis)
        else:
            self._napis = ""
        if zmiana_ukladu:
            self._rozmiar_ksztaltow = None
        self.update()

    def numery(self) -> list:
        return [g.nr for g in self._gniazda]

    def kolory(self) -> dict:
        """Numer gniazda -> kolor ``#rrggbb``, ktorym gniazdo jest wypelnione (prosto ze stanu)."""
        return {g.nr: g.rgb for g in self._gniazda}

    def podpisy(self) -> dict:
        return {g.nr: g.podpis for g in self._gniazda}

    def teksty_rysowane(self) -> list:
        """Wszystkie napisy rysowane przez widzet (kontrola: zadnych sciezek, nic zielonego)."""
        if self._napis:
            return [self._napis, self._plytka.napis] if self._plytka is not None else [self._napis]
        return [str(g.nr) for g in self._gniazda] + [g.podpis for g in self._gniazda if g.podpis] + [N.MAPA_PRZOD]

    def srodek_gniazda(self, nr: int) -> QPointF:
        return self._ksztalt(nr)[1]

    def punkt_probny(self, nr: int) -> QPointF:
        """Punkt wewnatrz gniazda blisko dolnej krawedzi - poza napisami (do odczytu koloru z obrazu widzetu)."""
        _, srodek, promien, _ = self._ksztalt(nr)
        return QPointF(srodek.x(), srodek.y() + 0.78 * promien)

    # --- geometria -------------------------------------------------------------------------------
    def _ksztalt(self, nr: int):
        self._przelicz()
        return self._ksztalty[nr]

    def _przelicz(self) -> None:
        rozmiar = (self.width(), self.height())
        if self._rozmiar_ksztaltow == rozmiar:
            return
        self._rozmiar_ksztaltow = rozmiar
        self._ksztalty = {}
        self._obrys = None
        if not self._gniazda:
            return
        numery = [g.nr for g in self._gniazda]
        uk = self._geometria
        znane = {g.id for g in uk.sockets} if uk is not None else set()
        if uk is None or not set(numery) <= znane:
            self._kratka(numery)
            return
        pol = (uk.d if uk.shape == "round" else uk.size) / 2
        w, h = self.width() - 2 * MARGINES_PX, self.height() - 2 * MARGINES_PX - MIEJSCE_NA_PODPIS_PX
        s = max(1.0, min(w, h) / (2 * pol))
        cx, cy = self.width() / 2, MARGINES_PX + h / 2

        def px(x: float, y: float) -> QPointF:
            return QPointF(cx + x * s, cy - y * s)  # y plytki "do tylu" = w gore ekranu; przod plytki na dole

        self._obrys = (uk.shape, QRectF(px(-pol, pol), px(pol, -pol)), s, px, uk)
        for g in uk.sockets:
            if g.id not in numery:
                continue
            sciezka = QPainterPath()
            sciezka.addPolygon(QPolygonF([px(x, y) for x, y in g.obrys(64)]))
            sciezka.closeSubpath()
            szer = (g.d_top if g.okragle else g.l) * s
            self._ksztalty[g.id] = (sciezka, px(g.x, g.y), g.promien_gorny * s, szer)

    def _kratka(self, numery: list) -> None:
        """Uklad nieznany: gniazda jako kola w kratce (kolejnosc numerow), zeby kolory i podpisy byly widoczne."""
        wierszy = math.ceil(len(numery) / KOLUMN_KRATKI)
        w, h = self.width() - 2 * MARGINES_PX, self.height() - 2 * MARGINES_PX
        bok = max(20.0, min(w / KOLUMN_KRATKI, h / max(1, wierszy)))
        x0 = (self.width() - bok * KOLUMN_KRATKI) / 2
        for i, nr in enumerate(numery):
            srodek = QPointF(x0 + (i % KOLUMN_KRATKI + 0.5) * bok, MARGINES_PX + (i // KOLUMN_KRATKI + 0.5) * bok)
            sciezka = QPainterPath()
            sciezka.addEllipse(srodek, bok * 0.45, bok * 0.45)
            self._ksztalty[nr] = (sciezka, srodek, bok * 0.45, bok * 0.9)

    def resizeEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        self._rozmiar_ksztaltow = None
        super().resizeEvent(zdarzenie)

    # --- rysowanie -------------------------------------------------------------------------------
    def paintEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(styl.TLO_PANELU))
        if self._napis:
            f = QFont(styl.CZCIONKA)
            f.setPixelSize(24)
            f.setBold(True)
            p.setFont(f)
            p.setPen(QColor(styl.TEKST_SLABY))
            p.drawText(self.rect().adjusted(30, 30, -30, -30), int(Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap), self._napis)
            p.end()
            return
        self._przelicz()
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self._obrys is not None:
            self._rysuj_plytke(p)
        for g in self._gniazda:
            if g.nr in self._ksztalty:
                self._rysuj_gniazdo(p, g)
        if self._wybrane in self._ksztalty:  # zaznaczenie na wierzchu: bialy i ciemny obrys
            sciezka = self._ksztalty[self._wybrane][0]
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(QPen(QColor("#ffffff"), 9))
            p.drawPath(sciezka)
            p.setPen(QPen(QColor("#101418"), 5))
            p.drawPath(sciezka)
        p.end()

    def _rysuj_plytke(self, p: QPainter) -> None:
        ksztalt, prostokat, s, px, uk = self._obrys
        p.setPen(QPen(QColor("#5b6470"), 2))
        p.setBrush(QBrush(QColor("#f6f7f9")))
        if ksztalt == "round":
            p.drawEllipse(prostokat)
        else:
            obrys = QPainterPath()
            obrys.addRoundedRect(prostokat, 6, 6)
            wyciecie = uk.notch or {}
            if {"x_min", "x_max", "y_min", "y_max"} <= set(wyciecie):  # wyciecie orientacyjne: narozniki plytki i ekranu sie zgadzaja
                naroznik = QPainterPath()
                naroznik.addRect(QRectF(px(wyciecie["x_min"], wyciecie["y_max"]), px(wyciecie["x_max"] + 2, wyciecie["y_min"] - 2)))
                obrys = obrys.subtracted(naroznik)
            p.drawPath(obrys)
        f = QFont(styl.CZCIONKA)
        f.setPixelSize(14)
        f.setBold(True)
        p.setFont(f)
        p.setPen(QColor(styl.TEKST_SLABY))
        p.drawText(QRectF(0, prostokat.bottom() + 4, self.width(), MIEJSCE_NA_PODPIS_PX), int(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop),
                   N.MAPA_PRZOD)

    def _rysuj_gniazdo(self, p: QPainter, g) -> None:
        sciezka, srodek, promien, szer = self._ksztalty[g.nr]
        p.setBrush(QBrush(QColor(g.rgb)))
        p.setPen(QPen(QColor("#3a4047"), 1.5))
        p.drawPath(sciezka)
        kolor_tekstu = QColor(styl.tekst_na(g.rgb)) if g.prace else QColor("#8a929c")
        p.setPen(kolor_tekstu)
        f = QFont(styl.CZCIONKA)
        f.setBold(True)
        podluzne = szer > 3 * promien  # rynienka: numer i podpis w jednej linii
        if podluzne:
            f.setPixelSize(int(max(13, min(26, promien * 0.62))))
            p.setFont(f)
            tekst = f"{g.nr}   {g.podpis}" if g.podpis else str(g.nr)
            p.drawText(QRectF(srodek.x() - szer / 2, srodek.y() - promien * 0.75, szer, promien * 1.3), int(Qt.AlignmentFlag.AlignCenter), tekst)
            return
        f.setPixelSize(int(max(12, min(26, promien * 0.52))))
        p.setFont(f)
        if not g.podpis:
            p.drawText(QRectF(srodek.x() - promien, srodek.y() - promien * 0.6, 2 * promien, promien * 1.2), int(Qt.AlignmentFlag.AlignCenter), str(g.nr))
            return
        p.drawText(QRectF(srodek.x() - promien, srodek.y() - promien * 0.88, 2 * promien, promien * 0.6), int(Qt.AlignmentFlag.AlignCenter), str(g.nr))
        pol_szer = max(10.0, promien * 0.95 - 7)  # 7 px zapasu na obrys zaznaczonego gniazda
        pole = QRectF(srodek.x() - pol_szer, srodek.y() - promien * 0.3, 2 * pol_szer, promien * 0.9)
        flagi = int(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter | Qt.TextFlag.TextWordWrap)
        for rozmiar in range(int(max(9, min(18, promien * 0.36))), 7, -1):  # najwiekszy napis, ktory miesci sie w gniezdzie
            f.setPixelSize(rozmiar)
            p.setFont(f)
            potrzebne = p.boundingRect(pole, flagi, g.podpis)
            najdluzsze = max(p.fontMetrics().horizontalAdvance(slowo) for slowo in g.podpis.split())  # slowo nie lamie sie w polowie
            if najdluzsze <= pole.width() and potrzebne.width() <= pole.width() + 1 and potrzebne.height() <= pole.height() + 1:
                break
        p.drawText(pole, flagi, g.podpis)

    # --- mysz ------------------------------------------------------------------------------------
    def gniazdo_w_punkcie(self, punkt: QPointF) -> int | None:
        self._przelicz()
        for nr, (sciezka, _, _, _) in self._ksztalty.items():
            if sciezka.contains(punkt):
                return nr
        najblizsze = None
        for nr, (_, srodek, promien, _) in self._ksztalty.items():  # klikniecie tuz obok gniazda tez sie liczy
            odleglosc = math.hypot(punkt.x() - srodek.x(), punkt.y() - srodek.y()) - promien
            if odleglosc <= 8 and (najblizsze is None or odleglosc < najblizsze[0]):
                najblizsze = (odleglosc, nr)
        return najblizsze[1] if najblizsze else None

    def mousePressEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        if zdarzenie.button() == Qt.MouseButton.LeftButton:
            nr = self.gniazdo_w_punkcie(zdarzenie.position())
            if nr is not None:
                self.klik.emit(nr)
