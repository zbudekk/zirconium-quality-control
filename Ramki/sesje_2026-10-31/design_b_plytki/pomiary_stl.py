"""Pomiary STL płytek n1–n6 (i bazowych) oraz wkładki — niezależnie od generatora.
Uruchom (z katalogu Ramki): PYTHONUTF8=1 py -3.12 sesje_2026-10-31/design_b_plytki/pomiary_stl.py
Układ STL płytki: spód z=0, wierzch z=8, XY jak uklad.json (środek 0,0).
Metody: ray-casting (trimesh.ray) cięciw i trafień; profil stożków promieniami co 0,25 mm.
Wynik: pomiary_stl.json (surowe) — tabele w pomiary_stl.md.
"""
from __future__ import annotations
import json, math, sys, hashlib
from pathlib import Path
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[2]
STL = ROOT / "wyniki_v2" / "stl"
OUT = Path(__file__).resolve().parent
Z_TOP = 8.0


def load(name):
    return trimesh.load(STL / name, force="mesh")


def ray(mesh, origin, direction):
    o = np.array([origin], float); d = np.array([direction], float)
    loc, idx, _ = mesh.ray.intersects_location(o, d, multiple_hits=False)
    if len(loc) == 0:
        return None
    return loc[0]


def chord(mesh, p, axis):
    d = np.zeros(3); d[axis] = 1
    a = ray(mesh, p, d); b = ray(mesh, p, -d)
    if a is None or b is None:
        return None, a, b
    return float(a[axis] - b[axis]), a, b


def depth_down(mesh, x, y, z0=Z_TOP + 5):
    h = ray(mesh, (x, y, z0), (0, 0, -1))
    return None if h is None else float(h[2])


def outer(mesh, p, axis):
    d = np.zeros(3); d[axis] = 1
    lo = np.array(p, float); lo[axis] = -500
    hi = np.array(p, float); hi[axis] = 500
    a = ray(mesh, lo, d); b = ray(mesh, hi, -d)
    if a is None or b is None:
        return None
    return float(b[axis] - a[axis])


def cone_profile(mesh, cx, cy, r_max=3.0, step=0.25):
    prof = []
    for r in np.arange(0, r_max + 1e-9, step):
        z = depth_down(mesh, cx + r, cy)
        prof.append((round(float(r), 3), None if z is None else round(z, 4)))
    return prof


def socket_measure(mesh, s):
    res = {"id": s["id"], "type": s["type"], "x": s["x"], "y": s["y"]}
    x, y = s["x"], s["y"]
    if s["type"] == "round":
        for zname, z in (("top", Z_TOP - 0.05), ("bottom", Z_TOP - s["depth"] + 0.05), ("mid", Z_TOP - 2)):
            cx, _, _ = chord(mesh, (x, y, z), 0)
            cy, _, _ = chord(mesh, (x, y, z), 1)
            res[f"d_{zname}_x"] = cx; res[f"d_{zname}_y"] = cy
        _, a, b = chord(mesh, (x, y, Z_TOP - 0.05), 0)
        _, c, d = chord(mesh, (x, y, Z_TOP - 0.05), 1)
        if a is not None and c is not None:
            res["cx_meas"] = float((a[0] + b[0]) / 2); res["cy_meas"] = float((c[1] + d[1]) / 2)
        off = s["d_bottom"] / 2 - 0.4
        res["z_floor"] = depth_down(mesh, x + off, y)
        res["hole_d"], _, _ = chord(mesh, (x, y, 2.0), 0)
        res["hole_through"] = depth_down(mesh, x, y) is None
        if res.get("d_top_x") and res.get("d_bottom_x"):
            res["wall_angle_deg"] = math.degrees(math.atan(((res["d_top_x"] - res["d_bottom_x"]) / 2) / 3.9))
    else:
        for zname, z in (("top", Z_TOP - 0.05), ("bottom", Z_TOP - s["depth"] + 0.05)):
            cl, _, _ = chord(mesh, (x, y, z), 0)
            cw, _, _ = chord(mesh, (x + 2.0, y, z), 1)
            res[f"l_{zname}"] = cl; res[f"w_{zname}"] = cw
        res["z_floor"] = depth_down(mesh, x + s["hole_pitch"] / 2, y + s["w"] / 2 - 1.5)
        n = s["hole_count"]; p = s["hole_pitch"]
        xs = [(-(n - 1) / 2 + i) * p for i in range(n)]
        holes = []
        for hx in xs:
            z = depth_down(mesh, x + hx, y)
            dd, _, _ = chord(mesh, (x + hx, y, 2.0), 1)
            holes.append({"x": hx, "through": z is None, "d": dd})
        res["holes"] = holes
    return res


def wall_between(mesh, p1, p2, z):
    p1 = np.array([p1[0], p1[1], z]); p2 = np.array([p2[0], p2[1], z])
    d = p2 - p1; d /= np.linalg.norm(d)
    a = ray(mesh, p1, d); b = ray(mesh, p2, -d)
    if a is None or b is None:
        return None
    return float(np.linalg.norm(b - a))


def measure_plate(name, uk):
    m = load(name)
    r = {"file": name, "watertight": bool(m.is_watertight), "volume_cm3": float(m.volume) / 1000,
         "bbox_min": m.bounds[0].round(4).tolist(), "bbox_max": m.bounds[1].round(4).tolist(),
         "faces": int(len(m.faces))}
    r["size_x"] = outer(m, (0, 20, 4), 0); r["size_y"] = outer(m, (20, 0, 4), 1)
    r["thickness_at"] = {f"({x},{y})": outer(m, (x, y, 4), 2) for x, y in ((0, -46.5), (46.5, 0), (-46.5, 20), (0, 46.5), (-20, -46.5))}
    pts = [(x, y) for x in (-46.5, -20, 0, 20, 46.5) for y in (-46.5, 46.5)] + [(-46.5, y) for y in (-20, 0, 20)] + [(46.5, y) for y in (-20, 0, 20)]
    zs = [depth_down(m, x, y) for x, y in pts]
    zs = [z for z in zs if z is not None]
    r["top_flatness"] = {"n": len(zs), "min": min(zs), "max": max(zs)}
    zb = []
    for x, y in pts:
        h = ray(m, (x, y, -5), (0, 0, 1)); zb.append(None if h is None else float(h[2]))
    zb = [z for z in zb if z is not None]
    r["bottom_flatness"] = {"n": len(zb), "min": min(zb), "max": max(zb)}
    r["markers"] = []
    for mk in uk["markers"]:
        cx, cy = mk["x"], mk["y"]
        dtop, _, _ = chord(m, (cx, cy, Z_TOP - 0.05), 0)
        dtop_y, _, _ = chord(m, (cx, cy, Z_TOP - 0.05), 1)
        zap = depth_down(m, cx, cy)
        prof = cone_profile(m, cx, cy, 3.0, 0.25)
        pr = [(rr, Z_TOP - zz) for rr, zz in prof if zz is not None and 0.2 < Z_TOP - zz < 2.8]
        ang = None
        if len(pr) >= 2:
            rs = np.array([p[0] for p in pr]); ds = np.array([p[1] for p in pr])
            k = np.polyfit(ds, rs, 1)[0]
            ang = math.degrees(math.atan(k))
        _, a, b = chord(m, (cx, cy, Z_TOP - 1.0), 0); _, c, d = chord(m, (cx, cy, Z_TOP - 1.0), 1)
        cm = None
        if a is not None and c is not None:
            cm = [float((a[0] + b[0]) / 2), float((c[1] + d[1]) / 2)]
        r["markers"].append({"corner": mk["corner"], "nominal": [cx, cy], "d_top_x": dtop, "d_top_y": dtop_y,
                             "apex_z": zap, "depth": None if zap is None else Z_TOP - zap,
                             "half_angle_deg": ang, "center_meas_z7": cm, "profile": prof})
    r["notch"] = {"through": depth_down(m, 45.5, -45.5) is None}
    h = ray(m, (40, -45.5, 4), (1, 0, 0)); r["notch"]["x_min_meas"] = None if h is None else float(h[0])
    h = ray(m, (45.5, -40, 4), (0, -1, 0)); r["notch"]["y_max_meas"] = None if h is None else float(h[1])
    r["code_dimples"] = []
    for cd in uk["code_dimples"]:
        z = depth_down(m, cd["x"], cd["y"])
        dd, a, b = chord(m, (cd["x"], cd["y"], Z_TOP - 0.5), 0)
        ddy, _, _ = chord(m, (cd["x"], cd["y"], Z_TOP - 0.5), 1)
        cxm = None if a is None else float((a[0] + b[0]) / 2)
        r["code_dimples"].append({"bit": cd["bit"], "nominal": [cd["x"], cd["y"]], "z_floor": z,
                                  "depth": None if z is None else Z_TOP - z, "present": z is not None and Z_TOP - z > 0.5,
                                  "d_x": dd, "d_y": ddy, "cx_meas": cxm,
                                  "floor_at_r0.6": depth_down(m, cd["x"] + 0.6, cd["y"])})
    r["magnet_pockets"] = []
    for mp in uk["magnet_pockets"]:
        h = ray(m, (mp["x"], mp["y"], -2), (0, 0, 1))
        dd, _, _ = chord(m, (mp["x"], mp["y"], 1.0), 0)
        r["magnet_pockets"].append({"corner": mp["corner"], "ceiling_z": None if h is None else float(h[2]), "d": dd,
                                    "material_to_cone_apex": None if h is None else (Z_TOP - 3.0) - float(h[2])})
    nr = uk["number_relief"]
    zmax = float(m.bounds[1][2])
    r["number_relief"] = {"zmax_file": zmax, "relief_h": zmax - Z_TOP, "sample_z_center": depth_down(m, nr["x"], nr["y"], 12)}
    h = ray(m, (60, 20, Z_TOP - 2), (-1, 0, 0)); r["cover_groove"] = {"floor_x": None if h is None else float(h[0])}
    gz = []
    for z in np.arange(Z_TOP - 3.5, Z_TOP - 0.5, 0.05):
        h = ray(m, (60, 20, z), (-1, 0, 0)); gz.append((round(float(z), 3), None if h is None else round(float(h[0]), 3)))
    inside = [z for z, xx in gz if xx is not None and xx < 47.9]
    r["cover_groove"]["z_range"] = [min(inside), max(inside)] if inside else None
    r["sockets"] = [socket_measure(m, s) for s in uk["sockets"]]
    walls = []
    rs = [s for s in uk["sockets"] if s["type"] == "round"]
    for i, a in enumerate(rs):
        for b in rs[i + 1:]:
            dist = math.hypot(a["x"] - b["x"], a["y"] - b["y"])
            nominal = dist - a["d_top"] / 2 - b["d_top"] / 2
            if nominal < 3.6:
                w = wall_between(m, (a["x"], a["y"]), (b["x"], b["y"]), Z_TOP - 0.05)
                walls.append({"a": a["id"], "b": b["id"], "nominal": round(nominal, 3), "meas": w})
    tr = [s for s in uk["sockets"] if s["type"] == "trough"]
    for a in rs:
        for t in tr:
            nominal = abs(t["y"] - a["y"]) - t["w"] / 2 - a["d_top"] / 2
            if nominal < 3.6 and abs(a["x"]) < t["l"] / 2 - t["w"] / 2:
                w = wall_between(m, (a["x"], a["y"]), (a["x"], t["y"]), Z_TOP - 0.05)
                walls.append({"a": a["id"], "b": t["id"], "nominal": round(nominal, 3), "meas": w})
    if len(tr) == 2:
        w = wall_between(m, (0, tr[0]["y"]), (0, tr[1]["y"]), Z_TOP - 0.05)
        walls.append({"a": tr[0]["id"], "b": tr[1]["id"], "nominal": round(abs(tr[1]["y"] - tr[0]["y"]) - tr[0]["w"], 3), "meas": w})
    r["walls"] = walls
    edge = []
    for s in rs:
        for ax in (0, 1):
            c = s["x"] if ax == 0 else s["y"]
            if c == 0:
                continue
            sgn = 1 if c > 0 else -1
            nominal = 48 - abs(c) - s["d_top"] / 2
            if nominal < 5:
                p = [s["x"], s["y"], Z_TOP - 0.05]; d = [0.0, 0.0, 0.0]; d[ax] = sgn
                hit = ray(m, p, d)
                far = [s["x"], s["y"], Z_TOP - 0.05]; far[ax] = sgn * 60
                hit2 = ray(m, far, [-v for v in d])
                if hit is not None and hit2 is not None:
                    edge.append({"id": s["id"], "axis": "xy"[ax], "nominal": round(nominal, 3), "meas": float(abs(hit2[ax] - hit[ax]))})
    r["socket_to_edge"] = edge
    h1 = ray(m, (-45, -36, Z_TOP - 0.5), (-1, 0, 0)); h2 = ray(m, (-60, -36, Z_TOP - 0.5), (1, 0, 0))
    r["dimple_A_to_edge"] = None if h1 is None or h2 is None else float(abs(h2[0] - h1[0]))
    hA = ray(m, (-45, -36, Z_TOP - 0.5), (0.4472, -0.8944, 0)); hB = ray(m, (-42, -42, Z_TOP - 0.5), (-0.4472, 0.8944, 0))
    r["dimple_A_to_cone_A"] = None if hA is None or hB is None else float(np.linalg.norm(hA - hB))
    # najbliższe gniazdo do dołków (ścianka): gniazdo z min odległości
    near = min(rs, key=lambda s: math.hypot(s["x"] + 45, s["y"] + 33) - s["d_top"] / 2)
    r["dimple_nearest_socket"] = {"id": near["id"], "nominal_wall": math.hypot(near["x"] + 45, near["y"] + 33) - near["d_top"] / 2 - 1.0}
    return r


def measure_insert():
    m = load("ramka_wkladka_v2.stl")
    r = {"file": "ramka_wkladka_v2.stl", "watertight": bool(m.is_watertight), "bbox_min": m.bounds[0].round(3).tolist(), "bbox_max": m.bounds[1].round(3).tolist()}
    r["opening_x"], _, _ = chord(m, (0, 0, 4), 0); r["opening_y"], _, _ = chord(m, (20, 0, 4), 1)
    r["opening_x_at_y40"], _, _ = chord(m, (0, 40, 4), 0); r["opening_x_at_ym40"], _, _ = chord(m, (0, -40, 4), 0)
    r["opening_y_at_x40"], _, _ = chord(m, (40, 0, 4), 1); r["opening_y_at_xm40"], _, _ = chord(m, (-40, 0, 4), 1)
    r["outer_x"] = outer(m, (0, 0, 4), 0)
    r["frame_h"] = outer(m, (-40, -50.3, 3), 2)
    r["shelf_top_z"] = {c: depth_down(m, x, y, 20) for c, (x, y) in {"A": (-38, -38), "B": (-38, 38), "C": (38, 38), "D": (38, -38)}.items()}
    hx1 = ray(m, (40, -45.6, 5), (1, 0, 0)); hx2 = ray(m, (48.2, -45.6, 5), (-1, 0, 0))
    hy1 = ray(m, (45.6, -40, 5), (0, -1, 0)); hy2 = ray(m, (45.6, -48.2, 5), (0, 1, 0))
    r["post"] = {"x_min": float(hx1[0]), "x_max": float(hx2[0]), "y_max": float(hy1[1]), "y_min": float(hy2[1]), "top_z": depth_down(m, 45.6, -45.6, 20)}
    r["hall_pockets"] = {}
    for c, (x, y) in {"A": (-42, -42), "B": (-42, 42), "C": (42, 42)}.items():
        cx, _, _ = chord(m, (x, y, 1.5), 0); cy, _, _ = chord(m, (x, y, 1.5), 1)
        r["hall_pockets"][c] = {"x": cx, "y": cy, "through": depth_down(m, x, y, 20) is None}
    prof = []
    for z in np.arange(4.0, 6.01, 0.1):
        h = ray(m, (0, 20, z), (1, 0, 0)); prof.append((round(float(z), 2), None if h is None else round(float(h[0]), 3)))
    r["chamfer_profile"] = prof
    r["post_at_B_z"] = depth_down(m, -45.6, 45.6, 20)
    r["post_at_A_z"] = depth_down(m, -45.6, -45.6, 20)
    r["post_at_C_z"] = depth_down(m, 45.6, 45.6, 20)
    return r


def main():
    out = {}
    plates = {"wieczorna": ["ramka_plytka_wieczorna_v2.stl"] + [f"ramka_plytka_wieczorna_n{i}_v2.stl" for i in (1, 2, 3)],
              "poranna": ["ramka_plytka_poranna_v2.stl"] + [f"ramka_plytka_poranna_n{i}_v2.stl" for i in (4, 5, 6)]}
    for typ, files in plates.items():
        uk = json.loads((ROOT / "stanowisko" / "modele_plytek" / typ / "uklad.json").read_text("utf-8"))
        for f in files:
            print("mierzę", f, file=sys.stderr)
            out[f] = measure_plate(f, uk)
    print("mierzę wkładkę", file=sys.stderr)
    out["ramka_wkladka_v2.stl"] = measure_insert()
    hs = {}
    for typ, nums in (("wieczorna", (1, 2, 3)), ("poranna", (4, 5, 6))):
        for n in nums:
            a = (ROOT / "stanowisko" / "modele_plytek" / typ / f"plytka_n{n}.stl").read_bytes()
            b = (STL / f"ramka_plytka_{typ}_n{n}_v2.stl").read_bytes()
            hs[f"n{n}"] = {"sha_modele": hashlib.sha256(a).hexdigest()[:16], "sha_wyniki": hashlib.sha256(b).hexdigest()[:16], "identical": a == b}
    out["_stl_identity"] = hs
    (OUT / "pomiary_stl.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float), "utf-8")
    print("zapisano pomiary_stl.json")


if __name__ == "__main__":
    main()
