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


@pytest.mark.parametrize("nazwa", ["wieczorna", "poranna", "wieczorna_r54", "poranna_r54"])
def test_osadzenie_w_gniezdzie_trzyma_sie_stozka(projekty, nazwa):
    """T4: wiele seedów i wszystkie rozmiary gniazd obu płytek (pełna siatka: test_edge_synth.py); układ R59 i R54."""
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
    g = next(g for g in U.wczytaj("wieczorna_r54").gniazda_okragle() if g.d_top == 9)
    walec = trimesh.creation.cylinder(radius=5.0, height=6.0)
    assert synth.osadz_w_gniezdzie(walec, g, np.random.default_rng(0)) is None


def test_generuj_plytke_i_prawda(projekty, tmp_path):
    uk = U.wczytaj("wieczorna_r54")
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


def test_uklad_r54_ma_te_sama_skale_co_typ_plytki():
    """R59: nazwa układu z przyrostkiem ``_r54`` nie zmienia tego, czy płytka jest poranna (skala 1,0)."""
    assert synth.poranna("poranna_r54") and synth.poranna("okragla_poranna_r54")
    assert not synth.poranna("wieczorna_r54") and not synth.poranna("okragla_wieczorna_r54")
    for n in ("poranna", "okragla_poranna", "wieczorna", "okragla_wieczorna"):
        assert synth.Opcje.z_toml(plytka=n + "_r54").wspolczynnik == synth.Opcje.z_toml(plytka=n).wspolczynnik


# --- P4 (15.11.2026): ubytek = poprawna geometria, ukruszenia celowe na krawędzi brzegu (K6) -----------------
def _korona_do_gory(projekty, i=1, skala=1.22):
    m = trimesh.load(projekty[i])
    m.apply_transform(synth.orientacja_brzegiem_do_gory(m) @ trimesh.transformations.scale_matrix(skala))
    return m


def _kontrola_geometrii(przed: trimesh.Trimesh, po: trimesh.Trimesh, c: np.ndarray, r: float) -> np.ndarray:
    """Wspólne warunki poprawnego ubytku; zwraca wierzchołki nowej powierzchni (na sferze kuli ubytku)."""
    odl_c = np.linalg.norm(po.vertices - c, axis=1)
    assert odl_c.min() > r - 1e-6  # materiał w kuli usunięty: żaden wierzchołek nie został wewnątrz kuli
    nowe = po.vertices[odl_c < r + 1e-6]
    assert len(nowe) >= 5
    # nowa powierzchnia leży W materiale pierwotnej bryły (trimesh: odległość dodatnia = wewnątrz), nic nie wisi w powietrzu
    odl = trimesh.proximity.signed_distance(przed, nowe)
    assert odl.min() > -1e-3, odl.min()
    return nowe


def test_czasza_ubytku_lezy_w_materiale_takze_na_krawedzi(projekty):
    """P4 (a): losowy ubytek przy samej krawędzi brzegu (pas 0,3 mm) — w wersji 2 żadna część czaszy nie wisi w
    powietrzu; wersja 1 (sprzed P4, zostawiona do odtwarzania starych zestawów) zostawia tam część czaszy."""
    m = _korona_do_gory(projekty)
    w_powietrzu_v1 = 0
    for seed in range(12):
        mat = synth.Material(m)
        po, ub = synth.wytnij_ubytek(m, 0.6, np.random.default_rng(seed), pas_brzegu=0.3, material=mat)
        c, r = mat.kule[-1]
        assert r == pytest.approx(0.3) and np.linalg.norm(c - [ub.x, ub.y, ub.z]) == pytest.approx(0.3 * 0.3, abs=1e-9)
        _kontrola_geometrii(m, po, c, r)
        assert ub.glebokosc == pytest.approx(0.21) and 0.05 < ub.glebokosc_rzeczywista <= 0.3 + 1e-6
        po1, ub1 = synth.wytnij_ubytek(m, 0.6, np.random.default_rng(seed), pas_brzegu=0.3, wersja=1)
        assert (ub1.x, ub1.y, ub1.z) == (ub.x, ub.y, ub.z) and ub1.glebokosc_rzeczywista is None and ub1.polozenie == ""
        nowe1 = po1.vertices[np.abs(np.linalg.norm(po1.vertices - c, axis=1) - r) < 1e-6]
        w_powietrzu_v1 += (trimesh.proximity.signed_distance(m, nowe1) < -0.02).mean() > 0.10
    assert w_powietrzu_v1 >= 6, w_powietrzu_v1  # stary generator: większość ubytków krawędziowych z czaszą w powietrzu


def test_ubytek_na_scianie_ma_glebokosc_nominalna(projekty):
    """Z dala od krawędzi (ściana, pas 4–6 mm pod brzegiem) czasza wersji 2 ma głębokość ≈ 0,7·r, jak zapisano w prawdzie."""
    m = _korona_do_gory(projekty)
    sciana = np.flatnonzero((m.vertices[:, 2] < -4.0) & (m.vertices[:, 2] > -6.0) & (np.hypot(m.vertices[:, 0], m.vertices[:, 1]) > 4.0))

    class _Wybor:  # „rng” wybierający zawsze z wierzchołków ściany zewnętrznej
        def __init__(self, seed):
            self.g = np.random.default_rng(seed)

        def choice(self, _):
            return self.g.choice(sciana)

    for seed in range(5):
        mat = synth.Material(m)
        po, ub = synth.wytnij_ubytek(m, 0.8, _Wybor(seed), material=mat)
        _kontrola_geometrii(m, po, *mat.kule[-1])
        assert ub.glebokosc == pytest.approx(0.28) and ub.glebokosc_rzeczywista == pytest.approx(0.28, abs=0.03)


def test_gestosc_punktow_ubytku_z_ustawien(projekty):
    """Nowa powierzchnia ubytku ma gęstość skanu: ok. jeden punkt na ``odstep``² (nie stałą liczbę jak w wersji 1)."""
    m = _korona_do_gory(projekty)
    licz = {}
    for odstep in (0.05, 0.1):
        mat = synth.Material(m)
        po, _ = synth.wytnij_ubytek(m, 1.0, np.random.default_rng(3), material=mat, odstep=odstep)
        c, r = mat.kule[-1]
        nowe = po.vertices[np.abs(np.linalg.norm(po.vertices - c, axis=1) - r) < 1e-6]
        pole = 2 * np.pi * r * 0.7 * r  # czasza o wysokości 0,7 r na płaskiej ścianie
        licz[odstep] = len(nowe)
        assert 0.4 * pole / odstep**2 < len(nowe) < 2.5 * pole / odstep**2, (odstep, len(nowe))
    assert licz[0.05] > 2.0 * licz[0.1]


@pytest.fixture(scope="module")
def korona_z_liniami(projekty):
    from stanowisko import krawedz

    m = _korona_do_gory(projekty)
    return m, krawedz.linie_siatki(m, skala=1.22)


@pytest.mark.parametrize("gdzie,klasa", [("srodek", "krawedz_srodek"), ("zewn", "krawedz_zewn"), ("wewn", "krawedz_wewn"), ("sciana", "sciana")])
def test_ukruszenie_celowe_na_krawedzi_brzegu(korona_z_liniami, gdzie, klasa):
    """K6: środek kuli leży NA powierzchni projektu, na linii krawędzi brzegu (albo na ścianie w pasie); rozmiar = promień."""
    m, linie = korona_z_liniami
    f = linie.filary[0]
    for seed, s in enumerate((0.08, 0.15, 0.30)):
        mat = synth.Material(m)
        po, ub = synth.wytnij_ukruszenie(m, linie, gdzie, s, np.random.default_rng(seed), material=mat)
        assert ub is not None and ub.celowy and ub.polozenie == klasa and ub.filar == 1
        assert ub.srednica == pytest.approx(2 * s) and ub.glebokosc == pytest.approx(s)
        p = np.array([ub.x, ub.y, ub.z])
        c, r = mat.kule[-1]
        assert np.allclose(c, p) and r == pytest.approx(s)
        _, odl, _ = trimesh.proximity.closest_point(m, [p])
        assert odl[0] < 1e-4  # środek kuli na powierzchni (błąd testów fali 1: środek pod powierzchnią)
        _kontrola_geometrii(m, po, c, r)
        # rzeczywista głębokość: najgłębszy punkt nowej powierzchni pod pierwotną — zmierzona niezależnie (trimesh)
        nowe = po.vertices[np.abs(np.linalg.norm(po.vertices - c, axis=1) - r) < 1e-6]
        zmierzona = trimesh.proximity.signed_distance(m, nowe).max()
        assert zmierzona <= ub.glebokosc_rzeczywista + 1e-3 and ub.glebokosc_rzeczywista <= s + 1e-4
        linia = {"srodek": f.S, "zewn": f.O, "wewn": f.I}.get(gdzie)
        if linia is not None:
            assert np.linalg.norm(linia - p, axis=1).min() < 1e-3
        if gdzie == "srodek":  # wgryz w płaską krawędź: głębokość bliska rozmiarowi (krawędź atrapy ma 0,73 mm szerokości)
            assert ub.glebokosc_rzeczywista > 0.85 * s if s <= 0.15 else ub.glebokosc_rzeczywista > 0.5 * s
        elif gdzie in ("zewn", "wewn"):  # odprysk narożnika: głębokość wyraźnie mniejsza niż rozmiar (≈ s·sin(kąt / 2))
            assert 0.4 * s < ub.glebokosc_rzeczywista < 0.98 * s and ub.odleglosc_od_linii < 0.03  # stacje linii co 0,05 mm
        else:  # ściana: kula nie dochodzi do płaskiej krawędzi, leży w pasie brzegu
            assert s + synth.SCIANA_OD_KRAWEDZI_MM - 1e-6 <= ub.odleglosc_od_linii <= 1.5 - s + 0.8 and ub.glebokosc_rzeczywista > 0.8 * s


def test_ukruszenia_celowe_nie_nachodza_na_siebie_i_brak_linii(korona_z_liniami):
    m, linie = korona_z_liniami
    mat = synth.Material(m)
    rng = np.random.default_rng(0)
    po, ubytki = m, []
    for gdzie in ("zewn", "srodek", "wewn", "zewn", "srodek"):
        po, ub = synth.wytnij_ukruszenie(po, linie, gdzie, 0.2, rng, material=mat)
        assert ub is not None
        ubytki.append(ub)
    P = np.array([[u.x, u.y, u.z] for u in ubytki])
    d = np.linalg.norm(P[:, None] - P[None], axis=2)[np.triu_indices(len(P), 1)]
    assert d.min() >= synth.ODSTEP_UKRUSZEN_MM + 0.4 - 1e-9
    for c, r in mat.kule:  # każda kula wycięta do końca, także po kolejnych ubytkach
        assert np.linalg.norm(po.vertices - c, axis=1).min() > r - 1e-6
    # bez linii (bryła bez wnęki) nie ma gdzie postawić ukruszenia: wynik jawny, siatka bez zmian
    from stanowisko import krawedz

    kula = trimesh.creation.icosphere(subdivisions=3, radius=4.0)
    wynik, ub = synth.wytnij_ukruszenie(kula, krawedz.linie_siatki(kula), "zewn", 0.2, np.random.default_rng(0))
    assert ub is None and wynik is kula
    assert synth.wytnij_ukruszenie(kula, None, "srodek", 0.2, np.random.default_rng(0))[1] is None
    with pytest.raises(ValueError, match="położenie"):
        synth.wytnij_ukruszenie(m, linie, "gdziekolwiek", 0.2, rng)
    with pytest.raises(ValueError, match="rozmiar"):
        synth.wytnij_ukruszenie(m, linie, "zewn", 0.0, rng)


def test_polozenie_wzgledem_brzegu(korona_z_liniami):
    _, linie = korona_z_liniami
    f = linie.filary[0]
    klasa, filar, odl = synth.polozenie_wzgledem_brzegu(linie, f.O[100], 0.1)
    assert (klasa, filar) == ("krawedz_zewn", 1) and odl < 0.03  # odległość do najbliższej stacji linii (co 0,05 mm)
    assert synth.polozenie_wzgledem_brzegu(linie, f.I[100], 0.1)[0] == "krawedz_wewn"
    assert synth.polozenie_wzgledem_brzegu(linie, f.S[100], 0.1)[0] == "krawedz_srodek"
    klasa, filar, odl = synth.polozenie_wzgledem_brzegu(linie, f.O[100] + [0, 0, -1.0], 0.3)  # 1 mm pod narożnikiem, kula 0,3
    assert klasa == "sciana" and filar == 1 and 0.9 < odl < 1.01
    assert synth.polozenie_wzgledem_brzegu(linie, f.O[100] + [0, 0, -0.2], 0.3)[0] == "krawedz_zewn"  # kula sięga krawędzi
    assert synth.polozenie_wzgledem_brzegu(None, f.O[100], 0.3) == ("", 0, None)


def test_generuj_plytke_z_ukruszeniami_krawedzi(projekty, tmp_path):
    """K6 w całym generatorze: klasy położenia i zmierzona głębokość w prawdzie, zapis / odczyt, stary format prawdy."""
    import json

    uk = U.wczytaj("okragla_wieczorna")
    op = synth.Opcje(ubytki_na_prace=(1, 1), krawedz_na_prace=(2, 2), krawedz_rozmiary=(0.1, 0.2), krawedz_polozenia=("zewn", "srodek"),
                     prace_na_plytce=2, wspolczynnik=(1.22, 1.22))
    skan, prawda = synth.generuj_plytke(uk, 8, projekty, np.random.default_rng(3), op, seed=3)
    assert len(prawda.prace) == 2
    for p in prawda.prace:
        celowe = [u for u in p.ubytki if u.celowy]
        losowe = [u for u in p.ubytki if not u.celowy]
        assert len(celowe) == 2 and len(losowe) == 1 and p.ukruszenia_pominiete == 0
        for u in celowe:
            assert u.polozenie in ("krawedz_zewn", "krawedz_srodek") and u.srednica in (pytest.approx(0.2), pytest.approx(0.4))
            assert u.glebokosc == pytest.approx(u.srednica / 2) and 0 < u.glebokosc_rzeczywista <= u.glebokosc + 1e-4 and u.filar == 1
        for u in losowe:
            assert u.polozenie in ("krawedz_zewn", "krawedz_srodek", "krawedz_wewn", "sciana") and u.glebokosc_rzeczywista > 0
            assert u.odleglosc_od_linii is not None and u.odleglosc_od_linii <= op.pas_brzegu + 1e-6
    _, p_json = synth.zapisz(skan, prawda, tmp_path, "k6")
    pr2 = synth.wczytaj_prawde(p_json)
    assert [dataclasses_asdict(u) for u in pr2.prace[0].ubytki] == [dataclasses_asdict(u) for u in prawda.prace[0].ubytki]
    # prawda sprzed P4 (bez nowych pól) nadal się wczytuje: pola dostają wartości „nieznane”
    d = json.loads(p_json.read_text(encoding="utf-8"))
    for p in d["prace"]:
        p.pop("ukruszenia_pominiete")
        for u in p["ubytki"]:
            for k in ("polozenie", "glebokosc_rzeczywista", "filar", "odleglosc_od_linii", "celowy"):
                u.pop(k)
    stary = tmp_path / "stary.json"
    stary.write_text(json.dumps(d), encoding="utf-8")
    pr3 = synth.wczytaj_prawde(stary)
    u3 = pr3.prace[0].ubytki[0]
    assert (u3.polozenie, u3.glebokosc_rzeczywista, u3.filar, u3.odleglosc_od_linii, u3.celowy) == ("", None, 0, None, False)
    assert pr3.prace[0].ukruszenia_pominiete == 0 and u3.srednica == prawda.prace[0].ubytki[0].srednica


def dataclasses_asdict(u):
    import dataclasses

    return dataclasses.asdict(u)


def test_wersja_1_generatora_do_odtwarzania_starych_zestawow(projekty):
    """``wersja_ubytkow`` = 1: ten sam seed daje ten sam skan co przed P4 (strumień losowy i geometria bez zmian);
    wersja 2 losuje te same prace, ale ubytki mają inną geometrię. K6 wymaga wersji 2."""
    uk = U.wczytaj("wieczorna")
    kw = dict(ubytki_na_prace=(1, 2), prace_na_plytce=3)
    a = synth.generuj_plytke(uk, 1, projekty, np.random.default_rng(4), synth.Opcje(wersja_ubytkow=1, **kw), seed=4)
    b = synth.generuj_plytke(uk, 1, projekty, np.random.default_rng(4), synth.Opcje(wersja_ubytkow=1, **kw), seed=4)
    assert np.array_equal(a[0].vertices, b[0].vertices) and np.array_equal(a[0].faces, b[0].faces)
    for p in a[1].prace:
        assert all(u.polozenie == "" and u.glebokosc_rzeczywista is None and not u.celowy for u in p.ubytki)
    c = synth.generuj_plytke(uk, 1, projekty, np.random.default_rng(4), synth.Opcje(**kw), seed=4)
    assert a[0].vertices.shape != c[0].vertices.shape  # inna siatka ubytków
    assert c[1].prace[0].projekt == a[1].prace[0].projekt and c[1].prace[0].gniazdo == a[1].prace[0].gniazdo  # początek losowania ten sam
    assert all(u.polozenie != "" and u.glebokosc_rzeczywista is not None for p in c[1].prace for u in p.ubytki)
    with pytest.raises(ValueError, match="wersja_ubytkow"):
        synth.Opcje(wersja_ubytkow=3)
    with pytest.raises(ValueError, match="K6"):
        synth.Opcje(wersja_ubytkow=1, krawedz_na_prace=(1, 1))
