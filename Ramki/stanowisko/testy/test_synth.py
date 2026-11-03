import numpy as np
import pytest
import trimesh

import atrapy_koron  # ścieżka: testy/conftest.py
from stanowisko import synth, uklad as U


@pytest.fixture(scope="module")
def projekty(tmp_path_factory):
    d = tmp_path_factory.mktemp("stl")
    rng = np.random.default_rng(3)
    pliki = []
    for i, t in enumerate(["siekacz", "przedtrzonowy", "trzonowy"]):
        W, L, H, g, amp = atrapy_koron.TYPY[t]
        m = atrapy_koron.korona(W, L, H, g, amp, n_theta=96, n_u=120, rng=rng)
        p = d / f"a{i}_{t}.stl"
        m.export(p)
        pliki.append(p)
    return pliki


def test_atrapa_szczelna_i_brzeg_na_dole(projekty):
    m = trimesh.load(projekty[2])
    assert m.is_watertight
    assert m.bounds[0, 2] == pytest.approx(0.0, abs=1e-6)
    O = synth.orientacja_brzegiem_do_gory(m)
    assert O[2, 2] == pytest.approx(-1.0)  # obrót o 180° wokół x
    m.apply_transform(O)
    # po obróceniu brzeg (dawniej z=0) jest najwyżej: max z = 0 (z dokładnością do zaokrągleń), reszta poniżej
    assert m.bounds[1, 2] == pytest.approx(0.0, abs=1e-9) and m.bounds[0, 2] < -5.0


def test_ubytek_jest_pod_powierzchnia(projekty):
    m = trimesh.load(projekty[1])
    m.apply_transform(synth.orientacja_brzegiem_do_gory(m))
    rng = np.random.default_rng(0)
    przed = m.copy()
    po, ub = synth.wytnij_ubytek(m, 0.5, rng, pas_brzegu=2.0)
    assert ub.glebokosc == pytest.approx(0.175)
    # punkty nowej czaszy leżą wewnątrz oryginalnej bryły (ubytek = brak materiału)
    c = np.array([ub.x, ub.y, ub.z])
    nowe = po.vertices[np.linalg.norm(po.vertices - c, axis=1) < 0.24]
    assert len(nowe) > 20
    # trimesh.signed_distance: dodatnia = WEWNĄTRZ bryły (w materiale), ujemna = na zewnątrz
    odl = trimesh.proximity.signed_distance(przed, nowe)
    assert (odl > -0.02).mean() > 0.9
    assert odl.max() > 0.1  # czasza sięga w głąb materiału (głębokość ubytku 0,175)
    # i brzeg ubytku leży w pasie brzegu pracy (górne 2 mm)
    assert ub.z > m.bounds[1, 2] - 2.0


def test_szum_ma_zadane_odchylenie(projekty):
    m = trimesh.load(projekty[0])
    rng = np.random.default_rng(1)
    s = synth.dodaj_szum(m, 0.03, rng)
    d = ((s.vertices - m.vertices) * m.vertex_normals).sum(1)  # przesunięcie wzdłuż normalnej, ze znakiem
    assert 0.025 < d.std() < 0.035 and abs(d.mean()) < 0.002


@pytest.mark.parametrize("nazwa", ["wieczorna", "poranna"])
def test_osadzenie_w_gniezdzie_trzyma_sie_stozka(projekty, nazwa):
    """T4: wiele seedów i wszystkie rozmiary gniazd obu płytek (pełna siatka: test_edge_synth.py)."""
    uk = U.wczytaj(nazwa)
    m = trimesh.load(projekty[1])
    m.apply_transform(synth.orientacja_brzegiem_do_gory(m) @ trimesh.transformations.scale_matrix(1.22))
    osadzen = 0
    for d in sorted({g.d_top for g in uk.gniazda_okragle()}):
        g = next(g for g in uk.gniazda_okragle() if g.d_top == d)
        for seed in range(10):
            T = synth.osadz_w_gniezdzie(m, g, np.random.default_rng(seed))
            if T is None:
                continue
            osadzen += 1
            V = trimesh.transform_points(m.vertices, T)
            rho = np.hypot(V[:, 0] - g.x, V[:, 1] - g.y)
            z = V[:, 2]
            assert z.min() >= g.z_dno - 1e-6
            w_gn = z < g.z_top
            dop = g.promien_dolny() + (z[w_gn] - g.z_dno) * synth.TAN_SCIANKI
            assert (rho[w_gn] <= dop + 1e-6).all(), (nazwa, d, seed)
    assert osadzen >= 20


def test_za_male_gniazdo_odrzuca():
    """T1: walec ø10 z płaskim spodem nie wejdzie w gniazdo ø9 (dno ø6,86)."""
    g = next(g for g in U.wczytaj("wieczorna").gniazda_okragle() if g.d_top == 9)
    walec = trimesh.creation.cylinder(radius=5.0, height=6.0)
    assert synth.osadz_w_gniezdzie(walec, g, np.random.default_rng(0)) is None


def test_generuj_plytke_i_prawda(projekty, tmp_path):
    uk = U.wczytaj("wieczorna")
    rng = np.random.default_rng(5)
    op = synth.Opcje(ubytki_na_prace=(1, 1), prace_na_plytce=3, p_drgniecia=1.0)
    skan, prawda = synth.generuj_plytke(uk, 1, projekty, rng, op, seed=5)
    assert len(prawda.prace) == 3
    assert all(len(p.ubytki) == 1 and p.drgniecie for p in prawda.prace)
    assert len(prawda.gniazda_puste) == 20 - 3  # R54: 18 + 2
    # transformacja z prawdy nakłada projekt na fragment skanu: wierzchołki projektu leżą w gnieździe
    p0 = prawda.prace[0]
    m = trimesh.load(next(q for q in projekty if synth.skrot_pliku(q) == p0.projekt))
    S = trimesh.transformations.scale_matrix(p0.wspolczynnik)
    V = trimesh.transform_points(m.vertices, np.array(p0.transformacja) @ S)
    g = uk.gniazdo(p0.gniazdo)
    assert g.zawiera(V[:, 0].mean(), V[:, 1].mean(), margines=1.0)
    assert V[:, 2].min() >= g.z_dno - 1e-6
    p_stl, p_json = synth.zapisz(skan, prawda, tmp_path, "t")
    assert p_stl.exists() and p_json.exists()
    pr2 = synth.wczytaj_prawde(p_json)
    assert pr2.prace[0].gniazdo == p0.gniazdo and pr2.prace[0].ubytki[0].srednica == p0.ubytki[0].srednica


def test_okragla_poranna_ma_skale_1():
    """Płytka okrągła poranna to też płytka poranna: skala 1,0 (błąd z 2.11: dostawała skurcz wieczorny)."""
    assert synth.poranna("okragla_poranna") and synth.poranna("poranna") and not synth.poranna("okragla_wieczorna")
    assert synth.Opcje.z_toml(plytka="okragla_poranna").wspolczynnik == (1.0, 1.0)
    assert synth.Opcje.z_toml(plytka="okragla_wieczorna").wspolczynnik[0] >= 1.2
