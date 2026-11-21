"""pole_skanu.py - liczby o polu skanera z JEDNEGO pliku skanu plytki (narzedzie pomocnicze dnia sprzetu, E3-S1 / E3-S2a).

Po co: program i okno "Dzien skanera" mowia "skan dobry / nie nada sie", ale nie podaja wprost: jaka jest srednica
pola skanera, ile dolkow numeru widac, czy brzeg plytki jest w skanie i jak gleboko widac scianke boczna (rowek
pokrywki). To narzedzie liczy te cztery rzeczy z pliku STL przywiezionego z laboratorium.

Programu nie zmienia: korzysta z modulow programu tylko przez import (`stanowisko.dzien_skanera_rdzen.rozpoznaj_uklad`,
`stanowisko.porownaj.uklady_z_ustawien`). Sprawdzone WYLACZNIE na skanach sztucznych (test obok: test_pole_skanu.py).

Uzycie - z instalacji programu (jedna linia; sciezki PELNE, bo Polecenie.cmd zmienia katalog biezacy):
    C:\\Stanowisko\\Polecenie.cmd C:\\sciezka\\pole_skanu.py C:\\sciezka\\SKAN.stl [--numer 1] [--wynik KATALOG]
Uzycie - z kopii repo (katalog Ramki\\stanowisko):
    python ..\\etap3\\testy_sprzet_2026-11-28\\narzedzia\\pole_skanu.py SKAN.stl [--ustawienia PLIK]
Wynik: tekst na ekranie (6 wierszy numerowanych + blok "DO ARKUSZA") + pliki `<skan>_<RRRRMMDD_GGMMSS>_pole.txt`, `.json`,
`.png` (rzut z gory; kolejny wynik tego samego skanu dostaje nowa nazwe - nic sie nie nadpisuje) obok skanu
albo w katalogu `--wynik`. Kod wyjscia: 0 = plytka rozpoznana i policzona, 3 = plytki nie rozpoznano (liczby zgrubne
sa mimo to podane), 2 = pliku nie da sie wczytac.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
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
PROG_USKOKU_MM = 0.4         # U3: kierunek "z uskokiem", gdy scianka w pasie rowka cofa sie o co najmniej tyle
ROZNICA_KOLA_MM = 5.0        # U1 (plytka nierozpoznana): dane "sa kolem", gdy kolo opisane minus najwezszy wymiar < tyle
MIN_KIERUNKOW_POLA = 12      # U1: pole kolowe liczone tylko, gdy dane koncza sie wewnatrz plytki w co najmniej tylu kierunkach
KONIEC_WEWNATRZ_MM = 1.5     # U1: koniec danych wewnatrz plytki = co najmniej tyle od obrysu (tam ucina pole skanera, nie brzeg plytki)
RESZTA_POLA_MM = 1.5         # U1: koniec danych "lezy na okregu pola", gdy jest od niego nie dalej niz tyle
UDZIAL_NA_OKREGU = 0.85      # U1: pole kolowe, gdy co najmniej taka czesc koncow danych lezy na dopasowanym okregu
PODLOZE_OD_MM = 140.0        # U5 (plytka nierozpoznana): dane wieksze niz jakakolwiek plytka (kwadrat 96 mm ma przekatna 135,8)
PODLOZE_ZAPAS_MM = 6.0       # U5 (plytka rozpoznana): dane siegaja poza kolo opisane plytki o wiecej niz tyle


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


def prostokat_najwezszy(xy: np.ndarray) -> tuple[float, float]:
    """Prostokat opisany na punktach o NAJMNIEJSZEJ szerokosci: (najwezej, w poprzek) w mm (otoczka wypukla, kazdy jej bok)."""
    from scipy.spatial import ConvexHull

    pts = np.asarray(xy, dtype=np.float64)
    try:
        pts = pts[ConvexHull(pts).vertices]
    except Exception:  # noqa: BLE001 - punkty wspolliniowe itp.
        pass
    naj = None
    for i in range(len(pts)):
        e = pts[(i + 1) % len(pts)] - pts[i]
        dl = float(np.hypot(*e))
        if dl < 1e-9:
            continue
        u = e / dl
        wzdluz, wpoprz = pts @ u, pts @ np.array([-u[1], u[0]])
        szer = float(wpoprz.max() - wpoprz.min())
        if naj is None or szer < naj[0]:
            naj = (szer, float(wzdluz.max() - wzdluz.min()))
    return naj if naj is not None else (0.0, 0.0)


def okrag_dopasowany(E: np.ndarray) -> tuple[np.ndarray, float, np.ndarray]:
    """Okrag najlepiej pasujacy do punktow (najmniejsze kwadraty): (srodek, promien, odleglosci punktow od okregu)."""
    E = np.asarray(E, dtype=np.float64)
    (cx, cy, c), *_ = np.linalg.lstsq(np.c_[2.0 * E, np.ones(len(E))], (E ** 2).sum(1), rcond=None)
    r = math.sqrt(max(float(c + cx * cx + cy * cy), 0.0))
    return np.array([cx, cy]), r, np.abs(np.hypot(E[:, 0] - cx, E[:, 1] - cy) - r)


def uskok_scianki(odl: np.ndarray, glebokosc: np.ndarray, kat: np.ndarray) -> dict:
    """Miara rowka pokrywki (propozycja recenzenta PR #54, U3): o ile mm scianka boczna COFA SIE do srodka plytki w pasie
    rowka (1,5-2,5 mm ponizej wierzchu) wobec pasa nad rowkiem (0,5-1,5 mm), osobno w kazdym z 72 kierunkow.
    `odl` = ile mm punkt lezy wewnatrz obrysu plytki, `glebokosc` = ile mm ponizej wierzchu, `kat` = numer kierunku.
    Zwraca surowe liczby; wniosku "rowek jest / nie ma" narzedzie NIE wyciaga (miara nie sprawdzona na prawdziwym skanie)."""
    od, do, _ = ROWEK_R58
    przy = (odl > -1.5) & (odl < 1.5)
    nad, wr = przy & (glebokosc >= od - 1.0) & (glebokosc < od), przy & (glebokosc >= od) & (glebokosc <= do)
    uskoki = []
    for i in range(KIERUNKOW):
        a, b = odl[nad & (kat == i)], odl[wr & (kat == i)]
        if len(a) >= MIN_PUNKTOW_SEKTORA and len(b) >= MIN_PUNKTOW_SEKTORA:
            uskoki.append(float(np.median(b) - np.median(a)))
    return {"kierunkow_policzonych": len(uskoki), "kierunkow_z_uskokiem": int(sum(u >= PROG_USKOKU_MM for u in uskoki)),
            "uskok_mediana_mm": round(float(np.median(uskoki)), 2) if uskoki else None}


def opis_rodzaju(nazwa: str) -> str:
    """Nazwa ukladu z programu -> opis dla czlowieka (slowa jak w programie po paczce O3)."""
    rdzen = nazwa[:-4] if nazwa.endswith("_r54") else nazwa
    if rdzen.startswith("okragla_ramkowa_"):
        opis, pora = "okragla ramkowa (do ramki)", rdzen[len("okragla_ramkowa_"):]
    elif rdzen.startswith("okragla_"):
        opis, pora = "okragla testowa (poza ramka)", rdzen[len("okragla_"):]
    else:
        opis, pora = "kwadratowa", rdzen
    return f"{opis}, {pora}" + (", stary rozstaw R54" if nazwa.endswith("_r54") else "")


def drugi_ksztalt(nazwa: str) -> str:
    """Uklad o drugim ksztalcie z tej samej rodziny (kwadrat <-> kolo) - tylko do pliku .json."""
    for p in ("okragla_ramkowa_", "okragla_"):
        if nazwa.startswith(p):
            return nazwa[len(p):]
    return "okragla_" + nazwa


POWODY = {"jedyny_pasujacy": "tylko ten rodzaj pasuje do skanu", "numer_podany": "wg numeru podanego przez czlowieka",
          "numer_z_dolkow": "wg numeru odczytanego z dolkow", "ksztalt": "wg ksztaltu brzegu plytki",
          "dolki_wykluczaja": "dolki wykluczaja inne rodzaje", "domyslny": "DOMYSLNIE - program nie mial czym rozstrzygnac"}


def _rozpoznaj(skan, ust: dict, numer: int | None) -> tuple[dict, str]:
    """Rozpoznanie programu (`dzien_skanera_rdzen.rozpoznaj_uklad`) + powod decyzji z `plate.rozpoznaj_uklad` (podgladany,
    bez zmiany programu i bez drugiego liczenia)."""
    from stanowisko import dzien_skanera_rdzen as R
    from stanowisko import plate as PL

    zlapane: dict = {}
    oryginal = PL.rozpoznaj_uklad

    def podglad(*a, **k):
        wynik = oryginal(*a, **k)
        zlapane.update(wynik[1])
        return wynik

    PL.rozpoznaj_uklad = podglad
    try:
        r = R.rozpoznaj_uklad(skan, ust, numer)
    finally:
        PL.rozpoznaj_uklad = oryginal
    return r, str(zlapane.get("powod") or "")


def zmierz(sciezka: Path, ust: dict, numer: int | None = None, seed: int = 0) -> tuple[dict, np.ndarray | None, object]:
    """Pomiar jednego pliku. Zwraca (wynik, punkty w ukladzie plytki albo None, uklad albo None)."""
    from stanowisko import porownaj as PO

    import trimesh

    skan = trimesh.load(str(sciezka), force="mesh", process=False)
    w: dict = {"plik": Path(sciezka).name, "trojkaty": int(len(skan.faces)), "numer_podany": numer,
               "obrys_w_ukladzie_skanera_mm": [round(float(v), 2) for v in (skan.vertices.max(0) - skan.vertices.min(0))]}
    pts, _ = trimesh.sample.sample_surface(skan, PROBKA, seed=seed)
    pts = np.asarray(pts, dtype=np.float64)
    r, powod_wyboru = _rozpoznaj(skan, ust, numer)
    w["rozpoznano"] = r["uklad"] is not None
    if not w["rozpoznano"]:
        # liczby zgrubne bez programu: plaszczyzna z glownych kierunkow chmury, prostokat i kolo opisane na rzucie
        c = pts.mean(0)
        _, _, vt = np.linalg.svd((pts - c)[:: max(1, len(pts) // 50_000)], full_matrices=False)
        xy = (pts - c) @ vt[:2].T
        _, rk = najmniejsze_kolo(xy)
        najw, wpoprz = prostokat_najwezszy(xy)
        w.update({"powod": r["powod"], "komunikat_programu": r["komunikat"], "stozki_znalezione": r["stozki"],
                  "srednica_danych_mm": round(2 * rk, 1), "dane_najwezej_mm": round(najw, 1), "dane_w_poprzek_mm": round(wpoprz, 1),
                  "dane_sa_kolem": bool(2 * rk - najw < ROZNICA_KOLA_MM), "podloze_prawdopodobne": bool(2 * rk > PODLOZE_OD_MM),
                  "uwaga": "plytki nie rozpoznano - wymiary liczone zgrubnie, bez ukladu plytki"})
        w["do_arkusza"] = do_arkusza(w)
        return w, None, None
    wyr, uk = r["wyrownanie"], r["obiekt_ukladu"]
    M = np.asarray(wyr.macierz, dtype=np.float64)
    P = pts @ M[:3, :3].T + M[:3, 3]
    th = float(uk.thickness)
    w.update({"uklad": uk.nazwa, "rodzaj_plytki": opis_rodzaju(uk.nazwa), "ksztalt": "okragla" if uk.shape == "round" else "kwadratowa",
              "rozpoznanie_pewne": bool(r["pewny"]), "powod_wyboru": powod_wyboru,
              "pasuja_tez": [k for k in r["kandydaci"][1:]],
              "wymiar_plytki_mm": float(uk.d) if uk.shape == "round" else float(uk.size),
              "numer_wg_programu": wyr.numer, "numer_zrodlo": wyr.numer_zrodlo, "numer_z_dolkow": wyr.numer_z_dolkow,
              "bity_wg_programu": list(wyr.bity)})
    # 1. wymiary danych skanu (rzut z gory): kolo opisane, prostokat o najmniejszej szerokosci, okrag wpisany wokol srodka plytki
    c, rk = najmniejsze_kolo(P[:, :2])
    najw, wpoprz = prostokat_najwezszy(P[:, :2])
    w["srednica_danych_mm"] = round(2 * rk, 1)
    w["dane_najwezej_mm"], w["dane_w_poprzek_mm"] = round(najw, 1), round(wpoprz, 1)
    w["srodek_danych_od_srodka_plytki_mm"] = [round(float(c[0]), 1), round(float(c[1]), 1)]
    opis = srednica_opisana(uk)
    w["srednica_opisana_plytki_mm"] = round(opis, 1)
    w["podloze_prawdopodobne"] = bool(2 * rk > opis + PODLOZE_ZAPAS_MM)
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
    w["cala_plytka_w_skanie"] = not brak            # U2: tylko gdy brzeg widac we WSZYSTKICH kierunkach
    w["pole_wieksze_niz_plytka"] = not brak         # nazwa z E3-S1 (zostaje dla zgodnosci plikow .json)
    rr = np.hypot(P[:, 0], P[:, 1])
    zasieg = np.zeros(KIERUNKOW)
    np.maximum.at(zasieg, kat[wierzch], rr[wierzch])
    w["zasieg_wierzchu_od_srodka_mm"] = {"min": round(float(zasieg.min()), 1), "mediana": round(float(np.median(zasieg)), 1),
                                         "max": round(float(zasieg.max()), 1)}
    if brak:
        w["zasieg_tam_gdzie_brak_brzegu_mm"] = {"min": round(float(zasieg[brak].min()), 1), "max": round(float(zasieg[brak].max()), 1)}
    zasieg_danych = np.zeros(KIERUNKOW)
    np.maximum.at(zasieg_danych, kat, rr)
    w["okrag_wpisany_wokol_srodka_plytki_mm"] = round(2.0 * float(zasieg_danych.min()), 1)
    # 2a. U1: "pole skanera ma ok. X mm" tylko gdy konce danych lezace WEWNATRZ plytki (tam skan ucina pole, nie brzeg plytki)
    #     ukladaja sie na jednym okregu; okrag dopasowany do tych koncow, nie kolo opisane na danych
    w["pole_kolowe_mm"], w["pole_stan"] = None, "cala_plytka" if not brak else "za_malo_danych"
    konce = []
    for i in range(KIERUNKOW):
        idx = np.flatnonzero(kat == i)
        if len(idx):
            k = idx[np.argmax(rr[idx])]
            if odl[k] > KONIEC_WEWNATRZ_MM:
                konce.append(P[k, :2])
    if brak and len(konce) >= MIN_KIERUNKOW_POLA:
        konce = np.array(konce)
        sr, rp, reszty = okrag_dopasowany(konce)
        if MIN_KIERUNKOW_POLA <= (reszty <= RESZTA_POLA_MM).sum() < len(konce):  # drugie dopasowanie bez koncow odstajacych
            sr, rp, _ = okrag_dopasowany(konce[reszty <= RESZTA_POLA_MM])
            reszty = np.abs(np.hypot(konce[:, 0] - sr[0], konce[:, 1] - sr[1]) - rp)
        w["pole_dopasowanie"] = {"kierunkow": len(konce), "srednica_mm": round(2 * rp, 1), "na_okregu": int((reszty <= RESZTA_POLA_MM).sum()),
                                 "srodek_od_srodka_plytki_mm": round(float(np.hypot(*sr)), 1)}
        w["pole_stan"] = "nie_kolowe"
        if 60.0 <= 2 * rp <= 250.0 and (reszty <= RESZTA_POLA_MM).mean() >= UDZIAL_NA_OKREGU:
            w["pole_kolowe_mm"], w["pole_stan"] = round(2 * rp, 1), "kolowe"
    # 3. dolki numeru: uklad rozpoznany; uklad o drugim ksztalcie z tej samej rodziny tylko do pliku .json (U12)
    w["dolki"] = {uk.nazwa: dolki(P, uk)}
    uklady = PO.uklady_z_ustawien(ust)
    druga = drugi_ksztalt(uk.nazwa)
    if druga in uklady:
        w["dolki_gdyby_drugi_ksztalt"] = {druga: dolki(P, uklady[druga])}
    # 4. stozki znacznikow
    j = wyr.jakosc
    w["stozki"] = {"dopasowane": j.get("stozki_dopasowane"), "reszta_mm": round(float(j.get("znaczniki_reszta_mm", float("nan"))), 4),
                   "szum_wierzchu_rms_mm": round(float(j.get("plaszczyzna_rms_mm", float("nan"))), 4),
                   "najdalszy_stozek_od_srodka_mm": round(max(math.hypot(z.x, z.y) + z.d / 2.0 for z in uk.markers), 1)}
    # 5. scianka boczna (ponizej wierzchu, przy obrysie albo poza nim) i - tylko plytka okragla ramkowa - miara rowka pokrywki (U3)
    bok = (P[:, 2] < th - 0.8) & (odl < 0.8) & (odl > -1.5)
    ile_b = np.bincount(kat[bok], minlength=KIERUNKOW)
    gleb = float(th - np.percentile(P[bok, 2], 2)) if bok.sum() >= 50 else 0.0
    w["scianka_boczna"] = {"widoczna": bool(bok.sum() >= 50), "kierunkow_z_danymi": int((ile_b >= MIN_PUNKTOW_SEKTORA).sum()),
                           "punktow": int(bok.sum()), "widoczna_do_mm_ponizej_wierzchu": round(gleb, 1)}
    w["rowek_pokrywki"] = {"dotyczy": uk.nazwa.startswith("okragla_ramkowa_")}
    if w["rowek_pokrywki"]["dotyczy"]:
        w["rowek_pokrywki"].update(uskok_scianki(odl, th - P[:, 2], kat))
    w["do_arkusza"] = do_arkusza(w)
    return w, P, uk


# ----------------------------------------------------------------------------- raport
def _l(v: float) -> str:
    return f"{v:.1f}".replace(".", ",")


def _rowek_tekst(w: dict) -> str:
    """Jedno zdanie o rowku pokrywki - surowe liczby, bez wniosku (U3)."""
    rw, b = w["rowek_pokrywki"], w["scianka_boczna"]
    od, do, gr = ROWEK_R58
    if not rw["dotyczy"]:
        return "nie dotyczy (ten rodzaj plytki nie ma rowka pokrywki)"
    if not b["widoczna"] or b["widoczna_do_mm_ponizej_wierzchu"] < do or not rw.get("kierunkow_policzonych"):
        return f"NIE widac - skan nie siega {_l(do)} mm ponizej wierzchu (rowek lezy {_l(od)}-{_l(do)} mm ponizej)"
    return (f"scianka cofa sie o {str(rw['uskok_mediana_mm']).replace('.', ',')} mm (projekt: {_l(gr)} mm); cofniecie co najmniej "
            f"{_l(PROG_USKOKU_MM)} mm w {rw['kierunkow_z_uskokiem']} z {rw['kierunkow_policzonych']} policzonych kierunkow - narzedzie NIE rozstrzyga")


def do_arkusza(w: dict) -> dict:
    """To, co wlasciciel przepisuje do arkusza obserwacji - stale etykiety, jedna wartosc w wierszu."""
    if not w["rozpoznano"]:
        nie = "nie policzono (plytka nierozpoznana)"
        return {"program mowi": f"PLYTKA NIE ROZPOZNANA (powod wg programu: {w['powod']})", "numer z dolkow": nie, "dolki numeru widac": nie,
                "scianka boczna": nie, "rowek pokrywki": nie, "brzeg plytki": nie,
                "pole": f"dane najwezej {_l(w['dane_najwezej_mm'])} mm, w poprzek {_l(w['dane_w_poprzek_mm'])} mm",
                "podloze w skanie": "PRAWDOPODOBNIE TAK (dane wieksze niz plytka)" if w["podloze_prawdopodobne"] else "nie widac"}
    b = w["scianka_boczna"]
    lista = w["dolki"][w["uklad"]]
    pole = f"okrag wpisany {_l(w['okrag_wpisany_wokol_srodka_plytki_mm'])} mm; dane najwezej {_l(w['dane_najwezej_mm'])} mm, w poprzek {_l(w['dane_w_poprzek_mm'])} mm"
    if w["pole_kolowe_mm"] is not None:
        pole += f"; pole kolowe ok. {_l(w['pole_kolowe_mm'])} mm"
    elif w["cala_plytka_w_skanie"]:
        pole += "; cala plytka w skanie"
    else:
        pole += "; pola kolowego nie da sie podac"
    pewnosc = "PEWNIE" if w["rozpoznanie_pewne"] else "NIEPEWNIE (pasuje tez: " + (", ".join(w["pasuja_tez"]) or "-") + ")"
    return {"program mowi": f"{w['rodzaj_plytki']} [{w['uklad']}], {pewnosc}" + (f", powod: {w['powod_wyboru']}" if w["powod_wyboru"] else ""),
            "numer z dolkow": str(w["numer_z_dolkow"]) if w["numer_z_dolkow"] is not None else "nie odczytany",
            "dolki numeru widac": f"{sum(d['stan'] != 'poza skanem' for d in lista)} z {len(lista)}",
            "scianka boczna": (f"widac ({b['kierunkow_z_danymi']} z {KIERUNKOW} kierunkow, do {_l(b['widoczna_do_mm_ponizej_wierzchu'])} mm ponizej wierzchu)"
                               if b["widoczna"] else "NIE widac"),
            "rowek pokrywki": _rowek_tekst(w),
            "brzeg plytki": f"{w['brzeg_widoczny_kierunkow']} z {KIERUNKOW} kierunkow",
            "pole": pole,
            "podloze w skanie": "PRAWDOPODOBNIE TAK (dane siegaja poza plytke)" if w["podloze_prawdopodobne"] else "nie widac"}


def _blok_arkusza(w: dict) -> list[str]:
    return ["", "DO ARKUSZA (przepisz):"] + [f"  {k}: {v}" for k, v in w["do_arkusza"].items()]


PODLOZE_TEKST = ("   UWAGA: w skanie jest prawdopodobnie PODLOZE (stolik / uchwyt wokol plytki). Zrob zdjecie ekranu programu skanera",
                 "   i zapisz to w arkuszu. Program moze nie rozpoznac plytki zeskanowanej razem z podlozem.")


def raport(w: dict) -> list[str]:
    t = [f"POLE SKANU - plik {w['plik']} ({w['trojkaty']} trojkatow)", ""]
    o = w["obrys_w_ukladzie_skanera_mm"]
    if not w["rozpoznano"]:
        t += ["1. Program mowi: PLYTKA NIE ROZPOZNANA.",
              f"   Powod wg programu: {w['powod']}" + (f" (stozkow znacznikow znaleziono: {w['stozki_znalezione']} z 3)" if w.get("stozki_znalezione") is not None else ""),
              f"2. Dane skanu: najwezej {_l(w['dane_najwezej_mm'])} mm, w poprzek {_l(w['dane_w_poprzek_mm'])} mm (liczone zgrubnie, bez rozpoznania plytki)."]
        if w["dane_sa_kolem"]:
            t.append(f"   Dane mieszcza sie w kole o srednicy ok. {_l(w['srednica_danych_mm'])} mm.")
        else:
            t.append(f"   DANE NIE SA KOLEM: {_l(w['dane_najwezej_mm'])} x {_l(w['dane_w_poprzek_mm'])} mm. Do arkusza wpisz OBIE liczby; liczy sie mniejsza.")
        t.append(f"   Obrys pliku: {_l(o[0])} x {_l(o[1])} x {_l(o[2])} mm.")
        if w["podloze_prawdopodobne"]:
            t += [f"   Dane sa wieksze niz jakakolwiek plytka (ponad {PODLOZE_OD_MM:.0f} mm).", *PODLOZE_TEKST]
        t += ["   Jesli najwezszy wymiar jest mniejszy niz ok. 94 mm, to pole skanera nie obejmuje trzech stozkow",
              "   znacznikow plytki - program nie rozpozna zadnej plytki. To wazna informacja: zapisz ja w arkuszu.",
              "3. Dolkow, brzegu i scianki nie da sie policzyc bez rozpoznania plytki."]
        return t + _blok_arkusza(w)
    t.append(f"1. Program mowi: plytka {w['rodzaj_plytki']} - nazwa w programie: {w['uklad']} ({_l(w['wymiar_plytki_mm'])} mm), "
             + ("PEWNIE." if w["rozpoznanie_pewne"] else "NIEPEWNIE - pasuje tez: " + (", ".join(w["pasuja_tez"]) or "-") + "."))
    nr = w["numer_wg_programu"]
    t.append("   Numer plytki wg programu: " + (f"{nr} (zrodlo: {w['numer_zrodlo']})" if nr is not None else "nie odczytany ze skanu")
             + (f". Dlaczego ten rodzaj: {POWODY.get(w['powod_wyboru'], w['powod_wyboru'])} [{w['powod_wyboru']}]." if w["powod_wyboru"] else "."))
    t.append(f"2. Dane skanu: najwezej {_l(w['dane_najwezej_mm'])} mm, w poprzek {_l(w['dane_w_poprzek_mm'])} mm; wokol srodka plytki dane siegaja")
    t.append(f"   wszedzie co najmniej na okrag o srednicy {_l(w['okrag_wpisany_wokol_srodka_plytki_mm'])} mm (tyle pola skaner na pewno ma wokol srodka TEJ plytki).")
    n_brzeg = f"{w['brzeg_widoczny_kierunkow']} z {w['brzeg_kierunkow_razem']}"
    if w["cala_plytka_w_skanie"]:
        t.append(f"   Cala plytka jest w skanie (brzeg widac w {n_brzeg} kierunkow): pole skanera jest CO NAJMNIEJ takie jak plytka.")
        t.append("   O ile wieksze - z tej plytki nie widac.")
    else:
        t.append(f"   Plytka NIE jest cala w skanie: brzeg widac w {n_brzeg} kierunkow.")
        if w["pole_kolowe_mm"] is not None:
            d = w["pole_dopasowanie"]
            t.append(f"   Tam, gdzie brzegu nie widac, dane koncza sie na jednym okregu: POLE SKANERA MA OK. {_l(w['pole_kolowe_mm'])} mm "
                     f"(srodek pola {_l(d['srodek_od_srodka_plytki_mm'])} mm od srodka plytki).")
            if d["srodek_od_srodka_plytki_mm"] > 5.0:
                t.append("   Plytka lezy z boku pola - przesun plytke na srodek pola i zeskanuj ponownie.")
        elif w["pole_stan"] == "za_malo_danych":
            t.append("   Skan konczy sie tuz przy brzegu plytki (albo brzeg jest zasloniety): wielkosci pola z tego skanu nie da sie podac.")
        else:
            t.append(f"   POLE NIE JEST KOLEM (albo plytka lezy z boku pola): dane najwezej {_l(w['dane_najwezej_mm'])} mm x {_l(w['dane_w_poprzek_mm'])} mm.")
            t.append("   Jednej 'srednicy pola' z tego skanu nie ma - wpisz obie liczby; przesun plytke na srodek pola i zeskanuj ponownie.")
    if w["podloze_prawdopodobne"]:
        t += [f"   Dane siegaja poza plytke (kolo opisane na danych {_l(w['srednica_danych_mm'])} mm, na plytce {_l(w['srednica_opisana_plytki_mm'])} mm).", *PODLOZE_TEKST]
    t.append(f"3. Brzeg plytki widac w {n_brzeg} kierunkow.")
    if w["brzeg_brak_w_kierunkach"]:
        z = w["zasieg_tam_gdzie_brak_brzegu_mm"]
        t.append("   Brzegu NIE widac w kierunkach: " + ", ".join(w["brzeg_brak_w_kierunkach"]) + " (0 st. = prawa strona plytki, 90 st. = tyl).")
        t.append(f"   Tam wierzch plytki konczy sie w skanie {_l(z['min'])}-{_l(z['max'])} mm od srodka plytki.")
    lista = w["dolki"][w["uklad"]]
    widac = sum(d["stan"] != "poza skanem" for d in lista)
    opis = "; ".join(f"{d['bit']}: {d['stan']}" + (f" {_l(d['zaglebienie_mm'])} mm" if "zaglebienie_mm" in d and d["stan"].endswith("wglebienie") else "") for d in lista)
    t.append(f"4. Dolki numeru plytki: w skanie widac {widac} z {len(lista)} miejsc (A, B, C, D; leza {_l(min(d['promien_od_srodka_mm'] for d in lista))}-"
             f"{_l(max(d['promien_od_srodka_mm'] for d in lista))} mm od srodka).")
    t.append(f"   {opis}. Numer z dolkow: " + (str(w["numer_z_dolkow"]) if w["numer_z_dolkow"] is not None else "nie odczytany") + ".")
    s = w["stozki"]
    t.append(f"5. Stozki znacznikow: dopasowane {s['dopasowane']} z 3 (najdalszy siega {_l(s['najdalszy_stozek_od_srodka_mm'])} mm od srodka); "
             f"szum plaskiego wierzchu {str(round(s['szum_wierzchu_rms_mm'], 3)).replace('.', ',')} mm.")
    b = w["scianka_boczna"]
    if not b["widoczna"]:
        t.append("6. Scianka boczna plytki: NIE widac jej w skanie (skan konczy sie na wierzchu).")
    else:
        t.append(f"6. Scianka boczna plytki: widac w {b['kierunkow_z_danymi']} z {KIERUNKOW} kierunkow, do {_l(b['widoczna_do_mm_ponizej_wierzchu'])} mm ponizej wierzchu.")
    t.append(f"   Rowek pokrywki: {_rowek_tekst(w)}.")
    if w["rowek_pokrywki"]["dotyczy"] and "NIE rozstrzyga" in _rowek_tekst(w):
        t.append("   (miara rowka nie byla sprawdzona na prawdziwym skanie - przepisz liczby do arkusza i obejrzyj rysunek .png)")
    return t + _blok_arkusza(w)


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


def nazwa_wyniku(katalog: Path, rdzen: str, znacznik: str | None = None) -> str:
    """Poczatek nazwy plikow wyniku: <skan>_<RRRRMMDD_GGMMSS>[_n] - nigdy nie nadpisuje wczesniejszego wyniku (U4)."""
    podstawa = f"{rdzen}_{znacznik or time.strftime('%Y%m%d_%H%M%S')}"
    nr = 1
    while any(katalog.glob((podstawa if nr == 1 else f"{podstawa}_{nr}") + "_pole*")):
        nr += 1
    return podstawa if nr == 1 else f"{podstawa}_{nr}"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Pole skanera z jednego pliku skanu plytki: wymiary danych, dolki numeru, brzeg, scianka boczna.")
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
    katalog = a.wynik if a.wynik is not None else a.skan.parent
    katalog.mkdir(parents=True, exist_ok=True)
    rdzen = nazwa_wyniku(katalog, a.skan.stem)
    try:
        w, P, uk = zmierz(a.skan, ust, a.numer)
    except Exception as e:  # noqa: BLE001 - plik pusty, uciety albo nie jest siatka (U10)
        print(f"BLAD: plik {a.skan.name} jest pusty albo uszkodzony - nie da sie go wczytac jako skanu.")
        print("Zapisz skan w programie skanera jeszcze raz (albo skopiuj plik ponownie) i sprobuj znowu.")
        (katalog / f"{rdzen}_pole_blad.json").write_text(json.dumps({"plik": a.skan.name, "bajtow": a.skan.stat().st_size,
                                                                      "blad": f"{type(e).__name__}: {e}"}, indent=1, ensure_ascii=True) + "\n",
                                                         encoding="ascii", newline="\n")
        return 2
    w["plik_ustawien"] = plik_ust.name if plik_ust else None
    tekst = raport(w)
    (katalog / f"{rdzen}_pole.txt").write_text("\n".join(tekst) + "\n", encoding="ascii", errors="replace", newline="\n")
    (katalog / f"{rdzen}_pole.json").write_text(json.dumps(w, indent=1, ensure_ascii=True) + "\n", encoding="ascii", newline="\n")
    if P is not None and not a.bez_rysunku:
        rysunek(P, uk, w, katalog / f"{rdzen}_pole.png")
    print("\n".join(tekst))
    print(f"\nZapisano: {katalog / (rdzen + '_pole.txt')} (+ .json" + ("" if P is None or a.bez_rysunku else ", .png") + ")")
    return 0 if w["rozpoznano"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
