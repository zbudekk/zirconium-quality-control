"""session_rano.py - sesja poranna (E3-A6): sesja pieca, punkty zlecen, kompletnosc, braki, dofrezowania, poprawki.

Kryterium odbioru (plan etapu 3, sekcja 4.1, E3-A6): scenariusz SE10 zapisany jako tabela oczekiwan ``TABELA_SE10`` -
kazdy wiersz to osobny test ``test_se10[Rnn]`` (100 % wierszy = wszystkie PASS), liczony na jednym przebiegu scenariusza
(fixture modulu ``se10``): dzien 1 wieczor - w zleceniu X (3 punkty) zab "Ukruszona"; dzien 2 piec 1 - 2 punkty X, komplet Y,
1 z 2 punktow Z (kompletne: Y; braki: X, Z); piec 2 - drugi punkt Z (kompletne: Z); dzien 3 piec 3 - dofrezowany zab X
rozpoznany po tym samym STL (kompletne: X) i poprawka zlecenia juz odhaczonego (tylko log); do tego dwuznaczna rozstrzygnieta
decyzja, nieznana przypisana recznie, ten sam projekt na dwoch plytkach = konflikt, plytka zeskanowana ponownie i restart
programu miedzy piecami (stan odtworzony z bazy).

Pozostale testy: reguly klasy pracy porannej, odmowy decyzji, blokady "Zamknij piec", plan plytek dla ramki (walidacja
protokolem ramki ``ramka.protokol.sprawdz_plan``), kolejnosc kuwet, blokada plytki nie z trybu, zastapienie tylko w tym samym
piecu, decyzje wieczorne nadal odrzucane na pracach porannych (wymaganie A1 dla A6), modul bez zmiany schematu bazy.

Dane: ``testy/dane_sesji/rano/se10.json`` - fikcyjne zlecenia i pliki; wyniki skanow w formacie ``porownaj.porownaj`` buduje
``wynik_skanu`` (status dopasowania wg reguly ``match``: zielony / zolty / szary z pokrycia i przewagi kandydata).
"""
from __future__ import annotations

import ast
import datetime as dt
import hashlib
import json
from pathlib import Path

import pytest

from stanowisko import baza as B
from stanowisko import session as SE
from stanowisko import session_rano as SR

from ramka import kalibracja, protokol  # noqa: E402 (sciezke katalogu stanowiska dodaje conftest)

DANE = Path(__file__).resolve().parent / "dane_sesji" / "rano"
STANOWISKO = Path(__file__).resolve().parent.parent
SCEN = json.loads((DANE / "se10.json").read_text(encoding="ascii"))
PROJ = {p["klucz"]: p for p in SCEN["projekty"]}
SKANY = {s["klucz"]: s for s in SCEN["skany"]}
OSOBY = ["Technik A", "Technik B"]
# zmyslona sciezka folderu zlecenia w wyniku silnika (foldery_projektow): nie moze trafic do pliku wyniku ani dziennika
SCIEZKA_PULI = "C:\\Users\\lab\\OneDrive\\Cyrkon\\3263 Testowa Anna"
DOBA2 = "2026-11-18"


def sha16(klucz: str) -> str:
    """Skrot projektu testowego (w aplikacji: 16 znakow SHA-256 zawartosci pliku STL)."""
    return hashlib.sha256(f"qc-test-rano/{klucz}".encode("ascii")).hexdigest()[:16]


class Zegar:
    """Zegar testu: ``ustaw`` przestawia czas, kazde wywolanie dodaje 1 s (czasy w bazie sa powtarzalne)."""

    def __init__(self, start: str = "2026-11-17T18:00:00"):
        self.t = dt.datetime.fromisoformat(start)

    def ustaw(self, czas: str) -> None:
        self.t = dt.datetime.fromisoformat(czas)

    def __call__(self) -> dt.datetime:
        self.t += dt.timedelta(seconds=1)
        return self.t


def wypelnij_indeks(b: B.Baza) -> None:
    """Zlecenia i projekty z ``se10.json`` (w aplikacji wpisuje je indeks folderow - paczka A4)."""
    zlecenia = {}
    with b.transakcja():
        for z in SCEN["zlecenia"]:
            zlecenia[z["klucz"]] = b.wstaw("zlecenia", zrodlo=z["zrodlo"], folder=z["folder"], folder_norm=z["folder"].lower(),
                                           kuweta=z["kuweta"], mtime=1794900000.0, dodano="2026-11-16T08:00:00")
        for p in SCEN["projekty"]:
            b.wstaw("projekty", zlecenie_id=zlecenia[p["zlecenie"]], plik=p["plik"], sha16=sha16(p["klucz"]), zeby=p["zeby"], typ=p["typ"],
                    mtime_ns=1794900000000000000, rozmiar=300000, zaindeksowano="2026-11-16T08:00:05")


def status_match(kandydaci: list) -> tuple[str, float]:
    """Status dopasowania jak w ``match`` (progi z ustawienia.przyklad.toml): akceptacja 0,85, ostrzezenie 0,6, przewaga 0,1."""
    if not kandydaci:
        return "szary", 0.0
    p1 = kandydaci[0][1]
    p2 = kandydaci[1][1] if len(kandydaci) > 1 else 0.0
    pewnosc = round(p1 - p2, 4)
    if p1 >= 0.85 and pewnosc >= 0.1:
        return "zielony", pewnosc
    if p1 >= 0.6 and pewnosc >= 0.1:
        return "zolty", pewnosc
    return "szary", pewnosc


def wynik_skanu(spec: dict, **zmiany) -> dict:
    """Wynik w formacie ``porownaj.porownaj`` (pola, ktore czyta ``session``) dla skanu ze scenariusza."""
    wieczor = spec["tryb"] == "wieczor"
    wsp = 1.225 if wieczor else 1.0
    gniazda = []
    for g in spec["gniazda"]:
        kand = [{"id": sha16(k), "zeby": [PROJ[k]["zeby"]], "typ": PROJ[k]["typ"], "pokrycie": p, "rms_mm": 0.021,
                 "pokrycie_odwrotne": 0.55, "metoda": "ransac"} for k, p in g["k"]]
        status, pewnosc = status_match(g["k"])
        ins = g.get("inspekcja", "ok")
        inspekcja = None if status == "szary" else {
            "status": ins, "ubytki": [{"srednica_mm": 0.9, "glebokosc_mm": 0.12}] if ins == "ubytek" else [], "metoda": "plaszczyzna"}
        gniazda.append({
            "gniazdo": g["g"], "status_fragmentu": "praca", "punkty": 15000, "srodek": [0.0, 0.0, 10.0], "status": status,
            "pewnosc": pewnosc, "czas_s": 0.6, "uwagi": [], "kandydaci": kand, "inspekcja": inspekcja,
            "status_gniazda": "szary" if status == "szary" else {"ok": "zielony", "ubytek": "czerwony"}[ins],
            "skala": {"wspolczynnik_puli": wsp, "poprawka_proc": 0.0} if kand else None})
    zajete = {g["g"] for g in spec["gniazda"]}
    w = {"skan": f"skan_{spec['klucz']}.stl", "plytka": spec["plytka"], "plytka_wybor": "auto", "uklad_zgodny": True, "wspolczynnik": wsp,
         "projekty": len(PROJ), "foldery_projektow": [SCIEZKA_PULI], "numer": spec["numer"], "numer_zrodlo": "dolki", "gniazda": gniazda,
         "gniazda_puste": [i for i in range(1, 25) if i not in zajete], "gniazda_podwojne": [], "poza_gniazdem": 0, "fragmenty_drobne": 0,
         "czas_s": {"razem": 31.5}}
    w.update(zmiany)
    return w


def zdarzenie(spec: dict) -> dict:
    return {"plik": f"C:/Skany/{spec['czas'][:10]}/skan_{spec['klucz']}.stl",
            "sha16": hashlib.sha256(f"skan/{spec['klucz']}".encode("ascii")).hexdigest()[:16], "rozmiar": 48000000, "czas_pliku": spec["czas"]}


def rano(nr: int, czas: str, gniazda: list, plytka: str = "poranna") -> dict:
    """Skan poranny spoza scenariusza (testy pojedynczych regul)."""
    return {"klucz": f"t{nr}_{czas}", "tryb": "rano", "plytka": plytka, "numer": nr, "czas": czas, "gniazda": gniazda}


class Stanowisko:
    """Baza w katalogu testu + ``Sesja`` (wieczor) + ``SesjaRano``; ``restart`` = zamkniecie i otwarcie programu."""

    def __init__(self, katalog: Path, operator: str | None = "Technik A"):
        self.katalog = katalog
        self.zegar = Zegar()
        self.operator = operator
        self.otworz()

    def otworz(self) -> None:
        b = B.otworz(self.katalog / "dane" / "stanowisko.sqlite")
        self.sesja = SE.Sesja(b, operatorzy=OSOBY, katalog_wynikow=self.katalog / "dane" / "wyniki", zegar=self.zegar)
        if self.operator:
            self.sesja.wybierz_operatora(self.operator)
        self.rano = SR.SesjaRano(self.sesja)

    def restart(self) -> None:
        self.sesja.baza.zamknij()
        self.otworz()

    def skan(self, spec: str | dict, **zmiany) -> int:
        spec = SKANY[spec] if isinstance(spec, str) else spec
        self.zegar.ustaw(spec["czas"])
        if spec["tryb"] == "wieczor":
            return self.sesja.przyjmij_wynik(zdarzenie(spec), wynik_skanu(spec, **zmiany))
        return self.rano.przyjmij_wynik(zdarzenie(spec), wynik_skanu(spec, **zmiany))

    def praca(self, skan_id: int, gniazdo: int) -> int:
        return self.sesja.baza.wiersz("SELECT id FROM prace WHERE skan_id = ? AND gniazdo = ?", (skan_id, gniazdo))["id"]

    def projekt_id(self, klucz: str) -> int:
        return self.sesja.baza.wiersz("SELECT id FROM projekty WHERE sha16 = ?", (sha16(klucz),))["id"]

    def stan_punktu(self, klucz: str) -> tuple | None:
        w = self.sesja.baza.wiersz("SELECT sp.stan, sp.sesja_pieca_id FROM stan_punktow sp JOIN projekty p ON p.id = sp.projekt_id "
                                   "WHERE p.sha16 = ?", (sha16(klucz),))
        return (w["stan"], w["sesja_pieca_id"]) if w else None

    def skan_wiersz(self, skan_id: int) -> dict:
        return self.sesja.baza.wiersz("SELECT * FROM skany WHERE id = ?", (skan_id,))

    def liczba(self, sql: str, parametry: tuple = ()) -> int:
        return self.sesja.baza.wiersz(f"SELECT count(*) AS n FROM {sql}", parametry)["n"]


@pytest.fixture
def st(tmp_path):
    s = Stanowisko(tmp_path)
    wypelnij_indeks(s.sesja.baza)
    yield s
    s.sesja.baza.zamknij()


# --- skroty wynikow API do porownan z tabela ----------------------------------------------------
def kuwety(zlecenia: list[dict]) -> list[str]:
    return [z["kuweta"] for z in zlecenia]


def braki_skrot(zlecenia: list[dict]) -> list[tuple]:
    return [(z["kuweta"], [(b["zeby"], b["stan"]) for b in z["brakujace"]]) for z in zlecenia]


def praca_stanu(stan: dict, skan_id: int, gniazdo: int) -> dict:
    return next(p for s in stan["skany"] if s["id"] == skan_id for p in s["prace"] if p["gniazdo"] == gniazdo)


def klasy(stan: dict, skan_id: int) -> dict[int, str]:
    return {p["gniazdo"]: p["klasa"] for s in stan["skany"] if s["id"] == skan_id for p in s["prace"]}


def lista_dofrez(sesja: SE.Sesja) -> list[tuple]:
    return [(x["kuweta"], x["zeby"]) for x in sesja.do_dofrezowania()]


def lista_zgodna_ze_stanem_punktow(sesja: SE.Sesja) -> bool:
    """Niezmiennik A1: kazdy punkt w stanie do_dofrezowania = dokladnie jedna pozycja listy (i odwrotnie)."""
    punkty = {w["projekt_id"] for w in sesja.baza.wiersze("SELECT projekt_id FROM stan_punktow WHERE stan = 'do_dofrezowania'")}
    pozycje = [x["projekt_id"] for x in sesja.do_dofrezowania() if x["projekt_id"] is not None]
    return sorted(pozycje) == sorted(punkty)


def skrot_planu(plan: dict) -> tuple:
    plytki = {n: [(g["id"], g["kolor"], g.get("kuweta")) for g in p["gniazda"]] for n, p in plan["plytki"].items()}
    return plytki, [(k["kuweta"], k["plytki"]) for k in plan["kuwety"]], plan["braki"]


def do_put_plan(plan: dict, kal: dict) -> dict:
    """Plan z ``plan_plytek`` uzupelniony tak, jak zrobi to ``indicate`` (A8): px z kalibracji i pola protokolu ramki."""
    plytki = {n: {"gniazda": kalibracja.gniazda_planu(kal, "P", plan["uklady"][n],
                                                      {g["id"]: {"kolor": g["kolor"], "kuweta": g.get("kuweta")} for g in p["gniazda"]})}
              for n, p in plan["plytki"].items()}
    return {"protokol": 1, "plan_id": plan["plan_id"], "wersja": 1, "start_id": "a1b2c3d4", "zdarzenia_do": 0, "wazny_s": 600,
            "tryb": plan["tryb"], "plytki": plytki, "kuwety": plan["kuwety"], "braki": plan["braki"]}


def waliduj_plan(plan: dict) -> bool:
    kal = kalibracja.domyslna(STANOWISKO / "modele_plytek")
    p = protokol.sprawdz_plan(do_put_plan(plan, kal), "P")
    return set(p.plytki) == {int(n) for n in plan["plytki"]} and [k.kuweta for k in p.kuwety] == [k["kuweta"] for k in plan["kuwety"]]


def odmowa_zamkniecia(rano_: SR.SesjaRano) -> bool:
    try:
        rano_.zamknij_piec()
    except SE.BladSesji:
        return True
    return False


def migawka(st_: Stanowisko) -> str:
    """Wszystko, co sesja poranna pokazuje miedzy piecami - do porownania przed i po restarcie programu."""
    return json.dumps({"braki": st_.rano.braki(), "wynik1": st_.rano.wynik_pieca(1), "stan1": st_.rano.stan_pieca(1),
                       "piece": st_.rano.piece(DOBA2), "punkty": {k: st_.stan_punktu(k) for k in PROJ},
                       "otwarty": st_.rano.otwarty_piec(), "lista": st_.sesja.do_dofrezowania()}, sort_keys=True, default=str)


# slowa z fikcyjnych nazw folderow (nazwiska, imiona), pelne nazwy folderow i plikow STL - nie moga wyjsc poza cztery tabele;
# slowa od 5 liter ("anna" jest czescia slowa "poranna" - nazwy ukladu plytki)
SLOWA = sorted({c.lower() for z in SCEN["zlecenia"] for c in z["folder"].split() if c.isalpha() and len(c) >= 5}
               | {z["folder"].lower() for z in SCEN["zlecenia"]} | {p["plik"].lower() for p in SCEN["projekty"]})


def nazwy_nie_wychodza(st_: Stanowisko, wyniki_api: list) -> tuple[bool, int]:
    """Czy zadne ze ``SLOWA`` nie wystepuje w 7 tabelach bez nazw, w plikach wynikow i w wynikach API; (wynik, liczba plikow)."""
    zrzut = st_.sesja.baza.zrzut()
    teksty = [str(v) for t in set(B.TABELE) - set(B.TABELE_Z_NAZWAMI) for w in zrzut[t] for v in w.values() if isinstance(v, str)]
    pliki = [p for p in (st_.katalog / "dane").rglob("*") if p.is_file() and p.suffix != ".sqlite"]
    teksty += [p.read_text(encoding="utf-8") for p in pliki]
    teksty.append(json.dumps(wyniki_api, default=str))
    return not any(sl in t.lower() for t in teksty for sl in SLOWA), len(pliki)


# --- SE10: tabela oczekiwan ------------------------------------------------------------------------
PLAN_PIEC1 = ({"4": [(2, "zielony", "3263"), (3, "zielony", "3263"), (4, "zielony", "3301")],
               "5": [(2, "zielony", "3301"), (3, "zielony", "412")]},
              [("3263", [4]), ("3301", [4, 5]), ("412", [5])], ["412", "3263"])
PLAN_PIEC3 = ({"4": [(2, "zielony", "3263"), (3, "bursztyn", "3301")]}, [("3263", [4]), ("3301", [4])], [])
STANY_PO_PIECU1 = {"X11": ("rozpoznany", 1), "X12": ("rozpoznany", 1), "X13": ("do_dofrezowania", None), "Y21": ("rozpoznany", 1),
                   "Y22": ("rozpoznany", 1), "Z31": ("rozpoznany", 1), "Z32": ("brak_po_piecu", 1), "Q46": None, "V36": None}

TABELA_SE10 = [
    ("R01", "dzien 1 wieczor: zlecenie X (3 punkty), zab 13 'Ukruszona' -> lista do dofrezowania", [("3263", "13")]),
    ("R02", "dzien 1 wieczor: punkt X13 w stanie do_dofrezowania", "do_dofrezowania"),
    ("R03", "piec 1 otwiera sie sam pierwszym skanem porannym (doba, nr w dniu, otwarty, plan_id)", (DOBA2, 1, True, "2026-11-18-p1")),
    ("R04", "piec 1: klasy prac plytek 4 i 5 przed rozstrzygnieciem", {4: {2: "pewna", 3: "pewna", 4: "pewna"}, 5: {2: "dwuznaczna", 3: "nieznana"}}),
    ("R05", "dwuznaczna: dwaj kandydaci z kuweta i zebem (podglad obu na ekranie)", [("3301", "22"), ("#1234", "46")]),
    ("R06", "dwuznaczna rozstrzygnieta decyzja wybor_kandydata (klasa, kolor, kuweta, wierszy decyzji)", ("przypisana", "zielony", "3301", 1)),
    ("R07", "nieznana przypisana recznie - przypisanie_reczne (klasa, kolor, kuweta, zab)", ("przypisana", "zielony", "412", "31")),
    ("R08", "plytka 5 zeskanowana ponownie: propozycja zastapienia, konflikt zeba 3301/22, Zamknij piec odmawia", (True, [("3301", "22")], True)),
    ("R09", "po potwierdzeniu: stary skan zastapiony, 0 konfliktow, decyzja starego skanu nie przechodzi (zab 31 znow nieznany)",
     ("zastapiony", 0, "nieznana")),
    ("R10", "nieznana na nowym skanie przypisana recznie ponownie", "przypisana"),
    ("R11", "piec 1 przed zamknieciem (stan prowizoryczny): kompletne i braki",
     (["3301"], [("412", [("32", "oczekuje")]), ("3263", [("13", "do_dofrezowania")])])),
    ("R12", "plan plytek pieca 1 dla ramki: gniazda (id, kolor, kuweta), kuwety od najliczniejszej, braki", PLAN_PIEC1),
    ("R13", "plan pieca 1 po dodaniu px z kalibracji przechodzi walidacje protokolu ramki porannej", True),
    ("R14", "Zamknij piec 1 -> kompletne: Y", ["3301"]),
    ("R15", "Zamknij piec 1 -> braki: Z (1 zab), X (1 zab, dofrezowywany) - kolejnosc wg numeru kuwety",
     [("412", [("32", "brak_po_piecu")]), ("3263", [("13", "do_dofrezowania")])]),
    ("R16", "stany punktow po piecu 1 (stan, sesja pieca)", STANY_PO_PIECU1),
    ("R17", "lista do dofrezowania po piecu 1 bez zmian i zgodna ze stan_punktow", ([("3263", "13")], True)),
    ("R18", "restart programu miedzy piecami: stan odtworzony (braki, wynik i stan pieca 1, piece doby, punkty), brak otwartego pieca", True),
    ("R19", "piec 2: ten sam projekt (Z32) na plytkach 4 i 6 = konflikt; Zamknij piec odmawia", ([("412", "32", [4, 6])], True)),
    ("R20", "konflikt rozstrzygniety: praca z plytki 6 'bez projektu' -> nieznana (biala), 0 konfliktow", ("nieznana", "bialy", 0)),
    ("R21", "Zamknij piec 2 -> kompletne: Z (drugi punkt Z)", ["412"]),
    ("R22", "braki po piecu 2: tylko X (zab 13 dofrezowywany); nierozstrzygnieta 1 praca nieznana",
     ([("3263", [("13", "do_dofrezowania")])], {"dwuznaczne": 0, "nieznane": 1})),
    ("R23", "dzien 2 wieczor: dofrezowany zab X13 zeskanowany wieczorem - lista do dofrezowania bez zmian (punkt domyka poranek)",
     ([("3263", "13")], "do_dofrezowania")),
    ("R24", "piec 3: dofrezowany zab X13 rozpoznany po tym samym STL (sha16) - pewna, domyka dofrezowanie", ("pewna", True, sha16("X13"))),
    ("R25", "piec 3: zab Y21 zlecenia juz odhaczonego = poprawka (bursztyn), nie liczona do kompletu", ("poprawka", "bursztynowy", True, False)),
    ("R26", "restart w trakcie pieca 3: ten sam otwarty piec i identyczny stan pieca", True),
    ("R27", "plan pieca 3: X13 zielony 3263, poprawka Y21 bursztyn 3301, braki puste", PLAN_PIEC3),
    ("R28", "Zamknij piec 3 -> kompletne: X", ["3263"]),
    ("R29", "Zamknij piec 3 -> poprawka Y21 tylko log (lista poprawek, 1 wpis poprawka_rano w dzienniku, Y nie w kompletnych)",
     ([("3301", "21", True)], 1, False)),
    ("R30", "po piecu 3: braki puste, lista do dofrezowania pusta, punkt X13 rozpoznany w piecu 3", ([], [], ("rozpoznany", 3))),
    ("R31", "restart: wynik_pieca 1-3 rowny wynikom zwroconym przez Zamknij piec (lista dla Excela po restarcie)", True),
    ("R32", "dane osobowe: 0 nazw folderow i plikow zlecen w 7 tabelach, plikach wynikow i wynikach API", True),
]


def _scenariusz(st: Stanowisko, w: dict) -> None:
    r = st.rano
    # dzien 1 (17.11) wieczor
    w1 = st.skan("w1")
    st.skan("w2")
    st.zegar.ustaw("2026-11-17T19:30:00")
    st.sesja.ukruszona(st.praca(w1, 4))
    w["R01"] = lista_dofrez(st.sesja)
    w["R02"] = st.stan_punktu("X13")[0]
    # dzien 2 (18.11), piec 1
    a = st.skan("p1_4")
    stan = r.stan_pieca()
    w["R03"] = (r.otwarty_piec()["data"], r.otwarty_piec()["nr_w_dniu"], stan["otwarty"], stan["plan_id"])
    b = st.skan("p1_5")
    stan = r.stan_pieca()
    w["R04"] = {4: klasy(stan, a), 5: klasy(stan, b)}
    p22 = praca_stanu(stan, b, 2)
    w["R05"] = [(pr["kuweta"], pr["zeby"]) for k in p22["kandydaci"] for pr in k["projekty"]]
    st.zegar.ustaw("2026-11-18T07:08:00")
    r.wybierz_kandydata(p22["id"], sha16("Y22"))
    x = praca_stanu(r.stan_pieca(), b, 2)
    w["R06"] = (x["klasa"], x["kolor"], x["kuweta"], st.liczba("decyzje WHERE rodzaj = 'wybor_kandydata'"))
    r.przypisz_recznie(st.praca(b, 3), st.projekt_id("Z31"))
    x = praca_stanu(r.stan_pieca(), b, 3)
    w["R07"] = (x["klasa"], x["kolor"], x["kuweta"], x["zeby"])
    c = st.skan("p1_5_ponownie")
    stan = r.stan_pieca()
    propozycje = [{k: p[k] for k in ("skan_id", "poprzedni_id", "numer_plytki")} for p in stan["do_potwierdzenia"]]
    w["R08"] = (propozycje == [{"skan_id": c, "poprzedni_id": b, "numer_plytki": 5}], [(k["kuweta"], k["zeby"]) for k in stan["konflikty"]],
                odmowa_zamkniecia(r))
    st.zegar.ustaw("2026-11-18T07:14:00")
    r.zastap_skan(c)
    stan = r.stan_pieca()
    w["R09"] = (st.skan_wiersz(b)["status"], len(stan["konflikty"]), klasy(stan, c)[3])
    r.przypisz_recznie(st.praca(c, 3), st.projekt_id("Z31"))
    stan = r.stan_pieca()
    w["R10"] = klasy(stan, c)[3]
    w["R11"] = (kuwety(stan["kompletne"]), braki_skrot(stan["braki"]))
    plan = r.plan_plytek()
    w["R12"] = skrot_planu(plan)
    w["R13"] = waliduj_plan(plan)
    st.zegar.ustaw("2026-11-18T07:30:00")
    wynik1 = r.zamknij_piec()
    w["R14"] = kuwety(wynik1["kompletne"])
    w["R15"] = braki_skrot(wynik1["braki"])
    w["R16"] = {k: st.stan_punktu(k) for k in PROJ}
    w["R17"] = (lista_dofrez(st.sesja), lista_zgodna_ze_stanem_punktow(st.sesja))
    # restart programu miedzy piecami
    przed = migawka(st)
    st.restart()
    r = st.rano
    w["R18"] = migawka(st) == przed and r.otwarty_piec() is None
    # dzien 2, piec 2
    st.skan("p2_4")
    e = st.skan("p2_6")
    stan = r.stan_pieca()
    w["R19"] = ([(k["kuweta"], k["zeby"], sorted(m["numer_plytki"] for m in k["miejsca"])) for k in stan["konflikty"]], odmowa_zamkniecia(r))
    st.zegar.ustaw("2026-11-18T09:40:00")
    r.przypisz_recznie(st.praca(e, 3), None)
    stan = r.stan_pieca()
    x = praca_stanu(stan, e, 3)
    w["R20"] = (x["klasa"], x["kolor"], len(stan["konflikty"]))
    st.zegar.ustaw("2026-11-18T09:45:00")
    wynik2 = r.zamknij_piec()
    w["R21"] = kuwety(wynik2["kompletne"])
    w["R22"] = (braki_skrot(r.braki()), wynik2["nierozstrzygniete"])
    # dzien 2 wieczor: dofrezowany zab X13 przechodzi przez skan wieczorny
    st.skan("w3")
    w["R23"] = (lista_dofrez(st.sesja), st.stan_punktu("X13")[0])
    # dzien 3 (19.11), piec 3
    f = st.skan("p3_4")
    stan = r.stan_pieca()
    x13, y21 = praca_stanu(stan, f, 2), praca_stanu(stan, f, 3)
    w["R24"] = (x13["klasa"], x13["domyka_dofrezowanie"], x13["sha16"])
    w["R25"] = (y21["klasa"], y21["kolor"], y21["zlecenie_odhaczone"], y21["liczona"])
    piec_przed = r.otwarty_piec()
    st.restart()
    r = st.rano
    w["R26"] = r.stan_pieca() == stan and r.otwarty_piec() == piec_przed
    w["R27"] = skrot_planu(r.plan_plytek())
    st.zegar.ustaw("2026-11-19T07:20:00")
    wynik3 = r.zamknij_piec()
    w["R28"] = kuwety(wynik3["kompletne"])
    w["R29"] = ([(p["kuweta"], p["zeby"], p["zlecenie_odhaczone"]) for p in wynik3["poprawki"]],
                st.liczba("zdarzenia WHERE typ = 'poprawka_rano'"), "3301" in kuwety(wynik3["kompletne"]))
    w["R30"] = (braki_skrot(r.braki()), lista_dofrez(st.sesja), st.stan_punktu("X13"))
    st.restart()
    r = st.rano
    w["R31"] = [r.wynik_pieca(i) for i in (1, 2, 3)] == [wynik1, wynik2, wynik3]
    api = [wynik1, wynik2, wynik3, r.braki(), r.piece(DOBA2), r.piece("2026-11-19")] + [r.stan_pieca(i) for i in (1, 2, 3)] + [r.plan_plytek(3)]
    czyste, pliki = nazwy_nie_wychodza(st, api)
    w["R32"] = czyste and pliki == 9  # 9 plikow wynikow skanow (3 wieczorne + 6 porannych)


@pytest.fixture(scope="module")
def se10(tmp_path_factory) -> dict:
    """Jeden przebieg scenariusza SE10; slownik wiersz -> wynik (przerwany scenariusz: klucz ``_blad``)."""
    st = Stanowisko(tmp_path_factory.mktemp("se10"))
    w: dict = {}
    try:
        wypelnij_indeks(st.sesja.baza)
        _scenariusz(st, w)
    except Exception as e:  # noqa: BLE001 - wiersze, ktorych nie policzono, dostaja FAIL z powodem
        w["_blad"] = f"{type(e).__name__}: {e}"
    finally:
        st.sesja.baza.zamknij()
    return w


@pytest.mark.parametrize("nr,opis,oczekiwane", TABELA_SE10, ids=[t[0] for t in TABELA_SE10])
def test_se10(se10, nr, opis, oczekiwane):
    if nr not in se10:
        pytest.fail(f"{nr} ({opis}): nie policzono - scenariusz przerwany: {se10.get('_blad')}")
    assert se10[nr] == oczekiwane, f"{nr} ({opis})"


def test_se10_tabela_kompletna(se10):
    """Kazdy wiersz tabeli ma wynik (scenariusz doszedl do konca) i wszystkie sa zgodne: 32 z 32."""
    assert "_blad" not in se10, se10.get("_blad")
    zgodne = sum(1 for nr, _, oczekiwane in TABELA_SE10 if se10.get(nr) == oczekiwane)
    print(f"\nSE10: {zgodne} z {len(TABELA_SE10)} wierszy PASS")
    for nr, opis, oczekiwane in TABELA_SE10:
        print(f"{nr} {'PASS' if se10.get(nr) == oczekiwane else 'FAIL'} - {opis}")
    assert zgodne == len(TABELA_SE10) == 32


# --- reguly pojedynczo ---------------------------------------------------------------------------
def test_klasa_pracy_porannej_i_przypisanie_obowiazujace(st):
    """Pewna = dopasowanie zielone; dwuznaczna = kandydat z pokryciem >= prog (0,6) bez pewnosci; nieznana = brak albo slaby kandydat.
    ``prace.projekt_id`` = przypisanie obowiazujace (plan 3.4): tylko dla pracy pewnej, dla innych puste do decyzji."""
    s = st.skan(rano(4, "2026-11-18T07:00:00", [
        {"g": 2, "k": [["X11", 0.95]]}, {"g": 3, "k": [["X12", 0.80], ["Y21", 0.76]]}, {"g": 4, "k": [["X13", 0.70]]},
        {"g": 5, "k": [["Y22", 0.50]]}, {"g": 6, "k": []}]))
    stan = st.rano.stan_pieca()
    assert klasy(stan, s) == {2: "pewna", 3: "dwuznaczna", 4: "dwuznaczna", 5: "nieznana", 6: "nieznana"}
    kolory = {p["gniazdo"]: (p["kolor"], p["kolor_ramki"]) for p in stan["skany"][0]["prace"]}
    assert kolory == {2: ("zielony", "zielony"), 3: ("zolty", "zolty"), 4: ("zolty", "zolty"), 5: ("bialy", "bialy"), 6: ("bialy", "bialy")}
    projekty = {w["gniazdo"]: w["projekt_id"] for w in st.sesja.baza.wiersze("SELECT gniazdo, projekt_id FROM prace WHERE skan_id = ?", (s,))}
    assert projekty == {2: st.projekt_id("X11"), 3: None, 4: None, 5: None, 6: None}
    assert stan["liczniki"] == {"pewna": 1, "dwuznaczna": 2, "nieznana": 2}
    assert stan["nierozstrzygniete"] == {"dwuznaczne": 2, "nieznane": 2}
    p2 = praca_stanu(stan, s, 2)
    assert (p2["kuweta"], p2["zeby"], p2["przypisanie"], p2["liczona"], p2["sha16"]) == ("3263", "11", "auto", True, sha16("X11"))


def test_prog_kandydata_z_ustawien(st):
    """Prog dwuznacznej = ``[match] prog_ostrzezenia_pokrycie`` (bez nowego klucza ustawien)."""
    r = SR.SesjaRano.z_ustawien({"match": {"prog_ostrzezenia_pokrycie": 0.75}}, sesja=st.sesja)
    assert r.prog_kandydata == 0.75
    s = st.skan(rano(4, "2026-11-18T07:00:00", [{"g": 2, "k": [["X12", 0.80], ["Y21", 0.76]]}, {"g": 3, "k": [["X13", 0.70]]}]))
    assert klasy(r.stan_pieca(), s) == {2: "dwuznaczna", 3: "nieznana"}
    assert klasy(st.rano.stan_pieca(), s) == {2: "dwuznaczna", 3: "dwuznaczna"}  # domyslnie 0,6


def test_decyzje_poranne_odmowy_bez_zmian_w_bazie(st):
    w1 = st.skan("w1")
    s = st.skan(rano(4, "2026-11-18T07:00:00", [{"g": 2, "k": [["X12", 0.80], ["Y21", 0.76]]}]))
    p = st.praca(s, 2)
    przed = st.liczba("decyzje")
    with pytest.raises(SE.BladSesji, match="kandydat"):
        st.rano.wybierz_kandydata(p, sha16("Q46"))  # nie jest kandydatem tej pracy
    with pytest.raises(SE.BladSesji, match="projekt"):
        st.rano.przypisz_recznie(p, 99999)
    with pytest.raises(SE.BladSesji, match="wieczor"):
        st.rano.przypisz_recznie(st.praca(w1, 2), st.projekt_id("X11"))  # praca skanu wieczornego
    with pytest.raises(SE.BladSesji, match="nie ma pracy"):
        st.rano.cofnij_przypisanie(99999)
    bez = Stanowisko(st.katalog / "drugi", operator=None)  # osobny program bez wybranej osoby
    try:
        wypelnij_indeks(bez.sesja.baza)
        s2 = bez.skan(rano(4, "2026-11-18T07:00:00", [{"g": 2, "k": [["X12", 0.80], ["Y21", 0.76]]}]))
        with pytest.raises(SE.BladSesji, match="operatora"):
            bez.rano.wybierz_kandydata(bez.praca(s2, 2), sha16("X12"))
        with pytest.raises(SE.BladSesji, match="operatora"):
            bez.rano.zamknij_piec()
        assert bez.liczba("decyzje") == 0
    finally:
        bez.sesja.baza.zamknij()
    # skan do powtorzenia (dwie prace w gniezdzie): decyzji nie przyjmuje
    s3 = st.skan(rano(5, "2026-11-18T07:05:00", [{"g": 2, "k": [["Z31", 0.80], ["Z32", 0.75]]}]), gniazda_podwojne=[2])
    assert st.skan_wiersz(s3)["status"] == "do_powtorzenia"
    with pytest.raises(SE.BladSesji, match="ponownie"):
        st.rano.wybierz_kandydata(st.praca(s3, 2), sha16("Z31"))
    assert klasy(st.rano.stan_pieca(), s3) == {2: "do_powtorzenia"}
    assert st.liczba("decyzje") == przed
    # po zamknieciu pieca decyzji o jego pracach nie da sie zmienic
    st.rano.wybierz_kandydata(p, sha16("X12"))
    st.rano.zamknij_piec()
    with pytest.raises(SE.BladSesji, match="zamkniety"):
        st.rano.cofnij_przypisanie(p)
    with pytest.raises(SE.BladSesji, match="zamkniety"):
        st.rano.podaj_numer_plytki(s, 6)


def test_cofnij_przypisanie_przywraca_poprzednie(st):
    s = st.skan(rano(4, "2026-11-18T07:00:00", [{"g": 2, "k": [["X12", 0.80], ["Y21", 0.76]]}]))
    p = st.praca(s, 2)
    d1 = st.rano.wybierz_kandydata(p, sha16("Y21"))
    d2 = st.rano.przypisz_recznie(p, st.projekt_id("Q46"))
    x = praca_stanu(st.rano.stan_pieca(), s, 2)
    assert (x["klasa"], x["kuweta"], x["decyzja"], x["decyzja_id"]) == ("przypisana", "#1234", "przypisanie_reczne", d2)
    c1 = st.rano.cofnij_przypisanie(p)
    x = praca_stanu(st.rano.stan_pieca(), s, 2)
    assert (x["klasa"], x["kuweta"], x["decyzja"], x["decyzja_id"]) == ("przypisana", "3301", "wybor_kandydata", d1)
    st.rano.cofnij_przypisanie(p)
    x = praca_stanu(st.rano.stan_pieca(), s, 2)
    assert (x["klasa"], x["projekt_id"], x["decyzja"]) == ("dwuznaczna", None, None)
    assert st.sesja.baza.wiersz("SELECT projekt_id FROM prace WHERE id = ?", (p,))["projekt_id"] is None
    rows = st.sesja.baza.wiersze("SELECT rodzaj, wartosc, operator, praca_id, skan_id FROM decyzje ORDER BY id")
    assert [(d["rodzaj"], d["wartosc"]) for d in rows] == [("wybor_kandydata", sha16("Y21")), ("przypisanie_reczne", str(st.projekt_id("Q46"))),
                                                          ("cofniecie", str(d2)), ("cofniecie", str(d1))]
    assert all(d["operator"] == "Technik A" and d["praca_id"] == p and d["skan_id"] == s for d in rows) and c1 > d2
    with pytest.raises(SE.BladSesji, match="nie ma decyzji"):
        st.rano.cofnij_przypisanie(p)


def test_zamknij_piec_wymaga_otwartego_pieca_i_numeru_plytki(st):
    with pytest.raises(SE.BladSesji, match="otwart"):
        st.rano.zamknij_piec()
    s = st.skan(rano(4, "2026-11-18T07:00:00", [{"g": 2, "k": [["Y21", 0.95]]}]), numer=None, numer_zrodlo="nieznany")
    stan = st.rano.stan_pieca()
    assert stan["bez_numeru"] == [s] and stan["blokady"]
    assert st.rano.plan_plytek()["pominiete"]["bez_numeru"] == [s] and st.rano.plan_plytek()["plytki"] == {}
    with pytest.raises(SE.BladSesji, match="numer"):
        st.rano.zamknij_piec()
    with pytest.raises(SE.BladSesji, match="otwarty"):
        st.rano.otworz_piec()
    st.rano.podaj_numer_plytki(s, 4)
    assert st.rano.stan_pieca()["blokady"] == []
    wynik = st.rano.zamknij_piec(operator="Technik B")
    assert wynik["zamknal"] == "Technik B" and kuwety(wynik["braki"]) == ["3301"] and wynik["kompletne"] == []
    piec = st.sesja.baza.wiersz("SELECT * FROM sesje_pieca WHERE id = ?", (wynik["sesja_pieca_id"],))
    assert piec["zamknal"] == "Technik B" and piec["zamknieto"] and st.rano.otwarty_piec() is None


def test_plytka_wieczorna_w_trybie_rano_zablokowana_az_do_dopuszczenia(st):
    s = st.skan(rano(2, "2026-11-18T07:00:00", [{"g": 2, "k": [["Y21", 0.95]]}, {"g": 3, "k": [["Y22", 0.95]]}], plytka="wieczorna"))
    stan = st.rano.stan_pieca()
    assert st.skan_wiersz(s)["status"] == "plytka_nie_z_trybu" and stan["skany"][0]["aktywny"] is False
    assert klasy(stan, s) == {2: None, 3: None} and stan["kompletne"] == [] and st.rano.plan_plytek()["plytki"] == {}
    st.rano.dopusc_plytke(s)
    stan = st.rano.stan_pieca()
    assert klasy(stan, s) == {2: "pewna", 3: "pewna"} and kuwety(stan["kompletne"]) == ["3301"]


def test_dwuznaczna_nierozstrzygnieta_nie_domyka_zlecenia(st):
    st.skan(rano(4, "2026-11-18T07:00:00", [{"g": 2, "k": [["Y21", 0.95]]}, {"g": 3, "k": [["Y22", 0.80], ["Q46", 0.76]]}]))
    wynik = st.rano.zamknij_piec()
    assert wynik["kompletne"] == [] and braki_skrot(wynik["braki"]) == [("3301", [("22", "brak_po_piecu")])]
    assert wynik["nierozstrzygniete"] == {"dwuznaczne": 1, "nieznane": 0} and st.stan_punktu("Q46") is None
    assert braki_skrot(st.rano.braki()) == [("3301", [("22", "brak_po_piecu")])]
    # brakujacy zab wychodzi z nastepnego pieca: lista brakow uzupelnia sie sama
    st.skan(rano(4, "2026-11-18T09:00:00", [{"g": 7, "k": [["Y22", 0.93]]}]))
    wynik2 = st.rano.zamknij_piec()
    assert kuwety(wynik2["kompletne"]) == ["3301"] and st.rano.braki() == []


def test_kolejnosc_kuwet_wg_numeru_i_kuweta_niejednoznaczna(st):
    s = st.skan(rano(4, "2026-11-18T07:00:00", [
        {"g": 2, "k": [["Q46", 0.95]]}, {"g": 3, "k": [["Z31", 0.95]]}, {"g": 4, "k": [["Z32", 0.95]]},
        {"g": 5, "k": [["X11", 0.95]]}, {"g": 6, "k": [["V36", 0.95]]}]))
    plan = st.rano.plan_plytek(kolejnosc="numer")
    assert [k["kuweta"] for k in plan["kuwety"]] == ["412", "3263", "#1234"]  # numery rosnaco, prywatne na koncu
    assert [k["kuweta"] for k in st.rano.plan_plytek()["kuwety"]] == ["412", "3263", "#1234"]  # od najliczniejszej (412: 2 prace)
    assert plan["liczba_prac"] == {"412": 2, "3263": 1, "#1234": 1}
    g6 = next(g for g in plan["plytki"]["4"]["gniazda"] if g["id"] == 6)
    assert g6 == {"id": 6, "kolor": "czerwony"}  # kuweta "?46,5120" (niejednoznaczna) nie idzie do ramki - "sprawdz"
    v = praca_stanu(st.rano.stan_pieca(), s, 6)
    assert (v["klasa"], v["kuweta"], v["kuweta_do_sprawdzenia"], v["liczona"]) == ("pewna", "?46,5120", True, True)
    assert waliduj_plan(plan)
    with pytest.raises(SE.BladSesji, match="kolejnosc"):
        st.rano.plan_plytek(kolejnosc="alfabet")


def test_decyzje_wieczorne_na_pracach_porannych_nadal_odrzucane(st):
    """Wymaganie A1 dla A6: decyzja poranna nie przestawia punktu z wieczorna "Ukruszona"; "Ukruszona" na pracy porannej - odmowa."""
    w1 = st.skan("w1")
    st.zegar.ustaw("2026-11-17T19:30:00")
    st.sesja.ukruszona(st.praca(w1, 4))
    s = st.skan(rano(4, "2026-11-18T07:00:00", [{"g": 2, "k": [["X13", 0.80], ["X12", 0.76]]}]))
    with pytest.raises(SE.BladSesji):
        st.sesja.ukruszona(st.praca(s, 2))
    st.rano.wybierz_kandydata(st.praca(s, 2), sha16("X13"))
    st.rano.cofnij_przypisanie(st.praca(s, 2))
    st.rano.wybierz_kandydata(st.praca(s, 2), sha16("X13"))
    assert lista_dofrez(st.sesja) == [("3263", "13")] and st.stan_punktu("X13") == ("do_dofrezowania", None)  # do zamkniecia pieca bez zmian
    assert lista_zgodna_ze_stanem_punktow(st.sesja)
    st.rano.zamknij_piec()
    assert lista_dofrez(st.sesja) == [] and st.stan_punktu("X13") == ("rozpoznany", 1) and lista_zgodna_ze_stanem_punktow(st.sesja)


def test_nowy_piec_po_zamknieciu_i_piece_doby(st):
    st.skan(rano(4, "2026-11-18T07:00:00", [{"g": 2, "k": [["Y21", 0.95]]}]))
    st.rano.zamknij_piec()
    st.skan(rano(4, "2026-11-18T09:00:00", [{"g": 2, "k": [["Y22", 0.95]]}]))
    piece = st.rano.piece(DOBA2)
    assert [(p["nr_w_dniu"], p["plan_id"], p["zamknieto"] is not None, p["skanow"]) for p in piece] == [
        (1, "2026-11-18-p1", True, 1), (2, "2026-11-18-p2", False, 1)]
    assert st.rano.otwarty_piec()["id"] == piece[1]["id"] and st.rano.stan_pieca()["nr_w_dniu"] == 2
    assert st.liczba("zdarzenia WHERE typ = 'piec_otwarty'") == 2 and st.liczba("zdarzenia WHERE typ = 'piec_zamkniety'") == 1


def test_zastapienie_tylko_w_tym_samym_otwartym_piecu(st):
    s1 = st.skan(rano(4, "2026-11-18T07:00:00", [{"g": 2, "k": [["Y21", 0.95]]}]))
    st.rano.zamknij_piec()
    s2 = st.skan(rano(4, "2026-11-18T07:20:00", [{"g": 3, "k": [["Y22", 0.95]]}]))
    assert st.rano.stan_pieca()["do_potwierdzenia"] == []  # ta sama plytka w nowym piecu = nowy wsad, bez pytania
    with pytest.raises(SE.BladSesji, match="piec"):
        st.rano.zastap_skan(s2, s1)
    assert st.skan_wiersz(s1)["status"] == "przyjety"


def test_modul_bez_zmiany_schematu_i_tylko_biblioteka_standardowa():
    assert B.WERSJA_SCHEMATU == 1 and len(B.TABELE) == 11
    drzewo = ast.parse((STANOWISKO / "stanowisko" / "session_rano.py").read_text(encoding="utf-8"))
    importy = {a.name.split(".")[0] for n in ast.walk(drzewo) if isinstance(n, ast.Import) for a in n.names}
    importy |= {n.module.split(".")[0] for n in ast.walk(drzewo) if isinstance(n, ast.ImportFrom) and n.module and n.level == 0}
    z_pakietu = {a.name for n in ast.walk(drzewo) if isinstance(n, ast.ImportFrom) and n.level == 1 for a in n.names}
    assert importy <= {"__future__", "datetime", "json", "re", "collections", "typing", "dataclasses"}, importy
    assert z_pakietu <= {"baza", "session"}, z_pakietu
