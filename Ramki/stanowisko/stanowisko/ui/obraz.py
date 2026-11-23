"""obraz - obraz odchylek jednej pracy (widok z gory) liczony POZA watkiem okna.

Kontroler podaje plik podgladu skanu (``SzczegolyPracy.plik_podgladu``: tablice ``g<nr>_P`` - punkty N x 3 w ukladzie
plytki i ``g<nr>_d`` - odchylka kazdego punktu od projektu w mm). Plik czyta ``kontroler_api.wczytaj_podglad`` (czysta
funkcja kontraktu, bez kontrolera - mozna ja wolac poza watkiem okna). Wczytanie pliku i narysowanie obrazu trwa dziesiatki milisekund,
wiec robi to jeden watek pomocniczy (``QThreadPool``); do okna wraca gotowy ``QImage`` sygnalem ``gotowy(klucz, obraz)``.
Watek pomocniczy nie dotyka kontrolera ani widzetow. Sciezka pliku nigdy nie trafia na ekran.

Kolory obrazu to skala odchylki (szary = zgodnie z projektem, czerwony = brakuje materialu, niebieski = nadmiar) -
jak w oknie testowym; to nie sa kolory statusow. Tlo obrazu to powierzchnia wglebiona okna (``motyw.WGLEBIENIE``, E3-U1a).
"""
from __future__ import annotations

import collections
import logging

from PySide6.QtCore import QObject, QPointF, QRunnable, Qt, QThreadPool, Signal
from PySide6.QtGui import QColor, QImage, QPainter, QPen

from . import motyw

LOG = logging.getLogger(__name__)
TLO_RGB = tuple(int(motyw.WGLEBIENIE[i:i + 2], 16) for i in (1, 3, 5))  # tlo obrazu = tlo pola obrazu w widoku pracy
PROG_ODCHYLKI_MM = 0.08  # od tej odchylki punkt jest kolorowany (prog wykrywania z planu; patrz POTRZEBUJE w raporcie)
SZEROKOSC_PX, WYSOKOSC_PX = 520, 230
PAMIEC_PLIKOW = 2  # tyle ostatnich plikow podgladu trzyma watek pomocniczy (kolejne prace tej samej plytki sa od reki)
PAMIEC_OBRAZOW = 60


def rysuj_odchylki(P, d, ubytki=(), szer: int = SZEROKOSC_PX, wys: int = WYSOKOSC_PX, prog: float = PROG_ODCHYLKI_MM) -> QImage:
    """Rzut z gory punktow pracy ``P`` (N x 3, mm) pokolorowanych odchylka ``d`` (mm); ``ubytki`` - slowniki z ``x``, ``y``,
    ``srednica_mm`` (uklad plytki) rysowane jako kolka. Obliczenia w numpy, bez petli po punktach."""
    import numpy as np  # noqa: PLC0415 - tylko w watku pomocniczym

    P = np.asarray(P, dtype=np.float64)
    d = np.asarray(d, dtype=np.float64)
    tlo = np.empty((wys, szer, 3), dtype=np.uint8)
    tlo[:] = TLO_RGB
    if P.ndim != 2 or P.shape[0] == 0 or P.shape[1] < 3 or d.shape[0] != P.shape[0]:
        return QImage(tlo.tobytes(), szer, wys, 3 * szer, QImage.Format.Format_RGB888).copy()
    lo, hi = P[:, :2].min(0) - 0.6, P[:, :2].max(0) + 0.6
    skala = float(min(szer / (hi[0] - lo[0]), wys / (hi[1] - lo[1])))
    ox, oy = (szer - (hi[0] - lo[0]) * skala) / 2, (wys - (hi[1] - lo[1]) * skala) / 2
    u = np.clip(np.abs(d) / (3 * prog), 0.0, 1.0)
    kolor = np.full((len(d), 3), 186.0)
    pod, nad = d < -prog, d > prog
    kolor[pod] = np.c_[186 + 54 * u[pod], 186 - 160 * u[pod], 186 - 160 * u[pod]]
    kolor[nad] = np.c_[186 - 150 * u[nad], 186 - 100 * u[nad], 186 + 60 * u[nad]]
    ix = (ox + (P[:, 0] - lo[0]) * skala).astype(np.int64)
    iy = (oy + (hi[1] - P[:, 1]) * skala).astype(np.int64)
    kolor = kolor.astype(np.uint8)
    pole = (P[:, 0].max() - P[:, 0].min() + 0.1) * (P[:, 1].max() - P[:, 1].min() + 0.1) * skala * skala
    kropka = int(np.clip(np.sqrt(pole / len(d)) * 1.3 + 1, 2, 7))
    for warstwa in (~pod, pod):  # punkty z brakiem materialu rysowane na koncu - zawsze widoczne
        kolejnosc = np.argsort(P[warstwa, 2], kind="stable")  # wyzsze punkty pozniej (widok z gory)
        wx, wy, wk = ix[warstwa][kolejnosc], iy[warstwa][kolejnosc], kolor[warstwa][kolejnosc]
        for dy in range(kropka):
            for dx in range(kropka):
                tlo[np.clip(wy + dy - kropka // 2, 0, wys - 1), np.clip(wx + dx - kropka // 2, 0, szer - 1)] = wk
    obraz = QImage(tlo.tobytes(), szer, wys, 3 * szer, QImage.Format.Format_RGB888).copy()
    if ubytki:
        p = QPainter(obraz)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        for ub in ubytki:
            try:
                x, y, srednica = float(ub["x"]), float(ub["y"]), float(ub.get("srednica_mm") or 0.5)
            except (KeyError, TypeError, ValueError):
                continue
            if not (lo[0] <= x <= hi[0] and lo[1] <= y <= hi[1]):
                continue  # ubytek poza obrazem tej pracy
            srodek = QPointF(ox + (x - lo[0]) * skala, oy + (hi[1] - y) * skala)
            r = max(0.5, srednica / 2) * skala + 5
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(QPen(QColor(motyw.TEKST), 5))
            p.drawEllipse(srodek, r, r)
            p.setPen(QPen(QColor(motyw.NA_STATUSIE), 2.5))
            p.drawEllipse(srodek, r, r)
        p.end()
    return obraz


class _Zadanie(QRunnable):
    def __init__(self, wczytywacz: "WczytywaczObrazow", klucz, plik, gniazdo: int, ubytki: tuple):
        super().__init__()
        self.wczytywacz, self.klucz, self.plik, self.gniazdo, self.ubytki = wczytywacz, klucz, plik, gniazdo, ubytki

    def run(self) -> None:
        obraz = None
        try:
            dane = self.wczytywacz._dane_pliku(self.plik)
            if self.gniazdo in dane:
                P, d = dane[self.gniazdo]
                obraz = rysuj_odchylki(P, d, self.ubytki)
        except Exception as e:  # noqa: BLE001 - brak obrazu to napis na ekranie, nie awaria
            LOG.warning("obraz odchylek: nie udalo sie przygotowac obrazu (%s)", type(e).__name__)
        if self.wczytywacz.koniec:  # A-D14: okno sie zamyka - bez sygnalu do obiektu w trakcie usuwania
            return
        try:
            self.wczytywacz.gotowy.emit(self.klucz, obraz)
        except RuntimeError:  # okno zamkniete w trakcie liczenia
            pass


class WczytywaczObrazow(QObject):
    """Kolejka obrazow odchylek: ``zlec(klucz, plik, gniazdo, ubytki)`` -> sygnal ``gotowy(klucz, QImage albo None)``
    w watku okna. Jeden watek pomocniczy; gotowe obrazy sa pamietane (``obraz(klucz)``)."""

    gotowy = Signal(object, object)

    def __init__(self, rodzic=None):
        super().__init__(rodzic)
        self._pula = QThreadPool(self)
        self._pula.setMaxThreadCount(1)
        self._pliki: collections.OrderedDict = collections.OrderedDict()  # uzywane tylko w watku pomocniczym (jest jeden)
        self._obrazy: collections.OrderedDict = collections.OrderedDict()
        self._zlecone: set = set()
        self.koniec = False
        self.gotowy.connect(self._zapamietaj)

    def obraz(self, klucz):
        return self._obrazy.get(klucz)

    def zlec(self, klucz, plik, gniazdo: int, ubytki: tuple = ()) -> bool:
        """Zleca obraz; False, gdy jest juz gotowy albo zlecony."""
        if klucz in self._obrazy or klucz in self._zlecone:
            return False
        self._zlecone.add(klucz)
        self._pula.start(_Zadanie(self, klucz, plik, gniazdo, tuple(ubytki)))
        return True

    def _dane_pliku(self, plik) -> dict:
        klucz = str(plik)
        if klucz not in self._pliki:
            from .. import kontroler_api as K  # noqa: PLC0415

            self._pliki[klucz] = K.wczytaj_podglad(plik)  # czysty odczyt pliku (kontrakt), bez kontrolera
            while len(self._pliki) > PAMIEC_PLIKOW:
                self._pliki.popitem(last=False)
        return self._pliki[klucz]

    def _zapamietaj(self, klucz, obraz) -> None:
        self._zlecone.discard(klucz)
        if obraz is not None:
            self._obrazy[klucz] = obraz
            while len(self._obrazy) > PAMIEC_OBRAZOW:
                self._obrazy.popitem(last=False)

    def zakoncz(self) -> None:
        self.koniec = True
        self._pula.clear()
        self._pula.waitForDone(3000)
