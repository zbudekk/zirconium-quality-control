"""Metryki plate + match na całym zestawie sztucznych skanów z prawdą (sesja P2).

Użycie (z katalogu stanowisko/):
    py -3.12 narzedzia/metryki_P2.py --skany dane/syntetyczne_P2 --projekty C:/Users/.../Prace_test
        [--dodatkowe dane/stl] [--wyjscie dane/wyniki_P2] [--wspolczynniki 1.20 1.25]

Dla każdego skanu: plate raz, potem match w wariantach: pula podstawowa (z filtrem i bez),
pula rozszerzona o ``--dodatkowe`` (z filtrem i bez), a dla płytek wieczornych dodatkowo
czułość na współczynnik (pula ×``--wspolczynniki`` zamiast prawdziwego 1,22).
Wynik: ``<wyjscie>/metryki_P2.json`` (per skan i zbiorczo) i tabela na stdout — bez nazw plików projektów.

Sztuczne skany są danymi do budowy i pomiaru kodu; test skanera będzie w P3 na prawdziwych płytkach.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import trimesh

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from stanowisko import match as M  # noqa: E402
from stanowisko import plate as PL  # noqa: E402
from stanowisko import porownaj as PO  # noqa: E402
from stanowisko import synth as S  # noqa: E402
from stanowisko import uklad as U  # noqa: E402
from stanowisko import ustawienia as UST  # noqa: E402


def zbiorczo(wyniki: list[dict], klucz: str) -> dict:
    """Sumy top‑1/top‑2/statusów po wszystkich skanach dla wariantu ``klucz``."""
    n = top1 = top2 = 0
    statusy = {s: 0 for s in M.STATUSY}
    zle_zielone = 0  # zielony status, a top‑1 błędny = fałszywa pewność
    pokrycia_ok, pokrycia_zle = [], []
    czas = 0.0
    for w in wyniki:
        mt = w["warianty"][klucz]
        n += mt["prac_prawda"]
        top1 += mt["top1"]
        top2 += mt["top2"]
        for s in M.STATUSY:
            statusy[s] += mt["statusy"][s]
        zle_zielone += mt["zielone_bledne"]
        pokrycia_ok += mt["pokrycia_top1_trafne"]
        pokrycia_zle += mt["pokrycia_top1_bledne"]
        czas += mt["czas_match_s"]
    return {
        "fragmentow": n, "top1": top1, "top2": top2,
        "top1_udzial": round(top1 / n, 4) if n else None, "top2_udzial": round(top2 / n, 4) if n else None,
        "statusy": statusy, "zielone_bledne": zle_zielone,
        "pokrycie_trafnych_min": round(min(pokrycia_ok), 3) if pokrycia_ok else None,
        "pokrycie_trafnych_mediana": round(float(np.median(pokrycia_ok)), 3) if pokrycia_ok else None,
        "pokrycie_blednych_max": round(max(pokrycia_zle), 3) if pokrycia_zle else None,
        "czas_match_s_na_plytke": round(czas / len(wyniki), 1) if wyniki else None,
    }


def wariant(wyr: PL.WynikWyrownania, pula: M.Pula, ust: dict, bez_filtru: bool, prawda: S.PrawdaPlytki, wynik_bazowy: dict) -> dict:
    t0 = time.time()
    gniazda = PO.dopasuj_fragmenty(wyr, pula, ust, bez_filtru)
    w = {**wynik_bazowy, "gniazda": gniazda}
    mt = PO.metryki(w, prawda, pula)
    praw = {p.gniazdo: p for p in prawda.prace}
    traf, bled, ziel_bled = [], [], 0
    for g in gniazda:
        if g["gniazdo"] not in praw or not g["kandydaci"]:
            continue
        k = g["kandydaci"][0]
        if k["id"] == praw[g["gniazdo"]].projekt:
            traf.append(k["pokrycie"])
        else:
            bled.append(k["pokrycie"])
            ziel_bled += g["status"] == "zielony"
    mt.update({"pokrycia_top1_trafne": traf, "pokrycia_top1_bledne": bled, "zielone_bledne": ziel_bled, "czas_match_s": round(time.time() - t0, 1),
               "pula": len(pula), "bez_filtru": bez_filtru, "wspolczynnik_puli": pula.wspolczynnik,
               "metody": {m: sum(1 for g in gniazda if g["kandydaci"] and g["kandydaci"][0]["metoda"] == m) for m in ("ransac", "obroty")}})
    return mt


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--skany", type=Path, default=Path("dane/syntetyczne_P2"))
    ap.add_argument("--projekty", type=Path, nargs="+", required=True)
    ap.add_argument("--dodatkowe", type=Path, nargs="*", default=[], help="folder(y) dodatkowych projektów (pula rozszerzona)")
    ap.add_argument("--wyjscie", type=Path, default=Path("dane/wyniki_P2"))
    ap.add_argument("--wspolczynniki", type=float, nargs="*", default=[1.20, 1.25], help="czułość na współczynnik (płytki wieczorne)")
    ap.add_argument("--limit", type=int, default=None, help="tylko pierwsze N skanów (próba)")
    ap.add_argument("--wzorzec", default="skan_*.stl", help="wzorzec nazw skanów (np. skan_*wieczorna*.stl)")
    ap.add_argument("--nazwa", default="metryki_P2.json", help="nazwa pliku wyniku w --wyjscie")
    a = ap.parse_args()
    ust = UST.wczytaj_ustawienia()
    skany = sorted(a.skany.glob(a.wzorzec))[: a.limit]
    if not skany:
        raise SystemExit(f"brak skanów w {a.skany}")
    a.wyjscie.mkdir(parents=True, exist_ok=True)
    pule: dict[tuple, M.Pula] = {}

    def pula(w: float, rozszerzona: bool) -> M.Pula:
        k = (w, rozszerzona)
        if k not in pule:
            pule[k] = M.Pula(list(a.projekty) + (list(a.dodatkowe) if rozszerzona else []), w)
        return pule[k]

    wyniki = []
    t_start = time.time()
    for p in skany:
        prawda = S.wczytaj_prawde(p.with_suffix(".json"))
        uk = U.wczytaj(prawda.plytka, UST.katalog_plytki(ust, prawda.plytka))
        w_prawdy = float(np.mean([x.wspolczynnik for x in prawda.prace])) if prawda.prace else 1.0
        t0 = time.time()
        m = trimesh.load(p, force="mesh")
        t1 = time.time()
        with warnings.catch_warnings(record=True) as ostrz:
            warnings.simplefilter("always")
            wyr = PL.wyrownaj(m, uk)  # bez --numer: kwadrat → nieznany (dołki poza polem)
        t2 = time.time()
        bl = PL.blad_wyrownania(wyr.macierz, prawda.poza_skanu)
        baza = {"skan": p.name, "plytka": prawda.plytka, "numer": wyr.numer, "numer_zrodlo": wyr.numer_zrodlo, "bity": wyr.bity, "numer_z_dolkow": wyr.numer_z_dolkow,
                "macierz_skan_do_plytki": wyr.macierz.tolist(), "gniazda_puste": wyr.gniazda_puste, "gniazda_podwojne": wyr.gniazda_podwojne,
                "poza_gniazdem": sum(1 for f in wyr.fragmenty if f.status == "poza_gniazdem"), "wspolczynnik": w_prawdy}
        warianty = {
            "pula_podstawowa_filtr": wariant(wyr, pula(w_prawdy, False), ust, False, prawda, baza),
            "pula_podstawowa_bez_filtru": wariant(wyr, pula(w_prawdy, False), ust, True, prawda, baza),
        }
        if a.dodatkowe:
            warianty["pula_rozszerzona_filtr"] = wariant(wyr, pula(w_prawdy, True), ust, False, prawda, baza)
            warianty["pula_rozszerzona_bez_filtru"] = wariant(wyr, pula(w_prawdy, True), ust, True, prawda, baza)
        if not S.poranna(prawda.plytka):
            for wsp in a.wspolczynniki:
                warianty[f"wspolczynnik_{wsp}"] = wariant(wyr, pula(wsp, False), ust, False, prawda, baza)
        rek = {
            "skan": p.name, "plytka": prawda.plytka, "seed": prawda.seed, "wierzcholki": int(len(m.vertices)), "trojkaty": int(len(m.faces)),
            "czas_s": {"wczytanie": round(t1 - t0, 2), "plate": round(t2 - t1, 2)},
            "wyrownanie": bl, "wyrownanie_ok": bl["max_przesuniecie_mm"] < 0.05, "jakosc_wyrownania": wyr.jakosc,
            "numer_prawda": prawda.numer, "numer": wyr.numer, "numer_zrodlo": wyr.numer_zrodlo, "numer_z_dolkow": wyr.numer_z_dolkow, "bity": wyr.bity,
            "numer_ok": wyr.numer == prawda.numer, "dolki_widoczne": all(b is not None for b in wyr.bity),
            "dolki_odczyt_poprawny_lub_niewidoczne": (wyr.numer_z_dolkow == prawda.numer) if all(b is not None for b in wyr.bity) else True,
            "prac_prawda": len(prawda.prace), "fragmentow_praca": sum(1 for f in wyr.fragmenty if f.status in ("praca", "podwojny")),
            "fragment_w_swoim_gniezdzie": sum(1 for f in wyr.fragmenty if f.status in ("praca", "podwojny") and f.gniazdo in {x.gniazdo for x in prawda.prace}),
            "puste_ok": set(wyr.gniazda_puste) == set(prawda.gniazda_puste), "podwojne": wyr.gniazda_podwojne, "poza_gniazdem": baza["poza_gniazdem"],
            "drobne": sum(1 for f in wyr.fragmenty if f.status == "drobny"), "drgniecia": sum(1 for x in prawda.prace if x.drgniecie),
            "ostrzezenia": [str(o.message) for o in ostrz], "warianty": warianty,
        }
        wyniki.append(rek)
        v = warianty["pula_podstawowa_filtr"]
        print(f"{p.name:40s} wyr {bl['max_przesuniecie_mm']:.4f} mm  numer {str(wyr.numer):4s} ({wyr.numer_zrodlo:8s}) prawda {prawda.numer}  "
              f"gniazda {rek['fragment_w_swoim_gniezdzie']}/{rek['prac_prawda']} puste {'OK' if rek['puste_ok'] else 'ZLE'}  "
              f"top1 {v['top1']}/{v['prac_prawda']} top2 {v['top2']}/{v['prac_prawda']}  plate {rek['czas_s']['plate']} s  match {v['czas_match_s']} s", flush=True)

    klucze = list(wyniki[0]["warianty"]) if wyniki else []
    for k in list(dict.fromkeys(kk for w in wyniki for kk in w["warianty"])):
        if k not in klucze:
            klucze.append(k)
    zb = {}
    for k in klucze:
        podzbior = [w for w in wyniki if k in w["warianty"]]
        zb[k] = zbiorczo(podzbior, k)
        zb[k]["skanow"] = len(podzbior)
    n = len(wyniki)
    plate_zb = {
        "skanow": n,
        "wyrownanie_ok": sum(w["wyrownanie_ok"] for w in wyniki),
        "wyrownanie_max_przesuniecie_mm_max": max(w["wyrownanie"]["max_przesuniecie_mm"] for w in wyniki),
        "wyrownanie_max_przesuniecie_mm_mediana": float(np.median([w["wyrownanie"]["max_przesuniecie_mm"] for w in wyniki])),
        "wyrownanie_translacja_mm_max": max(w["wyrownanie"]["translacja_mm"] for w in wyniki),
        "wyrownanie_obrot_deg_max": max(w["wyrownanie"]["obrot_deg"] for w in wyniki),
        "numer_z_dolkow_ok_gdy_widoczne": sum(1 for w in wyniki if w["dolki_widoczne"] and w["numer_z_dolkow"] == w["numer_prawda"]),
        "dolki_widoczne": sum(w["dolki_widoczne"] for w in wyniki),
        "dolki_niewidoczne_zgloszone": sum(1 for w in wyniki if not w["dolki_widoczne"] and w["numer_zrodlo"] == "nieznany"),
        "numer_bledny_odczyt": sum(1 for w in wyniki if w["dolki_widoczne"] and w["numer_z_dolkow"] != w["numer_prawda"]),
        "prac_prawda": sum(w["prac_prawda"] for w in wyniki),
        "fragment_w_swoim_gniezdzie": sum(w["fragment_w_swoim_gniezdzie"] for w in wyniki),
        "fragmentow_praca": sum(w["fragmentow_praca"] for w in wyniki),
        "puste_ok": sum(w["puste_ok"] for w in wyniki),
        "podwojne_falszywe": sum(len(w["podwojne"]) for w in wyniki),
        "poza_gniazdem_falszywe": sum(w["poza_gniazdem"] for w in wyniki),
        "drobne": sum(w["drobne"] for w in wyniki),
        "czas_plate_s_mediana": float(np.median([w["czas_s"]["plate"] for w in wyniki])),
        "czas_wczytania_s_mediana": float(np.median([w["czas_s"]["wczytanie"] for w in wyniki])),
        "czas_calosci_s": round(time.time() - t_start, 1),
    }
    out = {"skany": wyniki, "plate": plate_zb, "match": zb, "pule": {f"{k[0]}_{'rozszerzona' if k[1] else 'podstawowa'}": len(v) for k, v in pule.items()}}
    (a.wyjscie / a.nazwa).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\nPLATE:", json.dumps(plate_zb, ensure_ascii=False))
    for k, v in zb.items():
        print(f"MATCH {k}: {json.dumps(v, ensure_ascii=False)}")
    print(a.wyjscie / a.nazwa)


if __name__ == "__main__":
    main()
