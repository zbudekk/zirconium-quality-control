"""porownaj — skan płytki → które prace leżą w których gniazdach, do których projektów należą i czy są ukruszone.

Pełny łańcuch plate → match → inspect (P3a). Użycie (z katalogu stanowisko/):
    py -3.12 -m stanowisko.porownaj --skan <skan.stl> --projekty <folder> [<folder2> …]
        [--plytka auto|wieczorna|poranna|okragla_wieczorna|okragla_poranna|…_r54] [--wspolczynnik 1.22] [--numer N]
        [--wyjscie <folder>] [--prawda <skan.json>] [--bez-filtru] [--bez-inspekcji] [--orientacja auto|brzeg_dol|brzeg_gora]
        [--bez-straznika]
    py -3.12 -m stanowisko.porownaj --skan <skan.stl> --wpisy <wpisy.csv> [--pamiec-puli <katalog>] [opcje jak wyzej]

``--wpisy`` (E3-A5): pula per praca zamiast folderu - plik CSV ``plik;wspolczynnik[;krazek;frezowanie_id;projekt_id]``
(kazdy STL w skali swojego krazka; ten sam STL z dwoma wspolczynnikami = dwa wpisy, wynik wskazuje wpis: pola kandydata
``frezowanie_id``, ``krazek``, ``wspolczynnik``, ``wpisy``); w wyniku ``wspolczynnik`` = null i ``pula_wpisy`` (liczniki
puli i pamieci podrecznej). Pamiec podreczna projektow: ``--pamiec-puli`` albo ``[sciezki] pula_cache``/``projekty``.

``--plytka`` to ``auto`` (domyślnie) albo nazwa układu z ``[plytki]``: układ gniazd R59 (``wieczorna`` …) albo poprzedni R54
dla starych płytek fizycznych (``wieczorna_r54``, ``poranna_r54``, ``okragla_wieczorna_r54``, ``okragla_poranna_r54``).
``auto``: program sam rozpoznaje układ ze skanu (``plate.rozpoznaj_uklad``: rozstaw stożków znaczników → wieczorna / poranna
i R59 / R54; numer płytki albo kształt brzegu → kwadrat / koło), podaje go w wyniku (``plytka``, ``uklad_auto``) i bierze
współczynnik domyślny dla rozpoznanego typu. Układ podany ręcznie: gdy skan do niego nie pasuje (strażnik układu w ``plate``),
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

Błąd (wyjątek) w inspekcji jednego gniazda nie kładzie całej płytki: to gniazdo jest żółte („nie sprawdzono”, uwaga
„błąd inspekcji: …” w JSON, wiersz w tabeli i ostrzeżenie), pozostałe gniazda są policzone, a wynik zapisany.

Sztuczne skany z ``synth`` są wyłącznie danymi do budowy i pomiaru kodu, bo skanera jeszcze nie ma;
właściwy test skanera odbędzie się na prawdziwych płytkach i pracach w sesji P3.
"""
from __future__ import annotations

import argparse
import json
import math
import time
import traceback
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
                     "skan_ponownie": "zolty", "poprawka": "pomaranczowy", "nie_sprawdzono": "zolty", "pominieto": None}
OPISY_STATUSU = {"zielony": "OK", "czerwony": "UBYTEK", "zolty": "sprawdź", "szary": "bez projektu", "pomaranczowy": "poprawka"}
# podpis gniazda wg statusu inspect (P2: „nie sprawdzono” = żółte gniazdo z własnym opisem, nigdy zielone ani czerwone)
OPISY_INSPEKCJI = {"ok": "OK", "ubytek": "UBYTEK", "sprawdz": "sprawdź", "sprawdz_ulozenie": "sprawdź ułożenie", "popraw_ulozenie": "popraw ułożenie",
                   "skan_ponownie": "skan ponownie", "poprawka": "poprawka", "nie_sprawdzono": "nie sprawdzono", "pominieto": "pominięto"}
KLASY_POLOZENIA = ("krawedz", "sciana", "nieznane")  # metryki inspect osobno dla ubytków na krawędzi brzegu i na ścianie (P4)


def gniazda_nie_sprawdzone(wynik: dict) -> list:
    """Numery gniazd ze statusem inspect ``nie_sprawdzono`` (brzegu któregoś filaru nie dało się sprawdzić albo inspekcja
    gniazda zakończyła się błędem — wtedy wpis ma pole ``blad``)."""
    return [g["gniazdo"] for g in wynik.get("gniazda", []) if (g.get("inspekcja") or {}).get("status") == "nie_sprawdzono"]


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


STATUS_BLEDU_INSPEKCJI = "nie_sprawdzono"  # wyjątek w inspekcji gniazda: pracy nie sprawdzono — gniazdo żółte, nigdy zielone ani czerwone
UWAGA_BLEDU_INSPEKCJI = "błąd inspekcji"  # początek uwagi w takim wpisie
DLUGOSC_TRESCI_BLEDU = 300  # treść wyjątku w wyniku przycięta do tylu znaków


def inspekcja_z_bledem(gniazdo: int | None, projekt: str, pokrycie: float, blad: Exception) -> dict:
    """Wpis ``inspekcja`` gniazda, dla którego ``inspect.sprawdz`` zakończył się wyjątkiem (P7, recenzja PR #13).

    Te same pola co zwykły wynik inspekcji (``WynikInspekcji.json()``: puste listy ubytków / plam / wcięć, ``brzeg`` = {}),
    status ``nie_sprawdzono`` (gniazdo żółte z opisem „nie sprawdzono” — pracy nie sprawdzono, więc nigdy zielone), uwaga
    „błąd inspekcji: <typ>: <treść> (<plik>:<linia> <funkcja>)” i dodatkowe pole ``blad`` z tym samym opisem (tylko w takim wpisie).
    """
    opis = f"{type(blad).__name__}: {' '.join(str(blad).split())[:DLUGOSC_TRESCI_BLEDU]}"
    slad = traceback.extract_tb(blad.__traceback__)
    if slad:  # miejsce wyjątku: sama nazwa pliku (bez ścieżki konta), linia i funkcja
        opis += f" ({Path(slad[-1].filename).name}:{slad[-1].lineno} {slad[-1].name})"
    wi = I.WynikInspekcji(gniazdo, projekt, STATUS_BLEDU_INSPEKCJI, float(pokrycie), uwagi=[f"{UWAGA_BLEDU_INSPEKCJI}: {opis}"])
    return {**wi.json(), "blad": opis}


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


AUTO = "auto"  # wartość ``plytka``: układ rozpoznaje program (plate.rozpoznaj_uklad)


def uklady_z_ustawien(ust: dict) -> dict[str, U.UkladPlytki]:
    """Wszystkie układy z ``[plytki]``, które da się wczytać (w kolejności z ustawień) — kandydaci automatycznego rozpoznania."""
    uklady = {}
    for nazwa in ust["plytki"]:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                uklady[nazwa] = U.wczytaj(nazwa, UST.katalog_plytki(ust, nazwa))
        except (OSError, ValueError):
            continue
    return uklady


def opis_ukladu(nazwa: str, uk: U.UkladPlytki | None = None) -> str:
    """Opis układu dla człowieka: „[cytat usuniety]”."""
    typ = U.typ_plytki(nazwa)
    wersja = nazwa[len(typ):].lstrip("_").upper()
    ksztalt = "okrągła" if (uk.shape == "round" if uk is not None else typ.startswith("okragla")) else "kwadratowa"
    return (f"płytka {'poranna' if typ.endswith('poranna') else 'wieczorna'}, {ksztalt}, "
            + (f"stary układ gniazd ({wersja})" if wersja else "nowy układ gniazd (R59)"))


def dopasuj_fragmenty(wyr: PL.WynikWyrownania, pula: M.Pula, ust: dict, bez_filtru: bool = False, inspekcja: bool = True,
                      podglad: dict | None = None, start: float | None = None, statystyka: dict | None = None) -> list[dict]:
    """match (+ inspect) dla każdego fragmentu (bez drobnych); wpisy JSON z 5 najlepszymi kandydatami.

    ``podglad`` (dict) dostaje ``WynikInspekcji`` każdego gniazda (punkty i odchyłki do podglądu 3D w oknie).

    Wyjątek w inspekcji jednego gniazda (P7, recenzja PR #13) nie przerywa płytki: gniazdo dostaje wpis ``inspekcja_z_bledem``
    (status ``nie_sprawdzono`` = żółte, uwaga „błąd inspekcji: …”, pole ``blad``; bez wpisu w ``podglad``), idzie ostrzeżenie,
    a pozostałe gniazda są liczone dalej. ``KeyboardInterrupt``, ``SystemExit`` i ``MemoryError`` nie są łapane.

    Korekta skali ze skanu (``match``): wpis gniazda ma pole ``skala`` — ``poprawka_proc`` (o ile % praca jest większa
    niż projekt × współczynnik puli; None = nie wyznaczono), ``ostrzezenie`` (ponad ``[match] korekta_skali_ostrzezenie_proc``,
    także poza oknem), ``niepewna`` (skan nie pasuje do projektu także w tej skali — bez ostrzeżenia), ``zastosowana``,
    ``powod`` (dlaczego nie), ``wspolczynnik_puli``, ``wspolczynnik_ze_skanu``, pokrycie przed / po.
    Na płytce porannej (prace spieczone, współczynnik 1,0) poprawka jest tylko mierzona.
    Po zastosowanej korekcie transformacja kandydata jest podobieństwem i inspekcja liczy odchyłki w skali skorygowanej.

    Pula per praca (E3-A5, runda 3): najpierw zwykle dopasowanie WSZYSTKICH fragmentow, potem ratunek fragmentow
    nierozpoznanych albo niepewnych (``match.ratuj_plytke``: ranking niezalezny od obrotu pracy, budzet czasu od ``start`` -
    poczatku analizy plytki), na koncu inspekcja; ``statystyka`` (dict) dostaje liczby ratunku. Pula z folderu - jak dotad.
    """
    ust_m = ustawienia_bez_filtru(ust) if bez_filtru else ust
    bez_korekty = "płytka poranna: prace spieczone (współczynnik 1,0) — poprawka skali tylko mierzona" if S.poranna(wyr.plytka) else ""
    gniazda = []
    fragmenty = [f for f in wyr.fragmenty if f.status != "drobny"]
    wyniki = None
    if getattr(pula, "per_praca", False):
        start = time.time() if start is None else start
        wyniki = [M.dopasuj(f.punkty, f.normalne, pula, ust_m, f.gniazdo, bez_korekty=bez_korekty) for f in fragmenty]
        st = M.ratuj_plytke([f.punkty for f in fragmenty], wyniki, pula, ust_m, start)
        if statystyka is not None:
            statystyka.update(st)
    for nr, f in enumerate(fragmenty):
        r = wyniki[nr] if wyniki is not None else M.dopasuj(f.punkty, f.normalne, pula, ust_m, f.gniazdo, bez_korekty=bez_korekty)
        wpis = {
            "gniazdo": f.gniazdo, "status_fragmentu": f.status, "punkty": f.liczba, "srodek": [round(v, 3) for v in f.srodek],
            "status": r.status, "pewnosc": round(r.pewnosc, 4), "czas_s": r.czas_s, "uwagi": r.uwagi,
            "kandydaci": [{**asdict(k), "pokrycie": round(k.pokrycie, 4), "rms_mm": (round(k.rms_mm, 4) if math.isfinite(k.rms_mm) else None),
                           "pokrycie_odwrotne": round(k.pokrycie_odwrotne, 4)} for k in r.kandydaci[:5]],
            "skala": asdict(r.skala) if r.skala is not None else None,
            "inspekcja": None,
        }
        k = r.najlepszy
        if inspekcja and r.status != "szary" and k is not None and k.transformacja is not None:
            try:
                wi = I.sprawdz(f.punkty, f.normalne, pula.projekty[k.klucz], np.array(k.transformacja), k.pokrycie, ust, f.gniazdo)
                wpis["inspekcja"] = wi.json()
            except MemoryError:  # brak pamięci dotyczy całego przebiegu, nie jednego gniazda
                raise
            except Exception as e:  # noqa: BLE001 — błąd inspekcji jednego gniazda nie może kłaść całej płytki (KeyboardInterrupt / SystemExit przechodzą)
                wi = None
                wpis["inspekcja"] = inspekcja_z_bledem(f.gniazdo, k.id, k.pokrycie, e)
                warnings.warn(f"gniazdo {f.gniazdo}: {wpis['inspekcja']['uwagi'][0]} — gniazdo żółte „nie sprawdzono”, pozostałe gniazda policzone", stacklevel=2)
            if podglad is not None and wi is not None:
                podglad[f.gniazdo] = wi
        wpis["status_gniazda"] = status_gniazda(r.status, wpis["inspekcja"])
        gniazda.append(wpis)
    return gniazda


def porownaj(skan: Path, foldery: list[Path], plytka: str, ust: dict, wspolczynnik: float | None = None, numer: int | None = None,
             orientacja: str = "auto", bez_filtru: bool = False, pula: M.Pula | None = None, inspekcja: bool = True,
             podglad: dict | None = None, postep=None, straznik: bool = True, pula_dla=None, kontekst: dict | None = None) -> dict:
    """Cały łańcuch na jednym skanie. ``postep(etap: str, udzial: float)`` — wywołanie zwrotne dla okna.

    ``plytka`` = ``"auto"`` (``AUTO``): układ rozpoznaje program (``plate.rozpoznaj_uklad`` na wszystkich układach z ``[plytki]``).
    Wynik ma wtedy ``plytka`` = nazwa rozpoznanego układu, ``plytka_wybor`` = ``"auto"`` i ``uklad_auto`` (opis decyzji: wybrany,
    pewny, powod, kandydaci). Współczynnik domyślny (``wspolczynnik`` = None) zależy od rozpoznanego typu płytki (poranna 1,0;
    wieczorna środek ``[synth]``), więc pula powstaje dopiero po wyrównaniu: podana ``pula`` jest użyta tylko, gdy ma ten
    współczynnik, inaczej ``pula_dla(w)`` (np. pamięć pul okna) albo nowa ``match.Pula``. ``kontekst`` (dict) dostaje ``uk``
    i ``pula`` użyte w przebiegu. Żaden układ nie pasuje → wynik jak przy niezgodności (``uklad_zgodny`` = False, bez gniazd).

    Układ podany ręcznie: skan, który do niego nie pasuje (``plate.NiezgodnyUklad``), daje wynik z ``uklad_zgodny`` = False,
    ``uklad_komunikat``, ``uklady_pasujace`` i pustą listą gniazd (match i inspect nie są liczone) oraz ostrzeżenie.
    Gdy żaden inny układ nie pasuje, a w ``[plytki]`` nie ma układów ``*_r54`` (stary ``ustawienia.toml``), komunikat
    i pole ``uklad_podpowiedz`` mówią, że trzeba dopisać 4 wiersze ``*_r54`` z ``ustawienia.przyklad.toml``.
    """
    t0 = time.time()

    def krok(etap: str, udzial: float) -> None:
        if postep is not None:
            postep(etap, udzial)

    auto = plytka == AUTO
    uk = None if auto else U.wczytaj(plytka, UST.katalog_plytki(ust, plytka))
    w = wspolczynnik if wspolczynnik is not None else (None if auto else wspolczynnik_domyslny(plytka, ust))

    def pula_gotowa(p: M.Pula | None, w_: float, udzial: float) -> M.Pula:
        # pula per praca (E3-A5, match.Pula.z_wpisow) ma wspolczynnik kazdego wpisu - nie zalezy od typu plytki i nie jest zastepowana
        if p is not None and auto and wspolczynnik is None and not getattr(p, "per_praca", False) and not math.isclose(p.wspolczynnik, w_, rel_tol=0.0, abs_tol=1e-9):
            p = None  # pula z innym współczynnikiem niż domyślny dla rozpoznanej płytki
        if p is None:
            krok("pula projektów", udzial)
            p = pula_dla(w_) if pula_dla is not None else M.Pula(foldery, w_, orientacja)
        if len(p) == 0:
            if getattr(p, "per_praca", False):
                raise SystemExit(f"pula wpisow bez projektu do wczytania (liczniki: {json.dumps(p.liczniki, ensure_ascii=False)})")
            raise SystemExit(f"brak projektów STL w {', '.join(map(str, foldery))}")
        return p

    if w is not None:
        pula = pula_gotowa(pula, w, 0.05)
    krok("wczytanie skanu", 0.2)
    m = trimesh.load(skan, force="mesh")
    t1 = time.time()
    krok("rozpoznanie układu i wyrównanie płytki (plate)" if auto else "wyrównanie płytki (plate)", 0.35)
    info_auto = None
    try:
        if auto:
            uklady = uklady_z_ustawien(ust)
            wyr, info_auto = PL.rozpoznaj_uklad(m, list(uklady.values()), numer=numer, straznik=straznik)
            plytka, uk = wyr.plytka, uklady[wyr.plytka]
        else:
            wyr = PL.wyrownaj(m, uk, numer=numer, straznik=straznik)
    except PL.NiezgodnyUklad as e:
        t2 = time.time()
        if auto:
            pasujace = []
            podpowiedz = PODPOWIEDZ_BRAK_R54 if brak_ukladow_poprzednich(ust) else ""
            komunikat = str(e)
            info_auto = {"wybrany": None, "pewny": False, "powod": e.powod, "kandydaci": getattr(e, "kandydaci", [])}
        else:
            pasujace = uklady_pasujace(e.stozki, ust, plytka)
            podpowiedz = PODPOWIEDZ_BRAK_R54 if not pasujace and brak_ukladow_poprzednich(ust) else ""
            komunikat = str(e) + (f"; rozstaw stożków w skanie pasuje do układu: {', '.join(pasujace)}" if pasujace
                                  else "; rozstaw stożków w skanie nie pasuje do żadnego innego układu z [plytki]")
        komunikat += f"; {podpowiedz}" if podpowiedz else ""
        warnings.warn(komunikat, stacklevel=2)
        krok("wynik", 0.95)
        if kontekst is not None:
            kontekst.update(uk=uk, pula=pula)
        per_praca = getattr(pula, "per_praca", False)
        return {
            "skan": Path(skan).name, "plytka": plytka, "plytka_wybor": "auto" if auto else "reczny", "uklad_auto": info_auto,
            "uklad_zgodny": False, "uklad_komunikat": komunikat, "uklady_pasujace": pasujace,
            "uklad_podpowiedz": podpowiedz,
            **({"pula_wpisy": pula.opis()} if per_praca else {}),
            "wspolczynnik": None if per_praca else w, "projekty": len(pula) if pula is not None else None, "foldery_projektow": [str(f) for f in foldery],
            "numer": None, "numer_zrodlo": "nieznany", "bity": [], "numer_z_dolkow": None,
            "macierz_skan_do_plytki": e.macierz.tolist() if e.macierz is not None else None, "jakosc_wyrownania": e.jakosc,
            "gniazda": [], "gniazda_puste": [], "gniazda_podwojne": [], "poza_gniazdem": 0, "fragmenty_drobne": 0,
            "czas_s": {"wczytanie": round(t1 - t0, 2), "plate": round(t2 - t1, 2), "match": 0.0, "razem": round(t2 - t0, 2),
                       "pula": pula.czas_s if pula is not None else 0.0, "inspect": 0.0},
            "bez_filtru": bez_filtru, "inspekcja": inspekcja, "statusy_gniazd": {s: 0 for s in STATUSY_GNIAZDA}, "ubytki": 0,
        }
    t2 = time.time()
    if w is None:  # auto bez podanego współczynnika: domyślny dla rozpoznanego typu płytki
        w = wspolczynnik_domyslny(plytka, ust)
        pula = pula_gotowa(pula, w, 0.45)
    if kontekst is not None:
        kontekst.update(uk=uk, pula=pula)
    t2b = time.time()
    krok("identyfikacja i inspekcja gniazd (match + inspect)", 0.55)
    ratunek: dict = {}
    gniazda = dopasuj_fragmenty(wyr, pula, ust, bez_filtru, inspekcja, podglad, start=t0, statystyka=ratunek)
    t3 = time.time()
    krok("wynik", 0.95)
    wynik = {
        "skan": Path(skan).name, "plytka": plytka, "plytka_wybor": "auto" if auto else "reczny", "uklad_auto": info_auto,
        "uklad_zgodny": wyr.jakosc.get("uklad_zgodny"),  # None = strażnik wyłączony
        **({"pula_wpisy": pula.opis(), "ratunek": ratunek} if getattr(pula, "per_praca", False) else {}),  # E3-A5: pula per praca - wspolczynnik ma kazdy wpis; ratunek (runda 3)
        "wspolczynnik": None if getattr(pula, "per_praca", False) else w, "projekty": len(pula), "foldery_projektow": [str(f) for f in foldery],
        "numer": wyr.numer, "numer_zrodlo": wyr.numer_zrodlo, "bity": wyr.bity, "numer_z_dolkow": wyr.numer_z_dolkow,
        "macierz_skan_do_plytki": wyr.macierz.tolist(), "jakosc_wyrownania": wyr.jakosc,
        "gniazda": gniazda, "gniazda_puste": wyr.gniazda_puste, "gniazda_podwojne": wyr.gniazda_podwojne,
        "poza_gniazdem": sum(1 for f in wyr.fragmenty if f.status == "poza_gniazdem"), "fragmenty_drobne": sum(1 for f in wyr.fragmenty if f.status == "drobny"),
        "czas_s": {"wczytanie": round(t1 - t0, 2), "plate": round(t2 - t1, 2), "match": round(t3 - t2b, 2), "razem": round(t3 - t0, 2), "pula": pula.czas_s,
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


def _sumuj(suma: dict, czesc: dict) -> None:
    """Dodaje liczniki ``czesc`` do ``suma`` (słowniki zagnieżdżone dowolnie głęboko)."""
    for k, v in czesc.items():
        if isinstance(v, dict):
            _sumuj(suma[k], v)
        else:
            suma[k] += v


def metryki_inspekcji(wynik: dict, prawda: S.PrawdaPlytki, pula: M.Pula | None = None) -> dict:
    """Wykryte / fałszywe ubytki per metoda (A, B, A+B, czerwone, dowolne) i per scenariusz pracy; drgnięcie; poprawki.

    Praca liczy się, gdy fragment leży w swoim gnieździe, top‑1 trafny i inspekcja była liczona.
    Ubytki liczone tylko na pracach bez drgnięcia (drgnięcie = „skan ponownie”, ubytki nieliczone z definicji).
    P4: te same liczniki osobno dla ubytków na krawędzi brzegu i na ścianie (``klasy``: ``krawedz`` / ``sciana`` /
    ``nieznane``) — klasa z pola ``polozenie`` prawdy; dla prawdy sprzed P4 (bez tego pola) klasa jest liczona z linii
    brzegu projektu, gdy podano ``pula`` (inaczej ``nieznane``). ``ubytki`` = lista wszystkich ubytków prawdy z wynikiem
    (do metryk per rozmiar / położenie). P2: prace całe ze statusem „nie sprawdzono” liczone osobno — to nie alarm.
    """
    praw = {p.gniazdo: p for p in prawda.prace}
    klucze = ("A", "B", "A+B", "czerwony", "dowolny")
    puste = lambda: {"prac": 0, "prac_calych": 0, "ubytkow": 0, "wykryte": {k: 0 for k in klucze},  # noqa: E731
                     "prace_cale_z_alarmem": 0, "prace_cale_z_czerwonym": 0, "prace_cale_nie_sprawdzono": 0, "prace_nie_sprawdzono": 0,
                     "prace_cale_status_gniazda": {s: 0 for s in STATUSY_GNIAZDA},
                     "falszywe_ubytki": 0, "falszywe_czerwone": 0, "falszywe_metoda": {"A": 0, "B": 0, "A+B": 0},
                     "klasy": {kl: {"wszystkich": 0, "ubytkow": 0, "wykryte": {k: 0 for k in klucze}} for kl in KLASY_POLOZENIA},
                     "statusy": {s: 0 for s in I.STATUSY}, "statusy_gniazd": {s: 0 for s in STATUSY_GNIAZDA}, "top1_bledny": 0, "bez_inspekcji": 0}
    sc = {s: puste() for s in SCENARIUSZE}
    lista: list[dict] = []
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
        for j, u in enumerate(p.ubytki):  # P4: krawędź / ściana osobno + wiersz na ubytek
            klasa, odl_linii = I.klasa_polozenia(u.polozenie), u.odleglosc_od_linii
            if klasa == "nieznane" and pula is not None and p.projekt in pula.projekty:
                klasa, odl_linii = I.polozenie_ubytku_prawdy(u, pula.projekty[p.projekt], np.array(p.transformacja))
            kl = s["klasy"][klasa]
            kl["wszystkich"] += 1
            if u.wykrywalny:
                kl["ubytkow"] += 1
                for k in klucze:
                    kl["wykryte"][k] += dp["trafione"][k][j]
            lista.append({"gniazdo": g["gniazdo"], "projekt": p.projekt, "scenariusz": scenariusz(p), "klasa": klasa, "polozenie": u.polozenie,
                          "srednica": u.srednica, "glebokosc": u.glebokosc, "glebokosc_rzeczywista": u.glebokosc_rzeczywista, "celowy": u.celowy,
                          "filar": u.filar, "odleglosc_od_linii": odl_linii, "wykrywalny": u.wykrywalny, "widoczny": u.widoczny,
                          "status_inspekcji": ins["status"], "trafione": {k: bool(dp["trafione"][k][j]) for k in klucze}})
        s["prace_nie_sprawdzono"] += ins["status"] == "nie_sprawdzono"
        if not p.ubytki:
            s["prac_calych"] += 1
            s["prace_cale_z_alarmem"] += ins["status"] in ("ubytek", "sprawdz")
            s["prace_cale_z_czerwonym"] += ins["status"] == "ubytek"
            s["prace_cale_nie_sprawdzono"] += ins["status"] == "nie_sprawdzono"
            s["prace_cale_status_gniazda"][g["status_gniazda"]] += 1
        s["falszywe_ubytki"] += dp["falszywe"]
        s["falszywe_czerwone"] += dp["falszywe_czerwone"]
    razem = puste()
    for s in sc.values():
        _sumuj(razem, s)
    return {"scenariusze": sc, "razem": razem, "drgniecie": drg, "poprawki": pop, "ubytki": lista}


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
         "gniazdo  projekt           zęby          pokrycie  pewność  skala %   match    gniazdo       inspect           ubytki (metoda, ø mm)"]
    ostrz_skali = []
    for g in sorted(wynik["gniazda"], key=lambda g: (g["gniazdo"] is None, g["gniazdo"] or 0)):
        k = g["kandydaci"][0] if g["kandydaci"] else None
        gn = "poza" if g["gniazdo"] is None else f"{g['gniazdo']:>4d}" + ("×2" if g["status_fragmentu"] == "podwojny" else "  ")
        ins = g.get("inspekcja")
        ub = ", ".join(f"{u['metoda']} {u['kolor'][0]} ø{u['srednica_mm']:.2f}" for u in ins["ubytki"]) if ins else ""
        sk = g.get("skala")  # poprawka skali ze skanu: w nawiasie = zmierzona, ale niezastosowana; „!” = ostrzeżenie; „?” = estymata niepewna
        if not sk or sk["poprawka_proc"] is None:
            skala = "—"
        else:
            skala = (f"{sk['poprawka_proc']:+.2f}" if sk["zastosowana"] else f"({sk['poprawka_proc']:+.2f})") + ("!" if sk["ostrzezenie"] else "?" if sk.get("niepewna") else "")
            if sk["ostrzezenie"]:
                ostrz_skali.append(f"{gn.strip()}: {sk['poprawka_proc']:+.2f} %" + ("" if sk["zastosowana"] else f" (bez korekty: {sk['powod']})"))
        w.append(f"{gn:>7s}  {k['id'] if k else '—':16s}  {'-'.join(k['zeby']) if k else '':13s} {k['pokrycie'] if k else 0:8.3f}  {g['pewnosc']:7.3f}  {skala:>8s}  {g['status']:8s} "
                 f"{g['status_gniazda']:13s} {ins['status'] if ins else '—':17s} {ub}")
    w.append(f"puste: {wynik['gniazda_puste']}; podwójne: {wynik['gniazda_podwojne']}; poza gniazdem: {wynik['poza_gniazdem']}; "
             f"gniazda: {', '.join(f'{s} {n}' for s, n in wynik['statusy_gniazd'].items() if n)}; ubytków {wynik['ubytki']}")
    nie_spr = gniazda_nie_sprawdzone(wynik)
    if nie_spr:  # P2: żółte „nie sprawdzono” — brzegu nie dało się sprawdzić (to nie ubytek)
        w.append(f"NIE SPRAWDZONO (żółte, brzegu nie dało się sprawdzić): gniazda {nie_spr}")
    for g in sorted(wynik["gniazda"], key=lambda g: (g["gniazdo"] is None, g["gniazdo"] or 0)):
        brzeg = (g.get("inspekcja") or {}).get("brzeg") or {}
        if brzeg and not brzeg.get("sprawdzony", True):
            w.append(f"  gniazdo {g['gniazdo']}: brzeg nie sprawdzony — {brzeg.get('opis', '')}")
        blad = (g.get("inspekcja") or {}).get("blad")
        if blad:  # P7: wyjątek w inspekcji tego gniazda — reszta płytki policzona
            w.append(f"  gniazdo {g['gniazdo']}: {UWAGA_BLEDU_INSPEKCJI.upper()} — pracy nie sprawdzono ({blad})")
    if ostrz_skali:
        w.append("OSTRZEŻENIE SKALI (praca większa / mniejsza niż projekt × współczynnik — sprawdź współczynnik / krążek): gniazdo " + "; ".join(ostrz_skali))
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
        podpis = f"{g.id}" + (f"\n{'-'.join(k['zeby']) or k['id'][:6]}\n{k['pokrycie']:.2f}" if k else "") + (f"\n{ins['status'].replace('_', ' ')}" if ins and ins["status"] != "ok" else "")
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
    d.text(P(-r + 2, r - 2), f"{wynik['skan']}  {wynik['plytka']} nr {wynik['numer']}  zielone = OK, czerwone = ubytek, zolte = sprawdz / nie sprawdzono, szare = bez projektu, "
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


KOLUMNY_WPISOW = ("plik", "wspolczynnik", "krazek", "frezowanie_id", "projekt_id")


def wczytaj_wpisy(plik: Path) -> list[dict]:
    """Wpisy puli per praca z pliku CSV (wiersz polecen ``--wpisy``; E3-A5): naglowek z kolumnami ``plik;wspolczynnik``
    i opcjonalnie ``krazek``, ``frezowanie_id``, ``projekt_id`` (srednik; przecinek dziesietny dozwolony; UTF-8 albo cp1250).
    Brak ``projekt_id`` = numer wiersza. Bledny wiersz = ``ValueError`` z numerem linii (bez tresci pol - w sciezkach sa nazwiska)."""
    dane = Path(plik).read_bytes()
    try:
        tekst = dane.decode("utf-8-sig")
    except UnicodeDecodeError:
        tekst = dane.decode("cp1250")
    linie = [(nr, l.strip()) for nr, l in enumerate(tekst.splitlines(), start=1) if l.strip()]
    if not linie:
        raise ValueError("plik wpisow jest pusty")
    naglowek = [k.strip().lower() for k in linie[0][1].rstrip(";").split(";")]
    if not {"plik", "wspolczynnik"} <= set(naglowek) or not set(naglowek) <= set(KOLUMNY_WPISOW):
        raise ValueError(f"plik wpisow: naglowek ma miec kolumny plik;wspolczynnik[;krazek;frezowanie_id;projekt_id] (linia {linie[0][0]})")
    wpisy = []
    for nr, linia in linie[1:]:
        pola = [p.strip() for p in linia.rstrip(";").split(";")]
        if len(pola) != len(naglowek):
            raise ValueError(f"plik wpisow: linia {nr} ma {len(pola)} pol zamiast {len(naglowek)}")
        r = dict(zip(naglowek, pola))
        try:
            w = float(r["wspolczynnik"].replace(",", "."))
            fid = int(r["frezowanie_id"]) if r.get("frezowanie_id") else None
            pid = int(r["projekt_id"]) if r.get("projekt_id") else len(wpisy) + 1
        except ValueError:
            raise ValueError(f"plik wpisow: linia {nr} - zla liczba (wspolczynnik, frezowanie_id albo projekt_id)") from None
        if not (math.isfinite(w) and 0.5 <= w <= 2.0) or not r["plik"]:
            raise ValueError(f"plik wpisow: linia {nr} - wspolczynnik spoza 0,5-2,0 albo pusty plik")
        wpisy.append({"plik": r["plik"], "wspolczynnik": w, "krazek": r.get("krazek") or None, "frezowanie_id": fid, "projekt_id": pid, "sha16": None})
    return wpisy


def main(argv: list[str] | None = None) -> dict:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--skan", type=Path, required=True)
    ap.add_argument("--projekty", type=Path, nargs="+", default=None, help="folder(y) z STL projektów (podfoldery zleceń); albo --wpisy")
    ap.add_argument("--wpisy", type=Path, default=None, help="pula per praca: plik CSV plik;wspolczynnik[;krazek;frezowanie_id;projekt_id] (zamiast --projekty)")
    ap.add_argument("--pamiec-puli", type=Path, default=None, help="katalog pamieci podrecznej projektow puli per praca (domyslnie [sciezki] pula_cache/projekty)")
    ap.add_argument("--plytka", default=AUTO, help="auto (domyślnie: program sam rozpoznaje układ ze skanu) albo nazwa układu z [plytki]")
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
    auto = a.plytka == AUTO
    if not auto and a.plytka not in ust["plytki"]:
        ap.error(f"--plytka {a.plytka!r}: brak w [plytki] (są: {AUTO}, {', '.join(ust['plytki'])})")
    if not a.skan.exists():
        ap.error(f"brak pliku skanu {a.skan}")
    if (a.projekty is None) == (a.wpisy is None):
        ap.error("podaj --projekty (folder(y) STL) albo --wpisy (pula per praca) - jedno z nich")
    for f in a.projekty or []:
        if not f.is_dir():
            ap.error(f"brak folderu projektów {f}")
    if a.wpisy is not None:  # pula per praca (E3-A5): wspolczynnik kazdego wpisu; --wspolczynnik tylko dla wpisow bez wspolczynnika
        from . import pamiec_puli as PP
        try:
            wpisy = wczytaj_wpisy(a.wpisy)
        except (OSError, ValueError) as e:
            ap.error(str(e) if isinstance(e, ValueError) else f"nie da sie odczytac pliku wpisow ({type(e).__name__})")
        pamiec = PP.PamiecPuli(a.pamiec_puli) if a.pamiec_puli is not None else PP.z_ustawien(ust)
        w = a.wspolczynnik
        pula = M.Pula.z_wpisow(wpisy, None, a.orientacja, pamiec=pamiec, wspolczynnik_domyslny=a.wspolczynnik)
    elif auto:  # układ, współczynnik domyślny i pula wynikają z rozpoznania — robi to porownaj()
        w, pula = a.wspolczynnik, None
    else:
        w = a.wspolczynnik if a.wspolczynnik is not None else wspolczynnik_domyslny(a.plytka, ust)
        pula = M.Pula(a.projekty, w, a.orientacja)
    kontekst: dict = {}
    with warnings.catch_warnings(record=True) as ostrz:
        warnings.simplefilter("always")
        wynik = porownaj(a.skan, a.projekty or [], a.plytka, ust, w, a.numer, a.orientacja, a.bez_filtru, pula, inspekcja=not a.bez_inspekcji,
                         straznik=not a.bez_straznika, kontekst=kontekst)
    uk, pula = kontekst.get("uk"), kontekst.get("pula")
    wynik["ostrzezenia"] = [str(o.message) for o in ostrz]
    niezgodny = wynik.get("uklad_zgodny") is False  # metryk na prawdzie nie ma: skan nie jest wyrównany do tego układu
    if a.prawda is not None and not niezgodny:
        prawda = S.wczytaj_prawde(a.prawda)
        wynik["metryki"] = metryki(wynik, prawda, pula)
        if auto:
            wynik["metryki"]["uklad_rozpoznany_ok"] = wynik["plytka"] == prawda.plytka
        if not a.bez_inspekcji:
            wynik["metryki_inspekcji"] = metryki_inspekcji(wynik, prawda)
    wyj = a.wyjscie if a.wyjscie is not None else a.skan.parent
    wyj.mkdir(parents=True, exist_ok=True)
    p_json = wyj / f"{a.skan.stem}_wynik.json"
    p_json.write_text(json.dumps(wynik, ensure_ascii=False, indent=1), encoding="utf-8")
    if auto and niezgodny:
        print(f"skan {wynik['skan']}: NIE ROZPOZNANO UKŁADU PŁYTKI — gniazd nie oceniano ({wynik['uklad_komunikat']})")
    else:
        if auto:
            ua = wynik["uklad_auto"]
            print(f"układ rozpoznany automatycznie: {wynik['plytka']} — {opis_ukladu(wynik['plytka'], uk)} "
                  f"(podstawa: {ua['powod']}{'' if ua['pewny'] else '; NIEPEWNE — podaj --numer albo --plytka'})")
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
    if not a.bez_png and uk is not None:
        print(mapa_png(wynik, uk, wyj / f"{a.skan.stem}_mapa.png"))
    print(p_json)
    return wynik


if __name__ == "__main__":
    main()
