# Kontrola pomocnika zestaw_t11.py i tabela skan po skanie T11 (tylko odczyt; skrypt zbierajacego wynik, nie narzedzie planu).
# Zrodla INNE niz w zestaw_t11.py: prawda z pliku t11_prawda.txt (sha256sum z Git Bash + pole plytka z .json obok skanu),
# baza przez pliki TSV z narzedzia planu sql_odczyt.py (nie przez wlasne polaczenie z baza).
# Uzycie: python.exe -I sprawdz_t11.py <auto_uklad.json> <t11_prawda.txt> <t11_symulator.json> <t11_skany_sha16.tsv>
#             <t11_zielone.tsv> <wyjscie t11_tabela.tsv>
# Wypisuje tylko liczby, sha16 i nazwy skanow syntetycznych.
import json
import sys


def tsv(sciezka):
    with open(sciezka, encoding="utf-8") as f:
        wiersze = [w.rstrip("\r\n") for w in f if w.strip() and not w.startswith("-- wierszy")]
    nagl = wiersze[0].split("\t")
    return [dict(zip(nagl, w.split("\t"))) for w in wiersze[1:]]


def main():
    p_auto, p_prawda, p_dz, p_skany, p_ziel, p_tab = sys.argv[1:7]

    # --- czesc A: z rekordow skanow, nie z sekcji podsumowanie
    with open(p_auto, encoding="utf-8") as f:
        auto = json.load(f)
    for przebieg in ("bez_numeru", "z_numerem"):
        rek = [r["przebiegi"][przebieg] | {"prawda": r["prawda"]} for r in auto["skany"] if przebieg in r["przebiegi"]]
        ok = sum(1 for r in rek if r["wybrany"] == r["prawda"])
        zle_pewny = sum(1 for r in rek if r["wybrany"] != r["prawda"] and r.get("pewny"))
        pods = auto["podsumowanie"][przebieg]
        print("A %s z rekordow: ok %d z %d, zle_ale_pewny %d | podsumowanie narzedzia: ok %d z %d, zle_ale_pewny %d | zgodne: %s"
              % (przebieg, ok, len(rek), zle_pewny, pods["ok"], pods["skanow"], pods["zle_ale_pewny"],
                 "TAK" if (ok, len(rek), zle_pewny) == (pods["ok"], pods["skanow"], pods["zle_ale_pewny"]) else "NIE"))

    # --- czesc B
    prawda = {}
    with open(p_prawda, encoding="utf-8") as f:
        for w in f:
            pola = w.rstrip("\r\n").split("\t")
            if len(pola) == 4:
                prawda[pola[0]] = {"uklad": pola[1], "zestaw": pola[2], "skan": pola[3]}
    print("prawda: %d skanow, roznych sha16 %d" % (len(prawda), len(prawda)))
    with open(p_dz, encoding="utf-8") as f:
        dz = [z for z in json.load(f)["zapisy"] if z.get("rodzaj") == "dobry"]
    skany = tsv(p_skany)
    ziel = {w["id"]: w for w in tsv(p_ziel)}
    po_sha = {}
    for w in skany:
        po_sha.setdefault(w["sha16"], []).append(w)
    print("dziennik: dobrych zapisow %d, roznych sha16 %d, spoza prawdy %d" % (len(dz), len({z["sha16"] for z in dz}), sum(1 for z in dz if z["sha16"] not in prawda)))
    print("skany (TSV): wierszy %d, roznych sha16 %d, spoza dziennika %d, sha16 z wiecej niz 1 wierszem %d"
          % (len(skany), len(po_sha), sum(1 for s in po_sha if s not in {z["sha16"] for z in dz}), sum(1 for v in po_sha.values() if len(v) > 1)))
    m = len(dz)
    n_w = n_rozp = n_auto = n_niepusty = n_zly = ziel_zly = n_inny = 0
    statusy, per = {}, {}
    tab = ["nr\tsha16\tzestaw\tskan\tuklad_prawda\tuklad_baza\trozpoznany\tstatus\tuklad_zrodlo\tuklad_zgodny\tzielonych\tnumer_plytki\tczas_s"]
    for z in dz:
        pr = prawda.get(z["sha16"], {"uklad": "?", "zestaw": "?", "skan": "?"})
        ww = po_sha.get(z["sha16"])
        if not ww:
            tab.append("%d\t%s\t%s\t%s\t%s\tBRAK WIERSZA\tNIE ZMIERZONO\t\t\t\t\t\t" % (z["nr"], z["sha16"], pr["zestaw"], pr["skan"], pr["uklad"]))
            continue
        w = ww[-1]
        n_w += 1
        zl = int(ziel[w["id"]]["zielonych"] or 0) if w["id"] in ziel else -1
        zly = w["status"] == "niezgodny_uklad" or w["uklad_zgodny"] == "0"
        rozp = w["uklad"] == pr["uklad"] and not zly
        n_rozp += rozp
        n_auto += w["uklad_zrodlo"] == "auto"
        n_niepusty += bool(w["uklad"])
        n_inny += bool(w["uklad"]) and w["uklad"] != pr["uklad"]
        if zly or (w["uklad"] != pr["uklad"]):
            n_zly += 1
            ziel_zly += max(zl, 0)
        klucz = (w["status"], w["uklad"], w["uklad_zrodlo"], w["uklad_zgodny"])
        statusy[klucz] = statusy.get(klucz, 0) + 1
        k2 = (pr["zestaw"], pr["uklad"])
        a, b = per.get(k2, (0, 0))
        per[k2] = (a + rozp, b + 1)
        tab.append("\t".join(str(x) for x in (z["nr"], z["sha16"], pr["zestaw"], pr["skan"], pr["uklad"], w["uklad"], "TAK" if rozp else "NIE",
                                              w["status"], w["uklad_zrodlo"], w["uklad_zgodny"], zl, w.get("numer_plytki", ""), w.get("czas_s", ""))))
    with open(p_tab, "w", encoding="ascii", newline="\n") as f:
        f.write("\n".join(tab) + "\n")
    print("(n) skany z dziennika z wierszem w skany: %d z %d (bez wiersza = NIE ZMIERZONO: %d)" % (n_w, m, m - n_w))
    print("(a) uklad rozpoznany (skany.uklad = plytka z prawdy, status inny niz niezgodny_uklad, uklad_zgodny inny niz 0): %d z %d" % (n_rozp, m))
    print("    uklad_zrodlo = auto: %d z %d" % (n_auto, m))
    print("    uklad zapisany, ale inny niz w prawdzie: %d" % n_inny)
    print("(b) skany ze zlym ukladem (niezgodny_uklad / uklad_zgodny = 0 / uklad inny niz prawda): %d; zielonych na nich: %d" % (n_zly, ziel_zly))
    print("(c) skany.uklad niepusty: %d z %d" % (n_niepusty, m))
    for k in sorted(statusy):
        print("    grupa status / uklad / zrodlo / zgodny: %s / %s / %s / %s: %d" % (k + (statusy[k],)))
    for k in sorted(per):
        print("    %s %s: rozpoznane %d z %d" % (k[0], k[1], per[k][0], per[k][1]))
    czasy = sorted(float(w["czas_s"]) for w in skany if w.get("czas_s"))
    if czasy:
        print("czas_s (kolumna skany.czas_s; nie jest kryterium): min %.1f, mediana %.1f, max %.1f, pierwszy skan %s"
              % (czasy[0], czasy[len(czasy) // 2], czasy[-1], skany[0].get("czas_s")))
    zr = sum(max(int(w["zielonych"] or 0), 0) for w in ziel.values())
    zt = sum(int(ziel[w["id"]]["zielonych"] or 0) for w in skany if w["status"] == "plytka_nie_z_trybu" and w["id"] in ziel)
    print("informacyjnie: zielonych razem %d; na skanach plytka_nie_z_trybu (%d skanow): %d"
          % (zr, sum(1 for w in skany if w["status"] == "plytka_nie_z_trybu"), zt))


if __name__ == "__main__":
    main()
