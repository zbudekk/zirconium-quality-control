"""Syntetyczne skany prac: skala, szum, ubytki przy brzegu, poprawki, drgniecie, pokrycie.

Skan powstaje z projektu (uklad projektu, mm): ubytki i szum w ukladzie projektu, potem skala k
(T_projekt_do_skanu = diag(k, k, k, 1)) i tasowanie wierzcholkow oraz scian. Zwraca siatke i prawde.
"""

from __future__ import annotations

import math

import numpy as np
import trimesh

from qc.syntetyka.prawda import PrawdaPracy, UbytekPrawda

SEKTORY = 24
SIATKA_WZORCA_MM = 0.1
PAS_BRZEGU_MM = 0.3
ODSTEP_UBYTKOW_MM = 2.0
MAX_OD_BRZEGU_MM = 0.5
PRZESUNIECIE_DRGNIECIA_MM = 0.10
UDZIAL_DRGNIECIA = 0.40

ZAKRESY_UBYTKOW = {
    "ukruszenie": dict(srednica_mm=(0.2, 0.6), glebokosc_mm=(0.1, 0.3)),
    "poprawka": dict(srednica_mm=(2.5, 4.0), glebokosc_mm=(0.08, 0.2)),
}


def _siatka(projekt) -> trimesh.Trimesh:
    return projekt.siatka if hasattr(projekt, "siatka") else projekt


def normalne_wierzcholkow(v: np.ndarray, f: np.ndarray) -> np.ndarray:
    """Normalne wierzcholkow wazone polem scian (numpy; trimesh bez scipy liczy je bardzo wolno)."""
    c = np.cross(v[f[:, 1]] - v[f[:, 0]], v[f[:, 2]] - v[f[:, 0]])
    n = np.zeros((len(v), 3))
    for os_ in range(3):
        n[:, os_] = np.bincount(f.ravel(), weights=np.repeat(c[:, os_], 3), minlength=len(v))
    return n / np.maximum(np.linalg.norm(n, axis=1), 1e-15)[:, None]


def _zewnetrzne(siatka: trimesh.Trimesh, zmin: float, zmax: float) -> np.ndarray:
    """Indeksy wierzcholkow powierzchni zewnetrznej w pasie zmin <= z <= zmax.

    Punkt odsuniety o 0,5 mm wzdluz poziomej skladowej normalnej: we wnece korony jest otoczony
    probkami pasa ze wszystkich stron (wszystkie sektory katowe zajete), na zewnatrz nie.
    """
    v = np.asarray(siatka.vertices, dtype=np.float64)
    n = normalne_wierzcholkow(v, np.asarray(siatka.faces, dtype=np.int64))
    kand = np.flatnonzero((v[:, 2] >= zmin) & (v[:, 2] <= zmax))
    nxy = n[kand, :2]
    dl = np.linalg.norm(nxy, axis=1)
    kand, nxy, dl = kand[dl > 1e-6], nxy[dl > 1e-6], dl[dl > 1e-6]
    if len(kand) == 0:
        return kand
    q = v[kand, :2] + 0.5 * nxy / dl[:, None]
    # wzorzec: probki pasa przerzedzone siatka 0,1 mm (rowna gestosc katowa)
    _, jedne = np.unique(np.floor(v[kand, :2] / SIATKA_WZORCA_MM).astype(np.int64), axis=0, return_index=True)
    wzor = v[kand[np.sort(jedne)], :2]
    zewn = np.zeros(len(kand), dtype=bool)
    for start in range(0, len(kand), 400):
        d = wzor[None, :, :] - q[start:start + 400, None, :]
        kat = np.arctan2(d[..., 1], d[..., 0])
        sektor = ((kat + math.pi) / (2 * math.pi) * SEKTORY).astype(np.int64) % SEKTORY
        wiersz = np.arange(sektor.shape[0])[:, None]
        zajete = np.zeros((sektor.shape[0], SEKTORY), dtype=bool)
        zajete[np.broadcast_to(wiersz, sektor.shape), sektor] = True
        zewn[start:start + 400] = ~zajete.all(axis=1)
    return kand[zewn]


def brzeg(projekt) -> np.ndarray:
    """Probki krzywej brzegu (N,3): wierzcholki powierzchni zewnetrznej w pasie |z| < 0,3 mm."""
    m = _siatka(projekt)
    idx = _zewnetrzne(m, -PAS_BRZEGU_MM, PAS_BRZEGU_MM)
    return np.asarray(m.vertices, dtype=np.float64)[idx]


def _specyfikacje(ubytki, rodzaj: str, rng: np.random.Generator) -> list[dict]:
    zakres = ZAKRESY_UBYTKOW[rodzaj]
    lista = [{} for _ in range(int(ubytki))] if isinstance(ubytki, (int, np.integer)) else [dict(u) for u in ubytki]
    for u in lista:
        u["rodzaj"] = rodzaj
        for klucz, (a, b) in zakres.items():
            wartosc = float(rng.uniform(a, b))
            u.setdefault(klucz, wartosc)
    return lista


def _wybierz_srodki(siatka, spec, rng) -> np.ndarray:
    """Uzupelnia spec o srodek (wierzcholek powierzchni zewnetrznej przy brzegu); zwraca krzywa brzegu."""
    v = np.asarray(siatka.vertices, dtype=np.float64)
    zmax = max([u["srednica_mm"] / 2 + 0.3 if u["rodzaj"] == "poprawka" else 0.6 for u in spec] + [0.6])
    # jedno wywolanie _zewnetrzne: kandydaci na srodki i krzywa brzegu (pas |z| < 0,3) naraz
    kand = _zewnetrzne(siatka, -PAS_BRZEGU_MM, zmax)
    krzywa = v[kand[np.abs(v[kand, 2]) < PAS_BRZEGU_MM]]
    zajete = [(np.asarray(u["srodek"], dtype=np.float64), u["srednica_mm"] / 2) for u in spec if "srodek" in u]
    for u in spec:
        if "srodek" in u:
            continue
        r, g = u["srednica_mm"] / 2, u["glebokosc_mm"]
        if u["rodzaj"] == "ukruszenie":
            # wyzej niz glebokosc, zeby dno ubytku nie wychodzilo pod plaszczyzne brzegu
            zlo = 0.5 * r + 0.85 * g + 0.05
            zhi = max(zlo + 0.05, 0.55)
        else:
            zlo, zhi = r, r + 0.3
        pula = kand[(v[kand, 2] >= zlo) & (v[kand, 2] <= zhi)]
        dobre = np.ones(len(pula), dtype=bool)
        for c, rc in zajete:
            odstep = max(ODSTEP_UBYTKOW_MM, r + rc + 0.5)
            dobre &= np.linalg.norm(v[pula] - c, axis=1) >= odstep
        if u["rodzaj"] == "ukruszenie" and len(krzywa):
            for i in np.flatnonzero(dobre):
                if np.min(np.linalg.norm(krzywa - v[pula[i]], axis=1)) > MAX_OD_BRZEGU_MM:
                    dobre[i] = False
        pula = pula[dobre]
        if len(pula) == 0:
            raise ValueError("brak miejsca na kolejny ubytek przy brzegu")
        c = v[int(rng.choice(pula))].copy()
        u["srodek"] = c
        zajete.append((c, r))
    return krzywa


def _zagesc(v, f, n, srodek, r, krok):
    """Lokalny podzial trojkatow w kuli 2r, az krawedz <= r/4."""
    iteracje = int(math.ceil(math.log2(krok / (r / 4)))) if krok > r / 4 else 0
    for _ in range(iteracje):
        blisko = np.linalg.norm(v - srodek, axis=1) <= 2 * r + krok
        wybrane = np.flatnonzero(blisko[f].any(axis=1))
        if len(wybrane) == 0:
            break
        v, f, atr = _podziel(v, f, wybrane, n)
        n = atr
        krok /= 2
    return v, f, n


def _podziel(v, f, wybrane, n):
    # normalne nowych wierzcholkow (srodki krawedzi) = srednia normalnych koncow
    v2, f2, atr = trimesh.remesh.subdivide(v, f, face_index=wybrane, vertex_attributes={"n": n})
    n2 = atr["n"]
    n2 /= np.maximum(np.linalg.norm(n2, axis=1), 1e-12)[:, None]
    return v2, f2, n2


def _normalne_scian(v, f):
    c = np.cross(v[f[:, 1]] - v[f[:, 0]], v[f[:, 2]] - v[f[:, 0]])
    pole = np.linalg.norm(c, axis=1)
    return c / np.maximum(pole, 1e-15)[:, None], pole / 2


def _drgniecie(v, f, rng):
    """Kopia ~40 % scian (polowa bryly od strony kierunku u) przesunieta o 0,1 mm wzdluz sredniej normalnej."""
    kat = rng.uniform(0, 2 * math.pi)
    u = np.array([math.cos(kat), math.sin(kat), 0.0])
    ns, pole = _normalne_scian(v, f)
    c = v[f].mean(axis=1)
    strona = (c - c.mean(axis=0)) @ u >= 0
    kand = np.flatnonzero(strona)
    ile = min(int(round(UDZIAL_DRGNIECIA * len(f))), len(kand))
    kand = kand[np.argsort(-np.abs(ns[kand] @ u), kind="stable")[:ile]]
    znak = np.sign(ns[kand] @ u)
    n_sr = (ns[kand] * (znak * pole[kand])[:, None]).sum(axis=0)
    n_sr /= np.linalg.norm(n_sr)
    wierzch, odwr = np.unique(f[kand], return_inverse=True)
    nowe_v = v[wierzch] + PRZESUNIECIE_DRGNIECIA_MM * n_sr
    nowe_f = odwr.reshape(-1, 3) + len(v)
    return np.vstack([v, nowe_v]), np.vstack([f, nowe_f])


def _pokrycie(v, f, pokrycie, rng):
    """Usuwa sciany w 3-6 platach (kule wokol losowych scian) do udzialu pola = pokrycie.

    Wolane PRZED szumem: udzial liczony z pol scian bez szumu (szum zawyza pole o kilkanascie procent),
    wiec prawda.pokrycie nie zalezy od szum_mm.
    """
    _, pole = _normalne_scian(v, f)
    c = v[f].mean(axis=1)
    n_platow = int(rng.integers(3, 7))
    ziarna = c[rng.choice(len(f), n_platow, replace=False, p=pole / pole.sum())]
    odl = np.min(np.linalg.norm(c[:, None, :] - ziarna[None, :, :], axis=2), axis=1)
    cel = (1 - pokrycie) * pole.sum()
    lo, hi = 0.0, float(odl.max())
    for _ in range(40):
        sr = (lo + hi) / 2
        if pole[odl < sr].sum() < cel:
            lo = sr
        else:
            hi = sr
    return f[odl >= hi]


def _sprawdz_argumenty(wspolczynnik, szum_mm, ubytki, poprawki, pokrycie, widocznosc) -> None:
    if not wspolczynnik > 0:
        raise ValueError(f"wspolczynnik musi byc > 0, jest {wspolczynnik}")
    if not szum_mm >= 0:
        raise ValueError(f"szum_mm nie moze byc ujemny, jest {szum_mm}")
    if not 0 < pokrycie <= 1:
        raise ValueError(f"pokrycie musi byc w przedziale (0; 1], jest {pokrycie}")
    for nazwa, wartosc in (("ubytki", ubytki), ("poprawki", poprawki)):
        if isinstance(wartosc, (int, np.integer)) and not isinstance(wartosc, bool):
            if wartosc < 0:
                raise ValueError(f"{nazwa} nie moze byc ujemne, jest {wartosc}")
        elif not isinstance(wartosc, (list, tuple)):
            raise ValueError(f"{nazwa}: oczekiwano liczby albo listy slownikow, jest {type(wartosc).__name__}")
    if widocznosc not in ("pelna", "z_gory"):
        raise ValueError(f"nieznana widocznosc: {widocznosc} (dozwolone: pelna, z_gory)")


def skan_pracy(projekt, ziarno: int, wspolczynnik: float = 1.0, szum_mm: float = 0.02,
               ubytki=0, poprawki=0, drgniecie: bool = False, pokrycie: float = 1.0,
               widocznosc: str = "pelna") -> tuple[trimesh.Trimesh, PrawdaPracy]:
    """Syntetyczny skan pracy i prawda o nim (srodki ubytkow w ukladzie projektu)."""
    _sprawdz_argumenty(wspolczynnik, szum_mm, ubytki, poprawki, pokrycie, widocznosc)
    m = _siatka(projekt)
    rng = np.random.default_rng(ziarno)
    v = np.array(m.vertices, dtype=np.float64)
    f = np.array(m.faces, dtype=np.int64)
    n = normalne_wierzcholkow(v, f)
    krok = float(np.linalg.norm(v[f[:, 0]] - v[f[:, 1]], axis=1).mean())

    spec = _specyfikacje(ubytki, "ukruszenie", rng) + _specyfikacje(poprawki, "poprawka", rng)
    krzywa = _wybierz_srodki(m, spec, rng) if spec else np.zeros((0, 3))

    for u in spec:
        c = np.asarray(u["srodek"], dtype=np.float64)
        r = u["srednica_mm"] / 2
        if u["rodzaj"] == "ukruszenie":
            v, f, n = _zagesc(v, f, n, c, r, krok)
    for u in spec:
        c = np.asarray(u["srodek"], dtype=np.float64)
        r, g = u["srednica_mm"] / 2, u["glebokosc_mm"]
        n_c = n[int(np.argmin(np.linalg.norm(v - c, axis=1)))]
        rho = np.linalg.norm(v - c, axis=1)
        if u["rodzaj"] == "ukruszenie":
            maska = (rho < r) & (n @ n_c > 0.3)
            profil = g * np.clip((r - rho[maska]) / (0.3 * r), 0.0, 1.0)
        else:
            maska = (rho < 2 * r) & (n @ n_c > 0.3)
            profil = g * np.exp(-rho[maska] ** 2 / (2 * (r / 2) ** 2))
        v[maska] -= n[maska] * profil[:, None]

    if pokrycie < 1.0:
        f = _pokrycie(v, f, pokrycie, rng)

    # szum wzdluz normalnych liczonych przed ubytkami
    if szum_mm > 0:
        v = v + n * rng.normal(0.0, szum_mm, len(v))[:, None]

    if drgniecie:
        v, f = _drgniecie(v, f, rng)
    if widocznosc == "z_gory":
        ns, _ = _normalne_scian(v, f)
        f = f[ns[:, 2] >= -0.3]

    # usuniecie nieuzywanych wierzcholkow, skala, tasowanie
    uzyte = np.unique(f)
    mapa = np.full(len(v), -1, dtype=np.int64)
    mapa[uzyte] = np.arange(len(uzyte))
    v, f = v[uzyte], mapa[f]
    k = float(wspolczynnik)
    T = np.diag([k, k, k, 1.0])
    v = v * k
    perm_v = rng.permutation(len(v))
    odwr = np.empty_like(perm_v)
    odwr[perm_v] = np.arange(len(v))
    v, f = v[perm_v], odwr[f]
    f = f[rng.permutation(len(f))]
    siatka = trimesh.Trimesh(v, f, process=False)

    wpisy = []
    for u in spec:
        c = np.asarray(u["srodek"], dtype=np.float64)
        od_brzegu = float(np.min(np.linalg.norm(krzywa - c, axis=1))) if len(krzywa) else math.inf
        limit = MAX_OD_BRZEGU_MM if u["rodzaj"] == "ukruszenie" else u["srednica_mm"] / 2 + MAX_OD_BRZEGU_MM
        wpisy.append(UbytekPrawda(srodek=[float(x) for x in c], srednica_mm=float(u["srednica_mm"]),
                                  glebokosc_mm=float(u["glebokosc_mm"]), rodzaj=u["rodzaj"],
                                  przy_brzegu=od_brzegu <= limit))
    prawda = PrawdaPracy(
        id=str(m.metadata.get("id", "praca")) if hasattr(m, "metadata") else "praca",
        wspolczynnik=k,
        T_projekt_do_skanu=T,
        zakres_scian=[0, int(len(f))],
        drgniecie=bool(drgniecie),
        pokrycie=float(pokrycie),
        ubytki=wpisy,
    )
    return siatka, prawda
