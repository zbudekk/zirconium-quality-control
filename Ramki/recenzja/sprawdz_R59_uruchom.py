# -*- coding: utf-8 -*-
"""
Recenzent R59 - uruchomienie pomiarow na PC (python): 12 procesow Blendera rownolegle (po jednym na plik plytki),
kazdy z limitem czasu i wlasnym logiem w wyniki/log_<plik>.txt; potem zestawienie z plikow wynik_<plik>.json.
Uruchomienie: python sprawdz_R59_uruchom.py [--krok 0.05] [--limit 1500] [--tylko nazwa1,nazwa2]
Wynik: wyniki/zestawienie_R59.json + tekst na stdout (do log_R59_iter1.txt).
"""
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

TU = os.path.dirname(os.path.abspath(__file__))
BAZA = os.path.join(os.path.dirname(TU), "Ramki")
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
STL = os.path.join(BAZA, "wyniki_v2", "stl")
STARE = os.path.join(BAZA, "archiwum", "wyniki_v2_przed_R59_2026-11-14", "stl")
PAR = os.path.join(TU, "ref", "Ramki", "parametry.json")
PAR_ST = os.path.join(TU, "ref", "Ramki", "archiwum", "parametry_przed_R59_2026-11-14.json")
WYN = os.path.join(TU, "wyniki")
PLYTKI = ["ramka_plytka_wieczorna_v2", "ramka_plytka_wieczorna_n1_v2", "ramka_plytka_wieczorna_n2_v2",
          "ramka_plytka_wieczorna_n3_v2", "ramka_plytka_poranna_v2", "ramka_plytka_poranna_n4_v2",
          "ramka_plytka_poranna_n5_v2", "ramka_plytka_poranna_n6_v2", "ramka_plytka_okragla_wieczorna_v2",
          "ramka_plytka_okragla_wieczorna_n8_v2", "ramka_plytka_okragla_poranna_v2", "ramka_plytka_okragla_poranna_n9_v2"]


def arg(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


KROK = arg("--krok", "0.05")
LIMIT = int(arg("--limit", "1500"))
TYLKO = arg("--tylko", "")


def jeden(plik):
    t0 = time.time()
    logp = os.path.join(WYN, "log_%s.txt" % plik)
    wynp = os.path.join(WYN, "wynik_%s.json" % plik)
    if os.path.isfile(wynp):
        os.remove(wynp)
    cmd = [BLENDER, "-b", "-P", os.path.join(TU, "sprawdz_R59.py"), "--", "--plik", plik, "--stl", STL, "--stare", STARE,
           "--par", PAR, "--par-stare", PAR_ST, "--wyn", WYN, "--krok", KROK]
    with open(logp, "w", encoding="utf-8") as f:
        try:
            rc = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, timeout=LIMIT).returncode
        except subprocess.TimeoutExpired:
            rc = "LIMIT CZASU %d s" % LIMIT
    return plik, rc, round(time.time() - t0, 1)


def main():
    os.makedirs(WYN, exist_ok=True)
    pliki = [p for p in PLYTKI if not TYLKO or p in TYLKO.split(",")]
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=len(pliki)) as ex:
        kody = list(ex.map(jeden, pliki))
    print("PRZEBIEG: %d procesow Blendera rownolegle, krok mapy %s mm, limit %d s, czas calkowity %.1f s" % (
        len(pliki), KROK, LIMIT, time.time() - t0))
    zest = {"pliki": {}, "sumy": {}}
    sumy = {"sondy_punktowe": 0, "promienie_pomiarowe": 0, "promienie_mapy": 0, "sprawdzen": 0, "NIE": 0, "ZAL": 0}
    brak = 0
    for plik, rc, czas in kody:
        wynp = os.path.join(WYN, "wynik_%s.json" % plik)
        if rc != 0 or not os.path.isfile(wynp):
            print("== %s: BLAD PRZEBIEGU (kod %s, %.1f s) - patrz log_%s.txt" % (plik, rc, czas, plik))
            brak += 1
            continue
        with open(wynp, encoding="utf-8") as f:
            w = json.load(f)
        nie = [r for r in w["wyniki"] if r["wynik"] == "NIE"]
        print("== %s: kod %s, %.1f s, objetosc %.4f cm3, trojkatow %d, sprawdzen %d, NIE %d, sondy punktowe %d, promienie pomiarowe %d,"
              " promienie map %d" % (plik, rc, czas, w["objetosc_cm3"], w["trojkatow"], len(w["wyniki"]), len(nie),
                                     w["liczniki"]["sondy_punktowe"], w["liczniki"]["promienie_pomiarowe"],
                                     w["liczniki"]["promienie_mapy"]))
        for r in w["wyniki"]:
            print("   [%s] %-34s %s | oczek: %s%s" % (r["wynik"], r["id"], r["wartosc"], r["oczekiwane"],
                                                      (" | " + r["uwaga"]) if r["uwaga"] else ""))
        for k in ("sondy_punktowe", "promienie_pomiarowe", "promienie_mapy"):
            sumy[k] += w["liczniki"][k]
        sumy["sprawdzen"] += len(w["wyniki"])
        sumy["NIE"] += len(nie)
        sumy["ZAL"] += len(w["wyniki"]) - len(nie)
        zest["pliki"][plik] = {"objetosc_cm3": w["objetosc_cm3"], "nie": [r["id"] for r in nie], "czas_s": czas,
                               "liczniki": w["liczniki"]}
    zest["sumy"] = sumy
    zest["bledy_przebiegu"] = brak
    with open(os.path.join(WYN, "zestawienie_R59.json"), "w", encoding="utf-8") as f:
        json.dump(zest, f, indent=1)
    print("RAZEM: plikow %d, bledow przebiegu %d, sprawdzen %d (ZAL %d, NIE %d); sondy punktowe (3 kierunki) %d, promienie pomiarowe %d,"
          " promienie map %d" % (len(pliki), brak, sumy["sprawdzen"], sumy["ZAL"], sumy["NIE"], sumy["sondy_punktowe"],
                                 sumy["promienie_pomiarowe"], sumy["promienie_mapy"]))
    return 0 if (brak == 0 and sumy["NIE"] == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
