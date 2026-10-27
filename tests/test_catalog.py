"""Testy katalogu projektow STL (qc.catalog) na danych syntetycznych.

Drzewo w tmp_path: Cyrkon/<folder zlecenia>/<plik>.stl i Prywatne/#1234/11.stl; STL = projekty z puli 30
eksportowane do pliku. Nazwy folderow FIKCYJNE (RODO). Ustawienia = kopia ustawienia.toml w tmp_path
z sciezki.cyrkon, sciezki.prywatne i sciezki.baza wskazujacymi na drzewo.

Kontrakt pomocniczy (ustalany tymi testami):
- Cechy jest dataclass (dataclasses.replace dziala), wymiary_mm i d2 to np.ndarray.
- Baza.dodaj_projekt(rekord: dict kolumn bez id) -> id; projekt(id) -> dict kolumn albo None;
  projekty(...) -> list[dict]; d2 w rekordzie = bytes (BLOB); projekty(usuniete=False) pomija rekordy usuniety=1, usuniete=True je zawiera.
- RaportIndeksu.nowe/zmienione/usuniete to liczby (int).
- sciezka w bazie: wzgledna wobec katalogu zrodla, separator "/", np. "Kowalski 3263 zs/36.stl".
- Daty w pulach: lokalna data z mtime_ns pliku; teraz = naiwny datetime lokalny.
- CSV wspolczynnikow ma wiersz naglowka; numer linii w bledzie liczony od 1 (naglowek = linia 1);
  plik_stl w CSV = nazwa pliku STL (bez folderu), porownanie bez wielkosci liter; data = datetime.date.
"""

import dataclasses
import os
import re
import shutil
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pytest
import trimesh

from qc.ustawienia import katalog_repo, wczytaj

K = 1.22

DRZEWO = {
    ("Cyrkon", "Kowalski 3263 zs", "36.stl"): 0,
    ("Cyrkon", "Nowak 0041", "zab 46.stl"): 1,
    ("Cyrkon", "Nowak 0041", "zab 47.stl"): 2,
    ("Cyrkon", "Wisniewska 3 korona", "x.stl"): 3,
    ("Prywatne", "#1234", "11.stl"): 4,
}

KOLUMNY_PROJEKTY = [
    # nazwa, typ, notnull, pk
    ("id", "INTEGER", 0, 1),
    ("zrodlo", "TEXT", 1, 0),
    ("sciezka", "TEXT", 1, 0),
    ("folder", "TEXT", 1, 0),
    ("kuweta", "TEXT", 0, 0),
    ("nazwisko", "TEXT", 0, 0),
    ("numer_zeba", "INTEGER", 0, 0),
    ("mtime_ns", "INTEGER", 1, 0),
    ("rozmiar", "INTEGER", 1, 0),
    ("objetosc_mm3", "REAL", 0, 0),
    ("pole_mm2", "REAL", 0, 0),
    ("wym1_mm", "REAL", 0, 0),
    ("wym2_mm", "REAL", 0, 0),
    ("wym3_mm", "REAL", 0, 0),
    ("d2", "BLOB", 0, 0),
    ("zaindeksowano", "TEXT", 1, 0),
    ("usuniety", "INTEGER", 1, 0),
]

KOLUMNY_WSPOLCZYNNIKI = [
    ("id", "INTEGER", 0, 1),
    ("plik_stl", "TEXT", 1, 0),
    ("krazek", "TEXT", 0, 0),
    ("wspolczynnik", "REAL", 1, 0),
    ("data", "TEXT", 1, 0),
    ("zrodlo", "TEXT", 1, 0),
]


# --- pomocnicze ---------------------------------------------------------------


def _nazwy():
    from qc.catalog import nazwy

    return nazwy


def _cechy():
    from qc.catalog import cechy

    return cechy


def _baza():
    from qc.catalog import baza

    return baza


def _indeks():
    from qc.catalog import indeks

    return indeks


def _wspolczynniki():
    from qc.catalog import wspolczynniki

    return wspolczynniki


def _ustawienia(katalog: Path, monkeypatch):
    """Kopia ustawienia.toml w katalogu z sciezkami cyrkon/prywatne/baza na drzewo testowe."""
    monkeypatch.delenv("QC_USTAWIENIA", raising=False)
    tekst = (katalog_repo() / "ustawienia.toml").read_text(encoding="utf-8")
    zamiany = {"cyrkon": "Cyrkon", "prywatne": "Prywatne", "baza": "dane/qc.sqlite"}
    for klucz, wartosc in zamiany.items():
        tekst, n = re.subn(rf'(?m)^{klucz}\s*=.*$', f'{klucz} = "{wartosc}"', tekst, count=1)
        assert n == 1, klucz
    katalog.mkdir(parents=True, exist_ok=True)
    (katalog / "ustawienia.toml").write_text(tekst, encoding="utf-8")
    (katalog / "Cyrkon").mkdir(exist_ok=True)
    (katalog / "Prywatne").mkdir(exist_ok=True)
    (katalog / "dane").mkdir(exist_ok=True)
    return wczytaj(katalog / "ustawienia.toml")


def _ustawienia_repo(monkeypatch):
    monkeypatch.delenv("QC_USTAWIENIA", raising=False)
    return wczytaj(katalog_repo() / "ustawienia.toml")


def _nowa_baza(ust):
    b = _baza().Baza(ust.sciezki.baza)
    b.utworz()
    return b


def _ustaw_czas(sciezka: Path, kiedy: datetime) -> None:
    ns = int(kiedy.timestamp() * 1e9)
    os.utime(sciezka, ns=(ns, ns))


def _zapisz_stl(siatka, sciezka: Path, kiedy: datetime | None = None) -> None:
    sciezka.parent.mkdir(parents=True, exist_ok=True)
    siatka.export(sciezka)
    if kiedy is not None:
        _ustaw_czas(sciezka, kiedy)
        _ustaw_czas(sciezka.parent, kiedy)


def _zbuduj_drzewo(katalog: Path, pula30, kiedy: datetime) -> None:
    for (zrodlo, folder, plik), i in DRZEWO.items():
        _zapisz_stl(pula30[i].siatka, katalog / zrodlo / folder / plik, kiedy)


def _wedlug_sciezki(rekordy) -> dict:
    return {(r["zrodlo"], r["sciezka"]): r for r in rekordy}


def _obrot(ziarno: int) -> np.ndarray:
    rng = np.random.default_rng(ziarno)
    T = trimesh.transformations.random_rotation_matrix(rng.random(3))
    T[:3, 3] = rng.uniform(-20, 20, 3)
    return T


def _obrocona(siatka, ziarno: int):
    m = siatka.copy()
    m.apply_transform(_obrot(ziarno))
    return m


def _przeskalowana(siatka, k: float):
    m = siatka.copy()
    m.apply_scale(k)
    return m


@pytest.fixture(scope="module")
def cechy_puli(pula30):
    c = _cechy()
    return [c.policz(p.siatka) for p in pula30]


@pytest.fixture
def drzewo(tmp_path, pula30, monkeypatch):
    """(ustawienia, baza, teraz) z drzewem DRZEWO zapisanym wczoraj."""
    teraz = datetime(2026, 10, 27, 10, 0)  # wtorek
    ust = _ustawienia(tmp_path / "stanowisko", monkeypatch)
    _zbuduj_drzewo(tmp_path / "stanowisko", pula30, teraz - timedelta(days=1))
    return ust, _nowa_baza(ust), teraz


# --- nazwy --------------------------------------------------------------------


@pytest.mark.parametrize("folder, kuweta, nazwisko, prywatne", [
    ("Kowalski 3263 zs", "3263", "Kowalski", False),
    ("Nowak 0041", "41", "Nowak", False),
    ("03 Wisniewska", "3", "Wisniewska", False),
    ("#1234", "#1234", None, True),
    ("Kowalski", None, "Kowalski", False),
    ("Kowalski 12345", None, "Kowalski", False),
    ("Nowak-Kowalska 7", "7", "Nowak-Kowalska", False),
    ("Wisniewska 3 korona", "3", "Wisniewska", False),
    ("Zielinski 0 most", "0", "Zielinski", False),
    ("Lewandowski 12 zs 4567", "12", "Lewandowski", False),
    ("Kaminska_88_zs", "88", "Kaminska", False),
    ("  Dabrowski   0912  ", "912", "Dabrowski", False),
])
def test_rozbierz(folder, kuweta, nazwisko, prywatne):
    z = _nazwy().rozbierz(folder)
    assert z.kuweta == kuweta
    assert z.nazwisko == nazwisko
    assert z.prywatne is prywatne
    assert z.nazwa == folder


def test_znormalizuj():
    zn = _nazwy().znormalizuj
    assert zn("  Kowalski   0041 ZS ") == "kowalski 41 zs"
    assert zn("Nowak 3263") == "nowak 3263"
    assert zn("0") == "0"
    assert zn("007 Bond") == "7 bond"


@pytest.mark.parametrize("plik, numer", [
    ("36.stl", 36),
    ("zab 46.stl", 46),
    ("Kowalski_3263_47.stl", 47),
    ("3263.stl", None),
    ("korona.stl", None),
    ("19.stl", None),
    ("11.STL", 11),
    ("28.stl", 28),
    ("30.stl", None),
    ("49.stl", None),
    ("136.stl", None),
])
def test_numer_zeba(plik, numer):
    assert _nazwy().numer_zeba(plik) == numer


# --- cechy --------------------------------------------------------------------


def test_cechy_skala_i_obrot(pula30, cechy_puli):
    c = _cechy()
    for i in (0, 1, 2, 7):
        siatka = pula30[i].siatka
        baza = cechy_puli[i]
        assert baza.objetosc_mm3 is not None and baza.objetosc_mm3 > 0
        assert baza.pole_mm2 > 0
        assert baza.wymiary_mm.shape == (3,)
        assert np.all(np.diff(baza.wymiary_mm) <= 0), "wymiary malejaco"
        assert baza.d2.shape == (64,)
        assert baza.d2.sum() == pytest.approx(1.0, abs=1e-6)
        assert c.odleglosc(baza, baza) == pytest.approx(0.0, abs=1e-9)

        skalowana = c.policz(_przeskalowana(siatka, K))
        oczekiwana = baza.przeskaluj(K)
        assert skalowana.objetosc_mm3 == pytest.approx(oczekiwana.objetosc_mm3, rel=0.01)
        assert skalowana.pole_mm2 == pytest.approx(oczekiwana.pole_mm2, rel=0.01)
        np.testing.assert_allclose(skalowana.wymiary_mm, oczekiwana.wymiary_mm, rtol=0.01)
        assert c.odleglosc(skalowana, oczekiwana) < 0.05

        obrocona = c.policz(_obrocona(siatka, 100 + i), ziarno=1)
        assert obrocona.objetosc_mm3 == pytest.approx(baza.objetosc_mm3, rel=0.01)
        np.testing.assert_allclose(obrocona.wymiary_mm, baza.wymiary_mm, rtol=0.01)
        assert c.odleglosc(obrocona, baza) < 0.05

    odl = [c.odleglosc(cechy_puli[i], cechy_puli[j])
           for i in range(len(cechy_puli)) for j in range(i + 1, len(cechy_puli))]
    # prog 0,08: szum tego samego projektu przy 20 000 par daje odleglosc 0,017-0,033,
    # a 10. percentyl par roznych projektow (korony tego samego rodzaju sa podobne) to 0,087
    udzial = float(np.mean(np.array(odl) > 0.08))
    assert udzial >= 0.9, f"tylko {udzial:.0%} par roznych projektow ma odleglosc > 0,08"


def test_cechy_filtr(pula30, cechy_puli, skan, monkeypatch):
    c = _cechy()
    ust = _ustawienia_repo(monkeypatch)
    trafione = 0
    przepuszczone = []
    for i, projekt in enumerate(pula30):
        siatka, _ = skan(projekt, ziarno=200 + i, wspolczynnik=K, szum_mm=0.03)
        cs = c.policz(_obrocona(siatka, 300 + i), ziarno=i)
        wyniki = [c.pasuje(cs, cp, K, ust) for cp in cechy_puli]
        trafione += bool(wyniki[i])
        przepuszczone.append(sum(wyniki))
    assert trafione == 30
    srednio = float(np.mean(przepuszczone))
    assert srednio <= 9, f"srednio {srednio:.1f} projektow przepuszczonych na skan"


def test_cechy_skan_otwarty(pula30, cechy_puli, skan, monkeypatch):
    c = _cechy()
    ust = _ustawienia_repo(monkeypatch)
    siatka, _ = skan(pula30[0], wspolczynnik=K, widocznosc="z_gory")
    cs = c.policz(_obrocona(siatka, 5))
    assert cs.objetosc_mm3 is None
    assert cs.pole_mm2 > 0
    assert cs.wymiary_mm.shape == (3,)
    assert cs.d2.shape == (64,)

    projekt = cechy_puli[0]
    assert c.pasuje(cs, projekt, K, ust)
    # objetosc projektu nie gra roli, gdy skan jej nie ma
    inna_objetosc = dataclasses.replace(projekt, objetosc_mm3=projekt.objetosc_mm3 * 3)
    assert c.pasuje(cs, inna_objetosc, K, ust)
    # wymiary nadal sprawdzane
    inne_wymiary = dataclasses.replace(projekt, wymiary_mm=projekt.wymiary_mm + 3.0)
    assert not c.pasuje(cs, inne_wymiary, K, ust)


# --- baza ---------------------------------------------------------------------


def _opis_tabel(sciezka) -> tuple:
    with sqlite3.connect(sciezka) as pol:
        sql = sorted(pol.execute("SELECT type, name, sql FROM sqlite_master").fetchall(),
                     key=lambda w: (w[0], w[1]))
        wersja = pol.execute("PRAGMA user_version").fetchone()[0]
    return sql, wersja


def test_baza_schemat(tmp_path):
    sciezka = tmp_path / "qc.sqlite"
    b = _baza().Baza(sciezka)
    b.utworz()
    assert b.wersja() == 1
    with sqlite3.connect(sciezka) as pol:
        assert pol.execute("PRAGMA user_version").fetchone()[0] == 1
        tabele = {w[0] for w in pol.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
        assert tabele == {"projekty", "wspolczynniki"}
        for tabela, oczekiwane in (("projekty", KOLUMNY_PROJEKTY),
                                   ("wspolczynniki", KOLUMNY_WSPOLCZYNNIKI)):
            info = pol.execute(f"PRAGMA table_info({tabela})").fetchall()
            assert [(w[1], w[2].upper(), w[3], w[5]) for w in info] == oczekiwane, tabela
        dflt = {w[1]: w[4] for w in pol.execute("PRAGMA table_info(projekty)")}
        assert dflt["usuniety"] == "0"
        # sciezka unikalna w obrebie zrodla (decyzja wlasciciela): UNIQUE(zrodlo, sciezka)
        unikalne = set()
        for w in pol.execute("PRAGMA index_list(projekty)"):
            if w[2]:
                unikalne.add(tuple(k[2] for k in pol.execute(f"PRAGMA index_info('{w[1]}')")))
        assert ("zrodlo", "sciezka") in unikalne
        assert ("sciezka",) not in unikalne

    przed = _opis_tabel(sciezka)
    _baza().Baza(sciezka).utworz()
    assert _opis_tabel(sciezka) == przed


def _rekord(sciezka: str, mtime: datetime, usuniety: int = 0) -> dict:
    return dict(
        zrodlo="cyrkon", sciezka=sciezka, folder=sciezka.split("/")[0], kuweta="1",
        nazwisko="Testowy", numer_zeba=None, mtime_ns=int(mtime.timestamp() * 1e9), rozmiar=100,
        objetosc_mm3=None, pole_mm2=None, wym1_mm=None, wym2_mm=None, wym3_mm=None, d2=None,
        zaindeksowano=mtime.isoformat(), usuniety=usuniety,
    )


def test_usun_starsze(tmp_path):
    teraz = datetime(2026, 10, 27, 10, 0)
    b = _baza().Baza(tmp_path / "qc.sqlite")
    b.utworz()
    ids = {
        "swiezy": b.dodaj_projekt(_rekord("Testowy 1/a.stl", teraz - timedelta(days=2))),
        "prog": b.dodaj_projekt(_rekord("Testowy 2/a.stl", teraz - timedelta(days=9, hours=23))),
        "stary": b.dodaj_projekt(_rekord("Testowy 3/a.stl", teraz - timedelta(days=11))),
        "usuniety": b.dodaj_projekt(_rekord("Testowy 4/a.stl", teraz - timedelta(days=1), 1)),
        "oznaczony": b.dodaj_projekt(_rekord("Testowy 5/a.stl", teraz - timedelta(days=1))),
    }
    b.oznacz_usuniete([ids["oznaczony"]])
    assert b.projekt(ids["oznaczony"])["usuniety"] == 1
    assert {r["id"] for r in b.projekty()} == {ids["swiezy"], ids["prog"], ids["stary"]}

    assert b.usun_starsze_niz(10, teraz) == 3
    for klucz in ("stary", "usuniety", "oznaczony"):
        assert b.projekt(ids[klucz]) is None, klucz
    assert b.projekt(ids["swiezy"]) is not None
    assert b.projekt(ids["prog"]) is not None
    assert b.usun_starsze_niz(10, teraz) == 0


# --- indeks -------------------------------------------------------------------


def test_indeks_idempotentny(drzewo, pula30):
    ust, b, teraz = drzewo
    ix = _indeks()
    r = ix.skanuj(ust, b, teraz)
    assert (r.nowe, r.zmienione, r.usuniete) == (5, 0, 0)
    r = ix.skanuj(ust, b, teraz)
    assert (r.nowe, r.zmienione, r.usuniete) == (0, 0, 0)

    przed = _wedlug_sciezki(b.projekty())[("cyrkon", "Kowalski 3263 zs/36.stl")]
    plik = ust.sciezki.cyrkon / "Kowalski 3263 zs" / "36.stl"
    _zapisz_stl(pula30[10].siatka, plik, teraz - timedelta(hours=1))
    r = ix.skanuj(ust, b, teraz)
    assert (r.nowe, r.zmienione, r.usuniete) == (0, 1, 0)
    po = _wedlug_sciezki(b.projekty())[("cyrkon", "Kowalski 3263 zs/36.stl")]
    assert po["id"] == przed["id"]
    assert po["mtime_ns"] != przed["mtime_ns"]
    assert po["rozmiar"] == plik.stat().st_size
    assert po["objetosc_mm3"] == pytest.approx(pula30[10].siatka.volume, rel=0.01)
    assert po["objetosc_mm3"] != pytest.approx(przed["objetosc_mm3"], rel=0.001)
    assert po["d2"] != przed["d2"]

    usuwany = _wedlug_sciezki(b.projekty())[("cyrkon", "Nowak 0041/zab 47.stl")]
    (ust.sciezki.cyrkon / "Nowak 0041" / "zab 47.stl").unlink()
    r = ix.skanuj(ust, b, teraz)
    assert (r.nowe, r.zmienione, r.usuniete) == (0, 0, 1)
    assert b.projekt(usuwany["id"])["usuniety"] == 1
    assert len(b.projekty()) == 4
    assert len(b.projekty(usuniete=True)) == 5
    r = ix.skanuj(ust, b, teraz)
    assert (r.nowe, r.zmienione, r.usuniete) == (0, 0, 0)


def test_rekord_projektu(drzewo, pula30):
    ust, b, teraz = drzewo
    _indeks().skanuj(ust, b, teraz)
    rekordy = _wedlug_sciezki(b.projekty())
    assert set(rekordy) == {
        ("cyrkon", "Kowalski 3263 zs/36.stl"),
        ("cyrkon", "Nowak 0041/zab 46.stl"),
        ("cyrkon", "Nowak 0041/zab 47.stl"),
        ("cyrkon", "Wisniewska 3 korona/x.stl"),
        ("prywatne", "#1234/11.stl"),
    }

    r = rekordy[("cyrkon", "Kowalski 3263 zs/36.stl")]
    plik = ust.sciezki.cyrkon / "Kowalski 3263 zs" / "36.stl"
    assert r["folder"] == "Kowalski 3263 zs"
    assert r["kuweta"] == "3263"
    assert r["nazwisko"] == "Kowalski"
    assert r["numer_zeba"] == 36
    assert r["mtime_ns"] == plik.stat().st_mtime_ns
    assert r["rozmiar"] == plik.stat().st_size
    assert r["usuniety"] == 0
    assert datetime.fromisoformat(r["zaindeksowano"]) == teraz
    assert r["objetosc_mm3"] == pytest.approx(pula30[0].siatka.volume, rel=0.01)
    assert r["pole_mm2"] == pytest.approx(pula30[0].siatka.area, rel=0.01)
    assert r["wym1_mm"] >= r["wym2_mm"] >= r["wym3_mm"] > 0
    assert r["d2"] is not None and len(r["d2"]) > 0

    assert rekordy[("cyrkon", "Nowak 0041/zab 46.stl")]["kuweta"] == "41"
    assert rekordy[("cyrkon", "Wisniewska 3 korona/x.stl")]["numer_zeba"] is None

    p = rekordy[("prywatne", "#1234/11.stl")]
    assert p["kuweta"] == "#1234"
    assert p["folder"] == "#1234"
    assert p["nazwisko"] is None
    assert p["numer_zeba"] == 11
    assert [w["sciezka"] for w in b.projekty(zrodlo="prywatne")] == ["#1234/11.stl"]
    assert len(b.projekty(zrodlo="cyrkon")) == 4


def test_indeks_wielkosc_liter(tmp_path, pula30, monkeypatch):
    teraz = datetime(2026, 10, 27, 10, 0)
    ust = _ustawienia(tmp_path / "stanowisko", monkeypatch)
    _zapisz_stl(pula30[0].siatka, ust.sciezki.cyrkon / "Testowy 101" / "21.STL", teraz)
    _zapisz_stl(pula30[1].siatka, ust.sciezki.cyrkon / "Testowy 102" / "22.Stl", teraz)
    (ust.sciezki.cyrkon / "Testowy 102" / "opis.txt").write_text("nie stl", encoding="utf-8")
    b = _nowa_baza(ust)
    r = _indeks().skanuj(ust, b, teraz)
    assert r.nowe == 2
    assert {w["numer_zeba"] for w in b.projekty()} == {21, 22}


def _drzewo_dat(katalog: Path, pula30, daty: dict[str, datetime]) -> None:
    for i, (folder, kiedy) in enumerate(daty.items()):
        _zapisz_stl(pula30[i].siatka, katalog / "Cyrkon" / folder / "11.stl", kiedy)


def _foldery_puli_rano(b, teraz, dni) -> set[str]:
    wpisy = _indeks().pula_rano(b, teraz, dni)
    assert all(w.wspolczynnik == 1.0 for w in wpisy)
    return {b.projekt(w.projekt_id)["folder"] for w in wpisy}


def test_pula_rano_dni_robocze(tmp_path, pula30, monkeypatch):
    ix = _indeks()

    # poniedzialek 10:00
    teraz = datetime(2026, 10, 26, 10, 0)
    assert teraz.weekday() == 0
    ust = _ustawienia(tmp_path / "pn", monkeypatch)
    daty = {
        "Czwartek 101": datetime(2026, 10, 22, 15, 0),
        "Piatek 102": datetime(2026, 10, 23, 15, 0),
        "Sobota 103": datetime(2026, 10, 24, 11, 0),
        "Niedziela 104": datetime(2026, 10, 25, 20, 0),
        "Stary 105": teraz - timedelta(days=10),
        "Dzis 106": datetime(2026, 10, 26, 8, 0),
    }
    _drzewo_dat(tmp_path / "pn", pula30, daty)
    b = _nowa_baza(ust)
    ix.skanuj(ust, b, teraz)
    foldery = _foldery_puli_rano(b, teraz, 4)
    assert foldery == {"Czwartek 101", "Piatek 102", "Sobota 103", "Niedziela 104", "Dzis 106"}
    # domyslnie dni = pula.dni_rano (4)
    assert {b.projekt(w.projekt_id)["folder"] for w in ix.pula_rano(b, teraz)} == foldery

    # sroda 10:00: 4 dni robocze wstecz = wt, pn, pt, czw
    teraz = datetime(2026, 10, 28, 10, 0)
    assert teraz.weekday() == 2
    ust = _ustawienia(tmp_path / "sr", monkeypatch)
    daty = {
        "Sroda 201": datetime(2026, 10, 21, 18, 0),
        "Czwartek 202": datetime(2026, 10, 22, 0, 30),
        "Piatek 203": datetime(2026, 10, 23, 15, 0),
        "Sobota 204": datetime(2026, 10, 24, 11, 0),
        "Niedziela 205": datetime(2026, 10, 25, 20, 0),
        "Poniedzialek 206": datetime(2026, 10, 26, 9, 0),
        "Wtorek 207": datetime(2026, 10, 27, 23, 30),
        "Dzis 208": datetime(2026, 10, 28, 7, 0),
    }
    _drzewo_dat(tmp_path / "sr", pula30, daty)
    b = _nowa_baza(ust)
    ix.skanuj(ust, b, teraz)
    foldery = _foldery_puli_rano(b, teraz, 4)
    assert foldery == set(daty) - {"Sroda 201"}
    assert _foldery_puli_rano(b, teraz, 1) == {"Wtorek 207", "Dzis 208"}


# --- wspolczynniki ------------------------------------------------------------


def _zapisz_csv(sciezka: Path, wiersze: list[str]) -> Path:
    sciezka.write_text("plik;krazek;wspolczynnik;data\n" + "\n".join(wiersze) + "\n", encoding="utf-8")
    return sciezka


def test_wspolczynniki_csv(tmp_path):
    w = _wspolczynniki()
    poprawne = [
        "36.stl;K-01;1,2345;2026-10-27",
        "zab 46.stl;K-01;1.2210;2026-10-26",
        "x.stl;;1,22;2026-10-24",
    ]
    bledny = _zapisz_csv(tmp_path / "bledny.csv", poprawne + ["zab 47.stl;K-02;1,2x;2026-10-27"])
    with pytest.raises(ValueError, match=r"\b5\b"):
        w.wczytaj(bledny)

    wpisy = w.wczytaj(_zapisz_csv(tmp_path / "dobry.csv", poprawne))
    assert len(wpisy) == 3
    assert all(isinstance(x.wspolczynnik, float) for x in wpisy)
    assert wpisy[0].plik_stl == "36.stl"
    assert wpisy[0].krazek == "K-01"
    assert wpisy[0].wspolczynnik == pytest.approx(1.2345)
    assert wpisy[0].data == date(2026, 10, 27)
    assert wpisy[1].wspolczynnik == pytest.approx(1.221)
    assert wpisy[2].krazek in (None, "")

    zla_data = _zapisz_csv(tmp_path / "zla_data.csv", poprawne[:1] + ["x.stl;K-01;1,22;27 pazdziernika"])
    with pytest.raises(ValueError, match=r"\b3\b"):
        w.wczytaj(zla_data)


def test_pula_wieczor(drzewo, tmp_path):
    ust, b, teraz = drzewo  # wtorek 27.10.2026
    ix = _indeks()
    ix.skanuj(ust, b, teraz)
    csv = _zapisz_csv(tmp_path / "wspolczynniki.csv", [
        "36.stl;K-01;1,2345;2026-10-27",
        "zab 46.stl;K-01;1,2290;2026-10-26",
        "11.stl;K-02;1,2410;2026-10-26",
        "zab 47.stl;K-02;1,2500;2026-10-24",
        "brak.stl;K-03;1,2200;2026-10-27",
    ])
    wpisy, brakujace = ix.pula_wieczor(b, _wspolczynniki().wczytaj(csv), teraz)
    assert brakujace == 1
    wynik = {b.projekt(x.projekt_id)["sciezka"]: x.wspolczynnik for x in wpisy}
    assert wynik == pytest.approx({
        "Kowalski 3263 zs/36.stl": 1.2345,
        "Nowak 0041/zab 46.stl": 1.229,
        "#1234/11.stl": 1.241,
    })

    wpisy, brakujace = ix.pula_wieczor(b, _wspolczynniki().wczytaj(csv), teraz, dni=1)
    assert brakujace == 1
    assert [b.projekt(x.projekt_id)["sciezka"] for x in wpisy] == ["Kowalski 3263 zs/36.stl"]


def test_baza_sciezki_wzgledne(tmp_path, pula30, monkeypatch):
    teraz = datetime(2026, 10, 27, 10, 0)
    stare = tmp_path / "stary" / "stanowisko"
    ust = _ustawienia(stare, monkeypatch)
    _zbuduj_drzewo(stare, pula30, teraz - timedelta(days=1))
    b = _nowa_baza(ust)
    _indeks().skanuj(ust, b, teraz)
    przed = _wedlug_sciezki(b.projekty())
    del b

    nowe = tmp_path / "nowy" / "gdzie indziej"
    shutil.copytree(stare, nowe)
    ust2 = wczytaj(nowe / "ustawienia.toml")
    assert ust2.sciezki.baza != ust.sciezki.baza
    b2 = _baza().Baza(ust2.sciezki.baza)
    po = _wedlug_sciezki(b2.projekty())
    assert po == przed
    assert all(not os.path.isabs(k[1]) and "\\" not in k[1] for k in po)

    shutil.rmtree(stare / "Cyrkon")
    shutil.rmtree(stare / "Prywatne")
    r = _indeks().skanuj(ust2, b2, teraz)
    assert (r.nowe, r.zmienione, r.usuniete) == (0, 0, 0)


# --- poprawki po recenzji -----------------------------------------------------
#
# Kontrakt dopisany po recenzji PR #4:
# - RaportIndeksu.bledy: int i RaportIndeksu.bledne: list[str] (sciezki wzgledne z "/"); plik, ktorego nie
#   da sie wczytac, dostaje rekord z cechami None, skan idzie dalej; ponowna proba po zmianie mtime/rozmiaru.
# - skanuj pomija pliki z mtime starszym niz pula.usuwaj_po_dniach (bez rekordu i bez cech), a istniejacego
#   rekordu takiego pliku nie oznacza jako usuniety.
# - pula_wieczor zwraca krotke (wpisy, brakujace) z dodatkowym atrybutem `niejednoznaczne: int`.
# - pula_rano(..., ustawienia=None), pula_wieczor(..., ustawienia=None): dni domyslnie z ustawien.


def _ustawienia_z(katalog: Path, monkeypatch, **pula):
    """Jak _ustawienia, z nadpisanymi kluczami sekcji [pula]."""
    _ustawienia(katalog, monkeypatch)
    plik = katalog / "ustawienia.toml"
    tekst = plik.read_text(encoding="utf-8")
    for klucz, wartosc in pula.items():
        tekst, n = re.subn(rf'(?m)^{klucz}\s*=.*$', f'{klucz} = {wartosc}', tekst, count=1)
        assert n == 1, klucz
    plik.write_text(tekst, encoding="utf-8")
    return wczytaj(plik)


def test_ta_sama_sciezka_w_dwoch_zrodlach(tmp_path, pula30, monkeypatch):
    teraz = datetime(2026, 10, 27, 10, 0)
    katalog = tmp_path / "stanowisko"
    ust = _ustawienia(katalog, monkeypatch)
    _zapisz_stl(pula30[0].siatka, katalog / "Cyrkon" / "Testowy 101" / "11.stl", teraz - timedelta(hours=2))
    _zapisz_stl(pula30[1].siatka, katalog / "Prywatne" / "Testowy 101" / "11.stl", teraz - timedelta(hours=2))
    b = _nowa_baza(ust)
    r = _indeks().skanuj(ust, b, teraz)
    assert r.nowe == 2
    rekordy = _wedlug_sciezki(b.projekty())
    assert set(rekordy) == {("cyrkon", "Testowy 101/11.stl"), ("prywatne", "Testowy 101/11.stl")}
    assert rekordy[("cyrkon", "Testowy 101/11.stl")]["objetosc_mm3"] == pytest.approx(
        pula30[0].siatka.volume, rel=0.01)
    assert rekordy[("prywatne", "Testowy 101/11.stl")]["objetosc_mm3"] == pytest.approx(
        pula30[1].siatka.volume, rel=0.01)
    r = _indeks().skanuj(ust, b, teraz)
    assert (r.nowe, r.zmienione, r.usuniete) == (0, 0, 0)


def test_indeks_bledne_pliki(tmp_path, pula30, monkeypatch):
    teraz = datetime(2026, 10, 27, 10, 0)
    kiedy = teraz - timedelta(hours=2)
    katalog = tmp_path / "stanowisko"
    ust = _ustawienia(katalog, monkeypatch)
    for i in range(4):
        _zapisz_stl(pula30[i].siatka, katalog / "Cyrkon" / f"Testowy {101 + i}" / "11.stl", kiedy)
    uszkodzony = katalog / "Cyrkon" / "Testowy 105" / "11.stl"
    uszkodzony.parent.mkdir()
    uszkodzony.write_bytes(np.random.default_rng(7).integers(0, 256, 3000, dtype=np.uint8).tobytes())
    _ustaw_czas(uszkodzony, kiedy)
    _zapisz_stl(pula30[5].siatka, katalog / "Cyrkon" / "Testowy 106" / "11.stl", kiedy)

    oryginal = trimesh.load

    def load_z_blokada(plik, *a, **kw):
        if "Testowy 106" in str(plik):
            raise PermissionError(13, "plik zablokowany przez inny proces", str(plik))
        return oryginal(plik, *a, **kw)

    monkeypatch.setattr(trimesh, "load", load_z_blokada)
    b = _nowa_baza(ust)
    r = _indeks().skanuj(ust, b, teraz)
    assert r.bledy == 2
    assert sorted(r.bledne) == ["Testowy 105/11.stl", "Testowy 106/11.stl"]
    rekordy = {x["folder"]: x for x in b.projekty()}
    assert len(rekordy) == 6
    z_cechami = {f for f, x in rekordy.items() if x["d2"] is not None and x["wym1_mm"] is not None}
    assert z_cechami == {f"Testowy {101 + i}" for i in range(4)}
    assert rekordy["Testowy 105"]["d2"] is None and rekordy["Testowy 105"]["objetosc_mm3"] is None

    # bez zmiany pliku nie ma ponownej proby
    r = _indeks().skanuj(ust, b, teraz)
    assert (r.nowe, r.zmienione, r.usuniete, r.bledy) == (0, 0, 0, 0)

    # plik poprawiony (inny mtime i rozmiar) -> ponowna proba, cechy wypelnione
    monkeypatch.setattr(trimesh, "load", oryginal)
    _zapisz_stl(pula30[6].siatka, uszkodzony, teraz - timedelta(hours=1))
    r = _indeks().skanuj(ust, b, teraz)
    assert (r.zmienione, r.bledy) == (1, 0)
    po = {x["folder"]: x for x in b.projekty()}["Testowy 105"]
    assert po["objetosc_mm3"] == pytest.approx(pula30[6].siatka.volume, rel=0.01)


def test_indeks_pomija_stare_pliki(tmp_path, pula30, monkeypatch):
    teraz = datetime(2026, 10, 27, 10, 0)
    katalog = tmp_path / "stanowisko"
    ust = _ustawienia(katalog, monkeypatch)
    assert ust.pula.usuwaj_po_dniach == 10
    _zapisz_stl(pula30[0].siatka, katalog / "Cyrkon" / "Stary 101" / "11.stl", teraz - timedelta(days=11))
    _zapisz_stl(pula30[1].siatka, katalog / "Cyrkon" / "Prawie 102" / "11.stl",
                teraz - timedelta(days=9, hours=12))
    _zapisz_stl(pula30[2].siatka, katalog / "Cyrkon" / "Nowy 103" / "11.stl", teraz - timedelta(hours=1))
    b = _nowa_baza(ust)
    r = _indeks().skanuj(ust, b, teraz)
    assert r.nowe == 2
    assert {x["folder"] for x in b.projekty(usuniete=True)} == {"Prawie 102", "Nowy 103"}

    # dzien pozniej: "Prawie 102" ma juz 10,5 dnia - nie wraca jako nowy ani usuniety
    jutro = teraz + timedelta(days=1)
    r = _indeks().skanuj(ust, b, jutro)
    assert (r.nowe, r.zmienione, r.usuniete) == (0, 0, 0)
    assert b.usun_starsze_niz(ust.pula.usuwaj_po_dniach, jutro) == 1
    r = _indeks().skanuj(ust, b, jutro)
    assert (r.nowe, r.zmienione, r.usuniete) == (0, 0, 0)
    assert {x["folder"] for x in b.projekty(usuniete=True)} == {"Nowy 103"}


def test_pula_wieczor_te_same_nazwy(tmp_path, pula30, monkeypatch):
    teraz = datetime(2026, 10, 27, 10, 0)  # wtorek
    katalog = tmp_path / "stanowisko"
    ust = _ustawienia(katalog, monkeypatch)
    pliki = {
        "Stary 101/36.stl": datetime(2026, 10, 22, 12, 0),
        "Nowy 102/36.stl": datetime(2026, 10, 26, 12, 0),
        "Nowy A 201/47.stl": datetime(2026, 10, 26, 12, 0),
        "Nowy B 202/47.stl": datetime(2026, 10, 27, 8, 0),
    }
    for i, (sciezka, kiedy) in enumerate(pliki.items()):
        _zapisz_stl(pula30[i].siatka, katalog / "Cyrkon" / sciezka, kiedy)
    b = _nowa_baza(ust)
    _indeks().skanuj(ust, b, teraz)
    ids = {x["sciezka"]: x["id"] for x in b.projekty()}

    csv = _zapisz_csv(tmp_path / "wspolczynniki.csv", [
        "36.stl;K-01;1,2101;2026-10-27",  # bez folderu: Stary 101 poza oknem -> tylko Nowy 102
        "Stary 101\\36.STL;K-01;1,2102;2026-10-26",  # z folderem: dokladnie Stary 101
        "47.stl;K-02;1,2103;2026-10-26",  # dwoch kandydatow w oknie -> blizszy dacie z CSV
        "47.stl;K-02;1,2104;2026-10-27",
        "Brak 999/36.stl;K-03;1,2105;2026-10-27",  # folder podany, ale nie ma go w bazie
    ])
    wynik = _indeks().pula_wieczor(b, _wspolczynniki().wczytaj(csv), teraz, ustawienia=ust)
    wpisy, brakujace = wynik
    assert brakujace == 1
    assert wynik.niejednoznaczne == 2
    assert [(x.projekt_id, x.wspolczynnik) for x in wpisy] == [
        (ids["Nowy 102/36.stl"], pytest.approx(1.2101)),
        (ids["Stary 101/36.stl"], pytest.approx(1.2102)),
        (ids["Nowy A 201/47.stl"], pytest.approx(1.2103)),
        (ids["Nowy B 202/47.stl"], pytest.approx(1.2104)),
    ]


def test_pule_z_ustawien(tmp_path, pula30, monkeypatch):
    teraz = datetime(2026, 10, 28, 10, 0)  # sroda
    katalog = tmp_path / "stanowisko"
    ust = _ustawienia_z(katalog, monkeypatch, dni_rano=1, dni_wieczor=1)
    daty = {
        "Piatek 203": datetime(2026, 10, 23, 15, 0),
        "Wtorek 207": datetime(2026, 10, 27, 23, 30),
        "Dzis 208": datetime(2026, 10, 28, 7, 0),
    }
    _drzewo_dat(katalog, pula30, daty)
    b = _nowa_baza(ust)
    _indeks().skanuj(ust, b, teraz)
    wpisy = _indeks().pula_rano(b, teraz, ustawienia=ust)
    assert {b.projekt(w.projekt_id)["folder"] for w in wpisy} == {"Wtorek 207", "Dzis 208"}

    csv = _zapisz_csv(tmp_path / "wspolczynniki.csv", [
        "Wtorek 207/11.stl;K-01;1,22;2026-10-27",
        "Dzis 208/11.stl;K-01;1,23;2026-10-28",
    ])
    wpisy, brakujace = _indeks().pula_wieczor(b, _wspolczynniki().wczytaj(csv), teraz, ustawienia=ust)
    assert brakujace == 0
    assert [b.projekt(w.projekt_id)["folder"] for w in wpisy] == ["Dzis 208"]


def test_nazwy_nfc():
    n = _nazwy()
    z = n.rozbierz("Wis\u0301niewska 3")
    assert z.nazwisko == "Wi\u015bniewska"
    assert z.kuweta == "3"
    assert n.znormalizuj("  Wis\u0301niewska  003 ") == "wi\u015bniewska 3"
    assert n.numer_zeba("Wis\u0301niewska 36.stl") == 36


def test_wspolczynniki_kodowanie(tmp_path):
    w = _wspolczynniki()
    tekst = ("plik;krazek;wspolczynnik;data\n36.stl;K-01;1,22;2026-10-27\n"
             "Wi\u015bniewska.stl;K-01;1,23;2026-10-27\n")
    cp1250 = tmp_path / "cp1250.csv"
    cp1250.write_bytes(tekst.encode("cp1250"))
    with pytest.raises(ValueError, match=r"zapisz jako CSV UTF-8") as e:
        w.wczytaj(cp1250)
    assert re.search(r"\b3\b", str(e.value))

    puste = tmp_path / "puste.csv"
    puste.write_text("\n\n" + tekst, encoding="utf-8")
    with pytest.raises(ValueError, match=r"zapisz jako CSV UTF-8") as e:
        w.wczytaj(puste)
    assert re.search(r"\b1\b", str(e.value))


# --- nazwy: kod albo imie po numerze kuwety -----------------------------------


@pytest.mark.parametrize("folder, kuweta, nazwisko", [
    ("Kowalski 1784 PG", "1784", "Kowalski"),
    ("Kowalski 1784PG", "1784", "Kowalski"),
    ("Kowalski 1784 Patrycja", "1784", "Kowalski"),
    ("Kowalski 1784pg", "1784", "Kowalski"),
    ("Kowalski 0041AB", "41", "Kowalski"),
    ("Kowalski 12345", None, "Kowalski"),
    ("Kowalski 12345PG", None, "Kowalski"),
    # litery przed cyframi: liczba nie jest samodzielna -> brak kuwety, nazwisko = caly kod literowy
    ("PG1784", None, "PG"),
    ("Kowalski PG1784", None, "Kowalski"),
    # cyfry Unicode (pelnej szerokosci) i NFC jak dotad
    ("Kowalski \uff11\uff17\uff18\uff14PG", "1784", "Kowalski"),
    ("Wis\u0301niewska 3PG", "3", "Wi\u015bniewska"),
])
def test_rozbierz_kod_po_numerze(folder, kuweta, nazwisko):
    z = _nazwy().rozbierz(folder)
    assert z.kuweta == kuweta
    assert z.nazwisko == nazwisko
    assert z.prywatne is False


def test_znormalizuj_kod_po_numerze():
    zn = _nazwy().znormalizuj
    assert zn("Kowalski 1784PG") == "kowalski 1784 pg"
    assert zn("Kowalski 1784PG") == zn("Kowalski 1784 PG")
    assert zn("Kowalski 0041ab") == "kowalski 41 ab"
    assert zn("Kowalski 1784 Patrycja") == "kowalski 1784 patrycja"
    assert zn("PG1784") == "pg1784"


@pytest.mark.parametrize("plik, numer", [
    ("Kowalski 1784PG 36.stl", 36),
    ("Kowalski_1784PG_47.stl", 47),
    ("36PG.stl", None),
])
def test_numer_zeba_kod_po_numerze(plik, numer):
    assert _nazwy().numer_zeba(plik) == numer
