"""Testy qc.metryki: jedno polecenie, jedna strona metryk odbiorczych (sekcja 14 planu).

Dane wylacznie syntetyczne (qc.syntetyka). Wynik `policz(u, "szybko", 1)` liczony raz w fixture
session; testy sprawdzaja strukture slownika, spojnosc lancucha plate -> match -> inspect i progi.

Struktura slownika (kontrakt testow):
- plytka: blad_wyrownania_max_mm, blad_wyrownania_sredni_mm, numery {ok, zle, brak},
  fragmenty {praca, puste, podwojne, poza_gniazdem} x {wynik, prawda};
- identyfikacja: wieczor / rano / razem, kazde {fragmenty, top1, top2, pewny, dwuznaczny, brak,
  falszywe_pewny, udzial_top1, udzial_top2};
- ubytki: klasy {"0.2-0.3", "0.3-0.4", "0.4-0.6"} i sigma {"0.02", ...}, kazde {wykryte, pominiete,
  falszywe, udzial_wykrytych}; udzial_wykrytych_od_0_3, udzial_prac_z_falszywym_alarmem,
  sprawdzone_fragmenty, sprawdzone_rano;
- czasy: na_plytke_s, na_fragment_s, calosc_s;
- wersja, ziarno, tryb.
Kazdy klucz zaczynajacy sie od "udzial" to liczba w [0, 1].
"""

import copy
import json
import subprocess
import sys
import time

import pytest

from qc.ustawienia import katalog_repo, wczytaj

KLASY = ("0.2-0.3", "0.3-0.4", "0.4-0.6")


def _metryki():
    import qc.metryki

    return qc.metryki


@pytest.fixture(scope="session")
def ustawienia():
    return wczytaj(katalog_repo() / "ustawienia.toml")


@pytest.fixture(scope="session")
def wynik_szybko(ustawienia):
    return _metryki().policz(ustawienia, "szybko", 1)


def _udzialy(d, sciezka=""):
    """Lista (sciezka, wartosc) wszystkich kluczy "udzial*" w zagniezdzonym slowniku."""
    wynik = []
    for klucz, wartosc in d.items():
        s = f"{sciezka}.{klucz}" if sciezka else str(klucz)
        if isinstance(wartosc, dict):
            wynik += _udzialy(wartosc, s)
        elif str(klucz).startswith("udzial"):
            wynik.append((s, wartosc))
    return wynik


def _dobry():
    """Minimalny slownik z wartosciami powyzej progow odbiorczych."""
    return {
        "identyfikacja": {"razem": {"udzial_top1": 0.95}},
        "ubytki": {"udzial_wykrytych_od_0_3": 0.90, "udzial_prac_z_falszywym_alarmem": 0.05},
    }


# --- 1 -------------------------------------------------------------------------


def test_szybko_json(wynik_szybko):
    import qc

    w = wynik_szybko
    for klucz in ("plytka", "identyfikacja", "ubytki", "czasy", "wersja", "ziarno", "tryb"):
        assert klucz in w, klucz
    assert w["wersja"] == qc.__version__
    assert w["ziarno"] == 1
    assert w["tryb"] == "szybko"
    assert tuple(w["ubytki"]["klasy"]) == KLASY
    for tryb in ("wieczor", "rano", "razem"):
        assert tryb in w["identyfikacja"], tryb
    udzialy = _udzialy(w)
    assert len(udzialy) >= 10
    for sciezka, wartosc in udzialy:
        assert 0.0 <= wartosc <= 1.0, (sciezka, wartosc)
    assert w["czasy"]["na_fragment_s"] > 0
    assert w["czasy"]["na_plytke_s"] > 0
    assert w["czasy"]["calosc_s"] > 0
    json.dumps(w)  # serializowalny bez konwersji


# --- 2 -------------------------------------------------------------------------


def test_cli(tmp_path):
    plik = tmp_path / "m.json"
    proces = subprocess.run(
        [sys.executable, "-m", "qc.metryki", "--szybko", "--wyjscie", str(plik)],
        cwd=katalog_repo(), capture_output=True, text=True, timeout=300,
    )
    assert proces.returncode in (0, 3), proces.stderr
    linie = proces.stdout.splitlines()
    assert len(linie) <= 60, len(linie)
    assert "top-1" in proces.stdout
    assert "wykryte" in proces.stdout
    dane = json.loads(plik.read_text(encoding="utf-8"))
    for klucz in ("plytka", "identyfikacja", "ubytki", "czasy", "wersja", "ziarno", "tryb"):
        assert klucz in dane, klucz
    assert dane["tryb"] == "szybko"


# --- 3 -------------------------------------------------------------------------


def test_progi_odbiorcze():
    m = _metryki()
    assert m.PROGI_ODBIORCZE == {
        "top1": 0.85, "wykryte_od_0_3": 0.80, "prace_z_falszywym_alarmem": 0.15,
    }
    assert m.ocen(_dobry()) == (0, [])

    zly = copy.deepcopy(_dobry())
    zly["identyfikacja"]["razem"]["udzial_top1"] = 0.80
    zly["ubytki"]["udzial_wykrytych_od_0_3"] = 0.70
    zly["ubytki"]["udzial_prac_z_falszywym_alarmem"] = 0.20
    kod, nazwy = m.ocen(zly)
    assert kod == 3
    assert sorted(nazwy) == sorted(m.PROGI_ODBIORCZE)

    for sciezka, wartosc, nazwa in (
        (("identyfikacja", "razem", "udzial_top1"), 0.84, "top1"),
        (("ubytki", "udzial_wykrytych_od_0_3"), 0.79, "wykryte_od_0_3"),
        (("ubytki", "udzial_prac_z_falszywym_alarmem"), 0.16, "prace_z_falszywym_alarmem"),
    ):
        d = copy.deepcopy(_dobry())
        cel = d
        for k in sciezka[:-1]:
            cel = cel[k]
        cel[sciezka[-1]] = wartosc
        assert m.ocen(d) == (3, [nazwa]), nazwa

    # wartosci rowne progom = odbior zaliczony
    rowny = copy.deepcopy(_dobry())
    rowny["identyfikacja"]["razem"]["udzial_top1"] = 0.85
    rowny["ubytki"]["udzial_wykrytych_od_0_3"] = 0.80
    rowny["ubytki"]["udzial_prac_z_falszywym_alarmem"] = 0.15
    assert m.ocen(rowny) == (0, [])


# --- 4 -------------------------------------------------------------------------


def test_lancuch_spojny(wynik_szybko):
    w = wynik_szybko
    ident = w["identyfikacja"]
    fragmenty_praca = w["plytka"]["fragmenty"]["praca"]["wynik"]
    assert fragmenty_praca > 0
    assert ident["wieczor"]["fragmenty"] + ident["rano"]["fragmenty"] == fragmenty_praca
    assert ident["razem"]["fragmenty"] == fragmenty_praca
    for tryb in ("wieczor", "rano"):
        t = ident[tryb]
        assert t["pewny"] + t["dwuznaczny"] + t["brak"] == t["fragmenty"], tryb
    # inspect tylko na fragmentach "pewny" wieczornych, rano nic
    assert w["ubytki"]["sprawdzone_fragmenty"] == ident["wieczor"]["pewny"]
    assert w["ubytki"]["sprawdzone_rano"] == 0
    # suma po klasach = suma po sigma
    for pole in ("wykryte", "pominiete", "falszywe"):
        po_klasach = sum(k[pole] for k in w["ubytki"]["klasy"].values())
        po_sigma = sum(s[pole] for s in w["ubytki"]["sigma"].values())
        assert po_klasach == po_sigma, pole


# --- 5 -------------------------------------------------------------------------


def test_szybko_wyniki(wynik_szybko):
    w = wynik_szybko
    assert w["identyfikacja"]["razem"]["udzial_top1"] >= 0.9
    assert w["ubytki"]["udzial_wykrytych_od_0_3"] >= 0.85
    assert w["plytka"]["numery"] == {"ok": 3, "zle": 0, "brak": 0}
    ubytki_prawdy = sum(k["wykryte"] + k["pominiete"] for k in w["ubytki"]["klasy"].values())
    assert ubytki_prawdy >= 15  # ok. 20 ubytkow w trybie szybko
    assert _metryki().ocen(w) == (0, [])


# --- 6 -------------------------------------------------------------------------


@pytest.mark.wolne
def test_pelne(ustawienia):
    m = _metryki()
    start = time.perf_counter()
    w = m.policz(ustawienia, "pelne", 1)
    czas = time.perf_counter() - start
    print(f"\nmetryki pelne: {czas:.0f} s")
    assert w["tryb"] == "pelne"
    assert w["plytka"]["fragmenty"]["praca"]["prawda"] >= 150
    assert set(w["ubytki"]["sigma"]) == {"0.02", "0.03", "0.04"}
    assert m.ocen(w) == (0, [])
    assert czas <= 20 * 60


# --- 7-11. poprawki po recenzji ---------------------------------------------------
#
# Dodatkowe pola: ubytki.ubytki_bez_inspekcji_klasy {klasa: n}, ubytki.udzial_wykrytych_od_0_3_wszystkie
# (prog odbiorczy; ukruszenia prac bez "pewny" = niewykryte); identyfikacja.<tryb>.prace (mianownik top-1 =
# prace "praca" z prawdy) i .powtorzone; prace = lista {plytka, tryb, gniazdo, projekt_id, pewnosc, top1,
# ukruszenia, sprawdzona}. API: powtorzenia(tryb, ziarno) -> {"wieczor"/"rano": {powtorzone, prace}}.


def test_bez_inspekcji(wynik_szybko):
    ub = wynik_szybko["ubytki"]
    bez = ub["ubytki_bez_inspekcji_klasy"]
    assert tuple(bez) == KLASY
    assert sum(bez.values()) == ub["ubytki_bez_inspekcji"]
    oczekiwane = sum(p["ukruszenia"] for p in wynik_szybko["prace"]
                     if p["tryb"] == "wieczor" and p["pewnosc"] != "pewny")
    assert ub["ubytki_bez_inspekcji"] == oczekiwane
    assert all(not p["sprawdzona"] for p in wynik_szybko["prace"] if p["pewnosc"] != "pewny")
    assert all(not p["sprawdzona"] for p in wynik_szybko["prace"] if p["tryb"] == "rano")
    wyk = sum(ub["klasy"][k]["wykryte"] for k in KLASY[1:])
    pom = sum(ub["klasy"][k]["pominiete"] for k in KLASY[1:])
    bez_od_0_3 = sum(bez[k] for k in KLASY[1:])
    assert ub["udzial_wykrytych_od_0_3_wszystkie"] == pytest.approx(wyk / (wyk + pom + bez_od_0_3))
    assert ub["udzial_wykrytych_od_0_3_wszystkie"] <= ub["udzial_wykrytych_od_0_3"]


def test_prog_od_wszystkich():
    m = _metryki()
    d = copy.deepcopy(_dobry())
    d["ubytki"]["udzial_wykrytych_od_0_3_wszystkie"] = 0.79
    assert m.ocen(d) == (3, ["wykryte_od_0_3"])
    d["ubytki"]["udzial_wykrytych_od_0_3_wszystkie"] = 0.80
    d["ubytki"]["udzial_wykrytych_od_0_3"] = 0.70  # informacyjna (prace zidentyfikowane), nie prog
    assert m.ocen(d) == (0, [])


def test_mianownik_top1(wynik_szybko):
    ident = wynik_szybko["identyfikacja"]
    prawda_praca = wynik_szybko["plytka"]["fragmenty"]["praca"]["prawda"]
    assert ident["razem"]["prace"] == prawda_praca
    assert ident["wieczor"]["prace"] + ident["rano"]["prace"] == prawda_praca
    assert len(wynik_szybko["prace"]) == prawda_praca
    for tryb in ("wieczor", "rano", "razem"):
        t = ident[tryb]
        assert t["pewny"] + t["dwuznaczny"] + t["brak"] == t["prace"], tryb
        assert t["udzial_top1"] == pytest.approx(t["top1"] / t["prace"]), tryb


@pytest.mark.parametrize("tryb", ["szybko", "pelne"])
def test_powtorki(tryb):
    p = _metryki().powtorzenia(tryb, 1)
    for t in ("wieczor", "rano"):
        assert p[t]["prace"] > 0, t
        assert p[t]["powtorzone"] <= 0.10 * p[t]["prace"], (t, p[t])


def test_powtorki_na_stronie(wynik_szybko):
    p = _metryki().powtorzenia("szybko", 1)
    for t in ("wieczor", "rano"):
        assert wynik_szybko["identyfikacja"][t]["powtorzone"] == p[t]["powtorzone"], t


def test_watki_omp():
    import os

    kod = "import os, qc.metryki as m; print(os.environ['OMP_NUM_THREADS'], m.WATKI)"
    env = {k: v for k, v in os.environ.items() if k != "OMP_NUM_THREADS"}
    wynik = subprocess.run([sys.executable, "-c", kod], cwd=katalog_repo(), env=env,
                           capture_output=True, text=True, timeout=120)
    assert wynik.returncode == 0, wynik.stderr
    omp, watki = wynik.stdout.split()
    assert int(omp) == max(1, (os.cpu_count() or 1) // int(watki))
    env["OMP_NUM_THREADS"] = "3"
    wynik = subprocess.run([sys.executable, "-c", kod], cwd=katalog_repo(), env=env,
                           capture_output=True, text=True, timeout=120)
    assert wynik.stdout.split()[0] == "3"  # ustawienie uzytkownika ma pierwszenstwo
