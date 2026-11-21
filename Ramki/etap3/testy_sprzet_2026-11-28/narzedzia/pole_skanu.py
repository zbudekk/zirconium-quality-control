"""pole_skanu.py - liczby o polu skanera z JEDNEGO pliku skanu plytki (narzedzie pomocnicze dnia sprzetu, E3-S1).

Po co: program i okno "Dzien skanera" mowia "skan dobry / nie nada sie", ale nie podaja wprost: jaka jest srednica
pola skanera, ile dolkow numeru widac, czy brzeg plytki jest w skanie i jak gleboko widac scianke boczna (rowek
pokrywki). To narzedzie liczy te cztery rzeczy z pliku STL przywiezionego z laboratorium.

Programu nie zmienia: korzysta z modulow programu tylko przez import (`stanowisko.dzien_skanera_rdzen.rozpoznaj_uklad`,
`stanowisko.porownaj.uklady_z_ustawien`). Sprawdzone WYLACZNIE na skanach sztucznych (test obok: test_pole_skanu.py).

Uzycie - z instalacji programu (jedna linia; sciezki PELNE, bo Polecenie.cmd zmienia katalog biezacy):
    C:\\Stanowisko\\Polecenie.cmd C:\\sciezka\\pole_skanu.py C:\\sciezka\\SKAN.stl [--numer 1] [--wynik KATALOG]
Uzycie - z kopii repo (katalog Ramki\\stanowisko):
    python ..\\etap3\\testy_sprzet_2026-11-28\\narzedzia\\pole_skanu.py SKAN.stl [--ustawienia PLIK]
Wynik: tekst na ekranie + pliki `<skan>_pole.txt`, `<skan>_pole.json`, `<skan>_pole.png` (rzut z gory) obok skanu
albo w katalogu `--wynik`. Kod wyjscia: 0 = plytka rozpoznana i policzona, 3 = plytki nie rozpoznano (liczby zgrubne
sa mimo to podane), 2 = pliku nie da sie wczytac.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))  # katalog programu (instalacja: Polecenie.cmd ustawia go jako biezacy)

# pakiet programu MUSI byc zaimportowany przed numpy / trimesh (E3-A11w: wylacza zapytania WMI modulu platform)
import stanowisko  # noqa: E402, F401, I001

import numpy as np  # noqa: E402

KIERUNKOW = 72               # sektory po 5 stopni wokol srodka plytki
PAS_BRZEGU_MM = 0.6          # punkt wierzchu lezy "przy brzegu", gdy jest blizej obrysu plytki niz tyle
PAS_WIERZCHU_MM = 0.3        # punkt lezy "na wierzchu", gdy |z - grubosc| nie przekracza tyle
MIN_PUNKTOW_SEKTORA = 3
PROBKA = 800_000             # punktow rownomiernie po powierzchni siatki
ROWEK_R58 = (1.5, 2.5, 0.8)  # rowek pokrywki plytki okraglej ramkowej wg projektu R58: od-do ponizej wierzchu, glebokosc [mm]


# ----------------------------------------------------------------------------- geometria pomocnicza
def _kolo_z_2(a, b):
    c = (a + b) / 2.0
    return c, float(np.linalg.norm(a - c))


def _kolo_z_3(a, b, c):
    d = 2.0 * (a[0] * (b[1] - c[1]) + b[0] * (c[1] - a[1]) + c[0] * (a[1] - b[1]))
    if abs(d) < 1e-12:
        return None
    ux = ((a @ a) * (b[1] - c[1]) + (b @ b) * (c[1] - a[1]) + (c @ c) * (a[1] - b[1])) / d
    uy = ((a @ a) * (c[0] - b[0]) + (b @ b) * (a[0] - c[0]) + (c @ c) * (b[0] - a[0])) / d
    s = np.array([ux, uy])
    return s, float(np.linalg.norm(a - s))


def najmniejsze_kolo(xy: np.ndarray) -> tuple[np.ndarray, float]:
    """Najmniejsze kolo zawierajace wszystkie punkty (algorytm przyrostowy na otoczce wypuklej)."""
    from scipy.spatial import ConvexHull

    pts = np.asarray(xy, dtype=np.float64)
    if len(pts) >= 4:
        try:
            pts = pts[ConvexHull(pts).vertices]
        except Exception:  # noqa: BLE001 - punkty wspolliniowe itp.
            pass
    rng = np.random.default_rng(0)
    pts = pts[rng.permutation(len(pts))]
    eps = 1e-9

    def w(c, r, p):
        return np.linalg.norm(p - c) <= r + eps

    c, r = pts[0], 0.0
    for i in range(1, len(pts)):
        if w(c, r, pts[i]):
            continue
        c, r = pts[i], 0.0
        for j in range(i):
            if w(c, r, pts[j]):
                continue
            c, r = _kolo_z_2(pts[i], pts[j])
            for k in range(j):
                if w(c, r, pts[k]):
                    continue
                kolo = _kolo_z_3(pts[i], pts[j], pts[k])
                if kolo is not None:
                    c, r = kolo
    return np.asarray(c), float(r)


def odleglosc_od_obrysu(uk, x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Ile mm punkt lezy WEWNATRZ obrysu plytki (ujemne = poza obrysem). Kwadrat: bok `size`; kolo: srednica `d` ze scieciem."""
    if uk.shape == "round":
        odl = float(uk.d) / 2.0 - np.hypot(x, y)
        if uk.flat and "dist" in uk.flat:
            a = math.radians(float(uk.flat.get("angle_deg", 0.0)))
            odl = np.minimum(odl, float(uk.flat["dist"]) - (x * math.cos(a) + y * math.sin(a)))
        return odl
    return float(uk.size) / 2.0 - np.maximum(np.abs(x), np.abs(y))


def srednica_opisana(uk) -> float:
    return float(uk.d) if uk.shape == "round" else float(uk.size) * math.sqrt(2.0)


def _zakresy(brak: list[int]) -> list[str]:
    """Sektory bez danych -> czytelne zakresy katow, np. '40-95 st.' (0 st. = w prawo, 90 st. = do tylu plytki)."""
    if not brak:
        return []
    krok = 360 // KIERUNKOW
    s = sorted(brak)
    grupy, pocz, pop = [], s[0], s[0]
    for i in s[1:]:
        if i != pop + 1:
            grupy.append((pocz, pop))
            pocz = i
        pop = i
    grupy.append((pocz, pop))
    if len(grupy) > 1 and grupy[0][0] == 0 and grupy[-1][1] == KIERUNKOW - 1:  # zakres przechodzi przez 0 st.
        grupy = [(grupy[-1][0], grupy[0][1] + KIERUNKOW)] + grupy[1:-1]
    return [f"{a * krok}-{((b + 1) * krok) % 360 or 360} st." for a, b in grupy]


# ----------------------------------------------------------------------------- pomiar
def dolki(P: np.ndarray, uk) -> list[dict]:
    wynik = []
    for d in uk.code_dimples:
        m = np.hypot(P[:, 0] - d.x, P[:, 1] - d.y) < d.d / 2.0 - 0.2
        n = int(m.sum())
        wpis = {"bit": d.bit, "x": d.x, "y": d.y, "promien_od_srodka_mm": round(math.hypot(d.x, d.y), 1), "punktow": n}
        if n < 15:
            wpis["stan"] = "poza skanem"
        else:
            gl = float(uk.thickness - np.percentile(P[m, 2], 5))
            wpis["zaglebienie_mm"] = round(gl, 2)
            wpis["stan"] = "widoczny, wglebienie" if gl > 0.4 else "widoczny, plasko"
        wynik.append(wpis)
    return wynik


def zmierz(sciezka: Path, ust: dict, numer: int | None = None, seed: int = 0) -> tuple[dict, np.ndarray | None, object]:
    """Pomiar jednego pliku. Zwraca (wynik, punkty w ukladzie plytki albo None, uklad albo None)."""
    from stanowisko import dzien_skanera_rdzen as R
    from stanowisko import porownaj as PO

    import trimesh

    skan = trimesh.load(str(sciezka), force="mesh", process=False)
    w: dict = {"plik": Path(sciezka).name, "trojkaty": int(len(skan.faces)), "numer_podany": numer,
               "obrys_w_ukladzie_skanera_mm": [round(float(v), 2) for v in (skan.vertices.max(0) - skan.vertices.min(0))]}
    pts, _ = trimesh.sample.sample_surface(skan, PROBKA, seed=seed)
    pts = np.asarray(pts, dtype=np.float64)
    r = R.rozpoznaj_uklad(skan, ust, numer)
    w["rozpoznano"] = r["uklad"] is not None
    if not w["rozpoznano"]:
        # liczby zgrubne bez programu: plaszczyzna z glownych kierunkow chmury, kolo opisane na rzucie
        c = pts.mean(0)
        _, _, vt = np.linalg.svd((pts - c)[:: max(1, len(pts) // 50_000)], full_matrices=False)
        xy = (pts - c) @ vt[:2].T
        _, rk = najmniejsze_kolo(xy)
        w.update({"powod": r["powod"], "komunikat_programu": r["komunikat"], "stozki_znalezione": r["stozki"],
                  "srednica_danych_mm": round(2 * rk, 1), "uwaga": "plytki nie rozpoznano - srednica liczona zgrubnie, bez ukladu plytki"})
        return w, None, None
    wyr, uk = r["wyrownanie"], r["obiekt_ukladu"]
    M = np.asarray(wyr.macierz, dtype=np.float64)
    P = pts @ M[:3, :3].T + M[:3, 3]
    th = float(uk.thickness)
    w.update({"uklad": uk.nazwa, "ksztalt": "okragla" if uk.shape == "round" else "kwadratowa", "rozpoznanie_pewne": bool(r["pewny"]),
              "pasuja_tez": [k for k in r["kandydaci"][1:]],
              "wymiar_plytki_mm": float(uk.d) if uk.shape == "round" else float(uk.size),
              "numer_wg_programu": wyr.numer, "numer_zrodlo": wyr.numer_zrodlo, "numer_z_dolkow": wyr.numer_z_dolkow,
              "bity_wg_programu": list(wyr.bity)})
    # 1. kolo opisane na wszystkich danych skanu (rzut z gory)
    c, rk = najmniejsze_kolo(P[:, :2])
    w["srednica_danych_mm"] = round(2 * rk, 1)
    w["srodek_danych_od_srodka_plytki_mm"] = [round(float(c[0]), 1), round(float(c[1]), 1)]
    opis = srednica_opisana(uk)
    w["srednica_opisana_plytki_mm"] = round(opis, 1)
    w["pole_wieksze_niz_plytka"] = bool(2 * rk >= opis - 1.0)
    # 2. brzeg plytki: punkty wierzchu tuz przy obrysie, w 72 kierunkach
    odl = odleglosc_od_obrysu(uk, P[:, 0], P[:, 1])
    wierzch = np.abs(P[:, 2] - th) <= PAS_WIERZCHU_MM
    kat = (np.degrees(np.arctan2(P[:, 1], P[:, 0])) % 360.0 / (360.0 / KIERUNKOW)).astype(int) % KIERUNKOW
    przy_brzegu = wierzch & (odl >= -0.2) & (odl < PAS_BRZEGU_MM)
    ile = np.bincount(kat[przy_brzegu], minlength=KIERUNKOW)
    brak = [int(i) for i in np.flatnonzero(ile < MIN_PUNKTOW_SEKTORA)]
    w["brzeg_widoczny_kierunkow"] = KIERUNKOW - len(brak)
    w["brzeg_kierunkow_razem"] = KIERUNKOW
    w["brzeg_brak_w_kierunkach"] = _zakresy(brak)
    rr = np.hypot(P[:, 0], P[:, 1])
    zasieg = np.zeros(KIERUNKOW)
    np.maximum.at(zasieg, kat[wierzch], rr[wierzch])
    w["zasieg_wierzchu_od_srodka_mm"] = {"min": round(float(zasieg.min()), 1), "mediana": round(float(np.median(zasieg)), 1),
                                         "max": round(float(zasieg.max()), 1)}
    if brak:
        w["zasieg_tam_gdzie_brak_brzegu_mm"] = {"min": round(float(zasieg[brak].min()), 1), "max": round(float(zasieg[brak].max()), 1)}
    # 3. dolki numeru: uklad rozpoznany i uklad o drugim ksztalcie z tej samej rodziny (kwadrat <-> kolo)
    w["dolki"] = {uk.nazwa: dolki(P, uk)}
    uklady = PO.uklady_z_ustawien(ust)
    druga = uk.nazwa[len("okragla_"):] if uk.nazwa.startswith("okragla_") else "okragla_" + uk.nazwa
    if druga in uklady:
        w["dolki"][druga] = dolki(P, uklady[druga])
    # 4. stozki znacznikow
    j = wyr.jakosc
    w["stozki"] = {"dopasowane": j.get("stozki_dopasowane"), "reszta_mm": round(float(j.get("znaczniki_reszta_mm", float("nan"))), 4),
                   "szum_wierzchu_rms_mm": round(float(j.get("plaszczyzna_rms_mm", float("nan"))), 4),
                   "najdalszy_stozek_od_srodka_mm": round(max(math.hypot(z.x, z.y) + z.d / 2.0 for z in uk.markers), 1)}
    # 5. scianka boczna (ponizej wierzchu, przy obrysie albo poza nim)
    bok = (P[:, 2] < th - 0.8) & (odl < 0.8) & (odl > -1.5)
    ile_b = np.bincount(kat[bok], minlength=KIERUNKOW)
    gleb = float(th - np.percentile(P[bok, 2], 2)) if bok.sum() >= 50 else 0.0
    od, do, gr = ROWEK_R58
    w["scianka_boczna"] = {"kierunkow_z_danymi": int((ile_b >= MIN_PUNKTOW_SEKTORA).sum()), "punktow": int(bok.sum()),
                           "widoczna_do_mm_ponizej_wierzchu": round(gleb, 1),
                           "punktow_w_miejscu_rowka_R58": int(((P[:, 2] <= th - od) & (P[:, 2] >= th - do) & (odl > 0.25) & (odl <= gr + 0.2)).sum())}
    return w, P, uk


# ----------------------------------------------------------------------------- raport
def _l(v: float) -> str:
    return f"{v:.1f}".replace(".", ",")


def raport(w: dict) -> list[str]:
    t = [f"POLE SKANU - plik {w['plik']} ({w['trojkaty']} trojkatow)", ""]
    o = w["obrys_w_ukladzie_skanera_mm"]
    if not w["rozpoznano"]:
        t += ["1. Plytka: NIE ROZPOZNANA przez program.",
              f"   Powod wg programu: {w['powod']}" + (f" (stozkow znaleziono: {w['stozki_znalezione']})" if w.get("stozki_znalezione") is not None else ""),
              f"2. Dane skanu mieszcza sie w kole o srednicy ok. {_l(w['srednica_danych_mm'])} mm (liczone zgrubnie).",
              f"   Obrys pliku: {_l(o[0])} x {_l(o[1])} x {_l(o[2])} mm.",
              "   Jesli ta srednica jest mniejsza niz ok. 94 mm, to pole skanera nie obejmuje trzech stozkow",
              "   znacznikow plytki - program nie rozpozna zadnej plytki. To wazna informacja: zapisz ja w arkuszu.",
              "3. Dolkow, brzegu i scianki nie da sie policzyc bez rozpoznania plytki."]
        return t
    t.append(f"1. Plytka: rozpoznana, uklad {w['uklad']} ({w['ksztalt']} {_l(w['wymiar_plytki_mm'])} mm), "
             + ("pewnie." if w["rozpoznanie_pewne"] else "NIEPEWNIE - pasuje tez: " + ", ".join(w["pasuja_tez"]) + "."))
    nr = w["numer_wg_programu"]
    t.append("   Numer plytki wg programu: " + (f"{nr} (zrodlo: {w['numer_zrodlo']})" if nr is not None else "nie odczytany ze skanu"))
    t.append(f"2. Dane skanu mieszcza sie w kole o srednicy {_l(w['srednica_danych_mm'])} mm "
             f"(srodek kola {_l(math.hypot(*w['srodek_danych_od_srodka_plytki_mm']))} mm od srodka plytki).")
    if w["pole_wieksze_niz_plytka"]:
        t.append(f"   Cala plytka (kolo opisane {_l(w['srednica_opisana_plytki_mm'])} mm) jest w skanie: pole skanera jest CO NAJMNIEJ takie.")
        t.append("   O ile wieksze - z tej plytki nie widac.")
    else:
        t.append(f"   To mniej niz cala plytka (kolo opisane {_l(w['srednica_opisana_plytki_mm'])} mm): POLE SKANERA MA OK. {_l(w['srednica_danych_mm'])} mm.")
    t.append(f"3. Brzeg plytki widac w {w['brzeg_widoczny_kierunkow']} z {w['brzeg_kierunkow_razem']} kierunkow.")
    if w["brzeg_brak_w_kierunkach"]:
        z = w["zasieg_tam_gdzie_brak_brzegu_mm"]
        t.append("   Brzegu NIE widac w kierunkach: " + ", ".join(w["brzeg_brak_w_kierunkach"]) + " (0 st. = prawa strona plytki, 90 st. = tyl).")
        t.append(f"   Tam wierzch plytki konczy sie w skanie {_l(z['min'])}-{_l(z['max'])} mm od srodka plytki.")
    t.append("4. Dolki numeru plytki (4 miejsca: A, B, C, D):")
    for nazwa, lista in w["dolki"].items():
        widac = sum(d["stan"] != "poza skanem" for d in lista)
        opis = "; ".join(f"{d['bit']}: {d['stan']}" + (f" {_l(d['zaglebienie_mm'])} mm" if "zaglebienie_mm" in d and d["stan"].endswith("wglebienie") else "") for d in lista)
        t.append(f"   uklad {nazwa}: w skanie {widac} z {len(lista)} miejsc (leza {_l(min(d['promien_od_srodka_mm'] for d in lista))}-"
                 f"{_l(max(d['promien_od_srodka_mm'] for d in lista))} mm od srodka). {opis}")
    s = w["stozki"]
    t.append(f"5. Stozki znacznikow: dopasowane {s['dopasowane']} z 3 (najdalszy siega {_l(s['najdalszy_stozek_od_srodka_mm'])} mm od srodka); "
             f"szum plaskiego wierzchu {str(round(s['szum_wierzchu_rms_mm'], 3)).replace('.', ',')} mm.")
    b = w["scianka_boczna"]
    od, do, _ = ROWEK_R58
    if b["punktow"] < 50:
        t.append("6. Scianka boczna plytki: NIE widac jej w skanie (skan konczy sie na wierzchu).")
        t.append(f"   Rowek pokrywki plytki okraglej ramkowej ({_l(od)}-{_l(do)} mm ponizej wierzchu) nie jest wiec widoczny.")
    else:
        t.append(f"6. Scianka boczna plytki: dane w {b['kierunkow_z_danymi']} z {KIERUNKOW} kierunkow, do {_l(b['widoczna_do_mm_ponizej_wierzchu'])} mm ponizej wierzchu.")
        t.append(f"   Rowek pokrywki plytki okraglej ramkowej lezy {_l(od)}-{_l(do)} mm ponizej wierzchu: "
                 + ("skan siega tak gleboko" if b["widoczna_do_mm_ponizej_wierzchu"] >= do else "skan NIE siega tak gleboko")
                 + f"; punktow w miejscu rowka: {b['punktow_w_miejscu_rowka_R58']}.")
    return t


def rysunek(P: np.ndarray, uk, w: dict, plik: Path, bok: int = 720, zakres: float = 75.0) -> None:
    """Rzut z gory w ukladzie plytki: szare = dane skanu, niebieski = obrys plytki, zielone / czerwone kolka = dolki."""
    from PIL import Image, ImageDraw

    h, _, _ = np.histogram2d(P[:, 1], P[:, 0], bins=bok, range=[[-zakres, zakres], [-zakres, zakres]])
    tlo = np.where(h[::-1] > 0, 200, 255).astype(np.uint8)
    im = Image.fromarray(np.stack([tlo] * 3, axis=-1), "RGB")
    rys = ImageDraw.Draw(im)

    def px(x, y):
        return ((x + zakres) / (2 * zakres) * bok, (zakres - y) / (2 * zakres) * bok)

    if uk.shape == "round":
        r = float(uk.d) / 2
        rys.ellipse([px(-r, r), px(r, -r)], outline=(0, 70, 200), width=2)
    else:
        s = float(uk.size) / 2
        rys.rectangle([px(-s, s), px(s, -s)], outline=(0, 70, 200), width=2)
    for lista in w["dolki"].values():
        for d in lista:
            kolor = (200, 0, 0) if d["stan"] == "poza skanem" else (0, 150, 0)
            rys.ellipse([px(d["x"] - 1.5, d["y"] + 1.5), px(d["x"] + 1.5, d["y"] - 1.5)], outline=kolor, width=2)
    for z in uk.markers:
        rys.ellipse([px(z.x - 3, z.y + 3), px(z.x + 3, z.y - 3)], outline=(230, 130, 0), width=2)
    rk = w["srednica_danych_mm"] / 2
    cx, cy = w["srodek_danych_od_srodka_plytki_mm"]
    rys.ellipse([px(cx - rk, cy + rk), px(cx + rk, cy - rk)], outline=(120, 0, 160), width=1)
    rys.text((8, 8), f"{w['plik']}: dane w kole {w['srednica_danych_mm']} mm; brzeg {w['brzeg_widoczny_kierunkow']}/{KIERUNKOW}", fill=(0, 0, 0))
    im.save(str(plik))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Pole skanera z jednego pliku skanu plytki: srednica, dolki numeru, brzeg, scianka boczna.")
    ap.add_argument("skan", type=Path, help="plik skanu plytki (STL / PLY / OBJ) - PELNA sciezka")
    ap.add_argument("--numer", type=int, default=None, help="numer wybity na plytce (pomaga rozpoznac kwadrat / kolo)")
    ap.add_argument("--ustawienia", type=Path, default=None, help="plik ustawien programu (domyslnie: ustawienia programu albo wzor)")
    ap.add_argument("--wynik", type=Path, default=None, help="katalog na pliki wyniku (domyslnie obok skanu)")
    ap.add_argument("--bez-rysunku", action="store_true")
    a = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass
    from stanowisko import dzien_skanera_rdzen as R

    if not a.skan.is_file():
        print(f"BLAD: nie ma pliku {a.skan} (podaj pelna sciezke)")
        return 2
    ust, plik_ust, _ = R.wczytaj_ustawienia_bezpiecznie(a.ustawienia)
    if ust is None:
        print("BLAD: nie da sie wczytac ustawien programu (podaj --ustawienia)")
        return 2
    try:
        w, P, uk = zmierz(a.skan, ust, a.numer)
    except Exception as e:  # noqa: BLE001 - plik uszkodzony albo nie jest siatka
        print(f"BLAD: nie da sie policzyc pliku {a.skan.name}: {type(e).__name__}: {e}")
        return 2
    w["plik_ustawien"] = plik_ust.name if plik_ust else None
    katalog = a.wynik if a.wynik is not None else a.skan.parent
    katalog.mkdir(parents=True, exist_ok=True)
    tekst = raport(w)
    (katalog / f"{a.skan.stem}_pole.txt").write_text("\n".join(tekst) + "\n", encoding="ascii", errors="replace", newline="\n")
    (katalog / f"{a.skan.stem}_pole.json").write_text(json.dumps(w, indent=1, ensure_ascii=True) + "\n", encoding="ascii", newline="\n")
    if P is not None and not a.bez_rysunku:
        rysunek(P, uk, w, katalog / f"{a.skan.stem}_pole.png")
    print("\n".join(tekst))
    print(f"\nZapisano: {katalog / (a.skan.stem + '_pole.txt')} (+ .json" + ("" if P is None or a.bez_rysunku else ", .png") + ")")
    return 0 if w["rozpoznano"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
