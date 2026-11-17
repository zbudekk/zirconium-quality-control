"""inspect (P3a): mapa odchyłek (A), ciągłość linii brzegu (B), decyzja, drgnięcie, poprawka, brak danych, bokiem — na atrapach."""
from __future__ import annotations

import math
import shutil
import warnings
from dataclasses import asdict

import numpy as np
import pytest
import trimesh
from scipy.spatial import cKDTree

from stanowisko import inspect as I, krawedz as KR, match, plate, porownaj as PO, synth, ustawienia as UST, uklad as U


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
        assert set(d["brzeg"]) >= {"sprawdzony", "nie_sprawdzono", "filary", "opis"}  # P2: co z brzegu sprawdzono


# --- P2 (15.11.2026): pas brzegu od linii brzegu każdego filaru, status „nie sprawdzono” ------------------------
def bryla_obrotowa(profil, n=180, srodek=(0.0, 0.0), dz=0.0) -> trimesh.Trimesh:
    """Zamknięty profil (r, z) obrócony wokół osi z — szczelna siatka; faza kąta, żeby przekroje nie trafiały w wierzchołki."""
    profil = np.asarray(profil, dtype=float)
    th = np.linspace(0, 2 * math.pi, n, endpoint=False) + 0.0071
    V = np.vstack([np.c_[r * np.cos(th) + srodek[0], r * np.sin(th) + srodek[1], np.full(n, z + dz)] for r, z in profil])
    i = np.arange(n)
    j = np.roll(i, -1)
    F = []
    for a in range(len(profil)):
        b = (a + 1) % len(profil)
        F += [np.c_[a * n + i, b * n + i, b * n + j], np.c_[a * n + i, b * n + j, a * n + j]]
    m = trimesh.Trimesh(V, np.vstack(F), process=True)
    m.fix_normals()
    assert m.is_watertight and m.volume > 0
    return m


def filar_zaokraglony(srodek=(0.0, 0.0), dz=0.0) -> trimesh.Trimesh:
    """Filar z wnęką i ZAOKRĄGLONYM brzegiem (jak waxup): płaska krawędź 0,6 mm, fazy < 40°, więc projekt nie ma przy
    brzegu „ostrej krawędzi” — ukruszenie brzegu łapie tylko pas brzegu, nie reguła ostrej krawędzi projektu."""
    ro, ri, rd, h = 3.0, 2.0, 1.6, 6.0
    return bryla_obrotowa([(ro, -h), (ro, -0.2), (ro - 0.06, -0.07), (ro - 0.2, 0.0), (ri + 0.2, 0.0), (ri + 0.06, -0.07), (ri, -0.2),
                           (rd, -3.0), (0.02, -3.0), (0.02, -h)], srodek=srodek, dz=dz)


def _projekt(tmp, nazwa, czesci) -> match.Projekt:
    p = tmp / f"{nazwa}.stl"
    trimesh.util.concatenate(czesci).export(p)
    return match.Projekt(p, 1.0, "brzeg_gora")  # bryły testowe mają brzeg na górze, skala 1


def _skan(m: trimesh.Trimesh, odstep=0.05, seed=1):
    """Sztuczny skan = równomierna chmura punktów siatki z normalnymi trójkątów (układ puli; transformacja = pr.T0)."""
    P, fid = trimesh.sample.sample_surface(m, int(m.area / odstep**2), seed=seed)
    return np.asarray(P), np.asarray(m.face_normals[fid])


@pytest.fixture(scope="module")
def gleboki(tmp_path_factory):
    """Praca, w której brzeg filaru leży 4 mm PONIŻEJ najwyższego punktu (wyżej jest przęsło) — jak filary mostów:
    cały brzeg jest poza pasem 1,5 mm liczonym od płaszczyzny z = 0."""
    blok = trimesh.creation.box([8.0, 6.0, 3.0])
    blok.apply_translation([-5.5, 0.0, -1.5])  # „przęsło”: wierzch na z = 0, bez wnęki
    pr = _projekt(tmp_path_factory.mktemp("gleboki"), "gleboki", [filar_zaokraglony((5.0, 0.0), dz=-4.0), blok])
    brzeg = I.brzeg_projektu(pr)
    return pr, brzeg


def _ust(ust, **zmiany):
    return {**ust, "inspect": {**ust["inspect"], **zmiany}}


def test_pas_od_linii_obejmuje_brzeg_ponizej_plaszczyzny(gleboki, ust):
    """P2 (a): ukruszenie brzegu 4 mm pod najwyższym punktem pracy — pas od linii je widzi (A i B próbkują przy linii),
    pas od płaszczyzny (sposób sprzed P2) nie widzi go wcale i daje zielone."""
    pr, brzeg = gleboki
    linie = brzeg.linie
    assert len(linie.filary) == 1 and linie.filary[0].werdykt == "wiarygodna"
    zO = linie.filary[0].linie["O"].X[:, 2]
    assert zO.max() < -3.9 and zO.min() > -4.1  # cała linia brzegu poniżej pasa 1,5 mm od z = 0
    pas = ust["inspect"]["pas_brzegu_mm"]
    L_linia = I.probka_od_linii(pr, pas, brzeg)[0]
    L_plaszcz = I.probka_brzegu(pr, pas)[0]
    assert len(L_linia) > 5000 and L_linia[:, 2].max() < -3.9 and brzeg.drzewo.query(L_linia)[0].max() <= pas + 1e-9
    assert L_plaszcz[:, 2].min() >= -pas and L_plaszcz[:, 0].max() < 0  # stary pas: tylko wierzch przęsła, brzegu filaru w nim nie ma
    po, ub = synth.wytnij_ukruszenie(pr.siatka, linie, "srodek", 0.3, np.random.default_rng(2))
    assert ub is not None and ub.z < -3.9
    P, N = _skan(po)
    wi = I.sprawdz(P, N, pr, pr.T0, 0.99, _ust(ust, pas_brzegu_od="linia"), 1)
    assert wi.status in ("ubytek", "sprawdz"), (wi.status, wi.plamy, wi.uwagi)
    bliskie = [u for u in wi.ubytki if math.dist((u.x, u.y, u.z), (ub.x, ub.y, ub.z)) <= 0.6]
    assert bliskie and all(u.filar == 1 and u.odleglosc_od_brzegu_mm <= 0.6 for u in bliskie)
    assert any(u.metoda.startswith("A") for u in bliskie) and wi.brzeg["filarow"] == 1
    stary = I.sprawdz(P, N, pr, pr.T0, 0.99, _ust(ust, pas_brzegu_od="plaszczyzna"), 1)
    assert stary.status == "ok" and stary.ubytki == [] and stary.brzeg == {}  # przed P2: ukruszony brzeg = zielone
    assert any(pl.rodzaj == "poza_pasem" for pl in stary.plamy)


def test_tryb_sumy_pasow_obejmuje_brzeg_gleboki_i_stary_pas(gleboki, ust):
    """Tryb domyślny ``linia_i_plaszczyzna``: pas = suma pasa od linii i pasa sprzed P2 — widzi ukruszenie głębokiego brzegu
    (jak sama linia) ORAZ ubytek na wierzchu przęsła daleko od linii brzegu (jak sposób sprzed P2, sama linia go nie widzi)."""
    pr, brzeg = gleboki
    pas = ust["inspect"]["pas_brzegu_mm"]
    L, NL, n_linii = I.probka_suma(pr, pas, brzeg)
    L_linia, L_plaszcz = I.probka_od_linii(pr, pas, brzeg)[0], I.probka_brzegu(pr, pas)[0]
    assert n_linii == len(L_linia) and np.array_equal(L[:n_linii], L_linia) and len(L) == len(NL)
    assert len(L_linia) < len(L) <= len(L_linia) + len(L_plaszcz)  # część sprzed P2 bez punktów już objętych pasem od linii
    assert brzeg.drzewo.query(L[n_linii:])[0].min() > pas
    ust_suma = _ust(ust, pas_brzegu_od="linia_i_plaszczyzna")
    po, ub = synth.wytnij_ukruszenie(pr.siatka, brzeg.linie, "srodek", 0.3, np.random.default_rng(2))
    P, N = _skan(po)
    wi = I.sprawdz(P, N, pr, pr.T0, 0.99, ust_suma, 1)
    assert wi.status in ("ubytek", "sprawdz") and any(math.dist((u.x, u.y, u.z), (ub.x, ub.y, ub.z)) <= 0.6 for u in wi.ubytki)
    # ubytek na wierzchu „przęsła” (z = 0, ok. 7 mm od linii brzegu filaru): pas sprzed P2 go obejmuje, pas od linii nie
    srodek = np.array([-6.0, 0.0, 0.0])
    assert brzeg.drzewo.query(srodek)[0] > 3.0
    m = pr.siatka
    P0, fid = trimesh.sample.sample_surface(m, int(m.area / 0.05**2), seed=4)
    P0, N0 = np.asarray(P0), np.asarray(m.face_normals[fid])
    r = np.linalg.norm(P0 - srodek, axis=1)
    w = r < 0.35
    P0[w] = P0[w] - N0[w] * np.sqrt(np.maximum(0.35**2 - r[w] ** 2, 0.0))[:, None]  # czasza kuli r 0,35 w głąb materiału
    suma = I.sprawdz(P0, N0, pr, pr.T0, 0.99, ust_suma, 1)
    linia = I.sprawdz(P0, N0, pr, pr.T0, 0.99, _ust(ust, pas_brzegu_od="linia"), 1)
    plaszcz = I.sprawdz(P0, N0, pr, pr.T0, 0.99, _ust(ust, pas_brzegu_od="plaszczyzna"), 1)
    blisko = lambda wi: [u for u in wi.ubytki if math.dist((u.x, u.y), (srodek[0], srodek[1])) <= 0.8]  # noqa: E731
    assert blisko(plaszcz) and blisko(suma), (plaszcz.plamy, suma.plamy)
    assert not blisko(linia) and any(pl.rodzaj == "poza_pasem" for pl in linia.plamy)


def test_praca_cala_z_glebokim_brzegiem_jest_zielona(gleboki, ust):
    pr, brzeg = gleboki
    P, N = _skan(pr.siatka)
    assert I.sprawdz(P, N, pr, pr.T0, 0.99, _ust(ust, pas_brzegu_od="linia_i_plaszczyzna"), 1).status == "ok"
    ust = _ust(ust, pas_brzegu_od="linia")
    wi = I.sprawdz(P, N, pr, pr.T0, 0.99, ust, 1)
    assert wi.status == "ok" and wi.ubytki == [], (wi.status, wi.uwagi)
    assert wi.brzeg["sprawdzony"] and wi.brzeg["nie_sprawdzono"] == [] and wi.brzeg["stan_linii"] == "wiarygodne"
    f = wi.brzeg["filary"][0]
    # zaokrąglony brzeg: ok. 8 % przekrojów bez dwóch zgodnych wyznaczeń narożnika (krótkie odcinki, linia nadal wiarygodna)
    assert f["sprawdzony"] and f["udzial_sprawdzony"] >= ust["inspect"]["brzeg_min_sprawdzony"] and f["udzial_z_danymi"] > 0.99 and f["powody"] == []
    assert all(o["dlugosc_mm"] <= ust["inspect"]["brzeg_max_przerwa_mm"] and o["powod"] == "linia" for o in f["odcinki"])
    assert wi.czas_linii_s >= 0.0 and wi.linia_brzegu["udzial_ciagly"] > 0.95


def test_brak_danych_przy_linii_brzegu_to_nie_sprawdzono(gleboki, ust):
    """P2 (b): linia brzegu w skanie niewidoczna na części obwodu — „nie sprawdzono” (żółte), nigdy zielone ani czerwone;
    wynik mówi, który filar i jaka część linii; progi z ustawień sterują wynikiem."""
    pr, brzeg = gleboki
    P, N = _skan(pr.siatka)
    f = brzeg.linie.filary[0]
    kat = np.degrees(np.arctan2(P[:, 1] - f.srodek[1], P[:, 0] - f.srodek[0]))
    dziura = (np.abs(kat) < 60) & (brzeg.drzewo.query(P)[0] < 2.5)  # trzecia część obwodu brzegu bez danych
    suma = I.sprawdz(P[~dziura], N[~dziura], pr, pr.T0, 0.99, _ust(ust, pas_brzegu_od="linia_i_plaszczyzna"), 7)
    assert suma.status == "nie_sprawdzono" and suma.brzeg["filary"][0]["powody"] == ["dane"]  # brak danych skanu: tak samo w trybie sumy
    ust = _ust(ust, pas_brzegu_od="linia")
    wi = I.sprawdz(P[~dziura], N[~dziura], pr, pr.T0, 0.99, ust, 7)
    assert wi.status == "nie_sprawdzono" and wi.ubytki == [] and all(pl.rodzaj != "ubytek" for pl in wi.plamy), (wi.status, wi.uwagi)
    b = wi.brzeg
    assert not b["sprawdzony"] and b["nie_sprawdzono"] == [1] and "filar 1" in b["opis"] and "brak danych" in b["opis"]
    fb = b["filary"][0]
    assert fb["powody"] == ["dane"] and 0.55 < fb["udzial_sprawdzony"] < 0.85 and fb["udzial_linii_pewnej"] >= ust["inspect"]["brzeg_min_sprawdzony"]
    assert 3.0 < fb["najdl_przerwa_mm"] < 6.5  # 120° obwodu o promieniu 2,8 mm bez skraju, przy którym dane są bliżej niż 0,8 mm
    od = fb["odcinki"][0]
    assert od["powod"] == "dane" and od["dlugosc_mm"] == pytest.approx(fb["najdl_przerwa_mm"], abs=0.11) and od["srodek"][0] > f.srodek[0] + 2.0
    assert any("brzeg nie sprawdzony" in u for u in wi.uwagi)
    assert PO.status_gniazda("zielony", wi.json()) == "zolty" and PO.OPISY_INSPEKCJI[wi.status] == "nie sprawdzono"
    # próg z ustawień: dopuszczona ćwiartka bez sprawdzenia → zielone
    luz = I.sprawdz(P[~dziura], N[~dziura], pr, pr.T0, 0.99, _ust(ust, brzeg_min_sprawdzony=0.5, brzeg_max_przerwa_mm=50.0), 7)
    assert luz.status == "ok" and luz.brzeg["sprawdzony"]
    # sama długość przerwy też decyduje: udział wystarczy, przerwa za długa
    ostro = I.sprawdz(P[~dziura], N[~dziura], pr, pr.T0, 0.99, _ust(ust, brzeg_min_sprawdzony=0.5, brzeg_max_przerwa_mm=1.0), 7)
    assert ostro.status == "nie_sprawdzono"
    # sposób sprzed P2 nie zna tego statusu
    assert I.sprawdz(P[~dziura], N[~dziura], pr, pr.T0, 0.99, _ust(ust, pas_brzegu_od="plaszczyzna"), 7).status == "ok"


def test_brak_danych_i_ukruszenie_obok_nigdy_czerwone_z_braku_danych(gleboki, ust):
    """Brak danych nie robi czerwonego, ale też nie gasi prawdziwego ubytku: ukruszenie w widocznej części brzegu zostaje
    wykryte, a brak danych gdzie indziej jest tylko w opisie."""
    pr, brzeg = gleboki
    f = brzeg.linie.filary[0]
    i = int(np.argmin(np.abs(np.degrees(f.katy) - 180.0)))
    assert f.zweryf[i]

    class _Staly:  # „rng” stawiający ukruszenie na przekroju 180° (naprzeciw dziury w danych)
        def integers(self, n):
            return 0

        def choice(self, a):
            return i

    po, ub = synth.wytnij_ukruszenie(pr.siatka, brzeg.linie, "srodek", 0.3, _Staly())
    P, N = _skan(po)
    kat = np.degrees(np.arctan2(P[:, 1] - f.srodek[1], P[:, 0] - f.srodek[0]))
    dziura = (np.abs(kat) < 45) & (brzeg.drzewo.query(P)[0] < 2.5)
    ust = _ust(ust, pas_brzegu_od="linia")
    wi = I.sprawdz(P[~dziura], N[~dziura], pr, pr.T0, 0.99, ust, 3)
    assert wi.status in ("ubytek", "sprawdz") and not wi.brzeg["sprawdzony"] and any("brzeg nie sprawdzony" in u for u in wi.uwagi)
    for u in wi.ubytki:  # wszystkie zgłoszenia leżą przy ukruszeniu, żadne przy dziurze w danych
        assert math.dist((u.x, u.y, u.z), (ub.x, ub.y, ub.z)) <= 1.0, (u, ub)


def test_linia_projektu_niepewna_albo_brak_linii_to_nie_sprawdzono(tmp_path, ust):
    """P2 (b): linii projektu nie wyznaczono wiarygodnie → „nie sprawdzono”, choć skan jest pełny i bez odchyłek."""
    from test_krawedz import tuleja

    blok = trimesh.creation.box([8.0, 6.0, 3.0])
    blok.apply_translation([-6.0, 0.0, -1.5])
    # tuleja z kanałem na wylot obok bloku: wariant 2 nie działa (brak ściany wnęki), a oś „T3” leży poza filarem —
    # (prawie) żaden przekrój nie ma dwóch zgodnych wyznaczeń, pętla nie jest wiarygodna
    pr = _projekt(tmp_path, "niepewny", [tuleja(2.2, 1.4, srodek=(4.0, 0.0)), blok])
    linie = I.brzeg_projektu(pr).linie
    assert len(linie.filary) == 1 and linie.filary[0].werdykt != "wiarygodna" and linie.stan == "czesciowe"
    P, N = _skan(pr.siatka)
    ust_suma, ust = _ust(ust, pas_brzegu_od="linia_i_plaszczyzna"), _ust(ust, pas_brzegu_od="linia")
    # tryb sumy (domyślny): niepewna linia projektu to nasze ograniczenie, nie skanu — zielone z uwagą, pas także od płaszczyzny
    suma = I.sprawdz(P, N, pr, pr.T0, 0.99, ust_suma, 2)
    assert suma.status == "ok" and suma.brzeg["sprawdzony"] and suma.brzeg["filary"][0]["powody"] == []
    assert "linia projektu niepewna" in suma.brzeg["uwagi_linii"] and any("linia projektu niepewna" in u for u in suma.uwagi)
    wi = I.sprawdz(P, N, pr, pr.T0, 0.99, ust, 2)
    assert wi.status == "nie_sprawdzono" and wi.ubytki == []
    fb = wi.brzeg["filary"][0]
    assert fb["powody"] == ["linia"] and fb["udzial_z_danymi"] > 0.95 and fb["udzial_linii_pewnej"] < 0.5 and "linia projektu niepewna" in wi.brzeg["opis"]
    assert fb["odcinki"] and fb["odcinki"][0]["powod"] == "linia"
    assert I.sprawdz(P, N, pr, pr.T0, 0.99, _ust(ust, pas_brzegu_od="plaszczyzna"), 2).status == "ok"
    # bryła bez wnęki: żadnej linii
    pr2 = _projekt(tmp_path, "bez_wneki", [trimesh.creation.box([8.0, 6.0, 5.0])])
    P, N = _skan(pr2.siatka)
    suma = I.sprawdz(P, N, pr2, pr2.T0, 0.99, ust_suma, 3)
    assert suma.status == "ok" and suma.brzeg["stan_linii"] == "brak" and "nie wyznaczono" in suma.brzeg["uwagi_linii"]
    assert suma.linia_brzegu["punktow_linii"] == len(I.probka_brzegu(pr2, ust["inspect"]["pas_brzegu_mm"])[0]) > 0  # pas sprzed P2
    wi = I.sprawdz(P, N, pr2, pr2.T0, 0.99, ust, 3)
    assert wi.status == "nie_sprawdzono" and wi.brzeg["stan_linii"] == "brak" and wi.brzeg["filary"] == [] and "nie wyznaczono" in wi.brzeg["opis"]
    assert wi.linia_brzegu["punktow_linii"] == 0


def test_projekt_bez_linii_z_wcieciem_w_trybie_sumy_dziala_jak_przed_p2(tmp_path, ust):
    """B1 (recenzja PR #13): projekt bez żadnej linii brzegu (bryła bez wnęki, ``brzeg.drzewo is None``) i skupisko wcięć
    metody B w trybie domyślnym ``linia_i_plaszczyzna`` — wynik taki sam jak przy pasie od płaszczyzny (sposób sprzed P2),
    bez wyjątku. Scenariusz recenzenta: pudełko 8 × 6 × 5 mm, wgłębienie 0,3 mm o płaskim dnie na ścianie bocznej 0,7 mm
    pod wierzchem (r 0,6) i na wierzchu (r 0,8)."""
    pr = _projekt(tmp_path, "bez_wneki_b1", [trimesh.creation.box([8.0, 6.0, 5.0])])
    brzeg = I.brzeg_projektu(pr)
    assert brzeg.linie.filary == [] and brzeg.drzewo is None and brzeg.drzewo_O is None
    P0, N0 = _skan(pr.siatka, seed=4)
    statusy = []
    for srodek, r0 in (((4.0, 0.0, -0.7), 0.6), ((1.0, 0.5, 0.0), 0.8)):
        P = P0.copy()
        w = np.linalg.norm(P - np.array(srodek), axis=1) < r0
        P[w] = P[w] - N0[w] * 0.3
        plaszcz = I.sprawdz(P, N0, pr, pr.T0, 0.99, _ust(ust, pas_brzegu_od="plaszczyzna"), 1)
        assert any(v.rodzaj == "wciecie" for v in plaszcz.wciecia), plaszcz.wciecia  # metoda B ma skupisko wcięć
        # przed poprawką: AttributeError: 'NoneType' object has no attribute 'query' (inspect._linia_brzegu)
        suma = I.sprawdz(P, N0, pr, pr.T0, 0.99, _ust(ust, pas_brzegu_od="linia_i_plaszczyzna"), 1)
        assert suma.status == plaszcz.status
        assert [asdict(u) for u in suma.ubytki] == [asdict(u) for u in plaszcz.ubytki]
        assert [asdict(v) for v in suma.wciecia] == [asdict(v) for v in plaszcz.wciecia]
        assert [asdict(p) for p in suma.plamy] == [asdict(p) for p in plaszcz.plamy]
        assert suma.linia_brzegu == plaszcz.linia_brzegu and all(v.filar == 0 for v in suma.wciecia)
        assert suma.brzeg["stan_linii"] == "brak" and suma.brzeg["sprawdzony"] and "nie wyznaczono" in suma.brzeg["uwagi_linii"]
        # tryb samej linii: projekt bez linii = „nie sprawdzono” (bez zmiany)
        assert I.sprawdz(P, N0, pr, pr.T0, 0.99, _ust(ust, pas_brzegu_od="linia"), 1).status == "nie_sprawdzono"
        statusy.append((plaszcz.status, sorted({(u.metoda, u.kolor) for u in plaszcz.ubytki})))
    assert statusy == [("ubytek", [("A+B", "czerwony")]), ("sprawdz", [("B", "zolty")])], statusy  # jak na ``main``: czerwony ubytek / żółte „sprawdź”


def test_filar_z_niecka_bez_linii_nie_znika_po_cichu(tmp_path, ust, monkeypatch):
    """P1 (recenzja PR #13): praca z dwoma filarami; dla filaru 2 niecka jest przyjęta, ale linii nie wyznaczono
    (``krawedz.wyznacz`` zostawia wtedy tylko wpis „linii nie wyznaczono” w ``uwagi`` — filaru nie ma na liście ``filary``).
    Tryb ``linia``: brzeg tego filaru nie jest sprawdzony → „nie sprawdzono”, nigdy zielone. Tryb domyślny: działa pas od
    płaszczyzny (jak przed P2), ale wynik ma o tym uwagę."""
    pr = _projekt(tmp_path, "dwa_filary", [filar_zaokraglony((-5.0, 0.0)), filar_zaokraglony((5.0, 0.0))])
    pelny = I.brzeg_projektu(pr)
    assert [f.nr for f in pelny.linie.filary] == [1, 2] and sum(n["przyjeta"] for n in pelny.linie.niecki) == 2
    P, N = _skan(pr.siatka)
    ust_linia, ust_suma = _ust(ust, pas_brzegu_od="linia"), _ust(ust, pas_brzegu_od="linia_i_plaszczyzna")
    for u in (ust_linia, ust_suma):  # komplet linii: zielone, a wynik nie ma nowego pola (zwykłe dane bez zmian)
        wi = I.sprawdz(P, N, pr, pr.T0, 0.99, u, 1)
        assert wi.status == "ok" and wi.brzeg["filarow"] == 2 and "filary_bez_linii" not in wi.brzeg, (wi.status, wi.uwagi)
        assert not any("nie wyznaczono" in x for x in wi.uwagi)
    # te same linie bez filaru 2 — tak zwraca je krawedz.wyznacz, gdy żaden wariant nie da linii filaru
    bez_2 = KR.LinieProjektu([pelny.linie.filary[0]], pelny.linie.niecki, ["filar 2: za malo udanych przekrojow - linii nie wyznaczono"],
                             0.0, pelny.linie.skala)
    st, so = KR.stacje(bez_2, ("O", "I")), KR.stacje(bez_2, ("O",))
    brzeg = I.BrzegProjektu(bez_2, st["X"], st["filar"], cKDTree(st["X"]), so["X"], so["filar"], so["zweryf"], cKDTree(so["X"]))
    klucz = next(k for k, b in I._BRZEGI.items() if b is pelny)
    monkeypatch.setitem(I._BRZEGI, klucz, brzeg)
    assert I.brzeg_projektu(pr) is brzeg
    wi = I.sprawdz(P, N, pr, pr.T0, 0.99, ust_linia, 1)
    # przed poprawką: "ok" — zielone, choć brzegu filaru 2 nikt nie sprawdził
    assert wi.status == "nie_sprawdzono" and wi.ubytki == [], (wi.status, wi.brzeg.get("opis"), wi.uwagi)
    b = wi.brzeg
    assert not b["sprawdzony"] and b["nie_sprawdzono"] == [2] and b["filary_bez_linii"] == [2]
    assert "filar 2" in b["opis"] and "nie wyznaczono" in b["opis"]
    f1, f2 = (next(f for f in b["filary"] if f["nr"] == nr) for nr in (1, 2))
    assert f1["sprawdzony"] and f1["powody"] == []
    assert not f2["sprawdzony"] and f2["powody"] == ["linia"] and f2["werdykt_linii"] == "brak" and f2["odcinki"] == [] and f2["udzial_sprawdzony"] == 0.0
    assert set(f2) == set(f1)  # wpis filaru bez linii ma te same pola co zwykły
    assert any("brzeg nie sprawdzony" in u and "filar 2" in u for u in wi.uwagi)
    assert PO.status_gniazda("zielony", wi.json()) == "zolty" and PO.OPISY_INSPEKCJI[wi.status] == "nie sprawdzono"
    suma = I.sprawdz(P, N, pr, pr.T0, 0.99, ust_suma, 1)
    assert suma.status == "ok" and suma.brzeg["sprawdzony"] and suma.brzeg["nie_sprawdzono"] == []
    # przed poprawką: uwagi_linii puste — wynik nie mówił, że linii filaru 2 nie wyznaczono
    assert suma.brzeg["filary_bez_linii"] == [2] and "filar 2" in suma.brzeg["uwagi_linii"] and "nie wyznaczono" in suma.brzeg["uwagi_linii"]
    assert any("filar 2" in u and "nie wyznaczono" in u for u in suma.uwagi)
    assert [f["nr"] for f in suma.brzeg["filary"]] == [1]  # w trybie sumy brzeg filaru bez linii ocenia tylko pas od płaszczyzny
    # ukruszenie brzegu filaru 2 (brzeg na z = 0, czyli w pasie od płaszczyzny): tryb domyślny widzi je jak przed P2
    f = pelny.linie.filary[1]
    i = int(np.flatnonzero(f.zweryf)[int(f.zweryf.sum()) // 2])

    class _Staly:  # „rng” stawiający ukruszenie na filarze 2
        def integers(self, n):
            return 1

        def choice(self, a):
            return i

    po, ub = synth.wytnij_ukruszenie(pr.siatka, pelny.linie, "srodek", 0.3, _Staly())
    assert ub is not None and ub.filar == 2
    Pu, Nu = _skan(po)
    z_ukr = I.sprawdz(Pu, Nu, pr, pr.T0, 0.99, ust_suma, 1)
    assert z_ukr.status in ("ubytek", "sprawdz") and any(math.dist((u.x, u.y, u.z), (ub.x, ub.y, ub.z)) <= 0.6 for u in z_ukr.ubytki)
    assert any("filar 2" in u and "nie wyznaczono" in u for u in z_ukr.uwagi)


def test_prace_bokiem_i_czesciowe_nie_sa_zielone_bez_sprawdzonego_brzegu(korony, pula, ust):
    """Praca z wyciętą częścią powierzchni: gdy inspekcja jest liczona i nie ma ubytku, status zależy od tego, czy brzeg
    każdego filaru został sprawdzony — „ok” tylko ze sprawdzonym brzegiem."""
    n = 0
    for p, k, wi in _lancuch(korony, pula, ust, seed=9, ubytki_na_prace=(0, 0), p_drgniecia=0.0, p_pokrycie=1.0):
        if wi.status in ("ok", "nie_sprawdzono"):
            n += 1
            assert (wi.status == "ok") == wi.brzeg["sprawdzony"], (wi.status, wi.brzeg["opis"])
    assert n >= 1


def test_status_nie_sprawdzono_w_porownaj():
    assert "nie_sprawdzono" in I.STATUSY and PO.INSPECT_NA_STATUS["nie_sprawdzono"] == "zolty"
    assert PO.status_gniazda("zielony", {"status": "nie_sprawdzono"}) == "zolty"
    assert PO.status_gniazda("szary", {"status": "nie_sprawdzono"}) == "szary"
    assert set(PO.OPISY_INSPEKCJI) == set(I.STATUSY) and PO.OPISY_INSPEKCJI["nie_sprawdzono"] == "nie sprawdzono"
    k = {"id": "a" * 16, "zeby": ["16"], "pokrycie": 0.97}
    ins = {"status": "nie_sprawdzono", "ubytki": [], "brzeg": {"sprawdzony": False, "opis": "filar 2: sprawdzono 40% linii brzegu"}}
    wynik = {"skan": "s.stl", "plytka": "wieczorna", "numer": 1, "numer_zrodlo": "dolki", "wspolczynnik": 1.22, "projekty": 3,
             "czas_s": {"razem": 1.0, "plate": 0.5, "match": 0.4}, "gniazda_puste": [], "gniazda_podwojne": [], "poza_gniazdem": 0, "ubytki": 0,
             "statusy_gniazd": {"zielony": 1, "zolty": 1},
             "gniazda": [{"gniazdo": 3, "status_fragmentu": "praca", "kandydaci": [k], "pewnosc": 0.5, "status": "zielony", "status_gniazda": "zolty", "inspekcja": ins},
                         {"gniazdo": 4, "status_fragmentu": "praca", "kandydaci": [k], "pewnosc": 0.5, "status": "zielony", "status_gniazda": "zielony",
                          "inspekcja": {"status": "ok", "ubytki": [], "brzeg": {"sprawdzony": True, "opis": ""}}}]}
    assert PO.gniazda_nie_sprawdzone(wynik) == [3]
    t = PO.tabela(wynik)
    assert "NIE SPRAWDZONO" in t and "gniazda [3]" in t and "gniazdo 3: brzeg nie sprawdzony — filar 2" in t and "gniazdo 4: brzeg" not in t


def test_metryki_inspekcji_krawedz_i_sciana_osobno():
    """P4 (c): liczniki osobno dla ubytków na krawędzi i na ścianie; prawda bez klasy → „nieznane”; praca cała ze
    statusem „nie sprawdzono” nie jest alarmem."""
    def gniazdo(nr, status, wykryte):
        return {"gniazdo": nr, "status_fragmentu": "praca", "kandydaci": [{"id": f"p{nr}"}], "status": "zielony",
                "status_gniazda": PO.INSPECT_NA_STATUS[status], "inspekcja": {"status": status, "ubytki": wykryte, "plamy": []}}

    def wykrycie(x, metoda, kolor):
        return {"x": x, "y": 0.0, "z": 0.0, "metoda": metoda, "kolor": kolor}

    u_kr = synth.Ubytek(0, 0, 0, 0.3, 0.15, polozenie="krawedz_zewn", glebokosc_rzeczywista=0.11, celowy=True, filar=1, odleglosc_od_linii=0.0)
    u_kr2 = synth.Ubytek(5, 0, 0, 0.3, 0.15, polozenie="krawedz_srodek", glebokosc_rzeczywista=0.15, celowy=True, filar=1)
    u_sc = synth.Ubytek(10, 0, 0, 0.8, 0.28, polozenie="sciana", glebokosc_rzeczywista=0.27)
    u_st = synth.Ubytek(0, 0, 0, 0.8, 0.28)  # prawda sprzed P4
    prace = [synth.PracaNaPlytce(1, "p1", 1.22, np.eye(4).tolist(), ubytki=[u_kr, u_kr2, u_sc]),
             synth.PracaNaPlytce(2, "p2", 1.22, np.eye(4).tolist(), ubytki=[u_st]),
             synth.PracaNaPlytce(3, "p3", 1.22, np.eye(4).tolist()), synth.PracaNaPlytce(4, "p4", 1.22, np.eye(4).tolist()),
             synth.PracaNaPlytce(5, "p5", 1.22, np.eye(4).tolist())]
    prawda = synth.PrawdaPlytki("wieczorna", 1, 0, 0.0, 8.0, prace, [])
    wynik = {"gniazda": [gniazdo(1, "ubytek", [wykrycie(0.1, "A", "zolty"), wykrycie(10.1, "A+B", "czerwony")]),
                         gniazdo(2, "sprawdz", [wykrycie(0.0, "B", "zolty")]), gniazdo(3, "nie_sprawdzono", []), gniazdo(4, "ok", []),
                         gniazdo(5, "sprawdz", [wykrycie(3.0, "A", "zolty")])]}
    mi = PO.metryki_inspekcji(wynik, prawda)
    r = mi["razem"]
    assert r["klasy"]["krawedz"] == {"wszystkich": 2, "ubytkow": 2, "wykryte": {"A": 1, "B": 0, "A+B": 0, "czerwony": 0, "dowolny": 1}}
    assert r["klasy"]["sciana"] == {"wszystkich": 1, "ubytkow": 1, "wykryte": {"A": 1, "B": 1, "A+B": 1, "czerwony": 1, "dowolny": 1}}
    assert r["klasy"]["nieznane"]["wszystkich"] == 1 and r["klasy"]["nieznane"]["wykryte"]["B"] == 1
    assert r["ubytkow"] == 4 and r["wykryte"]["dowolny"] == 3  # suma klas = liczniki łączne
    assert sum(r["klasy"][k]["ubytkow"] for k in PO.KLASY_POLOZENIA) == r["ubytkow"]
    assert r["prac_calych"] == 3 and r["prace_cale_z_alarmem"] == 1 and r["prace_cale_z_czerwonym"] == 0 and r["prace_cale_nie_sprawdzono"] == 1
    assert r["prace_cale_status_gniazda"] == {"zielony": 1, "czerwony": 0, "zolty": 2, "szary": 0, "pomaranczowy": 0}
    assert r["statusy"]["nie_sprawdzono"] == 1 and r["prace_nie_sprawdzono"] == 1 and mi["scenariusze"]["dobrze"]["klasy"] == r["klasy"]
    lista = mi["ubytki"]
    assert len(lista) == 4 and [x["klasa"] for x in lista] == ["krawedz", "krawedz", "sciana", "nieznane"]
    assert lista[0]["trafione"]["dowolny"] and not lista[1]["trafione"]["dowolny"] and lista[0]["celowy"] and lista[0]["glebokosc_rzeczywista"] == 0.11
    assert lista[2]["trafione"]["czerwony"] and lista[2]["projekt"] == "p1" and lista[3]["polozenie"] == ""


def test_polozenie_ubytku_starej_prawdy_z_linii_projektu(pula):
    """Prawda sprzed P4 nie ma klasy położenia: klasa (krawędź / ściana) jest liczona z linii brzegu projektu w puli."""
    pr = next(iter(pula.projekty.values()))
    f = I.brzeg_projektu(pr).linie.filary[0]
    T = pr.T0  # transformacja_do_projektu(pr, pr.T0) = macierz jednostkowa: układ „płytki” = układ puli
    na_krawedzi = synth.Ubytek(*f.O[50], srednica=0.4, glebokosc=0.14)
    assert I.polozenie_ubytku_prawdy(na_krawedzi, pr, T)[0] == "krawedz"
    na_srodku = synth.Ubytek(*f.S[50], srednica=0.3, glebokosc=0.1)
    assert I.polozenie_ubytku_prawdy(na_srodku, pr, T)[0] == "krawedz"
    nizej = synth.Ubytek(*(f.O[50] + [0.0, 0.0, -1.2]), srednica=0.6, glebokosc=0.2)
    klasa, odl = I.polozenie_ubytku_prawdy(nizej, pr, T)
    assert klasa == "sciana" and 1.1 < odl < 1.25
    assert I.klasa_polozenia("krawedz_wewn") == "krawedz" and I.klasa_polozenia("sciana") == "sciana" and I.klasa_polozenia("") == "nieznane"
