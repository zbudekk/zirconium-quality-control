"""T10 - niezalezne liczenie kryterium z plikow wyniku (wykonawca testu T10, odbior koncowy etapu 3).

Uzycie: PY -I t10_licz.py --wynik-json <ROB>\\t10\\t10_surowe_metryki.json --log <ROB>\\t10_surowe.log
            --skany <katalog P2> <katalog P3a> --md <ROB>\\t10_wynik.md --json <ROB>\\t10_licz.json

Nie przepisuje podsumowania narzedzia: liczy z rekordow skanow (``skany[]``) i z plikow prawdy zestawow, a sekcje
``zbiorczo`` i wiersz logu "PRACE CA..." tylko porownuje. Wypisuje wylacznie liczby, zestaw, plytke (uklad / numer /
seed), numer gniazda i ``sha16`` projektu (identyfikator z pliku prawdy) - bez nazw plikow. Wyjscie ASCII + LF.

Definicje (zrodlo: ``stanowisko/porownaj.py`` ``metryki`` / ``metryki_inspekcji`` / ``scenariusz``; R59 pkt 6.2):
  wyrownanie OK       = skan ma rekord (nie "uklad niezgodny") i max_przesuniecie_mm < 0,05;
  scenariusz "dobrze" = praca z prawdy: bez drgniecia, ulozenie "dobrze", pokrycie >= 1,0;
  top-1 dobrze        = pierwszy kandydat gniazda == projekt z prawdy (brak gniazda w wyniku / brak kandydata = bledny);
  praca cala          = praca z prawdy bez ubytkow, bez drgniecia, top-1 trafny, inspekcja policzona;
  falszywe czerwone   = praca cala ze statusem inspekcji "ubytek" (gniazdo czerwone).
Gniazdo z kilkoma fragmentami (wynik ma wtedy kilka wpisow tego samego gniazda; narzedzie liczy kazdy wpis osobno):
  licze dwojako - "wpisy" (jak narzedzie, do porownania z ``zbiorczo``) i "prace z prawdy" (kazda praca raz; top-1
  trafny tylko gdy WSZYSTKIE wpisy gniazda maja wlasciwy projekt; praca cala, gdy choc jeden wpis spelnia definicje;
  czerwona, gdy choc jeden taki wpis ma status "ubytek").
Liczenie szersze (informacja, ostrozniejszy): KAZDA praca z prawdy bez ubytkow (takze z drgnieciem, bokiem, z blednym
top-1) z gniazdem czerwonym albo statusem inspekcji "ubytek".
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

ODN = {"R59 pkt 6.2": {"wyr": (40, 40), "top1": (276, 276), "czerw": (0, 127)},
       "E3-A5 runda 4 (pula)": {"wyr": (40, 40), "top1": (276, 276), "czerw": (0, 132)}}
PROG_MM = 0.05


def scen(p: dict) -> str:
    if p.get("drgniecie"):
        return "drgniecie"
    if p.get("ulozenie", "dobrze") != "dobrze":
        return "bokiem"
    if p.get("pokrycie", 1.0) < 1.0:
        return "czesciowo"
    return "dobrze"


def ascii_(t: str) -> str:
    return t.encode("ascii", "backslashreplace").decode("ascii")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wynik-json", type=Path, required=True)
    ap.add_argument("--log", type=Path, required=True)
    ap.add_argument("--skany", type=Path, nargs="+", required=True)
    ap.add_argument("--md", type=Path, required=True)
    ap.add_argument("--json", type=Path, required=True)
    a = ap.parse_args()

    wej = {}  # (zestaw, nazwa stl) -> prawda
    for d in a.skany:
        for stl in sorted(d.glob("skan_*.stl")):
            wej[(d.name, stl.name)] = json.loads(stl.with_suffix(".json").read_text(encoding="utf-8"))
    dane = json.loads(a.wynik_json.read_text(encoding="utf-8"))
    rek = {(r["zestaw"], r["skan"]): r for r in dane["skany"]}
    zb = dane.get("zbiorczo", {})
    niezg = dane.get("uklad_niezgodny", [])
    skrot = lambda z: z.replace("syntetyczne_R59_", "")  # noqa: E731

    w = []  # wiersze md
    out: dict = {}

    # --- A. wyrownanie
    bez_rekordu = [k for k in wej if k not in rek]
    obce = [k for k in rek if k not in wej]
    wyr_ok, wyr_zle, mx = 0, [], 0.0
    for k, r in rek.items():
        m = r["metryki"]["wyrownanie"]["max_przesuniecie_mm"]
        mx = max(mx, m)
        if m < PROG_MM:
            wyr_ok += 1
        else:
            wyr_zle.append((skrot(k[0]), r["plytka"], r["metryki"].get("numer_prawda"), r.get("seed"), round(m, 4)))
    flaga = sum(bool(r["metryki"]["wyrownanie_ok"]) for r in rek.values())
    out["wyrownanie"] = {"skanow_wejscie": len(wej), "rekordow": len(rek), "uklad_niezgodny": len(niezg), "bez_rekordu": len(bez_rekordu),
                         "rekordy_spoza_wejscia": len(obce), "ok_moje": wyr_ok, "ok_flaga_narzedzia": flaga, "max_mm": round(mx, 4), "zle": wyr_zle,
                         "zbiorczo": {k: zb.get("plate_match", {}).get(k) for k in ("skanow", "wyrownanie_ok", "wyrownanie_max_mm", "uklad_niezgodny")}}

    # --- B. top-1 "dobrze" (mianownik z plikow prawdy)
    prac_prawda = 0
    per_scen = {s: {"prac": 0, "top1_ok": 0, "brak_gniazda": 0} for s in ("dobrze", "bokiem", "czesciowo", "drgniecie")}
    bledne_dobrze = []
    # --- C. prace cale
    cale, cale_cz, lista_cz = 0, 0, []
    cale_wp, cale_wp_cz, wielokrotne = 0, 0, []
    cale_alarm, cale_niespr = 0, 0
    szer_prac, szer_cz, lista_szer = 0, 0, []
    for k, pr in wej.items():
        r = rek.get(k)
        gn: dict = {}
        for g in (r["gniazda"] if r else []):
            gn.setdefault(g["gniazdo"], []).append(g)
        for p in pr["prace"]:
            prac_prawda += 1
            s = scen(p)
            per_scen[s]["prac"] += 1
            wpisy = gn.get(p["gniazdo"], [])
            g = wpisy[0] if wpisy else None
            top_ok = bool(wpisy) and all(x.get("projekt") == p["projekt"] for x in wpisy)
            if len(wpisy) > 1:
                wielokrotne.append({"zestaw": skrot(k[0]), "plytka": pr["plytka"], "numer": pr["numer"], "seed": pr["seed"], "gniazdo": p["gniazdo"],
                                    "wpisow": len(wpisy), "scenariusz": s})
            if g is None:
                per_scen[s]["brak_gniazda"] += 1
            per_scen[s]["top1_ok"] += top_ok
            opis = {"zestaw": skrot(k[0]), "plytka": pr["plytka"], "numer": pr["numer"], "seed": pr["seed"], "gniazdo": p["gniazdo"], "sha16": p["projekt"]}
            if s == "dobrze" and not top_ok:
                bledne_dobrze.append({**opis, "powod": "brak gniazda w wyniku" if g is None else "inny pierwszy kandydat albo brak kandydata"})
            if not p["ubytki"]:
                szer_prac += 1
                czerw_w = [x for x in wpisy if x.get("status_gniazda") == "czerwony" or ((x.get("inspekcja") or {}).get("status") == "ubytek")]
                if czerw_w:
                    szer_cz += 1
                    lista_szer.append({**opis, "scenariusz": s, "top1_trafny": top_ok, "status_inspekcji": (czerw_w[0].get("inspekcja") or {}).get("status")})
                if not p.get("drgniecie"):
                    def_w = [x for x in wpisy if x.get("projekt") == p["projekt"] and x.get("inspekcja") is not None]  # wpisy spelniajace definicje pracy calej
                    for x in def_w:
                        st = x["inspekcja"]["status"]
                        cale_wp += 1
                        cale_wp_cz += st == "ubytek"
                        cale_alarm += st in ("ubytek", "sprawdz")
                        cale_niespr += st == "nie_sprawdzono"
                    if def_w:
                        cale += 1
                        if any(x["inspekcja"]["status"] == "ubytek" for x in def_w):
                            cale_cz += 1
                            lista_cz.append({**opis, "scenariusz": s})
    nt_prac = sum(1 for r in rek.values() for g in r["gniazda"] if g["scenariusz"] == "dobrze")
    nt_bl = sum(r["inspekcja"]["scenariusze"]["dobrze"]["top1_bledny"] for r in rek.values())
    out["top1"] = {"prac_prawda_razem": prac_prawda, "per_scenariusz_z_prawdy": per_scen, "dobrze_m": per_scen["dobrze"]["prac"],
                   "dobrze_n": per_scen["dobrze"]["top1_ok"], "bledne_dobrze": bledne_dobrze,
                   "narzedzie_z_rekordow": {"prac": nt_prac, "top1_bledny": nt_bl},
                   "zbiorczo": zb.get("top1_per_scenariusz", {}).get("dobrze")}
    nt_cale = sum(r["inspekcja"]["razem"]["prac_calych"] for r in rek.values())
    nt_cz = sum(r["inspekcja"]["razem"]["prace_cale_z_czerwonym"] for r in rek.values())
    out["wielokrotne_gniazda"] = wielokrotne
    out["czerwone"] = {"prac_calych_moje": cale, "z_czerwonym_moje": cale_cz, "lista": lista_cz, "wpisow_calych_moje": cale_wp, "wpisow_calych_z_czerwonym_moje": cale_wp_cz,
                       "z_alarmem_wpisy_moje": cale_alarm, "nie_sprawdzono_wpisy_moje": cale_niespr,
                       "narzedzie_z_rekordow": {"prac_calych": nt_cale, "z_czerwonym": nt_cz},
                       "zbiorczo": {k: zb.get("razem", {}).get(k) for k in ("prac_calych", "prace_cale_z_czerwonym", "prace_cale_z_alarmem", "prace_cale_nie_sprawdzono")},
                       "szerszy": {"prac_bez_ubytkow_w_prawdzie": szer_prac, "czerwone": szer_cz, "lista": lista_szer}}

    # --- log
    tekst = a.log.read_bytes().decode("utf-8", "replace")
    wiersze = tekst.splitlines()
    skan_w = [x for x in wiersze if x.startswith("skan_")]
    prace_cale_w = [x for x in wiersze if x.startswith("PRACE CA")]
    mlog = re.match(r"PRACE CA\S+: (\d+), z czerwonym (\d+), z alarmem .*?(\d+), nie sprawdzono (\d+)", prace_cale_w[-1]) if prace_cale_w else None
    out["log"] = {"wierszy": len(wiersze), "wierszy_skanow": len(skan_w), "traceback": sum("Traceback" in x for x in wiersze),
                  "nie_pasuje": sum("NIE PASUJE" in x for x in wiersze), "wiersz_prace_cale": ascii_(prace_cale_w[-1]) if prace_cale_w else None,
                  "prace_cale_log": [int(x) for x in mlog.groups()] if mlog else None}

    # --- czasy
    cz = [r["czas_s"]["razem"] for r in rek.values()]
    czasy = {"n": len(cz), "min": min(cz), "mediana": round(statistics.median(cz), 2), "max": max(cz), "suma": round(sum(cz), 1),
             "mediana_etapow": {e: round(statistics.median(r["czas_s"][e] for r in rek.values()), 2) for e in ("plate", "match", "inspect")},
             "czas_calosci_s": zb.get("plate_match", {}).get("czas_calosci_s")} if cz else {}
    out["czasy"] = czasy

    # --- liczby poza kryterium (do porownania z R59 pkt 6.1; informacja)
    pm, rz = zb.get("plate_match", {}), zb.get("razem", {})
    out["informacja"] = {"top1_razem": [pm.get("top1"), pm.get("prac")], "wykrycie_dowolna": [rz.get("wykryte", {}).get("dowolny"), rz.get("ubytkow")],
                         "A_B_czerwone": [rz.get("wykryte", {}).get(x) for x in ("A", "B", "czerwony")],
                         "falszywe_ubytki_miejsca": rz.get("falszywe_ubytki"), "falszywe_czerwone_miejsca": rz.get("falszywe_czerwone"),
                         "drgniecie": zb.get("drgniecie"), "poprawki": zb.get("poprawki"), "statusy_gniazd": pm.get("statusy_gniazd"),
                         "pominiete_projekty": pm.get("pominiete_projekty"), "nie_sprawdzono_powody": zb.get("nie_sprawdzono_prace_cale_powody")}

    # --- werdykty czesci
    A = out["wyrownanie"]
    wA = A["skanow_wejscie"] == 40 and A["rekordow"] == 40 and A["ok_moje"] == 40 and A["uklad_niezgodny"] == 0 and not bez_rekordu
    T = out["top1"]
    wB = T["dobrze_m"] > 0 and T["dobrze_n"] == T["dobrze_m"]
    C = out["czerwone"]
    wC = C["z_czerwonym_moje"] == 0 and cale_wp_cz == 0 and C["prac_calych_moje"] > 0
    zg = (A["ok_moje"] == A["ok_flaga_narzedzia"] == A["zbiorczo"]["wyrownanie_ok"] and A["rekordow"] == A["zbiorczo"]["skanow"]
          and T["zbiorczo"] is not None and T["dobrze_m"] == T["zbiorczo"]["prac"] == nt_prac and (T["dobrze_m"] - T["dobrze_n"]) == T["zbiorczo"]["top1_bledny"] == nt_bl
          and cale_wp == nt_cale == C["zbiorczo"]["prac_calych"] and cale_wp_cz == nt_cz == C["zbiorczo"]["prace_cale_z_czerwonym"]
          and cale_alarm == C["zbiorczo"]["prace_cale_z_alarmem"] and cale_niespr == C["zbiorczo"]["prace_cale_nie_sprawdzono"]
          and out["log"]["prace_cale_log"] is not None and out["log"]["prace_cale_log"] == [cale_wp, cale_wp_cz, cale_alarm, cale_niespr])
    out["werdykty"] = {"wyrownanie": wA, "top1_dobrze": wB, "falszywe_czerwone": wC, "moje_liczby_zgodne_z_narzedziem_i_logiem": zg}

    tak = lambda b: "spelnione" if b else "NIESPELNIONE"  # noqa: E731
    w += ["# T10 - liczby kryterium policzone z plikow wyniku (t10_licz.py)", "",
          "Zrodlo: rekordy skanow pliku wyniku narzedzia + pliki prawdy zestawow (mianowniki); sekcja `zbiorczo` i log tylko do porownania.", "",
          "| Czesc kryterium | Policzone z rekordow / prawdy | `zbiorczo` narzedzia | Log | R59 pkt 6.2 | E3-A5 r4 | Ocena |", "|---|---|---|---|---|---|---|",
          f"| wyrownanie (max blad < 0,05 mm) | {A['ok_moje']} z {A['skanow_wejscie']} (rekordow {A['rekordow']}, uklad niezgodny {A['uklad_niezgodny']}, max {A['max_mm']} mm) | {A['zbiorczo']['wyrownanie_ok']} z {A['zbiorczo']['skanow']} | wierszy skanow {out['log']['wierszy_skanow']} | 40 z 40 | 40 z 40 | {tak(wA)} |",
          f"| top-1 scenariusz \"dobrze\" | {T['dobrze_n']} z {T['dobrze_m']} (bledne {T['dobrze_m'] - T['dobrze_n']}) | prac {T['zbiorczo']['prac'] if T['zbiorczo'] else None}, bledne {T['zbiorczo']['top1_bledny'] if T['zbiorczo'] else None} | - | 276 z 276 | 276 z 276 | {tak(wB)} |",
          f"| falszywe czerwone na pracach calych | wpisy (jak narzedzie): {cale_wp_cz} z {cale_wp}; prace z prawdy (kazda raz): {C['z_czerwonym_moje']} z {C['prac_calych_moje']} | {C['zbiorczo']['prace_cale_z_czerwonym']} z {C['zbiorczo']['prac_calych']} | {out['log']['prace_cale_log'][1] if out['log']['prace_cale_log'] else None} z {out['log']['prace_cale_log'][0] if out['log']['prace_cale_log'] else None} | 0 z 127 | 0 z 132 | {tak(wC)} |", "",
          f"Moje liczby zgodne z `zbiorczo` narzedzia i z wierszem logu \"PRACE CA...\": {'TAK' if zg else 'NIE'}.", "",
          f"Liczenie szersze (informacja): prac bez ubytkow w prawdzie {szer_prac} (kazdy scenariusz, kazdy top-1), z gniazdem czerwonym / statusem \"ubytek\": {szer_cz}.", ""]
    for nazwa, lista in (("Falszywe czerwone na pracach calych (definicja R59)", lista_cz), ("Liczenie szersze - czerwone na pracach bez ubytkow w prawdzie", lista_szer),
                         ("Bledny top-1 w scenariuszu \"dobrze\"", bledne_dobrze)):
        w.append(f"{nazwa}: {len(lista)}")
        for x in lista:
            w.append("- zestaw " + str(x["zestaw"]) + f" / plytka {x['plytka']} nr {x['numer']} seed {x['seed']} / gniazdo {x['gniazdo']} / sha16 {x['sha16']}"
                     + "".join(f" / {k} {x[k]}" for k in ("scenariusz", "top1_trafny", "status_inspekcji", "powod") if k in x))
        w.append("")
    w += [f"Gniazda z wiecej niz jednym wpisem w wyniku (kilka fragmentow w gniezdzie): {len(wielokrotne)}, wg scenariusza pracy: "
          + ", ".join(f"{s} {sum(1 for x in wielokrotne if x['scenariusz'] == s)}" for s in per_scen) + ".", ""]
    if wyr_zle:
        w += ["Wyrownanie poza progiem (zestaw, plytka, numer, seed, mm):"] + [f"- {x}" for x in wyr_zle] + [""]
    if bez_rekordu:
        w += [f"Skany wejsciowe bez rekordu w wyniku: {len(bez_rekordu)}", ""]
    w += ["Prace w prawdzie wg scenariusza (prac / top-1 trafny / brak gniazda w wyniku): "
          + "; ".join(f"{s} {v['prac']} / {v['top1_ok']} / {v['brak_gniazda']}" for s, v in per_scen.items()) + f"; razem {prac_prawda}.", ""]
    if czasy:
        w += [f"Czas na skan (pole `czas_s.razem`, {czasy['n']} skanow): min {czasy['min']} s, mediana {czasy['mediana']} s, max {czasy['max']} s; suma {czasy['suma']} s; "
              f"mediany etapow: plate {czasy['mediana_etapow']['plate']} s, match {czasy['mediana_etapow']['match']} s, inspect {czasy['mediana_etapow']['inspect']} s; "
              f"czas calosci wg narzedzia {czasy['czas_calosci_s']} s. Mierzone pod obciazeniem (patrz WYNIK.md).", ""]
    i = out["informacja"]
    w += ["Liczby poza kryterium T10 (informacja; odniesienie R59 pkt 6.1, kolumna \"R59, zestawy dzisiejsze\"):", "",
          "| Miara | Ten przebieg | R59 pkt 6.1 |", "|---|---|---|",
          f"| top-1 razem | {i['top1_razem'][0]} z {i['top1_razem'][1]} | 382 z 397 |",
          f"| wykrycie dowolna metoda, razem | {i['wykrycie_dowolna'][0]} z {i['wykrycie_dowolna'][1]} | 221 z 248 |",
          f"| metoda A / B / czerwone | {i['A_B_czerwone'][0]} / {i['A_B_czerwone'][1]} / {i['A_B_czerwone'][2]} | 184 / 107 / 79 |",
          f"| prace cale z alarmem | {C['zbiorczo']['prace_cale_z_alarmem']} z {C['zbiorczo']['prac_calych']} | 0 z 127 |",
          f"| falszywe ubytki (miejsca) / w tym czerwone | {i['falszywe_ubytki_miejsca']} / {i['falszywe_czerwone_miejsca']} | 7 / 2 |",
          f"| drgniecie wykryte / prac, falszywe \"skan ponownie\" | {i['drgniecie']} | 35 / 39, 2 (powtorka 1) |",
          f"| poprawki | {i['poprawki']} | 5 / 14 |",
          f"| statusy gniazd | {i['statusy_gniazd']} | zolte 162 / szare 32 (powtorka 161 / 33) |",
          f"| projekty pominiete | {i['pominiete_projekty']} | 283 |",
          f"| prace cale \"nie sprawdzono\" | {C['zbiorczo']['prace_cale_nie_sprawdzono']} (powody: {ascii_(json.dumps(i['nie_sprawdzono_powody'], ensure_ascii=True))}) | - |", ""]
    w += [f"Log: wierszy {out['log']['wierszy']}, wierszy skanow {out['log']['wierszy_skanow']}, \"Traceback\" {out['log']['traceback']}, \"NIE PASUJE\" {out['log']['nie_pasuje']}.", ""]
    a.md.write_bytes(ascii_("\n".join(w)).encode("ascii"))
    a.json.write_bytes((json.dumps(out, ensure_ascii=True, indent=1) + "\n").encode("ascii"))
    print(json.dumps({k: out[k] for k in ("werdykty", "czasy")}, ensure_ascii=True))
    print("wyrownanie", A["ok_moje"], "z", A["skanow_wejscie"], "| top-1 dobrze", T["dobrze_n"], "z", T["dobrze_m"], "| czerwone na calych", C["z_czerwonym_moje"], "z", C["prac_calych_moje"],
          "(wpisy", cale_wp_cz, "z", cale_wp, ") | szerszy", szer_cz, "z", szer_prac, "| gniazd wielokrotnych", len(wielokrotne))
    return 0 if (wA and wB and wC) else 1


if __name__ == "__main__":
    sys.exit(main())
