"""porownaj — skan płytki → które prace leżą w których gniazdach, do których projektów należą i czy są ukruszone.

Pełny łańcuch plate → match → inspect (P3a). Użycie (z katalogu stanowisko/):
    py -3.12 -m stanowisko.porownaj --skan <skan.stl> --projekty <folder> [<folder2> …]
        --plytka wieczorna|poranna|okragla_wieczorna|okragla_poranna [--wspolczynnik 1.22] [--numer N]
        [--wyjscie <folder>] [--prawda <skan.json>] [--bez-filtru] [--bez-inspekcji] [--orientacja auto|brzeg_dol|brzeg_gora]
        [--bez-straznika]

``--plytka`` to nazwa układu z ``[plytki]``: układ gniazd R59 (``wieczorna`` …) albo poprzedni R54 dla starych płytek
fizycznych (``wieczorna_r54``, ``poranna_r54``, ``okragla_wieczorna_r54``, ``okragla_poranna_r54``). Numery płytek są w obu
układach te same, więc układ wybiera człowiek; gdy skan nie pasuje do wybranego układu (strażnik układu w ``plate``),
wynik ma ``uklad_zgodny`` = false, komunikat „płytka nie pasuje do wybranego układu”, nazwy układów, do których pasuje
rozstaw stożków, i ŻADNYCH gniazd (nic nie jest zielone).

Wynik: tabela gniazdo → id projektu → zęby → pokrycie → pewność → status match → status inspect → ubytki
(stdout, bez nazw plików), ``<wyjscie>/<skan>_wynik.json`` (macierz wyrównania, numer, fragmenty, kandydaci,
inspekcja każdego gniazda: ubytki z położeniem, rozmiarem i metodą, plamy, wcięcia, drgnięcie; metryki) i
``<wyjscie>/<skan>_mapa.png`` (mapa płytki). Statusy gniazd: zielone = rozpoznane bez ubytku, czerwone =
ubytek, żółte = niepewne / popraw ułożenie / skan ponownie / sprawdź, szare = bez projektu, pomarańczowe =
poprawka ręczna; fiolet = podwójne, czerwone kółko = praca poza gniazdem. Z ``--prawda`` (JSON generatora)
liczy metryki: wyrównanie, numer, gniazda, top‑1 / top‑2, błąd pozy, a dla inspect wykryte / fałszywe
ubytki per metoda i scenariusz (dobrze / bokiem / częściowo / drgnięcie).

Sztuczne skany z ``synth`` są wyłącznie danymi do budowy i pomiaru kodu, bo skanera jeszcze nie ma;
właściwy test skanera odbędzie się na prawdziwych płytkach i pracach w sesji P3.
"""
from __future__ import annotations

import argparse
import json
import math
import time
import warnings
from dataclasses import asdict
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image, ImageDraw

from . import inspect as I
from . import match as M
from . import plate as PL
from . import synth as S
from . import uklad as U
from . import ustawienia as UST

KOLORY = {"zielony": (60, 180, 75), "zolty": (240, 200, 40), "szary": (170, 170, 170), "czerwony": (220, 50, 50), "pomaranczowy": (245, 140, 30),
          "pusty": (235, 235, 235), "podwojny": (170, 80, 200), "poza": (160, 0, 0)}
STATUSY_GNIAZDA = ("zielony", "czerwony", "zolty", "szary", "pomaranczowy")
INSPECT_NA_STATUS = {"ok": "zielony", "ubytek": "czerwony", "sprawdz": "zolty", "sprawdz_ulozenie": "zolty", "popraw_ulozenie": "zolty",
                     "skan_ponownie": "zolty", "poprawka": "pomaranczowy", "pominieto": None}
OPISY_STATUSU = {"zielony": "OK", "czerwony": "UBYTEK", "zolty": "sprawdź", "szary": "bez projektu", "pomaranczowy": "poprawka"}


def wspolczynnik_domyslny(plytka: str, ust: dict) -> float:
    if S.poranna(plytka):
        return S.WSPOLCZYNNIK_PORANNA[0]
    return (ust["synth"]["wspolczynnik_min"] + ust["synth"]["wspolczynnik_max"]) / 2


def ustawienia_bez_filtru(ust: dict) -> dict:
    return {**ust, "match": {**ust["match"], "filtr_wymiar_mm": 1e9, "filtr_objetosc_udzial": 1e9}}


def status_gniazda(status_match: str, inspekcja: dict | None) -> str:
    """Kolor gniazda z match + inspect: szary (bez projektu) → match; inaczej status inspect (ok → zielony itd.)."""
    if status_match == "szary" or not inspekcja:
        return status_match
    return INSPECT_NA_STATUS.get(inspekcja["status"]) or status_match


def uklady_pasujace(stozki: list, ust: dict, wybrany: str) -> list[str]:
    """Inne układy z ``[plytki]``, do których pasuje rozstaw stożków znalezionych w skanie (podpowiedź przy niezgodności)."""
    pasuja = []
    for nazwa in ust["plytki"]:
        if nazwa == wybrany:
            continue
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                uk = U.wczytaj(nazwa, UST.katalog_plytki(ust, nazwa))
        except (OSError, ValueError):
            continue
        if PL.stozki_pasuja(stozki, uk):
            pasuja.append(nazwa)
    return pasuja


PODPOWIEDZ_BRAK_R54 = ("w [plytki] lokalnego ustawienia.toml nie ma układów …_r54 (stare płytki fizyczne sprzed R59) — "
                       "dopisz 4 wiersze *_r54 z ustawienia.przyklad.toml i porównaj ponownie z układem …_r54")


def brak_ukladow_poprzednich(ust: dict) -> bool:
    """Czy w ``[plytki]`` nie ma żadnego układu z przyrostkiem wersji (``*_r54``) — lokalny ``ustawienia.toml`` sprzed R59."""
    return not any(U.typ_plytki(nazwa) != nazwa for nazwa in ust["plytki"])


def dopasuj_fragmenty(wyr: PL.WynikWyrownania, pula: M.Pula, ust: dict, bez_filtru: bool = False, inspekcja: bool = True,
                      podglad: dict | None = None) -> list[dict]:
    """match (+ inspect) dla każdego fragmentu (bez drobnych); wpisy JSON z 5 najlepszymi kandydatami.

    ``podglad`` (dict) dostaje ``WynikInspekcji`` każdego gniazda (punkty i odchyłki do podglądu 3D w oknie).
    """
    ust_m = ustawienia_bez_filtru(ust) if bez_filtru else ust
    gniazda = []
    for f in wyr.fragmenty:
        if f.status == "drobny":
            continue
        r = M.dopasuj(f.punkty, f.normalne, pula, ust_m, f.gniazdo)
        wpis = {
            "gniazdo": f.gniazdo, "status_fragmentu": f.status, "punkty": f.liczba, "srodek": [round(v, 3) for v in f.srodek],
            "status": r.status, "pewnosc": round(r.pewnosc, 4), "czas_s": r.czas_s, "uwagi": r.uwagi,
            "kandydaci": [{**asdict(k), "pokrycie": round(k.pokrycie, 4), "rms_mm": (round(k.rms_mm, 4) if math.isfinite(k.rms_mm) else None),
                           "pokrycie_odwrotne": round(k.pokrycie_odwrotne, 4)} for k in r.kandydaci[:5]],
            "inspekcja": None,
        }
        k = r.najlepszy
        if inspekcja and r.status != "szary" and k is not None and k.transformacja is not None:
            wi = I.sprawdz(f.punkty, f.normalne, pula.projekty[k.id], np.array(k.transformacja), k.pokrycie, ust, f.gniazdo)
            wpis["inspekcja"] = wi.json()
            if podglad is not None:
                podglad[f.gniazdo] = wi
        wpis["status_gniazda"] = status_gniazda(r.status, wpis["inspekcja"])
        gniazda.append(wpis)
    return gniazda


def porownaj(skan: Path, foldery: list[Path], plytka: str, ust: dict, wspolczynnik: float | None = None, numer: int | None = None,
             orientacja: str = "auto", bez_filtru: bool = False, pula: M.Pula | None = None, inspekcja: bool = True,
             podglad: dict | None = None, postep=None, straznik: bool = True) -> dict:
    """Cały łańcuch na jednym skanie. ``postep(etap: str, udzial: float)`` — wywołanie zwrotne dla okna.

    Skan, który nie pasuje do układu ``plytka`` (``plate.NiezgodnyUklad``), daje wynik z ``uklad_zgodny`` = False,
    ``uklad_komunikat``, ``uklady_pasujace`` i pustą listą gniazd (match i inspect nie są liczone) oraz ostrzeżenie.
    Gdy żaden inny układ nie pasuje, a w ``[plytki]`` nie ma układów ``*_r54`` (stary ``ustawienia.toml``), komunikat
    i pole ``uklad_podpowiedz`` mówią, że trzeba dopisać 4 wiersze ``*_r54`` z ``ustawienia.przyklad.toml``.
    """
    t0 = time.time()

    def krok(etap: str, udzial: float) -> None:
        if postep is not None:
            postep(etap, udzial)

    uk = U.wczytaj(plytka, UST.katalog_plytki(ust, plytka))
    w = wspolczynnik if wspolczynnik is not None else wspolczynnik_domyslny(plytka, ust)
    if pula is None:
        krok("pula projektów", 0.05)
        pula = M.Pula(foldery, w, orientacja)
    if len(pula) == 0:
        raise SystemExit(f"brak projektów STL w {', '.join(map(str, foldery))}")
    krok("wczytanie skanu", 0.2)
    m = trimesh.load(skan, force="mesh")
    t1 = time.time()
    krok("wyrównanie płytki (plate)", 0.35)
    try:
        wyr = PL.wyrownaj(m, uk, numer=numer, straznik=straznik)
    except PL.NiezgodnyUklad as e:
        t2 = time.time()
        pasujace = uklady_pasujace(e.stozki, ust, plytka)
        podpowiedz = PODPOWIEDZ_BRAK_R54 if not pasujace and brak_ukladow_poprzednich(ust) else ""
        komunikat = str(e) + (f"; rozstaw stożków w skanie pasuje do układu: {', '.join(pasujace)}" if pasujace
                              else "; rozstaw stożków w skanie nie pasuje do żadnego innego układu z [plytki]")
        komunikat += f"; {podpowiedz}" if podpowiedz else ""
        warnings.warn(komunikat, stacklevel=2)
        krok("wynik", 0.95)
        return {
            "skan": Path(skan).name, "plytka": plytka, "uklad_zgodny": False, "uklad_komunikat": komunikat, "uklady_pasujace": pasujace,
            "uklad_podpowiedz": podpowiedz,
            "wspolczynnik": w, "projekty": len(pula), "foldery_projektow": [str(f) for f in foldery],
            "numer": None, "numer_zrodlo": "nieznany", "bity": [], "numer_z_dolkow": None,
            "macierz_skan_do_plytki": e.macierz.tolist() if e.macierz is not None else None, "jakosc_wyrownania": e.jakosc,
            "gniazda": [], "gniazda_puste": [], "gniazda_podwojne": [], "poza_gniazdem": 0, "fragmenty_drobne": 0,
            "czas_s": {"wczytanie": round(t1 - t0, 2), "plate": round(t2 - t1, 2), "match": 0.0, "razem": round(t2 - t0, 2), "pula": pula.czas_s, "inspect": 0.0},
            "bez_filtru": bez_filtru, "inspekcja": inspekcja, "statusy_gniazd": {s: 0 for s in STATUSY_GNIAZDA}, "ubytki": 0,
        }
    t2 = time.time()
    krok("identyfikacja i inspekcja gniazd (match + inspect)", 0.55)
    gniazda = dopasuj_fragmenty(wyr, pula, ust, bez_filtru, inspekcja, podglad)
    t3 = time.time()
    krok("wynik", 0.95)
    wynik = {
        "skan": Path(skan).name, "plytka": plytka, "uklad_zgodny": wyr.jakosc.get("uklad_zgodny"),  # None = strażnik wyłączony
        "wspolczynnik": w, "projekty": len(pula), "foldery_projektow": [str(f) for f in foldery],
        "numer": wyr.numer, "numer_zrodlo": wyr.numer_zrodlo, "bity": wyr.bity, "numer_z_dolkow": wyr.numer_z_dolkow,
        "macierz_skan_do_plytki": wyr.macierz.tolist(), "jakosc_wyrownania": wyr.jakosc,
        "gniazda": gniazda, "gniazda_puste": wyr.gniazda_puste, "gniazda_podwojne": wyr.gniazda_podwojne,
        "poza_gniazdem": sum(1 for f in wyr.fragmenty if f.status == "poza_gniazdem"), "fragmenty_drobne": sum(1 for f in wyr.fragmenty if f.status == "drobny"),
        "czas_s": {"wczytanie": round(t1 - t0, 2), "plate": round(t2 - t1, 2), "match": round(t3 - t2, 2), "razem": round(t3 - t0, 2), "pula": pula.czas_s,
                   "inspect": round(sum(g["inspekcja"]["czas_s"] for g in gniazda if g["inspekcja"]), 2)},
        "bez_filtru": bez_filtru, "inspekcja": inspekcja,
        "statusy_gniazd": {s: sum(1 for g in gniazda if g["status_gniazda"] == s) for s in STATUSY_GNIAZDA},
        "ubytki": sum(len(g["inspekcja"]["ubytki"]) for g in gniazda if g["inspekcja"]),
    }
    return wynik


# ----------------------------------------------------------------------------
# metryki na prawdzie
# ----------------------------------------------------------------------------
def metryki(wynik: dict, prawda: S.PrawdaPlytki, pula: M.Pula) -> dict:
    praw = {p.gniazdo: p for p in prawda.prace}
    bl = PL.blad_wyrownania(np.array(wynik["macierz_skan_do_plytki"]), prawda.poza_skanu)
    frag = [g for g in wynik["gniazda"] if g["status_fragmentu"] in ("praca", "podwojny")]
    w_swoim = sum(1 for g in frag if g["gniazdo"] in praw)
    top1 = top2 = 0
    pozy = []
    bledy_pozy = []
    for g in frag:
        if g["gniazdo"] not in praw:
            continue
        ids = [k["id"] for k in g["kandydaci"]]
        poz = ids.index(praw[g["gniazdo"]].projekt) + 1 if praw[g["gniazdo"]].projekt in ids else None
        pozy.append(poz)
        top1 += poz == 1
        top2 += poz is not None and poz <= 2
        if poz == 1 and g["kandydaci"][0]["transformacja"] is not None and praw[g["gniazdo"]].projekt in pula.projekty:
            bledy_pozy.append(M.blad_pozy(np.array(g["kandydaci"][0]["transformacja"]), np.array(praw[g["gniazdo"]].transformacja), pula.projekty[praw[g["gniazdo"]].projekt].siatka))
    return {
        "wyrownanie": bl,
        "wyrownanie_ok": bl["max_przesuniecie_mm"] < 0.05,
        "numer_prawda": prawda.numer, "numer_odczytany": wynik["numer"], "numer_zrodlo": wynik["numer_zrodlo"],
        "numer_ok": wynik["numer"] == prawda.numer, "numer_z_dolkow_ok": wynik["numer_z_dolkow"] == prawda.numer, "dolki_widoczne": all(b is not None for b in wynik["bity"]),
        "prac_prawda": len(praw), "fragmentow": len(frag), "fragment_w_swoim_gniezdzie": w_swoim,
        "puste_ok": set(wynik["gniazda_puste"]) == set(prawda.gniazda_puste), "podwojne": wynik["gniazda_podwojne"], "poza_gniazdem": wynik["poza_gniazdem"],
        "top1": top1, "top2": top2, "pozycje_prawdy": pozy,
        "statusy": {s: sum(1 for g in frag if g["status"] == s) for s in M.STATUSY},
        "drgniecia": sum(1 for p in prawda.prace if p.drgniecie),
        "blad_pozy_max_mm": max((b["przesuniecie_mm"] for b in bledy_pozy), default=None),
        "blad_pozy_max_deg": max((b["obrot_deg"] for b in bledy_pozy), default=None),
    }


def scenariusz(p: S.PracaNaPlytce) -> str:
    """dobrze | bokiem | czesciowo | drgniecie — do metryk inspect per scenariusz (drgnięcie ma pierwszeństwo)."""
    if p.drgniecie:
        return "drgniecie"
    if p.ulozenie != "dobrze":
        return "bokiem"
    if p.pokrycie < 1.0:
        return "czesciowo"
    return "dobrze"


SCENARIUSZE = ("dobrze", "bokiem", "czesciowo", "drgniecie")


def metryki_inspekcji(wynik: dict, prawda: S.PrawdaPlytki) -> dict:
    """Wykryte / fałszywe ubytki per metoda (A, B, A+B, czerwone, dowolne) i per scenariusz pracy; drgnięcie; poprawki.

    Praca liczy się, gdy fragment leży w swoim gnieździe, top‑1 trafny i inspekcja była liczona.
    Ubytki liczone tylko na pracach bez drgnięcia (drgnięcie = „skan ponownie”, ubytki nieliczone z definicji).
    """
    praw = {p.gniazdo: p for p in prawda.prace}
    puste = lambda: {"prac": 0, "prac_calych": 0, "ubytkow": 0, "wykryte": {k: 0 for k in ("A", "B", "A+B", "czerwony", "dowolny")},  # noqa: E731
                     "prace_cale_z_alarmem": 0, "prace_cale_z_czerwonym": 0, "falszywe_ubytki": 0, "falszywe_czerwone": 0, "falszywe_metoda": {"A": 0, "B": 0, "A+B": 0},
                     "statusy": {s: 0 for s in I.STATUSY}, "statusy_gniazd": {s: 0 for s in STATUSY_GNIAZDA}, "top1_bledny": 0, "bez_inspekcji": 0}
    sc = {s: puste() for s in SCENARIUSZE}
    drg = {"prac": 0, "wykryte": 0, "falszywe": 0}
    pop = {"prac": 0, "wykryte": 0, "falszywe": 0}
    for g in wynik["gniazda"]:
        if g["gniazdo"] not in praw or g["status_fragmentu"] not in ("praca", "podwojny"):
            continue
        p = praw[g["gniazdo"]]
        s = sc[scenariusz(p)]
        s["prac"] += 1
        s["statusy_gniazd"][g["status_gniazda"]] += 1
        ins = g["inspekcja"]
        if not g["kandydaci"] or g["kandydaci"][0]["id"] != p.projekt:
            s["top1_bledny"] += 1
            continue
        if ins is None:
            s["bez_inspekcji"] += 1
            continue
        s["statusy"][ins["status"]] += 1
        if p.drgniecie:
            drg["prac"] += 1
            drg["wykryte"] += ins["status"] == "skan_ponownie"
            continue
        drg["falszywe"] += ins["status"] == "skan_ponownie"
        if p.poprawki:
            pop["prac"] += 1
            pop["wykryte"] += ins["status"] == "poprawka" or any(pl["rodzaj"] == "poprawka" for pl in ins["plamy"])
        else:
            pop["falszywe"] += ins["status"] == "poprawka"
        dp = I.dopasuj_do_prawdy(p.ubytki, ins["ubytki"])  # fałszywe liczone wobec wszystkich ubytków, trafienia tylko wykrywalnych
        wykr = [u.wykrywalny for u in p.ubytki]
        s["ubytkow"] += sum(wykr)
        for k in s["wykryte"]:
            s["wykryte"][k] += sum(t for t, w in zip(dp["trafione"][k], wykr) if w)
        for m in s["falszywe_metoda"]:
            s["falszywe_metoda"][m] += dp["falszywe_metoda"][m]
        if not p.ubytki:
            s["prac_calych"] += 1
            s["prace_cale_z_alarmem"] += ins["status"] in ("ubytek", "sprawdz")
            s["prace_cale_z_czerwonym"] += ins["status"] == "ubytek"
        s["falszywe_ubytki"] += dp["falszywe"]
        s["falszywe_czerwone"] += dp["falszywe_czerwone"]
    razem = puste()
    for s in sc.values():
        for k, v in s.items():
            if isinstance(v, dict):
                for kk in v:
                    razem[k][kk] += v[kk]
            else:
                razem[k] += v
    return {"scenariusze": sc, "razem": razem, "drgniecie": drg, "poprawki": pop}


# ----------------------------------------------------------------------------
# tabela i mapa
# ----------------------------------------------------------------------------
def tabela(wynik: dict) -> str:
    if wynik.get("uklad_zgodny") is False:
        return (f"skan {wynik['skan']}: PŁYTKA NIE PASUJE DO WYBRANEGO UKŁADU „{wynik['plytka']}” — gniazd nie oceniano "
                f"(układy o pasującym rozstawie stożków: {', '.join(wynik['uklady_pasujace']) or 'brak'})"
                + (f" — {wynik['uklad_podpowiedz']}" if wynik.get("uklad_podpowiedz") else ""))
    w = [f"skan {wynik['skan']}: płytka {wynik['plytka']} nr {wynik['numer']} ({wynik['numer_zrodlo']}), współczynnik {wynik['wspolczynnik']}, "
         f"projektów w puli {wynik['projekty']}, czas {wynik['czas_s']['razem']} s (plate {wynik['czas_s']['plate']}, match {wynik['czas_s']['match']})",
         "gniazdo  projekt           zęby          pokrycie  pewność  match    gniazdo       inspect           ubytki (metoda, ø mm)"]
    for g in sorted(wynik["gniazda"], key=lambda g: (g["gniazdo"] is None, g["gniazdo"] or 0)):
        k = g["kandydaci"][0] if g["kandydaci"] else None
        gn = "poza" if g["gniazdo"] is None else f"{g['gniazdo']:>4d}" + ("×2" if g["status_fragmentu"] == "podwojny" else "  ")
        ins = g.get("inspekcja")
        ub = ", ".join(f"{u['metoda']} {u['kolor'][0]} ø{u['srednica_mm']:.2f}" for u in ins["ubytki"]) if ins else ""
        w.append(f"{gn:>7s}  {k['id'] if k else '—':16s}  {'-'.join(k['zeby']) if k else '':13s} {k['pokrycie'] if k else 0:8.3f}  {g['pewnosc']:7.3f}  {g['status']:8s} "
                 f"{g['status_gniazda']:13s} {ins['status'] if ins else '—':17s} {ub}")
    w.append(f"puste: {wynik['gniazda_puste']}; podwójne: {wynik['gniazda_podwojne']}; poza gniazdem: {wynik['poza_gniazdem']}; "
             f"gniazda: {', '.join(f'{s} {n}' for s, n in wynik['statusy_gniazd'].items() if n)}; ubytków {wynik['ubytki']}")
    return "\n".join(w)


def mapa_png(wynik: dict, uk: U.UkladPlytki, plik: Path, px: float = 0.1) -> Path:
    r = (uk.size if uk.shape == "square" else uk.d) / 2 + 4
    n = int(2 * r / px)
    im = Image.new("RGB", (n, n), (255, 255, 255))
    d = ImageDraw.Draw(im)

    def P(x, y):
        return ((x + r) / px, (r - y) / px)

    if uk.shape == "round":
        d.ellipse([P(-uk.d / 2, uk.d / 2), P(uk.d / 2, -uk.d / 2)], outline=(0, 0, 0), width=2)
    else:
        d.rectangle([P(-uk.size / 2, uk.size / 2), P(uk.size / 2, -uk.size / 2)], outline=(0, 0, 0), width=2)
    stan = {g["gniazdo"]: g for g in wynik["gniazda"] if g["gniazdo"] is not None}
    for g in uk.sockets:
        if g.id in wynik["gniazda_podwojne"]:
            kolor = KOLORY["podwojny"]
        elif g.id in stan:
            kolor = KOLORY[stan[g.id].get("status_gniazda", stan[g.id]["status"])]
        else:
            kolor = KOLORY["pusty"]
        d.polygon([P(x, y) for x, y in g.obrys(72)], fill=kolor, outline=(60, 60, 60))
        k = stan[g.id]["kandydaci"][0] if g.id in stan and stan[g.id]["kandydaci"] else None
        ins = stan[g.id].get("inspekcja") if g.id in stan else None
        podpis = f"{g.id}" + (f"\n{'-'.join(k['zeby']) or k['id'][:6]}\n{k['pokrycie']:.2f}" if k else "") + (f"\n{ins['status']}" if ins and ins["status"] != "ok" else "")
        d.multiline_text(P(g.x, g.y + (2.0 if k else 0.8)), podpis, fill=(0, 0, 0), align="center", anchor="ma")
        if ins:
            for u in ins["ubytki"]:
                rr = max(0.6, u["srednica_mm"] / 2)
                d.ellipse([P(u["x"] - rr, u["y"] + rr), P(u["x"] + rr, u["y"] - rr)], outline=(0, 0, 0) if u["kolor"] == "czerwony" else (90, 90, 90), width=2)
    for z in uk.markers:
        d.ellipse([P(z.x - z.d / 2, z.y + z.d / 2), P(z.x + z.d / 2, z.y - z.d / 2)], outline=(0, 0, 200), width=2)
    for dm in uk.code_dimples:
        d.ellipse([P(dm.x - dm.d / 2, dm.y + dm.d / 2), P(dm.x + dm.d / 2, dm.y - dm.d / 2)], outline=(0, 0, 200), width=1)
    for g in wynik["gniazda"]:
        if g["gniazdo"] is None:
            x, y, _ = g["srodek"]
            d.ellipse([P(x - 3, y + 3), P(x + 3, y - 3)], outline=KOLORY["poza"], width=3)
    d.text(P(-r + 2, r - 2), f"{wynik['skan']}  {wynik['plytka']} nr {wynik['numer']}  zielone = OK, czerwone = ubytek, zolte = sprawdz, szare = bez projektu, "
           "pomaranczowe = poprawka; fiolet = podwojne; ciemnoczerwone kolko = poza gniazdem; male kolka = ubytki", fill=(0, 0, 0))  # domyślna czcionka PIL bez polskich znaków
    if wynik.get("uklad_zgodny") is False:  # strażnik układu: przekreślona mapa wybranego układu, żadnych kolorów gniazd
        pol = (uk.size if uk.shape == "square" else uk.d) / 2
        for a, b in (((-pol, -pol), (pol, pol)), ((-pol, pol), (pol, -pol))):
            d.line([P(*a), P(*b)], fill=KOLORY["czerwony"], width=6)
        d.text(P(-r + 2, r - 6), f"PLYTKA NIE PASUJE DO WYBRANEGO UKLADU {wynik['plytka']} - gniazd nie oceniano; rozstaw stozkow pasuje do: "
               f"{', '.join(wynik.get('uklady_pasujace', [])) or 'zadnego innego ukladu'}"
               + ("; w ustawienia.toml brak ukladow _r54 - dopisz 4 wiersze z ustawienia.przyklad.toml" if wynik.get("uklad_podpowiedz") else ""), fill=KOLORY["czerwony"])
    im.save(plik)
    return plik


def main(argv: list[str] | None = None) -> dict:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--skan", type=Path, required=True)
    ap.add_argument("--projekty", type=Path, nargs="+", required=True, help="folder(y) z STL projektów (podfoldery zleceń)")
    ap.add_argument("--plytka", required=True)
    ap.add_argument("--wspolczynnik", type=float, default=None, help="skurcz (domyślnie: poranna 1,0; wieczorna środek [synth])")
    ap.add_argument("--numer", type=int, default=None, help="numer płytki, gdy dołki kodu są poza skanem")
    ap.add_argument("--wyjscie", type=Path, default=None, help="folder na JSON i PNG (domyślnie obok skanu)")
    ap.add_argument("--prawda", type=Path, default=None, help="JSON prawdy generatora: policz metryki")
    ap.add_argument("--orientacja", choices=S.ORIENTACJE, default="auto")
    ap.add_argument("--bez-filtru", action="store_true", help="dopasuj wszystkie projekty (bez filtru wymiarów)")
    ap.add_argument("--bez-inspekcji", action="store_true", help="tylko plate + match (bez ubytków)")
    ap.add_argument("--bez-straznika", action="store_true", help="wyłącz sprawdzenie, czy gniazda skanu leżą jak w wybranym układzie (rozstaw stożków jest sprawdzany zawsze)")
    ap.add_argument("--ustawienia", type=Path, default=None)
    ap.add_argument("--bez-png", action="store_true")
    a = ap.parse_args(argv)
    ust = UST.wczytaj_ustawienia(a.ustawienia)
    if a.plytka not in ust["plytki"]:
        ap.error(f"--plytka {a.plytka!r}: brak w [plytki] (są: {', '.join(ust['plytki'])})")
    if not a.skan.exists():
        ap.error(f"brak pliku skanu {a.skan}")
    for f in a.projekty:
        if not f.is_dir():
            ap.error(f"brak folderu projektów {f}")
    uk = U.wczytaj(a.plytka, UST.katalog_plytki(ust, a.plytka))
    w = a.wspolczynnik if a.wspolczynnik is not None else wspolczynnik_domyslny(a.plytka, ust)
    pula = M.Pula(a.projekty, w, a.orientacja)
    with warnings.catch_warnings(record=True) as ostrz:
        warnings.simplefilter("always")
        wynik = porownaj(a.skan, a.projekty, a.plytka, ust, w, a.numer, a.orientacja, a.bez_filtru, pula, inspekcja=not a.bez_inspekcji,
                         straznik=not a.bez_straznika)
    wynik["ostrzezenia"] = [str(o.message) for o in ostrz]
    niezgodny = wynik.get("uklad_zgodny") is False  # metryk na prawdzie nie ma: skan nie jest wyrównany do tego układu
    if a.prawda is not None and not niezgodny:
        prawda = S.wczytaj_prawde(a.prawda)
        wynik["metryki"] = metryki(wynik, prawda, pula)
        if not a.bez_inspekcji:
            wynik["metryki_inspekcji"] = metryki_inspekcji(wynik, prawda)
    wyj = a.wyjscie if a.wyjscie is not None else a.skan.parent
    wyj.mkdir(parents=True, exist_ok=True)
    p_json = wyj / f"{a.skan.stem}_wynik.json"
    p_json.write_text(json.dumps(wynik, ensure_ascii=False, indent=1), encoding="utf-8")
    print(tabela(wynik))
    for o in wynik["ostrzezenia"]:
        print("UWAGA:", o)
    if a.prawda is not None and not niezgodny:
        mt = wynik["metryki"]
        print(f"metryki: wyrównanie max {mt['wyrownanie']['max_przesuniecie_mm']:.4f} mm ({'OK' if mt['wyrownanie_ok'] else 'ZA DUŻO'}), numer {mt['numer_odczytany']} vs {mt['numer_prawda']} "
              f"({'OK' if mt['numer_ok'] else 'ŹLE'}, {mt['numer_zrodlo']}), fragmenty w swoim gnieździe {mt['fragment_w_swoim_gniezdzie']}/{mt['prac_prawda']}, puste {'OK' if mt['puste_ok'] else 'ŹLE'}, "
              f"top‑1 {mt['top1']}/{mt['prac_prawda']}, top‑2 {mt['top2']}/{mt['prac_prawda']}")
        if "metryki_inspekcji" in wynik:
            mi = wynik["metryki_inspekcji"]
            r = mi["razem"]
            print(f"inspect: ubytki wykrywalne {r['ubytkow']}: A {r['wykryte']['A']}, B {r['wykryte']['B']}, A+B {r['wykryte']['A+B']}, czerwone {r['wykryte']['czerwony']}, "
                  f"dowolne {r['wykryte']['dowolny']}; prace całe {r['prac_calych']}: z alarmem {r['prace_cale_z_alarmem']}, z czerwonym {r['prace_cale_z_czerwonym']}; "
                  f"drgnięcie {mi['drgniecie']['wykryte']}/{mi['drgniecie']['prac']} (fałszywe {mi['drgniecie']['falszywe']}); "
                  + "; ".join(f"{s}: prac {v['prac']}, ubytków {v['ubytkow']}, dowolne {v['wykryte']['dowolny']}, czerwone na całych {v['prace_cale_z_czerwonym']}" for s, v in mi["scenariusze"].items() if v["prac"]))
    if not a.bez_png:
        print(mapa_png(wynik, uk, wyj / f"{a.skan.stem}_mapa.png"))
    print(p_json)
    return wynik


if __name__ == "__main__":
    main()
