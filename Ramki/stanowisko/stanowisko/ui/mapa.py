"""mapa - mapa plytki: wszystkie gniazda ukladu w kolorach i z podpisami WYLACZNIE ze stanu (nowe okno, paczka E3-U1a).

``MapaPlytki.ustaw(plytka, geometria, wybrane)``: ``plytka`` to ``kontroler_api.Plytka`` (kolor ``Gniazdo.rgb`` i podpis
``Gniazdo.podpis`` policzyl kontroler ze ``statusy``), ``geometria`` - ``uklad.UkladPlytki`` (ksztalt plytki i gniazd)
albo None (wtedy gniazda sa rysowane jako kratka). Widzet niczego nie liczy i nie zna statusow; klikniecie gniazda =
sygnal ``klik(nr)``. Do testow i kontroli: ``kolory()``, ``podpisy()``, ``numery()``, ``srodek_gniazda(nr)``,
``punkt_probny(nr)``, ``teksty_rysowane()``, ``obrys_plytki()``, ``sciecie()``, ``wyglad_gniazda(nr)``.

Wyglad (``motyw``): plytka to powierzchnia wglebiona na tle okna; gniazdo z praca jest wypelnione kolorem ze stanu, napis na
nim ma kolor ``motyw.tekst_na``. Status nie jest rozpoznawalny tylko po barwie (SPEC p. 2): gniazdo z ubytkiem (klasa koloru
"czerwony" ze stanu) ma jasna obwodke 2 px, gniazdo bez pracy - obwodke przerywana bez wlasnego wypelnienia (kolor ze stanu
= kolor plytki), wybrane gniazdo - pierscien w kolorze akcentu, kursor klawiatury - pierscien przerywany; podpis statusu jest
w gniezdzie, gdy sie miesci, i zawsze w legendzie obok mapy.

Orientacja plytki na mapie: przod plytki jest na dole ekranu (napis "PRZOD PLYTKI"); kwadrat ma wyciety naroznik (pole
``notch`` ukladu), kolo - sciecie orientacyjne po stronie przod-prawo (E3-O3): cieciwa liczona z pola ``flat`` ukladu
(``sciecie_mm``: ``angle_deg`` i ``dist``), rysowana pogrubiona kreska, bo prawdziwe sciecie ma ok. 0,6 mm glebokosci i w skali
mapy byloby ledwie widoczne. Gniazda i trafianie klikniec nie zaleza od obrysu.

Ochrona przed kliknieciem w poprzedni obraz (A-P2): ``przygas(True)`` przygasza mape i do ``przygas(False)`` mapa nie
przyjmuje klikniec. Poprzednia plytka (S3-14): ``oznacz_poprzednia(True)`` - w czasie analizy nowego skanu mapa jest lzej
przygaszona (napis "POPRZEDNIA PLYTKA" stoi w naglowku plytki - nie zaslania gniazd); klikniecia dzialaja (technik moze
konczyc poprzednia plytke). Klawiatura (A-D):
``ustaw_kursor(nr)`` rysuje kursor gniazda, ``sasiad(nr, dx, dy)`` - najblizsze gniazdo w kierunku strzalki.
"""
from __future__ import annotations

import logging
import math
import time
import warnings

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath, QPen, QPolygonF
from PySide6.QtWidgets import QSizePolicy, QWidget

from .. import statusy as ST
from . import motyw
from . import napisy as N

LOG = logging.getLogger(__name__)
MARGINES_PX = 14
MIEJSCE_NA_PODPIS_PX = 26  # pas pod plytka na napis "przod plytki"
KOLUMN_KRATKI = 5
ODCINKOW_LUKU = 360  # obrys plytki okraglej ze scieciem: luk jako lamana (odchylka od okregu ponizej 0,05 piksela)
GRUBOSC_SCIECIA_PX = 4  # kreska na cieciwie sciecia orientacyjnego (obrys plytki ma 1)
PROMIEN_NAROZNIKA_PX = 6  # zaokraglenie naroznikow plytki kwadratowej
OBWODKA_UBYTKU_PX = 2  # jasna obwodka gniazda z ubytkiem (na zewnatrz gniazda)
ODSTEP_PIERSCIENIA_PX = 3  # przerwa miedzy gniazdem a pierscieniem wybranego gniazda
GRUBOSC_PIERSCIENIA_PX = 2
ALFA_OCHRONY = 150  # przygaszenie na czas ochrony (klikniecia pomijane)
ALFA_POPRZEDNIEJ = 105  # lzejsze przygaszenie mapy poprzedniej plytki w czasie analizy nowego skanu (klikniecia dzialaja)
PONOW_UKLAD_S = 60.0  # A-D2: nieudane wczytanie ukladu jest ponawiane po tylu sekundach (chwilowy blad dysku nie zostaje do restartu)
_GEOMETRIE: dict = {}
_BLEDY_UKLADU: dict = {}


def geometria_ukladu(kontroler, nazwa: str | None):
    """``uklad.UkladPlytki`` ukladu ``nazwa`` (ksztalt mapy) albo None, gdy ukladu nie da sie wczytac. Katalog ukladu jak
    w kontrolerze: z ustawien (``[plytki]``), gdy kontroler je ma; inaczej katalog domyslny programu. Wynik pamietany;
    nieudane wczytanie - przez ``PONOW_UKLAD_S``."""
    if not nazwa:
        return None
    ust = getattr(kontroler, "ust", None)
    klucz = (nazwa, id(ust))
    if klucz in _BLEDY_UKLADU and time.monotonic() - _BLEDY_UKLADU[klucz] >= PONOW_UKLAD_S:
        del _BLEDY_UKLADU[klucz]
        _GEOMETRIE.pop(klucz, None)
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
            _BLEDY_UKLADU[klucz] = time.monotonic()
    return _GEOMETRIE[klucz]


def sciecie_mm(uk) -> tuple | None:
    """Konce cieciwy sciecia orientacyjnego plytki okraglej w milimetrach ukladu plytki: ``((x1, y1), (x2, y2))`` albo None
    (kwadrat, uklad bez pola ``flat`` albo z polem, z ktorego nie da sie policzyc cieciwy). Geometria WYLACZNIE z ukladu
    (``uklad.json``): cieciwa jest prostopadla do kierunku ``flat.angle_deg`` (stopnie od +X, y do tylu) i lezy w odleglosci
    ``flat.dist`` od srodka plytki o srednicy ``d``; szerokosc cieciwy wynika z tych liczb (``flat.chord_w`` jej nie zmienia)."""
    if uk is None or getattr(uk, "shape", None) != "round" or not getattr(uk, "d", None):
        return None
    flat = getattr(uk, "flat", None) or {}
    kat, odl = flat.get("angle_deg"), flat.get("dist")
    if not all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) for v in (kat, odl)):
        return None
    pol = uk.d / 2
    if not 0 < odl < pol:
        return None
    nx, ny = math.cos(math.radians(kat)), math.sin(math.radians(kat))
    h = math.sqrt(pol * pol - odl * odl)  # polowa cieciwy
    return (odl * nx - h * ny, odl * ny + h * nx), (odl * nx + h * ny, odl * ny - h * nx)


class MapaPlytki(QWidget):
    klik = Signal(int)  # numer kliknietego gniazda
    MARGINES = MARGINES_PX  # odstep plytki od krawedzi widzetu (E3-U1b: mapa poranna ma mniejszy - trzy plytki obok siebie)

    def __init__(self, rodzic=None):
        super().__init__(rodzic)
        self.setObjectName("mapa")
        self.setMinimumSize(*motyw.UKLAD_WYSOKI.mapa_min)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._plytka = None
        self._gniazda: tuple = ()  # gniazda rysowane (ze stanu)
        self._geometria = None
        self._wybrane: int | None = None
        self._kursor: int | None = None
        self._przygaszona = False
        self._poprzednia = False
        self._ksztalty: dict = {}  # nr -> (QPainterPath, QPointF srodek, promien px, szerokosc px)
        self._rozmiar_ksztaltow = None
        self._obrys = None  # (ksztalt, prostokat plytki, skala px na mm, funkcja mm -> px, uklad)
        self._sciezka_plytki: QPainterPath | None = None  # obrys plytki na ekranie (kwadrat z wycieciem, kolo ze scieciem)
        self._sciecie: tuple | None = None  # konce cieciwy sciecia plytki okraglej na ekranie (QPointF, QPointF)
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

    def przygas(self, przygaszona: bool) -> None:
        """Przygaszenie mapy po zmianie jej zawartosci (A-P2): klikniecia pomijane, obraz przykryty polprzezroczysta warstwa."""
        if przygaszona != self._przygaszona:
            self._przygaszona = przygaszona
            self.update()

    def przygaszona(self) -> bool:
        return self._przygaszona

    def oznacz_poprzednia(self, poprzednia: bool) -> None:
        """S3-14: mapa pokazuje POPRZEDNIA plytke, a wynik nowego skanu nie jest jeszcze gotowy - lzejsze przygaszenie (napis
        jest w naglowku plytki); klikniecia dzialaja (to nie jest ochrona)."""
        if poprzednia != self._poprzednia:
            self._poprzednia = poprzednia
            self.update()

    def poprzednia(self) -> bool:
        return self._poprzednia

    def ustaw_kursor(self, nr: int | None) -> None:
        """Kursor klawiatury (strzalki): przerywany pierscien gniazda ``nr`` (None = bez kursora)."""
        if nr != self._kursor:
            self._kursor = nr
            self.update()

    def kursor(self) -> int | None:
        return self._kursor

    def sasiad(self, nr: int, dx: int, dy: int) -> int | None:
        """Gniazdo najblizsze ``nr`` w kierunku (``dx``, ``dy``) na ekranie (w prawo = (1, 0), w gore = (0, -1)); None, gdy w tym
        kierunku nie ma gniazda. Odchylenie od kierunku liczy sie podwojnie, wiec strzalka idzie "wzdluz rzedu"."""
        self._przelicz()
        if nr not in self._ksztalty:
            return None
        s0 = self._ksztalty[nr][1]
        najlepszy = None
        for inny, (_, s, _, _) in self._ksztalty.items():
            if inny == nr:
                continue
            vx, vy = s.x() - s0.x(), s.y() - s0.y()
            wzdluz = vx * dx + vy * dy
            if wzdluz <= 1.0:
                continue
            w_poprzek = abs(vx * dy - vy * dx)
            if w_poprzek > 2.5 * wzdluz:  # zbyt daleko od kierunku strzalki
                continue
            ocena = wzdluz + 2.0 * w_poprzek
            if najlepszy is None or ocena < najlepszy[0]:
                najlepszy = (ocena, inny)
        return najlepszy[1] if najlepszy else None

    def numery(self) -> list:
        return [g.nr for g in self._gniazda]

    def kolory(self) -> dict:
        """Numer gniazda -> kolor ``#rrggbb``, ktorym gniazdo jest wypelnione (prosto ze stanu)."""
        return {g.nr: g.rgb for g in self._gniazda}

    def podpisy(self) -> dict:
        return {g.nr: g.podpis for g in self._gniazda}

    def wyglad_gniazda(self, nr: int) -> dict:
        """Cechy wygladu gniazda poza barwa (SPEC p. 2): ``obwodka_ubytku`` (jasna obwodka 2 px), ``puste`` (obwodka przerywana,
        bez wlasnego wypelnienia), ``wybrane`` (pierscien akcentu), ``kursor`` (pierscien przerywany) - do testow."""
        g = next(x for x in self._gniazda if x.nr == nr)
        return {"obwodka_ubytku": self._z_ubytkiem(g), "puste": not g.prace, "wybrane": nr == self._wybrane, "kursor": nr == self._kursor}

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

    def obrys_plytki(self) -> QPainterPath | None:
        """Obrys plytki na ekranie (kwadrat z wycietym naroznikiem albo kolo ze scieciem orientacyjnym); None, gdy mapa nie
        zna ukladu (gniazda w kratke) albo nie pokazuje gniazd."""
        self._przelicz()
        return QPainterPath(self._sciezka_plytki) if self._sciezka_plytki is not None else None

    def sciecie(self) -> tuple | None:
        """Konce cieciwy sciecia orientacyjnego plytki okraglej na ekranie (``QPointF``, ``QPointF``); None dla kwadratu, ukladu
        bez pola ``flat`` i mapy bez ukladu."""
        self._przelicz()
        return (QPointF(self._sciecie[0]), QPointF(self._sciecie[1])) if self._sciecie is not None else None

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
        self._sciezka_plytki = None
        self._sciecie = None
        if not self._gniazda:
            return
        numery = [g.nr for g in self._gniazda]
        uk = self._geometria
        znane = {g.id for g in uk.sockets} if uk is not None else set()
        if uk is None or not set(numery) <= znane:
            self._kratka(numery)
            return
        pol = (uk.d if uk.shape == "round" else uk.size) / 2
        w, h = self.width() - 2 * self.MARGINES, self.height() - 2 * self.MARGINES - MIEJSCE_NA_PODPIS_PX
        s = max(1.0, min(w, h) / (2 * pol))
        cx, cy = self.width() / 2, self.MARGINES + h / 2

        def px(x: float, y: float) -> QPointF:
            return QPointF(cx + x * s, cy - y * s)  # y plytki "do tylu" = w gore ekranu; przod plytki na dole

        self._obrys = (uk.shape, QRectF(px(-pol, pol), px(pol, -pol)), s, px, uk)
        self._sciezka_plytki, self._sciecie = self._obrys_ukladu(uk, self._obrys[1], px)
        for g in uk.sockets:
            if g.id not in numery:
                continue
            sciezka = QPainterPath()
            sciezka.addPolygon(QPolygonF([px(x, y) for x, y in g.obrys(64)]))
            sciezka.closeSubpath()
            szer = (g.d_top if g.okragle else g.l) * s
            self._ksztalty[g.id] = (sciezka, px(g.x, g.y), g.promien_gorny * s, szer)

    @staticmethod
    def _obrys_ukladu(uk, prostokat: QRectF, px) -> tuple:
        """(obrys plytki na ekranie, konce cieciwy sciecia albo None). Kwadrat: zaokraglony prostokat bez naroznika ``notch``;
        kolo ze scieciem (``sciecie_mm``): luk od konca do konca cieciwy zamkniety cieciwa; kolo bez sciecia: elipsa."""
        obrys = QPainterPath()
        if uk.shape != "round":
            obrys.addRoundedRect(prostokat, PROMIEN_NAROZNIKA_PX, PROMIEN_NAROZNIKA_PX)
            wyciecie = uk.notch or {}
            if {"x_min", "x_max", "y_min", "y_max"} <= set(wyciecie):  # wyciecie orientacyjne: narozniki plytki i ekranu sie zgadzaja
                naroznik = QPainterPath()
                naroznik.addRect(QRectF(px(wyciecie["x_min"], wyciecie["y_max"]), px(wyciecie["x_max"] + 2, wyciecie["y_min"] - 2)))
                obrys = obrys.subtracted(naroznik)
            return obrys, None
        konce = sciecie_mm(uk)
        if konce is None:
            obrys.addEllipse(prostokat)
            return obrys, None
        pol = uk.d / 2
        (x1, y1), (x2, y2) = konce
        k1, k2 = math.atan2(y1, x1), math.atan2(y2, x2)  # luk plytki: od k1 rosnaco do k2, cieciwa go zamyka
        while k2 <= k1:
            k2 += 2 * math.pi
        if k2 - k1 < math.pi:  # zostaje dluzszy z dwoch lukow (sciecie odcina krotszy): idz w druga strone
            k1, k2 = k2, k1 + 2 * math.pi
        katy = [k1 + (k2 - k1) * i / ODCINKOW_LUKU for i in range(ODCINKOW_LUKU + 1)]
        obrys.addPolygon(QPolygonF([px(pol * math.cos(k), pol * math.sin(k)) for k in katy]))
        obrys.closeSubpath()
        return obrys, (px(x1, y1), px(x2, y2))

    def _kratka(self, numery: list) -> None:
        """Uklad nieznany: gniazda jako kola w kratce (kolejnosc numerow), zeby kolory i podpisy byly widoczne."""
        wierszy = math.ceil(len(numery) / KOLUMN_KRATKI)
        w, h = self.width() - 2 * self.MARGINES, self.height() - 2 * self.MARGINES
        bok = max(20.0, min(w / KOLUMN_KRATKI, h / max(1, wierszy)))
        x0 = (self.width() - bok * KOLUMN_KRATKI) / 2
        for i, nr in enumerate(numery):
            srodek = QPointF(x0 + (i % KOLUMN_KRATKI + 0.5) * bok, self.MARGINES + (i // KOLUMN_KRATKI + 0.5) * bok)
            sciezka = QPainterPath()
            sciezka.addEllipse(srodek, bok * 0.42, bok * 0.42)
            self._ksztalty[nr] = (sciezka, srodek, bok * 0.42, bok * 0.84)

    def resizeEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        self._rozmiar_ksztaltow = None
        super().resizeEvent(zdarzenie)

    # --- rysowanie -------------------------------------------------------------------------------
    def paintEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(motyw.TLO))
        if self._napis:
            p.setFont(motyw.czcionka(16, True))
            p.setPen(QColor(motyw.TEKST_POMOCNICZY))
            p.drawText(self.rect().adjusted(30, 30, -30, -30), int(Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap), self._napis)
            self._rysuj_warstwy(p)
            p.end()
            return
        self._przelicz()
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self._obrys is not None:
            self._rysuj_plytke(p)
        for g in self._gniazda:
            if g.nr in self._ksztalty:
                self._rysuj_gniazdo(p, g)
        if self._wybrane in self._ksztalty:  # wybrane gniazdo: pierscien akcentu na zewnatrz gniazda, z przerwa w kolorze plytki
            odstep, grubosc = ODSTEP_PIERSCIENIA_PX, GRUBOSC_PIERSCIENIA_PX
            self._pierscien(p, self._wybrane, ((motyw.AKCENT, 2 * (odstep + grubosc), Qt.PenStyle.SolidLine),
                                               (motyw.WGLEBIENIE, 2 * odstep, Qt.PenStyle.SolidLine)))
        if self._kursor in self._ksztalty:  # kursor klawiatury: przerywany pierscien tuz przy gniezdzie
            self._pierscien(p, self._kursor, ((motyw.WGLEBIENIE, 2 * ODSTEP_PIERSCIENIA_PX, Qt.PenStyle.SolidLine),
                                              (motyw.AKCENT_FOKUS, 2 * ODSTEP_PIERSCIENIA_PX, Qt.PenStyle.DashLine)))
        self._rysuj_warstwy(p)
        p.end()

    def _pierscien(self, p: QPainter, nr: int, kreski: tuple) -> None:
        """Kreski (kolor, grubosc, styl) wzdluz obrysu gniazda ``nr``, widoczne tylko NA ZEWNATRZ gniazda (wnetrze przyciete)."""
        sciezka = self._ksztalty[nr][0]
        p.save()
        calosc = QPainterPath()
        calosc.addRect(QRectF(self.rect()))
        p.setClipPath(calosc.subtracted(sciezka))
        p.setBrush(Qt.BrushStyle.NoBrush)
        for kolor, grubosc, styl in kreski:
            pioro = QPen(QColor(kolor), grubosc)
            pioro.setStyle(styl)
            p.setPen(pioro)
            p.drawPath(sciezka)
        p.restore()

    def _rysuj_warstwy(self, p: QPainter) -> None:
        """Warstwy nad mapa: przygaszenie mapy poprzedniej plytki (S3-14) i przygaszenie na czas ochrony (A-P2)."""
        if self._poprzednia and self._plytka is not None:
            kolor = QColor(motyw.TLO)
            kolor.setAlpha(ALFA_POPRZEDNIEJ)
            p.fillRect(self.rect(), kolor)
        if self._przygaszona:
            kolor = QColor(motyw.TLO)
            kolor.setAlpha(ALFA_OCHRONY)
            p.fillRect(self.rect(), kolor)

    def _rysuj_plytke(self, p: QPainter) -> None:
        ksztalt, prostokat, s, px, uk = self._obrys
        p.setPen(QPen(QColor(motyw.OBWODKA), 1))
        p.setBrush(QBrush(QColor(motyw.WGLEBIENIE)))
        if ksztalt == "round" and self._sciecie is None:  # kolo bez pola flat w ukladzie
            p.drawEllipse(prostokat)
        else:
            p.drawPath(self._sciezka_plytki)
        if self._sciecie is not None:  # sciecie orientacyjne plytki okraglej: pogrubiona kreska na cieciwie (przod-prawo)
            kreska = QPen(QColor(motyw.TEKST_PRZYGASZONY), GRUBOSC_SCIECIA_PX)
            kreska.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(kreska)
            p.drawLine(self._sciecie[0], self._sciecie[1])
        f = motyw.czcionka(11)
        f.setLetterSpacing(QFont.SpacingType.PercentageSpacing, 108)
        p.setFont(f)
        p.setPen(QColor(motyw.TEKST_PRZYGASZONY))
        p.drawText(QRectF(0, prostokat.bottom() + 6, self.width(), MIEJSCE_NA_PODPIS_PX), int(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop),
                   N.MAPA_PRZOD)

    @staticmethod
    def _z_ubytkiem(g) -> bool:
        """Gniazdo z ubytkiem: klasa koloru "czerwony" ze stanu (UBYTEK, UKRUSZONA) - dostaje jasna obwodke."""
        return bool(g.prace) and g.kolor == ST.KOLOR_CZERWONY

    def _wypelnij_gniazdo(self, p: QPainter, g, sciezka: QPainterPath) -> None:
        """Tlo gniazda: kolor ze stanu; z ubytkiem - jasna obwodka na zewnatrz; bez pracy - obwodka przerywana."""
        if self._z_ubytkiem(g):
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(QPen(QColor(motyw.OBWODKA_UBYTKU), 2 * OBWODKA_UBYTKU_PX))
            p.drawPath(sciezka)  # polowa kreski lezy pod wypelnieniem - zostaje obwodka na zewnatrz gniazda
        p.setBrush(QBrush(QColor(g.rgb)))
        if g.prace:
            p.setPen(Qt.PenStyle.NoPen)
        else:
            pioro = QPen(QColor(motyw.OBWODKA_MOCNA), 1)
            pioro.setStyle(Qt.PenStyle.DashLine)
            p.setPen(pioro)
        p.drawPath(sciezka)

    @staticmethod
    def _kolor_napisu(g) -> QColor:
        return QColor(motyw.tekst_na(g.rgb) if g.prace else motyw.tekst_pustego(g.rgb))

    def _rysuj_gniazdo(self, p: QPainter, g) -> None:
        sciezka, srodek, promien, szer = self._ksztalty[g.nr]
        self._wypelnij_gniazdo(p, g, sciezka)
        p.setPen(self._kolor_napisu(g))
        podluzne = szer > 3 * promien  # rynienka: numer i podpis w jednej linii
        if podluzne:
            f = motyw.czcionka(max(12, min(22, promien * 0.62)), True)
            p.setFont(f)
            tekst = f"{g.nr}   {g.podpis}" if g.podpis else str(g.nr)
            p.drawText(QRectF(srodek.x() - szer / 2, srodek.y() - promien * 0.75, szer, promien * 1.3), int(Qt.AlignmentFlag.AlignCenter), tekst)
            return
        f = motyw.czcionka(max(12, min(24, promien * 0.5)), True)
        numer = QRectF(srodek.x() - promien, srodek.y() - promien * 0.6, 2 * promien, promien * 1.2)
        if not g.podpis:
            p.setFont(f)
            p.drawText(numer, int(Qt.AlignmentFlag.AlignCenter), str(g.nr))
            return
        pol_szer = max(10.0, promien * 0.95 - 3)
        pole = QRectF(srodek.x() - pol_szer, srodek.y() - promien * 0.3, 2 * pol_szer, promien * 0.9)
        flagi = int(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter | Qt.TextFlag.TextWordWrap)
        podpis = None
        for rozmiar in range(int(max(9, min(16, promien * 0.34))), 7, -1):  # najwiekszy napis, ktory miesci sie w gniezdzie
            proba = motyw.czcionka(rozmiar, True)
            p.setFont(proba)
            potrzebne = p.boundingRect(pole, flagi, g.podpis)
            najdluzsze = max(p.fontMetrics().horizontalAdvance(slowo) for slowo in g.podpis.split())  # slowo nie lamie sie w polowie
            if najdluzsze <= pole.width() and potrzebne.width() <= pole.width() + 1 and potrzebne.height() <= pole.height() + 1:
                podpis = proba
                break
        if podpis is None:  # A-D7: podpis nie miesci sie nawet najmniejsza czcionka - sam numer (legenda i widok pracy mowia reszte)
            p.setFont(f)
            p.drawText(numer, int(Qt.AlignmentFlag.AlignCenter), str(g.nr))
            return
        p.setFont(f)
        p.drawText(QRectF(srodek.x() - promien, srodek.y() - promien * 0.88, 2 * promien, promien * 0.6), int(Qt.AlignmentFlag.AlignCenter), str(g.nr))
        p.setFont(podpis)
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
        okno = self.window()
        if okno is not self and okno.focusWidget() is not okno:
            okno.setFocus(Qt.FocusReason.MouseFocusReason)  # klawiatura wraca do okna (Enter nie kliknie przycisku z fokusem)
        if zdarzenie.button() == Qt.MouseButton.LeftButton and not self._przygaszona:  # przygaszona: klikniecie w poprzedni obraz
            nr = self.gniazdo_w_punkcie(zdarzenie.position())
            if nr is not None:
                self.klik.emit(nr)
