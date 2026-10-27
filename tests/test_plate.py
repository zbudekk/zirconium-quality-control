"""Testy modulu qc.plate: wyrownanie skanu plytki, numer plytki, ciecie na fragmenty gniazd.

Dane: qc.syntetyka.plytka.skan_plytki z pula30 (+ 2 mosty, jak w test_syntetyka_plytka.py), plytka
wieczorna nr 2, ustawienia domyslne. Skany i wyniki analizuj() wspoldzielone przez testy sa liczone raz
na sesje (fixtures scope="session").

Identyfikacja scian fragmentu: srodki scian skanu (zakresy scian z prawdy) przeniesione przez
T_skan_do_plytki z wyniku do ukladu plytki; sciana fragmentu nalezy do zrodla najblizszego srodka w
odleglosci <= 0,01 mm (inaczej -2 = nieznana).
"""

import dataclasses
import math
import time

import numpy as np
import pytest
import trimesh

from qc import uklad as modul_ukladu
from qc.syntetyka import plytka, prace
from qc.ustawienia import katalog_repo, wczytaj

PLIKI = {
    "wieczorna": katalog_repo() / "modele" / "uklad_gniazd_wieczorna.json",
    "poranna": katalog_repo() / "modele" / "uklad_gniazd_poranna.json",
}
NUMER = 2
TOL_SCIANY_MM = 0.01
PLYTKA = -1
NIEZNANA = -2

MIN_WLASNYCH = 0.95
MAX_CUDZYCH = 0.02
MAX_PLYTKI = 0.01


def _plate():
    import qc.plate as modul

    return modul


# --- fixtures -----------------------------------------------------------------------


@pytest.fixture(scope="session")
def ustawienia():
    return wczytaj()


@pytest.fixture(scope="session")
def wieczorna():
    return modul_ukladu.wczytaj(PLIKI["wieczorna"])


@pytest.fixture(scope="session")
def poranna():
    return modul_ukladu.wczytaj(PLIKI["poranna"])


def _mosty(krok_mm=0.1):
    return [prace.Projekt(id="most-01", rodzaj="most", siatka=prace.most(1, 4, krok_mm)),
            prace.Projekt(id="most-02", rodzaj="most", siatka=prace.most(2, 3, krok_mm))]


@pytest.fixture(scope="session")
def pula_z_mostami(pula30):
    """Pula 30 koron (krok 0,1) + 2 mosty (pula30 nie zawiera mostow)."""
    return list(pula30) + _mosty(0.1)


def _skan(uklad, numer, pula, n_koron, n_mostow, ziarno, szum_mm=0.02, T_plytki="losowa", zmien=None):
    """(rozmieszczenia, skan, prawda); zmien = {indeks rozmieszczenia: opcje} dopisane do opcji."""
    rozm = plytka.rozmiesc(uklad, pula, n_koron, n_mostow, ziarno=ziarno)
    for i, opcje in (zmien or {}).items():
        rozm[i] = dataclasses.replace(rozm[i], opcje={**rozm[i].opcje, **opcje})
    siatka, pr = plytka.skan_plytki(uklad, numer, rozm, ziarno=ziarno, szum_mm=szum_mm, T_plytki=T_plytki)
    return rozm, siatka, pr


@pytest.fixture(scope="session")
def plytka_6(wieczorna, pula_z_mostami):
    """Plytka wieczorna nr 2: 6 koron + 1 most, T losowa."""
    return _skan(wieczorna, NUMER, pula_z_mostami, 6, 1, ziarno=21)


@pytest.fixture(scope="session")
def wynik_6(plytka_6, wieczorna, ustawienia):
    """Pierwsze analizuj() na plytka_6 (takze rozgrzewka dla test_czas)."""
    _, siatka, _ = plytka_6
    return _plate().analizuj(siatka, wieczorna, ustawienia)


@pytest.fixture(scope="session")
def plytka_pelna(wieczorna, pula_z_mostami):
    """Plytka wieczorna nr 2: 24 korony + 2 mosty, T losowa."""
    return _skan(wieczorna, NUMER, pula_z_mostami, 24, 2, ziarno=22)


@pytest.fixture(scope="session")
def wynik_pelny(plytka_pelna, wieczorna, ustawienia):
    _, siatka, _ = plytka_pelna
    return _plate().analizuj(siatka, wieczorna, ustawienia)


# --- pomocnicze ---------------------------------------------------------------------


def _obrot_z(kat_deg):
    a = math.radians(kat_deg)
    R = np.eye(4)
    R[:2, :2] = [[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]]
    return R


def _obrot_os(os_, kat_deg):
    u = np.asarray(os_, dtype=np.float64)
    u = u / np.linalg.norm(u)
    a = math.radians(kat_deg)
    K = np.array([[0, -u[2], u[1]], [u[2], 0, -u[0]], [-u[1], u[0], 0]])
    R = np.eye(4)
    R[:3, :3] = np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * K @ K
    return R


def _przenies(punkty, T):
    T = np.asarray(T, dtype=np.float64)
    return np.asarray(punkty, dtype=np.float64) @ T[:3, :3].T + T[:3, 3]


def _przeksztalc(siatka, T):
    return trimesh.Trimesh(_przenies(siatka.vertices, T), np.asarray(siatka.faces), process=False)


def _T_prawdy(pr):
    return np.asarray(pr.plytka["T_skan_do_plytki"], dtype=np.float64)


def blad_T(T, T_prawdy):
    """(translacja mm, kat st.) roznicy T @ inv(T_prawdy) od tozsamosci."""
    D = np.asarray(T, dtype=np.float64) @ np.linalg.inv(T_prawdy)
    cos = np.clip((np.trace(D[:3, :3]) - 1) / 2, -1.0, 1.0)
    return float(np.linalg.norm(D[:3, 3])), math.degrees(math.acos(cos))


def _sprawdz_wyrownanie(uklad, w, pr, max_translacja, max_kat, max_znacznik=None):
    plate = _plate()
    assert isinstance(w, plate.Wyrownanie)
    T = np.asarray(w.T_skan_do_plytki, dtype=np.float64)
    assert T.shape == (4, 4)
    dt, dk = blad_T(T, _T_prawdy(pr))
    assert dt <= max_translacja, f"translacja {dt:.4f} mm"
    assert dk <= max_kat, f"kat {dk:.4f} st."
    assert w.blad_mm <= 0.1, f"blad_mm {w.blad_mm:.4f}"
    if max_znacznik is not None:
        z = np.asarray(w.znaczniki_xyz, dtype=np.float64)
        assert z.shape == (3, 3)
        z = _przenies(z, T)
        for i, naroznik in enumerate(("A", "B", "C")):
            x, y, _, glebokosc = uklad.znaczniki[naroznik]
            d = float(np.linalg.norm(z[i] - (x, y, -glebokosc)))
            assert d <= max_znacznik, f"znacznik {naroznik}: {d:.4f} mm"


def _srodki_scian(siatka):
    v = np.asarray(siatka.vertices, dtype=np.float64)
    f = np.asarray(siatka.faces, dtype=np.int64)
    return v[f].mean(axis=1)


def _pola_scian(siatka):
    v = np.asarray(siatka.vertices, dtype=np.float64)
    f = np.asarray(siatka.faces, dtype=np.int64)
    if len(f) == 0:
        return np.zeros(0)
    a, b, c = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    return np.linalg.norm(np.cross(b - a, c - a), axis=1) / 2


_ETYKIETY = {}


def etykiety(wynik, siatka, pr):
    """Lista etykiet scian dla kazdego fragmentu wyniku: PLYTKA, indeks pracy w pr.prace albo NIEZNANA."""
    import open3d as o3d

    klucz = (id(wynik), id(siatka))
    if klucz in _ETYKIETY:
        return _ETYKIETY[klucz]
    zrodlo = np.full(len(siatka.faces), PLYTKA, dtype=np.int64)
    for i, p in enumerate(pr.prace):
        a, b = p.zakres_scian
        zrodlo[a:b] = i
    srodki = _przenies(_srodki_scian(siatka), wynik.wyrownanie.T_skan_do_plytki)
    zapytania = [_srodki_scian(f.siatka) for f in wynik.fragmenty]
    wynik_et = [np.zeros(0, dtype=np.int64) for _ in zapytania]
    if sum(len(q) for q in zapytania):
        nns = o3d.core.nns.NearestNeighborSearch(o3d.core.Tensor(srodki))
        nns.knn_index()
        idx, d2 = nns.knn_search(o3d.core.Tensor(np.concatenate([q.reshape(-1, 3) for q in zapytania])), 1)
        idx = idx.numpy().ravel().astype(np.int64)
        d = np.sqrt(d2.numpy().ravel())
        et = np.where(d <= TOL_SCIANY_MM, zrodlo[idx], NIEZNANA)
        granice = np.cumsum([0] + [len(q) for q in zapytania])
        wynik_et = [et[granice[k]:granice[k + 1]] for k in range(len(zapytania))]
    _ETYKIETY[klucz] = wynik_et
    return wynik_et


def udzialy(wynik, siatka, pr, k, i):
    """(udzial scian pracy i we fragmencie k, udzial scian cudzych prac we fragmencie, udzial pola plytki)."""
    et = etykiety(wynik, siatka, pr)[k]
    a, b = pr.prace[i].zakres_scian
    wlasne = np.count_nonzero(et == i) / max(b - a, 1)
    if len(et) == 0:
        return wlasne, 0.0, 0.0
    cudze = np.count_nonzero((et >= 0) & (et != i)) / len(et)
    pola = _pola_scian(wynik.fragmenty[k].siatka)
    plyty = float(pola[et == PLYTKA].sum() / max(pola.sum(), 1e-12))
    return wlasne, cudze, plyty


def _fragment_gniazda(wynik, nr, stan=None):
    k = [i for i, f in enumerate(wynik.fragmenty) if f.gniazdo == nr and (stan is None or f.stan == stan)]
    assert len(k) == 1, f"gniazdo {nr}: {len(k)} fragmentow {stan or ''}"
    return k[0]


def _sprawdz_gniazda(uklad, wynik):
    """Jeden fragment na kazde gniazdo (poza fragmentami "poza_gniazdem")."""
    plate = _plate()
    for f in wynik.fragmenty:
        assert isinstance(f, plate.Fragment)
        assert isinstance(f.siatka, trimesh.Trimesh)
        assert f.stan in ("puste", "praca", "podwojne", "poza_gniazdem"), f.stan
    nr = sorted(f.gniazdo for f in wynik.fragmenty if f.stan != "poza_gniazdem")
    assert nr == sorted(g.nr for g in uklad.gniazda)


def _sprawdz_prace(uklad, wynik, siatka, pr, pomin=()):
    """Kazda praca "praca" z prawdy: fragment "praca" w jej gniezdzie z progami udzialow scian."""
    for i, p in enumerate(pr.prace):
        if p.stan != "praca" or i in pomin:
            continue
        k = _fragment_gniazda(wynik, p.gniazdo)
        assert wynik.fragmenty[k].stan == "praca", f"gniazdo {p.gniazdo}: {wynik.fragmenty[k].stan}"
        wlasne, cudze, plyty = udzialy(wynik, siatka, pr, k, i)
        assert wlasne >= MIN_WLASNYCH, f"gniazdo {p.gniazdo}: wlasne {wlasne:.3f}"
        assert cudze <= MAX_CUDZYCH, f"gniazdo {p.gniazdo}: cudze {cudze:.3f}"
        assert plyty <= MAX_PLYTKI, f"gniazdo {p.gniazdo}: plytka {plyty:.4f}"


def _liczba(wynik, stan):
    return sum(f.stan == stan for f in wynik.fragmenty)


def _dwa_najblizsze(uklad, x, y):
    """Numery 2 gniazd najblizszych punktowi: wg odleglosci od obrysu i wg odleglosci od srodka."""
    obrys, srodek = [], []
    for g in uklad.gniazda:
        (px, py), (qx, qy), r = g.os_rynienki()
        vx, vy = qx - px, qy - py
        dl2 = vx * vx + vy * vy
        t = 0.0 if dl2 == 0 else min(1.0, max(0.0, ((x - px) * vx + (y - py) * vy) / dl2))
        obrys.append((math.hypot(x - px - t * vx, y - py - t * vy) - r, g.nr))
        srodek.append((math.hypot(x - g.xy[0], y - g.xy[1]), g.nr))
    return {nr for _, nr in sorted(obrys)[:2]} | {nr for _, nr in sorted(srodek)[:2]}


def _usun_przy_znacznikach(siatka, pr, uklad, narozniki, promien=4.0):
    """Skan bez scian, ktorych srodek lezy w promieniu od osi (pionowej) znacznikow."""
    c = _przenies(_srodki_scian(siatka), _T_prawdy(pr))
    zostaw = np.ones(len(c), dtype=bool)
    for n in narozniki:
        x, y = uklad.znaczniki[n][:2]
        zostaw &= np.hypot(c[:, 0] - x, c[:, 1] - y) >= promien
    return trimesh.Trimesh(np.asarray(siatka.vertices), np.asarray(siatka.faces)[zostaw], process=False)


# --- 1-4. wyrownanie ------------------------------------------------------------------


def test_wyrownanie_dokladnosc(wieczorna, pula30, ustawienia):
    for z in range(1, 9):
        _, siatka, pr = _skan(wieczorna, NUMER, pula30, 6, 0, ziarno=z, szum_mm=0.02)
        w = _plate().wyrownaj(siatka, wieczorna, ustawienia)
        _sprawdz_wyrownanie(wieczorna, w, pr, 0.05, 0.05, max_znacznik=0.08)


def test_wyrownanie_szum_0_04(wieczorna, pula30, ustawienia):
    for z in range(11, 14):
        _, siatka, pr = _skan(wieczorna, NUMER, pula30, 6, 0, ziarno=z, szum_mm=0.04)
        w = _plate().wyrownaj(siatka, wieczorna, ustawienia)
        _sprawdz_wyrownanie(wieczorna, w, pr, 0.08, 0.08)


def test_wyrownanie_obrot_10(wieczorna, pula30, ustawienia):
    T = _obrot_os((1.0, 1.0, 0.0), 1.0) @ _obrot_z(10.0)
    T[:3, 3] = [3.0, -2.0, 1.0]
    _, siatka, pr = _skan(wieczorna, NUMER, pula30, 6, 0, ziarno=15, T_plytki=T)
    assert np.allclose(T @ _T_prawdy(pr), np.eye(4), atol=1e-9)
    w = _plate().wyrownaj(siatka, wieczorna, ustawienia)
    _sprawdz_wyrownanie(wieczorna, w, pr, 0.05, 0.05)


def test_brak_znacznikow(wieczorna, pula30, ustawienia):
    plate = _plate()
    _, siatka, pr = _skan(wieczorna, NUMER, pula30, 3, 0, ziarno=16)
    bez = _usun_przy_znacznikach(siatka, pr, wieczorna, ("A", "C"))
    assert len(bez.faces) < len(siatka.faces)
    with pytest.raises(plate.BladPlytki, match="znacznik"):
        plate.wyrownaj(bez, wieczorna, ustawienia)


# --- 5. numer plytki --------------------------------------------------------------------


@pytest.mark.parametrize("nazwa,numer", [("wieczorna", 1), ("wieczorna", 2), ("wieczorna", 3),
                                         ("poranna", 4), ("poranna", 5), ("poranna", 6),
                                         ("wieczorna", None)])
def test_numer_plytki(nazwa, numer, pula30, ustawienia, request):
    plate = _plate()
    uklad = request.getfixturevalue(nazwa)
    _, siatka, pr = _skan(uklad, numer, pula30, 2, 0, ziarno=30 + (numer or 0))
    w = plate.wyrownaj(siatka, uklad, ustawienia)
    assert plate.numer_plytki(_przeksztalc(siatka, w.T_skan_do_plytki), uklad) == numer


# --- 6-12. ciecie ---------------------------------------------------------------------


def test_ciecie_6(plytka_6, wynik_6, wieczorna):
    _, siatka, pr = plytka_6
    _sprawdz_gniazda(wieczorna, wynik_6)
    assert _liczba(wynik_6, "praca") == 7
    assert _liczba(wynik_6, "puste") == 19
    assert _liczba(wynik_6, "podwojne") == 0
    assert _liczba(wynik_6, "poza_gniazdem") == 0
    zajete = {p.gniazdo for p in pr.prace}
    for f in wynik_6.fragmenty:
        assert (f.stan == "praca") == (f.gniazdo in zajete), f"gniazdo {f.gniazdo}: {f.stan}"
    _sprawdz_prace(wieczorna, wynik_6, siatka, pr)


@pytest.mark.wolne
def test_ciecie_pelne(plytka_pelna, wynik_pelny, wieczorna):
    _, siatka, pr = plytka_pelna
    _sprawdz_gniazda(wieczorna, wynik_pelny)
    assert _liczba(wynik_pelny, "praca") == 26
    assert _liczba(wynik_pelny, "puste") == 0
    assert _liczba(wynik_pelny, "podwojne") == 0
    assert _liczba(wynik_pelny, "poza_gniazdem") == 0
    _sprawdz_prace(wieczorna, wynik_pelny, siatka, pr)


def test_podwojne(wieczorna, pula30, ustawienia):
    _, siatka, pr = _skan(wieczorna, NUMER, pula30, 4, 0, ziarno=41, zmien={1: {"stan": "podwojne"}})
    wynik = _plate().analizuj(siatka, wieczorna, ustawienia)
    _sprawdz_gniazda(wieczorna, wynik)
    podw = next(p for p in pr.prace if p.stan == "podwojne")
    k = _fragment_gniazda(wynik, podw.gniazdo)
    assert wynik.fragmenty[k].stan == "podwojne"
    assert _liczba(wynik, "podwojne") == 1
    assert _liczba(wynik, "praca") == 2
    assert _liczba(wynik, "poza_gniazdem") == 0
    pomin = {i for i, p in enumerate(pr.prace) if p.gniazdo == podw.gniazdo}
    _sprawdz_prace(wieczorna, wynik, siatka, pr, pomin=pomin)


def test_poza_gniazdem(wieczorna, pula30, ustawienia):
    _, siatka, pr = _skan(wieczorna, NUMER, pula30, 4, 0, ziarno=42, zmien={2: {"stan": "poza_gniazdem"}})
    wynik = _plate().analizuj(siatka, wieczorna, ustawienia)
    _sprawdz_gniazda(wieczorna, wynik)
    i_poza = next(i for i, p in enumerate(pr.prace) if p.stan == "poza_gniazdem")
    poza = [k for k, f in enumerate(wynik.fragmenty) if f.stan == "poza_gniazdem"]
    assert len(poza) == 1
    a, b = pr.prace[i_poza].zakres_scian
    v = np.asarray(siatka.vertices)[np.unique(np.asarray(siatka.faces)[a:b])]
    v = _przenies(v, _T_prawdy(pr))
    c = (v.min(axis=0) + v.max(axis=0)) / 2
    assert wynik.fragmenty[poza[0]].gniazdo in _dwa_najblizsze(wieczorna, c[0], c[1])
    wlasne, _, _ = udzialy(wynik, siatka, pr, poza[0], i_poza)
    assert wlasne >= 0.5, f"fragment poza_gniazdem ma {wlasne:.3f} scian pracy"
    for k, f in enumerate(wynik.fragmenty):
        if f.stan == "praca":
            assert udzialy(wynik, siatka, pr, k, i_poza)[0] <= 0.05, f"gniazdo {f.gniazdo}"
    assert _liczba(wynik, "praca") == 3
    _sprawdz_prace(wieczorna, wynik, siatka, pr)


def test_rynienka_most(plytka_6, wynik_6, wieczorna):
    rozm, siatka, pr = plytka_6
    i = next(i for i, r in enumerate(rozm) if r.projekt.rodzaj == "most")
    nr = pr.prace[i].gniazdo
    assert wieczorna.gniazdo(nr).rodzaj == "rynienka"
    k = _fragment_gniazda(wynik_6, nr)
    assert wynik_6.fragmenty[k].stan == "praca"
    wlasne, _, _ = udzialy(wynik_6, siatka, pr, k, i)
    assert wlasne >= MIN_WLASNYCH, f"most: {wlasne:.3f}"


def test_poranna(poranna, pula_z_mostami, ustawienia):
    rozm, siatka, pr = _skan(poranna, 5, pula_z_mostami, 10, 1, ziarno=51)
    assert all(r.wspolczynnik == 1.0 for r in rozm)
    wynik = _plate().analizuj(siatka, poranna, ustawienia)
    assert wynik.numer == 5
    _sprawdz_gniazda(poranna, wynik)
    assert _liczba(wynik, "praca") == 11
    zajete = {p.gniazdo for p in pr.prace}
    assert {f.gniazdo for f in wynik.fragmenty if f.stan == "praca"} == zajete
    _sprawdz_prace(poranna, wynik, siatka, pr)


def test_fragment_uklad(wynik_6):
    for f in wynik_6.fragmenty:
        if f.stan == "praca":
            assert len(f.siatka.faces) > 0, f"gniazdo {f.gniazdo}"
        if len(f.siatka.faces) == 0:
            continue
        # qc.inspect bierze wszystkie wierzcholki fragmentu: bez nieuzywanych
        assert len(np.unique(np.asarray(f.siatka.faces))) == len(f.siatka.vertices), f"gniazdo {f.gniazdo}"
        v = np.asarray(f.siatka.vertices, dtype=np.float64)
        assert v[:, 2].min() >= -4.5, f"gniazdo {f.gniazdo}: min z {v[:, 2].min():.2f}"
        assert v[:, 2].max() <= 10.5, f"gniazdo {f.gniazdo}: max z {v[:, 2].max():.2f}"


def test_wynik_analizuj(plytka_6, wynik_6, wieczorna):
    plate = _plate()
    _, siatka, pr = plytka_6
    assert isinstance(wynik_6, plate.WynikPlytki)
    assert wynik_6.numer == NUMER
    dt, dk = blad_T(wynik_6.wyrownanie.T_skan_do_plytki, _T_prawdy(pr))
    assert dt <= 0.05 and dk <= 0.05
    assert len(wynik_6.skan_wyrownany.faces) > 0
    v = np.asarray(wynik_6.skan_wyrownany.vertices, dtype=np.float64)
    assert np.all(np.abs(v[:, :2]) <= 49.0)


# --- 13. czas -----------------------------------------------------------------------


def test_czas(plytka_6, wynik_6, wieczorna, ustawienia):
    _, siatka, _ = plytka_6
    t0 = time.perf_counter()
    _plate().analizuj(siatka, wieczorna, ustawienia)
    czas = time.perf_counter() - t0
    assert czas <= 15.0, f"{czas:.1f} s"


@pytest.mark.wolne
def test_czas_pelny(plytka_pelna, wynik_pelny, wieczorna, ustawienia):
    _, siatka, _ = plytka_pelna
    t0 = time.perf_counter()
    _plate().analizuj(siatka, wieczorna, ustawienia)
    czas = time.perf_counter() - t0
    assert czas <= 40.0, f"{czas:.1f} s"


# --- 14. lancuch plate -> inspect ------------------------------------------------------


def test_wynik_dla_inspect(wieczorna, pula30, ustawienia):
    import qc.inspect as inspect
    from qc.inspect import metryki

    rozm, siatka, pr = _skan(wieczorna, NUMER, pula30, 3, 0, ziarno=61,
                             zmien={i: {"ubytki": 2} for i in range(3)})
    wynik = _plate().analizuj(siatka, wieczorna, ustawienia)
    T_sp = _T_prawdy(pr)
    wykryte = wszystkie = 0
    for r, p in zip(rozm, pr.prace):
        k = _fragment_gniazda(wynik, p.gniazdo, "praca")
        T = T_sp @ p.T_projekt_do_skanu
        wi = inspect.sprawdz(wynik.fragmenty[k].siatka, r.projekt.siatka, T, ustawienia)
        c = metryki.porownaj(wi, p, T, tolerancja_mm=0.5)
        wykryte += c.wykryte
        wszystkie += c.wykryte + c.pominiete
    assert wszystkie == 6
    assert wykryte >= 5, f"wykryte {wykryte}/6"


# --- 15-19. odpornosc (poprawki po recenzji) --------------------------------------------


def _bez_scian(siatka, usun):
    """Kopia skanu bez wskazanych scian (wierzcholki zostaja; zakresy prawdy nieaktualne)."""
    return trimesh.Trimesh(np.asarray(siatka.vertices), np.asarray(siatka.faces)[~usun], process=False)


def _sprawdz_powtarzalnosc(siatka, uklad, ustawienia, n):
    plate = _plate()
    macierze = []
    for _ in range(n):
        macierze.append(np.asarray(plate.wyrownaj(siatka, uklad, ustawienia).T_skan_do_plytki, dtype=np.float64))
    for i, T in enumerate(macierze[1:], start=1):
        assert np.allclose(T, macierze[0], atol=1e-6), f"wywolanie {i}: max roznica {np.abs(T - macierze[0]).max():.2e}"
    return macierze[0]


@pytest.mark.wolne
def test_wyrownanie_powtarzalne(plytka_pelna, wieczorna, ustawienia):
    _, siatka, pr = plytka_pelna
    T = _sprawdz_powtarzalnosc(siatka, wieczorna, ustawienia, 10)
    dt, dk = blad_T(T, _T_prawdy(pr))
    assert dt <= 0.05 and dk <= 0.05, f"{dt:.4f} mm, {dk:.4f} st."


def test_wyrownanie_powtarzalne_szybkie(wieczorna, pula_z_mostami, ustawienia):
    _, siatka, pr = _skan(wieczorna, NUMER, pula_z_mostami, 12, 2, ziarno=71)
    T = _sprawdz_powtarzalnosc(siatka, wieczorna, ustawienia, 5)
    dt, dk = blad_T(T, _T_prawdy(pr))
    assert dt <= 0.05 and dk <= 0.05, f"{dt:.4f} mm, {dk:.4f} st."


def test_skan_z_gory(plytka_6, wieczorna, ustawienia):
    """Skan tylko z gory (bez scian o normalnej z < -0,3) i z szumem plytki 0,03 mm wzdluz normalnych."""
    from qc.syntetyka.skan import normalne_wierzcholkow

    _, siatka, pr = plytka_6
    v = np.asarray(siatka.vertices, dtype=np.float64).copy()
    f = np.asarray(siatka.faces, dtype=np.int64)
    koniec_plytki = min(p.zakres_scian[0] for p in pr.prace)
    w_plytki = np.unique(f[:koniec_plytki])
    n = normalne_wierzcholkow(v, f)
    rng = np.random.default_rng(17)
    v[w_plytki] += n[w_plytki] * rng.normal(0.0, 0.03, len(w_plytki))[:, None]
    zaszumiona = trimesh.Trimesh(v, f, process=False)
    z_gory = _bez_scian(zaszumiona, np.asarray(zaszumiona.face_normals)[:, 2] < -0.3)
    assert len(z_gory.faces) < len(f)
    wynik = _plate().analizuj(z_gory, wieczorna, ustawienia)
    assert wynik.numer == NUMER
    dt, dk = blad_T(wynik.wyrownanie.T_skan_do_plytki, _T_prawdy(pr))
    assert dt <= 0.05, f"translacja {dt:.4f} mm"
    assert dk <= 0.05, f"kat {dk:.4f} st."
    _sprawdz_gniazda(wieczorna, wynik)
    assert _liczba(wynik, "podwojne") == 0
    assert _liczba(wynik, "poza_gniazdem") == 0
    assert _liczba(wynik, "praca") == 7
    assert {f.gniazdo for f in wynik.fragmenty if f.stan == "praca"} == {p.gniazdo for p in pr.prace}


@pytest.fixture(scope="session")
def plytka_nr3(wieczorna, pula30):
    """Plytka wieczorna nr 3 (dolki A, B; relief): 2 korony, T losowa."""
    return _skan(wieczorna, 3, pula30, 2, 0, ziarno=81)


def _srodki_w_plytce(siatka, pr):
    return _przenies(_srodki_scian(siatka), _T_prawdy(pr))


def test_dolek_zakryty(plytka_nr3, wieczorna, ustawienia):
    plate = _plate()
    _, siatka, pr = plytka_nr3
    T = _T_prawdy(pr)
    assert plate.numer_plytki(_przeksztalc(siatka, T), wieczorna) == 3
    c = _srodki_w_plytce(siatka, pr)
    dx, dy = wieczorna.dolki_kodu["A"]
    w_kole = np.hypot(c[:, 0] - dx, c[:, 1] - dy) < 1.5
    # caly dolek A bez danych: bit nieznany -> None (nie 2)
    bez_dolka = _bez_scian(siatka, w_kole)
    assert plate.numer_plytki(_przeksztalc(bez_dolka, T), wieczorna) is None
    wynik = plate.analizuj(bez_dolka, wieczorna, ustawienia)
    assert wynik.numer is None
    assert any("dolek" in u or "kod" in u for u in wynik.uwagi), wynik.uwagi
    # polowa dolka wystarcza
    pol = _bez_scian(siatka, w_kole & (c[:, 0] < dx))
    assert plate.numer_plytki(_przeksztalc(pol, T), wieczorna) == 3


def test_relief_nie_praca(plytka_nr3, wieczorna, ustawienia):
    plate = _plate()
    _, siatka, pr = plytka_nr3
    T = _T_prawdy(pr)
    c = _srodki_w_plytce(siatka, pr)
    przyciety = _przeksztalc(_bez_scian(siatka, (np.abs(c[:, 0]) > 43) | (np.abs(c[:, 1]) > 43)), T)
    fragmenty = plate.potnij(przyciety, wieczorna, ustawienia)
    rx, ry = wieczorna.relief_numeru[:2]
    poza = [f for f in fragmenty if f.stan == "poza_gniazdem"]
    assert not poza, [(f.gniazdo, len(f.siatka.faces), np.asarray(f.siatka.vertices).mean(axis=0).round(1).tolist())
                      for f in poza]
    assert sum(f.stan == "praca" for f in fragmenty) == 2
    # pelna plytka: relief takze nie jest praca
    assert not [f for f in plate.potnij(_przeksztalc(siatka, T), wieczorna, ustawienia) if f.stan == "poza_gniazdem"]
    assert abs(rx) <= 48 and abs(ry) <= 48
