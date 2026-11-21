"""Plytki okragle ramkowe n1-n6 w sesji wieczornej i porannej - paczka E3-O2 (21.11.2026).

Uklady ``okragla_ramkowa_wieczorna`` (numery 1, 2, 3) i ``okragla_ramkowa_poranna`` (4, 5, 6) - wbudowane i rozpoznawane
od paczki E3-O1 - maja te same gniazda, stozki i numery co kwadrat R59 i leza na ramkach tak jak kwadrat. Przed E3-O2
sesja znala tylko nazwy ``[okragla_]wieczorna|poranna[_rNN]``: skan plytki ramkowej byl blokowany ("nieznany uklad
plytki"), a rano plytka okragla nie szla do planu ramki.

Kryteria zlecenia E3-O2: (1) wieczor - 3 skany n1-n3 przyjete, 0 blokad trybu; (2, czesc sesji) rano - 3 plytki n4-n6
w planie ramki; (3) plytki testowe n8 / n9 i kwadraty jak dotad; (4, czesc sesji) numer z dolkow spoza numerow ukladu
(np. 0 przy zaslonietych dolkach) = numer nieznany (pytanie o numer jak dla kwadratu), plytka z numerem niezgodnym
z dolkami nie idzie do planu ramki, ale skan zostaje; (5) okragla ramkowa nie zastepuje skanu kwadratu o tym samym
numerze bez pytania i odwrotnie.

Dane w pelni sztuczne (scenariusz ``testy/dane_sesji/rano/se10.json``, pomocnicy z ``test_session_rano``).
"""
from __future__ import annotations

import json

import pytest

import test_session_rano as TSR
from stanowisko import session as SE
from stanowisko import session_rano as SR

RAMKOWA_W = "okragla_ramkowa_wieczorna"
RAMKOWA_P = "okragla_ramkowa_poranna"
PRACE_A = [{"g": 2, "k": [["X11", 0.95]]}, {"g": 3, "k": [["X12", 0.95]]}, {"g": 5, "k": [["X13", 0.95]]}]
PRACE_B = [{"g": 2, "k": [["Y21", 0.95]]}, {"g": 3, "k": [["Y22", 0.95]]}]


@pytest.fixture
def st(tmp_path):
    s = TSR.Stanowisko(tmp_path)
    TSR.wypelnij_indeks(s.sesja.baza)
    yield s
    s.sesja.baza.zamknij()


def wieczor(nr, czas: str, gniazda: list, plytka: str = RAMKOWA_W) -> dict:
    """Skan wieczorny spoza scenariusza (jak ``test_session_rano.rano`` dla poranka)."""
    return {"klucz": f"w{nr}_{czas}_{plytka}", "tryb": "wieczor", "plytka": plytka, "numer": nr, "czas": czas, "gniazda": gniazda}


def rano(nr, czas: str, gniazda: list, plytka: str = RAMKOWA_P) -> dict:
    return {**TSR.rano(nr, czas, gniazda, plytka), "klucz": f"t{nr}_{czas}_{plytka}"}


# --- umowy: nazwa ukladu -----------------------------------------------------------------------------------------------
def test_umowa_czesci_ukladu_zwraca_ramkowa_i_rodzine_kwadratu():
    assert SE.czesci_ukladu(RAMKOWA_W) == {"okragla": True, "ramkowa": True, "typ": "wieczorna", "wersja": ""}
    assert SE.czesci_ukladu(RAMKOWA_P) == {"okragla": True, "ramkowa": True, "typ": "poranna", "wersja": ""}
    # rodzina ukladu ramkowego = rodzina kwadratu R59 (ten sam rozstaw stozkow i gniazda)
    assert SE.rodzina_ukladu(RAMKOWA_W) == SE.rodzina_ukladu("wieczorna") == "wieczorna"
    assert SE.rodzina_ukladu(RAMKOWA_P) == SE.rodzina_ukladu("poranna") == "poranna"
    assert SE.rodzina_ukladu(RAMKOWA_P) != SE.rodzina_ukladu("poranna_r54")
    assert SE.typ_plytki(RAMKOWA_W) == "wieczorna" and SE.typ_plytki(RAMKOWA_P) == "poranna"
    # plytki testowe n8 / n9 i kwadraty: pole ``ramkowa`` jest i ma wartosc False, reszta jak dotad
    for nazwa, okragla, typ, wersja in (("wieczorna", False, "wieczorna", ""), ("poranna_r54", False, "poranna", "_r54"),
                                        ("okragla_wieczorna", True, "wieczorna", ""), ("okragla_poranna_r54", True, "poranna", "_r54")):
        c = SE.czesci_ukladu(nazwa)
        assert c["ramkowa"] is False and (c["okragla"], c["typ"], c["wersja"]) == (okragla, typ, wersja), nazwa
    # nazwa spoza wzoru nadal nieznana (blokada domyka sie na nieznanym)
    for zla in ("ramkowa_wieczorna", "okragla_ramkowa", "okragla_ramkowa_wieczornax", "okragla_ramkowa_wieczorna\n", "kwadratowa_ramkowa_poranna"):
        assert SE.czesci_ukladu(zla) is None and SE.powod_nie_z_trybu(zla, "wieczor") is not None, zla


def test_umowa_numery_i_na_ramce():
    assert SE.numery_ramkowe(RAMKOWA_W) == (1, 2, 3) and SE.numery_ramkowe(RAMKOWA_P) == (4, 5, 6)
    for nazwa in ("wieczorna", "poranna", "okragla_wieczorna", "okragla_poranna", "poranna_r54", "cos", None):
        assert SE.numery_ramkowe(nazwa) is None, nazwa
    assert SR.numery_plytki(RAMKOWA_P) == (4, 5, 6) and SR.na_ramce(RAMKOWA_P) is True
    assert SR.numery_plytki(RAMKOWA_W) is None and SR.na_ramce(RAMKOWA_W) is False  # wieczorna nie lezy na ramce porannej
    # kryterium 3: kwadrat i okragla testowa jak dotad
    assert SR.numery_plytki("poranna") == (4, 5, 6) and SR.na_ramce("poranna") is True and SR.na_ramce("poranna_r54") is True
    assert SR.numery_plytki("okragla_poranna") == (9,) and SR.na_ramce("okragla_poranna") is False
    assert SR.numery_plytki("okragla_poranna_r54") == (9,) and SR.na_ramce("okragla_poranna_r54") is False


# --- kryterium 1: wieczor ----------------------------------------------------------------------------------------------
def test_k1_wieczor_trzy_skany_n1_n3_przyjete_bez_blokady_trybu(st):
    assert SE.powod_nie_z_trybu(RAMKOWA_W, "wieczor") is None and SE.powod_nie_z_trybu(RAMKOWA_P, "rano") is None
    prace = {1: PRACE_A, 2: PRACE_B, 3: [{"g": 4, "k": [["Q46", 0.95]]}]}
    skany = [st.skan(wieczor(n, f"2026-11-17T18:{10 * n}:00", prace[n])) for n in (1, 2, 3)]
    wiersze = [st.skan_wiersz(s) for s in skany]
    assert [w["status"] for w in wiersze] == ["przyjety"] * 3
    assert [(w["uklad"], w["numer_plytki"], w["numer_zrodlo"]) for w in wiersze] == [(RAMKOWA_W, n, "dolki") for n in (1, 2, 3)]
    stan = st.sesja.stan_wieczoru()
    po_id = {s["id"]: s for s in stan["skany"]}
    assert all(po_id[s]["aktywny"] and po_id[s]["powod"] is None for s in skany)
    assert st.liczba("skany WHERE status = ?", (SE.STATUS_PLYTKA_NIE_Z_TRYBU,)) == 0
    # decyzje technika dzialaja jak na kwadracie
    praca = st.praca(skany[0], 2)
    st.sesja.ukruszona(praca)
    assert [x["gniazdo"] for x in st.sesja.do_dofrezowania()] == [2]
    print(f"\n[E3-O2 kryterium 1] wieczor: przyjete {sum(w['status'] == 'przyjety' for w in wiersze)} z 3 skanow n1-n3, blokad trybu 0")


def test_k1_plytka_ramkowa_nie_z_trybu_blokowana_jak_kwadrat(st):
    """Plytka ramkowa PORANNA wieczorem i WIECZORNA rano = ta sama blokada co dla kwadratu (regula trybu bez zmian)."""
    assert SE.powod_nie_z_trybu(RAMKOWA_P, "wieczor") == "plytka poranna w trybie wieczor"
    assert SE.powod_nie_z_trybu(RAMKOWA_W, "rano") == "plytka wieczorna w trybie rano"
    s = st.skan(wieczor(4, "2026-11-17T18:10:00", PRACE_A, plytka=RAMKOWA_P))
    assert st.skan_wiersz(s)["status"] == SE.STATUS_PLYTKA_NIE_Z_TRYBU
    r = st.skan(rano(1, "2026-11-18T07:00:00", PRACE_B, plytka=RAMKOWA_W))
    assert st.skan_wiersz(r)["status"] == SE.STATUS_PLYTKA_NIE_Z_TRYBU


# --- kryterium 2 (czesc sesji): rano ---------------------------------------------------------------------------------
def test_k2_rano_trzy_plytki_n4_n6_w_planie_ramki(st):
    prace = {4: PRACE_A, 5: PRACE_B, 6: [{"g": 4, "k": [["Q46", 0.95]]}]}
    skany = {n: st.skan(rano(n, f"2026-11-18T07:{10 + n}:00", prace[n])) for n in (4, 5, 6)}
    assert all(st.skan_wiersz(s)["status"] == "przyjety" for s in skany.values())
    stan = st.rano.stan_pieca()
    assert all(s["na_ramce"] and s["aktywny"] for s in stan["skany"]) and stan["blokady"] == []
    assert not any("okragla" in x for x in stan["ostrzezenia"])  # to nie jest plytka "poza ramka"
    plan = st.rano.plan_plytek()
    assert sorted(plan["plytki"]) == ["4", "5", "6"] and plan["uklady"] == {str(n): RAMKOWA_P for n in (4, 5, 6)}
    assert plan["skany"] == {str(n): s for n, s in skany.items()}
    assert plan["pominiete"]["poza_ramka"] == [] and plan["pominiete"]["bez_numeru"] == [] and plan["pominiete"]["zdublowane_plytki"] == []
    assert [g["id"] for g in plan["plytki"]["4"]["gniazda"]] == [2, 3, 5] and TSR.waliduj_plan(plan)
    st.rano.zamknij_piec()  # numer 4-6 z dolkow: "Zamknij piec" bez blokady
    print(f"\n[E3-O2 kryterium 2, sesja] rano: w planie ramki {len(plan['plytki'])} z 3 plytek n4-n6, poza ramka {len(plan['pominiete']['poza_ramka'])}")


def test_k2_rano_numer_obowiazkowy_i_tylko_4_6_dla_plytki_ramkowej(st):
    s = st.skan(rano(4, "2026-11-18T07:00:00", PRACE_A), numer=None, numer_zrodlo="nieznany")
    stan = st.rano.stan_pieca()
    assert stan["bez_numeru"] == [s] and any("podaj numer plytki" in b for b in stan["blokady"])  # jak kwadrat: numer blokuje "Zamknij piec"
    assert st.rano.plan_plytek()["pominiete"]["bez_numeru"] == [s]
    for zly in (9, 2, 0, 8):
        with pytest.raises(SE.BladSesji, match="spoza"):
            st.rano.podaj_numer_plytki(s, zly)
    st.rano.podaj_numer_plytki(s, 6)
    assert sorted(st.rano.plan_plytek()["plytki"]) == ["6"] and st.rano.stan_pieca()["blokady"] == []


# --- kryterium 3: plytki testowe n8 / n9 i kwadraty jak dotad -------------------------------------------------------------
def test_k3_okragla_testowa_i_kwadrat_bez_zmian(st):
    w8 = st.skan(wieczor(8, "2026-11-17T18:10:00", PRACE_A, plytka="okragla_wieczorna"))
    w1 = st.skan(wieczor(1, "2026-11-17T18:20:00", PRACE_B, plytka="wieczorna"))
    assert [st.skan_wiersz(s)["status"] for s in (w8, w1)] == ["przyjety", "przyjety"]
    kolo = st.skan(rano(9, "2026-11-18T07:10:00", [{"g": 2, "k": [["Y22", 0.95]]}], plytka="okragla_poranna"))
    kw = st.skan(rano(5, "2026-11-18T07:12:00", [{"g": 2, "k": [["Y21", 0.95]]}], plytka="poranna"))
    stan = st.rano.stan_pieca()
    plan = st.rano.plan_plytek()
    assert plan["pominiete"]["poza_ramka"] == [kolo] and sorted(plan["plytki"]) == ["5"] and plan["skany"] == {"5": kw}
    assert stan["blokady"] == [] and any("okragla" in x and "ramka poranna jej nie pokazuje" in x for x in stan["ostrzezenia"])
    with pytest.raises(SE.BladSesji, match="spoza"):
        st.rano.podaj_numer_plytki(kolo, 4)  # okragla testowa poranna: tylko 9


def test_k3_numer_zero_plytki_testowej_i_kwadratu_zapisany_jak_dotad(st):
    """Normalizacja "numer spoza numerow ukladu = nieznany" dotyczy tylko ukladow ramkowych - reszta bez zmian (kryterium 3)."""
    a = st.skan(wieczor(0, "2026-11-17T18:10:00", PRACE_A, plytka="okragla_wieczorna"))
    b = st.skan(wieczor(7, "2026-11-17T18:20:00", PRACE_B, plytka="wieczorna"))
    assert (st.skan_wiersz(a)["numer_plytki"], st.skan_wiersz(a)["numer_zrodlo"]) == (0, "dolki")
    assert (st.skan_wiersz(b)["numer_plytki"], st.skan_wiersz(b)["numer_zrodlo"]) == (7, "dolki")


# --- kryterium 4 (czesc sesji): numer z dolkow spoza numerow ukladu = nieznany ---------------------------------------------
@pytest.mark.parametrize("numer", [0, 4, 7, 8])
def test_k4_numer_z_dolkow_spoza_ukladu_ramkowego_to_numer_nieznany(st, numer):
    """Zasloniete dolki daja z analizy numer 0 ze zrodlem ``dolki`` (raport E3-O1, 9.3) - to nie jest numer plytki: skan
    zostaje przyjety BEZ numeru (program zapyta o numer jak dla kwadratu), a odczyt dolkow zostaje w pliku wyniku."""
    s = st.skan(wieczor(numer, "2026-11-17T18:10:00", PRACE_A), numer_z_dolkow=numer, bity=[0, 0, 0, 0])
    w = st.skan_wiersz(s)
    assert (w["status"], w["numer_plytki"], w["numer_zrodlo"]) == ("przyjety", None, "nieznany")
    zapisany = json.loads(st.sesja.sciezka_wyniku(s).read_text(encoding="utf-8"))
    assert zapisany["numer"] == numer and zapisany["numer_z_dolkow"] == numer and zapisany["numer_zrodlo"] == "dolki"  # wynik analizy bez zmian
    st.sesja.podaj_numer_plytki(s, 2)
    w = st.skan_wiersz(s)
    assert (w["numer_plytki"], w["numer_zrodlo"]) == (2, "podany")


def test_k4_numer_zero_rano_to_brak_numeru_a_nie_blad(st):
    s = st.skan(rano(0, "2026-11-18T07:00:00", PRACE_A), numer_z_dolkow=0)
    stan = st.rano.stan_pieca()
    assert st.skan_wiersz(s)["numer_plytki"] is None and stan["bez_numeru"] == [s]
    assert not any("spoza plytek porannych" in b for b in stan["blokady"])  # nie "numer 0 spoza 4, 5, 6 - popraw numer", tylko "podaj numer"
    st.rano.podaj_numer_plytki(s, 4)
    assert sorted(st.rano.plan_plytek()["plytki"]) == ["4"]


def test_k4_plan_plytek_wstrzymuje_plytke_z_numerem_niezgodnym_skan_zostaje(st):
    """``plan_plytek(wstrzymane=...)``: skany wskazane przez kontroler (numer podany rozny od waznego numeru z dolkow) nie ida
    do planu ramki (``pominiete.numer_niezgodny``) - ramka dla tej plytki ciemna; skan, prace i "Zamknij piec" bez zmian."""
    a = st.skan(rano(4, "2026-11-18T07:00:00", PRACE_A))
    b = st.skan(rano(5, "2026-11-18T07:05:00", PRACE_B, plytka="poranna"))
    pelny = st.rano.plan_plytek()
    assert sorted(pelny["plytki"]) == ["4", "5"] and pelny["pominiete"]["numer_niezgodny"] == []
    plan = st.rano.plan_plytek(wstrzymane=[a])
    assert sorted(plan["plytki"]) == ["5"] and plan["pominiete"]["numer_niezgodny"] == [a] and "4" not in plan["uklady"]
    assert all(4 not in k["plytki"] for k in plan["kuwety"]) and TSR.waliduj_plan(plan)
    assert st.skan_wiersz(a)["status"] == "przyjety" and st.skan_wiersz(b)["status"] == "przyjety"
    stan = st.rano.stan_pieca()
    assert stan["blokady"] == [] and TSR.klasy(stan, a) == {2: "pewna", 3: "pewna", 5: "pewna"}  # bez twardej blokady
    st.rano.zamknij_piec()


# --- kryterium 5: ponowny skan ---------------------------------------------------------------------------------------
@pytest.mark.parametrize("pierwsza, druga", [("wieczorna", RAMKOWA_W), (RAMKOWA_W, "wieczorna")])
def test_k5_wieczor_okragla_ramkowa_i_kwadrat_o_tym_samym_numerze_pytanie_zamiast_zastapienia(st, pierwsza, druga):
    a = st.skan(wieczor(1, "2026-11-17T18:10:00", PRACE_A, plytka=pierwsza))
    b = st.skan(wieczor(1, "2026-11-17T18:20:00", PRACE_A, plytka=druga))
    # bez pytania nic nie jest zastapione: oba skany aktywne
    assert [st.skan_wiersz(s)["status"] for s in (a, b)] == ["przyjety", "przyjety"] and st.skan_wiersz(b)["zastepuje_id"] is None
    stan = st.sesja.stan_wieczoru()
    propozycje = [(p["skan_id"], p["poprzedni_id"]) for p in stan["do_potwierdzenia"]]
    assert propozycje == [(b, a)]  # program PYTA ("to ponowny skan?") - ta sama rodzina ukladu i numer
    st.sesja.zastap_skan(b)  # dopiero potwierdzenie zastepuje
    assert st.skan_wiersz(a)["status"] == "zastapiony" and st.skan_wiersz(b)["zastepuje_id"] == a


def test_k5_wieczor_inne_prace_to_nowy_wsad_bez_pytania_i_bez_zastapienia(st):
    a = st.skan(wieczor(1, "2026-11-17T18:10:00", PRACE_A, plytka="wieczorna"))
    b = st.skan(wieczor(1, "2026-11-17T18:20:00", [{"g": 2, "k": [["Y21", 0.95]]}, {"g": 3, "k": [["Y22", 0.95]]}, {"g": 4, "k": [["Q46", 0.95]]}]))
    assert [st.skan_wiersz(s)["status"] for s in (a, b)] == ["przyjety", "przyjety"]
    assert st.sesja.stan_wieczoru()["do_potwierdzenia"] == []


@pytest.mark.parametrize("pierwsza, druga", [("poranna", RAMKOWA_P), (RAMKOWA_P, "poranna")])
def test_k5_rano_okragla_ramkowa_i_kwadrat_o_tym_samym_numerze_pytanie_i_brak_w_planie(st, pierwsza, druga):
    a = st.skan(rano(4, "2026-11-18T07:00:00", PRACE_A, plytka=pierwsza))
    b = st.skan(rano(4, "2026-11-18T07:10:00", PRACE_A, plytka=druga))
    assert [st.skan_wiersz(s)["status"] for s in (a, b)] == ["przyjety", "przyjety"]
    stan = st.rano.stan_pieca()
    assert [(p["skan_id"], p["poprzedni_id"]) for p in stan["do_potwierdzenia"]] == [(b, a)]
    assert stan["zdublowane_plytki"] == [4] and any("dwa skany z tym samym numerem" in x for x in stan["blokady"])
    plan = st.rano.plan_plytek()
    assert plan["plytki"] == {} and plan["pominiete"]["zdublowane_plytki"] == [4]  # ramka nie zgaduje, ktora plytka lezy
    st.rano.zastap_skan(b)
    assert st.skan_wiersz(a)["status"] == "zastapiony"
    plan = st.rano.plan_plytek()
    assert sorted(plan["plytki"]) == ["4"] and plan["uklady"] == {"4": druga} and st.rano.stan_pieca()["blokady"] == []
