# Zestawienie liczb kryterium T10 z surowego wyniku metryki_P3a.py (tylko odczyt; pomocnik wykonawcy testow, nie narzedzie planu).
# Uzycie: python.exe -I zestaw_t10.py <t10_surowe_metryki.json> <t10_surowe.log>
import json
import sys


def main():
    plik_json, plik_log = sys.argv[1], sys.argv[2]
    with open(plik_json, encoding="utf-8") as f:
        d = json.load(f)
    z = d["zbiorczo"]
    pm = z["plate_match"]
    print("skanow w wyniku (skany[]): %d" % len(d["skany"]))
    print("uklad_niezgodny: %r" % (d.get("uklad_niezgodny"),))
    print("WYROWNANIE: %d z %d (zbiorczo.plate_match.wyrownanie_ok / .skanow), max %.4f mm"
          % (pm["wyrownanie_ok"], pm["skanow"], pm["wyrownanie_max_mm"]))
    t = z["top1_per_scenariusz"]
    for nazwa in sorted(t):
        w = t[nazwa]
        print("TOP-1 scenariusz %-10s: %d z %d (top1_bledny %d)"
              % (nazwa, w["prac"] - w["top1_bledny"], w["prac"], w["top1_bledny"]))
    r = z["razem"]
    print("FALSZYWE CZERWONE na pracach calych: %d z %d (zbiorczo.razem.prace_cale_z_czerwonym / .prac_calych)"
          % (r["prace_cale_z_czerwonym"], r["prac_calych"]))
    print("czas calosci [s]: %r" % (pm.get("czas_calosci_s"),))
    wiersze = 0
    with open(plik_log, encoding="utf-8", errors="replace") as f:
        for linia in f:
            wiersze += 1
            if linia.startswith("PRACE CA"):
                print("wiersz logu: " + linia.strip().encode("ascii", "replace").decode("ascii")[:200])
    print("wierszy logu: %d" % wiersze)
    print("punkt odniesienia (noc, paczka 0.3.1): 40 z 40 / 276 z 276 (scenariusz dobrze) / 0 z 127")


if __name__ == "__main__":
    main()
