"""Korekta skali ze skanu (P3): estymata przy bledzie wspolczynnika, okno, ostrzezenie, plytka poranna, pas brzegu
(zastrzezenie R2b), inspekcja w skali skorygowanej, pola wyniku i tabela - na atrapach."""
from __future__ import annotations

import functools
import shutil
import warnings

import numpy as np
import pytest
import trimesh

from stanowisko import inspect as I, match, plate, porownaj as PO, synth, ustawienia as UST, uklad as U

W0 = 1.22  # wspolczynnik puli wieczornej w testach
CEL = 0.05  # dokladnosc estymaty skali [punkty proc.] (cel z testow T7)


@pytest.fixture(scope="module")
def ust():
    return UST.wczytaj_ustawienia()


@pytest.fixture(scope="module")
def folder_projektow(korony, tmp_path_factory):
    d = tmp_path_factory.mktemp("pula_skala")
    for i, p in enumerate(korony):
        shutil.copy(p, d / f"2026-11-02_p{i}-{['11', '14', '36'][i]}-crown_cad.stl")
    return d


@pytest.fixture(scope="module")
def pula(folder_projektow):
    return match.Pula([folder_projektow], W0)


@pytest.fixture(scope="module")
def plytka(korony):
    """Funkcja: (blad wspolczynnika w %, nazwa ukladu, wspolczynnik puli, seed, opcje) -> (wyrownanie, prawda); praca jest
    o ``blad`` % wieksza niz projekt x wspolczynnik puli. Wyniki zapamietane na czas modulu."""
    @functools.lru_cache(maxsize=None)
    def zrob(blad: float, uklad: str = "okragla_wieczorna", w_puli: float = W0, seed: int = 22, ubytki: tuple = (0, 0), srednica: tuple | None = None,
             drgniecie: float = 0.0):
        uk = U.wczytaj(uklad)
        w = w_puli * (1 + blad / 100)
        op = synth.Opcje.z_toml(plytka=uk.nazwa, prace_na_plytce=3, p_drgniecia=drgniecie, wspolczynnik=(w, w), poza_uklad=True, ubytki_na_prace=ubytki, srednica_ubytku=srednica)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            skan, prawda = synth.generuj_plytke(uk, uk.numery[0], list(korony), np.random.default_rng(seed), op, seed)
        wyr = plate.wyrownaj(skan, uk)
        assert len(wyr.fragmenty) == 3 and all(f.status == "praca" for f in wyr.fragmenty)
        return wyr, prawda
    return zrob


def _skala_transformacji(k) -> float:
    return float(np.cbrt(np.linalg.det(np.array(k.transformacja)[:3, :3])))


@pytest.mark.parametrize("blad", [-1.0, 0.0, 0.5])
def test_estymata_skali_i_korekta(pula, plytka, ust, blad):
    """Blad wspolczynnika -1 ... +1 %: estymata w granicy 0,05 punktu proc., po korekcie pokrycie i status jak bez bledu."""
    wyr, prawda = plytka(blad)
    mapa = {p.gniazdo: p for p in prawda.prace}
    for f in wyr.fragmenty:
        r = match.dopasuj(f.punkty, f.normalne, pula, ust, f.gniazdo)
        k, sk = r.najlepszy, r.skala
        assert k.id == mapa[f.gniazdo].projekt and sk is k.skala
        assert sk.poprawka_proc is not None and abs(sk.poprawka_proc - blad) <= CEL, (blad, sk)
        assert sk.zastosowana and sk.powod == "" and sk.ostrzezenie == (abs(blad) > ust["match"]["korekta_skali_ostrzezenie_proc"])
        assert sk.wspolczynnik_puli == W0 and abs(sk.wspolczynnik_ze_skanu / (W0 * (1 + blad / 100)) - 1) <= CEL / 100
        assert sk.punktow >= match.SKALA_MIN_PUNKTOW and sk.punktow_w_pasie_brzegu > 0
        assert r.status == "zielony" and k.pokrycie >= 0.85 and k.pokrycie == pytest.approx(sk.pokrycie_po, abs=1e-4)
        assert k.pokrycie >= sk.pokrycie_przed - 0.01 and (blad == 0 or k.pokrycie > sk.pokrycie_przed + 0.02)
        assert abs(_skala_transformacji(k) - (1 + sk.poprawka_proc / 100)) < 1e-6  # (projekt x w) -> plytka: podobienstwo
        # ta sama poza co w prawdzie generatora: prawda dziala na projekt x (w x (1 + blad)), kandydat na projekt x w
        A = np.array(k.transformacja) @ trimesh.transformations.scale_matrix(1 / (1 + blad / 100))
        b = match.blad_pozy(A, mapa[f.gniazdo].transformacja, pula.projekty[k.id].siatka)
        assert b["przesuniecie_mm"] < 0.05 and b["obrot_deg"] < 0.5, b
        assert bool(r.uwagi) == sk.ostrzezenie and all("skala" in u for u in r.uwagi)


def test_poza_oknem_bez_korekty_z_ostrzezeniem(pula, plytka, ust):
    wyr, prawda = plytka(2.0)
    mapa = {p.gniazdo: p for p in prawda.prace}
    for f in wyr.fragmenty:
        r = match.dopasuj(f.punkty, f.normalne, pula, ust, f.gniazdo)
        k, sk = r.najlepszy, r.skala
        assert k.id == mapa[f.gniazdo].projekt
        assert abs(sk.poprawka_proc - 2.0) <= CEL and not sk.zastosowana and sk.ostrzezenie and "poza oknem" in sk.powod
        assert _skala_transformacji(k) == pytest.approx(1.0, abs=1e-9) and k.pokrycie == sk.pokrycie_przed < 0.85 and r.status != "zielony"
        assert any("korekty nie zastosowano" in u and "poza oknem" in u for u in r.uwagi)


def test_plytka_poranna_tylko_pomiar(pula, plytka, ust):
    """``bez_korekty`` (plytka poranna: prace spieczone): poprawka zmierzona i z ostrzezeniem, ale nie zastosowana."""
    wyr, _ = plytka(0.5)
    f = wyr.fragmenty[0]
    powod = "plytka poranna"
    r = match.dopasuj(f.punkty, f.normalne, pula, ust, f.gniazdo, bez_korekty=powod)
    k, sk = r.najlepszy, r.skala
    assert abs(sk.poprawka_proc - 0.5) <= CEL and not sk.zastosowana and sk.powod == powod and sk.ostrzezenie
    assert _skala_transformacji(k) == pytest.approx(1.0, abs=1e-9) and k.pokrycie == sk.pokrycie_przed
    assert sk.pokrycie_po > sk.pokrycie_przed + 0.01  # widac, ile dalaby korekta


def test_ustawienia_steruja_korekta(pula, plytka, ust):
    wyr, _ = plytka(0.5)
    f = wyr.fragmenty[0]
    m = ust["match"]
    r = match.dopasuj(f.punkty, f.normalne, pula, {**ust, "match": {**m, "korekta_skali": False}}, f.gniazdo)
    assert r.skala.poprawka_proc is None and not r.skala.zastosowana and "[match] korekta_skali" in r.skala.powod and not r.skala.ostrzezenie
    assert _skala_transformacji(r.najlepszy) == pytest.approx(1.0, abs=1e-9) and r.uwagi == []
    r = match.dopasuj(f.punkty, f.normalne, pula, {**ust, "match": {**m, "korekta_skali_ostrzezenie_proc": 0.7}}, f.gniazdo)
    assert r.skala.zastosowana and not r.skala.ostrzezenie
    r = match.dopasuj(f.punkty, f.normalne, pula, {**ust, "match": {**m, "korekta_skali_okno_proc": 0.4}}, f.gniazdo)  # 0,5 % > okno 0,4 + dokladnosc 0,05
    assert not r.skala.zastosowana and r.skala.ostrzezenie and "poza oknem" in r.skala.powod and "0.4 %" in r.skala.powod
    # praca nierozpoznana takze w skali ze skanu (pokrycie po korekcie < prog_ostrzezenia_pokrycie): korekty nie stosuje sie
    r = match.dopasuj(f.punkty, f.normalne, pula, {**ust, "match": {**m, "prog_akceptacji_pokrycie": 0.999, "prog_ostrzezenia_pokrycie": 0.99}}, f.gniazdo)
    assert not r.skala.zastosowana and r.skala.niepewna and not r.skala.ostrzezenie and "nierozpoznana" in r.skala.powod
    assert _skala_transformacji(r.najlepszy) == pytest.approx(1.0, abs=1e-9) and r.status == "szary"


def _w_pasie(P, pr, T, od_brzegu):
    """Maska punktow (uklad plytki) lezacych blizej niz ``od_brzegu`` mm od brzegu (z = 0 w ukladzie puli projektu)."""
    return (P @ T[:3, :3].T + T[:3, 3])[:, 2] > -od_brzegu


def test_strefa_brzegu_nie_wplywa_na_skale(pula, plytka, ust):
    """Zastrzezenie R2b: krawedz brzegu przesunieta o 0,02 mm albo ukruszona nie zmienia estymaty skali.

    Estymator: te same punkty poza pasem i ten sam start -> skala identyczna; kontrolnie bez wylaczenia pasa
    (pas 0 mm) ta sama zmiana przesuwa skale. Caly ``dopasuj``: zmiana estymaty ponizej szumu estymaty."""
    wyr, prawda = plytka(0.3)
    mapa = {p.gniazdo: p for p in prawda.prace}
    pas = ust["match"]["korekta_skali_pas_brzegu_mm"]
    for f in wyr.fragmenty:
        pr = pula.projekty[mapa[f.gniazdo].projekt]
        k = match.dopasuj_pare(match.FragmentDoDopasowania.z_punktow(f.punkty, f.normalne), pr, ust)
        T = pr.T0 @ np.linalg.inv(np.array(k.transformacja))  # plytka -> uklad puli, przed korekta
        brzeg = _w_pasie(f.punkty, pr, T, 1.5)
        assert 0.02 < brzeg.mean() < 0.8
        grubiej = f.punkty + 0.02 * f.normalne * brzeg[:, None]  # caly pas 1,5 mm grubszy o 0,02 mm
        promien = f.punkty - np.median(f.punkty, axis=0)
        promien[:, 2] = 0.0
        promien /= np.maximum(np.linalg.norm(promien, axis=1, keepdims=True), 1e-9)
        odgiety = f.punkty + 0.02 * promien * brzeg[:, None]  # brzeg odgiety na zewnatrz o 0,02 mm (obie scianki)
        srodek = f.punkty[np.flatnonzero(_w_pasie(f.punkty, pr, T, 0.5))[0]]
        d = np.linalg.norm(f.punkty - srodek, axis=1)
        ukruszony = f.punkty - f.normalne * (0.4 * np.clip(1 - (d / 0.6) ** 2, 0, None) * brzeg)[:, None]  # ubytek fi 1,2 mm na krawedzi
        s0 = match.skala_ze_skanu(f.punkty, pr, T, pas)
        b0 = match.skala_ze_skanu(f.punkty, pr, T, 0.0)
        assert s0["ok"] and b0["ok"] and abs((1 / s0["s"] - 1) * 100 - 0.3) <= CEL
        for P2 in (grubiej, odgiety, ukruszony):
            s2 = match.skala_ze_skanu(P2, pr, T, pas)
            assert s2["ok"] and abs(s2["s"] - s0["s"]) < 1e-9 and s2["punktow"] == s0["punktow"]
        b2 = match.skala_ze_skanu(odgiety, pr, T, 0.0)
        assert (1 / b2["s"] - 1 / b0["s"]) * 100 > 0.01  # bez wylaczenia pasa odgiety brzeg udaje wieksza prace
        r0 = match.dopasuj(f.punkty, f.normalne, pula, ust, f.gniazdo)
        for P2 in (grubiej, odgiety, ukruszony):
            r2 = match.dopasuj(P2, f.normalne, pula, ust, f.gniazdo)
            assert r2.najlepszy.id == pr.id and abs(r2.skala.poprawka_proc - r0.skala.poprawka_proc) <= 0.02


def _wynik(wyr, gniazda) -> dict:
    """Najmniejszy slownik wyniku ``porownaj`` potrzebny tabeli."""
    return {"skan": "skan_test.stl", "plytka": wyr.plytka, "numer": 8, "numer_zrodlo": "dolki", "wspolczynnik": W0, "projekty": 3, "uklad_zgodny": True,
            "czas_s": {"razem": 1.0, "plate": 0.5, "match": 0.5}, "gniazda": gniazda, "gniazda_puste": [], "gniazda_podwojne": [], "poza_gniazdem": 0,
            "statusy_gniazd": {"zielony": len(gniazda)}, "ubytki": 0}


def _inspekcja(wyr, prawda, pula, ust):
    mapa = {p.gniazdo: p for p in prawda.prace}
    out = []
    for f in wyr.fragmenty:
        r = match.dopasuj(f.punkty, f.normalne, pula, ust, f.gniazdo)
        k = r.najlepszy
        assert k.id == mapa[f.gniazdo].projekt
        out.append((mapa[f.gniazdo], r, I.sprawdz(f.punkty, f.normalne, pula.projekty[k.id], np.array(k.transformacja), k.pokrycie, ust, f.gniazdo)))
    return out


def test_inspekcja_w_skali_skorygowanej_praca_cala(pula, plytka, ust):
    """Blad wspolczynnika +1 %: bez korekty prace cale nie sa 'ok' (alarm albo 'popraw ulozenie'), z korekta - wszystkie 'ok'."""
    wyr, prawda = plytka(1.0)
    bez = _inspekcja(wyr, prawda, pula, {**ust, "match": {**ust["match"], "korekta_skali": False}})
    assert all(wi.status != "ok" for _, _, wi in bez), [wi.status for _, _, wi in bez]
    for p, r, wi in _inspekcja(wyr, prawda, pula, ust):
        assert r.skala.zastosowana and wi.status == "ok" and wi.ubytki == [], (wi.status, wi.uwagi)
        assert abs(wi.odchylki["mediana_mm"]) < 0.01 and wi.odchylki["udzial_pod"] < 0.02


def test_korekta_nie_zjada_ukruszen(pula, folder_projektow, plytka, ust):
    """Ten sam skan (prace z ubytkami brzegu, o 0,5 % wieksze niz projekt x wspolczynnik puli) oceniony dwa razy: pula
    o dokladnym wspolczynniku bez korekty (odniesienie) i pula z bledem + korekta ze skanu - wykrycia takie same."""
    wyr, prawda = plytka(0.5, ubytki=(1, 2), srednica=(0.8, 1.4), seed=5)
    dokladna = match.Pula([folder_projektow], W0 * 1.005)
    odniesienie = _inspekcja(wyr, prawda, dokladna, {**ust, "match": {**ust["match"], "korekta_skali": False}})
    n = traf_odn = traf_kor = 0
    for (p, _, wi0), (_, r, wi) in zip(odniesienie, _inspekcja(wyr, prawda, pula, ust)):
        assert abs(r.skala.poprawka_proc - 0.5) <= CEL and r.skala.zastosowana, r.skala  # ubytki brzegu nie zmieniaja estymaty skali
        assert wi.status in ("ubytek", "sprawdz", "sprawdz_ulozenie") and wi.status == wi0.status, (wi.status, wi0.status, wi.uwagi)
        ub = [u for u in p.ubytki if u.wykrywalny]
        dp0 = I.dopasuj_do_prawdy(ub, [u.__dict__ for u in wi0.ubytki])
        dp = I.dopasuj_do_prawdy(ub, [u.__dict__ for u in wi.ubytki])
        n += len(ub)
        traf_odn += sum(dp0["trafione"]["dowolny"])
        traf_kor += sum(dp["trafione"]["dowolny"])
        assert dp["falszywe_czerwone"] == 0 and dp["falszywe"] <= dp0["falszywe"] + 1
    assert n >= 3 and traf_kor >= traf_odn - 1 and traf_kor >= 0.8 * n, (traf_kor, traf_odn, n)


def test_estymata_niepewna_bez_ostrzezenia(pula, plytka, ust):
    """Podwojna powierzchnia (drgniecie): skan nie pasuje do projektu w zadnej skali - estymata oznaczona jako niepewna,
    bez ostrzezenia o wspolczynniku, nawet przy progu ostrzezenia 0; skan dobry przy tym samym progu ostrzega."""
    czuly = {**ust, "match": {**ust["match"], "korekta_skali_ostrzezenie_proc": 0.0}}
    prog = ust["match"]["prog_akceptacji_pokrycie"]
    wyr, _ = plytka(0.0, drgniecie=1.0)
    gniazda = PO.dopasuj_fragmenty(wyr, pula, czuly, inspekcja=False)
    for g in gniazda:
        sk = g["skala"]
        assert sk["poprawka_proc"] is not None and sk["niepewna"] == (sk["pokrycie_po"] < prog)
        assert sk["niepewna"] and not sk["ostrzezenie"] and g["uwagi"] == [], sk
    t = PO.tabela(_wynik(wyr, gniazda))
    assert t.count("?") == 3 and "!" not in t and "SKALI (praca" not in t  # tabela: "?" = estymata niepewna, bez ostrzezenia
    wyr, _ = plytka(0.5)
    for g in PO.dopasuj_fragmenty(wyr, pula, czuly, inspekcja=False):
        assert not g["skala"]["niepewna"] and g["skala"]["ostrzezenie"]


def test_porownaj_pola_skali_i_tabela(pula, folder_projektow, plytka, ust):
    """Wynik gniazda ma pola korekty skali; tabela pokazuje poprawke i ostrzezenie; plytka poranna = tylko pomiar."""
    wyr, _ = plytka(0.5)
    gniazda = PO.dopasuj_fragmenty(wyr, pula, ust)
    assert len(gniazda) == 3
    for g in gniazda:
        sk = g["skala"]
        assert {"poprawka_proc", "zastosowana", "powod", "ostrzezenie", "wspolczynnik_puli", "wspolczynnik_ze_skanu", "pokrycie_przed", "pokrycie_po"} <= set(sk)
        assert sk["zastosowana"] and sk["ostrzezenie"] and abs(sk["poprawka_proc"] - 0.5) <= CEL
        assert g["status"] == "zielony" and g["inspekcja"]["status"] == "ok" and g["kandydaci"][0]["skala"] == sk
    t = PO.tabela(_wynik(wyr, gniazda))
    assert "skala %" in t and "SKALI (praca" in t and t.count("!") == 3 and "+0.5" in t
    # plytka poranna: pula 1,0, praca wieksza o 0,5 % - poprawka zmierzona, w nawiasie, nie zastosowana
    pula_rano = match.Pula([folder_projektow], 1.0)
    wyr_r, _ = plytka(0.5, uklad="okragla_poranna", w_puli=1.0)
    gniazda = PO.dopasuj_fragmenty(wyr_r, pula_rano, ust)
    for g in gniazda:
        sk = g["skala"]
        assert not sk["zastosowana"] and "poranna" in sk["powod"] and sk["ostrzezenie"] and abs(sk["poprawka_proc"] - 0.5) <= CEL
        assert sk["wspolczynnik_puli"] == 1.0
    t = PO.tabela(_wynik(wyr_r, gniazda))
    assert "(+0.5" in t and "bez korekty:" in t and "poranna: prace spieczone" in t
    # bez ostrzezen nie ma wiersza ostrzezenia
    wyr0, _ = plytka(0.0)
    t = PO.tabela(_wynik(wyr0, PO.dopasuj_fragmenty(wyr0, pula, ust, inspekcja=False)))
    assert "SKALI (praca" not in t and "!" not in t


def test_wzor_ustawien_ma_decyzje_wlasciciela():
    """Decyzja z 06.11.2026: korekta wlaczona, okno +-1 %, ostrzezenie powyzej 0,3 %."""
    m = UST.wczytaj_ustawienia(UST.PLIK_PRZYKLADU)["match"]
    assert m["korekta_skali"] is True and m["korekta_skali_okno_proc"] == 1.0 and m["korekta_skali_ostrzezenie_proc"] == 0.3
    assert m["korekta_skali_pas_brzegu_mm"] > 0 and 0 < m["filtr_wysokosc_min_udzial"] < 1


def test_blad_pozy_dla_podobienstwa():
    m = trimesh.creation.box([5, 6, 7])
    B = trimesh.transformations.rotation_matrix(0.3, [0, 0, 1]) @ trimesh.transformations.translation_matrix([1, 2, 3])
    A = B @ trimesh.transformations.scale_matrix(1.01)
    b = match.blad_pozy(A, B, m)
    assert b["obrot_deg"] < 1e-5 and b["przesuniecie_mm"] < 0.05
    assert match.skala_macierzy(A) == pytest.approx(1.01) and match.skala_macierzy(B) == 1.0


def test_pula_wspolczynnik_dla_projektu(folder_projektow, pula):
    """Wspolczynnik mozna podac dla pojedynczego projektu (docelowo z raportu MillBox kazdej pracy)."""
    pierwszy = next(iter(pula.projekty))
    p2 = match.Pula([folder_projektow], W0, wspolczynniki={pierwszy: 1.25})
    assert p2.wspolczynnik == W0 and set(p2.projekty) == set(pula.projekty)
    for i, pr in p2.projekty.items():
        w = 1.25 if i == pierwszy else W0
        assert pr.wspolczynnik == w and pr.wysokosc == pytest.approx(pula.projekty[i].wysokosc * w / W0, rel=1e-6)
