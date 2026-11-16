"""synth.py: osadzanie bez przenikania (B1, B1b), walidacje wejść (S2–S4, S7, S9), prawda (S1, P1), determinizm.

Przeniesione z sesje_2026-10-31/kod_a_stanowisko/testy_edge/test_edge_synth.py (xfail zdjęty
po naprawie P1 2026-11-02; numery gniazd dopasowane do układu R54) + nowe przypadki.
Funkcje ``przenikanie_okr`` / ``przenikanie_ryn`` są niezależne od ``synth.przenikanie``.
R59 (14.11.2026): testy z gniazdami ø9 / ø7,5 (układ R54) działają na ``wieczorna_r54`` / ``poranna_r54`` bez zmiany
oczekiwań; siatki „wszystkie gniazda” obejmują oba układy.
"""
import dataclasses
import json
import math
import sys

import numpy as np
import pytest
import trimesh

import atrapy_koron
from conftest import zapisz_ascii_stl
from stanowisko import synth, ustawienia as UST, uklad as U

TAN = math.tan(math.radians(15.0))


def przenikanie_okr(V, g):
    rho = np.hypot(V[:, 0] - g.x, V[:, 1] - g.y)
    z = V[:, 2]
    w = z < g.z_top
    dop = g.promien_dolny() + (z[w] - g.z_dno) * TAN
    return float(np.maximum(rho[w] - dop, 0).max(initial=0.0))


def przenikanie_ryn(V, g):
    a = math.radians(g.angle)
    dx, dy = V[:, 0] - g.x, V[:, 1] - g.y
    u = dx * math.cos(a) + dy * math.sin(a)
    v = -dx * math.sin(a) + dy * math.cos(a)
    z = V[:, 2]
    w = z < g.z_top
    du = g.l / 2 - g.depth * TAN + (z[w] - g.z_dno) * TAN
    dv = g.w / 2 - g.depth * TAN + (z[w] - g.z_dno) * TAN
    return float(max(np.maximum(np.abs(u[w]) - du, 0).max(initial=0), np.maximum(np.abs(v[w]) - dv, 0).max(initial=0)))


def okragle_o_srednicy(uk, d):
    return next(g for g in uk.gniazda_okragle() if g.d_top == d)


# --- osadzanie w gnieździe (B1, B1b) ---------------------------------------------------
def test_osadzenie_nie_przenika_stozka_wiele_seedow():
    W, L, H, gz, amp = atrapy_koron.TYPY["przedtrzonowy"]
    m = atrapy_koron.korona(W, L, H, gz, amp, n_theta=96, n_u=120, rng=np.random.default_rng(11))
    m.apply_transform(synth.orientacja_brzegiem_do_gory(m) @ trimesh.transformations.scale_matrix(1.22))
    g = okragle_o_srednicy(U.wczytaj("poranna_r54"), 7.5)
    maks = 0.0
    for seed in range(20):
        T = synth.osadz_w_gniezdzie(m, g, np.random.default_rng(seed))
        if T is None:
            continue
        maks = max(maks, przenikanie_okr(trimesh.transform_points(m.vertices, T), g))
    assert maks <= 1e-6, maks


def test_osadzenie_bez_luzu_nie_przenika_stozka():
    W, L, H, gz, amp = atrapy_koron.TYPY["przedtrzonowy"]
    m = atrapy_koron.korona(W, L, H, gz, amp, n_theta=96, n_u=120, rng=np.random.default_rng(11))
    m.apply_transform(synth.orientacja_brzegiem_do_gory(m) @ trimesh.transformations.scale_matrix(1.22))
    g = okragle_o_srednicy(U.wczytaj("poranna_r54"), 7.5)
    for seed in range(20):
        T = synth.osadz_w_gniezdzie(m, g, np.random.default_rng(seed), luz_xy=0.0)
        assert T is not None
        assert przenikanie_okr(trimesh.transform_points(m.vertices, T), g) <= 1e-6


@pytest.mark.parametrize("nazwa", ["wieczorna", "poranna", "wieczorna_r54", "poranna_r54"])
def test_osadzenie_30_seedow_wszystkie_gniazda_4_typy(nazwa):
    """Siatka z sondy B1 (31.10): 30 seedów × wszystkie gniazda okrągłe × 4 typy atrap ×1,22 — 0 przenikań."""
    uk = U.wczytaj(nazwa)
    osadzen = 0
    for typ, (W, L, H, gz, amp) in atrapy_koron.TYPY.items():
        m = atrapy_koron.korona(W, L, H, gz, amp, n_theta=96, n_u=120, rng=np.random.default_rng(11))
        m.apply_transform(synth.orientacja_brzegiem_do_gory(m) @ trimesh.transformations.scale_matrix(1.22))
        for g in uk.gniazda_okragle():
            for seed in range(30):
                T = synth.osadz_w_gniezdzie(m, g, np.random.default_rng(seed))
                if T is None:
                    continue
                osadzen += 1
                V = trimesh.transform_points(m.vertices, T)
                assert przenikanie_okr(V, g) <= 1e-6 and V[:, 2].min() >= g.z_dno - 1e-6, (typ, g.id, seed)
    assert osadzen >= 30 * len(uk.gniazda_okragle()) * 3  # siekacz, kieł, przedtrzonowy wchodzą wszędzie


@pytest.mark.parametrize("nazwa", ["wieczorna", "poranna", "wieczorna_r54", "poranna_r54"])
def test_most_w_rynience_nie_przenika_scianek(nazwa):
    """B1b: prostopadłościan 6 mm szeroki, którego narożniki leżą poza dnem stadionu, ale w ściance — uniesiony, bez przenikania.

    Obrys rynienki to stadion (D4): narożnik leży w półokrągłym końcu; promień końca przy dnie
    jest mniejszy o depth·tan15°. Długość dobrana tak, by przy losowym obrocie ±1° (osadz_w_gniezdzie)
    uniesienie nie przekroczyło MAKS_UNIESIENIE.
    """
    for g in U.wczytaj(nazwa).rynienki():
        r_dno = g.w / 2 - g.depth * math.tan(math.radians(15))
        h, v = (g.l - g.w) / 2, 3.0
        u_min = math.sqrt(r_dno**2 - v**2)  # od tego narożnik wystaje poza dno
        u_max = math.sqrt((r_dno + 0.4) ** 2 - (v + math.radians(1) * (h + 5)) ** 2)  # przy 1° jeszcze ≤ 1,5 mm uniesienia
        assert u_min < u_max
        box = trimesh.creation.box([2 * (h + (u_min + u_max) / 2), 2 * v, 5.0])
        maks = 0.0
        for seed in range(10):
            T = synth.osadz_w_gniezdzie(box, g, np.random.default_rng(seed))
            assert T is not None
            V = trimesh.transform_points(box.vertices, T)
            maks = max(maks, przenikanie_ryn(V, g))
            u, v = V[:, 0] - g.x, V[:, 1] - g.y  # angle = 0
            poza_dnem = synth._stadion(u, v, g) + g.depth * TAN > 1e-9
            assert poza_dnem.any() and (V[poza_dnem, 2] > g.z_dno + 1e-6).all()  # narożniki poza dnem wiszą na ściance
        assert maks <= 1e-6, (g.id, maks)
        most = atrapy_koron.most(np.random.default_rng(1))
        for seed in range(10):
            T = synth.osadz_w_gniezdzie(most, g, np.random.default_rng(seed))
            if T is not None:
                assert przenikanie_ryn(trimesh.transform_points(most.vertices, T), g) <= 1e-6


def test_rynienka_obrocona_przesuniecie_w_ukladzie_rynienki():
    """Losowe przesunięcie w rynience obróconej o 90° jest liczone wzdłuż rynienki (dawniej: w x/y płytki)."""
    g = U.Gniazdo(id=99, typ="trough", x=0, y=0, depth=4, l=60, w=15, angle=90)
    box = trimesh.creation.box([20.0, 8.0, 5.0])
    for seed in range(10):
        T = synth.osadz_w_gniezdzie(box, g, np.random.default_rng(seed))
        assert przenikanie_ryn(trimesh.transform_points(box.vertices, T), g) <= 1e-6


def test_most_za_szeroki_na_poranna_rynienke_odrzucony():
    g = U.wczytaj("poranna_r54").rynienki()[0]  # w=13
    box = trimesh.creation.box([40.0, 12.8, 5.0])  # 12.8 > 13 - 0.4
    assert synth.osadz_w_gniezdzie(box, g, np.random.default_rng(0)) is None


def test_praca_za_szeroka_na_gniazdo_odrzucona():
    g = okragle_o_srednicy(U.wczytaj("wieczorna_r54"), 9)  # dno ø6.86
    walec = trimesh.creation.cylinder(radius=5.0, height=6.0)
    assert synth.osadz_w_gniezdzie(walec, g, np.random.default_rng(0)) is None


def test_praca_wisi_na_krawedzi_odrzucona():
    """Stożek odwrócony: spód wchodzi, ale uniesienie > MAKS_UNIESIENIE."""
    g = okragle_o_srednicy(U.wczytaj("wieczorna_r54"), 9)
    stozek = trimesh.creation.cone(radius=6.0, height=2.0)
    stozek.apply_transform(trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0]))
    assert synth.osadz_w_gniezdzie(stozek, g, np.random.default_rng(0)) is None


def test_przenikanie_wykrywa_wejscie_w_scianke():
    g = okragle_o_srednicy(U.wczytaj("wieczorna_r54"), 9)
    V = np.array([[g.x + 3.43 + 0.2, g.y, g.z_dno + 0.01], [g.x, g.y, g.z_dno - 0.05], [g.x + 20, g.y, g.z_top + 1]])
    assert synth.przenikanie(V, g) == pytest.approx(0.2, abs=0.01)


# --- ubytki (S1, S3) ------------------------------------------------------------------
@pytest.mark.parametrize("d", [0.0, -0.3, float("nan")])
def test_ubytek_o_zerowej_lub_ujemnej_srednicy_odrzucony_od_razu(korona_siekacz, d):
    with pytest.raises(ValueError, match="średnica ubytku"):
        synth.wytnij_ubytek(korona_siekacz, d, np.random.default_rng(0))


def test_ubytki_z_zakresu_inspect_i_flaga_wykrywalny(korony):
    """S1: średnice i pas brzegu z [inspect]; ubytek płytszy niż prog_glebokosci_mm ma wykrywalny=False."""
    ins = UST.domyslne()["inspect"]
    op = synth.Opcje()
    assert op.srednica_ubytku == (ins["srednica_min_mm"], ins["srednica_max_mm"]) and op.pas_brzegu == ins["pas_brzegu_mm"]
    uk = U.wczytaj("wieczorna")
    op = synth.Opcje(ubytki_na_prace=(3, 3), srednica_ubytku=(0.2, 0.3))
    _, prawda = synth.generuj_plytke(uk, 1, korony, np.random.default_rng(2), op, seed=2)
    ubytki = [u for p in prawda.prace for u in p.ubytki]
    assert len(ubytki) == 9
    for u in ubytki:
        assert u.wykrywalny == (u.glebokosc >= ins["prog_glebokosci_mm"])
    assert {u.wykrywalny for u in ubytki} == {True, False}  # ø0,2–0,228 za płytkie (0,7·r < 0,08)
    assert not synth.Opcje().wykrywalny(ins["srednica_max_mm"] + 0.1, 1.0)  # poza zakresem średnic


def test_ubytek_w_pasie_brzegu_z_ustawien(korona_siekacz):
    m = korona_siekacz
    m.apply_transform(synth.orientacja_brzegiem_do_gory(m))
    pas = UST.domyslne()["inspect"]["pas_brzegu_mm"]
    for s in range(10):
        _, ub = synth.wytnij_ubytek(m, 0.4, np.random.default_rng(s))
        assert ub.z > m.bounds[1, 2] - pas - 1e-9


# --- szum (S4) ------------------------------------------------------------------------
@pytest.mark.parametrize("sigma", [float("nan"), -0.5, float("inf")])
def test_szum_nan_lub_ujemny_odrzucony(korona_siekacz, sigma):
    with pytest.raises(ValueError, match="sigma"):
        synth.dodaj_szum(korona_siekacz, sigma, np.random.default_rng(0))


def test_szum_zero_zwraca_te_sama_siatke(korona_siekacz):
    assert synth.dodaj_szum(korona_siekacz, 0.0, np.random.default_rng(0)) is korona_siekacz


# --- Opcje (S3, S4, S7) ---------------------------------------------------------------------
@pytest.mark.parametrize("pole,wartosc", [
    ("ubytki_na_prace", (2, 0)), ("ubytki_na_prace", (-1, 2)), ("srednica_ubytku", (0.0, 0.5)),
    ("srednica_ubytku", (0.6, 0.2)), ("szum_sigma", -0.1), ("szum_sigma", float("nan")),
    ("wspolczynnik", (1.25, 1.2)), ("p_drgniecia", 1.5), ("prace_na_plytce", -1),
])
def test_opcje_odrzucaja_zle_wartosci(pole, wartosc):
    with pytest.raises(ValueError, match=pole):
        synth.Opcje(**{pole: wartosc})


def test_opcje_z_toml_poranna_i_nadpisania():
    s = UST.domyslne()["synth"]
    assert synth.Opcje.z_toml(plytka="wieczorna").wspolczynnik == (s["wspolczynnik_min"], s["wspolczynnik_max"])
    assert synth.Opcje.z_toml(plytka="poranna").wspolczynnik == synth.WSPOLCZYNNIK_PORANNA
    op = synth.Opcje.z_toml(szum_sigma=0.01, prace_na_plytce=None)
    assert op.szum_sigma == 0.01 and op.prace_na_plytce is None


# --- generuj_plytke: wejścia skrajne (S2) ------------------------------------------------
def test_pusty_stl_w_projektach_jest_pomijany(korony, tmp_path):
    zly = zapisz_ascii_stl(tmp_path / "pusty.stl", [])
    uk = U.wczytaj("wieczorna")
    with pytest.warns(UserWarning, match="pomijam projekt pusty.stl"):
        _, prawda = synth.generuj_plytke(uk, 1, [zly] + korony, np.random.default_rng(0), synth.Opcje(prace_na_plytce=4), seed=0)
    assert len(prawda.prace) == 3 and synth.skrot_pliku(zly) not in {p.projekt for p in prawda.prace}


def test_stl_z_nan_jest_pomijany(korony, tmp_path):
    m = trimesh.load(korony[0])
    V = m.vertices.copy()
    V[0] = np.nan
    zly = tmp_path / "nan.stl"
    trimesh.Trimesh(V, m.faces, process=False).export(zly)
    uk = U.wczytaj("wieczorna")
    with pytest.warns(UserWarning, match="pomijam projekt nan.stl"):
        skan, prawda = synth.generuj_plytke(uk, 1, [zly], np.random.default_rng(0), synth.Opcje(), seed=0)
    assert np.isfinite(skan.vertices).all() and prawda.prace == []


# --- prawda: transformacje, determinizm, P1 -------------------------------------------------
def test_transformacje_z_prawdy_sa_sztywne_i_nakladaja_kazda_prace(korony):
    uk = U.wczytaj("wieczorna")
    op = synth.Opcje(ubytki_na_prace=(1, 2), prace_na_plytce=3)
    skan, prawda = synth.generuj_plytke(uk, 2, korony, np.random.default_rng(9), op, seed=9)
    assert len(prawda.prace) == 3
    pas = op.pas_brzegu
    for p in prawda.prace:
        T = np.array(p.transformacja)
        assert T.shape == (4, 4) and np.allclose(T[3], [0, 0, 0, 1])
        R = T[:3, :3]
        assert np.linalg.det(R) == pytest.approx(1.0, abs=1e-9) and np.allclose(R @ R.T, np.eye(3), atol=1e-9)
        assert op.wspolczynnik[0] <= p.wspolczynnik <= op.wspolczynnik[1]
        m = trimesh.load(next(q for q in korony if synth.skrot_pliku(q) == p.projekt))
        V = trimesh.transform_points(m.vertices, T @ trimesh.transformations.scale_matrix(p.wspolczynnik))
        g = uk.gniazdo(p.gniazdo)
        assert g.zawiera(V[:, 0].mean(), V[:, 1].mean(), margines=1.0)
        assert V[:, 2].min() >= g.z_dno - 1e-6
        # P4: z nowym generatorem ubytków ten seed kładzie jedną z prac w rynience (inne losowanie po pierwszym ubytku)
        assert (przenikanie_okr(V, g) if g.okragle else przenikanie_ryn(V, g)) <= 1e-6
        # ubytki leżą w pasie brzegu pracy ([inspect] pas_brzegu_mm) i na powierzchni pracy (albo na czaszy
        # poprzedniego ubytku tej pracy, czyli najwyżej o jego głębokość pod powierzchnią)
        powierzchnia = trimesh.Trimesh(V, m.faces, process=False)
        for u in p.ubytki:
            # P4: pas brzegu liczy się od linii krawędzi brzegu (odległość 3D), nie od najwyższego punktu pracy w gnieździe
            assert u.odleglosc_od_linii is not None and u.odleglosc_od_linii <= pas + 1e-6
            assert V[:, 2].max() - pas - 1.0 <= u.z <= V[:, 2].max() + 0.05  # przechył pracy ≤ 4° obniża brzeg najwyżej o ~0,9 mm
            _, odl, _ = trimesh.proximity.closest_point(powierzchnia, [[u.x, u.y, u.z]])
            assert odl[0] < max(x.glebokosc for x in p.ubytki) + 0.01


def test_determinizm_tego_samego_seeda(korony):
    uk = U.wczytaj("wieczorna")
    op = synth.Opcje(ubytki_na_prace=(1, 2), prace_na_plytce=3, p_drgniecia=0.5)
    a = synth.generuj_plytke(uk, 1, korony, np.random.default_rng(4), op, seed=4)
    b = synth.generuj_plytke(uk, 1, korony, np.random.default_rng(4), op, seed=4)
    assert dataclasses.asdict(a[1]) == dataclasses.asdict(b[1])
    assert a[0].vertices.shape == b[0].vertices.shape and np.array_equal(a[0].vertices, b[0].vertices)
    c = synth.generuj_plytke(uk, 1, korony, np.random.default_rng(5), op, seed=5)
    assert dataclasses.asdict(c[1]) != dataclasses.asdict(a[1])


def test_prawda_nie_zawiera_nazwy_pliku_projektu(korony, tmp_path):
    m = trimesh.load(korony[0])
    p = tmp_path / "Kowalski_Jan_12345_korona_16.stl"
    m.export(p)
    uk = U.wczytaj("wieczorna")
    skan, prawda = synth.generuj_plytke(uk, 1, [p], np.random.default_rng(0), synth.Opcje(), seed=0)
    _, p_json = synth.zapisz(skan, prawda, tmp_path / "w", "t")
    tekst = p_json.read_text(encoding="utf-8")
    assert "Kowalski" not in tekst
    assert json.loads(tekst)["prace"][0]["projekt"] == synth.skrot_pliku(p)
    assert len(synth.skrot_pliku(p)) == 16


# --- zapis (S9) -------------------------------------------------------------------------------
def test_zapis_nie_nadpisuje_istniejacego(korony, tmp_path):
    uk = U.wczytaj("wieczorna")
    skan, prawda = synth.generuj_plytke(uk, 1, korony, np.random.default_rng(0), synth.Opcje(prace_na_plytce=1), seed=0)
    synth.zapisz(skan, prawda, tmp_path, "t")
    (tmp_path / "t.json").write_text("{}", encoding="utf-8")
    with pytest.raises(FileExistsError):
        synth.zapisz(skan, prawda, tmp_path, "t")
    assert (tmp_path / "t.json").read_text(encoding="utf-8") == "{}"
    synth.zapisz(skan, prawda, tmp_path, "t", nadpisz=True)
    assert synth.wczytaj_prawde(tmp_path / "t.json").numer == 1


# --- CLI (S4, S7, S9, B3, P1) --------------------------------------------------------------
def uruchom_main(monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["synth", *map(str, args)])
    synth.main()


@pytest.mark.parametrize("ub", ["2", "0--2", "a-b", "2-0"])
def test_cli_zakres_ubytkow_zle_sformatowany(korony, tmp_path, monkeypatch, capsys, ub):
    with pytest.raises(SystemExit):
        uruchom_main(monkeypatch, "--projekty", korony[0].parent, "--ubytki", ub, "--wyjscie", tmp_path / "w")
    assert "--ubytki" in capsys.readouterr().err


@pytest.mark.parametrize("arg", [("--szum", "-1"), ("--srednica", "0-0.6"), ("--drgniecie", "2"), ("--ile", "-1")])
def test_cli_zle_wartosci_odrzucone_przez_argparse(korony, tmp_path, monkeypatch, arg):
    with pytest.raises(SystemExit):
        uruchom_main(monkeypatch, "--projekty", korony[0].parent, *arg, "--wyjscie", tmp_path / "w")
    assert not (tmp_path / "w").exists()


def test_cli_nie_nadpisuje_bez_flagi_i_pisze_mape(korony, tmp_path, monkeypatch):
    wy = tmp_path / "dane" / "syntetyczne"
    args = ("--projekty", korony[0].parent, "--prace", 1, "--ubytki", "0-0", "--wyjscie", wy)
    uruchom_main(monkeypatch, *args)
    with pytest.raises(SystemExit, match="--nadpisz"):
        uruchom_main(monkeypatch, *args)
    uruchom_main(monkeypatch, *args, "--nadpisz")
    mapa = json.loads((tmp_path / "dane" / "mapa_projektow.json").read_text(encoding="utf-8"))
    assert mapa == {synth.skrot_pliku(k): k.name for k in korony}
    assert len(list(wy.iterdir())) == 2  # tylko skan_*.stl/.json: mapa nie leży obok skanów


def test_cli_domyslne_z_ustawien_i_wlasny_plik(korony, tmp_path, monkeypatch):
    """B3: argparse default=None → wartości z toml; --ustawienia wskazuje inny plik."""
    tekst = UST.PLIK_USTAWIEN.read_text(encoding="utf-8").replace("szum_sigma_mm = 0.03", "szum_sigma_mm = 0.011")
    assert "0.011" in tekst
    plik = tmp_path / "moje.toml"
    plik.write_text(tekst, encoding="utf-8")
    uruchom_main(monkeypatch, "--ustawienia", plik, "--projekty", korony[0].parent, "--prace", 1, "--ubytki", "0-0", "--wyjscie", tmp_path / "w")
    pr = synth.wczytaj_prawde(next((tmp_path / "w").glob("*.json")))
    assert pr.szum_sigma == 0.011
    uruchom_main(monkeypatch, "--projekty", korony[0].parent, "--prace", 1, "--ubytki", "0-0", "--wyjscie", tmp_path / "w2")
    assert synth.wczytaj_prawde(next((tmp_path / "w2").glob("*.json"))).szum_sigma == UST.domyslne()["synth"]["szum_sigma_mm"]


# --- P4 (15.11.2026): ukruszenia celowe na krawędzi (K6), wersja generatora ---------------------------------
def test_opcje_k6_domyslne_z_ustawien_i_walidacja():
    s = UST.domyslne()["synth"]
    op = synth.Opcje()
    assert op.wersja_ubytkow == 2 and op.krawedz_na_prace == (0, 0) and op.krawedz_rozmiary is None
    assert op.krawedz_rozmiar == (s["krawedz_rozmiar_min_mm"], s["krawedz_rozmiar_max_mm"]) and op.odstep_ubytku == s["odstep_ubytku_mm"]
    assert synth.Opcje.z_toml(krawedz_rozmiar=(0.1, 0.2), odstep_ubytku=0.04).krawedz_rozmiar == (0.1, 0.2)
    for pole, wartosc in [("krawedz_na_prace", (2, 1)), ("krawedz_rozmiar", (0.0, 0.2)), ("krawedz_rozmiary", ()), ("krawedz_rozmiary", (0.1, -0.2)),
                          ("krawedz_polozenia", ("zewn", "obok")), ("krawedz_polozenia", ()), ("odstep_ubytku", 0.0)]:
        with pytest.raises(ValueError, match=pole):
            synth.Opcje(**{pole: wartosc})
    assert synth.Opcje(krawedz_polozenia="sciana").krawedz_polozenia == ("sciana",)


def test_cli_ukruszenia_krawedzi(korony, tmp_path, monkeypatch, capsys):
    """K6 z wiersza poleceń: lista rozmiarów i położeń trafia do prawdy; bez --krawedz prawda nie ma ubytków celowych."""
    wy = tmp_path / "k6"
    uruchom_main(monkeypatch, "--projekty", korony[0].parent, "--plytka", "okragla_wieczorna", "--prace", 2, "--ubytki", "0-0", "--wspolczynnik", 1.22,
                 "--krawedz", "2-2", "--krawedz-rozmiary", "0.10,0.25", "--krawedz-polozenie", "zewn,wewn", "--seed", 5, "--wyjscie", wy)
    assert "celowych na krawędzi 4" in capsys.readouterr().out
    pr = synth.wczytaj_prawde(next(wy.glob("*.json")))
    ubytki = [u for p in pr.prace for u in p.ubytki]
    assert len(ubytki) == 4 and all(u.celowy and u.polozenie in ("krawedz_zewn", "krawedz_wewn") for u in ubytki)
    assert {round(u.srednica, 6) for u in ubytki} <= {0.2, 0.5} and all(0 < u.glebokosc_rzeczywista < u.glebokosc for u in ubytki)
    op = synth.Opcje()
    assert [u.wykrywalny for u in ubytki] == [op.wykrywalny(u.srednica, u.glebokosc) for u in ubytki]
    uruchom_main(monkeypatch, "--projekty", korony[0].parent, "--prace", 1, "--ubytki", "1-1", "--wyjscie", tmp_path / "bez")
    pr = synth.wczytaj_prawde(next((tmp_path / "bez").glob("*.json")))
    assert all(not u.celowy and u.polozenie for p in pr.prace for u in p.ubytki) and sum(len(p.ubytki) for p in pr.prace) == 1


@pytest.mark.parametrize("arg", [("--krawedz", "2"), ("--krawedz-polozenie", "zewn,obok"), ("--krawedz-rozmiary", "0.1,x"), ("--krawedz-rozmiar", "0-0.2"),
                                 ("--wersja-ubytkow", "3"), ("--odstep-ubytku", "0")])
def test_cli_k6_zle_wartosci_odrzucone(korony, tmp_path, monkeypatch, arg):
    with pytest.raises(SystemExit):
        uruchom_main(monkeypatch, "--projekty", korony[0].parent, *arg, "--wyjscie", tmp_path / "w")
    assert not (tmp_path / "w").exists()


def test_cli_wersja_1_nie_laczy_sie_z_k6_i_pamiec_linii(korony, tmp_path, monkeypatch):
    from stanowisko import krawedz

    with pytest.raises(SystemExit):
        uruchom_main(monkeypatch, "--projekty", korony[0].parent, "--wersja-ubytkow", 1, "--krawedz", "1-1", "--wyjscie", tmp_path / "w")
    assert not (tmp_path / "w").exists()
    uruchom_main(monkeypatch, "--projekty", korony[0].parent, "--prace", 1, "--ubytki", "0-0", "--krawedz", "1-1", "--pamiec-linii", tmp_path / "linie",
                 "--wyjscie", tmp_path / "w")
    assert len(list((tmp_path / "linie").glob("*.npz"))) >= 1 and krawedz._KATALOG is None  # po zakończeniu pamięć na dysku wyłączona
    krawedz.wyczysc_pamiec()
