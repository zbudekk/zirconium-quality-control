"""session.py - wieczor (E3-A1): przyjecie wyniku skanu, prace, decyzje, ponowny skan, lista "do dofrezowania".

Kryteria odbioru E3-A1 (plan etapu 3, sekcja 4.1) - kazde ma test `test_kN_...`:
 1 trzy wyniki -> 3 skany, prace i statusy 1:1 z plikami wynikow      6 ten sam sha16 w dwoch gniazdach = konflikt
 2 "Ukruszona" x2 + "OK" + cofniecie -> lista i 4 wiersze decyzji     8 nazwy zlecen nie wychodza poza cztery tabele
 3 ponowny skan plytki: poprzedni `zastapiony`, decyzje nie licza sie  9 import decyzje.csv: wiersze 1:1
 4 niezgodny uklad / skan ponownie: status skanu i 0 zielonych        (7 -> test_baza.py, 10 -> test_ustawienia.py)
 5 zamkniecie i otwarcie bazy: identyczny stan

Runda 2 (recenzja PR #16, decyzje wlasciciela z 17.11.2026): testy `test_pN_...` = uwagi P2-P7 recenzenta (P1 w test_baza.py),
`test_dN_...` = uwagi drobne, `test_decyzja2_...` = lista operatorow wymagana; decyzja 3 (kolor po decyzji) = `test_p7_...`,
decyzja 4 (nazwy w czterech tabelach) = `test_k8_...`; `test_p5_...` = doba robocza 06:00-06:00, zmiany, okno ponownego skanu
60 min, lista biezaca (korekty wlasciciela do P5); `test_blokada_...` = plytka nie z tego trybu (wymaganie wlasciciela z 17.11).
Runda 3 (recenzja przyrostowa PR #16): `test_p1r3_...` = jedna pozycja listy na punkt, `test_p2r3_...` = plik wyniku nigdy
nie jest kasowany, `test_dNr3_...` = uwagi drobne D1, D2, D4, D5, D6, D7, D10.

Dane: `testy/dane_sesji` - wyniki w formacie `porownaj.porownaj` zbudowane recznie (male, w pelni sztuczne: projekty to skroty
`sha16` wymyslonych nazw, zlecenia maja fikcyjne nazwy folderow). Zgodnosc formatu z prawdziwym silnikiem pilnuje
`test_wynik_prawdziwego_porownaj_wchodzi_do_bazy` (skan sztucznej plytki z trzema atrapami koron).
"""
from __future__ import annotations

import datetime as dt
import json
import random
import re
import shutil
import sqlite3
from pathlib import Path

import pytest

from stanowisko import baza as B
from stanowisko import session as SE

import import_decyzji as IMP  # narzedzia/ (sciezke dodaje conftest)

DANE = Path(__file__).resolve().parent / "dane_sesji"
STANOWISKO = Path(__file__).resolve().parent.parent
DATA = "2026-11-17"
ZDARZENIA = json.loads((DANE / "zdarzenia.json").read_text(encoding="ascii"))
INDEKS = json.loads((DANE / "indeks.json").read_text(encoding="ascii"))
SHA = {(p["folder"].split()[0], p["zeby"]): p["sha16"] for p in INDEKS["projekty"]}  # (kuweta, zeby) -> sha16 projektu
PLIK_DECYZJI = DANE / "decyzje_okna_testowego.csv.txt"
OSOBY = ["Technik A", "Technik B"]
# zmyslona sciezka folderu zlecenia (P2, P3): nazwisko nie moze trafic poza cztery tabele z nazwami
SCIEZKA_ZLECENIA = "C:\\Users\\lab\\OneDrive\\Cyrkon\\9911 Zmyslony Nazwiskowski"
SCIEZKA_PRYWATNA = "D:/Prywatne/#77 Inna Nazwiskowska"


def wynik(nazwa: str) -> dict:
    return json.loads((DANE / f"{nazwa}.json").read_text(encoding="ascii"))


def zapisany(w: dict) -> dict:
    """Tresc pliku wyniku, jaka ma zapisac `session`: caly wynik bez `foldery_projektow` (zostaje sama liczba folderow)."""
    z = {k: v for k, v in w.items() if k != "foldery_projektow"}
    if "foldery_projektow" in w:
        z["foldery_projektow_liczba"] = len(w["foldery_projektow"])
    return z


def wypelnij_indeks(b: B.Baza) -> None:
    """Zlecenia, projekty i frezowania z `indeks.json` (to, co w aplikacji wpisza indeks folderow i raporty - paczka A4)."""
    zlecenia, projekty = {}, {}
    with b.transakcja():
        for z in INDEKS["zlecenia"]:
            zlecenia[z["folder"]] = b.wstaw("zlecenia", **z)
        for p in INDEKS["projekty"]:
            p = dict(p)
            projekty[p["sha16"]] = b.wstaw("projekty", zlecenie_id=zlecenia[p.pop("folder")], **p)
        for f in INDEKS["frezowania"]:
            f = dict(f)
            b.wstaw("frezowania", projekt_id=projekty[f.pop("sha16")], **f)


class Zegar:
    """Kolejne wywolania daja kolejne sekundy wieczoru 17.11.2026 (czasy w bazie sa wtedy powtarzalne)."""

    def __init__(self, start: str = f"{DATA}T19:00:00"):
        self.t = dt.datetime.fromisoformat(start)

    def ustaw(self, czas: str) -> None:
        self.t = dt.datetime.fromisoformat(czas)

    def __call__(self) -> dt.datetime:
        self.t += dt.timedelta(seconds=1)
        return self.t


def nowa_sesja(katalog: Path, operator: str | None = "Technik A", **kw) -> SE.Sesja:
    b = B.otworz(katalog / "dane" / "stanowisko.sqlite")
    kw.setdefault("operatorzy", OSOBY)
    kw.setdefault("katalog_wynikow", katalog / "dane" / "wyniki")
    kw.setdefault("zegar", Zegar())
    s = SE.Sesja(b, **kw)
    if operator:
        s.wybierz_operatora(operator)
    return s


@pytest.fixture
def zegar():
    return Zegar()


@pytest.fixture
def sesja(tmp_path, zegar):
    s = nowa_sesja(tmp_path, zegar=zegar)
    wypelnij_indeks(s.baza)
    yield s
    s.baza.zamknij()


def przyjmij(s: SE.Sesja, nazwa: str, **zmiany) -> int:
    return s.przyjmij_wynik({**ZDARZENIA[nazwa], **zmiany}, wynik(nazwa))


def praca(s: SE.Sesja, skan_id: int, gniazdo: int, nr: int = 1) -> int:
    return s.baza.wiersz("SELECT id FROM prace WHERE skan_id = ? AND gniazdo = ? AND nr_fragmentu = ?", (skan_id, gniazdo, nr))["id"]


def skan(s: SE.Sesja, skan_id: int) -> dict:
    return s.baza.wiersz("SELECT * FROM skany WHERE id = ?", (skan_id,))


def stan_punktu(s: SE.Sesja, sha16: str) -> dict | None:
    return s.baza.wiersz("SELECT sp.* FROM stan_punktow sp JOIN projekty p ON p.id = sp.projekt_id WHERE p.sha16 = ?", (sha16,))


def pozycje(lista: list[dict]) -> list[tuple]:
    return [(x["kuweta"], x["zeby"], x["krazek"]) for x in lista]


def liczba(s: SE.Sesja, tabela: str) -> int:
    return s.baza.wiersz(f"SELECT count(*) AS n FROM {tabela}")["n"]


def skany_po_id(s: SE.Sesja, data: str | None = DATA) -> dict[int, dict]:
    return {x["id"]: x for x in s.stan_wieczoru(data)["skany"]}


def potw(stan: dict) -> list[dict]:
    """Propozycje "to ponowny skan?" ze stanu: same pola podstawowe (pola o decyzjach do utraty sprawdza test_d10r3)."""
    return [{k: x[k] for k in ("skan_id", "poprzedni_id", "numer_plytki")} for x in stan["do_potwierdzenia"]]


def teksty_poza_tabelami_nazw(b: B.Baza) -> list[str]:
    zrzut = b.zrzut()
    return [str(v) for t in set(B.TABELE) - set(B.TABELE_Z_NAZWAMI) for w in zrzut[t] for v in w.values() if isinstance(v, str)]


def brak_slow_poza_tabelami_nazw(s: SE.Sesja, katalog: Path, slowa: list[str]) -> int:
    """Zadne ze slow (malymi literami) nie wystepuje: w tabelach poza czterema z nazwami, w plikach obok bazy, w stanie wieczoru.

    Zwraca liczbe sprawdzonych plikow."""
    for tekst in teksty_poza_tabelami_nazw(s.baza):
        assert not any(sl in tekst.lower() for sl in slowa), tekst
    pliki = [p for p in (katalog / "dane").rglob("*") if p.is_file() and p.suffix != ".sqlite"]
    for p in pliki:
        tresc = p.read_text(encoding="utf-8").lower()
        assert not any(sl in tresc for sl in slowa), p.name
    stan = json.dumps(s.stan_wieczoru(DATA)).lower()
    assert not any(sl in stan for sl in slowa)
    return len(pliki)


# --- kryterium 1 ------------------------------------------------------------------------------
def test_k1_trzy_wyniki_trzy_skany_prace_i_statusy_jak_w_plikach(sesja):
    nazwy = ("wynik_plytka1", "wynik_plytka2", "wynik_plytka3")
    ids = [przyjmij(sesja, n) for n in nazwy]
    assert len(set(ids)) == 3 and liczba(sesja, "skany") == 3
    assert liczba(sesja, "prace") == sum(len(wynik(n)["gniazda"]) for n in nazwy) == 12
    for n, sid in zip(nazwy, ids):
        w, zd, sk = wynik(n), ZDARZENIA[n], skan(sesja, sid)
        wiersze = sesja.baza.wiersze("SELECT * FROM prace WHERE skan_id = ? ORDER BY id", (sid,))
        assert len(wiersze) == len(w["gniazda"])
        for r, g in zip(wiersze, w["gniazda"]):  # kazda praca: statusy 1:1 z plikiem wyniku
            ins = g["inspekcja"]
            assert (r["gniazdo"], r["nr_fragmentu"], r["status_fragmentu"]) == (g["gniazdo"], 1, g["status_fragmentu"])
            assert (r["status_match"], r["status_gniazda"]) == (g["status"], g["status_gniazda"])
            assert r["status_inspekcji"] == (ins["status"] if ins else None)
            assert (r["kandydat1_sha16"], r["kandydat1_pokrycie"]) == (g["kandydaci"][0]["id"], g["kandydaci"][0]["pokrycie"])
            assert (r["kandydat2_sha16"], r["kandydat2_pokrycie"]) == (g["kandydaci"][1]["id"], g["kandydaci"][1]["pokrycie"])
            assert r["pewnosc"] == g["pewnosc"] and r["wspolczynnik"] == 1.225 and r["korekta_skali"] == g["skala"]["poprawka_proc"]
            assert r["ubytki"] == (len(ins["ubytki"]) if ins else None)
            assert r["ubytek_max_mm"] == (max((u["srednica_mm"] for u in ins["ubytki"]), default=None) if ins else None)
        for kolor, ile in w["statusy_gniazd"].items():  # liczniki kolorow jak w pliku
            assert sum(1 for r in wiersze if r["status_gniazda"] == kolor) == ile, (n, kolor)
        assert (sk["plik"], sk["sha16"], sk["rozmiar"], sk["czas_pliku"]) == (zd["plik"], zd["sha16"], zd["rozmiar"], zd["czas_pliku"])
        assert (sk["tryb"], sk["status"], sk["uklad"], sk["uklad_zrodlo"], sk["uklad_zgodny"]) == ("wieczor", "przyjety", w["plytka"], "auto", 1)
        assert (sk["numer_plytki"], sk["numer_zrodlo"], sk["czas_s"]) == (w["numer"], w["numer_zrodlo"], w["czas_s"]["razem"])
        assert sk["czas_analizy"].startswith(DATA) and sk["zastepuje_id"] is None and sk["sesja_pieca_id"] is None
        # plik wyniku: caly wynik poza sciezkami folderow projektow (P2)
        assert sk["wersja_programu"] and json.loads(sesja.sciezka_wyniku(sid).read_text(encoding="utf-8")) == zapisany(w)
    # przypisanie projektu i frezowania z indeksu: gniazdo 2 plytki 1 = zab 14 z kuwety 3263, jeden wpis frezowania
    r = sesja.baza.wiersz("SELECT p.projekt_id, f.krazek, f.data, z.kuweta, pr.zeby FROM prace p JOIN frezowania f ON f.id = p.frezowanie_id "
                          "JOIN projekty pr ON pr.id = p.projekt_id JOIN zlecenia z ON z.id = pr.zlecenie_id WHERE p.id = ?", (praca(sesja, ids[0], 2),))
    assert (r["kuweta"], r["zeby"], r["krazek"], r["data"]) == ("3263", "14", "K-1101", "2026-11-17")
    szara = sesja.baza.wiersz("SELECT * FROM prace WHERE id = ?", (praca(sesja, ids[0], 7),))
    assert szara["status_match"] == "szary" and szara["projekt_id"] is None and szara["frezowanie_id"] is None  # bez projektu: bez przypisania
    stan = sesja.stan_wieczoru(DATA)
    assert [s["id"] for s in stan["skany"]] == ids and stan["prac"] == 12
    assert stan["liczniki"] == {"zielony": 4, "czerwony": 4, "zolty": 2, "szary": 1, "pomaranczowy": 1} and stan["decyzje"] == {}
    assert liczba(sesja, "zdarzenia") == 3 and liczba(sesja, "decyzje") == 0


def test_d5_dwa_wpisy_frezowania_projektu_bez_wskazania_w_wyniku_krazek_pusty(sesja):
    """D5: zab frezowany na dwoch krazkach (K4), a wynik nie wskazuje wpisu - program nie zgaduje krazka (do A5)."""
    s2 = przyjmij(sesja, "wynik_plytka2")  # gniazdo 1 = zab 24 z kuwety 3301: w indeksie wpisy K-1101 (17.11) i K-1099 (16.11)
    p24 = sesja.baza.wiersz("SELECT * FROM prace WHERE id = ?", (praca(sesja, s2, 1),))
    assert p24["projekt_id"] is not None and p24["frezowanie_id"] is None
    assert liczba(sesja, "frezowania") == 16 and sesja.baza.wiersz("SELECT count(*) AS n FROM frezowania WHERE projekt_id = ?", (p24["projekt_id"],))["n"] == 2
    sesja.ukruszona(p24["id"])
    assert pozycje(sesja.do_dofrezowania(DATA)) == [("3301", "24", None)]
    # wynik wskazujacy wpis (kontrakt puli ze wspolczynnikiem per praca, A5) ma pierwszenstwo
    starszy = sesja.baza.wiersz("SELECT id FROM frezowania WHERE projekt_id = ? AND krazek = 'K-1099'", (p24["projekt_id"],))["id"]
    w = wynik("wynik_plytka2")
    w["gniazda"][0]["kandydaci"][0]["frezowanie_id"] = starszy
    w["numer"] = 5
    s = sesja.przyjmij_wynik({**ZDARZENIA["wynik_plytka2"], "sha16": "1111222233334444"}, w)
    assert sesja.baza.wiersz("SELECT frezowanie_id FROM prace WHERE id = ?", (praca(sesja, s, 1),))["frezowanie_id"] == starszy


# --- kryterium 2 ------------------------------------------------------------------------------
def test_k2_ukruszona_ok_cofniecie_lista_do_dofrezowania(sesja, tmp_path):
    s1, s2, _ = (przyjmij(sesja, n) for n in ("wynik_plytka1", "wynik_plytka2", "wynik_plytka3"))
    p14, p36, p16 = praca(sesja, s1, 2), praca(sesja, s1, 3), praca(sesja, s2, 4)
    assert sesja.do_dofrezowania(DATA) == []
    sesja.ukruszona(p14)
    sesja.ukruszona(p16)
    sesja.ok(p36)
    lista = sesja.do_dofrezowania(DATA)
    assert pozycje(lista) == [("3263", "14", "K-1101"), ("0412", "16", "K-1102")]  # 2 pozycje: kuweta, zab, krazek
    assert [(x["numer_plytki"], x["gniazdo"], x["praca_id"], x["sha16"]) for x in lista] == [(1, 2, p14, SHA["3263", "14"]), (2, 4, p16, SHA["0412", "16"])]
    assert all(x["decyzja"] == "ukruszona" and x["operator"] == "Technik A" and x["stan_punktu"] == "do_dofrezowania" for x in lista)
    assert stan_punktu(sesja, SHA["0412", "16"])["stan"] == "do_dofrezowania" and stan_punktu(sesja, SHA["0412", "16"])["praca_id"] == p16
    assert stan_punktu(sesja, SHA["3301", "36"]) is None  # "OK" = falszywy alarm, punkt bez zmian
    sesja.cofnij(p16)
    assert pozycje(sesja.do_dofrezowania(DATA)) == [("3263", "14", "K-1101")]  # po cofnieciu 1 pozycja
    decyzje = sesja.baza.wiersze("SELECT * FROM decyzje ORDER BY id")
    assert len(decyzje) == 4  # cofniecie to czwarty wiersz, nic nie znika
    assert [(d["praca_id"], d["rodzaj"]) for d in decyzje] == [(p14, "ukruszona"), (p16, "ukruszona"), (p36, "ok"), (p16, "cofniecie")]
    assert decyzje[3]["wartosc"] == str(decyzje[1]["id"])  # cofniecie wskazuje cofana decyzje (decyzja wlasciciela 1)
    assert all(d["operator"] == "Technik A" and d["czas"].startswith(DATA) for d in decyzje)
    assert stan_punktu(sesja, SHA["0412", "16"])["stan"] == "oczekuje" and stan_punktu(sesja, SHA["0412", "16"])["praca_id"] is None
    stan = sesja.stan_wieczoru(DATA)
    dec = {p["id"]: p["decyzja"] for s in stan["skany"] for p in s["prace"]}
    assert (dec[p14], dec[p36], dec[p16]) == ("ukruszona", "ok", None) and sum(1 for v in dec.values() if v) == 2
    assert stan["do_dofrezowania"] == sesja.do_dofrezowania(DATA) and stan["decyzje"] == {"ukruszona": 1, "ok": 1}
    # lista jako plik (zalozenie Z6): te same pozycje, bez nazw folderow i plikow zlecen
    plik = sesja.zapisz_do_dofrezowania(DATA, tmp_path / "dane" / "listy")
    tresc = plik.read_text(encoding="utf-8").splitlines()
    assert plik.name == f"do_dofrezowania_{DATA}.csv" and tresc[0] == "kuweta;zeby;krazek;plytka;gniazdo;projekt;doba;zmiana"
    assert tresc[1:] == [f"3263;14;K-1101;1;2;{SHA['3263', '14']};{DATA};2"]  # 19:00 = zmiana 2
    # ponowne "Ukruszona" po cofnieciu: praca wraca na liste (piaty wiersz decyzji)
    sesja.ukruszona(p16)
    assert pozycje(sesja.do_dofrezowania(DATA)) == [("3263", "14", "K-1101"), ("0412", "16", "K-1102")] and liczba(sesja, "decyzje") == 5
    assert sesja.do_dofrezowania("2026-11-18") == []  # widok innej doby: pusto
    assert sesja.do_dofrezowania() == sesja.do_dofrezowania(DATA) and all((x["doba"], x["zmiana"]) == (DATA, 2) for x in sesja.do_dofrezowania())


def test_k2_praca_bez_projektu_i_bez_krazka_tez_trafia_na_liste(sesja):
    s1, s3 = przyjmij(sesja, "wynik_plytka1"), przyjmij(sesja, "wynik_plytka3")
    sesja.ukruszona(praca(sesja, s1, 7))  # szare "bez projektu": technik widzi ukruszenie
    sesja.ukruszona(praca(sesja, s3, 10))  # most 26-27 z kuwety #1234: w indeksie nie ma wpisu frezowania
    lista = sesja.do_dofrezowania(DATA)
    assert pozycje(lista) == [(None, None, None), ("#1234", "26-27", None)]
    assert (lista[0]["sha16"], lista[0]["projekt_id"], lista[0]["stan_punktu"], lista[0]["gniazdo"]) == (None, None, None, 7)
    assert liczba(sesja, "stan_punktow") == 1


def test_kolejnosc_decyzji_cofniecie_wraca_do_poprzedniej(sesja):
    s1 = przyjmij(sesja, "wynik_plytka1")
    p = praca(sesja, s1, 2)

    def obowiazuje():
        return next(x["decyzja"] for x in sesja.stan_wieczoru(DATA)["skany"][0]["prace"] if x["id"] == p)

    with pytest.raises(SE.BladSesji, match="nie ma decyzji do cofniecia"):
        sesja.cofnij(p)
    sesja.ukruszona(p)
    sesja.ok(p)  # technik zmienil zdanie
    assert obowiazuje() == "ok" and sesja.do_dofrezowania(DATA) == []
    assert stan_punktu(sesja, SHA["3263", "14"])["stan"] == "oczekuje"
    sesja.cofnij(p)  # cofa "ok": znow obowiazuje "ukruszona"
    assert obowiazuje() == "ukruszona" and len(sesja.do_dofrezowania(DATA)) == 1
    sesja.cofnij(p)
    assert obowiazuje() is None and sesja.do_dofrezowania(DATA) == []
    with pytest.raises(SE.BladSesji, match="nie ma decyzji do cofniecia"):
        sesja.cofnij(p)
    assert liczba(sesja, "decyzje") == 4
    # tryb cienia (SE9): praca uznana przez technika za ukruszona, choc program jej nie zaznaczyl
    zielona = praca(sesja, s1, 1)
    sesja.decyzja(zielona, "ukruszona_niewykryta")
    lista = sesja.do_dofrezowania(DATA)
    assert [(x["praca_id"], x["decyzja"]) for x in lista] == [(zielona, "ukruszona_niewykryta")]


def test_decyzje_bledne_wywolania(sesja):
    s1 = przyjmij(sesja, "wynik_plytka1")
    with pytest.raises(SE.BladSesji, match="nie ma pracy 9999"):
        sesja.ukruszona(9999)
    with pytest.raises(SE.BladSesji, match="rodzaj decyzji 'moze'"):
        sesja.decyzja(praca(sesja, s1, 2), "moze")
    for rodzaj in ("wybor_kandydata", "przypisanie_reczne", "uklad"):  # rodzaje z sekcji 3.4 obslugiwane przez pozniejsze paczki
        with pytest.raises(SE.BladSesji, match="nie jest obslugiwany"):
            sesja.decyzja(praca(sesja, s1, 2), rodzaj, "x")
    assert liczba(sesja, "decyzje") == 0


def test_decyzja2_lista_operatorow_jest_wymagana(tmp_path):
    """Decyzja wlasciciela 2 (17.11): bez listy osob albo bez wskazanej osoby nie ma decyzji; komunikaty bez nazw osob (D8)."""
    s = nowa_sesja(tmp_path, operator=None)
    try:
        s1 = przyjmij(s, "wynik_plytka1")
        p = praca(s, s1, 2)
        assert s.operator is None and s.operatorzy == ("Technik A", "Technik B")
        with pytest.raises(SE.BladSesji, match="wybierz osobe") as e:
            s.ukruszona(p)
        assert "Technik" not in str(e.value)
        with pytest.raises(SE.BladSesji, match="nie ma na liscie") as e:
            s.wybierz_operatora("Ktos Inny")
        assert "Ktos" not in str(e.value) and "Technik" not in str(e.value)
        s.wybierz_operatora("Technik B")
        s.ukruszona(p)
        s.ok(p, operator="Technik A")  # operator podany wprost ma pierwszenstwo
        with pytest.raises(SE.BladSesji, match="nie ma na liscie"):
            s.ok(p, operator="Ktos Inny")
        assert [d["operator"] for d in s.baza.wiersze("SELECT operator FROM decyzje ORDER BY id")] == ["Technik B", "Technik A"]
        # pusta lista (stary plik ustawien bez [sesja] operatorzy): program dziala, skany sa przyjmowane, ale decyzji nie ma
        bez_listy = SE.Sesja(s.baza, katalog_wynikow=tmp_path / "dane" / "wyniki", zegar=Zegar())
        s2 = przyjmij(bez_listy, "wynik_plytka2")
        assert bez_listy.operatorzy == () and skan(s, s2)["status"] == "przyjety" and len(bez_listy.stan_wieczoru(DATA)["skany"]) == 2
        proby = [lambda: bez_listy.ukruszona(p), lambda: bez_listy.ok(p), lambda: bez_listy.cofnij(p),
                 lambda: bez_listy.ok(p, operator="Technik C"), lambda: bez_listy.wybierz_operatora("Technik C"),
                 lambda: bez_listy.podaj_numer_plytki(s2, 3), lambda: bez_listy.zastap_skan(s2, s1)]
        for proba in proby:
            with pytest.raises(SE.BladSesji, match=r"lista operatorow jest pusta.*\[sesja\] operatorzy"):
                proba()
        assert liczba(s, "decyzje") == 2 and skan(s, s2)["numer_plytki"] == 2 and skan(s, s1)["status"] == "przyjety"
    finally:
        s.baza.zamknij()


# --- P7 / decyzja wlasciciela 3: decyzja technika zmienia kolor ---------------------------------
def test_p7_decyzja_technika_zmienia_kolor_i_liczniki(sesja):
    s1 = przyjmij(sesja, "wynik_plytka1")  # gniazda: 1 zielone, 2 i 3 czerwone, 5 zolte, 7 szare
    g = {n: praca(sesja, s1, n) for n in (1, 2, 3, 5, 7)}

    def kolory():
        st = sesja.stan_wieczoru(DATA)
        return {p["gniazdo"]: p["kolor"] for p in st["skany"][0]["prace"]}, st

    k, st = kolory()
    assert k == {1: "zielony", 2: "czerwony", 3: "czerwony", 5: "zolty", 7: "szary"}
    sesja.decyzja(g[1], "ukruszona_niewykryta")  # zielona wg programu, technik widzi ukruszenie
    sesja.ok(g[2])  # czerwona wg programu, technik: falszywy alarm
    sesja.ukruszona(g[3])
    k, st = kolory()
    assert SE.KOLOR_ZATWIERDZONA_OK == "zatwierdzona_ok" and SE.KOLOR_UKRUSZONA == "czerwony"
    assert k == {1: "czerwony", 2: "zatwierdzona_ok", 3: "czerwony", 5: "zolty", 7: "szary"}
    assert st["liczniki"] == {"czerwony": 2, "zatwierdzona_ok": 1, "zolty": 1, "szary": 1} == st["skany"][0]["liczniki"]  # 0 zielonych
    assert st["decyzje"] == {"ukruszona_niewykryta": 1, "ok": 1, "ukruszona": 1} and st["prac"] == 5
    assert sorted(x["gniazdo"] for x in st["do_dofrezowania"]) == [1, 3]
    # ocena programu zostaje w bazie i w stanie bez zmian
    assert [r["status_gniazda"] for r in sesja.baza.wiersze("SELECT status_gniazda FROM prace WHERE skan_id = ? ORDER BY id", (s1,))] == [
        "zielony", "czerwony", "czerwony", "zolty", "szary"]
    assert [p["status_gniazda"] for p in st["skany"][0]["prace"]] == ["zielony", "czerwony", "czerwony", "zolty", "szary"]
    # cofniecie decyzji przywraca kolor z analizy; "OK" na zoltej i szarej tez daje stan "zatwierdzona OK"
    sesja.cofnij(g[1])
    sesja.cofnij(g[2])
    sesja.ok(g[5])
    sesja.ok(g[7])
    k, st = kolory()
    assert k == {1: "zielony", 2: "czerwony", 3: "czerwony", 5: "zatwierdzona_ok", 7: "zatwierdzona_ok"}
    assert st["liczniki"] == {"zielony": 1, "czerwony": 2, "zatwierdzona_ok": 2} and st["decyzje"] == {"ukruszona": 1, "ok": 2}


# --- kryterium 3 ------------------------------------------------------------------------------
def test_k3_ponowny_skan_plytki_zastepuje_poprzedni(sesja):
    s1, s2 = przyjmij(sesja, "wynik_plytka1"), przyjmij(sesja, "wynik_plytka2")
    stare14 = praca(sesja, s1, 2)
    sesja.ukruszona(stare14)
    sesja.ok(praca(sesja, s1, 3))
    sesja.ukruszona(praca(sesja, s2, 4))
    assert len(sesja.do_dofrezowania(DATA)) == 2 and potw(sesja.stan_wieczoru(DATA)) == []
    s1b = przyjmij(sesja, "wynik_plytka1_ponownie")  # ta sama plytka nr 1, ten sam wieczor
    stan = sesja.stan_wieczoru(DATA)
    assert potw(stan) == [{"skan_id": s1b, "poprzedni_id": s1, "numer_plytki": 1}]
    assert skan(sesja, s1)["status"] == "przyjety" and len(sesja.do_dofrezowania(DATA)) == 2  # zalozenie Z4: bez potwierdzenia nic sie nie zmienia
    assert sesja.zastap_skan(s1b) == s1
    assert skan(sesja, s1)["status"] == "zastapiony"
    assert (skan(sesja, s1b)["status"], skan(sesja, s1b)["zastepuje_id"]) == ("przyjety", s1)
    assert pozycje(sesja.do_dofrezowania(DATA)) == [("0412", "16", "K-1102")]  # decyzje zastapionego skanu nie licza sie do list
    assert stan_punktu(sesja, SHA["3263", "14"])["stan"] == "oczekuje"
    decyzje = sesja.baza.wiersze("SELECT * FROM decyzje ORDER BY id")
    assert len(decyzje) == 4 and (decyzje[3]["rodzaj"], decyzje[3]["skan_id"], decyzje[3]["wartosc"]) == ("powtorz_skan", s1b, str(s1))
    stan = sesja.stan_wieczoru(DATA)
    po_id = {s["id"]: s for s in stan["skany"]}
    assert potw(stan) == [] and [s["id"] for s in stan["skany"]] == [s1, s2, s1b]
    assert (po_id[s1]["aktywny"], po_id[s1b]["aktywny"], po_id[s2]["aktywny"]) == (False, True, True)
    assert all(p["decyzja"] is None for p in po_id[s1b]["prace"])  # decyzje nie przechodza na nowy skan
    assert all(p["kolor"] is None for p in po_id[s1]["prace"]) and po_id[s1]["liczniki"] == {}
    assert stan["prac"] == 9 and stan["liczniki"] == {"zielony": 4, "czerwony": 3, "zolty": 1, "pomaranczowy": 1}
    with pytest.raises(SE.BladSesji, match="zastapiony"):
        sesja.ukruszona(stare14)  # praca ze skanu zastapionego: bez nowych decyzji
    with pytest.raises(SE.BladSesji, match="nie ma skanu do zastapienia"):
        sesja.zastap_skan(s1b)
    nowe14 = praca(sesja, s1b, 2)
    sesja.ukruszona(nowe14)  # decyzja na nowym skanie liczy sie normalnie
    assert pozycje(sesja.do_dofrezowania(DATA)) == [("0412", "16", "K-1102"), ("3263", "14", "K-1101")]
    assert stan_punktu(sesja, SHA["3263", "14"])["praca_id"] == nowe14


def test_skan_bez_numeru_po_wskazaniu_numeru_jest_kandydatem_do_zastapienia(sesja, zegar):
    s1 = przyjmij(sesja, "wynik_plytka1")
    zegar.ustaw(f"{DATA}T19:30:00")
    w = wynik("wynik_plytka1_ponownie")
    w["numer"], w["numer_zrodlo"] = None, "nieznany"  # dolki poza polem, numer niepodany
    bez_numeru = sesja.przyjmij_wynik({**ZDARZENIA["wynik_plytka1_ponownie"], "sha16": "0123456789abcdef"}, w)
    assert skan(sesja, bez_numeru)["numer_plytki"] is None and potw(sesja.stan_wieczoru(DATA)) == []
    sesja.podaj_numer_plytki(bez_numeru, 1)
    sk = skan(sesja, bez_numeru)
    assert (sk["numer_plytki"], sk["numer_zrodlo"]) == (1, "podany")
    d = sesja.baza.wiersze("SELECT * FROM decyzje")
    assert len(d) == 1 and (d[0]["rodzaj"], d[0]["wartosc"], d[0]["skan_id"], d[0]["praca_id"], d[0]["operator"]) == ("numer_plytki", "1", bez_numeru, None, "Technik A")
    assert potw(sesja.stan_wieczoru(DATA)) == [{"skan_id": bez_numeru, "poprzedni_id": s1, "numer_plytki": 1}]
    with pytest.raises(SE.BladSesji, match="numer plytki"):
        sesja.podaj_numer_plytki(bez_numeru, 0)
    # nastepnego dnia ten sam numer plytki to nowy wsad: bez propozycji, a wskazanie wprost jest odrzucane (inna doba, poza oknem)
    zegar.ustaw("2026-11-18T19:05:00")
    jutro = przyjmij(sesja, "wynik_plytka1_ponownie")
    assert potw(sesja.stan_wieczoru("2026-11-18")) == []
    with pytest.raises(SE.BladSesji, match="nie ma skanu do zastapienia"):
        sesja.zastap_skan(jutro)
    with pytest.raises(SE.BladSesji, match="z tej samej doby"):
        sesja.zastap_skan(jutro, s1)


def test_ten_sam_plik_skanu_przeanalizowany_drugi_raz_jest_kandydatem_do_zastapienia(sesja):
    w = wynik("wynik_plytka3")
    w["numer"], w["numer_zrodlo"] = None, "nieznany"
    a = sesja.przyjmij_wynik(ZDARZENIA["wynik_plytka3"], w)
    b = sesja.przyjmij_wynik(ZDARZENIA["wynik_plytka3"], w)  # ta sama zawartosc pliku (sha16), numer nieznany
    assert potw(sesja.stan_wieczoru(DATA)) == [{"skan_id": b, "poprzedni_id": a, "numer_plytki": None}]
    assert sesja.sciezka_wyniku(a) != sesja.sciezka_wyniku(b) and sesja.sciezka_wyniku(a).exists()  # pliki wynikow sie nie nadpisuja


# --- P6: zastapienie skanu sprawdza plytke i daje sie cofnac --------------------------------------
def test_p6a_zastap_skan_odmawia_gdy_numer_albo_rodzina_ukladu_sie_nie_zgadza(sesja):
    s1, s2 = przyjmij(sesja, "wynik_plytka1"), przyjmij(sesja, "wynik_plytka2")  # wieczorna nr 1 i wieczorna nr 2
    sesja.ukruszona(praca(sesja, s1, 2))
    with pytest.raises(SE.BladSesji, match=r"numer plytki.*2.*1"):
        sesja.zastap_skan(s2, s1)  # skan plytki 2 nie moze "zastapic" skanu plytki 1
    assert skan(sesja, s1)["status"] == "przyjety" and len(sesja.do_dofrezowania(DATA)) == 1 and liczba(sesja, "decyzje") == 1
    # ten sam numer, ale inna rodzina ukladu (np. zly odczyt numeru): program nie proponuje i odmawia
    w = wynik("wynik_plytka1_ponownie")
    w["plytka"] = "wieczorna_r54"  # stary uklad gniazd: inny rozstaw stozkow, wiec inna plytka fizyczna
    inna = sesja.przyjmij_wynik(ZDARZENIA["wynik_plytka1_ponownie"], w)
    assert potw(sesja.stan_wieczoru(DATA)) == []
    with pytest.raises(SE.BladSesji, match=r"uklad plytki \(wieczorna_r54 i wieczorna\)"):
        sesja.zastap_skan(inna, s1)
    with pytest.raises(SE.BladSesji, match="nie ma skanu do zastapienia"):
        sesja.zastap_skan(inna)
    assert skan(sesja, s1)["status"] == "przyjety"
    # kwadrat i kolo tej samej rodziny (te same stozki i gniazda - rozpoznanie ksztaltu bywa niepewne): dozwolone
    w["plytka"] = "okragla_wieczorna"
    kolo = sesja.przyjmij_wynik({**ZDARZENIA["wynik_plytka1_ponownie"], "sha16": "aaaabbbbccccdddd"}, w)
    assert potw(sesja.stan_wieczoru(DATA)) == [{"skan_id": kolo, "poprzedni_id": s1, "numer_plytki": 1}]
    assert sesja.zastap_skan(kolo) == s1 and sesja.do_dofrezowania(DATA) == []
    assert SE.rodzina_ukladu("okragla_poranna_r54") == "poranna_r54" != SE.rodzina_ukladu("poranna")
    assert SE.rodzina_ukladu("okragla_wieczorna") == SE.rodzina_ukladu("wieczorna") == "wieczorna" and SE.rodzina_ukladu("nowy_uklad") == "nowy_uklad"


def test_p6b_cofniecie_zastapienia_przywraca_poprzedni_skan_i_jego_decyzje(sesja):
    s1 = przyjmij(sesja, "wynik_plytka1")
    stare14 = praca(sesja, s1, 2)
    sesja.ukruszona(stare14)
    sesja.ok(praca(sesja, s1, 3))
    s1b = przyjmij(sesja, "wynik_plytka1_ponownie")
    sesja.zastap_skan(s1b)  # pomylkowe potwierdzenie "to ponowny skan"
    assert sesja.do_dofrezowania(DATA) == [] and stan_punktu(sesja, SHA["3263", "14"])["stan"] == "oczekuje"
    with pytest.raises(SE.BladSesji, match="nie ma czego cofac"):
        sesja.cofnij_zastapienie(s1)
    d = sesja.cofnij_zastapienie(s1b)
    assert skan(sesja, s1)["status"] == "przyjety" and (skan(sesja, s1b)["status"], skan(sesja, s1b)["zastepuje_id"]) == ("przyjety", None)
    wiersz = sesja.baza.wiersz("SELECT * FROM decyzje WHERE id = ?", (d,))
    assert (wiersz["rodzaj"], wiersz["skan_id"], wiersz["wartosc"], wiersz["operator"]) == ("cofnij_zastapienie", s1b, str(s1), "Technik A")
    assert liczba(sesja, "decyzje") == 4  # ukruszona, ok, powtorz_skan, cofnij_zastapienie - nic nie znika
    assert [x["praca_id"] for x in sesja.do_dofrezowania(DATA)] == [stare14]  # decyzje poprzedniego skanu znow sie licza
    pk = stan_punktu(sesja, SHA["3263", "14"])
    assert (pk["stan"], pk["praca_id"]) == ("do_dofrezowania", stare14)
    stan = sesja.stan_wieczoru(DATA)
    stary = {p["gniazdo"]: p for p in stan["skany"][0]["prace"]}
    assert stan["skany"][0]["aktywny"] is True and (stary[2]["decyzja"], stary[2]["kolor"], stary[3]["kolor"]) == ("ukruszona", "czerwony", "zatwierdzona_ok")
    assert potw(stan) == [] and stan["prac"] == 10  # program nie proponuje drugi raz zastapienia, ktore cofnieto
    sesja.cofnij(stare14)  # na przywroconym skanie znow mozna decydowac
    assert sesja.do_dofrezowania(DATA) == []
    with pytest.raises(SE.BladSesji, match="nie ma czego cofac"):
        sesja.cofnij_zastapienie(s1b)
    assert sesja.zastap_skan(s1b, s1) == s1  # swiadome zastapienie wskazane wprost nadal dziala
    assert sesja.decyzja(None, "cofnij_zastapienie", skan_id=s1b) > d and skan(sesja, s1)["status"] == "przyjety"
    # skan "do powtorzenia" wraca po cofnieciu ze swoim statusem
    dr = przyjmij(sesja, "wynik_drgniecie")  # wieczorna nr 3
    k = przyjmij(sesja, "wynik_konflikt")  # wieczorna nr 3
    assert sesja.zastap_skan(k) == dr and skan(sesja, dr)["status"] == "zastapiony"
    sesja.cofnij_zastapienie(k)
    assert skan(sesja, dr)["status"] == "do_powtorzenia"


# --- kryterium 4 ------------------------------------------------------------------------------
def test_k4_niezgodny_uklad_i_skan_ponownie_bez_zielonych(sesja):
    nz = przyjmij(sesja, "wynik_niezgodny_uklad")
    sk = skan(sesja, nz)
    assert (sk["status"], sk["uklad_zgodny"], sk["uklad_zrodlo"], sk["numer_plytki"], sk["numer_zrodlo"]) == ("niezgodny_uklad", 0, "reczny", None, "nieznany")
    assert sesja.baza.wiersz("SELECT count(*) AS n FROM prace WHERE skan_id = ?", (nz,))["n"] == 0
    dr = przyjmij(sesja, "wynik_drgniecie")  # w pliku 2 gniazda zielone i 1 "skan ponownie"
    assert skan(sesja, dr)["status"] == "do_powtorzenia"
    assert [r["status_gniazda"] for r in sesja.baza.wiersze("SELECT status_gniazda FROM prace WHERE skan_id = ? ORDER BY id", (dr,))] == ["zielony", "zolty", "zielony"]
    pu = przyjmij(sesja, "wynik_popraw_ulozenie")  # dwie prace w gniezdzie 11 i jedna poza gniazdem
    assert skan(sesja, pu)["status"] == "do_powtorzenia"
    wiersze = sesja.baza.wiersze("SELECT gniazdo, nr_fragmentu, status_fragmentu FROM prace WHERE skan_id = ? ORDER BY id", (pu,))
    assert [(r["gniazdo"], r["nr_fragmentu"], r["status_fragmentu"]) for r in wiersze] == [
        (1, 1, "praca"), (11, 1, "podwojny"), (11, 2, "podwojny"), (None, 1, "poza_gniazdem")]
    stan = sesja.stan_wieczoru(DATA)
    po_id = {s["id"]: s for s in stan["skany"]}
    assert po_id[nz]["prace"] == [] and po_id[nz]["liczniki"] == {} and po_id[nz]["aktywny"] is False
    for sid in (dr, pu):  # 0 prac zielonych: skan do powtorzenia niczego nie potwierdza
        assert po_id[sid]["liczniki"].get("zielony", 0) == 0 and all(p["kolor"] != "zielony" for p in po_id[sid]["prace"])
        assert po_id[sid]["aktywny"] is True
    assert po_id[dr]["liczniki"] == {"zolty": 3} and po_id[pu]["liczniki"] == {"zolty": 3, "szary": 1}
    assert stan["liczniki"].get("zielony", 0) == 0 and stan["prac"] == 7
    # dla porownania: zwykly skan ma zielone
    ok = przyjmij(sesja, "wynik_plytka2")
    assert {s["id"]: s for s in sesja.stan_wieczoru(DATA)["skany"]}[ok]["liczniki"]["zielony"] == 1


def test_p4b_decyzje_tylko_na_pracy_skanu_przyjetego(sesja):
    """P4 (b): praca skanu `do_powtorzenia`, `niezgodny_uklad`, `blad` albo `zastapiony` nie przyjmuje decyzji."""
    dr = przyjmij(sesja, "wynik_drgniecie")
    w = wynik("wynik_plytka2")
    w["uklad_zgodny"] = False  # wynik z innego zrodla niz dzisiejszy porownaj: uklad niezgodny, a gniazda sa
    nz = sesja.przyjmij_wynik(ZDARZENIA["wynik_plytka2"], w)
    bl = sesja.przyjmij_blad(ZDARZENIA["wynik_plytka3"], "awaria analizy")
    projekt = sesja.baza.wiersz("SELECT id FROM projekty WHERE sha16 = ?", (SHA["#1234", "12"],))["id"]
    praca_bledu = sesja.baza.wstaw("prace", skan_id=bl, gniazdo=2, nr_fragmentu=1, status_gniazda="czerwony", projekt_id=projekt)
    s1 = przyjmij(sesja, "wynik_plytka1")
    sesja.ukruszona(praca(sesja, s1, 2))
    sesja.zastap_skan(przyjmij(sesja, "wynik_plytka1_ponownie"))
    assert (skan(sesja, dr)["status"], skan(sesja, nz)["status"], skan(sesja, bl)["status"], skan(sesja, s1)["status"]) == (
        "do_powtorzenia", "niezgodny_uklad", "blad", "zastapiony")
    przed = liczba(sesja, "decyzje")
    for praca_id, status in ((praca(sesja, dr, 1), "do_powtorzenia"), (praca(sesja, nz, 4), "niezgodny_uklad"), (praca_bledu, "blad"),
                             (praca(sesja, s1, 2), "zastapiony")):
        for akcja in (sesja.ukruszona, sesja.ok, sesja.cofnij, lambda p: sesja.decyzja(p, "ukruszona_niewykryta")):
            with pytest.raises(SE.BladSesji, match=f"status '{status}'.*tylko na skanie przyjetym"):
                akcja(praca_id)
    assert liczba(sesja, "decyzje") == przed == 2  # ukruszona + powtorz_skan
    assert sesja.do_dofrezowania(DATA) == []
    assert sesja.baza.wiersze("SELECT stan FROM stan_punktow WHERE stan = 'do_dofrezowania'") == []  # punkt bez pozycji na liscie nie powstaje


def test_awaria_analizy_zapisana_jako_skan_ze_statusem_blad(sesja):
    sid = sesja.przyjmij_blad(ZDARZENIA["wynik_plytka1"], "proces silnika zakonczyl sie w trakcie analizy")
    sk = skan(sesja, sid)
    assert (sk["status"], sk["tryb"], sk["sha16"], sk["wynik_json"]) == ("blad", "wieczor", ZDARZENIA["wynik_plytka1"]["sha16"], None)
    zd = sesja.baza.wiersze("SELECT * FROM zdarzenia")
    assert len(zd) == 1 and (zd[0]["typ"], zd[0]["skan_id"]) == ("blad_analizy", sid)
    assert json.loads(zd[0]["dane"]) == {"typ": None, "opis": "proces silnika zakonczyl sie w trakcie analizy"}
    stan = sesja.stan_wieczoru(DATA)
    assert stan["skany"][0]["status"] == "blad" and stan["skany"][0]["aktywny"] is False and stan["prac"] == 0
    dobry = przyjmij(sesja, "wynik_plytka1")  # ten sam plik przeanalizowany potem poprawnie: blad nie jest "poprzednim skanem"
    assert potw(sesja.stan_wieczoru(DATA)) == [] and skan(sesja, dobry)["status"] == "przyjety"


def test_p3_blad_analizy_w_dzienniku_typ_i_tresc_bez_sciezek(sesja, tmp_path):
    """P3: do `zdarzenia.dane` idzie typ wyjatku i tresc z wycietymi sciezkami - nazwa folderu zlecenia nie trafia do dziennika."""
    wyjatek = FileNotFoundError(2, "No such file or directory", SCIEZKA_ZLECENIA + "\\2026-11-16_nazwiskowski-11-crown_cad.stl")
    assert "Nazwiskowski" in str(wyjatek)
    a = sesja.przyjmij_blad(ZDARZENIA["wynik_plytka1"], wyjatek)
    b = sesja.przyjmij_blad(ZDARZENIA["wynik_plytka2"], f"brak projektow STL w {SCIEZKA_ZLECENIA}, {SCIEZKA_PRYWATNA}\nslad: silnik.py wiersz 40")
    c = sesja.przyjmij_blad(ZDARZENIA["wynik_plytka3"], ValueError("x" * 2000))
    dane = {z["skan_id"]: json.loads(z["dane"]) for z in sesja.baza.wiersze("SELECT skan_id, dane FROM zdarzenia WHERE typ = 'blad_analizy'")}
    assert dane[a] == {"typ": "FileNotFoundError", "opis": "[Errno 2] No such file or directory: '<sciezka>'"}
    assert dane[b] == {"typ": None, "opis": "brak projektow STL w <sciezka>\nslad: silnik.py wiersz 40"}
    assert dane[c]["typ"] == "ValueError" and len(dane[c]["opis"]) <= 500
    # dziennik ogolnie (wpisy scanner / silnik / okno z kolejnych paczek): sciezki sa wycinane w kazdym tekscie
    z = sesja.baza.zdarzenie("scanner", "proba", {"plik": SCIEZKA_PRYWATNA + "/a.stl", "lista": [f"x '{SCIEZKA_ZLECENIA}' y", 7], "liczba": 3})
    assert json.loads(sesja.baza.wiersz("SELECT dane FROM zdarzenia WHERE id = ?", (z,))["dane"]) == {
        "plik": "<sciezka>", "lista": ["x '<sciezka>' y", 7], "liczba": 3}
    assert brak_slow_poza_tabelami_nazw(sesja, tmp_path, ["nazwiskow", "zmyslony", "onedrive"]) == 0
    assert B.bez_sciezek("pokrycie 0.91 / pewnosc 0.75; A/B; 19:02:11; skala: -0.4 %") == "pokrycie 0.91 / pewnosc 0.75; A/B; 19:02:11; skala: -0.4 %"
    assert B.bez_sciezek("plik \\\\serwer\\Cyrkon\\9911 Zmyslony\\a.stl oraz /home/lab/Cyrkon/9911 x/a.stl") == "plik <sciezka>"


# --- kryterium 5 ------------------------------------------------------------------------------
def _scenariusz(s: SE.Sesja) -> None:
    s1, s2, _ = (przyjmij(s, n) for n in ("wynik_plytka1", "wynik_plytka2", "wynik_plytka3"))
    s.ukruszona(praca(s, s1, 2))
    s.ok(praca(s, s1, 3))
    s.ukruszona(praca(s, s2, 4))
    s.cofnij(praca(s, s2, 4))
    s1b = przyjmij(s, "wynik_plytka1_ponownie")
    s.zastap_skan(s1b)
    s.ukruszona(praca(s, s1b, 3))
    przyjmij(s, "wynik_drgniecie")
    przyjmij(s, "wynik_konflikt")
    przyjmij(s, "wynik_niezgodny_uklad")


def test_k5_po_zamknieciu_i_otwarciu_ten_sam_stan(tmp_path):
    s = nowa_sesja(tmp_path)
    wypelnij_indeks(s.baza)
    _scenariusz(s)
    zrzut, stan, lista, konflikty = s.baza.zrzut(), s.stan_wieczoru(DATA), s.do_dofrezowania(DATA), s.konflikty(DATA)
    assert len(zrzut["skany"]) == 7 and len(zrzut["decyzje"]) == 6 and len(lista) == 1 and len(konflikty) == 1
    tekst = json.dumps(stan, sort_keys=True)  # stan jest zwyklymi danymi (do okna, do ramki, do pliku)
    s.baza.zamknij()
    s2 = nowa_sesja(tmp_path)  # "restart programu": nowe polaczenie i nowy obiekt sesji, nic w pamieci
    try:
        assert s2.baza.kopia_przed_migracja is None
        assert s2.baza.zrzut() == zrzut  # identyczny zrzut wszystkich 11 tabel
        assert s2.stan_wieczoru(DATA) == stan and json.dumps(s2.stan_wieczoru(DATA), sort_keys=True) == tekst
        assert s2.do_dofrezowania(DATA) == lista and s2.konflikty(DATA) == konflikty
        assert s2.stan_wieczoru() == stan  # bez daty: biezacy wieczor wg zegara sesji
    finally:
        s2.baza.zamknij()


# --- P5: doba robocza 06:00 - 06:00 od chwili przyjecia, zmiany, okno ponownego skanu, lista biezaca -----
def _plytka(s: SE.Sesja, numer: int, sha16: str, nazwa: str = "wynik_plytka2", **zmiany) -> int:
    """Skan plytki o podanym numerze (te same prace co w pliku `nazwa`), z wlasnym skrotem pliku skanu."""
    w = wynik(nazwa)
    w["numer"] = numer
    return s.przyjmij_wynik({**ZDARZENIA[nazwa], "sha16": sha16, **zmiany}, w)


def test_p5_doba_robocza_od_chwili_przyjecia_i_numer_zmiany(sesja, zegar):
    # szesc skanow jednej doby D (17.11): 06:10, 13:50, 14:10, 23:59 oraz 00:05 i 05:55 dnia nastepnego -> zmiany 1, 1, 2, 3, 3, 3
    czasy = [f"{DATA}T06:10:00", f"{DATA}T13:50:00", f"{DATA}T14:10:00", f"{DATA}T23:59:00", "2026-11-18T00:05:00", "2026-11-18T05:55:00"]
    ids = []
    for i, czas in enumerate(czasy):
        zegar.ustaw(czas)
        ids.append(_plytka(sesja, i + 1, f"{i:016x}", czas_pliku="2026-11-10T08:00:00"))  # data pliku jest tylko informacja
    stan = sesja.stan_wieczoru()  # zegar: 05:55 dnia 18.11 - nadal doba 17.11, zmiana 3
    assert (stan["data"], stan["zmiana"]) == (DATA, 3) and sesja.doba() == DATA and sesja.zmiana() == 3
    assert [s["id"] for s in stan["skany"]] == ids and [s["zmiana"] for s in stan["skany"]] == [1, 1, 2, 3, 3, 3]
    assert all(s["czas_pliku"] == "2026-11-10T08:00:00" for s in stan["skany"]) and sesja.stan_wieczoru("2026-11-10")["skany"] == []
    assert [s["czas_analizy"][:16] for s in stan["skany"]] == [c[:16] for c in czasy] and potw(stan) == []
    # od 06:00 liczy sie nastepna doba (zmiana 1)
    zegar.ustaw("2026-11-18T06:00:00")
    stan = sesja.stan_wieczoru()
    assert (stan["data"], stan["zmiana"], stan["skany"]) == ("2026-11-18", 1, []) and sesja.doba() == "2026-11-18"
    assert len(sesja.stan_wieczoru(DATA)["skany"]) == 6 and sesja.stan_wieczoru(DATA)["zmiana"] is None  # doba miniona: bez biezacej zmiany
    # regula w jednym miejscu: doba() i zmiana(); granica i poczatki zmian sa ustawieniami
    assert sesja.doba(f"{DATA}T05:59:59") == "2026-11-16" and sesja.doba(dt.datetime(2026, 11, 17, 6, 0)) == DATA
    assert [sesja.zmiana(f"{DATA}T{g}:00") for g in ("05:59", "06:00", "13:59", "14:00", "21:59", "22:00", "23:59", "00:00")] == [3, 1, 1, 2, 2, 3, 3, 3]
    assert (sesja.granica_doby_godz, sesja.zmiany_start_godz, sesja.ponowny_skan_okno_min) == (6, (6, 14, 22), 60)
    inna = SE.Sesja(sesja.baza, operatorzy=OSOBY, granica_doby_godz=0, zmiany_start_godz=[0, 12], zegar=Zegar("2026-11-18T00:05:00"))
    assert inna.doba() == "2026-11-18" and inna.zmiana() == 1 and inna.zmiana("2026-11-18T12:00:00") == 2
    assert [s["id"] for s in inna.stan_wieczoru(DATA)["skany"]] == ids[:4]
    for zle in ({"granica_doby_godz": 24}, {"zmiany_start_godz": []}, {"zmiany_start_godz": [14, 6]}, {"ponowny_skan_okno_min": -1},
                {"ponowny_skan_okno_min": 0}, {"granica_doby_godz": 7}, {"zmiany_start_godz": [7, 15, 23]}):  # D8: zmiana 1 zaczyna dobe, okno > 0
        with pytest.raises(SE.BladSesji):
            SE.Sesja(sesja.baza, operatorzy=OSOBY, **zle)


def test_p5_ponowny_skan_w_oknie_60_minut_takze_przez_granice_doby(sesja, zegar):
    # skan 05:55 (doba D, zmiana 3) i powtorka 06:05 (doba D+1, zmiana 1): propozycja i dzialajace zastapienie
    zegar.ustaw("2026-11-18T05:55:00")
    s1 = przyjmij(sesja, "wynik_plytka1")
    sesja.ukruszona(praca(sesja, s1, 2))
    zegar.ustaw("2026-11-18T06:05:00")
    s1b = przyjmij(sesja, "wynik_plytka1_ponownie")
    assert sesja.doba(skan(sesja, s1)["czas_analizy"]) == DATA and sesja.doba(skan(sesja, s1b)["czas_analizy"]) == "2026-11-18"
    assert potw(sesja.stan_wieczoru()) == [{"skan_id": s1b, "poprzedni_id": s1, "numer_plytki": 1}]
    assert sesja.zastap_skan(s1b) == s1 and skan(sesja, s1)["status"] == "zastapiony" and sesja.do_dofrezowania() == []
    # granica okna (decyzja wlasciciela: "[cytat usuniety]"): 59 min -> propozycja, 60 min -> jeszcze propozycja, 61 min -> nowy wsad
    for numer, minut, propozycja in ((2, 59, True), (3, 60, True), (4, 61, False)):
        zegar.ustaw(f"2026-11-18T{7 + numer:02d}:00:00")
        pierwszy = _plytka(sesja, numer, f"a{numer:015x}")
        zegar.ustaw(f"2026-11-18T{7 + numer + minut // 60:02d}:{minut % 60:02d}:00")
        drugi = _plytka(sesja, numer, f"b{numer:015x}")
        oczekiwane = [{"skan_id": drugi, "poprzedni_id": pierwszy, "numer_plytki": numer}] if propozycja else []
        assert [x for x in potw(sesja.stan_wieczoru()) if x["numer_plytki"] == numer] == oczekiwane, (numer, minut)
    # ta sama plytka po 5 h w tej samej dobie = nowy wsad: bez propozycji, obie pozycje listy zachowane
    zegar.ustaw("2026-11-18T13:00:00")
    a = _plytka(sesja, 5, "c" * 16)
    sesja.ukruszona(praca(sesja, a, 4))
    zegar.ustaw("2026-11-18T18:00:00")
    b = _plytka(sesja, 5, "d" * 16)
    sesja.ukruszona(praca(sesja, b, 4))
    assert [x for x in potw(sesja.stan_wieczoru()) if x["numer_plytki"] == 5] == []
    with pytest.raises(SE.BladSesji, match="nie ma skanu do zastapienia.*60 min"):
        sesja.zastap_skan(b)
    # nowy wsad na tej samej plytce: prace obu skanow zostaja w stanie, a ten sam zab jest na liscie raz (P1 rundy 3)
    assert [(x["praca_id"], x["zmiana"]) for x in sesja.do_dofrezowania()] == [(praca(sesja, b, 4), 2)]
    assert [y["praca_id"] for y in sesja.do_dofrezowania()[0]["powtorzenia"]] == [praca(sesja, a, 4)]
    assert skan(sesja, a)["status"] == "przyjety" and skan(sesja, b)["status"] == "przyjety"
    # zastapienie wskazane wprost dziala w obrebie tej samej doby roboczej, takze poza oknem ...
    assert sesja.zastap_skan(b, a) == a and [x["praca_id"] for x in sesja.do_dofrezowania()] == [praca(sesja, b, 4)]
    assert sesja.do_dofrezowania()[0]["powtorzenia"] == []
    # ... a poza doba i poza oknem jest odrzucane
    zegar.ustaw("2026-11-19T07:30:00")
    c = _plytka(sesja, 5, "e" * 16)
    with pytest.raises(SE.BladSesji, match="z tej samej doby roboczej albo sprzed najwyzej 60 min"):
        sesja.zastap_skan(c, b)
    # okno jest ustawieniem
    krotkie = SE.Sesja(sesja.baza, operatorzy=OSOBY, ponowny_skan_okno_min=1, zegar=zegar)
    zegar.ustaw("2026-11-19T07:33:00")
    d = _plytka(krotkie, 5, "f" * 16)
    assert potw(krotkie.stan_wieczoru()) == [] and potw(sesja.stan_wieczoru()) == [{"skan_id": d, "poprzedni_id": c, "numer_plytki": 5}]


def test_p5_lista_biezaca_do_dofrezowania_nie_znika_na_granicy_doby(sesja, zegar, tmp_path):
    zegar.ustaw(f"{DATA}T23:00:00")
    s1 = przyjmij(sesja, "wynik_plytka1")
    p14, szara = praca(sesja, s1, 2), praca(sesja, s1, 7)
    sesja.ukruszona(p14)
    sesja.ukruszona(szara)  # praca bez projektu w indeksie
    zegar.ustaw("2026-11-18T06:30:00")  # nastepna doba, zmiana 1
    biezaca = sesja.do_dofrezowania()
    assert [(x["praca_id"], x["doba"], x["zmiana"]) for x in biezaca] == [(p14, DATA, 3), (szara, DATA, 3)]  # "Ukruszona" z doby D widoczna w D+1
    assert sesja.do_dofrezowania("2026-11-18") == [] and sesja.do_dofrezowania(DATA) == biezaca  # widok "ta doba" to filtr
    stan = sesja.stan_wieczoru()
    assert (stan["data"], stan["zmiana"], stan["skany"], stan["do_dofrezowania"]) == ("2026-11-18", 1, [], [])
    assert stan["do_dofrezowania_biezaca"] == biezaca
    s2 = przyjmij(sesja, "wynik_plytka2")
    p16 = praca(sesja, s2, 4)
    sesja.ukruszona(p16)
    assert [(x["praca_id"], x["doba"], x["zmiana"]) for x in sesja.do_dofrezowania()] == [(p14, DATA, 3), (szara, DATA, 3), (p16, "2026-11-18", 1)]
    assert [x["praca_id"] for x in sesja.stan_wieczoru()["do_dofrezowania"]] == [p16]
    plik = sesja.zapisz_do_dofrezowania(katalog=tmp_path / "dane" / "listy")
    wiersze = plik.read_text(encoding="utf-8").splitlines()
    assert plik.name == "do_dofrezowania_biezaca.csv" and len(wiersze) == 4 and wiersze[1].endswith(f";{DATA};3") and wiersze[3].endswith(";2026-11-18;1")
    # pozycja jest otwarta, dopoki punkt projektu ma stan do_dofrezowania; zamkniecie punktu (zrobi to poranek, A6) zdejmuje ja z listy
    sesja.baza.wykonaj("UPDATE stan_punktow SET stan = 'rozpoznany' WHERE projekt_id = (SELECT id FROM projekty WHERE sha16 = ?)", (SHA["3263", "14"],))
    assert [x["praca_id"] for x in sesja.do_dofrezowania()] == [szara, p16] and sesja.do_dofrezowania(DATA) == [biezaca[1]]
    # cofniecie decyzji z poprzedniej doby tez dziala nastepnego dnia
    sesja.cofnij(szara)
    assert [x["praca_id"] for x in sesja.do_dofrezowania()] == [p16]


# --- blokada: plytka nie z tego trybu (wymaganie wlasciciela z 17.11.2026, zmiana zalozenia Z1) -----
@pytest.mark.parametrize("uklad,tryb,powod", [
    ("poranna", "wieczor", "plytka poranna w trybie wieczor"),
    ("okragla_poranna", "wieczor", "plytka poranna w trybie wieczor"),
    ("poranna_r54", "wieczor", "plytka poranna w trybie wieczor"),
    ("okragla_poranna_r54", "wieczor", "plytka poranna w trybie wieczor"),
    ("wieczorna", "rano", "plytka wieczorna w trybie rano"),
    ("okragla_wieczorna_r54", "rano", "plytka wieczorna w trybie rano"),
])
def test_blokada_plytki_nie_z_trybu(sesja, uklad, tryb, powod):
    w = wynik("wynik_plytka2")  # w pliku wyniku: gniazdo 1 zielone, 4 czerwone, 6 zolte, 9 pomaranczowe
    w["plytka"] = uklad
    sid = sesja.przyjmij_wynik(ZDARZENIA["wynik_plytka2"], w, tryb=tryb)
    assert skan(sesja, sid)["status"] == "plytka_nie_z_trybu" == SE.STATUS_PLYTKA_NIE_Z_TRYBU and SE.powod_nie_z_trybu(uklad, tryb) == powod
    assert [r["status_gniazda"] for r in sesja.baza.wiersze("SELECT status_gniazda FROM prace WHERE skan_id = ? ORDER BY id", (sid,))] == [
        "zielony", "czerwony", "zolty", "pomaranczowy"]  # ocena programu zostaje w bazie
    for gniazdo in (1, 4):
        for akcja in (sesja.ukruszona, sesja.ok, sesja.cofnij, lambda p: sesja.decyzja(p, "ukruszona_niewykryta")):
            with pytest.raises(SE.BladSesji, match="status 'plytka_nie_z_trybu'.*tylko na skanie przyjetym.*nie z tego trybu"):
                akcja(praca(sesja, sid, gniazdo))
    assert liczba(sesja, "decyzje") == 0 and liczba(sesja, "stan_punktow") == 0 and sesja.do_dofrezowania() == []
    if tryb == "wieczor":
        stan = sesja.stan_wieczoru(DATA)
        s = stan["skany"][0]
        assert (s["status"], s["aktywny"], s["powod"], s["liczniki"], s["moze_zastapic"]) == ("plytka_nie_z_trybu", False, powod, {}, None)
        assert all(p["kolor"] is None for p in s["prace"]) and len(s["prace"]) == 4  # 0 zielonych: ramka nie zapala gniazd takiego skanu
        assert (stan["liczniki"], stan["prac"], stan["do_dofrezowania"], stan["konflikty"]) == ({}, 0, [], [])
    else:
        assert sesja.stan_wieczoru(DATA)["skany"] == []  # skan poranny nie nalezy do stanu wieczoru


def test_blokada_plytka_zgodna_z_trybem_bez_zmian_i_jedno_miejsce_reguly(sesja):
    for uklad, tryb in (("wieczorna", "wieczor"), ("okragla_wieczorna", "wieczor"), ("wieczorna_r54", "wieczor"), ("okragla_wieczorna_r54", "wieczor"),
                        ("poranna", "rano"), ("okragla_poranna_r54", "rano")):
        assert SE.powod_nie_z_trybu(uklad, tryb) is None, (uklad, tryb)
    assert SE.czesci_ukladu("okragla_poranna_r54") == {"okragla": True, "typ": "poranna", "wersja": "_r54"}
    assert SE.czesci_ukladu("wieczorna") == {"okragla": False, "typ": "wieczorna", "wersja": ""} and SE.czesci_ukladu("porannax") is None
    assert [SE.typ_plytki(u) for u in ("poranna", "okragla_poranna", "poranna_r54", "wieczorna_r54", "okragla_wieczorna", "cos")] == [
        "poranna", "poranna", "poranna", "wieczorna", "wieczorna", None]
    w = wynik("wynik_plytka2")
    w["plytka"] = "poranna"
    rano = sesja.przyjmij_wynik(ZDARZENIA["wynik_plytka2"], w, tryb="rano")  # plytka poranna rano: przyjeta jak dotad
    wieczor = przyjmij(sesja, "wynik_plytka3")  # okragla wieczorna wieczorem
    assert skan(sesja, rano)["status"] == "przyjety" and skan(sesja, wieczor)["status"] == "przyjety"
    assert skany_po_id(sesja)[wieczor]["powod"] is None
    with pytest.raises(SE.BladSesji, match="dopuscic mozna tylko skan plytki nie z tego trybu"):
        sesja.dopusc_plytke(wieczor)


def test_blokada_skan_nie_z_trybu_nie_zastepuje_i_nie_jest_zastepowany(sesja):
    dobry = przyjmij(sesja, "wynik_plytka2")  # wieczorna nr 2
    sesja.ukruszona(praca(sesja, dobry, 4))
    w = wynik("wynik_plytka2")
    w["plytka"] = "poranna"  # ten sam numer plytki, ale plytka poranna zeskanowana wieczorem
    zly = sesja.przyjmij_wynik({**ZDARZENIA["wynik_plytka2"], "sha16": "1" * 16}, w)
    assert potw(sesja.stan_wieczoru(DATA)) == []
    for wywolanie in (lambda: sesja.zastap_skan(zly), lambda: sesja.zastap_skan(zly, dobry)):
        with pytest.raises(SE.BladSesji, match="status 'plytka_nie_z_trybu'"):
            wywolanie()
    dobry2 = przyjmij(sesja, "wynik_plytka2", sha16="2" * 16)  # poprawny skan po zlym: zly nie jest kandydatem
    assert potw(sesja.stan_wieczoru(DATA)) == [{"skan_id": dobry2, "poprzedni_id": dobry, "numer_plytki": 2}]
    with pytest.raises(SE.BladSesji, match="musi byc wczesniejszy, aktywny"):
        sesja.zastap_skan(dobry2, zly)
    assert skan(sesja, dobry)["status"] == "przyjety" and len(sesja.do_dofrezowania()) == 1 and skan(sesja, zly)["status"] == "plytka_nie_z_trybu"


def test_blokada_swiadome_dopuszczenie_z_operatorem_i_jego_cofniecie(tmp_path):
    s = nowa_sesja(tmp_path, operator=None)
    try:
        wypelnij_indeks(s.baza)
        w = wynik("wynik_plytka2")
        w["plytka"] = "okragla_poranna_r54"
        sid = s.przyjmij_wynik(ZDARZENIA["wynik_plytka2"], w)
        with pytest.raises(SE.BladSesji, match="wybierz osobe"):  # dopuszczenie bez operatora: odmowa
            s.decyzja(None, "uklad", SE.DOPUSC_PLYTKE, skan_id=sid)
        assert skan(s, sid)["status"] == "plytka_nie_z_trybu" and liczba(s, "decyzje") == 0
        s.wybierz_operatora("Technik B")
        d = s.decyzja(None, "uklad", SE.DOPUSC_PLYTKE, skan_id=sid)
        wiersz = s.baza.wiersz("SELECT * FROM decyzje WHERE id = ?", (d,))
        assert (wiersz["rodzaj"], wiersz["wartosc"], wiersz["skan_id"], wiersz["praca_id"], wiersz["operator"]) == (
            "uklad", "dopusc_plytke_nie_z_trybu", sid, None, "Technik B")
        zd = s.baza.wiersze("SELECT * FROM zdarzenia WHERE typ = 'plytka_nie_z_trybu_dopuszczona'")
        assert len(zd) == 1 and zd[0]["skan_id"] == sid and json.loads(zd[0]["dane"])["decyzja_id"] == d and "Technik" not in zd[0]["dane"]
        # po dopuszczeniu skan jest liczony normalnie
        stan = s.stan_wieczoru(DATA)
        assert (stan["skany"][0]["status"], stan["skany"][0]["aktywny"], stan["skany"][0]["powod"]) == ("przyjety", True, None)
        assert stan["liczniki"] == {"zielony": 1, "czerwony": 1, "zolty": 1, "pomaranczowy": 1}
        p16 = praca(s, sid, 4)
        s.ukruszona(p16)
        assert [x["praca_id"] for x in s.do_dofrezowania()] == [p16] and stan_punktu(s, SHA["0412", "16"])["stan"] == "do_dofrezowania"
        # cofniecie dopuszczenia przywraca blokade: decyzje o pracach przestaja sie liczyc (zostaja w bazie)
        c = s.cofnij_dopuszczenie(sid)
        wiersz = s.baza.wiersz("SELECT * FROM decyzje WHERE id = ?", (c,))
        assert (wiersz["rodzaj"], wiersz["wartosc"], wiersz["skan_id"], wiersz["praca_id"]) == ("cofniecie", str(d), sid, None)
        assert skan(s, sid)["status"] == "plytka_nie_z_trybu" and s.do_dofrezowania() == [] and s.stan_wieczoru(DATA)["liczniki"] == {}
        assert stan_punktu(s, SHA["0412", "16"])["stan"] == "oczekuje" and liczba(s, "decyzje") == 3
        assert len(s.baza.wiersze("SELECT id FROM zdarzenia WHERE typ = 'plytka_nie_z_trybu_blokada_przywrocona'")) == 1
        with pytest.raises(SE.BladSesji, match="nie ma dopuszczenia do cofniecia"):
            s.cofnij_dopuszczenie(sid)
        with pytest.raises(SE.BladSesji, match="status 'plytka_nie_z_trybu'"):
            s.ok(p16)
        # ponowne dopuszczenie: wczesniejsza decyzja "Ukruszona" znow sie liczy; cofniecie takze przez decyzja(..., "cofniecie", skan_id=...)
        s.dopusc_plytke(sid)
        assert [x["praca_id"] for x in s.do_dofrezowania()] == [p16] and stan_punktu(s, SHA["0412", "16"])["praca_id"] == p16
        s.decyzja(None, "cofniecie", skan_id=sid)
        assert skan(s, sid)["status"] == "plytka_nie_z_trybu" and s.do_dofrezowania() == []
        # skan, ktory po dopuszczeniu i tak wymaga powtorzenia (drgniecie), dostaje status do_powtorzenia
        w = wynik("wynik_drgniecie")
        w["plytka"] = "poranna"
        dr = s.przyjmij_wynik(ZDARZENIA["wynik_drgniecie"], w)
        assert skan(s, dr)["status"] == "plytka_nie_z_trybu"
        s.dopusc_plytke(dr)
        assert skan(s, dr)["status"] == "do_powtorzenia" and skany_po_id(s)[dr]["liczniki"] == {"zolty": 3}
    finally:
        s.baza.zamknij()


# --- kryterium 6 ------------------------------------------------------------------------------
def test_k6_ten_sam_projekt_w_dwoch_gniazdach_wieczoru_to_konflikt(sesja):
    s1 = przyjmij(sesja, "wynik_plytka1")
    przyjmij(sesja, "wynik_plytka2")
    assert sesja.konflikty(DATA) == [] and sesja.stan_wieczoru(DATA)["konflikty"] == []
    sk = przyjmij(sesja, "wynik_konflikt")  # plytka nr 3, gniazdo 2: ten sam projekt co plytka nr 1, gniazdo 1
    wspolny = SHA["3263", "11"]
    konflikty = sesja.konflikty(DATA)
    assert len(konflikty) == 1 and konflikty[0]["sha16"] == wspolny
    assert [(m["skan_id"], m["numer_plytki"], m["gniazdo"], m["praca_id"]) for m in konflikty[0]["miejsca"]] == [
        (s1, 1, 1, praca(sesja, s1, 1)), (sk, 3, 2, praca(sesja, sk, 2))]
    assert sesja.stan_wieczoru(DATA)["konflikty"] == konflikty
    zd = sesja.baza.wiersze("SELECT * FROM zdarzenia WHERE typ = 'konflikt_projektu'")  # zgloszony przy przyjeciu skanu
    assert len(zd) == 1 and zd[0]["skan_id"] == sk and json.loads(zd[0]["dane"])["sha16"] == [wspolny]
    assert sesja.konflikty("2026-11-18") == []
    # projekt kandydata pracy szarej ("bez projektu") nie jest przypisaniem: gniazdo 7 plytki 1 (szare) + ten sam sha16 gdzie indziej to nie konflikt
    w = wynik("wynik_plytka3")
    w["gniazda"][0]["kandydaci"][0]["id"] = SHA["3350", "35"]
    w["numer"] = 9
    sesja.przyjmij_wynik({**ZDARZENIA["wynik_plytka3"], "sha16": "fedcba9876543210"}, w)
    assert [k["sha16"] for k in sesja.konflikty(DATA)] == [wspolny]


def test_k6_konflikt_znika_po_zastapieniu_skanu_i_nie_obejmuje_zeba_dofrezowanego(sesja):
    s1 = przyjmij(sesja, "wynik_plytka1")
    s1b = przyjmij(sesja, "wynik_plytka1_ponownie")
    # przed potwierdzeniem zastapienia te same projekty sa w dwoch aktywnych skanach: zgloszone
    assert {k["sha16"] for k in sesja.konflikty(DATA)} == {SHA["3263", "11"], SHA["3263", "14"], SHA["3301", "36"], SHA["3301", "46"]}
    sesja.zastap_skan(s1b)
    assert sesja.konflikty(DATA) == []
    # zab oznaczony "Ukruszona" i ten sam STL jeszcze raz tego wieczoru (dofrezowany, SE4): to nie konflikt
    sesja.ukruszona(praca(sesja, s1b, 1))
    przyjmij(sesja, "wynik_konflikt")
    assert sesja.konflikty(DATA) == []
    sesja.cofnij(praca(sesja, s1b, 1))
    assert [k["sha16"] for k in sesja.konflikty(DATA)] == [SHA["3263", "11"]]
    assert s1 != s1b


# --- kryterium 8 / decyzja wlasciciela 4: nazwy zlecen tylko w czterech tabelach -------------------
def test_k8_nazwy_folderow_i_plikow_zlecen_nie_wychodza_poza_cztery_tabele(tmp_path):
    s = nowa_sesja(tmp_path)
    try:
        wypelnij_indeks(s.baza)
        _scenariusz(s)
        IMP.importuj(s.baza, PLIK_DECYZJI)
        plik_listy = s.zapisz_do_dofrezowania(DATA, tmp_path / "dane" / "listy")
        foldery = [z["folder"] for z in INDEKS["zlecenia"]]
        nazwiska = sorted({czesc.lower() for f in foldery for czesc in f.split()[1:]})  # "testowa", "anna", ...
        pliki_stl = [p["plik"] for p in INDEKS["projekty"]]
        assert len(foldery) == 5 and len(nazwiska) == 10 and len(pliki_stl) == 16
        assert set(B.TABELE_Z_NAZWAMI) == {"zlecenia", "projekty", "frezowania", "excel_zapisy"}
        zrzut = s.baza.zrzut()
        # w czterech tabelach nazwy sa (excel_zapisy jeszcze puste) ...
        assert sorted(w["folder"] for w in zrzut["zlecenia"]) == sorted(foldery)
        assert sorted(w["plik"] for w in zrzut["projekty"]) == sorted(pliki_stl) and all(w["plik_w_raporcie"] in pliki_stl for w in zrzut["frezowania"])
        # ... a w siedmiu pozostalych, w plikach obok bazy i w stanie wieczoru - ani folderu, ani nazwiska, ani nazwy pliku STL
        assert all(zrzut[t] for t in ("skany", "prace", "decyzje", "stan_punktow", "zdarzenia"))
        slowa = nazwiska + [f.lower() for f in foldery] + [p.lower() for p in pliki_stl]
        assert brak_slow_poza_tabelami_nazw(s, tmp_path, slowa) == 8  # 7 plikow wynikow + lista "do dofrezowania"
        assert plik_listy.exists() and "3263" in json.dumps(s.stan_wieczoru(DATA))
        # zrzut "bez nazw" (do logow, dla programistow): kolumny z nazwami puste we wszystkich czterech tabelach
        bez = s.baza.zrzut(bez_nazw=True)
        for tekst in (str(v) for t in B.TABELE for w in bez[t] for v in w.values() if isinstance(v, str)):
            assert not any(sl in tekst.lower() for sl in slowa), tekst
        assert bez["zlecenia"][0]["kuweta"] == "3263" and bez["projekty"][0]["sha16"] == SHA["3263", "11"] and bez["skany"] == zrzut["skany"]
    finally:
        s.baza.zamknij()


def test_p2_plik_wyniku_bez_folderow_projektow_i_bez_sciezek(sesja, tmp_path):
    """P2: `foldery_projektow` i kazda sciezka w tekstach wyniku (uwagi, komunikaty) nie trafiaja do `dane/wyniki` ani do bazy."""
    w = wynik("wynik_plytka1")
    w["foldery_projektow"] = [SCIEZKA_ZLECENIA, SCIEZKA_PRYWATNA]  # silnik zbudowal pule z folderow zlecen
    w["gniazda"][0]["uwagi"] = [f"nie wczytano projektu {SCIEZKA_ZLECENIA}\\2026-11-16_nazwiskowski-11-crown_cad.stl - pominiety"]
    w["uklad_auto"]["powod"] = f"pula z '{SCIEZKA_PRYWATNA}' (1 folder)"
    sid = sesja.przyjmij_wynik(ZDARZENIA["wynik_plytka1"], w)
    sesja.ukruszona(praca(sesja, sid, 2))
    sesja.zapisz_do_dofrezowania(DATA, tmp_path / "dane" / "listy")
    zapis = json.loads(sesja.sciezka_wyniku(sid).read_text(encoding="utf-8"))
    assert "foldery_projektow" not in zapis and zapis["foldery_projektow_liczba"] == 2
    assert zapis["gniazda"][0]["uwagi"] == ["nie wczytano projektu <sciezka>"] and zapis["uklad_auto"]["powod"] == "pula z '<sciezka>' (1 folder)"
    assert zapis["gniazda"][1:] == w["gniazda"][1:] and zapis["skan"] == w["skan"] and zapis["macierz_skan_do_plytki"] == w["macierz_skan_do_plytki"]
    assert w["foldery_projektow"] == [SCIEZKA_ZLECENIA, SCIEZKA_PRYWATNA]  # slownik podany przez silnik nie jest zmieniany
    assert brak_slow_poza_tabelami_nazw(sesja, tmp_path, ["nazwiskow", "zmyslony", "onedrive"]) == 2  # wynik + lista


# --- runda 3: P2 - plik wyniku nigdy nie jest kasowany ani nadpisywany --------------------------------
def test_p2r3_plik_wyniku_nigdy_nie_jest_kasowany_ani_nadpisywany(tmp_path):
    katalog = tmp_path / "dane" / "wyniki"
    plik_bazy = tmp_path / "dane" / "stanowisko.sqlite"
    katalog.mkdir(parents=True)
    (katalog / "skan000001_skan_przerwany_wynik.json").write_text("{}", encoding="utf-8")  # sierota po zabitym procesie (nazwa z rundy 2)
    (katalog / "notatka.txt").write_text("plik spoza programu", encoding="utf-8")
    s = nowa_sesja(tmp_path)
    sid = przyjmij(s, "wynik_plytka1")
    stary = s.sciezka_wyniku(sid)
    tresc = stary.read_bytes()
    assert sid == 1 and ZDARZENIA["wynik_plytka1"]["sha16"] in stary.name and "20261117_1900" in stary.name  # nazwa: czas przyjecia + sha16 skanu
    assert sorted(x.name for x in katalog.iterdir()) == sorted(["notatka.txt", "skan000001_skan_przerwany_wynik.json", stary.name])
    # (B1) baza zalozona od nowa przy tym samym katalogu wynikow: numery skanow sie powtarzaja, plik starej bazy zostaje
    s.baza.zamknij()
    plik_bazy.unlink()
    s = nowa_sesja(tmp_path)  # ten sam zegar od poczatku: ten sam czas przyjecia i ten sam plik skanu
    try:
        nowy_id = przyjmij(s, "wynik_plytka1")
        nowy = s.sciezka_wyniku(nowy_id)
        assert nowy_id == sid and nowy != stary and stary.read_bytes() == tresc and nowy.exists()
        assert len(list(katalog.glob("*_wynik.json"))) == 3
        assert s.osierocone_wyniki() == sorted([katalog / "skan000001_skan_przerwany_wynik.json", stary])  # wypisane, nie usuniete
        # (B2) baza przywrocona z kopii: plik wyniku skanu sprzed przywrocenia zostaje
        kopia = s.baza.kopia(tmp_path / "kopia.sqlite")
        drugi = przyjmij(s, "wynik_plytka2")
        plik_drugiego = s.sciezka_wyniku(drugi)
        s.baza.zamknij()
        shutil.copy(kopia, plik_bazy)
        s = nowa_sesja(tmp_path)
        trzeci = przyjmij(s, "wynik_plytka3")
        assert trzeci == drugi and plik_drugiego.exists() and s.sciezka_wyniku(trzeci) != plik_drugiego
        assert json.loads(plik_drugiego.read_text(encoding="utf-8"))["skan"] == wynik("wynik_plytka2")["skan"]
        assert len(list(katalog.glob("*_wynik.json"))) == 5 and (katalog / "notatka.txt").exists()
        assert s.osierocone_wyniki() == sorted([katalog / "skan000001_skan_przerwany_wynik.json", stary, plik_drugiego])
        assert all(x.exists() for x in s.osierocone_wyniki())
    finally:
        s.baza.zamknij()


# --- runda 3: P1 - jedna pozycja listy na punkt projektu ---------------------------------------------
def test_p1r3_ten_sam_zab_ukruszony_na_dwoch_skanach_to_jedna_pozycja(sesja, zegar, tmp_path):
    # (a) ta sama plytka z tymi samymi pracami zeskanowana po ponad 60 min (nowy wsad): zab 16 z kuwety 0412 oznaczony na obu skanach
    zegar.ustaw(f"{DATA}T15:00:00")
    a = _plytka(sesja, 5, "c" * 16)
    pa = praca(sesja, a, 4)
    sesja.ukruszona(pa)
    zegar.ustaw(f"{DATA}T17:00:00")
    b = _plytka(sesja, 5, "d" * 16)
    pb = praca(sesja, b, 4)
    assert potw(sesja.stan_wieczoru(DATA)) == [] and sesja.pozycja_projektu(pb)["praca_id"] == pa  # okno moze ostrzec przed kliknieciem
    sesja.ukruszona(pb)
    lista = sesja.do_dofrezowania()
    assert [x["praca_id"] for x in lista] == [pb] and pozycje(lista) == [("0412", "16", "K-1102")]  # jeden punkt = jedna pozycja (aktualna praca)
    assert lista[0]["powtorzenia"] == [{"praca_id": pa, "skan_id": a, "numer_plytki": 5, "gniazdo": 4, "doba": DATA, "zmiana": 2}]
    punkty = sesja.baza.wiersze("SELECT projekt_id, praca_id FROM stan_punktow WHERE stan = 'do_dofrezowania'")
    assert len(punkty) == 1 and punkty[0]["praca_id"] == pb
    assert len(sesja.zapisz_do_dofrezowania(katalog=tmp_path / "dane" / "listy").read_text(encoding="utf-8").splitlines()) == 2  # naglowek + 1
    # informacja "ten zab jest juz na liscie (skan X, zmiana Y)": w dzienniku i w stanie obu prac
    zd = sesja.baza.wiersze("SELECT * FROM zdarzenia WHERE typ = 'ukruszona_powtorzona'")
    assert len(zd) == 1 and json.loads(zd[0]["dane"]) == {"praca_id": pb, "byla_praca_id": pa, "byl_skan_id": a, "doba": DATA, "zmiana": 2}
    stan = sesja.stan_wieczoru(DATA)
    na_liscie = {x["id"]: x["na_liscie"] for s in stan["skany"] for x in s["prace"]}
    assert na_liscie[pa] == na_liscie[pb] == {"praca_id": pb, "skan_id": b, "doba": DATA, "zmiana": 2} and na_liscie[praca(sesja, a, 1)] is None
    assert [x["praca_id"] for x in stan["do_dofrezowania"]] == [pb] and stan["konflikty"] != []  # zielone prace obu skanow sa konfliktem jak dotad
    # cofniecie nowszej decyzji: pozycja wraca na wczesniejsza prace, nie znika
    sesja.cofnij(pb)
    assert [(x["praca_id"], x["powtorzenia"]) for x in sesja.do_dofrezowania()] == [(pa, [])]
    # (c) cofniecie zastapienia, gdy oba skany maja "Ukruszona" na tym zebie
    sesja.ukruszona(pb)
    sesja.zastap_skan(b, a)
    assert [x["praca_id"] for x in sesja.do_dofrezowania()] == [pb]
    sesja.cofnij_zastapienie(b)
    lista = sesja.do_dofrezowania()
    assert len(lista) == 1 and lista[0]["projekt_id"] == punkty[0]["projekt_id"] and len(lista[0]["powtorzenia"]) == 1
    assert sesja.baza.wiersz("SELECT count(*) AS n FROM stan_punktow WHERE stan = 'do_dofrezowania'")["n"] == 1


def test_p1r3_zab_dofrezowany_znow_ukruszony_nastepnego_dnia_to_jedna_pozycja(sesja, zegar):
    s1 = przyjmij(sesja, "wynik_plytka1")  # doba 17.11, zmiana 2
    stara = praca(sesja, s1, 2)
    sesja.ukruszona(stara)
    assert [x["praca_id"] for x in sesja.do_dofrezowania(DATA)] == [stara]
    zegar.ustaw("2026-11-18T19:00:00")  # nastepnego dnia zab dofrezowany lezy na plytce i znow jest ukruszony
    s2 = przyjmij(sesja, "wynik_plytka1")
    nowa = praca(sesja, s2, 2)
    assert potw(sesja.stan_wieczoru()) == []
    sesja.ukruszona(nowa)
    biezaca = sesja.do_dofrezowania()
    assert [(x["praca_id"], x["doba"], x["zmiana"]) for x in biezaca] == [(nowa, "2026-11-18", 2)]  # jedna pozycja, nie dwie z dwoch dob
    assert [(y["praca_id"], y["doba"]) for y in biezaca[0]["powtorzenia"]] == [(stara, DATA)]
    assert sesja.do_dofrezowania(DATA) == [] and sesja.do_dofrezowania("2026-11-18") == biezaca
    assert sesja.baza.wiersz("SELECT count(*) AS n FROM stan_punktow WHERE stan = 'do_dofrezowania'")["n"] == 1


def _niezmienniki(s: SE.Sesja) -> None:
    """Lista "do dofrezowania" a `stan_punktow` i decyzje - liczone niezaleznie od kodu sesji (wlasne odtworzenie decyzji)."""
    lista = s.do_dofrezowania()
    punkty = {w["projekt_id"]: w["praca_id"] for w in s.baza.wiersze("SELECT projekt_id, praca_id FROM stan_punktow WHERE stan = 'do_dofrezowania'")}
    assert len({x["praca_id"] for x in lista}) == len(lista)
    assert sorted((x["projekt_id"], x["praca_id"]) for x in lista if x["projekt_id"] is not None) == sorted(punkty.items())  # 1 punkt = 1 pozycja
    prace = s.baza.wiersze("SELECT p.id, p.projekt_id FROM prace p JOIN skany k ON k.id = p.skan_id WHERE k.tryb = 'wieczor' AND k.status IN ('przyjety', 'do_powtorzenia')")
    ukruszone = {}
    for w in prace:
        decyzje = s.baza.wiersze("SELECT id, rodzaj, wartosc FROM decyzje WHERE praca_id = ? ORDER BY id", (w["id"],))
        cofniete = {int(d["wartosc"]) for d in decyzje if d["rodzaj"] == "cofniecie"}
        obowiazuje = [d["rodzaj"] for d in decyzje if d["rodzaj"] != "cofniecie" and d["id"] not in cofniete]
        if obowiazuje and obowiazuje[-1] in ("ukruszona", "ukruszona_niewykryta"):
            ukruszone[w["id"]] = w["projekt_id"]
    for projekt, praca_id in punkty.items():  # punkt wskazuje prace z obowiazujaca "Ukruszona" w skanie aktywnym
        assert ukruszone.get(praca_id) == projekt, (projekt, praca_id)
    assert {x for x in ukruszone.values() if x is not None} == set(punkty)  # kazdy ukruszony projekt ma punkt
    assert sorted(x["praca_id"] for x in lista if x["projekt_id"] is None) == sorted(i for i, pr in ukruszone.items() if pr is None)
    for x in lista:  # powtorzenia = pozostale ukruszone prace tego samego projektu
        if x["projekt_id"] is not None:
            assert sorted(y["praca_id"] for y in x["powtorzenia"]) == sorted(i for i, pr in ukruszone.items() if pr == x["projekt_id"] and i != x["praca_id"])


def test_p1r3_losowe_sekwencje_lista_zgodna_ze_stanem_punktow(tmp_path):
    """Losowe sekwencje przyjec, decyzji, cofniec, zastapien, dopuszczen i uplywu czasu: 0 rozbieznosci lista <-> `stan_punktow`."""
    nazwy = ("wynik_plytka1", "wynik_plytka2", "wynik_plytka3", "wynik_plytka1_ponownie", "wynik_drgniecie", "wynik_konflikt", "wynik_popraw_ulozenie")
    udane = kroki = 0
    for ziarno in range(40):
        los = random.Random(ziarno)
        katalog = tmp_path / f"s{ziarno}"
        zegar = Zegar(f"{DATA}T14:00:00")
        s = nowa_sesja(katalog, zegar=zegar)
        try:
            wypelnij_indeks(s.baza)
            for krok in range(40):
                kroki += 1
                skany = [w["id"] for w in s.baza.wiersze("SELECT id FROM skany")]
                prace = [w["id"] for w in s.baza.wiersze("SELECT id FROM prace")]
                ruch = los.choice(("skan", "skan", "ukruszona", "ukruszona", "ukruszona", "ok", "niewykryta", "cofnij", "cofnij", "zastap", "zastap_wprost",
                                   "cofnij_zastapienie", "dopusc", "cofnij_dopuszczenie", "czas"))
                try:
                    if ruch == "skan" or not prace:
                        w = wynik(los.choice(nazwy))
                        w["numer"] = los.choice((1, 2, 3))
                        if los.random() < 0.15:
                            w["plytka"] = "poranna"  # plytka nie z trybu
                        s.przyjmij_wynik({"plik": f"C:/Skany/skan_{ziarno}_{krok}.stl", "sha16": f"{ziarno:08x}{krok:08x}", "rozmiar": 1, "czas_pliku": None}, w)
                    elif ruch == "ukruszona":
                        s.ukruszona(los.choice(prace))
                    elif ruch == "ok":
                        s.ok(los.choice(prace))
                    elif ruch == "niewykryta":
                        s.decyzja(los.choice(prace), "ukruszona_niewykryta")
                    elif ruch == "cofnij":
                        s.cofnij(los.choice(prace))
                    elif ruch == "zastap":
                        s.zastap_skan(los.choice(skany))
                    elif ruch == "zastap_wprost":
                        s.zastap_skan(los.choice(skany), los.choice(skany))
                    elif ruch == "cofnij_zastapienie":
                        s.cofnij_zastapienie(los.choice(skany))
                    elif ruch == "dopusc":
                        s.dopusc_plytke(los.choice(skany))
                    elif ruch == "cofnij_dopuszczenie":
                        s.cofnij_dopuszczenie(los.choice(skany))
                    else:
                        zegar.t += dt.timedelta(minutes=los.choice((5, 30, 70, 200, 600)))
                    udane += 1
                except SE.BladSesji:
                    pass
                _niezmienniki(s)
                if krok % 8 == 7:  # kolory po decyzjach we wszystkich dobach, w ktorych sa skany
                    for doba in sorted({s.doba(w["czas_analizy"]) for w in s.baza.wiersze("SELECT czas_analizy FROM skany")}):
                        for sk in s.stan_wieczoru(doba)["skany"]:
                            for x in sk["prace"]:
                                oczekiwany = (None if not sk["aktywny"] else "czerwony" if x["decyzja"] in ("ukruszona", "ukruszona_niewykryta")
                                              else "zatwierdzona_ok" if x["decyzja"] == "ok" else x["kolor"])
                                assert x["kolor"] == oczekiwany and not (sk["status"] == "do_powtorzenia" and x["kolor"] == "zielony")
        finally:
            s.baza.zamknij()
    assert kroki == 1600 and udane >= 500, udane  # proba nie jest pusta: wiekszosc operacji sie wykonuje


# --- runda 3: uwagi drobne ------------------------------------------------------------------------------
def test_d1r3_zastapienie_wprost_wymaga_znanego_numeru_plytki(sesja):
    """D1: plytki kwadratowe wieczorem zwykle nie maja numeru (dolki poza polem) - dwa skany bez numeru to moga byc rozne plytki."""
    w = wynik("wynik_plytka1")
    w["numer"], w["numer_zrodlo"] = None, "nieznany"
    a = sesja.przyjmij_wynik({**ZDARZENIA["wynik_plytka1"], "sha16": "a" * 16}, w)
    sesja.ukruszona(praca(sesja, a, 2))
    b = sesja.przyjmij_wynik({**ZDARZENIA["wynik_plytka1"], "sha16": "b" * 16}, w)
    assert potw(sesja.stan_wieczoru(DATA)) == []
    with pytest.raises(SE.BladSesji, match="najpierw podaj numer plytki"):
        sesja.zastap_skan(b, a)
    sesja.podaj_numer_plytki(a, 1)
    with pytest.raises(SE.BladSesji, match="najpierw podaj numer plytki"):
        sesja.zastap_skan(b, a)  # numer zna tylko jeden ze skanow
    assert skan(sesja, a)["status"] == "przyjety" and len(sesja.do_dofrezowania()) == 1
    sesja.podaj_numer_plytki(b, 1)
    assert sesja.zastap_skan(b, a) == a
    # numer sprzeczny z powiazaniem "zastapil / zastapiony" jest odrzucany (po obu stronach)
    for skan_id in (a, b):
        with pytest.raises(SE.BladSesji, match="inny numer plytki"):
            sesja.podaj_numer_plytki(skan_id, 2)
    sesja.podaj_numer_plytki(b, 1)  # ten sam numer jeszcze raz: bez przeszkod
    assert (skan(sesja, a)["numer_plytki"], skan(sesja, b)["numer_plytki"]) == (1, 1)
    # ten sam plik skanu (sha16) bez numeru: to pewnie ta sama plytka, zastapienie wprost dozwolone
    c = sesja.przyjmij_wynik({**ZDARZENIA["wynik_plytka3"], "sha16": "c" * 16}, {**wynik("wynik_plytka3"), "numer": None})
    d = sesja.przyjmij_wynik({**ZDARZENIA["wynik_plytka3"], "sha16": "c" * 16}, {**wynik("wynik_plytka3"), "numer": None})
    assert sesja.zastap_skan(d, c) == c


def test_d2r3_doba_i_zmiana_pozycji_z_chwili_przyjecia_skanu(sesja, zegar):
    """D2: skan przyjety 05:50 (doba 17.11, zmiana 3), "Ukruszona" klikniete 06:05 - pozycja nalezy do doby skanu."""
    zegar.ustaw("2026-11-18T05:50:00")
    s1 = przyjmij(sesja, "wynik_plytka1")
    zegar.ustaw("2026-11-18T06:05:00")
    sesja.ukruszona(praca(sesja, s1, 2))
    lista = sesja.do_dofrezowania()
    assert [(x["doba"], x["zmiana"], x["czas"][:16]) for x in lista] == [(DATA, 3, "2026-11-18T06:05")]
    assert sesja.do_dofrezowania(DATA) == lista and sesja.do_dofrezowania("2026-11-18") == []
    assert sesja.stan_wieczoru(DATA)["do_dofrezowania"] == lista and sesja.stan_wieczoru("2026-11-18")["do_dofrezowania"] == []


def test_d4r3_cofniecie_dopuszczenia_skanu_ktory_zastapil_inny(sesja):
    """D4: plytka nie moze po cichu zostac bez aktywnego skanu - najpierw trzeba cofnac zastapienie."""
    w = wynik("wynik_plytka2")
    w["plytka"] = "poranna"
    stary = sesja.przyjmij_wynik({**ZDARZENIA["wynik_plytka2"], "sha16": "1" * 16}, w)
    sesja.dopusc_plytke(stary)
    sesja.ukruszona(praca(sesja, stary, 4))
    nowy = sesja.przyjmij_wynik({**ZDARZENIA["wynik_plytka2"], "sha16": "2" * 16}, w)
    sesja.dopusc_plytke(nowy)
    assert sesja.zastap_skan(nowy) == stary
    with pytest.raises(SE.BladSesji, match=f"skan {nowy} zastapil skan {stary}.*najpierw cofnij zastapienie"):
        sesja.cofnij_dopuszczenie(nowy)
    assert (skan(sesja, nowy)["status"], skan(sesja, stary)["status"]) == ("przyjety", "zastapiony")
    sesja.cofnij_zastapienie(nowy)
    sesja.cofnij_dopuszczenie(nowy)
    assert (skan(sesja, nowy)["status"], skan(sesja, stary)["status"]) == ("plytka_nie_z_trybu", "przyjety")
    assert len(sesja.do_dofrezowania()) == 1  # decyzja starego skanu znow sie liczy


def test_d5r3_blad_inspekcji_i_sciezki_wzgledne_w_pliku_wyniku(sesja, tmp_path):
    """D5: `porownaj` wpisuje tresc wyjatku inspekcji do `inspekcja.blad` i `uwagi` - plik wyniku dostaje je bez sciezek."""
    w = wynik("wynik_plytka1")
    opis = f"FileNotFoundError: brak pliku '{SCIEZKA_ZLECENIA}\\2026-11-16_nazwiskowski-11-crown_cad.stl' (inspect.py:120 sprawdz)"
    w["gniazda"][0]["inspekcja"] = {**w["gniazda"][0]["inspekcja"], "status": "nie_sprawdzono", "blad": opis, "uwagi": [f"blad inspekcji: {opis}"]}
    w["gniazda"][0]["status_gniazda"] = "zolty"
    w["gniazda"][1]["uwagi"] = ["nie wczytano: Cyrkon\\9911 Zmyslony Nazwiskowski\\a.stl", "zasob //serwer/Cyrkon/9911 Zmyslony Nazwiskowski/a.stl niedostepny",
                                "kopia w %USERPROFILE%\\OneDrive\\Cyrkon\\9911 Zmyslony Nazwiskowski"]
    sid = sesja.przyjmij_wynik(ZDARZENIA["wynik_plytka1"], w)
    zapis = json.loads(sesja.sciezka_wyniku(sid).read_text(encoding="utf-8"))
    assert zapis["gniazda"][0]["inspekcja"]["blad"] == "FileNotFoundError: brak pliku '<sciezka>' (inspect.py:120 sprawdz)"
    assert zapis["gniazda"][0]["inspekcja"]["uwagi"] == ["blad inspekcji: FileNotFoundError: brak pliku '<sciezka>' (inspect.py:120 sprawdz)"]
    assert zapis["gniazda"][1]["uwagi"] == ["nie wczytano: <sciezka>", "zasob <sciezka>", "kopia w <sciezka>"]
    assert sesja.baza.wiersz("SELECT status_inspekcji, status_gniazda FROM prace WHERE id = ?", (praca(sesja, sid, 1),)) == {
        "status_inspekcji": "nie_sprawdzono", "status_gniazda": "zolty"}  # blad inspekcji gniazda: zolte, nigdy zielone
    assert brak_slow_poza_tabelami_nazw(sesja, tmp_path, ["nazwiskow", "zmyslony", "onedrive", "serwer"]) == 1


def test_d6r3_import_musi_byc_przedluzeniem_ostatniego_importu(sesja, tmp_path):
    """D6: plik zgodny z pierwszym importem, ale ze zmienionymi wierszami dopisanymi drugim importem, jest odrzucany."""
    plik = tmp_path / "decyzje.csv"
    plik.write_bytes(PLIK_DECYZJI.read_bytes())
    assert IMP.importuj(sesja.baza, plik)["decyzje"] == 7
    with open(plik, "a", newline="", encoding="utf-8") as f:
        f.write("2026-11-12T10:00:00;skan_test_a.stl;2;a15b5b27bcd59f33;14;ok;czerwony;1\n2026-11-12T10:00:09;skan_test_c.stl;5;;;ukruszona;szary;0\n")
    assert IMP.importuj(sesja.baza, plik)["decyzje"] == 2 and liczba(sesja, "decyzje") == 9
    plik.write_text(plik.read_text(encoding="utf-8").replace("2026-11-12T10:00:09", "2026-11-12T10:00:10"), encoding="utf-8")  # zmieniony wiersz 9
    with pytest.raises(IMP.BladImportu, match="nie jest przedluzeniem"):
        IMP.importuj(sesja.baza, plik)
    assert liczba(sesja, "decyzje") == 9


def test_d7r3_blokada_nie_przepuszcza_nieznanego_ukladu_ani_trybu(sesja):
    """D7: uklad o nazwie spoza wzoru i nieznany tryb nie moga dac skanu przyjetego po cichu."""
    w = wynik("wynik_plytka2")
    w["plytka"] = "nowy_uklad_dopisany_w_ustawieniach"
    sid = sesja.przyjmij_wynik(ZDARZENIA["wynik_plytka2"], w)
    assert skan(sesja, sid)["status"] == "plytka_nie_z_trybu"
    st = sesja.stan_wieczoru(DATA)["skany"][0]
    assert st["powod"] == "nieznany uklad plytki 'nowy_uklad_dopisany_w_ustawieniach' w trybie wieczor" and st["liczniki"] == {} and st["aktywny"] is False
    assert SE.powod_nie_z_trybu(None, "wieczor") == "nieznany uklad plytki None w trybie wieczor" and SE.powod_nie_z_trybu("porannax", "rano") is not None
    sesja.dopusc_plytke(sid)  # swiadome dopuszczenie dziala jak dla plytki nie z trybu
    assert skan(sesja, sid)["status"] == "przyjety"
    przed = liczba(sesja, "skany")
    for tryb in ("wieczor ", "Wieczor", "inny_tryb", None, ""):
        with pytest.raises(SE.BladSesji, match="nieznany tryb"):
            sesja.przyjmij_wynik(ZDARZENIA["wynik_plytka3"], wynik("wynik_plytka3"), tryb=tryb)
        with pytest.raises(SE.BladSesji, match="nieznany tryb"):
            sesja.przyjmij_blad(ZDARZENIA["wynik_plytka3"], "awaria", tryb=tryb)
        with pytest.raises(SE.BladSesji, match="nieznany tryb"):
            SE.powod_nie_z_trybu("wieczorna", tryb)
    assert liczba(sesja, "skany") == przed and len(list((sesja.katalog_wynikow).glob("*_wynik.json"))) == przed


def test_d8r3_nazwy_operatorow_przycinane_z_bialych_znakow(sesja):
    s = SE.Sesja(sesja.baza, operatorzy=[" Technik A ", "Technik B\t"], zegar=Zegar())
    assert s.operatorzy == ("Technik A", "Technik B")
    s.wybierz_operatora("Technik B ")
    assert s.operator == "Technik B"
    with pytest.raises(SE.BladSesji, match="niepuste i rozne"):
        SE.Sesja(sesja.baza, operatorzy=["Technik A", "Technik A "])
    with pytest.raises(SE.BladSesji, match="niepuste i rozne"):
        SE.Sesja(sesja.baza, operatorzy=["Technik A", "  "])


def test_d10r3_propozycja_ponownego_skanu_podaje_decyzje_ktore_przestana_obowiazywac(sesja):
    """D10 (kontrakt dla A3): okno ma z czego ostrzec przed potwierdzeniem "to ponowny skan"."""
    s1 = przyjmij(sesja, "wynik_plytka1")
    sesja.ukruszona(praca(sesja, s1, 2))
    sesja.ok(praca(sesja, s1, 3))
    sesja.ukruszona(praca(sesja, s1, 5))
    sesja.cofnij(praca(sesja, s1, 5))  # cofnieta: nie liczy sie
    s1b = przyjmij(sesja, "wynik_plytka1_ponownie")
    propozycje = sesja.stan_wieczoru(DATA)["do_potwierdzenia"]
    assert len(propozycje) == 1 and (propozycje[0]["skan_id"], propozycje[0]["poprzedni_id"]) == (s1b, s1)
    assert (propozycje[0]["liczba_decyzji"], propozycje[0]["liczba_ukruszonych"]) == (2, 1)
    assert propozycje[0]["decyzje"] == [
        {"praca_id": praca(sesja, s1, 2), "gniazdo": 2, "rodzaj": "ukruszona", "kuweta": "3263", "zeby": "14"},
        {"praca_id": praca(sesja, s1, 3), "gniazdo": 3, "rodzaj": "ok", "kuweta": "3301", "zeby": "36"}]
    assert sesja.zastap_skan(s1b) == s1 and sesja.do_dofrezowania() == []  # samo potwierdzenie bez zmian
    bez = przyjmij(sesja, "wynik_plytka2")
    bez2 = przyjmij(sesja, "wynik_plytka2", sha16="9" * 16)
    p = [x for x in sesja.stan_wieczoru(DATA)["do_potwierdzenia"] if x["skan_id"] == bez2][0]
    assert (p["poprzedni_id"], p["liczba_decyzji"], p["liczba_ukruszonych"], p["decyzje"]) == (bez, 0, 0, [])


# --- kryterium 9 ------------------------------------------------------------------------------
def _wiersze_pliku(plik: Path) -> list[list[str]]:
    return [linia.split(";") for linia in plik.read_text(encoding="utf-8").splitlines()[1:] if linia.strip()]


def test_k9_import_decyzji_csv_wiersz_w_wiersz(sesja):
    wiersze = _wiersze_pliku(PLIK_DECYZJI)
    assert len(wiersze) == 7
    r = IMP.importuj(sesja.baza, PLIK_DECYZJI)
    assert r == {"wiersze": 7, "decyzje": 7, "skany": 2, "prace": 4, "pominiete": 0}
    decyzje = sesja.baza.wiersze("SELECT d.*, p.gniazdo, p.kandydat1_sha16, p.status_gniazda, p.ubytki, p.projekt_id, s.plik, s.tryb, s.status, s.wersja_programu "
                                 "FROM decyzje d JOIN prace p ON p.id = d.praca_id JOIN skany s ON s.id = p.skan_id ORDER BY d.id")
    assert len(decyzje) == len(wiersze)  # kryterium 9: liczba wierszy w `decyzje` = liczba wierszy pliku
    for d, (czas, plik, gniazdo, projekt, _zeby, decyzja, status, ubytkow) in zip(decyzje, wiersze):
        assert (d["czas"], d["plik"], d["gniazdo"], d["rodzaj"]) == (czas, plik, int(gniazdo), decyzja)
        assert (d["kandydat1_sha16"], d["status_gniazda"], d["ubytki"]) == (projekt or None, status, int(ubytkow))
        assert d["operator"] == "import" and d["wartosc"] is None and d["skan_id"] is None  # decyzja wlasciciela 2: operator = import
        assert (d["tryb"], d["status"], d["wersja_programu"]) == (None, "import", "import decyzje.csv")
    znane = [d for d in decyzje if d["kandydat1_sha16"]]
    assert len(znane) == 6 and all(d["projekt_id"] is not None for d in znane)  # projekt z indeksu po sha16
    assert liczba(sesja, "skany") == 2 and liczba(sesja, "prace") == 4
    # decyzje z okna testowego nie naleza do zadnego wieczoru: nie zmieniaja list ani stanu punktow
    assert sesja.do_dofrezowania("2026-11-10") == [] and sesja.stan_wieczoru("2026-11-10")["skany"] == [] and liczba(sesja, "stan_punktow") == 0
    zd = sesja.baza.wiersze("SELECT * FROM zdarzenia WHERE typ = 'import_decyzji'")
    assert len(zd) == 1 and json.loads(zd[0]["dane"])["wiersze"] == 7 and "skan_test" not in zd[0]["dane"]


def test_p4a_import_i_cofniecie_wieczorem_nie_zostawiaja_punktu_w_do_dofrezowania(sesja):
    """P4 (a): praca z okna testowego oznaczona "ukruszona" nie trzyma punktu projektu po cofnieciu decyzji wieczornej."""
    IMP.importuj(sesja.baza, PLIK_DECYZJI)  # w pliku okna: zab 14 z kuwety 3263 oznaczony "ukruszona"
    assert liczba(sesja, "stan_punktow") == 0
    s1 = przyjmij(sesja, "wynik_plytka1")
    p = praca(sesja, s1, 2)  # ten sam projekt wieczorem
    sesja.ukruszona(p)
    assert stan_punktu(sesja, SHA["3263", "14"])["stan"] == "do_dofrezowania"
    sesja.cofnij(p)
    pk = stan_punktu(sesja, SHA["3263", "14"])
    assert (pk["stan"], pk["praca_id"]) == ("oczekuje", None) and sesja.do_dofrezowania(DATA) == []
    # praca z importu nie przyjmuje decyzji wieczornych
    z_importu = sesja.baza.wiersz("SELECT p.id FROM prace p JOIN skany s ON s.id = p.skan_id WHERE s.wersja_programu = 'import decyzje.csv' LIMIT 1")["id"]
    with pytest.raises(SE.BladSesji, match="status 'import'"):
        sesja.ukruszona(z_importu)


def test_k9_ponowny_import_nie_dubluje_a_dopisane_wiersze_dochodza(sesja, tmp_path):
    kopia = tmp_path / "decyzje.csv"
    kopia.write_bytes(PLIK_DECYZJI.read_bytes().replace(b"\n", b"\r\n"))  # okno testowe pisze konce linii CRLF (csv.writer)
    assert IMP.importuj(sesja.baza, kopia)["decyzje"] == 7
    assert IMP.importuj(sesja.baza, kopia) == {"wiersze": 7, "decyzje": 0, "skany": 0, "prace": 0, "pominiete": 7}
    assert liczba(sesja, "decyzje") == 7
    with open(kopia, "a", newline="", encoding="utf-8") as f:  # okno testowe dopisalo dwa wiersze
        f.write("2026-11-12T10:00:00;skan_test_a.stl;2;a15b5b27bcd59f33;14;ok;czerwony;1\r\n")
        f.write("2026-11-12T10:00:09;skan_test_c.stl;5;;;ukruszona;szary;0\r\n")
    assert IMP.importuj(sesja.baza, kopia) == {"wiersze": 9, "decyzje": 2, "skany": 1, "prace": 1, "pominiete": 7}
    assert liczba(sesja, "decyzje") == 9 == len(_wiersze_pliku(kopia)) and liczba(sesja, "skany") == 3 and liczba(sesja, "prace") == 5


def test_d7_import_pliku_ktory_nie_jest_przedluzeniem_wczesniejszego_importu(sesja, tmp_path, capsys):
    """D7: plik z poprawionym wczesniejszym wierszem zdublowalby wszystkie decyzje (tabela jest tylko do dopisywania) - odmowa."""
    assert IMP.importuj(sesja.baza, PLIK_DECYZJI)["decyzje"] == 7
    zmieniony = tmp_path / "decyzje.csv"
    zmieniony.write_text(PLIK_DECYZJI.read_text(encoding="utf-8").replace("2026-11-10T18:01:02", "2026-11-10T18:01:03"), encoding="utf-8")
    with pytest.raises(IMP.BladImportu, match="nie jest przedluzeniem"):
        IMP.importuj(sesja.baza, zmieniony)
    assert liczba(sesja, "decyzje") == 7
    assert IMP.importuj(sesja.baza, zmieniony, wymus=True)["decyzje"] == 7 and liczba(sesja, "decyzje") == 14  # swiadomie, przelacznik --wymus
    sciezka_bazy = sesja.baza.plik
    sesja.baza.zamknij()
    zmieniony.write_text(zmieniony.read_text(encoding="utf-8").replace("2026-11-10T18:01:03", "2026-11-10T18:01:04"), encoding="utf-8")
    assert IMP.main(["--plik", str(zmieniony), "--baza", str(sciezka_bazy)]) == 1 and "--wymus" in capsys.readouterr().err
    assert IMP.main(["--plik", str(zmieniony), "--baza", str(sciezka_bazy), "--wymus"]) == 0
    sesja.baza = B.otworz(sciezka_bazy)  # do zamkniecia przez fixture
    assert liczba(sesja, "decyzje") == 21


@pytest.mark.parametrize("zmiana,komunikat", [
    (("czas;skan;gniazdo", "czas;plik;gniazdo"), "naglowek"),
    ((";ukruszona;czerwony;1\n2026-11-10T18:01:40", ";moze;czerwony;1\n2026-11-10T18:01:40"), r"wiersz 2: decyzja 'moze'"),
    ((";skan_test_b.stl;4;", ";skan_test_b.stl;cztery;"), r"wiersz 5: gniazdo"),
    (("2026-11-10T18:10:30;skan_test_b.stl;7;;;ok;szary;0", "2026-11-10T18:10:30;skan_test_b.stl;7;;;ok;szary"), r"wiersz 6: 7 kolumn zamiast 8"),
    (("2026-11-10T18:02:05", "wczoraj wieczorem"), r"wiersz 4: czas"),
])
def test_k9_zly_plik_decyzji_nic_nie_importuje(sesja, tmp_path, zmiana, komunikat):
    tresc = PLIK_DECYZJI.read_text(encoding="utf-8")
    assert zmiana[0] in tresc
    zly = tmp_path / "decyzje.csv"
    zly.write_text(tresc.replace(*zmiana), encoding="utf-8")
    with pytest.raises(IMP.BladImportu, match=komunikat):
        IMP.importuj(sesja.baza, zly)
    assert liczba(sesja, "decyzje") == 0 and liczba(sesja, "skany") == 0 and liczba(sesja, "zdarzenia") == 0  # calosc albo nic


def test_k9_naglowek_importu_jest_naglowkiem_okna_testowego():
    """Import czyta dokladnie te kolumny, ktore pisze `ui_test.py` (KOLUMNY_DECYZJI); bez importu modulu okna (Qt)."""
    zrodlo = (STANOWISKO / "stanowisko" / "ui_test.py").read_text(encoding="utf-8")
    m = re.search(r"^KOLUMNY_DECYZJI = \(([^)]*)\)", zrodlo, re.M)
    assert m and tuple(re.findall(r'"(\w+)"', m.group(1))) == IMP.KOLUMNY
    assert PLIK_DECYZJI.read_text(encoding="utf-8").splitlines()[0] == ";".join(IMP.KOLUMNY)


def test_k9_narzedzie_z_wiersza_polecen(tmp_path, capsys):
    baza = tmp_path / "dane" / "stanowisko.sqlite"
    plik = tmp_path / "decyzje.csv"
    plik.write_bytes(PLIK_DECYZJI.read_bytes())
    assert IMP.main(["--plik", str(plik), "--baza", str(baza)]) == 0
    wyjscie = capsys.readouterr().out
    assert "7 wierszy" in wyjscie and "7 decyzji" in wyjscie and "skan_test" not in wyjscie
    pol = sqlite3.connect(baza)
    assert pol.execute("SELECT count(*) FROM decyzje").fetchone()[0] == 7
    pol.close()
    assert IMP.main(["--plik", str(tmp_path / "nie_ma.csv"), "--baza", str(baza)]) == 2
    assert "brak pliku" in capsys.readouterr().err


# --- ustawienia -> sesja ------------------------------------------------------------------------
def test_sesja_z_ustawien(tmp_path):
    from stanowisko import ustawienia as UST

    ust = UST.wczytaj_ustawienia(UST.PLIK_PRZYKLADU)
    ust = {**ust, "sciezki": {**ust["sciezki"], "baza": (tmp_path / "b" / "stanowisko.sqlite").as_posix(), "wyniki": (tmp_path / "b" / "wyniki").as_posix()},
           "sesja": {**ust["sesja"], "operatorzy": ["Technik A"], "granica_doby_godz": 5, "zmiany_start_godz": [5, 13, 21], "ponowny_skan_okno_min": 45}}
    s = SE.Sesja.z_ustawien(ust)
    try:
        assert s.baza.plik == tmp_path / "b" / "stanowisko.sqlite" and s.operatorzy == ("Technik A",) and (s.granica_doby_godz, s.zmiany_start_godz, s.ponowny_skan_okno_min) == (5, (5, 13, 21), 45)
        sid = s.przyjmij_wynik(ZDARZENIA["wynik_plytka3"], wynik("wynik_plytka3"))
        sk = skan(s, sid)
        assert s.sciezka_wyniku(sid).parent == tmp_path / "b" / "wyniki" and sk["wynik_json"] == f"wyniki/{s.sciezka_wyniku(sid).name}"
        assert re.fullmatch(r"[0-9a-f]{16}", sk["skrot_ustawien"]) and sk["skrot_ustawien"] == SE.skrot_ustawien(ust)
    finally:
        s.baza.zamknij()
    assert SE.katalog_wynikow(UST.wczytaj_ustawienia(UST.PLIK_PRZYKLADU)) == UST.KORZEN / "dane" / "wyniki"
    # D13: skrot ustawien = progi i uklady, przy ktorych liczono skan ([match], [inspect], [plytki]); sciezki, ramki i osoby go nie zmieniaja
    skrot = SE.skrot_ustawien(ust)
    assert SE.skrot_ustawien({**ust, "ramki": {**ust["ramki"], "port": 9000}, "sesja": {**ust["sesja"], "operatorzy": ["Ktos"]}}) == skrot
    assert SE.skrot_ustawien({**ust, "sciezki": {**ust["sciezki"], "folder_cyrkon": "D:/inny"}}) == skrot
    assert SE.skrot_ustawien({**ust, "inspect": {**ust["inspect"], "prog_glebokosci_mm": 0.09}}) != skrot
    assert SE.skrot_ustawien({**ust, "match": {**ust["match"], "pewnosc_min": 0.2}}) != skrot


# --- zgodnosc z prawdziwym silnikiem ------------------------------------------------------------
def _klucze(d: dict) -> set[str]:
    return set(d)


def test_wynik_prawdziwego_porownaj_wchodzi_do_bazy(korony, tmp_path):
    """Skan sztucznej plytki (3 atrapy koron) -> porownaj.porownaj -> session: te same klucze co w danych testowych, prace 1:1."""
    import shutil
    import warnings

    import numpy as np

    from stanowisko import porownaj as PO, synth, uklad as U, ustawienia as UST

    proj = tmp_path / "projekty"
    proj.mkdir()
    for i, p in enumerate(korony):
        shutil.copy(p, proj / f"2026-11-02_p{i}-{['11', '14', '36'][i]}-crown_cad.stl")
    uk = U.wczytaj("okragla_wieczorna")
    op = synth.Opcje.z_toml(plytka=uk.nazwa, prace_na_plytce=3, wspolczynnik=(1.22, 1.22), ubytki_na_prace=(0, 1), srednica_ubytku=(0.8, 1.4), poza_uklad=True, pole=100.0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        skan_m, prawda = synth.generuj_plytke(uk, 8, synth.pliki_projektow(proj), np.random.default_rng(1), op, 1)
        p_stl, _ = synth.zapisz(skan_m, prawda, tmp_path, "skan_sesja")
        w = PO.porownaj(p_stl, [proj], "auto", UST.wczytaj_ustawienia(), wspolczynnik=1.22)
    w = json.loads(json.dumps(w))  # tak jak przyjdzie z procesu silnika / z pliku
    wzor = wynik("wynik_plytka3")
    assert _klucze(wzor) <= _klucze(w), _klucze(wzor) - _klucze(w)  # dane testowe nie maja pol, ktorych silnik nie zwraca
    assert w["gniazda"] and _klucze(wzor["gniazda"][0]) == _klucze(w["gniazda"][0])
    assert _klucze(wzor["gniazda"][0]["kandydaci"][0]) <= _klucze(w["gniazda"][0]["kandydaci"][0])
    z_inspekcja = next(g for g in w["gniazda"] if g["inspekcja"])
    assert _klucze(wzor["gniazda"][0]["inspekcja"]) <= _klucze(z_inspekcja["inspekcja"])
    ze_skala = next(g for g in w["gniazda"] if g["skala"])
    assert _klucze(wzor["gniazda"][0]["skala"]) <= _klucze(ze_skala["skala"])
    assert w["foldery_projektow"] == [str(proj)]  # prawdziwy silnik podaje sciezki folderow puli - do pliku wyniku nie ida (P2)
    s = nowa_sesja(tmp_path)
    try:
        sid = s.przyjmij_wynik({"plik": str(p_stl), "sha16": "abcdef0123456789", "rozmiar": p_stl.stat().st_size, "czas_pliku": f"{DATA}T19:00:00"}, w)
        wiersze = s.baza.wiersze("SELECT * FROM prace WHERE skan_id = ? ORDER BY id", (sid,))
        assert len(wiersze) == len(w["gniazda"]) >= len(prawda.prace) == 3
        assert [(r["gniazdo"], r["status_match"], r["status_gniazda"]) for r in wiersze] == [(g["gniazdo"], g["status"], g["status_gniazda"]) for g in w["gniazda"]]
        sk = skan(s, sid)
        assert (sk["uklad"], sk["uklad_zrodlo"], sk["numer_plytki"], sk["uklad_zgodny"]) == ("okragla_wieczorna", "auto", 8, 1)
        assert sum(s.stan_wieczoru(DATA)["liczniki"].values()) == len(w["gniazda"])
        tresc = s.sciezka_wyniku(sid).read_text(encoding="utf-8")
        assert json.loads(tresc) == zapisany(w) and json.dumps(str(proj))[1:-1] not in tresc and proj.as_posix() not in tresc
    finally:
        s.baza.zamknij()
