"""E3-P15 p. 1: komunikat ogolny, ktory przychodzi w trakcie ogladania plytki, nie moze podstawic innego gniazda pod kursor.

Stare okno (paczka E3-P15): komunikat ogolny (bez ``skan_id``, np. "Ten sam projekt w dwoch gniazdach") stawal NAD lista
plytek i mapa - mapa ogladanej plytki przesuwala sie i malala, wiec po kazdym takim ruchu wlaczala sie ochrona klikniec A-P2
(``okno.OCHRONA_MS``). Nowe okno (E3-U1a, ``etap3/nowy_interfejs/SPEC.md``): MAPA NIGDY SIE NIE PRZESUWA - strefa pytan,
naglowek plytki i lista "do dofrezowania" maja stale wysokosci, a lista bledow programu jest nakladka. Kryterium jest wiec
mocniejsze niz w E3-P15: po kazdym komunikacie (z tla i jako skutek polecenia technika) prostokat mapy w oknie
(``okno.miejsce_mapy()``) i srodki 19 gniazd sa te same, ochrona mapy NIE wlacza sie (mapa nie jest przygaszona, klikniecia
i skroty decyzji dzialaja od razu), a 19 z 19 klikniec w stare srodki gniazd otwiera TO SAMO gniazdo. Ochrona po zmianie
ZAWARTOSCI mapy (A-P2: inna plytka, nowy stan pokazanej plytki z tla) zostaje bez zmian - ``test_ui_wieczor`` / ``test_ui_okno``.

Strefa pytan pokazuje jedna pozycje naraz (reszta pod licznikiem "i jeszcze n"): komunikat, ktory nie jest pierwszy, technik
wybiera licznikiem (``pokaz_w_strefie``); komunikaty trwale (np. konflikt projektu) sa na liscie bledow programu.
Okno offscreen na ``AtrapaKontrolera``. Zrzuty do raportu: zmienna ``P15_ZRZUTY`` = katalog (poza repo).
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

import test_p14_ekran as P14
from stanowisko.ui import okno as OKNO

_qt = P14._qt  # ta sama aplikacja Qt offscreen i czcionka ekranu
swiat = P14.swiat
DLUGO_MS = 600_000  # gdyby ochrona mapy jednak sie wlaczyla - trwa do konca testu, wiec asercje ja wykryja (bez zaleznosci od obciazenia PC)


def zrzut(e, nazwa: str) -> None:
    katalog = os.environ.get("P15_ZRZUTY")
    if katalog:
        Path(katalog).mkdir(parents=True, exist_ok=True)
        e.zdarzenia()
        e.okno.grab().toImage().save(str(Path(katalog) / f"{nazwa}.png"), "PNG")


def ogolne(k) -> list:
    return [x for x in k.stan().komunikaty if x.skan_id is None and not x.ukryte]


def geometria(e) -> tuple:
    """(prostokat mapy w oknie, {gniazdo: srodek w oknie}) - to, w co celuje reka technika; prostokat = ``okno.miejsce_mapy()``."""
    g = P14._geometria_mapy(e)
    assert g[0] == e.okno.miejsce_mapy()
    return g


def bez_ochrony_mapy(e, co: str) -> None:
    assert not e.okno.ochrona_aktywna() and not e.mapa.przygaszona(), f"{co}: ochrona mapy wlaczona, choc mapa stoi w miejscu"


def pokaz_w_strefie(e, nazwa: str) -> None:
    """Strefa pytan pokazuje jedna pozycje naraz: technik przechodzi licznikiem "i jeszcze n" do pozycji ``nazwa``."""
    assert nazwa in e.strefa(), (nazwa, e.strefa())
    for _ in range(len(e.strefa())):
        if e.jest(nazwa):
            return
        e.klik("uwagi_jeszcze")
    assert e.jest(nazwa), (nazwa, e.strefa())


def zamknij_w_strefie(e, nazwa: str) -> None:
    """Technik zamyka komunikat ``nazwa`` ze strefy pytan wlasnym kliknieciem w punkt okna (przycisk "Zamknij" panelu)."""
    from PySide6.QtWidgets import QPushButton

    pokaz_w_strefie(e, nazwa)
    e.po_ochronie_nakladek()  # pozycja strefy zmieniona w tle jest przez chwile przygaszona (S3-3) - technik czeka jak przy kazdym kliknieciu
    przycisk = e.w(nazwa).findChild(QPushButton, "zamknij_komunikat")
    assert przycisk is not None and przycisk.isVisibleTo(e.okno), nazwa
    P14._klik_w_punkt(e, przycisk.mapTo(e.okno, przycisk.rect().center()))


def kliki_w_stare_srodki(e, stare: dict) -> list:
    """Klikniecie w stary srodek kazdego z 19 gniazd (punkt okna): lista (gniazdo celowane, gniazdo otwarte, trafiony element)
    tam, gdzie klikniecie NIE otworzylo celowanego gniazda (inne gniazdo albo nic)."""
    zle = []
    for nr, punkt in stare.items():
        trafione = P14._klik_w_punkt(e, punkt)
        otwarte = e.okno._gniazdo
        if otwarte != nr:
            zle.append((nr, otwarte, trafione))
        if otwarte is not None:
            e.okno._zamknij_prace()
            e.zdarzenia()
    return zle


def sprawdz_krok(e, przed: tuple, co: str) -> tuple:
    """Po zmianie komunikatow: mapa i srodki 19 gniazd w tym samym miejscu, ochrona mapy nieaktywna, 19 z 19 klikniec w stare
    srodki otwiera to samo gniazdo. Zwraca geometrie (te sama)."""
    e.odczekaj(60)
    bez_ochrony_mapy(e, co)
    po = geometria(e)
    ruszone = [nr for nr in przed[1] if po[1][nr] != przed[1][nr]]
    assert po[0] == przed[0] and not ruszone, f"{co}: mapa {przed[0]} -> {po[0]}, srodek zmienia {len(ruszone)} z 19 gniazd"
    zle = kliki_w_stare_srodki(e, przed[1])
    assert not zle, f"{co}: klikniecie w stary srodek nie otwiera celowanego gniazda w {len(zle)} z 19: {zle}"
    bez_ochrony_mapy(e, co)
    return po


@pytest.mark.parametrize("rozmiar", P14.ROZMIARY, ids=lambda r: f"{r[0]}x{r[1]}")
def test_p15_komunikat_ogolny_w_tle_nie_podstawia_innego_gniazda_pod_kursor(swiat, rozmiar):
    """Technik oglada plytke 1 i siega po gniazdo. W tle: dochodzi komunikat ogolny (konflikt projektu z nowej plytki - trwaly,
    na liscie bledow programu), dochodzi drugi (plik zajety - w strefie pytan), oba znikaja. Za kazdym razem: mapa stoi
    w miejscu, ochrona mapy sie nie wlacza, 19 z 19 klikniec w stare srodki gniazd otwiera to samo gniazdo; komunikat widac
    w calosci (w strefie - po wybraniu licznikiem "i jeszcze n"); klikniecie gniazda dziala od razu."""
    k, zegar = swiat.wieczor()
    s1 = k.symuluj_skan("zwykla", numer=1)
    e = swiat.ekran(k, rozmiar)
    e.po_ochronie()
    assert e.okno._ochrona.interval() == OKNO.OCHRONA_MS == 800
    e.okno._ochrona.setInterval(DLUGO_MS)
    r = f"{rozmiar[0]}x{rozmiar[1]}"
    g = geometria(e)
    poczatek = g
    assert len(g[1]) == 19 and not ogolne(k)
    zrzut(e, f"p15_bez_komunikatu_{r}")

    zegar.przesun(2)
    k.symuluj_skan("do_powtorzenia", numer=5, projekty={1: 41, 2: 42})
    assert [x.rodzaj for x in ogolne(k)] == ["konflikt_projektu"]
    g = sprawdz_krok(e, g, "doszedl 1. komunikat ogolny")
    assert e.okno.pokazana_plytka() == s1 and e.okno.bledy.isAncestorOf(e.w("komunikat_konflikt_projektu"))
    assert not P14.niewidoczne_w_calosci(e, ("komunikat_konflikt_projektu",))
    zrzut(e, f"p15_po_1_komunikacie_{r}")

    zegar.przesun(2)
    k.symuluj_komunikat("plik_zajety")
    assert sorted(x.rodzaj for x in ogolne(k)) == ["konflikt_projektu", "plik_zajety"]
    g = sprawdz_krok(e, g, "doszedl 2. komunikat ogolny")
    pokaz_w_strefie(e, "komunikat_plik_zajety")
    assert not P14.niewidoczne_w_calosci(e, ("komunikat_konflikt_projektu", "komunikat_plik_zajety"))
    assert geometria(e) == poczatek  # przejscie po strefie pytan tez nie rusza mapy
    zrzut(e, f"p15_po_2_komunikacie_{r}")

    for kom in ogolne(k):  # znikaja w tle (kontroler), nie kliknieciem technika
        k.zamknij_komunikat(kom.id)
    assert not ogolne(k)
    g = sprawdz_krok(e, g, "komunikaty ogolne zniknely")
    assert not e.jest("komunikat_konflikt_projektu") and not e.jest("komunikat_plik_zajety")
    zrzut(e, f"p15_po_zniknieciu_{r}")

    assert g == poczatek
    P14._klik_w_punkt(e, g[1][9])  # mapa przyjmuje klikniecia od razu: srodek gniazda 9 otwiera gniazdo 9
    assert e.okno._gniazdo == 9 and e.jest("widok_pracy") and e.okno.pokazana_plytka() == s1


def test_p15_komunikat_ogolny_przy_otwartej_pracy_nie_wlacza_ochrony_skrot_decyzji_dziala(swiat):
    """(Dawniej ``test_p15_ochrona_po_komunikacie_ogolnym_konczy_sie_sama_i_pomija_skroty_decyzji``: komunikat przesuwal mape,
    wiec skrot tuz po nim byl pomijany do konca ochrony.) Przy otwartej pracy dochodzi komunikat ogolny: mapa i widok pracy
    zostaja, ochrona mapy sie nie wlacza, a skrot decyzji ("U") nacisniety TUZ po komunikacie zapisuje decyzje na pracy
    z widoku pracy."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    k, zegar = swiat.wieczor()
    s1 = k.symuluj_skan("zwykla", numer=1)
    e = swiat.ekran(k, (1536, 864))
    e.klik_gniazdo(9)
    praca = e.okno._praca_widoku
    assert praca is not None and k.stan().praca(praca).decyzja is None and k.stan().praca(praca).gniazdo == 9
    e.okno._ochrona.setInterval(DLUGO_MS)
    przed = geometria(e)
    k.symuluj_komunikat("plik_zajety")
    e.odczekaj(40)
    assert "komunikat_plik_zajety" in e.strefa()
    bez_ochrony_mapy(e, "komunikat przy otwartej pracy")
    assert geometria(e) == przed and e.okno._praca_widoku == praca and e.okno._gniazdo == 9 and e.okno.pokazana_plytka() == s1
    QTest.keyClick(e.okno, Qt.Key.Key_U)  # bez czekania na koniec jakiejkolwiek ochrony
    e.zdarzenia()
    assert k.stan().praca(praca).decyzja == "ukruszona"  # skrot zadzialal od razu, na pracy pokazanej w widoku pracy
    assert e.okno._praca_widoku == praca and geometria(e) == przed


def test_p15_zmiana_samego_tekstu_i_wlasne_zamkniecie_komunikatu_nie_przygaszaja_mapy(swiat):
    """Komunikat "plik zajety (od 12 s)" dochodzi w tle, potem jest odswiezany co sekunde (ten sam komunikat, inny tekst), na
    koniec technik zamyka go sam. Mapa za kazdym razem stoi w miejscu i nie jest przygaszona (stare okno: pierwsze dojscie
    zsuwalo mape i wlaczalo ochrone, zamkniecie przesuwalo ja z powrotem); zmiana samego tekstu nie przygasza tez strefy pytan -
    inaczej byla by nieczynna przez caly czas skanowania."""
    k, zegar = swiat.wieczor()
    k.symuluj_skan("zwykla", numer=1)
    e = swiat.ekran(k, (1600, 900))
    e.po_ochronie()
    e.okno._ochrona.setInterval(DLUGO_MS)
    g = geometria(e)

    def plik_zajety(od_s: int) -> None:  # jak ``Aplikacja``: ten sam identyfikator komunikatu, tekst z nowa liczba sekund
        k._komunikat("plik_zajety", id_="plik_zajety:skaner", od_s=od_s)
        k._odswiez()

    plik_zajety(12)
    e.odczekaj(40)
    bez_ochrony_mapy(e, "doszedl komunikat")
    assert geometria(e) == g
    pokaz_w_strefie(e, "komunikat_plik_zajety")
    tekst = e.tekst_elementu("komunikat_plik_zajety")
    for od_s in (13, 14, 15):
        plik_zajety(od_s)
        e.odczekaj(40)
        assert len(ogolne(k)) == 1 and not e.okno.ochrona_aktywna() and not e.mapa.przygaszona()
        assert not e.okno.ochrona_strefy_aktywna() and e.jest("komunikat_plik_zajety")  # ta sama pozycja strefy, nowy tekst
    assert e.tekst_elementu("komunikat_plik_zajety") != tekst and "15" in e.tekst_elementu("komunikat_plik_zajety")
    assert geometria(e) == g
    zamknij_w_strefie(e, "komunikat_plik_zajety")
    e.odczekaj(40)
    assert not ogolne(k) and "komunikat_plik_zajety" not in e.strefa() and not e.okno.ochrona_aktywna()
    assert geometria(e) == g  # po decyzji technika mapa tez w tym samym miejscu (stare okno: wracala w gore)


def test_p15_komunikat_ogolny_bez_gniazd_na_mapie_nie_wlacza_ochrony(swiat):
    """Regula A-P2 zostaje: gdy mapa nie ma gniazd do klikniecia (nie ma jeszcze zadnej plytki), nie ma czego chronic -
    komunikat ogolny z tla nie przygasza mapy i niczego nie blokuje."""
    k, zegar = swiat.wieczor()
    e = swiat.ekran(k, (1600, 900))
    assert e.okno.pokazana_plytka() is None and not e.mapa.numery()
    k.symuluj_komunikat("plik_zajety")
    e.odczekaj(40)
    assert e.jest("komunikat_plik_zajety") and not e.okno.ochrona_aktywna() and not e.mapa.przygaszona()


# --- runda 2 (recenzja PR #45): zdarzenia z tla (P1) i komunikat bedacy skutkiem polecenia (P2) - mapa stoi w miejscu ----------
DLUGI_POWOD = "bardzo dlugi powod proby recenzenta " * 14


def swiat_3_plytek(swiat, rozmiar: tuple) -> tuple:
    """Jak w probie recenzenta: 3 plytki po 19 prac, technik oglada pierwsza. Zwraca (kontroler, zegar, ekran, skan_id)."""
    k, zegar = swiat.wieczor()
    ids = []
    for i in (1, 2, 3):
        zegar.przesun(2)
        ids.append(k.symuluj_skan("zwykla", numer=i, projekty={g: 100 * i + g for g in range(1, 20)}))
    e = swiat.ekran(k, rozmiar)
    e.po_ochronie()
    if e.okno.pokazana_plytka() != ids[0]:
        e.klik(f"plytka_{ids[0]}")
        e.odczekaj(30)
        e.po_ochronie()
    assert e.okno.pokazana_plytka() == ids[0] and len(e.mapa.numery()) == 19
    return k, zegar, e, ids


def zdarzenia_z_tla(k, zegar) -> list:
    """7 zdarzen z tla z proby recenzenta (tryb A): dochodza 3 komunikaty, jeden zmienia dlugosc tekstu, znikaja."""
    def ramka(powod: str) -> None:
        k._komunikat("ramka_blad", id_="rec:x", ramka="poranna", powod=powod)
        k._odswiez()

    def konflikt() -> None:
        zegar.przesun(2)
        k.symuluj_skan("do_powtorzenia", numer=5, projekty={1: 41, 2: 42})

    def plik_zajety() -> None:
        k._komunikat("plik_zajety", id_="plik_zajety:skaner", od_s=12)
        k._odswiez()

    def znika_jeden() -> None:
        k._usun_komunikat("rec:x")
        k._odswiez()

    def znikaja() -> None:
        for x in ogolne(k):
            k._usun_komunikat(x.id)
        k._odswiez()

    return [("doszedl konflikt projektu", konflikt), ("doszedl drugi (plik zajety)", plik_zajety),
            ("doszedl trzeci (blad ramki)", lambda: ramka("krotki")), ("dluzszy tekst", lambda: ramka(DLUGI_POWOD)),
            ("krotszy tekst", lambda: ramka("krotki")), ("zniknal jeden", znika_jeden), ("zniknely wszystkie", znikaja)]


@pytest.mark.parametrize("rozmiar", P14.ROZMIARY, ids=lambda r: f"{r[0]}x{r[1]}")
def test_p15_r2_p1_ochrona_wlacza_sie_tylko_gdy_mapa_zmienia_miejsce(swiat, rozmiar):
    """P1: ochrona klikniec idzie za RUCHEM mapy, nie za zmiana paneli. W nowym oknie mapa nie rusza sie przy ZADNYM z 7 zdarzen
    z tla (dochodza 3 komunikaty, tekst sie wydluza i skraca, znikaja): prostokat mapy i srodki 19 gniazd zostaja w miejscu,
    ochrona mapy sie nie wlacza, a klikniecie w stary srodek gniazda 9 od razu otwiera gniazdo 9 (stare okno: przy 1 - 2
    zdarzeniach mapa sie ruszala i wtedy ochrona sie wlaczala)."""
    k, zegar, e, ids = swiat_3_plytek(swiat, rozmiar)
    e.okno._ochrona.setInterval(DLUGO_MS)
    poczatek = geometria(e)
    zle = []
    for nazwa, zdarzenie in zdarzenia_z_tla(k, zegar):
        przed = geometria(e)
        zdarzenie()
        e.odczekaj(60)
        ochrona, przygaszona = e.okno.ochrona_aktywna(), e.mapa.przygaszona()
        po = geometria(e)
        if po != przed or ochrona or przygaszona:
            zle.append(f"{nazwa}: mapa {przed[0]} -> {po[0]}, ruch={po != przed}, ochrona={ochrona}, przygaszona={przygaszona}")
            continue
        P14._klik_w_punkt(e, przed[1][9])  # mapa stoi i nie jest chroniona: prawowite klikniecie gniazda dziala od razu
        if e.okno._gniazdo != 9 or not e.jest("widok_pracy"):
            zle.append(f"{nazwa}: klikniecie w srodek gniazda 9 otworzylo {e.okno._gniazdo}")
        e.okno._zamknij_prace()
        e.zdarzenia()
    assert not zle, f"mapa ruszona albo chroniona w {len(zle)} z 7 zdarzen: {zle}"
    assert geometria(e) == poczatek and e.okno.pokazana_plytka() == ids[0]


@pytest.mark.parametrize("rozmiar", P14.ROZMIARY, ids=lambda r: f"{r[0]}x{r[1]}")
def test_p15_r2_p2_komunikat_po_poleceniu_technika_nie_zsuwa_mapy_i_nie_wlacza_ochrony(swiat, rozmiar):
    """(Dawniej ``test_p15_r2_p2_komunikat_po_poleceniu_technika_ktory_zsuwa_mape_wlacza_ochrone``.) P2: technik klika
    "Ukruszona", zapis samoczynny listy sie nie udaje - komunikat ogolny dochodzi jako skutek JEGO polecenia. Mapa zostaje
    w miejscu (stare okno: zsuwala sie i wlaczala ochrone), ochrona sie nie wlacza, 19 z 19 klikniec w stare srodki gniazd
    otwiera to samo gniazdo; klikniecie gniazda 9 dziala od razu."""
    from stanowisko.ui.czesci import do_obejrzenia

    k, zegar, e, ids = swiat_3_plytek(swiat, rozmiar)

    def zepsuty(*a, **kw):
        raise OSError("proba: plik listy zajety")

    k.sesja.zapisz_do_dofrezowania = zepsuty
    plytka = k.stan().plytka(ids[0])
    do = {p.praca_id for p in do_obejrzenia(plytka)}
    nr = [g.nr for g in plytka.gniazda if any(p.praca_id in do for p in g.prace)][0]
    e.klik_gniazdo(nr)
    e.okno._ochrona.setInterval(DLUGO_MS)
    przed = geometria(e)
    e.klik("przycisk_ukruszona")
    e.odczekaj(60)
    assert [x.rodzaj for x in ogolne(k)] == ["lista_nie_zapisana"] and "komunikat_lista_nie_zapisana" in e.strefa()
    assert k.stan().plytka(ids[0]).gniazdo(nr).praca.decyzja == "ukruszona"
    sprawdz_krok(e, przed, "komunikat po poleceniu technika")
    P14._klik_w_punkt(e, przed[1][9])
    assert e.okno._gniazdo == 9 and e.jest("widok_pracy")


def test_p15_r2_p2_decyzja_bez_komunikatu_i_wlasne_zamkniecie_komunikatu_nie_przygaszaja_mapy(swiat):
    """Granica P2: zwykla decyzja z udanym zapisem listy, komunikat z tla i komunikat zamkniety kliknieciem technika - mapa za
    kazdym razem stoi w miejscu i nie jest przygaszona (stare okno: komunikat z tla zsuwal mape, zamkniecie ja podnosilo)."""
    k, zegar, e, ids = swiat_3_plytek(swiat, (1536, 864))
    e.okno._ochrona.setInterval(DLUGO_MS)
    e.klik_gniazdo(9)
    przed = geometria(e)
    e.klik("przycisk_ukruszona")
    e.odczekaj(60)
    assert not ogolne(k) and geometria(e) == przed
    bez_ochrony_mapy(e, "decyzja bez komunikatu")
    k.symuluj_komunikat("plik_zmieniony")
    e.odczekaj(40)
    bez_ochrony_mapy(e, "komunikat z tla")
    assert geometria(e) == przed and "komunikat_plik_zmieniony" in e.strefa()
    zamknij_w_strefie(e, "komunikat_plik_zmieniony")
    e.odczekaj(40)
    assert not ogolne(k) and "komunikat_plik_zmieniony" not in e.strefa() and geometria(e) == przed
    bez_ochrony_mapy(e, "komunikat zamkniety przez technika")
