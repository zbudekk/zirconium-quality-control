"""Pomiary do paczki "krawedz brzegu" (P2 / P4): linie krawedzi projektow, generator ubytkow, metryki krawedz / sciana.

Uzycie (z katalogu stanowisko/; wynik: JSON w ``--wyjscie`` i tabela na stdout, bez nazw plikow projektow):
    py -3.12 narzedzia/metryki_krawedz.py linie --projekty <folder> [--wspolczynnik 1.22] [--procesy N]
        linie krawedzi brzegu kazdego projektu: liczba petli, dlugosci, przekroje zweryfikowane, werdykt, czas;
        zasieg pasa brzegu: udzial linii ponizej starego pasa (plaszczyzna z = -pas) i w nowym pasie (od linii)

Sztuczne dane sa wylacznie do budowy i pomiaru kodu; rozstrzyga test skanera (P3b).
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from stanowisko import krawedz as KR  # noqa: E402
from stanowisko import match as M  # noqa: E402
from stanowisko import synth as S  # noqa: E402
from stanowisko import ustawienia as UST  # noqa: E402


# ----------------------------------------------------------------------------
# linie
# ----------------------------------------------------------------------------
def _linie_projektu(arg: tuple) -> dict:
    plik, w, pas, katalog = arg
    if katalog is not None:
        KR.ustaw_katalog_pamieci(katalog)
    t0 = time.time()
    pr = M.Projekt(plik, w)
    t1 = time.time()
    linie = KR.linie_siatki(pr.siatka, skala=w, klucz=pr.id)
    t2 = time.time()
    op = linie.opis()
    for f, d in zip(linie.filary, op["filary"]):
        O = f.linie["O"]
        seg = np.linalg.norm(np.roll(O.X, -1, 0) - O.X, axis=1)
        zmid = (np.roll(O.X, -1, 0)[:, 2] + O.X[:, 2]) / 2
        d["udzial_O_ponizej_starego_pasa"] = round(float(seg[zmid < -pas].sum() / seg.sum()), 4)
        d["caly_ponizej_starego_pasa"] = bool((O.X[:, 2] < -pas).all())
    return {"projekt": pr.id, "typ": pr.cechy.typ, "zeby": pr.cechy.zeby, "szczelna": bool(pr.siatka.is_watertight),
            "trojkatow": int(len(pr.siatka.faces)), "czas_puli_s": round(t1 - t0, 2), "czas_linii_s": round(t2 - t1, 2), **op}


def polecenie_linie(a) -> None:
    ust = UST.wczytaj_ustawienia(a.ustawienia)
    pas = ust["inspect"]["pas_brzegu_mm"]
    pliki = S.pliki_projektow(a.projekty)
    if not pliki:
        raise SystemExit(f"brak plikow STL w {a.projekty}")
    a.wyjscie.mkdir(parents=True, exist_ok=True)
    zadania = [(p, a.wspolczynnik, pas, a.pamiec) for p in pliki]
    t0 = time.time()
    if a.procesy > 1:
        with mp.Pool(a.procesy) as pool:
            wyniki = pool.map(_linie_projektu, zadania)
    else:
        wyniki = [_linie_projektu(z) for z in zadania]
    wyniki.sort(key=lambda r: r["projekt"])
    filary = [f for r in wyniki for f in r["filary"]]
    wielo = [f for r in wyniki if r["filarow"] > 1 for f in r["filary"]]
    zb = {
        "projektow": len(wyniki), "petli": len(filary), "projekty_bez_linii": sum(1 for r in wyniki if r["filarow"] == 0),
        "petle_werdykt": {w: sum(1 for f in filary if f["werdykt"] == w) for w in KR.WERDYKTY},
        "projekty_stan": {s: sum(1 for r in wyniki if r["stan"] == s) for s in ("wiarygodne", "czesciowe", "brak")},
        "wieloczlonowe_projektow": sum(1 for r in wyniki if r["filarow"] > 1), "wieloczlonowe_petli": len(wielo),
        "wieloczlonowe_petle_cale_ponizej_starego_pasa": sum(1 for f in wielo if f["caly_ponizej_starego_pasa"]),
        "petle_cale_ponizej_starego_pasa": sum(1 for f in filary if f["caly_ponizej_starego_pasa"]),
        "pas_brzegu_mm": pas, "wspolczynnik": a.wspolczynnik, "wersja_linii": KR.WERSJA,
        "czas_linii_s_mediana": float(np.median([r["czas_linii_s"] for r in wyniki])), "czas_linii_s_max": max(r["czas_linii_s"] for r in wyniki),
        "czas_calosci_s": round(time.time() - t0, 1),
    }
    (a.wyjscie / a.nazwa).write_text(json.dumps({"projekty": wyniki, "zbiorczo": zb}, ensure_ascii=False, indent=1), encoding="utf-8")
    print("projekt           typ          zeby         filar war. zweryf.      ciag  przerwa  werdykt     dl. O (zweryf.)  z O                 pod starym pasem  czas")
    for r in wyniki:
        if not r["filary"]:
            print(f"{r['projekt']}  {r['typ']:11s}  {'-'.join(r['zeby']):11s}  BRAK LINII: {'; '.join(r['uwagi'])}  {r['czas_linii_s']} s")
        for f in r["filary"]:
            print(f"{r['projekt']}  {r['typ']:11s}  {'-'.join(r['zeby']):11s}  {f['nr']:>3d}   {f['wariant']}   {f['przekroje_zweryfikowane']:>3d}/{f['przekroje']} ({f['udzial_zweryf']:.2f})"
                  f"  {f['najdl_ciag_st']:>5.1f}  {f['najdl_przerwa_mm']:>5.2f}  {f['werdykt']:10s}  {f['dlugosc_O_mm']:>5.1f} ({f['dlugosc_O_zweryf_mm']:>5.1f})"
                  f"  {f['z_O_min_max'][0]:>6.2f} ... {f['z_O_min_max'][1]:>5.2f}  {f['udzial_O_ponizej_starego_pasa']:>6.2f}{' CALY' if f['caly_ponizej_starego_pasa'] else '     '}"
                  f"  {r['czas_linii_s']} s")
    print("ZBIORCZO:", json.dumps(zb, ensure_ascii=False))
    print(a.wyjscie / a.nazwa)


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="polecenie", required=True)
    p = sub.add_parser("linie", help="linie krawedzi brzegu projektow i zasieg pasa brzegu")
    p.add_argument("--projekty", type=Path, required=True)
    p.add_argument("--wspolczynnik", type=float, default=1.22)
    p.add_argument("--wyjscie", type=Path, default=Path("dane/krawedz"))
    p.add_argument("--nazwa", default="linie.json")
    p.add_argument("--pamiec", type=Path, default=None, help="katalog pamieci podrecznej linii na dysku (domyslnie bez)")
    p.add_argument("--procesy", type=int, default=1)
    p.add_argument("--ustawienia", type=Path, default=None)
    p.set_defaults(fun=polecenie_linie)
    a = ap.parse_args(argv)
    a.fun(a)


if __name__ == "__main__":
    main()
