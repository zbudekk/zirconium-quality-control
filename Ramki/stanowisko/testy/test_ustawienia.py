"""ustawienia.py i ustawienia.toml (B3, D3, P2, P5)."""
import re
import subprocess
import tomllib

import pytest

from conftest import STANOWISKO
from stanowisko import synth, ustawienia as UST, uklad as U

ZRODLA = {p.stem: p for p in (STANOWISKO / "stanowisko").glob("*.py")}


def test_kod_czyta_ustawienia_toml():
    assert "tomllib" in ZRODLA["ustawienia"].read_text(encoding="utf-8")
    assert "UST." in ZRODLA["synth"].read_text(encoding="utf-8")


@pytest.mark.parametrize("plik", [UST.PLIK_USTAWIEN, UST.PLIK_PRZYKLADU])
def test_plik_ustawien_i_przyklad_przechodza_walidacje(plik):
    d = UST.wczytaj_ustawienia(plik)
    assert set(d) == set(UST.SCHEMAT)


def test_przyklad_ma_te_same_klucze_co_lokalny():
    a, b = UST.wczytaj_ustawienia(UST.PLIK_USTAWIEN), UST.wczytaj_ustawienia(UST.PLIK_PRZYKLADU)
    assert {s: set(v) for s, v in a.items()} == {s: set(v) for s, v in b.items()}
    assert a["synth"] == b["synth"] and a["inspect"] == b["inspect"] and a["plytki"] == b["plytki"]


def test_kazdy_klucz_uzyty_w_kodzie_albo_oznaczony_jako_przyszly():
    for sekcja, klucze in UST.SCHEMAT.items():
        for k, (_, moduly) in klucze.items():
            if moduly == UST.PRZYSZLY:
                continue
            for modul in moduly.split(", "):  # klucz może czytać kilka modułów, np. "inspect, synth"
                assert re.search(rf"\b{k}\b", ZRODLA[modul].read_text(encoding="utf-8")), (sekcja, k, modul)


def test_progi_synth_nie_sa_zdublowane_w_kodzie():
    src = ZRODLA["synth"].read_text(encoding="utf-8")
    assert "1.20, 1.25" not in src and "0.03" not in src and "pas_brzegu: float = 2.0" not in src


def test_sciezki_plytek_jedno_zrodlo():
    ust = UST.domyslne()
    for n in ("wieczorna", "poranna", "okragla_wieczorna", "okragla_poranna",
              "wieczorna_r54", "poranna_r54", "okragla_wieczorna_r54", "okragla_poranna_r54"):  # R59: układ nowy i poprzedni
        assert UST.katalog_plytki(ust, n) == (U.KATALOG_MODELI / n).resolve()
        assert (UST.katalog_plytki(ust, n) / "uklad.json").exists()
    with pytest.raises(UST.BladUstawien, match="brak płytki"):
        UST.katalog_plytki(ust, "obiadowa")


def _zepsuj(tmp_path, stare, nowe):
    t = UST.PLIK_PRZYKLADU.read_text(encoding="utf-8")
    assert stare in t
    p = tmp_path / "ustawienia.toml"
    p.write_text(t.replace(stare, nowe), encoding="utf-8")
    return p


@pytest.mark.parametrize("stare,nowe,komunikat", [
    ("szum_sigma_mm = 0.03", "szum_sigma_mm = \"0.03\"", r"\[synth\] szum_sigma_mm: oczekiwano float"),
    ("szum_sigma_mm = 0.03", "szum_sigma = 0.03", r"\[synth\] szum_sigma: nieznany klucz"),
    ("pas_brzegu_mm = 1.5", "", r"\[inspect\] pas_brzegu_mm: brak klucza"),
    ("wspolczynnik_min = 1.20", "wspolczynnik_min = 1.30", r"\[synth\] wspolczynnik_min: musi być"),
    ("srednica_min_mm = 0.2", "srednica_min_mm = 0", r"\[inspect\] srednica_min_mm"),
    ("port = 8765", "port = 8765.0", r"\[ramki\] port: oczekiwano int"),
    ("[ramki]", "[ramka]", r"\[ramka\]: nieznana sekcja"),
    ('wieczorna = "modele_plytek/wieczorna"', 'wieczorna = "modele_plytek\\\\wieczorna"', r"\[plytki\] wieczorna: ścieżka"),
    ("tryb_pytaj_przed_zapisem = true", "tryb_pytaj_przed_zapisem = 1", r"\[excel\] tryb_pytaj_przed_zapisem: oczekiwano bool"),
])
def test_zly_plik_ustawien_czytelny_blad(tmp_path, stare, nowe, komunikat):
    p = _zepsuj(tmp_path, stare, nowe)
    with pytest.raises(UST.BladUstawien, match=r"^ustawienia\.toml: " + komunikat):
        UST.wczytaj_ustawienia(p)


def test_zla_skladnia_i_brak_pliku(tmp_path):
    p = tmp_path / "ustawienia.toml"
    p.write_text("[synth\nszum = ", encoding="utf-8")
    with pytest.raises(UST.BladUstawien, match="ustawienia.toml: błąd składni TOML"):
        UST.wczytaj_ustawienia(p)
    with pytest.raises(FileNotFoundError, match="ustawienia.przyklad.toml"):
        UST.wczytaj_ustawienia(tmp_path / "brak.toml")


def test_opcje_domyslne_z_toml():
    d = UST.domyslne()
    op = synth.Opcje()
    assert op.szum_sigma == d["synth"]["szum_sigma_mm"]
    assert op.wspolczynnik == (d["synth"]["wspolczynnik_min"], d["synth"]["wspolczynnik_max"])
    assert op.prog_glebokosci == d["inspect"]["prog_glebokosci_mm"]


def test_toml_parsuje_sie_i_ma_sekcje_z_readme():
    with open(UST.PLIK_USTAWIEN, "rb") as f:
        assert set(tomllib.load(f)) == {"sciezki", "plytki", "match", "inspect", "synth", "excel", "ramki"}


# --- repo: P2, P5 ------------------------------------------------------------------------
def _sledzone():
    return subprocess.run(["git", "ls-files"], cwd=STANOWISKO, capture_output=True, text=True, check=True).stdout.split()


def test_gitignore_wyklucza_dane_ustawienia_csv():
    gi = (STANOWISKO / ".gitignore").read_text(encoding="utf-8").split()
    assert {"dane/", "*.png", "*.sqlite", "*.csv", "ustawienia.toml"} <= set(gi)


def test_repo_nie_sledzi_danych_ani_ustawien_maszyny():
    sledzone = _sledzone()
    assert "ustawienia.toml" not in sledzone
    assert not any(s.startswith("dane/") or s.endswith((".png", ".sqlite", ".csv")) for s in sledzone)
    assert all(s.startswith("modele_plytek/") for s in sledzone if s.endswith(".stl"))


def test_przyklad_bez_sciezek_konkretnej_maszyny():
    for v in UST.wczytaj_ustawienia(UST.PLIK_PRZYKLADU)["sciezki"].values():
        assert "Users/" not in v


def test_nowe_klucze_maja_domyslne_ze_wzoru(tmp_path):
    """Klucze dodane po R59 (DOMYSLNE_NOWYCH) mogą nie istnieć w lokalnym ustawienia.toml - dostają wartość ze wzoru."""
    with open(UST.PLIK_PRZYKLADU, "rb") as f:
        wzor = tomllib.load(f)
    for sekcja, klucze in UST.DOMYSLNE_NOWYCH.items():
        for k, v in klucze.items():
            assert k in UST.SCHEMAT[sekcja] and wzor[sekcja][k] == v, (sekcja, k)
    nowe = {k for kl in UST.DOMYSLNE_NOWYCH.values() for k in kl}
    stary = "\n".join(linia for linia in UST.PLIK_PRZYKLADU.read_text(encoding="utf-8").splitlines() if linia.split("=")[0].strip() not in nowe)
    p = tmp_path / "ustawienia.toml"
    p.write_text(stary, encoding="utf-8")
    ust = UST.wczytaj_ustawienia(p)
    assert ust["inspect"]["pas_brzegu_od"] == "linia_i_plaszczyzna" and ust["synth"]["krawedz_rozmiar_max_mm"] == 0.40
    # wpis w pliku ma pierwszeństwo; zła wartość nadal jest błędem
    p.write_text(stary.replace("[inspect]", '[inspect]\npas_brzegu_od = "linia"'), encoding="utf-8")
    assert UST.wczytaj_ustawienia(p)["inspect"]["pas_brzegu_od"] == "linia"
    p.write_text(stary.replace("[inspect]", '[inspect]\npas_brzegu_od = "obok"'), encoding="utf-8")
    with pytest.raises(UST.BladUstawien, match="pas_brzegu_od"):
        UST.wczytaj_ustawienia(p)
