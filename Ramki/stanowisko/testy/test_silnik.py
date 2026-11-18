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

import json
import math
import os
import signal
import subprocess
import sys
import threading
import time
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
    """Udaje analize: czyta plik, zglasza postep, zwraca slownik. Tresc pliku steruje awaria (ZLY / ZABIJ / SPIJ <s>)."""
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
    time.sleep(0.05)
    if postep is not None:
        postep("proba: koniec", 0.9)
    return {"skan": Path(skan).name, "plytka": plytka, "numer": numer, "wspolczynnik": wspolczynnik, "bajtow": len(dane),
            "pid": os.getpid(), "start": t0, "koniec": time.time(), "gniazda": [], "czas_s": {"razem": round(time.time() - t0, 3)}}


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


def roznice(a, b, sciezka="", tol: float = TOL_SZUMU, liczniki_z_tolerancja: bool = False) -> list[str]:
    """Lista pol, ktorymi roznia sie dwie struktury JSON. Wszystko porownywane dokladnie, poza liczbami zmiennoprzecinkowymi:
    te moga sie roznic o ``tol`` (wzglednie albo bezwzglednie). ``liczniki_z_tolerancja``: pola ``iteracje`` sa pomijane,
    a liczniki probek (``_licznik_punktow``) moga sie roznic o 2 albo 1 %.

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
            return [] if math.isclose(a, b, rel_tol=tol, abs_tol=tol) or (math.isnan(a) and math.isnan(b)) else [f"{sciezka}: {a!r} != {b!r}"]
        if licznik == "punkty" and abs(a - b) <= max(2, 0.01 * max(abs(a), abs(b))):
            return []
        return [] if a == b else [f"{sciezka}: {a!r} != {b!r}"]
    if type(a) is not type(b):
        return [f"{sciezka}: typ {type(a).__name__} != {type(b).__name__}"]
    if isinstance(a, dict):
        w = [f"{sciezka}.{k}: brak po jednej stronie" for k in sorted(set(a) ^ set(b))]
        for k in sorted(set(a) & set(b)):
            w += roznice(a[k], b[k], f"{sciezka}.{k}", tol, liczniki_z_tolerancja)
        return w
    if isinstance(a, list):
        if len(a) != len(b):
            return [f"{sciezka}: dlugosc {len(a)} != {len(b)}"]
        w = []
        for i, (x, y) in enumerate(zip(a, b)):
            w += roznice(x, y, f"{sciezka}[{i}]", tol, liczniki_z_tolerancja)
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
    ids = [s.zlec(_zadanie(p, numer=i, skan_sha16=f"{i:016x}")) for i, p in enumerate(pliki)]
    assert ids == sorted(ids) and len(set(ids)) == 20
    koncowe = odb.czekaj_na_koncowe(20)
    assert [z.typ for z in koncowe] == ["wynik"] * 20
    assert [z.zadanie_id for z in koncowe] == ids  # kolejnosc zlecen, zadnego zgubionego
    wyniki = [z.wynik for z in koncowe]
    assert [w["skan"] for w in wyniki] == [p.name for p in pliki]
    assert [w["zadanie_id"] for w in wyniki] == ids and [w["skan_sha16"] for w in wyniki] == [f"{i:016x}" for i in range(20)]
    assert [w["numer"] for w in wyniki] == list(range(20))
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
    assert "plytka.stl" in czysty and "PermissionError" in czysty and czysty.count("<plik z puli projektow>") == 3


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
            czasy[nr] = 0.6 + 0.15 * miejsce
        zapisy = SY.symuluj(folder, [SY.sztuczny_stl(200 + i, seed=i) for i in range(20)], ile=20, czasy=czasy, kawalki=(5, 5), rownolegle=20, seed=1)
        koncowe = odb.czekaj_na_koncowe(20, 120.0)
    finally:
        sc.stop()
    wg_zapisu = [Path(z["plik"]).name for z in sorted(zapisy, key=lambda z: z["mtime_ns"])]
    assert [z.typ for z in koncowe] == ["wynik"] * 20  # zadnego zgubionego, zadnej awarii
    assert [z.wynik["skan"] for z in koncowe] == wg_zapisu == [Path(z.plik).name for z in zdarzenia]  # analiza w kolejnosci zapisu
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
    assert sil["plytka"] == typ == cli["plytka"] and sil["plytka_wybor"] == "auto" and sil["uklad_zgodny"] is True
    assert len(sil["gniazda"]) >= 1
    dodatkowe = {"zadanie_id", "skan_sha16"}
    assert dodatkowe <= set(sil) and set(sil) - dodatkowe == set(cli)  # kontrakt 3.8: slownik porownaj + zadanie_id + skan_sha16
    _rowne(f"kryterium 5, {zrodlo}, {typ}", bez_czasow({k: v for k, v in sil.items() if k not in dodatkowe}), bez_czasow(cli), wymagany)


def _rowne(opis: str, a, b, wymagany: int = 2) -> None:
    """Porownanie dwoch wynikow na trzech poziomach (patrz ``roznice``); liczba pol roznych na kazdym jest wypisywana.

    1. szum numeryczny (1e-9) - wymagany tylko z E3A2_SCISLE=1: bywa niespelniony takze miedzy dwoma uruchomieniami
       wiersza polecen, wiec w zwyklym zestawie dawalby losowo czerwony test;
    2. miary (liczby do 2e-3, liczniki probek do 2 albo 1 %, bez liczby iteracji) - wymagany w testach na plytkach z atrap;
    3. decyzje: struktura, teksty, statusy, identyfikatory i liczniki decyzji (gniazdo, numer, liczba ubytkow ...) rowne,
       wartosci zmiennoprzecinkowe nieporownywane - wymagany w wariantach na skanach odniesienia 45-55 MB. Tam inna galaz
       ICP korekty skali zmienia tez miary skwantowane (17.11.2026: ``najdl_przerwa_mm`` 0,0 / 0,05 w 1 z 16 porownan
       silnik - wiersz polecen), a wiersz polecen rozni sie sam od siebie na poziomie 1 w 3 z 3 par przebiegow."""
    poziomy = {1: roznice(a, b), 2: roznice(a, b, tol=TOL_DECYZJI, liczniki_z_tolerancja=True),
               3: roznice(a, b, tol=math.inf, liczniki_z_tolerancja=True)}
    print(f"\n[{opis}] pol roznych: {len(poziomy[1])} przy tolerancji 1e-9, {len(poziomy[2])} na poziomie miar (2e-3, liczniki probek "
          f"z tolerancja), {len(poziomy[3])} na poziomie decyzji; wymagany poziom {1 if SCISLE else wymagany}"
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
        stem = Path(z.zadanie.skan).stem
        p_json, p_npz = d / "silnik" / f"{stem}_wynik.json", d / "silnik" / f"{stem}_podglad.npz"
        assert z.pliki == {"wynik": str(p_json), "podglad": str(p_npz)}
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
