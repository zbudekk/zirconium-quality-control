# -*- coding: utf-8 -*-
"""
Recenzent R59 - pkt 8.7 (K-53 / K-22 / K-32): WLASNY test przeciec plytka - wkladka, pokrywka - plytka, pokrywka - wkladka.
Zlozenie budowane przez recenzenta z plikow STL (nie z ramka_v2.blend i nie z wyniku generatora):
  uklad = srodek otworu wkladki, spod ramy wkladki z = 0 (tabela 1 protokolu);
  wkladka: STL z - 3,5, y - (y_min + 52,4), x - srodek obrysu;
  plytka: STL srodek XY = 0, spod na polkach wkladki (wysokosc polki MIERZONA promieniem z gory we wkladce);
  pokrywka: STL obrot 180 st. wokol X, wierzch zewnetrzny na z = wierzch plytki + cover_inner_h + cover_top_t.
Metody: (1) BVH overlap siatek surowych (styki = pary stykowe), (2) BVH overlap siatek skurczonych o 0,05 mm wzdluz
normalnych (metoda protokolu K-53) = 0, (3) wierzcholki jednej czesci wewnatrz drugiej (parzystosc promieni) glebiej niz
0,02 mm = 0, (4) luzy promieniami (plytka - otwor wkladki, plytka - wneka pokrywki, kolnierz pokrywki - rama wkladki).
Uruchomienie: blender.exe -b -P sprawdz_R59_K53.py -- --stl <kat> --par <parametry.json> --wyn <kat>
"""
import bpy
import bmesh
import json
import math
import os
import sys
import time

import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprawdz_R59_wspolne as W

ARG = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def arg(name, default=None):
    return ARG[ARG.index(name) + 1] if name in ARG else default


KAT_STL = arg("--stl")
PAR = W.wczytaj(arg("--par"))
KAT_WYN = arg("--wyn")
T0 = time.time()
RES = []
LICZ = {"sondy_punktowe": 0, "promienie_pomiarowe": 0, "wierzcholki_testowane": 0}
KIER = [Vector((1.0, 0.00071, 0.00137)).normalized(), Vector((0.00083, 1.0, 0.00119)).normalized(),
        Vector((0.00097, 0.00061, 1.0)).normalized()]


def log(*a):
    print("[%6.1fs]" % (time.time() - T0), *a)
    sys.stdout.flush()


def rec(kid, ok, wartosc, oczek, waga, uwaga=""):
    RES.append({"id": kid, "wynik": "ZAL" if ok else "NIE", "wartosc": wartosc, "oczekiwane": oczek, "waga": waga, "uwaga": uwaga})
    log("[%s] %s: %s | oczek: %s %s" % ("ZAL" if ok else "NIE", kid, wartosc, oczek, uwaga))


class Czesc(object):
    def __init__(self, nazwa, plik):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.wm.stl_import(filepath=os.path.join(KAT_STL, plik + ".stl"))
        obj = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        bm.verts.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        bm.verts.index_update()
        self.nazwa = nazwa
        self.plik = plik
        self.V = np.array([v.co[:] for v in bm.verts])
        self.F = np.array([[v.index for v in f.verts] for f in bm.faces], dtype=np.int64)
        bm.free()
        self.bvh = None

    def przeksztalc(self, obrot_x_180=False, przes=(0.0, 0.0, 0.0)):
        if obrot_x_180:
            self.V = self.V * np.array([1.0, -1.0, -1.0])     # obrot 180 st. wokol X: y -> -y, z -> -z (bez odbicia)
        self.V = self.V + np.array(przes)
        self.buduj()

    def buduj(self):
        self.bvh = BVHTree.FromPolygons([Vector(p) for p in self.V], [tuple(int(i) for i in t) for t in self.F],
                                        all_triangles=True, epsilon=0.0)
        v0 = self.V[self.F[:, 0]]
        v1 = self.V[self.F[:, 1]]
        v2 = self.V[self.F[:, 2]]
        fn = np.cross(v1 - v0, v2 - v0)
        self.obj = float(np.einsum("ij,ij->i", v0, np.cross(v1, v2)).sum() / 6.0)
        vn = np.zeros_like(self.V)
        # normalne wierzcholkow wazone katem bylyby lepsze; do skurczenia o 0,05 wystarcza suma normalnych jednostkowych scian
        fnu = fn / np.maximum(np.linalg.norm(fn, axis=1)[:, None], 1e-30)
        for k in range(3):
            np.add.at(vn, self.F[:, k], fnu)
        self.VN = vn / np.maximum(np.linalg.norm(vn, axis=1)[:, None], 1e-30)

    def skurczona(self, d=0.05):
        Vs = self.V - self.VN * d
        return BVHTree.FromPolygons([Vector(p) for p in Vs], [tuple(int(i) for i in t) for t in self.F],
                                    all_triangles=True, epsilon=0.0)

    def _licz(self, p, d):
        n = 0
        o = Vector(p)
        ost = None
        for _ in range(2000):
            h = self.bvh.ray_cast(o, d, 1000.0)
            if h[0] is None:
                break
            if ost is None or (h[0] - ost).length > 1e-5:
                n += 1
            ost = h[0]
            o = h[0] + d * 1e-4
        return n

    def w_bryle(self, p):
        r = [self._licz(p, d) % 2 == 1 for d in KIER]
        return r.count(True) >= 2, r.count(True) in (0, 3)

    def sonda(self, p, oczek_w, opis=""):
        LICZ["sondy_punktowe"] += 1
        w, pewna = self.w_bryle(p)
        return {"p": list(p), "oczek": "W" if oczek_w else "POZA", "wynik": "W" if w else "POZA", "pewna": pewna,
                "ok": (w == oczek_w) and pewna, "opis": opis}

    def promien(self, o, d, maxd=500.0):
        LICZ["promienie_pomiarowe"] += 1
        h = self.bvh.ray_cast(Vector(o), Vector(d).normalized(), maxd)
        return None if h[0] is None else (h[0], h[3])


def punkty_w(A, B, margines=0.02):
    """ile punktow A (wierzcholki + srodki trojkatow) lezy wewnatrz bryly B glebiej niz margines"""
    lo = B.V.min(axis=0) + margines
    hi = B.V.max(axis=0) - margines
    P = np.vstack([A.V, A.V[A.F].mean(axis=1)])
    kand = np.nonzero(np.all((P > lo) & (P < hi), axis=1))[0]
    n = 0
    maxg = 0.0
    for i in kand:
        p = Vector(P[i])
        LICZ["wierzcholki_testowane"] += 1
        w, pewna = B.w_bryle(p)
        if w:
            dist = B.bvh.find_nearest(p)[3]
            if dist > margines:
                n += 1
                maxg = max(maxg, dist)
    return n, len(kand), round(maxg, 4)


def para(A, B, z_styku=None):
    pary = A.bvh.overlap(B.bvh)
    surowe = len(pary)
    # pary stykowe (A = plytka, B = wkladka): spod plytki lezy na polkach - trojkat plytki w calosci na / nad plaszczyzna
    # styku, trojkat wkladki w calosci na / pod nia (moga sie stykac tylko w tej plaszczyznie); kazda inna para = przeciecie
    inne = 0
    if z_styku is not None:
        for i, j in pary:
            if A.V[A.F[i]][:, 2].min() < z_styku - 1e-5 or B.V[B.F[j]][:, 2].max() > z_styku + 1e-5:
                inne += 1
    skurcz = len(A.skurczona(0.05).overlap(B.skurczona(0.05)))
    ab = punkty_w(A, B)
    ba = punkty_w(B, A)
    return {"para": "%s - %s" % (A.nazwa, B.nazwa), "overlap_surowy": surowe,
            "overlap_surowy_poza_plaszczyzna_styku": inne if z_styku is not None else surowe, "overlap_skurczone_0.05": skurcz,
            "punkty_A_w_B": ab[0], "kandydatow_A": ab[1], "punkty_B_w_A": ba[0], "kandydatow_B": ba[1],
            "max_zaglebienie": max(ab[2], ba[2])}


def main():
    Pp = lambda k, sec="plytka": W.P(PAR, k, sec)
    gr = Pp("plate_thickness")
    inner_h = Pp("cover_inner_h", "pokrywka")
    top_t = Pp("cover_top_t", "pokrywka")
    # --- wkladka ---
    wk = Czesc("wkladka", "ramka_wkladka_v2")
    lo = wk.V.min(axis=0)
    hi = wk.V.max(axis=0)
    wk.przeksztalc(przes=(-(lo[0] + hi[0]) / 2.0, -(lo[1] + 52.4), -3.5))
    s = [wk.sonda((48.2, 0, 3), False, "K-23"), wk.sonda((48.6, 0, 3), True, "K-23"), wk.sonda((52.6, 0, 3), False, "K-23"),
         wk.sonda((0, 0, 3), False, "K-23"), wk.sonda((-38, -38, 1.5), True, "K-24"), wk.sonda((-38, -38, 3), False, "K-24"),
         wk.sonda((38, 38, 1.5), True, "K-24"), wk.sonda((-38, 38, 1.5), True, "K-24"), wk.sonda((38, -38, 1.5), True, "K-24"),
         wk.sonda((45.6, -45.6, 5), True, "K-27 kolek w D"), wk.sonda((45.6, -45.6, 8), False, "K-27"),
         wk.sonda((0, -50.3, 3), False, "K-28 wyciecie palcowe z przodu")]
    zle = [e for e in s if not e["ok"]]
    zp = [wk.promien((x, y, 30.0), (0, 0, -1))[0].z for x, y in ((-38, -38), (38, 38), (-38, 38), (38, -38))]
    z_polki = max(zp)
    z_ramy = wk.promien((51.0, 20.0, 30.0), (0, 0, -1))[0].z
    rec("K-53/uklad wkladki", not zle and max(zp) - min(zp) < 1e-3, "sondy orientacji wkladki %d/%d zgodnych; wysokosc 4 polek %s; wierzch ramy z = %.4f;"
        " objetosc %.3f cm3" % (len(s) - len(zle), len(s), [round(v, 4) for v in zp], z_ramy, wk.obj / 1000.0),
        "transformacja z tabeli 1 protokolu poprawna (K-23, K-24, K-27, K-28); polki na jednej wysokosci", "B", json.dumps(zle))
    # --- pokrywka ---
    pk = Czesc("pokrywka", "ramka_pokrywka_v2")
    lo = pk.V.min(axis=0)
    hi = pk.V.max(axis=0)
    pk.przeksztalc(obrot_x_180=True, przes=(-(lo[0] + hi[0]) / 2.0, (lo[1] + hi[1]) / 2.0, 0.0))
    s = [pk.sonda((0, 0, -1), True, "K-17"), pk.sonda((0, 0, -2.5), False, "K-17"), pk.sonda((48.1, 0, -10), False, "K-17"),
         pk.sonda((48.5, 0, -10), True, "K-17"), pk.sonda((50, 0, -10), False, "K-17"), pk.sonda((47.8, 0, -18), True, "K-18 garb"),
         pk.sonda((25, -47.8, -18), True, "K-18 garb przod x=+25"), pk.sonda((-25, 47.8, -18), True, "K-18 garb tyl x=-25"),
         pk.sonda((25, 47.8, -18), False, "K-18"), pk.sonda((0, -49, -19), False, "K-20 wyciecie palcowe")]
    zle = [e for e in s if not e["ok"]]
    zmin_pk = float(pk.V[:, 2].min())
    rec("K-53/uklad pokrywki", not zle and abs(zmin_pk + 20.0) < 0.01, "sondy orientacji pokrywki %d/%d zgodnych; z_min %.4f; objetosc %.3f cm3" % (
        len(s) - len(zle), len(s), zmin_pk, pk.obj / 1000.0), "transformacja z tabeli 1 poprawna (K-17, K-18, K-20); kolnierz do -20", "B",
        json.dumps(zle))
    z_wierzch_plytki = z_polki + gr
    dz_pk = z_wierzch_plytki + inner_h + top_t
    pk.przeksztalc(przes=(0.0, 0.0, dz_pk))
    wyn = {"z_polki": z_polki, "z_ramy_wkladki": z_ramy, "z_wierzch_plytki": z_wierzch_plytki, "z_wierzch_pokrywki": dz_pk,
           "z_dol_kolnierza_pokrywki": float(pk.V[:, 2].min()), "pary": [], "luzy": {}}
    pw = para(pk, wk)
    wyn["pary"].append(pw)
    luz_kw = float(pk.V[:, 2].min()) - z_ramy
    rec("K-22/K-53 pokrywka-wkladka", pw["overlap_skurczone_0.05"] == 0 and pw["punkty_A_w_B"] == 0 and pw["punkty_B_w_A"] == 0 and luz_kw > 0,
        json.dumps(pw) + "; dol kolnierza %.4f, wierzch ramy %.4f, luz %.4f" % (float(pk.V[:, 2].min()), z_ramy, luz_kw),
        "0 przeciec; kolnierz nad rama (plan: 0,5)", "B")
    plytki = ["ramka_plytka_wieczorna_n1_v2", "ramka_plytka_wieczorna_n2_v2", "ramka_plytka_wieczorna_n3_v2",
              "ramka_plytka_poranna_n4_v2", "ramka_plytka_poranna_n5_v2", "ramka_plytka_poranna_n6_v2",
              "ramka_plytka_wieczorna_v2", "ramka_plytka_poranna_v2"]
    for plik in plytki:
        pl = Czesc(plik.replace("ramka_", "").replace("_v2", ""), plik)
        lo = pl.V.min(axis=0)
        hi = pl.V.max(axis=0)
        pl.przeksztalc(przes=(-(lo[0] + hi[0]) / 2.0, -(lo[1] + hi[1]) / 2.0, z_polki - lo[2]))
        a = para(pl, wk, z_polki)
        c = para(pk, pl)
        wyn["pary"] += [a, c]
        # luzy promieniami (kazda czesc osobno): plytka - otwor wkladki na z = polka + 2; wneka pokrywki - plytka 0,8 pod wierzchem
        zl = z_polki + 2.0
        zc = z_wierzch_plytki - 0.8
        lz = {"plytka_wkladka": [], "pokrywka_plytka": []}
        for (ux, uy, ox, oy) in ((1, 0, 0, 20), (-1, 0, 0, 20), (0, 1, 20, 0), (0, -1, 30, 0)):
            hp = pl.promien((ox + ux * 70, oy + uy * 70, zl), (-ux, -uy, 0))
            hw = wk.promien((ox, oy, zl), (ux, uy, 0))
            lz["plytka_wkladka"].append(round((hw[0].x * ux + hw[0].y * uy) - (hp[0].x * ux + hp[0].y * uy), 4))
            hp2 = pl.promien((ox + ux * 70, oy + uy * 70, zc), (-ux, -uy, 0))
            hc = pk.promien((ox, oy, zc), (ux, uy, 0))
            lz["pokrywka_plytka"].append(round((hc[0].x * ux + hc[0].y * uy) - (hp2[0].x * ux + hp2[0].y * uy), 4))
        # garb pokrywki w rowku plytki (prawy bok, y = 0): czubek garbu i dno rowka na z = wierzch plytki - 2
        zg = z_wierzch_plytki - Pp("cover_groove_z")
        hg = pk.promien((0, 0, zg), (1, 0, 0))
        hr = pl.promien((70, 0, zg), (-1, 0, 0))
        lz["garb_x"] = round(hg[0].x, 4)
        lz["dno_rowka_x"] = round(hr[0].x, 4)
        lz["luz_garb_dno_rowka"] = round(hg[0].x - hr[0].x, 4)
        wyn["luzy"][plik] = lz
        ok = all(p["overlap_skurczone_0.05"] == 0 and p["punkty_A_w_B"] == 0 and p["punkty_B_w_A"] == 0 for p in (a, c))
        ok = ok and a["overlap_surowy_poza_plaszczyzna_styku"] == 0 and c["overlap_surowy"] == 0
        ok = ok and min(lz["plytka_wkladka"]) > 0.2 and min(lz["pokrywka_plytka"]) > 0.1 and lz["luz_garb_dno_rowka"] > 0
        rec("K-53 " + plik, ok, "plytka-wkladka: %s | pokrywka-plytka: %s | luzy: %s" % (json.dumps(a), json.dumps(c), json.dumps(lz)),
            "0 przeciec (siatki skurczone 0,05 i punkty w bryle); luz plytka-wkladka 0,4/strone, pokrywka-plytka 0,3/strone", "B")
    # --- kontrola czulosci metody (czy test wykrywa przenikanie): plytka n1 przesunieta o 0,6 mm w +x (luz 0,4),
    #     pokrywka opuszczona o 1,0 mm (luz do ramy 0,5) ---
    pl = Czesc("plytka_wieczorna_n1 (+0,6 mm x)", "ramka_plytka_wieczorna_n1_v2")
    lo = pl.V.min(axis=0)
    hi = pl.V.max(axis=0)
    pl.przeksztalc(przes=(-(lo[0] + hi[0]) / 2.0 + 0.6, -(lo[1] + hi[1]) / 2.0, z_polki - lo[2]))
    k1 = para(pl, wk, z_polki)
    pk.przeksztalc(przes=(0.0, 0.0, -1.0))
    k2 = para(pk, wk)
    ok = (k1["overlap_skurczone_0.05"] > 0 and k1["punkty_A_w_B"] + k1["punkty_B_w_A"] > 0 and k2["overlap_skurczone_0.05"] > 0)
    rec("K-53/kontrola czulosci", ok, "plytka +0,6 mm: %s | pokrywka -1,0 mm: %s" % (json.dumps(k1), json.dumps(k2)),
        "celowe przenikanie musi byc wykryte (overlap skurczonych > 0)", "B")
    wyn["wyniki"] = RES
    wyn["liczniki"] = LICZ
    with open(os.path.join(KAT_WYN, "wynik_K53.json"), "w", encoding="utf-8") as f:
        json.dump(wyn, f, indent=1)
    nie = sum(1 for r in RES if r["wynik"] == "NIE")
    log("KONIEC K-53: sprawdzen %d, NIE %d, liczniki %s" % (len(RES), nie, LICZ))


try:
    main()
except Exception:
    import traceback
    traceback.print_exc()
    print("BLAD SKRYPTU")
    sys.stdout.flush()
    os._exit(3)
