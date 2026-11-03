"""narzedzia/rzut_z_gory.py (B4, N1) i narzedzia/atrapy_koron.py (S9)."""
import sys

import numpy as np
import pytest
import trimesh
from PIL import Image

import atrapy_koron
import rzut_z_gory
from stanowisko import synth, uklad as U


@pytest.fixture
def skan_z_prawda(korony, tmp_path):
    uk = U.wczytaj("wieczorna")
    skan, prawda = synth.generuj_plytke(uk, 1, korony, np.random.default_rng(0), synth.Opcje(ubytki_na_prace=(1, 1), prace_na_plytce=2), seed=0)
    p_stl, p_json = synth.zapisz(skan, prawda, tmp_path / "wy ś", "skan ą")
    return p_stl, p_json, prawda, uk


def piksele_etykiet(png):
    """Piksele z przewagą niebieskiego: mapa wysokości ma B ≤ R + 40, tekst jest wygładzany (Pillow ≥ 10)."""
    a = np.asarray(Image.open(png)).astype(int)
    return np.argwhere(a[..., 2] - a[..., 0] > 100)


def test_etykieta_gniazda_w_rzucie_lezy_w_gniezdzie(korony, tmp_path):
    """B4: projekt nieskoncentrowany w (0,0) (jak STL z exocad) — etykieta i tak w środku gniazda."""
    m = trimesh.load(korony[0])
    m.apply_translation([30.0, -25.0, 0.0])
    p = tmp_path / "przesuniety.stl"
    m.export(p)
    uk = U.wczytaj("wieczorna")
    skan, prawda = synth.generuj_plytke(uk, 1, [p], np.random.default_rng(0), synth.Opcje(ubytki_na_prace=(0, 0)), seed=0)
    T = np.array(prawda.prace[0].transformacja)
    g = uk.gniazdo(prawda.prace[0].gniazdo)
    assert not g.zawiera(T[0, 3], T[1, 3], margines=2.0)  # translacja z prawdy NIE jest środkiem pracy
    p_stl, _ = synth.zapisz(skan, prawda, tmp_path / "w", "s")
    px = 0.2
    out = rzut_z_gory.render(p_stl, px, prawda=True)
    Z, xy0 = rzut_z_gory.mapa_wysokosci(trimesh.load(p_stl, force="mesh"), px)
    pix = piksele_etykiet(out)
    assert len(pix) > 0
    # piksel (wiersz, kolumna) → (x, y) w mm; obraz odwrócony w pionie
    x = xy0[0] + pix[:, 1].mean() * px
    y = xy0[1] + (Z.shape[0] - pix[:, 0].mean()) * px
    assert g.zawiera(x, y, margines=1.0), (x, y, g.x, g.y)


def test_render_png_rozmiar_i_krzyzyki(skan_z_prawda):
    p_stl, p_json, prawda, uk = skan_z_prawda
    out = rzut_z_gory.render(p_stl, 0.2, prawda=True)
    assert out == p_stl.with_suffix(".png") and out.exists()
    im = Image.open(out)
    assert im.size[0] == pytest.approx(96 / 0.2, abs=2) and im.size[1] == pytest.approx(96 / 0.2, abs=2)
    arr = np.asarray(im)
    assert ((arr[..., 0] == 255) & (arr[..., 1] == 0) & (arr[..., 2] == 0)).any()


@pytest.mark.parametrize("px", [0.0, -0.1, float("nan")])
def test_render_px_niedodatni_odrzucony(skan_z_prawda, px):
    with pytest.raises(ValueError, match="px"):
        rzut_z_gory.render(skan_z_prawda[0], px, prawda=False)


def test_mapa_wysokosci_nan_i_pusta_siatka():
    m = trimesh.creation.box([10, 10, 1])
    V = m.vertices.copy()
    V[0] = np.nan
    with pytest.raises(ValueError, match="NaN"):
        rzut_z_gory.mapa_wysokosci(trimesh.Trimesh(V, m.faces, process=False), 0.1)
    with pytest.raises(ValueError, match="pusta"):
        rzut_z_gory.mapa_wysokosci(trimesh.Trimesh(np.zeros((0, 3)), np.zeros((0, 3), dtype=int), process=False), 0.1)


def test_cli_rzut_px_ujemny(skan_z_prawda, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["rzut", str(skan_z_prawda[0]), "--px", "-1"])
    with pytest.raises(SystemExit):
        rzut_z_gory.main()
    assert "--px" in capsys.readouterr().err


def test_atrapy_nie_nadpisuja_bez_flagi(tmp_path):
    p = atrapy_koron.generuj(tmp_path, 1, 1, mosty=0)[0]
    p.write_bytes(b"x")
    with pytest.raises(FileExistsError):
        atrapy_koron.generuj(tmp_path, 1, 1, mosty=0)
    assert p.read_bytes() == b"x"
    atrapy_koron.generuj(tmp_path, 1, 1, mosty=0, nadpisz=True)
    assert p.stat().st_size > 1
