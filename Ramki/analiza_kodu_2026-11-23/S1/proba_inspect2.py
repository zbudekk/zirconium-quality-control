"""S1 - proba 2: gestosc skanu, odwrocona orientacja projektu, pelny lancuch na plytce okraglej R54 nr 8.

Tylko czytanie kodu programu (nic w Ramki/stanowisko nie jest zmieniane). Jeden proces python.
Uruchomienie (z katalogu Ramki\\stanowisko worktree):
    <PC-katalog>\\koordynator\\narz\\py.cmd ..\\analiza_kodu_2026-11-23\\S1\\proba_inspect2.py
"""
from __future__ import annotations

import shutil
import sys
import tempfile
import time
import warnings
from pathlib import Path

ST = Path.cwd()
for p in (ST, ST / "testy", ST / "narzedzia"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import stanowisko  # noqa: E402, F401

import numpy as np  # noqa: E402

import atrapy_koron  # noqa: E402
from stanowisko import inspect as I, match, plate, porownaj as PO, synth, uklad as U, ustawienia as UST  # noqa: E402
from test_inspect import _projekt, _skan, filar_zaokraglony  # noqa: E402

warnings.simplefilter("ignore")
T0 = time.time()
ust = UST.wczytaj_ustawienia(ST / "ustawienia.przyklad.toml")
tmp = Path(tempfile.mkdtemp(prefix="s1_proba2_", dir=str(Path(__file__).resolve().parent)))


def opis(wi) -> str:
    pl = [(p.rodzaj, p.srednica_mm, p.glebokosc_mm, p.odleglosc_od_brzegu_mm, p.punkty, p.pierscien_punkty) for p in wi.plamy]
    wc = [(v.rodzaj, v.szerokosc_mm, v.wciecie_mm) for v in wi.wciecia]
    b = wi.brzeg or {}
    return (f"status={wi.status:15s} gniazdo={PO.status_gniazda('zielony', wi.json())!s:8s} ubytki={[(u.metoda, u.kolor) for u in wi.ubytki]} "
            f"plamy(rodzaj,sr,gl,odl,pkt,pkt_pierscienia)={pl} wciecia={wc} brzeg.sprawdzony={b.get('sprawdzony')} stan_linii={b.get('stan_linii')}")


try:
    pr = _projekt(tmp, "filar", [filar_zaokraglony()])
    I.brzeg_projektu(pr)

    print("=== H. gestosc punktow skanu (odstep) a ubytek na krawedzi brzegu, przelom W skanie ===")
    for r in (0.25, 0.40, 0.55, 0.70):
        c = np.array([2.5, 0.0, 0.0]) + (1 - synth.GLEBOKOSC_UBYTKU) * r * np.array([0.0, 0.0, 1.0])
        po = synth._wytnij_kule(pr.siatka, synth.Material(pr.siatka), c, r, 0.05)[0]
        for odstep in (0.05, 0.10, 0.15, 0.20, 0.25):
            P, N = _skan(po, odstep=odstep)
            wi = I.sprawdz(P, N, pr, pr.T0, 0.99, ust, 1)
            print(f"  ubytek fi {2 * r:.2f} gl {0.7 * r:.2f} mm, odstep punktow skanu {odstep:.2f} mm ({len(P)} pkt): {opis(wi)}")

    print("\n=== I. projekt w puli odwrocony (orientacja zle rozpoznana): ubytek fi 1,1 mm na krawedzi brzegu ===")
    r = 0.55
    c = np.array([2.5, 0.0, 0.0]) + (1 - synth.GLEBOKOSC_UBYTKU) * r * np.array([0.0, 0.0, 1.0])
    po = synth._wytnij_kule(pr.siatka, synth.Material(pr.siatka), c, r, 0.05)[0]
    P, N = _skan(po)
    wi = I.sprawdz(P, N, pr, pr.T0, 0.99, ust, 1)
    print(f"  projekt brzegiem do gory (dobrze): {opis(wi)}")
    pr_odwr = match.Projekt(tmp / "filar.stl", 1.0, "brzeg_dol")  # ten sam plik, wymuszony obrot 180 st. = bledna orientacja
    M = pr_odwr.T0 @ np.linalg.inv(pr.T0)
    P2, N2 = P @ M[:3, :3].T + M[:3, 3], N @ M[:3, :3].T
    b = I.brzeg_projektu(pr_odwr)
    wi = I.sprawdz(P2, N2, pr_odwr, pr_odwr.T0, 0.99, ust, 1)
    print(f"  projekt odwrocony (linie: filarow {len(b.linie.filary)}, stan {b.linie.stan}): {opis(wi)}")
    print(f"    uwagi: {wi.uwagi}")
    print(f"  heurystyka orientacji dla tej bryly (plik nie-exocad): {synth.brzeg_z_heurystyki(synth.wczytaj_projekt(tmp / 'filar.stl'))}  [{time.time() - T0:.1f} s]")

    print("\n=== J. pelny lancuch synth -> plate -> match -> inspect, plytka okragla testowa R54 nr 8; ubytki stawiane w pasie 2,2 mm (inspect: 1,5) ===")
    d = tmp / "stl"
    d.mkdir()
    rng0 = np.random.default_rng(3)
    korony = []
    for i, t in enumerate(["siekacz", "przedtrzonowy", "trzonowy"]):
        W, L, H, g, amp = atrapy_koron.TYPY[t]
        pk = d / f"2026-11-02_p{i}-{['11', '14', '36'][i]}-crown_cad.stl"
        atrapy_koron.korona(W, L, H, g, amp, n_theta=96, n_u=120, rng=rng0).export(pk)
        korony.append(pk)
    pula = match.Pula([d], 1.22)
    uk = U.wczytaj("okragla_wieczorna_r54")
    licz = {"prac": 0, "zielone": 0, "zielone_ubytek_za_pasem": 0, "zielone_ubytek_w_pasie": 0}
    for seed in (41, 42, 43):
        if time.time() - T0 > 110:
            print("  (przerwane: limit czasu proby)")
            break
        op = synth.Opcje.z_toml(ust, plytka=uk.nazwa, prace_na_plytce=3, wspolczynnik=(1.22, 1.22), ubytki_na_prace=(1, 1), p_drgniecia=0.0,
                                srednica_ubytku=(0.6, 1.4), pas_brzegu=2.2)
        skan, prawda = synth.generuj_plytke(uk, 8, korony, np.random.default_rng(seed), op, seed)
        wyr, info = plate.rozpoznaj_uklad(skan, list(PO.uklady_z_ustawien(ust).values()))
        print(f"  seed {seed}: uklad rozpoznany {info['wybrany']} (pewny {info['pewny']}, powod {info['powod']}), numer {wyr.numer} ({wyr.numer_zrodlo})  [{time.time() - T0:.1f} s]")
        praw = {p.gniazdo: p for p in prawda.prace}
        for g in PO.dopasuj_fragmenty(wyr, pula, ust):
            p = praw.get(g["gniazdo"])
            if p is None or not g["inspekcja"]:
                print(f"    gniazdo {g['gniazdo']}: bez prawdy albo bez inspekcji (status {g['status']})")
                continue
            u = p.ubytki[0]
            ins = g["inspekcja"]
            licz["prac"] += 1
            ziel = g["status_gniazda"] == "zielony"
            licz["zielone"] += ziel
            za = u.odleglosc_od_linii is not None and u.odleglosc_od_linii > 1.5
            licz["zielone_ubytek_za_pasem"] += ziel and za
            licz["zielone_ubytek_w_pasie"] += ziel and not za
            print(f"    gniazdo {g['gniazdo']:2d}: prawda ubytek fi {u.srednica:.2f} gl {u.glebokosc:.2f} mm, {u.odleglosc_od_linii} mm od linii, polozenie {u.polozenie}, "
                  f"wykrywalny={u.wykrywalny} -> match {g['status']}, inspect {ins['status']}, GNIAZDO {g['status_gniazda']}; "
                  f"plamy {[(pl['rodzaj'], pl['srednica_mm'], pl['odleglosc_od_brzegu_mm']) for pl in ins['plamy']]}")
    print(f"  razem: {licz}")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
print(f"\nczas calkowity {time.time() - T0:.1f} s")
