# -*- coding: utf-8 -*-
"""
Skrypt RECENZENTA R59 (iteracja 1) - pomiar JEDNEGO pliku plytki z siatki STL (Blender -b, bpy + BVH + numpy).
Napisany bez czytania ramka_generator.py. Wartosci oczekiwane: wylacznie parametry.json (modul sprawdz_R59_wspolne).
Zakres (plan sesji R59 sekcja 8, pkt 1-5): K-01...K-04b, spis petli krawedzi na plaszczyznach (wierzch, dna gniazd,
spod, dna dolkow, stropy kieszeni), pomiar promieniowy kazdego gniazda / rynienki / stozka / dolka, scianki z promieni,
sondy protokolu K-06...K-16, K-61...K-63, mapa wierzchu i spodu (siatka promieni) wzgledem modelu oczekiwanego,
kontrola odwrotna starego ukladu (model ze starych parametrow + roznica map ze starym STL + sondy punktowe).
Uruchomienie (jeden plik):
  blender.exe -b -P sprawdz_R59.py -- --plik ramka_plytka_wieczorna_n1_v2 --stl <kat> --stare <kat> --par <json>
      --par-stare <json> --wyn <kat> [--krok 0.1]
Wynik: <wyn>/wynik_<plik>.json, <wyn>/mapa_<plik>.png, <wyn>/cyfra_<plik>.png
"""
import bpy
import bmesh
import json
import math
import os
import struct
import sys
import time
import zlib

import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprawdz_R59_wspolne as W

T0 = time.time()
ARG = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def arg(name, default=None):
    return ARG[ARG.index(name) + 1] if name in ARG else default


PLIK = arg("--plik")
KAT_STL = arg("--stl")
KAT_STARE = arg("--stare")
PAR = W.wczytaj(arg("--par"))
PAR_STARE = W.wczytaj(arg("--par-stare"))
KAT_WYN = arg("--wyn")
KROK = float(arg("--krok", "0.1"))

TYP = "wieczorna" if "wieczorna" in PLIK else "poranna"
KSZTALT = "okragla" if "okragla" in PLIK else "kwadrat"
NUMER = 0
for cz in PLIK.split("_"):
    if len(cz) >= 2 and cz[0] == "n" and cz[1:].isdigit():
        NUMER = int(cz[1:])
M = W.Model(PAR, TYP, KSZTALT)
MS = W.Model(PAR_STARE, TYP, KSZTALT)
BITY = W.bity_numeru(NUMER) if NUMER else "ABCD"
assert NUMER == 0 or NUMER in M.numery, "numer %d nie nalezy do typu %s (%s)" % (NUMER, TYP, M.numery)
HB = M.bok / 2.0
GR = M.gr
TOL = 0.06          # pas tolerancji wokol obrysow na mapach [mm]

RES = []
LICZ = {"sondy_punktowe": 0, "promienie_pomiarowe": 0, "promienie_mapy": 0}


def log(*a):
    print("[%7.1fs]" % (time.time() - T0), *a)
    sys.stdout.flush()


def rec(kid, ok, wartosc, oczek, waga, n=0, uwaga=""):
    RES.append({"id": kid, "wynik": "ZAL" if ok else "NIE", "wartosc": wartosc, "oczekiwane": oczek, "waga": waga,
                "n": n, "uwaga": uwaga})
    log("[%s] %s: %s | oczek: %s %s" % ("ZAL" if ok else "NIE", kid, wartosc, oczek, uwaga))


def sondy_wynik(kid, lst, waga, oczek="wszystkie zgodne", uwaga=""):
    zle = [e for e in lst if not e["ok"]]
    rec(kid, not zle, "%d/%d sond zgodnych" % (len(lst) - len(zle), len(lst)), oczek, waga, len(lst),
        uwaga + (" NIEZGODNE: " + json.dumps(zle[:6])) if zle else uwaga)


def zapisz_png(path, img):
    img = np.ascontiguousarray(img, dtype=np.uint8)
    h, w = img.shape[:2]
    ct = 0 if img.ndim == 2 else 2
    raw = b"".join(b"\x00" + img[j].tobytes() for j in range(h))

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, ct, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)


# ---------- import i bryla ----------
def importuj(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.stl_import(filepath=path)
    objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    assert len(objs) == 1, "import dal %d obiektow" % len(objs)
    return objs[0]


class Bryla(object):
    """siatka po spawaniu wierzcholkow, w ukladzie montazowym plytki (wierzch z = 0, srodek XY = 0)"""

    def __init__(self, path, spawaj=1e-5):
        obj = importuj(path)
        me = obj.data
        self.n_tr_surowe = len(me.polygons)
        co = np.zeros(len(me.vertices) * 3)
        me.vertices.foreach_get("co", co)
        co = co.reshape(-1, 3)
        self.nan = int(np.isnan(co).sum())
        self.bb_surowy = (co.min(axis=0).tolist(), co.max(axis=0).tolist())
        bm = bmesh.new()
        bm.from_mesh(me)
        n0 = len(bm.verts)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=spawaj)
        self.spawane = n0 - len(bm.verts)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        cx = (self.bb_surowy[0][0] + self.bb_surowy[1][0]) / 2.0
        cy = (self.bb_surowy[0][1] + self.bb_surowy[1][1]) / 2.0
        self.przes = Vector((-cx, -cy, -GR))     # tabela 1 protokolu: Z - 8, srodek XY na 0
        for v in bm.verts:
            v.co = v.co + self.przes
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        bm.verts.index_update()
        bm.faces.index_update()
        bm.normal_update()
        self.bm = bm
        self.V = np.array([v.co[:] for v in bm.verts])
        self.F = np.array([[v.index for v in f.verts] for f in bm.faces], dtype=np.int64)
        self.bvh = BVHTree.FromPolygons([Vector(p) for p in self.V], [tuple(int(i) for i in t) for t in self.F],
                                        all_triangles=True, epsilon=0.0)
        self.bb = (self.V.min(axis=0), self.V.max(axis=0))
        self.kier = [Vector((1.0, 0.00071, 0.00137)).normalized(), Vector((0.00083, 1.0, 0.00119)).normalized(),
                     Vector((0.00097, 0.00061, 1.0)).normalized()]
        self.zasieg = 400.0

    # --- sondy ---
    def _licz(self, p, d):
        n = 0
        o = Vector(p)
        ost = None
        for _ in range(2000):
            h = self.bvh.ray_cast(o, d, self.zasieg)
            if h[0] is None:
                break
            if ost is None or (h[0] - ost).length > 1e-5:
                n += 1
            ost = h[0]
            o = h[0] + d * 1e-4
        return n

    def w_bryle3(self, p):
        return [self._licz(p, d) % 2 == 1 for d in self.kier]

    def sonda(self, p, oczek_w, opis=""):
        """sonda punktowa: parzystosc przeciec w 3 kierunkach; kierunki niezgodne = przesuniecie 0,1 mm i powtorka"""
        LICZ["sondy_punktowe"] += 1
        r = self.w_bryle3(p)
        e = {"p": [round(float(c), 4) for c in p], "oczek": "W" if oczek_w else "POZA", "opis": opis}
        if r.count(True) in (0, 3):
            e["wynik"] = "W" if r[0] else "POZA"
        else:
            loc, nrm, idx, dist = self.bvh.find_nearest(Vector(p))
            if nrm is None or nrm.length == 0:
                nrm = Vector((0, 0, 1))
            p2 = Vector(p) + (-nrm if oczek_w else nrm) * 0.1
            r2 = self.w_bryle3(p2)
            e["niestabilna"] = ["W" if x else "P" for x in r]
            e["p_przes"] = [round(c, 4) for c in p2]
            e["wynik"] = ("W" if r2[0] else "POZA") if r2.count(True) in (0, 3) else "NIESTABILNA"
        e["ok"] = e["wynik"] == e["oczek"]
        return e

    def promien(self, o, d, maxd=300.0):
        LICZ["promienie_pomiarowe"] += 1
        h = self.bvh.ray_cast(Vector(o), Vector(d).normalized(), maxd)
        return None if h[0] is None else (h[0], h[3])

    def promienie_poziome(self, cx, cy, z, n=24, faza=0.0):
        """odleglosci trafien promieni poziomych z osi (cx, cy, z) w n kierunkach"""
        out = []
        for i in range(n):
            a = faza + 2 * math.pi * i / n
            h = self.promien((cx, cy, z), (math.cos(a), math.sin(a), 0.0))
            out.append(None if h is None else h[1])
        return out

    def z_gora(self, x, y):
        h = self.promien((x, y, 20.0), (0, 0, -1))
        return None if h is None else h[0].z

    def z_dol(self, x, y):
        h = self.promien((x, y, -30.0), (0, 0, 1))
        return None if h is None else h[0].z

    def mapa(self, xs, ys, z_start, dz):
        """siatka promieni pionowych; zwraca tablice z pierwszego trafienia (NaN = brak)"""
        Z = np.full((len(ys), len(xs)), np.nan)
        d = Vector((0, 0, dz))
        rc = self.bvh.ray_cast
        for j, y in enumerate(ys):
            row = Z[j]
            for i, x in enumerate(xs):
                h = rc(Vector((x, y, z_start)), d, 100.0)
                if h[0] is not None:
                    row[i] = h[0].z
        LICZ["promienie_mapy"] += len(xs) * len(ys)
        return Z


# deklaracje wykonawcy (R59_wdrozenie_zmiany.md pkt 0) - tylko do porownania PO pomiarze; orient. z tabeli 1 protokolu
DEKL_OBJ = {
    "ramka_plytka_wieczorna_v2": 59.64, "ramka_plytka_wieczorna_n1_v2": 59.66, "ramka_plytka_wieczorna_n2_v2": 59.66,
    "ramka_plytka_wieczorna_n3_v2": 59.66, "ramka_plytka_poranna_v2": 59.93, "ramka_plytka_poranna_n4_v2": 59.95,
    "ramka_plytka_poranna_n5_v2": 59.95, "ramka_plytka_poranna_n6_v2": 59.94,
    "ramka_plytka_okragla_wieczorna_v2": 49.34, "ramka_plytka_okragla_wieczorna_n8_v2": 49.36,
    "ramka_plytka_okragla_poranna_v2": 49.63, "ramka_plytka_okragla_poranna_n9_v2": 49.64,
}
OBJ_ORIENT = {("kwadrat", "wieczorna"): 60.0, ("kwadrat", "poranna"): 60.0, ("okragla", "wieczorna"): 49.0,
              ("okragla", "poranna"): 50.0}


def objetosc(b):
    v0 = b.V[b.F[:, 0]]
    v1 = b.V[b.F[:, 1]]
    v2 = b.V[b.F[:, 2]]
    return float(np.einsum("ij,ij->i", v0, np.cross(v1, v2)).sum() / 6.0)


def skladowe(b):
    n = len(b.V)
    rodzic = list(range(n))

    def znajdz(a):
        while rodzic[a] != a:
            rodzic[a] = rodzic[rodzic[a]]
            a = rodzic[a]
        return a
    for e in b.bm.edges:
        a = znajdz(e.verts[0].index)
        c = znajdz(e.verts[1].index)
        if a != c:
            rodzic[a] = c
    return len(set(znajdz(i) for i in range(n)))


def ogolne(b):
    rec("K-01", b.n_tr_surowe > 100 and b.nan == 0, "trojkatow %d, NaN %d, spawanych wierzcholkow %d" % (
        b.n_tr_surowe, b.nan, b.spawane), "> 100 trojkatow, 0 NaN", "B")
    lo, hi = b.bb
    wym = (hi - lo).tolist()
    exy = 2 * M.R if KSZTALT == "okragla" else M.bok
    ez = GR + (M.relief_h if NUMER else 0.0)
    sr = b.bb_surowy
    ok = abs(wym[0] - exy) <= 0.1 and abs(wym[1] - exy) <= 0.1 and abs(wym[2] - ez) <= 0.1
    ok = ok and abs(sr[0][2]) <= 0.01 and abs(b.przes.x) <= 0.01 and abs(b.przes.y) <= 0.01
    rec("K-02", ok, "gabaryt %.4f x %.4f x %.4f; surowy STL: z_min %.4f, srodek XY (%.5f; %.5f); po transformacji z %.4f...%.4f" % (
        wym[0], wym[1], wym[2], sr[0][2], -b.przes.x, -b.przes.y, lo[2], hi[2]),
        "%g x %g x %g +-0,1; spod STL na z = 0; srodek XY = 0" % (exy, exy, ez), "B")
    bm = b.bm
    zle = sum(1 for e in bm.edges if len(e.link_faces) != 2)
    luzne = sum(1 for v in bm.verts if not v.link_faces)
    nieciagle = sum(1 for e in bm.edges if len(e.link_faces) == 2 and not e.is_contiguous)
    zdeg = sum(1 for f in bm.faces if f.calc_area() < 1e-12)
    F = b.F
    nprz = 0
    przyk = []
    for i, j in b.bvh.overlap(b.bvh):
        if i >= j:
            continue
        if F[i][0] in F[j] or F[i][1] in F[j] or F[i][2] in F[j]:
            continue
        nprz += 1
        if len(przyk) < 3:
            przyk.append(b.V[F[i]].mean(axis=0).round(3).tolist())
    rec("K-03", zle == 0 and luzne == 0 and nprz == 0 and nieciagle == 0,
        "krawedzie z liczba scian != 2: %d; luzne wierzcholki: %d; przeciecia wlasne (bez sasiadow): %d; krawedzie o niezgodnym"
        " zwrocie scian: %d; trojkaty zdegenerowane: %d %s" % (zle, luzne, nprz, nieciagle, zdeg, przyk if przyk else ""),
        "0 / 0 / 0 / 0", "B")
    ns = skladowe(b)
    rec("K-04", ns == 1, "skladowych spojnych: %d" % ns, "1", "B")
    vol = objetosc(b) / 1000.0
    eo = OBJ_ORIENT[(KSZTALT, TYP)]
    dk = DEKL_OBJ.get(PLIK)
    rec("K-04b", vol > 0 and abs(vol - eo) <= 0.3 * eo, "objetosc %.4f cm3 (dodatnia = normalne na zewnatrz)" % vol,
        "%g +-30 %% (tabela 1 protokolu)" % eo, "B")
    rec("K-04b/dekl", dk is not None and abs(vol - dk) <= 0.01, "objetosc z siatki %.4f cm3; deklaracja wykonawcy %s" % (vol, dk),
        "roznica <= 0,01 cm3", "P")
    return vol


# ---------- spis petli krawedzi na plaszczyznie ----------
def petle(b, z0, tol=2e-4):
    """Petle krawedzi lezacych na plaszczyznie z0, przy ktorych dokladnie jedna sciana lezy w tej plaszczyznie
    (= krawedzie obrysow cech wycietych w plaszczyznie albo wyrastajacych z niej)."""
    bm = b.bm
    na = np.abs(b.V[:, 2] - z0) <= tol
    sas = {}
    for e in bm.edges:
        a = e.verts[0].index
        c = e.verts[1].index
        if not (na[a] and na[c]):
            continue
        lf = e.link_faces
        if len(lf) != 2:
            continue
        h0 = all(na[v.index] for v in lf[0].verts)
        h1 = all(na[v.index] for v in lf[1].verts)
        if h0 == h1:
            continue
        sas.setdefault(a, []).append(c)
        sas.setdefault(c, []).append(a)
    zle = sum(1 for v in sas.values() if len(v) != 2)
    odw = set()
    out = []
    for s in sas:
        if s in odw:
            continue
        lo = [s]
        odw.add(s)
        prev = None
        cur = s
        while True:
            nx = [n for n in sas[cur] if n != prev and n not in odw]
            if not nx:
                break
            prev, cur = cur, nx[0]
            lo.append(cur)
            odw.add(cur)
        out.append(b.V[lo][:, :2].copy())
    return out, zle


def dopasuj_okrag(Pt):
    """okrag metoda najmniejszych kwadratow (algebraicznie): srodek i promien - niezalezne od rozkladu wierzcholkow"""
    A = np.column_stack([Pt[:, 0], Pt[:, 1], np.ones(len(Pt))])
    y = -(Pt[:, 0] ** 2 + Pt[:, 1] ** 2)
    D, E, F = np.linalg.lstsq(A, y, rcond=None)[0]
    cx, cy = -D / 2.0, -E / 2.0
    return float(cx), float(cy), float(math.sqrt(max(cx * cx + cy * cy - F, 0.0)))


def spis(b, z0, oczek, etykieta, prost_cyfry=None, tol=0.02):
    """Dopasowanie petli na plaszczyznie z0 do cech oczekiwanych (lista (nazwa, Cecha)); kazda petla musi lezec na
    obrysie dokladnie jednej cechy (odchylka wierzcholkow <= tol), kazda cecha musi miec dokladnie jedna petle."""
    loops, zle = petle(b, z0)
    w = {"plaszczyzna": z0, "petli": len(loops), "wezly_nie_2": zle, "dopasowane": {}, "nieoczekiwane": [],
         "zewn": [], "cyfra": []}
    rim = {}
    for lo in loops:
        x0, y0 = lo.min(axis=0)
        x1, y1 = lo.max(axis=0)
        if (x1 - x0) > 80.0:
            sdp = [M.w_plytce_sd((float(p[0]), float(p[1]))) for p in lo]
            w["zewn"].append({"n": len(lo), "bbox": [round(float(v), 4) for v in (x0, x1, y0, y1)],
                              "sd_obrysu_min_max": [round(min(sdp), 4), round(max(sdp), 4)]})
            rim.setdefault("__zewn__", []).append(lo)
            continue
        if prost_cyfry and x0 >= prost_cyfry[0] and x1 <= prost_cyfry[1] and y0 >= prost_cyfry[2] and y1 <= prost_cyfry[3]:
            w["cyfra"].append({"n": len(lo), "bbox": [round(float(v), 4) for v in (x0, x1, y0, y1)]})
            rim.setdefault("__cyfra__", []).append(lo)
            continue
        cx = (x0 + x1) / 2.0
        cy = (y0 + y1) / 2.0
        best = None
        for nm, c in oczek:
            if abs(cx - c.x) > 2.0 or abs(cy - c.y) > 2.0:
                continue
            dev = max(abs(c.sd((float(p[0]), float(p[1])))) for p in lo)
            if best is None or dev < best[0]:
                best = (dev, nm, c)
        if best is not None and best[0] <= tol:
            dev, nm, c = best
            sr = dopasuj_okrag(lo) if (c.p0 == c.p1 and len(lo) >= 3) else lo.mean(axis=0)
            e = {"n": len(lo), "odch_max": round(dev, 5), "bbox": [round(float(v), 4) for v in (x0, x1, y0, y1)]}
            if c.p0 == c.p1:
                rr = np.hypot(lo[:, 0] - c.x, lo[:, 1] - c.y)
                e.update({"srodek": [round(float(sr[0]), 4), round(float(sr[1]), 4)], "r_max": round(float(rr.max()), 5),
                          "r_min": round(float(rr.min()), 5), "r_dopasowany": round(sr[2], 5),
                          "d_srodka": round(float(math.hypot(sr[0] - c.x, sr[1] - c.y)), 5)})
            w["dopasowane"].setdefault(nm, []).append(e)
            rim.setdefault(nm, []).append(lo)
        else:
            w["nieoczekiwane"].append({"n": len(lo), "bbox": [round(float(v), 4) for v in (x0, x1, y0, y1)],
                                       "najblizsza": None if best is None else [best[1], round(best[0], 4)]})
    w["brak"] = [nm for nm, c in oczek if nm not in w["dopasowane"]]
    w["zdublowane"] = [nm for nm, v in w["dopasowane"].items() if len(v) != 1]
    odch = [v[0]["odch_max"] for v in w["dopasowane"].values()]
    ds = [v[0]["d_srodka"] for v in w["dopasowane"].values() if "d_srodka" in v[0]]
    w["max_odch_srodka_okregu"] = max(ds) if ds else None
    w["wierzcholkow_w_petli_min_max"] = [min(v[0]["n"] for v in w["dopasowane"].values()), max(v[0]["n"] for v in w["dopasowane"].values())] if w["dopasowane"] else None
    ok = not w["nieoczekiwane"] and not w["brak"] and not w["zdublowane"] and zle == 0
    rec("SPIS/" + etykieta, ok, "petli %d: dopasowane do cech %d z %d oczekiwanych, obrys zewnetrzny %d, cyfra %d, NIEOCZEKIWANE %d,"
        " brak %d, zdublowane %d, wezly o stopniu != 2: %d; max odchylka wierzcholka od obrysu oczekiwanego %.5f;"
        " max odchylka srodka okregu (dopasowanie) %s; wierzcholkow w petli %s" % (
            len(loops), len(w["dopasowane"]), len(oczek), len(w["zewn"]), len(w["cyfra"]), len(w["nieoczekiwane"]),
            len(w["brak"]), len(w["zdublowane"]), zle, max(odch) if odch else 0.0, w["max_odch_srodka_okregu"],
            w["wierzcholkow_w_petli_min_max"]),
        "kazda petla = jedna cecha oczekiwana z parametry.json (tol %.2f), zadnych innych" % tol, "B", len(loops),
        (" NIEOCZEKIWANE: %s" % json.dumps(w["nieoczekiwane"][:8]) if w["nieoczekiwane"] else "")
        + (" BRAK: %s" % w["brak"] if w["brak"] else ""))
    return w, rim


def kopia_cechy(c, nazwa, r):
    return W.Cecha(c.rodzaj, nazwa, c.p0, c.p1, r)


def odl_wielobokow(A, B):
    def pts_segs(Pp, Q):
        Q2 = np.roll(Q, -1, axis=0)
        d = Q2 - Q
        L2 = np.maximum((d ** 2).sum(1), 1e-18)
        t = ((Pp[:, None, :] - Q[None, :, :]) * d[None]).sum(2) / L2[None]
        t = np.clip(t, 0.0, 1.0)
        pr = Q[None] + t[..., None] * d[None]
        return float(np.sqrt(((Pp[:, None, :] - pr) ** 2).sum(2)).min())
    return min(pts_segs(A, B), pts_segs(B, A))


def spisy(b):
    """spis petli na 5 plaszczyznach + scianki miedzy obrysami gornymi z wierzcholkow siatki"""
    out = {}
    tg = M.glebokosc * M.tan
    # wierzch
    gora = [(c.nazwa, c) for c in M.gniazda] + [("znacznik " + z.nazwa, z) for z in M.znaczniki] + \
           [("dolek " + k, M.dolki[k]) for k in BITY]
    pc = None
    if NUMER and M.cyfra is not None:
        pc = (M.cyfra[0] - 3.5, M.cyfra[0] + 3.5, M.cyfra[1] - 3.5, M.cyfra[1] + 3.5)
    out["wierzch"], rim = spis(b, 0.0, gora, "wierzch z=0", pc)
    # dna gniazd i rynienek (z = -4): obrys dna + krawedzie otworow
    dna = [("dno " + c.nazwa, kopia_cechy(c, "dno " + c.nazwa, c.r - tg)) for c in M.gniazda]
    otw = [("otwor " + nm, W.Cecha("hole", nm, (x, y), (x, y), M.otwor_d / 2.0)) for x, y, nm in M.otwory()]
    out["dna"], rim_d = spis(b, -M.glebokosc, dna + otw, "dna gniazd z=-%g" % M.glebokosc)
    # spod (z = -8): otwory przelotowe + kieszenie magnesow (kwadrat)
    sp = list(otw) + [("kieszen " + k, W.Cecha("pocket", k, p, p, M.magnes_d / 2.0)) for k, p in M.magnesy.items()]
    out["spod"], rim_s = spis(b, -GR, sp, "spod z=-%g" % GR)
    # dna dolkow (z = -1) i stropy kieszeni magnesow (z = -5,8)
    dd = [("dno dolka " + k, M.dolki[k]) for k in BITY]
    out["dna_dolkow"], _ = spis(b, -M.dolek_gl, dd, "dna dolkow z=-%g" % M.dolek_gl)
    if M.magnesy:
        st = [("strop kieszeni " + k, W.Cecha("pocket", k, p, p, M.magnes_d / 2.0)) for k, p in M.magnesy.items()]
        out["stropy_kieszeni"], _ = spis(b, -GR + M.magnes_gl, st, "stropy kieszeni z=%g" % (-GR + M.magnes_gl))
    return out, rim, rim_d


def poziome(b):
    """pola scian poziomych wg poziomu z: zwrocone w gore / w dol"""
    v0 = b.V[b.F[:, 0]]
    v1 = b.V[b.F[:, 1]]
    v2 = b.V[b.F[:, 2]]
    n = np.cross(v1 - v0, v2 - v0)
    pole = np.linalg.norm(n, axis=1) / 2.0
    nz = n[:, 2] / np.maximum(2 * pole, 1e-30)
    zs = (v0[:, 2] + v1[:, 2] + v2[:, 2]) / 3.0
    plaskie = (np.abs(v0[:, 2] - v1[:, 2]) < 1e-4) & (np.abs(v0[:, 2] - v2[:, 2]) < 1e-4)
    gora = {}
    dol = {}
    for i in np.nonzero(plaskie & (pole > 1e-12))[0]:
        d = gora if nz[i] > 0 else dol
        k = "%.3f" % (round(float(zs[i]), 3) + 0.0)
        d[k] = d.get(k, 0.0) + float(pole[i])
    skos_dol = int(((nz < -0.9) & ~plaskie).sum())
    return ({k: round(v, 3) for k, v in sorted(gora.items(), key=lambda t: float(t[0]))},
            {k: round(v, 3) for k, v in sorted(dol.items(), key=lambda t: float(t[0]))}, skos_dol)


def odl_kapsula(o, u, c, r):
    """odleglosc od punktu o (wewnatrz) wzdluz kierunku u do brzegu kapsuly (c.p0, c.p1, r) - bisekcja"""
    def f(t):
        return W.pt_seg((o[0] + t * u[0], o[1] + t * u[1]), c.p0, c.p1) - r
    a, bb = 0.0, 200.0
    for _ in range(60):
        m = (a + bb) / 2.0
        if f(m) < 0:
            a = m
        else:
            bb = m
    return (a + bb) / 2.0


def pomiar_cech(b):
    """pomiar promieniami kazdego gniazda, rynienki, stozka i dolka; zwraca slownik pomiarow"""
    out = {}
    zle = []
    maxodch = {"sciana": 0.0, "dno": 0.0, "otwor": 0.0}
    n0 = LICZ["promienie_pomiarowe"]
    for g in M.gniazda:
        e = {"r": {}}
        osie = [(g.x, g.y)] if g.rodzaj == "round" else [(g.x, g.y), g.p0, g.p1]
        for z in (-0.05, -2.0, -3.95):
            rz = g.r + z * M.tan
            odch = []
            for (ox, oy) in osie:
                nk = 24 if g.rodzaj == "round" else 36
                rr = b.promienie_poziome(ox, oy, z, nk, faza=0.131)
                for i, d in enumerate(rr):
                    a = 0.131 + 2 * math.pi * i / nk
                    ex = rz if g.rodzaj == "round" else odl_kapsula((ox, oy), (math.cos(a), math.sin(a)), g, rz)
                    odch.append(None if d is None else d - ex)
            if any(v is None for v in odch):
                zle.append("%s z=%g: promien bez trafienia" % (g.nazwa, z))
                continue
            e["r"]["%g" % z] = {"oczek_r": round(rz, 4), "odch_min": round(min(odch), 4), "odch_max": round(max(odch), 4)}
            maxodch["sciana"] = max(maxodch["sciana"], max(abs(v) for v in odch))
            if max(abs(v) for v in odch) > 0.1:
                zle.append("%s z=%g: odchylka promienia %.3f / %.3f" % (g.nazwa, z, min(odch), max(odch)))
        # dno i otwory
        if g.rodzaj == "round":
            pd = [(g.x + 2.2 * math.cos(a), g.y + 2.2 * math.sin(a)) for a in (0.3, 1.87, 3.44, 5.01)]
            srodki = [(g.x, g.y)]
        else:
            n = g.n_otw
            srodki = [(g.x + (j - (n - 1) / 2.0) * g.pitch, g.y) for j in range(n)]
            pd = [((srodki[j][0] + srodki[j + 1][0]) / 2.0, g.y) for j in range(n - 1)]
            pd += [(g.x, g.y + g.r - 2.5), (g.x, g.y - g.r + 2.5), (g.p0[0] - 2.0, g.y), (g.p1[0] + 2.0, g.y)]
        zd = [b.z_gora(px, py) for px, py in pd]
        e["dno_z"] = [None if v is None else round(v, 4) for v in zd]
        for v in zd:
            if v is None or abs(v + M.glebokosc) > 0.02:
                zle.append("%s: dno z=%s (oczek. %g)" % (g.nazwa, v, -M.glebokosc))
            else:
                maxodch["dno"] = max(maxodch["dno"], abs(v + M.glebokosc))
        e["otwory"] = []
        for (hx, hy) in srodki:
            zg = b.z_gora(hx, hy)
            zdl = b.z_dol(hx, hy)
            r6 = b.promienie_poziome(hx, hy, -6.0, 12, faza=0.2)
            r79 = b.promienie_poziome(hx, hy, -7.9, 12, faza=0.2)
            rr = [v for v in r6 + r79]
            if zg is not None or zdl is not None or any(v is None for v in rr):
                zle.append("%s: otwor (%g; %g) nieprzelotowy albo bez scianki: z_gora %s z_dol %s" % (g.nazwa, hx, hy, zg, zdl))
                continue
            od = [v - M.otwor_d / 2.0 for v in rr]
            e["otwory"].append({"xy": [hx, hy], "r_odch_min": round(min(od), 4), "r_odch_max": round(max(od), 4)})
            maxodch["otwor"] = max(maxodch["otwor"], max(abs(v) for v in od))
            if max(abs(v) for v in od) > 0.05:
                zle.append("%s: otwor (%g; %g) promien odchylka %.3f / %.3f" % (g.nazwa, hx, hy, min(od), max(od)))
        out[g.nazwa] = e
    n1 = LICZ["promienie_pomiarowe"]
    rec("POMIAR/gniazda", not zle, "%d gniazd i rynienek: max |odchylka promienia sciany| %.4f (z = -0,05 / -2 / -3,95), max |odchylka dna| %.4f,"
        " max |odchylka promienia otworu| %.4f; otworow przelotowych %d" % (
            len(M.gniazda), maxodch["sciana"], maxodch["dno"], maxodch["otwor"], sum(len(v["otwory"]) for v in out.values())),
        "promien = d/2 + z*tan(15) +-0,1; dno z = -4 +-0,02; otwor fi 3 przelotowy (r 1,5 +-0,05); otworow %d" % len(M.otwory()),
        "B", n1 - n0, "; ".join(zle[:10]))
    return out


def pomiar_znacznikow_dolkow(b):
    zle = []
    n0 = LICZ["promienie_pomiarowe"]
    out = {}
    mx = 0.0
    for zn in M.znaczniki:
        e = {}
        for z in (-0.05, -1.0, -2.0):
            rz = zn.r * (1.0 + z / M.marker_gl)
            rr = b.promienie_poziome(zn.x, zn.y, z, 16, faza=0.11)
            if any(v is None for v in rr):
                zle.append("znacznik %s z=%g: brak trafienia" % (zn.nazwa, z))
                continue
            od = [v - rz for v in rr]
            e["%g" % z] = [round(rz, 4), round(min(od), 4), round(max(od), 4)]
            mx = max(mx, max(abs(v) for v in od))
            if max(abs(v) for v in od) > 0.1:
                zle.append("znacznik %s z=%g: odchylka promienia %.3f / %.3f" % (zn.nazwa, z, min(od), max(od)))
        za = b.z_gora(zn.x + 0.05, zn.y + 0.02)
        ez = -M.marker_gl * (1.0 - math.hypot(0.05, 0.02) / zn.r)
        e["wierzcholek_z"] = None if za is None else round(za, 4)
        if za is None or abs(za - ez) > 0.05:
            zle.append("znacznik %s: glebokosc przy osi %s (oczek. %.3f)" % (zn.nazwa, za, ez))
        out["znacznik " + zn.nazwa] = e
    for k in "ABCD":
        d = M.dolki[k]
        zc = b.z_gora(d.x, d.y)
        if k in BITY:
            rr = b.promienie_poziome(d.x, d.y, -0.5, 12, faza=0.17)
            zo = [b.z_gora(d.x + 0.6 * math.cos(a), d.y + 0.6 * math.sin(a)) for a in (0.4, 2.5, 4.6)]
            if zc is None or any(v is None for v in rr) or any(v is None for v in zo):
                zle.append("dolek %s: brak trafienia" % k)
                continue
            od = [v - d.r for v in rr]
            out["dolek " + k] = {"dno_z": round(zc, 4), "dno_z_r06": [round(v, 4) for v in zo],
                                 "r_odch": [round(min(od), 4), round(max(od), 4)]}
            if abs(zc + M.dolek_gl) > 0.05 or max(abs(v) for v in od) > 0.05 or max(abs(v + M.dolek_gl) for v in zo) > 0.05:
                zle.append("dolek %s: dno %.3f, promien odch %.3f / %.3f" % (k, zc, min(od), max(od)))
        else:
            out["dolek " + k] = {"wierzch_z": None if zc is None else round(zc, 4)}
            if zc is None or abs(zc) > 0.005:
                zle.append("dolek %s (bit 0): wierzch z = %s zamiast 0" % (k, zc))
    rec("POMIAR/znaczniki+dolki", not zle, "3 stozki: max |odchylka promienia| %.4f na z -0,05 / -1 / -2, wierzcholek z %s; dolki obecne: %s"
        " (dno i promien w normie), dolki nieobecne: %s (wierzch z = 0)" % (
            mx, [out["znacznik " + z.nazwa].get("wierzcholek_z") for z in M.znaczniki], BITY,
            "".join(k for k in "ABCD" if k not in BITY) or "-"),
        "stozek fi %g x %g (r liniowo do 0 na z = -%g); dolek fi %g x %g tylko dla bitow %s" % (
            M.marker_d, M.marker_gl, M.marker_gl, M.dolek_d, M.dolek_gl, BITY), "B", LICZ["promienie_pomiarowe"] - n0,
        "; ".join(zle[:8]))
    return out


def najblizsze_punkty(c1, c2):
    """para punktow (na odcinkach osi obu cech) o najmniejszej odleglosci - przeszukanie z zageszczeniem"""
    best = None
    for i in range(201):
        t = i / 200.0
        a = (c1.p0[0] + t * (c1.p1[0] - c1.p0[0]), c1.p0[1] + t * (c1.p1[1] - c1.p0[1]))
        dx = c2.p1[0] - c2.p0[0]
        dy = c2.p1[1] - c2.p0[1]
        L2 = dx * dx + dy * dy
        s = 0.0 if L2 < 1e-18 else max(0.0, min(1.0, ((a[0] - c2.p0[0]) * dx + (a[1] - c2.p0[1]) * dy) / L2))
        q = (c2.p0[0] + s * dx, c2.p0[1] + s * dy)
        d = math.hypot(a[0] - q[0], a[1] - q[1])
        if best is None or d < best[0] - 1e-12:
            best = (d, a, q)
    return best


def scianki(b, rim):
    """scianki miedzy obrysami gornymi: (1) z wierzcholkow petli wierzchu, (2) promieniem poziomym na z = -0,01
    wzdluz linii najblizszych punktow; pary o odstepie analitycznym < 4,5 (gniazda, rynienki, stozki, dolki)"""
    cechy = [(c.nazwa, c) for c in M.gniazda] + [("znacznik " + z.nazwa, z) for z in M.znaczniki] + \
            [("dolek " + k, M.dolki[k]) for k in BITY]
    wyn = []
    zle = []
    n0 = LICZ["promienie_pomiarowe"]
    zr = -0.01
    for i in range(len(cechy)):
        for j in range(i + 1, len(cechy)):
            n1, c1 = cechy[i]
            n2, c2 = cechy[j]
            an = c1.odstep(c2)
            if an >= 4.5:
                continue
            rodz = set((c1.rodzaj, c2.rodzaj))
            if rodz == set(("dimple",)):
                lim = 1.0            # dolek - dolek: rozstaw 3, scianka 1 (opis code_dimples_round)
            elif rodz == set(("dimple", "marker")):
                lim = 1.5            # K-16 / K-62: dolek - stozek >= 1,5
            else:
                lim = M.wall_min     # gniazdo / rynienka / stozek / dolek - gniazdo: >= 3
            e = {"para": [n1, n2], "analit": round(an, 4), "limit": lim}
            if n1 in rim and n2 in rim:
                e["z_petli"] = round(odl_wielobokow(rim[n1][0], rim[n2][0]), 4)
            d, a, q = najblizsze_punkty(c1, c2)
            u = ((q[0] - a[0]) / d, (q[1] - a[1]) / d)
            # inna cecha na linii pomiaru (np. dolek B miedzy dolkami A i C) - promien mierzylby sasiada, pomijam promien
            zasl = None
            for nk, ck in cechy:
                if ck is c1 or ck is c2:
                    continue
                for t in range(1, 20):
                    w = c1.r + (d - c1.r - c2.r) * t / 20.0
                    if ck.sd((a[0] + u[0] * w, a[1] + u[1] * w)) < 0.0:
                        zasl = nk
                        break
                if zasl:
                    break
            if zasl:
                e["promien_pominiety_bo_miedzy_lezy"] = zasl
                wyn.append(e)
                continue
            # start 0,4 mm przed scianka cechy 1 (wewnatrz cechy 1), promien w strone cechy 2
            st = c1.r - 0.4
            o = (a[0] + u[0] * st, a[1] + u[1] * st, zr)
            h1 = b.promien(o, (u[0], u[1], 0.0))
            if h1 is None:
                zle.append("%s-%s: brak trafienia 1" % (n1, n2))
                wyn.append(e)
                continue
            p1 = h1[0]
            h2 = b.promien((p1.x + u[0] * 1e-4, p1.y + u[1] * 1e-4, zr), (u[0], u[1], 0.0))
            if h2 is None:
                zle.append("%s-%s: brak trafienia 2" % (n1, n2))
                wyn.append(e)
                continue
            # na glebokosci zr scianki stozkowe gniazd sa cofniete: poprawka do poziomu wierzchu
            popr = 0.0
            for c in (c1, c2):
                popr += abs(zr) * (M.tan if c.rodzaj in ("round", "trough") else (c.r / c.glebokosc if c.rodzaj == "marker" else 0.0))
            e["z_promienia_z-0.01"] = round(h2[1] + 1e-4, 4)
            e["z_promienia_na_wierzchu"] = round(h2[1] + 1e-4 - popr, 4)
            e["start_do_scianki1"] = round(h1[1], 4)
            wyn.append(e)
            m = min(e.get("z_petli", 99.0), e["z_promienia_na_wierzchu"])
            if m < lim - 0.005 or abs(e["z_promienia_na_wierzchu"] - an) > 0.05:
                zle.append("%s-%s: scianka %.4f (analit. %.4f, limit %g)" % (n1, n2, m, an, lim))
    gg = [e for e in wyn if e["limit"] == M.wall_min and "z_promienia_na_wierzchu" in e]
    mp = min(gg, key=lambda e: e["z_promienia_na_wierzchu"]) if gg else None
    zp_ = [e for e in wyn if "z_petli" in e]
    ml = min(zp_, key=lambda e: e["z_petli"]) if zp_ else None
    rec("SCIANKI", not zle and mp is not None, "par o odstepie < 4,5: %d; min scianka z promienia (na wierzchu) %s %s; min z wierzcholkow petli %s %s;"
        " max |pomiar - analit.| %.4f" % (
            len(wyn), mp and mp["z_promienia_na_wierzchu"], mp and mp["para"], ml and ml["z_petli"], ml and ml["para"],
            max([abs(e["z_promienia_na_wierzchu"] - e["analit"]) for e in gg] or [0.0])),
        "kazda scianka gniazdo/rynienka/stozek >= %g (tol. pomiaru 0,005), zgodna z rachunkiem z parametry.json +-0,05" % M.wall_min,
        "B", LICZ["promienie_pomiarowe"] - n0, "; ".join(zle[:8]))
    return wyn


# ---------- sondy protokolu (pozycje liczone z parametry.json) ----------
def sondy_protokolu(b):
    s = b.sonda
    k06 = []
    k07 = []
    for g in M.gniazda:
        if g.rodzaj != "round":
            continue
        d = g.d
        k06 += [s((g.x, g.y, -2), False, g.nazwa), s((g.x, g.y, -3.9), False, g.nazwa), s((g.x, g.y, -6), False, g.nazwa),
                s((g.x + 2.0, g.y, -6), True, g.nazwa), s((g.x + d / 2 + 1.6, g.y, -2), True, g.nazwa)]
        rm = (d - 2 * 2.0 * M.tan) / 2.0          # promien na z = -2 (protokol: (d - 1,07) / 2)
        k07 += [s((g.x + rm - 0.15, g.y, -2), False, g.nazwa), s((g.x + rm + 0.15, g.y, -2), True, g.nazwa),
                s((g.x, g.y + rm - 0.15, -2), False, g.nazwa), s((g.x, g.y - rm - 0.15, -2), True, g.nazwa)]
    sondy_wynik("K-06", k06, "B", uwaga="%d gniazd okraglych x 5 sond" % (len(k06) // 5))
    sondy_wynik("K-07", k07, "B", uwaga="wszystkie gniazda okragle (protokol: 3 na rozmiar), 4 sondy: +x i +-y")
    k08 = []
    k08n = []
    for g in M.gniazda:
        if g.rodzaj != "trough":
            continue
        l, w = g.l, g.w
        k08 += [s((g.x, g.y, -2), False, "srodek"), s((g.x + (l / 2 - 1), g.y, -2), False, "koniec +"),
                s((g.x - (l / 2 - 1), g.y, -2), False, "koniec -"), s((g.x + l / 2 + 1.6, g.y, -2), True, "za koncem +"),
                s((g.x - l / 2 - 1.6, g.y, -2), True, "za koncem -"), s((g.x, g.y, -6), True, "miedzy otworami")]
        n = g.n_otw
        for j in range(n):
            k08.append(s((g.x + (j - (n - 1) / 2.0) * g.pitch, g.y, -6), False, "otwor %d" % (j + 1)))
        u = (w / 2 + 0.6) / math.sqrt(2)
        for sx in (1, -1):
            for sy in (1, -1):
                k08.append(s((g.x + sx * ((l - w) / 2 + u), g.y + sy * u, -2), True, "45 st. od srodka polokregu"))
                e = s((g.x + sx * (l / 2 - 0.5), g.y + sy * (w / 2 - 0.5), -2), True, "naroznik prostokata")
                e["promien_xy"] = round(math.hypot(e["p"][0], e["p"][1]), 3)
                k08n.append(e)
    sondy_wynik("K-08", k08, "B", uwaga="rynienek: %d; otwory: %d na rynienke; sonda 45 st. na 4 koncach" % (
        sum(1 for g in M.gniazda if g.rodzaj == "trough"), M.trough_n))
    sondy_wynik("K-08/naroznik", k08n, "B", uwaga="sonda naroznika prostokata (4 narozniki), promien punktu %s" % (
        sorted(set(e["promien_xy"] for e in k08n))))
    k09 = []
    for zn in M.znaczniki:
        k09 += [s((zn.x, zn.y, -1), False, zn.nazwa), s((zn.x, zn.y, -3.3), True, zn.nazwa),
                s((zn.x + 1.5, zn.y, -1), False, zn.nazwa), s((zn.x + 2.7, zn.y, -1), True, zn.nazwa)]
    if KSZTALT == "kwadrat":
        for (x, y) in ((-42, -42), (-42, 42), (42, 42)):
            k09.append(s((x, y, -1), True, "dawny rog"))
    sondy_wynik("K-09", k09, "B")
    k11 = []
    for k in "ABCD":
        d = M.dolki[k]
        if k in BITY:
            k11 += [s((d.x, d.y, -0.5), False, "bit " + k), s((d.x, d.y, -1.3), True, "bit " + k)]
        else:
            k11.append(s((d.x, d.y, -0.5), True, "bit %s = 0" % k))
    sondy_wynik("K-11", k11, "B", uwaga="numer %d, bity %s" % (NUMER, BITY))
    if KSZTALT == "kwadrat":
        k10 = [s((45.5, -45.0, -4), False), s((45.5, -45.0, -7.9), False), s((41.5, -45.0, -4), True), s((45.5, -41.5, -4), True)]
        sondy_wynik("K-10", k10, "B")
        k12 = []
        for k, (x, y) in M.magnesy.items():
            k12 += [s((x, y, -7), False, k), s((x, y, -5.6), True, k), s((x + 2.45, y, -7), False, k), s((x + 2.8, y, -7), True, k)]
        k12.append(s((42, -42, -7), True, "D"))
        sondy_wynik("K-12", k12, "B")
        k14 = []
        for (ux, uy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            k14 += [s((47.5 * ux, 47.5 * uy, -2), False), s((46.9 * ux, 46.9 * uy, -2), True),
                    s((47.5 * ux, 47.5 * uy, -0.8), True), s((47.5 * ux, 47.5 * uy, -3.2), True)]
        sondy_wynik("K-14", k14, "B")
        k15 = [s((47.8, 47.8, -4), False), s((47.9, 0, -0.05), False), s((47.9, 0, -1), True)]
        sondy_wynik("K-15", k15, "D")
    else:
        R = M.R
        k61c = [s((0, R - 0.1, -0.05), False), s((0, R - 0.6, -0.15), True), s((0, R - 0.1, -1), True),
                s((0, R - 0.1, -7.9), True), s((0, R + 0.1, -4), False)]
        sondy_wynik("K-61c", k61c, "B")
        k63 = []
        for i in range(12):
            a = math.radians(15 + 30 * i)
            for z in (-7.0, -7.9):
                k63.append(s((45.5 * math.cos(a), 45.5 * math.sin(a), z), True, "r 45,5"))
        for a in (0.0, 90.0, 180.0):
            k63.append(s(((R - 0.5) * math.cos(math.radians(a)), (R - 0.5) * math.sin(math.radians(a)), -2), True, "dawny rowek"))
        for (x, y) in ((-42, -42), (-42, 42), (42, 42)):
            pass    # dawne rogi kwadratu leza poza plytka okragla (promien 59,4)
        sondy_wynik("K-63/sondy", k63, "B")


# ---------- mapy wierzchu i spodu wzgledem modelu oczekiwanego ----------
def sd_kapsula_np(X, Y, c, r):
    dx = c.p1[0] - c.p0[0]
    dy = c.p1[1] - c.p0[1]
    L2 = dx * dx + dy * dy
    if L2 < 1e-18:
        return np.hypot(X - c.p0[0], Y - c.p0[1]) - r
    t = np.clip(((X - c.p0[0]) * dx + (Y - c.p0[1]) * dy) / L2, 0.0, 1.0)
    return np.hypot(X - (c.p0[0] + t * dx), Y - (c.p0[1] + t * dy)) - r


def sd_plytki_np(Mo, X, Y):
    if Mo.ksztalt == "kwadrat":
        hb = Mo.bok / 2.0 - Mo.rog_r
        qx = np.abs(X) - hb
        qy = np.abs(Y) - hb
        return np.hypot(np.maximum(qx, 0.0), np.maximum(qy, 0.0)) + np.minimum(np.maximum(qx, qy), 0.0) - Mo.rog_r
    return np.maximum(np.hypot(X, Y) - Mo.R, X * Mo.flat_n[0] + Y * Mo.flat_n[1] - Mo.flat_dist)


def model_map(Mo, X, Y, bity, numer):
    """Model oczekiwany na siatce. Kody: 0 poza plytka (brak trafienia), 1 plaska powierzchnia, 2 cecha o znanej
    glebokosci, 3 przelot (brak trafienia), 4 strefa cyfry reliefu, 9 pas tolerancji (pomijany).
    Zwraca (KOD_gora, Z_gora, KOD_dol, Z_dol)."""
    sdp = sd_plytki_np(Mo, X, Y)
    KG = np.full(X.shape, 9, dtype=np.int8)
    ZG = np.zeros(X.shape)
    KD = np.full(X.shape, 9, dtype=np.int8)
    ZD = np.full(X.shape, -float(Mo.gr))
    KG[sdp > TOL] = 0
    KD[sdp > TOL] = 0
    KG[sdp < -(Mo.faza + TOL)] = 1
    KD[sdp < -(0.1 + TOL)] = 1
    for c in Mo.cechy_wierzchu(bity):
        sd = sd_kapsula_np(X, Y, c, c.r)
        wewn = sd < -TOL
        pas = (np.abs(sd) <= TOL) & (KG != 0)
        if c.rodzaj in ("round", "trough"):
            ze = -np.minimum(c.glebokosc, -sd / Mo.tan)
        elif c.rodzaj == "marker":
            ze = -c.glebokosc * np.minimum(1.0, -sd / c.r)
        else:
            ze = np.full(X.shape, -c.glebokosc)
        KG[wewn] = 2
        ZG[wewn] = ze[wewn]
        KG[pas] = 9
    for (hx, hy, nm) in Mo.otwory():
        ro = np.hypot(X - hx, Y - hy)
        rh = Mo.otwor_d / 2.0
        KG[ro < rh - TOL] = 3
        KD[ro < rh - TOL] = 3
        pas = np.abs(ro - rh) <= TOL
        KG[pas] = 9
        KD[pas] = 9
    for k, (mx, my) in Mo.magnesy.items():
        ro = np.hypot(X - mx, Y - my)
        rm = Mo.magnes_d / 2.0
        KD[ro < rm - TOL] = 2
        ZD[ro < rm - TOL] = -Mo.gr + Mo.magnes_gl
        KD[np.abs(ro - rm) <= TOL] = 9
    if Mo.wyciecie is not None:
        x0, x1, y0, y1 = Mo.wyciecie
        ax = X - x0
        ay = y1 - Y
        m = Mo.faza + TOL
        wpl = sdp <= TOL
        KG[(ax > -m) & (ay > -m) & wpl] = 9
        KD[(ax > -m) & (ay > -m) & wpl] = 9
        KG[(ax > TOL) & (ay > TOL)] = 3
        KD[(ax > TOL) & (ay > TOL)] = 3
    if numer and Mo.cyfra is not None:
        cz = (np.abs(X - Mo.cyfra[0]) <= 3.0) & (np.abs(Y - Mo.cyfra[1]) <= 3.5) & (KG == 1)
        KG[cz] = 4
    return KG, ZG, KD, ZD


def porownaj_mape(Z, K, ZE, xs, ys, etyk, relief=0.0, tol_plaski=0.005, tol_sciana=0.25):
    nan = np.isnan(Z)
    zle = np.zeros(Z.shape, dtype=bool)
    st = {}
    m = K == 1
    b1 = m & (nan | (np.abs(Z - ZE) > tol_plaski))
    st["plaskie_pkt"] = int(m.sum())
    st["plaskie_zle"] = int(b1.sum())
    m = K == 2
    dz = np.where(nan, 99.0, Z - ZE)
    b2 = m & (np.abs(dz) > tol_sciana)
    st["cechy_pkt"] = int(m.sum())
    st["cechy_zle"] = int(b2.sum())
    st["cechy_max_dz"] = round(float(np.abs(dz[m & ~nan]).max()), 4) if (m & ~nan).any() else None
    m = K == 3
    b3 = m & ~nan
    st["przeloty_pkt"] = int(m.sum())
    st["przeloty_zle"] = int(b3.sum())
    m = K == 0
    b0 = m & ~nan
    st["poza_pkt"] = int(m.sum())
    st["poza_zle"] = int(b0.sum())
    m = K == 4
    b4 = m & (nan | (Z < -tol_plaski) | (Z > relief + 0.01))
    st["cyfra_pkt"] = int(m.sum())
    st["cyfra_zle"] = int(b4.sum())
    st["cyfra_max_z"] = round(float(Z[m & ~nan].max()), 4) if (m & ~nan).any() else None
    st["pas_pkt"] = int((K == 9).sum())
    zle = b1 | b2 | b3 | b0 | b4
    przyk = []
    jj, ii = np.nonzero(zle)
    for t in range(0, len(jj), max(1, len(jj) // 12)):
        j, i = int(jj[t]), int(ii[t])
        przyk.append([round(float(xs[i]), 2), round(float(ys[j]), 2), None if nan[j, i] else round(float(Z[j, i]), 3),
                      int(K[j, i]), round(float(ZE[j, i]), 3)])
    st["zle_razem"] = int(zle.sum())
    n = st["plaskie_pkt"] + st["cechy_pkt"] + st["przeloty_pkt"] + st["poza_pkt"] + st["cyfra_pkt"]
    rec("MAPA/" + etyk, st["zle_razem"] == 0, "punktow ocenianych %d (plaskie %d, cechy %d, przeloty %d, poza plytka %d, strefa cyfry %d;"
        " pas tolerancji pominiety %d); NIEZGODNYCH %d (plaskie %d, cechy %d, przeloty %d, poza %d, cyfra %d); max |dz| w cechach %s" % (
            n, st["plaskie_pkt"], st["cechy_pkt"], st["przeloty_pkt"], st["poza_pkt"], st["cyfra_pkt"], st["pas_pkt"],
            st["zle_razem"], st["plaskie_zle"], st["cechy_zle"], st["przeloty_zle"], st["poza_zle"], st["cyfra_zle"],
            st["cechy_max_dz"]),
        "0 niezgodnych: plaskie z = oczek. +-%g; cechy +-%g w z; przeloty i poza plytka bez trafienia" % (tol_plaski, tol_sciana),
        "B", n, ("PRZYKLADY [x, y, z, kod, z_oczek]: %s" % json.dumps(przyk)) if przyk else "")
    return st, zle


def mapy_i_kontrola_odwrotna(b):
    L = 51.0
    n = int(round(2 * L / KROK)) + 1
    xs = np.linspace(-L, L, n) + 0.0137      # przesuniecie, zeby promienie nie biegly po krawedziach siatki
    ys = np.linspace(-L, L, n) + 0.0071
    X, Y = np.meshgrid(xs, ys)
    KG, ZG, KD, ZD = model_map(M, X, Y, BITY, NUMER)
    log("mapa wierzchu: %d x %d promieni, krok %g" % (n, n, KROK))
    Zg = b.mapa(xs, ys, 20.0, -1.0)
    stg, zleg = porownaj_mape(Zg, KG, ZG, xs, ys, "wierzch", relief=M.relief_h)
    log("mapa spodu")
    Zd = b.mapa(xs, ys, -30.0, 1.0)
    std, zled = porownaj_mape(Zd, KD, ZD, xs, ys, "spod")
    # cyfra: wysokosc reliefu i obrys z mapy
    cyf = None
    if NUMER and M.cyfra is not None:
        cz = (np.abs(X - M.cyfra[0]) <= 3.0) & (np.abs(Y - M.cyfra[1]) <= 3.5)
        rel = cz & (Zg > 0.3)
        poza = (~cz) & (Zg > 0.005)
        if rel.any():
            cyf = {"max_z": round(float(np.nanmax(Zg[cz])), 4), "pkt_reliefu": int(rel.sum()),
                   "x": [round(float(X[rel].min()), 2), round(float(X[rel].max()), 2)],
                   "y": [round(float(Y[rel].min()), 2), round(float(Y[rel].max()), 2)],
                   "pkt_nad_wierzchem_poza_strefa": int(poza.sum())}
            cyf["srodek"] = [round((cyf["x"][0] + cyf["x"][1]) / 2, 2), round((cyf["y"][0] + cyf["y"][1]) / 2, 2)]
            cyf["wys"] = round(cyf["y"][1] - cyf["y"][0] + KROK, 2)
            cyf["szer"] = round(cyf["x"][1] - cyf["x"][0] + KROK, 2)
            px = np.stack([X[rel], Y[rel]], axis=1)
            cyf["promien_max"] = round(float(np.hypot(px[:, 0], px[:, 1]).max()), 3)
            dmin = 99.0
            kto = ""
            for c in M.cechy_wierzchu(BITY):
                d = float(sd_kapsula_np(px[:, 0], px[:, 1], c, c.r).min())
                if d < dmin:
                    dmin, kto = d, c.opis()
            cyf["odstep_od_cech_min"] = [round(dmin, 3), kto]
            if KSZTALT == "okragla":
                cyf["do_sciecia"] = round(float((M.flat_dist - (px[:, 0] * M.flat_n[0] + px[:, 1] * M.flat_n[1])).min()), 3)
        ok = cyf is not None and abs(cyf["max_z"] - M.relief_h) <= 0.05 and abs(cyf["wys"] - M.cyfra_h) <= 0.3 \
            and cyf["pkt_nad_wierzchem_poza_strefa"] == 0 and math.hypot(cyf["srodek"][0] - M.cyfra[0], cyf["srodek"][1] - M.cyfra[1]) <= 0.6
        if ok and KSZTALT == "okragla":
            ok = cyf["promien_max"] <= M.zone_r + 0.05 and cyf["odstep_od_cech_min"][0] >= M.wall_min - 0.1
        rec("K-13", ok, "cyfra n%d: %s" % (NUMER, json.dumps(cyf)),
            "max z = %g +-0,05; wysokosc %g; srodek %s +-0,6; okragla: w kole %g i >= %g od gniazd; tresc cyfry - podglad PNG" % (
                M.relief_h, M.cyfra_h, list(M.cyfra), M.zone_r, M.wall_min), "B", int(cz.sum()))
        k = 8
        sub = Zg[np.ix_(np.abs(ys - M.cyfra[1]) <= 3.5, np.abs(xs - M.cyfra[0]) <= 3.5)][::-1]
        img = np.where(np.isnan(sub), 0, np.where(sub > 0.3, 255, np.where(sub < -0.005, 60, 150))).astype(np.uint8)
        zapisz_png(os.path.join(KAT_WYN, "cyfra_%s.png" % PLIK), np.kron(img, np.ones((k, k), dtype=np.uint8)))
    else:
        mz = float(np.nanmax(Zg))
        rec("K-13", abs(mz) <= 0.02, "plik bazowy: max z mapy wierzchu %.4f, max z wierzcholkow %.4f" % (mz, float(b.bb[1][2])),
            "0,00 +-0,02 (bez cyfry)", "B", 0)
    # obraz mapy wierzchu (co 2. punkt): szary = glebokosc, czarny = przelot / poza, czerwony = niezgodnosc z modelem
    g = np.where(np.isnan(Zg), 0.0, np.clip(255.0 + Zg * 45.0, 40.0, 255.0))
    g = np.where(Zg > 0.3, 110.0, g)
    rgb = np.stack([g, g, g], axis=2)
    rgb[zleg] = (255, 0, 0)
    zapisz_png(os.path.join(KAT_WYN, "mapa_%s.png" % PLIK), rgb[::-1][::2, ::2].astype(np.uint8))
    # --- kontrola odwrotna 1: stary STL tego samego pliku - gdzie stara siatka miala zaglebienie / przelot, a nowy model
    #     oczekuje plaskiej powierzchni, nowa siatka ma byc plaska
    ko = {}
    stary = os.path.join(KAT_STARE, PLIK + ".stl")
    if os.path.isfile(stary):
        bs = Bryla(stary)
        Zsg = bs.mapa(xs, ys, 20.0, -1.0)
        Zsd = bs.mapa(xs, ys, -30.0, 1.0)
        sdp = sd_plytki_np(M, X, Y)
        wn = sdp < -(M.faza + TOL)
        sg = wn & (np.isnan(Zsg) | (Zsg < -0.02))
        sd_ = wn & (np.isnan(Zsd) | (Zsd > -GR + 0.02))
        og = sg & (KG == 1)
        od = sd_ & (KD == 1)
        ko = {"stare_zaglebienia_wierzch_pkt": int(sg.sum()), "z_tego_nowy_model_plaski": int(og.sum()),
              "nowa_siatka_nieplaska": int((og & (np.isnan(Zg) | (np.abs(Zg) > 0.005))).sum()),
              "stare_przeloty_spod_pkt": int(sd_.sum()), "z_tego_nowy_model_plaski_spod": int(od.sum()),
              "nowa_siatka_nieplaska_spod": int((od & (np.isnan(Zd) | (np.abs(Zd + GR) > 0.005))).sum()),
              "stary_relief_pkt": int((wn & (Zsg > 0.3)).sum()),
              "stary_relief_poza_strefa_nowej_cyfry_a_nowa_siatka_z>0": int((wn & (Zsg > 0.3) & (KG == 1) & (Zg > 0.005)).sum())}
        ok = ko["nowa_siatka_nieplaska"] == 0 and ko["nowa_siatka_nieplaska_spod"] == 0 and \
            ko["stary_relief_poza_strefa_nowej_cyfry_a_nowa_siatka_z>0"] == 0
        rec("ODWROTNA/mapa-stary-STL", ok, json.dumps(ko), "w punktach, gdzie stary STL mial zaglebienie / przelot, a nowy uklad nie ma cechy:"
            " nowy wierzch z = 0, nowy spod z = -%g (0 punktow niezgodnych)" % GR, "B", 2 * n * n)
    else:
        rec("ODWROTNA/mapa-stary-STL", False, "brak pliku %s" % stary, "stary STL z archiwum", "P")
    return {"wierzch": stg, "spod": std, "cyfra": cyf, "odwrotna_mapa": ko}


def kontrola_odwrotna_sondy(b):
    """Kontrola odwrotna 2 (plan pkt 8.3): pozycje cech STAREGO ukladu liczone ze starych parametrow (archiwum).
    W punktach starej cechy lezacych >= 0,3 mm poza obrysami gornymi cech nowych: wierzch z = 0 i material w glebi."""
    nowe = M.cechy_wierzchu(BITY)
    stare = [("gniazdo", c) for c in MS.gniazda] + [("stozek", z) for z in MS.znaczniki]
    if KSZTALT == "okragla":
        stare += [("dolek okraglej", MS.dolki[k]) for k in "ABCD"]
    sondy = []
    zle = []
    stat = {"cech_starych": len(stare), "identyczne_z_nowa": 0, "sprawdzone": 0, "w_calosci_pod_nowa_cecha": 0,
            "punktow": 0, "punktow_pokrytych_nowa_cecha": 0, "otworow_starych": 0, "otworow_sprawdzonych": 0}
    lista = []
    for rodz, c in stare:
        ident = [n for n in nowe if n.rodzaj == c.rodzaj and abs(n.r - c.r) < 1e-6 and
                 max(abs(n.p0[0] - c.p0[0]), abs(n.p0[1] - c.p0[1]), abs(n.p1[0] - c.p1[0]), abs(n.p1[1] - c.p1[1])) < 1e-6]
        if ident:
            stat["identyczne_z_nowa"] += 1
            lista.append([rodz, c.opis(), "identyczna z nowa"])
            continue
        pts = []
        osie = [c.p0] if c.p0 == c.p1 else [(c.p0[0] + t * (c.p1[0] - c.p0[0]), c.p0[1]) for t in
                                              [i / 12.0 for i in range(13)]]
        for (ox, oy) in osie:
            pts.append((ox, oy))
            for fr in (0.45, 0.85):
                for i in range(8):
                    a = 0.2 + i * math.pi / 4
                    pts.append((ox + fr * c.r * math.cos(a), oy + fr * c.r * math.sin(a)))
        npok = 0
        nspr = 0
        for (px, py) in pts:
            stat["punktow"] += 1
            if min(n.sd((px, py)) for n in nowe) < 0.3 or M.w_plytce_sd((px, py)) > -(M.faza + 0.3):
                npok += 1
                continue
            if NUMER and M.cyfra is not None and abs(px - M.cyfra[0]) <= 3.3 and abs(py - M.cyfra[1]) <= 3.8:
                npok += 1
                continue
            nspr += 1
            zg = b.z_gora(px, py)
            if zg is None or abs(zg) > 0.005:
                zle.append("%s %s: wierzch w (%.2f; %.2f) z = %s" % (rodz, c.opis(), px, py, zg))
            gl = [-0.5, -2.0, -3.9] if rodz == "gniazdo" else ([-0.5, -2.0] if rodz == "stozek" else [-0.5])
            for z in gl:
                e = b.sonda((px, py, z), True, "stara cecha: %s %s" % (rodz, c.opis()))
                sondy.append(e)
        stat["punktow_pokrytych_nowa_cecha"] += npok
        if nspr:
            stat["sprawdzone"] += 1
        else:
            stat["w_calosci_pod_nowa_cecha"] += 1
        lista.append([rodz, c.opis(), "punktow %d, sprawdzonych %d, pod nowa cecha %d" % (len(pts), nspr, npok)])
    # stare otwory przelotowe fi 3: pod nowym wierzchem albo pod dnem nowego gniazda (poza nowymi otworami)
    no = M.otwory()
    for (hx, hy, nm) in MS.otwory():
        stat["otworow_starych"] += 1
        if min(math.hypot(hx - x, hy - y) for x, y, _ in no) < M.otwor_d + 0.3:
            continue
        stat["otworow_sprawdzonych"] += 1
        zd = b.z_dol(hx, hy)
        if zd is None or abs(zd + GR) > 0.005:
            zle.append("stary otwor %s (%.2f; %.2f): spod z = %s" % (nm, hx, hy, zd))
        for z in (-6.0, -7.5):
            sondy.append(b.sonda((hx, hy, z), True, "stary otwor " + nm))
    nz = [e for e in sondy if not e["ok"]]
    rec("ODWROTNA/sondy-stare-parametry", not zle and not nz, "%s; sond punktowych %d, niezgodnych %d" % (json.dumps(stat), len(sondy), len(nz)),
        "w miejscach cech starego ukladu poza cechami nowymi: wierzch z = 0, sondy W BRYLE, spod z = -%g" % GR, "B", len(sondy),
        "; ".join(zle[:8]) + (" NIEZGODNE: " + json.dumps(nz[:5]) if nz else ""))
    return {"stat": stat, "lista": lista}


def okragla_obrys(b, rim):
    """K-61 a, b, d, e, f oraz K-63 (sciany spodnie), scianki do krawedzi z wierzcholkow petli"""
    R = M.R
    pol = math.degrees(math.asin((M.flat_w / 2.0) / R))
    fa = math.degrees(M.flat_ang)
    pom = []
    zle = []
    n0 = LICZ["promienie_pomiarowe"]
    for z in (-4.0, -7.5):
        for i in range(36):
            a = 10.0 * i
            da = (a - fa + 180.0) % 360.0 - 180.0
            if abs(da) <= pol + 2.0:
                continue
            ar = math.radians(a)
            h = b.promien(((R + 5) * math.cos(ar), (R + 5) * math.sin(ar), z), (-math.cos(ar), -math.sin(ar), 0.0))
            r = None if h is None else R + 5 - h[1]
            pom.append(r)
            if r is None or abs(r - R) > 0.05:
                zle.append("a: kat %g z %g r = %s" % (a, z, r))
    plas = []
    for z in (-4.0, -7.5):
        ar = M.flat_ang
        h = b.promien(((R + 5) * math.cos(ar), (R + 5) * math.sin(ar), z), (-math.cos(ar), -math.sin(ar), 0.0))
        r = None if h is None else R + 5 - h[1]
        plas.append(r)
        if r is None or abs(r - M.flat_dist) > 0.05:
            zle.append("b: sciecie z %g odl = %s" % (z, r))
        for sgn in (1, -1):
            a2 = math.radians(fa + sgn * (pol + 3.0))
            h = b.promien(((R + 5) * math.cos(a2), (R + 5) * math.sin(a2), z), (-math.cos(a2), -math.sin(a2), 0.0))
            r2 = None if h is None else R + 5 - h[1]
            pom.append(r2)
            if r2 is None or abs(r2 - R) > 0.05:
                zle.append("b: 3 st. za sektorem sciecia, z %g r = %s" % (z, r2))
    gleb = (max(v for v in pom if v is not None) - min(v for v in plas if v is not None)) if not zle else None
    lo, hi = b.bb
    bbok = max(abs(lo[0] + R), abs(hi[0] - R), abs(lo[1] + R), abs(hi[1] - R)) <= 0.01 and abs(lo[2] + GR) <= 0.01
    ok = not zle and bbok and gleb is not None and gleb >= M.flat_depth_min
    rec("K-61abde", ok, "promien z %d sond: %.4f...%.4f; sciecie na %g st.: %s; glebokosc sciecia %s; bbox x %.4f...%.4f, y %.4f...%.4f, z_min %.4f" % (
        len(pom), min(v for v in pom if v is not None), max(v for v in pom if v is not None), fa,
        [None if v is None else round(v, 4) for v in plas], None if gleb is None else round(gleb, 4), lo[0], hi[0], lo[1], hi[1], lo[2]),
        "R = %g +-0,05; sciecie %.3f +-0,05; glebokosc >= %g; bbox +-R +-0,01, z_min -%g +-0,01" % (R, M.flat_dist, M.flat_depth_min, GR),
        "B", LICZ["promienie_pomiarowe"] - n0, "; ".join(zle[:6]))
    return {"promien_min_max": [min(v for v in pom if v is not None), max(v for v in pom if v is not None)], "sciecie": plas,
            "glebokosc": gleb}


def strefy_z_petli(rim, okr):
    """max promien obrysu, strefa +-45, scianki do krawedzi - z wierzcholkow petli wierzchu (siatka)"""
    out = {}
    gn = [(c.nazwa, c) for c in M.gniazda]
    zn = [("znacznik " + z.nazwa, z) for z in M.znaczniki]
    dl = [("dolek " + k, M.dolki[k]) for k in BITY]
    brak = [nm for nm, c in gn + zn + dl if nm not in rim]
    if brak:
        rec("STREFY", False, "brak petli wierzchu dla: %s" % brak, "petla dla kazdej cechy", "B")
        return out

    def mx(lst, f):
        return max((float(f(rim[nm][0]).max()), nm) for nm, c in lst)

    def mn(lst, f):
        return min((float(f(rim[nm][0]).min()), nm) for nm, c in lst)
    rg = mx(gn, lambda p: np.hypot(p[:, 0], p[:, 1]))
    rz = mx(zn, lambda p: np.hypot(p[:, 0], p[:, 1]))
    ax = mx(gn, lambda p: np.abs(p[:, 0]))
    ay = mx(gn, lambda p: np.abs(p[:, 1]))
    Lm = W.liczby_pelne(M)
    out.update({"max_promien_gniazd": rg, "max_promien_stozkow": rz, "max_abs_x": ax, "max_abs_y": ay,
                "analit_max_promien": Lm["max_promien"][0]})
    ok = rg[0] <= M.zone_r + 0.005 and rz[0] <= M.zone_r + 0.005 and ax[0] <= M.zone / 2.0 + 0.005 and ay[0] <= M.zone / 2.0 + 0.005
    ok = ok and abs(rg[0] - Lm["max_promien"][0]) <= 0.02
    rec("STREFY", ok, "z siatki: max promien obrysu gniazd %.4f (%s), stozkow %.4f (%s); max |x| %.4f (%s), max |y| %.4f (%s);"
        " rachunek z parametry.json: max promien %.4f" % (rg[0], rg[1], rz[0], rz[1], ax[0], ax[1], ay[0], ay[1], Lm["max_promien"][0]),
        "promien <= %g; |x|, |y| <= %g; zgodnosc z rachunkiem +-0,02" % (M.zone_r, M.zone / 2.0), "B")
    # K-05 (d): zaden wierzcholek obrysu gniazda w kwadracie naroznym; K-16 z petli: stozek - gniazdo, dolek - gniazdo,
    # dolek - stozek, promien srodka stozka
    nz = HB - M.rog_strefa
    wn = sum(int(((np.abs(rim[nm][0][:, 0]) > nz) & (np.abs(rim[nm][0][:, 1]) > nz)).sum()) for nm, c in gn)
    zg = {}
    for nm, z in zn:
        zg[nm] = min((odl_wielobokow(rim[nm][0], rim[g][0]), g) for g, c in gn)
    dg = min((odl_wielobokow(rim[nm][0], rim[g][0]), nm, g) for nm, c in dl for g, cc in gn)
    dz = min((odl_wielobokow(rim[nm][0], rim[g][0]), nm, g) for nm, c in dl for g, cc in zn)
    rs = dict((nm, float(np.hypot(*dopasuj_okrag(rim[nm][0])[:2]))) for nm, z in zn)
    a_zg = dict(("znacznik " + k, Lm["znaczniki"][k]["scianka_do_gniazda"][0]) for k in "ABC")
    a_dg = min(Lm["dolki"][k]["do_gniazda"][0] for k in BITY)
    a_dz = min(Lm["dolki"][k]["do_znacznika"][0] for k in BITY)
    out["k16"] = {"wierzcholkow_w_kwadratach_naroznych": wn, "stozek_gniazdo": zg, "dolek_gniazdo": dg, "dolek_stozek": dz,
                  "promien_srodka_stozka": rs, "analit": {"stozek_gniazdo": a_zg, "dolek_gniazdo": a_dg, "dolek_stozek": a_dz}}
    ok = wn == 0 and all(abs(zg[k][0] - a_zg[k]) <= 0.03 and zg[k][0] >= M.wall_min for k in zg)
    ok = ok and abs(dg[0] - a_dg) <= 0.03 and dg[0] >= M.wall_min and abs(dz[0] - a_dz) <= 0.03 and dz[0] >= 1.5
    ok = ok and all(v <= M.zone_r - M.marker_d / 2.0 + 0.005 for v in rs.values())
    rec("K-05d/K-16 siatka", ok, "z wierzcholkow petli [siatka / rachunek]: stozek-gniazdo %s; dolek-gniazdo %.3f (%s, %s) / %.3f;"
        " dolek-stozek %.3f (%s, %s) / %.3f; promien srodka stozka %s; wierzcholkow obrysow gniazd w kwadratach naroznych: %d" % (
            "; ".join("%s %.3f (%s) / %.3f" % (k[-1], zg[k][0], zg[k][1], a_zg[k]) for k in sorted(zg)),
            dg[0], dg[1], dg[2], a_dg, dz[0], dz[1], dz[2], a_dz, {k[-1]: round(v, 3) for k, v in rs.items()}, wn),
        "stozek-gniazdo >= %g, dolek-gniazdo >= %g, dolek-stozek >= 1,5, promien srodka stozka <= %g, 0 w narozach; zgodnosc +-0,03" % (
            M.wall_min, M.wall_min, M.zone_r - M.marker_d / 2.0), "B")
    if KSZTALT == "okragla":
        R = M.R
        n = M.flat_n
        fd = okr["sciecie"][0] if okr and okr.get("sciecie") and okr["sciecie"][0] else M.flat_dist

        def kr(p):
            return R - np.hypot(p[:, 0], p[:, 1])

        def sc(p):
            return fd - (p[:, 0] * n[0] + p[:, 1] * n[1])
        e = {"gniazdo_krawedz": mn(gn, kr), "stozek_krawedz": mn(zn, kr), "dolek_krawedz": mn(dl, kr),
             "gniazdo_sciecie": mn(gn, sc), "stozek_sciecie": mn(zn, sc), "dolek_sciecie": mn(dl, sc)}
        out["okragla"] = e
        a = {"gniazdo_krawedz": Lm["gniazdo_krawedz_okrag_min"][0], "stozek_krawedz": min(M.krawedz_odl(z)[0] for z in M.znaczniki),
             "dolek_krawedz": min(M.krawedz_odl(M.dolki[k])[0] for k in BITY),
             "gniazdo_sciecie": Lm["gniazdo_sciecie_min"][0], "stozek_sciecie": Lm["znacznik_sciecie_min"][0],
             "dolek_sciecie": min(M.krawedz_odl(M.dolki[k])[1] for k in BITY)}
        out["okragla_analit"] = a
        ok = all(abs(e[k][0] - a[k]) <= 0.03 for k in a)
        ok = ok and min(e["gniazdo_krawedz"][0], e["stozek_krawedz"][0], e["dolek_krawedz"][0]) >= 1.5
        ok = ok and min(e["gniazdo_sciecie"][0], e["stozek_sciecie"][0], e["dolek_sciecie"][0]) >= M.wall_min
        rec("K-16/K-61f/K-62 siatka", ok, "z wierzcholkow petli [siatka / rachunek]: " + "; ".join(
            "%s %.3f (%s) / %.3f" % (k, e[k][0], e[k][1], a[k]) for k in a),
            "do krawedzi >= 1,5; od plaszczyzny sciecia >= %g; zgodnosc z rachunkiem +-0,03" % M.wall_min, "B")
    return out


def main():
    log("PLIK %s typ %s ksztalt %s numer %d bity %s" % (PLIK, TYP, KSZTALT, NUMER, BITY))
    b = Bryla(os.path.join(KAT_STL, PLIK + ".stl"))
    wyn = {"plik": PLIK, "typ": TYP, "ksztalt": KSZTALT, "numer": NUMER, "bity": BITY, "krok_mapy": KROK}
    wyn["objetosc_cm3"] = ogolne(b)
    wyn["gabaryt"] = [b.bb[0].tolist(), b.bb[1].tolist()]
    wyn["trojkatow"] = b.n_tr_surowe
    wyn["spis"], rim, rim_d = spisy(b)
    # srednice z petli: gora (z = 0) i dno (z = -4) -> kat scianki
    katy = []
    for g in M.gniazda:
        if g.rodzaj != "round":
            continue
        e0 = wyn["spis"]["wierzch"]["dopasowane"].get(g.nazwa)
        e1 = wyn["spis"]["dna"]["dopasowane"].get("dno " + g.nazwa)
        if e0 and e1:
            katy.append(math.degrees(math.atan((e0[0]["r_max"] - e1[0]["r_max"]) / M.glebokosc)))
    ng = sum(1 for g in M.gniazda if g.rodzaj == "round")
    rec("KAT", len(katy) == ng and all(abs(k - math.degrees(M.kat)) <= 0.2 for k in katy),
        "kat scianki z petli gora/dno: %d gniazd, %.3f...%.3f st." % (len(katy), min(katy or [0]), max(katy or [0])),
        "%g st. +-0,2 dla %d gniazd" % (math.degrees(M.kat), ng), "B")
    g_, d_, skos = poziome(b)
    wyn["sciany_poziome_w_gore"] = g_
    wyn["sciany_poziome_w_dol"] = d_
    if KSZTALT == "okragla":
        inne = {k: v for k, v in d_.items() if abs(float(k) + GR) > 0.01}
        rec("K-63/spod", not inne and skos == 0, "sciany zwrocone w dol: poziomy z %s; skosne (n_z < -0,9) %d" % (d_, skos),
            "wszystkie na z = -%g +-0,01 (brak kieszeni i wnek)" % GR, "B")
    wyn["pomiar_gniazd"] = pomiar_cech(b)
    wyn["pomiar_znacznikow_dolkow"] = pomiar_znacznikow_dolkow(b)
    wyn["scianki"] = scianki(b, rim)
    sondy_protokolu(b)
    okr = okragla_obrys(b, rim) if KSZTALT == "okragla" else None
    wyn["okragla"] = okr
    wyn["strefy"] = strefy_z_petli(rim, okr)
    wyn["odwrotna_sondy"] = kontrola_odwrotna_sondy(b)
    wyn["mapy"] = mapy_i_kontrola_odwrotna(b)
    wyn["liczniki"] = LICZ
    wyn["wyniki"] = RES
    wyn["czas_s"] = round(time.time() - T0, 1)
    nie = [r for r in RES if r["wynik"] == "NIE"]
    wyn["nie"] = len(nie)
    with open(os.path.join(KAT_WYN, "wynik_%s.json" % PLIK), "w", encoding="utf-8") as f:
        json.dump(wyn, f, ensure_ascii=True, indent=1, default=str)
    log("KONIEC %s: sprawdzen %d, NIE %d, sondy %s, czas %.1f s" % (PLIK, len(RES), len(nie), LICZ, time.time() - T0))


try:
    main()
except Exception:
    import traceback
    traceback.print_exc()
    print("BLAD SKRYPTU")
    sys.stdout.flush()
    os._exit(3)
