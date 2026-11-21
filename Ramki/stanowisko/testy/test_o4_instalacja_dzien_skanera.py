"""E3-O4 punkty 1 i 2: okno "Dzien skanera" i pomiar szczegolowy uruchomione Z INSTALACJI (uklad katalogow instalatora).

Uklad instalacji jest odtwarzany w ``tmp_path`` prawdziwymi funkcjami instalatora (``ustawienia_ze_wzoru``, ``zapisz_skrypty``):

    <tmp>/Stanowisko/ustawienia.toml, wersja_biezaca.txt, dane/, *.cmd (skroty)
    <tmp>/Stanowisko/wersje/9.9.9/program/stanowisko/..., narzedzia/pomiar_skanu/..., ustawienia.przyklad.toml

Polecenia sa brane z wiersza uruchomienia Pythona w skrocie zapisanym przez instalator (``%KAT%``, ``%W%``, ``%*``
podstawione jak w cmd.exe), katalog biezacy = katalog programu wersji, bez katalogu repo w ``PYTHONPATH`` - tak jak robi to
skrot. Interpreter = interpreter testow (srodowiska wersji test nie buduje - to robi proba na instalacji probnej, etap B2).
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import types
from pathlib import Path

import pytest
import trimesh

from instalacja import instalator as I
from stanowisko import dzien_skanera as DS, dzien_skanera_rdzen as R, ustawienia as UST

STANOWISKO = Path(__file__).resolve().parent.parent
WZORY = STANOWISKO / "instalacja" / "wzory"
WERSJA = "9.9.9"
FOLDER_WZORU = "C:/Aidite/Scandata"  # folder skanera w ustawienia.przyklad.toml (to on byl obserwowany przed poprawka)
BEZ_PAMIECI = shutil.ignore_patterns("__pycache__", "*.pyc")


# ----------------------------------------------------------------------------
# pomocnicze
# ----------------------------------------------------------------------------
@pytest.fixture
def inst(tmp_path) -> types.SimpleNamespace:
    """Katalog instalacji z jedna wersja programu (kopia modulow z repo) i ustawieniami zalozonymi jak przez instalator."""
    kat = tmp_path / "Stanowisko"
    wersja = kat / "wersje" / WERSJA
    program = wersja / "program"
    shutil.copytree(STANOWISKO / "stanowisko", program / "stanowisko", ignore=BEZ_PAMIECI)
    shutil.copytree(STANOWISKO / "narzedzia" / "pomiar_skanu", program / "narzedzia" / "pomiar_skanu", ignore=BEZ_PAMIECI)
    shutil.copytree(WZORY, program / "instalacja" / "wzory")
    shutil.copy(STANOWISKO / "ustawienia.przyklad.toml", program / "ustawienia.przyklad.toml")
    (wersja / "venv" / "Scripts").mkdir(parents=True)
    (kat / "dane").mkdir()
    (kat / "wersja_biezaca.txt").write_bytes((WERSJA + "\r\n").encode("ascii"))
    eksport = tmp_path / "eksport_instalacji"
    eksport.mkdir()
    tresc = I.ustawienia_ze_wzoru((program / "ustawienia.przyklad.toml").read_bytes(), kat).decode("utf-8")
    assert FOLDER_WZORU in tresc
    tresc = tresc.replace(FOLDER_WZORU, eksport.as_posix())
    (kat / "ustawienia.toml").write_bytes(tresc.encode("utf-8"))
    I.zapisz_skrypty(program, kat)
    return types.SimpleNamespace(kat=kat, wersja=wersja, program=program, eksport=eksport, ustawienia=kat / "ustawienia.toml",
                                 sesje=kat / "dane" / "dzien_skanera")


def polecenie_skrotu(inst, nazwa: str, *argumenty: str) -> list[str]:
    """Wiersz uruchomienia Pythona ze skrotu ``<instalacja>/<nazwa>`` z podstawionymi zmiennymi cmd.exe."""
    wiersze = (inst.kat / nazwa).read_bytes().decode("ascii").splitlines()
    wiersz = next(w for w in wiersze if w.startswith('"%W%\\venv\\Scripts\\python.exe"'))
    polecenie = [sys.executable]
    for czesc in [c.strip('"') for c in re.findall(r'"[^"]*"|\S+', wiersz)][1:]:
        if czesc == "%*":
            polecenie += list(argumenty)
        else:
            polecenie.append(czesc.replace("%KAT%", str(inst.kat) + os.sep).replace("%W%", str(inst.wersja)))
    return polecenie


def srodowisko_skrotu() -> dict:
    """Zmienne jak po skrocie instalacji: katalogu repo nie ma w PYTHONPATH (skrot czysci PYTHONPATH; tu zostaja tylko
    katalogi pakietow, gdy interpreter testow dostaje pakiety ta droga), okna Qt bez ekranu."""
    env = dict(os.environ)
    swoje = {STANOWISKO.resolve(), (STANOWISKO / "narzedzia").resolve()}
    reszta = [p for p in env.get("PYTHONPATH", "").split(os.pathsep) if p and Path(p).resolve() not in swoje]
    env.pop("PYTHONPATH", None)
    env.pop("PYTHONHOME", None)
    if reszta:
        env["PYTHONPATH"] = os.pathsep.join(reszta)
    env.update(PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1", PYTHONNOUSERSITE="1", QT_QPA_PLATFORM="offscreen")
    return env


def uruchom(inst, polecenie: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(polecenie, cwd=str(inst.program), env=srodowisko_skrotu(), capture_output=True, text=True, encoding="utf-8",
                          errors="replace", stdin=subprocess.DEVNULL, timeout=300)


def pliki(katalog: Path) -> dict:
    return {p.relative_to(katalog).as_posix(): p.stat().st_size for p in sorted(katalog.rglob("*")) if p.is_file()}


def jedyna_sesja(inst) -> dict:
    """Manifest jedynej sesji w ``<instalacja>/dane/dzien_skanera``."""
    foldery = sorted(p for p in inst.sesje.iterdir() if p.is_dir())
    assert len(foldery) == 1, foldery
    return json.loads((foldery[0] / R.PLIK_MANIFESTU).read_text(encoding="utf-8"))


def obserwowane(manifest: dict) -> list[Path]:
    return [R.rozwin_sciezke(f["sciezka"]) for f in manifest["foldery"]]  # manifest skraca katalog domowy do "~"


# ----------------------------------------------------------------------------
# punkt 1: skrot i okno
# ----------------------------------------------------------------------------
def test_skrot_dzien_skanera_jest_wzorem_zakladanym_przez_instalator(inst):
    assert "Dzien_skanera.cmd" in I.WZORY_SKRYPTOW
    wzor = (WZORY / "Dzien_skanera.cmd").read_bytes()
    assert wzor.isascii() and b"\r\n" in wzor and b"\n" not in wzor.replace(b"\r\n", b"")  # jak pozostale wzory: ASCII, CRLF
    assert (inst.kat / "Dzien_skanera.cmd").read_bytes() == wzor  # zalozony przez instalator.zapisz_skrypty
    # ten sam mechanizm co Stanowisko.cmd: modul programu + plik ustawien instalacji, opcje czlowieka przechodza dalej
    assert polecenie_skrotu(inst, "Dzien_skanera.cmd", "--nowa")[1:] == ["-m", "stanowisko.dzien_skanera", "--ustawienia",
                                                                        str(inst.ustawienia), "--nowa"]
    assert polecenie_skrotu(inst, "Stanowisko.cmd")[1:] == ["-m", "stanowisko.aplikacja", "--ustawienia", str(inst.ustawienia)]

    def przed_startem(nazwa: str) -> list[str]:  # wszystko do wejscia do katalogu programu: wybor wersji, czyszczenie zmiennych Pythona
        wiersze = [w for w in (WZORY / nazwa).read_text(encoding="ascii").splitlines() if not w.lower().startswith("rem ")]
        return wiersze[:wiersze.index('cd /d "%W%\\program"') + 1]

    assert przed_startem("Dzien_skanera.cmd") == przed_startem("Stanowisko.cmd")


def test_okno_ze_skrotu_instalacji_bierze_ustawienia_i_dane_instalacji(inst):
    """Kryterium 1: ``Dzien_skanera.cmd --nowa --zamknij-po 1`` - sesja w ``<instalacja>/dane/dzien_skanera``, folder
    obserwowany z ``<instalacja>/ustawienia.toml``, w katalogu wersji 0 nowych plikow."""
    przed = pliki(inst.wersja)
    wynik = uruchom(inst, polecenie_skrotu(inst, "Dzien_skanera.cmd", "--nowa", "--zamknij-po", "1"))
    assert wynik.returncode == 0, wynik.stdout + wynik.stderr
    manifest = jedyna_sesja(inst)
    assert obserwowane(manifest) == [inst.eksport]
    assert pliki(inst.wersja) == przed
    assert not (inst.program / "dane").exists()


def test_okno_przez_polecenie_cmd_bez_opcji_tez_bierze_ustawienia_i_dane_instalacji(inst):
    """Droga z wydania 0.3.1 (``Polecenie.cmd -m stanowisko.dzien_skanera``, bez ``--ustawienia``): program sam rozpoznaje uklad
    instalacji - nie czyta wzoru z katalogu wersji i nie zapisuje w nim sesji."""
    przed = pliki(inst.wersja)
    wynik = uruchom(inst, polecenie_skrotu(inst, "Polecenie.cmd", "-m", "stanowisko.dzien_skanera", "--nowa", "--zamknij-po", "1"))
    assert wynik.returncode == 0, wynik.stdout + wynik.stderr
    assert obserwowane(jedyna_sesja(inst)) == [inst.eksport]
    assert pliki(inst.wersja) == przed


def test_zly_plik_ustawien_instalacji_nie_przenosi_sesji_do_katalogu_wersji(inst):
    """Plik ustawien instalacji z bledem: okno dziala na wzorze (jak dotad, z uwaga w dzienniku okna), ale sesja i tak
    powstaje w ``<instalacja>/dane/dzien_skanera`` - katalog wersji zostaje bez zmian."""
    inst.ustawienia.write_text("[sciezki\nto nie jest TOML", encoding="utf-8")
    przed = pliki(inst.wersja)
    wynik = uruchom(inst, polecenie_skrotu(inst, "Dzien_skanera.cmd", "--nowa", "--zamknij-po", "1"))
    assert wynik.returncode == 0, wynik.stdout + wynik.stderr
    manifest = jedyna_sesja(inst)
    assert obserwowane(manifest) == [Path(FOLDER_WZORU)]
    assert pliki(inst.wersja) == przed


def test_uklad_instalacji_jest_rozpoznawany_po_katalogach(inst, tmp_path):
    assert R.katalog_instalacji(inst.program) == inst.kat
    assert R.katalog_instalacji(STANOWISKO) is None and R.katalog_instalacji() is None  # repo
    inny = tmp_path / "x" / "wersje" / WERSJA / "program"
    inny.mkdir(parents=True)
    assert R.katalog_instalacji(inny) is None  # uklad katalogow jak w instalacji, ale bez pliku ustawien instalacji
    assert R.katalog_instalacji(inst.kat / "wersje" / WERSJA) is None and R.katalog_instalacji(tmp_path / "program") is None


def test_katalog_sesji_z_ustawien_instalacji_a_z_repo_jak_dotad(inst, monkeypatch):
    """Katalog sesji = katalog bazy z ustawien wskazanych programowi (tak program "Stanowisko" wyznacza katalog danych);
    z repo, na wlasnym pliku ustawien albo na wzorze - jak dotad ``<repo>/dane/dzien_skanera``."""
    ust_inst, plik, uwaga = R.wczytaj_ustawienia_bezpiecznie(inst.ustawienia)
    assert plik == inst.ustawienia and uwaga == ""
    assert R.katalog_sesji(ust_inst, plik) == inst.sesje
    repo = UST.KORZEN / "dane" / "dzien_skanera"
    assert R.KATALOG_SESJI == repo
    ust_repo, plik_repo, _ = R.wczytaj_ustawienia_bezpiecznie()
    assert plik_repo in (UST.PLIK_USTAWIEN, UST.PLIK_PRZYKLADU)  # z repo: wlasny plik programu, jak dotad
    assert R.katalog_sesji(ust_repo, plik_repo) == repo
    assert R.katalog_sesji(ust_repo, UST.PLIK_PRZYKLADU) == repo and R.katalog_sesji(None, None) == repo
    assert R.katalog_sesji(ust_repo) == repo
    # program lezacy w katalogu wersji instalacji: bez wskazania pliku bierze ustawienia instalacji; bez ustawien - dane instalacji
    monkeypatch.setattr(UST, "KORZEN", inst.program)
    ust_auto, plik_auto, _ = R.wczytaj_ustawienia_bezpiecznie()
    assert plik_auto == inst.ustawienia and ust_auto["sciezki"]["folder_eksportu_skanera"] == inst.eksport.as_posix()
    assert R.katalog_sesji(ust_auto, plik_auto) == inst.sesje
    assert R.katalog_sesji(None, None) == inst.sesje and R.katalog_sesji(ust_repo, UST.PLIK_PRZYKLADU) == inst.sesje


def test_wybor_sesji_katalog_domyslny(inst, monkeypatch):
    """``wybierz_sesje`` bez ``--dane``: z ustawieniami instalacji - katalog danych instalacji; z repo - jak dotad. Opcja
    ``--dane`` ma pierwszenstwo. (Sesji test nie zaklada - sprawdza katalog, do ktorego by trafila.)"""
    wolania = []
    monkeypatch.setattr(R.Sesja, "lista", staticmethod(lambda katalog=None: []))
    monkeypatch.setattr(R.Sesja, "nowa", staticmethod(lambda katalog=None, **k: wolania.append((Path(katalog), k.get("foldery"))) or "sesja"))

    class A:
        sesja, nowa, dane, folder = None, False, None, None

    ust_inst, plik, _ = R.wczytaj_ustawienia_bezpiecznie(inst.ustawienia)
    assert DS.wybierz_sesje(A, ust_inst, None, plik_ustawien=plik) == "sesja"
    assert wolania[-1] == (inst.sesje, [inst.eksport.as_posix()])
    ust_repo, plik_repo, _ = R.wczytaj_ustawienia_bezpiecznie()
    DS.wybierz_sesje(A, ust_repo, None, plik_ustawien=plik_repo)
    assert wolania[-1][0] == UST.KORZEN / "dane" / "dzien_skanera"
    DS.wybierz_sesje(A, ust_repo)  # wywolanie w starej postaci (testy, sterowniki prob)
    assert wolania[-1][0] == UST.KORZEN / "dane" / "dzien_skanera"
    A.dane = inst.kat / "gdzie_indziej"
    DS.wybierz_sesje(A, ust_inst, None, plik_ustawien=plik)
    assert wolania[-1][0] == inst.kat / "gdzie_indziej"


# ----------------------------------------------------------------------------
# punkt 2: pomiar szczegolowy
# ----------------------------------------------------------------------------
@pytest.fixture
def skan(tmp_path) -> Path:
    """Mala siatka (to nie jest plytka) - pomiar z ``--bez-plytki`` konczy sie w ulamku sekundy; test dotyczy drogi
    uruchomienia (import programu, plik ustawien), nie liczb pomiaru."""
    plik = tmp_path / "skany" / "skan_sztuczny.stl"
    plik.parent.mkdir()
    trimesh.creation.icosphere(subdivisions=2, radius=5.0).export(plik)
    return plik


def test_pomiar_skanu_przez_polecenie_cmd_w_instalacji(inst, skan, tmp_path):
    """Kryterium 2 (czesc jednostkowa): ``Polecenie.cmd narzedzia\\pomiar_skanu\\pomiar_skanu.py <skan> ...`` - bylo
    ``ModuleNotFoundError: stanowisko``, a po dodaniu katalogu programu ``FileNotFoundError`` pliku ustawien."""
    przed = pliki(inst.wersja)
    wyj = tmp_path / "wynik_pomiaru"
    wynik = uruchom(inst, polecenie_skrotu(inst, "Polecenie.cmd", r"narzedzia\pomiar_skanu\pomiar_skanu.py", str(skan), "--bez-plytki",
                                           "--wyj", str(wyj)))
    assert wynik.returncode == 0, wynik.stdout + wynik.stderr
    assert "Traceback" not in wynik.stderr
    assert f"ustawienia: {inst.ustawienia}" in wynik.stdout.splitlines()  # plik ustawien INSTALACJI, nie wzor z katalogu wersji
    assert (wyj / "raport.txt").is_file() and json.loads((wyj / "pomiar.json").read_text(encoding="utf-8"))["trojkatow"] == 320
    assert pliki(inst.wersja) == przed


def test_pomiar_skanu_opcja_ustawienia_i_brak_pliku(inst, skan, tmp_path):
    """Opcja ``--ustawienia`` (tak okno przekazuje swoj plik) ma pierwszenstwo; pliku nie ma = komunikat i kod 2 PRZED
    wczytaniem skanu, bez sladu wyjatku."""
    inny = tmp_path / "inne_ustawienia.toml"
    shutil.copy(inst.ustawienia, inny)
    narzedzie = r"narzedzia\pomiar_skanu\pomiar_skanu.py"
    wynik = uruchom(inst, polecenie_skrotu(inst, "Polecenie.cmd", narzedzie, str(skan), "--bez-plytki", "--ustawienia", str(inny),
                                           "--wyj", str(tmp_path / "w1")))
    assert wynik.returncode == 0 and f"ustawienia: {inny}" in wynik.stdout.splitlines(), wynik.stdout + wynik.stderr
    wynik = uruchom(inst, polecenie_skrotu(inst, "Polecenie.cmd", narzedzie, str(skan), "--bez-plytki", "--ustawienia",
                                           str(tmp_path / "nie_ma.toml"), "--wyj", str(tmp_path / "w2")))
    assert wynik.returncode == 2 and "Traceback" not in wynik.stderr and "nie_ma.toml" in wynik.stderr, wynik.stdout + wynik.stderr
    assert "wczytuje" not in wynik.stdout and not (tmp_path / "w2").exists()


def test_przycisk_pomiaru_przekazuje_plik_ustawien_okna(inst, tmp_path):
    """Przycisk "Pomiar szczegolowy": polecenie dostaje plik ustawien, na ktorym dziala okno (w instalacji - plik instalacji),
    interpreter = interpreter okna (w instalacji: srodowisko wersji), narzedzie z katalogu programu okna."""
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])  # noqa: F841
    ust, plik, _ = R.wczytaj_ustawienia_bezpiecznie(inst.ustawienia)
    sesja = R.Sesja.nowa(tmp_path / "sesje", foldery=[inst.eksport])
    okno = DS.Okno(sesja, ust, plik, "brak", autostart=False)
    try:
        wpis = {"id": 1, "cel": "kroki/k01_start/pliki/skan.stl", "krok": sesja.m["biezacy_krok"]}
        polecenie = okno.polecenie_pomiaru(wpis, 1.22, None)
        assert polecenie[0] == sys.executable and Path(polecenie[1]) == UST.KORZEN / "narzedzia" / "pomiar_skanu" / "pomiar_skanu.py"
        assert polecenie[polecenie.index("--ustawienia") + 1] == str(inst.ustawienia)
        assert polecenie[-2] == "--wyj" and Path(polecenie[-1]).parent == sesja.folder / "pomiary"
        okno.zbieracz.plik_ustawien = None  # okno bez pliku ustawien (ustawien nie dalo sie wczytac): narzedzie szuka pliku samo
        assert "--ustawienia" not in okno.polecenie_pomiaru(wpis, 1.22, None)
    finally:
        okno.close()


def test_pomiar_skanu_cmd_w_instalacji_bez_py_z_path():
    """``pomiar_skanu.cmd`` (przeciagniecie pliku): w instalacji bierze interpreter srodowiska wersji (``..\\venv`` obok katalogu
    programu, rozpoznany po ``instalacja.json``), a ``py -3.12`` zostaje tylko dla kopii repo. Skrypt jest interaktywny
    (pytanie, pauza, Notatnik) - test sprawdza tresc, nie uruchamia go."""
    tresc = (STANOWISKO / "narzedzia" / "pomiar_skanu" / "pomiar_skanu.cmd").read_bytes()
    assert tresc.isascii() and b"\n" not in tresc.replace(b"\r\n", b"")
    wiersze = tresc.decode("ascii").splitlines()
    wybor = [i for i, w in enumerate(wiersze) if w.startswith("if exist ") and "set PY=" in w]
    srodowisko_wersji = [i for i in wybor if r'"%STANOWISKO%\..\venv\Scripts\python.exe"' in wiersze[i] and "instalacja.json" in wiersze[i]]
    domyslny, start = wiersze.index("set PY=py -3.12"), next(i for i, w in enumerate(wiersze) if w.startswith("%PY% "))
    assert len(srodowisko_wersji) == 1 and domyslny < srodowisko_wersji[0] < start
    assert sum("py -3.12" in w for w in wiersze if not w.lower().startswith("rem ")) == 1  # tylko wartosc domyslna dla repo
