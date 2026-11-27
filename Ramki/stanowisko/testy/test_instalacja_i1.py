"""E3-I1: Python w paczce, wartosci z okna instalatora w ustawieniach, ikony bez konsoli, starter - instalator i budowa paczki.

Male paczki w tmp_path (jak ``test_instalacja.py``); srodowisko wersji = ``SrodowiskoAtrapa`` poza testami startera i skrotow
(prawdziwy ``python -m venv --without-pip``, ulamek sekundy). Python w paczce to w testach atrapa (pakiet nuget z kilkoma
plikami, suma podana wprost) - prawdziwy pakiet sprawdzaja proby K1-K5 raportu E3-I1.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import subprocess
import sys
import time
import tomllib
import zipfile
from pathlib import Path

import pytest

from instalacja import instalator as I
from stanowisko import ustawienia as UST
import zbuduj_wydanie as ZW
from test_instalacja import PYTHON, SrodowiskoAtrapa, Stanowisko, sha
from test_zbuduj_wydanie import DATA, STANOWISKO, drzewo_programu, kola_testowe, kolo

WZOR = (STANOWISKO / "ustawienia.przyklad.toml").read_bytes()


# ------------------------------------------------------------------------------------------------------- atrapy paczki

def nupkg(katalog: Path) -> tuple[Path, str]:
    """Atrapa pakietu nuget "python": tools/ z plikami, ktorych wymaga budowa (python.exe to NIE jest prawdziwy Python)."""
    katalog.mkdir(parents=True, exist_ok=True)
    plik = katalog / ZW.PYTHON_NUGET_PLIK
    with zipfile.ZipFile(plik, "w") as z:
        for nazwa, tresc in (("python.nuspec", "<package/>"), ("tools/python.exe", "atrapa python.exe"), ("tools/pythonw.exe", "atrapa pythonw"),
                             ("tools/python312.dll", "dll"), ("tools/Lib/venv/__init__.py", "# venv\n"),
                             ("tools/Lib/ensurepip/__init__.py", "# ensurepip\n"), ("tools/DLLs/_ssl.pyd", "pyd")):
            z.writestr(zipfile.ZipInfo(nazwa, date_time=(2026, 11, 25, 12, 0, 0)), tresc)
    return plik, sha(plik)


def kola_okna(katalog: Path) -> list[str]:
    """Atrapy kol shiboken6 i pyside6_essentials (pliki z wycinka okna i pliki spoza niego); dopisuje je do listy zamrozonej."""
    katalog.mkdir(parents=True, exist_ok=True)
    tresci = {"shiboken6-6.12.0-cp310-abi3-win_amd64.whl": ["shiboken6/__init__.py", "shiboken6/Shiboken.pyd", "shiboken6/shiboken6.abi3.dll",
                                                            "shiboken6/shiboken6.abi3.lib", "shiboken6/include/shiboken6/x.h",
                                                            "shiboken6/Shiboken.pyi", "shiboken6-6.12.0.dist-info/METADATA"],
              "pyside6_essentials-6.12.0-cp310-abi3-win_amd64.whl": ["PySide6/__init__.py", "PySide6/_config.py", "PySide6/QtCore.pyd",
                                                                     "PySide6/QtGui.pyd", "PySide6/QtWidgets.pyd", "PySide6/QtQml.pyd",
                                                                     "PySide6/Qt6Core.dll", "PySide6/Qt6Gui.dll", "PySide6/Qt6Widgets.dll",
                                                                     "PySide6/Qt6Quick.dll", "PySide6/pyside6.abi3.dll", "PySide6/msvcp140.dll",
                                                                     "PySide6/opengl32sw.dll", "PySide6/designer.exe",
                                                                     "PySide6/plugins/platforms/qwindows.dll", "PySide6/plugins/platforms/qminimal.dll",
                                                                     "PySide6/plugins/styles/qmodernwindowsstyle.dll",
                                                                     "pyside6_essentials-6.12.0.dist-info/METADATA"]}
    for nazwa, pliki in tresci.items():
        with zipfile.ZipFile(katalog / nazwa, "w") as z:
            for p in pliki:
                z.writestr(zipfile.ZipInfo(p, date_time=(2026, 11, 25, 12, 0, 0)), f"atrapa {p}")
    return ["shiboken6==6.12.0", "PySide6_Essentials==6.12.0"]


def zrodlo_z_oknem(tmp: Path) -> tuple[Path, Path]:
    zrodlo, kola = drzewo_programu(tmp / "zrodlo"), kola_testowe(tmp / "kola")
    lista = zrodlo / "instalacja" / "zamrozone.txt"
    lista.write_text(lista.read_text(encoding="ascii") + "\n".join(kola_okna(kola)) + "\n", encoding="ascii")
    return zrodlo, kola


def paczka_z_pythonem(tmp: Path, wersja: str = "1.0") -> Path:
    zrodlo, kola = zrodlo_z_oknem(tmp)
    plik, suma = nupkg(tmp / "nuget")
    wynik = ZW.zbuduj(tmp / "wyjscie", kola, wersja=wersja, zrodlo=zrodlo, data=DATA, python_nuget=plik, python_sha256=suma)
    with zipfile.ZipFile(wynik["plik"]) as z:
        z.extractall(tmp / "paczka")
    return tmp / "paczka"


class SrodowiskoZapis(SrodowiskoAtrapa):
    """Atrapa srodowiska, ktora zapamietuje interpreter bazowy (``python -m venv`` dostalby go jako pierwszy argument)."""

    def __init__(self):
        super().__init__()
        self.bazowe = []

    def utworz(self, python, venv):
        self.bazowe.append(Path(python))
        super().utworz(python, venv)
        (venv / "pyvenv.cfg").write_text(f"home = {Path(python).parent}\nversion = 3.12.10\n", encoding="utf-8")

    def instaluj(self, venv, katalogi_kol, lista, dziennik_pip):
        """Jak atrapa, ale kolo szukane po nazwie znormalizowanej (pyside6_essentials -> pyside6-essentials)."""
        pakiety = json.loads((venv / "pakiety.json").read_text(encoding="ascii"))
        dostepne = {ZW.kolo_zgodne(p.name) for k in katalogi_kol for p in Path(k).glob("*.whl")}
        for nazwa, wersja in I.wczytaj_liste_zamrozona(lista).items():
            assert (nazwa, wersja) in dostepne, f"brak kola {nazwa}"
            pakiety[nazwa] = wersja
        (venv / "pakiety.json").write_text(json.dumps(pakiety), encoding="ascii")


def atrapa_pythona_paczki(monkeypatch) -> list:
    """Python paczki jest w testach atrapa (nie da sie go uruchomic): kontrola wersji i zapytanie programu ida przez
    interpreter testow. Zwraca liste interpreterow, ktore instalator chcial uruchomic."""
    wolane = []
    prawdziwe_zapytanie = I.zapytaj_program

    def sprawdz(python, wymagana="3.12"):
        wolane.append(Path(python))
        return "3.12.10"

    monkeypatch.setattr(I, "sprawdz_pythona", sprawdz)
    monkeypatch.setattr(I, "zapytaj_program", lambda python, program, ustawienia=None: prawdziwe_zapytanie(PYTHON, program, ustawienia))
    return wolane


# ------------------------------------------------------------------------------------------------------ budowa paczki

def test_paczka_z_pythonem_i_oknem(tmp_path):
    zrodlo, kola = zrodlo_z_oknem(tmp_path)
    plik, suma = nupkg(tmp_path / "nuget")
    a = ZW.zbuduj(tmp_path / "a", kola, zrodlo=zrodlo, data=DATA, python_nuget=plik, python_sha256=suma)
    b = ZW.zbuduj(tmp_path / "b", kola, zrodlo=zrodlo, data=DATA, python_nuget=plik, python_sha256=suma)
    assert a["sha256"] == b["sha256"]  # powtarzalnosc bajtowa zostaje
    assert a["pliki_pythona"] == 6 and a["pliki_okna"] > 0
    with zipfile.ZipFile(a["plik"]) as z:
        nazwy = set(z.namelist())
        wydanie = json.loads(z.read("wydanie.json"))
        instaluj = z.read("Instaluj.cmd")
        czytaj = z.read("CZYTAJ.txt").decode("ascii")
    assert {"python/python.exe", "python/pythonw.exe", "python/Lib/venv/__init__.py", "python/DLLs/_ssl.pyd"} <= nazwy
    assert "python/python.nuspec" not in nazwy and not [n for n in nazwy if n.startswith("tools/")]  # tylko katalog tools/ pakietu
    okno = sorted(n[len("okno/"):] for n in nazwy if n.startswith("okno/"))
    assert okno == ["PySide6/Qt6Core.dll", "PySide6/Qt6Gui.dll", "PySide6/Qt6Widgets.dll", "PySide6/QtCore.pyd", "PySide6/QtGui.pyd",
                    "PySide6/QtWidgets.pyd", "PySide6/__init__.py", "PySide6/_config.py", "PySide6/msvcp140.dll",
                    "PySide6/plugins/platforms/qwindows.dll", "PySide6/plugins/styles/qmodernwindowsstyle.dll", "PySide6/pyside6.abi3.dll",
                    "shiboken6/Shiboken.pyd", "shiboken6/__init__.py", "shiboken6/shiboken6.abi3.dll"]  # bez QML, Quick, narzedzi, .lib, .pyi
    assert b"\r\n" in instaluj and b"\n" not in instaluj.replace(b"\r\n", b"")  # skrypt Windows z CRLF
    assert "Instaluj.cmd" in czytaj and "Python jest w paczce" in czytaj
    assert wydanie["python_w_paczce"] == {"wersja": "3.12.10", "zrodlo": "nuget.org pakiet python 3.12.10 (katalog tools)",
                                          "plik": ZW.PYTHON_NUGET_PLIK, "sha256": suma, "pliki": 6}
    assert wydanie["okno_instalatora"]["kola"] == ["shiboken6-6.12.0-cp310-abi3-win_amd64.whl",
                                                   "pyside6_essentials-6.12.0-cp310-abi3-win_amd64.whl"]
    # paczka BEZ Pythona (proby) - wydanie.json bez nowych kluczy, bez okna i Instaluj.cmd
    c = ZW.zbuduj(tmp_path / "c", kola, zrodlo=zrodlo, data=DATA)
    with zipfile.ZipFile(c["plik"]) as z:
        assert "python_w_paczce" not in json.loads(z.read("wydanie.json"))
        assert not [n for n in z.namelist() if n.startswith(("python/", "okno/")) or n == "Instaluj.cmd"]


def test_suma_pakietu_pythona_musi_byc_przypieta(tmp_path):
    zrodlo, kola = zrodlo_z_oknem(tmp_path)
    plik, suma = nupkg(tmp_path / "nuget")
    with pytest.raises(ZW.BladBudowy, match="inna niz przypieta"):
        ZW.zbuduj(tmp_path / "a", kola, zrodlo=zrodlo, data=DATA, python_nuget=plik)  # suma domyslna = prawdziwy pakiet
    plik.with_name(plik.name + ".sha256").write_text("0" * 64 + "  " + plik.name + "\n", encoding="ascii")
    with pytest.raises(ZW.BladBudowy, match="niezgodna z pakietem"):
        ZW.zbuduj(tmp_path / "a", kola, zrodlo=zrodlo, data=DATA, python_nuget=plik, python_sha256=suma)
    with pytest.raises(ZW.BladBudowy, match="pobierz go: --pobierz-pythona"):
        ZW.zbuduj(tmp_path / "a", kola, zrodlo=zrodlo, data=DATA, python_nuget=tmp_path / "brak.nupkg", python_sha256=suma)
    assert not list((tmp_path / "a").glob("*.zip")) if (tmp_path / "a").exists() else True
    # wiersz polecen: domyslnie wymaga pakietu Pythona (<wyjscie>/python_nuget); --bez-pythona tylko do prob
    argumenty = ["--wyjscie", str(tmp_path / "wy"), "--kola", str(kola), "--zrodlo", str(zrodlo), "--data", "2026-11-20T12:00:00"]
    assert ZW.main(argumenty) == 1
    assert ZW.main(argumenty + ["--bez-pythona"]) == 0


def test_okno_wymaga_kol_qt(tmp_path):
    zrodlo, kola = drzewo_programu(tmp_path / "zrodlo"), kola_testowe(tmp_path / "kola")  # lista bez shiboken6 / PySide6
    plik, suma = nupkg(tmp_path / "nuget")
    with pytest.raises(ZW.BladBudowy, match="brak kola shiboken6"):
        ZW.zbuduj(tmp_path / "a", kola, zrodlo=zrodlo, data=DATA, python_nuget=plik, python_sha256=suma)
    (zrodlo / "instalacja" / "Instaluj.cmd").unlink()
    with pytest.raises(ZW.BladBudowy, match="instalacja/Instaluj.cmd"):
        ZW.zbuduj(tmp_path / "a", kola, zrodlo=zrodlo, data=DATA, python_nuget=plik, python_sha256=suma)
    assert ZW.zbuduj(tmp_path / "b", kola, zrodlo=zrodlo, data=DATA)["pliki_okna"] == 0  # bez Pythona okno niewymagane


def test_pobierz_pythona_sprawdza_sume_bez_sieci(tmp_path, monkeypatch):
    tresc = b"pakiet nuget"
    monkeypatch.setattr(ZW.urllib.request, "urlopen", lambda url, timeout: io.BytesIO(tresc))
    plik = ZW.pobierz_pythona(tmp_path / "n", sha_oczekiwana=hashlib.sha256(tresc).hexdigest())
    assert plik.read_bytes() == tresc and plik.name == ZW.PYTHON_NUGET_PLIK
    assert plik.with_name(plik.name + ".sha256").read_text(encoding="ascii") == f"{hashlib.sha256(tresc).hexdigest()}  {plik.name}\n"
    with pytest.raises(ZW.BladBudowy, match="inna sume"):
        ZW.pobierz_pythona(tmp_path / "m", sha_oczekiwana="0" * 64)
    assert not list((tmp_path / "m").iterdir())  # plik o zlej sumie nie zostaje
    assert ZW.PYTHON_NUGET_URL.startswith("https://api.nuget.org/") and len(ZW.PYTHON_NUGET_SHA256) == 64


# ------------------------------------------------------------------------------------------- ustawienia z okna

def test_ustawienia_ze_wzoru_z_wartosciami_okna(tmp_path):
    osoby = ['Anna "Ania" Kowalska', "\u0141ukasz \u017b.", "C:\\dziwne"]
    tekst = I.ustawienia_ze_wzoru(WZOR, tmp_path / "Stanowisko", {("sciezki", "folder_eksportu_skanera"): "D:/Skany",
                                                                  ("sciezki", "folder_cyrkon"): "E:/Projekty exocad",
                                                                  ("sesja", "operatorzy"): osoby,
                                                                  ("ramki", "wlaczone"): False}).decode("utf-8")
    d = tomllib.loads(tekst)
    assert d["sciezki"]["folder_eksportu_skanera"] == "D:/Skany" and d["sciezki"]["folder_cyrkon"] == "E:/Projekty exocad"
    assert d["sesja"]["operatorzy"] == osoby and d["ramki"]["wlaczone"] is False
    assert d["sciezki"]["baza"] == (tmp_path / "Stanowisko").resolve().as_posix() + "/dane/stanowisko.sqlite"  # jak dotad
    wiersz = next(w for w in tekst.splitlines() if w.startswith("folder_eksportu_skanera"))
    assert wiersz.endswith("# obserwowany przez modul scanner (do potwierdzenia: Order Save Path)") or "#" in wiersz  # komentarz zostaje
    # E3-R1: wzor ma wiersz "wlaczone = true  # ..." - wartosc zamieniona w miejscu, komentarz (jak wlaczyc ramki) zostaje
    wzor_ramki = next(w for w in WZOR.decode("utf-8").splitlines() if w.startswith("wlaczone"))
    wiersz_ramki = next(w for w in tekst.splitlines() if w.startswith("wlaczone"))
    assert wiersz_ramki == wzor_ramki.replace("wlaczone = true", "wlaczone = false", 1) and "#" in wiersz_ramki
    # klucza, ktorego we wzorze nie ma (wzor sprzed E3-R1): wiersz zaraz pod naglowkiem sekcji
    bez = "".join(w for w in WZOR.decode("utf-8").splitlines(keepends=True) if not w.startswith("wlaczone")).encode("utf-8")
    tekst_bez = I.ustawienia_ze_wzoru(bez, tmp_path / "Stanowisko", {("ramki", "wlaczone"): False}).decode("utf-8")
    assert tekst_bez.splitlines()[tekst_bez.splitlines().index("[ramki]") + 1] == "wlaczone = false"
    # bez wartosci: dokladnie to, co dawala wersja sprzed E3-I1 (zmiana tylko sciezek wzglednych)
    assert I.ustawienia_ze_wzoru(WZOR, tmp_path) == I.ustawienia_ze_wzoru(WZOR, tmp_path, {})
    pusty = tomllib.loads(I.ustawienia_ze_wzoru(WZOR, tmp_path, {}).decode("utf-8"))
    assert pusty["sciezki"]["folder_eksportu_skanera"] == "C:/Aidite/Scandata" and pusty["sesja"]["operatorzy"] == []
    # wynik z folderami i osobami (bez klucza, ktorego program nie zna) przyjmuje kod programu
    plik = tmp_path / "ustawienia.toml"
    plik.write_bytes(I.ustawienia_ze_wzoru(WZOR, tmp_path, {("sciezki", "folder_eksportu_skanera"): "D:/Skany", ("sesja", "operatorzy"): osoby}))
    assert UST.wczytaj_ustawienia(plik)["sesja"]["operatorzy"] == osoby
    assert I.wartosc_toml("a\tb\x01") == '"a\\u0009b\\u0001"' and tomllib.loads("x = " + I.wartosc_toml("a\tb\x01"))["x"] == "a\tb\x01"


def test_wartosci_okna_trafiaja_tylko_do_nowego_pliku_ustawien(st, tmp_path, capsys):
    skany = tmp_path / "Skany"
    skany.mkdir()
    paczka = __import__("test_zbuduj_wydanie").zbuduj_paczke(tmp_path, "1.0")
    kod = st.zainstaluj(paczka, folder_skanow=str(skany), folder_projektow="", osoby=["Anna", "Piotr"], ramki_wylaczone=True)
    wyjscie = capsys.readouterr().out
    assert kod == 0, wyjscie  # foldery istnieja (projekty: pusty folder w danych) - od razu GOTOWA, bez etapu WSTRZYMANA
    ust = UST.wczytaj_ustawienia(st.katalog / "ustawienia.toml")
    assert ust["sciezki"]["folder_eksportu_skanera"] == skany.as_posix()
    assert ust["sciezki"]["folder_cyrkon"] == (st.katalog.resolve() / "dane" / "projekty").as_posix()
    assert (st.katalog / "dane" / "projekty").is_dir() and ust["sesja"]["operatorzy"] == ["Anna", "Piotr"]
    assert "folder projektow nie wybrany" in wyjscie
    # E3-R1: program zna przelacznik ramek - NOWA instalacja wpisuje [ramki] wlaczone = false (pokaz bez elektroniki ramek)
    assert ust["ramki"]["wlaczone"] is False and "ramki wylaczone ([ramki] wlaczone = false)" in st.dziennik()
    assert "nie ma przelacznika ramek" not in st.dziennik()
    # druga instalacja (aktualizacja) z innym wyborem: istniejacy plik zostaje bajt w bajt, a ekran mowi, ze wybor nie zostal wpisany
    suma = sha(st.katalog / "ustawienia.toml")
    assert st.zainstaluj(__import__("test_zbuduj_wydanie").zbuduj_paczke(tmp_path, "2.0"), folder_skanow="X:/inne", osoby=["Ktos"],
                         ramki_wylaczone=True) == 0
    assert sha(st.katalog / "ustawienia.toml") == suma and "NIE zostaly wpisane" in capsys.readouterr().out


def test_ramki_wylaczone_gdy_program_zna_przelacznik(st, tmp_path):
    """E3-R1: program z paczki zna klucz [ramki] wlaczone (instalator pyta o to kod programu z paczki) - bez podmiany kodu."""
    from test_zbuduj_wydanie import zbuduj_paczke

    skany = tmp_path / "Skany"
    skany.mkdir()
    paczka = zbuduj_paczke(tmp_path, "1.0")
    dane = I.zapytaj_program(PYTHON, paczka / "program")
    assert "wlaczone" in dane["klucze_ramek"] and "port" in dane["klucze_ramek"]
    wartosci, uwagi = I._wartosci_z_okna(PYTHON, paczka, st.katalog, str(skany), str(skany), ["A"], True)
    assert wartosci[("ramki", "wlaczone")] is False and "ramki wylaczone ([ramki] wlaczone = false)" in uwagi
    wartosci, uwagi = I._wartosci_z_okna(PYTHON, paczka, st.katalog, str(skany), str(skany), ["A"], False)
    assert ("ramki", "wlaczone") not in wartosci and not [u for u in uwagi if "ramk" in u]  # bez wyboru: wzor (true)


def test_ramki_wylaczone_gdy_program_nie_zna_przelacznika(st, tmp_path):
    """Runda 2 (D3): program z paczki starszy niz E3-R1 (``SCHEMAT["ramki"]`` bez ``wlaczone`` - instalator pyta o to kod programu
    z paczki): wybor "ramki wylaczone" NIE trafia do pliku (program odrzucilby nieznany klucz), uwaga mowi, ze program sprobuje
    polaczyc sie z ramkami."""
    from test_zbuduj_wydanie import zbuduj_paczke

    skany = tmp_path / "Skany"
    skany.mkdir()
    paczka = zbuduj_paczke(tmp_path, "1.0")
    ust_py = paczka / "program" / "stanowisko" / "ustawienia.py"
    wiersze = ust_py.read_text(encoding="utf-8").splitlines(keepends=True)
    bez = [w for w in wiersze if not w.lstrip().startswith('"wlaczone": (bool')]
    assert len(bez) == len(wiersze) - 1
    ust_py.write_text("".join(bez), encoding="utf-8")
    dane = I.zapytaj_program(PYTHON, paczka / "program")
    assert "wlaczone" not in dane["klucze_ramek"] and "port" in dane["klucze_ramek"]
    wartosci, uwagi = I._wartosci_z_okna(PYTHON, paczka, st.katalog, str(skany), str(skany), ["A"], True)
    assert ("ramki", "wlaczone") not in wartosci and "ramki wylaczone ([ramki] wlaczone = false)" not in uwagi
    assert [u for u in uwagi if "ramk" in u] == ["ta wersja programu nie ma przelacznika ramek ([ramki] wlaczone) - program sprobuje "
                                                "polaczyc sie z ramkami"]


def test_r1_aktualizacja_starej_instalacji_bez_klucza_plik_bez_zmian_ramki_wlaczone(st, tmp_path):
    """E3-R1: instalacja sprzed przelacznika (ustawienia.toml bez klucza wlaczone) - aktualizacja nie dopisuje klucza (plik bajt
    w bajt), program czyta brak klucza jako ramki wlaczone (jak dotad, bez kodu 7)."""
    from test_zbuduj_wydanie import zbuduj_paczke

    assert st.zainstaluj(zbuduj_paczke(tmp_path, "1.0")) in (0, I.KOD_WSTRZYMANA)
    plik = st.katalog / "ustawienia.toml"
    stary = "".join(w for w in plik.read_text(encoding="utf-8").splitlines(keepends=True) if not w.startswith("wlaczone"))
    plik.write_text(stary, encoding="utf-8")
    suma = sha(plik)
    kod = st.zainstaluj(zbuduj_paczke(tmp_path, "2.0"), ramki_wylaczone=True)
    assert kod in (0, I.KOD_WSTRZYMANA) and kod != I.KOD_USTAWIENIA and sha(plik) == suma
    ust = UST.wczytaj_ustawienia(plik)
    assert ust["ramki"]["wlaczone"] is True and UST.ramki_wlaczone(ust)


# ---------------------------------------------------------------------------------------------------- Python z paczki

def test_python_z_paczki_kopiowany_do_katalogu_instalacji(st, tmp_path, monkeypatch, capsys):
    wolane = atrapa_pythona_paczki(monkeypatch)
    st.srodowisko = SrodowiskoZapis()
    st.ustawienia_gotowe()
    paczka = paczka_z_pythonem(tmp_path)
    assert st.zainstaluj(paczka, python_z_paczki=True) == 0, capsys.readouterr().out
    kopia = st.katalog / "python" / "3.12.10"
    assert (kopia / "python.exe").read_bytes() == (paczka / "python" / "python.exe").read_bytes()
    assert sorted(p.relative_to(kopia).as_posix() for p in kopia.rglob("*") if p.is_file()) == \
        sorted(p.relative_to(paczka / "python").as_posix() for p in (paczka / "python").rglob("*") if p.is_file())
    assert wolane == [paczka.resolve() / "python" / "python.exe"]  # kontrola wersji: Python paczki
    assert st.srodowisko.bazowe == [st.katalog.resolve() / "python" / "3.12.10" / "python.exe"]  # srodowisko: KOPIA w katalogu instalacji
    assert I.python_bazowy_wersji(st.katalog, "1.0") == kopia.resolve()
    assert "sumy zgodne 6 z 6" in capsys.readouterr().out
    # ponowna instalacja: kopia zgodna - nic nie jest kopiowane; plik uszkodzony - tylko on wraca
    assert st.zainstaluj(paczka, python_z_paczki=True) == 0
    assert "skopiowano plikow: 0" in capsys.readouterr().out
    (kopia / "DLLs" / "_ssl.pyd").write_bytes(b"zepsuty")
    assert st.zainstaluj(paczka, python_z_paczki=True) == 0
    assert "skopiowano plikow: 1" in capsys.readouterr().out and (kopia / "DLLs" / "_ssl.pyd").read_bytes() == b"pyd"


def test_python_z_paczki_bez_pythona_w_paczce_to_blad_paczki(st, tmp_path, monkeypatch, capsys):
    from test_zbuduj_wydanie import zbuduj_paczke

    atrapa_pythona_paczki(monkeypatch)
    st.ustawienia_gotowe()
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "1.0"), python_z_paczki=True) == I.KOD_PACZKA
    assert "paczka nie zawiera Pythona" in capsys.readouterr().out and not (st.katalog / "wersje").exists()


def test_python_z_paczki_brak_zapisu_to_kod_6_bez_zmiany_wersji(st, tmp_path, monkeypatch, capsys):
    atrapa_pythona_paczki(monkeypatch)
    st.srodowisko = SrodowiskoZapis()
    st.ustawienia_gotowe()
    paczka = paczka_z_pythonem(tmp_path)
    prawdziwe = I.shutil.copyfile

    def odmowa(a, b, *args, **kw):
        if "python" in Path(b).parts:
            raise PermissionError(13, "Odmowa dostepu")
        return prawdziwe(a, b, *args, **kw)

    monkeypatch.setattr(I.shutil, "copyfile", odmowa)
    assert st.zainstaluj(paczka, python_z_paczki=True) == I.KOD_INSTALACJA
    wyjscie = capsys.readouterr().out
    assert "nie mozna skopiowac Pythona" in wyjscie and st.biezaca is None and st.srodowisko.bazowe == []


# ------------------------------------------------------------------------------------------------- skroty i starter

def _prawdziwa_wersja(katalog: Path, wersja: str, aplikacja: str) -> Path:
    """Katalog instalacji z wersja o PRAWDZIWYM srodowisku (``python -m venv --without-pip``) i atrapa programu."""
    kw = katalog / "wersje" / wersja
    (kw / "program" / "stanowisko").mkdir(parents=True)
    (kw / "program" / "stanowisko" / "__init__.py").write_text("", encoding="ascii")
    (kw / "program" / "stanowisko" / "aplikacja.py").write_text(aplikacja, encoding="utf-8")
    (kw / "program" / "stanowisko" / "dzien_skanera.py").write_text(aplikacja, encoding="utf-8")
    wynik = subprocess.run([sys.executable, "-I", "-m", "venv", "--copies", "--without-pip", str(kw / "venv")], capture_output=True, text=True,
                           stdin=subprocess.DEVNULL, timeout=300)
    assert wynik.returncode == 0, wynik.stderr
    (katalog / "wersja_biezaca.txt").write_bytes(f"{wersja}\r\n".encode("ascii"))
    (katalog / I.WZOR_STARTU).write_bytes((STANOWISKO / "instalacja" / "wzory" / I.WZOR_STARTU).read_bytes())
    (katalog / "ustawienia.toml").write_text("[sciezki]\n", encoding="ascii")
    return kw


ATRAPA_PROGRAMU = '''import os, sys
print("START", sys.argv[1:], "PREFIX", sys.prefix)
print("ZMIENNE", os.environ.get("PYTHONPATH"), os.environ.get("PYTHONUTF8"), os.environ.get("PYTHONDONTWRITEBYTECODE"))
print("CWD", os.getcwd())
sys.exit(int(os.environ.get("ATRAPA_KOD", "0")))
'''


def _starter(katalog: Path, *argumenty: str, **zmienne) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith("PYTHON")}
    env.update(STANOWISKO_START_BEZ_OKIENEK="1", PYTHONPATH=str(STANOWISKO), **zmienne)
    return subprocess.run([sys.executable, "-I", "-B", str(katalog / I.WZOR_STARTU), *argumenty], capture_output=True, text=True,
                          stdin=subprocess.DEVNULL, env=env, timeout=300)


@pytest.mark.skipif(os.name != "nt", reason="starter i srodowisko wersji: Windows")
def test_starter_bez_konsoli_uruchamia_wersje_biezaca(tmp_path):
    katalog = tmp_path / "Kat alog"
    kw = _prawdziwa_wersja(katalog, "1.0", ATRAPA_PROGRAMU)
    wynik = _starter(katalog, "stanowisko", "--atrapa", "--zamknij-po", "1")
    assert wynik.returncode == 0, wynik.stderr
    log = (katalog / "dane" / "ostatni_start_stanowisko.txt").read_text(encoding="utf-8")
    assert f"START ['--ustawienia', '{katalog / 'ustawienia.toml'}', '--atrapa', '--zamknij-po', '1']".replace("\\", "\\\\") in log
    assert str(kw / "venv").lower() in log.lower()  # interpreter srodowiska wersji
    assert "ZMIENNE None 1 1" in log and f"CWD {kw / 'program'}" in log  # bez PYTHONPATH z zewnatrz, katalog programu
    wynik = _starter(katalog, "dzien_skanera", "--nowa")
    log = (katalog / "dane" / "ostatni_start_dzien_skanera.txt").read_text(encoding="utf-8")
    assert wynik.returncode == 0 and str(katalog / "dane" / "dzien_skanera").replace("\\", "\\\\") in log and "'--nowa'" in log
    # kod bledu programu: komunikat (w probach na stderr zamiast okienka) z plikiem wyjscia; kod 3 "Stanowisko" = juz dziala, bez komunikatu
    wynik = _starter(katalog, "stanowisko", ATRAPA_KOD="5")
    assert wynik.returncode == 5 and "zakonczyl sie bledem (kod 5)" in wynik.stderr and "ostatni_start_stanowisko.txt" in wynik.stderr
    wynik = _starter(katalog, "stanowisko", ATRAPA_KOD="3")
    assert wynik.returncode == 3 and wynik.stderr == ""
    # D3 recenzji PR #63: kolejny start (np. drugi dwuklik, gdy program juz dziala - kod 3) DOPISUJE do pliku wyjscia,
    # nie obcina wyjscia wczesniejszego startu; kazdy start ma naglowek
    log = (katalog / "dane" / "ostatni_start_stanowisko.txt").read_text(encoding="utf-8")
    assert log.count("==== start ") == 3 and "'--atrapa', '--zamknij-po', '1']" in log and "zakonczyl" not in log
    assert log.index("'--zamknij-po', '1']") < log.rindex("==== start ")
    assert _starter(katalog, "inny").returncode == 2
    (kw / "NIEDOKONCZONA.txt").write_text("x", encoding="ascii")
    wynik = _starter(katalog, "stanowisko")
    assert wynik.returncode == 4 and "nie ma gotowej wersji" in wynik.stderr


def _cel_skrotu(lnk: Path) -> tuple[str, str, str]:
    skrypt = ("$s = (New-Object -ComObject WScript.Shell).CreateShortcut($env:PLIK_LNK); "
              "Write-Output $s.TargetPath; Write-Output $s.Arguments; Write-Output $s.WorkingDirectory")
    wynik = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", skrypt], capture_output=True, text=True,
                           env=dict(os.environ, PLIK_LNK=str(lnk)), stdin=subprocess.DEVNULL, timeout=120)
    assert wynik.returncode == 0 and wynik.stdout.strip(), (wynik.returncode, wynik.stdout, wynik.stderr[-800:])
    wiersze = wynik.stdout.splitlines() + ["", "", ""]
    return wiersze[0], wiersze[1], wiersze[2]


@pytest.mark.skipif(os.name != "nt", reason="skroty .lnk: Windows")
@pytest.mark.parametrize("bez_powershell", [False, True], ids=["powershell", "zapis_wlasny"])
def test_ikony_na_pulpicie_przez_starter(tmp_path, monkeypatch, bez_powershell, capsys):
    """Dwie ikony: pythonw.exe interpretera bazowego wersji + starter. Droga zapasowa (polityka blokuje PowerShell / COM):
    plik .lnk zapisany przez instalator - Windows czyta z niego ten sam cel (sprawdzenie: WScript.Shell, podsystem celu,
    uruchomienie wiersza polecen skrotu jako procesu potomnego). Start przez powloke (dwuklik) - proba reczna, instrukcja pkt 8."""
    if bez_powershell:
        monkeypatch.setenv("STANOWISKO_SKROT_BEZ_POWERSHELL", "1")
    katalog = tmp_path / "Stanowisko"
    _prawdziwa_wersja(katalog, "1.0", ATRAPA_PROGRAMU)
    (tmp_path / "pulpit").mkdir()
    skroty = I.utworz_skroty(katalog, tmp_path / "pulpit", I.Dziennik(katalog, "proba"))
    wyjscie = capsys.readouterr().out
    assert sorted(p.name for p in (tmp_path / "pulpit").iterdir()) == ["Dzie\u0144 skanera.lnk", "Stanowisko.lnk"]
    home = I.python_bazowy_wersji(katalog, "1.0")
    assert home is not None and (home / "pythonw.exe").is_file()
    for nazwa, cel, _ in I.SKROTY:
        assert skroty[nazwa] == tmp_path / "pulpit" / f"{nazwa}.lnk" and f"SKROT ZALOZONY: {nazwa} | " in wyjscie
        program, argumenty, roboczy = _cel_skrotu(skroty[nazwa])
        assert Path(program) == home / "pythonw.exe", (program, argumenty, roboczy)
        assert argumenty == f'-I -B "{katalog / I.WZOR_STARTU}" {cel}'
        assert Path(roboczy) == katalog
    # bez okna konsoli: cel skrotu to program okienkowy (podsystem PE "Windows GUI" = 2), nie konsolowy python.exe
    assert _podsystem_pe(Path(_cel_skrotu(skroty["Stanowisko"])[0])) == 2
    # skrot naprawde uruchamia program: wiersz polecen skrotu (cel + argumenty, katalog roboczy - to samo, co sklada powloka
    # przy dwukliku) uruchomiony WPROST jako proces potomny z limitem czasu - bez os.startfile / ShellExecute w procesie testu
    # (recenzja PR #63, P3: w sesji ssh recenzenta 3 z 3 przebiegow z os.startfile skonczylo sie smiercia calej sesji)
    for nazwa, cel, _ in I.SKROTY:
        program, argumenty, roboczy = _cel_skrotu(skroty[nazwa])
        env = {k: v for k, v in os.environ.items() if not k.upper().startswith("PYTHON")}
        wynik = subprocess.run(f'"{program}" {argumenty}', cwd=roboczy, env=dict(env, STANOWISKO_START_BEZ_OKIENEK="1"),
                               stdin=subprocess.DEVNULL, capture_output=True, timeout=120)
        assert wynik.returncode == 0, (nazwa, wynik.returncode, wynik.stderr[-800:])
        log = katalog / "dane" / f"ostatni_start_{cel}.txt"
        assert "START ['--ustawienia'" in log.read_text(encoding="utf-8"), nazwa


def _podsystem_pe(plik: Path) -> int:
    """Pole Subsystem naglowka PE (2 = Windows GUI - bez okna konsoli, 3 = konsola)."""
    dane = plik.read_bytes()[:4096]
    pe = int.from_bytes(dane[0x3C:0x40], "little")
    assert dane[pe:pe + 4] == b"PE\0\0"
    return int.from_bytes(dane[pe + 24 + 68:pe + 24 + 70], "little")


def test_zaden_test_nie_uruchamia_niczego_przez_powloke():
    """P3 recenzji PR #63 (runda 2): zaden test nie uruchamia pliku przez powloke Windows (os.startfile / ShellExecute).
    25.11 20:58 jedno uruchomienie skrotu .lnk przez powloke w sesji ssh -> Bitdefender (Advanced Threat Control, "Atc4.Detection")
    zakonczyl CALE drzewo procesow sesji i wzial do kwarantanny pliki tego drzewa (takze plik .cmd, ktory sesje uruchomil,
    i pliki testow) - raport E3-I1, Runda 2. Start skrotu sprawdza test_ikony_na_pulpicie_przez_starter bez powloki."""
    zakazane = ("os." + "startfile(", "Shell" + "Execute")
    znalezione = []
    for plik in sorted((STANOWISKO / "testy").rglob("*.py")):
        for nr, wiersz in enumerate(plik.read_text(encoding="utf-8").splitlines(), 1):
            kod = wiersz.split("#", 1)[0]
            if any(z in kod for z in zakazane):
                znalezione.append(f"{plik.name}:{nr}: {wiersz.strip()}")
    assert znalezione == []


def test_starter_obraca_duzy_plik_wyjscia(tmp_path):
    """Plik wyjscia startera nie rosnie bez konca: powyzej 1 MB poprzednie starty ida do .poprzednie.txt."""
    if os.name != "nt":
        pytest.skip("starter i srodowisko wersji: Windows")
    katalog = tmp_path / "Stanowisko"
    _prawdziwa_wersja(katalog, "1.0", ATRAPA_PROGRAMU)
    (katalog / "dane").mkdir()
    (katalog / "dane" / "ostatni_start_stanowisko.txt").write_bytes(b"x" * 1_000_001)
    assert _starter(katalog, "stanowisko").returncode == 0
    assert (katalog / "dane" / "ostatni_start_stanowisko.poprzednie.txt").stat().st_size == 1_000_001
    assert (katalog / "dane" / "ostatni_start_stanowisko.txt").read_text(encoding="utf-8").count("==== start ") == 1


def test_sprawdzenie_pythona_bez_plikow_pyc(tmp_path, monkeypatch):
    """D5 recenzji PR #63: kontrola Pythona (krok 2) uruchamia Pythona PACZKI - z -B, zeby nie dopisywal __pycache__ do
    rozpakowanej paczki; zainstaluj.cmd uruchamia instalator tez z -B."""
    wywolania = []

    def uruchom(polecenie, **_):
        wywolania.append([str(c) for c in polecenie])
        return subprocess.CompletedProcess(polecenie, 0, "3.12.10 64\n", "")

    monkeypatch.setattr(I, "uruchom", uruchom)
    assert I.sprawdz_pythona(Path(sys.executable)) == "3.12.10"
    assert wywolania[0][1:4] == ["-I", "-B", "-c"]
    zainstaluj = (STANOWISKO / "instalacja" / "zainstaluj.cmd").read_text(encoding="ascii")
    wiersze = [w for w in zainstaluj.splitlines() if 'instalator.py" zainstaluj' in w]
    assert len(wiersze) == 2 and all(" -I -B " in w for w in wiersze)


def test_ikona_nieudana_nie_zatrzymuje_i_wskazuje_plik(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(I, "utworz_skrot", lambda *a, **k: None)
    katalog = tmp_path / "Stanowisko"
    katalog.mkdir()
    wyniki = I.utworz_skroty(katalog, tmp_path, I.Dziennik(katalog, "proba"))
    assert wyniki == {"Stanowisko": None, "Dzie\u0144 skanera": None}
    wyjscie = capsys.readouterr().out
    assert f"SKROT NIEUDANY: Stanowisko | {katalog / 'Stanowisko.cmd'}" in wyjscie
    assert f"SKROT NIEUDANY: Dzie\u0144 skanera | {katalog / 'Dzien_skanera.cmd'}" in wyjscie


def test_lnk_zapis_wlasny_format(tmp_path):
    """Naglowek MS-SHLLINK: rozmiar 0x4C, CLSID, flagi (LinkInfo, unicode, opis, katalog, argumenty), napisy UTF-16."""
    plik = tmp_path / "x.lnk"
    I.zapisz_lnk(plik, Path("C:/Program/pythonw.exe"), '-I "a b"', Path("C:/Kat"), "Opis \u0144")
    dane = plik.read_bytes()
    assert dane[:4] == b"\x4c\0\0\0" and dane[4:20] == bytes.fromhex("0114020000000000c000000000000046")
    flagi = int.from_bytes(dane[20:24], "little")
    assert flagi & ~0x01 == 0x02 | 0x04 | 0x10 | 0x20 | 0x80
    assert not flagi & 0x01  # cel nie istnieje - powloka nie poda listy identyfikatorow, zostaje sam LinkInfo
    assert "Opis \u0144".encode("utf-16-le") in dane and '-I "a b"'.encode("utf-16-le") in dane
    assert str(Path("C:/Program/pythonw.exe")).encode("utf-16-le") in dane and dane.endswith(b"\0\0\0\0")
    rozmiar_info = int.from_bytes(dane[76:80], "little")
    assert int.from_bytes(dane[80:84], "little") == 0x24 and 76 + rozmiar_info < len(dane)
    if os.name == "nt":  # cel istniejacy: lista identyfikatorow powloki zaraz po naglowku (flaga 0x01), potem ten sam LinkInfo
        I.zapisz_lnk(plik, Path(sys.executable), "", None, "")
        dane = plik.read_bytes()
        assert int.from_bytes(dane[20:24], "little") & 0x01
        poczatek = 76 + 2 + int.from_bytes(dane[76:78], "little")
        assert int.from_bytes(dane[poczatek + 4:poczatek + 8], "little") == 0x24


def test_zapisz_skrypty_dodaje_starter_tylko_gdy_wersja_go_ma(tmp_path):
    program = tmp_path / "program"
    (program / "instalacja").mkdir(parents=True)
    import shutil

    shutil.copytree(STANOWISKO / "instalacja" / "wzory", program / "instalacja" / "wzory")
    katalog = tmp_path / "kat"
    katalog.mkdir()
    assert I.zapisz_skrypty(program, katalog) == len(I.WZORY_SKRYPTOW) + 1 and (katalog / I.WZOR_STARTU).is_file()
    (program / "instalacja" / "wzory" / I.WZOR_STARTU).unlink()  # wersja sprzed E3-I1 (powrot do niej): starter zostaje
    assert I.zapisz_skrypty(program, katalog) == 0 and (katalog / I.WZOR_STARTU).is_file()


@pytest.fixture
def st(tmp_path) -> Stanowisko:
    return Stanowisko(tmp_path)
