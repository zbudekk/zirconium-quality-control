"""ramka_proba.py - proba ramki swietlnej z komputera, bez programu "Stanowisko" (narzedzie dnia sprzetu, E3-S1).

Po co: program "Stanowisko" zapala gniazda dopiero po skanie z pracami. To narzedzie pozwala sprawdzic sama ramke:
czy odpowiada w sieci, jaki numer plytki czyta (z zapisem kazdej zmiany do pliku), czy swieca wszystkie diody i czy
blok diod trafia pod wlasciwe gniazdo (kalibracja gniazdo -> diody), gniazdo po gniazdzie.

Programu nie zmienia: z programu importuje tylko `ramka.kalibracja` (polozenia blokow diod); z ramka rozmawia
protokolem v1 z `ramka/README.md` (HTTP, biblioteka standardowa). Sprawdzone WYLACZNIE na atrapie ramki
(test obok: test_ramka_proba.py). Przed uzyciem ZAMKNIJ program "Stanowisko" (ramke obsluguje jeden komputer naraz).

Uzycie - z instalacji programu (kazde polecenie w jednej linii; ADRES = nazwa albo adres IP ramki):
    C:\\Stanowisko\\Polecenie.cmd C:\\sciezka\\ramka_proba.py stan     --adres ADRES
    C:\\Stanowisko\\Polecenie.cmd C:\\sciezka\\ramka_proba.py plytki   --adres ADRES --czas 300 --zapis C:\\sciezka\\plytki.csv
    C:\\Stanowisko\\Polecenie.cmd C:\\sciezka\\ramka_proba.py test-led --adres ADRES
    C:\\Stanowisko\\Polecenie.cmd C:\\sciezka\\ramka_proba.py gniazda  --adres ADRES --uklad wieczorna --zapis C:\\sciezka\\gniazda.csv
    C:\\Stanowisko\\Polecenie.cmd C:\\sciezka\\ramka_proba.py klawiatura --adres ADRES --uklad poranna --czas 120 --zapis C:\\sciezka
Opcje wspolne: --port 8765, --klucz KLUCZ (gdy ramka ma klucz w konfiguracji).
`gniazda`: --wszystkie (wszystkie gniazda naraz, 4 kolory na zmiane) albo domyslnie po kolei (Enter = nastepne, mozna
wpisac uwage, k = koniec); --przesun DX DY przesuwa wszystkie bloki o tyle diod (w prawo, w dol) - do proby poprawki;
--kalibracja PLIK (domyslnie polozenia startowe z geometrii plytek); --modele KATALOG (domyslnie modele_plytek programu).
`klawiatura` (tylko ramka poranna, plytka 4-6 lezy na ramce): wysyla plan z dwiema kuwetami probnymi 1111 i 2222
i wypisuje kazde zdarzenie klawiatury ramki (Enter, Backspace, cyfry + Enter, * + Enter).
Kody wyjscia: 0 = wykonano, 1 = ramka odmowila albo czegos brakuje, 2 = brak polaczenia z ramka.
"""
from __future__ import annotations

import argparse
import csv
import json
import secrets
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))  # katalog programu (instalacja: Polecenie.cmd ustawia go jako biezacy)

LAPTOP_ID = "proba-sprzetu-s1"
KOLORY_NA_ZMIANE = ("zielony", "czerwony", "niebieski", "zolty")
RODZINY = {"W": (1, 2, 3), "P": (4, 5, 6)}


class BrakPolaczenia(Exception):
    pass


class Ramka:
    """Klient HTTP ramki (protokol v1). Kazde zadanie z naglowkiem X-Laptop-Id i - gdy podano - X-Ramka-Klucz."""

    def __init__(self, adres: str, port: int = 8765, klucz: str = "", limit_s: float = 5.0):
        self.baza = f"http://{adres}:{port}"
        self.klucz, self.limit_s = klucz, limit_s

    def zadanie(self, metoda: str, trasa: str, dane=None, limit_s: float | None = None) -> tuple[int, dict]:
        tresc = None if dane is None else json.dumps(dane).encode("utf-8")
        z = urllib.request.Request(self.baza + trasa, data=tresc, method=metoda)
        z.add_header("X-Laptop-Id", LAPTOP_ID)
        if self.klucz:
            z.add_header("X-Ramka-Klucz", self.klucz)
        if tresc is not None:
            z.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(z, timeout=limit_s or self.limit_s) as o:
                return o.status, json.loads(o.read().decode("utf-8") or "{}")
        except urllib.error.HTTPError as e:
            try:
                return e.code, json.loads(e.read().decode("utf-8") or "{}")
            except ValueError:
                return e.code, {}
        except (urllib.error.URLError, OSError) as e:
            raise BrakPolaczenia(f"{type(e).__name__}: {getattr(e, 'reason', e)}") from None

    def stan(self) -> dict:
        kod, s = self.zadanie("GET", "/stan")
        if kod == 401:
            raise BrakPolaczenia("ramka wymaga klucza (odpowiedz 401) - podaj --klucz taki jak w pliku konfiguracji ramki")
        if kod != 200:
            raise BrakPolaczenia(f"ramka odpowiedziala kodem {kod}")
        return s

    def zdarzenia(self, start_id: str, od: int, czekaj: float = 0.0) -> dict:
        kod, o = self.zadanie("GET", f"/zdarzenia?od={od}&czekaj={czekaj:g}&start_id={start_id}&limit=500", limit_s=czekaj + self.limit_s)
        if kod != 200:
            raise BrakPolaczenia(f"/zdarzenia: kod {kod}")
        return o

    def wyslij_plan(self, plan_id: str, wersja: int, rola: str, nr_plytki: int, gniazda: list) -> tuple[int, dict, int]:
        """Plan z jedna plytka; przy 409 `zdarzenia_nieodebrane` (ramka zglosila cos w miedzyczasie) ponawia z nowa wersja."""
        kod, o = 0, {}
        for _ in range(4):
            s = self.stan()
            plan = {"protokol": 1, "plan_id": plan_id, "wersja": wersja, "start_id": s["start_id"], "zdarzenia_do": s["nr_zdarzenia"],
                    "wazny_s": 600 if rola == "P" else 30, "tryb": "rano" if rola == "P" else "wieczor",
                    "plytki": {str(nr_plytki): {"gniazda": gniazda}}}
            kod, o = self.zadanie("PUT", "/plan", plan)
            if kod == 200:
                break
            blad = (o.get("blad") or {}).get("kod")
            wersja = max(wersja, int(o.get("wersja_ramki") or 0)) + 1
            if blad not in ("zdarzenia_nieodebrane", "plan_starszy", "konflikt_wersji", "plan_zgaszony"):
                break
        return kod, o, wersja


def _godzina() -> str:
    t = time.time()
    return time.strftime("%H:%M:%S", time.localtime(t)) + f".{int(t * 1000) % 1000:03d}"


def _zapisz_csv(plik: Path | None, naglowek: list, wiersze: list, przedrostek: str = "ramka") -> Path | None:
    """Zapis obserwacji; gdy `plik` jest katalogiem - nowy plik <przedrostek>_<data>_<godzina>.csv w tym katalogu."""
    if plik is None:
        return None
    if plik.is_dir():
        plik = plik / f"{przedrostek}_{time.strftime('%Y%m%d_%H%M%S')}.csv"
    plik.parent.mkdir(parents=True, exist_ok=True)
    with open(plik, "w", encoding="ascii", errors="replace", newline="") as f:
        w = csv.writer(f, delimiter=";", lineterminator="\n")
        w.writerow(naglowek)
        w.writerows(wiersze)
    return plik


# ----------------------------------------------------------------------------- polecenia
def polecenie_stan(r: Ramka, pisz=print) -> int:
    t0 = time.perf_counter()
    s = r.stan()
    ms = (time.perf_counter() - t0) * 1000
    rola = {"W": "wieczorna (W)", "P": "poranna (P)"}.get(s.get("rola"), str(s.get("rola")))
    pisz(f"RAMKA ODPOWIADA ({ms:.0f} ms): ramka {rola}, program ramki {s.get('program')}, dziala od {s.get('czas_s', 0):.0f} s")
    pisz(f"  plytka na ramce: {s.get('plytka')} (0 = brak plytki)" + ("" if s.get("plytka_pewna") else " - odczyt NIEPEWNY (drga)"))
    pisz(f"  stan: {s.get('tryb')}; blad sprzetu: {'TAK' if s.get('blad_sprzetu') else 'nie'}; temperatura: {s.get('temp_c')} st. C")
    pisz(f"  numery plytek tej ramki: {', '.join(str(n) for n in RODZINY.get(s.get('rola'), ()))}")
    return 0


def polecenie_plytki(r: Ramka, czas_s: float, zapis: Path | None, pisz=print, stop: threading.Event | None = None) -> int:
    """Zapis kazdej zmiany odczytu plytki (zdarzenia ramki; tylko odczyt - nie przejmuje ramki)."""
    s = r.stan()
    start_id, od = s["start_id"], s["nr_zdarzenia"]
    rodzina = RODZINY.get(s.get("rola"), ())
    pisz(f"Ramka {s.get('rola')}: teraz plytka {s.get('plytka')}. Kladz i zdejmuj plytki; kazda zmiana pojawi sie ponizej. Koniec po {czas_s:.0f} s albo Ctrl+C.")
    wiersze, t_koniec = [], time.time() + czas_s
    try:
        while time.time() < t_koniec and not (stop is not None and stop.is_set()):
            o = r.zdarzenia(start_id, od, czekaj=min(2.0, max(0.0, t_koniec - time.time())))
            if o.get("restart"):
                start_id, od = o["start_id"], 0
                pisz(f"{_godzina()}  RAMKA URUCHOMILA SIE PONOWNIE (restart programu ramki)")
                wiersze.append([_godzina(), "", "restart", "", "", ""])
                continue
            for z in o.get("zdarzenia", []):
                od = max(od, z["nr"])
                if z.get("typ") == "plytka":
                    n, pop = z.get("plytka"), z.get("poprzednia")
                    uwaga = "" if n == 0 or n in rodzina else "NUMER SPOZA TEJ RAMKI"
                    pisz(f"{_godzina()}  plytka {pop} -> {n}   (czas ramki {z.get('czas_s', 0):.3f} s) {uwaga}")
                    wiersze.append([_godzina(), f"{z.get('czas_s', 0):.3f}", "plytka", pop, n, uwaga])
                elif z.get("typ") in ("blad_sprzetu", "sprzet_dziala", "start"):
                    pisz(f"{_godzina()}  zdarzenie ramki: {z.get('typ')}")
                    wiersze.append([_godzina(), f"{z.get('czas_s', 0):.3f}", z.get("typ"), "", "", ""])
            od = max(od, 0)
    except KeyboardInterrupt:
        pass
    finally:
        zapis = _zapisz_csv(zapis, ["godzina_komputera", "czas_ramki_s", "zdarzenie", "poprzednia", "plytka", "uwaga"], wiersze, "plytki")
    zmian = sum(w[2] == "plytka" for w in wiersze)
    pisz(f"Zmian odczytu plytki: {zmian}" + (f"; zapisano {zapis}" if zapis else ""))
    return 0


def polecenie_test_led(r: Ramka, pisz=print) -> int:
    kod, o = r.zadanie("PUT", "/tryb", {"protokol": 1, "stan": "test_led"})
    if kod != 200:
        pisz(f"RAMKA ODMOWILA testu diod: kod {kod} {(o.get('blad') or {}).get('kod', '')}"
             + (" - ramke obsluguje teraz inny komputer (zamknij program Stanowisko)" if (o.get("blad") or {}).get("kod") == "inny_laptop" else ""))
        return 1
    pisz("TEST DIOD WYSLANY: cala matryca ma swiecic kolejno na czerwono, zielono, niebiesko i bialo (po ok. 1 s), razem 8 s.")
    return 0


def bloki_ukladu(kal: dict, rola: str, uklad: str, przesun=(0, 0)) -> list:
    """[(id gniazda, [x, y, szer, wys])] ukladu z kalibracji, przesuniete o (dx, dy) diod."""
    gn = kal["ramki"][rola][uklad]["gniazda"]
    return [(int(g), [gn[g][0] + przesun[0], gn[g][1] + przesun[1], gn[g][2], gn[g][3]]) for g in sorted(gn, key=int)]


def polecenie_gniazda(r: Ramka, uklad: str, kalibracja: Path | None, modele: Path, wszystkie: bool, przesun: tuple, zapis: Path | None,
                      pisz=print, pytaj=input, plytka: int | None = None) -> int:
    from ramka import kalibracja as K

    s = r.stan()
    rola = s["rola"]
    kal = K.wczytaj(kalibracja) if kalibracja else K.domyslna(modele)
    if uklad not in kal["ramki"].get(rola, {}):
        pisz(f"BRAK ukladu '{uklad}' dla ramki {rola} w kalibracji. Sa: {', '.join(sorted(kal['ramki'].get(rola, {}))) or 'zadne'}.")
        return 1
    nr = plytka if plytka is not None else s.get("plytka")
    if nr not in RODZINY[rola]:
        pisz(f"NA RAMCE NIE LEZY PLYTKA TEJ RAMKI (odczyt: {s.get('plytka')}; ramka {rola} przyjmuje numery {RODZINY[rola]}). "
             "Poloz plytke i uruchom ponownie - ramka zapala gniazda tylko pod plytka, ktorej numer czyta.")
        return 1
    try:
        bloki = bloki_ukladu(kal, rola, uklad, przesun)
        K.sprawdz({"wersja": kal["wersja"], "matryca": kal["matryca"], "ramki": {rola: {uklad: {"gniazda": {str(g): b for g, b in bloki}}}}})
    except K.BladKalibracji as e:
        pisz(f"PRZESUNIECIE {przesun} wychodzi poza plytke albo bloki sie nakladaja: {e}")
        return 1
    plan_id, wersja = f"proba-{time.strftime('%H%M%S')}-{secrets.token_hex(3)}", 1  # nowy przy kazdym uruchomieniu
    zrodlo = kal["ramki"][rola][uklad].get("zrodlo", "geometria")
    pisz(f"Ramka {rola}, plytka {nr}, uklad {uklad} ({len(bloki)} gniazd), polozenia diod: {zrodlo}, przesuniecie {przesun[0]} w prawo, {przesun[1]} w dol.")
    wiersze, kod_wyjscia = [], 0
    zyje = threading.Event()

    def podtrzymuj():  # ramka gasi plan, gdy komputer milczy (wieczorna po 30 s) - odzywamy sie co 5 s
        while not zyje.wait(5.0):
            try:
                r.zadanie("GET", "/stan")
            except BrakPolaczenia:
                pass

    watek = threading.Thread(target=podtrzymuj, daemon=True)
    watek.start()
    try:
        if wszystkie:
            gniazda = [{"id": g, "px": b, "kolor": KOLORY_NA_ZMIANE[i % 4]} for i, (g, b) in enumerate(bloki)]
            kod, o, wersja = r.wyslij_plan(plan_id, wersja, rola, nr, gniazda)
            if kod != 200:
                pisz(f"RAMKA ODMOWILA: kod {kod} {(o.get('blad') or {}).get('kod', '')}")
                return 1
            pisz("SWIECA WSZYSTKIE GNIAZDA (sasiednie w roznych kolorach). Popatrz z gory: kazdy otwor w dnie gniazda ma swiecic, miedzy gniazdami ciemno.")
            odp = pytaj("Wpisz uwage (np. 'gniazda 3 i 7 ciemne') i Enter: ")
            wiersze.append([_godzina(), rola, nr, uklad, "wszystkie", "", przesun[0], przesun[1], odp.strip()])
        else:
            pisz("Po kolei: swieci JEDNO gniazdo na bialo. Enter = dobrze; albo wpisz, co widzisz (np. 'za bardzo w lewo', 'ciemno'); k = koniec.")
            for g, b in bloki:
                kod, o, wersja = r.wyslij_plan(plan_id, wersja, rola, nr, [{"id": g, "px": b, "kolor": "bialy"}])
                wersja += 1
                if kod != 200:
                    pisz(f"gniazdo {g}: RAMKA ODMOWILA (kod {kod} {(o.get('blad') or {}).get('kod', '')}) - sprawdz, czy plytka {nr} lezy na ramce i czy program Stanowisko jest zamkniety")
                    wiersze.append([_godzina(), rola, nr, uklad, g, " ".join(map(str, b)), przesun[0], przesun[1], f"ODMOWA {kod}"])
                    kod_wyjscia = 1
                    continue
                odp = pytaj(f"gniazdo {g:2d} (diody x={b[0]} y={b[1]} {b[2]}x{b[3]}): ").strip()
                if odp.lower() == "k":
                    break
                wiersze.append([_godzina(), rola, nr, uklad, g, " ".join(map(str, b)), przesun[0], przesun[1], odp or "ok"])
    finally:
        zyje.set()
        try:
            r.zadanie("DELETE", "/plan")
        except BrakPolaczenia:
            pass
        zapis = _zapisz_csv(zapis, ["godzina", "ramka", "plytka", "uklad", "gniazdo", "diody_x_y_szer_wys", "przesun_x", "przesun_y", "obserwacja"],
                            wiersze, "gniazda")
    dobre = sum(w[8] == "ok" for w in wiersze)
    pisz(f"Zapisanych obserwacji: {len(wiersze)}, w tym 'ok': {dobre}" + (f"; plik: {zapis}" if zapis else "") + ". Ramka zgaszona.")
    return kod_wyjscia


ZDARZENIA_KLAWIATURY = {"potwierdzenie": "Enter: kuweta potwierdzona", "cofniecie": "Backspace: potwierdzenie cofniete",
                        "kuweta_wybrana": "cyfry + Enter: kuweta wybrana", "kuweta_nieznana": "cyfry + Enter: numer spoza planu",
                        "zamknij_piec": "* + Enter: zamknij piec"}


def polecenie_klawiatura(r: Ramka, uklad: str, kalibracja: Path | None, modele: Path, czas_s: float, zapis: Path | None, pisz=print,
                         stop: threading.Event | None = None) -> int:
    """Ramka poranna: plan z dwiema kuwetami probnymi, potem zapis kazdego zdarzenia klawiatury numerycznej ramki."""
    from ramka import kalibracja as K

    s = r.stan()
    if s["rola"] != "P":
        pisz("Klawiature ma tylko ramka poranna (P). Ta ramka jest wieczorna - klawisze sa na niej pomijane.")
        return 1
    kal = K.wczytaj(kalibracja) if kalibracja else K.domyslna(modele)
    nr = s.get("plytka")
    if uklad not in kal["ramki"]["P"] or nr not in RODZINY["P"]:
        pisz(f"Potrzebna plytka poranna (4, 5 albo 6) na ramce i uklad z kalibracji; odczyt plytki: {nr}, uklad: {uklad}.")
        return 1
    bloki = bloki_ukladu(kal, "P", uklad)
    gniazda = [{"id": g, "px": b, "kolor": "zielony", "kuweta": "1111" if i % 2 == 0 else "2222"} for i, (g, b) in enumerate(bloki)]
    wersja, kod, o = 1, 0, {}
    plan_id = f"proba-{time.strftime('%H%M%S')}-{secrets.token_hex(3)}"
    for _ in range(4):
        s = r.stan()
        plan = {"protokol": 1, "plan_id": plan_id, "wersja": wersja, "start_id": s["start_id"], "zdarzenia_do": s["nr_zdarzenia"], "wazny_s": 600,
                "tryb": "rano", "plytki": {str(nr): {"gniazda": gniazda}}, "kuwety": [{"kuweta": "1111", "plytki": [nr]}, {"kuweta": "2222", "plytki": [nr]}]}
        kod, o = r.zadanie("PUT", "/plan", plan)
        if kod == 200:
            break
        wersja = max(wersja, int(o.get("wersja_ramki") or 0)) + 1
    if kod != 200:
        pisz(f"RAMKA ODMOWILA planu: kod {kod} {(o.get('blad') or {}).get('kod', '')}")
        return 1
    start_id, od = s["start_id"], r.stan()["nr_zdarzenia"]
    pisz("Ramka ma plan probny: kuwety 1111 i 2222 (napis z przodu ramki: numer kuwety i liczba prac).")
    pisz("Naciskaj na klawiaturze ramki, po kolei:  Enter | Backspace | 2 2 2 2 Enter | 9 Enter | * potem Enter.")
    wiersze, t_koniec = [], time.time() + czas_s
    try:
        while time.time() < t_koniec and not (stop is not None and stop.is_set()):
            o = r.zdarzenia(start_id, od, czekaj=min(2.0, max(0.0, t_koniec - time.time())))
            for z in o.get("zdarzenia", []):
                od = max(od, z["nr"])
                if z.get("typ") in ZDARZENIA_KLAWIATURY:
                    co = z.get("kuweta") or z.get("wpisano") or ""
                    pisz(f"{_godzina()}  {ZDARZENIA_KLAWIATURY[z['typ']]} {co}")
                    wiersze.append([_godzina(), z["typ"], co])
            if any(w[1] == "zamknij_piec" for w in wiersze):
                break
    except KeyboardInterrupt:
        pass
    finally:
        try:
            r.zadanie("DELETE", "/plan")
        except BrakPolaczenia:
            pass
        zapis = _zapisz_csv(zapis, ["godzina", "zdarzenie", "kuweta_albo_wpisano"], wiersze, "klawiatura")
    rodzaje = sorted({w[1] for w in wiersze})
    pisz(f"Zdarzen klawiatury: {len(wiersze)}; rodzaje: {len(rodzaje)} z {len(ZDARZENIA_KLAWIATURY)} ({', '.join(rodzaje) or 'zadne'})"
         + (f"; plik: {zapis}" if zapis else "") + ". Ramka zgaszona.")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Proba ramki swietlnej z komputera (bez programu Stanowisko).")
    ap.add_argument("polecenie", choices=("stan", "plytki", "test-led", "gniazda", "klawiatura"))
    ap.add_argument("--adres", required=True, help="nazwa albo adres IP ramki, np. ramka-w.local albo <adres-IP>")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--klucz", default="", help="klucz ramki, gdy jest w jej pliku konfiguracji")
    ap.add_argument("--czas", type=float, default=300.0, help="plytki: ile sekund obserwowac")
    ap.add_argument("--zapis", type=Path, default=None, help="plytki / gniazda: plik CSV na obserwacje albo istniejacy katalog (pelna sciezka)")
    ap.add_argument("--uklad", default=None, help="gniazda: nazwa ukladu z kalibracji, np. wieczorna, poranna, wieczorna_r54")
    ap.add_argument("--kalibracja", type=Path, default=None, help="gniazda: plik kalibracji (domyslnie polozenia startowe)")
    ap.add_argument("--modele", type=Path, default=Path("modele_plytek"), help="gniazda: katalog modeli plytek programu")
    ap.add_argument("--wszystkie", action="store_true", help="gniazda: wszystkie naraz zamiast po kolei")
    ap.add_argument("--przesun", type=int, nargs=2, default=(0, 0), metavar=("DX", "DY"), help="gniazda: przesun bloki o tyle diod w prawo i w dol")
    ap.add_argument("--plytka", type=int, default=None, help="gniazda: numer plytki (domyslnie ten, ktory czyta ramka)")
    a = ap.parse_args(argv)
    r = Ramka(a.adres, a.port, a.klucz)
    try:
        if a.polecenie == "stan":
            return polecenie_stan(r)
        if a.polecenie == "plytki":
            return polecenie_plytki(r, a.czas, a.zapis)
        if a.polecenie == "test-led":
            return polecenie_test_led(r)
        if a.polecenie == "klawiatura":
            return polecenie_klawiatura(r, a.uklad or "poranna", a.kalibracja, a.modele, a.czas if a.czas != 300.0 else 120.0, a.zapis)
        if not a.uklad:
            print("gniazda: podaj --uklad (np. wieczorna dla ramki W, poranna dla ramki P)")
            return 1
        return polecenie_gniazda(r, a.uklad, a.kalibracja, a.modele, a.wszystkie, tuple(a.przesun), a.zapis)
    except BrakPolaczenia as e:
        print(f"BRAK POLACZENIA Z RAMKA {a.adres}:{a.port} - {e}")
        print("Sprawdz: ramka ma prad, komputer i ramka sa w tej samej sieci, adres jest dobry, program Stanowisko jest zamkniety.")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
