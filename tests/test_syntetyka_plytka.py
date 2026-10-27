"""Testy syntetycznej plytki (qc.syntetyka.plytka): siatka, rozmieszczenie prac, skan z prawda, CLI."""

import dataclasses
import json
import math
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pytest
import trimesh

from qc import uklad as modul_ukladu
from qc.syntetyka import plytka, prace, prawda

KORZEN = Path(__file__).resolve().parent.parent
PLIKI = {
    "wieczorna": KORZEN / "modele" / "uklad_gniazd_wieczorna.json",
    "poranna": KORZEN / "modele" / "uklad_gniazd_poranna.json",
}
KATALOG_WZORCOW = KORZEN / "tests" / "dane" / "wzorce"


# --- fixtures -----------------------------------------------------------------------


@pytest.fixture(scope="module")
def wieczorna():
    return modul_ukladu.wczytaj(PLIKI["wieczorna"])


@pytest.fixture(scope="module")
def poranna():
    return modul_ukladu.wczytaj(PLIKI["poranna"])


def _mosty(krok_mm=0.1):
    return [prace.Projekt(id="most-01", rodzaj="most", siatka=prace.most(1, 4, krok_mm)),
            prace.Projekt(id="most-02", rodzaj="most", siatka=prace.most(2, 3, krok_mm))]


@pytest.fixture(scope="module")
def pula_z_mostami(pula30):
    """Pula 30 koron (krok 0,1) + 2 mosty (pula30 nie zawiera mostow)."""
    return list(pula30) + _mosty(0.1)


@pytest.fixture(scope="module")
def pula_gruba():
    """Szybka pula (krok 0,3) do testow transformacji i stanow."""
    return prace.pula_projektow(30, 1, krok_mm=0.3) + _mosty(0.3)


@pytest.fixture(scope="module")
def siatka_nr2(wieczorna):
    return plytka.siatka_plytki(wieczorna, 2, krok_mm=0.5)


@pytest.fixture(scope="module")
def skan_7(wieczorna, pula_z_mostami):
    rozm = plytka.rozmiesc(wieczorna, pula_z_mostami, 6, 1, ziarno=7)
    siatka, pr = plytka.skan_plytki(wieczorna, 2, rozm, ziarno=7, szum_mm=0.02, T_plytki=None)
    return rozm, siatka, pr


# --- pomocnicze ---------------------------------------------------------------------


def _scena(siatka):
    import open3d as o3d

    scena = o3d.t.geometry.RaycastingScene()
    scena.add_triangles(
        o3d.core.Tensor(np.asarray(siatka.vertices, dtype=np.float32)),
        o3d.core.Tensor(np.asarray(siatka.faces, dtype=np.uint32)),
    )
    return scena


def _promienie(scena, poczatki, kierunek):
    import open3d as o3d

    poczatki = np.atleast_2d(np.asarray(poczatki, dtype=np.float64))
    r = np.zeros((len(poczatki), 6), dtype=np.float32)
    r[:, :3] = poczatki
    r[:, 3:] = kierunek
    return scena.cast_rays(o3d.core.Tensor(r))["t_hit"].numpy().astype(np.float64)


def wysokosci(siatka, xy, z0=20.0):
    """Z pierwszego trafienia promienia z gory w punktach xy; NaN = brak trafienia."""
    xy = np.atleast_2d(np.asarray(xy, dtype=np.float64))
    poczatki = np.column_stack([xy, np.full(len(xy), z0)])
    t = _promienie(_scena(siatka), poczatki, (0, 0, -1))
    return np.where(np.isfinite(t), z0 - t, np.nan)


def wysokosc(siatka, x, y):
    return float(wysokosci(siatka, [(x, y)])[0])


def max_w_oknie(siatka, x, y, pol=1.5, krok=0.1):
    xs = np.arange(x - pol, x + pol + 1e-9, krok)
    ys = np.arange(y - pol, y + pol + 1e-9, krok)
    gx, gy = np.meshgrid(xs, ys, indexing="ij")
    return float(np.nanmax(wysokosci(siatka, np.column_stack([gx.ravel(), gy.ravel()]))))


def odleglosci_bez_znaku(punkty, siatka):
    import open3d as o3d

    wynik = _scena(siatka).compute_distance(o3d.core.Tensor(np.asarray(punkty, dtype=np.float32)))
    return wynik.numpy().astype(np.float64)


def wierzcholki_pracy(siatka, pp):
    a, b = pp.zakres_scian
    f = np.asarray(siatka.faces)[a:b]
    return np.asarray(siatka.vertices)[np.unique(f.ravel())]


def _do_plytki(punkty, T_skan_do_plytki):
    T = np.asarray(T_skan_do_plytki, dtype=np.float64)
    return punkty @ T[:3, :3].T + T[:3, 3]


def _w_gniezdzie(g, x, y):
    dx, dy = x - g.xy[0], y - g.xy[1]
    if g.rodzaj == "stozek":
        return math.hypot(dx, dy) <= g.d_gora / 2
    return abs(dx) <= g.dlugosc / 2 and abs(dy) <= g.szerokosc / 2


def _srodek_bbox(v):
    return (v.min(axis=0) + v.max(axis=0)) / 2


# --- 7. siatka plytki ---------------------------------------------------------------


def test_siatka_plytki(wieczorna, siatka_nr2):
    m = siatka_nr2
    assert isinstance(m, trimesh.Trimesh)
    ext = m.extents
    assert ext[0] == pytest.approx(96, abs=0.6)
    assert ext[1] == pytest.approx(96, abs=0.6)
    assert m.bounds[0, 2] >= -8.05 and m.bounds[1, 2] <= 0.65
    assert m.bounds[0, 2] == pytest.approx(-8, abs=0.05)

    # scianka miedzy rzedami R1 i R2
    assert wysokosc(m, 0.0, -34.5) == pytest.approx(0, abs=0.1)

    # gniazdo 13: dno -4 w 0,6 r_dna od osi, otwor przelotowy w osi
    g = wieczorna.gniazdo(13)
    x, y = g.xy
    r = 0.6 * g.d_dol / 2
    for kx, ky in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        assert wysokosc(m, x + kx * r, y + ky * r) == pytest.approx(-4, abs=0.3)
    z_osi = wysokosc(m, x, y)
    assert math.isnan(z_osi) or z_osi < -7.9

    # znacznik A: wklesly stozek do -3
    assert wysokosc(m, -42, -42) == pytest.approx(-3, abs=0.3)

    # wyciecie D przelotowe
    assert math.isnan(wysokosc(m, 45.5, -45.5))
    assert math.isnan(wysokosc(m, 47.0, -47.0))

    # dolki kodu dla numeru 2 (tylko B)
    assert wysokosc(m, -45, -33) == pytest.approx(-1, abs=0.2)
    assert wysokosc(m, -45, -36) == pytest.approx(0, abs=0.1)
    assert wysokosc(m, -45, -30) == pytest.approx(0, abs=0.1)

    # relief numeru +0,6
    assert max_w_oknie(m, 39.5, -44.5) == pytest.approx(0.6, abs=0.05)

    # rowek pokrywki: 0,8 w glab boku, srodek 2 mm pod wierzchem
    scena = _scena(m)
    t_rowek = _promienie(scena, [(0.0, -60.0, -2.0)], (0, 1, 0))[0]
    t_bok = _promienie(scena, [(0.0, -60.0, -5.0)], (0, 1, 0))[0]
    assert -60 + t_rowek == pytest.approx(-47.2, abs=0.15)
    assert -60 + t_bok == pytest.approx(-48.0, abs=0.15)
    t_lewy = _promienie(scena, [(-60.0, 0.0, -2.0)], (1, 0, 0))[0]
    assert -60 + t_lewy == pytest.approx(-47.2, abs=0.15)


def test_siatka_plytki_warianty(wieczorna):
    m5 = plytka.siatka_plytki(wieczorna, 5, krok_mm=0.5)
    assert wysokosc(m5, -45, -36) == pytest.approx(-1, abs=0.2)
    assert wysokosc(m5, -45, -30) == pytest.approx(-1, abs=0.2)
    assert wysokosc(m5, -45, -33) == pytest.approx(0, abs=0.1)

    baza = plytka.siatka_plytki(wieczorna, None, krok_mm=0.5)
    for y in (-36, -33, -30):
        assert wysokosc(baza, -45, y) == pytest.approx(-1, abs=0.2)
    assert max_w_oknie(baza, 39.5, -44.5) == pytest.approx(0, abs=0.05)

    bez_rowka = plytka.siatka_plytki(wieczorna, None, krok_mm=0.5, rowek=False)
    t = _promienie(_scena(bez_rowka), [(0.0, -60.0, -2.0)], (0, 1, 0))[0]
    assert -60 + t == pytest.approx(-48.0, abs=0.15)


# --- 8. skan plytki z prawda ---------------------------------------------------------


def test_skan_plytki_prawda(wieczorna, skan_7):
    rozm, siatka, pr = skan_7
    assert isinstance(siatka, trimesh.Trimesh)
    assert isinstance(pr, prawda.Prawda)
    assert pr.plytka["uklad"] == "wieczorna"
    assert pr.plytka["numer"] == 2
    assert np.allclose(np.asarray(pr.plytka["T_skan_do_plytki"], dtype=np.float64), np.eye(4), atol=1e-9)
    assert pr.szum_mm == pytest.approx(0.02)

    assert len(pr.prace) == 7
    gniazda = [p.gniazdo for p in pr.prace]
    assert len(set(gniazda)) == 7
    po_gniezdzie = {r.gniazdo: r for r in rozm}  # projekty puli moga sie powtarzac
    assert set(po_gniezdzie) == set(gniazda)
    mosty = [p for p in pr.prace if po_gniezdzie[p.gniazdo].projekt.rodzaj == "most"]
    assert len(mosty) == 1
    assert wieczorna.gniazdo(mosty[0].gniazdo).rodzaj == "rynienka"

    zakresy = sorted(tuple(p.zakres_scian) for p in pr.prace)
    for (a0, b0), (a1, b1) in zip(zakresy[:-1], zakresy[1:]):
        assert b0 <= a1, "zakresy scian nachodza"
    assert all(0 <= a < b <= len(siatka.faces) for a, b in zakresy)
    w_pracach = sum(b - a for a, b in zakresy)
    maska = np.ones(len(siatka.faces), dtype=bool)
    for a, b in zakresy:
        maska[a:b] = False
    plyta = siatka.faces[maska]
    assert len(plyta) == len(siatka.faces) - w_pracach > 0
    # reszta scian = plytka: obrys 96 x 96, nic powyzej reliefu
    v_plyty = np.asarray(siatka.vertices)[np.unique(plyta.ravel())]
    assert np.ptp(v_plyty[:, 0]) == pytest.approx(96, abs=0.6)
    assert v_plyty[:, 2].max() <= 0.7 and v_plyty[:, 2].min() >= -8.1

    for p in pr.prace:
        g = wieczorna.gniazdo(p.gniazdo)
        v = wierzcholki_pracy(siatka, p)
        c = _srodek_bbox(v)
        assert _w_gniezdzie(g, c[0], c[1]), f"praca {p.id} poza gniazdem {g.nr}"
        assert v[:, 2].min() >= -4.3
        assert v[:, 2].max() <= 10.0
        r = po_gniezdzie[p.gniazdo]
        assert p.id == r.projekt.id
        assert p.wspolczynnik == pytest.approx(r.wspolczynnik)
        projekt = np.asarray(r.projekt.siatka.vertices, dtype=np.float64)
        T = np.asarray(p.T_projekt_do_skanu, dtype=np.float64)
        po_T = projekt @ T[:3, :3].T + T[:3, 3]
        d = odleglosci_bez_znaku(po_T, siatka)
        assert np.percentile(d, 95) <= 0.1, f"praca {p.id}"
        # brzeg do gory: os Z projektu po T skierowana w dol
        assert T[2, 2] < 0


# --- 9. transformacja plytki ---------------------------------------------------------


def _sprawdz_znaczniki(uklad, siatka, T_skan_do_plytki):
    v = _do_plytki(np.asarray(siatka.vertices, dtype=np.float64), T_skan_do_plytki)
    for naroznik in ("A", "B", "C"):
        x, y = uklad.znaczniki[naroznik][:2]
        rho = np.hypot(v[:, 0] - x, v[:, 1] - y)
        wybrane = v[(rho < 2.0) & (v[:, 2] > -5.0)]  # bez kieszeni magnesu od spodu
        assert len(wybrane) > 0, naroznik
        najglebszy = wybrane[np.argmin(wybrane[:, 2])]
        assert math.hypot(najglebszy[0] - x, najglebszy[1] - y) <= 0.3, naroznik
        assert najglebszy[2] == pytest.approx(-3, abs=0.3), naroznik


def test_transformacja_losowa(wieczorna, pula_gruba):
    nietrywialne = 0
    for z in range(1, 6):
        rozm = plytka.rozmiesc(wieczorna, pula_gruba, 1, 0, ziarno=z)
        siatka, pr = plytka.skan_plytki(wieczorna, 1, rozm, ziarno=z, szum_mm=0.02, T_plytki="losowa")
        T_sp = np.asarray(pr.plytka["T_skan_do_plytki"], dtype=np.float64)
        assert T_sp.shape == (4, 4)
        assert np.allclose(T_sp[3], [0, 0, 0, 1])
        T = np.linalg.inv(T_sp)  # plytka -> skan
        R, t = T[:3, :3], T[:3, 3]
        assert np.allclose(R @ R.T, np.eye(3), atol=1e-6)
        assert np.linalg.det(R) == pytest.approx(1, abs=1e-6)
        przechyl = math.degrees(math.acos(min(1.0, R[2, 2])))
        obrot_z = math.degrees(math.atan2(R[1, 0], R[0, 0]))
        assert przechyl <= 1.0 + 1e-6
        assert abs(obrot_z) <= 5.0 + 1e-6
        assert math.hypot(t[0], t[1]) <= 3.0 + 1e-6
        assert abs(t[2]) <= 3.0 + 1e-6
        if abs(obrot_z) > 0.05 or math.hypot(t[0], t[1]) > 0.05:
            nietrywialne += 1
        _sprawdz_znaczniki(wieczorna, siatka, T_sp)
        # praca po T_projekt_do_skanu lezy na skanie (uklad skanu)
        p = pr.prace[0]
        Tp = np.asarray(p.T_projekt_do_skanu, dtype=np.float64)
        projekt = np.asarray(rozm[0].projekt.siatka.vertices, dtype=np.float64)
        d = odleglosci_bez_znaku(projekt @ Tp[:3, :3].T + Tp[:3, 3], siatka)
        assert np.percentile(d, 95) <= 0.1
        c = _srodek_bbox(_do_plytki(wierzcholki_pracy(siatka, p), T_sp))
        assert _w_gniezdzie(wieczorna.gniazdo(p.gniazdo), c[0], c[1])
    assert nietrywialne >= 4


def test_transformacja_jawna(wieczorna, pula_gruba):
    a = math.radians(3.0)
    T = np.eye(4)
    T[:3, :3] = [[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]]
    T[:3, 3] = [1.0, -2.0, 0.5]
    rozm = plytka.rozmiesc(wieczorna, pula_gruba, 1, 0, ziarno=3)
    siatka, pr = plytka.skan_plytki(wieczorna, 3, rozm, ziarno=3, szum_mm=0.02, T_plytki=T)
    T_sp = np.asarray(pr.plytka["T_skan_do_plytki"], dtype=np.float64)
    assert np.allclose(T @ T_sp, np.eye(4), atol=1e-9)
    _sprawdz_znaczniki(wieczorna, siatka, T_sp)


# --- 10. stany podwojne i poza gniazdem ----------------------------------------------


def test_podwojne_i_poza(wieczorna, pula_gruba):
    rozm = plytka.rozmiesc(wieczorna, pula_gruba, 3, 0, ziarno=11)
    rozm[1] = dataclasses.replace(rozm[1], opcje={**rozm[1].opcje, "stan": "podwojne"})
    rozm[2] = dataclasses.replace(rozm[2], opcje={**rozm[2].opcje, "stan": "poza_gniazdem"})
    siatka, pr = plytka.skan_plytki(wieczorna, 2, rozm, ziarno=11, szum_mm=0.02)
    stany = [p.stan for p in pr.prace]
    assert "podwojne" in stany and "poza_gniazdem" in stany

    podwojna = next(p for p in pr.prace if p.stan == "podwojne")
    assert podwojna.gniazdo is not None
    w_tym_gniezdzie = [p for p in pr.prace if p.gniazdo == podwojna.gniazdo]
    assert len(w_tym_gniezdzie) == 2
    g = wieczorna.gniazdo(podwojna.gniazdo)
    for p in w_tym_gniezdzie:
        c = _srodek_bbox(wierzcholki_pracy(siatka, p))
        assert _w_gniezdzie(g, c[0], c[1])

    poza = next(p for p in pr.prace if p.stan == "poza_gniazdem")
    v = wierzcholki_pracy(siatka, poza)
    c = _srodek_bbox(v)
    assert wieczorna.gniazdo_dla_xy(c[0], c[1]) is None
    assert v[:, 2].min() >= -0.5
    assert np.all(np.abs(c[:2]) <= 48)


# --- 11. rozmieszczenie ---------------------------------------------------------------


def _sprawdz_rozmieszczenie(uklad, rozm):
    for r in rozm:
        g = uklad.gniazdo(r.gniazdo)
        ext = np.asarray(r.projekt.siatka.extents, dtype=np.float64)
        if r.projekt.rodzaj == "most":
            assert g.rodzaj == "rynienka"
            assert ext[0] * r.wspolczynnik + 2 <= g.dlugosc + 1e-6
        else:
            assert g.rodzaj == "stozek"
            assert max(ext[:2]) * r.wspolczynnik + 1 <= g.d_gora + 0.05, f"{r.projekt.id} w {g.nr}"


def test_rozmiesc_pasuje(wieczorna, pula_z_mostami):
    rozm = plytka.rozmiesc(wieczorna, pula_z_mostami, 24, 2, ziarno=5)
    assert len(rozm) == 26
    assert len({r.gniazdo for r in rozm}) == 26
    assert sum(r.projekt.rodzaj == "most" for r in rozm) == 2
    for r in rozm:
        assert 1.20 <= r.wspolczynnik <= 1.25
        assert isinstance(r.opcje, dict)
        assert len(r.przesuniecie_xy) == 2
        assert -360.0 <= r.obrot_z_deg <= 360.0
    _sprawdz_rozmieszczenie(wieczorna, rozm)

    assert [(r.projekt.id, r.gniazdo) for r in plytka.rozmiesc(wieczorna, pula_z_mostami, 24, 2, ziarno=5)] \
        == [(r.projekt.id, r.gniazdo) for r in rozm]

    with pytest.raises(ValueError, match="gniazd"):
        plytka.rozmiesc(wieczorna, pula_z_mostami, 25, 0, ziarno=5)
    with pytest.raises(ValueError, match="gniazd"):
        plytka.rozmiesc(wieczorna, pula_z_mostami, 1, 3, ziarno=5)


# --- 12. CLI --------------------------------------------------------------------------


def _cli(*argumenty):
    return subprocess.run([sys.executable, "-m", "qc.syntetyka", *argumenty], cwd=KORZEN,
                          capture_output=True, text=True, timeout=300)


def test_cli_plytka(tmp_path):
    wyjscie = tmp_path / "plytka"
    w = _cli("plytka", "--uklad", "wieczorna", "--numer", "2", "--korony", "2", "--mosty", "1",
             "--ziarno", "7", "--szum", "0.02", "--wyjscie", str(wyjscie))
    assert w.returncode == 0, w.stderr
    assert (wyjscie / "skan.stl").is_file()
    pr = prawda.Prawda.z_json(wyjscie / "prawda.json")
    assert pr.plytka["uklad"] == "wieczorna"
    assert pr.plytka["numer"] == 2
    assert pr.ziarno == 7
    assert len(pr.prace) == 3
    skan = trimesh.load(wyjscie / "skan.stl", process=False, force="mesh")
    assert len(skan.faces) >= max(p.zakres_scian[1] for p in pr.prace)

    cel = Path("tests") / "dane" / "plytka-cli-test"
    w = _cli("plytka", "--uklad", "wieczorna", "--numer", "2", "--korony", "1", "--mosty", "0",
             "--ziarno", "7", "--wyjscie", str(cel))
    assert w.returncode == 2
    assert not (KORZEN / cel).exists()
    w = _cli("plytka", "--uklad", "wieczorna", "--numer", "2", "--korony", "1", "--mosty", "0",
             "--ziarno", "7", "--wyjscie", str(KORZEN / "tests" / "dane"))
    assert w.returncode == 2
    assert not (KORZEN / "tests" / "dane" / "skan.stl").exists()


def test_cli_wzorce(tmp_path):
    w = _cli("wzorce", "--katalog", str(tmp_path))
    assert w.returncode == 0, w.stderr
    for nazwa in ("korona-wzorzec", "most-wzorzec"):
        nowy = json.loads((tmp_path / f"{nazwa}.json").read_text(encoding="utf-8"))
        stary = json.loads((KATALOG_WZORCOW / f"{nazwa}.json").read_text(encoding="utf-8"))
        assert nowy == stary
        a = trimesh.load(tmp_path / f"{nazwa}.stl", process=False, force="mesh")
        b = trimesh.load(KATALOG_WZORCOW / f"{nazwa}.stl", process=False, force="mesh")
        assert len(a.faces) == len(b.faces)
        assert np.allclose(a.triangles, b.triangles, atol=1e-5)


# --- 13. pelna plytka (wolne) ----------------------------------------------------------


@pytest.mark.wolne
@pytest.mark.parametrize("nazwa,n_koron", [("wieczorna", 24), ("poranna", 35)])
def test_pelna_plytka(nazwa, n_koron, pula_z_mostami):
    u = modul_ukladu.wczytaj(PLIKI[nazwa])
    t0 = time.perf_counter()
    rozm = plytka.rozmiesc(u, pula_z_mostami, n_koron, 2, ziarno=1)
    siatka, pr = plytka.skan_plytki(u, u.numery[0], rozm, ziarno=1, szum_mm=0.02, T_plytki="losowa")
    czas = time.perf_counter() - t0
    assert czas <= 90.0, f"{nazwa}: {czas:.1f} s"
    assert len(siatka.vertices) <= 4_000_000
    assert len(pr.prace) == n_koron + 2
    assert len({p.gniazdo for p in pr.prace}) == n_koron + 2
    _sprawdz_rozmieszczenie(u, rozm)
