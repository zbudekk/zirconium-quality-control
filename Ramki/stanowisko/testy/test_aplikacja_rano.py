"""E3-A12: ramki swietlne (``indicate``) i Excel (``excel``) w programie "Stanowisko" - spiecie poranka i wieczoru.

Kryteria paczki (plan etapu 3, 4.1, E3-A12; tryb offscreen, atrapa ramki w OSOBNYM procesie - ``narzedzia/atrapa_ramki.py``,
HTTP 127.0.0.1; sztuczny arkusz ``arkusz_syntetyczny.ArkuszWPamieci``; raport ``raporty/E3-A12_2026-11-18.md``):
  (1) po skanach 3 plytek plan odebrany przez atrape ramki porannej = ``SesjaRano.plan_plytek`` (kolejnosc z ekranu), pole po polu,
      po kazdym skanie i po zmianie kolejnosci,
  (2) Enter na atrapie zapisuje potwierdzenie w ``zdarzenia`` DOKLADNIE RAZ (takze po restarcie programu i powtorce historii -
      klucz ``indicate.klucz_zdarzenia``), a klawisz "Zamknij piec" zamyka sesje pieca (tylko biezacy ``plan_id``; zdarzenie
      z historii / innego pieca - tylko dziennik),
  (3) po "Zamknij piec" w trybie "pytaj" program proponuje dokladnie zlecenia kompletne z A6, a po zatwierdzeniu w oknie "Excel:
      wskaz wiersz" w arkuszu zmienia sie tylko kolor wlasciwych komorek (tryb "cien" - nic),
  (4) Spacja zmienia stan atrapy ramki wieczornej w czasie ponizej 1 s, a po analizie atrapa dostaje kolory gniazd rowne mapie
      na ekranie (takze po decyzji),
  (5) wylaczona ramka albo brak Excela = ostrzezenie i dalsza praca; zamkniecie programu gasi ramki, zatrzymuje klientow
      i rozlacza Excel;
plus: petla okna < 200 ms (zegar 10 ms przez caly test ramek), okno 1920 x 1080 bez obciec (wzor ``test_ui_rozdzielczosc``),
``tryb`` w zdarzeniu ``start_skanu`` (prosba A10), D z recenzji PR #26 (D1, D2: pamiec brakow po zapisie z pominieciem
polecenia i po wyjatku). Test prawdziwego kontrolera (``Aplikacja``, silnik) - NA POCZATKU modulu (znane zawieszanie startu
procesu silnika po wielu testach z oknami - E3-A7 D7, poprawka A2p w toku).
"""
from __future__ import annotations

import copy
import datetime as dt
import gc
import http.client
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

import test_kontroler_api as TK
import test_ui_wieczor as UW

STANOWISKO = Path(__file__).resolve().parent.parent
NARZ = STANOWISKO / "narzedzia" / "atrapa_ramki.py"
MODELE = STANOWISKO / "modele_plytek"
LAPTOP = "lap-test-a12"
RANO_START = dt.datetime(2026, 11, 18, 6, 30, 0)
PELNY_EKRAN = (1920, 1001)
ZIELONY_EXCEL = (198, 239, 206)


@pytest.fixture(scope="module", autouse=True)
def _qt():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    if UW.FONTY_WINDOWS.is_dir():
        os.environ.setdefault("QT_QPA_FONTDIR", str(UW.FONTY_WINDOWS))
    import PySide6.QtCore  # noqa: F401
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    assert app.platformName() == "offscreen"
    UW.czcionka_ekranu()
    yield app


@pytest.fixture(scope="module")
def kal():
    from ramka import kalibracja

    return kalibracja.domyslna(MODELE)


class ZegarRano(UW.Zegar):
    def __init__(self):
        self.teraz = RANO_START


# ----------------------------------------------------------------------------
# atrapa ramki w osobnym procesie i ruch laptopa
# ----------------------------------------------------------------------------
def wolny_port() -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


class Ramka:
    """Atrapa ramki jako OSOBNY PROCES (``narzedzia/atrapa_ramki.py --sterowanie``); obserwacja i sterowanie przez HTTP."""

    def __init__(self, rola: str):
        args = [sys.executable, str(NARZ), "--rola", rola, "--port", "0", "--sterowanie"]
        linia = ""
        for _ in range(3):
            self.p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, cwd=str(STANOWISKO),
                                      text=True)
            linia = self.p.stdout.readline()
            if linia.startswith("ATRAPA_RAMKI "):
                break
            self.p.wait(10)
            time.sleep(0.3)
        assert linia.startswith("ATRAPA_RAMKI "), linia
        pola = dict(x.split("=") for x in linia.split()[1:])
        self.rola, self.port, self.start_id = rola, int(pola["port"]), pola["start_id"]

    def zadanie(self, metoda: str, sciezka: str, tresc=None):
        c = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        try:
            h = {"X-Laptop-Id": "test-a12-obserwator"}
            body = None
            if tresc is not None:
                body = json.dumps(tresc).encode("utf-8")
                h["Content-Type"] = "application/json"
            c.request(metoda, sciezka, body=body, headers=h)
            r = c.getresponse()
            dane = r.read()
            return r.status, (json.loads(dane.decode("utf-8")) if dane else None)
        finally:
            c.close()

    def stan(self) -> dict:
        st, odp = self.zadanie("GET", "/stan")
        assert st == 200, odp
        return odp

    def plytka(self, n: int) -> None:
        st, odp = self.zadanie("PUT", "/atrapa/plytka", {"plytka": n})
        assert st == 200, odp

    def klawisz(self, k: str) -> None:
        st, odp = self.zadanie("PUT", "/atrapa/klawisz", {"klawisz": k})
        assert st == 200, odp

    def zakoncz(self) -> None:
        if self.p.poll() is not None:
            return
        try:
            self.p.stdin.close()
            self.p.wait(10)
        except (OSError, subprocess.TimeoutExpired):
            self.p.kill()
            self.p.wait(10)


@pytest.fixture
def ramki():
    """Fabryka atrap ramek (osobne procesy) - po tescie konczone."""
    otwarte = []

    def nowa(rola: str) -> Ramka:
        r = Ramka(rola)
        otwarte.append(r)
        return r

    yield nowa
    for r in otwarte:
        r.zakoncz()


class Ruch:
    """Dziennik ruchu klientow ``indicate`` (hak ``dziennik_ruchu``): przyjete plany (PUT /plan + odpowiedz 200) po roli."""

    def __init__(self):
        import threading

        self.wpisy: list = []
        self._blok = threading.Lock()

    def __call__(self, wpis: dict) -> None:
        with self._blok:
            self.wpisy.append(dict(wpis))

    def przyjete_plany(self, rola: str) -> list:
        with self._blok:
            w = list(self.wpisy)
        zadania = {(x["rola"], x["nr"]): x for x in w if x["kierunek"] == "do_ramki" and x["metoda"] == "PUT" and x["sciezka"] == "/plan"}
        plany = []
        for x in w:
            if x["kierunek"] == "z_ramki" and x["rola"] == rola and x.get("status") == 200 and (rola, x["nr"]) in zadania:
                plany.append(json.loads(bytes(zadania[(rola, x["nr"])]["tresc"]).decode("utf-8")))
        return plany


def plan_na_ramce(ruch: Ruch, ramka: Ramka) -> dict | None:
    """Plan, ktory atrapa ramki TERAZ trzyma: przyjety PUT /plan o (plan_id, wersja) rownych ``GET /stan`` atrapy."""
    st = ramka.stan()
    if st.get("plan_id") is None:
        return None
    for plan in reversed(ruch.przyjete_plany(ramka.rola)):
        if (plan["plan_id"], plan["wersja"]) == (st["plan_id"], st["plan_wersja"]):
            return plan
    return None


def indicate(kal, w: Ramka | None = None, p: Ramka | None = None, ruch: Ruch | None = None, *, bez_w: bool = False, bez_p: bool = False):
    """``indicate.Indicate`` z klientami ramek W i P na atrapach (albo na porcie, na ktorym nikt nie slucha - ramka wylaczona)."""
    from stanowisko import indicate as IND

    def klient(rola, ramka):
        return IND.KlientRamki(rola, "127.0.0.1", ramka.port if ramka is not None else wolny_port(), laptop_id=LAPTOP, kalibracja=kal,
                               przerwa_min_s=0.05, przerwa_max_s=0.25, odpytywanie_s=2.0, dziennik_ruchu=ruch)

    return IND.Indicate(None if bez_w else klient("W", w), None if bez_p else klient("P", p))


def porownaj_plan_rano(plan: dict, pp: dict) -> int:
    """Plan przyjety przez ramke = ``SesjaRano.plan_plytek``: plan_id, gniazda kazdej plytki (id, kolor, kuweta - bez ``px``,
    ktore dodaje kalibracja), kuwety (kolejnosc i plytki), braki. Zwraca liczbe porownanych pol."""
    assert plan["plan_id"] == pp["plan_id"]
    na_ramce = {n: [{k: v for k, v in g.items() if k != "px"} for g in p["gniazda"]] for n, p in plan["plytki"].items()}
    z_sesji = {n: [g for g in p["gniazda"] if g.get("kolor") is not None] for n, p in pp["plytki"].items()}
    assert na_ramce == z_sesji
    assert plan["kuwety"] == [{"kuweta": k["kuweta"], "plytki": k["plytki"]} for k in pp["kuwety"]]
    assert plan["braki"] == pp["braki"]
    return 1 + sum(len(g) for p in na_ramce.values() for g in p) + 2 * len(plan["kuwety"]) + len(plan["braki"])


def kolory_mapy_dla_ramki(plytka) -> dict:
    """{gniazdo: kolor ramki} ze statusow gniazd plytki pokazanej na ekranie (``ramka_protokol.kolor_ramki``); bez gniazd ciemnych."""
    from stanowisko import ramka_protokol as RP

    return {g.nr: RP.kolor_ramki(g.status) for g in plytka.gniazda if RP.kolor_ramki(g.status) is not None}


def kolory_planu_w(plan: dict, numer: int) -> dict:
    return {g["id"]: g["kolor"] for g in plan["plytki"][str(numer)]["gniazda"]}


def ramka_zdarzen(baza, zrodlo: str = "ramka_p", typ: str | None = None) -> list:
    wiersze = baza.wiersze("SELECT typ, dane FROM zdarzenia WHERE zrodlo = ? ORDER BY id", (zrodlo,))
    return [{"typ": w["typ"], **json.loads(w["dane"])} for w in wiersze if typ is None or w["typ"] == typ]


def czekaj(warunek, limit_s: float = 10.0, co: str = "", pompa=None) -> None:
    """Czeka na warunek; ``pompa`` - funkcja wolana w petli (np. ``kontroler.przetworz``) zamiast petli okna."""
    koniec = time.monotonic() + limit_s
    while True:
        if pompa is not None:
            pompa()
        try:
            if warunek():
                return
        except (OSError, http.client.HTTPException):
            pass
        assert time.monotonic() < koniec, f"nie doczekalem sie: {co}"
        time.sleep(0.02)


class Ekran(UW.Ekran):
    """Okno programu (offscreen) - jak w ``test_ui_rano``: zamkniete i usuniete w watku okna."""

    def zamknij(self) -> None:
        from PySide6.QtCore import QCoreApplication, QEvent

        if getattr(self, "_usuniete", False):
            return
        self._usuniete = True
        super().zamknij()
        self.okno.deleteLater()
        self.lacznik.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)

    def klik_rano(self, skan_id: int, nr: int) -> None:
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest

        self.zdarzenia()
        self.czekaj(lambda: not self.okno.ekran_rano.ochrona_aktywna(), 5.0, "koniec przygaszenia map porannych")
        mapa = self.okno.ekran_rano.mapy()[skan_id]
        QTest.mouseClick(mapa, Qt.MouseButton.LeftButton, pos=mapa.srodek_gniazda(nr).toPoint())
        self.odczekaj(5)

    def klik_wiersz(self, nazwa_tabeli: str, wiersz: int) -> None:
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest

        self.zdarzenia()
        t = self.w(nazwa_tabeli)
        t.scrollToItem(t.item(wiersz, 0))
        self.zdarzenia()
        QTest.mouseClick(t.viewport(), Qt.MouseButton.LeftButton, pos=t.visualItemRect(t.item(wiersz, 0)).center())
        self.odczekaj(5)


@pytest.fixture
def ekrany():
    otwarte = []

    def nowy(kontroler, rozmiar: tuple = PELNY_EKRAN) -> Ekran:
        e = Ekran(kontroler, rozmiar)
        otwarte.append(e)
        return e

    yield nowy
    for e in otwarte:
        e.zamknij()
    otwarte.clear()
    gc.collect()


class Petla:
    """Zegar Qt co 10 ms mierzy najdluzsza przerwe petli okna (prog ``UW.PROG_PRZERWY_S`` = 200 ms) w czasie, gdy program pracuje
    sam (ruch ramek, zegar okna); ``pauza()`` - czynnosc testu wykonywana synchronicznie w watku okna (symulacja skanu atrapy z
    plikiem podgladu liczonym w watku okna, klikniecie, odczyt pikseli mapy) - poza pomiarem (czas reakcji na Spacje - osobno)."""

    def __init__(self):
        from PySide6.QtCore import QTimer

        self.przerwa, self.tykniec, self._ostatni = 0.0, 0, None
        self.zegar = QTimer()
        self.zegar.setInterval(10)
        self.zegar.timeout.connect(self._tyk)
        self.zegar.start()

    def _tyk(self) -> None:
        teraz = time.perf_counter()
        if self._ostatni is not None:
            self.przerwa = max(self.przerwa, teraz - self._ostatni)
            self.tykniec += 1
        self._ostatni = teraz

    def pauza(self):
        import contextlib

        @contextlib.contextmanager
        def wstrzymany():
            self._ostatni = None
            try:
                yield
            finally:
                self._ostatni = None  # nastepne tykniecie zaczyna pomiar od nowa

        return wstrzymany()

    def stop(self) -> None:
        self.zegar.stop()


def ust_excela(tmp_path: Path, tryb: str = "pytaj") -> dict:
    from stanowisko import ustawienia as UST

    ust = copy.deepcopy(UST.wczytaj_ustawienia(UST.PLIK_PRZYKLADU))
    ust["sciezki"]["log_excel"] = (tmp_path / "dane" / "log_excel.csv").as_posix()
    ust["excel"]["tryb"] = tryb
    return ust


def arkusz_zlecen(dzis: dt.date):
    """Sztuczny arkusz zlecen dla puli porannej ``kontroler_api.ZLECENIA_RANO`` (fikcyjne nazwy): dla kazdej kuwety wiersz
    "prawdziwy" (H = nazwa folderu, data sprzed 2 dni) i starszy, zielony wiersz tej samej kuwety innej osoby; kuweta 3214 ma
    DWA nieodhaczone wiersze z H = folder (reklamacja - "wskaz wiersz", prawdziwy = nowszy), kuweta 3228 - prawdziwy wiersz
    z pustym H (wybor bez zgodnej nazwy: ``do_sprawdzenia``); zlecenia prywatne - wiersz bez kuwety w C, numer w B.
    Zwraca (arkusz, {kuweta: numer prawdziwego wiersza})."""
    import arkusz_syntetyczny as AS
    from stanowisko import kontroler_api as K

    wiersze, prawda = [], {}

    def dodaj(a, b, c, h) -> int:
        wiersze.append([a, b, c, None, None, None, None, h, None])
        return len(wiersze) + 1  # wiersz 1 = naglowek

    zielone = []
    for i, (kuweta, _) in enumerate(K.ZLECENIA_RANO):
        folder = f"{kuweta} Fikcja Rano"
        if kuweta.startswith("#"):
            prawda[kuweta] = dodaj(dzis - dt.timedelta(days=2), kuweta[1:], None, folder)
            continue
        zielone.append(dodaj(dzis - dt.timedelta(days=400), f"S{i}", int(kuweta), f"Starsza Osoba {kuweta}"))
        if kuweta == "3214":
            dodaj(dzis - dt.timedelta(days=9), f"R{i}", int(kuweta), folder)
        prawda[kuweta] = dodaj(dzis - dt.timedelta(days=2), f"Z{1000 + i}", int(kuweta), "" if kuweta == "3228" else folder)
    arkusz = AS.ArkuszWPamieci(wiersze=wiersze)
    for nr in zielone:
        arkusz.zaznacz(nr, 2, ZIELONY_EXCEL)
    return arkusz, prawda


# ============================================================================
# prawdziwy kontroler (Aplikacja, silnik) - NA POCZATKU modulu (E3-A7 D7)
# ============================================================================
def test_a_prawdziwa_aplikacja_spacja_ramka_w_kolory_mapy_i_plan_ramki_p(tmp_path, ramki, ekrany, kal):
    """``Aplikacja`` z ``ramki=Indicate`` (atrapy W i P w osobnych procesach): Spacja w oknie -> atrapa W w stanie "skanowanie"
    ponizej 1 s; skan wieczorny przez folder skanera i silnik -> atrapa W dostaje kolory gniazd rowne mapie; tryb "Poranek",
    trzy skany porannne -> plan na atrapie P = ``plan_plytek`` pole po polu; zamkniecie programu gasi obie ramki."""
    from PySide6.QtCore import Qt

    from stanowisko import kontroler_api as K
    from stanowisko import session_rano as SR

    rw, rp = ramki("W"), ramki("P")
    ruch = Ruch()
    st = TK.StanowiskoAplikacji(tmp_path, ramki=indicate(kal, rw, rp, ruch))
    try:
        assert st.k.wybierz_operatora("Technik A")
        e = ekrany(st.k)
        e.czekaj(lambda: (r := st.k.stan().ramki) is not None and r.wieczorna.polaczona and r.poranna.polaczona, 15.0, "ramki polaczone")
        t0 = time.perf_counter()
        e.klawisz(Qt.Key.Key_Space)
        e.czekaj(lambda: rw.stan()["tryb"] == "skanowanie", 2.0, "atrapa W w stanie skanowanie")
        dt_spacji = time.perf_counter() - t0
        assert dt_spacji < 1.0 and st.starty_skanu() == 1
        st.zapisz(st.opis("zwykla", 1, None, None, None, 0))
        e.czekaj(lambda: len(st.k.stan().plytki) == 1 and rw.stan()["tryb"] == "wynik", 90.0, "wynik skanu na ramce W")
        plytka = st.k.stan().plytki[0]
        if e.okno.pokazana_plytka() != plytka.skan_id:
            e.klik(f"plytka_{plytka.skan_id}")
        gniazd = UW.mapa_rowna_stanowi(e, plytka)
        plan_w = plan_na_ramce(ruch, rw)
        assert plan_w is not None and kolory_planu_w(plan_w, 1) == kolory_mapy_dla_ramki(plytka)
        # poranek: trzy plytki przez skaner i silnik
        e.klik("przycisk_przelacz_tryb")
        K.indeks_rano_sztuczny(st.k.sesja.baza, st.k.sesja.teraz())
        for numer, (gniazda, projekty) in K.plan_scenariusza_rano().items():
            st.zapisz(st.opis_rano(numer, gniazda, projekty))
        e.czekaj(lambda: (r := st.k.stan().rano) is not None and len(r.plytki) == 3, 120.0, "trzy plytki poranne")
        rano = st.k.stan().rano
        pp = SR.SesjaRano(st.k.sesja).plan_plytek(kolejnosc=rano.kolejnosc)
        e.czekaj(lambda: (p := plan_na_ramce(ruch, rp)) is not None and p["plan_id"] == pp["plan_id"] and sorted(p["plytki"]) == ["4", "5", "6"],
                 10.0, "plan pieca na ramce P")
        pol = porownaj_plan_rano(plan_na_ramce(ruch, rp), pp)
        print(f"\n[A12, Aplikacja] Spacja -> ramka W {dt_spacji * 1000:.0f} ms; kolory W = mapa w {gniazd} gniazdach; plan P = session: {pol} pol")
    finally:
        st.koniec()
    assert rp.stan()["plan_id"] is None and rw.stan()["plan_id"] is None  # zamkniecie programu: obie ramki zgaszone


# ============================================================================
# (1) plan ramki porannej = plan_plytek z session, po kazdym skanie i po zmianie kolejnosci
# ============================================================================
def test_k1_plan_ramki_porannej_rowny_planowi_session_pole_po_polu(tmp_path, ramki, ekrany, kal):
    from stanowisko import kontroler_api as K
    from stanowisko import session_rano as SR

    rp = ramki("P")
    ruch = Ruch()
    k = K.AtrapaKontrolera(tmp_path / "k", zegar=ZegarRano())
    try:
        k.podlacz_ramki(indicate(kal, p=rp, ruch=ruch, bez_w=True))
        assert k.przelacz_tryb("rano") and k.wybierz_operatora("Technik A")
        e = ekrany(k)
        e.czekaj(lambda: k.stan().ramki.poranna.polaczona and k.stan().rano.ramka, 15.0, "ramka P polaczona")
        assert not e.jest("komunikat_ramka_niedostepna")
        porownane, plany = 0, 0
        for numer, (gniazda, projekty) in K.plan_scenariusza_rano().items():
            k.symuluj_skan_rano(numer, gniazda, projekty=projekty)
            pp = SR.SesjaRano(k.sesja).plan_plytek(kolejnosc=k.stan().rano.kolejnosc)
            e.czekaj(lambda: (p := plan_na_ramce(ruch, rp)) is not None and p["plytki"].keys() == pp["plytki"].keys()
                     and p["kuwety"] == [{"kuweta": x["kuweta"], "plytki": x["plytki"]} for x in pp["kuwety"]], 10.0, f"plan po skanie plytki {numer}")
            porownane += porownaj_plan_rano(plan_na_ramce(ruch, rp), pp)
            plany += 1
        assert sorted(plan_na_ramce(ruch, rp)["plytki"]) == ["4", "5", "6"]
        # kolejnosc kuwet z ekranu ("numer") -> nowy plan z ta kolejnoscia
        e.okno._polecenie("ustaw_kolejnosc", "numer")
        pp = SR.SesjaRano(k.sesja).plan_plytek(kolejnosc="numer")
        e.czekaj(lambda: (p := plan_na_ramce(ruch, rp)) is not None and p["kuwety"] == [{"kuweta": x["kuweta"], "plytki": x["plytki"]} for x in pp["kuwety"]],
                 10.0, "plan w kolejnosci wedlug numeru")
        porownane += porownaj_plan_rano(plan_na_ramce(ruch, rp), pp)
        plany += 1
        # decyzja zmieniajaca kuwete gniazda (wybor kandydata dwuznacznej) -> plan aktualny
        praca = k.stan().rano.plytki[0].gniazdo(9).praca
        assert k.wybierz_kandydata(praca.praca_id, praca.kandydaci[0].sha16)
        pp = SR.SesjaRano(k.sesja).plan_plytek(kolejnosc="numer")
        e.czekaj(lambda: (p := plan_na_ramce(ruch, rp)) is not None and any(g.get("id") == 9 and g.get("kuweta") for g in p["plytki"]["4"]["gniazda"]),
                 10.0, "plan po wyborze kandydata")
        porownane += porownaj_plan_rano(plan_na_ramce(ruch, rp), pp)
        plany += 1
        print(f"\n[kryterium 1] {plany} plany na atrapie P = plan_plytek: {porownane} pol zgodnych, 0 roznych")
    finally:
        k.zamknij()


# ============================================================================
# (2) Enter na ramce -> potwierdzenie w zdarzeniach dokladnie raz; "Zamknij piec" z ramki
# ============================================================================
def _poranek_kontroler(katalog: Path, ind) -> object:
    from stanowisko import kontroler_api as K

    k = K.AtrapaKontrolera(katalog, zegar=ZegarRano())
    k.podlacz_ramki(ind)
    if k.stan().tryb != "rano":
        assert k.przelacz_tryb("rano")
    assert k.wybierz_operatora("Technik A")
    return k


def test_k2_enter_na_ramce_raz_w_zdarzeniach_po_restarcie_i_zamknij_piec_tylko_biezacy(tmp_path, ramki, kal):
    rp = ramki("P")
    katalog = tmp_path / "k"
    k = _poranek_kontroler(katalog, indicate(kal, p=rp, bez_w=True))
    try:
        skan = k.symuluj_skan_rano(4, {1: "pewna", 2: "pewna", 3: "pewna", 5: "pewna"}, projekty={1: 301, 2: 302, 3: 303, 5: 304})
        plan_id = k.stan().rano.plan_id
        czekaj(lambda: rp.stan()["plan_id"] == plan_id, 10.0, "plan na ramce P", pompa=k.przetworz)
        rp.plytka(4)
        czekaj(lambda: rp.stan()["plytka"] == 4, 5.0, "plytka 4 na ramce", pompa=k.przetworz)
        kuweta = rp.stan()["kuweta"]
        rp.klawisz("enter")
        czekaj(lambda: len(ramka_zdarzen(k.sesja.baza, typ="potwierdzenie")) == 1, 5.0, "potwierdzenie w zdarzeniach", pompa=k.przetworz)
        p = ramka_zdarzen(k.sesja.baza, typ="potwierdzenie")[0]
        assert (p["plan_id"], p["plytka"], p["kuweta"], p["z_historii"]) == (plan_id, 4, kuweta, False)
        assert next(x for x in k.stan().rano.kuwety if x.kuweta == kuweta).potwierdzona  # Enter na ramce = kuweta rozlozona na ekranie
        assert p["klucz"] == f"{rp.start_id}:{p['nr']}"
    finally:
        k.zamknij()
    # restart programu (nowy klient ramki bez kursora = cala historia biezacego startu ramki) - dwa razy
    for proba in range(2):
        k = _poranek_kontroler(katalog, indicate(kal, p=rp, bez_w=True))
        try:
            czekaj(lambda: k.stan().ramki.poranna.polaczona and rp.stan()["plan_id"] == plan_id, 10.0, "plan po restarcie", pompa=k.przetworz)
            for _ in range(20):
                k.przetworz()
                time.sleep(0.02)
            zd = ramka_zdarzen(k.sesja.baza)
            klucze = [z["klucz"] for z in zd]
            assert len(klucze) == len(set(klucze)), f"proba {proba}: duplikaty kluczy"
            assert len([z for z in zd if z["typ"] == "potwierdzenie"]) == 1
            assert rp.stan()["potwierdzone"] == [[4, kuweta]]  # potwierdzenie z bazy wraca na ramke po zgaszeniu przy zamknieciu
            assert next(x for x in k.stan().rano.kuwety if x.kuweta == kuweta).potwierdzona  # i rozlozenie na ekranie po restarcie
        finally:
            k.zamknij()
    # "Zamknij piec" na klawiaturze ramki (dwa kroki: klawisz + Enter) - zamyka biezacy piec; drugi raz (historia) nic nie robi
    k = _poranek_kontroler(katalog, indicate(kal, p=rp, bez_w=True))
    try:
        czekaj(lambda: rp.stan()["plan_id"] == plan_id, 10.0, "plan", pompa=k.przetworz)
        rp.klawisz("zamknij_piec")
        rp.klawisz("enter")
        czekaj(lambda: k.sesja.baza.wiersz("SELECT zamknieto FROM sesje_pieca WHERE id = ?", (k.stan().rano.sesja_pieca_id,))["zamknieto"], 5.0,
               "piec zamkniety klawiszem ramki", pompa=k.przetworz)
        zp = ramka_zdarzen(k.sesja.baza, typ="zamknij_piec")
        assert [(z["plan_id"], z["skutek"]) for z in zp] == [(plan_id, "zamknieto")]
        czekaj(lambda: rp.stan()["plan_id"] is None, 5.0, "ramka P zgaszona po Zamknij piec", pompa=k.przetworz)
        assert not k.stan().rano.otwarty and k.stan().rano.sesja_pieca_id is not None
        # nowy piec (skan) -> nowy plan; "Zamknij piec" wcisniety, ale program zamkniety przed odebraniem zdarzenia
        k.symuluj_skan_rano(5, {1: "pewna", 2: "pewna"}, projekty={1: 305, 2: 306})
        plan2 = k.stan().rano.plan_id
        assert plan2 != plan_id
        czekaj(lambda: rp.stan()["plan_id"] == plan2, 10.0, "plan nowego pieca", pompa=k.przetworz)
        rp.plytka(5)
        czekaj(lambda: rp.stan()["plytka"] == 5, 5.0, "plytka 5")
        nr = rp.stan()["nr_zdarzenia"]
        rp.klawisz("zamknij_piec")
        rp.klawisz("enter")
        czekaj(lambda: rp.stan()["nr_zdarzenia"] > nr, 5.0, "zdarzenie zamknij_piec na ramce")
    finally:
        k.zamknij()  # bez przetworz: zdarzenie nieodebrane przez program
    k = _poranek_kontroler(katalog, indicate(kal, p=rp, bez_w=True))
    try:
        czekaj(lambda: len(ramka_zdarzen(k.sesja.baza, typ="zamknij_piec")) == 2, 10.0, "historia zamknij_piec", pompa=k.przetworz)
        zp = ramka_zdarzen(k.sesja.baza, typ="zamknij_piec")
        assert (zp[1]["plan_id"], zp[1]["z_historii"], zp[1]["nieaktualne"], zp[1]["skutek"]) == (plan2, True, True, "nieaktualne")
        assert k.stan().rano.otwarty and k.stan().rano.plan_id == plan2  # piec z historii nie zostal zamkniety
        assert any(x.rodzaj == "ramka_zamknij_nieaktualne" for x in k.stan().komunikaty)
        klucze = [z["klucz"] for z in ramka_zdarzen(k.sesja.baza)]
        assert len(klucze) == len(set(klucze))
        print(f"\n[kryterium 2] potwierdzenie z Enter: 1 wpis po 3 uruchomieniach (historia x2); zamknij_piec biezacy: zamknieto 1; "
              f"z historii: nieaktualne, piec otwarty; zdarzen ramki {len(klucze)}, duplikatow 0")
    finally:
        k.zamknij()


class KlientAtrapa:
    """Klient ramki bez sieci (zamiast ``indicate.KlientRamki``) - test podaje zdarzenia, klient zapisuje polecenia."""

    def __init__(self, rola: str):
        self.rola = rola
        self.zdarzenia: list = []
        self.polecenia: list = []
        self.polaczona = True
        self.potw: list = []  # lustro potwierdzen ramki (``potwierdzone()``)
        self.wersja = 0

    def uruchom(self) -> None:
        self.polecenia.append(("uruchom",))

    def zatrzymaj(self, timeout: float = 1.0) -> bool:
        self.polecenia.append(("zatrzymaj",))
        return True

    def wznow(self) -> None:
        self.polecenia.append(("wznow",))

    def odbierz_zdarzenia(self) -> list:
        wynik, self.zdarzenia = self.zdarzenia, []
        return wynik

    def stan(self) -> dict:
        return {"rola": self.rola, "polaczona": self.polaczona, "blad": None, "komunikat": None, "plytka": None, "tryb_ramki": None,
                "plan_przyjety": False, "wstrzymane": False, "potwierdzone": list(self.potw), "ostrzezenia": [], "wersja": self.wersja}

    def potwierdzone(self) -> list:
        return [list(x) for x in self.potw]

    def ustaw_plan_rano(self, plan_plytek, *, potwierdzone=None, wybrane=None) -> dict:
        self.wersja += 1
        self.polecenia.append(("plan", plan_plytek["plan_id"], potwierdzone))
        return {}

    def zgas(self) -> None:
        self.polecenia.append(("zgas",))

    def tryb(self, stan: str):
        self.polecenia.append(("tryb", stan))

    def skanowanie(self):
        return self.tryb("skanowanie")

    def znacznik(self):
        return self.tryb("skanowanie")


class IndicateAtrapa:
    def __init__(self):
        self.wieczorna, self.poranna = KlientAtrapa("W"), KlientAtrapa("P")

    def klienci(self) -> list:
        return [self.wieczorna, self.poranna]

    def uruchom(self) -> None:
        for k in self.klienci():
            k.uruchom()

    def zatrzymaj(self, timeout: float = 1.0) -> dict:
        return {k.rola: k.zatrzymaj(timeout) for k in self.klienci()}

    def stan(self) -> dict:
        return {k.rola: k.stan() for k in self.klienci()}


def test_k2_zdarzenia_ramki_klucz_unikalny_tylko_biezacy_piec_i_pamiec_brakow(tmp_path):
    """Zdarzenia podane wprost (klient bez sieci): kazde zapisane raz z kluczem (start_id, nr), takze pominiete i odrzucone;
    "Zamknij piec" innego pieca / bez osoby / w trakcie analizy - odmowa z wpisem; ten sam klucz drugi raz - bez skutku.
    D1 (recenzja PR #26): "Zamknij piec" z ramki (zapis z pominieciem polecenia okna) uniewaznia pamiec listy brakow."""
    from stanowisko import kontroler_api as K
    from stanowisko import session_rano as SR

    ind = IndicateAtrapa()
    k = _poranek_kontroler(tmp_path / "k", ind)
    try:
        k.symuluj_skan_rano(4, {1: "pewna", 2: "pewna", 3: "pewna", 5: "pewna"}, projekty={1: 301, 2: 302, 3: 303, 5: 304})
        k.symuluj_skan_rano(5, {1: "pewna"}, projekty={1: 307})  # zlecenie 3221: 1 z 4 punktow - brak po piecu
        k.przetworz()
        r = k.stan().rano
        assert ("plan", r.plan_id, []) in ind.poranna.polecenia or any(p[:2] == ("plan", r.plan_id) for p in ind.poranna.polecenia)
        braki_przed = [z.kuweta for z in r.braki_biezace]

        def zd(nr, typ, **pola):
            return {"nr": nr, "typ": typ, "czas_s": 1.0, "rola": "P", "start_id": "s1", "z_historii": False, "nieaktualne": False, **pola}

        ind.poranna.zdarzenia += [zd(1, "plan_przyjety", plan_id=r.plan_id, wersja=1), zd(2, "potwierdzenie", plan_id=r.plan_id, plytka=4, kuweta="3200"),
                                  zd(2, "potwierdzenie", plan_id=r.plan_id, plytka=4, kuweta="3200"),
                                  zd(3, "potwierdzenie", plan_id="2026-11-17-p9", plytka=4, kuweta="3200"),
                                  zd(4, "zamknij_piec", plan_id="2026-11-17-p9", plytka=4)]
        k.przetworz()
        zdarzenia = ramka_zdarzen(k.sesja.baza)
        assert [(z["klucz"], z["typ"], z["skutek"]) for z in zdarzenia] == [
            ("s1:1", "plan_przyjety", "zapisano"), ("s1:2", "potwierdzenie", "zapisano"), ("s1:3", "potwierdzenie", "inny_piec"),
            ("s1:4", "zamknij_piec", "inny_piec")]
        assert k.stan().rano.otwarty
        k.wybierz_operatora(None)
        ind.poranna.zdarzenia.append(zd(5, "zamknij_piec", plan_id=r.plan_id, plytka=4))
        k.przetworz()
        assert ramka_zdarzen(k.sesja.baza, typ="zamknij_piec")[-1]["skutek"] == "odmowa" and k.stan().rano.otwarty
        assert any(x.rodzaj == "ramka_zamknij_odmowa" for x in k.stan().komunikaty)
        k.wybierz_operatora("Technik A")
        k.symuluj_kolejke(czeka=1)  # skan w analizie: wynik po zamknieciu otworzylby nowy piec
        ind.poranna.zdarzenia.append(zd(6, "zamknij_piec", plan_id=r.plan_id, plytka=4))
        k.przetworz()
        assert ramka_zdarzen(k.sesja.baza, typ="zamknij_piec")[-1]["skutek"] == "analiza_trwa" and k.stan().rano.otwarty
        k.symuluj_kolejke(czeka=0)
        ind.poranna.zdarzenia += [zd(7, "zamknij_piec", plan_id=r.plan_id, plytka=4), zd(7, "zamknij_piec", plan_id=r.plan_id, plytka=4)]
        k.przetworz()
        zp = ramka_zdarzen(k.sesja.baza, typ="zamknij_piec")
        assert [z["skutek"] for z in zp] == ["inny_piec", "odmowa", "analiza_trwa", "zamknieto"]
        rano = k.stan().rano
        assert not rano.otwarty and ("zgas",) in ind.poranna.polecenia
        prawda = [z["kuweta"] for z in SR.SesjaRano(k.sesja).braki()]
        assert "3221" not in braki_przed and "3221" in prawda and [z.kuweta for z in rano.braki_biezace] == prawda  # D1: pamiec brakow
        assert k.sesja.baza.wiersz("SELECT count(*) AS n FROM sesje_pieca WHERE zamknieto IS NOT NULL")["n"] == 1
        # klucz jest w tej samej transakcji co skutek: zdarzenie powtorzone po restarcie (historia) - bez drugiego skutku
        k.symuluj_skan_rano(6, {1: "pewna"}, projekty={1: 308})
        ind.poranna.zdarzenia.append({**zd(7, "zamknij_piec", plan_id=k.stan().rano.plan_id, plytka=4), "z_historii": True, "nieaktualne": True})
        k.przetworz()
        assert k.stan().rano.otwarty and len(ramka_zdarzen(k.sesja.baza, typ="zamknij_piec")) == 4
        assert K.ID_EXCEL in {x.id for x in k.stan().komunikaty} or not rano.kompletne  # bez Excela: lista kuwet do odhaczenia recznie
    finally:
        k.zamknij()
    assert ("zatrzymaj",) in ind.poranna.polecenia and ("zgas",) in ind.wieczorna.polecenia


def test_d2_wyjatek_po_zamknieciu_pieca_uniewaznia_pamiec_brakow(tmp_path):
    """Recenzja PR #26 D2: wyjatek PO zatwierdzeniu "Zamknij piec" w bazie (np. w czynnosciach pobocznych) - odpowiedz
    ``blad_polecenia``, a lista brakow na ekranie = prawda (pamiec uniewazniona takze w galezi wyjatku)."""
    from stanowisko import kontroler_api as K
    from stanowisko import session_rano as SR

    k = K.AtrapaKontrolera(tmp_path / "k", zegar=ZegarRano())
    try:
        k.przelacz_tryb("rano")
        k.wybierz_operatora("Technik A")
        k.symuluj_skan_rano(4, {1: "pewna"}, projekty={1: 307})
        przed = [z.kuweta for z in k.stan().rano.braki_biezace]
        oryginal = k.rano.zamknij_piec

        def zamknij_i_wyjatek(*a, **kw):
            oryginal(*a, **kw)
            raise RuntimeError("blad po zapisie")

        k.rano.zamknij_piec = zamknij_i_wyjatek
        odp = k.zamknij_piec(k.stan().rano.sesja_pieca_id)
        assert not odp and odp.kod == "blad_polecenia"
        prawda = [z["kuweta"] for z in SR.SesjaRano(k.sesja).braki()]
        assert prawda != przed and [z.kuweta for z in k.stan().rano.braki_biezace] == prawda
    finally:
        k.zamknij()


# ============================================================================
# (3) Excel: "pytaj" - propozycje = zlecenia kompletne A6, zatwierdzenie zmienia tylko kolor wlasciwych komorek
# ============================================================================
def test_k3_excel_pytaj_propozycje_rowne_kompletnym_i_tylko_kolor_wlasciwych_komorek(tmp_path, ekrany):
    from stanowisko import excel as EX
    from stanowisko import kontroler_api as K
    from stanowisko import session_rano as SR

    k = K.AtrapaKontrolera(tmp_path / "k", zegar=ZegarRano())
    try:
        skany = k.scenariusz_poranny()
        arkusz, prawda = arkusz_zlecen(RANO_START.date())
        ex = EX.Excel.z_ustawien(ust_excela(tmp_path), zrodlo=arkusz, baza=k.sesja.baza, zegar=lambda: RANO_START)
        k.podlacz_excel(ex)
        e = ekrany(k)
        assert k.stan().rano.excel and not e.jest("excel_panel")
        e.klik_rano(skany[6], 11)  # konflikt: "bez projektu"
        e.klik("praca_rano_bez_projektu")
        przed = arkusz.zrzut()
        petla = Petla()
        e.klik("przycisk_zamknij_piec")
        assert not e.jest("excel_panel") and k.stan().excel.w_toku == 1  # P1: Excel odroczony - najpierw ekran (i ramka)
        e.czekaj(lambda: e.jest("excel_panel") and k.stan().excel.w_toku == 0, 10.0, "okno Excela po kolejnych obiegach petli")
        wynik = SR.SesjaRano(k.sesja).wynik_pieca(k.stan().rano.sesja_pieca_id)
        assert wynik["kompletne"] and e.jest("excel_tabela") and not e.okno.ekran_rano.excel.wybrana() and not e.aktywny("excel_zatwierdz")
        stan_ex = k.stan().excel
        assert stan_ex.tryb == "pytaj" and stan_ex.sesja_pieca_id == wynik["sesja_pieca_id"]
        assert [p.kuweta for p in stan_ex.pozycje] == [z["kuweta"] for z in wynik["kompletne"]]  # dokladnie zlecenia kompletne A6
        assert arkusz.zrzut() == przed  # propozycja niczego nie zapisuje
        assert not any(op[0] == "ustaw_wypelnienie" for op in arkusz.operacje)
        zatwierdzone, pominiete, sprawdz = {}, [], 0
        for i, poz in enumerate(stan_ex.pozycje):
            e.klik_wiersz("excel_tabela", i)
            assert e.okno.ekran_rano.excel.pokazana() == (poz.sesja_pieca_id, poz.zlecenie_id) and e.okno.ekran_rano.excel.wybrana()
            cel = prawda.get(poz.kuweta)
            if poz.do_sprawdzenia:
                assert e.jest("excel_sprawdz") and not e.aktywny("excel_zatwierdz")  # B1: wybor bez zgodnej nazwy - wskazanie wiersza
                sprawdz += 1
            if poz.klasa == EX.KLASA_WSKAZ_WIERSZ or poz.do_sprawdzenia:
                kandydaci = [x.wiersz for x in k.excel_szczegoly(poz.sesja_pieca_id, poz.zlecenie_id).kandydaci]
                if cel not in kandydaci:
                    e.klik("excel_pomin")
                    pominiete.append(poz.kuweta)
                    continue
                e.klik_wiersz("excel_kandydaci", kandydaci.index(cel))
            else:
                assert poz.wiersz == cel, (poz.kuweta, poz.wiersz, cel)
            e.klik("excel_zatwierdz")
            assert not e.aktywny("excel_zatwierdz")  # B1: nastepna pozycja dopiero po kliknieciu w liste
            zatwierdzone[poz.kuweta] = cel
        petla.stop()
        assert len(zatwierdzone) + len(pominiete) == len(wynik["kompletne"]) and "3214" in zatwierdzone and sprawdz >= 1
        wartosci_po, kolory_po = arkusz.zrzut()
        assert wartosci_po == przed[0]  # wartosci komorek bez zmian
        zmienione = {kl: c for kl, c in kolory_po.items() if przed[1].get(kl) != c}
        assert zmienione == {(nr, 2): ZIELONY_EXCEL for nr in zatwierdzone.values()}  # tylko kolor pola B wlasciwych wierszy
        assert all(p.zalatwiona for p in k.stan().excel.pozycje) and not e.jest("excel_panel")
        wpisy = k.sesja.baza.wiersze("SELECT wynik, wiersz, operator FROM excel_zapisy WHERE sesja_pieca_id = ?", (wynik["sesja_pieca_id"],))
        assert sorted(w["wiersz"] for w in wpisy if w["wynik"] in ("zapisano", "wskazano_recznie")) == sorted(zatwierdzone.values())
        assert all(w["operator"] == "Technik A" for w in wpisy)
        assert petla.tykniec >= 20 and petla.przerwa <= UW.PROG_PRZERWY_S
        print(f"\n[kryterium 3] propozycje {len(stan_ex.pozycje)} = kompletne A6 {len(wynik['kompletne'])}; zatwierdzone {len(zatwierdzone)}, "
              f"pominiete {len(pominiete)}, do sprawdzenia {sprawdz}; komorek zmienionych {len(zmienione)} (tylko B wlasciwych wierszy); "
              f"przerwa petli {petla.przerwa * 1000:.0f} ms")
    finally:
        k.zamknij()


def test_k3_excel_cien_tylko_log_i_restart_okna_excela(tmp_path):
    """Tryb "cien": po "Zamknij piec" log porownawczy calego pieca bez pytan, arkusz bez zmian. Tryb "pytaj" po restarcie
    programu: ``excel_pokaz`` proponuje tylko zlecenia bez wpisu w ``excel_zapisy``."""
    from stanowisko import excel as EX
    from stanowisko import kontroler_api as K

    k = K.AtrapaKontrolera(tmp_path / "k", zegar=ZegarRano())
    try:
        k.przelacz_tryb("rano")
        k.wybierz_operatora("Technik A")
        arkusz, _ = arkusz_zlecen(RANO_START.date())
        k.podlacz_excel(EX.Excel.z_ustawien(ust_excela(tmp_path, "cien"), zrodlo=arkusz, baza=k.sesja.baza, zegar=lambda: RANO_START))
        k.symuluj_skan_rano(4, {1: "pewna", 2: "pewna", 3: "pewna", 5: "pewna"}, projekty={1: 301, 2: 302, 3: 303, 5: 304})
        przed = arkusz.zrzut()
        odczyty = sum(1 for op in arkusz.operacje if op[0] == "odczytaj")
        odp = k.zamknij_piec(k.stan().rano.sesja_pieca_id)
        assert odp and len(odp.dane["kompletne"]) == 2 and k.stan().excel.w_toku == 1
        czekaj(lambda: k.stan().excel.w_toku == 0, 5.0, "krok Excela", pompa=k.przetworz)
        assert sum(1 for op in arkusz.operacje if op[0] == "odczytaj") - odczyty == 1  # P1: jeden odczyt arkusza na caly piec
        assert arkusz.zrzut() == przed and not any(op[0] == "ustaw_wypelnienie" for op in arkusz.operacje)
        wpisy = k.sesja.baza.wiersze("SELECT tryb, wynik FROM excel_zapisy")
        assert len(wpisy) == 2 and all(w["tryb"] == "cien" for w in wpisy)
        assert k.stan().excel.tryb == "cien" and not k.stan().excel.widoczne
        assert any(x.rodzaj == "excel_cien" for x in k.stan().komunikaty)
        # pytaj: drugi piec, jedno zlecenie zatwierdzone, restart programu - okno Excela tylko z drugim zleceniem
        k.podlacz_excel(EX.Excel.z_ustawien(ust_excela(tmp_path), zrodlo=arkusz, baza=k.sesja.baza, zegar=lambda: RANO_START))
        k.symuluj_skan_rano(5, {1: "pewna", 2: "pewna", 3: "pewna"}, projekty={1: 305, 2: 306, 3: 313})
        assert k.zamknij_piec(k.stan().rano.sesja_pieca_id)
        czekaj(lambda: k.stan().excel.w_toku == 0, 5.0, "krok Excela", pompa=k.przetworz)
        piec2 = k.stan().rano.sesja_pieca_id
        poz = k.stan().excel.pozycje
        assert [p.kuweta for p in poz] == ["3214", "3235"] and k.stan().excel.widoczne
        assert k.excel_zatwierdz(poz[1].sesja_pieca_id, poz[1].zlecenie_id) and k.stan().excel.pozycje[1].zalatwiona
        assert k.excel_zamknij() and not k.stan().excel.widoczne
    finally:
        k.zamknij()
    k = K.AtrapaKontrolera(tmp_path / "k", zegar=ZegarRano())
    try:
        k.wybierz_operatora("Technik A")
        k.podlacz_excel(EX.Excel.z_ustawien(ust_excela(tmp_path), zrodlo=arkusz, baza=k.sesja.baza, zegar=lambda: RANO_START))
        assert k.excel_pokaz(piec2)
        assert [p.kuweta for p in k.stan().excel.pozycje] == ["3214"] and k.stan().excel.widoczne
    finally:
        k.zamknij()


# ============================================================================
# (4) Spacja -> ramka W < 1 s; po analizie kolory gniazd = mapa na ekranie
# ============================================================================
def test_k4_spacja_ramka_w_ponizej_1s_kolory_rowne_mapie_i_petla_okna(tmp_path, ramki, ekrany, kal):
    from PySide6.QtCore import Qt

    from stanowisko import kontroler_api as K

    rw = ramki("W")
    ruch = Ruch()
    k = K.AtrapaKontrolera(tmp_path / "k", zegar=UW.Zegar())
    try:
        assert k.wybierz_operatora("Technik A")
        k.podlacz_ramki(indicate(kal, w=rw, ruch=ruch, bez_p=True))
        e = ekrany(k)
        e.czekaj(lambda: k.stan().ramki.wieczorna.polaczona, 15.0, "ramka W polaczona")
        petla = Petla()
        czasy, gniazd = [], 0
        for i in range(5):
            t0 = time.perf_counter()
            with petla.pauza():
                e.klawisz(Qt.Key.Key_Space)
            e.czekaj(lambda: rw.stan()["tryb"] == "skanowanie", 2.0, "atrapa W: skanowanie")
            czasy.append(time.perf_counter() - t0)
            with petla.pauza():
                skan = k.symuluj_skan("zwykla" if i % 2 == 0 else "czysta", numer=1 + i % 3)
            e.czekaj(lambda: rw.stan()["tryb"] == "wynik" and plan_na_ramce(ruch, rw) is not None, 5.0, "wynik na atrapie W")
            plytka = k.stan().plytka(skan)
            with petla.pauza():
                if e.okno.pokazana_plytka() != skan:
                    e.klik(f"plytka_{skan}")
                gniazd += UW.mapa_rowna_stanowi(e, plytka)
            plan = plan_na_ramce(ruch, rw)
            assert sorted(plan["plytki"]) == [str(plytka.numer)]  # ramka W: tylko ostatni skan
            assert kolory_planu_w(plan, plytka.numer) == kolory_mapy_dla_ramki(plytka)
        # decyzja zmienia kolor gniazda na ekranie -> ramka dostaje nowy kolor (ten sam skan)
        with petla.pauza():
            skan = k.symuluj_skan("zwykla", numer=2)
        e.czekaj(lambda: (p := plan_na_ramce(ruch, rw)) is not None and "2" in p["plytki"], 5.0, "wynik plytki 2")
        with petla.pauza():
            if e.okno.pokazana_plytka() != skan:
                e.klik(f"plytka_{skan}")
            e.klik_gniazdo(2)
            e.klik("przycisk_ok")  # czerwone -> "OK": zielone na ekranie i na ramce
            e.klawisz(Qt.Key.Key_Escape)  # widok pracy zamkniety (wybrane gniazdo nie jest podswietlone przy odczycie pikseli)
            plytka = k.stan().plytka(skan)
            UW.mapa_rowna_stanowi(e, plytka)
        e.czekaj(lambda: (p := plan_na_ramce(ruch, rw)) is not None and "2" in p["plytki"] and kolory_planu_w(p, 2) == kolory_mapy_dla_ramki(plytka),
                 5.0, "kolor po decyzji na ramce W")
        # skan zablokowany (niezgodny uklad) -> ramka W ciemna, stary wynik nie wraca
        with petla.pauza():
            e.klawisz(Qt.Key.Key_Space)
            k.symuluj_skan("niezgodny_uklad", numer=1)
        e.czekaj(lambda: rw.stan()["plan_id"] is None and rw.stan()["tryb"] in ("blad", "gotowa"), 5.0, "ramka W ciemna po skanie zablokowanym")
        petla.stop()
        print(f"\n[kryterium 4] Spacja -> stan atrapy W: maks {max(czasy) * 1000:.0f} ms ({len(czasy)} prob, prog 1000 ms); kolory W = mapa "
              f"w {gniazd} gniazdach; najdluzsza przerwa petli okna {petla.przerwa * 1000:.0f} ms (tykniec {petla.tykniec})")
        assert max(czasy) < 1.0 and petla.tykniec >= 100 and petla.przerwa <= UW.PROG_PRZERWY_S
        zd = k.sesja.baza.wiersze("SELECT dane FROM zdarzenia WHERE zrodlo = 'ui' AND typ = 'start_skanu'")
        assert len(zd) == 6 and all(json.loads(w["dane"])["tryb"] == "wieczor" for w in zd)  # prosba A10
    finally:
        k.zamknij()
    assert rw.stan()["plan_id"] is None


# ============================================================================
# (5) wylaczona ramka, brak Excela: ostrzezenie i dalsza praca; zamkniecie programu
# ============================================================================
def test_k5_wylaczona_ramka_i_brak_excela_ostrzezenie_i_dalsza_praca(tmp_path, ekrany, kal):
    from PySide6.QtCore import Qt

    from stanowisko import excel as EX
    from stanowisko import kontroler_api as K

    k = K.AtrapaKontrolera(tmp_path / "k", zegar=ZegarRano())
    try:
        k.podlacz_ramki(indicate(kal))  # obie ramki na portach, na ktorych nikt nie slucha
        arkusz, prawda = arkusz_zlecen(RANO_START.date())
        excel_otwarty = {"tak": False}

        def polacz():
            if not excel_otwarty["tak"]:
                raise RuntimeError("Excel nie jest uruchomiony")
            return arkusz

        k.podlacz_excel(EX.Excel.z_ustawien(ust_excela(tmp_path), zrodlo=polacz, baza=k.sesja.baza, zegar=lambda: RANO_START))
        assert k.wybierz_operatora("Technik A")
        e = ekrany(k)
        e.odczekaj(400)
        s = k.stan()
        assert s.ramki is not None and not s.ramki.wieczorna.polaczona and not s.ramki.poranna.polaczona
        assert e.jest("napis_ramki") and e.jest("przycisk_test_led") and not e.jest("komunikat_ramka_wieczorna_niedostepna")  # D7: bez migania
        e.czekaj(lambda: e.jest("komunikat_ramka_wieczorna_niedostepna"), 5.0, "komunikat po czasie na polaczenie")
        e.klawisz(Qt.Key.Key_Space)  # Spacja bez ramki: start skanu dziala
        assert len(k.starty_skanu) == 1
        skan = k.symuluj_skan("zwykla", numer=1)
        assert k.stan().plytka(skan) is not None
        assert isinstance(k.test_led(), K.Odpowiedz)  # bez polaczenia: polecenie nie rzuca wyjatku
        e.klik("przycisk_przelacz_tryb")
        assert e.jest("komunikat_ramka_niedostepna") and not k.stan().rano.ramka
        skany = {4: k.symuluj_skan_rano(4, {1: "pewna", 2: "pewna", 3: "pewna", 5: "pewna"}, projekty={1: 301, 2: 302, 3: 303, 5: 304})}
        e.klik("przycisk_zamknij_piec")
        assert not k.stan().rano.otwarty  # piec zamkniety mimo wylaczonej ramki i braku Excela
        e.czekaj(lambda: e.jest("komunikat_excel_blad"), 5.0, "komunikat Excela")
        assert not e.jest("excel_panel")
        assert k.stan().excel.blad and "3200" in next(x.tekst for x in k.stan().komunikaty if x.id == K.ID_EXCEL)
        excel_otwarty["tak"] = True  # czlowiek otworzyl plik w Excelu
        e.klik("przycisk_excel")
        assert e.jest("excel_panel") and [p.kuweta for p in k.stan().excel.pozycje] == ["3200", "3207"]
        assert skany[4] in {p.skan_id for p in k.stan().rano.plytki}
    finally:
        k.zamknij()


def test_k5_zamkniecie_programu_gasi_ramki_zatrzymuje_klientow_i_rozlacza_excel(tmp_path, ramki, kal):
    from stanowisko import excel as EX
    from stanowisko import kontroler_api as K

    rw, rp = ramki("W"), ramki("P")
    ind = indicate(kal, rw, rp)
    k = _poranek_kontroler(tmp_path / "k", ind)
    arkusz, _ = arkusz_zlecen(RANO_START.date())
    ex = EX.Excel.z_ustawien(ust_excela(tmp_path), zrodlo=lambda: arkusz, baza=k.sesja.baza)
    rozlaczenia = []
    oryginal = ex.rozlacz
    ex.rozlacz = lambda: (rozlaczenia.append(1), oryginal())[1]
    k.podlacz_excel(ex)
    k.symuluj_skan_rano(4, {1: "pewna", 2: "pewna"}, projekty={1: 301, 2: 302})
    czekaj(lambda: rp.stan()["plan_id"] == k.stan().rano.plan_id, 10.0, "plan na ramce P", pompa=k.przetworz)
    k.przelacz_tryb("wieczor")
    k.start_skanu()
    k.symuluj_skan("czysta", numer=1)
    czekaj(lambda: rw.stan()["plan_id"] is not None, 10.0, "wynik na ramce W", pompa=k.przetworz)
    t0 = time.perf_counter()
    k.zamknij()
    czas = time.perf_counter() - t0
    assert rp.stan()["plan_id"] is None and rw.stan()["plan_id"] is None and rozlaczenia == [1]
    assert all(not w.is_alive() for kl in ind.klienci() for w in kl._watki) and czas < 2.5
    print(f"\n[kryterium 5] zamkniecie programu {czas * 1000:.0f} ms: ramki W i P zgaszone, klienci zatrzymani, Excel rozlaczony")


# ============================================================================
# okno 1920 x 1080 bez obciec (pasek ramek, okno "Excel: wskaz wiersz")
# ============================================================================
def test_okno_1920x1080_bez_obciec_z_paskiem_ramek_i_oknem_excela(tmp_path, ekrany):
    from stanowisko import excel as EX
    from stanowisko import kontroler_api as K

    ind = IndicateAtrapa()
    k = K.AtrapaKontrolera(tmp_path / "k", zegar=ZegarRano())
    try:
        k.podlacz_ramki(ind)
        skany = k.scenariusz_poranny()
        arkusz, _ = arkusz_zlecen(RANO_START.date())
        k.podlacz_excel(EX.Excel.z_ustawien(ust_excela(tmp_path), zrodlo=arkusz, baza=k.sesja.baza, zegar=lambda: RANO_START))
        e = ekrany(k, (1920, 1080))
        e.klik_rano(skany[6], 11)
        e.klik("praca_rano_bez_projektu")
        e.klik("przycisk_zamknij_piec")
        assert e.jest("excel_panel") and e.jest("napis_ramki") and e.jest("przycisk_test_led")
        e.klik_wiersz("excel_tabela", 1)
        usterki = {}
        for rozmiar in ((1920, 1080), PELNY_EKRAN):
            usterki[rozmiar] = UW.sprawdz_uklad(e, rozmiar)
        k.przelacz_tryb("wieczor")
        e.odczekaj(50)
        usterki["wieczor"] = UW.sprawdz_uklad(e, (1920, 1080))
        if os.environ.get("E3_ZRZUTY"):
            katalog = Path(os.environ["E3_ZRZUTY"])
            katalog.mkdir(parents=True, exist_ok=True)
            e.obraz().save(str(katalog / "a12_wieczor_ramki_1920x1080.png"))
        assert all(not u for u in usterki.values()), usterki
    finally:
        k.zamknij()


# ============================================================================
# polecenia A12 bez ramek i Excela, ustawienia, plik startowy
# ============================================================================
def test_polecenia_a12_bez_ramek_i_excela_odmowa_bez_wyjatku(tmp_path):
    from stanowisko import kontroler_api as K

    k = K.AtrapaKontrolera(tmp_path / "k")
    try:
        assert k.wybierz_operatora("Technik A")
        assert set(K.POLECENIA_A12) <= set(K.POLECENIA) and K.WERSJA_KONTRAKTU >= 4
        s = k.stan()
        assert s.ramki is None and s.excel is None
        for nazwa, argumenty in (("test_led", ()), ("przejmij_ramke", ("P",)), ("excel_zatwierdz", (1, 1)), ("excel_pomin", (1, 1)),
                                 ("excel_odswiez", ()), ("excel_pokaz", ()), ("excel_zamknij", ())):
            odp = k.wykonaj(nazwa, *argumenty)
            assert isinstance(odp, K.Odpowiedz) and not odp and odp.kod, (nazwa, odp)
        assert k.excel_szczegoly(1, 1) is None
        assert not k.wykonaj("przejmij_ramke", "X") and k.wykonaj("przejmij_ramke", "X").kod == K.KOD_ZLE_ARGUMENTY
        ind = IndicateAtrapa()
        k.podlacz_ramki(ind)
        assert k.test_led() and ("tryb", "test_led") in ind.wieczorna.polecenia and ("tryb", "test_led") in ind.poranna.polecenia
        assert k.przejmij_ramke("P") and ("wznow",) in ind.poranna.polecenia
    finally:
        k.zamknij()


def test_ramki_i_excel_z_ustawien_ostrzezenie_bez_awarii(tmp_path):
    """``aplikacja.utworz_ramki`` / ``utworz_excel``: klienci ramek z ``[ramki]`` (identyfikator laptopa w katalogu danych programu,
    nie w repo), Excel z ``[excel]`` z polaczeniem leniwym (bez Excela start sie udaje); zle ustawienia ramek = None + ostrzezenie."""
    from stanowisko import aplikacja as AP
    from stanowisko import baza as B

    ust = ust_excela(tmp_path)
    ust["ramki"].update(wieczorna_host="127.0.0.1", poranna_host="127.0.0.1", port=wolny_port())
    ust["sciezki"]["kalibracja_ramek"] = (tmp_path / "brak" / "kalibracja_ramek.json").as_posix()
    dane = tmp_path / "dane"
    ind, ostrzezenia = AP.utworz_ramki(ust, dane)
    assert ind is not None and ind.wieczorna.adres == ("127.0.0.1", ust["ramki"]["port"]) and (dane / "ramki_laptop_id.txt").is_file()
    assert any("kalibrac" in o for o in ostrzezenia)
    zle = copy.deepcopy(ust)
    zle["ramki"]["klucz"] = "za krotki"
    ind2, ostrzezenia2 = AP.utworz_ramki(zle, dane)
    assert ind2 is None and ostrzezenia2
    baza = B.otworz(tmp_path / "dane" / "s.sqlite")
    try:
        ex, ostrzezenia3 = AP.utworz_excel(ust, baza)
        assert ex is not None and ex.tryb == "pytaj" and ex.baza is baza and ex._zrodlo is None  # COM dopiero przy pierwszym odczycie
    finally:
        baza.zamknij()


# ============================================================================
# runda 2 (recenzja PR #30): B1, P2-P8, D2, D9, decyzja wlasciciela (Enter na ramce = kuweta rozlozona), A10 D-R2
# ============================================================================
def _excel_pytaj(k, tmp_path, arkusz=None):
    from stanowisko import excel as EX

    arkusz = arkusz if arkusz is not None else arkusz_zlecen(RANO_START.date())[0]
    ex = EX.Excel.z_ustawien(ust_excela(tmp_path), zrodlo=arkusz, baza=k.sesja.baza, zegar=lambda: RANO_START)
    k.podlacz_excel(ex)
    return arkusz, ex


def _zd(nr, typ, **pola):
    return {"nr": nr, "typ": typ, "czas_s": 1.0, "rola": "P", "start_id": "s1", "z_historii": False, "nieaktualne": False, **pola}


PLYTKA_4 = ({1: "pewna", 2: "pewna", 3: "pewna", 5: "pewna"}, {1: 301, 2: 302, 3: 303, 5: 304})  # zlecenia 3200 (3 z 3), 3207 (1 z 1)


def test_b1_podwojne_klikniecie_zatwierdz_i_pomin_jeden_zapis(tmp_path, ekrany):
    """B1: po zapisie nastepna pozycja NIE jest uzbrojona - podwojne klikniecie "Zatwierdz" / "Pomin" = jeden wpis; "Zatwierdz"
    aktywne dopiero po kliknieciu pozycji na liscie."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    from stanowisko import kontroler_api as K

    k = K.AtrapaKontrolera(tmp_path / "k", zegar=ZegarRano())
    try:
        k.przelacz_tryb("rano")
        k.wybierz_operatora("Technik A")
        arkusz, _ = _excel_pytaj(k, tmp_path)
        k.symuluj_skan_rano(4, PLYTKA_4[0], projekty=PLYTKA_4[1])
        e = ekrany(k)
        e.klik("przycisk_zamknij_piec")
        e.czekaj(lambda: e.jest("excel_panel") and k.stan().excel.w_toku == 0, 10.0, "okno Excela")
        assert [p.kuweta for p in k.stan().excel.pozycje] == ["3200", "3207"] and not e.aktywny("excel_zatwierdz") and e.jest("excel_wybierz")
        e.klik_wiersz("excel_tabela", 0)
        assert e.aktywny("excel_zatwierdz")
        b = e.w("excel_zatwierdz")
        QTest.mouseClick(b, Qt.MouseButton.LeftButton)
        QTest.mouseClick(b, Qt.MouseButton.LeftButton)  # drugie klikniecie (podwojne / Excel odpowiada powoli)
        QTest.mouseDClick(b, Qt.MouseButton.LeftButton)
        e.odczekaj(50)
        zapisy = [op for op in arkusz.operacje if op[0] == "ustaw_wypelnienie"]
        poz = k.stan().excel.pozycje
        assert len(zapisy) == 1 and poz[0].zalatwiona and not poz[1].zalatwiona, (zapisy, poz)
        assert e.okno.ekran_rano.excel.pokazana() == (poz[1].sesja_pieca_id, poz[1].zlecenie_id) and not e.okno.ekran_rano.excel.wybrana()
        assert not e.aktywny("excel_zatwierdz") and not e.aktywny("excel_pomin")
        e.klik_wiersz("excel_tabela", 1)
        p = e.w("excel_pomin")
        QTest.mouseClick(p, Qt.MouseButton.LeftButton)
        QTest.mouseClick(p, Qt.MouseButton.LeftButton)
        e.odczekaj(50)
        wpisy = k.sesja.baza.wiersze("SELECT wynik FROM excel_zapisy ORDER BY id")
        assert [w["wynik"] for w in wpisy] == ["zapisano", "pominieto"]
        print(f"\n[B1] podwojne klikniecie: zapisow koloru {len(zapisy)}, wpisow logu {len(wpisy)} (zapisano, pominieto)")
    finally:
        k.zamknij()


def test_p2_blad_planu_gasi_ramke_komunikat_i_ponowienie(tmp_path, monkeypatch):
    from stanowisko import kontroler_api as K

    monkeypatch.setattr(K, "OKRES_PONOWIENIA_PLANU_S", 0.05)
    ind = IndicateAtrapa()
    k = _poranek_kontroler(tmp_path / "k", ind)
    try:
        k.symuluj_skan_rano(4, PLYTKA_4[0], projekty=PLYTKA_4[1])
        plany = [p for p in ind.poranna.polecenia if p[0] == "plan"]
        assert len(plany) == 1
        oryginal = k.rano.plan_plytek

        def zepsuty(*a, **kw):
            raise RuntimeError("blad odczytu bazy")

        k.rano.plan_plytek = zepsuty
        n = len(ind.poranna.polecenia)
        assert k.ustaw_kolejnosc("numer")  # zmiana pieca na ekranie -> plan od nowa -> blad
        assert ("zgas",) in ind.poranna.polecenia[n:]  # stary plan nie swieci
        czekaj(lambda: any(x.rodzaj == "ramka_plan_blad" for x in k.stan().komunikaty), 3.0, "komunikat bledu planu", pompa=k.przetworz)
        k.rano.plan_plytek = oryginal
        czekaj(lambda: len([p for p in ind.poranna.polecenia if p[0] == "plan"]) == 2, 3.0, "ponowienie planu", pompa=k.przetworz)
        czekaj(lambda: not any(x.rodzaj == "ramka_plan_blad" for x in k.stan().komunikaty), 3.0, "komunikat znika", pompa=k.przetworz)
    finally:
        k.zamknij()


def test_p3_zamknij_piec_z_ramki_w_trybie_wieczor_gasi_ramke_p(tmp_path):
    ind = IndicateAtrapa()
    k = _poranek_kontroler(tmp_path / "k", ind)
    try:
        k.symuluj_skan_rano(4, PLYTKA_4[0], projekty=PLYTKA_4[1])
        plan_id, sid = k.stan().rano.plan_id, k.stan().rano.sesja_pieca_id
        assert k.przelacz_tryb("wieczor")
        n = len(ind.poranna.polecenia)
        ind.poranna.zdarzenia.append(_zd(1, "zamknij_piec", plan_id=plan_id, plytka=4))
        k.przetworz()
        assert k.sesja.baza.wiersz("SELECT zamknieto FROM sesje_pieca WHERE id = ?", (sid,))["zamknieto"]
        assert ("zgas",) in ind.poranna.polecenia[n:] and k.stan().tryb == "wieczor"
    finally:
        k.zamknij()


def test_p4_pozycje_excela_tozsamoscia_po_odswiezeniu(tmp_path):
    from stanowisko import kontroler_api as K
    from stanowisko import statusy as ST

    k = K.AtrapaKontrolera(tmp_path / "k", zegar=ZegarRano())
    try:
        k.przelacz_tryb("rano")
        k.wybierz_operatora("Technik A")
        _excel_pytaj(k, tmp_path)
        k.symuluj_skan_rano(4, PLYTKA_4[0], projekty=PLYTKA_4[1])
        assert k.zamknij_piec(k.stan().rano.sesja_pieca_id)
        czekaj(lambda: k.stan().excel.w_toku == 0, 5.0, "propozycje", pompa=k.przetworz)
        a, b = k.stan().excel.pozycje
        assert (a.kuweta, a.nr, b.kuweta, b.nr) == ("3200", 0, "3207", 1)
        assert k.excel_zatwierdz(a.sesja_pieca_id, a.zlecenie_id)
        assert k.excel_odswiez()
        (b2,) = k.stan().excel.pozycje
        assert (b2.kuweta, b2.nr, b2.zlecenie_id) == ("3207", 0, b.zlecenie_id)  # numer na liscie sie przesunal, tozsamosc - nie
        odp = k.excel_pomin(a.sesja_pieca_id, a.zlecenie_id)  # stary wybor (pozycja juz zalatwiona i zniknela z listy)
        assert not odp and odp.tekst == ST.NAPIS_POZYCJA_EXCELA_INNA
        assert not k.stan().excel.pozycje[0].zalatwiona  # 3207 nie zostal pominiety zamiast 3200
        assert k.excel_pomin(b.sesja_pieca_id, b.zlecenie_id) and k.stan().excel.pozycje[0].zalatwiona
    finally:
        k.zamknij()


def test_p5_nowy_piec_nie_zastepuje_po_cichu_niezalatwionych(tmp_path):
    from stanowisko import kontroler_api as K

    k = K.AtrapaKontrolera(tmp_path / "k", zegar=ZegarRano())
    try:
        k.przelacz_tryb("rano")
        k.wybierz_operatora("Technik A")
        _excel_pytaj(k, tmp_path)
        k.symuluj_skan_rano(4, PLYTKA_4[0], projekty=PLYTKA_4[1])
        assert k.zamknij_piec(k.stan().rano.sesja_pieca_id)
        czekaj(lambda: k.stan().excel.w_toku == 0, 5.0, "propozycje pieca 1", pompa=k.przetworz)
        piec1 = k.stan().excel.sesja_pieca_id
        assert k.excel_zamknij()  # "Pozniej"
        k.symuluj_skan_rano(5, {1: "pewna", 2: "pewna"}, projekty={1: 305, 2: 306})
        assert k.zamknij_piec(k.stan().rano.sesja_pieca_id)
        czekaj(lambda: k.stan().excel.w_toku == 0, 5.0, "propozycje pieca 2", pompa=k.przetworz)
        ex = k.stan().excel
        piec2 = ex.sesja_pieca_id
        assert piec2 != piec1 and [p.kuweta for p in ex.pozycje] == ["3214"]
        assert [z[0] for z in ex.zalegle] == [piec1] and ex.zalegle[0][3] == 2  # piec 1 nie zniknal po cichu
        assert any(x.id == f"excel_zalegle:{piec1}" for x in k.stan().komunikaty)
        assert k.excel_pokaz(piec1)
        ex = k.stan().excel
        assert ex.sesja_pieca_id == piec1 and [p.kuweta for p in ex.pozycje] == ["3200", "3207"] and [z[0] for z in ex.zalegle] == [piec2]
        assert not any(x.id == f"excel_zalegle:{piec1}" for x in k.stan().komunikaty)
    finally:
        k.zamknij()
    k = K.AtrapaKontrolera(tmp_path / "k", zegar=ZegarRano())  # restart: przypomnienie o obu piecach
    try:
        _excel_pytaj(k, tmp_path)
        assert {z[0] for z in k.stan().excel.zalegle} == {piec1, piec2}
        assert {x.id for x in k.stan().komunikaty} >= {f"excel_zalegle:{piec1}", f"excel_zalegle:{piec2}"}
    finally:
        k.zamknij()


def test_p6_powtorzony_i_przemianowany_plik_nie_gasi_ramki_w_i_silnik_wrocil(tmp_path):
    """P6 (Aplikacja bez startu silnika, klient ramek bez sieci): znacznik ramki W tylko dla skanu zleconego do analizy - plik
    przemianowany / ta sama tresc w kolejce nie gasi wyniku. A10 D-R2: powrot silnika po awarii = wpis ``silnik_wrocil``."""
    import types

    from stanowisko import aplikacja as AP

    k = AP.Aplikacja(TK.ustawienia_probne(tmp_path), zegar=lambda: TK.START)
    try:
        ind = IndicateAtrapa()
        k.podlacz_ramki(ind)

        def skan(plik, sha16):
            return types.SimpleNamespace(plik=str(tmp_path / plik), sha16=sha16, rozmiar=1000, mtime_ns=1, trojkaty=10, zastany=False, ponowny=False,
                                         duplikat=False)

        def znaczniki():
            return sum(1 for p in ind.wieczorna.polecenia if p == ("tryb", "skanowanie"))

        k._zdarzenie_skrzynki("skan", skan("a.stl", "0123456789abcdef"))
        assert znaczniki() == 1 and len(k._wstrzymane) == 1
        k._zdarzenie_skrzynki("skan", skan("b.stl", "0123456789abcdef"))  # ta sama tresc pod inna nazwa (przemianowany / powtorka)
        assert znaczniki() == 1 and len(k._wstrzymane) == 1
        k._zdarzenie_skrzynki("skan", skan("c.stl", "fedcba9876543210"))  # nowy skan
        assert znaczniki() == 2
        k._silnik_nie_startuje = True
        k._zdarzenie_silnika(types.SimpleNamespace(typ="gotowy"))
        assert k.sesja.baza.wiersz("SELECT count(*) AS n FROM zdarzenia WHERE zrodlo = 'silnik' AND typ = 'silnik_wrocil'")["n"] == 1
    finally:
        k.zamknij()


def test_p7_stare_zamknij_piec_po_ponownym_otwarciu_nieaktualne(tmp_path):
    ind = IndicateAtrapa()
    k = _poranek_kontroler(tmp_path / "k", ind)
    try:
        k.symuluj_skan_rano(4, PLYTKA_4[0], projekty=PLYTKA_4[1])
        plan_id, sid = k.stan().rano.plan_id, k.stan().rano.sesja_pieca_id
        assert k.zamknij_piec(sid) and k.otworz_piec_ponownie(sid) and k.stan().rano.otwarty
        assert ind.poranna.wersja == 2  # plan ponownie otwartego pieca wyslany (nowa wersja)
        ind.poranna.zdarzenia.append(_zd(5, "zamknij_piec", plan_id=plan_id, plytka=4))  # klawisz sprzed zamkniecia (przerwa Wi-Fi)
        k.przetworz()
        assert k.stan().rano.otwarty and ramka_zdarzen(k.sesja.baza, typ="zamknij_piec")[-1]["skutek"] == "nieaktualne"
        ind.poranna.zdarzenia += [_zd(6, "plan_przyjety", plan_id=plan_id, wersja=2), _zd(7, "zamknij_piec", plan_id=plan_id, plytka=4)]
        k.przetworz()
        assert not k.stan().rano.otwarty and ramka_zdarzen(k.sesja.baza, typ="zamknij_piec")[-1]["skutek"] == "zamknieto"
    finally:
        k.zamknij()


def test_p8_nieoczekiwany_blad_excela_komunikat_z_lista_kuwet(tmp_path):
    from stanowisko import kontroler_api as K
    from stanowisko import statusy as ST

    k = K.AtrapaKontrolera(tmp_path / "k", zegar=ZegarRano())
    try:
        k.przelacz_tryb("rano")
        k.wybierz_operatora("Technik A")
        _, ex = _excel_pytaj(k, tmp_path)

        def zepsute(*a, **kw):
            raise TypeError("nieznany typ komorki")

        ex.propozycje = zepsute
        k.symuluj_skan_rano(4, PLYTKA_4[0], projekty=PLYTKA_4[1])
        assert k.zamknij_piec(k.stan().rano.sesja_pieca_id)
        czekaj(lambda: k.stan().excel.w_toku == 0, 5.0, "krok Excela", pompa=k.przetworz)
        kom = next(x for x in k.stan().komunikaty if x.id == K.ID_EXCEL)
        assert kom.rodzaj == "excel_blad" and "3200" in kom.tekst and "3207" in kom.tekst and k.stan().excel.blad == ST.NAPIS_EXCEL_BLAD_PROGRAMU
    finally:
        k.zamknij()


def test_d2_baza_zajeta_zdarzenia_ramki_czekaja_i_wracaja(tmp_path):
    from stanowisko import baza as B

    ind = IndicateAtrapa()
    k = _poranek_kontroler(tmp_path / "k", ind)
    try:
        k.symuluj_skan_rano(4, PLYTKA_4[0], projekty=PLYTKA_4[1])
        plan_id = k.stan().rano.plan_id
        oryginal = k.sesja.baza.zdarzenie
        zajeta = {"tak": True}

        def zdarzenie(zrodlo, *a, **kw):
            if zrodlo.startswith("ramka") and zajeta["tak"]:
                raise B.BladBazy("baza zajeta")
            return oryginal(zrodlo, *a, **kw)

        k.sesja.baza.zdarzenie = zdarzenie
        ind.poranna.zdarzenia += [_zd(1, "plytka", plytka=4, poprzednia=0), _zd(2, "potwierdzenie", plan_id=plan_id, plytka=4, kuweta="3200"),
                                  _zd(3, "zamknij_piec", plan_id=plan_id, plytka=4)]
        k.przetworz()
        k.przetworz()
        assert ramka_zdarzen(k.sesja.baza) == [] and k.stan().rano.otwarty  # nic nie zapisane, nic nie zgubione
        zajeta["tak"] = False
        k.przetworz()
        assert [(z["nr"], z["typ"]) for z in ramka_zdarzen(k.sesja.baza)] == [(1, "plytka"), (2, "potwierdzenie"), (3, "zamknij_piec")]
        assert not k.stan().rano.otwarty
        k.przetworz()
        assert len(ramka_zdarzen(k.sesja.baza)) == 3
    finally:
        k.zamknij()


def test_d9_poprzednia_proba_z_bledem_widoczna_przy_pozycji(tmp_path):
    from stanowisko import kontroler_api as K

    k = K.AtrapaKontrolera(tmp_path / "k", zegar=ZegarRano())
    try:
        k.przelacz_tryb("rano")
        k.wybierz_operatora("Technik A")
        k.symuluj_skan_rano(4, PLYTKA_4[0], projekty=PLYTKA_4[1])
        assert k.zamknij_piec(k.stan().rano.sesja_pieca_id)
        sid = k.stan().rano.sesja_pieca_id
        z3200 = k.sesja.baza.wiersz("SELECT id FROM zlecenia WHERE kuweta = '3200'")["id"]
        k.sesja.baza.wstaw("excel_zapisy", czas=RANO_START.isoformat(), sesja_pieca_id=sid, zlecenie_id=z3200, kuweta="3200", wiersz=77, regula=2,
                           wynik="blad", tryb="pytaj", operator="Technik A")
        _excel_pytaj(k, tmp_path)
        assert k.excel_pokaz(sid)
        a, b = k.stan().excel.pozycje
        assert (a.kuweta, a.poprzedni_blad, a.poprzedni_wiersz) == ("3200", True, 77) and not b.poprzedni_blad
    finally:
        k.zamknij()


def test_enter_na_ramce_kuweta_rozlozona_na_ekranie_takze_po_restarcie(tmp_path):
    """Decyzja (koordynator, runda 2): Enter na ramce porannej = kuweta rozlozona na ekranie - gdy potwierdzona na WSZYSTKICH
    plytkach planu, na ktorych lezy; Backspace (cofniecie) na ramce - znow do rozlozenia i biezaca; po restarcie z dziennika."""
    ind = IndicateAtrapa()
    k = _poranek_kontroler(tmp_path / "k", ind)

    def kuweta(k_, nr):
        return next(x for x in k_.stan().rano.kuwety if x.kuweta == nr)

    try:
        k.symuluj_skan_rano(4, {1: "pewna", 2: "pewna", 3: "pewna", 5: "pewna"}, projekty={1: 301, 2: 302, 3: 303, 5: 305})
        k.symuluj_skan_rano(5, {1: "pewna"}, projekty={1: 306})  # kuweta 3214 na plytkach 4 i 5
        plan_id = k.stan().rano.plan_id
        assert kuweta(k, "3214").plytki == (4, 5)
        ind.poranna.potw = [[4, "3214"]]
        ind.poranna.zdarzenia.append(_zd(1, "potwierdzenie", plan_id=plan_id, plytka=4, kuweta="3214"))
        k.przetworz()
        assert not kuweta(k, "3214").potwierdzona  # potwierdzona tylko na jednej z dwoch plytek
        ind.poranna.potw = [[4, "3214"], [5, "3214"], [4, "3200"]]
        ind.poranna.zdarzenia += [_zd(2, "potwierdzenie", plan_id=plan_id, plytka=5, kuweta="3214"),
                                  _zd(3, "potwierdzenie", plan_id=plan_id, plytka=4, kuweta="3200")]
        k.przetworz()
        assert kuweta(k, "3214").potwierdzona and kuweta(k, "3200").potwierdzona
        ind.poranna.potw = [[4, "3214"], [4, "3200"]]
        ind.poranna.zdarzenia.append(_zd(4, "cofniecie", plan_id=plan_id, plytka=5, kuweta="3214"))
        k.przetworz()
        assert not kuweta(k, "3214").potwierdzona and kuweta(k, "3200").potwierdzona and k.stan().rano.kuweta_biezaca == "3214"
    finally:
        k.zamknij()
    k = _poranek_kontroler(tmp_path / "k", IndicateAtrapa())
    try:
        assert not kuweta(k, "3214").potwierdzona and kuweta(k, "3200").potwierdzona
    finally:
        k.zamknij()
