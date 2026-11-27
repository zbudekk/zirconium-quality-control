"""czesci - czesci wspolne okna programu "Stanowisko" (paczka E3-U1a; ``etap3/nowy_interfejs/SPEC.md`` p. 2 i 3).

Sa tu: etykieta, przycisk ekranu i przycisk ze skrotem klawiszowym w ramce, znacznik i kropka statusu, tabela, uklad plynacy,
opis pytania / komunikatu ze stanu (``Uwaga``) i jego panel (``PanelUwagi``), strefa pytan i komunikatow o STALEJ wysokosci
(``StrefaKomunikatow``), lista osob rozwijana pod paskiem gornym (``PanelOsoby``), pasek gorny (``PasekGorny``), pasek stanu
(``PasekStanu``) z lista bledow programu (``ListaBledow``). Wyglad (kolory, czcionki, promienie) pochodzi wylacznie z ``motyw``;
kolory i napisy STATUSOW - z pol stanu (``rgb``, ``podpis``, ``opis``, ``napis``) i ze ``statusy``; pozostale napisy z ``napisy``.

Kazda czesc dostaje gotowe dane ze stanu kontrolera (``ustaw(...)``) i oddaje wybor technika sygnalem - sama nie wola
kontrolera i niczego nie liczy.

Klawiatura: przyciski i kafelki przyjmuja fokus TYLKO klawiszem Tab (nie kliknieciem) - Enter "klika" przycisk z fokusem;
Spacja, U / O / C / N, Esc i strzalki zawsze ida do okna (``PrzyciskEkranu``), dzieki czemu Spacja jest zawsze startem skanu,
a nie "kliknieciem" przycisku. Klikniecie mysza oddaje fokus oknu.

E3-U1b: tryb poranny (``ekran_rano``) uzywa tych samych czesci co wieczor (strefa pytan, kafelek, tabela, przycisk ze skrotem,
znacznik statusu); przejsciowe czesci starego ukladu porannego (``panel_*``, rozmiary ``styl``) zostaly usuniete.
"""
from __future__ import annotations

import dataclasses
import re
import time

from PySide6.QtCore import QEvent, QPoint, QRect, QRectF, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFontMetrics, QIcon, QPainter, QPen
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QFrame, QHBoxLayout, QHeaderView, QLabel, QLayout, QProgressBar, QPushButton,
                               QScrollArea, QSizePolicy, QStyle, QStyleOptionButton, QStylePainter, QTableWidget, QVBoxLayout, QWidget)

from .. import statusy as ST
from . import motyw
from . import napisy as N
from . import napisy_rano as NR

# polecenia, ktore kontroler przyjmuje tylko od wybranej osoby (reszta: zamkniecie pytania / komunikatu, pula, start skanu)
BEZ_OSOBY = ("zamknij_pytanie", "zamknij_komunikat", "odswiez_pule", "start_skanu", "wybierz_operatora", "ustaw_pule", "zamknij",
             "przelacz_tryb", "ustaw_kolejnosc", "wybierz_kuwete")  # poranek (E3-A7)
# "polecenia" przyciskow, ktore obsluguje samo okno (nie ida do kontrolera)
LOKALNE_NUMER_BEZ_ZMIAN = "_numer_bez_zmian"
LOKALNE_ZAMKNIJ_ODPOWIEDZ = "_zamknij_odpowiedz"
LOKALNE_ZAMKNIJ_INFORMACJE = "_zamknij_informacje"
LOKALNE_POKAZ_NOWA = "_pokaz_nowa"  # E3-P14 (N2): "Pokaz nowy wynik"
SKAN_PRZYJETY = "przyjety"  # klucz ``statusy.STATUSY_PLYTKI`` skanu, ktory sie liczy i przyjmuje decyzje
# Start skanu z programu jest atrapa do dnia skanera (kontrakt: ``aplikacja.md`` "Start skanu (DW5)"; stan nie mowi, czy
# akcja startu cokolwiek uruchamia). Do tego czasu przycisk mowi technikowi, ze program czeka na plik, a skan uruchamia sie
# w programie skanera - i nie wyglada jak przycisk glowny (E3-P14 poz. 6).
START_SKANU_ATRAPA = True
LIMIT_LICZENIA_PULI_S = 15.0  # A-D5: po tylu sekundach liczenia "Odswiez pule" znow jest aktywne (liczenie moglo zawisnac)
BLYSK_MS = 1500
# odpowiedz pytania pokazana jako glowna akcja (wypelnienie akcentem) - wg makiety; pozostale pytania: same przyciski zwykle
POZIOM_PYTANIA = "pytanie"  # wyglad pytania: tlo wybranej pozycji z obwodka akcentu (``motyw.POZIOMY``), bez wzgledu na poziom ze stanu
GLOWNE_ODPOWIEDZI = {"ponowny_skan": "potwierdz_ponowny_skan", "plytka_nie_z_trybu": "zamknij_pytanie", "nowy_wsad": "zamknij_piec_i_przenies"}


# ----------------------------------------------------------------------------
# drobne narzedzia
# ----------------------------------------------------------------------------
def etykieta(tekst: str = "", rola: str | None = None, nazwa: str | None = None, zawijaj: bool = False) -> QLabel:
    e = QLabel(tekst)
    e.setTextFormat(Qt.TextFormat.PlainText)  # napis ze stanu nigdy nie jest czytany jako znaczniki
    e.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    if rola:
        e.setProperty("rola", rola)
    if nazwa:
        e.setObjectName(nazwa)
    if zawijaj:
        e.setWordWrap(True)
    return e


def ustaw_role(widzet: QWidget, rola: str, wlasciwosc: str = "rola") -> None:
    """Zmienia wlasciwosc arkusza (``rola``, ``wybrany``, ``poziom`` ...) i odswieza wyglad widzetu."""
    if widzet.property(wlasciwosc) != rola:
        widzet.setProperty(wlasciwosc, rola)
        widzet.style().unpolish(widzet)
        widzet.style().polish(widzet)
        widzet.update()


def _klawisze_okna() -> frozenset:
    k = Qt.Key
    return frozenset((k.Key_Space, k.Key_U, k.Key_O, k.Key_C, k.Key_N, k.Key_Escape, k.Key_Left, k.Key_Right, k.Key_Up, k.Key_Down))


def _do_okna(widzet: QWidget, zdarzenie) -> bool:
    """Klawisz nalezacy do okna (Spacja, U, O, C, N, Esc, strzalki) - przekazany oknu, nawet gdy fokus ma przycisk w obszarze
    przewijanym (ten zjadlby strzalki)."""
    if zdarzenie.key() not in _klawisze_okna():
        return False
    okno = widzet.window()
    if okno is not widzet:
        okno.keyPressEvent(zdarzenie)
    zdarzenie.accept()
    return True


def _fokus_do_okna(widzet: QWidget) -> None:
    """Klikniecie mysza oddaje klawiature oknu: Enter nie "kliknie" pozniej przycisku, do ktorego technik doszedl Tabem."""
    okno = widzet.window()
    if okno is not widzet and okno.focusWidget() is not okno:
        okno.setFocus(Qt.FocusReason.MouseFocusReason)


class PrzyciskEkranu(QPushButton):
    """Przycisk ekranu: fokus tylko Tabem; Enter = klikniecie; Spacja i skroty okna ida do okna (nigdy "klik")."""

    def keyPressEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        if _do_okna(self, zdarzenie):
            return
        if zdarzenie.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if not zdarzenie.isAutoRepeat() and self.isEnabled():
                self.click()
            zdarzenie.accept()
            return
        super().keyPressEvent(zdarzenie)

    def keyReleaseEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        if zdarzenie.key() == Qt.Key.Key_Space:
            zdarzenie.accept()
            return
        super().keyReleaseEvent(zdarzenie)

    def mousePressEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        _fokus_do_okna(self)
        super().mousePressEvent(zdarzenie)


def _przygotuj_przycisk(b: QPushButton, nazwa: str | None, rola: str | None, po_kliknieciu, wysokosc: int | None) -> QPushButton:
    b.setFocusPolicy(Qt.FocusPolicy.TabFocus)  # fokus tylko klawiszem Tab; Spacja = start skanu (``PrzyciskEkranu``)
    b.setAutoDefault(False)
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    if rola:
        b.setProperty("rola", rola)
    if nazwa:
        b.setObjectName(nazwa)
    if wysokosc:
        b.setMinimumHeight(wysokosc)
    if po_kliknieciu is not None:
        b.clicked.connect(lambda _=False: po_kliknieciu())
    return b


def przycisk(tekst: str, nazwa: str | None = None, rola: str | None = None, po_kliknieciu=None, wysokosc: int | None = None) -> QPushButton:
    """Przycisk ekranu; ``wysokosc`` - najmniejsza wysokosc (None: wysokosc z napisu i dopelnienia arkusza). Czesci okna uzywaja
    ``guzik`` (wysokosc wg roli z ``motyw.WYSOKOSCI``)."""
    return _przygotuj_przycisk(PrzyciskEkranu(tekst), nazwa, rola, po_kliknieciu, wysokosc)


def guzik(tekst: str, nazwa: str | None = None, rola: str | None = None, po_kliknieciu=None, wysokosc: int | None = None) -> QPushButton:
    """Przycisk nowego okna: jak ``przycisk``, z wysokoscia wg roli z ``motyw.WYSOKOSCI`` (arkusz wysokosci nie ustawia); przycisk
    paska stanu ma wysokosc stala, cyfra - najmniejsza szerokosc celu klikniecia."""
    b = przycisk(tekst, nazwa, rola, po_kliknieciu, wysokosc or motyw.WYSOKOSCI.get(rola, motyw.WYSOKOSC_PRZYCISKU))
    if rola in ("stan", "stan_blad"):
        b.setFixedHeight(motyw.WYSOKOSCI[rola])
    if rola == "cyfra":
        b.setMinimumWidth(motyw.SZEROKOSC_CYFRY)
    return b


class PrzyciskSkrotu(PrzyciskEkranu):
    """Przycisk z napisem po lewej i skrotem klawiszowym w ramce po prawej (SPEC p. 2). Napis przycisku (``text()``) zostaje
    pelny - "Ukruszona  [U]" jak w ``napisy`` i w instrukcjach; czesc w nawiasie kwadratowym jest rysowana jako ramka skrotu.
    ``barwa``: ``zwykly`` (napis jasny), ``status`` (napis na kolorze statusu), ``akcent`` (napis w kolorze akcentu), ``cichy``."""

    WZOR = re.compile(r"^(.*?)\s*\[([^\[\]]+)\]\s*$", re.S)

    def __init__(self, tekst: str, barwa: str = "zwykly", px: int = motyw.PX_PODSTAWOWY, pogrubiony: bool = False, dopelnienie: int = 14):
        super().__init__(tekst)
        self._barwa, self._px, self._pogrubiony = barwa, px, pogrubiony
        self.DOPELNIENIE = dopelnienie  # odstep napisu i ramki skrotu od krawedzi przycisku
        self.ODSTEP_SKROTU = min(12, dopelnienie)

    def czesci(self) -> tuple:
        """(napis, skrot) - skrot pusty, gdy napis nie ma czesci w nawiasie kwadratowym."""
        m = self.WZOR.match(self.text())
        return (" ".join(m.group(1).split()), m.group(2).strip()) if m else (" ".join(self.text().split()), "")

    def _miary(self) -> tuple:
        napis, skrot = self.czesci()
        fm = QFontMetrics(motyw.czcionka(self._px, self._pogrubiony))
        fs = QFontMetrics(motyw.czcionka(motyw.PX_POMOCNICZY))
        ramka = QSize(fs.horizontalAdvance(skrot) + 14, fs.height() + 4) if skrot else QSize(0, 0)
        return napis, skrot, fm, fs, ramka

    def sizeHint(self) -> QSize:  # noqa: N802 - nazwa Qt
        napis, skrot, fm, _, ramka = self._miary()
        szer = 2 * self.DOPELNIENIE + fm.horizontalAdvance(napis) + (self.ODSTEP_SKROTU + ramka.width() if skrot else 0)
        return QSize(szer, max(self.minimumHeight(), fm.height() + 12, ramka.height() + 8))

    def minimumSizeHint(self) -> QSize:  # noqa: N802 - nazwa Qt
        return self.sizeHint()

    def _kolory(self) -> tuple:
        """(kolor napisu, kolor ramki skrotu) wg barwy i stanu przycisku."""
        if not self.isEnabled():
            return motyw.TEKST_PRZYGASZONY, motyw.OBWODKA
        if self._barwa == "status":
            return motyw.NA_STATUSIE, motyw.NA_STATUSIE
        if self._barwa == "akcent":
            return motyw.AKCENT_TEKST, motyw.AKCENT
        if self._barwa == "cichy":
            return motyw.TEKST_POMOCNICZY, motyw.OBWODKA_MOCNA
        return motyw.TEKST, motyw.OBWODKA_SKROTU

    def paintEvent(self, _zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        p = QStylePainter(self)
        opcja = QStyleOptionButton()
        self.initStyleOption(opcja)
        opcja.text = ""
        opcja.icon = QIcon()
        p.drawControl(QStyle.ControlElement.CE_PushButton, opcja)  # tlo i obwodka z arkusza (takze stan: kursor, nacisniecie, fokus)
        napis, skrot, fm, fs, ramka = self._miary()
        kolor_napisu, kolor_ramki = self._kolory()
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        obszar = QRectF(self.rect()).adjusted(self.DOPELNIENIE, 0, -self.DOPELNIENIE, 0)
        if skrot:
            pole = QRectF(obszar.right() - ramka.width(), obszar.center().y() - ramka.height() / 2, ramka.width(), ramka.height())
            p.setPen(QPen(QColor(kolor_ramki), 1))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRoundedRect(pole.adjusted(0.5, 0.5, -0.5, -0.5), motyw.PROMIEN_ZNACZNIKA, motyw.PROMIEN_ZNACZNIKA)
            p.setFont(motyw.czcionka(motyw.PX_POMOCNICZY))
            p.setPen(QColor(kolor_napisu))
            p.drawText(pole, int(Qt.AlignmentFlag.AlignCenter), skrot)
            obszar.setRight(pole.left() - self.ODSTEP_SKROTU)
        p.setFont(motyw.czcionka(self._px, self._pogrubiony))
        p.setPen(QColor(kolor_napisu))
        wyrownanie = Qt.AlignmentFlag.AlignLeft if skrot else Qt.AlignmentFlag.AlignHCenter
        p.drawText(obszar, int(wyrownanie | Qt.AlignmentFlag.AlignVCenter), napis)
        p.end()


def przycisk_skrotu(tekst: str, nazwa: str | None = None, rola: str | None = None, po_kliknieciu=None, wysokosc: int | None = None,
                    barwa: str = "zwykly", px: int = motyw.PX_PODSTAWOWY, pogrubiony: bool = False, dopelnienie: int = 14) -> PrzyciskSkrotu:
    """Przycisk ze skrotem klawiszowym w ramce: ``tekst`` w postaci "Napis  [K]"."""
    return _przygotuj_przycisk(PrzyciskSkrotu(tekst, barwa, px, pogrubiony, dopelnienie), nazwa, rola, po_kliknieciu, wysokosc)


def ramka(rola: str = "kafelek", nazwa: str | None = None) -> QFrame:
    r = QFrame()
    r.setProperty("rola", rola)
    r.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    if nazwa:
        r.setObjectName(nazwa)
    return r


def przegroda() -> QFrame:
    """Pozioma linia 1 px miedzy czesciami kolumny."""
    r = QFrame()
    r.setProperty("rola", "przegroda")
    r.setFixedHeight(1)
    r.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    return r


def wyczysc(uklad) -> None:
    """Usuwa wszystko z ukladu od razu (widzety odlaczone od okna, zanim Qt je skasuje). Gdy fokus mial usuwany przycisk,
    fokus wraca do okna - nie przeskakuje na przycisk nowego panelu (Enter nie potwierdzi przypadkiem pytania)."""
    fokus = QApplication.focusWidget()
    while uklad.count():
        pozycja = uklad.takeAt(0)
        w = pozycja.widget()
        if w is not None:
            if fokus is not None and (w is fokus or w.isAncestorOf(fokus)):
                okno = w.window()
                if okno is not w:
                    okno.setFocus(Qt.FocusReason.OtherFocusReason)
                fokus = None
            w.setParent(None)
            w.deleteLater()
        elif pozycja.layout() is not None:
            wyczysc(pozycja.layout())


def _styl_znaczka(hex_: str, rozmiar_px: int) -> str:
    return motyw.styl_znacznika(hex_, rozmiar_px)


def znaczek(tekst: str, hex_: str, nazwa: str | None = None, rozmiar_px: int = motyw.PX_TRESC) -> QLabel:
    """Znacznik statusu: prostokat w kolorze ``hex_`` (kolor podaje wolajacy - ze stanu albo ze ``statusy``) z napisem."""
    e = etykieta(tekst, nazwa=nazwa)
    e.setAlignment(Qt.AlignmentFlag.AlignCenter)
    e.setStyleSheet(_styl_znaczka(hex_, rozmiar_px))
    return e


def styl_znaczka_poziomu(poziom: str, rozmiar_px: int = motyw.PX_POMOCNICZY) -> str:
    return motyw.styl_znaczka_poziomu(poziom, rozmiar_px)


def znaczek_poziomu(tekst: str, poziom: str, nazwa: str | None = None, rozmiar_px: int = motyw.PX_POMOCNICZY) -> QLabel:
    """Znaczek w barwach poziomu komunikatu - np. "plytka poranna - dopuszczona swiadomie"."""
    e = etykieta(tekst, nazwa=nazwa)
    e.setAlignment(Qt.AlignmentFlag.AlignCenter)
    e.setStyleSheet(styl_znaczka_poziomu(poziom, rozmiar_px))
    return e


class Kropka(QWidget):
    """Kropka statusu obok napisu (kafelek plytki, legenda, pasek stanu). Status nie jest rozpoznawalny tylko po barwie: obok
    kropki zawsze stoi napis, kropka statusu z ubytkiem ma jasna obwodke, puste gniazdo - obwodke przerywana bez wypelnienia."""

    def __init__(self, hex_: str | None, srednica: int = 9, obwodka: bool = False, pusta: bool = False, kwadrat: bool = False):
        super().__init__()
        self._hex, self._d, self._obwodka, self._pusta, self._kwadrat = hex_, srednica, obwodka, pusta, kwadrat
        self.setFixedSize(srednica + 4, srednica + 4)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def ustaw(self, hex_: str | None, pusta: bool = False) -> None:
        if (hex_, pusta) != (self._hex, self._pusta):
            self._hex, self._pusta = hex_, pusta
            self.update()

    def kolor(self) -> str | None:
        return self._hex

    def paintEvent(self, _zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        pole = QRectF(2, 2, self._d, self._d)
        if self._pusta or self._hex is None:
            pioro = QPen(QColor(motyw.OBWODKA_MOCNA if self._pusta else motyw.TEKST_POMOCNICZY), 1.5)
            if self._pusta:
                pioro.setStyle(Qt.PenStyle.DashLine)
            p.setPen(pioro)
            p.setBrush(Qt.BrushStyle.NoBrush)
            pole = pole.adjusted(0.75, 0.75, -0.75, -0.75)
        else:
            p.setPen(QPen(QColor(motyw.OBWODKA_UBYTKU), 1.5) if self._obwodka else Qt.PenStyle.NoPen)
            p.setBrush(QColor(self._hex))
            if self._obwodka:
                pole = pole.adjusted(-0.75, -0.75, 0.75, 0.75)
        if self._kwadrat:
            p.drawRect(pole)
        else:
            p.drawEllipse(pole)
        p.end()


class EtykietaSkracana(QLabel):
    """Napis jednej linii, ktory przy braku miejsca jest skracany z wielokropkiem (pelny napis w podpowiedzi). Tylko dla pol
    paska stanu, ktorych tresc bywa dluga (napis puli, kolejka, ramki); ``text()`` zwraca zawsze pelny napis."""

    def __init__(self, rola: str | None = None, nazwa: str | None = None):
        super().__init__()
        self._pelny = ""
        self._podpowiedz = ""
        self.setTextFormat(Qt.TextFormat.PlainText)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        if rola:
            self.setProperty("rola", rola)
        if nazwa:
            self.setObjectName(nazwa)

    def setText(self, tekst: str) -> None:  # noqa: N802 - nazwa Qt
        if tekst != self._pelny:
            self._pelny = tekst
            self.updateGeometry()
        self._dopasuj()

    def text(self) -> str:
        return self._pelny

    def setToolTip(self, tekst: str) -> None:  # noqa: N802 - nazwa Qt
        self._podpowiedz = tekst
        self._dopasuj()

    def skrocona(self) -> bool:
        return QLabel.text(self) != self._pelny

    def _potrzebna(self) -> int:
        m = self.contentsMargins()
        return self.fontMetrics().horizontalAdvance(self._pelny) + m.left() + m.right() + 2 * self.margin() + 12  # 12: dopelnienie z arkusza

    def sizeHint(self) -> QSize:  # noqa: N802 - nazwa Qt
        return QSize(self._potrzebna(), super().sizeHint().height())

    def minimumSizeHint(self) -> QSize:  # noqa: N802 - nazwa Qt
        return QSize(min(48, self._potrzebna()), super().minimumSizeHint().height())

    def _dopasuj(self) -> None:
        if self._potrzebna() <= self.width():
            pokazany = self._pelny
        else:
            pokazany = self.fontMetrics().elidedText(self._pelny, Qt.TextElideMode.ElideRight, max(8, self.width() - 12))
        if pokazany != QLabel.text(self):
            QLabel.setText(self, pokazany)
        podpowiedz = "\n".join(t for t in ((self._pelny if pokazany != self._pelny else ""), self._podpowiedz) if t)
        if podpowiedz != QLabel.toolTip(self):
            QLabel.setToolTip(self, podpowiedz)

    def resizeEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        super().resizeEvent(zdarzenie)
        self._dopasuj()

    def changeEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        super().changeEvent(zdarzenie)
        if zdarzenie.type() in (QEvent.Type.FontChange, QEvent.Type.StyleChange):  # czcionka z arkusza: szerokosc napisu od nowa
            self.updateGeometry()
            self._dopasuj()


def godzina(czas_iso: str | None) -> str:
    """``2026-11-17T19:05:00`` -> ``19:05``; pusty napis, gdy czasu nie ma."""
    return czas_iso[11:16] if czas_iso and len(czas_iso) >= 16 else ""


def dzien(doba_iso: str | None, rok: bool = False) -> str:
    """``2026-11-17`` -> ``17.11`` (albo ``17.11.2026``)."""
    if not doba_iso or len(doba_iso) < 10:
        return doba_iso or ""
    return f"{doba_iso[8:10]}.{doba_iso[5:7]}" + (f".{doba_iso[0:4]}" if rok else "")


def liczba_mm(wartosc: float) -> str:
    return f"{wartosc:.2f}".replace(".", ",")


def nazwa_obiektu(przedrostek: str, rodzaj) -> str:
    """Nazwa obiektu Qt z rodzaju pytania / komunikatu ze stanu (rodzaj nieznany tej wersji ekranu tez daje poprawna nazwe)."""
    return przedrostek + "_" + "".join(z if z.isascii() and (z.isalnum() or z == "_") else "_" for z in str(rodzaj))


def nazwa_plytki(numer) -> str:
    return N.PLYTKA_NR.format(numer=numer) if numer is not None else N.PLYTKA_BEZ_NUMERU


def do_obejrzenia(plytka) -> list:
    """Prace plytki, ktore technik ma jeszcze obejrzec: bez decyzji, z dozwolona decyzja i w klasie koloru innej niz zielona
    (czerwone, zolte, szare, pomaranczowe, nieznane - klasa ``Praca.kolor`` ze stanu). Prace bez koloru (plytka bez numeru:
    zielone czekaja na numer) sie nie licza. Uzywaja tego: napis stanu plytki, "Nastepna" (N) i regula przelaczania ekranu
    na nowa plytke (A-P2)."""
    if plytka is None:
        return []
    return [p for p in plytka.prace
            if p.decyzja is None and "ukruszona" in p.dozwolone and p.kolor is not None and p.kolor not in (ST.KOLOR_ZIELONY, ST.KOLOR_ZATWIERDZONA_OK)]


def czeka_na_odpowiedz_o_ponowny_skan(plytka) -> bool:
    """Plytka ma otwarte pytanie "Ponowny skan tej samej plytki?" (to ONA jest nowym skanem; pytanie zamkniete - nie)."""
    return plytka is not None and any(q.rodzaj == "ponowny_skan" and not q.ukryte for q in plytka.pytania)


def stan_obejrzenia(plytka) -> str:
    """Napis stanu plytki na ekranie (A-P5 poz. 1). Skan przyjety ma w ``statusy`` napis "przeanalizowana"; ekran mowi
    dokladniej: "do obejrzenia: n", dopoki sa prace do obejrzenia, a "sprawdzona" dopiero, gdy wszystkie czerwone i zolte
    maja decyzje (i plytka ma numer). Kazdy inny napis ze stanu (inny status skanu, napis nieznany tej wersji ekranu) -
    bez zmian."""
    if plytka is None:
        return ""
    if czeka_na_odpowiedz_o_ponowny_skan(plytka):
        return N.PLYTKA_NOWY_SKAN  # E3-P14 (poz. 8): do odpowiedzi nowy skan nie jest "sprawdzony" (ani "do obejrzenia")
    if not plytka.aktywna or plytka.napis != ST.napis_plytki(SKAN_PRZYJETY):
        return plytka.napis
    n = len(do_obejrzenia(plytka))
    if n:
        return N.PLYTKA_DO_OBEJRZENIA.format(n=n)
    if plytka.numer is None or not any(p.dozwolone for p in plytka.prace):
        return plytka.napis  # bez numeru zielone nie sa potwierdzone; bez decyzji (np. inny tryb) - napis ze stanu
    return N.PLYTKA_SPRAWDZONA


def napis_dopuszczenia(plytka) -> str:
    """Staly znacznik plytki dopuszczonej swiadomie (plytka poranna wieczorem): "plytka poranna - dopuszczona swiadomie"."""
    if plytka is None or not plytka.dopuszczona:
        return ""
    return N.PLYTKA_DOPUSZCZONA.format(jaka=ST.JAKA_PLYTKA.get(plytka.typ, ST.JAKA_PLYTKA[None]))


def tabela(nazwa: str, kolumny: tuple, wiersz: int, naglowek: int) -> QTableWidget:
    """Tabela okna: bez kratki, wiersze oddzielone linia, naglowek przygaszony, zaznaczanie calych wierszy, bez fokusu."""
    t = QTableWidget(0, len(kolumny))
    t.setObjectName(nazwa)
    t.setHorizontalHeaderLabels(list(kolumny))
    t.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    t.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    t.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    t.setShowGrid(False)
    t.setFrameShape(QFrame.Shape.NoFrame)
    t.verticalHeader().setVisible(False)
    t.verticalHeader().setDefaultSectionSize(wiersz)
    t.verticalHeader().setMinimumSectionSize(wiersz)
    t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    t.horizontalHeader().setSectionsClickable(False)
    t.horizontalHeader().setHighlightSections(False)
    t.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    t.horizontalHeader().setFixedHeight(naglowek)
    t.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    return t


# ----------------------------------------------------------------------------
# uklady
# ----------------------------------------------------------------------------
class UkladPlynny(QLayout):
    """Elementy w wierszu od lewej; gdy brakuje szerokosci - nastepny wiersz. Element nigdy nie jest zwezany ponizej
    ``sizeHint`` (napis przycisku nie jest ucinany); wysokosc zalezy od szerokosci (``heightForWidth``)."""

    def __init__(self, rodzic=None, odstep_poziomy: int = 8, odstep_pionowy: int = 6):
        super().__init__(rodzic)
        self._elementy: list = []
        self._poziomy, self._pionowy = odstep_poziomy, odstep_pionowy
        self.setContentsMargins(0, 0, 0, 0)

    def ustaw_odstepy(self, poziomy: int, pionowy: int) -> None:
        self._poziomy, self._pionowy = poziomy, pionowy
        self.invalidate()

    def addItem(self, element) -> None:  # noqa: N802 - nazwa Qt
        self._elementy.append(element)

    def count(self) -> int:
        return len(self._elementy)

    def itemAt(self, i: int):  # noqa: N802 - nazwa Qt
        return self._elementy[i] if 0 <= i < len(self._elementy) else None

    def takeAt(self, i: int):  # noqa: N802 - nazwa Qt
        return self._elementy.pop(i) if 0 <= i < len(self._elementy) else None

    def expandingDirections(self):  # noqa: N802 - nazwa Qt
        return Qt.Orientation.Horizontal

    def hasHeightForWidth(self) -> bool:  # noqa: N802 - nazwa Qt
        return True

    def heightForWidth(self, szerokosc: int) -> int:  # noqa: N802 - nazwa Qt
        return self._uloz(QRect(0, 0, szerokosc, 0), test=True)

    def setGeometry(self, prostokat) -> None:  # noqa: N802 - nazwa Qt
        super().setGeometry(prostokat)
        zapas = prostokat.height() - self._uloz(prostokat, test=True)
        self._uloz(prostokat.translated(0, zapas // 2) if zapas > 1 else prostokat, test=False)  # wiersze wysrodkowane w pionie

    def _widoczne(self) -> list:
        return [e for e in self._elementy if not e.isEmpty()]

    def sizeHint(self) -> QSize:  # noqa: N802 - nazwa Qt
        m = self.contentsMargins()
        widoczne = self._widoczne()
        if not widoczne:
            return QSize(m.left() + m.right(), m.top() + m.bottom())
        szer = sum(e.sizeHint().width() for e in widoczne) + self._poziomy * (len(widoczne) - 1)
        wys = max(e.sizeHint().height() for e in widoczne)
        return QSize(szer + m.left() + m.right(), wys + m.top() + m.bottom())

    def minimumSize(self) -> QSize:  # noqa: N802 - nazwa Qt
        m = self.contentsMargins()
        widoczne = self._widoczne()
        if not widoczne:
            return QSize(m.left() + m.right(), m.top() + m.bottom())
        return QSize(max(e.sizeHint().width() for e in widoczne) + m.left() + m.right(),
                     max(e.sizeHint().height() for e in widoczne) + m.top() + m.bottom())

    def _uloz(self, prostokat, test: bool) -> int:
        m = self.contentsMargins()
        obszar = prostokat.adjusted(m.left(), m.top(), -m.right(), -m.bottom())
        widoczne = self._widoczne()
        if not widoczne:
            return m.top() + m.bottom()
        x, y, wys_wiersza, wiersz = obszar.x(), obszar.y(), 0, []

        def rozmiesc() -> None:
            for element, x0, hint in wiersz:
                element.setGeometry(QRect(QPoint(x0, y + (wys_wiersza - hint.height()) // 2), hint))

        for element in widoczne:
            hint = element.sizeHint()
            if wiersz and x + hint.width() > obszar.x() + obszar.width():
                if not test:
                    rozmiesc()
                y += wys_wiersza + self._pionowy
                x, wys_wiersza, wiersz = obszar.x(), 0, []
            wiersz.append((element, x, hint))
            x += hint.width() + self._poziomy
            wys_wiersza = max(wys_wiersza, hint.height())
        if not test:
            rozmiesc()
        return y + wys_wiersza - prostokat.y() + m.bottom()


class ObszarPaneli(QScrollArea):
    """Panele (pytania, komunikaty) jeden pod drugim. Wysokosc = suma paneli, gdy jest miejsce; gdy brakuje - najmniej
    ``widocznych_min`` pierwszych paneli w calosci, reszta jest przewijana (nic nie jest uciete). Pusty obszar jest ukryty.
    Uzywa go lista bledow programu."""

    def __init__(self, nazwa: str, widocznych_min: int = 1, odstep: int = 6):
        super().__init__()
        self.setObjectName(nazwa)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.wnetrze = QWidget()
        self.wnetrze.setObjectName(f"{nazwa}_wnetrze")
        # arkusz z selektorem: arkusz bez selektora przeszedlby na wszystkie panele i przyciski
        self.wnetrze.setStyleSheet(f"QWidget#{nazwa}_wnetrze {{ background: transparent; }}")
        self.uklad = QVBoxLayout(self.wnetrze)
        self.uklad.setContentsMargins(0, 0, 0, 0)
        self.uklad.setSpacing(odstep)
        self.setWidget(self.wnetrze)
        self._widocznych_min = widocznych_min
        self._limit_minimum: int | None = None
        self._szerokosc = 0
        self._szerokosc_paneli = 0  # szerokosc obszaru widoku (bez paska przewijania pionowego)

    def ustaw_limit_minimum(self, piksele: int | None) -> None:
        """Najwyzej tyle pikseli obszar zajmuje "na pewno" (minimum ukladu); reszta paneli jest wtedy przewijana."""
        if piksele != self._limit_minimum:
            self._limit_minimum = piksele
            self.updateGeometry()

    def panele(self) -> list:
        """Wszystkie panele obszaru (takze dopiero dodane - Qt pokazuje je w nastepnym obiegu petli)."""
        return [self.uklad.itemAt(i).widget() for i in range(self.uklad.count()) if self.uklad.itemAt(i).widget() is not None]

    def wysokosc_paneli(self, szerokosc: int, ile: int | None = None) -> int:
        """Wysokosc ``ile`` pierwszych paneli (wszystkich) ulozonych w szerokosci ``szerokosc``."""
        panele = self.panele()
        if ile is not None:
            panele = panele[:ile]
        if not panele:
            return 0
        wys = [p.heightForWidth(szerokosc) if p.hasHeightForWidth() else p.sizeHint().height() for p in panele]
        return sum(max(h, p.minimumSizeHint().height()) for h, p in zip(wys, panele)) + self.uklad.spacing() * (len(panele) - 1)

    def _wysokosc(self, ile: int | None = None) -> int:
        # szerokosc, ktora panele naprawde maja: przy widocznym pasku przewijania pionowego - wezsza (E3-A1p: liczona dla pelnej
        # szerokosci wysokosc byla za mala, tekst zawijal sie w dodatkowy wiersz i obszar zostawal przyciety z paskiem przewijania)
        return self.wysokosc_paneli(max(120, self.viewport().width() if self.verticalScrollBar().isVisible() else self.width()), ile)

    def sizeHint(self) -> QSize:  # noqa: N802 - nazwa Qt
        return QSize(super().sizeHint().width(), self._wysokosc())

    def minimumSizeHint(self) -> QSize:  # noqa: N802 - nazwa Qt
        wys = self._wysokosc(self._widocznych_min)
        return QSize(0, wys if self._limit_minimum is None else min(wys, self._limit_minimum))

    def odswiez(self) -> None:
        """Po wymianie paneli: widocznosc i wysokosc obszaru."""
        self.setVisible(bool(self.panele()))
        self.updateGeometry()

    def resizeEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        super().resizeEvent(zdarzenie)
        if self.width() != self._szerokosc:  # wysokosc paneli zalezy od szerokosci (zawijany tekst, przyciski w wierszach)
            self._szerokosc = self.width()
            self.updateGeometry()

    def viewportEvent(self, zdarzenie) -> bool:  # noqa: N802 - nazwa Qt
        """Pasek przewijania pionowego pojawil sie albo zniknal (zmienila sie szerokosc paneli, a nie obszaru): wysokosc od nowa."""
        wynik = super().viewportEvent(zdarzenie)
        if zdarzenie.type() == QEvent.Type.Resize and self.viewport().width() != getattr(self, "_szerokosc_paneli", None):
            self._szerokosc_paneli = self.viewport().width()
            self.updateGeometry()
        return wynik


# ----------------------------------------------------------------------------
# pytania i komunikaty: opis (``Uwaga``) i panel
# ----------------------------------------------------------------------------
@dataclasses.dataclass(frozen=True)
class Uwaga:
    """Jedno pytanie albo komunikat do pokazania: nazwa obiektu Qt, poziom, tytul, tekst, opcjonalnie rada, ostrzezenie
    i wyjasnienie, przyciski - krotki (nazwa obiektu, napis, polecenie, argumenty, aktywny, rola). ``klucz`` - tozsamosc
    pozycji (rodzaj i identyfikatory ze stanu): po nim strefa poznaje, ze pod kursorem stoi juz INNE pytanie (ochrona 800 ms)."""

    nazwa: str
    poziom: str
    tytul: str
    tekst: str = ""
    przyciski: tuple = ()
    rada: str = ""
    ostrzezenie: str = ""
    wyjasnienie: str = ""
    pod_tekstem: bool = False
    klucz: tuple = ()


def tytul_plytki(nazwa_plytki_: str, tytul: str) -> str:
    return N.UWAGA_PLYTKI.format(plytka=nazwa_plytki_, tytul=tytul) if nazwa_plytki_ else tytul


def tytul_ze_skanem(tytul: str, czas: str) -> str:
    """S3-3: tytul panelu plytki bez numeru wskazuje skan godzina ("Podaj numer plytki - skan z 19:05")."""
    return N.TYTUL_ZE_SKANEM.format(tytul=tytul, godzina=czas) if czas else tytul


def uwaga_pytania(pytanie, stan, typ_plytki: str | None, plytka: str = "", czas: str = "") -> Uwaga:
    """Pytanie ze stanu: przyciski z ``pytanie.odpowiedzi``; polecenia wymagajace osoby nieaktywne bez niej (z wyjasnieniem).
    ``plytka`` - nazwa plytki do tytulu ("Plytka 2: ..."); bez niej (plytka bez numeru) tytul wskazuje skan godzina ``czas``."""
    jest_osoba = stan.operator is not None
    przyciski, wymaga = [], False
    glowna = GLOWNE_ODPOWIEDZI.get(pytanie.rodzaj)
    for odp in pytanie.odpowiedzi:
        potrzebuje_osoby = odp.polecenie not in BEZ_OSOBY
        wymaga = wymaga or potrzebuje_osoby
        cyfra = odp.polecenie == "podaj_numer_plytki" and len(odp.argumenty) == 2  # (skan, numer); rano "mimo to" - zwykly przycisk
        nazwa = nazwa_obiektu("odp", odp.polecenie) + (f"_{odp.argumenty[-1]}" if cyfra else "")
        rola = "cyfra" if cyfra else ("glowny" if odp.polecenie == glowna else "wglebiony")
        przyciski.append((nazwa, odp.napis, odp.polecenie, tuple(odp.argumenty), jest_osoba or not potrzebuje_osoby, rola))
    tekst, ostrzezenie, rada = pytanie.tekst, "", ""
    if pytanie.rodzaj == "ponowny_skan" and pytanie.liczba_decyzji:
        skutek = ST.SKUTEK_Z_DECYZJAMI.format(n=pytanie.liczba_decyzji, u=pytanie.liczba_ukruszonych,
                                              decyzji=ST.odmiana(pytanie.liczba_decyzji, "decyzja", "decyzje", "decyzji"))
        if tekst.endswith(skutek):  # ostrzezenie o decyzjach, ktore przepadna, jako osobny wyrozniony napis
            tekst, ostrzezenie = tekst[:-len(skutek)].rstrip(), skutek
    if pytanie.rodzaj == "plytka_nie_z_trybu":
        rada = {"poranna": N.RADA_PLYTKA_PORANNA, "wieczorna": N.RADA_PLYTKA_WIECZORNA}.get(typ_plytki, N.RADA_PLYTKA_NIEZNANA)
    wyjasnienie = ""
    if wymaga and not jest_osoba:
        wyjasnienie = ST.tekst_komunikatu("brak_operatora" if stan.operatorzy else "pusta_lista_operatorow")[2]
    tytul = tytul_plytki(plytka, pytanie.tytul) if plytka else tytul_ze_skanem(pytanie.tytul, czas)
    return Uwaga(nazwa_obiektu("pytanie", pytanie.rodzaj), POZIOM_PYTANIA, tytul, tekst, tuple(przyciski), rada=rada,
                 ostrzezenie=ostrzezenie, wyjasnienie=wyjasnienie, pod_tekstem=len(przyciski) > 2,
                 klucz=("pytanie", pytanie.id, pytanie.skan_id))


def uwaga_numeru(skan_id: int, numery: tuple, obecny, jest_osoba: bool, wyjasnienie: str, plytka: str = "", czas: str = "") -> Uwaga:
    """Reczne podanie albo poprawienie numeru plytki (polecenie ``podaj_numer_plytki`` z ``Plytka.dozwolone``). Plytka bez
    numeru: tytul "Podaj numer plytki - skan z GG:MM" (S3-3: wiadomo, ktorego skanu dotyczy); z numerem: "Plytka n: zmien numer
    plytki". Przyciski niosa ``skan_id`` tej plytki."""
    przyciski = [(f"odp_podaj_numer_plytki_{n}", str(n), "podaj_numer_plytki", (skan_id, n), jest_osoba and n != obecny, "cyfra") for n in numery]
    przyciski.append(("numer_bez_zmian", N.ZOSTAW_OSOBE, LOKALNE_NUMER_BEZ_ZMIAN, (), True, "lacze"))
    tytul = tytul_ze_skanem(ST.PRZYCISKI["podaj_numer_plytki"], czas) if obecny is None else tytul_plytki(plytka, N.ZMIEN_NUMER_TYTUL)
    return Uwaga("panel_numer_plytki", "info", tytul, N.NUMER_PLYTKI_TEKST, tuple(przyciski), wyjasnienie="" if jest_osoba else wyjasnienie,
                 pod_tekstem=True, klucz=("numer", skan_id))


def uwaga_odmowy(tekst: str) -> Uwaga:
    """Odmowa polecenia, ktorej nie ma w komunikatach stanu (np. ``zle_argumenty``): tekst odpowiedzi kontrolera."""
    return Uwaga("komunikat_odpowiedz", ST.KOMUNIKATY["odmowa"].poziom, ST.KOMUNIKATY["odmowa"].tytul, tekst,
                 (("zamknij_odpowiedz", ST.PRZYCISKI["zamknij_komunikat"], LOKALNE_ZAMKNIJ_ODPOWIEDZ, (), True, "lacze"),),
                 klucz=("odmowa", tekst))


def uwaga_informacji(tekst: str) -> Uwaga:
    """Informacja samego ekranu (np. widok pracy zamkniety, bo pracy nie ma juz w stanie) - nie komunikat kontrolera."""
    return Uwaga("informacja_ekranu", "info", N.INFORMACJA, tekst,
                 (("zamknij_informacje", ST.PRZYCISKI["zamknij_komunikat"], LOKALNE_ZAMKNIJ_INFORMACJE, (), True, "lacze"),),
                 klucz=("informacja", tekst))


def uwaga_komunikatu(komunikaty: tuple, plytka: str = "", dodatek: str = "") -> Uwaga:
    """Komunikat ze stanu; ``komunikaty`` - jeden albo kilka jednakowych (ten sam rodzaj i tekst: jedna pozycja z licznikiem,
    "Zamknij" zamyka wszystkie). ``dodatek`` - dopisek ekranu ze stanu (np. gniazda konfliktu projektu)."""
    komunikat = komunikaty[0]
    przyciski = []
    if komunikat.rodzaj in ("pula_pusta", "pula_brak_folderu"):
        przyciski.append(("komunikat_odswiez_pule", ST.PRZYCISKI["odswiez_pule"], "odswiez_pule", (), True, "wglebiony"))
    if komunikat.rodzaj in ST.NAPISY_NIEZAPISANE:  # blad zapisu wynikow / baza zajeta: zapis mozna ponowic od razu
        przyciski.append(("komunikat_ponow_zapis", ST.PRZYCISKI["ponow_zapis"], "ponow_zapis", (), True, "wglebiony"))
    if komunikat.rodzaj == "lista_nie_zapisana":
        przyciski.append(("komunikat_zapisz_liste", ST.PRZYCISKI["zapisz_liste"], "zapisz_liste", (), True, "wglebiony"))
    zamknij = ST.PRZYCISKI["zamknij_komunikat"]
    if komunikat.rodzaj in ST.KOMUNIKATY_DO_PONOWIENIA:  # E3-P14 (N1): polecenie odrzucone przy zajetej bazie - ponowienie TEGO polecenia
        przyciski.append(("komunikat_ponow_polecenie", ST.PRZYCISKI["ponow_polecenie"], "ponow_polecenie", (komunikat.id,), True, "glowny"))
        zamknij = ST.PRZYCISK_REZYGNUJE  # zamkniecie = swiadoma rezygnacja z tej decyzji
    przyciski.append(("zamknij_komunikat", zamknij, "zamknij_komunikat", tuple(k.id for k in komunikaty), True, "lacze"))
    tytul = tytul_plytki(plytka, komunikat.tytul)
    if len(komunikaty) > 1:
        tytul = N.KILKA_RAZY.format(tytul=tytul, n=len(komunikaty))
    return Uwaga(nazwa_obiektu("komunikat", komunikat.rodzaj), komunikat.poziom, tytul, komunikat.tekst, tuple(przyciski),
                 wyjasnienie=dodatek, klucz=("komunikat",) + tuple(k.id for k in komunikaty))


def sprawy_nowych_plytek(stan, nowe: list) -> tuple:
    """E3-P14 (N2): dla plytek, na ktore ekran sie nie przelaczyl - ((nazwa plytki, godzina skanu, (tytuly otwartych pytan),
    (tytuly otwartych komunikatow)), ...) w kolejnosci skanow. Tylko czytanie stanu (``stan.pytania`` / ``stan.komunikaty``)."""
    wynik = []
    for p in nowe:
        pytania = tuple(q.tytul for q in stan.pytania if not q.ukryte and q.skan_id == p.skan_id)
        komunikaty = tuple(dict.fromkeys(k.tytul for k in stan.komunikaty if not k.ukryte and k.skan_id == p.skan_id))
        wynik.append((nazwa_plytki(p.numer), godzina(p.czas), pytania, komunikaty))
    return tuple(wynik)


def uwaga_nowego_wyniku(sprawy: tuple) -> Uwaga:
    """E3-P14 (N2): trwala informacja "Nowy wynik czeka: Plytka n" - wynik nowej plytki przyszedl, a ekran zostal na ogladanej
    (regula A-P2). Wymienia pytania i komunikaty czekajacych plytek; poziom "ostrzezenie", gdy jest o co pytac, inaczej "info".
    Stoi w kolumnie plytek pod przyciskiem "Pokaz nowy wynik" - jej pojawienie sie nie rusza mapy. Bez "Zamknij"."""
    nazwy = ", ".join(dict.fromkeys(s[0] for s in sprawy))
    tytul = N.NOWY_WYNIK_TYTUL.format(plytki=nazwy) if len(sprawy) == 1 else N.NOWE_WYNIKI_TYTUL.format(n=len(sprawy), plytki=nazwy)
    wiersze = []
    for nazwa, czas, pytania, komunikaty in sprawy:
        czesci = [N.NOWY_WYNIK_PYTANIE.format(tytul=t) for t in pytania] + [N.NOWY_WYNIK_KOMUNIKAT.format(tytul=t) for t in komunikaty]
        if czesci:
            wiersze.append(N.NOWY_WYNIK_SPRAWY.format(plytka=nazwa, godzina=czas or N.BRAK_DANYCH, sprawy=", ".join(czesci)))
    return Uwaga("panel_nowy_wynik", "ostrzezenie" if wiersze else "info", tytul, N.NOWY_WYNIK_RADA, (), rada=" ".join(wiersze),
                 pod_tekstem=True, klucz=("nowy_wynik",) + sprawy)


class PanelUwagi(QFrame):
    """Jedno pytanie albo komunikat: tytul, tekst, opcjonalnie rada, ostrzezenie i wyjasnienie, przyciski. Klikniecie przycisku
    = sygnal ``polecenie(nazwa, argumenty)``. Przyciski stoja obok tekstu (do dwoch - jeden pod drugim) albo pod nim.
    ``przewijany`` (strefa o stalej wysokosci): napisy sa w obszarze przewijanym - panel miesci sie w kazdej wysokosci,
    przyciski zostaja widoczne, nic nie jest uciete bez paska przewijania. ``licznik`` - (napis, funkcja): przycisk w wierszu
    tytulu ("i jeszcze n"); ``ciasny`` - uklad zwarty okna (mniejsze odstepy)."""

    polecenie = Signal(str, tuple)

    def __init__(self, nazwa: str, poziom: str, tytul: str, tekst: str, przyciski, *, rada: str = "", ostrzezenie: str = "",
                 wyjasnienie: str = "", przyciski_pod_tekstem: bool = False, waski: bool = False, przewijany: bool = False,
                 licznik: tuple | None = None, wysokosc_przycisku: int | None = None, ciasny: bool = False):
        super().__init__()
        self.setObjectName(nazwa)
        self.setProperty("rola", "uwaga_panel")
        self.setProperty("poziom", poziom if poziom in motyw.POZIOMY else motyw.POZIOM_DOMYSLNY)
        zwarty = ciasny  # strefa pytan w ukladzie zwartym okna
        if wysokosc_przycisku is None:
            wysokosc_przycisku = motyw.WYSOKOSC_PRZYCISKU
        uklad = QHBoxLayout(self)
        uklad.setContentsMargins(*((8, 6, 8, 6) if waski else (12, 6, 12, 6) if zwarty else (14, 10, 14, 10)))
        uklad.setSpacing(12 if zwarty else 16)
        kolumna = QVBoxLayout()
        kolumna.setContentsMargins(0, 0, 0, 0)
        kolumna.setSpacing(4)
        naglowek = QHBoxLayout()
        naglowek.setSpacing(8)
        naglowek.addWidget(etykieta(tytul, "naglowek", zawijaj=True), 1)
        if licznik is not None:
            self.przycisk_licznika = guzik(licznik[0], "uwagi_jeszcze", "lacze", licznik[1], 26)
            self.przycisk_licznika.setToolTip(N.JESZCZE_OPIS)
            naglowek.addWidget(self.przycisk_licznika, 0, Qt.AlignmentFlag.AlignTop)
        kolumna.addLayout(naglowek)
        napisy = QVBoxLayout()
        napisy.setContentsMargins(0, 0, 0, 0)
        napisy.setSpacing(2 if zwarty else 4)
        if rada:
            napisy.addWidget(etykieta(rada, "tresc_glowna", zawijaj=True))
        if tekst:
            napisy.addWidget(etykieta(tekst, "tresc", zawijaj=True))
        if ostrzezenie:
            napisy.addWidget(etykieta(ostrzezenie, "uwaga", "pytanie_ostrzezenie", zawijaj=True))
        if wyjasnienie:
            napisy.addWidget(etykieta(wyjasnienie, "tresc", zawijaj=True))
        if przewijany:
            wnetrze = QWidget()
            wnetrze.setObjectName("uwaga_napisy")
            wnetrze.setStyleSheet("QWidget#uwaga_napisy { background: transparent; }")
            napisy.addStretch(1)
            wnetrze.setLayout(napisy)
            self.przewijanie = QScrollArea()
            self.przewijanie.setObjectName("uwaga_przewijanie")
            self.przewijanie.setWidgetResizable(True)
            self.przewijanie.setFrameShape(QFrame.Shape.NoFrame)
            self.przewijanie.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.przewijanie.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.przewijanie.setWidget(wnetrze)
            self.przewijanie.viewport().setAutoFillBackground(False)
            kolumna.addWidget(self.przewijanie, 1)
        else:
            self.przewijanie = None
            kolumna.addLayout(napisy)
        uklad.addLayout(kolumna, 1)
        self.przyciski: list = []
        if not przyciski:
            return
        pod_tekstem = przyciski_pod_tekstem or len(przyciski) > 2
        if pod_tekstem or not przewijany:
            miejsce = UkladPlynny(odstep_poziomy=8, odstep_pionowy=4 if zwarty else 6)
        else:
            miejsce = QVBoxLayout()  # strefa: do dwoch przyciskow jeden pod drugim po prawej stronie
            miejsce.setSpacing(8)
            miejsce.addStretch(1)
        for nazwa_b, napis, nazwa_polecenia, argumenty, aktywny, rola in przyciski:
            wyslij = lambda p=nazwa_polecenia, a=tuple(argumenty): self.polecenie.emit(p, a)  # noqa: E731
            b = guzik(napis, nazwa_b, rola, wyslij)  # wysokosc wg roli z ``motyw.WYSOKOSCI``
            b.setEnabled(aktywny)
            if rola not in ("cyfra", "lacze"):
                b.setMinimumHeight(wysokosc_przycisku)
            miejsce.addWidget(b)
            self.przyciski.append(b)
        if isinstance(miejsce, QVBoxLayout):
            miejsce.addStretch(1)
        if pod_tekstem:
            kolumna.addLayout(miejsce)
        else:
            uklad.addLayout(miejsce)

    @classmethod
    def z_uwagi(cls, u: Uwaga, **parametry) -> "PanelUwagi":
        return cls(u.nazwa, u.poziom, u.tytul, u.tekst, u.przyciski, rada=u.rada, ostrzezenie=u.ostrzezenie, wyjasnienie=u.wyjasnienie,
                   przyciski_pod_tekstem=u.pod_tekstem, **parametry)


class Zaslona(QWidget):
    """Polprzezroczysta warstwa nad czescia ekranu na czas ochrony (800 ms po zmianie zawartosci): przygasza ja i zabiera
    klikniecia myszy, zeby klikniecie wycelowane w poprzednia tresc nie trafilo w nowa."""

    def __init__(self, rodzic: QWidget, alfa: int = 150):
        super().__init__(rodzic)
        self._alfa = alfa
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.hide()

    def paintEvent(self, _zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        p = QPainter(self)
        kolor = QColor(motyw.TLO)
        kolor.setAlpha(self._alfa)
        p.fillRect(self.rect(), kolor)
        p.end()

    def mousePressEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        _fokus_do_okna(self)
        zdarzenie.accept()

    def mouseReleaseEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        zdarzenie.accept()

    def mouseDoubleClickEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        zdarzenie.accept()


class StrefaKomunikatow(QFrame):
    """Strefa pytan i komunikatow nad mapa: STALA wysokosc (``Uklad.strefa``), jedna pozycja naraz, reszta w liczniku
    "i jeszcze n" (klikniecie licznika pokazuje nastepna). Mapa pod strefa nigdy sie nie przesuwa, bez wzgledu na to, co
    i ile przychodzi. ``chron(True)`` - na czas ochrony przyciski strefy nie przyjmuja klikniec, a strefa jest przygaszona
    (S3-3: pytanie, ktore zmienilo sie pod reka technika)."""

    polecenie = Signal(str, tuple)
    nastepna = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("strefa_komunikatow")
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._uklad = QVBoxLayout(self)
        self._uklad.setSpacing(0)
        self._miejsce = QVBoxLayout()
        self._miejsce.setContentsMargins(0, 0, 0, 0)
        self._uklad.addLayout(self._miejsce, 1)
        self._pusta = etykieta(N.STREFA_PUSTA, "przygaszony", "strefa_pusta")
        self._uklad.addWidget(self._pusta, 0, Qt.AlignmentFlag.AlignVCenter)
        self._zaslona = Zaslona(self)
        self._sygnatura = None
        self._uwaga: Uwaga | None = None
        self._panel: PanelUwagi | None = None
        self._chroniona = False
        self._wysokosc_przycisku = motyw.CEL_KLIKNIECIA
        self._ciasny = False
        self.ustaw_uklad(motyw.UKLAD_WYSOKI)

    def ustaw_uklad(self, u: motyw.Uklad) -> None:
        self.setFixedHeight(u.strefa)
        pion = 6 if u.zwarty else 12
        self._uklad.setContentsMargins(u.bok, pion, u.bok, pion)
        self._wysokosc_przycisku = 40 if u.zwarty else motyw.CEL_KLIKNIECIA
        self._ciasny = u.zwarty
        self._sygnatura = None

    def ustaw(self, uwaga: Uwaga | None, jeszcze: int = 0) -> None:
        """Pokazuje ``uwaga`` (None = strefa pusta); ``jeszcze`` - ile dalszych pozycji czeka za nia."""
        sygnatura = (uwaga, jeszcze, self._wysokosc_przycisku, self._ciasny)
        if sygnatura == self._sygnatura:
            return
        self._sygnatura = sygnatura
        self._uwaga = uwaga
        wyczysc(self._miejsce)
        self._panel = None
        if uwaga is not None:
            licznik = (N.JESZCZE_KROTKO.format(n=jeszcze), self.nastepna.emit) if jeszcze > 0 else None
            self._panel = PanelUwagi.z_uwagi(uwaga, przewijany=True, licznik=licznik, wysokosc_przycisku=self._wysokosc_przycisku,
                                             ciasny=self._ciasny)
            self._panel.polecenie.connect(self._wyslij)
            self._miejsce.addWidget(self._panel)
        self._pusta.setVisible(uwaga is None)
        self._zaslona.raise_()

    def _wyslij(self, nazwa: str, argumenty: tuple) -> None:
        if not self._chroniona:  # klikniecie (takze Enter na przycisku z fokusem) w czasie ochrony jest pomijane
            self.polecenie.emit(nazwa, argumenty)

    def uwaga(self) -> Uwaga | None:
        return self._uwaga

    def klucz(self) -> tuple | None:
        """Tozsamosc pokazanej pozycji (``Uwaga.klucz``) albo None, gdy strefa jest pusta."""
        return self._uwaga.klucz if self._uwaga is not None else None

    def panele(self) -> list:
        """Panel pokazanej pozycji (lista jednoelementowa albo pusta) - do testow i kontroli."""
        return [self._panel] if self._panel is not None else []

    def chron(self, wlaczona: bool) -> None:
        if wlaczona != self._chroniona:
            self._chroniona = wlaczona
            self._zaslona.setGeometry(self.rect())
            self._zaslona.setVisible(wlaczona)
            self._zaslona.raise_()

    def chroniona(self) -> bool:
        return self._chroniona

    def resizeEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        super().resizeEvent(zdarzenie)
        self._zaslona.setGeometry(self.rect())


# ----------------------------------------------------------------------------
# wybor osoby: lista rozwijana pod paskiem gornym
# ----------------------------------------------------------------------------
class PanelOsoby(QFrame):
    """"Kto teraz pracuje?" - przycisk na kazda osobe z listy; przy zmianie osoby takze "Odchodze od stanowiska" i "Bez zmian".
    Lista rozwija sie pod paskiem gornym (nakladka okna, nie okno modalne). Bez listy osob: sam komunikat."""

    wybrano = Signal(str)
    bez_zmian = Signal()
    wyloguj = Signal()
    SZEROKOSC = 420

    def __init__(self, rodzic: QWidget):
        super().__init__(rodzic)
        self.setObjectName("panel_osoba")
        self.setProperty("rola", "nakladka")
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._uklad = QVBoxLayout(self)
        self._uklad.setContentsMargins(16, 12, 16, 14)
        self._uklad.setSpacing(8)
        self._sygnatura = None
        self.hide()

    def ustaw(self, operatorzy: tuple, obecna: str | None, teksty: list, zmiana_osoby: bool) -> None:
        sygnatura = (tuple(operatorzy), obecna, tuple(teksty), zmiana_osoby)
        if sygnatura == self._sygnatura:
            return
        self._sygnatura = sygnatura
        wyczysc(self._uklad)
        self._uklad.addWidget(etykieta(N.ZMIANA_OSOBY if zmiana_osoby else N.KTO_PRACUJE, "naglowek"))
        for tekst in teksty:
            self._uklad.addWidget(etykieta(tekst, "tresc", zawijaj=True))
        przyciski = UkladPlynny(odstep_poziomy=8, odstep_pionowy=8)
        for i, osoba in enumerate(operatorzy):
            b = guzik(osoba, f"osoba_{i}", "osoba", lambda o=osoba: self.wybrano.emit(o))
            b.setCheckable(True)
            b.setChecked(osoba == obecna)
            przyciski.addWidget(b)
        if przyciski.count():
            self._uklad.addLayout(przyciski)
        if zmiana_osoby:
            dol = UkladPlynny(odstep_poziomy=8, odstep_pionowy=6)
            dol.addWidget(guzik(ST.PRZYCISK_WYLOGUJ, "osoba_wyloguj", "lacze", self.wyloguj.emit, 34))
            dol.addWidget(guzik(N.ZOSTAW_OSOBE, "osoba_bez_zmian", "lacze", self.bez_zmian.emit, 34))
            self._uklad.addLayout(dol)
        self.updateGeometry()

    def mousePressEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        _fokus_do_okna(self)
        zdarzenie.accept()  # klikniecie w tlo listy nie trafia w to, co lezy pod nia


# ----------------------------------------------------------------------------
# pasek gorny
# ----------------------------------------------------------------------------
class PasekGorny(QFrame):
    """Pasek gorny (52 px): nazwa programu, przelacznik trybu Wieczor / Poranek, doba robocza i zmiana; po prawej "program
    czeka na plik skanu [Spacja]" i osoba z przyciskiem zmiany (lista osob rozwija sie pod paskiem - ``PanelOsoby``)."""

    skanuj = Signal()
    zmien_osobe = Signal()
    przelacz_tryb = Signal(str)  # tryb docelowy: "wieczor" / "rano"

    def __init__(self):
        super().__init__()
        self.setObjectName("pasek_gorny")
        self.setProperty("blysk", "false")
        self.setFixedHeight(motyw.WYSOKOSC_PASKA_GORNEGO)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._uklad = u = QHBoxLayout(self)
        u.setContentsMargins(20, 0, 20, 0)
        u.setSpacing(24)
        u.addWidget(etykieta(N.NAZWA_PROGRAMU, "nazwa_programu", "napis_program"))
        tryby = QHBoxLayout()
        tryby.setSpacing(0)
        self.przyciski_trybu = {}
        for tryb, rola in (("wieczor", "segment_lewy"), ("rano", "segment_prawy")):
            b = guzik(ST.NAZWY_TRYBOW[tryb], f"przycisk_tryb_{tryb}", rola, lambda t=tryb: self._klik_trybu(t))
            b.setMinimumWidth(108)  # wybrana czesc ma napis pogrubiony - szerokosc nie zalezy od tego, ktora jest wybrana
            b.setCheckable(True)
            b.setToolTip(NR.PRZELACZ_OPIS.format(tryb=ST.NAZWY_TRYBOW[tryb]))
            b.setAccessibleDescription(N.TRYB_GRUPA)
            self.przyciski_trybu[tryb] = b
            tryby.addWidget(b)
        u.addLayout(tryby)
        self.doba = etykieta("", "tresc_glowna", "napis_doba")
        u.addWidget(self.doba)
        u.addStretch(1)
        tekst = N.SKANUJ_ATRAPA if START_SKANU_ATRAPA else ST.PRZYCISKI["start_skanu"]
        self.przycisk_skanuj = przycisk_skrotu(tekst, "przycisk_skanuj", "czekanie" if START_SKANU_ATRAPA else "glowny", self.skanuj.emit, 34,
                                               barwa="cichy", px=motyw.PX_TRESC)
        if START_SKANU_ATRAPA:
            self.przycisk_skanuj.setToolTip(N.SKANUJ_ATRAPA_OPIS)
        u.addWidget(self.przycisk_skanuj)
        osoba = QHBoxLayout()
        osoba.setSpacing(10)
        osoba.addWidget(etykieta(N.OSOBA, "tresc"))
        self.osoba = etykieta("", "osoba", "napis_osoba")
        osoba.addWidget(self.osoba, 0, Qt.AlignmentFlag.AlignVCenter)
        self.przycisk_osoby = guzik(N.ZMIEN_OSOBE, "przycisk_zmien_osobe", "wglebiony", self.zmien_osobe.emit, 34)
        polityka = self.przycisk_osoby.sizePolicy()
        polityka.setRetainSizeWhenHidden(True)  # ukryty zachowuje miejsce: pasek nie zmienia ukladu
        self.przycisk_osoby.setSizePolicy(polityka)
        osoba.addWidget(self.przycisk_osoby)
        u.addLayout(osoba)
        self._tryb = "wieczor"
        self._sygnatura = None
        self._blysk = QTimer(self)
        self._blysk.setSingleShot(True)
        self._blysk.timeout.connect(lambda: ustaw_role(self, "false", "blysk"))

    def ustaw_uklad(self, u: motyw.Uklad) -> None:
        self._uklad.setContentsMargins(u.bok, 0, u.bok, 0)
        self._uklad.setSpacing(16 if u.zwarty else 24)

    def _klik_trybu(self, tryb: str) -> None:
        self._zaznacz()  # wyglad przelacznika idzie za stanem programu, nie za kliknieciem (polecenie moze zostac odrzucone)
        if tryb != self._tryb:
            self.przelacz_tryb.emit(tryb)

    def _zaznacz(self) -> None:
        for tryb, b in self.przyciski_trybu.items():
            b.setChecked(tryb == self._tryb)

    def blysk(self) -> None:
        """Krotki sygnal na pasku (A-P2): nowy wynik plytki, na ktora ekran sie nie przelaczyl - linia paska w kolorze akcentu."""
        ustaw_role(self, "true", "blysk")
        self._blysk.start(BLYSK_MS)

    def ustaw(self, stan) -> None:
        sygnatura = (stan.tryb, stan.doba, stan.zmiana, stan.operator)
        self._tryb = stan.tryb
        self._zaznacz()
        if sygnatura == self._sygnatura:
            return
        self._sygnatura = sygnatura
        self.doba.setText(N.DOBA_I_ZMIANA.format(doba=dzien(stan.doba, rok=True), zmiana=stan.zmiana))
        self.osoba.setText(stan.operator or N.OSOBA_BRAK)
        ustaw_role(self.osoba, "osoba" if stan.operator else "osoba_brak")
        self.przycisk_osoby.setVisible(stan.operator is not None)


# ----------------------------------------------------------------------------
# pasek stanu i lista bledow programu
# ----------------------------------------------------------------------------
class ListaBledow(QFrame):
    """Rozwijana lista bledow programu nad paskiem stanu (nakladka okna): komunikaty poziomu "blad" i trwale, ktore nie
    dotycza pokazanej plytki. Licznik i przycisk rozwijania sa na pasku stanu; lista nie zabiera miejsca mapie."""

    polecenie = Signal(str, tuple)

    def __init__(self, rodzic: QWidget):
        super().__init__(rodzic)
        self.setObjectName("lista_bledow")
        self.setProperty("rola", "nakladka")
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        uklad = QVBoxLayout(self)
        uklad.setContentsMargins(10, 10, 10, 10)
        uklad.setSpacing(0)
        self.obszar = ObszarPaneli("pasek_bledow", widocznych_min=1)
        uklad.addWidget(self.obszar)
        self._zaslona = Zaslona(self, alfa=110)
        self._chroniona = False
        self.hide()

    def ustaw(self, uwagi: list) -> None:
        """Wymienia panele bledow (``uwagi`` - lista ``Uwaga``, najwazniejsze pierwsze)."""
        wyczysc(self.obszar.uklad)
        for u in uwagi:
            panel = PanelUwagi.z_uwagi(u)
            panel.polecenie.connect(self._wyslij)
            self.obszar.uklad.addWidget(panel)
        self.obszar.odswiez()
        self._zaslona.raise_()

    def _wyslij(self, nazwa: str, argumenty: tuple) -> None:
        if not self._chroniona:
            self.polecenie.emit(nazwa, argumenty)

    def panele(self) -> list:
        return self.obszar.panele()

    def wysokosc_dla(self, szerokosc: int, limit: int) -> int:
        """Wysokosc listy przy szerokosci ``szerokosc``: wszystkie panele w calosci, najwyzej ``limit`` (reszta przewijana)."""
        m = self.layout().contentsMargins()
        w = max(120, szerokosc - m.left() - m.right())
        wnetrze = self.obszar.wysokosc_paneli(w) + 2
        limit = max(limit, self.obszar.wysokosc_paneli(w, 1) + 2 + m.top() + m.bottom())  # pierwszy (najwazniejszy) blad zawsze w calosci
        miesci_sie = wnetrze + m.top() + m.bottom() <= limit
        # pasek przewijania tylko wtedy, gdy bledow jest wiecej, niz miesci lista (z paskiem panele sa wezsze - i tak limit)
        self.obszar.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff if miesci_sie else Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        return wnetrze + m.top() + m.bottom() if miesci_sie else limit

    def chron(self, wlaczona: bool) -> None:
        if wlaczona != self._chroniona:
            self._chroniona = wlaczona
            self._zaslona.setGeometry(self.rect())
            self._zaslona.setVisible(wlaczona)
            self._zaslona.raise_()

    def chroniona(self) -> bool:
        return self._chroniona

    def resizeEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        super().resizeEvent(zdarzenie)
        self._zaslona.setGeometry(self.rect())

    def mousePressEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        _fokus_do_okna(self)
        zdarzenie.accept()


class PasekStanu(QFrame):
    """Pasek stanu na dole okna (32 px, jeden wiersz): folder skanera, analiza (procent, pasek, kolejka), folder projektow
    z "Odswiez pule", ramki W / P z "Test LED" i "Przejmij ramke", po prawej licznik bledow programu (rozwija liste) i wersja
    programu. Wysokosc paska jest stala. Dlugie wartosci (napis puli, kolejka, ramki) przy braku miejsca sa skracane
    z wielokropkiem, a pelny napis jest w podpowiedzi (``EtykietaSkracana``)."""

    odswiez_pule = Signal()
    test_led = Signal()  # E3-A12: "Test LED" (ramki)
    przejmij_ramke = Signal(str)  # E3-A12: rola ramki do przejecia ("W" / "P") po "drugi laptop" / "zly klucz"
    przelacz_bledy = Signal()

    def __init__(self, wersja: str = ""):
        super().__init__()
        self.setObjectName("pasek_stanu")
        self.setFixedHeight(motyw.WYSOKOSC_PASKA_STANU)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._uklad = u = QHBoxLayout(self)
        u.setContentsMargins(20, 0, 20, 0)
        u.setSpacing(24)
        self.kropka_skanera = Kropka(None, 8)
        self.skaner = self._pole(N.SKANER, "napis_skaner", self.kropka_skanera, stala=True)
        self.postep = QProgressBar()
        self.postep.setObjectName("pasek_postepu")
        self.postep.setRange(0, 100)
        self.postep.setTextVisible(False)  # procent jest w napisie obok
        self.postep.setFixedWidth(64)
        self.postep.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.kolejka = EtykietaSkracana("stan_wartosc", "napis_kolejka")
        self.kropka_analizy = Kropka(None, 8)
        self.analiza = self._pole(N.ANALIZA, "napis_analiza", self.kropka_analizy, self.postep, self.kolejka, stala=True)
        self.przycisk_puli = guzik(ST.PRZYCISKI["odswiez_pule"], "przycisk_odswiez_pule", "stan", self.odswiez_pule.emit)
        self.postep_puli = QProgressBar()  # liczenie puli trwa: pasek bez konca, przycisk nieaktywny
        self.postep_puli.setObjectName("pasek_puli")
        self.postep_puli.setRange(0, 0)
        self.postep_puli.setTextVisible(False)
        self.postep_puli.setFixedWidth(48)
        self.postep_puli.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.kropka_puli = Kropka(None, 8)
        self.pula = self._pole(N.PULA, "napis_pula", self.kropka_puli, self.przycisk_puli, self.postep_puli)
        # E3-A12: stan ramek, "Test LED" i "Przejmij ramke" - tylko gdy program ma ramki (``stan.ramki``)
        self.przycisk_test_led = guzik(NR.TEST_LED, "przycisk_test_led", "stan", self.test_led.emit)
        self.przycisk_test_led.setToolTip(NR.TEST_LED_OPIS)
        self._do_przejecia: str | None = None
        self.przycisk_przejmij = guzik("", "przycisk_przejmij_ramke", "stan", lambda: self.przejmij_ramke.emit(self._do_przejecia or ""))
        self.przycisk_przejmij.setToolTip(NR.PRZEJMIJ_OPIS)
        self.kropka_ramek = Kropka(None, 8, kwadrat=True)
        self.ramki = self._pole(NR.RAMKI, "napis_ramki", self.kropka_ramek, self.przycisk_test_led, self.przycisk_przejmij)
        self.pole_ramki = self.ramki.parentWidget()
        self.pole_ramki.setVisible(False)
        # E3-U1b: stan Excela (makieta poranka) - tylko w trybie "Poranek"
        self.kropka_excela = Kropka(None, 8)
        self.excel = self._pole(NR.EXCEL_PASEK, "napis_excel", self.kropka_excela)
        self.pole_excela = self.excel.parentWidget()
        self.pole_excela.setVisible(False)
        u.addStretch(1)
        self.przycisk_bledy = guzik("", "przycisk_bledy", "stan_blad", self.przelacz_bledy.emit)
        self.przycisk_bledy.setToolTip(N.BLEDY_OPIS)
        self.przycisk_bledy.setVisible(False)
        u.addWidget(self.przycisk_bledy)
        self.wersja = etykieta(N.WERSJA.format(wersja=wersja) if wersja else "", "stan", "napis_wersja")
        self.wersja.setVisible(bool(wersja))
        u.addWidget(self.wersja)
        self._sygnatura = None
        self._liczenie_od: float | None = None

    def _pole(self, podpis: str, nazwa: str, kropka: Kropka, *dodatki: QWidget, stala: bool = False) -> QLabel:
        pole = QWidget()
        pole.setObjectName(f"pole_{nazwa}")
        uklad = QHBoxLayout(pole)
        uklad.setContentsMargins(0, 0, 0, 0)
        uklad.setSpacing(6)
        uklad.addWidget(kropka, 0, Qt.AlignmentFlag.AlignVCenter)
        uklad.addWidget(etykieta(N.PODPIS_POLA.format(podpis=podpis), "stan"))
        wartosc = etykieta("", "stan_wartosc", nazwa) if stala else EtykietaSkracana("stan_wartosc", nazwa)
        uklad.addWidget(wartosc)
        for dodatek in dodatki:
            uklad.addWidget(dodatek, 0, Qt.AlignmentFlag.AlignVCenter)
        self._uklad.addWidget(pole)
        return wartosc

    def ustaw_uklad(self, u: motyw.Uklad) -> None:
        self._uklad.setContentsMargins(u.bok, 0, u.bok, 0)
        self._uklad.setSpacing(12 if u.zwarty else 24)

    def ustaw_bledy(self, ile: int, rozwiniete: bool) -> None:
        """Licznik bledow programu (przycisk rozwijajacy liste); ``ile`` = 0 - przycisk ukryty."""
        self.przycisk_bledy.setText(N.BLEDY_PROGRAMU.format(n=ile))
        self.przycisk_bledy.setVisible(ile > 0)
        self.przycisk_bledy.setAccessibleDescription(N.BLEDY_ROZWINIETE if rozwiniete else N.BLEDY_ZWINIETE)

    def ustaw(self, stan) -> None:
        sk, kol, an = stan.skaner, stan.kolejka, stan.analiza
        sygnatura = (stan.pula.napis, stan.pula.stan, getattr(stan.pula, "budowa_razem", None), getattr(stan.pula, "budowa_gotowe", None),
                     sk.dostepny, sk.dziala, sk.zajete, sk.czeka_na_skan, kol, kol.w_toku, kol.silnik_gotowy,
                     None if an is None else round(an.udzial * 100), stan.zamkniety, getattr(stan, "ramki", None), stan.tryb,
                     getattr(stan, "excel", None))
        if sygnatura == self._sygnatura:
            return
        self._sygnatura = sygnatura
        # napis puli ze stanu (takze dla stanu, ktorego ta wersja ekranu nie zna); folder puli jest ustawieniem i nie jest pokazywany
        self.pula.setText(stan.pula.napis or ST.STANY_PULI.get(stan.pula.stan, ""))
        pula_dobra = stan.pula.stan in ("gotowa", "liczenie")
        ustaw_role(self.pula, "stan_wartosc" if pula_dobra else "stan_uwaga")
        self.kropka_puli.ustaw(motyw.AKCENT if stan.pula.stan == "gotowa" else None)
        liczenie = stan.pula.stan == "liczenie"
        if liczenie and self._liczenie_od is None:
            self._liczenie_od = time.monotonic()
            QTimer.singleShot(int(LIMIT_LICZENIA_PULI_S * 1000) + 50, self, self._sprawdz_liczenie)
        elif not liczenie:
            self._liczenie_od = None
        self._sprawdz_liczenie()
        # E3-A5i: budowa puli wpisow w procesie silnika - pasek z postepem (gotowe z razem); liczenie katalogu - pasek bez konca
        razem, gotowe = getattr(stan.pula, "budowa_razem", None), getattr(stan.pula, "budowa_gotowe", None) or 0
        buduje = bool(razem) and gotowe < razem
        if buduje:
            self.postep_puli.setRange(0, razem)
            self.postep_puli.setValue(gotowe)
        elif self.postep_puli.maximum() != 0:
            self.postep_puli.setRange(0, 0)
        self.postep_puli.setVisible(liczenie or buduje)
        if not sk.dostepny:
            self.skaner.setText(N.SKANER_BRAK_FOLDERU)
        elif not sk.dziala:
            self.skaner.setText(N.SKANER_NIE_DZIALA)
        elif sk.zajete:
            self.skaner.setText(N.SKANER_ZAJETY)
        elif sk.czeka_na_skan:
            self.skaner.setText(N.SKANER_CZEKA)
        else:
            self.skaner.setText(N.SKANER_GOTOWY)
        skaner_dobry = sk.dostepny and sk.dziala
        ustaw_role(self.skaner, "stan_wartosc" if skaner_dobry else "stan_uwaga")
        self.kropka_skanera.ustaw(motyw.AKCENT if skaner_dobry else None)
        self.postep.setVisible(an is not None)
        if an is not None:
            procent = max(0, min(100, round(an.udzial * 100)))
            self.postep.setValue(procent)
            self.analiza.setText(N.ANALIZA_TRWA.format(procent=procent))
        else:
            self.analiza.setText(N.ANALIZA_CZEKA if kol.razem else N.ANALIZA_BRAK)
        self.kropka_analizy.ustaw(motyw.AKCENT if an is not None else None)
        czesci = [N.KOLEJKA.format(n=kol.czeka)] if kol.czeka else []
        niezapisane = kol.niezapisane  # czesc ``wstrzymane``: policzone, czekaja na zapis w bazie (kontrakt w wersji 2)
        if kol.wstrzymane - niezapisane > 0:  # skany wstrzymane CZEKAJA (na pule projektow albo na analize) - to nie blad
            czeka_na_pule = stan.pula.stan != "gotowa"
            czesci.append((N.WSTRZYMANE_PULA if czeka_na_pule else N.WSTRZYMANE_ANALIZA).format(n=kol.wstrzymane - niezapisane))
        if niezapisane:
            czesci.append(N.WSTRZYMANE_ZAPIS.format(n=niezapisane))
        self.kolejka.setText(N.ODSTEP_KOLEJKI.join(czesci))
        self.kolejka.setVisible(bool(czesci))
        self._ustaw_ramki(getattr(stan, "ramki", None))
        self._ustaw_excel(stan)

    def _ustaw_excel(self, stan) -> None:
        """E3-U1b: "Excel: gotowy / do zatwierdzenia: n / przygotowuje... / blad - sprawdz / niedostepny" - tylko rano (makieta).
        Tresc bledu Excela (ze stanu) w podpowiedzi; kolor kropki: akcent, gdy Excel dziala."""
        rano = stan.tryb == "rano"
        self.pole_excela.setVisible(rano)
        if not rano:
            return
        ex = getattr(stan, "excel", None)
        if ex is None:
            klucz = "brak"
        elif ex.blad:
            klucz = "blad"
        elif ex.w_toku:
            klucz = "w_toku"
        elif ex.do_zalatwienia:
            klucz = "do_zatwierdzenia"
        else:
            klucz = "gotowy"
        self.excel.setText(NR.EXCEL_PASEK_STANY[klucz].format(n=ex.do_zalatwienia if ex is not None else 0))
        self.excel.setToolTip(NR.dla_technika(ex.blad) if ex is not None and ex.blad else "")
        dobrze = klucz in ("gotowy", "do_zatwierdzenia", "w_toku")
        ustaw_role(self.excel, "stan_wartosc" if dobrze else "stan_uwaga")
        self.kropka_excela.ustaw(motyw.AKCENT if dobrze else None)

    def _ustaw_ramki(self, r) -> None:
        """E3-A12: "Ramki: W: gotowa, P: brak polaczenia" (podpowiedz: komunikaty i ostrzezenia klientow), przycisk "Przejmij
        ramke" przy ramce wstrzymanej (drugi laptop, zly klucz). Bez ramek pole ukryte. E3-R1: ramki wylaczone w ustawieniach
        (``r.wylaczone``) - neutralne "Ramki: wylaczone" (zwykly kolor tekstu, kropka bez barwy, bez przyciskow ramek)."""
        self.pole_ramki.setVisible(r is not None)
        if r is None:
            return
        if getattr(r, "wylaczone", False):
            self.ramki.setText(NR.RAMKI_WYLACZONE)
            self.ramki.setToolTip(NR.RAMKI_WYLACZONE_OPIS)
            ustaw_role(self.ramki, "stan_wartosc")
            self.kropka_ramek.ustaw(None)
            self._do_przejecia = None
            self.przycisk_test_led.setVisible(False)
            self.przycisk_przejmij.setVisible(False)
            return
        self.przycisk_test_led.setVisible(True)
        czesci, podpowiedz, dobrze, przejecie = [], [], True, None
        for x in (r.wieczorna, r.poranna):
            if x is None:
                continue
            klucz = "test" if r.test_led else ("gotowa" if x.polaczona and x.blad is None else (x.blad or "brak_polaczenia"))
            czesci.append(NR.RAMKA_STAN.format(rola=x.rola, stan=NR.RAMKA_STANY.get(klucz, NR.RAMKA_STANY["inny"]))
                          + (NR.RAMKA_PLYTKA.format(n=x.plytka) if x.plytka else ""))
            podpowiedz += [t for t in ((x.komunikat or ""),) + tuple(x.ostrzezenia) if t and t not in podpowiedz]
            if getattr(x, "utracone", 0):  # recenzja PR #30 D7: utracone zdarzenia ramki (dziennik ramki przepelniony w przerwie)
                podpowiedz.append(NR.RAMKA_UTRACONE.format(rola=x.rola, n=x.utracone))
            dobrze = dobrze and klucz in ("gotowa", "test")
            if przejecie is None and (x.wstrzymane or x.blad in ("inny_laptop", "zly_klucz")):
                przejecie = x.rola
        self.ramki.setText(NR.RAMKI_ODSTEP.join(czesci))
        self.ramki.setToolTip(chr(10).join(podpowiedz))
        ustaw_role(self.ramki, "stan_wartosc" if dobrze else "stan_uwaga")
        self.kropka_ramek.ustaw(motyw.AKCENT if dobrze else None)
        self._do_przejecia = przejecie
        self.przycisk_przejmij.setText(NR.PRZEJMIJ_RAMKE.format(rola=przejecie or ""))
        self.przycisk_przejmij.setVisible(przejecie is not None)

    def _sprawdz_liczenie(self) -> None:
        """"Odswiez pule" nieaktywne w trakcie liczenia; po ``LIMIT_LICZENIA_PULI_S`` znowu aktywne (A-D5: liczenie moglo zawisnac
        na folderze sieciowym - nowe klikniecie uruchamia nowe liczenie)."""
        trwa = self._liczenie_od is not None and time.monotonic() - self._liczenie_od < LIMIT_LICZENIA_PULI_S
        self.przycisk_puli.setEnabled(not trwa)
