"""Testy narzedzia pole_skanu.py (E3-S1). Tylko skany sztuczne; pisza wylacznie do tmp_path; bez internetu.

Uruchomienie (katalog Ramki/stanowisko):
    python -m pytest ../etap3/testy_sprzet_2026-11-28/narzedzia -q -p no:cacheprovider
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

STANOWISKO = Path(__file__).resolve().parents[3] / "stanowisko"
for _p in (STANOWISKO, STANOWISKO / "narzedzia", Path(__file__).resolve().parent):
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
    assert w["pole_kolowe_mm"] == pytest.approx(110.0, abs=1.0)  # okrag dopasowany do koncow danych (E3-S2a, U1)
    assert "POLE SKANERA MA OK. 1" in tekst and "POLE NIE JEST KOLEM" not in tekst and tekst.isascii()


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
    assert w["pole_kolowe_mm"] == pytest.approx(95.0, abs=1.0)
    tekst = "\n".join(PS.raport(w))  # U9 (a): pole 95 mm nie obejmuje scianki bocznej plytki 100 mm
    assert w["scianka_boczna"]["widoczna"] is False and "Scianka boczna plytki: NIE widac" in tekst
    assert "scianka boczna: NIE widac" in tekst and "Cala plytka" not in tekst


def test_pole_80_plytka_nierozpoznana_ale_srednica_podana(ust, tmp_path):
    """Pole 80 mm nie obejmuje stozkow: program nie rozpoznaje plytki, narzedzie mimo to podaje srednice i kod 3."""
    plik = _skan(ust, tmp_path, "okragla_wieczorna", 8, 80.0, 24)
    w, P, uk = PS.zmierz(plik, ust)
    assert not w["rozpoznano"] and P is None and uk is None
    assert w["srednica_danych_mm"] == pytest.approx(80.0, abs=1.5)
    assert PS.main([str(plik), "--ustawienia", str(STANOWISKO / "ustawienia.przyklad.toml"), "--wynik", str(tmp_path / "wynik")]) == 3
    (txt,) = list((tmp_path / "wynik").glob(f"{plik.stem}_*_pole.txt"))
    tekst = txt.read_text(encoding="ascii")
    assert "NIE ROZPOZNANA" in tekst and "94 mm" in tekst and "Dane mieszcza sie w kole o srednicy ok. 8" in tekst
    assert not list((tmp_path / "wynik").glob("*_pole.png"))


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
        (wynik,) = list((tmp_path / "w").glob(f"{plik.stem}_*_pole.{r}"))
        assert wynik.stat().st_size > 100
    assert PS.main([str(tmp_path / "nie_ma.stl")]) == 2


# ----------------------------------------------------------------------------- E3-S2a: poprawki po recenzji PR #54 (U1-U5, U9, U10, U12)
def _pelny(ust: dict, plytka: str, numer: int, seed: int) -> tuple[trimesh.Trimesh, object, np.random.Generator]:
    """Pelny skan sztuczny PUSTEJ plytki W UKLADZIE PLYTKI (bez pola, bez losowego polozenia) - do wlasnego przyciecia."""
    uk = U.wczytaj(plytka, UST.katalog_plytki(ust, plytka))
    rng = np.random.default_rng(seed)
    opcje = S.Opcje.z_toml(ust, plytka, prace_na_plytce=0, poza_uklad=False, pole=None)
    skan, _ = S.generuj_plytke(uk, numer, [], rng, opcje, seed)
    return skan, uk, rng


def _zapisz(skan: trimesh.Trimesh, rng, plik: Path) -> Path:
    skan.apply_transform(S.losowa_poza_skanu(rng))  # losowe polozenie w ukladzie skanera
    plik.parent.mkdir(parents=True, exist_ok=True)
    skan.export(plik)
    return plik


def _prostokat(skan: trimesh.Trimesh, dx: float, dy: float) -> trimesh.Trimesh:
    """Pole PROSTOKATNE dx x dy wokol srodka plytki: cztery ciecia plaszczyzna (trojkaty na granicy sa dzielone)."""
    for normalna, punkt in (([1, 0, 0], [-dx / 2, 0, 0]), ([-1, 0, 0], [dx / 2, 0, 0]), ([0, 1, 0], [0, -dy / 2, 0]), ([0, -1, 0], [0, dy / 2, 0])):
        v, f, _ = trimesh.intersections.slice_faces_plane(skan.vertices, skan.faces, np.array(normalna, dtype=float), np.array(punkt, dtype=float))
        skan = trimesh.Trimesh(v, f, process=False)
    return skan


def _siatka_plaska(bok: float, krok: float = 1.0, z: float = 0.0) -> tuple[np.ndarray, np.ndarray]:
    n = int(bok / krok) + 1
    gx, gy = np.meshgrid(np.linspace(-bok / 2, bok / 2, n), np.linspace(-bok / 2, bok / 2, n))
    v = np.c_[gx.ravel(), gy.ravel(), np.full(n * n, z)]
    i = np.arange(n * n).reshape(n, n)
    f = np.vstack([np.c_[i[:-1, :-1].ravel(), i[:-1, 1:].ravel(), i[1:, :-1].ravel()], np.c_[i[1:, :-1].ravel(), i[:-1, 1:].ravel(), i[1:, 1:].ravel()]])
    return v, f


def test_prostokat_najwezszy_okrag_dopasowany_i_nazwy_rodzajow():
    rng = np.random.default_rng(3)
    xy = rng.uniform([-50, -40], [50, 40], (4000, 2))
    a = math.radians(27)
    obr = xy @ np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]]).T
    najw, wpoprz = PS.prostokat_najwezszy(obr)
    assert najw == pytest.approx(80.0, abs=0.5) and wpoprz == pytest.approx(100.0, abs=0.5)
    kat = np.linspace(0.3, 1.4, 20)  # luk 63 stopni okregu fi 120 o srodku (15, -4)
    sr, r, reszty = PS.okrag_dopasowany(np.c_[15 + 60 * np.cos(kat), -4 + 60 * np.sin(kat)])
    assert np.allclose(sr, [15, -4], atol=1e-6) and r == pytest.approx(60.0) and reszty.max() < 1e-6
    assert PS.opis_rodzaju("wieczorna") == "kwadratowa, wieczorna"
    assert PS.opis_rodzaju("okragla_ramkowa_poranna") == "okragla ramkowa (do ramki), poranna"
    assert PS.opis_rodzaju("okragla_wieczorna") == "okragla testowa (poza ramka), wieczorna"
    assert PS.opis_rodzaju("poranna_r54") == "kwadratowa, poranna, stary rozstaw R54"
    assert PS.drugi_ksztalt("okragla_ramkowa_wieczorna") == "wieczorna" and PS.drugi_ksztalt("poranna") == "okragla_poranna"


def test_u1_plaski_arkusz_w_polu_prostokatnym_nie_dostaje_srednicy_kola(ust, tmp_path):
    """Recenzja PR #54 proba 9: karton w polu 100 x 80 mm dawal 'mieszcza sie w kole o srednicy ok. 127,9 mm'."""
    v, f = _siatka_plaska(160.0)
    srodki = v[f].mean(axis=1)
    f = f[(np.abs(srodki[:, 0]) <= 50.0) & (np.abs(srodki[:, 1]) <= 40.0)]
    m = trimesh.Trimesh(v, f, process=False)
    m.remove_unreferenced_vertices()
    m.apply_transform(trimesh.transformations.rotation_matrix(0.4, [0.1, 0.2, 1], [5, 5, 5]))
    plik = tmp_path / "karton.stl"
    m.export(plik)
    w, _, _ = PS.zmierz(plik, ust)
    assert not w["rozpoznano"] and w["dane_sa_kolem"] is False
    assert w["dane_najwezej_mm"] == pytest.approx(80.0, abs=1.5) and w["dane_w_poprzek_mm"] == pytest.approx(100.0, abs=1.5)
    tekst = "\n".join(PS.raport(w))
    assert "DANE NIE SA KOLEM: 8" in tekst and "mieszcza sie w kole" not in tekst and "12" + "7," not in tekst and "128" not in tekst
    assert "pole: dane najwezej 8" in tekst and tekst.isascii()


def test_u1_kwadrat_w_polu_prostokatnym_bez_zdania_o_srednicy_pola(ust, tmp_path):
    """Recenzja PR #54 proba 10: kwadrat w polu 130 x 90 mm dawal 'POLE SKANERA MA OK. 134,4 mm'."""
    skan, uk, rng = _pelny(ust, "wieczorna", 1, 31)
    w, _, _ = PS.zmierz(_zapisz(_prostokat(skan, 130.0, 90.0), rng, tmp_path / "prostokat.stl"), ust)
    assert w["rozpoznano"] and w["uklad"] == "wieczorna"
    assert w["pole_kolowe_mm"] is None and w["cala_plytka_w_skanie"] is False
    assert w["dane_najwezej_mm"] == pytest.approx(90.0, abs=1.5)
    assert w["okrag_wpisany_wokol_srodka_plytki_mm"] == pytest.approx(90.0, abs=1.5)
    tekst = "\n".join(PS.raport(w))
    assert "POLE SKANERA MA OK." not in tekst and "POLE NIE JEST KOLEM" in tekst and "Cala plytka" not in tekst
    assert "pola kolowego nie da sie podac" in tekst


def test_u2_pole_przesuniete_plytka_nie_jest_cala_w_skanie(ust, tmp_path):
    """Recenzja PR #54 proba 7: plytka okragla 100 mm, pole kolowe 120 mm przesuniete o 15 mm - bylo 'Cala plytka ... jest w skanie'."""
    skan, uk, rng = _pelny(ust, "okragla_wieczorna", 8, 32)
    skan = S.przytnij_do_kola(skan, np.array([15.0, 0.0]), 60.0)
    w, _, _ = PS.zmierz(_zapisz(skan, rng, tmp_path / "przesuniete.stl"), ust)
    assert w["rozpoznano"] and w["uklad"] == "okragla_wieczorna"
    assert 40 <= w["brzeg_widoczny_kierunkow"] < PS.KIERUNKOW and w["cala_plytka_w_skanie"] is False
    assert w["pole_kolowe_mm"] == pytest.approx(120.0, abs=2.0)
    assert w["pole_dopasowanie"]["srodek_od_srodka_plytki_mm"] == pytest.approx(15.0, abs=1.5)
    tekst = "\n".join(PS.raport(w))
    assert "Cala plytka" not in tekst and "CO NAJMNIEJ" not in tekst
    assert f"Plytka NIE jest cala w skanie: brzeg widac w {w['brzeg_widoczny_kierunkow']} z 72 kierunkow" in tekst
    assert "przesun plytke na srodek pola i zeskanuj ponownie" in tekst


def test_u3_miara_rowka_na_chmurze_z_rowkiem_i_bez():
    """Miara 'scianka cofa sie w pasie rowka' na chmurze punktow scianki: z rowkiem 0,8 mm = 72 kierunki, bez = 0."""
    rng = np.random.default_rng(5)
    n = 60_000
    kat = rng.integers(0, PS.KIERUNKOW, n)
    gl = rng.uniform(0.5, 4.0, n)
    szum = rng.normal(0, 0.02, n)
    z_rowkiem = PS.uskok_scianki(np.where((gl >= 1.5) & (gl <= 2.5), 0.8, 0.0) + szum, gl, kat)
    assert z_rowkiem["kierunkow_z_uskokiem"] == PS.KIERUNKOW and z_rowkiem["uskok_mediana_mm"] == pytest.approx(0.8, abs=0.05)
    bez = PS.uskok_scianki(0.5 + szum, gl, kat)  # scianka rowna, 0,5 mm wewnatrz obrysu nominalnego (plytka o mniejszej srednicy)
    assert bez["kierunkow_z_uskokiem"] == 0 and bez["kierunkow_policzonych"] == PS.KIERUNKOW and abs(bez["uskok_mediana_mm"]) < 0.05
    assert PS.uskok_scianki(szum[:0], gl[:0], kat[:0]) == {"kierunkow_policzonych": 0, "kierunkow_z_uskokiem": 0, "uskok_mediana_mm": None}


def test_u3_u9_scianka_pelnego_skanu_i_rowek_tylko_dla_plytki_ramkowej(ust, tmp_path):
    """Recenzja PR #54 proby 3, 30: kwadrat (bez rowka) dostawal 'punktow w miejscu rowka: 21037'. Teraz: kwadrat i okragla
    testowa - 'nie dotyczy'; okragla ramkowa - surowe liczby bez wniosku. Scianka pelnego skanu: 72 z 72 kierunkow."""
    w, _, _ = PS.zmierz(_skan(ust, tmp_path, "wieczorna", 1, None, 33), ust)
    tekst = "\n".join(PS.raport(w))
    assert w["uklad"] == "wieczorna" and w["scianka_boczna"]["kierunkow_z_danymi"] == PS.KIERUNKOW and w["scianka_boczna"]["widoczna"]
    assert "6. Scianka boczna plytki: widac w 72 z 72 kierunkow" in tekst and "scianka boczna: widac (72 z 72 kierunkow" in tekst
    assert w["rowek_pokrywki"] == {"dotyczy": False}
    assert "Rowek pokrywki: nie dotyczy" in tekst and "rowek pokrywki: nie dotyczy" in tekst
    assert "cofa" not in tekst and "punktow w miejscu rowka" not in tekst and "punktow_w_miejscu_rowka_R58" not in w["scianka_boczna"]
    assert w["cala_plytka_w_skanie"] is True and "CO NAJMNIEJ" in tekst and w["podloze_prawdopodobne"] is False
    w, _, _ = PS.zmierz(_skan(ust, tmp_path, "okragla_ramkowa_wieczorna", 3, None, 34), ust)
    tekst = "\n".join(PS.raport(w))
    assert w["uklad"] == "okragla_ramkowa_wieczorna" and w["rodzaj_plytki"] == "okragla ramkowa (do ramki), wieczorna"
    assert w["numer_z_dolkow"] == 3 and w["powod_wyboru"]
    rw = w["rowek_pokrywki"]
    assert rw["dotyczy"] is True and rw["kierunkow_policzonych"] >= 60 and rw["uskok_mediana_mm"] is not None
    assert "narzedzie NIE rozstrzyga" in tekst and "miara rowka nie byla sprawdzona na prawdziwym skanie" in tekst
    assert "program mowi: okragla ramkowa (do ramki), wieczorna [okragla_ramkowa_wieczorna], PEWNIE" in tekst and "numer z dolkow: 3" in tekst


def test_u4_ta_sama_nazwa_pliku_z_dwoch_folderow_daje_dwa_komplety(ust, tmp_path):
    """Recenzja PR #54 proba 6: drugi wynik nadpisywal pierwszy (1 plik _pole.txt zamiast 2)."""
    a = _skan(ust, tmp_path / "zlecenie_1", "okragla_wieczorna", 8, 80.0, 35)
    b = _skan(ust, tmp_path / "zlecenie_2", "okragla_wieczorna", 8, 85.0, 36)
    b = b.rename(b.with_name(a.name))
    opcje = ["--ustawienia", str(STANOWISKO / "ustawienia.przyklad.toml"), "--wynik", str(tmp_path / "wynik")]
    assert PS.main([str(a), *opcje]) == 3 and PS.main([str(b), *opcje]) == 3
    txt = sorted((tmp_path / "wynik").glob("*_pole.txt"))
    js = sorted((tmp_path / "wynik").glob("*_pole.json"))
    assert len(txt) == 2 and len(js) == 2
    import json as _json
    srednice = sorted(_json.loads(p.read_text(encoding="ascii"))["srednica_danych_mm"] for p in js)
    assert srednice[0] == pytest.approx(80.0, abs=1.5) and srednice[1] == pytest.approx(85.0, abs=1.5)
    assert all(str(tmp_path) not in p.read_text(encoding="ascii") for p in js)  # w wyniku tylko nazwa pliku, bez sciezki folderu
    nowa = PS.nazwa_wyniku(tmp_path / "wynik", a.stem, txt[0].name[len(a.stem) + 1:len(a.stem) + 16])  # ta sama sekunda: licznik
    assert nowa.startswith(a.stem) and not list((tmp_path / "wynik").glob(nowa + "_pole*")) and nowa[-2:] in ("_2", "_3")


def test_u5_podloze_w_skanie_jest_nazwane(ust, tmp_path):
    """Recenzja PR #54 proba 11: plytka + plaski stolik 180 x 180 mm na poziomie spodu plytki - trop 'w skanie jest podloze'."""
    skan, uk, rng = _pelny(ust, "okragla_wieczorna", 8, 37)
    v, f = _siatka_plaska(180.0, 2.0, 0.0)
    srodki = v[f].mean(axis=1)
    stolik = trimesh.Trimesh(v, f[PS.odleglosc_od_obrysu(uk, srodki[:, 0], srodki[:, 1]) < -0.5], process=False)
    stolik.remove_unreferenced_vertices()
    w, _, _ = PS.zmierz(_zapisz(trimesh.util.concatenate([skan, stolik]), rng, tmp_path / "ze_stolikiem.stl"), ust)
    tekst = "\n".join(PS.raport(w))
    assert w["podloze_prawdopodobne"] is True and "prawdopodobnie PODLOZE (stolik / uchwyt" in tekst
    assert "podloze w skanie: PRAWDOPODOBNIE TAK" in tekst and "zdjecie ekranu programu skanera" in tekst


def test_u10_plik_pusty_albo_uciety_daje_zdanie_dla_czlowieka(ust, tmp_path, capsys):
    dobry = _skan(ust, tmp_path, "okragla_wieczorna", 8, 80.0, 38)
    pusty, uciety, tekstowy = tmp_path / "pusty.stl", tmp_path / "uciety.stl", tmp_path / "tekst.stl"
    pusty.write_bytes(b"")
    uciety.write_bytes(dobry.read_bytes()[: dobry.stat().st_size // 2])
    tekstowy.write_text("to nie jest skan\n", encoding="ascii")
    for plik in (pusty, uciety, tekstowy):
        assert PS.main([str(plik), "--ustawienia", str(STANOWISKO / "ustawienia.przyklad.toml"), "--wynik", str(tmp_path / "w")]) == 2
        wyjscie = capsys.readouterr().out
        assert "jest pusty albo uszkodzony" in wyjscie and "Zapisz skan w programie skanera jeszcze raz" in wyjscie
        assert "Error" not in wyjscie and "zero-size" not in wyjscie
    assert len(list((tmp_path / "w").glob("*_pole_blad.json"))) == 3 and not list((tmp_path / "w").glob("*_pole.txt"))


def test_blok_do_arkusza_ma_stale_etykiety_takze_w_json(ust, tmp_path):
    etykiety = ["program mowi", "numer z dolkow", "dolki numeru widac", "scianka boczna", "rowek pokrywki", "brzeg plytki", "pole", "podloze w skanie"]
    w, _, _ = PS.zmierz(_skan(ust, tmp_path, "wieczorna", 1, 110.0, 21), ust)
    assert list(w["do_arkusza"]) == etykiety
    linie = PS.raport(w)
    i = linie.index("DO ARKUSZA (przepisz):")
    assert [x.strip().split(":")[0] for x in linie[i + 1:]] == etykiety
    assert w["do_arkusza"]["program mowi"].startswith("kwadratowa, wieczorna [wieczorna], PEWNIE")
    assert "pole kolowe ok. 1" in w["do_arkusza"]["pole"] and w["do_arkusza"]["podloze w skanie"] == "nie widac"
    assert [x for x in linie if x.startswith("4. Dolki numeru plytki: w skanie widac")] and "uklad okragla_wieczorna" not in "\n".join(linie)  # U12
    assert "okragla_wieczorna" in w["dolki_gdyby_drugi_ksztalt"]
    w, _, _ = PS.zmierz(_skan(ust, tmp_path, "okragla_wieczorna", 8, 80.0, 24), ust)
    assert list(w["do_arkusza"]) == etykiety and w["do_arkusza"]["program mowi"].startswith("PLYTKA NIE ROZPOZNANA")
    assert "DO ARKUSZA (przepisz):" in PS.raport(w)


def test_ograniczenie_o1_plytka_okragla_wzieta_za_kwadrat_dostaje_uwage(ust, tmp_path):
    """Znane ograniczenie programu (paczka O1, opisy_modulow/plate.md): plytka okragla bez czytelnych dolkow numeru i bez
    scianki bocznej w skanie jest brana za kwadratowa, 'pewnie'. Narzedzie programu nie poprawia - dopisuje UWAGE, gdy
    program mowi 'kwadratowa', a dane skanu sa kolem o srednicy plytki okraglej. Skan: konstrukcja jak w recenzji PR #51."""
    import auto_uklad_r58 as AR

    skan, uk, rng = _pelny(ust, "okragla_ramkowa_wieczorna", 1, 41)
    skan = AR.usun_scianke_boczna(AR.zaslon_dolki(skan, uk, ["A", "B", "C", "D"]), uk)
    w, _, _ = PS.zmierz(_zapisz(skan, rng, tmp_path / "okragla_bez_dolkow_i_scianki.stl"), ust)
    tekst = "\n".join(PS.raport(w))
    assert w["rozpoznano"] and w["scianka_boczna"]["widoczna"] is False and "scianka boczna: NIE widac" in tekst
    if w["ksztalt"] == "kwadratowa":   # dzisiejsze zachowanie programu (main 8001b55); po zmianie reguly ksztaltu galaz 'else'
        assert w["moze_okragla_wzieta_za_kwadrat"] is True and "UWAGA: program mowi 'kwadratowa'" in tekst
        assert "UWAGA: dane sa kolem jak plytka OKRAGLA" in w["do_arkusza"]["program mowi"]
    else:
        assert w["moze_okragla_wzieta_za_kwadrat"] is False and "UWAGA: program mowi" not in tekst
    w, _, _ = PS.zmierz(_skan(ust, tmp_path, "wieczorna", 1, 95.0, 42), ust)   # prawdziwy kwadrat w polu 95 mm: bez uwagi
    assert w["uklad"] == "wieczorna" and w["moze_okragla_wzieta_za_kwadrat"] is False
    assert "UWAGA: program mowi" not in "\n".join(PS.raport(w))
