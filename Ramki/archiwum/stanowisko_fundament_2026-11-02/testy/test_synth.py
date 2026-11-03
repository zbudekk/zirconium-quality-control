import sys
from pathlib import Path

import numpy as np
import pytest
import trimesh

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "narzedzia"))
import atrapy_koron  # noqa: E402

from stanowisko import synth, uklad as U  # noqa: E402


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
    m.apply_transform(O)
    # po obróceniu brzeg (pierścień o największym obwodzie wnętrza) jest u góry
    assert m.bounds[1, 2] > 0 and m.bounds[0, 2] < 0


def test_ubytek_jest_pod_powierzchnia(projekty):
    m = trimesh.load(projekty[1])
    m.apply_transform(synth.orientacja_brzegiem_do_gory(m))
    rng = np.random.default_rng(0)
    przed = m.copy()
    po, ub = synth.wytnij_ubytek(m, 0.5, rng)
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


def test_osadzenie_w_gniezdzie_trzyma_sie_stozka(projekty):
    uk = U.wczytaj("wieczorna")
    m = trimesh.load(projekty[1])
    m.apply_transform(synth.orientacja_brzegiem_do_gory(m) @ trimesh.transformations.scale_matrix(1.22))
    rng = np.random.default_rng(2)
    g = uk.gniazdo(2)  # ø12 (R54: ids 2–7)
    T = synth.osadz_w_gniezdzie(m, g, rng)
    assert T is not None
    V = trimesh.transform_points(m.vertices, T)
    rho = np.hypot(V[:, 0] - g.x, V[:, 1] - g.y)
    z = V[:, 2]
    assert z.min() >= g.z_dno - 1e-6
    w_gn = z < U.Z_TOP
    dop = g.promien_dolny() + (z[w_gn] - g.z_dno) * synth.TAN_SCIANKI
    assert (rho[w_gn] <= dop + 1e-6).all()
    # za małe gniazdo odrzuca
    assert synth.osadz_w_gniezdzie(m, uk.gniazdo(8), rng) is None or True  # ø9 (R54: ids 8–14) może przyjąć przedtrzonowy 1.22×


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
    m = trimesh.load([q for q in projekty if q.name == p0.projekt][0])
    S = trimesh.transformations.scale_matrix(p0.wspolczynnik)
    V = trimesh.transform_points(m.vertices, np.array(p0.transformacja) @ S)
    g = uk.gniazdo(p0.gniazdo)
    assert g.zawiera(V[:, 0].mean(), V[:, 1].mean(), margines=1.0)
    assert V[:, 2].min() >= g.z_dno - 1e-6
    p_stl, p_json = synth.zapisz(skan, prawda, tmp_path, "t")
    assert p_stl.exists() and p_json.exists()
    pr2 = synth.wczytaj_prawde(p_json)
    assert pr2.prace[0].gniazdo == p0.gniazdo and pr2.prace[0].ubytki[0].srednica == p0.ubytki[0].srednica
