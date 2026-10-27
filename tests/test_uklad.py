"""Testy ukladu gniazd plytek (qc.uklad): format pliku ramki, walidacja K-05, kod numeru."""

import json
import math
from collections import Counter
from pathlib import Path

import pytest

from qc import uklad

KORZEN = Path(__file__).resolve().parent.parent
PLIKI = {
    "wieczorna": KORZEN / "modele" / "uklad_gniazd_wieczorna.json",
    "poranna": KORZEN / "modele" / "uklad_gniazd_poranna.json",
}
KLUCZE_RAMKI = {
    "plate", "version", "units", "coords", "size", "thickness", "markers", "notch", "code_dimples",
    "magnet_pockets", "number_relief", "sockets", "leds",
}
TAN15 = math.tan(math.radians(15.0))


def _surowy(nazwa):
    return json.loads(PLIKI[nazwa].read_text(encoding="utf-8"))


def _zapisz(tmp_path, dane, nazwa="uklad_gniazd_wieczorna.json"):
    sciezka = tmp_path / nazwa
    sciezka.write_text(json.dumps(dane), encoding="utf-8")
    return sciezka


# --- wlasna geometria obrysow (niezalezna od qc.uklad) ---------------------------


def _obrys(s):
    """Obrys gorny jako odcinek (p, q) i promien: kolo = odcinek zerowy, stadion = os + w/2."""
    if s["type"] == "round":
        p = (float(s["x"]), float(s["y"]))
        return p, p, s["d_top"] / 2
    pol = (s["l"] - s["w"]) / 2
    a = math.radians(s.get("angle", 0))
    dx, dy = pol * math.cos(a), pol * math.sin(a)
    return (s["x"] - dx, s["y"] - dy), (s["x"] + dx, s["y"] + dy), s["w"] / 2


def _punkt_odcinek(pt, p, q):
    vx, vy = q[0] - p[0], q[1] - p[1]
    dl2 = vx * vx + vy * vy
    t = 0.0 if dl2 == 0 else max(0.0, min(1.0, ((pt[0] - p[0]) * vx + (pt[1] - p[1]) * vy) / dl2))
    return math.hypot(pt[0] - p[0] - t * vx, pt[1] - p[1] - t * vy)


def _odcinek_odcinek(p1, q1, p2, q2):
    # odcinki obrysow sie nie przecinaja (inaczej obrysy i tak nachodza): minimum na koncach
    return min(_punkt_odcinek(p1, p2, q2), _punkt_odcinek(q1, p2, q2),
               _punkt_odcinek(p2, p1, q1), _punkt_odcinek(q2, p1, q1))


def _odstep(s1, s2):
    p1, q1, r1 = _obrys(s1)
    p2, q2, r2 = _obrys(s2)
    return _odcinek_odcinek(p1, q1, p2, q2) - r1 - r2


def _punkty_obrysu(s, n=72):
    p, q, r = _obrys(s)
    wynik = []
    for srodek in (p, q):
        for i in range(n):
            a = 2 * math.pi * i / n
            wynik.append((srodek[0] + r * math.cos(a), srodek[1] + r * math.sin(a)))
    return wynik


def _rzedy(sockets):
    rzedy = {}
    for s in sockets:
        rzedy.setdefault(round(s["y"], 2), []).append(s)
    return [rzedy[y] for y in sorted(rzedy)]


# --- 1. liczby gniazd -------------------------------------------------------------


def _sprawdz_wspolne(u):
    assert u.rozmiar == pytest.approx(96)
    assert u.grubosc == pytest.approx(8)
    assert set(u.znaczniki) == {"A", "B", "C"}
    assert tuple(u.znaczniki["A"]) == pytest.approx((-42, -42, 5, 3))
    assert tuple(u.znaczniki["B"]) == pytest.approx((-42, 42, 5, 3))
    assert tuple(u.znaczniki["C"]) == pytest.approx((42, 42, 5, 3))
    assert tuple(u.wyciecie) == pytest.approx((43, 48, -48, -43))
    assert set(u.dolki_kodu) == {"A", "B", "C"}
    assert tuple(u.dolki_kodu["A"]) == pytest.approx((-45, -36))
    assert tuple(u.dolki_kodu["B"]) == pytest.approx((-45, -33))
    assert tuple(u.dolki_kodu["C"]) == pytest.approx((-45, -30))
    for g in u.gniazda:
        assert g.glebokosc == pytest.approx(4)
        assert g.otwor_d == pytest.approx(3)
        if g.rodzaj == "stozek":
            assert g.d_dol == pytest.approx(g.d_gora - 2 * 4 * TAN15, abs=0.01)
            assert g.dlugosc is None and g.szerokosc is None and g.liczba_otworow is None
        else:
            assert g.rodzaj == "rynienka"
            assert g.d_gora is None and g.d_dol is None
            assert g.kat == pytest.approx(0)
            assert g.liczba_otworow == 4


def test_wieczorna_liczby():
    u = uklad.wczytaj(PLIKI["wieczorna"])
    assert u.nazwa == "wieczorna"
    assert list(u.numery) == [1, 2, 3]
    assert [g.nr for g in u.gniazda] == list(range(1, 27))
    okragle = [g for g in u.gniazda if g.rodzaj == "stozek"]
    rynienki = [g for g in u.gniazda if g.rodzaj == "rynienka"]
    assert len(okragle) == 24
    assert Counter(round(g.d_gora, 2) for g in okragle) == {9.0: 13, 12.0: 6, 15.0: 5}
    assert len(rynienki) == 2
    assert [g.nr for g in rynienki] == [25, 26]
    for g in rynienki:
        assert (g.dlugosc, g.szerokosc) == pytest.approx((60, 15))
        assert g.rozstaw_otworow == pytest.approx(12)
    assert tuple(u.gniazdo(25).xy) == pytest.approx((0, 19.5))
    assert tuple(u.gniazdo(26).xy) == pytest.approx((0, 37.5))
    g1 = u.gniazdo(1)
    assert tuple(g1.xy) == pytest.approx((30, -40.5))
    assert g1.d_gora == pytest.approx(9) and g1.d_dol == pytest.approx(6.86, abs=0.01)
    assert tuple(u.gniazdo(13).xy) == pytest.approx((-36, -28.5))
    _sprawdz_wspolne(u)


def test_poranna_liczby():
    u = uklad.wczytaj(PLIKI["poranna"])
    assert u.nazwa == "poranna"
    assert list(u.numery) == [4, 5, 6]
    assert [g.nr for g in u.gniazda] == list(range(1, 38))
    okragle = [g for g in u.gniazda if g.rodzaj == "stozek"]
    rynienki = [g for g in u.gniazda if g.rodzaj == "rynienka"]
    assert len(okragle) == 35
    assert Counter(round(g.d_gora, 2) for g in okragle) == {7.5: 22, 10.0: 7, 12.5: 6}
    assert len(rynienki) == 2
    assert [g.nr for g in rynienki] == [36, 37]
    for g in rynienki:
        assert (g.dlugosc, g.szerokosc) == pytest.approx((50, 13))
        assert g.rozstaw_otworow == pytest.approx(10)
    assert tuple(u.gniazdo(36).xy) == pytest.approx((0, 21.5))
    assert tuple(u.gniazdo(37).xy) == pytest.approx((0, 37.5))
    assert tuple(u.gniazdo(1).xy) == pytest.approx((26.25, -41.25))
    _sprawdz_wspolne(u)


# --- 2. walidacja K-05 na surowym JSON ---------------------------------------------


@pytest.mark.parametrize("nazwa", ["wieczorna", "poranna"])
def test_walidacja_k05(nazwa):
    d = _surowy(nazwa)
    s = d["sockets"]

    # id 1..N ciagle, rzedami od przodu (rosnace y), w rzedzie malejace x
    assert [g["id"] for g in s] == list(range(1, len(s) + 1))
    kolejnosc = [g["id"] for rzad in _rzedy(s) for g in sorted(rzad, key=lambda g: -g["x"])]
    assert kolejnosc == list(range(1, len(s) + 1))

    # rzedy symetryczne wzgledem x = 0
    for rzad in _rzedy(s):
        xs = sorted(g["x"] for g in rzad)
        lustro = sorted(-x for x in xs)
        assert all(abs(a - b) <= 0.01 for a, b in zip(xs, lustro)), f"rzad y={rzad[0]['y']}"

    for g in s:
        # obrysy w [-45, 45]^2 i poza kwadratami naroznymi (|x| > 35 i |y| > 35)
        for x, y in _punkty_obrysu(g):
            assert -45 - 1e-9 <= x <= 45 + 1e-9 and -45 - 1e-9 <= y <= 45 + 1e-9, f"gniazdo {g['id']}"
            assert not (abs(x) > 35 + 1e-9 and abs(y) > 35 + 1e-9), f"gniazdo {g['id']} w narozniku"
        # d_bottom = d_top - 2 depth tan 15
        if g["type"] == "round":
            assert abs(g["d_bottom"] - (g["d_top"] - 2 * g["depth"] * TAN15)) <= 0.01, f"gniazdo {g['id']}"
        else:
            assert g["type"] == "trough"
            assert g["hole_count"] == 4

    # min odleglosc obrysow gornych >= 3,0
    najmniejszy = min(_odstep(a, b) for i, a in enumerate(s) for b in s[i + 1:])
    assert najmniejszy >= 3.0 - 1e-6

    znaczniki = {m["corner"]: (m["x"], m["y"]) for m in d["markers"]}
    assert znaczniki == {"A": (-42, -42), "B": (-42, 42), "C": (42, 42)}
    assert all(m["d"] == 5 and m["depth"] == 3 for m in d["markers"])
    assert d["notch"] == {"corner": "D", "x_min": 43, "x_max": 48, "y_min": -48, "y_max": -43}
    dolki = {c["bit"]: (c["x"], c["y"]) for c in d["code_dimples"]}
    assert dolki == {"A": (-45, -36), "B": (-45, -33), "C": (-45, -30)}
    assert {m["corner"] for m in d["magnet_pockets"]} == {"A", "B", "C"}


# --- 3. bledy ukladu ----------------------------------------------------------------


def test_blad_ukladu(tmp_path):
    assert issubclass(uklad.BladUkladu, Exception)
    baza = _surowy("wieczorna")

    nachodzace = json.loads(json.dumps(baza))
    rynienka = next(g for g in nachodzace["sockets"] if g["id"] == 25)
    rynienka["w"] = 30  # siega do rzedu R4 i rynienki 26
    with pytest.raises(uklad.BladUkladu, match="gniazd"):
        uklad.wczytaj(_zapisz(tmp_path, nachodzace))

    bez_znacznikow = json.loads(json.dumps(baza))
    del bez_znacznikow["markers"]
    with pytest.raises(uklad.BladUkladu, match="markers"):
        uklad.wczytaj(_zapisz(tmp_path, bez_znacznikow))

    zle_dno = json.loads(json.dumps(baza))
    zle_dno["sockets"][0]["d_bottom"] = 7.5
    with pytest.raises(uklad.BladUkladu, match="d_bottom"):
        uklad.wczytaj(_zapisz(tmp_path, zle_dno))

    zle_id = json.loads(json.dumps(baza))
    zle_id["sockets"][0]["id"], zle_id["sockets"][1]["id"] = 2, 1
    with pytest.raises(uklad.BladUkladu, match="id"):
        uklad.wczytaj(_zapisz(tmp_path, zle_id))

    # nieznane klucze ignorowane
    dodatkowe = json.loads(json.dumps(baza))
    dodatkowe["nieznany_klucz"] = {"cokolwiek": 1}
    dodatkowe["leds"] = {"1": [0, 1]}
    u = uklad.wczytaj(_zapisz(tmp_path, dodatkowe))
    assert len(u.gniazda) == 26


# --- 4. gniazdo dla punktu ----------------------------------------------------------


def test_gniazdo_dla_xy():
    u = uklad.wczytaj(PLIKI["wieczorna"])
    g = u.gniazdo(13)
    x, y = g.xy
    assert u.gniazdo_dla_xy(x, y) == 13
    assert u.gniazdo_dla_xy(0.0, -34.5) is None  # scianka miedzy R1 i R2
    za_krawedzia = (x - g.d_gora / 2 - 0.5, y)
    assert u.gniazdo_dla_xy(*za_krawedzia) is None
    assert u.gniazdo_dla_xy(*za_krawedzia, margines=1.0) == 13
    assert u.gniazdo_dla_xy(10.0, 19.5) == 25
    assert u.gniazdo_dla_xy(-24.0, 37.5) == 26
    with pytest.raises((KeyError, ValueError, uklad.BladUkladu)):
        u.gniazdo(99)


# --- 5. kod numeru ------------------------------------------------------------------


def test_kod():
    oczekiwane = {1: {"A"}, 2: {"B"}, 3: {"A", "B"}, 4: {"C"}, 5: {"A", "C"}, 6: {"B", "C"}}
    for n, bity in oczekiwane.items():
        assert uklad.kod_numeru(n) == bity
        assert uklad.numer_z_kodu(bity) == n
    assert uklad.numer_z_kodu(set()) is None
    assert uklad.numer_z_kodu({"A", "B", "C"}) is None


# --- 6. zgodnosc z formatem ramki ---------------------------------------------------


@pytest.mark.parametrize("nazwa", ["wieczorna", "poranna"])
def test_zgodnosc_z_ramka(nazwa):
    d = _surowy(nazwa)
    assert set(d) == KLUCZE_RAMKI
    assert d["plate"] == nazwa
    assert d["version"] == "v2"
    assert d["units"] == "mm"
    assert d["size"] == 96 and d["thickness"] == 8
    assert set(d["coords"]) == {"origin", "x", "y", "notch_corner"}
    assert {k: d["number_relief"][k] for k in ("x", "y", "text_h")} == {"x": 39.5, "y": -44.5, "text_h": 5}
    if nazwa == "wieczorna":
        assert d["sockets"][0] == {"id": 1, "type": "round", "x": 30, "y": -40.5, "d_top": 9,
                                   "d_bottom": 6.86, "depth": 4, "hole_d": 3}
        s25 = next(g for g in d["sockets"] if g["id"] == 25)
        assert s25 == {"id": 25, "type": "trough", "x": 0, "y": 19.5, "l": 60, "w": 15, "angle": 0,
                       "depth": 4, "hole_d": 3, "hole_pitch": 12, "hole_count": 4}
    else:
        s36 = next(g for g in d["sockets"] if g["id"] == 36)
        assert s36 == {"id": 36, "type": "trough", "x": 0, "y": 21.5, "l": 50, "w": 13, "angle": 0,
                       "depth": 4, "hole_d": 3, "hole_pitch": 10, "hole_count": 4}
    dozwolone = {"round": {"id", "type", "x", "y", "d_top", "d_bottom", "depth", "hole_d"},
                 "trough": {"id", "type", "x", "y", "l", "w", "angle", "depth", "hole_d", "hole_pitch",
                            "hole_count"}}
    for g in d["sockets"]:
        assert set(g) == dozwolone[g["type"]], f"gniazdo {g['id']}"
