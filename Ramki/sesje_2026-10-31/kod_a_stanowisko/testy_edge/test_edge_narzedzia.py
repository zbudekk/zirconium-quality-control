"""Edge-case'y narzedzia/atrapy_koron.py i narzedzia/rzut_z_gory.py."""
import json
import sys

import numpy as np
import pytest
import trimesh
from PIL import Image

from conftest import U, atrapy_koron, rzut_z_gory, synth


# --- atrapy_koron ------------------------------------------------------------------
@pytest.mark.parametrize("typ", list(atrapy_koron.TYPY))
def test_kazda_atrapa_szczelna_brzeg_na_z0(typ):
    W, L, H, g, amp = atrapy_koron.TYPY[typ]
    m = atrapy_koron.korona(W, L, H, g, amp, rng=np.random.default_rng(0))
    assert m.is_watertight and m.is_winding_consistent
    assert m.bounds[0, 2] == pytest.approx(0.0, abs=1e-9)
    assert m.volume > 0
    assert max(m.extents[:2]) == pytest.approx(max(W, L) * 1.1, rel=0.15)  # obrys ≈ W×L (+10 % wybrzuszenia, nieregularność)


def test_atrapa_most_jest_szczelna_i_szersza_niz_20mm():
    m = atrapy_koron.most(np.random.default_rng(1))
    assert m.is_watertight and m.extents[0] > 20.0  # synth: szer > 20 → rynienka


def test_atrapa_zdegenerowane_parametry():
    # ścianka większa niż promień → wnętrze obcięte do r=0.5, nadal siatka skończona
    m = atrapy_koron.korona(2.0, 2.0, 5.0, 1, 0.05, scianka=5.0, rng=np.random.default_rng(0))
    assert np.isfinite(m.vertices).all() and len(m.faces) > 0
    # bardzo mało segmentów
    m = atrapy_koron.korona(6, 6, 8, 1, 0.05, n_theta=4, n_u=6, rng=np.random.default_rng(0))
    assert len(m.faces) > 0


def test_generuj_ile_zero_tylko_most(tmp_path):
    pliki = atrapy_koron.generuj(tmp_path / "ą ę", 0, 1, mosty=1)
    assert [p.name for p in pliki] == ["atrapa_most_01_4pkt.stl"] and pliki[0].exists()


def test_generuj_deterministyczne(tmp_path):
    a = atrapy_koron.generuj(tmp_path / "a", 3, 7, mosty=0)
    b = atrapy_koron.generuj(tmp_path / "b", 3, 7, mosty=0)
    for pa, pb in zip(a, b):
        assert pa.read_bytes() == pb.read_bytes()


def test_generuj_nadpisuje_bez_ostrzezenia(tmp_path):
    """ZNALEZISKO S9 (obserwowane, analogicznie do synth.zapisz)."""
    p = atrapy_koron.generuj(tmp_path, 1, 1, mosty=0)[0]
    p.write_bytes(b"x")
    atrapy_koron.generuj(tmp_path, 1, 1, mosty=0)
    assert p.stat().st_size > 1


def test_nazwy_atrap_bez_danych_osobowych(tmp_path):
    for p in atrapy_koron.generuj(tmp_path, 4, 1):
        assert p.name.startswith("atrapa_")


# --- rzut_z_gory -------------------------------------------------------------------
@pytest.fixture
def skan_z_prawda(korony, tmp_path):
    uk = U.wczytaj("wieczorna")
    skan, prawda = synth.generuj_plytke(uk, 1, korony, np.random.default_rng(0), synth.Opcje(ubytki_na_prace=(1, 1), prace_na_plytce=2), seed=0)
    p_stl, p_json = synth.zapisz(skan, prawda, tmp_path / "wy ś", "skan ą")
    return p_stl, p_json, prawda, uk


def test_render_png_rozmiar_i_krzyzyki(skan_z_prawda):
    p_stl, p_json, prawda, uk = skan_z_prawda
    out = rzut_z_gory.render(p_stl, 0.2, prawda=True)
    assert out == p_stl.with_suffix(".png") and out.exists()
    im = Image.open(out)
    assert im.size[0] == pytest.approx(96 / 0.2, abs=2) and im.size[1] == pytest.approx(96 / 0.2, abs=2)
    arr = np.asarray(im)
    assert ((arr[..., 0] == 255) & (arr[..., 1] == 0) & (arr[..., 2] == 0)).any()  # czerwone krzyżyki ubytków


def test_render_bez_json_nie_wybucha(skan_z_prawda):
    p_stl, p_json, *_ = skan_z_prawda
    p_json.unlink()
    assert rzut_z_gory.render(p_stl, 0.5, prawda=True).exists()


def test_render_bez_prawdy_nie_czyta_json(skan_z_prawda, monkeypatch):
    p_stl, p_json, *_ = skan_z_prawda
    p_json.write_text("to nie jest json", encoding="utf-8")
    assert rzut_z_gory.render(p_stl, 0.5, prawda=False).exists()


@pytest.mark.xfail(reason="ZNALEZISKO B4: etykieta numeru gniazda rysowana w T[0,3],T[1,3] — to translacja łączna z centrowaniem projektu; projekt nieskoncentrowany w (0,0) (jak STL z exocad) daje etykietę poza gniazdem", strict=True)
def test_etykieta_gniazda_w_rzucie_lezy_w_gniezdzie(korony, tmp_path):
    m = trimesh.load(korony[0])
    m.apply_translation([30.0, -25.0, 0.0])  # projekt w układzie szczęki, nie w (0,0)
    p = tmp_path / "przesuniety.stl"
    m.export(p)
    uk = U.wczytaj("wieczorna")
    _, prawda = synth.generuj_plytke(uk, 1, [p], np.random.default_rng(0), synth.Opcje(ubytki_na_prace=(0, 0)), seed=0)
    T = np.array(prawda.prace[0].transformacja)
    g = uk.gniazdo(prawda.prace[0].gniazdo)
    # sama transformacja jest poprawna…
    V = trimesh.transform_points(m.vertices, T @ trimesh.transformations.scale_matrix(prawda.prace[0].wspolczynnik))
    assert g.zawiera(V[:, 0].mean(), V[:, 1].mean(), margines=1.0)
    # …ale rzut_z_gory używa kolumny translacji jako środka pracy
    assert g.zawiera(T[0, 3], T[1, 3], margines=2.0)


@pytest.mark.parametrize("px", [0.0, float("nan")])
def test_render_px_zero_lub_nan_wybucha_przypadkowo(skan_z_prawda, px):
    """ZNALEZISKO N1 (obserwowane): px=0/NaN → 'negative dimensions are not allowed' z numpy, nie komunikat o px."""
    with pytest.raises(ValueError, match="negative dimensions"):
        rzut_z_gory.render(skan_z_prawda[0], px, prawda=False)


@pytest.mark.xfail(reason="ZNALEZISKO N1: px<0 nie jest walidowane — ujemne indeksy pikseli → IndexError w np.maximum.at", strict=True)
def test_render_px_ujemny_odrzucony(skan_z_prawda):
    with pytest.raises(ValueError):
        rzut_z_gory.render(skan_z_prawda[0], -0.1, prawda=False)


def test_mapa_wysokosci_px_wiekszy_niz_plytka(skan_z_prawda):
    m = trimesh.load(skan_z_prawda[0], force="mesh")
    Z, xy0 = rzut_z_gory.mapa_wysokosci(m, 200.0)
    assert Z.shape == (1, 1) and Z[0, 0] == pytest.approx(m.vertices[:, 2].max())


def test_mapa_wysokosci_nan_wybucha_przypadkowo():
    """ZNALEZISKO N1 (obserwowane): NaN w wierzchołkach → min() = NaN → 'negative dimensions' zamiast komunikatu o NaN."""
    m = trimesh.creation.box([10, 10, 1])
    V = m.vertices.copy()
    V[0] = np.nan
    with pytest.raises(ValueError, match="negative dimensions"):
        rzut_z_gory.mapa_wysokosci(trimesh.Trimesh(V, m.faces, process=False), 0.1)


def test_mapa_wysokosci_pusta_siatka_wybucha():
    """ZNALEZISKO N1 (obserwowane): 0 wierzchołków → ValueError z numpy (min of empty)."""
    with pytest.raises(ValueError):
        rzut_z_gory.mapa_wysokosci(trimesh.Trimesh(np.zeros((0, 3)), np.zeros((0, 3), dtype=int), process=False), 0.1)


def test_cli_rzut_wiele_plikow(skan_z_prawda, monkeypatch, capsys):
    p_stl = skan_z_prawda[0]
    monkeypatch.setattr(sys, "argv", ["rzut", str(p_stl), str(p_stl), "--px", "0.5", "--prawda"])
    rzut_z_gory.main()
    out = capsys.readouterr().out.strip().splitlines()
    assert len(out) == 2 and out[0].endswith("skan ą.png")
