"""Edge-case'y modułu stanowisko/uklad.py. Identyfikatory znalezisk: znaleziska.md."""
import json
import math

import pytest

from conftest import U, STANOWISKO


# --- wczytywanie uklad.json ---------------------------------------------------
def test_brak_pliku_ukladu_daje_czytelny_blad(uklad_tmp):
    uklad_tmp("wieczorna")
    with pytest.raises(FileNotFoundError, match="uklad.json"):
        U.wczytaj("nieistniejaca")


@pytest.mark.xfail(reason="ZNALEZISKO U1: brak walidacji uklad.json — pusty JSON kończy się gołym KeyError('sockets') bez nazwy pliku", strict=True)
def test_pusty_uklad_json_zglasza_blad_z_nazwa_pliku(uklad_tmp):
    uklad_tmp("wieczorna", zmien=lambda d: {})
    with pytest.raises(ValueError, match="uklad.json"):
        U.wczytaj("wieczorna")


@pytest.mark.xfail(reason="ZNALEZISKO U1: gniazdo okrągłe bez d_top przechodzi przez wczytaj(); błąd (TypeError) dopiero przy promien_gorny/zawiera", strict=True)
def test_gniazdo_bez_d_top_odrzucone_przy_wczytaniu(uklad_tmp):
    def zmien(d):
        del d["sockets"][0]["d_top"]
        return d

    uklad_tmp("wieczorna", zmien=zmien)
    with pytest.raises(ValueError):
        U.wczytaj("wieczorna")


def test_gniazdo_bez_d_top_wybucha_dopiero_przy_uzyciu(uklad_tmp):
    """Obserwowane zachowanie (dokumentacja U1): wczytaj() przechodzi, zawiera() rzuca TypeError."""
    def zmien(d):
        del d["sockets"][0]["d_top"]
        return d

    uklad_tmp("wieczorna", zmien=zmien)
    uk = U.wczytaj("wieczorna")
    g = uk.gniazdo(1)
    with pytest.raises(TypeError):
        g.zawiera(g.x, g.y)
    with pytest.raises(TypeError):
        _ = g.promien_gorny


@pytest.mark.xfail(reason="ZNALEZISKO U1: nieznany typ gniazda ('square') nie jest odrzucany — traktowany jak rynienka z l=w=None", strict=True)
def test_nieznany_typ_gniazda_odrzucony(uklad_tmp):
    def zmien(d):
        d["sockets"][0]["type"] = "square"
        return d

    uklad_tmp("wieczorna", zmien=zmien)
    with pytest.raises(ValueError):
        U.wczytaj("wieczorna")


@pytest.mark.xfail(reason="ZNALEZISKO U1: gniazdo poza płytką (x=60 przy size=96, d_top=9) nie jest wykrywane przy wczytaniu", strict=True)
def test_gniazdo_poza_plytka_odrzucone(uklad_tmp):
    def zmien(d):
        d["sockets"][0]["x"] = 60.0
        return d

    uklad_tmp("wieczorna", zmien=zmien)
    with pytest.raises(ValueError):
        U.wczytaj("wieczorna")


def test_pusta_lista_gniazd_wczytuje_sie_a_najblizsze_wybucha(uklad_tmp):
    uklad_tmp("wieczorna", zmien=lambda d: {**d, "sockets": []})
    uk = U.wczytaj("wieczorna")
    assert uk.sockets == []
    with pytest.raises(ValueError):  # min() arg is an empty sequence — ZNALEZISKO U1 (brak komunikatu)
        uk.najblizsze_gniazdo(0, 0)


def test_dodatkowe_pole_w_znaczniku_wybucha(uklad_tmp):
    """Znacznik(**m) nie toleruje nowych kluczy — rozszerzenie JSON (np. 'uwaga') psuje wczytanie. ZNALEZISKO U1."""
    def zmien(d):
        d["markers"][0]["uwaga"] = "test"
        return d

    uklad_tmp("wieczorna", zmien=zmien)
    with pytest.raises(TypeError):
        U.wczytaj("wieczorna")


# --- numery płytek z nazw plików ---------------------------------------------
def test_numery_z_plikow_stl(uklad_tmp):
    uklad_tmp("wieczorna", pliki=("plytka_n3.stl", "plytka_n1.stl"))
    assert U.wczytaj("wieczorna").numery == [1, 3]


@pytest.mark.xfail(reason="ZNALEZISKO U2: plik plytka_n1_kopia.stl w katalogu modeli wysadza wczytaj() (ValueError z int())", strict=True)
def test_obcy_plik_plytka_n_kopia_nie_psuje_wczytania(uklad_tmp):
    uklad_tmp("wieczorna", pliki=("plytka_n1.stl", "plytka_n1_kopia.stl"))
    assert U.wczytaj("wieczorna").numery == [1]


def test_plik_plytka_n1_0_daje_numer_10(uklad_tmp):
    """int('1_0') == 10 — podkreślenie w nazwie zmienia numer płytki. ZNALEZISKO U2 (obserwowane)."""
    uklad_tmp("wieczorna", pliki=("plytka_n1_0.stl",))
    assert U.wczytaj("wieczorna").numery == [10]


@pytest.mark.parametrize("n", [0, 7, -1, 99])
def test_plik_stl_spoza_zakresu(n):
    uk = U.wczytaj("wieczorna")
    with pytest.raises(FileNotFoundError):
        uk.plik_stl(n)


def test_plik_stl_poranny_w_wieczornej():
    with pytest.raises(FileNotFoundError):
        U.wczytaj("wieczorna").plik_stl(4)


# --- kody płytek -------------------------------------------------------------
def test_kody_1_do_6_zgodne_z_arkuszem_kody_plytek():
    # kody_plytek.md: 1=A, 2=B, 3=A+B, 4=C, 5=A+C, 6=B+C
    oczek = {1: (1, 0, 0), 2: (0, 1, 0), 3: (1, 1, 0), 4: (0, 0, 1), 5: (1, 0, 1), 6: (0, 1, 1)}
    for n, b in oczek.items():
        assert U.UkladPlytki.bity_z_numeru(n) == tuple(map(bool, b))


@pytest.mark.xfail(reason="ZNALEZISKO U3: bity_z_numeru(8) zwraca (F,F,F) jak dla 0, bity_z_numeru(-1) → (T,T,T); brak kontroli zakresu 0…7", strict=True)
def test_numer_poza_zakresem_3_bitow_odrzucony():
    with pytest.raises(ValueError):
        U.UkladPlytki.bity_z_numeru(8)


def test_numer_z_bitow_przyjmuje_liczby_calkowite_bez_kontroli():
    """numer_z_bitow(2, 0, 0) == 2 zamiast błędu — ZNALEZISKO U3 (obserwowane)."""
    assert U.UkladPlytki.numer_z_bitow(2, 0, 0) == 2


# --- geometria gniazd ----------------------------------------------------------
@pytest.mark.xfail(reason="ZNALEZISKO B2: najblizsze_gniazdo liczy odległość do ŚRODKA — punkt wewnątrz rynienki 25 (28, 19.5) dostaje gniazdo okrągłe 20", strict=True)
def test_najblizsze_gniazdo_punkt_w_rynience():
    uk = U.wczytaj("wieczorna")
    assert uk.gniazdo(25).zawiera(28, 19.5)
    assert uk.najblizsze_gniazdo(28, 19.5).id == 25


@pytest.mark.xfail(reason="ZNALEZISKO B2: punkt daleko poza płytką (100, 100) dostaje gniazdo 20 zamiast informacji 'poza gniazdem'", strict=True)
def test_najblizsze_gniazdo_poza_plytka():
    uk = U.wczytaj("wieczorna")
    g = uk.najblizsze_gniazdo(100, 100)
    assert g is None or g.zawiera(100, 100, margines=5)


def test_zawiera_rynienka_obrocona_o_90():
    r = U.Gniazdo(id=99, typ="trough", x=0, y=0, depth=4, l=60, w=15, angle=90)
    assert r.zawiera(0, 29) and not r.zawiera(29, 0)
    assert r.zawiera(7, 0) and not r.zawiera(8, 0)


def test_zawiera_margines_ujemny():
    g = U.wczytaj("wieczorna").gniazdo(1)  # ø9
    assert g.zawiera(g.x + 3.4, g.y, margines=-1.0) and not g.zawiera(g.x + 3.6, g.y, margines=-1.0)


def test_promien_dolny_rynienki_zgodny_ze_stl():
    r = U.wczytaj("wieczorna").rynienki()[0]
    assert r.promien_dolny() == pytest.approx(15 / 2 - 4 * math.tan(math.radians(15)), abs=1e-6)  # 6.43 w STL


@pytest.mark.parametrize("nazwa", ["wieczorna", "poranna"])
def test_d_bottom_z_jsona_zgodne_z_katem_15_stopni(nazwa):
    for g in U.wczytaj(nazwa).gniazda_okragle():
        assert g.d_bottom == pytest.approx(g.d_top - 2 * g.depth * math.tan(math.radians(U.KAT_SCIANKI_DEG)), abs=0.01)


@pytest.mark.parametrize("nazwa", ["wieczorna", "poranna"])
def test_scianki_3mm_takze_okragle_vs_rynienki_i_poranna(nazwa):
    """testy/test_uklad.py sprawdza tylko okr↔okr w wieczornej."""
    uk = U.wczytaj(nazwa)
    okr, ryn = uk.gniazda_okragle(), uk.rynienki()
    for i, a in enumerate(okr):
        for b in okr[i + 1:]:
            assert math.hypot(a.x - b.x, a.y - b.y) - a.d_top / 2 - b.d_top / 2 >= 3.0 - 1e-6
        for r in ryn:
            if abs(a.x - r.x) <= r.l / 2:
                assert abs(a.y - r.y) - r.w / 2 - a.d_top / 2 >= 3.0 - 1e-6
    assert abs(ryn[0].y - ryn[1].y) - ryn[0].w >= 3.0 - 1e-6
    # strefa gniazd 90 × 90 (parametry.json socket_zone)
    for g in uk.sockets:
        assert abs(g.x) + g.promien_gorny <= 45 + 1e-6 and abs(g.y) + (g.d_top if g.okragle else g.w) / 2 <= 45 + 1e-6


# --- układ współrzędnych / stałe -----------------------------------------------
def test_z_top_rowne_grubosci_z_jsona():
    for n in ("wieczorna", "poranna"):
        assert U.Z_TOP == U.wczytaj(n).thickness == 8


@pytest.mark.xfail(reason="ZNALEZISKO U4: Z_TOP=8 zaszyte w kodzie; zmiana 'thickness' w uklad.json nie przesuwa dna gniazda (z_dno nadal 4)", strict=True)
def test_z_dno_podaza_za_thickness_z_jsona(uklad_tmp):
    uklad_tmp("wieczorna", zmien=lambda d: {**d, "thickness": 10})
    uk = U.wczytaj("wieczorna")
    assert uk.thickness == 10
    assert uk.gniazdo(1).z_dno == pytest.approx(10 - 4)


def test_uklad_json_identyczny_z_wyniki_v2():
    for n in ("wieczorna", "poranna"):
        a = (STANOWISKO / "modele_plytek" / n / "uklad.json").read_bytes()
        b = (STANOWISKO.parent / "wyniki_v2" / "json" / f"uklad_gniazd_{n}.json").read_bytes()
        assert a == b


def test_uklad_json_zgodny_z_parametry_json():
    par = json.loads((STANOWISKO.parent / "parametry.json").read_text(encoding="utf-8"))["plytka"]
    v = lambda k: par[k]["value"]  # noqa: E731
    for n, rows in (("wieczorna", "ev_rows"), ("poranna", "mo_rows")):
        uk = U.wczytaj(n)
        oczek = sorted((r["type"], x, r["y"], r.get("d"), r.get("l"), r.get("w")) for r in v(rows) for x in r["x"])
        got = sorted((g.typ, g.x, g.y, g.d_top, g.l, g.w) for g in uk.sockets)
        assert oczek == got
        for i, d in enumerate(uk.code_dimples):
            assert (d.x, d.y, d.d, d.depth) == (v("code_dimple_x"), v("code_dimple_y0") + i * v("code_dimple_pitch"), v("code_dimple_d"), v("code_dimple_depth"))
        for m in uk.markers:
            assert abs(m.x) == abs(m.y) == uk.size / 2 - v("marker_offset") and m.d == v("marker_cone_d") and m.depth == v("marker_cone_depth")
        assert all(g.depth == v("socket_depth") for g in uk.sockets)
        assert U.KAT_SCIANKI_DEG == v("socket_wall_angle")  # ZNALEZISKO U5: ta sama liczba w 3 miejscach
