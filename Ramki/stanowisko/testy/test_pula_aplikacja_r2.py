"""E3-A5i runda 2 - poprawki po recenzji PR #32 runda 1 (P1-P6, D1-D4, D9, D13).

P1 odswiezanie katalogu zlecen (start, "Odswiez pule", tryb, doba, plik wspolczynnikow - nie po wyniku); P2 zmiana krazka po
"Ukruszona" przenosi punkt; P3 projekt wpisu usuniety -> nastepca z tego zlecenia / kuwety albo brak, nigdy globalne sha16; P4 przyczyna
pustej puli wpisow i krazki sprzeczne na ekranie; P5 moduly z DLL watku indeksu ladowane przy starcie; P6 plytka drugiego typu dostaje
pule drugiego trybu. Dane FIKCYJNE, tylko tmp_path.
"""
from __future__ import annotations

import ast
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

import test_kontroler_api as TK
import test_pula_aplikacja as T1
from stanowisko import baza as B
from stanowisko import session as SE
from stanowisko import session_rano as SR

STANOWISKO = Path(__file__).resolve().parent.parent
atrapy_puli = T1.atrapy_puli  # fixture modulu r1 (24 atrapy koron w folderach zlecen)


class Zegar:
    """Zegar aplikacji do przestawiania (doba robocza w P1); bezpieczny dla watkow (tylko odczyt atrybutu)."""

    def __init__(self, t: dt.datetime):
        self.t = t

    def __call__(self) -> dt.datetime:
        return self.t


# ----------------------------------------------------------------------------
# P1: odswiezanie katalogu
# ----------------------------------------------------------------------------
def test_r2_p1_odswiezanie_katalogu_tryb_doba_plik_nie_po_wyniku(atrapy_puli, tmp_path):
    from stanowisko import aplikacja as AP

    drzewo, millbox = atrapy_puli[0].parents[2], tmp_path / "millbox"
    zegar = Zegar(dt.datetime.combine(dt.date.today(), dt.time(19, 0)))
    dzis = zegar.t.date().isoformat()
    T1.zapisz_csv(millbox, [(p.name, "K-120", 1.20, dzis) for p in atrapy_puli[:4]])
    ust = T1.ustawienia_puli(tmp_path, drzewo, millbox)
    (tmp_path / "eksport").mkdir()
    k = AP.Aplikacja(ust, zegar=zegar, funkcja_analizy=T1.FUNKCJA_Z_PULA, parametry_scannera=TK.PARAMETRY_SCANNERA)
    try:
        k.start()
        assert k.wybierz_operatora("Technik A")
        T1.czekaj(k, lambda: k.stan().pula.stan == "gotowa" and k.stan().pula.czas_budowy_s is not None, "pula po starcie", 180)
        assert k.odswiezenia_katalogu == ["glosne"]
        (tmp_path / "eksport" / "s1.stl").write_bytes(TK.plik_skanu({"gniazda": {1: "zielony"}, "numer": 1}))
        T1.czekaj(k, lambda: len(k.stan().plytki) == 1, "wynik skanu", 120)
        for _ in range(60):  # 1,2 s: kontrola co 1 s nie widzi zmian
            k.przetworz()
            time.sleep(0.02)
        assert k.odswiezenia_katalogu == ["glosne"]  # P1: wynik nie odswieza katalogu
        assert k.przelacz_tryb("rano")
        assert k.odswiezenia_katalogu[-1] == "tryb" and k.stan().pula.stan == "liczenie"  # skany nowego trybu czekaja na swieza pule
        T1.czekaj(k, lambda: k.stan().pula.stan in ("gotowa", "pusta") and not k._liczenie_puli, "pula po zmianie trybu", 120)
        time.sleep(0.05)
        T1.zapisz_csv(millbox, [(p.name, "K-120", 1.20, dzis) for p in atrapy_puli[:5]])  # nowy wiersz w pliku wspolczynnikow
        T1.czekaj(k, lambda: k.odswiezenia_katalogu[-1] == "plik_wspolczynnikow", "odswiezenie po zmianie pliku", 30)
        T1.czekaj(k, lambda: not k._liczenie_puli, "koniec odswiezenia", 120)
        zegar.t = zegar.t + dt.timedelta(hours=12)  # nastepna doba robocza (07:00)
        T1.czekaj(k, lambda: k.odswiezenia_katalogu[-1] == "doba", "odswiezenie po zmianie doby", 30)
        assert k.przelacz_tryb("wieczor")
        T1.czekaj(k, lambda: k.stan().pula.stan in ("gotowa", "pusta") and not k._liczenie_puli, "pula wieczorna nowej doby", 120)
        assert k.stan().pula.wpisy == 0 or k.stan().pula.wpisy == 5
    finally:
        k.zamknij()


def test_r2_d8_odswiez_pule_w_trakcie_odswiezenia_bez_drugiego_watku(atrapy_puli, tmp_path):
    """D8: "Odswiez pule" w trakcie odswiezania - bez drugiego watku indeksu; kolejne odswiezenie glosne po biezacym."""
    from stanowisko import aplikacja as AP

    drzewo, millbox = atrapy_puli[0].parents[2], tmp_path / "millbox"
    T1.zapisz_csv(millbox, [(p.name, "K-120", 1.20, dt.date.today().isoformat()) for p in atrapy_puli[:3]])
    ust = T1.ustawienia_puli(tmp_path, drzewo, millbox)
    k = AP.Aplikacja(ust, funkcja_analizy=T1.FUNKCJA_Z_PULA, parametry_scannera=TK.PARAMETRY_SCANNERA)
    try:
        k.start()
        assert k._liczenie_puli
        assert k.odswiez_pule()  # w trakcie odswiezenia startowego: bez drugiego watku indeksu
        assert k.odswiezenia_katalogu == ["glosne"] and k._pula_ponownie_glosno and k.stan().pula.stan == "liczenie"
        T1.czekaj(k, lambda: len(k.odswiezenia_katalogu) == 2 and not k._liczenie_puli and k.stan().pula.stan == "gotowa", "drugie odswiezenie", 120)
        assert k.odswiezenia_katalogu == ["glosne", "odswiez_pule"]
    finally:
        k.zamknij()


def test_r2_d3_blad_dziennika_nie_zostawia_liczenia(atrapy_puli, tmp_path, monkeypatch):
    from stanowisko import aplikacja as AP

    drzewo, millbox = atrapy_puli[0].parents[2], tmp_path / "millbox"
    T1.zapisz_csv(millbox, [(p.name, "K-120", 1.20, dt.date.today().isoformat()) for p in atrapy_puli[:2]])
    k = AP.Aplikacja(T1.ustawienia_puli(tmp_path, drzewo, millbox), funkcja_analizy=T1.FUNKCJA_Z_PULA, parametry_scannera=TK.PARAMETRY_SCANNERA)
    prawdziwy = k.sesja.baza.zdarzenie

    def zdarzenie(zrodlo, typ, *a, **kw):
        if typ == "pula_wpisow":
            raise B.BladBazy("baza zajeta (proba)")
        return prawdziwy(zrodlo, typ, *a, **kw)

    monkeypatch.setattr(k.sesja.baza, "zdarzenie", zdarzenie)
    try:
        k.start()
        T1.czekaj(k, lambda: not k._liczenie_puli, "koniec odswiezenia", 120)
        assert k.stan().pula.stan == "gotowa" and k.stan().pula.wpisy == 2
    finally:
        k.zamknij()


# ----------------------------------------------------------------------------
# P2 / D9: zmiana krazka po "Ukruszona", cofniecie wyboru
# ----------------------------------------------------------------------------
def _baza_dwa_zlecenia(tmp_path: Path):
    baza = B.otworz(tmp_path / "dane" / "stanowisko.sqlite")
    with baza.transakcja():
        z1 = baza.wstaw("zlecenia", zrodlo="cyrkon", folder="Testowski 1001 zs", folder_norm="testowski 1001 zs", kuweta="1001", mtime=1.0, dodano="2026-11-18T08:00:00")
        z2 = baza.wstaw("zlecenia", zrodlo="cyrkon", folder="Probna 1002 kor", folder_norm="probna 1002 kor", kuweta="1002", mtime=1.0, dodano="2026-11-18T08:00:00")
        p1 = baza.wstaw("projekty", zlecenie_id=z1, plik="a.stl", sha16="a" * 16, zeby="11", typ="crown", zaindeksowano="2026-11-18T08:00:00")
        p2 = baza.wstaw("projekty", zlecenie_id=z2, plik="a.stl", sha16="a" * 16, zeby="11", typ="crown", zaindeksowano="2026-11-18T08:00:00")
        f1 = baza.wstaw("frezowania", projekt_id=p1, plik_w_raporcie="a.stl", krazek="K-1", wspolczynnik=1.2, data="2026-11-18", zrodlo="csv")
        f2 = baza.wstaw("frezowania", projekt_id=p2, plik_w_raporcie="a.stl", krazek="K-2", wspolczynnik=1.2, data="2026-11-17", zrodlo="csv")
    return baza, (p1, p2), (f1, f2)


def test_r2_p2_zmiana_krazka_po_ukruszonej_przenosi_punkt_i_cofniecia(tmp_path):
    baza, (p1, p2), (f1, f2) = _baza_dwa_zlecenia(tmp_path)
    try:
        s = SE.Sesja(baza, operatorzy=["Technik A"])
        s.wybierz_operatora("Technik A")
        wpisy = [{"frezowanie_id": f1, "projekt_id": p1, "krazek": "K-1", "wspolczynnik": 1.2},
                 {"frezowanie_id": f2, "projekt_id": p2, "krazek": "K-2", "wspolczynnik": 1.2}]
        g = T1._gniazdo(3, "a" * 16, projekt_id=None, frezowanie_id=None, wpisy=wpisy)
        g["status_gniazda"] = "czerwony"
        skan_id = s.przyjmij_wynik({"plik": "C:/Skany/s.stl", "sha16": "1" * 16}, T1._wynik([g]))
        praca = baza.wiersz("SELECT * FROM prace WHERE skan_id = ?", (skan_id,))
        assert praca["projekt_id"] is None and praca["frezowanie_id"] is None

        def punkty():
            return {w["projekt_id"]: (w["stan"], w["praca_id"]) for w in baza.wiersze("SELECT * FROM stan_punktow")}

        s.wybierz_wpis(praca["id"], f1)
        s.ukruszona(praca["id"])
        assert punkty() == {p1: ("do_dofrezowania", praca["id"])}
        s.wybierz_wpis(praca["id"], f2)  # P2: punkt przechodzi z P1 na P2
        assert punkty()[p2] == ("do_dofrezowania", praca["id"]) and punkty()[p1][0] == "oczekuje"
        assert [x["kuweta"] for x in s.do_dofrezowania()] == ["1002"]
        s.cofnij_wpis(praca["id"])  # D9: wraca poprzedni wybor (K-1)
        assert baza.wiersz("SELECT frezowanie_id, projekt_id FROM prace WHERE id = ?", (praca["id"],)) == {"frezowanie_id": f1, "projekt_id": p1}
        assert punkty()[p1] == ("do_dofrezowania", praca["id"]) and punkty()[p2][0] == "oczekuje"
        s.cofnij_wpis(praca["id"])  # i do "nierozstrzygniety"
        assert baza.wiersz("SELECT frezowanie_id, projekt_id FROM prace WHERE id = ?", (praca["id"],)) == {"frezowanie_id": None, "projekt_id": None}
        assert punkty()[p1][0] == "oczekuje" and punkty()[p2][0] == "oczekuje"
        with pytest.raises(SE.BladSesji):
            s.cofnij_wpis(praca["id"])  # nic do cofniecia
        s.wybierz_wpis(praca["id"], f2)
        s.cofnij(praca["id"])  # cofniecie "Ukruszona" po zmianie krazka - spojnie
        assert punkty()[p1][0] == "oczekuje" and punkty()[p2][0] == "oczekuje" and s.do_dofrezowania() == []
        x = s.stan_wieczoru()["skany"][0]["prace"][0]
        assert x["krazek"] == "K-2" and x["wybor_wpisu"]["wartosc"] == str(f2)
    finally:
        baza.zamknij()


def test_r2_d9_kontroler_cofnij_wpis(tmp_path):
    from stanowisko import kontroler_api as K

    assert "cofnij_wpis" in K.POLECENIA
    a = K.AtrapaKontrolera()
    try:
        baza = a.sesja.baza
        with baza.transakcja():
            z = baza.wstaw("zlecenia", zrodlo="cyrkon", folder="Zmyslony 3400 x", folder_norm="zmyslony 3400 x", kuweta="3400", mtime=1.0, dodano="2026-11-18T08:00:00")
            p = baza.wstaw("projekty", zlecenie_id=z, plik="c.stl", sha16="c" * 16, zeby="36", typ="crown", zaindeksowano="2026-11-18T08:00:00")
            f1 = baza.wstaw("frezowania", projekt_id=p, plik_w_raporcie="c.stl", krazek="K-1", wspolczynnik=1.22, data="2026-11-18", zrodlo="csv")
            f2 = baza.wstaw("frezowania", projekt_id=p, plik_w_raporcie="c.stl", krazek="K-2", wspolczynnik=1.22, data="2026-11-17", zrodlo="csv")
        wpisy = [{"frezowanie_id": f1, "projekt_id": p, "krazek": "K-1", "wspolczynnik": 1.22},
                 {"frezowanie_id": f2, "projekt_id": p, "krazek": "K-2", "wspolczynnik": 1.22}]
        a.sesja.przyjmij_wynik({"plik": "C:/Skany/s.stl", "sha16": "3" * 16},
                               T1._wynik([T1._gniazdo(2, "c" * 16, projekt_id=p, frezowanie_id=None, krazek=None, wpisy=wpisy)]))
        a._odswiez()
        assert a.wybierz_operatora("Technik A")
        praca = a.stan().plytki[-1].gniazdo(2).praca
        assert "cofnij_wpis" not in praca.dozwolone
        assert a.wybierz_wpis(praca.praca_id, f1)
        praca = a.stan().plytki[-1].gniazdo(2).praca
        assert "cofnij_wpis" in praca.dozwolone and praca.wybor_wpisu_osoba == "Technik A"
        assert a.cofnij_wpis(praca.praca_id)
        praca = a.stan().plytki[-1].gniazdo(2).praca
        assert praca.krazek is None and "cofnij_wpis" not in praca.dozwolone and not any(w.wybrany for w in praca.wpisy_do_wyboru)
        assert not a.wykonaj("cofnij_wpis", "x")
    finally:
        a.zamknij()


# ----------------------------------------------------------------------------
# P3: usuniety projekt wpisu
# ----------------------------------------------------------------------------
def test_r2_p3_usuniety_projekt_wpisu_nastepca_albo_brak_nigdy_globalne_sha16(tmp_path):
    baza = B.otworz(tmp_path / "dane" / "stanowisko.sqlite")
    try:
        with baza.transakcja():
            za = baza.wstaw("zlecenia", zrodlo="cyrkon", folder="Testowski 3263 zs", folder_norm="testowski 3263 zs", kuweta="3263", mtime=1.0, dodano="2026-11-18T08:00:00")
            zb = baza.wstaw("zlecenia", zrodlo="prywatne", folder="#77 Kopia", folder_norm="#77 kopia", kuweta="#77", mtime=1.0, dodano="2026-11-18T08:00:00")
            # STL "a": projekt wpisu usuniety (zmiana nazwy pliku), nastepca w TYM SAMYM zleceniu
            pa_stary = baza.wstaw("projekty", zlecenie_id=za, plik="a.stl", sha16="a" * 16, zeby="11", typ="crown", zaindeksowano="x", usuniety=1)
            pa_nowy = baza.wstaw("projekty", zlecenie_id=za, plik="a2.stl", sha16="a" * 16, zeby="11", typ="crown", zaindeksowano="x")
            # STL "b": projekt wpisu usuniety, jedyny zywy projekt o tej zawartosci w INNYM zleceniu (kopia w "Prywatne")
            pb_stary = baza.wstaw("projekty", zlecenie_id=za, plik="b.stl", sha16="b" * 16, zeby="14", typ="crown", zaindeksowano="x", usuniety=1)
            baza.wstaw("projekty", zlecenie_id=zb, plik="b.stl", sha16="b" * 16, zeby="14", typ="crown", zaindeksowano="x")
        s = SE.Sesja(baza, operatorzy=["Technik A"])
        rano = SR.SesjaRano(s)

        def wpis(pid):
            return {"frezowanie_id": None, "projekt_id": pid, "krazek": None, "wspolczynnik": 1.0}

        g = [T1._gniazdo(1, "a" * 16, projekt_id=pa_stary, wpisy=[wpis(pa_stary)]), T1._gniazdo(2, "b" * 16, projekt_id=pb_stary, wpisy=[wpis(pb_stary)])]
        for x in g:
            x["skala"]["wspolczynnik_puli"] = 1.0
        skan_id = rano.przyjmij_wynik({"plik": "C:/Skany/r.stl", "sha16": "9" * 16}, T1._wynik(g, uklad="poranna", numer=4))
        prace = {p["gniazdo"]: p for p in baza.wiersze("SELECT * FROM prace WHERE skan_id = ?", (skan_id,))}
        assert prace[1]["projekt_id"] == pa_nowy  # nastepca z tego samego zlecenia (regula _nastepcy)
        assert prace[2]["projekt_id"] is None  # nie kopia z innego zlecenia (globalne sha16 dawaloby zlego pacjenta)
        s._wpisy_puli_skanu = None  # z dziennika (cofniecie przypisania po restarcie) - ta sama regula
        assert rano._przypisanie_auto(prace[2]) is None and rano._przypisanie_auto(prace[1]) == pa_nowy
        # wieczor: projekt wpisu usuniety = bez przypisania
        w = s.przyjmij_wynik({"plik": "C:/Skany/w.stl", "sha16": "8" * 16}, T1._wynik([T1._gniazdo(5, "b" * 16, projekt_id=pb_stary, wpisy=[wpis(pb_stary)])]))
        assert baza.wiersz("SELECT projekt_id FROM prace WHERE skan_id = ?", (w,))["projekt_id"] is None
    finally:
        baza.zamknij()


# ----------------------------------------------------------------------------
# P4: przyczyna pustej puli, krazki sprzeczne
# ----------------------------------------------------------------------------
def test_r2_p4_pusta_pula_wpisow_przyczyna_i_krazki_sprzeczne_na_ekranie(atrapy_puli, tmp_path):
    from stanowisko import aplikacja as AP
    from stanowisko import statusy as ST

    drzewo, millbox = atrapy_puli[0].parents[2], tmp_path / "millbox"
    millbox.mkdir()
    ust = T1.ustawienia_puli(tmp_path, drzewo, millbox)
    (tmp_path / "eksport").mkdir()
    k = AP.Aplikacja(ust, funkcja_analizy=T1.FUNKCJA_Z_PULA, parametry_scannera=TK.PARAMETRY_SCANNERA)
    try:
        k.start()
        assert k.wybierz_operatora("Technik A")
        T1.czekaj(k, lambda: k.stan().pula.stan == "pusta", "pusta pula (brak pliku wspolczynnikow)", 120)
        (tmp_path / "eksport" / "s1.stl").write_bytes(TK.plik_skanu({"gniazda": {1: "zielony"}, "numer": 1}))
        T1.czekaj(k, lambda: any(x.rodzaj == "pula_wpisow_pusta" for x in k.stan().komunikaty), "komunikat pustej puli", 60)
        kom = next(x for x in k.stan().komunikaty if x.rodzaj == "pula_wpisow_pusta")
        assert ST.PRZYCZYNY_PULI["csv_brak"] in kom.tekst and "folderze projektow" not in kom.tekst
        assert k.stan().pula.przyczyna and ST.PRZYCZYNY_PULI["csv_brak"] in k.stan().pula.przyczyna
        dzis = dt.date.today().isoformat()
        T1.zapisz_csv(millbox, [(atrapy_puli[0].name, "K-9", 1.20, dzis), (atrapy_puli[1].name, "K-9", 1.25, dzis),  # K-9: dwie wartosci
                                (atrapy_puli[2].name, "K-1", 1.22, dzis), (atrapy_puli[3].name, "K-1", 1.22, dzis)])
        assert k.odswiez_pule()
        T1.czekaj(k, lambda: k.stan().pula.stan == "gotowa" and len(k.stan().plytki) == 1, "pula po poprawie pliku i skan", 180)
        s = k.stan()
        assert s.pula.wpisy == 2 and s.pula.krazki_sprzeczne == ("K-9",) and "sprzeczne wspolczynniki: 2" in s.pula.napis
        kr = next(x for x in s.komunikaty if x.rodzaj == "pula_wpisow_krazki")
        assert "K-9" in kr.tekst and "2" in kr.tekst
        assert not any(x.rodzaj == "pula_wpisow_pusta" for x in s.komunikaty)
    finally:
        k.zamknij()


# ----------------------------------------------------------------------------
# P5: moduly z DLL watku indeksu
# ----------------------------------------------------------------------------
def test_r2_p5_moduly_watku_indeksu_zaladowane_przy_starcie(atrapy_puli, tmp_path):
    """Po ``zaladuj_moduly_dll(MODULY_DLL + MODULY_DLL_PULI)`` cechy i miniatura nowego pliku (watek indeksu) nie laduja zadnego
    nowego modulu z DLL (.pyd); ``main()`` laduje moduly puli przed ``Aplikacja``."""
    skrypt = tmp_path / "proba_dll.py"
    skrypt.write_text(f"""
import sys
sys.path.insert(0, {str(STANOWISKO)!r})
from stanowisko import aplikacja as AP
wynik = AP.zaladuj_moduly_dll(AP.MODULY_DLL + AP.MODULY_DLL_PULI)
def rozszerzenia():
    return {{n for n, m in list(sys.modules.items()) if str(getattr(m, "__file__", "") or "").lower().endswith((".pyd", ".dll"))}}
przed = rozszerzenia()
from stanowisko import indeks as I
dane = open({str(atrapy_puli[0])!r}, "rb").read()
m = I.siatka_z_bajtow(dane)
I.cechy_siatki(m, "2026-11-18_proba-11-crown_cad.stl")
I.miniatura_png(m, "2026-11-18_proba-11-crown_cad.stl")
print(sorted(rozszerzenia() - przed))
print(sorted(n for n, ok in wynik.items() if ok is not True))
""", encoding="utf-8")
    wynik = subprocess.run([sys.executable, str(skrypt)], capture_output=True, text=True, timeout=300, cwd=str(tmp_path),
                           env={**os.environ, "PYTHONPATH": os.pathsep.join(sys.path)})
    assert wynik.returncode == 0, wynik.stderr[-2000:]
    nowe, brak = wynik.stdout.strip().splitlines()[-2:]
    assert nowe == "[]", nowe
    assert all(n in ("'pythoncom'", "'win32com.client'") for n in brak.strip("[]").split(", ") if n), brak
    drzewo = ast.parse((STANOWISKO / "stanowisko" / "aplikacja.py").read_text(encoding="utf-8"))
    main = next(n for n in drzewo.body if isinstance(n, ast.FunctionDef) and n.name == "main")
    linie = [w.lineno for w in ast.walk(main) if isinstance(w, ast.Call) and getattr(w.func, "id", "") == "zaladuj_moduly_dll"
             and any(getattr(a, "id", "") == "MODULY_DLL_PULI" for a in w.args)]
    aplikacja = min(w.lineno for w in ast.walk(main) if isinstance(w, ast.Call) and getattr(w.func, "id", "") == "Aplikacja")
    assert linie and linie[0] < aplikacja


# ----------------------------------------------------------------------------
# P6: plytka drugiego typu
# ----------------------------------------------------------------------------
def test_r2_p6_plytka_poranna_wieczorem_dostaje_pule_poranna(atrapy_puli, tmp_path):
    from stanowisko import silnik as SI

    def opis(pliki, wsp, typ, druga=None):
        wpisy = tuple({"sha16": hashlib.sha256(p.read_bytes()).hexdigest()[:16], "wspolczynnik": wsp, "krazek": None,
                       "frezowanie_id": None, "projekt_id": 100 + i} for i, p in enumerate(pliki))
        return SI.OpisPuli(wpisy=wpisy, sciezki={100 + i: p for i, p in enumerate(pliki)}, typ_plytki=typ, druga=druga, rodzaj=typ)

    rano = opis(atrapy_puli[:2], 1.0, "poranna")
    wieczor = opis(atrapy_puli[2:5], 1.22, "wieczorna", druga=rano)
    assert SI.PamiecPul.opis_dla_plytki(wieczor, 1.0) is rano  # plytka rozpoznana jako poranna (wspolczynnik domyslny 1,0)
    assert SI.PamiecPul.opis_dla_plytki(wieczor, 1.225) is wieczor and SI.PamiecPul.opis_dla_plytki(rano, 1.0) is rano
    pamiec = SI.PamiecPul(2, TK.ustawienia_probne(tmp_path))
    assert len(pamiec.dla(wieczor)(1.0)) == 2 and len(pamiec.dla(wieczor)(1.225)) == 3


# ----------------------------------------------------------------------------
# D: zdarzenia puli z rodzajem, przyczyna bledu na pasku, sprzatanie tylko przy pierwszym starcie, propozycja po polu
# ----------------------------------------------------------------------------
def test_r2_d1_d2_zdarzenia_innej_puli_pomijane_i_blad_budowy_na_pasku():
    from stanowisko import aplikacja as AP
    from stanowisko import silnik as SI
    from stanowisko import statusy as ST

    k = AP.Aplikacja.__new__(AP.Aplikacja)  # tylko logika paska (bez bazy i silnika)
    opis = SI.OpisPuli(wpisy=({"sha16": "a" * 16, "wspolczynnik": 1.2, "projekt_id": 1},), sciezki={1: Path("x.stl")}, rodzaj="wieczor:2")
    k._budowa = {"opis": opis, "gotowe": 0, "razem": 10, "czas_s": None, "blad": None, "liczniki": {}}
    k._pula_stan, k._pula_liczba, k._pule_wpisow, k.tryb = "gotowa", 10, {}, "wieczor"
    k._zdarzenie_puli(SI.ZdarzenieSilnika("pula", 0.0, etap="budowa", wynik={"gotowe": 7, "razem": 9, "rodzaj": "rano:1"}))
    assert (k._budowa["gotowe"], k._budowa["razem"]) == (0, 10)  # D1: postep innej puli nie zmienia paska
    k._zdarzenie_puli(SI.ZdarzenieSilnika("pula", 0.0, etap="budowa", wynik={"gotowe": 4, "razem": 10, "rodzaj": "wieczor:2"}))
    assert k._budowa["gotowe"] == 4
    k._zdarzenie_puli(SI.ZdarzenieSilnika("pula", 0.0, etap="blad", blad="OSError: dysk niedostepny", wynik={"koniec_prob": True, "rodzaj": "wieczor:2"}))
    napis = k._napis_puli_wpisow()
    assert "dysk niedostepny" in napis and napis.endswith(ST.NAPIS_BLAD_BUDOWY_PULI.format(blad="OSError: dysk niedostepny"))


def test_r2_d4_sprzatanie_tylko_przy_pierwszym_starcie_procesu_roboczego(tmp_path):
    from stanowisko import silnik as SI

    ust = TK.ustawienia_probne(tmp_path)
    katalog = tmp_path / "dane" / "pula_cache" / "projekty"
    katalog.mkdir(parents=True)

    def stary(nazwa):
        p = katalog / f"{'0' * 16}_1.2_auto_h_{nazwa}.npz"
        p.write_bytes(b"x")
        os.utime(p, (time.time() - 40 * 86400,) * 2)
        return p

    p1 = stary("pierwszy")
    zdarzenia = []
    TK.pula_probna(tmp_path)
    plik = tmp_path / "zabij.stl"
    plik.write_bytes(TK.plik_skanu({"gniazda": {1: "zielony"}, "numer": 1, "zabij": True}))
    with SI.Silnik(ust, funkcja=TK.FUNKCJA_SZTUCZNA, na_zdarzenie=zdarzenia.append, pamiec_puli_dni=30) as s:
        t0 = time.monotonic()
        while s.stan()["pamiec_puli_usuniete"] is None:
            assert time.monotonic() - t0 < 120
            time.sleep(0.05)
        assert s.stan()["pamiec_puli_usuniete"] == 1 and not p1.exists()
        p2 = stary("po_awarii")  # wpis "uzywany z pamieci procesu" (mtime stary) - nowy proces po awarii go nie usuwa
        s.zlec(SI.ZadanieAnalizy(skan=plik, pula=SI.OpisPuli(foldery=(str(tmp_path / "projekty"),))))
        while not any(z.typ == "blad" for z in zdarzenia):
            assert time.monotonic() - t0 < 120
            time.sleep(0.05)
        while s.stan()["starty_procesu"] < 2:
            assert time.monotonic() - t0 < 120
            time.sleep(0.05)
        time.sleep(1.0)
        assert p2.exists() and s.stan()["pamiec_puli_usuniete"] == 1


def test_r2_d13_propozycja_po_polu_ratunek():
    uwaga = ["ratunek: pelne dopasowanie 4 kandydatow wg deskryptorow FPFH (praca nierozpoznana albo niepewna)"]
    assert SE.propozycja_ratunku({"status": "zolty", "uwagi": uwaga})  # bez pola - napis (wynik dzisiejszego match)
    assert not SE.propozycja_ratunku({"status": "zolty", "uwagi": uwaga, "ratunek": False})  # pole ma pierwszenstwo
    assert SE.propozycja_ratunku({"status": "zolty", "uwagi": [], "ratunek": True})
    assert not SE.propozycja_ratunku({"status": "zielony", "uwagi": uwaga, "ratunek": True})
