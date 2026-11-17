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
    """Okno wieczorne na kontrolerze ``k``: pokazane (offscreen) w rozmiarze 1600 x 900 i sterowane myszka i klawiatura."""

    def __init__(self, kontroler):
        from PySide6.QtTest import QTest

        from stanowisko import kontroler_api as K
        from stanowisko import ui

        self.k = kontroler
        self.lacznik = K.lacznik_qt(kontroler)
        self.okno = ui.utworz_okno(kontroler, self.lacznik)
        self.okno.resize(*ROZMIAR_OKNA)
        self.okno.show()
        QTest.qWaitForWindowExposed(self.okno)
        self.odczekaj()

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
        w = self.w(nazwa)
        assert w.isVisibleTo(self.okno), f"element {nazwa!r} nie jest widoczny\n{self.tekst()}"
        assert w.isEnabled(), f"element {nazwa!r} jest nieaktywny"
        QTest.mouseClick(w, Qt.MouseButton.LeftButton)
        self.odczekaj(5)

    def klik_gniazdo(self, nr: int) -> None:
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest

        self.zdarzenia()
        QTest.mouseClick(self.mapa, Qt.MouseButton.LeftButton, pos=self.mapa.srodek_gniazda(nr).toPoint())
        self.odczekaj(5)

    def klawisz(self, klawisz) -> None:
        from PySide6.QtTest import QTest

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

    def nowy(kontroler) -> Ekran:
        e = Ekran(kontroler)
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
    e.klik("plytka_cofnij_dopuszczenie")
    assert k.polecenia[-1] == ("cofnij_dopuszczenie", (skan_id,))
    nic_zielonego(e)


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
    zegar.przesun(4 * 60)  # 23:00 - zmiana 3; ekran jeszcze nie dostal nowego stanu
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
    z powodem (na projekty w puli) - nie jako blad."""
    import dataclasses

    from stanowisko import kontroler_api as K
    from stanowisko import statusy as ST
    from stanowisko.ui import napisy as N

    e = ekrany(atrapa)
    assert e.aktywny("przycisk_odswiez_pule") and not e.jest("pasek_puli")
    for stan_puli in ("liczenie", "pusta", "nieustawiona", "brak_folderu", "gotowa"):
        napis = ST.STANY_PULI[stan_puli].format(n=7)
        podmien_zywe(atrapa, pula=dataclasses.replace(atrapa.stan().pula, stan=stan_puli, napis=napis, liczba_stl=None if stan_puli == "liczenie" else 7),
                     kolejka=K.Kolejka(wstrzymane=0 if stan_puli == "gotowa" else 2, silnik_gotowy=True))
        assert e.w("napis_pula").text() == napis
        assert e.aktywny("przycisk_odswiez_pule") == (stan_puli != "liczenie") and e.jest("pasek_puli") == (stan_puli == "liczenie")
        if stan_puli != "gotowa":
            assert N.WSTRZYMANE_PULA.format(n=2) in e.w("napis_kolejka").text() and N.ANALIZA_CZEKA in e.w("napis_analiza").text()
    podmien_zywe(atrapa, kolejka=K.Kolejka(wstrzymane=1, silnik_gotowy=False))  # pula gotowa, analiza jeszcze nie ruszyla
    assert N.WSTRZYMANE_ANALIZA.format(n=1) in e.w("napis_kolejka").text()
    podmien_zywe(atrapa, pula=dataclasses.replace(atrapa.stan().pula, stan="stan_z_przyszlosci", napis="napis ze stanu"))
    assert e.w("napis_pula").text() == "napis ze stanu"  # stan puli nieznany tej wersji ekranu: napis ze stanu, bez bledu


def test_4_skaner_niedostepny_i_nieudany_start_skanu(atrapa, ekrany):
    """Folder skanera niedostepny: napis na pasku i komunikat ze stanu. Nieudany start skanu: tekst odmowy na ekranie - takze
    wtedy, gdy kontroler nie dal go w komunikatach stanu."""
    from PySide6.QtCore import Qt

    from stanowisko import kontroler_api as K
    from stanowisko import statusy as ST
    from stanowisko.ui import napisy as N

    odmowa = K.Odpowiedz(False, ST.tekst_komunikatu("start_skanu_nieudany")[2], "start_skanu_nieudany")
    k = Podstawiony(atrapa, {"start_skanu": odmowa})
    e = ekrany(k)
    podmien_zywe(atrapa, skaner=K.Skaner(dostepny=False, dziala=True))
    assert e.w("napis_skaner").text() == N.SKANER_BRAK_FOLDERU
    kom = atrapa.symuluj_komunikat("folder_skanera_niedostepny")
    assert e.jest("komunikat_folder_skanera_niedostepny") and kom.tekst in e.tekst()
    e.klawisz(Qt.Key.Key_Space)
    assert k.polecenia == [("start_skanu", ())]
    assert e.jest("komunikat_odpowiedz") and odmowa.tekst in e.tekst_elementu("komunikat_odpowiedz")  # komunikat, nie cisza
    e.klik("zamknij_odpowiedz")
    assert not e.jest("komunikat_odpowiedz")
    komunikat = atrapa.symuluj_komunikat("start_skanu_nieudany")  # ten sam tekst w komunikatach stanu: jeden panel, nie dwa
    e.klawisz(Qt.Key.Key_Space)
    assert e.jest("komunikat_start_skanu_nieudany") and not e.jest("komunikat_odpowiedz") and komunikat.tekst == odmowa.tekst


def test_4_zle_argumenty_tekst_odpowiedzi_na_ekranie(atrapa, ekrany):
    """Kazde polecenie moze zwrocic ``Odpowiedz(ok=False, kod="zle_argumenty")``: ekran pokazuje tekst odpowiedzi, nic nie rzuca."""
    from stanowisko import kontroler_api as K

    atrapa.wybierz_operatora("Technik A")
    skan_id = atrapa.symuluj_skan("zwykla")
    k = Podstawiony(atrapa, {"ukruszona": K.Odpowiedz(False, "Tego polecenia nie da sie wykonac - tekst z kontrolera.", "zle_argumenty")})
    e = ekrany(k)
    e.klik_gniazdo(2)
    e.klik("przycisk_ukruszona")
    assert k.polecenia == [("ukruszona", (atrapa.stan().plytka(skan_id).gniazdo(2).praca.praca_id,))]
    assert e.jest("komunikat_odpowiedz") and "tekst z kontrolera" in e.tekst_elementu("komunikat_odpowiedz")
    assert e.jest("widok_pracy") and e.lista() == []
    e.klik("przycisk_ok")  # nastepne polecenie przyjete: odmowa znika
    assert not e.jest("komunikat_odpowiedz")


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


def test_lista_zapis_do_pliku_gdy_kontrakt_ma_polecenie(atrapa, ekrany):
    """Polecenie ``zapisz_liste`` (kontrakt po rundzie 2 rdzenia): przycisk przy liscie jest wtedy i tylko wtedy, gdy kontrakt
    ma to polecenie; klikniecie wysyla je raz, a ekran nie pokazuje nazwy pliku."""
    from stanowisko import kontroler_api as K

    k = Szpieg(atrapa)
    k.wybierz_operatora("Technik A")
    atrapa.symuluj_skan("zwykla")
    e = ekrany(k)
    if "zapisz_liste" not in K.POLECENIA:
        assert not e.jest("przycisk_zapisz_liste")
        pytest.skip("kontrakt nie ma jeszcze polecenia zapisz_liste (czeka na rdzen)")
    e.klik_gniazdo(2)
    e.klik("przycisk_ukruszona")
    k.polecenia.clear()
    e.klik("przycisk_zapisz_liste")
    assert k.polecenia == [("zapisz_liste", ())]
    bez_sciezek(e)


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
    e.czekaj(lambda: e.okno.pokazana_plytka() == druga)
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
        if plytka is not None and plytka not in pomiar["zdecydowane"] and e.mapa.podpisy().get(2) == ST.STATUSY["czerwony"].napis:
            pomiar["w_kroku"] = True
            t0 = time.perf_counter()
            QTest.mouseClick(e.mapa, Qt.MouseButton.LeftButton, pos=e.mapa.srodek_gniazda(2).toPoint())
            QTest.mouseClick(e.w("przycisk_ukruszona"), Qt.MouseButton.LeftButton)
            QTest.keyClick(e.okno, Qt.Key.Key_Escape)
            pomiar["kroki"].append(time.perf_counter() - t0)
            pomiar["zdecydowane"].add(plytka)
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
    atrapa._liczba_stl = 21  # w folderze projektow przybylo plikow
    e.klik("przycisk_odswiez_pule")
    assert k.polecenia == [("odswiez_pule", ())]
    assert e.w("napis_pula").text() == ST.STANY_PULI["gotowa"].format(n=21)
    atrapa._liczba_stl = 0
    e.klik("przycisk_odswiez_pule")
    assert e.w("napis_pula").text() == ST.STANY_PULI["pusta"]


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
    re.compile(r"atrapa|podglad|wynik|qc_|AppData|Temp|pytest", re.I),  # nazwy plikow i katalogow danych sztucznych
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
    e.czekaj(lambda: len(e.plytki()) == 2 and e.jest("komunikat_skan_do_powtorzenia"), 90.0, "komunikat o poprawie ulozenia")
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
    """Gdy technik oglada prace, wynik nastepnej plytki nie przelacza ekranu - nowa plytka jest oznaczona na liscie."""
    from PySide6.QtCore import Qt

    from stanowisko.ui import napisy as N

    atrapa.wybierz_operatora("Technik A")
    pierwsza = atrapa.symuluj_skan("zwykla", numer=1)
    e = ekrany(atrapa)
    e.klik_gniazdo(2)
    druga = atrapa.symuluj_skan("czysta", numer=2, projekty={1: 11, 2: 12, 3: 13, 4: 14})
    assert e.okno.pokazana_plytka() == pierwsza and e.jest("widok_pracy")
    assert N.PLYTKA_NOWA in e.tekst_elementu(f"plytka_{druga}")
    e.klawisz(Qt.Key.Key_Escape)
    trzecia = atrapa.symuluj_skan("czysta", numer=3, projekty={1: 21, 2: 22, 3: 23, 4: 24})
    assert e.okno.pokazana_plytka() == trzecia  # bez otwartej pracy ekran idzie za nowa plytka
    e.klik(f"plytka_{druga}")
    assert N.PLYTKA_NOWA not in e.tekst_elementu(f"plytka_{druga}")


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
    assert e.jest("widok_pracy") and e.w("praca_tytul").text() == N.PRACA_TYTUL_POZA
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
    assert e.w("praca_tytul").text() == N.PRACA_TYTUL.format(gniazdo=2)
    # N: kolejne prace bez decyzji, ktore nie sa zielone (3, 4, 5, 6, 7, 9), potem od poczatku
    kolejne = []
    for _ in range(7):
        e.klawisz(Qt.Key.Key_N)
        kolejne.append(e.w("praca_tytul").text())
    assert kolejne == [N.PRACA_TYTUL.format(gniazdo=nr) for nr in (3, 4, 5, 6, 7, 9, 3)]
    e.klawisz(Qt.Key.Key_Escape)
    # nastepna zmiana tej samej doby: lista pokazuje plytki biezacej zmiany, wczesniejsze pod przyciskiem
    zegar.przesun(4 * 60)
    atrapa.przetworz()
    atrapa.wybierz_operatora("Technik A")
    trzecia = atrapa.symuluj_skan("czysta", numer=3, projekty={1: 21, 2: 22, 3: 23, 4: 24})
    assert atrapa.stan().zmiana == 3 and e.plytki() == [trzecia]
    assert e.w("przycisk_wczesniejsze").text() == N.WCZESNIEJSZE_POKAZ.format(n=2)
    e.klik("przycisk_wczesniejsze")
    assert e.plytki() == [pierwsza, druga, trzecia] and e.w("przycisk_wczesniejsze").text() == N.WCZESNIEJSZE_UKRYJ
    e.klik("przycisk_wczesniejsze")
    assert e.plytki() == [trzecia]
