"""narzedzia/zbuduj_wydanie.py (E3-A11i): paczka wydania na malym sztucznym drzewie w tmp_path, bez sieci.

Pomocnicze ``drzewo_programu`` / ``zbuduj_paczke`` buduja mala paczke (prawdziwy instalator i wzory skryptow, atrapa
samokontroli wg umowy A11s, dwa reczne kola pip) - uzywa ich takze ``test_instalacja.py``.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import shutil
import subprocess
import zipfile
from pathlib import Path

import pytest

import zbuduj_wydanie as ZW
from instalacja import instalator as I

STANOWISKO = Path(__file__).resolve().parent.parent
DATA = dt.datetime(2026, 11, 20, 12, 0, 0, tzinfo=dt.timezone.utc)

# Atrapa samokontroli wg umowy A11s (zlecenie a11s.md, "Umowa"): opcje, wiersze OK / OSTRZEZENIE / BLAD, wiersz koncowy,
# kody 0 / 1 / 2, --sumy liczone naprawde. BLAD, gdy folder skanera albo Cyrkon z [sciezki] nie istnieje.
ATRAPA_SAMOKONTROLI = '''"""ATRAPA samokontroli wg umowy A11s - tylko do prob instalatora (prawdziwy modul: paczka E3-A11s)."""
import argparse
import hashlib
import sys
import tomllib
from pathlib import Path

KOD_WYMUSZONY = None


def main(argv=None):
    p = argparse.ArgumentParser(prog="stanowisko.samokontrola")
    p.add_argument("--ustawienia")
    p.add_argument("--sumy")
    p.add_argument("--json", action="store_true")
    p.add_argument("--bez-sieci", action="store_true")
    a = p.parse_args(argv)
    if KOD_WYMUSZONY == 2:
        print("Samokontroli nie dalo sie wykonac (atrapa: kod wymuszony 2).")
        return 2
    try:
        ust = tomllib.loads(Path(a.ustawienia).read_text(encoding="utf-8"))
        sciezki = ust["sciezki"]
    except Exception as e:
        print("Nie mozna wczytac pliku ustawien (%s) - popraw plik i uruchom samokontrole ponownie." % type(e).__name__)
        return 2
    wiersze = [("OK", "python", "Python %d.%d" % sys.version_info[:2], "")]
    program = Path(__file__).resolve().parent.parent
    if a.sumy:
        roznice, n = [], 0
        for wiersz in Path(a.sumy).read_text(encoding="utf-8").splitlines():
            suma, nazwa = wiersz.split("  ", 1)
            n += 1
            plik = program / nazwa
            if not plik.is_file() or hashlib.sha256(plik.read_bytes()).hexdigest() != suma:
                roznice.append(nazwa)
        if roznice:
            wiersze.append(("BLAD", "sumy", "pliki programu niezgodne: " + ", ".join(roznice[:10]), "zainstaluj program ponownie"))
        else:
            wiersze.append(("OK", "sumy", "zgodne %d z %d" % (n, n), ""))
    for klucz in ("folder_eksportu_skanera", "folder_cyrkon"):
        if Path(sciezki[klucz]).is_dir():
            wiersze.append(("OK", klucz, "folder istnieje", ""))
        else:
            wiersze.append(("BLAD", klucz, "folder nie istnieje", "popraw [sciezki] %s w pliku ustawien" % klucz))
    wiersze.append(("OSTRZEZENIE", "ramki", "pominieto" if a.bez_sieci else "ramki nieobecne", "wlacz ramki przed praca"))
    if KOD_WYMUSZONY == 1:
        wiersze.append(("BLAD", "wymuszony", "blad wymuszony w atrapie", "to tylko proba"))
    for poziom, kod, opis, rada in wiersze:
        print("%s %s: %s" % (poziom, kod, opis) + ("; " + rada if rada else ""))
    ok = sum(1 for w in wiersze if w[0] == "OK")
    ostrzezenia = sum(1 for w in wiersze if w[0] == "OSTRZEZENIE")
    bledy = sum(1 for w in wiersze if w[0] == "BLAD")
    if bledy:
        print("SAMOKONTROLA: CZERWONA (ok %d, ostrzezenia %d, bledy %d)" % (ok, ostrzezenia, bledy))
        return 1
    print("SAMOKONTROLA: ZIELONA (ok %d, ostrzezenia %d)" % (ok, ostrzezenia))
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''

ATRAPA_BAZY = '''"""Atrapa modulu baza: tylko to, o co pyta instalator (wersja schematu, plik bazy)."""
from pathlib import Path

from .ustawienia import KORZEN

MIGRACJE = {MIGRACJE}


def sciezka_bazy(ust):
    p = Path(ust["sciezki"]["baza"])
    return p if p.is_absolute() else KORZEN / p
'''

ATRAPA_APLIKACJI = '''"""Atrapa programu: wypisuje wersje i konczy (proba uruchomienia przez Stanowisko.cmd)."""
import argparse
import sys
from pathlib import Path


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--ustawienia")
    p.add_argument("--atrapa", action="store_true")
    p.add_argument("--zamknij-po", type=float, default=None)
    a = p.parse_args(argv)
    wersja = (Path(__file__).resolve().parent.parent / "WERSJA").read_text(encoding="ascii").strip()
    print("STANOWISKO wersja=%s atrapa=%s ustawienia=%s" % (wersja, a.atrapa, Path(a.ustawienia).is_file()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''


def kolo(katalog: Path, nazwa: str, wersja: str, znacznik: str = "py3-none-any") -> Path:
    """Minimalne kolo pip z jednym modulem (instalowalne przez prawdziwego pip bez sieci)."""
    katalog.mkdir(parents=True, exist_ok=True)
    plik = katalog / f"{nazwa}-{wersja}-{znacznik}.whl"
    info = f"{nazwa}-{wersja}.dist-info"
    tresc = {f"{nazwa}/__init__.py": f'WERSJA = "{wersja}"\n',
             f"{info}/METADATA": f"Metadata-Version: 2.1\nName: {nazwa}\nVersion: {wersja}\n",
             f"{info}/WHEEL": f"Wheel-Version: 1.0\nGenerator: test\nRoot-Is-Purelib: true\nTag: {znacznik}\n"}
    tresc[f"{info}/RECORD"] = "".join(f"{n},,\n" for n in tresc) + f"{info}/RECORD,,\n"
    with zipfile.ZipFile(plik, "w") as z:
        for n, t in tresc.items():
            z.writestr(zipfile.ZipInfo(n, date_time=(2026, 11, 20, 12, 0, 0)), t)
    return plik


def drzewo_programu(katalog: Path, *, migracje: str = "{1: ()}", kod_samokontroli: int | None = None, samokontrola: bool = True) -> Path:
    """Male drzewo ``stanowisko/`` w tmp: prawdziwe ``ustawienia.py``, wzor ustawien i ``instalacja/``, reszta atrapy."""
    (katalog / "stanowisko").mkdir(parents=True)
    (katalog / "stanowisko" / "__init__.py").write_text('"""Atrapa pakietu programu."""\n', encoding="ascii")
    shutil.copyfile(STANOWISKO / "stanowisko" / "ustawienia.py", katalog / "stanowisko" / "ustawienia.py")
    (katalog / "stanowisko" / "baza.py").write_text(ATRAPA_BAZY.replace("{MIGRACJE}", migracje), encoding="ascii")
    (katalog / "stanowisko" / "aplikacja.py").write_text(ATRAPA_APLIKACJI, encoding="ascii")
    if samokontrola:
        (katalog / "stanowisko" / "samokontrola.py").write_text(
            ATRAPA_SAMOKONTROLI.replace("KOD_WYMUSZONY = None", f"KOD_WYMUSZONY = {kod_samokontroli}"), encoding="ascii")
    shutil.copyfile(STANOWISKO / "ustawienia.przyklad.toml", katalog / "ustawienia.przyklad.toml")
    (katalog / "requirements.txt").write_text("pakiecik==1.0\npytest==9.1.1\n", encoding="ascii")
    (katalog / "WERSJA").write_text("1.0\n", encoding="ascii")
    shutil.copytree(STANOWISKO / "instalacja", katalog / "instalacja", ignore=shutil.ignore_patterns("__pycache__"))
    (katalog / "instalacja" / "zamrozone.txt").write_text("# lista testowa\npakiecik==1.0\n", encoding="ascii")
    (katalog / "instalacja" / "zamrozone_testy.txt").write_text("testowy==2.0\n", encoding="ascii")
    for nazwa, tresc in (("modele_plytek/wieczorna/uklad.json", "{}"), ("narzedzia/narzedzie.py", "print('narzedzie')\n"),
                         ("ramka/__init__.py", ""), ("instrukcje/wieczor.md", "# instrukcja\n"),
                         # ponizsze NIE moga trafic do paczki
                         ("narzedzia/zbuduj_wydanie.py", "# budowa\n"), ("testy/test_x.py", "def test_x(): pass\n"),
                         ("raporty/raport.md", "raport\n"), ("dane/stanowisko.sqlite", "dane"), ("ustawienia.toml", "[sciezki]\n"),
                         ("stanowisko/__pycache__/baza.cpython-312.pyc", "pyc"), ("opisy_modulow/x.md", "opis\n"), ("README.md", "readme\n")):
        (katalog / nazwa).parent.mkdir(parents=True, exist_ok=True)
        (katalog / nazwa).write_text(tresc, encoding="ascii")
    return katalog


def kola_testowe(katalog: Path) -> Path:
    kolo(katalog, "pakiecik", "1.0")
    kolo(katalog, "testowy", "2.0")
    return katalog


def zbuduj_paczke(tmp: Path, wersja: str = "1.0", **opcje_drzewa) -> Path:
    """Buduje paczke ``wersja`` z malego drzewa i rozpakowuje ja; zwraca katalog rozpakowanej paczki."""
    korzen = tmp / f"budowa_{wersja}"
    bez_samokontroli = opcje_drzewa.get("samokontrola") is False
    wynik = ZW.zbuduj(korzen / "wyjscie", kola_testowe(korzen / "kola"), wersja=wersja, zrodlo=drzewo_programu(korzen / "zrodlo", **opcje_drzewa),
                      data=DATA, bez_samokontroli=bez_samokontroli)
    with zipfile.ZipFile(wynik["plik"]) as z:
        z.extractall(korzen / "paczka")
    return korzen / "paczka"


def sha(plik: Path) -> str:
    return hashlib.sha256(plik.read_bytes()).hexdigest()


# ------------------------------------------------------------------------------------------------------------- testy

def test_dwie_budowy_daja_ten_sam_zip(tmp_path):
    zrodlo, kola = drzewo_programu(tmp_path / "zrodlo"), kola_testowe(tmp_path / "kola")
    a = ZW.zbuduj(tmp_path / "a", kola, zrodlo=zrodlo, data=DATA)
    b = ZW.zbuduj(tmp_path / "b", kola, zrodlo=zrodlo, data=DATA)
    assert a["plik"].name == "Stanowisko_1.0.zip"
    assert a["plik"].read_bytes() == b["plik"].read_bytes()
    assert a["sha256"] == b["sha256"] == sha(a["plik"])
    assert (tmp_path / "a" / "Stanowisko_1.0.zip.sha256").read_text(encoding="ascii") == f"{a['sha256']}  Stanowisko_1.0.zip\n"
    assert a["rozmiar"] == a["plik"].stat().st_size
    with zipfile.ZipFile(a["plik"]) as z:  # liczba plikow w komunikacie = pliki paczki bez samego SHA256SUMS
        assert a["pliki"] == len(z.namelist()) - 1 == len(z.read("SHA256SUMS").splitlines())
    inna_data = ZW.zbuduj(tmp_path / "c", kola, zrodlo=zrodlo, data=DATA + dt.timedelta(days=1))
    assert inna_data["sha256"] != a["sha256"]  # data wpisow wchodzi do paczki - dlatego jest stala (data commita)


def test_zawartosc_paczki(tmp_path):
    paczka = zbuduj_paczke(tmp_path)
    pliki = sorted(p.relative_to(paczka).as_posix() for p in paczka.rglob("*") if p.is_file())
    for nazwa in ("zainstaluj.cmd", "CZYTAJ.txt", "SHA256SUMS", "wydanie.json", "program/SUMY_PROGRAMU.sha256", "program/WERSJA",
                  "program/stanowisko/samokontrola.py", "program/stanowisko/aplikacja.py", "program/modele_plytek/wieczorna/uklad.json",
                  "program/narzedzia/narzedzie.py", "program/ramka/__init__.py", "program/instrukcje/wieczor.md", "program/requirements.txt",
                  "program/ustawienia.przyklad.toml", "program/instalacja/instalator.py", "program/instalacja/wzory/Stanowisko.cmd",
                  "program/instalacja/zamrozone.txt", "kola/pakiecik-1.0-py3-none-any.whl", "kola_testy/testowy-2.0-py3-none-any.whl"):
        assert nazwa in pliki, nazwa
    for fragment in ("program/testy/", "raporty/", "dane/", "__pycache__", ".pyc", "zbuduj_wydanie", "opisy_modulow", "README.md", "program/ustawienia.toml"):
        assert not [n for n in pliki if fragment in n], fragment
    assert "kola/testowy-2.0-py3-none-any.whl" not in pliki  # zestaw testowy osobno, nigdy w kolach programu
    # SHA256SUMS: kazdy plik paczki (poza samym plikiem sum), sumy zgodne
    sumy = I.wczytaj_sumy(paczka / "SHA256SUMS")
    assert sorted(sumy) == [n for n in pliki if n != "SHA256SUMS"]
    assert I.sprawdz_sumy(paczka, sumy) == []
    # SUMY_PROGRAMU.sha256: format umowy A11s (<64 hex><dwie spacje><sciezka wzgledna od katalogu programu>), kazdy plik programu
    wiersze = (paczka / "program" / "SUMY_PROGRAMU.sha256").read_text(encoding="utf-8").splitlines()
    sumy_programu = dict(reversed(w.split("  ", 1)) for w in wiersze)
    assert all(len(s) == 64 and not n.startswith(("/", "program/")) for n, s in sumy_programu.items())
    assert sorted(sumy_programu) == sorted(n[len("program/"):] for n in pliki if n.startswith("program/") and n != "program/SUMY_PROGRAMU.sha256")
    assert all(sha(paczka / "program" / n) == s for n, s in sumy_programu.items())


def test_wydanie_json_i_skrypty_crlf(tmp_path):
    zrodlo = drzewo_programu(tmp_path / "zrodlo")
    skrypt = zrodlo / "instalacja" / "wzory" / "Stanowisko.cmd"
    skrypt.write_bytes(skrypt.read_bytes().replace(b"\r\n", b"\n"))  # zrodlo z LF (np. inne ustawienia gita) - paczka i tak ma CRLF
    wynik = ZW.zbuduj(tmp_path / "wy", kola_testowe(tmp_path / "kola"), zrodlo=zrodlo, data=DATA, commit="abc123", wersja="2.5-proba")
    with zipfile.ZipFile(wynik["plik"]) as z:
        wydanie = json.loads(z.read("wydanie.json"))
        for nazwa in ("zainstaluj.cmd", "program/instalacja/wzory/Stanowisko.cmd", "program/instalacja/wzory/Wroc_do_poprzedniej.cmd"):
            tresc = z.read(nazwa)
            assert b"\r\n" in tresc and b"\n" not in tresc.replace(b"\r\n", b""), nazwa
        assert z.read("program/WERSJA") == b"2.5-proba\n"  # --wersja zastepuje plik WERSJA takze w paczce
        assert {w.date_time for w in z.infolist()} == {(2026, 11, 20, 12, 0, 0)}
        assert [w.filename for w in z.infolist()] == sorted(w.filename for w in z.infolist())
        assert {w.compress_type for w in z.infolist() if w.filename.endswith(".whl")} == {zipfile.ZIP_STORED}
    assert wynik["plik"].name == "Stanowisko_2.5-proba.zip"
    assert wydanie["wersja"] == "2.5-proba" and wydanie["commit"] == "abc123" and wydanie["data_commita"] == "2026-11-20T12:00:00Z"
    assert wydanie["python"] == "3.12" and wydanie["platforma"] == "win_amd64" and wydanie["samokontrola"] is True and wydanie["zrodlo"] == "katalog"
    assert [(k["pakiet"], k["wersja"]) for k in wydanie["kola"]] == [("pakiecik", "1.0")]
    assert [(k["pakiet"], k["wersja"]) for k in wydanie["kola_testy"]] == [("testowy", "2.0")]
    assert wydanie["kola"][0]["sha256"] == sha(tmp_path / "kola" / "pakiecik-1.0-py3-none-any.whl")


def test_rozpakowana_paczka_przechodzi_kontrole_instalatora_a_zmieniona_nie(tmp_path):
    paczka = zbuduj_paczke(tmp_path)
    wydanie, sumy = I.sprawdz_paczke(paczka)
    assert wydanie["wersja"] == "1.0" and len(sumy) == len([p for p in paczka.rglob("*") if p.is_file()]) - 1
    with open(paczka / "program" / "stanowisko" / "aplikacja.py", "ab") as f:
        f.write(b"# zmiana\n")
    with pytest.raises(I.BladInstalacji) as blad:
        I.sprawdz_paczke(paczka)
    assert blad.value.kod == I.KOD_PACZKA and "zmieniony plik program/stanowisko/aplikacja.py" in blad.value.opis


def test_brak_kola_binarnego_zatrzymuje_budowe(tmp_path):
    zrodlo, kola = drzewo_programu(tmp_path / "zrodlo"), tmp_path / "kola"
    kolo(kola, "testowy", "2.0")
    kolo(kola, "pakiecik", "1.1")                           # inna wersja
    kolo(kola, "pakiecik", "1.0", "cp311-cp311-win_amd64")  # inny Python
    kolo(kola, "pakiecik", "1.0", "cp312-cp312-manylinux_2_28_x86_64")  # inny system
    (kola / "pakiecik-1.0.tar.gz").write_bytes(b"zrodla")   # zrodla nie sa kolem - budowa ich nie kompiluje
    with pytest.raises(ZW.BladBudowy, match=r"brak kola binarnego.*1 z 1 pakietow programu.*pakiecik==1\.0"):
        ZW.zbuduj(tmp_path / "wy", kola, zrodlo=zrodlo, data=DATA)
    assert not list((tmp_path / "wy").glob("*.zip")) if (tmp_path / "wy").exists() else True
    kolo(kola, "pakiecik", "1.0", "cp312-cp312-win_amd64")
    assert ZW.zbuduj(tmp_path / "wy", kola, zrodlo=zrodlo, data=DATA)["kola"] == 1


@pytest.mark.parametrize("nazwa, wynik", [
    ("numpy-2.5.4-cp312-cp312-win_amd64.whl", ("numpy", "2.5.4")),
    ("pyside6_essentials-6.12.0-cp310-abi3-win_amd64.whl", ("pyside6-essentials", "6.12.0")),
    ("psutil-7.2.2-cp37-abi3-win_amd64.whl", ("psutil", "7.2.2")),
    ("rtree-1.4.1-py3-none-win_amd64.whl", ("rtree", "1.4.1")),
    ("jedi-0.20.1-py2.py3-none-any.whl", ("jedi", "0.20.1")),
    ("numpy-2.5.4-cp313-cp313-win_amd64.whl", None),
    ("numpy-2.5.4-cp312-cp312-win32.whl", None),
    ("numpy-2.5.4-cp312-cp312-manylinux_2_28_x86_64.whl", None),
    ("cos-1.0-cp313-abi3-win_amd64.whl", None),
    ("numpy-2.5.4.tar.gz", None),
])
def test_kolo_zgodne(nazwa, wynik):
    assert ZW.kolo_zgodne(nazwa) == wynik


def test_brak_samokontroli_to_blad_wydania(tmp_path):
    zrodlo, kola = drzewo_programu(tmp_path / "zrodlo", samokontrola=False), kola_testowe(tmp_path / "kola")
    with pytest.raises(ZW.BladBudowy, match="samokontroli"):
        ZW.zbuduj(tmp_path / "wy", kola, zrodlo=zrodlo, data=DATA)
    wynik = ZW.zbuduj(tmp_path / "wy", kola, zrodlo=zrodlo, data=DATA, bez_samokontroli=True)  # tylko do prob
    assert wynik["samokontrola"] is False and any("BEZ modulu samokontroli" in o for o in wynik["ostrzezenia"])
    with zipfile.ZipFile(wynik["plik"]) as z:
        assert json.loads(z.read("wydanie.json"))["samokontrola"] is False


def test_bledy_wejscia(tmp_path):
    zrodlo, kola = drzewo_programu(tmp_path / "zrodlo"), kola_testowe(tmp_path / "kola")
    with pytest.raises(ZW.BladBudowy, match="--data"):
        ZW.zbuduj(tmp_path / "wy", kola, zrodlo=zrodlo)
    with pytest.raises(ZW.BladBudowy, match="numer wersji"):
        ZW.zbuduj(tmp_path / "wy", kola, zrodlo=zrodlo, data=DATA, wersja="1.0/..")
    (zrodlo / "instalacja" / "zamrozone.txt").write_text("pakiecik>=1.0\n", encoding="ascii")
    with pytest.raises(ZW.BladBudowy, match="nazwa==wersja"):
        ZW.zbuduj(tmp_path / "wy", kola, zrodlo=zrodlo, data=DATA)
    (zrodlo / "instalacja" / "instalator.py").unlink()
    with pytest.raises(ZW.BladBudowy, match="instalacja/instalator.py"):
        ZW.zbuduj(tmp_path / "wy", kola, zrodlo=zrodlo, data=DATA)
    assert ZW.main(["--wyjscie", str(tmp_path / "wy"), "--kola", str(kola), "--zrodlo", str(zrodlo), "--data", "2026-11-20T12:00:00"]) == 1


def test_main_buduje_i_podaje_sume(tmp_path, capsys):
    zrodlo, kola = drzewo_programu(tmp_path / "zrodlo"), kola_testowe(tmp_path / "kola")
    kod = ZW.main(["--wyjscie", str(tmp_path / "wy"), "--kola", str(kola), "--zrodlo", str(zrodlo), "--data", "2026-11-20T12:00:00", "--wersja", "7"])
    wyjscie = capsys.readouterr().out
    assert kod == 0 and f"SHA-256 {sha(tmp_path / 'wy' / 'Stanowisko_7.zip')}" in wyjscie and "bajtow" in wyjscie
    assert ZW.sprawdz_zip(tmp_path / "wy" / "Stanowisko_7.zip") == []


def _git(repo: Path, *argumenty: str) -> str:
    srodowisko = {"GIT_AUTHOR_DATE": "2026-11-19T10:00:00+00:00", "GIT_COMMITTER_DATE": "2026-11-19T10:00:00+00:00",
                  "GIT_CONFIG_GLOBAL": str(repo / "brak_konfiguracji"), "GIT_CONFIG_NOSYSTEM": "1"}
    import os

    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "-c", "core.autocrlf=false",
                           *argumenty], check=True, capture_output=True, text=True, env={**os.environ, **srodowisko}).stdout.strip()


def test_budowa_z_commita_nie_z_katalogu_roboczego(tmp_path):
    """Tryb domyslny: tresc z commita HEAD (obiekty gita). Zmiana niezacommitowana i plik spoza gita nie wchodza do paczki."""
    repo = tmp_path / "repo"
    stanowisko = drzewo_programu(repo / "Ramki" / "stanowisko")
    shutil.rmtree(stanowisko / "dane")
    (stanowisko / "ustawienia.toml").unlink()
    _git(tmp_path, "init", "-q", str(repo))
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "proba")
    commit = _git(repo, "rev-parse", "HEAD")
    kola = kola_testowe(tmp_path / "kola")
    a = ZW.zbuduj(tmp_path / "a", kola, stanowisko=stanowisko)
    assert a["commit"] == commit and a["ostrzezenia"] == []
    aplikacja = (stanowisko / "stanowisko" / "aplikacja.py").read_bytes()
    (stanowisko / "stanowisko" / "aplikacja.py").write_bytes(aplikacja + b"# zmiana niezacommitowana\n")
    (stanowisko / "stanowisko" / "nowy_bez_gita.py").write_text("x = 1\n", encoding="ascii")
    b = ZW.zbuduj(tmp_path / "b", kola, stanowisko=stanowisko)
    assert b["sha256"] == a["sha256"]  # ten sam commit + te same kola = ten sam ZIP, mimo zmian w katalogu roboczym
    assert any("niezacommitowane" in o for o in b["ostrzezenia"])
    with zipfile.ZipFile(b["plik"]) as z:
        wydanie = json.loads(z.read("wydanie.json"))
        assert z.read("program/stanowisko/aplikacja.py") == aplikacja
        assert "program/stanowisko/nowy_bez_gita.py" not in z.namelist() and "program/testy/test_x.py" not in z.namelist()
        assert {w.date_time for w in z.infolist()} == {(2026, 11, 19, 10, 0, 0)}  # data commita (UTC)
    assert wydanie["commit"] == commit and wydanie["data_commita"] == "2026-11-19T10:00:00Z" and wydanie["zrodlo"] == "git"
    # nowy commit zmienia paczke z HEAD, ale --rewizja odtwarza wczesniejsze wydanie bajt w bajt
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "druga zmiana")
    assert ZW.zbuduj(tmp_path / "c", kola, stanowisko=stanowisko)["sha256"] != a["sha256"]
    assert ZW.zbuduj(tmp_path / "d", kola, stanowisko=stanowisko, rewizja=commit)["sha256"] == a["sha256"]


def test_listy_zamrozone_w_repo_zgodne_z_requirements():
    """Kazdy pakiet przypiety w requirements.txt jest na liscie zamrozonej w tej samej wersji (pytest: w zestawie testowym)."""
    program = ZW.wczytaj_liste((STANOWISKO / "instalacja" / "zamrozone.txt").read_bytes(), "zamrozone.txt")
    testy = ZW.wczytaj_liste((STANOWISKO / "instalacja" / "zamrozone_testy.txt").read_bytes(), "zamrozone_testy.txt")
    assert program and testy and not set(program) & set(testy)
    assert I.wczytaj_liste_zamrozona(STANOWISKO / "instalacja" / "zamrozone.txt") == program
    przypiete = {}
    for wiersz in (STANOWISKO / "requirements.txt").read_text(encoding="utf-8").splitlines():
        wiersz = wiersz.split("#", 1)[0].split(";", 1)[0].strip()
        if wiersz:
            nazwa, wersja = wiersz.split("==")
            przypiete[ZW.normalizuj_nazwe(nazwa)] = wersja.strip()
    assert przypiete.pop("pytest") == testy["pytest"]
    assert {n: program.get(n) for n in przypiete} == przypiete
    assert "pytest" not in program and "pip" not in program
    assert ZW.WZOR_WERSJI.fullmatch((STANOWISKO / "WERSJA").read_text(encoding="ascii").strip())
