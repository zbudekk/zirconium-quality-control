"""qc.metryki - metryki odbiorcze calego lancucha plate -> match -> inspect na danych syntetycznych.

Jedno polecenie (`python -m qc.metryki`) = jedna strona wynikow (sekcja 14 planu). `policz` generuje plytki
syntetyczne wg ukladow z ustawien, uruchamia lancuch i porownuje z prawda; `ocen` sprawdza progi odbiorcze.
"""

from __future__ import annotations

import gc
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field, replace

WATKI = 4  # dopasuj + sprawdz rownolegle na fragmentach jednej plytki (moduly bez stanu globalnego)

# OpenMP open3d (ICP, KD-tree) w kazdym z WATKI watkow: bez limitu na 24-watkowym CPU nadsubskrypcja (fixture
# szybko > 9 min, z maska 4 rdzeni 97 s). Zmienna dziala tylko przed pierwszym importem open3d; ustawienie
# uzytkownika ma pierwszenstwo.
if "open3d" not in sys.modules:
    os.environ.setdefault("OMP_NUM_THREADS", str(max(1, (os.cpu_count() or 1) // WATKI)))

import numpy as np  # noqa: E402
import trimesh  # noqa: E402

# Kryteria odbioru z sekcji 14 planu (nie strojenie, nie ustawienia stanowiska). Wartosc rowna progowi
# zalicza odbior. top1 i wykryte_od_0_3: minimum; prace_z_falszywym_alarmem: maksimum.
PROGI_ODBIORCZE = {"top1": 0.85, "wykryte_od_0_3": 0.80, "prace_z_falszywym_alarmem": 0.15}
_POLA_PROGOW = {
    "top1": (("identyfikacja", "razem", "udzial_top1"), "min"),
    # uczciwa wersja: ukruszenia prac bez "pewny" (bez inspekcji) licza sie jako niewykryte
    "wykryte_od_0_3": (("ubytki", "udzial_wykrytych_od_0_3_wszystkie"), "min"),
    "prace_z_falszywym_alarmem": (("ubytki", "udzial_prac_z_falszywym_alarmem"), "max"),
}
KOD_OK = 0
KOD_PONIZEJ_PROGU = 3

KLASY = (("0.2-0.3", 0.2, 0.3), ("0.3-0.4", 0.3, 0.4), ("0.4-0.6", 0.4, 0.6))
KLASY_ODBIORU = ("0.3-0.4", "0.4-0.6")
STANY = ("praca", "puste", "podwojne", "poza_gniazdem")
TOLERANCJA_SRODKA_MM = 0.5  # przypisanie wykrytego ubytku do prawdy (qc.inspect.metryki.porownaj)
K_WIECZOR = (1.20, 1.25)
PROG_Z_GORY = 0.3  # rano: skan z gory bez scian o normalnej z < -0,3
MAX_MALA_MM = 6.3  # mala korona (siekacz) miesci sie w gniezdzie 7,5 rano i 9,0 wieczorem (k 1,25 + luz 1)


@dataclass
class PlanPlytki:
    tryb: str  # "wieczor" | "rano"
    numer: int
    korony: int
    mosty: int
    sigma: float
    zmien: dict = field(default_factory=dict)  # indeks rozmieszczenia -> dodatkowe opcje (stan)


@dataclass
class PlanDanych:
    korony: int  # projekty koron w bazie (pula_projektow)
    male: int  # dodatkowe male korony (siekacze <= MAX_MALA_MM): najmniejsze gniazda bez powtorek
    mosty: int
    wabiki_wieczor: int  # projekty spoza plytki w puli wieczornej
    max_pula: int
    poprawka_co: int  # co ktora praca wieczorna dostaje poprawke (0 = zadna)
    plytki: list[PlanPlytki]


PLANY = {
    "szybko": PlanDanych(korony=20, male=10, mosty=2, wabiki_wieczor=8, max_pula=30, poprawka_co=0, plytki=[
        PlanPlytki("wieczor", 1, 6, 1, 0.02),
        PlanPlytki("wieczor", 2, 6, 1, 0.03),
        PlanPlytki("rano", 4, 8, 1, 0.03),
    ]),
    "pelne": PlanDanych(korony=50, male=26, mosty=4, wabiki_wieczor=10, max_pula=60, poprawka_co=6, plytki=[
        PlanPlytki("wieczor", 1, 24, 2, 0.02),
        PlanPlytki("wieczor", 2, 18, 2, 0.03, zmien={3: {"stan": "podwojne"}}),
        PlanPlytki("wieczor", 3, 14, 2, 0.04),
        PlanPlytki("rano", 4, 35, 2, 0.02),
        PlanPlytki("rano", 5, 30, 2, 0.03, zmien={5: {"stan": "poza_gniazdem"}}),
        PlanPlytki("rano", 6, 22, 2, 0.04),
    ]),
}


# --- ocena ---------------------------------------------------------------------------


def _pole(d: dict, sciezka):
    for i, k in enumerate(sciezka):
        if k not in d and k == "udzial_wykrytych_od_0_3_wszystkie" and i == len(sciezka) - 1:
            k = "udzial_wykrytych_od_0_3"  # slownik sprzed poprawki (bez prac bez inspekcji)
        d = d[k]
    return float(d)


def ocen(wynik: dict) -> tuple[int, list[str]]:
    """(kod, nazwy metryk ponizej progu odbiorczego): (0, []) albo (3, [...])."""
    zle = []
    for nazwa, prog in PROGI_ODBIORCZE.items():
        sciezka, kierunek = _POLA_PROGOW[nazwa]
        wartosc = _pole(wynik, sciezka)
        if (kierunek == "min" and wartosc < prog) or (kierunek == "max" and wartosc > prog):
            zle.append(nazwa)
    return (KOD_PONIZEJ_PROGU if zle else KOD_OK), zle


# --- dane syntetyczne ----------------------------------------------------------------


def _udzial(a: int, b: int) -> float:
    return float(a) / b if b else 0.0


def _klasa(srednica: float) -> str:
    for nazwa, od, do in KLASY:
        if srednica < do:
            return nazwa
    return KLASY[-1][0]


def _ubytki_pracy(rng, n: int) -> list[dict]:
    """n ukruszen o srednicach rowno z 3 klas (kolejna klasa losowa)."""
    wynik = []
    for _ in range(n):
        _, od, do = KLASY[int(rng.integers(len(KLASY)))]
        wynik.append({"srednica_mm": float(rng.uniform(od, do))})
    return wynik


def _baza(plan: PlanDanych, ziarno: int):
    from qc.syntetyka import prace

    projekty = list(prace.pula_projektow(plan.korony, ziarno))
    z, male = ziarno * 10_000, 0
    while male < plan.male:
        z += 1
        siatka = prace.korona(z, "siekacz")
        if float(np.max(np.asarray(siatka.extents)[:2])) <= MAX_MALA_MM:
            siatka.metadata["id"] = f"mala-{z}"
            projekty.append(prace.Projekt(id=f"mala-{z}", rodzaj="siekacz", siatka=siatka))
            male += 1
    for i in range(plan.mosty):
        projekty.append(prace.Projekt(id=f"most-{ziarno}-{i + 1:02d}", rodzaj="most",
                                      siatka=prace.most(ziarno * 100 + i, 4 if i % 2 == 0 else 3)))
    return projekty


def _zwolnij(siatka) -> None:
    """Czysci cache trimesh siatki projektu (triangles, edges...: ok. 35 MB na projekt 150 tys. scian).

    Siatki projektow sa wspolne dla pul wszystkich plytek; bez tego cache rosnie z kazda plytka.
    """
    siatka._cache.clear()


def _pula(rozm, projekty, plan: PlanDanych, tryb: str, rng, cechy: dict):
    """Pula dla plytki: prace plytki (wieczor: k z prawdy, rano k = 1) + wabiki, najwyzej max_pula."""
    from qc.catalog.cechy import policz
    from qc.match import WpisPuli

    def wpis(p, k):
        if p.id not in cechy:
            cechy[p.id] = policz(p.siatka)
            _zwolnij(p.siatka)
        return WpisPuli(projekt_id=p.id, siatka=p.siatka, cechy=cechy[p.id], wspolczynnik=float(k))

    if tryb == "wieczor":
        pula = [wpis(r.projekt, r.wspolczynnik) for r in rozm]
        na_plytce = {r.projekt.id for r in rozm}
        reszta = [p for p in projekty if p.id not in na_plytce]
        for i in rng.permutation(len(reszta))[:plan.wabiki_wieczor]:
            pula.append(wpis(reszta[int(i)], rng.uniform(*K_WIECZOR)))
    else:
        widziane, pula = set(), []
        for r in rozm:
            if r.projekt.id not in widziane:
                widziane.add(r.projekt.id)
                pula.append(wpis(r.projekt, 1.0))
        reszta = [p for p in projekty if p.id not in widziane]
        for i in rng.permutation(len(reszta))[:max(0, plan.max_pula - len(pula))]:
            pula.append(wpis(reszta[int(i)], 1.0))
    return pula


def _rozmiesc(uklad, projekty, pp: PlanPlytki, ziarno: int):
    from qc.syntetyka import plytka

    return plytka.rozmiesc(uklad, projekty, pp.korony, pp.mosty, ziarno=ziarno * 1000 + pp.numer)


def _powtorzone(rozm) -> int:
    """Prace, ktorych projekt juz lezy na tej plytce (kopie ponad pierwsza)."""
    return len(rozm) - len({r.projekt.id for r in rozm})


def powtorzenia(tryb: str = "szybko", ziarno: int = 1, ustawienia=None) -> dict:
    """{"wieczor"/"rano": {"powtorzone", "prace"}} dla planu trybu - samo rozmieszczenie, bez skanow."""
    from qc import uklad as modul_ukladu
    from qc.ustawienia import wczytaj

    u = ustawienia or wczytaj()
    plan = PLANY[tryb]
    uklady = {"wieczor": modul_ukladu.wczytaj(u.plytki.wieczorna), "rano": modul_ukladu.wczytaj(u.plytki.poranna)}
    projekty = _baza(plan, ziarno)
    wynik = {t: {"powtorzone": 0, "prace": 0} for t in ("wieczor", "rano")}
    for pp in plan.plytki:
        rozm = _rozmiesc(uklady[pp.tryb], projekty, pp, ziarno)
        wynik[pp.tryb]["powtorzone"] += _powtorzone(rozm)
        wynik[pp.tryb]["prace"] += len(rozm)
    return wynik


def _plytka(uklad, projekty, plan: PlanDanych, pp: PlanPlytki, ziarno: int, przesuniecie: int, cechy: dict):
    """(rozmieszczenia, skan, prawda, pula) jednej plytki; przesuniecie = prace wieczorne wczesniejszych plytek."""
    from qc.syntetyka import plytka

    z = ziarno * 1000 + pp.numer
    rng = np.random.default_rng(z)
    rozm = _rozmiesc(uklad, projekty, pp, ziarno)
    for i, opcje in pp.zmien.items():
        rozm[i] = replace(rozm[i], opcje={**rozm[i].opcje, **opcje})
    for i, r in enumerate(rozm):
        opcje = dict(r.opcje)
        if pp.tryb == "wieczor":
            n = przesuniecie + i + 1
            opcje["ubytki"] = _ubytki_pracy(rng, 1 if n % 3 == 1 else 2)
            if plan.poprawka_co and n % plan.poprawka_co == 0:
                opcje["poprawki"] = 1
        rozm[i] = replace(r, opcje=opcje)
    siatka, prawda = plytka.skan_plytki(uklad, pp.numer, rozm, ziarno=z, szum_mm=pp.sigma, T_plytki="losowa")
    if pp.tryb == "rano":
        # rano skan calej plytki z gory: bez scian o normalnej z < -0,3 (jak test_plate::test_skan_z_gory;
        # zakresy scian prawdy po tym nieaktualne - metryki ich nie uzywaja)
        zostaw = np.asarray(siatka.face_normals)[:, 2] >= -PROG_Z_GORY
        siatka = trimesh.Trimesh(np.asarray(siatka.vertices), np.asarray(siatka.faces)[zostaw], process=False)
    return rozm, siatka, prawda, _pula(rozm, projekty, plan, pp.tryb, rng, cechy)


# --- lancuch -------------------------------------------------------------------------


def _blad_wyrownania(T, T_prawdy, uklad) -> float:
    """Max przesuniecie narozy plytki (wierzch i dno) miedzy T a prawda, mm."""
    h = uklad.rozmiar / 2
    p = np.array([[x, y, z, 1.0] for x in (-h, h) for y in (-h, h) for z in (0.0, -uklad.grubosc)])
    a = p @ np.linalg.inv(T).T
    b = p @ np.linalg.inv(T_prawdy).T
    return float(np.max(np.linalg.norm(a[:, :3] - b[:, :3], axis=1)))


def _stany_prawdy(uklad, prawda) -> tuple[dict, int]:
    """Stan gniazd z prawdy (gniazdo -> stan) i liczba prac poza gniazdem."""
    stany = {g.nr: "puste" for g in uklad.gniazda}
    poza = 0
    for p in prawda.prace:
        if p.stan == "poza_gniazdem" or p.gniazdo is None:
            poza += 1
        elif p.stan == "podwojne":
            stany[p.gniazdo] = "podwojne"
        elif stany[p.gniazdo] == "puste":
            stany[p.gniazdo] = "praca"
    return stany, poza


def _licznik_ident() -> dict:
    return {"prace": 0, "fragmenty": 0, "bez_fragmentu": 0, "fragmenty_bez_prawdy": 0, "top1": 0, "top2": 0,
            "pewny": 0, "dwuznaczny": 0, "brak": 0, "falszywe_pewny": 0, "powtorzone": 0}


def _licznik_ubytkow() -> dict:
    return {"wykryte": 0, "pominiete": 0, "falszywe": 0}


def _prace_w_gniazdach(prawda) -> dict:
    """Gniazdo -> PrawdaPracy prac w stanie "praca" (mianownik identyfikacji i ubytkow).

    Prace "podwojne" / "poza_gniazdem" sa poza mianownikiem: plate je zglasza, operator poprawia ulozenie
    i skanuje ponownie.
    """
    podwojne = {p.gniazdo for p in prawda.prace if p.stan == "podwojne"}
    return {p.gniazdo: p for p in prawda.prace
            if p.stan == "praca" and p.gniazdo is not None and p.gniazdo not in podwojne}


def _rozlicz(pp, rozm, prawda, zwykle, wyniki_praca, ident, bez_inspekcji, lista_prac) -> None:
    """Identyfikacja i ukruszenia bez inspekcji po pracach z prawdy (brak fragmentu = "brak")."""
    t = ident[pp.tryb]
    t["powtorzone"] += _powtorzone(rozm)
    for g, p in sorted(zwykle.items()):
        w = wyniki_praca.get(g)
        pewnosc = w["pewnosc"] if w else "brak"
        top1, top2 = (bool(w["top1"]), bool(w["top2"])) if w else (False, False)
        sprawdzona = bool(w) and w["porownanie"] is not None
        t["prace"] += 1
        t["bez_fragmentu"] += int(w is None)
        t[pewnosc] += 1
        t["top1"] += int(top1)
        t["top2"] += int(top2)
        t["falszywe_pewny"] += int(pewnosc == "pewny" and not top1)
        ukruszenia = [x for x in p.ubytki if x.rodzaj == "ukruszenie"]
        if pp.tryb == "wieczor" and not sprawdzona:
            for x in ukruszenia:
                bez_inspekcji[_klasa(x.srednica_mm)] += 1
        lista_prac.append({"plytka": pp.numer, "tryb": pp.tryb, "gniazdo": int(g), "projekt_id": p.id,
                           "pewnosc": pewnosc, "top1": top1, "ukruszenia": len(ukruszenia),
                           "sprawdzona": sprawdzona})


def _fragment(frag, prawda_pracy, pula, T_skan_do_plytki, u, tryb, pamiec):
    """dopasuj (+ sprawdz wieczorem przy "pewny" pracy z prawda) jednego fragmentu: slownik wyniku.

    Prawda przenoszona do ukladu fragmentu zmierzona T_skan_do_plytki (wyrownanie plate), jak na stanowisku.
    """
    import qc.inspect as inspect
    import qc.match as match
    from qc.inspect import metryki

    t0 = time.perf_counter()
    wd = match.dopasuj(frag.siatka, pula, u, tryb=tryb, pamiec=pamiec)
    ids = [k.projekt_id for k in wd.kandydaci]
    prawdziwy = prawda_pracy.id if prawda_pracy is not None else None
    wynik = {"pewnosc": wd.pewnosc, "top1_id": ids[0] if ids else None, "top1": bool(ids) and ids[0] == prawdziwy,
             "top2": prawdziwy in ids[:2], "porownanie": None}
    if tryb == "wieczor" and wd.pewnosc == "pewny" and prawda_pracy is not None:
        top = wd.kandydaci[0]
        projekt = next(w.siatka for w in pula if w.projekt_id == top.projekt_id)
        wi = inspect.sprawdz(frag.siatka, projekt, top.T_projekt_do_fragmentu, u)
        T = T_skan_do_plytki @ prawda_pracy.T_projekt_do_skanu
        c = metryki.porownaj(wi, prawda_pracy, T, tolerancja_mm=TOLERANCJA_SRODKA_MM)
        sparowane = {id(w) for w, _ in c.pary}
        prawdy = [x for x in prawda_pracy.ubytki if x.rodzaj == metryki.RODZAJ_LICZONY]
        sparowane_p = {id(p) for _, p in c.pary}
        wynik["porownanie"] = {
            "wykryte": [_klasa(p.srednica_mm) for _, p in c.pary],
            "pominiete": [_klasa(p.srednica_mm) for p in prawdy if id(p) not in sparowane_p],
            "falszywe": [_klasa(w.srednica_mm) for w in wi.ubytki if id(w) not in sparowane],
        }
    wynik["czas_s"] = time.perf_counter() - t0
    return wynik


def policz(ustawienia, tryb: str = "szybko", ziarno: int = 1) -> dict:
    """Generuje dane syntetyczne wg trybu, uruchamia lancuch i zwraca slownik metryk (JSON)."""
    import qc
    import qc.plate as plate
    from qc import uklad as modul_ukladu

    if tryb not in PLANY:
        raise ValueError(f"nieznany tryb '{tryb}' (dozwolone: {', '.join(PLANY)})")
    plan = PLANY[tryb]
    start = time.perf_counter()
    uklady = {"wieczor": modul_ukladu.wczytaj(ustawienia.plytki.wieczorna),
              "rano": modul_ukladu.wczytaj(ustawienia.plytki.poranna)}
    projekty = _baza(plan, ziarno)
    cechy: dict = {}
    przesuniecia, n = [], 0
    for pp in plan.plytki:
        przesuniecia.append(n)
        n += (pp.korony + pp.mosty) if pp.tryb == "wieczor" else 0

    bledy_wyr, numery = [], {"ok": 0, "zle": 0, "brak": 0}
    bledy_plytek = []
    stany = {s: {"wynik": 0, "prawda": 0} for s in STANY}
    gniazda_zgodne = gniazda_wszystkie = 0
    ident = {t: _licznik_ident() for t in ("wieczor", "rano")}
    podwojne = {"fragmenty": 0, "top1_ktorakolwiek": 0}
    klasy = {n: _licznik_ubytkow() for n, _, _ in KLASY}
    sigmy: dict[str, dict] = {}
    sprawdzone = {"wieczor": 0, "rano": 0}
    prace_z_alarmem = 0
    bez_inspekcji = {n: 0 for n, _, _ in KLASY}
    lista_prac = []
    czasy_plytek, czasy_fragmentow = [], []

    for i_plytki, pp in enumerate(plan.plytki):
        uklad = uklady[pp.tryb]
        rozm, siatka, prawda, pula = _plytka(uklad, projekty, plan, pp, ziarno, przesuniecia[i_plytki], cechy)
        T_prawdy = np.asarray(prawda.plytka["T_skan_do_plytki"], dtype=np.float64)
        st_prawdy, poza_prawdy = _stany_prawdy(uklad, prawda)
        for s in st_prawdy.values():
            stany[s]["prawda"] += 1
        stany["poza_gniazdem"]["prawda"] += poza_prawdy

        t0 = time.perf_counter()
        try:
            wp = plate.analizuj(siatka, uklad, ustawienia)
        except plate.BladPlytki as e:
            bledy_plytek.append(f"plytka {pp.numer}: {e}")
            numery["brak"] += 1
            czasy_plytek.append(time.perf_counter() - t0)
            _rozlicz(pp, rozm, prawda, _prace_w_gniazdach(prawda), {}, ident, bez_inspekcji, lista_prac)
            continue
        czasy_plytek.append(time.perf_counter() - t0)
        bledy_wyr.append(_blad_wyrownania(wp.wyrownanie.T_skan_do_plytki, T_prawdy, uklad))
        numery["ok" if wp.numer == pp.numer else ("brak" if wp.numer is None else "zle")] += 1

        st_wyniku = {f.gniazdo: f.stan for f in wp.fragmenty if f.stan != "poza_gniazdem"}
        for f in wp.fragmenty:
            stany[f.stan]["wynik"] += 1
        for nr, s in st_prawdy.items():
            gniazda_wszystkie += 1
            gniazda_zgodne += int(st_wyniku.get(nr) == s)

        zwykle = _prace_w_gniazdach(prawda)
        do_dopasowania = [f for f in wp.fragmenty if f.stan in ("praca", "podwojne")]
        zadania = [(f, zwykle.get(f.gniazdo) if f.stan == "praca" else None) for f in do_dopasowania]
        T_zmierzone = np.asarray(wp.wyrownanie.T_skan_do_plytki, dtype=np.float64)
        # skan plytki (oryginal i wyrownany) niepotrzebny po cieciu - fragmenty maja wlasne siatki
        del siatka, wp
        gc.collect()
        pamieci = {}

        def wykonaj(zadanie):
            f, p = zadanie
            pam = pamieci.setdefault(threading.get_ident(), {})
            return _fragment(f, p, pula, T_zmierzone, ustawienia, pp.tryb, pam)

        with ThreadPoolExecutor(max_workers=WATKI) as wykonawca:
            wyniki = list(wykonawca.map(wykonaj, zadania))
        del pamieci
        gc.collect()  # cykle referencji w danych dopasowania: ok. 1 GB na plytke bez tego

        sg = sigmy.setdefault(f"{pp.sigma:.2f}", _licznik_ubytkow())
        wyniki_praca = {}
        for (f, p), w in zip(zadania, wyniki):
            czasy_fragmentow.append(w["czas_s"])
            if f.stan == "podwojne":
                podwojne["fragmenty"] += 1
                w_gniezdzie = {x.id for x in prawda.prace if x.gniazdo == f.gniazdo}
                podwojne["top1_ktorakolwiek"] += int(w["top1_id"] in w_gniezdzie)
                continue
            t = ident[pp.tryb]
            t["fragmenty"] += 1
            if p is None:  # fragment "praca" bez pracy w prawdzie: tylko falszywy "pewny" sie liczy
                t["fragmenty_bez_prawdy"] += 1
                t["falszywe_pewny"] += int(w["pewnosc"] == "pewny")
                continue
            wyniki_praca[f.gniazdo] = w
            c = w["porownanie"]
            if c is None:
                continue
            sprawdzone[pp.tryb] += 1
            prace_z_alarmem += int(bool(c["falszywe"]))
            for pole in ("wykryte", "pominiete", "falszywe"):
                for k in c[pole]:
                    klasy[k][pole] += 1
                    sg[pole] += 1
        _rozlicz(pp, rozm, prawda, zwykle, wyniki_praca, ident, bez_inspekcji, lista_prac)
        del pula, wyniki, zadania, do_dopasowania
        for p in projekty:
            _zwolnij(p.siatka)
        gc.collect()

    def z_udzialem(d):
        return {**d, "udzial_wykrytych": _udzial(d["wykryte"], d["wykryte"] + d["pominiete"])}

    razem = {k: ident["wieczor"][k] + ident["rano"][k] for k in _licznik_ident()}
    identyfikacja = {}
    for nazwa, t in (("wieczor", ident["wieczor"]), ("rano", ident["rano"]), ("razem", razem)):
        identyfikacja[nazwa] = {**t, "udzial_top1": _udzial(t["top1"], t["prace"]),
                                "udzial_top2": _udzial(t["top2"], t["prace"])}
    identyfikacja["podwojne"] = podwojne

    wyk = sum(klasy[k]["wykryte"] for k in KLASY_ODBIORU)
    pom = sum(klasy[k]["pominiete"] for k in KLASY_ODBIORU)
    bez = sum(bez_inspekcji[k] for k in KLASY_ODBIORU)
    n_frag = len(czasy_fragmentow)
    wynik = {
        "wersja": qc.__version__,
        "ziarno": int(ziarno),
        "tryb": tryb,
        "plytka": {
            "plytki": len(plan.plytki),
            "blad_wyrownania_max_mm": float(max(bledy_wyr)) if bledy_wyr else 0.0,
            "blad_wyrownania_sredni_mm": float(np.mean(bledy_wyr)) if bledy_wyr else 0.0,
            "numery": numery,
            "fragmenty": stany,
            "gniazda": gniazda_wszystkie,
            "gniazda_zgodne": gniazda_zgodne,
            "udzial_gniazd_zgodnych": _udzial(gniazda_zgodne, gniazda_wszystkie),
            "bledy": bledy_plytek,
        },
        "identyfikacja": identyfikacja,
        "ubytki": {
            "klasy": {k: z_udzialem(v) for k, v in klasy.items()},
            "sigma": {k: z_udzialem(v) for k, v in sorted(sigmy.items())},
            "udzial_wykrytych_od_0_3": _udzial(wyk, wyk + pom),  # informacyjnie: prace zidentyfikowane
            "udzial_wykrytych_od_0_3_wszystkie": _udzial(wyk, wyk + pom + bez),  # prog odbiorczy
            "udzial_prac_z_falszywym_alarmem": _udzial(prace_z_alarmem, sprawdzone["wieczor"]),
            "prace_z_falszywym_alarmem": prace_z_alarmem,
            "sprawdzone_fragmenty": sprawdzone["wieczor"],
            "sprawdzone_rano": sprawdzone["rano"],
            "ubytki_bez_inspekcji": sum(bez_inspekcji.values()),
            "ubytki_bez_inspekcji_klasy": bez_inspekcji,
        },
        "czasy": {
            "na_plytke_s": float(np.mean(czasy_plytek)) if czasy_plytek else 0.0,
            "na_fragment_s": float(np.mean(czasy_fragmentow)) if n_frag else 0.0,
            "calosc_s": time.perf_counter() - start,
        },
    }
    wynik["prace"] = lista_prac
    wynik["progi_odbiorcze"] = dict(PROGI_ODBIORCZE)
    kod, zle = ocen(wynik)
    wynik["kod"] = kod
    wynik["ponizej_progu"] = zle
    return wynik
