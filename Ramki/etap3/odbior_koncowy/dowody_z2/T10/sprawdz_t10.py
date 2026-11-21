# Kontrola pomocnika zestaw_t10.py: 3 liczby kryterium T10 policzone z rekordow skanow (skany[].gniazda[]),
# bez sekcji zbiorczo; do tego porownanie gniazdo po gniezdzie z surowym wynikiem nocy (tylko odczyt obu plikow).
# Uzycie: python.exe -I sprawdz_t10.py <wynik tego przebiegu .json> <wynik nocy .json>
# Wypisuje tylko liczby, nazwy skanow syntetycznych, numery gniazd i sha16 projektow (bez nazw plikow projektow).
import json
import sys


def wczytaj(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def licz(d):
    skany = d["skany"]
    wyr = sum(1 for r in skany if r["metryki"]["wyrownanie"]["max_przesuniecie_mm"] < 0.05)
    mx = max(r["metryki"]["wyrownanie"]["max_przesuniecie_mm"] for r in skany)
    dobrze = top_bl = cale = cale_cz = 0
    for r in skany:
        for g in r["gniazda"]:
            ins = g.get("inspekcja")
            if g["scenariusz"] == "dobrze":
                dobrze += 1
                if g.get("projekt") != g.get("projekt_prawda"):
                    top_bl += 1
            if (g.get("ubytkow_prawda") == 0 and g["scenariusz"] != "drgniecie"
                    and g.get("projekt") == g.get("projekt_prawda") and ins is not None):
                cale += 1
                if ins.get("status") == "ubytek" or g.get("status_gniazda") == "czerwony":
                    cale_cz += 1
    return {"skanow": len(skany), "wyrownanie_ok": wyr, "max_mm": round(mx, 4), "dobrze_prac": dobrze,
            "dobrze_top1_bledny": top_bl, "prac_calych": cale, "prace_cale_z_czerwonym": cale_cz}


def klucze(d):
    w = {}
    for r in d["skany"]:
        nr = {}
        for g in r["gniazda"]:
            i = nr.get(g["gniazdo"], 0)
            nr[g["gniazdo"]] = i + 1
            ins = g.get("inspekcja") or {}
            w[(r["zestaw"], r["skan"], g["gniazdo"], i)] = (
                g.get("status"), g.get("status_gniazda"), g.get("projekt"), ins.get("status"),
                g.get("scenariusz"), g.get("projekt_prawda"), g.get("ubytkow_prawda"))
    return w


def main():
    teraz, noc = wczytaj(sys.argv[1]), wczytaj(sys.argv[2])
    a, b = licz(teraz), licz(noc)
    print("TEN PRZEBIEG z rekordow: %s" % json.dumps(a, sort_keys=True))
    print("NOC          z rekordow: %s" % json.dumps(b, sort_keys=True))
    z = teraz["zbiorczo"]
    zb = {"skanow": z["plate_match"]["skanow"], "wyrownanie_ok": z["plate_match"]["wyrownanie_ok"],
          "dobrze_prac": z["top1_per_scenariusz"]["dobrze"]["prac"],
          "dobrze_top1_bledny": z["top1_per_scenariusz"]["dobrze"]["top1_bledny"],
          "prac_calych": z["razem"]["prac_calych"], "prace_cale_z_czerwonym": z["razem"]["prace_cale_z_czerwonym"]}
    print("TEN PRZEBIEG zbiorczo  : %s" % json.dumps(zb, sort_keys=True))
    print("rekordy = zbiorczo (6 pol): %s" % ("TAK" if all(a[k] == zb[k] for k in zb) else "NIE"))
    print("zbiorczo.drgniecie: teraz %s, noc %s" % (json.dumps(z["drgniecie"]), json.dumps(noc["zbiorczo"]["drgniecie"])))
    ka, kb = klucze(teraz), klucze(noc)
    print("wpisow gniazd: teraz %d, noc %d; tylko teraz %d, tylko w nocy %d"
          % (len(ka), len(kb), len(set(ka) - set(kb)), len(set(kb) - set(ka))))
    pola = ("status_match", "status_gniazda", "projekt", "status_inspekcji")
    rozne = 0
    for k in sorted(set(ka) & set(kb)):
        x, y = ka[k], kb[k]
        if x[:4] != y[:4]:
            rozne += 1
            zm = "; ".join("%s: noc %s -> teraz %s" % (pola[i], y[i], x[i]) for i in range(4) if x[i] != y[i])
            print("ROZNICA %s / %s / gniazdo %d wpis %d / scenariusz %s / ubytkow w prawdzie %s / sha16 %s: %s"
                  % (k[0].replace("syntetyczne_R59_", ""), k[1], k[2], k[3], x[4], x[6], x[5], zm))
    for k in sorted(set(ka) ^ set(kb)):
        print("WPIS TYLKO W JEDNYM: %s / %s / gniazdo %d wpis %d (%s)" % (k[0].replace("syntetyczne_R59_", ""), k[1], k[2], k[3], "teraz" if k in ka else "noc"))
    print("wpisow gniazd rozniacych sie od nocy (4 pola: %s): %d z %d" % (", ".join(pola), rozne, len(set(ka) & set(kb))))
    print("statusy gniazd: teraz %s, noc %s" % (json.dumps(z["plate_match"]["statusy_gniazd"], sort_keys=True),
                                               json.dumps(noc["zbiorczo"]["plate_match"]["statusy_gniazd"], sort_keys=True)))


if __name__ == "__main__":
    main()
