"""Testy szkieletu pakietu qc: import, stos, ustawienia, pyproject, CI, .gitattributes, brak danych."""

import importlib
import os
import re
import shutil
import tomllib
from pathlib import Path

import pytest

KORZEN = Path(__file__).resolve().parent.parent
MODULY_ETAPOW = ["session", "ui", "indicate", "excel", "scanner"]
NAGLOWKI_OPISU = ["## Co robi", "## Wejscie", "## Wyjscie", '## Kryterium "dziala"']
SEKCJE = ["sciezki", "plytki", "skaner", "dopasowanie", "ubytki", "plytka", "pula"]


def _kopia_ustawien(katalog: Path) -> Path:
    cel = katalog / "ustawienia.toml"
    shutil.copyfile(KORZEN / "ustawienia.toml", cel)
    return cel


def _bez_sekcji(tekst: str, sekcja: str) -> str:
    wynik = []
    pomijaj = False
    for linia in tekst.splitlines():
        naglowek = re.match(r"^\s*\[([^\]]+)\]\s*$", linia)
        if naglowek:
            pomijaj = naglowek.group(1).strip() == sekcja
        if not pomijaj:
            wynik.append(linia)
    return "\n".join(wynik) + "\n"


@pytest.fixture
def bez_env(monkeypatch):
    monkeypatch.delenv("QC_USTAWIENIA", raising=False)
    return monkeypatch


def test_import_pakietu():
    import qc

    assert qc.__version__ == "0.1.0"
    for nazwa in MODULY_ETAPOW:
        modul = importlib.import_module(f"qc.{nazwa}")
        assert modul is not None
        opis = KORZEN / "qc" / nazwa / "OPIS.md"
        assert opis.is_file(), f"brak {opis}"
        tresc = opis.read_text(encoding="utf-8")
        for naglowek in NAGLOWKI_OPISU:
            assert naglowek in tresc, f"{opis}: brak naglowka {naglowek}"
        assert re.search(r"Nie zaimplementowano \(etap [^)]+\)", tresc), f"{opis}: brak zdania o etapie"


def test_stos_importuje_sie():
    import numpy  # noqa: F401
    import open3d
    import trimesh  # noqa: F401

    assert tomllib is not None
    import open3d.pipelines.registration  # noqa: F401

    assert hasattr(open3d.pipelines, "registration")
    assert hasattr(open3d.t.geometry, "RaycastingScene")


def test_ustawienia_domyslne(bez_env):
    from qc.ustawienia import wczytaj

    bez_env.chdir(KORZEN)
    u = wczytaj()
    for sekcja in SEKCJE:
        assert getattr(u, sekcja, None) is not None, f"brak sekcji {sekcja}"
    assert u.dopasowanie.odleglosc_mm == pytest.approx(0.05)
    assert u.dopasowanie.min_pokrycie_wieczor == pytest.approx(0.85)
    assert u.ubytki.min_glebokosc_mm == pytest.approx(0.08)
    assert u.ubytki.min_srednica_mm == pytest.approx(0.2)
    assert u.ubytki.max_srednica_mm == pytest.approx(1.5)
    assert u.ubytki.pas_brzegu_mm == pytest.approx(1.5)
    assert u.ubytki.poprawka_min_srednica_mm == pytest.approx(2.0)
    assert u.plytka.max_blad_wyrownania_mm == pytest.approx(0.1)
    assert u.pula.dni_rano == 4


def test_ustawienia_lokalne_nadpisuja(bez_env, tmp_path):
    from qc.ustawienia import wczytaj

    plik = _kopia_ustawien(tmp_path)
    (tmp_path / "ustawienia.lokalne.toml").write_text("[ubytki]\nmin_glebokosc_mm = 0.12\n", encoding="utf-8")
    u = wczytaj(plik)
    assert u.ubytki.min_glebokosc_mm == pytest.approx(0.12)
    assert u.ubytki.min_srednica_mm == pytest.approx(0.2)
    assert u.ubytki.max_srednica_mm == pytest.approx(1.5)
    assert u.dopasowanie.odleglosc_mm == pytest.approx(0.05)
    assert u.pula.dni_rano == 4


def test_ustawienia_nieznany_klucz(bez_env, tmp_path):
    from qc.ustawienia import BladUstawien, wczytaj

    assert issubclass(BladUstawien, Exception)

    katalog_a = tmp_path / "a"
    katalog_a.mkdir()
    plik_a = _kopia_ustawien(katalog_a)
    (katalog_a / "ustawienia.lokalne.toml").write_text("[ubytki]\nliterowka = 1\n", encoding="utf-8")
    with pytest.raises(BladUstawien) as blad:
        wczytaj(plik_a)
    assert "literowka" in str(blad.value)

    katalog_b = tmp_path / "b"
    katalog_b.mkdir()
    plik_b = katalog_b / "ustawienia.toml"
    tekst = (KORZEN / "ustawienia.toml").read_text(encoding="utf-8")
    plik_b.write_text(_bez_sekcji(tekst, "ubytki"), encoding="utf-8")
    assert "ubytki" not in tomllib.loads(plik_b.read_text(encoding="utf-8"))
    with pytest.raises(BladUstawien) as blad:
        wczytaj(plik_b)
    assert "ubytki" in str(blad.value)


def test_ustawienia_sciezki(bez_env, tmp_path):
    from qc.ustawienia import wczytaj

    plik = _kopia_ustawien(tmp_path)
    u = wczytaj(plik)
    baza = u.sciezki.baza
    assert isinstance(baza, Path)
    assert baza.is_absolute()
    assert baza.resolve() == (tmp_path / "dane" / "qc.sqlite").resolve()
    wieczorna = u.plytki.wieczorna
    assert isinstance(wieczorna, Path)
    assert wieczorna.is_absolute()
    assert wieczorna.as_posix().endswith("modele/plytka-wieczorna.json")


def test_ustawienia_env(bez_env, tmp_path):
    from qc.ustawienia import wczytaj

    katalog = tmp_path / "env"
    katalog.mkdir()
    plik = katalog / "ustawienia.toml"
    tekst = (KORZEN / "ustawienia.toml").read_text(encoding="utf-8")
    nowy, ile = re.subn(r"(?m)^(\s*min_glebokosc_mm\s*=\s*)[0-9.]+", r"\g<1>0.33", tekst)
    assert ile == 1
    plik.write_text(nowy, encoding="utf-8")
    bez_env.setenv("QC_USTAWIENIA", str(plik))
    bez_env.chdir(KORZEN)
    u = wczytaj(KORZEN / "ustawienia.toml")
    assert u.ubytki.min_glebokosc_mm == pytest.approx(0.33)
    assert u.sciezki.baza.resolve() == (katalog / "dane" / "qc.sqlite").resolve()


def test_pyproject():
    dane = tomllib.loads((KORZEN / "pyproject.toml").read_text(encoding="utf-8"))
    projekt = dane["project"]
    assert projekt["requires-python"] == ">=3.12"
    nazwy = {re.split(r"[<>=!~\[; ]", z, maxsplit=1)[0].strip().lower() for z in projekt["dependencies"]}
    for wymagana in ("numpy", "trimesh", "open3d"):
        assert wymagana in nazwy, f"brak zaleznosci {wymagana}"
    opcje = dane["tool"]["pytest"]["ini_options"]
    assert any(m.startswith("wolne") for m in opcje["markers"])
    assert "." in opcje["pythonpath"]


def test_ci_workflow():
    plik = KORZEN / ".github" / "workflows" / "testy.yml"
    assert plik.is_file()
    tekst = plik.read_text(encoding="utf-8")
    for fraza in ("ubuntu-latest", "python -m pytest", "concurrency", '-m "not wolne"', "timeout-minutes"):
        assert fraza in tekst, f"brak {fraza} w testy.yml"
    linie = tekst.splitlines()
    indeksy = [i for i, linia in enumerate(linie) if "windows-latest" in linia]
    assert len(indeksy) <= 1
    for i in indeksy:
        okno = linie[max(0, i - 5) : i + 6]
        assert any("inputs" in linia or "if:" in linia for linia in okno), "windows-latest bez warunku"


def test_gitattributes():
    tekst = (KORZEN / ".gitattributes").read_text(encoding="utf-8")
    linie = [" ".join(linia.split()) for linia in tekst.splitlines()]
    for wpis in ("*.stl binary", "*.ps1 text eol=crlf", "* text=auto eol=lf"):
        assert wpis in linie, f"brak {wpis} w .gitattributes"


def test_brak_danych_produkcyjnych():
    zakazane = {".stl", ".ply", ".obj", ".pdf", ".sqlite", ".db"}
    dozwolone = [KORZEN / "tests" / "dane", KORZEN / "modele"]
    znalezione = []
    for katalog, podkatalogi, pliki in os.walk(KORZEN):
        podkatalogi[:] = [d for d in podkatalogi if d != ".git"]
        sciezka_katalogu = Path(katalog)
        if any(sciezka_katalogu == d or d in sciezka_katalogu.parents for d in dozwolone):
            continue
        for nazwa in pliki:
            if Path(nazwa).suffix.lower() in zakazane:
                znalezione.append(str((sciezka_katalogu / nazwa).relative_to(KORZEN)))
    assert znalezione == [], f"pliki danych poza tests/dane i modele: {znalezione}"
