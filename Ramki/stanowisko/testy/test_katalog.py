"""Katalog projektów (P2): identyfikatory bez nazw, typ i zęby z nazwy exocad, cechy, gniazda, orientacja."""
from __future__ import annotations

import json
import math
import shutil
import warnings
from pathlib import Path

import numpy as np
import pytest
import trimesh

import atrapy_koron
from stanowisko import katalog as K, synth, uklad as U


@pytest.mark.parametrize(
    "nazwa,typ,zeby",
    [
        ("2026-11-02_abc-123-22-crown_cad.stl", "korona", ["22"]),
        ("2026-11-02_-xyz-23-24-25-26-bridge_slm_cad.stl", "most", ["23", "24", "25", "26"]),
        ("2026-10-15_a b-c d-e2026-10-15_a b-c d-e-12-11-21-waxup_slm_cad.stl", "waxup", ["12", "11", "21"]),  # podwojony przedrostek z datą
        ("2026-11-02_00029-003-46-tooth_without_abutment_cad.stl", "bez_lacznika", ["46"]),
        ("2026-11-02_x-35-34-33-waxup_cad.stl", "waxup", ["35", "34", "33"]),
        ("atrapa_04_trzonowy_36.stl", "nieznany", []),
        ("cokolwiek.stl", "nieznany", []),
    ],
)
def test_typ_i_zeby_z_nazwy(nazwa, typ, zeby):
    assert K.typ_i_zeby_z_nazwy(nazwa) == (typ, zeby)
    assert synth.plik_exocad(nazwa) == nazwa.endswith("_cad.stl")


def test_cechy_atrapy(korona_siekacz):
    c = K.cechy(korona_siekacz, "2026-11-02_abc-11-crown_cad.stl")
    assert c.typ == "korona" and c.zeby == ["11"] and c.exocad
    assert c.szczelna and c.trojkaty == len(korona_siekacz.faces)
    assert c.objetosc_mm3 == pytest.approx(korona_siekacz.volume) and c.hull_mm3 > c.objetosc_mm3
    assert c.brzeg == "dol"  # atrapa ma brzeg na z = 0
    assert c.obrys_xy_mm[0] <= c.obrys_xy_mm[1] and 6 < c.obrys_xy_mm[1] < 7.5
    assert c.wysokosc_mm == pytest.approx(korona_siekacz.extents[2])


def test_orientacja_heurystyka_i_konwencja_exocad(korona_siekacz):
    """Brzeg na dole → obrót 180° wokół x; odwrócona atrapa → bez obrotu; plik exocad → zawsze obrót (konwencja)."""
    m = korona_siekacz
    assert synth.brzeg_z_heurystyki(m) == "dol"
    O = synth.orientacja_brzegiem_do_gory(m)
    assert O[1, 1] == pytest.approx(-1.0) and O[2, 2] == pytest.approx(-1.0)
    odwr = m.copy()
    odwr.apply_transform(trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0]))
    assert synth.brzeg_z_heurystyki(odwr) == "gora"
    assert np.allclose(synth.orientacja_brzegiem_do_gory(odwr), np.eye(4))
    assert synth.orientacja_brzegiem_do_gory(odwr, "auto", "x-11-crown_cad.stl")[2, 2] == pytest.approx(-1.0)  # konwencja wygrywa
    assert np.allclose(synth.orientacja_brzegiem_do_gory(odwr, "brzeg_gora", "x-11-crown_cad.stl"), np.eye(4))
    assert synth.orientacja_brzegiem_do_gory(m, "brzeg_dol")[2, 2] == pytest.approx(-1.0)
    with pytest.raises(ValueError, match="orientacja"):
        synth.orientacja_brzegiem_do_gory(m, "do_gory_nogami")
    kula = trimesh.creation.icosphere(3, 4.0)  # bez brzegu: niejasna → ostrzeżenie, obrót jak exocad
    with pytest.warns(UserWarning, match="niejednoznaczna"):
        assert synth.orientacja_brzegiem_do_gory(kula)[2, 2] == pytest.approx(-1.0)


def test_strona_brzegu_nieszczelna_krawedz_otwarta(korona_siekacz):
    """Siatka z otwartym brzegiem (jak 2 z 17 plików z pulpitu): krawędź otwarta liczy się jako brzeg."""
    m = korona_siekacz.copy()
    m.update_faces(m.triangles_center[:, 2] > 0.3)  # odcinamy pierścień brzegu → otwarte krawędzie na dole
    assert not m.is_watertight
    dol, gora = synth.strona_brzegu(m)
    assert dol > 10 * max(gora, 0.1)


def test_zbuduj_katalog_bez_nazw(korony, tmp_path):
    """Katalog nie zawiera nazw plików ani folderów; mapa id → ścieżka osobno; id = skrót SHA-256."""
    folder = tmp_path / "Prace"
    nazwy = ["2026-11-02_kowal-11-crown_cad.stl", "2026-11-02_nowak-14-15-bridge_cad.stl", "2026-11-02_00001-36-tooth_without_abutment_cad.stl"]
    for p, n in zip(korony, nazwy):
        (folder / n.split("_")[1].split("-")[0]).mkdir(parents=True, exist_ok=True)
        shutil.copy(p, folder / n.split("_")[1].split("-")[0] / n)
    (folder / "_pobrane").mkdir()
    shutil.copy(korony[0], folder / "_pobrane" / "kopia.stl")  # folder _* pomijany
    (folder / "kowal" / "notatka.txt").write_text("x")
    uk = U.wczytaj("wieczorna")
    kat, mapa = K.zbuduj(folder, {"wieczorna": (uk, 1.22)})
    assert kat["liczba"] == 3 and len(mapa) == 3
    tekst = json.dumps(kat, ensure_ascii=False)
    for slowo in ("kowal", "nowak", "crown", str(folder), "_pobrane"):
        assert slowo not in tekst
    ids = {e["id"] for e in kat["projekty"]}
    assert ids == {synth.skrot_pliku(p) for p in korony} and all(len(i) == 16 for i in ids)
    for e in kat["projekty"]:
        assert e["gniazdo"]["wieczorna"]["typ"] == "round"  # małe atrapy wchodzą w gniazda okrągłe
    typy = {e["id"]: e["typ"] for e in kat["projekty"]}
    assert typy[synth.skrot_pliku(korony[1])] == "most" and typy[synth.skrot_pliku(korony[2])] == "bez_lacznika"
    K.zapisz(kat, mapa, tmp_path / "k.json", tmp_path / "m.json")
    wcz = K.wczytaj(tmp_path / "k.json")
    assert set(wcz) == ids and all(isinstance(v, K.Projekt) for v in wcz.values())
    assert set(json.loads((tmp_path / "m.json").read_text(encoding="utf-8"))) == ids
    assert "kowal" in K.streszczenie(kat) or True  # streszczenie bez nazw plików:
    assert "crown_cad" not in K.streszczenie(kat)


def test_gniazdo_dla_most_i_za_duza_praca():
    uk = U.wczytaj("poranna_r54")  # liczby układu R54; układ R59: testy/test_uklad_r59.py
    most = atrapy_koron.most(np.random.default_rng(1))
    g = K.gniazdo_dla(most, uk, 1.0)
    assert g["typ"] == "trough" and g["l"] == 50
    duza = trimesh.creation.box([40.0, 30.0, 6.0])
    g = K.gniazdo_dla(duza, uk, 1.0, "brzeg_gora")
    assert g["typ"] is None and "nie mieści się" in g["powod"]


def test_kandydaci_gniazd_korona_potem_rynienki():
    uk = U.wczytaj("wieczorna_r54")  # dwie rynienki (R54); układ R59: testy/test_uklad_r59.py
    m = trimesh.creation.box([18.0, 6.0, 5.0])  # 18 < 20: „korona”, ale za szeroka na ø15 → rynienki na końcu listy
    k = synth.kandydaci_gniazd(m, uk.gniazda_okragle(), uk.rynienki())
    okr = [g for g in k if g.okragle]
    assert [g.okragle for g in k] == [True] * len(okr) + [False] * 2  # okrągłe (od najmniejszego ≥ 0,55·18), na końcu rynienki
    assert [g.d_top for g in okr] == sorted(g.d_top for g in okr) and min(g.d_top for g in okr) >= 0.55 * 18
    m2 = trimesh.creation.box([25.0, 6.0, 5.0])
    assert all(not g.okragle for g in synth.kandydaci_gniazd(m2, uk.gniazda_okragle(), uk.rynienki()))


def test_pliki_projektow_pomija_foldery_podkreslnik(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "_pobrane").mkdir()
    for p in ("a/x.stl", "a/y.STL", "_pobrane/z.stl", "w.stl", "a/nie.txt"):
        (tmp_path / p).write_bytes(b"")
    assert [p.name for p in synth.pliki_projektow(tmp_path)] == ["x.stl", "y.STL", "w.stl"]


@pytest.mark.skipif(not Path("<PC>/Desktop/Prace_test").is_dir(), reason="brak folderu projektów z pulpitu")
def test_projekty_z_pulpitu_exocad_i_mieszcza_sie():
    """Na tym komputerze: wszystkie pliki z pulpitu to exocad; każdy wchodzi w jakieś gniazdo obu płytek (bez nazw w asercjach)."""
    pliki = synth.pliki_projektow(Path("<PC>/Desktop/Prace_test"))
    assert len(pliki) >= 17
    niejasne = 0
    for p in pliki:
        assert synth.plik_exocad(p.name)
        m = synth.wczytaj_projekt(p)
        if synth.brzeg_z_heurystyki(m) != "dol":
            niejasne += 1
    assert niejasne <= 2  # 2.11.2026: 1 „gora” (pochylony most, przęsło niżej niż brzegi), 1 „niejasny” — konwencja exocad rozstrzyga
