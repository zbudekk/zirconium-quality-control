"""Metryki plate + match + inspect na zestawach sztucznych skanów z prawdą (sesja P3a).

Użycie (z katalogu stanowisko/):
    py -3.12 narzedzia/metryki_P3a.py --skany dane/syntetyczne_P2 dane/syntetyczne_P3a --projekty C:/Users/.../Prace_test
        [--wyjscie dane/wyniki_P3a] [--limit N] [--wzorzec "skan_*.stl"]

Dla każdego skanu pełny łańcuch ``porownaj.porownaj`` (plate → match → inspect) i metryki na prawdzie
(``porownaj.metryki`` + ``porownaj.metryki_inspekcji``). Zbiorczo: wykryte / fałszywe ubytki per metoda
(A, B, A+B, czerwone, dowolne) i per scenariusz pracy (dobrze / bokiem / częściowo / drgnięcie), drgnięcie,
poprawki, statusy gniazd, czasy. Wynik: ``<wyjscie>/metryki_P3a.json`` i tabela na stdout — bez nazw plików projektów.

Sztuczne skany są danymi do budowy i pomiaru kodu; test skanera będzie w P3b na prawdziwych płytkach.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from stanowisko import match as M  # noqa: E402
from stanowisko import porownaj as PO  # noqa: E402
from stanowisko import synth as S  # noqa: E402
from stanowisko import ustawienia as UST  # noqa: E402


def _dodaj(suma: dict, czesc: dict) -> None:
    for k, v in czesc.items():
        if isinstance(v, dict):
            suma.setdefault(k, {})
            _dodaj(suma[k], v)
        elif isinstance(v, (int, float)) and not isinstance(v, bool):
            suma[k] = suma.get(k, 0) + v


def udzialy(s: dict) -> dict:
    """Odsetki z liczników jednego scenariusza (albo „razem”)."""
    n = s["ubytkow"]
    c = s["prac_calych"]
    return {
        "wykryte_udzial": {k: (round(v / n, 4) if n else None) for k, v in s["wykryte"].items()},
        "prace_cale_z_alarmem_udzial": round(s["prace_cale_z_alarmem"] / c, 4) if c else None,
        "prace_cale_z_czerwonym_udzial": round(s["prace_cale_z_czerwonym"] / c, 4) if c else None,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--skany", type=Path, nargs="+", default=[Path("dane/syntetyczne_P2"), Path("dane/syntetyczne_P3a")])
    ap.add_argument("--projekty", type=Path, nargs="+", required=True)
    ap.add_argument("--wyjscie", type=Path, default=Path("dane/wyniki_P3a"))
    ap.add_argument("--limit", type=int, default=None, help="tylko pierwsze N skanów (próba)")
    ap.add_argument("--wzorzec", default="skan_*.stl")
    ap.add_argument("--nazwa", default="metryki_P3a.json")
    ap.add_argument("--ustawienia", type=Path, default=None)
    a = ap.parse_args()
    ust = UST.wczytaj_ustawienia(a.ustawienia)
    skany = sorted(p for d in a.skany for p in d.glob(a.wzorzec))[: a.limit]
    if not skany:
        raise SystemExit(f"brak skanów w {a.skany}")
    a.wyjscie.mkdir(parents=True, exist_ok=True)
    pule: dict[float, M.Pula] = {}
    wyniki = []
    t_start = time.time()
    for p in skany:
        prawda = S.wczytaj_prawde(p.with_suffix(".json"))
        w = float(np.mean([x.wspolczynnik for x in prawda.prace])) if prawda.prace else 1.0
        if w not in pule:
            pule[w] = M.Pula(list(a.projekty), w)
        with warnings.catch_warnings(record=True) as ostrz:
            warnings.simplefilter("always")
            wynik = PO.porownaj(p, list(a.projekty), prawda.plytka, ust, w, None, "auto", False, pule[w])
        mt = PO.metryki(wynik, prawda, pule[w])
        mi = PO.metryki_inspekcji(wynik, prawda)
        rek = {
            "skan": p.name, "zestaw": p.parent.name, "plytka": prawda.plytka, "seed": prawda.seed, "czas_s": wynik["czas_s"],
            "ostrzezenia": [str(o.message) for o in ostrz], "metryki": mt, "inspekcja": mi, "statusy_gniazd": wynik["statusy_gniazd"],
            "gniazda": [{"gniazdo": g["gniazdo"], "status": g["status"], "status_gniazda": g["status_gniazda"],
                         "inspekcja": ({k: v for k, v in g["inspekcja"].items() if k in ("status", "ubytki", "drgniecie", "linia_brzegu", "odchylki", "czas_s")} if g["inspekcja"] else None),
                         "scenariusz": (PO.scenariusz(next(x for x in prawda.prace if x.gniazdo == g["gniazdo"])) if any(x.gniazdo == g["gniazdo"] for x in prawda.prace) else None)}
                        for g in wynik["gniazda"]],
        }
        wyniki.append(rek)
        r = mi["razem"]
        print(f"{p.name:38s} wyr {mt['wyrownanie']['max_przesuniecie_mm']:.4f}  top1 {mt['top1']}/{mt['prac_prawda']}  "
              f"ubytki {r['ubytkow']}: A {r['wykryte']['A']} B {r['wykryte']['B']} A+B {r['wykryte']['A+B']} cz {r['wykryte']['czerwony']} any {r['wykryte']['dowolny']}  "
              f"całe {r['prac_calych']} alarm {r['prace_cale_z_alarmem']} cz {r['prace_cale_z_czerwonym']}  drg {mi['drgniecie']['wykryte']}/{mi['drgniecie']['prac']}  "
              f"gniazda {wynik['statusy_gniazd']}  {wynik['czas_s']['razem']} s", flush=True)

    zb = {"scenariusze": {s: {} for s in PO.SCENARIUSZE}, "razem": {}, "drgniecie": {}, "poprawki": {}}
    for rek in wyniki:
        for s in PO.SCENARIUSZE:
            _dodaj(zb["scenariusze"][s], rek["inspekcja"]["scenariusze"][s])
        _dodaj(zb["razem"], rek["inspekcja"]["razem"])
        _dodaj(zb["drgniecie"], rek["inspekcja"]["drgniecie"])
        _dodaj(zb["poprawki"], rek["inspekcja"]["poprawki"])
    for s in PO.SCENARIUSZE:
        zb["scenariusze"][s]["udzialy"] = udzialy(zb["scenariusze"][s])
    zb["razem"]["udzialy"] = udzialy(zb["razem"])
    zb["plate_match"] = {
        "skanow": len(wyniki),
        "wyrownanie_ok": sum(r["metryki"]["wyrownanie_ok"] for r in wyniki),
        "wyrownanie_max_mm": max(r["metryki"]["wyrownanie"]["max_przesuniecie_mm"] for r in wyniki),
        "prac": sum(r["metryki"]["prac_prawda"] for r in wyniki),
        "fragment_w_swoim_gniezdzie": sum(r["metryki"]["fragment_w_swoim_gniezdzie"] for r in wyniki),
        "top1": sum(r["metryki"]["top1"] for r in wyniki), "top2": sum(r["metryki"]["top2"] for r in wyniki),
        "statusy_match": {s: sum(r["metryki"]["statusy"][s] for r in wyniki) for s in M.STATUSY},
        "statusy_gniazd": {s: sum(r["statusy_gniazd"][s] for r in wyniki) for s in PO.STATUSY_GNIAZDA},
        "czas_s_mediana": {k: float(np.median([r["czas_s"][k] for r in wyniki])) for k in ("plate", "match", "inspect", "razem")},
        "czas_calosci_s": round(time.time() - t_start, 1),
    }
    zb["top1_per_scenariusz"] = {}
    for s in PO.SCENARIUSZE:
        prac = sum(1 for r in wyniki for g in r["gniazda"] if g["scenariusz"] == s)
        bledne = sum(r["inspekcja"]["scenariusze"][s]["top1_bledny"] for r in wyniki)
        st = {k: sum(1 for r in wyniki for g in r["gniazda"] if g["scenariusz"] == s and g["status_gniazda"] == k) for k in PO.STATUSY_GNIAZDA}
        zb["top1_per_scenariusz"][s] = {"prac": prac, "top1_bledny": bledne, "top1_udzial": round((prac - bledne) / prac, 4) if prac else None, "statusy_gniazd": st}
    out = {"skany": wyniki, "zbiorczo": zb}
    (a.wyjscie / a.nazwa).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\nZBIORCZO:", json.dumps({k: v for k, v in zb.items() if k != "scenariusze"}, ensure_ascii=False))
    for s, v in zb["scenariusze"].items():
        print(f"SCENARIUSZ {s}: {json.dumps(v, ensure_ascii=False)}")
    print(a.wyjscie / a.nazwa)


if __name__ == "__main__":
    main()
