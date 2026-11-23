"""S1 - proba sciezek do zielonego w inspect / porownaj (analiza kodu 23.11.2026).

Tylko czytanie kodu programu: skrypt niczego w Ramki/stanowisko nie zmienia. Jeden proces python, bez plate / match
(inspekcja wprost na brylach testowych z testy/test_inspect.py: filar_zaokraglony, pudelko bez wneki).

Uruchomienie (z katalogu Ramki\\stanowisko worktree):
    <PC-katalog>\\koordynator\\narz\\py.cmd ..\\analiza_kodu_2026-11-23\\S1\\proba_inspect.py
"""
from __future__ import annotations

import math
import sys
import tempfile
import time
import warnings
from pathlib import Path

ST = Path.cwd()
for p in (ST, ST / "testy", ST / "narzedzia"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import stanowisko  # noqa: E402, F401  (przed trimesh - jak w conftest)

import numpy as np  # noqa: E402
import trimesh  # noqa: E402

from stanowisko import inspect as I, porownaj as PO, synth, ustawienia as UST  # noqa: E402
from test_inspect import _projekt, _skan, _ust, filar_zaokraglony  # noqa: E402

warnings.simplefilter("ignore")
T0 = time.time()
ust = UST.wczytaj_ustawienia(ST / "ustawienia.przyklad.toml")  # w worktree nie ma ustawienia.toml (plik lokalny, poza repo) - wartosci z przykladu
ui = ust["inspect"]
print("ustawienia [inspect]:", {k: ui[k] for k in ("pas_brzegu_od", "pas_brzegu_mm", "prog_glebokosci_mm", "srednica_min_mm", "srednica_max_mm",
                                                   "krawedz_pas_mm", "min_punktow_plamy", "wciecie_min_mm", "wciecie_pewne_mm", "linia_min_udzial",
                                                   "brzeg_min_sprawdzony", "brzeg_max_przerwa_mm", "poprawka_min_mm")})
print("[match] prog_akceptacji_pokrycie:", ust["match"]["prog_akceptacji_pokrycie"])


def opis(wi) -> str:
    pl = [(p.rodzaj, p.srednica_mm, p.glebokosc_mm, p.odleglosc_od_brzegu_mm, p.punkty, p.ostra_krawedz, p.pierscien_mediana_mm) for p in wi.plamy]
    wc = [(v.rodzaj, v.szerokosc_mm, v.wciecie_mm) for v in wi.wciecia]
    ub = [(u.metoda, u.kolor, u.srednica_mm) for u in wi.ubytki]
    b = wi.brzeg or {}
    fb = [(f["nr"], f["sprawdzony"], f["udzial_z_danymi"], f["najdl_przerwa_mm"]) for f in b.get("filary", [])]
    return (f"status={wi.status:15s} gniazdo={PO.status_gniazda('zielony', wi.json())!s:8s} ubytki={ub} plamy(rodzaj,sr,gl,odl,pkt,ostra,med_pier)={pl} "
            f"wciecia={wc} brzeg.sprawdzony={b.get('sprawdzony')} filary(nr,spr,dane,przerwa)={fb} linia.udzial_ciagly={wi.linia_brzegu.get('udzial_ciagly')} "
            f"uwagi={len(wi.uwagi)}")


tmp = Path(tempfile.mkdtemp(prefix="s1_proba_", dir=str(Path(__file__).resolve().parent)))

# ---------------------------------------------------------------------------------------------------------------
print("\n=== A. porownaj.status_gniazda: co daje zielone bez inspekcji 'ok' ===")
for sm, ins in (("zielony", None), ("zielony", {"status": "pominieto"}), ("zielony", {"status": "nowy_status_z_przyszlosci"}),
                ("zolty", {"status": "ok"}), ("zolty", None), ("szary", {"status": "ok"}), ("zielony", {"status": "nie_sprawdzono"})):
    print(f"  status_match={sm:8s} inspekcja={ins!s:42s} -> status_gniazda={PO.status_gniazda(sm, ins)}")

# ---------------------------------------------------------------------------------------------------------------
pr = _projekt(tmp, "filar", [filar_zaokraglony()])
brzeg = I.brzeg_projektu(pr)
f0 = brzeg.linie.filary[0]
print(f"\nprojekt 'filar' (korona-atrapa z wneka, brzeg zaokraglony): filarow {len(brzeg.linie.filary)}, stan linii {brzeg.linie.stan}, werdykt {f0.werdykt}, "
      f"dlugosc linii O {f0.dlugosc:.2f} mm, promien linii O ~{float(np.linalg.norm(f0.linie['O'].X[:, :2], axis=1).mean()):.2f} mm  [{time.time() - T0:.1f} s]")
P0, N0 = _skan(pr.siatka)
wi = I.sprawdz(P0, N0, pr, pr.T0, 0.99, ust, 1)
print("  praca cala, skan pelny:", opis(wi))

print("\n=== B. klasa T2(e): ubytek kulisty na scianie zewnetrznej, srodek s mm ponizej wierzchu (ro=3,0; kula r=0,46 -> fi 0,92; glebokosc 0,7 r = 0,32) ===")
r = 0.46
for s in (1.00, 1.30, 1.45, 1.55, 1.70, 2.00):
    p = np.array([3.0, 0.0, -s])
    n = np.array([1.0, 0.0, 0.0])
    wyn = synth._wytnij_kule(pr.siatka, synth.Material(pr.siatka), p + (1 - synth.GLEBOKOSC_UBYTKU) * r * n, r, 0.05)
    if wyn is None:
        print(f"  s={s:.2f}: kula nie siega materialu")
        continue
    P, N = _skan(wyn[0])
    odl_linii = float(brzeg.drzewo.query(p)[0])
    wi = I.sprawdz(P, N, pr, pr.T0, 0.99, ust, 1)
    print(f"  s={s:.2f} mm (srodek ubytku {odl_linii:.3f} mm od linii O/I; brzeg kuli siega {max(0.0, odl_linii - r):.2f} mm od linii): {opis(wi)}")

print("\n=== C. ubytek na plaskiej krawedzi brzegu: powierzchnia przelomu W skanie / BRAK jej w skanie (dziura w siatce) ===")
for r in (0.25, 0.40, 0.55, 0.70):
    p = np.array([2.5, 0.0, 0.0])
    n = np.array([0.0, 0.0, 1.0])
    c = p + (1 - synth.GLEBOKOSC_UBYTKU) * r * n
    wyn = synth._wytnij_kule(pr.siatka, synth.Material(pr.siatka), c, r, 0.05)
    if wyn is None:
        print(f"  r={r}: kula nie siega materialu")
        continue
    P, N = _skan(wyn[0])
    wi = I.sprawdz(P, N, pr, pr.T0, 0.99, ust, 1)
    print(f"  fi {2 * r:.2f} mm, przelom w skanie      : {opis(wi)}")
    dziura = np.linalg.norm(P - c, axis=1) < r * 1.03  # punkty nowej powierzchni (sfera) i nic wiecej
    wi = I.sprawdz(P[~dziura], N[~dziura], pr, pr.T0, 0.99, ust, 1)
    print(f"  fi {2 * r:.2f} mm, przelomu BRAK ({int(dziura.sum())} pkt mniej): {opis(wi)}")

print("\n=== D. zaglebienie o lagodnym zboczu na brzegu (model: skaner wygladza krawedz ubytku): g*(1-(rho/R)^2)^2 ===")
for g, R in ((0.12, 0.5), (0.19, 0.5), (0.19, 0.9), (0.30, 0.5), (0.30, 0.9)):
    P = P0.copy()
    rho = np.linalg.norm(P - np.array([2.5, 0.0, 0.0]), axis=1)
    w = rho < R
    P[w] = P[w] - N0[w] * (g * (1 - (rho[w] / R) ** 2) ** 2)[:, None]
    wi = I.sprawdz(P, N0, pr, pr.T0, 0.99, ust, 1)
    print(f"  glebokosc {g:.2f} mm, promien {R:.1f} mm (fi {2 * R:.1f}): {opis(wi)}")

print("\n=== F. dziura w danych skanu na brzegu (luk o dlugosci L wzdluz linii, pas 2,5 mm od linii): kiedy 'nie sprawdzono' ===")
kat = np.arctan2(P0[:, 1], P0[:, 0])
blisko = brzeg.drzewo.query(P0)[0] < 2.5
rO = float(np.linalg.norm(f0.linie["O"].X[:, :2], axis=1).mean())
for L in (1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.5):
    dziura = (np.abs(kat) < L / rO / 2) & blisko
    wi = I.sprawdz(P0[~dziura], N0[~dziura], pr, pr.T0, 0.99, ust, 1)
    print(f"  L={L:.1f} mm bez danych: {opis(wi)}")

print("\n=== G. pokrycie = NaN / 0.85 / 0.849 przekazane do inspekcji (praca cala) ===")
for pok in (float("nan"), 0.85, 0.849):
    wi = I.sprawdz(P0, N0, pr, pr.T0, pok, ust, 1)
    print(f"  pokrycie={pok}: status={wi.status}")

# ---------------------------------------------------------------------------------------------------------------
print("\n=== E. projekt BEZ linii brzegu (bryla bez wneki 8x6x5; tryb domyslny) i brak danych skanu przy brzegu ===")
pr2 = _projekt(tmp, "bez_wneki", [trimesh.creation.box([8.0, 6.0, 5.0])])
b2 = I.brzeg_projektu(pr2)
print(f"  linie: filarow {len(b2.linie.filary)}, stan {b2.linie.stan}  [{time.time() - T0:.1f} s]")
Pb, Nb = _skan(pr2.siatka, seed=4)
for nazwa, maska in (("skan pelny", np.zeros(len(Pb), dtype=bool)),
                     ("bez gornych 2 mm po stronie x>0 (pol brzegu bez danych)", (Pb[:, 2] > -2.0) & (Pb[:, 0] > 0)),
                     ("bez gornych 2 mm w calosci (brzegu nie ma w skanie)", Pb[:, 2] > -2.0)):
    for tryb in ("linia_i_plaszczyzna", "linia"):
        wi = I.sprawdz(Pb[~maska], Nb[~maska], pr2, pr2.T0, 0.99, _ust(ust, pas_brzegu_od=tryb), 1)
        print(f"  {nazwa:58s} tryb={tryb:20s}: {opis(wi)}  uwagi={wi.uwagi}")

print(f"\nczas calkowity {time.time() - T0:.1f} s")
