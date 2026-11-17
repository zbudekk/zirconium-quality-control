"""session.py - wieczor (E3-A1): przyjecie wyniku skanu, prace, decyzje, ponowny skan, lista "do dofrezowania".

Kryteria odbioru E3-A1 (plan etapu 3, sekcja 4.1) - kazde ma test `test_kN_...`:
 1 trzy wyniki -> 3 skany, prace i statusy 1:1 z plikami wynikow      6 ten sam sha16 w dwoch gniazdach = konflikt
 2 "Ukruszona" x2 + "OK" + cofniecie -> lista i 4 wiersze decyzji     8 nazwy zlecen nie wychodza poza cztery tabele
 3 ponowny skan plytki: poprzedni `zastapiony`, decyzje nie licza sie  9 import decyzje.csv: wiersze 1:1
 4 niezgodny uklad / skan ponownie: status skanu i 0 zielonych        (7 -> test_baza.py, 10 -> test_ustawienia.py)
 5 zamkniecie i otwarcie bazy: identyczny stan

Runda 2 (recenzja PR #16, decyzje wlasciciela z 17.11.2026): testy `test_pN_...` = uwagi P2-P7 recenzenta (P1 w test_baza.py),
`test_dN_...` = uwagi drobne, `test_decyzja2_...` = lista operatorow wymagana; decyzja 3 (kolor po decyzji) = `test_p7_...`,
decyzja 4 (nazwy w czterech tabelach) = `test_k8_...`.

Dane: `testy/dane_sesji` - wyniki w formacie `porownaj.porownaj` zbudowane recznie (male, w pelni sztuczne: projekty to skroty
`sha16` wymyslonych nazw, zlecenia maja fikcyjne nazwy folderow). Zgodnosc formatu z prawdziwym silnikiem pilnuje
`test_wynik_prawdziwego_porownaj_wchodzi_do_bazy` (skan sztucznej plytki z trzema atrapami koron).
"""
from __future__ import annotations

import datetime as dt
import json
import re
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
    assert plik.name == f"do_dofrezowania_{DATA}.csv" and tresc[0] == "kuweta;zeby;krazek;plytka;gniazdo;projekt"
    assert tresc[1:] == [f"3263;14;K-1101;1;2;{SHA['3263', '14']}"]
    # ponowne "Ukruszona" po cofnieciu: praca wraca na liste (piaty wiersz decyzji)
    sesja.ukruszona(p16)
    assert pozycje(sesja.do_dofrezowania(DATA)) == [("3263", "14", "K-1101"), ("0412", "16", "K-1102")] and liczba(sesja, "decyzje") == 5
    assert sesja.do_dofrezowania("2026-11-18") == []  # inny wieczor: pusta lista


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
    assert len(sesja.do_dofrezowania(DATA)) == 2 and sesja.stan_wieczoru(DATA)["do_potwierdzenia"] == []
    s1b = przyjmij(sesja, "wynik_plytka1_ponownie")  # ta sama plytka nr 1, ten sam wieczor
    stan = sesja.stan_wieczoru(DATA)
    assert stan["do_potwierdzenia"] == [{"skan_id": s1b, "poprzedni_id": s1, "numer_plytki": 1}]
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
    assert stan["do_potwierdzenia"] == [] and [s["id"] for s in stan["skany"]] == [s1, s2, s1b]
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


def test_ponowny_skan_tylko_w_tym_samym_wieczorze_i_po_numerze_plytki(sesja, zegar):
    s1 = przyjmij(sesja, "wynik_plytka1")
    zegar.ustaw("2026-11-18T19:05:00")  # nastepny wieczor: ten sam numer plytki to juz inna partia
    jutro = przyjmij(sesja, "wynik_plytka1_ponownie")
    assert sesja.stan_wieczoru(DATA)["do_potwierdzenia"] == [] and sesja.stan_wieczoru("2026-11-18")["do_potwierdzenia"] == []
    with pytest.raises(SE.BladSesji, match="nie ma skanu do zastapienia"):
        sesja.zastap_skan(jutro)
    with pytest.raises(SE.BladSesji, match="z tego samego wieczoru"):
        sesja.zastap_skan(jutro, s1)
    # skan bez numeru (dolki poza polem, numer niepodany): po wskazaniu numeru staje sie kandydatem do zastapienia
    zegar.ustaw(f"{DATA}T19:30:00")
    w = wynik("wynik_plytka1_ponownie")
    w["numer"], w["numer_zrodlo"] = None, "nieznany"
    bez_numeru = sesja.przyjmij_wynik({**ZDARZENIA["wynik_plytka1_ponownie"], "sha16": "0123456789abcdef"}, w)
    assert skan(sesja, bez_numeru)["numer_plytki"] is None and sesja.stan_wieczoru(DATA)["do_potwierdzenia"] == []
    sesja.podaj_numer_plytki(bez_numeru, 1)
    sk = skan(sesja, bez_numeru)
    assert (sk["numer_plytki"], sk["numer_zrodlo"]) == (1, "podany")
    d = sesja.baza.wiersze("SELECT * FROM decyzje")
    assert len(d) == 1 and (d[0]["rodzaj"], d[0]["wartosc"], d[0]["skan_id"], d[0]["praca_id"], d[0]["operator"]) == ("numer_plytki", "1", bez_numeru, None, "Technik A")
    assert sesja.stan_wieczoru(DATA)["do_potwierdzenia"] == [{"skan_id": bez_numeru, "poprzedni_id": s1, "numer_plytki": 1}]
    with pytest.raises(SE.BladSesji, match="numer plytki"):
        sesja.podaj_numer_plytki(bez_numeru, 0)


def test_ten_sam_plik_skanu_przeanalizowany_drugi_raz_jest_kandydatem_do_zastapienia(sesja):
    w = wynik("wynik_plytka3")
    w["numer"], w["numer_zrodlo"] = None, "nieznany"
    a = sesja.przyjmij_wynik(ZDARZENIA["wynik_plytka3"], w)
    b = sesja.przyjmij_wynik(ZDARZENIA["wynik_plytka3"], w)  # ta sama zawartosc pliku (sha16), numer nieznany
    assert sesja.stan_wieczoru(DATA)["do_potwierdzenia"] == [{"skan_id": b, "poprzedni_id": a, "numer_plytki": None}]
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
    w["plytka"] = "poranna"
    inna = sesja.przyjmij_wynik(ZDARZENIA["wynik_plytka1_ponownie"], w)
    assert sesja.stan_wieczoru(DATA)["do_potwierdzenia"] == []
    with pytest.raises(SE.BladSesji, match=r"uklad.*poranna.*wieczorna"):
        sesja.zastap_skan(inna, s1)
    with pytest.raises(SE.BladSesji, match="nie ma skanu do zastapienia"):
        sesja.zastap_skan(inna)
    assert skan(sesja, s1)["status"] == "przyjety"
    # kwadrat i kolo tej samej rodziny (te same stozki i gniazda - rozpoznanie ksztaltu bywa niepewne): dozwolone
    w["plytka"] = "okragla_wieczorna"
    kolo = sesja.przyjmij_wynik({**ZDARZENIA["wynik_plytka1_ponownie"], "sha16": "aaaabbbbccccdddd"}, w)
    assert sesja.stan_wieczoru(DATA)["do_potwierdzenia"] == [{"skan_id": kolo, "poprzedni_id": s1, "numer_plytki": 1}]
    assert sesja.zastap_skan(kolo) == s1 and sesja.do_dofrezowania(DATA) == []
    assert SE.rodzina_ukladu("okragla_poranna_r54") == "poranna_r54" != SE.rodzina_ukladu("poranna")


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
    assert stan["do_potwierdzenia"] == [] and stan["prac"] == 10  # program nie proponuje drugi raz zastapienia, ktore cofnieto
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
    assert sesja.stan_wieczoru(DATA)["do_potwierdzenia"] == [] and skan(sesja, dobry)["status"] == "przyjety"


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


# --- P5: wieczor = chwila przyjecia skanu, doba robocza 04:00 - 04:00 ------------------------------
def test_p5_wieczor_od_chwili_przyjecia_skanu_doba_od_4_do_4(sesja, zegar):
    # (a) plik ze stara data (kopia z zachowana data, ponowna analiza pliku z wczoraj): liczy sie chwila przyjecia
    stary = przyjmij(sesja, "wynik_plytka2", czas_pliku="2026-11-10T08:00:00")
    assert skan(sesja, stary)["czas_pliku"] == "2026-11-10T08:00:00" and skan(sesja, stary)["czas_analizy"].startswith(DATA)
    assert [s["id"] for s in sesja.stan_wieczoru()["skany"]] == [stary] and sesja.stan_wieczoru("2026-11-10")["skany"] == []
    sesja.ukruszona(praca(sesja, stary, 4))
    assert len(sesja.do_dofrezowania()) == 1 and sesja.do_dofrezowania("2026-11-10") == []
    # (b) polnoc: skan o 23:59 i powtorka o 00:05 to ten sam wieczor
    zegar.ustaw(f"{DATA}T23:59:00")
    s1 = przyjmij(sesja, "wynik_plytka1")
    sesja.ukruszona(praca(sesja, s1, 2))
    zegar.ustaw("2026-11-18T00:05:00")
    s1b = przyjmij(sesja, "wynik_plytka1_ponownie")
    assert skan(sesja, s1b)["czas_analizy"].startswith("2026-11-18T00:05")
    stan = sesja.stan_wieczoru()
    assert sesja.wieczor() == DATA == stan["data"] and [s["id"] for s in stan["skany"]] == [stary, s1, s1b]
    assert stan["do_potwierdzenia"] == [{"skan_id": s1b, "poprzedni_id": s1, "numer_plytki": 1}]
    assert sesja.zastap_skan(s1b) == s1
    assert pozycje(sesja.do_dofrezowania()) == [("0412", "16", "K-1102")]
    sesja.ukruszona(praca(sesja, s1b, 2))  # decyzja po polnocy trafia na liste tego samego wieczoru
    assert len(sesja.do_dofrezowania()) == 2 == len(sesja.do_dofrezowania(DATA))
    # (c) od 04:00 liczy sie nowa doba robocza
    zegar.ustaw("2026-11-18T03:59:00")
    assert sesja.wieczor() == DATA
    zegar.ustaw("2026-11-18T04:00:00")
    assert sesja.wieczor() == "2026-11-18" and sesja.stan_wieczoru()["skany"] == [] and sesja.do_dofrezowania() == []
    rano = przyjmij(sesja, "wynik_plytka1")  # ten sam numer plytki, ale juz nastepna doba
    assert sesja.stan_wieczoru()["do_potwierdzenia"] == [] and [s["id"] for s in sesja.stan_wieczoru()["skany"]] == [rano]
    with pytest.raises(SE.BladSesji, match="nie ma skanu do zastapienia"):
        sesja.zastap_skan(rano)
    assert len(sesja.stan_wieczoru(DATA)["skany"]) == 3
    # granica doby jest ustawieniem ([sesja] granica_doby_godz) i jedna regula w kodzie
    assert sesja.granica_doby_godz == 4 and sesja.wieczor("2026-11-18T00:05:00") == DATA
    o_polnocy = SE.Sesja(sesja.baza, operatorzy=OSOBY, granica_doby_godz=0, zegar=Zegar("2026-11-18T00:05:00"))
    assert o_polnocy.wieczor() == "2026-11-18" and o_polnocy.wieczor(dt.datetime(2026, 11, 17, 23, 59)) == DATA
    assert [s["id"] for s in o_polnocy.stan_wieczoru(DATA)["skany"]] == [stary, s1]


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


def test_d3_osierocony_plik_wyniku_nie_zostaje_obok_nowego(sesja, tmp_path):
    """D3: plik wyniku po przerwanym przyjeciu skanu (proces zabity przed zatwierdzeniem) nie dubluje numeru nastepnego skanu."""
    katalog = tmp_path / "dane" / "wyniki"
    katalog.mkdir(parents=True)
    (katalog / "skan000001_skan_przerwany_wynik.json").write_text("{}", encoding="utf-8")
    (katalog / "notatka.txt").write_text("plik spoza programu zostaje", encoding="utf-8")
    sid = przyjmij(sesja, "wynik_plytka1")
    assert sid == 1 and sorted(p.name for p in katalog.iterdir()) == ["notatka.txt", sesja.sciezka_wyniku(sid).name]
    drugi = przyjmij(sesja, "wynik_plytka2")
    assert len(list(katalog.glob("skan*_wynik.json"))) == 2 and sesja.sciezka_wyniku(sid).exists() and sesja.sciezka_wyniku(drugi).exists()


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
           "sesja": {**ust["sesja"], "operatorzy": ["Technik A"], "granica_doby_godz": 6}}
    s = SE.Sesja.z_ustawien(ust)
    try:
        assert s.baza.plik == tmp_path / "b" / "stanowisko.sqlite" and s.operatorzy == ("Technik A",) and s.granica_doby_godz == 6
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
