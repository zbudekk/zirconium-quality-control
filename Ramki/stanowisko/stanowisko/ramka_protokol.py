"""ramka_protokol - budowa i walidacja komunikatow laptop <-> ramka (protokol v1, strona laptopa; E3-A8 czesc "indicate").

Kontrakt: `ramka/README.md`, rozdzialy "Protokol v1" i "Wymagania dla strony laptopa" (ramka = serwer HTTP + JSON, laptop
odpytuje - DW8; laptop wysyla gotowe bloki pikseli dla plytki o danym numerze, kalibracja w osobnym pliku lokalnym - DW9).

- Plan przed wyslaniem jest sprawdzany TYM SAMYM kodem, ktorym sprawdza go ramka (`ramka.protokol.sprawdz_plan`): plan,
  ktory ramka odrzucilaby 400 (i przy tym zgasila obraz), nie wychodzi z laptopa.
- Dane osobowe (I7): z planu sesji do ramki przechodza tylko pola protokolu - numery plytek, gniazd i kuwet (kuweta tylko
  `#?[0-9]{1,6}`), kolory i bloki pikseli z kalibracji. Pola pomocnicze, nieznane klucze, nazwy w miejscu numeru kuwety -
  odrzucane (gniazdo z odrzucona kuweta swieci "sprawdz", jak w `session_rano`).
- Kolory ramki wieczornej biora sie z jednej tabeli statusow (`statusy.py`, kolumna `ramka`) - `kolor_ramki`.
- Odpowiedzi ramki sa sprawdzane (`sprawdz_stan`, `sprawdz_zdarzenia`, ...): odpowiedz niezgodna z protokolem =
  `BladOdpowiedzi` (klient traktuje ja jak blad sieci - nic z niej nie bierze).
Tylko biblioteka standardowa i pakiet `ramka` (walidacja, kalibracja).
"""
from __future__ import annotations

import copy
import hashlib
import json

from ramka import kalibracja as KAL
from ramka import protokol as RPR

from . import statusy

PROTOKOL = RPR.PROTOKOL
WAZNY_S_ROLI = dict(RPR.MAX_WAZNY_S_ROLI)       # W 30 s, P 600 s (wiecej ramka i tak przytnie)
TRYB_ROLI = dict(RPR.TRYB_ROLI)                 # W -> "wieczor", P -> "rano"
RODZINY = {r: tuple(v) for r, v in RPR.RODZINY.items()}  # W: plytki 1-3, P: 4-6
KOLORY = tuple(RPR.KOLORY_GNIAZD)
STANY_TRYBU = tuple(RPR.STANY_TRYBU)            # PUT /tryb (bez "wynik": ten stan ustawia tylko przyjety plan)
KOLOR_SPRAWDZ = "czerwony"                      # gniazdo, ktorego kuwety albo koloru nie da sie wyslac: "sprawdz"
WZOR_KUWETY = RPR.WZOR_KUWETY
WZOR_ID = RPR.WZOR_ID
WZOR_START = RPR.WZOR_START
WZOR_KLUCZA = RPR.WZOR_KLUCZA
POLA_TRANSPORTU = ("wersja", "start_id", "zdarzenia_do")  # bez nich odcisk tresci planu
POLA_PLANU_PLYTEK = ("plan_id", "plytki", "kuwety", "braki", "uklady")  # z `SesjaRano.plan_plytek` - reszta pomijana
ZDARZENIA_KUWET = ("potwierdzenie", "cofniecie", "kuweta_wybrana")
MAX_ODPOWIEDZI = 4 * 1024 * 1024


class BladProtokolu(ValueError):
    """Komunikatu nie da sie zbudowac zgodnie z protokolem (kod staly, opis bez danych z wejscia)."""

    def __init__(self, kod: str, opis: str = ""):
        super().__init__(f"{kod}: {opis}" if opis else kod)
        self.kod = kod
        self.opis = opis


class BladOdpowiedzi(ValueError):
    """Odpowiedz ramki niezgodna z protokolem v1."""


def _int(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def kolor_ramki(status_klucz) -> str | None:
    """Kolor diod pod gniazdem dla statusu z `statusy.STATUSY` (None = nie swieci); status nieznany = jak w `statusy`."""
    return statusy.status(status_klucz).ramka


# ----------------------------------------------------------------------------- kalibracja (DW9)

def wczytaj_kalibracje(sciezka) -> dict:
    """Plik kalibracji diod (`dane/kalibracja_ramek.json`); `ramka.kalibracja.BladKalibracji` przy zlym pliku."""
    return KAL.wczytaj(sciezka)


def kalibracja_domyslna(katalog_modeli) -> dict:
    """Wartosci startowe z geometrii `modele_plytek/*/uklad.json` (pliki ukladow tylko czytane): uklady kwadratowe
    i - E3-O2 - okragle ramkowe (`okragla_ramkowa_*`: te same gniazda i srodek co kwadrat, wiec te same bloki)."""
    return KAL.domyslna(katalog_modeli)


def uzupelnij_kalibracje(sciezka, katalog_modeli) -> tuple:
    """E3-O2: plik kalibracji uzupelniony o uklady, ktorych w nim nie ma (plik sprzed E3-O2 nie ma ukladow okraglych
    ramkowych) - `ramka.kalibracja.uzupelnij_plik`: (dane, [(rola, uklad), ...]); wpisow istniejacych nie zmienia.
    `OSError` = pliku nie da sie zapisac."""
    return KAL.uzupelnij_plik(sciezka, katalog_modeli)


def uzupelnij_kalibracje_w_pamieci(kal: dict, katalog_modeli) -> list:
    """Jak `uzupelnij_kalibracje`, ale tylko w danych `kal` (plik tylko do odczytu); zwraca liste dopisanych."""
    return KAL.uzupelnij(kal, katalog_modeli)


def _blok(kal, rola: str, uklad, gid: int):
    try:
        return list(KAL.blok(kal, rola, uklad, gid))
    except (KeyError, TypeError, ValueError):
        return None


def _nowe_pominiete() -> dict:
    return {"zla_plytka": [], "brak_kalibracji": [], "kuweta_odrzucona": 0, "zly_kolor": 0, "zle_gniazdo": 0}


def _numer_plytki(klucz):
    if isinstance(klucz, str) and klucz.isascii() and klucz.isdigit() and len(klucz) <= 2:
        return int(klucz)
    if _int(klucz):
        return klucz
    return None


def _gniazda(kal, rola: str, uklad, gniazda_we, kuwety_znane, pominiete: dict):
    """Lista gniazd planu (z px) albo None, gdy plytki nie da sie pokazac (brak kalibracji ukladu albo gniazda).
    `kuwety_znane` None = plan wieczorny (bez kuwet)."""
    if kal is None or not isinstance(uklad, str) or not isinstance(gniazda_we, list):
        return None
    wynik, ids = [], set()
    for g in gniazda_we:
        if not isinstance(g, dict) or not _int(g.get("id")) or not 1 <= g["id"] <= RPR.MAX_ID_GNIAZDA or g["id"] in ids:
            pominiete["zle_gniazdo"] += 1
            continue
        kolor = g.get("kolor")
        if kolor is None:
            continue  # gniazdo bez koloru (puste, skan nieaktywny) - nie swieci
        px = _blok(kal, rola, uklad, g["id"])
        if px is None:
            return None
        if kolor not in KOLORY:
            kolor = KOLOR_SPRAWDZ
            pominiete["zly_kolor"] += 1
        wpis = {"id": g["id"], "px": px, "kolor": kolor}
        kuw = g.get("kuweta") if kuwety_znane is not None else None
        if kuw is not None:
            if isinstance(kuw, str) and WZOR_KUWETY.fullmatch(kuw) and kuw in kuwety_znane:
                wpis["kuweta"] = kuw
            else:
                wpis["kolor"] = KOLOR_SPRAWDZ
                pominiete["kuweta_odrzucona"] += 1
        wynik.append(wpis)
        ids.add(g["id"])
    return sorted(wynik, key=lambda x: x["id"])


def _plytki(plytki_we, uklady, kal, rola: str, kuwety_znane, pominiete: dict) -> dict:
    plytki = {}
    if not isinstance(plytki_we, dict):
        return plytki
    uklady = uklady if isinstance(uklady, dict) else {}
    for klucz in sorted(plytki_we, key=lambda x: (_numer_plytki(x) is None, _numer_plytki(x) or 0)):
        n = _numer_plytki(klucz)
        if n is None or n not in RODZINY[rola]:
            if n is not None:
                pominiete["zla_plytka"].append(n)
            continue
        wpis = plytki_we[klucz]
        gn = _gniazda(kal, rola, uklady.get(str(n)), wpis.get("gniazda") if isinstance(wpis, dict) else None,
                      kuwety_znane, pominiete)
        if gn is None:
            pominiete["brak_kalibracji"].append(n)
            continue
        plytki[str(n)] = {"gniazda": gn}
    pominiete["zla_plytka"].sort()
    pominiete["brak_kalibracji"].sort()
    return plytki


def sprawdz_plan(plan: dict, rola: str) -> dict:
    """Walidacja kodem ramki (`ramka.protokol.sprawdz_plan`); `BladProtokolu` z kodem bledu ramki."""
    try:
        RPR.sprawdz_plan(copy.deepcopy(plan), rola)
    except RPR.BladProtokolu as b:
        raise BladProtokolu(b.kod, b.opis) from None
    return plan


def _sprawdz_transport(plan_id, wersja, start_id, zdarzenia_do) -> None:
    if not (isinstance(plan_id, str) and WZOR_ID.fullmatch(plan_id)):
        raise BladProtokolu("zly_plan_id", "plan_id: [A-Za-z0-9._-]{1,40}, generuje go program")
    if not (_int(wersja) and wersja >= 0 and isinstance(start_id, str) and WZOR_START.fullmatch(start_id)
            and _int(zdarzenia_do) and zdarzenia_do >= 0):
        raise BladProtokolu("zle_pole", "wersja / start_id / zdarzenia_do")


def plan_rano(plan_plytek: dict, kal, *, wersja: int, start_id: str, zdarzenia_do: int, potwierdzone=(),
              wybrane=None, wazny_s=None):
    """`PUT /plan` ramki porannej z `SesjaRano.plan_plytek` (A6): px z kalibracji (uklad z `uklady`), pola protokolu,
    `potwierdzone` / `wybrane` ze stanu laptopa. Zwraca (plan, pominiete); plan przechodzi walidacje ramki "P".

    Pomijane (licznik / lista w `pominiete`): plytka spoza rodziny ramki P (`zla_plytka`), plytka bez kalibracji ukladu albo
    gniazda - cala (`brak_kalibracji`; np. plytka okragla testowa n9), kuweta niezgodna z protokolem albo spoza listy kuwet (gniazdo
    zostaje jako "sprawdz", `kuweta_odrzucona`), kolor spoza protokolu ("sprawdz", `zly_kolor`), potwierdzenia i wybory
    plytek spoza planu albo kuwet spoza listy (ramka odrzucilaby caly plan)."""
    if not isinstance(plan_plytek, dict):
        raise BladProtokolu("zly_plan", "oczekiwano slownika z SesjaRano.plan_plytek")
    _sprawdz_transport(plan_plytek.get("plan_id"), wersja, start_id, zdarzenia_do)
    pominiete = _nowe_pominiete()
    kuwety, znane = [], set()
    for k in plan_plytek.get("kuwety") or []:
        kuw = k.get("kuweta") if isinstance(k, dict) else None
        if not (isinstance(kuw, str) and WZOR_KUWETY.fullmatch(kuw)) or kuw in znane or len(kuwety) >= RPR.MAX_KUWET:
            continue
        pl = []
        for p in k.get("plytki") or []:
            if _int(p) and 1 <= p <= RPR.MAX_PLYTKA and p not in pl:
                pl.append(p)
        kuwety.append({"kuweta": kuw, "plytki": pl})
        znane.add(kuw)
    plytki = _plytki(plan_plytek.get("plytki"), plan_plytek.get("uklady"), kal, "P", znane, pominiete)
    potw, widziane = [], set()
    for para in potwierdzone or ():
        if not (isinstance(para, (list, tuple)) and len(para) == 2):
            continue
        p, kuw = _numer_plytki(para[0]), para[1]
        if p is not None and str(p) in plytki and kuw in znane and (p, kuw) not in widziane:
            potw.append([p, kuw])
            widziane.add((p, kuw))
    wyb = {}
    for klucz, kuw in (wybrane or {}).items():
        p = _numer_plytki(klucz)
        if p is not None and str(p) in plytki and kuw in znane and (p, kuw) not in widziane:
            wyb[str(p)] = kuw
    braki = []
    for b in plan_plytek.get("braki") or []:
        if isinstance(b, str) and WZOR_KUWETY.fullmatch(b) and b not in braki:
            braki.append(b)
    plan = {"protokol": PROTOKOL, "plan_id": plan_plytek["plan_id"], "wersja": wersja, "start_id": start_id,
            "zdarzenia_do": zdarzenia_do, "wazny_s": float(wazny_s or WAZNY_S_ROLI["P"]), "tryb": TRYB_ROLI["P"],
            "plytki": plytki, "kuwety": kuwety, "potwierdzone": potw, "wybrane": wyb, "braki": braki[:RPR.MAX_BRAKOW]}
    return sprawdz_plan(plan, "P"), pominiete


def plan_wieczor(wyniki: dict, kal, *, plan_id: str, wersja: int, start_id: str, zdarzenia_do: int, wazny_s=None):
    """`PUT /plan` ramki wieczornej: `wyniki` = {numer plytki: (uklad, {gniazdo: kolor ramki albo None})}. Gniazda bez
    kuwet i bez pol porannych; None = gniazdo nie swieci. Zwraca (plan, pominiete); plan przechodzi walidacje ramki "W"."""
    _sprawdz_transport(plan_id, wersja, start_id, zdarzenia_do)
    pominiete = _nowe_pominiete()
    wejscie, uklady = {}, {}
    for n, (uklad, kolory) in wyniki.items():
        wejscie[str(n)] = {"gniazda": [{"id": int(g), "kolor": c} for g, c in sorted(kolory.items(), key=lambda x: int(x[0]))]}
        uklady[str(n)] = uklad
    plytki = _plytki(wejscie, uklady, kal, "W", None, pominiete)
    plan = {"protokol": PROTOKOL, "plan_id": plan_id, "wersja": wersja, "start_id": start_id, "zdarzenia_do": zdarzenia_do,
            "wazny_s": float(wazny_s or WAZNY_S_ROLI["W"]), "tryb": TRYB_ROLI["W"], "plytki": plytki}
    return sprawdz_plan(plan, "W"), pominiete


def odcisk_tresci(plan: dict) -> str:
    """Odcisk tresci planu bez pol transportowych (wersja, start_id, zdarzenia_do) - "ta sama tresc"."""
    tresc = {k: v for k, v in plan.items() if k not in POLA_TRANSPORTU}
    return hashlib.sha256(json.dumps(tresc, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def odcisk(obiekt) -> str:
    return hashlib.sha256(json.dumps(obiekt, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")).hexdigest()


def tresc_trybu(stan: str) -> dict:
    """Tresc `PUT /tryb`; stan "wynik" nie istnieje (ustawia go tylko przyjety plan)."""
    if stan not in STANY_TRYBU:
        raise BladProtokolu("zly_stan", "stan: " + ", ".join(STANY_TRYBU))
    return {"protokol": PROTOKOL, "stan": stan}


def koduj(d: dict) -> bytes:
    return json.dumps(d, ensure_ascii=True, separators=(",", ":")).encode("ascii")


# ----------------------------------------------------------------------------- odpowiedzi ramki

def _wymagaj(warunek, opis: str) -> None:
    if not warunek:
        raise BladOdpowiedzi(opis)


def _naglowek(d, co: str) -> None:
    _wymagaj(isinstance(d, dict) and d.get("protokol") == PROTOKOL and not isinstance(d.get("protokol"), bool),
             f"{co}: oczekiwano obiektu JSON protokolu {PROTOKOL}")
    _wymagaj(isinstance(d.get("start_id"), str) and WZOR_START.fullmatch(d["start_id"]), f"{co}: start_id")


def _kuweta(v) -> bool:
    return isinstance(v, str) and bool(WZOR_KUWETY.fullmatch(v))


def sprawdz_stan(d) -> dict:
    """Odpowiedz `GET /stan` (pola, z ktorych korzysta laptop)."""
    _naglowek(d, "stan")
    _wymagaj(d.get("rola") in ("W", "P"), "stan: rola")
    _wymagaj(_int(d.get("nr_zdarzenia")) and d["nr_zdarzenia"] >= 0, "stan: nr_zdarzenia")
    _wymagaj(d.get("plytka") is None or (_int(d["plytka"]) and 0 <= d["plytka"] <= RPR.MAX_PLYTKA), "stan: plytka")
    _wymagaj(d.get("tryb") is None or d["tryb"] in RPR.STANY, "stan: tryb")
    _wymagaj(d.get("plan_id") is None or (isinstance(d["plan_id"], str) and WZOR_ID.fullmatch(d["plan_id"])), "stan: plan_id")
    _wymagaj(d.get("plan_wersja") is None or (_int(d["plan_wersja"]) and d["plan_wersja"] >= 0), "stan: plan_wersja")
    potw = d.get("potwierdzone", [])
    _wymagaj(isinstance(potw, list) and all(isinstance(x, list) and len(x) == 2 and _int(x[0]) and _kuweta(x[1])
                                            for x in potw), "stan: potwierdzone")
    wyb = d.get("wybrane", {})
    _wymagaj(isinstance(wyb, dict) and all(_numer_plytki(k) is not None and _kuweta(v) for k, v in wyb.items()),
             "stan: wybrane")
    _wymagaj(isinstance(d.get("blad_sprzetu", False), bool), "stan: blad_sprzetu")
    return d


def _sprawdz_zdarzenie(z, poprzedni: int) -> int:
    _wymagaj(isinstance(z, dict) and _int(z.get("nr")) and z["nr"] > poprzedni, "zdarzenia: nr rosnace")
    _wymagaj(isinstance(z.get("typ"), str), "zdarzenia: typ")
    if z["typ"] == "plytka":
        _wymagaj(_int(z.get("plytka")) and _int(z.get("poprzednia")), "zdarzenia: plytka")
    elif z["typ"] in ZDARZENIA_KUWET:
        _wymagaj(_int(z.get("plytka")) and _kuweta(z.get("kuweta")) and isinstance(z.get("plan_id"), str),
                 "zdarzenia: kuweta")
    elif z["typ"] == "plan_przyjety":
        _wymagaj(isinstance(z.get("plan_id"), str) and _int(z.get("wersja")), "zdarzenia: plan_przyjety")
    return z["nr"]


def sprawdz_zdarzenia(d) -> dict:
    """Odpowiedz `GET /zdarzenia`: numery zdarzen rosnace, typy napisami, pola zdarzen kuwet i plytki poprawne."""
    _naglowek(d, "zdarzenia")
    _wymagaj(isinstance(d.get("restart"), bool), "zdarzenia: restart")
    _wymagaj(_int(d.get("nr_zdarzenia")) and d["nr_zdarzenia"] >= 0, "zdarzenia: nr_zdarzenia")
    _wymagaj(_int(d.get("utracone", 0)) and d.get("utracone", 0) >= 0, "zdarzenia: utracone")
    _wymagaj(d.get("utracone_do") is None or _int(d["utracone_do"]), "zdarzenia: utracone_do")
    _wymagaj(isinstance(d.get("zdarzenia"), list), "zdarzenia: lista")
    poprzedni = 0
    for z in d["zdarzenia"]:
        poprzedni = _sprawdz_zdarzenie(z, poprzedni)
    return d


def sprawdz_odpowiedz_polecenia(d) -> dict:
    """Odpowiedz 200 na `PUT /plan`, `PUT /tryb`, `DELETE /plan`: `start_id` i `nr_zdarzenia` (numer zdarzenia polecenia)."""
    _naglowek(d, "odpowiedz")
    _wymagaj(_int(d.get("nr_zdarzenia")) and d["nr_zdarzenia"] >= 0, "odpowiedz: nr_zdarzenia")
    return d


def blad_odpowiedzi(d) -> tuple:
    """(kod, zgaszono, wersja_ramki) z odpowiedzi bledu ramki; braki = (None, None, None)."""
    b = d.get("blad") if isinstance(d, dict) else None
    if not isinstance(b, dict):
        return None, None, None
    kod = b.get("kod") if isinstance(b.get("kod"), str) else None
    wr = b.get("wersja_ramki") if _int(b.get("wersja_ramki")) else None
    return kod, b.get("zgaszono") if isinstance(b.get("zgaszono"), bool) else None, wr
