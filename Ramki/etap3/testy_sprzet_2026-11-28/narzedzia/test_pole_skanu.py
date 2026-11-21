"""Testy narzedzia pole_skanu.py (E3-S1). Tylko skany sztuczne; pisza wylacznie do tmp_path; bez internetu.

Uruchomienie (katalog Ramki/stanowisko):
    python -m pytest ../etap3/testy_sprzet_2026-11-28/narzedzia -q -p no:cacheprovider
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

STANOWISKO = Path(__file__).resolve().parents[3] / "stanowisko"
for _p in (STANOWISKO, Path(__file__).resolve().parent):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import stanowisko  # noqa: E402, F401, I001 - przed numpy / trimesh (E3-A11w)

import numpy as np  # noqa: E402
import pytest  # noqa: E402
import trimesh  # noqa: E402

import pole_skanu as PS  # noqa: E402
from stanowisko import synth as S  # noqa: E402
from stanowisko import uklad as U  # noqa: E402
from stanowisko import ustawienia as UST  # noqa: E402


@pytest.fixture(scope="module")
def ust() -> dict:
    return UST.wczytaj_ustawienia(STANOWISKO / "ustawienia.przyklad.toml")


def _skan(ust: dict, katalog: Path, plytka: str, numer: int, pole: float | None, seed: int) -> Path:
    """Sztuczny skan PUSTEJ plytki generatorem programu, w losowym ukladzie skanera, przyciety do pola."""
    uk = U.wczytaj(plytka, UST.katalog_plytki(ust, plytka))
    opcje = S.Opcje.z_toml(ust, plytka, prace_na_plytce=0, poza_uklad=True, pole=pole)
    skan, prawda = S.generuj_plytke(uk, numer, [], np.random.default_rng(seed), opcje, seed)
    katalog.mkdir(parents=True, exist_ok=True)
    plik, _ = S.zapisz(skan, prawda, katalog, f"skan_{plytka}_n{numer}_p{int(pole or 0)}")
    return plik


def test_najmniejsze_kolo_znane_przypadki():
    c, r = PS.najmniejsze_kolo(np.array([[0.0, 0.0], [10.0, 0.0]]))
    assert np.allclose(c, [5, 0]) and r == pytest.approx(5.0)
    kat = np.linspace(0, 2 * math.pi, 400, endpoint=False)
    okrag = np.c_[3 + 40 * np.cos(kat), -2 + 40 * np.sin(kat)]
    wnetrze = np.random.default_rng(1).uniform(-20, 20, (500, 2))
    c, r = PS.najmniejsze_kolo(np.vstack([wnetrze, okrag]))
    assert np.allclose(c, [3, -2], atol=1e-6) and r == pytest.approx(40.0, abs=1e-6)
    # trojkat rozwartokatny: kolo na najdluzszym boku, nie opisane na trzech punktach
    c, r = PS.najmniejsze_kolo(np.array([[0.0, 0.0], [10.0, 0.0], [5.0, 1.0]]))
    assert r == pytest.approx(5.0)


def test_odleglosc_od_obrysu_kwadrat_i_kolo(ust):
    kw = U.wczytaj("wieczorna", UST.katalog_plytki(ust, "wieczorna"))
    ok = U.wczytaj("okragla_wieczorna", UST.katalog_plytki(ust, "okragla_wieczorna"))
    x, y = np.array([0.0, 47.0, 48.0, 50.0]), np.array([0.0, 0.0, 48.0, 0.0])
    assert np.allclose(PS.odleglosc_od_obrysu(kw, x, y), [48, 1, 0, -2])
    assert np.allclose(PS.odleglosc_od_obrysu(ok, np.array([0.0, 49.0, 0.0]), np.array([0.0, 0.0, -51.0])), [49.3559, 1, -1], atol=1e-3)
    a = math.radians(-45)  # sciecie plytki okraglej: 49,36 mm od srodka na kierunku -45 st.
    assert PS.odleglosc_od_obrysu(ok, np.array([49.9 * math.cos(a)]), np.array([49.9 * math.sin(a)]))[0] < 0
    assert PS.srednica_opisana(kw) == pytest.approx(96 * math.sqrt(2)) and PS.srednica_opisana(ok) == pytest.approx(100.0)


def test_zakresy_kierunkow():
    assert PS._zakresy([]) == []
    assert PS._zakresy([0, 1, 2]) == ["0-15 st."]
    assert PS._zakresy([70, 71, 0, 1]) == ["350-10 st."]
    assert PS._zakresy([4, 5, 20]) == ["20-30 st.", "100-105 st."]


def test_pole_mniejsze_niz_plytka_kwadratowa_daje_srednice_pola(ust, tmp_path):
    """Kwadrat 96 mm, pole 110 mm: srednica danych = pole (blad do 1 mm); widac 2 z 4 dolkow kwadratu; brzegu nie widac w rogach."""
    w, P, uk = PS.zmierz(_skan(ust, tmp_path, "wieczorna", 1, 110.0, 21), ust)
    assert w["rozpoznano"] and w["uklad"] == "wieczorna" and uk.shape == "square"
    assert w["srednica_danych_mm"] == pytest.approx(110.0, abs=1.0)
    assert w["pole_wieksze_niz_plytka"] is False
    assert 0 < w["brzeg_widoczny_kierunkow"] < PS.KIERUNKOW and w["brzeg_brak_w_kierunkach"]
    widac = sum(d["stan"] != "poza skanem" for d in w["dolki"]["wieczorna"])
    assert 1 <= widac <= 3  # dolki kwadratu leza 52,5-57,6 mm od srodka; pole 110 mm obejmuje tylko blizsze
    assert w["stozki"]["dopasowane"] == 3
    tekst = "\n".join(PS.raport(w))
    assert "POLE SKANERA MA OK. 11" in tekst and tekst.isascii()


def test_plytka_okragla_cala_w_polu(ust, tmp_path):
    """Kolo 100 mm, bez ograniczenia pola: 'co najmniej', brzeg we wszystkich kierunkach, 4 dolki, numer 8 z dolkow."""
    w, P, uk = PS.zmierz(_skan(ust, tmp_path, "okragla_wieczorna", 8, None, 22), ust)
    assert w["rozpoznano"] and w["uklad"] == "okragla_wieczorna"
    assert w["pole_wieksze_niz_plytka"] is True and w["srednica_danych_mm"] == pytest.approx(100.0, abs=1.0)
    assert w["brzeg_widoczny_kierunkow"] == PS.KIERUNKOW
    d = w["dolki"]["okragla_wieczorna"]
    assert [x["stan"] != "poza skanem" for x in d] == [True] * 4
    assert [x["stan"] for x in d if x["stan"].endswith("wglebienie")] and w["numer_z_dolkow"] == 8
    assert "CO NAJMNIEJ" in "\n".join(PS.raport(w))


def test_pole_95_okragla_brzegu_nie_widac(ust, tmp_path):
    w, _, _ = PS.zmierz(_skan(ust, tmp_path, "okragla_wieczorna", 8, 95.0, 23), ust)
    assert w["rozpoznano"] and w["srednica_danych_mm"] == pytest.approx(95.0, abs=1.0)
    assert w["brzeg_widoczny_kierunkow"] == 0 and w["pole_wieksze_niz_plytka"] is False
    assert w["zasieg_tam_gdzie_brak_brzegu_mm"]["max"] < 50.0


def test_pole_80_plytka_nierozpoznana_ale_srednica_podana(ust, tmp_path):
    """Pole 80 mm nie obejmuje stozkow: program nie rozpoznaje plytki, narzedzie mimo to podaje srednice i kod 3."""
    plik = _skan(ust, tmp_path, "okragla_wieczorna", 8, 80.0, 24)
    w, P, uk = PS.zmierz(plik, ust)
    assert not w["rozpoznano"] and P is None and uk is None
    assert w["srednica_danych_mm"] == pytest.approx(80.0, abs=1.5)
    assert PS.main([str(plik), "--ustawienia", str(STANOWISKO / "ustawienia.przyklad.toml"), "--wynik", str(tmp_path / "wynik")]) == 3
    tekst = (tmp_path / "wynik" / f"{plik.stem}_pole.txt").read_text(encoding="ascii")
    assert "NIE ROZPOZNANA" in tekst and "94 mm" in tekst
    assert not (tmp_path / "wynik" / f"{plik.stem}_pole.png").exists()


def test_plaski_arkusz_wiekszy_niz_pole_daje_srednice_pola(ust, tmp_path):
    """Sposob na pole wieksze niz plytka: plaski przedmiot wiekszy niz pole (np. karton). Tu: siatka 160 x 160 przycieta do kola 105 mm."""
    n = 161
    gx, gy = np.meshgrid(np.linspace(-80, 80, n), np.linspace(-80, 80, n))
    v = np.c_[gx.ravel(), gy.ravel(), np.zeros(n * n)]
    i = np.arange(n * n).reshape(n, n)
    f = np.vstack([np.c_[i[:-1, :-1].ravel(), i[:-1, 1:].ravel(), i[1:, :-1].ravel()], np.c_[i[1:, :-1].ravel(), i[:-1, 1:].ravel(), i[1:, 1:].ravel()]])
    srodki = v[f].mean(axis=1)
    f = f[np.hypot(srodki[:, 0] - 4.0, srodki[:, 1] + 3.0) <= 52.5]
    m = trimesh.Trimesh(v, f, process=False)
    m.apply_transform(trimesh.transformations.rotation_matrix(0.3, [1, 0.2, 0], [5, 5, 5]))
    plik = tmp_path / "arkusz.stl"
    m.export(plik)
    w, _, _ = PS.zmierz(plik, ust)
    assert not w["rozpoznano"]
    assert w["srednica_danych_mm"] == pytest.approx(105.0, abs=1.5)


def test_main_zapisuje_trzy_pliki_i_kod_0(ust, tmp_path):
    plik = _skan(ust, tmp_path, "okragla_poranna", 9, None, 25)
    assert PS.main([str(plik), "--ustawienia", str(STANOWISKO / "ustawienia.przyklad.toml"), "--wynik", str(tmp_path / "w")]) == 0
    for r in ("txt", "json", "png"):
        assert (tmp_path / "w" / f"{plik.stem}_pole.{r}").stat().st_size > 100
    assert PS.main([str(tmp_path / "nie_ma.stl")]) == 2
