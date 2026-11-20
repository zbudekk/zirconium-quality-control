"""ui (E3-A7): ekran poranny - tryb "Poranek" okna ``stanowisko.ui.utworz_okno`` sterowany z testu jak przez osobe
rozkladajaca piec (klikniecia, klawisze), tryb offscreen, dane sztuczne (pula poranna ``kontroler_api.indeks_rano_sztuczny``).

Kryteria paczki (plan etapu 3, 4.1, E3-A7; raport ``raporty/E3-A7_2026-11-18.md``):
  (1) 3 plytki jednego pieca -> podpisy (kuweta, zab, miniatura) i kolory zgodne z wynikiem w 100 % gniazd (U2) - atrapa
      i prawdziwy kontroler; prawda: tabela oczekiwan scenariusza i ``session_rano.stan_pieca`` (A6),
  (2) klik w zolte pokazuje dwoch kandydatow, wybor zapisuje decyzje (``decyzje``) i zmienia kolor,
  (3) trzy sposoby kolejnosci kuwet (U7): od najliczniejszej, wedlug numeru (= ``plan_plytek`` A6), numer wpisany recznie,
  (4) "Zamknij piec" pokazuje zlecenia kompletne i liste brakow rowna wynikowi A6 (``wynik_pieca``, ``braki``),
  (5) bez ramki i bez Excela program dziala dalej (komunikat, nie awaria),
  (6) zamiast przegladu z czlowiekiem: szesc zadan porannych T14 sterowaniem z testu i zrzuty PNG dla wlasciciela (G2) -
      zmienna ``E3_ZRZUTY`` = katalog zrzutow.
Dodatkowo: przelacznik trybu Wieczor / Poranek (pasek stanu, pamiec po restarcie), nieznana przypisana recznie, konflikt,
poprawka (Z9), uklad bez obciec przy 1920 x 1080 i 100 / 125 / 150 % (jak ``test_ui_rozdzielczosc``), przerwy petli okna
ponizej 200 ms przy 3 plytkach x 23 prace (prawdziwy kontroler), okno zmaksymalizowane, 0 sciezek i nazw plikow na ekranie.
"""
from __future__ import annotations

import datetime as dt
import gc
import os
import time
from pathlib import Path

import pytest

import test_kontroler_api as TK
import test_ui_wieczor as UW
from stanowisko import statusy as ST  # bez Qt (napisy ekranu - plik testow jest ASCII)
from stanowisko.ui import napisy_rano as NR

RANO_START = dt.datetime(2026, 11, 18, 6, 30, 0)  # sroda, zmiana 1
PELNY_EKRAN = (1920, 1001)  # 1920 x 1080 przy 100 %, okno zmaksymalizowane
ROZMIARY = (("100proc_ekran", 1920, 1080), ("100proc_zmaksymalizowane", 1920, 1001), ("125proc_ekran", 1536, 864),
            ("125proc_zmaksymalizowane", 1536, 784), ("150proc_ekran", 1280, 720), ("150proc_zmaksymalizowane", 1280, 642))
ROZMIARY_ZRZUTOW = (("100proc", 1920, 1080), ("125proc", 1536, 864))
KONFLIKT = ((5, 3), (6, 11))
POPRAWKA = (6, 2)
RODZAJ_NA_KLASE = {"pewna": "pewna", "zolta": "dwuznaczna", "dwuznaczna": "dwuznaczna", "nieznana": "nieznana", "brak": "nieznana"}


@pytest.fixture(scope="module", autouse=True)
def _qt():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    if UW.FONTY_WINDOWS.is_dir():
        os.environ.setdefault("QT_QPA_FONTDIR", str(UW.FONTY_WINDOWS))
    import PySide6.QtCore  # noqa: F401
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    assert app.platformName() == "offscreen"
    UW.czcionka_ekranu()
    yield app


class ZegarRano(UW.Zegar):
    def __init__(self):
        self.teraz = RANO_START


@pytest.fixture
def zegar():
    return ZegarRano()


@pytest.fixture
def atrapa(tmp_path, zegar):
    from stanowisko import kontroler_api as K

    k = K.AtrapaKontrolera(tmp_path / "atrapa", zegar=zegar)
    yield k
    k.zamknij()


class Ekran(UW.Ekran):
    """Okno na kontrolerze ``k`` w trybie porannym: mapy plytek pieca, klikniecia gniazd, klawisze ramki porannej."""

    def zamknij(self) -> None:
        """Okno zamkniete i USUNIETE teraz, w watku okna (``deleteLater`` + ``DeferredDelete``) - nie zostaje do zbierania przez GC
        w przypadkowym watku (recenzja PR #26, D7)."""
        from PySide6.QtCore import QCoreApplication, QEvent

        if getattr(self, "_usuniete", False):
            return
        self._usuniete = True
        super().zamknij()
        self.okno.deleteLater()
        self.lacznik.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)

    @property
    def rano(self):
        return self.okno.ekran_rano

    def po_ochronie_rano(self) -> None:
        self.czekaj(lambda: not self.rano.ochrona_aktywna(), 5.0, "koniec przygaszenia map porannych")

    def mapy(self) -> dict:
        self.zdarzenia()
        return self.rano.mapy()

    def klik_rano(self, skan_id: int, nr: int) -> None:
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest

        self.zdarzenia()
        self.po_ochronie_rano()
        mapa = self.mapy()[skan_id]
        QTest.mouseClick(mapa, Qt.MouseButton.LeftButton, pos=mapa.srodek_gniazda(nr).toPoint())
        self.odczekaj(5)

    def piksele(self, skan_id: int) -> dict:
        self.zdarzenia()
        self.po_ochronie_rano()
        mapa = self.mapy()[skan_id]
        obraz = mapa.grab().toImage()
        return {nr: obraz.pixelColor(mapa.punkt_probny(nr).toPoint()).name() for nr in mapa.numery()}

    def wpisz(self, tekst: str) -> None:
        from PySide6.QtTest import QTest

        QTest.keyClicks(self.okno, tekst)
        self.odczekaj(5)

    def tabela(self, nazwa: str) -> list:
        from stanowisko.ui.ekran_rano import teksty_tabeli

        self.zdarzenia()
        return teksty_tabeli(self.w(nazwa))

    def obraz(self):
        self.zdarzenia()
        if self.okno.rano():
            self.po_ochronie_rano()
        return self.okno.grab().toImage()


@pytest.fixture
def ekrany():
    otwarte = []

    def nowy(kontroler, rozmiar: tuple = PELNY_EKRAN) -> Ekran:
        e = Ekran(kontroler, rozmiar)
        otwarte.append(e)
        return e

    yield nowy
    for e in otwarte:
        e.zamknij()
    otwarte.clear()
    gc.collect()  # reszta obiektow Pythona tego testu sprzatana teraz, w watku okna (D7)


def zasoby_gui() -> tuple:
    """(obiekty USER, obiekty GDI) procesu testow - diagnostyka zawieszenia startu procesu silnika (D7); poza Windows ()."""
    if os.name != "nt":
        return ()
    import ctypes

    user32 = ctypes.WinDLL("user32")
    user32.GetGuiResources.argtypes = [ctypes.c_void_p, ctypes.c_uint32]  # E3-A2p: bez typow uchwyt -1 (ten proces) obcinany do 32 bitow = zawsze (0, 0)
    proces = ctypes.c_void_p(-1)
    return user32.GetGuiResources(proces, 1), user32.GetGuiResources(proces, 0)


def oczekiwane_gniazda() -> dict:
    """Tabela oczekiwan scenariusza porannego (piec 2): (numer plytki, gniazdo) -> (klasa pracy porannej, projekt w gniezdzie)."""
    from stanowisko import kontroler_api as K

    wynik = {}
    for numer, (gniazda, projekty) in K.plan_scenariusza_rano().items():
        for nr, rodzaj in gniazda.items():
            projekt = projekty[nr][0] if isinstance(projekty[nr], tuple) else projekty[nr]
            wynik[(numer, nr)] = (RODZAJ_NA_KLASE[rodzaj], projekt)
    for miejsce in KONFLIKT:
        wynik[miejsce] = ("konflikt", wynik[miejsce][1])
    wynik[POPRAWKA] = ("poprawka", wynik[POPRAWKA][1])
    return wynik


def kuweta_projektu() -> dict:
    from stanowisko import kontroler_api as K

    return {nr: k for k, numery in K.projekty_zlecen_rano().items() for nr in numery}


def sprawdz_plytke(e: Ekran, numer: int, skan_id: int, oczekiwane: dict) -> int:
    """Kolor (dane i piksel), kuweta, zab i miniatura w kazdym gniezdzie plytki = tabela oczekiwan; zwraca liczbe gniazd."""
    from stanowisko import kontroler_api as K
    from stanowisko import statusy as ST

    mapa = e.mapy()[skan_id]
    kolory, piksele, rysowane = mapa.kolory(), e.piksele(skan_id), mapa.rysowane()
    kuwety = kuweta_projektu()
    assert sorted(mapa.numery()) == list(range(1, 25))
    for nr in range(1, 25):
        narysowane = {k: rysowane[nr][k] for k in ("kuweta", "zab", "miniatura")}
        if (numer, nr) not in oczekiwane:  # gniazdo puste
            assert kolory[nr] == piksele[nr] == ST.STATUSY["pusty"].hex and narysowane == {"kuweta": None, "zab": None, "miniatura": None}
            continue
        klasa, projekt = oczekiwane[(numer, nr)]
        w = ST.status_rano(klasa)
        assert kolory[nr] == w.hex and piksele[nr] == w.hex, (numer, nr, klasa, kolory[nr], piksele[nr])
        if klasa in ("pewna", "poprawka", "konflikt"):
            assert narysowane == {"kuweta": kuwety[projekt], "zab": f"z. {K.zab_sztuczny(projekt)}", "miniatura": K.projekt_sztuczny(projekt)}, (numer, nr)
        else:
            assert narysowane == {"kuweta": w.napis, "zab": None, "miniatura": None}, (numer, nr, narysowane)
    return 24


# ----------------------------------------------------------------------------
# (1) podpisy i kolory w 100 % gniazd
# ----------------------------------------------------------------------------
def test_k1_trzy_plytki_pieca_podpisy_i_kolory_100_proc(atrapa, ekrany):
    from stanowisko import session_rano as SR

    skany = atrapa.scenariusz_poranny()
    e = ekrany(atrapa)
    assert e.okno.rano() and e.jest("ekran_rano")
    oczekiwane = oczekiwane_gniazda()
    prawda = SR.SesjaRano(atrapa.sesja).stan_pieca()  # wynik A6 na tej samej bazie
    assert {(s["numer_plytki"], p["gniazdo"]): p["klasa"] for s in prawda["skany"] for p in s["prace"]} == {k: v[0] for k, v in oczekiwane.items()}
    assert sorted(e.mapy()) == sorted(skany[n] for n in (4, 5, 6))
    gniazd = sum(sprawdz_plytke(e, n, skany[n], oczekiwane) for n in (4, 5, 6))
    assert gniazd == 72  # 3 plytki x 24 gniazda (23 prace + puste): 100 % zgodnych
    stan = atrapa.stan()
    assert stan.rano.plytka(skany[5]).gniazdo(3).praca.konflikt_z == ((6, 11),)
    print(f"\n[kryterium 1] 3 plytki, {gniazd} gniazd: kolor (dane i piksel), kuweta, zab i miniatura zgodne w {gniazd} z {gniazd}")


# ----------------------------------------------------------------------------
# (2) dwuznaczna: dwaj kandydaci, wybor = decyzja i zmiana koloru
# ----------------------------------------------------------------------------
def test_k2_klik_w_zolte_dwaj_kandydaci_wybor_zapisuje_decyzje_i_zmienia_kolor(atrapa, ekrany):
    from stanowisko import kontroler_api as K
    from stanowisko import statusy as ST

    skany = atrapa.scenariusz_poranny()
    e = ekrany(atrapa)
    s4 = skany[4]
    gniazda, projekty = K.plan_scenariusza_rano()[4]
    dobry, zly = projekty[9]
    assert e.mapy()[s4].kolory()[9] == ST.status_rano("dwuznaczna").hex
    e.klik_rano(s4, 9)
    assert e.jest("kandydat_1") and e.jest("kandydat_2") and not e.jest("kandydat_3")
    kuwety = kuweta_projektu()
    for i, projekt in ((1, dobry), (2, zly)):
        assert e.w(f"kandydat_{i}_kuweta").text() == f"Kuweta {kuwety[projekt]}"
        assert K.zab_sztuczny(projekt) in e.w(f"kandydat_{i}_zab").text()
        assert e.w(f"kandydat_{i}_miniatura").sha16 == K.projekt_sztuczny(projekt)  # miniatura kandydata ze stanu
        assert e.aktywny(f"kandydat_{i}_wybierz")
    praca_id = e.rano.pokazana_praca().praca_id
    e.klik("kandydat_1_wybierz")
    d = atrapa.sesja.baza.wiersz("SELECT * FROM decyzje WHERE praca_id = ? ORDER BY id DESC LIMIT 1", (praca_id,))
    assert (d["rodzaj"], d["wartosc"], d["operator"]) == ("wybor_kandydata", K.projekt_sztuczny(dobry), "Technik A")
    assert e.mapy()[s4].kolory()[9] == ST.status_rano("przypisana").hex == e.piksele(s4)[9]
    assert e.mapy()[s4].rysowane()[9]["kuweta"] == kuwety[dobry]
    assert e.jest("kandydat_1_wybrany") and e.jest("praca_rano_cofnij")
    e.klik("praca_rano_cofnij")  # pomylka: cofniecie wyboru - znow zolta
    assert e.mapy()[s4].kolory()[9] == ST.status_rano("dwuznaczna").hex
    assert atrapa.sesja.baza.wiersz("SELECT rodzaj FROM decyzje WHERE praca_id = ? ORDER BY id DESC LIMIT 1", (praca_id,))["rodzaj"] == "cofniecie"


def test_k2_bez_osoby_wybor_nieaktywny_z_wyjasnieniem(atrapa, ekrany):
    skany = atrapa.scenariusz_poranny()
    atrapa.wybierz_operatora(None)
    e = ekrany(atrapa)
    e.klik_rano(skany[4], 9)
    assert e.jest("kandydat_1_wybierz") and not e.aktywny("kandydat_1_wybierz") and e.jest("praca_rano_wyjasnienie")
    assert e.jest("panel_osoba")


# ----------------------------------------------------------------------------
# (3) trzy sposoby kolejnosci kuwet
# ----------------------------------------------------------------------------
def test_k3_trzy_sposoby_kolejnosci_kuwet(atrapa, ekrany):
    from stanowisko import session_rano as SR

    skany = atrapa.scenariusz_poranny()
    e = ekrany(atrapa)
    rano = SR.SesjaRano(atrapa.sesja)
    # (a) od najliczniejszej = plan ramki A6
    plan = rano.plan_plytek(kolejnosc="liczba")
    assert [w[0] for w in e.tabela("tabela_kuwet")] == [k["kuweta"] for k in plan["kuwety"]]
    assert [int(w[1]) for w in e.tabela("tabela_kuwet")] == [plan["liczba_prac"][k["kuweta"]] for k in plan["kuwety"]]
    pierwsza = plan["kuwety"][0]["kuweta"]
    assert e.w("rano_kuweta_biezaca").text() == f"Kuweta {pierwsza}"
    # (b) wedlug numeru
    e.klik("kolejnosc_numer")
    plan_n = rano.plan_plytek(kolejnosc="numer")
    assert [w[0] for w in e.tabela("tabela_kuwet")] == [k["kuweta"] for k in plan_n["kuwety"]]
    assert atrapa.stan().rano.kolejnosc == "numer" and e.w("kolejnosc_numer").isChecked()
    # (c) numer wpisany recznie (cyfry + Enter, jak na klawiaturze ramki): kuweta biezaca, jej gniazda obwiedzione
    cel = plan_n["kuwety"][len(plan_n["kuwety"]) // 2]["kuweta"]
    e.wpisz(cel[:-1])
    assert e.jest("rano_bufor") and cel[:-1] in e.w("rano_bufor").text()
    e.wpisz(cel[-1])
    from PySide6.QtCore import Qt

    e.klawisz(Qt.Key.Key_Return)
    assert atrapa.stan().rano.kuweta_biezaca == cel and e.w("rano_kuweta_biezaca").text() == f"Kuweta {cel}" and not e.jest("rano_bufor")
    obwiedzione = {(s, nr) for s, m in e.mapy().items() for nr in m.biezace()}
    kuweta = next(k for k in atrapa.stan().rano.kuwety if k.biezaca)
    assert obwiedzione == set(kuweta.gniazda) and len(obwiedzione) == kuweta.prac == plan_n["liczba_prac"][cel]  # P4: gniazda z kontrolera
    # numer spoza pieca: odmowa (komunikat), nic sie nie psuje
    e.wpisz("9999")
    e.klawisz(Qt.Key.Key_Return)
    assert atrapa.stan().rano.kuweta_biezaca == cel and "9999" in e.tekst()
    assert len(e.mapy()) == 3 and skany


def test_k3_rozkladanie_enter_i_cofniecie_backspace(atrapa, ekrany):
    """Kuweta po kuwecie wedlug ekranu: Enter = rozlozona (wpis w dzienniku, biezaca = nastepna), Backspace = cofnij pomylke."""
    from PySide6.QtCore import Qt

    atrapa.scenariusz_poranny()
    e = ekrany(atrapa)
    kolejne = [k.kuweta for k in atrapa.stan().rano.kuwety]
    e.klawisz(Qt.Key.Key_Return)
    e.klawisz(Qt.Key.Key_Return)
    rano = atrapa.stan().rano
    assert [k.kuweta for k in rano.kuwety if k.potwierdzona] == kolejne[:2] and rano.kuweta_biezaca == kolejne[2]
    assert e.tabela("tabela_kuwet")[0][3] == NR.KUWETA_STAN_ROZLOZONA
    e.klawisz(Qt.Key.Key_Backspace)
    rano = atrapa.stan().rano
    assert [k.kuweta for k in rano.kuwety if k.potwierdzona] == kolejne[:1] and rano.kuweta_biezaca == kolejne[1]
    wpisy = atrapa.sesja.baza.wiersze("SELECT typ FROM zdarzenia WHERE typ IN ('kuweta_potwierdzona', 'kuweta_cofnieta') ORDER BY id")
    assert [w["typ"] for w in wpisy] == ["kuweta_potwierdzona", "kuweta_potwierdzona", "kuweta_cofnieta"]
    e.klik("rano_potwierdz_kuwete")  # przycisk = Enter
    assert [k.kuweta for k in atrapa.stan().rano.kuwety if k.potwierdzona] == kolejne[:2]


# ----------------------------------------------------------------------------
# (4) "Zamknij piec": kompletne i braki = wynik A6
# ----------------------------------------------------------------------------
def zamknij_piec(e: Ekran, *, pytanie: bool) -> None:
    """Klikniecie "Zamknij piec". E3-P14 (N3): gdy piec ma prace bez rozstrzygniecia, przycisk nie zamyka - ekran pyta; test
    zamyka wtedy swiadomie odpowiedzia "Zamknij piec mimo to" (samo pytanie sprawdza ``test_p14_ekran``). Runda 2 (P4):
    ``pytanie`` - jawne oczekiwanie testu, czy ekran ma zapytac (falszywe pytanie albo jego brak = test pada)."""
    e.klik("przycisk_zamknij_piec")
    assert e.jest("pytanie_zamknij_mimo") == pytanie, f"pytanie przed zamknieciem pieca: jest {e.jest('pytanie_zamknij_mimo')}, oczekiwane {pytanie}"
    if pytanie:
        e.klik("zamknij_mimo_tak")


def rozstrzygnij_konflikt(e: Ekran, atrapa, skany: dict) -> None:
    e.klik_rano(skany[6], 11)
    assert e.jest("praca_rano_konflikt")
    e.klik("praca_rano_bez_projektu")


def test_k4_zamknij_piec_kompletne_i_braki_rowne_wynikowi_A6(atrapa, ekrany):
    from stanowisko import session_rano as SR

    skany = atrapa.scenariusz_poranny()
    e = ekrany(atrapa)
    assert e.jest("przycisk_zamknij_piec") and not e.aktywny("przycisk_zamknij_piec") and e.jest("rano_blokady")
    rozstrzygnij_konflikt(e, atrapa, skany)
    assert e.aktywny("przycisk_zamknij_piec") and not e.jest("rano_blokady")
    zamknij_piec(e, pytanie=True)
    rano = SR.SesjaRano(atrapa.sesja)
    piec = atrapa.stan().rano
    wynik = rano.wynik_pieca(piec.sesja_pieca_id)
    assert wynik is not None and not piec.otwarty and e.w("rano_strona_wynik").isChecked() and e.jest("tabela_kompletne")
    kompletne = e.tabela("tabela_kompletne")
    braki = e.tabela("tabela_braki")
    assert [w[0] for w in kompletne] == [z["kuweta"] for z in wynik["kompletne"]] and len(kompletne) > 5
    assert [w[1] for w in kompletne] == [f"{z['rozpoznane']} z {z['punktow']}" for z in wynik["kompletne"]]
    assert [(w[0], w[1]) for w in braki] == [(z["kuweta"], ", ".join(b["zeby"] for b in z["brakujace"])) for z in wynik["braki"]]
    assert len(braki) >= 3
    biezace = e.tabela("tabela_braki_biezace")
    assert [w[0] for w in biezace] == [z["kuweta"] for z in rano.braki()]
    poprawki = e.w("rano_poprawki").text()
    assert "3200" in poprawki and len(wynik["poprawki"]) == 1
    print(f"\n[kryterium 4] kompletne {len(kompletne)} = A6 {len(wynik['kompletne'])}; braki {len(braki)} = A6 {len(wynik['braki'])}; "
          f"lista brakow biezaca {len(biezace)} = A6 {len(rano.braki())}")


# ----------------------------------------------------------------------------
# (5) bez ramki i Excela: komunikat, nie awaria
# ----------------------------------------------------------------------------
def test_k5_bez_ramki_i_excela_komunikat_program_dziala_dalej(atrapa, ekrany):
    from stanowisko import statusy as ST

    skany = atrapa.scenariusz_poranny()
    e = ekrany(atrapa)
    assert e.jest("komunikat_ramka_niedostepna") and ST.KOMUNIKATY["ramka_niedostepna"].tytul in e.tekst()
    assert not atrapa.stan().rano.ramka and not atrapa.stan().rano.excel
    rozstrzygnij_konflikt(e, atrapa, skany)
    zamknij_piec(e, pytanie=True)
    assert e.jest("komunikat_excel_niedostepny")
    kompletne = atrapa.stan().rano.kompletne
    assert kompletne and all(z.kuweta in e.tekst_elementu("komunikat_excel_niedostepny") for z in kompletne)  # wlasna lista kuwet (P1)
    # program dziala dalej: nastepny skan otwiera nowy piec, ekran pokazuje plytke, komunikat ramki zostaje
    nowy = atrapa.symuluj_skan_rano(4, {1: "pewna", 2: "zolta"}, projekty={1: 380, 2: (381, 382)})
    e.czekaj(lambda: list(e.mapy()) == [nowy], 5.0, "plytka nowego pieca")
    rano = atrapa.stan().rano
    assert rano.otwarty and rano.nr_w_dniu == 3 and e.jest("komunikat_ramka_niedostepna") and e.w("rano_strona_rozkladanie").isChecked()
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QPushButton

    zamknij = e.w("komunikat_ramka_niedostepna").findChild(QPushButton, "zamknij_komunikat")  # komunikat ramki mozna zamknac
    QTest.mouseClick(zamknij, Qt.MouseButton.LeftButton)
    assert not e.jest("komunikat_ramka_niedostepna") and atrapa.przetworz() == 0 and atrapa.stan().rano.otwarty


# ----------------------------------------------------------------------------
# przypadki szczegolne: nieznana, konflikt, poprawka (Z9), plytka bez numeru, ponowny skan
# ----------------------------------------------------------------------------
def test_nieznana_przypisana_recznie_po_numerze_kuwety(atrapa, ekrany):
    from PySide6.QtTest import QTest

    from stanowisko import kontroler_api as K
    from stanowisko import statusy as ST

    skany = atrapa.scenariusz_poranny()
    e = ekrany(atrapa)
    gniazda, projekty = K.plan_scenariusza_rano()[6]
    projekt = projekty[20]
    kuweta = kuweta_projektu()[projekt]
    assert e.mapy()[skany[6]].kolory()[20] == ST.STATUSY["nieznana_rano"].hex
    e.klik_rano(skany[6], 20)
    e.klik("praca_rano_przypisz")
    from PySide6.QtCore import Qt

    pole = e.w("praca_rano_przypisz_kuweta")
    pole.setFocus()
    QTest.keyClicks(pole, kuweta)
    QTest.keyClick(pole, Qt.Key.Key_Return)  # D2: Enter w polu = "Pokaz projekty", nie "kuweta rozlozona"
    e.odczekaj(5)
    pid = atrapa.sesja.baza.wiersz("SELECT id FROM projekty WHERE sha16 = ?", (K.projekt_sztuczny(projekt),))["id"]
    assert e.jest(f"projekt_{pid}") and e.w(f"projekt_{pid}_miniatura").sha16 == K.projekt_sztuczny(projekt)
    assert atrapa.stan().rano.kuweta_biezaca is not None and not e.rano.bufor()  # cyfry w polu nie ida do numeru kuwety
    assert atrapa.sesja.baza.wiersz("SELECT count(*) AS n FROM zdarzenia WHERE typ = 'kuweta_potwierdzona'")["n"] == 0
    assert e.okno.focusWidget() is e.w("praca_rano_przypisz_kuweta")  # fokus w nowym polu (poprawka numeru)
    e.klik("praca_rano_przypisz_pokaz")
    e.klik(f"projekt_{pid}")
    praca = atrapa.stan().rano.plytka(skany[6]).gniazdo(20).praca
    assert (praca.klasa, praca.decyzja, praca.projekt_id, praca.kuweta) == ("przypisana", "przypisanie_reczne", pid, kuweta)
    assert e.mapy()[skany[6]].kolory()[20] == ST.status_rano("przypisana").hex == e.piksele(skany[6])[20]


def test_konflikt_blokuje_zamkniecie_poprawka_bursztyn_z9(atrapa, ekrany):
    from stanowisko import statusy as ST

    skany = atrapa.scenariusz_poranny()
    e = ekrany(atrapa)
    blokady = e.w("rano_blokady").text()
    assert "konflikt" in blokady.lower() and not e.aktywny("przycisk_zamknij_piec")
    e.klik_rano(skany[5], 3)
    assert NR.KONFLIKT_MIEJSCE.format(plytka=NR.PLYTKA_NR.format(numer=6), gniazdo=11) in e.w("praca_rano_konflikt").text()
    # Z9: zab dofrezowany do zlecenia juz odhaczonego - bursztyn i napis inny niz "poprawiana recznie"
    kolor = e.mapy()[skany[6]].kolory()[2]
    assert kolor == ST.STATUSY["dofrezowany"].hex == e.piksele(skany[6])[2] and kolor != ST.STATUSY["pomaranczowy"].hex
    e.klik_rano(skany[6], 2)
    assert e.w("praca_rano_status").text() == ST.STATUSY["dofrezowany"].napis != ST.STATUSY["pomaranczowy"].napis
    assert e.jest("praca_rano_poprawka") and e.w("praca_rano_poprawka").text() == NR.POPRAWKA_INFO  # zlecenie 3200 odhaczone w piecu 1
    legenda = e.tekst_elementu("rano_legenda")
    assert ST.STATUSY["dofrezowany"].napis in legenda and ST.STATUSY["nieznana_rano"].napis in legenda


def test_plytka_bez_numeru_ponowny_skan_i_plytka_wieczorna_rano(atrapa, ekrany, zegar):
    from stanowisko import kontroler_api as K

    atrapa.przelacz_tryb("rano")
    atrapa.wybierz_operatora("Technik A")
    K.indeks_rano_sztuczny(atrapa.sesja.baza, atrapa.sesja.teraz())
    e = ekrany(atrapa)
    bez = atrapa.symuluj_skan_rano(None, {1: "pewna", 2: "pewna"}, projekty={1: 305, 2: 306})
    e.czekaj(lambda: e.jest("pytanie_brak_numeru_plytki"), 5.0, "pytanie o numer plytki")
    assert not e.aktywny("przycisk_zamknij_piec") and "numer" in e.w("rano_blokady").text().lower()
    e.klik("odp_podaj_numer_plytki_5")
    assert atrapa.stan().rano.plytka(bez).numer == 5 and e.aktywny("przycisk_zamknij_piec")
    zegar.przesun(2)
    drugi = atrapa.symuluj_skan_rano(5, {1: "pewna", 2: "pewna"}, projekty={1: 305, 2: 306})
    e.czekaj(lambda: e.jest("pytanie_ponowny_skan"), 5.0, "pytanie o ponowny skan")
    assert len(e.mapy()) == 2
    e.klik("odp_potwierdz_ponowny_skan")
    assert list(e.mapy()) == [drugi] and e.jest("rano_nieaktywne")
    wieczorna = atrapa.symuluj_skan("nie_z_trybu", numer=1, gniazda={1: "zielony"})
    e.czekaj(lambda: e.jest("pytanie_plytka_nie_z_trybu"), 5.0, "pytanie o plytke nie z trybu")
    assert atrapa.stan().rano.plytka(wieczorna).status == "plytka_nie_z_trybu" and not e.aktywny("przycisk_zamknij_piec")
    assert e.jest("odp_pomin_skan") and not e.jest("odp_dopusc_plytke")  # rano plytki nie z trybu sie nie dopuszcza (A6 runda 2)
    e.klik("odp_pomin_skan")
    assert atrapa.stan().rano.plytka(wieczorna).pominieta and e.aktywny("przycisk_zamknij_piec")
    assert ST.NAPIS_POMINIETEJ in e.w(f"rano_plytka_{wieczorna}_tytul").text() and e.jest(f"rano_plytka_{wieczorna}_cofnij_pominiecie")
    e.klik(f"rano_plytka_{wieczorna}_cofnij_pominiecie")
    assert not atrapa.stan().rano.plytka(wieczorna).pominieta and not e.aktywny("przycisk_zamknij_piec")


def test_a6r2_reczne_zamkniecie_braku_ponowne_otwarcie_pieca_i_zamkniecie_w_trakcie_analizy(atrapa, ekrany):
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    from stanowisko import statusy as ST

    skany = atrapa.scenariusz_poranny()
    e = ekrany(atrapa)
    rozstrzygnij_konflikt(e, atrapa, skany)
    atrapa.symuluj_postep(udzial=0.4)  # skan w analizie: "Zamknij piec" niedostepne (A6 runda 2, D11)
    e.zdarzenia()
    assert not e.aktywny("przycisk_zamknij_piec") and ST.tekst_komunikatu("analiza_trwa")[2] in e.w("rano_blokady").text()
    atrapa.symuluj_postep(udzial=None)
    e.zdarzenia()
    assert e.aktywny("przycisk_zamknij_piec")
    zamknij_piec(e, pytanie=True)
    assert e.jest("przycisk_otworz_piec") and not e.jest("przycisk_zamknij_piec")
    biezace = atrapa.stan().rano.braki_biezace
    t = e.w("tabela_braki_biezace")
    QTest.mouseClick(t.viewport(), Qt.MouseButton.LeftButton, pos=t.visualItemRect(t.item(0, 0)).center())
    e.odczekaj(5)
    punkt = biezace[0].brakujace[0]
    assert e.jest("rano_brak_reczny_tytul") and biezace[0].kuweta in e.w("rano_brak_reczny_tytul").text()
    e.klik(f"brak_{punkt.projekt_id}_zaginiona")
    assert len(atrapa.stan().rano.braki_biezace) == len(biezace) - (len(biezace[0].brakujace) == 1) and e.jest(f"brak_cofnij_{punkt.projekt_id}")
    d = atrapa.sesja.baza.wiersz("SELECT rodzaj, wartosc FROM decyzje WHERE rodzaj = 'zamkniecie_reczne'")
    assert '"powod": "zaginiona"' in d["wartosc"]
    e.klik(f"brak_cofnij_{punkt.projekt_id}")
    assert len(atrapa.stan().rano.braki_biezace) == len(biezace) and not e.jest(f"brak_cofnij_{punkt.projekt_id}")
    e.klik("przycisk_otworz_piec")  # pomylka przy zamykaniu: piec otwarty ponownie
    assert atrapa.stan().rano.otwarty and e.jest("przycisk_zamknij_piec") and not e.jest("przycisk_otworz_piec")


# ----------------------------------------------------------------------------
# przelacznik trybu
# ----------------------------------------------------------------------------
def test_przelacznik_trybu_wieczor_poranek_i_pamiec_po_restarcie(tmp_path, zegar, ekrany):
    from stanowisko import kontroler_api as K
    from stanowisko import statusy as ST

    katalog = tmp_path / "stanowisko"
    a = K.AtrapaKontrolera(katalog, zegar=zegar)
    try:
        e = ekrany(a)
        assert a.stan().tryb == "wieczor" and not e.okno.rano() and e.w("przycisk_przelacz_tryb").text() == NR.PRZELACZ_NA.format(tryb=ST.NAZWY_TRYBOW["rano"])
        e.klik("przycisk_przelacz_tryb")  # bez wybranej osoby tez dziala
        assert a.stan().tryb == "rano" and e.okno.rano() and e.w("napis_tryb").text() == ST.NAZWY_TRYBOW["rano"]
        assert e.w("przycisk_przelacz_tryb").text() == NR.PRZELACZ_NA.format(tryb=ST.NAZWY_TRYBOW["wieczor"]) and e.jest("rano_bez_plytek")
        a.wybierz_operatora("Technik A")
        rano = a.symuluj_skan_rano(4, {1: "pewna"}, projekty={1: 305})
        assert a.stan().rano.plytka(rano) is not None and a.stan().plytka(rano) is None  # skan poranny poza stanem wieczoru
        e.klik("przycisk_przelacz_tryb")
        assert a.stan().tryb == "wieczor" and not e.okno.rano() and e.jest("lista_plytek") and a.stan().rano is None
        wieczorny = a.symuluj_skan("czysta", numer=1)
        assert a.stan().plytka(wieczorny) is not None
        e.klik("przycisk_przelacz_tryb")
        e.zamknij()
    finally:
        a.zamknij()
    b = K.AtrapaKontrolera(katalog, zegar=zegar)  # restart programu na tej samej bazie: tryb ostatnio wybrany
    try:
        assert b.stan().tryb == "rano" and b.stan().rano.plytka(rano) is not None
        wpisy = b.sesja.baza.wiersze("SELECT dane FROM zdarzenia WHERE typ = 'tryb_zmieniony' ORDER BY id")
        assert len(wpisy) == 3
    finally:
        b.zamknij()


def test_okno_zmaksymalizowane_w_trybie_rano(atrapa, monkeypatch):
    from PySide6.QtCore import Qt

    from stanowisko import kontroler_api as K
    from stanowisko import ui
    from stanowisko.ui import okno

    atrapa.scenariusz_poranny()
    monkeypatch.setattr(okno, "okno_zmaksymalizowane", lambda platforma, dostepne=None: True)
    lacznik = K.lacznik_qt(atrapa)
    w = ui.utworz_okno(atrapa, lacznik)
    try:
        assert w.windowState() & Qt.WindowState.WindowMaximized and w.rano()
    finally:
        w.close()
        lacznik.zatrzymaj()


# ----------------------------------------------------------------------------
# uklad bez obciec: laptop 1920 x 1080 przy 100 / 125 / 150 %
# ----------------------------------------------------------------------------
SCENY = ("piec_z_kolorami", "dwuznaczna_kandydaci", "nieznana_przypisana", "konflikt", "zamknij_piec_wynik", "poprawka_bursztyn",
         "ostatni_zamkniety_piec")


def zbuduj_scene(atrapa, ekrany, scena: str, rozmiar: tuple) -> Ekran:
    from stanowisko import kontroler_api as K

    skany = atrapa.scenariusz_poranny()
    e = ekrany(atrapa, rozmiar)
    if scena == "dwuznaczna_kandydaci":
        e.klik_rano(skany[4], 9)
    elif scena == "nieznana_przypisana":
        projekt = K.plan_scenariusza_rano()[6][1][20]
        pid = atrapa.sesja.baza.wiersz("SELECT id FROM projekty WHERE sha16 = ?", (K.projekt_sztuczny(projekt),))["id"]
        atrapa.przypisz_recznie(atrapa.stan().rano.plytka(skany[6]).gniazdo(20).praca.praca_id, pid)
        e.klik_rano(skany[6], 20)
    elif scena == "konflikt":
        e.klik_rano(skany[5], 3)
    elif scena == "zamknij_piec_wynik":
        atrapa.przypisz_recznie(atrapa.stan().rano.plytka(skany[6]).gniazdo(11).praca.praca_id, None)
        zamknij_piec(e, pytanie=True)
    elif scena == "poprawka_bursztyn":
        e.klik_rano(skany[6], 2)
    elif scena == "ostatni_zamkniety_piec":  # P1: piec zamkniety, skan nastepnego pieca, lista do Excela w zakladce
        atrapa.przypisz_recznie(atrapa.stan().rano.plytka(skany[6]).gniazdo(11).praca.praca_id, None)
        zamknij_piec(e, pytanie=True)
        atrapa.symuluj_skan_rano(4, {1: "pewna", 2: "zolta", 3: "pewna"}, projekty={1: 380, 2: (381, 382), 3: 383})
        e.zdarzenia()
        e.klik("rano_strona_ostatni")
    e.zdarzenia()
    return e


def usterki_rano(e: Ekran, rozmiar: tuple) -> list:
    """``test_ui_wieczor.sprawdz_uklad`` + kontrolki poza oknem, pasek przewijania poziomego, mapy i "Zamknij piec" w calosci."""
    from PySide6.QtWidgets import QAbstractScrollArea, QWidget

    usterki = UW.sprawdz_uklad(e, rozmiar)
    okno = e.okno
    ramka = okno.rect().adjusted(-1, -1, 1, 1)
    for w in okno.findChildren(QWidget):
        if w.isVisibleTo(okno) and not UW._w_obszarze_przewijanym(okno, w) and not ramka.contains(UW._w_oknie(okno, w)):
            usterki.append(f"kontrolka poza oknem: {w.objectName() or type(w).__name__} {UW._w_oknie(okno, w)}")
    for obszar in okno.findChildren(QAbstractScrollArea):
        if obszar.isVisibleTo(okno) and obszar.horizontalScrollBar().isVisibleTo(okno):
            usterki.append(f"pasek przewijania poziomego: {obszar.objectName() or type(obszar).__name__}")
    for skan_id, mapa in e.mapy().items():
        if UW._widoczny_wycinek(okno, mapa) != UW._w_oknie(okno, mapa):
            usterki.append(f"mapa {skan_id} przycieta")
        if mapa.height() < mapa.minimumHeight() or mapa.width() < mapa.minimumWidth():
            usterki.append(f"mapa {skan_id} mniejsza niz minimum")
    for nazwa in ("przycisk_zamknij_piec", "rano_potwierdz_kuwete", "przycisk_przelacz_tryb", "kandydat_1_wybierz", "kandydat_2_wybierz",
                  "rano_strona_ostatni"):
        w = okno.findChild(QWidget, nazwa)
        if w is not None and w.isVisibleTo(okno) and not UW._w_obszarze_przewijanym(okno, w) and UW._widoczny_wycinek(okno, w) != UW._w_oknie(okno, w):
            usterki.append(f"przyciety {nazwa}")
    return usterki


@pytest.mark.parametrize("scena", SCENY)
def test_uklad_poranny_1920x1080_przy_100_125_150_proc_bez_obciec(atrapa, ekrany, scena):
    """Kazda scena z zrzutow przy kazdym rozmiarze z ``ROZMIARY`` (i z powrotem): zero usterek ukladu; przy 1920 x 1080 /
    1001 uklad zwykly, ponizej progu - zwarty. Z ``E3_ZRZUTY``: zrzuty PNG dla wlasciciela (1920 x 1080 i 1536 x 864)."""
    from PySide6.QtGui import QGuiApplication

    from stanowisko.ui import styl

    e = zbuduj_scene(atrapa, ekrany, scena, PELNY_EKRAN)
    dpr = QGuiApplication.primaryScreen().devicePixelRatio()
    zrzuty = Path(os.environ["E3_ZRZUTY"]) if os.environ.get("E3_ZRZUTY") else None
    wyniki = []
    for nazwa, szer, wys in ROZMIARY + tuple(reversed(ROZMIARY[:-1])):
        usterki = usterki_rano(e, (szer, wys))
        assert e.okno.rano()
        assert e.okno.zwarty() == (szer < styl.PROG_ZWARTEGO[0] or wys < styl.PROG_ZWARTEGO[1])
        promien = min((m._ksztalt(nr)[2] for m in e.mapy().values() for nr in m.numery() if nr != 1), default=0)
        wyniki.append(f"{nazwa} {szer}x{wys}: usterek {len(usterki)}, promien gniazda {promien:.0f} px")
        assert not usterki, f"{scena} {nazwa} {szer}x{wys} (dpr {dpr}):\n" + "\n".join(usterki)
    if zrzuty is not None:
        zrzuty.mkdir(parents=True, exist_ok=True)
        for nazwa, szer, wys in ROZMIARY_ZRZUTOW:
            e.okno.resize(szer, wys)
            for _ in range(3):
                e.zdarzenia()
                e.odczekaj(20)
            e.obraz().save(str(zrzuty / f"rano_{scena}_{nazwa}_{szer}x{wys}_dpr{dpr:g}.png"))
    print(f"\n[uklad poranny {scena}, dpr {dpr:g}]\n  " + "\n  ".join(wyniki))


def test_przy_100_proc_w_gniezdzie_kuweta_zab_i_miniatura(atrapa, ekrany):
    """Przy 1920 x 1001 (100 %) kazde gniazdo okragle z praca rozpoznana ma narysowana kuwete, zab i miniature; przy 150 %
    (1280 x 642) - co najmniej kuwete."""
    skany = atrapa.scenariusz_poranny()
    e = ekrany(atrapa)
    for rozmiar, wymagane in ((PELNY_EKRAN, ("kuweta", "zab", "miniatura")), ((1280, 642), ("kuweta",))):
        UW.sprawdz_uklad(e, rozmiar)
        for numer in (4, 5, 6):
            mapa = e.mapy()[skany[numer]]
            plytka = atrapa.stan().rano.plytka(skany[numer])
            for g in plytka.gniazda:
                if g.praca is not None and g.praca.klasa in ("pewna", "poprawka", "konflikt"):
                    assert all(mapa.rysowane()[g.nr][k] for k in wymagane), (rozmiar, numer, g.nr, mapa.rysowane()[g.nr])


# ----------------------------------------------------------------------------
# czas: odswiezenie ekranu i petla okna przy 3 plytkach x 23 prace
# ----------------------------------------------------------------------------
def test_odswiezenie_ekranu_rano_3_plytki_x_23_prace(atrapa, ekrany):
    from PySide6.QtCore import Qt

    skany = atrapa.scenariusz_poranny()
    e = ekrany(atrapa)
    czasy = []
    prawdziwe = e.okno.pokaz_stan

    def mierzone(stan):
        t0 = time.perf_counter()
        prawdziwe(stan)
        czasy.append(time.perf_counter() - t0)

    e.okno.pokaz_stan = mierzone
    for _ in range(3):
        e.klik_rano(skany[4], 9)
        e.klik("kandydat_1_wybierz")
        e.klik("praca_rano_cofnij")
        e.klawisz(Qt.Key.Key_Return)
        e.klawisz(Qt.Key.Key_Backspace)
    for i in range(50):
        atrapa.symuluj_postep(udzial=(i % 100) / 100)
    e.odczekaj(30)
    print(f"\n[rano, atrapa] odswiezen ekranu {len(czasy)}, najdluzsze {max(czasy) * 1000:.1f} ms")
    assert len(czasy) >= 10 and max(czasy) <= UW.PROG_PRZERWY_S / 2


# ----------------------------------------------------------------------------
# dane osobowe i (6) szesc zadan porannych T14
# ----------------------------------------------------------------------------
def test_zero_sciezek_i_nazw_plikow_na_ekranie_porannym(atrapa, ekrany):
    skany = atrapa.scenariusz_poranny()
    e = ekrany(atrapa)
    for numer in (4, 5, 6):
        for nr in (1, 2, 3, 9, 11, 14, 20, 22):
            e.klik_rano(skany[numer], nr)
            UW.bez_sciezek(e, zakazane=("Fikcja",))
    e.klik_rano(skany[6], 20)
    e.klik("praca_rano_przypisz")
    e.rano.widok.szukaj("3256")
    UW.bez_sciezek(e, zakazane=("Fikcja", "crown_cad"))
    e.klik("rano_strona_wynik")
    assert UW.bez_sciezek(e, zakazane=("Fikcja", "crown_cad")) > 50


def test_t14_szesc_zadan_porannych(atrapa, ekrany, zegar):
    """T14 (czesc poranna) sterowaniem z testu - test czyta tylko ekran: (1) zeskanuj 2 plytki pieca, (2) rozstrzygnij dwuznaczna,
    (3) rozloz jedna kuwete wedlug ekranu, (4) cofnij pomylke, (5) znajdz kuwete po numerze, (6) zamknij piec i odczytaj braki."""
    from PySide6.QtCore import Qt

    from stanowisko import kontroler_api as K
    from stanowisko import statusy as ST

    atrapa.wybierz_operatora("Technik B")
    e = ekrany(atrapa)
    e.klik("przycisk_przelacz_tryb")
    K.indeks_rano_sztuczny(atrapa.sesja.baza, atrapa.sesja.teraz())
    # (1) dwie plytki pieca
    p4 = atrapa.symuluj_skan_rano(4, {1: "pewna", 2: "pewna", 3: "zolta", 4: "pewna", 5: "pewna"},
                                  projekty={1: 307, 2: 308, 3: (309, 320), 4: 311, 5: 312})
    zegar.przesun(1)
    p5 = atrapa.symuluj_skan_rano(5, {1: "pewna", 2: "pewna", 3: "pewna"}, projekty={1: 310, 2: 313, 3: 314})
    e.czekaj(lambda: sorted(e.mapy()) == sorted([p4, p5]), 5.0, "dwie plytki na ekranie")
    zadania = ["skan 2 plytek"]
    # (2) dwuznaczna: zolte gniazdo -> kandydat 1
    zolte = [nr for nr, kolor in e.mapy()[p4].kolory().items() if kolor == ST.status_rano("dwuznaczna").hex]
    assert zolte == [3]
    e.klik_rano(p4, 3)
    e.klik("kandydat_1_wybierz")
    assert e.mapy()[p4].kolory()[3] == ST.status_rano("przypisana").hex
    zadania.append("dwuznaczna")
    # (3) jedna kuweta wedlug ekranu: biezaca kuweta i jej gniazda, Enter
    biezaca = e.w("rano_kuweta_biezaca").text().split()[-1]
    obwiedzione = [nr for m in e.mapy().values() for nr in m.biezace()]
    assert obwiedzione and all(e.mapy()[s].rysowane()[nr]["kuweta"] == biezaca for s in e.mapy() for nr in e.mapy()[s].biezace())
    e.klawisz(Qt.Key.Key_Return)
    assert e.tabela("tabela_kuwet")[[w[0] for w in e.tabela("tabela_kuwet")].index(biezaca)][3] == NR.KUWETA_STAN_ROZLOZONA
    zadania.append("kuweta wedlug ekranu")
    # (4) pomylka: druga kuweta potwierdzona za wczesnie -> Backspace
    druga = e.w("rano_kuweta_biezaca").text().split()[-1]
    e.klawisz(Qt.Key.Key_Return)
    e.klawisz(Qt.Key.Key_Backspace)
    assert e.w("rano_kuweta_biezaca").text().split()[-1] == druga
    zadania.append("cofniecie pomylki")
    # (5) kuweta po numerze
    e.wpisz("3221")
    e.klawisz(Qt.Key.Key_Return)
    assert e.w("rano_kuweta_biezaca").text() == "Kuweta 3221"
    zadania.append("kuweta po numerze")
    # (6) zamknij piec i odczytaj braki
    zamknij_piec(e, pytanie=False)
    braki = {w[0]: w[1] for w in e.tabela("tabela_braki")}
    kompletne = [w[0] for w in e.tabela("tabela_kompletne")]
    # zlecenia: 3221 = projekty 307-310 (4 z 4 w piecu), 3228 = 311-312, 3235 = 313, 3242 = 314-316 (w piecu tylko 314)
    assert kompletne == ["3221", "3228", "3235"] and braki == {"3242": f"{K.zab_sztuczny(315)}, {K.zab_sztuczny(316)}"}
    zadania.append("zamknij piec i braki")
    assert len(zadania) == 6
    print(f"\n[T14 rano] {len(zadania)} z 6 zadan: {', '.join(zadania)}")


# ----------------------------------------------------------------------------
# runda 2 (recenzja PR #26 runda 1: B1, P1-P5, D2, D7) i A6 runda 4 (nowy wsad)
# ----------------------------------------------------------------------------
def poranek(atrapa) -> None:
    from stanowisko import kontroler_api as K

    atrapa.przelacz_tryb("rano")
    atrapa.wybierz_operatora("Technik A")
    K.indeks_rano_sztuczny(atrapa.sesja.baza, atrapa.sesja.teraz())


def test_r2_b1_enter_niesie_kuwete_pokazana_odmowa_gdy_w_kontrolerze_inna(atrapa, ekrany):
    """B1: Enter wysyla kuwete widoczna na ekranie; gdy kontroler ma juz inna biezaca (stan nie doszedl do okna), odmowa bez wpisu
    w dzienniku, a ekran pokazuje nowa biezaca - dopiero drugi Enter ja potwierdza."""
    from PySide6.QtCore import Qt

    atrapa.scenariusz_poranny()
    e = ekrany(atrapa)
    pokazana = atrapa.stan().rano.kuweta_biezaca
    inna = next(k.kuweta for k in atrapa.stan().rano.kuwety if k.kuweta != pokazana)
    e.lacznik.blockSignals(True)  # nowy stan "w drodze": okno pokazuje jeszcze stara kuwete
    try:
        assert atrapa.wybierz_kuwete(inna)
    finally:
        e.lacznik.blockSignals(False)
    assert e.w("rano_kuweta_biezaca").text() == f"Kuweta {pokazana}"
    e.klawisz(Qt.Key.Key_Return)
    wpisy = lambda: [w["dane"] for w in atrapa.sesja.baza.wiersze("SELECT dane FROM zdarzenia WHERE typ = 'kuweta_potwierdzona'")]  # noqa: E731
    assert wpisy() == [] and e.w("rano_kuweta_biezaca").text() == f"Kuweta {inna}" and inna in e.tekst()
    e.klawisz(Qt.Key.Key_Return)
    assert len(wpisy()) == 1 and inna in wpisy()[0]
    e.klawisz(Qt.Key.Key_Backspace)  # D3: panel mowi, co cofnieto
    assert NR.KUWETA_COFNIETA.format(kuweta=inna) in e.tekst() and atrapa.stan().rano.kuweta_biezaca == inna


def test_r2_p1_zakladka_ostatni_zamkniety_piec_po_skanie_nastepnego(atrapa, ekrany):
    from stanowisko import session_rano as SR

    skany = atrapa.scenariusz_poranny()
    e = ekrany(atrapa)
    rozstrzygnij_konflikt(e, atrapa, skany)
    zamknij_piec(e, pytanie=True)
    piec = atrapa.stan().rano.sesja_pieca_id
    assert e.w("rano_strona_wynik").isChecked() and not e.jest("rano_strona_ostatni")  # zamkniety piec jest jeszcze glownym widokiem
    nowy = atrapa.symuluj_skan_rano(4, {1: "pewna"}, projekty={1: 380})
    e.czekaj(lambda: list(e.mapy()) == [nowy], 5.0, "plytka nowego pieca")
    assert e.jest("rano_strona_ostatni") and e.w("rano_strona_rozkladanie").isChecked()
    e.klik("rano_strona_ostatni")
    wynik = SR.SesjaRano(atrapa.sesja).wynik_pieca(piec)
    assert e.w("rano_strona_ostatni").isChecked() and e.jest("ostatni_tabela_kompletne")
    assert [w[0] for w in e.tabela("ostatni_tabela_kompletne")] == [z["kuweta"] for z in wynik["kompletne"]] and wynik["kompletne"]
    assert [w[0] for w in e.tabela("ostatni_tabela_braki")] == [z["kuweta"] for z in wynik["braki"]]
    assert not e.jest("ostatni_tabela_braki_biezace") and str(wynik["nr_w_dniu"]) in e.w("ostatni_rano_wynik_tytul").text()
    assert all(z["kuweta"] in e.tekst_elementu("komunikat_excel_niedostepny") for z in wynik["kompletne"])


def historia_zlecen(plik_bazy, zlecen: int = 20_000, czas: str = "2026-06-01T08:00:00") -> None:
    """Duza historia (inne polaczenie z baza - jak import indeksu albo drugi program): ``zlecen`` zlecen po 3 punkty, wszystkie
    rozpoznane w dawnym piecu. Lista brakow ich nie pokazuje, ale ``session_rano.braki()`` czyta je wszystkie. Dane sztuczne."""
    import sqlite3

    pol = sqlite3.connect(plik_bazy)
    try:
        z0 = (pol.execute("SELECT max(id) FROM zlecenia").fetchone()[0] or 0) + 1
        p0 = (pol.execute("SELECT max(id) FROM projekty").fetchone()[0] or 0) + 1
        piec = pol.execute("INSERT INTO sesje_pieca (data, nr_w_dniu, otwarto, zamknieto, zamknal) VALUES (?, 1, ?, ?, ?)",
                           (czas[:10], czas, czas, "Technik A")).lastrowid
        pol.executemany("INSERT INTO zlecenia (id, zrodlo, folder, folder_norm, kuweta, dodano, usuniety) VALUES (?, 'cyrkon', ?, ?, ?, ?, 0)",
                        [(z0 + i, f"H{i} Historia", f"h{i} historia", str(100000 + i), czas) for i in range(zlecen)])
        pol.executemany("INSERT INTO projekty (id, zlecenie_id, plik, sha16, zeby, typ, usuniety) VALUES (?, ?, ?, ?, '11', 'korona', 0)",
                        [(p0 + 3 * i + j, z0 + i, f"h{i}-{j}.stl", f"{i:010d}{j:06d}") for i in range(zlecen) for j in range(3)])
        pol.executemany("INSERT INTO stan_punktow (projekt_id, stan, praca_id, sesja_pieca_id, czas) VALUES (?, 'rozpoznany', NULL, ?, ?)",
                        [(p0 + k, piec, czas) for k in range(3 * zlecen)])
        pol.commit()
    finally:
        pol.close()


def test_r2_p2_petla_okna_z_historia_20_tys_zlecen(atrapa, ekrany):
    """P2: baza z historia 20 tys. zlecen (60 tys. punktow). Lista brakow liczona raz (po zapisie z zewnatrz), potem z pamieci:
    klikniecia, wybor kandydata, Enter, Backspace, numer kuwety, cofniecie i nowy skan - najdluzsza przerwa petli okna < 200 ms."""
    from PySide6.QtCore import QEventLoop, Qt, QTimer
    from PySide6.QtTest import QTest

    skany = atrapa.scenariusz_poranny()
    historia_zlecen(atrapa.sesja.baza.plik)
    wywolania = []
    prawdziwe = atrapa.rano.braki

    def braki():
        t0 = time.perf_counter()
        wynik = prawdziwe()
        wywolania.append(time.perf_counter() - t0)
        return wynik

    atrapa.rano.braki = braki
    assert atrapa.przelacz_tryb("rano") and len(wywolania) == 1  # pierwszy stan po zapisie historii z zewnatrz: lista od nowa (raz)
    e = ekrany(atrapa)
    mapa = e.mapy()[skany[4]]

    def klik_gniazda():
        QTest.mouseClick(mapa, Qt.MouseButton.LeftButton, pos=mapa.srodek_gniazda(9).toPoint())

    akcje = [klik_gniazda, lambda: QTest.mouseClick(e.w("kandydat_1_wybierz"), Qt.MouseButton.LeftButton),
             lambda: QTest.keyClick(e.okno, Qt.Key.Key_Return), lambda: QTest.keyClick(e.okno, Qt.Key.Key_Backspace),
             lambda: QTest.keyClicks(e.okno, "3235"), lambda: QTest.keyClick(e.okno, Qt.Key.Key_Return),
             lambda: QTest.mouseClick(e.w("praca_rano_cofnij"), Qt.MouseButton.LeftButton),
             lambda: atrapa.symuluj_skan_rano(None, {1: "pewna", 2: "pewna"}, projekty={1: 383, 2: 384})]
    pomiar = {"ostatni": None, "przerwa": 0.0, "i": 0, "czasy": []}
    petla = QEventLoop()

    def tyk():
        teraz = time.perf_counter()
        if pomiar["ostatni"] is not None:
            pomiar["przerwa"] = max(pomiar["przerwa"], teraz - pomiar["ostatni"])
        pomiar["ostatni"] = teraz
        if pomiar["i"] >= len(akcje):
            petla.quit()
            return
        t0 = time.perf_counter()
        akcje[pomiar["i"]]()
        pomiar["czasy"].append(time.perf_counter() - t0)
        pomiar["i"] += 1

    zegar = QTimer()
    zegar.setInterval(20)
    zegar.timeout.connect(tyk)
    limit = QTimer()
    limit.setSingleShot(True)
    limit.timeout.connect(petla.quit)
    e.po_ochronie_rano()
    zegar.start()
    limit.start(30_000)
    petla.exec()
    zegar.stop()
    rano = atrapa.stan().rano
    print(f"\n[rano, historia 20 tys. zlecen] lista brakow od nowa: {wywolania[0] * 1000:.0f} ms (raz); akcje "
          f"{', '.join(f'{c * 1000:.0f}' for c in pomiar['czasy'])} ms; najdluzsza przerwa petli {pomiar['przerwa'] * 1000:.0f} ms")
    assert pomiar["i"] == len(akcje) and len(wywolania) == 1  # zadna akcja nie liczyla listy brakow od nowa
    assert rano.kuweta_biezaca == "3235" and len(rano.plytki) == 4
    assert pomiar["przerwa"] <= UW.PROG_PRZERWY_S and max(pomiar["czasy"]) <= UW.PROG_PRZERWY_S


def test_r2_p3_zamknij_piec_niedostepne_w_trakcie_skanowania(atrapa, ekrany, zegar):
    from PySide6.QtCore import Qt

    from stanowisko import kontroler_api as K

    skany = atrapa.scenariusz_poranny()
    e = ekrany(atrapa)
    rozstrzygnij_konflikt(e, atrapa, skany)
    assert e.aktywny("przycisk_zamknij_piec")
    e.klawisz(Qt.Key.Key_Space)  # start skanu: do pliku skanu "Zamknij piec" niedostepne (blokada w kontrolerze)
    assert len(atrapa.starty_skanu) == 1 and not e.aktywny("przycisk_zamknij_piec")
    assert ST.tekst_komunikatu("skanowanie_trwa")[2] in e.w("rano_blokady").text()
    zegar.przesun(K.LIMIT_SKANOWANIA_S / 60 + 1)  # skan przerwany: po limicie czasu blokada znika sama (zegar okna -> przetworz)
    e.czekaj(lambda: e.aktywny("przycisk_zamknij_piec"), 5.0, "koniec blokady skanowania")
    assert ST.tekst_komunikatu("skanowanie_trwa")[2] not in e.tekst()


def test_r2_p4_obwodka_tylko_gniazd_z_listy_kuwet(atrapa, ekrany, zegar):
    poranek(atrapa)
    s4 = atrapa.symuluj_skan_rano(4, {1: "pewna", 2: "pewna"}, projekty={1: 307, 2: 308})
    zegar.przesun(1)
    bez = atrapa.symuluj_skan_rano(None, {1: "pewna", 2: "pewna"}, projekty={1: 309, 2: 310})  # ta sama kuweta na plytce bez numeru
    e = ekrany(atrapa)
    rano = atrapa.stan().rano
    assert rano.kuweta_biezaca == "3221" and [(k.kuweta, k.prac) for k in rano.kuwety] == [("3221", 2)]
    assert sorted(e.mapy()[s4].biezace()) == [1, 2] and e.mapy()[bez].biezace() == []  # obwodka = lista kuwet (P4)
    assert e.w("rano_kuweta_opis").text().count("2") >= 1


def test_r2_p5_napisy_poprawki_wg_zlecenie_odhaczone(atrapa, ekrany, zegar):
    """P5 / Z9: zab juz rozpoznany przy zleceniu z brakami - napis "zab juz rozpoznany"; zab do zlecenia odhaczonego - "zlecenie
    juz odhaczone"; na stronie wyniku dwie osobne listy."""
    poranek(atrapa)
    atrapa.symuluj_skan_rano(4, {1: "pewna", 2: "pewna"}, projekty={1: 307, 2: 313})  # 3221 (4 punkty) i 3235 (1 punkt)
    assert atrapa.zamknij_piec()
    zegar.przesun(5)
    s = atrapa.symuluj_skan_rano(5, {1: "pewna", 2: "pewna"}, projekty={1: 307, 2: 313})
    e = ekrany(atrapa)
    e.klik_rano(s, 1)
    assert e.w("praca_rano_status").text() == ST.status("rano_juz_rozpoznany").napis
    assert e.w("praca_rano_poprawka").text() == NR.JUZ_ROZPOZNANY_INFO != NR.POPRAWKA_INFO
    e.klik_rano(s, 2)
    assert e.w("praca_rano_status").text() == ST.STATUSY["dofrezowany"].napis and e.w("praca_rano_poprawka").text() == NR.POPRAWKA_INFO
    e.klik("rano_strona_wynik")
    assert "3235" in e.w("rano_poprawki").text() and "3221" not in e.w("rano_poprawki").text()
    assert "3221" in e.w("rano_juz_rozpoznane").text() and "3235" not in e.w("rano_juz_rozpoznane").text()


def test_r2_a6r4_nowy_wsad_pytanie_w_oknie_numer_mimo_i_przeniesienie(atrapa, ekrany, zegar):
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QPushButton

    poranek(atrapa)
    atrapa.symuluj_skan_rano(4, {1: "pewna", 2: "pewna"}, projekty={1: 307, 2: 308})
    zegar.przesun(30)
    e = ekrany(atrapa)
    s2 = atrapa.symuluj_skan_rano(4, {1: "pewna", 2: "pewna"}, projekty={1: 313, 2: 314})  # nastepny wsad, piec niezamkniety
    e.czekaj(lambda: e.jest("pytanie_nowy_wsad"), 5.0, "pytanie o nowy wsad")
    assert not e.aktywny("przycisk_zamknij_piec") and "nowy wsad" in e.w("rano_blokady").text()
    e.klik(f"rano_plytka_{s2}_podaj_numer_plytki")  # zmiana numeru drugiego skanu: tylko po jawnym potwierdzeniu
    e.klik("odp_podaj_numer_plytki_5")
    assert e.jest("pytanie_numer_nowy_wsad") and atrapa.stan().rano.plytka(s2).numer == 4 and not e.jest("panel_numer_plytki")
    nie = e.w("pytanie_numer_nowy_wsad").findChild(QPushButton, "odp_zamknij_pytanie")
    QTest.mouseClick(nie, Qt.MouseButton.LeftButton)  # "Nie zmieniaj"
    e.odczekaj(5)
    assert not e.jest("pytanie_numer_nowy_wsad") and atrapa.stan().rano.plytka(s2).numer == 4
    e.klik("odp_zamknij_piec_i_przenies")  # "Tak, zamknij piec i przenies nowe skany"
    rano = atrapa.stan().rano
    assert rano.otwarty and [p.skan_id for p in rano.plytki] == [s2] and rano.ostatni_zamkniety is not None
    e.czekaj(lambda: list(e.mapy()) == [s2], 5.0, "nowy piec na ekranie")
    assert e.jest("rano_strona_ostatni") and not e.jest("pytanie_nowy_wsad") and e.aktywny("przycisk_zamknij_piec")
    e.klik("przycisk_cofnij_przeniesienie")  # A6 runda 5: pomylka - skany wracaja do poprzedniego pieca
    e.czekaj(lambda: len(e.mapy()) == 2, 5.0, "poprzedni piec z powrotem")
    assert e.jest("pytanie_nowy_wsad") and not e.jest("przycisk_cofnij_przeniesienie")


# ----------------------------------------------------------------------------
# prawdziwy kontroler NA KONCU modulu (D7, E3-A2p): start procesu silnika po ok. 30 testach z oknami
# ----------------------------------------------------------------------------
def test_k1_prawdziwy_kontroler_trzy_plytki_przez_skaner_i_petla_okna(tmp_path, ekrany, caplog):
    """Prawdziwa ``Aplikacja``: tryb "Poranek" przyciskiem na pasku, trzy pliki skanow (3 x 23 prace) do folderu skanera, analiza
    sztuczna w procesie silnika, wynik do sesji pieca (A6). (1) mapa = tabela oczekiwan w 100 % gniazd; potem osoba klika zolte
    gniazda, wybiera kandydata i potwierdza kuwete (Enter). Przez caly czas (analizy i klikniecia) zegar co 10 ms mierzy
    najdluzsza przerwe petli okna - prog 200 ms. Celowo NA KONCU modulu (D7; E3-A2p): tu, po ok. 30 testach z oknami, start
    procesu silnika zawisal na PC w 9 z 22 przebiegow w ``multiprocessing.popen_spawn_win32``. Przyczyna (raport E3-A2p): proces
    testow tracil mozliwosc podlaczania nowych procesow do swojej konsoli - potomek ginal przy starcie z 0xC0000142, zanim
    przeczytal dane startowe, a ``Process.start()`` czekal bez konca. Od E3-A2p proces roboczy ma wlasna konsole
    (``CREATE_NO_WINDOW``), a start ma limit czasu i ponowienia (``silnik.md``). Diagnostyka zostaje: liczba przerwanych prob
    i stan potomka z logu silnika (``[D7]``), a przy niepowodzeniu - zrzut watkow, kod wyjscia potomka, zasoby USER / GDI."""
    import logging
    import threading

    from PySide6.QtCore import QEventLoop, Qt, QTimer
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QWidget

    from stanowisko import kontroler_api as K
    from stanowisko import session_rano as SR

    caplog.set_level(logging.WARNING, logger="stanowisko.silnik")

    def proby_startu() -> list:  # wpisy silnika o przerwanych probach uruchomienia procesu (E3-A2p) - stan potomka do raportu
        return [r.getMessage() for r in caplog.records if r.name == "stanowisko.silnik" and "uruchomienia" in r.getMessage()]

    gc.collect()
    zbierania_poza = []

    def obserwuj_gc(faza, info):  # diagnostyka D7: zbieranie cykli w innym watku niz watek okna
        if faza == "stop" and threading.current_thread() is not threading.main_thread() and info.get("collected"):
            zbierania_poza.append((threading.current_thread().name, info["generation"], info["collected"]))

    gc.callbacks.append(obserwuj_gc)
    zasoby_na_poczatku = zasoby_gui()
    st = TK.StanowiskoAplikacji(tmp_path)
    try:
        st.teraz = RANO_START
        K.indeks_rano_sztuczny(st.k.sesja.baza, st.k.sesja.teraz())
        st.k.wybierz_operatora("Technik A")
        e = ekrany(st.k)
        e.klik("przycisk_przelacz_tryb")
        assert st.k.stan().tryb == "rano" and e.okno.rano()
        czasy_ekranu = []
        prawdziwe = e.okno.pokaz_stan

        def mierzone(stan):
            t0 = time.perf_counter()
            prawdziwe(stan)
            czasy_ekranu.append(time.perf_counter() - t0)

        e.okno.pokaz_stan = mierzone
        plan = K.plan_scenariusza_rano()
        pomiar = {"ostatni": time.perf_counter(), "przerwa": 0.0, "tykniec": 0, "zrobione": set(), "w_kroku": False, "klikaj": False}
        zolte = {4: 9, 5: 14}
        petla = QEventLoop()

        def tyk():
            teraz = time.perf_counter()
            pomiar["przerwa"] = max(pomiar["przerwa"], teraz - pomiar["ostatni"])
            pomiar["ostatni"] = teraz
            pomiar["tykniec"] += 1
            if pomiar["w_kroku"]:
                return
            rano = st.k.stan().rano
            if not pomiar["klikaj"]:
                if rano is not None and len(rano.plytki) == 3 and len(e.rano.mapy()) == 3:
                    petla.quit()  # faza 1: wszystkie plytki policzone i na ekranie
                return
            mapy = e.rano.mapy()
            for p in rano.plytki:
                nr = zolte.get(p.numer)
                if nr is not None and p.numer not in pomiar["zrobione"] and p.skan_id in mapy and not e.rano.ochrona_aktywna():
                    pomiar["w_kroku"] = True
                    mapa = mapy[p.skan_id]
                    QTest.mouseClick(mapa, Qt.MouseButton.LeftButton, pos=mapa.srodek_gniazda(nr).toPoint())
                    b = e.okno.findChild(QWidget, "kandydat_1_wybierz")
                    if b is not None and b.isEnabled():
                        QTest.mouseClick(b, Qt.MouseButton.LeftButton)
                        QTest.keyClick(e.okno, Qt.Key.Key_Return)
                        pomiar["zrobione"].add(p.numer)
                    pomiar["w_kroku"] = False
                    break
            if pomiar["zrobione"] == {4, 5}:
                petla.quit()

        zegar = QTimer()
        zegar.setInterval(10)
        zegar.timeout.connect(tyk)
        limit = QTimer()
        limit.setSingleShot(True)
        limit.timeout.connect(petla.quit)
        for numer, (gniazda, projekty) in plan.items():
            st.zapisz(st.opis_rano(numer, gniazda, projekty, spij=0.8))
        zegar.start()
        limit.start(120_000)
        t0 = time.perf_counter()
        petla.exec()
        czas_analiz = time.perf_counter() - t0
        zegar.stop()  # zegar 10 ms zalewa kolejke Windows - zwykle zegary okna (przygaszenie map 800 ms) czekalyby w nieskonczonosc
        rano = st.k.stan().rano
        if rano is None or len(rano.plytki) != 3:  # diagnostyka zawieszenia startu procesu silnika (D7): watki i zbieranie GC poza watkiem okna
            import faulthandler
            import sys

            faulthandler.dump_traceback(file=sys.stderr, all_threads=True)
            print(f"GC poza watkiem okna: {zbierania_poza}", file=sys.stderr)
            import subprocess

            for opis, flagi in (("w konsoli procesu testow", 0), ("z wlasna konsola (CREATE_NO_WINDOW)", 0x08000000))[: 2 if os.name == "nt" else 0]:  # E3-A2p
                try:
                    kod = subprocess.run([sys.executable, "-c", "pass"], creationflags=flagi, timeout=60).returncode & 0xFFFFFFFF
                    print(f"proces potomny {opis}: kod wyjscia 0x{kod:08X} (0xC0000142 = blad inicjalizacji DLL przy starcie)", file=sys.stderr)
                except subprocess.TimeoutExpired:  # runda 2, D8: potomek stoi - reszta diagnostyki i wlasciwy assert zostaja
                    print(f"proces potomny {opis}: stoi dluzej niz 60 s (zabity)", file=sys.stderr)
            print(f"obiekty USER / GDI okna: {zasoby_gui()} (na poczatku testu {zasoby_na_poczatku})", file=sys.stderr)
            from multiprocessing import popen_spawn_win32
            import _winapi

            for obiekt in gc.get_objects():  # proces potomny tworzony w zawieszonym ``Process.start()``: kod wyjscia (0xC0000142 = DLL init)
                if isinstance(obiekt, popen_spawn_win32.Popen) and getattr(obiekt, "_handle", None) is not None:
                    try:
                        kod = _winapi.GetExitCodeProcess(int(obiekt._handle))
                    except OSError as blad:
                        kod = f"blad {blad}"
                    print(f"proces potomny pid {obiekt.pid}: kod wyjscia {kod if isinstance(kod, str) else hex(kod & 0xFFFFFFFF)} "
                          f"(0x103 = dziala)", file=sys.stderr)
            print("proby uruchomienia procesu silnika:", *proby_startu(), sep="\n", file=sys.stderr)
        assert rano.otwarty and [p.numer for p in rano.plytki] == [4, 5, 6] and all(len(p.prace) == 23 for p in rano.plytki), (
            st.k.stan().kolejka, st.k.silnik.stan() if st.k.silnik is not None else None)
        skany = {p.numer: p.skan_id for p in rano.plytki}
        oczekiwane = {k: v for k, v in oczekiwane_gniazda().items() if k != POPRAWKA}  # bez pieca 1: projekt 301 to zwykla praca
        oczekiwane[POPRAWKA] = ("pewna", 301)
        prawda = SR.SesjaRano(st.k.sesja).stan_pieca()
        assert {(s["numer_plytki"], p["gniazdo"]): p["klasa"] for s in prawda["skany"] for p in s["prace"]} == {k: v[0] for k, v in oczekiwane.items()}
        assert sum(sprawdz_plytke(e, n, skany[n], oczekiwane) for n in (4, 5, 6)) == 72
        assert st.k.sesja.baza.wiersz("SELECT count(*) AS n FROM skany WHERE tryb = 'rano' AND sesja_pieca_id IS NOT NULL")["n"] == 3
        # faza 2: osoba rozstrzyga zolte i potwierdza kuwete - nadal pomiar petli okna
        e.po_ochronie_rano()
        pomiar["klikaj"], pomiar["ostatni"] = True, time.perf_counter()
        zegar.start()
        limit.start(60_000)
        petla.exec()
        zegar.stop()
        print(f"\n[rano, petla okna, prawdziwy kontroler] 3 plytki x 23 prace policzone w {czas_analiz:.1f} s; najdluzsza przerwa "
              f"{pomiar['przerwa'] * 1000:.0f} ms (prog {UW.PROG_PRZERWY_S * 1000:.0f} ms); odswiezen ekranu {len(czasy_ekranu)}, najdluzsze "
              f"{max(czasy_ekranu) * 1000:.1f} ms; tykniec {pomiar['tykniec']}")
        rano = st.k.stan().rano
        assert pomiar["zrobione"] == {4, 5} and sum(1 for p in rano.plytki for x in p.prace if x.decyzja == "wybor_kandydata") == 2
        assert sum(1 for k in rano.kuwety if k.potwierdzona) == 2
        assert pomiar["tykniec"] >= 100 and pomiar["przerwa"] <= UW.PROG_PRZERWY_S
        assert max(czasy_ekranu) <= UW.PROG_PRZERWY_S / 2
        print(f"[D7] zbierania GC poza watkiem okna w tescie: {zbierania_poza}; obiekty USER / GDI: {zasoby_na_poczatku} -> {zasoby_gui()}")
        print(f"[D7] przerwane proby uruchomienia procesu silnika (E3-A2p): {st.k.silnik.stan().get('nieudane_uruchomienia')}; "
              f"starty procesu {st.k.silnik.stan()['starty_procesu']}")
        for wpis in proby_startu():
            print(f"[D7] {wpis}")
    finally:
        gc.callbacks.remove(obserwuj_gc)
        st.koniec()
