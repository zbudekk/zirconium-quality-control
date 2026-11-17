# -*- coding: utf-8 -*-
"""
Recenzent R59 - modul wspolny (bez bpy, bez numpy): model OCZEKIWANY plytki liczony wylacznie z parametry.json
(rzedy ev_rows / mo_rows, *_marker_pos, code_dimples_round, number_pos_round, klucze geometrii gniazd) oraz
funkcje odleglosci obrysow. Nie czyta JSON ukladu ani niczego z generatora.
Uzywany przez: sprawdz_R59_liczby.py (python), sprawdz_R59.py i sprawdz_R59_K53.py (Blender).
"""
import json
import math


def wczytaj(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def P(par, key, sec="plytka"):
    return par[sec][key]["value"]


# ---------- geometria 2D ----------
def pt_seg(p, a, b):
    ax, ay = a
    bx, by = b
    px, py = p
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    if L2 < 1e-18:
        return math.hypot(px - ax, py - ay)
    t = ((px - ax) * dx + (py - ay) * dy) / L2
    t = max(0.0, min(1.0, t))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def _orient(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def seg_przeciecie(a, b, c, d):
    o1 = _orient(a, b, c)
    o2 = _orient(a, b, d)
    o3 = _orient(c, d, a)
    o4 = _orient(c, d, b)
    return (o1 * o2 < 0) and (o3 * o4 < 0)


def seg_seg(a, b, c, d):
    if seg_przeciecie(a, b, c, d):
        return 0.0
    return min(pt_seg(a, c, d), pt_seg(b, c, d), pt_seg(c, a, b), pt_seg(d, a, b))


class Cecha(object):
    """Obrys gorny cechy jako 'kapsula': odcinek p0-p1 pogrubiony o r (okrag: p0 == p1)."""

    def __init__(self, rodzaj, nazwa, p0, p1, r, **kw):
        self.rodzaj = rodzaj      # 'round' | 'trough' | 'marker' | 'dimple'
        self.nazwa = nazwa
        self.p0 = (float(p0[0]), float(p0[1]))
        self.p1 = (float(p1[0]), float(p1[1]))
        self.r = float(r)
        self.x = (self.p0[0] + self.p1[0]) / 2.0
        self.y = (self.p0[1] + self.p1[1]) / 2.0
        for k, v in kw.items():
            setattr(self, k, v)

    def sd(self, p):
        """odleglosc ze znakiem punktu od obrysu gornego (ujemna = wewnatrz)"""
        return pt_seg(p, self.p0, self.p1) - self.r

    def odstep(self, inna):
        return seg_seg(self.p0, self.p1, inna.p0, inna.p1) - self.r - inna.r

    def max_promien(self):
        return max(math.hypot(*self.p0), math.hypot(*self.p1)) + self.r

    def max_abs_x(self):
        return max(abs(self.p0[0]), abs(self.p1[0])) + self.r

    def max_abs_y(self):
        return max(abs(self.p0[1]), abs(self.p1[1])) + self.r

    def opis(self):
        if self.rodzaj == "round":
            return "%s fi%g (%g; %g)" % (self.nazwa, 2 * self.r, self.x, self.y)
        if self.rodzaj == "trough":
            return "%s rynienka %gx%g (%g; %g)" % (self.nazwa, self.l, self.w, self.x, self.y)
        return "%s %s (%g; %g)" % (self.rodzaj, self.nazwa, self.x, self.y)


def odl_prostokat_cecha(rect, c):
    """rect = (x0, x1, y0, y1); odleglosc prostokata (pelnego) od obrysu cechy (kapsuly); 0 gdy sie nakladaja"""
    x0, x1, y0, y1 = rect
    rogi = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    # srodek odcinka kapsuly w prostokacie?
    for p in (c.p0, c.p1):
        if x0 <= p[0] <= x1 and y0 <= p[1] <= y1:
            return 0.0
    d = min(seg_seg(rogi[i], rogi[(i + 1) % 4], c.p0, c.p1) for i in range(4))
    return max(0.0, d - c.r)


class Model(object):
    """Model oczekiwany plytki: typ 'wieczorna' | 'poranna', ksztalt 'kwadrat' | 'okragla'."""

    def __init__(self, par, typ, ksztalt):
        self.par = par
        self.typ = typ
        self.ksztalt = ksztalt
        pre = "ev" if typ == "wieczorna" else "mo"
        self.rows = P(par, pre + "_rows")
        self.gr = P(par, "plate_thickness")
        self.glebokosc = P(par, "socket_depth")
        self.kat = math.radians(P(par, "socket_wall_angle"))
        self.tan = math.tan(self.kat)
        self.otwor_d = P(par, "socket_hole_d")
        self.zone_r = P(par, "socket_zone_r")
        self.zone = P(par, "socket_zone")
        self.wall_min = P(par, "socket_wall_min")
        self.faza = P(par, "plate_top_chamfer")
        self.bok = P(par, "plate_size")
        self.rog_r = P(par, "plate_edge_r")
        self.rog_strefa = P(par, "plate_corner_zone")
        self.marker_d = P(par, "marker_cone_d")
        self.marker_gl = P(par, "marker_cone_depth")
        self.dolek_d = P(par, "code_dimple_d")
        self.dolek_gl = P(par, "code_dimple_depth")
        self.relief_h = P(par, "number_relief_h")
        self.cyfra_h = P(par, "number_text_h")
        self.trough_pitch = P(par, pre + "_trough_hole_pitch")
        self.trough_n = P(par, "trough_hole_count")
        self.R = P(par, "plate_round_d") / 2.0
        self.flat_w = P(par, "round_flat_w")
        self.flat_ang = math.radians(P(par, "round_flat_angle"))
        self.flat_dist = math.sqrt(self.R ** 2 - (self.flat_w / 2.0) ** 2)
        self.flat_n = (math.cos(self.flat_ang), math.sin(self.flat_ang))
        self.flat_depth_min = P(par, "round_flat_depth_min")
        # gniazda: wpisy rzedow po y (od przodu), we wpisie malejace x; id 1..N
        self.gniazda = []
        wpisy = sorted(enumerate(self.rows), key=lambda t: (t[1]["y"], t[0]))
        i = 0
        for nr, row in wpisy:
            for x in sorted(row["x"], reverse=True):
                i += 1
                if row["type"] == "round":
                    c = Cecha("round", "id%d" % i, (x, row["y"]), (x, row["y"]), row["d"] / 2.0, id=i, d=row["d"],
                              wpis=nr, glebokosc=self.glebokosc)
                else:
                    h = (row["l"] - row["w"]) / 2.0
                    c = Cecha("trough", "id%d" % i, (x - h, row["y"]), (x + h, row["y"]), row["w"] / 2.0, id=i,
                              l=row["l"], w=row["w"], wpis=nr, glebokosc=self.glebokosc,
                              pitch=self.trough_pitch, n_otw=self.trough_n)
                self.gniazda.append(c)
        mp = P(par, pre + "_marker_pos")
        self.znaczniki = [Cecha("marker", k, mp[k], mp[k], self.marker_d / 2.0, glebokosc=self.marker_gl) for k in "ABC"]
        if ksztalt == "kwadrat":
            x = P(par, "code_dimple_x")
            y0 = P(par, "code_dimple_y0")
            pt = P(par, "code_dimple_pitch")
            dp = {"A": (x, y0), "B": (x, y0 + pt), "C": (x, y0 + 2 * pt), "D": tuple(P(par, "code_bit_d_pos"))}
            self.cyfra = (P(par, "number_pos_x"), P(par, "number_pos_y"))
            self.numery = P(par, "plate_numbers_ev" if typ == "wieczorna" else "plate_numbers_mo")
            mo = self.bok / 2.0 - P(par, "marker_offset")
            self.magnesy = {"A": (-mo, -mo), "B": (-mo, mo), "C": (mo, mo)}
            self.magnes_d = P(par, "magnet_pocket_d")
            self.magnes_gl = P(par, "magnet_pocket_depth")
            ns = P(par, "notch_size")
            hb = self.bok / 2.0
            self.wyciecie = (hb - ns, hb, -hb, -hb + ns)   # x0, x1, y0, y1
        else:
            d = P(par, "code_dimples_round")[typ]
            dp = dict((k, tuple(d[k])) for k in "ABCD")
            c = P(par, "number_pos_round")[typ]
            self.cyfra = None if c is None else tuple(c)
            self.numery = P(par, "plate_numbers_round")[typ]
            self.magnesy = {}
            self.magnes_d = P(par, "magnet_pocket_d")
            self.magnes_gl = P(par, "magnet_pocket_depth")
            self.wyciecie = None
        self.dolki = dict((k, Cecha("dimple", k, dp[k], dp[k], self.dolek_d / 2.0, glebokosc=self.dolek_gl)) for k in "ABCD")

    # --- zestawy cech ---
    def otwory(self):
        """srodki otworow przelotowych fi socket_hole_d: lista (x, y, nazwa)"""
        out = []
        for g in self.gniazda:
            if g.rodzaj == "round":
                out.append((g.x, g.y, g.nazwa))
            else:
                n = g.n_otw
                for j in range(n):
                    k = j - (n - 1) / 2.0
                    out.append((g.x + k * g.pitch, g.y, "%s/otw%d" % (g.nazwa, j + 1)))
        return out

    def cechy_wierzchu(self, bity="ABCD"):
        return list(self.gniazda) + list(self.znaczniki) + [self.dolki[b] for b in bity]

    def w_plytce_sd(self, p):
        """odleglosc ze znakiem od obrysu plytki w rzucie (ujemna = w plytce); kwadrat z promieniem rogow, bez wyciecia;
        okragla: okrag i plaszczyzna sciecia"""
        x, y = p
        if self.ksztalt == "kwadrat":
            hb = self.bok / 2.0 - self.rog_r
            qx = abs(x) - hb
            qy = abs(y) - hb
            return math.hypot(max(qx, 0.0), max(qy, 0.0)) + min(max(qx, qy), 0.0) - self.rog_r
        a = math.hypot(x, y) - self.R
        b = x * self.flat_n[0] + y * self.flat_n[1] - self.flat_dist
        return max(a, b)

    def krawedz_odl(self, c):
        """okragla: odleglosc obrysu cechy do krawedzi (sciana pionowa): (do okregu, do plaszczyzny sciecia)"""
        o = min(self.R - math.hypot(*p) for p in (c.p0, c.p1)) - c.r
        f = min(self.flat_dist - (p[0] * self.flat_n[0] + p[1] * self.flat_n[1]) for p in (c.p0, c.p1)) - c.r
        return o, f

    def prostokat_cyfry(self, szer=3.6):
        cx, cy = self.cyfra
        return (cx - szer / 2.0, cx + szer / 2.0, cy - self.cyfra_h / 2.0, cy + self.cyfra_h / 2.0)


def bity_numeru(n):
    return "".join(b for i, b in enumerate("ABCD") if (n >> i) & 1)


def liczby(m):
    """Liczby ukladu do porownania z dokumentami (plan D6 / 4.1 / 4.1a / 4.11, protokol K-05 / K-16 / K-61 / K-62)."""
    out = {}
    g = m.gniazda
    licz = {}
    for c in g:
        k = ("fi%g" % c.d) if c.rodzaj == "round" else ("rynienka %gx%g" % (c.l, c.w))
        licz[k] = licz.get(k, 0) + 1
    out["liczby_gniazd"] = licz
    out["round"] = sum(1 for c in g if c.rodzaj == "round")
    out["trough"] = sum(1 for c in g if c.rodzaj == "trough")
    out["max_promien"] = max((c.max_promien(), c.opis()) for c in g)
    out["promienie_wpisow"] = {}
    for c in g:
        k = "wpis%d y=%g" % (c.wpis + 1, c.y)
        v = out["promienie_wpisow"].get(k, (0, ""))
        if c.max_promien() > v[0]:
            out["promienie_wpisow"][k] = (round(c.max_promien(), 4), c.opis())
    out["max_abs_x"] = max((c.max_abs_x(), c.opis()) for c in g)
    out["max_abs_y"] = max((c.max_abs_y(), c.opis()) for c in g)
    out["blok_y"] = (min(c.y - c.r for c in g), max(c.y + c.r for c in g))
    pary = []
    for i in range(len(g)):
        for j in range(i + 1, len(g)):
            pary.append((g[i].odstep(g[j]), g[i].opis(), g[j].opis(), g[i].wpis + 1, g[j].wpis + 1))
    pary.sort()
    out["min_scianka"] = pary[0]
    out["scianki_ponizej_3_1"] = [p for p in pary if p[0] < 3.1]
    mw = {}
    for p in pary:
        k = "%d-%d" % (min(p[3], p[4]), max(p[3], p[4]))
        if k not in mw or p[0] < mw[k][0]:
            mw[k] = p
    out["min_scianka_par_wpisow"] = dict((k, (round(v[0], 4), v[1], v[2])) for k, v in mw.items() if v[0] < 6)
    # naroza (kwadraty narozne plate_corner_zone bez gniazd)
    hb = m.bok / 2.0
    nz = hb - m.rog_strefa
    w_narozu = []
    for c in g:
        for sx in (-1, 1):
            for sy in (-1, 1):
                rect = (min(sx * nz, sx * hb), max(sx * nz, sx * hb), min(sy * nz, sy * hb), max(sy * nz, sy * hb))
                w_narozu.append((odl_prostokat_cecha(rect, c), c.opis(), (sx, sy)))
    out["min_odl_do_kwadratu_naroznego"] = min(w_narozu)
    # znaczniki
    zn = {}
    for z in m.znaczniki:
        o = min((z.odstep(c), c.opis()) for c in g)
        zn[z.nazwa] = {"xy": (z.x, z.y), "promien_srodka": math.hypot(z.x, z.y), "promien_obrysu": z.max_promien(),
                       "scianka_do_gniazda": o}
    out["znaczniki"] = zn
    A, B, C = m.znaczniki
    out["trojkat"] = {"AB": math.hypot(A.x - B.x, A.y - B.y), "BC": math.hypot(B.x - C.x, B.y - C.y),
                      "AC": math.hypot(A.x - C.x, A.y - C.y)}
    # dolki
    dl = {}
    for k in "ABCD":
        d = m.dolki[k]
        e = {"xy": (d.x, d.y), "promien_srodka": math.hypot(d.x, d.y),
             "do_gniazda": min((d.odstep(c), c.opis()) for c in g),
             "do_znacznika": min((d.odstep(z), z.nazwa) for z in m.znaczniki)}
        if m.ksztalt == "okragla":
            o, f = m.krawedz_odl(d)
            e["do_krawedzi_okrag"] = o
            e["do_sciecia"] = f
        else:
            e["do_krawedzi"] = m.bok / 2.0 - abs(d.x) - d.r
        dl[k] = e
    out["dolki"] = dl
    out["dolek_gniazdo_min"] = min(dl[k]["do_gniazda"] for k in "ABCD")
    out["dolek_znacznik_min"] = min(dl[k]["do_znacznika"] for k in "ABCD")
    out["dolek_gniazdo_max"] = max(dl[k]["do_gniazda"][0] for k in "ABCD")
    out["dolek_znacznik_max"] = max(dl[k]["do_znacznika"][0] for k in "ABCD")
    out["dolek_promien_min_max"] = (min(dl[k]["promien_srodka"] for k in "ABCD"),
                                    max(dl[k]["promien_srodka"] for k in "ABCD"))
    return out, dl


def liczby_pelne(m):
    """liczby() + cyfra, wyciecie, krawedzie plytki okraglej, sciecie"""
    out, dl = liczby(m)
    g = m.gniazda
    if m.cyfra is not None:
        rect = m.prostokat_cyfry()
        rogi = [(rect[0], rect[2]), (rect[1], rect[2]), (rect[1], rect[3]), (rect[0], rect[3])]
        cy = {"xy": m.cyfra, "promien_naroznika_max": max(math.hypot(*r) for r in rogi),
              "do_gniazda": min((odl_prostokat_cecha(rect, c), c.opis()) for c in g),
              "do_znacznika": min((odl_prostokat_cecha(rect, z), z.nazwa) for z in m.znaczniki),
              "do_dolka": min((odl_prostokat_cecha(rect, m.dolki[k]), k) for k in "ABCD")}
        if m.ksztalt == "okragla":
            cy["do_sciecia"] = m.flat_dist - max(r[0] * m.flat_n[0] + r[1] * m.flat_n[1] for r in rogi)
        out["cyfra"] = cy
    if m.ksztalt == "kwadrat":
        out["wyciecie_gniazdo"] = min((odl_prostokat_cecha(m.wyciecie, c), c.opis()) for c in g)
        out["dolek_krawedz"] = min(dl[k]["do_krawedzi"] for k in "ABCD")
    else:
        out["gniazdo_krawedz_okrag_min"] = min((m.krawedz_odl(c)[0], c.opis()) for c in g)
        out["gniazdo_poczatek_fazy_min"] = out["gniazdo_krawedz_okrag_min"][0] - m.faza
        out["gniazdo_sciecie_min"] = min((m.krawedz_odl(c)[1], c.opis()) for c in g)
        out["gniazdo_krawedz_min"] = min(out["gniazdo_krawedz_okrag_min"], out["gniazdo_sciecie_min"])
        out["znacznik_krawedz_min"] = min((min(m.krawedz_odl(z)), z.nazwa) for z in m.znaczniki)
        out["znacznik_sciecie_min"] = min((m.krawedz_odl(z)[1], z.nazwa) for z in m.znaczniki)
        out["dolek_krawedz_min"] = min((min(dl[k]["do_krawedzi_okrag"], dl[k]["do_sciecia"]), k) for k in "ABCD")
        out["dolek_sciecie_min"] = min((dl[k]["do_sciecia"], k) for k in "ABCD")
        out["sciecie_obrysy_min"] = min(out["gniazdo_sciecie_min"][0], out["znacznik_sciecie_min"][0],
                                        out["dolek_sciecie_min"][0])
        out["flat_dist"] = m.flat_dist
        out["flat_depth"] = m.R - m.flat_dist
    return out
