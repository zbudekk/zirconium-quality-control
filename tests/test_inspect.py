"""Testy inspekcji ukruszen (qc.inspect) na syntetycznych skanach z prawda.

Fragment = skan pracy, T = prawda.T_projekt_do_skanu (dopasowanie idealne, bez modulu match).
Projekty losowane z puli 30 deterministycznie. Zestawy skanow i wynikow sprawdz() sa liczone raz na
sesje (fixture `bank`) i wspoldzielone przez testy o tych samych parametrach.

Kontrakt metryki.porownaj: Porownanie.pary = lista par (Ubytek wykryty, UbytekPrawda).
"""

import os
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pytest

from qc.syntetyka import prawda as modul_prawdy
from qc.syntetyka import skan as modul_skan
from qc.ustawienia import katalog_repo, wczytaj

TOLERANCJA_MM = 0.5


# --- pomocnicze ---------------------------------------------------------------


def _inspect():
    import qc.inspect as modul

    return modul


def _metryki():
    from qc.inspect import metryki

    return metryki


def przenies(T, punkt):
    """Punkt z ukladu projektu do ukladu fragmentu przez T (4x4)."""
    p = np.append(np.asarray(punkt, dtype=np.float64), 1.0)
    return (np.asarray(T, dtype=np.float64) @ p)[:3]


def losuj_ubytki(rng, n, srednica, glebokosc):
    return [
        {"srednica_mm": float(rng.uniform(*srednica)), "glebokosc_mm": float(rng.uniform(*glebokosc))}
        for _ in range(n)
    ]


def przygotuj_prace(pula, ziarno, n, ubytki=None, **kw):
    """Lista n zadan (projekt, ziarno skanu, kwargs skan_pracy); projekty losowane z puli z ziarna.

    ubytki = None (bez ubytkow), int (liczba, rozmiary z generatora) albo
    (liczba, (srednica_min, srednica_max), (glebokosc_min, glebokosc_max)).
    """
    rng = np.random.default_rng(ziarno)
    indeksy = rng.choice(len(pula), size=n, replace=n > len(pula))
    zadania = []
    for i, ind in enumerate(indeksy):
        argumenty = dict(kw)
        if isinstance(ubytki, tuple):
            argumenty["ubytki"] = losuj_ubytki(rng, *ubytki)
        elif ubytki:
            argumenty["ubytki"] = ubytki
        zadania.append((pula[int(ind)].siatka, ziarno * 1000 + i, argumenty))
    return zadania


def _licz(zadanie, ustawienia, inspekcja=True):
    projekt, ziarno, kw = zadanie
    fragment, prawda = modul_skan.skan_pracy(projekt, ziarno=ziarno, **kw)
    wynik = _inspect().sprawdz(fragment, projekt, prawda.T_projekt_do_skanu, ustawienia) if inspekcja else None
    return {"projekt": projekt, "fragment": fragment, "prawda": prawda, "wynik": wynik}


def licz_rownolegle(zadania, ustawienia, inspekcja=True):
    watki = min(8, os.cpu_count() or 1)
    with ThreadPoolExecutor(max_workers=watki) as pula_watkow:
        return list(pula_watkow.map(lambda z: _licz(z, ustawienia, inspekcja), zadania))


def porownaj(rekord, tolerancja_mm=TOLERANCJA_MM):
    p = rekord["prawda"]
    return _metryki().porownaj(rekord["wynik"], p, p.T_projekt_do_skanu, tolerancja_mm=tolerancja_mm)


def sumuj(rekordy):
    """(wykryte, pominiete, falszywe, liczba prac z falszywym alarmem, porownania)."""
    porownania = [porownaj(r) for r in rekordy]
    return (
        sum(c.wykryte for c in porownania),
        sum(c.pominiete for c in porownania),
        sum(c.falszywe for c in porownania),
        sum(1 for c in porownania if c.falszywe > 0),
        porownania,
    )


# --- fixtures -----------------------------------------------------------------


@pytest.fixture(scope="session")
def ustawienia():
    return wczytaj(katalog_repo() / "ustawienia.toml")


ZESTAWY = {
    # nazwa: (ziarno, liczba prac, ubytki, kwargs skan_pracy)
    "duze": (101, 20, (3, (0.4, 0.6), (0.12, 0.3)), dict(szum_mm=0.02)),
    "srednie": (102, 20, (3, (0.3, 0.4), (0.10, 0.2)), dict(szum_mm=0.02)),
    "male": (103, 20, (3, (0.2, 0.3), (0.08, 0.15)), dict(szum_mm=0.02)),
    "szum_0_04": (104, 20, (3, (0.4, 0.6), (0.15, 0.3)), dict(szum_mm=0.04)),
    "czyste_0_03": (105, 30, None, dict(szum_mm=0.03)),
    "poprawki": (106, 10, None, dict(szum_mm=0.02)),
    "skala": (107, 10, 2, dict(szum_mm=0.02, wspolczynnik=1.22)),
}


@pytest.fixture(scope="session")
def bank(pula30, ustawienia):
    """Fabryka: bank(nazwa) -> lista rekordow {projekt, fragment, prawda, wynik} (liczona raz)."""
    pamiec = {}

    def _bank(nazwa):
        if nazwa not in pamiec:
            ziarno, n, ubytki, kw = ZESTAWY[nazwa]
            zadania = przygotuj_prace(pula30, ziarno, n, ubytki, **kw)
            if nazwa == "poprawki":
                rng = np.random.default_rng(ziarno + 1)
                zadania = [
                    (p, z, dict(a, poprawki=losuj_ubytki(rng, 1, (2.5, 4.0), (0.08, 0.2))))
                    for p, z, a in zadania
                ]
            pamiec[nazwa] = licz_rownolegle(zadania, ustawienia)
        return pamiec[nazwa]

    return _bank


# --- testy --------------------------------------------------------------------


def test_mapa_bez_ubytkow(pula30, skan, ustawienia):
    projekt = pula30[3].siatka
    fragment, prawda = skan(projekt, szum_mm=0.02)
    mapa = _inspect().mapa_odchylek(fragment, projekt, prawda.T_projekt_do_skanu, ustawienia)
    n = len(fragment.vertices)
    assert mapa.punkty.shape == (n, 3)
    assert mapa.odleglosci.shape == (n,)
    assert mapa.normalne_projektu.shape == (n, 3)
    assert mapa.przy_brzegu.shape == (n,) and mapa.przy_brzegu.dtype == bool
    d = np.asarray(mapa.odleglosci)
    assert np.percentile(np.abs(d), 95) < 0.06
    assert abs(float(np.mean(d))) < 0.005
    udzial = float(np.mean(mapa.przy_brzegu))
    assert 0.1 <= udzial <= 0.6, udzial


def test_wykrywa_ubytki_duze(bank):
    rekordy = bank("duze")
    wykryte, pominiete, falszywe, _, porownania = sumuj(rekordy)
    print(f"duze: wykryte {wykryte}/60, pominiete {pominiete}, falszywe {falszywe}")
    assert wykryte >= 54
    assert falszywe <= 2
    for c in porownania:
        for wykryty, prawdziwy in c.pary:
            assert abs(wykryty.srednica_mm - prawdziwy.srednica_mm) <= 0.5 * prawdziwy.srednica_mm, (
                wykryty, prawdziwy)
            assert abs(wykryty.glebokosc_mm - prawdziwy.glebokosc_mm) <= 0.5 * prawdziwy.glebokosc_mm, (
                wykryty, prawdziwy)


def test_wykrywa_ubytki_srednie(bank):
    wykryte, pominiete, falszywe, _, _ = sumuj(bank("srednie"))
    print(f"srednie: wykryte {wykryte}/60, pominiete {pominiete}, falszywe {falszywe}")
    assert wykryte >= 48


def test_ubytki_male_raport(bank):
    wykryte, pominiete, falszywe, _, _ = sumuj(bank("male"))
    print(f"male (0,2-0,3 mm): wykryte {wykryte}/60, pominiete {pominiete}, falszywe {falszywe}")
    assert wykryte >= 30


def test_szum_0_04(bank):
    wykryte, pominiete, falszywe, prace_z_alarmem, _ = sumuj(bank("szum_0_04"))
    print(f"szum 0,04: wykryte {wykryte}/60, pominiete {pominiete}, falszywe {falszywe}")
    assert wykryte >= 45
    assert prace_z_alarmem <= 2


def test_falszywe_alarmy(bank):
    rekordy = bank("czyste_0_03")
    assert len(rekordy) == 30
    z_alarmem = sum(1 for r in rekordy if len(r["wynik"].ubytki) >= 1)
    assert z_alarmem <= 3, z_alarmem


def test_poprawka_nie_alarm(bank):
    rekordy = bank("poprawki")
    assert all(len(r["prawda"].ubytki) == 1 and r["prawda"].ubytki[0].rodzaj == "poprawka" for r in rekordy)
    ukruszen = sum(len(r["wynik"].ubytki) for r in rekordy)
    z_poprawka = sum(1 for r in rekordy if len(r["wynik"].poprawki) > 0)
    assert ukruszen <= 1, ukruszen
    assert z_poprawka >= 7, z_poprawka


def test_poprawka_i_ubytek(pula30, skan, ustawienia):
    projekt = pula30[7].siatka
    fragment, prawda = skan(projekt, szum_mm=0.02, ubytki=[{"srednica_mm": 0.5, "glebokosc_mm": 0.2}],
                            poprawki=1)
    wynik = _inspect().sprawdz(fragment, projekt, prawda.T_projekt_do_skanu, ustawienia)
    c = _metryki().porownaj(wynik, prawda, prawda.T_projekt_do_skanu, tolerancja_mm=0.5)
    assert c.wykryte == 1
    assert len(wynik.ubytki) == 1


def test_drgniecie(pula30, bank, ustawienia):
    inspect = _inspect()
    zadania = przygotuj_prace(pula30, 108, 5, None, szum_mm=0.02, drgniecie=True)
    drgniete = licz_rownolegle(zadania, ustawienia, inspekcja=False)
    for r in drgniete:
        T = r["prawda"].T_projekt_do_skanu
        assert inspect.wykryj_drgniecie(r["fragment"], r["projekt"], T, ustawienia) is True
    normalne = bank("czyste_0_03")[:20]
    falszywe = [
        i for i, r in enumerate(normalne)
        if inspect.wykryj_drgniecie(r["fragment"], r["projekt"], r["prawda"].T_projekt_do_skanu, ustawienia)
    ]
    assert falszywe == []
    assert all(r["wynik"].drgniecie is False for r in normalne)
    r = drgniete[0]
    wynik = inspect.sprawdz(r["fragment"], r["projekt"], r["prawda"].T_projekt_do_skanu, ustawienia)
    assert wynik.drgniecie is True
    assert wynik.ubytki == []


def test_skala_wieczorna(bank):
    rekordy = bank("skala")
    assert all(abs(r["prawda"].wspolczynnik - 1.22) < 1e-9 for r in rekordy)
    wykryte, pominiete, falszywe, _, _ = sumuj(rekordy)
    print(f"skala 1,22: wykryte {wykryte}/20, pominiete {pominiete}, falszywe {falszywe}")
    assert wykryte >= 17


def _srodek_nad_brzegiem(projekt, odleglosc_mm=3.5):
    """Wierzcholek powierzchni zewnetrznej ok. odleglosc_mm od krzywej brzegu."""
    v = np.asarray(projekt.vertices, dtype=np.float64)
    n = modul_skan.normalne_wierzcholkow(v, np.asarray(projekt.faces))
    krzywa = modul_skan.brzeg(projekt)
    os_xy = krzywa[:, :2].mean(axis=0)
    radialny = np.zeros_like(v)
    radialny[:, :2] = v[:, :2] - os_xy
    radialny /= np.linalg.norm(radialny, axis=1, keepdims=True) + 1e-12
    kand = np.flatnonzero((np.einsum("ij,ij->i", n, radialny) > 0.7) & (v[:, 2] > 1.0))
    kand = kand[np.abs(v[kand, 2] - odleglosc_mm) < 0.6][::7]
    od_brzegu = np.array([np.min(np.linalg.norm(krzywa - v[i], axis=1)) for i in kand])
    i = int(kand[np.argmin(np.abs(od_brzegu - odleglosc_mm))])
    return v[i], float(np.min(np.linalg.norm(krzywa - v[i], axis=1)))


def test_ubytek_poza_pasem(pula30, skan, ustawienia):
    projekt = pula30[0].siatka
    srodek, od_brzegu = _srodek_nad_brzegiem(projekt, 3.5)
    assert 3.0 <= od_brzegu <= 4.0, od_brzegu
    assert od_brzegu > ustawienia.ubytki.pas_brzegu_mm + 0.5
    fragment, prawda = skan(projekt, szum_mm=0.02,
                            ubytki=[{"srednica_mm": 0.5, "glebokosc_mm": 0.2, "srodek": srodek}])
    assert prawda.ubytki[0].przy_brzegu is False
    T = prawda.T_projekt_do_skanu
    wynik = _inspect().sprawdz(fragment, projekt, T, ustawienia)
    cel = przenies(T, srodek)
    assert all(np.linalg.norm(np.asarray(u.srodek) - cel) > TOLERANCJA_MM for u in wynik.ubytki)
    trafione = [u for u in wynik.inne if np.linalg.norm(np.asarray(u.srodek) - cel) <= TOLERANCJA_MM]
    assert len(trafione) == 1, wynik.inne
    assert trafione[0].przy_brzegu is False


def test_most(projekt_mostu, skan, ustawienia):
    fragment, prawda = skan(projekt_mostu, szum_mm=0.02, ubytki=3)
    wynik = _inspect().sprawdz(fragment, projekt_mostu, prawda.T_projekt_do_skanu, ustawienia)
    c = _metryki().porownaj(wynik, prawda, prawda.T_projekt_do_skanu, tolerancja_mm=TOLERANCJA_MM)
    print(f"most: wykryte {c.wykryte}/3, falszywe {c.falszywe}")
    assert c.wykryte >= 2
    assert c.falszywe <= 1


def test_pokrycie_70(pula30, skan, ustawienia):
    projekt = pula30[11].siatka
    fragment, prawda = skan(projekt, szum_mm=0.02, ubytki=2, pokrycie=0.7)
    wynik = _inspect().sprawdz(fragment, projekt, prawda.T_projekt_do_skanu, ustawienia)
    c = _metryki().porownaj(wynik, prawda, prawda.T_projekt_do_skanu, tolerancja_mm=TOLERANCJA_MM)
    print(f"pokrycie 0,7: wykryte {c.wykryte}/2, falszywe {c.falszywe}")
    assert c.falszywe <= 1


def _prawda_testowa(srodki, rodzaje=None):
    rodzaje = rodzaje or ["ukruszenie"] * len(srodki)
    k = 1.2
    return modul_prawdy.PrawdaPracy(
        id="syntetyczna", wspolczynnik=k, T_projekt_do_skanu=np.diag([k, k, k, 1.0]), zakres_scian=[0, 0],
        ubytki=[modul_prawdy.UbytekPrawda(srodek=list(s), srednica_mm=0.4, glebokosc_mm=0.2, rodzaj=r)
                for s, r in zip(srodki, rodzaje)],
    )


def _wynik_testowy(srodki):
    inspect = _inspect()
    ubytki = [inspect.Ubytek(srodek=np.asarray(s, dtype=np.float64), srednica_mm=0.4, glebokosc_mm=0.2,
                             przy_brzegu=True) for s in srodki]
    return inspect.WynikInspekcji(ubytki=ubytki, poprawki=[], inne=[], drgniecie=False, mapa=np.zeros(0))


def test_porownaj():
    metryki = _metryki()
    # 3 ukruszenia + poprawka (nie liczona); srodki prawdy w ukladzie projektu, wykryte w ukladzie fragmentu
    prawdy = [(0.0, 0.0, 0.3), (5.0, 0.0, 0.3), (0.0, 5.0, 0.3), (-4.0, 0.0, 2.0)]
    p = _prawda_testowa(prawdy, ["ukruszenie"] * 3 + ["poprawka"])
    T = p.T_projekt_do_skanu
    wykryte = [przenies(T, prawdy[0]) + [0.3, 0, 0], przenies(T, prawdy[1]) + [0, 0.2, 0.1],
               przenies(T, prawdy[2]) + [2.0, 0, 0]]
    c = metryki.porownaj(_wynik_testowy(wykryte), p, T, tolerancja_mm=0.5)
    assert (c.wykryte, c.pominiete, c.falszywe) == (2, 1, 1)
    assert len(c.pary) == 2

    p1 = _prawda_testowa([(1.0, 1.0, 0.3)])
    T1 = p1.T_projekt_do_skanu
    cel = przenies(T1, (1.0, 1.0, 0.3))
    c = metryki.porownaj(_wynik_testowy([cel + [0.1, 0, 0], cel - [0.2, 0, 0]]), p1, T1, tolerancja_mm=0.5)
    assert (c.wykryte, c.pominiete, c.falszywe) == (1, 0, 1)


def test_czas(projekt_korony, skan, ustawienia):
    inspect = _inspect()
    fragment, prawda = skan(projekt_korony, szum_mm=0.02, ubytki=2)
    T = prawda.T_projekt_do_skanu
    inspect.mapa_odchylek(fragment, projekt_korony, T, ustawienia)  # rozgrzewka (importy, open3d)
    t0 = time.perf_counter()
    inspect.mapa_odchylek(fragment, projekt_korony, T, ustawienia)
    t_mapa = time.perf_counter() - t0
    t0 = time.perf_counter()
    inspect.sprawdz(fragment, projekt_korony, T, ustawienia)
    t_sprawdz = time.perf_counter() - t0
    print(f"czas: mapa_odchylek {t_mapa:.2f} s, sprawdz {t_sprawdz:.2f} s")
    assert t_mapa <= 1.5
    assert t_sprawdz <= 3.0


def _klasa(srednica):
    if srednica < 0.3:
        return "0,2-0,3"
    if srednica < 0.4:
        return "0,3-0,4"
    return "0,4-0,6"


@pytest.mark.wolne
def test_metryki_pelne(pula30, ustawienia):
    metryki = _metryki()
    tabela = {}
    for sigma in (0.02, 0.03, 0.04):
        zadania = przygotuj_prace(pula30, 200, 34, (3, (0.2, 0.6), (0.1, 0.3)), szum_mm=sigma)
        for r in licz_rownolegle(zadania, ustawienia):
            p = r["prawda"]
            c = metryki.porownaj(r["wynik"], p, p.T_projekt_do_skanu, tolerancja_mm=TOLERANCJA_MM)
            sparowane = {tuple(pr.srodek) for _, pr in c.pary}
            for u in p.ubytki:
                if u.rodzaj != "ukruszenie":
                    continue
                wiersz = tabela.setdefault((sigma, _klasa(u.srednica_mm)), [0, 0, 0])
                wiersz[0 if tuple(u.srodek) in sparowane else 1] += 1
            tabela.setdefault((sigma, "falszywe"), [0, 0, 0])[2] += c.falszywe
    print("\nsigma  klasa     wykryte  pominiete  falszywe")
    for (sigma, klasa), (w, pm, f) in sorted(tabela.items()):
        print(f"{sigma:.2f}   {klasa:9s} {w:7d}  {pm:9d}  {f:8d}")
    w = sum(tabela[(0.02, k)][0] for k in ("0,3-0,4", "0,4-0,6"))
    razem = sum(tabela[(0.02, k)][0] + tabela[(0.02, k)][1] for k in ("0,3-0,4", "0,4-0,6"))
    assert razem > 0
    assert w / razem >= 0.85, (w, razem)


# --- testy po recenzji: zaburzone T, plytkie szerokie ukruszenia, siatka bez zageszczania ----------


def zaburzenie(rng, przesuniecie_mm=0.05, obrot_st=0.1):
    """Macierz 4x4: obrot o obrot_st wokol losowej osi i przesuniecie w losowym kierunku."""
    os_obrotu = rng.normal(size=3)
    os_obrotu /= np.linalg.norm(os_obrotu)
    kierunek = rng.normal(size=3)
    kierunek /= np.linalg.norm(kierunek)
    kat = np.radians(obrot_st)
    K = np.array([[0, -os_obrotu[2], os_obrotu[1]], [os_obrotu[2], 0, -os_obrotu[0]],
                  [-os_obrotu[1], os_obrotu[0], 0]])
    D = np.eye(4)
    D[:3, :3] = np.eye(3) + np.sin(kat) * K + (1 - np.cos(kat)) * K @ K
    D[:3, 3] = przesuniecie_mm * kierunek
    return D


def _licz_z_T(zadanie, ustawienia, inspekcja=True):
    """Jak _licz, ale T = prawda.T @ D (D = zadanie[3] albo None); prawda nadal liczona przez prawda.T."""
    projekt, ziarno, kw, D = zadanie
    fragment, prawda = modul_skan.skan_pracy(projekt, ziarno=ziarno, **kw)
    T = prawda.T_projekt_do_skanu if D is None else prawda.T_projekt_do_skanu @ D
    wynik = _inspect().sprawdz(fragment, projekt, T, ustawienia) if inspekcja else None
    return {"projekt": projekt, "fragment": fragment, "prawda": prawda, "wynik": wynik, "T": T}


def licz_rownolegle_z_T(zadania, ustawienia, inspekcja=True):
    watki = min(8, os.cpu_count() or 1)
    with ThreadPoolExecutor(max_workers=watki) as pula_watkow:
        return list(pula_watkow.map(lambda z: _licz_z_T(z, ustawienia, inspekcja), zadania))


@pytest.fixture(scope="session")
def pula30_008():
    """Pula 30 projektow jak pula30, ale krok siatki 0,08 mm."""
    from qc.syntetyka import prace

    return prace.pula_projektow(30, 1, krok_mm=0.08)


ZESTAWY_RECENZJI = {
    # nazwa: (pula, ziarno, liczba prac, ubytki, kwargs skan_pracy, zaburzenie T)
    "duze_zaburzone": ("pula30", 101, 20, (3, (0.4, 0.6), (0.12, 0.3)), dict(szum_mm=0.02), True),
    "plytkie_1_0": ("pula30", 111, 10, [{"srednica_mm": 1.0, "glebokosc_mm": 0.12}], dict(szum_mm=0.02), False),
    "plytkie_1_2": ("pula30", 112, 10, [{"srednica_mm": 1.2, "glebokosc_mm": 0.10}], dict(szum_mm=0.02), False),
    "plytkie_1_5": ("pula30", 113, 10, [{"srednica_mm": 1.5, "glebokosc_mm": 0.15}], dict(szum_mm=0.02), False),
    "srednie_bez_zag": ("pula30_008", 121, 20, (3, (0.3, 0.4), (0.10, 0.2)),
                        dict(szum_mm=0.02, zageszczaj=False), False),
    "male_bez_zag": ("pula30_008", 122, 20, (3, (0.2, 0.3), (0.08, 0.15)),
                     dict(szum_mm=0.02, zageszczaj=False), False),
}


@pytest.fixture(scope="session")
def bank_recenzji(pula30, pula30_008, ustawienia):
    """Fabryka: bank_recenzji(nazwa) -> rekordy {projekt, fragment, prawda, wynik, T} (liczona raz)."""
    pule = {"pula30": pula30, "pula30_008": pula30_008}
    pamiec = {}

    def _bank(nazwa):
        if nazwa not in pamiec:
            pula, ziarno, n, ubytki, kw, zaburz = ZESTAWY_RECENZJI[nazwa]
            rng = np.random.default_rng(ziarno + 7)
            zadania = [(p, z, a, zaburzenie(rng) if zaburz else None)
                       for p, z, a in przygotuj_prace(pule[pula], ziarno, n, ubytki, **kw)]
            pamiec[nazwa] = licz_rownolegle_z_T(zadania, ustawienia)
        return pamiec[nazwa]

    return _bank


def test_t_zaburzone(bank_recenzji):
    rekordy = bank_recenzji("duze_zaburzone")
    drgniete = sum(1 for r in rekordy if r["wynik"].drgniecie)
    wykryte, pominiete, falszywe, _, _ = sumuj(rekordy)
    print(f"T zaburzone 0,05 mm / 0,1 st.: drgniecie {drgniete}/20, wykryte {wykryte}/60, "
          f"pominiete {pominiete}, falszywe {falszywe}")
    assert drgniete <= 1
    assert wykryte >= 48
    assert falszywe <= 3


def test_drgniecie_przy_zaburzonym_t(pula30, ustawienia):
    inspect = _inspect()
    rng = np.random.default_rng(131)
    zadania = [(p, z, a, zaburzenie(rng))
               for p, z, a in przygotuj_prace(pula30, 131, 5, None, szum_mm=0.02, drgniecie=True)]
    rekordy = licz_rownolegle_z_T(zadania, ustawienia, inspekcja=False)
    wyniki = [inspect.wykryj_drgniecie(r["fragment"], r["projekt"], r["T"], ustawienia) for r in rekordy]
    assert wyniki == [True] * 5, wyniki


@pytest.mark.parametrize("nazwa", ["plytkie_1_0", "plytkie_1_2", "plytkie_1_5"])
def test_ukruszenia_plytkie_szerokie(bank_recenzji, nazwa):
    rekordy = bank_recenzji(nazwa)
    wykryte, pominiete, falszywe, _, _ = sumuj(rekordy)
    print(f"{nazwa}: wykryte {wykryte}/10, pominiete {pominiete}, falszywe {falszywe}")
    assert wykryte >= 8


def test_bez_zageszczania(bank_recenzji):
    wykryte, pominiete, falszywe, _, _ = sumuj(bank_recenzji("srednie_bez_zag"))
    print(f"bez zageszczania, krok 0,08, srednie: wykryte {wykryte}/60, pominiete {pominiete}, "
          f"falszywe {falszywe}")
    assert wykryte >= 48
    assert falszywe <= 2
    wykryte, pominiete, falszywe, _, _ = sumuj(bank_recenzji("male_bez_zag"))
    print(f"bez zageszczania, krok 0,08, male: wykryte {wykryte}/60, pominiete {pominiete}, "
          f"falszywe {falszywe}")
    assert wykryte >= 10
