# -*- coding: utf-8 -*-
"""
Skrypt RECENZENTA — R54, zestaw złożony z wyniki_v2/ramka_v2.blend: K-53 (brak przenikań), K-55 (magnes–czujnik), K-32/K-22 (luzy płytki
we wkładce i w pokrywce z promieni w złożeniu), K-54 (wybrane wysokości) oraz kontrola, że płytka n1 w .blend jest płytką po R54
(znacznik A w (−35,5, −26,5), dawny róg (−42, −42) pełny; objętość = STL n1).
Napisany bez czytania ramka_generator.py. Uruchomienie:
  "C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe" -b -P recenzja/sprawdz_R54_C.py -- --iter 1
Wyniki: recenzja/wyniki_R54_iter<n>_C.json
"""
import bpy, json, math, os, sys, hashlib
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

ROOT = r"<PC>\Desktop\Ramki"
WYN = os.path.join(ROOT, "wyniki_v2")
REC = os.path.join(ROOT, "recenzja")
ITER = "1"
if "--" in sys.argv:
    a = sys.argv[sys.argv.index("--") + 1:]
    if "--iter" in a:
        ITER = a[a.index("--iter") + 1]
PAR = json.load(open(os.path.join(ROOT, "parametry.json"), encoding="utf-8"))
def P(sec, key):
    return PAR[sec][key]["value"]

RESULTS = []
def rec(kid, plik, wynik, wartosc, waga, sondy=None, uwaga=""):
    RESULTS.append({"id": kid, "plik": plik, "wynik": wynik, "wartosc": wartosc, "waga": waga, "sondy": sondy or [], "uwaga": uwaga})
    print(f"[{wynik}] {kid} {plik}: {wartosc} {uwaga}")

def bbox(verts):
    xs = [v.x for v in verts]; ys = [v.y for v in verts]; zs = [v.z for v in verts]
    return (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))

class Solid:
    def __init__(self, verts, tris, name=""):
        self.name = name; self.verts = verts; self.tris = tris
        self.bvh = BVHTree.FromPolygons(verts, tris, all_triangles=True, epsilon=0.0)
        self.bb = bbox(verts)
        self.dirs = [Vector((1.0, 0.00071, 0.00137)).normalized(), Vector((0.00083, 1.0, 0.00119)).normalized(), Vector((0.00097, 0.00061, 1.0)).normalized()]
        self.diag = (Vector((self.bb[1], self.bb[3], self.bb[5])) - Vector((self.bb[0], self.bb[2], self.bb[4]))).length + 10
    @classmethod
    def from_object(cls, obj, matrix, name=""):
        me = obj.data
        verts = [matrix @ v.co for v in me.vertices]
        me.calc_loop_triangles()
        return cls(verts, [tuple(t.vertices) for t in me.loop_triangles], name)
    def count_hits(self, p, d):
        n = 0; o = Vector(p); last = None
        for _ in range(500):
            hit = self.bvh.ray_cast(o, d, self.diag)
            if hit[0] is None:
                break
            loc = hit[0]
            if last is None or (loc - last).length > 1e-5:
                n += 1
            last = loc; o = loc + d * 1e-4
        return n
    def inside3(self, p):
        return [self.count_hits(p, d) % 2 == 1 for d in self.dirs]
    def probe(self, p, expect_in, tag=""):
        p = Vector(p); r = self.inside3(p)
        loc, nrm, idx, dist = self.bvh.find_nearest(p)
        e = {"p": [round(c, 3) for c in p], "oczek": "W" if expect_in else "POZA", "r3": ["W" if x else "P" for x in r], "d_sciana": round(dist, 3) if dist is not None else None, "tag": tag}
        if r.count(True) in (0, 3):
            e["wynik"] = "W" if r[0] else "POZA"
        else:
            nrm = nrm if (nrm is not None and nrm.length > 0) else Vector((0, 0, 1))
            p2 = p + (-nrm if expect_in else nrm) * 0.1; r2 = self.inside3(p2)
            e["niestabilna"] = True; e["p_przes"] = [round(c, 3) for c in p2]
            e["wynik"] = ("W" if r2[0] else "POZA") if r2.count(True) in (0, 3) else "NIESTABILNA"
        e["ok"] = (e["wynik"] == e["oczek"])
        return e
    def first_hit(self, origin, direction):
        hit = self.bvh.ray_cast(Vector(origin), Vector(direction).normalized(), self.diag)
        return None if hit[0] is None else hit[0]
    def top_z(self, x, y):
        h = self.first_hit((x, y, self.bb[5] + 5), (0, 0, -1))
        return None if h is None else h.z
    def volume(self):
        v = 0.0; V = self.verts
        for a, b, c in self.tris:
            v += V[a].dot(V[b].cross(V[c]))
        return v / 6.0 / 1000.0

def vertex_normals(verts, tris):
    nrm = [Vector((0, 0, 0)) for _ in verts]
    for a, b, c in tris:
        n = (verts[b] - verts[a]).cross(verts[c] - verts[a])
        nrm[a] += n; nrm[b] += n; nrm[c] += n
    return [n.normalized() if n.length > 0 else Vector((0, 0, 1)) for n in nrm]

def shrunk_bvh(S, d=0.05):
    nrm = vertex_normals(S.verts, S.tris)
    return BVHTree.FromPolygons([v - n * d for v, n in zip(S.verts, nrm)], S.tris, all_triangles=True, epsilon=0.0)

def main():
    blend = os.path.join(WYN, "ramka_v2.blend")
    sha = hashlib.sha256(open(blend, "rb").read()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=blend)
    sol = {}
    for o in bpy.data.objects:
        if o.type == "MESH":
            sol[o.name] = Solid.from_object(o, o.matrix_world, o.name)
    assembled = [n for n, S in sol.items() if max(abs(S.bb[0]), abs(S.bb[1]), abs(S.bb[2]), abs(S.bb[3])) <= 150]
    offset = sorted(n for n in sol if n not in assembled)
    mind_off = min((min(abs(sol[n].bb[0]), abs(sol[n].bb[1]), abs(sol[n].bb[2]), abs(sol[n].bb[3])) for n in offset), default=None)
    rec("INFO-blend", "ramka_v2.blend", "ZAL", f"SHA {sha[:16]}…; obiektów MESH {len(sol)}; zestaw złożony ({len(assembled)}): {sorted(assembled)}; odsunięte ({len(offset)}): {offset}; najmniejsza |współrzędna XY| odsuniętych {mind_off}", "-")
    # płytka n1 w zestawie = płytka po R54?
    pl = sol.get("plytka_wieczorna_n1")
    if pl is None:
        rec("INFO-plytka", "ramka_v2.blend", "NIE", "brak obiektu plytka_wieczorna_n1 w zestawie", "B")
    else:
        top = pl.top_z(0, -46.5)   # pas płaski między R1 a fazą (K-54: 74,1)
        zt = round(top, 3) if top is not None else None
        ev = P("plytka", "ev_marker_pos")
        lst = []
        for c, (mx, my) in ev.items():
            lst += [pl.probe((mx, my, top - 1.0), False, f"znacznik {c}"), pl.probe((mx, my, top - 3.3), True, f"znacznik {c}"), pl.probe((mx + 2.7, my, top - 1.0), True, f"znacznik {c}")]
        for (x, y) in ((-42, -42), (-42, 42), (42, 42)):
            lst.append(pl.probe((x, y, top - 1.0), True, "dawny róg"))
        # gniazdo id 2 (37,5, −15) ø12 i dawne gniazdo (−30, −40,5) ø9 ze starego układu → materiał
        lst += [pl.probe((37.5, -15, top - 2.0), False, "gniazdo id2"), pl.probe((0, -31.5, top - 2.0), False, "rynienka id1"), pl.probe((-30, -40.5, top - 2.0), True, "dawne gniazdo R1 (−30, −40,5)"),
                pl.probe((36, 1.5, top - 2.0), True if False else False, "gniazdo id8 (36, −1,5)? → to (36, 1,5): krawędź ø9 na −1,5 sięga do 3,0 → POZA")]
        nbad = sum(1 for e in lst if not e["ok"])
        vol = pl.volume()
        rec("INFO-plytka", "ramka_v2.blend", "ZAL" if nbad == 0 else "NIE",
            f"plytka_wieczorna_n1: wierzch w (0, −46,5) Z {zt}; objętość {vol:.3f} cm³ (STL n1 z sprawdz_R54: 59,313); bbox X[{pl.bb[0]:.2f},{pl.bb[1]:.2f}] Y[{pl.bb[2]:.2f},{pl.bb[3]:.2f}] Z[{pl.bb[4]:.2f},{pl.bb[5]:.2f}]; "
            f"sondy układu R54 (znaczniki w kole, dawne rogi pełne, gniazda nowe, stare miejsce gniazda pełne): {len(lst) - nbad}/{len(lst)}", "B", lst)
    # K-53
    shr = {n: shrunk_bvh(sol[n]) for n in assembled}
    names = sorted(assembled); pairs = []; bad = []; nall = 0
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]; nall += 1
            A, B = sol[a].bb, sol[b].bb
            if A[1] < B[0] or B[1] < A[0] or A[3] < B[2] or B[3] < A[2] or A[5] < B[4] or B[5] < A[4]:
                pairs.append((a, b, 0, "bbox rozłączne")); continue
            n = len(shr[a].overlap(shr[b]))
            pairs.append((a, b, n, "bbox wspólne"))
            if n:
                bad.append((a, b, n))
    sens = {}
    for a, b in (("blat", "korpus_W"), ("wkladka", "proxy_dyfuzor"), ("plytka_wieczorna_n1", "wkladka"), ("proxy_dystans_1", "korpus_W"), ("proxy_panel", "proxy_dystans_1"), ("tulejka_dc", "korpus_W"), ("proxy_gniazdo_dc", "tulejka_dc"), ("proxy_magnes_A", "plytka_wieczorna_n1")):
        if a in sol and b in sol:
            sens[f"{a}–{b}"] = len(sol[a].bvh.overlap(sol[b].bvh))
    key_pairs = {f"{a}–{b}": n for a, b, n, _ in pairs if {a, b} & {"plytka_wieczorna_n1", "pokrywka"} or (a.startswith("proxy_magnes") or b.startswith("proxy_magnes") or a.startswith("proxy_hall") or b.startswith("proxy_hall"))}
    rec("K-53", "ramka_v2.blend", "ZAL" if not bad else "NIE",
        f"obiektów {len(names)}, par {nall} (bbox wspólne {sum(1 for p in pairs if p[3] == 'bbox wspólne')}); par z przecięciem po skurczu 0,05: {len(bad)} {bad}; "
        f"pary z płytką n1 / pokrywką / magnesami / czujnikami: {key_pairs}; kontrola czułości bez skurczu (pary stykowe → >0 = test widzi styk): {sens}", "B",
        [{"para": f"{a}–{b}", "przeciec": n, "bbox": t, "ok": n == 0} for a, b, n, t in pairs])
    # K-55
    if "proxy_magnes_A" in sol and "proxy_hall_A" in sol:
        mg = sol["proxy_magnes_A"]; hl = sol["proxy_hall_A"]
        gap = mg.bb[4] - hl.bb[5]
        extra = {k: (round(sol[f"proxy_magnes_{k}"].bb[4] - sol[f"proxy_hall_{k}"].bb[5], 3) if f"proxy_magnes_{k}" in sol and f"proxy_hall_{k}" in sol else None) for k in "ABC"}
        cen = {k: (round((sol[f"proxy_magnes_{k}"].bb[0] + sol[f"proxy_magnes_{k}"].bb[1]) / 2, 2), round((sol[f"proxy_magnes_{k}"].bb[2] + sol[f"proxy_magnes_{k}"].bb[3]) / 2, 2)) for k in "ABC" if f"proxy_magnes_{k}" in sol}
        hcen = {k: (round((sol[f"proxy_hall_{k}"].bb[0] + sol[f"proxy_hall_{k}"].bb[1]) / 2, 2), round((sol[f"proxy_hall_{k}"].bb[2] + sol[f"proxy_hall_{k}"].bb[3]) / 2, 2)) for k in "ABC" if f"proxy_hall_{k}" in sol}
        rec("K-55", "ramka_v2.blend", "ZAL" if abs(gap - 1.2) <= 0.05 else "NIE",
            f"spód magnesu A {mg.bb[4]:.3f} − wierzch Halla A {hl.bb[5]:.3f} = {gap:.3f} (1,2 ± 0,05); +0,5 = {gap + 0.5:.2f} ≤ 4; szczeliny A/B/C {extra}; środki magnesów XY {cen}; środki czujników XY {hcen} (rogi ±42 — bez zmian po R54)", "B")
    else:
        rec("K-55", "ramka_v2.blend", "NIE", f"brak proxy_magnes_A / proxy_hall_A; obiekty: {sorted(sol)}", "B")
    # K-32 / K-22 z promieni w złożeniu: szczelina płytka–wkładka i płytka–pokrywka mierzona z punktu W SZCZELINIE na 4 bokach
    def gap(other, x, y, z, d):
        d = Vector(d)
        h_o = other.first_hit((x, y, z), d); h_p = pl.first_hit((x, y, z), -d)
        return None if (h_o is None or h_p is None) else (round((h_o - Vector((x, y, z))).length + (h_p - Vector((x, y, z))).length, 3), round((h_o - Vector((x, y, z))).length, 3), round((h_p - Vector((x, y, z))).length, 3))
    if pl is not None and "wkladka" in sol:
        wk = sol["wkladka"]; z = pl.bb[4] + 1.0
        res = {"+X": gap(wk, 48.2, 0, z, (1, 0, 0)), "-X": gap(wk, -48.2, 0, z, (-1, 0, 0)), "+Y": gap(wk, 0, 48.2, z, (0, 1, 0)), "-Y": gap(wk, 20, -48.2, z, (0, -1, 0))}
        exp_luz = (P("blat_rama_wkladka", "insert_opening") - 96) / 2
        ok = all(v is not None and abs(v[0] - exp_luz) <= 0.1 for v in res.values())
        n_pw = next((n for a_, b_, n, _ in pairs if {a_, b_} == {"plytka_wieczorna_n1", "wkladka"}), None)
        rec("K-32", "ramka_v2.blend", "ZAL" if (ok and n_pw == 0) else "NIE", f"szczelina płytka–wkładka na Z {z:.1f} (łącznie, do wkładki, do płytki od punktu ±48,2): {res}; oczek. {exp_luz}/stronę ± 0,1; para płytka–wkładka przecięć {n_pw}", "B")
    if pl is not None and "pokrywka" in sol:
        pk = sol["pokrywka"]; z = pl.bb[4] + 5.0
        res = {"+X": gap(pk, 48.15, 0, z, (1, 0, 0)), "-X": gap(pk, -48.15, 0, z, (-1, 0, 0)), "+Y": gap(pk, 20, 48.15, z, (0, 1, 0)), "-Y": gap(pk, 20, -48.15, z, (0, -1, 0))}
        n_pp = next((n for a_, b_, n, _ in pairs if {a_, b_} == {"plytka_wieczorna_n1", "pokrywka"}), None)
        ok = all(v is not None and abs(v[0] - 0.3) <= 0.1 for v in res.values()) and n_pp == 0
        rec("K-22", "ramka_v2.blend", "ZAL" if ok else "NIE", f"szczelina płytka–pokrywka na Z {z:.1f}: {res} (oczek. 0,3/stronę ± 0,1); min Z pokrywki {pk.bb[4]:.3f} vs wierzch ramy wkładki (0, 50,3) {round(sol['wkladka'].top_z(0, 50.3), 3)} (70,1 vs 69,6 → 0,5); para płytka–pokrywka przecięć {n_pp}", "B")
    # K-54 (wybrane)
    vals = {}
    def topz(n, x, y):
        return sol[n].top_z(x, y) if n in sol else None
    for k, (v, e) in {"blat (90,0)": (topz("blat", 90, 0), 63.6), "wkladka (0,50.3)": (topz("wkladka", 0, 50.3), 69.6), "plytka n1 (0,-46.5)": (topz("plytka_wieczorna_n1", 0, -46.5), 74.1),
                      "plytka n1 relief (39.5,-44.5)": (topz("plytka_wieczorna_n1", 39.5, -44.5), 74.7), "pokrywka (40,40)": (topz("pokrywka", 40, 40), 90.1),
                      "pokrywka min Z": (sol["pokrywka"].bb[4] if "pokrywka" in sol else None, 70.1), "plytka n1 min Z": (pl.bb[4] if pl else None, 66.1), "korpus_W max Z": (sol["korpus_W"].bb[5] if "korpus_W" in sol else None, 59.6)}.items():
        vals[k] = (round(v, 3) if v is not None else None, e)
    bad = {k: v for k, v in vals.items() if v[0] is None or abs(v[0] - v[1]) > 0.05}
    rec("K-54", "ramka_v2.blend", "ZAL" if not bad else "NIE", "; ".join(f"{k} {v[0]}/{v[1]}" for k, v in vals.items()) + (f"; NIEZGODNE {bad}" if bad else ""), "B")
    out = {"etap": "R54-C", "iteracja": ITER, "blender": bpy.app.version_string, "blend_sha256": sha, "wyniki": RESULTS}
    json.dump(out, open(os.path.join(REC, f"wyniki_R54_iter{ITER}_C.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    nie = [r for r in RESULTS if r["wynik"] == "NIE"]
    print(f"\n=== PODSUMOWANIE: {len(RESULTS)} sprawdzeń, NIE: {len(nie)}")

main()
