import math

import pytest

from stanowisko import uklad as U


@pytest.mark.parametrize("nazwa,n_okr,n_ryn,numery", [("wieczorna", 18, 2, [1, 2, 3]), ("poranna", 31, 2, [4, 5, 6])])  # R54: układ w kole r 47
def test_uklad_zgodny_z_planem(nazwa, n_okr, n_ryn, numery):
    uk = U.wczytaj(nazwa)
    assert uk.size == 96 and uk.thickness == 8
    assert len(uk.gniazda_okragle()) == n_okr
    assert len(uk.rynienki()) == n_ryn
    assert len(uk.markers) == 3 and len(uk.code_dimples) == 3
    assert uk.numery == numery
    for n in numery:
        assert uk.plik_stl(n).exists()


def test_gniazda_nie_nachodza_i_scianka_3mm():
    uk = U.wczytaj("wieczorna")
    okr = uk.gniazda_okragle()
    for i, a in enumerate(okr):
        for b in okr[i + 1 :]:
            d = math.hypot(a.x - b.x, a.y - b.y)
            assert d >= a.d_top / 2 + b.d_top / 2 + 3.0 - 1e-6, (a.id, b.id, d)


def test_geometria_gniazda():
    g = U.wczytaj("wieczorna").gniazdo(8)  # R54: id 1 to rynienka przednia; 8–14 = ø9
    assert g.okragle and g.d_top == 9
    assert g.z_dno == 4.0
    assert abs(g.promien_dolny() - 6.86 / 2) < 1e-6
    assert g.zawiera(g.x + 4.4, g.y) and not g.zawiera(g.x + 4.6, g.y)


def test_rynienka_zawiera():
    r = U.wczytaj("wieczorna").rynienki()[0]
    assert r.zawiera(r.x + 29, r.y + 7) and not r.zawiera(r.x + 31, r.y)


def test_kody_plytek():
    for n in range(8):
        assert U.UkladPlytki.numer_z_bitow(*U.UkladPlytki.bity_z_numeru(n)) == n
    assert U.UkladPlytki.bity_z_numeru(5) == (True, False, True)
