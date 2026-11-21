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
if str(STANOWISKO / "narzedzia") not in sys.path:
    sys.path.insert(0, str(STANOWISKO / "narzedzia"))
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
    # runda 2 (P2): katalog sesji podany wprost - wersja 0.3.1 (po powrocie do niej) tez zapisze sesje w danych instalacji
    assert polecenie_skrotu(inst, "Dzien_skanera.cmd", "--nowa")[1:] == ["-m", "stanowisko.dzien_skanera", "--ustawienia",
                                                                        str(inst.ustawienia), "--dane", str(inst.sesje), "--nowa"]
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
    assert R.katalog_instalacji(inny) is None  # uklad katalogow jak w instalacji, ale bez zadnego pliku instalatora
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


# ----------------------------------------------------------------------------
# runda 2 (recenzja PR #52): P1 - brak pliku ustawien instalacji, wzgledna sciezka bazy; P2 - skrot podaje katalog sesji
# ----------------------------------------------------------------------------
def ustaw_baze_wzgledna(inst) -> None:
    """``[sciezki] baza`` taka jak we wzorze (wzgledna = liczona od katalogu programu, czyli w instalacji od katalogu wersji)."""
    tresc = inst.ustawienia.read_text(encoding="utf-8")
    nowa, ile = re.subn(r'(?m)^baza = "[^"]*"', 'baza = "dane/stanowisko.sqlite"', tresc)
    assert ile == 1
    inst.ustawienia.write_text(nowa, encoding="utf-8")
    assert not UST.wczytaj_ustawienia(inst.ustawienia)["sciezki"]["baza"].startswith(inst.kat.as_posix())


def test_p1_instalacja_rozpoznawana_po_plikach_instalatora_takze_bez_pliku_ustawien(inst, tmp_path):
    """P1: brak ``<instalacja>/ustawienia.toml`` nie robi z instalacji kopii repo - wystarcza ``wersja_biezaca.txt`` albo
    ``wersje/<wersja>/instalacja.json`` (zaklada je instalator)."""
    assert I.PLIK_BIEZACEJ == "wersja_biezaca.txt" and I.PLIK_INSTALACJI == "instalacja.json" and I.PLIK_USTAWIEN == "ustawienia.toml"
    inst.ustawienia.unlink()
    assert R.katalog_instalacji(inst.program) == inst.kat  # zostal wersja_biezaca.txt
    (inst.kat / I.PLIK_BIEZACEJ).unlink()
    assert R.katalog_instalacji(inst.program) is None
    (inst.wersja / I.PLIK_INSTALACJI).write_text("{}", encoding="ascii")  # stan po kodzie 10: wersja zalozona, wskaznika jeszcze nie ma
    assert R.katalog_instalacji(inst.program) == inst.kat
    obok = tmp_path / "y" / "wersje" / WERSJA
    (obok / "program").mkdir(parents=True)
    (obok.parent / I.PLIK_INSTALACJI).write_text("{}", encoding="ascii")  # plik w zlym miejscu to nie instalacja
    assert R.katalog_instalacji(obok / "program") is None


@pytest.mark.parametrize("droga", ["Dzien_skanera.cmd", "Polecenie.cmd"])
def test_p1_brak_pliku_ustawien_instalacji_bez_wzoru_i_bez_sesji_w_katalogu_wersji(inst, droga):
    """P1 (a): ``<instalacja>/ustawienia.toml`` nie istnieje. Okno nie czyta wzoru ani ``ustawienia.toml`` z katalogu wersji
    (nie obserwuje folderu ze wzoru), sesja powstaje w ``<instalacja>/dane/dzien_skanera``, proba mowi wprost ``ustawienia BRAK``
    i podaje, ktorego pliku brakuje; w katalogu wersji 0 nowych plikow."""
    shutil.copy(inst.ustawienia, inst.program / "ustawienia.toml")  # plik w katalogu wersji (stara, zla rada) - nie wolno go czytac
    inst.ustawienia.unlink()
    przed = pliki(inst.wersja)
    argumenty = ("--nowa", "--zamknij-po", "1") if droga == "Dzien_skanera.cmd" else ("-m", "stanowisko.dzien_skanera", "--nowa", "--zamknij-po", "1")
    wynik = uruchom(inst, polecenie_skrotu(inst, droga, *argumenty))
    assert wynik.returncode == 0, wynik.stdout + wynik.stderr
    assert obserwowane(jedyna_sesja(inst)) == []  # ani folder ze wzoru, ani z pliku w katalogu wersji
    assert pliki(inst.wersja) == przed and not (inst.program / "dane").exists()
    wiersz = next(w for w in wynik.stdout.splitlines() if w.startswith("DZIEN SKANERA: "))
    assert f"sesja {inst.sesje}" in wiersz and "; ustawienia BRAK; foldery obserwowane: brak" in wiersz
    uwaga = next(w for w in wynik.stdout.splitlines() if w.startswith("UWAGA: "))
    assert str(inst.ustawienia) in uwaga and "zainstaluj.cmd" in uwaga and "przyklad" not in uwaga


def test_p1_baza_wzgledna_katalog_sesji_w_katalogu_wersji_jest_odrzucany(inst):
    """P1 (b): ``[sciezki] baza`` wzgledna - katalog bazy lezy w katalogu wersji. Bez ``--dane`` (droga ``Polecenie.cmd``):
    komunikat po polsku, kod 1, zadnej sesji. Skrot ``Dzien_skanera.cmd`` (P2: podaje ``--dane``) dziala i zapisuje sesje w
    danych instalacji. Katalog sesji z ``--dane`` wskazany w ``wersje`` tez jest odrzucany."""
    ustaw_baze_wzgledna(inst)
    przed = pliki(inst.wersja)
    wynik = uruchom(inst, polecenie_skrotu(inst, "Polecenie.cmd", "-m", "stanowisko.dzien_skanera", "--nowa", "--zamknij-po", "1"))
    assert wynik.returncode == 1, wynik.stdout + wynik.stderr
    assert "Traceback" not in wynik.stderr and "DZIEN SKANERA: sesja" not in wynik.stdout
    blad = next(w for w in wynik.stderr.splitlines() if w.startswith("BLAD: "))
    for napis in ("lezy w katalogu wersji programu", str(inst.kat / "wersje"), "CO ZROBIC", "[sciezki] baza", str(inst.kat / "Dzien_skanera.cmd")):
        assert napis in blad, napis
    assert pliki(inst.wersja) == przed and not inst.sesje.exists()

    wynik = uruchom(inst, polecenie_skrotu(inst, "Dzien_skanera.cmd", "--nowa", "--zamknij-po", "1"))
    assert wynik.returncode == 0, wynik.stdout + wynik.stderr
    assert obserwowane(jedyna_sesja(inst)) == [inst.eksport]
    assert pliki(inst.wersja) == przed and not (inst.program / "dane").exists()

    wynik = uruchom(inst, polecenie_skrotu(inst, "Dzien_skanera.cmd", "--nowa", "--zamknij-po", "1", "--dane", str(inst.wersja / "moje_sesje")))
    assert wynik.returncode == 1 and "BLAD: katalog sesji" in wynik.stderr, wynik.stdout + wynik.stderr
    assert pliki(inst.wersja) == przed and len(list(inst.sesje.iterdir())) == 1


def test_p1_katalog_sesji_w_wersjach_odrzucany_tylko_w_instalacji(inst, monkeypatch, tmp_path):
    """``sprawdz_katalog_sesji``: z kopii repo niczego nie odrzuca (zachowanie jak dotad); w instalacji odrzuca katalog
    wewnatrz ``<instalacja>/wersje`` (takze sam katalog ``wersje``), a przyjmuje katalog danych instalacji i katalog obcy."""
    w_wersji = inst.program / "dane" / "dzien_skanera"
    assert R.sprawdz_katalog_sesji(w_wersji) == w_wersji and R.sprawdz_katalog_sesji(R.KATALOG_SESJI) == R.KATALOG_SESJI  # repo
    monkeypatch.setattr(UST, "KORZEN", inst.program)
    for zly in (w_wersji, inst.kat / "wersje", inst.kat / "wersje" / "0.3.1" / "program" / "dane" / "dzien_skanera",
                inst.kat / "dane" / ".." / "wersje" / "x"):
        with pytest.raises(R.BladKataloguSesji, match="lezy w katalogu wersji programu"):
            R.sprawdz_katalog_sesji(zly)
    for dobry in (inst.sesje, tmp_path / "gdzie_indziej", inst.kat / "wersje_stare"):
        assert R.sprawdz_katalog_sesji(dobry) == dobry

    class A:
        sesja, nowa, dane, folder = None, True, w_wersji, None

    ust, plik, _ = R.wczytaj_ustawienia_bezpiecznie(inst.ustawienia)
    with pytest.raises(R.BladKataloguSesji):  # wybierz_sesje odrzuca katalog, zanim cokolwiek w nim powstanie
        DS.wybierz_sesje(A, ust, None, plik_ustawien=plik)
    assert not (inst.program / "dane").exists()
    A.sesja = tmp_path / "nie_ma_takiej_sesji"  # wznowienie wskazanej sesji (--sesja) nie przechodzi przez te kontrole
    with pytest.raises(Exception) as blad:
        DS.wybierz_sesje(A, ust, None, plik_ustawien=plik)
    assert not isinstance(blad.value, R.BladKataloguSesji)


def test_p2_wlasne_dane_przy_skrocie_maja_pierwszenstwo(inst, tmp_path):
    """P2: ``--dane`` ze skrotu stoi PRZED opcjami czlowieka, wiec ``Dzien_skanera.cmd --dane X`` dalej zapisuje sesje w X."""
    wiersz = next(w for w in (WZORY / "Dzien_skanera.cmd").read_text(encoding="ascii").splitlines() if w.startswith('"%W%'))
    assert wiersz.endswith(r'--ustawienia "%KAT%ustawienia.toml" --dane "%KAT%dane\dzien_skanera" %*')
    inne = tmp_path / "inne_sesje"
    wynik = uruchom(inst, polecenie_skrotu(inst, "Dzien_skanera.cmd", "--nowa", "--zamknij-po", "1", "--dane", str(inne)))
    assert wynik.returncode == 0, wynik.stdout + wynik.stderr
    assert len([p for p in inne.iterdir() if p.is_dir()]) == 1 and not inst.sesje.exists()


def test_p1_pomiar_bez_pliku_ustawien_instalacji_wskazuje_plik_instalacji(inst, skan, tmp_path):
    """P1: pomiar szczegolowy w instalacji bez ``<instalacja>/ustawienia.toml`` - kod 2 i komunikat o pliku INSTALACJI oraz
    ``zainstaluj.cmd``; nie radzi zalozenia ``ustawienia.toml`` w katalogu wersji i nie czyta pliku, ktory tam lezy."""
    narzedzie = r"narzedzia\pomiar_skanu\pomiar_skanu.py"
    inst.ustawienia.rename(inst.kat / "ustawienia_odlozone.toml")
    for z_plikiem_w_wersji in (False, True):
        if z_plikiem_w_wersji:
            shutil.copy(inst.kat / "ustawienia_odlozone.toml", inst.program / "ustawienia.toml")
        wynik = uruchom(inst, polecenie_skrotu(inst, "Polecenie.cmd", narzedzie, str(skan), "--bez-plytki", "--wyj", str(tmp_path / "w")))
        assert wynik.returncode == 2 and "Traceback" not in wynik.stderr, wynik.stdout + wynik.stderr
        blad = wynik.stderr.strip()
        assert blad.startswith("blad: ustawienia: brak pliku ustawien instalacji") and str(inst.ustawienia) in blad and "zainstaluj.cmd" in blad
        assert str(inst.program) not in blad and "skopiuj" not in blad and "przyklad" not in blad
        assert "wczytuje" not in wynik.stdout and not (tmp_path / "w").exists()


def test_d1_kazdy_wzor_skrotu_instalatora_jest_wymagany_przy_budowie_paczki():
    """Uwaga D1 recenzji: paczka bez ktoregos wzoru skrotu zatrzymalaby instalacje dopiero w kroku [8/9] - budowa ma ja odrzucic."""
    import zbuduj_wydanie

    assert len(I.WZORY_SKRYPTOW) == 6
    assert {"instalacja/wzory/" + nazwa for nazwa in I.WZORY_SKRYPTOW} <= set(zbuduj_wydanie.WYMAGANE)
    assert all((WZORY / nazwa).is_file() for nazwa in I.WZORY_SKRYPTOW)


def test_okno_testowe_decyzje_w_danych_instalacji(inst, monkeypatch):
    """POTRZEBUJE 5 z etapu B1: ``ui_test.py`` w instalacji pisal ``dane/decyzje.csv`` do katalogu wersji. Ten sam mechanizm
    rozpoznania instalacji co "Dzien skanera": ``<instalacja>/dane/decyzje.csv``; z repo jak dotad."""
    from PySide6.QtWidgets import QApplication

    from stanowisko import ui_test

    app = QApplication.instance() or QApplication([])  # noqa: F841
    assert ui_test.plik_decyzji_domyslny() == ui_test.PLIK_DECYZJI == UST.KORZEN / "dane" / "decyzje.csv"  # repo
    ust = UST.wczytaj_ustawienia(inst.ustawienia)
    monkeypatch.setattr(UST, "KORZEN", inst.program)
    assert ui_test.plik_decyzji_domyslny() == inst.kat / "dane" / "decyzje.csv"
    okno = ui_test.Okno(ust)
    try:
        assert okno.plik_decyzji == inst.kat / "dane" / "decyzje.csv"
    finally:
        okno.close()
