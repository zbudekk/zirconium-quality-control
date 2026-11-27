"""mapa_rano - mapa plytki porannej (E3-A7): gniazda ukladu w kolorze klasy pracy porannej i z podpisami WYLACZNIE ze stanu.

``MapaRano`` to ``mapa.MapaPlytki`` z innym wnetrzem gniazda: numer kuwety (``Gniazdo.podpis`` - kontroler podaje kuwete albo
napis statusu, np. "wybierz" / "nieznana"), zab i miniatura przypisanego projektu (``PracaRano.zeby`` / ``miniatura``) oraz
obwodka gniazd biezacej kuwety (rozkladanie wedlug ekranu; gniazda podaje kontroler - ``StanRano.obwodka``, recenzja PR #26 P4). Co sie miesci w gniezdzie, zalezy od jego wielkosci na ekranie:
od promienia ``PROG_MINIATURY_PX`` - numer gniazda, miniatura, kuweta i zab; od ``PROG_ZEBA_PX`` - kuweta i zab; mniejsze -
sama kuweta (albo numer gniazda, gdy i ona sie nie miesci; kolor i legenda mowia reszte). Do testow: ``rysowane()``
(numer gniazda -> co jest narysowane: kuweta, zab, ``sha16`` miniatury), ``punkt_probny`` (piksel tla gniazda poza napisami).
Widzet niczego nie liczy i nie zna statusow.
"""
from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QFontMetricsF, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget

from . import motyw
from . import napisy_rano as NR
from .mapa import MapaPlytki

PROG_MINIATURY_PX = 25.0  # promien gniazda (px), od ktorego w gniezdzie jest miniatura i numer gniazda
PROG_ZEBA_PX = 16.0  # od tego promienia - kuweta i zab
# obwodka gniazd biezacej kuwety: biala z ciemnym brzegiem - INNA niz pierscien akcentu wybranego gniazda (SPEC p. 2; runda 2
# recenzji PR #64, P3: obie w barwie akcentu nie dawaly sie odroznic); objasnienie w legendzie "Na plytkach" (``WzorOznaczenia``)
KOLOR_BIEZACEJ = motyw.TEKST
KOLOR_BIEZACEJ_BRZEG = motyw.TLO
GRUBOSC_BIEZACEJ_PX = 4
GRUBOSC_BRZEGU_BIEZACEJ_PX = 7


def _czcionka(px: float, pogrubiona: bool = True) -> QFont:
    """Czcionka napisow gniazda z ``motyw`` (rodziny z zapasem, cyfry tabelaryczne)."""
    return motyw.czcionka(px, pogrubiona)


class MapaRano(MapaPlytki):
    """Mapa jednej plytki porannej. ``ustaw_rano(plytka, geometria, wybrane, obwodka, obrazy)``: ``obwodka`` - numery gniazd
    biezacej kuwety z kontrolera (``StanRano.obwodka(skan_id)`` - mapa niczego nie liczy), ``obrazy`` - ``sha16`` -> ``QImage``
    miniatury (zdekodowane przez ekran raz)."""

    MARGINES = 4  # E3-U1b: trzy plytki pieca obok siebie - plytka prawie do krawedzi widzetu (wieczorem 14 px)

    def __init__(self, skan_id: int, rodzic=None):
        super().__init__(rodzic)
        self.skan_id = skan_id
        self.setObjectName(f"mapa_rano_{skan_id}")
        self.setMinimumSize(*motyw.UKLAD_WYSOKI.mapa_rano_min)  # ekran ustawia minimum wg ukladu okna (``Uklad.mapa_rano_min``)
        self._obwodka: frozenset = frozenset()
        self._obrazy: dict = {}

    def ustaw_rano(self, plytka, geometria, wybrane: int | None, obwodka: frozenset, obrazy: dict) -> None:
        obwodka = frozenset(obwodka)
        zmiana = obwodka != self._obwodka or obrazy is not self._obrazy
        self._obwodka, self._obrazy = obwodka, obrazy
        self.ustaw(plytka, geometria, wybrane)
        if zmiana:
            self.update()

    # --- plan napisow w gniezdzie (ten sam dla rysowania i dla ``rysowane``) -------------------------------------------
    @staticmethod
    def _praca(g):
        return g.prace[0] if len(g.prace) == 1 else None

    def _plan(self, g) -> list:
        """Elementy do narysowania w gniezdzie: (rodzaj, prostokat, tekst albo sha16, czcionka). Rodzaje: ``nr``, ``kuweta``,
        ``zab``, ``miniatura``."""
        _, srodek, promien, szer = self._ksztalty[g.nr]
        praca = self._praca(g)
        kuweta = g.podpis or ""
        zab = NR.ZAB_KROTKO.format(zab=praca.zeby) if praca is not None and praca.zeby and praca.kuweta and kuweta == praca.kuweta else ""
        sha = praca.sha16 if praca is not None and praca.miniatura and praca.sha16 in self._obrazy else None
        x, y = srodek.x(), srodek.y()
        if szer > 3 * promien:  # rynienka: wszystko w jednej linii
            return self._plan_rynienki(g, x, y, promien, szer, kuweta, zab, sha)
        plan: list = []
        r = promien

        def miesci(tekst: str, px: float, dy: float, pogrubiona: bool = True) -> QFont | None:
            szerokosc = 2 * r * max(0.0, 1 - (abs(dy) / r) ** 2) ** 0.5 - 6  # cieciwa kola na wysokosci napisu, 3 px zapasu z kazdej strony
            for rozmiar in range(int(px), 7, -1):
                f = _czcionka(rozmiar, pogrubiona)
                if QFontMetricsF(f).horizontalAdvance(tekst) <= szerokosc:
                    return f
            return None

        def tekst(rodzaj: str, napis: str, px: float, dy: float, pogrubiona: bool = True) -> bool:
            f = miesci(napis, px, dy, pogrubiona)
            if f is None:
                return False
            h = QFontMetricsF(f).height()
            plan.append((rodzaj, QRectF(x - r, y + dy - h / 2, 2 * r, h), napis, f))
            return True

        if not kuweta:
            tekst("nr", str(g.nr), min(26, max(12, r * 0.52)), 0.0)
            return plan
        if r >= PROG_MINIATURY_PX:
            tekst("nr", str(g.nr), min(13, max(8, r * 0.26)), -0.74 * r, pogrubiona=False)
            if sha is not None:
                bok = 0.6 * r
                plan.append(("miniatura", QRectF(x - bok / 2, y - 0.56 * r, bok, bok), sha, None))
            ok = tekst("kuweta", kuweta, min(22, max(9, r * 0.40)), 0.27 * r)
            if ok and zab:
                tekst("zab", zab, min(16, max(8, r * 0.29)), 0.62 * r, pogrubiona=False)
            if not ok:
                plan[:] = []
                tekst("nr", str(g.nr), min(26, max(12, r * 0.52)), 0.0)
            return plan
        if r >= PROG_ZEBA_PX and zab:
            if tekst("kuweta", kuweta, min(18, max(8, r * 0.48)), -0.16 * r):
                tekst("zab", zab, min(14, max(7, r * 0.34)), 0.42 * r, pogrubiona=False)
                return plan
            plan[:] = []
        if not tekst("kuweta", kuweta, min(18, max(8, r * 0.5)), 0.0):
            tekst("nr", str(g.nr), min(26, max(12, r * 0.52)), 0.0)
        return plan

    def _plan_rynienki(self, g, x: float, y: float, promien: float, szer: float, kuweta: str, zab: str, sha) -> list:
        plan: list = []
        h = 2 * promien
        f = _czcionka(min(22, max(9, promien * 0.62)))
        fs = _czcionka(min(16, max(8, promien * 0.5)), pogrubiona=False)
        odstep = 8.0
        bok = 0.85 * h
        # warianty od najpelniejszego: najpierw znika numer gniazda, potem miniatura, potem zab (kuweta zostaje najdluzej)
        warianty = [(True, True, True), (False, True, True), (False, False, True), (False, False, False)] if kuweta else [(True, False, False)]
        for z_nr, z_mini, z_zebem in warianty:
            czesci = ([("nr", str(g.nr), fs)] if z_nr else []) + ([("kuweta", kuweta, f)] if kuweta else []) + ([("zab", zab, fs)] if zab and z_zebem else [])
            szerokosci = [QFontMetricsF(c[2]).horizontalAdvance(c[1]) for c in czesci]
            mini = z_mini and sha is not None
            razem = sum(szerokosci) + odstep * (len(czesci) - 1) + (bok + odstep if mini else 0.0)
            if razem <= 0.7 * szer:  # lewy koniec rynienki zostaje wolny (tlo gniazda - punkt probny)
                break
        xx = x - razem / 2 + 0.12 * szer
        if mini:
            plan.append(("miniatura", QRectF(xx, y - bok / 2, bok, bok), sha, None))
            xx += bok + odstep
        for (rodzaj, napis, czcionka), w in zip(czesci, szerokosci):
            plan.append((rodzaj, QRectF(xx, y - h / 2, w + 2, h), napis, czcionka))
            xx += w + odstep
        return plan

    # --- rysowanie -----------------------------------------------------------------------------------------------------
    def _rysuj_gniazdo(self, p: QPainter, g) -> None:
        sciezka, srodek, promien, szer = self._ksztalty[g.nr]
        self._wypelnij_gniazdo(p, g, sciezka)  # jak wieczorem: kolor ze stanu, jasna obwodka klasy czerwonej, przerywana - pustego
        kolor_tekstu = self._kolor_napisu(g)
        for rodzaj, prostokat, wartosc, czcionka in self._plan(g):
            if rodzaj == "miniatura":
                p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Screen)  # tlo miniatury (czarne) nie zmienia koloru gniazda
                p.drawImage(prostokat, self._obrazy[wartosc])
                p.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
                continue
            p.setFont(czcionka)
            p.setPen(kolor_tekstu)
            p.drawText(prostokat, int(Qt.AlignmentFlag.AlignCenter), wartosc)
        if self._biezacej(g):
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(QPen(QColor(KOLOR_BIEZACEJ_BRZEG), GRUBOSC_BRZEGU_BIEZACEJ_PX))
            p.drawPath(sciezka)
            p.setPen(QPen(QColor(KOLOR_BIEZACEJ), GRUBOSC_BIEZACEJ_PX))
            p.drawPath(sciezka)

    # --- kontrola (testy) -----------------------------------------------------------------------------------------------
    def rysowane(self) -> dict:
        """Numer gniazda -> {"kuweta", "zab", "miniatura"} narysowane w gniezdzie przy obecnym rozmiarze (None = nie ma)."""
        self._przelicz()
        wynik = {}
        for g in self._gniazda:
            if g.nr not in self._ksztalty:
                continue
            plan = self._plan(g)
            wynik[g.nr] = {r: next((w for rr, _, w, _ in plan if rr == r), None) for r in ("kuweta", "zab", "miniatura", "nr")}
        return wynik

    def biezace(self) -> list:
        """Gniazda z obwodka biezacej kuwety."""
        return [g.nr for g in self._gniazda if self._biezacej(g)]

    def _biezacej(self, g) -> bool:
        """Gniazdo biezacej kuwety - wg kontrolera (ta sama regula co lista kuwet: plytka z numerem jedynym w piecu, praca
        rozpoznana z kuweta zgodna z protokolem ramki)."""
        return g.nr in self._obwodka

    def teksty_rysowane(self) -> list:
        if self._napis:
            return super().teksty_rysowane()
        self._przelicz()
        teksty = []
        for g in self._gniazda:
            if g.nr in self._ksztalty:
                teksty += [w for r, _, w, _ in self._plan(g) if r != "miniatura"]
        return teksty + [g.podpis for g in self._gniazda if g.podpis]

    def punkt_probny(self, nr: int) -> QPointF:
        """Punkt tla gniazda poza napisami i miniatura (lewa czesc gniazda) - do odczytu koloru z obrazu widzetu."""
        _, srodek, promien, szer = self._ksztalt(nr)
        if szer > 3 * promien:
            return QPointF(srodek.x() - 0.44 * szer, srodek.y())
        return QPointF(srodek.x() - 0.72 * promien, srodek.y() - 0.08 * promien)


class WzorOznaczenia(QWidget):
    """Wzor oznaczenia gniazda do legendy "Na plytkach" (runda 2, P3): ``kuweta`` - obwodka gniazd biezacej kuwety (jak
    ``MapaRano``), ``wybrane`` - pierscien akcentu wybranego gniazda z przerwa w kolorze plytki (jak ``MapaPlytki``)."""

    def __init__(self, rodzaj: str, bok: int = 22):
        super().__init__()
        self.rodzaj = rodzaj
        self.setFixedSize(bok, bok)

    def paintEvent(self, _zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        srodek = QPointF(self.width() / 2, self.height() / 2)
        promien = self.width() / 2 - (6 if self.rodzaj == "wybrane" else 4)
        sciezka = QPainterPath()
        sciezka.addEllipse(srodek, promien, promien)
        p.fillPath(sciezka, QColor(motyw.OBWODKA_MOCNA))
        p.setBrush(Qt.BrushStyle.NoBrush)
        if self.rodzaj == "kuweta":
            p.setPen(QPen(QColor(KOLOR_BIEZACEJ_BRZEG), GRUBOSC_BRZEGU_BIEZACEJ_PX / 2))
            p.drawPath(sciezka)
            p.setPen(QPen(QColor(KOLOR_BIEZACEJ), GRUBOSC_BIEZACEJ_PX / 2))
            p.drawPath(sciezka)
        else:
            p.setPen(QPen(QColor(motyw.AKCENT), 2))
            p.drawEllipse(srodek, promien + 4, promien + 4)
        p.end()
