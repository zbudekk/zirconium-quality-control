"""match (P2): pula, filtr, zgrubne dopasowanie, ICP, ocena, ranking — na atrapach (3 typy) i skanie syntetycznym."""
from __future__ import annotations

import math
import shutil
import warnings

import numpy as np
import pytest
import trimesh

from stanowisko import match, plate, synth, ustawienia as UST, uklad as U


@pytest.fixture(scope="module")
def ust():
    return UST.wczytaj_ustawienia()


@pytest.fixture(scope="module")
def pula(korony, tmp_path_factory):
    """Trzy atrapy (siekacz, przedtrzonowy, trzonowy) × 1,22 w dwóch folderach (pula z wielu folderów)."""
    d1 = tmp_path_factory.mktemp("pula_a")
    d2 = tmp_path_factory.mktemp("pula_b")
    shutil.copy(korony[0], d1 / "2026-11-02_x-11-crown_cad.stl")
    shutil.copy(korony[1], d1 / "2026-11-02_y-14-crown_cad.stl")
    shutil.copy(korony[2], d2 / "2026-11-02_z-36-crown_cad.stl")
    (d2 / "_pobrane").mkdir()
    (d2 / "_pobrane" / "smiec.stl").write_bytes(b"")
    p = match.Pula([d1, d2], 1.22)
    assert len(p) == 3 and p.pominiete == 0
    return p


@pytest.fixture(scope="module")
def fragmenty(korony):
    """Fragmenty z plate na sztucznym skanie (okrągła wieczorna, 3 atrapy × 1,22, bez drgnięcia) + prawda."""
    uk = U.wczytaj("okragla_wieczorna")
    rng = np.random.default_rng(22)  # seed 21 (i 27, 29): atrapa siekacza dopasowana odwrotnie (180°, pokrycie 0,52 → szary) — słabość match do P3a-2, patrz raporty/P3a_przekazanie.md
    op = synth.Opcje.z_toml(plytka=uk.nazwa, prace_na_plytce=3, p_drgniecia=0.0, wspolczynnik=(1.22, 1.22), poza_uklad=True)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        skan, prawda = synth.generuj_plytke(uk, 8, list(korony), rng, op, 22)
    w = plate.wyrownaj(skan, uk)
    assert len(w.fragmenty) == 3 and all(f.status == "praca" for f in w.fragmenty)
    return w, prawda


def test_pula_i_cechy(pula):
    for pr in pula.projekty.values():
        assert len(pr.id) == 16 and pr.cechy.typ == "korona" and pr.wspolczynnik == 1.22
        assert abs(pr.siatka.bounds[1, 2]) < 1e-9  # brzeg (góra) na z = 0
        assert abs(pr.siatka.bounds[:, 0].mean()) < 1e-9 and abs(pr.siatka.bounds[:, 1].mean()) < 1e-9
        assert pr.hull > 0 and pr.obrys_xy[0] <= pr.obrys_xy[1] and pr.wysokosc > 5
        assert pr.odleglosci(np.asarray(pr.chmura.points)[:100]).max() < 1e-3


def test_dopasowanie_top1_i_transformacja(pula, fragmenty, ust):
    w, prawda = fragmenty
    mapa = {p.gniazdo: p for p in prawda.prace}
    for f in w.fragmenty:
        r = match.dopasuj(f.punkty, f.normalne, pula, ust, f.gniazdo)
        assert r.gniazdo == f.gniazdo and r.liczba_punktow == f.liczba and r.czas_s < 30
        assert [k.id for k in r.kandydaci][0] == mapa[f.gniazdo].projekt, (f.gniazdo, [(k.id, k.pokrycie) for k in r.kandydaci])
        k = r.najlepszy
        assert k.pokrycie >= 0.85 and k.rms_mm < 0.04 and k.metoda in ("ransac", "obroty")
        assert r.status == "zielony" and r.pewnosc >= ust["match"]["pewnosc_min"]
        pr = pula.projekty[k.id]
        b = match.blad_pozy(k.transformacja, mapa[f.gniazdo].transformacja, pr.siatka)
        assert b["przesuniecie_mm"] < 0.05 and b["obrot_deg"] < 0.5, b
        assert all(kk.pokrycie <= k.pokrycie for kk in r.kandydaci[1:])


def test_filtr_wymiarow(pula, fragmenty, ust):
    w, prawda = fragmenty
    mapa = {p.gniazdo: p for p in prawda.prace}
    f = next(f for f in w.fragmenty if pula.projekty[mapa[f.gniazdo].projekt].cechy.zeby == ["11"])  # siekacz
    fr = match.FragmentDoDopasowania.z_punktow(f.punkty, f.normalne)
    wyniki = {pr.cechy.zeby[0]: match.filtr(fr, pr, ust) for pr in pula.projekty.values()}
    assert wyniki["11"][0] and not wyniki["36"][0] and "mm" in wyniki["36"][1]  # trzonowy 10,5 × 11 vs siekacz 6,5 × 5
    ust2 = {**ust, "match": {**ust["match"], "filtr_wymiar_mm": 100.0, "filtr_objetosc_udzial": 100.0}}
    assert all(match.filtr(fr, pr, ust2)[0] for pr in pula.projekty.values())
    r = match.dopasuj(f.punkty, f.normalne, pula, ust2, f.gniazdo)  # bez filtru: wszystkie dopasowane, siekacz nadal pierwszy
    assert all(k.filtr_ok for k in r.kandydaci) and r.kandydaci[0].zeby == ["11"] and r.kandydaci[1].pokrycie < 0.6


def test_zgrubne_obroty_i_ocena(pula, fragmenty, ust):
    w, prawda = fragmenty
    mapa = {p.gniazdo: p for p in prawda.prace}
    f = w.fragmenty[0]
    pr = pula.projekty[mapa[f.gniazdo].projekt]
    fr = match.FragmentDoDopasowania.z_punktow(f.punkty, f.normalne)
    T, pok = match.zgrubne_obroty(fr, pr, ust["match"]["odleglosc_max_mm"])
    assert pok > 0.8
    T2 = match._icp(fr.chmura, pr.chmura, T)
    pok2, rms, odwr = match.ocena(fr, pr, T2, ust["match"]["odleglosc_max_mm"])
    assert pok2 >= 0.85 and rms < 0.04 and odwr > 0.3  # pokrycie odwrotne (próg 2·odl_max) jest tylko informacyjne
    T3 = match.zgrubne_ransac(fr, pr)
    assert T3 is not None
    assert match.ocena(fr, pr, match._icp(fr.chmura, pr.chmura, T3), 0.05)[0] >= 0.85


def test_dopasuj_brzegi(pula, ust):
    r = match.dopasuj(np.zeros((10, 3)), np.zeros((10, 3)), pula, ust)
    assert r.status == "szary" and r.kandydaci == [] and "za mało" in r.uwagi[0]
    pusta = match.Pula.__new__(match.Pula)
    pusta.projekty, pusta.pominiete, pusta.wspolczynnik = {}, 0, 1.0
    r = match.dopasuj(np.random.default_rng(0).normal(size=(100, 3)), np.zeros((100, 3)), pusta, ust)
    assert r.status == "szary" and "pusta pula" in r.uwagi[0]


def test_statusy_z_progow(pula, fragmenty, ust):
    """Progi z ustawień decydują o statusie: zaostrzony próg akceptacji → żółty, a potem szary."""
    w, _ = fragmenty
    f = w.fragmenty[0]
    r = match.dopasuj(f.punkty, f.normalne, pula, ust, f.gniazdo)
    pok = r.najlepszy.pokrycie
    ust_z = {**ust, "match": {**ust["match"], "prog_akceptacji_pokrycie": min(1.0, pok + 0.01), "prog_ostrzezenia_pokrycie": pok - 0.05}}
    assert match.dopasuj(f.punkty, f.normalne, pula, ust_z, f.gniazdo).status == "zolty"
    ust_s = {**ust, "match": {**ust["match"], "prog_akceptacji_pokrycie": min(1.0, pok + 0.02), "prog_ostrzezenia_pokrycie": min(1.0, pok + 0.01)}}
    assert match.dopasuj(f.punkty, f.normalne, pula, ust_s, f.gniazdo).status == "szary"
    ust_p = {**ust, "match": {**ust["match"], "pewnosc_min": 1.0}}
    assert match.dopasuj(f.punkty, f.normalne, pula, ust_p, f.gniazdo).status == "szary"


def test_blad_pozy_tozsamosc():
    m = trimesh.creation.box([5, 6, 7])
    T = trimesh.transformations.rotation_matrix(math.radians(2.0), [0, 0, 1]) @ trimesh.transformations.translation_matrix([1, 0, 0])
    b = match.blad_pozy(T, T, m)
    assert b["przesuniecie_mm"] == 0 and b["obrot_deg"] == 0
    b = match.blad_pozy(T, np.eye(4), m)
    assert abs(b["obrot_deg"] - 2.0) < 1e-6 and b["przesuniecie_mm"] > 0.9
