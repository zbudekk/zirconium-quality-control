"""E3-O3: ekran dla plytek okraglych - testowych n8 / n9 i ramkowych n1-n6 (R58, uklady ``okragla_ramkowa_*``).

Kryteria paczki (zlecenie 2 z 21.11.2026, plan ``Ramki/etap3/plan_plytki_okragle_n1-n6_2026-11-21.md`` sekcja 4 "E3-O3"):
  (1) mapa plytki okraglej (wieczor ``MapaPlytki`` i rano ``MapaRano``, uklad testowy i ramkowy) ma sciecie orientacyjne po
      stronie przod-prawo, z geometrii pola ``flat`` ukladu (``uklad.json``), nie z liczb wpisanych w kod; klik w 19 z 19
      (wieczorna) i 24 z 24 (poranna) gniazd trafia w dobre gniazdo; kwadrat: 0 zmian (obraz i obrys przed = po),
  (2) ``porownaj.opis_ukladu`` odroznia plytke okragla ramkowa od testowej; napis miesci sie w oknie proby przy 1536 x 864.

"Przed" w tescie kwadratu to ``StaryObrys`` - doslowna kopia rysowania plytki sprzed paczki (commit 8001b55): obraz mapy
kwadratowej musi byc bajt w bajt rowny obrazowi z tamtego kodu, a obraz mapy okraglej musi sie od niego roznic.
Zrzuty calego okna: zmienna ``E3_ZRZUTY`` = katalog na PNG (jak w ``test_ui_rozdzielczosc``). Plik jest ASCII.
"""
from __future__ import annotations

import dataclasses
import math
import os
import warnings
from pathlib import Path

import pytest

import test_ui_rano as UR
import test_ui_wieczor as UW

OKRAGLE = ("okragla_wieczorna", "okragla_poranna", "okragla_wieczorna_r54", "okragla_poranna_r54",
           "okragla_ramkowa_wieczorna", "okragla_ramkowa_poranna")
KWADRATY = ("wieczorna", "poranna", "wieczorna_r54", "poranna_r54")
RAMKOWE = ("okragla_ramkowa_wieczorna", "okragla_ramkowa_poranna")
GNIAZD = {"okragla_wieczorna": 19, "okragla_ramkowa_wieczorna": 19, "okragla_poranna": 24, "okragla_ramkowa_poranna": 24}
ROZMIARY_MAPY = ((700, 640), (430, 400))  # mapa w oknie 1920 x 1080 i mapa w ukladzie zwartym / poranna obok innych
ROZMIARY_OKNA = (("100proc", 1920, 1080), ("125proc", 1536, 864))
KOLORY = ("#2e9d4f", "#d23b3b", "#e6b422", "#9aa3ad", "#f6f7f9")


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


def uklad(nazwa: str):
    from stanowisko import uklad as U

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return U.wczytaj(nazwa)


def plytka(uk):
    """Plytka kontraktu (``kontroler_api.Plytka``) ze wszystkimi gniazdami ukladu: kolory na przemian, co piate z podpisem."""
    from stanowisko import kontroler_api as K

    gniazda = tuple(K.Gniazdo(nr=g.id, status="pusty", kolor=None, rgb=KOLORY[g.id % len(KOLORY)], podpis="ubytek" if g.id % 5 == 1 else "")
                    for g in uk.sockets)
    return K.Plytka(skan_id=1, status="przyjety", aktywna=True, napis="proba", uklad=uk.nazwa, gniazda=gniazda)


def _stary_obrys(mapa, p) -> None:
    """Rysowanie plytki SPRZED paczki E3-O3 (``mapa.MapaPlytki._rysuj_plytke`` z commita 8001b55, bez zmian)."""
    from PySide6.QtCore import QRectF, Qt
    from PySide6.QtGui import QBrush, QColor, QFont, QPainterPath, QPen

    from stanowisko.ui import mapa as M
    from stanowisko.ui import napisy as N
    from stanowisko.ui import styl

    ksztalt, prostokat, s, px, uk = mapa._obrys
    p.setPen(QPen(QColor("#5b6470"), 2))
    p.setBrush(QBrush(QColor("#f6f7f9")))
    if ksztalt == "round":
        p.drawEllipse(prostokat)
    else:
        obrys = QPainterPath()
        obrys.addRoundedRect(prostokat, 6, 6)
        wyciecie = uk.notch or {}
        if {"x_min", "x_max", "y_min", "y_max"} <= set(wyciecie):
            naroznik = QPainterPath()
            naroznik.addRect(QRectF(px(wyciecie["x_min"], wyciecie["y_max"]), px(wyciecie["x_max"] + 2, wyciecie["y_min"] - 2)))
            obrys = obrys.subtracted(naroznik)
        p.drawPath(obrys)
    f = QFont(styl.CZCIONKA)
    f.setPixelSize(14)
    f.setBold(True)
    p.setFont(f)
    p.setPen(QColor(styl.TEKST_SLABY))
    p.drawText(QRectF(0, prostokat.bottom() + 4, mapa.width(), M.MIEJSCE_NA_PODPIS_PX), int(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop),
               N.MAPA_PRZOD)


def klasa_mapy(rodzaj: str, stara: bool = False):
    from stanowisko.ui.mapa import MapaPlytki
    from stanowisko.ui.mapa_rano import MapaRano

    baza = MapaPlytki if rodzaj == "wieczor" else MapaRano
    if not stara:
        return baza

    class StaryObrys(baza):
        def _rysuj_plytke(self, p) -> None:
            _stary_obrys(self, p)

    return StaryObrys


@pytest.fixture
def mapy():
    """Funkcja ``nowa(rodzaj, uk, rozmiar, stara=False)`` -> pokazany widzet mapy z plytka ``plytka(uk)``; zamykane po tescie."""
    from PySide6.QtTest import QTest

    otwarte = []

    def nowa(rodzaj: str, uk, rozmiar: tuple, stara: bool = False, wybrane: int | None = 2):
        klasa = klasa_mapy(rodzaj, stara)
        m = klasa() if rodzaj == "wieczor" else klasa(1)
        m.resize(*rozmiar)
        if rodzaj == "wieczor":
            m.ustaw(plytka(uk), uk, wybrane)
        else:
            m.ustaw_rano(plytka(uk), uk, wybrane, frozenset({3}), {})
        m.show()
        QTest.qWaitForWindowExposed(m)
        assert (m.width(), m.height()) == tuple(rozmiar)
        otwarte.append(m)
        return m

    yield nowa
    for m in otwarte:
        m.close()
        m.deleteLater()


def kolo_na_ekranie(m) -> tuple:
    """(srodek x, srodek y, promien) plytki okraglej na ekranie z obrysu mapy: sciecie lezy na kierunku 45 st., wiec skrajne
    punkty kola (lewo, prawo, gora, dol) zostaja i prostokat obrysu jest prostokatem pelnego kola."""
    r = m.obrys_plytki().boundingRect()
    assert abs(r.width() - r.height()) < 0.01
    return r.center().x(), r.center().y(), r.width() / 2


def punkt_gniazda(m, uk, nr: int):
    """Srodek gniazda ``nr`` na ekranie policzony NIEZALEZNIE od mapy: wspolrzedne gniazda z ukladu (mm; x w prawo, y do tylu =
    w gore ekranu) przeniesione na kolo plytki z obrysu mapy."""
    from PySide6.QtCore import QPointF

    cx, cy, r = kolo_na_ekranie(m)
    g = uk.gniazdo(nr)
    return QPointF(cx + g.x * 2 * r / uk.d, cy - g.y * 2 * r / uk.d)


# ----------------------------------------------------------------------------
# (1) sciecie orientacyjne: geometria z pola ``flat``
# ----------------------------------------------------------------------------
@pytest.mark.parametrize("nazwa", OKRAGLE)
def test_sciecie_mm_z_pola_flat_ukladu(nazwa):
    from stanowisko.ui import mapa as M

    uk = uklad(nazwa)
    assert uk.shape == "round" and uk.flat, "uklad okragly bez pola flat"
    a, b = M.sciecie_mm(uk)
    pol = uk.d / 2
    for x, y in (a, b):
        assert math.hypot(x, y) == pytest.approx(pol, abs=1e-6)  # konce cieciwy leza na okregu plytki
    sx, sy = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    assert math.hypot(sx, sy) == pytest.approx(uk.flat["dist"], abs=1e-6)  # odleglosc cieciwy od srodka = flat.dist
    assert math.degrees(math.atan2(sy, sx)) == pytest.approx(uk.flat["angle_deg"], abs=1e-6)  # kierunek = flat.angle_deg
    assert math.dist(a, b) == pytest.approx(uk.flat["chord_w"], abs=0.01)  # zgodne z szerokoscia cieciwy zapisana w pliku
    assert sx > 0 and sy < 0  # przod-prawo: x w prawo, y do tylu (przod plytki = y ujemne)


def test_sciecie_idzie_za_polem_flat_a_nie_za_liczbami_w_kodzie():
    from stanowisko.ui import mapa as M

    uk = uklad("okragla_ramkowa_wieczorna")
    inny = dataclasses.replace(uk, flat={"corner": "B", "angle_deg": 135.0, "chord_w": 60.0, "dist": 40.0})
    a, b = M.sciecie_mm(inny)
    sx, sy = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    assert sx < 0 and sy > 0 and math.hypot(sx, sy) == pytest.approx(40.0)  # tyl-lewo, 40 mm od srodka
    assert math.dist(a, b) == pytest.approx(60.0)  # 2 * sqrt(50^2 - 40^2)
    assert M.sciecie_mm(dataclasses.replace(uk, flat={})) is None  # uklad okragly bez pola flat: kolo bez sciecia
    assert M.sciecie_mm(dataclasses.replace(uk, flat={"angle_deg": -45.0, "dist": 60.0})) is None  # cieciwa poza plytka
    assert M.sciecie_mm(dataclasses.replace(uk, flat={"angle_deg": "x", "dist": 40.0})) is None  # zle dane: bez sciecia, bez wyjatku
    assert M.sciecie_mm(uklad("wieczorna")) is None  # kwadrat nie ma sciecia (ma wyciecie naroznika)


@pytest.mark.parametrize("rozmiar", ROZMIARY_MAPY)
@pytest.mark.parametrize("nazwa", sorted(GNIAZD))
@pytest.mark.parametrize("rodzaj", ["wieczor", "rano"])
def test_mapa_okragla_ma_sciecie_po_stronie_przod_prawo(mapy, rodzaj, nazwa, rozmiar):
    from PySide6.QtCore import QPointF

    uk = uklad(nazwa)
    m = mapy(rodzaj, uk, rozmiar)
    konce = m.sciecie()
    assert konce is not None, "mapa okragla bez sciecia"
    cx, cy, r = kolo_na_ekranie(m)
    skala = 2 * r / uk.d
    for k in konce:
        assert k.x() > cx and k.y() > cy  # prawo i dol ekranu; przod plytki jest na dole ekranu (napis "PRZOD PLYTKI")
        assert math.hypot(k.x() - cx, k.y() - cy) == pytest.approx(r, abs=0.5)
        assert m.rect().contains(k.toPoint())
    sx, sy = (konce[0].x() + konce[1].x()) / 2 - cx, (konce[0].y() + konce[1].y()) / 2 - cy
    assert sx == pytest.approx(sy, abs=0.5)  # kierunek -45 st. od +X plytki = 45 st. w dol ekranu
    odl = math.hypot(sx, sy)
    assert odl == pytest.approx(uk.flat["dist"] * skala, abs=0.5)
    assert math.hypot(konce[0].x() - konce[1].x(), konce[0].y() - konce[1].y()) == pytest.approx(uk.flat["chord_w"] * skala, abs=1.0)
    obrys = m.obrys_plytki()
    w = math.sqrt(0.5)
    za_cieciwa = (odl + r) / 2  # miedzy cieciwa a lukiem, ktorego juz nie ma
    assert not obrys.contains(QPointF(cx + za_cieciwa * w, cy + za_cieciwa * w))  # tu plytka jest scieta
    assert obrys.contains(QPointF(cx + (odl - 2) * w, cy + (odl - 2) * w))  # tuz przed cieciwa: plytka
    for kx, ky in ((1, -1), (-1, -1), (-1, 1)):  # pozostale trzy kierunki ukosne: kolo nietkniete
        assert obrys.contains(QPointF(cx + kx * za_cieciwa * w, cy + ky * za_cieciwa * w))


@pytest.mark.parametrize("nazwa", ["okragla_wieczorna", "okragla_ramkowa_poranna"])
@pytest.mark.parametrize("rodzaj", ["wieczor", "rano"])
def test_sciecie_widac_na_obrazie(mapy, rodzaj, nazwa):
    """Piksel miedzy cieciwa a dawnym lukiem ma kolor tla panelu (plytki tam nie ma), a w rysunku sprzed paczki - kolor plytki."""
    from stanowisko.ui import styl

    uk = uklad(nazwa)
    rozmiar = (2000, 1900)  # duza mapa: sciecie 0,64 mm ma tu ok. 12 pikseli glebokosci
    nowa, stara = mapy(rodzaj, uk, rozmiar), mapy(rodzaj, uk, rozmiar, stara=True)
    cx, cy, r = kolo_na_ekranie(nowa)
    odl = uk.flat["dist"] * 2 * r / uk.d
    assert r - odl > 10
    w = math.sqrt(0.5) * (odl + r) / 2
    x, y = round(cx + w), round(cy + w)
    assert nowa.grab().toImage().pixelColor(x, y).name() == styl.TLO_PANELU.lower()
    assert stara.grab().toImage().pixelColor(x, y).name() == "#f6f7f9"


# ----------------------------------------------------------------------------
# (1) klik w kazde gniazdo trafia w dobre gniazdo
# ----------------------------------------------------------------------------
@pytest.mark.parametrize("rozmiar", ROZMIARY_MAPY)
@pytest.mark.parametrize("nazwa", sorted(GNIAZD))
@pytest.mark.parametrize("rodzaj", ["wieczor", "rano"])
def test_klik_w_kazde_gniazdo_trafia_w_dobre_gniazdo(mapy, rodzaj, nazwa, rozmiar):
    from PySide6.QtCore import QPointF, Qt
    from PySide6.QtTest import QTest

    uk = uklad(nazwa)
    m = mapy(rodzaj, uk, rozmiar)
    trafione = []
    m.klik.connect(trafione.append)
    for g in uk.sockets:
        QTest.mouseClick(m, Qt.MouseButton.LeftButton, pos=m.srodek_gniazda(g.id).toPoint())
    assert trafione == [g.id for g in uk.sockets] and len(trafione) == GNIAZD[nazwa]
    # polozenie gniazda liczone NIEZALEZNIE od mapy: ze wspolrzednych gniazda w ukladzie (mm) i z kola plytki na ekranie
    # (x w prawo, y plytki do tylu = w gore ekranu) - klik w tak policzony punkt ma dac numer tego gniazda
    cx, cy, r = kolo_na_ekranie(m)
    skala = 2 * r / uk.d
    del trafione[:]
    for g in uk.sockets:
        punkt = QPointF(cx + g.x * skala, cy - g.y * skala)
        assert math.hypot(m.srodek_gniazda(g.id).x() - punkt.x(), m.srodek_gniazda(g.id).y() - punkt.y()) < 0.5
        QTest.mouseClick(m, Qt.MouseButton.LeftButton, pos=punkt.toPoint())
    assert trafione == [g.id for g in uk.sockets] and len(trafione) == GNIAZD[nazwa]
    obok = 0
    for g in uk.sockets:  # takze klik poza srodkiem gniazda: 4 punkty w 60 % promienia gniazda (z ukladu) i punkt probny
        promien = (g.d_top / 2 if g.okragle else g.w / 2) * skala
        s = QPointF(cx + g.x * skala, cy - g.y * skala)
        punkty = [QPointF(s.x() + dx * 0.6 * promien, s.y() + dy * 0.6 * promien) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
        for punkt in punkty + [m.punkt_probny(g.id)]:
            assert m.gniazdo_w_punkcie(punkt) == g.id
            obok += 1
    assert obok == 5 * GNIAZD[nazwa]


# ----------------------------------------------------------------------------
# (1) kwadrat: 0 zmian
# ----------------------------------------------------------------------------
@pytest.mark.parametrize("rozmiar", ROZMIARY_MAPY)
@pytest.mark.parametrize("nazwa", KWADRATY)
@pytest.mark.parametrize("rodzaj", ["wieczor", "rano"])
def test_mapa_kwadratowa_bez_zmian(mapy, rodzaj, nazwa, rozmiar):
    from PySide6.QtCore import QRectF
    from PySide6.QtGui import QPainterPath

    uk = uklad(nazwa)
    nowa, stara = mapy(rodzaj, uk, rozmiar), mapy(rodzaj, uk, rozmiar, stara=True)
    assert nowa.sciecie() is None
    assert nowa.grab().toImage() == stara.grab().toImage()  # obraz przed = obraz po, piksel w piksel
    _, prostokat, _, px, _ = nowa._obrys
    wzor = QPainterPath()  # obrys kwadratu liczony wzorem sprzed paczki
    wzor.addRoundedRect(prostokat, 6, 6)
    naroznik = QPainterPath()
    naroznik.addRect(QRectF(px(uk.notch["x_min"], uk.notch["y_max"]), px(uk.notch["x_max"] + 2, uk.notch["y_min"] - 2)))
    assert nowa.obrys_plytki() == wzor.subtracted(naroznik)


@pytest.mark.parametrize("nazwa", OKRAGLE)
def test_mapa_okragla_rozni_sie_od_rysunku_sprzed_paczki(mapy, nazwa):
    uk = uklad(nazwa)
    nowa, stara = mapy("wieczor", uk, ROZMIARY_MAPY[0]), mapy("wieczor", uk, ROZMIARY_MAPY[0], stara=True)
    assert nowa.grab().toImage() != stara.grab().toImage()


def test_mapa_ramkowa_i_testowa_maja_te_sama_geometrie(mapy):
    """Uklad ramkowy ma te same gniazda i ten sam obrys wierzchu co okragla testowa - mapy sa takie same (rozni je opis ukladu)."""
    for typ in ("wieczorna", "poranna"):
        a = mapy("wieczor", uklad(f"okragla_{typ}"), ROZMIARY_MAPY[0])
        b = mapy("wieczor", uklad(f"okragla_ramkowa_{typ}"), ROZMIARY_MAPY[0])
        assert a.grab().toImage() == b.grab().toImage()


# ----------------------------------------------------------------------------
# (1) cale okno 1920 x 1080 i 1536 x 864: wieczor i rano, uklad testowy i ramkowy
# ----------------------------------------------------------------------------
@pytest.fixture
def zegar():
    return UW.Zegar()


@pytest.fixture
def atrapa(tmp_path, zegar):
    from stanowisko import kontroler_api as K

    k = K.AtrapaKontrolera(tmp_path / "atrapa", zegar=zegar)
    yield k
    k.zamknij()


@pytest.fixture
def ekrany():
    otwarte = []

    def nowy(kontroler, rozmiar: tuple, rano: bool = False):
        e = (UR.Ekran if rano else UW.Ekran)(kontroler, rozmiar)
        otwarte.append(e)
        return e

    yield nowy
    for e in otwarte:
        e.zamknij()


def _zrzut(e, nazwa: str) -> None:
    katalog = os.environ.get("E3_ZRZUTY")
    if katalog:
        Path(katalog).mkdir(parents=True, exist_ok=True)
        e.obraz().save(str(Path(katalog) / f"{nazwa}.png"))


def _sciecie_w_oknie(mapa, uk) -> None:
    konce = mapa.sciecie()
    assert konce is not None
    cx, cy, r = kolo_na_ekranie(mapa)
    for k in konce:
        assert k.x() > cx and k.y() > cy and mapa.rect().contains(k.toPoint())
    assert mapa.rect().contains(mapa.obrys_plytki().boundingRect().toAlignedRect())  # cala plytka w widzecie mapy


@pytest.mark.parametrize("ekran, szer, wys", ROZMIARY_OKNA)
@pytest.mark.parametrize("nazwa, numer", [("okragla_wieczorna", 8), ("okragla_ramkowa_wieczorna", 1)])
def test_okno_wieczorne_mapa_okragla_sciecie_i_klikniecia(atrapa, ekrany, nazwa, numer, ekran, szer, wys):
    """Skan plytki okraglej w oknie wieczornym: mapa ze scieciem, uklad okna bez usterek, klik w 19 z 19 gniazd. Status skanu
    nie jest tu sprawdzany (na galezi bez E3-O2 sesja blokuje uklad ramkowy - mapa i tak pokazuje gniazda z pracami)."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    atrapa.wybierz_operatora("Technik A")
    e = ekrany(atrapa, (szer, wys))
    skan_id = atrapa.symuluj_skan("zwykla", numer=numer, uklad=nazwa)
    e.czekaj(lambda: e.okno.pokazana_plytka() == skan_id, co="plytka na ekranie")
    assert UW.sprawdz_uklad(e, (szer, wys)) == []
    uk = uklad(nazwa)
    assert sorted(e.mapa.numery()) == list(range(1, 20))
    _sciecie_w_oknie(e.mapa, uk)
    _zrzut(e, f"o3_wieczor_{nazwa}_{szer}x{wys}")
    trafione = []
    e.mapa.klik.connect(trafione.append)
    for nr in range(1, 20):
        e.zdarzenia()
        e.po_ochronie()
        QTest.mouseClick(e.mapa, Qt.MouseButton.LeftButton, pos=punkt_gniazda(e.mapa, uk, nr).toPoint())
    assert trafione == list(range(1, 20))


@pytest.mark.parametrize("ekran, szer, wys", ROZMIARY_OKNA)
def test_okno_poranne_mapy_okragle_sciecie_i_klikniecia(tmp_path, ekrany, ekran, szer, wys):
    """Piec z plytka okragla testowa n9 i okragla ramkowa n4: obie mapy ze scieciem, klik w 24 z 24 gniazd kazdej."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    from stanowisko import kontroler_api as K

    k = K.AtrapaKontrolera(tmp_path / "atrapa_rano", zegar=UR.ZegarRano())
    try:
        k.przelacz_tryb(K.TRYB_RANO)
        k.wybierz_operatora(k.sesja.operatorzy[0])
        gniazda = {1: "pewna", 2: "pewna", 3: "pewna"}
        skany = {"okragla_poranna": k.symuluj_skan_rano(9, gniazda, projekty={1: 305, 2: 306, 3: 307}, uklad="okragla_poranna"),
                 "okragla_ramkowa_poranna": k.symuluj_skan_rano(4, gniazda, projekty={1: 308, 2: 309, 3: 311}, uklad="okragla_ramkowa_poranna")}
        e = ekrany(k, (szer, wys), rano=True)
        e.czekaj(lambda: set(skany.values()) <= set(e.mapy()), co="mapy obu plytek na ekranie porannym")
        assert UR.usterki_rano(e, (szer, wys)) == []
        _zrzut(e, f"o3_rano_okragle_{szer}x{wys}")
        for nazwa, skan_id in skany.items():
            mapa = e.mapy()[skan_id]
            assert sorted(mapa.numery()) == list(range(1, 25)), nazwa
            _sciecie_w_oknie(mapa, uklad(nazwa))
            trafione = []
            mapa.klik.connect(trafione.append)
            for nr in range(1, 25):
                e.zdarzenia()
                e.po_ochronie_rano()
                mapa = e.mapy()[skan_id]
                QTest.mouseClick(mapa, Qt.MouseButton.LeftButton, pos=punkt_gniazda(mapa, uklad(nazwa), nr).toPoint())
            assert trafione == list(range(1, 25)), nazwa
    finally:
        k.zamknij()


# ----------------------------------------------------------------------------
# (2) opis ukladu: ramkowa a testowa
# ----------------------------------------------------------------------------
def test_opis_ukladu_odroznia_okragla_ramkowa_od_testowej():
    from stanowisko import porownaj as PO
    from stanowisko import ustawienia as UST

    for typ in ("wieczorna", "poranna"):
        ramkowa, testowa = PO.opis_ukladu(f"okragla_ramkowa_{typ}"), PO.opis_ukladu(f"okragla_{typ}")
        assert ramkowa != testowa
        assert "ramk" in ramkowa and "test" not in ramkowa and "kwadratowa" not in ramkowa
        assert "test" in testowa and "ramk" not in testowa.replace("poza ramk", "") and "kwadratowa" not in testowa
        for opis in (ramkowa, testowa):
            assert f"p\u0142ytka {typ}" in opis and "okr\u0105g\u0142a" in opis and "R59" in opis
        assert "test" in PO.opis_ukladu(f"okragla_{typ}_r54") and "R54" in PO.opis_ukladu(f"okragla_{typ}_r54")
        assert PO.opis_ukladu(typ) == f"p\u0142ytka {typ}, kwadratowa, nowy uk\u0142ad gniazd (R59)"  # kwadrat: tekst bez zmian
        assert PO.opis_ukladu(f"{typ}_r54") == f"p\u0142ytka {typ}, kwadratowa, stary uk\u0142ad gniazd (R54)"
    opisy = {n: PO.opis_ukladu(n) for n in UST.UKLADY_WBUDOWANE}
    assert len(opisy) == 10 and len(set(opisy.values())) == 10  # 10 ukladow = 10 roznych opisow
    for nazwa in UST.UKLADY_WBUDOWANE:  # z wczytanym ukladem i bez niego: ten sam tekst
        assert PO.opis_ukladu(nazwa, uklad(nazwa)) == opisy[nazwa]


def test_opis_ukladu_w_oknie_proby_miesci_sie_przy_1536x864():
    """Jedyne miejsce na ekranie z opisem ukladu to okno proby ``ui_test`` (etykieta "rozpoznano: ..."; drugie to wydruk
    ``porownaj`` w konsoli): najdluzszy napis - plytka ramkowa z dopiskiem NIEPEWNE - nie rozpycha okna ponad 1536 x 864."""
    from PySide6.QtWidgets import QApplication

    from stanowisko import porownaj as PO
    from stanowisko import ui_test
    from stanowisko import ustawienia as UST

    okno = ui_test.Okno(UST.wczytaj_ustawienia(UST.PLIK_PRZYKLADU))
    try:
        okno.show()
        najdluzszy = 0
        for nazwa in UST.UKLADY_WBUDOWANE:
            okno.etykieta_plytki.setText(f"rozpoznano: {nazwa} \u2014 {PO.opis_ukladu(nazwa, uklad(nazwa))}; nr 1; wsp\u00f3\u0142czynnik 1.220"
                                         + " \u2014 NIEPEWNE: wpisz numer p\u0142ytki albo wybierz uk\u0142ad z listy")
            QApplication.processEvents()
            potrzebne = okno.minimumSizeHint()
            najdluzszy = max(najdluzszy, potrzebne.width())
            assert potrzebne.width() <= 1536 and potrzebne.height() <= 864, (nazwa, potrzebne)
            okno.resize(1536, 864)
            QApplication.processEvents()
            assert (okno.width(), okno.height()) == (1536, 864)
            e = okno.etykieta_plytki
            assert e.sizeHint().width() <= e.width() + 1, (nazwa, e.sizeHint().width(), e.width())  # napis nieuciety
        assert najdluzszy > 0
    finally:
        okno.close()
        okno.deleteLater()
