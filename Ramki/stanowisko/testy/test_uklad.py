import math

import pytest

from stanowisko import uklad as U


# Testy z liczbami układu R54 (18 + 2, 31 + 2, ø9, ø7,5) działają na układach ``*_r54`` — stare płytki fizyczne są nadal
# skanowane (R59, decyzja D4); oczekiwania bez zmian. Układ R59 (liczby z ../parametry.json): testy/test_uklad_r59.py.
@pytest.mark.parametrize("nazwa,n_okr,n_ryn,numery", [("wieczorna_r54", 18, 2, [1, 2, 3]), ("poranna_r54", 31, 2, [4, 5, 6])])  # R54: układ w kole r 47
def test_uklad_zgodny_z_planem(nazwa, n_okr, n_ryn, numery):
    uk = U.wczytaj(nazwa)
    assert uk.size == 96 and uk.thickness == 8
    assert len(uk.gniazda_okragle()) == n_okr
    assert len(uk.rynienki()) == n_ryn
    assert len(uk.markers) == 3 and len(uk.code_dimples) == 3
    assert uk.numery == numery
    for n in numery:
        assert uk.plik_stl(n).exists()


@pytest.mark.parametrize("nazwa", ["wieczorna", "poranna", "wieczorna_r54", "poranna_r54"])
def test_gniazda_nie_nachodza_i_scianka_3mm(nazwa):
    """T3: obie płytki, okrągłe↔okrągłe i okrągłe↔rynienki (odległość obrysów ≥ 3 mm)."""
    uk = U.wczytaj(nazwa)
    okr = uk.gniazda_okragle()
    for i, a in enumerate(okr):
        for b in okr[i + 1 :]:
            d = math.hypot(a.x - b.x, a.y - b.y)
            assert d >= a.d_top / 2 + b.d_top / 2 + 3.0 - 1e-6, (a.id, b.id, d)
        for r in uk.rynienki():
            assert r.odleglosc_do_obrysu(a.x, a.y) - a.d_top / 2 >= 3.0 - 1e-6, (a.id, r.id)


def test_geometria_gniazda():
    g = U.wczytaj("wieczorna_r54").gniazdo(8)  # R54: id 1 to rynienka przednia; 8–14 = ø9
    assert g.z_top == 8.0
    assert g.okragle and g.d_top == 9
    assert g.z_dno == 4.0
    assert abs(g.promien_dolny() - 6.86 / 2) < 1e-6
    assert g.zawiera(g.x + 4.4, g.y) and not g.zawiera(g.x + 4.6, g.y)


def test_rynienka_zawiera():
    """Obrys rynienki to stadion (D4): narożnik prostokąta 60 × 15 leży poza otworem."""
    r = U.wczytaj("wieczorna_r54").rynienki()[0]
    assert r.zawiera(r.x + 29, r.y) and r.zawiera(r.x + 22.5, r.y + 7.4) and not r.zawiera(r.x + 31, r.y)
    assert not r.zawiera(r.x + 29, r.y + 7)  # w prostokącie, poza stadionem
    assert max(math.hypot(x, y) for x, y in r.obrys()) == pytest.approx(math.hypot(22.5, 31.5) + 7.5, abs=0.01)  # 46,18


@pytest.mark.parametrize("nazwa,n_okr,n_ryn,numery,bity", [("okragla_wieczorna_r54", 18, 2, [8], 4), ("okragla_poranna_r54", 31, 2, [9], 4)])
def test_plytki_okragle(nazwa, n_okr, n_ryn, numery, bity):
    """R57 (2.11.2026): płytki okrągłe ø100 z 4 dołkami kodu i ścięciem orientacyjnym; gniazda jak na kwadracie."""
    uk = U.wczytaj(nazwa)
    assert uk.shape == "round" and uk.d == 100.0 and uk.size == 100.0 and uk.thickness == 8
    assert len(uk.gniazda_okragle()) == n_okr and len(uk.rynienki()) == n_ryn
    assert len(uk.code_dimples) == bity and uk.liczba_bitow == 4
    assert uk.numery == numery
    assert uk.plik_stl(numery[0]).name == f"plytka_n{numery[0]}.stl" and uk.plik_stl(numery[0]).exists()
    assert (uk.katalog / U.PLIK_PLYTKI_BAZOWEJ).exists()
    assert uk.flat["chord_w"] == 16 and uk.flat["angle_deg"] == -45.0 and 49 < uk.flat["dist"] < 50
    kw = U.wczytaj(nazwa.replace("okragla_", ""))
    assert [(g.id, g.typ, g.x, g.y, g.d_top, g.l, g.w) for g in uk.sockets] == [(g.id, g.typ, g.x, g.y, g.d_top, g.l, g.w) for g in kw.sockets]
    assert [(m.corner, m.x, m.y) for m in uk.markers] == [(m.corner, m.x, m.y) for m in kw.markers]
    for d in uk.code_dimples:  # dołki w polu skanowania ø100 (na kwadracie leżą poza nim: r 54–58)
        assert math.hypot(d.x, d.y) < 47
    for g in uk.sockets:  # cały obrys (stadion) w kole r 47
        assert max(math.hypot(x, y) for x, y in g.obrys()) <= 47.0


def test_wszystkie_plytki_z_ustawien():
    """Każda płytka z [plytki] w ustawieniach wczytuje się i ma 3 znaczniki w trójkącie nierównobocznym."""
    from stanowisko import ustawienia as UST

    ust = UST.wczytaj_ustawienia()
    nowe = {"wieczorna", "poranna", "okragla_wieczorna", "okragla_poranna"}
    assert set(ust["plytki"]) == nowe | {n + "_r54" for n in nowe} | {"okragla_ramkowa_wieczorna", "okragla_ramkowa_poranna"}  # R59: układ nowy i poprzedni (stare płytki); E3-O1: 2 uklady okragle ramkowe (R58)
    for nazwa in ust["plytki"]:
        uk = U.wczytaj(nazwa, UST.katalog_plytki(ust, nazwa))
        m = uk.markers
        boki = sorted(math.hypot(m[i].x - m[j].x, m[i].y - m[j].y) for i, j in ((0, 1), (1, 2), (0, 2)))
        assert boki[1] - boki[0] > 0.5 and boki[2] - boki[1] > 0.5, (nazwa, boki)  # orientacja ze znaczników jednoznaczna


def test_typ_plytki_bez_przyrostka_ukladu():
    """Nazwa układu = klucz z [plytki]; przyrostek ``_r54`` oznacza poprzedni układ tego samego typu płytki."""
    assert U.typ_plytki("wieczorna_r54") == "wieczorna" and U.typ_plytki("okragla_poranna_r54") == "okragla_poranna"
    assert U.typ_plytki("poranna") == "poranna" and U.typ_plytki("okragla_wieczorna") == "okragla_wieczorna"
    for n in ("wieczorna", "wieczorna_r54", "okragla_poranna", "okragla_poranna_r54"):
        assert U.wczytaj(n).nazwa == n  # nazwa układu, nie pole ``plate`` z pliku (w obu układach takie samo)


def test_kody_plytek():
    for n in range(8):
        assert U.UkladPlytki.numer_z_bitow(*U.UkladPlytki.bity_z_numeru(n)) == n
    for n in range(16):  # bit D (płytki n8, n9…)
        assert U.UkladPlytki.numer_z_bitow(*U.UkladPlytki.bity_z_numeru(n, 4)) == n
    assert U.UkladPlytki.bity_z_numeru(5) == (True, False, True)
    assert U.UkladPlytki.bity_z_numeru(9, 4) == (True, False, False, True)
    for n in (-1, 8, 16):
        with pytest.raises(ValueError):
            U.UkladPlytki.bity_z_numeru(n)
    with pytest.raises(ValueError):
        U.UkladPlytki.bity_z_numeru(16, 4)
    with pytest.raises(ValueError):
        U.UkladPlytki.numer_z_bitow(2, 0, 0)
