"""Pomiar straznika ukladu (R59): plytka zgodna i niezgodna z wybranym ukladem, pusta / czesciowo zajeta / pelna.

Uzycie (z katalogu stanowisko/):
    py -3.12 narzedzia/straznik_R59.py --projekty C:/.../Prace_test [--wyjscie dane/straznik_R59] [--seedy 5]
        [--seed0 7200] [--procesy 12] [--zachowaj]

Dla kazdego typu plytki (wieczorna, poranna, okragla_wieczorna, okragla_poranna), obu ukladow (R59 i ``*_r54``),
trzech zajetosci i ``--seedy`` seedow generuje sztuczny skan (losowa poza skanera, pole fi 100) i sprawdza:
  a) plytka ZGODNA: ``plate.wyrownaj`` z ukladem skanu - nie moze byc ``NiezgodnyUklad`` (falszywe "nie pasuje"),
  b) plytka NIEZGODNA, sciezka programu: ``plate.wyrownaj`` z drugim ukladem tego typu - musi byc ``NiezgodnyUklad``,
  c) plytka NIEZGODNA, sam straznik gniazd: skan wyrownany wlasnym ukladem (jakby stozki obu ukladow lezaly tak samo)
     i ``plate.zgodnosc_ukladu`` z modelem drugiego ukladu - musi dac ``uklad_zgodny`` = False.
Zajetosc: ``pusta`` = 0 prac; ``czesciowa`` = 3-6 projektow; ``pelna`` = projekty x 3 + atrapy x 3 (ile wejdzie).
Seedy nieparzyste maja trudne scenariusze P3a (praca bokiem, czesciowe pokrycie, poprawka).
Wynik: ``<wyjscie>/straznik_R59.json`` i tabela na stdout - bez nazw plikow projektow (tylko liczby).
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import sys
import time
import warnings
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

TYPY = ("wieczorna", "poranna", "okragla_wieczorna", "okragla_poranna")
ZAJETOSCI = ("pusta", "czesciowa", "pelna")
LIMIT_ZADANIA_S = 1500  # gorna granica czasu jednego skanu (generowanie + 3 sprawdzenia)


def zadanie(arg: tuple) -> dict:
    typ, uklad_skanu, zajetosc, seed, projekty, atrapy, wyjscie, zachowaj = arg
    import trimesh  # noqa: F401 - import w procesie roboczym

    from stanowisko import plate as PL, synth as S, uklad as U, ustawienia as UST

    t0 = time.time()
    ust = UST.wczytaj_ustawienia()
    drugi = typ if uklad_skanu.endswith("_r54") else typ + "_r54"
    uk = U.wczytaj(uklad_skanu, UST.katalog_plytki(ust, uklad_skanu))
    uk2 = U.wczytaj(drugi, UST.katalog_plytki(ust, drugi))
    rng = np.random.default_rng(seed)
    w = 1.0 if S.poranna(uklad_skanu) else 1.22
    trudne = seed % 2 == 1
    if zajetosc == "pusta":
        pula, ile = list(projekty), 0
    elif zajetosc == "czesciowa":
        pula, ile = list(projekty), int(rng.integers(3, 7))
    else:
        pula, ile = (list(projekty) + list(atrapy)) * 3, None
    op = S.Opcje.z_toml(ust, uklad_skanu, wspolczynnik=(w, w), prace_na_plytce=ile, ubytki_na_prace=(0, 1), poza_uklad=True, pole=100.0,
                        p_drgniecia=0.1, p_bokiem=0.35 if trudne else 0.0, p_pokrycie=0.35 if trudne else 0.0, p_poprawki=0.15 if trudne else 0.0)
    numer = uk.numery[seed % len(uk.numery)]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        skan, prawda = S.generuj_plytke(uk, numer, pula, rng, op, seed)
    if zachowaj:
        S.zapisz(skan, prawda, Path(wyjscie) / "skany", f"skan_{uklad_skanu}_n{numer}_{zajetosc}_s{seed}", nadpisz=True)
    numer_podany = numer if uk.shape == "square" else None  # kwadrat: dolki poza polem fi 100
    rek = {"typ": typ, "uklad_skanu": uklad_skanu, "uklad_drugi": drugi, "zajetosc": zajetosc, "seed": seed, "trudne": trudne, "numer": numer,
           "prac": len(prawda.prace), "gniazd": len(uk.sockets), "pominietych": len(prawda.pominiete), "trojkatow": int(len(skan.faces))}
    # a) zgodna
    T = None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            wyr = PL.wyrownaj(skan, uk, numer=numer_podany)
            T = wyr.macierz
            j = wyr.jakosc
            rek["zgodna"] = {"wynik": "ok", "uklad_zgodny": j.get("uklad_zgodny"), "k1": j.get("uklad_gniazdo_nad_pelnym_mm2"), "k2": j.get("uklad_dziura_w_pelnym_mm2"),
                             "strefa_dna": j.get("uklad_strefa_dna_mm2"), "strefa_wierzchu": j.get("uklad_strefa_wierzchu_mm2"),
                             "fragmentow": sum(1 for f in wyr.fragmenty if f.status in ("praca", "podwojny")),
                             "blad_wyrownania_mm": PL.blad_wyrownania(wyr.macierz, prawda.poza_skanu)["max_przesuniecie_mm"]}
        except PL.NiezgodnyUklad as e:
            T = e.macierz
            rek["zgodna"] = {"wynik": "NiezgodnyUklad", "powod": e.powod, "k1": e.jakosc.get("uklad_gniazdo_nad_pelnym_mm2"), "k2": e.jakosc.get("uklad_dziura_w_pelnym_mm2")}
        except PL.BladWyrownania as e:
            rek["zgodna"] = {"wynik": "BladWyrownania", "komunikat": str(e)[:200]}
        # b) niezgodna, sciezka programu
        try:
            wyr2 = PL.wyrownaj(skan, uk2, numer=numer_podany)
            j = wyr2.jakosc
            rek["niezgodna_program"] = {"wynik": "ok", "uklad_zgodny": j.get("uklad_zgodny"), "k1": j.get("uklad_gniazdo_nad_pelnym_mm2"), "k2": j.get("uklad_dziura_w_pelnym_mm2"),
                                        "fragmentow": sum(1 for f in wyr2.fragmenty if f.status in ("praca", "podwojny"))}
        except PL.NiezgodnyUklad as e:
            rek["niezgodna_program"] = {"wynik": "NiezgodnyUklad", "powod": e.powod, "reszta_mm": e.jakosc.get("znaczniki_reszta_mm"),
                                        "k1": e.jakosc.get("uklad_gniazdo_nad_pelnym_mm2"), "k2": e.jakosc.get("uklad_dziura_w_pelnym_mm2"),
                                        "komunikat_ok": str(e).startswith("p\u0142ytka nie pasuje do wybranego uk\u0142adu")}
        except PL.BladWyrownania as e:
            rek["niezgodna_program"] = {"wynik": "BladWyrownania", "komunikat": str(e)[:200]}
        # c) niezgodna, sam straznik gniazd (wyrownanie wlasnym ukladem, model drugiego ukladu)
        if T is not None:
            Ps, _ = PL.probka_powierzchni(skan, 1500000, np.random.default_rng(seed + 1))
            Ps = Ps @ T[:3, :3].T + T[:3, 3]
            z = PL.zgodnosc_ukladu(Ps, uk2, PL.plik_modelu_plytki(uk2, numer))
            rek["niezgodna_gniazda"] = {"uklad_zgodny": z["uklad_zgodny"], "k1": z["uklad_gniazdo_nad_pelnym_mm2"], "k2": z["uklad_dziura_w_pelnym_mm2"],
                                        "strefa_dna": z["uklad_strefa_dna_mm2"], "strefa_wierzchu": z["uklad_strefa_wierzchu_mm2"]}
    rek["czas_s"] = round(time.time() - t0, 1)
    return rek


def tabela(wyniki: list[dict]) -> list[str]:
    linie = ["typ / uklad skanu / zajetosc | skanow | zajete gniazda (min-max) | ZGODNA: falszywe 'nie pasuje' | max K1 | max K2 | "
             "NIEZGODNA program: wykryte (powod) | NIEZGODNA sam straznik gniazd: wykryte | min K1 | min K2"]
    for typ in TYPY:
        for uklad in (typ, typ + "_r54"):
            for zaj in ZAJETOSCI:
                r = [x for x in wyniki if x["uklad_skanu"] == uklad and x["zajetosc"] == zaj]
                if not r:
                    continue
                zg = [x["zgodna"] for x in r]
                falszywe = sum(1 for z in zg if z["wynik"] != "ok" or z.get("uklad_zgodny") is not True)
                npr = [x["niezgodna_program"] for x in r]
                wykryte_p = sum(1 for z in npr if z["wynik"] == "NiezgodnyUklad")
                powody = sorted({z.get("powod", z["wynik"]) for z in npr})
                ng = [x["niezgodna_gniazda"] for x in r if "niezgodna_gniazda" in x]
                wykryte_g = sum(1 for z in ng if z["uklad_zgodny"] is False)
                linie.append(
                    f"{typ} / {uklad} / {zaj} | {len(r)} | {min(x['prac'] for x in r)}-{max(x['prac'] for x in r)} z {r[0]['gniazd']} | {falszywe}/{len(r)} | "
                    f"{max((z.get('k1') or 0) for z in zg):.2f} | {max((z.get('k2') or 0) for z in zg):.2f} | {wykryte_p}/{len(r)} ({', '.join(powody)}) | "
                    f"{wykryte_g}/{len(ng)} | {min((z['k1'] for z in ng), default=float('nan')):.1f} | {min((z['k2'] for z in ng), default=float('nan')):.1f}")
    return linie


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--projekty", type=Path, required=True, help="folder z STL projektow (podfoldery zlecen)")
    ap.add_argument("--wyjscie", type=Path, default=Path("dane/straznik_R59"))
    ap.add_argument("--seedy", type=int, default=5, help="ile seedow na kombinacje (typ, uklad, zajetosc)")
    ap.add_argument("--seed0", type=int, default=7200)
    ap.add_argument("--procesy", type=int, default=12)
    ap.add_argument("--zachowaj", action="store_true", help="zapisz skany (STL + prawda) w <wyjscie>/skany")
    a = ap.parse_args()
    import atrapy_koron
    from stanowisko import plate as PL, synth as S

    projekty = S.pliki_projektow(a.projekty)
    if not projekty:
        raise SystemExit(f"brak plikow STL w {a.projekty}")
    a.wyjscie.mkdir(parents=True, exist_ok=True)
    atrapy = atrapy_koron.generuj(a.wyjscie / "atrapy", 12, 1, mosty=1, nadpisz=True)
    zadania = []
    k = 0
    for typ in TYPY:
        for uklad in (typ, typ + "_r54"):
            for zaj in ZAJETOSCI:
                for s in range(a.seedy):
                    zadania.append((typ, uklad, zaj, a.seed0 + k, projekty, atrapy, str(a.wyjscie), a.zachowaj))
                    k += 1
    print(f"zadan {len(zadania)}, procesow {a.procesy}, projektow {len(projekty)}, atrap {len(atrapy)}; progi niezgodnosci {PL.PROG_GNIAZDO_NAD_PELNYM_MM2} / {PL.PROG_DZIURA_W_PELNYM_MM2} mm2", flush=True)
    t0 = time.time()
    wyniki = []
    with mp.Pool(a.procesy) as pool:
        it = pool.imap_unordered(zadanie, zadania)
        for n in range(len(zadania)):
            rek = it.next(timeout=LIMIT_ZADANIA_S)
            wyniki.append(rek)
            zg, npr, ng = rek["zgodna"], rek["niezgodna_program"], rek.get("niezgodna_gniazda", {})
            print(f"[{n + 1}/{len(zadania)} {time.time() - t0:5.0f} s] {rek['uklad_skanu']:24s} {rek['zajetosc']:9s} s{rek['seed']} prac {rek['prac']:2d}/{rek['gniazd']} "
                  f"zgodna: {zg['wynik']} K1 {zg.get('k1')} K2 {zg.get('k2')} | niezgodna (program): {npr['wynik']} {npr.get('powod', '')} | "
                  f"niezgodna (gniazda): zgodny={ng.get('uklad_zgodny')} K1 {ng.get('k1')} K2 {ng.get('k2')} | {rek['czas_s']} s", flush=True)
    wyniki.sort(key=lambda r: (TYPY.index(r["typ"]), r["uklad_skanu"], ZAJETOSCI.index(r["zajetosc"]), r["seed"]))
    zg = [r["zgodna"] for r in wyniki]
    ng = [r["niezgodna_gniazda"] for r in wyniki if "niezgodna_gniazda" in r]
    zb = {
        "skanow": len(wyniki), "prog_gniazdo_nad_pelnym_mm2": PL.PROG_GNIAZDO_NAD_PELNYM_MM2, "prog_dziura_w_pelnym_mm2": PL.PROG_DZIURA_W_PELNYM_MM2,
        "zgodne_falszywe_nie_pasuje": sum(1 for z in zg if z["wynik"] != "ok" or z.get("uklad_zgodny") is not True),
        "zgodne_max_k1": max((z.get("k1") or 0) for z in zg), "zgodne_max_k2": max((z.get("k2") or 0) for z in zg),
        "niezgodne_program_wykryte": sum(1 for r in wyniki if r["niezgodna_program"]["wynik"] == "NiezgodnyUklad"),
        "niezgodne_program_komunikat_ok": sum(1 for r in wyniki if r["niezgodna_program"].get("komunikat_ok")),
        "niezgodne_gniazda_skanow": len(ng), "niezgodne_gniazda_wykryte": sum(1 for z in ng if z["uklad_zgodny"] is False),
        "niezgodne_gniazda_min_k1": min((z["k1"] for z in ng), default=None), "niezgodne_gniazda_min_k2": min((z["k2"] for z in ng), default=None),
        "niezgodne_gniazda_min_wiekszej_miary": min((max(z["k1"], z["k2"]) for z in ng), default=None),
        "czas_s": round(time.time() - t0, 1),
    }
    (a.wyjscie / "straznik_R59.json").write_text(json.dumps({"zbiorczo": zb, "skany": wyniki}, ensure_ascii=True, indent=1), encoding="utf-8")
    print("\n".join(tabela(wyniki)))
    print("ZBIORCZO:", json.dumps(zb, ensure_ascii=True))
    print(a.wyjscie / "straznik_R59.json")


if __name__ == "__main__":
    main()
