"""ui (E3-U1b): tryb "Poranek" w nowym ukladzie okna (``etap3/nowy_interfejs/SPEC.md`` p. 3-5, makieta ``Rano.dc.html``) - bez ekranu.

Uzupelnia ``test_ui_rano.py`` (funkcje trybu porannego: kolory i podpisy gniazd, kandydaci, kolejnosc kuwet, "Zamknij piec",
kompletne i braki, sceny przy 6 rozmiarach okna) o to, co wnosi nowy uklad:
* szkielet poranka wg ``motyw`` przy 6 rozmiarach okna (kolumny, stale wysokosci strefy pytan, zakladek i wiersza "Teraz
  rozkladasz", kolejnosc czesci);
* mapy plytek pieca NIE PRZESUWAJA SIE przy zmianach stanu (jak ``test_ap1_*`` wieczorem);
* S3-16: lista kuwet wybiera po numerze kuwety (nie po indeksie wiersza), kolejnosc zmieniona w tle = 800 ms bez klikniec;
  "Wszystkie kuwety rozlozone - mozesz zamknac piec" tylko bez blokad; "Przypisanie: program (dopasowanie pewne)" nie przy konflikcie;
* ochrona 800 ms: strefa pytan zmieniona w tle (S3-3 rano), mapy po wejsciu w tryb poranny i po zmianie zestawu plytek;
* kazdy skrot poranka (cyfry, "#", Enter, Backspace, Esc, Spacja, przytrzymany klawisz) i pytanie przed "Zamknij piec";
* zakladka "Excel" (sama sie pokazuje, "Pozniej" wraca), pole Excela na pasku stanu, bledy programu na liscie okna.
Dane wylacznie sztuczne (``AtrapaKontrolera``), Qt ``offscreen``.
"""
from __future__ import annotations

import os

import pytest

import test_ui_rano as TR
import test_ui_wieczor as UW
from stanowisko.ui import napisy_rano as NR

ROZMIARY = tuple((szer, wys) for _, szer, wys in TR.ROZMIARY)  # 1920 x 1080 / 1001, 1536 x 864 / 784, 1280 x 720 / 642
ROZMIARY_MAP = ((1920, 1080), (1536, 864), (1280, 720), (1240, 640))


@pytest.fixture(scope="module", autouse=True)
def _qt():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    if UW.FONTY_WINDOWS.is_dir():
        os.environ.setdefault("QT_QPA_FONTDIR", str(UW.FONTY_WINDOWS))
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    UW.czcionka_ekranu()
    yield app


@pytest.fixture
def zegar():
    return TR.ZegarRano()


@pytest.fixture
def atrapa(tmp_path, zegar):
    from stanowisko import kontroler_api as K

    k = K.AtrapaKontrolera(tmp_path / "atrapa", zegar=zegar)
    yield k
    k.zamknij()


@pytest.fixture
def ekrany():
    otwarte = []

    def nowy(kontroler, rozmiar: tuple = TR.PELNY_EKRAN) -> TR.Ekran:
        e = TR.Ekran(kontroler, rozmiar)
        otwarte.append(e)
        return e

    yield nowy
    for e in otwarte:
        e.zamknij()


def maly_piec(atrapa) -> int:
    """Poranek z jedna plytka bez blokad: plytka 4, zlecenia 3200 (3 z 3) i 3207 (1 z 1)."""
    from stanowisko import kontroler_api as K

    atrapa.przelacz_tryb("rano")
    atrapa.wybierz_operatora("Technik A")
    K.indeks_rano_sztuczny(atrapa.sesja.baza, atrapa.sesja.teraz())
    return atrapa.symuluj_skan_rano(4, {1: "pewna", 2: "pewna", 3: "pewna", 5: "pewna"}, projekty={1: 301, 2: 302, 3: 303, 5: 304})


def klik_wiersza(t, wiersz: int) -> None:
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    QTest.mouseClick(t.viewport(), Qt.MouseButton.LeftButton, pos=t.visualItemRect(t.item(wiersz, 0)).center())


def klawisz_przytrzymany(okno, klawisz, tekst: str = "") -> None:
    """Zdarzenie klawisza z autopowtarzania (klawisz przytrzymany) - QTest go nie wysyla."""
    from PySide6.QtCore import QEvent, Qt
    from PySide6.QtGui import QKeyEvent
    from PySide6.QtWidgets import QApplication

    QApplication.sendEvent(okno, QKeyEvent(QEvent.Type.KeyPress, klawisz, Qt.KeyboardModifier.NoModifier, tekst, True))


# ----------------------------------------------------------------------------
# szkielet i rozmiary
# ----------------------------------------------------------------------------
@pytest.mark.parametrize("rozmiar", ROZMIARY)
def test_szkielet_poranka_wg_motywu_przy_6_rozmiarach(atrapa, ekrany, rozmiar):
    """SPEC p. 3: lewa kolumna "Piec n" (280 / 240 px), kolumna "Praca" (340 / 320 px), strefa pytan, pasek zakladek i wiersz
    "Teraz rozkladasz" o stalych wysokosciach z ``motyw``; od lewej piec, srodek, praca; od gory pasek gorny, strefa, zakladki,
    wiersz kuwety, mapy, pasek stanu. Zero usterek ukladu (``test_ui_wieczor.sprawdz_uklad``) - takze przy oknie otwartym od razu
    w tym rozmiarze i po zmianie z innego."""
    from stanowisko.ui import motyw

    skany = atrapa.scenariusz_poranny()
    e = ekrany(atrapa, rozmiar)
    for proba in (rozmiar, (1600, 900), rozmiar):
        assert not UW.sprawdz_uklad(e, proba), proba
    u = motyw.uklad_dla(*rozmiar)
    assert e.okno.uklad() is u and e.okno.rano()
    assert (e.w("rano_piec").width(), e.w("rano_prawa_kolumna").width()) == (u.lewa, u.prawa_rano)
    assert (u.lewa, u.prawa_rano) == ((240, 320) if u.zwarty else (280, 340))
    assert e.w("rano_strefa_komunikatow").height() == u.strefa and e.w("rano_zakladki").height() == u.zakladki
    assert e.w("rano_kuweta_wiersz").height() == u.kuweta
    x = [UW._w_oknie(e.okno, e.w(n)).x() for n in ("rano_piec", "rano_srodek", "rano_prawa_kolumna")]
    y = [UW._w_oknie(e.okno, e.w(n)).y() for n in ("pasek_gorny", "rano_strefa_komunikatow", "rano_zakladki", "rano_kuweta_wiersz", "rano_plytki",
                                                   "pasek_stanu")]
    assert x == sorted(x) and y == sorted(y), (rozmiar, x, y)
    mapy = e.mapy()
    assert sorted(mapy) == sorted(skany[n] for n in (4, 5, 6))
    for mapa in mapy.values():
        assert mapa.isVisibleTo(e.okno) and UW._widoczny_wycinek(e.okno, mapa) == UW._w_oknie(e.okno, mapa)
        assert mapa.width() >= u.mapa_rano_min[0] and mapa.height() >= u.mapa_rano_min[1]
    for nazwa in ("przycisk_zamknij_piec", "rano_potwierdz_kuwete", "rano_cofnij_kuwete", "przycisk_tryb_wieczor", "rano_strona_wynik"):
        w = e.w(nazwa)
        assert UW._widoczny_wycinek(e.okno, w) == UW._w_oknie(e.okno, w), nazwa
    for nazwa in ("przycisk_zamknij_piec", "rano_potwierdz_kuwete", "rano_cofnij_kuwete"):  # przyciski akcji (przelacznik trybu: 34 px, makieta)
        assert e.w(nazwa).height() >= motyw.CEL_KLIKNIECIA, nazwa


@pytest.mark.parametrize("rozmiar", ROZMIARY_MAP)
def test_mapy_rano_nie_przesuwaja_sie_przy_zmianach_stanu(atrapa, ekrany, rozmiar):
    """Jak ``test_ap1_pasek_stalej_wysokosci_i_prawa_kolumna_w_miejscu`` wieczorem: mapy wszystkich plytek pieca maja to samo polozenie
    i rozmiar po kazdej zmianie stanu w trybie rano - komunikat w tle, analiza (blokada "Zamknij piec"), kuweta rozlozona, wpisywany
    numer kuwety, otwarta praca i wybor kandydata, pytanie przed "Zamknij piec" i odpowiedz, kolejnosc kuwet, blad zapisu (lista
    bledow), skaner niedostepny, osoba wylogowana (lista osob)."""
    from PySide6.QtCore import Qt

    skany = atrapa.scenariusz_poranny()
    e = ekrany(atrapa, rozmiar)
    e.po_ochronie_rano()
    poczatek = e.rano.miejsca_map()
    assert len(poczatek) == 3
    zmiany = (
        ("komunikat w tle", lambda: atrapa.symuluj_komunikat("plik_zajety")),
        ("analiza - blokada zamkniecia pieca", lambda: atrapa.symuluj_postep(udzial=0.4)),
        ("koniec analizy", lambda: atrapa.symuluj_postep(udzial=None)),
        ("kuweta rozlozona (Enter)", lambda: e.klawisz(Qt.Key.Key_Return)),
        ("cyfry numeru kuwety", lambda: e.wpisz("32")),
        ("numer wyczyszczony (Esc)", lambda: e.klawisz(Qt.Key.Key_Escape)),
        ("kolejnosc wedlug numeru", lambda: e.klik("kolejnosc_numer")),
        ("otwarta praca dwuznaczna", lambda: e.klik_rano(skany[4], 9)),
        ("wybor kandydata", lambda: e.klik("kandydat_1_wybierz")),
        ("praca zamknieta (Esc)", lambda: e.klawisz(Qt.Key.Key_Escape)),
        ("konflikt rozstrzygniety (Bez projektu)", lambda: TR.rozstrzygnij_konflikt(e, atrapa, skany)),
        ("pytanie przed Zamknij piec", lambda: e.klik("przycisk_zamknij_piec")),
        ("Wroc do rozstrzygania", lambda: e.klik("zamknij_mimo_wroc")),
        ("blad zapisu - lista bledow", lambda: atrapa.symuluj_blad_zapisu(1)),
        ("skaner niedostepny", lambda: atrapa.symuluj_skaner(dostepny=False)),
        ("osoba wylogowana - lista osob", lambda: atrapa.wybierz_operatora(None)),
    )
    for opis, zmiana in zmiany:
        zmiana()
        e.zdarzenia()
        e.odczekaj(40)
        assert e.rano.miejsca_map() == poczatek, f"{rozmiar}: mapy przesunely sie po zmianie: {opis}"
    assert e.jest("lista_bledow") and e.jest("panel_osoba") and e.rano.pokazana_praca() is not None


# ----------------------------------------------------------------------------
# S3-16
# ----------------------------------------------------------------------------
def test_s3_16_lista_kuwet_wybiera_po_numerze_a_kolejnosc_zmieniona_w_tle_wstrzymuje_klikniecia(atrapa, ekrany):
    """S3-16: kazdy wiersz listy kuwet niesie numer swojej kuwety; klikniecie wysyla ``wybierz_kuwete`` z numerem zapisanym w KLIKNIETYM
    wierszu. Kolejnosc zmieniona w tle (np. druga osoba / ramka) przestawia wiersze pod kursorem - klikniecie w ciagu ``OCHRONA_MS``
    jest pomijane; zmiana kolejnosci przez osobe (przycisk) nie wlacza ochrony."""
    from stanowisko.ui import ekran_rano

    k = UW.Szpieg(atrapa)
    atrapa.scenariusz_poranny()
    e = ekrany(k)
    t = e.w("tabela_kuwet")
    panel = e.rano.kuwety
    assert [panel.kuweta_w_wierszu(i) for i in range(t.rowCount())] == [t.item(i, 0).text() for i in range(t.rowCount())]
    przed = [t.item(i, 0).text() for i in range(t.rowCount())]
    atrapa.ustaw_kolejnosc("numer")  # w tle - nie z okna
    e.zdarzenia()
    e.odczekaj(30)
    po = [t.item(i, 0).text() for i in range(t.rowCount())]
    wiersz = next(i for i, (a, b) in enumerate(zip(przed, po)) if a != b)  # wiersz, pod ktorym stoi teraz inna kuweta
    assert panel.ochrona_aktywna() and ekran_rano.OCHRONA_MS == 800
    klik_wiersza(t, wiersz)
    assert k.wyslane("wybierz_kuwete") == []  # klikniecie wycelowane w poprzednia kuwete - pominiete
    e.czekaj(lambda: not panel.ochrona_aktywna(), 5.0, "koniec ochrony listy kuwet")
    klik_wiersza(t, wiersz)
    assert k.wyslane("wybierz_kuwete") == [("wybierz_kuwete", (po[wiersz],))] and atrapa.stan().rano.kuweta_biezaca == po[wiersz]
    e.klik("kolejnosc_liczba")  # zmiana przez osobe: bez ochrony
    assert not panel.ochrona_aktywna()
    t = e.w("tabela_kuwet")
    klik_wiersza(t, 0)
    assert k.wyslane("wybierz_kuwete")[-1] == ("wybierz_kuwete", (t.item(0, 0).text(),))


def test_s3_16_wszystkie_kuwety_rozlozone_mozesz_zamknac_piec_tylko_bez_blokad(atrapa, ekrany):
    """S3-16: po rozlozeniu wszystkich kuwet napis "Wszystkie kuwety rozlozone - mozesz zamknac piec" pokazuje sie tylko, gdy nic
    nie trzyma pieca; przy blokadzie (np. trwa analiza skanu) - napis z tym, na co czeka zamkniecie, i "Zamknij piec" nieaktywne."""
    from PySide6.QtCore import Qt

    maly_piec(atrapa)
    e = ekrany(atrapa)
    for _ in range(20):
        if atrapa.stan().rano.kuweta_biezaca is None:
            break
        e.klawisz(Qt.Key.Key_Return)
    rano = atrapa.stan().rano
    assert rano.kuweta_biezaca is None and all(x.potwierdzona for x in rano.kuwety) and not rano.blokady
    assert e.w("rano_kuweta_opis").text() == NR.KUWETA_BRAK and e.aktywny("przycisk_zamknij_piec")
    atrapa.symuluj_postep(udzial=0.4)
    e.zdarzenia()
    blokady = atrapa.stan().rano.blokady
    assert blokady
    assert e.w("rano_kuweta_opis").text() == NR.KUWETA_BRAK_BLOKADY.format(lista="; ".join(blokady))
    assert NR.KUWETA_BRAK not in e.tekst() and not e.aktywny("przycisk_zamknij_piec") and e.jest("rano_blokady")
    atrapa.symuluj_postep(udzial=None)
    e.zdarzenia()
    assert e.w("rano_kuweta_opis").text() == NR.KUWETA_BRAK


def test_s3_16_przypisanie_programu_nie_przy_konflikcie(atrapa, ekrany):
    """S3-16: "Przypisanie: program (dopasowanie pewne)" przy pracy przypisanej przez program bez konfliktu; przy konflikcie (ten sam
    projekt w dwoch gniazdach - przypisanie nie jest pewne) tego napisu nie ma, jest "Ten sam projekt jest tez w: ..."."""
    from stanowisko.ui import kandydaci

    skany = atrapa.scenariusz_poranny()
    e = ekrany(atrapa)
    e.klik_rano(skany[4], 1)
    assert e.w("praca_rano_decyzja").text() == NR.PRZYPISANIE_AUTO
    konflikt = atrapa.stan().rano.plytka(skany[5]).gniazdo(3).praca
    assert konflikt.klasa == "konflikt" and konflikt.konflikt_z and konflikt.przypisanie == "auto"  # stary ekran pisal tu "dopasowanie pewne"
    e.klik_rano(skany[5], 3)
    assert e.jest("praca_rano_konflikt") and NR.PRZYPISANIE_AUTO not in e.tekst() and not kandydaci.przypisanie_programu(konflikt)


# ----------------------------------------------------------------------------
# ochrona 800 ms
# ----------------------------------------------------------------------------
def test_ochrona_strefy_pytan_rano_po_zmianie_w_tle(atrapa, ekrany):
    """S3-3 rano: pozycja strefy pytan podmieniona w tle (pytanie o numer plytki nowego skanu staje na miejscu komunikatu) - strefa
    przygaszona, klikniecie odpowiedzi w ciagu ``OCHRONA_MS`` pominiete; potem dziala. Pozycja otwarta przez osobe (wybor numeru plytki)
    nie wlacza ochrony."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    k = UW.Szpieg(atrapa)
    skany = atrapa.scenariusz_poranny()
    e = ekrany(k)
    TR.rozstrzygnij_konflikt(e, atrapa, skany)
    e.klawisz(Qt.Key.Key_Escape)
    e.po_ochronie_nakladek()
    przed = e.rano.strefa.klucz()
    assert przed is not None  # komunikat "ramka poranna nie jest podlaczona"
    atrapa.symuluj_skan_rano(None, {1: "pewna", 2: "pewna"}, projekty={1: 305, 2: 306})
    e.czekaj(lambda: e.jest("pytanie_brak_numeru_plytki"), 5.0, "pytanie o numer plytki")
    assert e.rano.strefa.klucz() != przed and e.rano.strefa.chroniona() and e.okno.ochrona_nakladek_aktywna()
    QTest.mouseClick(e.w("odp_podaj_numer_plytki_5"), Qt.MouseButton.LeftButton)
    assert k.wyslane("podaj_numer_plytki") == []
    e.klik("odp_podaj_numer_plytki_5")  # ``klik`` czeka na koniec ochrony jak technik
    assert len(k.wyslane("podaj_numer_plytki")) == 1
    e.klik(f"rano_plytka_{skany[4]}_podaj_numer_plytki")  # wybor numeru otwarty przez osobe: nowa pozycja strefy bez ochrony
    assert e.jest("panel_numer_plytki") and not e.rano.strefa.chroniona()


def test_ochrona_map_po_wejsciu_w_tryb_rano_i_po_zmianie_zestawu_plytek(atrapa, ekrany):
    """Mapy plytek pieca staja tam, gdzie byla mapa wieczorna: po wejsciu w tryb poranny klikniecie gniazda w ciagu ``OCHRONA_MS``
    jest pomijane (mapy przygaszone). To samo, gdy w tle zmienia sie zestaw plytek (nowy skan przestawia mapy)."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    skany = atrapa.scenariusz_poranny()
    atrapa.przelacz_tryb("wieczor")
    e = ekrany(atrapa)
    assert not e.okno.rano()
    e.klik("przycisk_tryb_rano")
    assert e.okno.rano() and e.rano.ochrona_aktywna()
    mapa = e.mapy()[skany[4]]
    assert mapa.przygaszona()
    QTest.mouseClick(mapa, Qt.MouseButton.LeftButton, pos=mapa.srodek_gniazda(9).toPoint())
    assert e.rano.pokazana_praca() is None
    e.klik_rano(skany[4], 9)  # po ochronie
    assert e.rano.pokazana_praca() is not None and not mapa.przygaszona()
    atrapa.symuluj_skan_rano(7, {1: "pewna"}, projekty={1: 380})
    e.czekaj(lambda: len(e.mapy()) == 4, 5.0, "czwarta plytka")
    assert e.rano.ochrona_aktywna()


# ----------------------------------------------------------------------------
# skroty i pytanie przed "Zamknij piec"
# ----------------------------------------------------------------------------
def test_skroty_poranka(atrapa, ekrany):
    """Klawiatura jak ramka poranna: cyfry i "#" (tylko na poczatku) = numer kuwety w polu "Inna kuweta", litery nic nie robia,
    najwyzej ``MAX_BUFORA`` znakow; Backspace poprawia numer, Esc go czysci; Enter z numerem = ``wybierz_kuwete``, bez numeru =
    ``potwierdz_kuwete`` POKAZANEJ kuwety; Backspace bez numeru = ``cofnij_kuwete``; przytrzymany Enter / Backspace = jedno nacisniecie;
    Esc zamyka otwarta prace; Spacja = start skanu (takze z fokusem na przycisku - nigdy go nie klika)."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    from stanowisko.ui import ekran_rano

    k = UW.Szpieg(atrapa)
    skany = atrapa.scenariusz_poranny()
    e = ekrany(k)
    e.wpisz("#3a2")
    assert e.rano.bufor() == "#32" and NR.BUFOR.format(bufor="#32") == e.w("rano_bufor").text() and "#32" in e.w("rano_pole_kuwety").text()
    e.wpisz("#")
    assert e.rano.bufor() == "#32"  # "#" tylko na poczatku
    e.klawisz(Qt.Key.Key_Backspace)
    assert e.rano.bufor() == "#3" and k.wyslane("cofnij_kuwete") == []
    e.klawisz(Qt.Key.Key_Escape)
    assert e.rano.bufor() == "" and not e.jest("rano_bufor") and e.w("rano_pole_kuwety").text() == NR.POLE_KUWETY_PUSTE
    e.wpisz("1234567890")
    assert len(e.rano.bufor()) == ekran_rano.MAX_BUFORA
    e.klawisz(Qt.Key.Key_Escape)
    pokazana = atrapa.stan().rano.kuweta_biezaca
    e.klawisz(Qt.Key.Key_Return)
    assert k.wyslane("potwierdz_kuwete") == [("potwierdz_kuwete", (pokazana,))]
    klawisz_przytrzymany(e.okno, Qt.Key.Key_Return)
    assert len(k.wyslane("potwierdz_kuwete")) == 1
    do_cofniecia = atrapa.stan().rano.kuweta_do_cofniecia
    e.klawisz(Qt.Key.Key_Backspace)
    assert k.wyslane("cofnij_kuwete") == [("cofnij_kuwete", (do_cofniecia,))]
    klawisz_przytrzymany(e.okno, Qt.Key.Key_Backspace)
    assert len(k.wyslane("cofnij_kuwete")) == 1
    cel = atrapa.stan().rano.kuwety[-1].kuweta
    e.wpisz(cel)
    e.klawisz(Qt.Key.Key_Return)
    assert k.wyslane("wybierz_kuwete") == [("wybierz_kuwete", (cel,))] and e.w("rano_kuweta_biezaca").text() == cel
    e.klik_rano(skany[4], 9)
    assert e.rano.pokazana_praca() is not None and e.w("rano_prawa_kolumna").isAncestorOf(e.w("praca_rano_tytul"))
    e.klawisz(Qt.Key.Key_Escape)
    assert e.rano.pokazana_praca() is None and e.jest("tabela_kuwet")
    przycisk = e.w("przycisk_zamknij_piec")
    przycisk.setFocus(Qt.FocusReason.TabFocusReason)
    QTest.keyClick(przycisk, Qt.Key.Key_Space)
    e.odczekaj(5)
    assert len(k.wyslane("start_skanu")) == 1 and k.wyslane("zamknij_piec") == [] and not e.jest("pytanie_zamknij_mimo")


def test_pytanie_przed_zamknij_piec_enter_nie_rozklada_esc_wraca_do_rozstrzygania(atrapa, ekrany):
    """E3-P14 (N3) w nowej strefie: "Zamknij piec" z pracami bez rozstrzygniecia - pytanie w strefie pytan nad mapami (pierwsza pozycja,
    przed komunikatami), Enter nie zapisuje "Rozlozona", Esc = "Wroc do rozstrzygania" (otwiera pierwsza prace bez rozstrzygniecia);
    "Zamknij piec mimo to" zamyka TEN piec i przelacza na "Kompletne i braki"."""
    from PySide6.QtCore import Qt

    k = UW.Szpieg(atrapa)
    skany = atrapa.scenariusz_poranny()
    e = ekrany(k)
    TR.rozstrzygnij_konflikt(e, atrapa, skany)
    e.klawisz(Qt.Key.Key_Escape)
    e.klik("przycisk_zamknij_piec")
    assert e.strefa_rano()[0] == "pytanie_zamknij_mimo" and e.jest("pytanie_zamknij_mimo") and k.wyslane("zamknij_piec") == []
    assert e.w("rano_strefa_komunikatow").isAncestorOf(e.w("zamknij_mimo_tak"))
    e.klawisz(Qt.Key.Key_Return)
    assert k.wyslane("potwierdz_kuwete") == [] and e.jest("pytanie_zamknij_mimo")
    e.klawisz(Qt.Key.Key_Escape)
    pierwsza = atrapa.stan().rano.nierozstrzygniete_prace[0]
    assert not e.jest("pytanie_zamknij_mimo") and e.rano.pokazana_praca().praca_id == pierwsza.praca_id
    e.klik("przycisk_zamknij_piec")
    piec = atrapa.stan().rano.sesja_pieca_id
    e.klik("zamknij_mimo_tak")
    assert k.wyslane("zamknij_piec") == [("zamknij_piec", (piec,))] and not atrapa.stan().rano.otwarty
    assert e.rano.strona() == "wynik" and e.w("rano_strona_wynik").isChecked() and e.jest("tabela_kompletne")


def test_kafelek_plytki_otwiera_pierwsza_prace_bez_rozstrzygniecia_i_polecenia_plytki(atrapa, ekrany):
    """Kafelek plytki w lewej kolumnie: liczba prac, ile bez rozstrzygniecia (ze stanu), liczniki klas z napisem; klikniecie = plytka
    wybrana (obwodka mapy) i pierwsza jej praca bez rozstrzygniecia w kolumnie "Praca". Polecenia plytki ("Zmien numer") na kafelku -
    wybor numeru w strefie pytan z godzina skanu (S3-3)."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    from stanowisko.ui import napisy as N
    from stanowisko.ui.czesci import godzina

    skany = atrapa.scenariusz_poranny()
    e = ekrany(atrapa)
    nier =[x for x in atrapa.stan().rano.nierozstrzygniete_prace if x.skan_id == skany[5]]
    assert nier
    kafelek = e.w(f"rano_kafelek_{skany[5]}")
    assert NR.KAFELEK_DO_ROZSTRZYGNIECIA.format(n=len(nier)) in e.w(f"rano_kafelek_{skany[5]}_stan").text()
    QTest.mouseClick(kafelek, Qt.MouseButton.LeftButton)
    e.odczekaj(5)
    assert e.rano.pokazana_praca().praca_id == nier[0].praca_id and e.w(f"rano_plytka_{skany[5]}").property("wybrany") == "true"
    e.klik(f"rano_plytka_{skany[4]}_podaj_numer_plytki")
    plytka = atrapa.stan().rano.plytka(skany[4])
    assert e.jest("panel_numer_plytki")
    tytul = e.tekst_elementu("panel_numer_plytki")
    assert N.PLYTKA_ZE_SKANEM.format(plytka=NR.PLYTKA_NR.format(numer=plytka.numer), godzina=godzina(plytka.czas)) in tytul
    e.klik("numer_bez_zmian")
    assert not e.jest("panel_numer_plytki")


# ----------------------------------------------------------------------------
# Excel i pasek stanu, bledy programu
# ----------------------------------------------------------------------------
def test_zakladka_excel_sama_sie_pokazuje_pozniej_wraca_i_pole_excela_na_pasku(tmp_path, ekrany):
    """E3-A12 w nowym ukladzie: po "Zamknij piec" (tryb "pytaj") zakladka "Excel" pokazuje sie sama; osoba moze przejsc na inna
    zakladke i wrocic; "Pozniej" zamyka okno Excela - wraca "Kompletne i braki", zakladka "Excel" nieaktywna. Pole Excela na pasku
    stanu tylko rano: "do zatwierdzenia: n", bez Excela "niedostepny"."""
    import test_aplikacja_rano as TA
    from stanowisko import kontroler_api as K

    k = K.AtrapaKontrolera(tmp_path / "k", zegar=TR.ZegarRano())
    try:
        k.przelacz_tryb("rano")
        k.wybierz_operatora("Technik A")
        e = ekrany(k)
        assert e.jest("napis_excel") and e.w("napis_excel").text() == NR.EXCEL_PASEK_STANY["brak"] and not e.jest("rano_strona_excel")
        TA._excel_pytaj(k, tmp_path)
        k.symuluj_skan_rano(4, TA.PLYTKA_4[0], projekty=TA.PLYTKA_4[1])
        TR.zamknij_piec(e, pytanie=False)
        e.czekaj(lambda: e.jest("excel_panel") and k.stan().excel.w_toku == 0, 10.0, "okno Excela")
        ile = k.stan().excel.do_zalatwienia
        assert e.rano.strona() == "excel" and e.w("rano_strona_excel").isChecked() and e.aktywny("rano_strona_excel")
        assert e.w("napis_excel").text() == NR.EXCEL_PASEK_STANY["do_zatwierdzenia"].format(n=ile) and ile > 0
        e.klik("rano_strona_rozkladanie")
        assert not e.jest("excel_panel") and e.jest("rano_kuweta_wiersz")
        e.klik("rano_strona_excel")
        assert e.jest("excel_panel")
        e.klik("excel_pozniej")
        assert not e.jest("excel_panel") and e.rano.strona() == "wynik" and e.jest("rano_strona_excel") and not e.aktywny("rano_strona_excel")
        k.przelacz_tryb("wieczor")
        e.zdarzenia()
        e.odczekaj(30)
        assert not e.jest("napis_excel")
    finally:
        k.zamknij()


def test_bledy_programu_rano_na_liscie_okna_nie_w_strefie(atrapa, ekrany):
    """Bledy programu rano: licznik na pasku stanu i rozwijana lista okna (jak wieczorem, SPEC p. 3 pkt 5), nie w strefie pytan;
    licznik zwija i rozwija liste."""
    from stanowisko.ui import napisy as N

    atrapa.scenariusz_poranny()
    e = ekrany(atrapa)
    atrapa.symuluj_skaner(dostepny=False)
    e.czekaj(lambda: e.jest("lista_bledow"), 5.0, "lista bledow")
    assert e.jest("przycisk_bledy") and e.w("przycisk_bledy").text() == N.BLEDY_PROGRAMU.format(n=1)
    assert "komunikat_folder_skanera_niedostepny" not in e.strefa_rano()
    e.klik("przycisk_bledy")
    assert not e.jest("lista_bledow") and e.jest("przycisk_bledy")



# ----------------------------------------------------------------------------
# runda 2 (recenzja PR #64): P1 - P4
# ----------------------------------------------------------------------------
ROZMIARY_LISTY = ((1920, 1001), (1536, 784), (1280, 642))  # okno zmaksymalizowane przy 100 / 125 / 150 %


def kuwety_pod_punktami(t, punkty: list) -> list:
    """Numer kuwety w wierszu pod kazdym punktem pola listy (y w ``viewport``) - to, co widzi i w co celuje osoba."""
    wynik = []
    for y in punkty:
        w = t.rowAt(y)
        wynik.append(t.item(w, 0).text() if w >= 0 and t.item(w, 0) is not None else None)
    return wynik


@pytest.mark.parametrize("rozmiar", ROZMIARY_LISTY)
def test_s3_16_lista_kuwet_przewinieta_w_tle_wstrzymuje_klikniecia(atrapa, ekrany, rozmiar):
    """Runda 2, P1: "Rozlozona" z tla (ramka poranna / drugie stanowisko) zmienia biezaca kuwete i lista przewija sie do niej -
    pod nieruchomym kursorem staje inna kuweta, chociaz kolejnosc listy sie nie zmienila. Za KAZDYM razem, gdy w ktoryms punkcie
    pola listy stoi po zmianie inna kuweta, ochrona ``OCHRONA_MS`` jest aktywna i klikniecie w ten punkt nic nie wysyla
    (pomiar recenzenta: 8 / 13 / 19 zmian bez ochrony na 33 kroki)."""
    from PySide6.QtCore import QPoint, Qt
    from PySide6.QtTest import QTest

    k = UW.Szpieg(atrapa)
    atrapa.scenariusz_poranny()
    e = ekrany(k, rozmiar)
    e.po_ochronie_rano()
    t = e.w("tabela_kuwet")
    panel = e.rano.kuwety
    assert t.verticalScrollBar().maximum() > 0, "lista kuwet miesci sie w polu - proba bez sensu"
    wys = t.viewport().height()
    punkty = [wys * i // 8 for i in range(1, 8)]
    zmian, bez_ochrony = 0, []
    for krok in range(t.rowCount() + 2):
        rano = atrapa.stan().rano
        if rano.kuweta_biezaca is None:
            break
        przed = kuwety_pod_punktami(t, punkty)
        assert atrapa.potwierdz_kuwete(rano.kuweta_biezaca).ok  # w tle - nie przez okno
        e.zdarzenia()
        e.odczekaj(20)
        po = kuwety_pod_punktami(t, punkty)
        if po == przed:
            continue
        zmian += 1
        if not panel.ochrona_aktywna():
            bez_ochrony.append((krok, przed, po))
            continue
        y = next(y for y, a, b in zip(punkty, przed, po) if a != b)
        wyslane = len(k.wyslane("wybierz_kuwete"))
        QTest.mouseClick(t.viewport(), Qt.MouseButton.LeftButton, pos=QPoint(20, y))
        e.odczekaj(5)
        assert len(k.wyslane("wybierz_kuwete")) == wyslane, f"krok {krok}: klikniecie w przesunieta liste wybralo kuwete"
    assert zmian > 0 and bez_ochrony == [], f"zmian pod kursorem {zmian}, bez ochrony {len(bez_ochrony)}: {bez_ochrony[:3]}"


def test_excel_wskaz_wiersz_z_zakladki_kompletne_przy_otwartym_oknie_excela(tmp_path, ekrany):
    """Runda 2, P2: okno Excela juz otwarte dla pieca (zakladka "Excel" pokazala sie sama), osoba przeszla na "Kompletne i braki"
    i klika "Excel: wskaz wiersz" - zakladka "Excel" pokazuje sie (wczesniej przycisk nic nie robil)."""
    import test_aplikacja_rano as TA
    from stanowisko import kontroler_api as K

    k0 = K.AtrapaKontrolera(tmp_path / "k", zegar=TR.ZegarRano())
    k = UW.Szpieg(k0)
    try:
        k0.przelacz_tryb("rano")
        k0.wybierz_operatora("Technik A")
        e = ekrany(k)
        TA._excel_pytaj(k0, tmp_path)
        k0.symuluj_skan_rano(4, TA.PLYTKA_4[0], projekty=TA.PLYTKA_4[1])
        TR.zamknij_piec(e, pytanie=False)
        e.czekaj(lambda: e.jest("excel_panel") and k0.stan().excel.w_toku == 0, 10.0, "okno Excela")
        e.klik("rano_strona_wynik")
        assert e.rano.strona() == "wynik" and not e.jest("excel_panel") and k0.stan().excel.widoczne
        assert e.aktywny("przycisk_excel")
        e.klik("przycisk_excel")
        e.odczekaj(20)
        assert k.wyslane("excel_pokaz") and e.rano.strona() == "excel" and e.jest("excel_panel") and e.w("rano_strona_excel").isChecked()
    finally:
        k0.zamknij()


def test_przycisk_zaleglego_pieca_przez_pokaz_excel_pokazuje_zakladke_excel(tmp_path, ekrany):
    """Runda 3, D10 (do P2): przycisk zaleglego pieca ("Piec n (doba) - ile") na zakladce "Kompletne i braki" idzie przez
    ``EkranRano.pokaz_excel`` - te sama funkcje co "Excel: wskaz wiersz" (przelaczenie na zakladke "Excel" takze przy oknie Excela
    juz otwartym), nie przez gole polecenie ``excel_pokaz``. Okno Excela pieca 2 otwarte, piec 1 odlozony ("Pozniej") - osoba na
    "Kompletne i braki" klika przycisk pieca 1: polecenie ``excel_pokaz`` z piecem 1, zakladka "Excel" z oknem pieca 1. Kontroler
    nie podaje pieca okna wsrod zaleglych (``kontroler_api``: ``zalegle`` bez ``sid`` okna), wiec przy dzisiejszym kontrolerze
    zakladke przelacza tez samo pokazanie okna innego pieca - dlatego test pilnuje rowniez drogi przez ``pokaz_excel``."""
    import test_aplikacja_rano as TA
    from stanowisko import kontroler_api as K

    k0 = K.AtrapaKontrolera(tmp_path / "k", zegar=TR.ZegarRano())
    k = UW.Szpieg(k0)
    try:
        k0.przelacz_tryb("rano")
        k0.wybierz_operatora("Technik A")
        e = ekrany(k)
        TA._excel_pytaj(k0, tmp_path)
        k0.symuluj_skan_rano(4, TA.PLYTKA_4[0], projekty=TA.PLYTKA_4[1])
        TR.zamknij_piec(e, pytanie=False)
        e.czekaj(lambda: e.jest("excel_panel") and k0.stan().excel.w_toku == 0, 10.0, "okno Excela pieca 1")
        piec1 = k0.stan().excel.sesja_pieca_id
        e.klik("excel_pozniej")
        assert not e.jest("excel_panel")
        k0.symuluj_skan_rano(5, {1: "pewna", 2: "pewna"}, projekty={1: 305, 2: 306})
        TR.zamknij_piec(e, pytanie=False)
        e.czekaj(lambda: e.jest("excel_panel") and k0.stan().excel.sesja_pieca_id != piec1, 10.0, "okno Excela pieca 2")
        e.klik("rano_strona_wynik")
        assert e.rano.strona() == "wynik" and k0.stan().excel.widoczne and [z[0] for z in k0.stan().excel.zalegle] == [piec1]
        wywolania = []
        oryginal = e.rano.pokaz_excel

        def szpieg_pokaz_excel(sid):
            wywolania.append(sid)
            return oryginal(sid)

        e.rano.pokaz_excel = szpieg_pokaz_excel
        przycisk = f"wynik_excel_zalegly_{piec1}"
        assert e.aktywny(przycisk)
        e.klik(przycisk)
        e.odczekaj(20)
        assert wywolania == [piec1], f"przycisk zaleglego pieca ominal EkranRano.pokaz_excel: {wywolania}"
        assert k.wyslane("excel_pokaz")[-1] == ("excel_pokaz", (piec1,))
        assert e.rano.strona() == "excel" and e.jest("excel_panel") and e.w("rano_strona_excel").isChecked()
        assert k0.stan().excel.sesja_pieca_id == piec1 and [p.kuweta for p in k0.stan().excel.pozycje] == ["3200", "3207"]
    finally:
        k0.zamknij()


def kolory_zmiany(mapa, wybrane, obwodka) -> list:
    """Kolory pikseli mapy, ktore zmienia samo oznaczenie (``wybrane`` gniazdo albo ``obwodka`` gniazd kuwety) wobec mapy bez
    oznaczen - to, czym oznaczenie wyglada na ekranie (odczyt z obrazu widzetu)."""
    plytka, geometria, obrazy = mapa._plytka, mapa._geometria, mapa._obrazy
    mapa.ustaw_rano(plytka, geometria, None, frozenset(), obrazy)
    bez = mapa.grab().toImage()
    mapa.ustaw_rano(plytka, geometria, wybrane, frozenset(obwodka), obrazy)
    z = mapa.grab().toImage()
    kolory = []
    for x in range(bez.width()):
        for y in range(bez.height()):
            if bez.pixel(x, y) != z.pixel(x, y):
                kolory.append(z.pixelColor(x, y))
    return kolory


def blisko(kolor, hex_: str, tolerancja: int = 40) -> bool:
    from PySide6.QtGui import QColor

    w = QColor(hex_)
    return abs(kolor.red() - w.red()) + abs(kolor.green() - w.green()) + abs(kolor.blue() - w.blue()) <= tolerancja


def test_mapa_rano_obwodka_kuwety_inna_niz_pierscien_wybranego_gniazda_i_objasnienie(atrapa, ekrany):
    """Runda 2, P3: gniazdo wybrane kliknieciem (pierscien akcentu - SPEC p. 2) i gniazda biezacej kuwety (obwodka) sa na mapie
    porannej rozroznialne: w obwodce kuwety nie ma barwy akcentu, w pierscieniu wybranego jest. Legenda "Na plytkach" objasnia
    oba oznaczenia (napis "Gniazda biezacej kuwety sa obwiedzione" zniknal z ekranu w U1b)."""
    from stanowisko.ui import mapa_rano as MR
    from stanowisko.ui import motyw

    skany = atrapa.scenariusz_poranny()
    e = ekrany(atrapa)
    e.po_ochronie_rano()
    rano = atrapa.stan().rano
    p4 = skany[4]
    obwodka = rano.obwodka(p4)
    assert obwodka, "biezaca kuweta nie ma gniazd na plytce 4"
    mapa = e.mapy()[p4]
    inne = next(nr for nr in mapa.numery() if nr not in obwodka)
    kuweta = kolory_zmiany(mapa, None, obwodka)
    wybrane = kolory_zmiany(mapa, inne, ())
    assert kuweta and wybrane
    akcent_w_kuwecie = sum(blisko(c, motyw.AKCENT) for c in kuweta)
    akcent_w_wybranym = sum(blisko(c, motyw.AKCENT) for c in wybrane)
    assert akcent_w_kuwecie == 0, f"obwodka kuwety ma {akcent_w_kuwecie} z {len(kuweta)} pikseli w barwie akcentu (jak pierscien wybranego)"
    assert akcent_w_wybranym > len(wybrane) // 3  # pierscien wybranego gniazda w barwie akcentu (SPEC)
    assert sum(blisko(c, MR.KOLOR_BIEZACEJ) for c in kuweta) > len(kuweta) // 3
    assert sum(blisko(c, MR.KOLOR_BIEZACEJ) for c in wybrane) == 0
    # objasnienie na ekranie (legenda lewej kolumny)
    for nazwa, napis in (("rano_legenda_obwodka_kuwety", NR.LEGENDA_OBWODKA_KUWETY), ("rano_legenda_wybrane_gniazdo", NR.LEGENDA_WYBRANE_GNIAZDO)):
        assert e.jest(nazwa) and e.w(nazwa).text() == napis
    # kontrast obu oznaczen na plytce (WGLEBIENIE) - pary w ``motyw.PARY_KONTRASTU`` (sprawdza ``test_ui_motyw``)
    pary = {(a, b) for _, a, b in motyw.PARY_KONTRASTU}
    assert (MR.KOLOR_BIEZACEJ, motyw.WGLEBIENIE) in pary and (motyw.AKCENT, motyw.WGLEBIENIE) in pary


@pytest.mark.parametrize("dodatkowe", (0, 3))
@pytest.mark.parametrize("rozmiar", ROZMIARY)
def test_objasnienie_obwodek_widoczne_bez_przewijania(atrapa, ekrany, rozmiar, dodatkowe):
    """Runda 3, P9: objasnienie oznaczen na mapach (biala obwodka - gniazda biezacej kuwety, niebieski pierscien - gniazdo wybrane)
    widac w calosci bez przewijania w 6 rozmiarach okna (w tym 1536 x 784 i 1280 x 642 - okno zmaksymalizowane przy 125 / 150 %),
    w piecu z 3 plytkami (scenariusz) i z 6 plytkami. W rundzie 2 objasnienie stalo na dole przewijanej lewej kolumny - przy 125 / 150 %
    widac bylo z niego 0 px. Sprawdza polozenie w widocznym obszarze okna (przyciete przez rodzicow), nie samo ``isVisible``."""
    from stanowisko.ui import mapa_rano as MR

    skany = atrapa.scenariusz_poranny()
    for nr in (1, 2, 3)[:dodatkowe]:
        atrapa.symuluj_skan_rano(nr, {1: "pewna", 2: "pewna", 3: "pewna"})
    e = ekrany(atrapa, rozmiar)
    e.po_ochronie_rano()
    assert len(e.mapy()) == 3 + dodatkowe and atrapa.stan().rano.obwodka(skany[4])
    for nazwa, napis in (("rano_legenda_obwodka_kuwety", NR.LEGENDA_OBWODKA_KUWETY), ("rano_legenda_wybrane_gniazdo", NR.LEGENDA_WYBRANE_GNIAZDO)):
        w = e.w(nazwa)
        assert w.isVisibleTo(e.okno) and w.text() == napis, nazwa
        for czesc in (w, *w.parentWidget().findChildren(MR.WzorOznaczenia)):
            cala = UW._w_oknie(e.okno, czesc)
            assert not cala.isEmpty() and UW._widoczny_wycinek(e.okno, czesc) == cala, (rozmiar, nazwa, cala, UW._widoczny_wycinek(e.okno, czesc))
        assert not UW._w_obszarze_przewijanym(e.okno, w), nazwa  # nie zalezy od tego, jak daleko przewinieto liste plytek


def liczby(tekst: str) -> list:
    import re

    return [int(x) for x in re.findall(r"\d+", tekst)]


@pytest.mark.parametrize("rozmiar", ((1920, 1001), (1280, 642)))
def test_napis_gniazd_biezacej_kuwety_wszystkie_gniazda_wszystkich_plytek(atrapa, ekrany, rozmiar):
    """Runda 2, P4 (a): napis "Plytka 4 - gniazda 2 i 9; Plytka 5 - gniazdo 1" wymienia KAZDE gniazdo biezacej kuwety z
    ``KuwetaRano.gniazda`` (kazda kuweta scenariusza po kolei biezaca; uklad wysoki - ``rano_kuweta_miejsca``, zwarty -
    ``rano_kuweta_miejsca_krotko``, pelny tekst)."""
    atrapa.scenariusz_poranny()
    e = ekrany(atrapa, rozmiar)
    zwarty = rozmiar[1] < 700
    nazwa = "rano_kuweta_miejsca_krotko" if zwarty else "rano_kuweta_miejsca"
    odstep = NR.NIEROZSTRZYGNIETE_ODSTEP if zwarty else "\n"
    sprawdzone = wiele_gniazd = wiele_plytek = 0
    for x in atrapa.stan().rano.kuwety:
        assert atrapa.wybierz_kuwete(x.kuweta).ok
        e.zdarzenia()
        e.odczekaj(5)
        rano = atrapa.stan().rano
        biezaca = next(y for y in rano.kuwety if y.biezaca)
        assert biezaca.kuweta == x.kuweta and e.w("rano_kuweta_biezaca").text() == x.kuweta
        oczekiwane: dict = {}
        for skan_id, nr in biezaca.gniazda:
            oczekiwane.setdefault(rano.plytka(skan_id).numer, set()).add(nr)
        if not oczekiwane:
            continue
        assert e.jest(nazwa)
        wiersze = e.w(nazwa).text().split(odstep)
        widziane = {liczby(w)[0]: set(liczby(w)[1:]) for w in wiersze}
        assert len(wiersze) == len(oczekiwane) and widziane == oczekiwane, f"kuweta {x.kuweta}: {e.w(nazwa).text()!r} != {oczekiwane}"
        sprawdzone += 1
        wiele_gniazd += any(len(v) > 1 for v in oczekiwane.values())
        wiele_plytek += len(oczekiwane) > 1
    assert sprawdzone >= 8 and wiele_gniazd >= 1 and wiele_plytek >= 1, (sprawdzone, wiele_gniazd, wiele_plytek)


def test_to_ten_projekt_drugiego_kandydata_zapisuje_drugiego(atrapa, ekrany):
    """Runda 2, P4 (b): "To ten projekt" na karcie DRUGIEGO kandydata wysyla ``wybierz_kandydata(praca_id, sha16 drugiego)`` i praca
    dostaje projekt drugiego kandydata (testy klikaly tylko pierwszego)."""
    k = UW.Szpieg(atrapa)
    skany = atrapa.scenariusz_poranny()
    atrapa.wybierz_operatora("Technik A")
    e = ekrany(k)
    p4 = skany[4]
    praca = atrapa.stan().rano.plytka(p4).gniazdo(9).praca
    assert praca.klasa == "dwuznaczna" and len(praca.kandydaci) >= 2
    pierwszy, drugi = praca.kandydaci[0], praca.kandydaci[1]
    assert drugi.projekt_id is not None and drugi.projekt_id != pierwszy.projekt_id and drugi.sha16 != pierwszy.sha16
    e.klik_rano(p4, 9)
    assert e.aktywny("kandydat_2_wybierz")
    e.klik("kandydat_2_wybierz")
    assert k.wyslane("wybierz_kandydata") == [("wybierz_kandydata", (praca.praca_id, drugi.sha16))]
    assert atrapa.stan().rano.plytka(p4).gniazdo(9).praca.projekt_id == drugi.projekt_id


def test_rozlozona_i_cofnij_nieaktywne_bez_osoby(atrapa, ekrany):
    """Runda 2, P4 (c): bez wybranej osoby "Rozlozona [Enter]" i "Cofnij [Backspace]" sa nieaktywne (z osoba - aktywne)."""
    atrapa.scenariusz_poranny()
    atrapa.wybierz_operatora("Technik A")
    rano = atrapa.stan().rano
    assert atrapa.potwierdz_kuwete(rano.kuweta_biezaca).ok  # jest co cofnac
    e = ekrany(atrapa)
    assert e.aktywny("rano_potwierdz_kuwete") and e.aktywny("rano_cofnij_kuwete")
    assert atrapa.wybierz_operatora(None).ok
    e.zdarzenia()
    e.odczekaj(20)
    rano = atrapa.stan().rano
    assert rano.kuweta_biezaca is not None and rano.kuweta_do_cofniecia is not None and atrapa.stan().operator is None
    assert e.jest("rano_potwierdz_kuwete") and not e.aktywny("rano_potwierdz_kuwete")
    assert e.jest("rano_cofnij_kuwete") and not e.aktywny("rano_cofnij_kuwete")



# ----------------------------------------------------------------------------
# runda 2 (recenzja PR #64): uwagi D
# ----------------------------------------------------------------------------
@pytest.mark.parametrize("rozmiar", ROZMIARY_LISTY)
def test_d6_wysokosc_wierszy_listy_kuwet_od_otwarcia_okna(atrapa, ekrany, rozmiar):
    """Runda 2, D6: wiersze listy kuwet maja wysokosc z ukladu okna (``Uklad.wiersz_tabeli``: 30 / 26 px) od razu po otwarciu
    okna, a nie dopiero po pierwszej zmianie stanu - wiersze nie przeskakuja pod kursorem (bylo: zwarty 30 -> 26 px)."""
    from stanowisko.ui import motyw

    atrapa.scenariusz_poranny()
    e = ekrany(atrapa, rozmiar)
    e.zdarzenia()
    u = motyw.uklad_dla(*rozmiar)
    t = e.w("tabela_kuwet")
    przed = {t.rowHeight(i) for i in range(t.rowCount())}
    assert przed == {u.wiersz_tabeli}, f"{rozmiar}: wiersze {przed}, uklad {u.nazwa} {u.wiersz_tabeli}"
    assert atrapa.potwierdz_kuwete(atrapa.stan().rano.kuweta_biezaca).ok
    e.zdarzenia()
    e.odczekaj(20)
    assert {t.rowHeight(i) for i in range(t.rowCount())} == {u.wiersz_tabeli}



@pytest.mark.parametrize("rozmiar", ((1536, 784), (1280, 642)))
def test_d6_wysokosc_wierszy_tabel_panelu_excela_w_ukladzie_zwartym(tmp_path, ekrany, rozmiar):
    """Runda 2, D6 (panel Excela): wiersze tabel panelu Excela w ukladzie zwartym maja ``Uklad.wiersz_tabeli`` od pierwszego
    pokazania (ta sama kolejnosc minimum / domyslna co w liscie kuwet)."""
    import test_aplikacja_rano as TA
    from PySide6.QtWidgets import QTableWidget
    from stanowisko import kontroler_api as K
    from stanowisko.ui import motyw

    k0 = K.AtrapaKontrolera(tmp_path / "k", zegar=TR.ZegarRano())
    try:
        k0.przelacz_tryb("rano")
        k0.wybierz_operatora("Technik A")
        e = ekrany(k0, rozmiar)
        TA._excel_pytaj(k0, tmp_path)
        k0.symuluj_skan_rano(4, TA.PLYTKA_4[0], projekty=TA.PLYTKA_4[1])
        TR.zamknij_piec(e, pytanie=False)
        e.czekaj(lambda: e.jest("excel_panel") and k0.stan().excel.w_toku == 0, 10.0, "okno Excela")
        u = motyw.uklad_dla(*rozmiar)
        tabele = [t for t in e.w("excel_panel").findChildren(QTableWidget) if t.isVisible() and t.rowCount()]
        assert tabele
        wysokosci = {(t.objectName(), t.rowHeight(i)) for t in tabele for i in range(t.rowCount())}
        assert {w for _, w in wysokosci} == {u.wiersz_tabeli}, f"{rozmiar}: {sorted(wysokosci)}"
    finally:
        k0.zamknij()


def test_d8_kuweta_juz_rozlozona_wybrana_ponownie_widac_na_liscie_i_w_wierszu(atrapa, ekrany):
    """Runda 2, D8: kuweta juz rozlozona i wybrana ponownie numerem jest biezaca - lista pokazuje "teraz, juz rozlozona", a wiersz
    "Teraz rozkladasz" dopisek "juz rozlozona" (bylo: "teraz", jak kuweta jeszcze nierozlozona)."""
    atrapa.scenariusz_poranny()
    atrapa.wybierz_operatora("Technik A")
    e = ekrany(atrapa)
    kuweta = atrapa.stan().rano.kuweta_biezaca
    assert NR.KUWETA_JUZ_ROZLOZONA not in e.w("rano_kuweta_opis").text()
    assert atrapa.potwierdz_kuwete(kuweta).ok and atrapa.wybierz_kuwete(kuweta).ok
    e.zdarzenia()
    e.odczekaj(20)
    x = next(y for y in atrapa.stan().rano.kuwety if y.kuweta == kuweta)
    assert x.biezaca and x.potwierdzona
    wiersz = next(w for w in e.tabela("tabela_kuwet") if w[0] == kuweta)
    assert wiersz[3] == NR.KUWETA_STAN_BIEZACA_ROZLOZONA
    assert e.w("rano_kuweta_biezaca").text() == kuweta and NR.KUWETA_JUZ_ROZLOZONA in e.w("rano_kuweta_opis").text()
    inne = [w for w in e.tabela("tabela_kuwet") if w[0] != kuweta]
    assert all(w[3] != NR.KUWETA_STAN_BIEZACA_ROZLOZONA for w in inne)


@pytest.mark.parametrize("rozmiar", ((1536, 784), (1280, 642)))
def test_d5_gniazda_biezacej_kuwety_w_ukladzie_zwartym_bez_wielokropka(atrapa, ekrany, rozmiar):
    """Runda 2, D5: w ukladzie zwartym gniazda biezacej kuwety (jeden wiersz, zapis krotszy: "Plytka 4: gn. 2, 9") nie sa skracane
    wielokropkiem dla zadnej kuwety scenariusza (bylo: 2 z 33 przy 1280 x 642 - numer gniazda na drugiej plytce nieczytelny)."""
    atrapa.scenariusz_poranny()
    e = ekrany(atrapa, rozmiar)
    pole = e.w("rano_kuweta_miejsca_krotko")
    skrocone, sprawdzone = [], 0
    for x in atrapa.stan().rano.kuwety:
        assert atrapa.wybierz_kuwete(x.kuweta).ok
        e.zdarzenia()
        e.odczekaj(5)
        if not x.gniazda:
            continue
        assert e.jest("rano_kuweta_miejsca_krotko")
        sprawdzone += 1
        if pole.skrocona():
            skrocone.append((x.kuweta, pole.text()))
    assert sprawdzone >= 8 and skrocone == [], skrocone
