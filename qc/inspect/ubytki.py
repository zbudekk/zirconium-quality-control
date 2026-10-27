"""Wykrywanie ubytkow na mapie odchylek: korekta niedopasowania, wygladzanie w mm, skladowe, klasyfikacja."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import open3d as o3d

# wygladzanie: jadro gaussowskie po pozycjach (sigma = promien / 2) w promieniu
# PROMIEN_WYGLADZANIA x skaner.gestosc_mm - niezalezne od podzialu siatki
PROMIEN_WYGLADZANIA = 1.5
# minimalna liczba punktow nasion w skladowej (jak min_points w DBSCAN)
MIN_PUNKTOW = 4
# obszar ubytku = punkty z d <= -poziom, poziom = max(UDZIAL_POZIOMU x glebokosc szczytowa, SIGMY_SZUMU x
# sigma szumu wygladzonego d, MIN_POZIOM_MM)
UDZIAL_POZIOMU = 0.25
SIGMY_SZUMU = 3.0
MIN_POZIOM_MM = 0.02
# stromosc obwodu mierzona miedzy poziomami DOLNY_POZIOM i GORNY_POZIOM glebokosci
DOLNY_POZIOM = 0.3
GORNY_POZIOM = 0.7
# korekta sztywnego niedopasowania T: iteracje dopasowania z odrzucaniem punktow > PROG_ODRZUCENIA sigma
ITERACJE_KOREKTY = 3
PROG_ODRZUCENIA = 2.5
CO_KTORY_PUNKT_KOREKTY = 3  # dopasowanie na podprobce (6 parametrow + stala), korekta wszystkich punktow


@dataclass
class Ubytek:
    """Wykryty ubytek; srodek w ukladzie fragmentu."""

    srodek: np.ndarray
    srednica_mm: float
    glebokosc_mm: float
    przy_brzegu: bool
    stromosc: float = 0.0  # mm/mm na obwodzie (ukruszenie ostre, poprawka gladka)


@dataclass
class WynikInspekcji:
    ubytki: list[Ubytek] = field(default_factory=list)  # ukruszenia przy brzegu
    poprawki: list[Ubytek] = field(default_factory=list)  # szerokie gladkie zaglebienia
    inne: list[Ubytek] = field(default_factory=list)  # pozostale (poza pasem brzegu, nietypowe)
    drgniecie: bool = False
    mapa: np.ndarray = field(default_factory=lambda: np.zeros(0))  # odleglosci per wierzcholek


@dataclass
class Sasiedztwo:
    """Pary punktow fragmentu w promieniu (kazda raz, i < j), odleglosci i krawedzie siatki."""

    i: np.ndarray
    j: np.ndarray
    odl: np.ndarray
    krawedzie: np.ndarray  # (E, 2) unikalne krawedzie siatki (lo, hi); puste bez scian


def krawedzie_siatki(sciany, n: int) -> np.ndarray:
    if sciany is None or len(sciany) == 0:
        return np.zeros((0, 2), dtype=np.int64)
    f = np.asarray(sciany, dtype=np.int64)
    a = np.concatenate([f[:, 0], f[:, 1], f[:, 2]])
    b = np.concatenate([f[:, 1], f[:, 2], f[:, 0]])
    lo, hi = np.minimum(a, b), np.maximum(a, b)
    kod = np.sort(lo[lo != hi] * n + hi[lo != hi])
    kod = kod[np.concatenate([[True], kod[1:] != kod[:-1]])] if len(kod) else kod
    return np.stack([kod // n, kod % n], axis=1)


def sasiedztwo(mapa, promien_mm: float) -> Sasiedztwo:
    punkty = np.ascontiguousarray(mapa.punkty, dtype=np.float32)
    n = len(punkty)
    t = o3d.core.Tensor(punkty)
    nns = o3d.core.nns.NearestNeighborSearch(t)
    nns.fixed_radius_index(promien_mm)
    ind, odl2, podzialy = nns.fixed_radius_search(t, promien_mm, sort=False)
    ind = ind.numpy().astype(np.int64)
    podzialy = podzialy.numpy().astype(np.int64)
    i = np.repeat(np.arange(n), np.diff(podzialy))
    raz = i < ind
    return Sasiedztwo(i=i[raz], j=ind[raz], odl=np.sqrt(odl2.numpy()[raz].astype(np.float64)),
                      krawedzie=krawedzie_siatki(getattr(mapa, "sciany", None), n))


def odstep_punktow(mapa) -> float:
    """Mediana dlugosci krawedzi scian fragmentu (0 bez scian)."""
    sciany = getattr(mapa, "sciany", None)
    if sciany is None or len(sciany) == 0:
        return 0.0
    p = np.asarray(mapa.punkty, dtype=np.float64)
    f = np.asarray(sciany, dtype=np.int64)
    return float(np.median(np.linalg.norm(p[f[:, 0]] - p[f[:, 1]], axis=1)))


def promien_wygladzania(mapa, ustawienia) -> float:
    """PROMIEN_WYGLADZANIA x max(skaner.gestosc_mm, odstep punktow skanu) - rzadszy skan = wiekszy promien."""
    return PROMIEN_WYGLADZANIA * max(float(ustawienia.skaner.gestosc_mm), odstep_punktow(mapa))


def wygladz(d: np.ndarray, s: Sasiedztwo, promien_mm: float) -> np.ndarray:
    """Srednia d wazona jadrem gaussowskim po pozycjach w promieniu promien_mm."""
    w = np.where(s.odl <= promien_mm, np.exp(-0.5 * (s.odl / (0.5 * promien_mm)) ** 2), 0.0)
    n = len(d)
    suma = d + np.bincount(s.i, weights=w * d[s.j], minlength=n) + np.bincount(s.j, weights=w * d[s.i], minlength=n)
    wagi = 1.0 + np.bincount(s.i, weights=w, minlength=n) + np.bincount(s.j, weights=w, minlength=n)
    return suma / wagi


def sigma_szumu(d: np.ndarray) -> float:
    return float(1.4826 * np.median(np.abs(d - np.median(d))))


def korekta_dopasowania(mapa, d: np.ndarray) -> np.ndarray:
    """d bez sztywnego niedopasowania T (liniowo: d ~ n.t + (p x n).w + c, z odrzucaniem odstajacych).

    Ukruszenia i poprawki zajmuja maly ulamek powierzchni, wiec odpadaja jako punkty odstajace.
    """
    p = np.asarray(mapa.punkty, dtype=np.float64)
    p = p - p.mean(axis=0)
    nrm = np.asarray(mapa.normalne_projektu, dtype=np.float64)
    A = np.hstack([nrm, np.cross(p, nrm), np.ones((len(p), 1))])
    Ap, dp = A[::CO_KTORY_PUNKT_KOREKTY], d[::CO_KTORY_PUNKT_KOREKTY]
    uzyte = np.ones(len(dp), dtype=bool)
    x = np.zeros(A.shape[1])
    for _ in range(ITERACJE_KOREKTY):
        if uzyte.sum() < 7 * 3:
            break
        x, *_ = np.linalg.lstsq(Ap[uzyte], dp[uzyte], rcond=None)
        reszta = dp - Ap @ x
        uzyte = np.abs(reszta) <= PROG_ODRZUCENIA * max(sigma_szumu(reszta), 1e-4)
    return d - A @ x


def skladowe(maska: np.ndarray, kraw: np.ndarray) -> np.ndarray:
    """Etykiety skladowych spojnych podgrafu na wierzcholkach maski (-1 poza maska)."""
    etykiety = np.where(maska, np.arange(len(maska)), -1)
    k = kraw[maska[kraw[:, 0]] & maska[kraw[:, 1]]]
    if len(k) == 0:
        return etykiety
    a, b = k[:, 0], k[:, 1]
    while True:
        m = np.minimum(etykiety[a], etykiety[b])
        stare = etykiety.copy()
        np.minimum.at(etykiety, a, m)
        np.minimum.at(etykiety, b, m)
        wybrane = etykiety >= 0
        etykiety[wybrane] = etykiety[etykiety[wybrane]]  # skok wskaznikow (etykieta <= indeks)
        if np.array_equal(etykiety, stare):
            return etykiety


def _promien(punkty: np.ndarray, srodek: np.ndarray) -> float:
    """Promien kola o tym samym 90. percentylu odleglosci od srodka."""
    if len(punkty) == 0:
        return 0.0
    return float(np.percentile(np.linalg.norm(punkty - srodek, axis=1), 90)) / np.sqrt(0.9)


def szukaj_ubytkow(mapa, ustawienia, s: Sasiedztwo | None = None) -> WynikInspekcji:
    """Ubytki, poprawki i inne zaglebienia na mapie odchylek (bez sprawdzania drgniecia).

    s = gotowe sasiedztwo w promieniu >= promien_wygladzania (z sprawdz), inaczej liczone tutaj.
    """
    u = ustawienia.ubytki
    d = np.asarray(mapa.odleglosci, dtype=np.float64)
    wynik = WynikInspekcji(mapa=d)
    if len(d) < MIN_PUNKTOW:
        return wynik
    promien = promien_wygladzania(mapa, ustawienia)
    if s is None:
        s = sasiedztwo(mapa, promien)
    ds = wygladz(korekta_dopasowania(mapa, d), s, promien)
    # graf skladowych: pary punktow w promieniu wygladzania (nie zalezy od podzialu siatki)
    blisko = s.odl <= promien
    kraw = np.stack([s.i[blisko], s.j[blisko]], axis=1)
    sigma = sigma_szumu(ds)
    punkty = np.asarray(mapa.punkty, dtype=np.float64)

    nasiona = skladowe(ds <= -float(u.min_glebokosc_mm), kraw)
    etyk, liczby = np.unique(nasiona[nasiona >= 0], return_counts=True)
    etyk = etyk[liczby >= MIN_PUNKTOW]
    # od najglebszych; nasiona wchloniete przez obszar wczesniejszego ubytku pomijane
    etyk = sorted(etyk, key=lambda e: float(ds[nasiona == e].min()))
    zajete = np.zeros(len(d), dtype=bool)
    for e in etyk:
        czlonkowie = np.flatnonzero(nasiona == e)
        if zajete[czlonkowie].any():
            continue
        szczyt = -float(np.percentile(ds[czlonkowie], 5))
        poziom = max(UDZIAL_POZIOMU * szczyt, SIGMY_SZUMU * sigma, MIN_POZIOM_MM)
        obszar_et = skladowe(ds <= -poziom, kraw)
        etykiety_obszaru = np.unique(obszar_et[czlonkowie])
        obszar = np.flatnonzero(np.isin(obszar_et, etykiety_obszaru[etykiety_obszaru >= 0]))
        if len(obszar) < MIN_PUNKTOW:
            continue
        zajete[obszar] = True

        do = ds[obszar]
        glebokosc = -float(np.percentile(do, 10))
        wagi = np.clip(-do, 1e-9, None)
        srodek = (punkty[obszar] * wagi[:, None]).sum(axis=0) / wagi.sum()
        promien = _promien(punkty[obszar], srodek)
        # stromosc obwodu: roznica poziomow / roznica promieni obszarow na tych poziomach
        p1 = max(DOLNY_POZIOM * glebokosc, poziom)
        p2 = max(GORNY_POZIOM * glebokosc, 0.5 * (p1 + glebokosc))
        r1 = _promien(punkty[obszar[do <= -p1]], srodek)
        r2 = _promien(punkty[obszar[do <= -p2]], srodek)
        stromosc = (p2 - p1) / max(r1 - r2, 1e-3)
        ostra = stromosc >= float(u.ostrosc_min)
        srednica = 2.0 * promien
        if not ostra and szczyt > poziom * 1.05:
            # profil gaussowski: promien obszaru na poziomie p -> sigma; srednica poprawki = 4 sigma
            srednica = 2.0 * srednica / np.sqrt(2.0 * np.log(szczyt / poziom))
        najglebszy = obszar[int(np.argmin(do))]
        ubytek = Ubytek(srodek=srodek, srednica_mm=float(srednica), glebokosc_mm=glebokosc,
                        przy_brzegu=bool(mapa.przy_brzegu[najglebszy]), stromosc=float(stromosc))
        if ostra and u.min_srednica_mm <= srednica <= u.max_srednica_mm and ubytek.przy_brzegu:
            wynik.ubytki.append(ubytek)
        elif not ostra and srednica > u.poprawka_min_srednica_mm:
            wynik.poprawki.append(ubytek)
        else:
            wynik.inne.append(ubytek)
    return wynik
