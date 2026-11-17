"""Uklad gniazd R59 (14.11.2026, decyzje G0: wieczorna W-b, poranna P-e, jedna rynienka na plytke).

Liczby gniazd, srednice i pozycje sa liczone z ``../parametry.json`` (klucze ``ev_rows``, ``mo_rows``,
``*_marker_pos``, ``code_dimples_round``, ``plate_numbers_*``), nie ze stalych. Stale sa tylko trzy decyzje
wlasciciela z bramki G0: jedna rynienka na plytke (D3-a), gniazdo fi 15 na plytce porannej (D2) i brak
malych gniazd (wieczorna bez fi 9, poranna bez fi 7,5 i fi 10).

Poprzedni uklad R54 (stare plytki fizyczne) jest sprawdzany w pozostalych plikach testow na nazwach ``*_r54``;
tutaj tylko suma kontrolna jego plikow (dowod, ze stary uklad jest nietkniety).
"""
from __future__ import annotations

import hashlib
import json
import math
import warnings
from collections import Counter

import numpy as np
import pytest
import trimesh

import atrapy_koron
from conftest import RAMKI, STANOWISKO
from stanowisko import katalog as K, plate, synth, uklad as U

PAR = json.loads((RAMKI / "parametry.json").read_text(encoding="utf-8"))["plytka"]
NOWE = ("wieczorna", "poranna", "okragla_wieczorna", "okragla_poranna")
WIERSZE = {"wieczorna": "ev_rows", "poranna": "mo_rows"}
ZNACZNIKI = {"wieczorna": "ev_marker_pos", "poranna": "mo_marker_pos"}
NUMERY = {"wieczorna": "plate_numbers_ev", "poranna": "plate_numbers_mo"}
RYNIENEK_G0 = 1  # decyzja D3-a: jedna dluga rynienka na plytke
FI_PORANNA_G0 = 15  # decyzja D2: plytka poranna ma gniazda fi 15


def v(klucz: str):
    return PAR[klucz]["value"]


def kwadrat(nazwa: str) -> str:
    """Typ kwadratu, z ktorego plytka okragla bierze rzedy gniazd (K-05 h)."""
    return nazwa.replace("okragla_", "")


def gniazda_z_parametrow(nazwa: str) -> list[tuple]:
    """(typ, x, y, d, l, w) w kolejnosci id: wpisy rzedow po y, w rzedzie od prawej (x malejaco)."""
    wiersze = sorted(v(WIERSZE[kwadrat(nazwa)]), key=lambda r: r["y"])
    return [(r["type"], float(x), float(r["y"]), r.get("d"), r.get("l"), r.get("w")) for r in wiersze for x in sorted(r["x"], reverse=True)]


def odstep_obrysow(a: U.Gniazdo, b: U.Gniazdo) -> float:
    """Odleglosc obrysow gornych dwoch gniazd (okragle - okragle, okragle - rynienka)."""
    if a.okragle and b.okragle:
        return math.hypot(a.x - b.x, a.y - b.y) - a.d_top / 2 - b.d_top / 2
    if a.okragle != b.okragle:
        okr, ryn = (a, b) if a.okragle else (b, a)
        return ryn.odleglosc_do_obrysu(okr.x, okr.y) - okr.d_top / 2
    return min(a.odleglosc_do_obrysu(x, y) for x, y in b.obrys(360))


# --- liczby i pozycje z parametrow -------------------------------------------------------
@pytest.mark.parametrize("nazwa", NOWE)
def test_liczby_gniazd_i_srednice_z_parametrow(nazwa):
    uk = U.wczytaj(nazwa)
    par = gniazda_z_parametrow(nazwa)
    oczek = Counter((t, d if t == "round" else (l, w)) for t, _, _, d, l, w in par)
    jest = Counter((g.typ, g.d_top if g.okragle else (g.l, g.w)) for g in uk.sockets)
    assert jest == oczek and len(uk.sockets) == len(par)
    assert len(uk.gniazda_okragle()) == sum(1 for p in par if p[0] == "round")
    # decyzje G0 (stale): jedna rynienka, w porannej fi 15, bez malych gniazd
    assert len(uk.rynienki()) == sum(1 for p in par if p[0] == "trough") == RYNIENEK_G0
    srednice = {g.d_top for g in uk.gniazda_okragle()}
    if synth.poranna(nazwa):
        assert FI_PORANNA_G0 in srednice and min(srednice) > v("mo_socket_d_m")  # bez fi 7,5 i fi 10
    else:
        assert min(srednice) > v("ev_socket_d_s")  # bez fi 9


@pytest.mark.parametrize("nazwa", NOWE)
def test_uklad_json_zgodny_z_parametrami_takze_okragle(nazwa):
    uk = U.wczytaj(nazwa)
    par = gniazda_z_parametrow(nazwa)
    gn = sorted(uk.sockets, key=lambda g: g.id)
    assert [g.id for g in gn] == list(range(1, len(par) + 1))  # id po y wpisu rzedu, w rzedzie od prawej
    assert [(g.typ, g.x, g.y, g.d_top, g.l, g.w) for g in gn] == par
    tan = math.tan(math.radians(v("socket_wall_angle")))
    for g in gn:
        assert g.depth == v("socket_depth") and g.z_top == v("plate_thickness")
        if g.okragle:
            assert g.d_bottom == pytest.approx(g.d_top - 2 * g.depth * tan, abs=0.01)
    pozycje = v(ZNACZNIKI[kwadrat(nazwa)])
    assert sorted(m.corner for m in uk.markers) == sorted(pozycje)
    for m in uk.markers:
        assert [m.x, m.y] == pozycje[m.corner] and m.d == v("marker_cone_d") and m.depth == v("marker_cone_depth")
    if uk.shape == "round":
        assert uk.d == v("plate_round_d") and uk.flat["chord_w"] == v("round_flat_w") and uk.flat["angle_deg"] == v("round_flat_angle")
        dolki = v("code_dimples_round")[kwadrat(nazwa)]
        assert [d.bit for d in uk.code_dimples] == list(dolki)
        assert all([d.x, d.y] == dolki[d.bit] for d in uk.code_dimples)
    else:
        assert uk.size == v("plate_size")
        abc = [[v("code_dimple_x"), v("code_dimple_y0") + i * v("code_dimple_pitch")] for i in range(3)]
        assert [[d.x, d.y] for d in uk.code_dimples] == abc + [v("code_bit_d_pos")]
    assert all(d.d == v("code_dimple_d") and d.depth == v("code_dimple_depth") for d in uk.code_dimples)
    assert uk.thickness == v("plate_thickness")


@pytest.mark.parametrize("nazwa", NOWE)
def test_plytki_okragle_maja_gniazda_kwadratu(nazwa):
    uk, kw = U.wczytaj(nazwa), U.wczytaj(kwadrat(nazwa))
    assert [(g.id, g.typ, g.x, g.y, g.d_top, g.l, g.w) for g in uk.sockets] == [(g.id, g.typ, g.x, g.y, g.d_top, g.l, g.w) for g in kw.sockets]
    assert [(m.corner, m.x, m.y) for m in uk.markers] == [(m.corner, m.x, m.y) for m in kw.markers]


@pytest.mark.parametrize("nazwa", NOWE)
def test_scianki_i_kolo_pola_skanowania(nazwa):
    """Wszystkie pary obrysow >= socket_wall_min (takze okragle - rynienka); wszystko w kole socket_zone_r i w strefie socket_zone."""
    uk = U.wczytaj(nazwa)
    sciana, r_kola, pol_strefy = v("socket_wall_min"), v("socket_zone_r"), v("socket_zone") / 2
    gn = uk.sockets
    for i, a in enumerate(gn):
        for b in gn[i + 1:]:
            assert odstep_obrysow(a, b) >= sciana - 1e-6, (a.id, b.id, odstep_obrysow(a, b))
    for g in gn:
        assert max(math.hypot(x, y) for x, y in g.obrys(360)) <= r_kola + 1e-6, g.id
        assert max(max(abs(x), abs(y)) for x, y in g.obrys(360)) <= pol_strefy + 1e-6, g.id
    for m in uk.markers:  # stozki znacznikow: w kole pola i >= scianka od gniazd
        assert math.hypot(m.x, m.y) + m.d / 2 <= r_kola + 1e-6, m.corner
        for g in gn:
            assert g.odleglosc_do_obrysu(m.x, m.y) - m.d / 2 >= sciana - 1e-6, (m.corner, g.id)
    boki = sorted(math.hypot(a.x - b.x, a.y - b.y) for i, a in enumerate(uk.markers) for b in uk.markers[i + 1:])
    assert boki[1] - boki[0] > 0.5 and boki[2] - boki[1] > 0.5, boki  # trojkat nierownoboczny: orientacja jednoznaczna
    if uk.shape == "round":  # dolki kodu w polu skanowania, poza gniazdami i stozkami
        for d in uk.code_dimples:
            assert math.hypot(d.x, d.y) + d.d / 2 <= r_kola + 1e-6
            assert all(g.odleglosc_do_obrysu(d.x, d.y) - d.d / 2 >= sciana - 1e-6 for g in gn), d.bit
            assert all(math.hypot(d.x - m.x, d.y - m.y) - d.d / 2 - m.d / 2 > 0 for m in uk.markers), d.bit


@pytest.mark.parametrize("nazwa", NOWE)
def test_pliki_stl_dla_wszystkich_numerow(nazwa):
    uk = U.wczytaj(nazwa)
    numery = v("plate_numbers_round")[kwadrat(nazwa)] if uk.shape == "round" else v(NUMERY[nazwa])
    assert uk.numery == sorted(numery)
    for n in numery:
        m = trimesh.load(uk.plik_stl(n), force="mesh")
        assert m.is_watertight and m.bounds[1, 2] >= uk.thickness - 1e-6  # wierzch na z = thickness (relief numeru wyzej)
    assert (uk.katalog / U.PLIK_PLYTKI_BAZOWEJ).exists() == (uk.shape == "round")
    assert U.wczytaj(nazwa + "_r54").numery == uk.numery  # D5-A: te same numery w obu ukladach


# --- pliki modeli: suma kontrolna (R59 = wyniki_v2 z R59-A; *_r54 = pliki sprzed R59) ---------------
SHA_MODELI = {
    "wieczorna/uklad.json": "7ae07ba861950724cf68ce9de0b45f3a05436089df8f73b3b4fc07bf2cc05869",
    "wieczorna/plytka_n1.stl": "3b0db5452a0cd9533464772c10b67c05fa7a006fcdb3d140a74af275e79946f7",
    "wieczorna/plytka_n2.stl": "b87026134b25cf32a84a231b73d5c4eb9fde4dfeb5b16b627cf09ccc3f29c999",
    "wieczorna/plytka_n3.stl": "59e615d596771c6c0351284c710e94e406a965afef423ffeae5cd18ffa2c4dd3",
    "poranna/uklad.json": "46e474b759c4b78b7975fc8c5580c9916a4cc64c6a88cd4711b2207e3978b98b",
    "poranna/plytka_n4.stl": "20f15f2214f6c9a9baf2b4701e7f99bfbc5f739b6379398294e9f931b8763237",
    "poranna/plytka_n5.stl": "a275775b9c9b5ddd015b68659f213505bdd28b9476cad5e13405bef2df5b64d1",
    "poranna/plytka_n6.stl": "c44be370c8b9ad2b70f9e486c3f6f9d2b227b91f2a6544bfe14bf7e66bd65b21",
    "okragla_wieczorna/uklad.json": "c07791f4bb976be2ad5eddaaeefe011b2384ea71e3fabd25cf55da690eb14a33",
    "okragla_wieczorna/plytka_n8.stl": "d5591f652ea1b6b23825abb5ad05ac12b78d17f6abb52946bd1a010ef5e4ff54",
    "okragla_wieczorna/plytka_bazowa.stl": "aad8033e6c1d1f34b43825861d18e82b45599a76ebb453c294400a7713ebbd83",
    "okragla_poranna/uklad.json": "b943e6c5dd54a8b3b35974908a3910bd654062bb659284a649ee68679174268e",
    "okragla_poranna/plytka_n9.stl": "f9444e6f14e37d9d0bcc8ae84cfec5249146bce20420c53a86a73965727fd4c4",
    "okragla_poranna/plytka_bazowa.stl": "e35835d7618e6665fdda84cbe2d65a3c7b46d7f9cef1e99141b42af2eb9e22c7",
}
SHA_MODELI_R54 = {
    "wieczorna_r54/uklad.json": "a4648f3562105bb19809bd7671e6421461f51fa2a4f29b5ecf0e1d6f29d1fb1e",
    "wieczorna_r54/plytka_n1.stl": "515d32d3dd8a69ae0a94d293a639b201f2d9ce9af19df664ad1b44b59408f775",
    "wieczorna_r54/plytka_n2.stl": "360cff9ddd6bbcf8a84b463fed930532612a38118006f1550c2df01b02fa852d",
    "wieczorna_r54/plytka_n3.stl": "2fc7040e212ace4a8efda17f61909ca09563009513adcd82ecf5bcaac3e98aaf",
    "poranna_r54/uklad.json": "6e8290c3a7c4becd3b065f8ccd39da9e8f8a2f0cb9bab6a1464fbcda84995812",
    "poranna_r54/plytka_n4.stl": "a8d07cbeb0dafc0e55d3fe2fe516c7d3e854a6259bce587785b796d34b54c65e",
    "poranna_r54/plytka_n5.stl": "159503ca4cd66b90a1e2441cae64016901ed83390b48a27345f9484ac1a05830",
    "poranna_r54/plytka_n6.stl": "0d5d712d42084a19846f24d385484d01b2254c5c1ec3945d71cfd3493816f15e",
    "okragla_wieczorna_r54/uklad.json": "260f807c630211dcd3c1b552cded03838d1367156c856fc51f3a3f7ec12f0743",
    "okragla_wieczorna_r54/plytka_n8.stl": "c4c8a18d0b83fd2a2903f5d782188a8de4827ee07c55dca9df7bd0d8e4a37d32",
    "okragla_wieczorna_r54/plytka_bazowa.stl": "3ca8178262f7f1f253480ca1d49adbbccf2db3648647814ec2390311e5553ace",
    "okragla_poranna_r54/uklad.json": "5adcc977dd9b456e5261d1e2225bc386def23a165d79de124b5733fb9ef43d53",
    "okragla_poranna_r54/plytka_n9.stl": "a87bc6c5f8f0323bc202e5ebfeab6be6d7c8432beba6aafe4a8372d70666e2be",
    "okragla_poranna_r54/plytka_bazowa.stl": "713aef6c0cef1dc2fc3b3809ce3756557b41b0cc4268c85166e985f18f74e0dd",
}


@pytest.mark.parametrize("tabela", [SHA_MODELI, SHA_MODELI_R54], ids=["r59", "r54"])
def test_pliki_modeli_bajtowo_bez_zmian(tabela):
    """Modele R59 = pliki z ``wyniki_v2`` (lista SHA w ``R59_wdrozenie_zmiany.md`` pkt 0); modele ``*_r54`` = pliki sprzed R59."""
    kat = STANOWISKO / "modele_plytek"
    for wzgl, sha in tabela.items():
        assert hashlib.sha256((kat / wzgl).read_bytes()).hexdigest() == sha, wzgl
    foldery = {w.split("/")[0] for w in tabela}
    assert {f"{p.parent.name}/{p.name}" for f in foldery for p in (kat / f).iterdir()} == set(tabela)  # zadnych innych plikow


# --- generator i katalog na ukladzie R59 -----------------------------------------------------
def test_generuj_plytke_puste_gniazda_z_parametrow(korony):
    uk = U.wczytaj("wieczorna")
    op = synth.Opcje(ubytki_na_prace=(0, 0), prace_na_plytce=3)
    _, prawda = synth.generuj_plytke(uk, 1, korony, np.random.default_rng(5), op, seed=5)
    assert len(prawda.prace) == 3 and prawda.plytka == "wieczorna"
    assert len(prawda.gniazda_puste) == len(gniazda_z_parametrow("wieczorna")) - 3


def _dwa_mosty(tmp_path):
    pliki = []
    for i in (1, 2):
        p = tmp_path / f"most{i}.stl"
        atrapy_koron.most(np.random.default_rng(i)).export(p)
        pliki.append(p)
    return pliki


@pytest.mark.parametrize("nazwa", NOWE)
def test_jedna_rynienka_jeden_most_drugi_pominiety(nazwa, tmp_path):
    """D3-a: most trafia do rynienki, drugi most nie ma gdzie lezec -> ``pominiete``; plate nie widzi ``podwojny``."""
    uk = U.wczytaj(nazwa)
    mosty = _dwa_mosty(tmp_path)
    assert all(synth.szerokosc_pracy(trimesh.load(p, force="mesh")) > synth.PROG_MOSTU_MM for p in mosty)
    op = synth.Opcje.z_toml(plytka=nazwa, ubytki_na_prace=(0, 0), wspolczynnik=(1.0, 1.0))  # atrapa mostu x 1,22 nie wchodzi w rynienke 60 x 15
    with pytest.warns(UserWarning, match="1 projekt"):
        skan, prawda = synth.generuj_plytke(uk, uk.numery[0], mosty, np.random.default_rng(3), op, seed=3)
    ryn = uk.rynienki()[0]
    assert [p.gniazdo for p in prawda.prace] == [ryn.id] and len(prawda.pominiete) == 1
    assert prawda.pominiete[0] in {synth.skrot_pliku(p) for p in mosty} and prawda.pominiete[0] != prawda.prace[0].projekt
    assert ryn.id not in prawda.gniazda_puste and len(prawda.gniazda_puste) == len(uk.sockets) - 1
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        w = plate.wyrownaj(skan, uk, numer=uk.numery[0])
    assert [(f.gniazdo, f.status) for f in w.fragmenty if f.status != "drobny"] == [(ryn.id, "praca")]
    assert w.gniazda_podwojne == [] and set(w.gniazda_puste) == set(prawda.gniazda_puste)


def test_praca_poza_gniazdem_i_dwie_w_rynience(korony):
    """Jak test_plate.test_praca_poza_gniazdem_i_podwojna, ale miejsca liczone z ukladu R59 (nie ze stalych)."""
    uk = U.wczytaj("okragla_wieczorna")
    rng = np.random.default_rng(3)
    op = synth.Opcje.z_toml(plytka=uk.nazwa, prace_na_plytce=1, p_drgniecia=0.0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        skan, prawda = synth.generuj_plytke(uk, 8, list(korony[:1]), rng, op, 3)
    duze = sorted((g for g in uk.gniazda_okragle() if g.d_top == max(x.d_top for x in uk.gniazda_okragle())), key=lambda g: (g.y, -g.x))
    a, b = duze[0], duze[1]  # dwa sasiednie gniazda najwiekszej srednicy w jednym rzedzie: srodek scianki miedzy nimi
    mx, my = (a.x + b.x) / 2, (a.y + b.y) / 2
    assert a.y == b.y and uk.najblizsze_gniazdo(mx, my, 1.0) is None
    k1 = trimesh.load(korony[0], force="mesh")
    k1.apply_transform(synth.orientacja_brzegiem_do_gory(k1))
    k1.apply_translation([mx - k1.centroid[0], my - k1.centroid[1], uk.thickness - k1.bounds[0, 2]])
    ryn = uk.rynienki()[0]
    assert ryn.id not in {p.gniazdo for p in prawda.prace}
    czesci = [skan, k1]
    for znak, plik in ((-1, korony[0]), (1, korony[1])):
        k = trimesh.load(plik, force="mesh")
        k.apply_transform(synth.orientacja_brzegiem_do_gory(k))
        k.apply_translation([ryn.x + znak * ryn.l / 4 - k.centroid[0], ryn.y - k.centroid[1], ryn.z_dno + 1.0 - k.bounds[0, 2]])
        czesci.append(k)
    szum = np.random.default_rng(1)
    for k in czesci[1:]:
        k.vertices += szum.normal(0, 0.02, k.vertices.shape)
    w = plate.wyrownaj(trimesh.util.concatenate(czesci), uk)
    assert w.numer == 8
    poza = w.poza_gniazdem
    assert len(poza) == 1 and abs(poza[0].srodek[0] - mx) < 1.5 and abs(poza[0].srodek[1] - my) < 1.5
    assert w.gniazda_podwojne == [ryn.id]
    assert sum(1 for f in w.fragmenty if f.status == "podwojny" and f.gniazdo == ryn.id) == 2
    assert {f.gniazdo for f in w.fragmenty if f.status == "praca"} == {p.gniazdo for p in prawda.prace}


@pytest.mark.parametrize("nazwa", ["poranna", "okragla_poranna"])
def test_najwieksza_korona_trafia_do_fi15_w_porannej(nazwa):
    """D2: korona, ktora nie wchodzi w fi 12,5 (skala 1,0), laduje w fi 15 bez przenikania (<= 1e-6 mm)."""
    uk = U.wczytaj(nazwa)
    srednice = sorted({g.d_top for g in uk.gniazda_okragle()})
    assert srednice[-1] == FI_PORANNA_G0 and len(srednice) >= 2
    mniejsze = next(g for g in uk.gniazda_okragle() if g.d_top == srednice[-2])
    duze = next(g for g in uk.gniazda_okragle() if g.d_top == srednice[-1])
    W, L, H, guzki, amp = atrapy_koron.TYPY["trzonowy"]
    znaleziona = None
    for skala in np.arange(1.0, 1.6, 0.02):  # coraz wieksza korona: pierwsza, ktora nie wchodzi w mniejsze gniazdo
        m = atrapy_koron.korona(W * skala, L * skala, H, guzki, amp, n_theta=96, n_u=120, rng=np.random.default_rng(11))
        m.apply_transform(synth.orientacja_brzegiem_do_gory(m))
        if all(synth.osadz_w_gniezdzie(m, mniejsze, np.random.default_rng(s)) is None for s in range(5)):
            znaleziona = m
            break
    assert znaleziona is not None
    assert [g.d_top for g in synth.kandydaci_gniazd(znaleziona, uk.gniazda_okragle(), uk.rynienki()) if g.okragle][-1] == FI_PORANNA_G0
    osadzen = 0
    for s in range(10):
        T = synth.osadz_w_gniezdzie(znaleziona, duze, np.random.default_rng(s))
        if T is not None:
            osadzen += 1
            assert synth.przenikanie(trimesh.transform_points(znaleziona.vertices, T), duze) <= 1e-6
    assert osadzen == 10
    odwr = znaleziona.copy()  # katalog obraca projekt sam: wejscie w ukladzie pliku (brzeg na dole)
    odwr.apply_transform(synth.orientacja_brzegiem_do_gory(odwr, "brzeg_dol"))
    assert K.gniazdo_dla(odwr, uk, 1.0, "brzeg_dol") == {"typ": "round", "d_top": FI_PORANNA_G0}


@pytest.mark.parametrize("nazwa", ["wieczorna", "poranna"])
def test_katalog_most_do_jedynej_rynienki(nazwa):
    uk = U.wczytaj(nazwa)
    ryn = next(p for p in gniazda_z_parametrow(nazwa) if p[0] == "trough")
    most = atrapy_koron.most(np.random.default_rng(1))
    assert K.gniazdo_dla(most, uk, 1.0) == {"typ": "trough", "l": ryn[4], "w": ryn[5]}
    duza = trimesh.creation.box([ryn[4] - 10.0, ryn[5] * 2, 6.0])
    g = K.gniazdo_dla(duza, uk, 1.0, "brzeg_gora")
    assert g["typ"] is None and "nie mie" in g["powod"]
    za_szeroka = trimesh.creation.box([ryn[4] - 10.0, ryn[5] - 0.2, 5.0])  # szersza niz w - 0,4
    assert synth.osadz_w_gniezdzie(za_szeroka, uk.rynienki()[0], np.random.default_rng(0)) is None


def test_kandydaci_gniazd_korona_potem_jedyna_rynienka():
    uk = U.wczytaj("wieczorna")
    m = trimesh.creation.box([18.0, 6.0, 5.0])  # 18 < 20: "korona", za szeroka na okragle -> rynienka na koncu listy
    k = synth.kandydaci_gniazd(m, uk.gniazda_okragle(), uk.rynienki())
    okr = [g for g in k if g.okragle]
    assert [g.okragle for g in k] == [True] * len(okr) + [False] * len(uk.rynienki()) and len(uk.rynienki()) == RYNIENEK_G0
    assert [g.d_top for g in okr] == sorted(g.d_top for g in okr) and min(g.d_top for g in okr) >= 0.55 * 18
    m2 = trimesh.creation.box([25.0, 6.0, 5.0])
    assert [g.id for g in synth.kandydaci_gniazd(m2, uk.gniazda_okragle(), uk.rynienki())] == [g.id for g in uk.rynienki()]
