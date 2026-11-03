# -*- coding: utf-8 -*-
"""K-59 (R54): porównanie plików z czystego przebiegu (recenzja/powtorka_R54/wyniki_v2; kopia: ramka_generator.py, parametry.json,
plan_ramki_v2.md, protokol_weryfikacji_v2.md, BEZ wyniki_v2/ — JSON układów odtworzone z ev_rows/mo_rows) z wyniki_v2 —
SHA, kanonicznie (wierzchołki i trójkąty), objętość, gabaryt."""
import os, struct, hashlib, json, glob
A = r"<PC>\Desktop\Ramki\wyniki_v2"; B = r"<PC>\Desktop\Ramki\recenzja\powtorka_R54\wyniki_v2"
def read_stl(p):
    d = open(p, "rb").read()
    n = struct.unpack("<I", d[80:84])[0]
    tris = []; vol = 0.0; xs = []; ys = []; zs = []
    for i in range(n):
        o = 84 + 50 * i
        v = struct.unpack("<12f", d[o:o + 48])
        a, b, c = v[3:6], v[6:9], v[9:12]
        for q in (a, b, c):
            xs.append(q[0]); ys.append(q[1]); zs.append(q[2])
        vol += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0]) + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6.0
        key = tuple(sorted(tuple(round(x, 5) for x in q) for q in (a, b, c)))
        tris.append(key)
    tris.sort()
    return n, tris, vol / 1000.0, (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
out = {}
files = sorted(os.path.basename(p) for p in glob.glob(os.path.join(A, "stl", "*.stl")))
filesB = sorted(os.path.basename(p) for p in glob.glob(os.path.join(B, "stl", "*.stl")))
print("PLIKI", len(files), "POWTORKA", len(filesB), "brakuje:", sorted(set(files) - set(filesB)), "nadmiar:", sorted(set(filesB) - set(files)))
n_sha = n_tri = 0
for f in files:
    pa, pb = os.path.join(A, "stl", f), os.path.join(B, "stl", f)
    if not os.path.exists(pb):
        out[f] = {"status": "BRAK"}; print("BRAK", f); continue
    ha = hashlib.sha256(open(pa, "rb").read()).hexdigest(); hb = hashlib.sha256(open(pb, "rb").read()).hexdigest()
    na, ta, va, ga = read_stl(pa); nb, tb, vb, gb = read_stl(pb)
    same_tris = (ta == tb)
    sa, sb = set(ta), set(tb); diff = len(sa ^ sb)
    n_sha += (ha == hb); n_tri += same_tris
    out[f] = {"sha_rowne": ha == hb, "sha_wyniki": ha, "sha_powtorka": hb, "trojkaty_rowne": same_tris, "n": (na, nb), "roznych_trojkatow": diff,
              "objetosc": (round(va, 4), round(vb, 4)), "gabaryt": ([round(x, 3) for x in ga], [round(x, 3) for x in gb])}
    print(f"{'SHA=' if ha == hb else 'SHA≠'} {'TRI=' if same_tris else 'TRI≠'} {f}: n {na}/{nb}, różnych trójkątów {diff}, obj {va:.4f}/{vb:.4f}, gab {[round(x,3) for x in ga]}/{[round(x,3) for x in gb]}")
print(f"STL: SHA identyczne {n_sha}/{len(files)}, kanonicznie identyczne {n_tri}/{len(files)}")
for rel in ("json/uklad_gniazd_wieczorna.json", "json/uklad_gniazd_poranna.json", "arkusze/arkusz_zamowienia.csv", "arkusze/kody_plytek.md", "arkusze/arkusz_wymiarow.md", "arkusze/arkusz_zamowienia.md", "ramka_v2.blend", "render/render_rozstrzelony.png", "render/render_zlozony.png", "render/render_plytki.png", "README.md", "do_v3.md"):
    pa, pb = os.path.join(A, rel), os.path.join(B, rel)
    if os.path.exists(pa) and os.path.exists(pb):
        ha = hashlib.sha256(open(pa, "rb").read()).hexdigest(); hb = hashlib.sha256(open(pb, "rb").read()).hexdigest()
        print(f"INNE {'SHA=' if ha == hb else 'SHA≠'} {rel} ({os.path.getsize(pa)} / {os.path.getsize(pb)} B)")
        out[rel] = {"sha_rowne": ha == hb, "rozmiar": (os.path.getsize(pa), os.path.getsize(pb))}
    else:
        print("INNE BRAK", rel, os.path.exists(pa), os.path.exists(pb)); out[rel] = {"status": "BRAK"}
json.dump(out, open(r"<PC>\Desktop\Ramki\recenzja\wyniki_R54_iter1_K59.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
