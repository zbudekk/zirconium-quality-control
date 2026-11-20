"""instalacja/instalator.py (E3-A11i): instalacja, aktualizacja, powrot - na malej sztucznej paczce w tmp_path, bez sieci.

Srodowisko wirtualne i pip zastepuje ``SrodowiskoAtrapa`` (poza jednym krotkim testem z prawdziwym ``python -m venv``);
samokontrola to atrapa wg umowy A11s, uruchamiana naprawde jako proces (``python -m stanowisko.samokontrola``).
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tomllib
import types
from pathlib import Path

import pytest

from instalacja import instalator as I
from stanowisko import ustawienia as UST
import zbuduj_wydanie as ZW
from test_zbuduj_wydanie import DATA, STANOWISKO, drzewo_programu, kola_testowe, zbuduj_paczke

PYTHON = Path(sys.executable)


class SrodowiskoAtrapa(I.Srodowisko):
    """Zamiast venv i pip: katalog z plikiem ``pakiety.json``; interpreter wersji = interpreter testow."""

    def __init__(self):
        self.instalacje, self.blad_pip = 0, None

    def utworz(self, python, venv):
        venv.mkdir(parents=True)
        (venv / "pakiety.json").write_text("{}", encoding="ascii")

    def python(self, venv):
        return PYTHON

    def instaluj(self, venv, katalogi_kol, lista, dziennik_pip):
        if self.blad_pip is not None:
            raise self.blad_pip
        self.instalacje += 1
        pakiety = json.loads((venv / "pakiety.json").read_text(encoding="ascii"))
        for nazwa, wersja in I.wczytaj_liste_zamrozona(lista).items():
            assert any(list(Path(k).glob(f"{nazwa}-{wersja}-*.whl")) for k in katalogi_kol), f"brak kola {nazwa}"
            pakiety[nazwa] = wersja
        (venv / "pakiety.json").write_text(json.dumps(pakiety), encoding="ascii")

    def pakiety(self, venv):
        try:
            return dict(json.loads((venv / "pakiety.json").read_text(encoding="ascii")), pip="25.0.1")
        except OSError as e:
            raise I.BladInstalacji(I.KOD_INSTALACJA, "brak srodowiska") from e


class Stanowisko:
    """Katalog instalacji w tmp z gotowymi ustawieniami (foldery pracy istnieja) i licznikiem instalacji pakietow."""

    def __init__(self, tmp: Path):
        self.tmp, self.katalog, self.srodowisko = tmp, tmp / "Stanowisko", SrodowiskoAtrapa()
        self.zegar_n = 0

    def zegar(self) -> dt.datetime:
        self.zegar_n += 1
        return dt.datetime(2026, 11, 20, 12, 0, 0) + dt.timedelta(seconds=self.zegar_n)

    def ustawienia_gotowe(self) -> Path:
        """Ustawienia jak po pierwszej instalacji i uzupelnieniu folderow pracy przez osobe instalujaca."""
        self.katalog.mkdir(parents=True, exist_ok=True)
        tekst = I.ustawienia_ze_wzoru((STANOWISKO / "ustawienia.przyklad.toml").read_bytes(), self.katalog).decode("utf-8")
        for klucz, wzor in (("skaner", "C:/Aidite/Scandata"), ("cyrkon", "C:/sciezka/do/OneDrive/Cyrkon")):
            (self.tmp / "foldery" / klucz).mkdir(parents=True, exist_ok=True)
            assert wzor in tekst
            tekst = tekst.replace(wzor, (self.tmp / "foldery" / klucz).as_posix())
        (self.katalog / "ustawienia.toml").write_bytes(tekst.encode("utf-8"))
        return self.katalog / "ustawienia.toml"

    def zainstaluj(self, paczka: Path, **opcje) -> int:
        return I.zainstaluj(paczka, self.katalog, PYTHON, srodowisko=self.srodowisko, zegar=self.zegar, bez_sieci=True, **opcje)

    def wroc(self, **opcje) -> int:
        return I.wroc(self.katalog, srodowisko=self.srodowisko, zegar=self.zegar, **opcje)

    @property
    def biezaca(self):
        return I.czytaj_wskaznik(self.katalog, I.PLIK_BIEZACEJ)

    @property
    def poprzednia(self):
        return I.czytaj_wskaznik(self.katalog, I.PLIK_POPRZEDNIEJ)

    @property
    def baza(self) -> Path:
        return self.katalog / "dane" / "stanowisko.sqlite"

    def zaloz_baze(self, schemat: int = 1, wiersze: int = 3) -> Path:
        self.baza.parent.mkdir(parents=True, exist_ok=True)
        pol = sqlite3.connect(self.baza)
        pol.execute("CREATE TABLE IF NOT EXISTS skany (id INTEGER PRIMARY KEY, opis TEXT)")
        pol.executemany("INSERT INTO skany (opis) VALUES (?)", [(f"skan {i}",) for i in range(wiersze)])
        pol.execute(f"PRAGMA user_version = {schemat}")
        pol.commit()
        pol.close()
        return self.baza

    def dziennik(self) -> str:
        return (self.katalog / I.PLIK_DZIENNIKA).read_text(encoding="utf-8")


def sha(plik: Path) -> str:
    return hashlib.sha256(plik.read_bytes()).hexdigest()


def liczba_skanow(plik: Path) -> int:
    pol = sqlite3.connect(plik)
    try:
        return pol.execute("SELECT count(*) FROM skany").fetchone()[0]
    finally:
        pol.close()


@pytest.fixture
def st(tmp_path) -> Stanowisko:
    return Stanowisko(tmp_path)


@pytest.fixture
def zainstalowane(st, tmp_path) -> Stanowisko:
    """Stanowisko z zainstalowana wersja 1.0, baza (schemat 1, 3 skany) i plikiem danych."""
    st.ustawienia_gotowe()
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "1.0")) == 0
    st.zaloz_baze()
    (st.katalog / "dane" / "wyniki").mkdir()
    (st.katalog / "dane" / "wyniki" / "skan_wynik.json").write_text('{"gniazda": []}', encoding="ascii")
    return st


# ------------------------------------------------------------------------------------------------ czysta instalacja

def test_czysta_instalacja_najpierw_wstrzymana_po_poprawce_ustawien_gotowa(st, tmp_path, capsys):
    paczka = zbuduj_paczke(tmp_path, "1.0")
    # 1. pierwsza proba: ustawienia ze wzoru, foldery pracy nie istnieja -> samokontrola czerwona -> wersja NIE jest biezaca;
    #    to zamierzony etap, nie blad: wynik "WSTRZYMANA" i osobny kod wyjscia (decyzja koordynatora 20.11)
    assert st.zainstaluj(paczka) == I.KOD_WSTRZYMANA == 10
    wyjscie = capsys.readouterr().out
    assert "BLAD folder_cyrkon: folder nie istnieje" in wyjscie and "SAMOKONTROLA: CZERWONA" in wyjscie
    koniec = wyjscie.strip().splitlines()
    assert koniec[-1] == "INSTALACJA: WSTRZYMANA - uzupelnij ustawienia.toml i uruchom zainstaluj.cmd ponownie (kod 10)"
    assert "NIEUDANA" not in wyjscie and "CO ZROBIC:" in wyjscie
    ogon = koniec[next(i for i, w in enumerate(koniec) if w.startswith("Wersja 1.0 jest zainstalowana")):]
    assert [w.strip().split(":")[0] for w in ogon if w.strip().startswith("BLAD ")] == ["BLAD folder_eksportu_skanera", "BLAD folder_cyrkon"]
    assert f"Plik ustawien: {st.katalog.resolve() / 'ustawienia.toml'}" in ogon  # pelna sciezka pliku do uzupelnienia
    assert st.biezaca is None and not (st.katalog / "Stanowisko.cmd").exists()
    assert I.stan_wersji(st.katalog, "1.0") == "zainstalowana" and st.srodowisko.instalacje == 1
    # ustawienia ze wzoru: sciezki danych bezwzgledne w katalogu instalacji (poza katalogiem wersji), plik poprawny dla programu
    ust = UST.wczytaj_ustawienia(st.katalog / "ustawienia.toml")
    korzen = st.katalog.resolve().as_posix()
    assert ust["sciezki"]["baza"] == f"{korzen}/dane/stanowisko.sqlite" and ust["sciezki"]["logi"] == f"{korzen}/dane/logi"
    assert all(Path(v).is_absolute() and "wersje" not in Path(v).parts for v in ust["sciezki"].values())
    # 2. osoba instalujaca poprawia foldery i uruchamia to samo polecenie: bez ponownej instalacji pakietow, wersja biezaca
    plik = st.ustawienia_gotowe()
    suma = sha(plik)
    assert st.zainstaluj(paczka) == 0
    wyjscie = capsys.readouterr().out
    assert "jest juz zainstalowana i zgodna z paczka" in wyjscie and "SAMOKONTROLA: ZIELONA" in wyjscie
    assert "OK sumy: zgodne" in wyjscie and "INSTALACJA: GOTOWA - wersja biezaca 1.0" in wyjscie
    assert st.biezaca == "1.0" and st.poprzednia is None and st.srodowisko.instalacje == 1 and sha(plik) == suma
    assert (st.katalog / "wersja_biezaca.txt").read_bytes() == b"1.0\r\n"
    for nazwa in I.WZORY_SKRYPTOW:  # skrypty uruchamiajace w katalogu instalacji, z CRLF
        tresc = (st.katalog / nazwa).read_bytes()
        assert tresc == (STANOWISKO / "instalacja" / "wzory" / nazwa).read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    wersja = st.katalog / "wersje" / "1.0"
    assert (wersja / "program" / "stanowisko" / "samokontrola.py").is_file() and (wersja / "wydanie.json").is_file()
    assert not (wersja / I.ZNACZNIK_NIEDOKONCZONEJ).exists()
    assert not list((wersja / "program").rglob("__pycache__"))  # katalog programu zostaje zgodny z sumami
    sumy_programu = I.wczytaj_sumy(wersja / "program" / I.PLIK_SUM_PROGRAMU)  # ... i nie ma w nim zadnego pliku spoza listy sum
    assert sorted(p.relative_to(wersja / "program").as_posix() for p in (wersja / "program").rglob("*") if p.is_file()) == \
        sorted(list(sumy_programu) + [I.PLIK_SUM_PROGRAMU])
    assert "requirements.txt" in sumy_programu and any(n.startswith("ramka/") for n in sumy_programu)
    zapis = json.loads((wersja / "instalacja.json").read_text(encoding="ascii"))
    assert zapis["wersja"] == "1.0" and zapis["schemat_bazy"] == 1 and zapis["pakiety"] == 1 and zapis["testy"] is False
    dziennik = st.dziennik()
    for fragment in ("zainstaluj 1.0", "sumy paczki zgodne", "samokontrola: BLAD folder_cyrkon", "SAMOKONTROLA: CZERWONA",
                     "samokontrola: kod wyjscia 1", "INSTALACJA: WSTRZYMANA", "SAMOKONTROLA: ZIELONA", "samokontrola: kod wyjscia 0",
                     "INSTALACJA: GOTOWA"):
        assert fragment in dziennik, fragment
    assert "folder nie istnieje" not in dziennik  # do dziennika trafia poziom i kod sprawdzenia, bez opisu ze sciezkami


def test_ustawienia_ze_wzoru_zmieniaja_tylko_sciezki_wzgledne(tmp_path):
    wzor = (STANOWISKO / "ustawienia.przyklad.toml").read_bytes()
    wynik = I.ustawienia_ze_wzoru(wzor, tmp_path / "Kat alog")
    stare, nowe = wzor.decode("utf-8").splitlines(), wynik.decode("utf-8").splitlines()
    assert len(stare) == len(nowe)
    zmienione = [(s, n) for s, n in zip(stare, nowe) if s != n]
    przed, po = tomllib.loads(wzor.decode("utf-8")), tomllib.loads(wynik.decode("utf-8"))
    wzgledne = sorted(k for k, v in przed["sciezki"].items() if not Path(v).is_absolute())
    assert wzgledne == ["baza", "kalibracja_ramek", "log_excel", "logi", "podglady", "pula_cache", "wyniki"]
    assert len(zmienione) == len(wzgledne)
    korzen = (tmp_path / "Kat alog").resolve().as_posix()
    assert all(po["sciezki"][k] == f"{korzen}/{przed['sciezki'][k]}" for k in wzgledne)
    assert {k: v for k, v in po["sciezki"].items() if k not in wzgledne} == {k: v for k, v in przed["sciezki"].items() if k not in wzgledne}
    assert {s: v for s, v in po.items() if s != "sciezki"} == {s: v for s, v in przed.items() if s != "sciezki"}  # [plytki] zostaja wzgledne
    plik = tmp_path / "ustawienia.toml"
    plik.write_bytes(wynik)
    UST.wczytaj_ustawienia(plik)  # program przyjmuje taki plik (ukosniki /, wszystkie klucze)


# ------------------------------------------------------------------------------------------- bledy przed instalacja

def test_zepsuty_plik_w_paczce_zatrzymuje_przed_jakakolwiek_zmiana(st, tmp_path, capsys):
    paczka = zbuduj_paczke(tmp_path, "1.0")
    kolo = next((paczka / "kola").glob("*.whl"))
    kolo.write_bytes(kolo.read_bytes()[:-1] + b"X")
    assert st.zainstaluj(paczka) == I.KOD_PACZKA
    wyjscie = capsys.readouterr().out
    assert "sumy SHA-256 paczki niezgodne: 1 z" in wyjscie and "zmieniony plik kola/pakiecik-1.0-py3-none-any.whl" in wyjscie
    assert "Niczego nie zmieniono" in wyjscie and not st.katalog.exists()
    (paczka / "wydanie.json").unlink()
    assert st.zainstaluj(paczka) == I.KOD_PACZKA and "brak pliku wydanie.json" in capsys.readouterr().out
    (paczka / "SHA256SUMS").unlink()
    assert st.zainstaluj(paczka) == I.KOD_PACZKA and not st.katalog.exists()


def test_zepsuty_plik_przy_aktualizacji_nie_rusza_wersji_biezacej(zainstalowane, tmp_path, capsys):
    st = zainstalowane
    paczka = zbuduj_paczke(tmp_path, "2.0")
    (paczka / "program" / "stanowisko" / "baza.py").write_text("zepsute\n", encoding="ascii")
    przed = {p: sha(p) for p in st.katalog.rglob("*") if p.is_file() and p.name != I.PLIK_DZIENNIKA}
    assert st.zainstaluj(paczka) == I.KOD_PACZKA
    assert "INSTALACJA: NIEUDANA (kod 3) - wersja biezaca bez zmian: 1.0" in capsys.readouterr().out
    assert "sumy SHA-256 paczki niezgodne" in st.dziennik()  # przy aktualizacji nieudana proba zostaje w dzienniku
    assert {p: sha(p) for p in st.katalog.rglob("*") if p.is_file() and p.name != I.PLIK_DZIENNIKA} == przed
    assert st.biezaca == "1.0" and I.stan_wersji(st.katalog, "2.0") == "brak"


def test_paczka_bez_samokontroli_to_blad_wydania(st, tmp_path, capsys):
    paczka = zbuduj_paczke(tmp_path, "1.0", samokontrola=False)
    assert st.zainstaluj(paczka) == I.KOD_PACZKA
    assert "blad wydania: paczka nie zawiera modulu samokontroli" in capsys.readouterr().out and not st.katalog.exists()


def test_brak_albo_zla_wersja_pythona(st, tmp_path, capsys, monkeypatch):
    paczka = zbuduj_paczke(tmp_path, "1.0")
    assert I.zainstaluj(paczka, st.katalog, tmp_path / "nie_ma" / "python.exe", srodowisko=st.srodowisko) == I.KOD_PYTHON
    wyjscie = capsys.readouterr().out
    assert "nie mozna uruchomic Pythona" in wyjscie and "/python" in wyjscie and not st.katalog.exists()
    prawdziwe = I.uruchom
    for odpowiedz, fragment in (("3.11.9 64", "zla wersja Pythona"), ("3.14.0 64", "zla wersja Pythona"), ("3.12.10 32", "(32-bit)")):
        def falszywe(polecenie, **kw):
            if "-c" in polecenie and "struct" in polecenie[polecenie.index("-c") + 1]:
                return subprocess.CompletedProcess(polecenie, 0, odpowiedz + "\n", "")
            return prawdziwe(polecenie, **kw)

        monkeypatch.setattr(I, "uruchom", falszywe)
        assert st.zainstaluj(paczka) == I.KOD_PYTHON
        wyjscie = capsys.readouterr().out
        assert fragment in wyjscie and "a program wymaga 3.12 (64-bit)" in wyjscie and not st.katalog.exists()
    monkeypatch.setattr(I, "uruchom", prawdziwe)
    assert I.sprawdz_pythona(PYTHON, "%d.%d" % sys.version_info[:2]).startswith("%d.%d." % sys.version_info[:2])


def test_katalog_w_folderze_synchronizowanym(st, tmp_path, capsys, monkeypatch):
    paczka = zbuduj_paczke(tmp_path, "1.0")
    monkeypatch.setenv("OneDriveCommercial", str(tmp_path / "Firma"))
    assert I.zainstaluj(paczka, tmp_path / "Firma" / "Stanowisko", PYTHON, srodowisko=st.srodowisko) == I.KOD_INSTALACJA
    wyjscie = capsys.readouterr().out.lower()  # Windows podaje nazwy zmiennych wielkimi literami
    assert "folderze synchronizowanym (zmienna onedrivecommercial)" in wyjscie and not (tmp_path / "Firma").exists()
    assert I.katalog_synchronizowany(tmp_path / "OneDrive - Firma" / "Stanowisko") is not None
    assert I.katalog_synchronizowany(st.katalog) is None


def test_sciezki_wzgledne_w_istniejacych_ustawieniach_zatrzymuja_instalacje(st, tmp_path, capsys):
    """Plik ze starej instalacji (kopia folderu): ``baza = "dane/..."`` trafilaby do katalogu wersji i znikla przy aktualizacji."""
    st.katalog.mkdir()
    shutil.copyfile(STANOWISKO / "ustawienia.przyklad.toml", st.katalog / "ustawienia.toml")
    suma = sha(st.katalog / "ustawienia.toml")
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "1.0")) == I.KOD_USTAWIENIA
    wyjscie = capsys.readouterr().out
    assert "sciezki wzgledne w [sciezki] (baza, kalibracja_ramek, log_excel, logi, podglady, pula_cache, wyniki)" in wyjscie
    assert f'baza = "{st.katalog.resolve().as_posix()}/dane/stanowisko.sqlite"' in wyjscie
    assert sha(st.katalog / "ustawienia.toml") == suma and I.stan_wersji(st.katalog, "1.0") == "brak" and st.srodowisko.instalacje == 0
    (st.katalog / "ustawienia.toml").write_text("[sciezki\n", encoding="ascii")  # blad skladni: komunikat programu, kod 7
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "1.1")) == I.KOD_USTAWIENIA
    assert "plik ustawien nie przechodzi kontroli tej wersji programu: ustawienia.toml" in capsys.readouterr().out


# ---------------------------------------------------------------------------------------- aktualizacja i powrot

def test_aktualizacja_zachowuje_ustawienia_i_dane_robi_kopie_bazy_i_przelacza(zainstalowane, tmp_path, capsys):
    st = zainstalowane
    ustawienia, wynik = st.katalog / "ustawienia.toml", st.katalog / "dane" / "wyniki" / "skan_wynik.json"
    przed = {p: p.read_bytes() for p in (ustawienia, st.baza, wynik)}
    wersja_1 = {p: sha(p) for p in (st.katalog / "wersje" / "1.0").rglob("*") if p.is_file()}
    capsys.readouterr()
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "2.0")) == 0
    wyjscie = capsys.readouterr().out
    assert {p: p.read_bytes() for p in przed} == przed  # ustawienia, baza i dane bajt w bajt
    assert st.biezaca == "2.0" and st.poprzednia == "1.0"
    kopie = list((st.katalog / "dane" / "kopie").glob("*.sqlite"))
    assert len(kopie) == 1 and kopie[0].name.startswith("stanowisko_przed_2.0_20261120_12")
    assert kopie[0].name.endswith("_v1.sqlite") and liczba_skanow(kopie[0]) == 3 and I.wersja_schematu(kopie[0]) == 1
    assert f"kopia bazy: kopie/{kopie[0].name}" in wyjscie and "INSTALACJA: GOTOWA - wersja biezaca 2.0 (poprzednia: 1.0)" in wyjscie
    assert "istniejacy ustawienia.toml zostaje bez zmian" in wyjscie
    assert {p: sha(p) for p in (st.katalog / "wersje" / "1.0").rglob("*") if p.is_file()} == wersja_1  # stara wersja nietknieta
    assert (st.katalog / "wersje" / "2.0" / "program" / "WERSJA").read_text(encoding="ascii") == "2.0\n"


def test_powrot_bez_zmiany_schematu_nie_rusza_bazy(zainstalowane, tmp_path, capsys):
    st = zainstalowane
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "2.0")) == 0
    przed = {p: p.read_bytes() for p in (st.katalog / "ustawienia.toml", st.baza)}
    kopie = sorted(p.name for p in (st.katalog / "dane" / "kopie").iterdir())
    capsys.readouterr()
    assert st.wroc() == 0
    wyjscie = capsys.readouterr().out
    assert st.biezaca == "1.0" and st.poprzednia == "2.0"
    assert "schemat zgodny - baza zostaje bez zmian" in wyjscie and "POWROT: GOTOWY - wersja biezaca 1.0" in wyjscie
    assert "SAMOKONTROLA: ZIELONA" in wyjscie
    assert {p: p.read_bytes() for p in przed} == przed and sorted(p.name for p in (st.katalog / "dane" / "kopie").iterdir()) == kopie
    assert st.wroc() == 0 and st.biezaca == "2.0" and st.poprzednia == "1.0"  # ponowny powrot = z powrotem do nowszej
    assert "wroc 1.0 -> 2.0" in st.dziennik() and "wroc 2.0 -> 1.0" in st.dziennik()


def test_powrot_po_migracji_wymaga_zgody_i_przywraca_kopie(zainstalowane, tmp_path, capsys):
    st = zainstalowane
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "2.0", migracje="{1: (), 2: ()}")) == 0
    kopia = next((st.katalog / "dane" / "kopie").glob("*_przed_2.0_*_v1.sqlite"))
    st.zaloz_baze(schemat=2, wiersze=2)  # program 2.0 zmigrowal baze i dopisal 2 skany
    baza_v2 = st.baza.read_bytes()
    capsys.readouterr()
    # bez zgody: wykrycie PRZED przelaczeniem, ostrzezenie z licznikami, nic nie zmienione
    assert st.wroc() == I.KOD_BAZA_NOWSZA
    wyjscie = capsys.readouterr().out
    assert st.biezaca == "2.0" and st.poprzednia == "1.0" and st.baza.read_bytes() == baza_v2
    assert "Baza: schemat 2; wersja 1.0 obsluguje schemat do 1" in wyjscie and "wersja 1.0 tej bazy NIE otworzy" in wyjscie
    assert f"Kopia sprzed aktualizacji: {kopia.name}" in wyjscie and "zniknie wszystko, co zapisano po tej chwili: 2 wpisow w 1 tabelach" in wyjscie
    assert "tabela skany: 3 w kopii, 5 teraz (+2)" in wyjscie and "/przywroc-kopie" in wyjscie and "POWROT: NIEUDANA (kod 8)" in wyjscie
    # ze zgoda: kopia v1 wraca, baza v2 odlozona (nie skasowana), wersja 1.0 biezaca
    assert st.wroc(przywroc=True) == 0
    wyjscie = capsys.readouterr().out
    assert st.biezaca == "1.0" and st.poprzednia == "2.0"
    assert I.wersja_schematu(st.baza) == 1 and liczba_skanow(st.baza) == 3
    odlozone = list((st.katalog / "dane" / "kopie").glob("stanowisko_odlozona_v2_*.sqlite"))
    # odlozona = sprawdzona kopia tresci (mechanizm kopii SQLite: te same strony, inny licznik zmian w naglowku pliku)
    assert len(odlozone) == 1 and liczba_skanow(odlozone[0]) == 5 and I.schemat_kopii(odlozone[0]) == 2
    assert odlozone[0].read_bytes()[100:] == baza_v2[100:]
    assert kopia.is_file() and f"przywrocono kopie {kopia.name}" in wyjscie and f"kopie/{odlozone[0].name}" in wyjscie


def test_powrot_po_migracji_bez_kopii_niczego_nie_zmienia(zainstalowane, tmp_path, capsys):
    st = zainstalowane
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "2.0", migracje="{1: (), 2: ()}")) == 0
    shutil.rmtree(st.katalog / "dane" / "kopie")
    st.zaloz_baze(schemat=2, wiersze=1)
    baza = st.baza.read_bytes()
    assert st.wroc(przywroc=True) == I.KOD_BAZA_NOWSZA
    assert "nie ma sprawdzonej kopii bazy o schemacie do 1" in capsys.readouterr().out
    assert st.biezaca == "2.0" and st.baza.read_bytes() == baza
    # kopia zrobiona przez sam program przed migracja (baza.py: <baza>.kopia_v1_<czas>.sqlite) tez sie nadaje
    kopia_programu = st.baza.with_name("stanowisko.kopia_v1_20261120_130000.sqlite")
    pol = sqlite3.connect(kopia_programu)
    pol.execute("CREATE TABLE skany (id INTEGER PRIMARY KEY, opis TEXT)")
    pol.execute("PRAGMA user_version = 1")
    pol.commit()
    pol.close()
    assert st.wroc(przywroc=True) == 0 and st.biezaca == "1.0" and I.wersja_schematu(st.baza) == 1


def test_powrot_bez_poprzedniej_wersji(zainstalowane, st, capsys):
    assert zainstalowane.wroc() == I.KOD_BRAK_WERSJI
    assert "nie ma poprzedniej wersji" in capsys.readouterr().out and zainstalowane.biezaca == "1.0"
    assert I.wroc(zainstalowane.tmp / "pusty", srodowisko=st.srodowisko) == I.KOD_BRAK_WERSJI


# ------------------------------------------------------------------------- bledy w trakcie: wersja biezaca nietknieta

@pytest.mark.parametrize("kod_modulu, kod_instalatora, fragment", [
    (1, I.KOD_SAMOKONTROLA_CZERWONA, "samokontrola wersji 2.0 zglosila bledy - wersja biezaca zostaje 1.0"),
    (2, I.KOD_SAMOKONTROLA_NIEWYKONANA, "samokontroli wersji 2.0 nie dalo sie wykonac (kod 2) - wersja biezaca zostaje 1.0"),
])
def test_samokontrola_nowej_wersji_z_bledem_nie_przelacza(zainstalowane, tmp_path, capsys, kod_modulu, kod_instalatora, fragment):
    st = zainstalowane
    skrypty = {n: (st.katalog / n).read_bytes() for n in I.WZORY_SKRYPTOW}
    capsys.readouterr()
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "2.0", kod_samokontroli=kod_modulu)) == kod_instalatora
    wyjscie = capsys.readouterr().out
    assert fragment in wyjscie and f"INSTALACJA: NIEUDANA (kod {kod_instalatora}) - wersja biezaca bez zmian: 1.0" in wyjscie
    assert st.biezaca == "1.0" and st.poprzednia is None
    assert {n: (st.katalog / n).read_bytes() for n in I.WZORY_SKRYPTOW} == skrypty
    assert I.stan_wersji(st.katalog, "2.0") == "zainstalowana"  # gotowa do ponownej proby, ale nie biezaca
    assert st.wroc() == I.KOD_BRAK_WERSJI  # nieudana aktualizacja nie zostaje "poprzednia"


def test_program_uruchomiony_podczas_aktualizacji_i_powrotu(zainstalowane, tmp_path, capsys):
    """Blokade trzyma prawdziwa ``aplikacja.BlokadaStanowiska`` - ten sam plik ``<baza>.blokada``, co w dzialajacym programie."""
    from stanowisko import aplikacja

    st = zainstalowane
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "2.0")) == 0
    paczka_3 = zbuduj_paczke(tmp_path, "3.0")
    instalacje = st.srodowisko.instalacje
    blokada = aplikacja.BlokadaStanowiska(st.baza).zajmij()
    try:
        capsys.readouterr()
        assert st.zainstaluj(paczka_3) == I.KOD_PROGRAM_DZIALA
        wyjscie = capsys.readouterr().out
        assert 'program "Stanowisko" jest uruchomiony' in wyjscie and "Zamknij program" in wyjscie
        assert st.biezaca == "2.0" and I.stan_wersji(st.katalog, "3.0") == "brak" and st.srodowisko.instalacje == instalacje
        assert st.wroc() == I.KOD_PROGRAM_DZIALA and st.biezaca == "2.0" and st.poprzednia == "1.0"
    finally:
        blokada.zwolnij()
    assert st.zainstaluj(paczka_3) == 0 and st.biezaca == "3.0" and st.poprzednia == "2.0"
    with I.BlokadaProgramu(st.baza):  # i odwrotnie: w czasie przelaczania programu nie da sie uruchomic
        with pytest.raises(aplikacja.ProgramJuzDziala):
            aplikacja.BlokadaStanowiska(st.baza).zajmij()
    aplikacja.BlokadaStanowiska(st.baza).zajmij().zwolnij()


def test_brak_miejsca_na_dysku(zainstalowane, tmp_path, capsys, monkeypatch):
    st = zainstalowane
    paczka = zbuduj_paczke(tmp_path, "2.0")
    capsys.readouterr()
    assert st.zainstaluj(paczka, min_wolne_mb=10**9) == I.KOD_INSTALACJA
    assert "za malo miejsca na dysku: potrzeba ok. 1000000000 MB" in capsys.readouterr().out
    monkeypatch.setattr(I.shutil, "disk_usage", lambda _: types.SimpleNamespace(total=10**12, used=10**12 - 10**6, free=10**6))
    assert st.zainstaluj(paczka) == I.KOD_INSTALACJA
    wyjscie = capsys.readouterr().out
    assert f"za malo miejsca na dysku: potrzeba ok. {I.ZAPAS_MB} MB, wolne 0 MB" in wyjscie and "Wersja biezaca bez zmian" in wyjscie
    assert st.biezaca == "1.0" and I.stan_wersji(st.katalog, "2.0") == "brak" and st.srodowisko.instalacje == 1


@pytest.mark.parametrize("blad", [I.BladInstalacji(I.KOD_INSTALACJA, "pip zakonczyl sie bledem (kod 1): No space left on device", "rada"),
                                  KeyboardInterrupt(), OSError(28, "No space left on device")])
def test_przerwany_pip_zostawia_znacznik_a_nastepna_proba_sprzata(zainstalowane, tmp_path, capsys, blad):
    st = zainstalowane
    paczka = zbuduj_paczke(tmp_path, "2.0")
    przed = {p: p.read_bytes() for p in (st.katalog / "ustawienia.toml", st.baza, st.katalog / "wersja_biezaca.txt")}
    st.srodowisko.blad_pip = blad
    capsys.readouterr()
    assert st.zainstaluj(paczka) == I.KOD_INSTALACJA
    wyjscie = capsys.readouterr().out
    assert "INSTALACJA: NIEUDANA (kod 6) - wersja biezaca bez zmian: 1.0" in wyjscie
    assert st.biezaca == "1.0" and st.poprzednia is None and {p: p.read_bytes() for p in przed} == przed
    assert I.stan_wersji(st.katalog, "2.0") == "niedokonczona" and (st.katalog / "wersje" / "2.0" / I.ZNACZNIK_NIEDOKONCZONEJ).is_file()
    assert [w["stan"] for w in I.lista_wersji(st.katalog)] == ["zainstalowana", "niedokonczona"]
    st.srodowisko.blad_pip = None
    assert st.zainstaluj(paczka) == 0
    wyjscie = capsys.readouterr().out
    assert "usunieto niedokonczona instalacje wersji 2.0" in wyjscie and st.biezaca == "2.0" and st.poprzednia == "1.0"
    assert I.stan_wersji(st.katalog, "2.0") == "zainstalowana"


# -------------------------------------------------------------------------------- ponowna instalacja, naprawa, wersje

def test_ponowna_instalacja_tej_samej_wersji_jest_bezpieczna(zainstalowane, tmp_path, capsys):
    st = zainstalowane
    paczka = zbuduj_paczke(tmp_path / "ponownie", "1.0")
    przed = {p: p.read_bytes() for p in (st.katalog / "ustawienia.toml", st.baza)}
    capsys.readouterr()
    assert st.zainstaluj(paczka) == 0
    wyjscie = capsys.readouterr().out
    assert "jest juz zainstalowana i zgodna z paczka" in wyjscie and "kopia bazy niepotrzebna" in wyjscie
    assert st.srodowisko.instalacje == 1 and st.biezaca == "1.0" and st.poprzednia is None and {p: p.read_bytes() for p in przed} == przed
    assert not (st.katalog / "dane" / "kopie").exists()
    # uszkodzony plik programu -> naprawa: wersja zalozona od nowa, dane bez zmian
    (st.katalog / "wersje" / "1.0" / "program" / "stanowisko" / "aplikacja.py").write_text("uszkodzony\n", encoding="ascii")
    assert st.zainstaluj(paczka) == 0
    wyjscie = capsys.readouterr().out
    assert "pliki programu niezgodne z sumami (1) - naprawa" in wyjscie and st.srodowisko.instalacje == 2
    assert {p: p.read_bytes() for p in przed} == przed and st.biezaca == "1.0"
    assert I.sprawdz_sumy(st.katalog / "wersje" / "1.0" / "program", I.wczytaj_sumy(st.katalog / "wersje" / "1.0" / "program" / I.PLIK_SUM_PROGRAMU)) == []


def test_inna_budowa_o_tym_samym_numerze_nie_zastepuje_wersji_uzywanej(zainstalowane, tmp_path, capsys):
    """Paczka 1.0 o innej tresci (tu: samokontrola z bledem) nie moze podmienic wersji biezacej ani poprzedniej - inaczej
    nieudana samokontrola zostawilaby stanowisko z zepsuta wersja biezaca."""
    st = zainstalowane
    inna = zbuduj_paczke(tmp_path / "inna", "1.0", kod_samokontroli=1)

    def stan_wersji_1():
        return {p: sha(p) for p in (st.katalog / "wersje" / "1.0").rglob("*") if p.is_file()}

    przed = stan_wersji_1()
    capsys.readouterr()
    assert st.zainstaluj(inna) == I.KOD_PACZKA  # 1.0 jest biezaca
    wyjscie = capsys.readouterr().out
    assert "wersja 1.0 jest juz zainstalowana z INNEJ budowy o tym samym numerze i jest wersja biezaca" in wyjscie and "nowym numerem wersji" in wyjscie
    assert stan_wersji_1() == przed and st.biezaca == "1.0" and st.srodowisko.instalacje == 1
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "2.0")) == 0
    assert st.zainstaluj(inna) == I.KOD_PACZKA  # 1.0 jest poprzednia
    assert "jest wersja poprzednia" in capsys.readouterr().out and stan_wersji_1() == przed and st.biezaca == "2.0"
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "3.0")) == 0  # 1.0 nie jest juz ani biezaca, ani poprzednia
    assert st.zainstaluj(inna) == I.KOD_SAMOKONTROLA_CZERWONA  # zastapiona nowa budowa; ta nie przechodzi samokontroli
    wyjscie = capsys.readouterr().out
    assert "inna budowa o tym samym numerze wersji - naprawa (instalacja od nowa)" in wyjscie and "wersja biezaca zostaje 3.0" in wyjscie
    assert stan_wersji_1() != przed and I.stan_wersji(st.katalog, "1.0") == "zainstalowana"
    assert st.biezaca == "3.0" and st.poprzednia == "2.0"


def test_naprawa_sprawdza_miejsce_przed_usunieciem_wersji(zainstalowane, tmp_path, capsys):
    st = zainstalowane
    aplikacja = st.katalog / "wersje" / "1.0" / "program" / "stanowisko" / "aplikacja.py"
    aplikacja.write_text("uszkodzony\n", encoding="ascii")
    assert st.zainstaluj(zbuduj_paczke(tmp_path / "ponownie", "1.0"), min_wolne_mb=10**9) == I.KOD_INSTALACJA
    assert "za malo miejsca na dysku" in capsys.readouterr().out
    assert aplikacja.read_text(encoding="ascii") == "uszkodzony\n" and I.stan_wersji(st.katalog, "1.0") == "zainstalowana"  # nic nie usunieto


def test_zestaw_testowy_tylko_na_zadanie(zainstalowane, tmp_path, capsys):
    st = zainstalowane
    pakiety = json.loads((st.katalog / "wersje" / "1.0" / "venv" / "pakiety.json").read_text(encoding="ascii"))
    assert pakiety == {"pakiecik": "1.0"}  # domyslnie bez zestawu testowego
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "2.0"), testy=True) == 0
    assert "zestaw testowy (pytest): 1 pakietow" in capsys.readouterr().out
    pakiety = json.loads((st.katalog / "wersje" / "2.0" / "venv" / "pakiety.json").read_text(encoding="ascii"))
    assert pakiety == {"pakiecik": "1.0", "testowy": "2.0"}
    assert json.loads((st.katalog / "wersje" / "2.0" / "instalacja.json").read_text(encoding="ascii"))["testy"] is True
    # /testy na wersji juz zainstalowanej: sam zestaw testowy, bez zakladania wersji od nowa
    assert st.wroc() == 0 and st.biezaca == "1.0"
    instalacje = st.srodowisko.instalacje
    assert st.zainstaluj(zbuduj_paczke(tmp_path / "ponownie", "1.0"), testy=True) == 0
    assert "dokladam zestaw testowy" in capsys.readouterr().out and st.srodowisko.instalacje == instalacje + 1
    assert json.loads((st.katalog / "wersje" / "1.0" / "venv" / "pakiety.json").read_text(encoding="ascii")) == pakiety
    zapis = json.loads((st.katalog / "wersje" / "1.0" / "instalacja.json").read_text(encoding="ascii"))
    assert zapis["testy"] is True and zapis["pakiety"] == 2 and zapis["wersja"] == "1.0"
    assert st.zainstaluj(zbuduj_paczke(tmp_path / "trzeci", "1.0")) == 0 and st.srodowisko.instalacje == instalacje + 1  # bez /testy: zgodna
    assert I.porownaj_pakiety({"pakiecik": "1.1", "obcy": "3", "pip": "25"}, {"pakiecik": "1.0", "drugi": "2"}) == [
        "brak drugi==2", "pakiecik: jest 1.1, ma byc 1.0", "nadmiarowy obcy==3"]


def test_lista_wersji_i_usuwanie(zainstalowane, tmp_path, capsys):
    st = zainstalowane
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "2.0")) == 0 and st.zainstaluj(zbuduj_paczke(tmp_path, "3.0")) == 0
    capsys.readouterr()
    assert I.wersje(st.katalog) == 0
    wiersze = capsys.readouterr().out.splitlines()
    assert [w.split()[0] for w in wiersze] == ["1.0", "2.0", "3.0"]
    assert "BIEZACA" in wiersze[2] and "poprzednia" in wiersze[1] and "BIEZACA" not in wiersze[0] and "poprzednia" not in wiersze[0]
    for wersja in ("3.0", "2.0", "9.9"):  # biezaca, poprzednia, nieistniejaca
        assert I.wersje(st.katalog, usun=wersja) == I.KOD_BRAK_WERSJI
    assert sorted(p.name for p in (st.katalog / "wersje").iterdir()) == ["1.0", "2.0", "3.0"]
    przed = {p: p.read_bytes() for p in (st.katalog / "ustawienia.toml", st.baza)}
    assert I.wersje(st.katalog, usun="1.0") == 0
    assert sorted(p.name for p in (st.katalog / "wersje").iterdir()) == ["2.0", "3.0"] and {p: p.read_bytes() for p in przed} == przed
    assert st.biezaca == "3.0" and st.poprzednia == "2.0"


# -------------------------------------------------------------------------------------------------------- drobne

def test_sumy_odrzucaja_sciezki_poza_katalog(tmp_path):
    for wiersz in ("0" * 64 + "  ../poza.txt", "0" * 64 + "  /bezwzgledna", "0" * 64 + "  C:/dysk.txt", "krotka  plik.txt", "0" * 64 + " plik.txt"):
        (tmp_path / "SUMY").write_text(wiersz + "\n", encoding="ascii")
        with pytest.raises(I.BladInstalacji):
            I.wczytaj_sumy(tmp_path / "SUMY")
    (tmp_path / "SUMY").write_text("a" * 64 + "  kat/plik.txt\n" + "b" * 64 + " *inny.bin\n\n", encoding="ascii")
    assert I.wczytaj_sumy(tmp_path / "SUMY") == {"kat/plik.txt": "a" * 64, "inny.bin": "b" * 64}


def test_dziennik_bez_katalogu_profilu(tmp_path, monkeypatch):
    monkeypatch.setenv("USERPROFILE", r"C:\Users\Jan Kowalski")
    assert I.bez_profilu(r"python c:\users\jan kowalski\AppData\python.exe i C:/Users/Jan Kowalski/x") == \
        r"python %USERPROFILE%\AppData\python.exe i %USERPROFILE%/x"
    dziennik = I.Dziennik(tmp_path, "proba", lambda: dt.datetime(2026, 11, 20, 8, 5, 1))
    dziennik.wpis("START C:\\Users\\Jan Kowalski\\Stanowisko\ndrugi wiersz")
    assert (tmp_path / I.PLIK_DZIENNIKA).read_bytes() == (b"2026-11-20 08:05:01 | proba | START %USERPROFILE%\\Stanowisko\r\n"
                                                         b"2026-11-20 08:05:01 | proba | drugi wiersz\r\n")


def test_opcje_w_stylu_windows_i_wskaznik(tmp_path):
    assert I._normalizuj_argumenty(["zainstaluj", "/katalog", "C:\\X", "/Python", "p.exe", "/testy", "/bez-pauzy", "/nieznana", "C:/a"]) == \
        ["zainstaluj", "--katalog", "C:\\X", "--python", "p.exe", "--testy", "--bez-pauzy", "/nieznana", "C:/a"]
    assert I.czytaj_wskaznik(tmp_path, I.PLIK_BIEZACEJ) is None
    for tresc, wynik in ((b"1.0\r\n", "1.0"), (b"  2.0-rc1 \n", "2.0-rc1"), (b"", None), (b"..\\..\\x", None), (b"\xff\xfe", None)):
        (tmp_path / I.PLIK_BIEZACEJ).write_bytes(tresc)
        assert I.czytaj_wskaznik(tmp_path, I.PLIK_BIEZACEJ) == wynik
    assert I.main(["wersje", "/katalog", str(tmp_path)]) == 0
    assert I.main(["wroc", "/katalog", str(tmp_path), "/przywroc-kopie", "/bez-pauzy"]) == I.KOD_BRAK_WERSJI


def test_skrot_nie_zatrzymuje_instalacji(tmp_path):
    """Skrot zaklada PowerShell (WScript.Shell); gdy polityka komputera na to nie pozwala, wynik to None, nie wyjatek."""
    (tmp_path / "pulpit").mkdir()
    skrot = I.utworz_skrot(tmp_path / "Stanowisko", tmp_path / "pulpit")
    assert skrot is None or (skrot == tmp_path / "pulpit" / "Stanowisko.lnk" and skrot.is_file())
    assert [p.name for p in (tmp_path / "pulpit").iterdir()] == ([] if skrot is None else ["Stanowisko.lnk"])


# ------------------------------------------------------- runda 2 (recenzja PR #39): baza nigdy nie znika ani nie psuje sie

class Zabicie(BaseException):
    """Udaje zabicie procesu instalatora: nie lapie go ``except Exception`` ani ``except KeyboardInterrupt``."""


def przerwij_zapis(baza: Path) -> Path:
    """Proces "programu" ginie w srodku transakcji (zanik zasilania): obok bazy zostaje goracy plik ``-journal``."""
    kod = ("import os, sqlite3, sys\np = sqlite3.connect(sys.argv[1], isolation_level=None)\np.execute('PRAGMA cache_size = 5')\n"
           "p.execute('BEGIN IMMEDIATE')\np.execute(\"UPDATE skany SET opis = 'NIEZATWIERDZONE ' || opis\")\n"
           "p.execute('DELETE FROM skany WHERE id % 2 = 0')\nos._exit(9)\n")
    subprocess.run([sys.executable, "-I", "-c", kod, str(baza)], check=False)
    dziennik = baza.with_name(baza.name + "-journal")
    assert dziennik.is_file() and dziennik.stat().st_size > 0  # strony zmienione trafily na dysk, COMMIT nie nastapil
    return dziennik


def stan_bazy(plik: Path) -> tuple:
    """(quick_check, wersja schematu, liczba skanow, liczba wierszy niezatwierdzonych) pliku bazy otwartego do odczytu."""
    pol = sqlite3.connect(f"{plik.resolve().as_uri()}?mode=ro", uri=True)
    try:
        return (pol.execute("PRAGMA quick_check").fetchall(), pol.execute("PRAGMA user_version").fetchone()[0],
                *pol.execute("SELECT count(*), coalesce(sum(opis LIKE 'NIEZATWIERDZONE%'), 0) FROM skany").fetchone())
    finally:
        pol.close()


def kopie_bazy(st: Stanowisko, wzor: str = "*.sqlite") -> list[Path]:
    return sorted((st.katalog / "dane" / "kopie").glob(wzor))


def pliki_wersji(st: Stanowisko) -> dict:
    return {p.relative_to(st.katalog).as_posix(): sha(p) for p in (st.katalog / "wersje").rglob("*") if p.is_file()}


def test_p1_kopia_bazy_przy_goracym_dzienniku_jest_spojna(zainstalowane, tmp_path, capsys):
    """Program zabity w trakcie zapisu, aktualizacja przed nastepnym startem: kopia ma byc spojna baza (stan sprzed przerwanej
    transakcji), a nie plikiem glownym bez dziennika ("database disk image is malformed")."""
    st = zainstalowane
    pol = sqlite3.connect(st.baza)
    pol.executemany("INSERT INTO skany (opis) VALUES (?)", [("stary %05d " % i + "x" * 200,) for i in range(3000)])
    pol.commit()
    pol.close()
    dziennik = przerwij_zapis(st.baza)
    capsys.readouterr()
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "2.0")) == 0
    wyjscie = capsys.readouterr().out
    kopie = kopie_bazy(st)
    assert len(kopie) == 1 and kopie[0].name.startswith("stanowisko_przed_2.0_") and kopie[0].name.endswith("_v1.sqlite")
    assert stan_bazy(kopie[0]) == ([("ok",)], 1, 3003, 0)  # kopia cala: komplet wierszy sprzed przerwanej transakcji
    assert f"kopia bazy: kopie/{kopie[0].name}" in wyjscie and "sprawdzona" in wyjscie
    assert stan_bazy(st.baza) == ([("ok",)], 1, 3003, 0) and not dziennik.exists() and st.biezaca == "2.0"


def test_p1_baza_nieczytelna_zatrzymuje_aktualizacje_bez_zmian(zainstalowane, tmp_path, capsys):
    """Bez sprawdzonej kopii bazy wersja nie jest przelaczana: plik bazy, ktorego SQLite nie czyta = stop, nic nie zmienione."""
    st = zainstalowane
    st.baza.write_bytes(b"to nie jest baza SQLite " * 200)
    przed = st.baza.read_bytes()
    capsys.readouterr()
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "2.0")) == I.KOD_INSTALACJA
    wyjscie = capsys.readouterr().out
    assert "pliku bazy nie da sie odczytac" in wyjscie and "INSTALACJA: NIEUDANA (kod 6) - wersja biezaca bez zmian: 1.0" in wyjscie
    assert st.biezaca == "1.0" and st.poprzednia is None and st.baza.read_bytes() == przed
    assert kopie_bazy(st) == [] and st.srodowisko.instalacje == 1  # zadnej "kopii" pliku uszkodzonego, pakiety nie instalowane


def test_p1_powrot_pomija_kopie_ktora_nie_przechodzi_kontroli(zainstalowane, tmp_path, capsys):
    st = zainstalowane
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "2.0", migracje="{1: (), 2: ()}")) == 0
    dobra = kopie_bazy(st, "*_przed_2.0_*_v1.sqlite")[0]
    st.zaloz_baze(schemat=2, wiersze=2)
    # nowsza "kopia" uszkodzona (np. plik glowny skopiowany bez dziennika): naglowek czytelny, druga strona zamazana
    zla = dobra.with_name("stanowisko_przed_2.0_20261121_090000_v1.sqlite")
    dane = dobra.read_bytes()
    zla.write_bytes(dane[:4096] + b"\xa5" * (len(dane) - 4096))
    assert I.wersja_schematu(zla) == 1  # sam naglowek nie zdradza uszkodzenia
    capsys.readouterr()
    assert st.wroc(przywroc=True) == 0
    wyjscie = capsys.readouterr().out
    assert f"przywrocono kopie {dobra.name}" in wyjscie and f"1 takich, ktore nie przeszly kontroli ({zla.name})" in wyjscie
    assert stan_bazy(st.baza) == ([("ok",)], 1, 3, 0) and st.biezaca == "1.0" and zla.read_bytes()[4096:4100] == b"\xa5" * 4


def test_p1_powtorzona_proba_aktualizacji_nie_mnozy_kopii(zainstalowane, tmp_path):
    st = zainstalowane
    paczka = zbuduj_paczke(tmp_path, "2.0", kod_samokontroli=1)
    assert st.zainstaluj(paczka) == I.KOD_SAMOKONTROLA_CZERWONA and st.zainstaluj(paczka) == I.KOD_SAMOKONTROLA_CZERWONA
    assert len(kopie_bazy(st)) == 1  # baza bez zmian miedzy probami: jedna kopia
    st.zaloz_baze(wiersze=1)
    assert st.zainstaluj(paczka) == I.KOD_SAMOKONTROLA_CZERWONA
    assert [stan_bazy(k)[2] for k in kopie_bazy(st)] == [3, 4]  # baza sie zmienila: nowa kopia, stara zostaje


@pytest.mark.parametrize("nr_zamiany", [1, 2])
@pytest.mark.parametrize("blad", [PermissionError(13, "Access is denied"), Zabicie()], ids=["blad_systemu", "zabicie"])
def test_p2_przerwane_przywrocenie_kopii_nie_zostawia_stanowiska_bez_bazy(zainstalowane, tmp_path, capsys, monkeypatch, nr_zamiany, blad):
    """Blad systemu albo zabicie przy ktorejkolwiek zamianie plikow w folderze bazy: plik bazy caly czas istnieje i jest caly,
    komunikat "wersja biezaca bez zmian" jest prawdziwy, a ponowny powrot dokonuje przywrocenia (nie konczy "GOTOWY" bez bazy)."""
    st = zainstalowane
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "2.0", migracje="{1: (), 2: ()}")) == 0
    st.zaloz_baze(schemat=2, wiersze=2)
    prawdziwe, licznik = os.replace, {"n": 0}

    def zamiana(a, b):
        if Path(b).parent in (st.baza.parent, st.baza.parent / "kopie"):
            licznik["n"] += 1
            if licznik["n"] == nr_zamiany:
                raise blad
        return prawdziwe(a, b)

    monkeypatch.setattr(I.os, "replace", zamiana)
    capsys.readouterr()
    try:
        kod = st.wroc(przywroc=True)
    except Zabicie:
        kod = None
    monkeypatch.setattr(I.os, "replace", prawdziwe)
    wyjscie = capsys.readouterr().out
    assert licznik["n"] >= nr_zamiany  # blad naprawde wstrzykniety
    assert st.baza.is_file() and stan_bazy(st.baza) == ([("ok",)], 2, 5, 0)  # baza jest i jest cala (nadal wersja 2.0)
    assert st.biezaca == "2.0" and st.poprzednia == "1.0"
    if kod is not None:
        assert kod == I.KOD_INSTALACJA and "POWROT: NIEUDANA (kod 6) - wersja biezaca bez zmian: 2.0" in wyjscie
        assert not st.baza.with_name(st.baza.name + ".nowy").exists()
    assert st.wroc(przywroc=True) == 0  # ponowna proba: pelne przywrocenie
    assert "POWROT: GOTOWY - wersja biezaca 1.0" in capsys.readouterr().out
    assert stan_bazy(st.baza) == ([("ok",)], 1, 3, 0) and st.biezaca == "1.0"
    assert 5 in [stan_bazy(k)[2] for k in kopie_bazy(st, "stanowisko_odlozona_v2_*.sqlite")]  # baza v2 odlozona, nie skasowana
    assert not st.baza.with_name(st.baza.name + ".nowy").exists()


def test_p2_plik_nowy_bez_bazy_zatrzymuje_powrot_i_instalacje(zainstalowane, tmp_path, capsys):
    """Stan po przerwanym przywroceniu w starszym instalatorze: bazy nie ma, lezy ``<baza>.nowy``. Program zalozylby PUSTA
    baze - instalator i powrot zatrzymuja sie i mowia, co przywrocic; niczego sami nie zgaduja."""
    st = zainstalowane
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "2.0", migracje="{1: (), 2: ()}")) == 0
    st.zaloz_baze(schemat=2, wiersze=2)
    nowy = st.baza.with_name(st.baza.name + ".nowy")
    os.replace(st.baza, nowy)
    tresc = nowy.read_bytes()
    capsys.readouterr()
    assert st.wroc(przywroc=True) == I.KOD_INSTALACJA
    wyjscie = capsys.readouterr().out
    assert "nie ma pliku bazy" in wyjscie and "stanowisko.sqlite.nowy" in wyjscie and "POWROT: GOTOWY" not in wyjscie
    assert st.biezaca == "2.0" and st.poprzednia == "1.0"
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "3.0")) == I.KOD_INSTALACJA
    assert "nie ma pliku bazy" in capsys.readouterr().out and st.biezaca == "2.0" and I.stan_wersji(st.katalog, "3.0") == "brak"
    assert not st.baza.exists() and nowy.read_bytes() == tresc


def test_p3_drugi_powrot_przywraca_najnowsza_kopie(zainstalowane, tmp_path, capsys):
    """N -> N+1 (migracja, kopia A) -> powrot z przywroceniem -> praca na N -> Wroc do N+1 (program N+1 migruje ponownie i sam
    robi kopie) -> drugi powrot: wraca stan sprzed DRUGIEJ migracji (7 skanow), nie stara kopia A (3 skany)."""
    st = zainstalowane
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "2.0", migracje="{1: (), 2: ()}")) == 0  # kopia A: 3 skany, v1
    kopia_a = kopie_bazy(st)[0]
    st.zaloz_baze(schemat=2, wiersze=2)                       # program 2.0: migracja, 5 skanow
    assert st.wroc(przywroc=True) == 0 and stan_bazy(st.baza)[1:3] == (1, 3)   # powrot nr 1: wraca A
    st.zaloz_baze(schemat=1, wiersze=4)                       # praca na 1.0: 7 skanow
    capsys.readouterr()
    assert st.wroc() == 0 and st.biezaca == "2.0"             # "powrot" do nowszej: wersja 2.0 zmieni schemat przy starcie
    wyjscie = capsys.readouterr().out
    przed_druga = [k for k in kopie_bazy(st, "*_przed_2.0_*_v1.sqlite") if k != kopia_a]
    assert len(przed_druga) == 1 and stan_bazy(przed_druga[0])[2] == 7 and f"kopia bazy: kopie/{przed_druga[0].name}" in wyjscie
    kopia_programu = st.baza.with_name("stanowisko.kopia_v1_20261127_080000.sqlite")  # baza.py: kopia programu sprzed migracji
    shutil.copyfile(st.baza, kopia_programu)
    st.zaloz_baze(schemat=2, wiersze=1)                       # program 2.0: druga migracja, 8 skanow
    capsys.readouterr()
    assert st.wroc() == I.KOD_BAZA_NOWSZA                     # ostrzezenie liczy od najnowszej kopii: +1, nie +5
    wyjscie = capsys.readouterr().out
    assert f"Kopia sprzed aktualizacji: {kopia_programu.name}" in wyjscie and "tabela skany: 7 w kopii, 8 teraz (+1)" in wyjscie
    assert "starszych kopii: 2" in wyjscie
    assert st.wroc(przywroc=True) == 0                        # powrot nr 2
    assert stan_bazy(st.baza) == ([("ok",)], 1, 7, 0) and st.biezaca == "1.0"
    kopia_programu.unlink()                                   # bez kopii programu: nastepna w kolejnosci jest kopia instalatora z powrotu
    st.zaloz_baze(schemat=2, wiersze=0)
    assert st.wroc() == 0 and st.wroc(przywroc=True) == 0 and stan_bazy(st.baza)[1:3] == (1, 7)


# ------------------------------------------------------------- runda 2: katalogi wersji (obce, pisownia numeru, naprawa)

def test_p4_obce_podkatalogi_wersje_zostaja_nietkniete(st, tmp_path, capsys):
    """``/katalog`` wskazuje katalog, w ktorym jest juz podkatalog ``wersje`` z czyms cudzym: instalator usuwa wylacznie
    katalogi, ktore sam oznaczyl znacznikiem ``NIEDOKONCZONA.txt``."""
    st.ustawienia_gotowe()
    wersje = st.katalog / "wersje"
    obce = [wersje / "projekt 2025 - wersja robocza" / "wazne.txt", wersje / "archiwum2024" / "dane.txt", wersje / "9.9" / "notatki.txt"]
    for plik in obce:
        plik.parent.mkdir(parents=True)
        plik.write_text("dane uzytkownika\n", encoding="ascii")
    (wersje / "7.7").mkdir()  # pusty katalog o nazwie jak numer wersji
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "1.0")) == 0
    wyjscie = capsys.readouterr().out
    assert all(p.read_text(encoding="ascii") == "dane uzytkownika\n" for p in obce) and (wersje / "7.7").is_dir()
    assert "usunieto" not in wyjscie and "nie zalozyl ich instalator" in wyjscie and st.biezaca == "1.0"
    assert "projekt 2025" not in st.dziennik()  # nazwy cudzych katalogow nie trafiaja do dziennika
    # paczka o numerze, pod ktorym lezy cudzy katalog: stop, katalog nietkniety
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "9.9")) == I.KOD_INSTALACJA
    assert "nie zalozyl go instalator" in capsys.readouterr().out and obce[2].is_file() and st.biezaca == "1.0"
    assert I.wersje(st.katalog, usun="9.9") == I.KOD_BRAK_WERSJI and obce[2].is_file()  # Wersje.cmd /usun tez go nie ruszy
    capsys.readouterr()
    assert I.wersje(st.katalog) == 0
    lista = capsys.readouterr().out
    assert "projekt 2025" not in lista and [w.split()[0] for w in lista.splitlines()] == ["1.0", "7.7", "9.9", "archiwum2024"]
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "7.7")) == 0 and st.biezaca == "7.7"  # pusty katalog o numerze paczki nie przeszkadza


def test_p5_numer_rozniacy_sie_wielkoscia_liter_nie_wymienia_wersji_biezacej(st, tmp_path, capsys):
    """W Windows ``wersje\\1.0-rc1`` i ``wersje\\1.0-RC1`` to ten sam katalog: paczka o takim numerze nie moze podmienic
    wersji biezacej budowa, ktora nie przeszla samokontroli."""
    st.ustawienia_gotowe()
    assert st.zainstaluj(zbuduj_paczke(tmp_path / "a", "1.0-rc1")) == 0
    przed = pliki_wersji(st)
    capsys.readouterr()
    assert st.zainstaluj(zbuduj_paczke(tmp_path / "b", "1.0-RC1", kod_samokontroli=1)) == I.KOD_PACZKA
    wyjscie = capsys.readouterr().out
    assert "zapisanym inaczej (1.0-rc1)" in wyjscie and "INSTALACJA: NIEUDANA (kod 3) - wersja biezaca bez zmian: 1.0-rc1" in wyjscie
    assert pliki_wersji(st) == przed and st.biezaca == "1.0-rc1" and st.srodowisko.instalacje == 1
    assert sorted(p.name for p in (st.katalog / "wersje").iterdir()) == ["1.0-rc1"]
    assert I.wersje(st.katalog, usun="1.0-RC1") == I.KOD_BRAK_WERSJI and pliki_wersji(st) == przed  # usuwanie tez nie da sie oszukac


def przerob_wydanie(paczka: Path, **zmiany) -> None:
    """Zmienia pola ``wydanie.json`` rozpakowanej paczki i poprawia jego sume w ``SHA256SUMS`` (paczka zbudowana recznie)."""
    plik = paczka / "wydanie.json"
    stara = sha(plik)
    plik.write_text(json.dumps(dict(json.loads(plik.read_text(encoding="ascii")), **zmiany), indent=1, sort_keys=True) + "\n", encoding="ascii")
    sumy = paczka / "SHA256SUMS"
    sumy.write_bytes(sumy.read_bytes().replace(stara.encode("ascii"), sha(plik).encode("ascii")))


@pytest.mark.parametrize("numer", ["1.0.", "1.0 ", "1.0-", ".1", "nul", "COM1.5", "a/b", "1" * 33])
def test_p5_paczka_z_numerem_ktory_windows_zapisze_inaczej_jest_odrzucana(zainstalowane, tmp_path, capsys, numer):
    """``1.0.`` to w Windows katalog ``1.0`` - taki numer nie przechodzi ani w budowie, ani w instalatorze."""
    st = zainstalowane
    paczka = zbuduj_paczke(tmp_path / "b", "1.0", kod_samokontroli=1)
    przerob_wydanie(paczka, wersja=numer)
    przed = pliki_wersji(st)
    capsys.readouterr()
    assert st.zainstaluj(paczka) == I.KOD_PACZKA
    assert "niepoprawny numer wersji" in capsys.readouterr().out and pliki_wersji(st) == przed and st.biezaca == "1.0"
    with pytest.raises(ZW.BladBudowy, match="numer wersji"):
        ZW.zbuduj(tmp_path / "wy", kola_testowe(tmp_path / "kola"), zrodlo=drzewo_programu(tmp_path / "zrodlo"), data=DATA, wersja=numer)


def test_p5_nieudana_naprawa_wersji_biezacej_przywraca_ja(zainstalowane, tmp_path, capsys):
    """Naprawa wersji BIEZACEJ (uszkodzony plik) przerwana w kroku pip: katalog wersji wraca do stanu sprzed naprawy, wiec
    wiersz koncowy "wersja biezaca bez zmian" jest prawda i ``Stanowisko.cmd`` nadal ja uruchamia."""
    st = zainstalowane
    paczka = zbuduj_paczke(tmp_path / "ponownie", "1.0")
    (st.katalog / "wersje" / "1.0" / "program" / "stanowisko" / "aplikacja.py").write_text("uszkodzony\n", encoding="ascii")
    przed = pliki_wersji(st)
    for blad in (I.BladInstalacji(I.KOD_INSTALACJA, "pip zakonczyl sie bledem (kod 1)", "rada"), KeyboardInterrupt()):
        st.srodowisko.blad_pip = blad
        capsys.readouterr()
        assert st.zainstaluj(paczka) == I.KOD_INSTALACJA
        wyjscie = capsys.readouterr().out
        assert "przywrocono katalog wersji 1.0 sprzed naprawy" in wyjscie
        assert wyjscie.strip().splitlines()[-1] == "INSTALACJA: NIEUDANA (kod 6) - wersja biezaca bez zmian: 1.0"
        assert I.stan_wersji(st.katalog, "1.0") == "zainstalowana" and pliki_wersji(st) == przed
        assert sorted(p.name for p in (st.katalog / "wersje").iterdir()) == ["1.0"] and st.biezaca == "1.0"
    st.srodowisko.blad_pip = None
    assert st.zainstaluj(paczka) == 0 and sorted(p.name for p in (st.katalog / "wersje").iterdir()) == ["1.0"]
    program = st.katalog / "wersje" / "1.0" / "program"
    assert I.sprawdz_sumy(program, I.wczytaj_sumy(program / I.PLIK_SUM_PROGRAMU)) == []


def test_p5_wymiana_wersji_przerwana_zabiciem_jest_cofana_a_komunikat_mowi_prawde(zainstalowane, tmp_path, capsys):
    """Stan po zamknieciu okna w trakcie naprawy wersji biezacej: stara wersja lezy odlozona (``_stara_1.0``), nowy katalog ma
    znacznik. Instalator nie twierdzi wtedy "wersja biezaca bez zmian", a nastepna proba najpierw przywraca stara wersje."""
    st = zainstalowane
    wersje = st.katalog / "wersje"
    przed = pliki_wersji(st)
    os.rename(wersje / "1.0", wersje / "_stara_1.0")
    (wersje / "1.0").mkdir()
    (wersje / "1.0" / I.ZNACZNIK_NIEDOKONCZONEJ).write_text("przerwana\r\n", encoding="ascii")
    zepsuta = zbuduj_paczke(tmp_path, "2.0")
    (zepsuta / "program" / "WERSJA").write_text("zepsute\n", encoding="ascii")
    capsys.readouterr()
    assert st.zainstaluj(zepsuta) == I.KOD_PACZKA  # blad przed sprzataniem: wersja biezaca nadal niekompletna
    koniec = capsys.readouterr().out.strip().splitlines()[-1]
    assert koniec.startswith("INSTALACJA: NIEUDANA (kod 3) - UWAGA: wersja biezaca 1.0 jest niekompletna") and "bez zmian" not in koniec
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "3.0")) == 0
    wyjscie = capsys.readouterr().out
    assert "przywrocono wersje 1.0 sprzed przerwanej wymiany" in wyjscie
    assert {n: s for n, s in pliki_wersji(st).items() if n.startswith("wersje/1.0/")} == przed
    assert sorted(p.name for p in wersje.iterdir()) == ["1.0", "3.0"] and st.biezaca == "3.0" and st.poprzednia == "1.0"


# --------------------------------------------------------------------- runda 2: izolacja srodowiska (P6), decyzje, drobne

def test_p6_polecenia_srodowiska_bez_sieci_i_bez_pakietow_bazowych(tmp_path, monkeypatch):
    """Polecenia ``python -m venv`` i ``pip install``, ktore wykonuje instalator (atrapa srodowiska ich nie sprawdza)."""
    polecenia = []
    srodowisko = I.Srodowisko()
    venv, lista = tmp_path / "venv", tmp_path / "zamrozone.txt"

    def falszywe(polecenie, **_):
        polecenia.append([str(c) for c in polecenie])
        if "venv" in polecenia[-1]:
            srodowisko.python(venv).parent.mkdir(parents=True)
            srodowisko.python(venv).write_bytes(b"")
        return subprocess.CompletedProcess(polecenie, 0, "True\n", "")

    monkeypatch.setattr(I, "uruchom", falszywe)
    srodowisko.utworz(PYTHON, venv)
    srodowisko.instaluj(venv, [tmp_path / "kola", tmp_path / "kola_testy"], lista, tmp_path / "pip.log")
    tworzenie, proba, pip = polecenia
    assert tworzenie == [str(PYTHON), "-I", "-m", "venv", "--copies", str(venv)]  # bez --system-site-packages, bez dowiazan
    assert proba[:2] == [str(srodowisko.python(venv)), "-I"]
    assert pip[:5] == [str(srodowisko.python(venv)), "-I", "-m", "pip", "install"] and pip[-2:] == ["-r", str(lista)]
    for opcja in ("--no-index", "--isolated", "--only-binary=:all:", "--no-cache-dir"):
        assert pip.count(opcja) == 1, opcja
    assert [pip[i + 1] for i, c in enumerate(pip) if c == "--find-links"] == [str(tmp_path / "kola"), str(tmp_path / "kola_testy")]
    zakazane = ("--index-url", "--extra-index-url", "-i", "--trusted-host", "--proxy", "--pre", "--no-binary", "--system-site-packages")
    assert not [c for c in pip + tworzenie if c.split("=")[0] in zakazane or "://" in c]


def test_powrot_pyta_t_n_i_pokazuje_wersje(zainstalowane, tmp_path, capsys, monkeypatch):
    """``Wroc_do_poprzedniej.cmd`` bez opcji pyta T / N (z jakiej wersji na jaka); ``/tak`` pomija pytanie (skrypty, T12)."""
    st = zainstalowane
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "2.0")) == 0
    pytania = []

    def odpowiedz(tekst):
        def potwierdz(pytanie):
            pytania.append(pytanie)
            return tekst
        return potwierdz

    capsys.readouterr()
    assert st.wroc(potwierdz=odpowiedz(False)) == I.KOD_ANULOWANO == 11
    wyjscie = capsys.readouterr().out
    assert pytania == ["Powrot z wersji 2.0 do wersji 1.0. Kontynuowac? [T/N]: "]
    assert "POWROT: ANULOWANY (kod 11) - wersja biezaca bez zmian: 2.0" in wyjscie and st.biezaca == "2.0" and st.poprzednia == "1.0"
    assert st.wroc(potwierdz=odpowiedz(True)) == 0 and st.biezaca == "1.0" and len(pytania) == 2
    # wiersz polecen: bez /tak pytanie idzie na konsole (brak odpowiedzi = N), /tak go nie zadaje
    wejscie = iter(["n", "T"])
    monkeypatch.setattr(I, "Srodowisko", SrodowiskoAtrapa)  # main() nie przyjmuje atrapy srodowiska
    monkeypatch.setattr("builtins.input", lambda pytanie="": next(wejscie))
    assert I.main(["wroc", "/katalog", str(st.katalog), "/bez-pauzy"]) == I.KOD_ANULOWANO and st.biezaca == "1.0"
    assert I.main(["wroc", "/katalog", str(st.katalog), "/bez-pauzy"]) == 0 and st.biezaca == "2.0"

    def brak_konsoli(pytanie=""):
        raise EOFError

    monkeypatch.setattr("builtins.input", brak_konsoli)
    assert I.main(["wroc", "/katalog", str(st.katalog)]) == I.KOD_ANULOWANO and st.biezaca == "2.0"
    assert I.main(["wroc", "/katalog", str(st.katalog), "/tak", "/bez-pauzy"]) == 0 and st.biezaca == "1.0"


def test_python_inna_wersja_poprawkowa_przyjeta_z_ostrzezeniem_w_dzienniku(st, tmp_path, capsys, monkeypatch):
    """Sprawdzona wersja Pythona jest w ``wydanie.json``; inne 3.12.x (64-bit) przechodza z wierszem OSTRZEZENIE w dzienniku."""
    st.ustawienia_gotowe()
    paczka = zbuduj_paczke(tmp_path, "1.0")
    assert json.loads((paczka / "wydanie.json").read_text(encoding="ascii"))["python_sprawdzony"] == "3.12.10"
    prawdziwe = I.uruchom

    def falszywe(polecenie, **kw):
        if "-c" in polecenie and "struct" in polecenie[polecenie.index("-c") + 1]:
            return subprocess.CompletedProcess(polecenie, 0, "3.12.7 64\n", "")
        return prawdziwe(polecenie, **kw)

    monkeypatch.setattr(I, "uruchom", falszywe)
    assert st.zainstaluj(paczka) == 0
    ostrzezenie = "OSTRZEZENIE: Python 3.12.7 - paczka byla sprawdzana na Pythonie 3.12.10"
    assert ostrzezenie in capsys.readouterr().out and ostrzezenie in st.dziennik()
    monkeypatch.setattr(I, "uruchom", lambda polecenie, **kw: subprocess.CompletedProcess(polecenie, 0, "3.12.10 64\n", "")
                        if "-c" in polecenie and "struct" in polecenie[polecenie.index("-c") + 1] else prawdziwe(polecenie, **kw))
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "2.0")) == 0
    assert "OSTRZEZENIE: Python" not in capsys.readouterr().out and st.dziennik().count("OSTRZEZENIE: Python") == 1


def test_d2_drugi_instalator_w_tym_samym_katalogu_czeka_na_pierwszego(zainstalowane, tmp_path, capsys):
    """Podwojny dwuklik ``zainstaluj.cmd``: drugi nie sprzata "niedokonczonej" wersji pierwszego, tylko odmawia."""
    st = zainstalowane
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "2.0")) == 0
    paczka = zbuduj_paczke(tmp_path, "3.0")
    wynik = {}

    class Pierwszy(SrodowiskoAtrapa):
        def instaluj(self, venv, katalogi_kol, lista, dziennik_pip):
            if not wynik:  # pierwszy instalator jest w kroku pip - w tym momencie rusza drugi (ta sama paczka, ten sam katalog)
                wynik["kod"] = I.zainstaluj(paczka, st.katalog, PYTHON, srodowisko=SrodowiskoAtrapa(), zegar=st.zegar, bez_sieci=True)
                wynik["powrot"] = I.wroc(st.katalog, srodowisko=SrodowiskoAtrapa(), zegar=st.zegar)
                wynik["znacznik"] = (venv.parent / I.ZNACZNIK_NIEDOKONCZONEJ).is_file()
            return super().instaluj(venv, katalogi_kol, lista, dziennik_pip)

    st.srodowisko = Pierwszy()
    capsys.readouterr()
    assert st.zainstaluj(paczka) == 0 and st.biezaca == "3.0" and st.poprzednia == "2.0"
    wyjscie = capsys.readouterr().out
    assert wynik == {"kod": I.KOD_INSTALACJA, "powrot": I.KOD_INSTALACJA, "znacznik": True}
    assert wyjscie.count("BLAD: inna instalacja albo powrot juz trwa") == 2 and "usunieto niedokonczona" not in wyjscie
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "4.0")) == 0  # blokada zwolniona po zakonczeniu


@pytest.mark.parametrize("zmiana, kod, fragment", [
    ("pusty_millbox", 0, "INSTALACJA: GOTOWA"),                       # pusta wartosc to nie sciezka wzgledna
    ("bom", I.KOD_USTAWIENIA, "UTF-8 bez BOM"),                       # Notatnik "UTF-8 z BOM": podpowiedz o kodowaniu
    ("crlf", 0, "INSTALACJA: GOTOWA"),
])
def test_d4_ustawienia_pusty_folder_bom_crlf(st, tmp_path, capsys, zmiana, kod, fragment):
    plik = st.ustawienia_gotowe()
    tresc = plik.read_bytes()
    if zmiana == "pusty_millbox":
        assert b'folder_millbox = "C:/MillBox/raporty"' in tresc
        tresc = tresc.replace(b'folder_millbox = "C:/MillBox/raporty"', b'folder_millbox = ""')
    elif zmiana == "bom":
        tresc = b"\xef\xbb\xbf" + tresc
    else:
        tresc = tresc.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    plik.write_bytes(tresc)
    assert st.zainstaluj(zbuduj_paczke(tmp_path, "1.0")) == kod
    assert fragment in capsys.readouterr().out and plik.read_bytes() == tresc


def test_d5_srednik_w_sciezce_katalogu_instalacji(st, tmp_path, capsys):
    paczka = zbuduj_paczke(tmp_path, "1.0")
    katalog = tmp_path / "a;b" / "Stanowisko"
    assert I.zainstaluj(paczka, katalog, PYTHON, srodowisko=st.srodowisko) == I.KOD_INSTALACJA
    wyjscie = capsys.readouterr().out
    assert "srednik" in wyjscie and "/katalog" in wyjscie and not katalog.exists() and st.srodowisko.instalacje == 0


# --------------------------------------------------------------- prawdziwe srodowisko wirtualne i skrypty .cmd (Windows)

@pytest.mark.skipif(os.name != "nt", reason="skrypty .cmd dzialaja tylko w Windows")
def test_zainstaluj_cmd_prawdziwe_srodowisko_i_skrypty(st, tmp_path):
    """Jedyny test z prawdziwym ``python -m venv`` i pip (jedno male kolo, bez sieci): zainstaluj.cmd -> Stanowisko.cmd -> Wersje.cmd.

    Wszystkie skrypty dostaja WROGIE srodowisko (P6): ``PYTHONPATH`` = pakiety interpretera bazowego, ``PYTHONHOME`` = katalog,
    ktorego nie ma. Skrypt, ktory by ich nie wyczyscil, nie uruchomi Pythona albo wczyta pakiety spoza srodowiska wersji."""
    paczka = Path(shutil.move(zbuduj_paczke(tmp_path, "1.0"), tmp_path / "Paczka ze spacja"))  # sciezki ze spacjami: paczka i katalog
    st.katalog = tmp_path / "Katalog ze spacja" / "Stanowisko"
    st.ustawienia_gotowe()
    bazowe = Path(sys.base_prefix) / "Lib" / "site-packages"
    srodowisko = {k: v for k, v in os.environ.items() if k.upper() != "STANOWISKO_PYTHON"}
    srodowisko.update(PYTHONPATH=str(bazowe), PYTHONHOME=str(tmp_path / "zly_pythonhome"))

    def cmd(*polecenie) -> subprocess.CompletedProcess:
        # cmd /s /c "<calosc>": zewnetrzne cudzyslowy zdejmuje cmd, wiec sciezki ze spacjami tez dzialaja
        return subprocess.run('cmd /s /c "' + subprocess.list2cmdline(list(map(str, polecenie))) + '"', capture_output=True, text=True,
                              encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL, env=srodowisko, timeout=600)

    def ostatni(wynik) -> str:
        return wynik.stdout.strip().splitlines()[-1]

    # zly Python wskazany wprost: stop z kodem 4, zanim cokolwiek powstanie; z opcjami okno tez czeka na klawisz (D3) - chyba ze /bez-pauzy
    wynik = cmd(paczka / "zainstaluj.cmd", "/katalog", st.katalog, "/python", tmp_path / "nie_ma" / "python.exe", "/bez-pauzy")
    assert wynik.returncode == I.KOD_PYTHON and "brak Pythona - opcja /python wskazuje plik, ktorego nie ma" in wynik.stdout
    assert ostatni(wynik) == "INSTALACJA: NIEUDANA (kod 4) - niczego nie zmieniono." and not (st.katalog / "wersje").exists()
    z_pauza = cmd(paczka / "zainstaluj.cmd", "/katalog", st.katalog, "/python", tmp_path / "nie_ma" / "python.exe")
    assert z_pauza.returncode == I.KOD_PYTHON and z_pauza.stdout.startswith(wynik.stdout.rstrip())
    assert len(z_pauza.stdout.strip().splitlines()) == len(wynik.stdout.strip().splitlines()) + 1  # wiersz polecenia pause
    # poprawny Python mimo PYTHONHOME z zewnatrz (D1): zainstaluj.cmd sam czysci PYTHONHOME / PYTHONPATH
    wynik = cmd(paczka / "zainstaluj.cmd", "/katalog", st.katalog, "/python", sys.executable, "/bez-sieci", "/testy", "/bez-pauzy")
    assert wynik.returncode == 0, wynik.stdout + wynik.stderr
    assert "pakiety zgodne z lista zamrozona: 2 z 2" in wynik.stdout and ostatni(wynik).startswith("INSTALACJA: GOTOWA - wersja biezaca 1.0")
    venv = st.katalog / "wersje" / "1.0" / "venv"
    assert (venv / "Scripts" / "python.exe").is_file() and (st.katalog / "wersje" / "1.0" / "pip.log").is_file()
    wynik = cmd(st.katalog / "Stanowisko.cmd", "--atrapa", "--zamknij-po", "1")
    assert wynik.returncode == 0 and "STANOWISKO wersja=1.0 atrapa=True ustawienia=True" in wynik.stdout, wynik.stdout + wynik.stderr
    wynik = cmd(st.katalog / "Polecenie.cmd", "-c", "import sys, os, pakiecik, testowy; print(sys.prefix); print(sys.path); "
                "print('ZMIENNE', os.environ.get('PYTHONPATH'), os.environ.get('PYTHONHOME'))")
    assert wynik.returncode == 0 and str(venv).lower() in wynik.stdout.splitlines()[0].lower(), wynik.stdout + wynik.stderr
    assert str(bazowe).replace("\\", "\\\\").lower() not in wynik.stdout.lower()  # srodowisko wersji nie widzi pakietow interpretera bazowego
    assert "ZMIENNE None None" in wynik.stdout
    wynik = cmd(st.katalog / "Samokontrola.cmd", "--bez-sieci")
    assert wynik.returncode == 0 and "SAMOKONTROLA: ZIELONA" in wynik.stdout and "OK sumy: zgodne" in wynik.stdout
    wynik = cmd(st.katalog / "Wersje.cmd", "/bez-pauzy")
    assert wynik.returncode == 0 and wynik.stdout.split()[0] == "1.0" and "BIEZACA" in wynik.stdout
    z_pauza = cmd(st.katalog / "Wersje.cmd")
    assert z_pauza.returncode == 0 and len(z_pauza.stdout.strip().splitlines()) == len(wynik.stdout.strip().splitlines()) + 1
    wynik = cmd(st.katalog / "Wroc_do_poprzedniej.cmd", "/bez-pauzy")
    assert wynik.returncode == I.KOD_BRAK_WERSJI and "nie ma poprzedniej wersji" in wynik.stdout
    assert ostatni(wynik).startswith("POWROT: NIEUDANA (kod 9)")
    assert not list((st.katalog / "wersje" / "1.0" / "program").rglob("__pycache__"))
