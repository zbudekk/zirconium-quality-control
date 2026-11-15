"""Pomiary do paczki "krawedz brzegu" (P2 / P4): linie krawedzi projektow, generator ubytkow, metryki krawedz / sciana.

Uzycie (z katalogu stanowisko/; wynik: JSON w ``--wyjscie`` i tabela na stdout, bez nazw plikow projektow):
    py -3.12 narzedzia/metryki_krawedz.py linie --projekty <folder> [--wspolczynnik 1.22] [--procesy N]
        linie krawedzi brzegu kazdego projektu: liczba petli, dlugosci, przekroje zweryfikowane, werdykt, czas;
        zasieg pasa brzegu: udzial linii ponizej starego pasa (plaszczyzna z = -pas)
    py -3.12 narzedzia/metryki_krawedz.py ubytki --projekty <folder> [--ile 40] [--seed 0] [--procesy N]
        P4 (a): ubytki losowe w pasie brzegu, generator sprzed P4 (wersja 1) i po (wersja 2) w TYCH SAMYCH miejscach:
        udzial czaszy w powietrzu, czasza nad projektem, material w kuli bez powierzchni, glebokosc rzeczywista / nominalna
    py -3.12 narzedzia/metryki_krawedz.py k6 --projekty <folder> [--rozmiary 0.08,...] [--powtorzen 4] [--procesy N]
        P4 (b): ukruszenia celowe K6 na liniach krawedzi (srodek / naroznik zewn. / wewn. / sciana): glebokosc rzeczywista
        vs rozmiar, czasza w powietrzu, srodek na powierzchni; osobno korony, korony implantowe, filary prac wieloczlonowych
    py -3.12 narzedzia/metryki_krawedz.py analiza --przed <metryki_P3a.json> --po <metryki_P3a.json> [--linie linie.json]
        P2 (c): inspect przed / po na tych samych skanach: prace cale (zmiana koloru, powody "nie sprawdzono"), falszywe
        alarmy, wykrycia krawedz / sciana, po rozmiarach i polozeniach (zestaw K6), pokrycie filarow mostow, czas
    py -3.12 narzedzia/metryki_krawedz.py mapa --wyniki <katalog z *_wynik.json> --wzor <t8_mapa_seed7001.json>
        P4 (d): mapa gniazdo -> projekt -> status na skanach seed 7001 vs mapa odniesienia

Sztuczne dane sa wylacznie do budowy i pomiaru kodu; rozstrzyga test skanera (P3b).
"""
from __future__ import annotations

import argparse
import json
import math
import multiprocessing as mp
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import trimesh
from scipy.spatial import cKDTree

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from stanowisko import krawedz as KR  # noqa: E402
from stanowisko import match as M  # noqa: E402
from stanowisko import synth as S  # noqa: E402
from stanowisko import ustawienia as UST  # noqa: E402

POZA_MATERIALEM_MM = 0.01  # punkt nowej powierzchni dalej niz tyle NA ZEWNATRZ pierwotnej bryly = "w powietrzu"


# ----------------------------------------------------------------------------
# linie
# ----------------------------------------------------------------------------
def _linie_projektu(arg: tuple) -> dict:
    plik, w, pas, katalog = arg
    if katalog is not None:
        KR.ustaw_katalog_pamieci(katalog)
    t0 = time.time()
    pr = M.Projekt(plik, w)
    t1 = time.time()
    linie = KR.linie_siatki(pr.siatka, skala=w, klucz=KR.klucz_projektu(pr.id, pr.T0))
    t2 = time.time()
    op = linie.opis()
    for f, d in zip(linie.filary, op["filary"]):
        O = f.linie["O"]
        seg = np.linalg.norm(np.roll(O.X, -1, 0) - O.X, axis=1)
        zmid = (np.roll(O.X, -1, 0)[:, 2] + O.X[:, 2]) / 2
        d["udzial_O_ponizej_starego_pasa"] = round(float(seg[zmid < -pas].sum() / seg.sum()), 4)
        d["caly_ponizej_starego_pasa"] = bool((O.X[:, 2] < -pas).all())
    return {"projekt": pr.id, "typ": pr.cechy.typ, "zeby": pr.cechy.zeby, "szczelna": bool(pr.siatka.is_watertight),
            "trojkatow": int(len(pr.siatka.faces)), "czas_puli_s": round(t1 - t0, 2), "czas_linii_s": round(t2 - t1, 2), **op}


def polecenie_linie(a) -> None:
    ust = UST.wczytaj_ustawienia(a.ustawienia)
    pas = ust["inspect"]["pas_brzegu_mm"]
    pliki = S.pliki_projektow(a.projekty)
    if not pliki:
        raise SystemExit(f"brak plikow STL w {a.projekty}")
    a.wyjscie.mkdir(parents=True, exist_ok=True)
    zadania = [(p, a.wspolczynnik, pas, a.pamiec) for p in pliki]
    t0 = time.time()
    if a.procesy > 1:
        with mp.Pool(a.procesy) as pool:
            wyniki = pool.map(_linie_projektu, zadania)
    else:
        wyniki = [_linie_projektu(z) for z in zadania]
    wyniki.sort(key=lambda r: r["projekt"])
    filary = [f for r in wyniki for f in r["filary"]]
    wielo = [f for r in wyniki if r["filarow"] > 1 for f in r["filary"]]
    zb = {
        "projektow": len(wyniki), "petli": len(filary), "projekty_bez_linii": sum(1 for r in wyniki if r["filarow"] == 0),
        "petle_werdykt": {w: sum(1 for f in filary if f["werdykt"] == w) for w in KR.WERDYKTY},
        "projekty_stan": {s: sum(1 for r in wyniki if r["stan"] == s) for s in ("wiarygodne", "czesciowe", "brak")},
        "wieloczlonowe_projektow": sum(1 for r in wyniki if r["filarow"] > 1), "wieloczlonowe_petli": len(wielo),
        "wieloczlonowe_petle_cale_ponizej_starego_pasa": sum(1 for f in wielo if f["caly_ponizej_starego_pasa"]),
        "petle_cale_ponizej_starego_pasa": sum(1 for f in filary if f["caly_ponizej_starego_pasa"]),
        "petle_z_kanalem_na_wylot": sum(1 for f in filary if f.get("kanal_na_wylot")),
        "pas_brzegu_mm": pas, "wspolczynnik": a.wspolczynnik, "wersja_linii": KR.WERSJA,
        "czas_linii_s_mediana": float(np.median([r["czas_linii_s"] for r in wyniki])), "czas_linii_s_max": max(r["czas_linii_s"] for r in wyniki),
        "czas_calosci_s": round(time.time() - t0, 1),
    }
    (a.wyjscie / a.nazwa).write_text(json.dumps({"projekty": wyniki, "zbiorczo": zb}, ensure_ascii=False, indent=1), encoding="utf-8")
    print("projekt           typ          zeby         filar war. zweryf.      ciag  przerwa  werdykt     dl. O (zweryf.)  z O                 pod starym pasem  kanal  czas")
    for r in wyniki:
        if not r["filary"]:
            print(f"{r['projekt']}  {r['typ']:11s}  {'-'.join(r['zeby']):11s}  BRAK LINII: {'; '.join(r['uwagi'])}  {r['czas_linii_s']} s")
        for f in r["filary"]:
            print(f"{r['projekt']}  {r['typ']:11s}  {'-'.join(r['zeby']):11s}  {f['nr']:>3d}   {f['wariant']}   {f['przekroje_zweryfikowane']:>3d}/{f['przekroje']} ({f['udzial_zweryf']:.2f})"
                  f"  {f['najdl_ciag_st']:>5.1f}  {f['najdl_przerwa_mm']:>5.2f}  {f['werdykt']:10s}  {f['dlugosc_O_mm']:>5.1f} ({f['dlugosc_O_zweryf_mm']:>5.1f})"
                  f"  {f['z_O_min_max'][0]:>6.2f} ... {f['z_O_min_max'][1]:>5.2f}  {f['udzial_O_ponizej_starego_pasa']:>6.2f}{' CALY' if f['caly_ponizej_starego_pasa'] else '     '}"
                  f"  {'tak' if f.get('kanal_na_wylot') else 'nie':5s}  {r['czas_linii_s']} s")
    print("ZBIORCZO:", json.dumps(zb, ensure_ascii=False))
    print(a.wyjscie / a.nazwa)


# ----------------------------------------------------------------------------
# geometria ubytkow (P4 a, b)
# ----------------------------------------------------------------------------
class _Staly:
    """"rng" zwracajacy zawsze ten sam wierzcholek / przekroj (te same miejsca dla obu wersji generatora)."""

    def __init__(self, i: int):
        self.i = i

    def choice(self, _):
        return self.i

    def integers(self, _):
        return 0


def _praca(plik: Path, w: float):
    m = S.wczytaj_projekt(plik)
    O = S.orientacja_brzegiem_do_gory(m, "auto", plik.name)
    m.apply_transform(O @ trimesh.transformations.scale_matrix(w))
    return m, KR.linie_siatki(m, skala=w, klucz=KR.klucz_projektu(S.skrot_pliku(plik), O))


def _pomiar_czaszy(przed: trimesh.Trimesh, po: trimesh.Trimesh, c: np.ndarray, r: float) -> dict:
    """Niezalezny pomiar (trimesh, nie kod generatora) nowej powierzchni ubytku = trojkaty, ktorych wszystkie wierzcholki
    leza na sferze (c, r): udzial pola w powietrzu, najwieksza wysokosc nad pierwotna bryla, glebokosc rzeczywista,
    udzial materialu w kuli bez powierzchni, wierzcholki pozostale wewnatrz kuli."""
    na_sferze = np.abs(np.linalg.norm(po.vertices - c, axis=1) - r) < 1e-6
    tw = na_sferze[po.faces].all(axis=1)
    out = {"wierzcholkow_w_kuli": int((np.linalg.norm(po.vertices - c, axis=1) < r - 1e-6).sum()), "trojkatow_czaszy": int(tw.sum())}
    if not tw.any():
        return {**out, "udzial_w_powietrzu": None, "nad_projektem_mm": None, "glebokosc_mm": 0.0, "material_bez_powierzchni": 1.0}
    tri = po.triangles[tw]
    srodki = tri.mean(axis=1)
    pola = po.area_faces[tw]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        sd_s = trimesh.proximity.signed_distance(przed, srodki)  # > 0 = wewnatrz pierwotnej bryly
        V = np.unique(po.faces[tw])
        sd_v = trimesh.proximity.signed_distance(przed, po.vertices[V])
        kier = S._punkty_kuli(1500)
        sd_k = trimesh.proximity.signed_distance(przed, c + r * kier)
    w_mat = sd_k > POZA_MATERIALEM_MM
    tol = max(1.5 * float(np.median(cKDTree(po.vertices[V]).query(po.vertices[V], k=2)[0][:, 1])), 0.02)
    pokryte = cKDTree(srodki).query(c + r * kier[w_mat])[0] <= tol if w_mat.any() else np.zeros(0, bool)
    return {**out, "udzial_w_powietrzu": round(float(pola[sd_s < -POZA_MATERIALEM_MM].sum() / pola.sum()), 4),
            "nad_projektem_mm": round(float(max(0.0, -sd_v.min())), 4), "glebokosc_mm": round(float(max(0.0, sd_v.max())), 4),
            "material_bez_powierzchni": round(float(1 - pokryte.mean()), 4) if w_mat.any() else 0.0}


def _ubytki_projektu(arg: tuple) -> list[dict]:
    plik, w, ile, seed, pas, odstep = arg
    m, linie = _praca(plik, w)
    skrot = S.skrot_pliku(plik)
    pewne = S._stacje_pewne(linie)
    kand = (np.flatnonzero(np.isfinite(cKDTree(pewne).query(m.vertices, distance_upper_bound=pas)[0])) if len(pewne)
            else np.flatnonzero(m.vertices[:, 2] > m.bounds[1, 2] - pas))
    rng = np.random.default_rng(seed)
    szczelna = bool(m.is_watertight)
    wyniki = []
    for k in range(ile):
        iv = int(rng.choice(kand))
        d = float(rng.uniform(0.2, 1.5))
        r = d / 2
        rek = {"projekt": skrot, "szczelna": szczelna, "nr": k, "srednica": round(d, 4), "glebokosc_nominalna": round(0.7 * r, 4)}
        po1, ub1 = S._wytnij_ubytek_v1(m, d, _Staly(iv), pas_brzegu=pas)
        mat = S.Material(m)
        try:
            po2, ub2 = S.wytnij_ubytek(m, d, _Staly(iv), pas, linie=linie, material=mat, odstep=odstep)
        except RuntimeError:
            continue
        c, _ = mat.kule[-1]
        klasa, filar, odl = S.polozenie_wzgledem_brzegu(linie, np.array([ub2.x, ub2.y, ub2.z]), r)
        rek.update({"klasa": klasa, "filar": filar, "odleglosc_od_linii": odl, "glebokosc_generator_v2": ub2.glebokosc_rzeczywista,
                    "v1": _pomiar_czaszy(m, po1, c, r), "v2": _pomiar_czaszy(m, po2, c, r)})
        wyniki.append(rek)
    return wyniki


def _podsumuj_ubytki(rek: list[dict], wersja: str) -> dict:
    v = [x[wersja] for x in rek if x[wersja]["udzial_w_powietrzu"] is not None]
    if not v:
        return {"ubytkow": len(rek)}
    rel = np.array([x[wersja]["glebokosc_mm"] / x["glebokosc_nominalna"] for x in rek if x[wersja]["udzial_w_powietrzu"] is not None])
    return {
        "ubytkow": len(rek), "z_czasza": len(v),
        "czasza_w_powietrzu_ponad_10_proc": sum(x["udzial_w_powietrzu"] > 0.10 for x in v),
        "czasza_w_powietrzu_cokolwiek": sum(x["udzial_w_powietrzu"] > 0.0 for x in v),
        "udzial_w_powietrzu_sredni": round(float(np.mean([x["udzial_w_powietrzu"] for x in v])), 4),
        "czasza_ponad_0_08_nad_projektem": sum(x["nad_projektem_mm"] > 0.08 for x in v),
        "material_w_kuli_bez_powierzchni_ponad_10_proc": sum(x["material_bez_powierzchni"] > 0.10 for x in v),
        "wierzcholki_w_kuli": sum(x["wierzcholkow_w_kuli"] > 0 for x in v),
        "glebokosc_rzeczywista_do_nominalnej_p10_med_p90": [round(float(q), 3) for q in np.percentile(rel, [10, 50, 90])],
    }


def polecenie_ubytki(a) -> None:
    ust = UST.wczytaj_ustawienia(a.ustawienia)
    pas, odstep = ust["inspect"]["pas_brzegu_mm"], ust["synth"]["odstep_ubytku_mm"]
    pliki = S.pliki_projektow(a.projekty)
    a.wyjscie.mkdir(parents=True, exist_ok=True)
    zad = [(p, a.wspolczynnik, a.ile, a.seed + i, pas, odstep) for i, p in enumerate(pliki)]
    t0 = time.time()
    with mp.Pool(max(1, a.procesy)) as pool:
        rek = [x for czesc in pool.map(_ubytki_projektu, zad) for x in czesc]
    zb = {}
    for grupa, filtr in (("wszystkie", lambda x: True), ("krawedz", lambda x: x["klasa"].startswith("krawedz")), ("sciana", lambda x: x["klasa"] == "sciana"),
                         ("siatki_szczelne", lambda x: x["szczelna"]), ("siatki_nieszczelne", lambda x: not x["szczelna"])):
        czesc = [x for x in rek if filtr(x)]
        zb[grupa] = {"przed_wersja_1": _podsumuj_ubytki(czesc, "v1"), "po_wersja_2": _podsumuj_ubytki(czesc, "v2")}
    zgodnosc = [abs(x["glebokosc_generator_v2"] - x["v2"]["glebokosc_mm"]) for x in rek if x["szczelna"]]
    zb["glebokosc_generator_vs_pomiar_trimesh_max_mm_szczelne"] = round(float(max(zgodnosc)), 4) if zgodnosc else None
    zb["czas_s"] = round(time.time() - t0, 1)
    (a.wyjscie / a.nazwa).write_text(json.dumps({"ubytki": rek, "zbiorczo": zb}, ensure_ascii=False, indent=1), encoding="utf-8")
    for g, v in zb.items():
        print(g, json.dumps(v, ensure_ascii=False))
    print(a.wyjscie / a.nazwa)


def _k6_projektu(arg: tuple) -> list[dict]:
    plik, w, rozmiary, powtorzen, seed, pas, odstep = arg
    m, linie = _praca(plik, w)
    skrot = S.skrot_pliku(plik)
    rng = np.random.default_rng(seed)
    kanal = {f.nr: bool(f.kontrola.get("kanal_na_wylot")) for f in linie.filary}
    wyniki = []
    for gdzie in S.POLOZENIA_UKRUSZEN:
        for s in rozmiary:
            for k in range(powtorzen):
                mat = S.Material(m)
                po, ub = S.wytnij_ukruszenie(m, linie, gdzie, s, rng, material=mat, pas_brzegu=pas, odstep=odstep)
                rek = {"projekt": skrot, "szczelna": bool(m.is_watertight), "filarow": len(linie.filary), "polozenie": gdzie, "rozmiar": s, "nr": k}
                if ub is None:
                    wyniki.append({**rek, "postawione": False})
                    continue
                c, r = mat.kule[-1]
                _, odl_pow, _ = trimesh.proximity.closest_point(m, [c])
                wyniki.append({**rek, "postawione": True, "filar": ub.filar, "kanal_na_wylot": kanal.get(ub.filar, False), "klasa": ub.polozenie,
                               "glebokosc_generator": ub.glebokosc_rzeczywista, "srodek_od_powierzchni_mm": round(float(odl_pow[0]), 6),
                               "odleglosc_od_linii": ub.odleglosc_od_linii, **_pomiar_czaszy(m, po, c, r)})
    return wyniki


def _grupa_projektu(x: dict, typy: dict) -> str:
    typ = typy.get(x["projekt"], "")
    if x["filarow"] > 1:
        return "wieloczlonowe_pierscien_implantowy" if x.get("kanal_na_wylot") else "wieloczlonowe_filar"
    if x.get("kanal_na_wylot") or typ == "bez_lacznika":
        return "korona_implantowa"
    return "korona" if typ == "korona" else "pojedyncza_inna"


def polecenie_k6(a) -> None:
    ust = UST.wczytaj_ustawienia(a.ustawienia)
    pas, odstep = ust["inspect"]["pas_brzegu_mm"], ust["synth"]["odstep_ubytku_mm"]
    pliki = S.pliki_projektow(a.projekty)
    a.wyjscie.mkdir(parents=True, exist_ok=True)
    typy = {}
    if a.linie is not None:
        typy = {r["projekt"]: r["typ"] for r in json.loads(a.linie.read_text(encoding="utf-8"))["projekty"]}
    zad = [(p, a.wspolczynnik, a.rozmiary, a.powtorzen, a.seed + i, pas, odstep) for i, p in enumerate(pliki)]
    t0 = time.time()
    with mp.Pool(max(1, a.procesy)) as pool:
        rek = [x for czesc in pool.map(_k6_projektu, zad) for x in czesc]
    tab = {}
    for x in rek:
        klucz = (x["polozenie"], x["rozmiar"])
        t = tab.setdefault(klucz, {"zamowione": 0, "postawione": 0, "glebokosc": [], "w_powietrzu": 0, "srodek_poza": 0, "grupy": {}})
        t["zamowione"] += 1
        if not x["postawione"]:
            continue
        t["postawione"] += 1
        t["glebokosc"].append(x["glebokosc_mm"])
        t["w_powietrzu"] += (x["udzial_w_powietrzu"] or 0) > 0.0 and x["szczelna"]
        t["srodek_poza"] += x["srodek_od_powierzchni_mm"] > 1e-3
        g = _grupa_projektu(x, typy)
        t["grupy"].setdefault(g, []).append(x["glebokosc_mm"])
    zb = {}
    print("polozenie  rozmiar  postawione  glebokosc rzecz. p10 / med / p90 [mm]  rzecz./rozmiar (med)  czasza w powietrzu (szczelne)  srodek poza powierzchnia  grupy (n, med)")
    for (gdzie, s), t in sorted(tab.items(), key=lambda kv: (S.POLOZENIA_UKRUSZEN.index(kv[0][0]), kv[0][1])):
        g = np.array(t["glebokosc"]) if t["glebokosc"] else np.array([np.nan])
        wpis = {"zamowione": t["zamowione"], "postawione": t["postawione"], "glebokosc_p10_med_p90": [round(float(q), 4) for q in np.nanpercentile(g, [10, 50, 90])],
                "glebokosc_do_rozmiaru_med": round(float(np.nanmedian(g) / s), 3), "czasza_w_powietrzu": t["w_powietrzu"], "srodek_poza_powierzchnia": t["srodek_poza"],
                "grupy": {k: [len(v), round(float(np.median(v)), 4)] for k, v in sorted(t["grupy"].items())}}
        zb[f"{gdzie}_{s}"] = wpis
        print(f"{gdzie:9s}  {s:6.2f}   {t['postawione']:>4d}/{t['zamowione']:<4d}  {wpis['glebokosc_p10_med_p90']}  {wpis['glebokosc_do_rozmiaru_med']:>6.3f}  "
              f"{t['w_powietrzu']:>4d}  {t['srodek_poza']:>4d}  {wpis['grupy']}")
    zb["czas_s"] = round(time.time() - t0, 1)
    (a.wyjscie / a.nazwa).write_text(json.dumps({"ukruszenia": rek, "zbiorczo": zb}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(a.wyjscie / a.nazwa)


# ----------------------------------------------------------------------------
# analiza przed / po (P2 c)
# ----------------------------------------------------------------------------
def _gniazda(d: dict) -> dict:
    """(skan, gniazdo) -> wpis gniazda z metryk P3a."""
    return {(r["skan"], g["gniazdo"]): g for r in d["skany"] for g in r["gniazda"] if g["gniazdo"] is not None}


def _cala(g: dict) -> bool:
    """Praca cala z trafnym top-1 i policzona inspekcja (bez drgniecia)."""
    return (g.get("ubytkow_prawda") == 0 and g.get("projekt") == g.get("projekt_prawda") and g["inspekcja"] is not None
            and g.get("scenariusz") != "drgniecie")


def _klasy_ubytkow(d: dict) -> list[dict]:
    return [u for r in d["skany"] for u in r["inspekcja"].get("ubytki", [])]


def _tabela_ubytkow(lista: list[dict], klucz, typy: dict, filarow: dict) -> dict:
    out: dict = {}
    for u in lista:
        if not u["wykrywalny"] and not u.get("celowy"):
            continue
        k = klucz(u, typy, filarow)
        if k is None:
            continue
        t = out.setdefault(k, {"n": 0, "dowolny": 0, "czerwony": 0, "A": 0, "B": 0})
        t["n"] += 1
        for m in ("dowolny", "czerwony", "A", "B"):
            t[m] += bool(u["trafione"][m])
    return dict(sorted(out.items(), key=lambda kv: str(kv[0])))


def _grupa(u: dict, typy: dict, filarow: dict) -> str:
    typ = typy.get(u["projekt"], "?")
    if filarow.get(u["projekt"], 1) > 1:
        return "wieloczlonowe"
    return {"korona": "korona", "bez_lacznika": "korona_implantowa"}.get(typ, "pojedyncza_inna")


def polecenie_analiza(a) -> None:
    przed = json.loads(a.przed.read_text(encoding="utf-8"))
    po = json.loads(a.po.read_text(encoding="utf-8"))
    typy, filarow, linie_f = {}, {}, {}
    if a.linie is not None:
        L = json.loads(a.linie.read_text(encoding="utf-8"))["projekty"]
        typy = {r["projekt"]: r["typ"] for r in L}
        filarow = {r["projekt"]: r["filarow"] for r in L}
        linie_f = {(r["projekt"], f["nr"]): f for r in L for f in r["filary"]}
    gp, gn = _gniazda(przed), _gniazda(po)
    wspolne = sorted(set(gp) & set(gn), key=str)
    out = {"skanow": len(po["skany"]), "gniazd_wspolnych": len(wspolne)}
    # prace cale: kolor przed -> po
    przejscia: dict = {}
    powody: dict = {}
    projekty_ns: dict = {}
    for k in wspolne:
        a_, b_ = gp[k], gn[k]
        if not (_cala(a_) and _cala(b_)):
            continue
        sp, sn = a_["inspekcja"]["status"], b_["inspekcja"]["status"]
        przejscia[f"{sp} -> {sn}"] = przejscia.get(f"{sp} -> {sn}", 0) + 1
        if sn == "nie_sprawdzono":
            brzeg = b_["inspekcja"].get("brzeg") or {}
            p = "+".join(sorted({x for f in brzeg.get("filary", []) if not f["sprawdzony"] for x in f["powody"]})) or "brak linii projektu"
            powody[p] = powody.get(p, 0) + 1
            pr = b_["projekt"]
            projekty_ns.setdefault(pr, {"typ": typy.get(pr, "?"), "filarow": filarow.get(pr), "prac": 0, "powody": {}})
            projekty_ns[pr]["prac"] += 1
            projekty_ns[pr]["powody"][p] = projekty_ns[pr]["powody"].get(p, 0) + 1
    calych = sum(przejscia.values())
    out["prace_cale"] = {"liczba": calych, "przejscia_statusu": dict(sorted(przejscia.items(), key=lambda kv: -kv[1])),
                         "nie_sprawdzono_powody": powody, "nie_sprawdzono_projekty": dict(sorted(projekty_ns.items(), key=lambda kv: -kv[1]["prac"]))}
    for nazwa, d in (("przed", przed), ("po", po)):
        r = d["zbiorczo"]["razem"]
        out[nazwa] = {"ubytkow": r["ubytkow"], "wykryte": r["wykryte"], "prace_cale": r["prac_calych"],
                      "prace_cale_z_czerwonym": r["prace_cale_z_czerwonym"], "prace_cale_z_alarmem": r["prace_cale_z_alarmem"],
                      "prace_cale_nie_sprawdzono": r.get("prace_cale_nie_sprawdzono", 0), "prace_cale_status_gniazda": r.get("prace_cale_status_gniazda"),
                      "falszywe_ubytki": r["falszywe_ubytki"], "falszywe_czerwone": r["falszywe_czerwone"], "falszywe_metoda": r["falszywe_metoda"],
                      "statusy_inspect": r["statusy"], "statusy_gniazd": d["zbiorczo"]["plate_match"]["statusy_gniazd"],
                      "klasy": r.get("klasy"), "czas_s_mediana": d["zbiorczo"]["plate_match"]["czas_s_mediana"],
                      "ustawienia_inspect": d["zbiorczo"].get("ustawienia_inspect")}
        lista = _klasy_ubytkow(d)
        out[nazwa]["po_klasie_i_grupie"] = _tabela_ubytkow(lista, lambda u, t, f: f"{u['klasa']} / {_grupa(u, t, f)}", typy, filarow)
        out[nazwa]["k6_polozenie_rozmiar"] = _tabela_ubytkow(lista, lambda u, t, f: (f"{u['polozenie']} {u['srednica'] / 2:.2f}" if u.get("celowy") else None), typy, filarow)
        out[nazwa]["k6_polozenie_grupa"] = _tabela_ubytkow(lista, lambda u, t, f: (f"{u['polozenie']} / {_grupa(u, t, f)}" if u.get("celowy") else None), typy, filarow)
        out[nazwa]["k6_rozmiar_grupa"] = _tabela_ubytkow(lista, lambda u, t, f: (f"{u['srednica'] / 2:.2f} / {_grupa(u, t, f)}" if u.get("celowy") else None), typy, filarow)
    # zmiany wykryc tego samego ubytku (lista ubytkow ma te same skany i kolejnosc)
    lp, ln = _klasy_ubytkow(przed), _klasy_ubytkow(po)
    if len(lp) == len(ln):
        zm = {"zyskane_dowolny": 0, "stracone_dowolny": 0, "zyskane_czerwony": 0, "stracone_czerwony": 0}
        for u, v in zip(lp, ln):
            if not u["wykrywalny"] and not u.get("celowy"):
                continue
            for m in ("dowolny", "czerwony"):
                zm[f"zyskane_{m}"] += (not u["trafione"][m]) and v["trafione"][m]
                zm[f"stracone_{m}"] += u["trafione"][m] and not v["trafione"][m]
        out["zmiany_wykryc"] = zm
    # filary prac wieloczlonowych: pokrycie pasem (linie) i co sprawdzono na pracach calych (po)
    fil: dict = {}
    for k in wspolne:
        b_ = gn[k]
        if not _cala(b_) or filarow.get(b_["projekt"], 1) < 2:
            continue
        for f in (b_["inspekcja"].get("brzeg") or {}).get("filary", []):
            t = fil.setdefault((b_["projekt"], f["nr"]), {"prac": 0, "sprawdzony": 0, "udzial_sprawdzony": [], "powody": {}})
            t["prac"] += 1
            t["sprawdzony"] += f["sprawdzony"]
            t["udzial_sprawdzony"].append(f["udzial_sprawdzony"])
            for p in f["powody"]:
                t["powody"][p] = t["powody"].get(p, 0) + 1
    out["filary_wieloczlonowe"] = {f"{p} F{n}": {"prac_calych": t["prac"], "sprawdzony": t["sprawdzony"],
                                                 "udzial_sprawdzony_med": round(float(np.median(t["udzial_sprawdzony"])), 3), "powody": t["powody"],
                                                 "caly_ponizej_starego_pasa": linie_f.get((p, n), {}).get("caly_ponizej_starego_pasa"),
                                                 "werdykt_linii": linie_f.get((p, n), {}).get("werdykt")} for (p, n), t in sorted(fil.items())}
    a.wyjscie.mkdir(parents=True, exist_ok=True)
    (a.wyjscie / a.nazwa).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=1))


# ----------------------------------------------------------------------------
# mapa seed 7001 (P4 d)
# ----------------------------------------------------------------------------
def polecenie_mapa(a) -> None:
    wzor = json.loads(a.wzor.read_text(encoding="utf-8"))
    out = {}
    for p in sorted(a.wyniki.glob("*_wynik.json")):
        w = json.loads(p.read_text(encoding="utf-8"))
        nazwa = p.name[: -len("_wynik.json")].replace("_r54", "")
        nowa = {str(g["gniazdo"]): {"projekt": g["kandydaci"][0]["id"] if g["kandydaci"] else None, "match": g["status"], "status_gniazda": g["status_gniazda"]}
                for g in w["gniazda"] if g["gniazdo"] is not None}
        stara = wzor.get(nazwa, {}).get("gniazda", {})
        rozne = {g: {"wzor": stara.get(g), "teraz": nowa.get(g)} for g in sorted(set(stara) | set(nowa), key=int) if stara.get(g) != nowa.get(g)}
        out[nazwa] = {"gniazd_wzor": len(stara), "gniazd_teraz": len(nowa), "zgodne": len(stara) > 0 and not rozne,
                      "projekty_wzor": sorted({v["projekt"] for v in stara.values()}), "projekty_teraz": sorted({v["projekt"] for v in nowa.values() if v["projekt"]}),
                      "rozne": rozne, "statusy_teraz": w["statusy_gniazd"]}
        print(f"{nazwa}: gniazd {len(stara)} -> {len(nowa)}, {'ZGODNA' if out[nazwa]['zgodne'] else f'rozne gniazda: {len(rozne)}'}; statusy teraz {w['statusy_gniazd']}")
    if a.wyjscie is not None:
        a.wyjscie.parent.mkdir(parents=True, exist_ok=True)
        a.wyjscie.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")


def _lista_float(s: str) -> list[float]:
    return [float(x) for x in s.split(",")]


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="polecenie", required=True)
    p = sub.add_parser("linie", help="linie krawedzi brzegu projektow i zasieg pasa brzegu")
    p.add_argument("--projekty", type=Path, required=True)
    p.add_argument("--wspolczynnik", type=float, default=1.22)
    p.add_argument("--wyjscie", type=Path, default=Path("dane/krawedz"))
    p.add_argument("--nazwa", default="linie.json")
    p.add_argument("--pamiec", type=Path, default=None, help="katalog pamieci podrecznej linii na dysku (domyslnie bez)")
    p.add_argument("--procesy", type=int, default=1)
    p.add_argument("--ustawienia", type=Path, default=None)
    p.set_defaults(fun=polecenie_linie)
    p = sub.add_parser("ubytki", help="P4 (a): geometria ubytkow losowych, wersja 1 vs 2 w tych samych miejscach")
    p.add_argument("--projekty", type=Path, required=True)
    p.add_argument("--wspolczynnik", type=float, default=1.22)
    p.add_argument("--ile", type=int, default=40, help="ubytkow na projekt")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--wyjscie", type=Path, default=Path("dane/krawedz"))
    p.add_argument("--nazwa", default="ubytki.json")
    p.add_argument("--procesy", type=int, default=1)
    p.add_argument("--ustawienia", type=Path, default=None)
    p.set_defaults(fun=polecenie_ubytki)
    p = sub.add_parser("k6", help="P4 (b): ukruszenia celowe na krawedzi - glebokosc rzeczywista vs rozmiar")
    p.add_argument("--projekty", type=Path, required=True)
    p.add_argument("--wspolczynnik", type=float, default=1.22)
    p.add_argument("--rozmiary", type=_lista_float, default=[0.08, 0.10, 0.15, 0.20, 0.30, 0.40])
    p.add_argument("--powtorzen", type=int, default=4)
    p.add_argument("--seed", type=int, default=100)
    p.add_argument("--linie", type=Path, default=None, help="linie.json z polecenia linie (typy projektow)")
    p.add_argument("--wyjscie", type=Path, default=Path("dane/krawedz"))
    p.add_argument("--nazwa", default="k6_geometria.json")
    p.add_argument("--procesy", type=int, default=1)
    p.add_argument("--ustawienia", type=Path, default=None)
    p.set_defaults(fun=polecenie_k6)
    p = sub.add_parser("analiza", help="P2 (c): inspect przed / po na tych samych skanach")
    p.add_argument("--przed", type=Path, required=True)
    p.add_argument("--po", type=Path, required=True)
    p.add_argument("--linie", type=Path, default=None)
    p.add_argument("--wyjscie", type=Path, default=Path("dane/krawedz"))
    p.add_argument("--nazwa", default="analiza.json")
    p.set_defaults(fun=polecenie_analiza)
    p = sub.add_parser("mapa", help="P4 (d): mapa seed 7001 vs mapa odniesienia")
    p.add_argument("--wyniki", type=Path, required=True)
    p.add_argument("--wzor", type=Path, required=True)
    p.add_argument("--wyjscie", type=Path, default=None)
    p.set_defaults(fun=polecenie_mapa)
    a = ap.parse_args(argv)
    a.fun(a)


if __name__ == "__main__":
    main()
