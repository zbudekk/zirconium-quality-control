"""excel - reguly wyboru wiersza, log CSV, tryby "pytaj" i "cien" na sztucznym arkuszu (E3-A9).

Kryteria (plan etapu 3, 4.1 E3-A9 i T6): (1) 200 zapytan o znanej odpowiedzi na arkuszu 30 tys. wierszy A-I: 200 z 200
we wlasciwej klasie (jeden wiersz / juz odhaczone / wskaz wiersz z lista kandydatow), 0 zapisow w zlym wierszu;
(2) wyszukanie ponizej 50 ms na zapytanie; (3) log CSV ma pola reguly 6; (4) domyslnie "pytaj przed zapisem", tryb "cien"
nie zapisuje niczego; (5) zapis dotyka wylacznie koloru jednej komorki (atrapa arkusza: zadna inna komorka sie nie zmienia).
Arkusz: ``narzedzia/arkusz_syntetyczny.py`` (fikcyjne nazwy, budowany w tescie, prawda z budowy scenariusza).
Bez prawdziwego Excela i bez COM: warstwa ``excel_com`` sprawdzana na atrapie obiektow COM.
"""
from __future__ import annotations

import ast
import csv
import datetime as dt
import json
import statistics
import time
import unicodedata
from collections import Counter

import pytest

import arkusz_syntetyczny as AS
from conftest import STANOWISKO
from stanowisko import baza as B, excel as EX, excel_com as XC, nazwy as N, ustawienia as UST

TERAZ = dt.datetime(2026, 11, 18, 7, 30, 0)
ZIELONY = (198, 239, 206)
ZOLTY = (255, 235, 156)
KOL_B = 2
OSOBA = "Technik A"


def zegar() -> dt.datetime:
    return TERAZ


@pytest.fixture(scope="module")
def zestaw():
    return AS.zbuduj()


def _excel(arkusz, tmp_path, tryb: str = EX.TRYB_PYTAJ, baza=None) -> EX.Excel:
    ex = EX.Excel(EX.Konfiguracja(tryb=tryb, log=tmp_path / "log_excel.csv"), arkusz, baza=baza, zegar=zegar)
    ex.odswiez()
    return ex


def _log(tmp_path) -> list[dict]:
    with open(tmp_path / "log_excel.csv", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def _zapisy(arkusz) -> list[tuple]:
    return [op for op in arkusz.operacje if op[0] == "ustaw_wypelnienie"]


def _pierwsze(zestaw, pulapka: str) -> AS.Zapytanie:
    return next(q for q in zestaw.zapytania if q.pulapka == pulapka)


# --- kryterium 1: 200 zapytan, wlasciwa klasa, 0 zapisow w zlym wierszu ---------------------------------------------
def test_k1_200_zapytan_wlasciwa_klasa(zestaw, tmp_path):
    assert (AS.KLASA_JEDEN, AS.KLASA_JUZ, AS.KLASA_WSKAZ) == (EX.KLASA_JEDEN_WIERSZ, EX.KLASA_JUZ_ODHACZONE, EX.KLASA_WSKAZ_WIERSZ)
    assert len(zestaw.zapytania) == 200 and zestaw.arkusz.ostatni_wiersz == 30001
    ex = _excel(zestaw.arkusz, tmp_path)
    tabela: dict[str, list[int]] = {}
    regula = Counter()
    bledy = []
    for q in zestaw.zapytania:
        d = ex.dopasuj(q.kuweta, q.folder)
        if q.klasa in (EX.KLASA_JEDEN_WIERSZ, EX.KLASA_JUZ_ODHACZONE):
            ok = d.klasa == q.klasa and d.wiersz == q.wiersz
        else:  # wskaz wiersz: zadnego wyboru programu, wiersz tego zlecenia (gdy jest) na liscie kandydatow
            ok = d.klasa == q.klasa and d.wiersz is None and (q.prawdziwy is None or q.prawdziwy in d.kandydaci)
        nazwisko = q.folder.replace("_", " ").split()[0].lower()
        ok = ok and nazwisko not in d.powod.lower()  # powod bez nazwisk (trafia do okna i do logow programu)
        t = tabela.setdefault(q.pulapka, [0, 0])
        t[0] += ok
        t[1] += 1
        regula[(d.klasa, d.regula)] += 1
        if not ok:
            bledy.append((q.id, q.pulapka, q.klasa, q.wiersz, q.prawdziwy, d.klasa, d.wiersz, d.regula, d.kandydaci[:5]))
    print("\npulapka                      ok / razem")
    for p, (ok, razem) in tabela.items():
        print(f"  {p:28s} {ok:3d} / {razem}")
    print("klasa, regula:", dict(sorted(regula.items())))
    zgodne = sum(ok for ok, _ in tabela.values())
    print(f"RAZEM: {zgodne} z {len(zestaw.zapytania)}")
    assert not bledy, bledy
    assert zgodne == 200


def test_k1_zero_zapisow_w_zlym_wierszu(zestaw, tmp_path):
    """Caly przebieg w trybie "pytaj": jeden wiersz -> zatwierdzenie; juz odhaczone -> tylko log; wskaz wiersz -> czlowiek
    wybiera z listy kandydatow wiersz tego zlecenia (gdy jest), inaczej pomija. Zmieniaja sie dokladnie oczekiwane pola B."""
    ark = zestaw.arkusz.kopia()
    ex = _excel(ark, tmp_path)
    w0, k0 = ark.zrzut()
    oczekiwane, wyniki = set(), Counter()
    for q in zestaw.zapytania:
        poz = ex.pozycja(q.kuweta, q.folder)
        d = poz.dopasowanie
        if d.klasa == EX.KLASA_JEDEN_WIERSZ:
            wpis = ex.zatwierdz(poz, OSOBA)
            assert (wpis["wynik"], wpis["wiersz"]) == (EX.WYNIK_ZAPISANO, q.wiersz), q
            oczekiwane.add(q.wiersz)
        elif d.klasa == EX.KLASA_JUZ_ODHACZONE:
            wpis = ex.zatwierdz(poz, OSOBA)
            assert (wpis["wynik"], wpis["wiersz"]) == (EX.WYNIK_JUZ_ODHACZONE, q.wiersz), q
        elif q.pulapka == "pole_b_inny_kolor":  # program nie nadpisuje innego koloru nawet po wskazaniu
            with pytest.raises(EX.BladExcela, match="inne wypelnienie"):
                ex.zatwierdz(poz, OSOBA, wiersz=q.prawdziwy)
            wpis = ex.pomin(poz, OSOBA)
        elif q.prawdziwy is not None:
            assert q.prawdziwy in d.kandydaci
            wpis = ex.zatwierdz(poz, OSOBA, wiersz=q.prawdziwy)
            assert (wpis["wynik"], wpis["wiersz"]) == (EX.WYNIK_WSKAZANO, q.prawdziwy), q
            oczekiwane.add(q.prawdziwy)
        else:
            wpis = ex.pomin(poz, OSOBA)
        wyniki[wpis["wynik"]] += 1
    w1, k1 = ark.zrzut()
    zmienione = {kl for kl in set(k0) | set(k1) if k0.get(kl) != k1.get(kl)}
    zle = [op for op in _zapisy(ark) if op[1] not in oczekiwane or op[2] != KOL_B or op[3] != ZIELONY]
    print(f"\nwyniki: {dict(wyniki)}; zapisow {len(_zapisy(ark))}, w zlym wierszu {len(zle)}")
    assert w1 == w0  # zadna wartosc komorki sie nie zmienila
    assert zmienione == {(nr, KOL_B) for nr in oczekiwane} and all(k1[kl] == ZIELONY for kl in zmienione)
    assert zle == [] and len(_zapisy(ark)) == len(oczekiwane)
    assert sum(wyniki.values()) == 200 and len(_log(tmp_path)) == 200


# --- kryterium 2: wyszukanie ponizej 50 ms -------------------------------------------------------------------------
def test_k2_wyszukanie_ponizej_50_ms(zestaw, tmp_path):
    ex = EX.Excel(EX.Konfiguracja(log=tmp_path / "log_excel.csv"), zestaw.arkusz, zegar=zegar)
    t0 = time.perf_counter()
    ex.odswiez()
    budowa = time.perf_counter() - t0
    czasy = []
    for q in zestaw.zapytania:
        t = time.perf_counter()
        ex.dopasuj(q.kuweta, q.folder)
        czasy.append(time.perf_counter() - t)
    print(f"\nodczyt i indeks 30 tys. wierszy: {budowa * 1000:.0f} ms; zapytanie: mediana {statistics.median(czasy) * 1000:.3f} ms, "
          f"max {max(czasy) * 1000:.3f} ms ({len(czasy)} zapytan)")
    assert max(czasy) < 0.050
    assert budowa < 10.0  # odczyt "co kilka minut" (X2) - nie blokuje programu na dlugo


# --- kryterium 3: log CSV z polami reguly 6 --------------------------------------------------------------------------
def test_k3_log_csv_ma_pola_reguly_6(zestaw, tmp_path):
    assert EX.POLA_REGULY_6 == ("data", "godzina", "kuweta", "folder", "numer_zlecenia_b", "arkusz", "wiersz", "kto_zatwierdzil")
    ark = zestaw.arkusz.kopia()
    ex = _excel(ark, tmp_path)
    q1, q2, q3 = _pierwsze(zestaw, "prosty"), _pierwsze(zestaw, "pole_b_zielone"), _pierwsze(zestaw, "brak_kuwety_w_arkuszu")
    ex.zatwierdz(ex.pozycja(q1.kuweta, q1.folder), OSOBA)
    ex.zatwierdz(ex.pozycja(q2.kuweta, q2.folder), OSOBA)
    ex.pomin(ex.pozycja(q3.kuweta, q3.folder), OSOBA)
    with open(tmp_path / "log_excel.csv", encoding="utf-8-sig", newline="") as f:
        naglowek = next(csv.reader(f, delimiter=";"))
    assert tuple(naglowek[:8]) == EX.POLA_REGULY_6 and tuple(naglowek) == EX.POLA_LOGU
    w = _log(tmp_path)
    numer_b = ark.wartosc(q1.wiersz, KOL_B)
    assert w[0] == {"data": "2026-11-18", "godzina": "07:30:00", "kuweta": q1.kuweta, "folder": q1.folder,
                    "numer_zlecenia_b": EX.norm_numer(numer_b), "arkusz": "Zlecenia", "wiersz": str(q1.wiersz),
                    "kto_zatwierdzil": OSOBA, "regula": "2", "wynik": "zapisano", "tryb": "pytaj"}
    assert EX.norm_numer(numer_b) and "." not in w[0]["numer_zlecenia_b"]  # 40123.0 z COM -> "40123"
    assert (w[1]["wynik"], w[1]["regula"], w[1]["wiersz"]) == ("juz_odhaczone", "4", str(q2.wiersz))
    assert (w[2]["wynik"], w[2]["regula"], w[2]["wiersz"], w[2]["numer_zlecenia_b"]) == ("pominieto", "5", "", "")
    # nowy obiekt Excel dopisuje do tego samego pliku bez drugiego naglowka
    ex2 = _excel(ark, tmp_path)
    q4 = [q for q in zestaw.zapytania if q.pulapka == "prosty"][1]
    ex2.zatwierdz(ex2.pozycja(q4.kuweta, q4.folder), "Technik B")
    tekst = (tmp_path / "log_excel.csv").read_text(encoding="utf-8-sig")
    assert tekst.count("kto_zatwierdzil") == 1 and len(_log(tmp_path)) == 4 and _log(tmp_path)[3]["kto_zatwierdzil"] == "Technik B"


# --- kryterium 4: domyslnie "pytaj", "cien" nie zapisuje niczego ------------------------------------------------------
def test_k4_domyslnie_pytaj_przed_zapisem(zestaw, tmp_path):
    ust = UST.wczytaj_ustawienia(UST.PLIK_PRZYKLADU)
    konf = EX.Konfiguracja.z_ustawien(ust)
    assert konf.tryb == EX.TRYB_PYTAJ == EX.Konfiguracja().tryb == "pytaj" and konf.ostrzezenia == ()
    assert (konf.kolumna_daty, konf.kolumna_odhaczenia, konf.kolumna_kuwety, konf.kolumna_nazwy) == ("A", "B", "C", "H")
    assert konf.kolor == ZIELONY and konf.pierwszy_wiersz == 2 and konf.log == B.sciezka_z_ustawien(ust, "log_excel")
    assert EX.TRYBY == ("pytaj", "cien")  # etap 3 (DW10): bez zapisu samodzielnego
    with pytest.raises(EX.BladExcela, match="tryb"):
        EX.Konfiguracja(tryb="auto")
    ust["excel"]["tryb_pytaj_przed_zapisem"] = False  # DW10: false nie wlacza zapisu samodzielnego
    konf2 = EX.Konfiguracja.z_ustawien(ust)
    assert konf2.tryb == "pytaj" and any("DW10" in o for o in konf2.ostrzezenia)
    # propozycje bez zatwierdzenia nie zmieniaja arkusza i nie pisza logu
    ark = zestaw.arkusz.kopia()
    ex = _excel(ark, tmp_path)
    przed = ark.zrzut()
    pozycje = [ex.pozycja(q.kuweta, q.folder) for q in zestaw.zapytania]
    assert len(pozycje) == 200 and ark.zrzut() == przed and _zapisy(ark) == []
    assert not (tmp_path / "log_excel.csv").exists()


def test_k4_tryb_cien_nie_zapisuje_niczego(zestaw, tmp_path):
    ark = zestaw.arkusz.kopia()
    ex = _excel(ark, tmp_path, tryb=EX.TRYB_CIEN)
    przed = ark.zrzut()
    wyniki = Counter()
    for q in zestaw.zapytania:
        poz = ex.pozycja(q.kuweta, q.folder)
        if poz.dopasowanie.klasa != EX.KLASA_WSKAZ_WIERSZ:
            wyniki[ex.zatwierdz(poz, OSOBA)["wynik"]] += 1
        elif q.prawdziwy is not None and q.pulapka != "pole_b_inny_kolor":
            wyniki[ex.zatwierdz(poz, OSOBA, wiersz=q.prawdziwy)["wynik"]] += 1
        else:
            wyniki[ex.pomin(poz, OSOBA)["wynik"]] += 1
    assert ark.zrzut() == przed and _zapisy(ark) == []
    log = _log(tmp_path)
    assert len(log) == 200 and {w["tryb"] for w in log} == {"cien"}
    wskazane = sum(1 for q in zestaw.zapytania if q.klasa == W and q.prawdziwy is not None and q.pulapka != "pole_b_inny_kolor")
    assert wskazane == 34
    # w trybie "pytaj" te same zatwierdzenia daja 120 + 34 zapisow koloru (test_k1_zero_zapisow_w_zlym_wierszu); tu: 0
    assert wyniki == {EX.WYNIK_TYLKO_LOG: 120 + wskazane, EX.WYNIK_JUZ_ODHACZONE: 21, EX.WYNIK_POMINIETO: 200 - 141 - wskazane}
    print(f"\ntryb cien: {dict(wyniki)}; zapisow koloru: {len(_zapisy(ark))}")


def test_k4_zapisz_cien_loguje_caly_piec(zestaw, tmp_path):
    ark = zestaw.arkusz.kopia()
    ex = _excel(ark, tmp_path, tryb=EX.TRYB_CIEN)
    przed = ark.zrzut()
    pozycje = [ex.pozycja(q.kuweta, q.folder) for q in zestaw.zapytania[:40]]
    wpisy = ex.zapisz_cien(pozycje, OSOBA)
    assert len(wpisy) == 40 and ark.zrzut() == przed and _zapisy(ark) == []
    for poz, wpis in zip(pozycje, wpisy):
        oczekiwany = EX.WYNIK_JUZ_ODHACZONE if poz.dopasowanie.klasa == EX.KLASA_JUZ_ODHACZONE else EX.WYNIK_TYLKO_LOG
        assert (wpis["wynik"], wpis["tryb"], wpis["wiersz"]) == (oczekiwany, "cien", poz.dopasowanie.wiersz)
    with pytest.raises(EX.BladExcela, match="cien"):
        _excel(ark, tmp_path).zapisz_cien(pozycje, OSOBA)  # w trybie "pytaj" kazdy zapis zatwierdza czlowiek


# --- kryterium 5: zapis = kolor jednej komorki ------------------------------------------------------------------------
def test_k5_zapis_dotyka_tylko_koloru_jednej_komorki(zestaw, tmp_path):
    ark = zestaw.arkusz.kopia()
    ex = _excel(ark, tmp_path)
    q = _pierwsze(zestaw, "ta_sama_kuweta_inne_daty")
    poz = ex.pozycja(q.kuweta, q.folder)
    w0, k0 = ark.zrzut()
    ark.operacje.clear()
    wpis = ex.zatwierdz(poz, OSOBA)
    w1, k1 = ark.zrzut()
    assert wpis["wynik"] == "zapisano" and w1 == w0
    assert {kl for kl in set(k0) | set(k1) if k0.get(kl) != k1.get(kl)} == {(q.wiersz, KOL_B)} and k1[(q.wiersz, KOL_B)] == ZIELONY
    assert _zapisy(ark) == [("ustaw_wypelnienie", q.wiersz, KOL_B, ZIELONY)]
    assert {op[0] for op in ark.operacje} <= {"wiersz", "wypelnienie", "ustaw_wypelnienie"}  # poza zapisem tylko odczyty


# --- bezpieczenstwo zapisu -------------------------------------------------------------------------------------------
def test_arkusz_zmieniony_po_propozycji_odmowa_bez_zapisu(zestaw, tmp_path):
    ark = zestaw.arkusz.kopia()
    ex = _excel(ark, tmp_path)
    q = _pierwsze(zestaw, "prosty")
    poz = ex.pozycja(q.kuweta, q.folder)
    ark.wstaw_wiersz(q.wiersz - 3, [dt.datetime(2026, 11, 17), 99999.0, 7.0, "", "", 1, "", "Abakowski 7 zs", ""])  # wspoledycja
    przed = ark.zrzut()
    with pytest.raises(EX.BladExcela, match="zmienil"):
        ex.zatwierdz(poz, OSOBA)
    assert ark.zrzut() == przed and _zapisy(ark) == []
    assert _log(tmp_path)[-1]["wynik"] == "blad"
    ex.odswiez()
    poz2 = ex.pozycja(q.kuweta, q.folder)
    assert poz2.dopasowanie.wiersz == q.wiersz + 1
    assert ex.zatwierdz(poz2, OSOBA)["wiersz"] == q.wiersz + 1 and ark.wartosc(q.wiersz + 1, 8) == q.folder


def test_pole_b_zazielenione_w_miedzyczasie_tylko_log(zestaw, tmp_path):
    ark = zestaw.arkusz.kopia()
    ex = _excel(ark, tmp_path)
    q = _pierwsze(zestaw, "prosty")
    poz = ex.pozycja(q.kuweta, q.folder)
    ark.zaznacz(q.wiersz, KOL_B, ZIELONY)  # ktos odhaczyl recznie
    wpis = ex.zatwierdz(poz, OSOBA)
    assert (wpis["wynik"], wpis["regula"]) == (EX.WYNIK_JUZ_ODHACZONE, 4) and _zapisy(ark) == []


def test_wskaz_wiersz_tylko_z_listy_kandydatow(zestaw, tmp_path):
    ark = zestaw.arkusz.kopia()
    ex = _excel(ark, tmp_path)
    q = _pierwsze(zestaw, "inicjaly_zamiast_nazwiska")
    poz = ex.pozycja(q.kuweta, q.folder)
    assert poz.dopasowanie.klasa == EX.KLASA_WSKAZ_WIERSZ and q.prawdziwy in poz.dopasowanie.kandydaci
    okno = poz.kandydaci_do_okna
    assert [k["wiersz"] for k in okno] == list(poz.dopasowanie.kandydaci)
    assert {"wiersz", "data", "numer_b", "kuweta", "nazwa", "wartosci", "wypelnienie_b"} <= set(okno[0])
    with pytest.raises(EX.BladExcela, match="wskaz"):
        ex.zatwierdz(poz, OSOBA)
    spoza = next(nr for nr in range(2, 100) if nr not in poz.dopasowanie.kandydaci)
    with pytest.raises(EX.BladExcela, match="kandydat"):
        ex.zatwierdz(poz, OSOBA, wiersz=spoza)
    assert _zapisy(ark) == []
    wpis = ex.zatwierdz(poz, OSOBA, wiersz=q.prawdziwy)
    assert (wpis["wynik"], wpis["regula"], wpis["wiersz"]) == (EX.WYNIK_WSKAZANO, 5, q.prawdziwy)
    assert _zapisy(ark) == [("ustaw_wypelnienie", q.prawdziwy, KOL_B, ZIELONY)]


def test_operator_wymagany_i_podwojne_zatwierdzenie(zestaw, tmp_path):
    ark = zestaw.arkusz.kopia()
    ex = _excel(ark, tmp_path)
    q = _pierwsze(zestaw, "prosty")
    poz = ex.pozycja(q.kuweta, q.folder)
    for zly in ("", "   ", None):
        with pytest.raises(EX.BladExcela, match="kto zatwierdza"):
            ex.zatwierdz(poz, zly)
    ex.zatwierdz(poz, OSOBA)
    with pytest.raises(EX.BladExcela, match="juz zalatwiona"):
        ex.zatwierdz(poz, OSOBA)
    with pytest.raises(EX.BladExcela, match="juz zalatwiona"):
        ex.pomin(poz, OSOBA)
    assert len(_zapisy(ark)) == 1 and len(_log(tmp_path)) == 1


def test_odswiezanie_odczytu_co_kilka_minut(tmp_path):
    chwila = [TERAZ]
    ark = _maly([(_d("2026-11-16"), 51001.0, 3263.0, "Testowski 3263 zs")])
    ex = EX.Excel(EX.Konfiguracja(odswiez_co_min=5, log=tmp_path / "log.csv"), ark, zegar=lambda: chwila[0])
    ex.dopasuj("3263", "Testowski 3263 zs")
    ex.indeks()
    chwila[0] += dt.timedelta(minutes=4)
    ex.dopasuj("3263", "Testowski 3263 zs")
    assert sum(1 for op in ark.operacje if op[0] == "odczytaj") == 1
    chwila[0] += dt.timedelta(minutes=2)
    ex.dopasuj("3263", "Testowski 3263 zs")
    assert sum(1 for op in ark.operacje if op[0] == "odczytaj") == 2
    assert ark.operacje[0] == ("odczytaj", 2, 9)  # kolumny A-I od pierwszego wiersza danych


def test_excel_niedostepny_komunikat_bez_awarii(tmp_path):
    def brak():
        raise XC.BladCom("Excel nie jest uruchomiony")

    ex = EX.Excel(EX.Konfiguracja(log=tmp_path / "log.csv"), brak, zegar=zegar)
    with pytest.raises(EX.BladExcela, match="Excel niedostepny"):
        ex.odswiez()
    ark = _maly([(_d("2026-11-16"), 51001.0, 3263.0, "Testowski 3263 zs")])
    ex2 = EX.Excel(EX.Konfiguracja(log=tmp_path / "log.csv"), lambda: ark, zegar=zegar)  # polaczenie leniwe (fabryka)
    assert ex2.dopasuj("3263", "Testowski 3263 zs").wiersz == 2


# --- reguly 1-5 na malym arkuszu (czytelna specyfikacja) --------------------------------------------------------------
def _d(s: str) -> dt.datetime:
    return dt.datetime.fromisoformat(s)


def _maly(wiersze, kolory=()):
    """Maly arkusz: wiersze (A, B, C, H) od wiersza 2; ``kolory``: (nr wiersza, rgb) pola B."""
    ark = AS.ArkuszWPamieci("Test", [[a, b, c, "Gabinet 01", "korona", 1, "A2", h, ""] for a, b, c, h in wiersze])
    for nr, rgb in kolory:
        ark.zaznacz(nr, KOL_B, rgb)
    return ark


T = "Testowski 3263 zs"
J, Z, W = EX.KLASA_JEDEN_WIERSZ, EX.KLASA_JUZ_ODHACZONE, EX.KLASA_WSKAZ_WIERSZ
D1, D2, D3 = _d("2026-10-01"), _d("2026-11-10"), _d("2026-11-16")
PRZYPADKI = [
    # opis, wiersze (A, B, C, H), kolory B, kuweta, folder, klasa, wiersz, regula, kandydaci (None = nie sprawdzaj)
    ("r1 dokladnie, nie fragment", [(D3, 1.0, "13263", T), (D2, 2.0, 3263.0, T), (D3, 3.0, "3263/2", T)], (), "3263", T, J, 3, 2, (3,)),
    ("r2 nazwa rozstrzyga miedzy osobami", [(D3, 1.0, 3263.0, "Probny 3263 kor"), (D1, 2.0, 3263.0, T)], (), "3263", T, J, 3, 2, None),
    ("r2 normalizacja H", [(D3, 1.0, 3263.0, "  TESTOWSKI   3263 ZS ")], (), "3263", T, J, 2, 2, None),
    ("r3 inicjal imienia, najnowszy", [(D1, 1.0, 3263.0, "Probny 3263 kor"), (D3, 2.0, 3263.0, "Testowski J. 3263")], (), "3263", T, J, 3, 3, None),
    ("r3 puste H, najnowszy", [(D1, 1.0, 3263.0, "Probny 3263 kor"), (D3, 2.0, 3263.0, "")], (), "3263", T, J, 3, 3, None),
    ("r3 najnowszy innej osoby", [(D3, 1.0, 3263.0, "Probny 3263 kor"), (D1, 2.0, 3263.0, None)], (), "3263", T, W, None, 5, (2, 3)),
    ("r3 inicjaly zamiast nazwiska", [(D3, 1.0, 3263.0, "T.J. 3263 zs")], (), "3263", T, W, None, 5, (2,)),
    ("r3 dwa najnowsze z ta sama data", [(D3, 1.0, 3263.0, ""), (D3, 2.0, 3263.0, "")], (), "3263", T, W, None, 5, None),
    ("r3 wiersz bez daty pod najnowszym", [(D3, 1.0, 3263.0, ""), (None, 2.0, 3263.0, "")], (), "3263", T, W, None, 5, None),
    ("r3 wiersz bez daty nad najnowszym", [(None, 1.0, 3263.0, "Probny 3263 kor"), (D3, 2.0, 3263.0, "")], (), "3263", T, J, 3, 3, None),
    ("r3 data tekstem i numer seryjny", [(AS.data_seryjna(dt.date(2026, 11, 10)), 1.0, 3263.0, ""), ("16.11.2026", 2.0, 3263.0, "")], (),
     "3263", T, J, 3, 3, None),
    ("r4 pole B juz zielone", [(D3, 1.0, 3263.0, T)], ((2, ZIELONY),), "3263", T, Z, 2, 4, None),
    ("r4 reklamacja: stary zielony, nowy otwarty", [(D1, 1.0, 3263.0, T), (D3, 2.0, 3263.0, T)], ((2, ZIELONY),), "3263", T, J, 3, 3, None),
    ("r4 reklamacja: oba zielone", [(D1, 1.0, 3263.0, T), (D3, 2.0, 3263.0, T)], ((2, ZIELONY), (3, ZIELONY)), "3263", T, Z, 3, 4, None),
    ("r4 bialy = bez wypelnienia", [(D3, 1.0, 3263.0, T)], ((2, (255, 255, 255)),), "3263", T, J, 2, 2, None),
    ("r5 inne wypelnienie B", [(D3, 1.0, 3263.0, T)], ((2, ZOLTY),), "3263", T, W, None, 5, (2,)),
    ("r5 dwa otwarte z ta sama nazwa", [(D1, 1.0, 3263.0, T), (D3, 2.0, 3263.0, T)], (), "3263", T, W, None, 5, (3, 2)),
    ("r5 starszy otwarty, najnowszy zielony", [(D1, 1.0, 3263.0, T), (D3, 2.0, 3263.0, T)], ((3, ZIELONY),), "3263", T, W, None, 5, None),
    ("r5 brak kuwety w C", [(D3, 1.0, 4444.0, T)], (), "3263", T, W, None, 5, ()),
    ("r5 brak numeru kuwety", [(D3, 1.0, 3263.0, T)], (), None, "Testowski zs", W, None, 5, ()),
    ("r5 kuweta niejednoznaczna", [(D3, 1.0, 3263.0, "Testowski 46 3263")], (), "?46,3263", "Testowski 46 3263", W, None, 5, (2,)),
    ("zera wiodace i spacje w C", [(D3, 1.0, " 0412 ", "Testowski 412")], (), "412", "Testowski 0412", J, 2, 2, None),
    ("prywatne: numer w B", [(D3, 1234.0, None, "Testowski")], (), "#1234", "#1234", J, 2, 2, None),
    ("prywatne: numer w H", [(D3, 40001.0, None, "Testowski #1234")], (), "#1234", "#1234 Testowski", J, 2, 2, None),
    ("prywatne: dwa wiersze", [(D2, 1234.0, None, "Probny"), (D3, 40001.0, None, "Testowski #1234")], (), "#1234", "#1234", W, None, 5, None),
    ("prywatne: zielone", [(D3, "1234", None, "Testowski")], ((2, ZIELONY),), "#1234", "#1234", Z, 2, 4, None),
    ("prywatne: brak", [(D3, 1235.0, None, "Testowski")], (), "#1234", "#1234", W, None, 5, ()),
]


@pytest.mark.parametrize("opis, wiersze, kolory, kuweta, folder, klasa, wiersz, regula, kandydaci", PRZYPADKI, ids=[p[0] for p in PRZYPADKI])
def test_reguly_1_5_na_malym_arkuszu(tmp_path, opis, wiersze, kolory, kuweta, folder, klasa, wiersz, regula, kandydaci):
    ex = _excel(_maly(wiersze, kolory), tmp_path)
    d = ex.dopasuj(kuweta, folder)
    assert (d.klasa, d.wiersz, d.regula) == (klasa, wiersz, regula), d
    if kandydaci is not None:
        assert d.kandydaci == kandydaci, d
    assert "testowski" not in d.powod.lower() and "probny" not in d.powod.lower()


# --- normalizacja ----------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("v, oczekiwane", [
    (3263.0, "3263"), (3263, "3263"), ("3263", "3263"), (" 3263 ", "3263"), ("03263", "3263"), ("0412", "412"), ("3263\u00a0", "3263"),
    (None, None), ("", None), ("  ", None), ("13263", "13263"), ("3263/2", "3263/2"), ("3263a", "3263a"), (3263.5, "3263.5"), ("#1234", "#1234"),
])
def test_norm_kuweta(v, oczekiwane):
    assert EX.norm_kuweta(v) == oczekiwane


@pytest.mark.parametrize("v, oczekiwane", [
    (dt.datetime(2026, 11, 16, 0, 0), dt.date(2026, 11, 16)), (dt.date(2026, 11, 16), dt.date(2026, 11, 16)),
    ("16.11.2026", dt.date(2026, 11, 16)), ("2026-11-16", dt.date(2026, 11, 16)), ("16.11.26", dt.date(2026, 11, 16)),
    ("16-11-2026", dt.date(2026, 11, 16)), ("16/11/2026", dt.date(2026, 11, 16)), (" 16.11.2026 ", dt.date(2026, 11, 16)),
    (AS.data_seryjna(dt.date(2026, 11, 16)), dt.date(2026, 11, 16)), (int(AS.data_seryjna(dt.date(2026, 11, 16))), dt.date(2026, 11, 16)),
    (None, None), ("", None), ("abc", None), (5.0, None), ("31.02.2026", None), (True, None),
])
def test_data_z_komorki(v, oczekiwane):
    assert EX.data_z_komorki(v) == oczekiwane


@pytest.mark.parametrize("v, oczekiwane", [(40123.0, "40123"), (40123, "40123"), (" 40123 ", "40123"), (None, ""), ("Z-12/2026", "Z-12/2026"), (12.5, "12.5")])
def test_norm_numer(v, oczekiwane):
    assert EX.norm_numer(v) == oczekiwane


@pytest.mark.parametrize("folder, kuweta, oczekiwane", [
    ("Testowski 3263 zs", "3263", ("testowski",)),
    ("Testowski 1784PG", "1784", ("testowski",)),
    ("Testowski J. 3263 zs", "3263", ("testowski",)),
    ("Testowski J.3263", "3263", ("testowski",)),
    ("Testowski 0412", "412", ("testowski",)),
    ("3263 Testowski Jan", "3263", ("testowski",)),
    ("Testowski_88_zs", "88", ("testowski",)),
    ("Testowski 512 Anna", "512", ("testowski",)),
    ("Nowak-Testowa 3263 zs", "3263", ("nowak", "testowa")),
    (unicodedata.normalize("NFD", "\u017b\u00f3\u0142tkowska 3263 ZS1"), "3263", ("\u017c\u00f3\u0142tkowska",)),
    ("#1234 Testowski", "#1234", ("testowski",)),
    ("J.K. 3263", "3263", ()),
])
def test_nazwisko_z_folderu(folder, kuweta, oczekiwane):
    assert EX.nazwisko_z_folderu(folder, kuweta) == oczekiwane


# --- propozycje z wyniku "Zamknij piec" (session_rano) i zapis w excel_zapisy ----------------------------------------
def test_propozycje_z_wyniku_pieca_i_tabela_excel_zapisy(tmp_path):
    baza = B.otworz(tmp_path / "stanowisko.sqlite", zegar=zegar)
    zl = {}
    for folder, kuweta in (("Testowski 3263 zs", "3263"), ("Probna 412 kor", "412"), ("Atrapowicz 77 zs", "77")):
        zl[kuweta] = baza.wstaw("zlecenia", zrodlo="cyrkon", folder=folder, folder_norm=N.znormalizuj(folder), kuweta=kuweta)
    piec = baza.wstaw("sesje_pieca", data="2026-11-18", nr_w_dniu=1, otwarto="2026-11-18T06:40:00", zamknieto="2026-11-18T07:25:00", zamknal=OSOBA)
    ark = _maly([(D2, 51001.0, 3263.0, "Testowski 3263 zs"), (D3, 51002.0, "0412", "Probna 0412 kor")], kolory=((3, ZIELONY),))
    wynik = {"sesja_pieca_id": piec, "zamknieto": "2026-11-18T07:25:00", "zamknal": OSOBA,
             "kompletne": [{"zlecenie_id": zl[k], "kuweta": k, "zrodlo": "cyrkon", "punktow": 2, "rozpoznane": 2, "kompletne": True, "brakujace": []}
                           for k in ("3263", "412", "77")],
             "braki": [], "poprawki": [{"praca_id": 9, "skan_id": 3, "numer_plytki": 2, "gniazdo": 5, "projekt_id": 4, "sha16": "ab" * 8,
                                        "zlecenie_id": zl["3263"], "kuweta": "3263", "zeby": "46", "zlecenie_odhaczone": True}]}
    ex = _excel(ark, tmp_path, baza=baza)
    pozycje = ex.propozycje(wynik)
    assert [(p.zlecenie_id, p.sesja_pieca_id, p.kuweta, p.dopasowanie.klasa, p.dopasowanie.wiersz) for p in pozycje] == [
        (zl["3263"], piec, "3263", J, 2), (zl["412"], piec, "412", Z, 3), (zl["77"], piec, "77", W, None)]
    assert pozycje[0].folder == "Testowski 3263 zs"  # nazwa folderu z tabeli zlecenia (DW2) - tylko do logu i excel_zapisy
    ex.zatwierdz(pozycje[0], OSOBA)
    ex.zatwierdz(pozycje[1], OSOBA)
    ex.pomin(pozycje[2], OSOBA)
    assert [w["wynik"] for w in ex.zaloguj_poprawki(wynik, OSOBA)] == ["tylko_log"]
    assert _zapisy(ark) == [("ustaw_wypelnienie", 2, KOL_B, ZIELONY)]
    zapisy = baza.wiersze("SELECT * FROM excel_zapisy ORDER BY id")
    # poprawka zlecenia juz odhaczonego: tylko log (SE5); wiersz zlecenia jest juz zielony (zapis wyzej) - regula 4
    assert [(w["wynik"], w["regula"], w["wiersz"]) for w in zapisy] == [("zapisano", 2, 2), ("juz_odhaczone", 4, 3), ("pominieto", 5, None),
                                                                        ("tylko_log", 4, 2)]
    assert {k: zapisy[0][k] for k in ("czas", "sesja_pieca_id", "zlecenie_id", "kuweta", "folder", "numer_zlecenia_b", "arkusz", "tryb", "operator")} == {
        "czas": "2026-11-18T07:30:00", "sesja_pieca_id": piec, "zlecenie_id": zl["3263"], "kuweta": "3263", "folder": "Testowski 3263 zs",
        "numer_zlecenia_b": "51001", "arkusz": "Test", "tryb": "pytaj", "operator": OSOBA}
    assert len(_log(tmp_path)) == 4  # kazdy wiersz excel_zapisy idzie tez do log_excel.csv (plan 3.4)
    # DW2: nazwa folderu tylko w zlecenia i excel_zapisy
    zrzut = baza.zrzut()
    for tabela, wiersze in zrzut.items():
        if tabela not in ("zlecenia", "excel_zapisy"):
            assert "Testowski" not in json.dumps(wiersze, ensure_ascii=False), tabela
    # zapis tylko po "Zamknij piec" (X4)
    with pytest.raises(EX.BladExcela, match="Zamknij piec"):
        ex.propozycje({**wynik, "zamknieto": None})
    with pytest.raises(EX.BladExcela, match="zlecenia"):
        ex.propozycje({**wynik, "kompletne": [{"zlecenie_id": 999, "kuweta": "1"}]})
    baza.zamknij()


# --- warstwa COM (bez Excela: atrapa obiektow COM) -------------------------------------------------------------------
class _Interior:
    def __init__(self, komorka):
        object.__setattr__(self, "_k", komorka)

    def __getattr__(self, nazwa):
        kolor = self._k.arkusz.kolory.get((self._k.row, self._k.column))
        if nazwa == "ColorIndex":
            return XC.XL_BRAK_WYPELNIENIA if kolor is None else 35
        if nazwa == "Color":
            return 16777215 if kolor is None else kolor
        raise AttributeError(nazwa)

    def __setattr__(self, nazwa, wartosc):
        self._k.arkusz.ustawienia.append((self._k.row, self._k.column, nazwa, wartosc))
        if nazwa == "Color":
            self._k.arkusz.kolory[(self._k.row, self._k.column)] = wartosc


class _Komorka:
    def __init__(self, arkusz, row, column):
        self.arkusz, self.row, self.column = arkusz, row, column
        self.Interior = _Interior(self)


class _Zakres:
    def __init__(self, arkusz, a, b):
        self.arkusz, self.a, self.b = arkusz, a, b

    @property
    def Value(self):
        w = tuple(tuple(self.arkusz.dane[r - 1][c - 1] if r - 1 < len(self.arkusz.dane) and c - 1 < len(self.arkusz.dane[r - 1]) else None
                        for c in range(self.a.column, self.b.column + 1)) for r in range(self.a.row, self.b.row + 1))
        return w[0][0] if len(w) == 1 and len(w[0]) == 1 else w


class _Wiersze:
    def __init__(self, n):
        self.Count = n


class _UzytyZakres:
    def __init__(self, arkusz):
        self.Row = 1
        self.Rows = _Wiersze(len(arkusz.dane))


class _ArkuszCom:
    def __init__(self, nazwa, dane):
        self.Name, self.dane, self.kolory, self.ustawienia = nazwa, dane, {}, []

    @property
    def UsedRange(self):
        return _UzytyZakres(self)

    def Cells(self, r, c):
        return _Komorka(self, r, c)

    def Range(self, a, b):
        return _Zakres(self, a, b)


class _Zakazane:
    def __init__(self, dziennik, nazwa):
        self.dziennik, self.nazwa = dziennik, nazwa

    def __call__(self, *a, **k):
        self.dziennik.append(self.nazwa)
        raise AssertionError(f"wywolano zakazane {self.nazwa}")


class _Skoroszyt:
    def __init__(self, nazwa, arkusze, dziennik):
        self.Name, self._arkusze = nazwa, {a.Name: a for a in arkusze}
        self.ActiveSheet = arkusze[0]
        for zakazane in ("Save", "SaveAs", "SaveCopyAs", "Close"):
            setattr(self, zakazane, _Zakazane(dziennik, zakazane))

    def Worksheets(self, nazwa):
        return self._arkusze[nazwa]


class _Skoroszyty(list):
    def __init__(self, elementy, dziennik):
        super().__init__(elementy)
        self.Open = _Zakazane(dziennik, "Open")
        self.Add = _Zakazane(dziennik, "Add")


class _Aplikacja:
    def __init__(self, skoroszyty):
        self.dziennik: list[str] = []
        self.Workbooks = _Skoroszyty(skoroszyty(self.dziennik), self.dziennik)
        self.ActiveWorkbook = self.Workbooks[0]
        self.Quit = _Zakazane(self.dziennik, "Quit")


def _aplikacja():
    dane = [list(AS.NAGLOWEK), [D2, 51001.0, 3263.0, "Gab", "korona", 1, "A2", "Testowski 3263 zs", ""],
            [D3, 51002.0, 412.0, "Gab", "most", 2, "A3", "Probna 412 kor", ""]]
    return _Aplikacja(lambda dz: [_Skoroszyt("Inny.xlsx", [_ArkuszCom("Arkusz1", [["x"]])], dz),
                                  _Skoroszyt("Zlecenia 2026.xlsx", [_ArkuszCom("Archiwum", [["y"]]), _ArkuszCom("2026", dane)], dz)])


def test_excel_com_atrapa_interfejsu_odczyt_i_kolor():
    app = _aplikacja()
    ark = XC.polacz("zlecenia", "2026", aplikacja=app)
    assert (ark.nazwa, ark.skoroszyt) == ("2026", "Zlecenia 2026.xlsx")
    assert ark.odczytaj(2, 9) == [tuple(r) for r in app.Workbooks[1].Worksheets("2026").dane[1:]]
    assert ark.wiersz(3, 9)[7] == "Probna 412 kor" and ark.wiersz(2, 3) == (D2, 51001.0, 3263.0)
    com = app.Workbooks[1].Worksheets("2026")
    assert ark.wypelnienie(2, 2) is None
    com.kolory[(3, 2)] = 206 * 65536 + 239 * 256 + 198  # COM: kolor = R + 256 G + 65536 B
    assert ark.wypelnienie(3, 2) == ZIELONY
    ark.ustaw_wypelnienie(2, 2, ZIELONY)
    assert com.ustawienia == [(2, 2, "Color", 198 + 239 * 256 + 206 * 65536)]  # jedna komorka, jedna wlasciwosc
    assert ark.wypelnienie(2, 2) == ZIELONY
    assert app.dziennik == []  # bez Open, Add, Save, SaveAs, SaveCopyAs, Close, Quit (X1)
    # domyslnie: aktywny skoroszyt i aktywny arkusz
    assert XC.polacz(aplikacja=app).nazwa == "Arkusz1"
    with pytest.raises(XC.BladCom, match="skoroszyt"):
        XC.polacz("nie ma takiego", aplikacja=app)
    with pytest.raises(XC.BladCom, match="arkusz"):
        XC.polacz("zlecenia", "1999", aplikacja=app)


def test_excel_com_pelny_przebieg_zmienia_tylko_kolor_jednej_komorki(tmp_path):
    app = _aplikacja()
    ex = EX.Excel(EX.Konfiguracja(log=tmp_path / "log_excel.csv"), lambda: XC.polacz("zlecenia", "2026", aplikacja=app), zegar=zegar)
    com = app.Workbooks[1].Worksheets("2026")
    dane_przed = [list(r) for r in com.dane]
    poz = ex.pozycja("3263", "Testowski 3263 zs")
    wpis = ex.zatwierdz(poz, OSOBA)
    assert (wpis["wynik"], wpis["wiersz"], wpis["arkusz"]) == ("zapisano", 2, "2026")
    assert com.ustawienia == [(2, 2, "Color", 198 + 239 * 256 + 206 * 65536)] and com.dane == dane_przed and app.dziennik == []


def test_excel_com_bez_pywin32_czytelny_blad(monkeypatch):
    def brak():
        raise ImportError("No module named 'win32com'")

    monkeypatch.setattr(XC, "_win32com_client", brak)
    with pytest.raises(XC.BladCom, match="pywin32"):
        XC.polacz()


def test_kolor_com_w_obie_strony():
    assert XC.rgb_na_kolor(ZIELONY) == 13561798 and XC.kolor_na_rgb(13561798) == ZIELONY
    assert XC.kolor_na_rgb(XC.rgb_na_kolor((1, 2, 3))) == (1, 2, 3)


# --- zaleznosci, dane osobowe, arkusz syntetyczny --------------------------------------------------------------------
STDLIB = {"__future__", "csv", "dataclasses", "datetime", "pathlib", "re", "typing", "unicodedata", "time", "math", "collections",
          "itertools", "functools", "contextlib", "enum", "bisect", "os"}


def _importy(plik) -> tuple[set[str], set[str]]:
    """(importy na poziomie modulu, importy wewnatrz funkcji) - nazwy pierwszego czlonu; import wzgledny = ".nazwa"."""
    drzewo = ast.parse(plik.read_text(encoding="utf-8"))
    gora, srodek = set(), set()
    for wezel in ast.walk(drzewo):
        if isinstance(wezel, (ast.Import, ast.ImportFrom)):
            if isinstance(wezel, ast.Import):
                nazwy = {a.name.split(".")[0] for a in wezel.names}
            else:
                nazwy = {("." * wezel.level) + (wezel.module or "").split(".")[0]}
            (gora if wezel in drzewo.body else srodek).update(nazwy)
    return gora, srodek


def test_tylko_biblioteka_standardowa_i_com_leniwie():
    gora, srodek = _importy(STANOWISKO / "stanowisko" / "excel.py")
    wzgledne = {n for n in gora | srodek if n.startswith(".")}
    assert (gora | srodek) - wzgledne <= STDLIB, (gora | srodek) - wzgledne - STDLIB
    assert wzgledne <= {".", ".baza", ".nazwy", ".excel_com"}, wzgledne  # bez session, ui, aplikacja (podpiecie robi A12)
    gora, srodek = _importy(STANOWISKO / "stanowisko" / "excel_com.py")
    assert gora <= STDLIB, gora - STDLIB  # pywin32 tylko w funkcji (modul importuje sie bez Excela)
    assert "win32com" in srodek
    gora, srodek = _importy(STANOWISKO / "narzedzia" / "arkusz_syntetyczny.py")
    assert gora | srodek <= STDLIB | {"argparse", "copy", "random"}


def test_arkusz_syntetyczny_pulapki_i_fikcyjne_nazwy(zestaw):
    ark = zestaw.arkusz
    wiersze = ark.odczytaj(2, 9)
    assert len(wiersze) == 30000 and {len(w) for w in wiersze} == {9}
    assert Counter(q.pulapka for q in zestaw.zapytania) == {p: n for p, (n, _) in AS.PULAPKI.items()}
    assert Counter(q.klasa for q in zestaw.zapytania) == {J: 120, Z: 21, W: 59}
    assert all(N.kuweta(q.folder) == q.kuweta for q in zestaw.zapytania)  # kuweta jak z indeksu (A4)
    c = [w[2] for w in wiersze]
    h = [w[7] for w in wiersze]
    assert sum(1 for v in c if isinstance(v, str) and v.startswith("0")) > 50  # zera wiodace
    assert sum(1 for v in h if not v) > 500 and sum(1 for v in h if isinstance(v, str) and v[1:2] == ".") > 200  # puste H, inicjaly
    assert sum(1 for w in wiersze if w[8] == "reklamacja") > 10 and zestaw.liczniki["zielonych_b"] > 25000
    po_kuwecie = Counter(EX.norm_kuweta(v) for v in c)
    assert all(po_kuwecie[q.kuweta] >= 3 for q in zestaw.zapytania if q.pulapka == "ta_sama_kuweta_inne_daty")
    assert sum(1 for q in zestaw.zapytania if q.kuweta and q.kuweta[0].isdigit() and po_kuwecie[q.kuweta] >= 2) > 100  # kuweta w roznych datach
    tekst = " ".join(str(v) for w in wiersze for v in (w[7], w[3])).lower() + " ".join(q.folder for q in zestaw.zapytania).lower()
    for prawdziwe in ("kowalsk", "nowak", "wisniewsk", "wojcik", "kowalczyk", "kaminsk", "lewandowsk", "zielinsk", "szymansk", "wozniak"):
        assert prawdziwe not in tekst
    druga = AS.zbuduj()
    assert druga.arkusz.zrzut() == ark.zrzut() and [vars(q) for q in druga.zapytania] == [vars(q) for q in zestaw.zapytania]
