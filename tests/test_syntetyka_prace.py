"""Testy generatora syntetycznych prac (korony, mosty) i skanow z prawda (qc.syntetyka)."""

import dataclasses
import itertools
import json
import time
from pathlib import Path

import numpy as np
import pytest
import trimesh

from qc.syntetyka import prace, prawda
from qc.syntetyka import skan as modul_skan

KATALOG_DANYCH = Path(__file__).parent / "dane"
KATALOG_WZORCOW = KATALOG_DANYCH / "wzorce"


# --- pomocnicze ---------------------------------------------------------------


def do_ukladu_projektu(siatka, prawda_pracy):
    """Kopia siatki skanu przeniesiona do ukladu projektu (odwrotnosc T_projekt_do_skanu)."""
    T = np.asarray(prawda_pracy.T_projekt_do_skanu, dtype=np.float64)
    kopia = siatka.copy()
    kopia.apply_transform(np.linalg.inv(T))
    return kopia


def rozmiar_xy(siatka):
    return float(np.max(siatka.extents[:2]))


def wymiary_obb_pca(siatka):
    """Posortowane wymiary prostopadloscianu w osiach glownych (PCA, bez scipy)."""
    v = np.asarray(siatka.vertices, dtype=np.float64)
    v = v - v.mean(axis=0)
    _, wektory = np.linalg.eigh(np.cov(v.T))
    rzut = v @ wektory
    return np.sort(rzut.max(axis=0) - rzut.min(axis=0))


def mapa_wysokosci(siatka, krok_mm=1.0):
    """Wysokosc gornej powierzchni na siatce XY (promienie z gory, open3d); NaN = brak trafienia."""
    import open3d as o3d

    scena = o3d.t.geometry.RaycastingScene()
    scena.add_triangles(
        o3d.core.Tensor(np.asarray(siatka.vertices, dtype=np.float32)),
        o3d.core.Tensor(np.asarray(siatka.faces, dtype=np.uint32)),
    )
    (xmin, ymin, zmin), (xmax, ymax, zmax) = siatka.bounds
    xs = np.arange(xmin + krok_mm / 2, xmax, krok_mm)
    ys = np.arange(ymin + krok_mm / 2, ymax, krok_mm)
    gx, gy = np.meshgrid(xs, ys, indexing="ij")
    z0 = zmax + 5.0
    promienie = np.zeros((gx.size, 6), dtype=np.float32)
    promienie[:, 0] = gx.ravel()
    promienie[:, 1] = gy.ravel()
    promienie[:, 2] = z0
    promienie[:, 5] = -1.0
    t = scena.cast_rays(o3d.core.Tensor(promienie))["t_hit"].numpy().astype(np.float64)
    z = np.where(np.isfinite(t), z0 - t, np.nan)
    return z.reshape(gx.shape)


def lokalne_maksima_2d(mapa, prog_z):
    """Liczba komorek wyzszych od wszystkich 8 sasiadow i powyzej prog_z."""
    n = 0
    nx, ny = mapa.shape
    for i in range(1, nx - 1):
        for j in range(1, ny - 1):
            w = mapa[i, j]
            if not np.isfinite(w) or w < prog_z:
                continue
            okno = mapa[i - 1:i + 2, j - 1:j + 2].copy()
            okno[1, 1] = -np.inf
            okno = np.where(np.isfinite(okno), okno, -np.inf)
            if np.all(w > okno):
                n += 1
    return n


def maksima_profilu(profil, prominencja_mm=0.5):
    """Liczba maksimow profilu 1D o prominencji >= prominencja_mm."""
    p = np.asarray(profil, dtype=np.float64)
    n = 0
    for i in range(len(p)):
        lewy = p[i - 1] if i > 0 else -np.inf
        prawy = p[i + 1] if i < len(p) - 1 else -np.inf
        if not (p[i] >= lewy and p[i] > prawy):
            continue
        # minimum po lewej do pierwszego wyzszego punktu
        min_l = p[i]
        for k in range(i - 1, -1, -1):
            if p[k] > p[i]:
                break
            min_l = min(min_l, p[k])
        else:
            min_l = -np.inf
        min_p = p[i]
        for k in range(i + 1, len(p)):
            if p[k] > p[i]:
                break
            min_p = min(min_p, p[k])
        else:
            min_p = -np.inf
        if p[i] - max(min_l, min_p) >= prominencja_mm:
            n += 1
    return n


def profil_wzdluz_osi(siatka, krok_mm=1.0):
    """Maksymalne z w przedzialach wzdluz glownej osi XY (PCA)."""
    v = np.asarray(siatka.vertices, dtype=np.float64)
    xy = v[:, :2] - v[:, :2].mean(axis=0)
    _, wektory = np.linalg.eigh(np.cov(xy.T))
    s = xy @ wektory[:, -1]
    krawedzie = np.arange(s.min(), s.max() + krok_mm, krok_mm)
    indeks = np.digitize(s, krawedzie)
    profil = []
    for i in range(1, len(krawedzie)):
        maska = indeks == i
        if np.any(maska):
            profil.append(v[maska, 2].max())
    return np.array(profil)


def min_odleglosc_do(punkt, punkty):
    return float(np.min(np.linalg.norm(np.asarray(punkty) - np.asarray(punkt), axis=1)))


def normalna_projektu(projekt, punkt):
    """Normalna najblizszej sciany projektu w punkcie (open3d)."""
    import open3d as o3d

    scena = o3d.t.geometry.RaycastingScene()
    scena.add_triangles(
        o3d.core.Tensor(np.asarray(projekt.vertices, dtype=np.float32)),
        o3d.core.Tensor(np.asarray(projekt.faces, dtype=np.uint32)),
    )
    zapytanie = o3d.core.Tensor(np.asarray([punkt], dtype=np.float32))
    sciana = int(scena.compute_closest_points(zapytanie)["primitive_ids"].numpy()[0])
    return np.asarray(projekt.face_normals[sciana], dtype=np.float64)


def odleglosc_boczna(siatka, srodek, normalna, glebokosc_mm):
    """Odleglosc wierzcholkow od srodka w plaszczyznie prostopadlej do normalnej.

    Wierzcholki ze skladowa normalna |w . n| > glebokosc + 0,1 dostaja inf.
    """
    w = np.asarray(siatka.vertices, dtype=np.float64) - np.asarray(srodek, dtype=np.float64)
    wn = w @ normalna
    boczna = np.linalg.norm(w - np.outer(wn, normalna), axis=1)
    return np.where(np.abs(wn) <= glebokosc_mm + 0.1, boczna, np.inf)


def jako_proste(obj):
    """Rekurencyjna zamiana dataclass/numpy na dict/list do porownan."""
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return {f.name: jako_proste(getattr(obj, f.name)) for f in dataclasses.fields(obj)}
    if isinstance(obj, np.ndarray):
        return jako_proste(obj.tolist())
    if isinstance(obj, (list, tuple)):
        return [jako_proste(x) for x in obj]
    if isinstance(obj, dict):
        return {k: jako_proste(w) for k, w in obj.items()}
    if isinstance(obj, np.generic):
        return obj.item()
    return obj


# --- testy --------------------------------------------------------------------


def test_korona_deterministyczna():
    a = prace.korona(7)
    b = prace.korona(7)
    assert a.vertices.shape == b.vertices.shape
    assert np.allclose(a.vertices, b.vertices, atol=1e-9)
    assert np.array_equal(a.faces, b.faces)
    c = prace.korona(8)
    assert abs(a.volume - c.volume) / max(a.volume, c.volume) > 0.02


def test_korona_geometria():
    for z in range(1, 11):
        k = prace.korona(z, krok_mm=0.1)
        assert k.is_watertight, f"ziarno {z}: bryla niezamknieta"
        assert 20.0 <= k.volume <= 400.0, f"ziarno {z}: objetosc {k.volume}"
        assert 5.0 <= k.extents[2] <= 11.0, f"ziarno {z}: wysokosc {k.extents[2]}"
        assert 5.0 <= rozmiar_xy(k) <= 13.0, f"ziarno {z}: rozmiar XY {rozmiar_xy(k)}"
        assert 10_000 <= len(k.faces) <= 300_000, f"ziarno {z}: scian {len(k.faces)}"
        assert abs(k.bounds[0, 2]) < 0.3, f"ziarno {z}: min z {k.bounds[0, 2]}"


def test_rodzaje():
    siekacz = prace.korona(1, "siekacz")
    trzonowiec = prace.korona(1, "trzonowiec")
    assert rozmiar_xy(siekacz) < rozmiar_xy(trzonowiec)
    mapa = mapa_wysokosci(trzonowiec, krok_mm=1.0)
    zmin, zmax = np.nanmin(mapa), np.nanmax(mapa)
    prog = zmin + 0.5 * (zmax - zmin)
    assert lokalne_maksima_2d(mapa, prog) >= 3


def test_pula_roznorodna(pula30):
    assert len(pula30) == 30
    assert len({p.id for p in pula30}) == 30
    assert {p.rodzaj for p in pula30} == {"trzonowiec", "przedtrzonowiec", "siekacz"}
    objetosci = [p.siatka.volume for p in pula30]
    wymiary = [wymiary_obb_pca(p.siatka) for p in pula30]
    pary = list(itertools.combinations(range(30), 2))
    rozne = 0
    for i, j in pary:
        dv = abs(objetosci[i] - objetosci[j]) / max(objetosci[i], objetosci[j])
        dw = float(np.max(np.abs(wymiary[i] - wymiary[j])))
        if dv >= 0.03 or dw >= 0.3:
            rozne += 1
    assert rozne / len(pary) >= 0.90


def test_most():
    pojedyncza = prace.korona(3).volume
    for siatka, punkty in ((prace.most(3, punkty=4), 4), (prace.most(4, punkty=3), 3)):
        dlugosc = float(np.max(siatka.extents[:2]))
        assert 20.0 <= dlugosc <= 45.0, f"punkty {punkty}: dlugosc {dlugosc}"
        assert siatka.extents[2] <= 11.0
        assert siatka.volume > 2 * pojedyncza
    assert maksima_profilu(profil_wzdluz_osi(prace.most(3, punkty=4))) == 4


def test_przepis():
    p = prace.przepis(5, "trzonowiec", 0.1)
    assert isinstance(p, dict)
    p = json.loads(json.dumps(p))  # przepis musi byc serializowalny do JSON
    a = prace.z_przepisu(p)
    b = prace.korona(5, "trzonowiec", 0.1)
    assert a.vertices.shape == b.vertices.shape
    assert np.allclose(a.vertices, b.vertices, atol=1e-9)
    assert np.array_equal(a.faces, b.faces)


def test_skan_szum(projekt_korony, skan, odleglosci):
    s, pp = skan(projekt_korony, szum_mm=0.03)
    d = odleglosci(do_ukladu_projektu(s, pp), projekt_korony)
    rms = float(np.sqrt(np.mean(d ** 2)))
    assert 0.024 <= rms <= 0.036, f"RMS {rms}"
    assert np.percentile(np.abs(d), 95) < 0.08
    assert abs(float(np.mean(d))) < 0.004
    assert len(s.faces) == len(projekt_korony.faces)
    n = min(len(s.vertices), len(projekt_korony.vertices))
    takie_same = np.linalg.norm(s.vertices[:n] - projekt_korony.vertices[:n], axis=1) < 0.1
    assert takie_same.mean() < 0.5, "kolejnosc wierzcholkow skanu nie jest tasowana"


def test_skan_skala(projekt_korony, skan):
    s, pp = skan(projekt_korony, wspolczynnik=1.23, szum_mm=0)
    assert np.allclose(s.extents, 1.23 * projekt_korony.extents, rtol=0.01)
    assert pp.wspolczynnik == 1.23
    T = np.asarray(pp.T_projekt_do_skanu, dtype=np.float64)
    assert T.shape == (4, 4)
    assert np.allclose(np.diag(T), [1.23, 1.23, 1.23, 1.0])


def test_ubytki_prawda(projekt_korony, skan, odleglosci):
    s, pp = skan(projekt_korony, szum_mm=0.02, ubytki=5)
    assert len(pp.ubytki) == 5
    krzywa = modul_skan.brzeg(projekt_korony)
    sp = do_ukladu_projektu(s, pp)
    d = odleglosci(sp, projekt_korony)
    srodki = [np.asarray(u.srodek, dtype=np.float64) for u in pp.ubytki]
    for u, c in zip(pp.ubytki, srodki):
        assert u.rodzaj == "ukruszenie"
        assert 0.2 <= u.srednica_mm <= 0.6
        assert 0.1 <= u.glebokosc_mm <= 0.3
        assert u.przy_brzegu is True
        assert min_odleglosc_do(c, krzywa) <= 0.5
        r = u.srednica_mm / 2
        odl = odleglosc_boczna(sp, c, normalna_projektu(projekt_korony, c), u.glebokosc_mm)
        kula = odl <= 0.5 * r
        assert kula.any(), "brak wierzcholkow skanu w odleglosci bocznej 0,5 r"
        assert np.median(d[kula]) <= -0.8 * u.glebokosc_mm
        pierscien = (odl >= 1.5 * r) & (odl <= 2.5 * r)
        assert pierscien.any()
        assert np.median(d[pierscien]) > -0.03
    for a, b in itertools.combinations(srodki, 2):
        assert np.linalg.norm(a - b) >= 2.0


def test_ubytek_ostry(projekt_korony, skan, odleglosci):
    s, pp = skan(projekt_korony, ubytki=[{"srednica_mm": 0.5, "glebokosc_mm": 0.2}])
    assert len(pp.ubytki) == 1
    u = pp.ubytki[0]
    assert u.srednica_mm == pytest.approx(0.5)
    assert u.glebokosc_mm == pytest.approx(0.2)
    r = 0.25
    sp = do_ukladu_projektu(s, pp)
    d = odleglosci(sp, projekt_korony)
    odl = odleglosc_boczna(sp, u.srodek, normalna_projektu(projekt_korony, u.srodek), u.glebokosc_mm)
    wewnatrz = odl <= 0.6 * r
    assert wewnatrz.any()
    assert -np.median(d[wewnatrz]) >= 0.14
    obok = (odl >= 1.1 * r) & (odl <= 1.3 * r)
    assert obok.any()
    assert abs(np.median(d[obok])) <= 0.03


def test_poprawka_gladka(projekt_korony, skan, odleglosci):
    s, pp = skan(projekt_korony, szum_mm=0.0, poprawki=[{"srednica_mm": 3.0, "glebokosc_mm": 0.12}])
    assert len(pp.ubytki) == 1
    u = pp.ubytki[0]
    assert u.rodzaj == "poprawka"
    sp = do_ukladu_projektu(s, pp)
    d = odleglosci(sp, projekt_korony)
    odl = odleglosc_boczna(sp, u.srodek, normalna_projektu(projekt_korony, u.srodek), u.glebokosc_mm)
    obszar = np.flatnonzero(odl <= 1.5 * 1.5)
    v = np.asarray(sp.vertices)[obszar]
    dd = d[obszar]
    roznice = []
    for i in range(len(v)):
        blisko = np.linalg.norm(v[i + 1:] - v[i], axis=1) <= 0.3
        if blisko.any():
            roznice.append(np.abs(dd[i + 1:][blisko] - dd[i]).max())
    assert roznice
    assert np.percentile(roznice, 99) <= 0.03
    srodek = odl <= 0.2
    assert srodek.any()
    assert -np.median(d[srodek]) >= 0.08


def test_drgniecie(projekt_korony, skan, odleglosci):
    s, pp = skan(projekt_korony, szum_mm=0.02, drgniecie=True)
    ratio = len(s.faces) / len(projekt_korony.faces)
    assert 1.3 <= ratio <= 1.6, f"scian x{ratio}"
    d = np.abs(odleglosci(do_ukladu_projektu(s, pp), projekt_korony))
    assert np.mean((d >= 0.05) & (d <= 0.14)) >= 0.15
    assert pp.drgniecie is True
    s0, pp0 = skan(projekt_korony, szum_mm=0.02)
    d0 = np.abs(odleglosci(do_ukladu_projektu(s0, pp0), projekt_korony))
    assert np.mean((d0 >= 0.05) & (d0 <= 0.14)) < 0.02
    assert pp0.drgniecie is False


def test_pokrycie(projekt_korony, skan):
    k = 1.22
    s, pp = skan(projekt_korony, wspolczynnik=k, pokrycie=0.7, szum_mm=0)
    udzial = s.area / (projekt_korony.area * k ** 2)
    assert 0.6 <= udzial <= 0.8, f"udzial pola {udzial}"
    assert pp.pokrycie == 0.7


def test_widocznosc_z_gory(projekt_korony, skan):
    pelny, _ = skan(projekt_korony)
    s, _ = skan(projekt_korony, widocznosc="z_gory")
    assert len(s.faces) > 0
    assert np.all(s.face_normals[:, 2] >= -0.3)
    udzial = s.area / pelny.area
    assert 0.4 <= udzial <= 0.9, f"udzial pola {udzial}"


def test_ubytki_na_moscie(projekt_mostu, skan):
    s, pp = skan(projekt_mostu, ubytki=3)
    assert len(pp.ubytki) == 3
    krzywa = modul_skan.brzeg(projekt_mostu)
    for u in pp.ubytki:
        assert min_odleglosc_do(u.srodek, krzywa) <= 0.5


@pytest.mark.parametrize("nazwa", ["korona-wzorzec", "most-wzorzec"])
def test_wzorce_zgodne(nazwa):
    plik_json = KATALOG_WZORCOW / f"{nazwa}.json"
    plik_stl = KATALOG_WZORCOW / f"{nazwa}.stl"
    assert plik_json.is_file(), f"brak {plik_json}"
    assert plik_stl.is_file(), f"brak {plik_stl}"
    assert plik_stl.stat().st_size <= 300 * 1024
    opis = json.loads(plik_json.read_text(encoding="utf-8"))
    # zmiana losowania parametrow generatora = inny przepis niz zapisany we wzorcu
    oczekiwany = {
        "korona-wzorzec": lambda: prace.przepis(1, "trzonowiec", 0.8),
        "most-wzorzec": lambda: prace.przepis_mostu(1, 3, 1.0),
    }[nazwa]()
    assert opis["przepis"] == json.loads(json.dumps(oczekiwany))
    wygenerowana = prace.z_przepisu(opis["przepis"])
    wzorzec = trimesh.load(plik_stl, process=False, force="mesh")
    assert len(wygenerowana.faces) == len(wzorzec.faces)
    assert np.allclose(wygenerowana.triangles, wzorzec.triangles, atol=1e-5)


def test_rozmiar_danych():
    assert KATALOG_DANYCH.is_dir()
    pliki = [p for p in KATALOG_DANYCH.rglob("*") if p.is_file()]
    assert pliki
    suma = 0
    for p in pliki:
        assert p.suffix.lower() in {".stl", ".json", ".md"}, f"niedozwolony plik {p}"
        rozmiar = p.stat().st_size
        assert rozmiar <= 300 * 1024, f"za duzy plik {p}"
        suma += rozmiar
    assert suma <= 1024 * 1024


def test_prawda_json_roundtrip(projekt_korony, skan, tmp_path):
    _, pp = skan(projekt_korony, wspolczynnik=1.21, ubytki=2, poprawki=1)
    calosc = prawda.Prawda(
        wersja=1, ziarno=42, szum_mm=0.02, gestosc_mm=0.1, plytka=None, prace=[pp]
    )
    sciezka = tmp_path / "prawda.json"
    calosc.do_json(sciezka)
    surowe = json.loads(sciezka.read_text(encoding="utf-8"))
    assert surowe["wersja"] == 1
    T = surowe["prace"][0]["T_projekt_do_skanu"]
    assert isinstance(T, list) and len(T) == 4
    assert all(isinstance(w, list) and len(w) == 4 for w in T)
    assert isinstance(surowe["prace"][0]["ubytki"][0]["srodek"], list)
    wczytana = prawda.Prawda.z_json(sciezka)
    assert isinstance(wczytana, prawda.Prawda)
    assert isinstance(wczytana.prace[0], prawda.PrawdaPracy)
    assert isinstance(wczytana.prace[0].ubytki[0], prawda.UbytekPrawda)
    assert jako_proste(wczytana) == jako_proste(calosc)


def test_czas_generacji(skan):
    t0 = time.perf_counter()
    k = prace.korona(1)
    czas_korony = time.perf_counter() - t0
    assert czas_korony <= 2.0, f"korona {czas_korony:.2f} s"
    t0 = time.perf_counter()
    skan(k, ubytki=5)
    czas_skanu = time.perf_counter() - t0
    assert czas_skanu <= 3.0, f"skan {czas_skanu:.2f} s"
