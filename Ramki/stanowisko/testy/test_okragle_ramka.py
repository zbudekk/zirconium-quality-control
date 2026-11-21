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
NOWE_KOMUNIKATY = ("plytka_nie_z_ramki", "plytka_inna_niz_skan", "plytka_bez_skanu", "numer_niezgodny")


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
            assert kom.tekst == tekst("blad_analizy", powod=ST.PRZYCZYNY_BLEDU_ANALIZY["znaczniki"].format(n=n))
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
