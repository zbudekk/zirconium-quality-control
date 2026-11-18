"""session.py - pytanie "to ponowny skan tej plytki?" tylko przy tych samych pracach (E3-A1p, 18.11.2026).

Regula (``opisy_modulow/session.md``, "Ponowny skan plytki"): propozycja zastapienia (``do_potwierdzenia`` / ``moze_zastapic``)
tylko, gdy (a) ta sama zawartosc pliku skanu albo (b) ten sam numer plytki, rodzina ukladu, tryb, okno
``[sesja] ponowny_skan_okno_min`` ORAZ udzial prac rozpoznanych nowego skanu (projekt top-1 = ``sha16`` pierwszego kandydata,
bez prac szarych), ktorych projekt jest wsrod prac rozpoznanych poprzedniego skanu, wynosi co najmniej
``[sesja] ponowny_skan_min_wspolnych`` (domyslnie 0.5). Gdy nowy albo poprzedni skan ma mniej niz 3 prace rozpoznane, albo prog
= 0 - regula sprzed E3-A1p (pytanie przy kazdym skanie tej plytki w oknie).

Kryteria paczki E3-A1p (raport ``raporty/E3-A1p_2026-11-18.md``) - kazde ma test ``test_kN_...``:
 1 wieczor 36 plytek, 3 numery, kazda z innym wsadem, skany co 5-15 min -> 0 pytan; stara regula (prog 0) na tych samych
   danych: 33 pytania (liczby wypisuje ``pytest -s``)
 2 10 prawdziwych ponownych skanow (te same prace w innych gniazdach albo przesuniete, 1-2 prace mniej / wiecej) -> 10 z 10
 3 mniej niz 3 prace rozpoznane w nowym albo poprzednim skanie -> pytanie jak dawniej
 4 ``ponowny_skan_min_wspolnych = 0`` -> stara regula
 5 ten sam plik skanu -> pytanie zawsze (takze przy innych pracach i progu 1); okno 60 min obowiazuje jak dawniej
Do tego: kontroler (pytania i konflikty projektu w stanie aplikacji wynikaja z nowej reguly; wariant prawdziwej aplikacji
w ``test_kontroler_api.py::test_e3a1p_*``), granica progu, "liczy sie ostatni skan plytki", zastapienie wprost bez zmian,
walidacja progu (ustawienia: ``test_ustawienia.py``).

Dane sztuczne: wyniki ``kontroler_api.sztuczny_wynik`` (projekt N = skrot ``sha16`` napisu "projekt sztuczny N").
"""
from __future__ import annotations

import datetime as dt
import math
import random
from pathlib import Path

import pytest

from stanowisko import baza as B
from stanowisko import kontroler_api as K
from stanowisko import session as SE
from stanowisko import ustawienia as UST

OSOBY = ["Technik A", "Technik B"]
START = "2026-11-17T16:00:00"
DOBA = "2026-11-17"
SLOTY = tuple(range(1, 20))  # 19 gniazd plytki wieczornej
ZIARNO = 20261118


class Zegar:
    """Zegar sesji ustawiany z testu (kazde wywolanie daje te sama chwile, dopoki test jej nie przesunie)."""

    def __init__(self, start: str = START):
        self.t = dt.datetime.fromisoformat(start)

    def przesun(self, minut: float) -> None:
        self.t += dt.timedelta(minutes=minut)

    def __call__(self) -> dt.datetime:
        return self.t


class Wieczor:
    """Sesja na swiezej bazie i "skaner": ``skan(numer, prace)`` przyjmuje sztuczny wynik plytki ``numer``.

    ``prace``: gniazdo -> numer sztucznego projektu (top-1 kandydat pracy); ``szare``: gniazda, w ktorych match nie rozpoznal
    projektu (praca nieznana - regula ja pomija); ``rodzaje``: gniazdo -> rodzaj pracy z ``kontroler_api.RODZAJE_PRAC``."""

    def __init__(self, katalog: Path, prog: float | None = None, zegar: Zegar | None = None):
        self.katalog = katalog
        self.zegar = zegar or Zegar()
        self.baza = B.otworz(katalog / "dane" / "stanowisko.sqlite")
        kw = {} if prog is None else {"ponowny_skan_min_wspolnych": prog}
        self.sesja = SE.Sesja(self.baza, operatorzy=OSOBY, katalog_wynikow=katalog / "dane" / "wyniki", zegar=self.zegar, **kw)
        self.sesja.wybierz_operatora(OSOBY[0])
        self.nr = 0

    def skan(self, numer, prace: dict, *, szare=(), rodzaje: dict | None = None, uklad: str = "wieczorna", sha16: str | None = None) -> int:
        self.nr += 1
        gniazda = {g: "szary" if g in szare else (rodzaje or {}).get(g, "zielony") for g in prace}
        wynik = K.sztuczny_wynik(uklad, numer, gniazda, projekty=dict(prace), skan=f"skan_{self.nr:03d}.stl")
        zdarzenie = {"plik": f"C:/Skany/skan_{self.nr:03d}.stl", "sha16": sha16 or K.skrot_sztuczny(f"skan E3-A1p {self.nr}"),
                     "rozmiar": 48_000_000 + self.nr, "czas_pliku": self.zegar().isoformat()}
        return self.sesja.przyjmij_wynik(zdarzenie, wynik)

    def propozycje(self, sesja: SE.Sesja | None = None) -> dict:
        """skan_id -> poprzedni_id: propozycje "to ponowny skan?" doby (``sesja`` z innym progiem czyta te sama baze)."""
        return {p["skan_id"]: p["poprzedni_id"] for p in (sesja or self.sesja).stan_wieczoru(DOBA)["do_potwierdzenia"]}

    def podstawa(self, skan_id: int) -> str | None:
        """Pole ``podstawa`` propozycji dla skanu (dlaczego program pyta)."""
        return next((p["podstawa"] for p in self.sesja.stan_wieczoru(DOBA)["do_potwierdzenia"] if p["skan_id"] == skan_id), None)

    def z_progiem(self, prog: float) -> SE.Sesja:
        """Druga sesja na tej samej bazie z innym progiem: te same skany ocenione inna regula (odczyt stanu niczego nie zmienia)."""
        return SE.Sesja(self.baza, operatorzy=OSOBY, zegar=self.zegar, ponowny_skan_min_wspolnych=prog)

    def status(self, skan_id: int) -> str:
        return self.baza.wiersz("SELECT status FROM skany WHERE id = ?", (skan_id,))["status"]


@pytest.fixture
def wieczor(tmp_path):
    w = Wieczor(tmp_path)
    yield w
    w.baza.zamknij()


def praca_po_pracy(od: int, sloty) -> dict:
    """Gniazda ``sloty`` z kolejnymi projektami od ``od`` (kazda praca inny projekt)."""
    return {g: od + i for i, g in enumerate(sloty)}


# --- kryterium 1: wieczor 36 plytek krazacych z nowym wsadem ---------------------------------------------------------
def wieczor_36(los: random.Random) -> list[dict]:
    """36 plytek krazacych (numery 1, 2, 3 po kolei), kazda z nowym wsadem: 8-19 prac w losowych gniazdach, projekty
    niepowtarzalne, do 2 prac bez rozpoznania (szare), czesc czerwonych i zoltych; odstep miedzy skanami 5-15 min."""
    plan, projekt = [], 100
    for i in range(36):
        sloty = sorted(los.sample(SLOTY, los.randint(8, 19)))
        prace = {}
        for g in sloty:
            projekt += 1
            prace[g] = projekt
        szare = set(los.sample(sloty, los.randint(0, 2)))
        rodzaje = {g: los.choice(("zielony",) * 6 + ("czerwony", "zolty")) for g in sloty}
        plan.append({"numer": i % 3 + 1, "prace": prace, "szare": szare, "rodzaje": rodzaje, "odstep": 0 if i == 0 else los.randint(5, 15)})
    return plan


def przyjmij_plan(w: Wieczor, plan: list[dict]) -> list[int]:
    skany = []
    for x in plan:
        w.zegar.przesun(x["odstep"])
        skany.append(w.skan(x["numer"], x["prace"], szare=x["szare"], rodzaje=x["rodzaje"]))
    return skany


def pytania_starej_reguly(plan: list[dict], okno_min: int = SE.PONOWNY_SKAN_OKNO_MIN) -> int:
    """Ile razy zapytalaby regula sprzed E3-A1p: poprzedni skan plytki o tym numerze przyjety najwyzej ``okno_min`` wczesniej."""
    t, ostatni, n = 0, {}, 0
    for x in plan:
        t += x["odstep"]
        if x["numer"] in ostatni and t - ostatni[x["numer"]] <= okno_min:
            n += 1
        ostatni[x["numer"]] = t
    return n


def test_k1_wieczor_36_plytek_z_nowym_wsadem_bez_pytan(wieczor):
    """Kryterium 1: 36 plytek, 3 numery, nowy wsad co 5-15 min - zadnego pytania (stara regula na tych samych danych: 33)."""
    plan = wieczor_36(random.Random(ZIARNO))
    skany = przyjmij_plan(wieczor, plan)
    nowa = wieczor.propozycje()
    stara = wieczor.propozycje(wieczor.z_progiem(0))
    print(f"\n[E3-A1p kryterium 1] 36 plytek, 3 numery, nowy wsad co 5-15 min: pytan {len(nowa)} (nowa regula, prog "
          f"{SE.PONOWNY_SKAN_MIN_WSPOLNYCH}), {len(stara)} (stara regula, prog 0)")
    assert len(nowa) == 0
    assert len(stara) == pytania_starej_reguly(plan) == 33  # odstep 3 skanow 15-45 min < 60: pytanie przy kazdej plytce poza pierwszymi trzema
    stan = wieczor.sesja.stan_wieczoru(DOBA)
    assert len(stan["skany"]) == 36 and all(s["moze_zastapic"] is None and s["aktywny"] for s in stan["skany"])
    assert stan["konflikty"] == [] and wieczor.baza.wiersz("SELECT count(*) AS n FROM zdarzenia WHERE typ = 'konflikt_projektu'")["n"] == 0
    for skan_id in skany[3:]:  # bez propozycji nie ma tez zastapienia "na potwierdzenie"
        with pytest.raises(SE.BladSesji, match="nie ma skanu do zastapienia"):
            wieczor.sesja.zastap_skan(skan_id)
    assert {wieczor.status(s) for s in skany} == {SE.STATUS_PRZYJETY}


def test_k1_dziesiec_losowych_wieczorow_bez_pytan(tmp_path):
    """Kryterium 1 na 10 innych losowaniach (inne liczby prac, gniazda, szare i odstepy): zawsze 0 pytan, stara regula 33."""
    wyniki = []
    for nr in range(10):
        w = Wieczor(tmp_path / f"w{nr}")
        try:
            plan = wieczor_36(random.Random(ZIARNO + 1 + nr))
            przyjmij_plan(w, plan)
            wyniki.append((len(w.propozycje()), len(w.propozycje(w.z_progiem(0))), pytania_starej_reguly(plan)))
        finally:
            w.baza.zamknij()
    print(f"\n[E3-A1p kryterium 1, 10 wieczorow] pytan nowa / stara regula: {[(a, b) for a, b, _ in wyniki]}")
    assert all(nowa == 0 and stara == oczekiwane == 33 for nowa, stara, oczekiwane in wyniki)


# --- kryterium 2: prawdziwe ponowne skany --------------------------------------------------------------------------------
def ponowne_skany(los: random.Random) -> list[dict]:
    """10 par (pierwszy skan, ponowny skan tej samej plytki z tym samym wsadem) - kazda na innym numerze plytki."""
    pary = []

    def para(opis: str, pierwszy: dict, ponowny: dict, **kw) -> None:
        pary.append({"opis": opis, "pierwszy": pierwszy, "ponowny": ponowny, **kw})

    baza = 1000
    p = praca_po_pracy(baza, SLOTY)
    para("te same prace, te same gniazda", p, dict(p))
    baza += 100
    p = praca_po_pracy(baza, SLOTY)
    projekty = list(p.values())
    los.shuffle(projekty)
    para("te same prace, inne gniazda (przemieszane)", p, dict(zip(SLOTY, projekty)))
    baza += 100
    p = praca_po_pracy(baza, range(1, 19))
    para("przesuniecie o jedno gniazdo", p, {g + 1: pr for g, pr in p.items()})
    baza += 100
    p = praca_po_pracy(baza, SLOTY)
    bez = los.choice(SLOTY)
    para("jedna praca mniej", p, {g: pr for g, pr in p.items() if g != bez})
    baza += 100
    p = praca_po_pracy(baza, SLOTY)
    bez = set(los.sample(SLOTY, 2))
    para("dwie prace mniej", p, {g: pr for g, pr in p.items() if g not in bez})
    baza += 100
    p = praca_po_pracy(baza, range(1, 18))
    para("jedna praca wiecej", p, {**p, 18: baza + 50})
    baza += 100
    p = praca_po_pracy(baza, range(1, 16))
    para("dwie prace wiecej", p, {**p, 16: baza + 50, 17: baza + 51})
    baza += 100
    p = praca_po_pracy(baza, SLOTY)
    zmieniona = los.choice(SLOTY)
    para("jedna praca mniej, jedna wiecej", p, {**p, zmieniona: baza + 50})
    baza += 100
    p = praca_po_pracy(baza, SLOTY)
    para("te same prace, dwie teraz bez rozpoznania (szare)", p, dict(p), szare_ponowny=set(los.sample(SLOTY, 2)))
    baza += 100
    p = praca_po_pracy(baza, range(1, 7))
    ponowny = {g + 2: pr for g, pr in p.items()}
    ponowny[5] = baza + 50  # jedna praca z innym projektem top-1 (pomylka match)
    para("mala plytka (6 prac): kolo zamiast kwadratu, przesuniecie o 2 gniazda, jedna praca z innym projektem", p, ponowny,
         uklad_ponowny="okragla_wieczorna")
    return pary


def test_k2_dziesiec_prawdziwych_ponownych_skanow_daje_10_pytan(wieczor):
    """Kryterium 2: 10 ponownych skanow tego samego wsadu (5-20 min pozniej, miedzy nimi plytki z nowym wsadem) -> 10 z 10."""
    los = random.Random(ZIARNO)
    pary = ponowne_skany(los)
    oczekiwane, inne, udzialy = {}, [], []
    for i, x in enumerate(pary):
        numer = i + 1
        pierwszy = wieczor.skan(numer, x["pierwszy"])
        for j in range(los.randint(1, 2)):  # w tym czasie inne plytki (inne numery) z nowym wsadem
            wieczor.zegar.przesun(los.randint(2, 6))
            inne.append(wieczor.skan(40 + 2 * i + j, praca_po_pracy(5000 + 100 * (2 * i + j), range(1, los.randint(8, 19)))))
        wieczor.zegar.przesun(los.randint(3, 8))
        ponowny = wieczor.skan(numer, x["ponowny"], szare=x.get("szare_ponowny", ()), uklad=x.get("uklad_ponowny", "wieczorna"))
        oczekiwane[ponowny] = pierwszy
        z = wieczor.sesja.zgodnosc_prac(ponowny, pierwszy)
        udzialy.append(f"{x['opis']}: {z['wspolne']}/{z['rozpoznane']} = {z['udzial']:.2f}")
        wieczor.zegar.przesun(los.randint(1, 4))
    propozycje = wieczor.propozycje()
    trafione = sum(1 for k, v in oczekiwane.items() if propozycje.get(k) == v)
    print(f"\n[E3-A1p kryterium 2] ponowne skany z pytaniem: {trafione} z {len(oczekiwane)}\n  " + "\n  ".join(udzialy))
    assert trafione == len(oczekiwane) == 10
    assert propozycje == oczekiwane  # plytki z nowym wsadem (inne numery) bez pytan
    assert {wieczor.podstawa(k) for k in oczekiwane} == {"te_same_prace"}
    for ponowny, pierwszy in oczekiwane.items():  # potwierdzenie "Tak, to ponowny skan" dziala jak dawniej
        assert wieczor.sesja.zastap_skan(ponowny) == pierwszy and wieczor.status(pierwszy) == SE.STATUS_ZASTAPIONY
    assert wieczor.propozycje() == {} and wieczor.sesja.stan_wieczoru(DOBA)["konflikty"] == []


# --- kryterium 3: za malo prac rozpoznanych --------------------------------------------------------------------------
def test_k3_mniej_niz_3_prace_rozpoznane_pytanie_jak_dawniej(wieczor):
    w = wieczor
    a = w.skan(1, praca_po_pracy(100, SLOTY))
    w.zegar.przesun(10)
    b = w.skan(1, praca_po_pracy(200, range(1, 6)), szare={3, 4, 5})  # nowy skan: 2 prace rozpoznane (inne projekty)
    assert w.propozycje() == {b: a} and w.podstawa(b) == "za_malo_rozpoznanych"
    assert w.sesja.zgodnosc_prac(b, a) == {"rozpoznane": 2, "rozpoznane_poprzedniego": 19, "wspolne": 0, "udzial": 0.0}
    c = w.skan(2, {1: 301, 2: 302, 7: 307, 9: 309}, szare={7, 9})  # poprzedni skan: 2 prace rozpoznane
    w.zegar.przesun(10)
    d = w.skan(2, praca_po_pracy(400, SLOTY))
    assert w.propozycje()[d] == c and w.podstawa(d) == "za_malo_rozpoznanych"
    e = w.skan(3, praca_po_pracy(500, range(1, 6)), szare={1, 2, 3, 4, 5})  # zadna praca rozpoznana (np. pusta pula)
    w.zegar.przesun(5)
    f = w.skan(3, praca_po_pracy(600, range(1, 6)), szare={1, 2, 3, 4, 5})
    assert w.propozycje()[f] == e and w.sesja.zgodnosc_prac(f, e)["udzial"] is None
    # po 3 prace rozpoznane w obu skanach to juz podstawa do oceny: inne projekty = nowy wsad, bez pytania
    g = w.skan(4, {1: 701, 2: 702, 3: 703, 4: 704}, szare={4})
    w.zegar.przesun(10)
    h = w.skan(4, {1: 801, 2: 802, 3: 803})
    assert h not in w.propozycje()
    w.zegar.przesun(5)
    i = w.skan(4, {4: 801, 5: 802, 6: 899})  # 2 z 3 jak w poprzednim skanie (0.67 >= 0.5): pytanie
    assert w.propozycje() == {b: a, d: c, f: e, i: h} and w.podstawa(i) == "te_same_prace"
    assert g not in w.propozycje().values()


# --- kryterium 4: prog 0 = stara regula --------------------------------------------------------------------------------
def test_k4_prog_0_to_stara_regula(tmp_path):
    w = Wieczor(tmp_path, prog=0)
    try:
        a = w.skan(1, praca_po_pracy(100, SLOTY))
        w.zegar.przesun(15)
        b = w.skan(1, praca_po_pracy(200, SLOTY))  # nowy wsad: stara regula pyta
        assert w.propozycje() == {b: a} and w.podstawa(b) == "regula_wylaczona"
        assert w.propozycje(w.z_progiem(SE.PONOWNY_SKAN_MIN_WSPOLNYCH)) == {}  # te same skany przy progu domyslnym: bez pytania
        w.zegar.przesun(61)
        c = w.skan(1, praca_po_pracy(200, SLOTY))  # po oknie 60 min bez propozycji - jak dawniej, takze przy tych samych pracach
        assert c not in w.propozycje()
        # prog z pliku ustawien: [sesja] ponowny_skan_min_wspolnych = 0
        ust = UST.wczytaj_ustawienia(UST.PLIK_PRZYKLADU)
        assert ust["sesja"]["ponowny_skan_min_wspolnych"] == SE.PONOWNY_SKAN_MIN_WSPOLNYCH == 0.5
        ust["sesja"]["ponowny_skan_min_wspolnych"] = 0
        ust["sciezki"]["wyniki"] = (tmp_path / "wyniki_ustawien").as_posix()
        s = SE.Sesja.z_ustawien(ust, w.baza, zegar=w.zegar)
        assert s.ponowny_skan_min_wspolnych == 0 and w.propozycje(s) == {b: a}
        ust["sesja"]["ponowny_skan_min_wspolnych"] = 0.5
        assert w.propozycje(SE.Sesja.z_ustawien(ust, w.baza, zegar=w.zegar)) == {}
        del ust["sesja"]["ponowny_skan_min_wspolnych"]  # slownik ustawien bez klucza (np. zbudowany recznie): wartosc domyslna
        assert SE.Sesja.z_ustawien(ust, w.baza, zegar=w.zegar).ponowny_skan_min_wspolnych == 0.5
    finally:
        w.baza.zamknij()


# --- kryterium 5: ten sam plik skanu -------------------------------------------------------------------------------------
def test_k5_ten_sam_plik_skanu_pytanie_zawsze(tmp_path):
    w = Wieczor(tmp_path, prog=1.0)
    try:
        a = w.skan(1, praca_po_pracy(100, SLOTY), sha16="5" * 16)
        w.zegar.przesun(10)
        b = w.skan(1, praca_po_pracy(200, SLOTY), sha16="5" * 16)  # ta sama tresc pliku, inne prace (np. analiza po zmianie indeksu)
        assert w.propozycje() == {b: a} and w.podstawa(b) == "ten_sam_plik"
        c = w.skan(None, praca_po_pracy(300, range(1, 4)), sha16="6" * 16)  # bez numeru plytki
        w.zegar.przesun(5)
        d = w.skan(None, praca_po_pracy(400, range(1, 4)), sha16="6" * 16, szare={1, 2})
        assert w.propozycje() == {b: a, d: c} and w.podstawa(d) == "ten_sam_plik"
        for prog in (0, 0.5, 1):
            assert w.propozycje(w.z_progiem(prog)) == {b: a, d: c}, prog
        # okno obowiazuje jak dawniej: ten sam plik przyjety ponad 60 min pozniej - bez propozycji (zastapienie wprost dziala)
        w.zegar.przesun(61)
        e = w.skan(None, praca_po_pracy(400, range(1, 4)), sha16="6" * 16)
        assert e not in w.propozycje()
        assert w.sesja.zastap_skan(e, d) == d
    finally:
        w.baza.zamknij()


# --- granica progu, ostatni skan plytki, zastapienie wprost ----------------------------------------------------------------
def test_granica_progu_i_prace_szare_poprzedniego_skanu(tmp_path):
    w = Wieczor(tmp_path)  # prog domyslny 0.5
    try:
        a = w.skan(1, praca_po_pracy(100, range(1, 11)))
        w.zegar.przesun(10)
        b = w.skan(1, {**praca_po_pracy(100, range(1, 6)), **praca_po_pracy(200, range(6, 11))})  # 5 z 10 = 0.5: pytanie
        assert w.sesja.zgodnosc_prac(b, a) == {"rozpoznane": 10, "rozpoznane_poprzedniego": 10, "wspolne": 5, "udzial": 0.5}
        c = w.skan(2, praca_po_pracy(300, range(1, 10)))
        w.zegar.przesun(10)
        d = w.skan(2, {**praca_po_pracy(300, range(1, 5)), **praca_po_pracy(400, range(5, 10))})  # 4 z 9 = 0.44: nowy wsad
        e = w.skan(3, praca_po_pracy(500, range(1, 11)), szare={1, 2, 3, 4, 5, 6})  # 4 rozpoznane (projekty 506-509)
        w.zegar.przesun(5)
        f = w.skan(3, praca_po_pracy(500, range(1, 11)))  # te same prace, ale 6 z nich w poprzednim skanie bylo szarych: 4 z 10
        assert w.propozycje() == {b: a} and d not in w.propozycje() and f not in w.propozycje()
        assert w.sesja.zgodnosc_prac(f, e) == {"rozpoznane": 10, "rozpoznane_poprzedniego": 4, "wspolne": 4, "udzial": 0.4}
        assert c not in w.propozycje().values()
        jeden = w.z_progiem(1)  # prog 1: tylko gdy kazda praca rozpoznana nowego skanu jest w poprzednim
        assert w.propozycje(jeden) == {}
        g = w.skan(4, praca_po_pracy(600, SLOTY))
        w.zegar.przesun(5)
        h = w.skan(4, praca_po_pracy(600, range(1, 18)))  # 2 prace mniej: 17 z 17
        w.zegar.przesun(5)
        i = w.skan(4, {**praca_po_pracy(600, range(1, 18)), 18: 699})  # jedna praca wiecej: 17 z 18
        assert w.propozycje(jeden) == {h: g}
        assert w.propozycje() == {b: a, h: g, i: h}
    finally:
        w.baza.zamknij()


def test_liczy_sie_ostatni_skan_plytki(wieczor):
    """Ostatni skan plytki z nowym wsadem zamyka sprawe: wczesniejszy skan z tymi samymi pracami to starszy wsad (bez pytania);
    zastapienie wprost w tej samej dobie nadal dziala."""
    w = wieczor
    a = w.skan(1, praca_po_pracy(100, SLOTY))
    w.zegar.przesun(15)
    b = w.skan(1, praca_po_pracy(200, SLOTY))
    w.zegar.przesun(10)
    c = w.skan(1, praca_po_pracy(100, SLOTY))
    assert w.propozycje() == {}
    assert w.sesja.zastap_skan(c, a) == a


def test_zastapienie_wprost_i_cofniecie_bez_zmian_dla_nowego_wsadu(wieczor):
    w = wieczor
    a = w.skan(1, praca_po_pracy(100, SLOTY))
    w.sesja.ukruszona(w.baza.wiersz("SELECT id FROM prace WHERE skan_id = ? AND gniazdo = 2", (a,))["id"])
    w.zegar.przesun(15)
    b = w.skan(1, praca_po_pracy(200, SLOTY))
    assert w.propozycje() == {}
    with pytest.raises(SE.BladSesji, match=r"nie ma skanu do zastapienia.*60 min.*z tymi samymi pracami"):
        w.sesja.zastap_skan(b)
    assert w.status(a) == SE.STATUS_PRZYJETY and len(w.sesja.do_dofrezowania()) == 1
    assert w.sesja.zastap_skan(b, a) == a and w.status(a) == SE.STATUS_ZASTAPIONY and w.sesja.do_dofrezowania() == []
    w.sesja.cofnij_zastapienie(b)
    assert w.status(a) == SE.STATUS_PRZYJETY and len(w.sesja.do_dofrezowania()) == 1 and w.propozycje() == {}


@pytest.mark.parametrize("prog", [-0.1, 1.01, 2, True, "0.5", None, math.nan, math.inf])
def test_prog_spoza_zakresu_to_blad_sesji(tmp_path, prog):
    b = B.otworz(tmp_path / "stanowisko.sqlite")
    try:
        with pytest.raises(SE.BladSesji, match="ponownego skanu"):
            SE.Sesja(b, operatorzy=OSOBY, ponowny_skan_min_wspolnych=prog)
    finally:
        b.zamknij()


@pytest.mark.parametrize("prog", [0, 0.0, 0.25, 0.5, 1, 1.0])
def test_prog_w_zakresie(tmp_path, prog):
    b = B.otworz(tmp_path / "stanowisko.sqlite")
    try:
        assert SE.Sesja(b, operatorzy=OSOBY, ponowny_skan_min_wspolnych=prog).ponowny_skan_min_wspolnych == prog
    finally:
        b.zamknij()


# --- kontroler: pytania i konflikty w stanie aplikacji -------------------------------------------------------------------
def test_kontroler_36_plytek_bez_pytan_i_konfliktow_a_ponowny_skan_z_pytaniem(tmp_path):
    """Stan aplikacji (``KontrolerSesji`` na atrapie, prawdziwa ``Sesja``): wieczor kryterium 1 nie daje zadnego pytania
    "Ponowny skan tej samej plytki?", zadnego konfliktu "Ten sam projekt w dwoch gniazdach" i zadnych przyciskow
    potwierdzenia; prawdziwy ponowny skan ostatniej plytki - jedno pytanie, po potwierdzeniu bez konfliktow."""
    zegar = Zegar()
    k = K.AtrapaKontrolera(tmp_path / "atrapa", operatorzy=tuple(OSOBY), zegar=zegar)
    try:
        assert k.wybierz_operatora(OSOBY[0])
        plan = wieczor_36(random.Random(ZIARNO))
        skany = []
        for x in plan:
            zegar.przesun(x["odstep"])
            gniazda = {g: "szary" if g in x["szare"] else x["rodzaje"][g] for g in x["prace"]}
            skany.append(k.symuluj_skan("zwykla", numer=x["numer"], gniazda=gniazda, projekty=x["prace"]))
        s = k.stan()
        assert len(s.plytki) == 36
        assert [q.rodzaj for q in s.pytania if q.rodzaj == "ponowny_skan"] == []
        assert all(q.rodzaj != "ponowny_skan" for p in s.plytki for q in p.pytania)
        assert s.konflikty == () and [x.rodzaj for x in s.komunikaty if x.rodzaj == "konflikt_projektu"] == []
        assert all(p.moze_zastapic is None and "potwierdz_ponowny_skan" not in p.dozwolone for p in s.plytki)
        stara = SE.Sesja(k.sesja.baza, operatorzy=OSOBY, zegar=zegar, ponowny_skan_min_wspolnych=0).stan_wieczoru()["do_potwierdzenia"]
        print(f"\n[E3-A1p kontroler] 36 plytek z nowym wsadem: pytan o ponowny skan {len(s.pytania)}, konfliktow {len(s.konflikty)}; "
              f"stara regula na tej samej bazie: {len(stara)} propozycji")
        assert len(stara) == 33
        # prawdziwy ponowny skan ostatniej plytki: te same prace w odwrotnej kolejnosci gniazd
        ostatni = plan[-1]
        sloty = sorted(ostatni["prace"])
        projekty = dict(zip(sloty, [ostatni["prace"][g] for g in reversed(sloty)]))
        zegar.przesun(6)
        ponowny = k.symuluj_skan("zwykla", numer=ostatni["numer"], gniazda={g: "zielony" for g in sloty}, projekty=projekty)
        s = k.stan()
        assert [(q.rodzaj, q.skan_id, q.poprzedni_id) for q in s.pytania] == [("ponowny_skan", ponowny, skany[-1])]
        assert s.plytka(ponowny).moze_zastapic == skany[-1] and "potwierdz_ponowny_skan" in s.plytka(ponowny).dozwolone
        assert s.konflikty  # do potwierdzenia te same projekty leza na dwoch aktywnych skanach (stan podaje je jak dawniej) ...
        assert [x.rodzaj for x in s.komunikaty if x.rodzaj == "konflikt_projektu"] == []  # ... ale nie na pasku bledow (runda 2)
        assert k.potwierdz_ponowny_skan(ponowny)
        s = k.stan()
        assert s.pytania == () and s.konflikty == () and s.plytka(skany[-1]).status == SE.STATUS_ZASTAPIONY
    finally:
        k.zamknij()
