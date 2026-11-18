"""metryki - metryki odbiorcze stanowiska liczone z bazy programu (E3-A10).

M1 (plan etapu 3, 3.3; PW "Testy odbiorcze i kryteria"): kazda metryke program liczy sam z wlasnego logu, raport = jedno
polecenie i jedna strona (``narzedzia/raport_metryk.py``). Zrodla - wylacznie istniejace tabele schematu w wersji 1
(``skany``, ``prace``, ``decyzje``, ``sesje_pieca``, ``zdarzenia``) czytane przez publiczne API sesji, zeby reguly byly te
same co na ekranie: ``Sesja.stan_wieczoru`` (skany aktywne, decyzja obowiazujaca po cofnieciach i zastapieniach) i
``SesjaRano.stan_pieca`` (klasa pracy porannej, przypisanie po decyzjach technika). Proste liczniki statusow i czasy
aktywnosci - zapytania SELECT. Modul TYLKO CZYTA (baza otwarta ``tylko_odczyt`` wystarcza) i nie zmienia schematu: tabela
testow wykrywalnosci (M2) wymaga zmiany schematu - wiersz M2 ma ocene "wymaga zmiany schematu" i nie ma wartosci.

Dane osobowe: wynik (slownik / JSON) i strona maja tylko liczby, daty dob i nazwy metryk - zadnych nazw folderow, plikow,
skanow ani osob (operator z ``decyzje.operator`` nie jest czytany).

Definicje (szczegoly i uzasadnienia: ``opisy_modulow/metryki.md``):
- okres = doby robocze ``od`` .. ``do`` (wlacznie; doba od ``granica_doby_godz`` do tej samej godziny nastepnego dnia);
  wieczor i skany: ``skany.czas_analizy`` w okresie; rano (klasy, top-1/2): piece ZAMKNIETE z ``sesje_pieca.data`` w okresie;
- falszywe alarmy = prace skanow wieczornych aktywnych z ocena programu ``czerwony`` i obowiazujaca decyzja "OK",
  udzial w calosci prac skanow aktywnych (PW);
- top-1 / top-2 = praca poranna z projektem po decyzjach technika (klasa pewna, przypisana, poprawka) - projekt jest
  1. kandydatem programu / jest wsrod 2 pierwszych; mianownik = takie prace;
- prace nieznane = wieczor: praca bez przypisania (szara, bez kandydata); rano: klasa ``nieznana``;
- czas przy stanowisku = suma posiedzen (start skanu, przyjecie skanu, decyzja; przerwa > ``przerwa_min`` konczy
  posiedzenie) na zmiane;
- skany powtorzone = skany zastapione ponownym skanem albo zakonczone statusem do powtorzenia / niezgodny uklad / plytka
  nie z trybu / blad, udzial we wszystkich skanach;
- dni bez awarii = seria kolejnych dob z wpisami dziennika bez awarii wymagajacej restartu (``program_start`` bez
  wczesniejszego ``program_stop`` albo ``silnik_nie_startuje``).
"""
from __future__ import annotations

import datetime as dt
import statistics
from bisect import bisect_left
from typing import Any

from . import baza as B
from . import session as SE
from . import session_rano as SR

WERSJA = "etap3-A10"
TRYB_WIECZOR, TRYB_RANO, TRYB_OBA = SE.TRYB_WIECZOR, SE.TRYB_RANO, "oba"
TRYBY = (TRYB_WIECZOR, TRYB_RANO, TRYB_OBA)
PRZERWA_MIN = 10  # [PROPOZYCJA] dluzsza przerwa w aktywnosci = technik odszedl od stanowiska (koniec posiedzenia)
OKRES_DOMYSLNY_DOB = 7  # raport bez --od: tydzien konczacy sie na --do
STATUS_IMPORT = "import"  # skany z okna testowego (narzedzia/import_decyzji.py) - poza metrykami
STATUSY_POWTORZONE = (SE.STATUS_ZASTAPIONY, SE.STATUS_DO_POWTORZENIA, SE.STATUS_NIEZGODNY_UKLAD, SE.STATUS_PLYTKA_NIE_Z_TRYBU, SE.STATUS_BLAD)
KLASY_Z_PRAWDA = (SR.KLASA_PEWNA, SR.KLASA_PRZYPISANA, SR.KLASA_POPRAWKA)  # praca poranna z projektem obowiazujacym po decyzjach technika
KOLOR_ALARMU = "czerwony"  # ocena programu "UBYTEK" (porownaj.INSPECT_NA_STATUS)
TYP_START, TYP_STOP, TYP_SILNIK, TYP_START_SKANU = "program_start", "program_stop", "silnik_nie_startuje", "start_skanu"  # = aplikacja.py
AWARIA_RESTART, AWARIA_SILNIK = "restart_bez_zamkniecia", "silnik_nie_startuje"

# Progi odbioru z PW "Testy odbiorcze i kryteria" (kolumna "Prog odbioru", nie "Cel po 3 miesiacach"); wartosc rowna progowi zalicza.
# Nie stroi sie ich pod wynik - zmiana tylko po zmianie planu wdrozenia.
PROGI: dict[str, tuple[float, str]] = {
    "falszywe_alarmy": (0.15, "max"),
    "top1": (0.85, "min"),
    "top2": (0.95, "min"),
    "nieznane_wieczor": (0.10, "max"),
    "nieznane_rano": (0.10, "max"),
    "czas_wieczor": (20.0, "max"),  # minut na zmiane (srednio)
    "powtorzone_wieczor": (0.05, "max"),
    "powtorzone_rano": (0.05, "max"),
    "dni_bez_awarii": (5, "min"),  # kolejnych dni (najdluzsza seria w okresie)
}
PROG_WYKRYWALNOSCI = 0.80  # M2 (PW: wykrywalnosc ubytkow >= 0,3 mm) - tylko do pokazania; metryka wymaga zmiany schematu
OCENA_OK, OCENA_PONIZEJ, OCENA_BRAK, OCENA_SCHEMAT = "OK", "PONIZEJ", "brak danych", "wymaga zmiany schematu"
KOD_OK, KOD_BLAD, KOD_PONIZEJ = 0, 2, 3
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


def posiedzenia(czasy: list[str], przerwa_min: float = PRZERWA_MIN) -> list[tuple[str, str]]:
    """Posiedzenia przy stanowisku z chwil aktywnosci (czasy ISO): kolejne chwile z przerwa najwyzej ``przerwa_min`` minut
    to jedno posiedzenie (poczatek, koniec). Kolejnosc wejscia bez znaczenia."""
    wynik: list[tuple[str, str]] = []
    for c in sorted(czasy):
        if wynik and _minut(wynik[-1][1], c) <= przerwa_min:
            wynik[-1] = (wynik[-1][0], c)
        else:
            wynik.append((c, c))
    return wynik


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


# --- czesci raportu ---------------------------------------------------------------------------------------------------
def _powtorzone(baza: B.Baza, tryb: str, start: str, koniec: str) -> dict:
    """Skany trybu przyjete w okresie (bez importu) i te, ktore trzeba bylo powtorzyc (``STATUSY_POWTORZONE``)."""
    wiersze = baza.wiersze("SELECT status, count(*) AS n FROM skany WHERE tryb = ? AND czas_analizy >= ? AND czas_analizy < ? "
                           "AND status != ? GROUP BY status", (tryb, start, koniec, STATUS_IMPORT))
    po_statusie = {w["status"]: w["n"] for w in wiersze}
    statusy = {s: po_statusie[s] for s in STATUSY_POWTORZONE if po_statusie.get(s)}
    skany, powt = sum(po_statusie.values()), sum(statusy.values())
    return {"skany": skany, "powtorzone": powt, "udzial": _udzial(powt, skany), "statusy": statusy}


def _punkty_aktywnosci(baza: B.Baza, start: str, koniec: str, przerwa_min: float, koniec_startow: str) -> dict[str, list[str]]:
    """Chwile aktywnosci przy stanowisku w okresie, osobno wieczor i rano: przyjecie skanu, decyzja o pracy albo skanie danego
    trybu (decyzje bez pracy i skanu - zamkniecie reczne, ponowne otwarcie pieca, przeniesienie skanow - sa poranne), otwarcie
    i zamkniecie pieca (rano) oraz ``start_skanu`` z dziennika - przypisany do trybu najblizszego przyjetego po nim skanu, o ile
    ten przyszedl najwyzej ``przerwa_min`` minut pozniej (start bez skanu nie liczy sie)."""
    punkty: dict[str, list[str]] = {TRYB_WIECZOR: [], TRYB_RANO: []}
    for w in baza.wiersze("SELECT tryb, czas_analizy FROM skany WHERE tryb IN (?, ?) AND czas_analizy >= ? AND czas_analizy < ?",
                          (TRYB_WIECZOR, TRYB_RANO, start, koniec)):
        punkty[w["tryb"]].append(w["czas_analizy"])
    for w in baza.wiersze(
            """SELECT d.czas, d.praca_id, d.skan_id, COALESCE(sp.tryb, ss.tryb) AS tryb FROM decyzje d
               LEFT JOIN prace p ON p.id = d.praca_id LEFT JOIN skany sp ON sp.id = p.skan_id LEFT JOIN skany ss ON ss.id = d.skan_id
               WHERE d.czas >= ? AND d.czas < ?""", (start, koniec)):
        tryb = TRYB_RANO if w["praca_id"] is None and w["skan_id"] is None else w["tryb"]
        if tryb in punkty:  # decyzje z importu okna testowego (skan bez trybu) - poza metrykami
            punkty[tryb].append(w["czas"])
    for w in baza.wiersze("SELECT otwarto, zamknieto FROM sesje_pieca"):
        punkty[TRYB_RANO] += [c for c in (w["otwarto"], w["zamknieto"]) if c and start <= c < koniec]
    skany = baza.wiersze("SELECT tryb, czas_analizy FROM skany WHERE tryb IN (?, ?) AND czas_analizy >= ? AND czas_analizy < ? "
                         "ORDER BY czas_analizy, id", (TRYB_WIECZOR, TRYB_RANO, start, koniec_startow))
    czasy = [s["czas_analizy"] for s in skany]
    for w in baza.wiersze("SELECT czas FROM zdarzenia WHERE typ = ? AND czas >= ? AND czas < ?", (TYP_START_SKANU, start, koniec)):
        i = bisect_left(czasy, w["czas"])
        if i < len(czasy) and _minut(w["czas"], czasy[i]) <= przerwa_min:
            punkty[skany[i]["tryb"]].append(w["czas"])
    return punkty


def _czas(punkty: list[str], sesja: SE.Sesja, przerwa_min: float) -> dict:
    """Czas przy stanowisku: posiedzenia, suma na zmiane (doba robocza + numer zmiany poczatku posiedzenia)."""
    sit = posiedzenia(punkty, przerwa_min)
    na_zmiane: dict[tuple[str, int], float] = {}
    for a, b in sit:
        klucz = (sesja.doba(a), sesja.zmiana(a))
        na_zmiane[klucz] = na_zmiane.get(klucz, 0.0) + _minut(a, b)
    suma = sum(na_zmiane.values())
    return {"posiedzen": len(sit), "zmian": len(na_zmiane), "suma_min": suma,
            "srednio_min": suma / len(na_zmiane) if na_zmiane else None, "max_min": max(na_zmiane.values()) if na_zmiane else None}


def _wieczor(baza: B.Baza, sesja: SE.Sesja, doby: list[str], start: str, koniec: str, punkty: list[str], przerwa_min: float) -> dict:
    aktywne = prace = czerwone = falszywe = ukruszone = bez_decyzji = niewykryte = nieznane = 0
    for doba in doby:
        for sk in sesja.stan_wieczoru(doba)["skany"]:
            if not sk["aktywny"]:  # zastapiony, niezgodny uklad, plytka nie z trybu, blad: decyzje o jego pracach sie nie licza
                continue
            aktywne += 1
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
                if p["sha16"] is None:  # bez przypisania: szara (bez projektu) albo bez kandydata
                    nieznane += 1
    powt = _powtorzone(baza, TRYB_WIECZOR, start, koniec)
    return {"skany": powt["skany"], "skany_aktywne": aktywne, "prace": prace, "czerwone": czerwone, "falszywe_alarmy": falszywe,
            "udzial_falszywych": _udzial(falszywe, prace), "czerwone_ukruszone": ukruszone, "czerwone_bez_decyzji": bez_decyzji,
            "niewykryte_cien": niewykryte, "wykrywalnosc_cien": _udzial(ukruszone, ukruszone + niewykryte), "nieznane": nieznane,
            "udzial_nieznanych": _udzial(nieznane, prace), "powtorzone": powt, "czas": _czas(punkty, sesja, przerwa_min)}


def _rano(baza: B.Baza, rano: SR.SesjaRano, od: str, do: str, start: str, koniec: str, punkty: list[str], przerwa_min: float) -> dict:
    piece = baza.wiersze("SELECT id, otwarto, zamknieto FROM sesje_pieca WHERE data >= ? AND data <= ? ORDER BY id", (od, do))
    zamkniete = [p for p in piece if p["zamknieto"]]
    klasy: dict[str, int] = {}
    prace = z_prawda = top1 = top2 = 0
    for piec in zamkniete:
        for sk in rano.stan_pieca(piec["id"])["skany"]:
            if not sk["aktywny"]:  # nieaktywny albo pominiety
                continue
            for p in sk["prace"]:
                if p["klasa"] is None:
                    continue
                prace += 1
                klasy[p["klasa"]] = klasy.get(p["klasa"], 0) + 1
                if p["klasa"] in KLASY_Z_PRAWDA and p["sha16"]:
                    z_prawda += 1
                    kandydaci = [k["sha16"] for k in p["kandydaci"]]
                    top1 += kandydaci[:1] == [p["sha16"]]
                    top2 += p["sha16"] in kandydaci[:2]
    czasy_piecow = [_minut(p["otwarto"], p["zamknieto"]) for p in zamkniete if p["otwarto"]]
    nieznane = klasy.get(SR.KLASA_NIEZNANA, 0)
    return {"piece": len(zamkniete), "piece_otwarte": len(piece) - len(zamkniete), "prace": prace, "klasy": klasy, "z_prawda": z_prawda,
            "top1": top1, "top2": top2, "udzial_top1": _udzial(top1, z_prawda), "udzial_top2": _udzial(top2, z_prawda),
            "nieznane": nieznane, "udzial_nieznanych": _udzial(nieznane, prace), "dwuznaczne": klasy.get(SR.KLASA_DWUZNACZNA, 0),
            "powtorzone": _powtorzone(baza, TRYB_RANO, start, koniec), "czas": _czas(punkty, rano.sesja, przerwa_min),
            "czas_pieca_min": {"mediana": statistics.median(czasy_piecow) if czasy_piecow else None,
                               "max": max(czasy_piecow) if czasy_piecow else None}}


def _stabilnosc(baza: B.Baza, sesja: SE.Sesja, start: str, koniec: str) -> dict:
    """Dni pracy (doby z wpisami dziennika) i awarie wymagajace restartu: ``program_start``, gdy od poprzedniego startu nie bylo
    ``program_stop`` (program zabity albo padl - awaria w chwili ostatniego wpisu dziennika przed ponownym startem), oraz
    ``silnik_nie_startuje``. Dziennik czytany w kolejnosci dopisywania (id), od poczatku - start w okresie moze domykac awarie."""
    wpisy = baza.wiersze("SELECT czas, typ FROM zdarzenia WHERE czas < ? ORDER BY id", (koniec,))
    awarie: list[tuple[str, str]] = []
    uruchomiony, poprzedni = False, None
    for w in wpisy:
        if w["typ"] == TYP_START:
            if uruchomiony and poprzedni is not None:
                awarie.append((poprzedni, AWARIA_RESTART))
            uruchomiony = True
        elif w["typ"] == TYP_STOP:
            uruchomiony = False
        elif w["typ"] == TYP_SILNIK:
            awarie.append((w["czas"], AWARIA_SILNIK))
        poprzedni = w["czas"]
    w_okresie = [(c, r) for c, r in awarie if start <= c < koniec]
    dni = sorted({sesja.doba(w["czas"]) for w in wpisy if w["czas"] >= start})
    z_awaria = sorted({sesja.doba(c) for c, _ in w_okresie})
    seria = najdluzsza = 0
    for d in dni:
        seria = 0 if d in z_awaria else seria + 1
        najdluzsza = max(najdluzsza, seria)
    return {"dni_pracy": len(dni), "dni_z_awaria": len(z_awaria), "awarie": len(w_okresie),
            AWARIA_RESTART: sum(1 for _, r in w_okresie if r == AWARIA_RESTART), AWARIA_SILNIK: sum(1 for _, r in w_okresie if r == AWARIA_SILNIK),
            "najdluzsza_seria": najdluzsza, "obecna_seria": seria, "doby_z_awaria": z_awaria}


def _wiersz(klucz: str, nazwa: str, wartosc: float | None, licznik: int | None = None, mianownik: int | None = None,
            jednostka: str = "%") -> dict:
    prog, kierunek = PROGI[klucz]
    return {"klucz": klucz, "nazwa": nazwa, "wartosc": wartosc, "licznik": licznik, "mianownik": mianownik, "prog": prog,
            "kierunek": kierunek, "jednostka": jednostka, "ocena": ocena(wartosc, prog, kierunek)}


def _wiersze(w: dict) -> list[dict]:
    """Wiersze tabeli metryk (kolejnosc strony); metryki trybu pominietego nie maja wiersza."""
    wi, ra, st = w["wieczor"], w["rano"], w["stabilnosc"]
    lista = []
    if wi is not None:
        lista.append(_wiersz("falszywe_alarmy", "falszywe alarmy (czerwone uznane za OK)", wi["udzial_falszywych"], wi["falszywe_alarmy"], wi["prace"]))
    if ra is not None:
        lista.append(_wiersz("top1", "top-1 wzgledem decyzji technika (rano)", ra["udzial_top1"], ra["top1"], ra["z_prawda"]))
        lista.append(_wiersz("top2", "top-2 wzgledem decyzji technika (rano)", ra["udzial_top2"], ra["top2"], ra["z_prawda"]))
    if wi is not None:
        lista.append(_wiersz("nieznane_wieczor", "prace nieznane - wieczor", wi["udzial_nieznanych"], wi["nieznane"], wi["prace"]))
    if ra is not None:
        lista.append(_wiersz("nieznane_rano", "prace nieznane - rano", ra["udzial_nieznanych"], ra["nieznane"], ra["prace"]))
    if wi is not None:
        lista.append(_wiersz("czas_wieczor", "czas przy stanowisku wieczorem (na zmiane)", wi["czas"]["srednio_min"], jednostka="min"))
        p = wi["powtorzone"]
        lista.append(_wiersz("powtorzone_wieczor", "skany powtorzone - wieczor", p["udzial"], p["powtorzone"], p["skany"]))
    if ra is not None:
        p = ra["powtorzone"]
        lista.append(_wiersz("powtorzone_rano", "skany powtorzone - rano", p["udzial"], p["powtorzone"], p["skany"]))
    lista.append(_wiersz("dni_bez_awarii", "dni bez awarii (najdluzsza seria)", st["najdluzsza_seria"] if st["dni_pracy"] else None,
                         jednostka="dni"))
    lista.append({"klucz": "m2", "nazwa": "M2 tabela testow wykrywalnosci", "wartosc": None, "licznik": None, "mianownik": None,
                  "prog": PROG_WYKRYWALNOSCI, "kierunek": "min", "jednostka": "%", "ocena": OCENA_SCHEMAT})
    return lista


def policz(baza: B.Baza, od: str, do: str, tryb: str = TRYB_OBA, *, granica_doby_godz: int = SE.GRANICA_DOBY_GODZ,
           zmiany_start_godz: tuple[int, ...] | list[int] = SE.ZMIANY_START_GODZ, prog_kandydata: float = SR.PROG_KANDYDATA,
           przerwa_min: float = PRZERWA_MIN, teraz: str | None = None) -> dict:
    """Wszystkie metryki okresu ``od`` .. ``do`` (doby robocze RRRR-MM-DD, wlacznie) dla trybu ``wieczor`` / ``rano`` / ``oba``.

    Zwraca zwykle dane (JSON): ``okres``, ``parametry``, ``wieczor`` / ``rano`` (None dla trybu pominietego), ``stabilnosc``,
    ``m2``, ``metryki`` (wiersze strony z ocena wzgledem ``PROGI``), ``ponizej_progu``, ``kod`` (0 albo 3). Baza tylko czytana.
    Zly okres albo tryb: ``ValueError``.
    """
    if tryb not in TRYBY:
        raise ValueError(f"tryb raportu: {', '.join(TRYBY)} (jest {tryb!r})")
    d_od, d_do = sprawdz_okres(od, do)
    sesja = SE.Sesja(baza, granica_doby_godz=granica_doby_godz, zmiany_start_godz=zmiany_start_godz)  # tylko odczyt (bez operatora)
    rano = SR.SesjaRano(sesja, prog_kandydata=prog_kandydata)
    doby = [(d_od + dt.timedelta(days=i)).isoformat() for i in range((d_do - d_od).days + 1)]
    granica = dt.time(granica_doby_godz)
    start = dt.datetime.combine(d_od, granica)
    koniec = dt.datetime.combine(d_do + dt.timedelta(days=1), granica)
    s_start, s_koniec = start.isoformat(), koniec.isoformat()
    punkty = _punkty_aktywnosci(baza, s_start, s_koniec, przerwa_min, (koniec + dt.timedelta(minutes=przerwa_min)).isoformat())
    w: dict[str, Any] = {
        "wersja": WERSJA, "wygenerowano": teraz or dt.datetime.now().replace(microsecond=0).isoformat(), "schemat_bazy": baza.wersja(),
        "okres": {"od": d_od.isoformat(), "do": d_do.isoformat(), "tryb": tryb, "doby": len(doby)},
        "parametry": {"granica_doby_godz": granica_doby_godz, "zmiany_start_godz": list(zmiany_start_godz), "prog_kandydata": prog_kandydata,
                      "przerwa_min": przerwa_min},
        "wieczor": _wieczor(baza, sesja, doby, s_start, s_koniec, punkty[TRYB_WIECZOR], przerwa_min) if tryb != TRYB_RANO else None,
        "rano": _rano(baza, rano, d_od.isoformat(), d_do.isoformat(), s_start, s_koniec, punkty[TRYB_RANO], przerwa_min) if tryb != TRYB_WIECZOR else None,
        "stabilnosc": _stabilnosc(baza, sesja, s_start, s_koniec),
        "m2": {"dostepne": False, "powod": POWOD_M2},
    }
    w["metryki"] = _wiersze(w)
    w["ponizej_progu"] = [m["klucz"] for m in w["metryki"] if m["ocena"] == OCENA_PONIZEJ]
    w["kod"] = KOD_PONIZEJ if w["ponizej_progu"] else KOD_OK
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
        cz = wi["czas"]
        linie += [
            f"WIECZOR: skany {wi['skany']} (aktywne {wi['skany_aktywne']}), prace w skanach aktywnych {wi['prace']}",
            f"  czerwone {wi['czerwone']}: OK (falszywy alarm) {wi['falszywe_alarmy']}, Ukruszona {wi['czerwone_ukruszone']}, "
            f"bez decyzji {wi['czerwone_bez_decyzji']}",
            f"  tryb cienia: ukruszone, ktorych program nie wskazal {wi['niewykryte_cien']}; wykrywalnosc wzgledem technika "
            f"{_proc(wi['wykrywalnosc_cien'])} ({wi['czerwone_ukruszone']}/{wi['czerwone_ukruszone'] + wi['niewykryte_cien']}) - nie zastepuje M2",
            f"  nieznane (szare, bez kandydata): {wi['nieznane']}",
            f"  skany powtorzone {wi['powtorzone']['powtorzone']} z {wi['powtorzone']['skany']}: {_statusy(wi['powtorzone'])}",
            f"  czas przy stanowisku: zmian {cz['zmian']}, posiedzen {cz['posiedzen']}, razem {_min(cz['suma_min'])} min, "
            f"srednio {_min(cz['srednio_min'])}, najwiecej {_min(cz['max_min'])} min na zmiane"]
    ra = w["rano"]
    if ra is None:
        linie.append(f"RANO: pominiety (tryb {ok['tryb']})")
    else:
        cz, cp = ra["czas"], ra["czas_pieca_min"]
        klasy = ", ".join(f"{k} {ra['klasy'].get(k, 0)}" for k in (SR.KLASA_PEWNA, SR.KLASA_PRZYPISANA, SR.KLASA_POPRAWKA, SR.KLASA_DWUZNACZNA,
                                                                   SR.KLASA_NIEZNANA, SR.KLASA_KONFLIKT, SR.KLASA_DO_POWTORZENIA) if ra["klasy"].get(k))
        linie += [
            f"RANO: piece zamkniete {ra['piece']} (niezamkniete {ra['piece_otwarte']} - poza metrykami klas), prace {ra['prace']}",
            f"  klasy: {klasy or '-'}",
            f"  top-1 {ra['top1']} z {ra['z_prawda']}, top-2 {ra['top2']} z {ra['z_prawda']} (prace z projektem po decyzjach technika: "
            f"pewna, przypisana, poprawka); dwuznaczne nierozstrzygniete {ra['dwuznaczne']}",
            f"  skany powtorzone {ra['powtorzone']['powtorzone']} z {ra['powtorzone']['skany']}: {_statusy(ra['powtorzone'])}",
            f"  czas przy stanowisku (informacyjnie): zmian {cz['zmian']}, posiedzen {cz['posiedzen']}, razem {_min(cz['suma_min'])} min, "
            f"srednio {_min(cz['srednio_min'])}, najwiecej {_min(cz['max_min'])} min",
            f"  piec od otwarcia do zamkniecia (nie stoper z PW): mediana {_min(cp['mediana'])} min, najwiecej {_min(cp['max'])} min"]
    st = w["stabilnosc"]
    doby = st["doby_z_awaria"]
    lista = ", ".join(doby[:MAX_DOB_NA_STRONIE]) + (f" (+{len(doby) - MAX_DOB_NA_STRONIE})" if len(doby) > MAX_DOB_NA_STRONIE else "")
    linie += [
        f"STABILNOSC: dni pracy {st['dni_pracy']}, z awaria {st['dni_z_awaria']}, awarii {st['awarie']} (restart bez zamkniecia "
        f"programu {st[AWARIA_RESTART]}, silnik nie startuje {st[AWARIA_SILNIK]})",
        f"  najdluzsza seria bez awarii {st['najdluzsza_seria']} dni, obecna {st['obecna_seria']} dni; doby z awaria: {lista or '-'}",
        "M2: tabela testow wykrywalnosci (5 prac tygodniowo ze znanymi ubytkami) - wymaga zmiany schematu:",
        "  tabela testy_wykrywalnosci (migracja bazy do wersji 2, decyzja wlasciciela); do tego czasu brak danych",
        f"UWAGI: posiedzenie = start skanu, przyjecie skanu, decyzja bez przerwy dluzszej niz {w['parametry']['przerwa_min']:g} min; "
        "zmiana z poczatku posiedzenia;",
        "  blizniacze prace implantologiczne (PW: poza trafnoscia) nie sa wykluczone - baza ich nie rozroznia",
        "WYNIK: wszystkie metryki z danymi w progu odbioru (kod 0)" if w["kod"] == KOD_OK else f"WYNIK: PONIZEJ PROGU (kod {w['kod']}):"]
    if w["kod"] != KOD_OK:
        linie.append("  " + ", ".join(w["ponizej_progu"]))
    return linie
