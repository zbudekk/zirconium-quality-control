"""Proby sesji S3 (analiza kodu 23.11.2026) - tylko odczyt kodu programu, dane w katalogu tymczasowym.

Uruchomienie (z katalogu Ramki\\stanowisko worktree analiza-s3, 1 proces python):
  <PC-katalog>\\koordynator\\narz\\py.cmd ..\\analiza_kodu_2026-11-23\\S3\\proba_s3.py > ..\\analiza_kodu_2026-11-23\\S3\\proba_s3_wynik.txt
Proby: P1 statusy (tabela decyzyjna), P2 session (ponowny skan a czerwone bez decyzji; OK na czerwonym),
P3 kalibracja ramek z geometrii, P4 logika ramki (pierscien, waznosc planu).
"""
from __future__ import annotations

import copy
import datetime as dt
import itertools
import json
import sys
import tempfile
from pathlib import Path

TU = Path.cwd()
sys.path.insert(0, str(TU))

from ramka import kalibracja as KAL  # noqa: E402
from ramka import obraz as OBR  # noqa: E402
from ramka.logika import LogikaRamki  # noqa: E402
from stanowisko import baza as B  # noqa: E402
from stanowisko import ramka_protokol as RP  # noqa: E402
from stanowisko import session as SE  # noqa: E402
from stanowisko import statusy as ST  # noqa: E402


def naglowek(t: str) -> None:
    print()
    print("=" * 100)
    print(t)
    print("=" * 100)


# ------------------------------------------------------------------------------------------------ P1
def p1() -> None:
    naglowek("P1 statusy.status_pracy / kolor_pracy / kolor_ramki - pelna tabela decyzyjna")
    kolory = (None, "zielony", "czerwony", "zolty", "szary", "pomaranczowy", "zatwierdzona_ok", "xyz", "")
    skany = ("przyjety", "do_powtorzenia", "zastapiony", "blad", "niezgodny_uklad", "plytka_nie_z_trybu", "xyz")
    insp = (None, "ok", "ubytek", "sprawdz", "nie_sprawdzono", "pominieto", "skan_ponownie", "popraw_ulozenie", "sprawdz_ulozenie",
            "poprawka", "xyz", "")
    decyzje = (None, "ok", "ukruszona", "ukruszona_niewykryta", "xyz")
    mecze = (None, "zielony", "zolty", "szary", "brak", "xyz")
    n = 0
    zielone: dict = {}
    wyjatki = 0
    for k, s, i, d, m, numer, blad in itertools.product(kolory, skany, insp, decyzje, mecze, (True, False), (True, False)):
        n += 1
        try:
            klucz = ST.status_pracy(k, status_skanu=s, status_inspekcji=i, decyzja=d, blad_inspekcji=blad, numer_znany=numer, status_match=m,
                                    status_gniazda=k if k in ("zielony", "czerwony", "zolty", "szary", "pomaranczowy") else None)
            kp = ST.kolor_pracy(k, klucz)
            ramka = RP.kolor_ramki(klucz)
        except Exception as e:  # noqa: BLE001
            wyjatki += 1
            print("WYJATEK", type(e).__name__, (k, s, i, d, m, numer, blad))
            continue
        if ramka == "zielony" or kp in ("zielony", "zatwierdzona_ok") or klucz in ("zielony", "zatwierdzona_ok"):
            zielone.setdefault((klucz, kp, ramka), []).append((k, s, i, d, m, numer, blad))
    print(f"kombinacji: {n}, wyjatkow: {wyjatki}")
    for (klucz, kp, ramka), lista in sorted(zielone.items(), key=str):
        print(f"\nstatus={klucz!r} kolor_pracy={kp!r} ramka={ramka!r}: {len(lista)} kombinacji")
        for nazwa, idx in (("kolor z sesji", 0), ("status_skanu", 1), ("status_inspekcji", 2), ("decyzja", 3), ("status_match", 4),
                           ("numer_znany", 5), ("blad_inspekcji", 6)):
            print(f"   {nazwa:17s}: {sorted({x[idx] for x in lista}, key=str)}")
    print("\nStatusy, ktorych kolumna 'ramka' = zielony (wszystkie wiersze tabeli, takze poranne):")
    for w in list(ST.STATUSY.values()) + list(ST.STATUSY_RANO_WIERSZE.values()):
        if w.ramka == "zielony":
            print(f"   {w.klucz:18s} kolor={w.kolor!r:20s} rgb={w.hex} napis={w.napis!r}")
    print("\nstatus(None / '' / nieznany) ->", ST.status(None).klucz, ST.status("").klucz, ST.status("cos_nowego").klucz,
          "| ramka:", RP.kolor_ramki(None), RP.kolor_ramki("cos_nowego"))
    print("status_rano(None / nieznana) ->", ST.status_rano(None).klucz, ST.status_rano("cos").klucz)
    print("kolory ramki ze statusow spoza protokolu ramki:",
          sorted({w.ramka for w in list(ST.STATUSY.values()) + list(ST.STATUSY_RANO_WIERSZE.values()) if w.ramka} - set(RP.KOLORY)))


# ------------------------------------------------------------------------------------------------ P2
class Zegar:
    def __init__(self, start: str = "2026-11-17T19:00:00"):
        self.t = dt.datetime.fromisoformat(start)

    def __call__(self) -> dt.datetime:
        self.t += dt.timedelta(seconds=1)
        return self.t


def p2() -> None:
    naglowek("P2 session: ponowny skan a praca czerwona BEZ decyzji; 'OK' na czerwonej -> kolor ramki")
    dane = TU / "testy" / "dane_sesji"
    zd = json.loads((dane / "zdarzenia.json").read_text(encoding="ascii"))
    a = json.loads((dane / "wynik_plytka1.json").read_text(encoding="ascii"))
    b = json.loads((dane / "wynik_plytka1_ponownie.json").read_text(encoding="ascii"))
    b = copy.deepcopy(b)
    for g in b["gniazda"]:  # drugi skan tych samych prac: gniazdo 2 (w skanie A czerwone) wychodzi zielone
        if g["gniazdo"] == 2:
            g["inspekcja"]["status"] = "ok"
            g["inspekcja"]["ubytki"] = []
            g["status_gniazda"] = "zielony"
    with tempfile.TemporaryDirectory(prefix="tmp_proba_", dir=str(Path(__file__).resolve().parent)) as kat:  # tylko w <PC-katalog>
        kat = Path(kat)
        baza = B.otworz(kat / "dane" / "stanowisko.sqlite")
        try:
            s = SE.Sesja(baza, operatorzy=["Technik A"], katalog_wynikow=kat / "dane" / "wyniki", zegar=Zegar())
            s.wybierz_operatora("Technik A")
            id_a = s.przyjmij_wynik(zd["wynik_plytka1"], a)
            id_b = s.przyjmij_wynik({**zd["wynik_plytka1"], "sha16": "0000000000000001", "plik": "C:/Skany/drugi.stl"}, b)
            st = s.stan_wieczoru()

            def kolory(skan_id: int, stan: dict) -> dict:
                sk = next(x for x in stan["skany"] if x["id"] == skan_id)
                return {p["gniazdo"]: (p["kolor"], p["decyzja"]) for p in sk["prace"]}

            print("skan A (pierwszy), gniazdo -> (kolor, decyzja):", kolory(id_a, st))
            print("skan B (ponowny),  gniazdo -> (kolor, decyzja):", kolory(id_b, st))
            dp = st["do_potwierdzenia"]
            print("do_potwierdzenia:", [{k: v for k, v in x.items() if k != "decyzje"} for x in dp])
            print("pola wpisu do_potwierdzenia:", sorted(dp[0]) if dp else None)
            n = dp[0]["liczba_decyzji"] if dp else None
            skutek = ST.SKUTEK_BEZ_DECYZJI if n == 0 else "(z decyzjami)"
            print("tekst pytania dla technika:", ST.tekst_pytania("ponowny_skan", numer=1, minut=0, skutek=skutek)[2].encode("ascii", "replace").decode())
            czerwone_a = {g for g, (k, d) in kolory(id_a, st).items() if k == "czerwony" and d is None}
            zielone_b = {g for g, (k, d) in kolory(id_b, st).items() if k == "zielony"}
            print("czerwone bez decyzji w A:", sorted(czerwone_a), "| z nich zielone w B:", sorted(czerwone_a & zielone_b))
            s.zastap_skan(id_b)
            st2 = s.stan_wieczoru()
            print("po 'Tak, to ponowny skan': status A =", next(x["status"] for x in st2["skany"] if x["id"] == id_a),
                  "| kolory A:", kolory(id_a, st2), "| kolory B:", kolory(id_b, st2), "| liczniki doby:", st2["liczniki"])
            wpisy = baza.wiersze("SELECT zrodlo, typ, dane FROM zdarzenia WHERE skan_id IN (?, ?) ORDER BY id", (id_a, id_b))
            print("dziennik zdarzen obu skanow (typy):", [w["typ"] for w in wpisy])
            # 'OK' na czerwonej pracy gniazda 3 skanu B
            pid = baza.wiersz("SELECT id FROM prace WHERE skan_id = ? AND gniazdo = 3", (id_b,))["id"]
            s.ok(pid)
            st3 = s.stan_wieczoru()
            k3, d3 = kolory(id_b, st3)[3]
            klucz = ST.status_pracy(k3, status_skanu="przyjety", status_gniazda="czerwony", status_inspekcji="ubytek", decyzja=d3, status_match="zielony")
            w = ST.status(klucz)
            print(f"gniazdo 3 po 'OK' na czerwonym: kolor sesji={k3!r}, status={klucz!r}, napis={w.napis.encode('ascii', 'replace').decode()!r}, "
                  f"rgb ekranu={w.hex}, kolor diod ramki={RP.kolor_ramki(klucz)!r} (zwykly zielony: rgb {ST.status('zielony').hex}, ramka "
                  f"{RP.kolor_ramki('zielony')!r})")
        finally:
            baza.zamknij()


# ------------------------------------------------------------------------------------------------ P3
def p3() -> dict:
    naglowek("P3 kalibracja ramek z geometrii (ramka.kalibracja.domyslna) - uklady, bloki, odstepy")
    modele = TU / "modele_plytek"
    kal = KAL.domyslna(modele)
    for rola in ("W", "P"):
        for nazwa, wpis in sorted(kal["ramki"][rola].items()):
            print(f"ramka {rola}: uklad {nazwa:28s} gniazd {len(wpis['gniazda']):2d} zrodlo {wpis['zrodlo']}")
    wszystkie = sorted(p.parent.name for p in modele.glob("*/uklad.json"))
    z_kal = {n for r in kal["ramki"].values() for n in r}
    print("uklady BEZ kalibracji (ramka ciemna):", [n for n in wszystkie if n not in z_kal])
    for rola, okr, kw in (("W", "okragla_ramkowa_wieczorna", "wieczorna"), ("P", "okragla_ramkowa_poranna", "poranna")):
        a, b = kal["ramki"][rola][okr]["gniazda"], kal["ramki"][rola][kw]["gniazda"]
        print(f"{okr} == {kw} (bloki): {a == b} ({sum(1 for k in a if a[k] == b.get(k))} z {len(a)})")
    for nazwa in ("okragla_ramkowa_wieczorna", "okragla_ramkowa_poranna"):
        uk = json.loads((modele / nazwa / "uklad.json").read_text(encoding="utf-8"))
        rola = KAL.rola_ukladu(uk)
        bloki = kal["ramki"][rola][nazwa]["gniazda"]
        pol = uk["d"] / 2
        maks_przes, poza_kolem, stykajace = 0.0, [], []
        for g in uk["sockets"]:
            x, y, w, h = bloki[str(g["id"])]
            sx = (x + w / 2 - OBR.SZEROKOSC / 2) * OBR.RASTER_MM
            sy = (OBR.WYSOKOSC / 2 - (y + h / 2)) * OBR.RASTER_MM
            maks_przes = max(maks_przes, ((sx - g["x"]) ** 2 + (sy - g["y"]) ** 2) ** 0.5)
            rogi = [((xx - 32) * 2.5, (32 - yy) * 2.5) for xx in (x, x + w) for yy in (y, y + h)]
            if any((rx * rx + ry * ry) ** 0.5 > pol for rx, ry in rogi):
                poza_kolem.append(g["id"])
        ids = sorted(bloki, key=int)
        for i, j in itertools.combinations(ids, 2):
            x1, y1, w1, h1 = bloki[i]
            x2, y2, w2, h2 = bloki[j]
            dx = max(x2 - (x1 + w1), x1 - (x2 + w2), 0)
            dy = max(y2 - (y1 + h1), y1 - (y2 + h2), 0)
            if dx == 0 and dy == 0:
                stykajace.append((int(i), int(j)))
        print(f"{nazwa}: d={uk['d']} mm, flat={uk['flat']['angle_deg']} st., srodek bloku a srodek gniazda - maks. {maks_przes:.2f} mm; "
              f"bloki z rogiem poza kolem plytki: {poza_kolem}; pary gniazd o blokach stykajacych sie (0 px przerwy): {stykajace}")
    return kal


# ------------------------------------------------------------------------------------------------ P4
def p4(kal: dict) -> None:
    naglowek("P4 logika ramki: pierscien stanu przy czerwonych gniazdach, plan bez gniazd, waznosc planu bez laptopa")

    def scena(rola: str, plytka: int, plan: dict, opis: str, czasy: tuple) -> None:
        lg = LogikaRamki(rola, start_id="abcd1234", teraz=0.0)
        lg.ustaw_plytke(plytka, 0.1)
        plan = dict(plan, start_id="abcd1234", zdarzenia_do=lg.nr)
        odp = lg.przyjmij_plan(plan, "lap-1", 1.0)
        print(f"\n[{opis}] plan: {odp['wynik']}, wazny_s={odp['wazny_s']}")
        for t in czasy:
            lg.tick(t)
            k = lg.obraz(t)
            zap = k.zapalone()
            w_plytce = {xy: c for xy, c in zap.items() if OBR.w_obszarze_plytki(*xy)}
            barwy = {}
            for c in w_plytce.values():
                nazwa = next((n for n, v in OBR.KOLORY.items() if v == c), str(c))
                barwy[nazwa] = barwy.get(nazwa, 0) + 1
            print(f"   t={t:6.1f} s (ostatni kontakt laptopa t=1.0): tryb={lg.tryb:8s} pierscien(0,0)={k.piksel(0, 0)} "
                  f"lacznosc={lg.lacznosc(t)} piksele gniazd={barwy or '-'}")

    w1, _ = RP.plan_wieczor({2: ("okragla_ramkowa_wieczorna", {1: "czerwony", 5: "czerwony", 7: "zielony"})}, kal, plan_id="w-proba",
                            wersja=1, start_id="abcd1234", zdarzenia_do=0)
    scena("W", 2, w1, "W: plytka 2, gniazda 1 i 5 czerwone, 7 zielone", (1.5, 29.0, 30.9, 31.5))
    w2, _ = RP.plan_wieczor({2: ("okragla_ramkowa_wieczorna", {1: None, 5: None})}, kal, plan_id="w-proba2", wersja=1, start_id="abcd1234",
                            zdarzenia_do=0)
    print("\nplan wieczorny, w ktorym zadne gniazdo nie ma koloru:", json.dumps(w2["plytki"]))
    scena("W", 2, w2, "W: plytka 2, plan bez swiecacych gniazd", (1.5,))
    plan_plytek = {"plan_id": "2026-11-18-p1", "plytki": {"4": {"gniazda": [{"id": 1, "kolor": "zielony", "kuweta": "3263"},
                                                                          {"id": 2, "kolor": "czerwony"}]}},
                   "kuwety": [{"kuweta": "3263", "plytki": [4]}], "braki": [], "uklady": {"4": "okragla_ramkowa_poranna"}}
    p1_, pom = RP.plan_rano(plan_plytek, kal, wersja=1, start_id="abcd1234", zdarzenia_do=0)
    print("\nplan poranny pominiete:", pom)
    scena("P", 4, p1_, "P: plytka 4, gniazdo 1 zielone (kuweta 3263), gniazdo 2 'sprawdz'", (1.5, 300.0, 600.5, 601.5))


if __name__ == "__main__":
    p1()
    p2()
    p4(p3())
    print("\nKONIEC PROB")
