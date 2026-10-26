"""Proceduralne projekty prac: korony i mosty z cyrkonii (dane syntetyczne, bez prawdziwych STL).

Uklad projektu: brzeg w plaszczyznie z ~ 0, powierzchnia zujaca w gore, os wprowadzenia = Z, mm.

Korona = powierzchnia obrotowa z profilu (r, z) 60 wezlow (brzeg -> ekwator -> bark -> powierzchnia
zujaca), z owalnoscia r *= 1 + e*cos(2 theta) i guzkami z += b*w(r)*(1 + cos(n_g*(theta - fi)))/2 (guzki nierowne o +-20 %).
Wnetrze = profil bazowy przesuniety o grubosc sciany do srodka (odwrocone normalne), polaczone pasem
trojkatow na brzegu. Bryla zamknieta, bez operacji boolowskich.

Odtworzenie danych w tests/dane (z katalogu repo):

    python -c "from qc.syntetyka import prace; prace.zapisz_dane_testowe('tests/dane')"
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import trimesh

RODZAJE = ("trzonowiec", "przedtrzonowiec", "siekacz")

# zakresy parametrow wg rodzaju: srednica (max wymiar XY), wysokosc, owalnosc, liczba guzkow,
# amplituda guzkow, glebokosc dolka, grubosc sciany
ZAKRESY = {
    "trzonowiec": dict(srednica=(9.5, 12.5), wysokosc=(6.5, 8.5), owalnosc=(0.0, 0.10),
                       guzki=(4, 5), amplituda=(0.6, 1.0), dolek=(0.5, 0.9), sciana=(0.8, 1.3)),
    "przedtrzonowiec": dict(srednica=(7.0, 9.0), wysokosc=(7.0, 9.0), owalnosc=(0.03, 0.12),
                            guzki=(2, 3), amplituda=(0.4, 0.8), dolek=(0.4, 0.7), sciana=(0.7, 1.2)),
    "siekacz": dict(srednica=(5.5, 7.5), wysokosc=(8.0, 10.0), owalnosc=(0.08, 0.15),
                    guzki=(2, 2), amplituda=(0.3, 0.5), dolek=(0.2, 0.4), sciana=(0.6, 1.0)),
}

WEZLY_BRZEG = 15
WEZLY_BARK = 25
WEZLY_ZUJACA = 20


@dataclass
class Projekt:
    id: str
    rodzaj: str
    siatka: trimesh.Trimesh
    parametry: dict = field(default_factory=dict)


# --- parametry ----------------------------------------------------------------


def _losuj_parametry(rng: np.random.Generator, rodzaj: str, srednica=None, wysokosc=None) -> dict:
    z = ZAKRESY[rodzaj]
    p = {
        "rodzaj": rodzaj,
        "srednica": float(rng.uniform(*z["srednica"])),
        "wysokosc": float(rng.uniform(*z["wysokosc"])),
        "owalnosc": float(rng.uniform(*z["owalnosc"])),
        "guzki": int(rng.integers(z["guzki"][0], z["guzki"][1] + 1)),
        "amplituda": float(rng.uniform(*z["amplituda"])),
        "dolek": float(rng.uniform(*z["dolek"])),
        "sciana": float(rng.uniform(*z["sciana"])),
        "faza": float(rng.uniform(0.0, 2 * math.pi)),
        "faza_nierownosci": float(rng.uniform(0.0, 2 * math.pi)),
    }
    if srednica is not None:
        p["srednica"] = float(srednica)
    if wysokosc is not None:
        p["wysokosc"] = float(wysokosc)
    return p


def _rodzaj_z_ziarna(ziarno: int, rodzaj: str | None) -> tuple[np.random.Generator, str]:
    rng = np.random.default_rng(ziarno)
    wylosowany = RODZAJE[int(rng.integers(0, len(RODZAJE)))]
    if rodzaj is None:
        rodzaj = wylosowany
    if rodzaj not in RODZAJE:
        raise ValueError(f"nieznany rodzaj korony: {rodzaj}")
    return rng, rodzaj


# --- profil -------------------------------------------------------------------


def _wymiary(p: dict) -> dict:
    """Wielkosci pochodne profilu: promien brzegu, ekwatora, barku i wysokosci."""
    e = p["owalnosc"]
    R = p["srednica"] / (2 * 1.08 * (1 + e))
    Re = 1.08 * R
    h = p["wysokosc"]
    b, f, t = p["amplituda"], p["dolek"], p["sciana"]
    zs = h - max(0.0, b - f / 2)
    ze = 0.35 * h
    bz = zs - ze
    a = max(0.45 * R, math.sqrt(1.6 * t * bz))
    Rs = max(Re - a, 0.25 * R)
    return dict(R=R, Re=Re, Rs=Rs, ze=ze, zs=zs)


def profil(p: dict) -> np.ndarray:
    """Profil bazowy (r, z) korony, 60 wezlow od brzegu (r=R, z=0) do osi (r=0)."""
    w = _wymiary(p)
    R, Re, Rs, ze, zs, f = w["R"], w["Re"], w["Rs"], w["ze"], w["zs"], p["dolek"]
    u = np.linspace(0.0, 1.0, WEZLY_BRZEG, endpoint=False)
    s1 = np.column_stack([R + (Re - R) * np.sin(0.5 * math.pi * u), ze * u])
    fi = np.linspace(0.0, 0.5 * math.pi, WEZLY_BARK, endpoint=False)
    s2 = np.column_stack([Rs + (Re - Rs) * np.cos(fi), ze + (zs - ze) * np.sin(fi)])
    v = np.linspace(0.0, 1.0, WEZLY_ZUJACA)
    s3 = np.column_stack([Rs * (1 - v), zs - f * (1 - np.cos(math.pi * v)) / 2])
    return np.vstack([s1, s2, s3])


def _przeprobkuj(wezly: np.ndarray, krok_mm: float) -> np.ndarray:
    dl = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(wezly, axis=0), axis=1))]
    n = max(int(math.ceil(dl[-1] / krok_mm)), 8)
    s = np.linspace(0.0, dl[-1], n + 1)
    return np.column_stack([np.interp(s, dl, wezly[:, 0]), np.interp(s, dl, wezly[:, 1])])


def _odsuniecie_do_srodka(rz: np.ndarray, t: float) -> np.ndarray:
    """Profil przesuniety o t wzdluz normalnej do srodka bryly."""
    dr = np.gradient(rz[:, 0])
    dz = np.gradient(rz[:, 1])
    n = np.column_stack([dz, -dr])
    n /= np.linalg.norm(n, axis=1, keepdims=True)
    wew = rz - t * n
    wew[:, 0] = np.maximum(wew[:, 0], 0.0)
    wew[:, 1] = np.maximum(wew[:, 1], 0.0)
    wew[0, 1] = 0.0
    wew[-1, 0] = 0.0
    return wew


def _pierscienie(rz, theta, p, guzki: bool):
    """Wierzcholki pierscieni (bez ostatniego wezla = biegun) i biegun."""
    e = p["owalnosc"]
    skala = 1 + e * np.cos(2 * theta)
    r = rz[:-1, 0:1] * skala[None, :]
    z = np.repeat(rz[:-1, 1:2], len(theta), axis=1)
    if guzki:
        Rs = _wymiary(p)["Rs"]
        q = np.clip(rz[:-1, 0] / Rs, 0.0, 1.0)
        waga = np.where(rz[:-1, 0] < Rs, np.sin(math.pi * q) ** 2, 0.0)
        # guzki nierownej wysokosci (+-20 %), jak w naturalnych zebach
        mod = (1 + np.cos(p["guzki"] * (theta - p["faza"]))) / 2
        mod = mod * (1 + 0.2 * np.cos(theta - p["faza_nierownosci"]))
        z = z + p["amplituda"] * waga[:, None] * mod[None, :]
    v = np.stack([r * np.cos(theta)[None, :], r * np.sin(theta)[None, :], z], axis=-1).reshape(-1, 3)
    biegun = np.array([[0.0, 0.0, rz[-1, 1]]])
    return np.vstack([v, biegun])


def _sciany_powloki(n_wierszy: int, n_theta: int, przesuniecie: int, odwroc: bool) -> np.ndarray:
    i = np.arange(n_theta)
    i1 = (i + 1) % n_theta
    sciany = []
    for j in range(n_wierszy - 1):
        a = j * n_theta + i
        b = j * n_theta + i1
        c = (j + 1) * n_theta + i
        d = (j + 1) * n_theta + i1
        sciany.append(np.column_stack([a, b, c]))
        sciany.append(np.column_stack([b, d, c]))
    biegun = n_wierszy * n_theta
    j = n_wierszy - 1
    sciany.append(np.column_stack([j * n_theta + i, j * n_theta + i1, np.full(n_theta, biegun)]))
    f = np.vstack(sciany) + przesuniecie
    if odwroc:
        f = f[:, ::-1]
    return f


def _siatka_korony(p: dict, krok_mm: float) -> trimesh.Trimesh:
    zew_rz = _przeprobkuj(profil(p), krok_mm)
    wew_rz = _odsuniecie_do_srodka(zew_rz, p["sciana"])
    n_theta = max(int(math.ceil(math.pi * p["srednica"] / krok_mm)), 24)
    theta = np.linspace(0.0, 2 * math.pi, n_theta, endpoint=False)
    vz = _pierscienie(zew_rz, theta, p, guzki=True)
    vw = _pierscienie(wew_rz, theta, p, guzki=False)
    n_wierszy = len(zew_rz) - 1
    fz = _sciany_powloki(n_wierszy, n_theta, 0, odwroc=False)
    fw = _sciany_powloki(n_wierszy, n_theta, len(vz), odwroc=True)
    i = np.arange(n_theta)
    i1 = (i + 1) % n_theta
    oz, ow = i, len(vz) + i
    oz1, ow1 = i1, len(vz) + i1
    fb = np.vstack([np.column_stack([oz, ow, oz1]), np.column_stack([oz1, ow, ow1])])
    return trimesh.Trimesh(np.vstack([vz, vw]), np.vstack([fz, fw, fb]), process=False)


# --- przepisy -----------------------------------------------------------------


def przepis(ziarno: int, rodzaj: str | None = None, krok_mm: float = 0.1) -> dict:
    """Przepis korony: komplet parametrow do odtworzenia siatki (bez geometrii)."""
    rng, rodzaj = _rodzaj_z_ziarna(ziarno, rodzaj)
    return {
        "typ": "korona",
        "ziarno": int(ziarno),
        "rodzaj": rodzaj,
        "krok_mm": float(krok_mm),
        "parametry": _losuj_parametry(rng, rodzaj),
    }


def przepis_mostu(ziarno: int, punkty: int = 4, krok_mm: float = 0.1) -> dict:
    """Przepis mostu: 3 lub 4 korony w szeregu wzdluz X z lacznikami walcowymi."""
    if punkty not in (3, 4):
        raise ValueError("most ma 3 albo 4 punkty")
    rng = np.random.default_rng(ziarno)
    zakres_sr = (7.0, 9.0) if punkty == 4 else (8.0, 10.5)
    wys = float(rng.uniform(6.5, 8.5))
    korony = []
    for _ in range(punkty):
        rodzaj = RODZAJE[int(rng.integers(0, 2))]
        p = _losuj_parametry(rng, rodzaj, srednica=rng.uniform(*zakres_sr),
                             wysokosc=wys + rng.uniform(-0.5, 0.5))
        p["amplituda"] = min(p["amplituda"], 0.45)
        korony.append(p)
    laczniki = [float(rng.uniform(3.0, 4.0)) for _ in range(punkty - 1)]
    return {
        "typ": "most",
        "ziarno": int(ziarno),
        "rodzaj": "most",
        "punkty": int(punkty),
        "krok_mm": float(krok_mm),
        "korony": korony,
        "laczniki": laczniki,
    }


def _promien_na_wysokosci(p: dict, z: float) -> float:
    """Promien zewnetrzny korony wzdluz +X na wysokosci z (czesc boczna profilu)."""
    rz = profil(p)[: WEZLY_BRZEG + WEZLY_BARK]
    return float(np.interp(z, rz[:, 1], rz[:, 0]) * (1 + p["owalnosc"]))


def _siatka_mostu(prz: dict) -> trimesh.Trimesh:
    krok = prz["krok_mm"]
    korony = prz["korony"]
    srodki = [0.0]
    for a, b in zip(korony[:-1], korony[1:]):
        srodki.append(srodki[-1] + (a["srednica"] + b["srednica"]) / 2 + 2.0)
    przes = (srodki[0] + srodki[-1]) / 2
    srodki = [x - przes for x in srodki]
    czesci = []
    for x, p in zip(srodki, korony):
        k = _siatka_korony(p, krok)
        k.apply_translation([x, 0.0, 0.0])
        czesci.append(k)
    z_l = 0.45 * min(p["wysokosc"] for p in korony)
    for i, d in enumerate(prz["laczniki"]):
        a, b = korony[i], korony[i + 1]
        x0 = srodki[i] + _promien_na_wysokosci(a, z_l) - a["sciana"] / 2
        x1 = srodki[i + 1] - _promien_na_wysokosci(b, z_l) + b["sciana"] / 2
        sekcje = max(int(math.ceil(math.pi * d / krok)), 16)
        walec = trimesh.creation.cylinder(radius=d / 2, sections=sekcje,
                                          segment=[[x0, 0.0, z_l], [x1, 0.0, z_l]])
        czesci.append(walec)
    v, f, n = [], [], 0
    for c in czesci:
        v.append(np.asarray(c.vertices, dtype=np.float64))
        f.append(np.asarray(c.faces, dtype=np.int64) + n)
        n += len(c.vertices)
    return trimesh.Trimesh(np.vstack(v), np.vstack(f), process=False)


def z_przepisu(prz: dict) -> trimesh.Trimesh:
    """Siatka z przepisu korony albo mostu."""
    if prz.get("typ", "korona") == "most":
        m = _siatka_mostu(prz)
        m.metadata["id"] = f"most-{int(prz['ziarno']):02d}"
    else:
        m = _siatka_korony(prz["parametry"], float(prz["krok_mm"]))
        m.metadata["id"] = f"korona-{int(prz['ziarno']):02d}"
    m.metadata["przepis"] = prz
    return m


# --- funkcje publiczne --------------------------------------------------------


def korona(ziarno: int, rodzaj: str | None = None, krok_mm: float = 0.1) -> trimesh.Trimesh:
    """Zamknieta bryla korony; rodzaj None = losowy z ziarna."""
    return z_przepisu(przepis(ziarno, rodzaj, krok_mm))


def most(ziarno: int, punkty: int = 4, krok_mm: float = 0.1) -> trimesh.Trimesh:
    """Most 3- lub 4-punktowy (konkatenacja koron i lacznikow, bez boolean)."""
    return z_przepisu(przepis_mostu(ziarno, punkty, krok_mm))


def przepisy_puli(n: int = 30, ziarno: int = 1, krok_mm: float = 0.1) -> list[dict]:
    """Lista przepisow puli (ziarno, rodzaj kolejno z RODZAJE)."""
    wynik = []
    for i in range(n):
        prz = przepis(ziarno * 1000 + i, RODZAJE[i % len(RODZAJE)], krok_mm)
        prz["id"] = f"korona-{i + 1:02d}"
        wynik.append(prz)
    return wynik


def pula_projektow(n: int = 30, ziarno: int = 1, krok_mm: float = 0.1) -> list[Projekt]:
    """Pula n roznych projektow koron (3 rodzaje)."""
    pula = []
    for prz in przepisy_puli(n, ziarno, krok_mm):
        siatka = z_przepisu(prz)
        siatka.metadata["id"] = prz["id"]
        pula.append(Projekt(id=prz["id"], rodzaj=prz["rodzaj"], siatka=siatka,
                            parametry=dict(prz["parametry"])))
    return pula


def zapisz_dane_testowe(katalog, krok_korony: float = 0.8, krok_mostu: float = 1.0) -> None:
    """Zapisuje wzorce regresyjne (STL + JSON) i przepisy puli do katalogu tests/dane."""
    katalog = Path(katalog)
    (katalog / "wzorce").mkdir(parents=True, exist_ok=True)
    (katalog / "przepisy").mkdir(parents=True, exist_ok=True)
    wzorce = {
        "korona-wzorzec": przepis(1, "trzonowiec", krok_korony),
        "most-wzorzec": przepis_mostu(1, 3, krok_mostu),
    }
    for nazwa, prz in wzorce.items():
        opis = {"przepis": prz, "uwaga": "gruby krok tylko do regresji"}
        (katalog / "wzorce" / f"{nazwa}.json").write_text(json.dumps(opis, indent=1), encoding="utf-8")
        z_przepisu(prz).export(katalog / "wzorce" / f"{nazwa}.stl", file_type="stl")
    pula = [{"id": p["id"], "ziarno": p["ziarno"], "rodzaj": p["rodzaj"], "krok_mm": p["krok_mm"]}
            for p in przepisy_puli(30, 1)]
    (katalog / "przepisy" / "pula30.json").write_text(json.dumps(pula, indent=1), encoding="utf-8")
