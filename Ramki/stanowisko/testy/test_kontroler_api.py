"""kontroler_api (E3-A3a): WSPOLNY test kontraktu kontrolera - ten sam zestaw dla atrapy i dla prawdziwej aplikacji.

Kazdy test dostaje ``st`` - stanowisko probne z kontrolerem (``st.k``), sztucznym zegarem (``st.przesun``) i funkcja
``st.wrzuc(rodzaj, ...)``, ktora "wrzuca skan":
* ``atrapa``     - ``AtrapaKontrolera.symuluj_skan`` (bez skanera i silnika),
* ``aplikacja``  - plik STL zapisany do folderu skanera prawdziwej ``aplikacja.Aplikacja``; ``scanner`` go zauwaza,
  ``silnik`` w osobnym procesie wykonuje ``analiza_sztuczna`` (ponizej) zamiast ``porownaj``, wynik trafia do ``session``.
Oba warianty musza dac ten sam stan i te same odpowiedzi (kryterium (j) paczki). Wariant ``aplikacja`` jest pomijany,
dopoki nie ma modulu ``stanowisko.aplikacja``.

Dane sa sztuczne: opis plytki (uklad, numer, prace w gniazdach) jest zapisany w tresci pliku "skanu" i odczytywany przez
``analiza_sztuczna`` w procesie silnika - dlatego ten modul na poziomie importu uzywa tylko biblioteki standardowej i pytest.
"""
from __future__ import annotations

import copy
import dataclasses
import datetime as dt
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

STANOWISKO = Path(__file__).resolve().parent.parent
FUNKCJA_SZTUCZNA = "test_kontroler_api:analiza_sztuczna"
FOLDER_ZLECENIA = "9911 Zmyslona Fikcja"  # fikcyjna nazwa folderu zlecenia (kryterium (i)): nie moze wyjsc poza 4 tabele bazy
START = dt.datetime(2026, 11, 17, 19, 0, 0)  # wtorek, zmiana 2
ZESTAW_ZWYKLY = {1: "zielony", 2: "czerwony", 3: "zolty", 4: "szary", 5: "pomaranczowy", 6: "nie_sprawdzono", 7: "blad_inspekcji", 8: "zielony",
                 9: "czerwony"}


# ----------------------------------------------------------------------------
# plik sztucznego skanu i funkcja wykonywana W PROCESIE SILNIKA zamiast porownaj
# ----------------------------------------------------------------------------
def plik_skanu(opis: dict) -> bytes:
    """Poprawny binarny STL (naglowek 80 B + liczba trojkatow + 50 B na trojkat), ktorego "trojkaty" to opis plytki w JSON."""
    tresc = json.dumps(opis, sort_keys=True).encode("ascii")
    tresc += b" " * (-len(tresc) % 50)
    return b"QC-SKAN-SZTUCZNY".ljust(80, b" ") + (len(tresc) // 50).to_bytes(4, "little") + tresc


def opis_z_pliku(plik) -> dict:
    return json.loads(Path(plik).read_bytes()[84:].decode("ascii"))


def analiza_sztuczna(skan, foldery, plytka, ust, wspolczynnik=None, numer=None, *reszta, postep=None, **kw):
    """Udaje ``porownaj.porownaj``: czyta opis z pliku skanu i zwraca ``kontroler_api.sztuczny_wynik``. Pola opisu:
    ``uklad``, ``numer``, ``gniazda``, ``projekty``, ``poza``, ``uklad_zgodny``; ``spij`` (sekundy pracy z postepem),
    ``blad`` (wyjatek z nazwa folderu puli w tresci - sprawdza, ze nazwy nie wychodza), ``zabij`` (proces znika)."""
    from stanowisko import kontroler_api as K

    opis = opis_z_pliku(skan)
    if postep is not None:
        postep("wczytanie skanu", 0.2)
    if opis.get("brama"):  # D13: analiza czeka na plik-brame, ktory tworzy test (zamiast zakladac, ile trwa "spij")
        koniec, nastepny = time.monotonic() + float(opis.get("brama_limit_s", 300)), 0.0
        while not Path(opis["brama"]).exists() and time.monotonic() < koniec:
            if postep is not None and time.monotonic() >= nastepny:
                postep("identyfikacja i inspekcja gniazd (match + inspect)", 0.3)
                nastepny = time.monotonic() + 0.25
            time.sleep(0.02)
    kroki = max(1, int(float(opis.get("spij", 0)) / 0.05))
    for i in range(kroki):
        if opis.get("spij"):
            time.sleep(0.05)
        if postep is not None:
            postep("identyfikacja i inspekcja gniazd (match + inspect)", 0.3 + 0.6 * (i + 1) / kroki)
    if opis.get("zabij"):
        os._exit(7)
    projekty = [p for f in foldery for p in sorted(Path(f).rglob("*.stl"))]
    if opis.get("podglad") and kw.get("podglad") is not None:  # jak porownaj: punkty i odchylki gniazd -> silnik zapisze *_podglad.npz
        import numpy as np

        for nr in (opis.get("gniazda") or {}):
            wpis = type("WynikInspekcji", (), {})()
            wpis._P, wpis._d = np.zeros((20, 3)), np.full(20, -0.05)
            kw["podglad"][int(nr)] = wpis
    if opis.get("blad"):
        gdzie = f"{projekty[0].parent.name} ({projekty[0]})" if projekty else "?"
        raise ValueError(f"blad sztuczny w projekcie z folderu {gdzie}")
    if not projekty:
        raise SystemExit(f"brak projektow STL w {', '.join(map(str, foldery))}")
    if opis.get("rano"):  # E3-A7: plytka poranna z kandydatami (``sztuczny_wynik_rano``); JSON: klucze napisami, pary listami
        wynik = K.sztuczny_wynik_rano(opis.get("uklad", "poranna"), opis.get("numer") if numer is None else numer,
                                      {int(k): v for k, v in (opis.get("gniazda") or {}).items()}, skan=Path(skan).name,
                                      projekty={int(k): (tuple(v) if isinstance(v, list) else v) for k, v in (opis.get("projekty") or {}).items()})
        wynik["foldery_projektow"] = [str(f) for f in foldery]
        return wynik
    wynik = K.sztuczny_wynik(opis.get("uklad", "wieczorna"), opis.get("numer") if numer is None else numer,
                             {int(k): v for k, v in (opis.get("gniazda") or {}).items()}, uklad_zgodny=opis.get("uklad_zgodny", True),
                             poza_gniazdem=int(opis.get("poza", 0)), skan=Path(skan).name,
                             projekty={int(k): v for k, v in (opis.get("projekty") or {}).items()})
    wynik["foldery_projektow"] = [str(f) for f in foldery]
    wynik["wspolczynnik"] = wspolczynnik
    wynik["projekty"] = len(projekty)
    if projekty:  # jak prawdziwa analiza: uwagi z nazwa pliku i folderu projektu - silnik i sesja maja je wyciac
        wynik["uwagi"] = [f"zob. {projekty[0].parent.name} / {projekty[0].name}"]
    return wynik


# ----------------------------------------------------------------------------
# stanowiska probne
# ----------------------------------------------------------------------------
OPISY_SKANOW = {
    "zwykla": {"gniazda": ZESTAW_ZWYKLY},
    "czysta": {"gniazda": {1: "zielony", 2: "zielony", 3: "zielony", 4: "zielony"}},
    "do_powtorzenia": {"gniazda": {1: "zielony", 2: "skan_ponownie", 3: "podwojny", 4: "czerwony"}},
    "niezgodny_uklad": {"gniazda": {}, "uklad_zgodny": False},
    "nie_z_trybu": {"gniazda": {1: "zielony", 2: "zielony", 3: "czerwony"}, "uklad": "poranna"},
    "bez_numeru": {"gniazda": {1: "zielony", 2: "czerwony", 3: "zielony"}, "numer": None},
    "blad": {"gniazda": {}, "blad": True},
}


class Stanowisko:
    """Wspolne narzedzia stanowiska probnego: sztuczny zegar, kontroler ``k`` i ``wrzuc``."""

    nazwa = ""

    def __init__(self):
        self.teraz = START
        self.sygnaly: list = []

    def zegar(self) -> dt.datetime:
        return self.teraz

    def przesun(self, minut: float) -> None:
        self.teraz += dt.timedelta(minutes=minut)

    def opis(self, rodzaj: str, numer, gniazda, projekty, uklad, poza) -> dict:
        opis = copy.deepcopy(OPISY_SKANOW[rodzaj])
        opis.setdefault("numer", numer)
        if rodzaj == "bez_numeru":
            opis["numer"] = None
        if gniazda is not None:
            opis["gniazda"] = gniazda
        if projekty is not None:
            opis["projekty"] = projekty
        if uklad is not None:
            opis["uklad"] = uklad
        opis.setdefault("uklad", "wieczorna")
        opis["poza"] = poza
        return opis

    def wynik(self, opis: dict) -> dict:
        from stanowisko import kontroler_api as K

        return K.sztuczny_wynik(opis["uklad"], opis["numer"], opis["gniazda"], uklad_zgodny=opis.get("uklad_zgodny", True),
                                poza_gniazdem=opis.get("poza", 0), projekty=opis.get("projekty"))

    def stan(self):
        return self.k.stan()

    def poranek(self) -> None:
        """E3-A7: pula poranna (fikcyjne zlecenia ``indeks_rano_sztuczny``), osoba i tryb "rano"."""
        from stanowisko import kontroler_api as K

        K.indeks_rano_sztuczny(self.k.sesja.baza, self.k.sesja.teraz())
        assert self.k.przelacz_tryb("rano") and self.k.wybierz_operatora("Technik A")

    def odbierz(self, z) -> None:
        self.sygnaly.append(z)

    def czekaj(self, warunek, limit_s: float = 60.0, co: str = "") -> None:
        """Wola ``przetworz()`` (jak zegar okna), az warunek bedzie spelniony."""
        koniec = time.monotonic() + limit_s
        while True:
            self.k.przetworz()
            if warunek():
                return
            assert time.monotonic() < koniec, f"nie doczekalem sie: {co}; stan: {self.k.stan().kolejka}, komunikaty {[k.rodzaj for k in self.k.stan().komunikaty]}"
            time.sleep(0.01)


class StanowiskoAtrapy(Stanowisko):
    nazwa = "atrapa"

    def __init__(self, tmp_path: Path):
        super().__init__()
        from stanowisko import kontroler_api as K

        self.k = K.AtrapaKontrolera(tmp_path / "atrapa", operatorzy=("Technik A", "Technik B"), zegar=self.zegar)
        self.k.subskrybuj(self.odbierz)
        self.folder_puli = "(atrapa)"

    def start_nieudany(self) -> None:
        self.k.symuluj_skaner(start_udany=False)

    def wrzuc(self, rodzaj: str = "zwykla", *, numer=1, gniazda=None, projekty=None, uklad=None, poza=0) -> int:
        opis = self.opis(rodzaj, numer, gniazda, projekty, uklad, poza)
        return self.k.symuluj_skan(rodzaj, numer=opis["numer"], uklad=opis["uklad"], gniazda=opis["gniazda"], projekty=opis.get("projekty"),
                                   poza_gniazdem=poza)

    def starty_skanu(self) -> int:
        return len(self.k.starty_skanu)

    def wrzuc_rano(self, numer, gniazda: dict, projekty: dict | None = None, *, uklad: str = "poranna") -> int:
        return self.k.symuluj_skan_rano(numer, gniazda, projekty=projekty, uklad=uklad)

    def koniec(self) -> None:
        self.k.zamknij()


def ustawienia_probne(tmp_path: Path, operatorzy=("Technik A", "Technik B")) -> dict:
    """Ustawienia ze wzoru programu ze sciezkami w ``tmp_path`` i szybkim obserwatorem folderu."""
    from stanowisko import ustawienia as UST

    ust = copy.deepcopy(UST.wczytaj_ustawienia(UST.PLIK_PRZYKLADU))
    for klucz, wartosc in (("folder_eksportu_skanera", "eksport"), ("folder_cyrkon", "projekty"), ("baza", "dane/stanowisko.sqlite"),
                           ("wyniki", "dane/wyniki"), ("podglady", "dane/podglady"), ("pula_cache", "dane/pula_cache"), ("logi", "dane/logi")):
        ust["sciezki"][klucz] = (tmp_path / wartosc).as_posix()
    ust["sesja"]["operatorzy"] = list(operatorzy)
    ust["scanner"].update(stabilizacja_ms=40)
    return ust


def pula_probna(tmp_path: Path, ile: int = 3) -> Path:
    """Folder projektow z ``ile`` plikami STL w podfolderze o fikcyjnej nazwie zlecenia (tresc plikow bez znaczenia)."""
    folder = tmp_path / "projekty" / FOLDER_ZLECENIA
    folder.mkdir(parents=True, exist_ok=True)
    for i in range(ile):
        (folder / f"Fikcja-{11 + i}-crown_cad.stl").write_bytes(plik_skanu({"projekt": i}))
    return folder.parent


PARAMETRY_SCANNERA = {"okres_s": 0.02, "przeglad_s": 0.3, "odrzuc_po_s": 0.6, "informuj_po_s": 0.5, "informuj_co_s": 1.0}


class StanowiskoAplikacji(Stanowisko):
    nazwa = "aplikacja"

    def __init__(self, tmp_path: Path, **parametry):
        super().__init__()
        from stanowisko import aplikacja as AP
        from stanowisko import kontroler_api as K
        from stanowisko import scanner as SC

        self.tmp = tmp_path
        self.eksport = tmp_path / "eksport"
        self.eksport.mkdir(parents=True, exist_ok=True)
        self.folder_puli = str(pula_probna(tmp_path))
        self.ust = parametry.pop("ust", None) or ustawienia_probne(tmp_path)
        self.atrapa_startu = SC.AtrapaStartuSkanu()
        self._nr = len(list(self.eksport.rglob("*.stl")))
        self.k = AP.Aplikacja(self.ust, **{"zegar": self.zegar, "funkcja_analizy": FUNKCJA_SZTUCZNA, "start_skanu": self.atrapa_startu,
                                           "parametry_scannera": PARAMETRY_SCANNERA, **parametry})
        self.k.subskrybuj(self.odbierz)
        self.k.start()
        K.indeks_sztuczny(self.k.sesja.baza, self.k.sesja.teraz())
        self.czekaj(lambda: self.k.stan().pula.liczba_stl is not None, 30.0, "pula policzona")

    def start_nieudany(self) -> None:
        self.k.scanner.akcja_startu = lambda: False  # skaner nie odpowiada na "start skanu"

    def zapisz(self, opis: dict, podfolder: str = "") -> Path:
        """Zapisuje plik sztucznego skanu do folderu skanera (nie czeka na analize)."""
        self._nr += 1
        opis = {**opis, "sol": f"{self._nr}-{time.time_ns()}"}  # kazdy skan ma inna tresc (inny sha16), jak prawdziwe skany
        cel = self.eksport / podfolder / f"skan_{self._nr:03d}.stl"
        cel.parent.mkdir(parents=True, exist_ok=True)
        tmp = cel.with_suffix(".tmp")
        tmp.write_bytes(plik_skanu(opis))
        os.replace(tmp, cel)
        return cel

    def _skany(self) -> set:
        """skan_id plytek w stanie: wieczornych i - w trybie "rano" - plytek pieca (E3-A7)."""
        s = self.k.stan()
        return {p.skan_id for p in s.plytki} | ({p.skan_id for p in s.rano.plytki} if s.rano is not None else set())

    def wrzuc(self, rodzaj: str = "zwykla", *, numer=1, gniazda=None, projekty=None, uklad=None, poza=0) -> int:
        przed = self._skany()
        self.zapisz(self.opis(rodzaj, numer, gniazda, projekty, uklad, poza))
        self.czekaj(lambda: self._skany() - przed, 90.0, f"skan {rodzaj} w stanie")
        return max(self._skany() - przed)

    @staticmethod
    def opis_rano(numer, gniazda: dict, projekty: dict | None = None, *, uklad: str = "poranna", spij: float = 0.0) -> dict:
        """Opis sztucznego skanu plytki porannej (``kontroler_api.sztuczny_wynik_rano`` w procesie silnika)."""
        return {"rano": True, "uklad": uklad, "numer": numer, "gniazda": gniazda, "projekty": projekty or {}, "poza": 0, "spij": spij}

    def wrzuc_rano(self, numer, gniazda: dict, projekty: dict | None = None, *, uklad: str = "poranna") -> int:
        przed = self._skany()
        self.zapisz(self.opis_rano(numer, gniazda, projekty, uklad=uklad))
        self.czekaj(lambda: self._skany() - przed, 90.0, f"skan poranny plytki {numer} w stanie")
        return max(self._skany() - przed)

    def starty_skanu(self) -> int:
        return len(self.atrapa_startu.wywolania)

    def koniec(self) -> None:
        self.k.zamknij()


def _jest_aplikacja() -> bool:
    return (STANOWISKO / "stanowisko" / "aplikacja.py").is_file()


@pytest.fixture(scope="module", autouse=True)
def _qt_przed_silnikiem():
    """Qt ladowane przed pierwszym uzyciem silnika - w tej kolejnosci pracuje aplikacja (patrz ``test_silnik``)."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import PySide6.QtCore  # noqa: F401


@pytest.fixture(params=["atrapa", "aplikacja"])
def st(request, tmp_path):
    if request.param == "atrapa":
        stanowisko = StanowiskoAtrapy(tmp_path)
    else:
        if not _jest_aplikacja():
            pytest.skip("brak modulu stanowisko.aplikacja (wariant prawdziwego kontrolera)")
        stanowisko = StanowiskoAplikacji(tmp_path)
    yield stanowisko
    stanowisko.koniec()


def kolory(plytka) -> dict:
    """(gniazdo, nr fragmentu) -> klasa koloru kazdej pracy na plytce ze stanu kontrolera."""
    return {(p.gniazdo, p.nr_fragmentu): p.kolor for p in plytka.prace}


def bez_zielonego(plytka) -> None:
    from stanowisko import statusy as ST

    assert plytka.zielonych == 0
    assert all(p.kolor != "zielony" and p.status not in ST.STATUSY_ZIELONE for p in plytka.prace), [(p.gniazdo, p.status) for p in plytka.prace]
    assert all(g.kolor != "zielony" and g.status not in ST.STATUSY_ZIELONE for g in plytka.gniazda)


# ----------------------------------------------------------------------------
# kontrakt: stan
# ----------------------------------------------------------------------------
def test_stan_poczatkowy(st):
    from stanowisko import kontroler_api as K

    s = st.stan()
    assert isinstance(s, K.StanAplikacji) and dataclasses.is_dataclass(s)
    assert (s.doba, s.zmiana, s.tryb) == ("2026-11-17", 2, "wieczor")
    assert s.operator is None and s.wymaga_operatora and s.operatorzy == ("Technik A", "Technik B")
    assert s.plytki == () and s.pytania == () and s.do_dofrezowania == () and s.biezaca_plytka is None
    assert isinstance(s.kolejka, K.Kolejka) and s.kolejka.razem == 0 and s.analiza is None
    assert isinstance(s.pula, K.Pula) and isinstance(s.pula.liczba_stl, int) and s.pula.liczba_stl > 0 and s.pula.stan == "gotowa"
    assert isinstance(s.skaner, K.Skaner) and s.skaner.startow_skanu == 0
    assert not s.zamkniety
    with pytest.raises(dataclasses.FrozenInstanceError):
        s.operator = "ktos"  # stan jest zamrozony - okno go nie zmienia


def test_a_kolory_gniazd_rowne_wynikowi_analizy_po_decyzjach(st):
    """Kryterium (a): kolory rowne wynikowi analizy po zastosowaniu decyzji w 100 % gniazd."""
    from stanowisko import kontroler_api as K
    from stanowisko import statusy as ST

    skan_id = st.wrzuc("zwykla", numer=3)
    wynik = st.wynik(st.opis("zwykla", 3, None, None, None, 0))
    s = st.stan()
    p = s.plytka(skan_id)
    assert s.biezaca_plytka == skan_id and p.status == "przyjety" and p.aktywna and p.numer == 3 and p.uklad == "wieczorna" and p.typ == "wieczorna"
    oczekiwane = K.kolory_oczekiwane(wynik)
    assert kolory(p) == oczekiwane and len(oczekiwane) == 9
    assert len(p.gniazda) == 19 and [g.nr for g in p.gniazda] == sorted(g.nr for g in p.gniazda)  # caly uklad plytki, takze puste gniazda
    for g in p.gniazda:
        wpis = ST.STATUSY[g.status]
        assert g.rgb == wpis.hex and g.podpis == wpis.napis
        if g.nr in ZESTAW_ZWYKLY:
            assert g.praca is not None and g.kolor == oczekiwane[(g.nr, 1)] and g.praca.status_programu == oczekiwane[(g.nr, 1)]
        else:
            assert (g.status, g.kolor, g.prace) == ("pusty", None, ())
    statusy = {g.nr: g.status for g in p.gniazda if g.prace}
    assert statusy == {1: "zielony", 2: "czerwony", 3: "zolty", 4: "szary", 5: "pomaranczowy", 6: "nie_sprawdzono", 7: "blad_inspekcji", 8: "zielony",
                       9: "czerwony"}
    assert p.zielonych == 2 and s.liczniki == {"zielony": 2, "czerwony": 2, "zolty": 3, "szary": 1, "pomaranczowy": 1} and s.prac == 9
    assert [k.rodzaj for k in p.komunikaty] == ["blad_inspekcji"] and p.komunikaty[0].gniazda == (7,) and "7" in p.komunikaty[0].tekst

    assert st.k.wybierz_operatora("Technik A")
    assert st.k.ukruszona(p.gniazdo(2).praca.praca_id)  # program: czerwony
    assert st.k.ukruszona(p.gniazdo(1).praca.praca_id)  # program: zielony -> ukruszona niewykryta (SE9)
    assert st.k.ok(p.gniazdo(9).praca.praca_id)  # falszywy alarm
    assert st.k.ok(p.gniazdo(3).praca.praca_id)
    p = st.stan().plytka(skan_id)
    assert kolory(p) == K.kolory_oczekiwane(wynik, {(2, 1): "ukruszona", (1, 1): "ukruszona", (9, 1): "ok", (3, 1): "ok"})
    assert {g.nr: g.status for g in p.gniazda if g.nr in (1, 2, 3, 9)} == {1: "ukruszona", 2: "ukruszona", 3: "zatwierdzona_ok", 9: "zatwierdzona_ok"}
    assert (p.gniazdo(2).praca.decyzja, p.gniazdo(1).praca.decyzja, p.gniazdo(9).praca.decyzja) == ("ukruszona", "ukruszona_niewykryta", "ok")
    assert p.gniazdo(1).praca.status_programu == "zielony" and p.gniazdo(1).praca.operator == "Technik A"
    assert st.stan().liczniki == {"zielony": 1, "czerwony": 2, "zolty": 2, "szary": 1, "pomaranczowy": 1, "zatwierdzona_ok": 2}


def test_b_decyzja_zapisana_lista_odswiezona_a_bez_operatora_odmowa(st):
    """Kryterium (b): decyzja przez kontroler zapisuje sie w bazie i odswieza liste; bez operatora - odmowa z komunikatem."""
    skan_id = st.wrzuc("zwykla", numer=2)
    praca = st.stan().plytka(skan_id).gniazdo(2).praca
    assert praca.dozwolone == ("ukruszona", "ok")
    baza = st.k.sesja.baza
    przed = baza.wiersz("SELECT count(*) AS n FROM decyzje")["n"]

    odp = st.k.ukruszona(praca.praca_id)
    assert not odp and odp.kod == "brak_operatora" and "osob" in odp.tekst.lower()
    s = st.stan()
    assert [k.tekst for k in s.komunikaty if k.rodzaj == "brak_operatora"] == [odp.tekst]
    assert baza.wiersz("SELECT count(*) AS n FROM decyzje")["n"] == przed and s.do_dofrezowania == ()
    assert s.plytka(skan_id).gniazdo(2).praca.decyzja is None
    assert not st.k.ok(praca.praca_id) and not st.k.podaj_numer_plytki(skan_id, 4)
    assert not st.k.wybierz_operatora("Osoba Spoza Listy") and st.stan().operator is None

    assert st.k.wybierz_operatora("Technik B") and st.stan().operator == "Technik B" and not st.stan().wymaga_operatora
    assert not [k for k in st.stan().komunikaty if k.rodzaj in ("brak_operatora", "osoba_spoza_listy")]  # odmowy nieaktualne
    odp = st.k.ukruszona(praca.praca_id)
    assert odp and isinstance(odp.dane, int)
    wiersz = baza.wiersz("SELECT * FROM decyzje WHERE id = ?", (odp.dane,))
    assert (wiersz["praca_id"], wiersz["rodzaj"], wiersz["operator"]) == (praca.praca_id, "ukruszona", "Technik B")
    s = st.stan()
    assert len(s.do_dofrezowania) == 1 and len(s.do_dofrezowania_biezaca) == 1
    poz = s.do_dofrezowania[0]
    assert (poz.praca_id, poz.skan_id, poz.numer_plytki, poz.gniazdo, poz.operator, poz.zmiana, poz.doba) == (
        praca.praca_id, skan_id, 2, 2, "Technik B", 2, "2026-11-17")
    assert (poz.kuweta, poz.krazek, poz.ubytki) == ("9002", "K-1", 1) and poz.ubytek_max_mm == pytest.approx(0.62)
    praca = s.praca(praca.praca_id)
    assert praca.dozwolone == ("ok", "cofnij") and praca.na_liscie is not None and praca.na_liscie.ta_praca

    assert st.k.cofnij(praca.praca_id)
    s = st.stan()
    assert s.do_dofrezowania == () and s.praca(praca.praca_id).decyzja is None and s.praca(praca.praca_id).kolor == "czerwony"
    assert baza.wiersz("SELECT count(*) AS n FROM decyzje")["n"] == przed + 2  # decyzja i jej cofniecie: tylko dopisywanie
    odp = st.k.cofnij(praca.praca_id)  # nic do cofniecia: odmowa sesji jako odpowiedz, nie wyjatek
    assert not odp and odp.kod == "odmowa" and odp.tekst
    assert not st.k.ukruszona(999999)


def test_c_start_skanu_wola_akcje_dokladnie_raz(st):
    """Kryterium (c): akcja "start skanu" wola atrape dokladnie raz na polecenie."""
    assert st.starty_skanu() == 0
    assert st.k.start_skanu()
    assert st.starty_skanu() == 1
    s = st.stan()
    assert s.skaner.startow_skanu == 1 and s.skaner.ostatni_start_skanu and s.skaner.czeka_na_skan
    st.wrzuc("czysta", numer=5)
    assert st.starty_skanu() == 1 and not st.stan().skaner.czeka_na_skan  # nowy skan przyszedl: nie czekamy
    assert st.k.wykonaj("start_skanu") and st.starty_skanu() == 2


def test_d_plytka_niezgodna_z_ukladem(st):
    skan_id = st.wrzuc("niezgodny_uklad")
    s = st.stan()
    p = s.plytka(skan_id)
    assert p.status == "niezgodny_uklad" and not p.aktywna and p.prace == () and p.napis
    bez_zielonego(p)
    assert [k.rodzaj for k in s.komunikaty] == ["niezgodny_uklad"] and s.komunikaty[0].poziom == "blad" and s.komunikaty[0].skan_id == skan_id
    assert s.komunikaty[0].trwaly and s.liczniki == {} and s.pytania == ()
    assert st.k.zamknij_komunikat(s.komunikaty[0].id)
    assert st.stan().komunikaty == () and [k.rodzaj for k in st.stan().plytka(skan_id).komunikaty] == ["niezgodny_uklad"]  # przy plytce zostaje


def test_d_skan_do_powtorzenia(st):
    skan_id = st.wrzuc("do_powtorzenia", numer=4, poza=1)
    s = st.stan()
    p = s.plytka(skan_id)
    assert p.status == "do_powtorzenia" and p.aktywna
    bez_zielonego(p)
    assert {g.nr: g.status for g in p.gniazda if g.prace} == {1: "skan_do_powtorzenia", 2: "skan_ponownie", 3: "podwojny", 4: "czerwony"}
    assert len(p.gniazdo(3).prace) == 2 and len(p.poza_gniazdem) == 1 and p.poza_gniazdem[0].status == "poza_gniazdem"
    k = [k for k in s.komunikaty if k.rodzaj == "skan_do_powtorzenia"]
    assert len(k) == 1 and k[0].skan_id == skan_id and set(k[0].gniazda) == {2, 3} and "ponownie" in k[0].tekst
    assert st.k.wybierz_operatora("Technik A")
    praca = p.gniazdo(4).praca
    assert praca.dozwolone == ()
    odp = st.k.ukruszona(praca.praca_id)  # skan do powtorzenia nie przyjmuje decyzji
    assert not odp and odp.kod == "odmowa" and st.stan().do_dofrezowania == ()


def test_d_plytka_nie_z_trybu_blokada_i_swiadome_dopuszczenie(st):
    skan_id = st.wrzuc("nie_z_trybu", numer=2)
    s = st.stan()
    p = s.plytka(skan_id)
    assert p.status == "plytka_nie_z_trybu" and not p.aktywna and p.typ == "poranna" and "dopusc_plytke" in p.dozwolone
    bez_zielonego(p)
    assert {x.status for x in p.prace} == {"plytka_nie_z_trybu"} and {x.kolor for x in p.prace} == {None} and s.liczniki == {}
    assert [q.rodzaj for q in s.pytania] == ["plytka_nie_z_trybu"]
    q = s.pytania[0]
    assert q.skan_id == skan_id and "poranna" in q.tekst and [o.polecenie for o in q.odpowiedzi] == ["zamknij_pytanie", "dopusc_plytke"]
    assert not st.k.dopusc_plytke(skan_id)  # bez operatora nie ma dopuszczenia
    assert st.k.wybierz_operatora("Technik A")
    assert not st.k.ukruszona(p.gniazdo(3).praca.praca_id) and st.stan().do_dofrezowania == ()  # zablokowana: bez decyzji

    assert st.k.wykonaj(q.odpowiedzi[0].polecenie, *q.odpowiedzi[0].argumenty)  # "zeskanuje wlasciwa plytke": pytanie znika, blokada zostaje
    s = st.stan()
    assert s.pytania == () and s.plytka(skan_id).status == "plytka_nie_z_trybu" and len(s.plytka(skan_id).pytania) == 1

    assert st.k.wykonaj(q.odpowiedzi[1].polecenie, *q.odpowiedzi[1].argumenty)  # swiadome dopuszczenie
    p = st.stan().plytka(skan_id)
    assert p.status == "przyjety" and p.aktywna and p.dopuszczona and p.zielonych == 2 and "cofnij_dopuszczenie" in p.dozwolone
    assert st.k.sesja.baza.wiersz("SELECT operator FROM decyzje WHERE skan_id = ? AND rodzaj = 'uklad'", (skan_id,))["operator"] == "Technik A"
    assert st.k.cofnij_dopuszczenie(skan_id)
    bez_zielonego(st.stan().plytka(skan_id))


def test_d_brak_numeru_plytki(st):
    skan_id = st.wrzuc("bez_numeru")
    s = st.stan()
    p = s.plytka(skan_id)
    assert p.status == "przyjety" and p.numer is None
    bez_zielonego(p)
    assert {g.nr: (g.status, g.kolor) for g in p.gniazda if g.prace} == {1: ("czeka_na_numer", None), 2: ("czerwony", "czerwony"), 3: ("czeka_na_numer", None)}
    assert s.liczniki == {"czerwony": 1}
    assert [q.rodzaj for q in s.pytania] == ["brak_numeru_plytki"]
    q = s.pytania[0]
    assert q.numery and all(isinstance(n, int) for n in q.numery) and [o.argumenty for o in q.odpowiedzi[:-1]] == [(skan_id, n) for n in q.numery]
    assert st.k.wybierz_operatora("Technik A")
    assert not st.k.podaj_numer_plytki(skan_id, 0)
    assert st.k.wykonaj("podaj_numer_plytki", skan_id, q.numery[1])
    s = st.stan()
    p = s.plytka(skan_id)
    assert p.numer == q.numery[1] and p.numer_zrodlo == "podany" and p.zielonych == 2 and s.pytania == ()
    assert {g.nr: g.status for g in p.gniazda if g.prace} == {1: "zielony", 2: "czerwony", 3: "zielony"}


def test_d_blad_analizy(st):
    skan_id = st.wrzuc("blad")
    s = st.stan()
    p = s.plytka(skan_id)
    assert p.status == "blad" and not p.aktywna and p.prace == ()
    bez_zielonego(p)
    k = [k for k in s.komunikaty if k.rodzaj == "blad_analizy"]
    assert len(k) == 1 and k[0].skan_id == skan_id and k[0].poziom == "blad"
    assert FOLDER_ZLECENIA not in json.dumps(dataclasses.asdict(s), ensure_ascii=False, default=str)


def test_h_ponowny_skan_pytanie_potwierdzenie_cofniecie_odrzucenie(st):
    """Kryterium (h): ta sama plytka do 60 min = pytanie z liczba decyzji do utraty; potwierdzenie i cofniecie dzialaja."""
    assert st.k.wybierz_operatora("Technik A")
    pierwszy = st.wrzuc("zwykla", numer=1)
    p = st.stan().plytka(pierwszy)
    assert st.k.ukruszona(p.gniazdo(2).praca.praca_id) and st.k.ok(p.gniazdo(9).praca.praca_id) and st.k.ok(p.gniazdo(3).praca.praca_id)
    assert st.stan().pytania == () and len(st.stan().do_dofrezowania) == 1

    st.przesun(10)
    drugi = st.wrzuc("zwykla", numer=1)
    s = st.stan()
    assert [q.rodzaj for q in s.pytania] == ["ponowny_skan"]
    q = s.pytania[0]
    assert (q.skan_id, q.poprzedni_id, q.numer_plytki, q.liczba_decyzji, q.liczba_ukruszonych) == (drugi, pierwszy, 1, 3, 1)
    assert "3 decyzje" in q.tekst and "10 min" in q.tekst and [o.polecenie for o in q.odpowiedzi] == ["potwierdz_ponowny_skan", "odrzuc_ponowny_skan"]
    assert s.plytka(drugi).moze_zastapic == pierwszy and s.plytka(pierwszy).aktywna  # samo pytanie niczego nie zastepuje
    assert len(s.do_dofrezowania) == 1

    assert st.k.wykonaj(q.odpowiedzi[0].polecenie, *q.odpowiedzi[0].argumenty)  # potwierdzenie
    s = st.stan()
    assert s.plytka(pierwszy).status == "zastapiony" and not s.plytka(pierwszy).aktywna and s.plytka(drugi).zastepuje_id == pierwszy
    assert s.do_dofrezowania == () and s.pytania == () and "cofnij_zastapienie" in s.plytka(drugi).dozwolone
    assert {x.status for x in s.plytka(pierwszy).prace} == {"nieaktywny"}

    assert st.k.cofnij_zastapienie(drugi)  # pomylka: poprzedni skan wraca z decyzjami
    s = st.stan()
    assert s.plytka(pierwszy).status == "przyjety" and len(s.do_dofrezowania) == 1 and s.plytka(pierwszy).gniazdo(9).status == "zatwierdzona_ok"
    assert s.pytania == ()  # program nie proponuje ponownie tego samego zastapienia

    st.przesun(10)
    trzeci = st.wrzuc("zwykla", numer=1)
    q = st.stan().pytania[0]
    assert (q.skan_id, q.poprzedni_id, q.liczba_decyzji) == (trzeci, drugi, 0) and "nie ma" in q.tekst
    assert st.k.odrzuc_ponowny_skan(trzeci)  # "to nowy wsad": pytanie znika, oba skany zostaja
    s = st.stan()
    assert s.pytania == () and s.plytka(drugi).aktywna and s.plytka(trzeci).aktywna
    assert not st.k.odrzuc_ponowny_skan(pierwszy)

    st.przesun(61)  # po godzinie ta sama plytka to nowy wsad - bez pytania
    czwarty = st.wrzuc("zwykla", numer=1)
    assert st.stan().pytania == () and st.stan().plytka(czwarty).moze_zastapic is None


def test_e3a1p_nowy_wsad_bez_pytania_i_konfliktu_ponowny_skan_z_pytaniem(st):
    """E3-A1p: plytki krazace (3 numery) z nowym wsadem co 7-15 min - zadnego pytania o ponowny skan, zadnego konfliktu
    projektu i zadnych przyciskow potwierdzenia (regula sprzed E3-A1p pytala tu 3 razy); prawdziwy ponowny skan (te same
    prace w innych gniazdach) - pytanie jak dawniej, po potwierdzeniu bez konfliktow."""
    assert st.k.wybierz_operatora("Technik A")
    skany = []
    for i in range(6):
        if i:
            st.przesun(5 + 2 * i)
        skany.append(st.wrzuc("czysta", numer=i % 3 + 1, gniazda={g: "zielony" for g in range(1, 7)},
                              projekty={g: 100 * (i + 1) + g for g in range(1, 7)}))
    s = st.stan()
    assert len(s.plytki) == 6 and s.pytania == () and s.konflikty == ()
    assert [k.rodzaj for k in s.komunikaty if k.rodzaj == "konflikt_projektu"] == []
    assert all(p.moze_zastapic is None and "potwierdz_ponowny_skan" not in p.dozwolone for p in s.plytki)
    st.przesun(4)  # ponowny skan ostatniej plytki (nr 3): te same prace przesuniete o jedno gniazdo
    ponowny = st.wrzuc("czysta", numer=3, gniazda={g: "zielony" for g in range(2, 8)}, projekty={g + 1: 600 + g for g in range(1, 7)})
    s = st.stan()
    assert [(q.rodzaj, q.skan_id, q.poprzedni_id) for q in s.pytania] == [("ponowny_skan", ponowny, skany[5])]
    assert s.plytka(ponowny).moze_zastapic == skany[5] and len(s.konflikty) == 6  # do potwierdzenia: te same projekty na dwoch skanach
    assert [k.rodzaj for k in s.komunikaty if k.rodzaj == "konflikt_projektu"] == []  # runda 2: nie na pasku bledow, dopoki czeka
    assert st.k.potwierdz_ponowny_skan(ponowny)
    s = st.stan()
    assert s.pytania == () and s.konflikty == () and s.plytka(skany[5]).status == "zastapiony"


def test_e3a1p_konflikt_ze_skanem_do_zastapienia_nie_na_pasku_bledow_dopoki_czeka(st):
    """E3-A1p runda 2 (decyzja wlasciciela 18.11.2026): gdy skan czeka na odpowiedz "to ponowny skan?", konflikty projektu
    miedzy nim a skanem, ktory proponuje zastapic, nie trafiaja na pasek bledow (takze po "Pozniej"); konflikt z innym skanem
    zostaje. Po "Nie, to nowy wsad" konflikty pojawiaja sie normalnie, po "Tak" znikaja (poprzedni skan zastapiony).
    ``stan.konflikty`` podaje wszystkie konflikty jak dotad."""
    from stanowisko import kontroler_api as K

    def komunikaty_konfliktu() -> list:
        return sorted(k.id for k in st.stan().komunikaty if k.rodzaj == "konflikt_projektu")

    assert st.k.wybierz_operatora("Technik A")
    zielone = {g: "zielony" for g in range(1, 10)}
    st.wrzuc("czysta", numer=2, gniazda={g: "zielony" for g in (1, 2, 3, 9)}, projekty={1: 201, 2: 202, 3: 203, 9: 700})
    st.przesun(7)
    poprzedni = st.wrzuc("czysta", numer=3, gniazda={g: "zielony" for g in range(1, 7)}, projekty={g: 300 + g for g in range(1, 7)})
    st.przesun(5)  # ponowny skan plytki 3: te same prace przesuniete o gniazdo + praca 700 lezaca tez na plytce 2
    ponowny = st.wrzuc("czysta", numer=3, gniazda={g: zielone[g] for g in range(2, 10)},
                       projekty={**{g + 1: 300 + g for g in range(1, 7)}, 8: 801, 9: 700})
    s = st.stan()
    q = s.pytania[0]
    assert [(p.rodzaj, p.skan_id, p.poprzedni_id) for p in s.pytania] == [("ponowny_skan", ponowny, poprzedni)]
    assert len(s.konflikty) == 7  # stan podaje wszystkie: 6 z poprzednim skanem plytki 3, 1 z plytka 2
    z_plytka_2 = f"konflikt_projektu:{K.projekt_sztuczny(700)}"
    assert komunikaty_konfliktu() == [z_plytka_2]
    assert st.k.zamknij_pytanie(q.id) and st.stan().pytania == ()  # "Pozniej" to nie odpowiedz: konflikty dalej poza paskiem
    assert komunikaty_konfliktu() == [z_plytka_2]
    assert st.k.odrzuc_ponowny_skan(ponowny)  # "Nie, to nowy wsad": konflikty z poprzednim skanem wracaja na pasek
    assert komunikaty_konfliktu() == sorted([z_plytka_2] + [f"konflikt_projektu:{K.projekt_sztuczny(300 + g)}" for g in range(1, 7)])
    assert st.k.potwierdz_ponowny_skan(ponowny)  # zmiana zdania "Tak": poprzedni skan zastapiony - jego konflikty znikaja
    s = st.stan()
    assert s.plytka(poprzedni).status == "zastapiony" and komunikaty_konfliktu() == [z_plytka_2] and len(s.konflikty) == 1


def test_zab_juz_na_liscie(st):
    assert st.k.wybierz_operatora("Technik A")
    pierwszy = st.wrzuc("zwykla", numer=1)
    assert st.k.ukruszona(st.stan().plytka(pierwszy).gniazdo(2).praca.praca_id)
    st.przesun(90)
    drugi = st.wrzuc("czysta", numer=1, gniazda={5: "czerwony", 6: "zielony"}, projekty={5: 2, 6: 16})  # ten sam projekt 2 w nowym wsadzie
    praca = st.stan().plytka(drugi).gniazdo(5).praca
    assert praca.na_liscie is not None and not praca.na_liscie.ta_praca and praca.na_liscie.skan_id == pierwszy
    assert "dofrezowania" in praca.na_liscie.tekst and st.stan().plytka(drugi).gniazdo(6).praca.na_liscie is None
    assert st.k.ukruszona(praca.praca_id)
    s = st.stan()
    assert len(s.do_dofrezowania_biezaca) == 1 and s.do_dofrezowania_biezaca[0].praca_id == praca.praca_id and s.do_dofrezowania_biezaca[0].powtorzenia == 1
    assert s.praca(praca.praca_id).na_liscie.ta_praca


def test_szczegoly_pracy(st):
    from stanowisko import kontroler_api as K

    skan_id = st.wrzuc("zwykla", numer=1)
    p = st.stan().plytka(skan_id)
    sz = st.k.szczegoly_pracy(p.gniazdo(2).praca.praca_id)
    assert isinstance(sz, K.SzczegolyPracy) and sz.praca.praca_id == p.gniazdo(2).praca.praca_id
    assert len(sz.ubytki) == 1 and sz.ubytki[0]["srednica_mm"] == pytest.approx(0.62) and sz.ubytki[0]["na_krawedzi"] is True
    assert sz.kandydaci and sz.kandydaci[0]["sha16"] == K.projekt_sztuczny(2) == sz.praca.sha16
    assert sz.plik_podgladu is None or Path(sz.plik_podgladu).is_file()
    blad = st.k.szczegoly_pracy(p.gniazdo(7).praca.praca_id)
    assert blad.praca.blad_inspekcji and blad.praca.status == "blad_inspekcji" and blad.uwagi
    assert st.k.szczegoly_pracy(999999) is None


def test_sygnaly_po_kazdej_zmianie(st):
    from stanowisko import kontroler_api as K

    st.sygnaly.clear()
    odp = st.k.ukruszona(1)
    assert not odp
    typy = [z.typ for z in st.sygnaly]
    assert "stan" in typy and "komunikat" in typy and all(t in K.SYGNALY for t in typy)
    assert [z.komunikat.rodzaj for z in st.sygnaly if z.typ == "komunikat"] == ["brak_operatora"]
    assert st.sygnaly[-1].stan is st.stan() or st.sygnaly[-1].stan == st.stan()
    st.sygnaly.clear()
    skan_id = st.wrzuc("bez_numeru")
    assert [z.pytanie.rodzaj for z in st.sygnaly if z.typ == "pytanie"] == ["brak_numeru_plytki"]
    wersje = [z.stan.wersja for z in st.sygnaly if z.typ == "stan"]
    assert wersje == sorted(wersje) and wersje and st.stan().wersja >= wersje[-1]
    st.sygnaly.clear()
    assert st.k.wybierz_operatora("Technik A") and st.k.podaj_numer_plytki(skan_id, 2)
    assert [z.typ for z in st.sygnaly].count("stan") >= 2 and not [z for z in st.sygnaly if z.typ == "pytanie"]
    st.k.odsubskrybuj(st.odbierz)
    st.sygnaly.clear()
    st.k.zamknij_pytanie("nic")
    assert st.sygnaly == []


def test_operator_wybierany_na_zmiane(st):
    assert st.k.wybierz_operatora("Technik A")
    skan_id = st.wrzuc("zwykla", numer=1)
    st.przesun(170)  # 21:50 - nadal zmiana 2
    st.k.przetworz()
    assert st.stan().operator == "Technik A" and st.stan().zmiana == 2
    st.przesun(20)  # 22:10 - zmiana 3: wybor osoby wygasa
    st.k.przetworz()
    s = st.stan()
    assert s.zmiana == 3 and s.doba == "2026-11-17" and s.operator is None and s.wymaga_operatora
    nowa = [k for k in s.komunikaty if k.rodzaj == "nowa_zmiana"]
    assert len(nowa) == 1 and "3" in nowa[0].tekst
    praca = s.plytka(skan_id).gniazdo(2).praca
    assert not st.k.ukruszona(praca.praca_id)
    assert st.k.wybierz_operatora("Technik B") and st.k.ukruszona(praca.praca_id)
    assert not [k for k in st.stan().komunikaty if k.rodzaj == "nowa_zmiana"]
    assert st.stan().do_dofrezowania[0].operator == "Technik B" and st.stan().do_dofrezowania[0].zmiana == 2  # zmiana z chwili przyjecia skanu
    st.przesun(8 * 60)  # 06:10 nastepnego dnia: nowa doba robocza - plytki poprzedniej znikaja z mapy, lista biezaca zostaje
    st.k.przetworz()
    s = st.stan()
    assert (s.doba, s.zmiana) == ("2026-11-18", 1) and s.plytki == () and s.do_dofrezowania == () and len(s.do_dofrezowania_biezaca) == 1


def test_g_pula_liczba_stl_i_odswiez(st):
    """Kryterium (g): liczba STL w puli i "odswiez pule" w stanie."""
    s = st.stan()
    assert s.pula.liczba_stl > 0 and str(s.pula.liczba_stl) in s.pula.napis and s.pula.odswiezono
    odp = st.k.odswiez_pule()
    assert odp and odp.dane == "liczenie" and st.stan().pula.stan == "liczenie"  # P6: atrapa tez liczy "w tle" (wynik w przetworz)
    st.czekaj(lambda: st.stan().pula.stan == "gotowa", 30.0, "pula po odswiezeniu")
    assert st.stan().pula.stan == "gotowa" and st.stan().pula.liczba_stl == s.pula.liczba_stl


# ----------------------------------------------------------------------------
# runda 2 recenzji PR #20: zmiany kontraktu (P4, P6, P7, P1 / P8, D1, D2, D6, D7, D12)
# ----------------------------------------------------------------------------
def test_p4_zielony_tylko_przy_inspekcji_ok_i_znanym_dopasowaniu(st):
    """P4: kolor gniazda "zielony" z analizy bez inspekcji "ok" (brak inspekcji, pominieta, nowy status inspect) albo przy
    nieznanym statusie dopasowania - praca NIE jest zielona: status nie_sprawdzono / nieznany, kolor zolty, poza "zielonych"."""
    from stanowisko import kontroler_api as K
    from stanowisko import statusy as ST

    gniazda = {1: "zielony", 2: "zielony_bez_inspekcji", 3: "zielony_pominieto", 4: "zielony_nowa_inspekcja", 5: "zielony_nowe_dopasowanie"}
    skan_id = st.wrzuc("czysta", numer=2, gniazda=gniazda)
    p = st.stan().plytka(skan_id)
    assert {g.nr: g.status for g in p.gniazda if g.prace} == {1: "zielony", 2: "nie_sprawdzono", 3: "nie_sprawdzono", 4: "nieznany", 5: "nieznany"}
    assert {g.nr: g.kolor for g in p.gniazda if g.prace} == {1: "zielony", 2: "zolty", 3: "zolty", 4: "zolty", 5: "zolty"}
    assert all(g.rgb != ST.STATUSY["zielony"].hex for g in p.gniazda if g.nr != 1)
    assert kolory(p) == K.kolory_oczekiwane(st.wynik(st.opis("czysta", 2, gniazda, None, None, 0)))
    assert p.zielonych == 1 and p.liczniki == {"zielony": 1, "zolty": 4} and st.stan().liczniki == {"zielony": 1, "zolty": 4}
    assert all(x.dozwolone == ("ukruszona", "ok") for x in p.prace)  # praca do sprawdzenia: technik decyduje


def test_p4_tabela_zadna_para_poza_zielony_ok_nie_jest_zielona():
    """P4 (test tabelaryczny): kazda para (kolor, status inspekcji, status dopasowania) spoza "zielony + ok + znane dopasowanie"
    daje status spoza ``STATUSY_ZIELONE`` i klase koloru inna niz zielona; nieznane wartosci nigdy nie rzucaja wyjatku."""
    from stanowisko import porownaj as PO
    from stanowisko import statusy as ST

    kolory_ = list(ST.KOLORY_PRACY) + [None, "fioletowy", ""]
    inspekcje = list(PO.INSPECT_NA_STATUS) + [None, "nowy_status_inspect", ""]
    dopasowania = ["zielony", "zolty", "szary", None, "nowy_status_match", ""]
    zielonych = 0
    for kolor in kolory_:
        for insp in inspekcje:
            for match in dopasowania:
                for status_skanu in ("przyjety", "do_powtorzenia", "zastapiony", "blad", "plytka_nie_z_trybu", "nowy_status_skanu"):
                    klucz = ST.status_pracy(kolor, status_skanu=status_skanu, status_gniazda=kolor, status_inspekcji=insp, status_match=match)
                    assert klucz in ST.STATUSY, (kolor, insp, match, klucz)
                    wolno = kolor == "zielony" and insp == "ok" and match in ("zielony", "zolty", None) and status_skanu not in ("plytka_nie_z_trybu",)
                    if klucz in ST.STATUSY_ZIELONE:
                        zielonych += 1
                        assert wolno, (kolor, insp, match, status_skanu)
                    assert (ST.kolor_pracy(kolor, klucz) == "zielony") == (klucz in ST.STATUSY_ZIELONE), (kolor, insp, match, klucz)
    assert zielonych > 0
    assert ST.status_pracy(None, status_skanu="przyjety") == "nieznany" and ST.kolor_pracy(None, "nieznany") == "zolty"  # D3
    assert ST.kolor_pracy("fioletowy", "nieznany") == "zolty" and ST.kolor_pracy("zielony", "czeka_na_numer") is None


def _sekwencja_zgodnosci(st) -> list:
    """P6: ta sama sekwencja polecen dla atrapy i prawdziwego kontrolera; zwraca (polecenie, ok, kod, dane / stan)."""
    k, wynik = st.k, []

    def zapisz(opis: str, odp, *dodatki) -> None:
        wynik.append((opis, odp.ok, odp.kod) + dodatki)

    zapisz("ustaw_pule zly wspolczynnik", k.ustaw_pule(st.folder_puli, 7.5), st.stan().pula.stan)
    zapisz("ustaw_pule wspolczynnik tekst", k.ustaw_pule(st.folder_puli, "abc"))
    zapisz("ustaw_pule wspolczynnik nan", k.ustaw_pule(st.folder_puli, float("nan")))
    zapisz("ustaw_pule wspolczynnik bool", k.ustaw_pule(st.folder_puli, True))
    zapisz("ustaw_pule folder liczba", k.ustaw_pule(123))
    odp = k.ustaw_pule(None)
    zapisz("ustaw_pule None", odp, odp.dane, st.stan().pula.stan, st.stan().pula.folder)
    odp = k.odswiez_pule()
    zapisz("odswiez_pule bez folderu", odp, odp.dane, st.stan().pula.stan)
    odp = k.ustaw_pule(st.folder_puli, "1,22")
    zapisz("ustaw_pule", odp, odp.dane, st.stan().pula.stan)
    st.czekaj(lambda: st.stan().pula.stan != "liczenie", 30.0, "pula policzona")
    zapisz("pula po liczeniu", odp, st.stan().pula.stan, st.stan().pula.wspolczynnik)
    odp = k.odswiez_pule()
    zapisz("odswiez_pule", odp, odp.dane, st.stan().pula.stan)
    st.czekaj(lambda: st.stan().pula.stan != "liczenie", 30.0, "pula policzona")
    for opis, odp in (("wykonaj bez argumentu", k.wykonaj("ukruszona")), ("wykonaj za duzo argumentow", k.wykonaj("ukruszona", 1, 2)),
                      ("wykonaj numer bez numeru", k.wykonaj("podaj_numer_plytki", 1)), ("wykonaj nie napis", k.wykonaj(5)),
                      ("wykonaj nieznane", k.wykonaj("usun_wszystko")), ("ok lista", k.ok([1])), ("ukruszona bool", k.ukruszona(True)),
                      ("numer za duzy", k.podaj_numer_plytki(1, 10 ** 30)), ("zamknij_pytanie liczba", k.zamknij_pytanie(5)),
                      ("zamknij_komunikat None", k.zamknij_komunikat(None)), ("zapisz_liste zla doba", k.zapisz_liste(5)),
                      ("ukruszona bez osoby", k.ukruszona(1)), ("osoba liczba", k.wybierz_operatora(123)),
                      ("osoba spoza listy", k.wybierz_operatora("Nikt Taki"))):
        zapisz(opis, odp)
    zapisz("osoba", k.wybierz_operatora("Technik A"), st.stan().operator)
    zapisz("ukruszona nieznanej pracy", k.ukruszona(999999))
    zapisz("wyloguj", k.wybierz_operatora(None), st.stan().operator, st.stan().wymaga_operatora)
    zapisz("ukruszona po wylogowaniu", k.ukruszona(999999))
    odp = k.zapisz_liste()
    zapisz("zapisz_liste", odp, odp.dane)
    odp = k.zapisz_liste("2026-11-17")
    zapisz("zapisz_liste doby", odp, odp.dane)
    odp = k.ponow_zapis()
    zapisz("ponow_zapis", odp, odp.dane)
    zapisz("start_skanu", k.start_skanu(), st.stan().skaner.czeka_na_skan)
    st.start_nieudany()
    zapisz("start_skanu nieudany", k.start_skanu(), st.stan().skaner.czeka_na_skan, [x.rodzaj for x in st.stan().komunikaty if x.rodzaj == "start_skanu_nieudany"])
    zapisz("zamknij", k.zamknij())
    for opis, odp in (("po zamknieciu ustaw_pule", k.ustaw_pule(st.folder_puli)), ("po zamknieciu odswiez_pule", k.odswiez_pule()),
                      ("po zamknieciu zapisz_liste", k.zapisz_liste()), ("po zamknieciu ponow_zapis", k.ponow_zapis()),
                      ("po zamknieciu wyloguj", k.wybierz_operatora(None)), ("po zamknieciu zamknij_pytanie", k.zamknij_pytanie("x"))):
        zapisz(opis, odp)
    return wynik


def test_p6_atrapa_i_prawdziwy_kontroler_daja_te_same_odpowiedzi(tmp_path):
    """P6: ta sama sekwencja polecen (pula, zle argumenty, osoba, lista, zapis, start skanu, zamkniecie) na atrapie i na
    prawdziwym kontrolerze daje te same odpowiedzi (ok, kod, dane) i te same stany puli."""
    if not _jest_aplikacja():
        pytest.skip("brak modulu stanowisko.aplikacja")
    atrapa = StanowiskoAtrapy(tmp_path / "a")
    try:
        z_atrapy = _sekwencja_zgodnosci(atrapa)
    finally:
        atrapa.koniec()
    aplikacja = StanowiskoAplikacji(tmp_path / "b")
    try:
        z_aplikacji = _sekwencja_zgodnosci(aplikacja)
    finally:
        aplikacja.koniec()
    assert [w[:3] for w in z_atrapy] == [w[:3] for w in z_aplikacji]
    assert z_atrapy == z_aplikacji
    oczekiwane = {"ustaw_pule zly wspolczynnik": (False, "zly_wspolczynnik", "gotowa"), "ustaw_pule wspolczynnik tekst": (False, "zly_wspolczynnik"),
                  "ustaw_pule wspolczynnik nan": (False, "zly_wspolczynnik"), "ustaw_pule wspolczynnik bool": (False, "zly_wspolczynnik"),
                  "ustaw_pule folder liczba": (False, "zle_argumenty"), "ustaw_pule None": (True, "", "nieustawiona", "nieustawiona", None),
                  "odswiez_pule bez folderu": (True, "", "nieustawiona", "nieustawiona"), "ustaw_pule": (True, "", "liczenie", "liczenie"),
                  "pula po liczeniu": (True, "", "gotowa", 1.22), "odswiez_pule": (True, "", "liczenie", "liczenie"),
                  "wykonaj bez argumentu": (False, "zle_argumenty"), "wykonaj za duzo argumentow": (False, "zle_argumenty"),
                  "wykonaj numer bez numeru": (False, "zle_argumenty"), "wykonaj nie napis": (False, "odmowa"), "wykonaj nieznane": (False, "odmowa"),
                  "ok lista": (False, "zle_argumenty"), "ukruszona bool": (False, "zle_argumenty"), "numer za duzy": (False, "zle_argumenty"),
                  "zamknij_pytanie liczba": (False, "zle_argumenty"), "zamknij_komunikat None": (False, "zle_argumenty"),
                  "zapisz_liste zla doba": (False, "zle_argumenty"), "ukruszona bez osoby": (False, "brak_operatora"),
                  "osoba liczba": (False, "zle_argumenty"), "osoba spoza listy": (False, "osoba_spoza_listy"), "osoba": (True, "", "Technik A"),
                  "ukruszona nieznanej pracy": (False, "odmowa"), "wyloguj": (True, "wylogowano", None, True),
                  "ukruszona po wylogowaniu": (False, "brak_operatora"), "zapisz_liste": (True, "", "do_dofrezowania_biezaca.csv"),
                  "zapisz_liste doby": (True, "", "do_dofrezowania_2026-11-17.csv"), "ponow_zapis": (True, "", 0), "start_skanu": (True, "", True),
                  "start_skanu nieudany": (False, "start_skanu_nieudany", False, ["start_skanu_nieudany"]), "zamknij": (True, "")}
    for w in z_atrapy:
        if w[0] in oczekiwane:
            assert w[1:] == oczekiwane[w[0]], w
        else:
            assert w[0].startswith("po zamknieciu") and w[1:] == (False, "program_zamkniety"), w


def test_p6_atrapa_pokazuje_stany_zywe_prawdziwego_kontrolera(tmp_path):
    """P6: atrapa umie pokazac oknu stany, ktore ma prawdziwy kontroler: pula nieustawiona / liczenie / pusta / brak folderu /
    gotowa, skany wstrzymane (z komunikatem), silnik bez startu, skaner niedostepny i plik zajety, nieudany start skanu;
    liczba_stl=0 startuje jako pula pusta (nie "gotowa, 0 STL")."""
    from stanowisko import kontroler_api as K

    a = K.AtrapaKontrolera(tmp_path / "atrapa", liczba_stl=0)
    try:
        assert a.stan().pula.stan == "pusta" and a.stan().pula.liczba_stl == 0
        a.symuluj_pule("gotowa", 12)
        assert (a.stan().pula.stan, a.stan().pula.liczba_stl, a.stan().pula.napis) == ("gotowa", 12, "plik\u00f3w projekt\u00f3w: 12")  # napis statusy.STANY_PULI (E3-A3b runda 2)
        a.symuluj_pule("pusta")
        a.symuluj_kolejke(wstrzymane=2)
        s = a.stan()
        assert s.kolejka.wstrzymane == 2 and s.kolejka.razem == 2 and [k.rodzaj for k in s.komunikaty if k.id == "pula"] == ["pula_pusta"]
        assert "2" in [k.tekst for k in s.komunikaty if k.id == "pula"][0]
        a.symuluj_pule("brak_folderu")
        assert a.stan().pula.stan == "brak_folderu" and [k.rodzaj for k in a.stan().komunikaty if k.id == "pula"] == ["pula_brak_folderu"]
        a.symuluj_pule("liczenie")
        assert a.stan().pula.stan == "liczenie" and a.stan().pula.napis
        a.przetworz()
        assert a.stan().pula.stan == "liczenie"  # bez "Odswiez pule" liczenie trwa
        a.symuluj_pule("gotowa", 5)  # pula wrocila: skany wstrzymane ida do analizy, komunikat znika
        s = a.stan()
        assert s.kolejka.wstrzymane == 0 and s.kolejka.czeka == 2 and not [k for k in s.komunikaty if k.id == "pula"]
        a.symuluj_pule("nieustawiona")
        assert a.stan().pula.stan == "nieustawiona" and a.stan().pula.folder is None
        assert a.ustaw_pule("(inny folder)") and a.stan().pula.stan == "liczenie"
        a.przetworz()
        assert a.stan().pula.stan == "gotowa" and a.stan().pula.liczba_stl == 5 and a.stan().pula.folder == "(inny folder)"
        a.symuluj_kolejke(wstrzymane=1, silnik_gotowy=False)
        assert not a.stan().kolejka.silnik_gotowy and [k.rodzaj for k in a.stan().komunikaty if k.id == "silnik"] == ["silnik_nie_startuje"]
        a.symuluj_kolejke()
        assert a.stan().kolejka.razem == 0 and not [k for k in a.stan().komunikaty if k.id == "silnik"]
        a.symuluj_skaner(dostepny=False, zajete=1)
        s = a.stan()
        assert not s.skaner.dostepny and s.skaner.zajete == 1
        assert sorted(k.rodzaj for k in s.komunikaty) == ["folder_skanera_niedostepny", "plik_zajety"]
        a.symuluj_skaner()
        assert a.stan().skaner.dostepny and a.stan().komunikaty == ()
        a.symuluj_skaner(start_udany=False)
        odp = a.start_skanu()
        assert not odp and odp.kod == "start_skanu_nieudany" and len(a.starty_skanu) == 1 and not a.stan().skaner.czeka_na_skan
        a.symuluj_skaner()
        assert a.start_skanu() and a.stan().skaner.czeka_na_skan and not [k for k in a.stan().komunikaty if k.rodzaj == "start_skanu_nieudany"]
        with pytest.raises(ValueError):
            a.symuluj_pule("nie_ma_takiego")
    finally:
        a.zamknij()


def test_p1_p8_atrapa_pozycje_nie_zapisano_i_komunikat_trwaly(tmp_path):
    """P1 / P8 (kontrakt): skan policzony, ale niezapisany - pozycja ``stan.niezapisane`` z napisem, komunikat TRWALY o stalym id
    ``blad_zapisu`` (zostaje do udanego zapisu albo zamkniecia przez technika; zamkniety wraca tylko z nowa pozycja),
    ``baza_zajeta`` znika sam po zapisie; ``ponow_zapis`` - proba na zadanie."""
    from stanowisko import kontroler_api as K
    from stanowisko import statusy as ST

    a = K.AtrapaKontrolera(tmp_path / "atrapa")
    try:
        a.symuluj_blad_zapisu(2)
        s = a.stan()
        assert len(s.niezapisane) == 2 and all(isinstance(n, K.Niezapisany) for n in s.niezapisane)
        assert {(n.przyczyna, n.rodzaj, n.napis) for n in s.niezapisane} == {("blad_zapisu", "wynik", ST.NAPISY_NIEZAPISANE["blad_zapisu"])}
        assert s.kolejka.niezapisane == 2 and s.kolejka.wstrzymane == 2 and s.plytki == ()
        k = [x for x in s.komunikaty if x.id == K.ID_BLAD_ZAPISU]
        assert len(k) == 1 and k[0].rodzaj == "blad_zapisu" and k[0].trwaly and k[0].poziom == "blad" and "2" in k[0].tekst
        odp = a.ponow_zapis()  # przyczyna trwa: odmowa z kodem przyczyny, pozycje zostaja
        assert not odp and odp.kod == "blad_zapisu" and odp.dane == 2 and len(a.stan().niezapisane) == 2
        assert a.zamknij_komunikat(K.ID_BLAD_ZAPISU) and not [x for x in a.stan().komunikaty if x.id == K.ID_BLAD_ZAPISU]
        a.ponow_zapis()
        assert not [x for x in a.stan().komunikaty if x.id == K.ID_BLAD_ZAPISU]  # zamkniety nie wraca przy kolejnej probie
        a.symuluj_blad_zapisu(1)
        assert [x.tekst for x in a.stan().komunikaty if x.id == K.ID_BLAD_ZAPISU] and len(a.stan().niezapisane) == 3  # nowa pozycja: wraca
        a.symuluj_blad_zapisu(1, przyczyna="baza_zajeta")
        assert sorted(x.rodzaj for x in a.stan().komunikaty) == ["baza_zajeta", "blad_zapisu"]
        a.symuluj_blad_zapisu(0)  # przyczyna ustapila: przetworz zapisuje (jak samoczynne ponowienie)
        a.przetworz()
        s = a.stan()
        assert s.niezapisane == () and len(s.plytki) == 4 and s.komunikaty == () and s.kolejka.niezapisane == 0
        assert a.ponow_zapis() and a.ponow_zapis().dane == 0
    finally:
        a.zamknij()


def test_p7_lista_do_dofrezowania_w_pliku_po_kazdej_zmianie(st):
    """P7 (Z6): kontroler SAM zapisuje liste biezaca do pliku w folderze bazy po kazdej zmianie listy; ``zapisz_liste``
    (17. polecenie) - na zadanie, takze dla doby. W pliku nie ma nazw zlecen."""
    import csv

    plik = st.k.sesja.baza.plik.parent / "do_dofrezowania_biezaca.csv"

    def wiersze() -> list:
        with open(plik, encoding="utf-8", newline="") as f:
            return list(csv.reader(f, delimiter=";"))

    assert st.k.wybierz_operatora("Technik A")
    skan_id = st.wrzuc("zwykla", numer=4)
    assert plik.is_file() and len(wiersze()) == 1 and st.stan().lista_zapisana  # pusta lista: sam naglowek
    p = st.stan().plytka(skan_id)
    assert st.k.ukruszona(p.gniazdo(2).praca.praca_id)
    assert wiersze()[1][:5] == ["9002", str(10 + 2 % 38), "K-1", "4", "2"]  # kuweta, zeby, krazek, plytka, gniazdo
    assert st.k.ukruszona(p.gniazdo(9).praca.praca_id) and len(wiersze()) == 3
    assert st.k.cofnij(p.gniazdo(2).praca.praca_id) and len(wiersze()) == 2 and wiersze()[1][4] == "9"
    plik.unlink()
    odp = st.k.zapisz_liste()
    assert odp and odp.dane == "do_dofrezowania_biezaca.csv" and len(wiersze()) == 2 and "do_dofrezowania_biezaca.csv" in odp.tekst
    odp = st.k.wykonaj("zapisz_liste", st.stan().doba)
    assert odp and odp.dane == f"do_dofrezowania_{st.stan().doba}.csv" and (plik.parent / odp.dane).is_file()
    for nazwa in (plik, plik.parent / odp.dane):
        assert FOLDER_ZLECENIA not in nazwa.read_text(encoding="utf-8") and "Fikcja" not in nazwa.read_text(encoding="utf-8")


def test_d1_zle_argumenty_nigdy_wyjatek(st):
    """D1: kazde polecenie z argumentami zlego typu albo w zlej liczbie zwraca ``Odpowiedz`` (``ok`` False) - nigdy wyjatek."""
    from stanowisko import kontroler_api as K

    zle = (None, "x", [1], 10 ** 30, -(10 ** 30), 1.5, True, (), {"a": 1}, b"\x00", float("nan"))
    # jedyne wywolania z tej listy, ktore maja sens (wylogowanie, zamkniecie pozycji o takim id, lista biezaca, pula bez folderu / folder "x")
    wolno = [("wybierz_operatora", (None,)), ("zamknij_pytanie", ("x",)), ("zamknij_komunikat", ("x",)), ("zapisz_liste", (None,)),
             ("ustaw_pule", (None,)), ("ustaw_pule", ("x",)), ("ustaw_pule", (None, None))]  # lista: argumenty bywaja niehaszowalne
    assert st.k.wybierz_operatora("Technik A")
    for nazwa in K.POLECENIA:
        if nazwa in ("zamknij", "start_skanu"):
            continue
        for argumenty in [(z,) for z in zle] + [(z, z) for z in zle] + [(1, 2, 3, 4)]:
            odp = st.k.wykonaj(nazwa, *argumenty)
            assert isinstance(odp, K.Odpowiedz), (nazwa, argumenty)
            if (nazwa, argumenty) not in wolno:
                assert not odp and odp.kod, (nazwa, argumenty, odp)
            if odp.kod == K.KOD_ZLE_ARGUMENTY:
                assert nazwa in odp.tekst
            if nazwa == "wybierz_operatora":
                st.k.wybierz_operatora("Technik A")
    for funkcja, argumenty in ((st.k.ok, ([1],)), (st.k.podaj_numer_plytki, (1, 10 ** 30)), (st.k.ustaw_pule, (123,)), (st.k.cofnij, ("1",)),
                               (st.k.dopusc_plytke, (None,)), (st.k.szczegoly_pracy, ("x",))):
        odp = funkcja(*argumenty)  # wywolanie wprost (nie przez wykonaj)
        assert odp is None or (isinstance(odp, K.Odpowiedz) and not odp and odp.kod == K.KOD_ZLE_ARGUMENTY), (funkcja.__name__, odp)
    assert not st.k.stan().zamkniety and st.k.wybierz_operatora("Technik B")


def test_d2_stan_tylko_do_odczytu_i_haszowalny(st):
    """D2: liczniki stanu i plytki, konflikty i szczegoly pracy sa tylko do odczytu (zmiana = ``TypeError``), a sam stan ma
    ``hash``; porownanie z ``dict``, ``asdict`` i JSON dzialaja jak dotad."""
    import copy

    from stanowisko import kontroler_api as K

    skan_id = st.wrzuc("zwykla", numer=1)
    s = st.stan()
    p = s.plytka(skan_id)
    for slownik in (s.liczniki, p.liczniki):
        assert isinstance(slownik, dict) and isinstance(slownik, K.ZamrozonySlownik)
        for zmiana in (lambda d: d.__setitem__("zielony", 999), lambda d: d.update(zielony=1), lambda d: d.pop("zielony"), lambda d: d.clear(),
                       lambda d: d.setdefault("x", 1), lambda d: d.__delitem__("zielony"), lambda d: d.popitem()):
            with pytest.raises(TypeError):
                zmiana(slownik)
    assert s.liczniki["zielony"] == 2 and st.stan().liczniki == {"zielony": 2, "czerwony": 2, "zolty": 3, "szary": 1, "pomaranczowy": 1}
    assert isinstance(hash(s), int) and hash(s) == hash(st.stan()) and copy.deepcopy(s) == s
    assert json.loads(json.dumps(dataclasses.asdict(s), default=str))["liczniki"]["zielony"] == 2
    sz = st.k.szczegoly_pracy(p.gniazdo(2).praca.praca_id)
    with pytest.raises(TypeError):
        sz.ubytki[0]["srednica_mm"] = 5.0
    with pytest.raises(TypeError):
        sz.kandydaci[0]["sha16"] = "x"


def test_d6_d7_pytania_otwarte_i_historia_oraz_wylogowanie(st):
    """D6: ``stan.pytania`` = otwarte; przy plytce pytanie zamkniete ("Pozniej") zostaje z ``ukryte=True`` (to samo komunikaty).
    D7: ``wybierz_operatora(None)`` = nikt nie jest wybrany - decyzje odmawiane do ponownego wyboru osoby."""
    skan_id = st.wrzuc("bez_numeru")
    q = st.stan().pytania[0]
    assert not q.ukryte and st.k.zamknij_pytanie(q.id)
    s = st.stan()
    assert s.pytania == () and [x.ukryte for x in s.plytka(skan_id).pytania] == [True] and s.plytka(skan_id).pytania[0].id == q.id
    niezgodny = st.wrzuc("niezgodny_uklad")
    k = [x for x in st.stan().komunikaty if x.skan_id == niezgodny][0]
    assert st.k.zamknij_komunikat(k.id) and [x.ukryte for x in st.stan().plytka(niezgodny).komunikaty] == [True]
    assert st.k.wybierz_operatora("Technik A") and st.k.podaj_numer_plytki(skan_id, 2)
    odp = st.k.wybierz_operatora(None)
    assert odp and odp.kod == "wylogowano" and odp.tekst and st.stan().operator is None and st.stan().wymaga_operatora
    praca = st.stan().plytka(skan_id).gniazdo(2).praca
    odp = st.k.ukruszona(praca.praca_id)
    assert not odp and odp.kod == "brak_operatora" and st.stan().do_dofrezowania == ()
    assert st.k.wybierz_operatora("Technik B") and st.k.ukruszona(praca.praca_id)


def test_polecenia_i_wykonaj(st):
    from stanowisko import kontroler_api as K

    for nazwa in K.POLECENIA:
        assert callable(getattr(st.k, nazwa)), nazwa
        assert getattr(type(st.k), nazwa) is not getattr(K.Kontroler, nazwa), f"{nazwa}: brak implementacji"
    for nazwa in ("stan", "subskrybuj", "odsubskrybuj", "przetworz", "szczegoly_pracy"):
        assert getattr(type(st.k), nazwa) is not getattr(K.Kontroler, nazwa), nazwa
    odp = st.k.wykonaj("usun_wszystko")
    assert isinstance(odp, K.Odpowiedz) and not odp
    assert isinstance(st.k.przetworz(), int)


def test_zamkniecie_konczy_polecenia(st):
    assert st.k.wybierz_operatora("Technik A")
    skan_id = st.wrzuc("czysta", numer=1)
    st.sygnaly.clear()
    assert st.k.zamknij()
    s = st.stan()
    assert s.zamkniety and s.plytka(skan_id) is not None and [z.typ for z in st.sygnaly][-1] == "zamkniety"
    odp = st.k.ukruszona(s.plytka(skan_id).gniazdo(1).praca.praca_id)
    assert not odp and odp.kod == "program_zamkniety"
    assert not st.k.start_skanu() and not st.k.wybierz_operatora("Technik B")
    assert st.k.zamknij() and st.k.przetworz() == 0  # drugie zamkniecie nic nie psuje


def test_lacznik_qt_sygnaly_w_petli_okna(st):
    """Sygnaly Qt dla okna: zegar lacznika sam wola ``przetworz`` i emituje stan, komunikat i pytanie."""
    from PySide6.QtCore import QEventLoop, QTimer
    from PySide6.QtWidgets import QApplication

    from stanowisko import kontroler_api as K

    app = QApplication.instance() or QApplication([])
    assert app.platformName() == "offscreen"
    lacznik = K.lacznik_qt(st.k, okres_ms=10)
    odebrane = {"stan": [], "komunikat": [], "pytanie": [], "zamkniety": 0}
    lacznik.stan_zmieniony.connect(odebrane["stan"].append)
    lacznik.komunikat.connect(odebrane["komunikat"].append)
    lacznik.pytanie.connect(odebrane["pytanie"].append)
    lacznik.zamkniety.connect(lambda: odebrane.__setitem__("zamkniety", odebrane["zamkniety"] + 1))
    petla = QEventLoop()
    if st.nazwa == "atrapa":
        QTimer.singleShot(20, lambda: st.k.symuluj_skan("bez_numeru"))
    else:
        QTimer.singleShot(20, lambda: st.zapisz(st.opis("bez_numeru", None, None, None, None, 0)))
    koniec = time.monotonic() + 90.0
    sprawdzacz = QTimer()
    sprawdzacz.setInterval(20)
    sprawdzacz.timeout.connect(lambda: petla.quit() if odebrane["pytanie"] or time.monotonic() > koniec else None)
    sprawdzacz.start()
    petla.exec()
    sprawdzacz.stop()
    assert [q.rodzaj for q in odebrane["pytanie"]] == ["brak_numeru_plytki"]
    assert odebrane["stan"] and isinstance(odebrane["stan"][-1], K.StanAplikacji) and len(odebrane["stan"][-1].plytki) == 1
    assert not st.k.ukruszona(1) and [k.rodzaj for k in odebrane["komunikat"]] == ["brak_operatora"]
    lacznik.zatrzymaj()
    n = len(odebrane["stan"])
    st.k.zamknij_pytanie(odebrane["pytanie"][0].id)
    assert len(odebrane["stan"]) == n  # po zatrzymaniu lacznik niczego nie emituje


# ----------------------------------------------------------------------------
# tabela statusow i modul bez Qt
# ----------------------------------------------------------------------------
def test_statusy_jedna_tabela_kolorow_i_napisow():
    from stanowisko import porownaj as PO
    from stanowisko import statusy as ST

    wymagane = ("zielony", "czerwony", "zolty", "nie_sprawdzono", "szary", "zatwierdzona_ok", "plytka_nie_z_trybu", "blad_inspekcji", "pusty",
                "podwojny", "poza_gniazdem", "ukruszona", "pomaranczowy", "dofrezowany", "czeka_na_numer", "nieaktywny")
    for klucz in wymagane:
        w = ST.STATUSY[klucz]
        assert w.klucz == klucz and len(w.hex) == 7 and w.hex.startswith("#") and w.opis and (w.napis or klucz == "pusty")
        assert w.kolor is None or w.kolor in ST.KOLORY_PRACY + (ST.KOLOR_BURSZTYNOWY,)
    for kolor in ST.KOLORY_PRACY:  # kazda klasa koloru z session ma swoj status podstawowy
        assert ST.STATUSY[ST.STATUS_WG_KOLORU[kolor]].kolor == kolor
    for klucz, nazwa in (("zielony", "zielony"), ("czerwony", "czerwony"), ("zolty", "zolty"), ("szary", "szary"), ("pomaranczowy", "pomaranczowy"),
                         ("pusty", "pusty"), ("podwojny", "podwojny"), ("poza_gniazdem", "poza")):
        assert ST.STATUSY[klucz].rgb == tuple(PO.KOLORY[nazwa]), klucz  # te same kolory, co okno testowe i mapa PNG
    assert ST.STATUSY_ZIELONE == ("zielony",)
    assert ST.STATUSY["zatwierdzona_ok"].rgb != ST.STATUSY["zielony"].rgb  # "zatwierdzona OK" odroznialna od zwyklego zielonego
    assert ST.STATUSY["pomaranczowy"].napis != ST.STATUSY["dofrezowany"].napis and ST.STATUSY["pomaranczowy"].rgb != ST.STATUSY["dofrezowany"].rgb  # Z9
    assert "poprawka" not in (ST.STATUSY["pomaranczowy"].napis + ST.STATUSY["dofrezowany"].napis).split()  # zadne nie nazywa sie samym slowem "poprawka"
    for status_inspekcji in PO.INSPECT_NA_STATUS:  # kazdy status inspect ma swoj wiersz albo klase koloru
        kolor = PO.INSPECT_NA_STATUS[status_inspekcji]
        if kolor is not None:
            assert ST.status_pracy(kolor, status_skanu="przyjety", status_gniazda=kolor, status_inspekcji=status_inspekcji) in ST.STATUSY
    assert ST.status("cos_nowego").klucz == "nieznany" and ST.status("cos_nowego").kolor == "zolty"  # nowy status z analizy: nigdy zielony
    assert ST.status_pracy("fioletowy", status_skanu="przyjety") == "nieznany"
    assert ST.status_pracy("zielony", status_skanu="przyjety", status_inspekcji="ok", numer_znany=False) == "czeka_na_numer"
    assert ST.status_pracy("zolty", status_skanu="do_powtorzenia", status_gniazda="zielony", status_inspekcji="ok") == "skan_do_powtorzenia"
    assert ST.status_pracy(None, status_skanu="plytka_nie_z_trybu") == "plytka_nie_z_trybu" and ST.status_pracy(None, status_skanu="zastapiony") == "nieaktywny"
    assert [ST.odmiana(n, "decyzja", "decyzje", "decyzji") for n in (1, 2, 5, 12, 22, 25)] == ["decyzja", "decyzje", "decyzji", "decyzji", "decyzje", "decyzji"]
    for rodzaj in ("niezgodny_uklad", "skan_do_powtorzenia", "blad_inspekcji", "plik_zajety", "plik_niedostepny", "plik_zmieniony", "brak_operatora"):
        poziom, tytul, tekst = ST.tekst_komunikatu(rodzaj)
        assert poziom in (ST.POZIOM_INFO, ST.POZIOM_OSTRZEZENIE, ST.POZIOM_BLAD) and tytul and tekst
    for polecenie in ("ukruszona", "ok", "cofnij", "potwierdz_ponowny_skan", "odrzuc_ponowny_skan", "cofnij_zastapienie", "dopusc_plytke",
                      "start_skanu", "odswiez_pule"):
        assert ST.PRZYCISKI[polecenie]


def test_modul_kontraktu_nie_laduje_qt_ani_bibliotek_obliczen():
    """Kontrakt i statusy to biblioteka standardowa: import nie laduje Qt, numpy ani Open3D (plik startowy bez Qt - D8)."""
    kod = ("import sys; from stanowisko import kontroler_api, statusy; "
           "print(sorted(m for m in ('PySide6', 'numpy', 'trimesh', 'open3d') if m in sys.modules))")
    w = subprocess.run([sys.executable, "-c", kod], cwd=STANOWISKO, capture_output=True, text=True, timeout=120)
    assert w.returncode == 0, w.stderr
    assert w.stdout.strip() == "[]"


def test_atrapa_scenariusz_pokazowy_i_sprzatanie(tmp_path):
    from stanowisko import kontroler_api as K
    from stanowisko import silnik as SI

    a = K.AtrapaKontrolera()
    katalog = a.katalog
    skany = a.scenariusz_pokazowy()
    s = a.stan()
    assert set(skany) == {"zwykla", "czysta", "do_powtorzenia", "nie_z_trybu", "bez_numeru"} and len(s.plytki) == 5 and s.operator == "Technik A"
    assert sorted(q.rodzaj for q in s.pytania) == ["brak_numeru_plytki", "plytka_nie_z_trybu"]
    assert sorted(k.rodzaj for k in s.komunikaty) == ["blad_inspekcji", "skan_do_powtorzenia"] and s.konflikty == ()
    assert len(s.do_dofrezowania) == 1 and s.liczniki["zatwierdzona_ok"] == 1
    sz = a.szczegoly_pracy(s.plytka(skany["zwykla"]).gniazdo(2).praca.praca_id)
    podglad = SI.wczytaj_podglad(sz.plik_podgladu)  # ten sam format, co plik z silnika: punkty i odchylki gniazda
    P, d = podglad[2]
    assert P.shape == (600, 3) and d.shape == (600,) and float(d.min()) < -0.1
    z_kontraktu = K.wczytaj_podglad(sz.plik_podgladu)  # D12: okno czyta obraz odchylek przez kontrakt, bez importu silnika
    assert sorted(z_kontraktu) == sorted(podglad) and (z_kontraktu[2][1] == d).all()
    a.symuluj_postep(udzial=0.4, czeka=2)
    assert a.stan().analiza.udzial == pytest.approx(0.4) and a.stan().kolejka.razem == 3
    a.symuluj_postep(udzial=None)
    assert a.stan().analiza is None
    for rodzaj in ("plik_zajety", "plik_niedostepny", "plik_zmieniony", "pula_pusta"):
        k = a.symuluj_komunikat(rodzaj)
        assert k in a.stan().komunikaty and "?" not in k.tekst
    with pytest.raises(ValueError):
        a.symuluj_skan("nie_ma_takiego")
    assert katalog.is_dir()
    a.zamknij()
    assert not katalog.exists()


# ----------------------------------------------------------------------------
# poranek (E3-A7, kontrakt w wersji 3): ten sam zestaw dla atrapy i prawdziwej aplikacji
# ----------------------------------------------------------------------------
PLYTKA_RANO = {1: "pewna", 2: "pewna", 3: "zolta", 4: "nieznana", 5: "pewna", 6: "dwuznaczna", 7: "brak"}
PROJEKTY_RANO = {1: 307, 2: 308, 3: (309, 319), 4: 311, 5: 313, 6: (312, 320), 7: 314}  # 3221 = 307-310, 3228 = 311-312, 3235 = 313


def klasy_rano(st, skan_id: int) -> dict:
    return {p.gniazdo: p.klasa for p in st.stan().rano.plytka(skan_id).prace}


def test_rano_przelacznik_trybu_i_skan_do_sesji_pieca(st):
    """Kryterium A6 dla A7 (recenzja A6, D7): w trybie "rano" skan idzie do ``SesjaRano`` - piec otwiera sie sam, ``skany.sesja_pieca_id``;
    plytka poza stanem wieczoru; klasy prac i kolory = ``session_rano.stan_pieca``; tryb w dzienniku."""
    from stanowisko import kontroler_api as K
    from stanowisko import session_rano as SR
    from stanowisko import statusy as ST

    assert st.stan().tryb == "wieczor" and st.stan().rano is None
    odp = st.k.przelacz_tryb("rano")  # bez osoby
    assert odp and odp.dane == "rano" and st.stan().tryb == "rano" and isinstance(st.stan().rano, K.StanRano)
    assert st.stan().rano.sesja_pieca_id is None and not st.stan().rano.otwarty
    st.poranek()
    skan_id = st.wrzuc_rano(4, PLYTKA_RANO, PROJEKTY_RANO)
    s = st.stan()
    assert s.plytka(skan_id) is None and s.rano.otwarty and s.rano.plan_id.endswith("-p1")
    assert st.k.sesja.baza.wiersz("SELECT tryb, sesja_pieca_id FROM skany WHERE id = ?", (skan_id,)) == {"tryb": "rano", "sesja_pieca_id": s.rano.sesja_pieca_id}
    prawda = SR.SesjaRano(st.k.sesja).stan_pieca()
    oczekiwane = {p["gniazdo"]: p["klasa"] for x in prawda["skany"] for p in x["prace"]}
    assert klasy_rano(st, skan_id) == oczekiwane == {1: "pewna", 2: "pewna", 3: "dwuznaczna", 4: "nieznana", 5: "pewna", 6: "dwuznaczna", 7: "nieznana"}
    plytka = s.rano.plytka(skan_id)
    for g in plytka.gniazda:
        if g.praca is None:
            assert g.status == "pusty"
            continue
        w = ST.status_rano(g.praca.klasa)
        assert (g.rgb, g.kolor, g.praca.status) == (w.hex, SR.KOLOR_KLASY[g.praca.klasa], w.klucz)
        assert g.podpis == (g.praca.kuweta if g.praca.klasa == "pewna" else w.napis)
    p1 = plytka.gniazdo(1).praca
    assert (p1.kuweta, p1.zeby, p1.sha16) == ("3221", K.zab_sztuczny(307), K.projekt_sztuczny(307)) and p1.miniatura.startswith(b"\x89PNG")
    p3 = plytka.gniazdo(3).praca
    assert [k.kuweta for k in p3.kandydaci] == ["3221", "3256"] and all(k.miniatura and k.projekt_id for k in p3.kandydaci)
    assert p3.dozwolone == ("wybierz_kandydata", "przypisz_recznie")
    assert s.rano.liczniki == {"pewna": 3, "dwuznaczna": 2, "nieznana": 2} and s.rano.nierozstrzygniete == {"dwuznaczne": 2, "nieznane": 2}
    assert any(k.id == K.ID_RAMKA_PORANNA for k in s.komunikaty)  # ramka poranna niepodlaczona: komunikat, nie awaria
    assert st.k.przelacz_tryb("wieczor") and st.stan().rano is None
    wpisy = st.k.sesja.baza.wiersze("SELECT dane FROM zdarzenia WHERE typ = 'tryb_zmieniony' ORDER BY id")
    assert [json.loads(w["dane"])["tryb"] for w in wpisy] == ["rano", "wieczor"]


def test_rano_decyzje_wybor_przypisanie_cofniecie_i_odmowy(st):
    from stanowisko import kontroler_api as K

    st.poranek()
    skan_id = st.wrzuc_rano(4, PLYTKA_RANO, PROJEKTY_RANO)
    plytka = st.stan().rano.plytka(skan_id)
    p3, p4 = plytka.gniazdo(3).praca, plytka.gniazdo(4).praca
    assert st.k.wybierz_kandydata(p3.praca_id, p3.kandydaci[0].sha16)
    assert klasy_rano(st, skan_id)[3] == "przypisana" and st.stan().rano.plytka(skan_id).gniazdo(3).rgb == plytka.gniazdo(1).rgb
    projekty = st.k.projekty_kuwety("3228")
    assert [(x.kuweta, x.zeby, x.stan) for x in projekty] == [("3228", K.zab_sztuczny(311), "oczekuje"), ("3228", K.zab_sztuczny(312), "oczekuje")]
    assert all(isinstance(x, K.ProjektPuli) and x.miniatura for x in projekty) and st.k.projekty_kuwety(" 03228 ") == projekty
    assert st.k.projekty_kuwety("1") == () and st.k.projekty_kuwety(None) == ()
    assert st.k.przypisz_recznie(p4.praca_id, projekty[0].projekt_id)  # nieznana przypisana recznie -> konflikt z gniazdem 5? nie: 311 ma tylko gniazdo 4
    assert klasy_rano(st, skan_id)[4] == "przypisana"
    assert st.k.cofnij_przypisanie(p4.praca_id) and klasy_rano(st, skan_id)[4] == "nieznana"
    assert st.k.przypisz_recznie(p4.praca_id) and klasy_rano(st, skan_id)[4] == "nieznana"  # "bez projektu"
    d = st.k.sesja.baza.wiersze("SELECT rodzaj, wartosc, operator FROM decyzje WHERE skan_id = ? ORDER BY id", (skan_id,))
    assert [x["rodzaj"] for x in d] == ["wybor_kandydata", "przypisanie_reczne", "cofniecie", "przypisanie_reczne"] and d[-1]["wartosc"] == ""
    # odmowy: zly kandydat (session_rano), brak osoby, zle argumenty - odpowiedz, nigdy wyjatek
    odp = st.k.wybierz_kandydata(p4.praca_id, "0" * 16)
    assert not odp and odp.kod == "odmowa" and "kandydat" in odp.tekst
    for zle in ((p4.praca_id, 5), ("x", "y"), (True, p3.kandydaci[0].sha16)):
        odp = st.k.wykonaj("wybierz_kandydata", *zle)
        assert not odp and odp.kod == K.KOD_ZLE_ARGUMENTY
    assert st.k.wykonaj("przypisz_recznie", p4.praca_id, "12").kod == K.KOD_ZLE_ARGUMENTY
    assert st.k.wykonaj("przelacz_tryb", "noc").kod == K.KOD_ZLE_ARGUMENTY and st.k.wykonaj("ustaw_kolejnosc", "losowo").kod == K.KOD_ZLE_ARGUMENTY
    assert st.k.wybierz_operatora(None)
    odp = st.k.cofnij_przypisanie(p3.praca_id)
    assert not odp and odp.kod == "brak_operatora"


def test_rano_kolejnosc_kuwet_wybor_po_numerze_rozkladanie(st):
    from stanowisko import session_rano as SR

    st.poranek()
    st.wrzuc_rano(4, PLYTKA_RANO, PROJEKTY_RANO)
    st.wrzuc_rano(5, {1: "pewna", 2: "pewna", 3: "pewna"}, {1: 310, 2: 315, 3: 316})
    rano = SR.SesjaRano(st.k.sesja)
    for kolejnosc in ("liczba", "numer"):
        assert st.k.ustaw_kolejnosc(kolejnosc)
        plan = rano.plan_plytek(kolejnosc=kolejnosc)
        assert [(k.kuweta, k.prac, k.plytki) for k in st.stan().rano.kuwety] == [(k["kuweta"], plan["liczba_prac"][k["kuweta"]], tuple(k["plytki"]))
                                                                               for k in plan["kuwety"]]
    assert st.k.ustaw_kolejnosc("liczba")
    kolejne = [k.kuweta for k in st.stan().rano.kuwety]
    assert kolejne[0] == "3221" and st.stan().rano.kuweta_biezaca == "3221"
    assert st.k.wybierz_kuwete(" 03242") and st.stan().rano.kuweta_biezaca == "3242"  # numer wpisany recznie (zera i spacje bez znaczenia)
    odp = st.k.wybierz_kuwete("9999")
    assert not odp and "9999" in odp.tekst and st.stan().rano.kuweta_biezaca == "3242"
    assert st.k.potwierdz_kuwete().dane == "3242"
    assert st.stan().rano.kuweta_biezaca == "3221" and [k.kuweta for k in st.stan().rano.kuwety if k.potwierdzona] == ["3242"]
    assert st.k.potwierdz_kuwete().dane == "3221" and st.k.cofnij_kuwete().dane == "3221" and st.stan().rano.kuweta_biezaca == "3221"
    for _ in kolejne:
        st.k.potwierdz_kuwete()
    odp = st.k.potwierdz_kuwete()
    assert not odp and st.stan().rano.kuweta_biezaca is None
    wpisy = st.k.sesja.baza.wiersze("SELECT typ, dane FROM zdarzenia WHERE typ LIKE 'kuweta_%' ORDER BY id")
    assert all(json.loads(w["dane"])["operator"] == "Technik A" and json.loads(w["dane"])["plan_id"] == st.stan().rano.plan_id for w in wpisy)


def test_rano_zamknij_piec_wynik_rowny_A6_i_komunikat_excela(st):
    from stanowisko import kontroler_api as K
    from stanowisko import session_rano as SR

    st.poranek()
    skan_id = st.wrzuc_rano(4, PLYTKA_RANO, PROJEKTY_RANO)
    rano = st.stan().rano
    assert rano.dozwolone == ("zamknij_piec",) and rano.blokady == ()
    assert [z.kuweta for z in rano.kompletne] == ["3235"] and [z.kuweta for z in rano.braki] == ["3221"]  # prowizorycznie
    odp = st.k.zamknij_piec()
    assert odp and isinstance(odp.dane, dict)
    wynik = SR.SesjaRano(st.k.sesja).wynik_pieca(rano.sesja_pieca_id)
    assert dict(odp.dane) == wynik or json.loads(json.dumps(odp.dane)) == wynik
    s = st.stan()
    assert not s.rano.otwarty and s.rano.wynik is not None and s.rano.dozwolone == ()
    assert [z.kuweta for z in s.rano.kompletne] == [z["kuweta"] for z in wynik["kompletne"]] == ["3235"]
    assert [(z.kuweta, [b.zeby for b in z.brakujace]) for z in s.rano.braki] == [(z["kuweta"], [b["zeby"] for b in z["brakujace"]]) for z in wynik["braki"]]
    assert [z.kuweta for z in s.rano.braki_biezace] == [z["kuweta"] for z in SR.SesjaRano(st.k.sesja).braki()]
    assert all(b.napis for z in s.rano.braki for b in z.brakujace)
    assert any(k.id == K.ID_EXCEL and "(1)" in k.tekst for k in s.komunikaty)  # bez Excela: komunikat, program dziala dalej
    odp = st.k.przypisz_recznie(s.rano.plytka(skan_id).gniazdo(4).praca.praca_id)
    assert not odp and "zamkniety" in odp.tekst  # piec zamkniety jest zamrozony (A6)
    assert not st.k.zamknij_piec()
    nowy = st.wrzuc_rano(5, {1: "pewna"}, {1: 310})
    assert st.stan().rano.otwarty and st.stan().rano.nr_w_dniu == 2 and st.stan().rano.plytka(nowy) is not None


def test_rano_polecenia_plytki_numer_ponowny_skan_konflikt_blokuje(st):
    st.poranek()
    bez = st.wrzuc_rano(None, {1: "pewna", 2: "pewna"}, {1: 307, 2: 308})
    rano = st.stan().rano
    assert rano.blokady and "numer" in rano.blokady[0].lower() and "zamknij_piec" not in rano.dozwolone
    assert [q.rodzaj for q in st.stan().pytania] == ["brak_numeru_plytki"] and st.stan().pytania[0].numery == (4, 5, 6)
    assert st.k.podaj_numer_plytki(bez, 4) and st.stan().rano.plytka(bez).numer == 4 and st.stan().rano.dozwolone == ("zamknij_piec",)
    st.przesun(2)
    drugi = st.wrzuc_rano(4, {1: "pewna", 3: "pewna"}, {1: 307, 3: 308})
    s = st.stan()
    assert s.rano.plytka(drugi).moze_zastapic == bez and [q.rodzaj for q in s.pytania] == ["ponowny_skan"]
    assert "konflikt" in " ".join(s.rano.blokady).lower() and len(s.rano.konflikty) == 2
    assert st.k.potwierdz_ponowny_skan(drugi)
    s = st.stan()
    assert s.rano.plytka(bez).status == "zastapiony" and s.rano.konflikty == () and s.rano.dozwolone == ("zamknij_piec",)
    assert st.k.cofnij_zastapienie(drugi) and st.stan().rano.plytka(bez).status == "przyjety"


def test_rano_statusy_jedna_tabela_zgodna_z_session_rano():
    from stanowisko import session_rano as SR
    from stanowisko import statusy as ST

    for klasa in SR.KOLOR_KLASY:
        w = ST.status_rano(klasa)
        assert (w.kolor, w.ramka) == (SR.KOLOR_KLASY[klasa], SR.KOLOR_RAMKI[klasa]), klasa
        assert ST.status(w.klucz) is w and w.napis and w.opis
    assert ST.STATUSY["nieznana_rano"].kolor == ST.KOLOR_BIALY and ST.status_rano("nieznana") is ST.STATUSY["nieznana_rano"]
    assert ST.status_rano("poprawka") is ST.STATUSY["dofrezowany"]  # Z9: "zab dofrezowany", nie "poprawiana recznie"
    assert ST.STATUSY_ZIELONE == ("zielony",)  # wiersze poranne nie zmieniaja zielonego wieczoru (P4)
    assert ST.status_rano("nowa_klasa").kolor == ST.KOLOR_ZOLTY  # nieznana klasa: nigdy zielona
    for polecenie in ("wybierz_kandydata", "przypisz_recznie", "cofnij_przypisanie", "zamknij_piec", "potwierdz_kuwete", "cofnij_kuwete"):
        assert ST.PRZYCISKI[polecenie]
    for rodzaj in ("ramka_niedostepna", "excel_niedostepny"):
        assert ST.tekst_komunikatu(rodzaj, ile=1)[2]
