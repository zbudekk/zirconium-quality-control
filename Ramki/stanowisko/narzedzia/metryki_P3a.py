"""Metryki plate + match + inspect na zestawach sztucznych skanów z prawdą (sesja P3a).

Użycie (z katalogu stanowisko/):
    py -3.12 narzedzia/metryki_P3a.py --skany dane/syntetyczne_P2 dane/syntetyczne_P3a --projekty C:/Users/.../Prace_test
        [--wyjscie dane/wyniki_P3a] [--limit N] [--wzorzec "skan_*.stl"] [--sufiks-ukladu _r54] [--procesy N]

``--sufiks-ukladu _r54``: zestawy wygenerowane przed R59 (``dane/syntetyczne_P2``, ``dane/syntetyczne_P3a``) mają w prawdzie
płytkę ``wieczorna`` / ``poranna`` / ``okragla_…``, a to był układ gniazd R54 — przyrostek kieruje je na układy ``*_r54``.
Skan, który nie pasuje do układu (strażnik układu), trafia do listy ``uklad_niezgodny`` i nie wchodzi do metryk.

Dla każdego skanu pełny łańcuch ``porownaj.porownaj`` (plate → match → inspect) i metryki na prawdzie
(``porownaj.metryki`` + ``porownaj.metryki_inspekcji``). Zbiorczo: wykryte / fałszywe ubytki per metoda
(A, B, A+B, czerwone, dowolne) i per scenariusz pracy (dobrze / bokiem / częściowo / drgnięcie), drgnięcie,
poprawki, statusy gniazd, czasy. Wynik: ``<wyjscie>/metryki_P3a.json`` i tabela na stdout — bez nazw plików projektów.

Sztuczne skany są danymi do budowy i pomiaru kodu; test skanera będzie w P3b na prawdziwych płytkach.
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
from stanowisko import match as M  # noqa: E402
from stanowisko import porownaj as PO  # noqa: E402
from stanowisko import synth as S  # noqa: E402
from stanowisko import uklad as U  # noqa: E402
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


def klasa_gniazda(g: U.Gniazdo) -> str:
    """Klasa gniazda do metryk per średnica: ``fi12`` / ``fi12.5`` / ``fi15`` … albo ``rynienka``."""
    return f"fi{g.d_top:g}" if g.okragle else "rynienka"


LIMIT_SKANU_S = 1800  # górna granica czasu jednego skanu przy --procesy (zawieszony proces kończy pomiar błędem)
_PULE: dict[tuple, M.Pula] = {}  # pamięć procesu: (foldery, współczynnik) → pula projektów
_UKLADY: dict[str, U.UkladPlytki] = {}


def przelicz_skan(arg: tuple) -> dict:
    """Jeden skan: ``porownaj`` + metryki na prawdzie. Zwraca ``{"rek": …, "linia": …}`` albo ``{"niezgodny": …, "linia": …}``.

    Funkcja na poziomie modułu, bo przy ``--procesy N`` wykonują ją procesy robocze (każdy z własną pulą projektów).
    """
    p, projekty, sufiks, plik_ustawien = arg
    ust = UST.wczytaj_ustawienia(plik_ustawien)
    prawda = S.wczytaj_prawde(p.with_suffix(".json"))
    plytka = prawda.plytka if prawda.plytka.endswith(sufiks) else prawda.plytka + sufiks
    if plytka not in _UKLADY:
        _UKLADY[plytka] = U.wczytaj(plytka, UST.katalog_plytki(ust, plytka))
    w = float(np.mean([x.wspolczynnik for x in prawda.prace])) if prawda.prace else 1.0
    if (projekty, w) not in _PULE:
        _PULE[(projekty, w)] = M.Pula(list(projekty), w)
    pula = _PULE[(projekty, w)]
    with warnings.catch_warnings(record=True) as ostrz:
        warnings.simplefilter("always")
        wynik = PO.porownaj(p, list(projekty), plytka, ust, w, None, "auto", False, pula)
    if wynik.get("uklad_zgodny") is False:  # strażnik układu: skan nie pasuje do układu — bez metryk
        return {"niezgodny": {"skan": p.name, "zestaw": p.parent.name, "plytka": plytka, "pasujace": wynik["uklady_pasujace"], "komunikat": wynik["uklad_komunikat"]},
                "linia": f"{p.name:38s} PŁYTKA NIE PASUJE DO UKŁADU {plytka} (pasujące: {', '.join(wynik['uklady_pasujace']) or 'brak'})"}
    mt = PO.metryki(wynik, prawda, pula)
    mi = PO.metryki_inspekcji(wynik, prawda)
    klasy = {g.id: klasa_gniazda(g) for g in _UKLADY[plytka].sockets}
    per_klasa = {}
    for k in sorted(set(klasy.values())):  # te same liczniki co „razem”, ale tylko dla prac w gniazdach jednej średnicy
        czesc = PO.metryki_inspekcji({**wynik, "gniazda": [g for g in wynik["gniazda"] if klasy.get(g["gniazdo"]) == k]}, prawda)
        per_klasa[k] = {**czesc["razem"], "prac_prawda": sum(1 for x in prawda.prace if klasy.get(x.gniazdo) == k),
                        "drgniecie": czesc["drgniecie"], "poprawki": czesc["poprawki"]}
    rek = {
        "skan": p.name, "zestaw": p.parent.name, "plytka": plytka, "seed": prawda.seed, "czas_s": wynik["czas_s"],
        "straznik": {k: v for k, v in wynik["jakosc_wyrownania"].items() if k.startswith("uklad_")}, "per_klasa_gniazda": per_klasa,
        "pominiete": len(prawda.pominiete),
        "ostrzezenia": [str(o.message) for o in ostrz], "metryki": mt, "inspekcja": mi, "statusy_gniazd": wynik["statusy_gniazd"],
        "gniazda": [{"gniazdo": g["gniazdo"], "status": g["status"], "status_gniazda": g["status_gniazda"],
                     "inspekcja": ({k: v for k, v in g["inspekcja"].items() if k in ("status", "ubytki", "drgniecie", "linia_brzegu", "odchylki", "czas_s")} if g["inspekcja"] else None),
                     "klasa": klasy.get(g["gniazdo"]),
                     "scenariusz": (PO.scenariusz(next(x for x in prawda.prace if x.gniazdo == g["gniazdo"])) if any(x.gniazdo == g["gniazdo"] for x in prawda.prace) else None)}
                    for g in wynik["gniazda"]],
    }
    r = mi["razem"]
    linia = (f"{p.name:38s} wyr {mt['wyrownanie']['max_przesuniecie_mm']:.4f}  top1 {mt['top1']}/{mt['prac_prawda']}  "
             f"ubytki {r['ubytkow']}: A {r['wykryte']['A']} B {r['wykryte']['B']} A+B {r['wykryte']['A+B']} cz {r['wykryte']['czerwony']} any {r['wykryte']['dowolny']}  "
             f"całe {r['prac_calych']} alarm {r['prace_cale_z_alarmem']} cz {r['prace_cale_z_czerwonym']}  drg {mi['drgniecie']['wykryte']}/{mi['drgniecie']['prac']}  "
             f"gniazda {wynik['statusy_gniazd']}  {wynik['czas_s']['razem']} s")
    return {"rek": rek, "linia": linia}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--skany", type=Path, nargs="+", default=[Path("dane/syntetyczne_P2"), Path("dane/syntetyczne_P3a")])
    ap.add_argument("--projekty", type=Path, nargs="+", required=True)
    ap.add_argument("--wyjscie", type=Path, default=Path("dane/wyniki_P3a"))
    ap.add_argument("--limit", type=int, default=None, help="tylko pierwsze N skanów (próba)")
    ap.add_argument("--wzorzec", default="skan_*.stl")
    ap.add_argument("--nazwa", default="metryki_P3a.json")
    ap.add_argument("--ustawienia", type=Path, default=None)
    ap.add_argument("--sufiks-ukladu", default="", help="przyrostek układu dopisywany do nazwy płytki z prawdy, np. _r54 dla zestawów sprzed R59")
    ap.add_argument("--procesy", type=int, default=1, help="ile skanów liczyć równolegle (osobne procesy; czasy na płytkę są wtedy zawyżone)")
    a = ap.parse_args()
    UST.wczytaj_ustawienia(a.ustawienia)  # błąd w pliku ustawień od razu, nie w procesie roboczym
    skany = sorted(p for d in a.skany for p in d.glob(a.wzorzec))[: a.limit]
    if not skany:
        raise SystemExit(f"brak skanów w {a.skany}")
    a.wyjscie.mkdir(parents=True, exist_ok=True)
    zadania = [(p, tuple(a.projekty), a.sufiks_ukladu, a.ustawienia) for p in skany]
    wyniki = []
    niezgodne = []
    t_start = time.time()

    def przyjmij(odp: dict) -> None:
        print(odp["linia"], flush=True)
        if "niezgodny" in odp:
            niezgodne.append(odp["niezgodny"])
        else:
            wyniki.append(odp["rek"])

    if a.procesy > 1:  # skany są niezależne: każdy proces ma własną pulę projektów; kolejność wyników = kolejność skanów
        with mp.Pool(a.procesy) as pool:
            it = pool.imap(przelicz_skan, zadania)
            for _ in zadania:
                przyjmij(it.next(timeout=LIMIT_SKANU_S))
    else:
        for z in zadania:
            przyjmij(przelicz_skan(z))

    if not wyniki:
        (a.wyjscie / a.nazwa).write_text(json.dumps({"skany": [], "zbiorczo": {}, "uklad_niezgodny": niezgodne}, ensure_ascii=False, indent=1), encoding="utf-8")
        raise SystemExit(f"żaden z {len(skany)} skanów nie pasuje do układu — zestaw sprzed R59? (--sufiks-ukladu _r54); {a.wyjscie / a.nazwa}")
    zb = {"scenariusze": {s: {} for s in PO.SCENARIUSZE}, "razem": {}, "drgniecie": {}, "poprawki": {}, "per_klasa_gniazda": {}}
    for rek in wyniki:
        for k, v in rek["per_klasa_gniazda"].items():
            zb["per_klasa_gniazda"].setdefault(k, {})
            _dodaj(zb["per_klasa_gniazda"][k], v)
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
        "uklad_niezgodny": len(niezgodne), "pominiete_projekty": sum(r["pominiete"] for r in wyniki),
        "straznik_max_gniazdo_nad_pelnym_mm2": max(r["straznik"].get("uklad_gniazdo_nad_pelnym_mm2", 0.0) for r in wyniki),
        "straznik_max_dziura_w_pelnym_mm2": max(r["straznik"].get("uklad_dziura_w_pelnym_mm2", 0.0) for r in wyniki),
    }
    zb["top1_per_scenariusz"] = {}
    for s in PO.SCENARIUSZE:
        prac = sum(1 for r in wyniki for g in r["gniazda"] if g["scenariusz"] == s)
        bledne = sum(r["inspekcja"]["scenariusze"][s]["top1_bledny"] for r in wyniki)
        st = {k: sum(1 for r in wyniki for g in r["gniazda"] if g["scenariusz"] == s and g["status_gniazda"] == k) for k in PO.STATUSY_GNIAZDA}
        zb["top1_per_scenariusz"][s] = {"prac": prac, "top1_bledny": bledne, "top1_udzial": round((prac - bledne) / prac, 4) if prac else None, "statusy_gniazd": st}
    out = {"skany": wyniki, "zbiorczo": zb, "uklad_niezgodny": niezgodne}
    (a.wyjscie / a.nazwa).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\nZBIORCZO:", json.dumps({k: v for k, v in zb.items() if k not in ("scenariusze", "per_klasa_gniazda")}, ensure_ascii=False))
    for k, v in zb["per_klasa_gniazda"].items():
        print(f"GNIAZDA {k}: prac {v.get('prac_prawda', 0)}, top-1 błędny {v.get('top1_bledny', 0)}, ubytków {v.get('ubytkow', 0)}, wykryte {json.dumps(v.get('wykryte', {}), ensure_ascii=False)}, "
              f"prace całe {v.get('prac_calych', 0)}, z alarmem {v.get('prace_cale_z_alarmem', 0)}, fałszywe czerwone {v.get('falszywe_czerwone', 0)}")
    for s, v in zb["scenariusze"].items():
        print(f"SCENARIUSZ {s}: {json.dumps(v, ensure_ascii=False)}")
    print(a.wyjscie / a.nazwa)


if __name__ == "__main__":
    main()
