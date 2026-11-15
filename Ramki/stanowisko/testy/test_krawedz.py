"""krawedz: linie krawedzi brzegu kazdego filaru - na atrapach i brylach zbudowanych w tescie (bez plikow spoza repo).

Liczby dla 17 prawdziwych projektow (23 petle) sa w raporcie paczki; tu sprawdzane sa wlasnosci metody:
liczba petli, polozenie naroznikow O / I, oznaczanie odcinkow niezweryfikowanych, jawny brak linii,
niezaleznosc od skali i przesuniecia, pamiec podreczna.
"""
from __future__ import annotations

import math

import numpy as np
import pytest
import trimesh
from scipy.spatial import cKDTree

import atrapy_koron  # sciezka: testy/conftest.py
from stanowisko import krawedz as KR, synth

SKALA = 1.22


def _atrapa(typ: str, seed: int = 11, skala: float = SKALA) -> trimesh.Trimesh:
    W, L, H, g, amp = atrapy_koron.TYPY[typ]
    m = atrapy_koron.korona(W, L, H, g, amp, n_theta=96, n_u=120, rng=np.random.default_rng(seed))
    m.apply_transform(synth.orientacja_brzegiem_do_gory(m) @ trimesh.transformations.scale_matrix(skala))
    return m


def tuleja(ro, ri, h: float = 6.0, n: int = 180, srodek=(0.0, 0.0)) -> trimesh.Trimesh:
    """Tuleja z kanalem na wylot (jak korona implantowa bez lacznika): plaski pierscien na z = 0, promienie zewnetrzny
    i wewnetrzny jako funkcje kata (albo liczby)."""
    th = np.linspace(0, 2 * math.pi, n, endpoint=False) + 0.0071  # faza: przekroje nie trafiaja dokladnie w wierzcholki
    Ro = np.broadcast_to(ro(th) if callable(ro) else ro, th.shape)
    Ri = np.broadcast_to(ri(th) if callable(ri) else ri, th.shape)
    V = np.vstack([np.c_[R * np.cos(th) + srodek[0], R * np.sin(th) + srodek[1], np.full(n, z)] for R, z in ((Ro, 0.0), (Ri, 0.0), (Ro, -h), (Ri, -h))])
    i = np.arange(n)
    j = np.roll(i, -1)
    F = []
    for a, b in ((1, 0), (0, 2), (2, 3), (3, 1)):  # wierzch, sciana zewnetrzna, spod, sciana kanalu
        F += [np.c_[a * n + i, b * n + i, b * n + j], np.c_[a * n + i, b * n + j, a * n + j]]
    m = trimesh.Trimesh(V, np.vstack(F), process=True)
    m.fix_normals()
    assert m.is_watertight and m.volume > 0
    return m


@pytest.fixture(scope="module")
def linie_korony():
    m = _atrapa("przedtrzonowy")
    return m, KR.linie_siatki(m, skala=SKALA)


# --- korona, most, korona implantowa ------------------------------------------------------
def test_korona_ma_jedna_petle_na_brzegu(linie_korony):
    m, linie = linie_korony
    assert linie.stan == "wiarygodne" and len(linie.filary) == 1 and linie.skala == pytest.approx(SKALA)
    f = linie.filary[0]
    assert f.werdykt == "wiarygodna" and f.udzial_zweryf >= 0.95 and f.najdl_przerwa_mm <= 0.5
    O, I, S = f.linie["O"], f.linie["I"], f.linie["S"]
    # naroznik zewnetrzny = zewnetrzny obwod brzegu (najwyzsze wierzcholki atrapy, z = 0); wewnetrzny nizej i blizej osi
    obwod = m.vertices[m.vertices[:, 2] > -1e-6]
    assert cKDTree(obwod).query(O.X)[0].max() < 0.2
    assert abs(O.X[:, 2]).max() < 0.02 and -0.4 < I.X[:, 2].mean() < -0.05
    rO, rI = np.hypot(*(O.X[:, :2] - f.srodek).T), np.hypot(*(I.X[:, :2] - f.srodek).T)
    assert rI.mean() < rO.mean() - 0.5
    szer = np.linalg.norm(f.O - f.I, axis=1)  # plaska krawedz atrapy: scianka 0,6 mm x 1,22
    assert 0.6 < np.median(szer) < 0.9
    # dlugosc petli = obwod brzegu; stacje co ok. 0,05 mm (w skali odniesienia)
    kolo = np.vstack([obwod[np.argsort(np.arctan2(obwod[:, 1], obwod[:, 0]))]])
    dl = np.linalg.norm(np.diff(np.vstack([kolo, kolo[:1]]), axis=0), axis=1).sum()
    assert O.dlugosc == pytest.approx(dl, rel=0.02) and O.krok == pytest.approx(KR.KROK_STACJI, rel=0.1)
    # srodek plaskiej krawedzi lezy NA powierzchni projektu, miedzy naroznikami
    _, odl, _ = trimesh.proximity.closest_point(m, f.S[::20])
    assert odl.max() < 1e-4
    assert np.linalg.norm(f.S - (f.O + f.I) / 2, axis=1).max() < 0.1 and len(S.X) > 100


def test_most_ma_petle_na_kazdy_filar():
    most = atrapy_koron.most(np.random.default_rng(1))  # 4 korony w rzedzie + laczniki
    most.apply_transform(synth.orientacja_brzegiem_do_gory(most, "brzeg_dol"))
    linie = KR.linie_siatki(most, skala=1.0)
    assert len(linie.filary) == 4 and [f.nr for f in linie.filary] == [1, 2, 3, 4]
    xs = sorted(f.srodek[0] for f in linie.filary)
    assert all(b - a > 4.0 for a, b in zip(xs, xs[1:]))  # kazda petla wokol innej wneki
    for f in linie.filary:
        O = f.linie["O"].X
        assert f.werdykt in KR.WERDYKTY and f.dlugosc > 10.0
        assert np.hypot(*(O[:, :2] - f.srodek).T).max() < 8.0  # petla nie ucieka na sasiedni czlon


def test_korona_implantowa_obwod_powierzchni_przylegania():
    """Kanal sruby na wylot tez jest "wneka": petla = obwod powierzchni przylegania (O zewnetrzny, I przy kanale)."""
    m = tuleja(2.2, 1.4)
    linie = KR.linie_siatki(m, skala=SKALA)
    assert len(linie.filary) == 1
    f = linie.filary[0]
    assert f.werdykt == "wiarygodna" and f.udzial_zweryf > 0.95
    assert np.hypot(f.O[:, 0], f.O[:, 1]) == pytest.approx(2.2, abs=0.02) and np.hypot(f.I[:, 0], f.I[:, 1]) == pytest.approx(1.4, abs=0.02)
    assert np.abs(f.O[:, 2]).max() < 1e-6 and f.dlugosc == pytest.approx(2 * math.pi * 2.2, rel=0.01)
    assert "T3" in f.kontrola["zrodla_drugiej_opinii"]


def test_odcinek_niepewny_jest_oznaczony_a_nie_zgadywany():
    """Plaska krawedz szersza niz kryterium (1,5 mm w skali odniesienia) na czesci obwodu: te przekroje nie sa
    zweryfikowane, petla nie jest wiarygodna, a linia zostaje (oznaczona)."""
    m = tuleja(3.2, lambda th: np.where(np.cos(th) > 0.3, 0.9, 2.5))  # szerokosc 0,7 albo 2,3 mm
    linie = KR.linie_siatki(m, skala=SKALA)
    assert len(linie.filary) == 1 and linie.stan == "czesciowe"
    f = linie.filary[0]
    szer = np.linalg.norm(f.O - f.I, axis=1)  # szerokosc plaskiej krawedzi w przekroju (os przekrojow = srodek kanalu)
    szeroko = szer > KR.SZER_MAX + 0.05
    wasko = szer < 1.0
    assert szeroko.mean() > 0.2 and wasko.mean() > 0.3
    assert f.werdykt in ("czesciowa", "niepewna") and not f.zweryf[szeroko].any() and f.zweryf[wasko].mean() > 0.95
    assert 0.3 < f.udzial_zweryf < 0.8 and f.najdl_ciag_st > 60 and f.najdl_przerwa_mm > 3.0
    O = f.linie["O"]
    assert len(O.X) == len(O.zweryf) and 0.3 < O.zweryf.mean() < 0.8 and np.isfinite(O.X).all()
    assert linie.opis()["filary"][0]["przekroje_zweryfikowane"] == int(f.zweryf.sum())


@pytest.mark.parametrize("bryla", [trimesh.creation.box([8.0, 6.0, 5.0]), trimesh.creation.icosphere(subdivisions=3, radius=4.0)])
def test_bryla_bez_wneki_nie_ma_linii(bryla):
    linie = KR.linie_siatki(bryla)
    assert linie.filary == [] and linie.stan == "brak" and linie.uwagi and "brak niecki" in linie.uwagi[0]
    assert KR.stacje(linie)["X"].shape == (0, 3)


# --- skala, przesuniecie, pamiec -------------------------------------------------------------
def test_skala_i_przesuniecie_nie_zmieniaja_linii(linie_korony):
    m, linie = linie_korony
    m2 = m.copy()
    m2.apply_transform(trimesh.transformations.translation_matrix([30.0, -12.0, 4.0]) @ trimesh.transformations.scale_matrix(1.0 / SKALA))
    linie2 = KR.linie_siatki(m2, skala=1.0)  # ten sam projekt w skali pliku, przesuniety
    f, f2 = linie.filary[0], linie2.filary[0]
    assert linie2.skala == pytest.approx(1.0) and f2.werdykt == f.werdykt and abs(f2.udzial_zweryf - f.udzial_zweryf) < 0.02
    X2 = (f2.linie["O"].X - [30.0, -12.0, 4.0]) * SKALA
    d = cKDTree(f.linie["O"].X).query(X2)[0]
    assert np.percentile(d, 99) < 0.03
    assert f2.dlugosc * SKALA == pytest.approx(f.dlugosc, rel=0.005) and f2.najdl_przerwa_mm <= f.najdl_przerwa_mm + 0.1


def test_zla_skala_odrzucona(linie_korony):
    for s in (0.0, -1.0, float("nan")):
        with pytest.raises(ValueError, match="skala"):
            KR.linie_siatki(linie_korony[0], skala=s)


def test_pamiec_w_module_i_na_dysku(tmp_path, monkeypatch):
    m = tuleja(2.2, 1.4)
    KR.wyczysc_pamiec()
    licznik = {"n": 0}
    prawdziwe = KR.wyznacz

    def liczone(siatka):
        licznik["n"] += 1
        return prawdziwe(siatka)

    monkeypatch.setattr(KR, "wyznacz", liczone)
    try:
        a = KR.linie_siatki(m, skala=SKALA, klucz="proj-1")
        b = KR.linie_siatki(m, skala=SKALA, klucz="proj-1")
        assert licznik["n"] == 1 and np.array_equal(a.filary[0].linie["O"].X, b.filary[0].linie["O"].X)
        KR.linie_siatki(m, skala=SKALA)  # bez klucza: bez pamieci
        assert licznik["n"] == 2
        # ten sam projekt w innej skali: linie z pamieci, przeliczone
        m1 = m.copy()
        m1.apply_scale(1.0 / SKALA)
        c = KR.linie_siatki(m1, skala=1.0, klucz="proj-1")
        assert licznik["n"] == 2 and c.filary[0].dlugosc * SKALA == pytest.approx(a.filary[0].dlugosc)
        assert not list(tmp_path.iterdir())  # domyslnie nic nie trafia na dysk
        KR.ustaw_katalog_pamieci(tmp_path / "linie")
        KR.wyczysc_pamiec()
        d = KR.linie_siatki(m, skala=SKALA, klucz="proj-1")
        pliki = list((tmp_path / "linie").iterdir())
        assert licznik["n"] == 3 and [p.name for p in pliki] == [f"proj-1_v{KR.WERSJA}.npz"]
        KR.wyczysc_pamiec()
        e = KR.linie_siatki(m, skala=SKALA, klucz="proj-1")  # z dysku, bez liczenia
        assert licznik["n"] == 3
        fd, fe = d.filary[0], e.filary[0]
        for nazwa in KR.NAZWY_LINII:
            assert np.array_equal(fd.linie[nazwa].X, fe.linie[nazwa].X) and np.array_equal(fd.linie[nazwa].zweryf, fe.linie[nazwa].zweryf)
        assert np.array_equal(fd.zweryf, fe.zweryf) and fd.werdykt == fe.werdykt and fd.kontrola == fe.kontrola
        pliki[0].write_bytes(b"zepsuty")  # uszkodzony plik = liczenie od nowa, nie blad
        KR.wyczysc_pamiec()
        KR.linie_siatki(m, skala=SKALA, klucz="proj-1")
        assert licznik["n"] == 4
    finally:
        KR.ustaw_katalog_pamieci(None)
        KR.wyczysc_pamiec()


def test_stacje_wszystkich_filarow(linie_korony):
    _, linie = linie_korony
    st = KR.stacje(linie)
    f = linie.filary[0]
    assert len(st["X"]) == len(f.linie["O"].X) + len(f.linie["I"].X) == len(st["zweryf"]) == len(st["nr"])
    assert set(st["filar"]) == {0} and set(st["linia"]) == {0, 1}
    assert len(KR.stacje(linie, ("O",))["X"]) == len(f.linie["O"].X)


def test_przeksztalcenie_ukladu(linie_korony):
    _, linie = linie_korony
    p = linie.przeksztalc(2.0, (1.0, 2.0, 3.0))
    f, g = linie.filary[0], p.filary[0]
    assert np.allclose(g.linie["O"].X, f.linie["O"].X * 2 + [1, 2, 3]) and g.dlugosc == pytest.approx(2 * f.dlugosc)
    assert g.najdl_przerwa_mm == pytest.approx(2 * f.najdl_przerwa_mm) and p.skala == pytest.approx(2 * linie.skala)
    assert np.allclose(g.S, f.S * 2 + [1, 2, 3]) and g.srodek == pytest.approx((f.srodek[0] * 2 + 1, f.srodek[1] * 2 + 2))


# --- jednostkowe ---------------------------------------------------------------------------
def test_najdluzsza_przerwa_kolowa():
    assert KR.najdluzsza_przerwa(np.ones(10, bool)) == 0 and KR.najdluzsza_przerwa(np.zeros(10, bool)) == 10
    ok = np.ones(12, bool)
    ok[[0, 1, 11, 5]] = False  # przerwa przez koniec tablicy liczy sie jako jedna
    assert KR.najdluzsza_przerwa(ok) == 3


def test_fourier_odporny_pomija_odstajace():
    th = np.radians(np.arange(0, 360, 2.0))
    y = 5 + 0.8 * np.cos(th) + 0.3 * np.sin(2 * th)
    z = y.copy()
    z[10:14] += 3.0  # odstajace
    z[40:45] = np.nan
    f = KR.fourier_odporny(th, z, 8)
    assert np.abs(f - y).max() < 0.05
    assert np.isnan(KR.fourier_odporny(th[:10], y[:10], 8)).all()  # za malo punktow


def test_niecki_i_dzial_wodny_na_sztucznej_mapie():
    """Dwie niecki rozdzielone grzbietem na plaskim wierzchu (z = 0), tlo = brak trafienia."""
    g = np.arange(-6, 6, KR.PIKSEL)
    X, Y = np.meshgrid(g, g)
    Z = np.zeros_like(X)
    for cx in (-2.5, 2.5):
        r = np.hypot(X - cx, Y)
        Z = np.where(r < 1.5, -3.0 * (1 - (r / 1.5) ** 2), Z)
    Z[(np.abs(X) > 5) | (np.abs(Y) > 3)] = np.nan
    wyp, Zf = KR.wypelnij_niecki(Z)
    assert wyp[np.isfinite(Z)].min() == pytest.approx(0.0) and (wyp >= Zf).all()
    ws, niecki, k, gl = KR.obszary_filarow(Z)
    assert k == 2 and sum(n["przyjeta"] for n in niecki) == 2 and gl.max() == pytest.approx(3.0, abs=0.01)
    lewa, prawa = ws[Y.shape[0] // 2, np.searchsorted(g, -2.5)], ws[Y.shape[0] // 2, np.searchsorted(g, 2.5)]
    assert {int(lewa), int(prawa)} == {1, 2} and (ws[np.isnan(Z)] == 0).all()
    plytka = np.where(np.isnan(Z), np.nan, 0.0)  # bez niecek: zadnego filaru
    assert KR.obszary_filarow(plytka)[2] == 0
