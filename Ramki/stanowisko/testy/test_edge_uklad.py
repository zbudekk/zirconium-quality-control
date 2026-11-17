"""uklad.py: walidacja uklad.json (U1–U4), najblizsze_gniazdo (B2), geometria gniazd.

Przeniesione z sesje_2026-10-31/kod_a_stanowisko/testy_edge/test_edge_uklad.py (xfail zdjęty
po naprawie P1 2026-11-02; numery gniazd dopasowane do układu R54) + nowe przypadki.
R59 (14.11.2026): testy z liczbami układu R54 (20 gniazd, ø9, dwie rynienki, 3 dołki kodu) działają na
``wieczorna_r54`` / ``poranna_r54`` bez zmiany oczekiwań; układ R59: testy/test_uklad_r59.py.
"""
import json
import math

import pytest

from conftest import RAMKI, STANOWISKO
from stanowisko import uklad as U


def pierwsze_okragle(d: dict) -> dict:
    return next(s for s in d["sockets"] if s["type"] == "round")


# --- walidacja uklad.json (U1) --------------------------------------------------
def test_pusty_uklad_json_zglasza_blad_z_nazwa_pliku(uklad_tmp):
    uklad_tmp("wieczorna", zmien=lambda d: {})
    with pytest.raises(ValueError, match=r"uklad\.json"):
        U.wczytaj("wieczorna")


def test_gniazdo_bez_d_top_odrzucone_przy_wczytaniu(uklad_tmp):
    def zmien(d):
        s = pierwsze_okragle(d)
        del s["d_top"]
        zmien.id = s["id"]

    uklad_tmp("wieczorna", zmien=zmien)
    with pytest.raises(U.BladUkladu, match=rf"uklad\.json: gniazdo {zmien.id}: brak d_top"):
        U.wczytaj("wieczorna")


def test_nieznany_typ_gniazda_odrzucony(uklad_tmp):
    def zmien(d):
        d["sockets"][0]["type"] = "square"

    uklad_tmp("wieczorna", zmien=zmien)
    with pytest.raises(ValueError, match="type 'square'"):
        U.wczytaj("wieczorna")


def test_gniazdo_poza_plytka_odrzucone(uklad_tmp):
    def zmien(d):
        d["sockets"][0]["x"] = 60.0

    uklad_tmp("wieczorna", zmien=zmien)
    with pytest.raises(ValueError, match="poza obrys"):
        U.wczytaj("wieczorna")


def test_pusta_lista_gniazd_odrzucona(uklad_tmp):
    uklad_tmp("wieczorna", zmien=lambda d: {**d, "sockets": []})
    with pytest.raises(U.BladUkladu, match="co najmniej jedno gniazdo"):
        U.wczytaj("wieczorna")


@pytest.mark.parametrize("klucz", ["plate", "thickness", "markers", "code_dimples", "sockets"])
def test_brak_wymaganego_klucza(uklad_tmp, klucz):
    uklad_tmp("wieczorna", zmien=lambda d: {k: v for k, v in d.items() if k != klucz})
    with pytest.raises(U.BladUkladu, match=f"brak klucza '{klucz}'"):
        U.wczytaj("wieczorna")


def test_zly_json_ma_nazwe_pliku(uklad_tmp):
    kat = uklad_tmp("wieczorna")
    (kat / "uklad.json").write_text("{nie json", encoding="utf-8")
    with pytest.raises(U.BladUkladu, match=r"uklad\.json: błąd składni JSON"):
        U.wczytaj("wieczorna")


def test_dodatkowe_pole_w_znaczniku_tolerowane(uklad_tmp):
    def zmien(d):
        d["markers"][0]["uwaga"] = "test"

    uklad_tmp("wieczorna", zmien=zmien)
    assert U.wczytaj("wieczorna").markers[0].corner == "A"


def test_shape_domyslnie_kwadrat_i_okragla_z_d(uklad_tmp):
    uklad_tmp("wieczorna", zrodlo="wieczorna_r54")  # plik R54 nie ma pola shape (plik R59 ma "square")
    uk = U.wczytaj("wieczorna")
    assert uk.shape == "square" and uk.d is None
    uklad_tmp("okragla", zmien=lambda d: {**{k: v for k, v in d.items() if k != "size"}, "shape": "round", "d": 100.0}, zrodlo="wieczorna_r54")
    uk = U.wczytaj("okragla")
    assert uk.shape == "round" and uk.d == 100.0 and len(uk.sockets) == 20
    uklad_tmp("zla", zmien=lambda d: {**d, "shape": "hex"}, zrodlo="wieczorna_r54")
    with pytest.raises(U.BladUkladu, match="shape"):
        U.wczytaj("zla")


def test_okragla_plytka_gniazdo_poza_kolem_odrzucone(uklad_tmp):
    # rynienka 60 × 15 przy y = ±31,5 ma narożniki w odległości ~45 mm od środka: koło ø80 jej nie mieści
    uklad_tmp("okragla", zmien=lambda d: {**d, "shape": "round", "d": 80.0}, zrodlo="wieczorna_r54")
    with pytest.raises(U.BladUkladu, match="poza obrys"):
        U.wczytaj("okragla")


def test_bit_d_kodu_opcjonalny(uklad_tmp):
    def zmien(d):
        d["code_dimples"].append({"bit": "D", "x": -45.0, "y": -27, "d": 2, "depth": 1})

    uklad_tmp("wieczorna", zmien=zmien, pliki=("plytka_n1.stl", "plytka_n9.stl"), zrodlo="wieczorna_r54")  # plik R54: 3 dołki
    uk = U.wczytaj("wieczorna")
    assert uk.liczba_bitow == 4 and uk.numery == [1, 9]
    assert uk.bity_z_numeru(9, uk.liczba_bitow) == (True, False, False, True)


def test_numer_plytki_za_duzy_na_3_dolki(uklad_tmp):
    uklad_tmp("wieczorna", pliki=("plytka_n1.stl", "plytka_n9.stl"), zrodlo="wieczorna_r54")
    with pytest.raises(U.BladUkladu, match="plytka_n9.stl"):
        U.wczytaj("wieczorna")


def test_z_dno_podaza_za_thickness_z_jsona(uklad_tmp):
    uklad_tmp("wieczorna", zmien=lambda d: {**d, "thickness": 10})
    uk = U.wczytaj("wieczorna")
    assert uk.thickness == 10
    assert uk.gniazdo(1).z_top == 10 and uk.gniazdo(1).z_dno == pytest.approx(10 - 4)


# --- numery płytek z nazw plików (U2) -------------------------------------------
def test_obcy_plik_plytka_n_kopia_nie_psuje_wczytania(uklad_tmp):
    uklad_tmp("wieczorna", pliki=("plytka_n1.stl", "plytka_n1_kopia.stl", "plytka_n1_0.stl"))
    with pytest.warns(UserWarning, match="pomijam plik"):
        assert U.wczytaj("wieczorna").numery == [1]


# --- kody płytek (U3) ---------------------------------------------------------------
def test_numer_poza_zakresem_3_bitow_odrzucony():
    with pytest.raises(ValueError):
        U.UkladPlytki.bity_z_numeru(8)


# --- najblizsze_gniazdo (B2) ----------------------------------------------------------
@pytest.mark.parametrize("nazwa", ["wieczorna", "wieczorna_r54"])
def test_najblizsze_gniazdo_punkt_w_rynience(nazwa):
    """Punkt przy końcu rynienki jest bliżej środka gniazda okrągłego niż środka rynienki — wygrywa rynienka."""
    uk = U.wczytaj(nazwa)
    r = uk.rynienki()[0]
    x, y = r.x + r.l / 2 - 1.0, r.y + 0.5 * (1 if r.y < 0 else -1)  # w półokrągłym końcu stadionu
    assert r.zawiera(x, y)
    po_srodkach = min(uk.sockets, key=lambda g: math.hypot(g.x - x, g.y - y))
    assert po_srodkach.id != r.id  # stary algorytm (do środka) dawał złe gniazdo
    assert uk.najblizsze_gniazdo(x, y).id == r.id


@pytest.mark.parametrize("nazwa", ["wieczorna", "wieczorna_r54"])
def test_najblizsze_gniazdo_poza_plytka(nazwa):
    uk = U.wczytaj(nazwa)
    assert uk.najblizsze_gniazdo(100, 100) is None
    assert uk.najblizsze_gniazdo(100, 100, margines=5) is None


def test_najblizsze_gniazdo_na_scianie_miedzy_gniazdami():
    uk = U.wczytaj("wieczorna_r54")
    g = next(g for g in uk.gniazda_okragle() if g.d_top == 9)
    x, y = g.x + g.d_top / 2 + 1.0, g.y  # 1 mm za obrysem, w ściance ≥ 3 mm
    assert uk.najblizsze_gniazdo(x, y) is None
    assert uk.najblizsze_gniazdo(x, y, margines=1.2).id == g.id


def test_odleglosc_do_obrysu():
    r = U.Gniazdo(id=99, typ="trough", x=0, y=0, depth=4, l=60, w=15, angle=90)
    assert r.odleglosc_do_obrysu(0, 0) == pytest.approx(-7.5)
    assert r.odleglosc_do_obrysu(10, 0) == pytest.approx(2.5)  # po obrocie o 90° szerokość leży wzdłuż x
    assert r.odleglosc_do_obrysu(7.5 + 3, 30 + 4) == pytest.approx(math.hypot(34 - 22.5, 10.5) - 7.5)  # stadion: od środka półokręgu końca (D4)
    assert r.odleglosc_do_obrysu(0, 30) == pytest.approx(0.0) and r.odleglosc_do_obrysu(7.4, 22.5) == pytest.approx(-0.1)
    k = U.Gniazdo(id=98, typ="round", x=1, y=1, depth=4, d_top=10, d_bottom=7.86)
    assert k.odleglosc_do_obrysu(1, 1) == pytest.approx(-5) and k.odleglosc_do_obrysu(1, 9) == pytest.approx(3)


# --- geometria (przeniesione bez zmian / dopasowane do R54) -----------------------------
def test_zawiera_margines_ujemny():
    g = next(g for g in U.wczytaj("wieczorna_r54").gniazda_okragle() if g.d_top == 9)
    assert g.zawiera(g.x + 3.4, g.y, margines=-1.0) and not g.zawiera(g.x + 3.6, g.y, margines=-1.0)


@pytest.mark.parametrize("nazwa", ["wieczorna_r54", "poranna_r54"])
def test_scianki_3mm_takze_okragle_vs_rynienki_i_poranna(nazwa):
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


def test_uklad_json_zgodny_z_parametry_json():
    par = json.loads((RAMKI / "parametry.json").read_text(encoding="utf-8"))["plytka"]
    v = lambda k: par[k]["value"]  # noqa: E731
    for n, rows, prefiks in (("wieczorna", "ev_rows", "ev"), ("poranna", "mo_rows", "mo")):
        uk = U.wczytaj(n)
        oczek = sorted((r["type"], x, r["y"], r.get("d"), r.get("l"), r.get("w")) for r in v(rows) for x in r["x"])
        got = sorted((g.typ, g.x, g.y, g.d_top, g.l, g.w) for g in uk.sockets)
        assert oczek == got
        for i, d in enumerate(uk.code_dimples):
            assert (d.x, d.y, d.d, d.depth) == (v("code_dimple_x"), v("code_dimple_y0") + i * v("code_dimple_pitch"), v("code_dimple_d"), v("code_dimple_depth"))
        pozycje = v(f"{prefiks}_marker_pos")  # R54: znaczniki w kole pola skanowania, pozycje per płytka
        for m in uk.markers:
            assert [m.x, m.y] == pozycje[m.corner] and m.d == v("marker_cone_d") and m.depth == v("marker_cone_depth")
        assert all(g.depth == v("socket_depth") for g in uk.sockets)
        assert uk.thickness == v("plate_thickness") and uk.size == v("plate_size")
        assert U.KAT_SCIANKI_DEG == v("socket_wall_angle")  # U5: ta sama liczba w 3 miejscach


def test_modele_plytek_bez_zmian_w_kodzie():
    """Kod czytający nie wymaga pól shape / bitu D: pliki układu R54 ich nie mają i wczytują się."""
    for n in ("wieczorna_r54", "poranna_r54"):
        d = json.loads((STANOWISKO / "modele_plytek" / n / "uklad.json").read_text(encoding="utf-8"))
        assert "shape" not in d and [c["bit"] for c in d["code_dimples"]] == ["A", "B", "C"]
        assert U.wczytaj(n).shape == "square"
