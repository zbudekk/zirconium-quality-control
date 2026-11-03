"""ustawienia.toml (klucze vs kod, duplikaty progów) i bezpieczeństwo danych pacjentów (plan wdrożenia v2, w. 365/369)."""
import json
import re
import subprocess
import sys
import tomllib

import numpy as np
import pytest

from conftest import STANOWISKO, U, synth

TOML = STANOWISKO / "ustawienia.toml"
ZRODLA = [STANOWISKO / "stanowisko" / "uklad.py", STANOWISKO / "stanowisko" / "synth.py",
          STANOWISKO / "narzedzia" / "atrapy_koron.py", STANOWISKO / "narzedzia" / "rzut_z_gory.py"]


@pytest.fixture(scope="module")
def toml():
    with open(TOML, "rb") as f:
        return tomllib.load(f)


def test_toml_parsuje_sie_i_ma_sekcje_z_readme(toml):
    assert set(toml) == {"sciezki", "plytki", "match", "inspect", "synth", "excel", "ramki"}
    assert toml["synth"] == {"szum_sigma_mm": 0.03, "wspolczynnik_min": 1.20, "wspolczynnik_max": 1.25}


@pytest.mark.xfail(reason="ZNALEZISKO B3: żaden moduł nie czyta ustawienia.toml (brak 'tomllib'/'toml' w kodzie); README nazywa go „jedynym plikiem ustawień”", strict=True)
def test_kod_czyta_ustawienia_toml():
    tekst = "\n".join(p.read_text(encoding="utf-8") for p in ZRODLA)
    assert re.search(r"tomllib|ustawienia\.toml", tekst)


def test_progi_synth_z_toml_zdublowane_w_kodzie(toml):
    """ZNALEZISKO B3 (obserwowane): te same liczby w Opcje, w argparse i w main() — toml ich nie steruje."""
    assert synth.Opcje().szum_sigma == toml["synth"]["szum_sigma_mm"]
    assert synth.Opcje().wspolczynnik == (toml["synth"]["wspolczynnik_min"], toml["synth"]["wspolczynnik_max"])
    src = (STANOWISKO / "stanowisko" / "synth.py").read_text(encoding="utf-8")
    assert src.count("1.20, 1.25") == 2 and 'default=0.03' in src


def test_sciezki_plytek_z_toml_istnieja(toml):
    for n in ("wieczorna", "poranna"):
        assert (STANOWISKO / toml["plytki"][n] / "uklad.json").exists()
        assert U.KATALOG_MODELI / n == (STANOWISKO / toml["plytki"][n]).resolve()


def test_sciezki_w_toml_uzywaja_ukosnikow_posix(toml):
    for v in toml["sciezki"].values():
        assert "\\" not in v


def test_klucze_toml_bez_duplikatow_i_z_jednostkami(toml):
    """Spójność nazewnictwa: progi w mm mają sufiks _mm; bez jednostki tylko udziały i współczynniki."""
    for sekcja in ("match", "inspect", "synth"):
        for k, v in toml[sekcja].items():
            if isinstance(v, float) and not k.endswith("_mm"):
                assert k in ("prog_akceptacji_pokrycie", "wspolczynnik_min", "wspolczynnik_max"), (sekcja, k)


# --- bezpieczeństwo danych pacjentów ---------------------------------------------------
@pytest.mark.xfail(reason="ZNALEZISKO P1: PracaNaPlytce.projekt = nazwa pliku STL projektu; gdy nazwa pliku z „Cyrkon” niesie nazwisko/numer zlecenia, trafia do JSON obok skanu (plan wdrożenia v2 w. 369)", strict=True)
def test_prawda_nie_zawiera_nazwy_pliku_projektu(korony, tmp_path):
    m = __import__("trimesh").load(korony[0])
    p = tmp_path / "Kowalski_Jan_12345_korona_16.stl"
    m.export(p)
    uk = U.wczytaj("wieczorna")
    skan, prawda = synth.generuj_plytke(uk, 1, [p], np.random.default_rng(0), synth.Opcje(), seed=0)
    _, p_json = synth.zapisz(skan, prawda, tmp_path / "w", "t")
    assert "Kowalski" not in p_json.read_text(encoding="utf-8")


def test_stdout_synth_nie_wypisuje_nazw_projektow(korony, tmp_path, monkeypatch, capsys):
    m = __import__("trimesh").load(korony[0])
    proj = tmp_path / "p"
    proj.mkdir()
    m.export(proj / "Kowalski_Jan_12345.stl")
    monkeypatch.setattr(sys, "argv", ["synth", "--projekty", str(proj), "--wyjscie", str(tmp_path / "w"), "--ubytki", "0-0"])
    synth.main()
    assert "Kowalski" not in capsys.readouterr().out


def test_nazwa_pliku_skanu_bez_danych_pacjenta(korony, tmp_path, monkeypatch):
    proj = tmp_path / "p"
    proj.mkdir()
    __import__("trimesh").load(korony[0]).export(proj / "Kowalski_Jan.stl")
    monkeypatch.setattr(sys, "argv", ["synth", "--projekty", str(proj), "--wyjscie", str(tmp_path / "w"), "--ubytki", "0-0"])
    synth.main()
    assert all(re.fullmatch(r"skan_wieczorna_n[1-3]_s\d{4}\.(stl|json)", p.name) for p in (tmp_path / "w").iterdir())


def test_gitignore_wyklucza_dane_png_sqlite():
    gi = (STANOWISKO / ".gitignore").read_text(encoding="utf-8").split()
    assert "dane/" in gi and "*.png" in gi and "*.sqlite" in gi


@pytest.mark.xfail(reason="ZNALEZISKO P2 (UWAGA): ustawienia.toml w repozytorium zawiera ścieżki konkretnej maszyny (OneDrive, konto 'stanowisko', folder eksportu skanera) — przenośność; zalecany ustawienia.przyklad.toml", strict=True)
def test_toml_w_repo_bez_wewnetrznych_sciezek(toml):
    sledzone = subprocess.run(["git", "ls-files"], cwd=STANOWISKO, capture_output=True, text=True).stdout.split()
    if "ustawienia.toml" not in sledzone:
        pytest.skip("toml nieśledzony w git")
    for v in toml["sciezki"].values():
        assert "OneDrive" not in v and "Users/" not in v


def test_repo_nie_sledzi_danych(korony):
    sledzone = subprocess.run(["git", "ls-files"], cwd=STANOWISKO, capture_output=True, text=True).stdout.split()
    assert not any(s.startswith("dane/") or s.endswith((".png", ".sqlite", ".csv")) for s in sledzone)
    assert all(s.startswith("modele_plytek/") for s in sledzone if s.endswith(".stl"))


def test_prawda_json_pola_bez_sciezek_absolutnych(korony, tmp_path):
    uk = U.wczytaj("wieczorna")
    skan, prawda = synth.generuj_plytke(uk, 1, korony, np.random.default_rng(0), synth.Opcje(prace_na_plytce=1), seed=0)
    _, p_json = synth.zapisz(skan, prawda, tmp_path, "t")
    d = json.loads(p_json.read_text(encoding="utf-8"))
    assert "/" not in d["plik_stl"] and "\\" not in d["plik_stl"]
    assert all("/" not in p["projekt"] and "\\" not in p["projekt"] for p in d["prace"])
    assert str(tmp_path) not in p_json.read_text(encoding="utf-8")
