"""metryki - metryki odbiorcze stanowiska liczone z bazy programu (E3-A10; runda 2 po recenzji PR #29).

M1 (plan etapu 3, 3.3; PW "Testy odbiorcze i kryteria"): kazda metryke program liczy sam z wlasnego logu, raport = jedno
polecenie i jedna strona (``narzedzia/raport_metryk.py``). Zrodla - wylacznie istniejace tabele schematu w wersji 1
(``skany``, ``prace``, ``decyzje``, ``sesje_pieca``, ``zdarzenia``, indeks ``projekty``) czytane przez publiczne API sesji, zeby
reguly byly te same co na ekranie: ``Sesja.stan_wieczoru`` (skany aktywne, decyzja obowiazujaca po cofnieciach i zastapieniach,
propozycje ponownego skanu) i ``SesjaRano.stan_pieca`` (klasa pracy porannej, przypisanie po decyzjach technika, kandydaci
z indeksem). Proste liczniki statusow i czasy aktywnosci - zapytania SELECT. Caly raport w JEDNEJ transakcji odczytu (spojny
stan, gdy program w tym czasie pisze). Modul TYLKO CZYTA (baza otwarta ``tylko_odczyt`` wystarcza) i nie zmienia schematu:
tabela testow wykrywalnosci (M2) wymaga zmiany schematu - wiersz M2 ma ocene "wymaga zmiany schematu" i nie ma wartosci.

Dane osobowe: wynik (slownik / JSON) i strona maja tylko liczby, daty dob i nazwy metryk - zadnych nazw folderow, plikow,
skanow, kuwet ani osob (operator z ``decyzje.operator`` nie jest czytany).

Definicje (szczegoly i uzasadnienia: ``opisy_modulow/metryki.md``):
- okres = doby robocze ``od`` .. ``do`` (wlacznie); wieczor: skany przyjete w okresie; rano: piece ZAMKNIETE z doba otwarcia
  w okresie (klasy, top-1/2, skany powtorzone);
- praca nieznana (wieczor i rano ta sama regula) = program nie mial kandydata: brak 1. kandydata, 1. kandydat ponizej progu
  pracy dwuznacznej albo zaden z 2 kandydatow nie jest w indeksie;
- falszywe alarmy = czerwone z obowiazujaca decyzja "OK" / prace skanow wieczornych PRZYJETYCH (tylko na nich technik decyduje),
  bez skanu, ktory czeka na potwierdzenie ponownego skanu (te same prace nie licza sie dwa razy);
- top-1 / top-2 = rozpoznanie programu wzgledem decyzji technika w zamknietym piecu: praca z projektem (pewna, przypisana,
  poprawka) i praca, ktorej propozycje programu technik odrzucil ("bez projektu") - ta jest chybieniem; top-1 = projekt jest
  1. kandydatem, top-2 = wlasciwa kuweta (albo projekt) wsrod 2 kandydatow (PW);
- czas przy stanowisku = suma posiedzen na zmiane (start skanu, wykrycie pliku, zdarzenie okna, przyjecie skanu, decyzja;
  przerwa > ``przerwa_min`` konczy posiedzenie); zmiana bez mierzalnego czasu (same pojedyncze chwile) - poza srednia;
- skany powtorzone = zastapione albo zakonczone statusem do powtorzenia / niezgodny uklad / plytka nie z trybu / blad;
- dni bez awarii = seria kolejnych dob z wpisami dziennika (z calej historii) biegnaca do konca okresu; awaria wymagajaca
  restartu = ``program_start`` bez wczesniejszego ``program_stop`` (``silnik_nie_startuje`` - osobny licznik, nie awaria).
"""
from __future__ import annotations

import datetime as dt
import statistics
from bisect import bisect_left
from typing import Any

from . import baza as B
from . import session as SE
from . import session_rano as SR

WERSJA = "etap3-A10r2"
TRYB_WIECZOR, TRYB_RANO, TRYB_OBA = SE.TRYB_WIECZOR, SE.TRYB_RANO, "oba"
TRYBY = (TRYB_WIECZOR, TRYB_RANO, TRYB_OBA)
PRZERWA_MIN = 10  # [PROPOZYCJA] dluzsza przerwa w aktywnosci = technik odszedl od stanowiska (koniec posiedzenia)
OKRES_DOMYSLNY_DOB = 7  # raport bez --od: tydzien konczacy sie na --do
STATUS_IMPORT = "import"  # skany z okna testowego (narzedzia/import_decyzji.py) - poza metrykami
STATUSY_POWTORZONE = (SE.STATUS_ZASTAPIONY, SE.STATUS_DO_POWTORZENIA, SE.STATUS_NIEZGODNY_UKLAD, SE.STATUS_PLYTKA_NIE_Z_TRYBU, SE.STATUS_BLAD)
KLASY_Z_PRAWDA = (SR.KLASA_PEWNA, SR.KLASA_PRZYPISANA, SR.KLASA_POPRAWKA)  # praca poranna z projektem obowiazujacym po decyzjach technika
KOLOR_ALARMU = "czerwony"  # ocena programu "UBYTEK" (porownaj.INSPECT_NA_STATUS)
TYP_START, TYP_STOP, TYP_SILNIK, TYP_START_SKANU = "program_start", "program_stop", "silnik_nie_startuje", "start_skanu"  # = aplikacja.py
ZRODLO_OKNA = "ui"  # kazde zdarzenie okna (klikniecie) to chwila aktywnosci przy stanowisku
TYPY_AKTYWNOSCI = ("nowy_skan", "podglad")  # wykrycie pliku skanu (koniec skanowania) i podglad 3D - tez aktywnosc
AWARIA_RESTART, AWARIA_SILNIK = "restart_bez_zamkniecia", "silnik_nie_startuje"

# Progi odbioru z PW "Testy odbiorcze i kryteria" (kolumna "Prog odbioru", nie "Cel po 3 miesiacach"); wartosc rowna progowi zalicza.
# Nie stroi sie ich pod wynik - zmiana tylko po zmianie planu wdrozenia.
PROGI: dict[str, tuple[float, str]] = {
    "falszywe_alarmy": (0.15, "max"),
    "top1": (0.85, "min"),
    "top2": (0.95, "min"),
    "nieznane_wieczor": (0.10, "max"),
    "nieznane_rano": (0.10, "max"),
    "czas_wieczor": (20.0, "max"),  # minut na zmiane (srednio, ze zmian z mierzalnym czasem)
    "powtorzone_wieczor": (0.05, "max"),
    "powtorzone_rano": (0.05, "max"),
    "dni_bez_awarii": (5, "min"),  # kolejnych dni (seria biegnaca do konca okresu)
}
PROG_WYKRYWALNOSCI = 0.80  # M2 (PW: wykrywalnosc ubytkow >= 0,3 mm) - tylko do pokazania; metryka wymaga zmiany schematu
OCENA_OK, OCENA_PONIZEJ, OCENA_BRAK, OCENA_SCHEMAT = "OK", "PONIZEJ", "brak danych", "wymaga zmiany schematu"
OCENA_ZA_KROTKI = "za krotki okres"  # dni bez awarii: historia krotsza niz prog i bez awarii - nie da sie jeszcze ocenic
KOD_OK, KOD_BLAD, KOD_PONIZEJ, KOD_BRAK_DANYCH = 0, 2, 3, 4
POWOD_M2 = ("wymaga zmiany schematu: tabela testow wykrywalnosci (testy_wykrywalnosci, migracja bazy do wersji 2 - decyzja "
            "wlasciciela); baza nie zapisuje, ktora praca jest testowa ani jaki ma znany ubytek")
MAX_DOB_NA_STRONIE = 5


def ocena(wartosc: float | None, prog: float, kierunek: str) -> str:
    """"OK" / "PONIZEJ" / "brak danych" (wartosc None). ``kierunek``: "min" (wartosc >= prog) albo "max" (wartosc <= prog)."""
    if wartosc is None:
        return OCENA_BRAK
    dobrze = wartosc >= prog if kierunek == "min" else wartosc <= prog
    return OCENA_OK if dobrze else OCENA_PONIZEJ


def _udzial(a: int, b: int) -> float | None:
    return a / b if b else None


def _minut(od: str, do: str) -> float:
    return (dt.datetime.fromisoformat(do) - dt.datetime.fromisoformat(od)).total_seconds() / 60


def _posiedzenia(punkty: list[tuple[str, bool]], przerwa_min: float) -> list[list]:
    """[[poczatek, koniec, czy_byl_start_skanu], ...] z chwil (czas ISO, czy to start skanu)."""
    wynik: list[list] = []
    for czas, start in sorted(punkty):
        if wynik and _minut(wynik[-1][1], czas) <= przerwa_min:
            wynik[-1][1] = czas
            wynik[-1][2] = wynik[-1][2] or start
        else:
            wynik.append([czas, czas, start])
    return wynik


def posiedzenia(czasy: list[str], przerwa_min: float = PRZERWA_MIN) -> list[tuple[str, str]]:
    """Posiedzenia przy stanowisku z chwil aktywnosci (czasy ISO): kolejne chwile z przerwa najwyzej ``przerwa_min`` minut
    to jedno posiedzenie (poczatek, koniec). Kolejnosc wejscia bez znaczenia."""
    return [(a, b) for a, b, _ in _posiedzenia([(c, False) for c in czasy], przerwa_min)]


def sprawdz_okres(od: str, do: str) -> tuple[dt.date, dt.date]:
    """Daty dob RRRR-MM-DD, ``od`` <= ``do``; inaczej ``ValueError`` z komunikatem dla czlowieka."""
    try:
        d_od, d_do = dt.date.fromisoformat(str(od)), dt.date.fromisoformat(str(do))
    except ValueError:
        raise ValueError(f"okres: daty dob w postaci RRRR-MM-DD (jest od={od!r}, do={do!r})") from None
    if d_od > d_do:
        raise ValueError(f"okres: poczatek {od} jest po koncu {do}")
    return d_od, d_do


def biezaca_doba(granica_doby_godz: int = SE.GRANICA_DOBY_GODZ, teraz: dt.datetime | None = None) -> str:
    """Data biezacej doby roboczej (jak ``Sesja.doba``) - domyslny koniec okresu raportu."""
    return ((teraz or dt.datetime.now()) - dt.timedelta(hours=granica_doby_godz)).date().isoformat()


def parametry_z_ustawien(ust: dict | None) -> dict:
    """Parametry ``policz`` z ``ustawienia.toml``: doba i zmiany (``[sesja]``), prog dwuznacznej (``[match]``); None = domyslne."""
    if ust is None:
        return {"granica_doby_godz": SE.GRANICA_DOBY_GODZ, "zmiany_start_godz": SE.ZMIANY_START_GODZ, "prog_kandydata": SR.PROG_KANDYDATA}
    return {"granica_doby_godz": ust["sesja"]["granica_doby_godz"], "zmiany_start_godz": tuple(ust["sesja"]["zmiany_start_godz"]),
            "prog_kandydata": ust["match"]["prog_ostrzezenia_pokrycie"]}


def bez_kandydata(kandydaci: list[tuple[str | None, float | None, bool]], prog_kandydata: float) -> bool:
    """Praca nieznana - program nie mial kandydata (ta sama regula wieczorem i rano, jak klasa ``dwuznaczna`` / ``nieznana``
    pracy bez decyzji w ``session_rano``): brak 1. kandydata, 1. kandydat z pokryciem ponizej ``prog_kandydata`` albo zaden
    z kandydatow nie jest w indeksie. ``kandydaci``: (sha16, pokrycie, czy_w_indeksie) w kolejnosci programu."""
    if not kandydaci or not kandydaci[0][0] or (kandydaci[0][1] or 0.0) < prog_kandydata:
        return True
    return not any(sha and w_indeksie for sha, _, w_indeksie in kandydaci)


class _SesjaOdczyt(SE.Sesja):
    """``Sesja`` raportu: ``stan_wieczoru`` bez listy "do dofrezowania" i konfliktow - raport ich nie uzywa, a lista biezaca liczy sie
    z calej historii przy kazdej dobie okresu (recenzja PR #29 D1). Reguly skanow, prac i decyzji - bez zmian (dziedziczone)."""

    def do_dofrezowania(self, data: str | None = None) -> list[dict]:
        return []

    def konflikty(self, data: str | None = None, tryb: str = SE.TRYB_WIECZOR) -> list[dict]:
        return []


class _SesjaRanoOdczyt(SR.SesjaRano):
    """``SesjaRano`` raportu: ``stan_pieca`` bez zapisu "Zamknij piec" (lista dla Excela; raport go nie uzywa, a szukanie zapisu
    przeglada caly dziennik dla kazdego pieca - O(piece^2), recenzja PR #29 D1)."""

    def wynik_pieca(self, sesja_pieca_id: int) -> dict | None:
        return None


# --- czesci raportu ---------------------------------------------------------------------------------------------------
def _powtorzone(wiersze: list[dict]) -> dict:
    """Z wierszy (status, n): skany (bez importu) i te, ktore trzeba bylo powtorzyc (``STATUSY_POWTORZONE``)."""
    po_statusie = {w["status"]: w["n"] for w in wiersze if w["status"] != STATUS_IMPORT}
    statusy = {s: po_statusie[s] for s in STATUSY_POWTORZONE if po_statusie.get(s)}
    skany, powt = sum(po_statusie.values()), sum(statusy.values())
    return {"skany": skany, "powtorzone": powt, "udzial": _udzial(powt, skany), "statusy": statusy}


def _punkty_aktywnosci(baza: B.Baza, start: str, koniec: str, przerwa_min: float) -> dict[str, list[tuple[str, bool]]]:
    """Chwile aktywnosci przy stanowisku w okresie, osobno wieczor i rano, jako (czas, czy start skanu): przyjecie skanu, decyzja
    o pracy albo skanie danego trybu (decyzje bez pracy i skanu - zamkniecie reczne, ponowne otwarcie pieca, przeniesienie
    skanow - sa poranne), otwarcie i zamkniecie pieca (rano) oraz zdarzenia dziennika: kazde zdarzenie okna (``ui``, w tym
    ``start_skanu``), wykrycie pliku skanu (``nowy_skan`` - koniec skanowania, gdy przycisk "Skanuj" nie jest uzywany) i podglad
    3D. Zdarzenie ze skanem nalezy do trybu skanu; bez skanu - do trybu najblizszego w czasie skanu, o ile ten jest najwyzej
    ``przerwa_min`` minut od niego (inaczej sie nie liczy)."""
    punkty: dict[str, list[tuple[str, bool]]] = {TRYB_WIECZOR: [], TRYB_RANO: []}
    for w in baza.wiersze("SELECT tryb, czas_analizy FROM skany WHERE tryb IN (?, ?) AND czas_analizy >= ? AND czas_analizy < ?",
                          (TRYB_WIECZOR, TRYB_RANO, start, koniec)):
        punkty[w["tryb"]].append((w["czas_analizy"], False))
    for w in baza.wiersze(
            """SELECT d.czas, d.praca_id, d.skan_id, COALESCE(sp.tryb, ss.tryb) AS tryb FROM decyzje d
               LEFT JOIN prace p ON p.id = d.praca_id LEFT JOIN skany sp ON sp.id = p.skan_id LEFT JOIN skany ss ON ss.id = d.skan_id
               WHERE d.czas >= ? AND d.czas < ?""", (start, koniec)):
        tryb = TRYB_RANO if w["praca_id"] is None and w["skan_id"] is None else w["tryb"]
        if tryb in punkty:  # decyzje z importu okna testowego (skan bez trybu) - poza metrykami
            punkty[tryb].append((w["czas"], False))
    for w in baza.wiersze("SELECT otwarto, zamknieto FROM sesje_pieca WHERE (otwarto >= ? AND otwarto < ?) OR (zamknieto >= ? AND zamknieto < ?)",
                          (start, koniec, start, koniec)):
        punkty[TRYB_RANO] += [(c, False) for c in (w["otwarto"], w["zamknieto"]) if c and start <= c < koniec]
    margines = dt.timedelta(minutes=przerwa_min)
    skany = baza.wiersze("SELECT tryb, czas_analizy FROM skany WHERE tryb IN (?, ?) AND czas_analizy >= ? AND czas_analizy < ? "
                         "ORDER BY czas_analizy, id", (TRYB_WIECZOR, TRYB_RANO, (dt.datetime.fromisoformat(start) - margines).isoformat(),
                                                       (dt.datetime.fromisoformat(koniec) + margines).isoformat()))
    czasy = [s["czas_analizy"] for s in skany]
    for w in baza.wiersze(
            f"""SELECT z.czas, z.typ, s.tryb FROM zdarzenia z LEFT JOIN skany s ON s.id = z.skan_id
                WHERE (z.zrodlo = ? OR z.typ IN ({', '.join('?' * len(TYPY_AKTYWNOSCI))})) AND z.czas >= ? AND z.czas < ?""",
            (ZRODLO_OKNA, *TYPY_AKTYWNOSCI, start, koniec)):
        tryb = w["tryb"]
        if tryb is None:  # bez skanu: tryb najblizszego skanu w promieniu przerwy (remis - nastepny)
            i = bisect_left(czasy, w["czas"])
            sasiedzi = [(abs(_minut(w["czas"], czasy[j])), j > i - 1, j) for j in (i - 1, i) if 0 <= j < len(czasy)]
            blisko = [s for s in sasiedzi if s[0] <= przerwa_min]
            tryb = skany[min(blisko, key=lambda s: (s[0], not s[1]))[2]]["tryb"] if blisko else None
        if tryb in punkty:
            punkty[tryb].append((w["czas"], w["typ"] == TYP_START_SKANU))
    return punkty


def _czas(punkty: list[tuple[str, bool]], sesja: SE.Sesja, przerwa_min: float, prog_min: float | None = None) -> dict:
    """Czas przy stanowisku: posiedzenia, suma na zmiane (doba robocza + numer zmiany poczatku posiedzenia). Zmiana z sama
    pojedyncza chwila (np. skan bez decyzji) nie ma mierzalnego czasu - liczy sie w ``zmian_bez_danych``, nie w sredniej."""
    sit = _posiedzenia(punkty, przerwa_min)
    na_zmiane: dict[tuple[str, int], float] = {}
    for a, b, _ in sit:
        klucz = (sesja.doba(a), sesja.zmiana(a))
        na_zmiane[klucz] = na_zmiane.get(klucz, 0.0) + _minut(a, b)
    z_czasem = [v for v in na_zmiane.values() if v > 0]
    return {"posiedzen": len(sit), "posiedzen_bez_startu": sum(1 for s in sit if not s[2]), "zmian": len(na_zmiane),
            "zmian_bez_danych": len(na_zmiane) - len(z_czasem), "suma_min": sum(z_czasem),
            "srednio_min": sum(z_czasem) / len(z_czasem) if z_czasem else None, "max_min": max(z_czasem) if z_czasem else None,
            "zmian_ponad_prog": sum(1 for v in z_czasem if v > prog_min) if prog_min is not None else None}


def _wieczor(baza: B.Baza, sesja: SE.Sesja, doby: list[str], start: str, koniec: str, punkty: list, przerwa_min: float,
             prog_kandydata: float) -> dict:
    indeks = {w["sha16"] for w in baza.wiersze("SELECT DISTINCT sha16 FROM projekty WHERE usuniety = 0 AND sha16 IS NOT NULL")}
    stany = [sesja.stan_wieczoru(doba) for doba in doby]
    czekajace = {x["poprzedni_id"] for st in stany for x in st["do_potwierdzenia"]}  # ponowny skan bez odpowiedzi: jak zastapiony
    aktywne = do_powtorzenia = w_mianowniku = 0
    prace = czerwone = falszywe = ukruszone = bez_decyzji = niewykryte = nieznane = dwuznaczne = 0
    for st in stany:
        for sk in st["skany"]:
            if not sk["aktywny"]:  # zastapiony, niezgodny uklad, plytka nie z trybu, blad: decyzje o jego pracach sie nie licza
                continue
            aktywne += 1
            if sk["status"] != SE.STATUS_PRZYJETY:  # do powtorzenia: decyzji na nim nie ma, plytka i tak bedzie skanowana ponownie
                do_powtorzenia += 1
                continue
            if sk["id"] in czekajace:
                continue
            w_mianowniku += 1
            for p in sk["prace"]:
                prace += 1
                decyzja = p["decyzja"]
                if p["status_gniazda"] == KOLOR_ALARMU:
                    czerwone += 1
                    if decyzja == "ok":
                        falszywe += 1
                    elif decyzja in SE.DECYZJE_UKRUSZENIA:
                        ukruszone += 1
                    else:
                        bez_decyzji += 1
                elif decyzja in SE.DECYZJE_UKRUSZENIA:  # tryb cienia: technik zaznaczyl ukruszenie, ktorego program nie wskazal
                    niewykryte += 1
                kand = [(p[f"kandydat{i}_sha16"], p[f"kandydat{i}_pokrycie"], p[f"kandydat{i}_sha16"] in indeks) for i in (1, 2)
                        if p[f"kandydat{i}_sha16"]]
                if bez_kandydata(kand, prog_kandydata):
                    nieznane += 1
                elif p["sha16"] is None:  # szara z kandydatem >= progu (bliscy kandydaci) - rano bylaby dwuznaczna
                    dwuznaczne += 1
    wiersze = baza.wiersze("SELECT status, count(*) AS n FROM skany WHERE tryb = ? AND czas_analizy >= ? AND czas_analizy < ? GROUP BY status",
                           (TRYB_WIECZOR, start, koniec))
    powt = _powtorzone(wiersze)
    return {"skany": powt["skany"], "skany_aktywne": aktywne, "skany_mianownik": w_mianowniku, "skany_do_powtorzenia": do_powtorzenia,
            "skany_do_potwierdzenia": len(czekajace), "prace": prace, "czerwone": czerwone, "falszywe_alarmy": falszywe,
            "udzial_falszywych": _udzial(falszywe, prace), "czerwone_ukruszone": ukruszone, "czerwone_bez_decyzji": bez_decyzji,
            "niewykryte_cien": niewykryte, "wykrywalnosc_cien": _udzial(ukruszone, ukruszone + niewykryte), "nieznane": nieznane,
            "udzial_nieznanych": _udzial(nieznane, prace), "dwuznaczne": dwuznaczne, "powtorzone": powt,
            "czas": _czas(punkty, sesja, przerwa_min, PROGI["czas_wieczor"][0])}


def _rano(baza: B.Baza, rano: SR.SesjaRano, od: str, do: str, punkty: list, przerwa_min: float) -> dict:
    piece = baza.wiersze("SELECT id, otwarto, zamknieto FROM sesje_pieca WHERE data >= ? AND data <= ? ORDER BY id", (od, do))
    zamkniete = [p for p in piece if p["zamknieto"]]
    klasy: dict[str, int] = {}
    prace = z_prawda = top1 = top2 = top2_projekt = odrzucone = nieznane = 0
    for piec in zamkniete:
        for sk in rano.stan_pieca(piec["id"])["skany"]:
            if not sk["aktywny"]:  # nieaktywny albo pominiety
                continue
            for p in sk["prace"]:
                if p["klasa"] is None:
                    continue
                prace += 1
                klasy[p["klasa"]] = klasy.get(p["klasa"], 0) + 1
                kand = p["kandydaci"]
                bez = bez_kandydata([(k["sha16"], k["pokrycie"], bool(k["projekty"])) for k in kand], rano.prog_kandydata)
                nieznane += bez
                if p["klasa"] in KLASY_Z_PRAWDA and p["sha16"]:
                    z_prawda += 1
                    shas = [k["sha16"] for k in kand[:2]]
                    kuwety = {q["kuweta"] for k in kand[:2] for q in k["projekty"] if q["kuweta"]}
                    top1 += shas[:1] == [p["sha16"]]
                    top2_projekt += p["sha16"] in shas
                    top2 += p["sha16"] in shas or (bool(p["kuweta"]) and p["kuweta"] in kuwety)
                elif p["decyzja"] == SR.RODZAJ_PRZYPISANIE and p["projekt_id"] is None and not bez:
                    z_prawda += 1  # technik odrzucil propozycje programu ("bez projektu", takze rozstrzygniecie konfliktu): chybienie
                    odrzucone += 1
    czasy_piecow = [_minut(p["otwarto"], p["zamknieto"]) for p in zamkniete if p["otwarto"]]
    ids = [p["id"] for p in zamkniete]
    wiersze = []
    for i in range(0, len(ids), 500):
        czesc = ids[i:i + 500]
        wiersze += baza.wiersze(f"SELECT status, count(*) AS n FROM skany WHERE tryb = ? AND sesja_pieca_id IN ({', '.join('?' * len(czesc))}) "
                                f"GROUP BY status", (TRYB_RANO, *czesc))
    po_statusie: dict[str, int] = {}
    for w in wiersze:
        po_statusie[w["status"]] = po_statusie.get(w["status"], 0) + w["n"]
    return {"piece": len(zamkniete), "piece_otwarte": len(piece) - len(zamkniete), "prace": prace, "klasy": klasy, "z_prawda": z_prawda,
            "top1": top1, "top2": top2, "top2_projekt": top2_projekt, "odrzucone": odrzucone, "udzial_top1": _udzial(top1, z_prawda),
            "udzial_top2": _udzial(top2, z_prawda), "nieznane": nieznane, "udzial_nieznanych": _udzial(nieznane, prace),
            "dwuznaczne": klasy.get(SR.KLASA_DWUZNACZNA, 0),
            "powtorzone": _powtorzone([{"status": s, "n": n} for s, n in po_statusie.items()]), "czas": _czas(punkty, rano.sesja, przerwa_min),
            "czas_pieca_min": {"mediana": statistics.median(czasy_piecow) if czasy_piecow else None,
                               "max": max(czasy_piecow) if czasy_piecow else None}}


def _stabilnosc(baza: B.Baza, sesja: SE.Sesja, start: str, koniec: str) -> dict:
    """Dni pracy (doby z wpisami dziennika) i awarie wymagajace restartu: ``program_start``, gdy od poprzedniego startu nie bylo
    ``program_stop`` (program zabity albo padl - awaria w chwili ostatniego wpisu dziennika przed ponownym startem). Dziennik
    czytany caly w kolejnosci dopisywania (id): start PO okresie domyka awarie z okresu, seria liczy sie z historii sprzed okresu.
    ``silnik_nie_startuje`` - osobny licznik (program umie wrocic sam, gdy proces silnika jednak wystartuje)."""
    wpisy = baza.wiersze("SELECT czas, typ FROM zdarzenia ORDER BY id")
    awarie: list[str] = []
    uruchomiony, poprzedni, na_koniec = False, None, False
    for w in wpisy:
        if w["typ"] == TYP_START:
            if uruchomiony and poprzedni is not None:
                awarie.append(poprzedni)
            uruchomiony = True
        elif w["typ"] == TYP_STOP:
            uruchomiony = False
        poprzedni = w["czas"]
        if w["czas"] < koniec:
            na_koniec = uruchomiony
    historia = sorted({sesja.doba(w["czas"]) for w in wpisy if w["czas"] < koniec})
    z_awaria_hist = {sesja.doba(c) for c in awarie if c < koniec}
    seria = najdluzsza = 0
    for d in historia:
        seria = 0 if d in z_awaria_hist else seria + 1
        najdluzsza = max(najdluzsza, seria)
    w_okresie = [c for c in awarie if start <= c < koniec]
    dni_okresu = {sesja.doba(x["czas"]) for x in wpisy if start <= x["czas"] < koniec}
    return {"dni_pracy": len(dni_okresu),
            "dni_z_awaria": len({sesja.doba(c) for c in w_okresie}), "awarie": len(w_okresie), AWARIA_RESTART: len(w_okresie),
            AWARIA_SILNIK: sum(1 for w in wpisy if w["typ"] == TYP_SILNIK and start <= w["czas"] < koniec),
            "dni_historii": len(historia), "awarie_w_historii": len(z_awaria_hist), "najdluzsza_seria": najdluzsza, "obecna_seria": seria,
            "doby_z_awaria": sorted({sesja.doba(c) for c in w_okresie}), "uruchomiony_na_koniec": na_koniec}


def _wiersz(klucz: str, nazwa: str, wartosc: float | None, licznik: int | None = None, mianownik: int | None = None,
            jednostka: str = "%", ocena_: str | None = None) -> dict:
    prog, kierunek = PROGI[klucz]
    return {"klucz": klucz, "nazwa": nazwa, "wartosc": wartosc, "licznik": licznik, "mianownik": mianownik, "prog": prog,
            "kierunek": kierunek, "jednostka": jednostka, "ocena": ocena_ or ocena(wartosc, prog, kierunek)}


def _wiersze(w: dict) -> list[dict]:
    """Wiersze tabeli metryk (kolejnosc strony); metryki trybu pominietego nie maja wiersza."""
    wi, ra, st = w["wieczor"], w["rano"], w["stabilnosc"]
    lista = []
    if wi is not None:
        lista.append(_wiersz("falszywe_alarmy", "falszywe alarmy (czerwone uznane za OK)", wi["udzial_falszywych"], wi["falszywe_alarmy"], wi["prace"]))
    if ra is not None:
        lista.append(_wiersz("top1", "top-1 wzgledem decyzji technika (rano)", ra["udzial_top1"], ra["top1"], ra["z_prawda"]))
        lista.append(_wiersz("top2", "top-2: kuweta wsrod 2 kandydatow (rano)", ra["udzial_top2"], ra["top2"], ra["z_prawda"]))
    if wi is not None:
        lista.append(_wiersz("nieznane_wieczor", "prace nieznane (bez kandydata) - wieczor", wi["udzial_nieznanych"], wi["nieznane"], wi["prace"]))
    if ra is not None:
        lista.append(_wiersz("nieznane_rano", "prace nieznane (bez kandydata) - rano", ra["udzial_nieznanych"], ra["nieznane"], ra["prace"]))
    if wi is not None:
        lista.append(_wiersz("czas_wieczor", "czas przy stanowisku wieczorem (na zmiane)", wi["czas"]["srednio_min"], jednostka="min"))
        p = wi["powtorzone"]
        lista.append(_wiersz("powtorzone_wieczor", "skany powtorzone - wieczor", p["udzial"], p["powtorzone"], p["skany"]))
    if ra is not None:
        p = ra["powtorzone"]
        lista.append(_wiersz("powtorzone_rano", "skany powtorzone - rano", p["udzial"], p["powtorzone"], p["skany"]))
    seria = st["obecna_seria"] if st["dni_historii"] else None
    prog = PROGI["dni_bez_awarii"][0]
    za_krotki = seria is not None and seria < prog and not st["awarie_w_historii"] and st["dni_historii"] < prog
    lista.append(_wiersz("dni_bez_awarii", "dni bez awarii (seria do konca okresu)", seria, jednostka="dni",
                         ocena_=OCENA_ZA_KROTKI if za_krotki else None))
    lista.append({"klucz": "m2", "nazwa": "M2 tabela testow wykrywalnosci", "wartosc": None, "licznik": None, "mianownik": None,
                  "prog": PROG_WYKRYWALNOSCI, "kierunek": "min", "jednostka": "%", "ocena": OCENA_SCHEMAT})
    return lista


def policz(baza: B.Baza, od: str, do: str, tryb: str = TRYB_OBA, *, granica_doby_godz: int = SE.GRANICA_DOBY_GODZ,
           zmiany_start_godz: tuple[int, ...] | list[int] = SE.ZMIANY_START_GODZ, prog_kandydata: float = SR.PROG_KANDYDATA,
           przerwa_min: float = PRZERWA_MIN, teraz: str | None = None) -> dict:
    """Wszystkie metryki okresu ``od`` .. ``do`` (doby robocze RRRR-MM-DD, wlacznie) dla trybu ``wieczor`` / ``rano`` / ``oba``.

    Zwraca zwykle dane (JSON): ``okres``, ``parametry``, ``wieczor`` / ``rano`` (None dla trybu pominietego), ``stabilnosc``,
    ``m2``, ``metryki`` (wiersze strony z ocena wzgledem ``PROGI``), ``ponizej_progu``, ``bez_danych``, ``kod`` (0 / 3 / 4).
    Baza tylko czytana, w jednej transakcji odczytu (otwarta tu, gdy wywolujacy nie ma swojej). Zly okres albo tryb: ``ValueError``.
    """
    if tryb not in TRYBY:
        raise ValueError(f"tryb raportu: {', '.join(TRYBY)} (jest {tryb!r})")
    d_od, d_do = sprawdz_okres(od, do)
    sesja = _SesjaOdczyt(baza, granica_doby_godz=granica_doby_godz, zmiany_start_godz=zmiany_start_godz)  # tylko odczyt (bez operatora)
    rano = _SesjaRanoOdczyt(sesja, prog_kandydata=prog_kandydata)
    doby = [(d_od + dt.timedelta(days=i)).isoformat() for i in range((d_do - d_od).days + 1)]
    granica = dt.time(granica_doby_godz)  # te same granice co Sesja.doba / _przedzial_doby
    s_start = dt.datetime.combine(d_od, granica).isoformat()
    s_koniec = dt.datetime.combine(d_do + dt.timedelta(days=1), granica).isoformat()
    wlasna = not baza.polaczenie.in_transaction
    if wlasna:
        baza.wykonaj("BEGIN")  # transakcja odczytu (dziala tez na polaczeniu tylko do odczytu): caly raport z jednego stanu bazy
    try:
        punkty = _punkty_aktywnosci(baza, s_start, s_koniec, przerwa_min)
        w: dict[str, Any] = {
            "wersja": WERSJA, "wygenerowano": teraz or dt.datetime.now().replace(microsecond=0).isoformat(), "schemat_bazy": baza.wersja(),
            "okres": {"od": d_od.isoformat(), "do": d_do.isoformat(), "tryb": tryb, "doby": len(doby)},
            "parametry": {"granica_doby_godz": granica_doby_godz, "zmiany_start_godz": list(zmiany_start_godz),
                          "prog_kandydata": prog_kandydata, "przerwa_min": przerwa_min},
            "wieczor": (_wieczor(baza, sesja, doby, s_start, s_koniec, punkty[TRYB_WIECZOR], przerwa_min, prog_kandydata)
                        if tryb != TRYB_RANO else None),
            "rano": _rano(baza, rano, d_od.isoformat(), d_do.isoformat(), punkty[TRYB_RANO], przerwa_min) if tryb != TRYB_WIECZOR else None,
            "stabilnosc": _stabilnosc(baza, sesja, s_start, s_koniec),
            "m2": {"dostepne": False, "powod": POWOD_M2},
        }
    finally:
        if wlasna and baza.polaczenie.in_transaction:
            baza.wykonaj("ROLLBACK")  # nic nie bylo zapisywane - zwolnienie blokady odczytu
    w["metryki"] = _wiersze(w)
    w["ponizej_progu"] = [m["klucz"] for m in w["metryki"] if m["ocena"] == OCENA_PONIZEJ]
    w["bez_danych"] = [m["klucz"] for m in w["metryki"] if m["ocena"] in (OCENA_BRAK, OCENA_ZA_KROTKI)]
    ocenione = [m for m in w["metryki"] if m["ocena"] in (OCENA_OK, OCENA_PONIZEJ)]
    w["kod"] = KOD_PONIZEJ if w["ponizej_progu"] else (KOD_OK if ocenione else KOD_BRAK_DANYCH)
    return w


# --- strona -----------------------------------------------------------------------------------------------------------
def _proc(x: float | None) -> str:
    return "-" if x is None else f"{100 * x:.1f}%"


def _min(x: float | None) -> str:
    return "-" if x is None else f"{x:.1f}"


def _wartosc(m: dict) -> str:
    if m["wartosc"] is None:
        return "-"
    if m["jednostka"] == "%":
        return _proc(m["wartosc"])
    if m["jednostka"] == "min":
        return f"{m['wartosc']:.1f} min"
    return f"{m['wartosc']:g} {m['jednostka']}"


def _prog(m: dict) -> str:
    znak = ">=" if m["kierunek"] == "min" else "<="
    if m["jednostka"] == "%":
        return f"{znak} {100 * m['prog']:g}%"
    return f"{znak} {m['prog']:g} {m['jednostka']}"


def _statusy(p: dict) -> str:
    s = p["statusy"]
    return (f"zastapione {s.get(SE.STATUS_ZASTAPIONY, 0)}, do powtorzenia {s.get(SE.STATUS_DO_POWTORZENIA, 0)}, "
            f"niezgodny uklad {s.get(SE.STATUS_NIEZGODNY_UKLAD, 0)}, plytka nie z trybu {s.get(SE.STATUS_PLYTKA_NIE_Z_TRYBU, 0)}, "
            f"blad {s.get(SE.STATUS_BLAD, 0)}")


def _czas_linia(cz: dict) -> str:
    tekst = (f"zmian {cz['zmian']} (bez danych {cz['zmian_bez_danych']}), posiedzen {cz['posiedzen']} (bez start_skanu "
             f"{cz['posiedzen_bez_startu']}), razem {_min(cz['suma_min'])} min, srednio {_min(cz['srednio_min'])}, max {_min(cz['max_min'])}")
    return tekst + (f", zmian > 20 min: {cz['zmian_ponad_prog']}" if cz["zmian_ponad_prog"] is not None else "")


def strona(w: dict) -> list[str]:
    """Jedna strona tekstowa (do 60 linii, ASCII): tabela metryk z progami, szczegoly wieczoru, poranka i stabilnosci, M2, wynik."""
    ok = w["okres"]
    linie = [f"RAPORT METRYK STANOWISKA - okres {ok['od']} .. {ok['do']} (dob: {ok['doby']}), tryb: {ok['tryb']}",
             f"wygenerowano {w['wygenerowano']}; baza programu (schemat {w['schemat_bazy']}, tylko odczyt); progi odbioru: plan "
             f"wdrozenia, \"Testy odbiorcze i kryteria\"", ""]
    naglowek = f"{'METRYKA':<44} {'WARTOSC':>9} {'LICZNIK':>8}   {'PROG':<10} OCENA"
    linie += [naglowek, "-" * len(naglowek)]
    for m in w["metryki"]:
        licznik = f"{m['licznik']}/{m['mianownik']}" if m["licznik"] is not None else "-"
        linie.append(f"{m['nazwa']:<44} {_wartosc(m):>9} {licznik:>8}   {_prog(m):<10} {m['ocena']}")
    linie.append("")
    wi = w["wieczor"]
    if wi is None:
        linie.append(f"WIECZOR: pominiety (tryb {ok['tryb']})")
    else:
        linie += [
            f"WIECZOR: skany {wi['skany']} (aktywne {wi['skany_aktywne']}), prace {wi['prace']} w skanach przyjetych ({wi['skany_mianownik']}); "
            f"poza: do powtorzenia {wi['skany_do_powtorzenia']}, ponowny skan bez potwierdzenia {wi['skany_do_potwierdzenia']}",
            f"  czerwone {wi['czerwone']}: OK (falszywy alarm) {wi['falszywe_alarmy']}, Ukruszona {wi['czerwone_ukruszone']}, "
            f"bez decyzji {wi['czerwone_bez_decyzji']}",
            f"  tryb cienia: ukruszone, ktorych program nie wskazal {wi['niewykryte_cien']}; wykrywalnosc wzgledem technika "
            f"{_proc(wi['wykrywalnosc_cien'])} ({wi['czerwone_ukruszone']}/{wi['czerwone_ukruszone'] + wi['niewykryte_cien']}) - nie zastepuje M2",
            f"  nieznane (bez kandydata) {wi['nieznane']}; szare z kandydatem (dwuznaczne) {wi['dwuznaczne']}",
            f"  skany powtorzone {wi['powtorzone']['powtorzone']} z {wi['powtorzone']['skany']}: {_statusy(wi['powtorzone'])}",
            f"  czas: {_czas_linia(wi['czas'])}"]
    ra = w["rano"]
    if ra is None:
        linie.append(f"RANO: pominiety (tryb {ok['tryb']})")
    else:
        cp = ra["czas_pieca_min"]
        klasy = ", ".join(f"{k} {ra['klasy'].get(k, 0)}" for k in (SR.KLASA_PEWNA, SR.KLASA_PRZYPISANA, SR.KLASA_POPRAWKA, SR.KLASA_DWUZNACZNA,
                                                                   SR.KLASA_NIEZNANA, SR.KLASA_KONFLIKT, SR.KLASA_DO_POWTORZENIA) if ra["klasy"].get(k))
        linie += [
            f"RANO: piece zamkniete {ra['piece']} (niezamkniete {ra['piece_otwarte']} - poza metrykami), prace {ra['prace']}",
            f"  klasy: {klasy or '-'}",
            f"  top-1 {ra['top1']} z {ra['z_prawda']}, top-2 {ra['top2']} z {ra['z_prawda']} (po projekcie {ra['top2_projekt']}); odrzucone przez "
            f"technika ('bez projektu', chybione) {ra['odrzucone']}; dwuznaczne nierozstrzygniete {ra['dwuznaczne']}",
            f"  skany powtorzone {ra['powtorzone']['powtorzone']} z {ra['powtorzone']['skany']}: {_statusy(ra['powtorzone'])}",
            f"  czas (informacyjnie): {_czas_linia(ra['czas'])}",
            f"  piec od otwarcia do zamkniecia (nie stoper z PW): mediana {_min(cp['mediana'])} min, najwiecej {_min(cp['max'])} min"]
    st = w["stabilnosc"]
    doby = st["doby_z_awaria"]
    lista = ", ".join(doby[:MAX_DOB_NA_STRONIE]) + (f" (+{len(doby) - MAX_DOB_NA_STRONIE})" if len(doby) > MAX_DOB_NA_STRONIE else "")
    linie += [
        f"STABILNOSC: dni pracy {st['dni_pracy']} (w historii {st['dni_historii']}), z awaria {st['dni_z_awaria']}, awarii {st['awarie']} "
        f"(restart bez program_stop); silnik nie startuje {st[AWARIA_SILNIK]} (nie awaria)",
        f"  seria bez awarii do konca okresu {st['obecna_seria']} dni, najdluzsza {st['najdluzsza_seria']}; doby z awaria: {lista or '-'}",
        f"  program uruchomiony bez program_stop na koniec okresu: {'tak (dziala albo padl - awaria liczy sie po ponownym starcie)' if st['uruchomiony_na_koniec'] else 'nie'}",
        "M2: tabela testow wykrywalnosci (5 prac tygodniowo ze znanymi ubytkami) - wymaga zmiany schematu:",
        "  tabela testy_wykrywalnosci (migracja bazy do wersji 2, decyzja wlasciciela); do tego czasu brak danych",
        f"UWAGI: posiedzenie = start skanu, wykrycie pliku, klikniecie, przyjecie skanu, decyzja; przerwa > "
        f"{w['parametry']['przerwa_min']:g} min = koniec;",
        "  blizniacze prace implantologiczne (PW: poza trafnoscia) nie sa wykluczone - baza ich nie rozroznia"]
    bez = len(w["bez_danych"])
    razem = sum(1 for m in w["metryki"] if m["klucz"] != "m2")
    if w["kod"] == KOD_PONIZEJ:
        linie += [f"WYNIK: PONIZEJ PROGU (kod {w['kod']}; metryk bez danych {bez} z {razem}):", "  " + ", ".join(w["ponizej_progu"])]
    elif w["kod"] == KOD_BRAK_DANYCH:
        linie.append(f"WYNIK: BRAK DANYCH - zadna metryka nie dala sie ocenic ({bez} z {razem}); sprawdz --baza i okres (kod {w['kod']})")
    else:
        linie.append(f"WYNIK: metryki z danymi w progu odbioru (kod {w['kod']}; bez danych {bez} z {razem})")
    return linie
