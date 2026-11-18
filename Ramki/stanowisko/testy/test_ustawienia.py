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
    # [match]: filtr wysokości (P1) i korekta skali ze skanu (P3)
    ("filtr_wysokosc_min_udzial = 0.5", "filtr_wysokosc_min_udzial = 1.5", r"\[match\] filtr_wysokosc_min_udzial: udział z \[0, 1\]"),
    ("korekta_skali = true", "korekta_skali = 1", r"\[match\] korekta_skali: oczekiwano bool"),
    ("korekta_skali_okno_proc = 1.0", "korekta_skali_okno_proc = 0", r"\[match\] korekta_skali_okno_proc: okno korekty skali"),
    ("korekta_skali_ostrzezenie_proc = 0.3", "korekta_skali_ostrzezenie_proc = 1.5", r"\[match\] korekta_skali_ostrzezenie_proc: próg ostrzeżenia"),
    ("korekta_skali_pas_brzegu_mm = 2.0", "korekta_skali_pas_brzegu_mm = -1.0", r"\[match\] korekta_skali_pas_brzegu_mm: musi być >= 0"),  # brak klucza: wartość ze wzoru (DOMYSLNE_NOWYCH)
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
        sekcje = set(tomllib.load(f))
    wymagane = {"sciezki", "plytki", "match", "inspect", "synth", "excel", "ramki"}
    assert wymagane <= sekcje <= wymagane | set(UST.SEKCJE_OPCJONALNE)  # E3-A1: sekcja [sesja] jest opcjonalna


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
    p.write_text(stary.replace("\n[inspect]\n", '\n[inspect]\npas_brzegu_od = "linia"\n'), encoding="utf-8")
    assert UST.wczytaj_ustawienia(p)["inspect"]["pas_brzegu_od"] == "linia"
    p.write_text(stary.replace("\n[inspect]\n", '\n[inspect]\npas_brzegu_od = "obok"\n'), encoding="utf-8")
    with pytest.raises(UST.BladUstawien, match="pas_brzegu_od"):
        UST.wczytaj_ustawienia(p)


# --- E3-A1: klucze opcjonalne z wartoscia domyslna (plan etapu 3, sekcja 3.7) ---------------------
# Klucze WYMAGANE w stanie sprzed etapu 3 (commit fe66217). Etap 3 dodaje wylacznie klucze opcjonalne:
# stary lokalny ustawienia.toml ma dzialac bez recznych poprawek (R59 pkt 9.1).
WYMAGANE_PRZED_ETAPEM_3 = {
    "sciezki": ["baza", "folder_cyrkon", "folder_eksportu_skanera", "folder_millbox", "folder_prywatne", "log_excel"],
    "plytki": ["poranna", "wieczorna"],
    "match": ["filtr_objetosc_udzial", "filtr_wymiar_mm", "filtr_wymiar_udzial", "odleglosc_max_mm", "pewnosc_min", "prog_akceptacji_pokrycie",
              "prog_ostrzezenia_pokrycie", "pula_rano_dni_roboczych", "pula_wieczor_dni", "usun_z_puli_po_dniach"],
    "inspect": ["drgniecie_odchylka_mm", "drgniecie_udzial_obszaru", "drgniecie_udzial_w_komorce", "krawedz_pas_mm", "linia_min_udzial",
                "min_punktow_plamy", "pas_brzegu_mm", "poprawka_min_mm", "prog_glebokosci_mm", "srednica_max_mm", "srednica_min_mm",
                "wciecie_min_mm", "wciecie_pewne_mm"],
    "synth": ["szum_sigma_mm", "wspolczynnik_max", "wspolczynnik_min"],
    "excel": ["kolor_rgb", "kolumna_kuwety", "kolumna_nazwy", "kolumna_odhaczenia", "tryb_pytaj_przed_zapisem"],
    "ramki": ["poranna_host", "port", "wieczorna_host"],
}
NOWE_E3_A1 = {"sciezki": {"wyniki": "dane/wyniki"}, "sesja": {"operatorzy": [], "przechowuj_skany_dni": 0, "granica_doby_godz": 6, "zmiany_start_godz": [6, 14, 22], "ponowny_skan_okno_min": 60}}


def test_e3_a1_nie_dodaje_kluczy_wymaganych():
    wymagane = {s: sorted(set(klucze) - set(UST.DOMYSLNE_NOWYCH.get(s, {}))) for s, klucze in UST.SCHEMAT.items()}
    assert {s: k for s, k in wymagane.items() if k} == WYMAGANE_PRZED_ETAPEM_3
    assert set(UST.SEKCJE_OPCJONALNE) == {"sesja", "scanner", "silnik"}  # sekcja, ktorej wszystkie klucze maja wartosc domyslna, moze nie istniec w pliku (E3-A3a: scanner, silnik)
    for sekcja, klucze in NOWE_E3_A1.items():
        for k, v in klucze.items():
            assert k in UST.SCHEMAT[sekcja] and UST.DOMYSLNE_NOWYCH[sekcja][k] == v, (sekcja, k)


def _stary_plik(tmp_path, dopisek: str = ""):
    """Wzor ustawien cofniety do stanu sprzed E3-A1: bez sekcji [sesja] i bez nowych kluczy."""
    linie, w_sesji = [], False
    for linia in UST.PLIK_PRZYKLADU.read_text(encoding="utf-8").splitlines():
        if linia.startswith("["):
            w_sesji = linia.startswith("[sesja]")
        if not w_sesji and linia.split("=")[0].strip() != "wyniki":
            linie.append(linia)
    stary = "\n".join(linie) + "\n"
    assert "[sesja]" not in stary and "operatorzy" not in stary and "wyniki" not in stary and "[ramki]" in stary
    p = tmp_path / "ustawienia.toml"
    p.write_text(stary + dopisek, encoding="utf-8")
    return p


def test_k10_stary_plik_ustawien_bez_nowych_kluczy_wczytuje_sie(tmp_path):
    """Kryterium 10 E3-A1: plik ustawien sprzed etapu 3 wczytuje sie bez bledu, nowe klucze dostaja wartosci domyslne."""
    p = _stary_plik(tmp_path)
    ust = UST.wczytaj_ustawienia(p)
    assert ust["sesja"] == {"operatorzy": [], "przechowuj_skany_dni": 0, "granica_doby_godz": 6, "zmiany_start_godz": [6, 14, 22], "ponowny_skan_okno_min": 60} and ust["sciezki"]["wyniki"] == "dane/wyniki"
    assert ust == UST.wczytaj_ustawienia(UST.PLIK_PRZYKLADU)  # wzor ma nowe klucze wpisane z wartosciami domyslnymi
    ust["sesja"]["operatorzy"].append("Technik A")  # wartosc domyslna nie jest wspolna miedzy wczytaniami
    assert UST.wczytaj_ustawienia(p)["sesja"]["operatorzy"] == [] and UST.DOMYSLNE_NOWYCH["sesja"]["operatorzy"] == []
    # lokalny plik tej maszyny (na PC: kopia sprzed etapu 3) tez przechodzi i ma nowe klucze po wczytaniu
    lokalny = UST.wczytaj_ustawienia(UST.PLIK_USTAWIEN)
    assert isinstance(lokalny["sesja"]["operatorzy"], list) and lokalny["sciezki"]["wyniki"]


def test_nowe_klucze_wpis_w_pliku_ma_pierwszenstwo(tmp_path):
    p = _stary_plik(tmp_path, '\n[sesja]\noperatorzy = ["Technik A", "Technik B"]\n')
    ust = UST.wczytaj_ustawienia(p)
    assert ust["sesja"] == {"operatorzy": ["Technik A", "Technik B"], "przechowuj_skany_dni": 0, "granica_doby_godz": 6, "zmiany_start_godz": [6, 14, 22], "ponowny_skan_okno_min": 60}  # brakujacy klucz sekcji: domyslny
    p = _stary_plik(tmp_path, "\n[sesja]\nprzechowuj_skany_dni = 30\n")
    assert UST.wczytaj_ustawienia(p)["sesja"] == {"operatorzy": [], "przechowuj_skany_dni": 30, "granica_doby_godz": 6,
                                                   "zmiany_start_godz": [6, 14, 22], "ponowny_skan_okno_min": 60}
    # runda 2 (P5): doba robocza, zmiany i okno ponownego skanu sa ustawieniami
    p = _stary_plik(tmp_path, "\n[sesja]\ngranica_doby_godz = 7\nzmiany_start_godz = [7, 19]\nponowny_skan_okno_min = 30\n")
    sesja = UST.wczytaj_ustawienia(p)["sesja"]
    assert (sesja["granica_doby_godz"], sesja["zmiany_start_godz"], sesja["ponowny_skan_okno_min"]) == (7, [7, 19], 30)
    # runda 3 (D8): nazwy osob sa przycinane z bialych znakow przy wczytaniu
    p = _stary_plik(tmp_path, '\n[sesja]\noperatorzy = [" Technik A ", "Technik B\\t"]\n')
    assert UST.wczytaj_ustawienia(p)["sesja"]["operatorzy"] == ["Technik A", "Technik B"]


@pytest.mark.parametrize("dopisek,komunikat", [
    ('[sesja]\noperatorzy = "Technik A"\n', r"\[sesja\] operatorzy: oczekiwano list"),
    ('[sesja]\noperatorzy = ["Technik A", ""]\n', r"\[sesja\] operatorzy: lista niepustych"),
    ('[sesja]\noperatorzy = ["Technik A", 7]\n', r"\[sesja\] operatorzy: lista niepustych"),
    ('[sesja]\noperatorzy = ["Technik A", "Technik A"]\n', r"\[sesja\] operatorzy: lista niepustych"),
    ("[sesja]\nprzechowuj_skany_dni = -1\n", r"\[sesja\] przechowuj_skany_dni: musi"),
    ("[sesja]\nprzechowuj_skany_dni = 30.5\n", r"\[sesja\] przechowuj_skany_dni: oczekiwano int"),
    ("[sesja]\ngranica_doby_godz = 24\n", r"\[sesja\] granica_doby_godz: godzina"),
    ("[sesja]\ngranica_doby_godz = -1\n", r"\[sesja\] granica_doby_godz: godzina"),
    ("[sesja]\ngranica_doby_godz = 4.5\n", r"\[sesja\] granica_doby_godz: oczekiwano int"),
    ("[sesja]\nzmiany_start_godz = []\n", r"\[sesja\] zmiany_start_godz: niepusta lista"),
    ("[sesja]\nzmiany_start_godz = [14, 6, 22]\n", r"\[sesja\] zmiany_start_godz: niepusta lista"),
    ("[sesja]\nzmiany_start_godz = [6, 14, 24]\n", r"\[sesja\] zmiany_start_godz: niepusta lista"),
    ("[sesja]\nzmiany_start_godz = 6\n", r"\[sesja\] zmiany_start_godz: oczekiwano list"),
    ("[sesja]\nponowny_skan_okno_min = -5\n", r"\[sesja\] ponowny_skan_okno_min: musi"),
    # runda 3 (D8): okno > 0, pierwsza zmiana zaczyna dobe robocza, nazwy osob rozne takze po przycieciu
    ("[sesja]\nponowny_skan_okno_min = 0\n", r"\[sesja\] ponowny_skan_okno_min: musi być > 0"),
    ("[sesja]\nzmiany_start_godz = [7, 15, 23]\n", r"\[sesja\] zmiany_start_godz: pierwsza zmiana"),
    ("[sesja]\ngranica_doby_godz = 5\n", r"\[sesja\] zmiany_start_godz: pierwsza zmiana"),
    ('[sesja]\noperatorzy = ["Technik A", "Technik A "]\n', r"\[sesja\] operatorzy: lista niepustych"),
    ('[sesja]\noperatorzy = ["Technik A", "   "]\n', r"\[sesja\] operatorzy: lista niepustych"),
    ("[sesja]\nponowny_skan_okno_min = \"60\"\n", r"\[sesja\] ponowny_skan_okno_min: oczekiwano int"),
    ('[sesja]\noperator = "Technik A"\n', r"\[sesja\] operator: nieznany klucz"),
    ('[sesje]\noperatorzy = []\n', r"\[sesje\]: nieznana sekcja"),
])
def test_nowe_klucze_zla_wartosc_nadal_jest_bledem(tmp_path, dopisek, komunikat):
    p = _stary_plik(tmp_path, "\n" + dopisek)
    with pytest.raises(UST.BladUstawien, match=r"^ustawienia\.toml: " + komunikat):
        UST.wczytaj_ustawienia(p)


# --- E3-A3a: parametry scanner / silnik i sciezki programu "Stanowisko" - wylacznie klucze opcjonalne ---------------
NOWE_E3_A3A = {
    "sciezki": {"podglady": "dane/podglady", "pula_cache": "dane/pula_cache", "logi": "dane/logi"},
    "scanner": {"stabilizacja_ms": 300, "min_rozmiar_mb": 0.0, "min_trojkatow": 1, "wzorzec_pliku": "*.stl", "rekurencyjnie": True, "obserwator": "watchdog"},
    "silnik": {"limit_zadania_s": 600.0, "czekaj_na_plik_s": 60.0, "pamiec_linii": True, "ponow_plik_niedostepny": 3},
}


def _plik_sprzed_etapu_3(tmp_path, dopisek: str = ""):
    """Wzor ustawien cofniety do stanu sprzed etapu 3: bez sekcji [sesja], [scanner], [silnik] i bez nowych kluczy [sciezki]."""
    nowe = {k for kl in list(NOWE_E3_A1.values()) + list(NOWE_E3_A3A.values()) for k in kl}
    linie, pomijaj = [], False
    for linia in UST.PLIK_PRZYKLADU.read_text(encoding="utf-8").splitlines():
        if linia.startswith("["):
            pomijaj = linia.split("]")[0].strip("[") in UST.SEKCJE_OPCJONALNE
        if not pomijaj and linia.split("=")[0].strip() not in nowe:
            linie.append(linia)
    stary = "\n".join(linie) + "\n"
    assert not [s for s in ("[sesja]", "[scanner]", "[silnik]", "podglady =", "pula_cache =", "logi =", "stabilizacja_ms") if s in stary] and "[ramki]" in stary
    p = tmp_path / "ustawienia.toml"
    p.write_text(stary + dopisek, encoding="utf-8")
    return p


def test_e3_a3a_nowe_klucze_sa_opcjonalne_i_rowne_stalym_modulow(tmp_path):
    """Stary plik ustawien (sprzed etapu 3) wczytuje sie bez zmian, a wartosci domyslne sa tymi samymi liczbami, co stale
    modulow scanner i silnik (jedno zrodlo prawdy: podpiecie do ustawien nie zmienia zachowania)."""
    from stanowisko import scanner as SC, silnik as SI

    for sekcja, klucze in NOWE_E3_A3A.items():
        for k, v in klucze.items():
            assert k in UST.SCHEMAT[sekcja] and UST.DOMYSLNE_NOWYCH[sekcja][k] == v, (sekcja, k)
    assert set(UST.SCHEMAT["scanner"]) == set(NOWE_E3_A3A["scanner"]) and set(UST.SCHEMAT["silnik"]) == set(NOWE_E3_A3A["silnik"])
    d = UST.DOMYSLNE_NOWYCH
    assert (d["scanner"]["stabilizacja_ms"], d["scanner"]["min_rozmiar_mb"], d["scanner"]["min_trojkatow"], d["scanner"]["wzorzec_pliku"]) == (
        SC.STABILIZACJA_MS, SC.MIN_ROZMIAR_MB, SC.MIN_TROJKATOW, SC.WZORZEC_PLIKU)
    assert (d["silnik"]["limit_zadania_s"], d["silnik"]["czekaj_na_plik_s"]) == (SI.LIMIT_ZADANIA_S, SI.CZEKAJ_NA_PLIK_S)
    ust = UST.wczytaj_ustawienia(_plik_sprzed_etapu_3(tmp_path))
    assert ust == UST.wczytaj_ustawienia(UST.PLIK_PRZYKLADU)  # wzor ma nowe klucze wpisane z wartosciami domyslnymi
    assert ust["scanner"] == NOWE_E3_A3A["scanner"] and ust["silnik"] == NOWE_E3_A3A["silnik"]
    assert {k: ust["sciezki"][k] for k in NOWE_E3_A3A["sciezki"]} == NOWE_E3_A3A["sciezki"]
    # lokalny plik tej maszyny (na PC: kopia sprzed etapu 3, bez nowych kluczy) tez przechodzi
    lokalny = UST.wczytaj_ustawienia(UST.PLIK_USTAWIEN)
    assert lokalny["scanner"]["wzorzec_pliku"] and lokalny["silnik"]["limit_zadania_s"] > 0 and lokalny["sciezki"]["logi"]
    # wpis w pliku ma pierwszenstwo, brakujace klucze sekcji dostaja wartosci domyslne
    ust = UST.wczytaj_ustawienia(_plik_sprzed_etapu_3(tmp_path, '\n[scanner]\nstabilizacja_ms = 500\nwzorzec_pliku = "plytka_*.stl"\n\n[silnik]\nlimit_zadania_s = 300\n'))
    assert ust["scanner"] == {**NOWE_E3_A3A["scanner"], "stabilizacja_ms": 500, "wzorzec_pliku": "plytka_*.stl"}
    assert ust["silnik"] == {**NOWE_E3_A3A["silnik"], "limit_zadania_s": 300}


@pytest.mark.parametrize("dopisek, komunikat", [
    ("[scanner]\nstabilizacja_ms = -1\n", r"\[scanner\] stabilizacja_ms: musi"),
    ('[scanner]\nstabilizacja_ms = "300"\n', r"\[scanner\] stabilizacja_ms: oczekiwano float"),
    ("[scanner]\nmin_rozmiar_mb = -0.5\n", r"\[scanner\] min_rozmiar_mb: musi"),
    ("[scanner]\nmin_trojkatow = 0\n", r"\[scanner\] min_trojkatow: musi"),
    ("[scanner]\nmin_trojkatow = 1.5\n", r"\[scanner\] min_trojkatow: oczekiwano int"),
    ('[scanner]\nwzorzec_pliku = " "\n', r"\[scanner\] wzorzec_pliku: niepusty"),
    ('[scanner]\nobserwator = "inny"\n', r"\[scanner\] obserwator: dopuszczalne"),
    ('[scanner]\nrekurencyjnie = "tak"\n', r"\[scanner\] rekurencyjnie: oczekiwano bool"),
    ("[scanner]\nstabilizacja = 300\n", r"\[scanner\] stabilizacja: nieznany klucz"),
    ("[silnik]\nlimit_zadania_s = 0\n", r"\[silnik\] limit_zadania_s: musi"),
    ("[silnik]\nczekaj_na_plik_s = -1\n", r"\[silnik\] czekaj_na_plik_s: musi"),
    ("[silnik]\nponow_plik_niedostepny = -1\n", r"\[silnik\] ponow_plik_niedostepny: musi"),
    ("[silnik]\npamiec_linii = 1\n", r"\[silnik\] pamiec_linii: oczekiwano bool"),
    ("[silniki]\nlimit_zadania_s = 5\n", r"\[silniki\]: nieznana sekcja"),
])
def test_e3_a3a_zla_wartosc_nowego_klucza_jest_bledem(tmp_path, dopisek, komunikat):
    p = _plik_sprzed_etapu_3(tmp_path, "\n" + dopisek)
    with pytest.raises(UST.BladUstawien, match=r"^ustawienia\.toml: " + komunikat):
        UST.wczytaj_ustawienia(p)
