"""czesci - elementy ekranu wieczornego: pasek stanu, wybor osoby, panele pytan i komunikatow, lista plytek, widok pracy,
lista "do dofrezowania".

Kazdy element dostaje gotowe dane ze stanu kontrolera (``ustaw(...)``) i oddaje wybor technika sygnalem - sam nie wola
kontrolera i niczego nie liczy. Kolory i napisy statusow pochodza z pol stanu (``rgb``, ``podpis``, ``opis``, ``napis``)
i ze ``statusy``; pozostale napisy z ``napisy``.

Klawiatura: przyciski i kafelki plytek przyjmuja fokus TYLKO klawiszem Tab (nie kliknieciem) - Enter "klika" przycisk
z fokusem; Spacja, U / O / C / N, Esc i strzalki zawsze ida do okna (``PrzyciskEkranu``), dzieki czemu Spacja jest zawsze
startem skanu, a nie "kliknieciem" przycisku. Klikniecie mysza oddaje fokus oknu.

Rozmiary (A-P1): przyciski stoja w ukladzie "plynacym" (``UkladPlynny`` - gdy brakuje szerokosci, przechodza do nastepnego
wiersza zamiast byc ucinane), panele uwag w obszarze przewijanym o wysokosci z zawartosci (``ObszarPaneli``); kazdy element
ma ``ustaw_tryb(rozmiary)`` dla ukladu zwykle / zwarte (``styl``).
"""
from __future__ import annotations

import time

from PySide6.QtCore import QEvent, QPoint, QRect, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QFrame, QHBoxLayout, QHeaderView, QLabel, QLayout, QProgressBar, QPushButton,
                               QScrollArea, QSizePolicy, QStackedLayout, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

from .. import statusy as ST
from . import napisy as N
from . import napisy_rano as NR
from . import styl

# polecenia, ktore kontroler przyjmuje tylko od wybranej osoby (reszta: zamkniecie pytania / komunikatu, pula, start skanu)
BEZ_OSOBY = ("zamknij_pytanie", "zamknij_komunikat", "odswiez_pule", "start_skanu", "wybierz_operatora", "ustaw_pule", "zamknij",
             "przelacz_tryb", "ustaw_kolejnosc", "wybierz_kuwete")  # poranek (E3-A7)
# "polecenia" przyciskow, ktore obsluguje samo okno (nie ida do kontrolera)
LOKALNE_NUMER_BEZ_ZMIAN = "_numer_bez_zmian"
LOKALNE_ZAMKNIJ_ODPOWIEDZ = "_zamknij_odpowiedz"
LOKALNE_ZAMKNIJ_INFORMACJE = "_zamknij_informacje"
LOKALNE_POKAZ_NOWA = "_pokaz_nowa"  # E3-P14 (N2): "Pokaz nowy wynik" z panelu "Nowy wynik czeka"
KLASY_LICZNIKOW = (ST.KOLOR_CZERWONY, ST.KOLOR_ZOLTY, ST.KOLOR_POMARANCZOWY, ST.KOLOR_SZARY, ST.KOLOR_ZATWIERDZONA_OK, ST.KOLOR_ZIELONY)
SKAN_PRZYJETY = "przyjety"  # klucz ``statusy.STATUSY_PLYTKI`` skanu, ktory sie liczy i przyjmuje decyzje
# Start skanu z programu jest atrapa do dnia skanera (kontrakt: ``aplikacja.md`` "Start skanu (DW5)"; stan nie mowi, czy
# akcja startu cokolwiek uruchamia - POTRZEBUJE w raporcie). Do tego czasu przycisk mowi technikowi, ze skan uruchamia
# w programie skanera, a Spacja tylko oznacza "czekam na plik".
START_SKANU_ATRAPA = True
LIMIT_LICZENIA_PULI_S = 15.0  # A-D5: po tylu sekundach liczenia "Odswiez pule" znow jest aktywne (liczenie moglo zawisnac)
BLYSK_MS = 1500


# ----------------------------------------------------------------------------
# drobne narzedzia
# ----------------------------------------------------------------------------
def etykieta(tekst: str = "", rola: str | None = None, nazwa: str | None = None, zawijaj: bool = False) -> QLabel:
    e = QLabel(tekst)
    e.setTextFormat(Qt.TextFormat.PlainText)
    e.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    if rola:
        e.setProperty("rola", rola)
    if nazwa:
        e.setObjectName(nazwa)
    if zawijaj:
        e.setWordWrap(True)
    return e


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


def przycisk(tekst: str, nazwa: str | None = None, rola: str | None = None, po_kliknieciu=None, wysokosc: int | None = None) -> QPushButton:
    b = PrzyciskEkranu(tekst)
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


def ramka(rola: str = "panel", nazwa: str | None = None) -> QFrame:
    r = QFrame()
    r.setProperty("rola", rola)
    r.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    if nazwa:
        r.setObjectName(nazwa)
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


def znaczek(tekst: str, hex_: str, nazwa: str | None = None, rozmiar_px: int = 15) -> QLabel:
    """Maly prostokat w kolorze ``hex_`` (kolor podaje wolajacy - ze stanu albo ze ``statusy``) z napisem."""
    e = etykieta(tekst, nazwa=nazwa)
    e.setAlignment(Qt.AlignmentFlag.AlignCenter)
    e.setStyleSheet(_styl_znaczka(hex_, rozmiar_px))
    return e


def _styl_znaczka(hex_: str, rozmiar_px: int) -> str:
    dopelnienie = "1px 5px" if rozmiar_px <= 13 else "2px 8px"
    return (f"background: {hex_}; color: {styl.tekst_na(hex_)}; border: 1px solid #3a4047; border-radius: 5px; "
            f"padding: {dopelnienie}; font-size: {rozmiar_px}px; font-weight: 700;")


def styl_znaczka_poziomu(poziom: str, rozmiar_px: int) -> str:
    tlo, pasek, kolor = styl.POZIOMY.get(poziom, styl.POZIOMY["info"])
    return (f"background: {tlo}; color: {kolor}; border: 2px solid {pasek}; border-radius: 5px; padding: 1px 6px; "
            f"font-size: {rozmiar_px}px; font-weight: 700;")


def znaczek_poziomu(tekst: str, poziom: str, nazwa: str | None = None, rozmiar_px: int = 13) -> QLabel:
    """Znaczek w barwach poziomu komunikatu (``styl.POZIOMY``) - np. "plytka poranna - dopuszczona swiadomie"."""
    e = etykieta(tekst, nazwa=nazwa)
    e.setAlignment(Qt.AlignmentFlag.AlignCenter)
    e.setStyleSheet(styl_znaczka_poziomu(poziom, rozmiar_px))
    return e


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
    ``widocznych_min`` pierwszych paneli w calosci, reszta jest przewijana (nic nie jest uciete). Pusty obszar jest ukryty."""

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
        # arkusz z selektorem: arkusz bez selektora przeszedlby na wszystkie panele i przyciski (np. bez tla zaznaczonej osoby)
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

    def _wysokosc(self, ile: int | None = None) -> int:
        # szerokosc, ktora panele naprawde maja: przy widocznym pasku przewijania pionowego - wezsza (E3-A1p: liczona dla pelnej
        # szerokosci wysokosc byla za mala, tekst zawijal sie w dodatkowy wiersz i obszar zostawal przyciety z paskiem przewijania)
        szer = max(120, self.viewport().width() if self.verticalScrollBar().isVisible() else self.width())
        panele = self.panele()
        if ile is not None:
            panele = panele[:ile]
        if not panele:
            return 0
        wys = [p.heightForWidth(szer) if p.hasHeightForWidth() else p.sizeHint().height() for p in panele]
        return sum(max(h, p.minimumSizeHint().height()) for h, p in zip(wys, panele)) + self.uklad.spacing() * (len(panele) - 1)

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
# pasek stanu
# ----------------------------------------------------------------------------
class PasekStanu(QFrame):
    """Tryb, doba robocza i zmiana, osoba, kolejka (wiersz 1); folder projektow z "Odswiez pule", folder skanera, analiza
    z postepem (wiersz 2); po prawej "Skanuj". Dwa STALE wiersze "podpis: wartosc": wysokosc paska nie zalezy od tresci,
    wiec nic pod nim (zwlaszcza przyciski decyzji) nie przesuwa sie, gdy zmienia sie kolejka albo stan skanera."""

    skanuj = Signal()
    odswiez_pule = Signal()
    zmien_osobe = Signal()
    przelacz_tryb = Signal()  # E3-A7: przycisk "-> Poranek" / "-> Wieczor" obok trybu
    test_led = Signal()  # E3-A12: "Test LED" (ramki)
    przejmij_ramke = Signal(str)  # E3-A12: rola ramki do przejecia ("W" / "P") po "drugi laptop" / "zly klucz"

    def __init__(self):
        super().__init__()
        self.setProperty("rola", "pasek")
        self.setProperty("blysk", "false")
        self.setObjectName("pasek_stanu")
        self._uklad = QHBoxLayout(self)
        self._uklad.setContentsMargins(14, 6, 14, 6)
        self._uklad.setSpacing(14)
        siatka = QVBoxLayout()
        siatka.setSpacing(2)
        self._wiersze = (QHBoxLayout(), QHBoxLayout())
        for wiersz in self._wiersze:
            wiersz.setSpacing(22)
            siatka.addLayout(wiersz)
        self._uklad.addLayout(siatka, 1)
        w1, w2 = self._wiersze
        self.przycisk_trybu = przycisk("", "przycisk_przelacz_tryb", "lacze", self.przelacz_tryb.emit)  # E3-A7: Wieczor <-> Poranek
        self.tryb = self._pole(w1, N.TRYB, "napis_tryb", self.przycisk_trybu)
        self.doba = self._pole(w1, N.DOBA, "napis_doba")
        self.przycisk_osoby = przycisk(N.ZMIEN_OSOBE, "przycisk_zmien_osobe", "lacze", self.zmien_osobe.emit)
        self.osoba = self._pole(w1, N.OSOBA, "napis_osoba", self.przycisk_osoby)
        # E3-A12: stan ramek, "Test LED" i "Przejmij ramke" - tylko gdy program ma ramki (``stan.ramki``)
        self.przycisk_test_led = przycisk(NR.TEST_LED, "przycisk_test_led", "lacze", self.test_led.emit)
        self.przycisk_test_led.setToolTip(NR.TEST_LED_OPIS)
        self.przycisk_przejmij = przycisk("", "przycisk_przejmij_ramke", "lacze", lambda: self.przejmij_ramke.emit(self._do_przejecia or ""))
        self.przycisk_przejmij.setToolTip(NR.PRZEJMIJ_OPIS)
        self._do_przejecia: str | None = None
        self.ramki = self._pole(w1, NR.RAMKI, "napis_ramki", self.przycisk_test_led, self.przycisk_przejmij)
        self.pole_ramki = self.ramki.parentWidget()
        self.pole_ramki.setVisible(False)
        self.kolejka = etykieta("", "slaby", "napis_kolejka")
        w1.addWidget(self.kolejka)
        w1.addStretch(1)
        self.przycisk_puli = przycisk(ST.PRZYCISKI["odswiez_pule"], "przycisk_odswiez_pule", None, self.odswiez_pule.emit)
        self.postep_puli = QProgressBar()  # liczenie puli trwa: pasek bez konca, przycisk nieaktywny
        self.postep_puli.setObjectName("pasek_puli")
        self.postep_puli.setRange(0, 0)
        self.postep_puli.setTextVisible(False)
        self.postep_puli.setFixedWidth(70)
        self.postep_puli.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.pula = self._pole(w2, N.PULA, "napis_pula", self.przycisk_puli, self.postep_puli)
        self.skaner = self._pole(w2, N.SKANER, "napis_skaner")
        self.postep = QProgressBar()
        self.postep.setObjectName("pasek_postepu")
        self.postep.setRange(0, 100)
        self.postep.setTextVisible(False)  # procent jest w napisie obok
        self.postep.setFixedWidth(120)
        self.postep.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.analiza = self._pole(w2, N.ANALIZA, "napis_analiza", self.postep)
        w2.addStretch(1)
        tekst = N.SKANUJ_ATRAPA if START_SKANU_ATRAPA else ST.PRZYCISKI["start_skanu"]
        # E3-P14 (poz. 6): dopoki start skanu jest atrapa, przycisk NIE wyglada jak przycisk glowny "start" (jasne tlo, mniejsze
        # pismo) - mowi tylko, ze program czeka na plik, a skan uruchamia sie w programie skanera
        self.przycisk_skanuj = przycisk(tekst, "przycisk_skanuj", "czekanie" if START_SKANU_ATRAPA else "glowny", self.skanuj.emit,
                                        styl.ZWYKLE.wysokosc_skanuj)
        if START_SKANU_ATRAPA:
            self.przycisk_skanuj.setToolTip(N.SKANUJ_ATRAPA_OPIS)
        self._uklad.addWidget(self.przycisk_skanuj, 0, Qt.AlignmentFlag.AlignVCenter)
        for w in (self.przycisk_osoby, self.postep_puli, self.postep):  # ukryte zachowuja miejsce: pasek nie zmienia wysokosci ani ukladu
            polityka = w.sizePolicy()
            polityka.setRetainSizeWhenHidden(True)
            w.setSizePolicy(polityka)
        self._sygnatura = None
        self._liczenie_od: float | None = None
        self._blysk = QTimer(self)
        self._blysk.setSingleShot(True)
        self._blysk.timeout.connect(lambda: self._ustaw_blysk(False))

    @staticmethod
    def _pole(wiersz: QHBoxLayout, podpis: str, nazwa: str, *dodatki: QWidget) -> QLabel:
        pole = QWidget()
        pole.setObjectName(f"pole_{nazwa}")
        uklad = QHBoxLayout(pole)
        uklad.setContentsMargins(0, 0, 0, 0)
        uklad.setSpacing(6)
        uklad.addWidget(etykieta(N.PODPIS_POLA.format(podpis=podpis), "podpis"))
        wartosc = etykieta("", "wartosc", nazwa)
        uklad.addWidget(wartosc)
        for dodatek in dodatki:
            uklad.addSpacing(4)
            uklad.addWidget(dodatek)
        wiersz.addWidget(pole)
        return wartosc

    def ustaw_tryb(self, r: styl.Rozmiary) -> None:
        self._uklad.setContentsMargins(*((8, 3, 8, 3) if r.zwarty else (14, 6, 14, 6)))
        self._uklad.setSpacing(10 if r.zwarty else 14)
        for wiersz in self._wiersze:
            wiersz.setSpacing(14 if r.zwarty else 22)
        self.przycisk_skanuj.setMinimumHeight(r.wysokosc_skanuj)
        self.postep.setFixedWidth(90 if r.zwarty else 120)
        self.postep_puli.setFixedWidth(56 if r.zwarty else 70)

    def blysk(self) -> None:
        """Krotki sygnal na pasku (A-P2): nowy wynik plytki, na ktora ekran sie nie przelaczyl - pasek na chwile w kolorze akcentu."""
        self._ustaw_blysk(True)
        self._blysk.start(BLYSK_MS)

    def _ustaw_blysk(self, wlaczony: bool) -> None:
        self.setProperty("blysk", "true" if wlaczony else "false")
        self.style().unpolish(self)
        self.style().polish(self)

    def ustaw(self, stan) -> None:
        sk, kol, an = stan.skaner, stan.kolejka, stan.analiza
        sygnatura = (stan.tryb, stan.doba, stan.zmiana, stan.operator, stan.operatorzy, stan.wymaga_operatora, stan.pula.napis, stan.pula.stan,
                     sk.dostepny, sk.dziala, sk.zajete, sk.czeka_na_skan, kol, kol.w_toku, kol.silnik_gotowy,
                     None if an is None else round(an.udzial * 100), stan.zamkniety, getattr(stan, "ramki", None))
        if sygnatura == self._sygnatura:
            return
        self._sygnatura = sygnatura
        self.tryb.setText(ST.NAZWY_TRYBOW.get(stan.tryb, stan.tryb))
        inny = ST.NAZWY_TRYBOW["wieczor" if stan.tryb == "rano" else "rano"]
        self.przycisk_trybu.setText(NR.PRZELACZ_NA.format(tryb=inny))
        self.przycisk_trybu.setToolTip(NR.PRZELACZ_OPIS.format(tryb=inny))
        self.doba.setText(N.DOBA_I_ZMIANA.format(doba=dzien(stan.doba, rok=True), zmiana=stan.zmiana))
        self.osoba.setText(stan.operator or N.OSOBA_BRAK)
        self._rola(self.osoba, "wartosc" if stan.operator else "wartosc_uwaga")
        self.przycisk_osoby.setVisible(stan.operator is not None)
        # napis puli ze stanu (takze dla stanu, ktorego ta wersja ekranu nie zna); folder puli jest ustawieniem i nie jest pokazywany
        self.pula.setText(stan.pula.napis or ST.STANY_PULI.get(stan.pula.stan, ""))
        self._rola(self.pula, "wartosc" if stan.pula.stan in ("gotowa", "liczenie") else "wartosc_uwaga")
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
        self._rola(self.skaner, "wartosc" if sk.dostepny and sk.dziala else "wartosc_uwaga")
        self.postep.setVisible(an is not None)
        if an is not None:
            procent = max(0, min(100, round(an.udzial * 100)))
            self.postep.setValue(procent)
            self.analiza.setText(N.ANALIZA_TRWA.format(procent=procent))
        else:
            self.analiza.setText(N.ANALIZA_CZEKA if kol.razem else N.ANALIZA_BRAK)
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

    def _ustaw_ramki(self, r) -> None:
        """E3-A12: "Ramki: W: gotowa, P: brak polaczenia" (podpowiedz: komunikaty i ostrzezenia klientow), przycisk "Przejmij
        ramke" przy ramce wstrzymanej (drugi laptop, zly klucz). Bez ramek pole ukryte."""
        self.pole_ramki.setVisible(r is not None)
        if r is None:
            return
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
        self._rola(self.ramki, "wartosc" if dobrze else "wartosc_uwaga")
        self._do_przejecia = przejecie
        self.przycisk_przejmij.setText(NR.PRZEJMIJ_RAMKE.format(rola=przejecie or ""))
        self.przycisk_przejmij.setVisible(przejecie is not None)

    def _sprawdz_liczenie(self) -> None:
        """"Odswiez pule" nieaktywne w trakcie liczenia; po ``LIMIT_LICZENIA_PULI_S`` znowu aktywne (A-D5: liczenie moglo zawisnac
        na folderze sieciowym - nowe klikniecie uruchamia nowe liczenie)."""
        trwa = self._liczenie_od is not None and time.monotonic() - self._liczenie_od < LIMIT_LICZENIA_PULI_S
        self.przycisk_puli.setEnabled(not trwa)

    @staticmethod
    def _rola(pole: QLabel, rola: str) -> None:
        if pole.property("rola") != rola:
            pole.setProperty("rola", rola)
            pole.style().unpolish(pole)
            pole.style().polish(pole)


# ----------------------------------------------------------------------------
# wybor osoby
# ----------------------------------------------------------------------------
class PanelOsoby(QFrame):
    """"Kto teraz pracuje?" - przycisk na kazda osobe z listy. Bez listy osob: sam komunikat (decyzje nie sa zapisywane)."""

    wybrano = Signal(str)
    bez_zmian = Signal()
    wyloguj = Signal()

    def __init__(self, operatorzy: tuple, obecna: str | None, teksty: list, zmiana_osoby: bool, wylogowanie: bool = True,
                 r: styl.Rozmiary = styl.ZWYKLE):
        super().__init__()
        self.setObjectName("panel_osoba")
        tlo, pasek, _ = styl.POZIOMY["info" if zmiana_osoby else "ostrzezenie"]
        self.setStyleSheet(f"QFrame#panel_osoba {{ background: {tlo}; border: 1px solid {pasek}; border-left: 10px solid {pasek}; border-radius: 6px; }}")
        uklad = QHBoxLayout(self)
        uklad.setContentsMargins(*((14, 5, 10, 5) if r.zwarty else (18, 10, 14, 10)))
        uklad.setSpacing(10 if r.zwarty else 16)
        kolumna = QVBoxLayout()
        kolumna.setSpacing(2)
        kolumna.addWidget(etykieta(N.ZMIANA_OSOBY if zmiana_osoby else N.KTO_PRACUJE, "naglowek"))
        for tekst in teksty:
            kolumna.addWidget(etykieta(tekst, zawijaj=True))
        uklad.addLayout(kolumna, 1)
        przyciski = UkladPlynny(odstep_poziomy=8, odstep_pionowy=6)
        for i, osoba in enumerate(operatorzy):
            b = przycisk(osoba, f"osoba_{i}", "osoba", lambda o=osoba: self.wybrano.emit(o))
            b.setCheckable(True)
            b.setChecked(osoba == obecna)
            przyciski.addWidget(b)
        if zmiana_osoby:
            if wylogowanie:
                przyciski.addWidget(przycisk(ST.PRZYCISK_WYLOGUJ, "osoba_wyloguj", "lacze", self.wyloguj.emit))
            przyciski.addWidget(przycisk(N.ZOSTAW_OSOBE, "osoba_bez_zmian", "lacze", self.bez_zmian.emit))
        uklad.addLayout(przyciski)


# ----------------------------------------------------------------------------
# panele pytan i komunikatow
# ----------------------------------------------------------------------------
class PanelUwagi(QFrame):
    """Jedno pytanie albo komunikat ze stanu: tytul, tekst, opcjonalnie rada, ostrzezenie i wyjasnienie, przyciski.
    ``przyciski``: lista (nazwa obiektu, napis, polecenie, argumenty, aktywny, rola); klikniecie = sygnal ``polecenie``.
    Przyciski stoja obok tekstu (do dwoch) albo pod nim; przy waskim panelu przechodza do nastepnego wiersza."""

    polecenie = Signal(str, tuple)

    def __init__(self, nazwa: str, poziom: str, tytul: str, tekst: str, przyciski: list, *, rada: str = "", ostrzezenie: str = "",
                 wyjasnienie: str = "", przyciski_pod_tekstem: bool = False, r: styl.Rozmiary = styl.ZWYKLE):
        super().__init__()
        self.setObjectName(nazwa)
        tlo, pasek, _ = styl.POZIOMY.get(poziom, styl.POZIOMY["ostrzezenie"])
        self.setStyleSheet(f"QFrame#{nazwa} {{ background: {tlo}; border: 1px solid {pasek}; border-left: 10px solid {pasek}; border-radius: 6px; }}")
        uklad = QHBoxLayout(self)
        uklad.setContentsMargins(*((14, 4, 8, 4) if r.zwarty else (18, 8, 12, 8)))
        uklad.setSpacing(10 if r.zwarty else 14)
        kolumna = QVBoxLayout()
        kolumna.setSpacing(1 if r.zwarty else 3)
        kolumna.addWidget(etykieta(tytul, "naglowek", zawijaj=True))
        if rada:
            kolumna.addWidget(etykieta(rada, "duzy", zawijaj=True))
        if tekst:
            kolumna.addWidget(etykieta(tekst, zawijaj=True))
        if ostrzezenie:
            kolumna.addWidget(etykieta(ostrzezenie, "uwaga", "pytanie_ostrzezenie", zawijaj=True))
        if wyjasnienie:
            kolumna.addWidget(etykieta(wyjasnienie, "slaby", zawijaj=True))
        uklad.addLayout(kolumna, 1)
        miejsce = UkladPlynny(odstep_poziomy=8, odstep_pionowy=6 if not r.zwarty else 4)
        for nazwa_b, napis, polecenie, argumenty, aktywny, rola in przyciski:
            b = przycisk(napis, nazwa_b, rola, lambda p=polecenie, a=tuple(argumenty): self.polecenie.emit(p, a))
            b.setEnabled(aktywny)
            if rola not in ("cyfra", "lacze"):
                b.setMinimumHeight(r.wysokosc_przycisku)
            miejsce.addWidget(b)
        if przyciski_pod_tekstem:
            kolumna.addLayout(miejsce)
        else:
            uklad.addLayout(miejsce)


def tytul_plytki(nazwa_plytki_: str, tytul: str) -> str:
    return N.UWAGA_PLYTKI.format(plytka=nazwa_plytki_, tytul=tytul) if nazwa_plytki_ else tytul


def panel_pytania(pytanie, stan, typ_plytki: str | None, plytka: str = "", r: styl.Rozmiary = styl.ZWYKLE) -> PanelUwagi:
    """Panel pytania ze stanu: przyciski z ``pytanie.odpowiedzi``; polecenia wymagajace osoby nieaktywne bez niej (z wyjasnieniem)."""
    jest_osoba = stan.operator is not None
    przyciski, wymaga = [], False
    for odp in pytanie.odpowiedzi:
        potrzebuje_osoby = odp.polecenie not in BEZ_OSOBY
        wymaga = wymaga or potrzebuje_osoby
        cyfra = odp.polecenie == "podaj_numer_plytki" and len(odp.argumenty) == 2  # (skan, numer); rano "mimo to" - zwykly przycisk
        nazwa = nazwa_obiektu("odp", odp.polecenie) + (f"_{odp.argumenty[-1]}" if cyfra else "")
        przyciski.append((nazwa, odp.napis, odp.polecenie, odp.argumenty, jest_osoba or not potrzebuje_osoby, "cyfra" if cyfra else None))
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
    return PanelUwagi(nazwa_obiektu("pytanie", pytanie.rodzaj), pytanie.poziom, tytul_plytki(plytka, pytanie.tytul), tekst, przyciski, rada=rada,
                      ostrzezenie=ostrzezenie, wyjasnienie=wyjasnienie, przyciski_pod_tekstem=len(przyciski) > 2, r=r)


def panel_numeru(skan_id: int, numery: tuple, obecny, jest_osoba: bool, wyjasnienie: str, plytka: str = "",
                 r: styl.Rozmiary = styl.ZWYKLE) -> PanelUwagi:
    """Reczne podanie albo poprawienie numeru plytki (polecenie ``podaj_numer_plytki`` z ``Plytka.dozwolone``). Plytka bez
    numeru: tytul "Podaj numer plytki" bez przedrostka; z numerem: "Plytka n: zmien numer plytki"."""
    przyciski = [(f"odp_podaj_numer_plytki_{n}", str(n), "podaj_numer_plytki", (skan_id, n), jest_osoba and n != obecny, "cyfra") for n in numery]
    przyciski.append(("numer_bez_zmian", N.ZOSTAW_OSOBE, LOKALNE_NUMER_BEZ_ZMIAN, (), True, "lacze"))
    tytul = ST.PRZYCISKI["podaj_numer_plytki"] if obecny is None else tytul_plytki(plytka, N.ZMIEN_NUMER_TYTUL)
    return PanelUwagi("panel_numer_plytki", "info", tytul, N.NUMER_PLYTKI_TEKST, przyciski,
                      wyjasnienie="" if jest_osoba else wyjasnienie, przyciski_pod_tekstem=True, r=r)


def panel_odmowy(tekst: str, r: styl.Rozmiary = styl.ZWYKLE) -> PanelUwagi:
    """Odmowa polecenia, ktorej nie ma w komunikatach stanu (np. ``zle_argumenty``): tekst odpowiedzi kontrolera."""
    return PanelUwagi("komunikat_odpowiedz", ST.KOMUNIKATY["odmowa"].poziom, ST.KOMUNIKATY["odmowa"].tytul, tekst,
                      [("zamknij_odpowiedz", ST.PRZYCISKI["zamknij_komunikat"], LOKALNE_ZAMKNIJ_ODPOWIEDZ, (), True, "lacze")], r=r)


def panel_informacji(tekst: str, r: styl.Rozmiary = styl.ZWYKLE) -> PanelUwagi:
    """Informacja samego ekranu (np. widok pracy zamkniety, bo pracy nie ma juz w stanie) - nie komunikat kontrolera."""
    return PanelUwagi("informacja_ekranu", "info", N.INFORMACJA, tekst,
                      [("zamknij_informacje", ST.PRZYCISKI["zamknij_komunikat"], LOKALNE_ZAMKNIJ_INFORMACJE, (), True, "lacze")], r=r)


def sprawy_nowych_plytek(stan, nowe: list) -> tuple:
    """E3-P14 (N2): dla plytek, na ktore ekran sie nie przelaczyl - ((nazwa plytki, godzina skanu, (tytuly otwartych pytan),
    (tytuly otwartych komunikatow)), ...) w kolejnosci skanow. Tylko czytanie stanu (``stan.pytania`` / ``stan.komunikaty``)."""
    wynik = []
    for p in nowe:
        pytania = tuple(q.tytul for q in stan.pytania if not q.ukryte and q.skan_id == p.skan_id)
        komunikaty = tuple(dict.fromkeys(k.tytul for k in stan.komunikaty if not k.ukryte and k.skan_id == p.skan_id))
        wynik.append((nazwa_plytki(p.numer), godzina(p.czas), pytania, komunikaty))
    return tuple(wynik)


def panel_nowego_wyniku(sprawy: tuple, r: styl.Rozmiary = styl.ZWYKLE) -> PanelUwagi:
    """E3-P14 (N2): trwaly panel "Nowy wynik czeka: Plytka n" - wynik nowej plytki przyszedl, a ekran zostal na ogladanej
    (regula A-P2). Wymienia pytania i komunikaty czekajacych plytek (technik nie przeoczy, ze nowa plytka o cos pyta);
    poziom "ostrzezenie", gdy jest o co pytac, inaczej "info". Jedyny przycisk: "Pokaz nowy wynik" (bez "Zamknij" - panel
    znika, gdy technik obejrzy plytke)."""
    nazwy = ", ".join(dict.fromkeys(s[0] for s in sprawy))
    tytul = N.NOWY_WYNIK_TYTUL.format(plytki=nazwy) if len(sprawy) == 1 else N.NOWE_WYNIKI_TYTUL.format(n=len(sprawy), plytki=nazwy)
    wiersze = []
    for nazwa, czas, pytania, komunikaty in sprawy:
        czesci = [N.NOWY_WYNIK_PYTANIE.format(tytul=t) for t in pytania] + [N.NOWY_WYNIK_KOMUNIKAT.format(tytul=t) for t in komunikaty]
        if czesci:
            wiersze.append(N.NOWY_WYNIK_SPRAWY.format(plytka=nazwa, godzina=czas or N.BRAK_DANYCH, sprawy=", ".join(czesci)))
    return PanelUwagi("panel_nowy_wynik", "ostrzezenie" if wiersze else "info", tytul, N.NOWY_WYNIK_RADA,
                      [("nowy_wynik_pokaz", N.NOWY_WYNIK_POKAZ, LOKALNE_POKAZ_NOWA, (), True, "glowny")], rada=" ".join(wiersze), r=r)


def panel_komunikatu(komunikaty: tuple, plytka: str = "", dodatek: str = "", r: styl.Rozmiary = styl.ZWYKLE) -> PanelUwagi:
    """Panel komunikatu ze stanu; ``komunikaty`` - jeden albo kilka jednakowych (ten sam rodzaj i tekst: jeden panel z licznikiem,
    "Zamknij" zamyka wszystkie). ``dodatek`` - dopisek ekranu ze stanu (np. gniazda konfliktu projektu)."""
    komunikat = komunikaty[0]
    przyciski = []
    if komunikat.rodzaj in ("pula_pusta", "pula_brak_folderu"):
        przyciski.append(("komunikat_odswiez_pule", ST.PRZYCISKI["odswiez_pule"], "odswiez_pule", (), True, None))
    if komunikat.rodzaj in ST.NAPISY_NIEZAPISANE:  # blad zapisu wynikow / baza zajeta: zapis mozna ponowic od razu
        przyciski.append(("komunikat_ponow_zapis", ST.PRZYCISKI["ponow_zapis"], "ponow_zapis", (), True, None))
    if komunikat.rodzaj == "lista_nie_zapisana":
        przyciski.append(("komunikat_zapisz_liste", ST.PRZYCISKI["zapisz_liste"], "zapisz_liste", (), True, None))
    zamknij = ST.PRZYCISKI["zamknij_komunikat"]
    if komunikat.rodzaj in ST.KOMUNIKATY_DO_PONOWIENIA:  # E3-P14 (N1): polecenie odrzucone przy zajetej bazie - ponowienie TEGO polecenia
        przyciski.append(("komunikat_ponow_polecenie", ST.PRZYCISKI["ponow_polecenie"], "ponow_polecenie", (komunikat.id,), True, "glowny"))
        zamknij = ST.PRZYCISK_REZYGNUJE  # zamkniecie = swiadoma rezygnacja z tej decyzji
    przyciski.append(("zamknij_komunikat", zamknij, "zamknij_komunikat", tuple(k.id for k in komunikaty), True, "lacze"))
    tytul = tytul_plytki(plytka, komunikat.tytul)
    if len(komunikaty) > 1:
        tytul = N.KILKA_RAZY.format(tytul=tytul, n=len(komunikaty))
    return PanelUwagi(nazwa_obiektu("komunikat", komunikat.rodzaj), komunikat.poziom, tytul, komunikat.tekst, przyciski,
                      wyjasnienie=dodatek, przyciski_pod_tekstem=False, r=r)


# ----------------------------------------------------------------------------
# lista plytek
# ----------------------------------------------------------------------------
class KafelekPlytki(QFrame):
    """Jedna plytka na liscie: numer, godzina skanu, stan plytki (napis ze stanu albo "do obejrzenia: n" / "sprawdzona"),
    znaczniki (NOWA, plytka dopuszczona, czeka na odpowiedz, ma komunikat) i liczniki prac wg koloru (z podpowiedzia)."""

    wybrano = Signal(int)

    def __init__(self, plytka, wybrana: bool, nowa: bool, z_pytaniem: bool, z_komunikatem: bool = False, r: styl.Rozmiary = styl.ZWYKLE,
                 poprzedni: bool = False):
        super().__init__()
        self.setObjectName(f"plytka_{plytka.skan_id}")
        self.setProperty("rola", "kafelek")
        self.setProperty("wybrany", "true" if wybrana else "false")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self._skan_id = plytka.skan_id
        self._liczniki = {k: n for k, n in plytka.liczniki.items() if n}
        uklad = QVBoxLayout(self)
        uklad.setContentsMargins(*((7, 3, 7, 5) if r.zwarty else (10, 6, 10, 8)))
        uklad.setSpacing(2 if r.zwarty else 3)
        wiersz = QHBoxLayout()
        wiersz.addWidget(etykieta(nazwa_plytki(plytka.numer), "naglowek", zawijaj=True), 1)  # "Plytka bez numeru" w waskiej liscie: 2 wiersze
        wiersz.addWidget(etykieta(godzina(plytka.czas), "slaby"), 0, Qt.AlignmentFlag.AlignTop)
        uklad.addLayout(wiersz)
        stan = stan_obejrzenia(plytka)
        uklad.addWidget(etykieta(stan, "slaby", "plytka_stan", zawijaj=True))
        if napis_dopuszczenia(plytka):  # dluzszy napis: wlasny wiersz z zawijaniem (waska lista)
            dopuszczona = etykieta(napis_dopuszczenia(plytka), nazwa="plytka_znacznik_dopuszczona", zawijaj=True)
            dopuszczona.setStyleSheet(styl_znaczka_poziomu("ostrzezenie", r.znaczek))
            uklad.addWidget(dopuszczona)
        znaczniki = UkladPlynny(odstep_poziomy=5, odstep_pionowy=3)
        if nowa:
            znaczniki.addWidget(znaczek(N.PLYTKA_NOWA, styl.AKCENT, "plytka_znacznik_nowa", rozmiar_px=r.znaczek))
        if poprzedni:  # E3-P14 (poz. 8): dwa kafelki z tym samym numerem - poprzedni skan nazwany napisem, nie samym kolorem
            znaczniki.addWidget(etykieta(N.PLYTKA_POPRZEDNI_SKAN, "uwaga", "plytka_znacznik_poprzedni"))
        if z_pytaniem:
            znaczniki.addWidget(etykieta(N.PLYTKA_PYTANIE, "uwaga"))
        if z_komunikatem:
            znaczniki.addWidget(etykieta(N.PLYTKA_KOMUNIKAT, "uwaga"))
        if znaczniki.count():
            uklad.addLayout(znaczniki)
        liczniki = UkladPlynny(odstep_poziomy=5, odstep_pionowy=3)
        for klasa in KLASY_LICZNIKOW:  # kolor znaczka: kolor ekranu statusu tej klasy ze ``statusy``; podpowiedz z napisem statusu
            if self._liczniki.get(klasa):
                wiersz_st = ST.status(ST.STATUS_WG_KOLORU[klasa])
                z = znaczek(str(self._liczniki[klasa]), wiersz_st.hex, rozmiar_px=r.znaczek)
                z.setToolTip(N.LICZNIK_OPIS.format(napis=wiersz_st.napis, n=self._liczniki[klasa]))
                liczniki.addWidget(z)
        for klasa, n in self._liczniki.items():
            if klasa not in KLASY_LICZNIKOW:  # klasa koloru nieznana tej wersji ekranu: kolor "nieznany" ze ``statusy``
                z = znaczek(str(n), ST.status(None).hex, rozmiar_px=r.znaczek)
                z.setToolTip(N.LICZNIK_OPIS.format(napis=ST.status(None).napis, n=n))
                liczniki.addWidget(z)
        if not self._liczniki and plytka.aktywna:
            liczniki.addWidget(etykieta(N.PLYTKA_BEZ_PRAC, "slaby"))
        if liczniki.count():
            uklad.addLayout(liczniki)

    def liczniki(self) -> dict:
        """Klasa koloru -> liczba pokazana na kafelku."""
        return dict(self._liczniki)

    def mousePressEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        if zdarzenie.button() == Qt.MouseButton.LeftButton:
            _fokus_do_okna(self)
            self.wybrano.emit(self._skan_id)

    def keyPressEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        if _do_okna(self, zdarzenie):
            return
        if zdarzenie.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if not zdarzenie.isAutoRepeat():
                self.wybrano.emit(self._skan_id)
            zdarzenie.accept()
            return
        super().keyPressEvent(zdarzenie)


class KafelekNiezapisany(QFrame):
    """Skan policzony, ale jeszcze niezapisany (``StanAplikacji.niezapisane``): numer plytki, napis ze stanu, liczba prac.
    Nie da sie go otworzyc - prace pojawia sie po udanym zapisie."""

    def __init__(self, nr: int, pozycja, r: styl.Rozmiary = styl.ZWYKLE):
        super().__init__()
        self.setObjectName(f"niezapisany_{nr}")
        tlo, pasek, _ = styl.POZIOMY["blad"]
        self.setStyleSheet(f"QFrame#niezapisany_{nr} {{ background: {tlo}; border: 2px dashed {pasek}; border-radius: 8px; }}")
        uklad = QVBoxLayout(self)
        uklad.setContentsMargins(*((7, 3, 7, 5) if r.zwarty else (10, 6, 10, 8)))
        uklad.setSpacing(2 if r.zwarty else 3)
        wiersz = QHBoxLayout()
        wiersz.addWidget(etykieta(nazwa_plytki(pozycja.numer), "naglowek", zawijaj=True), 1)
        wiersz.addWidget(etykieta(godzina(pozycja.od), "slaby"), 0, Qt.AlignmentFlag.AlignTop)
        uklad.addLayout(wiersz)
        uklad.addWidget(etykieta(pozycja.napis, "duzy", zawijaj=True))
        if pozycja.prac is not None:
            uklad.addWidget(etykieta(N.PRAC.format(n=pozycja.prac), "slaby"))


class ListaPlytek(QFrame):
    """Plytki biezacej zmiany (kafelki, najnowsza na gorze); wczesniejsze zmiany tej doby na zadanie. Na samej gorze skany
    policzone, ktorych wyniku nie udalo sie jeszcze zapisac ("nie zapisano") z przyciskiem "Ponow zapis". Pod naglowkiem
    (poza przewijaniem) przycisk "Pokaz nowy wynik" - plytki, na ktore ekran sie nie przelaczyl (A-P2)."""

    wybrano = Signal(int)
    przelacz_wczesniejsze = Signal()
    ponow_zapis = Signal()
    pokaz_nowa = Signal()

    def __init__(self):
        super().__init__()
        self.setProperty("rola", "panel")
        self.setObjectName("lista_plytek")
        self.setFixedWidth(styl.ZWYKLE.szerokosc_listy_plytek)
        self._uklad = QVBoxLayout(self)
        self._uklad.setContentsMargins(8, 8, 8, 8)
        self._uklad.setSpacing(6)
        self._uklad.addWidget(etykieta(N.PLYTKI_ZMIANY, "naglowek"))
        self.przycisk_nowa = przycisk("", "przycisk_nowa_plytka", "nowa", self.pokaz_nowa.emit)
        self.przycisk_nowa.setVisible(False)
        self._uklad.addWidget(self.przycisk_nowa)
        self._nowe = None
        self._przewijanie = QScrollArea()
        self._przewijanie.setWidgetResizable(True)
        self._przewijanie.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._przewijanie.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        wnetrze = QWidget()
        wnetrze.setObjectName("lista_plytek_wnetrze")
        wnetrze.setStyleSheet("QWidget#lista_plytek_wnetrze { background: transparent; }")  # tylko to tlo, nie kafelki (zaznaczenie)
        self._kafelki = QVBoxLayout(wnetrze)
        self._kafelki.setContentsMargins(0, 0, 0, 0)
        self._kafelki.setSpacing(6)
        self._przewijanie.setWidget(wnetrze)
        self._uklad.addWidget(self._przewijanie, 1)
        self._sygnatura = None
        self._r = styl.ZWYKLE

    def ustaw_tryb(self, r: styl.Rozmiary) -> None:
        self._r = r
        self.setFixedWidth(r.szerokosc_listy_plytek)
        self._uklad.setContentsMargins(*((5, 5, 5, 5) if r.zwarty else (8, 8, 8, 8)))
        self._uklad.setSpacing(4 if r.zwarty else 6)
        self._kafelki.setSpacing(4 if r.zwarty else 6)
        self._sygnatura = None

    def ustaw_nowe(self, plytka: str | None, ile: int) -> None:
        """"Pokaz nowy wynik: Plytka n" - najnowsza plytka, na ktora ekran sie nie przelaczyl (``ile`` takich plytek)."""
        nowe = (plytka, ile)
        if nowe == self._nowe:
            return
        self._nowe = nowe
        if plytka is not None:
            self.przycisk_nowa.setText(N.NOWA_PLYTKA.format(plytka=plytka) if ile <= 1 else N.NOWE_PLYTKI.format(n=ile, plytka=plytka))
        self.przycisk_nowa.setVisible(plytka is not None)

    def ustaw(self, plytki: list, wybrana: int | None, nowe: set, z_pytaniem: set, wczesniejszych: int, pokazane_wczesniejsze: bool,
              niezapisane: tuple = (), z_komunikatem: set = frozenset(), poprzednie: set = frozenset()) -> None:
        """``poprzednie`` - skany, ktore otwarte pytanie o ponowny skan proponuje zastapic (znacznik "poprzedni skan tej plytki")."""
        sygnatura = (tuple((p.skan_id, p.numer, p.napis, p.czas, p.aktywna, p.dopuszczona, p.typ, tuple(sorted(p.liczniki.items())), stan_obejrzenia(p))
                           for p in plytki), wybrana, frozenset(nowe), frozenset(z_pytaniem), frozenset(z_komunikatem), wczesniejszych,
                     pokazane_wczesniejsze, tuple(niezapisane), frozenset(poprzednie))
        if sygnatura == self._sygnatura:
            return
        self._sygnatura = sygnatura
        wyczysc(self._kafelki)
        for nr, pozycja in enumerate(reversed(niezapisane)):
            self._kafelki.addWidget(KafelekNiezapisany(nr, pozycja, self._r))
        if niezapisane:
            self._kafelki.addWidget(przycisk(ST.PRZYCISKI["ponow_zapis"], "przycisk_ponow_zapis", None, self.ponow_zapis.emit))
        if not plytki and not niezapisane:
            self._kafelki.addWidget(etykieta(N.PLYTKI_BRAK, "slaby", zawijaj=True))
        for p in reversed(plytki):  # najnowsza na gorze
            kafelek = KafelekPlytki(p, p.skan_id == wybrana, p.skan_id in nowe, p.skan_id in z_pytaniem, p.skan_id in z_komunikatem, self._r,
                                    poprzedni=p.skan_id in poprzednie)
            kafelek.wybrano.connect(self.wybrano.emit)
            self._kafelki.addWidget(kafelek)
        if wczesniejszych:
            napis = N.WCZESNIEJSZE_UKRYJ if pokazane_wczesniejsze else N.WCZESNIEJSZE_POKAZ.format(n=wczesniejszych)
            self._kafelki.addWidget(przycisk(napis, "przycisk_wczesniejsze", "lacze", self.przelacz_wczesniejsze.emit))
        self._kafelki.addStretch(1)


# ----------------------------------------------------------------------------
# widok pracy
# ----------------------------------------------------------------------------
class ObrazPracy(QLabel):
    """Obraz odchylek skalowany do wolnego miejsca (albo napis, gdy obrazu nie ma)."""

    def __init__(self):
        super().__init__()
        self.setObjectName("praca_obraz")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(300, styl.ZWYKLE.obraz_min)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.setStyleSheet(f"background: #ffffff; border: 1px solid {styl.RAMKA}; border-radius: 4px; color: {styl.TEKST_SLABY};")
        self._oryginal: QPixmap | None = None

    def ustaw_obraz(self, obraz) -> None:
        self._oryginal = QPixmap.fromImage(obraz) if obraz is not None else None
        self._dopasuj()

    def ustaw_napis(self, napis: str) -> None:
        self._oryginal = None
        self.setPixmap(QPixmap())
        self.setText(napis)

    def _dopasuj(self) -> None:
        if self._oryginal is None:
            return
        cel = QSize(max(100, self.width() - 4), max(40, self.height() - 4))
        self.setPixmap(self._oryginal.scaled(cel, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def resizeEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        super().resizeEvent(zdarzenie)
        self._dopasuj()


class WidokPracy(QFrame):
    """Widok jednej pracy: naglowek "Plytka n - gniazdo m" (duzy - A-P2), status i opis ze stanu, kuweta / zab / krazek,
    rozmiar najwiekszego ubytku i liczba ubytkow, obraz odchylek, "ten zab jest juz na liscie", duze przyciski decyzji.
    Gdy nic nie jest wybrane - podpowiedz, co kliknac. ``praca_id`` - praca, ktorej dane sa pokazane (do niej idzie decyzja)."""

    decyzja = Signal(str)  # ukruszona / ok / cofnij
    zamknij = Signal()
    nastepna = Signal()
    inna_praca = Signal()
    wybor_wpisu = Signal(int)  # E3-A5i: frezowanie_id krazka wybranego przez technika (``Praca.wpisy_do_wyboru``)
    cofnij_wpis = Signal()  # E3-A5i runda 2 (D9): cofniecie wyboru krazka

    def __init__(self):
        super().__init__()
        self.setProperty("rola", "panel")
        self.setObjectName("ramka_pracy")
        self.praca_id: int | None = None
        self._r = styl.ZWYKLE
        self._stos = QStackedLayout(self)
        self._stos.setContentsMargins(0, 0, 0, 0)
        self._pusty = etykieta(N.PRACA_PUSTY_WIDOK, "duzy", "praca_pusty_widok", zawijaj=True)
        self._pusty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._pusty.setContentsMargins(30, 20, 30, 20)
        self._pusty.setMinimumSize(10, 10)
        self._pusty.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self._stos.addWidget(self._pusty)
        self._widok = QWidget()
        self._widok.setObjectName("widok_pracy")
        self._stos.addWidget(self._widok)
        self._u = u = QVBoxLayout(self._widok)
        u.setContentsMargins(14, 10, 14, 12)
        u.setSpacing(6)
        wiersz = QHBoxLayout()
        wiersz.setSpacing(10)
        self.tytul = etykieta("", "tytul", "praca_tytul", zawijaj=True)
        self.z_dwoch = przycisk("", "przycisk_inna_praca", "lacze", self.inna_praca.emit)
        wiersz.addWidget(self.tytul, 1)
        wiersz.addWidget(self.z_dwoch, 0, Qt.AlignmentFlag.AlignTop)
        u.addLayout(wiersz)
        wiersz = QHBoxLayout()
        wiersz.setSpacing(10)
        self.status = znaczek("", "#ffffff", "praca_status", 18)
        self.opis = etykieta("", nazwa="praca_opis", zawijaj=True)
        wiersz.addWidget(self.status, 0, Qt.AlignmentFlag.AlignTop)
        wiersz.addWidget(self.opis, 1)
        u.addLayout(wiersz)
        self._dane_uklad = wiersz = QHBoxLayout()
        wiersz.setSpacing(6)
        self.dane = {}
        for klucz, podpis in (("kuweta", N.KUWETA), ("zeby", N.ZAB), ("krazek", N.KRAZEK)):
            wiersz.addWidget(etykieta(podpis, "podpis"))
            self.dane[klucz] = etykieta("", "duzy", f"praca_{klucz}")
            wiersz.addWidget(self.dane[klucz])
            wiersz.addSpacing(18)
        wiersz.addStretch(1)
        u.addLayout(wiersz)
        # E3-A5i: krazek do wyboru (wynik puli per praca nierozstrzygniety) - przycisk na kazdy wpis puli
        self._wpisy_pole = QWidget()
        self._wpisy_pole.setObjectName("praca_wpisy_do_wyboru")
        self._wpisy_uklad = QHBoxLayout(self._wpisy_pole)
        self._wpisy_uklad.setContentsMargins(0, 0, 0, 0)
        self._wpisy_uklad.setSpacing(8)
        self._wpisy_uklad.addWidget(etykieta(N.KRAZEK_DO_WYBORU, "podpis"))
        self._wpisy_przyciski: list[QPushButton] = []
        self._wpisy_uklad.addStretch(1)
        self.przycisk_cofnij_wpis = przycisk(N.KRAZEK_COFNIJ, "przycisk_cofnij_wpis", "lacze", self.cofnij_wpis.emit)
        self._wpisy_uklad.addWidget(self.przycisk_cofnij_wpis)
        self._wpisy_pole.setVisible(False)
        u.addWidget(self._wpisy_pole)
        self.ubytek = etykieta("", "duzy", "praca_ubytek", zawijaj=True)
        u.addWidget(self.ubytek)
        self.obraz = ObrazPracy()
        u.addWidget(self.obraz, 1)
        self.opis_obrazu = etykieta(N.OBRAZ_OPIS, "slaby", "praca_opis_obrazu", zawijaj=True)
        u.addWidget(self.opis_obrazu)
        self.na_liscie = etykieta("", "informacja", "praca_na_liscie", zawijaj=True)
        u.addWidget(self.na_liscie)
        self.zapisana = etykieta("", "slaby", "praca_decyzja", zawijaj=True)
        u.addWidget(self.zapisana)
        self.wyjasnienie = etykieta("", "uwaga", "praca_wyjasnienie", zawijaj=True)
        u.addWidget(self.wyjasnienie)
        self._decyzje = wiersz = QHBoxLayout()
        wiersz.setSpacing(12)
        self.przyciski = {}
        self._kolory_decyzji = {}
        for polecenie, status_koloru, klawisz in (("ukruszona", "ukruszona", N.KLAWISZ_UKRUSZONA), ("ok", "zatwierdzona_ok", N.KLAWISZ_OK)):
            b = przycisk(N.SKROT.format(napis=ST.PRZYCISKI[polecenie], klawisz=klawisz), f"przycisk_{polecenie}", None,
                         lambda p=polecenie: self.decyzja.emit(p), styl.ZWYKLE.wysokosc_decyzji)
            self._kolory_decyzji[polecenie] = ST.STATUSY[status_koloru].hex  # kolor = kolor gniazda po tej decyzji (ze ``statusy``)
            b.setStyleSheet(styl.przycisk_w_kolorze(self._kolory_decyzji[polecenie], styl.ZWYKLE))
            self.przyciski[polecenie] = b
            wiersz.addWidget(b, 1)
        u.addLayout(wiersz)
        self._drugi = wiersz = QHBoxLayout()
        wiersz.setSpacing(10)
        wys = styl.ZWYKLE.wysokosc_drugiego_rzedu
        self.przyciski["cofnij"] = przycisk(N.SKROT.format(napis=ST.PRZYCISKI["cofnij"], klawisz=N.KLAWISZ_COFNIJ), "przycisk_cofnij", None,
                                            lambda: self.decyzja.emit("cofnij"), wys)
        self.przycisk_nastepna = przycisk(N.NASTEPNA, "przycisk_nastepna", "lacze", self.nastepna.emit, wys)
        self.przycisk_nastepna.setToolTip(N.NASTEPNA_OPIS)
        self.przycisk_zamknij = przycisk(N.ZAMKNIJ_PRACE, "przycisk_zamknij_prace", "lacze", self.zamknij.emit, wys)
        wiersz.addWidget(self.przyciski["cofnij"], 3)
        wiersz.addWidget(self.przycisk_nastepna, 2)
        wiersz.addWidget(self.przycisk_zamknij, 2)
        u.addLayout(wiersz)
        self._sygnatura = None

    def ustaw_tryb(self, r: styl.Rozmiary) -> None:
        self._r = r
        self._u.setContentsMargins(*((10, 5, 10, 6) if r.zwarty else (14, 10, 14, 12)))
        self._u.setSpacing(2 if r.zwarty else 6)
        self._pusty.setContentsMargins(*((16, 10, 16, 10) if r.zwarty else (30, 20, 30, 20)))
        self._decyzje.setSpacing(8 if r.zwarty else 12)
        self._drugi.setSpacing(6 if r.zwarty else 10)
        for polecenie in ("ukruszona", "ok"):
            self.przyciski[polecenie].setMinimumHeight(r.wysokosc_decyzji)
            self.przyciski[polecenie].setStyleSheet(styl.przycisk_w_kolorze(self._kolory_decyzji[polecenie], r))
        for b in (self.przyciski["cofnij"], self.przycisk_nastepna, self.przycisk_zamknij):
            b.setMinimumHeight(r.wysokosc_drugiego_rzedu)
        self.obraz.setMinimumSize(200 if r.zwarty else 300, r.obraz_min)
        self._sygnatura = None

    def otwarty(self) -> bool:
        return self._stos.currentIndex() == 1

    def minimumSizeHint(self) -> QSize:  # noqa: N802 - nazwa Qt
        """Otwarty widok pracy potrzebuje tyle wysokosci, ile zajmuja zawiniete napisy przy obecnej szerokosci (zwykle minimum
        ukladu liczy je w jednej linii) - inaczej przyciski decyzji wchodzilyby na drugi rzad przyciskow (A-P1)."""
        s = super().minimumSizeHint()
        if self.otwarty():
            u = self._widok.layout()
            s.setHeight(max(s.height(), u.minimumHeightForWidth(max(200, self.width()))))
        return s

    def aktywny(self, polecenie: str) -> bool:
        return self.otwarty() and self.przyciski[polecenie].isEnabled()

    def przyciski_wpisow(self) -> list:
        """E3-A5i: przyciski krazkow do wyboru pokazanej pracy (puste, gdy wynik rozstrzygniety)."""
        return list(self._wpisy_przyciski)

    def _ustaw_wpisy(self, praca, jest_osoba: bool) -> None:
        """Przyciski krazkow ``Praca.wpisy_do_wyboru``: napis = krazek (wybrany - z dopiskiem), klik = ``wybor_wpisu(frezowanie_id)``."""
        wpisy = tuple(getattr(praca, "wpisy_do_wyboru", ()) or ()) if praca is not None else ()
        for b in self._wpisy_przyciski:
            self._wpisy_uklad.removeWidget(b)
            b.deleteLater()
        self._wpisy_przyciski = []
        mozna = praca is not None and "wybierz_wpis" in praca.dozwolone and jest_osoba
        for nr, w in enumerate(wpisy):
            tekst = w.krazek or str(w.frezowanie_id)
            b = przycisk(N.KRAZEK_WYBRANY.format(krazek=tekst) if w.wybrany else tekst, f"przycisk_wpis_{w.frezowanie_id}", "lacze",
                         lambda f=w.frezowanie_id: self.wybor_wpisu.emit(int(f)))
            b.setToolTip(N.KRAZEK_PODPOWIEDZ.format(wspolczynnik=w.wspolczynnik if w.wspolczynnik is not None else N.BRAK_DANYCH))
            b.setEnabled(mozna)
            self._wpisy_uklad.insertWidget(1 + nr, b)
            self._wpisy_przyciski.append(b)
        self.przycisk_cofnij_wpis.setVisible(praca is not None and "cofnij_wpis" in praca.dozwolone)
        self.przycisk_cofnij_wpis.setEnabled(jest_osoba)
        self._wpisy_pole.setVisible(bool(wpisy))

    def wyczysc(self) -> None:
        if self.otwarty():
            self._stos.setCurrentIndex(0)
            self.updateGeometry()
        self._sygnatura = None
        self.praca_id = None

    def ustaw(self, stan, plytka, gniazdo, praca, nr_pracy: int, jest_nastepna: bool) -> None:
        """``gniazdo`` - ``Gniazdo`` ze stanu albo None (praca poza gniazdem); ``praca`` - pokazywana ``Praca`` albo None
        (puste gniazdo); ``nr_pracy`` - ktora praca gniazda (od 0), gdy leza w nim dwie."""
        sygnatura = (plytka.skan_id, plytka.napis, plytka.numer, gniazdo, praca, nr_pracy, stan.operator, stan.operatorzy, jest_nastepna)
        self._stos.setCurrentIndex(1)
        self.praca_id = praca.praca_id if praca is not None else None
        if sygnatura == self._sygnatura:
            return
        self._sygnatura = sygnatura
        zrodlo = gniazdo if gniazdo is not None and (praca is None or len(gniazdo.prace) > 1) else praca  # dwie prace: status gniazda
        nazwa = nazwa_plytki(plytka.numer)
        self.tytul.setText(N.PRACA_TYTUL.format(plytka=nazwa, gniazdo=gniazdo.nr) if gniazdo is not None else N.PRACA_TYTUL_POZA.format(plytka=nazwa))
        self.status.setText(zrodlo.podpis)
        self.status.setVisible(bool(zrodlo.podpis))
        self.status.setStyleSheet(_styl_znaczka(zrodlo.rgb, self._r.status_pracy))
        ile = len(gniazdo.prace) if gniazdo is not None else 1
        self.z_dwoch.setVisible(ile > 1)
        self.z_dwoch.setText(N.PRACA_Z_DWOCH.format(nr=nr_pracy + 1, ile=ile))
        opis = ST.status(zrodlo.status).opis if zrodlo is gniazdo else praca.opis
        self.opis.setText(opis)
        for klucz, pole in self.dane.items():
            pole.setText((getattr(praca, klucz) if praca is not None else None) or N.BRAK_DANYCH)
        if praca is not None and praca.ubytki:
            czesci = ([N.NAJWIEKSZY_UBYTEK.format(mm=liczba_mm(praca.ubytek_max_mm))] if praca.ubytek_max_mm is not None else [])
            self.ubytek.setText(N.ODSTEP.join(czesci + [N.LICZBA_UBYTKOW.format(n=praca.ubytki)]))
        else:
            self.ubytek.setText(N.BEZ_UBYTKOW if praca is not None else "")
        self.ubytek.setVisible(praca is not None)
        tekst_listy = praca.na_liscie.tekst if praca is not None and praca.na_liscie is not None else ""
        self.na_liscie.setText(tekst_listy)
        self.na_liscie.setVisible(bool(tekst_listy))
        if praca is not None and praca.decyzja:
            nazwa_decyzji = ST.PRZYCISKI["ok"] if praca.decyzja == "ok" else ST.PRZYCISKI["ukruszona"]
            if praca.decyzja == "ukruszona_niewykryta":
                nazwa_decyzji = N.DECYZJA_NIEWYKRYTA.format(decyzja=nazwa_decyzji)
            self.zapisana.setText(N.DECYZJA_ZAPISANA.format(decyzja=nazwa_decyzji, osoba=praca.operator or N.BRAK_DANYCH,
                                                            godzina=godzina(praca.czas_decyzji)))
        self.zapisana.setVisible(praca is not None and bool(praca.decyzja))
        dozwolone = praca.dozwolone if praca is not None else ()
        jest_osoba = stan.operator is not None
        for polecenie, b in self.przyciski.items():
            b.setEnabled(polecenie in dozwolone and jest_osoba)
            b.setVisible(praca is not None)
        self._ustaw_wpisy(praca, jest_osoba)
        if praca is None:
            wyjasnienie = ""
        elif not dozwolone:
            wyjasnienie = N.DECYZJE_NIEDOSTEPNE.format(napis=plytka.napis)
        elif not stan.operatorzy:
            wyjasnienie = ST.tekst_komunikatu("pusta_lista_operatorow")[2]
        elif not jest_osoba:
            wyjasnienie = ST.tekst_komunikatu("brak_operatora")[2]
        else:
            wyjasnienie = ""
        self.wyjasnienie.setText(wyjasnienie)
        self.wyjasnienie.setVisible(bool(wyjasnienie))
        self.przycisk_nastepna.setEnabled(jest_nastepna)
        self.obraz.setVisible(praca is not None)
        self.opis_obrazu.setVisible(praca is not None)
        self.updateGeometry()  # wysokosc widoku zalezy od napisow (``minimumSizeHint``)


# ----------------------------------------------------------------------------
# lista "do dofrezowania"
# ----------------------------------------------------------------------------
class ListaDofrezowania(QFrame):
    """Lista "do dofrezowania": kuweta, zab, krazek, plytka i gniazdo, doba i zmiana; filtr "ta doba" / "wszystkie otwarte"."""

    filtr = Signal(bool)  # True = wszystkie otwarte
    wybrano = Signal(object)  # PozycjaListy
    zapisz = Signal()

    def __init__(self):
        super().__init__()
        self.setProperty("rola", "panel")
        self.setObjectName("lista_dofrezowania")
        self._uklad = uklad = QVBoxLayout(self)
        uklad.setContentsMargins(12, 8, 12, 10)
        uklad.setSpacing(6)
        wiersz = QHBoxLayout()
        wiersz.setSpacing(8)
        self.tytul = etykieta("", "naglowek", "lista_tytul")
        wiersz.addWidget(self.tytul)
        wiersz.addStretch(1)
        self.ta_doba = przycisk(N.LISTA_TA_DOBA, "lista_ta_doba", None, lambda: self.filtr.emit(False))
        self.wszystkie = przycisk(N.LISTA_WSZYSTKIE, "lista_wszystkie", None, lambda: self.filtr.emit(True))
        for b in (self.ta_doba, self.wszystkie):
            b.setCheckable(True)
            wiersz.addWidget(b)
        uklad.addLayout(wiersz)
        self.tabela = QTableWidget(0, len(N.KOLUMNY_LISTY))
        self.tabela.setObjectName("tabela_dofrezowania")
        self.tabela.setHorizontalHeaderLabels(list(N.KOLUMNY_LISTY))
        self.tabela.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tabela.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela.horizontalHeader().setSectionsClickable(False)
        self.tabela.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tabela.cellClicked.connect(self._klik)
        uklad.addWidget(self.tabela, 1)
        wiersz = QHBoxLayout()
        self.pusta = etykieta(N.LISTA_PUSTA, "slaby", "lista_pusta")
        self.zapisano = etykieta("", "slaby", "lista_zapisano")
        wiersz.addWidget(self.pusta)
        wiersz.addWidget(self.zapisano)
        wiersz.addStretch(1)
        # polecenie ``zapisz_liste``; lista zapisuje sie tez sama po kazdej zmianie (``StanAplikacji.lista_zapisana``)
        wiersz.addWidget(przycisk(ST.PRZYCISKI["zapisz_liste"], "przycisk_zapisz_liste", "lacze", self.zapisz.emit))
        uklad.addLayout(wiersz)
        self._pozycje: tuple = ()
        self._sygnatura = None
        self.ustaw_tryb(styl.ZWYKLE)

    def ustaw_tryb(self, r: styl.Rozmiary) -> None:
        self._uklad.setContentsMargins(*((8, 4, 8, 5) if r.zwarty else (12, 8, 12, 10)))
        self._uklad.setSpacing(3 if r.zwarty else 6)
        self.tabela.verticalHeader().setDefaultSectionSize(r.wiersz_tabeli)
        naglowek = r.naglowek_tabeli + (8 if r.zwarty else 14)
        self.tabela.setMinimumHeight(naglowek + 2 * r.wiersz_tabeli)  # naglowek i dwie pozycje zawsze widoczne, reszta przewijana

    def ustaw(self, pozycje: tuple, wszystkie: bool, zapisana: str | None = None) -> None:
        sygnatura = (pozycje, wszystkie, zapisana)
        if sygnatura == self._sygnatura:
            return
        self._sygnatura = sygnatura
        self._pozycje = tuple(pozycje)
        self.tytul.setText(N.LISTA_TYTUL.format(n=len(pozycje)))
        self.ta_doba.setChecked(not wszystkie)
        self.wszystkie.setChecked(wszystkie)
        self.tabela.setRowCount(len(pozycje))
        for r, x in enumerate(pozycje):
            zab = x.zeby or N.BRAK_DANYCH
            if x.powtorzenia:
                zab = f"{zab}  ({N.POWTORZONY.format(n=x.powtorzenia + 1)})"
            komorki = (x.kuweta or N.BRAK_DANYCH, zab, x.krazek or N.BRAK_DANYCH, str(x.numer_plytki) if x.numer_plytki is not None else N.BRAK_DANYCH,
                       str(x.gniazdo) if x.gniazdo is not None else N.BRAK_DANYCH, dzien(x.doba), str(x.zmiana))
            for k, tekst in enumerate(komorki):
                pole = QTableWidgetItem(tekst)
                pole.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabela.setItem(r, k, pole)
        self.tabela.clearSelection()
        self.pusta.setVisible(not pozycje)
        self.zapisano.setText(N.LISTA_PLIK.format(godzina=godzina(zapisana)) if zapisana else "")  # bez nazwy pliku
        self.zapisano.setVisible(bool(zapisana))

    def _klik(self, wiersz: int, _kolumna: int) -> None:
        if 0 <= wiersz < len(self._pozycje):
            self.wybrano.emit(self._pozycje[wiersz])


# ----------------------------------------------------------------------------
# legenda mapy
# ----------------------------------------------------------------------------
class Legenda(QWidget):
    """Pasek pod mapa: kolory i podpisy statusow, ktore SA na pokazanej plytce (wprost ze stanu). Na plytce, ktora niczego
    nie potwierdza, legenda nie pokazuje wiec zielonego. Ten sam podpis i kolor = jeden znaczek (opisy razem w podpowiedzi)."""

    def __init__(self):
        super().__init__()
        self.setObjectName("legenda")
        self._uklad = UkladPlynny(self, odstep_poziomy=8, odstep_pionowy=4)
        self._sygnatura = None
        self._r = styl.ZWYKLE

    def ustaw_tryb(self, r: styl.Rozmiary) -> None:
        self._r = r
        self._sygnatura = None

    def ustaw(self, plytka) -> None:
        pozycje: dict = {}
        for g in (plytka.gniazda if plytka is not None else ()):
            if g.prace and g.podpis:
                opisy = pozycje.setdefault((g.podpis, g.rgb), [])
                if ST.status(g.status).opis not in opisy:
                    opisy.append(ST.status(g.status).opis)
        sygnatura = (tuple((k, tuple(v)) for k, v in pozycje.items()), self._r.zwarty)
        if sygnatura == self._sygnatura:
            return
        self._sygnatura = sygnatura
        wyczysc(self._uklad)
        if pozycje:
            self._uklad.addWidget(etykieta(N.LEGENDA, "slaby"))
        for (podpis, rgb), opisy in pozycje.items():
            z = znaczek(podpis, rgb, rozmiar_px=self._r.znaczek)
            z.setToolTip("\n".join(opisy))
            self._uklad.addWidget(z)
