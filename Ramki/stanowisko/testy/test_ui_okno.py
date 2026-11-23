"""ui: nowe okno programu (E3-U1a; ``etap3/nowy_interfejs/SPEC.md``) - zachowania, ktorych stare okno nie mialo.

  (1) znaleziska analizy do zamkniecia w oknie wieczornym (SPEC p. 4): S3-3 (pytanie / wybor numeru zwiazane ze skanem, ochrona
      800 ms strefy pytan), S3-4 (napis o ubytkach), S3-14 (mapa poprzedniej plytki w czasie analizy), S3-15 (powrot z trybu
      rano, pozycja listy -> ``praca_id``, N pod ochrona),
  (2) strefa pytan i komunikatow: stala wysokosc, jedna pozycja naraz, licznik "i jeszcze n", pytania bez przewijania,
  (3) nakladki: lista osob pod paskiem gornym, lista bledow programu nad paskiem stanu - bez okien modalnych, mapa w miejscu,
  (4) szkielet: przelacznik trybu, wersja programu, pasek stanu bez skrotow w zwyklej pracy, blysk paska,
  (5) przycisk ze skrotem klawiszowym w ramce; status na mapie, w legendzie i na kafelku nie tylko barwa.
Okno sterowane z testu jak przez technika (``test_ui_wieczor.Ekran``), tryb offscreen, dane sztuczne. Plik jest ASCII.
"""
from __future__ import annotations

import dataclasses
from pathlib import Path

import pytest

import test_ui_wieczor as UW
from test_ui_wieczor import DLUGI_TEKST, Podstawiony, Szpieg, _qt_przed_silnikiem, _w_oknie, atrapa, ekrany, zegar  # noqa: F401 - fikstury

STANOWISKO = Path(__file__).resolve().parent.parent
ROZMIARY = ((1920, 1080), (1536, 864), (1280, 720))


def klik_w_punkcie(e, punkt) -> None:
    """Klikniecie w punkt okna - trafia w to, co technik ma pod kursorem (takze w przygaszajaca zaslone)."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    cel = e.okno.childAt(punkt) or e.okno
    QTest.mouseClick(cel, Qt.MouseButton.LeftButton, pos=cel.mapFrom(e.okno, punkt))


def srodek_w_oknie(e, nazwa: str):
    return _w_oknie(e.okno, e.w(nazwa)).center()


def pokazana(e) -> list:
    """Nazwa pozycji pokazanej w strefie pytan (lista jednoelementowa albo pusta)."""
    e.zdarzenia()
    return [p.objectName() for p in e.okno.strefa.panele()]


# ----------------------------------------------------------------------------
# (1) S3-3: pytanie o numer zwiazane ze skanem; ochrona strefy
# ----------------------------------------------------------------------------
def test_s3_3_pytanie_o_numer_ma_godzine_skanu_i_nowy_wynik_nie_podmienia_przyciskow(atrapa, ekrany, zegar):
    """Plytka A bez numeru z samymi zielonymi pracami (nic "do obejrzenia") i otwartym pytaniem "Podaj numer plytki". Tytul pytania
    wskazuje skan godzina. Wynik plytki B (tez bez numeru) NIE przelacza ekranu: pytanie zostaje pytaniem plytki A, a klikniecie
    cyfry w to samo miejsce nadaje numer plytce A. Stare okno przelaczalo sie na B i cyfra trafiala w B (znalezisko S3-3)."""
    from stanowisko import statusy as ST
    from stanowisko.ui import napisy as N
    from stanowisko.ui.czesci import do_obejrzenia

    k = Szpieg(atrapa)
    k.wybierz_operatora("Technik A")
    a = atrapa.symuluj_skan("bez_numeru", gniazda={1: "zielony", 2: "zielony"})
    e = ekrany(k)
    assert e.okno.pokazana_plytka() == a and pokazana(e) == ["pytanie_brak_numeru_plytki"]
    assert do_obejrzenia(atrapa.stan().plytka(a)) == []  # zadnej pracy do obejrzenia - stara regula pozwalala przelaczyc ekran
    tytul_a = N.TYTUL_ZE_SKANEM.format(tytul=ST.PYTANIA["brak_numeru_plytki"].tytul, godzina="19:00")
    assert tytul_a in e.tekst_elementu("pytanie_brak_numeru_plytki")
    punkt = srodek_w_oknie(e, "odp_podaj_numer_plytki_2")
    zegar.przesun(3)
    b = atrapa.symuluj_skan("bez_numeru", gniazda={1: "zielony", 3: "zielony"}, projekty={1: 11, 3: 13})
    assert e.okno.pokazana_plytka() == a and e.jest("przycisk_nowa_plytka")  # ekran zostal na A; B czeka jako nowy wynik
    assert N.PLYTKA_NOWA in e.tekst_elementu(f"plytka_{b}") and tytul_a in e.tekst_elementu("pytanie_brak_numeru_plytki")
    assert srodek_w_oknie(e, "odp_podaj_numer_plytki_2") == punkt and not e.okno.ochrona_strefy_aktywna()  # pytanie to samo - nie ma czego chronic
    klik_w_punkcie(e, punkt)
    e.odczekaj(10)
    stan = atrapa.stan()
    assert k.wyslane("podaj_numer_plytki") == [("podaj_numer_plytki", (a, 2))]
    assert stan.plytka(a).numer == 2 and stan.plytka(b).numer is None
    # po numerze plytka A nie ma juz nic do zrobienia; pytanie plytki B pokazuje dopiero klikniecie technika - z godzina JEGO skanu
    e.klik("przycisk_nowa_plytka")
    assert e.okno.pokazana_plytka() == b
    assert N.TYTUL_ZE_SKANEM.format(tytul=ST.PYTANIA["brak_numeru_plytki"].tytul, godzina="19:03") in e.tekst_elementu("pytanie_brak_numeru_plytki")


def test_s3_3_wybor_numeru_otwarty_przez_technika_nalezy_do_jednego_skanu(atrapa, ekrany, zegar):
    """Wybor numeru otwarty przyciskiem obok mapy ("Podaj numer plytki" po "Pozniej", "Zmien numer"): tytul wskazuje skan, przyciski
    niosa ``skan_id`` tej plytki, nowy wynik nie przelacza ekranu; po przelaczeniu przez technika wybor numeru sie zamyka (nie
    przechodzi na inna plytke)."""
    from stanowisko import statusy as ST
    from stanowisko.ui import napisy as N

    k = Szpieg(atrapa)
    k.wybierz_operatora("Technik A")
    a = atrapa.symuluj_skan("bez_numeru", gniazda={1: "zielony"})
    e = ekrany(k)
    e.klik("odp_zamknij_pytanie")  # "Pozniej": pytanie znika, plytka dalej bez numeru
    assert pokazana(e) == [] and e.aktywny("plytka_podaj_numer_plytki")
    zegar.przesun(2)
    b = atrapa.symuluj_skan("czysta", numer=3, projekty={n: 20 + n for n in range(1, 5)})
    assert e.okno.pokazana_plytka() == a  # plytka bez numeru ma jeszcze cos do zrobienia: ekran zostaje (S3-3)
    e.klik("plytka_podaj_numer_plytki")
    assert pokazana(e) == ["panel_numer_plytki"]
    assert N.TYTUL_ZE_SKANEM.format(tytul=ST.PRZYCISKI["podaj_numer_plytki"], godzina="19:00") in e.tekst_elementu("panel_numer_plytki")
    zegar.przesun(2)
    c = atrapa.symuluj_skan("czysta", numer=1, projekty={n: 10 + n for n in range(1, 5)})
    assert e.okno.pokazana_plytka() == a and pokazana(e) == ["panel_numer_plytki"] and e.okno._numer_dla == a
    e.klik("odp_podaj_numer_plytki_2")
    assert k.wyslane("podaj_numer_plytki") == [("podaj_numer_plytki", (a, 2))] and atrapa.stan().plytka(a).numer == 2
    assert pokazana(e) == [] and e.okno._numer_dla is None
    # "Zmien numer" plytki z numerem: tytul z numerem plytki; przelaczenie plytki przez technika zamyka wybor
    e.klik("plytka_podaj_numer_plytki")
    assert e.w("plytka_podaj_numer_plytki").text() == N.ZMIEN_NUMER and pokazana(e) == ["panel_numer_plytki"]
    assert N.PLYTKA_NR.format(numer=2) in e.tekst_elementu("panel_numer_plytki") and N.ZMIEN_NUMER_TYTUL in e.tekst_elementu("panel_numer_plytki")
    e.klik(f"plytka_{c}")
    assert e.okno.pokazana_plytka() == c and pokazana(e) == [] and e.okno._numer_dla is None
    assert {b, c} <= set(e.plytki())


def test_s3_3_pytanie_pokazanej_plytki_wstrzymuje_przelaczenie_na_nowy_wynik(atrapa, ekrany, zegar):
    """Otwarte pytanie pokazanej plytki (tu: plytka nie z trybu, bez prac z dozwolona decyzja) = ekran nie przelacza sie sam na nowy
    wynik - przyciski pytania nie zmieniaja plytki pod reka technika. Po odpowiedzi ekran przelacza sie jak dawniej."""
    k = Szpieg(atrapa)
    k.wybierz_operatora("Technik A")
    a = atrapa.symuluj_skan("nie_z_trybu", numer=4)
    e = ekrany(k)
    assert pokazana(e) == ["pytanie_plytka_nie_z_trybu"]
    zegar.przesun(2)
    b = atrapa.symuluj_skan("czysta", numer=1)
    assert e.okno.pokazana_plytka() == a and pokazana(e) == ["pytanie_plytka_nie_z_trybu"] and e.jest("przycisk_nowa_plytka")
    e.klik("odp_zamknij_pytanie")  # "Zeskanuje wlasciwa plytke"
    assert k.polecenia[-1] == ("zamknij_pytanie", (f"plytka_nie_z_trybu:{a}",)) and e.okno.pokazana_plytka() == a
    zegar.przesun(2)
    c = atrapa.symuluj_skan("czysta", numer=2, projekty={n: 10 + n for n in range(1, 5)})
    assert e.okno.pokazana_plytka() == c and b in e.plytki()  # pytania nie ma, nic do obejrzenia: nowy wynik zajmuje ekran sam


def test_s3_3_ochrona_strefy_gdy_pozycja_zmienia_sie_w_tle(atrapa, ekrany):
    """Pozycja strefy pytan podmieniona w tle (przyszedl wazniejszy komunikat) - przez ``OCHRONA_MS`` przyciski strefy nie przyjmuja
    klikniec (mysz i Enter), strefa jest przygaszona; potem dzialaja. Zmiana po kliknieciu technika ochrony nie wlacza."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    from stanowisko.ui import okno as O

    assert O.OCHRONA_MS == 800
    k = Szpieg(atrapa)
    k.wybierz_operatora("Technik A")
    atrapa.symuluj_skan("czysta")
    e = ekrany(k)
    pierwszy = atrapa.symuluj_komunikat("plik_zmieniony")
    assert pokazana(e) == ["komunikat_plik_zmieniony"] and not e.okno.ochrona_strefy_aktywna()  # strefa byla pusta: nie ma czego chronic
    punkt = srodek_w_oknie(e, "zamknij_komunikat")
    drugi = atrapa.symuluj_komunikat("start_skanu_nieudany")  # ostrzezenie staje przed informacja - w tym samym miejscu
    assert pokazana(e) == ["komunikat_start_skanu_nieudany"]
    assert e.okno.ochrona_strefy_aktywna() and e.okno.strefa.chroniona() and e.okno.ochrona_nakladek_aktywna()
    przed = list(k.polecenia)
    klik_w_punkcie(e, punkt)  # klikniecie wycelowane w "Zamknij" poprzedniego komunikatu
    QTest.mouseClick(e.w("zamknij_komunikat"), Qt.MouseButton.LeftButton)
    QTest.keyClick(e.w("zamknij_komunikat"), Qt.Key.Key_Return)
    assert e.okno.ochrona_strefy_aktywna(), "proba za wolna - klikniecia po czasie ochrony"
    e.odczekaj(10)
    assert k.polecenia == przed and pokazana(e) == ["komunikat_start_skanu_nieudany"]
    assert {x.id for x in atrapa.stan().komunikaty} >= {pierwszy.id, drugi.id}
    e.po_ochronie_nakladek()
    assert not e.okno.strefa.chroniona()
    e.klik("zamknij_komunikat")  # technik zamyka ostrzezenie: nastepna pozycja wchodzi po JEGO kliknieciu - bez ochrony
    assert k.polecenia[-1] == ("zamknij_komunikat", (drugi.id,))
    assert pokazana(e) == ["komunikat_plik_zmieniony"] and not e.okno.ochrona_strefy_aktywna() and not e.okno.strefa.chroniona()


# ----------------------------------------------------------------------------
# (1) S3-4: napis o ubytkach
# ----------------------------------------------------------------------------
def test_s3_4_program_nie_wskazal_ubytku_tylko_po_kontroli_z_wynikiem_ok(atrapa, ekrany):
    """Widok pracy: "Program nie wskazal ubytku." tylko, gdy kontrola byla i dala wynik "ok"; praca "nie sprawdzono", "blad kontroli",
    "bez projektu", bez kontroli albo z kontrola pominieta - "Tej pracy program nie sprawdzil."; praca z ubytkiem - rozmiar i liczba;
    inny wynik kontroli bez ubytkow - zadnego z tych zdan."""
    from stanowisko import statusy as ST
    from stanowisko.ui import napisy as N
    from stanowisko.ui.wieczor import WidokPracy

    atrapa.wybierz_operatora("Technik A")
    rodzaje = {1: "zielony", 2: "czerwony", 3: "nie_sprawdzono", 4: "blad_inspekcji", 5: "szary", 6: "zielony_bez_inspekcji", 7: "zielony_pominieto",
               8: "zolty", 9: "pomaranczowy", 10: "zielony_nowe_dopasowanie", 11: "zielony_nowa_inspekcja"}
    skan = atrapa.symuluj_skan("zwykla", gniazda=rodzaje)
    e = ekrany(atrapa)
    plytka = atrapa.stan().plytka(skan)
    oczekiwane = {1: N.BEZ_UBYTKOW, 3: N.NIE_SPRAWDZIL, 4: N.NIE_SPRAWDZIL, 5: N.NIE_SPRAWDZIL, 6: N.NIE_SPRAWDZIL, 7: N.NIE_SPRAWDZIL,
                  8: None, 9: None, 10: N.BEZ_UBYTKOW, 11: None}
    assert N.BEZ_UBYTKOW != N.NIE_SPRAWDZIL and "nie sprawdzi" in N.NIE_SPRAWDZIL and "nie wskaza" in N.BEZ_UBYTKOW
    for nr, napis in oczekiwane.items():
        e.klik_gniazdo(nr)
        praca = plytka.gniazdo(nr).praca
        widok = e.tekst_elementu("widok_pracy")
        if napis is None:
            assert not e.jest("praca_ubytek"), (nr, praca.status_inspekcji)
            assert N.BEZ_UBYTKOW not in widok and N.NIE_SPRAWDZIL not in widok, nr
        else:
            assert e.jest("praca_ubytek") and e.w("praca_ubytek").text() == napis, (nr, praca.status, praca.status_inspekcji, e.w("praca_ubytek").text())
            assert (N.BEZ_UBYTKOW if napis == N.NIE_SPRAWDZIL else N.NIE_SPRAWDZIL) not in widok, nr
        assert not e.jest("praca_liczba_ubytkow")
    assert [plytka.gniazdo(nr).status for nr in (3, 4, 5)] == ["nie_sprawdzono", "blad_inspekcji", "szary"]  # "nie sprawdzono", "blad kontroli", "bez projektu"
    e.klik_gniazdo(2)  # praca z ubytkiem: rozmiar najwiekszego ubytku i liczba, zadnego zdania o braku
    assert "0,62" in e.w("praca_ubytek").text() and e.w("praca_liczba_ubytkow").text() == N.LICZBA_UBYTKOW.format(n=1)
    assert N.BEZ_UBYTKOW not in e.tekst_elementu("widok_pracy") and N.NIE_SPRAWDZIL not in e.tekst_elementu("widok_pracy")
    # regula na samych danych stanu (takze kombinacje, ktorych atrapa nie podaje)
    praca = plytka.gniazdo(1).praca
    assert praca.status_inspekcji == ST.INSPEKCJA_ZIELONA and WidokPracy.napis_ubytkow(praca) == (N.BEZ_UBYTKOW, "")
    for zmiana in ({"status_inspekcji": None}, {"status_inspekcji": "pominieto"}, {"status_inspekcji": "nie_sprawdzono"}, {"blad_inspekcji": True},
                   {"kolor": ST.KOLOR_SZARY}):
        assert WidokPracy.napis_ubytkow(dataclasses.replace(praca, **zmiana)) == (N.NIE_SPRAWDZIL, ""), zmiana
    assert WidokPracy.napis_ubytkow(dataclasses.replace(praca, status_inspekcji="status_z_przyszlosci")) == ("", "")
    assert WidokPracy.napis_ubytkow(dataclasses.replace(praca, ubytki=2, ubytek_max_mm=None)) == (N.LICZBA_UBYTKOW.format(n=2), "")
    assert WidokPracy.napis_ubytkow(None) == ("", "")


# ----------------------------------------------------------------------------
# (1) S3-14: mapa poprzedniej plytki w czasie analizy nowego skanu
# ----------------------------------------------------------------------------
def test_s3_14_mapa_poprzedniej_plytki_w_czasie_analizy_nowego_skanu(atrapa, ekrany):
    """Trwa analiza nowego skanu (albo skan czeka w kolejce): mapa na ekranie jest mapa POPRZEDNIEJ plytki - znak "POPRZEDNIA PLYTKA"
    w naglowku plytki i przygaszona mapa. Znak nie rusza mapy, a klikniecia dzialaja (to nie ochrona): technik moze konczyc
    poprzednia plytke. Po wyniku znak znika."""
    from stanowisko.ui import napisy as N

    k = Szpieg(atrapa)
    k.wybierz_operatora("Technik A")
    skan = atrapa.symuluj_skan("zwykla")
    e = ekrany(k)
    plytka = atrapa.stan().plytka(skan)
    miejsce = e.okno.miejsce_mapy()
    assert not e.mapa.poprzednia() and not e.jest("mapa_poprzednia") and e.kolory_pikseli()[2] == plytka.gniazdo(2).rgb
    atrapa.symuluj_postep(udzial=0.3)  # analiza nowego skanu
    assert e.mapa.poprzednia() and e.jest("mapa_poprzednia") and e.w("mapa_poprzednia").text() == N.MAPA_POPRZEDNIA
    assert N.MAPA_POPRZEDNIA.startswith("POPRZEDNIA") and e.okno.naglowek_pole.isAncestorOf(e.w("mapa_poprzednia"))
    e.zdarzenia()
    assert e.okno.miejsce_mapy() == miejsce and not UW.sprawdz_uklad(e, UW.ROZMIAR_OKNA)
    obraz = e.mapa.grab().toImage()
    for g in plytka.gniazda:  # mapa przygaszona: zaden piksel gniazda nie ma juz pelnego koloru statusu
        if g.prace:
            assert obraz.pixelColor(e.mapa.punkt_probny(g.nr).toPoint()).name() != g.rgb, g.nr
    assert not e.okno.ochrona_aktywna() and not e.mapa.przygaszona()  # to nie jest ochrona klikniec
    e.klik_gniazdo(2)
    e.klik("przycisk_ukruszona")
    assert atrapa.stan().plytka(skan).gniazdo(2).praca.decyzja == "ukruszona"  # decyzje dla poprzedniej plytki dzialaja
    atrapa.symuluj_postep(udzial=None)
    assert not e.mapa.poprzednia() and not e.jest("mapa_poprzednia") and e.kolory_pikseli()[9] == plytka.gniazdo(9).rgb
    atrapa.symuluj_kolejke(czeka=1)  # skan czeka w kolejce (analiza jeszcze nie ruszyla)
    assert e.mapa.poprzednia() and e.jest("mapa_poprzednia")
    atrapa.symuluj_kolejke()
    assert not e.mapa.poprzednia() and e.okno.miejsce_mapy() == miejsce


def test_s3_14_bez_plytki_nie_ma_znaku_poprzedniej(atrapa, ekrany):
    e = ekrany(atrapa)
    atrapa.symuluj_postep(udzial=0.5)
    assert not e.mapa.poprzednia() and not e.jest("mapa_poprzednia") and e.mapa.numery() == []


# ----------------------------------------------------------------------------
# (1) S3-15: powrot z trybu rano, pozycja listy, klawisz N
# ----------------------------------------------------------------------------
def test_s3_15_powrot_z_trybu_rano_zeruje_kursor_i_wlacza_ochrone(atrapa, ekrany):
    """Po powrocie z trybu "Poranek": kursor gniazda wyzerowany, mapa przygaszona na ``OCHRONA_MS`` - klawisz N, Enter i klikniecie
    mapy sa pomijane; potem dzialaja."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    k = Szpieg(atrapa)
    k.wybierz_operatora("Technik A")
    atrapa.symuluj_skan("zwykla")
    e = ekrany(k)
    e.klawisz(Qt.Key.Key_Right)
    assert e.mapa.kursor() == 2
    e.klik("przycisk_tryb_rano")
    assert e.okno.rano() and atrapa.stan().tryb == "rano"
    e.klik("przycisk_tryb_wieczor")
    assert not e.okno.rano() and e.mapa.numery()
    assert e.mapa.kursor() is None and e.okno._kursor is None
    assert e.okno.ochrona_aktywna() and e.mapa.przygaszona()
    przed = list(k.polecenia)
    QTest.keyClick(e.okno, Qt.Key.Key_N)
    QTest.keyClick(e.okno, Qt.Key.Key_Return)
    QTest.mouseClick(e.mapa, Qt.MouseButton.LeftButton, pos=e.mapa.srodek_gniazda(2).toPoint())
    assert e.okno.ochrona_aktywna(), "proba za wolna - klawisze po czasie ochrony"
    e.odczekaj(10)
    assert not e.jest("widok_pracy") and k.polecenia == przed and e.okno._gniazdo is None
    e.po_ochronie()
    e.klawisz(Qt.Key.Key_N)
    assert e.jest("widok_pracy") and e.okno._gniazdo == 2


def test_s3_15_klawisz_n_pod_ochrona_i_pozycja_listy_otwiera_dokladnie_te_prace(atrapa, ekrany, zegar):
    """Klawisz N tuz po zmianie mapy (technik przelaczyl plytke) jest pomijany. Pozycja listy "do dofrezowania" otwiera prace o swoim
    ``praca_id`` - w gniezdzie z dwiema pracami druga, nie pierwsza."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    from stanowisko import kontroler_api as K
    from stanowisko.ui import napisy as N

    atrapa.wybierz_operatora("Technik A")
    a = atrapa.symuluj_skan("zwykla", numer=1)
    zegar.przesun(2)
    b = atrapa.symuluj_skan("zwykla", numer=2, projekty={n: 10 + n for n in range(1, 10)})
    e = ekrany(atrapa)
    assert e.okno.pokazana_plytka() == b
    e.klik(f"plytka_{a}")
    assert e.okno.pokazana_plytka() == a and e.okno.ochrona_aktywna()
    QTest.keyClick(e.okno, Qt.Key.Key_N)
    assert e.okno.ochrona_aktywna(), "proba za wolna"
    assert not e.jest("widok_pracy") and e.okno._gniazdo is None
    e.klawisz(Qt.Key.Key_N)  # po ochronie
    assert e.jest("widok_pracy") and e.okno._gniazdo == 2
    e.klawisz(Qt.Key.Key_Escape)
    zegar.przesun(2)
    c = atrapa.symuluj_skan("do_powtorzenia", numer=3, gniazda={1: "zielony", 3: "podwojny"}, projekty={1: 41, 3: 43})
    stan = atrapa.stan()
    pierwsza, druga = stan.plytka(c).gniazdo(3).prace
    pozycja = K.PozycjaListy(praca_id=druga.praca_id, skan_id=c, numer_plytki=3, gniazdo=3, kuweta=None, zeby=None, krazek=None, sha16=None,
                             doba=stan.doba, zmiana=stan.zmiana)
    e.okno._klik_pozycja(pozycja)
    e.odczekaj(20)
    assert e.okno.pokazana_plytka() == c and e.okno.widok.praca_id == druga.praca_id != pierwsza.praca_id
    assert e.w("przycisk_inna_praca").text() == N.PRACA_Z_DWOCH.format(nr=2, ile=2)
    e.okno._klik_pozycja(dataclasses.replace(pozycja, praca_id=pierwsza.praca_id))
    e.odczekaj(20)
    assert e.okno.widok.praca_id == pierwsza.praca_id and e.w("przycisk_inna_praca").text() == N.PRACA_Z_DWOCH.format(nr=1, ile=2)


# ----------------------------------------------------------------------------
# (2) strefa pytan i komunikatow
# ----------------------------------------------------------------------------
def test_strefa_jedna_pozycja_naraz_i_licznik_i_jeszcze_n(atrapa, ekrany):
    """Strefa pokazuje jedna pozycje; pozostale sa pod licznikiem "i jeszcze n" - klikniecie licznika pokazuje nastepna (po ostatniej
    znowu pierwsza) i niczego nie wysyla do kontrolera. Kolejnosc: ostrzezenia przed informacjami, w poziomie od najnowszego.
    Zmiana zestawu pozycji (zamkniecie, nowy komunikat) = strefa wraca do pierwszej."""
    from stanowisko.ui import napisy as N

    k = Szpieg(atrapa)
    k.wybierz_operatora("Technik A")
    atrapa.symuluj_skan("czysta")
    e = ekrany(k)
    assert pokazana(e) == [] and e.jest("strefa_pusta") and e.w("strefa_pusta").text() == N.STREFA_PUSTA and not e.jest("uwagi_jeszcze")
    atrapa.symuluj_komunikat("plik_zmieniony")
    juz_jest = atrapa.symuluj_komunikat("skan_juz_jest")
    atrapa.symuluj_komunikat("start_skanu_nieudany")
    assert e.strefa() == ["komunikat_start_skanu_nieudany", "komunikat_skan_juz_jest", "komunikat_plik_zmieniony"]
    assert pokazana(e) == ["komunikat_start_skanu_nieudany"] and not e.jest("strefa_pusta")
    assert e.w("uwagi_jeszcze").text() == N.JESZCZE_KROTKO.format(n=2)
    przed = list(k.polecenia)
    kolejne = []
    for _ in range(3):
        e.klik("uwagi_jeszcze")
        kolejne += pokazana(e)
    assert kolejne == ["komunikat_skan_juz_jest", "komunikat_plik_zmieniony", "komunikat_start_skanu_nieudany"] and k.polecenia == przed
    e.klik("uwagi_jeszcze")
    assert pokazana(e) == ["komunikat_skan_juz_jest"]
    e.klik("zamknij_komunikat")  # zamkniecie przegladanej pozycji: zestaw sie zmienil - strefa wraca do najwazniejszej
    assert k.polecenia[-1] == ("zamknij_komunikat", (juz_jest.id,))
    assert pokazana(e) == ["komunikat_start_skanu_nieudany"] and e.w("uwagi_jeszcze").text() == N.JESZCZE_KROTKO.format(n=1)
    e.klik("uwagi_jeszcze")
    assert pokazana(e) == ["komunikat_plik_zmieniony"]
    atrapa.symuluj_komunikat("lista_nie_zapisana")  # nowy komunikat: strefa wraca do pierwszej pozycji (najnowsze ostrzezenie)
    assert pokazana(e) == ["komunikat_lista_nie_zapisana"] and e.w("uwagi_jeszcze").text() == N.JESZCZE_KROTKO.format(n=2)


@pytest.mark.parametrize("rozmiar", ROZMIARY)
def test_strefa_ma_stala_wysokosc_dlugi_tekst_przewijany_przyciski_widoczne(atrapa, ekrany, rozmiar):
    """Wysokosc strefy nie zalezy od tresci (pusta, komunikat, bardzo dlugi komunikat) - mapa nie zmienia miejsca. Tekst, ktory sie nie
    miesci, jest przewijany WEWNATRZ pozycji (nic nie jest uciete bez paska), a jej przyciski zostaja widoczne w strefie."""
    k = Szpieg(atrapa)
    k.wybierz_operatora("Technik A")
    atrapa.symuluj_skan("czysta")
    e = ekrany(k, rozmiar)
    u = e.okno.uklad()
    miejsce = e.okno.miejsce_mapy()

    def stale() -> bool:
        e.zdarzenia()
        e.odczekaj(20)
        return e.w("strefa_komunikatow").height() == u.strefa and e.okno.miejsce_mapy() == miejsce

    assert stale()
    atrapa.symuluj_komunikat("plik_zmieniony")
    assert stale() and pokazana(e) == ["komunikat_plik_zmieniony"]
    atrapa.symuluj_komunikat("odmowa", powod=DLUGI_TEKST * 4)  # kilkanascie wierszy takze w srodku okna 1920 x 1080
    assert stale() and pokazana(e) == ["komunikat_odmowa"]
    panel = e.okno.strefa.panele()[0]
    strefa = _w_oknie(e.okno, e.w("strefa_komunikatow"))
    assert strefa.contains(_w_oknie(e.okno, panel))
    assert panel.przewijanie.verticalScrollBar().maximum() > 0  # dlugi tekst: pasek przewijania w pozycji
    for b in panel.przyciski + [panel.przycisk_licznika]:
        assert b.isVisibleTo(e.okno) and strefa.contains(_w_oknie(e.okno, b)) and b.height() >= b.sizeHint().height() - 1, b.objectName()
    assert not UW.sprawdz_uklad(e, rozmiar)
    e.klik("zamknij_komunikat")
    e.klik("zamknij_komunikat")
    assert pokazana(e) == [] and stale()


@pytest.mark.parametrize("rozmiar", ROZMIARY + ((1240, 640),))
@pytest.mark.parametrize("pytanie", ["ponowny_skan", "plytka_nie_z_trybu", "brak_numeru_plytki"])
def test_pytania_mieszcza_sie_w_strefie_bez_przewijania(atrapa, ekrany, zegar, rozmiar, pytanie):
    """Kazde pytanie wieczorne (ponowny skan z ostrzezeniem o decyzjach, plytka nie z trybu z rada, numer plytki z cyframi) miesci sie
    w strefie w calosci: bez paska przewijania, z przyciskami odpowiedzi widocznymi w strefie - przy kazdym rozmiarze okna."""
    atrapa.wybierz_operatora("Technik A")
    if pytanie == "ponowny_skan":
        pierwszy = atrapa.symuluj_skan("zwykla", numer=1)
        plytka = atrapa.stan().plytka(pierwszy)
        atrapa.ukruszona(plytka.gniazdo(2).praca.praca_id)
        atrapa.ok(plytka.gniazdo(9).praca.praca_id)
        atrapa.ok(plytka.gniazdo(3).praca.praca_id)
        zegar.przesun(5)
        atrapa.symuluj_skan("zwykla", numer=1)
    elif pytanie == "plytka_nie_z_trybu":
        atrapa.symuluj_skan("nie_z_trybu", numer=4)
    else:
        atrapa.symuluj_skan("bez_numeru")
    e = ekrany(atrapa, rozmiar)
    assert pokazana(e) == [f"pytanie_{pytanie}"]
    e.odczekaj(30)
    panel = e.okno.strefa.panele()[0]
    strefa = _w_oknie(e.okno, e.w("strefa_komunikatow"))
    pasek = panel.przewijanie.verticalScrollBar()
    assert pasek.maximum() == 0, f"{pytanie} {rozmiar}: tekst pytania wymaga przewijania o {pasek.maximum()} px"
    assert len(panel.przyciski) >= 2
    for b in panel.przyciski:
        assert b.isVisibleTo(e.okno) and strefa.contains(_w_oknie(e.okno, b)), (pytanie, rozmiar, b.objectName())
    if pytanie == "ponowny_skan":
        assert e.jest("pytanie_ostrzezenie") and strefa.contains(_w_oknie(e.okno, e.w("pytanie_ostrzezenie")))  # ostrzezenie o decyzjach w calosci
    assert not UW.sprawdz_uklad(e, rozmiar)


# ----------------------------------------------------------------------------
# (3) nakladki: lista osob, lista bledow
# ----------------------------------------------------------------------------
def test_lista_osob_rozwija_sie_pod_paskiem_gornym_bez_okna_modalnego(atrapa, ekrany):
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication

    from stanowisko.ui import napisy as N

    k = Szpieg(atrapa)
    atrapa.symuluj_skan("zwykla")
    e = ekrany(k)
    panel = e.w("panel_osoba")
    assert e.jest("panel_osoba") and panel.parentWidget() is e.okno and not panel.isWindow()  # czesc okna, nie osobne okno
    assert QApplication.activeModalWidget() is None and not e.okno.isModal()
    r, pasek = _w_oknie(e.okno, panel), _w_oknie(e.okno, e.w("pasek_gorny"))
    assert pasek.bottom() < r.top() <= pasek.bottom() + 8 and e.okno.width() - 24 <= r.right() < e.okno.width()  # pod paskiem, po prawej (przy osobie)
    assert not r.intersects(_w_oknie(e.okno, e.okno.widok.decyzje)) and not r.intersects(e.okno.miejsce_mapy())
    assert N.KTO_PRACUJE in e.tekst_elementu("panel_osoba") and not e.jest("przycisk_zmien_osobe")
    miejsce = e.okno.miejsce_mapy()
    e.klik("osoba_0")
    assert not e.jest("panel_osoba") and e.okno.miejsce_mapy() == miejsce and e.w("napis_osoba").text() == "Technik A"
    e.klik("przycisk_zmien_osobe")
    assert e.jest("panel_osoba") and N.ZMIANA_OSOBY in e.tekst_elementu("panel_osoba") and e.w("osoba_0").isChecked() and not e.w("osoba_1").isChecked()
    assert e.okno.miejsce_mapy() == miejsce and not UW.sprawdz_uklad(e, UW.ROZMIAR_OKNA)
    e.klawisz(Qt.Key.Key_Escape)  # Esc zamyka liste otwarta przez technika
    assert not e.jest("panel_osoba")
    e.klik("przycisk_zmien_osobe")
    e.klik("osoba_bez_zmian")
    assert not e.jest("panel_osoba") and k.wyslane("wybierz_operatora") == [("wybierz_operatora", ("Technik A",))]
    e.klik("przycisk_zmien_osobe")
    e.klik("osoba_1")
    assert k.polecenia[-1] == ("wybierz_operatora", ("Technik B",)) and e.w("napis_osoba").text() == "Technik B" and not e.jest("panel_osoba")


def test_lista_bledow_rozwijana_z_licznika_na_pasku_stanu(atrapa, ekrany):
    """Bledy programu: licznik na pasku stanu i lista nad paskiem. Nowy blad sam rozwija liste (i przez ``OCHRONA_MS`` jej przyciski
    nie przyjmuja klikniec); technik zwija ja licznikiem - zostaje zwinieta do nastepnego NOWEGO bledu. Lista nie zabiera miejsca
    mapie i nie zaslania mapy, strefy pytan ani kolumny "Praca"."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QPushButton

    from stanowisko.ui import napisy as N

    k = Szpieg(atrapa)
    k.wybierz_operatora("Technik A")
    atrapa.symuluj_skan("czysta")
    e = ekrany(k)
    miejsce = e.okno.miejsce_mapy()
    assert not e.jest("przycisk_bledy") and not e.jest("lista_bledow")
    atrapa.symuluj_skaner(dostepny=False)
    assert e.jest("lista_bledow") and e.w("przycisk_bledy").text() == N.BLEDY_PROGRAMU.format(n=1)
    assert e.okno.pasek_stanu.isAncestorOf(e.w("przycisk_bledy")) and e.w("lista_bledow").parentWidget() is e.okno
    assert [p.objectName() for p in e.okno.bledy.panele()] == ["komunikat_folder_skanera_niedostepny"] and pokazana(e) == []
    e.zdarzenia()
    lista = _w_oknie(e.okno, e.w("lista_bledow"))
    assert lista.bottom() < _w_oknie(e.okno, e.w("pasek_stanu")).top() and e.okno.rect().contains(lista)
    for nazwa in ("mapa", "strefa_komunikatow", "ramka_pracy"):
        assert not lista.intersects(_w_oknie(e.okno, e.w(nazwa))), nazwa
    assert e.okno.miejsce_mapy() == miejsce
    zamknij = e.okno.bledy.findChild(QPushButton, "zamknij_komunikat")
    assert e.okno.bledy.chroniona() and e.okno.ochrona_nakladek_aktywna()  # lista pojawila sie w tle: ochrona klikniec
    przed = list(k.polecenia)
    QTest.mouseClick(zamknij, Qt.MouseButton.LeftButton)
    klik_w_punkcie(e, _w_oknie(e.okno, zamknij).center())
    assert e.okno.bledy.chroniona(), "proba za wolna - klikniecia po czasie ochrony"
    assert k.polecenia == przed and e.jest("lista_bledow")
    e.po_ochronie_nakladek()
    e.klik("przycisk_bledy")  # technik zwija liste: licznik zostaje
    assert not e.jest("lista_bledow") and e.jest("przycisk_bledy") and e.okno.miejsce_mapy() == miejsce
    atrapa.symuluj_komunikat("plik_zmieniony")  # zwykly komunikat idzie do strefy i nie rozwija listy bledow
    assert not e.jest("lista_bledow") and pokazana(e) == ["komunikat_plik_zmieniony"]
    atrapa.symuluj_blad_zapisu(1)  # NOWY blad: lista rozwija sie sama
    assert e.jest("lista_bledow") and e.w("przycisk_bledy").text() == N.BLEDY_PROGRAMU.format(n=2)
    assert {p.objectName() for p in e.okno.bledy.panele()} == {"komunikat_blad_zapisu", "komunikat_folder_skanera_niedostepny"}
    assert not UW.sprawdz_uklad(e, UW.ROZMIAR_OKNA)
    e.klik("komunikat_ponow_zapis")  # przyczyna trwa: odmowa, blad zostaje na liscie
    assert k.polecenia[-1] == ("ponow_zapis", ()) and e.jest("komunikat_blad_zapisu")
    atrapa.symuluj_skaner(dostepny=True)
    assert e.w("przycisk_bledy").text() == N.BLEDY_PROGRAMU.format(n=1)
    atrapa.symuluj_blad_zapisu(0)  # dysk wrocil: ponowienie zapisuje skan - bledow nie ma, licznik i lista znikaja
    e.klik("komunikat_ponow_zapis")
    assert not e.jest("przycisk_bledy") and not e.jest("lista_bledow") and e.okno.miejsce_mapy() == miejsce


# ----------------------------------------------------------------------------
# (4) szkielet: przelacznik trybu, wersja, pasek stanu, blysk
# ----------------------------------------------------------------------------
def test_przelacznik_trybu_idzie_za_stanem_programu(atrapa, ekrany):
    from stanowisko import kontroler_api as K

    k = Szpieg(atrapa)
    e = ekrany(k)
    e.klik("przycisk_tryb_rano")
    assert k.polecenia[-1] == ("przelacz_tryb", ("rano",)) and e.okno.rano()
    assert e.w("przycisk_tryb_rano").isChecked() and not e.w("przycisk_tryb_wieczor").isChecked()
    assert e.jest("ekran_rano") and e.jest("pasek_gorny") and e.jest("pasek_stanu") and not e.jest("lista_plytek")  # paski wspolne dla obu trybow
    e.klik("przycisk_tryb_rano")  # klikniecie wybranej czesci niczego nie wysyla
    assert len(k.wyslane("przelacz_tryb")) == 1 and e.w("przycisk_tryb_rano").isChecked()
    e.klik("przycisk_tryb_wieczor")
    assert k.polecenia[-1] == ("przelacz_tryb", ("wieczor",)) and not e.okno.rano() and e.jest("lista_plytek")
    assert e.w("przycisk_tryb_wieczor").isChecked() and not e.w("przycisk_tryb_rano").isChecked()
    # polecenie odrzucone: przelacznik zostaje przy trybie ze stanu (wyglad idzie za stanem, nie za kliknieciem)
    odmowa = Podstawiony(atrapa, {"przelacz_tryb": K.Odpowiedz(False, "Trybu nie mozna teraz zmienic - tekst z kontrolera.", "odmowa")})
    e2 = ekrany(odmowa)
    e2.klik("przycisk_tryb_rano")
    assert not e2.okno.rano() and e2.w("przycisk_tryb_wieczor").isChecked() and not e2.w("przycisk_tryb_rano").isChecked()
    assert e2.jest("komunikat_odpowiedz") and "tekst z kontrolera" in e2.tekst_elementu("komunikat_odpowiedz")


def test_wersja_programu_na_pasku_stanu(atrapa, ekrany):
    from stanowisko.ui import napisy as N
    from stanowisko.ui import okno as O

    wersja = (STANOWISKO / "WERSJA").read_text(encoding="ascii").strip()
    assert wersja and O.wersja_programu() == wersja
    e = ekrany(atrapa)
    assert e.jest("napis_wersja") and e.w("napis_wersja").text() == N.WERSJA.format(wersja=wersja)
    assert e.okno.pasek_stanu.isAncestorOf(e.w("napis_wersja")) and O.PLIK_WERSJI not in e.tekst(tylko_widoczne=False)
    assert UW.bez_sciezek(e) > 10


@pytest.mark.parametrize("rozmiar", ROZMIARY)
def test_pasek_stanu_bez_skrotow_w_zwyklej_pracy(atrapa, ekrany, rozmiar):
    """Zwykla praca (czekanie na plik skanu, analiza z jednym skanem w kolejce, liczenie puli, jeden blad programu): przy 1920 x 1080,
    1536 x 864 i 1280 x 720 zadne pole paska stanu nie jest skrocone ani uciete (pelna kontrola ukladu, bez taryfy dla dlugich pol)."""
    from PySide6.QtCore import Qt

    atrapa.wybierz_operatora("Technik A")
    atrapa.symuluj_skan("zwykla")
    e = ekrany(atrapa, rozmiar)
    assert not UW.sprawdz_uklad(e, rozmiar)
    e.klawisz(Qt.Key.Key_Space)
    assert not UW.sprawdz_uklad(e, rozmiar)
    for krok in (lambda: atrapa.symuluj_postep(udzial=0.4, czeka=1), lambda: atrapa.symuluj_pule("liczenie"), lambda: atrapa.symuluj_skaner(dostepny=False)):
        krok()
        usterki = UW.sprawdz_uklad(e, rozmiar)
        assert not usterki, f"{rozmiar}:\n" + "\n".join(usterki)
    assert e.w("pasek_stanu").height() == 32


def test_pole_paska_stanu_skracane_ma_pelny_napis_w_podpowiedzi(atrapa, ekrany):
    """Dlugie pole paska stanu, ktore sie nie miesci, jest skracane z wielokropkiem; ``text()`` i podpowiedz maja pelny napis."""
    from PySide6.QtWidgets import QLabel

    from stanowisko.ui import czesci as C

    e = ekrany(atrapa)
    pole = C.EtykietaSkracana("stan_wartosc", "pole_proby")
    pole.setParent(e.okno)
    pelny = "wpisow puli: 412 - buduje pule: 12 z 400 (analiza czeka) - bardzo dlugi napis ze stanu programu"
    pole.setText(pelny)
    pole.setToolTip("podpowiedz pola")
    pole.setGeometry(10, 60, 150, 20)
    pole.show()
    e.zdarzenia()
    assert pole.skrocona() and pole.text() == pelny and QLabel.text(pole) != pelny and QLabel.text(pole).endswith("…")
    assert pelny in pole.toolTip() and "podpowiedz pola" in pole.toolTip()
    pole.setGeometry(10, 60, 900, 20)
    e.zdarzenia()
    assert not pole.skrocona() and QLabel.text(pole) == pelny and pole.toolTip() == "podpowiedz pola"
    pole.hide()
    pole.setParent(None)


def test_blysk_paska_gornego_gdy_nowy_wynik_czeka(atrapa, ekrany, zegar, monkeypatch):
    from stanowisko.ui import czesci as C

    monkeypatch.setattr(C, "BLYSK_MS", 200)
    atrapa.wybierz_operatora("Technik A")
    a = atrapa.symuluj_skan("zwykla", numer=1)
    e = ekrany(atrapa)
    assert e.w("pasek_gorny").property("blysk") == "false"
    zegar.przesun(2)
    atrapa.symuluj_skan("czysta", numer=2, projekty={n: 10 + n for n in range(1, 5)})
    assert e.okno.pokazana_plytka() == a and e.jest("przycisk_nowa_plytka") and e.w("pasek_gorny").property("blysk") == "true"
    e.czekaj(lambda: e.w("pasek_gorny").property("blysk") == "false", 3.0, "koniec blysku paska")
    assert e.w("pasek_gorny").height() == 52


# ----------------------------------------------------------------------------
# (5) przycisk ze skrotem w ramce; status nie tylko barwa
# ----------------------------------------------------------------------------
def test_przyciski_ze_skrotem_klawiszowym_w_ramce(atrapa, ekrany):
    """Przyciski ze skrotem: napis po lewej, skrot w ramce po prawej stronie przycisku (SPEC p. 2); ``text()`` zostaje pelnym napisem
    "Napis  [K]" jak w ``napisy`` (instrukcje cytuja te napisy)."""
    from stanowisko import statusy as ST
    from stanowisko.ui import czesci as C
    from stanowisko.ui import motyw
    from stanowisko.ui import napisy as N

    atrapa.wybierz_operatora("Technik A")
    atrapa.symuluj_skan("zwykla")
    e = ekrany(atrapa)
    e.klik_gniazdo(2)
    oczekiwane = {"przycisk_ukruszona": (ST.PRZYCISKI["ukruszona"], N.KLAWISZ_UKRUSZONA), "przycisk_ok": (ST.PRZYCISKI["ok"], N.KLAWISZ_OK),
                  "przycisk_cofnij": (ST.PRZYCISKI["cofnij"], N.KLAWISZ_COFNIJ), "przycisk_nastepna": (N.NASTEPNA.split("[")[0].strip(), "N"),
                  "przycisk_zamknij_prace": (N.ZAMKNIJ_PRACE.split("[")[0].strip(), "Esc"),
                  "przycisk_skanuj": (N.SKANUJ_ATRAPA.split("[")[0].strip(), "Spacja")}
    for nazwa, (napis, skrot) in oczekiwane.items():
        b = e.w(nazwa)
        assert isinstance(b, C.PrzyciskSkrotu) and b.czesci() == (napis, skrot), (nazwa, b.czesci())
        assert b.text().startswith(napis) and b.text().endswith(f"[{skrot}]")
        assert b.width() >= b.sizeHint().width() - 1 and b.height() >= b.sizeHint().height() - 1  # napis i ramka skrotu sie mieszcza
    # ramka skrotu jest narysowana po prawej stronie przycisku: ciemna ramka na czerwonym "Ukruszona", napis zaczyna sie z lewej
    b = e.w("przycisk_ukruszona")
    obraz = b.grab().toImage()
    tlo = ST.STATUSY["ukruszona"].hex
    assert obraz.pixelColor(b.width() // 2, 4).name() == tlo  # wypelnienie czerwonym statusu ze ``statusy``
    kolumny = sorted({x for x in range(b.width()) for y in range(4, b.height() - 4) if obraz.pixelColor(x, y).name() == motyw.NA_STATUSIE})
    assert kolumny and kolumny[0] < 30 and kolumny[-1] > b.width() - 24  # napis od lewej krawedzi, ramka skrotu przy prawej
    przerwy = [(b2 - a2, a2, b2) for a2, b2 in zip(kolumny, kolumny[1:])]
    najwieksza = max(przerwy)
    assert najwieksza[0] >= 10 and najwieksza[2] > b.width() - 50  # miedzy napisem a ramka skrotu jest przerwa; ramka stoi po prawej stronie
    assert C.PrzyciskSkrotu("Bez skrotu").czesci() == ("Bez skrotu", "") and C.PrzyciskSkrotu("Rozlozona [Enter]").czesci() == ("Rozlozona", "Enter")


def test_status_na_mapie_w_legendzie_i_na_kafelku_nie_tylko_barwa(atrapa, ekrany):
    """SPEC p. 2: gniazdo z ubytkiem ma jasna obwodke 2 px, puste gniazdo - obwodke przerywana bez wlasnego wypelnienia, wybrane -
    pierscien akcentu; w legendzie i na kafelku plytki przy kolorze zawsze stoi NAPIS statusu i liczba."""
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QLabel

    from stanowisko import statusy as ST
    from stanowisko.ui import motyw
    from stanowisko.ui import napisy as N

    atrapa.wybierz_operatora("Technik A")
    skan = atrapa.symuluj_skan("zwykla")  # 1 zielone, 2 i 9 czerwone, 3-7 zolte / szare / pomaranczowe, 8 zielone, 10-19 puste
    e = ekrany(atrapa)
    plytka = atrapa.stan().plytka(skan)
    for g in plytka.gniazda:
        wyglad = e.mapa.wyglad_gniazda(g.nr)
        assert wyglad["obwodka_ubytku"] == (g.kolor == ST.KOLOR_CZERWONY) and wyglad["puste"] == (not g.prace), g.nr
        assert not wyglad["wybrane"] and not wyglad["kursor"]
    srodek_plytki = e.mapa.obrys_plytki().boundingRect().center()

    def obok(obraz, nr: int, od: float, do: float) -> set:
        """Kolory pikseli w odleglosci ``od`` - ``do`` px za krawedzia gniazda ``nr`` (w strone srodka plytki, co cwierc piksela)."""
        import math

        s, promien = e.mapa.srodek_gniazda(nr), e.mapa._ksztalt(nr)[2]
        dx, dy = srodek_plytki.x() - s.x(), srodek_plytki.y() - s.y()
        d = math.hypot(dx, dy) or 1.0
        kroki = [od + 0.25 * i for i in range(int((do - od) / 0.25) + 1)]
        return {obraz.pixelColor(round(s.x() + dx / d * (promien + k)), round(s.y() + dy / d * (promien + k))).name() for k in kroki}

    e.po_ochronie()
    obraz = e.mapa.grab().toImage()
    plytka_tlo, jasna = motyw.WGLEBIENIE.lower(), motyw.OBWODKA_UBYTKU.lower()
    assert jasna in obok(obraz, 2, 0.5, 2.0) and jasna in obok(obraz, 9, 0.5, 2.0)  # czerwone: jasna obwodka tuz za krawedzia gniazda
    assert obok(obraz, 2, 4.0, 6.0) == {plytka_tlo}  # obwodka ma 2 px - dalej juz plytka
    for nr in (1, 3, 4, 8):  # pozostale gniazda z praca: bez obwodki
        assert jasna not in obok(obraz, nr, 0.5, 6.0) and plytka_tlo in obok(obraz, nr, 1.0, 3.0), nr
    assert e.kolory_pikseli()[12] == ST.STATUSY["pusty"].hex == plytka_tlo  # puste gniazdo: bez wlasnego wypelnienia (kolor plytki)
    e.klik_gniazdo(1)
    obraz = e.mapa.grab().toImage()
    assert e.mapa.wyglad_gniazda(1)["wybrane"]
    assert motyw.AKCENT.lower() in obok(obraz, 1, 3.0, 5.0) and plytka_tlo in obok(obraz, 1, 0.75, 2.5)  # pierscien akcentu z przerwa w kolorze plytki
    assert motyw.AKCENT.lower() not in obok(obraz, 3, 0.5, 6.0)
    e.klawisz(Qt.Key.Key_Escape)
    e.klawisz(Qt.Key.Key_Right)
    assert e.mapa.wyglad_gniazda(e.mapa.kursor())["kursor"]
    # legenda: napis, kolor i liczba dla kazdego statusu obecnego na plytce; puste gniazda osobna pozycja z napisem
    pozycje = e.okno.legenda.pozycje()
    assert (ST.STATUSY["czerwony"].napis, ST.STATUSY["czerwony"].hex, 2) in pozycje and (ST.STATUSY["zielony"].napis, ST.STATUSY["zielony"].hex, 2) in pozycje
    assert pozycje[-1] == (N.LEGENDA_PUSTE, None, 10) and sum(n for _, _, n in pozycje) == 19
    legenda = e.tekst_elementu("legenda")
    assert N.LEGENDA in legenda and all(napis in legenda for napis, _, _ in pozycje)
    # kafelek plytki: licznik = kropka + napis statusu + liczba
    napisy = [w.text() for w in e.w(f"plytka_{skan}").findChildren(QLabel)]
    assert N.LICZNIK.format(napis=ST.STATUSY["czerwony"].napis, n=2) in napisy and N.LICZNIK.format(napis=ST.STATUSY["zielony"].napis, n=2) in napisy
