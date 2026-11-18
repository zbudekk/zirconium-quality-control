"""ui (E3-A1p): ekran wieczorny na laptopie stanowiska 1920 x 1080 przy skalowaniu 100 %, 125 % i 150 %.

Skalowanie jest emulowane rozmiarem okna w punktach (pikselach logicznych): ekran 1920 x 1080 przy 125 % = 1536 x 864 punktow,
przy 150 % = 1280 x 720. Dla kazdego ekranu dwa rozmiary okna: caly ekran i okno zmaksymalizowane (ekran minus pasek zadan
Windows 11 - 48 punktow - i belka tytulu, ok. 30 punktow; liczby w ``ROZMIARY``). Ten sam plik uruchomiony osobno ze zmienna
``QT_SCALE_FACTOR=1.25`` albo ``1.5`` sprawdza uklad przy prawdziwym mnozniku pikseli (czcionki i obraz w pikselach ekranu).

Dane: 10 plytek x 19 prac - dziewiec plytek z nowym wsadem (trzy z decyzjami, lista "do dofrezowania"), dziesiaty skan =
ponowny skan plytki 9 (te same prace, dwie zamienione gniazdami) -> panel pytania "Ponowny skan tej samej plytki?" z ostrzezeniem
o decyzjach; otwarta czerwona praca (przyciski decyzji). Sprawdzane przy kazdym rozmiarze: wszystko z
``test_ui_wieczor.sprawdz_uklad`` (napisy i przyciski w oknie i w rodzicu, napisy nieuciete - ``sizeHint`` <= rozmiar,
klikalne elementy nie na sobie, mapa w oknie i nie mniejsza niz minimum) oraz: zadna widoczna kontrolka poza oknem (poza
zawartoscia list przewijanych), przyciski decyzji, przyciski pytania i mapa widoczne w calosci (bez przewijania), panel
pytania z ostrzezeniem o decyzjach w calosci (bez pionowego paska przewijania obszaru paneli - po zmniejszeniu okna z 1536 x 784
do 1280 x 720 obszar zostawal przyciety: pasek przewijania zwezal panel, tekst zawijal sie w dodatkowy wiersz, a wysokosc
obszaru byla liczona dla pelnej szerokosci), zaden widoczny pasek przewijania poziomego.

Zrzuty: zmienna ``E3_ZRZUTY`` = katalog, do ktorego test zapisuje PNG kazdego rozmiaru (``wieczor_<nazwa>_<w>x<h>_dpr<m>.png``,
obraz w pikselach ekranu).
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

import test_ui_wieczor as UW

SLOTY = tuple(range(1, 20))  # 19 gniazd plytki wieczornej
PASEK_ZADAN, BELKA_TYTULU = 48, 31  # punkty (Windows 11, przy kazdym skalowaniu)
# (nazwa, szerokosc, wysokosc okna w punktach)
ROZMIARY = (
    ("100proc_ekran", 1920, 1080), ("100proc_zmaksymalizowane", 1920, 1080 - PASEK_ZADAN - BELKA_TYTULU),
    ("125proc_ekran", 1536, 864), ("125proc_zmaksymalizowane", 1536, 784),  # 864 - 48 - 31 = 785, w pikselach ekranu 980
    ("150proc_ekran", 1280, 720), ("150proc_zmaksymalizowane", 1280, 642),  # 720 - 48 - 30 = 642, w pikselach ekranu 963
)
PRZYCISKI_DECYZJI = ("przycisk_ukruszona", "przycisk_ok", "przycisk_cofnij", "przycisk_nastepna", "przycisk_zamknij_prace")
PRZYCISKI_PYTANIA = ("odp_potwierdz_ponowny_skan", "odp_odrzuc_ponowny_skan")


@pytest.fixture(scope="module", autouse=True)
def _qt():
    """Qt w trybie offscreen z czcionkami systemu (jak ``test_ui_wieczor``); ``QT_SCALE_FACTOR`` dziala, gdy ten plik
    tworzy QApplication (uruchomiony osobno)."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    if UW.FONTY_WINDOWS.is_dir():
        os.environ.setdefault("QT_QPA_FONTDIR", str(UW.FONTY_WINDOWS))
    import PySide6.QtCore  # noqa: F401
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    assert app.platformName() == "offscreen"
    UW.czcionka_ekranu()
    yield app


@pytest.fixture
def zegar():
    return UW.Zegar()


@pytest.fixture
def atrapa(tmp_path, zegar):
    from stanowisko import kontroler_api as K

    k = K.AtrapaKontrolera(tmp_path / "atrapa", zegar=zegar)
    yield k
    k.zamknij()


def indeks_plytek(atrapa, plytek: int = 9) -> None:
    """Fikcyjne zlecenia projektow ``100 * i + g`` (plytka i, gniazdo g): kuweta, zab i krazek na liscie "do dofrezowania"."""
    from stanowisko import kontroler_api as K

    baza, czas = atrapa.sesja.baza, atrapa.sesja.teraz()
    with baza.transakcja():
        for i in range(1, plytek + 1):
            for g in SLOTY:
                nr = 100 * i + g
                zlecenie = baza.wstaw("zlecenia", zrodlo="cyrkon", folder=f"{8000 + nr} Zlecenie {nr}", folder_norm=f"{8000 + nr} zlecenie {nr}",
                                      kuweta=str(8000 + nr), dodano=czas, usuniety=0)
                projekt = baza.wstaw("projekty", zlecenie_id=zlecenie, plik=f"projekt-{nr}-crown_cad.stl", sha16=K.projekt_sztuczny(nr),
                                     zeby=str(11 + nr % 37), typ="korona", usuniety=0)
                baza.wstaw("frezowania", projekt_id=projekt, plik_w_raporcie=f"projekt-{nr}-crown_cad.stl", krazek="K-3", wspolczynnik=1.225,
                           data=czas[:10], zrodlo="reczny")


def wieczor_10_plytek(atrapa, zegar) -> tuple:
    """Dziewiec plytek (nr 1-9) po 19 prac z nowym wsadem co 7 min, na plytkach 3, 6 i 9 "Ukruszona" + "OK"; dziesiaty skan
    6 min pozniej = ponowny skan plytki 9 (te same prace, gniazda 3 i 5 zamienione) - pytanie o ponowny skan."""
    pelne = {**UW.PELNA, 19: "zielony"}
    skany = []
    for i in range(1, 10):
        if i > 1:
            zegar.przesun(7)
        skany.append(atrapa.symuluj_skan("zwykla", numer=i, gniazda=pelne, projekty={g: 100 * i + g for g in SLOTY}))
        if i % 3 == 0:
            p = atrapa.stan().plytka(skany[-1])
            atrapa.ukruszona(p.gniazdo(2).praca.praca_id)
            atrapa.ok(p.gniazdo(9).praca.praca_id)
    zegar.przesun(6)
    projekty = {g: 900 + g for g in SLOTY}
    projekty[3], projekty[5] = projekty[5], projekty[3]
    ponowny = atrapa.symuluj_skan("zwykla", numer=9, gniazda=pelne, projekty=projekty)
    return skany, ponowny


def usterki_rozdzielczosci(e, rozmiar: tuple) -> list:
    """``test_ui_wieczor.sprawdz_uklad`` (zmienia rozmiar okna) + kontrolki poza oknem, przyciete przyciski decyzji i pytania,
    przycieta mapa, widoczny pasek przewijania poziomego."""
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
    for nazwa in PRZYCISKI_DECYZJI + PRZYCISKI_PYTANIA:
        w = e.w(nazwa)
        if not w.isVisibleTo(okno):
            usterki.append(f"niewidoczny {nazwa}")
        elif UW._widoczny_wycinek(okno, w) != UW._w_oknie(okno, w):
            usterki.append(f"przyciety (zasloniety albo do przewiniecia) {nazwa}: widac {UW._widoczny_wycinek(okno, w)} z {UW._w_oknie(okno, w)}")
    if UW._widoczny_wycinek(okno, okno.mapa) != UW._w_oknie(okno, okno.mapa):
        usterki.append(f"mapa przycieta: {UW._widoczny_wycinek(okno, okno.mapa)} z {UW._w_oknie(okno, okno.mapa)}")
    # panel pytania pokazanej plytki (pierwszy panel obszaru "uwagi") w calosci, z ostrzezeniem o decyzjach - bez przewijania
    for nazwa in ("pytanie_ponowny_skan", "pytanie_ostrzezenie"):
        w = e.w(nazwa)
        if not w.isVisibleTo(okno) or UW._widoczny_wycinek(okno, w) != UW._w_oknie(okno, w):
            usterki.append(f"panel pytania do przewiniecia: {nazwa} widac {UW._widoczny_wycinek(okno, w)} z {UW._w_oknie(okno, w)}")
    if okno.uwagi.verticalScrollBar().isVisibleTo(okno) and len(okno.uwagi.panele()) == 1:
        usterki.append("pasek przewijania pionowego przy jednym panelu pytania")
    return usterki


def test_ekran_1920x1080_przy_100_125_150_proc_10_plytek_x_19_prac_z_pytaniem(atrapa, zegar):
    """Kazdy rozmiar z ``ROZMIARY`` (od najwiekszego do najmniejszego i z powrotem - przelaczanie ukladu zwykly / zwarty):
    zero usterek; panel pytania i otwarta praca na ekranie; przy 1920 x 1080 uklad zwykly, przy 125 % i 150 % - zwarty."""
    from PySide6.QtGui import QGuiApplication

    from stanowisko.ui import styl

    indeks_plytek(atrapa)
    atrapa.wybierz_operatora("Technik A")
    skany, ponowny = wieczor_10_plytek(atrapa, zegar)
    stan = atrapa.stan()
    assert len(stan.plytki) == 10 and all(len(p.prace) == 19 for p in stan.plytki)
    assert [(q.rodzaj, q.skan_id, q.poprzedni_id) for q in stan.pytania] == [("ponowny_skan", ponowny, skany[-1])]
    e = UW.Ekran(atrapa, (ROZMIARY[0][1], ROZMIARY[0][2]))
    try:
        assert e.okno.pokazana_plytka() == ponowny and e.jest("pytanie_ponowny_skan")
        e.klik_gniazdo(2)  # czerwona praca: widok pracy z przyciskami decyzji
        assert e.jest("przycisk_ukruszona") and e.w("przycisk_ukruszona").isEnabled()
        dpr = QGuiApplication.primaryScreen().devicePixelRatio()
        zrzuty = Path(os.environ["E3_ZRZUTY"]) if os.environ.get("E3_ZRZUTY") else None
        if zrzuty is not None:
            zrzuty.mkdir(parents=True, exist_ok=True)
        wyniki = []
        for nazwa, szer, wys in ROZMIARY + tuple(reversed(ROZMIARY[:-1])):
            usterki = usterki_rozdzielczosci(e, (szer, wys))
            assert e.jest("pytanie_ponowny_skan") and e.okno.pokazana_plytka() == ponowny
            zwarty = szer < styl.PROG_ZWARTEGO[0] or wys < styl.PROG_ZWARTEGO[1]
            assert e.okno.zwarty() == zwarty, (nazwa, szer, wys)
            wyniki.append(f"{nazwa} {szer}x{wys}: usterek {len(usterki)}, uklad {'zwarty' if zwarty else 'zwykly'}, "
                          f"mapa {e.mapa.width()}x{e.mapa.height()}, przycisk Ukruszona {e.w('przycisk_ukruszona').width()}x"
                          f"{e.w('przycisk_ukruszona').height()}")
            assert not usterki, f"{nazwa} {szer}x{wys} (mnoznik pikseli {dpr}):\n" + "\n".join(usterki)
            if zrzuty is not None:
                e.obraz().save(str(zrzuty / f"wieczor_{nazwa}_{szer}x{wys}_dpr{dpr:g}.png"))
        print(f"\n[E3-A1p ekran, mnoznik pikseli {dpr:g}]\n  " + "\n  ".join(wyniki))
    finally:
        e.zamknij()
