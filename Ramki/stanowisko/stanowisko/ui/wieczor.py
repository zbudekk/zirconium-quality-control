"""wieczor - czesci trybu "Wieczor" nowego okna (paczka E3-U1a; ``etap3/nowy_interfejs/SPEC.md`` p. 3, makieta ``Main.dc.html``).

* ``ListaPlytek`` - lewa kolumna "Plytki tej zmiany": kafelek na plytke (numer, godzina, stan, liczniki z napisem statusu),
  nowy wynik na gorze ("Pokaz nowy wynik" i informacja "Nowy wynik czeka"), skany niezapisane z "Ponow zapis",
  wczesniejsze zmiany tej doby na zadanie;
* ``PanelBoczny`` - obok mapy: znacznik plytki dopuszczonej swiadomie, legenda statusow obecnych na plytce (kropka, napis,
  liczba), prace poza gniazdami, polecenia plytki ze stanu (numer, dopuszczenie, cofniecie zastapienia);
* ``WidokPracy`` - prawa kolumna "Praca": gniazdo i status, kuweta / zab / krazek, ubytki, obraz odchylek, a na STALYM
  miejscu na dole kolumny decyzje "Ukruszona" [U], "OK" [O], "Cofnij decyzje" [C], "Nastepna" [N];
* ``ListaDofrezowania`` - na dole srodka: tabela "Do dofrezowania" o stalej wysokosci, zakres "Ta doba" / "Wszystkie otwarte".

Kazda czesc dostaje gotowe dane ze stanu kontrolera (``ustaw(...)``) i oddaje wybor technika sygnalem; kolory i napisy
statusow wylacznie z pol stanu i ze ``statusy``, wyglad z ``motyw``.
"""
from __future__ import annotations

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QSizePolicy, QStackedLayout, QTableWidgetItem,
                               QVBoxLayout, QWidget)

from .. import statusy as ST
from . import motyw
from . import napisy as N
from .czesci import (Kropka, PanelUwagi, UkladPlynny, _do_okna, _fokus_do_okna, dzien, etykieta, godzina, liczba_mm, napis_dopuszczenia,
                     nazwa_plytki, przegroda, przycisk, przycisk_skrotu, stan_obejrzenia, tabela, ustaw_role, wyczysc, znaczek)

KLASY_LICZNIKOW = (ST.KOLOR_CZERWONY, ST.KOLOR_ZOLTY, ST.KOLOR_POMARANCZOWY, ST.KOLOR_SZARY, ST.KOLOR_ZATWIERDZONA_OK, ST.KOLOR_ZIELONY)
POLECENIA_PLYTKI = ("podaj_numer_plytki", "dopusc_plytke", "cofnij_zastapienie", "cofnij_dopuszczenie")


def _przewijany(nazwa: str) -> tuple:
    """(obszar przewijany w pionie, uklad jego wnetrza) - wnetrze przezroczyste (tlo kolumny)."""
    obszar = QScrollArea()
    obszar.setObjectName(nazwa)
    obszar.setWidgetResizable(True)
    obszar.setFrameShape(QFrame.Shape.NoFrame)
    obszar.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    obszar.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    wnetrze = QWidget()
    wnetrze.setObjectName(f"{nazwa}_wnetrze")
    wnetrze.setStyleSheet(f"QWidget#{nazwa}_wnetrze {{ background: transparent; }}")  # tylko to tlo, nie kafelki (zaznaczenie)
    uklad = QVBoxLayout(wnetrze)
    uklad.setContentsMargins(0, 0, 0, 0)
    obszar.setWidget(wnetrze)
    return obszar, uklad


# ----------------------------------------------------------------------------
# lewa kolumna: plytki tej zmiany
# ----------------------------------------------------------------------------
class KafelekPlytki(QFrame):
    """Jedna plytka na liscie: numer, godzina skanu, stan plytki (napis ze stanu albo "do obejrzenia: n" / "sprawdzona"),
    znaczniki (NOWA, poprzedni skan, plytka dopuszczona, czeka na odpowiedz, ma komunikat) i liczniki prac wg klasy koloru:
    kropka w kolorze statusu (ze ``statusy``), NAPIS statusu i liczba - status nie jest rozpoznawalny tylko po barwie."""

    wybrano = Signal(int)

    def __init__(self, plytka, wybrana: bool, nowa: bool, z_pytaniem: bool, z_komunikatem: bool = False, poprzedni: bool = False):
        super().__init__()
        self.setObjectName(f"plytka_{plytka.skan_id}")
        self.setProperty("rola", "kafelek")
        self.setProperty("wybrany", "true" if wybrana else "false")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self._skan_id = plytka.skan_id
        self._liczniki = {k: n for k, n in plytka.liczniki.items() if n}
        uklad = QVBoxLayout(self)
        uklad.setContentsMargins(12, 10, 12, 10)
        uklad.setSpacing(6)
        wiersz = QHBoxLayout()
        wiersz.setSpacing(8)
        wiersz.addWidget(etykieta(nazwa_plytki(plytka.numer), "numer_plytki", zawijaj=True), 1)  # "Plytka bez numeru" w waskiej liscie: 2 wiersze
        wiersz.addWidget(etykieta(godzina(plytka.czas), "przygaszony"), 0, Qt.AlignmentFlag.AlignTop)
        uklad.addLayout(wiersz)
        uklad.addWidget(etykieta(stan_obejrzenia(plytka), "tresc", "plytka_stan", zawijaj=True))
        if napis_dopuszczenia(plytka):  # dluzszy napis: wlasny wiersz z zawijaniem (waska lista)
            uklad.addWidget(etykieta(napis_dopuszczenia(plytka), "znaczek_uwaga", "plytka_znacznik_dopuszczona", zawijaj=True))
        znaczniki = UkladPlynny(odstep_poziomy=6, odstep_pionowy=4)
        if nowa:
            znaczniki.addWidget(etykieta(N.PLYTKA_NOWA, "znaczek_nowa", "plytka_znacznik_nowa"))
        if poprzedni:  # E3-P14 (poz. 8): dwa kafelki z tym samym numerem - poprzedni skan nazwany napisem, nie samym kolorem
            znaczniki.addWidget(etykieta(N.PLYTKA_POPRZEDNI_SKAN, "znaczek_uwaga", "plytka_znacznik_poprzedni"))
        if z_pytaniem:
            znaczniki.addWidget(etykieta(N.PLYTKA_PYTANIE, "znaczek_uwaga", "plytka_znacznik_pytanie"))
        if z_komunikatem:
            znaczniki.addWidget(etykieta(N.PLYTKA_KOMUNIKAT, "znaczek_uwaga", "plytka_znacznik_komunikat"))
        if znaczniki.count():
            uklad.addLayout(znaczniki)
        liczniki = UkladPlynny(odstep_poziomy=12, odstep_pionowy=4)
        for klasa in KLASY_LICZNIKOW:  # kolor kropki: kolor ekranu statusu tej klasy ze ``statusy``; obok napis statusu i liczba
            if self._liczniki.get(klasa):
                liczniki.addWidget(self._licznik(ST.status(ST.STATUS_WG_KOLORU[klasa]), self._liczniki[klasa], klasa == ST.KOLOR_CZERWONY))
        for klasa, n in self._liczniki.items():
            if klasa not in KLASY_LICZNIKOW:  # klasa koloru nieznana tej wersji ekranu: kolor i napis "nieznany" ze ``statusy``
                liczniki.addWidget(self._licznik(ST.status(None), n, False))
        if not self._liczniki and plytka.aktywna:
            liczniki.addWidget(etykieta(N.PLYTKA_BEZ_PRAC, "pomocniczy"))
        if liczniki.count():
            uklad.addLayout(liczniki)

    @staticmethod
    def _licznik(wiersz, n: int, z_obwodka: bool) -> QWidget:
        pole = QWidget()
        pole.setObjectName("plytka_licznik")
        u = QHBoxLayout(pole)
        u.setContentsMargins(0, 0, 0, 0)
        u.setSpacing(4)
        u.addWidget(Kropka(wiersz.hex, 9, obwodka=z_obwodka), 0, Qt.AlignmentFlag.AlignVCenter)
        napis = etykieta(N.LICZNIK.format(napis=wiersz.napis, n=n), "pomocniczy")
        u.addWidget(napis)
        pole.setToolTip(N.LICZNIK_OPIS.format(napis=wiersz.napis, n=n))
        napis.setToolTip(pole.toolTip())
        return pole

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

    def __init__(self, nr: int, pozycja):
        super().__init__()
        self.setObjectName(f"niezapisany_{nr}")
        self.setProperty("rola", "kafelek_niezapisany")
        uklad = QVBoxLayout(self)
        uklad.setContentsMargins(12, 10, 12, 10)
        uklad.setSpacing(4)
        wiersz = QHBoxLayout()
        wiersz.addWidget(etykieta(nazwa_plytki(pozycja.numer), "numer_plytki", zawijaj=True), 1)
        wiersz.addWidget(etykieta(godzina(pozycja.od), "tresc"), 0, Qt.AlignmentFlag.AlignTop)
        uklad.addLayout(wiersz)
        uklad.addWidget(etykieta(pozycja.napis, "wyrozniony", zawijaj=True))
        if pozycja.prac is not None:
            uklad.addWidget(etykieta(N.PRAC.format(n=pozycja.prac), "tresc"))


class ListaPlytek(QFrame):
    """Plytki biezacej zmiany (kafelki, najnowsza na gorze); wczesniejsze zmiany tej doby na zadanie. Na samej gorze skany
    policzone, ktorych wyniku nie udalo sie jeszcze zapisac ("nie zapisano") z przyciskiem "Ponow zapis". Pod naglowkiem
    (poza przewijaniem) przycisk "Pokaz nowy wynik" - plytki, na ktore ekran sie nie przelaczyl (A-P2) - i informacja "Nowy
    wynik czeka" (E3-P14 N2). Kolumna ma stala szerokosc: nic, co sie w niej pojawia, nie rusza mapy."""

    wybrano = Signal(int)
    przelacz_wczesniejsze = Signal()
    ponow_zapis = Signal()
    pokaz_nowa = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("lista_plytek")
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._uklad = QVBoxLayout(self)
        self._uklad.setSpacing(8)
        naglowek = QHBoxLayout()
        naglowek.addWidget(etykieta(N.PLYTKI_ZMIANY, "naglowek_sekcji"), 1)
        self.ile = etykieta("", "przygaszony", "plytki_ile")
        naglowek.addWidget(self.ile)
        self._uklad.addLayout(naglowek)
        self.przycisk_nowa = przycisk("", "przycisk_nowa_plytka", "glowny", self.pokaz_nowa.emit, motyw.CEL_KLIKNIECIA)
        self.przycisk_nowa.setVisible(False)
        self._uklad.addWidget(self.przycisk_nowa)
        self._nowe = None
        self._miejsce_panelu = QVBoxLayout()
        self._miejsce_panelu.setContentsMargins(0, 0, 0, 0)
        self._uklad.addLayout(self._miejsce_panelu)
        self._przewijanie, self._kafelki = _przewijany("plytki")
        self._kafelki.setSpacing(6)
        self._uklad.addWidget(self._przewijanie, 1)
        self._sygnatura = None
        self.ustaw_uklad(motyw.UKLAD_WYSOKI)

    def ustaw_uklad(self, u: motyw.Uklad) -> None:
        self.setFixedWidth(u.lewa)
        self._uklad.setContentsMargins(12, u.odstep, 12, 12)

    def ustaw_panel_nowego(self, uwaga) -> None:
        """Informacja "Nowy wynik czeka" pod przyciskiem "Pokaz nowy wynik" (None = bez niej)."""
        wyczysc(self._miejsce_panelu)
        if uwaga is not None:
            self._miejsce_panelu.addWidget(PanelUwagi.z_uwagi(uwaga, waski=True))

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
        """``poprzednie`` - skany, ktore otwarte pytanie o ponowny skan proponuje zastapic (znacznik "poprzedni skan")."""
        sygnatura = (tuple((p.skan_id, p.numer, p.napis, p.czas, p.aktywna, p.dopuszczona, p.typ, tuple(sorted(p.liczniki.items())), stan_obejrzenia(p))
                           for p in plytki), wybrana, frozenset(nowe), frozenset(z_pytaniem), frozenset(z_komunikatem), wczesniejszych,
                     pokazane_wczesniejsze, tuple(niezapisane), frozenset(poprzednie))
        if sygnatura == self._sygnatura:
            return
        self._sygnatura = sygnatura
        self.ile.setText(str(len(plytki)) if plytki else "")
        wyczysc(self._kafelki)
        for nr, pozycja in enumerate(reversed(niezapisane)):
            self._kafelki.addWidget(KafelekNiezapisany(nr, pozycja))
        if niezapisane:
            self._kafelki.addWidget(przycisk(ST.PRZYCISKI["ponow_zapis"], "przycisk_ponow_zapis", "wglebiony", self.ponow_zapis.emit, 36))
        if not plytki and not niezapisane:
            self._kafelki.addWidget(etykieta(N.PLYTKI_BRAK, "tresc", "plytki_brak", zawijaj=True))
        for p in reversed(plytki):  # najnowsza na gorze
            kafelek = KafelekPlytki(p, p.skan_id == wybrana, p.skan_id in nowe, p.skan_id in z_pytaniem, p.skan_id in z_komunikatem,
                                    poprzedni=p.skan_id in poprzednie)
            kafelek.wybrano.connect(self.wybrano.emit)
            self._kafelki.addWidget(kafelek)
        if wczesniejszych:
            napis = N.WCZESNIEJSZE_UKRYJ if pokazane_wczesniejsze else N.WCZESNIEJSZE_POKAZ.format(n=wczesniejszych)
            self._kafelki.addWidget(przycisk(napis, "przycisk_wczesniejsze", "lacze", self.przelacz_wczesniejsze.emit, 34))
        self._kafelki.addStretch(1)


# ----------------------------------------------------------------------------
# panel obok mapy: legenda, prace poza gniazdami, polecenia plytki
# ----------------------------------------------------------------------------
class Legenda(QWidget):
    """Statusy, ktore SA na pokazanej plytce (wprost ze stanu): kropka w kolorze gniazda, podpis i liczba gniazd. Ten sam
    podpis i kolor = jedna pozycja (opisy razem w podpowiedzi). Gniazda bez pracy: pozycja "Puste gniazdo" z obwodka
    przerywana. Na plytce, ktora niczego nie potwierdza, legenda nie pokazuje wiec zielonego."""

    def __init__(self):
        super().__init__()
        self.setObjectName("legenda")
        self._uklad = QVBoxLayout(self)
        self._uklad.setContentsMargins(0, 0, 0, 0)
        self._uklad.setSpacing(8)
        self._sygnatura = None
        self._pozycje: list = []

    def pozycje(self) -> list:
        """[(napis, kolor albo None dla pustych gniazd, liczba gniazd), ...] w kolejnosci pokazania - do testow."""
        return list(self._pozycje)

    def ustaw(self, plytka) -> None:
        pozycje: dict = {}
        pustych = 0
        rysowane = plytka is not None and (plytka.aktywna or plytka.prace)
        for g in (plytka.gniazda if rysowane else ()):
            if not g.prace:
                pustych += 1
            elif g.podpis:
                wpis = pozycje.setdefault((g.podpis, g.rgb), {"n": 0, "opisy": [], "ubytek": False})
                wpis["n"] += 1
                wpis["ubytek"] = wpis["ubytek"] or g.kolor == ST.KOLOR_CZERWONY
                if ST.status(g.status).opis not in wpis["opisy"]:
                    wpis["opisy"].append(ST.status(g.status).opis)
        sygnatura = (tuple((k, v["n"], tuple(v["opisy"]), v["ubytek"]) for k, v in pozycje.items()), pustych)
        if sygnatura == self._sygnatura:
            return
        self._sygnatura = sygnatura
        wyczysc(self._uklad)
        self._pozycje = []
        if pozycje or pustych:
            self._uklad.addWidget(etykieta(N.LEGENDA, "naglowek_sekcji"))
        for (podpis, rgb), wpis in pozycje.items():
            self._uklad.addWidget(self._wiersz(Kropka(rgb, 12, obwodka=wpis["ubytek"]), podpis, wpis["n"], "\n".join(wpis["opisy"])))
            self._pozycje.append((podpis, rgb, wpis["n"]))
        if pustych:
            self._uklad.addWidget(self._wiersz(Kropka(None, 12, pusta=True), N.LEGENDA_PUSTE, pustych, ST.status("pusty").opis))
            self._pozycje.append((N.LEGENDA_PUSTE, None, pustych))

    @staticmethod
    def _wiersz(kropka: Kropka, napis: str, n: int, podpowiedz: str) -> QWidget:
        wiersz = QWidget()
        wiersz.setObjectName("legenda_pozycja")
        u = QHBoxLayout(wiersz)
        u.setContentsMargins(0, 0, 0, 0)
        u.setSpacing(8)
        u.addWidget(kropka, 0, Qt.AlignmentFlag.AlignTop)
        u.addWidget(etykieta(napis, "tresc_glowna", zawijaj=True), 1)
        u.addWidget(etykieta(str(n), "tresc"), 0, Qt.AlignmentFlag.AlignTop)
        wiersz.setToolTip(podpowiedz)
        return wiersz


class PanelBoczny(QWidget):
    """Panel obok mapy (stala szerokosc): znacznik plytki dopuszczonej swiadomie, legenda, prace poza gniazdami (przycisk
    w kolorze statusu na kazda), a na dole polecenia plytki ze stanu (``Plytka.dozwolone``). Przyciski sa obok mapy, nie nad
    nia - ich pojawienie sie nie rusza mapy."""

    poza = Signal(int)  # praca_id pracy poza gniazdem
    numer = Signal()  # "Podaj numer plytki" / "Zmien numer": otwiera wybor numeru w strefie pytan
    polecenie = Signal(str, tuple)

    def __init__(self):
        super().__init__()
        self.setObjectName("panel_boczny")
        self._uklad = u = QVBoxLayout(self)
        u.setContentsMargins(0, 0, 0, 0)
        u.setSpacing(12)
        self.dopuszczenie = etykieta("", "znaczek_uwaga", "plytka_dopuszczona", zawijaj=True)
        self.dopuszczenie.setVisible(False)
        u.addWidget(self.dopuszczenie)
        self.legenda = Legenda()
        u.addWidget(self.legenda)
        self.poza_pole = QWidget()
        self.poza_pole.setObjectName("poza_gniazdem")
        self._poza_uklad = QVBoxLayout(self.poza_pole)
        self._poza_uklad.setContentsMargins(0, 0, 0, 0)
        self._poza_uklad.setSpacing(6)
        u.addWidget(self.poza_pole)
        u.addStretch(1)
        self.akcje_pole = QWidget()
        self.akcje_pole.setObjectName("polecenia_plytki")
        self._akcje_uklad = QVBoxLayout(self.akcje_pole)
        self._akcje_uklad.setContentsMargins(0, 0, 0, 0)
        self._akcje_uklad.setSpacing(6)
        u.addWidget(self.akcje_pole)
        self._sygnatury: dict = {}
        self.ustaw_uklad(motyw.UKLAD_WYSOKI)

    def ustaw_uklad(self, u: motyw.Uklad) -> None:
        self.setFixedWidth(u.boczny)
        self._uklad.setSpacing(8 if u.zwarty else 12)

    def _zmienione(self, czesc: str, sygnatura) -> bool:
        if self._sygnatury.get(czesc) == sygnatura:
            return False
        self._sygnatury[czesc] = sygnatura
        return True

    def ustaw(self, plytka, akcje: tuple, jest_osoba: bool, wybrana_poza: int | None) -> None:
        """``akcje`` - polecenia plytki do pokazania (bez tych, o ktore wlasnie pyta otwarte pytanie)."""
        dopuszczenie = napis_dopuszczenia(plytka)  # plytka poranna dopuszczona swiadomie: staly znacznik (A-P5 poz. 5)
        self.dopuszczenie.setText(dopuszczenie)
        self.dopuszczenie.setVisible(bool(dopuszczenie))
        self.legenda.ustaw(plytka)
        poza = plytka.poza_gniazdem if plytka is not None else ()
        if self._zmienione("poza", (poza, wybrana_poza, plytka is not None)):
            wyczysc(self._poza_uklad)
            if plytka is not None and (plytka.aktywna or plytka.prace):
                self._poza_uklad.addWidget(etykieta(N.POZA_GNIAZDEM.format(n=len(poza)), "tresc", "poza_ile"))
            for i, p in enumerate(poza):
                b = przycisk(p.podpis, f"poza_{i}", None, lambda praca_id=p.praca_id: self.poza.emit(praca_id), 34)
                wybrany = p.praca_id == wybrana_poza
                b.setStyleSheet(f"QPushButton {{ background: {p.rgb}; color: {motyw.tekst_na(p.rgb)}; border-radius: {motyw.PROMIEN}px; "
                                f"border: {'3px solid ' + motyw.AKCENT if wybrany else '1px solid ' + p.rgb}; font-size: {motyw.PX_TRESC}px; "
                                f"font-weight: 600; padding: {'2px 10px' if wybrany else '4px 12px'}; }}"
                                f"QPushButton:focus {{ border: 3px solid {motyw.AKCENT_FOKUS}; padding: 2px 10px; }}")
                self._poza_uklad.addWidget(b)
        self.poza_pole.setVisible(self._poza_uklad.count() > 0)
        if self._zmienione("akcje", (plytka.skan_id if plytka else None, plytka.numer if plytka else None, akcje, jest_osoba)):
            wyczysc(self._akcje_uklad)
            for akcja in akcje:
                if akcja == "podaj_numer_plytki":  # numer wybiera sie w strefie pytan (cyfry); z numerem: "Zmien numer" (A-P5 poz. 2)
                    napis = ST.PRZYCISKI[akcja] if plytka.numer is None else N.ZMIEN_NUMER
                    b = przycisk(napis, f"plytka_{akcja}", "lacze", self.numer.emit, 34)
                else:
                    b = przycisk(ST.PRZYCISKI[akcja], f"plytka_{akcja}", "lacze", lambda a=akcja, s=plytka.skan_id: self.polecenie.emit(a, (s,)), 34)
                    b.setEnabled(jest_osoba)
                self._akcje_uklad.addWidget(b)
        self.akcje_pole.setVisible(bool(akcje))


class PoleMapy(QWidget):
    """Mapa i panel obok niej jako jedna grupa na srodku wolnego miejsca: mapa dostaje najwiekszy kwadrat, ktory sie miesci,
    panel stoi tuz przy niej. Polozenie i wielkosc mapy zaleza WYLACZNIE od rozmiaru tego pola (czyli od rozmiaru okna) -
    nigdy od tresci panelu ani od stanu programu."""

    def __init__(self, mapa: QWidget, boczny: QWidget):
        super().__init__()
        self.setObjectName("pole_mapy")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._mapa, self._boczny, self._odstep = mapa, boczny, 16
        mapa.setParent(self)
        boczny.setParent(self)
        self._ustaw_minimum()

    def ustaw_odstep(self, odstep: int) -> None:
        self._odstep = odstep
        self._ustaw_minimum()
        self._uloz()

    def _ustaw_minimum(self) -> None:
        self.setMinimumSize(self._mapa.minimumWidth() + self._odstep + self._boczny.width(), self._mapa.minimumHeight())

    def _uloz(self) -> None:
        szer, wys = self.width(), self.height()
        boczny = self._boczny.width()  # stala szerokosc (``PanelBoczny.ustaw_uklad``)
        bok = max(self._mapa.minimumWidth(), min(szer - boczny - self._odstep, wys))
        x0 = max(0, (szer - (bok + self._odstep + boczny)) // 2)
        self._mapa.setGeometry(x0, 0, bok, wys)
        self._boczny.setGeometry(x0 + bok + self._odstep, 0, boczny, wys)

    def resizeEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        super().resizeEvent(zdarzenie)
        self._uloz()


# ----------------------------------------------------------------------------
# prawa kolumna: praca
# ----------------------------------------------------------------------------
class ObrazPracy(QLabel):
    """Obraz odchylek skalowany do wolnego miejsca (albo napis, gdy obrazu nie ma)."""

    def __init__(self):
        super().__init__()
        self.setObjectName("praca_obraz")
        self.setProperty("rola", "tresc")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(120, motyw.UKLAD_WYSOKI.obraz_min)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.setStyleSheet(f"QLabel#praca_obraz {{ background: {motyw.WGLEBIENIE}; border: 1px dashed {motyw.OBWODKA_MOCNA}; "
                           f"border-radius: {motyw.PROMIEN}px; color: {motyw.TEKST_POMOCNICZY}; font-size: {motyw.PX_TRESC}px; }}")
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
        cel = QSize(max(100, self.width() - 6), max(24, self.height() - 6))
        self.setPixmap(self._oryginal.scaled(cel, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def resizeEvent(self, zdarzenie) -> None:  # noqa: N802 - nazwa Qt
        super().resizeEvent(zdarzenie)
        self._dopasuj()


class WidokPracy(QFrame):
    """Kolumna "Praca": naglowek "Plytka n - gniazdo m" (wyrazny - A-P2: wiadomo, do ktorej pracy idzie decyzja), status
    i opis ze stanu, kuweta / zab / krazek, najwiekszy ubytek i liczba ubytkow, obraz odchylek, "ten zab jest juz na liscie",
    a na dole - zawsze w tym samym miejscu - zapisana decyzja i przyciski "Ukruszona" [U], "OK" [O], "Cofnij decyzje" [C],
    "Nastepna" [N]. Gdy nic nie jest wybrane: podpowiedz, co kliknac; przyciski decyzji zostaja na miejscu, nieaktywne.
    ``praca_id`` - praca, ktorej dane sa pokazane (do niej idzie decyzja).

    S3-4: "Program nie wskazal ubytku." tylko, gdy kontrola pracy byla i dala wynik "ok" (``status_inspekcji``); gdy pracy
    nie sprawdzono (brak kontroli, kontrola pominieta, bez danych, blad kontroli, praca bez projektu) - "Tej pracy program nie
    sprawdzil."; przy innym wyniku kontroli bez ubytkow (np. popraw ulozenie) - zadnego z tych zdan (mowi to opis statusu)."""

    decyzja = Signal(str)  # ukruszona / ok / cofnij
    zamknij = Signal()
    nastepna = Signal()
    inna_praca = Signal()
    wybor_wpisu = Signal(int)  # E3-A5i: frezowanie_id krazka wybranego przez technika (``Praca.wpisy_do_wyboru``)
    cofnij_wpis = Signal()  # E3-A5i runda 2 (D9): cofniecie wyboru krazka

    def __init__(self):
        super().__init__()
        self.setObjectName("ramka_pracy")
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.praca_id: int | None = None
        self._calosc = calosc = QVBoxLayout(self)
        calosc.setContentsMargins(0, 0, 0, 0)
        calosc.setSpacing(0)
        gora = QWidget()
        gora.setObjectName("praca_gora")
        self._stos = QStackedLayout(gora)
        self._stos.setContentsMargins(0, 0, 0, 0)
        self._pusty = etykieta(N.PRACA_PUSTY_WIDOK, "tresc", "praca_pusty_widok", zawijaj=True)
        self._pusty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._pusty.setContentsMargins(24, 20, 24, 20)
        self._pusty.setMinimumSize(10, 10)
        self._pusty.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self._stos.addWidget(self._pusty)
        self._widok = QWidget()
        self._widok.setObjectName("widok_pracy")
        self._stos.addWidget(self._widok)
        calosc.addWidget(gora, 1)
        self._u = u = QVBoxLayout(self._widok)
        u.setSpacing(10)
        wiersz = QHBoxLayout()
        wiersz.setSpacing(8)
        self.tytul = etykieta("", "tytul_pracy", "praca_tytul", zawijaj=True)
        self.z_dwoch = przycisk("", "przycisk_inna_praca", "lacze", self.inna_praca.emit)
        self.przycisk_zamknij = przycisk_skrotu(N.ZAMKNIJ_PRACE, "przycisk_zamknij_prace", "lacze", self.zamknij.emit, 28, barwa="cichy",
                                                px=motyw.PX_POMOCNICZY, dopelnienie=8)
        wiersz.addWidget(self.tytul, 1)
        wiersz.addWidget(self.z_dwoch, 0, Qt.AlignmentFlag.AlignTop)
        wiersz.addWidget(self.przycisk_zamknij, 0, Qt.AlignmentFlag.AlignTop)
        u.addLayout(wiersz)
        wiersz = QHBoxLayout()
        wiersz.setSpacing(10)
        self.status = znaczek("", motyw.WGLEBIENIE, "praca_status", motyw.PX_TRESC)
        self.opis = etykieta("", "tresc", "praca_opis", zawijaj=True)
        wiersz.addWidget(self.status, 0, Qt.AlignmentFlag.AlignTop)
        wiersz.addWidget(self.opis, 1)
        u.addLayout(wiersz)
        u.addWidget(przegroda())
        siatka = QGridLayout()
        siatka.setContentsMargins(0, 0, 0, 0)
        siatka.setHorizontalSpacing(12)
        siatka.setVerticalSpacing(2)
        self.dane = {}
        for kolumna, (klucz, podpis) in enumerate((("kuweta", N.KUWETA), ("zeby", N.ZAB), ("krazek", N.KRAZEK))):
            siatka.addWidget(etykieta(podpis, "pomocniczy"), 0, kolumna)
            self.dane[klucz] = etykieta("", "wartosc", f"praca_{klucz}", zawijaj=True)
            siatka.addWidget(self.dane[klucz], 1, kolumna)
            siatka.setColumnStretch(kolumna, 1)
        u.addLayout(siatka)
        # E3-A5i: krazek do wyboru (wynik puli per praca nierozstrzygniety) - przycisk na kazdy wpis puli
        self._wpisy_pole = QWidget()
        self._wpisy_pole.setObjectName("praca_wpisy_do_wyboru")
        self._wpisy_uklad = UkladPlynny(self._wpisy_pole, odstep_poziomy=8, odstep_pionowy=6)
        self._wpisy_napis = etykieta(N.KRAZEK_DO_WYBORU, "pomocniczy")
        self._wpisy_uklad.addWidget(self._wpisy_napis)
        self._wpisy_przyciski: list[QPushButton] = []
        self.przycisk_cofnij_wpis = przycisk(N.KRAZEK_COFNIJ, "przycisk_cofnij_wpis", "lacze", self.cofnij_wpis.emit)
        self._wpisy_uklad.addWidget(self.przycisk_cofnij_wpis)
        self._wpisy_pole.setVisible(False)
        u.addWidget(self._wpisy_pole)
        u.addWidget(przegroda())
        self.ubytek = etykieta("", "wyrozniony", "praca_ubytek", zawijaj=True)
        u.addWidget(self.ubytek)
        self.liczba_ubytkow = etykieta("", "wyrozniony", "praca_liczba_ubytkow")
        u.addWidget(self.liczba_ubytkow)
        self.obraz = ObrazPracy()
        u.addWidget(self.obraz, 1)
        self.opis_obrazu = etykieta(N.OBRAZ_OPIS, "pomocniczy", "praca_opis_obrazu", zawijaj=True)
        u.addWidget(self.opis_obrazu)
        self.na_liscie = etykieta("", "informacja", "praca_na_liscie", zawijaj=True)
        u.addWidget(self.na_liscie)
        calosc.addWidget(przegroda())
        # decyzje: stale miejsce na dole kolumny - nie przesuwaja sie, gdy zmienia sie praca, komunikat albo pasek stanu
        self.decyzje = QWidget()
        self.decyzje.setObjectName("decyzje_pracy")
        self._d = d = QVBoxLayout(self.decyzje)
        d.setSpacing(10)
        self.zapisana = etykieta(N.BRAK_DECYZJI, "tresc", "praca_decyzja", zawijaj=True)
        d.addWidget(self.zapisana)
        self.wyjasnienie = etykieta("", "uwaga", "praca_wyjasnienie", zawijaj=True)
        self.wyjasnienie.setVisible(False)
        d.addWidget(self.wyjasnienie)
        self._decyzje = wiersz = QHBoxLayout()
        wiersz.setSpacing(10)
        self.przyciski = {}
        # "Ukruszona" = wypelnienie czerwonym statusu ze ``statusy``; "OK" neutralny (zielen jest zastrzezona dla statusu ze stanu)
        b = przycisk_skrotu(N.SKROT.format(napis=ST.PRZYCISKI["ukruszona"], klawisz=N.KLAWISZ_UKRUSZONA), "przycisk_ukruszona", None,
                            lambda: self.decyzja.emit("ukruszona"), motyw.UKLAD_WYSOKI.decyzja, barwa="status",
                            px=motyw.PX_PRZYCISK_DECYZJI, pogrubiony=True)
        b.setStyleSheet(motyw.styl_przycisku_statusu(ST.STATUSY["ukruszona"].hex))
        self.przyciski["ukruszona"] = b
        wiersz.addWidget(b, 1)
        b = przycisk_skrotu(N.SKROT.format(napis=ST.PRZYCISKI["ok"], klawisz=N.KLAWISZ_OK), "przycisk_ok", "ok", lambda: self.decyzja.emit("ok"),
                            motyw.UKLAD_WYSOKI.decyzja, px=motyw.PX_PRZYCISK_DECYZJI, pogrubiony=True)
        self.przyciski["ok"] = b
        wiersz.addWidget(b, 1)
        d.addLayout(wiersz)
        self._drugi = wiersz = QHBoxLayout()
        wiersz.setSpacing(10)
        self.przyciski["cofnij"] = przycisk_skrotu(N.SKROT.format(napis=ST.PRZYCISKI["cofnij"], klawisz=N.KLAWISZ_COFNIJ), "przycisk_cofnij", None,
                                                   lambda: self.decyzja.emit("cofnij"), motyw.UKLAD_WYSOKI.przycisk)
        self.przycisk_nastepna = przycisk_skrotu(N.NASTEPNA, "przycisk_nastepna", "akcent", self.nastepna.emit, motyw.UKLAD_WYSOKI.przycisk,
                                                 barwa="akcent")
        self.przycisk_nastepna.setToolTip(N.NASTEPNA_OPIS)
        wiersz.addWidget(self.przyciski["cofnij"], 1)
        wiersz.addWidget(self.przycisk_nastepna, 1)
        d.addLayout(wiersz)
        calosc.addWidget(self.decyzje)
        self._sygnatura = None
        self.ustaw_uklad(motyw.UKLAD_WYSOKI)
        self.wyczysc()

    def ustaw_uklad(self, u: motyw.Uklad) -> None:
        self._uklad_okna = u
        self.setFixedWidth(u.prawa)
        self._u.setContentsMargins(u.bok, u.odstep, u.bok, 8 if u.zwarty else 12)
        self._u.setSpacing(6 if u.zwarty else 10)
        self._d.setContentsMargins(u.bok, 8 if u.zwarty else 12, u.bok, 10 if u.zwarty else 16)
        self._d.setSpacing(6 if u.zwarty else 10)
        for polecenie in ("ukruszona", "ok"):
            self.przyciski[polecenie].setMinimumHeight(u.decyzja)
        for b in (self.przyciski["cofnij"], self.przycisk_nastepna):
            b.setMinimumHeight(u.przycisk)
        self.obraz.setMinimumSize(120, u.obraz_min)
        self._sygnatura = None

    def otwarty(self) -> bool:
        return self._stos.currentIndex() == 1

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
            b.setParent(None)
            b.deleteLater()
        self._wpisy_przyciski = []
        self._wpisy_uklad.removeWidget(self.przycisk_cofnij_wpis)
        mozna = praca is not None and "wybierz_wpis" in praca.dozwolone and jest_osoba
        for w in wpisy:
            tekst = w.krazek or str(w.frezowanie_id)
            b = przycisk(N.KRAZEK_WYBRANY.format(krazek=tekst) if w.wybrany else tekst, f"przycisk_wpis_{w.frezowanie_id}", "wglebiony",
                         lambda f=w.frezowanie_id: self.wybor_wpisu.emit(int(f)))
            b.setToolTip(N.KRAZEK_PODPOWIEDZ.format(wspolczynnik=w.wspolczynnik if w.wspolczynnik is not None else N.BRAK_DANYCH))
            b.setEnabled(mozna)
            self._wpisy_uklad.addWidget(b)
            self._wpisy_przyciski.append(b)
        self._wpisy_uklad.addWidget(self.przycisk_cofnij_wpis)  # "Cofnij wybor krazka" zawsze na koncu wiersza
        self.przycisk_cofnij_wpis.setVisible(praca is not None and "cofnij_wpis" in praca.dozwolone)
        self.przycisk_cofnij_wpis.setEnabled(jest_osoba)
        self._wpisy_pole.setVisible(bool(wpisy))

    def wyczysc(self, jest_nastepna: bool = False) -> None:
        """Nic nie jest wybrane: podpowiedz zamiast danych pracy; przyciski decyzji zostaja na miejscu, nieaktywne."""
        self._stos.setCurrentIndex(0)
        self._sygnatura = None
        self.praca_id = None
        for b in self.przyciski.values():
            b.setEnabled(False)
        self.przycisk_nastepna.setEnabled(jest_nastepna)
        self.zapisana.setText("")
        self.zapisana.setVisible(False)
        self.wyjasnienie.setVisible(False)

    @staticmethod
    def napis_ubytkow(praca) -> tuple:
        """(wiersz 1, wiersz 2) o ubytkach pracy - S3-4: zdanie "program nie wskazal ubytku" tylko po kontroli z wynikiem "ok"."""
        if praca is None:
            return "", ""
        if praca.ubytki:
            pierwszy = N.NAJWIEKSZY_UBYTEK.format(mm=liczba_mm(praca.ubytek_max_mm)) if praca.ubytek_max_mm is not None else ""
            drugi = N.LICZBA_UBYTKOW.format(n=praca.ubytki)
            return (pierwszy, drugi) if pierwszy else (drugi, "")
        if praca.blad_inspekcji or praca.status_inspekcji in ST.INSPEKCJE_NIESPRAWDZONE or praca.kolor == ST.KOLOR_SZARY:
            return N.NIE_SPRAWDZIL, ""
        if praca.status_inspekcji == ST.INSPEKCJA_ZIELONA:
            return N.BEZ_UBYTKOW, ""
        return "", ""

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
        self.status.setStyleSheet(motyw.styl_znacznika(zrodlo.rgb, motyw.PX_TRESC, 22))
        ile = len(gniazdo.prace) if gniazdo is not None else 1
        self.z_dwoch.setVisible(ile > 1)
        self.z_dwoch.setText(N.PRACA_Z_DWOCH.format(nr=nr_pracy + 1, ile=ile))
        self.opis.setText(ST.status(zrodlo.status).opis if zrodlo is gniazdo else praca.opis)
        for klucz, pole in self.dane.items():
            pole.setText((getattr(praca, klucz) if praca is not None else None) or N.BRAK_DANYCH)
        pierwszy, drugi = self.napis_ubytkow(praca)
        self.ubytek.setText(pierwszy)
        self.ubytek.setVisible(bool(pierwszy))
        self.liczba_ubytkow.setText(drugi)
        self.liczba_ubytkow.setVisible(bool(drugi))
        tekst_listy = praca.na_liscie.tekst if praca is not None and praca.na_liscie is not None else ""
        self.na_liscie.setText(tekst_listy)
        self.na_liscie.setVisible(bool(tekst_listy))
        if praca is not None and praca.decyzja:
            nazwa_decyzji = ST.PRZYCISKI["ok"] if praca.decyzja == "ok" else ST.PRZYCISKI["ukruszona"]
            if praca.decyzja == "ukruszona_niewykryta":
                nazwa_decyzji = N.DECYZJA_NIEWYKRYTA.format(decyzja=nazwa_decyzji)
            self.zapisana.setText(N.DECYZJA_ZAPISANA.format(decyzja=nazwa_decyzji, osoba=praca.operator or N.BRAK_DANYCH,
                                                            godzina=godzina(praca.czas_decyzji)))
        else:
            self.zapisana.setText(N.BRAK_DECYZJI if praca is not None else "")
        self.zapisana.setVisible(praca is not None)
        dozwolone = praca.dozwolone if praca is not None else ()
        jest_osoba = stan.operator is not None
        for polecenie, b in self.przyciski.items():
            b.setEnabled(polecenie in dozwolone and jest_osoba)
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
        self.opis_obrazu.setVisible(praca is not None and not self._uklad_okna.zwarty)  # uklad zwarty: opis obrazu jest podpowiedzia
        self.obraz.setToolTip(N.OBRAZ_OPIS)


# ----------------------------------------------------------------------------
# lista "do dofrezowania"
# ----------------------------------------------------------------------------
class ListaDofrezowania(QFrame):
    """Lista "do dofrezowania" na dole srodka okna: kuweta, zab, krazek, plytka i gniazdo, doba i zmiana; zakres "Ta doba" /
    "Wszystkie otwarte"; godzina ostatniego zapisu do pliku i "Zapisz liste do pliku". Wysokosc sekcji jest STALA (widac
    ``Uklad.wiersze_listy`` pozycji, reszta przewijana) - dopisanie pozycji po decyzji nie zmienia wielkosci mapy."""

    filtr = Signal(bool)  # True = wszystkie otwarte
    wybrano = Signal(object)  # PozycjaListy
    zapisz = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("lista_dofrezowania")
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._uklad = uklad = QVBoxLayout(self)
        uklad.setSpacing(0)
        self._naglowek = wiersz = QHBoxLayout()
        wiersz.setSpacing(12)
        self.tytul = etykieta("", "naglowek", "lista_tytul")
        wiersz.addWidget(self.tytul)
        zakres = QHBoxLayout()
        zakres.setSpacing(0)
        self.ta_doba = przycisk(N.LISTA_TA_DOBA, "lista_ta_doba", "zakres_lewy", lambda: self._klik_zakresu(False))
        self.wszystkie = przycisk(N.LISTA_WSZYSTKIE, "lista_wszystkie", "zakres_prawy", lambda: self._klik_zakresu(True))
        for b in (self.ta_doba, self.wszystkie):
            b.setCheckable(True)
            zakres.addWidget(b)
        wiersz.addLayout(zakres)
        self.pusta = etykieta(N.LISTA_PUSTA, "przygaszony", "lista_pusta")
        wiersz.addWidget(self.pusta)
        wiersz.addStretch(1)
        self.zapisano = etykieta("", "przygaszony", "lista_zapisano")
        wiersz.addWidget(self.zapisano)
        # polecenie ``zapisz_liste``; lista zapisuje sie tez sama po kazdej zmianie (``StanAplikacji.lista_zapisana``)
        self.przycisk_zapisz = przycisk(ST.PRZYCISKI["zapisz_liste"], "przycisk_zapisz_liste", "lacze", self.zapisz.emit)
        wiersz.addWidget(self.przycisk_zapisz)
        uklad.addLayout(wiersz)
        self.tabela = tabela("tabela_dofrezowania", N.KOLUMNY_LISTY, motyw.UKLAD_WYSOKI.wiersz_tabeli, motyw.UKLAD_WYSOKI.naglowek_tabeli)
        self.tabela.cellClicked.connect(self._klik)
        uklad.addWidget(self.tabela, 1)
        self._pozycje: tuple = ()
        self._wszystkie = False
        self._sygnatura = None
        self.ustaw_uklad(motyw.UKLAD_WYSOKI)

    def ustaw_uklad(self, u: motyw.Uklad) -> None:
        self.setFixedHeight(u.lista)
        self._uklad.setContentsMargins(u.bok, 0, u.bok, u.odstep)
        self._naglowek.setContentsMargins(0, 0, 0, 0)
        for b in (self.ta_doba, self.wszystkie, self.przycisk_zapisz):
            b.setMinimumHeight(30 if not u.zwarty else 28)
        self.tabela.verticalHeader().setMinimumSectionSize(u.wiersz_tabeli)
        self.tabela.verticalHeader().setDefaultSectionSize(u.wiersz_tabeli)
        self.tabela.horizontalHeader().setFixedHeight(u.naglowek_tabeli)

    def _klik_zakresu(self, wszystkie: bool) -> None:
        self.ta_doba.setChecked(not self._wszystkie)  # wyglad przelacznika idzie za stanem okna, nie za kliknieciem
        self.wszystkie.setChecked(self._wszystkie)
        self.filtr.emit(wszystkie)

    def ustaw(self, pozycje: tuple, wszystkie: bool, zapisana: str | None = None) -> None:
        sygnatura = (pozycje, wszystkie, zapisana)
        self._wszystkie = wszystkie
        self.ta_doba.setChecked(not wszystkie)
        self.wszystkie.setChecked(wszystkie)
        if sygnatura == self._sygnatura:
            return
        self._sygnatura = sygnatura
        self._pozycje = tuple(pozycje)
        self.tytul.setText(N.LISTA_TYTUL.format(n=len(pozycje)))
        self.tabela.setRowCount(len(pozycje))
        for r, x in enumerate(pozycje):
            zab = x.zeby or N.BRAK_DANYCH
            if x.powtorzenia:
                zab = f"{zab}  ({N.POWTORZONY.format(n=x.powtorzenia + 1)})"
            komorki = (x.kuweta or N.BRAK_DANYCH, zab, x.krazek or N.BRAK_DANYCH, str(x.numer_plytki) if x.numer_plytki is not None else N.BRAK_DANYCH,
                       str(x.gniazdo) if x.gniazdo is not None else N.BRAK_DANYCH, dzien(x.doba), str(x.zmiana))
            for k, tekst in enumerate(komorki):
                pole = QTableWidgetItem(tekst)
                pole.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.tabela.setItem(r, k, pole)
        self.tabela.clearSelection()
        self.pusta.setVisible(not pozycje)
        self.zapisano.setText(N.LISTA_PLIK.format(godzina=godzina(zapisana)) if zapisana else "")  # bez nazwy pliku
        self.zapisano.setVisible(bool(zapisana))

    def _klik(self, wiersz: int, _kolumna: int) -> None:
        if 0 <= wiersz < len(self._pozycje):
            self.wybrano.emit(self._pozycje[wiersz])
