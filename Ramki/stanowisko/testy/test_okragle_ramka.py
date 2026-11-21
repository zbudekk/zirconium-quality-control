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
import hashlib
import json

import pytest

import test_indicate as TI
import test_session_rano as TSR
from ramka import kalibracja, test_led
from stanowisko import indicate as IND
from stanowisko import ramka_protokol as RP

MODELE = TI.MODELE
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
