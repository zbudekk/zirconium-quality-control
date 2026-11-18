"""match z pula wpisow (E3-A5): pula per praca (wpis = projekt STL x wspolczynnik krazka), pamiec podreczna projektow na
dysku, ranking wstepny przy duzej puli, wybor wpisu wsrod wariantow tego samego STL, porownaj z pula wpisow.

Kryteria planu etapu 3 (sekcja 4.1, E3-A5) sprawdzane tutaj na atrapach: 1 (plytka z pracami z dwoch krazkow 1,20 i 1,25 -
top-1 wlasciwy), 2 (ten sam STL z dwoma wspolczynnikami w puli - wynik wskazuje wlasciwy wpis). Kryteria 3 i 4 (pula 400
wpisow, czas i pamiec; regresja R59) mierzy ``narzedzia/metryki_pula.py`` na PC (raport E3-A5).
Dane FIKCYJNE (atrapy, zmyslone nazwy plikow), tylko tmp_path.
"""
from __future__ import annotations

import json
import os
import shutil
import time
import warnings
from pathlib import Path

import numpy as np
import pytest

import atrapy_koron
import drzewo_syntetyczne as D
import metryki_pula as MP
from stanowisko import baza as B
from stanowisko import indeks as I
from stanowisko import match
from stanowisko import pamiec_puli as PP
from stanowisko import plate
from stanowisko import porownaj as PO
from stanowisko import pula as PL
from stanowisko import synth
from stanowisko import uklad as U
from stanowisko import ustawienia as UST
from stanowisko import wspolczynniki as WS

KRAZKI = {1.20: "K-120", 1.25: "K-125"}  # dwa krazki wieczoru (kryterium 1)
NAZWY = ("2026-11-17_fikcyjny-11-crown_cad.stl", "2026-11-17_zmyslony-14-crown_cad.stl", "2026-11-17_atrapowy-36-crown_cad.stl")
NAZWISKA = ("fikcyjny", "zmyslony", "atrapowy", "rozpraszacz")  # fragmenty nazw plikow - nie moga trafic do pamieci ani wyniku


@pytest.fixture(scope="module")
def ust():
    return UST.wczytaj_ustawienia()


@pytest.fixture(scope="module")
def stl(korony, tmp_path_factory) -> dict:
    """3 atrapy (siekacz, przedtrzonowy, trzonowy) + 6 rozpraszaczy podobnych wymiarow (przechodza filtr wymiarow)."""
    d = tmp_path_factory.mktemp("pula_wpisow")
    pliki = {}
    for p, nazwa in zip(korony, NAZWY):
        shutil.copy(p, d / nazwa)
        pliki[nazwa] = d / nazwa
    rng = np.random.default_rng(11)
    for i in range(6):
        t = ("trzonowy", "przedtrzonowy")[i % 2]
        W, L, H, g, amp = atrapy_koron.TYPY[t]
        sk = rng.uniform(0.97, 1.03, 3)
        m = atrapy_koron.korona(W * sk[0], L * sk[1], H * sk[2], g, amp, n_theta=96, n_u=120, rng=rng)
        nazwa = f"2026-11-17_rozpraszacz{i}-{36 if t == 'trzonowy' else 14}-crown_cad.stl"
        m.export(d / nazwa)
        pliki[nazwa] = d / nazwa
    return pliki


def wpis(plik: Path, w: float | None, frezowanie_id: int | None, projekt_id: int, krazek: str | None = None) -> PL.Wpis:
    return PL.Wpis(sha16=synth.skrot_pliku(plik), wspolczynnik=w, krazek=krazek, frezowanie_id=frezowanie_id, projekt_id=projekt_id,
                   kuweta=str(3000 + projekt_id), zeby=None, typ=None, zrodlo_wspolczynnika="csv" if frezowanie_id else "rano")


def wpisy_obu_krazkow(stl: dict) -> tuple[list, dict]:
    """Kazdy plik na obu krazkach (1,20 i 1,25): wpisy (frezowanie_id rozne) i sciezki projekt_id -> plik (kryterium 2)."""
    wp, sciezki = [], {}
    fid = 0
    for pid, (nazwa, p) in enumerate(sorted(stl.items()), start=1):
        sciezki[pid] = p
        for w, krazek in KRAZKI.items():
            fid += 1
            wp.append(wpis(p, w, fid, pid, krazek))
    return wp, sciezki


@pytest.fixture(scope="module")
def plytka(stl):
    """Plytka okragla wieczorna R59 z 3 atrapami; wspolczynnik pracy na przemian 1,20 / 1,25 (dwa krazki); prawda."""
    uk = U.wczytaj("okragla_wieczorna")
    op = synth.Opcje.z_toml(plytka=uk.nazwa, prace_na_plytce=3, p_drgniecia=0.0, wspolczynnik=(1.20, 1.25), poza_uklad=True, wersja_ubytkow=1)
    rng = MP.LosowanieKrazkow(np.random.default_rng(22), tuple(KRAZKI), kolejno=True)
    projekty = [stl[n] for n in NAZWY]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        skan, prawda = synth.generuj_plytke(uk, uk.numery[0], projekty, rng, op, 22)
    assert sorted({round(p.wspolczynnik, 2) for p in prawda.prace}) == [1.20, 1.25]  # obie wartosci krazkow na plytce
    wyr = plate.wyrownaj(skan, uk)
    assert len(wyr.fragmenty) == 3 and all(f.status == "praca" for f in wyr.fragmenty)
    return skan, wyr, prawda


@pytest.fixture(scope="module")
def pula_obu(stl, tmp_path_factory):
    wp, sciezki = wpisy_obu_krazkow(stl)
    pam = PP.PamiecPuli(tmp_path_factory.mktemp("pamiec_obu"))
    return match.Pula.z_wpisow(wp, sciezki, pamiec=pam), wp, sciezki


def wpis_prawdy(praca, wp: list) -> PL.Wpis:
    return next(w for w in wp if w.sha16 == praca.projekt and abs(w.wspolczynnik - praca.wspolczynnik) < 1e-9)


# --- budowa puli z wpisow ---------------------------------------------------------------------------------------------
def test_pula_z_wpisow_geometrie_klucze_i_liczniki(stl, tmp_path):
    wp, sciezki = wpisy_obu_krazkow(stl)
    p0 = stl[NAZWY[0]]
    pid0 = next(k for k, v in sciezki.items() if v == p0)
    wp += [wpis(p0, 1.20, 901, pid0, "K-120B"),                       # drugi krazek o tym samym wspolczynniku: ta sama geometria
           wpis(p0, None, 902, pid0, "K-BEZ"),                         # wpis bez wspolczynnika
           wpis(p0, 1.22, 903, 777, "K-X")]                            # projekt bez sciezki (usuniety z dysku albo spoza zrodel)
    sciezki = {**sciezki, 777: tmp_path / "nie_ma.stl"}
    pula = match.Pula.z_wpisow(wp, sciezki, pamiec=PP.PamiecPuli(tmp_path / "pamiec"))
    assert pula.per_praca and pula.wspolczynnik is None and pula.ranking_wstepny
    assert len(pula) == len(stl) * 2 == len(pula.lekkie) == len(pula.projekty)  # projekt x wspolczynnik
    lz = pula.liczniki
    assert (lz["wpisow"], lz["brak_pliku"], lz["bez_wspolczynnika"], lz["geometrii"]) == (len(wp), 1, 1, len(stl) * 2)
    sha0 = synth.skrot_pliku(p0)
    klucze = [k for k in pula.lekkie if k.startswith(sha0)]
    assert sorted(klucze) == [f"{sha0}@1.2", f"{sha0}@1.25"]  # ten sam STL z dwoma wspolczynnikami = dwa klucze
    fid0 = next(w.frezowanie_id for w in wp if w.projekt_id == pid0 and w.wspolczynnik == 1.20)
    assert sorted(w["frezowanie_id"] for w in pula.wpisy_geometrii[f"{sha0}@1.2"]) == [fid0, 901]  # ta sama geometria, dwa wpisy
    for kl, lk in pula.lekkie.items():
        assert lk.id == kl.split("@")[0] and lk.wspolczynnik in KRAZKI
    opis = json.dumps(pula.opis())
    assert not any(n in opis for n in NAZWISKA)


def test_pula_z_wpisow_wspolczynnik_domyslny_i_pusta(stl, tmp_path):
    p0 = stl[NAZWY[2]]
    pula = match.Pula.z_wpisow([wpis(p0, None, None, 1)], {1: p0}, wspolczynnik_domyslny=1.0)
    assert len(pula) == 1 and next(iter(pula.lekkie.values())).wspolczynnik == 1.0
    pusta = match.Pula.z_wpisow([], {})
    assert len(pusta) == 0 and pusta.liczniki["wpisow"] == 0


# --- pamiec podreczna na dysku ----------------------------------------------------------------------------------------
def test_pamiec_zimna_i_ciepla_te_same_projekty(stl, tmp_path):
    kat = tmp_path / "pamiec"
    wp, sciezki = wpisy_obu_krazkow(stl)
    pam1 = PP.PamiecPuli(kat)
    t0 = time.time()
    p1 = match.Pula.z_wpisow(wp, sciezki, pamiec=pam1)
    t_zimna = time.time() - t0
    assert pam1.statystyka["lekkie_policzone"] == len(p1) and pam1.statystyka["lekkie_z_dysku"] == 0
    assert len(pam1.pliki()) == len(p1)
    pam2 = PP.PamiecPuli(kat)  # nowy proces: wszystko z dysku
    t0 = time.time()
    p2 = match.Pula.z_wpisow(wp, sciezki, pamiec=pam2)
    t_ciepla = time.time() - t0
    assert pam2.statystyka["lekkie_z_dysku"] == len(p2) and pam2.statystyka["lekkie_policzone"] == 0
    assert t_ciepla < t_zimna
    nazwa = NAZWY[2]
    sha = synth.skrot_pliku(stl[nazwa])
    kl = f"{sha}@1.25"
    pr = p2.projekty[kl]  # projekt pelny z dysku
    assert pam2.statystyka["ciezkie_z_dysku"] == 1
    wzor = match.Projekt(stl[nazwa], 1.25)
    assert pr.id == wzor.id == sha and pr.wspolczynnik == 1.25
    np.testing.assert_array_equal(pr.T0, wzor.T0)
    np.testing.assert_array_equal(np.asarray(pr.chmura.points), np.asarray(wzor.chmura.points))
    np.testing.assert_array_equal(np.asarray(pr.chmura.normals), np.asarray(wzor.chmura.normals))
    np.testing.assert_array_equal(np.asarray(pr.fpfh.data), np.asarray(wzor.fpfh.data))
    np.testing.assert_array_equal(np.asarray(pr.siatka.vertices), np.asarray(wzor.siatka.vertices))
    assert (pr.obrys_xy, pr.wysokosc, pr.hull) == (wzor.obrys_xy, wzor.wysokosc, wzor.hull)
    assert pr.cechy.zeby == wzor.cechy.zeby == ["36"] and pr.cechy.typ == "korona"
    pts = np.asarray(wzor.chmura.points)[::50]
    np.testing.assert_allclose(pr.odleglosci(pts), wzor.odleglosci(pts), atol=1e-6)
    lk = p2.lekkie[kl]
    for g in (0.4, 1.0, 2.2, 3.7, wzor.wysokosc - 0.6, wzor.wysokosc + 1.0):  # profil filtru = Projekt.cechy_do_glebokosci
        (o1, h1), (o2, h2) = lk.cechy_do_glebokosci(g), wzor.cechy_do_glebokosci(g)
        np.testing.assert_allclose(o1, o2, rtol=1e-6, atol=1e-9)
        assert h1 == pytest.approx(h2, rel=1e-6, abs=1e-9)
    assert p2.projekty[kl] is pr and pam2.statystyka["ciezkie_z_pamieci"] >= 1  # drugi raz z pamieci procesu


def test_pamiec_uniewaznienie_zmieniony_plik_uszkodzony_wpis_i_sprzatanie(stl, tmp_path):
    kat = tmp_path / "pamiec"
    d = tmp_path / "stl"
    d.mkdir()
    p = d / NAZWY[1]
    shutil.copy(stl[NAZWY[1]], p)
    sha_stary = synth.skrot_pliku(p)
    match.Pula.z_wpisow([wpis(p, 1.22, 1, 1)], {1: p}, pamiec=PP.PamiecPuli(kat))
    assert len(PP.PamiecPuli(kat).pliki()) == 1
    shutil.copy(stl["2026-11-17_rozpraszacz1-14-crown_cad.stl"], p)  # ta sama sciezka, inna zawartosc (plik zmieniony po indeksowaniu)
    os.utime(p, ns=(time.time_ns() + 10**9, time.time_ns() + 10**9))
    pam = PP.PamiecPuli(kat)
    pula = match.Pula.z_wpisow([PL.Wpis(sha16=sha_stary, wspolczynnik=1.22, krazek=None, frezowanie_id=1, projekt_id=1, kuweta=None, zeby=None,
                                        typ=None, zrodlo_wspolczynnika="csv")], {1: p}, pamiec=pam)
    assert pula.liczniki["plik_zmieniony"] == 1 and pam.statystyka["lekkie_policzone"] == 1
    assert next(iter(pula.lekkie.values())).id == synth.skrot_pliku(p) != sha_stary  # geometria z biezacej zawartosci
    assert len(pam.pliki()) == 2
    for f in pam.pliki():  # uszkodzony plik pamieci = liczenie od nowa, bez wyjatku
        f.write_bytes(b"to nie jest npz")
    pam3 = PP.PamiecPuli(kat)
    match.Pula.z_wpisow([wpis(p, 1.22, 1, 1)], {1: p}, pamiec=pam3)
    assert pam3.statystyka["lekkie_policzone"] == 1 and pam3.statystyka["bledy_odczytu"] >= 1
    n = len(pam3.pliki())
    assert pam3.sprzataj(dni=14) == 0  # pliki uzywane przed chwila zostaja
    stary = time.time() - 30 * 86400
    for f in pam3.pliki():
        os.utime(f, (stary, stary))
    assert pam3.sprzataj(dni=14) == n and pam3.pliki() == []


def test_pamiec_bez_nazw_plikow(stl, tmp_path):
    kat = tmp_path / "pamiec"
    wp, sciezki = wpisy_obu_krazkow(stl)
    match.Pula.z_wpisow(wp, sciezki, pamiec=PP.PamiecPuli(kat))
    pliki = list(kat.rglob("*"))
    assert pliki
    for f in pliki:
        assert not any(n in f.name.lower() for n in NAZWISKA)
        if f.is_file():
            tresc = f.read_bytes().lower()
            assert not any(n.encode() in tresc for n in NAZWISKA), f.name


def test_pamiec_z_ustawien(tmp_path):
    ust = UST.wczytaj_ustawienia()
    ust = {**ust, "sciezki": {**ust["sciezki"], "pula_cache": str(tmp_path / "pula_cache")}}
    pam = PP.z_ustawien(ust)
    assert pam.katalog is not None and Path(pam.katalog).is_relative_to(tmp_path / "pula_cache")


# --- kryteria 1 i 2: dwa krazki, ten sam STL z dwoma wspolczynnikami --------------------------------------------------
def test_kryterium1_dwa_krazki_top1_wlasciwy_projekt_i_wpis(stl, plytka, ust, tmp_path):
    """Pula = prace plytki, kazda w skali swojego krazka (1,20 albo 1,25) + rozpraszacze: top-1 = wlasciwy projekt i wpis, zielony."""
    _, wyr, prawda = plytka
    wp, sciezki = [], {}
    for pid, p in enumerate(sorted(stl.values()), start=1):
        sciezki[pid] = p
        sha = synth.skrot_pliku(p)
        praca = next((x for x in prawda.prace if x.projekt == sha), None)
        w = praca.wspolczynnik if praca is not None else 1.22
        wp.append(wpis(p, w, 100 + pid, pid, KRAZKI.get(round(w, 2), "K-122")))
    pula = match.Pula.z_wpisow(wp, sciezki, pamiec=PP.PamiecPuli(tmp_path / "pamiec"))
    mapa = {x.gniazdo: x for x in prawda.prace}
    for f in wyr.fragmenty:
        r = match.dopasuj(f.punkty, f.normalne, pula, ust, f.gniazdo)
        k = r.najlepszy
        wl = wpis_prawdy(mapa[f.gniazdo], wp)
        assert k.id == mapa[f.gniazdo].projekt and k.frezowanie_id == wl.frezowanie_id and k.krazek == wl.krazek, (f.gniazdo, k.id, k.frezowanie_id)
        assert k.projekt_id == wl.projekt_id and k.wspolczynnik == pytest.approx(wl.wspolczynnik)
        assert r.status == "zielony" and k.pokrycie >= 0.85


def test_kryterium2_ten_sam_stl_z_dwoma_wspolczynnikami_wlasciwy_wpis(pula_obu, plytka, ust):
    """Kazdy STL w puli dwa razy (1,20 i 1,25): wynik wskazuje wpis krazka, na ktorym praca byla frezowana; pewnosc liczona
    wzgledem innych projektow (blizniak tego samego STL nie robi z pracy szarej)."""
    pula, wp, _ = pula_obu
    _, wyr, prawda = plytka
    mapa = {x.gniazdo: x for x in prawda.prace}
    for f in wyr.fragmenty:
        r = match.dopasuj(f.punkty, f.normalne, pula, ust, f.gniazdo)
        k = r.najlepszy
        wl = wpis_prawdy(mapa[f.gniazdo], wp)
        assert (k.id, k.frezowanie_id, k.krazek) == (wl.sha16, wl.frezowanie_id, wl.krazek), (f.gniazdo, [(x.id, x.wspolczynnik, x.pokrycie) for x in r.kandydaci[:4]])
        assert k.wpisy == [{"frezowanie_id": wl.frezowanie_id, "projekt_id": wl.projekt_id, "krazek": wl.krazek, "wspolczynnik": wl.wspolczynnik}]
        assert r.status == "zielony"


def test_bliskie_wspolczynniki_wpis_z_estymaty_skali(stl, plytka, ust, tmp_path):
    """Ten sam STL z wspolczynnikami 0,6 % od siebie (oba w oknie korekty skali): wybrany wpis o wspolczynniku blizszym
    estymacie ze skanu; 0,02 % od siebie (ponizej dokladnosci estymaty): oba wpisy w wyniku, frezowanie_id nieznane."""
    _, wyr, prawda = plytka
    praca = max(prawda.prace, key=lambda x: x.wspolczynnik)  # praca z krazka 1,25
    f = next(fr for fr in wyr.fragmenty if fr.gniazdo == praca.gniazdo)
    p = next(v for v in stl.values() if synth.skrot_pliku(v) == praca.projekt)
    inne = [v for v in stl.values() if v != p]
    for drugi, rozroznialne in ((praca.wspolczynnik * 1.006, True), (praca.wspolczynnik * 0.994, True), (praca.wspolczynnik * 1.0002, False)):
        wp = [wpis(p, praca.wspolczynnik, 1, 1, "K-A"), wpis(p, drugi, 2, 1, "K-B")] + [wpis(v, 1.22, 10 + i, 10 + i) for i, v in enumerate(inne)]
        sciezki = {1: p, **{10 + i: v for i, v in enumerate(inne)}}
        pula = match.Pula.z_wpisow(wp, sciezki, pamiec=PP.PamiecPuli(tmp_path / "pamiec"))
        r = match.dopasuj(f.punkty, f.normalne, pula, ust, f.gniazdo)
        k = r.najlepszy
        assert k.id == praca.projekt and r.status == "zielony", (drugi, [(x.wspolczynnik, x.pokrycie) for x in r.kandydaci[:3]])
        if rozroznialne:
            assert (k.frezowanie_id, k.krazek, len(k.wpisy)) == (1, "K-A", 1), (drugi, k.wpisy)
        else:
            assert k.frezowanie_id is None and k.krazek is None and k.projekt_id == 1
            assert sorted(x["frezowanie_id"] for x in k.wpisy) == [1, 2]
            assert any("wpis" in u for u in r.uwagi)


def test_ta_sama_geometria_w_dwoch_wpisach_bez_zgadywania(stl, plytka, ust, tmp_path):
    """Wieczor: ten sam STL na dwoch krazkach o tym samym wspolczynniku; rano: ten sam plik w dwoch zleceniach (projekt_id) -
    jedna geometria, wynik podaje oba wpisy, a krazka / zlecenia nie zgaduje (D6 recenzji A4)."""
    _, wyr, prawda = plytka
    praca = prawda.prace[0]
    f = next(fr for fr in wyr.fragmenty if fr.gniazdo == praca.gniazdo)
    p = next(v for v in stl.values() if synth.skrot_pliku(v) == praca.projekt)
    pam = PP.PamiecPuli(tmp_path / "pamiec")
    wp = [wpis(p, praca.wspolczynnik, 1, 5, "K-A"), wpis(p, praca.wspolczynnik, 2, 5, "K-B")]
    pula = match.Pula.z_wpisow(wp, {5: p}, pamiec=pam)
    assert len(pula) == 1
    k = match.dopasuj(f.punkty, f.normalne, pula, ust, f.gniazdo).najlepszy
    assert k.id == praca.projekt and k.frezowanie_id is None and k.krazek is None and k.projekt_id == 5 and len(k.wpisy) == 2
    rano = [wpis(p, praca.wspolczynnik, None, 5), wpis(p, praca.wspolczynnik, None, 6)]
    k = match.dopasuj(f.punkty, f.normalne, match.Pula.z_wpisow(rano, {5: p, 6: p}, pamiec=pam), ust, f.gniazdo).najlepszy
    assert k.projekt_id is None and sorted(x["projekt_id"] for x in k.wpisy) == [5, 6]


# --- ranking wstepny (duza pula) --------------------------------------------------------------------------------------
def test_ranking_wstepny_ogranicza_pelne_dopasowania(stl, pula_obu, plytka, ust, monkeypatch):
    pula, wp, _ = pula_obu
    _, wyr, prawda = plytka
    mapa = {x.gniazdo: x for x in prawda.prace}
    sha_trzonowy = synth.skrot_pliku(stl[NAZWY[2]])  # trzonowiec: 3 rozpraszacze podobnych wymiarow x 2 krazki = ranking wstepny
    f = next(fr for fr in wyr.fragmenty if mapa[fr.gniazdo].projekt == sha_trzonowy)
    fr = match.FragmentDoDopasowania.z_punktow(f.punkty, f.normalne)
    przeszly = [kl for kl, lk in pula.lekkie.items() if match.filtr(fr, lk, ust)[0]]
    if len(przeszly) <= match.WSTEPNY_PELNYCH:
        pytest.skip(f"za malo kandydatow po filtrze ({len(przeszly)}) - ranking wstepny nieaktywny dla tego fragmentu")
    wynik_wstepny = {kl: match.ocena_wstepna(fr, pula.lekkie[kl]) for kl in przeszly}
    wl = wpis_prawdy(mapa[f.gniazdo], wp)
    kl_wl = next(kl for kl in przeszly if pula.lekkie[kl].id == wl.sha16 and pula.lekkie[kl].wspolczynnik == wl.wspolczynnik)
    assert wynik_wstepny[kl_wl] == max(wynik_wstepny.values()) and wynik_wstepny[kl_wl] >= 0.8, wynik_wstepny
    wywolania = []
    oryg = match.dopasuj_pare
    monkeypatch.setattr(match, "dopasuj_pare", lambda *a, **k: wywolania.append(a[1]) or oryg(*a, **k))
    r = match.dopasuj(f.punkty, f.normalne, pula, ust, f.gniazdo)
    assert len(wywolania) <= match.WSTEPNY_PELNYCH
    assert r.najlepszy.frezowanie_id == wl.frezowanie_id and r.status == "zielony"
    wstepne = [k for k in r.kandydaci if k.metoda == "wstepny"]
    assert wstepne and all(k.pokrycie == 0.0 and k.pokrycie_wstepne is not None for k in wstepne)


def test_ratunek_bez_filtru_tez_przez_ranking(pula_obu, plytka, ust, monkeypatch):
    """Zaden projekt nie przechodzi filtru wymiarow: mala pula (do WSTEPNY_RATUNEK_WSZYSTKIE geometrii) dopasowana w calosci
    jak pula z folderu; duza pula - przez ranking wstepny (nie 400 pelnych dopasowan)."""
    pula, wp, _ = pula_obu
    _, wyr, prawda = plytka
    f = wyr.fragmenty[0]
    ust_z = {**ust, "match": {**ust["match"], "filtr_wymiar_mm": 0.0, "filtr_wymiar_udzial": 0.0, "filtr_objetosc_udzial": 0.0}}
    wywolania = []
    oryg = match.dopasuj_pare
    monkeypatch.setattr(match, "dopasuj_pare", lambda *a, **k: wywolania.append(1) or oryg(*a, **k))
    assert len(pula) <= match.WSTEPNY_RATUNEK_WSZYSTKIE
    r = match.dopasuj(f.punkty, f.normalne, pula, ust_z, f.gniazdo)
    assert any("dopasowano wszystkie" in u for u in r.uwagi) and len(wywolania) == len(pula)
    prawda_f = {x.gniazdo: x for x in prawda.prace}[f.gniazdo].projekt
    assert r.najlepszy.id == prawda_f
    wywolania.clear()
    monkeypatch.setattr(match, "WSTEPNY_RATUNEK_WSZYSTKIE", 4)  # jak pula kilkuset wpisow
    r = match.dopasuj(f.punkty, f.normalne, pula, ust_z, f.gniazdo)
    assert any("dopasowano wszystkie" in u for u in r.uwagi)
    assert len(wywolania) <= 2 * match.WSTEPNY_PELNYCH < len(pula)
    assert r.najlepszy.id == prawda_f


def test_stara_pula_bez_rankingu_wstepnego(stl, plytka, ust, monkeypatch):
    """Pula z folderu (dotychczasowe wywolanie porownaj): bez rankingu wstepnego i bez zmian pol kandydatow poza nowymi
    polami z wartosciami domyslnymi."""
    _, wyr, _ = plytka
    d = Path(next(iter(stl.values()))).parent
    pula = match.Pula([d], 1.22)
    assert not pula.per_praca
    monkeypatch.setattr(match, "ocena_wstepna", lambda *a, **k: (_ for _ in ()).throw(AssertionError("ranking wstepny w starej puli")))
    f = wyr.fragmenty[0]
    r = match.dopasuj(f.punkty, f.normalne, pula, {**ust, "match": {**ust["match"], "filtr_wymiar_mm": 1e9, "filtr_objetosc_udzial": 1e9}}, f.gniazdo)
    assert len(r.kandydaci) == len(pula) > match.WSTEPNY_PELNYCH
    for k in r.kandydaci:
        assert k.klucz == k.id and k.wpisy == [] and k.frezowanie_id is None and k.krazek is None and k.projekt_id is None
        assert k.wspolczynnik == 1.22 and k.pokrycie_wstepne is None and k.metoda in ("ransac", "obroty")


# --- porownaj z pula wpisow -------------------------------------------------------------------------------------------
def test_porownaj_z_pula_wpisow_i_cli(pula_obu, plytka, ust, tmp_path):
    pula, wp, sciezki = pula_obu
    skan, _, prawda = plytka
    plik_skanu = tmp_path / "skan_okragla_wieczorna.stl"
    skan.export(plik_skanu)
    wynik = PO.porownaj(plik_skanu, [], PO.AUTO, ust, None, None, "auto", False, pula)  # auto, bez wspolczynnika: pula wpisow zostaje
    assert wynik["wspolczynnik"] is None and wynik["pula_wpisy"]["wpisow"] == len(wp) and wynik["projekty"] == len(pula)
    mapa = {x.gniazdo: x for x in prawda.prace}
    for g in wynik["gniazda"]:
        k = g["kandydaci"][0]
        wl = wpis_prawdy(mapa[g["gniazdo"]], wp)
        assert (k["id"], k["frezowanie_id"], k["krazek"], k["klucz"]) == (wl.sha16, wl.frezowanie_id, wl.krazek, f"{wl.sha16}@{wl.wspolczynnik:g}")
        assert g["status"] == "zielony" and g["inspekcja"] is not None and g["skala"]["wspolczynnik_puli"] == pytest.approx(wl.wspolczynnik)
    csv = tmp_path / "wpisy.csv"
    csv.write_text("plik;wspolczynnik;krazek;frezowanie_id;projekt_id\n"
                   + "".join(f"{sciezki[w.projekt_id]};{str(w.wspolczynnik).replace('.', ',')};{w.krazek};{w.frezowanie_id};{w.projekt_id}\n" for w in wp),
                   encoding="utf-8")
    assert len(PO.wczytaj_wpisy(csv)) == len(wp)
    wyj = tmp_path / "wyjscie"
    w2 = PO.main(["--skan", str(plik_skanu), "--wpisy", str(csv), "--pamiec-puli", str(tmp_path / "pamiec_cli"), "--wyjscie", str(wyj),
                  "--bez-png", "--bez-inspekcji"])
    tekst = (wyj / "skan_okragla_wieczorna_wynik.json").read_text(encoding="utf-8").lower()
    assert not any(n in tekst for n in NAZWISKA)
    assert [g["kandydaci"][0]["frezowanie_id"] for g in w2["gniazda"]] == [g["kandydaci"][0]["frezowanie_id"] for g in wynik["gniazda"]]
    with pytest.raises(SystemExit):
        PO.main(["--skan", str(plik_skanu), "--wpisy", str(csv), "--projekty", str(tmp_path), "--bez-png"])  # albo --projekty, albo --wpisy


# --- kontrakt z A4: pula wieczorna z bazy -> pula match ----------------------------------------------------------------
def test_kontrakt_pula_wieczorna_z_katalogu(tmp_path):
    import datetime as dt
    teraz = dt.datetime(2026, 11, 17, 20, 0)
    cel = tmp_path / "drzewo"
    rng = np.random.default_rng(5)
    pliki = {"Testowski 3263 zs": ["2026-11-16_testowski-14-crown_cad.stl", "2026-11-16_testowski-15-crown_cad.stl"],
             "Probna 3301 kor": ["2026-11-16_probna-36-crown_cad.stl"]}
    for folder, nazwy in pliki.items():
        for n in nazwy:
            D.zapisz_stl(D.atrapa(rng), cel / "Cyrkon" / folder / n, dt.datetime(2026, 11, 16, 12))
    baza = B.otworz(tmp_path / "dane" / "stanowisko.sqlite")
    try:
        zrodla = {"cyrkon": cel / "Cyrkon", "prywatne": cel / "Prywatne"}
        I.indeksuj(baza, zrodla, teraz)
        csv = tmp_path / "millbox" / "wspolczynniki.csv"
        csv.parent.mkdir()
        csv.write_text("plik;krazek;wspolczynnik;data\n"
                       "2026-11-16_testowski-14-crown_cad.stl;K-1;1,2210;2026-11-17\n"
                       "2026-11-16_testowski-14-crown_cad.stl;K-2;1,2480;2026-11-17\n"   # ten sam STL, drugi krazek
                       "2026-11-16_testowski-15-crown_cad.stl;K-3;1,2210;2026-11-16\n"
                       "2026-11-16_probna-36-crown_cad.stl;K-4;1,2350;2026-11-17\n", encoding="utf-8")
        WS.wczytaj_do_bazy(baza, csv, teraz=teraz)
        pw = PL.pula_wieczorna(baza, teraz)
        assert len(pw.wpisy) == 4
        sciezki = PL.sciezki_plikow(baza, pw.wpisy, zrodla)
        pula = match.Pula.z_wpisow(pw.wpisy, sciezki, pamiec=PP.PamiecPuli(tmp_path / "pula_cache"))
        assert len(pula) == 4 and pula.liczniki["wpisow"] == 4 and pula.liczniki["brak_pliku"] == 0
        fids = sorted(w["frezowanie_id"] for ws in pula.wpisy_geometrii.values() for w in ws)
        assert fids == sorted(w.frezowanie_id for w in pw.wpisy)
        sciezki[pw.wpisy[0].projekt_id].unlink()  # D17: plik prawdziwie usuniety = wpis pominiety z licznikiem, nie blad
        pula2 = match.Pula.z_wpisow(pw.wpisy, sciezki, pamiec=PP.PamiecPuli(tmp_path / "pula_cache"))
        assert pula2.liczniki["brak_pliku"] == sum(1 for w in pw.wpisy if w.projekt_id == pw.wpisy[0].projekt_id) and len(pula2) < 4
    finally:
        baza.zamknij()
