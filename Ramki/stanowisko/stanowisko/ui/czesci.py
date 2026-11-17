"""czesci - elementy ekranu wieczornego: pasek stanu, wybor osoby, panele pytan i komunikatow, lista plytek, widok pracy,
lista "do dofrezowania".

Kazdy element dostaje gotowe dane ze stanu kontrolera (``ustaw(...)``) i oddaje wybor technika sygnalem - sam nie wola
kontrolera i niczego nie liczy. Kolory i napisy statusow pochodza z pol stanu (``rgb``, ``podpis``, ``opis``, ``napis``)
i ze ``statusy``; pozostale napisy z ``napisy``. Zaden element nie przyjmuje klawiatury (``NoFocus``) - klawisze
obsluguje okno, dzieki czemu Spacja jest zawsze startem skanu, a nie "kliknieciem" ostatnio uzytego przycisku.
"""
from __future__ import annotations

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QAbstractItemView, QFrame, QHBoxLayout, QHeaderView, QLabel, QProgressBar, QPushButton, QScrollArea,
                               QSizePolicy, QStackedLayout, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

from .. import statusy as ST
from . import napisy as N
from . import styl

# polecenia, ktore kontroler przyjmuje tylko od wybranej osoby (reszta: zamkniecie pytania / komunikatu, pula, start skanu)
BEZ_OSOBY = ("zamknij_pytanie", "zamknij_komunikat", "odswiez_pule", "start_skanu", "wybierz_operatora", "ustaw_pule", "zamknij")
# "polecenia" przyciskow, ktore obsluguje samo okno (nie ida do kontrolera)
LOKALNE_NUMER_BEZ_ZMIAN = "_numer_bez_zmian"
LOKALNE_ZAMKNIJ_ODPOWIEDZ = "_zamknij_odpowiedz"
KLASY_LICZNIKOW = (ST.KOLOR_CZERWONY, ST.KOLOR_ZOLTY, ST.KOLOR_POMARANCZOWY, ST.KOLOR_SZARY, ST.KOLOR_ZATWIERDZONA_OK, ST.KOLOR_ZIELONY)


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


def przycisk(tekst: str, nazwa: str | None = None, rola: str | None = None, po_kliknieciu=None, wysokosc: int | None = None) -> QPushButton:
    b = QPushButton(tekst)
    b.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # klawiatura nalezy do okna (Spacja = start skanu)
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
    """Usuwa wszystko z ukladu od razu (widzety odlaczone od okna, zanim Qt je skasuje)."""
    while uklad.count():
        pozycja = uklad.takeAt(0)
        w = pozycja.widget()
        if w is not None:
            w.setParent(None)
            w.deleteLater()
        elif pozycja.layout() is not None:
            wyczysc(pozycja.layout())


def znaczek(tekst: str, hex_: str, nazwa: str | None = None, rozmiar_px: int = 15) -> QLabel:
    """Maly prostokat w kolorze ``hex_`` (kolor podaje wolajacy - ze stanu albo ze ``statusy``) z napisem."""
    e = etykieta(tekst, nazwa=nazwa)
    e.setAlignment(Qt.AlignmentFlag.AlignCenter)
    e.setStyleSheet(f"background: {hex_}; color: {styl.tekst_na(hex_)}; border: 1px solid #3a4047; border-radius: 5px; "
                    f"padding: 2px 8px; font-size: {rozmiar_px}px; font-weight: 700;")
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


# ----------------------------------------------------------------------------
# pasek stanu
# ----------------------------------------------------------------------------
class PasekStanu(QFrame):
    """Tryb, doba robocza i zmiana, osoba, pula projektow z "Odswiez pule", skaner, analiza z postepem i kolejka, "Skanuj"."""

    skanuj = Signal()
    odswiez_pule = Signal()
    zmien_osobe = Signal()

    def __init__(self):
        super().__init__()
        self.setProperty("rola", "pasek")
        self.setObjectName("pasek_stanu")
        uklad = QHBoxLayout(self)
        uklad.setContentsMargins(14, 8, 14, 8)
        uklad.setSpacing(22)
        self.tryb = self._pole(uklad, N.TRYB, "napis_tryb")
        self.doba = self._pole(uklad, N.DOBA, "napis_doba")
        self.osoba = self._pole(uklad, N.OSOBA, "napis_osoba", przycisk(N.ZMIEN_OSOBE, "przycisk_zmien_osobe", "lacze", self.zmien_osobe.emit))
        self.przycisk_puli = przycisk(ST.PRZYCISKI["odswiez_pule"], "przycisk_odswiez_pule", None, self.odswiez_pule.emit)
        self.postep_puli = QProgressBar()  # liczenie puli trwa: pasek bez konca, przycisk nieaktywny
        self.postep_puli.setObjectName("pasek_puli")
        self.postep_puli.setRange(0, 0)
        self.postep_puli.setTextVisible(False)
        self.postep_puli.setFixedWidth(70)
        self.postep_puli.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.pula = self._pole(uklad, N.PULA, "napis_pula", self.przycisk_puli, self.postep_puli)
        self.skaner = self._pole(uklad, N.SKANER, "napis_skaner")
        kolumna = QVBoxLayout()
        kolumna.setSpacing(2)
        kolumna.addWidget(etykieta(N.ANALIZA, "podpis"))
        wiersz = QHBoxLayout()
        wiersz.setSpacing(8)
        self.analiza = etykieta("", "wartosc", "napis_analiza")
        self.postep = QProgressBar()
        self.postep.setObjectName("pasek_postepu")
        self.postep.setRange(0, 100)
        self.postep.setTextVisible(False)  # procent jest w napisie obok
        self.postep.setFixedWidth(120)
        self.postep.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.kolejka = etykieta("", "slaby", "napis_kolejka")
        wiersz.addWidget(self.analiza)
        wiersz.addWidget(self.postep)
        wiersz.addWidget(self.kolejka)
        wiersz.addStretch(1)
        kolumna.addLayout(wiersz)
        uklad.addLayout(kolumna, 1)
        self.przycisk_skanuj = przycisk(ST.PRZYCISKI["start_skanu"], "przycisk_skanuj", "glowny", self.skanuj.emit, 52)
        self.przycisk_skanuj.setMinimumWidth(190)
        uklad.addWidget(self.przycisk_skanuj)
        self._sygnatura = None

    @staticmethod
    def _pole(uklad: QHBoxLayout, podpis: str, nazwa: str, *dodatki: QWidget) -> QLabel:
        kolumna = QVBoxLayout()
        kolumna.setSpacing(2)
        kolumna.addWidget(etykieta(podpis, "podpis"))
        wiersz = QHBoxLayout()
        wiersz.setSpacing(10)
        wartosc = etykieta("", "wartosc", nazwa)
        wiersz.addWidget(wartosc)
        for dodatek in dodatki:
            wiersz.addWidget(dodatek)
        kolumna.addLayout(wiersz)
        uklad.addLayout(kolumna)
        return wartosc

    def ustaw(self, stan) -> None:
        sk, kol, an = stan.skaner, stan.kolejka, stan.analiza
        sygnatura = (stan.tryb, stan.doba, stan.zmiana, stan.operator, stan.operatorzy, stan.wymaga_operatora, stan.pula.napis, stan.pula.stan,
                     sk.dostepny, sk.dziala, sk.zajete, sk.czeka_na_skan, kol.czeka, kol.wstrzymane, kol.w_toku, kol.silnik_gotowy,
                     None if an is None else round(an.udzial * 100), stan.zamkniety)
        if sygnatura == self._sygnatura:
            return
        self._sygnatura = sygnatura
        self.tryb.setText(ST.NAZWY_TRYBOW.get(stan.tryb, stan.tryb))
        self.doba.setText(N.DOBA_I_ZMIANA.format(doba=dzien(stan.doba, rok=True), zmiana=stan.zmiana))
        self.osoba.setText(stan.operator or N.OSOBA_BRAK)
        self._rola(self.osoba, "wartosc" if stan.operator else "uwaga")
        self.findChild(QPushButton, "przycisk_zmien_osobe").setVisible(stan.operator is not None)
        # napis puli ze stanu (takze dla stanu, ktorego ta wersja ekranu nie zna); folder puli jest ustawieniem i nie jest pokazywany
        self.pula.setText(stan.pula.napis or ST.STANY_PULI.get(stan.pula.stan, ""))
        self._rola(self.pula, "wartosc" if stan.pula.stan in ("gotowa", "liczenie") else "uwaga")
        liczenie = stan.pula.stan == "liczenie"
        self.przycisk_puli.setEnabled(not liczenie)  # odswiezanie trwa: drugie klikniecie nic by nie dalo
        self.postep_puli.setVisible(liczenie)
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
        self._rola(self.skaner, "wartosc" if sk.dostepny and sk.dziala else "uwaga")
        self.postep.setVisible(an is not None)
        if an is not None:
            procent = max(0, min(100, round(an.udzial * 100)))
            self.postep.setValue(procent)
            self.analiza.setText(N.ANALIZA_TRWA.format(procent=procent))
        else:
            self.analiza.setText(N.ANALIZA_CZEKA if kol.razem else N.ANALIZA_BRAK)
        czesci = [N.KOLEJKA.format(n=kol.czeka)] if kol.czeka else []
        if kol.wstrzymane:  # skany wstrzymane CZEKAJA (na pule projektow albo na analize) - to nie blad
            czeka_na_pule = stan.pula.stan != "gotowa"
            czesci.append((N.WSTRZYMANE_PULA if czeka_na_pule else N.WSTRZYMANE_ANALIZA).format(n=kol.wstrzymane))
        self.kolejka.setText(", ".join(czesci))
        self.kolejka.setVisible(bool(czesci))

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

    def __init__(self, operatorzy: tuple, obecna: str | None, teksty: list, zmiana_osoby: bool, wylogowanie: bool = False):
        super().__init__()
        self.setObjectName("panel_osoba")
        tlo, pasek, _ = styl.POZIOMY["info" if zmiana_osoby else "ostrzezenie"]
        self.setStyleSheet(f"QFrame#panel_osoba {{ background: {tlo}; border: 1px solid {pasek}; border-left: 10px solid {pasek}; border-radius: 6px; }}")
        uklad = QHBoxLayout(self)
        uklad.setContentsMargins(18, 10, 14, 10)
        uklad.setSpacing(16)
        kolumna = QVBoxLayout()
        kolumna.setSpacing(2)
        kolumna.addWidget(etykieta(N.ZMIANA_OSOBY if zmiana_osoby else N.KTO_PRACUJE, "naglowek"))
        for tekst in teksty:
            kolumna.addWidget(etykieta(tekst, zawijaj=True))
        uklad.addLayout(kolumna, 1)
        for i, osoba in enumerate(operatorzy):
            b = przycisk(osoba, f"osoba_{i}", "osoba", lambda o=osoba: self.wybrano.emit(o))
            b.setCheckable(True)
            b.setChecked(osoba == obecna)
            uklad.addWidget(b)
        if zmiana_osoby:
            if wylogowanie:
                uklad.addWidget(przycisk(N.WYLOGUJ, "osoba_wyloguj", "lacze", self.wyloguj.emit))
            uklad.addWidget(przycisk(N.ZOSTAW_OSOBE, "osoba_bez_zmian", "lacze", self.bez_zmian.emit))


# ----------------------------------------------------------------------------
# panele pytan i komunikatow
# ----------------------------------------------------------------------------
class PanelUwagi(QFrame):
    """Jedno pytanie albo komunikat ze stanu: tytul, tekst, opcjonalnie rada, ostrzezenie i wyjasnienie, przyciski.
    ``przyciski``: lista (nazwa obiektu, napis, polecenie, argumenty, aktywny, rola); klikniecie = sygnal ``polecenie``."""

    polecenie = Signal(str, tuple)

    def __init__(self, nazwa: str, poziom: str, tytul: str, tekst: str, przyciski: list, *, rada: str = "", ostrzezenie: str = "",
                 wyjasnienie: str = "", przyciski_pod_tekstem: bool = False):
        super().__init__()
        self.setObjectName(nazwa)
        tlo, pasek, _ = styl.POZIOMY.get(poziom, styl.POZIOMY["ostrzezenie"])
        self.setStyleSheet(f"QFrame#{nazwa} {{ background: {tlo}; border: 1px solid {pasek}; border-left: 10px solid {pasek}; border-radius: 6px; }}")
        uklad = QHBoxLayout(self)
        uklad.setContentsMargins(18, 8, 12, 8)
        uklad.setSpacing(14)
        kolumna = QVBoxLayout()
        kolumna.setSpacing(3)
        kolumna.addWidget(etykieta(tytul, "naglowek"))
        if rada:
            e = etykieta(rada, "duzy", zawijaj=True)
            kolumna.addWidget(e)
        if tekst:
            kolumna.addWidget(etykieta(tekst, zawijaj=True))
        if ostrzezenie:
            kolumna.addWidget(etykieta(ostrzezenie, "uwaga", "pytanie_ostrzezenie", zawijaj=True))
        if wyjasnienie:
            kolumna.addWidget(etykieta(wyjasnienie, "slaby", zawijaj=True))
        uklad.addLayout(kolumna, 1)
        miejsce = QHBoxLayout()
        miejsce.setSpacing(8)
        for nazwa_b, napis, polecenie, argumenty, aktywny, rola in przyciski:
            b = przycisk(napis, nazwa_b, rola, lambda p=polecenie, a=tuple(argumenty): self.polecenie.emit(p, a))
            b.setEnabled(aktywny)
            if rola not in ("cyfra", "lacze"):
                b.setMinimumHeight(styl.WYSOKOSC_PRZYCISKU)
            miejsce.addWidget(b, 0, Qt.AlignmentFlag.AlignVCenter)
        if przyciski_pod_tekstem:
            miejsce.addStretch(1)
            kolumna.addLayout(miejsce)
        else:
            uklad.addLayout(miejsce)


def tytul_plytki(nazwa_plytki_: str, tytul: str) -> str:
    return N.UWAGA_PLYTKI.format(plytka=nazwa_plytki_, tytul=tytul) if nazwa_plytki_ else tytul


def panel_pytania(pytanie, stan, typ_plytki: str | None, plytka: str = "") -> PanelUwagi:
    """Panel pytania ze stanu: przyciski z ``pytanie.odpowiedzi``; polecenia wymagajace osoby nieaktywne bez niej (z wyjasnieniem)."""
    jest_osoba = stan.operator is not None
    przyciski, wymaga = [], False
    for odp in pytanie.odpowiedzi:
        potrzebuje_osoby = odp.polecenie not in BEZ_OSOBY
        wymaga = wymaga or potrzebuje_osoby
        cyfra = odp.polecenie == "podaj_numer_plytki"
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
                      ostrzezenie=ostrzezenie, wyjasnienie=wyjasnienie, przyciski_pod_tekstem=len(przyciski) > 2)


def panel_numeru(skan_id: int, numery: tuple, obecny, jest_osoba: bool, wyjasnienie: str, plytka: str = "") -> PanelUwagi:
    """Reczne podanie albo poprawienie numeru plytki (polecenie ``podaj_numer_plytki`` z ``Plytka.dozwolone``)."""
    przyciski = [(f"odp_podaj_numer_plytki_{n}", str(n), "podaj_numer_plytki", (skan_id, n), jest_osoba and n != obecny, "cyfra") for n in numery]
    przyciski.append(("numer_bez_zmian", N.ZOSTAW_OSOBE, LOKALNE_NUMER_BEZ_ZMIAN, (), True, "lacze"))
    return PanelUwagi("panel_numer_plytki", "info", tytul_plytki(plytka, ST.PRZYCISKI["podaj_numer_plytki"]), N.NUMER_PLYTKI_TEKST, przyciski,
                      wyjasnienie="" if jest_osoba else wyjasnienie, przyciski_pod_tekstem=True)


def panel_odmowy(tekst: str) -> PanelUwagi:
    """Odmowa polecenia, ktorej nie ma w komunikatach stanu (np. ``zle_argumenty``): tekst odpowiedzi kontrolera."""
    return PanelUwagi("komunikat_odpowiedz", ST.KOMUNIKATY["odmowa"].poziom, ST.KOMUNIKATY["odmowa"].tytul, tekst,
                      [("zamknij_odpowiedz", ST.PRZYCISKI["zamknij_komunikat"], LOKALNE_ZAMKNIJ_ODPOWIEDZ, (), True, "lacze")])


def panel_komunikatu(komunikaty: tuple, plytka: str = "") -> PanelUwagi:
    """Panel komunikatu ze stanu; ``komunikaty`` - jeden albo kilka jednakowych (ten sam rodzaj i tekst: jeden panel z licznikiem,
    "Zamknij" zamyka wszystkie)."""
    komunikat = komunikaty[0]
    przyciski = []
    if komunikat.rodzaj in ("pula_pusta", "pula_brak_folderu"):
        przyciski.append(("komunikat_odswiez_pule", ST.PRZYCISKI["odswiez_pule"], "odswiez_pule", (), True, None))
    przyciski.append(("zamknij_komunikat", ST.PRZYCISKI["zamknij_komunikat"], "zamknij_komunikat", tuple(k.id for k in komunikaty), True, "lacze"))
    tytul = tytul_plytki(plytka, komunikat.tytul)
    if len(komunikaty) > 1:
        tytul = N.KILKA_RAZY.format(tytul=tytul, n=len(komunikaty))
    return PanelUwagi(nazwa_obiektu("komunikat", komunikat.rodzaj), komunikat.poziom, tytul, komunikat.tekst, przyciski,
                      przyciski_pod_tekstem=False)


# ----------------------------------------------------------------------------
# lista plytek
# ----------------------------------------------------------------------------
class KafelekPlytki(QFrame):
    """Jedna plytka na liscie: numer, godzina skanu, status skanu (napis ze stanu) i liczniki prac wg koloru."""

    wybrano = Signal(int)

    def __init__(self, plytka, wybrana: bool, nowa: bool, z_pytaniem: bool):
        super().__init__()
        self.setObjectName(f"plytka_{plytka.skan_id}")
        self.setProperty("rola", "kafelek")
        self.setProperty("wybrany", "true" if wybrana else "false")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._skan_id = plytka.skan_id
        self._liczniki = {k: n for k, n in plytka.liczniki.items() if n}
        uklad = QVBoxLayout(self)
        uklad.setContentsMargins(10, 6, 10, 8)
        uklad.setSpacing(3)
        wiersz = QHBoxLayout()
        wiersz.addWidget(etykieta(nazwa_plytki(plytka.numer), "naglowek"))
        wiersz.addStretch(1)
        if nowa:
            wiersz.addWidget(znaczek(N.PLYTKA_NOWA, styl.AKCENT, rozmiar_px=13))
        wiersz.addWidget(etykieta(godzina(plytka.czas), "slaby"))
        uklad.addLayout(wiersz)
        uklad.addWidget(etykieta(plytka.napis, "slaby", zawijaj=True))
        if z_pytaniem:
            uklad.addWidget(etykieta(N.PLYTKA_PYTANIE, "uwaga"))
        wiersz = QHBoxLayout()
        wiersz.setSpacing(5)
        for klasa in KLASY_LICZNIKOW:  # kolor znaczka: kolor ekranu statusu tej klasy ze ``statusy``
            if self._liczniki.get(klasa):
                wiersz.addWidget(znaczek(str(self._liczniki[klasa]), ST.status(ST.STATUS_WG_KOLORU[klasa]).hex))
        for klasa, n in self._liczniki.items():
            if klasa not in KLASY_LICZNIKOW:  # klasa koloru nieznana tej wersji ekranu: kolor "nieznany" ze ``statusy``
                wiersz.addWidget(znaczek(str(n), ST.status(None).hex))
        if not self._liczniki:
            wiersz.addWidget(etykieta(N.PLYTKA_BEZ_PRAC if plytka.aktywna else "", "slaby"))
        wiersz.addStretch(1)
        uklad.addLayout(wiersz)

    def liczniki(self) -> dict:
        """Klasa koloru -> liczba pokazana na kafelku."""
        return dict(self._liczniki)

    def mousePressEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        if zdarzenie.button() == Qt.MouseButton.LeftButton:
            self.wybrano.emit(self._skan_id)


class ListaPlytek(QFrame):
    """Plytki biezacej zmiany (kafelki, najnowsza na gorze); wczesniejsze zmiany tej doby na zadanie."""

    wybrano = Signal(int)
    przelacz_wczesniejsze = Signal()

    def __init__(self):
        super().__init__()
        self.setProperty("rola", "panel")
        self.setObjectName("lista_plytek")
        self.setFixedWidth(styl.SZEROKOSC_LISTY_PLYTEK)
        uklad = QVBoxLayout(self)
        uklad.setContentsMargins(8, 8, 8, 8)
        uklad.setSpacing(6)
        uklad.addWidget(etykieta(N.PLYTKI_ZMIANY, "naglowek"))
        self._przewijanie = QScrollArea()
        self._przewijanie.setWidgetResizable(True)
        self._przewijanie.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._przewijanie.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        wnetrze = QWidget()
        wnetrze.setStyleSheet("background: transparent;")
        self._kafelki = QVBoxLayout(wnetrze)
        self._kafelki.setContentsMargins(0, 0, 0, 0)
        self._kafelki.setSpacing(6)
        self._przewijanie.setWidget(wnetrze)
        uklad.addWidget(self._przewijanie, 1)
        self._sygnatura = None

    def ustaw(self, plytki: list, wybrana: int | None, nowe: set, z_pytaniem: set, wczesniejszych: int, pokazane_wczesniejsze: bool) -> None:
        sygnatura = (tuple((p.skan_id, p.numer, p.napis, p.czas, p.aktywna, tuple(sorted(p.liczniki.items()))) for p in plytki), wybrana,
                     frozenset(nowe), frozenset(z_pytaniem), wczesniejszych, pokazane_wczesniejsze)
        if sygnatura == self._sygnatura:
            return
        self._sygnatura = sygnatura
        wyczysc(self._kafelki)
        if not plytki:
            self._kafelki.addWidget(etykieta(N.PLYTKI_BRAK, "slaby", zawijaj=True))
        for p in reversed(plytki):  # najnowsza na gorze
            kafelek = KafelekPlytki(p, p.skan_id == wybrana, p.skan_id in nowe, p.skan_id in z_pytaniem)
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
        self.setMinimumSize(300, 110)
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
        cel = QSize(max(300, self.width() - 4), max(100, self.height() - 4))
        self.setPixmap(self._oryginal.scaled(cel, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def resizeEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        super().resizeEvent(zdarzenie)
        self._dopasuj()


class WidokPracy(QFrame):
    """Widok jednej pracy: status i opis ze stanu, kuweta / zab / krazek, rozmiar najwiekszego ubytku i liczba ubytkow, obraz
    odchylek, "ten zab jest juz na liscie", duze przyciski decyzji. Gdy nic nie jest wybrane - podpowiedz, co kliknac."""

    decyzja = Signal(str)  # ukruszona / ok / cofnij
    zamknij = Signal()
    nastepna = Signal()
    inna_praca = Signal()

    def __init__(self):
        super().__init__()
        self.setProperty("rola", "panel")
        self.setObjectName("ramka_pracy")
        self._stos = QStackedLayout(self)
        self._stos.setContentsMargins(0, 0, 0, 0)
        pusty = etykieta(N.PRACA_PUSTY_WIDOK, "duzy", "praca_pusty_widok", zawijaj=True)
        pusty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pusty.setContentsMargins(30, 20, 30, 20)
        self._stos.addWidget(pusty)
        self._widok = QWidget()
        self._widok.setObjectName("widok_pracy")
        self._stos.addWidget(self._widok)
        u = QVBoxLayout(self._widok)
        u.setContentsMargins(14, 10, 14, 12)
        u.setSpacing(6)
        wiersz = QHBoxLayout()
        wiersz.setSpacing(10)
        self.tytul = etykieta("", "tytul", "praca_tytul")
        self.status = znaczek("", "#ffffff", "praca_status", 18)
        self.z_dwoch = przycisk("", "przycisk_inna_praca", "lacze", self.inna_praca.emit)
        self.plytka = etykieta("", "slaby", "praca_plytka")
        wiersz.addWidget(self.tytul)
        wiersz.addWidget(self.status)
        wiersz.addWidget(self.z_dwoch)
        wiersz.addStretch(1)
        wiersz.addWidget(self.plytka)
        u.addLayout(wiersz)
        self.opis = etykieta("", nazwa="praca_opis", zawijaj=True)
        u.addWidget(self.opis)
        wiersz = QHBoxLayout()
        wiersz.setSpacing(6)
        self.dane = {}
        for klucz, podpis in (("kuweta", N.KUWETA), ("zeby", N.ZAB), ("krazek", N.KRAZEK)):
            wiersz.addWidget(etykieta(podpis, "podpis"))
            self.dane[klucz] = etykieta("", "duzy", f"praca_{klucz}")
            wiersz.addWidget(self.dane[klucz])
            wiersz.addSpacing(18)
        wiersz.addStretch(1)
        u.addLayout(wiersz)
        self.ubytek = etykieta("", "duzy", "praca_ubytek", zawijaj=True)
        u.addWidget(self.ubytek)
        self.obraz = ObrazPracy()
        u.addWidget(self.obraz, 1)
        self.opis_obrazu = etykieta(N.OBRAZ_OPIS, "slaby", "praca_opis_obrazu")
        u.addWidget(self.opis_obrazu)
        self.na_liscie = etykieta("", "informacja", "praca_na_liscie", zawijaj=True)
        u.addWidget(self.na_liscie)
        self.zapisana = etykieta("", "slaby", "praca_decyzja", zawijaj=True)
        u.addWidget(self.zapisana)
        self.wyjasnienie = etykieta("", "uwaga", "praca_wyjasnienie", zawijaj=True)
        u.addWidget(self.wyjasnienie)
        wiersz = QHBoxLayout()
        wiersz.setSpacing(12)
        self.przyciski = {}
        for polecenie, status_koloru, klawisz in (("ukruszona", "ukruszona", N.KLAWISZ_UKRUSZONA), ("ok", "zatwierdzona_ok", N.KLAWISZ_OK)):
            b = przycisk(N.SKROT.format(napis=ST.PRZYCISKI[polecenie], klawisz=klawisz), f"przycisk_{polecenie}", None,
                         lambda p=polecenie: self.decyzja.emit(p), styl.WYSOKOSC_PRZYCISKU_DECYZJI)
            b.setStyleSheet(styl.przycisk_w_kolorze(ST.STATUSY[status_koloru].hex))  # kolor = kolor gniazda po tej decyzji (ze ``statusy``)
            self.przyciski[polecenie] = b
            wiersz.addWidget(b, 1)
        u.addLayout(wiersz)
        wiersz = QHBoxLayout()
        wiersz.setSpacing(10)
        self.przyciski["cofnij"] = przycisk(N.SKROT.format(napis=ST.PRZYCISKI["cofnij"], klawisz=N.KLAWISZ_COFNIJ), "przycisk_cofnij", None,
                                            lambda: self.decyzja.emit("cofnij"), 56)
        self.przycisk_nastepna = przycisk(N.NASTEPNA, "przycisk_nastepna", "lacze", self.nastepna.emit, 56)
        self.przycisk_nastepna.setToolTip(N.NASTEPNA_OPIS)
        self.przycisk_zamknij = przycisk(N.ZAMKNIJ_PRACE, "przycisk_zamknij_prace", "lacze", self.zamknij.emit, 56)
        wiersz.addWidget(self.przyciski["cofnij"], 3)
        wiersz.addWidget(self.przycisk_nastepna, 2)
        wiersz.addWidget(self.przycisk_zamknij, 2)
        u.addLayout(wiersz)
        self._sygnatura = None

    def otwarty(self) -> bool:
        return self._stos.currentIndex() == 1

    def aktywny(self, polecenie: str) -> bool:
        return self.otwarty() and self.przyciski[polecenie].isEnabled()

    def wyczysc(self) -> None:
        self._sygnatura = None
        self._stos.setCurrentIndex(0)

    def ustaw(self, stan, plytka, gniazdo, praca, nr_pracy: int, jest_nastepna: bool) -> None:
        """``gniazdo`` - ``Gniazdo`` ze stanu albo None (praca poza gniazdem); ``praca`` - pokazywana ``Praca`` albo None
        (puste gniazdo); ``nr_pracy`` - ktora praca gniazda (od 0), gdy leza w nim dwie."""
        sygnatura = (plytka.skan_id, plytka.napis, plytka.numer, gniazdo, praca, nr_pracy, stan.operator, stan.operatorzy, jest_nastepna)
        self._stos.setCurrentIndex(1)
        if sygnatura == self._sygnatura:
            return
        self._sygnatura = sygnatura
        zrodlo = gniazdo if gniazdo is not None and (praca is None or len(gniazdo.prace) > 1) else praca  # dwie prace: status gniazda
        self.tytul.setText(N.PRACA_TYTUL.format(gniazdo=gniazdo.nr) if gniazdo is not None else N.PRACA_TYTUL_POZA)
        self.status.setText(zrodlo.podpis)
        self.status.setVisible(bool(zrodlo.podpis))
        self.status.setStyleSheet(f"background: {zrodlo.rgb}; color: {styl.tekst_na(zrodlo.rgb)}; border: 1px solid #3a4047; border-radius: 5px; "
                                  f"padding: 3px 10px; font-size: 18px; font-weight: 700;")
        ile = len(gniazdo.prace) if gniazdo is not None else 1
        self.z_dwoch.setVisible(ile > 1)
        self.z_dwoch.setText(N.PRACA_Z_DWOCH.format(nr=nr_pracy + 1, ile=ile))
        self.plytka.setText(nazwa_plytki(plytka.numer))
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
            nazwa = ST.PRZYCISKI["ok"] if praca.decyzja == "ok" else ST.PRZYCISKI["ukruszona"]
            if praca.decyzja == "ukruszona_niewykryta":
                nazwa = N.DECYZJA_NIEWYKRYTA.format(decyzja=nazwa)
            self.zapisana.setText(N.DECYZJA_ZAPISANA.format(decyzja=nazwa, osoba=praca.operator or N.BRAK_DANYCH, godzina=godzina(praca.czas_decyzji)))
        self.zapisana.setVisible(praca is not None and bool(praca.decyzja))
        dozwolone = praca.dozwolone if praca is not None else ()
        jest_osoba = stan.operator is not None
        for polecenie, b in self.przyciski.items():
            b.setEnabled(polecenie in dozwolone and jest_osoba)
            b.setVisible(praca is not None)
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


# ----------------------------------------------------------------------------
# lista "do dofrezowania"
# ----------------------------------------------------------------------------
class ListaDofrezowania(QFrame):
    """Lista "do dofrezowania": kuweta, zab, krazek, plytka i gniazdo, doba i zmiana; filtr "ta doba" / "wszystkie otwarte"."""

    filtr = Signal(bool)  # True = wszystkie otwarte
    wybrano = Signal(object)  # PozycjaListy
    zapisz = Signal()

    def __init__(self, z_zapisem: bool = False):
        super().__init__()
        self.setProperty("rola", "panel")
        self.setObjectName("lista_dofrezowania")
        uklad = QVBoxLayout(self)
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
        self.tabela.verticalHeader().setDefaultSectionSize(30)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela.horizontalHeader().setSectionsClickable(False)
        self.tabela.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tabela.setMinimumHeight(30 + 3 * 30)  # naglowek i trzy pozycje zawsze widoczne
        self.tabela.cellClicked.connect(self._klik)
        uklad.addWidget(self.tabela, 1)
        wiersz = QHBoxLayout()
        self.pusta = etykieta(N.LISTA_PUSTA, "slaby", "lista_pusta")
        self.zapisano = etykieta("", "slaby", "lista_zapisano")
        wiersz.addWidget(self.pusta)
        wiersz.addWidget(self.zapisano)
        wiersz.addStretch(1)
        if z_zapisem:  # polecenie ``zapisz_liste`` (kontrakt po rundzie 2); lista zapisuje sie tez sama
            wiersz.addWidget(przycisk(ST.PRZYCISKI.get("zapisz_liste", N.ZAPISZ_LISTE), "przycisk_zapisz_liste", "lacze", self.zapisz.emit))
        uklad.addLayout(wiersz)
        self._pozycje: tuple = ()
        self._sygnatura = None

    def ustaw(self, pozycje: tuple, wszystkie: bool) -> None:
        sygnatura = (pozycje, wszystkie)
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
        self.pokaz_zapisano("")

    def pokaz_zapisano(self, napis: str) -> None:
        self.zapisano.setText(napis)
        self.zapisano.setVisible(bool(napis))

    def _klik(self, wiersz: int, _kolumna: int) -> None:
        if 0 <= wiersz < len(self._pozycje):
            self.wybrano.emit(self._pozycje[wiersz])


# ----------------------------------------------------------------------------
# legenda mapy
# ----------------------------------------------------------------------------
class Legenda(QWidget):
    """Pasek pod mapa: kolory i podpisy statusow, ktore SA na pokazanej plytce (wprost ze stanu). Na plytce, ktora niczego
    nie potwierdza, legenda nie pokazuje wiec zielonego."""

    def __init__(self):
        super().__init__()
        self.setObjectName("legenda")
        self._uklad = QHBoxLayout(self)
        self._uklad.setContentsMargins(0, 0, 0, 0)
        self._uklad.setSpacing(8)
        self._sygnatura = None

    def ustaw(self, plytka) -> None:
        pozycje = []
        for g in (plytka.gniazda if plytka is not None else ()):
            if g.prace and g.podpis and (g.podpis, g.rgb, g.status) not in pozycje:
                pozycje.append((g.podpis, g.rgb, g.status))
        if pozycje == self._sygnatura:
            return
        self._sygnatura = pozycje
        wyczysc(self._uklad)
        if pozycje:
            self._uklad.addWidget(etykieta(N.LEGENDA, "slaby"))
        for podpis, rgb, status in pozycje:
            z = znaczek(podpis, rgb, rozmiar_px=13)
            z.setToolTip(ST.status(status).opis)
            self._uklad.addWidget(z)
        self._uklad.addStretch(1)
