"""aplikacja (E3-A3a): prawdziwy kontroler - scanner -> silnik -> session, bez okien (tryb offscreen, dane sztuczne).

Kryteria odbioru paczki (lista w raporcie ``raporty/E3-A3a_2026-11-17.md``):
  (a) symulator skanera wrzuca skan -> kolory gniazd w stanie rowne wynikowi analizy po decyzjach w 100 % gniazd
      (tu: PRAWDZIWA analiza ``porownaj`` na malej plytce z atrap; ten sam test na danych sztucznych: test_kontroler_api),
  (e) zamkniecie w polowie wieczoru (takze w trakcie analizy i z kolejka) + start: plytki, decyzje, zalegle skany - nic nie
      ginie i nic nie jest policzone dwa razy; takze po awarii bez zamkniecia,
  (f) petla zdarzen Qt bez przerw dluzszych niz 200 ms podczas analizy 10 plytek,
  (g) liczba STL w puli i "odswiez pule": bez projektow skany czekaja,
  (i) fikcyjna nazwa folderu zlecenia: 0 wystapien w logach, komunikatach, dzienniku i plikach wynikow,
  oraz: powtorki po sha16, ``plik_zmieniony``, ``plik_niedostepny``, zabity proces analizy, baza zajeta, kolejnosc zamykania,
  parametry z ustawien, ``main()`` bez Qt na poziomie modulu.
Kryteria (b), (c), (d), (h), (j) sprawdza wspolny test kontraktu ``test_kontroler_api`` (wariant ``aplikacja``).

Analize w procesie silnika zastepuje ``test_kontroler_api.analiza_sztuczna`` (opis plytki zapisany w pliku "skanu");
tylko test (a) uzywa ``porownaj`` (oraz wariant na duzych skanach odniesienia, wlaczany zmiennymi E3A3_DANE_REF
i E3A3_PROJEKTY - bez nich pomijany z opisem). Prog przerwy petli Qt: 200 ms (kryterium); E3A3_LUZNE=1 podnosi go do 1 s na komputerze
obciazonym przez inne sesje - wartosc zmierzona jest wypisywana (pytest -s).
"""
from __future__ import annotations

import ast
import dataclasses
import json
import logging
import logging.handlers
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

import test_kontroler_api as TK
from test_kontroler_api import FOLDER_ZLECENIA, STANOWISKO, StanowiskoAplikacji, kolory

PROG_PRZERWY_S = 1.0 if os.environ.get("E3A3_LUZNE") == "1" else 0.2  # kryterium (f): 200 ms
NAZWISKO_SKANU = "Nazwiskowa Jadwiga"  # P5: fikcyjne nazwisko w nazwie PLIKU skanu (skaner moze nazywac eksport wg zlecenia)
DANE_REF = os.environ.get("E3A3_DANE_REF")
PROJEKTY_REF = os.environ.get("E3A3_PROJEKTY")
BRAK_DANYCH_REF = "wariant na duzych skanach odniesienia: ustaw E3A3_DANE_REF (folder skan_<typ>_n*.stl) i E3A3_PROJEKTY (folder puli)"
WINDOWS = pytest.mark.skipif(os.name != "nt", reason="plik otwarty bez zgody na wspoldzielenie istnieje tylko na Windows")


@pytest.fixture(scope="module", autouse=True)
def _qt_przed_silnikiem():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import PySide6.QtCore  # noqa: F401


@pytest.fixture
def stanowiska(tmp_path):
    """Funkcja ``nowe(**parametry) -> StanowiskoAplikacji`` na wspolnym katalogu (kolejne wywolanie = ponowny start programu);
    wszystkie sa zamykane po tescie."""
    utworzone = []

    def nowe(**parametry):
        st = StanowiskoAplikacji(tmp_path, **parametry)
        utworzone.append(st)
        return st

    yield nowe
    for st in utworzone:
        st.koniec()


def skany_w_bazie(st) -> list[dict]:
    return st.k.sesja.baza.wiersze("SELECT id, sha16, status, plik FROM skany ORDER BY id")


def czekaj_na_pusta_kolejke(st, limit_s: float = 90.0) -> None:
    st.czekaj(lambda: st.stan().kolejka.razem == 0 and st.stan().analiza is None and st.k._skrzynka.empty(), limit_s, "pusta kolejka")


def mierz_kroki(k) -> dict:
    """Pomiar czasu krokow wykonywanych w watku okna (do szukania przyczyny przerw petli Qt): nazwa kroku -> lista czasow [s]."""
    czasy: dict = {}

    def owin(obiekt, nazwa: str, etykieta: str) -> None:
        prawdziwa = getattr(obiekt, nazwa)
        czasy[etykieta] = []

        def mierzona(*a, **kw):
            t0 = time.perf_counter()
            try:
                return prawdziwa(*a, **kw)
            finally:
                czasy[etykieta].append(time.perf_counter() - t0)

        setattr(obiekt, nazwa, mierzona)

    owin(k, "przetworz", "przetworz")
    owin(k, "_zbuduj", "stan z bazy")
    owin(k.sesja, "przyjmij_wynik", "przyjecie wyniku")
    owin(k, "_zapisz_podglad", "wpis podgladu")
    owin(k.sesja, "stan_wieczoru", "stan_wieczoru")
    return czasy


def obraz_plytek(stan) -> list:
    """Plytki ze stanu bez pol, ktore zaleza od chwili budowy stanu (do porownania przed i po restarcie)."""
    return [dataclasses.replace(p, pytania=(), komunikaty=()) for p in stan.plytki]


# ----------------------------------------------------------------------------
# (a) symulator skanera + prawdziwa analiza
# ----------------------------------------------------------------------------
@pytest.fixture(scope="module")
def plytka_z_atrap(korony, tmp_path_factory):
    """Sztuczny skan plytki okraglej wieczornej z 3 atrap koron (generator ``synth``) + folder puli; nazwy fikcyjne."""
    import shutil
    import warnings

    import numpy as np

    from stanowisko import synth, uklad as U

    d = tmp_path_factory.mktemp("aplikacja_a")
    pula = d / "pula" / FOLDER_ZLECENIA
    pula.mkdir(parents=True)
    for i, p in enumerate(korony):
        shutil.copy(p, pula / f"2026-11-17_Fikcja{i}-{['11', '14', '36'][i]}-crown_cad.stl")
    uk = U.wczytaj("okragla_wieczorna")
    op = synth.Opcje.z_toml(plytka="okragla_wieczorna", prace_na_plytce=3, wspolczynnik=(1.22, 1.22), ubytki_na_prace=(0, 1), srednica_ubytku=(0.8, 1.4),
                            poza_uklad=True, pole=100.0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        skan, prawda = synth.generuj_plytke(uk, uk.numery[0], synth.pliki_projektow(pula.parent), np.random.default_rng(41), op, 41)
    plik, _ = synth.zapisz(skan, prawda, d / "skany", "skan_okragla_wieczorna")
    return plik, pula.parent, uk.numery[0]


def test_a_symulator_prawdziwa_analiza_kolory_rowne_wynikowi(plytka_z_atrap, tmp_path):
    """Kryterium (a) na prawdziwym ``porownaj``: plik zapisany w kawalkach jak przez skaner -> stan = wynik analizy, 100 % gniazd."""
    import symulator_skanera as SY
    from stanowisko import aplikacja as AP
    from stanowisko import kontroler_api as K
    from stanowisko import silnik as SI

    plik, pula, numer = plytka_z_atrap
    ust = TK.ustawienia_probne(tmp_path)
    ust["sciezki"]["folder_cyrkon"] = pula.as_posix()
    (tmp_path / "eksport").mkdir()
    k = AP.Aplikacja(ust, parametry_scannera=TK.PARAMETRY_SCANNERA)  # prawdziwa funkcja analizy: stanowisko.porownaj:porownaj
    try:
        k.start()
        assert k.wybierz_operatora("Technik A")
        t0 = time.monotonic()
        SY.zapisz_jak_skaner(plik, tmp_path / "eksport" / FOLDER_ZLECENIA / "eksport_plytki.stl", czas_s=1.0, kawalki=8)
        etapy = []
        k.subskrybuj(lambda z: etapy.append(z.postep.etap) if z.typ == "postep" and z.postep is not None else None)
        while not k.stan().plytki:
            k.przetworz()
            assert time.monotonic() - t0 < 600.0, f"brak wyniku analizy; komunikaty: {[x.tekst for x in k.stan().komunikaty]}"
            time.sleep(0.02)
        czas = time.monotonic() - t0
        s = k.stan()
        p = s.plytki[0]
        wynik = json.loads(k.sesja.sciezka_wyniku(p.skan_id).read_text(encoding="utf-8"))
        assert p.status == "przyjety" and p.uklad == wynik["plytka"] == "okragla_wieczorna" and p.numer == wynik["numer"] == numer
        oczekiwane = K.kolory_oczekiwane(wynik)
        assert len(oczekiwane) == 3 and kolory(p) == oczekiwane  # 100 % gniazd
        assert {g.nr for g in p.gniazda if not g.prace} == set(wynik["gniazda_puste"]) and all(g.status == "pusty" for g in p.gniazda if not g.prace)
        assert len(set(etapy)) >= 3 and s.pula.liczba_stl == 3 and s.komunikaty == () and s.pytania == ()
        praca = p.prace[0]
        assert k.ukruszona(praca.praca_id)
        klucz = (praca.gniazdo, praca.nr_fragmentu)
        assert kolory(k.stan().plytki[0]) == K.kolory_oczekiwane(wynik, {klucz: "ukruszona"}) and len(k.stan().do_dofrezowania) == 1
        sz = k.szczegoly_pracy(praca.praca_id)  # obraz odchylek dla okna: plik podgladu z silnika nalezy do tego skanu
        assert sz.plik_podgladu is not None and praca.gniazdo in SI.wczytaj_podglad(sz.plik_podgladu)
        assert not list(k.katalog_podgladow.glob("*_wynik.json"))  # kopia wyniku z folderem puli usunieta; zostaje plik sesji bez sciezek
        assert FOLDER_ZLECENIA not in k.sesja.sciezka_wyniku(p.skan_id).read_text(encoding="utf-8")
        print(f"\n[kryterium a, prawdziwa analiza] plik -> stan w {czas:.1f} s; prace: {sorted(oczekiwane.items())}")
    finally:
        k.zamknij()


# ----------------------------------------------------------------------------
# (e) zamkniecie i ponowny start
# ----------------------------------------------------------------------------
def test_e_zamkniecie_w_trakcie_analizy_i_ponowny_start(stanowiska):
    """Kryterium (e): zamkniecie w polowie wieczoru - w trakcie analizy, z zadaniami w kolejce i ze skanem zapisanym, gdy
    program nie dzialal; po starcie plytki i decyzje sa odtworzone, zalegle skany dokonczone, kazdy policzony dokladnie raz."""
    from stanowisko import aplikacja as AP

    st = stanowiska()
    assert st.k.wybierz_operatora("Technik A")
    pierwszy, drugi = st.wrzuc("zwykla", numer=1), st.wrzuc("czysta", numer=2, projekty={1: 11, 2: 12, 3: 13, 4: 14})
    p = st.stan().plytka(pierwszy)
    assert st.k.ukruszona(p.gniazdo(2).praca.praca_id) and st.k.ok(p.gniazdo(9).praca.praca_id)
    przed = st.stan()
    brama = st.tmp / "brama_e.txt"  # D13: analiza czeka na plik-brame (nie na uplyw czasu) - zawsze trwa przy zamknieciu
    for i in range(4):  # 4 plytki naraz: pierwsza w analizie, trzy w kolejce
        st.zapisz({"gniazda": {1: "zielony", 2: "czerwony"}, "numer": 3 + i, "projekty": {1: 15 + i, 2: 20 + i}, "brama": str(brama)})
    st.czekaj(lambda: st.stan().analiza is not None and st.stan().kolejka.razem == 4, 60.0, "analiza w toku i 3 zadania w kolejce")
    odp = st.k.zamknij()
    assert odp and odp.dane == 4  # nic nie zdazylo sie policzyc: 4 zadania niezakonczone
    plik_zadan = st.tmp / "dane" / AP.PLIK_ZADAN
    zapisane = json.loads(plik_zadan.read_text(encoding="utf-8"))["zadania"]
    assert len(zapisane) == 4 and all(z["sha16"] and z["tryb"] == "wieczor" for z in zapisane)
    assert not st.k.scanner.dziala() and not st.k.silnik.dziala()
    brama.write_text("otwarta", encoding="utf-8")  # po starcie zadania licza sie bez czekania
    st.zapisz({"gniazda": {5: "zielony"}, "numer": 7, "projekty": {5: 25}})  # skan zapisany, gdy program nie dzialal

    st2 = stanowiska()
    assert not plik_zadan.exists()  # zadania wczytane i zlecone
    czekaj_na_pusta_kolejke(st2)
    po = st2.stan()
    assert obraz_plytek(po)[:2] == obraz_plytek(przed) and po.do_dofrezowania == przed.do_dofrezowania  # plytki i decyzje odtworzone
    assert po.plytka(pierwszy).gniazdo(2).status == "ukruszona" and po.plytka(pierwszy).gniazdo(9).status == "zatwierdzona_ok"
    skany = skany_w_bazie(st2)
    assert len(skany) == 7 and len({s["sha16"] for s in skany}) == 7 and {s["status"] for s in skany} == {"przyjety"}  # 2 + 4 + 1, kazdy raz
    assert sorted(p.numer for p in po.plytki) == [1, 2, 3, 4, 5, 6, 7]
    assert [p.numer for p in po.plytki][2:6] == [3, 4, 5, 6]  # zadania wznowione w kolejnosci sprzed zamkniecia
    assert [k.rodzaj for k in po.komunikaty if k.rodzaj == "wznowiono"] == ["wznowiono"] and "5" in [k for k in po.komunikaty if k.rodzaj == "wznowiono"][0].tekst
    assert po.operator is None  # osoba jest wybierana od nowa po kazdym starcie programu
    assert st2.k.zamknij().dane == 0 and not plik_zadan.exists()

    st3 = stanowiska()  # trzeci start: nic do nadrobienia, nic policzone drugi raz
    for _ in range(40):
        st3.k.przetworz()
        time.sleep(0.02)
    assert len(skany_w_bazie(st3)) == 7 and st3.stan().kolejka.razem == 0 and obraz_plytek(st3.stan()) == obraz_plytek(po)
    assert st3.k.scanner.stan()["zdarzen"] == 0  # zaden plik nie zostal zgloszony ponownie


def test_e_awaria_bez_zamkniecia_nadrabianie_folderu(stanowiska):
    """Awaria (proces okna znika bez ``zamknij``): pliku zadan nie ma, a skany bez wyniku wracaja przez nadrabianie folderu."""
    from stanowisko import aplikacja as AP

    st = stanowiska()
    st.wrzuc("czysta", numer=1)
    brama = st.tmp / "brama_awaria.txt"  # D13: analizy trwaja do awarii niezaleznie od obciazenia komputera
    for i in range(3):
        st.zapisz({"gniazda": {1: "zielony"}, "numer": 2 + i, "projekty": {1: 11 + i}, "brama": str(brama)})
    st.czekaj(lambda: st.stan().kolejka.razem == 3, 60.0, "3 zadania w silniku")
    # symulacja awarii: watki i proces koncza sie, ale kontroler niczego nie zapisuje (jak po zabiciu procesu okna);
    # system zwalnia blokade jednego egzemplarza razem z procesem (B1) - tu robi to test
    st.k.scanner.stop()
    st.k.silnik.stop()
    st.k.sesja.baza.zamknij()
    st.k._zamkniety = True
    st.k._blokada.zwolnij()
    assert not (st.tmp / "dane" / AP.PLIK_ZADAN).exists()
    brama.write_text("otwarta", encoding="utf-8")

    st2 = stanowiska()
    st2.czekaj(lambda: len(st2.stan().plytki) == 4 and st2.stan().kolejka.razem == 0, 90.0, "3 skany nadrobione z folderu")
    for _ in range(30):  # i nic ponad to
        st2.k.przetworz()
        time.sleep(0.02)
    skany = skany_w_bazie(st2)
    assert len(skany) == 4 and len({s["sha16"] for s in skany}) == 4 and {s["status"] for s in skany} == {"przyjety"}
    assert [k.rodzaj for k in st2.stan().komunikaty if k.rodzaj == "wznowiono"] == ["wznowiono"]  # technik widzi, ze program dokancza zalegle skany
    assert sorted(p.numer for p in st2.stan().plytki) == [1, 2, 3, 4]
    assert st2.k.scanner.stan()["zdarzen"] == 3  # plik z wynikiem w bazie nie jest zglaszany ponownie


def test_powtorka_tej_samej_tresci_nie_jest_liczona_dwa_razy(stanowiska):
    """Odsiewanie powtorek po ``sha16``: wobec skanu z wynikiem i wobec zadania w kolejce; skan z bledem wolno liczyc ponownie."""
    st = stanowiska()
    opis = {"gniazda": {1: "zielony", 2: "czerwony"}, "numer": 4}
    plik = st.zapisz(opis)
    czekaj_na_pusta_kolejke(st)
    st.czekaj(lambda: len(st.stan().plytki) == 1, 30.0, "pierwszy skan")
    (st.eksport / "kopia_tego_samego.stl").write_bytes(plik.read_bytes())  # ta sama tresc pod inna nazwa, na zywo
    st.czekaj(lambda: any(k.rodzaj == "skan_juz_jest" for k in st.stan().komunikaty), 30.0, "komunikat o powtorce")
    czekaj_na_pusta_kolejke(st)
    assert len(skany_w_bazie(st)) == 1 and len(st.stan().plytki) == 1
    dziennik = [w["typ"] for w in st.k.sesja.baza.wiersze("SELECT typ FROM zdarzenia WHERE zrodlo = 'scanner' ORDER BY id")]
    assert dziennik.count("nowy_skan") == 2 and dziennik.count("skan_powtorzony") == 1

    brama = st.tmp / "brama_powtorka.txt"  # D13: analiza trwa, dopoki test nie zobaczy powtorki w kolejce
    wolny = st.zapisz({"gniazda": {1: "zielony"}, "numer": 5, "brama": str(brama)})  # w analizie; ta sama tresc drugi raz trafia na zadanie w kolejce
    st.czekaj(lambda: st.stan().analiza is not None, 30.0, "analiza wolnego skanu")
    (st.eksport / "kopia_wolnego.stl").write_bytes(wolny.read_bytes())
    st.czekaj(lambda: st.k.sesja.baza.wiersz("SELECT count(*) AS n FROM zdarzenia WHERE typ = 'skan_powtorzony_w_kolejce'")["n"] == 1, 30.0,
              "powtorka odsiana w kolejce")
    brama.write_text("otwarta", encoding="utf-8")
    czekaj_na_pusta_kolejke(st)
    st.czekaj(lambda: len(st.stan().plytki) == 2, 30.0, "drugi skan")
    for _ in range(30):
        st.k.przetworz()
        time.sleep(0.02)
    assert len(skany_w_bazie(st)) == 2 and st.k.scanner.stan()["zdarzen"] == 4  # 4 zdarzenia skanera, 2 skany w bazie

    bledny = st.zapisz({"gniazda": {}, "blad": True, "numer": 6})
    st.czekaj(lambda: len(st.stan().plytki) == 3 and st.stan().plytki[-1].status == "blad", 30.0, "skan z bledem")
    (st.eksport / "kopia_blednego.stl").write_bytes(bledny.read_bytes())  # skan z bledem NIE ma wyniku: powtorka jest liczona
    st.czekaj(lambda: len(st.stan().plytki) == 4, 30.0, "ponowna analiza skanu z bledem")
    assert [s["status"] for s in skany_w_bazie(st)] == ["przyjety", "przyjety", "blad", "blad"]


# ----------------------------------------------------------------------------
# (f) petla zdarzen Qt
# ----------------------------------------------------------------------------
def test_f_petla_qt_bez_przerw_podczas_analizy_10_plytek(stanowiska):
    """Kryterium (f): podczas analizy 10 plytek (przyjecie wyniku, zapis w bazie, nowy stan - w watku okna) petla zdarzen Qt
    nie ma przerw dluzszych niz 200 ms. Zegar co 10 ms mierzy najdluzsza przerwe; ``lacznik_qt`` sam wola ``przetworz``."""
    from PySide6.QtCore import QEventLoop, QTimer
    from PySide6.QtWidgets import QApplication

    from stanowisko import kontroler_api as K

    app = QApplication.instance() or QApplication([])
    assert app.platformName() == "offscreen"
    st = stanowiska()
    assert st.k.wybierz_operatora("Technik A")
    lacznik = K.lacznik_qt(st.k, okres_ms=30)
    stany, postepy = [], []
    lacznik.stan_zmieniony.connect(stany.append)
    lacznik.postep.connect(postepy.append)
    petla = QEventLoop()
    pomiar = {"ostatni": 0.0, "przerwa": 0.0, "tykniec": 0, "decyzji": 0, "odmowy": []}

    def tyk():
        teraz = time.perf_counter()
        pomiar["przerwa"] = max(pomiar["przerwa"], teraz - pomiar["ostatni"])
        pomiar["ostatni"] = teraz
        pomiar["tykniec"] += 1
        s = st.k.stan()
        if len(s.plytki) > pomiar["decyzji"]:  # jak technik w trakcie analizy kolejnych plytek: decyzja na swiezo policzonej plytce
            odp = st.k.ukruszona(s.plytki[pomiar["decyzji"]].gniazdo(2).praca.praca_id)
            if not odp:
                pomiar["odmowy"].append(odp.tekst)
            pomiar["decyzji"] += 1
        if (len(s.plytki) == 10 and s.kolejka.razem == 0 and pomiar["decyzji"] == 10) or pomiar["odmowy"]:
            petla.quit()

    zegar = QTimer()
    zegar.setInterval(10)
    zegar.timeout.connect(tyk)
    QTimer.singleShot(180_000, petla.quit)
    for i in range(10):  # 10 plytek po 19 prac, kazda "liczona" 0,3 s w procesie silnika
        st.zapisz({"gniazda": {n: ("czerwony" if n == 2 else "zielony") for n in range(1, 20)}, "numer": 1 + i,
                   "projekty": {n: 100 * (i + 1) + n for n in range(1, 20)}, "spij": 0.3})
    pomiar["ostatni"] = time.perf_counter()
    zegar.start()
    t0 = time.perf_counter()
    petla.exec()
    czas = time.perf_counter() - t0
    zegar.stop()
    lacznik.zatrzymaj()
    s = st.k.stan()
    print(f"\n[kryterium f] 10 plytek w {czas:.1f} s, najdluzsza przerwa petli Qt {pomiar['przerwa'] * 1000:.0f} ms (prog {PROG_PRZERWY_S * 1000:.0f} ms), "
          f"tykniec zegara {pomiar['tykniec']}, sygnalow stanu {len(stany)}, postepu {len(postepy)}")
    assert not pomiar["odmowy"], pomiar["odmowy"]
    assert len(s.plytki) == 10 and all(p.status == "przyjety" and len(p.prace) == 19 for p in s.plytki) and pomiar["decyzji"] == 10
    assert len(s.do_dofrezowania_biezaca) == 10
    assert pomiar["tykniec"] >= 100 and len(postepy) >= 20 and len(stany) >= 20  # petla naprawde pracowala, okno dostawalo postep i stan
    assert pomiar["przerwa"] <= PROG_PRZERWY_S


# ----------------------------------------------------------------------------
# (g) pula projektow
# ----------------------------------------------------------------------------
def test_g_bez_projektow_skany_czekaja_do_odswiezenia_puli(stanowiska, tmp_path):
    """Kryterium (g): liczba STL i "odswiez pule" w stanie; pusta pula nie daje bledu analizy - skany czekaja."""
    st = stanowiska()
    assert st.stan().pula.liczba_stl == 3 and st.stan().pula.stan == "gotowa" and "3" in st.stan().pula.napis
    pusta = tmp_path / "pusta_pula"
    pusta.mkdir()
    assert st.k.ustaw_pule(str(pusta), None)
    st.czekaj(lambda: st.stan().pula.stan == "pusta", 30.0, "pusta pula policzona")
    assert st.stan().pula.liczba_stl == 0
    st.zapisz({"gniazda": {1: "zielony"}, "numer": 1})
    st.zapisz({"gniazda": {1: "czerwony"}, "numer": 2, "projekty": {1: 12}})
    st.czekaj(lambda: st.stan().kolejka.wstrzymane == 2, 30.0, "2 skany wstrzymane")
    s = st.stan()
    k = [k for k in s.komunikaty if k.rodzaj == "pula_pusta"]
    assert len(k) == 1 and "2" in k[0].tekst and s.plytki == () and skany_w_bazie(st) == []
    assert st.k.ustaw_pule(str(tmp_path / "nie_ma_takiego_folderu"), None)
    st.czekaj(lambda: st.stan().pula.stan == "brak_folderu", 30.0, "brak folderu puli")
    assert [k.rodzaj for k in st.stan().komunikaty if k.id == "pula"] == ["pula_brak_folderu"] and st.stan().pula.liczba_stl is None

    odp = st.k.ustaw_pule(str(pusta), 7.5)  # zly wspolczynnik: odmowa, nic sie nie zmienia
    assert not odp and odp.kod == "zly_wspolczynnik" and st.stan().pula.stan == "brak_folderu"
    (pusta / "Fikcja-21-crown_cad.stl").write_bytes(TK.plik_skanu({"projekt": 21}))
    (pusta / "_pobrane").mkdir()
    (pusta / "_pobrane" / "pomijany.stl").write_bytes(TK.plik_skanu({"projekt": 22}))  # foldery _* nie naleza do puli (jak synth.pliki_projektow)
    assert st.k.ustaw_pule(str(pusta), 1.21)
    st.czekaj(lambda: len(st.stan().plytki) == 2 and st.stan().kolejka.razem == 0, 60.0, "skany wstrzymane policzone")
    s = st.stan()
    assert s.pula.liczba_stl == 1 and s.pula.stan == "gotowa" and s.pula.wspolczynnik == pytest.approx(1.21) and s.pula.folder == str(pusta)
    assert not [k for k in s.komunikaty if k.id == "pula"] and [p.numer for p in s.plytki] == [1, 2]
    wynik = json.loads(st.k.sesja.sciezka_wyniku(s.plytki[0].skan_id).read_text(encoding="utf-8"))
    assert wynik["wspolczynnik"] == pytest.approx(1.21)  # analiza dostala wspolczynnik wpisany w oknie
    st.k.zamknij()

    st2 = stanowiska()  # folder i wspolczynnik wpisane przez technika przezywaja restart
    assert st2.stan().pula.folder == str(pusta) and st2.stan().pula.wspolczynnik == pytest.approx(1.21) and st2.stan().pula.liczba_stl == 1


# ----------------------------------------------------------------------------
# bledy pliku i analizy
# ----------------------------------------------------------------------------
def test_plik_zmieniony_przed_analiza(stanowiska):
    st = stanowiska()
    brama = st.tmp / "brama_zmieniony.txt"  # D13: drugi skan na pewno czeka w kolejce, gdy jest nadpisywany
    st.zapisz({"gniazda": {1: "zielony"}, "numer": 1, "brama": str(brama)})
    st.czekaj(lambda: st.stan().analiza is not None, 30.0, "analiza pierwszego skanu")
    drugi = st.zapisz({"gniazda": {1: "zielony"}, "numer": 2, "projekty": {1: 12}})
    st.czekaj(lambda: st.stan().kolejka.razem == 2, 30.0, "drugi skan w kolejce")
    drugi.write_bytes(TK.plik_skanu({"gniazda": {1: "czerwony"}, "numer": 3, "projekty": {1: 13}, "sol": "nowa tresc"}))  # zapis ponowny przed analiza
    brama.write_text("otwarta", encoding="utf-8")
    czekaj_na_pusta_kolejke(st)
    st.czekaj(lambda: len(st.stan().plytki) == 2, 30.0, "dwa skany w stanie")
    s = st.stan()
    assert [p.numer for p in s.plytki] == [1, 3] and [k.rodzaj for k in s.komunikaty if k.rodzaj == "plik_zmieniony"] == ["plik_zmieniony"]
    assert len(skany_w_bazie(st)) == 2  # stara tresc nie dostala ani wyniku, ani skanu "blad"
    assert st.k.sesja.baza.wiersz("SELECT count(*) AS n FROM zdarzenia WHERE typ = 'plik_zmieniony'")["n"] == 1


@WINDOWS
def test_plik_niedostepny_ponawianie_i_blad(stanowiska, tmp_path):
    """Plik skanu trzymany przez inny program bez zgody na odczyt: ``plik_niedostepny`` -> komunikat i ponowienie; po zwolnieniu
    wynik; plik trzymany do konca ponowien -> skan ``blad`` z komunikatem ``plik_niedostepny`` (nic nie ginie po cichu)."""
    import symulator_skanera as SY

    ust = TK.ustawienia_probne(tmp_path)
    ust["silnik"].update(czekaj_na_plik_s=0.4, ponow_plik_niedostepny=2)
    st = stanowiska(ust=ust)
    assert st.k.silnik.czekaj_na_plik_s == pytest.approx(0.4) and st.k.ponow_plik_niedostepny == 2

    brama1, brama2 = st.tmp / "brama_n1.txt", st.tmp / "brama_n2.txt"  # D13: plik zablokowany, zanim silnik po niego siegnie
    st.zapisz({"gniazda": {1: "zielony"}, "numer": 1, "brama": str(brama1)})
    st.czekaj(lambda: st.stan().analiza is not None, 30.0, "analiza pierwszego skanu")
    plik = st.zapisz({"gniazda": {1: "czerwony"}, "numer": 2, "projekty": {1: 12}})
    st.czekaj(lambda: st.stan().kolejka.razem == 2, 30.0, "drugi skan w kolejce")
    uchwyt = SY.otworz_wylacznie(plik, zapis=False)  # jak podglad w programie skanera: nikt inny nie przeczyta pliku
    brama1.write_text("otwarta", encoding="utf-8")
    try:
        st.czekaj(lambda: any(k.rodzaj == "plik_niedostepny" for k in st.stan().komunikaty), 60.0, "komunikat plik_niedostepny")
        k = [k for k in st.stan().komunikaty if k.rodzaj == "plik_niedostepny"][0]
        assert "2 z 3" in k.tekst and not k.trwaly and st.stan().kolejka.razem == 1  # zlecony ponownie, nadal czeka
    finally:
        uchwyt.close()
    st.czekaj(lambda: len(st.stan().plytki) == 2 and st.stan().kolejka.razem == 0, 60.0, "wynik po zwolnieniu pliku")
    s = st.stan()
    assert [p.status for p in s.plytki] == ["przyjety", "przyjety"] and not [k for k in s.komunikaty if k.rodzaj == "plik_niedostepny"]

    plik = st.zapisz({"gniazda": {1: "zielony"}, "numer": 3, "projekty": {1: 13}, "brama": str(brama2)})
    st.czekaj(lambda: st.stan().analiza is not None, 30.0, "analiza trzeciego skanu")
    trzymany = st.zapisz({"gniazda": {1: "zielony"}, "numer": 4, "projekty": {1: 14}})
    st.czekaj(lambda: st.stan().kolejka.razem == 2, 30.0, "czwarty skan w kolejce")
    uchwyt = SY.otworz_wylacznie(trzymany, zapis=False)
    brama2.write_text("otwarta", encoding="utf-8")
    try:
        st.czekaj(lambda: len(st.stan().plytki) == 4 and st.stan().kolejka.razem == 0, 90.0, "skan z bledem po 3 probach")
    finally:
        uchwyt.close()
    s = st.stan()
    assert [p.status for p in s.plytki] == ["przyjety", "przyjety", "przyjety", "blad"]
    k = [k for k in s.komunikaty if k.rodzaj == "plik_niedostepny"]
    assert len(k) == 1 and k[0].trwaly and k[0].skan_id == s.plytki[-1].skan_id and "ponownie" in k[0].tekst
    assert trzymany.name not in json.dumps(dataclasses.asdict(s), default=str)  # nazwa pliku skanu nie trafia do stanu


def test_zabity_proces_analizy_komunikat_i_nastepny_skan(stanowiska):
    st = stanowiska()
    st.zapisz({"gniazda": {1: "zielony"}, "numer": 1, "zabij": True})
    st.zapisz({"gniazda": {1: "czerwony"}, "numer": 2, "projekty": {1: 12}})
    st.czekaj(lambda: len(st.stan().plytki) == 2 and st.stan().kolejka.razem == 0, 90.0, "blad procesu i nastepny skan")
    s = st.stan()
    assert [p.status for p in s.plytki] == ["blad", "przyjety"] and s.plytki[1].gniazdo(1).status == "czerwony"
    k = [k for k in s.komunikaty if k.rodzaj == "blad_analizy"]
    assert len(k) == 1 and "przerwana" in k[0].tekst and k[0].skan_id == s.plytki[0].skan_id
    wpis = st.k.sesja.baza.wiersz("SELECT dane FROM zdarzenia WHERE typ = 'blad_analizy_rodzaj'")
    assert json.loads(wpis["dane"]) == {"rodzaj": "proces"}


def test_baza_zajeta_wynik_nie_ginie(stanowiska, monkeypatch):
    """Baza zajeta przez inny program w chwili przyjecia wyniku: wynik czeka w pamieci i jest zapisywany przy nastepnej probie."""
    from stanowisko import aplikacja as AP
    from stanowisko import baza as B

    monkeypatch.setattr(AP, "OKRES_KONTROLI_S", 0.2)
    st = stanowiska()
    prawdziwe = st.k.sesja.przyjmij_wynik
    proby = []

    def zajeta(*a, **kw):
        proby.append(time.monotonic())
        if len(proby) <= 2:
            raise B.BladBazy("stanowisko.sqlite: baza jest zajeta przez inny program")
        return prawdziwe(*a, **kw)

    monkeypatch.setattr(st.k.sesja, "przyjmij_wynik", zajeta)
    st.zapisz({"gniazda": {1: "zielony", 2: "czerwony"}, "numer": 1})
    st.czekaj(lambda: len(proby) >= 1, 30.0, "pierwsza proba zapisu")
    s = st.stan()
    assert s.plytki == () and s.kolejka.wstrzymane == 1 and [k.rodzaj for k in s.komunikaty] == ["baza_zajeta"]
    st.czekaj(lambda: len(st.stan().plytki) == 1, 30.0, "wynik zapisany po zwolnieniu bazy")
    assert len(proby) == 3 and st.stan().komunikaty == () and st.stan().kolejka.razem == 0 and len(skany_w_bazie(st)) == 1


def test_plik_odrzucony_i_plik_zajety_w_stanie(stanowiska):
    """Plik, ktory nie jest skanem: komunikat bez nazwy pliku; plik zajety w folderze skanera: "czeka na zwolnienie"."""
    st = stanowiska()
    zly = st.eksport / "uciety_plik_skanu.stl"
    zly.write_bytes(TK.plik_skanu({"gniazda": {1: "zielony"}})[:-20])
    (st.eksport / "notatka.txt").write_text("to nie skan", encoding="utf-8")
    st.czekaj(lambda: any(k.rodzaj == "plik_odrzucony" for k in st.stan().komunikaty), 30.0, "komunikat o odrzuconym pliku")
    s = st.stan()
    assert len([k for k in s.komunikaty if k.rodzaj == "plik_odrzucony"]) == 1 and s.plytki == ()  # plik spoza wzorca nie daje komunikatu
    assert "uciety_plik_skanu" not in json.dumps(dataclasses.asdict(s), ensure_ascii=False, default=str)
    assert st.k.zamknij_komunikat([k for k in s.komunikaty if k.rodzaj == "plik_odrzucony"][0].id) and st.stan().komunikaty == ()
    if os.name != "nt":
        return
    import symulator_skanera as SY

    zajety = st.eksport / "zajety.stl"
    with SY.otworz_wylacznie(zajety, zapis=True) as f:  # skaner trzyma plik bez zgody na odczyt
        f.write(TK.plik_skanu({"gniazda": {1: "zielony"}, "numer": 1, "sol": "zajety"}))
        f.flush()
        st.czekaj(lambda: any(k.rodzaj == "plik_zajety" for k in st.stan().komunikaty), 30.0, "komunikat czeka na zwolnienie")
        assert st.stan().skaner.zajete == 1 and st.stan().plytki == ()
    st.czekaj(lambda: len(st.stan().plytki) == 1, 30.0, "skan po zwolnieniu pliku")
    assert not [k for k in st.stan().komunikaty if k.rodzaj == "plik_zajety"] and st.stan().skaner.zajete == 0


def test_silnik_nie_startuje_skan_czeka_i_wraca_po_restarcie(stanowiska):
    """Proces analizy nie umie wystartowac (brak pakietu, zly plik): skan NIE dostaje bledu - czeka, technik widzi komunikat,
    a po zamknieciu i poprawnym starcie programu skan jest policzony (nic nie ginie)."""
    st = stanowiska(funkcja_analizy="nie_ma_takiego_modulu_analizy:funkcja")
    st.zapisz({"gniazda": {1: "zielony", 2: "czerwony"}, "numer": 1})
    st.czekaj(lambda: any(k.rodzaj == "silnik_nie_startuje" for k in st.stan().komunikaty), 90.0, "komunikat o silniku")
    s = st.stan()
    assert s.plytki == () and s.kolejka.wstrzymane == 1 and not s.kolejka.silnik_gotowy and skany_w_bazie(st) == []
    st.zapisz({"gniazda": {1: "zielony"}, "numer": 2, "projekty": {1: 12}})  # kolejne skany tez czekaja
    st.czekaj(lambda: st.stan().kolejka.wstrzymane == 2, 30.0, "drugi skan wstrzymany")
    assert st.k.zamknij().dane == 2

    st2 = stanowiska()  # program uruchomiony ponownie z dzialajaca analiza
    st2.czekaj(lambda: len(st2.stan().plytki) == 2 and st2.stan().kolejka.razem == 0, 90.0, "skany policzone po restarcie")
    assert [p.numer for p in st2.stan().plytki] == [1, 2] and {s["status"] for s in skany_w_bazie(st2)} == {"przyjety"}
    assert not [k for k in st2.stan().komunikaty if k.rodzaj == "silnik_nie_startuje"]


def test_folder_skanera_pojawia_sie_pozniej(tmp_path):
    """Folderu skanera nie ma przy starcie (dysk niepodlaczony): komunikat w stanie; gdy folder sie pojawi - komunikat znika,
    a skan zapisany potem jest analizowany."""
    from stanowisko import aplikacja as AP

    TK.pula_probna(tmp_path)
    k = AP.Aplikacja(TK.ustawienia_probne(tmp_path), funkcja_analizy=TK.FUNKCJA_SZTUCZNA, parametry_scannera=TK.PARAMETRY_SCANNERA)

    def czekaj(warunek, co: str, limit_s: float = 60.0) -> None:
        koniec = time.monotonic() + limit_s
        while not warunek():
            k.przetworz()
            assert time.monotonic() < koniec, f"nie doczekalem sie: {co}; komunikaty {[x.rodzaj for x in k.stan().komunikaty]}"
            time.sleep(0.02)

    try:
        k.start()
        czekaj(lambda: any(x.rodzaj == "folder_skanera_niedostepny" for x in k.stan().komunikaty), "komunikat o braku folderu")
        assert not k.stan().skaner.dostepny and k.stan().skaner.dziala
        (tmp_path / "eksport").mkdir()
        czekaj(lambda: k.stan().skaner.dostepny and not [x for x in k.stan().komunikaty if x.rodzaj == "folder_skanera_niedostepny"], "folder widoczny")
        (tmp_path / "eksport" / "skan_po_podlaczeniu.stl").write_bytes(TK.plik_skanu({"gniazda": {1: "zielony"}, "numer": 1}))
        czekaj(lambda: len(k.stan().plytki) == 1, "skan z folderu, ktory pojawil sie pozniej")
        assert k.stan().plytki[0].status == "przyjety"
    finally:
        k.zamknij()


def test_odrzucona_propozycja_ponownego_skanu_nie_wraca_po_restarcie(stanowiska):
    st = stanowiska()
    assert st.k.wybierz_operatora("Technik A")
    pierwszy, drugi = st.wrzuc("czysta", numer=3), st.wrzuc("czysta", numer=3)
    assert [q.rodzaj for q in st.stan().pytania] == ["ponowny_skan"] and st.k.odrzuc_ponowny_skan(drugi) and st.stan().pytania == ()
    st.k.zamknij()
    st2 = stanowiska()
    s = st2.stan()
    assert len(s.plytki) == 2 and s.pytania == () and s.plytka(drugi).moze_zastapic == pierwszy  # propozycja jest, pytanie nie wraca
    wpis = st2.k.sesja.baza.wiersz("SELECT dane, skan_id FROM zdarzenia WHERE typ = 'ponowny_skan_odrzucony'")
    assert wpis["skan_id"] == drugi and json.loads(wpis["dane"]) == {"operator": "Technik A", "poprzedni_id": pierwszy}
    assert st2.k.wybierz_operatora("Technik B") and st2.k.potwierdz_ponowny_skan(drugi)  # zmiana zdania: zastapienie wprost nadal dziala
    assert st2.stan().plytka(pierwszy).status == "zastapiony"


# ----------------------------------------------------------------------------
# runda 2 recenzji PR #20: B1, P1, P2, P3, P8, P9 i dodatkowe punkty awarii kryterium (e)
# ----------------------------------------------------------------------------
def _dziennik(st, typ: str) -> int:
    return st.k.sesja.baza.wiersz("SELECT count(*) AS n FROM zdarzenia WHERE typ = ?", (typ,))["n"]


def test_b1_drugi_egzemplarz_odmawia_i_nie_dotyka_bazy(stanowiska, tmp_path):
    """B1: drugi egzemplarz programu na tej samej bazie (dwuklik dwa razy, drugi pulpit) odmawia startu z komunikatem
    "program juz dziala" i nie dotyka bazy, logu ani folderu skanera; kazdy skan jest liczony raz. Drugi ``main()`` (osobny
    proces, jak drugi dwuklik): kod wyjscia 3 bez sladu wyjatku."""
    from stanowisko import aplikacja as AP

    st = stanowiska()
    baza = st.k.sesja.baza
    zdarzen = baza.wiersz("SELECT count(*) AS n FROM zdarzenia")["n"]
    with pytest.raises(AP.ProgramJuzDziala, match="juz dziala"):  # druga Aplikacja w tym samym procesie
        AP.Aplikacja(st.ust, funkcja_analizy=TK.FUNKCJA_SZTUCZNA, parametry_scannera=TK.PARAMETRY_SCANNERA)
    plik = _plik_ustawien(tmp_path)  # te same sciezki danych i folderu skanera, co stanowisko probne
    w = subprocess.run([sys.executable, "-m", "stanowisko.aplikacja", "--ustawienia", str(plik), "--zamknij-po", "5"], cwd=STANOWISKO,
                       capture_output=True, text=True, timeout=180, env={**os.environ, "QT_QPA_PLATFORM": "offscreen"})
    assert w.returncode == AP.KOD_PROGRAM_JUZ_DZIALA and "juz dziala" in w.stderr and "Traceback" not in w.stderr, w.stdout + w.stderr
    assert baza.wiersz("SELECT count(*) AS n FROM zdarzenia")["n"] == zdarzen  # zaden egzemplarz nie dopisal nic do bazy
    assert not (tmp_path / "dane" / "logi" / AP.PLIK_LOGU).exists()  # drugi main() nie zalozyl nawet logu
    st.zapisz({"gniazda": {1: "zielony", 2: "czerwony"}, "numer": 1})
    st.czekaj(lambda: len(st.stan().plytki) == 1, 60.0, "skan")
    for _ in range(30):
        st.k.przetworz()
        time.sleep(0.02)
    assert len(skany_w_bazie(st)) == 1 and len(st.stan().plytki) == 1 and _dziennik(st, "nowy_skan") == 1


def test_b1_blokada_znika_razem_z_procesem(tmp_path):
    """B1: blokada jest odporna na awarie - program zabity w trakcie pracy (bez zamkniecia) nie zostawia blokady; kolejny
    start dziala bez recznego sprzatania."""
    from stanowisko import aplikacja as AP
    from stanowisko import baza as B

    plik = _plik_ustawien(tmp_path)
    TK.pula_probna(tmp_path)
    (tmp_path / "eksport").mkdir()
    plik_bazy = tmp_path / "dane" / "stanowisko.sqlite"
    proces = subprocess.Popen([sys.executable, "-m", "stanowisko.aplikacja", "--ustawienia", str(plik), "--zamknij-po", "300"], cwd=STANOWISKO,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env={**os.environ, "QT_QPA_PLATFORM": "offscreen"})
    try:
        koniec = time.monotonic() + 120.0
        while True:  # pierwszy egzemplarz pracuje: wpis program_start w dzienniku
            if plik_bazy.exists():
                try:
                    with B.otworz(plik_bazy, tylko_odczyt=True) as b:
                        if b.wiersz("SELECT id FROM zdarzenia WHERE typ = 'program_start'"):
                            break
                except B.BladBazy:
                    pass
            assert proces.poll() is None and time.monotonic() < koniec, "pierwszy egzemplarz nie wystartowal"
            time.sleep(0.2)
        with pytest.raises(AP.ProgramJuzDziala):
            AP.BlokadaStanowiska(plik_bazy).zajmij()
        proces.kill()  # awaria: proces znika bez zamkniecia programu
        proces.wait(60)
    finally:
        if proces.poll() is None:
            proces.kill()
            proces.wait(60)
    blokada = AP.BlokadaStanowiska(plik_bazy).zajmij()  # system zwolnil blokade razem z procesem
    assert blokada.zajeta
    blokada.zwolnij()
    k = AP.Aplikacja(TK.ustawienia_probne(tmp_path), funkcja_analizy=TK.FUNKCJA_SZTUCZNA, parametry_scannera=TK.PARAMETRY_SCANNERA)
    k.zamknij()


def test_b1_wynik_skanu_juz_zapisanego_nie_daje_drugiego_skanu(stanowiska):
    """B1, twarde zabezpieczenie w zapisie: gdy ta sama tresc (``sha16``) dostala wynik w bazie w trakcie analizy (np. drugi
    program piszacy do tej bazy), wynik kontrolera jest odsiewany w tej samej transakcji co zapis - jeden skan, bez
    osieroconego pliku podgladu."""
    from stanowisko import baza as B
    from stanowisko import kontroler_api as K
    from stanowisko import session as SE

    st = stanowiska()
    brama = st.tmp / "brama_b1.txt"
    plik = st.zapisz({"gniazda": {1: "zielony"}, "numer": 1, "brama": str(brama), "podglad": True})
    st.czekaj(lambda: st.stan().analiza is not None, 30.0, "analiza w toku")
    sha16 = st.stan().analiza.sha16
    with B.otworz(st.k.sesja.baza.plik) as inna:  # "drugi program": osobne polaczenie z ta sama baza
        SE.Sesja(inna, katalog_wynikow=st.tmp / "dane" / "wyniki_inne", zegar=st.zegar).przyjmij_wynik(
            {"plik": str(plik), "sha16": sha16, "rozmiar": plik.stat().st_size, "czas_pliku": None}, K.sztuczny_wynik("wieczorna", 1, {1: "zielony"}))
    brama.write_text("otwarta", encoding="utf-8")
    czekaj_na_pusta_kolejke(st)
    st.czekaj(lambda: _dziennik(st, "wynik_powtorzony") == 1, 30.0, "wynik odsiany")
    assert len(skany_w_bazie(st)) == 1 and len(st.stan().plytki) == 1 and st.stan().niezapisane == ()
    assert not list(st.k.katalog_podgladow.glob("*")), [p.name for p in st.k.katalog_podgladow.glob("*")]  # P9: podglad odsianego wyniku usuniety


def test_p1_blad_zapisu_skan_nie_znika_i_jest_zapisywany_ponownie(stanowiska, monkeypatch):
    """P1: blad zapisu inny niz "baza zajeta" (pelny dysk: ``database or disk is full``; blad zapisu pliku wyniku: ``OSError``)
    - skan NIE znika: pozycja "nie zapisano - blad zapisu" i komunikat TRWALY ``blad_zapisu``; zapis ponawiany sam (rosnacy
    odstep) i na zadanie (``ponow_zapis``); po ustaniu przyczyny skan jest w bazie raz, komunikat znika. Zamkniecie z wynikiem
    niezapisanym: zadanie wraca do pliku zadan, w ``dane/podglady`` nic nie zostaje."""
    from stanowisko import aplikacja as AP
    from stanowisko import kontroler_api as K

    monkeypatch.setattr(AP, "OKRES_KONTROLI_S", 0.2)
    st = stanowiska()
    dysk = {"blad": sqlite3.OperationalError("database or disk is full"), "proby": 0}

    def pelny(prawdziwa):
        def zapis(*a, **kw):
            if dysk["blad"] is not None:
                dysk["proby"] += 1
                raise dysk["blad"]
            return prawdziwa(*a, **kw)
        return zapis

    monkeypatch.setattr(st.k.sesja, "przyjmij_wynik", pelny(st.k.sesja.przyjmij_wynik))
    monkeypatch.setattr(st.k.sesja, "przyjmij_blad", pelny(st.k.sesja.przyjmij_blad))
    st.zapisz({"gniazda": {1: "zielony", 2: "czerwony"}, "numer": 1, "podglad": True})
    st.czekaj(lambda: st.stan().niezapisane, 30.0, "pozycja nie zapisano")
    s = st.stan()
    assert s.plytki == () and skany_w_bazie(st) == [] and len(s.niezapisane) == 1
    n = s.niezapisane[0]
    assert (n.przyczyna, n.rodzaj, n.numer, n.uklad, n.prac) == ("blad_zapisu", "wynik", 1, "wieczorna", 2) and "nie zapisano" in n.napis
    k = [x for x in s.komunikaty if x.id == K.ID_BLAD_ZAPISU]
    assert len(k) == 1 and k[0].rodzaj == "blad_zapisu" and k[0].trwaly and k[0].poziom == "blad"
    assert s.kolejka.niezapisane == 1 and s.kolejka.wstrzymane == 1 and not list(st.k.katalog_podgladow.glob("*_wynik.json"))
    st.czekaj(lambda: dysk["proby"] >= 3, 30.0, "samoczynne ponowienia")
    assert st.stan().plytki == () and st.stan().niezapisane[0].proby >= 3
    odp = st.k.ponow_zapis()
    assert not odp and odp.kod == "blad_zapisu" and odp.dane == 1
    dysk["blad"] = None  # dysk zwolniony: nastepne samoczynne ponowienie zapisuje
    st.czekaj(lambda: len(st.stan().plytki) == 1, 30.0, "zapis po ustaniu przyczyny")
    s = st.stan()
    assert s.niezapisane == () and not [x for x in s.komunikaty if x.rodzaj in ("blad_zapisu", "baza_zajeta")] and s.kolejka.razem == 0
    assert [x["status"] for x in skany_w_bazie(st)] == ["przyjety"] and s.plytki[0].gniazdo(2).status == "czerwony"
    assert st.k.szczegoly_pracy(s.plytki[0].gniazdo(1).praca.praca_id).plik_podgladu is not None  # podglad powiazany przy zapisie

    monkeypatch.setattr(AP, "OKRES_KONTROLI_S", 600.0)  # samoczynne ponowienie daleko: tylko na zadanie
    dysk["blad"] = OSError(28, "No space left on device")
    st.zapisz({"gniazda": {1: "zielony"}, "numer": 2, "projekty": {1: 12}})
    st.czekaj(lambda: st.stan().niezapisane, 30.0, "drugi skan nie zapisany")
    dysk["blad"] = None
    odp = st.k.ponow_zapis()
    assert odp and odp.dane == 0 and len(st.stan().plytki) == 2 and st.stan().niezapisane == ()

    dysk["blad"] = sqlite3.OperationalError("disk I/O error")
    st.zapisz({"gniazda": {1: "zielony"}, "numer": 3, "projekty": {1: 13}, "podglad": True})
    st.czekaj(lambda: st.stan().niezapisane, 30.0, "trzeci skan nie zapisany")
    assert st.k.zamknij().dane == 1  # nie przepadl: zadanie wraca do pliku zadan i liczy sie od nowa po starcie
    assert len(json.loads((st.tmp / "dane" / AP.PLIK_ZADAN).read_text(encoding="utf-8"))["zadania"]) == 1
    zostalo = sorted(p.name for p in st.k.katalog_podgladow.iterdir())
    assert len(zostalo) == 1 and zostalo[0].endswith("_podglad.npz"), zostalo  # tylko podglad zapisanego skanu nr 1


def test_p2_plik_przemianowany_w_kolejce_przejmuje_zadanie(stanowiska, monkeypatch):
    """P2: plik skanu przemianowany, gdy czeka w kolejce (zapis pod nazwa robocza, technik poprawia nazwe) - nowa sciezka tej
    samej tresci przejmuje zadanie: skan przyjety (nie "blad analizy"), w bazie nowa sciezka. Takze gdy silnik zdazyl siegnac
    po stara sciezke ("brak pliku" - zadanie zlecone ponownie z nowa)."""
    st = stanowiska()
    brama = st.tmp / "brama_p2a.txt"
    st.zapisz({"gniazda": {1: "zielony"}, "numer": 1, "brama": str(brama)})
    st.czekaj(lambda: st.stan().analiza is not None, 30.0, "analiza pierwszego skanu")
    b = st.zapisz({"gniazda": {1: "czerwony"}, "numer": 2, "projekty": {1: 12}})
    st.czekaj(lambda: st.stan().kolejka.razem == 2, 30.0, "drugi skan w kolejce")
    os.replace(b, st.eksport / "docelowa_nazwa.stl")
    st.czekaj(lambda: _dziennik(st, "skan_przemianowany") == 1, 30.0, "zadanie przejelo nowa sciezke")
    brama.write_text("otwarta", encoding="utf-8")
    czekaj_na_pusta_kolejke(st)
    st.czekaj(lambda: len(st.stan().plytki) == 2, 30.0, "dwa skany")
    s = st.stan()
    assert [p.status for p in s.plytki] == ["przyjety", "przyjety"] and not [k for k in s.komunikaty if k.rodzaj in ("blad_analizy", "skan_juz_jest")]
    assert Path(skany_w_bazie(st)[1]["plik"]).name == "docelowa_nazwa.stl" and s.plytki[1].gniazdo(1).status == "czerwony"

    monkeypatch.setattr(st.k.silnik, "anuluj", lambda nr: False)  # zadanie juz u silnika: przejecie dopiero po bledzie "brak pliku"
    brama2 = st.tmp / "brama_p2b.txt"
    st.zapisz({"gniazda": {1: "zielony"}, "numer": 3, "projekty": {1: 13}, "brama": str(brama2)})
    st.czekaj(lambda: st.stan().analiza is not None, 30.0, "analiza trzeciego skanu")
    c = st.zapisz({"gniazda": {1: "zielony"}, "numer": 4, "projekty": {1: 14}})
    st.czekaj(lambda: st.stan().kolejka.razem == 2, 30.0, "czwarty skan w kolejce")
    os.replace(c, st.eksport / "docelowa_2.stl")
    st.czekaj(lambda: _dziennik(st, "skan_powtorzony_w_kolejce") == 2, 30.0, "nowa sciezka zauwazona")
    brama2.write_text("otwarta", encoding="utf-8")
    st.czekaj(lambda: len(st.stan().plytki) == 4 and st.stan().kolejka.razem == 0, 60.0, "cztery skany")
    assert [p.status for p in st.stan().plytki] == ["przyjety"] * 4 and _dziennik(st, "skan_przemianowany") == 2
    assert Path(skany_w_bazie(st)[3]["plik"]).name == "docelowa_2.stl" and not [k for k in st.stan().komunikaty if k.rodzaj == "blad_analizy"]


def test_p3_pula_oprozniona_po_policzeniu_skany_czekaja(stanowiska):
    """P3: pula policzona przy starcie, potem folder oprozniony: skany NIE dostaja "blad analizy" - pula jest liczona od nowa
    (przy nowym skanie i po bledzie analizy), stan ``pusta``, licznik 0, skany ``wstrzymane`` z komunikatem; po powrocie
    plikow i "Odswiez pule" skany sa liczone. Blad analizy przy niepustej puli nadal jest bledem."""
    st = stanowiska()
    assert (st.stan().pula.stan, st.stan().pula.liczba_stl) == ("gotowa", 3)
    for p in Path(st.folder_puli).rglob("*.stl"):
        p.unlink()
    st.zapisz({"gniazda": {1: "zielony"}, "numer": 1})
    st.zapisz({"gniazda": {1: "czerwony"}, "numer": 2, "projekty": {1: 12}})
    st.czekaj(lambda: st.stan().kolejka.wstrzymane == 2 and st.stan().pula.stan == "pusta" and st.stan().kolejka.razem == 2, 60.0, "skany czekaja")
    s = st.stan()
    assert s.plytki == () and skany_w_bazie(st) == [] and s.pula.liczba_stl == 0 and "0" in s.pula.napis
    k = [x for x in s.komunikaty if x.id == "pula"]
    assert [x.rodzaj for x in k] == ["pula_pusta"] and "2" in k[0].tekst and not [x for x in s.komunikaty if x.rodzaj == "blad_analizy"]
    TK.pula_probna(st.tmp)  # pliki wrocily
    assert st.k.odswiez_pule()
    st.czekaj(lambda: len(st.stan().plytki) == 2 and st.stan().kolejka.razem == 0, 60.0, "skany policzone")
    s = st.stan()
    assert [p.status for p in s.plytki] == ["przyjety", "przyjety"] and (s.pula.stan, s.pula.liczba_stl) == ("gotowa", 3)
    assert not [x for x in s.komunikaty if x.id == "pula"]
    st.zapisz({"gniazda": {}, "blad": True, "numer": 9})
    st.czekaj(lambda: len(st.stan().plytki) == 3 and st.stan().kolejka.razem == 0, 60.0, "blad analizy po sprawdzeniu puli")
    assert st.stan().plytki[-1].status == "blad" and [x.rodzaj for x in st.stan().komunikaty if x.rodzaj == "blad_analizy"] == ["blad_analizy"]


def test_p8_blad_analizy_przy_zajetej_bazie_ponawiany_bez_ponownej_analizy(stanowiska, monkeypatch):
    """P8: blad analizy, gdy baza jest zajeta - skan nie czeka bez konca na "Odswiez pule": zapis bledu jest ponawiany sam
    (rosnacy odstep, bez ponownej analizy), komunikat ``baza_zajeta`` znika po udanym zapisie."""
    from stanowisko import aplikacja as AP
    from stanowisko import baza as B

    monkeypatch.setattr(AP, "OKRES_KONTROLI_S", 0.2)
    st = stanowiska()
    prawdziwe, proby = st.k.sesja.przyjmij_blad, []

    def zajeta(*a, **kw):
        proby.append(time.monotonic())
        if len(proby) <= 2:
            raise B.BladBazy("stanowisko.sqlite: baza jest zajeta przez inny program")
        return prawdziwe(*a, **kw)

    monkeypatch.setattr(st.k.sesja, "przyjmij_blad", zajeta)
    st.zapisz({"gniazda": {1: "zielony"}, "numer": 1, "zabij": True})  # proces analizy znika: blad "proces"
    st.czekaj(lambda: len(proby) >= 1, 60.0, "pierwsza proba zapisu bledu")
    s = st.stan()
    assert s.plytki == () and [k.rodzaj for k in s.komunikaty] == ["baza_zajeta"] and [(n.rodzaj, n.przyczyna) for n in s.niezapisane] == [("blad", "baza_zajeta")]
    st.czekaj(lambda: len(st.stan().plytki) == 1, 30.0, "blad zapisany po zwolnieniu bazy")
    s = st.stan()
    assert len(proby) == 3 and s.plytki[0].status == "blad" and [k.rodzaj for k in s.komunikaty] == ["blad_analizy"]
    assert s.kolejka.razem == 0 and s.niezapisane == () and _dziennik(st, "blad_analizy_rodzaj") == 1 and len(skany_w_bazie(st)) == 1


def test_p9_kopie_wynikow_i_podglady_nie_zostaja(stanowiska, monkeypatch):
    """P9: kopia wyniku z silnika (zawiera folder puli) nie zostaje w ``dane/podglady`` po przyjeciu ani po bledzie przyjecia
    (wtedy znika tez plik podgladu); pliki osierocone po awarii sa usuwane przy starcie, plik podgladu skanu z bazy zostaje."""
    st = stanowiska()
    podglady = st.k.katalog_podgladow
    st.zapisz({"gniazda": {1: "zielony", 2: "czerwony"}, "numer": 1, "podglad": True})
    st.czekaj(lambda: len(st.stan().plytki) == 1, 60.0, "pierwszy skan")
    p = st.stan().plytki[0]
    podglad = st.k.szczegoly_pracy(p.gniazdo(1).praca.praca_id).plik_podgladu
    assert podglad is not None and sorted(x.name for x in podglady.iterdir()) == [podglad.name]

    def zly_wynik(*a, **kw):
        raise ValueError("wynik niezgodny z oczekiwanym")  # blad danych: ponowienie nic nie da

    monkeypatch.setattr(st.k.sesja, "przyjmij_wynik", zly_wynik)
    st.zapisz({"gniazda": {1: "zielony"}, "numer": 2, "projekty": {1: 12}, "podglad": True})
    st.czekaj(lambda: len(st.stan().plytki) == 2 and st.stan().kolejka.razem == 0, 60.0, "skan z bledem przyjecia")
    assert st.stan().plytki[1].status == "blad" and sorted(x.name for x in podglady.iterdir()) == [podglad.name]
    monkeypatch.undo()
    st.k.zamknij()
    (podglady / "20261117_190000_aaaaaaaaaaaaaaaa_wynik.json").write_text('{"foldery_projektow": ["X"]}', encoding="utf-8")  # po awarii
    (podglady / "20261117_190000_bbbbbbbbbbbbbbbb_podglad.npz").write_bytes(b"x")
    st2 = stanowiska()
    assert sorted(x.name for x in podglady.iterdir()) == [podglad.name]
    assert st2.k.szczegoly_pracy(p.gniazdo(1).praca.praca_id).plik_podgladu == podglad


def test_e_dodatkowe_punkty_awarii(stanowiska):
    """Kryterium (e), punkty awarii poza zamknieciem w trakcie analizy (recenzja D14): (1) silnik oddal wynik i zapisal pliki,
    kontroler go nie przyjal - awaria: po starcie skan liczony raz, pliki osierocone usuniete; (2) awaria przy starcie, po
    zleceniu zadan, przed usunieciem pliku zadan - zadanie, ktore ma juz wynik, nie jest liczone drugi raz, a nowe - raz."""
    import hashlib

    from stanowisko import aplikacja as AP

    st = stanowiska()
    st.wrzuc("czysta", numer=1)
    brama = st.tmp / "brama_e2.txt"
    st.zapisz({"gniazda": {1: "zielony"}, "numer": 2, "projekty": {1: 12}, "podglad": True, "brama": str(brama)})
    st.czekaj(lambda: st.stan().analiza is not None, 60.0, "analiza u silnika")
    brama.write_text("otwarta", encoding="utf-8")  # od teraz bez przetworz(): wynik dojdzie do kolejki silnika, kontroler go nie przyjmie
    koniec = time.monotonic() + 60.0
    while not any(e.typ == "wynik" for e in list(st.k.silnik.zdarzenia.queue)):  # wynik czeka w kolejce - kontroler go NIE przyjmuje
        assert time.monotonic() < koniec, "brak wyniku w kolejce silnika"
        time.sleep(0.02)
    assert list(st.k.katalog_podgladow.glob("*_wynik.json")) and list(st.k.katalog_podgladow.glob("*_podglad.npz"))
    st.k.scanner.stop()  # awaria (jak w test_e_awaria_bez_zamkniecia): nic nie zostaje zapisane, system zwalnia blokade
    st.k.silnik.stop()
    st.k.sesja.baza.zamknij()
    st.k._zamkniety = True
    st.k._blokada.zwolnij()

    st2 = stanowiska()
    st2.czekaj(lambda: len(st2.stan().plytki) == 2 and st2.stan().kolejka.razem == 0, 90.0, "skan nadrobiony")
    skany = skany_w_bazie(st2)
    assert len(skany) == 2 and len({s["sha16"] for s in skany}) == 2 and {s["status"] for s in skany} == {"przyjety"}
    assert not list(st2.k.katalog_podgladow.glob("*_wynik.json")) and len(list(st2.k.katalog_podgladow.glob("*_podglad.npz"))) == 1
    st2.k.zamknij()

    # (2) plik zadan zostal po starcie: jedno zadanie juz ma wynik w bazie (skan nr 2), drugie - skan zapisany potem
    nowy = st2.zapisz({"gniazda": {1: "zielony"}, "numer": 3, "projekty": {1: 13}})
    dane, stat = nowy.read_bytes(), nowy.stat()
    zadania = [{"plik": skany[1]["plik"], "sha16": skany[1]["sha16"], "rozmiar": None, "mtime_ns": None, "trojkaty": 1, "tryb": "wieczor", "numer": None},
               {"plik": str(nowy), "sha16": hashlib.sha256(dane).hexdigest()[:16], "rozmiar": stat.st_size, "mtime_ns": stat.st_mtime_ns,
                "trojkaty": 1, "tryb": "wieczor", "numer": None}]
    (st2.tmp / "dane" / AP.PLIK_ZADAN).write_text(json.dumps({"wersja": 1, "zadania": zadania}), encoding="utf-8")
    st3 = stanowiska()
    st3.czekaj(lambda: len(st3.stan().plytki) == 3 and st3.stan().kolejka.razem == 0, 90.0, "zadanie z pliku zadan")
    for _ in range(30):
        st3.k.przetworz()
        time.sleep(0.02)
    skany = skany_w_bazie(st3)
    assert len(skany) == 3 and len({s["sha16"] for s in skany}) == 3 and st3.k.scanner.stan()["zdarzen"] == 0
    assert not (st3.tmp / "dane" / AP.PLIK_ZADAN).exists() and not [k for k in st3.stan().komunikaty if k.rodzaj == "skan_juz_jest"]


# ----------------------------------------------------------------------------
# (i) nazwy zlecen nie wychodza poza 4 tabele
# ----------------------------------------------------------------------------
def test_i_fikcyjna_nazwa_folderu_zlecenia_nie_wychodzi(stanowiska, tmp_path, caplog):
    """Kryterium (i): fikcyjna nazwa folderu zlecenia jest nazwa podfolderu puli (pliki projektow) ORAZ podfolderu w folderze
    skanera (zlecenie w programie skanera), a fikcyjne nazwisko - nazwa PLIKU skanu (P5: skaner moze nazywac eksport wg
    zlecenia); po wieczorze z wynikami, bledami, decyzjami i restartem: 0 wystapien w logach (takze wpisy ``scanner``
    i ``silnik``), komunikatach (caly stan), dzienniku, plikach wynikow, podgladach i liscie "do dofrezowania"."""
    from stanowisko import aplikacja as AP
    from stanowisko import baza as B

    caplog.set_level(logging.DEBUG)
    ust = TK.ustawienia_probne(tmp_path)
    plik_logu = AP.konfiguruj_logi(ust, logging.DEBUG)
    zrzuty = []
    try:
        st = stanowiska(ust=ust)
        st.k.subskrybuj(lambda z: zrzuty.append(json.dumps(dataclasses.asdict(z), ensure_ascii=False, default=str)))
        assert st.k.wybierz_operatora("Technik A")
        st.zapisz({"gniazda": TK.ZESTAW_ZWYKLY, "numer": 1}, FOLDER_ZLECENIA)
        st.zapisz({"gniazda": {}, "blad": True}, FOLDER_ZLECENIA)  # wyjatek analizy z nazwa folderu puli w tresci
        st.zapisz({"gniazda": {1: "zielony"}, "numer": None}, FOLDER_ZLECENIA)
        st.zapisz({"gniazda": {1: "zielony"}, "uklad": "poranna", "numer": 2}, FOLDER_ZLECENIA)
        nazwisko = st.eksport / FOLDER_ZLECENIA / f"{NAZWISKO_SKANU} plytka 3.stl"  # P5: plik skanu nazwany wg zlecenia
        nazwisko.write_bytes(TK.plik_skanu({"gniazda": {1: "czerwony", 2: "zielony"}, "numer": 3, "projekty": {1: 13, 2: 14}, "sol": "nazwisko"}))
        (st.eksport / FOLDER_ZLECENIA / f"{NAZWISKO_SKANU} uciety.stl").write_bytes(TK.plik_skanu({"x": 1})[:-7])
        st.czekaj(lambda: len(st.stan().plytki) == 5 and st.stan().kolejka.razem == 0
                  and any(k.rodzaj == "plik_odrzucony" for k in st.stan().komunikaty), 90.0, "5 skanow i odrzucony plik")
        p = next(x for x in st.stan().plytki if x.numer == 1)
        zablokowana = next(x for x in st.stan().plytki if x.status == "plytka_nie_z_trybu")
        assert sorted(x.status for x in st.stan().plytki) == ["blad", "plytka_nie_z_trybu", "przyjety", "przyjety", "przyjety"]
        assert st.k.ukruszona(p.gniazdo(2).praca.praca_id) and st.k.ok(p.gniazdo(9).praca.praca_id)
        assert st.k.ukruszona(next(x for x in st.stan().plytki if x.numer == 3).gniazdo(1).praca.praca_id)
        assert not st.k.ukruszona(zablokowana.prace[0].praca_id)  # odmowa sesji (skan zablokowany) jako komunikat
        st.k.szczegoly_pracy(p.gniazdo(7).praca.praca_id)
        assert st.k.zapisz_liste() and st.k.zapisz_liste(st.stan().doba)  # P7: przez kontroler (plik i tak zapisany samoczynnie)
        brama = tmp_path / "brama_i.txt"
        st.zapisz({"gniazda": {1: "zielony"}, "numer": 5, "brama": str(brama)}, FOLDER_ZLECENIA)
        st.czekaj(lambda: st.stan().analiza is not None, 30.0, "analiza w toku przed zamknieciem")
        st.k.zamknij()
        brama.write_text("otwarta", encoding="utf-8")
        st2 = stanowiska(ust=ust)
        st2.k.subskrybuj(lambda z: zrzuty.append(json.dumps(dataclasses.asdict(z), ensure_ascii=False, default=str)))
        czekaj_na_pusta_kolejke(st2)
        assert len(st2.stan().plytki) == 6
        stan = json.dumps(dataclasses.asdict(st2.stan()), ensure_ascii=False, default=str)
        zrzut = st2.k.sesja.baza.zrzut()
        st2.k.zamknij()
    finally:
        AP.odlacz_logi(plik_logu)
    assert not [h for h in logging.getLogger().handlers if isinstance(h, logging.handlers.RotatingFileHandler) and Path(h.baseFilename) == plik_logu]
    szukane = (FOLDER_ZLECENIA, "Zmyslona", "Fikcja", "crown_cad", NAZWISKO_SKANU, "Nazwiskowa")  # folder, jego czlony, pliki puli, plik skanu
    miejsca = {"log (caplog)": caplog.text, "stan koncowy": stan, "sygnaly kontrolera": "\n".join(zrzuty),
               "dziennik": json.dumps(zrzut["zdarzenia"], ensure_ascii=False), "decyzje": json.dumps(zrzut["decyzje"], ensure_ascii=False),
               "prace": json.dumps(zrzut["prace"], ensure_ascii=False)}
    for plik in sorted((tmp_path / "dane").rglob("*")):
        if plik.is_file() and plik.suffix in (".log", ".json", ".csv") and plik.name != AP.PLIK_ZADAN:
            miejsca[f"plik {plik.relative_to(tmp_path).as_posix()}"] = plik.read_text(encoding="utf-8", errors="replace")
        assert not any(s in plik.name for s in szukane), plik.name  # takze nazwy plikow wynikow i podgladow
    assert any(m.startswith("plik dane/logi/stanowisko.log") for m in miejsca) and any("wynik.json" in m for m in miejsca)
    assert "nowy skan" in miejsca["plik dane/logi/stanowisko.log"] and "skan_przyjety" in miejsca["dziennik"]  # miejsca naprawde zawieraja tresc
    sha_nazwiska = next(s["sha16"] for s in zrzut["skany"] if NAZWISKO_SKANU in (s["plik"] or "") and s["status"] == "przyjety")
    assert sha_nazwiska in miejsca["log (caplog)"] and "plik pominiety: <plik>" in miejsca["log (caplog)"]  # P5: skrot zamiast nazwy pliku
    assert any(m.startswith("plik dane/do_dofrezowania_") for m in miejsca)  # lista "do dofrezowania" (P7) tez sprawdzona
    assert "blad_analizy" in miejsca["dziennik"] and len(zrzut["zdarzenia"]) >= 15 and len(zrzuty) >= 10
    wystapienia = {m: [s for s in szukane if s in tekst] for m, tekst in miejsca.items()}
    assert not {m: w for m, w in wystapienia.items() if w}, wystapienia
    # nazwa zostaje tylko tam, gdzie wolno: skany.plik (sciezka skanu, kolumna z planu) - i nigdzie indziej w tabelach bez nazw
    assert any(FOLDER_ZLECENIA in (s["plik"] or "") for s in zrzut["skany"])
    for tabela in set(B.TABELE) - set(B.TABELE_Z_NAZWAMI) - {"skany"}:
        assert FOLDER_ZLECENIA not in json.dumps(zrzut[tabela], ensure_ascii=False), tabela


# ----------------------------------------------------------------------------
# zamykanie, ustawienia, plik startowy
# ----------------------------------------------------------------------------
def test_kolejnosc_zamykania_scanner_przed_silnikiem(stanowiska, monkeypatch):
    """``silnik.md``: najpierw ``scanner.stop()``, potem ``silnik.stop()`` - zadne zlecenie w trakcie zatrzymywania silnika."""
    st = stanowiska()
    kolejnosc = []
    stop_scannera, stop_silnika, zamknij_baze = st.k.scanner.stop, st.k.silnik.stop, st.k.sesja.baza.zamknij
    monkeypatch.setattr(st.k.scanner, "stop", lambda *a, **kw: (kolejnosc.append("scanner"), stop_scannera(*a, **kw))[1])
    monkeypatch.setattr(st.k.silnik, "stop", lambda *a, **kw: (kolejnosc.append("silnik"), stop_silnika(*a, **kw))[1])
    monkeypatch.setattr(st.k.sesja.baza, "zamknij", lambda: (kolejnosc.append("baza"), zamknij_baze())[1])
    st.zapisz({"gniazda": {1: "zielony"}, "numer": 1, "brama": str(st.tmp / "brama_nigdy.txt")})  # D13: analiza trwa do zamkniecia
    st.czekaj(lambda: st.stan().analiza is not None, 30.0, "analiza w toku")
    watki_przed = {w.name for w in threading.enumerate()}
    assert {"scanner", "silnik-nadzorca"} <= watki_przed
    pid = st.k.silnik.pid
    assert pid is not None and st.k.zamknij().dane == 1
    assert kolejnosc == ["scanner", "silnik", "baza"]
    assert not {"scanner", "silnik-nadzorca"} & {w.name for w in threading.enumerate() if w.is_alive()} and st.k.silnik.pid is None
    dziennik = st.tmp / "dane" / "stanowisko.sqlite"
    assert dziennik.is_file() and st.stan().zamkniety


def test_parametry_scannera_i_silnika_z_ustawien(tmp_path):
    """Podpiecie ``[scanner]`` / ``[silnik]`` / ``[sciezki]`` z ``ustawienia.toml`` do konstruktorow (bez uruchamiania analizy)."""
    from stanowisko import aplikacja as AP

    ust = TK.ustawienia_probne(tmp_path)
    ust["scanner"].update(stabilizacja_ms=750, min_rozmiar_mb=0.001, min_trojkatow=3, wzorzec_pliku="plytka_*.stl", rekurencyjnie=False,
                          obserwator="odpytywanie")
    ust["silnik"].update(limit_zadania_s=123.0, czekaj_na_plik_s=4.5, pamiec_linii=False, ponow_plik_niedostepny=0)
    (tmp_path / "eksport").mkdir()
    k = AP.Aplikacja(ust, funkcja_analizy=TK.FUNKCJA_SZTUCZNA)
    try:
        assert k.stan().plytki == () and k.przetworz() == 0  # przed startem: stan z bazy, bez obserwatora i silnika
        k.start()
        sc, si = k.scanner, k.silnik
        assert (sc.folder, sc.stabilizacja_s, sc.min_rozmiar_mb, sc.min_trojkatow, sc.wzorzec_pliku, sc.rekurencyjnie) == (
            tmp_path / "eksport", 0.75, 0.001, 3, "plytka_*.stl", False)
        assert sc.stan()["obserwator"] == "odpytywanie" and sc.znane is not None and sc.akcja_startu is k._akcja_startu
        assert (si.limit_zadania_s, si.czekaj_na_plik_s, si.pamiec_linii, si.funkcja) == (123.0, 4.5, None, TK.FUNKCJA_SZTUCZNA)
        assert Path(si.plik_logu) == tmp_path / "dane" / "logi" / "silnik.log" and si.ust is ust
        assert k.sesja.baza.plik == tmp_path / "dane" / "stanowisko.sqlite" and k.sesja.katalog_wynikow == tmp_path / "dane" / "wyniki"
        assert k.katalog_podgladow == tmp_path / "dane" / "podglady" and k.ponow_plik_niedostepny == 0
        assert k.sesja.operatorzy == ("Technik A", "Technik B") and k.sesja.wersja_programu == AP.WERSJA_PROGRAMU
    finally:
        k.zamknij()
    ust["silnik"]["pamiec_linii"] = True
    k = AP.Aplikacja(ust, funkcja_analizy=TK.FUNKCJA_SZTUCZNA)
    try:
        k.start()
        assert Path(k.silnik.pamiec_linii) == tmp_path / "dane" / "pula_cache"
    finally:
        k.zamknij()


def test_plik_startowy_bez_qt_na_poziomie_modulu():
    """``silnik.md`` (D8): plik startowy nie importuje Qt na poziomie modulu - proces roboczy silnika wykonuje go ponownie."""
    zrodlo = (STANOWISKO / "stanowisko" / "aplikacja.py").read_text(encoding="utf-8")
    drzewo = ast.parse(zrodlo)
    na_gorze = [ast.unparse(w) for w in drzewo.body if isinstance(w, (ast.Import, ast.ImportFrom))]
    assert na_gorze and not [w for w in na_gorze if "PySide6" in w or "ui" in w.split()]
    main = next(w for w in drzewo.body if isinstance(w, ast.FunctionDef) and w.name == "main")
    importy = [w for w in ast.walk(main) if isinstance(w, (ast.Import, ast.ImportFrom))]
    assert importy and "PySide6" in ast.unparse(importy[0]) and {a.name for a in importy[0].names} >= {"QtCore", "QtGui", "QtWidgets"}
    pierwsze = [w for w in main.body if not isinstance(w, ast.Expr)][0]
    assert pierwsze is importy[0]  # Qt w calosci na poczatku main(), przed kontrolerem i silnikiem
    assert re.search(r'if __name__ == "__main__":\n    raise SystemExit\(main\(\)\)', zrodlo)
    kod = ("import sys; import stanowisko.aplikacja; "
           "print(sorted(m for m in ('PySide6', 'numpy', 'trimesh', 'open3d') if m in sys.modules))")
    w = subprocess.run([sys.executable, "-c", kod], cwd=STANOWISKO, capture_output=True, text=True, timeout=120)
    assert w.returncode == 0 and w.stdout.strip() == "[]", w.stdout + w.stderr
    bat = (STANOWISKO / "uruchom_stanowisko.bat").read_bytes()
    assert b"-m stanowisko.aplikacja" in bat and bat.count(b"\r\n") == bat.count(b"\n") >= 4 and bat.isascii()


def _plik_ustawien(tmp_path: Path) -> Path:
    """Plik ``ustawienia.toml`` ze wzoru programu ze sciezkami danych w ``tmp_path`` (dla ``main``)."""
    from stanowisko import ustawienia as UST

    tekst = UST.PLIK_PRZYKLADU.read_text(encoding="utf-8")
    for klucz, wartosc in (("folder_eksportu_skanera", "eksport"), ("folder_cyrkon", "projekty"), ("baza", "dane/stanowisko.sqlite"),
                           ("wyniki", "dane/wyniki"), ("podglady", "dane/podglady"), ("pula_cache", "dane/pula_cache"), ("logi", "dane/logi")):
        tekst, n = re.subn(rf'(?m)^{klucz} = "[^"]*"', f'{klucz} = "{(tmp_path / wartosc).as_posix()}"', tekst)
        assert n == 1, klucz
    plik = tmp_path / "ustawienia.toml"
    plik.write_text(tekst, encoding="utf-8")
    return plik


def test_main_uruchamia_program_i_zamyka_go_czysto(tmp_path):
    """``python -m stanowisko.aplikacja`` (to, co robi ``uruchom_stanowisko.bat``): start z plikiem ustawien, okno, czyste
    zamkniecie po 2 s; baza zalozona, w dzienniku start i stop, log zapisany; druga proba na danych sztucznych (--atrapa)."""
    from stanowisko import baza as B

    plik = _plik_ustawien(tmp_path)
    TK.pula_probna(tmp_path)
    (tmp_path / "eksport").mkdir()
    srodowisko = {**os.environ, "QT_QPA_PLATFORM": "offscreen"}
    w = subprocess.run([sys.executable, "-m", "stanowisko.aplikacja", "--ustawienia", str(plik), "--zamknij-po", "2"], cwd=STANOWISKO,
                       capture_output=True, text=True, timeout=180, env=srodowisko)
    assert w.returncode == 0, w.stdout + w.stderr
    assert "Traceback" not in w.stderr, w.stderr
    with B.otworz(tmp_path / "dane" / "stanowisko.sqlite", tylko_odczyt=True) as baza:
        typy = [x["typ"] for x in baza.wiersze("SELECT typ FROM zdarzenia WHERE zrodlo = 'system' ORDER BY id")]
    assert typy == ["program_start", "program_stop"]
    log = (tmp_path / "dane" / "logi" / "stanowisko.log").read_text(encoding="utf-8")
    assert "stanowisko: start" in log and "stanowisko: zamkniete" in log
    w = subprocess.run([sys.executable, "-m", "stanowisko.aplikacja", "--atrapa", "--zamknij-po", "1"], cwd=STANOWISKO,
                       capture_output=True, text=True, timeout=180, env=srodowisko)
    assert w.returncode == 0 and "Traceback" not in w.stderr, w.stdout + w.stderr
    zly = tmp_path / "zle.toml"
    zly.write_text("[sciezki]\nbaza = 5\n", encoding="utf-8")
    w = subprocess.run([sys.executable, "-m", "stanowisko.aplikacja", "--ustawienia", str(zly), "--zamknij-po", "1"], cwd=STANOWISKO,
                       capture_output=True, text=True, timeout=180, env=srodowisko)
    assert w.returncode == 2 and "BLAD: zle.toml" in w.stderr and "Traceback" not in w.stderr  # komunikat dla czlowieka, nie slad wyjatku

# ----------------------------------------------------------------------------
# wariant na duzych skanach odniesienia (wlaczany zmiennymi srodowiskowymi; liczby do raportu paczki)
# ----------------------------------------------------------------------------
@pytest.mark.skipif(not (DANE_REF and PROJEKTY_REF), reason=BRAK_DANYCH_REF)
def test_skany_odniesienia_przez_cala_aplikacje_w_petli_qt(tmp_path):
    """Trzy duze sztuczne skany (45-55 MB: okragla wieczorna, kwadratowa wieczorna, okragla poranna) i pula prawdziwych
    projektow przez CALA aplikacje w petli Qt: symulator zapisuje pliki w kawalkach, ``scanner`` liczy skroty, ``silnik`` wykonuje
    ``porownaj``, wynik trafia do sesji. Stan = wynik analizy w 100 % gniazd; plytka poranna zablokowana; przerwa petli okna."""
    import symulator_skanera as SY
    from PySide6.QtCore import QEventLoop, QTimer
    from PySide6.QtWidgets import QApplication

    from stanowisko import aplikacja as AP
    from stanowisko import kontroler_api as K

    skany = [sorted(Path(DANE_REF).glob(f"skan_{typ}_n*.stl"))[0] for typ in ("okragla_wieczorna", "wieczorna", "okragla_poranna")]
    ust = TK.ustawienia_probne(tmp_path)
    ust["sciezki"]["folder_cyrkon"] = Path(PROJEKTY_REF).as_posix()
    ust["scanner"]["stabilizacja_ms"] = 300  # jak w programie
    (tmp_path / "eksport").mkdir()
    app = QApplication.instance() or QApplication([])
    assert app.platformName() == "offscreen"
    k = AP.Aplikacja(ust)
    try:
        k.start()
        kroki = mierz_kroki(k)
        lacznik = K.lacznik_qt(k)
        petla = QEventLoop()
        pomiar = {"ostatni": 0.0, "przerwa": 0.0, "tykniec": 0, "czasy": {}}

        def tyk():
            teraz = time.perf_counter()
            pomiar["przerwa"] = max(pomiar["przerwa"], teraz - pomiar["ostatni"])
            pomiar["ostatni"] = teraz
            pomiar["tykniec"] += 1
            s = k.stan()
            for p in s.plytki:
                pomiar["czasy"].setdefault(p.skan_id, teraz)
            if len(s.plytki) == len(skany) and s.kolejka.razem == 0:
                petla.quit()

        zegar = QTimer()
        zegar.setInterval(10)
        zegar.timeout.connect(tyk)
        QTimer.singleShot(1_500_000, petla.quit)

        def zapisuj():  # jak skaner: kolejne pliki zapisywane w kawalkach przez 2 s, w podfolderze "zlecenia"
            for i, skan in enumerate(skany):
                SY.zapisz_jak_skaner(skan, tmp_path / "eksport" / FOLDER_ZLECENIA / f"eksport_{i}.stl", czas_s=2.0, kawalki=10)

        pisarz = threading.Thread(target=zapisuj, daemon=True)
        t0 = pomiar["ostatni"] = time.perf_counter()
        zegar.start()
        pisarz.start()
        petla.exec()
        zegar.stop()
        lacznik.zatrzymaj()
        pisarz.join(60.0)
        s = k.stan()
        assert len(s.plytki) == 3, [x.tekst for x in s.komunikaty]
        opis = []
        for p in s.plytki:
            wynik = json.loads(k.sesja.sciezka_wyniku(p.skan_id).read_text(encoding="utf-8"))
            assert kolory(p) == K.kolory_oczekiwane(wynik, status_skanu=p.status, numer_znany=p.numer is not None)  # 100 % gniazd
            opis.append(f"{p.uklad} nr {p.numer}: {p.status}, prac {len(p.prace)}, kolory {dict(sorted(p.liczniki.items()))}, "
                        f"analiza {p.czas_s:.1f} s, w stanie po {pomiar['czasy'][p.skan_id] - t0:.1f} s")
        print("\n[skany odniesienia przez aplikacje] " + "; ".join(opis) + f"; pula {s.pula.liczba_stl} STL; najdluzsza przerwa petli Qt "
              f"{pomiar['przerwa'] * 1000:.0f} ms (prog {PROG_PRZERWY_S * 1000:.0f} ms), tykniec {pomiar['tykniec']}; pytania: {[q.rodzaj for q in s.pytania]}; "
              f"komunikaty: {[x.rodzaj for x in s.komunikaty]}; najdluzsze kroki w watku okna [ms]: "
              + ", ".join(f"{nazwa} {max(czasy) * 1000:.0f} (x{len(czasy)})" for nazwa, czasy in sorted(kroki.items()) if czasy))
        # status dwoch plytek wieczornych zalezy od danych (zestaw ma skany z drgnieciem = do powtorzenia); poranna jest zawsze zablokowana
        assert [p.status for p in s.plytki][2] == "plytka_nie_z_trybu" and s.plytki[2].zielonych == 0
        assert all(p.status in ("przyjety", "do_powtorzenia") and (p.status == "przyjety" or p.zielonych == 0) for p in s.plytki[:2])
        assert [q.rodzaj for q in s.pytania if q.rodzaj == "plytka_nie_z_trybu"] == ["plytka_nie_z_trybu"]
        assert all(len(p.prace) >= 5 for p in s.plytki)
        assert pomiar["przerwa"] <= PROG_PRZERWY_S
    finally:
        k.zamknij()
