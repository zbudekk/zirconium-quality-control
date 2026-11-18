"""silnik (E3-A2): analiza ``porownaj.porownaj`` w osobnym procesie - kolejka, postep, awarie, wynik rowny wierszowi polecen.

Kryteria odbioru z planu etapu 3 (sekcja 4.1, E3-A2), ktore sprawdza ten plik:
  4. 20 plikow naraz: analiza po kolei w kolejnosci zapisu, zadnego zgubionego (symulator -> scanner -> silnik),
  5. wynik silnika dla sztucznego skanu kazdego z 4 typow plytek = wynik ``porownaj`` z wiersza polecen (pole po polu, poza
     czasami). UWAGA - odstepstwo opisane w ``roznice`` i ``_rowne``: ``porownaj`` nie jest powtarzalne nawet miedzy dwoma
     uruchomieniami wiersza polecen, wiec rownosc bit w bit jest nieosiagalna. Test wymaga: na plytkach z atrap rownosci
     wszystkich pol z tolerancja 2e-3 dla liczb zmiennoprzecinkowych (liczniki probek z tolerancja, bez liczby iteracji),
     na skanach odniesienia rownosci decyzji (struktura, statusy, identyfikatory); liczbe pol roznych przy tolerancji 1e-9
     wypisuje (wymagana tylko z E3A2_SCISLE=1),
  6. silnik wywolany z aplikacji Qt (offscreen) konczy plytke w czasie do 60 s, petla okna bez przerw dluzszych niz 200 ms,
  7. awaria analizy (zly plik, zabity proces) = komunikat i podjecie nastepnego zadania.

Progi czasu (kryterium 6). Zestaw pytest biegnie na komputerze, na ktorym rownolegle licza inne sesje, wiec domyslne progi
testu sa luzniejsze: plytka do PROG_PLYTKI_S = 180 s, przerwa petli do PROG_PRZERWY_S = 1,0 s. Progi z kryterium (60 s
i 0,2 s) wlacza zmienna srodowiskowa E3A2_SCISLE=1; wartosci zmierzone sa wypisywane (pytest -s) i podane w raporcie.

Dane. Testy domyslne buduja male plytki z 3 atrap koron (bez danych z dysku). Te same testy kryteriow 5 i 6 na duzych
sztucznych skanach odniesienia (45-55 MB, pula prawdziwych projektow) wlaczaja zmienne E3A2_DANE_REF (folder ze skanami
``skan_<typ>_n*.stl``) i E3A2_PROJEKTY (folder puli); bez nich te warianty sa pomijane z opisem.

Funkcja ``analiza_probna`` jest ladowana w procesie silnika (parametr ``funkcja``) zamiast ``porownaj``
- dlatego ten modul na poziomie importu uzywa tylko biblioteki standardowej i pytest.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import signal
import subprocess
import sys
import threading
import time
import warnings
from pathlib import Path

import pytest

SCISLE = os.environ.get("E3A2_SCISLE") == "1"
PROG_PLYTKI_S = 60.0 if SCISLE else 180.0  # kryterium 6: 60 s
PROG_PRZERWY_S = 0.2 if SCISLE else 1.0  # kryterium 6: 200 ms
DANE_REF = os.environ.get("E3A2_DANE_REF")
PROJEKTY_REF = os.environ.get("E3A2_PROJEKTY")
BRAK_DANYCH_REF = "wariant na duzych skanach odniesienia: ustaw E3A2_DANE_REF (folder skan_<typ>_n*.stl) i E3A2_PROJEKTY (folder puli)"
TYPY = ("wieczorna", "poranna", "okragla_wieczorna", "okragla_poranna")
STANOWISKO = Path(__file__).resolve().parent.parent
FUNKCJA_PROBNA = "test_silnik:analiza_probna"


# ----------------------------------------------------------------------------
# funkcje wykonywane W PROCESIE SILNIKA zamiast porownaj (ta sama sygnatura wywolania)
# ----------------------------------------------------------------------------
def analiza_probna(skan, foldery, plytka, ust, wspolczynnik=None, numer=None, *reszta, postep=None, **kw):
    """Udaje analize: czyta plik, zglasza postep, zwraca slownik. Tresc pliku steruje awaria (ZLY / ZABIJ / SPIJ <s> /
    GIL <s> = wywolanie natywne, ktore trzyma GIL przez <s> sekund, jak ``segment_plane`` w Open3D / PULA = ostrzezenia
    i uwagi z nazwami plikow i folderow puli, jak ``synth.wczytaj_projekt`` i inspekcja; PULA_BLAD = wyjatek z taka nazwa /
    SLOWNIK = wynik o ksztalcie ``porownaj`` ze slowami ze slownikow wyniku, ``wynik_ze_slownikiem``). ``qt``: czy w procesie
    roboczym jest zaladowane PySide6 (nie powinno byc); ``sciezka``: plik, ktory dostala analiza (N1: kopia robocza)."""
    t0 = time.time()
    dane = Path(skan).read_bytes()
    if postep is not None:
        postep("proba: start", 0.1)
    if dane.startswith(b"ZLY"):
        raise ValueError("zly plik probny")
    if dane.startswith(b"ZABIJ"):
        os._exit(7)  # proces silnika znika bez komunikatu (jak zabity z zewnatrz)
    if dane.startswith(b"SPIJ"):
        time.sleep(float(dane.split()[1]))
    if dane.startswith(b"GIL"):
        import ctypes

        ctypes.PyDLL("kernel32").Sleep(int(float(dane.split()[1]) * 1000))  # PyDLL: wywolanie BEZ zwalniania GIL
    if dane.startswith(b"SLOWNIK"):
        for p in [p for f in foldery for p in sorted(Path(f).rglob("*.stl"))]:
            warnings.warn(f"pomijam projekt {p.name}: brak trojkatow", stacklevel=2)
        return wynik_ze_slownikiem(Path(skan).name)
    uwagi = []
    if dane.startswith(b"PULA"):
        projekty = [p for f in foldery for p in sorted(Path(f).rglob("*.stl")) if p != Path(skan)]
        if dane.startswith(b"PULA_BLAD"):
            raise ValueError(f"nie da sie wczytac projektu {projekty[0].name} z folderu {projekty[0].parent.name} ({projekty[0]})")
        for p in projekty:
            warnings.warn(f"pomijam projekt {p.name}: brak trojkatow", stacklevel=2)
            uwagi.append(f"zob. {p.parent.name} / {p.stem.upper()}")
    time.sleep(0.05)
    if postep is not None:
        postep("proba: koniec", 0.9)
    wynik = {"skan": Path(skan).name, "plytka": plytka, "numer": numer, "wspolczynnik": wspolczynnik, "bajtow": len(dane), "qt": "PySide6" in sys.modules,
             "pid": os.getpid(), "start": t0, "koniec": time.time(), "gniazda": [], "czas_s": {"razem": round(time.time() - t0, 3)}, "sciezka": str(skan)}
    if uwagi:
        wynik["uwagi"] = uwagi
    return wynik


def wynik_ze_slownikiem(skan: str) -> dict:
    """Wynik o ksztalcie ``porownaj`` (N2): w polach decyzji slowa ze slownikow wyniku - statusy inspekcji (``ok``, ``sprawdz``),
    typy pracy (``waxup``, ``korona``, ``most``), kolory gniazd; w tekstach wolnych (uwagi, powod, blad, komunikat) nazwy
    plikow i folderow puli, ktore silnik ma usunac."""

    def gniazdo(nr: int, kolor: str, typ: str, inspekcja: str | None) -> dict:
        return {"gniazdo": nr, "status_fragmentu": "praca", "punkty": 1000 + nr, "srodek": [1.0, 2.0, 3.0], "status": "szary" if kolor == "szary" else "zielony",
                "pewnosc": 0.5, "uwagi": [f"zob. Fikcyjna Testowa 4321 / {typ}"],
                "kandydaci": [{"id": f"{nr:016x}", "zeby": ["11"], "typ": typ, "pokrycie": 0.9, "metoda": "ransac", "filtr_ok": True, "powod_filtru": "",
                               "skala": None}],
                "skala": {"poprawka_proc": 0.1, "zastosowana": False, "powod": "korona ok", "ostrzezenie": False, "niepewna": False},
                "inspekcja": None if inspekcja is None else {"gniazdo": nr, "projekt": f"{nr:016x}", "status": inspekcja, "pokrycie": 0.9, "ubytki": [],
                                                             "uwagi": [f"{inspekcja}: FikcyjnaTestowa-11-crown_cad"], "brzeg": {"status": "ok"}},
                "status_gniazda": kolor}

    gniazda = [gniazdo(1, "zielony", "waxup", "ok"), gniazdo(2, "zolty", "korona", "sprawdz"), gniazdo(3, "szary", "most", None)]
    gniazda[1]["inspekcja"]["blad"] = "ValueError: FikcyjnaTestowa-11-crown_cad.stl"
    return {"skan": skan, "plytka": "wieczorna", "plytka_wybor": "auto", "uklad_zgodny": True, "uklad_komunikat": "folder Fikcyjna Testowa 4321",
            "uklad_auto": {"wybrany": "wieczorna", "pewny": True, "powod": "jedyny pasujacy uklad", "kandydaci": [{"plytka": "wieczorna", "zgodny": True}]},
            "numer": 7, "numer_zrodlo": "dolki", "gniazda": gniazda, "statusy_gniazd": {"zielony": 1, "czerwony": 0, "zolty": 1, "szary": 1, "pomaranczowy": 0},
            "ubytki": 0}


TEKSTY_WOLNE = {"ostrzezenia", "uwagi", "blad", "powod", "powod_filtru", "uklad_komunikat", "uklad_podpowiedz"}  # pola, ktore wolno czyscic (N2)


def bez_tekstow(o):
    """Wynik bez pol z tekstem wolnym (``TEKSTY_WOLNE``) - zostaja pola decyzji: statusy, typy, identyfikatory, liczby."""
    if isinstance(o, dict):
        return {k: bez_tekstow(v) for k, v in o.items() if k not in TEKSTY_WOLNE}
    if isinstance(o, list):
        return [bez_tekstow(v) for v in o]
    return o


def _skrot(dane: bytes) -> str:
    return hashlib.sha256(dane).hexdigest()[:16]


def _pid_martwego_procesu() -> int:
    """Numer procesu, ktory juz sie zakonczyl (jak proces roboczy zabity w trakcie zadania)."""
    w = subprocess.run([sys.executable, "-c", "import os; print(os.getpid())"], capture_output=True, text=True, timeout=60)
    return int(w.stdout.strip())


# ----------------------------------------------------------------------------
# narzedzia testow
# ----------------------------------------------------------------------------
@pytest.fixture(scope="module", autouse=True)
def _qt_przed_silnikiem():
    """Qt ladowane w procesie testow PRZED pierwszym uzyciem silnika - w tej kolejnosci pracuje aplikacja (okno startuje
    pierwsze). Powod: na PC wlasciciela 17.11.2026 pierwszy import PySide6 dopiero PO wykonaniu prawdziwych analiz przez
    silnik (przebieg samych wariantow ``-k odniesienia``) konczyl sie bledem "DLL load failed while importing Shiboken"
    w 3 z 3 prob; z Qt zaladowanym wczesniej albo po imporcie Open3D w procesie testow - 0 bledow. Przyczyny nie ustalono
    (prostsze proby odtworzenia poza ta sciezka: 0 z 12); opis w raporcie paczki. Proces roboczy silnika tej funkcji nie
    wykonuje."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import PySide6.QtCore  # noqa: F401


class Odbior:
    """Zbiera zdarzenia silnika (wywolywany w watku nadzorcy)."""

    def __init__(self):
        self.wszystkie = []
        self._zmiana = threading.Condition()

    def __call__(self, z) -> None:
        with self._zmiana:
            self.wszystkie.append(z)
            self._zmiana.notify_all()

    def typu(self, *typy):
        return [z for z in list(self.wszystkie) if z.typ in typy]

    def koncowe(self):
        return self.typu("wynik", "blad")

    def czekaj(self, warunek, limit_s: float = 120.0) -> bool:
        with self._zmiana:
            return self._zmiana.wait_for(warunek, limit_s)

    def czekaj_na_koncowe(self, ile: int, limit_s: float = 120.0) -> list:
        assert self.czekaj(lambda: len([z for z in self.wszystkie if z.typ in ("wynik", "blad")]) >= ile, limit_s), \
            [(z.typ, z.zadanie_id, z.rodzaj, z.blad) for z in self.wszystkie if z.typ != "postep"]
        return self.koncowe()


@pytest.fixture
def silnik_probny():
    """Funkcja ``start(**parametry) -> (Silnik, Odbior)`` z funkcja probna zamiast porownaj; silniki sa zatrzymywane po tescie."""
    from stanowisko import silnik as SI

    uruchomione = []

    def start(**parametry):
        odb = Odbior()
        s = SI.Silnik(ust={}, na_zdarzenie=odb, **{"funkcja": FUNKCJA_PROBNA, **parametry})
        s.start()
        uruchomione.append(s)
        return s, odb

    yield start
    for s in uruchomione:
        s.stop()


def _zadanie(skan: Path, **pola):
    from stanowisko import silnik as SI

    return SI.ZadanieAnalizy(skan=skan, pula=SI.OpisPuli(foldery=(str(skan.parent),)), **pola)


def _proces_zyje(pid: int) -> bool:
    if os.name == "nt":  # os.kill(pid, 0) na Windows KONCZY proces, wiec pytamy system o kod wyjscia
        import ctypes

        k32 = ctypes.windll.kernel32
        uchwyt = k32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not uchwyt:
            return False
        kod = ctypes.c_ulong()
        k32.GetExitCodeProcess(uchwyt, ctypes.byref(kod))
        k32.CloseHandle(uchwyt)
        return kod.value == 259  # STILL_ACTIVE
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def bez_czasow(o):
    """Wynik bez pol czasu (klucze ``czas...``) - porownanie "pole po polu, poza czasami"."""
    if isinstance(o, dict):
        return {k: bez_czasow(v) for k, v in o.items() if not k.startswith("czas")}
    if isinstance(o, list):
        return [bez_czasow(v) for v in o]
    return o


TOL_SZUMU = 1e-9  # poziom 1: szum numeryczny
TOL_DECYZJI = 2e-3  # poziom 2: 0,002 mm (albo wzglednie) - 25 razy ponizej najmniejszego progu decyzji (0,05 mm)
TOL_SKANOW_ODNIESIENIA = 0.1  # poziom 3: 0,1 mm bezwzglednie


def _licznik_punktow(sciezka: str) -> str | None:
    """``iteracje`` albo ``punkty`` dla pol-licznikow probek (po nazwie pola), None dla pozostalych pol. Licznik probek =
    ile punktow albo komorek spelnilo warunek odleglosci: w wyniku ``porownaj`` to pola z ``punkt`` w nazwie (``punkty``,
    ``punktow_w_pasie_brzegu``, ``pierscien_punkty``, ``icp_punkty`` ...), ``komorek`` i ``brak_danych``. Pola decyzji i
    tozsamosci (``gniazdo``, ``numer``, ``nr``, ``filar``, ``filarow``, ``wciec``, ``ubytki``, ``projekty``, ``statusy_gniazd``,
    ``bity`` ...) NIE sa licznikami - musza byc rowne."""
    nazwa = sciezka.rsplit(".", 1)[-1].split("[", 1)[0]
    if nazwa == "iteracje":
        return "iteracje"
    return "punkty" if "punkt" in nazwa or nazwa in ("komorek", "brak_danych") else None


def roznice(a, b, sciezka="", tol: float = TOL_SZUMU, liczniki_z_tolerancja: bool = False, tol_wzgl: float | None = None) -> list[str]:
    """Lista pol, ktorymi roznia sie dwie struktury JSON. Wszystko porownywane dokladnie, poza liczbami zmiennoprzecinkowymi:
    te moga sie roznic o ``tol`` (bezwzglednie) albo o ``tol_wzgl`` wzglednie (domyslnie tez ``tol``; 0 = tylko prog
    bezwzgledny). ``liczniki_z_tolerancja``: pola ``iteracje`` sa pomijane, a liczniki probek (``_licznik_punktow``) moga
    sie roznic o 2 albo 1 %.

    Dlaczego nie rownosc bit w bit: ``porownaj`` nie jest powtarzalne - DWA URUCHOMIENIA Z WIERSZA POLECEN na tym samym
    skanie roznia sie (pomiary 17.11.2026 na PC: 2 x 6 przebiegow na plytkach z atrap, 3 przebiegi na skanie odniesienia):
    (1) zawsze szumem rzedu 1e-15 w 31-224 polach (ICP Open3D liczy wielowatkowo; ta sama uwaga i tolerancja 1e-9 jest
    w test_auto_uklad.py), (2) czasem (2 z 12 i 1 z 3 przebiegow) inna galezia ICP korekty skali jednego gniazda:
    ``skala.iteracje`` 20 albo 41, liczniki punktow i komorek o 1, transformacja o ok. 1e-5, a za tym pokrycie o 1e-4,
    szerokosc wciecia o 0,001 mm. Poziom 1 (``TOL_SZUMU``) przepuszcza tylko (1); poziom 2 (``TOL_DECYZJI`` + ``liczniki_z_tolerancja``)
    jest odporny takze na (2) i nadal wymaga rownych statusow, identyfikatorow, numerow, liczby gniazd / kandydatow /
    ubytkow i tekstow."""
    licznik = _licznik_punktow(sciezka) if liczniki_z_tolerancja else None
    if licznik == "iteracje":
        return []
    liczby = lambda x: isinstance(x, (int, float)) and not isinstance(x, bool)  # noqa: E731
    if liczby(a) and liczby(b):
        if isinstance(a, float) or isinstance(b, float):
            wzgl = tol if tol_wzgl is None else tol_wzgl
            return [] if math.isclose(a, b, rel_tol=wzgl, abs_tol=tol) or (math.isnan(a) and math.isnan(b)) else [f"{sciezka}: {a!r} != {b!r}"]
        if licznik == "punkty" and abs(a - b) <= max(2, 0.01 * max(abs(a), abs(b))):
            return []
        return [] if a == b else [f"{sciezka}: {a!r} != {b!r}"]
    if type(a) is not type(b):
        return [f"{sciezka}: typ {type(a).__name__} != {type(b).__name__}"]
    if isinstance(a, dict):
        w = [f"{sciezka}.{k}: brak po jednej stronie" for k in sorted(set(a) ^ set(b))]
        for k in sorted(set(a) & set(b)):
            w += roznice(a[k], b[k], f"{sciezka}.{k}", tol, liczniki_z_tolerancja, tol_wzgl)
        return w
    if isinstance(a, list):
        if len(a) != len(b):
            return [f"{sciezka}: dlugosc {len(a)} != {len(b)}"]
        w = []
        for i, (x, y) in enumerate(zip(a, b)):
            w += roznice(x, y, f"{sciezka}[{i}]", tol, liczniki_z_tolerancja, tol_wzgl)
        return w
    return [] if a == b else [f"{sciezka}: {a!r} != {b!r}"]


# ----------------------------------------------------------------------------
# budowa modulu: proces okna nie laduje ciezkich bibliotek
# ----------------------------------------------------------------------------
def test_import_silnika_i_scannera_nie_laduje_open3d_ani_qt():
    """Open3D nie moze trafic do procesu okna: import ``silnik`` i ``scanner`` nie pociaga open3d, numpy, trimesh ani Qt."""
    kod = ("import sys; import stanowisko.silnik, stanowisko.scanner; "
           "zle = [m for m in ('open3d', 'numpy', 'trimesh', 'scipy', 'PySide6') if m in sys.modules]; print(zle); sys.exit(1 if zle else 0)")
    w = subprocess.run([sys.executable, "-c", kod], cwd=str(STANOWISKO), capture_output=True, text=True, env={**os.environ, "PYTHONPATH": os.pathsep.join(sys.path)})
    assert w.returncode == 0, w.stdout + w.stderr


# ----------------------------------------------------------------------------
# kolejka i kontrakt (funkcja probna)
# ----------------------------------------------------------------------------
def test_kolejka_20_zadan_po_kolei(tmp_path, silnik_probny):
    s, odb = silnik_probny()
    pliki = []
    for i in range(20):
        p = tmp_path / f"s{i:02d}.stl"
        p.write_bytes(b"x" * (100 + i))
        pliki.append(p)
    ids = [s.zlec(_zadanie(p, numer=i, skan_sha16=_skrot(p.read_bytes()))) for i, p in enumerate(pliki)]
    assert ids == sorted(ids) and len(set(ids)) == 20
    koncowe = odb.czekaj_na_koncowe(20)
    assert [z.typ for z in koncowe] == ["wynik"] * 20
    assert [z.zadanie_id for z in koncowe] == ids  # kolejnosc zlecen, zadnego zgubionego
    wyniki = [z.wynik for z in koncowe]
    assert [w["skan"] for w in wyniki] == [p.name for p in pliki]
    assert [w["zadanie_id"] for w in wyniki] == ids and [w["skan_sha16"] for w in wyniki] == [_skrot(p.read_bytes()) for p in pliki]
    assert [w["numer"] for w in wyniki] == list(range(20))
    assert "PySide6" in sys.modules and not any(w["qt"] for w in wyniki)  # D8: Qt jest w procesie testow (okna), nie w procesie roboczym
    assert all(a["koniec"] <= b["start"] for a, b in zip(wyniki, wyniki[1:]))  # jedna analiza naraz
    assert len({w["pid"] for w in wyniki}) == 1 and wyniki[0]["pid"] != os.getpid()  # jeden proces, inny niz proces testu
    assert wyniki[0]["pid"] == s.pid
    # zdarzenia jednego zadania: start -> postep (rosnacy) -> wynik
    for i in ids:
        moje = [z for z in odb.wszystkie if z.zadanie_id == i]
        assert [z.typ for z in moje][0] == "start" and [z.typ for z in moje][-1] == "wynik"
        udzialy = [z.udzial for z in moje if z.typ == "postep"]
        assert udzialy == [0.1, 0.9] and [z.etap for z in moje if z.typ == "postep"] == ["proba: start", "proba: koniec"]
    assert odb.typu("gotowy") and s.w_kolejce() == 0 and not s.zajety()


def test_skrot_skanu_liczony_gdy_nie_podany(tmp_path, silnik_probny):
    import hashlib

    s, odb = silnik_probny()
    p = tmp_path / "a.stl"
    p.write_bytes(b"zawartosc skanu")
    s.zlec(_zadanie(p, uklad="rozpoznaj"))
    w = odb.czekaj_na_koncowe(1)[0].wynik
    assert w["skan_sha16"] == hashlib.sha256(b"zawartosc skanu").hexdigest()[:16]
    assert w["plytka"] == "auto"  # "rozpoznaj" z kontraktu planu = plytka="auto" w porownaj (zalozenie Z2)
    assert w["ostrzezenia"] == []


def test_awarie_zly_plik_zabity_proces_brak_pliku(tmp_path, silnik_probny):
    """Kryterium 7 na funkcji probnej: kazda awaria = zdarzenie ``blad`` z rodzajem i tekstem, nastepne zadanie jest wykonane."""
    s, odb = silnik_probny()
    tresci = [b"dobry 1", b"ZLY plik", b"ZABIJ proces", b"dobry 2", None, b"dobry 3"]
    ids = []
    for i, t in enumerate(tresci):
        p = tmp_path / f"s{i}.stl"
        if t is not None:
            p.write_bytes(t)
        ids.append(s.zlec(_zadanie(p)))
    koncowe = odb.czekaj_na_koncowe(6)
    assert [z.zadanie_id for z in koncowe] == ids
    assert [(z.typ, z.rodzaj) for z in koncowe] == [("wynik", ""), ("blad", "analiza"), ("blad", "proces"), ("wynik", ""), ("blad", "analiza"), ("wynik", "")]
    assert "ValueError" in koncowe[1].blad and "zly plik probny" in koncowe[1].blad and "Traceback" in koncowe[1].szczegoly
    assert "proces silnika" in koncowe[2].blad and "7" in koncowe[2].blad  # kod wyjscia procesu w komunikacie
    assert "s4.stl" in koncowe[4].blad  # brak pliku skanu: nazwa pliku w komunikacie
    assert koncowe[0].wynik["pid"] != koncowe[3].wynik["pid"] == koncowe[5].wynik["pid"]  # po awarii procesu pracuje nowy proces
    assert all(z.zadanie is not None and z.czas_s is not None for z in koncowe)
    assert len(odb.typu("gotowy")) == 2  # start i jeden restart


def test_zabicie_procesu_z_zewnatrz(tmp_path, silnik_probny):
    s, odb = silnik_probny()
    wolny, szybki = tmp_path / "wolny.stl", tmp_path / "szybki.stl"
    wolny.write_bytes(b"SPIJ 30")
    szybki.write_bytes(b"dobry")
    a, b = s.zlec(_zadanie(wolny)), s.zlec(_zadanie(szybki))
    assert odb.czekaj(lambda: any(z.typ == "postep" and z.zadanie_id == a for z in odb.wszystkie), 60.0)
    pid = s.pid
    os.kill(pid, signal.SIGTERM)  # Windows: TerminateProcess
    koncowe = odb.czekaj_na_koncowe(2, 60.0)
    assert [(z.zadanie_id, z.typ, z.rodzaj) for z in koncowe] == [(a, "blad", "proces"), (b, "wynik", "")]
    assert koncowe[1].wynik["pid"] != pid


def test_limit_czasu_zadania(tmp_path, silnik_probny):
    s, odb = silnik_probny(limit_zadania_s=1.5)
    wolny, szybki = tmp_path / "wolny.stl", tmp_path / "szybki.stl"
    wolny.write_bytes(b"SPIJ 60")
    szybki.write_bytes(b"dobry")
    a, b = s.zlec(_zadanie(wolny)), s.zlec(_zadanie(szybki))
    koncowe = odb.czekaj_na_koncowe(2, 60.0)
    assert [(z.zadanie_id, z.typ, z.rodzaj) for z in koncowe] == [(a, "blad", "limit_czasu"), (b, "wynik", "")]
    assert 1.5 <= koncowe[0].czas_s < 20.0


def test_blad_startu_procesu_nie_petli_sie(tmp_path, silnik_probny):
    """Proces silnika, ktory nie umie wystartowac (tu: nieistniejaca funkcja analizy), oddaje blad kazdemu zadaniu i nie restartuje sie bez konca."""
    s, odb = silnik_probny(funkcja="nie_ma_takiego_modulu_e3a2:funkcja")
    p = tmp_path / "a.stl"
    p.write_bytes(b"dobry")
    ids = [s.zlec(_zadanie(p)), s.zlec(_zadanie(p))]
    koncowe = odb.czekaj_na_koncowe(2, 60.0)
    assert [(z.zadanie_id, z.typ, z.rodzaj) for z in koncowe] == [(ids[0], "blad", "start"), (ids[1], "blad", "start")]
    assert "nie_ma_takiego_modulu_e3a2" in koncowe[0].blad
    time.sleep(1.0)
    assert s.stan()["starty_procesu"] <= 3  # bez zadan w kolejce nie ma kolejnych prob


def test_anulowanie_i_stop(tmp_path, silnik_probny):
    s, odb = silnik_probny()
    wolny, szybki = tmp_path / "wolny.stl", tmp_path / "szybki.stl"
    wolny.write_bytes(b"SPIJ 1.0")
    szybki.write_bytes(b"dobry")
    a, b, c = s.zlec(_zadanie(wolny)), s.zlec(_zadanie(szybki)), s.zlec(_zadanie(szybki))
    assert odb.czekaj(lambda: any(z.typ == "start" and z.zadanie_id == a for z in odb.wszystkie), 60.0)
    assert s.anuluj(b) is True and s.anuluj(a) is False and s.anuluj(999) is False  # zadania w toku nie da sie anulowac
    koncowe = odb.czekaj_na_koncowe(2)
    assert [z.zadanie_id for z in koncowe] == [a, c]
    assert s.czekaj_na_pusta_kolejke(10.0) is True
    pid = s.pid
    s.stop()
    assert not s.dziala() and s.pid is None
    with pytest.raises(RuntimeError):
        s.zlec(_zadanie(szybki))
    # proces silnika konczy sie razem z silnikiem
    t0 = time.time()
    while _proces_zyje(pid) and time.time() - t0 < 10:
        time.sleep(0.1)
    assert not _proces_zyje(pid), "proces silnika zyje po stop()"


def test_kolejka_zdarzen_bez_funkcji_zwrotnej(tmp_path):
    from stanowisko import silnik as SI

    p = tmp_path / "a.stl"
    p.write_bytes(b"dobry")
    with SI.Silnik(ust={}, funkcja=FUNKCJA_PROBNA) as s:  # start i stop przez "with"
        nr = s.zlec(_zadanie(p))
        typy = []
        while not typy or typy[-1] not in ("wynik", "blad"):
            z = s.zdarzenia.get(timeout=60.0)
            if z.zadanie_id == nr:
                typy.append(z.typ)
    assert typy == ["start", "postep", "postep", "wynik"]


def test_komunikat_bledu_bez_nazw_plikow_puli():
    """K10: nazwy plikow projektow (nazwiska) nie wychodza z procesu silnika w tekscie bledu."""
    from stanowisko import silnik as SI

    foldery = ["C:\\dane\\Cyrkon", "D:/prywatne"]
    tekst = ("PermissionError: [Errno 13] Permission denied: 'C:\\\\dane\\\\Cyrkon\\\\Kowalski Jan 3263\\\\kowalski-11-crown_cad.stl'\n"
             "  plik C:\\dane\\Cyrkon\\Nowak 12\\nowak_cad.stl uszkodzony; D:/prywatne/#1234 Wisniewska/x.stl; skan C:\\skany\\plytka.stl")
    czysty = SI.bez_nazw_z_puli(tekst, foldery)
    for nazwisko in ("Kowalski", "kowalski", "Nowak", "nowak", "Wisniewska"):
        assert nazwisko not in czysty
    assert "plytka.stl" in czysty and "PermissionError" in czysty and czysty.count("<projekt>") == 3


def test_nazwy_plikow_i_folderow_puli_zastapione_skrotem(tmp_path):
    """P5: sama nazwa pliku projektu (bez sciezki) i nazwa folderu zlecenia tez nie wychodza - plik dostaje ``<projekt sha16>``,
    folder ``<projekt>``; ``foldery_projektow`` (folder puli podany w zadaniu) zostaje, liczby i inne pola bez zmian."""
    from stanowisko import silnik as SI

    pula = tmp_path / "pula"
    (pula / "Fikcyjna Testowa 4321").mkdir(parents=True)
    (pula / "12").mkdir()
    (pula / "Fikcyjna Testowa 4321" / "FikcyjnaTestowa-11-crown_cad.stl").write_bytes(b"smiec")
    (pula / "12" / "a.stl").write_bytes(b"x")
    cz = SI.CzyscicielNazw([str(pula)])
    t = cz("pomijam projekt FikcyjnaTestowa-11-crown_cad.stl: pusty; folder Fikcyjna Testowa 4321; gniazdo 12; plik a.stl i fikcyjnatestowa-11-crown_cad.STL")
    assert "ikcyjna" not in t.lower() and "testowa" not in t.lower()
    assert t.count(f"<projekt {_skrot(b'smiec')}>") == 2 and f"<projekt {_skrot(b'x')}>" in t and "folder <projekt>;" in t
    assert "gniazdo 12;" in t  # nazwa folderu bez liter (numer kuwety) nie jest dana osobowa i nie psuje liczb w tekscie
    wynik = {"ostrzezenia": ["pomijam projekt FikcyjnaTestowa-11-crown_cad.stl: x"], "foldery_projektow": [str(pula)], "ubytki": 5, "uklad_zgodny": True,
             "gniazda": [{"uwagi": ["zob. Fikcyjna Testowa 4321"], "inspekcja": {"blad": "ValueError: FikcyjnaTestowa-11-crown_cad.stl", "pokrycie": 0.5}}]}
    czysty = cz.oczysc(wynik)
    assert "ikcyjna" not in json.dumps({k: v for k, v in czysty.items() if k != "foldery_projektow"}).lower()
    assert czysty["foldery_projektow"] == [str(pula)] and czysty["ubytki"] == 5 and czysty["uklad_zgodny"] is True
    assert czysty["gniazda"][0]["inspekcja"]["pokrycie"] == 0.5 and czysty["gniazda"][0]["uwagi"] == ["zob. <projekt>"]
    assert SI.CzyscicielNazw([str(tmp_path / "nie_ma")])("tekst bez zmian") == "tekst bez zmian"
    # nazwa tylko jako czesc dluzszej nazwy albo slowa nie jest ruszana (skan "plytka.stl" przy projekcie "a.stl")
    assert cz("skan plytka.stl; plik a.stl.") == f"skan plytka.stl; plik <projekt {_skrot(b'x')}>."


def _bez_nazwiska(tekst: str) -> bool:
    return "fikcyjn" not in tekst.lower() and "testowa" not in tekst.lower()


def test_nazwy_z_puli_nie_wychodza_z_silnika(tmp_path, silnik_probny):
    """P5 na silniku (funkcja probna udaje ``synth.wczytaj_projekt`` i inspekcje): projekt w puli, ktorego nie da sie
    wczytac, z fikcyjnym nazwiskiem w nazwie pliku i folderu -> 0 wystapien w zdarzeniach (wynik, blad, szczegoly) i w
    plikach wyjscia; w ich miejscu skrot pliku albo znacznik."""
    from stanowisko import silnik as SI

    s, odb = silnik_probny()
    pula = tmp_path / "pula"
    (pula / "Fikcyjna Testowa 4321").mkdir(parents=True)
    (pula / "Fikcyjna Testowa 4321" / "FikcyjnaTestowa-11-crown_cad.stl").write_bytes(b"smiec")
    skany = tmp_path / "skany"
    skany.mkdir()
    ok, zly = skany / "ok.stl", skany / "zly.stl"
    ok.write_bytes(b"PULA ostrzezenia")
    zly.write_bytes(b"PULA_BLAD")
    opis, wyj = SI.OpisPuli(foldery=(str(pula),)), tmp_path / "wyniki"
    ids = [s.zlec(SI.ZadanieAnalizy(skan=p, pula=opis, wyjscie=wyj)) for p in (ok, zly)]
    koncowe = odb.czekaj_na_koncowe(2, 60.0)
    assert [(z.zadanie_id, z.typ, z.rodzaj) for z in koncowe] == [(ids[0], "wynik", ""), (ids[1], "blad", "analiza")]
    znacznik = f"<projekt {_skrot(b'smiec')}>"
    w = koncowe[0].wynik
    assert w["ostrzezenia"] == [f"pomijam projekt {znacznik}: brak trojkatow"] and w["uwagi"] == [f"zob. <projekt> / {znacznik}"]
    assert koncowe[1].blad.startswith(f"ValueError: nie da sie wczytac projektu {znacznik} z folderu <projekt> (")
    assert "Traceback" in koncowe[1].szczegoly
    pliki = list(wyj.iterdir())
    assert [p.name for p in pliki] == [Path(koncowe[0].pliki["wynik"]).name]
    for tekst in [repr(z) for z in odb.wszystkie] + [p.read_text(encoding="utf-8") for p in pliki]:
        assert _bez_nazwiska(tekst), tekst[:500]


def test_plik_nadpisany_w_kolejce_nie_dostaje_cudzego_skrotu(tmp_path, silnik_probny):
    """P1, proba ``s1`` recenzenta: plik zapisany ponownie pod ta sama nazwa, gdy jego zadanie czeka w kolejce. Zadanie ze
    starym skrotem konczy sie ``plik_zmieniony`` (bez wyniku); nowa tresc ma wlasne zadanie i wynik ze SWOIM skrotem."""
    s, odb = silnik_probny()
    wolny, x = tmp_path / "wolny.stl", tmp_path / "x.stl"
    tresc1, tresc2 = b"plytka A " * 20, b"plytka B, inna " * 20
    wolny.write_bytes(b"SPIJ 1.5")
    x.write_bytes(tresc1)
    a = s.zlec(_zadanie(wolny))
    b = s.zlec(_zadanie(x, skan_sha16=_skrot(tresc1)))
    assert odb.czekaj(lambda: any(z.typ == "start" and z.zadanie_id == a for z in odb.wszystkie), 60.0)
    x.write_bytes(tresc2)  # nadpisanie, gdy zadanie b czeka w kolejce
    c = s.zlec(_zadanie(x, skan_sha16=_skrot(tresc2)))  # zdarzenie ze scannera dla nowej tresci
    koncowe = odb.czekaj_na_koncowe(3, 60.0)
    assert [(z.zadanie_id, z.typ, z.rodzaj) for z in koncowe] == [(a, "wynik", ""), (b, "blad", "plik_zmieniony"), (c, "wynik", "")]
    assert koncowe[1].wynik is None and _skrot(tresc1) in koncowe[1].blad and _skrot(tresc2) in koncowe[1].blad
    assert koncowe[2].wynik["skan_sha16"] == _skrot(tresc2) and koncowe[2].wynik["bajtow"] == len(tresc2)
    assert not any(z.typ == "postep" and z.zadanie_id == b for z in odb.wszystkie)  # analizy zmienionego pliku nie zaczynano


def test_plik_zmieniony_w_trakcie_analizy(tmp_path, silnik_probny):
    """P1 po N1 (runda 3): plik nadpisany, gdy analiza juz trwa. Analiza czyta WLASNA KOPIE pliku zrobiona przed analiza,
    wiec wynik nalezy do tresci ze zdarzenia (skrot, liczba bajtow) - nie do nowej, ktora dostaje wlasne zdarzenie skanu.
    (Runda 2: wynik odrzucany jako ``plik_zmieniony``, bo nie bylo wiadomo, ktora tresc przeczytala analiza.)"""
    s, odb = silnik_probny()
    p, q = tmp_path / "n.stl", tmp_path / "q.stl"
    stara, nowa = b"SPIJ 1.5 tresc ze zdarzenia", b"inna tresc zapisana w trakcie analizy, dluzsza"
    p.write_bytes(stara)
    q.write_bytes(b"dobry")
    a, b = s.zlec(_zadanie(p, skan_sha16=_skrot(stara))), s.zlec(_zadanie(q))
    assert odb.czekaj(lambda: any(z.typ == "postep" and z.zadanie_id == a for z in odb.wszystkie), 60.0)
    p.write_bytes(nowa)  # program skanera nadpisuje plik w trakcie analizy
    koncowe = odb.czekaj_na_koncowe(2, 60.0)
    assert [(z.zadanie_id, z.typ, z.rodzaj) for z in koncowe] == [(a, "wynik", ""), (b, "wynik", "")], [z.blad for z in koncowe]
    assert koncowe[0].wynik["skan_sha16"] == _skrot(stara) and koncowe[0].wynik["bajtow"] == len(stara)  # wynik = tresc analizowana
    assert koncowe[1].wynik["skan_sha16"] == _skrot(b"dobry")


# ----------------------------------------------------------------------------
# runda 3 recenzji PR #17: N1 (kopia robocza skanu), N2 (czyszczenie tylko tekstow wolnych), D-N3 ... D-N6
# ----------------------------------------------------------------------------
WINDOWS = pytest.mark.skipif(os.name != "nt", reason="uchwyt wylaczny (plik otwarty bez zgody na wspoldzielenie) i obiekt zadania istnieja tylko na Windows")


def _czekaj_na(odb: Odbior, zadanie_id: int, *typy, limit_s: float = 60.0):
    """Pierwsze zdarzenie zadania o jednym z ``typy`` (None po limicie czasu)."""
    odb.czekaj(lambda: any(z.zadanie_id == zadanie_id and z.typ in typy for z in odb.wszystkie), limit_s)
    return next((z for z in list(odb.wszystkie) if z.zadanie_id == zadanie_id and z.typ in typy), None)


@WINDOWS
def test_n1_plik_trzymany_wylacznie_w_trakcie_analizy_wynik_zostaje(tmp_path, silnik_probny):
    """N1, proba K1 recenzenta: inny program (kopia zapasowa, podglad w programie skanera, antywirus) trzyma plik skanu bez
    zgody na odczyt pod koniec analizy, tresc bez zmian. Wynik zostaje (przed poprawka: ``plik_zmieniony`` z komunikatem
    "nowa tresc ma wlasne zdarzenie", choc zadnego zdarzenia nie bylo - skan przepadal)."""
    import symulator_skanera as SY

    s, odb = silnik_probny()
    p = tmp_path / "skany" / "skan.stl"
    p.parent.mkdir()
    dane = b"SPIJ 2 " + b"x" * 1000
    p.write_bytes(dane)
    nr = s.zlec(_zadanie(p, skan_sha16=_skrot(dane)))
    assert _czekaj_na(odb, nr, "postep") is not None
    uchwyt = SY.otworz_wylacznie(p, zapis=False)
    try:
        z = odb.czekaj_na_koncowe(1, 60.0)[0]
    finally:
        uchwyt.close()
    assert (z.typ, z.rodzaj) == ("wynik", ""), z.blad
    assert z.wynik["skan_sha16"] == _skrot(dane) and z.wynik["bajtow"] == len(dane) and z.wynik["skan"] == "skan.stl"
    assert os.path.normcase(z.wynik["sciezka"]) != os.path.normcase(str(p))  # analiza czytala kopie, nie plik programu skanera


def test_n1_plik_przeniesiony_albo_usuniety_w_trakcie_analizy(tmp_path, silnik_probny):
    """N1, proba K2 recenzenta: plik skanu przemianowany (archiwizacja przez program skanera, technik) albo usuniety w trakcie
    analizy - wynik zostaje, ze skrotem tresci ze zdarzenia (przed poprawka: ``plik_zmieniony`` "brak pliku", a zdarzenie
    ``duplikat`` z tym samym ``sha16`` kontrakt kazal odsiac - skan bez wyniku i bez informacji)."""
    s, odb = silnik_probny()
    d = tmp_path / "skany"
    d.mkdir()
    a, b = d / "a.stl", d / "b.stl"
    da, db = b"SPIJ 1.5 przeniesiony", b"SPIJ 1.5 usuniety"
    a.write_bytes(da)
    b.write_bytes(db)
    ids = [s.zlec(_zadanie(a, skan_sha16=_skrot(da))), s.zlec(_zadanie(b, skan_sha16=_skrot(db)))]
    assert _czekaj_na(odb, ids[0], "postep") is not None
    a.rename(d / "a_archiwum.stl")
    assert _czekaj_na(odb, ids[1], "postep", "blad", "wynik").typ == "postep"
    b.unlink()
    koncowe = odb.czekaj_na_koncowe(2, 60.0)
    assert [(z.zadanie_id, z.typ, z.rodzaj) for z in koncowe] == [(ids[0], "wynik", ""), (ids[1], "wynik", "")], [z.blad for z in koncowe]
    assert [z.wynik["skan_sha16"] for z in koncowe] == [_skrot(da), _skrot(db)] and [z.wynik["skan"] for z in koncowe] == ["a.stl", "b.stl"]


@WINDOWS
def test_n1_plik_zajety_przed_analiza_czeka_i_daje_wynik(tmp_path, silnik_probny):
    """N1: plik skanu trzymany bez zgody na odczyt, gdy przychodzi kolej jego zadania. Proces roboczy ponawia kopiowanie
    z rosnacym odstepem (jak scanner B1), zglasza postep "oczekiwanie na zwolnienie pliku skanu" i po zwolnieniu daje
    wynik (przed poprawka: od razu blad ``analiza`` PermissionError ze skrotu)."""
    import symulator_skanera as SY

    s, odb = silnik_probny()
    d = tmp_path / "skany"
    d.mkdir()
    wolny, x = d / "wolny.stl", d / "x.stl"
    wolny.write_bytes(b"SPIJ 0.5")
    dane = b"plytka trzymana przez inny program " * 40
    x.write_bytes(dane)
    uchwyt = SY.otworz_wylacznie(x, zapis=False)
    try:
        a, b = s.zlec(_zadanie(wolny)), s.zlec(_zadanie(x, skan_sha16=_skrot(dane)))
        pierwsze = _czekaj_na(odb, b, "postep", "blad", "wynik")
        assert pierwsze is not None and pierwsze.typ == "postep" and "oczekiwanie" in pierwsze.etap, pierwsze
        time.sleep(1.5)
        assert not [z for z in odb.koncowe() if z.zadanie_id == b]  # czeka, nie odrzuca
    finally:
        uchwyt.close()
    koncowe = odb.czekaj_na_koncowe(2, 60.0)
    assert [(z.zadanie_id, z.typ, z.rodzaj) for z in koncowe] == [(a, "wynik", ""), (b, "wynik", "")], [z.blad for z in koncowe]
    assert koncowe[1].wynik["skan_sha16"] == _skrot(dane) and koncowe[1].czas_s >= 1.5
    etapy = [z.etap for z in odb.wszystkie if z.typ == "postep" and z.zadanie_id == b]
    assert "oczekiwanie" in etapy[0] and etapy[-2:] == ["proba: start", "proba: koniec"]


@WINDOWS
def test_n1_plik_zajety_dluzej_niz_limit_osobny_rodzaj_bledu(tmp_path, silnik_probny):
    """N1: plik skanu trzymany bez zgody na odczyt dluzej niz ``czekaj_na_plik_s`` - blad rodzaju ``plik_niedostepny``
    z prawdziwym komunikatem (nazwa pliku, powod systemu), nie ``plik_zmieniony``; nastepne zadanie jest wykonane."""
    import symulator_skanera as SY

    s, odb = silnik_probny(czekaj_na_plik_s=1.0)
    d = tmp_path / "skany"
    d.mkdir()
    x, y = d / "x.stl", d / "y.stl"
    x.write_bytes(b"plytka zajeta")
    y.write_bytes(b"dobry")
    uchwyt = SY.otworz_wylacznie(x, zapis=False)
    try:
        a, b = s.zlec(_zadanie(x, skan_sha16=_skrot(b"plytka zajeta"))), s.zlec(_zadanie(y))
        koncowe = odb.czekaj_na_koncowe(2, 60.0)
    finally:
        uchwyt.close()
    assert [(z.zadanie_id, z.typ, z.rodzaj) for z in koncowe] == [(a, "blad", "plik_niedostepny"), (b, "wynik", "")], [z.blad for z in koncowe]
    assert "x.stl" in koncowe[0].blad and "nie da sie odczytac" in koncowe[0].blad and "WinError 32" in koncowe[0].blad, koncowe[0].blad
    assert koncowe[0].wynik is None and 1.0 <= koncowe[0].czas_s < 30.0


def test_n1_kopia_robocza_jedna_naraz_i_sprzatanie(tmp_path, silnik_probny):
    """N1 / D-N6: analiza czyta kopie w ``katalog_roboczy`` - w trakcie analizy jest tam jedna kopia (ta sama nazwa pliku,
    folder ``<pid procesu roboczego>_<zadanie_id>``), po zadaniu zadna. Kopie po procesie, ktorego juz nie ma (zabity w
    trakcie zadania), sa usuwane przy starcie procesu roboczego; kopie zyjacego procesu (inny silnik) zostaja."""
    rob = tmp_path / "robocze"
    martwy = _pid_martwego_procesu()
    (rob / f"{martwy}_7").mkdir(parents=True)
    (rob / f"{martwy}_7" / "stary.stl").write_bytes(b"x" * 100)
    zywy = rob / f"{os.getpid()}_1"
    zywy.mkdir()
    (zywy / "cudzy.stl").write_bytes(b"z")
    s, odb = silnik_probny(katalog_roboczy=rob)
    p = tmp_path / "skany" / "skan.stl"
    p.parent.mkdir()
    p.write_bytes(b"SPIJ 1.0 kopia")
    nr = s.zlec(_zadanie(p))
    assert _czekaj_na(odb, nr, "postep") is not None
    w_trakcie = sorted(x.relative_to(rob).as_posix() for x in rob.rglob("*") if x.is_file())
    z = odb.czekaj_na_koncowe(1, 60.0)[0]
    assert z.typ == "wynik", z.blad
    po = sorted(x.relative_to(rob).as_posix() for x in rob.rglob("*"))
    assert w_trakcie == sorted([f"{os.getpid()}_1/cudzy.stl", f"{z.wynik['pid']}_{nr}/skan.stl"])
    assert os.path.normcase(z.wynik["sciezka"]) == os.path.normcase(str(rob / f"{z.wynik['pid']}_{nr}" / "skan.stl"))
    assert po == [f"{os.getpid()}_1", f"{os.getpid()}_1/cudzy.stl"]


def test_n2_slowa_ze_slownika_wyniku_w_puli_nie_zmieniaja_decyzji(tmp_path, silnik_probny):
    """N2, proba K3 recenzenta: w puli foldery ``OK``, ``ok``, ``Waxup``, ``sprawdz``, ``zielony`` i plik ``korona.stl``
    (laboratoria tak nazywaja foldery prac). Statusy, typy, kolory i identyfikatory w wyniku silnika sa identyczne z wynikiem
    funkcji analizy PRZED czyszczeniem (przed poprawka: ``inspekcja.status`` ``ok`` -> ``<projekt>``, typ ``waxup`` /
    ``korona`` -> ``<projekt ...>``); nazwy z puli w tekstach wolnych nadal usuniete (fikcyjne nazwisko 0 razy)."""
    from stanowisko import silnik as SI

    s, odb = silnik_probny()
    pula = tmp_path / "pula"
    for f in ("OK", "Waxup", "sprawdz", "zielony", "Zlecenie 7/ok", "Fikcyjna Testowa 4321"):
        (pula / f).mkdir(parents=True)
    (pula / "Zlecenie 7" / "korona.stl").write_bytes(b"korona smiec")
    (pula / "Fikcyjna Testowa 4321" / "FikcyjnaTestowa-11-crown_cad.stl").write_bytes(b"smiec")
    skan = tmp_path / "skany" / "skan.stl"
    skan.parent.mkdir()
    skan.write_bytes(b"SLOWNIK")
    s.zlec(SI.ZadanieAnalizy(skan=skan, pula=SI.OpisPuli(foldery=(str(pula),))))
    z = odb.czekaj_na_koncowe(1, 60.0)[0]
    assert z.typ == "wynik", (z.rodzaj, z.blad, z.szczegoly)
    w = z.wynik
    assert bez_tekstow({k: v for k, v in w.items() if k not in ("zadanie_id", "skan_sha16")}) == bez_tekstow(wynik_ze_slownikiem("skan.stl"))
    g = w["gniazda"]
    assert [x["inspekcja"] and x["inspekcja"]["status"] for x in g] == ["ok", "sprawdz", None]
    assert [x["kandydaci"][0]["typ"] for x in g] == ["waxup", "korona", "most"] and [x["status_gniazda"] for x in g] == ["zielony", "zolty", "szary"]
    assert sorted(w["ostrzezenia"]) == sorted(f"pomijam projekt <projekt {_skrot(t)}>: brak trojkatow" for t in (b"korona smiec", b"smiec"))
    assert w["uklad_komunikat"] == "folder <projekt>" and g[1]["inspekcja"]["blad"] == f"ValueError: <projekt {_skrot(b'smiec')}>"
    for tekst in [repr(x) for x in odb.wszystkie]:
        assert _bez_nazwiska(tekst), tekst[:500]


def test_n2_czysciciel_zmienia_tylko_teksty_wolne_i_cale_nazwy(tmp_path):
    """N2: ``oczysc`` zmienia tylko pola z tekstem wolnym (ostrzezenia, uwagi, blad, powod, komunikaty); statusy, typy,
    identyfikatory, nazwa skanu i liczby zostaja nawet wtedy, gdy rowne sa nazwie z puli. W tekstach zamieniane sa tylko
    cale nazwy (granice slowa i separatory), najdluzsza najpierw."""
    from stanowisko import silnik as SI

    pula = tmp_path / "pula"
    for f in ("OK", "Jan", "Jan Nowak", "Nowak"):
        (pula / f).mkdir(parents=True)
    (pula / "Jan Nowak" / "korona.stl").write_bytes(b"k")
    cz = SI.CzyscicielNazw([str(pula)])
    znacznik = f"<projekt {_skrot(b'k')}>"
    wynik = {"status": "ok", "typ": "korona", "id": "Nowak", "skan": "korona.stl", "liczba": 3, "uklad_zgodny": True,
             "inspekcja": {"status": "OK", "projekt": "Jan", "uwagi": ["ok: korona.stl"]},
             "ostrzezenia": ["Jan Nowak; Nowakowski; Jan-Nowak; plik korona.stl.bak; Nowak."], "uklad_komunikat": "folder OK",
             "skala": {"powod": "Jan Nowak", "zastosowana": False}, "gniazda": [{"status_gniazda": "zielony", "uwagi": ["zob. Jan"]}]}
    c = cz.oczysc(wynik)
    assert {k: c[k] for k in ("status", "typ", "id", "skan", "liczba", "uklad_zgodny")} == {"status": "ok", "typ": "korona", "id": "Nowak",
                                                                                            "skan": "korona.stl", "liczba": 3, "uklad_zgodny": True}
    assert c["inspekcja"] == {"status": "OK", "projekt": "Jan", "uwagi": [f"<projekt>: {znacznik}"]}
    assert c["ostrzezenia"] == ["<projekt>; Nowakowski; Jan-Nowak; plik korona.stl.bak; <projekt>."]
    assert c["uklad_komunikat"] == "folder <projekt>" and c["skala"] == {"powod": "<projekt>", "zastosowana": False}
    assert c["gniazda"] == [{"status_gniazda": "zielony", "uwagi": ["zob. <projekt>"]}]
    assert wynik["status"] == "ok" and wynik["ostrzezenia"][0].startswith("Jan Nowak")  # oryginal bez zmian (kopia)


class OdbiorBlokujacy(Odbior):
    """Odbior, ktory zatrzymuje watek nadzorcy na pierwszym zdarzeniu spelniajacym ``warunek`` (jak funkcja ``na_zdarzenie``
    czekajaca na watek okna), az test wywola ``puszczony.set()``. Zdarzenie jest zapisywane dopiero po puszczeniu."""

    def __init__(self, warunek):
        super().__init__()
        self.warunek = warunek
        self.zablokowany = threading.Event()
        self.puszczony = threading.Event()

    def __call__(self, z) -> None:
        if z.typ != "zatrzymany" and not self.zablokowany.is_set() and self.warunek(z):
            self.zablokowany.set()
            self.puszczony.wait(60.0)
        super().__call__(z)


def test_dn3_zadanie_z_listy_stop_nie_dostaje_juz_wyniku(tmp_path):
    """D-N3: ``stop()``, ktory nie doczekal sie konca nadzorcy (``na_zdarzenie`` blokuje sie w trakcie przekazywania wyniku),
    nie zwraca jako niezakonczonego zadania, ktorego wynik jest wlasnie przekazywany. Kazde zadanie albo dostaje jedno
    zdarzenie koncowe, albo jest na liscie ``stop()`` - nigdy oba (przed poprawka: na liscie i z wynikiem = po restarcie
    programu analiza drugi raz)."""
    from stanowisko import silnik as SI

    odb = OdbiorBlokujacy(lambda z: z.typ == "wynik")
    s = SI.Silnik(ust={}, funkcja=FUNKCJA_PROBNA, na_zdarzenie=odb)
    s.start()
    a, b = tmp_path / "a.stl", tmp_path / "b.stl"
    a.write_bytes(b"dobry a")
    b.write_bytes(b"dobry b")
    try:
        ida, idb = s.zlec(_zadanie(a)), s.zlec(_zadanie(b))
        assert odb.zablokowany.wait(60.0)  # nadzorca stoi w przekazywaniu wyniku zadania a
        t0 = time.time()
        niezakonczone = s.stop(czekaj_s=0.5)
        assert time.time() - t0 < 15.0
    finally:
        odb.puszczony.set()
    time.sleep(1.5)  # nadzorca konczy przekazywanie
    lista, koncowe = [z.zadanie_id for z in niezakonczone], [(z.zadanie_id, z.typ) for z in odb.koncowe()]
    assert koncowe == [(ida, "wynik")] and lista == [idb], (koncowe, lista)
    assert [z.zadanie_id for z in odb.typu("zatrzymany")[0].niezakonczone] == [idb]


def test_dn4_zlec_w_trakcie_stop_odmawia_a_zadanie_trafia_na_liste(tmp_path):
    """D-N4: ``zlec`` w trakcie ``stop()`` (np. ``zlec_skan`` z watku obserwatora, gdy okno juz zatrzymuje silnik) odmawia
    wyjatkiem ``SilnikZatrzymany`` (podklasa RuntimeError), a zadanie trafia na liste niezakonczonych, ktora zwraca ``stop()``
    (``na_liscie`` True). Po zebraniu listy - odmowa z ``na_liscie`` False. Zadne z tych zadan nie rusza."""
    from stanowisko import silnik as SI

    odb = OdbiorBlokujacy(lambda z: z.typ == "postep")
    s = SI.Silnik(ust={}, funkcja=FUNKCJA_PROBNA, na_zdarzenie=odb)
    s.start()
    a, b = tmp_path / "a.stl", tmp_path / "b.stl"
    a.write_bytes(b"dobry a")
    b.write_bytes(b"dobry b")
    wynik_stop = []
    try:
        ida = s.zlec(_zadanie(a))
        assert odb.zablokowany.wait(60.0)  # nadzorca stoi na postepie zadania a
        w = threading.Thread(target=lambda: wynik_stop.append(s.stop(czekaj_s=2.0)))
        w.start()
        time.sleep(0.5)  # stop() czeka na nadzorce
        with pytest.raises(SI.SilnikZatrzymany) as e:
            s.zlec(_zadanie(b, numer=5))
        assert isinstance(e.value, RuntimeError) and e.value.na_liscie is True and Path(e.value.zadanie.skan) == b
        w.join(30.0)
    finally:
        odb.puszczony.set()
    time.sleep(1.0)
    lista = wynik_stop[0]
    assert [(Path(z.skan).name, z.numer) for z in lista] == [("a.stl", None), ("b.stl", 5)] and lista[0].zadanie_id == ida
    assert list(odb.typu("zatrzymany")[0].niezakonczone) == lista and odb.koncowe() == []
    with pytest.raises(SI.SilnikZatrzymany) as e2:
        s.zlec(_zadanie(b))
    assert e2.value.na_liscie is False


def test_stop_zwraca_zadania_niezakonczone(tmp_path, silnik_probny):
    """P2 (b), proba ``s3`` recenzenta: ``stop()`` przy 1 zadaniu w toku i 3 w kolejce zwraca te 4 zadania (w toku pierwsze)
    i zglasza je zdarzeniem ``zatrzymany`` - aplikacja moze je zapisac i zlecic ponownie po starcie."""
    s, odb = silnik_probny()
    wolny, szybki = tmp_path / "wolny.stl", tmp_path / "szybki.stl"
    wolny.write_bytes(b"SPIJ 30")
    szybki.write_bytes(b"dobry")
    ids = [s.zlec(_zadanie(wolny, skan_sha16=_skrot(b"SPIJ 30")))] + [s.zlec(_zadanie(szybki, numer=i)) for i in range(3)]
    assert odb.czekaj(lambda: any(z.typ == "postep" and z.zadanie_id == ids[0] for z in odb.wszystkie), 60.0)
    t0 = time.time()
    niezakonczone = s.stop()
    assert time.time() - t0 < 10.0
    assert [z.zadanie_id for z in niezakonczone] == ids and [z.numer for z in niezakonczone[1:]] == [0, 1, 2]
    assert Path(niezakonczone[0].skan) == wolny and niezakonczone[0].skan_sha16 == _skrot(b"SPIJ 30")
    ostatnie = odb.wszystkie[-1]
    assert ostatnie.typ == "zatrzymany" and [z.zadanie_id for z in ostatnie.niezakonczone] == ids
    assert odb.koncowe() == []  # zadne z tych zadan nie dostalo wyniku ani bledu - nie sa "zakonczone"
    assert s.stop() == []  # drugie wywolanie niczego nie zwraca ani nie zglasza
    assert len(odb.typu("zatrzymany")) == 1


def test_stop_bez_zadan_zwraca_pusta_liste(tmp_path, silnik_probny):
    s, odb = silnik_probny()
    p = tmp_path / "a.stl"
    p.write_bytes(b"dobry")
    s.zlec(_zadanie(p))
    odb.czekaj_na_koncowe(1)
    assert s.czekaj_na_pusta_kolejke(10.0) is True
    assert s.stop() == [] and odb.wszystkie[-1].typ == "zatrzymany" and odb.wszystkie[-1].niezakonczone == ()


def test_wyjscie_unikalne_nazwy_na_zadanie(tmp_path, silnik_probny):
    """P4, proba ``s2`` recenzenta: ``zlec1\\scan.stl`` i ``zlec2\\scan.stl`` oraz ten sam skan zlecony ponownie daja osobne
    pliki ``<czas przyjecia>_<sha16>[_n]_wynik.json`` (D-N6: bez nazwy skanu, jak w A1); zdarzenie kazdego zadania wskazuje
    SWOJ plik; nic nie jest nadpisywane; po zapisie nie zostaja pliki tymczasowe."""
    s, odb = silnik_probny()
    wyj = tmp_path / "wyniki"
    p1, p2 = tmp_path / "zlec1" / "scan.stl", tmp_path / "zlec2" / "scan.stl"
    for p, tresc in ((p1, b"plytka pierwsza"), (p2, b"plytka druga, inna")):
        p.parent.mkdir()
        p.write_bytes(tresc)
    ids = [s.zlec(_zadanie(p, wyjscie=wyj)) for p in (p1, p2, p1, p1)]
    koncowe = odb.czekaj_na_koncowe(4, 60.0)
    assert [(z.zadanie_id, z.typ) for z in koncowe] == [(i, "wynik") for i in ids]
    pliki = [Path(z.pliki["wynik"]) for z in koncowe]
    assert len(set(pliki)) == 4 and all(p.is_file() and p.parent == wyj for p in pliki)
    for z, p in zip(koncowe, pliki):
        d = json.loads(p.read_text(encoding="utf-8"))
        assert d == z.wynik and d["zadanie_id"] == z.zadanie_id  # plik = wynik TEGO zadania
        m = re.fullmatch(r"(\d{8}_\d{6})_([0-9a-f]{16})(_\d+)?_wynik\.json", p.name)
        assert m and m.group(2) == z.wynik["skan_sha16"], p.name
        assert abs(time.mktime(time.strptime(m.group(1), "%Y%m%d_%H%M%S")) - time.time()) < 600
    assert [z.wynik["skan_sha16"] for z in koncowe] == [_skrot(b"plytka pierwsza"), _skrot(b"plytka druga, inna")] + [_skrot(b"plytka pierwsza")] * 2
    assert sorted(x.name for x in wyj.iterdir()) == sorted(p.name for p in pliki)


def test_dn6_nazwy_plikow_wyjscia_bez_nazwy_skanu_i_sprzatanie_tmp(tmp_path, silnik_probny):
    """D-N6: program skanera moze nazywac eksport nazwiskiem ze zlecenia - nazwy plikow w ``wyjscie`` nie zawieraja nazwy
    skanu (``<czas przyjecia>_<sha16>[_n]_wynik.json``, jak w A1). Pliki tymczasowe zapisu po procesie, ktorego juz nie ma
    (zabity w trakcie zapisu), sa usuwane przy kolejnym zapisie do tego folderu; plik zyjacego procesu zostaje."""
    wyj = tmp_path / "wyniki"
    wyj.mkdir()
    martwy = _pid_martwego_procesu()
    stary = wyj / f"20261117_120000_0123456789abcdef_wynik.json.{martwy}.tmp"
    cudzy = wyj / f"20261117_120000_0123456789abcdef_wynik.json.{os.getpid()}.tmp"
    stary.write_bytes(b"{")
    cudzy.write_bytes(b"{")
    s, odb = silnik_probny()
    p = tmp_path / "zlec" / "Fikcyjna_Testowa_plytka.stl"
    p.parent.mkdir()
    p.write_bytes(b"dobry skan z nazwiskiem w nazwie pliku")
    s.zlec(_zadanie(p, wyjscie=wyj))
    z = odb.czekaj_na_koncowe(1, 60.0)[0]
    assert z.typ == "wynik", z.blad
    nazwa = Path(z.pliki["wynik"]).name
    assert re.fullmatch(rf"\d{{8}}_\d{{6}}_{z.wynik['skan_sha16']}(_\d+)?_wynik\.json", nazwa), nazwa
    assert sorted(x.name for x in wyj.iterdir()) == sorted([nazwa, cudzy.name])  # stary plik tymczasowy usuniety, cudzy zostal
    assert all(_bez_nazwiska(x.name) for x in wyj.iterdir())


def test_straznik_procesu_roboczego():
    """P6: straznik w procesie roboczym konczy proces, gdy zniknie proces okna albo gdy zadanie przekroczy wlasny limit
    czasu (limit nadzorcy + zapas - nadzorca moze juz nie zyc)."""
    from stanowisko import silnik as SI

    konce, rodzic, t = [], [True], [100.0]
    st = SI.Straznik(rodzic_zyje=lambda: rodzic[0], limit_zadania_s=10.0, zakoncz=konce.append, zegar=lambda: t[0])
    st.sprawdz()
    st.poczatek_zadania()
    t[0] += 10.0 + SI.ZAPAS_LIMITU_S - 0.5
    st.sprawdz()
    assert konce == []
    st.koniec_zadania()
    t[0] += 1000.0
    st.sprawdz()
    assert konce == []  # miedzy zadaniami limit nie biegnie
    st.poczatek_zadania()
    t[0] += 10.0 + SI.ZAPAS_LIMITU_S + 0.5
    st.sprawdz()
    assert konce == [SI.KOD_LIMIT_ZADANIA]
    st.koniec_zadania()
    rodzic[0] = False
    st.sprawdz()
    assert konce == [SI.KOD_LIMIT_ZADANIA, SI.KOD_BEZ_PROCESU_OKNA]


KOD_PROCESU_OKNA = """
import sys, time
from pathlib import Path
from stanowisko import silnik as SI

if __name__ == "__main__":
    p = Path(sys.argv[1])
    s = SI.Silnik(ust={}, funkcja="test_silnik:analiza_probna")
    s.start()
    s.zlec(SI.ZadanieAnalizy(skan=p, pula=SI.OpisPuli(foldery=(str(p.parent),))))
    while True:
        z = s.zdarzenia.get(timeout=120)
        if z.typ == "postep":
            print(s.pid, flush=True)
            break
    time.sleep(300)
"""


def test_proces_roboczy_konczy_sie_po_smierci_procesu_okna(tmp_path):
    """P6, proba ``eksp3`` recenzenta: proces okna zabity twardo W TRAKCIE analizy (zadanie probne 60 s) - procesu roboczego
    nie ma najpozniej po 10 s (przed poprawka liczyl do konca zadania)."""
    _zabij_okno_w_trakcie_analizy(tmp_path, b"SPIJ 60", "P6")


@WINDOWS
def test_dn5_proces_roboczy_ginie_z_oknem_takze_w_kodzie_natywnym_z_gil(tmp_path):
    """D-N5, proba ``eks_gil`` recenzenta: analiza stoi w wywolaniu natywnym, ktore trzyma GIL (jak ``segment_plane`` /
    ``estimate_normals`` w Open3D; tu ``Sleep`` przez ``ctypes.PyDLL``), wiec watek ``Straznik`` nie dostaje czasu. Proces
    roboczy konczy wtedy system: jest w obiekcie zadania Windows (Job Object) procesu okna z ``KILL_ON_JOB_CLOSE``. Procesu
    roboczego nie ma najpozniej 10 s po zabiciu okna (przed poprawka: zyl do konca wywolania - tu 60 s)."""
    _zabij_okno_w_trakcie_analizy(tmp_path, b"GIL 60", "D-N5")


def test_dn5_bez_obiektu_zadania_silnik_dziala_jak_dotad(tmp_path, silnik_probny, monkeypatch):
    """D-N5: proces roboczy jest w obiekcie zadania (Windows) - ``stan()["obiekt_zadania"]``. Gdy obiektu zadania nie da sie
    utworzyc ani przypisac (inny system, zasady komputera), silnik dziala jak dotad (zostaje ``Straznik``)."""
    from stanowisko import silnik as SI

    p = tmp_path / "a.stl"
    p.write_bytes(b"dobry")
    s, odb = silnik_probny()
    s.zlec(_zadanie(p))
    assert odb.czekaj_na_koncowe(1)[0].typ == "wynik"
    assert s.stan()["obiekt_zadania"] is (os.name == "nt")

    def odmowa(pid):
        raise OSError("odmowa dostepu (proba)")

    monkeypatch.setattr(SI, "_dolacz_do_obiektu_zadania", odmowa)
    s2, odb2 = silnik_probny()
    s2.zlec(_zadanie(p))
    z = odb2.czekaj_na_koncowe(1)[0]
    assert z.typ == "wynik" and s2.stan()["obiekt_zadania"] is False


def _zabij_okno_w_trakcie_analizy(tmp_path, tresc: bytes, opis: str) -> None:
    """Proces okna (osobny proces z silnikiem) zabity twardo w trakcie analizy pliku o tresci ``tresc``; proces roboczy
    musi zniknac najpozniej 10 s pozniej."""
    p = tmp_path / "wolny.stl"
    p.write_bytes(tresc)
    env = {**os.environ, "PYTHONPATH": os.pathsep.join(sys.path)}
    with open(tmp_path / "okno.log", "wb") as log:
        okno = subprocess.Popen([sys.executable, "-c", KOD_PROCESU_OKNA, str(p)], cwd=str(STANOWISKO), stdout=subprocess.PIPE, stderr=log, text=True, env=env)
    pid = None
    try:
        wiersz = okno.stdout.readline().strip()
        assert wiersz.isdigit(), (tmp_path / "okno.log").read_text(errors="replace")[-2000:]
        pid = int(wiersz)
        assert _proces_zyje(pid) and pid != okno.pid
        okno.kill()  # jak Menedzer zadan: bez sprzatania
        okno.wait(10)
        t0 = time.time()
        while _proces_zyje(pid) and time.time() - t0 < 20:
            time.sleep(0.1)
        czas = time.time() - t0
        print(f"\n[{opis}] proces roboczy zniknal {czas:.1f} s po zabiciu procesu okna (wymagane <= 10 s)")
        assert not _proces_zyje(pid) and czas <= 10.0
    finally:
        if okno.poll() is None:
            okno.kill()
        if pid is not None and _proces_zyje(pid):
            os.kill(pid, signal.SIGTERM)


PLIK_STARTOWY = """
import sys
from pathlib import Path

from stanowisko import silnik as SI
{import_qt_na_gorze}


def main():
    import PySide6.QtCore  # noqa: F401 - jak w aplikacji: Qt importowane w main(), przed pierwszym uzyciem silnika
    p = Path(sys.argv[1])
    with SI.Silnik(ust={{}}, funkcja="test_silnik:analiza_probna") as s:
        s.zlec(SI.ZadanieAnalizy(skan=p, pula=SI.OpisPuli(foldery=(str(p.parent),))))
        while True:
            z = s.zdarzenia.get(timeout=120)
            if z.typ in ("wynik", "blad"):
                break
    print("QT_W_PROCESIE_ROBOCZYM", z.wynik["qt"] if z.wynik else z.blad, flush=True)


if __name__ == "__main__":
    main()
"""


@pytest.mark.parametrize("qt_na_gorze", [False, True])
def test_qt_w_procesie_roboczym_zalezy_od_pliku_startowego(tmp_path, qt_na_gorze):
    """D8: proces roboczy (spawn) wykonuje ponownie plik startowy programu jako ``__mp_main__``. Plik startowy z importem
    Qt w ``main()`` (zalecenie dla A3) -> w procesie roboczym nie ma PySide6; import Qt na poziomie modulu -> jest (tego
    ukladu A3 ma unikac: Qt obok Open3D w procesie liczacym)."""
    p = tmp_path / "skan.stl"
    p.write_bytes(b"dobry")
    start = tmp_path / "start_programu.py"
    start.write_text(PLIK_STARTOWY.format(import_qt_na_gorze="import PySide6.QtCore  # noqa" if qt_na_gorze else ""), encoding="utf-8")
    env = {**os.environ, "PYTHONPATH": os.pathsep.join(sys.path), "QT_QPA_PLATFORM": "offscreen"}
    w = subprocess.run([sys.executable, str(start), str(p)], cwd=str(STANOWISKO), capture_output=True, text=True, env=env, timeout=300)
    assert w.returncode == 0, w.stdout[-2000:] + w.stderr[-2000:]
    assert f"QT_W_PROCESIE_ROBOCZYM {qt_na_gorze}" in w.stdout, w.stdout[-2000:] + w.stderr[-2000:]


def test_pamiec_pul(tmp_path, monkeypatch):
    """Pula budowana raz na (foldery, wspolczynnik, zawartosc folderow); zmiana plikow w folderze = nowa pula; limit liczby pul."""
    from stanowisko import match as M, silnik as SI

    zbudowane = []

    class PulaAtrapa:
        def __init__(self, foldery, wspolczynnik, orientacja="auto", wspolczynniki=None):
            zbudowane.append((tuple(str(f) for f in foldery), wspolczynnik, orientacja, wspolczynniki))
            self.wspolczynnik = wspolczynnik

    monkeypatch.setattr(M, "Pula", PulaAtrapa)
    folder = tmp_path / "projekty"
    folder.mkdir()
    (folder / "a.stl").write_bytes(b"1")
    pamiec = SI.PamiecPul(limit=2)
    opis = SI.OpisPuli(foldery=(str(folder),))
    p1 = pamiec.dla(opis)(1.225)
    assert pamiec.dla(opis)(1.225) is p1 and len(zbudowane) == 1  # drugi skan tego samego wieczoru: ta sama pula
    p2 = pamiec.dla(opis)(1.0)
    assert p2 is not p1 and len(zbudowane) == 2
    (folder / "b.stl").write_bytes(b"22")  # nowy projekt w folderze: pula budowana od nowa
    p3 = pamiec.dla(opis)(1.225)
    assert p3 is not p1 and len(zbudowane) == 3 and len(pamiec) == 2
    assert pamiec.dla(SI.OpisPuli(foldery=(str(folder),), wspolczynniki={"abc": 1.21}))(1.225) is not p3
    assert zbudowane[-1][3] == {"abc": 1.21} and len(pamiec) == 2


# ----------------------------------------------------------------------------
# kryterium 4: symulator -> scanner -> silnik, 20 plikow naraz
# ----------------------------------------------------------------------------
def test_20_plikow_naraz_symulator_scanner_silnik(tmp_path, silnik_probny):
    import symulator_skanera as SY
    from stanowisko import scanner as SC, silnik as SI

    s, odb = silnik_probny()
    folder = tmp_path / "eksport"
    folder.mkdir()
    pula = SI.OpisPuli(foldery=(str(tmp_path),))
    zdarzenia = []

    def na_skan(z):
        zdarzenia.append(z)
        s.zlec_skan(z, pula)

    sc = SC.Scanner(folder, na_skan=na_skan, stabilizacja_ms=150, okres_s=0.03)
    sc.start()
    try:
        kolejnosc = [(3 * i + 5) % 20 for i in range(20)]
        czasy = [0.0] * 20
        for miejsce, nr in enumerate(kolejnosc):
            czasy[nr] = 0.6 + 0.3 * miejsce
        zapisy = SY.symuluj(folder, [SY.sztuczny_stl(200 + i, seed=i) for i in range(20)], ile=20, czasy=czasy, kawalki=(5, 5), rownolegle=20, seed=1)
        koncowe = odb.czekaj_na_koncowe(20, 120.0)
    finally:
        sc.stop()
    assert [z.typ for z in koncowe] == ["wynik"] * 20 and len(zdarzenia) == 20  # zadnego zgubionego, zadnej awarii
    assert sorted(z.wynik["skan"] for z in koncowe) == sorted(Path(z["plik"]).name for z in zapisy)
    # analiza w kolejnosci zdarzen, a zdarzenia w kolejnosci czasu zapisu plikow (bez zakladania, w jakiej kolejnosci symulator
    # skonczyl zapisy - to zalezy od obciazenia komputera, uwaga D9 recenzji; luz 0,1 s = dwa obiegi obserwatora)
    assert [z.wynik["skan"] for z in koncowe] == [Path(z.plik).name for z in zdarzenia]
    czasy_plikow = [z.mtime_ns / 1e9 for z in zdarzenia]
    assert all(a <= b + 0.1 for a, b in zip(czasy_plikow, czasy_plikow[1:])), czasy_plikow
    assert [z.wynik["skan_sha16"] for z in koncowe] == [z.sha16 for z in zdarzenia]
    wyniki = [z.wynik for z in koncowe]
    assert all(a["koniec"] <= b["start"] for a, b in zip(wyniki, wyniki[1:]))  # po kolei, nie rownolegle
    koniec_zapisu = {Path(z["plik"]).name: z["koniec"] for z in zapisy}
    assert all(w["start"] >= koniec_zapisu[w["skan"]] for w in wyniki)  # zadna analiza przed koncem zapisu pliku


# ----------------------------------------------------------------------------
# prawdziwa analiza: male plytki z atrap (4 typy)
# ----------------------------------------------------------------------------
@pytest.fixture(scope="module")
def plytki(korony, tmp_path_factory):
    """Po jednym sztucznym skanie z 3 atrapami dla kazdego z 4 typow plytek + folder puli: {typ: plik STL}, folder."""
    import shutil
    import warnings

    import numpy as np

    from stanowisko import synth, uklad as U

    d = tmp_path_factory.mktemp("silnik")
    proj = d / "projekty"
    proj.mkdir()
    for i, p in enumerate(korony):
        shutil.copy(p, proj / f"2026-11-17_p{i}-{['11', '14', '36'][i]}-crown_cad.stl")
    pliki = {}
    for i, typ in enumerate(TYPY):
        uk = U.wczytaj(typ)
        w = 1.0 if synth.poranna(typ) else 1.22
        op = synth.Opcje.z_toml(plytka=typ, prace_na_plytce=3, wspolczynnik=(w, w), ubytki_na_prace=(0, 1), srednica_ubytku=(0.8, 1.4), poza_uklad=True, pole=100.0)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            skan, prawda = synth.generuj_plytke(uk, uk.numery[0], synth.pliki_projektow(proj), np.random.default_rng(40 + i), op, 40 + i)
        pliki[typ], _ = synth.zapisz(skan, prawda, d / "skany", f"skan_{typ}")
    return pliki, proj


def _uruchom_cli(zadania: dict, folder_puli: Path, wyjscie: Path) -> dict:
    """``porownaj`` z wiersza polecen, kazdy skan w osobnym procesie, PO KOLEI (wspolny komputer: jeden proces liczacy
    naraz): {klucz: slownik z <skan>_wynik.json}."""
    wyjscie.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "PYTHONUTF8": "1", "PYTHONPATH": os.pathsep.join(sys.path)}
    wyniki = {}
    for klucz, skan in zadania.items():
        with open(wyjscie / f"{klucz}_cli.log", "wb") as log:
            kod = subprocess.run([sys.executable, "-m", "stanowisko.porownaj", "--skan", str(skan), "--projekty", str(folder_puli), "--wyjscie",
                                  str(wyjscie), "--bez-png"], cwd=str(STANOWISKO), stdout=log, stderr=subprocess.STDOUT, env=env, timeout=1800).returncode
        assert kod == 0, (wyjscie / f"{klucz}_cli.log").read_text(encoding="utf-8", errors="replace")[-2000:]
        wyniki[klucz] = json.loads((wyjscie / f"{Path(skan).stem}_wynik.json").read_text(encoding="utf-8"))
    return wyniki


def _uruchom_silnik(zadania: dict, folder_puli: Path, wyjscie: Path | None = None, limit_s: float = 1800.0) -> tuple[dict, list]:
    """Te same skany przez silnik (jeden proces, jedna pula w pamieci): {klucz: wynik}, wszystkie zdarzenia."""
    from stanowisko import silnik as SI

    odb = Odbior()
    with SI.Silnik(na_zdarzenie=odb) as s:
        ids = {s.zlec(SI.ZadanieAnalizy(skan=skan, pula=SI.OpisPuli(foldery=(str(folder_puli),)), wyjscie=wyjscie)): klucz for klucz, skan in zadania.items()}
        koncowe = odb.czekaj_na_koncowe(len(ids), limit_s)
    assert [z.typ for z in koncowe] == ["wynik"] * len(ids), [(z.zadanie_id, z.rodzaj, z.blad, z.szczegoly) for z in koncowe if z.typ == "blad"]
    return {ids[z.zadanie_id]: z.wynik for z in koncowe}, list(odb.wszystkie)


@pytest.fixture(scope="module")
def wyniki_atrap(plytki, tmp_path_factory):
    pliki, proj = plytki
    d = tmp_path_factory.mktemp("wyniki")
    cli = _uruchom_cli(pliki, proj, d / "cli")
    sil, zdarzenia = _uruchom_silnik(pliki, proj, d / "silnik")
    return cli, sil, zdarzenia, d


def _sprawdz_rownosc(typ: str, cli: dict, sil: dict, zrodlo: str = "atrapy", wymagany: int = 2) -> None:
    from stanowisko import silnik as SI

    assert sil["plytka"] == typ == cli["plytka"] and sil["plytka_wybor"] == "auto" and sil["uklad_zgodny"] is True
    assert len(sil["gniazda"]) >= 1
    dodatkowe = {"zadanie_id", "skan_sha16"}
    assert dodatkowe <= set(sil) and set(sil) - dodatkowe == set(cli)  # kontrakt 3.8: slownik porownaj + zadanie_id + skan_sha16
    czysty = SI.CzyscicielNazw(cli["foldery_projektow"]).oczysc(cli)  # P5: silnik oddaje teksty bez nazw z puli - wiersz polecen tak samo
    # N2: czyszczenie zmienia tylko teksty wolne - pola decyzji (statusy, typy, identyfikatory, liczby) silnika porownywane sa
    # z wynikiem wiersza polecen NIECZYSZCZONYM, wiec zamiana psujaca decyzje bylaby tu widoczna
    assert bez_tekstow(czysty) == bez_tekstow(cli), "czyszczenie nazw zmienilo pole decyzji"
    zmienione = len(roznice(czysty, cli))
    print(f"\n[{zrodlo}, {typ}] czyszczenie nazw zmienilo {zmienione} tekstow wolnych wyniku wiersza polecen")
    sil = {k: v for k, v in sil.items() if k not in dodatkowe}
    _rowne(f"kryterium 5, {zrodlo}, {typ}, pola decyzji", bez_czasow(bez_tekstow(sil)), bez_czasow(bez_tekstow(cli)), wymagany)
    _rowne(f"kryterium 5, {zrodlo}, {typ}", bez_czasow(sil), bez_czasow(czysty), wymagany)


def _rowne(opis: str, a, b, wymagany: int = 2) -> None:
    """Porownanie dwoch wynikow na trzech poziomach (patrz ``roznice``); liczba pol roznych na kazdym jest wypisywana.

    1. szum numeryczny (1e-9) - wymagany tylko z E3A2_SCISLE=1: bywa niespelniony takze miedzy dwoma uruchomieniami
       wiersza polecen, wiec w zwyklym zestawie dawalby losowo czerwony test;
    2. miary (liczby do 2e-3, liczniki probek do 2 albo 1 %, bez liczby iteracji) - wymagany w testach na plytkach z atrap;
    3. decyzje: struktura, teksty, statusy, identyfikatory i liczniki decyzji (gniazdo, numer, liczba ubytkow ...) rowne,
       liczby zmiennoprzecinkowe do ``TOL_SKANOW_ODNIESIENIA`` = 0,1 (mm; bezwzglednie - prog posredni z recenzji PR #17:
       ubytek 0,5 mm i 1,5 mm nie moga uchodzic za rowne) - wymagany w wariantach na skanach odniesienia 45-55 MB. Tam inna
       galaz ICP korekty skali zmienia tez miary skwantowane (17.11.2026: ``najdl_przerwa_mm`` 0,0 / 0,05 w 1 z 16 porownan
       silnik - wiersz polecen), a wiersz polecen rozni sie sam od siebie na poziomie 1 w 3 z 3 par przebiegow."""
    poziomy = {1: roznice(a, b), 2: roznice(a, b, tol=TOL_DECYZJI, liczniki_z_tolerancja=True),
               3: roznice(a, b, tol=TOL_SKANOW_ODNIESIENIA, liczniki_z_tolerancja=True, tol_wzgl=0.0)}
    print(f"\n[{opis}] pol roznych: {len(poziomy[1])} przy tolerancji 1e-9, {len(poziomy[2])} na poziomie miar (2e-3, liczniki probek "
          f"z tolerancja), {len(poziomy[3])} na poziomie decyzji (liczby do 0,1); wymagany poziom {1 if SCISLE else wymagany}"
          + "".join(f"\n    {x}" for x in (poziomy[2] + poziomy[1])[:6]))
    r = poziomy[1 if SCISLE else wymagany]
    assert not r, f"pol roznych: {len(r)}\n" + "\n".join(r[:40])


@pytest.mark.parametrize("typ", TYPY)
def test_wynik_silnika_rowny_wierszowi_polecen(wyniki_atrap, typ):
    """Kryterium 5 na malych plytkach z atrap: 4 typy, pole po polu, poza czasami."""
    cli, sil, _, _ = wyniki_atrap
    _sprawdz_rownosc(typ, cli[typ], sil[typ])


def test_postep_i_pliki_wyjscia(wyniki_atrap, plytki):
    from stanowisko import silnik as SI

    cli, sil, zdarzenia, d = wyniki_atrap
    pliki, _ = plytki
    for z in [z for z in zdarzenia if z.typ == "wynik"]:
        etapy = [(p.etap, p.udzial) for p in zdarzenia if p.typ == "postep" and p.zadanie_id == z.zadanie_id]
        assert len(etapy) >= 4 and [u for _, u in etapy] == sorted(u for _, u in etapy) and etapy[-1] == ("wynik", 0.95)
        p_json, p_npz = Path(z.pliki["wynik"]), Path(z.pliki["podglad"])
        rdzen = re.fullmatch(rf"(\d{{8}}_\d{{6}}_{z.wynik['skan_sha16']}(_\d+)?)_wynik\.json", p_json.name)
        assert rdzen and p_npz.name == f"{rdzen.group(1)}_podglad.npz" and p_json.parent == p_npz.parent == d / "silnik"  # wzor nazw jak w A1 (D-N6)
        assert set(z.pliki) == {"wynik", "podglad"}
        assert json.loads(p_json.read_text(encoding="utf-8")) == z.wynik  # plik = slownik ze zdarzenia
        podglad = SI.wczytaj_podglad(p_npz)
        z_inspekcja = {g["gniazdo"] for g in z.wynik["gniazda"] if g["inspekcja"] and g["gniazdo"] is not None}
        assert podglad and set(podglad) <= z_inspekcja
        for gid, (P, odchylki) in podglad.items():
            assert P.ndim == 2 and P.shape[1] == 3 and len(P) == len(odchylki) > 100
    assert len({z.wynik["skan_sha16"] for z in zdarzenia if z.typ == "wynik"}) == 4


def test_awaria_prawdziwej_analizy_i_nastepne_zadanie(plytki, wyniki_atrap, tmp_path):
    """Kryterium 7 na prawdziwym ``porownaj``: zabity proces w trakcie analizy, plik-smiec, potem poprawna plytka z tym samym wynikiem."""
    from stanowisko import silnik as SI

    pliki, proj = plytki
    _, sil, _, _ = wyniki_atrap
    smiec = tmp_path / "smiec.stl"
    smiec.write_bytes(os.urandom(5000))
    pula = SI.OpisPuli(foldery=(str(proj),))
    odb = Odbior()
    with SI.Silnik(na_zdarzenie=odb) as s:
        a = s.zlec(SI.ZadanieAnalizy(skan=pliki["wieczorna"], pula=pula))
        b = s.zlec(SI.ZadanieAnalizy(skan=smiec, pula=pula))
        c = s.zlec(SI.ZadanieAnalizy(skan=pliki["okragla_poranna"], pula=pula))
        assert odb.czekaj(lambda: any(z.typ == "postep" and z.zadanie_id == a for z in odb.wszystkie), 300.0)
        os.kill(s.pid, signal.SIGTERM)
        koncowe = odb.czekaj_na_koncowe(3, 600.0)
    assert [(z.zadanie_id, z.typ, z.rodzaj) for z in koncowe] == [(a, "blad", "proces"), (b, "blad", "analiza"), (c, "wynik", "")]
    assert koncowe[1].blad and koncowe[0].blad
    # nowy proces po awarii daje ten sam wynik, co pierwszy
    _rowne("kryterium 7, wynik po restarcie procesu", bez_czasow(koncowe[2].wynik), bez_czasow({**sil["okragla_poranna"], "zadanie_id": c}))


def test_brak_projektow_w_puli_to_blad_a_nie_koniec_procesu(plytki, tmp_path):
    """``porownaj`` konczy sie ``SystemExit`` przy pustej puli - w silniku to zwykly blad zadania, proces pracuje dalej."""
    from stanowisko import silnik as SI, uklad as U

    pliki, proj = plytki
    pusty = tmp_path / "pusta_pula"
    pusty.mkdir()
    nr = U.wczytaj("poranna").numery[0]
    odb = Odbior()
    with SI.Silnik(na_zdarzenie=odb) as s:
        a = s.zlec(SI.ZadanieAnalizy(skan=pliki["poranna"], pula=SI.OpisPuli(foldery=(str(pusty),))))
        b = s.zlec(SI.ZadanieAnalizy(skan=pliki["poranna"], pula=SI.OpisPuli(foldery=(str(proj),)), uklad="poranna", numer=nr, inspekcja=False))
        koncowe = odb.czekaj_na_koncowe(2, 600.0)
        assert len(odb.typu("gotowy")) == 1  # bez restartu procesu
    assert [(z.zadanie_id, z.typ, z.rodzaj) for z in koncowe] == [(a, "blad", "analiza"), (b, "wynik", "")]
    assert "brak projekt" in koncowe[0].blad
    w = koncowe[1].wynik  # pola zadania trafiaja do porownaj: uklad podany recznie, numer plytki, bez inspekcji
    assert (w["plytka"], w["plytka_wybor"], w["numer"], w["inspekcja"]) == ("poranna", "reczny", nr, False)


def test_p5_prawdziwa_analiza_z_projektem_niewczytywalnym(plytki, tmp_path):
    """P5 na prawdziwym ``porownaj`` (proba ``s4`` recenzenta): w puli plik-smiec z fikcyjnym nazwiskiem w nazwie pliku
    i folderu. ``synth.wczytaj_projekt`` ostrzega "pomijam projekt <nazwa pliku>" - w zdarzeniach i w plikach wyjscia ma byc
    skrot pliku, a nazwiska 0 razy."""
    import shutil

    from stanowisko import silnik as SI

    pliki, proj = plytki
    pula = tmp_path / "pula"
    shutil.copytree(proj, pula)
    (pula / "Fikcyjna Testowa 4321").mkdir()
    (pula / "Fikcyjna Testowa 4321" / "FikcyjnaTestowa-11-crown_cad.stl").write_bytes(b"smiec")
    wyj = tmp_path / "wyniki"
    odb = Odbior()
    with SI.Silnik(na_zdarzenie=odb) as s:
        s.zlec(SI.ZadanieAnalizy(skan=pliki["poranna"], pula=SI.OpisPuli(foldery=(str(pula),)), wyjscie=wyj))
        koncowe = odb.czekaj_na_koncowe(1, 600.0)
    assert koncowe[0].typ == "wynik", (koncowe[0].blad, koncowe[0].szczegoly)
    ostrz = koncowe[0].wynik["ostrzezenia"]
    assert any(o.startswith(f"pomijam projekt <projekt {_skrot(b'smiec')}>") for o in ostrz), ostrz
    assert sorted(p.name for p in wyj.iterdir()) == sorted(Path(x).name for x in koncowe[0].pliki.values())  # _wynik.json i _podglad.npz
    for tekst in [repr(z) for z in odb.wszystkie] + [Path(koncowe[0].pliki["wynik"]).read_text(encoding="utf-8")]:
        assert _bez_nazwiska(tekst), tekst[:500]


def test_pamiec_linii_na_dysku(plytki, wyniki_atrap, tmp_path):
    """``pamiec_linii``: linie brzegu projektow trafiaja do katalogu, nowy proces silnika czyta je zamiast liczyc; wynik bez zmian."""
    from stanowisko import silnik as SI

    pliki, proj = plytki
    _, sil, _, _ = wyniki_atrap
    katalog = tmp_path / "pula_cache"
    koncowe, stany = [], []
    for _ in range(2):  # dwa osobne procesy: pierwszy wypelnia katalog, drugi z niego czyta
        odb = Odbior()
        with SI.Silnik(na_zdarzenie=odb, pamiec_linii=katalog) as s:
            nr = s.zlec(SI.ZadanieAnalizy(skan=pliki["okragla_wieczorna"], pula=SI.OpisPuli(foldery=(str(proj),))))
            koncowe.append(odb.czekaj_na_koncowe(1, 600.0)[0])
        stany.append({p.name: p.stat().st_mtime_ns for p in katalog.glob("*.npz")})
        assert koncowe[-1].typ == "wynik", koncowe[-1].blad
        _rowne("pamiec linii na dysku", bez_czasow(koncowe[-1].wynik), bez_czasow({**sil["okragla_wieczorna"], "zadanie_id": nr}))
    assert stany[0] and stany[0] == stany[1]  # pliki linii powstaly raz; drugi proces ich nie liczyl ani nie zapisywal od nowa
    linie = [sum(g["inspekcja"]["czas_linii_s"] for g in z.wynik["gniazda"] if g["inspekcja"]) for z in koncowe]
    print(f"\n[pamiec linii] czas wyznaczania linii brzegu: pierwszy proces {linie[0]:.2f} s, drugi (z dysku) {linie[1]:.2f} s; plikow {len(stany[0])}")


# ----------------------------------------------------------------------------
# kryterium 6: silnik z aplikacji Qt (offscreen)
# ----------------------------------------------------------------------------
def _plytka_w_qt(skan: Path, folder_puli: Path) -> dict:
    """Jedna plytka przez silnik w dzialajacej petli Qt: czas od zlecenia do wyniku (z zimnym startem procesu i budowa puli)
    oraz najdluzsza przerwa petli okna mierzona zegarem co 10 ms."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtCore import QEventLoop, QTimer
    from PySide6.QtWidgets import QApplication

    from stanowisko import silnik as SI

    app = QApplication.instance() or QApplication([])
    assert app.platformName() == "offscreen"
    petla = QEventLoop()
    stan = {"ostatni": time.perf_counter(), "przerwa": 0.0, "tykniec": 0, "wynik": None, "blad": None, "postep": [], "t_start": None}

    def tyk():
        teraz = time.perf_counter()
        stan["przerwa"] = max(stan["przerwa"], teraz - stan["ostatni"])
        stan["ostatni"] = teraz
        stan["tykniec"] += 1

    zegar = QTimer()
    zegar.setInterval(10)
    zegar.timeout.connect(tyk)
    s = SI.Silnik()
    lacznik = SI.lacznik_qt(s)
    lacznik.postep.connect(lambda nr, etap, udzial: stan["postep"].append((etap, udzial)))
    lacznik.wynik.connect(lambda nr, w: (stan.update(wynik=w, t_koniec=time.perf_counter()), petla.quit()))
    lacznik.blad.connect(lambda nr, rodzaj, tekst: (stan.update(blad=f"{rodzaj}: {tekst}"), petla.quit()))
    QTimer.singleShot(900_000, petla.quit)  # czekamy na wynik dluzej niz prog: przy przekroczeniu test ma podac zmierzony czas
    zegar.start()
    stan["ostatni"] = time.perf_counter()
    t0 = time.perf_counter()
    s.start()
    s.zlec(SI.ZadanieAnalizy(skan=skan, pula=SI.OpisPuli(foldery=(str(folder_puli),))))
    petla.exec()
    zegar.stop()
    lacznik.zatrzymaj()
    s.stop()
    assert stan["blad"] is None, stan["blad"]
    assert stan["wynik"] is not None, "brak wyniku w limicie czasu"
    return {"czas_s": stan["t_koniec"] - t0, "przerwa_s": stan["przerwa"], "tykniec": stan["tykniec"], "wynik": stan["wynik"], "postep": stan["postep"]}


def test_qt_offscreen_plytka_bez_zamrozenia_okna(plytki, wyniki_atrap):
    """Kryterium 6 na malej plytce z atrap (dawniej: QThread z Open3D, 195 s bez wyniku - P3a pkt 5.1)."""
    pliki, proj = plytki
    cli, _, _, _ = wyniki_atrap
    m = _plytka_w_qt(pliki["okragla_wieczorna"], proj)
    print(f"\n[kryterium 6, atrapy] plytka {m['czas_s']:.1f} s (prog testu {PROG_PLYTKI_S:.0f} s, kryterium 60 s), "
          f"najdluzsza przerwa petli Qt {m['przerwa_s'] * 1000:.0f} ms (prog testu {PROG_PRZERWY_S * 1000:.0f} ms, kryterium 200 ms), tykniec zegara {m['tykniec']}")
    assert m["przerwa_s"] <= PROG_PRZERWY_S
    assert m["tykniec"] >= 20 and len(m["postep"]) >= 4  # petla okna naprawde pracowala w trakcie analizy
    _sprawdz_rownosc("okragla_wieczorna", cli["okragla_wieczorna"], m["wynik"], "atrapy, Qt")
    assert m["czas_s"] <= PROG_PLYTKI_S


# ----------------------------------------------------------------------------
# warianty na duzych skanach odniesienia (wlaczane zmiennymi srodowiskowymi; liczby do raportu paczki)
# ----------------------------------------------------------------------------
def _skany_ref() -> dict:
    if not (DANE_REF and PROJEKTY_REF and Path(DANE_REF).is_dir() and Path(PROJEKTY_REF).is_dir()):
        pytest.skip(BRAK_DANYCH_REF)
    skany = {}
    for typ in TYPY:
        pasuja = sorted(Path(DANE_REF).glob(f"skan_{typ}_n*.stl"))
        assert pasuja, f"brak skanu typu {typ} w E3A2_DANE_REF"
        skany[typ] = pasuja[int(os.environ.get("E3A2_KTORY", "0")) % len(pasuja)]
    return skany


@pytest.fixture(scope="module")
def wyniki_ref(tmp_path_factory):
    skany = _skany_ref()
    d = tmp_path_factory.mktemp("ref")
    t0 = time.time()
    cli = _uruchom_cli(skany, Path(PROJEKTY_REF), d / "cli")
    t1 = time.time()
    sil, zdarzenia = _uruchom_silnik(skany, Path(PROJEKTY_REF))
    print(f"\n[kryterium 5, skany odniesienia] {', '.join(p.name for p in skany.values())}: wiersz polecen (4 procesy po kolei) {t1 - t0:.0f} s, "
          f"silnik (jeden proces, po kolei) {time.time() - t1:.0f} s; czas porownaj na plytke, wiersz polecen / silnik: "
          + ", ".join(f"{t} {cli[t]['czas_s']['razem']} / {w['czas_s']['razem']} s" for t, w in sil.items()))
    return cli, sil


@pytest.mark.parametrize("typ", TYPY)
def test_skany_odniesienia_wynik_rowny_wierszowi_polecen(wyniki_ref, typ):
    """Kryterium 5 na sztucznych skanach odniesienia 45-55 MB z pula prawdziwych projektow (tylko z E3A2_DANE_REF)."""
    cli, sil = wyniki_ref
    _sprawdz_rownosc(typ, cli[typ], sil[typ], "skany odniesienia", wymagany=3)


def test_skany_odniesienia_qt_offscreen(wyniki_ref):
    """Kryterium 6 na skanie odniesienia: czas plytki z zimnym startem procesu i budowa puli, przerwy petli Qt."""
    cli, _ = wyniki_ref
    skany = _skany_ref()
    typ = os.environ.get("E3A2_TYP_QT", "wieczorna")
    m = _plytka_w_qt(skany[typ], Path(PROJEKTY_REF))
    print(f"\n[kryterium 6, skan odniesienia {skany[typ].name}] plytka {m['czas_s']:.1f} s od zlecenia do wyniku, z zimnym startem procesu "
          f"(prog testu {PROG_PLYTKI_S:.0f} s, kryterium 60 s; samo porownaj w silniku {m['wynik']['czas_s']['razem']} s, "
          f"ten sam skan z wiersza polecen {cli[typ]['czas_s']['razem']} s), najdluzsza przerwa petli Qt {m['przerwa_s'] * 1000:.0f} ms "
          f"(prog testu {PROG_PRZERWY_S * 1000:.0f} ms, kryterium 200 ms), tykniec zegara {m['tykniec']}")
    assert m["przerwa_s"] <= PROG_PRZERWY_S
    _sprawdz_rownosc(typ, cli[typ], m["wynik"], "skany odniesienia, Qt", wymagany=3)
    assert m["czas_s"] <= PROG_PLYTKI_S  # na koncu: czas zalezy od obciazenia komputera, pozostale warunki nie
