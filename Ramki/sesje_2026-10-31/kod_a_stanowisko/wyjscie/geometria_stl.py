"""Sprawdzenie zgodności uklad.json z geometrią plytka_n*.stl i z ../parametry.json."""
import json, hashlib, sys, math
from pathlib import Path
import numpy as np, trimesh
R = Path(r"<PC>/Desktop/Ramki")
S = R / "stanowisko"
par = json.load(open(R/"parametry.json", encoding="utf-8"))["plytka"]
def val(k): return par[k]["value"]
for nazwa, rows_key, nums_key in [("wieczorna","ev_rows","plate_numbers_ev"),("poranna","mo_rows","plate_numbers_mo")]:
    uk = json.load(open(S/"modele_plytek"/nazwa/"uklad.json", encoding="utf-8"))
    print(f"=== {nazwa} ===")
    # parametry.json rows -> lista gniazd
    oczek = []
    for r in val(rows_key):
        for x in r["x"]:
            oczek.append((r["type"], x, r["y"], r.get("d"), r.get("l"), r.get("w")))
    got = [(s["type"], s["x"], s["y"], s.get("d_top"), s.get("l"), s.get("w")) for s in uk["sockets"]]
    print("gniazda parametry.json vs uklad.json:", "ZGODNE" if sorted(map(str,oczek))==sorted(map(str,got)) else "ROZNE")
    # d_bottom = d_top - 2*depth*tan(15)
    for s in uk["sockets"]:
        if s["type"]=="round":
            db = s["d_top"] - 2*s["depth"]*math.tan(math.radians(val("socket_wall_angle")))
            if abs(db - s["d_bottom"])>0.01: print("  d_bottom niezgodne", s["id"], db, s["d_bottom"])
        assert s["depth"]==val("socket_depth")
    # dołki kodu
    dc = uk["code_dimples"]
    for i,d in enumerate(dc):
        assert d["x"]==val("code_dimple_x") and d["y"]==val("code_dimple_y0")+i*val("code_dimple_pitch"), d
    print("dołki kodu zgodne z parametry.json; markers:", [(m["x"],m["y"]) for m in uk["markers"]], "offset", val("marker_offset"))
    for n in val(nums_key):
        p = S/"modele_plytek"/nazwa/f"plytka_n{n}.stl"
        ref = R/"wyniki_v2"/"stl"/f"ramka_plytka_{nazwa}_n{n}_v2.stl"
        same = hashlib.sha256(p.read_bytes()).hexdigest()==hashlib.sha256(ref.read_bytes()).hexdigest()
        m = trimesh.load(p, force="mesh")
        V = m.vertices
        print(f"-- n{n}: trójkątów {len(m.faces)}, watertight={m.is_watertight}, identyczny z wyniki_v2={same}")
        print("   bounds x", V[:,0].min(), V[:,0].max(), " y", V[:,1].min(), V[:,1].max(), " z", V[:,2].min(), V[:,2].max())
        # gniazda: wierzchołki w promieniu d_top/2+0.3 od środka, z-min
        bad=0
        for s in uk["sockets"]:
            if s["type"]=="round":
                rr = np.hypot(V[:,0]-s["x"], V[:,1]-s["y"])
                sel = (rr < s["d_top"]/2 + 0.05) & (rr > s["hole_d"]/2 + 0.2)
                zmin = V[sel,2].min(); zmax=V[sel,2].max()
                # pierścień górny: wierzchołki z~8 ; promień max
                gora = V[(sel)&(np.abs(V[:,2]-8)<1e-3)]
                rg = np.hypot(gora[:,0]-s["x"],gora[:,1]-s["y"]).max() if len(gora) else float('nan')
                dol = V[(sel)&(np.abs(V[:,2]-4)<1e-3)]
                rd = np.hypot(dol[:,0]-s["x"],dol[:,1]-s["y"]).max() if len(dol) else float('nan')
                ok = abs(zmin-4)<1e-3 and abs(rg*2-s["d_top"])<0.05 and abs(rd*2-s["d_bottom"])<0.05
                if not ok: bad+=1; print("   gniazdo", s["id"], "zmin",zmin,"d_top_stl",2*rg,"d_bot_stl",2*rd)
            else:
                a=math.radians(s["angle"]); dx=V[:,0]-s["x"]; dy=V[:,1]-s["y"]
                u=dx*math.cos(a)+dy*math.sin(a); v=-dx*math.sin(a)+dy*math.cos(a)
                sel=(np.abs(u)<s["l"]/2+0.05)&(np.abs(v)<s["w"]/2+0.05)
                dno = sel & (np.abs(V[:,2]-4)<1e-3)
                if not dno.any(): bad+=1; print("   rynienka", s["id"], "brak dna na z=4")
                else:
                    print(f"   rynienka {s['id']}: dno z=4 OK, obrys dna u±{np.abs(u[dno]).max():.2f} v±{np.abs(v[dno]).max():.2f} (oczek. {s['l']/2-4*math.tan(math.radians(15)):.2f} / {s['w']/2-4*math.tan(math.radians(15)):.2f})")
        print("   gniazda okrągłe niezgodne:", bad)
        # znaczniki: stożek ø5 gł. 3 -> z min 5 przy środku
        for mk in uk["markers"]:
            rr=np.hypot(V[:,0]-mk["x"],V[:,1]-mk["y"]); sel=rr<mk["d"]/2+0.05
            zs=V[sel,2]; zs=zs[zs>4.5]
            print(f"   znacznik {mk['corner']}: zmin={zs.min():.3f} (oczek 5.0), r_top={np.hypot(V[sel&(np.abs(V[:,2]-8)<1e-3),0]-mk['x'],V[sel&(np.abs(V[:,2]-8)<1e-3),1]-mk['y']).max():.3f}")
        # dołki kodu obecne?
        bits=[]
        for d in dc:
            rr=np.hypot(V[:,0]-d["x"],V[:,1]-d["y"]); sel=(rr<d["d"]/2+0.05)&(V[:,2]>6.5)&(V[:,2]<7.999)
            bits.append(bool(sel.any()))
        kod = int(bits[0])+2*int(bits[1])+4*int(bits[2])
        print(f"   dołki kodu w STL: A={bits[0]} B={bits[1]} C={bits[2]} -> n={kod} {'OK' if kod==n else 'BLAD'}")
        # wycięcie D
        nt=uk["notch"]; sel=(V[:,0]>nt["x_min"]-0.01)&(V[:,1]<nt["y_max"]+0.01)
        print(f"   wycięcie D: wierzchołków w obszarze {sel.sum()} (obszar powinien być pusty poza krawędziami)")
        # relief numeru
        nr=uk["number_relief"]; sel=(np.abs(V[:,0]-nr["x"])<5)&(np.abs(V[:,1]-nr["y"])<4)
        print(f"   relief numeru: zmax={V[sel,2].max():.2f} (oczek 8.6)")
