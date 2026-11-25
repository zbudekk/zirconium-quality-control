"""zrzuty_instrukcji - zrzuty okna programu "Stanowisko" do instrukcji dla technika (paczka E3-A11d).

Okno jest prawdziwe (``stanowisko.ui.utworz_okno``), dane wylacznie sztuczne (``kontroler_api.AtrapaKontrolera``: fikcyjne
kuwety 9001-9030 i 3200-3445, osoby "Technik A" / "Technik B"), ekranu nie trzeba (Qt ``offscreen``), zegar jest staly -
to samo polecenie daje te same obrazki. Skrypt steruje oknem jak technik (klikniecia, klawisze) i zapisuje caly ekran
albo jego czesc (nazwany element okna) jako PNG.

Uzycie (z katalogu stanowisko/):
    py -3.12 narzedzia/zrzuty_instrukcji.py                      komplet do instrukcje/obrazki/
    py -3.12 narzedzia/zrzuty_instrukcji.py --wyjscie KATALOG    komplet do innego katalogu
    py -3.12 narzedzia/zrzuty_instrukcji.py --tylko wieczor_mapa rano_piec ...
    py -3.12 narzedzia/zrzuty_instrukcji.py --t14                obrazki jednej strony proby T14 (Ramki/etap3/t14/obrazki)
    py -3.12 narzedzia/zrzuty_instrukcji.py --lista              nazwy i opisy zrzutow

Po zmianie wygladu okna: uruchom ponownie, OBEJRZYJ kazdy PNG, potem ``narzedzia/instrukcje_html.py`` (strony do druku).
Lista ``ZRZUTY`` jest zrodlem prawdy dla ``testy/test_instrukcje.py`` (obrazek wskazany w instrukcji musi byc na liscie).
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import os
import sys
import tempfile
import time
from pathlib import Path

STANOWISKO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(STANOWISKO))
sys.path.insert(0, str(Path(__file__).resolve().parent))

KATALOG_DOMYSLNY = STANOWISKO / "instrukcje" / "obrazki"
FONTY_WINDOWS = Path(r"C:\Windows\Fonts")
OKNO = (1600, 900)  # uklad zwykly okna (ui/motyw.py: od 1500 x 860 punktow)
OKNO_RANO = (1920, 1080)  # ekran laptopa stanowiska (opisy_modulow/ui_rano.md)
OKNO_EXCEL = (1280, 720)  # panel Excela w malym oknie: na wydruku (ok. 83 mm) napisy i przycisk "Zatwierdz wiersz" sa czytelne
WIECZOR = dt.datetime(2026, 11, 17, 19, 0, 0)  # wtorek, zmiana 2
RANO = dt.datetime(2026, 11, 18, 7, 10, 0)  # sroda, zmiana 1
OSOBA = "Technik A"  # jedna z dwoch fikcyjnych osob atrapy

# plytka wieczorna do pokazu: gniazdo -> rodzaj pracy (``kontroler_api.RODZAJE_PRAC``); projekty = numer gniazda
PLYTKA_1 = {1: "zielony", 2: "czerwony", 3: "zielony", 4: "szary", 5: "zielony", 7: "zolty", 8: "zielony", 9: "czerwony",
            10: "zielony", 11: "zielony", 13: "zielony", 14: "zielony", 16: "zielony"}
PLYTKA_2 = ({1: "zielony", 3: "popraw_ulozenie", 5: "zielony", 6: "zielony"}, {1: 21, 3: 23, 5: 25, 6: 26})
# dwie plytki pieca (jak testy/test_ui_rano.py::test_t14_szesc_zadan_porannych): zlecenia 3221, 3228, 3235 kompletne, 3242 z brakami
PIEC = ((4, {1: "pewna", 2: "pewna", 3: "zolta", 4: "pewna", 5: "pewna"}, {1: 307, 2: 308, 3: (309, 320), 4: 311, 5: 312}),
        (5, {1: "pewna", 2: "pewna", 3: "pewna"}, {1: 310, 2: 313, 3: 314}))


class Zegar:
    """Staly zegar programu (te same godziny na kazdym zrzucie); ``przesun`` - kolejny skan o minute pozniej."""

    def __init__(self, start: dt.datetime):
        self.teraz = start

    def __call__(self) -> dt.datetime:
        return self.teraz

    def przesun(self, minut: float = 1.0) -> None:
        self.teraz += dt.timedelta(minutes=minut)


def przygotuj_qt():
    """Qt bez ekranu, z czcionkami systemu (offscreen nie ma wlasnych); zwraca ``QApplication``."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    if FONTY_WINDOWS.is_dir():
        os.environ.setdefault("QT_QPA_FONTDIR", str(FONTY_WINDOWS))
    from PySide6.QtGui import QFontDatabase
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication(sys.argv[:1])
    from stanowisko.ui import motyw

    if motyw.CZCIONKI[-1] not in QFontDatabase.families() and FONTY_WINDOWS.is_dir():
        for wzor in ("segoeui*.ttf", "seguisb*.ttf", "seguisym*.ttf"):
            for plik in sorted(FONTY_WINDOWS.glob(wzor)):
                QFontDatabase.addApplicationFont(str(plik))
    return app


class Ekran:
    """Okno programu na kontrolerze ``k``, pokazane bez ekranu i sterowane jak przez technika."""

    def __init__(self, kontroler, rozmiar: tuple = OKNO):
        from PySide6.QtTest import QTest

        from stanowisko import kontroler_api as K
        from stanowisko import ui

        self.k = kontroler
        self.lacznik = K.lacznik_qt(kontroler)
        self.okno = ui.utworz_okno(kontroler, self.lacznik)
        self.okno.resize(*rozmiar)
        self.okno.show()
        QTest.qWaitForWindowExposed(self.okno)
        self.odczekaj(50)

    def odczekaj(self, ms: int = 30) -> None:
        from PySide6.QtTest import QTest

        QTest.qWait(ms)

    def zdarzenia(self) -> None:
        from PySide6.QtWidgets import QApplication

        QApplication.sendPostedEvents()
        QApplication.processEvents()

    def czekaj(self, warunek, limit_s: float = 20.0, co: str = "") -> None:
        koniec = time.monotonic() + limit_s
        while not warunek():
            if time.monotonic() >= koniec:
                raise RuntimeError(f"nie doczekalem sie: {co}")
            self.odczekaj(10)

    def w(self, nazwa: str):
        from PySide6.QtWidgets import QWidget

        w = self.okno.findChild(QWidget, nazwa)
        if w is None:
            raise RuntimeError(f"na ekranie nie ma elementu {nazwa!r}")
        return w

    def jest(self, nazwa: str) -> bool:
        from PySide6.QtWidgets import QWidget

        self.zdarzenia()
        w = self.okno.findChild(QWidget, nazwa)
        return w is not None and w.isVisibleTo(self.okno)

    def po_ochronie(self) -> None:
        """Po zmianie mapy okno przez chwile nie przyjmuje klikniec (mapa przygaszona) - czeka jak technik."""
        if self.okno.rano():
            self.czekaj(lambda: not self.okno.ekran_rano.ochrona_aktywna(), 5.0, "koniec przygaszenia map porannych")
        else:
            self.czekaj(lambda: not self.okno.ochrona_aktywna(), 5.0, "koniec przygaszenia mapy")

    def po_ochronie_nakladek(self) -> None:
        """Nowe okno (E3-U1a): strefa pytan i lista bledow, ktorych zawartosc zmienila sie w tle, sa przez chwile przygaszone
        i nie przyjmuja klikniec (S3-3) - czeka jak technik."""
        self.czekaj(lambda: not self.okno.ochrona_nakladek_aktywna(), 5.0, "koniec przygaszenia strefy pytan / listy bledow")

    def klik(self, nazwa: str) -> None:
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest

        self.zdarzenia()
        self.po_ochronie_nakladek()
        w = self.w(nazwa)
        if not (w.isVisibleTo(self.okno) and w.isEnabled()):
            raise RuntimeError(f"element {nazwa!r} jest niewidoczny albo nieaktywny")
        QTest.mouseClick(w, Qt.MouseButton.LeftButton)
        self.odczekaj(5)

    def klik_gniazdo(self, nr: int, skan_id: int | None = None) -> None:
        """Klikniecie gniazda ``nr`` na mapie wieczornej albo (``skan_id``) na mapie plytki porannej."""
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest

        self.zdarzenia()
        self.po_ochronie()
        mapa = self.okno.mapa if skan_id is None else self.okno.ekran_rano.mapy()[skan_id]
        QTest.mouseClick(mapa, Qt.MouseButton.LeftButton, pos=mapa.srodek_gniazda(nr).toPoint())
        self.odczekaj(5)

    def klawisz(self, klawisz) -> None:
        from PySide6.QtTest import QTest

        self.zdarzenia()
        self.po_ochronie()
        QTest.keyClick(self.okno, klawisz)
        self.odczekaj(5)

    def wpisz(self, tekst: str) -> None:
        from PySide6.QtTest import QTest

        QTest.keyClicks(self.okno, tekst)
        self.odczekaj(5)

    def teksty(self) -> str:
        """Wszystkie widoczne napisy okna (etykiety, przyciski, tabele) - do sprawdzen."""
        from PySide6.QtWidgets import QAbstractButton, QLabel, QTableWidget, QWidget

        self.zdarzenia()
        wynik = []
        for w in self.okno.findChildren(QWidget):
            if not w.isVisibleTo(self.okno):
                continue
            if isinstance(w, (QLabel, QAbstractButton)):
                wynik.append(w.text())
            elif isinstance(w, QTableWidget):
                wynik += [w.item(r, k).text() for r in range(w.rowCount()) for k in range(w.columnCount()) if w.item(r, k) is not None]
        return "\n".join(t for t in wynik if t)

    def obraz(self, element: str | None = None, szerokosc: int | None = None):
        """Obraz calego okna albo elementu ``element``; ``szerokosc`` - pomniejszenie do tej szerokosci (piksele)."""
        from PySide6.QtCore import Qt

        self.zdarzenia()
        self.po_ochronie()
        self.po_ochronie_nakladek()
        self.odczekaj(60)
        obraz = (self.w(element) if element else self.okno).grab().toImage()
        if szerokosc and obraz.width() > szerokosc:
            obraz = obraz.scaledToWidth(szerokosc, Qt.TransformationMode.SmoothTransformation)
        return obraz

    def zamknij(self) -> None:
        from PySide6.QtCore import QCoreApplication, QEvent

        self.okno.close()
        self.lacznik.zatrzymaj()
        self.odczekaj(5)
        self.okno.deleteLater()
        self.lacznik.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)


# ----------------------------------------------------------------------------
# sceny: kazda dostaje katalog roboczy i zwraca (Ekran, kontroler, element do wyciecia albo None)
# ----------------------------------------------------------------------------
def _atrapa(katalog: Path, start: dt.datetime):
    from stanowisko import kontroler_api as K

    zegar = Zegar(start)
    return K.AtrapaKontrolera(katalog / "atrapa", zegar=zegar), zegar


def _wieczor(katalog: Path, *, osoba: bool = True, plytka_1: bool = True, decyzje: bool = False):
    k, zegar = _atrapa(katalog, WIECZOR)
    if osoba:
        k.wybierz_operatora(OSOBA)
    skan = None
    if plytka_1:
        zegar.przesun(2)
        skan = k.symuluj_skan("zwykla", numer=1, gniazda=PLYTKA_1)
        if decyzje:
            plytka = k.stan().plytka(skan)
            k.ukruszona(plytka.gniazdo(2).praca.praca_id)
            k.ok(plytka.gniazdo(9).praca.praca_id)
    return k, zegar, skan


def _wieczor_z_praca(katalog: Path):
    from stanowisko.ui import napisy as N

    k, _, _ = _wieczor(katalog)
    e = Ekran(k)
    e.klik_gniazdo(2)
    e.czekaj(lambda: e.jest("widok_pracy") and N.OBRAZ_WCZYTYWANIE not in e.teksty(), 10.0, "widok pracy z obrazem odchylek")
    return e, k


def scena_wieczor_ekran(katalog: Path):
    e, k = _wieczor_z_praca(katalog)
    return e, k, None


def scena_wieczor_praca(katalog: Path):
    e, k = _wieczor_z_praca(katalog)
    return e, k, "ramka_pracy"


def _wieczor_popraw(katalog: Path):
    k, zegar, _ = _wieczor(katalog, decyzje=True)
    plytka = k.stan().plytka(k.stan().plytki[0].skan_id)
    for nr in (4, 7):  # wszystko obejrzane - ekran sam przechodzi na nowa plytke
        k.ok(plytka.gniazdo(nr).praca.praca_id)
    zegar.przesun(6)
    k.symuluj_skan("do_powtorzenia", numer=2, gniazda=PLYTKA_2[0], projekty=PLYTKA_2[1])
    e = Ekran(k)
    e.czekaj(lambda: e.jest("komunikat_skan_do_powtorzenia"), 5.0, "komunikat o powtorzeniu skanu")
    return e, k, zegar


def scena_wieczor_popraw(katalog: Path):
    e, k, _ = _wieczor_popraw(katalog)
    return e, k, "komunikat_skan_do_powtorzenia"


def scena_wieczor_ponowny(katalog: Path):
    e, k, zegar = _wieczor_popraw(katalog)
    zegar.przesun(3)
    k.symuluj_skan("czysta", numer=2, gniazda={nr: "zielony" for nr in PLYTKA_2[0]}, projekty=PLYTKA_2[1])
    e.czekaj(lambda: e.jest("pytanie_ponowny_skan"), 5.0, "pytanie o ponowny skan")
    return e, k, "pytanie_ponowny_skan"


def scena_wieczor_lista(katalog: Path):
    k, _, _ = _wieczor(katalog, decyzje=True)
    return Ekran(k), k, "lista_dofrezowania"


def _poranek(katalog: Path, *, wybor: bool = True, rozmiar: tuple = OKNO_RANO):
    """Poranek na ekranie stanowiska (1920 x 1080): dwie plytki pieca; ``wybor`` - zolte gniazdo 3 plytki 4 juz rozstrzygniete."""
    from PySide6.QtCore import Qt

    from stanowisko import kontroler_api as K

    k, zegar = _atrapa(katalog, RANO)
    k.przelacz_tryb(K.TRYB_RANO)
    k.wybierz_operatora(OSOBA)
    K.indeks_rano_sztuczny(k.sesja.baza, k.sesja.teraz())
    skany = {}
    for numer, gniazda, projekty in PIEC:
        zegar.przesun(2)
        skany[numer] = k.symuluj_skan_rano(numer, gniazda, projekty=projekty)
    e = Ekran(k, rozmiar)
    e.czekaj(lambda: len(e.okno.ekran_rano.mapy()) == 2, 5.0, "dwie plytki pieca")
    if wybor:
        e.klik_gniazdo(3, skany[4])
        e.czekaj(lambda: e.jest("kandydat_1_wybierz"), 5.0, "dwaj kandydaci")
        e.klik("kandydat_1_wybierz")
        e.klawisz(Qt.Key.Key_Escape)
    return e, k, skany


def scena_rano_ekran(katalog: Path):
    from PySide6.QtCore import Qt

    e, k, _ = _poranek(katalog)
    e.klawisz(Qt.Key.Key_Return)  # pierwsza kuweta rozlozona, nastepna biezaca
    return e, k, None


def scena_rano_kandydaci(katalog: Path):
    e, k, skany = _poranek(katalog, wybor=False)
    e.klik_gniazdo(3, skany[4])
    e.czekaj(lambda: e.jest("kandydat_1_wybierz"), 5.0, "dwaj kandydaci")
    return e, k, "praca_rano_wnetrze"


def scena_rano_braki(katalog: Path):
    e, k, _ = _poranek(katalog)
    e.klik("przycisk_zamknij_piec")
    e.czekaj(lambda: e.jest("tabela_braki"), 5.0, "lista brakow po zamknieciu pieca")
    return e, k, "rano_wynik_wnetrze"


def _arkusz_zlecen(dzis: dt.date):
    """Sztuczny arkusz zlecen dla puli porannej atrapy: wiersz "prawdziwy" kazdej kuwety (kolumna H = fikcyjna nazwa folderu)
    i starszy, zielony wiersz tej samej kuwety; kuweta 3228 ma dwa niezaznaczone wiersze - program prosi "wskaz wiersz"."""
    import arkusz_syntetyczny as AS
    from stanowisko import kontroler_api as K

    wiersze, zielone = [], []

    def dodaj(a, b, c, h) -> int:
        wiersze.append([a, b, c, None, None, None, None, h, None])
        return len(wiersze) + 1  # wiersz 1 = naglowek

    for i, (kuweta, _) in enumerate(K.ZLECENIA_RANO):
        folder = f"{kuweta} Fikcja Rano"
        if kuweta.startswith("#"):
            dodaj(dzis - dt.timedelta(days=2), kuweta[1:], None, folder)
            continue
        zielone.append(dodaj(dzis - dt.timedelta(days=400), f"S{i}", int(kuweta), f"Starsza Osoba {kuweta}"))
        if kuweta == "3228":
            dodaj(dzis - dt.timedelta(days=9), f"R{i}", int(kuweta), folder)
        dodaj(dzis - dt.timedelta(days=2), f"Z{1000 + i}", int(kuweta), folder)
    arkusz = AS.ArkuszWPamieci(wiersze=wiersze)
    for nr in zielone:
        arkusz.zaznacz(nr, 2, (198, 239, 206))
    return arkusz


def scena_rano_excel(katalog: Path):
    import copy

    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    from stanowisko import excel as EX
    from stanowisko import ustawienia as UST

    e, k, _ = _poranek(katalog, rozmiar=OKNO_EXCEL)
    arkusz = _arkusz_zlecen(RANO.date())
    ust = copy.deepcopy(UST.wczytaj_ustawienia(UST.PLIK_PRZYKLADU))
    ust["sciezki"]["log_excel"] = (katalog / "dane" / "log_excel.csv").as_posix()
    ust["excel"]["tryb"] = "pytaj"
    # stanowisko skonfigurowane: skoroszyt i arkusz wskazane w ustawieniach - panel bez ostrzezenia o pliku "aktywnym" (P3)
    ust["excel"]["skoroszyt"], ust["excel"]["arkusz"] = arkusz.skoroszyt, arkusz.nazwa
    k.podlacz_excel(EX.Excel.z_ustawien(ust, zrodlo=arkusz, baza=k.sesja.baza, zegar=lambda: RANO))
    e.klik("przycisk_zamknij_piec")
    e.czekaj(lambda: e.jest("excel_panel") and k.stan().excel.w_toku == 0, 10.0, "panel Excela")
    tabela = e.w("excel_tabela")
    QTest.mouseClick(tabela.viewport(), Qt.MouseButton.LeftButton, pos=tabela.visualItemRect(tabela.item(0, 0)).center())
    e.odczekaj(30)
    return e, k, "excel_panel"


# nazwa pliku (bez .png) -> (scena, szerokosc obrazka w pikselach albo None = bez pomniejszania, opis: co ma byc widac)
ZRZUTY = {
    "wieczor_ekran": (scena_wieczor_ekran, 1400, "caly ekran wieczorny: pasek stanu, lista plytek, mapa plytki 1, widok pracy z gniazda 2, lista"),
    "wieczor_praca": (scena_wieczor_praca, None, 'widok pracy z czerwonego gniazda 2: rozmiar ubytku, obraz, przyciski "Ukruszona" i "OK"'),
    "wieczor_popraw": (scena_wieczor_popraw, None, 'komunikat "Skan do powtorzenia" z powodem "popraw ulozenie pracy (gniazdo 3)"'),
    "wieczor_ponowny": (scena_wieczor_ponowny, None, 'pytanie "Ponowny skan tej samej plytki?" z dwoma przyciskami odpowiedzi'),
    "wieczor_lista": (scena_wieczor_lista, None, 'lista "Do dofrezowania: 1" z jedna pozycja i przyciskiem zapisu do pliku'),
    "rano_ekran": (scena_rano_ekran, 1400, "caly ekran poranny: piec, dwie plytki, biezaca kuweta obwiedziona, lista kuwet"),
    "rano_kandydaci": (scena_rano_kandydaci, None, 'zolte gniazdo otwarte: "Ktory to projekt?", dwaj kandydaci z przyciskiem "To ten projekt"'),
    "rano_braki": (scena_rano_braki, None, 'po "Zamknij piec": zlecenia kompletne, braki w piecu i lista brakow'),
    "rano_excel": (scena_rano_excel, None, 'tryb "pytaj": panel "Excel: wskaz wiersz" z propozycjami i przyciskiem "Zatwierdz wiersz"'),
}


@contextlib.contextmanager
def staly_licznik_czasu():
    """Atrapa kontrolera nadaje sztucznym skanom skrot z ``time.time_ns()`` i z niego losuje punkty obrazu odchylek; na czas
    budowy sceny licznik jest staly (kolejne wartosci 1, 2, 3 ...), zeby ten sam zrzut wyszedl taki sam."""
    prawdziwy, kolejny = time.time_ns, iter(range(1, 10**9))
    time.time_ns = lambda: next(kolejny)
    try:
        yield
    finally:
        time.time_ns = prawdziwy


def bez_pustego_dolu(obraz, zapas: int = 10):
    """Obraz bez pustego pasa na dole (element okna bywa wyzszy niz jego tresc): obciety pod ostatnim wierszem pikseli,
    ktory rozni sie od koloru tla (tlo = kolor nad dolna krawedzia, w polowie szerokosci)."""
    szer, wys = obraz.width(), obraz.height()
    tlo = obraz.pixel(szer // 2, wys - 4)
    for y in range(wys - 4, 0, -1):
        if any(obraz.pixel(x, y) != tlo for x in range(4, szer - 4, 3)):
            return obraz.copy(0, 0, szer, min(wys, y + 1 + zapas))
    return obraz


def zrob(nazwa: str, katalog_wyjscia: Path) -> Path:
    """Buduje scene ``nazwa`` w katalogu tymczasowym i zapisuje ``<nazwa>.png``; zwraca plik."""
    scena, szerokosc, _ = ZRZUTY[nazwa]
    with tempfile.TemporaryDirectory(prefix="qc_zrzuty_") as tmp, staly_licznik_czasu():
        e, k, element = scena(Path(tmp))
        try:
            obraz = e.obraz(element, szerokosc)
            if nazwa in BEZ_PUSTEGO_DOLU:
                obraz = bez_pustego_dolu(obraz)
            katalog_wyjscia.mkdir(parents=True, exist_ok=True)
            plik = katalog_wyjscia / f"{nazwa}.png"
            if not obraz.save(str(plik), "PNG", 0):
                raise RuntimeError(f"nie zapisano {plik.name}")
        finally:
            e.zamknij()
            k.zamknij()
    return plik


BEZ_PUSTEGO_DOLU = ("rano_kandydaci", "rano_braki")  # elementy okna wyzsze niz ich tresc
T14_OBRAZKI = ("wieczor_ekran", "wieczor_praca", "rano_ekran", "rano_kandydaci")  # obrazki jednej strony proby T14
KATALOG_T14 = STANOWISKO.parent / "etap3" / "t14" / "obrazki"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Zrzuty okna programu "Stanowisko" do instrukcji (dane sztuczne, bez ekranu).')
    parser.add_argument("--wyjscie", type=Path, default=KATALOG_DOMYSLNY, help="katalog na PNG (domyslnie instrukcje/obrazki)")
    parser.add_argument("--tylko", nargs="+", metavar="NAZWA", help="tylko te zrzuty")
    parser.add_argument("--t14", action="store_true", help="tylko obrazki jednej strony proby T14, do Ramki/etap3/t14/obrazki")
    parser.add_argument("--lista", action="store_true", help="wypisz nazwy i opisy zrzutow")
    args = parser.parse_args(argv)
    if args.lista:
        for nazwa, (_, _, opis) in ZRZUTY.items():
            print(f"{nazwa}.png - {opis}")
        return 0
    if args.t14:
        args.tylko, args.wyjscie = list(T14_OBRAZKI), (KATALOG_T14 if args.wyjscie == KATALOG_DOMYSLNY else args.wyjscie)
    nazwy = args.tylko or list(ZRZUTY)
    nieznane = [n for n in nazwy if n not in ZRZUTY]
    if nieznane:
        print(f"BLAD: nieznany zrzut: {', '.join(nieznane)} (znane: {', '.join(ZRZUTY)})", file=sys.stderr)
        return 2
    przygotuj_qt()
    razem = 0
    for nazwa in nazwy:
        plik = zrob(nazwa, args.wyjscie)
        razem += plik.stat().st_size
        print(f"{plik.name}: {plik.stat().st_size} B - {ZRZUTY[nazwa][2]}")
    print(f"zrzutow: {len(nazwy)}, razem {razem} B, katalog: {args.wyjscie}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
