"""inspect (P3a): mapa odchyłek (A), ciągłość linii brzegu (B), decyzja, drgnięcie, poprawka, brak danych, bokiem — na atrapach."""
from __future__ import annotations

import math
import shutil
import warnings

import numpy as np
import pytest
import trimesh

from stanowisko import inspect as I, match, plate, porownaj as PO, synth, ustawienia as UST, uklad as U


@pytest.fixture(scope="module")
def ust():
    return UST.wczytaj_ustawienia()


@pytest.fixture(scope="module")
def pula(korony, tmp_path_factory):
    d = tmp_path_factory.mktemp("pula_inspect")
    for i, p in enumerate(korony):
        shutil.copy(p, d / f"2026-11-02_p{i}-{['11', '14', '36'][i]}-crown_cad.stl")
    return match.Pula([d], 1.22)


def _lancuch(korony, pula, ust, seed, **opcje):
    """Sztuczny skan (okrągła wieczorna, 3 atrapy × 1,22) → plate → match → inspect; zwraca listę (praca_prawdy, kandydat, wynik_inspekcji)."""
    uk = U.wczytaj("okragla_wieczorna")
    rng = np.random.default_rng(seed)
    op = synth.Opcje.z_toml(plytka=uk.nazwa, prace_na_plytce=3, wspolczynnik=(1.22, 1.22), **opcje)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        skan, prawda = synth.generuj_plytke(uk, 8, list(korony), rng, op, seed)
        w = plate.wyrownaj(skan, uk)
    praw = {p.gniazdo: p for p in prawda.prace}
    out = []
    for f in w.fragmenty:
        if f.status != "praca" or f.gniazdo not in praw:
            continue
        r = match.dopasuj(f.punkty, f.normalne, pula, ust, f.gniazdo)
        k = r.najlepszy
        wi = I.sprawdz(f.punkty, f.normalne, pula.projekty[k.id], np.array(k.transformacja), k.pokrycie, ust, f.gniazdo)
        out.append((praw[f.gniazdo], k, wi))
    assert len(out) == len(prawda.prace) > 0
    return out


@pytest.fixture(scope="module")
def z_ubytkami(korony, pula, ust):
    return _lancuch(korony, pula, ust, seed=5, ubytki_na_prace=(1, 2), p_drgniecia=0.0, srednica_ubytku=(0.6, 1.4))


# --- metoda A i B na ubytkach z prawdy -------------------------------------------------
def test_ubytki_z_prawdy_sa_wykrywane(z_ubytkami, ust):
    wyk = traf_a = traf_b = traf_cz = traf_any = 0
    for p, k, wi in z_ubytkami:
        assert k.id == p.projekt and wi.status in ("ubytek", "sprawdz", "sprawdz_ulozenie"), (wi.status, wi.uwagi)
        ub = [u for u in p.ubytki if u.wykrywalny]
        dp = I.dopasuj_do_prawdy(ub, [u.__dict__ for u in wi.ubytki])
        wyk += len(ub)
        traf_a += sum(dp["trafione"]["A"])
        traf_b += sum(dp["trafione"]["B"])
        traf_cz += sum(dp["trafione"]["czerwony"])
        traf_any += sum(dp["trafione"]["dowolny"])
        assert dp["falszywe_czerwone"] == 0
        for u in wi.ubytki:
            assert u.metoda in ("A", "B", "A+B") and u.kolor in ("czerwony", "zolty")
            assert u.srednica_mm <= ust["inspect"]["srednica_max_mm"] + 0.5 and u.glebokosc_mm >= 0.08
            assert (u.metoda != "A+B") or u.kolor == "czerwony"
    assert wyk >= 3
    assert traf_any >= 0.8 * wyk, (traf_any, wyk)
    assert traf_a >= 0.7 * wyk and traf_b >= 1 and traf_cz >= 1


def test_ubytek_w_ukladzie_plytki_blisko_prawdy(z_ubytkami):
    """Środek wykrytego ubytku leży przy środku ubytku z prawdy (układ płytki), odległość od brzegu w pasie."""
    for p, _, wi in z_ubytkami:
        for u in wi.ubytki:
            if u.metoda.startswith("A"):
                naj = min(math.dist((u.x, u.y, u.z), (t.x, t.y, t.z)) for t in p.ubytki)
                assert naj <= 1.0, naj
                assert u.odleglosc_od_brzegu_mm <= 1.5 + 0.8 or u.na_krawedzi


def test_praca_cala_bez_alarmu(korony, pula, ust):
    for p, k, wi in _lancuch(korony, pula, ust, seed=6, ubytki_na_prace=(0, 0), p_drgniecia=0.0):
        assert wi.status == "ok" and wi.ubytki == [] and not wi.drgniecie["wykryte"], (wi.status, wi.plamy, wi.wciecia)
        assert all(pl.rodzaj != "ubytek" for pl in wi.plamy) and all(v.rodzaj != "wciecie" for v in wi.wciecia)
        assert wi.odchylki["udzial_pod"] < 0.02 and abs(wi.odchylki["mediana_mm"]) < 0.01


# --- drgnięcie, pokrycie, poprawka, brak danych, bokiem ------------------------------
def test_drgniecie_daje_skan_ponownie(korony, pula, ust):
    for p, k, wi in _lancuch(korony, pula, ust, seed=7, ubytki_na_prace=(0, 1), p_drgniecia=1.0):
        assert p.drgniecie and wi.status == "skan_ponownie" and wi.drgniecie["wykryte"] and wi.ubytki == []
        assert "skan ponownie" in wi.uwagi[0]


def test_niskie_pokrycie_to_popraw_ulozenie(z_ubytkami, pula, ust):
    p, k, _ = z_ubytkami[0]
    P, N = _punkty(z_ubytkami, pula, ust, 0)
    wi = I.sprawdz(P, N, pula.projekty[k.id],
                   np.array(k.transformacja), 0.5, ust, p.gniazdo)
    assert wi.status == "popraw_ulozenie" and wi.ubytki == [] and "popraw ułożenie" in wi.uwagi[0]


def _punkty(z_ubytkami, pula, ust, i):
    """Punkty fragmentu odtworzone z podglądu (układ płytki)."""
    wi = z_ubytkami[i][2]
    assert wi._P is not None and wi._d is not None and len(wi._P) == len(wi._d)
    N = np.tile([0.0, 0.0, 1.0], (len(wi._P), 1))
    return wi._P, N


def test_poprawka_reczna_bez_ostrej_krawedzi_to_pomaranczowe(korony, pula, ust):
    n_pop = 0
    for p, k, wi in _lancuch(korony, pula, ust, seed=8, ubytki_na_prace=(0, 0), p_drgniecia=0.0, p_poprawki=1.0):
        assert len(p.poprawki) == 1 and p.poprawki[0].srednica > ust["inspect"]["poprawka_min_mm"]
        assert wi.status != "ubytek" and all(u.kolor != "czerwony" for u in wi.ubytki), (wi.status, wi.ubytki)
        n_pop += wi.status == "poprawka"
        for pl in wi.plamy:
            if pl.rodzaj == "poprawka":
                assert not pl.ostra_krawedz and pl.srednica_mm > ust["inspect"]["poprawka_min_mm"]
    assert n_pop >= 2, n_pop


def test_brak_danych_w_skanie_nie_jest_ubytkiem(korony, pula, ust):
    """Wycięte 30–60 % powierzchni (zasłonięcia): żadnego czerwonego, brak danych raportowany, nie liczony."""
    for p, k, wi in _lancuch(korony, pula, ust, seed=9, ubytki_na_prace=(0, 0), p_drgniecia=0.0, p_pokrycie=1.0):
        assert p.pokrycie < 1.0
        assert wi.status not in ("ubytek", "skan_ponownie"), (wi.status, wi.ubytki, wi.uwagi)
        assert all(u.kolor != "czerwony" for u in wi.ubytki)
        assert all(pl.rodzaj != "ubytek" for pl in wi.plamy)


def test_praca_bokiem_nigdy_czerwona(korony, pula, ust):
    """Praca bokiem / do góry nogami widziana z góry: albo popraw ułożenie (żółte), albo rozpoznana bez fałszywego ubytku."""
    n = 0
    for seed in (10, 11, 12):
        uk = U.wczytaj("okragla_wieczorna")
        rng = np.random.default_rng(seed)
        op = synth.Opcje.z_toml(plytka=uk.nazwa, prace_na_plytce=3, wspolczynnik=(1.22, 1.22), ubytki_na_prace=(0, 0), p_bokiem=1.0)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            skan, prawda = synth.generuj_plytke(uk, 8, list(korony), rng, op, seed)
            w = plate.wyrownaj(skan, uk)
        praw = {p.gniazdo: p for p in prawda.prace}
        for f in w.fragmenty:
            if f.status != "praca" or f.gniazdo not in praw:
                continue
            assert praw[f.gniazdo].ulozenie in ("bokiem", "do_gory_nogami") and praw[f.gniazdo].pokrycie < 1.0
            r = match.dopasuj(f.punkty, f.normalne, pula, ust, f.gniazdo)
            k = r.najlepszy
            if r.status == "szary":
                continue
            wi = I.sprawdz(f.punkty, f.normalne, pula.projekty[k.id], np.array(k.transformacja), k.pokrycie, ust, f.gniazdo)
            assert wi.status != "ubytek" and all(u.kolor != "czerwony" for u in wi.ubytki), (seed, f.gniazdo, wi.status, wi.ubytki)
            n += 1
    assert n >= 1


# --- progi z ustawień ------------------------------------------------------------------
def test_progi_z_ustawien_steruja_wynikiem(z_ubytkami, pula, ust):
    p, k, wi0 = z_ubytkami[0]
    P, N = _punkty(z_ubytkami, pula, ust, 0)
    pr = pula.projekty[k.id]
    T = np.array(k.transformacja)
    ust_glebokie = {**ust, "inspect": {**ust["inspect"], "prog_glebokosci_mm": 5.0}}
    wi = I.sprawdz(P, N, pr, T, k.pokrycie, ust_glebokie, p.gniazdo)
    assert all(u.metoda != "A" and u.metoda != "A+B" for u in wi.ubytki) and wi.plamy == []
    ust_b = {**ust, "inspect": {**ust["inspect"], "wciecie_min_mm": 5.0, "wciecie_pewne_mm": 6.0}}
    wi = I.sprawdz(P, N, pr, T, k.pokrycie, ust_b, p.gniazdo)
    assert all(u.metoda == "A" and u.kolor == "zolty" for u in wi.ubytki) and wi.linia_brzegu["wciec"] == 0
    ust_drg = {**ust, "inspect": {**ust["inspect"], "drgniecie_udzial_obszaru": 1e-9, "drgniecie_odchylka_mm": 1e-6}}
    assert I.sprawdz(P, N, pr, T, k.pokrycie, ust_drg, p.gniazdo).status == "skan_ponownie"


# --- jednostkowe -------------------------------------------------------------------------
def test_wykryj_drgniecie_na_sztucznych_odchylkach(ust):
    rng = np.random.default_rng(0)
    P = rng.uniform(-5, 5, (20000, 3))
    d = rng.normal(0, 0.03, 20000)
    assert not I.wykryj_drgniecie(P, d, ust["inspect"])["wykryte"]
    d2 = d.copy()
    warstwa = rng.uniform(size=len(P)) < 0.5
    d2[(P[:, 0] > 0) & warstwa] += 0.06  # połowa pracy jako dwie warstwy ±0,06 (ICP staje pośrodku)
    d2[(P[:, 0] > 0) & ~warstwa] -= 0.06
    r = I.wykryj_drgniecie(P, d2, ust["inspect"])
    assert r["wykryte"] and r["udzial_obszaru"] > 0.4
    d5 = d.copy()
    d5[P[:, 0] > 0] -= 0.2  # połowa pracy tylko pod powierzchnią (duża poprawka / złe ułożenie), nie drgnięcie
    assert not I.wykryj_drgniecie(P, d5, ust["inspect"])["wykryte"]
    d3 = d.copy()
    d3[np.linalg.norm(P - [1, 1, 1], axis=1) < 0.5] -= 0.3  # jedna plama (ubytek), nie drgnięcie
    assert not I.wykryj_drgniecie(P, d3, ust["inspect"])["wykryte"]


class _Plaski:
    """Zastępczy projekt: płaska siatka bez ostrych krawędzi (do plam)."""

    def __init__(self):
        self.siatka = trimesh.creation.box([20, 20, 0.001])
        self._krawedzie = np.zeros((0, 3))


def _siatka_punktow(krok=0.05):
    g = np.arange(-4, 4, krok)
    X, Y = np.meshgrid(g, g)
    return np.c_[X.ravel(), Y.ravel(), np.zeros(X.size)]


def test_plamy_ostra_vs_lagodna(ust):
    ui = ust["inspect"]
    P = _siatka_punktow()
    rho = np.hypot(P[:, 0], P[:, 1])
    d = np.random.default_rng(1).normal(0, 0.02, len(P))
    d[rho < 0.4] -= 0.3  # ostry dołek ø0,8
    pl = I.plamy_pod_powierzchnia(P, d, _Plaski(), ui)
    assert len(pl) == 1 and pl[0].rodzaj == "ubytek" and pl[0].ostra_krawedz and 0.5 < pl[0].srednica_mm < 1.2, pl
    d2 = np.random.default_rng(1).normal(0, 0.02, len(P)) - 0.3 * np.clip(1 - (rho / 2.5) ** 2, 0, None) ** 2  # gładkie ø5
    pl = I.plamy_pod_powierzchnia(P, d2, _Plaski(), ui)
    assert len(pl) == 1 and pl[0].rodzaj == "poprawka" and not pl[0].ostra_krawedz and pl[0].srednica_mm > ui["poprawka_min_mm"], pl
    d3 = np.random.default_rng(1).normal(0, 0.02, len(P))
    d3[rho < 1.0] -= 0.3  # ostra plama ø2 > srednica_max → sprawdź ułożenie
    pl = I.plamy_pod_powierzchnia(P, d3, _Plaski(), ui)
    assert len(pl) == 1 and pl[0].rodzaj == "sprawdz_ulozenie", pl
    d4 = np.random.default_rng(1).normal(0, 0.02, len(P))
    d4[(rho < 0.4) & (P[:, 0] > 3.7)] -= 0.3  # plama na skraju danych: pierścień niepełny → brak danych
    P4 = P[P[:, 0] <= 3.9]
    pl = I.plamy_pod_powierzchnia(P4, d4[P[:, 0] <= 3.9], _Plaski(), ui)
    assert all(p.rodzaj != "ubytek" for p in pl), pl


def test_dopasuj_do_prawdy():
    u = synth.Ubytek(0, 0, 0, 1.0, 0.35)
    wyk = [{"x": 0.3, "y": 0, "z": 0, "metoda": "A+B", "kolor": "czerwony"}, {"x": 5, "y": 5, "z": 0, "metoda": "B", "kolor": "zolty"}]
    r = I.dopasuj_do_prawdy([u], wyk)
    assert r["trafione"]["A"] == [True] and r["trafione"]["B"] == [True] and r["trafione"]["czerwony"] == [True]
    assert r["falszywe"] == 1 and r["falszywe_czerwone"] == 0


def test_status_gniazda_i_scenariusz():
    assert PO.status_gniazda("szary", {"status": "ubytek"}) == "szary"
    assert PO.status_gniazda("zielony", {"status": "ubytek"}) == "czerwony"
    assert PO.status_gniazda("zielony", {"status": "poprawka"}) == "pomaranczowy"
    assert PO.status_gniazda("zolty", {"status": "popraw_ulozenie"}) == "zolty"
    assert PO.status_gniazda("zielony", None) == "zielony"
    p = synth.PracaNaPlytce(1, "x", 1.0, np.eye(4).tolist())
    assert PO.scenariusz(p) == "dobrze"
    assert PO.scenariusz(synth.PracaNaPlytce(1, "x", 1.0, [], ulozenie="bokiem")) == "bokiem"
    assert PO.scenariusz(synth.PracaNaPlytce(1, "x", 1.0, [], pokrycie=0.5)) == "czesciowo"
    assert PO.scenariusz(synth.PracaNaPlytce(1, "x", 1.0, [], drgniecie=True, pokrycie=0.5)) == "drgniecie"


def test_json_wyniku_bez_tablic(z_ubytkami):
    import json

    for _, _, wi in z_ubytkami:
        d = wi.json()
        assert "_P" not in d and "_d" not in d
        json.dumps(d)
