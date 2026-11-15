"""Pomiary do poprawek P1 (filtr wymiarow w match) i P3 (korekta skali ze skanu) - odtwarzalne, z licznikami.

Uzycie (z katalogu stanowisko/; skany z prawda JSON generatora, np. dane/syntetyczne_R59_P2):
    py -3.12 narzedzia/metryki_skala.py p1 --skany <zestaw> [<zestaw2> ...] --projekty <folder> --wyjscie <folder>
        [--scenariusze pelny z_gory ...] [--dopasuj] [--sufiks-ukladu _r54] [--limit N] [--procesy N]
    py -3.12 narzedzia/metryki_skala.py program --skany <zestaw> ... --projekty <folder> --wyjscie <folder>
        [--bledy 0,0.1,-0.1,0.3,-0.3,0.5,-0.5,1,-1] [--korekta tak nie] [--sufiks-ukladu _r54] [--limit N] [--procesy N]
    py -3.12 narzedzia/metryki_skala.py brzeg --skany <zestaw> ... --projekty <folder> --wyjscie <folder>
        [--wielkosc 0.02] [--limit N] [--procesy N]

p1      - filtr wymiarow przed / po poprawce na fragmentach z plate, w scenariuszach widocznosci: pelny (jak w danych
          syntetycznych), z_gory (stozek 30 st., praca zaslania sama siebie - jak T5 / T7), z_gory_plytka (to samo +
          zaslanianie przez plytke: scianki pracy w gniezdzie), bez_dolu_1.5 / bez_dolu_3.0 (dolne mm odciete - jak T10),
          nad_plytka (wszystko ponizej wierzchu plytki odciete). Liczy: czy wlasciwy projekt przechodzi filtr, ile
          projektow z puli przechodzi, a z --dopasuj takze top-1, status i czas match (filtr stary i nowy).
program - pelny lancuch porownaj (plate -> match -> inspect) przy zadanym bledzie wspolczynnika puli (blad e %: praca
          jest o e % wieksza niz projekt x wspolczynnik puli), z korekta skali i bez: blad estymaty skali, top-1,
          statusy, wykrycia ubytkow, falszywe alarmy na pracach calych, czasy. Plytki poranne licza sie osobno
          (korekta jest tam tylko mierzona).
brzeg   - czy strefa przy krawedzi brzegu wplywa na estymate skali (zastrzezenie R2b): ta sama praca bez zmian i ze
          zmieniona strefa brzegu (grubosc / przesuniecie z o +-wielkosc w pasie A: 0-0,3-0,5 mm i C: 0-1,4-2,0 mm,
          trzy ukruszenia fi 1,0), estymata z wylaczeniem pasa brzegu (ustawienia) i kontrolnie bez wylaczenia (pas 0).

Wyniki: <wyjscie>/<nazwa>.json (wiersz = jedna praca; tylko skroty projektow) i tabela na stdout.
Sztuczne skany sa danymi do budowy i pomiaru kodu; skanera jeszcze nie ma.
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
import open3d as o3d
import trimesh

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from stanowisko import match as M  # noqa: E402
from stanowisko import plate as PL  # noqa: E402
from stanowisko import porownaj as PO  # noqa: E402
from stanowisko import synth as S  # noqa: E402
from stanowisko import uklad as U  # noqa: E402
from stanowisko import ustawienia as UST  # noqa: E402

SCENARIUSZE_P1 = ("pelny", "z_gory", "z_gory_plytka", "bez_dolu_1.5", "bez_dolu_3.0", "nad_plytka")
BLEDY = (0.0, 0.1, -0.1, 0.3, -0.3, 0.5, -0.5, 1.0, -1.0)
CEL_ESTYMATY_PROC = 0.05  # cel dokladnosci estymaty skali (T7)
LIMIT_ZADANIA_S = 3600
_PULE: dict[tuple, M.Pula] = {}


def pula(projekty: tuple, w: float) -> M.Pula:
    """Pula projektow w pamieci procesu (najwyzej 2 naraz - kazda to kilkaset MB)."""
    k = (projekty, round(w, 9))
    if k not in _PULE:
        while len(_PULE) >= 2:
            _PULE.pop(next(iter(_PULE)))
        _PULE[k] = M.Pula(list(projekty), w)
    return _PULE[k]


def nazwa_plytki(prawda: S.PrawdaPlytki, sufiks: str) -> str:
    return prawda.plytka if prawda.plytka.endswith(sufiks) else prawda.plytka + sufiks


def wspolczynnik_prawdy(prawda: S.PrawdaPlytki) -> float:
    return float(np.mean([x.wspolczynnik for x in prawda.prace])) if prawda.prace else 1.0


def percentyl(v: list[float], q: float) -> float | None:
    return round(float(np.percentile(v, q)), 4) if len(v) else None


# ----------------------------------------------------------------------------
# P1: filtr wymiarow
# ----------------------------------------------------------------------------
def filtr_sprzed_P1(fr: M.FragmentDoDopasowania, pr: M.Projekt, ust: dict) -> tuple[bool, str]:
    """Filtr wymiarow w brzmieniu sprzed poprawki P1 (commit 8b83da7) - do pomiaru przed / po."""
    m = ust["match"]
    tol = lambda v: max(m["filtr_wymiar_mm"], m["filtr_wymiar_udzial"] * v)  # noqa: E731
    for nazwa, a, b in (("dlugosc", fr.obrys_xy[1], pr.obrys_xy[1]), ("szerokosc", fr.obrys_xy[0], pr.obrys_xy[0]), ("wysokosc", fr.wysokosc, pr.wysokosc)):
        if abs(a - b) > tol(b):
            return False, f"{nazwa} {a:.1f} vs {b:.1f} mm"
    if pr.hull > 0 and abs(fr.hull - pr.hull) > m["filtr_objetosc_udzial"] * pr.hull:
        return False, f"objetosc otoczki {fr.hull:.0f} vs {pr.hull:.0f} mm3"
    return True, ""


def kierunki_widoku(przechyl_max_deg: float = 30.0, pierscienie: int = 2, na_pierscien: int = 8) -> np.ndarray:
    """Kierunki patrzenia skanera: +z i pierscienie do ``przechyl_max_deg`` od pionu (jak w testach T5)."""
    v = [np.array([0.0, 0.0, 1.0])]
    for i in range(1, pierscienie + 1):
        a = math.radians(przechyl_max_deg * i / pierscienie)
        for j in range(na_pierscien):
            b = 2 * math.pi * (j + 0.5 * (i % 2)) / na_pierscien
            v.append(np.array([math.sin(a) * math.cos(b), math.sin(a) * math.sin(b), math.cos(a)]))
    return np.array(v)


def widoczne_z_gory(P: np.ndarray, N: np.ndarray, siatki: list[trimesh.Trimesh], kat_padania_max_deg: float = 75.0, odsun: float = 0.15) -> np.ndarray:
    """Maska punktow (uklad plytki) widocznych z ktoregos kierunku w stozku 30 st. wokol +z: kat padania <= 75 st.
    i promien z punktu odsunietego o ``odsun`` wzdluz normalnej (szum skanu) nie trafia w zadna z siatek (praca, plytka)."""
    scena = o3d.t.geometry.RaycastingScene()
    for m in siatki:
        scena.add_triangles(o3d.t.geometry.TriangleMesh(o3d.core.Tensor(np.asarray(m.vertices, dtype=np.float32)), o3d.core.Tensor(np.asarray(m.faces, dtype=np.int32))))
    widoczny = np.zeros(len(P), dtype=bool)
    cmin = math.cos(math.radians(kat_padania_max_deg))
    S0 = P + odsun * N
    for v in kierunki_widoku():
        idx = np.flatnonzero(~widoczny & (N @ v >= cmin))
        if len(idx) == 0:
            continue
        promienie = np.concatenate([S0[idx], np.repeat(v[None], len(idx), 0)], axis=1).astype(np.float32)
        traf = scena.cast_rays(o3d.core.Tensor(promienie))["t_hit"].numpy()
        widoczny[idx[~np.isfinite(traf)]] = True
    return widoczny


def maska_scenariusza(sc: str, P: np.ndarray, N: np.ndarray, pr: M.Projekt, T_pula_do_plytki: np.ndarray, uk: U.UkladPlytki, plik_plytki: Path) -> np.ndarray:
    if sc == "pelny":
        return np.ones(len(P), dtype=bool)
    if sc.startswith("bez_dolu_"):
        return P[:, 2] >= P[:, 2].min() + float(sc.rsplit("_", 1)[1])
    if sc == "nad_plytka":
        return P[:, 2] >= uk.thickness
    if sc in ("z_gory", "z_gory_plytka"):
        praca = pr.siatka.copy()
        praca.apply_transform(T_pula_do_plytki)
        siatki = [praca] + ([trimesh.load(plik_plytki, force="mesh")] if sc == "z_gory_plytka" else [])
        return widoczne_z_gory(P, N, siatki)
    raise ValueError(f"nieznany scenariusz {sc!r}")


def zadanie_p1(arg: tuple) -> dict:
    p, projekty, sufiks, plik_ust, scenariusze, z_dopasowaniem = arg
    ust = UST.wczytaj_ustawienia(plik_ust)
    prawda = S.wczytaj_prawde(p.with_suffix(".json"))
    plytka = nazwa_plytki(prawda, sufiks)
    uk = U.wczytaj(plytka, UST.katalog_plytki(ust, plytka))
    pl = pula(projekty, wspolczynnik_prawdy(prawda))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            wyr = PL.wyrownaj(trimesh.load(p, force="mesh"), uk)
        except PL.BladWyrownania as e:
            return {"wiersze": [], "linia": f"{p.name}: {e}"}
    praw = {x.gniazdo: x for x in prawda.prace}
    plik_plytki = PL.plik_modelu_plytki(uk, wyr.numer)
    wiersze = []
    for f in wyr.fragmenty:
        if f.status != "praca" or f.gniazdo not in praw or praw[f.gniazdo].projekt not in pl.projekty:
            continue
        x = praw[f.gniazdo]
        pr = pl.projekty[x.projekt]
        T_pp = np.array(x.transformacja) @ np.linalg.inv(pr.T0)  # uklad puli projektu -> plytka (prawda)
        for sc in scenariusze:
            maska = maska_scenariusza(sc, f.punkty, f.normalne, pr, T_pp, uk, plik_plytki)
            w = {"skan": p.name, "zestaw": p.parent.name, "plytka": plytka, "gniazdo": f.gniazdo, "projekt": x.projekt, "scenariusz_pracy": PO.scenariusz(x),
                 "scenariusz": sc, "punktow": int(maska.sum()), "udzial_punktow": round(float(maska.mean()), 3)}
            if maska.sum() < 300:
                w["pominiety"] = "za malo punktow"
                wiersze.append(w)
                continue
            P2, N2 = f.punkty[maska], f.normalne[maska]
            fr = M.FragmentDoDopasowania.z_punktow(P2, N2)
            w["wysokosc_udzial"] = round(fr.wysokosc / pr.wysokosc, 3)
            for nazwa, fun in (("stary", filtr_sprzed_P1), ("nowy", M.filtr)):
                wyn = {k.id: fun(fr, k, ust) for k in pl.projekty.values()}
                w[f"filtr_{nazwa}_wlasciwy"] = bool(wyn[x.projekt][0])
                w[f"filtr_{nazwa}_powod"] = wyn[x.projekt][1].split(" ")[0]
                w[f"filtr_{nazwa}_przechodzi"] = int(sum(v[0] for v in wyn.values()))
                if z_dopasowaniem:
                    oryg = M.filtr
                    M.filtr = fun
                    try:
                        t0 = time.time()
                        r = M.dopasuj(P2, N2, pl, {**ust, "match": {**ust["match"], "korekta_skali": False}}, f.gniazdo)
                    finally:
                        M.filtr = oryg
                    w[f"top1_{nazwa}"] = bool(r.najlepszy is not None and r.najlepszy.id == x.projekt)
                    w[f"status_{nazwa}"] = r.status
                    w[f"pokrycie_{nazwa}"] = round(r.najlepszy.pokrycie, 4) if r.najlepszy else None
                    w[f"czas_{nazwa}_s"] = round(time.time() - t0, 2)
            wiersze.append(w)
    return {"wiersze": wiersze, "linia": f"{p.name}: prac {len({w['gniazdo'] for w in wiersze})}, wierszy {len(wiersze)}"}


def podsumuj_p1(wiersze: list[dict], pula_n: int | None = None) -> list[str]:
    out = ["scenariusz        prace  wys/proj (min-med)  wlasciwy odrzucony: stary / nowy   przechodzi filtr (srednio): stary / nowy"
           "   top-1: stary / nowy   zielony: stary / nowy   czas match na prace [s]: stary / nowy"]
    for grupa in sorted({w["scenariusz_pracy"] for w in wiersze}):
        for sc in dict.fromkeys(w["scenariusz"] for w in wiersze):
            ww = [w for w in wiersze if w["scenariusz"] == sc and w["scenariusz_pracy"] == grupa and "pominiety" not in w]
            if not ww:
                continue
            n = len(ww)
            h = [w["wysokosc_udzial"] for w in ww]
            wiersz = (f"{grupa + ' / ' + sc:26s} {n:4d}  {min(h):.2f}-{float(np.median(h)):.2f}   "
                      f"{sum(not w['filtr_stary_wlasciwy'] for w in ww):4d}/{n} / {sum(not w['filtr_nowy_wlasciwy'] for w in ww):4d}/{n}   "
                      f"{np.mean([w['filtr_stary_przechodzi'] for w in ww]):5.2f} / {np.mean([w['filtr_nowy_przechodzi'] for w in ww]):5.2f}")
            if "top1_stary" in ww[0]:
                wiersz += (f"   {sum(w['top1_stary'] for w in ww):4d}/{n} / {sum(w['top1_nowy'] for w in ww):4d}/{n}"
                           f"   {sum(w['status_stary'] == 'zielony' and w['top1_stary'] for w in ww):4d}/{n} / {sum(w['status_nowy'] == 'zielony' and w['top1_nowy'] for w in ww):4d}/{n}"
                           f"   {np.mean([w['czas_stary_s'] for w in ww]):5.2f} / {np.mean([w['czas_nowy_s'] for w in ww]):5.2f}")
            out.append(wiersz)
    return out


# ----------------------------------------------------------------------------
# P3: pelny program przy bledzie wspolczynnika
# ----------------------------------------------------------------------------
def zadanie_program(arg: tuple) -> dict:
    p, projekty, sufiks, plik_ust, blad, korekta = arg
    ust = UST.wczytaj_ustawienia(plik_ust)
    ust = {**ust, "match": {**ust["match"], "korekta_skali": korekta}}
    prawda = S.wczytaj_prawde(p.with_suffix(".json"))
    plytka = nazwa_plytki(prawda, sufiks)
    w_puli = wspolczynnik_prawdy(prawda) / (1 + blad / 100)
    pl = pula(projekty, w_puli)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        wynik = PO.porownaj(p, list(projekty), plytka, ust, w_puli, None, "auto", False, pl)
    baza = {"skan": p.name, "zestaw": p.parent.name, "plytka": plytka, "poranna": S.poranna(plytka), "blad_proc": blad, "korekta": korekta}
    if wynik.get("uklad_zgodny") is False:
        return {"rek": {**baza, "niezgodny": True}, "linia": f"{p.name} blad {blad:+.1f} korekta {korekta}: PLYTKA NIE PASUJE DO UKLADU"}
    mt = PO.metryki(wynik, prawda, pl)
    mi = PO.metryki_inspekcji(wynik, prawda)
    praw = {x.gniazdo: x for x in prawda.prace}
    prace = []
    for g in wynik["gniazda"]:
        if g["gniazdo"] not in praw or g["status_fragmentu"] not in ("praca", "podwojny"):
            continue
        x = praw[g["gniazdo"]]
        k = g["kandydaci"][0] if g["kandydaci"] else None
        sk = g.get("skala") or {}
        prace.append({"gniazdo": g["gniazdo"], "projekt": x.projekt, "scenariusz": PO.scenariusz(x), "ubytkow": len(x.ubytki), "poprawek": len(x.poprawki),
                      "top1": bool(k and k["id"] == x.projekt), "status": g["status"], "status_gniazda": g["status_gniazda"],
                      "inspekcja": g["inspekcja"]["status"] if g["inspekcja"] else None, "pokrycie": k["pokrycie"] if k else None,
                      "blad_prawdziwy_proc": round((x.wspolczynnik / w_puli - 1) * 100, 4),
                      "poprawka_proc": sk.get("poprawka_proc"), "zastosowana": sk.get("zastosowana"), "ostrzezenie": sk.get("ostrzezenie"),
                      "niepewna": sk.get("niepewna"), "powod": sk.get("powod"),
                      "pokrycie_przed": sk.get("pokrycie_przed"), "pokrycie_po": sk.get("pokrycie_po"), "czas_skali_s": sk.get("czas_s")})
    rek = {**baza, "czas_s": wynik["czas_s"], "metryki": {k: mt[k] for k in ("prac_prawda", "top1", "top2", "statusy", "wyrownanie_ok")},
           "inspekcja": mi, "statusy_gniazd": wynik["statusy_gniazd"], "prace": prace}
    r = mi["razem"]
    linia = (f"{p.name:38s} blad {blad:+5.1f} korekta {'tak' if korekta else 'nie'}: top1 {mt['top1']}/{mt['prac_prawda']} ubytki {r['ubytkow']} wykryte {r['wykryte']['dowolny']} "
             f"cale {r['prac_calych']} alarm {r['prace_cale_z_alarmem']} cz {r['prace_cale_z_czerwonym']} gniazda {wynik['statusy_gniazd']} {wynik['czas_s']['razem']} s")
    return {"rek": rek, "linia": linia}


def _estymata(prace: list[dict]) -> dict:
    """Blad estymaty skali (poprawka - blad prawdziwy) [punkty proc.] dla prac z trafnym top-1 i wyznaczona poprawka."""
    est = [x["poprawka_proc"] - x["blad_prawdziwy_proc"] for x in prace if x["top1"] and x["poprawka_proc"] is not None]
    return {"n": len(est), "w_celu": sum(abs(e) <= CEL_ESTYMATY_PROC for e in est), "srednia": round(float(np.mean(est)), 4) if est else None,
            "p95_abs": percentyl([abs(e) for e in est], 95), "max_abs": round(max((abs(e) for e in est), default=0.0), 4)}


def _est_tekst(e: dict) -> str:
    if not e["n"]:
        return "   0/   0"
    return f"{e['w_celu']:4d}/{e['n']:4d} sr {e['srednia']:+.4f} p95 {e['p95_abs']:.4f} max {e['max_abs']:.4f}"


def podsumuj_program(rekordy: list[dict]) -> tuple[list[dict], list[str]]:
    """Liczniki per (pora plytki, blad, korekta)."""
    grupy: dict[tuple, list[dict]] = {}
    for r in rekordy:
        if not r.get("niezgodny"):
            grupy.setdefault((r["poranna"], r["blad_proc"], r["korekta"]), []).append(r)
    tab, linie = [], []
    linie.append("pora      blad %  korekta  skanow  prace  top-1  top-2  match ziel/zolty/szary  gniazda ziel/czerw/zolte/szare/pom  ubytki wykr. dowolne/A/B/czerw."
                 "  cale: alarm/czerw.  falszywe (czerw.)  popraw_ul/skan_pon  zastos.  ostrzez.  niepewne  czas plytki med. [s]: match/inspect/razem")
    linie_est = ["", "estymata skali: |blad| <= 0,05 punktu proc. / prace z estymata (srednia, p95 |.|, max |.|)",
                 "pora      blad %  wszystkie                                       scenariusz dobrze                               estymaty wiarygodne (nie 'niepewna')            niepewne"]
    for (por, blad, kor), rr in sorted(grupy.items(), key=lambda kv: (kv[0][0], abs(kv[0][1]), -kv[0][1], not kv[0][2])):
        prace = [x for r in rr for x in r["prace"]]
        zb = {}
        for r in rr:
            for k, v in r["inspekcja"]["razem"].items():
                if isinstance(v, dict):
                    zb.setdefault(k, {})
                    for kk, vv in v.items():
                        zb[k][kk] = zb[k].get(kk, 0) + vv
                else:
                    zb[k] = zb.get(k, 0) + v
        w = {
            "poranna": por, "blad_proc": blad, "korekta": kor, "skanow": len(rr), "prac": sum(r["metryki"]["prac_prawda"] for r in rr),
            "top1": sum(r["metryki"]["top1"] for r in rr), "top2": sum(r["metryki"]["top2"] for r in rr),
            "statusy_match": {s: sum(r["metryki"]["statusy"][s] for r in rr) for s in M.STATUSY},
            "statusy_gniazd": {s: sum(r["statusy_gniazd"][s] for r in rr) for s in rr[0]["statusy_gniazd"]},
            "ubytkow": zb["ubytkow"], "wykryte": zb["wykryte"], "prac_calych": zb["prac_calych"], "prace_cale_z_alarmem": zb["prace_cale_z_alarmem"],
            "prace_cale_z_czerwonym": zb["prace_cale_z_czerwonym"], "falszywe_ubytki": zb["falszywe_ubytki"], "falszywe_czerwone": zb["falszywe_czerwone"],
            "inspekcja_statusy": zb["statusy"], "top1_bledny": zb["top1_bledny"], "bez_inspekcji": zb["bez_inspekcji"],
            "drgniecie": {k: sum(r["inspekcja"]["drgniecie"][k] for r in rr) for k in ("prac", "wykryte", "falszywe")},
            "estymata": _estymata(prace), "estymata_dobrze": _estymata([x for x in prace if x["scenariusz"] == "dobrze"]),
            "estymata_wiarygodna": _estymata([x for x in prace if not x["niepewna"]]),
            "estymata_niepewna": _estymata([x for x in prace if x["niepewna"]]),
            "korekta_zastosowana": sum(bool(x["zastosowana"]) for x in prace), "ostrzezen": sum(bool(x["ostrzezenie"]) for x in prace),
            "niepewnych": sum(bool(x["niepewna"]) for x in prace),
            "czas_s_mediana": {k: round(float(np.median([r["czas_s"][k] for r in rr])), 2) for k in ("match", "inspect", "razem")},
            "czas_skali_na_prace_s_mediana": percentyl([x["czas_skali_s"] for x in prace if x["czas_skali_s"] is not None], 50),
        }
        tab.append(w)
        sm, sg = w["statusy_match"], w["statusy_gniazd"]
        pora = "poranna" if por else "wieczorna"
        linie.append(f"{pora:9s} {blad:+5.1f}  {'tak' if kor else 'nie':7s} {w['skanow']:6d} {w['prac']:6d} {w['top1']:6d} {w['top2']:6d}  "
                     f"{sm['zielony']:4d}/{sm['zolty']:4d}/{sm['szary']:4d}      {sg['zielony']:4d}/{sg['czerwony']:4d}/{sg['zolty']:4d}/{sg['szary']:4d}/{sg['pomaranczowy']:3d}         "
                     f"{w['ubytkow']:4d}: {w['wykryte']['dowolny']:4d}/{w['wykryte']['A']:4d}/{w['wykryte']['B']:4d}/{w['wykryte']['czerwony']:4d}   "
                     f"{w['prac_calych']:4d}: {w['prace_cale_z_alarmem']:3d}/{w['prace_cale_z_czerwonym']:3d}   {w['falszywe_ubytki']:4d} ({w['falszywe_czerwone']:3d})   "
                     f"{w['inspekcja_statusy'].get('popraw_ulozenie', 0):4d}/{w['inspekcja_statusy'].get('skan_ponownie', 0):4d}   "
                     f"{w['korekta_zastosowana']:4d}   {w['ostrzezen']:4d}   {w['niepewnych']:4d}   {w['czas_s_mediana']['match']:.1f}/{w['czas_s_mediana']['inspect']:.1f}/{w['czas_s_mediana']['razem']:.1f}")
        if kor:
            linie_est.append(f"{pora:9s} {blad:+5.1f}  {_est_tekst(w['estymata']):46s}  {_est_tekst(w['estymata_dobrze']):46s}  {_est_tekst(w['estymata_wiarygodna']):46s}  {_est_tekst(w['estymata_niepewna'])}")
    linie += linie_est
    return tab, linie


# ----------------------------------------------------------------------------
# P3: strefa brzegu a estymata skali (zastrzezenie R2b)
# ----------------------------------------------------------------------------
PASY = {"A": (0.3, 0.5, "liniowo"), "C": (1.4, 2.0, "kosinus")}  # pelna zmiana do [mm od brzegu], wygaszenie do [mm]


def waga_pasa(glebokosc: np.ndarray, pas: str) -> np.ndarray:
    a, b, jak = PASY[pas]
    t = np.clip((glebokosc - a) / (b - a), 0.0, 1.0)
    return 1.0 - t if jak == "liniowo" else 0.5 * (1.0 + np.cos(np.pi * t))


def zaburz_brzeg(P: np.ndarray, N: np.ndarray, T_plytka_do_puli: np.ndarray, wariant: str, wielkosc: float, rng: np.random.Generator) -> np.ndarray:
    """Punkty fragmentu ze zmieniona strefa brzegu. Warianty: ``grubosc+A`` / ``grubosc-A`` / ``grubosc+C`` / ``grubosc-C``
    (przesuniecie wzdluz normalnych o +-wielkosc w pasie), ``z+A`` / ``z-A`` (przesuniecie wzdluz osi pracy),
    ``ukruszenia`` (3 czasze fi 1,0 mm, glebokosc 0,35 mm, srodki do 1 mm od brzegu)."""
    X = P @ T_plytka_do_puli[:3, :3].T + T_plytka_do_puli[:3, 3]
    gl = -X[:, 2]  # glebokosc od brzegu (z = 0 w ukladzie puli)
    if wariant == "ukruszenia":
        P2 = P.copy()
        kand = np.flatnonzero(gl <= 1.0)
        for i in rng.choice(kand, size=min(3, len(kand)), replace=False):
            d = np.linalg.norm(P - P[i], axis=1)
            P2 -= N * (0.35 * np.clip(1 - (d / 0.5) ** 2, 0.0, None))[:, None]
        return P2
    rodzaj, pas = wariant[:-2], wariant[-1]
    znak = 1.0 if wariant[-2] == "+" else -1.0
    w = waga_pasa(gl, pas) * znak * wielkosc
    if rodzaj == "grubosc":
        return P + N * w[:, None]
    if rodzaj == "z":
        return P + (T_plytka_do_puli[:3, :3].T @ np.array([0.0, 0.0, 1.0]))[None] * w[:, None]
    raise ValueError(f"nieznany wariant {wariant!r}")


WARIANTY_BRZEGU = ("powtorka", "grubosc+A", "grubosc-A", "z+A", "z-A", "grubosc+C", "grubosc-C", "ukruszenia")


def estymata_pracy(P: np.ndarray, N: np.ndarray, pr: M.Projekt, ust: dict, pas_mm: float, seed: int) -> float | None:
    """Poprawka skali [%] dla jednej pary fragment - projekt sciezka programu (dopasuj_pare + koryguj_skale)."""
    fr = M.FragmentDoDopasowania.z_punktow(P, N)
    k = M.dopasuj_pare(fr, pr, ust, seed)
    if k.transformacja is None:
        return None
    M.koryguj_skale(P, fr, k, pr, {**ust["match"], "korekta_skali": True, "korekta_skali_pas_brzegu_mm": pas_mm})
    return k.skala.poprawka_proc


def zadanie_brzeg(arg: tuple) -> dict:
    p, projekty, sufiks, plik_ust, wielkosc = arg
    ust = UST.wczytaj_ustawienia(plik_ust)
    prawda = S.wczytaj_prawde(p.with_suffix(".json"))
    plytka = nazwa_plytki(prawda, sufiks)
    uk = U.wczytaj(plytka, UST.katalog_plytki(ust, plytka))
    pl = pula(projekty, wspolczynnik_prawdy(prawda))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        wyr = PL.wyrownaj(trimesh.load(p, force="mesh"), uk)
    praw = {x.gniazdo: x for x in prawda.prace}
    pas_ust = ust["match"]["korekta_skali_pas_brzegu_mm"]
    wiersze = []
    for f in wyr.fragmenty:
        x = praw.get(f.gniazdo)
        if f.status != "praca" or x is None or x.projekt not in pl.projekty or PO.scenariusz(x) != "dobrze":
            continue
        pr = pl.projekty[x.projekt]
        T = pr.T0 @ np.linalg.inv(np.array(x.transformacja))  # plytka -> uklad puli (prawda)
        rng = np.random.default_rng(1000 * prawda.seed + f.gniazdo)
        w = {"skan": p.name, "plytka": plytka, "gniazdo": f.gniazdo, "projekt": x.projekt, "ubytkow": len(x.ubytki)}
        for pas_mm, nazwa in ((pas_ust, "pas"), (0.0, "bez_pasa")):
            e0 = estymata_pracy(f.punkty, f.normalne, pr, ust, pas_mm, 0)
            w[f"{nazwa}_bez_zmian"] = e0
            for wariant in WARIANTY_BRZEGU:
                P2 = f.punkty if wariant == "powtorka" else zaburz_brzeg(f.punkty, f.normalne, T, wariant, wielkosc, np.random.default_rng(rng.integers(1 << 30)))
                e = estymata_pracy(P2, f.normalne, pr, ust, pas_mm, 1 if wariant == "powtorka" else 0)
                w[f"{nazwa}_{wariant}"] = None if e is None or e0 is None else round(e - e0, 4)
        wiersze.append(w)
    return {"wiersze": wiersze, "linia": f"{p.name}: prac {len(wiersze)}"}


def podsumuj_brzeg(wiersze: list[dict], prog: float) -> list[str]:
    out = [f"zmiana estymaty skali [punkty proc.] wzgledem tej samej pracy bez zmian; prac {len(wiersze)}; prog = {prog} (szum estymaty)",
           "wariant        z wylaczeniem pasa brzegu: |zmiana| <= prog, srednia, p95 |.|, max |.|      bez wylaczenia (pas 0): |zmiana| <= prog, srednia, p95 |.|, max |.|"]
    for wariant in WARIANTY_BRZEGU:
        cz = []
        for nazwa in ("pas", "bez_pasa"):
            v = [w[f"{nazwa}_{wariant}"] for w in wiersze if w.get(f"{nazwa}_{wariant}") is not None]
            cz.append(f"{sum(abs(x) <= prog for x in v):4d}/{len(v):<4d} {float(np.mean(v)) if v else float('nan'):+.4f}  {percentyl([abs(x) for x in v], 95) or 0:.4f}  {max((abs(x) for x in v), default=0):.4f}")
        out.append(f"{wariant:14s} {cz[0]}                              {cz[1]}")
    return out


# ----------------------------------------------------------------------------
def uruchom(fun, zadania: list, procesy: int) -> list[dict]:
    wyniki = []
    if procesy > 1:
        with mp.Pool(procesy) as pool:
            it = pool.imap(fun, zadania)
            for _ in zadania:
                odp = it.next(timeout=LIMIT_ZADANIA_S)
                print(odp["linia"], flush=True)
                wyniki.append(odp)
    else:
        for z in zadania:
            odp = fun(z)
            print(odp["linia"], flush=True)
            wyniki.append(odp)
    return wyniki


def main(argv: list[str] | None = None) -> dict:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("tryb", choices=("p1", "program", "brzeg"))
    ap.add_argument("--skany", type=Path, nargs="+", required=True, help="foldery ze skanami skan_*.stl i prawda skan_*.json")
    ap.add_argument("--projekty", type=Path, nargs="+", required=True)
    ap.add_argument("--wyjscie", type=Path, required=True)
    ap.add_argument("--nazwa", default=None, help="nazwa pliku wyniku (domyslnie metryki_skala_<tryb>.json)")
    ap.add_argument("--wzorzec", default="skan_*.stl")
    ap.add_argument("--limit", type=int, default=None, help="tylko pierwsze N skanow kazdego zestawu")
    ap.add_argument("--sufiks-ukladu", default="", help="przyrostek ukladu dla zestawow sprzed R59, np. _r54")
    ap.add_argument("--ustawienia", type=Path, default=None)
    ap.add_argument("--procesy", type=int, default=1)
    ap.add_argument("--scenariusze", nargs="+", default=list(SCENARIUSZE_P1), choices=SCENARIUSZE_P1, help="p1: scenariusze widocznosci")
    ap.add_argument("--dopasuj", action="store_true", help="p1: takze pelne match.dopasuj starym i nowym filtrem (top-1, status, czas)")
    ap.add_argument("--bledy", default=",".join(str(b) for b in BLEDY), help="program: bledy wspolczynnika puli w procentach, po przecinku")
    ap.add_argument("--korekta", nargs="+", default=["tak", "nie"], choices=("tak", "nie"), help="program: z korekta skali / bez")
    ap.add_argument("--wielkosc", type=float, default=0.02, help="brzeg: wielkosc zmiany strefy brzegu [mm]")
    ap.add_argument("--prog", type=float, default=0.02, help="brzeg: prog 'bez zmiany' [punkty proc.] = szum estymaty")
    a = ap.parse_args(argv)
    UST.wczytaj_ustawienia(a.ustawienia)
    skany = [p for d in a.skany for p in sorted(d.glob(a.wzorzec))[: a.limit]]
    if not skany:
        raise SystemExit(f"brak skanow w {a.skany}")
    a.wyjscie.mkdir(parents=True, exist_ok=True)
    proj = tuple(a.projekty)
    t0 = time.time()
    if a.tryb == "p1":
        odp = uruchom(zadanie_p1, [(p, proj, a.sufiks_ukladu, a.ustawienia, tuple(a.scenariusze), a.dopasuj) for p in skany], a.procesy)
        wiersze = [w for o in odp for w in o["wiersze"]]
        linie = podsumuj_p1(wiersze)
        out = {"tryb": "p1", "wiersze": wiersze, "tabela": linie}
    elif a.tryb == "program":
        bledy = [float(b) for b in a.bledy.split(",")]
        zadania = [(p, proj, a.sufiks_ukladu, a.ustawienia, b, k == "tak") for b in bledy for k in a.korekta for p in skany]
        odp = uruchom(zadanie_program, zadania, a.procesy)
        rekordy = [o["rek"] for o in odp]
        tab, linie = podsumuj_program(rekordy)
        out = {"tryb": "program", "zbiorczo": tab, "tabela": linie, "skany": rekordy}
    else:
        odp = uruchom(zadanie_brzeg, [(p, proj, a.sufiks_ukladu, a.ustawienia, a.wielkosc) for p in skany], a.procesy)
        wiersze = [w for o in odp for w in o["wiersze"]]
        linie = podsumuj_brzeg(wiersze, a.prog)
        out = {"tryb": "brzeg", "wielkosc_mm": a.wielkosc, "prog": a.prog, "wiersze": wiersze, "tabela": linie}
    out["czas_calosci_s"] = round(time.time() - t0, 1)
    plik = a.wyjscie / (a.nazwa or f"metryki_skala_{a.tryb}.json")
    plik.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print()
    print("\n".join(linie))
    print(plik)
    return out


if __name__ == "__main__":
    main()
