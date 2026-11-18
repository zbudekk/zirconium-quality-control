"""ui (E3-A3b): ekran wieczorny - okno ``stanowisko.ui.utworz_okno(kontroler, lacznik)`` sterowane z testu jak przez technika
(klikniecia mysza i klawisze), tryb offscreen, dane sztuczne.

Kryteria paczki (raport ``raporty/E3-A3b_2026-11-17.md``):
  (1) mapa ma kolory rowne stanowi w 100 % gniazd dla kazdego scenariusza atrapy (i na prawdziwym kontrolerze),
  (2) klik w czerwone gniazdo -> widok pracy z rozmiarem ubytku; "Ukruszona" / "OK" / "Cofnij" wysyla wlasciwe polecenie,
      ekran odswieza liste "do dofrezowania",
  (3) Spacja wywoluje "start skanu" dokladnie raz,
  (4) kazdy rodzaj pytania / komunikatu daje wlasciwy panel i przyciski, nic zielonego tam, gdzie stan tego zabrania;
      bez wybranej osoby przyciski decyzji nieaktywne z wyjasnieniem,
  (5) okno zamkniete i otwarte ponownie na tym samym stanie wyglada tak samo (takze po restarcie programu),
  (6) przerwy petli okna ponizej 200 ms przy 10 plytkach x 19 prac i podczas przychodzenia zdarzen,
  (7) liczba projektow w puli i "Odswiez pule" na ekranie,
  (8) 0 sciezek i nazw plikow w tekstach wszystkich widzetow dla wszystkich scenariuszy atrapy,
  (9) piec zadan wieczornych T14 sterowaniem z testu, bez zagladania do kontrolera inaczej niz przez ekran.

Napisy ekranu sa brane ze ``statusy`` i ``ui.napisy`` (ten plik jest ASCII). Prog przerwy petli: 200 ms; E3A3_LUZNE=1 podnosi
go do 1 s na komputerze obciazonym przez inne sesje - wartosc zmierzona jest wypisywana (pytest -s).
"""
from __future__ import annotations

import contextlib
import datetime as dt
import os
import re
import time
from pathlib import Path

import pytest

import test_kontroler_api as TK
from test_kontroler_api import FOLDER_ZLECENIA, StanowiskoAplikacji

PROG_PRZERWY_S = 1.0 if os.environ.get("E3A3_LUZNE") == "1" else 0.2
START = dt.datetime(2026, 11, 17, 19, 0, 0)  # wtorek, zmiana 2
FONTY_WINDOWS = Path(r"C:\Windows\Fonts")
ROZMIAR_OKNA = (1600, 900)


@pytest.fixture(scope="module", autouse=True)
def _qt_przed_silnikiem():
    """Qt ladowane przed pierwszym uzyciem silnika (kolejnosc jak w aplikacji); czcionki systemu dla trybu offscreen."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    if FONTY_WINDOWS.is_dir():
        os.environ.setdefault("QT_QPA_FONTDIR", str(FONTY_WINDOWS))
    import PySide6.QtCore  # noqa: F401
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    assert app.platformName() == "offscreen"
    yield app


# ----------------------------------------------------------------------------
# narzedzia: zegar, szpieg polecen, ekran sterowany jak przez technika
# ----------------------------------------------------------------------------
class Zegar:
    def __init__(self):
        self.teraz = START

    def __call__(self) -> dt.datetime:
        return self.teraz

    def przesun(self, minut: float) -> None:
        self.teraz += dt.timedelta(minutes=minut)


class Szpieg:
    """Kontroler z zapisem polecen wyslanych przez okno: ``polecenia`` = lista (nazwa, argumenty). Reszta bez zmian."""

    def __init__(self, kontroler):
        self._k = kontroler
        self.polecenia: list = []

    def __getattr__(self, nazwa):
        from stanowisko import kontroler_api as K

        cel = getattr(self._k, nazwa)
        if nazwa not in K.POLECENIA:
            return cel

        def polecenie(*argumenty, **kw):
            self.polecenia.append((nazwa, argumenty))
            return cel(*argumenty, **kw)

        return polecenie

    def wykonaj(self, polecenie, *argumenty):
        from stanowisko import kontroler_api as K

        if polecenie not in K.POLECENIA:
            return self._k.wykonaj(polecenie, *argumenty)
        return getattr(self, polecenie)(*argumenty)

    def wyslane(self, *nazwy) -> list:
        return [p for p in self.polecenia if not nazwy or p[0] in nazwy]


class Podstawiony(Szpieg):
    """Kontroler, ktory na wskazane polecenia odpowiada gotowa ``Odpowiedz`` (bez wykonania) - proba odmow spoza stanu."""

    def __init__(self, kontroler, odpowiedzi: dict):
        super().__init__(kontroler)
        self.odpowiedzi = odpowiedzi

    def wykonaj(self, polecenie, *argumenty):
        if polecenie in self.odpowiedzi:
            self.polecenia.append((polecenie, argumenty))
            return self.odpowiedzi[polecenie]
        return super().wykonaj(polecenie, *argumenty)


def podmien_zywe(atrapa, **pola) -> None:
    """Czesc "zywa" stanu atrapy (``kolejka``, ``pula``, ``skaner``, ``analiza``) podmieniona na podane obiekty kontraktu."""
    prawdziwe = type(atrapa)._stan_zywy

    def zywe():
        return {**prawdziwe(atrapa), **pola}

    atrapa._stan_zywy = zywe
    atrapa._odswiez_zywe()


def teksty_widzetu(w) -> list:
    """Wszystkie napisy jednego widzetu: tekst, podpowiedzi, tytuly, komorki tabeli, napisy rysowane na mapie."""
    from PySide6.QtWidgets import QTableWidget

    wynik = []
    for nazwa in ("text", "windowTitle", "toolTip", "statusTip", "whatsThis", "accessibleName", "accessibleDescription", "placeholderText",
                  "title", "format"):
        f = getattr(w, nazwa, None)
        if not callable(f):
            continue
        try:
            v = f()
        except (TypeError, RuntimeError):
            continue
        if isinstance(v, str) and v:
            wynik.append(v)
    if isinstance(w, QTableWidget):
        for k in range(w.columnCount()):
            if w.horizontalHeaderItem(k) is not None:
                wynik.append(w.horizontalHeaderItem(k).text())
        for r in range(w.rowCount()):
            for k in range(w.columnCount()):
                if w.item(r, k) is not None:
                    wynik += [t for t in (w.item(r, k).text(), w.item(r, k).toolTip()) if t]
    if hasattr(w, "teksty_rysowane"):
        wynik += list(w.teksty_rysowane())
    return wynik


class Ekran:
    """Okno wieczorne na kontrolerze ``k``: pokazane (offscreen) w rozmiarze 1600 x 900 (albo ``rozmiar``) i sterowane myszka
    i klawiatura. Po zmianie zawartosci mapy okno przez chwile pomija klikniecia mapy i skroty decyzji (A-P2) - technik widzi
    przygaszona mape i czeka; tak samo czekaja ``klik_gniazdo``, klawisze decyzji, odczyt pikseli i obraz okna."""

    def __init__(self, kontroler, rozmiar: tuple = ROZMIAR_OKNA):
        from PySide6.QtTest import QTest

        from stanowisko import kontroler_api as K
        from stanowisko import ui

        self.k = kontroler
        self.lacznik = K.lacznik_qt(kontroler)
        self.okno = ui.utworz_okno(kontroler, self.lacznik)
        self.okno.resize(*rozmiar)
        self.okno.show()
        QTest.qWaitForWindowExposed(self.okno)
        self.odczekaj()

    def po_ochronie(self) -> None:
        """Czeka, az mapa przestanie byc przygaszona po zmianie zawartosci (A-P2, ``okno.OCHRONA_MS``)."""
        self.czekaj(lambda: not self.okno.ochrona_aktywna(), 5.0, "koniec przygaszenia mapy")

    @contextlib.contextmanager
    def bez_zegara(self):
        """Zegar lacznika (co 30 ms ``kontroler.przetworz()``) zatrzymany: test sprawdza stan przejsciowy bez wyscigu z tyknieciem
        (A-P4); ``przetworz()`` wola wtedy sam test."""
        self.lacznik._zegar.stop()
        try:
            yield
        finally:
            self.lacznik._zegar.start()

    @property
    def mapa(self):
        return self.okno.mapa

    def zdarzenia(self) -> None:
        """Ekran dostaje czas na pokazanie nowych elementow (Qt pokazuje widzety dodane do ukladu w nastepnym obiegu petli)."""
        from PySide6.QtWidgets import QApplication

        QApplication.sendPostedEvents()
        QApplication.processEvents()

    def odczekaj(self, ms: int = 30) -> None:
        from PySide6.QtTest import QTest

        QTest.qWait(ms)

    def czekaj(self, warunek, limit_s: float = 20.0, co: str = "") -> None:
        koniec = time.monotonic() + limit_s
        while not warunek():
            assert time.monotonic() < koniec, f"nie doczekalem sie: {co}\n{self.tekst()}"
            self.odczekaj(10)

    def w(self, nazwa: str):
        from PySide6.QtWidgets import QWidget

        w = self.okno.findChild(QWidget, nazwa)
        assert w is not None, f"na ekranie nie ma elementu {nazwa!r}"
        return w

    def jest(self, nazwa: str) -> bool:
        """Element o tej nazwie jest na ekranie i jest widoczny."""
        from PySide6.QtWidgets import QWidget

        self.zdarzenia()
        w = self.okno.findChild(QWidget, nazwa)
        return w is not None and w.isVisibleTo(self.okno)

    def aktywny(self, nazwa: str) -> bool:
        return self.jest(nazwa) and self.w(nazwa).isEnabled()

    def klik(self, nazwa: str) -> None:
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest

        self.zdarzenia()
        if nazwa.startswith("poza_"):  # przyciski prac poza gniazdem sa czescia mapy
            self.po_ochronie()
        w = self.w(nazwa)
        assert w.isVisibleTo(self.okno), f"element {nazwa!r} nie jest widoczny\n{self.tekst()}"
        assert w.isEnabled(), f"element {nazwa!r} jest nieaktywny"
        QTest.mouseClick(w, Qt.MouseButton.LeftButton)
        self.odczekaj(5)

    def klik_gniazdo(self, nr: int) -> None:
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest

        self.zdarzenia()
        self.po_ochronie()
        QTest.mouseClick(self.mapa, Qt.MouseButton.LeftButton, pos=self.mapa.srodek_gniazda(nr).toPoint())
        self.odczekaj(5)

    def klawisz(self, klawisz) -> None:
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest

        if klawisz in (Qt.Key.Key_U, Qt.Key.Key_O, Qt.Key.Key_C, Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.zdarzenia()
            self.po_ochronie()
        QTest.keyClick(self.okno, klawisz)
        self.odczekaj(5)

    def teksty(self, tylko_widoczne: bool = True) -> list:
        from PySide6.QtWidgets import QWidget

        self.zdarzenia()
        wynik = teksty_widzetu(self.okno)
        for w in self.okno.findChildren(QWidget):
            if not tylko_widoczne or w.isVisibleTo(self.okno):
                wynik += teksty_widzetu(w)
        return wynik

    def tekst(self, tylko_widoczne: bool = True) -> str:
        return "\n".join(self.teksty(tylko_widoczne))

    def tekst_elementu(self, nazwa: str) -> str:
        """Napisy elementu ``nazwa`` i wszystkiego, co w nim lezy."""
        from PySide6.QtWidgets import QWidget

        self.zdarzenia()
        w = self.w(nazwa)
        return "\n".join(teksty_widzetu(w) + [t for d in w.findChildren(QWidget) for t in teksty_widzetu(d)])

    def kolory_pikseli(self) -> dict:
        """Numer gniazda -> kolor piksela mapy wewnatrz gniazda (z obrazu widzetu, nie z danych)."""
        self.zdarzenia()
        self.po_ochronie()
        obraz = self.mapa.grab().toImage()
        return {nr: obraz.pixelColor(self.mapa.punkt_probny(nr).toPoint()).name() for nr in self.mapa.numery()}

    def lista(self) -> list:
        """Wiersze tabeli "do dofrezowania" jako listy napisow."""
        t = self.w("tabela_dofrezowania")
        return [[t.item(r, k).text() if t.item(r, k) is not None else "" for k in range(t.columnCount())] for r in range(t.rowCount())]

    def plytki(self) -> list:
        """skan_id plytek widocznych na liscie plytek (kafelki ``plytka_<id>``)."""
        from PySide6.QtWidgets import QWidget

        self.zdarzenia()
        return sorted(int(w.objectName().split("_")[1]) for w in self.okno.findChildren(QWidget)
                      if re.fullmatch(r"plytka_\d+", w.objectName()) and w.isVisibleTo(self.okno))

    def obraz(self):
        self.zdarzenia()
        self.po_ochronie()
        return self.okno.grab().toImage()

    def zamknij(self) -> None:
        self.okno.close()
        self.lacznik.zatrzymaj()
        self.odczekaj(5)


@pytest.fixture
def zegar():
    return Zegar()


@pytest.fixture
def atrapa(tmp_path, zegar):
    from stanowisko import kontroler_api as K

    k = K.AtrapaKontrolera(tmp_path / "atrapa", zegar=zegar)
    yield k
    k.zamknij()


@pytest.fixture
def ekrany():
    """Funkcja ``nowy(kontroler) -> Ekran``; wszystkie okna sa zamykane po tescie."""
    otwarte = []

    def nowy(kontroler, rozmiar: tuple = ROZMIAR_OKNA) -> Ekran:
        e = Ekran(kontroler, rozmiar)
        otwarte.append(e)
        return e

    yield nowy
    for e in otwarte:
        e.zamknij()


@pytest.fixture
def stanowiska(tmp_path):
    """Funkcja ``nowe() -> StanowiskoAplikacji`` (prawdziwy kontroler, symulator skanera = plik zapisany do folderu skanera,
    analiza sztuczna w procesie silnika); kolejne wywolanie = ponowny start programu na tych samych danych."""
    utworzone = []

    def nowe(**parametry):
        st = StanowiskoAplikacji(tmp_path, **parametry)
        utworzone.append(st)
        return st

    yield nowe
    for st in utworzone:
        st.koniec()


def nic_zielonego(e: Ekran) -> None:
    """Na mapie nie ma zadnego gniazda w kolorze ani z podpisem statusu zielonego (dane rysowane i piksele)."""
    from stanowisko import statusy as ST

    zielone = {ST.STATUSY[k].hex for k in ST.STATUSY_ZIELONE}
    napisy = {ST.STATUSY[k].napis for k in ST.STATUSY_ZIELONE}
    assert not zielone & set(e.mapa.kolory().values()), e.mapa.kolory()
    assert not zielone & set(e.kolory_pikseli().values()), e.kolory_pikseli()
    assert not napisy & set(e.mapa.podpisy().values()), e.mapa.podpisy()


def mapa_rowna_stanowi(e: Ekran, plytka) -> int:
    """Kolor (dane rysowane i piksel) oraz podpis kazdego gniazda plytki na mapie = stan; zwraca liczbe gniazd."""
    from stanowisko import statusy as ST

    assert e.okno.pokazana_plytka() == plytka.skan_id
    gniazda = plytka.gniazda if plytka.aktywna or plytka.prace else ()  # skan bez prac, ktory sie nie liczy: napis zamiast gniazd
    assert sorted(e.mapa.numery()) == [g.nr for g in gniazda]
    kolory, piksele, podpisy = e.mapa.kolory(), e.kolory_pikseli(), e.mapa.podpisy()
    for g in gniazda:
        assert kolory[g.nr] == g.rgb == ST.status(g.status).hex, (g.nr, g.status, kolory[g.nr], g.rgb)
        assert piksele[g.nr] == g.rgb, (g.nr, g.status, piksele[g.nr], g.rgb)
        assert podpisy[g.nr] == g.podpis, (g.nr, podpisy[g.nr], g.podpis)
    return len(gniazda)


# ----------------------------------------------------------------------------
# (1) mapa = stan w 100 % gniazd
# ----------------------------------------------------------------------------
@pytest.mark.parametrize("rodzaj", ["zwykla", "czysta", "do_powtorzenia", "niezgodny_uklad", "nie_z_trybu", "bez_numeru", "blad"])
def test_1_mapa_ma_kolory_stanu_dla_kazdego_rodzaju_skanu(atrapa, ekrany, rodzaj):
    from stanowisko import kontroler_api as K

    atrapa.wybierz_operatora("Technik A")
    e = ekrany(atrapa)
    skan_id = atrapa.symuluj_skan(rodzaj)  # skan przychodzi, gdy okno juz stoi (sygnal stanu)
    plytka = atrapa.stan().plytka(skan_id)
    assert e.plytki() == [skan_id] and e.jest(f"plytka_{skan_id}")
    ile = mapa_rowna_stanowi(e, plytka)
    if rodzaj in ("zwykla", "czysta"):
        wynik = K.sztuczny_wynik("wieczorna", 1, {"zwykla": TK.ZESTAW_ZWYKLY, "czysta": dict.fromkeys(range(1, 5), "zielony")}[rodzaj])
        prawda = K.kolory_oczekiwane(wynik)
        assert {g.nr: g.kolor for g in plytka.gniazda if g.prace} == {nr: kolor for (nr, _), kolor in prawda.items()}
        assert ile == 19  # wszystkie gniazda ukladu, takze puste
    if rodzaj in ("do_powtorzenia", "niezgodny_uklad", "nie_z_trybu", "bez_numeru", "blad"):
        nic_zielonego(e)
    if rodzaj in ("niezgodny_uklad", "blad"):
        assert ile == 0 and plytka.napis in e.mapa.teksty_rysowane()  # zamiast gniazd: napis, co sie stalo


def test_1_scenariusz_pokazowy_kazda_plytka_i_decyzje(atrapa, ekrany):
    """Piec plytek pokazu (z decyzjami "Ukruszona" i "OK"): po przelaczeniu na kazda plytke mapa = stan; liczniki na kafelkach."""
    skany = atrapa.scenariusz_pokazowy()
    e = ekrany(atrapa)
    stan = atrapa.stan()
    assert e.plytki() == sorted(skany.values())
    assert e.okno.pokazana_plytka() == stan.biezaca_plytka  # po otwarciu: ostatnia plytka
    gniazd = 0
    for nazwa, skan_id in skany.items():
        e.klik(f"plytka_{skan_id}")
        plytka = stan.plytka(skan_id)
        gniazd += mapa_rowna_stanowi(e, plytka)
        liczniki = e.w(f"plytka_{skan_id}").liczniki()  # klasa koloru -> liczba pokazana na kafelku
        assert liczniki == {k: n for k, n in plytka.liczniki.items() if n}, (nazwa, liczniki, plytka.liczniki)
        if nazwa in ("do_powtorzenia", "nie_z_trybu", "bez_numeru"):
            nic_zielonego(e)
    assert gniazd == 19 * 4 + 24  # 4 plytki wieczorne po 19 gniazd + poranna 24


def test_1_prawdziwy_kontroler_symulator_skanera(stanowiska, ekrany):
    """Plik zapisany do folderu skanera -> analiza w procesie silnika -> mapa okna = wynik analizy po decyzjach, 100 % gniazd."""
    from stanowisko import kontroler_api as K
    from stanowisko import statusy as ST

    st = stanowiska()
    e = ekrany(st.k)
    e.klik("osoba_0")
    skan_id = st.wrzuc("zwykla")
    e.czekaj(lambda: e.okno.pokazana_plytka() == skan_id, co="plytka na ekranie")
    assert mapa_rowna_stanowi(e, st.stan().plytka(skan_id)) == 19
    e.klik_gniazdo(2)
    e.klik("przycisk_ukruszona")
    e.klik_gniazdo(9)
    e.klik("przycisk_ok")
    prawda = K.kolory_oczekiwane(st.wynik(st.opis("zwykla", 1, None, None, None, 0)), {(2, 1): "ukruszona", (9, 1): "ok"})
    kolory = e.kolory_pikseli()
    for (nr, _), klasa in prawda.items():
        assert kolory[nr] == ST.status(st.stan().plytka(skan_id).gniazdo(nr).status).hex
        assert st.stan().plytka(skan_id).gniazdo(nr).kolor == klasa
    assert kolory[2] == ST.STATUSY["ukruszona"].hex and kolory[9] == ST.STATUSY["zatwierdzona_ok"].hex
    assert mapa_rowna_stanowi(e, st.stan().plytka(skan_id)) == 19


# ----------------------------------------------------------------------------
# (2) widok pracy i decyzje
# ----------------------------------------------------------------------------
def test_2_czerwone_gniazdo_widok_pracy_decyzje_i_lista(atrapa, ekrany):
    from PySide6.QtCore import Qt

    from stanowisko import statusy as ST
    from stanowisko.ui import napisy as N

    k = Szpieg(atrapa)
    k.wybierz_operatora("Technik A")
    skan_id = atrapa.symuluj_skan("zwykla")
    e = ekrany(k)
    praca = atrapa.stan().plytka(skan_id).gniazdo(2).praca
    assert not e.jest("widok_pracy") and e.lista() == []
    e.klik_gniazdo(2)
    assert e.jest("widok_pracy")
    widok = e.tekst_elementu("widok_pracy")
    assert "0,62" in widok and ST.STATUSY["czerwony"].napis in widok and ST.STATUSY["czerwony"].opis in widok  # rozmiar najwiekszego ubytku
    assert N.LICZBA_UBYTKOW.format(n=1) in widok and "9002" in widok and "K-1" in widok  # liczba ubytkow, kuweta, krazek
    e.czekaj(lambda: e.w("praca_obraz").pixmap() is not None and not e.w("praca_obraz").pixmap().isNull(), co="obraz odchylek")
    assert e.w("praca_obraz").pixmap().width() >= 300
    for nazwa in ("przycisk_ukruszona", "przycisk_ok", "przycisk_cofnij"):
        assert e.jest(nazwa) and e.w(nazwa).height() >= 56  # duze przyciski
    assert e.aktywny("przycisk_ukruszona") and e.aktywny("przycisk_ok") and not e.aktywny("przycisk_cofnij")
    assert ST.PRZYCISKI["ukruszona"] in e.w("przycisk_ukruszona").text() and ST.PRZYCISKI["ok"] in e.w("przycisk_ok").text()

    k.polecenia.clear()
    e.klik("przycisk_ukruszona")
    assert k.polecenia == [("ukruszona", (praca.praca_id,))]
    assert atrapa.stan().praca(praca.praca_id).decyzja == "ukruszona"
    wiersze = e.lista()
    assert len(wiersze) == 1 and "9002" in wiersze[0] and "12" in wiersze[0] and "K-1" in wiersze[0]  # kuweta, zab, krazek
    assert any("17.11" in x for x in wiersze[0]) and "2" in wiersze[0]  # doba i zmiana
    assert e.mapa.podpisy()[2] == ST.STATUSY["ukruszona"].napis
    assert e.aktywny("przycisk_cofnij") and e.aktywny("przycisk_ok") and not e.aktywny("przycisk_ukruszona")

    e.klik("przycisk_ok")
    assert k.polecenia[-1] == ("ok", (praca.praca_id,)) and e.lista() == []
    assert e.mapa.podpisy()[2] == ST.STATUSY["zatwierdzona_ok"].napis and e.kolory_pikseli()[2] == ST.STATUSY["zatwierdzona_ok"].hex
    e.klik("przycisk_cofnij")  # cofa "OK": wraca "Ukruszona" i pozycja listy
    assert k.polecenia[-1] == ("cofnij", (praca.praca_id,)) and len(e.lista()) == 1
    e.klik("przycisk_cofnij")
    assert e.lista() == [] and e.mapa.podpisy()[2] == ST.STATUSY["czerwony"].napis
    assert [p[0] for p in k.polecenia] == ["ukruszona", "ok", "cofnij", "cofnij"]

    # skroty klawiszowe przy otwartej pracy: U, O, C; Esc zamyka widok
    k.polecenia.clear()
    e.klawisz(Qt.Key.Key_U)
    e.klawisz(Qt.Key.Key_O)
    e.klawisz(Qt.Key.Key_C)
    assert k.polecenia == [("ukruszona", (praca.praca_id,)), ("ok", (praca.praca_id,)), ("cofnij", (praca.praca_id,))]
    e.klawisz(Qt.Key.Key_Escape)
    assert not e.jest("widok_pracy")
    e.klawisz(Qt.Key.Key_U)  # bez otwartej pracy klawisz decyzji nic nie robi
    assert len(k.polecenia) == 3


def test_2_ukruszona_na_pracy_ktorej_program_nie_oznaczyl(atrapa, ekrany):
    """Technik moze oznaczyc "Ukruszona" takze prace zielona (program jej nie wskazal): pozycja trafia na liste."""
    from stanowisko import statusy as ST

    atrapa.wybierz_operatora("Technik A")
    skan_id = atrapa.symuluj_skan("zwykla")
    e = ekrany(atrapa)
    e.klik_gniazdo(1)
    assert ST.STATUSY["zielony"].opis in e.tekst_elementu("widok_pracy")
    e.klik("przycisk_ukruszona")
    praca = atrapa.stan().plytka(skan_id).gniazdo(1).praca
    assert praca.decyzja == "ukruszona_niewykryta" and len(e.lista()) == 1 and "9001" in e.lista()[0]
    assert e.kolory_pikseli()[1] == ST.STATUSY["ukruszona"].hex


def test_2_lista_ta_doba_i_wszystkie_otwarte_oraz_zab_juz_na_liscie(atrapa, ekrany, zegar):
    """Lista: domyslnie "ta doba", przelacznik "wszystkie otwarte"; widok pracy mowi "ten zab jest juz na liscie"."""
    from stanowisko import statusy as ST

    atrapa.wybierz_operatora("Technik A")
    wczoraj = atrapa.symuluj_skan("zwykla", numer=1)
    atrapa.ukruszona(atrapa.stan().plytka(wczoraj).gniazdo(2).praca.praca_id)
    zegar.przesun(24 * 60)  # nastepna doba robocza, ta sama zmiana
    atrapa.przetworz()
    atrapa.wybierz_operatora("Technik A")
    dzis = atrapa.symuluj_skan("zwykla", numer=1, projekty={2: 2, 9: 9})  # ten sam projekt w gniezdzie 2 (zab dofrezowany)
    atrapa.ukruszona(atrapa.stan().plytka(dzis).gniazdo(9).praca.praca_id)
    e = ekrany(atrapa)
    assert e.w("lista_ta_doba").isChecked() and not e.w("lista_wszystkie").isChecked()
    assert [w[0] for w in e.lista()] == ["9009"]  # tylko pozycja tej doby
    e.klik("lista_wszystkie")
    assert sorted(w[0] for w in e.lista()) == ["9002", "9009"]
    assert any("17.11" in x for w in e.lista() for x in w) and any("18.11" in x for w in e.lista() for x in w)
    e.klik("lista_ta_doba")
    assert [w[0] for w in e.lista()] == ["9009"]
    e.klik_gniazdo(2)  # praca tego samego projektu, co pozycja z wczoraj
    praca = atrapa.stan().plytka(dzis).gniazdo(2).praca
    assert praca.na_liscie is not None and not praca.na_liscie.ta_praca and praca.na_liscie.tekst
    assert e.jest("praca_na_liscie") and praca.na_liscie.tekst in e.tekst_elementu("widok_pracy")
    assert ST.ZAB_JUZ_NA_LISCIE.format(doba="2026-11-17", zmiana=2) == praca.na_liscie.tekst
    e.klik_gniazdo(3)
    assert not e.jest("praca_na_liscie")


# ----------------------------------------------------------------------------
# (3) Spacja = start skanu
# ----------------------------------------------------------------------------
def test_3_spacja_start_skanu_dokladnie_raz(atrapa, ekrany):
    from PySide6.QtCore import QEvent, Qt
    from PySide6.QtGui import QKeyEvent
    from PySide6.QtWidgets import QApplication

    from stanowisko.ui import napisy as N

    k = Szpieg(atrapa)
    k.wybierz_operatora("Technik A")
    skan_id = atrapa.symuluj_skan("zwykla")
    e = ekrany(k)
    k.polecenia.clear()
    e.klawisz(Qt.Key.Key_Space)
    assert k.polecenia == [("start_skanu", ())] and len(atrapa.starty_skanu) == 1
    assert N.SKANER_CZEKA in e.tekst()  # ekran mowi, ze czeka na skan
    # przytrzymana Spacja (autopowtarzanie klawiatury) nie startuje kolejnych skanow
    QApplication.sendEvent(e.okno, QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Space, Qt.KeyboardModifier.NoModifier, " ", True))
    assert len(atrapa.starty_skanu) == 1
    # po kliknieciu przycisku decyzji Spacja nadal jest TYLKO startem skanu (nie "klika" ostatniego przycisku)
    e.klik_gniazdo(2)
    e.klik("przycisk_ukruszona")
    przed = list(k.polecenia)
    e.klawisz(Qt.Key.Key_Space)
    assert k.polecenia == przed + [("start_skanu", ())] and len(atrapa.starty_skanu) == 2
    assert atrapa.stan().plytka(skan_id).gniazdo(2).praca.decyzja == "ukruszona"
    e.klik("przycisk_skanuj")  # to samo przyciskiem
    assert len(atrapa.starty_skanu) == 3


def test_3_spacja_prawdziwy_kontroler(stanowiska, ekrany):
    from PySide6.QtCore import Qt

    st = stanowiska()
    e = ekrany(st.k)
    e.klawisz(Qt.Key.Key_Space)
    assert st.starty_skanu() == 1 and st.stan().skaner.startow_skanu == 1


# ----------------------------------------------------------------------------
# (4) pytania i komunikaty
# ----------------------------------------------------------------------------
def test_4_bez_osoby_decyzje_nieaktywne_z_wyjasnieniem(atrapa, ekrany):
    from PySide6.QtCore import Qt

    from stanowisko import statusy as ST

    k = Szpieg(atrapa)
    skan_id = atrapa.symuluj_skan("zwykla")
    e = ekrany(k)
    assert e.jest("panel_osoba") and e.jest("osoba_0") and e.jest("osoba_1")
    assert [e.w("osoba_0").text(), e.w("osoba_1").text()] == ["Technik A", "Technik B"]
    wyjasnienie = ST.tekst_komunikatu("brak_operatora")[2]
    assert wyjasnienie in e.tekst_elementu("panel_osoba")
    e.klik_gniazdo(2)
    for nazwa in ("przycisk_ukruszona", "przycisk_ok", "przycisk_cofnij"):
        assert e.jest(nazwa) and not e.aktywny(nazwa)
    assert e.jest("praca_wyjasnienie") and e.w("praca_wyjasnienie").text() == wyjasnienie
    e.klawisz(Qt.Key.Key_U)  # skrot tez nie dziala
    assert k.wyslane("ukruszona", "ok", "cofnij") == [] and atrapa.stan().plytka(skan_id).gniazdo(2).praca.decyzja is None
    e.klik("osoba_1")
    assert k.polecenia[-1] == ("wybierz_operatora", ("Technik B",)) and atrapa.stan().operator == "Technik B"
    assert not e.jest("panel_osoba") and "Technik B" in e.w("napis_osoba").text()
    assert e.aktywny("przycisk_ukruszona") and e.aktywny("przycisk_ok") and not e.jest("praca_wyjasnienie")
    e.klik("przycisk_zmien_osobe")  # zmiana osoby w trakcie zmiany
    assert e.jest("panel_osoba")
    e.klik("osoba_0")
    assert atrapa.stan().operator == "Technik A" and not e.jest("panel_osoba")


def test_4_pusta_lista_osob(tmp_path, ekrany):
    from stanowisko import kontroler_api as K
    from stanowisko import statusy as ST

    atrapa = K.AtrapaKontrolera(tmp_path / "bez_osob", operatorzy=(), zegar=Zegar())
    try:
        atrapa.symuluj_skan("zwykla")
        e = ekrany(atrapa)
        assert e.jest("panel_osoba") and not e.jest("osoba_0")
        assert ST.tekst_komunikatu("pusta_lista_operatorow")[2] in e.tekst_elementu("panel_osoba")
        e.klik_gniazdo(2)
        assert not e.aktywny("przycisk_ukruszona") and e.w("praca_wyjasnienie").text() == ST.tekst_komunikatu("pusta_lista_operatorow")[2]
        e.zamknij()
    finally:
        atrapa.zamknij()


def test_4_ponowny_skan_ostrzezenie_o_decyzjach_przed_potwierdzeniem(atrapa, ekrany, zegar):
    from stanowisko import statusy as ST

    k = Szpieg(atrapa)
    k.wybierz_operatora("Technik A")
    pierwszy = atrapa.symuluj_skan("zwykla", numer=1)
    plytka = atrapa.stan().plytka(pierwszy)
    atrapa.ukruszona(plytka.gniazdo(2).praca.praca_id)
    atrapa.ok(plytka.gniazdo(9).praca.praca_id)
    atrapa.ok(plytka.gniazdo(3).praca.praca_id)
    e = ekrany(k)
    assert len(e.lista()) == 1
    zegar.przesun(5)
    drugi = atrapa.symuluj_skan("zwykla", numer=1)
    # na pokazanej plytce zostaly prace do obejrzenia: ekran nie przelacza sie sam (A-P2) - technik klika sygnal na pasku
    assert e.okno.pokazana_plytka() == pierwszy and e.jest("przycisk_nowa_plytka")
    e.klik("przycisk_nowa_plytka")
    assert e.okno.pokazana_plytka() == drugi and e.jest("pytanie_ponowny_skan")
    pytanie = atrapa.stan().pytania[0]
    assert (pytanie.liczba_decyzji, pytanie.liczba_ukruszonych) == (3, 1)
    panel = e.tekst_elementu("pytanie_ponowny_skan")
    skutek = ST.SKUTEK_Z_DECYZJAMI.format(n=3, u=1, decyzji=ST.odmiana(3, "decyzja", "decyzje", "decyzji"))
    assert pytanie.tytul in panel and skutek in panel and "5 min" in panel  # ILE decyzji i ile "Ukruszona" przepadnie
    assert e.w("pytanie_ostrzezenie").text() == skutek  # ostrzezenie jest osobnym, wyroznionym napisem
    assert e.w("odp_potwierdz_ponowny_skan").text() == ST.PRZYCISKI["potwierdz_ponowny_skan"]
    assert e.w("odp_odrzuc_ponowny_skan").text() == ST.PRZYCISKI["odrzuc_ponowny_skan"]
    assert len(e.lista()) == 1 and k.wyslane("potwierdz_ponowny_skan") == []  # przed potwierdzeniem nic sie nie zmienia
    e.klik("odp_potwierdz_ponowny_skan")
    assert k.polecenia[-1] == ("potwierdz_ponowny_skan", (drugi,))
    assert not e.jest("pytanie_ponowny_skan") and e.lista() == []
    assert atrapa.stan().plytka(pierwszy).status == "zastapiony"
    e.klik(f"plytka_{pierwszy}")
    nic_zielonego(e)  # skan zastapiony niczego nie potwierdza
    assert ST.STATUSY_PLYTKI["zastapiony"] in e.tekst()
    e.klik(f"plytka_{drugi}")
    assert e.jest("plytka_cofnij_zastapienie")  # pomylke da sie cofnac
    e.klik("plytka_cofnij_zastapienie")
    assert k.polecenia[-1] == ("cofnij_zastapienie", (drugi,)) and len(e.lista()) == 1


def test_4_ponowny_skan_nowy_wsad_i_bez_osoby(atrapa, ekrany, zegar):
    from stanowisko import statusy as ST

    k = Szpieg(atrapa)
    pierwszy = atrapa.symuluj_skan("czysta", numer=2)
    zegar.przesun(10)
    drugi = atrapa.symuluj_skan("czysta", numer=2)
    e = ekrany(k)
    assert e.jest("pytanie_ponowny_skan") and ST.SKUTEK_BEZ_DECYZJI in e.tekst_elementu("pytanie_ponowny_skan")
    assert not e.aktywny("odp_potwierdz_ponowny_skan") and not e.aktywny("odp_odrzuc_ponowny_skan")  # bez osoby: nieaktywne
    assert ST.tekst_komunikatu("brak_operatora")[2] in e.tekst_elementu("pytanie_ponowny_skan")
    e.klik("osoba_0")
    e.klik("odp_odrzuc_ponowny_skan")
    assert k.polecenia[-1] == ("odrzuc_ponowny_skan", (drugi,)) and not e.jest("pytanie_ponowny_skan")
    assert atrapa.stan().plytka(pierwszy).status == "przyjety" and atrapa.stan().plytka(drugi).status == "przyjety"


def test_4_plytka_poranna_w_trybie_wieczor_blokada(atrapa, ekrany):
    from stanowisko import statusy as ST
    from stanowisko.ui import napisy as N

    k = Szpieg(atrapa)
    skan_id = atrapa.symuluj_skan("nie_z_trybu")
    e = ekrany(k)
    assert e.jest("pytanie_plytka_nie_z_trybu")
    panel = e.tekst_elementu("pytanie_plytka_nie_z_trybu")
    pytanie = atrapa.stan().pytania[0]
    assert pytanie.tytul in panel and pytanie.tekst in panel and ST.JAKA_PLYTKA["poranna"] in panel
    assert N.RADA_PLYTKA_PORANNA in panel  # jasna rada: przeloz prace na wieczorna i zeskanuj ponownie
    nic_zielonego(e)
    assert set(e.mapa.podpisy().values()) <= {ST.STATUSY["plytka_nie_z_trybu"].napis, ""}
    assert e.w("odp_zamknij_pytanie").text() == ST.PRZYCISK_ZESKANUJE_WLASCIWA and e.aktywny("odp_zamknij_pytanie")
    assert e.w("odp_dopusc_plytke").text() == ST.PRZYCISKI["dopusc_plytke"]
    assert not e.aktywny("odp_dopusc_plytke")  # swiadome dopuszczenie tylko dla wybranej osoby
    assert ST.tekst_komunikatu("brak_operatora")[2] in panel
    e.klik_gniazdo(3)  # praca czerwona wg programu: na zablokowanej plytce bez decyzji
    assert not e.aktywny("przycisk_ukruszona") and not e.aktywny("przycisk_ok")
    assert ST.STATUSY_PLYTKI["plytka_nie_z_trybu"] in e.w("praca_wyjasnienie").text()
    e.klik("osoba_0")
    assert e.aktywny("odp_dopusc_plytke")
    e.klik("odp_dopusc_plytke")
    assert k.polecenia[-1] == ("dopusc_plytke", (skan_id,)) and not e.jest("pytanie_plytka_nie_z_trybu")
    assert atrapa.stan().plytka(skan_id).status == "przyjety" and mapa_rowna_stanowi(e, atrapa.stan().plytka(skan_id)) == 24
    assert ST.STATUSY["zielony"].hex in e.kolory_pikseli().values()
    assert e.jest("plytka_cofnij_dopuszczenie")
    # swiadome dopuszczenie zostaje widoczne dla nastepnej osoby: staly znacznik przy naglowku mapy i na kafelku (A-P5 poz. 5)
    dopuszczona = N.PLYTKA_DOPUSZCZONA.format(jaka=ST.JAKA_PLYTKA["poranna"])
    assert e.jest("plytka_dopuszczona") and e.w("plytka_dopuszczona").text() == dopuszczona and dopuszczona in e.tekst_elementu(f"plytka_{skan_id}")
    e.klik("plytka_cofnij_dopuszczenie")
    assert k.polecenia[-1] == ("cofnij_dopuszczenie", (skan_id,))
    nic_zielonego(e)
    assert not e.jest("plytka_dopuszczona") and dopuszczona not in e.tekst_elementu(f"plytka_{skan_id}")


def test_4_plytka_nie_z_trybu_zeskanuje_wlasciwa_i_powrot_do_pytania(atrapa, ekrany):
    """"Zeskanuje wlasciwa plytke" chowa pytanie; plytka zostaje zablokowana, a dopuszczenie jest nadal dostepne przy plytce."""
    k = Szpieg(atrapa)
    k.wybierz_operatora("Technik A")
    skan_id = atrapa.symuluj_skan("nie_z_trybu")
    e = ekrany(k)
    e.klik("odp_zamknij_pytanie")
    assert k.polecenia[-1] == ("zamknij_pytanie", (f"plytka_nie_z_trybu:{skan_id}",))
    assert not e.jest("pytanie_plytka_nie_z_trybu") and atrapa.stan().plytka(skan_id).status == "plytka_nie_z_trybu"
    nic_zielonego(e)
    assert e.aktywny("plytka_dopusc_plytke")  # polecenie plytki ze stanu (``Plytka.dozwolone``) zostaje pod reka
    e.klik("plytka_dopusc_plytke")
    assert k.polecenia[-1] == ("dopusc_plytke", (skan_id,)) and atrapa.stan().plytka(skan_id).status == "przyjety"


def test_4_brak_numeru_plytki_podanie_cyfry(atrapa, ekrany):
    from stanowisko import statusy as ST

    k = Szpieg(atrapa)
    k.wybierz_operatora("Technik A")
    skan_id = atrapa.symuluj_skan("bez_numeru")
    e = ekrany(k)
    pytanie = atrapa.stan().pytania[0]
    assert e.jest("pytanie_brak_numeru_plytki") and pytanie.tekst in e.tekst_elementu("pytanie_brak_numeru_plytki")
    assert pytanie.numery and all(e.aktywny(f"odp_podaj_numer_plytki_{n}") and e.w(f"odp_podaj_numer_plytki_{n}").text() == str(n)
                                  for n in pytanie.numery)
    nic_zielonego(e)
    assert e.mapa.podpisy()[1] == ST.STATUSY["czeka_na_numer"].napis and e.mapa.podpisy()[2] == ST.STATUSY["czerwony"].napis
    e.klik("odp_podaj_numer_plytki_2")
    assert k.polecenia[-1] == ("podaj_numer_plytki", (skan_id, 2))
    assert not e.jest("pytanie_brak_numeru_plytki") and atrapa.stan().plytka(skan_id).numer == 2
    assert e.kolory_pikseli()[1] == ST.STATUSY["zielony"].hex and e.mapa.podpisy()[1] == ST.STATUSY["zielony"].napis


def test_4_brak_numeru_pozniej_i_bez_osoby(atrapa, ekrany):
    k = Szpieg(atrapa)
    skan_id = atrapa.symuluj_skan("bez_numeru")
    e = ekrany(k)
    assert not e.aktywny("odp_podaj_numer_plytki_1") and e.aktywny("odp_zamknij_pytanie")  # bez osoby numeru nie da sie zapisac
    e.klik("odp_zamknij_pytanie")  # "Pozniej"
    assert k.polecenia[-1] == ("zamknij_pytanie", (f"brak_numeru_plytki:{skan_id}",)) and not e.jest("pytanie_brak_numeru_plytki")
    nic_zielonego(e)
    e.klik("plytka_podaj_numer_plytki")  # numer mozna podac pozniej: polecenie plytki ze stanu
    assert e.jest("panel_numer_plytki") and not e.aktywny("odp_podaj_numer_plytki_3")  # bez osoby nieaktywne
    e.klik("osoba_0")
    e.klik("odp_podaj_numer_plytki_3")
    assert k.polecenia[-1] == ("podaj_numer_plytki", (skan_id, 3))
    assert atrapa.stan().plytka(skan_id).numer == 3 and not e.jest("panel_numer_plytki")
    e.klik("plytka_podaj_numer_plytki")  # poprawienie zle podanego numeru
    assert not e.aktywny("odp_podaj_numer_plytki_3") and e.aktywny("odp_podaj_numer_plytki_1")
    e.klik("numer_bez_zmian")
    assert not e.jest("panel_numer_plytki") and atrapa.stan().plytka(skan_id).numer == 3


def test_4_pozycje_ukryte_nie_sa_pokazywane(atrapa, ekrany):
    """D6: pytanie i komunikat zamkniete przez technika zostaja przy plytce z ``ukryte=True`` (``Plytka.pytania`` /
    ``Plytka.komunikaty``) - ekran ich nie pokazuje (ani panelu, ani znaczka "czeka na odpowiedz"), takze gdyby pozycja
    ukryta trafila do ``stan.pytania`` / ``stan.komunikaty``."""
    import dataclasses

    from stanowisko.ui import napisy as N

    k = Szpieg(atrapa)
    k.wybierz_operatora("Technik A")
    bez_numeru = atrapa.symuluj_skan("bez_numeru")
    niezgodny = atrapa.symuluj_skan("niezgodny_uklad", numer=2)
    e = ekrany(k)
    e.klik(f"plytka_{bez_numeru}")
    assert e.jest("pytanie_brak_numeru_plytki") and N.PLYTKA_PYTANIE in e.tekst_elementu(f"plytka_{bez_numeru}")
    e.klik("odp_zamknij_pytanie")  # "Pozniej"
    assert k.polecenia[-1] == ("zamknij_pytanie", (f"brak_numeru_plytki:{bez_numeru}",))
    e.klik(f"plytka_{niezgodny}")
    assert e.jest("komunikat_niezgodny_uklad")
    e.klik("zamknij_komunikat")
    assert k.polecenia[-1] == ("zamknij_komunikat", (f"niezgodny_uklad:{niezgodny}",))
    stan = atrapa.stan()
    pytanie = next(q for q in stan.plytka(bez_numeru).pytania if q.rodzaj == "brak_numeru_plytki")
    komunikat = next(x for x in stan.plytka(niezgodny).komunikaty if x.rodzaj == "niezgodny_uklad")
    assert pytanie.ukryte and komunikat.ukryte and pytanie not in stan.pytania and komunikat not in stan.komunikaty
    assert not e.jest("komunikat_niezgodny_uklad") and N.PLYTKA_PYTANIE not in e.tekst_elementu(f"plytka_{bez_numeru}")
    e.klik(f"plytka_{bez_numeru}")
    assert not e.jest("pytanie_brak_numeru_plytki") and e.aktywny("plytka_podaj_numer_plytki")  # numer nadal pod reka
    # ochrona ekranu: pozycje ukryte w stan.* (kontrakt mowi, ze ich tam nie ma) tez nie sa pokazywane
    e.okno.pokaz_stan(dataclasses.replace(stan, wersja=stan.wersja + 1, pytania=stan.pytania + (pytanie,),
                                          komunikaty=stan.komunikaty + (komunikat,)))
    assert not e.jest("pytanie_brak_numeru_plytki") and N.PLYTKA_PYTANIE not in e.tekst_elementu(f"plytka_{bez_numeru}")
    e.klik(f"plytka_{niezgodny}")
    assert not e.jest("komunikat_niezgodny_uklad")


def test_4_plytka_niezgodna_z_ukladem(atrapa, ekrany):
    from stanowisko import statusy as ST

    k = Szpieg(atrapa)
    skan_id = atrapa.symuluj_skan("niezgodny_uklad")
    e = ekrany(k)
    assert e.jest("komunikat_niezgodny_uklad")
    panel = e.tekst_elementu("komunikat_niezgodny_uklad")
    assert ST.KOMUNIKATY["niezgodny_uklad"].tytul in panel and ST.KOMUNIKATY["niezgodny_uklad"].tekst in panel
    nic_zielonego(e)
    assert e.mapa.numery() == [] and ST.STATUSY_PLYTKI["niezgodny_uklad"] in e.tekst()
    assert e.w("zamknij_komunikat").text() == ST.PRZYCISKI["zamknij_komunikat"]
    e.klik("zamknij_komunikat")
    assert k.polecenia[-1] == ("zamknij_komunikat", (f"niezgodny_uklad:{skan_id}",)) and not e.jest("komunikat_niezgodny_uklad")


@pytest.mark.parametrize("wada, powod", [("skan_ponownie", "skan_ponownie"), ("popraw_ulozenie", "popraw_ulozenie")])
def test_4_skan_ponownie_i_popraw_ulozenie(atrapa, ekrany, wada, powod):
    """Drgniecie ("skan ponownie") i "popraw ulozenie": komunikat z powodem i numerem gniazda, nic zielonego, bez decyzji."""
    from stanowisko import statusy as ST

    atrapa.wybierz_operatora("Technik A")
    atrapa.symuluj_skan("do_powtorzenia", gniazda={1: "zielony", 2: wada, 4: "czerwony"})
    e = ekrany(atrapa)
    assert e.jest("komunikat_skan_do_powtorzenia")
    panel = e.tekst_elementu("komunikat_skan_do_powtorzenia")
    assert ST.KOMUNIKATY["skan_do_powtorzenia"].tytul in panel and ST.POWODY_POWTORZENIA[powod].format(gniazda="2") in panel
    nic_zielonego(e)
    assert e.mapa.podpisy()[2] == ST.STATUSY[wada].napis and e.mapa.podpisy()[1] == ST.STATUSY["skan_do_powtorzenia"].napis
    assert ST.STATUSY_PLYTKI["do_powtorzenia"] in e.tekst()
    e.klik_gniazdo(2)
    assert ST.STATUSY[wada].opis in e.tekst_elementu("widok_pracy")
    for nazwa in ("przycisk_ukruszona", "przycisk_ok", "przycisk_cofnij"):
        assert not e.aktywny(nazwa)
    assert ST.STATUSY_PLYTKI["do_powtorzenia"] in e.w("praca_wyjasnienie").text()


def test_4_dwie_prace_w_gniezdzie_i_praca_poza_gniazdem(atrapa, ekrany):
    from stanowisko import statusy as ST

    atrapa.wybierz_operatora("Technik A")
    atrapa.symuluj_skan("do_powtorzenia", gniazda={1: "zielony", 3: "podwojny"}, poza_gniazdem=1)
    e = ekrany(atrapa)
    panel = e.tekst_elementu("komunikat_skan_do_powtorzenia")
    assert ST.POWODY_POWTORZENIA["podwojny"].format(gniazda="3") in panel and ST.POWODY_POWTORZENIA["poza_gniazdem"].format(ile=1) in panel
    assert e.mapa.podpisy()[3] == ST.STATUSY["podwojny"].napis and e.kolory_pikseli()[3] == ST.STATUSY["podwojny"].hex
    assert e.jest("poza_gniazdem") and ST.STATUSY["poza_gniazdem"].napis in e.tekst_elementu("poza_gniazdem")
    e.klik_gniazdo(3)
    assert ST.STATUSY["podwojny"].opis in e.tekst_elementu("widok_pracy")
    nic_zielonego(e)


def test_4_pusta_pula_blad_analizy_i_inne_komunikaty(atrapa, ekrany):
    from stanowisko import statusy as ST

    k = Szpieg(atrapa)
    k.wybierz_operatora("Technik A")
    e = ekrany(k)
    pusta = atrapa.symuluj_komunikat("pula_pusta", czeka=2)
    assert e.jest("komunikat_pula_pusta")
    panel = e.tekst_elementu("komunikat_pula_pusta")
    assert pusta.tytul in panel and pusta.tekst in panel and ST.PRZYCISKI["odswiez_pule"] in panel
    k.polecenia.clear()
    e.klik("komunikat_odswiez_pule")
    assert k.polecenia == [("odswiez_pule", ())]
    e.klik("zamknij_komunikat")
    assert k.polecenia[-1] == ("zamknij_komunikat", (pusta.id,)) and not e.jest("komunikat_pula_pusta")
    skan_id = atrapa.symuluj_skan("blad")
    assert e.okno.pokazana_plytka() == skan_id and e.jest("komunikat_blad_analizy")
    blad = next(x for x in atrapa.stan().komunikaty if x.rodzaj == "blad_analizy")
    assert blad.tytul in e.tekst_elementu("komunikat_blad_analizy") and blad.tekst in e.tekst_elementu("komunikat_blad_analizy")
    nic_zielonego(e)
    for rodzaj in ("plik_zajety", "plik_niedostepny", "silnik_nie_startuje", "folder_skanera_niedostepny", "pula_brak_folderu"):
        kom = atrapa.symuluj_komunikat(rodzaj)
        assert kom.tytul in e.tekst(tylko_widoczne=False) and kom.tekst in e.tekst(tylko_widoczne=False), rodzaj
    assert e.jest("komunikat_pula_brak_folderu")  # najnowszy komunikat jest widoczny


def test_4_odmowa_polecenia_to_komunikat_nie_wyjatek(atrapa, ekrany, zegar):
    """Zmiana osoby wygasa z koncem zmiany: decyzja kliknieta tuz po 22:00 jest odmowa z komunikatem na ekranie, bez wyjatku."""
    from stanowisko import statusy as ST

    atrapa.wybierz_operatora("Technik A")
    skan_id = atrapa.symuluj_skan("zwykla")
    e = ekrany(atrapa)
    e.klik_gniazdo(2)
    assert e.aktywny("przycisk_ukruszona")
    with e.bez_zegara():  # ekran jeszcze nie dostal nowego stanu - bez wyscigu z tyknieciem zegara lacznika (A-P4)
        zegar.przesun(4 * 60)  # 23:00 - zmiana 3
        e.klik("przycisk_ukruszona")
    assert atrapa.stan().plytka(skan_id).gniazdo(2).praca.decyzja is None and atrapa.stan().operator is None
    assert e.jest("panel_osoba") and not e.aktywny("przycisk_ukruszona")
    tekst = e.tekst()
    assert ST.tekst_komunikatu("nowa_zmiana", zmiana=3)[2] in tekst or ST.tekst_komunikatu("brak_operatora")[2] in tekst


def test_4_postep_analizy_i_kolejka_na_pasku(atrapa, ekrany):
    from stanowisko.ui import napisy as N

    e = ekrany(atrapa)
    assert N.ANALIZA_BRAK in e.w("napis_analiza").text() and not e.jest("pasek_postepu")
    atrapa.symuluj_postep(udzial=0.55, czeka=2)
    assert e.jest("pasek_postepu") and e.w("pasek_postepu").value() == 55
    assert N.KOLEJKA.format(n=2) in e.tekst()
    atrapa.symuluj_postep(udzial=None)
    assert not e.jest("pasek_postepu") and N.ANALIZA_BRAK in e.w("napis_analiza").text()


def test_4_pasek_tryb_doba_zmiana(atrapa, ekrany):
    from stanowisko import statusy as ST

    e = ekrany(atrapa)
    assert ST.NAZWY_TRYBOW["wieczor"] in e.w("napis_tryb").text()
    assert "17.11.2026" in e.w("napis_doba").text() and "2" in e.w("napis_doba").text()


def test_4_pula_liczenie_i_skany_wstrzymane_czekaja(atrapa, ekrany):
    """Odswiezanie puli trwa: przycisk "Odswiez pule" nieaktywny, obok pasek. Skany wstrzymane sa pokazane jako czekajace
    z powodem (na projekty w puli) - nie jako blad. Kazdy stan puli z kontraktu ma napis ze stanu."""
    import dataclasses

    from stanowisko import kontroler_api as K
    from stanowisko import statusy as ST
    from stanowisko.ui import napisy as N

    k = Szpieg(atrapa)
    e = ekrany(k)
    assert e.aktywny("przycisk_odswiez_pule") and not e.jest("pasek_puli")
    for stan_puli in K.STANY_PULI:
        atrapa.symuluj_pule(stan_puli)
        assert e.w("napis_pula").text() == atrapa.stan().pula.napis == ST.STANY_PULI[stan_puli].format(n=16)
        assert e.aktywny("przycisk_odswiez_pule") == (stan_puli != "liczenie") and e.jest("pasek_puli") == (stan_puli == "liczenie")
    atrapa.symuluj_pule("pusta")
    atrapa.symuluj_kolejke(czeka=0, wstrzymane=2)
    assert N.WSTRZYMANE_PULA.format(n=2) in e.w("napis_kolejka").text() and N.ANALIZA_CZEKA in e.w("napis_analiza").text()
    assert e.jest("komunikat_pula_pusta") and e.aktywny("komunikat_odswiez_pule")  # powod i wyjscie: komunikat ze stanu
    atrapa._pula_prawda = ("gotowa", 5)  # technik skopiowal projekty
    with e.bez_zegara():  # A-P4: stan "liczenie trwa" sprawdzany bez wyscigu z tyknieciem zegara lacznika (30 ms)
        e.klik("komunikat_odswiez_pule")
        assert k.polecenia[-1] == ("odswiez_pule", ()) and not e.aktywny("przycisk_odswiez_pule") and e.jest("pasek_puli")  # liczenie trwa
        atrapa.przetworz()  # wynik liczenia (w prawdziwym kontrolerze - watek liczenia + nastepne tykniecie)
    e.czekaj(lambda: e.w("napis_pula").text() == ST.STANY_PULI["gotowa"].format(n=5), co="pula policzona")
    assert not e.jest("komunikat_pula_pusta") and N.KOLEJKA.format(n=2) in e.w("napis_kolejka").text()  # skany poszly do analizy
    atrapa.symuluj_kolejke(wstrzymane=1, silnik_gotowy=False)  # pula gotowa, analiza nie rusza
    assert N.WSTRZYMANE_ANALIZA.format(n=1) in e.w("napis_kolejka").text() and e.jest("komunikat_silnik_nie_startuje")
    podmien_zywe(atrapa, pula=dataclasses.replace(atrapa.stan().pula, stan="stan_z_przyszlosci", napis="napis ze stanu"))
    assert e.w("napis_pula").text() == "napis ze stanu"  # stan puli nieznany tej wersji ekranu: napis ze stanu, bez bledu


def test_4_skaner_niedostepny_i_nieudany_start_skanu(atrapa, ekrany):
    """Folder skanera niedostepny: napis na pasku i komunikat ze stanu. Nieudany start skanu (Spacja): komunikat, nie cisza."""
    from PySide6.QtCore import Qt

    from stanowisko import statusy as ST
    from stanowisko.ui import napisy as N

    k = Szpieg(atrapa)
    e = ekrany(k)
    assert e.w("napis_skaner").text() == N.SKANER_GOTOWY
    atrapa.symuluj_skaner(dostepny=False)
    assert e.w("napis_skaner").text() == N.SKANER_BRAK_FOLDERU
    assert e.jest("komunikat_folder_skanera_niedostepny") and ST.KOMUNIKATY["folder_skanera_niedostepny"].tekst in e.tekst()
    atrapa.symuluj_skaner(dostepny=True, zajete=1)
    assert e.w("napis_skaner").text() == N.SKANER_ZAJETY and e.jest("komunikat_plik_zajety")
    assert not e.jest("komunikat_folder_skanera_niedostepny")
    atrapa.symuluj_skaner(start_udany=False)
    e.klawisz(Qt.Key.Key_Space)
    assert k.polecenia == [("start_skanu", ())] and len(atrapa.starty_skanu) == 1
    assert e.jest("komunikat_start_skanu_nieudany") and ST.KOMUNIKATY["start_skanu_nieudany"].tekst in e.tekst()
    assert not e.jest("komunikat_odpowiedz") and N.SKANER_CZEKA not in e.tekst()  # jeden komunikat (ze stanu), ekran nie czeka na skan
    atrapa.symuluj_skaner(start_udany=True)
    e.klawisz(Qt.Key.Key_Space)
    assert not e.jest("komunikat_start_skanu_nieudany") and e.w("napis_skaner").text() == N.SKANER_CZEKA


def test_4_odmowa_spoza_stanu_tekst_odpowiedzi_na_ekranie(atrapa, ekrany):
    """Odmowa, ktorej kontroler nie dal w komunikatach stanu: ekran pokazuje tekst ``Odpowiedz`` w panelu i pozwala go zamknac."""
    from PySide6.QtCore import Qt

    from stanowisko import kontroler_api as K
    from stanowisko import statusy as ST

    odmowa = K.Odpowiedz(False, ST.tekst_komunikatu("start_skanu_nieudany")[2], "start_skanu_nieudany")
    k = Podstawiony(atrapa, {"start_skanu": odmowa})
    e = ekrany(k)
    e.klawisz(Qt.Key.Key_Space)
    assert k.polecenia == [("start_skanu", ())]
    assert e.jest("komunikat_odpowiedz") and odmowa.tekst in e.tekst_elementu("komunikat_odpowiedz")
    e.klik("zamknij_odpowiedz")
    assert not e.jest("komunikat_odpowiedz")


def test_4_blad_zapisu_komunikat_trwaly_pozycje_nie_zapisano_i_ponow_zapis(atrapa, ekrany):
    """Wynikow nie da sie zapisac: komunikat TRWALY na ekranie (przed innymi), pozycje "nie zapisano" przy plytkach, "Ponow zapis".
    Przyczyna ustepuje - komunikat i pozycje znikaja, plytki pojawiaja sie na liscie."""
    from stanowisko import kontroler_api as K
    from stanowisko import statusy as ST
    from stanowisko.ui import napisy as N

    k = Szpieg(atrapa)
    k.wybierz_operatora("Technik A")
    atrapa.symuluj_skan("zwykla")
    e = ekrany(k)
    atrapa.symuluj_blad_zapisu(2)
    stan = atrapa.stan()
    assert len(stan.niezapisane) == 2 and any(x.id == K.ID_BLAD_ZAPISU and x.trwaly for x in stan.komunikaty)
    assert e.jest("komunikat_blad_zapisu") and ST.KOMUNIKATY["blad_zapisu"].tytul in e.tekst_elementu("komunikat_blad_zapisu")
    assert e.jest("niezapisany_0") and e.jest("niezapisany_1") and ST.NAPISY_NIEZAPISANE["blad_zapisu"] in e.tekst_elementu("niezapisany_0")
    assert N.WSTRZYMANE_ZAPIS.format(n=2) in e.w("napis_kolejka").text()
    for i in range(6):  # inne komunikaty nie spychaja bledu zapisu z ekranu
        atrapa.symuluj_komunikat("plik_zmieniony")
        atrapa.symuluj_komunikat("skan_juz_jest")
    assert e.jest("komunikat_blad_zapisu")
    assert e.w("przycisk_ponow_zapis").text() == ST.PRZYCISKI["ponow_zapis"] == e.w("komunikat_ponow_zapis").text()
    k.polecenia.clear()
    e.klik("przycisk_ponow_zapis")  # przyczyna trwa: odmowa, pozycje zostaja
    assert k.polecenia == [("ponow_zapis", ())] and len(atrapa.stan().niezapisane) == 2 and e.jest("niezapisany_1")
    assert e.jest("komunikat_blad_zapisu") and not e.jest("komunikat_odpowiedz")  # tekst odmowy = komunikat ze stanu, jeden panel
    with e.bez_zegara():  # bez wyscigu z tyknieciem lacznika: zapis ma przyjsc z klikniecia, nie z ``przetworz`` (A-P4)
        atrapa.symuluj_blad_zapisu(0)  # dysk wrocil
        e.klik("komunikat_ponow_zapis")
    assert atrapa.stan().niezapisane == () and not e.jest("niezapisany_0") and not e.jest("komunikat_blad_zapisu")
    assert len(e.plytki()) == 3 and not e.jest("przycisk_ponow_zapis")
    atrapa.symuluj_blad_zapisu(1, "baza_zajeta")
    assert ST.NAPISY_NIEZAPISANE["baza_zajeta"] in e.tekst_elementu("niezapisany_0") and e.jest("komunikat_baza_zajeta")
    bez_sciezek(e)


def test_4_blad_zapisu_prawdziwy_kontroler_ponow_zapis(stanowiska, ekrany, monkeypatch):
    """Prawdziwy kontroler (P1, polecenie ``ponow_zapis``): wyniku nie da sie zapisac (pelny dysk) - na ekranie komunikat trwaly
    ``blad_zapisu``, pozycja "nie zapisano" z napisem ze stanu i "Ponow zapis"; klikniecie przy trwajacej przyczynie = jedna
    proba, pozycja zostaje, jeden panel (tekst odmowy = komunikat ze stanu); po zwolnieniu dysku klikniecie zapisuje skan -
    plytka na liscie i mapie, komunikat i pozycja znikaja."""
    import sqlite3

    from stanowisko import aplikacja as AP
    from stanowisko import statusy as ST
    from stanowisko.ui import napisy as N

    st = stanowiska()
    monkeypatch.setattr(AP, "OKRES_KONTROLI_S", 600.0)  # samoczynne ponowienie daleko: zapis tylko z przycisku na ekranie
    dysk = {"blad": sqlite3.OperationalError("database or disk is full"), "proby": 0}
    prawdziwa = st.k.sesja.przyjmij_wynik

    def zapis(*a, **kw):
        if dysk["blad"] is not None:
            dysk["proby"] += 1
            raise dysk["blad"]
        return prawdziwa(*a, **kw)

    monkeypatch.setattr(st.k.sesja, "przyjmij_wynik", zapis)
    k = Szpieg(st.k)
    e = ekrany(k)
    e.klik("osoba_0")
    st.zapisz(st.opis("zwykla", 1, None, None, None, 0))
    e.czekaj(lambda: e.jest("niezapisany_0"), 90.0, "pozycja nie zapisano")
    stan = st.stan()
    assert stan.plytki == () and len(stan.niezapisane) == 1 and stan.kolejka.niezapisane == 1
    assert e.jest("komunikat_blad_zapisu") and ST.NAPISY_NIEZAPISANE["blad_zapisu"] in e.tekst_elementu("niezapisany_0")
    assert stan.niezapisane[0].napis in e.tekst_elementu("niezapisany_0") and N.WSTRZYMANE_ZAPIS.format(n=1) in e.w("napis_kolejka").text()
    assert e.w("przycisk_ponow_zapis").text() == ST.PRZYCISKI["ponow_zapis"] == e.w("komunikat_ponow_zapis").text()
    proby = dysk["proby"]
    k.polecenia.clear()
    e.klik("przycisk_ponow_zapis")  # przyczyna trwa: odmowa, pozycja zostaje
    assert k.polecenia == [("ponow_zapis", ())] and dysk["proby"] == proby + 1
    assert e.jest("niezapisany_0") and e.jest("komunikat_blad_zapisu") and not e.jest("komunikat_odpowiedz") and e.plytki() == []
    dysk["blad"] = None  # dysk zwolniony
    e.klik("komunikat_ponow_zapis")
    assert k.polecenia[-1] == ("ponow_zapis", ()) and st.stan().niezapisane == () and len(st.stan().plytki) == 1
    e.czekaj(lambda: len(e.plytki()) == 1, 10.0, "plytka po zapisie")
    assert not e.jest("niezapisany_0") and not e.jest("komunikat_blad_zapisu") and not e.jest("przycisk_ponow_zapis")
    assert mapa_rowna_stanowi(e, st.stan().plytki[0]) > 0 and not e.jest("napis_kolejka")
    bez_sciezek(e)


def test_4_praca_bez_inspekcji_albo_o_nieznanym_statusie_nie_jest_zielona(atrapa, ekrany):
    """P4 rdzenia: zielone na ekranie jest tylko to, co stan nazywa zielonym; praca bez inspekcji, z inspekcja pominieta albo
    o statusie nieznanym tej wersji programu jest zolta z napisem ze stanu."""
    from stanowisko import statusy as ST

    atrapa.wybierz_operatora("Technik A")
    rodzaje = {2: "zielony_bez_inspekcji", 3: "zielony_pominieto", 4: "zielony_nowa_inspekcja", 5: "zielony_nowe_dopasowanie", 6: "zielony"}
    skan_id = atrapa.symuluj_skan("zwykla", gniazda=rodzaje)
    e = ekrany(atrapa)
    plytka = atrapa.stan().plytka(skan_id)
    assert mapa_rowna_stanowi(e, plytka) == 19
    zielone = {ST.STATUSY[x].hex for x in ST.STATUSY_ZIELONE}
    piksele = e.kolory_pikseli()
    assert piksele[6] in zielone and all(piksele[nr] not in zielone for nr in (2, 3, 4, 5))
    assert [plytka.gniazdo(nr).status for nr in (2, 3, 4, 5)] == ["nie_sprawdzono", "nie_sprawdzono", "nieznany", "nieznany"]
    for nr in (2, 3, 4, 5):  # klasa koloru ze stanu = ``statusy.kolor_pracy`` dla zielonego z sesji; ekran rysuje ``rgb`` tej klasy
        g = plytka.gniazdo(nr)
        assert g.kolor == ST.kolor_pracy(ST.KOLOR_ZIELONY, g.status) == ST.KOLOR_ZOLTY and piksele[nr] == g.rgb, (nr, g.kolor, g.status)
    assert e.w(f"plytka_{skan_id}").liczniki() == {"zielony": 1, "zolty": 4}
    e.klik_gniazdo(4)
    assert ST.STATUSY["nieznany"].opis in e.tekst_elementu("widok_pracy") and e.aktywny("przycisk_ukruszona") and e.aktywny("przycisk_ok")


def test_4_wylogowanie_osoby(atrapa, ekrany):
    """"Odchodze od stanowiska" (``wybierz_operatora(None)``): nikt nie jest wybrany, decyzje nieaktywne, ekran pyta o osobe."""
    from stanowisko import statusy as ST

    k = Szpieg(atrapa)
    k.wybierz_operatora("Technik A")
    atrapa.symuluj_skan("zwykla")
    e = ekrany(k)
    e.klik_gniazdo(2)
    assert e.aktywny("przycisk_ukruszona")
    e.klik("przycisk_zmien_osobe")
    assert e.w("osoba_wyloguj").text() == ST.PRZYCISK_WYLOGUJ
    k.polecenia.clear()
    e.klik("osoba_wyloguj")
    assert k.polecenia == [("wybierz_operatora", (None,))] and atrapa.stan().operator is None
    assert not e.jest("komunikat_odpowiedz")  # ``Odpowiedz(ok=True, kod="wylogowano")`` to nie odmowa: bez panelu odmowy
    assert e.jest("panel_osoba") and not e.jest("osoba_wyloguj") and not e.aktywny("przycisk_ukruszona")
    assert e.w("praca_wyjasnienie").text() == ST.tekst_komunikatu("brak_operatora")[2]
    e.klik("osoba_1")
    assert atrapa.stan().operator == "Technik B" and e.aktywny("przycisk_ukruszona")


@pytest.mark.parametrize("kod", ["zle_argumenty", "blad_polecenia"])
def test_4_zle_argumenty_tekst_odpowiedzi_na_ekranie(atrapa, ekrany, kod):
    """Kazde polecenie moze zwrocic ``Odpowiedz(ok=False, kod="zle_argumenty")`` albo ``kod="blad_polecenia"`` (D1): ekran
    pokazuje tekst odpowiedzi, nic nie rzuca. Odmowa z komunikatem w stanie (prawdziwa ``zle_argumenty`` atrapy) = jeden panel
    komunikatu ze stanu, bez drugiego panelu z tym samym tekstem."""
    from stanowisko import kontroler_api as K
    from stanowisko import statusy as ST

    atrapa.wybierz_operatora("Technik A")
    skan_id = atrapa.symuluj_skan("zwykla")
    k = Podstawiony(atrapa, {"ukruszona": K.Odpowiedz(False, "Tego polecenia nie da sie wykonac - tekst z kontrolera.", kod)})
    e = ekrany(k)
    e.klik_gniazdo(2)
    e.klik("przycisk_ukruszona")
    assert k.polecenia == [("ukruszona", (atrapa.stan().plytka(skan_id).gniazdo(2).praca.praca_id,))]
    assert e.jest("komunikat_odpowiedz") and "tekst z kontrolera" in e.tekst_elementu("komunikat_odpowiedz")
    assert e.jest("widok_pracy") and e.lista() == []
    e.klik("przycisk_ok")  # nastepne polecenie przyjete: odmowa znika
    assert not e.jest("komunikat_odpowiedz")
    odp = atrapa.wykonaj("ok", "nie liczba")  # prawdziwa odmowa kontraktu: komunikat ``zle_argumenty`` w stanie
    assert not odp and odp.kod == "zle_argumenty"
    e.odczekaj()
    assert e.jest("komunikat_zle_argumenty") and odp.tekst in e.tekst_elementu("komunikat_zle_argumenty")
    assert ST.KOMUNIKATY["zle_argumenty"].tytul in e.tekst_elementu("komunikat_zle_argumenty") and not e.jest("komunikat_odpowiedz")


def test_4_komunikat_i_status_nieznane_tej_wersji_ekranu(atrapa, ekrany):
    """Ekran nie zaklada zamknietej listy: komunikat nieznanego rodzaju (np. trwaly blad zapisu) jest panelem z tytulem i tekstem
    ze stanu; gniazdo o nieznanym statusie i klasie koloru ma kolor ``rgb`` i podpis ze stanu (nigdy zielony z domyslu)."""
    import dataclasses

    from stanowisko import statusy as ST

    atrapa.wybierz_operatora("Technik A")
    skan_id = atrapa.symuluj_skan("zwykla")
    e = ekrany(atrapa)
    kom = atrapa.symuluj_komunikat("blad_zapisu:nowy rodzaj", powod="Nie zapisano - blad zapisu (tekst ze stanu).")
    assert e.jest("komunikat_blad_zapisu_nowy_rodzaj") and kom.tytul in e.tekst() and kom.tekst in e.tekst()
    stan = atrapa.stan()
    plytka = stan.plytka(skan_id)
    nieznany = ST.status("status_z_przyszlosci")  # bezpieczny wyglad nieznanego klucza wg ``statusy``: zolty
    assert nieznany.hex not in {ST.STATUSY[x].hex for x in ST.STATUSY_ZIELONE}
    praca = dataclasses.replace(plytka.gniazdo(1).praca, status="status_z_przyszlosci", kolor="klasa_z_przyszlosci", rgb=nieznany.hex,
                                podpis="do sprawdzenia", opis="Opis ze stanu.")
    gniazda = tuple(dataclasses.replace(g, status=praca.status, kolor=praca.kolor, rgb=praca.rgb, podpis=praca.podpis, prace=(praca,))
                    if g.nr == 1 else g for g in plytka.gniazda)
    nowa = dataclasses.replace(plytka, gniazda=gniazda, napis="nie zapisano - blad zapisu", liczniki={**plytka.liczniki, "klasa_z_przyszlosci": 1})
    e.okno.pokaz_stan(dataclasses.replace(stan, wersja=stan.wersja + 1, plytki=(nowa,)))
    assert e.mapa.kolory()[1] == nieznany.hex == e.kolory_pikseli()[1] and e.mapa.podpisy()[1] == "do sprawdzenia"
    assert "nie zapisano - blad zapisu" in e.w("mapa_naglowek").text() and "nie zapisano - blad zapisu" in e.tekst_elementu(f"plytka_{skan_id}")
    assert e.w(f"plytka_{skan_id}").liczniki()["klasa_z_przyszlosci"] == 1
    e.klik_gniazdo(1)
    widok = e.tekst_elementu("widok_pracy")
    assert "do sprawdzenia" in widok and "Opis ze stanu." in widok


def test_lista_zapis_do_pliku(atrapa, ekrany):
    """Polecenie ``zapisz_liste``: przycisk przy liscie wysyla je raz; ekran pokazuje godzine zapisu ze stanu, nigdy nazwe pliku.
    Lista zapisuje sie tez sama po kazdej zmianie (``stan.lista_zapisana``)."""
    from stanowisko import statusy as ST
    from stanowisko.ui import napisy as N

    k = Szpieg(atrapa)
    k.wybierz_operatora("Technik A")
    atrapa.symuluj_skan("zwykla")
    e = ekrany(k)
    assert e.w("przycisk_zapisz_liste").text() == ST.PRZYCISKI["zapisz_liste"]
    e.klik_gniazdo(2)
    e.klik("przycisk_ukruszona")
    assert atrapa.stan().lista_zapisana and e.w("lista_zapisano").text() == N.LISTA_PLIK.format(godzina="19:00")  # zapis samoczynny
    k.polecenia.clear()
    e.klik("przycisk_zapisz_liste")
    assert k.polecenia == [("zapisz_liste", ())] and not e.jest("komunikat_odpowiedz")
    assert e.jest("lista_zapisano") and bez_sciezek(e) > 20
    kom = atrapa.symuluj_komunikat("lista_nie_zapisana")  # blad dysku przy zapisie listy: komunikat z przyciskiem ponowienia
    assert e.jest("komunikat_lista_nie_zapisana") and kom.tekst in e.tekst()
    e.klik("komunikat_zapisz_liste")
    assert k.polecenia[-1] == ("zapisz_liste", ())


# ----------------------------------------------------------------------------
# (5) ponowne otwarcie okna
# ----------------------------------------------------------------------------
def test_5_ponowne_otwarcie_okna_na_tym_samym_stanie(atrapa, ekrany):
    atrapa.scenariusz_pokazowy()
    pierwsze = ekrany(atrapa)
    teksty, obraz = pierwsze.teksty(), pierwsze.obraz()
    assert obraz.width() == ROZMIAR_OKNA[0] and obraz.height() == ROZMIAR_OKNA[1]
    pierwsze.zamknij()
    drugie = ekrany(atrapa)
    assert drugie.teksty() == teksty
    assert drugie.obraz() == obraz  # ten sam obraz co do piksela
    assert drugie.mapa.kolory() and drugie.kolory_pikseli() == {nr: k for nr, k in drugie.mapa.kolory().items()}


def test_5_restart_programu_odtwarza_plytki_i_decyzje_na_ekranie(stanowiska, ekrany):
    """Prawdziwy kontroler: zamkniecie programu w polowie wieczoru i ponowny start - mapa, kafelki plytek i lista jak przedtem."""
    st = stanowiska()
    e = ekrany(st.k)
    e.klik("osoba_0")
    pierwsza = st.wrzuc("zwykla", numer=1)
    druga = st.wrzuc("czysta", numer=2, projekty={1: 11, 2: 12, 3: 13, 4: 14})
    e.czekaj(lambda: e.plytki() == [pierwsza, druga], co="dwie plytki na liscie")  # plytka 1 ma prace do obejrzenia: ekran zostaje (A-P2)
    e.klik(f"plytka_{pierwsza}")
    e.klik_gniazdo(2)
    e.klik("przycisk_ukruszona")
    e.klik_gniazdo(9)
    e.klik("przycisk_ok")

    def obraz_ekranu(ekran) -> dict:
        wynik = {"plytki": ekran.plytki(), "lista": ekran.lista()}
        for skan_id in ekran.plytki():
            ekran.klik(f"plytka_{skan_id}")
            wynik[skan_id] = (ekran.mapa.kolory(), ekran.mapa.podpisy(), ekran.kolory_pikseli(), ekran.w(f"plytka_{skan_id}").liczniki(),
                              ekran.tekst_elementu(f"plytka_{skan_id}"))
        return wynik

    przed = obraz_ekranu(e)
    assert len(przed["lista"]) == 1 and przed["plytki"] == [pierwsza, druga]
    e.zamknij()
    st.koniec()
    st2 = stanowiska()  # ponowny start programu na tej samej bazie
    e2 = ekrany(st2.k)
    assert e2.jest("panel_osoba")  # po starcie programu trzeba wskazac osobe ponownie
    e2.klik("osoba_0")
    assert obraz_ekranu(e2) == przed


# ----------------------------------------------------------------------------
# (6) petla okna
# ----------------------------------------------------------------------------
def test_6_petla_okna_bez_przerw_10_plytek_po_19_prac(stanowiska, ekrany):
    """Prawdziwy kontroler, 10 plytek po 19 prac liczonych w procesie silnika; okno pokazane, technik w trakcie klika decyzje
    (gniazdo 2 -> "Ukruszona" na kazdej nowej plytce). Zegar co 10 ms mierzy najdluzsza przerwe petli okna."""
    from PySide6.QtCore import QEventLoop, Qt, QTimer
    from PySide6.QtTest import QTest

    from stanowisko import statusy as ST

    st = stanowiska()
    e = ekrany(st.k)
    e.klik("osoba_0")
    czasy_ekranu = []
    prawdziwe = e.okno.pokaz_stan

    def mierzone(stan):
        t0 = time.perf_counter()
        prawdziwe(stan)
        czasy_ekranu.append(time.perf_counter() - t0)

    e.okno.pokaz_stan = mierzone  # okno wola ``pokaz_stan`` przy kazdym sygnale stanu
    petla = QEventLoop()
    pomiar = {"ostatni": 0.0, "przerwa": 0.0, "tykniec": 0, "zdecydowane": set(), "kroki": [], "w_kroku": False}

    def tyk():
        teraz = time.perf_counter()  # przerwa = czas miedzy kolejnymi tyknieciami zegara (zawiera prace okna i klikniecia technika)
        pomiar["przerwa"] = max(pomiar["przerwa"], teraz - pomiar["ostatni"])
        pomiar["ostatni"] = teraz
        pomiar["tykniec"] += 1
        if pomiar["w_kroku"]:  # tykniecie w trakcie obslugi klikniecia (zagniezdzone zdarzenia) - tylko pomiar
            return
        plytka = e.okno.pokazana_plytka()
        if (plytka is not None and plytka not in pomiar["zdecydowane"] and e.mapa.podpisy().get(2) == ST.STATUSY["czerwony"].napis
                and not e.okno.ochrona_aktywna()):  # technik klika, gdy mapa nie jest juz przygaszona po zmianie (A-P2)
            pomiar["w_kroku"] = True
            t0 = time.perf_counter()
            QTest.mouseClick(e.mapa, Qt.MouseButton.LeftButton, pos=e.mapa.srodek_gniazda(2).toPoint())
            QTest.mouseClick(e.w("przycisk_ukruszona"), Qt.MouseButton.LeftButton)
            QTest.keyClick(e.okno, Qt.Key.Key_Escape)
            pomiar["kroki"].append(time.perf_counter() - t0)
            pomiar["zdecydowane"].add(plytka)
            pomiar["w_kroku"] = False
        elif (plytka is None or plytka in pomiar["zdecydowane"]) and e.w("przycisk_nowa_plytka").isVisibleTo(e.okno):
            pomiar["w_kroku"] = True  # nowy wynik przyszedl, zanim technik skonczyl poprzednia plytke: przelacza sam (A-P2)
            QTest.mouseClick(e.w("przycisk_nowa_plytka"), Qt.MouseButton.LeftButton)
            pomiar["w_kroku"] = False
        if len(pomiar["zdecydowane"]) == 10 and len(e.lista()) == 10:
            petla.quit()

    zegar = QTimer()
    zegar.setInterval(10)
    zegar.timeout.connect(tyk)
    QTimer.singleShot(180_000, petla.quit)
    for i in range(10):
        st.zapisz({"gniazda": {n: ("czerwony" if n == 2 else "zielony") for n in range(1, 20)}, "numer": 1 + i,
                   "projekty": {n: 100 * (i + 1) + n for n in range(1, 20)}, "spij": 0.3})
    pomiar["ostatni"] = time.perf_counter()
    zegar.start()
    t0 = time.perf_counter()
    petla.exec()
    czas = time.perf_counter() - t0
    zegar.stop()
    print(f"\n[kryterium 6] 10 plytek x 19 prac w {czas:.1f} s; najdluzsza przerwa petli okna {pomiar['przerwa'] * 1000:.0f} ms "
          f"(prog {PROG_PRZERWY_S * 1000:.0f} ms); odswiezen ekranu {len(czasy_ekranu)}, najdluzsze {max(czasy_ekranu) * 1000:.1f} ms; "
          f"najdluzszy krok technika (klik gniazda + Ukruszona + Esc) {max(pomiar['kroki'] or [0]) * 1000:.0f} ms; tykniec {pomiar['tykniec']}")
    assert len(pomiar["zdecydowane"]) == 10 and len(e.lista()) == 10 and len(e.plytki()) == 10
    assert all(len(p.prace) == 19 for p in st.stan().plytki)
    assert pomiar["tykniec"] >= 100 and len(czasy_ekranu) >= 20
    assert pomiar["przerwa"] <= PROG_PRZERWY_S
    assert max(czasy_ekranu) <= PROG_PRZERWY_S / 2


def test_6_odswiezenie_ekranu_przy_10_plytkach_i_zdarzeniach(atrapa, ekrany):
    """Atrapa: 10 plytek x 19 prac, potem 200 zdarzen postepu i 30 komunikatow - kazde odswiezenie ekranu ponizej 100 ms."""
    from PySide6.QtCore import Qt

    atrapa.wybierz_operatora("Technik A")
    e = ekrany(atrapa)
    czasy = []
    prawdziwe = e.okno.pokaz_stan

    def mierzone(stan):
        t0 = time.perf_counter()
        prawdziwe(stan)
        czasy.append(time.perf_counter() - t0)

    e.okno.pokaz_stan = mierzone  # okno wola ``pokaz_stan`` przy kazdym sygnale stanu
    for i in range(10):
        skan_id = atrapa.symuluj_skan("zwykla", numer=1 + i % 6, gniazda={n: ("czerwony" if n % 5 == 2 else "zielony") for n in range(1, 20)},
                                      projekty={n: (19 * i + n) % 30 + 1 for n in range(1, 20)})
        if e.okno.pokazana_plytka() != skan_id:  # na poprzedniej plytce zostaly prace do obejrzenia: przelacza technik (A-P2)
            e.klik(f"plytka_{skan_id}")
        e.klik_gniazdo(2)
        e.klik("przycisk_ukruszona")
        e.klawisz(Qt.Key.Key_Escape)
        assert e.okno.pokazana_plytka() == skan_id
    t0 = time.perf_counter()
    for i in range(200):
        atrapa.symuluj_postep(udzial=(i % 100) / 100, czeka=i % 4)
    postep_s = (time.perf_counter() - t0) / 200
    for i in range(30):
        atrapa.symuluj_komunikat("plik_zajety", od_s=i)
    atrapa.symuluj_postep(udzial=None)
    e.odczekaj(50)
    print(f"\n[kryterium 6, atrapa] odswiezen ekranu {len(czasy)}, najdluzsze {max(czasy) * 1000:.1f} ms; zdarzenie postepu {postep_s * 1000:.2f} ms")
    assert len(e.plytki()) == 10 and len(czasy) >= 40
    assert max(czasy) <= PROG_PRZERWY_S / 2 and postep_s <= 0.02


# ----------------------------------------------------------------------------
# (7) pula projektow
# ----------------------------------------------------------------------------
def test_7_liczba_projektow_w_puli_i_odswiez_pule(atrapa, ekrany):
    from stanowisko import statusy as ST

    k = Szpieg(atrapa)
    e = ekrany(k)
    assert e.w("napis_pula").text() == ST.STANY_PULI["gotowa"].format(n=16) == atrapa.stan().pula.napis
    assert e.w("przycisk_odswiez_pule").text() == ST.PRZYCISKI["odswiez_pule"]
    atrapa._pula_prawda = ("gotowa", 21)  # w folderze projektow przybylo plikow (wynik nastepnego liczenia)
    e.klik("przycisk_odswiez_pule")
    assert k.polecenia == [("odswiez_pule", ())]
    e.czekaj(lambda: e.w("napis_pula").text() == ST.STANY_PULI["gotowa"].format(n=21), co="pula po odswiezeniu")
    assert e.aktywny("przycisk_odswiez_pule") and not e.jest("pasek_puli")
    atrapa._pula_prawda = ("pusta", 0)
    e.klik("przycisk_odswiez_pule")
    e.czekaj(lambda: e.w("napis_pula").text() == ST.STANY_PULI["pusta"], co="pusta pula po odswiezeniu")


def test_7_pula_prawdziwy_kontroler(stanowiska, ekrany):
    from stanowisko import statusy as ST

    st = stanowiska()
    e = ekrany(st.k)
    assert e.w("napis_pula").text() == ST.STANY_PULI["gotowa"].format(n=3)
    (st.tmp / "projekty" / FOLDER_ZLECENIA / "Fikcja-99-crown_cad.stl").write_bytes(TK.plik_skanu({"projekt": 99}))
    e.klik("przycisk_odswiez_pule")
    e.czekaj(lambda: e.w("napis_pula").text() == ST.STANY_PULI["gotowa"].format(n=4), co="pula po odswiezeniu")


# ----------------------------------------------------------------------------
# (8) dane osobowe: 0 sciezek i nazw plikow na ekranie
# ----------------------------------------------------------------------------
WZORY_SCIEZEK = (
    re.compile(r"[A-Za-z]:[\\/]"),  # dysk
    re.compile(r"\\\\|\\[A-Za-z0-9_]"),  # odwrotny ukosnik (sciezka Windows, zasob sieciowy)
    re.compile(r"\.(stl|npz|json|sqlite|toml|csv|db|log|txt|py)\b", re.I),  # nazwa pliku
    re.compile(r"[A-Za-z0-9_]/[A-Za-z_]"),  # sciezka z ukosnikiem (daty z kropkami i liczby sa dozwolone)
    re.compile(r"atrapa|_podglad|_wynik|qc_|AppData|pytest|\bTemp\b", re.I),  # nazwy plikow i katalogow danych sztucznych
)


def bez_sciezek(e: Ekran, zakazane: tuple = ()) -> int:
    teksty = e.teksty(tylko_widoczne=False)
    for t in teksty:
        for wzor in WZORY_SCIEZEK:
            assert not wzor.search(t), f"sciezka albo nazwa pliku na ekranie: {t!r} ({wzor.pattern})"
        for slowo in zakazane:
            assert slowo.lower() not in t.lower(), f"{slowo!r} na ekranie: {t!r}"
    return len(teksty)


def przejdz_po_ekranie(e: Ekran, stan, zakazane: tuple = ()) -> int:
    """Kazda plytka, kazde gniazdo z praca (widok pracy z obrazem), obie listy - po kazdym kroku kontrola wszystkich napisow."""
    sprawdzone = bez_sciezek(e, zakazane)
    for plytka in stan.plytki:
        e.klik(f"plytka_{plytka.skan_id}")
        sprawdzone += bez_sciezek(e, zakazane)
        for g in plytka.gniazda:
            if g.prace:
                e.klik_gniazdo(g.nr)
                assert e.jest("widok_pracy")
                sprawdzone += bez_sciezek(e, zakazane)
    e.klik("lista_wszystkie")
    sprawdzone += bez_sciezek(e, zakazane)
    e.klik("lista_ta_doba")
    return sprawdzone


@pytest.mark.parametrize("scenariusz", ["pusty", "zwykla", "czysta", "do_powtorzenia", "niezgodny_uklad", "nie_z_trybu", "bez_numeru", "blad",
                                        "pokazowy", "komunikaty"])
def test_8_zero_sciezek_i_nazw_plikow_w_tekstach_widzetow(atrapa, ekrany, tmp_path, scenariusz):
    from stanowisko import statusy as ST

    atrapa.wybierz_operatora("Technik A")
    if scenariusz == "pokazowy":
        atrapa.scenariusz_pokazowy()
    elif scenariusz == "komunikaty":
        atrapa.symuluj_skan("zwykla")
        atrapa.symuluj_postep(udzial=0.4, czeka=3)
        for rodzaj in ST.KOMUNIKATY:
            atrapa.symuluj_komunikat(rodzaj)
    elif scenariusz != "pusty":
        atrapa.symuluj_skan(scenariusz, poza_gniazdem=1 if scenariusz == "do_powtorzenia" else 0)
    e = ekrany(atrapa)
    if scenariusz in ("zwykla", "czysta", "komunikaty"):
        e.klik_gniazdo(2)
        e.klik("przycisk_ukruszona")  # pozycja na liscie "do dofrezowania"
        e.czekaj(lambda: e.w("praca_obraz").pixmap() is not None and not e.w("praca_obraz").pixmap().isNull(), co="obraz odchylek")
    if scenariusz in ("zwykla", "czysta", "komunikaty", "pokazowy"):
        assert len(e.lista()) == 1
    zakazane = (str(tmp_path), tmp_path.name, "(atrapa)", "Atrapa ")
    ile = przejdz_po_ekranie(e, atrapa.stan(), zakazane)
    for _ in range(60):  # komunikaty po kolei (ekran pokazuje kilka naraz): zamkniecie odslania nastepne
        if not e.jest("zamknij_komunikat"):
            break
        e.klik("zamknij_komunikat")
        ile += bez_sciezek(e, zakazane)
    assert not e.jest("zamknij_komunikat")
    assert ile > 20
    stan = atrapa.stan()
    assert stan.pula.folder == "(atrapa)" and stan.pula.folder not in e.tekst(tylko_widoczne=False)  # folder puli nie jest pokazywany


def test_8_fikcyjna_nazwa_zlecenia_prawdziwy_kontroler(stanowiska, ekrany, tmp_path):
    """Prawdziwy kontroler: pula w folderze o fikcyjnej nazwie zlecenia, skan w podfolderze o tej nazwie - 0 wystapien na ekranie."""
    st = stanowiska()
    e = ekrany(st.k)
    e.klik("osoba_0")
    przed = {p.skan_id for p in st.stan().plytki}
    st.zapisz(st.opis("zwykla", 1, None, None, None, 0), podfolder=FOLDER_ZLECENIA)
    st.czekaj(lambda: {p.skan_id for p in st.stan().plytki} - przed, 90.0, "skan w stanie")
    e.klik_gniazdo(2)
    e.klik("przycisk_ukruszona")
    zakazane = (FOLDER_ZLECENIA, "Zmyslona", "Fikcja", str(tmp_path), tmp_path.name, "eksport", "skan_0")
    assert przejdz_po_ekranie(e, st.stan(), zakazane) > 20


# ----------------------------------------------------------------------------
# (9) piec zadan wieczornych T14 - tylko ekran
# ----------------------------------------------------------------------------
def test_9_piec_zadan_wieczornych_T14(stanowiska, ekrany):
    """T14 (plan, sekcja 7), wieczor: (1) zeskanuj plytke, (2) wskaz prace do obejrzenia, (3) oznacz jedna jako ukruszona
    i jedna jako OK, (4) poradz sobie z "popraw ulozenie", (5) pokaz liste do dofrezowania. Test steruje oknem (klikniecia,
    klawisze) i czyta wylacznie ekran; symulator skanera podaje skany (plik zapisany do folderu skanera)."""
    from PySide6.QtCore import Qt

    from stanowisko import statusy as ST
    from stanowisko.ui import napisy as N

    st = stanowiska()
    e = ekrany(st.k)
    # start zmiany: ekran pyta o osobe
    assert e.jest("panel_osoba")
    e.klik("osoba_0")
    assert "Technik A" in e.w("napis_osoba").text()

    # (1) zeskanuj plytke: Spacja, symulator podaje skan, po analizie mapa
    e.klawisz(Qt.Key.Key_Space)
    assert N.SKANER_CZEKA in e.tekst() and st.starty_skanu() == 1
    st.zapisz(st.opis("zwykla", 1, None, None, None, 0))
    e.czekaj(lambda: len(e.plytki()) == 1 and e.mapa.numery(), 90.0, "mapa pierwszej plytki")
    assert ST.STATUSY_PLYTKI["przyjety"] in e.tekst() and N.SKANER_CZEKA not in e.tekst()

    # (2) wskaz prace do obejrzenia: czerwone ("UBYTEK") i zolte / szare / pomaranczowe - z podpisow na mapie
    podpisy = e.mapa.podpisy()
    czerwone = sorted(nr for nr, p in podpisy.items() if p == ST.STATUSY["czerwony"].napis)
    do_obejrzenia = sorted(nr for nr, p in podpisy.items() if p and p != ST.STATUSY["zielony"].napis)
    assert czerwone == [2, 9] and do_obejrzenia == [2, 3, 4, 5, 6, 7, 9]
    assert all(e.kolory_pikseli()[nr] == ST.STATUSY["czerwony"].hex for nr in czerwone)
    e.klik_gniazdo(czerwone[0])
    assert e.jest("widok_pracy") and "0,62" in e.tekst_elementu("widok_pracy")

    # (3) jedna "Ukruszona" (przycisk), jedna "OK" (klawisz)
    e.klik("przycisk_ukruszona")
    assert e.mapa.podpisy()[2] == ST.STATUSY["ukruszona"].napis
    e.klik_gniazdo(czerwone[1])
    e.klawisz(Qt.Key.Key_O)
    assert e.mapa.podpisy()[9] == ST.STATUSY["zatwierdzona_ok"].napis and e.kolory_pikseli()[9] == ST.STATUSY["zatwierdzona_ok"].hex
    e.klawisz(Qt.Key.Key_Escape)

    # (4) "popraw ulozenie": druga plytka ze zle ulozona praca -> komunikat; poprawka, Spacja, ponowny skan -> pytanie -> "Tak"
    e.klawisz(Qt.Key.Key_Space)
    st.zapisz(st.opis("do_powtorzenia", 2, {1: "zielony", 3: "popraw_ulozenie", 5: "zielony"}, {1: 11, 3: 13, 5: 15}, None, 0))
    e.czekaj(lambda: len(e.plytki()) == 2, 90.0, "druga plytka na liscie")
    # na plytce 1 zostaly prace do obejrzenia (zolte, szare): ekran nie zabiera mapy - sygnal "Nowy wynik" na pasku (A-P2)
    assert e.jest("przycisk_nowa_plytka") and len(e.mapa.numery()) == 19
    e.klik("przycisk_nowa_plytka")
    assert e.jest("komunikat_skan_do_powtorzenia")
    komunikat = e.tekst_elementu("komunikat_skan_do_powtorzenia")
    assert ST.POWODY_POWTORZENIA["popraw_ulozenie"].format(gniazda="3") in komunikat
    assert e.mapa.podpisy()[3] == ST.STATUSY["popraw_ulozenie"].napis
    nic_zielonego(e)
    e.klawisz(Qt.Key.Key_Space)  # technik poprawil ulozenie i skanuje jeszcze raz
    assert st.starty_skanu() == 3
    st.zapisz(st.opis("czysta", 2, {1: "zielony", 3: "zielony", 5: "zielony"}, {1: 11, 3: 13, 5: 15}, None, 0))
    e.czekaj(lambda: len(e.plytki()) == 3 and e.jest("pytanie_ponowny_skan"), 90.0, "pytanie o ponowny skan")
    assert ST.SKUTEK_BEZ_DECYZJI in e.tekst_elementu("pytanie_ponowny_skan")
    e.klik("odp_potwierdz_ponowny_skan")
    assert not e.jest("pytanie_ponowny_skan") and not e.jest("komunikat_skan_do_powtorzenia")
    assert [e.mapa.podpisy()[nr] for nr in (1, 3, 5)] == [ST.STATUSY["zielony"].napis] * 3
    assert all(e.kolory_pikseli()[nr] == ST.STATUSY["zielony"].hex for nr in (1, 3, 5))

    # (5) lista "do dofrezowania": jedna pozycja - kuweta, zab, krazek, doba i zmiana
    assert e.jest("tabela_dofrezowania") and N.LISTA_TYTUL.format(n=1) in e.tekst()
    wiersze = e.lista()
    assert len(wiersze) == 1 and wiersze[0][:3] == ["9002", "12", "K-1"]
    assert any("17.11" in x for x in wiersze[0])
    e.klik("lista_wszystkie")
    assert len(e.lista()) == 1
    # kontrola koncowa poza ekranem: baza ma dokladnie te decyzje
    decyzje = {(p.gniazdo, p.decyzja) for pl in st.stan().plytki if pl.aktywna for p in pl.prace if p.decyzja}
    assert decyzje == {(2, "ukruszona"), (9, "ok")} and len(st.stan().do_dofrezowania) == 1


# ----------------------------------------------------------------------------
# kontrakt pakietu
# ----------------------------------------------------------------------------
def test_pakiet_ui_bez_qt_na_poziomie_modulu_i_okno_z_aplikacji(atrapa):
    """``import stanowisko.ui`` nie laduje PySide6 (proces roboczy silnika importuje pakiet ``stanowisko``); wejscie
    ``aplikacja.utworz_okno`` zwraca okno wieczorne, nie okno zastepcze."""
    import subprocess
    import sys

    kod = "import sys; import stanowisko.ui; print(any(m.startswith('PySide6') for m in sys.modules))"
    wynik = subprocess.run([sys.executable, "-c", kod], capture_output=True, text=True, cwd=str(TK.STANOWISKO), timeout=120)
    assert wynik.stdout.strip() == "False", wynik.stdout + wynik.stderr
    from stanowisko import aplikacja as AP
    from stanowisko import kontroler_api as K
    from stanowisko import ui

    lacznik = K.lacznik_qt(atrapa)
    okno = AP.utworz_okno(atrapa, lacznik)
    try:
        assert type(okno).__module__.startswith("stanowisko.ui") and okno.objectName() == "okno_wieczor"
        assert not okno.isVisible() and callable(ui.utworz_okno)
    finally:
        okno.close()
        lacznik.zatrzymaj()


def test_program_startuje_z_oknem_wieczornym_i_zamyka_sie_czysto():
    """Plik startowy z danymi sztucznymi (``--atrapa``): okno wieczorne powstaje, program konczy sie kodem 0 i bez sladu wyjatku."""
    import subprocess
    import sys

    wynik = subprocess.run([sys.executable, "-m", "stanowisko.aplikacja", "--atrapa", "--zamknij-po", "1.5"], capture_output=True, text=True,
                           cwd=str(TK.STANOWISKO), timeout=180, env={**os.environ, "QT_QPA_PLATFORM": "offscreen"})
    assert wynik.returncode == 0, wynik.stdout + wynik.stderr
    assert "Traceback" not in wynik.stderr and "Error" not in wynik.stderr, wynik.stderr


def test_stan_o_nizszej_wersji_jest_pomijany(atrapa, ekrany):
    """Stan starszy niz pokazany (zagniezdzona petla okna) nie cofa ekranu."""
    atrapa.wybierz_operatora("Technik A")
    stary = atrapa.stan()
    e = ekrany(atrapa)
    skan_id = atrapa.symuluj_skan("zwykla")
    assert e.plytki() == [skan_id]
    e.okno.pokaz_stan(stary)
    assert e.plytki() == [skan_id] and e.okno.pokazana_plytka() == skan_id


def test_nowa_plytka_nie_zabiera_otwartej_pracy(atrapa, ekrany):
    """Gdy technik oglada prace, wynik nastepnej plytki nie przelacza ekranu - nowa plytka jest oznaczona na liscie i na pasku.
    Bez otwartej pracy ekran idzie za nowa plytka tylko wtedy, gdy na pokazanej nie zostalo nic do obejrzenia (A-P2)."""
    from PySide6.QtCore import Qt

    from stanowisko.ui import napisy as N

    atrapa.wybierz_operatora("Technik A")
    pierwsza = atrapa.symuluj_skan("zwykla", numer=1)
    e = ekrany(atrapa)
    e.klik_gniazdo(2)
    druga = atrapa.symuluj_skan("czysta", numer=2, projekty={1: 11, 2: 12, 3: 13, 4: 14})
    assert e.okno.pokazana_plytka() == pierwsza and e.jest("widok_pracy")
    assert N.PLYTKA_NOWA in e.tekst_elementu(f"plytka_{druga}") and e.jest("przycisk_nowa_plytka")
    e.klawisz(Qt.Key.Key_Escape)
    trzecia = atrapa.symuluj_skan("czysta", numer=3, projekty={1: 21, 2: 22, 3: 23, 4: 24})
    assert e.okno.pokazana_plytka() == pierwsza  # bez otwartej pracy, ale na plytce 1 sa prace do obejrzenia
    e.klik(f"plytka_{druga}")
    assert N.PLYTKA_NOWA not in e.tekst_elementu(f"plytka_{druga}") and N.PLYTKA_NOWA in e.tekst_elementu(f"plytka_{trzecia}")
    czwarta = atrapa.symuluj_skan("czysta", numer=4, projekty={1: 31, 2: 32, 3: 33, 4: 34})
    assert e.okno.pokazana_plytka() == czwarta  # plytka 2 (same zielone) nie miala nic do obejrzenia: ekran idzie za nowa plytka
    assert N.PLYTKA_NOWA in e.tekst_elementu(f"plytka_{trzecia}")  # trzecia nadal nieobejrzana - znaczek zostaje
    e.klik("przycisk_nowa_plytka")
    assert e.okno.pokazana_plytka() == trzecia and not e.jest("przycisk_nowa_plytka")


def test_nawigacja_lista_nastepna_poza_gniazdem_dwie_prace_i_wczesniejsze_zmiany(atrapa, ekrany, zegar):
    """Drogi po ekranie: klikniecie pozycji listy pokazuje prace, N = nastepna praca do obejrzenia, praca poza gniazdem
    i dwie prace w gniezdzie maja swoj widok, plytki wczesniejszej zmiany tej doby sa pod przyciskiem."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    from stanowisko import statusy as ST
    from stanowisko.ui import napisy as N

    atrapa.wybierz_operatora("Technik A")
    pierwsza = atrapa.symuluj_skan("zwykla", numer=1)
    atrapa.ukruszona(atrapa.stan().plytka(pierwsza).gniazdo(2).praca.praca_id)
    druga = atrapa.symuluj_skan("do_powtorzenia", numer=2, gniazda={1: "zielony", 3: "podwojny"}, poza_gniazdem=1, projekty={1: 11, 3: 13})
    e = ekrany(atrapa)
    assert e.okno.pokazana_plytka() == druga
    # praca poza gniazdem i dwie prace w jednym gniezdzie
    e.klik("poza_0")
    assert e.jest("widok_pracy") and e.w("praca_tytul").text() == N.PRACA_TYTUL_POZA.format(plytka=N.PLYTKA_NR.format(numer=2))
    assert ST.STATUSY["poza_gniazdem"].opis in e.tekst_elementu("widok_pracy")
    e.klik_gniazdo(3)
    assert e.jest("przycisk_inna_praca") and e.w("przycisk_inna_praca").text() == N.PRACA_Z_DWOCH.format(nr=1, ile=2)
    e.klik("przycisk_inna_praca")
    assert e.w("przycisk_inna_praca").text() == N.PRACA_Z_DWOCH.format(nr=2, ile=2)
    e.klik("przycisk_zamknij_prace")
    assert not e.jest("widok_pracy")
    # pozycja listy -> plytka i gniazdo tej pracy
    tabela = e.w("tabela_dofrezowania")
    QTest.mouseClick(tabela.viewport(), Qt.MouseButton.LeftButton, pos=tabela.visualItemRect(tabela.item(0, 0)).center())
    e.odczekaj(20)
    assert e.okno.pokazana_plytka() == pierwsza and e.jest("widok_pracy")
    plytka_1 = N.PLYTKA_NR.format(numer=1)
    assert e.w("praca_tytul").text() == N.PRACA_TYTUL.format(plytka=plytka_1, gniazdo=2)
    # N: kolejne prace bez decyzji, ktore nie sa zielone (3, 4, 5, 6, 7, 9), potem od poczatku
    kolejne = []
    for _ in range(7):
        e.klawisz(Qt.Key.Key_N)
        kolejne.append(e.w("praca_tytul").text())
    assert kolejne == [N.PRACA_TYTUL.format(plytka=plytka_1, gniazdo=nr) for nr in (3, 4, 5, 6, 7, 9, 3)]
    e.klawisz(Qt.Key.Key_Escape)
    # nastepna zmiana tej samej doby: lista pokazuje plytki biezacej zmiany, wczesniejsze pod przyciskiem
    zegar.przesun(4 * 60)
    atrapa.przetworz()
    atrapa.wybierz_operatora("Technik A")
    trzecia = atrapa.symuluj_skan("czysta", numer=3, projekty={1: 21, 2: 22, 3: 23, 4: 24})
    assert atrapa.stan().zmiana == 3 and e.okno.pokazana_plytka() == pierwsza  # plytka 1 ma prace do obejrzenia: ekran czeka (A-P2)
    e.klik("przycisk_nowa_plytka")
    assert e.plytki() == [trzecia]
    assert e.w("przycisk_wczesniejsze").text() == N.WCZESNIEJSZE_POKAZ.format(n=2)
    e.klik("przycisk_wczesniejsze")
    assert e.plytki() == [pierwsza, druga, trzecia] and e.w("przycisk_wczesniejsze").text() == N.WCZESNIEJSZE_UKRYJ
    e.klik("przycisk_wczesniejsze")
    assert e.plytki() == [trzecia]


# ----------------------------------------------------------------------------
# runda 2 recenzji PR #21 (raport ``recenzja/raport_recenzenta_PR21_PR20r2.md``): A-P1 ... A-P5 i uwagi D
# ----------------------------------------------------------------------------
ROZMIARY_PROBY = ((1280, 720), (1366, 768), (1600, 900))
PELNA = {1: "zielony", 2: "czerwony", 3: "zielony", 4: "zolty", 5: "zielony", 6: "zielony", 7: "szary", 8: "zielony", 9: "czerwony", 10: "zielony",
         11: "zielony", 12: "pomaranczowy", 13: "zielony", 14: "zielony", 15: "nie_sprawdzono", 16: "zielony", 17: "zielony", 18: "zielony"}
DLUGI_TEKST = "Bardzo dlugi tekst komunikatu, ktory ma sprawdzic zawijanie i wysokosc panelu. " * 8


def pelna_baza(atrapa) -> None:
    """Fikcyjne zlecenia 31-90 w indeksie atrapy (jak w zrzutach ekranu): pelne plytki po 18 prac z kuweta, zebem i krazkiem."""
    from stanowisko import kontroler_api as K

    baza, czas = atrapa.sesja.baza, atrapa.sesja.teraz()
    with baza.transakcja():
        for nr in range(31, 91):
            zlecenie = baza.wstaw("zlecenia", zrodlo="cyrkon", folder=f"{9000 + nr} Zlecenie {nr}", folder_norm=f"{9000 + nr} zlecenie {nr}",
                                  kuweta=str(9000 + nr), dodano=czas, usuniety=0)
            projekt = baza.wstaw("projekty", zlecenie_id=zlecenie, plik=f"projekt-{nr}-crown_cad.stl", sha16=K.projekt_sztuczny(nr),
                                 zeby=str(11 + nr % 37), typ="korona", usuniety=0)
            baza.wstaw("frezowania", projekt_id=projekt, plik_w_raporcie=f"projekt-{nr}-crown_cad.stl", krazek="K-2", wspolczynnik=1.225,
                       data=czas[:10], zrodlo="reczny")


def wieczor_pokazowy(atrapa, zegar, decyzje: bool = True) -> tuple:
    """Trzy plytki jak na zrzutach: nr 1 pelna (z decyzjami), nr 2 czysta, nr 3 pelna bez decyzji (biezaca)."""
    pierwsza = atrapa.symuluj_skan("zwykla", numer=1, gniazda=PELNA)
    zegar.przesun(12)
    atrapa.symuluj_skan("czysta", numer=2, gniazda={n: "zielony" for n in range(2, 14)}, projekty={n: 17 + n for n in range(2, 14)})
    zegar.przesun(11)
    if decyzje:
        p = atrapa.stan().plytka(pierwsza)
        atrapa.ukruszona(p.gniazdo(2).praca.praca_id)
        atrapa.ok(p.gniazdo(9).praca.praca_id)
    trzecia = atrapa.symuluj_skan("zwykla", numer=3, gniazda={**PELNA, 2: "zielony", 5: "czerwony", 9: "zielony", 11: "zolty", 4: "zielony",
                                                              12: "zielony", 15: "zielony", 7: "zielony"}, projekty={n: 30 + n for n in range(1, 19)})
    return pierwsza, trzecia


SCENY = ("mapa_po_skanie", "czerwona_praca", "lista_wszystkie", "pytanie_ponowny_skan", "poranna_pytanie", "bez_osoby", "bez_numeru",
         "popraw_ulozenie", "blad_zapisu_pula_osoba", "trzy_panele_dwa_bledy", "praca_z_decyzja_bez_osoby_i_bledy", "dlugi_komunikat", "wiele_plytek")


def zbuduj_scene(atrapa, zegar, ekrany, scena: str, rozmiar: tuple) -> Ekran:
    """Stan ekranu z zrzutow i prob recenzenta (dane fikcyjne); okno otwarte w rozmiarze ``rozmiar``."""
    pelna_baza(atrapa)
    if scena != "bez_osoby":
        atrapa.wybierz_operatora("Technik A")
    kroki: list = []
    if scena in ("mapa_po_skanie", "czerwona_praca", "lista_wszystkie", "bez_osoby"):
        wieczor_pokazowy(atrapa, zegar, decyzje=scena != "bez_osoby")
        kroki = {"czerwona_praca": [("gniazdo", 5)], "lista_wszystkie": [("gniazdo", 5), ("klik", "przycisk_ukruszona"), ("klik", "lista_wszystkie")],
                 "bez_osoby": [("gniazdo", 5)]}.get(scena, [])
    elif scena == "pytanie_ponowny_skan":
        wieczor_pokazowy(atrapa, zegar)
        zegar.przesun(9)
        atrapa.symuluj_skan("zwykla", numer=1, gniazda=PELNA)
    elif scena == "poranna_pytanie":
        wieczor_pokazowy(atrapa, zegar)
        zegar.przesun(5)
        atrapa.symuluj_skan("nie_z_trybu", numer=4, gniazda={n: ("czerwony" if n in (6, 15) else "zolty" if n == 9 else "zielony") for n in range(1, 25)},
                            projekty={n: 50 + n for n in range(1, 25)})
    elif scena == "bez_numeru":
        wieczor_pokazowy(atrapa, zegar)
        zegar.przesun(5)
        atrapa.symuluj_skan("bez_numeru", gniazda={n: ("czerwony" if n == 6 else "zolty" if n == 10 else "zielony") for n in range(2, 16)},
                            projekty={n: 50 + n for n in range(2, 16)})
    elif scena == "popraw_ulozenie":
        wieczor_pokazowy(atrapa, zegar)
        zegar.przesun(5)
        atrapa.symuluj_skan("do_powtorzenia", numer=4, gniazda={2: "zielony", 3: "popraw_ulozenie", 5: "zielony", 6: "skan_ponownie", 8: "zielony",
                                                                9: "czerwony"}, projekty={n: 50 + n for n in range(1, 12)}, poza_gniazdem=1)
        atrapa.symuluj_postep(udzial=0.4, czeka=1)
    elif scena == "blad_zapisu_pula_osoba":
        wieczor_pokazowy(atrapa, zegar)
        zegar.przesun(5)
        atrapa.symuluj_blad_zapisu(1)
        atrapa.symuluj_pule("pusta")
        atrapa.symuluj_kolejke(wstrzymane=2)
        kroki = [("klik", "przycisk_zmien_osobe")]
    elif scena == "trzy_panele_dwa_bledy":  # proba recenzenta "blad zapisu schowany" (A-P3)
        atrapa.symuluj_skan("zwykla", numer=1, gniazda=PELNA)
        zegar.przesun(15)
        atrapa.symuluj_skan("do_powtorzenia", numer=1, gniazda={1: "zielony", 2: "skan_ponownie", 7: "blad_inspekcji", 9: "czerwony"},
                            projekty={n: 60 + n for n in range(1, 10)})
        kroki = [("blad_zapisu",), ("skaner",), ("postep",)]
    elif scena == "praca_z_decyzja_bez_osoby_i_bledy":  # najwiecej napisow w widoku pracy naraz + pasek bledow + dlugi pasek stanu
        wieczor_pokazowy(atrapa, zegar)
        zegar.przesun(70)
        piata = atrapa.symuluj_skan("zwykla", numer=5, gniazda=PELNA)  # te same projekty co plytka 1: "zab juz na liscie" i konflikty
        atrapa.ok(atrapa.stan().plytka(piata).gniazdo(2).praca.praca_id)
        atrapa.symuluj_blad_zapisu(1)
        atrapa.symuluj_skaner(dostepny=False)
        atrapa.symuluj_postep(udzial=0.4, czeka=2)
        atrapa.symuluj_kolejke(czeka=2, wstrzymane=1)
        atrapa.wybierz_operatora(None)
        kroki = [("plytka", piata), ("gniazdo", 2)]
    elif scena == "dlugi_komunikat":
        wieczor_pokazowy(atrapa, zegar)
        zegar.przesun(5)
        rano = atrapa.symuluj_skan("nie_z_trybu", numer=4, gniazda={n: ("czerwony" if n in (6, 15) else "zielony") for n in range(1, 25)},
                                   projekty={n: 50 + n for n in range(1, 25)})
        atrapa.dopusc_plytke(rano)
        atrapa.symuluj_komunikat("odmowa", powod=DLUGI_TEKST)
        kroki = [("gniazdo", 6)]
    elif scena == "wiele_plytek":  # proba recenzenta "36 plytek" w mniejszej skali: 3 numery plytek, ponowne skany co 3 min
        for i in range(12):
            zegar.przesun(3)
            atrapa.symuluj_skan("zwykla", numer=i % 3 + 1, gniazda=PELNA, projekty={n: 31 + (i * 18 + n) % 60 for n in range(1, 19)})
    else:
        raise ValueError(scena)
    e = ekrany(atrapa, rozmiar)
    for krok in kroki:
        if krok[0] == "gniazdo":
            e.klik_gniazdo(krok[1])
        elif krok[0] == "klik":
            e.klik(krok[1])
        elif krok[0] == "plytka":
            e.klik(f"plytka_{krok[1]}")
        elif krok[0] == "blad_zapisu":
            atrapa.symuluj_blad_zapisu(1)
        elif krok[0] == "skaner":
            atrapa.symuluj_skaner(dostepny=False)
        elif krok[0] == "postep":
            atrapa.symuluj_postep(udzial=0.4, czeka=2)
    e.zdarzenia()
    return e


def _w_oknie(okno, w):
    from PySide6.QtCore import QPoint, QRect

    return QRect(w.mapTo(okno, QPoint(0, 0)), w.size())


def _widoczny_wycinek(okno, w):
    """Prostokat ``w`` w ukladzie okna przyciety przez wszystkich rodzicow (to, co technik naprawde widzi)."""
    r = _w_oknie(okno, w)
    p = w.parentWidget()
    while p is not None and p is not okno:
        r = r.intersected(_w_oknie(okno, p))
        p = p.parentWidget()
    return r.intersected(okno.rect())


def _w_obszarze_przewijanym(okno, w) -> bool:
    from PySide6.QtWidgets import QAbstractScrollArea

    p = w.parentWidget()
    while p is not None and p is not okno:
        if isinstance(p, QAbstractScrollArea):
            return True
        p = p.parentWidget()
    return False


def sprawdz_uklad(e: Ekran, rozmiar: tuple) -> list:
    """A-P1: okno w rozmiarze ``rozmiar``; zwraca liste usterek: przycisk albo napis poza oknem / poza rodzicem, napis przycisku
    albo etykiety uciety (``sizeHint`` / ``heightForWidth`` wieksze niz rozmiar), dwa klikalne elementy na sobie, mapa poza oknem
    albo mniejsza niz jej minimum, uklad potrzebujacy wiecej miejsca niz okno."""
    from PySide6.QtWidgets import QLabel, QPushButton, QTableWidget, QWidget

    from stanowisko.ui.czesci import KafelekPlytki
    from stanowisko.ui.mapa import MapaPlytki

    okno = e.okno
    okno.resize(*rozmiar)
    for _ in range(3):
        e.zdarzenia()
        e.odczekaj(20)
    usterki = []
    if (okno.width(), okno.height()) != tuple(rozmiar):
        usterki.append(f"okno {okno.width()}x{okno.height()} zamiast {rozmiar}")
    minimum = okno.layout().minimumSize()
    if minimum.width() > okno.width() or minimum.height() > okno.height():
        usterki.append(f"uklad potrzebuje {minimum.width()}x{minimum.height()}")
    klikalne = []
    for w in okno.findChildren(QWidget):
        if not w.isVisibleTo(okno):
            continue
        nazwa = f"{w.objectName() or type(w).__name__} {(w.text() if isinstance(w, (QLabel, QPushButton)) else '')[:40]!r}"
        tekstowy = isinstance(w, QPushButton) or (isinstance(w, QLabel) and bool(w.text()) and w.objectName() != "praca_obraz")
        if tekstowy:
            rodzic = w.parentWidget()
            if rodzic is not None and not rodzic.rect().adjusted(-1, -1, 1, 1).contains(w.geometry()):
                usterki.append(f"poza rodzicem {rodzic.objectName() or type(rodzic).__name__}: {nazwa} {w.geometry()}")
            if not _w_obszarze_przewijanym(okno, w) and not okno.rect().adjusted(-1, -1, 1, 1).contains(_w_oknie(okno, w)):
                usterki.append(f"poza oknem: {nazwa} {_w_oknie(okno, w)}")
            if isinstance(w, QPushButton):
                hint = w.sizeHint()
                if hint.width() > w.width() + 1 or hint.height() > w.height() + 1:
                    usterki.append(f"uciety przycisk {nazwa}: {w.width()}x{w.height()}, potrzebne {hint.width()}x{hint.height()}")
            elif w.wordWrap():
                if w.heightForWidth(w.width()) > w.height() + 1:
                    usterki.append(f"ucieta etykieta (wysokosc) {nazwa}: {w.height()}, potrzebne {w.heightForWidth(w.width())}")
            elif w.sizeHint().width() > w.width() + 1:
                usterki.append(f"ucieta etykieta {nazwa}: {w.width()}, potrzebne {w.sizeHint().width()}")
        if isinstance(w, (QPushButton, KafelekPlytki, MapaPlytki, QTableWidget)):
            wycinek = _widoczny_wycinek(okno, w)
            if not wycinek.isEmpty():
                klikalne.append((w, wycinek, nazwa))
    for i, (a, ra, na) in enumerate(klikalne):
        for b, rb, nb in klikalne[i + 1:]:
            if not (a.isAncestorOf(b) or b.isAncestorOf(a)) and ra.intersects(rb):
                usterki.append(f"na sobie: {na} {ra} i {nb} {rb}")
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QScrollArea

    for obszar in okno.findChildren(QScrollArea):  # bez poziomego przewijania zawartosc musi miescic sie w szerokosci obszaru
        if (obszar.isVisibleTo(okno) and obszar.widget() is not None and obszar.horizontalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAlwaysOff
                and obszar.widget().width() > obszar.viewport().width() + 1):
            usterki.append(f"za szeroka zawartosc {obszar.objectName() or type(obszar).__name__}: {obszar.widget().width()} > {obszar.viewport().width()}")
    mapa = okno.mapa
    if not okno.rect().contains(_w_oknie(okno, mapa)):
        usterki.append(f"mapa poza oknem: {_w_oknie(okno, mapa)}")
    if mapa.height() < mapa.minimumHeight() or mapa.width() < mapa.minimumWidth():
        usterki.append(f"mapa {mapa.width()}x{mapa.height()} mniejsza niz minimum {mapa.minimumWidth()}x{mapa.minimumHeight()}")
    return usterki


@pytest.mark.parametrize("scena", SCENY)
def test_ap1_uklad_miesci_sie_przy_1280x720_1366x768_1600x900_i_minimum(atrapa, ekrany, zegar, scena):
    """A-P1: dla kazdego stanu z zrzutow i prob recenzenta - przy 1280 x 720 (laptop 1920 x 1080, skalowanie 150 %), 1366 x 768,
    1600 x 900 i przy najmniejszym oknie - kazdy widoczny przycisk i napis miesci sie w oknie i w rodzicu, nie jest uciety,
    klikalne elementy nie leza na sobie, mapa jest w oknie. Okno otwarte od razu male, potem zmieniane (przelaczanie ukladu)."""
    from stanowisko.ui import styl

    assert styl.MINIMUM_OKNA[0] <= 1280 and styl.MINIMUM_OKNA[1] <= 720
    e = zbuduj_scene(atrapa, zegar, ekrany, scena, ROZMIARY_PROBY[0])
    assert (e.okno.minimumWidth(), e.okno.minimumHeight()) == styl.MINIMUM_OKNA
    for rozmiar in ROZMIARY_PROBY + (styl.MINIMUM_OKNA, ROZMIARY_PROBY[0]):
        usterki = sprawdz_uklad(e, rozmiar)
        assert not usterki, f"{scena} {rozmiar}:\n" + "\n".join(usterki)
        assert e.okno.zwarty() == (rozmiar[0] < styl.PROG_ZWARTEGO[0] or rozmiar[1] < styl.PROG_ZWARTEGO[1])


def test_ap1_wyglad_przy_1600x900_bez_zmian(atrapa, ekrany, zegar):
    """Przy 1600 x 900 uklad zwykly jak w rundzie 1: duze przyciski decyzji (68 px), kolumny 250 / 540 px, mapa co najmniej
    380 x 300 px; przy 1280 x 720 uklad zwarty z mniejszymi przyciskami, ale nadal duzymi do klikniecia (co najmniej 34 px)."""
    from stanowisko.ui import styl

    pelna_baza(atrapa)
    atrapa.wybierz_operatora("Technik A")
    wieczor_pokazowy(atrapa, zegar)
    e = ekrany(atrapa)
    e.klik_gniazdo(5)
    assert not e.okno.zwarty()
    assert e.w("przycisk_ukruszona").height() >= styl.ZWYKLE.wysokosc_decyzji and e.w("lista_plytek").width() == 250
    assert e.w("prawa_kolumna").width() == 540 and e.mapa.width() >= 380 and e.mapa.height() >= 300
    assert not sprawdz_uklad(e, (1280, 720))
    assert e.okno.zwarty() and e.w("przycisk_ukruszona").height() >= styl.ZWARTE.wysokosc_decyzji >= 34
    assert all(e.w(n).height() >= 34 for n in ("przycisk_ok", "przycisk_cofnij", "przycisk_nastepna", "przycisk_zamknij_prace"))


def test_ap2_nowy_wynik_nie_podmienia_mapy_z_pracami_do_obejrzenia(atrapa, ekrany, zegar):
    """Scenariusz recenzenta: technik celuje w czerwone gniazdo 2 plytki A, w tej chwili przychodzi wynik plytki B. Na A sa prace
    do obejrzenia - ekran zostaje na A, B dostaje "NOWA" i sygnal na pasku; klikniecie i klawisz U trafiaja w A, nie w B."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    from stanowisko.ui import napisy as N

    k = Szpieg(atrapa)
    k.wybierz_operatora("Technik A")
    a = atrapa.symuluj_skan("zwykla", numer=1)
    e = ekrany(k)
    punkt = e.mapa.srodek_gniazda(2).toPoint()  # technik celuje w gniazdo 2 plytki A
    zegar.przesun(3)
    b = atrapa.symuluj_skan("zwykla", numer=2, projekty={n: 10 + n for n in range(1, 10)})
    QTest.mouseClick(e.mapa, Qt.MouseButton.LeftButton, pos=punkt)  # bez czekania, jak technik w trakcie ruchu reki
    QTest.keyClick(e.okno, Qt.Key.Key_U)
    e.odczekaj(10)
    stan = atrapa.stan()
    assert e.okno.pokazana_plytka() == a and not e.okno.ochrona_aktywna()  # mapa sie nie zmienila - nie ma czego chronic
    assert stan.plytka(a).gniazdo(2).praca.decyzja == "ukruszona" and stan.plytka(b).gniazdo(2).praca.decyzja is None
    assert k.wyslane("ukruszona") == [("ukruszona", (stan.plytka(a).gniazdo(2).praca.praca_id,))]
    assert N.PLYTKA_NOWA in e.tekst_elementu(f"plytka_{b}")
    assert e.jest("przycisk_nowa_plytka") and e.w("przycisk_nowa_plytka").text() == N.NOWA_PLYTKA.format(plytka=N.PLYTKA_NR.format(numer=2))
    e.klawisz(Qt.Key.Key_Escape)
    e.klik("przycisk_nowa_plytka")  # przelacza technik
    assert e.okno.pokazana_plytka() == b and not e.jest("przycisk_nowa_plytka") and N.PLYTKA_NOWA not in e.tekst_elementu(f"plytka_{b}")


def test_ap2_klawisz_U_tuz_po_wyniku_plytki_B_nie_zapisuje_decyzji_na_B(atrapa, ekrany, zegar):
    """Plytka A bez prac do obejrzenia: wynik plytki B przelacza ekran sam. Klikniecie w miejsce gniazda 2 (celowane w A),
    klawisz U i Enter w ciagu ``OCHRONA_MS`` po podmianie mapy sa pomijane, mapa jest przygaszona (widac na obrazie);
    po tym czasie klikniecie dziala. Zmiana plytki przez technika tez przygasza mape; wlasna decyzja - nie."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    from stanowisko.ui import okno as O

    assert O.OCHRONA_MS == 800
    k = Szpieg(atrapa)
    k.wybierz_operatora("Technik A")
    a = atrapa.symuluj_skan("czysta", numer=1)
    e = ekrany(k)
    punkt = e.mapa.srodek_gniazda(2).toPoint()
    assert not e.okno.ochrona_aktywna()
    zegar.przesun(3)
    b = atrapa.symuluj_skan("zwykla", numer=2, projekty={n: 10 + n for n in range(1, 10)})
    assert e.okno.pokazana_plytka() == b and e.okno.ochrona_aktywna() and e.mapa.przygaszona()
    przed = list(k.polecenia)
    QTest.mouseClick(e.mapa, Qt.MouseButton.LeftButton, pos=punkt)
    QTest.keyClick(e.okno, Qt.Key.Key_U)
    QTest.keyClick(e.okno, Qt.Key.Key_Return)
    assert e.okno.ochrona_aktywna(), "proba za wolna - klikniecia po czasie ochrony"
    obraz = e.mapa.grab().toImage()
    assert obraz.pixelColor(e.mapa.punkt_probny(2).toPoint()).name() != atrapa.stan().plytka(b).gniazdo(2).rgb  # mapa przygaszona
    e.odczekaj(10)
    assert k.polecenia == przed and not e.jest("widok_pracy")
    assert all(p.decyzja is None for p in atrapa.stan().plytka(b).prace)
    e.po_ochronie()
    assert not e.mapa.przygaszona() and e.kolory_pikseli()[2] == atrapa.stan().plytka(b).gniazdo(2).rgb
    QTest.mouseClick(e.mapa, Qt.MouseButton.LeftButton, pos=e.mapa.srodek_gniazda(2).toPoint())
    e.odczekaj(10)
    assert e.jest("widok_pracy")
    e.klawisz(Qt.Key.Key_U)
    assert k.wyslane("ukruszona") == [("ukruszona", (atrapa.stan().plytka(b).gniazdo(2).praca.praca_id,))]
    assert not e.okno.ochrona_aktywna()  # wlasna decyzja zmienia mape, ale jej nie przygasza
    e.klawisz(Qt.Key.Key_Escape)
    e.klik(f"plytka_{a}")  # przelaczenie przez technika (kafelek) tez zmienia zawartosc mapy
    assert e.okno.pokazana_plytka() == a and e.okno.ochrona_aktywna()
    k.polecenia.clear()
    e.klik_gniazdo(2)  # technik poczekal na koniec przygaszenia
    assert e.jest("widok_pracy") and k.polecenia == []


def test_ap2_widok_pracy_naglowek_i_decyzja_tylko_dla_pokazanej_pracy(atrapa, ekrany):
    """Widok pracy ma duzy naglowek "Plytka n - gniazdo m". Stan zmieniony w tle tak, ze gniazdo pokazuje inna prace -> widok
    sie zamyka z informacja i U / O nic nie wysylaja; praca znika ze stanu -> to samo z inna informacja."""
    import dataclasses

    from PySide6.QtCore import Qt

    from stanowisko.ui import napisy as N

    k = Szpieg(atrapa)
    k.wybierz_operatora("Technik A")
    skan_id = atrapa.symuluj_skan("zwykla", numer=3)
    e = ekrany(k)
    e.klik_gniazdo(2)
    assert e.w("praca_tytul").text() == N.PRACA_TYTUL.format(plytka=N.PLYTKA_NR.format(numer=3), gniazdo=2)
    assert e.w("praca_tytul").property("rola") == "tytul"  # najwieksza czcionka widoku
    stan = atrapa.stan()
    plytka = stan.plytka(skan_id)
    praca_2, praca_9 = plytka.gniazdo(2).praca, plytka.gniazdo(9).praca
    zamienione = tuple(dataclasses.replace(g, prace=(praca_9,)) if g.nr == 2 else dataclasses.replace(g, prace=(praca_2,)) if g.nr == 9 else g
                       for g in plytka.gniazda)
    e.okno.pokaz_stan(dataclasses.replace(stan, wersja=stan.wersja + 1, plytki=(dataclasses.replace(plytka, gniazda=zamienione),)))
    assert not e.jest("widok_pracy") and e.jest("informacja_ekranu") and N.PRACA_ZMIENIONA in e.tekst_elementu("informacja_ekranu")
    k.polecenia.clear()
    e.klawisz(Qt.Key.Key_U)
    e.klawisz(Qt.Key.Key_O)
    assert k.polecenia == []
    e.klik("zamknij_informacje")
    assert not e.jest("informacja_ekranu")
    atrapa.symuluj_komunikat("plik_zmieniony")  # prawdziwy stan (wersja rowna podmienionej) wraca na ekran
    e.klik_gniazdo(2)
    assert e.jest("widok_pracy") and e.w("praca_tytul").text() == N.PRACA_TYTUL.format(plytka=N.PLYTKA_NR.format(numer=3), gniazdo=2)
    stan = atrapa.stan()
    e.okno.pokaz_stan(dataclasses.replace(stan, wersja=stan.wersja + 5, plytki=()))  # np. nowa doba robocza: plytki nie ma
    assert not e.jest("widok_pracy") and N.PRACA_ZNIKNELA in e.tekst_elementu("informacja_ekranu")
    e.klawisz(Qt.Key.Key_U)
    assert k.wyslane("ukruszona", "ok", "cofnij") == []


def test_ap3_bledy_programu_na_wlasnym_pasku_poza_limitem_paneli(atrapa, ekrany, zegar):
    """Proba recenzenta: pokazana plytka ma 3 wlasne panele (pytanie o ponowny skan, "Praca niesprawdzona", "Skan do powtorzenia"),
    przychodzi blad zapisu i znika folder skanera. Oba bledy programu sa na pasku bledow nad calym ekranem, w calosci widoczne
    (1600 x 900 i 1280 x 720), nie licza sie do "i jeszcze n"; inne komunikaty ogolne zostaja w panelach pod limitem."""
    from stanowisko.ui import napisy as N

    k = Szpieg(atrapa)
    k.wybierz_operatora("Technik A")
    atrapa.symuluj_skan("zwykla", numer=1, gniazda=PELNA)
    zegar.przesun(15)
    drugi = atrapa.symuluj_skan("do_powtorzenia", numer=1, gniazda={1: "zielony", 2: "skan_ponownie", 7: "blad_inspekcji", 9: "czerwony"},
                                projekty={n: 60 + n for n in range(1, 10)})
    e = ekrany(k)
    assert e.okno.pokazana_plytka() == drugi
    assert {p.objectName() for p in e.okno.uwagi.panele()} == {"pytanie_ponowny_skan", "komunikat_blad_inspekcji", "komunikat_skan_do_powtorzenia"}
    atrapa.symuluj_blad_zapisu(1)
    atrapa.symuluj_skaner(dostepny=False)
    for _ in range(4):
        atrapa.symuluj_komunikat("plik_zmieniony")  # komunikat informacyjny - zostaje w panelach (czwarty panel -> "i jeszcze 1")
    for rozmiar in ((1600, 900), (1280, 720)):
        assert not sprawdz_uklad(e, rozmiar)
        for nazwa in ("komunikat_blad_zapisu", "komunikat_folder_skanera_niedostepny"):
            w = e.w(nazwa)
            assert e.jest(nazwa) and e.okno.bledy.isAncestorOf(w) and not e.okno.uwagi.isAncestorOf(w), (rozmiar, nazwa)
            assert _widoczny_wycinek(e.okno, w) == _w_oknie(e.okno, w), (rozmiar, nazwa, "blad programu nie jest widoczny w calosci")
        assert e.w("uwagi_jeszcze").text() == N.JESZCZE.format(n=1) and e.w("uwagi_jeszcze").property("rola") == "uwaga"
        assert len([p for p in e.okno.uwagi.panele() if p.objectName() != "uwagi_jeszcze"]) == 3
    e.klik("komunikat_ponow_zapis")  # przyciski bledu dzialaja z paska bledow
    assert k.polecenia[-1] == ("ponow_zapis", ())


def test_ap5_napisy_po_recenzji(atrapa, ekrany, zegar):
    """Lista "bylo -> ma byc" recenzenta: plytka z pracami do obejrzenia nie jest "sprawdzona" ("do obejrzenia: n", w statusy
    "przeanalizowana"), "sprawdzona" dopiero po decyzjach; "Podaj numer plytki" tylko bez numeru (z numerem maly "Zmien numer");
    "Plytka bez numeru" bez "?" i panel numeru bez przedrostka; pytanie o plytke nie z trybu bez powtorzonego zdania; napis puli
    bez "STL" i "pula"; przycisk skanu nie mowi, ze program skanuje (start skanu to atrapa)."""
    from PySide6.QtCore import Qt

    from stanowisko import statusy as ST
    from stanowisko.ui import czesci as C
    from stanowisko.ui import napisy as N

    k = Szpieg(atrapa)
    k.wybierz_operatora("Technik A")
    s = atrapa.symuluj_skan("zwykla", numer=1, gniazda={1: "zielony", 2: "czerwony", 3: "zolty", 4: "zielony"})
    e = ekrany(k)
    przeanalizowana = ST.STATUSY_PLYTKI["przyjety"]
    assert przeanalizowana != N.PLYTKA_SPRAWDZONA
    assert e.w("mapa_naglowek").text() == N.MAPA_NAGLOWEK.format(plytka=N.PLYTKA_NR.format(numer=1), napis=N.PLYTKA_DO_OBEJRZENIA.format(n=2))
    assert przeanalizowana in e.w("mapa_godzina").text() and N.PLYTKA_DO_OBEJRZENIA.format(n=2) in e.tekst_elementu(f"plytka_{s}")
    assert N.PLYTKA_SPRAWDZONA not in e.tekst()
    assert e.w("plytka_podaj_numer_plytki").text() == N.ZMIEN_NUMER  # plytka ma numer
    e.klik_gniazdo(2)
    e.klik("przycisk_ukruszona")
    assert e.w("mapa_naglowek").text().endswith(N.PLYTKA_DO_OBEJRZENIA.format(n=1))
    e.klik_gniazdo(3)
    e.klik("przycisk_ok")
    assert e.w("mapa_naglowek").text() == N.MAPA_NAGLOWEK.format(plytka=N.PLYTKA_NR.format(numer=1), napis=N.PLYTKA_SPRAWDZONA)
    assert N.PLYTKA_SPRAWDZONA in e.tekst_elementu(f"plytka_{s}")
    e.klawisz(Qt.Key.Key_Escape)
    # plytka bez numeru: "Plytka bez numeru", panel pytania z tytulem bez przedrostka, przycisk "Podaj numer plytki" po "Pozniej"
    zegar.przesun(5)
    b = atrapa.symuluj_skan("bez_numeru")
    assert e.okno.pokazana_plytka() == b  # plytka 1 obejrzana w calosci: ekran przechodzi na nowa plytke sam
    assert e.w("mapa_naglowek").text().startswith(N.PLYTKA_BEZ_NUMERU) and "?" not in e.w("mapa_naglowek").text()
    assert ST.PYTANIA["brak_numeru_plytki"].tytul in e.tekst_elementu("pytanie_brak_numeru_plytki")
    assert C.tytul_plytki(N.PLYTKA_BEZ_NUMERU, ST.PYTANIA["brak_numeru_plytki"].tytul) not in e.tekst_elementu("pytanie_brak_numeru_plytki")
    e.klik("odp_zamknij_pytanie")
    assert e.w("plytka_podaj_numer_plytki").text() == ST.PRZYCISKI["podaj_numer_plytki"]
    e.klik("plytka_podaj_numer_plytki")
    assert ST.PRZYCISKI["podaj_numer_plytki"] in e.tekst_elementu("panel_numer_plytki")
    e.klik("numer_bez_zmian")
    # plytka poranna: rada i tekst pytania bez powtorzonego "To plytka poranna"
    zegar.przesun(5)
    p = atrapa.symuluj_skan("nie_z_trybu", numer=4)
    e.klik(f"plytka_{p}")  # plytka bez numeru ma czerwona prace bez decyzji: ekran nie przelacza sie sam
    panel = e.tekst_elementu("pytanie_plytka_nie_z_trybu")
    assert panel.count(ST.JAKA_PLYTKA["poranna"]) == 1 and N.RADA_PLYTKA_PORANNA in panel
    # pasek: napis puli bez zargonu, folder skanera, przycisk skanu zgodny z atrapa startu skanu
    assert "STL" not in e.w("napis_pula").text() and "pul" not in e.w("napis_pula").text().lower()
    assert e.w("napis_skaner").text() == N.SKANER_GOTOWY and N.SKANER in e.tekst_elementu("pole_napis_skaner")
    assert C.START_SKANU_ATRAPA and e.w("przycisk_skanuj").text() == N.SKANUJ_ATRAPA
    e.klawisz(Qt.Key.Key_Space)
    assert e.w("napis_skaner").text() == N.SKANER_CZEKA and e.w("przycisk_skanuj").text() == N.SKANUJ_ATRAPA


def test_klawiatura_strzalki_enter_tab(atrapa, ekrany):
    """Z klawiatury (A-D): strzalki przesuwaja kursor gniazda po mapie, Enter otwiera prace pod kursorem; Tab idzie po przyciskach
    i kafelkach w kolejnosci ekranu (pasek, panele, plytki, mapa, widok pracy, lista), Enter klika przycisk z fokusem, a Spacja
    zostaje startem skanu takze przy fokusie na przycisku. Klikniecie mysza oddaje fokus oknu."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    from stanowisko.ui import napisy as N

    k = Szpieg(atrapa)
    k.wybierz_operatora("Technik A")
    s = atrapa.symuluj_skan("zwykla", numer=1)
    e = ekrany(k)
    e.klawisz(Qt.Key.Key_Right)
    assert e.mapa.kursor() == 2  # pierwsze nacisniecie: pierwsza praca do obejrzenia
    x0, y0 = e.mapa.srodek_gniazda(2).x(), e.mapa.srodek_gniazda(2).y()
    e.klawisz(Qt.Key.Key_Right)  # gniazdo 2 jest skrajne z prawej w swoim rzedzie: kursor zostaje
    assert e.mapa.kursor() == 2
    e.klawisz(Qt.Key.Key_Left)
    nr = e.mapa.kursor()
    assert nr != 2 and e.mapa.srodek_gniazda(nr).x() < x0 and abs(e.mapa.srodek_gniazda(nr).y() - y0) < 30  # sasiad w tym samym rzedzie
    e.klawisz(Qt.Key.Key_Up)
    assert e.mapa.srodek_gniazda(e.mapa.kursor()).y() < y0  # rzad wyzej
    nr = e.mapa.kursor()
    e.klawisz(Qt.Key.Key_Return)
    assert e.jest("widok_pracy") and e.w("praca_tytul").text() == N.PRACA_TYTUL.format(plytka=N.PLYTKA_NR.format(numer=1), gniazdo=nr)
    e.klawisz(Qt.Key.Key_Escape)
    e.klik_gniazdo(2)
    # kolejnosc klawisza Tab
    lancuch, w = [], e.okno.nextInFocusChain()
    while w is not e.okno and len(lancuch) < 1000:
        if w.isVisibleTo(e.okno) and w.isEnabled() and w.focusPolicy() == Qt.FocusPolicy.TabFocus:
            lancuch.append(w.objectName())
        w = w.nextInFocusChain()
    poz = {nazwa: i for i, nazwa in reversed(list(enumerate(lancuch)))}
    kolejnosc = ["przycisk_zmien_osobe", "przycisk_skanuj", "zamknij_komunikat", f"plytka_{s}", "plytka_podaj_numer_plytki", "przycisk_ukruszona",
                 "przycisk_ok", "przycisk_zamknij_prace", "lista_ta_doba", "przycisk_zapisz_liste"]
    pozycje = [poz.get(n, -1) for n in kolejnosc]
    assert -1 not in pozycje and pozycje == sorted(pozycje), lancuch
    # Spacja przy fokusie na przycisku = start skanu (nie "Ukruszona"); Enter = klikniecie przycisku z fokusem
    b = e.w("przycisk_ukruszona")
    b.setFocus(Qt.FocusReason.TabFocusReason)
    k.polecenia.clear()
    QTest.keyClick(b, Qt.Key.Key_Space)
    assert k.polecenia == [("start_skanu", ())]
    QTest.keyClick(b, Qt.Key.Key_U)  # skrot okna takze przy fokusie na przycisku
    assert k.polecenia[-1][0] == "ukruszona"
    QTest.keyClick(e.w("przycisk_cofnij"), Qt.Key.Key_Return)
    assert [p[0] for p in k.polecenia] == ["start_skanu", "ukruszona", "cofnij"]
    e.w(f"plytka_{s}").setFocus(Qt.FocusReason.TabFocusReason)
    e.klik_gniazdo(9)  # mysza: fokus wraca do okna (Enter nie kliknie pozniej elementu, do ktorego doszedl Tab)
    assert e.okno.focusWidget() is e.okno


def test_d_pasek_kafelki_lista_i_kolory_napisow(atrapa, ekrany, zegar, monkeypatch):
    """Uwagi D: (A-D6) kafelek innej plytki z komunikatem ma znacznik; (poz. 18) podpowiedz licznikow na kafelku; (A-D9) pozycja
    listy z innej doby - informacja zamiast ciszy; (A-D5) "Odswiez pule" znow aktywne po limicie liczenia; (A-D4) zamkniecie
    grupy jednakowych komunikatow = jedno odswiezenie ekranu; (A-D7) czarny napis na zielonym, bialy na czerwonym."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QLabel

    from stanowisko import statusy as ST
    from stanowisko.ui import czesci as C
    from stanowisko.ui import napisy as N
    from stanowisko.ui import styl

    monkeypatch.setattr(C, "LIMIT_LICZENIA_PULI_S", 0.3)
    atrapa.wybierz_operatora("Technik A")
    wczoraj = atrapa.symuluj_skan("zwykla", numer=1)
    atrapa.ukruszona(atrapa.stan().plytka(wczoraj).gniazdo(2).praca.praca_id)
    zegar.przesun(24 * 60)
    atrapa.przetworz()
    atrapa.wybierz_operatora("Technik A")
    a = atrapa.symuluj_skan("zwykla", numer=2, projekty={n: 10 + n for n in range(1, 10)})  # gniazdo 7: blad kontroli -> komunikat plytki
    b = atrapa.symuluj_skan("czysta", numer=3, projekty={n: 20 + n for n in range(1, 5)})
    e = ekrany(atrapa)
    assert e.okno.pokazana_plytka() == b
    assert N.PLYTKA_KOMUNIKAT in e.tekst_elementu(f"plytka_{a}") and N.PLYTKA_KOMUNIKAT not in e.tekst_elementu(f"plytka_{b}")
    licznik = next(w for w in e.w(f"plytka_{a}").findChildren(QLabel) if w.text() == "2" and w.toolTip())
    assert licznik.toolTip() == N.LICZNIK_OPIS.format(napis=ST.STATUSY["czerwony"].napis, n=2)
    # A-D9: pozycja listy z poprzedniej doby
    e.klik("lista_wszystkie")
    tabela = e.w("tabela_dofrezowania")
    QTest.mouseClick(tabela.viewport(), Qt.MouseButton.LeftButton, pos=tabela.visualItemRect(tabela.item(0, 0)).center())
    e.odczekaj(20)
    assert e.jest("informacja_ekranu") and N.POZYCJA_Z_INNEJ_DOBY.format(doba="17.11.2026", zmiana=2) in e.tekst_elementu("informacja_ekranu")
    assert e.okno.pokazana_plytka() == b
    # A-D5: liczenie puli, ktore nie wraca
    with e.bez_zegara():
        atrapa.symuluj_pule("liczenie")
        assert not e.aktywny("przycisk_odswiez_pule")
        e.czekaj(lambda: e.aktywny("przycisk_odswiez_pule"), 3.0, "Odswiez pule aktywne po limicie liczenia")
    # A-D4: grupa jednakowych komunikatow zamykana jednym kliknieciem, ekran odswiezany raz
    for _ in range(6):
        atrapa.symuluj_komunikat("plik_zmieniony")
    assert e.jest("komunikat_plik_zmieniony")
    przycisk = next(w for w in e.w("komunikat_plik_zmieniony").findChildren(C.QPushButton) if w.objectName() == "zamknij_komunikat")
    odswiezen = []
    prawdziwe = e.okno._odswiez
    e.okno._odswiez = lambda: (odswiezen.append(1), prawdziwe())
    QTest.mouseClick(przycisk, Qt.MouseButton.LeftButton)
    e.okno._odswiez = prawdziwe
    assert not e.jest("komunikat_plik_zmieniony") and len(odswiezen) == 1
    # A-D7: kolor napisu na tle statusu
    assert styl.tekst_na(ST.STATUSY["zielony"].hex) == "#111111" and styl.tekst_na(ST.STATUSY["czerwony"].hex) == "#ffffff"
    assert styl.kontrast(ST.STATUSY["zielony"].hex, styl.tekst_na(ST.STATUSY["zielony"].hex)) >= 4.5


def test_d_konflikt_projektu_z_gniazdami_i_tlo_zaznaczonej_osoby(atrapa, ekrany, zegar):
    """(A-P5 poz. 10) Panel konfliktu projektu wypisuje gniazda ze ``stan.konflikty`` (z godzina skanu - dwa skany jednej plytki
    maja ten sam numer); konflikt jest trwaly, wiec stoi na pasku bledow programu. Zaznaczona osoba w panelu zmiany osoby ma
    tlo w kolorze akcentu (arkusz obszaru paneli nie zdejmuje tla przyciskom)."""
    from PySide6.QtCore import QPoint

    from stanowisko.ui import napisy as N
    from stanowisko.ui import styl

    atrapa.wybierz_operatora("Technik A")
    atrapa.symuluj_skan("zwykla", numer=1)
    zegar.przesun(10)
    atrapa.symuluj_skan("zwykla", numer=5)  # te same projekty co na plytce 1
    e = ekrany(atrapa)
    assert atrapa.stan().konflikty and e.jest("komunikat_konflikt_projektu")
    assert e.okno.bledy.isAncestorOf(e.w("komunikat_konflikt_projektu"))
    panel = e.tekst_elementu("komunikat_konflikt_projektu")
    for numer, czas in ((1, "19:00"), (5, "19:10")):
        assert N.PLYTKA_NR.format(numer=numer) + N.KONFLIKT_GODZINA.format(godzina=czas) + ", " in panel, panel
    e.klik("przycisk_zmien_osobe")
    b = e.w("osoba_0")
    assert b.isChecked()
    p = b.mapTo(e.okno, QPoint(0, 0))
    obraz = e.obraz().copy(p.x(), p.y(), b.width(), b.height())
    assert obraz.pixelColor(8, b.height() // 2).name() == styl.AKCENT


@pytest.mark.parametrize("rozmiar", [(1600, 900), (1280, 720)])
def test_ap1_pasek_stalej_wysokosci_i_prawa_kolumna_w_miejscu(atrapa, ekrany, rozmiar):
    """Pasek stanu ma stala wysokosc (dwa stale wiersze), a przyciski decyzji stoja w miejscu, gdy zmienia sie stan: osoba
    wylogowana, pula pusta / liczona, folder skanera niedostepny, analiza z kolejka, blad zapisu i komunikaty (bledy programu
    i panele stoja nad lista plytek i mapa, nie nad prawa kolumna)."""
    from PySide6.QtCore import QPoint

    atrapa.wybierz_operatora("Technik A")
    atrapa.symuluj_skan("zwykla", numer=1)
    e = ekrany(atrapa, rozmiar)
    e.klik_gniazdo(2)

    def polozenie():
        e.zdarzenia()
        e.odczekaj(20)
        return e.w("pasek_stanu").height(), e.w("przycisk_ukruszona").mapTo(e.okno, QPoint(0, 0)), e.w("przycisk_cofnij").mapTo(e.okno, QPoint(0, 0))

    poczatek = polozenie()
    for krok in (lambda: atrapa.symuluj_pule("pusta"), lambda: atrapa.symuluj_kolejke(czeka=2, wstrzymane=3),
                 lambda: atrapa.symuluj_postep(udzial=0.4, czeka=2), lambda: atrapa.symuluj_skaner(dostepny=False),
                 lambda: atrapa.symuluj_blad_zapisu(1), lambda: atrapa.symuluj_komunikat("plik_zmieniony"),
                 lambda: atrapa.symuluj_pule("liczenie"), lambda: atrapa.wybierz_operatora(None)):
        krok()
        assert polozenie() == poczatek, (rozmiar, polozenie(), poczatek)
    assert not sprawdz_uklad(e, rozmiar)
