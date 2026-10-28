"""Testy qc.match: filtr kandydatow, FPFH + RANSAC, ICP, ranking i pewnosc.

Dane wylacznie syntetyczne (qc.syntetyka). Fragment = skan_pracy(projekt, wspolczynnik=k, szum)
przeniesiony losowa transformacja M (obrot Z 0-360 st., przechyl <= 10 st., przesuniecie <= 20 mm);
prawda T_projekt_do_fragmentu = M @ T_projekt_do_skanu. Fragmenty i wyniki dopasowania liczone raz
w fixtures session, testy tylko licza metryki.
"""

import math
import time
from dataclasses import dataclass

import numpy as np
import pytest
import trimesh

from qc.ustawienia import katalog_repo, wczytaj

K_MIN, K_MAX = 1.20, 1.25
SZUM = 0.03


# --- pomocnicze ---------------------------------------------------------------


def _match():
    import qc.match

    return qc.match


def _filtr():
    from qc.match import filtr

    return filtr


def _policz(siatka):
    from qc.catalog.cechy import policz

    return policz(siatka)


@dataclass
class Fragment:
    siatka: trimesh.Trimesh
    projekt_id: str
    projekt: trimesh.Trimesh
    wspolczynnik: float
    T_prawdy: np.ndarray  # projekt w ukladzie CAD -> fragment


def _losowa_transformacja(rng: np.random.Generator) -> np.ndarray:
    """Obrot wokol Z 0-360 st., przechyl <= 10 st. wokol osi poziomej, przesuniecie <= 20 mm."""
    a = rng.uniform(0.0, 2 * math.pi)
    rz = np.array([[math.cos(a), -math.sin(a), 0.0], [math.sin(a), math.cos(a), 0.0], [0.0, 0.0, 1.0]])
    b = rng.uniform(0.0, 2 * math.pi)
    os_ = np.array([math.cos(b), math.sin(b), 0.0])
    kat = math.radians(rng.uniform(0.0, 10.0))
    kx = np.array([[0.0, -os_[2], os_[1]], [os_[2], 0.0, -os_[0]], [-os_[1], os_[0], 0.0]])
    rp = np.eye(3) + math.sin(kat) * kx + (1 - math.cos(kat)) * kx @ kx
    kierunek = rng.normal(size=3)
    kierunek /= np.linalg.norm(kierunek)
    T = np.eye(4)
    T[:3, :3] = rp @ rz
    T[:3, 3] = kierunek * rng.uniform(0.0, 20.0)
    return T


def _fragment(projekt_id, siatka_projektu, ziarno, k, szum=SZUM, **kw) -> Fragment:
    from qc.syntetyka.skan import skan_pracy

    siatka, prawda = skan_pracy(siatka_projektu, ziarno=ziarno, wspolczynnik=k, szum_mm=szum, **kw)
    M = _losowa_transformacja(np.random.default_rng(10_000 + ziarno))
    siatka.apply_transform(M)
    return Fragment(siatka=siatka, projekt_id=projekt_id, projekt=siatka_projektu, wspolczynnik=k,
                    T_prawdy=M @ prawda.T_projekt_do_skanu)


def _wpis(projekt_id, siatka, k, cechy="licz"):
    m = _match()
    return m.WpisPuli(projekt_id=projekt_id, siatka=siatka,
                      cechy=_policz(siatka) if cechy == "licz" else cechy, wspolczynnik=k)


def _po_transformacji(T, punkty):
    p = np.asarray(punkty, dtype=np.float64)
    return p @ T[:3, :3].T + T[:3, 3]


def _odleglosci_od(punkty, siatka) -> np.ndarray:
    """Odleglosc (bez znaku) punktow od powierzchni siatki (open3d)."""
    import open3d as o3d

    scena = o3d.t.geometry.RaycastingScene()
    scena.add_triangles(o3d.core.Tensor(np.asarray(siatka.vertices, dtype=np.float32)),
                        o3d.core.Tensor(np.asarray(siatka.faces, dtype=np.uint32)))
    wynik = scena.compute_distance(o3d.core.Tensor(np.asarray(punkty, dtype=np.float32)))
    return wynik.numpy().astype(np.float64)


def _ids(wynik, n):
    return [k.projekt_id for k in wynik.kandydaci[:n]]


def _top(wyniki, n):
    return sum(f.projekt_id in _ids(w, n) for f, w in wyniki)


def _dopasuj_wszystkie(fragmenty, pula, ustawienia, tryb="wieczor"):
    m = _match()
    return [(f, m.dopasuj(f.siatka, pula, ustawienia, tryb=tryb)) for f in fragmenty]


# --- fixtures -----------------------------------------------------------------


@pytest.fixture(scope="session")
def ustawienia_match():
    with pytest.MonkeyPatch.context() as mp:
        mp.delenv("QC_USTAWIENIA", raising=False)
        return wczytaj(katalog_repo() / "ustawienia.toml")


@pytest.fixture(scope="session")
def pula_wieczor(pula30):
    """pula30 z k_i losowym w [1,20; 1,25]."""
    rng = np.random.default_rng(7)
    return [_wpis(p.id, p.siatka, float(rng.uniform(K_MIN, K_MAX))) for p in pula30]


def _fragmenty_z_puli(pula, ziarna, **kw):
    return [_fragment(pula[(z - 1) % len(pula)].projekt_id, pula[(z - 1) % len(pula)].siatka, z,
                      pula[(z - 1) % len(pula)].wspolczynnik, **kw) for z in ziarna]


@pytest.fixture(scope="session")
def wyniki_wieczor(pula_wieczor, ustawienia_match):
    """40 fragmentow (ziarna 1..40), szum 0,03, bez ubytkow; (fragment, wynik, czas_s)."""
    m = _match()
    fragmenty = _fragmenty_z_puli(pula_wieczor, range(1, 41))
    rozgrzewka = _fragmenty_z_puli(pula_wieczor, [1000])[0]
    m.dopasuj(rozgrzewka.siatka, pula_wieczor, ustawienia_match, tryb="wieczor")
    wyniki = []
    for f in fragmenty:
        t0 = time.perf_counter()
        w = m.dopasuj(f.siatka, pula_wieczor, ustawienia_match, tryb="wieczor")
        wyniki.append((f, w, time.perf_counter() - t0))
    return wyniki


# --- testy --------------------------------------------------------------------


def test_top1_wieczor(wyniki_wieczor):
    pary = [(f, w) for f, w, _ in wyniki_wieczor]
    top1, top2 = _top(pary, 1), _top(pary, 2)
    pewne = sum(w.pewnosc == "pewny" for _, w in pary)
    print(f"\nwieczor: top-1 {top1}/40, top-2 {top2}/40, pewny {pewne}/40")
    assert top1 >= 38
    assert top2 >= 39
    assert pewne >= 34
    for f, w in pary:
        if _ids(w, 1) != [f.projekt_id]:
            continue
        k = w.kandydaci[0]
        assert k.pokrycie >= 0.85, f"{f.projekt_id}: pokrycie {k.pokrycie:.3f}"
        T = np.asarray(k.T_projekt_do_fragmentu)
        p95 = float(np.percentile(_odleglosci_od(_po_transformacji(T, f.projekt.vertices), f.siatka), 95))
        assert p95 <= 0.1, f"{f.projekt_id}: p95 odleglosci projektu od fragmentu {p95:.3f} mm"


def test_top1_rano(ustawienia_match):
    from qc.syntetyka import prace

    pula = [_wpis(p.id, p.siatka, 1.0) for p in prace.pula_projektow(60, 2)]
    indeksy = np.random.default_rng(2).choice(60, 40, replace=False)
    fragmenty = [_fragment(pula[i].projekt_id, pula[i].siatka, z, 1.0, pokrycie=0.7)
                 for z, i in enumerate(indeksy, start=1)]
    wyniki = _dopasuj_wszystkie(fragmenty, pula, ustawienia_match, tryb="rano")
    top1, top2 = _top(wyniki, 1), _top(wyniki, 2)
    print(f"\nrano: top-1 {top1}/40, top-2 {top2}/40")
    assert top1 >= 36
    assert top2 >= 38


def test_blizniaki(pula_wieczor, ustawienia_match):
    from qc.syntetyka import prace

    oryginal = prace.korona(9)
    v = np.array(oryginal.vertices, dtype=np.float64)
    szczyt = v[int(np.argmax(v[:, 2]))]
    maska = np.linalg.norm(v - szczyt, axis=1) <= 1.0
    assert maska.sum() > 0
    v[maska, 2] += 0.05
    kopia = trimesh.Trimesh(v, np.array(oryginal.faces), process=False)
    k = 1.22
    # 30 projektow (29 z puli + oryginal) + 1 blizniak
    pula = pula_wieczor[:29] + [_wpis("blizniak-oryginal", oryginal, k), _wpis("blizniak-kopia", kopia, k)]
    fragmenty = [_fragment("blizniak-oryginal", oryginal, z, k, szum=0.02) for z in range(1, 6)]
    wyniki = _dopasuj_wszystkie(fragmenty, pula, ustawienia_match)
    oba = sum(set(_ids(w, 2)) == {"blizniak-oryginal", "blizniak-kopia"} for _, w in wyniki)
    dwuznaczne = sum(w.pewnosc == "dwuznaczny" for _, w in wyniki)
    print(f"\nblizniaki: oba w top-2 {oba}/5, dwuznaczny {dwuznaczne}/5")
    assert oba == 5
    assert dwuznaczne >= 4


def test_brak_kandydata(pula_wieczor, ustawienia_match):
    from qc.syntetyka import prace

    obce = prace.pula_projektow(10, 99)
    rng = np.random.default_rng(99)
    fragmenty = [_fragment("obcy-" + p.id, p.siatka, 500 + i, float(rng.uniform(K_MIN, K_MAX)))
                 for i, p in enumerate(obce)]
    wyniki = _dopasuj_wszystkie(fragmenty, pula_wieczor, ustawienia_match)
    brak = sum(w.pewnosc == "brak" for _, w in wyniki)
    print(f"\nspoza puli: brak {brak}/10")
    assert brak >= 9


def test_filtr(wyniki_wieczor, pula_wieczor, ustawienia_match):
    filtr = _filtr()
    trafione, liczby = 0, []
    for f, _, _ in wyniki_wieczor:
        kandydaci = filtr.kandydaci(_policz(f.siatka), pula_wieczor, ustawienia_match)
        assert len(kandydaci) <= ustawienia_match.dopasowanie.max_kandydatow
        trafione += f.projekt_id in [k.projekt_id for k in kandydaci]
        liczby.append(len(kandydaci))
    print(f"\nfiltr: wlasciwy {trafione}/40, srednio {np.mean(liczby):.1f} kandydatow")
    assert trafione >= 39
    assert float(np.mean(liczby)) <= 9

    # wpis z cechy None (plik uszkodzony) pominiety bez wyjatku
    f = wyniki_wieczor[0][0]
    zepsuty = _wpis("uszkodzony", f.projekt, f.wspolczynnik, cechy=None)
    kandydaci = filtr.kandydaci(_policz(f.siatka), [zepsuty] + pula_wieczor, ustawienia_match)
    assert "uszkodzony" not in [k.projekt_id for k in kandydaci]
    assert f.projekt_id in [k.projekt_id for k in kandydaci]


def test_ubytki_nie_psuja(pula_wieczor, ustawienia_match):
    fragmenty = _fragmenty_z_puli(pula_wieczor, range(101, 121), ubytki=3)
    wyniki = _dopasuj_wszystkie(fragmenty, pula_wieczor, ustawienia_match)
    top1 = _top(wyniki, 1)
    print(f"\nubytki: top-1 {top1}/20")
    assert top1 >= 19


def test_szum_0_04(pula_wieczor, ustawienia_match):
    fragmenty = _fragmenty_z_puli(pula_wieczor, range(201, 221), szum=0.04)
    wyniki = _dopasuj_wszystkie(fragmenty, pula_wieczor, ustawienia_match)
    top1 = _top(wyniki, 1)
    print(f"\nszum 0,04: top-1 {top1}/20")
    assert top1 >= 18


def test_z_gory(pula_wieczor, ustawienia_match):
    fragmenty = _fragmenty_z_puli(pula_wieczor, range(301, 321), szum=0.02, widocznosc="z_gory")
    wyniki = _dopasuj_wszystkie(fragmenty, pula_wieczor, ustawienia_match)
    top1, top2 = _top(wyniki, 1), _top(wyniki, 2)
    pewnosci = [w.pewnosc for _, w in wyniki]
    print(f"\nz gory: top-1 {top1}/20, top-2 {top2}/20, "
          f"pewny {pewnosci.count('pewny')}, dwuznaczny {pewnosci.count('dwuznaczny')}, "
          f"brak {pewnosci.count('brak')}")
    assert top1 >= 17


def test_czas(wyniki_wieczor, ustawienia_match):
    # rozgrzewka w fixture; 10 kolejnych fragmentow przy puli 30
    czasy = [c for _, _, c in wyniki_wieczor[:10]]
    srednio = float(np.mean(czasy))
    print(f"\nczas: srednio {srednio:.2f} s, max {max(czasy):.2f} s na fragment")
    assert srednio <= 3.0
    for _, w, _ in wyniki_wieczor:
        assert len(w.kandydaci) <= ustawienia_match.dopasowanie.max_kandydatow


def test_transformacja_wlasciwa(wyniki_wieczor):
    sprawdzone = 0
    for f, w, _ in wyniki_wieczor:
        if _ids(w, 1) != [f.projekt_id]:
            continue
        T = np.asarray(w.kandydaci[0].T_projekt_do_fragmentu, dtype=np.float64)
        assert T.shape == (4, 4)
        roznica = np.linalg.norm(_po_transformacji(T, f.projekt.vertices)
                                 - _po_transformacji(f.T_prawdy, f.projekt.vertices), axis=1)
        p95 = float(np.percentile(roznica, 95))
        assert p95 <= 0.05, f"{f.projekt_id}: p95 polozenia wierzcholkow {p95:.3f} mm"
        D = T @ np.linalg.inv(f.T_prawdy)
        R = D[:3, :3] / np.cbrt(np.linalg.det(D[:3, :3]))
        kat = math.degrees(math.acos(float(np.clip((np.trace(R) - 1) / 2, -1.0, 1.0))))
        assert kat <= 0.2, f"{f.projekt_id}: kat {kat:.3f} st."
        sprawdzone += 1
    assert sprawdzone >= 38


def test_most(pula_wieczor, ustawienia_match):
    from qc.syntetyka import prace

    rng = np.random.default_rng(11)
    mosty = [_wpis(f"most-{j + 1:02d}", prace.most(40 + j, punkty=3 + j % 2), float(rng.uniform(K_MIN, K_MAX)))
             for j in range(5)]
    pula = pula_wieczor + mosty
    fragmenty = [_fragment(w.projekt_id, w.siatka, 401 + j, w.wspolczynnik, szum=0.02)
                 for j, w in enumerate(mosty)]
    wyniki = _dopasuj_wszystkie(fragmenty, pula, ustawienia_match)
    top1 = _top(wyniki, 1)
    print(f"\nmosty: top-1 {top1}/5")
    assert top1 == 5


@pytest.mark.wolne
def test_metryki_200(pula_wieczor, ustawienia_match):
    wiersze = {}
    wszystkie = []
    for i in range(200):
        wpis = pula_wieczor[i % len(pula_wieczor)]
        szum = 0.02 if i % 2 else 0.03
        ubytki = 3 if (i // 2) % 2 else 0
        f = _fragment(wpis.projekt_id, wpis.siatka, 1000 + i, wpis.wspolczynnik, szum=szum, ubytki=ubytki)
        para = _dopasuj_wszystkie([f], pula_wieczor, ustawienia_match)[0]
        wiersze.setdefault((szum, ubytki), []).append(para)
        wszystkie.append(para)
    print("\nszum  ubytki    n  top-1  top-2  brak")
    for (szum, ubytki), pary in sorted(wiersze.items()):
        brak = sum(w.pewnosc == "brak" for _, w in pary)
        print(f"{szum:.2f}  {ubytki:6d}  {len(pary):3d}  {_top(pary, 1):5d}  {_top(pary, 2):5d}  {brak:4d}")
    top1, top2 = _top(wszystkie, 1), _top(wszystkie, 2)
    brak = sum(w.pewnosc == "brak" for _, w in wszystkie)
    print(f"razem       {len(wszystkie):3d}  {top1:5d}  {top2:5d}  {brak:4d}")
    assert top1 >= 190
    assert top2 >= 196
    assert brak <= 2


# --- poprawki po recenzji -------------------------------------------------------


@pytest.fixture(scope="session")
def pula_rano60():
    from qc.syntetyka import prace

    return [_wpis(p.id, p.siatka, 1.0) for p in prace.pula_projektow(60, 2)]


@pytest.mark.wolne
def test_rano_pula_200(ustawienia_match):
    from qc.syntetyka import prace

    pula = [_wpis(p.id, p.siatka, 1.0) for p in prace.pula_projektow(200, 3)]
    indeksy = np.random.default_rng(3).choice(len(pula), 20, replace=False)
    fragmenty = [_fragment(pula[i].projekt_id, pula[i].siatka, 600 + z, 1.0, pokrycie=0.7)
                 for z, i in enumerate(indeksy)]
    wyniki = _dopasuj_wszystkie(fragmenty, pula, ustawienia_match, tryb="rano")
    top1 = _top(wyniki, 1)
    zle_pewne = sum(w.pewnosc == "pewny" and _ids(w, 1) != [f.projekt_id] for f, w in wyniki)
    print(f"\nrano pula 200: top-1 {top1}/20, pewny na zlym projekcie {zle_pewne}")
    assert top1 >= 19
    assert zle_pewne == 0


@pytest.mark.wolne
def test_rano_spoza_puli(pula_rano60, ustawienia_match):
    from qc.syntetyka import prace

    obce = prace.pula_projektow(15, 77)
    fragmenty = [_fragment("obcy-" + p.id, p.siatka, 700 + i, 1.0, pokrycie=0.7) for i, p in enumerate(obce)]
    wyniki = _dopasuj_wszystkie(fragmenty, pula_rano60, ustawienia_match, tryb="rano")
    pewnosci = [w.pewnosc for _, w in wyniki]
    print(f"\nrano spoza puli: pewny {pewnosci.count('pewny')}, dwuznaczny {pewnosci.count('dwuznaczny')}, "
          f"brak {pewnosci.count('brak')}, max pokrycie "
          f"{max((w.kandydaci[0].pokrycie for _, w in wyniki if w.kandydaci), default=0):.3f}")
    assert pewnosci.count("pewny") == 0


def test_ransac_awaryjny(pula_wieczor, tmp_path, monkeypatch):
    """prog_wyraznosci_osi = 1,0: os PCA zawsze niepewna -> zgrubne FPFH + RANSAC, poprawny top-1."""
    import re

    from qc.match import dopasowanie

    monkeypatch.delenv("QC_USTAWIENIA", raising=False)
    tekst = (katalog_repo() / "ustawienia.toml").read_text(encoding="utf-8")
    tekst, n = re.subn(r"(?m)^prog_wyraznosci_osi\s*=.*$", "prog_wyraznosci_osi = 1.0", tekst)
    assert n == 1, "brak klucza dopasowanie.prog_wyraznosci_osi w ustawienia.toml"
    (tmp_path / "ustawienia.toml").write_text(tekst, encoding="utf-8")
    ust = wczytaj(tmp_path / "ustawienia.toml")

    wywolania = []
    oryginal = dopasowanie.zgrubne_z_cech

    def liczona(*a, **kw):
        wywolania.append(1)
        return oryginal(*a, **kw)

    monkeypatch.setattr(dopasowanie, "zgrubne_z_cech", liczona)
    f = _fragmenty_z_puli(pula_wieczor, [3], szum=0.02)[0]
    w = _match().dopasuj(f.siatka, pula_wieczor, ust)
    print(f"\nRANSAC awaryjny: {len(wywolania)} wywolan, top-1 {_ids(w, 1)}, pewnosc {w.pewnosc}")
    assert wywolania
    assert _ids(w, 1) == [f.projekt_id]


def test_pamiec_klucz(pula_wieczor, ustawienia_match):
    """Te same projekt_id i k, nowe obiekty Trimesh + wspolna pamiec: cache trafia, wyniki identyczne."""
    m = _match()

    def nowa_pula():
        return [m.WpisPuli(w.projekt_id, trimesh.Trimesh(np.array(w.siatka.vertices), np.array(w.siatka.faces),
                                                          process=False), w.cechy, w.wspolczynnik)
                for w in pula_wieczor]

    fragmenty = _fragmenty_z_puli(pula_wieczor, range(801, 806))
    pamiec = {}
    t0 = time.perf_counter()
    pierwsze = [m.dopasuj(f.siatka, nowa_pula(), ustawienia_match, pamiec=pamiec) for f in fragmenty]
    t1 = time.perf_counter()
    klucze = set(pamiec)
    drugie = [m.dopasuj(f.siatka, nowa_pula(), ustawienia_match, pamiec=pamiec) for f in fragmenty]
    t2 = time.perf_counter()
    print(f"\npamiec: 1. przebieg {t1 - t0:.2f} s, 2. przebieg {t2 - t1:.2f} s, kluczy {len(klucze)}")
    assert klucze and set(pamiec) == klucze
    assert t2 - t1 < t1 - t0
    for a, b in zip(pierwsze, drugie):
        assert a.pewnosc == b.pewnosc
        assert [k.projekt_id for k in a.kandydaci] == [k.projekt_id for k in b.kandydaci]
        for ka, kb in zip(a.kandydaci, b.kandydaci):
            assert ka.pokrycie == kb.pokrycie
            # ICP open3d liczy rownolegle - roznice rzedu 1e-15
            assert np.allclose(ka.T_projekt_do_fragmentu, kb.T_projekt_do_fragmentu, rtol=0, atol=1e-9)


# --- poprawki 2 po recenzji ------------------------------------------------------


def test_pewnosc_wieczor_pelne(wyniki_wieczor):
    """Kontrola obrotu 180 st. nie obniza pewnosci: pelne skany wieczorem 'pewny' >= 38/40."""
    pewne = sum(w.pewnosc == "pewny" and _ids(w, 1) == [f.projekt_id] for f, w, _ in wyniki_wieczor)
    print(f"\nwieczor pelne: pewny (trafiony) {pewne}/40")
    assert pewne >= 38


@pytest.mark.wolne
def test_pewnosc_rano(pula_rano60, ustawienia_match):
    """Rano bez kontroli obrotu: 40 fragmentow pokrycie 0,7 -> 'pewny' >= 38/40."""
    indeksy = np.random.default_rng(9).choice(len(pula_rano60), 40, replace=False)
    fragmenty = [_fragment(pula_rano60[i].projekt_id, pula_rano60[i].siatka, 900 + z, 1.0, pokrycie=0.7)
                 for z, i in enumerate(indeksy)]
    wyniki = _dopasuj_wszystkie(fragmenty, pula_rano60, ustawienia_match, tryb="rano")
    pewne = sum(w.pewnosc == "pewny" and _ids(w, 1) == [f.projekt_id] for f, w in wyniki)
    print(f"\nrano: top-1 {_top(wyniki, 1)}/40, pewny (trafiony) {pewne}/40")
    assert pewne >= 38


@pytest.mark.wolne
def test_mosty_rano_niepelne(pula30, ustawienia_match):
    """Sito nie odrzuca wlasciwego mostu: 10 mostow rano pokrycie 0,7 w puli 30 + 10 mostow -> top-1 >= 9/10."""
    from qc.syntetyka import prace

    mosty = [_wpis(f"most-{j + 1:02d}", prace.most(60 + j, punkty=3 + j % 2), 1.0) for j in range(10)]
    pula = [_wpis(p.id, p.siatka, 1.0) for p in pula30] + mosty
    fragmenty = [_fragment(w.projekt_id, w.siatka, 950 + j, 1.0, pokrycie=0.7) for j, w in enumerate(mosty)]
    wyniki = _dopasuj_wszystkie(fragmenty, pula, ustawienia_match, tryb="rano")
    top1 = _top(wyniki, 1)
    print(f"\nmosty rano 0,7: top-1 {top1}/10, pokrycia "
          f"{[round(w.kandydaci[0].pokrycie, 3) if w.kandydaci else None for _, w in wyniki]}")
    assert top1 >= 9


@pytest.mark.wolne
def test_ransac_limit_rano(pula_rano60, tmp_path, monkeypatch):
    """Wymuszona sciezka RANSAC rano dla pracy spoza puli: najwyzej 2 x max_kandydatow wywolan RANSAC."""
    import re

    from qc.match import dopasowanie
    from qc.syntetyka import prace

    monkeypatch.delenv("QC_USTAWIENIA", raising=False)
    tekst = (katalog_repo() / "ustawienia.toml").read_text(encoding="utf-8")
    tekst = re.sub(r"(?m)^prog_wyraznosci_osi\s*=.*$", "prog_wyraznosci_osi = 1.0", tekst)
    (tmp_path / "ustawienia.toml").write_text(tekst, encoding="utf-8")
    ust = wczytaj(tmp_path / "ustawienia.toml")

    wywolania = []
    oryginal = dopasowanie.zgrubne_z_cech

    def liczona(*a, **kw):
        wywolania.append(1)
        return oryginal(*a, **kw)

    monkeypatch.setattr(dopasowanie, "zgrubne_z_cech", liczona)
    obcy = prace.pula_projektow(1, 78)[0]
    f = _fragment("obcy", obcy.siatka, 990, 1.0, pokrycie=0.7)
    t0 = time.perf_counter()
    w = _match().dopasuj(f.siatka, pula_rano60, ust, tryb="rano")
    czas = time.perf_counter() - t0
    print(f"\nRANSAC rano spoza puli: {len(wywolania)} wywolan, {czas:.1f} s, pewnosc {w.pewnosc}")
    assert len(wywolania) <= 2 * ust.dopasowanie.max_kandydatow
    assert w.pewnosc != "pewny"
