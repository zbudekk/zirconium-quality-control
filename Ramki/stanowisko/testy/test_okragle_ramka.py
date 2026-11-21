"""Plytki okragle ramkowe n1-n6 na ramkach swietlnych - paczka E3-O2 (21.11.2026), czesc "kalibracja i plan".

Uklady ``okragla_ramkowa_wieczorna`` (n1-n3) i ``okragla_ramkowa_poranna`` (n4-n6) maja te same gniazda i srodek co
kwadrat R59 (R58), wiec kalibracja startowa diod = geometria ich ``uklad.json`` (``zrodlo`` = "geometria") i bloki pikseli
sa rowne blokom kwadratu. Przed E3-O2 kalibracja znala tylko kwadraty: wynik plytki okraglej wieczorem dawal
``brak_kalibracji``, a plan poranny pomijal cala plytke.

Kryteria zlecenia E3-O2: (2) rano 3 plytki n4-n6 w planie ramki, 24 z 24 gniazd z blokiem pikseli, bloki = bloki
kwadratu ``poranna`` (72 z 72); wieczorem n1-n3 wobec kwadratu ``wieczorna`` (19 gniazd; 57 z 57); (3) plytka okragla
testowa n8 / n9 jak dotad; (6) stary plik kalibracji (tylko kwadraty, takze z wpisami ``zrodlo`` = "kalibracja") po
starcie ma 2 nowe uklady, wpisy skalibrowane bajtowo bez zmian; ``python -m ramka.test_led --uklad
okragla_ramkowa_wieczorna`` na atrapie dziala. Komunikaty dla technika (kryterium 4) - sekcja "kontroler" na koncu pliku.

Atrapa ramki dziala w procesie testu (``narzedzia/atrapa_ramki.uruchom_atrape`` przez pomocnikow ``test_indicate``):
obraz ramki jest sprawdzany piksel po pikselu. Dane w pelni sztuczne; testy pisza tylko do ``tmp_path``.
"""
from __future__ import annotations

import copy
import datetime as dt
import hashlib
import json
import re
import time

import pytest

import test_indicate as TI
import test_session_rano as TSR
from ramka import kalibracja, test_led
from stanowisko import indicate as IND
from stanowisko import ramka_protokol as RP

MODELE = TI.MODELE
STANOWISKO = TI.MODELE.parent
RAMKOWA_W = "okragla_ramkowa_wieczorna"
RAMKOWA_P = "okragla_ramkowa_poranna"
# uklad ramkowy -> (rola ramki, kwadrat R59 o tych samych gniazdach, numery plytek, liczba gniazd)
RAMKOWE = {RAMKOWA_W: ("W", "wieczorna", (1, 2, 3), 19), RAMKOWA_P: ("P", "poranna", (4, 5, 6), 24)}


@pytest.fixture(scope="module")
def kal():
    return kalibracja.domyslna(MODELE)


@pytest.fixture
def sprzataj():
    lista = []
    yield lista
    for f in reversed(lista):
        try:
            f()
        except Exception:  # noqa: BLE001 - sprzatanie po tescie
            pass


def stara_kalibracja() -> dict:
    """Plik kalibracji sprzed E3-O2: tylko uklady kwadratowe; ``wieczorna`` i ``poranna`` SKALIBROWANE na ramce (bloki
    przesuniete wzgledem geometrii, ``zrodlo`` = "kalibracja"), uklady ``_r54`` z geometrii."""
    dane = kalibracja.domyslna(MODELE)
    for rola in ("W", "P"):
        for nazwa in list(dane["ramki"][rola]):
            if nazwa.startswith("okragla"):
                del dane["ramki"][rola][nazwa]
    for rola, nazwa in (("W", "wieczorna"), ("P", "poranna")):
        wpis = dane["ramki"][rola][nazwa]
        wpis["zrodlo"] = "kalibracja"
        wpis["gniazda"] = {gid: [x + 1, y, w, h] for gid, (x, y, w, h) in wpis["gniazda"].items()}  # przesuniecie o 1 piksel
    return kalibracja.sprawdz(dane)


# --- kalibracja startowa z geometrii (umowa; kryterium 2 - bloki) -----------------------------------------------------------
def test_kalibracja_startowa_ma_uklady_ramkowe_z_geometrii_i_bloki_kwadratu():
    przed = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in MODELE.glob("*/uklad.json")}
    kal_ = kalibracja.domyslna(MODELE)
    assert przed == {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in MODELE.glob("*/uklad.json")}  # modele tylko czytane
    kalibracja.sprawdz(kal_)
    rowne = 0
    for nazwa, (rola, kwadrat, _, gniazd) in RAMKOWE.items():
        wpis = kal_["ramki"][rola][nazwa]
        assert wpis["zrodlo"] == "geometria" and len(wpis["gniazda"]) == gniazd
        assert sorted(wpis["gniazda"], key=int) == sorted(kal_["ramki"][rola][kwadrat]["gniazda"], key=int)
        for gid, blok in wpis["gniazda"].items():
            assert blok == kal_["ramki"][rola][kwadrat]["gniazda"][gid], (nazwa, gid)
            rowne += 1
        druga = "P" if rola == "W" else "W"
        assert nazwa not in kal_["ramki"][druga]  # uklad wieczorny tylko na ramce W, poranny tylko na P
    assert rowne == 19 + 24
    # kryterium 3: plytki okragle testowe n8 / n9 nadal bez kalibracji (nie leza na ramce)
    wszystkie = set(kal_["ramki"]["W"]) | set(kal_["ramki"]["P"])
    assert wszystkie == {"wieczorna", "wieczorna_r54", "poranna", "poranna_r54", RAMKOWA_W, RAMKOWA_P}
    assert not wszystkie & {"okragla_wieczorna", "okragla_poranna", "okragla_wieczorna_r54", "okragla_poranna_r54"}


# --- kryterium 2: plan ramki porannej i wieczornej -----------------------------------------------------------------------------
def _piec_z_pelnymi_plytkami(katalog, uklad: str):
    """Sesja poranna z 3 plytkami n4-n6 ukladu ``uklad``; w kazdym z 24 gniazd praca (bez kandydata = "nieznana", biala)."""
    st = TSR.Stanowisko(katalog)
    TSR.wypelnij_indeks(st.sesja.baza)
    for n in (4, 5, 6):
        spec = TSR.rano(n, f"2026-11-18T07:{10 + n}:00", [{"g": g, "k": []} for g in range(1, 25)], uklad)
        st.skan({**spec, "klucz": f"{uklad}_{n}"})
    return st


def test_k2_rano_trzy_plytki_n4_n6_w_planie_24_z_24_gniazd_bloki_rowne_kwadratowi(kal, tmp_path):
    plany = {}
    for uklad in (RAMKOWA_P, "poranna"):
        st = _piec_z_pelnymi_plytkami(tmp_path / uklad, uklad)
        try:
            pp = st.rano.plan_plytek()
        finally:
            st.sesja.baza.zamknij()
        assert sorted(pp["plytki"]) == ["4", "5", "6"] and pp["uklady"] == {str(n): uklad for n in (4, 5, 6)}
        plan, pominiete = RP.plan_rano(pp, kal, wersja=1, start_id="a1b2c3d4", zdarzenia_do=0)
        assert pominiete["brak_kalibracji"] == [] and pominiete["zla_plytka"] == [] and pominiete["zle_gniazdo"] == 0
        plany[uklad] = plan
    okragly, kwadrat = plany[RAMKOWA_P], plany["poranna"]
    assert sorted(okragly["plytki"]) == ["4", "5", "6"]
    z_blokiem = rowne = 0
    for n in ("4", "5", "6"):
        gn_o = {g["id"]: g for g in okragly["plytki"][n]["gniazda"]}
        gn_k = {g["id"]: g for g in kwadrat["plytki"][n]["gniazda"]}
        assert sorted(gn_o) == list(range(1, 25))
        for gid in range(1, 25):
            px = gn_o[gid]["px"]
            assert isinstance(px, list) and len(px) == 4 and gn_o[gid]["kolor"] is not None
            z_blokiem += 1
            assert px == gn_k[gid]["px"] == kal["ramki"]["P"]["poranna"]["gniazda"][str(gid)], (n, gid)
            rowne += 1
    print(f"\n[E3-O2 kryterium 2] rano: plytek w planie {len(okragly['plytki'])} z 3; gniazd z blokiem pikseli {z_blokiem} z 72 "
          f"(24 z 24 na plytke); bloki rowne blokom kwadratu poranna: {rowne} z 72")
    assert (z_blokiem, rowne) == (72, 72)


def test_k2_wieczor_n1_n3_19_z_19_gniazd_bloki_rowne_kwadratowi(kal):
    z_blokiem = rowne = 0
    for n in (1, 2, 3):
        plany = {}
        for uklad in (RAMKOWA_W, "wieczorna"):
            kolory = {g: "zielony" for g in range(1, 20)}
            plan, pominiete = RP.plan_wieczor({n: (uklad, kolory)}, kal, plan_id="2026-11-17-w-abc123", wersja=1, start_id="a1b2c3d4",
                                              zdarzenia_do=0)
            assert pominiete["brak_kalibracji"] == [] and pominiete["zla_plytka"] == [], uklad
            plany[uklad] = {g["id"]: g["px"] for g in plan["plytki"][str(n)]["gniazda"]}
        assert sorted(plany[RAMKOWA_W]) == list(range(1, 20))
        for gid in range(1, 20):
            z_blokiem += 1
            assert plany[RAMKOWA_W][gid] == plany["wieczorna"][gid], (n, gid)
            rowne += 1
    print(f"\n[E3-O2 kryterium 2] wieczor: gniazd z blokiem pikseli {z_blokiem} z 57 (19 z 19 na plytke n1-n3); bloki rowne blokom "
          f"kwadratu wieczorna: {rowne} z 57")
    assert (z_blokiem, rowne) == (57, 57)


def test_k2_wynik_plytki_ramkowej_swieci_na_ramce_w_piksel_po_pikselu(kal, sprzataj):
    """``KlientRamki.wynik(2, "okragla_ramkowa_wieczorna", ...)``: przed E3-O2 "brak_kalibracji" i ramka ciemna; teraz
    "wyslany", a obraz na atrapie ramki = te same piksele co dla kwadratu ``wieczorna`` z tymi samymi kolorami."""
    program, atrapa, port, k, d = TI._wieczor(kal, sprzataj)
    kolory = TI.kolory_wieczor(kal, "wieczorna")
    z = k.skanowanie()
    k.analiza()
    assert k.wynik(2, RAMKOWA_W, kolory, z) == "wyslany"
    assert TI.czekaj_na(lambda: program.logika.plan is not None and sorted(program.logika.plan.plytki) == [2], 5.0)
    atrapa.poloz_plytke(2)
    oczekiwane = TI.piksele(kal, "W", "wieczorna", TI.swiecace(kolory))
    assert len(oczekiwane) > 50 and TI.czekaj_klatka(lambda: atrapa.klatka, oczekiwane) == []
    # kryterium 3: okragla testowa nadal nie swieci (bez kalibracji), numer spoza ramki W nadal "zla_plytka"
    z2 = k.skanowanie()
    assert k.wynik(3, "okragla_wieczorna", {1: "zielony"}, z2) == "brak_kalibracji"
    assert k.wynik(5, RAMKOWA_P, {2: "zielony"}, z2) == "zla_plytka"
    assert k.wynik(2, RAMKOWA_P, {2: "zielony"}, z2) == "brak_kalibracji"  # uklad poranny nie ma kalibracji na ramce W


def test_k2_plan_poranny_z_plytka_ramkowa_swieci_na_ramce_p(kal, tmp_path, sprzataj):
    st = TSR.Stanowisko(tmp_path)
    sprzataj.append(st.sesja.baza.zamknij)
    TSR.wypelnij_indeks(st.sesja.baza)
    st.skan(TSR.rano(4, "2026-11-18T07:00:00", [{"g": 2, "k": [["X11", 0.95]]}, {"g": 3, "k": [["X12", 0.95]]}, {"g": 7, "k": []}], RAMKOWA_P))
    pp = st.rano.plan_plytek()
    program, atrapa, port, k, d = TI._poranek(kal, sprzataj)
    pominiete = k.ustaw_plan_rano(pp)
    assert pominiete["zla_plytka"] == [] and pominiete["brak_kalibracji"] == []
    assert TI.czekaj_na(lambda: program.logika.plan is not None and program.logika.plan.plan_id == pp["plan_id"], 5.0)
    assert sorted(program.logika.plan.plytki) == [4]
    atrapa.poloz_plytke(4)
    pierwsza = pp["kuwety"][0]["kuweta"]
    kolory = {g["id"]: g["kolor"] for g in pp["plytki"]["4"]["gniazda"] if g.get("kuweta") in (None, pierwsza)}
    oczekiwane = TI.piksele(kal, "P", "poranna", kolory)  # bloki kwadratu = bloki plytki ramkowej
    assert {2, 3, 7} <= set(kolory) and atrapa.czekaj(lambda a: TI.roznice_plytki(a.klatka, oczekiwane) == [], 3.0)


# --- kryterium 6: stary plik kalibracji dostaje brakujace uklady -------------------------------------------------------------
def test_k6_stary_plik_kalibracji_po_starcie_ma_2_nowe_uklady_a_skalibrowane_bajtowo_bez_zmian(tmp_path):
    plik = tmp_path / "dane" / "kalibracja_ramek.json"
    stara = stara_kalibracja()
    kalibracja.zapisz(stara, plik)
    bajty_przed = plik.read_bytes()
    assert RAMKOWA_W not in stara["ramki"]["W"] and RAMKOWA_P not in stara["ramki"]["P"]

    kal_, ostrzezenia = IND.wczytaj_kalibracje(plik, MODELE)  # = start programu (``Indicate.z_ustawien``)

    na_dysku = kalibracja.wczytaj(plik)
    assert kal_ == na_dysku
    dopisane = sorted((r, u) for r in ("W", "P") for u in na_dysku["ramki"][r] if u not in stara["ramki"][r])
    assert dopisane == [("P", RAMKOWA_P), ("W", RAMKOWA_W)]
    wzor = kalibracja.domyslna(MODELE)
    for rola, nazwa in dopisane:
        assert na_dysku["ramki"][rola][nazwa] == wzor["ramki"][rola][nazwa] and na_dysku["ramki"][rola][nazwa]["zrodlo"] == "geometria"
    # wpisy sprzed uzupelnienia bajtowo bez zmian: plik po usunieciu 2 dopisanych ukladow, zapisany ta sama funkcja = stary plik
    bez_nowych = copy.deepcopy(na_dysku)
    for rola, nazwa in dopisane:
        del bez_nowych["ramki"][rola][nazwa]
    kalibracja.zapisz(bez_nowych, tmp_path / "bez_nowych.json")
    assert (tmp_path / "bez_nowych.json").read_bytes() == bajty_przed
    for rola, nazwa in (("W", "wieczorna"), ("P", "poranna")):  # wpisy skalibrowane: te same wartosci i zrodlo
        assert na_dysku["ramki"][rola][nazwa] == stara["ramki"][rola][nazwa] and na_dysku["ramki"][rola][nazwa]["zrodlo"] == "kalibracja"
        tekst = json.dumps(stara["ramki"][rola][nazwa], ensure_ascii=True, indent=1, sort_keys=True).replace("\n", "\n   ")
        assert tekst.encode("ascii") in plik.read_bytes()  # ten sam ciag bajtow wpisu w nowym pliku
    assert any(RAMKOWA_W in o and RAMKOWA_P in o for o in ostrzezenia), ostrzezenia  # czlowiek wie, ze doszly uklady z geometrii
    # kopia pliku sprzed uzupelnienia zostaje obok
    kopie = sorted(p for p in plik.parent.iterdir() if p != plik)
    assert len(kopie) == 1 and kopie[0].read_bytes() == bajty_przed
    # drugi start: nic do dopisania - plik nietkniety, bez ostrzezenia
    bajty_po = plik.read_bytes()
    kal2, ostrzezenia2 = IND.wczytaj_kalibracje(plik, MODELE)
    assert kal2 == kal_ and ostrzezenia2 == [] and plik.read_bytes() == bajty_po
    assert sorted(p for p in plik.parent.iterdir() if p != plik) == kopie
    print(f"\n[E3-O2 kryterium 6] stary plik kalibracji: dopisane uklady {len(dopisane)} (oczekiwane 2); wpisy sprzed uzupelnienia "
          f"bajtowo bez zmian: {len(bajty_przed)} z {len(bajty_przed)} bajtow; skalibrowane (zrodlo = kalibracja) bez zmian: 2 z 2")


def test_k6_uklad_ramkowy_juz_skalibrowany_nie_jest_ruszany(tmp_path):
    plik = tmp_path / "kalibracja_ramek.json"
    dane = kalibracja.domyslna(MODELE)
    wpis = dane["ramki"]["W"][RAMKOWA_W]
    wpis["zrodlo"] = "kalibracja"
    wpis["gniazda"] = {gid: [x, y + 1, w, h] for gid, (x, y, w, h) in wpis["gniazda"].items()}
    del dane["ramki"]["P"][RAMKOWA_P]
    kalibracja.zapisz(dane, plik)
    kal_, ostrzezenia = IND.wczytaj_kalibracje(plik, MODELE)
    assert kal_["ramki"]["W"][RAMKOWA_W] == wpis  # skalibrowany uklad ramkowy zostaje
    assert kal_["ramki"]["P"][RAMKOWA_P]["zrodlo"] == "geometria" and any(RAMKOWA_P in o and RAMKOWA_W not in o for o in ostrzezenia)


def test_k6_zly_albo_brakujacy_plik_jak_dotad_bez_zapisu(tmp_path):
    brak = tmp_path / "nie_ma" / "kalibracja_ramek.json"
    kal_, ostrzezenia = IND.wczytaj_kalibracje(brak, MODELE)
    assert RAMKOWA_W in kal_["ramki"]["W"] and RAMKOWA_P in kal_["ramki"]["P"] and ostrzezenia and not brak.exists()
    zly = tmp_path / "zly.json"
    zly.write_text("{}", encoding="ascii")
    assert IND.wczytaj_kalibracje(zly, MODELE)[0] is None and zly.read_text(encoding="ascii") == "{}"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["zly.json"]


def test_k6_pliku_nie_da_sie_zapisac_uklady_sa_w_pamieci_i_jest_ostrzezenie(tmp_path, monkeypatch):
    plik = tmp_path / "kalibracja_ramek.json"
    kalibracja.zapisz(stara_kalibracja(), plik)
    bajty = plik.read_bytes()

    def odmowa(*a, **kw):
        raise PermissionError("tylko do odczytu")

    monkeypatch.setattr(kalibracja, "zapisz", odmowa)
    kal_, ostrzezenia = IND.wczytaj_kalibracje(plik, MODELE)
    assert RAMKOWA_W in kal_["ramki"]["W"] and RAMKOWA_P in kal_["ramki"]["P"]  # program swieci plytki ramkowe mimo to
    assert plik.read_bytes() == bajty and any("nie zostal" in o for o in ostrzezenia), ostrzezenia


def test_k6_test_led_na_atrapie_dla_ukladu_ramkowego(tmp_path, capsys):
    """``python -m ramka.test_led --uklad okragla_ramkowa_wieczorna`` (bez zmiany ``test_led.py`` - uklad z pliku kalibracji):
    na starym pliku "brak ukladu", po starcie programu (uzupelnienie pliku) - 19 gniazd; to samo dla ramki P (24)."""
    plik = tmp_path / "kalibracja_ramek.json"
    kalibracja.zapisz(stara_kalibracja(), plik)
    argumenty = ["--kalibracja", str(plik), "--rola", "W", "--uklad", RAMKOWA_W, "--sprzet", "atrapa"]
    assert test_led.main(argumenty) == 1 and "brak ukladu" in capsys.readouterr().err
    IND.wczytaj_kalibracje(plik, MODELE)
    assert test_led.main(argumenty) == 0
    assert f"test LED: 19 gniazd ukladu {RAMKOWA_W} (ramka W)" in capsys.readouterr().out
    assert test_led.main(["--kalibracja", str(plik), "--rola", "P", "--uklad", RAMKOWA_P, "--sprzet", "atrapa", "--wszystkie"]) == 0
    assert f"test LED: 24 gniazd ukladu {RAMKOWA_P} (ramka P)" in capsys.readouterr().out
    assert test_led.main(["--kalibracja", str(plik), "--rola", "P", "--uklad", RAMKOWA_W, "--sprzet", "atrapa"]) == 1  # W nie na ramce P


def test_k6_uzupelnij_z_wiersza_polecen(tmp_path, capsys):
    """``python -m ramka.kalibracja --uzupelnij <plik> --modele modele_plytek`` - to samo uzupelnienie bez programu
    stanowiska (np. plik kalibracji trzymany na Raspberry Pi dla ``test_led``)."""
    plik = tmp_path / "kalibracja_ramek.json"
    stara = stara_kalibracja()
    kalibracja.zapisz(stara, plik)
    assert kalibracja.main(["--uzupelnij", str(plik), "--modele", str(MODELE)]) == 0
    assert RAMKOWA_W in capsys.readouterr().out
    po = kalibracja.wczytaj(plik)
    assert po["ramki"]["W"]["wieczorna"] == stara["ramki"]["W"]["wieczorna"] and RAMKOWA_P in po["ramki"]["P"]
    assert kalibracja.main(["--uzupelnij", str(plik), "--modele", str(MODELE)]) == 0 and "nic do dopisania" in capsys.readouterr().out
    assert kalibracja.main(["--uzupelnij", str(plik)]) == 2


# =============================================================================================================================
# kontroler: komunikaty dla technika (kryterium 4; decyzja 5: komunikat na ekranie + ramka ciemna, skan PRZYJETY, bez blokady)
# =============================================================================================================================
NOWE_KOMUNIKATY = ("plytka_nie_z_ramki", "plytka_inna_niz_skan", "plytka_bez_skanu", "numer_niezgodny",
                   "dwa_skany_numeru", "plytka_czeka_na_numer")  # dwa ostatnie: runda 2 (recenzja PR #55: B1, P1)


class Zegar:
    def __init__(self, teraz: dt.datetime):
        self.teraz = teraz

    def __call__(self) -> dt.datetime:
        return self.teraz


class StanowiskoZRamkami:
    """Kontroler na danych sztucznych (``AtrapaKontrolera``: prawdziwa sesja i baza w ``tmp_path``) + prawdziwi klienci
    ``indicate.KlientRamki`` + dwie atrapy ramek (program ramki z atrapa sprzetu) w procesie testu. Plytke na ramce "kladzie"
    test (``poloz``); obraz ramki = klatka atrapy (piksele)."""

    def __init__(self, katalog, kal, sprzataj, tryb: str = "wieczor"):
        from stanowisko import kontroler_api as K

        self.K, self.kal = K, kal
        self.programy, self.atrapy, klienci = {}, {}, {}
        for rola in ("W", "P"):
            program, atrapa, port = TI.ramka_wewnatrz(rola)
            sprzataj.append(program.zatrzymaj)
            self.programy[rola], self.atrapy[rola] = program, atrapa
            klienci[rola] = IND.KlientRamki(rola, "127.0.0.1", port, laptop_id=TI.LAPTOP, kalibracja=kal, przerwa_min_s=0.05,
                                            przerwa_max_s=0.25, odpytywanie_s=2.0)
        start = dt.datetime(2026, 11, 17, 19, 0, 0) if tryb == "wieczor" else dt.datetime(2026, 11, 18, 6, 30, 0)
        self.k = K.AtrapaKontrolera(katalog, zegar=Zegar(start), tryb=tryb)
        sprzataj.append(self.k.zamknij)
        assert self.k.wybierz_operatora("Technik A")
        self.k.podlacz_ramki(IND.Indicate(klienci["W"], klienci["P"]))
        self.czekaj(lambda: self.ramka("W").polaczona and self.ramka("P").polaczona, "polaczenie z ramkami")

    def ramka(self, rola: str):
        r = self.k.stan().ramki
        return r.wieczorna if rola == "W" else r.poranna

    def czekaj(self, warunek, co: str = "", limit_s: float = 10.0) -> None:
        koniec = time.monotonic() + limit_s
        while True:
            self.k.przetworz()
            if warunek():
                return
            assert time.monotonic() < koniec, f"nie doczekalem sie: {co}; komunikaty: {[(x.rodzaj, x.tekst) for x in self.k.stan().komunikaty]}"
            time.sleep(0.02)

    def poloz(self, rola: str, numer: int) -> None:
        """Plytka o numerze ``numer`` (magnesy) polozona na ramce; 0 = zdjeta. Czeka, az program zobaczy ja w stanie ramki."""
        self.atrapy[rola].poloz_plytke(numer)
        self.czekaj(lambda: self.ramka(rola).plytka == numer, f"plytka {numer} na ramce {rola}")

    def komunikaty(self, rodzaj: str) -> list:
        return [x for x in self.k.stan().komunikaty if x.rodzaj == rodzaj]

    def nowe(self) -> list:
        return sorted(x.rodzaj for x in self.k.stan().komunikaty if x.rodzaj in NOWE_KOMUNIKATY)

    def komunikat(self, rodzaj: str):
        self.czekaj(lambda: len(self.komunikaty(rodzaj)) == 1, f"komunikat {rodzaj}")
        return self.komunikaty(rodzaj)[0]

    def bez_komunikatu(self, rodzaj: str) -> None:
        self.czekaj(lambda: not self.komunikaty(rodzaj), f"komunikat {rodzaj} znika")

    def plan_na_ramce(self, rola: str, plytki: list) -> None:
        self.czekaj(lambda: (p := self.programy[rola].logika.plan) is not None and sorted(p.plytki) == plytki, f"plan {plytki} na ramce {rola}")

    def ciemna(self, rola: str, przez_s: float = 0.4) -> bool:
        """W calym obszarze plytki nie swieci zaden piksel: ramka gasnie (polecenie idzie siecia - czekanie do 5 s) i zostaje
        ciemna przez ``przez_s`` (obraz nie pojawia sie z opoznieniem)."""
        self.czekaj(lambda: not TI.roznice_plytki(self.atrapy[rola].klatka, {}), f"ramka {rola} gasnie", 5.0)
        koniec = time.monotonic() + przez_s
        while time.monotonic() < koniec:
            self.k.przetworz()
            if TI.roznice_plytki(self.atrapy[rola].klatka, {}):
                return False
            time.sleep(0.02)
        return True

    def swieci_wynik(self, skan_id: int, uklad_kalibracji: str = "wieczorna") -> int:
        """Ramka W pokazuje wynik skanu: piksele = bloki kalibracji w kolorach mapy z ekranu. Zwraca liczbe swiecacych gniazd."""
        plytka = self.k.stan().plytka(skan_id)
        kolory = {g.nr: RP.kolor_ramki(g.status) for g in plytka.gniazda if RP.kolor_ramki(g.status) is not None}
        oczekiwane = TI.piksele(self.kal, "W", uklad_kalibracji, kolory)
        roznice = [None]

        def zgodne() -> bool:
            roznice[0] = TI.roznice_plytki(self.atrapy["W"].klatka, oczekiwane)
            return roznice[0] == []

        self.czekaj(zgodne, f"wynik skanu {skan_id} na ramce W (roznych pikseli: {len(roznice[0] or [])})")
        return len(kolory)

    def swieci(self, rola: str) -> None:
        self.czekaj(lambda: len(TI.roznice_plytki(self.atrapy[rola].klatka, {})) >= 9, f"ramka {rola} swieci")

    def skan_w_bazie(self, skan_id: int) -> dict:
        """Skan nie przepada: wiersz skanu, liczba prac i plik wyniku (kryterium 4)."""
        baza = self.k.sesja.baza
        w = baza.wiersz("SELECT status, numer_plytki, numer_zrodlo, uklad, wynik_json FROM skany WHERE id = ?", (skan_id,))
        plik = self.k.sesja.sciezka_wyniku(skan_id)
        return {**w, "prac": baza.wiersz("SELECT count(*) AS n FROM prace WHERE skan_id = ?", (skan_id,))["n"],
                "plik_wyniku": plik is not None and plik.is_file()}


def tekst(rodzaj: str, **pola) -> str:
    from stanowisko import statusy as ST

    return ST.tekst_komunikatu(rodzaj, **pola)[2]


def test_k4_umowa_numery_ramek_jak_w_protokole_ramki():
    from ramka import protokol
    from stanowisko import kontroler_api as K
    from stanowisko import session as SE
    from stanowisko import statusy as ST

    assert K.NUMERY_RAMEK == {r: tuple(v) for r, v in protokol.RODZINY.items()}
    assert SE.NUMERY_RAMKOWE == {"wieczorna": tuple(protokol.RODZINY["W"]), "poranna": tuple(protokol.RODZINY["P"])}
    assert set(NOWE_KOMUNIKATY) <= set(ST.KOMUNIKATY) and set(ST.RAMKA_KTOREJ) == {"W", "P"} == set(ST.RADY_PLYTKA_NIE_Z_RAMKI) - {None}
    for rodzaj in NOWE_KOMUNIKATY:  # komunikat mowi, CO zrobic, i nie blokuje (poziom ostrzezenie, nie blad)
        assert ST.KOMUNIKATY[rodzaj].poziom == ST.POZIOM_OSTRZEZENIE and len(ST.KOMUNIKATY[rodzaj].tekst) > 80


# --- (a) numer plytki lezacej na ramce spoza roli ramki ------------------------------------------------------------------------
def test_k4a_plytka_poranna_nr_5_na_ramce_wieczornej_komunikat_ramka_ciemna_skan_zostaje(kal, tmp_path, sprzataj):
    """Przeglad E3-S1 (POTRZEBUJE 5): plytka nr 5 na ramce W - dotad pasek "W: gotowa (plytka 5)" i 0 komunikatow."""
    from stanowisko import statusy as ST

    s = StanowiskoZRamkami(tmp_path / "k", kal, sprzataj)
    skan = s.k.symuluj_skan("czysta", numer=1, uklad=RAMKOWA_W, numer_z_dolkow=1)
    s.plan_na_ramce("W", [1])
    assert s.nowe() == []
    s.poloz("W", 5)
    kom = s.komunikat("plytka_nie_z_ramki")
    assert kom.id == "plytka_nie_z_ramki:W" and kom.poziom == "ostrzezenie" and not kom.ukryte
    assert kom.tekst == tekst("plytka_nie_z_ramki", ramka=ST.RAMKA_KTOREJ["W"], numer=5, numery="1, 2, 3", rada=ST.RADY_PLYTKA_NIE_Z_RAMKI["W"])
    assert "nr 5" in kom.tekst and "1, 2, 3" in kom.tekst and "{" not in kom.tekst and "?" not in kom.tekst
    assert s.ciemna("W")
    w = s.skan_w_bazie(skan)
    assert (w["status"], w["numer_plytki"], w["prac"], w["plik_wyniku"]) == ("przyjety", 1, 4, True)
    assert s.k.stan().plytka(skan).aktywna and s.k.ukruszona(s.k.stan().plytka(skan).gniazdo(2).praca.praca_id)  # bez blokady: decyzje dzialaja
    # plytka zdjeta: komunikat znika sam; wlasciwa plytka: ramka swieci
    s.poloz("W", 0)
    s.bez_komunikatu("plytka_nie_z_ramki")
    s.poloz("W", 1)
    assert s.swieci_wynik(skan) == 4 and s.nowe() == []
    # numer spoza obu ramek (7): komunikat z rada ogolna
    s.poloz("W", 7)
    assert s.komunikat("plytka_nie_z_ramki").tekst == tekst("plytka_nie_z_ramki", ramka=ST.RAMKA_KTOREJ["W"], numer=7, numery="1, 2, 3",
                                                           rada=ST.RADY_PLYTKA_NIE_Z_RAMKI[None])


def test_k4a_plytka_wieczorna_nr_2_na_ramce_porannej_komunikat_ramka_ciemna_skan_zostaje(kal, tmp_path, sprzataj):
    from stanowisko import statusy as ST

    s = StanowiskoZRamkami(tmp_path / "k", kal, sprzataj, tryb="rano")
    skan = s.k.symuluj_skan_rano(4, {1: "pewna", 2: "pewna", 5: "pewna"}, projekty={1: 301, 2: 302, 5: 304}, uklad=RAMKOWA_P, numer_z_dolkow=4)
    s.plan_na_ramce("P", [4])
    s.poloz("P", 2)
    kom = s.komunikat("plytka_nie_z_ramki")
    assert kom.id == "plytka_nie_z_ramki:P"
    assert kom.tekst == tekst("plytka_nie_z_ramki", ramka=ST.RAMKA_KTOREJ["P"], numer=2, numery="4, 5, 6", rada=ST.RADY_PLYTKA_NIE_Z_RAMKI["P"])
    assert s.ciemna("P")
    w = s.skan_w_bazie(skan)
    assert (w["status"], w["numer_plytki"], w["prac"], w["plik_wyniku"]) == ("przyjety", 4, 3, True)
    assert s.k.stan().rano.blokady == ()  # "Zamknij piec" bez blokady
    s.poloz("P", 4)
    s.bez_komunikatu("plytka_nie_z_ramki")
    s.swieci("P")
    assert s.nowe() == []


# --- (b) numer z ramki rozny od numeru plytki ze skanu, ktorej wynik ma byc swiecony --------------------------------------------
def test_k4b_wieczor_na_ramce_plytka_2_a_wynik_plytki_1_komunikat_ramka_ciemna_skan_zostaje(kal, tmp_path, sprzataj):
    s = StanowiskoZRamkami(tmp_path / "k", kal, sprzataj)
    skan = s.k.symuluj_skan("zwykla", numer=1, uklad=RAMKOWA_W, numer_z_dolkow=1)
    s.plan_na_ramce("W", [1])
    assert s.nowe() == []  # plytka jeszcze w skanerze (ramka pusta): bez komunikatu
    s.poloz("W", 2)
    kom = s.komunikat("plytka_inna_niz_skan")
    assert kom.id == "plytka_inna_niz_skan:W" and kom.tekst == tekst("plytka_inna_niz_skan", na_ramce=2, ze_skanu=1)
    assert "nr 2" in kom.tekst and "nr 1" in kom.tekst and "{" not in kom.tekst and "?" not in kom.tekst
    assert s.ciemna("W")
    w = s.skan_w_bazie(skan)
    assert (w["status"], w["numer_plytki"], w["numer_zrodlo"], w["prac"], w["plik_wyniku"]) == ("przyjety", 1, "dolki", 9, True)
    # wlasciwa plytka na ramce: komunikat znika, wynik swieci (te same piksele co dla kwadratu)
    s.poloz("W", 1)
    s.bez_komunikatu("plytka_inna_niz_skan")
    assert s.swieci_wynik(skan) >= 5
    # nastepny skan (plytka 3) przy plytce 1 lezacej na ramce: komunikat o nowej parze numerow
    skan3 = s.k.symuluj_skan("czysta", numer=3, uklad=RAMKOWA_W, numer_z_dolkow=3)
    s.czekaj(lambda: [x.tekst for x in s.komunikaty("plytka_inna_niz_skan")] == [tekst("plytka_inna_niz_skan", na_ramce=1, ze_skanu=3)],
             "komunikat o plytce 1 na ramce i skanie plytki 3")
    assert s.ciemna("W") and s.skan_w_bazie(skan3)["status"] == "przyjety"


def test_k4b_rano_na_ramce_plytka_6_ktorej_nie_ma_w_planie_pieca_komunikat_ramka_ciemna(kal, tmp_path, sprzataj):
    from stanowisko import statusy as ST

    s = StanowiskoZRamkami(tmp_path / "k", kal, sprzataj, tryb="rano")
    skan4 = s.k.symuluj_skan_rano(4, {1: "pewna", 2: "pewna"}, projekty={1: 301, 2: 302}, uklad=RAMKOWA_P, numer_z_dolkow=4)
    skan5 = s.k.symuluj_skan_rano(5, {1: "pewna"}, projekty={1: 307}, uklad=RAMKOWA_P, numer_z_dolkow=5)
    s.plan_na_ramce("P", [4, 5])
    assert s.nowe() == []
    s.poloz("P", 6)
    kom = s.komunikat("plytka_bez_skanu")
    assert kom.id == "plytka_bez_skanu:P"
    assert kom.tekst == tekst("plytka_bez_skanu", na_ramce=6, w_planie=ST.W_PLANIE_PLYTKI.format(plytki="4, 5"))
    assert "nr 6" in kom.tekst and "4, 5" in kom.tekst and "{" not in kom.tekst and "?" not in kom.tekst
    assert s.ciemna("P")
    assert [s.skan_w_bazie(x)["status"] for x in (skan4, skan5)] == ["przyjety", "przyjety"] and s.k.stan().rano.blokady == ()
    # plytka 6 zeskanowana: plan ja dostaje, komunikat znika, ramka swieci
    s.k.symuluj_skan_rano(6, {1: "pewna"}, projekty={1: 308}, uklad=RAMKOWA_P, numer_z_dolkow=6)
    s.plan_na_ramce("P", [4, 5, 6])
    s.bez_komunikatu("plytka_bez_skanu")
    s.swieci("P")


# --- (c) numer podany rozny od waznego numeru z dolkow ---------------------------------------------------------------------------
def test_k4c_wieczor_numer_podany_inny_niz_z_dolkow_komunikat_ramka_ciemna_skan_zostaje(kal, tmp_path, sprzataj):
    s = StanowiskoZRamkami(tmp_path / "k", kal, sprzataj)
    skan = s.k.symuluj_skan("czysta", numer=1, uklad=RAMKOWA_W, numer_z_dolkow=1)
    s.poloz("W", 1)
    assert s.swieci_wynik(skan) == 4 and s.nowe() == []
    assert s.k.podaj_numer_plytki(skan, 2)  # technik zmienia numer na inny niz odczytany z dolkow
    kom = s.komunikat("numer_niezgodny")
    assert kom.id == f"numer_niezgodny:{skan}" and kom.skan_id == skan and kom.trwaly
    assert kom.tekst == tekst("numer_niezgodny", podany=2, dolki=1) and "{" not in kom.tekst and "?" not in kom.tekst
    plytka = s.k.stan().plytka(skan)
    assert (plytka.numer, plytka.numer_zrodlo, plytka.numer_niezgodny, plytka.numer_z_dolkow) == (2, "podany", True, 1)
    assert kom in plytka.komunikaty
    assert s.ciemna("W")  # plytka 1 (numer z dolkow) na ramce: ciemno
    w = s.skan_w_bazie(skan)
    assert (w["status"], w["numer_plytki"], w["numer_zrodlo"], w["prac"], w["plik_wyniku"]) == ("przyjety", 2, "podany", 4, True)
    assert plytka.aktywna and plytka.zielonych == 4  # skan przyjety, prace sie licza, decyzje dostepne
    # numer poprawiony na zgodny z dolkami: komunikat znika, ramka swieci (plytka nie byla zdejmowana z ramki)
    assert s.k.podaj_numer_plytki(skan, 1)
    s.bez_komunikatu("numer_niezgodny")
    assert s.swieci_wynik(skan) == 4 and not s.k.stan().plytka(skan).numer_niezgodny
    # znow numer niezgodny; na ramce plytka o numerze PODANYM: tez ciemno (program nie zgaduje, ktory numer jest dobry)
    assert s.k.podaj_numer_plytki(skan, 3)
    assert s.komunikat("numer_niezgodny").tekst == tekst("numer_niezgodny", podany=3, dolki=1)
    s.poloz("W", 3)
    assert s.ciemna("W")
    assert s.komunikaty("plytka_inna_niz_skan") == []  # jeden komunikat o jednej przyczynie
    assert s.skan_w_bazie(skan)["status"] == "przyjety"


def test_k4c_rano_numer_podany_inny_niz_z_dolkow_plytka_poza_planem_bez_blokady(kal, tmp_path, sprzataj):
    s = StanowiskoZRamkami(tmp_path / "k", kal, sprzataj, tryb="rano")
    skan4 = s.k.symuluj_skan_rano(4, {1: "pewna", 2: "pewna"}, projekty={1: 301, 2: 302}, uklad=RAMKOWA_P, numer_z_dolkow=4)
    skan5 = s.k.symuluj_skan_rano(5, {1: "pewna"}, projekty={1: 307}, uklad="poranna")
    s.plan_na_ramce("P", [4, 5])
    assert s.k.podaj_numer_plytki(skan4, 6)
    kom = s.komunikat("numer_niezgodny")
    assert kom.id == f"numer_niezgodny:{skan4}" and kom.tekst == tekst("numer_niezgodny", podany=6, dolki=4)
    plytka = s.k.stan().rano.plytka(skan4)
    assert (plytka.numer, plytka.numer_niezgodny, plytka.numer_z_dolkow) == (6, True, 4)
    s.plan_na_ramce("P", [5])  # plytka z niezgodnym numerem wypada z planu ramki
    assert s.k._plan_p_dane["pominiete"]["numer_niezgodny"] == [skan4]
    s.poloz("P", 6)
    assert s.ciemna("P") and s.komunikaty("plytka_bez_skanu") == []  # numer podany: ciemno, przyczyne podaje komunikat numer_niezgodny
    s.poloz("P", 5)
    s.swieci("P")  # druga plytka pieca swieci jak zwykle
    w = s.skan_w_bazie(skan4)
    assert (w["status"], w["numer_plytki"], w["numer_zrodlo"], w["prac"], w["plik_wyniku"]) == ("przyjety", 6, "podany", 2, True)
    assert s.k.stan().rano.blokady == () and s.skan_w_bazie(skan5)["status"] == "przyjety"  # bez twardej blokady "Zamknij piec"
    assert plytka.aktywna and plytka.zielonych == 2
    assert s.k.podaj_numer_plytki(skan4, 4)
    s.bez_komunikatu("numer_niezgodny")
    s.plan_na_ramce("P", [4, 5])
    s.poloz("P", 4)
    s.swieci("P")


def test_k4_szesc_przypadkow_licznik():
    """Kryterium 4: komunikat w 6 z 6 przypadkow (po 2 na a, b, c) - licznik dla raportu; przypadki to 6 testow ``test_k4a_*``,
    ``test_k4b_*``, ``test_k4c_*`` tego pliku (kazdy sprawdza: komunikat, ramke ciemna piksel po pikselu, skan w bazie)."""
    przypadki = [n for n in globals() if n.startswith(("test_k4a_", "test_k4b_", "test_k4c_"))]
    assert len(przypadki) == 6 and sorted(n[:8] for n in przypadki) == ["test_k4a"] * 2 + ["test_k4b"] * 2 + ["test_k4c"] * 2
    print(f"\n[E3-O2 kryterium 4] przypadkow z komunikatem, ramka ciemna i skanem w bazie: {len(przypadki)} (a: 2, b: 2, c: 2)")


def test_k4_numer_z_dolkow_spoza_ukladu_to_pytanie_o_numer_a_nie_komunikat(kal, tmp_path, sprzataj):
    """Zasloniete dolki = numer 0 z analizy: plytka BEZ numeru (pytanie z numerami 1, 2, 3 jak dla kwadratu); po podaniu numeru
    nie ma komunikatu o niezgodnosci (0 to nie jest wazny numer z dolkow) i ramka swieci."""
    s = StanowiskoZRamkami(tmp_path / "k", kal, sprzataj)
    skan = s.k.symuluj_skan("czysta", numer=0, uklad=RAMKOWA_W, numer_z_dolkow=0)
    plytka = s.k.stan().plytka(skan)
    assert (plytka.status, plytka.numer, plytka.numer_zrodlo) == ("przyjety", None, "nieznany")
    pytanie = next(q for q in s.k.stan().pytania if q.rodzaj == "brak_numeru_plytki" and q.skan_id == skan)
    assert pytanie.numery == (1, 2, 3)
    s.poloz("W", 2)
    assert s.ciemna("W") and s.nowe() == []  # bez numeru: ramka ciemna jak dla kwadratu, bez nowych komunikatow
    assert s.k.podaj_numer_plytki(skan, 2)
    assert s.swieci_wynik(skan) == 4 and s.nowe() == [] and not s.k.stan().plytka(skan).numer_niezgodny


# --- kryterium 3: kwadrat i plytka testowa bez nowych komunikatow ---------------------------------------------------------------
def test_k3_kwadrat_z_numerem_podanym_i_plytka_testowa_bez_nowych_komunikatow(kal, tmp_path, sprzataj):
    s = StanowiskoZRamkami(tmp_path / "k", kal, sprzataj)
    kwadrat = s.k.symuluj_skan("bez_numeru", uklad="wieczorna")  # dolki kwadratu poza polem skanu: wynik bez numeru z dolkow
    assert s.k.podaj_numer_plytki(kwadrat, 2)
    s.poloz("W", 2)
    assert s.swieci_wynik(kwadrat) >= 1 and s.nowe() == [] and not s.k.stan().plytka(kwadrat).numer_niezgodny
    assert s.k.podaj_numer_plytki(kwadrat, 3)  # zmiana numeru kwadratu: nie ma z czym porownac - bez komunikatu numer_niezgodny
    assert s.komunikaty("numer_niezgodny") == []
    s.poloz("W", 3)
    assert s.swieci_wynik(kwadrat) >= 1 and s.nowe() == []
    s.poloz("W", 0)
    testowa = s.k.symuluj_skan("czysta", numer=8, uklad="okragla_wieczorna", numer_z_dolkow=8)
    plytka = s.k.stan().plytka(testowa)
    assert (plytka.status, plytka.numer, plytka.numer_niezgodny) == ("przyjety", 8, False)
    assert s.ciemna("W") and s.nowe() == []  # jak dotad: plytka testowa nie swieci na ramce i nie daje komunikatu


# --- przeglad narzedzi E3-S1: POTRZEBUJE 3 (przyczyna bledu analizy) ---------------------------------------------------------------
def _blad_analizy(k, opis: str) -> int:
    """Skan z bledem analizy zapisany tak, jak robi to ``Aplikacja`` (``przyjmij_blad`` + wpis ``blad_analizy_rodzaj``)."""
    skrot = hashlib.sha256(opis.encode("utf-8")).hexdigest()[:16]
    zdarzenie = {"plik": f"atrapa/blad_{skrot}.stl", "sha16": skrot, "rozmiar": 1000, "czas_pliku": k._teraz()}
    skan_id = k.sesja.przyjmij_blad(zdarzenie, f"analiza: {opis}", k.tryb)
    k.sesja.baza.zdarzenie("silnik", "blad_analizy_rodzaj", {"rodzaj": "analiza"}, skan_id=skan_id, czas=k._teraz())
    k._odswiez()
    return skan_id


def test_s1_blad_analizy_podaje_przyczyne_ile_znacznikow_widac(tmp_path):
    """Skan bez 3 stozkow znacznikow (pole skanera 80 / 90 mm): dotad "Program nie przeanalizowal tego skanu (blad analizy).
    Zeskanuj plytke ponownie" - technik skanowal w kolko. Teraz przyczyna i rada; tekst bledu bierze test z PRAWDZIWEGO
    wyjatku ``plate.przypisz_znaczniki`` (zmiana tekstu w ``plate.py`` = ten test pada, a nie cicha utrata przyczyny)."""
    from stanowisko import kontroler_api as K
    from stanowisko import plate
    from stanowisko import statusy as ST
    from stanowisko import uklad as U

    k = K.AtrapaKontrolera(tmp_path / "k", zegar=Zegar(dt.datetime(2026, 11, 17, 19, 0, 0)))
    try:
        teksty = {}
        for n in (0, 1, 2):
            with pytest.raises(plate.BladWyrownania) as blad:
                plate.przypisz_znaczniki([{"x": 10.0 * i, "y": 0.0} for i in range(n)], U.wczytaj("wieczorna"))
            skan = _blad_analizy(k, f"BladWyrownania: {blad.value}")
            kom = next(x for x in k.stan().komunikaty if x.id == f"blad_analizy:{skan}")
            # runda 3: 0 z 3 znacznikow ma osobny tekst (druga przyczyna: stolik / podloze w skanie)
            assert kom.tekst == tekst("blad_analizy", powod=ST.PRZYCZYNY_BLEDU_ANALIZY["znaczniki" if n else "znaczniki_0"].format(n=n))
            assert f"{n} z 3" in kom.tekst and kom.tekst != tekst("blad_analizy", powod=ST.POWODY_BLEDU_ANALIZY["analiza"])
            teksty[n] = kom.tekst
        assert len(set(teksty.values())) == 3
        # inny blad analizy: powod ogolny jak dotad
        inny = _blad_analizy(k, "ValueError: cos innego")
        assert next(x for x in k.stan().komunikaty if x.id == f"blad_analizy:{inny}").tekst == tekst("blad_analizy", powod=ST.POWODY_BLEDU_ANALIZY["analiza"])
        assert k.stan().plytka(inny).status == "blad"
    finally:
        k.zamknij()


def test_s1_blad_analizy_brak_wierzchu_i_pusty_skan(tmp_path):
    from stanowisko import kontroler_api as K
    from stanowisko import statusy as ST

    k = K.AtrapaKontrolera(tmp_path / "k", zegar=Zegar(dt.datetime(2026, 11, 17, 19, 0, 0)))
    try:
        zrodlo = (STANOWISKO / "stanowisko" / "plate.py").read_text(encoding="utf-8")
        wyjatki = re.findall(r"raise BladWyrownania\(f?\"([^\"]+)\"", zrodlo)
        assert len(wyjatki) >= 3
        for klucz, wzor in K.WZORY_PRZYCZYN_BLEDU[1:]:
            # tekst wyjatku wyciety z plate.py - wzor kontrolera musi go rozpoznac (dokladnie jeden)
            trafienia = [m for m in wyjatki if wzor.search(m)]
            assert len(trafienia) == 1, (klucz, trafienia)
            skan = _blad_analizy(k, f"BladWyrownania: {trafienia[0]}")
            kom = next(x for x in k.stan().komunikaty if x.id == f"blad_analizy:{skan}")
            assert kom.tekst == tekst("blad_analizy", powod=ST.PRZYCZYNY_BLEDU_ANALIZY[klucz])
    finally:
        k.zamknij()


# =============================================================================================================================
# komunikat NA EKRANIE (istniejaca droga: stan kontrolera -> okno; bez zmian w ui/**) i drobne poprawki z przegladu E3-S1
# =============================================================================================================================
class KlientProbny:
    """Klient ramki bez sieci (jak ``test_aplikacja_rano.KlientAtrapa``), z numerem plytki lezacej na ramce i odpowiedzia
    ``wynik`` jak w ``indicate.KlientRamki._sprawdz_wynik`` (bez kalibracji: numer spoza 1-3 = "zla_plytka")."""

    def __init__(self, rola: str):
        self.rola, self.plytka, self.tryb_ramki = rola, None, "gotowa"
        self.polecenia: list = []
        self.wyniki: list = []

    def uruchom(self) -> None:
        pass

    def zatrzymaj(self, timeout: float = 1.0) -> bool:
        return True

    def wznow(self) -> None:
        pass

    def odbierz_zdarzenia(self) -> list:
        return []

    def stan(self) -> dict:
        return {"rola": self.rola, "polaczona": True, "blad": None, "komunikat": None, "plytka": self.plytka, "tryb_ramki": self.tryb_ramki,
                "plan_przyjety": False, "wstrzymane": False, "potwierdzone": [], "ostrzezenia": []}

    def potwierdzone(self) -> list:
        return []

    def ustaw_plan_rano(self, plan_plytek, *, potwierdzone=None, wybrane=None) -> dict:
        self.polecenia.append(("plan", sorted(plan_plytek["plytki"])))
        return {}

    def zgas(self) -> None:
        self.polecenia.append(("zgas",))

    def tryb(self, stan: str):
        self.polecenia.append(("tryb", stan))
        if stan == "test_led":
            self.tryb_ramki = "test_led"  # ramka konczy test sama, bez zdarzenia - klient dalej podaje "test_led"
        return ("znacznik", len(self.polecenia))

    def skanowanie(self):
        return self.tryb("skanowanie")

    def znacznik(self):
        return self.tryb("skanowanie")

    def analiza(self):
        return self.tryb("analiza")

    def blad(self):
        return self.tryb("blad")

    def wynik(self, numer, uklad, kolory, znacznik) -> str:
        self.wyniki.append((numer, uklad))
        return "bez_numeru" if numer is None else ("wyslany" if numer in (1, 2, 3) else "zla_plytka")


class RamkiProbne:
    def __init__(self):
        self.wieczorna, self.poranna = KlientProbny("W"), KlientProbny("P")

    def klienci(self) -> list:
        return [self.wieczorna, self.poranna]

    def uruchom(self) -> None:
        pass

    def zatrzymaj(self, timeout: float = 1.0) -> dict:
        return {"W": True, "P": True}

    def stan(self) -> dict:
        return {k.rola: k.stan() for k in self.klienci()}


@pytest.fixture
def ekrany():
    """Okno programu w trybie offscreen (pomocnicy ``test_aplikacja_rano`` / ``test_ui_wieczor``), 1920 x 1001."""
    import gc
    import os

    import test_aplikacja_rano as TAR
    import test_ui_wieczor as UW

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    if UW.FONTY_WINDOWS.is_dir():
        os.environ.setdefault("QT_QPA_FONTDIR", str(UW.FONTY_WINDOWS))
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    assert app.platformName() == "offscreen"
    UW.czcionka_ekranu()
    otwarte = []

    def nowy(kontroler):
        e = TAR.Ekran(kontroler, TAR.PELNY_EKRAN)
        otwarte.append(e)
        return e

    yield nowy
    for e in otwarte:
        e.zamknij()
    otwarte.clear()
    gc.collect()


def test_k4_komunikaty_sa_na_ekranie_okna_programu(tmp_path, ekrany):
    """Kryterium 4: "komunikat na ekranie" - trzy rodzaje komunikatow w oknie programu (widzet ``komunikat_<rodzaj>``, tytul
    i pelny tekst), istniejaca droga komunikatow kontrolera; zrzuty okna w ``tmp_path`` (do obejrzenia przez czlowieka)."""
    from stanowisko import kontroler_api as K
    from stanowisko import statusy as ST

    ramki = RamkiProbne()
    k = K.AtrapaKontrolera(tmp_path / "k", zegar=Zegar(dt.datetime(2026, 11, 17, 19, 0, 0)))
    try:
        assert k.wybierz_operatora("Technik A")
        k.podlacz_ramki(ramki)
        skan = k.symuluj_skan("czysta", numer=1, uklad=RAMKOWA_W, numer_z_dolkow=1)
        assert ramki.wieczorna.wyniki == [(1, RAMKOWA_W)]
        e = ekrany(k)

        def na_ekranie(rodzaj: str, tresc: str, zrzut: str) -> None:
            e.czekaj(lambda: e.jest(f"komunikat_{rodzaj}"), 5.0, f"komunikat {rodzaj} na ekranie")
            widac = e.tekst_elementu(f"komunikat_{rodzaj}")
            assert ST.KOMUNIKATY[rodzaj].tytul in widac and tresc in widac, widac
            assert e.okno.grab().save(str(tmp_path / zrzut))

        # komunikaty odsylaja do przycisku przy plytce - jego napis na ekranie (wieczor i rano) musi byc w tekscie komunikatu
        from stanowisko.ui import napisy as N
        from stanowisko.ui import napisy_rano as NR

        assert N.ZMIEN_NUMER == NR.ZMIEN_NUMER and e.jest("plytka_podaj_numer_plytki") and N.ZMIEN_NUMER in e.tekst()
        for rodzaj in ("plytka_inna_niz_skan", "plytka_bez_skanu", "numer_niezgodny"):
            assert N.ZMIEN_NUMER in ST.KOMUNIKATY[rodzaj].tekst, rodzaj
        ramki.wieczorna.plytka = 5  # (a) plytka poranna na ramce wieczornej
        na_ekranie("plytka_nie_z_ramki", tekst("plytka_nie_z_ramki", ramka=ST.RAMKA_KTOREJ["W"], numer=5, numery="1, 2, 3",
                                                 rada=ST.RADY_PLYTKA_NIE_Z_RAMKI["W"]), "a_plytka_nie_z_ramki.png")
        ramki.wieczorna.plytka = 2  # (b) na ramce plytka 2, wynik dotyczy plytki 1
        na_ekranie("plytka_inna_niz_skan", tekst("plytka_inna_niz_skan", na_ramce=2, ze_skanu=1), "b_plytka_inna_niz_skan.png")
        e.czekaj(lambda: not e.jest("komunikat_plytka_nie_z_ramki"), 5.0, "komunikat (a) znika, gdy plytki 5 nie ma juz na ramce")
        ramki.wieczorna.plytka = 0
        e.czekaj(lambda: not e.jest("komunikat_plytka_inna_niz_skan"), 5.0, "komunikat (b) znika po zdjeciu plytki")
        assert k.podaj_numer_plytki(skan, 2)  # (c) numer podany inny niz odczytany z dolkow
        na_ekranie("numer_niezgodny", tekst("numer_niezgodny", podany=2, dolki=1), "c_numer_niezgodny.png")
        assert ramki.wieczorna.wyniki[-1] == (None, RAMKOWA_W)  # ramka dostaje "bez numeru" = ciemna
        assert k.stan().plytka(skan).status == "przyjety"
    finally:
        k.zamknij()


def test_s1_tryb_ramki_po_tescie_diod_wraca_do_gotowa(tmp_path, monkeypatch):
    """Przeglad E3-S1 (POTRZEBUJE 8): ramka konczy test diod sama (po 8 s, bez zdarzenia), a ``StanRamki.tryb_ramki`` zostawalo
    ``test_led`` do nastepnego zdarzenia ramki. Kontroler zna koniec wlasnego testu - po nim podaje ``gotowa``."""
    from stanowisko import kontroler_api as K

    monkeypatch.setattr(K, "CZAS_TEST_LED_S", 0.3)
    ramki = RamkiProbne()
    k = K.AtrapaKontrolera(tmp_path / "k", zegar=Zegar(dt.datetime(2026, 11, 17, 19, 0, 0)))
    try:
        k.podlacz_ramki(ramki)
        assert k.test_led()
        k.przetworz()
        assert k.stan().ramki.test_led and k.stan().ramki.wieczorna.tryb_ramki == "test_led"
        koniec = time.monotonic() + 5.0
        while k.stan().ramki.test_led and time.monotonic() < koniec:
            k.przetworz()
            time.sleep(0.02)
        k.przetworz()
        assert not k.stan().ramki.test_led
        assert ramki.wieczorna.stan()["tryb_ramki"] == "test_led"  # klient nadal podaje stary tryb (ramka nie wyslala zdarzenia)
        assert (k.stan().ramki.wieczorna.tryb_ramki, k.stan().ramki.poranna.tryb_ramki) == ("gotowa", "gotowa")
    finally:
        k.zamknij()


def test_tytul_komunikatu_ma_wypelnione_pola():
    """``statusy.tekst_komunikatu`` wypelnia pola takze w TYTULE (komunikat ``ramka_blad``: tytul "Ramka {ramka}: problem" szedl
    na ekran z doslownym "{ramka}")."""
    from stanowisko import statusy as ST

    poziom, tytul, tresc = ST.tekst_komunikatu("ramka_blad", ramka="poranna", powod="x")
    assert "{" not in tytul and "poranna" in tytul and tresc == "x"
    assert ST.tekst_komunikatu("blad_analizy", powod="p")[1] == ST.KOMUNIKATY["blad_analizy"].tytul  # tytul bez pol - bez zmian
    assert "{" not in ST.tekst_komunikatu("ramka_blad", powod="x")[1]  # brak pola = znak zapytania, nie wyjatek


# =============================================================================================================================
# runda 2 (recenzja PR #55): B1 - dwa skany z jednym numerem a ramka wieczorna; P1 - skan bez numeru a plytka na ramce porannej;
# D1 / D3 - zapis pliku kalibracji; D2 - dwa warunki ochronne
# =============================================================================================================================
def _pytania_ponowny(s, skan_id: int) -> list:
    return [q for q in s.k.stan().pytania if q.rodzaj == "ponowny_skan" and q.skan_id == skan_id]


def test_r2_b1_okragla_n2_swieci_skan_kwadratu_n2_ramka_ciemna_do_odpowiedzi_potem_to_ponowny_skan(kal, tmp_path, sprzataj):
    """Recenzja PR #55, B1 (proba G1): okragla n2 lezy na ramce W i swieci swoj wynik; w skanerze kwadrat n2.
    WARIANT Z PYTANIEM (runda 3, P2): skan sztuczny bierze projekt = numer gniazda, wiec oba skany maja TE SAME projekty i
    program pyta "Ponowny skan tej samej plytki?" (``session._podstawa_ponownego``). Dotad pod plytka LEZACA zapalal sie wynik
    nowego skanu (9 gniazd), 0 komunikatow, a pytanie nie wstrzymywalo ramki. Teraz: do odpowiedzi ramka ciemna + komunikat;
    po "Tak, to ponowny skan" swieci wynik nowego skanu. Wariant BEZ pytania (inna plytka z INNYMI pracami - ramka NIE jest
    wstrzymywana): ``test_r3_p2_inna_plytka_nr_2_z_innymi_pracami_...``."""
    s = StanowiskoZRamkami(tmp_path / "k", kal, sprzataj)
    a = s.k.symuluj_skan("czysta", numer=2, uklad=RAMKOWA_W, numer_z_dolkow=2)
    s.poloz("W", 2)
    assert s.swieci_wynik(a) == 4 and s.nowe() == []
    b = s.k.symuluj_skan("zwykla", numer=2, uklad="wieczorna")
    pytania = _pytania_ponowny(s, b)
    assert len(pytania) == 1 and pytania[0].poprzedni_id == a and pytania[0].numer_plytki == 2
    assert s.ciemna("W", 1.0)  # 0 swiecacych pikseli pod plytka lezaca, dopoki pytanie jest otwarte
    kom = s.komunikat("dwa_skany_numeru")
    assert kom.id == "dwa_skany_numeru:W" and kom.poziom == "ostrzezenie" and not kom.ukryte
    assert kom.tekst == tekst("dwa_skany_numeru", numer=2) and "nr 2" in kom.tekst and "{" not in kom.tekst and "?" not in kom.tekst
    from stanowisko import statusy as ST

    for przycisk in ("potwierdz_ponowny_skan", "odrzuc_ponowny_skan"):  # komunikat podaje napisy przyciskow pytania - doslownie
        assert ST.PRZYCISKI[przycisk] in kom.tekst, przycisk
    assert "Dwa skany z numerem" in kom.tytul and "2" in kom.tytul and "{" not in kom.tytul and "?" not in kom.tytul
    assert s.nowe() == ["dwa_skany_numeru"] and s.ciemna("W", 0.6)
    for skan, prac in ((a, 4), (b, 9)):  # skany nie przepadaja, pytanie nadal czeka
        w = s.skan_w_bazie(skan)
        assert (w["status"], w["numer_plytki"], w["prac"], w["plik_wyniku"]) == ("przyjety", 2, prac, True)
    assert len(_pytania_ponowny(s, b)) == 1 and s.k.stan().plytka(a).aktywna and s.k.stan().plytka(b).aktywna
    # odpowiedz "Tak, to ponowny skan": stary skan zastapiony, komunikat znika, ramka swieci wynik nowego skanu (bloki kwadratu)
    assert s.k.potwierdz_ponowny_skan(b)
    s.bez_komunikatu("dwa_skany_numeru")
    swieci = s.swieci_wynik(b)
    assert swieci >= 5 and s.nowe() == [] and _pytania_ponowny(s, b) == []
    assert (s.skan_w_bazie(a)["status"], s.skan_w_bazie(b)["status"]) == ("zastapiony", "przyjety")
    print(f"\n[E3-O2 runda 2, B1] okragla n2 na ramce + skan kwadratu n2: swiecacych pikseli do odpowiedzi 0; po odpowiedzi "
          f"'to ponowny skan' swieci wynik nowego skanu: {swieci} gniazd")


def test_r2_b1_okragla_n3_odczytana_jako_2_ramka_ciemna_do_odpowiedzi_potem_to_inna_plytka(kal, tmp_path, sprzataj):
    """Recenzja PR #55, B1 (proba H1): okragla n2 lezy i swieci; w skanerze okragla n3 z zaslonietym dolkiem, odczytana jako 2.
    WARIANT Z PYTANIEM (runda 3, P2): skan sztuczny ma TE SAME projekty co skan plytki nr 2 (projekt = numer gniazda), wiec
    program pyta; prawdziwa plytka n3 z INNYMI pracami (co najmniej 3 rozpoznane projekty, mniej niz polowa wspolnych) pytania
    NIE dostaje i ramka nie jest wstrzymywana - ``test_r3_p2_inna_plytka_nr_2_z_innymi_pracami_...``.
    Do odpowiedzi ramka ciemna + komunikat (znika po zdjeciu plytki z ramki, wraca po polozeniu). Technik robi to, co kaze
    komunikat dla dwoch roznych plytek: NAJPIERW zdejmuje plytke lezaca, potem "Nie, to nowy wsad". Wtedy ramka zostaje ciemna
    takze dla plytki nr 2 polozonej pozniej (zasada ramki sprzed paczki: zdjecie plytki o numerze N po starcie skanu uniewaznia
    wynik dla numeru N - ``indicate.KlientRamki._wynik_wazny``); wynik ostatniego skanu pokazuje ekran."""
    s = StanowiskoZRamkami(tmp_path / "k", kal, sprzataj)
    a = s.k.symuluj_skan("czysta", numer=2, uklad=RAMKOWA_W, numer_z_dolkow=2)
    s.poloz("W", 2)
    assert s.swieci_wynik(a) == 4
    b = s.k.symuluj_skan("zwykla", numer=2, uklad=RAMKOWA_W, numer_z_dolkow=2)  # plytka n3, z dolkow WAZNY numer 2
    assert len(_pytania_ponowny(s, b)) == 1 and s.ciemna("W", 1.0)
    assert s.komunikat("dwa_skany_numeru").tekst == tekst("dwa_skany_numeru", numer=2)
    # zdjecie plytki lezacej na ramce: komunikat znika, pytanie zostaje
    s.poloz("W", 0)
    s.bez_komunikatu("dwa_skany_numeru")
    assert len(_pytania_ponowny(s, b)) == 1
    # plytka o numerze 2 polozona PRZED odpowiedzia: nadal ciemno, komunikat wraca
    s.poloz("W", 2)
    assert s.komunikat("dwa_skany_numeru").tekst == tekst("dwa_skany_numeru", numer=2) and s.ciemna("W", 0.6)
    s.poloz("W", 0)
    s.bez_komunikatu("dwa_skany_numeru")
    # odpowiedz "Nie, to nowy wsad" (to inna plytka): pytanie znika, oba skany zostaja aktywne z numerem 2
    assert s.k.odrzuc_ponowny_skan(b)
    assert _pytania_ponowny(s, b) == [] and s.k.stan().plytka(a).aktywna and s.k.stan().plytka(b).aktywna
    assert (s.skan_w_bazie(a)["status"], s.skan_w_bazie(b)["status"]) == ("przyjety", "przyjety")
    s.poloz("W", 2)  # ktorakolwiek z dwoch plytek o numerze 2: ramka ciemna (wynik uniewazniony zdjeciem plytki), bez komunikatu
    assert s.ciemna("W", 1.0) and s.nowe() == []
    assert s.k._w_wynik[:3] == (b, 2, "niewazny")
    print("\n[E3-O2 runda 2, B1] okragla n3 odczytana jako 2: swiecacych pikseli do odpowiedzi 0; plytka zdjeta, odpowiedz "
          "'to inna plytka', plytka nr 2 polozona: swiecacych pikseli 0 (wynik na ekranie)")


def test_r2_b1_odpowiedz_to_inna_plytka_gdy_plytka_nadal_lezy_swieci_wynik_ostatniego_skanu_mechanizm_zastany(kal, tmp_path, sprzataj):
    """Utrwalenie stanu faktycznego (NIE zmieniane w rundzie 2 - lista decyzji wlasciciela): technik odpowiada "Nie, to nowy
    wsad", NIE zdejmujac plytki lezacej na ramce (wariant Z PYTANIEM: te same projekty skanu sztucznego). Po odpowiedzi oba skany sa aktywne z numerem 2 i ramka - jak przed runda 2
    dla dwoch skanow bez pytania (proby H2 / H3 recenzenta) - swieci wynik OSTATNIEGO skanu pod plytka o numerze 2, czyli
    pod plytka z POPRZEDNIEGO skanu. Dlatego komunikat kaze najpierw zdjac plytke z ramki."""
    s = StanowiskoZRamkami(tmp_path / "k", kal, sprzataj)
    a = s.k.symuluj_skan("czysta", numer=2, uklad=RAMKOWA_W, numer_z_dolkow=2)
    s.poloz("W", 2)
    assert s.swieci_wynik(a) == 4
    b = s.k.symuluj_skan("zwykla", numer=2, uklad=RAMKOWA_W, numer_z_dolkow=2)
    assert len(_pytania_ponowny(s, b)) == 1 and s.ciemna("W", 1.0)
    kom = s.komunikat("dwa_skany_numeru")
    assert "najpierw zdejmij z ramki" in kom.tekst  # rada, ktorej ten scenariusz NIE slucha
    assert s.k.odrzuc_ponowny_skan(b)
    s.bez_komunikatu("dwa_skany_numeru")
    assert s.k.stan().plytka(a).aktywna and s.k.stan().plytka(b).aktywna
    swieci = s.swieci_wynik(b)
    assert swieci >= 5 and s.nowe() == []
    print(f"\n[E3-O2 runda 2, B1 - mechanizm zastany] odpowiedz 'to inna plytka' bez zdjecia plytki z ramki: pod plytka nr 2 "
          f"swieci wynik OSTATNIEGO skanu, {swieci} gniazd")


def test_r2_b1_inna_plytka_na_ramce_przy_otwartym_pytaniu_komunikat_b_jak_dotad(kal, tmp_path, sprzataj):
    """Pytanie o ponowny skan plytki 2 otwarte, a na ramce lezy plytka 1: komunikat (b) "na ramce lezy inna plytka" jak przed
    runda 2 (ramka ciemna), bez komunikatu o dwoch skanach - ten jest tylko dla plytki o numerze z pytania."""
    s = StanowiskoZRamkami(tmp_path / "k", kal, sprzataj)
    a = s.k.symuluj_skan("czysta", numer=2, uklad=RAMKOWA_W, numer_z_dolkow=2)
    s.poloz("W", 1)
    assert s.komunikat("plytka_inna_niz_skan").tekst == tekst("plytka_inna_niz_skan", na_ramce=1, ze_skanu=2)
    b = s.k.symuluj_skan("czysta", numer=2, uklad=RAMKOWA_W, numer_z_dolkow=2)  # ponowny skan tej samej plytki
    assert len(_pytania_ponowny(s, b)) == 1 and _pytania_ponowny(s, b)[0].poprzedni_id == a
    s.czekaj(lambda: [x.tekst for x in s.komunikaty("plytka_inna_niz_skan")] == [tekst("plytka_inna_niz_skan", na_ramce=1, ze_skanu=2)],
             "komunikat (b) o plytce 1 na ramce i skanie plytki 2")
    assert s.ciemna("W", 0.6) and s.nowe() == ["plytka_inna_niz_skan"]


def test_r2_b1_zwykla_praca_ramka_dostaje_numer_plytki_i_zero_nowych_komunikatow(tmp_path):
    """Zwykla praca (kazdy numer raz) - ramka W dostaje wynik z numerem plytki jak przed runda 2, 0 nowych komunikatow, 0 pytan.
    Ponowny skan TEJ SAMEJ plytki, gdy na ramce nic nie lezy: do odpowiedzi wynik "bez numeru" (ramka i tak pusta), bez
    komunikatu; po odpowiedzi wynik z numerem."""
    from stanowisko import kontroler_api as K

    ramki = RamkiProbne()
    k = K.AtrapaKontrolera(tmp_path / "k", zegar=Zegar(dt.datetime(2026, 11, 17, 19, 0, 0)))
    try:
        assert k.wybierz_operatora("Technik A")
        k.podlacz_ramki(ramki)

        def nowe() -> list:
            k.przetworz()
            return sorted(x.rodzaj for x in k.stan().komunikaty if x.rodzaj in NOWE_KOMUNIKATY)

        def poloz(numer: int) -> None:  # program czyta stan ramki co ``OKRES_STANU_RAMEK_S``
            ramki.wieczorna.plytka = numer
            koniec = time.monotonic() + 5.0
            while k.stan().ramki.wieczorna.plytka != numer:
                assert time.monotonic() < koniec, "program nie widzi plytki na ramce"
                k.przetworz()
                time.sleep(0.02)

        skany = []
        for numer in (1, 2, 3):
            skany.append(k.symuluj_skan("zwykla", numer=numer, uklad=RAMKOWA_W, numer_z_dolkow=numer))
            assert ramki.wieczorna.wyniki[-1] == (numer, RAMKOWA_W)
            poloz(numer)  # wlasciwa plytka polozona na ramce
            assert nowe() == []
            poloz(0)  # i zdjeta przed skanem nastepnej
            assert nowe() == []
        kwadrat = k.symuluj_skan("bez_numeru", uklad="wieczorna_r54")
        assert ramki.wieczorna.wyniki[-1] == (None, "wieczorna_r54")
        assert k.podaj_numer_plytki(kwadrat, 1)  # inna rodzina plytki niz skan okraglej n1: bez pytania (mechanizm zastany)
        assert ramki.wieczorna.wyniki[-1] == (1, "wieczorna_r54") and nowe() == []
        assert [q.rodzaj for q in k.stan().pytania if q.rodzaj == "ponowny_skan"] == []
        assert ramki.wieczorna.wyniki == [(1, RAMKOWA_W), (2, RAMKOWA_W), (3, RAMKOWA_W), (None, "wieczorna_r54"), (1, "wieczorna_r54")]
        # ponowny skan plytki 3 (te same prace), na ramce nic nie lezy
        ponowny = k.symuluj_skan("zwykla", numer=3, uklad=RAMKOWA_W, numer_z_dolkow=3)
        assert [q.skan_id for q in k.stan().pytania if q.rodzaj == "ponowny_skan"] == [ponowny]
        assert ramki.wieczorna.wyniki[-1] == (None, RAMKOWA_W) and nowe() == []
        assert k.potwierdz_ponowny_skan(ponowny)
        assert ramki.wieczorna.wyniki[-1] == (3, RAMKOWA_W) and nowe() == []
        assert k.stan().plytka(skany[2]).status == "zastapiony" and k.stan().plytka(ponowny).status == "przyjety"
    finally:
        k.zamknij()


def test_r2_b1_rano_dwa_skany_z_numerem_4_ramka_ciemna_jak_dotad(kal, tmp_path, sprzataj):
    """Rano ten sam uklad zdarzen byl i zostaje bezpieczny (proba G2 recenzenta): okragla n4 swieci, kwadrat dostaje numer 4 -
    plytka 4 wypada z planu ramki (``zdublowane_plytki``), ramka ciemna, bez komunikatu wieczornego o dwoch skanach."""
    s = StanowiskoZRamkami(tmp_path / "k", kal, sprzataj, tryb="rano")
    s.k.symuluj_skan_rano(4, {1: "pewna", 2: "pewna"}, projekty={1: 301, 2: 302}, uklad=RAMKOWA_P, numer_z_dolkow=4)
    s.plan_na_ramce("P", [4])
    s.poloz("P", 4)
    s.swieci("P")
    b = s.k.symuluj_skan_rano(None, {5: "pewna"}, projekty={5: 307}, uklad="poranna")
    assert s.k.podaj_numer_plytki(b, 4)
    s.plan_na_ramce("P", [])
    assert s.k._plan_p_dane["pominiete"]["zdublowane_plytki"] == [4]
    assert s.ciemna("P", 0.6) and s.komunikaty("dwa_skany_numeru") == [] and s.komunikaty("plytka_bez_skanu") == []
    assert s.k.stan().rano.blokady != ()  # "Zamknij piec" czeka na rozstrzygniecie dwoch skanow (mechanizm sprzed paczki)


# --- P1: rano skan bez numeru + plytka na ramce P - bez falszywej rady "Zeskanuj plytke nr N" ----------------------------------
def test_r2_p1_rano_skan_bez_numeru_i_plytka_na_ramce_bez_rady_zeskanuj(kal, tmp_path, sprzataj):
    """Recenzja PR #55, P1 (proba C2): zwykla droga kwadratow - skan bez numeru, plytka polozona na ramce P przed odpowiedzia
    na "Podaj numer plytki". Dotad: "Zeskanuj plytke nr 4 ... popraw przyciskiem Zmien numer" (plytka BYLA skanowana, a kafelek
    plytki bez numeru nie ma przycisku "Zmien numer"). Teraz: osobny komunikat - podaj numer w pytaniu."""
    from stanowisko import statusy as ST

    s = StanowiskoZRamkami(tmp_path / "k", kal, sprzataj, tryb="rano")
    skan = s.k.symuluj_skan_rano(None, {1: "pewna", 2: "pewna"}, projekty={1: 301, 2: 302}, uklad="poranna")
    assert [q.rodzaj for q in s.k.stan().pytania if q.skan_id == skan] == ["brak_numeru_plytki"]
    s.czekaj(lambda: s.k._plan_p_dane is not None and s.k._plan_p_dane["pominiete"]["bez_numeru"] == [skan], "plan z plytka bez numeru")
    s.poloz("P", 4)
    kom = s.komunikat("plytka_czeka_na_numer")
    assert kom.id == "plytka_czeka_na_numer:P" and kom.poziom == "ostrzezenie"
    assert kom.tekst == tekst("plytka_czeka_na_numer", na_ramce=4, w_planie=ST.W_PLANIE_BRAK, jest_skan=ST.JEST_SKAN_BEZ_NUMERU[False])
    assert "nr 4" in kom.tekst and "{" not in kom.tekst and "?" not in kom.tekst
    wszystkie = " ".join(x.tekst for x in s.k.stan().komunikaty)
    # ani bezwarunkowe "Zeskanuj plytke nr 4", ani "Zmien numer" (runda 3, D7: rada warunkowa "jesli ... nie skanowano - zeskanuj ja" jest)
    assert "Zeskanuj" not in wszystkie and "Zmie" not in wszystkie, wszystkie
    assert s.komunikaty("plytka_bez_skanu") == [] and s.ciemna("P")
    # numer podany w pytaniu: komunikat znika, plan dostaje plytke, ramka swieci
    assert s.k.podaj_numer_plytki(skan, 4)
    s.bez_komunikatu("plytka_czeka_na_numer")
    s.plan_na_ramce("P", [4])
    s.swieci("P")
    assert s.nowe() == []
    # bez skanu czekajacego na numer: plytka niezeskanowana na ramce = rada "Zeskanuj" jak dotad (kryterium 4b)
    s.poloz("P", 6)
    assert s.komunikat("plytka_bez_skanu").tekst == tekst("plytka_bez_skanu", na_ramce=6, w_planie=ST.W_PLANIE_PLYTKI.format(plytki="4"))
    assert s.komunikaty("plytka_czeka_na_numer") == []


# --- D2: dwa warunki ochronne (wstrzykniecia recenzenta I7 i I8 nie byly wykrywane) -----------------------------------------------
def test_r2_d2_rano_w_czasie_analizy_bez_komunikatu_o_plytce_bez_skanu(kal, tmp_path, sprzataj):
    """Plytka polozona na ramce P, zanim jej skan trafi do programu (analiza w toku): bez komunikatu ``plytka_bez_skanu`` -
    wynik jest w drodze; komunikat pojawia sie dopiero, gdy program nic nie liczy."""
    s = StanowiskoZRamkami(tmp_path / "k", kal, sprzataj, tryb="rano")
    s.k.symuluj_skan_rano(4, {1: "pewna", 2: "pewna"}, projekty={1: 301, 2: 302}, uklad=RAMKOWA_P, numer_z_dolkow=4)
    s.plan_na_ramce("P", [4])
    s.k.symuluj_kolejke(czeka=1)  # skan plytki 6 w analizie
    assert s.k._zajety() == "analiza_trwa"
    s.poloz("P", 6)
    koniec = time.monotonic() + 0.8
    while time.monotonic() < koniec:
        s.k.przetworz()
        assert s.komunikaty("plytka_bez_skanu") == []
        time.sleep(0.02)
    assert s.ciemna("P")
    s.k.symuluj_kolejke(czeka=0)  # analiza skonczona, a skanu plytki 6 nie ma: teraz rada
    assert s.k._zajety() is None and "nr 6" in s.komunikat("plytka_bez_skanu").tekst


def test_r2_d2_przyczyna_bledu_tylko_dla_bledu_analizy(tmp_path):
    """Przyczyna "w skanie widac N z 3 znacznikow" jest brana z opisu bledu TYLKO przy rodzaju "analiza" (albo bez rodzaju);
    blad innego rodzaju (np. przekroczony czas) z podobnym opisem zachowuje swoj powod."""
    from stanowisko import kontroler_api as K
    from stanowisko import statusy as ST

    k = K.AtrapaKontrolera(tmp_path / "k", zegar=Zegar(dt.datetime(2026, 11, 17, 19, 0, 0)))
    try:
        opis = "BladWyrownania: znaleziono 1 stozki znacznikow, potrzeba 3"
        analiza = _blad_analizy(k, opis)
        assert next(x for x in k.stan().komunikaty if x.id == f"blad_analizy:{analiza}").tekst == tekst(
            "blad_analizy", powod=ST.PRZYCZYNY_BLEDU_ANALIZY["znaczniki"].format(n=1))
        for rodzaj in ("limit_czasu", "proces", "start", "plik_zmieniony"):
            skan = _blad_analizy(k, f"{opis} ({rodzaj})")
            k.sesja.baza.zdarzenie("silnik", "blad_analizy_rodzaj", {"rodzaj": rodzaj}, skan_id=skan, czas=k._teraz())
            k._przyczyny_bledu.clear()
            k._odswiez()
            kom = next(x for x in k.stan().komunikaty if x.id == f"blad_analizy:{skan}")
            assert kom.tekst == tekst("blad_analizy", powod=ST.POWODY_BLEDU_ANALIZY[rodzaj]) and "z 3" not in kom.tekst, rodzaj
    finally:
        k.zamknij()


# --- D1 / D3: zapis pliku kalibracji - plik nigdy w polowie zapisany, bez pliku-smiecia obok --------------------------------------
def test_r2_d1_zapis_kalibracji_przerwany_w_polowie_plik_bajtowo_bez_zmian(tmp_path, monkeypatch):
    """Uzupelnienie pliku kalibracji idzie przez plik tymczasowy i podmiane: zapis przerwany w polowie (brak miejsca, zanik
    zasilania) nie rusza pliku kalibracji; nie zostaje ani plik tymczasowy, ani kopia ``.przed_uzupelnieniem``."""
    plik = tmp_path / "dane" / "kalibracja_ramek.json"
    kalibracja.zapisz(stara_kalibracja(), plik)
    bajty = plik.read_bytes()
    prawdziwy, zapisy = kalibracja.zapisz, []

    def w_polowie(dane, sciezka) -> None:
        prawdziwy(dane, sciezka)
        with open(sciezka, "rb") as f:
            calosc = f.read()
        with open(sciezka, "wb") as f:
            f.write(calosc[:len(calosc) // 2])  # na dysk trafila polowa pliku
        zapisy.append(str(sciezka))
        raise OSError(28, "brak miejsca na dysku")

    monkeypatch.setattr(kalibracja, "zapisz", w_polowie)
    with pytest.raises(OSError):
        kalibracja.uzupelnij_plik(plik, MODELE)
    assert len(zapisy) == 1 and plik.read_bytes() == bajty  # plik kalibracji bajtowo bez zmian
    assert sorted(p.name for p in plik.parent.iterdir()) == [plik.name]  # bez pliku tymczasowego i bez kopii
    # start programu przy takim bledzie: uklady w pamieci + ostrzezenie, plik nadal bez zmian
    kal_, ostrzezenia = IND.wczytaj_kalibracje(plik, MODELE)
    assert RAMKOWA_W in kal_["ramki"]["W"] and RAMKOWA_P in kal_["ramki"]["P"] and any("nie zostal" in o for o in ostrzezenia)
    assert plik.read_bytes() == bajty and sorted(p.name for p in plik.parent.iterdir()) == [plik.name]
    # po ustaniu przyczyny: zwykle uzupelnienie (2 uklady, kopia starego pliku)
    monkeypatch.setattr(kalibracja, "zapisz", prawdziwy)
    _, dopisane = kalibracja.uzupelnij_plik(plik, MODELE)
    assert len(dopisane) == 2 and kalibracja.wczytaj(plik)["ramki"]["W"][RAMKOWA_W]["zrodlo"] == "geometria"
    assert (plik.parent / (plik.name + kalibracja.PRZYROSTEK_KOPII)).read_bytes() == bajty


def test_r2_d3_podmiana_pliku_kalibracji_nieudana_bez_kopii_obok(tmp_path, monkeypatch):
    """Plik kalibracji tylko do odczytu (podmiana odmawia): plik bez zmian, bez pliku tymczasowego i - inaczej niz w rundzie 1 -
    bez kopii ``.przed_uzupelnieniem`` (powstawala przy KAZDYM starcie i mylila przy pozniejszym prawdziwym uzupelnieniu).
    Kopia, ktora juz byla (z wczesniejszego uzupelnienia), zostaje nietknieta."""
    plik = tmp_path / "kalibracja_ramek.json"
    kalibracja.zapisz(stara_kalibracja(), plik)
    bajty = plik.read_bytes()
    proby = []

    def odmowa(zrodlo, cel):
        proby.append((str(zrodlo), str(cel)))
        raise PermissionError(13, "plik tylko do odczytu")

    monkeypatch.setattr(kalibracja.os, "replace", odmowa)
    for _ in range(2):  # dwa starty programu
        kal_, ostrzezenia = IND.wczytaj_kalibracje(plik, MODELE)
        assert RAMKOWA_W in kal_["ramki"]["W"] and any("nie zostal" in o for o in ostrzezenia)
        assert plik.read_bytes() == bajty and sorted(p.name for p in tmp_path.iterdir()) == [plik.name]
    assert len(proby) == 2 and all(cel == str(plik) for _, cel in proby)
    kopia = plik.with_name(plik.name + kalibracja.PRZYROSTEK_KOPII)
    kopia.write_bytes(b"kopia sprzed wczesniejszego uzupelnienia")
    with pytest.raises(PermissionError):
        kalibracja.uzupelnij_plik(plik, MODELE)
    assert kopia.read_bytes() == b"kopia sprzed wczesniejszego uzupelnienia" and plik.read_bytes() == bajty
    assert sorted(p.name for p in tmp_path.iterdir()) == sorted([plik.name, kopia.name])


# =============================================================================================================================
# runda 3 (recenzja PR #55 runda 2): P2 - stan faktyczny wariantu BEZ pytania; P3 - tekst ``dwa_skany_numeru``; P4 - komunikat
# po "Zmien numer"; D6 - dwie galezie ``_czeka_na_ponowny_skan``; D7 - tekst ``plytka_czeka_na_numer``; blad analizy 0 z 3
# =============================================================================================================================
INNE_PRACE = {i: 100 + i for i in range(1, 10)}  # projekty inne niz domyslne skanu sztucznego (projekt = numer gniazda): INNY wsad


@pytest.mark.parametrize("uklad_b, dolki_b", [(RAMKOWA_W, 2), ("wieczorna", None)], ids=["okragla_z_dolkiem_odczytanym_jako_2", "kwadrat_nr_2"])
def test_r3_p2_inna_plytka_nr_2_z_innymi_pracami_bez_pytania_wynik_nowego_skanu_pod_plytka_lezaca_mechanizm_zastany(
        kal, tmp_path, sprzataj, uklad_b, dolki_b):
    """Utrwalenie stanu faktycznego - OGRANICZENIE ZNANE, mechanizm zastany (na ``main`` sprzed paczki to samo dla par kwadrat
    R59 + R54 i dla numeru wpisanego z bledem); DO DECYZJI WLASCICIELA (pozycja nr 1 listy) - po wprowadzeniu twardszej reguly
    ramki ten test ma zostac ODWROCONY (ramka ciemna + komunikat).
    Okragla nr 2 lezy na ramce W i swieci. Technik skanuje INNA plytke, ktorej skan dostaje numer 2 (okragla z dolkiem
    odczytanym jako 2 albo kwadrat nr 2), z INNYMI pracami: co najmniej 3 rozpoznane projekty w kazdym skanie, mniej niz polowa
    wspolnych. Program NIE pyta o ponowny skan (``session._podstawa_ponownego``: to dla niego nowy wsad), wiec wstrzymanie
    z rundy 2 (B1) nie dziala: 0 pytan, 0 komunikatow, a pod plytka LEZACA (z 1. skanu) swieci wynik NOWEGO skanu
    (proby X1, X1b recenzenta). Zasada pracy do decyzji: przed skanem nastepnej plytki zdejmij poprzednia z ramki wieczornej;
    w jednej zmianie nie uzywaj dwoch plytek z tym samym numerem."""
    from stanowisko import session as SE

    s = StanowiskoZRamkami(tmp_path / "k", kal, sprzataj)
    a = s.k.symuluj_skan("czysta", numer=2, uklad=RAMKOWA_W, numer_z_dolkow=2)
    s.poloz("W", 2)
    assert s.swieci_wynik(a) == 4 and s.nowe() == []
    b = s.k.symuluj_skan("zwykla", numer=2, uklad=uklad_b, projekty=INNE_PRACE, numer_z_dolkow=dolki_b)
    z = s.k.sesja.zgodnosc_prac(b, a)
    assert min(z["projekty"], z["projekty_poprzedniego"]) >= SE.PONOWNY_SKAN_MIN_ROZPOZNANYCH and z["wspolne"] == 0
    assert 0 < s.k.sesja.ponowny_skan_min_wspolnych and z["udzial"] < s.k.sesja.ponowny_skan_min_wspolnych
    swieci = s.swieci_wynik(b)  # obraz ramki piksel po pikselu = wynik NOWEGO skanu, a na ramce lezy plytka z 1. skanu
    pikseli = len(TI.roznice_plytki(s.atrapy["W"].klatka, {}))
    assert swieci >= 5 and pikseli > 0 and s.k._w_wynik == (b, 2, "wyslany", None)
    koniec = time.monotonic() + 0.8
    while time.monotonic() < koniec:  # 0 pytan o ponowny skan i 0 komunikatow - takze po chwili
        s.k.przetworz()
        assert [q for q in s.k.stan().pytania if q.rodzaj == "ponowny_skan"] == [] and s.nowe() == []
        time.sleep(0.02)
    stan = s.k.stan()
    assert stan.plytka(b).moze_zastapic is None and stan.plytka(a).aktywna and stan.plytka(b).aktywna
    assert (stan.plytka(a).numer, stan.plytka(b).numer) == (2, 2) and s.ramka("W").plytka == 2
    assert len(TI.roznice_plytki(s.atrapy["W"].klatka, {})) == pikseli
    print(f"\n[E3-O2 runda 3, P2 - mechanizm zastany, do decyzji wlasciciela] okragla n2 lezy na ramce W, skan {uklad_b} z numerem 2 "
          f"i innymi pracami (rozpoznane projekty {z['projekty']} i {z['projekty_poprzedniego']}, wspolne {z['wspolne']}): pytan 0, "
          f"komunikatow 0, pod plytka lezaca swieci wynik nowego skanu: {swieci} gniazd, {pikseli} pikseli")


def test_r3_p3_tekst_dwa_skany_numeru_trzy_rady_wg_kryterium_pytania_te_same_prace():
    """Recenzja rundy 2, P3: pytanie mowi o "tych samych pracach", a komunikat pod nim przestawial kryterium na "te sama
    plytke" - nowy wsad na TEJ SAMEJ plytce (maly, ponizej 3 rozpoznanych projektow = pytanie) prowadzil do "Tak, to ponowny
    skan", czyli do zastapienia skanu poprzedniego wsadu. Tekst ma 3 rady wg kryterium pytania."""
    from stanowisko import statusy as ST

    t = tekst("dwa_skany_numeru", numer=2)
    tak, nie = ST.PRZYCISKI["potwierdz_ponowny_skan"], ST.PRZYCISKI["odrzuc_ponowny_skan"]
    zdania = t.split(". ")

    def zdanie(fragment: str) -> str:
        z = [x for x in zdania if fragment in x]
        assert len(z) == 1, (fragment, t)
        return z[0]

    te_same = zdanie("Te same prace zeskanowane drugi raz")
    nowe = zdanie("Nowe prace na tej samej")
    inna = zdanie("najpierw zdejmij z ramki")
    assert zdania.index(te_same) < zdania.index(nowe) < zdania.index(inna)
    assert tak in te_same and nie not in te_same and "ramka za" in te_same  # te same prace drugi raz: "Tak", ramka zaswieci
    assert nie in nowe and tak not in nowe and "zdejmij" not in nowe and "ramka za" in nowe  # nowy wsad, ta sama plytka: "Nie"
    # na ramce lezy INNA plytka niz ta z ostatniego skanu: najpierw zdejmij, potem "Nie"
    assert "inna p" in inna and nie in inna and tak not in inna and inna.index("najpierw zdejmij z ramki") < inna.index(nie)
    assert "ta sama p" not in t  # kryterium "ta sama plytka zeskanowana drugi raz" (runda 2) - usuniete
    assert (t.count(tak), t.count(nie)) == (1, 2) and "nr 2" in t and "{" not in t and "?" not in t


def _pytanie_otwarte_plytka_2_lezy(s) -> tuple:
    """Okragla nr 2 lezy na ramce W i swieci; drugi skan z numerem 2 i tymi samymi projektami: pytanie otwarte, ramka ciemna,
    komunikat ``dwa_skany_numeru`` (stan wyjsciowy prob X2, X5, X5b recenzenta)."""
    a = s.k.symuluj_skan("czysta", numer=2, uklad=RAMKOWA_W, numer_z_dolkow=2)
    s.poloz("W", 2)
    assert s.swieci_wynik(a) == 4
    b = s.k.symuluj_skan("zwykla", numer=2, uklad=RAMKOWA_W, numer_z_dolkow=2)
    assert len(_pytania_ponowny(s, b)) == 1 and s.ciemna("W", 0.6)
    assert s.komunikat("dwa_skany_numeru").tekst == tekst("dwa_skany_numeru", numer=2)
    assert s.k._w_wynik == (b, None, "bez_numeru", 2)
    return a, b


def test_r3_p4_zmien_numer_przy_otwartym_pytaniu_komunikat_o_dwoch_skanach_znika(kal, tmp_path, sprzataj):
    """Recenzja rundy 2, P4 (proba X5): pytanie otwarte, plytka nr 2 na ramce, komunikat ``dwa_skany_numeru``. Technik poprawia
    numer nowego skanu na 3 ("Zmien numer") - pytanie znika, zostaje komunikat (c) ``numer_niezgodny`` i ciemna ramka. Obraz
    dla ramki sie nie zmienil (numer None przed i po), wiec dotad numer wstrzymany zostawal w ``_w_wynik`` i komunikat "ramka
    czeka na odpowiedz" wisial bez pytania."""
    s = StanowiskoZRamkami(tmp_path / "k", kal, sprzataj)
    a, b = _pytanie_otwarte_plytka_2_lezy(s)
    assert s.k.podaj_numer_plytki(b, 3)
    assert _pytania_ponowny(s, b) == [] and s.k.stan().plytka(b).numer == 3 and s.k.stan().plytka(b).numer_niezgodny
    s.bez_komunikatu("dwa_skany_numeru")
    assert s.k._w_wynik == (b, None, "bez_numeru", None)
    assert s.ciemna("W", 0.8) and s.nowe() == ["numer_niezgodny"]  # jeden komunikat (c); ramka ciemna jak dotad
    assert s.komunikaty("dwa_skany_numeru") == [] and s.k.stan().plytka(a).aktywna


def test_r3_p4_po_zmianie_numeru_plytka_o_nowym_numerze_na_ramce_bez_rady_poloz_plytke_o_starym_numerze(kal, tmp_path, sprzataj):
    """Recenzja rundy 2, P4 (proba X5b): po "Zmien numer" na 3 technik kladzie na ramce plytke nr 3 (te ze skanu). Dotad:
    komunikat (b) "Na ramce lezy plytka nr 3, a ostatni skan to plytka nr 2 ... Poloz na ramce plytke nr 2" (rada falszywa),
    a po ponownym polozeniu plytki nr 2 wracal komunikat o dwoch skanach. Teraz: tylko komunikat (c), ramka ciemna."""
    s = StanowiskoZRamkami(tmp_path / "k", kal, sprzataj)
    a, b = _pytanie_otwarte_plytka_2_lezy(s)
    assert s.k.podaj_numer_plytki(b, 3)
    for numer in (0, 3, 0, 2):
        s.poloz("W", numer)
        koniec = time.monotonic() + 0.8
        while time.monotonic() < koniec:
            s.k.przetworz()
            assert s.komunikaty("plytka_inna_niz_skan") == [] and s.komunikaty("dwa_skany_numeru") == [], (numer, s.nowe())
            time.sleep(0.02)
        assert s.nowe() == ["numer_niezgodny"] and s.ciemna("W", 0.3), numer
    assert _pytania_ponowny(s, b) == [] and s.k._w_wynik[3] is None


def test_r3_d6_poprzedni_skan_spoza_stanu_doby_tez_wstrzymuje_ramke():
    """Recenzja rundy 2, D6 (wstrzykniecie J2 nie bylo wykrywane): pytanie o ponowny skan wskazuje poprzedni skan, ktorego nie
    ma w stanie doby (ponowny skan przez granice 6:00) - ramka czeka na odpowiedz tak samo (wariant bezpieczniejszy)."""
    from types import SimpleNamespace as N

    from stanowisko import kontroler_api as K

    czeka = K.AtrapaKontrolera._czeka_na_ponowny_skan

    def plytka(*pytania, numer=2):
        return N(skan_id=8, numer=numer, pytania=tuple(pytania))

    pytanie = N(rodzaj="ponowny_skan", poprzedni_id=7, ukryte=False)
    spoza_doby = N(plytka=lambda skan_id: None)
    assert czeka(spoza_doby, plytka(pytanie)) is True
    w_stanie = {7: N(skan_id=7, numer=2, aktywna=True)}
    assert czeka(N(plytka=w_stanie.get), plytka(pytanie)) is True
    # bez wstrzymania: poprzedni skan nieaktywny albo z innym numerem, pytanie innego rodzaju, skan bez numeru, brak pytan
    for poprzednia in (N(skan_id=7, numer=2, aktywna=False), N(skan_id=7, numer=3, aktywna=True)):
        assert czeka(N(plytka={7: poprzednia}.get), plytka(pytanie)) is False
    assert czeka(spoza_doby, plytka(N(rodzaj="brak_numeru_plytki", poprzedni_id=7, ukryte=False))) is False
    assert czeka(spoza_doby, plytka(pytanie, numer=None)) is False and czeka(spoza_doby, plytka()) is False


def test_r3_d6_pytanie_o_ponowny_skan_ukryte_ramka_nadal_ciemna_komunikat_zostaje(kal, tmp_path, sprzataj):
    """Recenzja rundy 2, D6 (wstrzykniecie J9 nie bylo wykrywane; proba X2): pytanie ukryte ("Pozniej" przez API - okno nie ma
    takiego przycisku dla tego pytania) nadal wstrzymuje ramke: 0 swiecacych pikseli, komunikat zostaje."""
    s = StanowiskoZRamkami(tmp_path / "k", kal, sprzataj)
    a, b = _pytanie_otwarte_plytka_2_lezy(s)
    assert s.k.zamknij_pytanie(_pytania_ponowny(s, b)[0].id)
    assert _pytania_ponowny(s, b) == []  # pytanie nie jest juz na liscie okienek ...
    assert [q.ukryte for q in s.k.stan().plytka(b).pytania if q.rodzaj == "ponowny_skan"] == [True]  # ... zostaje przy plytce
    assert s.ciemna("W", 1.0) and s.nowe() == ["dwa_skany_numeru"]
    assert s.k._w_wynik == (b, None, "bez_numeru", 2) and s.k.stan().plytka(a).aktywna and s.k.stan().plytka(b).aktywna


def test_r3_d7_rano_dwa_skany_bez_numeru_liczba_mnoga_i_rada_zeskanuj_gdy_plytki_nie_skanowano(kal, tmp_path, sprzataj):
    """Recenzja rundy 2, D7: komunikat ``plytka_czeka_na_numer`` ma drugie zdanie (plytka na ramce moze byc INNA niz ta ze skanu
    bez numeru - wtedy trzeba ja zeskanowac) i liczbe mnoga przy dwoch skanach bez numeru."""
    from stanowisko import statusy as ST

    s = StanowiskoZRamkami(tmp_path / "k", kal, sprzataj, tryb="rano")
    a = s.k.symuluj_skan_rano(None, {1: "pewna", 2: "pewna"}, projekty={1: 301, 2: 302}, uklad="poranna")
    s.czekaj(lambda: s.k._plan_p_dane is not None and s.k._plan_p_dane["pominiete"]["bez_numeru"] == [a], "plan z 1 plytka bez numeru")
    s.poloz("P", 5)
    jeden = s.komunikat("plytka_czeka_na_numer").tekst
    assert jeden == tekst("plytka_czeka_na_numer", na_ramce=5, w_planie=ST.W_PLANIE_BRAK, jest_skan=ST.JEST_SKAN_BEZ_NUMERU[False])
    assert "jest skan bez numeru" in jeden and "wybierz numer 5" in jeden and "{" not in jeden and "?" not in jeden
    assert "jeszcze nie skanowano" in jeden and "zeskanuj j" in jeden and jeden.index("wybierz numer 5") < jeden.index("jeszcze nie skanowano")
    b = s.k.symuluj_skan_rano(None, {3: "pewna"}, projekty={3: 303}, uklad="poranna")
    mnoga = tekst("plytka_czeka_na_numer", na_ramce=5, w_planie=ST.W_PLANIE_BRAK, jest_skan=ST.JEST_SKAN_BEZ_NUMERU[True])
    s.czekaj(lambda: [x.tekst for x in s.komunikaty("plytka_czeka_na_numer")] == [mnoga], "komunikat z liczba mnoga")
    assert s.k._plan_p_dane["pominiete"]["bez_numeru"] == [a, b]
    assert "skany bez numeru" in mnoga and "jest skan bez numeru" not in mnoga and mnoga != jeden and "zeskanuj j" in mnoga
    assert s.komunikaty("plytka_bez_skanu") == [] and s.ciemna("P")


def test_r3_d7_rano_skan_bez_numeru_plytki_spoza_ramki_zostaje_rada_zeskanuj(kal, tmp_path, sprzataj):
    """Recenzja rundy 2, D7 (proba P1f): jedyny skan bez numeru to okragla TESTOWA (jej pytanie o numer ma tylko "9") - plytka
    nr 6 na ramce P nie moze byc plytka z tego skanu, wiec zostaje rada "Zeskanuj plytke nr 6" (``plytka_bez_skanu``), a nie
    "wybierz numer 6 w pytaniu"."""
    from stanowisko import statusy as ST

    s = StanowiskoZRamkami(tmp_path / "k", kal, sprzataj, tryb="rano")
    t = s.k.symuluj_skan_rano(None, {1: "pewna"}, projekty={1: 308}, uklad="okragla_poranna")
    pytania = [q for q in s.k.stan().pytania if q.skan_id == t]
    assert [q.rodzaj for q in pytania] == ["brak_numeru_plytki"] and 6 not in pytania[0].numery
    s.czekaj(lambda: s.k._plan_p_dane is not None and s.k._plan_p_dane["pominiete"]["bez_numeru"] == [t], "plan z plytka testowa bez numeru")
    s.poloz("P", 6)
    assert s.komunikat("plytka_bez_skanu").tekst == tekst("plytka_bez_skanu", na_ramce=6, w_planie=ST.W_PLANIE_BRAK)
    koniec = time.monotonic() + 0.6
    while time.monotonic() < koniec:
        s.k.przetworz()
        assert s.komunikaty("plytka_czeka_na_numer") == []
        time.sleep(0.02)
    assert s.ciemna("P")


def test_r3_blad_analizy_0_z_3_znacznikow_druga_przyczyna_stolik_w_skanie(tmp_path):
    """Dodatek koordynatora (pomiar recenzenta materialow dnia sprzetu: skan z plaskim podlozem >= 150 mm = 11 z 11
    nierozpoznanych, 0 z 3 znacznikow): przy 0 z 3 komunikat podaje druga mozliwa przyczyne (stolik / podloze wokol plytki
    w skanie) i rade "ustaw ciecie skanu powyzej stolika"; przy 1 i 2 z 3 tekst jak dotad."""
    from stanowisko import kontroler_api as K
    from stanowisko import statusy as ST

    k = K.AtrapaKontrolera(tmp_path / "k", zegar=Zegar(dt.datetime(2026, 11, 17, 19, 0, 0)))
    try:
        teksty = {}
        for n in (0, 1, 2):
            skan = _blad_analizy(k, f"BladWyrownania: znaleziono {n} stozki znacznikow, potrzeba 3")
            teksty[n] = next(x for x in k.stan().komunikaty if x.id == f"blad_analizy:{skan}").tekst
            assert f"{n} z 3" in teksty[n] and "{" not in teksty[n] and "?" not in teksty[n]
        assert teksty[0] == tekst("blad_analizy", powod=ST.PRZYCZYNY_BLEDU_ANALIZY["znaczniki_0"])
        assert "stolik" in teksty[0] and "pod\u0142o\u017ce" in teksty[0] and "powy\u017cej stolika" in teksty[0]
        assert "nie mie\u015bci si\u0119 w polu skanera" in teksty[0]  # pierwsza przyczyna zostaje
        for n in (1, 2):
            assert teksty[n] == tekst("blad_analizy", powod=ST.PRZYCZYNY_BLEDU_ANALIZY["znaczniki"].format(n=n))
            assert "stolik" not in teksty[n] and "pod\u0142o\u017c" not in teksty[n]
    finally:
        k.zamknij()
