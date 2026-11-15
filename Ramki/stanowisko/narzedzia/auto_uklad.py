"""Pomiar automatycznego rozpoznania ukladu plytki (``plate.rozpoznaj_uklad``) na skanach z prawda.

Uzycie (z katalogu stanowisko/):
    py -3.12 narzedzia/auto_uklad.py --skany <folder> [<folder2> ...] [--wyjscie dane/auto_uklad] [--procesy 8] [--limit N]

Dla kazdego pliku ``skan_*.stl`` z plikiem prawdy ``.json`` obok (generator ``stanowisko.synth``) uruchamia rozpoznanie
na wszystkich ukladach z ``[plytki]`` dwa razy: bez numeru plytki (pierwsze uruchomienie okna) i - dla plytek
kwadratowych - z numerem z prawdy (czlowiek wpisal numer). Liczy: ile skanow rozpoznano poprawnie (uklad = prawda),
ile z flaga ``pewny``, na jakiej podstawie (jedyny pasujacy / numer podany / numer z dolkow / ksztalt / dolki wykluczaja /
domyslny), miary ksztaltu brzegu dla ukladu wlasciwego i dla drugiego ksztaltu tej samej rodziny (do oceny progu
``plate.PROG_KSZTALTU_MM2``) oraz czas rozpoznania. Wynik: ``<wyjscie>/auto_uklad.json`` i tabela na stdout.
W wyniku sa tylko nazwy plikow skanow (bez nazw projektow).
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

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def zadanie(arg: tuple) -> dict:
    plik, ustawienia = arg
    import trimesh

    from stanowisko import plate, porownaj as PO, synth, ustawienia as UST

    ust = UST.wczytaj_ustawienia(ustawienia)
    uklady = list(PO.uklady_z_ustawien(ust).values())
    prawda = synth.wczytaj_prawde(Path(plik).with_suffix(".json"))
    wpis: dict = {"skan": Path(plik).name, "prawda": prawda.plytka, "numer_prawda": prawda.numer, "prac": len(prawda.prace), "przebiegi": {}}
    m = trimesh.load(plik, force="mesh")
    kwadrat = next(u for u in uklady if u.nazwa == prawda.plytka).shape == "square"
    for nazwa, numer in (("bez_numeru", None),) + ((("z_numerem", prawda.numer),) if kwadrat else ()):
        t0 = time.time()
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                wyr, info = plate.rozpoznaj_uklad(m, uklady, numer=numer, ciecie=False)
            wlasciwy = next((k for k in info["kandydaci"] if k["uklad"] == prawda.plytka), {})
            inne = [k for k in info["kandydaci"] if k["uklad"] != prawda.plytka and "ksztalt_niewyjasnione_mm2" in k]
            wpis["przebiegi"][nazwa] = {
                "wybrany": info["wybrany"], "ok": info["wybrany"] == prawda.plytka, "pewny": info["pewny"], "powod": info["powod"],
                "numer": wyr.numer, "numer_zrodlo": wyr.numer_zrodlo, "numer_ok": wyr.numer == prawda.numer,
                "ksztalt_wlasciwy_mm2": wlasciwy.get("ksztalt_niewyjasnione_mm2"), "ksztalt_strefa_mm2": wlasciwy.get("ksztalt_strefa_mm2"),
                "ksztalt_inny_mm2": [k["ksztalt_niewyjasnione_mm2"] for k in inne],
                "inny_dolki_widoczne": [k.get("dolki_widoczne") for k in inne], "inny_numer_z_dolkow": [k.get("numer_z_dolkow") for k in inne],
                "kandydatow_po_strazniku": 1 + len(inne), "czas_s": round(time.time() - t0, 2), "czas_rozpoznania_s": info["czas_rozpoznania_s"],
            }
        except Exception as e:  # noqa: BLE001 - blad jednego skanu nie zatrzymuje pomiaru
            wpis["przebiegi"][nazwa] = {"wybrany": None, "ok": False, "pewny": False, "powod": f"BLAD {type(e).__name__}: {e}", "czas_s": round(time.time() - t0, 2)}
    return wpis


def podsumuj(wyniki: list[dict]) -> dict:
    pods: dict = {}
    for przebieg in ("bez_numeru", "z_numerem"):
        w = [(x["prawda"], x["przebiegi"][przebieg]) for x in wyniki if przebieg in x["przebiegi"]]
        if not w:
            continue
        per: dict = {}
        for plytka in sorted({p for p, _ in w}):
            r = [x for p, x in w if p == plytka]
            per[plytka] = {"skanow": len(r), "ok": sum(x["ok"] for x in r), "ok_i_pewny": sum(x["ok"] and x["pewny"] for x in r),
                           "zle_ale_pewny": sum((not x["ok"]) and x["pewny"] for x in r), "powody": dict(Counter(x["powod"] for x in r))}
        r = [x for _, x in w]
        wl = [x["ksztalt_wlasciwy_mm2"] for x in r if x.get("ksztalt_wlasciwy_mm2") is not None]
        inn = [v for x in r for v in x.get("ksztalt_inny_mm2", [])]
        czasy = sorted(x["czas_rozpoznania_s"] for x in r if "czas_rozpoznania_s" in x)
        pods[przebieg] = {
            "skanow": len(r), "ok": sum(x["ok"] for x in r), "ok_i_pewny": sum(x["ok"] and x["pewny"] for x in r),
            "zle_ale_pewny": sum((not x["ok"]) and x["pewny"] for x in r), "numer_ok": sum(bool(x.get("numer_ok")) for x in r),
            "powody": dict(Counter(x["powod"] for x in r)), "per_plytka": per,
            "ksztalt_wlasciwy_max_mm2": max(wl) if wl else None, "ksztalt_inny_min_mm2": min(inn) if inn else None,
            "czas_rozpoznania_mediana_s": czasy[len(czasy) // 2] if czasy else None, "czas_rozpoznania_max_s": czasy[-1] if czasy else None,
        }
    return pods


def main(argv: list[str] | None = None) -> dict:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--skany", type=Path, nargs="+", required=True, help="foldery ze skanami skan_*.stl i prawda .json")
    ap.add_argument("--wyjscie", type=Path, default=Path("dane/auto_uklad"))
    ap.add_argument("--procesy", type=int, default=8)
    ap.add_argument("--limit", type=int, default=0, help="najwyzej tyle skanow z kazdego folderu (0 = wszystkie)")
    ap.add_argument("--ustawienia", type=Path, default=None)
    a = ap.parse_args(argv)
    pliki = []
    for f in a.skany:
        z = sorted(p for p in f.glob("skan_*.stl") if p.with_suffix(".json").exists())
        pliki += z[: a.limit] if a.limit else z
    if not pliki:
        raise SystemExit("brak skanow z prawda w podanych folderach")
    t0 = time.time()
    with mp.get_context("spawn").Pool(max(1, min(a.procesy, len(pliki)))) as pool:
        wyniki = list(pool.imap_unordered(zadanie, [(str(p), a.ustawienia) for p in pliki]))
    wyniki.sort(key=lambda x: x["skan"])
    wynik = {"skanow": len(wyniki), "czas_calosci_s": round(time.time() - t0, 1), "podsumowanie": podsumuj(wyniki), "skany": wyniki}
    a.wyjscie.mkdir(parents=True, exist_ok=True)
    (a.wyjscie / "auto_uklad.json").write_text(json.dumps(wynik, ensure_ascii=False, indent=1), encoding="utf-8")
    for przebieg, p in wynik["podsumowanie"].items():
        print(f"{przebieg}: poprawnie {p['ok']}/{p['skanow']}, poprawnie i pewnie {p['ok_i_pewny']}/{p['skanow']}, zle ale pewnie {p['zle_ale_pewny']}/{p['skanow']}, "
              f"numer ok {p['numer_ok']}/{p['skanow']}; podstawy: {p['powody']}; ksztalt: wlasciwy max {p['ksztalt_wlasciwy_max_mm2']} mm2, "
              f"inny min {p['ksztalt_inny_min_mm2']} mm2; czas rozpoznania mediana {p['czas_rozpoznania_mediana_s']} s, max {p['czas_rozpoznania_max_s']} s")
        for plytka, r in p["per_plytka"].items():
            print(f"  {plytka:24s} {r['ok']}/{r['skanow']} (pewnie {r['ok_i_pewny']}) {r['powody']}")
    for x in wyniki:
        for przebieg, r in x["przebiegi"].items():
            if not r["ok"] or not r["pewny"]:
                print(f"  UWAGA {x['skan']} [{przebieg}]: prawda {x['prawda']}, wybrany {r['wybrany']}, pewny {r['pewny']}, {r['powod']}")
    print(a.wyjscie / "auto_uklad.json")
    return wynik


if __name__ == "__main__":
    main()
