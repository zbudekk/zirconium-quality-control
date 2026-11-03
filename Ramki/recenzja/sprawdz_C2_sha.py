# -*- coding: utf-8 -*-
"""C iter2: SHA wszystkich plików z raportu C2 vs dysk; SHA STL vs raport C1; kanonicznie (trójkąty) vs czysta kopia C1 (recenzja/powtorka)."""
import os, re, struct, hashlib, json, glob
R = r"<PC>\Desktop\Ramki"; WYN = os.path.join(R, "wyniki_v2"); POW = os.path.join(R, "recenzja", "powtorka", "wyniki_v2")
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def tab(path):
    out = {}
    for ln in open(path, encoding="utf-8"):
        m = re.match(r"\| `([^`]+)` \| (\d+) \| `([0-9a-f]{64})` \|", ln)
        if m: out[m.group(1)] = (int(m.group(2)), m.group(3))
    return out
c1 = tab(os.path.join(WYN, "raport", "raport_wykonawcy_C_iter1.md")); c2 = tab(os.path.join(WYN, "raport", "raport_wykonawcy_C_iter2.md"))
print("wierszy C1", len(c1), "C2", len(c2))
res = {"raport_vs_dysk": {}, "stl_vs_C1": {}, "kanonicznie_vs_powtorka": {}}
bad = []
for f, (sz, h) in c2.items():
    p = os.path.join(WYN, f)
    ok = os.path.exists(p) and os.path.getsize(p) == sz and sha(p) == h
    res["raport_vs_dysk"][f] = ok
    if not ok: bad.append(f)
print("RAPORT C2 vs DYSK:", "wszystkie zgodne" if not bad else bad)
def read_stl(p):
    d = open(p, "rb").read(); n = struct.unpack("<I", d[80:84])[0]; tris = []; vol = 0.0
    for i in range(n):
        o = 84 + 50 * i; v = struct.unpack("<12f", d[o:o + 48]); a, b, c = v[3:6], v[6:9], v[9:12]
        vol += (a[0]*(b[1]*c[2]-b[2]*c[1]) - a[1]*(b[0]*c[2]-b[2]*c[0]) + a[2]*(b[0]*c[1]-b[1]*c[0])) / 6.0
        tris.append(tuple(sorted(tuple(round(x, 5) for x in q) for q in (a, b, c))))
    tris.sort(); return n, tris, vol / 1000.0
for f in sorted(k for k in c2 if k.endswith(".stl")):
    same_sha = c1.get(f, (None, None))[1] == c2[f][1]
    na, ta, va = read_stl(os.path.join(WYN, f)); nb, tb, vb = read_stl(os.path.join(POW, f))
    same_tri = ta == tb; diff = len(set(ta) ^ set(tb))
    res["stl_vs_C1"][f] = same_sha
    res["kanonicznie_vs_powtorka"][f] = {"trojkaty_rowne": same_tri, "n": (na, nb), "roznych": diff, "objetosc": (round(va, 4), round(vb, 4))}
    print(f"{'SHA=C1' if same_sha else 'SHA!=C1'} {'TRI=' if same_tri else 'TRI!='} {f}: n {na}/{nb}, roznych {diff}, obj {va:.4f}/{vb:.4f}")
for f in sorted(k for k in c2 if not k.endswith(".stl")):
    print(f"{'SHA=C1' if c1.get(f, (None, None))[1] == c2[f][1] else 'SHA!=C1'} {f}")
    res["stl_vs_C1"][f] = c1.get(f, (None, None))[1] == c2[f][1]
json.dump(res, open(os.path.join(R, "recenzja", "wyniki_C_iter2_sha.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
