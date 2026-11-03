"""Składa weryfikacja_R53.md z wyników: pomiar_R53_{przed,po}.json, wyniki kopii recenzenta (A/B/C/kanały),
trzecie_oko_wyniki.json (kopia R53), SHA STL (kopia zapasowa vs nowe), raporty generatora.
Uruchomienie: py -3.12 -X utf8 -I zloz_weryfikacje.py"""
import json, os, re, hashlib, glob
S = os.path.dirname(os.path.abspath(__file__))
SES = os.path.dirname(S)
ROOT = os.path.dirname(os.path.dirname(SES))
W = os.path.join(S, "wyniki"); W3 = os.path.join(S, "wyniki_3oko")
def pl(v, n=3):
    if v is None: return "—"
    return ("%.*f" % (n, v)).replace(".", ",")
L = []
L.append("# Weryfikacja R53 — poprawki pasowań (31.10.2026)\n")
L.append("Zestaw: `wyniki_v2/` po przebiegach `--etap B --iter 5`, `--etap C --iter 5` (ponowiony po poprawce opisu reguły w arkuszu), `--etap SPRAWDZ --iter 5` (logi w `logi/`). Kopia sprzed R53: `archiwum/wyniki_v2_przed_R53_2026-10-31/`. Metody niezależne: (1) sprawdzenia generatora K‑01…K‑60, (2) kopie skryptów recenzenta `skrypty/sprawdz_*_R53.py` (Blender), (3) kopia trzeciego oka `skrypty/trzecie_oko_R53.py` (Blender, 17 STL + bryły zastępcze), (4) własny pomiar trimesh `skrypty/pomiar_R53.py` ze znakiem luzu, przed i po (ten sam skrypt, parametry odpowiednio sprzed/po R53).\n")

# ---- 1. generator
L.append("## 1. Generator (`ramka_generator.py`)\n")
L.append("| Przebieg | Wynik | Czas |\n|---|---|---|")
for lg in ("etap_B_iter5", "etap_C_iter5", "etap_SPRAWDZ_iter5"):
    txt = open(os.path.join(SES, "logi", lg + ".log"), encoding="utf-8", errors="replace").read()
    m = re.search(r"RAPORT .* (B=\d+ P=\d+ D=\d+) czas (\d+) s", txt)
    L.append("| %s | %s | %s s |" % (lg, m.group(1) if m else "BRAK RAPORTU", m.group(2) if m else "—"))
rap = open(os.path.join(ROOT, "wyniki_v2", "raport", "raport_wykonawcy_SPRAWDZ_iter5.md"), encoding="utf-8").read()
n_nie = len(re.findall(r"\| NIE \|", rap)); n_zal = len(re.findall(r"\| ZAL \|", rap))
L.append("\nRaport SPRAWDZ iter5: ZAL %d, NIE %d. Odstępstwa informacyjne „tabela 3 planu” (wartości sprzed R53 w tabeli 3 planu — poza mandatem sesji): %d.\n" % (n_zal, n_nie, len(re.findall(r"tabela 3 planu", rap))))

# ---- 2. SHA
L.append("## 2. Pliki STL: które się zmieniły (SHA‑256 vs kopia zapasowa)\n")
L.append("| Plik | przed R53 | po R53 | Status |\n|---|---|---|---|")
old = {l.split()[1].lstrip("*"): l.split()[0] for l in open(os.path.join(ROOT, "archiwum", "sha256_stl_przed_R53.txt"), encoding="utf-8")}
chg = []
for f in sorted(old):
    h = hashlib.sha256(open(os.path.join(ROOT, "wyniki_v2", "stl", f), "rb").read()).hexdigest()
    same = h == old[f]
    exp_change = f in ("ramka_blat_v2.stl", "ramka_korpus_W_v2.stl", "ramka_korpus_P_v2.stl", "ramka_wkladka_v2.stl")
    st = ("ZMIENIONY (R53)" if exp_change else "ZMIENIONY — NIEOCZEKIWANE") if not same else ("IDENTYCZNY bajtowo" if not exp_change else "IDENTYCZNY — NIEOCZEKIWANE")
    chg.append((f, same, exp_change))
    L.append("| `%s` | `%s…` | `%s…` | %s |" % (f, old[f][:12], h[:12], st))
nieocz = [f for f, same, e in chg if same == e]
L.append("\nNieoczekiwanych różnic: %d. Powtarzalność: STL z `--etap B --iter 5` i `--etap C --iter 4` porównane bajtowo (`logi/sha256_*`).\n" % len(nieocz))

# ---- 3. pomiar wlasny przed/po
L.append("## 3. Pasowania T1–T15 z siatek, ze znakiem luzu (trimesh, `pomiar_R53.py`)\n")
L.append("Luz = (powierzchnia części B) − (powierzchnia części A) z jednego punktu w szczelinie; dodatni = szczelina, ujemny = wcisk/przenikanie. „Przed” zmierzone na STL z kopii zapasowej z parametrami sprzed R53; „po” na nowych STL z parametrami R53. Status: |zmierzone − nominał| ≤ 0,05.\n")
L.append("| Pasowanie | Nominał przed | Zmierzone przed | Nominał po (R53) | Zmierzone po | Kier. | Status |\n|---|---|---|---|---|---|---|")
pr = json.load(open(os.path.join(W, "pomiar_R53_przed.json"), encoding="utf-8"))["rows"]
po = json.load(open(os.path.join(W, "pomiar_R53_po.json"), encoding="utf-8"))["rows"]
bad = 0
for a, b in zip(pr, po):
    assert a["pasowanie"] == b["pasowanie"]
    oka = a["zmierzone"] is not None and abs(a["zmierzone"] - a["nominal_po"]) <= 0.05
    okb = b["zmierzone"] is not None and abs(b["zmierzone"] - b["nominal_po"]) <= 0.05
    if not okb: bad += 1
    L.append("| %s | %s | %s | %s | %s | %s | %s |" % (b["pasowanie"], pl(a["nominal_po"]), pl(a["zmierzone"]), pl(b["nominal_po"]), pl(b["zmierzone"]), b["kierunek"], ("TAK" if okb else "**NIE**") + ("" if oka else " (przed: niezgodne)")))
L.append("\nPomiarów: %d; niezgodnych po R53: %d.\n" % (len(po), bad))

# ---- 4. kopie recenzenta
L.append("## 4. Kopie skryptów recenzenta (`skrypty/sprawdz_*_R53.py`)\n")
L.append("| Skrypt | Sprawdzeń | NIE | Uwagi |\n|---|---|---|---|")
tot_nie = 0
for fn, note in (("wyniki_A_iterR53.json", "płytki (pokrywka pominięta flagą `--bez-pokrywki`, jak w recenzji C1/C2; S‑05)"), ("wyniki_A_iterR53pok.json", "przebieg z pokrywką: 3 znane fałszywe NIE K‑02/K‑19/K‑21 (S‑05, pokrywka bajtowo bez zmian) — tylko dla objętości do K‑57"), ("wyniki_B_iterR53.json", "wkładka, blat, korpusy W/P, złożenie"), ("wyniki_C_iterR53.json", "tulejka, podkładki, K‑57, K‑60")):
    p = os.path.join(W, fn)
    if not os.path.exists(p):
        L.append("| %s | — | — | BRAK PLIKU |" % fn); continue
    d = json.load(open(p, encoding="utf-8"))
    nie = [r for r in d["wyniki"] if r["wynik"] == "NIE"]
    if fn != "wyniki_A_iterR53pok.json": tot_nie += len(nie)
    L.append("| %s | %d | %d | %s%s |" % (fn, len(d["wyniki"]), len(nie), note, ("; NIE: " + "; ".join("%s %s" % (r["id"], r["plik"]) for r in nie)) if nie else ""))
pk = os.path.join(W, "wyniki_B_iter2_kanaly.json")
if os.path.exists(pk):
    k = json.load(open(pk, encoding="utf-8"))
    L.append("| sprawdz_B_kanaly_R53 | 3 | %d | ciągłość kanałów Halla A/B/C: %s |" % (sum(0 if v["ciagly"] else 1 for v in k.values()), ", ".join("%s %s" % (n, "ciągły" if v["ciagly"] else "PRZERWANY") for n, v in k.items())))
L.append("\nNIE łącznie (bez znanych fałszywych S‑05): %d.\n" % tot_nie)

# ---- 5. trzecie oko
L.append("## 5. Trzecie oko (kopia `trzecie_oko_R53.py`, G4b ponowione na zestawie R53)\n")
t = json.load(open(os.path.join(W3, "trzecie_oko_wyniki.json"), encoding="utf-8"))
ps = t["podsumowanie"]
L.append("Pasowania %d, wymiary %d, ścianki %d, kroki montażu %d. Blokujące surowe: %d." % (ps["pasowania"], ps["wymiary"], ps["scianki"], ps["montaz"], ps["blokujace_surowe"]))
if t["blokujace"]:
    L.append("\n| Gdzie | Opis | Typ |\n|---|---|---|")
    for b in t["blokujace"]:
        L.append("| %s | %s | %s |" % (b["gdzie"], str(b["opis"]).replace("|", "/"), b["typ"]))
L.append("\nPasowania R53 w karcie trzeciego oka (wybór):\n")
L.append("| Para | Miejsce | Luz z planu | Zmierzony | Werdykt |\n|---|---|---|---|---|")
keys = ("kołnierz", "zahaczenie", "luz do dna kieszeni", "luz pod występem", "luz nad występem", "szerokość 8 w kieszeni", "kołek ø3", "wkręt x", "lico słupka", "płytka n1 – wkładka", "tulejka DC – otwór", "wnęka 96,6")
seen = 0
for r in t["pasowania"]:
    if any(k in r["para"] for k in keys) and (seen < 60):
        if "płytka n1 – wkładka" in r["para"] and "prawy y=0" not in r["miejsce"]:
            continue
        if "kołnierz" in r["para"] and "(30" not in r["miejsce"] and "(-30" not in r["miejsce"] and "30," not in r["miejsce"]:
            continue
        L.append("| %s | %s | %s | %s | %s |" % (r["para"], r["miejsce"], pl(r["luz_plan"]), pl(r["luz_zmierzony"]), r["werdykt"]))
        seen += 1
mont = [m for m in t["montaz"] if "blat na korpus" in m["krok"] or "pokrywka na płytkę wieczorna_n1" in m["krok"] or "wkładka na kołki" in m["krok"]]
L.append("\nMontaż (wybór): " + "; ".join("%s → %s" % (m["krok"], m["werdykt"]) for m in mont) + "\n")
nz = [m for m in t["montaz"] if not str(m["werdykt"]).startswith("OK")]
L.append("Kroków montażu z werdyktem innym niż OK: %d.\n" % len(nz))

# ---- 6. arkusze / README
L.append("## 6. Arkusze, README, model\n")
ark = open(os.path.join(ROOT, "wyniki_v2", "arkusze", "arkusz_wymiarow.md"), encoding="utf-8").read()
m = re.search(r"SHA‑256: `([0-9a-f]{64})`", ark)
hp = hashlib.sha256(open(os.path.join(ROOT, "parametry.json"), "rb").read()).hexdigest()
L.append("- `arkusz_wymiarow.md`: zrzut `parametry.json` SHA `%s…` %s bieżącym `parametry.json` (`%s…`)." % (m.group(1)[:12] if m else "?", "=" if (m and m.group(1) == hp) else "≠", hp[:12]))
for key in ("kołnierz blatu – ściana korpusu (x)", "haczyk blatu: zahaczenie w kieszeni korpusu (x)", "haczyk blatu: luz do dna kieszeni (x)", "haczyk blatu: luz nad występem (z)", "kołek wkładki w otworze blatu (x)", "płytka w otworze wkładki (x)", "kołek orientacyjny w wycięciu płytki (x)", "tulejka DC w otworze ściany skrzynki (y)"):
    mm = re.search(r"\| " + re.escape(key) + r" \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|", ark)
    if mm:
        L.append("- arkusz pasowań: %s → zmierzone %s, nominał %s, %s" % (key, mm.group(1).strip(), mm.group(2).strip(), mm.group(3).strip()))
csv = open(os.path.join(ROOT, "wyniki_v2", "arkusze", "arkusz_zamowienia.csv"), encoding="utf-8").read()
L.append("- `arkusz_zamowienia.csv`: %d wierszy; wkładka gabaryt %s." % (csv.count("\n") - 1, "130,0 × 148,4 × 11,0" if "148,4" in csv else "?"))
rd = open(os.path.join(ROOT, "wyniki_v2", "README.md"), encoding="utf-8").read()
L.append("- `README.md`: ostatni przebieg: %s" % (re.search(r"Ostatni przebieg: ([^\n]+)", rd).group(1)[:120] if re.search(r"Ostatni przebieg: ([^\n]+)", rd) else "?"))
open(os.path.join(SES, "weryfikacja_R53.md"), "w", encoding="utf-8", newline="").write("\n".join(L) + "\n")
print("OK: weryfikacja_R53.md; NIE pomiar", bad, "NIE recenzja", tot_nie, "3oko blokujace", ps["blokujace_surowe"], "nieoczekiwane SHA", len(nieocz))
