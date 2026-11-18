"""porownaj: blad inspekcji jednego gniazda nie kladzie calej plytki (P7, recenzja PR #13).

Wyjatek z ``inspect.sprawdz`` dla jednego gniazda: to gniazdo jest zolte (status inspekcji ``nie_sprawdzono``) z uwaga
"blad inspekcji: <typ>: <tresc>", nigdy zielone; pozostale gniazda sa policzone jak bez bledu, a wynik JSON zapisany.
``KeyboardInterrupt``, ``SystemExit`` i ``MemoryError`` nie sa lapane.
"""
from __future__ import annotations

import json
import shutil
import warnings

import numpy as np
import pytest

from stanowisko import inspect as I, match, plate, porownaj as PO, synth, uklad as U, ustawienia as UST

BLAD = "b" + chr(0x142) + chr(0x105) + "d inspekcji"  # "blad inspekcji" z polskimi znakami: poczatek uwagi w wyniku (teksty wyniku sa po polsku ze znakami diakrytycznymi)
BLAD_B1 = "'NoneType' object has no attribute 'query'"  # wyjatek z uwagi B1 recenzji


@pytest.fixture(scope="module")
def ust():
    return UST.wczytaj_ustawienia()


@pytest.fixture(scope="module")
def folder_projektow(korony, tmp_path_factory):
    d = tmp_path_factory.mktemp("projekty_bledy")
    for i, p in enumerate(korony):
        shutil.copy(p, d / f"2026-11-02_p{i}-{['11', '14', '36'][i]}-crown_cad.stl")
    return d


@pytest.fixture(scope="module")
def plytka(korony, folder_projektow, tmp_path_factory, ust):
    """Sztuczny skan okraglej plytki wieczornej z 3 atrapami bez ubytkow: wyrownanie, pula, wynik bez bledu, pliki skanu i prawdy."""
    uk = U.wczytaj("okragla_wieczorna")
    op = synth.Opcje.z_toml(plytka=uk.nazwa, prace_na_plytce=3, wspolczynnik=(1.22, 1.22), ubytki_na_prace=(0, 0), p_drgniecia=0.0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        skan, prawda = synth.generuj_plytke(uk, 8, list(korony), np.random.default_rng(6), op, 6)
        wyr = plate.wyrownaj(skan, uk)
    p_stl, p_json = synth.zapisz(skan, prawda, tmp_path_factory.mktemp("skan_bledy"), "skan_bledy")
    pula = match.Pula([folder_projektow], 1.22)
    wzor = PO.dopasuj_fragmenty(wyr, pula, ust)
    assert len(wzor) == 3 and all(g["inspekcja"] is not None and g["gniazdo"] is not None for g in wzor)
    assert all(g["status"] == "zielony" and g["inspekcja"]["status"] == "ok" and g["status_gniazda"] == "zielony" for g in wzor)
    return wyr, pula, wzor, p_stl, p_json


def _zepsuj(monkeypatch, gniazdo: int, wyjatek: BaseException) -> None:
    """``inspect.sprawdz`` rzuca ``wyjatek`` dla jednego gniazda; pozostale gniazda liczy prawdziwa inspekcja."""
    prawdziwe = I.sprawdz

    def sprawdz(P, N, pr, transformacja, pokrycie, ust, nr=None):
        if nr == gniazdo:
            raise wyjatek
        return prawdziwe(P, N, pr, transformacja, pokrycie, ust, nr)

    monkeypatch.setattr(I, "sprawdz", sprawdz)


def _skrot(g: dict) -> tuple:
    """To, co ma sie nie zmienic w gniezdzie bez bledu (bez czasow)."""
    ins = g["inspekcja"]
    return (g["gniazdo"], g["status"], g["status_gniazda"], g["kandydaci"][0]["id"], ins["status"], len(ins["ubytki"]), ins["uwagi"],
            ins["brzeg"].get("sprawdzony"))


def test_blad_inspekcji_jednego_gniazda_nie_kladzie_plytki(plytka, ust, monkeypatch):
    wyr, pula, wzor, _, _ = plytka
    zle = wzor[1]["gniazdo"]
    _zepsuj(monkeypatch, zle, AttributeError(BLAD_B1))
    podglad: dict = {}
    with pytest.warns(UserWarning, match=f"gniazdo {zle}: {BLAD}"):
        gniazda = PO.dopasuj_fragmenty(wyr, pula, ust, podglad=podglad)  # przed poprawka: AttributeError przerywa cala plytke
    assert [g["gniazdo"] for g in gniazda] == [g["gniazdo"] for g in wzor]
    for g, w in zip(gniazda, wzor):
        if g["gniazdo"] != zle:  # reszta plytki policzona jak bez bledu
            assert _skrot(g) == _skrot(w)
            assert podglad[g["gniazdo"]]._P is not None
            continue
        ins = g["inspekcja"]
        assert g["status"] == "zielony" and g["kandydaci"][0]["id"] == w["kandydaci"][0]["id"]  # match rozpoznal prace jak zwykle
        assert g["status_gniazda"] == "zolty" and ins["status"] == "nie_sprawdzono"  # nigdy zielone
        assert len(ins["uwagi"]) == 1 and ins["uwagi"][0].startswith(f"{BLAD}: AttributeError: {BLAD_B1}")
        assert ins["blad"].startswith(f"AttributeError: {BLAD_B1}")
        assert ins["gniazdo"] == zle and ins["projekt"] == w["inspekcja"]["projekt"] and ins["pokrycie"] == w["inspekcja"]["pokrycie"]
        assert ins["ubytki"] == [] and ins["plamy"] == [] and ins["wciecia"] == [] and ins["brzeg"] == {}
        assert set(w["inspekcja"]) <= set(ins)  # te same pola co zwykly wynik inspekcji (+ "blad")
        assert zle not in podglad or podglad[zle]._P is None  # okno: "brak mapy odchylek", bez wyjatku
        for status_match in ("zielony", "zolty"):
            assert PO.status_gniazda(status_match, ins) == "zolty"
    json.dumps(gniazda)
    assert PO.gniazda_nie_sprawdzone({"gniazda": gniazda}) == [zle]


def test_cli_zapisuje_wynik_mimo_bledu_inspekcji(plytka, folder_projektow, tmp_path, monkeypatch, capsys):
    _, _, wzor, p_stl, p_json = plytka
    zle = wzor[0]["gniazdo"]
    _zepsuj(monkeypatch, zle, ValueError("zepsute dane projektu"))
    # przed poprawka: ValueError konczy program przed zapisem pliku wyniku
    wynik = PO.main(["--skan", str(p_stl), "--projekty", str(folder_projektow), "--plytka", "okragla_wieczorna", "--wspolczynnik", "1.22",
                     "--prawda", str(p_json), "--wyjscie", str(tmp_path)])
    zapis = json.loads((tmp_path / f"{p_stl.stem}_wynik.json").read_text(encoding="utf-8"))
    assert len(zapis["gniazda"]) == 3 and len(wynik["gniazda"]) == 3
    for g in zapis["gniazda"]:
        w = next(x for x in wzor if x["gniazdo"] == g["gniazdo"])
        if g["gniazdo"] != zle:
            assert (g["status"], g["status_gniazda"], g["inspekcja"]["status"]) == (w["status"], w["status_gniazda"], w["inspekcja"]["status"])
            continue
        assert g["status_gniazda"] == "zolty" and g["inspekcja"]["status"] == "nie_sprawdzono"
        assert g["inspekcja"]["uwagi"][0].startswith(f"{BLAD}: ValueError: zepsute dane projektu")
    assert zapis["statusy_gniazd"]["zolty"] == 1 and zapis["statusy_gniazd"]["zielony"] == 2 and zapis["ubytki"] == 0
    assert any(f"gniazdo {zle}: {BLAD}" in o and "ValueError" in o for o in zapis["ostrzezenia"])
    r = zapis["metryki_inspekcji"]["razem"]  # metryki licza sie dalej; blad inspekcji to nie alarm ubytku
    assert r["statusy"]["nie_sprawdzono"] == 1 and r["statusy"]["ok"] == 2 and r["prace_cale_z_alarmem"] == 0 and r["prace_cale_nie_sprawdzono"] == 1
    assert (tmp_path / f"{p_stl.stem}_mapa.png").exists()
    wyjscie = capsys.readouterr().out
    assert "UWAGA:" in wyjscie and "NIE SPRAWDZONO" in wyjscie and f"gniazdo {zle}: {BLAD.upper()}" in wyjscie and "ValueError" in wyjscie


@pytest.mark.parametrize("wyjatek", [KeyboardInterrupt(), SystemExit(3), MemoryError("brak pamieci")])
def test_przerwanie_i_brak_pamieci_nie_sa_lapane(plytka, ust, monkeypatch, wyjatek):
    wyr, pula, wzor, _, _ = plytka
    _zepsuj(monkeypatch, wzor[0]["gniazdo"], wyjatek)
    with pytest.raises(type(wyjatek)):
        PO.dopasuj_fragmenty(wyr, pula, ust)
