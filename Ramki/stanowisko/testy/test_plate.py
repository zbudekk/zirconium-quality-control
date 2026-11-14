"""plate (P2): wyrównanie po 3 stożkach, numer z dołków, cięcie na gniazda — na sztucznych skanach z atrap.

R59 (14.11.2026): łańcuch plate jest sprawdzany na układzie R59 i na poprzednim ``*_r54`` (stare płytki fizyczne);
testy z liczbami układu R54 (punkt (0; 22,5), gniazdo 20 = rynienka, 3 dołki kodu na kwadracie) zostają na ``*_r54``
bez zmiany oczekiwań. Strażnik układu: testy/test_straznik.py.
"""
from __future__ import annotations

import math
import warnings

import numpy as np
import pytest
import trimesh

import atrapy_koron
from stanowisko import plate, synth, uklad as U


def _skan(uk: U.UkladPlytki, numer: int, projekty, seed: int, **opcje):
    rng = np.random.default_rng(seed)
    op = synth.Opcje.z_toml(plytka=uk.nazwa, prace_na_plytce=len(projekty), **opcje)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return synth.generuj_plytke(uk, numer, list(projekty), rng, op, seed)


@pytest.fixture(scope="module", params=["okragla_wieczorna", "okragla_wieczorna_r54"])
def skan_okragla(korony, request):
    """Płytka okrągła wieczorna n8 (dołki w polu), 3 atrapy, losowa poza skanu, pole ø100 — układ R59 i R54."""
    uk = U.wczytaj(request.param)
    skan, prawda = _skan(uk, 8, korony, seed=11, poza_uklad=True, pole=100.0, p_drgniecia=0.0)
    return uk, skan, prawda


def test_wyrownanie_numer_i_gniazda(skan_okragla):
    uk, skan, prawda = skan_okragla
    assert prawda.poza_skanu is not None and len(prawda.prace) == 3
    w = plate.wyrownaj(skan, uk)
    b = plate.blad_wyrownania(w.macierz, prawda.poza_skanu)
    assert b["max_przesuniecie_mm"] < 0.05 and b["translacja_mm"] < 0.03 and b["obrot_deg"] < 0.02, b
    assert w.jakosc["stozki_dopasowane"] >= 3 and w.jakosc["znaczniki_reszta_mm"] < 0.05
    assert w.jakosc["znaczniki_reszta_druga_mm"] > 1.0  # trójkąt nierównoboczny: drugie przypisanie wyraźnie gorsze
    assert w.numer == 8 and w.numer_zrodlo == "dolki" and w.bity == [False, False, False, True]
    prace = {f.gniazdo for f in w.fragmenty if f.status == "praca"}
    assert prace == {p.gniazdo for p in prawda.prace}
    assert all(f.status == "praca" for f in w.fragmenty), [(f.gniazdo, f.status, f.liczba) for f in w.fragmenty]
    assert set(w.gniazda_puste) == set(prawda.gniazda_puste) and w.gniazda_podwojne == []
    for f in w.fragmenty:  # fragment leży nad swoim gniazdem i ma normalne
        g = uk.gniazdo(f.gniazdo)
        assert g.zawiera(f.srodek[0], f.srodek[1], 0.5) and f.normalne.shape == f.punkty.shape and f.liczba > 1000
    assert w.jakosc["czas_s"] < 30


def test_numer_podany_wygrywa_z_ostrzezeniem(skan_okragla):
    uk, skan, _ = skan_okragla
    with pytest.warns(UserWarning, match="podany 9, z dołków odczytano 8"):
        w = plate.wyrownaj(skan, uk, numer=9, ciecie=False)
    assert w.numer == 9 and w.numer_zrodlo == "podany" and w.numer_z_dolkow == 8


@pytest.mark.parametrize("nazwa,bity", [("wieczorna_r54", [None, None, None]), ("wieczorna", [None, None, None, None])])  # R59: kwadrat ma też dołek D (r 52,5)
def test_kwadrat_dolki_poza_polem_wymaga_numeru(korony, nazwa, bity):
    """Na kwadracie dołki leżą na r 52–58, poza polem ø100: bity None, numer nieznany → --numer."""
    uk = U.wczytaj(nazwa)
    skan, prawda = _skan(uk, 2, korony[:2], seed=5, poza_uklad=True, pole=100.0, p_drgniecia=0.0)
    with pytest.warns(UserWarning, match="dołki kodu poza skanem"):
        w = plate.wyrownaj(skan, uk, ciecie=False)
    assert w.numer is None and w.numer_zrodlo == "nieznany" and w.bity == bity
    assert plate.blad_wyrownania(w.macierz, prawda.poza_skanu)["max_przesuniecie_mm"] < 0.05
    w2 = plate.wyrownaj(skan, uk, numer=2)
    assert w2.numer == 2 and w2.numer_zrodlo == "podany"
    assert {f.gniazdo for f in w2.fragmenty} == {p.gniazdo for p in prawda.prace}


def test_praca_poza_gniazdem_i_podwojna(korony):
    """Korona położona na wierzchu płytki między gniazdami → poza gniazdem; dwie w jednym ø15 → podwójne."""
    uk = U.wczytaj("okragla_wieczorna_r54")
    skan, prawda = _skan(uk, 8, korony[:1], seed=3, poza_uklad=False, p_drgniecia=0.0)
    rng = np.random.default_rng(1)
    k1 = trimesh.load(korony[0], force="mesh")
    k1.apply_transform(synth.orientacja_brzegiem_do_gory(k1))
    k1.apply_translation([0 - k1.centroid[0], 22.5 - k1.centroid[1], uk.thickness - k1.bounds[0, 2]])  # na wierzchu, y=22,5: 1,5 mm od ø15 (gniazdo 17) i od rynienki 20
    assert uk.najblizsze_gniazdo(0, 22.5, 1.0) is None
    ryn = uk.gniazdo(20)  # rynienka 60 × 15: dwie korony daleko od siebie = podwójne (stykające się korony zlewają się w jeden fragment)
    assert ryn.id not in {p.gniazdo for p in prawda.prace}
    k2 = trimesh.load(korony[0], force="mesh")
    k2.apply_transform(synth.orientacja_brzegiem_do_gory(k2))
    k2.apply_translation([ryn.x - 15 - k2.centroid[0], ryn.y - k2.centroid[1], ryn.z_dno + 1.0 - k2.bounds[0, 2]])
    k3 = trimesh.load(korony[1], force="mesh")
    k3.apply_transform(synth.orientacja_brzegiem_do_gory(k3))
    k3.apply_translation([ryn.x + 15 - k3.centroid[0], ryn.y - k3.centroid[1], ryn.z_dno + 1.0 - k3.bounds[0, 2]])
    for k in (k1, k2, k3):
        k.vertices += rng.normal(0, 0.02, k.vertices.shape)
    skan2 = trimesh.util.concatenate([skan, k1, k2, k3])
    w = plate.wyrownaj(skan2, uk)
    assert w.numer == 8
    poza = w.poza_gniazdem
    assert len(poza) == 1 and abs(poza[0].srodek[0]) < 1.5 and abs(poza[0].srodek[1] - 22.5) < 1.5
    assert w.gniazda_podwojne == [ryn.id]
    assert sum(1 for f in w.fragmenty if f.status == "podwojny" and f.gniazdo == ryn.id) == 2
    assert {f.gniazdo for f in w.fragmenty if f.status == "praca"} == {p.gniazdo for p in prawda.prace}
    assert ryn.id not in w.gniazda_puste


# --- części składowe ------------------------------------------------------------------
def test_kabsch_2d_bez_odbicia():
    A = np.array([[0, 0], [10, 0], [0, 7.0]])
    a = math.radians(33)
    R = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
    B = A @ R.T + [3, -4]
    R2, t2, rms = plate.kabsch_2d(A, B)
    assert rms < 1e-9 and np.allclose(R2, R) and np.allclose(t2, [3, -4])
    B_odb = A * [1, -1]  # odbicie: Kabsch bez odbicia nie dopasuje idealnie
    assert plate.kabsch_2d(A, B_odb)[2] > 1.0


@pytest.mark.parametrize("nazwa", ["poranna_r54", "poranna"])
def test_przypisz_znaczniki_z_nadmiarowym_i_permutacja(nazwa):
    uk = U.wczytaj(nazwa)  # R54: boki 60,0 / 60,7 / 88,4 — prawie równoramienny; R59: 55,9 / 79,4 / 86,5
    a = math.radians(-71)
    R = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
    cel = np.array([[z.x, z.y] for z in uk.markers])
    skan = cel @ R + [12.0, -5.0]  # skan = R⁻¹·płytka + t
    srodki = [{"x": x, "y": y} for x, y in skan[[2, 0, 1]]] + [{"x": 0.0, "y": 0.0}]  # kolejność zmieniona + fałszywy stożek
    T, j = plate.przypisz_znaczniki(srodki, uk)
    po = skan @ T[:2, :2].T + T[:2, 3]
    assert np.allclose(po, cel, atol=1e-9) and j["znaczniki_reszta_mm"] < 1e-9
    assert j["znaczniki_reszta_druga_mm"] > 0.3  # 0,67 mm różnicy boków wystarcza przy stożkach z dokładnością 0,01 mm
    with pytest.raises(plate.BladWyrownania, match="potrzeba 3"):
        plate.przypisz_znaczniki(srodki[:2], uk)
    with pytest.raises(plate.BladWyrownania, match="nie pasują"):
        plate.przypisz_znaczniki([{"x": 0, "y": 0}, {"x": 10, "y": 0}, {"x": 0, "y": 10}], uk)


def test_dopasuj_stozek_na_punktach_syntetycznych():
    zn = U.Znacznik("A", 3.0, -4.0, 5.0, 3.0)
    rng = np.random.default_rng(0)
    r = np.sqrt(rng.uniform(0, 1, 20000)) * 2.5
    t = rng.uniform(0, 2 * math.pi, 20000)
    P = np.c_[zn.x + r * np.cos(t), zn.y + r * np.sin(t), 5.0 + 1.2 * r + rng.normal(0, 0.03, 20000)]
    P = np.vstack([P, np.c_[rng.uniform(-5, 10, 5000), rng.uniform(-10, 5, 5000), np.full(5000, 8.0)]])  # wierzch płytki
    s = plate.dopasuj_stozek(P, (zn.x + 0.4, zn.y - 0.3), 8.0, zn)
    assert s is not None and abs(s["x"] - zn.x) < 0.01 and abs(s["y"] - zn.y) < 0.01 and abs(s["z_wierzcholka"] - 5.0) < 0.02
    assert s["rms"] < 0.05
    assert plate.dopasuj_stozek(P[-5000:], (0.0, 0.0), 8.0, zn) is None  # sama płaszczyzna: brak punktów stożka


@pytest.mark.parametrize("nazwa", ["wieczorna", "poranna", "wieczorna_r54", "poranna_r54"])
def test_kandydaci_znacznikow_z_mapy_wysokosci(nazwa):
    uk = U.wczytaj(nazwa)
    m = trimesh.load(uk.plik_stl(uk.numery[0]), force="mesh")
    m.update_faces(m.triangles_center[:, 2] > 0.5)
    P, _ = trimesh.sample.sample_surface(m, 1500000, seed=1)
    kand = plate.kandydaci_znacznikow(np.asarray(P), uk.thickness, uk.markers[0])
    assert len(kand) >= 3
    for z in uk.markers:
        assert min(math.hypot(x - z.x, y - z.y) for x, y in kand) < 0.4


@pytest.mark.parametrize("nazwa", ["okragla_poranna", "okragla_poranna_r54"])
def test_odczytaj_bity_i_blad_tozsamosci(nazwa):
    uk = U.wczytaj(nazwa)
    rng = np.random.default_rng(2)
    P = np.c_[rng.uniform(-45, 45, 200000), rng.uniform(-45, 45, 200000), np.full(200000, 8.0)]
    for d, obecny in zip(uk.code_dimples, (True, False, False, True)):  # n9 = A + D
        bl = np.hypot(P[:, 0] - d.x, P[:, 1] - d.y) < d.d / 2
        if obecny:
            P[bl, 2] = 7.0
    assert plate.odczytaj_bity(P, uk) == [True, False, False, True]
    assert uk.numer_z_bitow(*plate.odczytaj_bity(P, uk)) == 9
    assert plate.odczytaj_bity(P[np.hypot(P[:, 0], P[:, 1]) < 20], uk) == [None] * 4
    b = plate.blad_wyrownania(np.eye(4), None)
    assert b["translacja_mm"] == 0 and b["obrot_deg"] == 0 and b["max_przesuniecie_mm"] == 0
    T = trimesh.transformations.rotation_matrix(math.radians(0.1), [0, 0, 1])
    assert abs(plate.blad_wyrownania(T, None)["max_przesuniecie_mm"] - 50 * math.radians(0.1)) < 1e-4
