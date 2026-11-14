"""Pojemnosc plytek: ile prac z puli projektow miesci sie na plytce - uklad R59 i poprzedni R54 (R59, krok 7).

Uzycie (z katalogu stanowisko/):
    py -3.12 narzedzia/pojemnosc_R59.py --projekty C:/.../Prace_test [--wyjscie dane/pojemnosc_R59] [--seedy 20]
        [--seed0 5000] [--procesy 12] [--plytki wieczorna wieczorna_r54 poranna poranna_r54] [--powtorz 3 --tylko-pierwsza]

Dla kazdego ukladu i seeda generator (``synth.generuj_plytke``, ta sama procedura doboru gniazda co w skanach) uklada
cala pule na jednej plytce: plytki wieczorne ze skurczem 1,22, poranne 1,0. Potem z prac, ktore sie nie zmiescily,
uklada kolejne plytki, az nic wiecej nie wejdzie. Liczy: prace osadzone / pominiete na pierwszej plytce, zajetosc
gniazd per srednica, ile prac trafia do rynienki (mosty i korony, ktore nie weszly w gniazda okragle), ile plytek
trzeba na cala pule i ktore projekty nie wchodza na zadna. Plytki okragle maja te same gniazda co kwadrat tego typu.
``--powtorz N`` bierze kazdy projekt N razy (plytka pelna: ile prac wchodzi najwyzej), ``--tylko-pierwsza`` nie uklada
kolejnych plytek.
Wynik: ``<wyjscie>/pojemnosc_R59.json`` i tabele na stdout - projekty tylko jako skroty SHA-16, bez nazw plikow.
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import sys
import time
import warnings
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

LIMIT_ZADANIA_S = 1200
MAKS_PLYTEK = 8  # gorna granica liczby kolejnych plytek na jeden seed


def klasa(g) -> str:
    return f"fi{g.d_top:g}" if g.okragle else "rynienka"


def zadanie(arg: tuple) -> dict:
    plytka, seed, projekty, w, maks_plytek = arg
    from stanowisko import synth as S, uklad as U, ustawienia as UST

    ust = UST.wczytaj_ustawienia()
    uk = U.wczytaj(plytka, UST.katalog_plytki(ust, plytka))
    klasy = {g.id: klasa(g) for g in uk.sockets}
    op = S.Opcje.z_toml(ust, plytka, wspolczynnik=(w, w), ubytki_na_prace=(0, 0), szum_sigma=0.0)
    skroty = {S.skrot_pliku(p): p for p in projekty}
    zostalo = list(projekty)
    plytki = []
    for k in range(maks_plytek):
        if not zostalo:
            break
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            _, prawda = S.generuj_plytke(uk, uk.numery[0], zostalo, np.random.default_rng(seed * 100 + k), op, seed)
        if not prawda.prace:
            break
        plytki.append({"prace": [{"projekt": p.projekt, "gniazdo": p.gniazdo, "klasa": klasy[p.gniazdo]} for p in prawda.prace], "pominiete": list(prawda.pominiete)})
        zostalo = [skroty[h] for h in prawda.pominiete]
    return {"plytka": plytka, "seed": seed, "wspolczynnik": w, "plytki": plytki, "nie_wchodza": sorted(S.skrot_pliku(p) for p in zostalo)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--projekty", type=Path, required=True)
    ap.add_argument("--wyjscie", type=Path, default=Path("dane/pojemnosc_R59"))
    ap.add_argument("--seedy", type=int, default=20)
    ap.add_argument("--seed0", type=int, default=5000)
    ap.add_argument("--procesy", type=int, default=12)
    ap.add_argument("--plytki", nargs="+", default=["wieczorna", "wieczorna_r54", "poranna", "poranna_r54"])
    ap.add_argument("--wspolczynnik", type=float, default=1.22, help="skurcz dla plytek wieczornych")
    ap.add_argument("--powtorz", type=int, default=1, help="ile razy wziac kazdy projekt (pula x N)")
    ap.add_argument("--tylko-pierwsza", action="store_true", help="tylko pierwsza plytka (bez ukladania reszty na kolejnych)")
    a = ap.parse_args()
    import trimesh

    from stanowisko import katalog as K, synth as S, uklad as U, ustawienia as UST

    ust = UST.wczytaj_ustawienia()
    projekty = S.pliki_projektow(a.projekty)
    if not projekty:
        raise SystemExit(f"brak plikow STL w {a.projekty}")
    a.wyjscie.mkdir(parents=True, exist_ok=True)
    # cechy projektow (bez nazw): typ z nazwy exocad, szerokosc po skurczu, czy most wg generatora
    cechy = {}
    for p in projekty:
        m = S.wczytaj_projekt(p)
        h = S.skrot_pliku(p)
        typ = K.typ_i_zeby_z_nazwy(p.name)[0]
        m.apply_transform(S.orientacja_brzegiem_do_gory(m, "auto", p.name))
        _, boki = trimesh.bounds.oriented_bounds_2D(m.vertices[:, :2])
        cechy[h] = {"typ": typ, "obrys_mm": [round(float(min(boki)), 1), round(float(max(boki)), 1)]}
    uklady = {n: U.wczytaj(n, UST.katalog_plytki(ust, n)) for n in a.plytki}
    wsp = {n: (1.0 if S.poranna(n) else a.wspolczynnik) for n in a.plytki}
    pula = list(projekty) * a.powtorz
    zadania = [(n, a.seed0 + s, pula, wsp[n], 1 if a.tylko_pierwsza else MAKS_PLYTEK) for n in a.plytki for s in range(a.seedy)]
    print(f"projektow {len(projekty)} x {a.powtorz}, ukladow {len(a.plytki)}, seedow {a.seedy}, zadan {len(zadania)}, procesow {a.procesy}", flush=True)
    t0 = time.time()
    wyniki = []
    with mp.Pool(a.procesy) as pool:
        it = pool.imap_unordered(zadanie, zadania)
        for n in range(len(zadania)):
            r = it.next(timeout=LIMIT_ZADANIA_S)
            wyniki.append(r)
            if (n + 1) % 10 == 0:
                print(f"[{n + 1}/{len(zadania)} {time.time() - t0:5.0f} s]", flush=True)
    zb = {}
    for n in a.plytki:
        uk = uklady[n]
        r = sorted((x for x in wyniki if x["plytka"] == n), key=lambda x: x["seed"])
        gniazd = Counter(klasa(g) for g in uk.sockets)
        pierwsze = [x["plytki"][0] if x["plytki"] else {"prace": [], "pominiete": []} for x in r]
        osadzone = [len(p["prace"]) for p in pierwsze]
        zaj = {k: [sum(1 for q in p["prace"] if q["klasa"] == k) for p in pierwsze] for k in gniazd}
        w = wsp[n]
        most = {h: c["obrys_mm"][1] * w > S.PROG_MOSTU_MM for h, c in cechy.items()}
        w_rynience = [[q["projekt"] for q in p["prace"] if q["klasa"] == "rynienka"] for p in pierwsze]
        per_projekt = {}
        for h in cechy:
            gdzie = Counter(q["klasa"] for p in pierwsze for q in p["prace"] if q["projekt"] == h)
            per_projekt[h] = {"typ": cechy[h]["typ"], "obrys_po_skurczu_mm": [round(v * w, 1) for v in cechy[h]["obrys_mm"]], "most_wg_generatora": most[h],
                              "na_pierwszej_plytce": sum(gdzie.values()), "gdzie": dict(gdzie), "nigdy_nie_wchodzi": sum(1 for x in r if h in x["nie_wchodza"])}
        zb[n] = {
            "wspolczynnik": w, "seedow": len(r), "projektow": len(cechy), "prac_w_puli": len(pula), "gniazd": dict(gniazd), "gniazd_razem": len(uk.sockets),
            "osadzone_srednio": round(float(np.mean(osadzone)), 2), "osadzone_min": int(min(osadzone)), "osadzone_max": int(max(osadzone)),
            "pominiete_srednio": round(float(np.mean([len(p["pominiete"]) for p in pierwsze])), 2),
            "zajete_gniazda_srednio": {k: round(float(np.mean(v)), 2) for k, v in zaj.items()},
            "zajetosc_udzial": {k: round(float(np.mean(v)) / gniazd[k], 3) for k, v in zaj.items()},
            "w_rynience_srednio": round(float(np.mean([len(x) for x in w_rynience])), 2),
            "w_rynience_mosty_srednio": round(float(np.mean([sum(most[h] for h in x) for x in w_rynience])), 2),
            "w_rynience_korony_srednio": round(float(np.mean([sum(not most[h] for h in x) for x in w_rynience])), 2),
            "prac_tylko_do_rynienki_w_puli": sum(most.values()) * a.powtorz,
            "plytek_na_pule_srednio": round(float(np.mean([len(x["plytki"]) for x in r])), 2), "plytek_na_pule_min": min(len(x["plytki"]) for x in r),
            "plytek_na_pule_max": max(len(x["plytki"]) for x in r),
            "nie_wchodza_nigdzie_srednio": round(float(np.mean([len(x["nie_wchodza"]) for x in r])), 2),
            "tylko_pierwsza_plytka": bool(a.tylko_pierwsza),  # wtedy liczby "plytek na pule" i "nie wchodza nigdzie" nie maja znaczenia
            "per_projekt": per_projekt,
        }
    (a.wyjscie / "pojemnosc_R59.json").write_text(json.dumps({"zbiorczo": zb, "cechy_projektow": cechy, "przebiegi": wyniki}, ensure_ascii=True, indent=1), encoding="utf-8")
    print("\nuklad | wsp. | gniazd | osadzone na 1. plytce: srednio (min-max) z", len(pula), "| pominiete srednio | w rynience (mosty + korony) | plytek na cala pule: srednio (min-max) | nie wchodza nigdzie")
    for n, v in zb.items():
        print(f"{n} | {v['wspolczynnik']} | {v['gniazd_razem']} | {v['osadzone_srednio']} ({v['osadzone_min']}-{v['osadzone_max']}) | {v['pominiete_srednio']} | "
              f"{v['w_rynience_srednio']} ({v['w_rynience_mosty_srednio']} + {v['w_rynience_korony_srednio']}) | "
              + ("- | -" if a.tylko_pierwsza else f"{v['plytek_na_pule_srednio']} ({v['plytek_na_pule_min']}-{v['plytek_na_pule_max']}) | {v['nie_wchodza_nigdzie_srednio']}"))
    print("\nzajetosc gniazd na 1. plytce (srednio zajetych / gniazd tej srednicy):")
    for n, v in zb.items():
        print(f"{n}: " + ", ".join(f"{k} {v['zajete_gniazda_srednio'][k]}/{v['gniazd'][k]}" for k in sorted(v["gniazd"])))
    print("\nprojekt (SHA-16) | typ | obrys w pliku [mm] | " + " | ".join(f"{n}: na 1. plytce / seedow (gdzie)" for n in zb))
    for h in sorted(cechy, key=lambda h: (cechy[h]["typ"], cechy[h]["obrys_mm"][1])):
        kom = []
        for n, v in zb.items():
            pp = v["per_projekt"][h]
            kom.append(f"{pp['na_pierwszej_plytce']}/{v['seedow']} ({', '.join(f'{k} {c}' for k, c in sorted(pp['gdzie'].items())) or '-'})" + (f" nigdzie {pp['nigdy_nie_wchodzi']}" if pp["nigdy_nie_wchodzi"] and not a.tylko_pierwsza else ""))
        print(f"{h} | {cechy[h]['typ']} | {cechy[h]['obrys_mm'][0]} x {cechy[h]['obrys_mm'][1]} | " + " | ".join(kom))
    print(a.wyjscie / "pojemnosc_R59.json")


if __name__ == "__main__":
    main()
