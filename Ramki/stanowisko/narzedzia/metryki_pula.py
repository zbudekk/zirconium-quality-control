"""Metryki puli per praca (E3-A5): duza pula wpisow (projekt x wspolczynnik krazka), czasy zimne / cieple, szczyt pamieci,
kryteria 1 i 2 (dwa krazki 1,20 / 1,25; ten sam STL z dwoma wspolczynnikami) i regresja R59 przez pule wpisow.

Uzycie (z katalogu stanowisko/, na PC przez run.cmd):
    py -3.12 narzedzia/metryki_pula.py przygotuj --projekty <Prace_test> --katalog <W> [--wpisow 400] [--plytek 10] [--seed 1]
    py -3.12 narzedzia/metryki_pula.py czas --katalog <W> --pamiec <W/pamiec> [--linie <W/linie>] [--plytek 5] [--nazwa czas_zimna]
    py -3.12 narzedzia/metryki_pula.py jakosc --katalog <W> --pamiec <W/pamiec> [--linie <W/linie>] [--procesy 6]
    py -3.12 narzedzia/metryki_pula.py r59 --skany <dane/syntetyczne_R59_P2> <..._P3a> --projekty <Prace_test> --wyjscie <W> [--procesy 6]

``przygotuj``: w ``<W>/stl`` warianty projektow (te same prace, skala anizotropowa 0,97-1,03 - nowe pliki, podobny ksztalt)
i atrapy koron / mostow o losowych wymiarach; ``<W>/pula_<n>.csv`` = wpisy puli (``porownaj --wpisy``): kazdy projekt
testowy i 10 atrap "plytkowych" na OBU krazkach (1,20 i 1,25), warianty i pozostale atrapy z wspolczynnikiem 1,20 / 1,22 /
1,25; ``<W>/plytki`` = sztuczne skany plytek wieczornych (kwadrat i kolo R59, prace "dobrze") z pracami z dwoch krazkow
(``LosowanieKrazkow``: wspolczynnik pracy = 1,20 albo 1,25) + prawda. ``czas``: JEDEN proces - budowa puli, analiza
kolejnych plytek (``porownaj`` z pula wpisow), czas kazdej, szczyt pamieci procesu (peak working set); pierwszy przebieg z
pustym katalogiem ``--pamiec`` = pamiec zimna, kolejny = ciepla. ``jakosc``: kryterium 2 na puli ``pula_<n>.csv`` (wynik
wskazuje wpis krazka prawdy) i kryterium 1 na puli bez blizniakow (prace plytki tylko ze swoim krazkiem + rozpraszacze do
``n`` wpisow). ``r59``: zestawy R59 (40 skanow) jak ``metryki_P3a.py``, ale pula z wpisow (projekt x wspolczynnik prawdy).

Pliki CSV puli zawieraja sciezki projektow (nazwy folderow) - zostaja w katalogu roboczym PC; wyniki JSON i stdout tylko ze
skrotami. Sztuczne skany sa danymi do pomiaru kodu, nie skanera.
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import sys
import time
import warnings
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from stanowisko import krawedz as KR  # noqa: E402
from stanowisko import match as M  # noqa: E402
from stanowisko import pamiec_puli as PP  # noqa: E402
from stanowisko import porownaj as PO  # noqa: E402
from stanowisko import synth as S  # noqa: E402
from stanowisko import uklad as U  # noqa: E402
from stanowisko import ustawienia as UST  # noqa: E402

KRAZKI = (1.20, 1.25)
WSPOLCZYNNIKI_ROZPRASZACZY = (1.20, 1.22, 1.25)
UKLADY = ("wieczorna", "okragla_wieczorna")
ATRAP_PLYTKOWYCH = 10


class LosowanieKrazkow:
    """``rng`` dla ``synth.generuj_plytke``: wspolczynnik pracy = jeden z ``krazki`` (na przemian albo losowo), pozostale
    losowania bez zmian. Generator losuje wspolczynnik wywolaniem ``rng.uniform(*opcje.wspolczynnik)`` - przy
    ``opcje.wspolczynnik = (min(krazki), max(krazki))`` to wywolanie dostaje wartosc krazka zamiast liczby z przedzialu."""

    def __init__(self, rng: np.random.Generator, krazki, kolejno: bool = False):
        self._rng = rng
        self.krazki = tuple(float(k) for k in krazki)
        self.zakres = (min(self.krazki), max(self.krazki))
        self.kolejno = kolejno
        self._nr = 0

    def uniform(self, low=0.0, high=1.0, size=None):
        if size is None and (float(low), float(high)) == self.zakres:
            if self.kolejno:
                w = self.krazki[self._nr % len(self.krazki)]
                self._nr += 1
                return w
            return self.krazki[int(self._rng.integers(len(self.krazki)))]
        return self._rng.uniform(low, high, size)

    def __getattr__(self, nazwa):
        return getattr(self._rng, nazwa)


def szczyt_pamieci_mb() -> float | None:
    """Szczyt pamieci procesu (Windows: peak working set; inne: ru_maxrss) w MB."""
    try:
        import psutil
        mi = psutil.Process().memory_info()
        if hasattr(mi, "peak_wset"):
            return round(mi.peak_wset / 2**20, 1)
    except ImportError:
        pass
    try:
        import resource
        return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)
    except ImportError:
        return None


def pamiec_teraz_mb() -> float | None:
    try:
        import psutil
        return round(psutil.Process().memory_info().rss / 2**20, 1)
    except ImportError:
        return None


# ----------------------------------------------------------------------------
# przygotowanie: warianty, atrapy, wpisy, plytki
# ----------------------------------------------------------------------------
def zapisz_wpisy(plik: Path, wpisy: list[dict]) -> None:
    linie = ["plik;wspolczynnik;krazek;frezowanie_id;projekt_id"]
    for w in wpisy:
        linie.append(f"{w['plik']};{w['wspolczynnik']:.4f};{w['krazek']};{w['frezowanie_id']};{w['projekt_id']}")
    plik.write_text("\n".join(linie) + "\n", encoding="utf-8")


def przygotuj(a) -> None:
    import trimesh
    import atrapy_koron as AK

    rng = np.random.default_rng(a.seed)
    kat = a.katalog
    (kat / "stl" / "warianty").mkdir(parents=True, exist_ok=True)
    (kat / "stl" / "atrapy").mkdir(parents=True, exist_ok=True)
    projekty = sorted(p for d in a.projekty for p in S.pliki_projektow(d))
    wpisy: list[dict] = []
    pid = {}

    def dodaj(p: Path, w: float, krazek: str) -> None:
        pid.setdefault(str(p), len(pid) + 1)
        wpisy.append({"plik": str(p), "wspolczynnik": float(w), "krazek": krazek, "frezowanie_id": len(wpisy) + 1, "projekt_id": pid[str(p)]})

    for p in projekty:  # projekty testowe na obu krazkach (kryterium 2)
        for w in KRAZKI:
            dodaj(p, w, f"K-{round(w * 100)}")
    for i, p in enumerate(projekty):  # warianty: ta sama praca w skali anizotropowej (nowy plik, inny skrot, podobny ksztalt)
        m = S.wczytaj_projekt(p)
        if m is None:
            continue
        for j in range(2):
            sk = rng.uniform(0.97, 1.03, 3)
            m2 = m.copy()
            m2.apply_transform(np.diag([*sk, 1.0]))
            cel = kat / "stl" / "warianty" / f"wariant_{i:02d}_{j}{'_cad' if S.plik_exocad(p.name) else ''}.stl"
            m2.export(cel)
            dodaj(cel, float(rng.choice(WSPOLCZYNNIKI_ROZPRASZACZY)), "K-122")
    typy = list(AK.TYPY)
    atrapy_plytkowe = []
    n = 0
    while len(wpisy) < a.wpisow:
        n += 1
        plytkowa = len(atrapy_plytkowe) < ATRAP_PLYTKOWYCH
        if n % 25 == 0 and not plytkowa:
            m = AK.most(rng, punkty=int(rng.integers(2, 5)))
            zab = "most"
        else:
            t = typy[int(rng.integers(len(typy)))]
            W, L, H, g, amp = AK.TYPY[t]
            sk = rng.uniform(0.85, 1.15, 3)
            m = AK.korona(W * sk[0], L * sk[1], H * sk[2], g, amp, n_theta=128, n_u=160, rng=rng)
            zab = t
        cel = kat / "stl" / "atrapy" / f"atrapa_{n:03d}_{zab}.stl"
        m.export(cel)
        if plytkowa:  # atrapa, ktora moze trafic na plytke: na obu krazkach
            atrapy_plytkowe.append(cel)
            for w in KRAZKI:
                dodaj(cel, w, f"K-{round(w * 100)}")
        else:
            dodaj(cel, float(rng.choice(WSPOLCZYNNIKI_ROZPRASZACZY)), "K-122")
    wpisy = wpisy[: a.wpisow]
    zapisz_wpisy(kat / f"pula_{a.wpisow}.csv", wpisy)
    plytkowe = [str(p) for p in projekty] + [str(p) for p in atrapy_plytkowe]
    (kat / "plytkowe.json").write_text(json.dumps({"projekty": plytkowe, "wpisow": len(wpisy)}, ensure_ascii=False), encoding="utf-8")
    # plytki: prace z dwoch krazkow, scenariusz "dobrze", ubytki jak w ustawieniach
    (kat / "plytki").mkdir(exist_ok=True)
    ust = UST.wczytaj_ustawienia(a.ustawienia)
    for i in range(a.plytek):
        uk = U.wczytaj(UKLADY[i % len(UKLADY)], UST.katalog_plytki(ust, UKLADY[i % len(UKLADY)]))
        seed = 5000 + i
        op = S.Opcje.z_toml(ust, plytka=uk.nazwa, p_drgniecia=0.0, wspolczynnik=(min(KRAZKI), max(KRAZKI)), poza_uklad=True)
        rng_p = LosowanieKrazkow(np.random.default_rng(seed), KRAZKI)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            skan, prawda = S.generuj_plytke(uk, uk.numery[i % len(uk.numery)], [Path(p) for p in plytkowe], rng_p, op, seed)
        nazwa = f"skan_{uk.nazwa}_s{seed}"
        S.zapisz(skan, prawda, kat / "plytki", nazwa, nadpisz=True)
        print(f"{nazwa}: prac {len(prawda.prace)} (1,20: {sum(1 for x in prawda.prace if x.wspolczynnik < 1.225)}, "
              f"1,25: {sum(1 for x in prawda.prace if x.wspolczynnik > 1.225)})", flush=True)
    print(f"wpisow {len(wpisy)}, projektow (plikow) {len(pid)}, plytek {a.plytek}: {kat}")


# ----------------------------------------------------------------------------
# analiza plytki z pula wpisow
# ----------------------------------------------------------------------------
def wpisy_puli(kat: Path, wpisow: int) -> list[dict]:
    return PO.wczytaj_wpisy(kat / f"pula_{wpisow}.csv")


def plytki(kat: Path, limit: int | None = None) -> list[Path]:
    return sorted((kat / "plytki").glob("skan_*.stl"))[:limit]


def ocen_plytke(wynik: dict, prawda, wpisy: list[dict], skroty: dict) -> dict:
    """Kryteria na jednej plytce: top-1 projekt, top-1 wpis (frezowanie_id prawdy), status, prace cale z czerwonym."""
    praw = {p.gniazdo: p for p in prawda.prace}
    po_kluczu = {}
    for w in wpisy:
        po_kluczu.setdefault((skroty[w["plik"]], round(w["wspolczynnik"], 4)), []).append(w["frezowanie_id"])
    r = {"prac": 0, "top1_projekt": 0, "top1_wpis": 0, "zielone": 0, "wpis_niejednoznaczny": 0, "bledy": []}
    for g in wynik["gniazda"]:
        p = praw.get(g["gniazdo"])
        if p is None or g["status_fragmentu"] not in ("praca", "podwojny"):
            continue
        r["prac"] += 1
        k = g["kandydaci"][0] if g["kandydaci"] else {}
        ok_p = k.get("id") == p.projekt
        fids = po_kluczu.get((p.projekt, round(p.wspolczynnik, 4)), [])
        ok_w = ok_p and k.get("frezowanie_id") in fids
        r["top1_projekt"] += ok_p
        r["top1_wpis"] += ok_w
        r["zielone"] += g["status"] == "zielony"
        r["wpis_niejednoznaczny"] += ok_p and k.get("frezowanie_id") is None
        if not ok_w:
            r["bledy"].append({"gniazdo": g["gniazdo"], "prawda": p.projekt, "w": round(p.wspolczynnik, 4), "top1": k.get("id"), "w_top1": k.get("wspolczynnik"),
                               "frezowanie_id": k.get("frezowanie_id"), "pokrycie": k.get("pokrycie"), "status": g["status"]})
    return r


def _skroty(wpisy: list[dict]) -> dict:
    return {p: S.skrot_pliku(Path(p)) for p in {w["plik"] for w in wpisy}}


def czas(a) -> None:
    """Jeden proces: budowa puli z wpisow i analiza kolejnych plytek; czasy i szczyt pamieci."""
    ust = UST.wczytaj_ustawienia(a.ustawienia)
    if a.linie is not None:
        KR.ustaw_katalog_pamieci(a.linie)
    wpisy = wpisy_puli(a.katalog, a.wpisow)
    t0 = time.time()
    pam = PP.PamiecPuli(a.pamiec)
    pula = M.Pula.z_wpisow(wpisy, None, pamiec=pam)
    t_puli = time.time() - t0
    rek = {"wpisow": len(wpisy), "geometrii": len(pula), "czas_puli_s": round(t_puli, 2), "pamiec_po_puli_mb": pamiec_teraz_mb(),
           "statystyka_po_puli": dict(pam.statystyka), "liczniki": pula.liczniki, "plytki": []}
    print(f"pula: {len(wpisy)} wpisow, {len(pula)} geometrii, {t_puli:.1f} s, pamiec {rek['pamiec_po_puli_mb']} MB, {pam.statystyka}", flush=True)
    skroty = _skroty(wpisy)
    for p in plytki(a.katalog, a.plytek):
        prawda = S.wczytaj_prawde(p.with_suffix(".json"))
        przed = dict(pam.statystyka)
        t0 = time.time()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            wynik = PO.porownaj(p, [], PO.AUTO, ust, None, None, "auto", False, pula)
        t = time.time() - t0
        oc = ocen_plytke(wynik, prawda, wpisy, skroty)
        st = {k: pam.statystyka[k] - przed.get(k, 0) for k in pam.statystyka}
        rek["plytki"].append({"skan": p.name, "czas_s": round(t, 2), "czasy": wynik["czas_s"], "szczyt_mb": szczyt_pamieci_mb(), "pamiec_mb": pamiec_teraz_mb(),
                              "statystyka": st, **{k: v for k, v in oc.items() if k != "bledy"}, "bledy": oc["bledy"]})
        print(f"{p.name}: {t:.1f} s (plate {wynik['czas_s']['plate']}, match {wynik['czas_s']['match']}, inspect {wynik['czas_s']['inspect']}), "
              f"prac {oc['prac']}, top1 projekt {oc['top1_projekt']}, wpis {oc['top1_wpis']}, zielone {oc['zielone']}, szczyt {szczyt_pamieci_mb()} MB, {st}", flush=True)
    rek["szczyt_mb"] = szczyt_pamieci_mb()
    rek["statystyka"] = dict(pam.statystyka)
    a.wyjscie.mkdir(parents=True, exist_ok=True)
    (a.wyjscie / f"{a.nazwa}.json").write_text(json.dumps(rek, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"szczyt pamieci procesu {rek['szczyt_mb']} MB; {a.wyjscie / (a.nazwa + '.json')}")


# ----------------------------------------------------------------------------
# jakosc (kryteria 1 i 2) - procesy rownolegle
# ----------------------------------------------------------------------------
_STAN: dict = {}


def _init(pamiec, linie, plik_ust) -> None:
    if linie is not None:
        KR.ustaw_katalog_pamieci(linie)
    _STAN["ust"] = UST.wczytaj_ustawienia(plik_ust)
    _STAN["pamiec"] = PP.PamiecPuli(pamiec)


def _plytka_jakosc(arg) -> dict:
    p, wpisy_2, wpisy_inne, wpisow = arg
    ust, pam = _STAN["ust"], _STAN["pamiec"]
    prawda = S.wczytaj_prawde(p.with_suffix(".json"))
    skroty = _skroty(wpisy_2 + wpisy_inne)
    out = {"skan": p.name}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        # kryterium 2: pula z blizniakami (kazda praca plytki na obu krazkach)
        w2 = PO.porownaj(p, [], PO.AUTO, ust, None, None, "auto", False, M.Pula.z_wpisow(wpisy_2, None, pamiec=pam))
        out["k2"] = ocen_plytke(w2, prawda, wpisy_2, skroty)
        out["k2"]["czas_s"] = w2["czas_s"]
        # kryterium 1: prace plytki tylko ze swoim krazkiem + rozpraszacze (bez blizniakow) do `wpisow`
        na_plytce = {(x.projekt, round(x.wspolczynnik, 4)) for x in prawda.prace}
        sha_plytki = {x.projekt for x in prawda.prace}
        w1 = [w for w in wpisy_2 if (skroty[w["plik"]], round(w["wspolczynnik"], 4)) in na_plytce]
        reszta = [w for w in wpisy_2 + wpisy_inne if skroty[w["plik"]] not in sha_plytki]
        uzyte = set()
        for w in reszta:  # projekt spoza plytki tylko raz (jeden krazek)
            if skroty[w["plik"]] in uzyte:
                continue
            uzyte.add(skroty[w["plik"]])
            w1.append(w)
            if len(w1) >= wpisow:
                break
        w1r = PO.porownaj(p, [], PO.AUTO, ust, None, None, "auto", False, M.Pula.z_wpisow(w1, None, pamiec=pam))
        out["k1"] = ocen_plytke(w1r, prawda, w1, skroty)
        out["k1"]["wpisow"] = len(w1)
        out["k1"]["czas_s"] = w1r["czas_s"]
        cale = PO.metryki_inspekcji(w2, prawda)["razem"]
        out["k2"]["prace_cale"], out["k2"]["prace_cale_z_czerwonym"] = cale["prac_calych"], cale["prace_cale_z_czerwonym"]
    out["linia"] = (f"{p.name}: k2 prac {out['k2']['prac']} wpis {out['k2']['top1_wpis']} projekt {out['k2']['top1_projekt']} zielone {out['k2']['zielone']}; "
                    f"k1 ({out['k1']['wpisow']} wpisow) prac {out['k1']['prac']} wpis {out['k1']['top1_wpis']} projekt {out['k1']['top1_projekt']} zielone {out['k1']['zielone']}")
    return out


def jakosc(a) -> None:
    wpisy = wpisy_puli(a.katalog, a.wpisow)
    lista = plytki(a.katalog, a.plytek)
    zadania = [(p, wpisy, [], a.wpisow) for p in lista]
    wyniki = []
    with mp.Pool(a.procesy, initializer=_init, initargs=(a.pamiec, a.linie, a.ustawienia)) as pool:
        for r in pool.imap(_plytka_jakosc, zadania):
            print(r["linia"], flush=True)
            wyniki.append(r)
    zb = {}
    for k in ("k1", "k2"):
        zb[k] = {p: sum(r[k][p] for r in wyniki) for p in ("prac", "top1_projekt", "top1_wpis", "zielone", "wpis_niejednoznaczny")}
        zb[k]["bledy"] = [b for r in wyniki for b in r[k]["bledy"]]
    zb["k2"]["prace_cale"] = sum(r["k2"]["prace_cale"] for r in wyniki)
    zb["k2"]["prace_cale_z_czerwonym"] = sum(r["k2"]["prace_cale_z_czerwonym"] for r in wyniki)
    a.wyjscie.mkdir(parents=True, exist_ok=True)
    (a.wyjscie / f"{a.nazwa}.json").write_text(json.dumps({"plytki": wyniki, "zbiorczo": zb}, ensure_ascii=False, indent=1), encoding="utf-8")
    print("ZBIORCZO:", json.dumps({k: {p: v for p, v in d.items() if p != "bledy"} for k, d in zb.items()}, ensure_ascii=False))


# ----------------------------------------------------------------------------
# regresja R59 przez pule wpisow
# ----------------------------------------------------------------------------
def _skan_r59(arg) -> dict:
    p, projekty = arg
    ust, pam = _STAN["ust"], _STAN["pamiec"]
    prawda = S.wczytaj_prawde(p.with_suffix(".json"))
    w = float(np.mean([x.wspolczynnik for x in prawda.prace])) if prawda.prace else 1.0  # jak metryki_P3a
    pliki = [q for d in projekty for q in S.pliki_projektow(d)]
    wpisy = [{"plik": str(q), "wspolczynnik": w, "krazek": "K", "frezowanie_id": i + 1, "projekt_id": i + 1} for i, q in enumerate(pliki)]
    pula = M.Pula.z_wpisow(wpisy, None, pamiec=pam)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        wynik = PO.porownaj(p, [], prawda.plytka, ust, w, None, "auto", False, pula)
    if wynik.get("uklad_zgodny") is False:
        return {"skan": p.name, "niezgodny": True, "linia": f"{p.name}: UKLAD NIEZGODNY"}
    mt = PO.metryki(wynik, prawda, pula)
    mi = PO.metryki_inspekcji(wynik, prawda, pula)
    dobrze = mi["scenariusze"]["dobrze"]
    prac_dobrze = sum(1 for x in prawda.prace if PO.scenariusz(x) == "dobrze")
    rek = {"skan": p.name, "zestaw": p.parent.name, "wyrownanie_ok": mt["wyrownanie_ok"], "wyrownanie_mm": mt["wyrownanie"]["max_przesuniecie_mm"],
           "prac": mt["prac_prawda"], "top1": mt["top1"], "prac_dobrze": prac_dobrze, "top1_bledny_dobrze": dobrze["top1_bledny"],
           "prace_cale": mi["razem"]["prac_calych"], "prace_cale_z_czerwonym": mi["razem"]["prace_cale_z_czerwonym"],
           "prace_cale_z_alarmem": mi["razem"]["prace_cale_z_alarmem"], "ubytkow": mi["razem"]["ubytkow"], "wykryte_dowolny": mi["razem"]["wykryte"]["dowolny"],
           "statusy_gniazd": wynik["statusy_gniazd"], "statusy_match": mt["statusy"], "czas_s": wynik["czas_s"],
           "gniazda": [{"gniazdo": g["gniazdo"], "status": g["status"], "status_gniazda": g["status_gniazda"],
                        "projekt": (g["kandydaci"][0]["id"] if g["kandydaci"] else None),
                        "projekt_prawda": next((x.projekt for x in prawda.prace if x.gniazdo == g["gniazdo"]), None),
                        "scenariusz": next((PO.scenariusz(x) for x in prawda.prace if x.gniazdo == g["gniazdo"]), None)} for g in wynik["gniazda"]]}
    rek["linia"] = (f"{p.name}: wyr {rek['wyrownanie_mm']:.4f} top1 {rek['top1']}/{rek['prac']} dobrze bledne {rek['top1_bledny_dobrze']}/{prac_dobrze} "
                    f"cale z czerwonym {rek['prace_cale_z_czerwonym']}/{rek['prace_cale']} {wynik['czas_s']['razem']} s")
    return rek


def r59(a) -> None:
    skany = sorted(q for d in a.skany for q in d.glob("skan_*.stl"))[: a.limit]
    t0 = time.time()
    wyniki = []
    with mp.Pool(a.procesy, initializer=_init, initargs=(a.pamiec, a.linie, a.ustawienia)) as pool:
        for r in pool.imap(_skan_r59, [(q, tuple(a.projekty)) for q in skany]):
            print(r["linia"], flush=True)
            wyniki.append(r)
    ok = [r for r in wyniki if not r.get("niezgodny")]
    zb = {"skanow": len(wyniki), "uklad_niezgodny": len(wyniki) - len(ok), "wyrownanie_ok": sum(r["wyrownanie_ok"] for r in ok),
          "wyrownanie_max_mm": max(r["wyrownanie_mm"] for r in ok), "prac": sum(r["prac"] for r in ok), "top1": sum(r["top1"] for r in ok),
          "prac_dobrze": sum(r["prac_dobrze"] for r in ok), "top1_bledny_dobrze": sum(r["top1_bledny_dobrze"] for r in ok),
          "prace_cale": sum(r["prace_cale"] for r in ok), "prace_cale_z_czerwonym": sum(r["prace_cale_z_czerwonym"] for r in ok),
          "prace_cale_z_alarmem": sum(r["prace_cale_z_alarmem"] for r in ok), "ubytkow": sum(r["ubytkow"] for r in ok),
          "wykryte_dowolny": sum(r["wykryte_dowolny"] for r in ok),
          "statusy_gniazd": {s: sum(r["statusy_gniazd"][s] for r in ok) for s in PO.STATUSY_GNIAZDA},
          "statusy_match": {s: sum(r["statusy_match"][s] for r in ok) for s in M.STATUSY}, "czas_calosci_s": round(time.time() - t0, 1)}
    zb["top1_dobrze"] = zb["prac_dobrze"] - zb["top1_bledny_dobrze"]
    a.wyjscie.mkdir(parents=True, exist_ok=True)
    (a.wyjscie / f"{a.nazwa}.json").write_text(json.dumps({"skany": wyniki, "zbiorczo": zb}, ensure_ascii=False, indent=1), encoding="utf-8")
    print("ZBIORCZO:", json.dumps(zb, ensure_ascii=False))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="tryb", required=True)
    for nazwa in ("przygotuj", "czas", "jakosc", "r59"):
        s = sub.add_parser(nazwa)
        s.add_argument("--ustawienia", type=Path, default=None)
        s.add_argument("--wpisow", type=int, default=400)
        s.add_argument("--plytek", type=int, default=None if nazwa != "przygotuj" else 10)
        s.add_argument("--pamiec", type=Path, default=None, help="katalog pamieci podrecznej projektow (pusty = pamiec zimna)")
        s.add_argument("--linie", type=Path, default=None, help="katalog pamieci linii brzegu (krawedz) - jak [silnik] pamiec_linii")
        s.add_argument("--procesy", type=int, default=1)
        s.add_argument("--nazwa", default=f"metryki_pula_{nazwa}")
        s.add_argument("--seed", type=int, default=1)
        s.add_argument("--limit", type=int, default=None)
        if nazwa in ("przygotuj", "r59"):
            s.add_argument("--projekty", type=Path, nargs="+", required=True)
        if nazwa == "r59":
            s.add_argument("--skany", type=Path, nargs="+", required=True)
            s.add_argument("--wyjscie", type=Path, required=True)
        else:
            s.add_argument("--katalog", type=Path, required=True)
            s.add_argument("--wyjscie", type=Path, default=None)
    a = ap.parse_args()
    if getattr(a, "wyjscie", None) is None:
        a.wyjscie = a.katalog / "wyniki"
    {"przygotuj": przygotuj, "czas": czas, "jakosc": jakosc, "r59": r59}[a.tryb](a)


if __name__ == "__main__":
    main()
