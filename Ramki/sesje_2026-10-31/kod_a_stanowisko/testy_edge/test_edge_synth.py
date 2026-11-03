"""Edge-case'y modułu stanowisko/synth.py. Identyfikatory znalezisk: znaleziska.md."""
import dataclasses
import json
import math
import sys

import numpy as np
import pytest
import trimesh

from conftest import U, atrapy_koron, synth, zapisz_ascii_stl

TAN = synth.TAN_SCIANKI


def przenikanie_okr(V, g):
    rho = np.hypot(V[:, 0] - g.x, V[:, 1] - g.y)
    z = V[:, 2]
    w = z < U.Z_TOP
    dop = g.promien_dolny() + (z[w] - g.z_dno) * TAN
    return float(np.maximum(rho[w] - dop, 0).max(initial=0.0))


def przenikanie_ryn(V, g):
    a = math.radians(g.angle)
    dx, dy = V[:, 0] - g.x, V[:, 1] - g.y
    u = dx * math.cos(a) + dy * math.sin(a)
    v = -dx * math.sin(a) + dy * math.cos(a)
    z = V[:, 2]
    w = z < U.Z_TOP
    du = g.l / 2 - g.depth * TAN + (z[w] - g.z_dno) * TAN
    dv = g.w / 2 - g.depth * TAN + (z[w] - g.z_dno) * TAN
    return float(max(np.maximum(np.abs(u[w]) - du, 0).max(initial=0), np.maximum(np.abs(v[w]) - dv, 0).max(initial=0)))


# --- osadzanie w gnieździe ---------------------------------------------------
@pytest.mark.xfail(reason="ZNALEZISKO B1: losowe dx,dy (luz_xy) dodawane PO obliczeniu uniesienia — praca przenika stożek (poranna ø7,5, przedtrzonowy ×1,22: do 0,73 mm)", strict=True)
def test_osadzenie_nie_przenika_stozka_wiele_seedow():
    W, L, H, gz, amp = atrapy_koron.TYPY["przedtrzonowy"]
    m = atrapy_koron.korona(W, L, H, gz, amp, n_theta=96, n_u=120, rng=np.random.default_rng(11))
    m.apply_transform(synth.orientacja_brzegiem_do_gory(m) @ trimesh.transformations.scale_matrix(1.22))
    g = U.wczytaj("poranna").gniazdo(1)  # ø7.5
    maks = 0.0
    for seed in range(20):
        T = synth.osadz_w_gniezdzie(m, g, np.random.default_rng(seed))
        if T is None:
            continue
        maks = max(maks, przenikanie_okr(trimesh.transform_points(m.vertices, T), g))
    assert maks <= 0.01, maks


def test_osadzenie_bez_luzu_nie_przenika_stozka():
    """Kontrola przyczyny B1: z luz_xy=0 przenikanie = 0 → pętla uniesienia jest poprawna, winne jest przesunięcie."""
    W, L, H, gz, amp = atrapy_koron.TYPY["przedtrzonowy"]
    m = atrapy_koron.korona(W, L, H, gz, amp, n_theta=96, n_u=120, rng=np.random.default_rng(11))
    m.apply_transform(synth.orientacja_brzegiem_do_gory(m) @ trimesh.transformations.scale_matrix(1.22))
    g = U.wczytaj("poranna").gniazdo(1)
    for seed in range(20):
        T = synth.osadz_w_gniezdzie(m, g, np.random.default_rng(seed), luz_xy=0.0)
        assert T is not None
        assert przenikanie_okr(trimesh.transform_points(m.vertices, T), g) <= 1e-6


@pytest.mark.xfail(reason="ZNALEZISKO B1b: rynienka — brak sprawdzenia ścianek 15°; prostopadłościan 58,5 mm przechodzi warunek l-1=59, a dno ma 57,86 mm", strict=True)
def test_most_w_rynience_nie_przenika_scianek():
    g = U.wczytaj("wieczorna").gniazdo(25)  # l=60, w=15
    box = trimesh.creation.box([58.5, 10.0, 5.0])
    maks = 0.0
    for seed in range(10):
        T = synth.osadz_w_gniezdzie(box, g, np.random.default_rng(seed))
        assert T is not None
        maks = max(maks, przenikanie_ryn(trimesh.transform_points(box.vertices, T), g))
    assert maks <= 0.01, maks


def test_most_za_szeroki_na_poranna_rynienke_odrzucony():
    g = U.wczytaj("poranna").gniazdo(36)  # w=13
    box = trimesh.creation.box([40.0, 12.8, 5.0])  # 12.8 > 13 - 0.4
    assert synth.osadz_w_gniezdzie(box, g, np.random.default_rng(0)) is None


def test_praca_za_szeroka_na_gniazdo_odrzucona():
    g = U.wczytaj("wieczorna").gniazdo(1)  # ø9, dno ø6.86
    walec = trimesh.creation.cylinder(radius=5.0, height=6.0)  # ø10 > ø9 i płaski spód
    assert synth.osadz_w_gniezdzie(walec, g, np.random.default_rng(0)) is None


def test_praca_wisi_na_krawedzi_odrzucona():
    """Stożek odwrócony: spód ø2 wchodzi, ale uniesienie > MAKS_UNIESIENIE."""
    g = U.wczytaj("wieczorna").gniazdo(1)
    stozek = trimesh.creation.cone(radius=6.0, height=2.0)  # płaski stożek, ostrze w górze → odwracamy ostrzem w dół
    stozek.apply_transform(trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0]))
    assert synth.osadz_w_gniezdzie(stozek, g, np.random.default_rng(0)) is None


# --- ubytki ---------------------------------------------------------------------
def test_ubytek_o_ujemnej_srednicy_wybucha_przypadkowo(korona_siekacz):
    """ZNALEZISKO S3 (obserwowane): r<0 → po ~2 s ValueError 'max_iter exceeded!' z trimesh, nie z walidacji."""
    with pytest.raises(ValueError, match="max_iter"):
        synth.wytnij_ubytek(korona_siekacz, -0.3, np.random.default_rng(0))


@pytest.mark.xfail(reason="ZNALEZISKO S3: średnica 0 → max_edge=min(0.05, r/3)=0 → subdivide_to_size mieli 10 iteracji (~230 s, miliony trójkątów) zamiast natychmiast odrzucić", strict=True)
def test_ubytek_o_zerowej_srednicy_konczy_sie_szybko(korony):
    import subprocess

    kod = (
        "import sys, numpy as np, trimesh; sys.path.insert(0, %r); from stanowisko import synth; "
        "m = trimesh.load(%r); synth.wytnij_ubytek(m, 0.0, np.random.default_rng(0))"
    ) % (str(synth.__file__).rsplit("stanowisko", 1)[0], str(korony[0]))
    try:
        subprocess.run([sys.executable, "-c", kod], timeout=20, capture_output=True)
    except subprocess.TimeoutExpired:
        pytest.fail("wytnij_ubytek(srednica=0) nie skończył się w 20 s")


def test_ubytek_pas_brzegu_wiekszy_niz_praca(korona_siekacz):
    m = korona_siekacz
    m.apply_transform(synth.orientacja_brzegiem_do_gory(m))
    po, ub = synth.wytnij_ubytek(m, 0.4, np.random.default_rng(0), pas_brzegu=1000.0)
    assert len(po.faces) > 0 and np.isfinite(po.vertices).all()
    assert ub.glebokosc == pytest.approx(0.14)


def test_ubytek_na_siatce_bez_pasa_brzegu_bierze_dowolny_wierzcholek():
    """Siatka całkowicie poniżej z_max - 2 nie istnieje; sprawdzamy gałąź kand=all dla płaskiej płytki 0 mm wysokości."""
    m = trimesh.creation.box([10, 10, 0.001])
    po, ub = synth.wytnij_ubytek(m, 0.4, np.random.default_rng(0), pas_brzegu=-1.0)
    assert np.isfinite(po.vertices).all()


def test_ubytek_w_pasie_2mm_ale_inspect_szuka_w_1_5mm(korony):
    """ZNALEZISKO S1 (dokumentacja): synth wycina w górnych 2,0 mm, inspect ma pas_brzegu_mm = 1,5 w toml."""
    import tomllib

    toml = tomllib.load(open(synth.__file__.replace("stanowisko\\synth.py", "ustawienia.toml").replace("stanowisko/synth.py", "ustawienia.toml"), "rb"))
    assert toml["inspect"]["pas_brzegu_mm"] == 1.5
    assert synth.wytnij_ubytek.__defaults__[0] == 2.0  # pas_brzegu
    # i najmniejszy ubytek (ø0,2 → głębokość 0,07) jest płytszy niż próg 0,08
    assert 0.7 * (synth.Opcje().srednica_ubytku[0] / 2) < toml["inspect"]["prog_glebokosci_mm"]


# --- szum i drgnięcie ----------------------------------------------------------
def test_szum_ujemny_jest_cicho_ignorowany(korona_siekacz):
    """ZNALEZISKO S4 (obserwowane): sigma<0 zwraca siatkę bez zmian zamiast błędu; CLI --szum -1 przechodzi."""
    s = synth.dodaj_szum(korona_siekacz, -0.5, np.random.default_rng(0))
    assert s is korona_siekacz


@pytest.mark.xfail(reason="ZNALEZISKO S4: sigma=NaN przechodzi warunek 'sigma <= 0' i daje siatkę pełną NaN", strict=True)
def test_szum_nan_odrzucony(korona_siekacz):
    with pytest.raises(ValueError):
        synth.dodaj_szum(korona_siekacz, float("nan"), np.random.default_rng(0))


def test_szum_zero_zwraca_te_sama_siatke(korona_siekacz):
    assert synth.dodaj_szum(korona_siekacz, 0.0, np.random.default_rng(0)) is korona_siekacz


def test_drgniecie_dodaje_druga_powierzchnie(korona_siekacz):
    d = synth.drgniecie(korona_siekacz, np.random.default_rng(0))
    assert len(korona_siekacz.faces) < len(d.faces) <= 2 * len(korona_siekacz.faces)


@pytest.mark.xfail(reason="ZNALEZISKO S5: prawda zapisuje tylko flagę drgniecie=True; wektor/wielkość przesunięcia (0,08–0,15 mm) nie trafia do JSON", strict=True)
def test_prawda_drgniecia_ma_wektor(korony):
    uk = U.wczytaj("wieczorna")
    op = synth.Opcje(ubytki_na_prace=(0, 0), prace_na_plytce=1, p_drgniecia=1.0)
    _, prawda = synth.generuj_plytke(uk, 1, korony, np.random.default_rng(1), op, seed=1)
    p = prawda.prace[0]
    assert p.drgniecie
    assert any(k in dataclasses.asdict(p) for k in ("drgniecie_wektor", "drgniecie_mm", "przesuniecie"))


# --- generuj_plytke: wejścia skrajne ---------------------------------------------
def test_brak_projektow_daje_pusta_plytke():
    uk = U.wczytaj("wieczorna")
    skan, prawda = synth.generuj_plytke(uk, 1, [], np.random.default_rng(0), synth.Opcje(), seed=0)
    assert prawda.prace == [] and sorted(prawda.gniazda_puste) == sorted(g.id for g in uk.sockets)
    assert len(skan.faces) > 0  # sama płytka


def test_prace_na_plytce_zero(korony):
    uk = U.wczytaj("wieczorna")
    _, prawda = synth.generuj_plytke(uk, 1, korony, np.random.default_rng(0), synth.Opcje(prace_na_plytce=0), seed=0)
    assert prawda.prace == []


def test_prace_wiecej_niz_projektow_cicho_ograniczone(korony):
    """ZNALEZISKO S6 (obserwowane): każdy projekt użyty raz; prace_na_plytce=30 daje len(korony)=3 prac bez ostrzeżenia."""
    uk = U.wczytaj("wieczorna")
    _, prawda = synth.generuj_plytke(uk, 1, korony, np.random.default_rng(0), synth.Opcje(prace_na_plytce=30), seed=0)
    assert len(prawda.prace) == 3


def test_zakres_ubytkow_odwrocony_wybucha(korony):
    """ZNALEZISKO S7 (obserwowane): ubytki_na_prace=(2, 0) → ValueError z numpy (high < low) bez własnego komunikatu."""
    uk = U.wczytaj("wieczorna")
    with pytest.raises(ValueError):
        synth.generuj_plytke(uk, 1, korony, np.random.default_rng(0), synth.Opcje(ubytki_na_prace=(2, 0), prace_na_plytce=1), seed=0)


def test_numer_plytki_bez_stl_wybucha_czytelnie(korony):
    uk = U.wczytaj("wieczorna")
    with pytest.raises(FileNotFoundError, match="plytka_n7"):
        synth.generuj_plytke(uk, 7, korony, np.random.default_rng(0), synth.Opcje(), seed=0)


@pytest.mark.xfail(reason="ZNALEZISKO S2: jeden zepsuty STL (0 trójkątów) w folderze projektów przerywa generowanie całej płytki (AttributeError na m.bounds=None)", strict=True)
def test_pusty_stl_w_projektach_jest_pomijany(korony, tmp_path):
    zly = zapisz_ascii_stl(tmp_path / "pusty.stl", [])
    uk = U.wczytaj("wieczorna")
    _, prawda = synth.generuj_plytke(uk, 1, [zly] + korony, np.random.default_rng(0), synth.Opcje(prace_na_plytce=4), seed=0)
    assert len(prawda.prace) == 3 and all(p.projekt != "pusty.stl" for p in prawda.prace)


@pytest.mark.xfail(reason="ZNALEZISKO S2: STL z NaN w wierzchołkach przechodzi bez walidacji — skan/prawda mogą zawierać NaN albo praca nie jest w gnieździe", strict=True)
def test_stl_z_nan_jest_pomijany(korony, tmp_path):
    m = trimesh.load(korony[0])
    V = m.vertices.copy()
    V[0] = np.nan
    zly = tmp_path / "nan.stl"
    trimesh.Trimesh(V, m.faces, process=False).export(zly)
    uk = U.wczytaj("wieczorna")
    skan, prawda = synth.generuj_plytke(uk, 1, [zly], np.random.default_rng(0), synth.Opcje(), seed=0)
    assert np.isfinite(skan.vertices).all()
    assert all(p.projekt != "nan.stl" for p in prawda.prace)


def test_stl_ze_zduplikowanymi_trojkatami_przechodzi(korony, tmp_path):
    m = trimesh.load(korony[0])
    dup = tmp_path / "dup.stl"
    trimesh.Trimesh(m.vertices, np.concatenate([m.faces, m.faces[:200]]), process=False).export(dup)
    uk = U.wczytaj("wieczorna")
    skan, prawda = synth.generuj_plytke(uk, 1, [dup], np.random.default_rng(0), synth.Opcje(ubytki_na_prace=(1, 1)), seed=0)
    assert len(prawda.prace) == 1 and np.isfinite(skan.vertices).all()


def test_most_trafia_do_rynienki_i_mosty_false_go_pomija(tmp_path):
    most = atrapy_koron.most(np.random.default_rng(1))
    p = tmp_path / "most.stl"
    most.export(p)
    uk = U.wczytaj("wieczorna")
    _, prawda = synth.generuj_plytke(uk, 1, [p], np.random.default_rng(0), synth.Opcje(ubytki_na_prace=(0, 0)), seed=0)
    assert len(prawda.prace) == 1 and not uk.gniazdo(prawda.prace[0].gniazdo).okragle
    _, prawda2 = synth.generuj_plytke(uk, 1, [p], np.random.default_rng(0), synth.Opcje(mosty=False), seed=0)
    assert prawda2.prace == []


# --- prawda: transformacje, układ współrzędnych, determinizm ---------------------
def test_transformacje_z_prawdy_sa_sztywne_i_nakladaja_kazda_prace(korony):
    uk = U.wczytaj("wieczorna")
    op = synth.Opcje(ubytki_na_prace=(1, 2), prace_na_plytce=3)
    skan, prawda = synth.generuj_plytke(uk, 2, korony, np.random.default_rng(9), op, seed=9)
    assert len(prawda.prace) == 3
    for p in prawda.prace:
        T = np.array(p.transformacja)
        assert T.shape == (4, 4) and np.allclose(T[3], [0, 0, 0, 1])
        R = T[:3, :3]
        assert np.linalg.det(R) == pytest.approx(1.0, abs=1e-9) and np.allclose(R @ R.T, np.eye(3), atol=1e-9)
        assert 1.20 <= p.wspolczynnik <= 1.25
        m = trimesh.load(next(q for q in korony if q.name == p.projekt))
        V = trimesh.transform_points(m.vertices, T @ trimesh.transformations.scale_matrix(p.wspolczynnik))
        g = uk.gniazdo(p.gniazdo)
        assert g.zawiera(V[:, 0].mean(), V[:, 1].mean(), margines=1.0)
        assert V[:, 2].min() >= g.z_dno - 1e-6
        # ubytki leżą w pasie brzegu pracy (górne 2 mm) i wewnątrz obrysu pracy
        for u in p.ubytki:
            assert V[:, 2].max() - 2.0 - 0.05 <= u.z <= V[:, 2].max() + 0.05
            assert np.linalg.norm(V - [u.x, u.y, u.z], axis=1).min() < 0.1


def test_uklad_wspolrzednych_skanu(korony):
    """Góra płytki z=8 (bez reliefu numeru 8,6), spód usunięty (z>0,5), prace nie poniżej dna gniazda z=4."""
    uk = U.wczytaj("wieczorna")
    plytka = synth.siatka_plytki(uk, 1, 0.0, np.random.default_rng(0))
    V = plytka.vertices[plytka.faces].reshape(-1, 3)
    assert plytka.triangles_center[:, 2].min() > 0.5
    plaskie = V[(np.abs(V[:, 0]) < 20) & (V[:, 1] > 44) & (V[:, 1] < 47)]  # pas wierzchu bez gniazd
    assert np.allclose(plaskie[:, 2], 8.0, atol=1e-6)
    assert V[:, 2].max() == pytest.approx(8.6, abs=1e-3)  # relief numeru
    assert plytka.triangles_center[:, 2].min() > 0.5
    skan, prawda = synth.generuj_plytke(uk, 1, korony, np.random.default_rng(0), synth.Opcje(ubytki_na_prace=(0, 0)), seed=0)
    assert prawda.z_top == 8.0
    # ściany boczne płytki sięgają z=0 (trójkąty o środku > 0,5 mają wierzchołki na spodzie) — to nie błąd
    assert skan.vertices[:, 2].min() >= -1e-6 and skan.triangles_center[:, 2].min() > 0.5
    for p in prawda.prace:
        assert uk.gniazdo(p.gniazdo).z_dno == 4.0


def test_siatka_plytki_bez_szumu_lezy_na_oryginale():
    """Zagęszczenie (subdivide_to_size) nie przesuwa powierzchni."""
    uk = U.wczytaj("wieczorna")
    org = trimesh.load(uk.plik_stl(1), force="mesh")
    p = synth.siatka_plytki(uk, 1, 0.0, np.random.default_rng(0))
    c = p.triangles_center
    c = c[np.random.default_rng(0).choice(len(c), 3000, replace=False)]
    _, d, _ = trimesh.proximity.closest_point(org, c)
    assert d.max() < 1e-6
    assert len(p.faces) > len(org.faces)


@pytest.mark.xfail(reason="ZNALEZISKO S8: komentarz 'kieszenie magnesów usuwamy', ale filtr z>0,5 zostawia ścianki kieszeni (z 0,5…2,2) w narożnikach", strict=True)
def test_siatka_plytki_bez_kieszeni_magnesow():
    uk = U.wczytaj("wieczorna")
    p = synth.siatka_plytki(uk, 1, 0.0, np.random.default_rng(0))
    c = p.triangles_center
    kieszen = (np.hypot(c[:, 0] + 42, c[:, 1] + 42) < 2.7) & (c[:, 2] < 2.3)
    assert not kieszen.any()


def test_determinizm_tego_samego_seeda(korony):
    uk = U.wczytaj("wieczorna")
    op = synth.Opcje(ubytki_na_prace=(1, 2), prace_na_plytce=3, p_drgniecia=0.5)
    a = synth.generuj_plytke(uk, 1, korony, np.random.default_rng(4), op, seed=4)
    b = synth.generuj_plytke(uk, 1, korony, np.random.default_rng(4), op, seed=4)
    assert dataclasses.asdict(a[1]) == dataclasses.asdict(b[1])
    assert a[0].vertices.shape == b[0].vertices.shape and np.array_equal(a[0].vertices, b[0].vertices)
    c = synth.generuj_plytke(uk, 1, korony, np.random.default_rng(5), op, seed=5)
    assert dataclasses.asdict(c[1]) != dataclasses.asdict(a[1])


def test_gniazda_puste_dopelniaja_zajete(korony):
    uk = U.wczytaj("poranna")
    _, prawda = synth.generuj_plytke(uk, 4, korony, np.random.default_rng(0), synth.Opcje(wspolczynnik=(1.0, 1.0)), seed=0)
    zajete = {p.gniazdo for p in prawda.prace}
    assert zajete.isdisjoint(prawda.gniazda_puste)
    assert zajete | set(prawda.gniazda_puste) == {g.id for g in uk.sockets}
    assert len(zajete) == len(prawda.prace)  # bez podwójnego obsadzenia


# --- zapis / odczyt ------------------------------------------------------------
def test_zapis_tworzy_brakujacy_katalog_i_polskie_znaki_ze_spacja(korony, tmp_path):
    uk = U.wczytaj("wieczorna")
    skan, prawda = synth.generuj_plytke(uk, 1, korony, np.random.default_rng(0), synth.Opcje(prace_na_plytce=1), seed=0)
    wy = tmp_path / "brak katalogu" / "dane żółć ś"
    assert not wy.exists()
    p_stl, p_json = synth.zapisz(skan, prawda, wy, "skan ąę")
    assert p_stl.exists() and p_json.exists()
    pr = synth.wczytaj_prawde(p_json)
    assert pr.plik_stl == "skan ąę.stl" and pr.prace[0].projekt == prawda.prace[0].projekt
    assert len(trimesh.load(p_stl, force="mesh").faces) == len(skan.faces)


@pytest.mark.xfail(reason="ZNALEZISKO S9: zapisz() nadpisuje istniejący skan_*.stl/.json bez ostrzeżenia (ten sam seed i numer → cicha utrata poprzedniej prawdy)", strict=True)
def test_zapis_nie_nadpisuje_istniejacego(korony, tmp_path):
    uk = U.wczytaj("wieczorna")
    skan, prawda = synth.generuj_plytke(uk, 1, korony, np.random.default_rng(0), synth.Opcje(prace_na_plytce=1), seed=0)
    synth.zapisz(skan, prawda, tmp_path, "t")
    (tmp_path / "t.json").write_text("{}", encoding="utf-8")
    with pytest.raises(FileExistsError):
        synth.zapisz(skan, prawda, tmp_path, "t")


@pytest.mark.xfail(reason="ZNALEZISKO S10: wczytaj_prawde nie toleruje nowych pól w JSON (TypeError) — każde rozszerzenie formatu psuje odczyt starych/nowych plików", strict=True)
def test_wczytaj_prawde_toleruje_nowe_pola(korony, tmp_path):
    uk = U.wczytaj("wieczorna")
    skan, prawda = synth.generuj_plytke(uk, 1, korony, np.random.default_rng(0), synth.Opcje(prace_na_plytce=1), seed=0)
    _, p_json = synth.zapisz(skan, prawda, tmp_path, "t")
    d = json.loads(p_json.read_text(encoding="utf-8"))
    d["wersja_formatu"] = 2
    p_json.write_text(json.dumps(d), encoding="utf-8")
    assert synth.wczytaj_prawde(p_json).numer == 1


def test_wczytaj_prawde_bez_ubytkow_wybucha(tmp_path):
    p = tmp_path / "x.json"
    p.write_text(json.dumps({"plytka": "wieczorna", "numer": 1, "seed": 0, "szum_sigma": 0.03, "z_top": 8.0,
                             "gniazda_puste": [], "prace": [{"gniazdo": 1, "projekt": "a.stl", "wspolczynnik": 1.2, "transformacja": np.eye(4).tolist()}]}), encoding="utf-8")
    with pytest.raises(KeyError):  # ZNALEZISKO S10 (obserwowane): brak 'ubytki' = KeyError zamiast domyślnej pustej listy
        synth.wczytaj_prawde(p)


def test_zdegenerowana_transformacja_w_prawdzie_nie_jest_wykrywana(tmp_path):
    """ZNALEZISKO S10 (obserwowane): macierz zerowa / 3×3 przechodzi przez wczytaj_prawde bez walidacji."""
    for T in (np.zeros((4, 4)).tolist(), np.eye(3).tolist()):
        p = tmp_path / "x.json"
        p.write_text(json.dumps({"plytka": "wieczorna", "numer": 1, "seed": 0, "szum_sigma": 0.03, "z_top": 8.0,
                                 "gniazda_puste": [], "prace": [{"gniazdo": 1, "projekt": "a.stl", "wspolczynnik": 1.2, "transformacja": T, "ubytki": []}]}), encoding="utf-8")
        assert synth.wczytaj_prawde(p).prace[0].transformacja == T


# --- CLI -------------------------------------------------------------------------
def uruchom_main(monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["synth", *map(str, args)])
    synth.main()


def test_cli_sciezki_ze_spacjami_i_polskimi_znakami(korony, tmp_path, monkeypatch, capsys):
    proj = tmp_path / "projekty ąćę ł"
    proj.mkdir()
    for k in korony:
        (proj / k.name).write_bytes(k.read_bytes())
    wy = tmp_path / "wyjście ś"
    uruchom_main(monkeypatch, "--projekty", proj, "--plytka", "poranna", "--numer", 5, "--ile", 2, "--seed", 3, "--wyjscie", wy, "--prace", 1, "--ubytki", "0-0")
    pliki = sorted(p.name for p in wy.iterdir())
    assert pliki == ["skan_poranna_n5_s0003.json", "skan_poranna_n5_s0003.stl", "skan_poranna_n5_s0004.json", "skan_poranna_n5_s0004.stl"]
    pr = synth.wczytaj_prawde(wy / "skan_poranna_n5_s0004.json")
    assert pr.seed == 4 and pr.numer == 5 and pr.prace[0].wspolczynnik == 1.0
    out = capsys.readouterr().out
    assert "skan_poranna_n5_s0003.stl" in out and korony[0].name not in out


def test_cli_brak_projektow_konczy_sie_systemexit(tmp_path, monkeypatch):
    with pytest.raises(SystemExit, match="brak plików STL"):
        uruchom_main(monkeypatch, "--projekty", tmp_path, "--wyjscie", tmp_path / "w")


@pytest.mark.parametrize("numer", [0, 7, 4])
def test_cli_zly_numer_plytki(korony, tmp_path, monkeypatch, numer):
    with pytest.raises(FileNotFoundError):
        uruchom_main(monkeypatch, "--projekty", korony[0].parent, "--plytka", "wieczorna", "--numer", numer, "--wyjscie", tmp_path)
    assert not (tmp_path / f"skan_wieczorna_n{numer}_s0000.stl").exists()


def test_cli_ile_zero_nic_nie_pisze(korony, tmp_path, monkeypatch):
    uruchom_main(monkeypatch, "--projekty", korony[0].parent, "--ile", 0, "--wyjscie", tmp_path / "w")
    assert not (tmp_path / "w").exists()


def test_cli_ujemny_szum_przechodzi_bez_bledu(korony, tmp_path, monkeypatch):
    """ZNALEZISKO S4 (obserwowane)."""
    uruchom_main(monkeypatch, "--projekty", korony[0].parent, "--szum", -1, "--prace", 1, "--ubytki", "0-0", "--wyjscie", tmp_path / "w")
    pr = synth.wczytaj_prawde(next((tmp_path / "w").glob("*.json")))
    assert pr.szum_sigma == -1.0


@pytest.mark.xfail(reason="ZNALEZISKO S7: '--ubytki 2' / '0--2' / 'a-b' kończy się surowym ValueError z split('-') zamiast komunikatem argparse", strict=True)
@pytest.mark.parametrize("ub", ["2", "0--2", "a-b"])
def test_cli_zakres_ubytkow_zle_sformatowany(korony, tmp_path, monkeypatch, ub):
    with pytest.raises(SystemExit):
        uruchom_main(monkeypatch, "--projekty", korony[0].parent, "--ubytki", ub, "--wyjscie", tmp_path / "w")


@pytest.mark.xfail(sys.platform != "win32", reason="ZNALEZISKO S11: glob('*.stl') na POSIX pomija pliki .STL (exocad/Windows piszą wielkimi literami); na Windows działa przez przypadek", strict=True)
def test_cli_rozszerzenie_wielkimi_literami(korony, tmp_path, monkeypatch):
    proj = tmp_path / "p"
    proj.mkdir()
    (proj / "A.STL").write_bytes(korony[0].read_bytes())
    uruchom_main(monkeypatch, "--projekty", proj, "--prace", 1, "--ubytki", "0-0", "--wyjscie", tmp_path / "w")
    assert synth.wczytaj_prawde(next((tmp_path / "w").glob("*.json"))).prace[0].projekt == "A.STL"
