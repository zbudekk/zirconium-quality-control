"""excel - reguly wyboru wiersza, log CSV, tryby "pytaj" i "cien" na sztucznym arkuszu (E3-A9, runda 2 po recenzji PR #27).

Kryteria (plan etapu 3, 4.1 E3-A9 i T6): (1) 200 zapytan o znanej odpowiedzi na arkuszu 30 tys. wierszy A-I: 200 z 200
we wlasciwej klasie (jeden wiersz / juz odhaczone / wskaz wiersz z lista kandydatow), 0 zapisow w zlym wierszu;
(2) wyszukanie ponizej 50 ms na zapytanie; (3) log CSV ma pola reguly 6; (4) domyslnie "pytaj przed zapisem", tryb "cien"
nie zapisuje niczego; (5) zapis dotyka wylacznie koloru jednej komorki (atrapa arkusza: zadna inna komorka sie nie zmienia).
Runda 2 (raport recenzenta PR #27 runda 1): B1 ponowienie zapisu = caly krok z kontrola, kontrola po zapisie; P1 swiezy
odczyt przy propozycji i zatwierdzeniu; P2 ten sam skoroszyt i arkusz; P3 limit wieku i nowszy otwarty wiersz; P4 wyniki bez
nazwy folderu; P5 blad logu CSV po zapisie; P6 pulapki P1 i P3 w arkuszu, bledy COM; D1, D2, D3, D5, D8.
Arkusz: ``narzedzia/arkusz_syntetyczny.py`` (fikcyjne nazwy, budowany w tescie, prawda z budowy scenariusza).
Bez prawdziwego Excela i bez COM: warstwa ``excel_com`` sprawdzana na atrapie obiektow COM.
"""
from __future__ import annotations

import ast
import csv
import datetime as dt
import json
import re
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
SESJA = 1  # sesja pieca (X4: zapis tylko dla pozycji z zamknietego pieca; bez bazy - podana wprost)


def zegar() -> dt.datetime:
    return TERAZ


def bez_czekania(_s: float) -> None:
    return None


@pytest.fixture(scope="module")
def zestaw():
    return AS.zbuduj()


def _excel(arkusz, tmp_path, tryb: str = EX.TRYB_PYTAJ, baza=None, **konf) -> EX.Excel:
    ex = EX.Excel(EX.Konfiguracja(tryb=tryb, log=tmp_path / "log_excel.csv", **konf), arkusz, baza=baza, zegar=zegar, czekaj=bez_czekania)
    ex.odswiez()
    return ex


def _kopia(zestaw) -> AS.ArkuszWPamieci:
    """Kopia arkusza z wierszami dopisanymi po odczycie juz na miejscu (stan, ktory opisuje prawda zapytan)."""
    ark = zestaw.arkusz.kopia()
    zestaw.dopisz(ark)
    return ark


def _log(tmp_path) -> list[dict]:
    with open(tmp_path / "log_excel.csv", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def _zapisy(arkusz) -> list[tuple]:
    return [op for op in arkusz.operacje if op[0] == "ustaw_wypelnienie"]


def _pierwsze(zestaw, pulapka: str) -> AS.Zapytanie:
    return next(q for q in zestaw.zapytania if q.pulapka == pulapka)


def _poz(ex, q, **kw) -> EX.Pozycja:
    return ex.pozycja(q.kuweta, q.folder, sesja_pieca_id=SESJA, **kw)


def _bez_nazw(wpis: dict, folder: str) -> None:
    """P4: wynik dla A12 ma tylko pola ``POLA_WYNIKU`` i nie niesie nazwy folderu (nazwiska)."""
    assert set(wpis) == set(EX.POLA_WYNIKU), wpis
    tekst = json.dumps(wpis, ensure_ascii=False).lower()
    slowa = [s.lower() for s in re.findall(r"[^\W\d_]{2,}", folder)]  # slowa nazwy folderu ("#1758" = sam numer kuwety - bez slow)
    assert slowa == [] or not any(s in tekst for s in slowa if s not in ("zs", "kor", "pg", "ab")), (wpis, slowa)


# --- kryterium 1: 200 zapytan, wlasciwa klasa, 0 zapisow w zlym wierszu ---------------------------------------------
def test_k1_200_zapytan_wlasciwa_klasa(zestaw, tmp_path):
    """Odczyt arkusza PRZED dopisaniem wierszy (P1), potem dopisanie, potem 200 propozycji - kazda na swiezym odczycie."""
    assert (AS.KLASA_JEDEN, AS.KLASA_JUZ, AS.KLASA_WSKAZ) == (EX.KLASA_JEDEN_WIERSZ, EX.KLASA_JUZ_ODHACZONE, EX.KLASA_WSKAZ_WIERSZ)
    assert len(zestaw.zapytania) == 200 and zestaw.arkusz.ostatni_wiersz == 30001 and len(zestaw.dopisania) == 4
    ark = zestaw.arkusz.kopia()
    ex = _excel(ark, tmp_path)  # odczyt sprzed dopisania
    zestaw.dopisz(ark)  # wspolpracownik dopisuje wiersze zlecen po odczycie
    tabela: dict[str, list[int]] = {}
    regula = Counter()
    bledy = []
    for q in zestaw.zapytania:
        d = _poz(ex, q).dopasowanie
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
            bledy.append((q.id, q.pulapka, q.klasa, q.wiersz, q.prawdziwy, d.klasa, d.wiersz, d.regula, d.kandydaci[:5], d.powod))
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
    wybiera z listy kandydatow wiersz tego zlecenia (gdy jest - wiersz wskazany przez TEST), inaczej pomija.
    Zmieniaja sie dokladnie oczekiwane pola B. Osobno: zapisy z wyboru programu i zapisy wierszy wskazanych przez test (P6)."""
    ark = _kopia(zestaw)
    ex = _excel(ark, tmp_path)
    w0, k0 = ark.zrzut()
    z_wyboru, ze_wskazania, wyniki = set(), set(), Counter()
    for q in zestaw.zapytania:
        poz = _poz(ex, q)
        d = poz.dopasowanie
        if d.klasa == EX.KLASA_JEDEN_WIERSZ:
            wpis = ex.zatwierdz(poz, OSOBA)
            assert (wpis["wynik"], wpis["wiersz"]) == (EX.WYNIK_ZAPISANO, q.wiersz), q
            z_wyboru.add(q.wiersz)
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
            ze_wskazania.add(q.prawdziwy)
        else:
            wpis = ex.pomin(poz, OSOBA)
        _bez_nazw(wpis, q.folder)
        wyniki[wpis["wynik"]] += 1
    oczekiwane = z_wyboru | ze_wskazania
    w1, k1 = ark.zrzut()
    zmienione = {kl for kl in set(k0) | set(k1) if k0.get(kl) != k1.get(kl)}
    zle = [op for op in _zapisy(ark) if op[1] not in oczekiwane or op[2] != KOL_B or op[3] != ZIELONY]
    print(f"\nwyniki: {dict(wyniki)}; zapisow {len(_zapisy(ark))}: z wyboru programu {len(z_wyboru)}, wiersz wskazany przez test "
          f"{len(ze_wskazania)}; w zlym wierszu {len(zle)}")
    assert w1 == w0  # zadna wartosc komorki sie nie zmienila
    assert zmienione == {(nr, KOL_B) for nr in oczekiwane} and all(k1[kl] == ZIELONY for kl in zmienione)
    assert zle == [] and len(_zapisy(ark)) == len(oczekiwane) and (len(z_wyboru), len(ze_wskazania)) == (110, 38)
    log = Counter(w["wynik"] for w in _log(tmp_path))
    # 200 wpisow koncowych + 4 odmowy "pole B w innym kolorze" (proba zapisu po wskazaniu - wpis "blad", potem "pominieto")
    assert sum(wyniki.values()) == 200 and log == {**wyniki, EX.WYNIK_BLAD: 4}


# --- kryterium 2: wyszukanie ponizej 50 ms -------------------------------------------------------------------------
def test_k2_wyszukanie_ponizej_50_ms(zestaw, tmp_path):
    ark = _kopia(zestaw)
    ex = EX.Excel(EX.Konfiguracja(log=tmp_path / "log_excel.csv"), ark, zegar=zegar)
    t0 = time.perf_counter()
    ex.odswiez()
    budowa = time.perf_counter() - t0
    t0 = time.perf_counter()
    ex.odswiez()  # ponowny odczyt (propozycja, zatwierdzenie): niezmienione wiersze z pamieci podrecznej
    ponowny = time.perf_counter() - t0
    czasy = []
    for q in zestaw.zapytania:
        t = time.perf_counter()
        ex.dopasuj(q.kuweta, q.folder)
        czasy.append(time.perf_counter() - t)
    print(f"\nodczyt i indeks 30 tys. wierszy: pierwszy {budowa * 1000:.0f} ms, ponowny {ponowny * 1000:.0f} ms; zapytanie: mediana "
          f"{statistics.median(czasy) * 1000:.3f} ms, max {max(czasy) * 1000:.3f} ms ({len(czasy)} zapytan)")
    assert max(czasy) < 0.050
    assert budowa < 10.0 and ponowny < 5.0


# --- kryterium 3: log CSV z polami reguly 6 --------------------------------------------------------------------------
def test_k3_log_csv_ma_pola_reguly_6(zestaw, tmp_path):
    assert EX.POLA_REGULY_6 == ("data", "godzina", "kuweta", "folder", "numer_zlecenia_b", "arkusz", "wiersz", "kto_zatwierdzil")
    assert EX.POLA_LOGU == EX.POLA_REGULY_6 + ("skoroszyt", "regula", "wynik", "tryb")
    ark = _kopia(zestaw)
    ex = _excel(ark, tmp_path)
    q1, q2, q3 = _pierwsze(zestaw, "prosty"), _pierwsze(zestaw, "pole_b_zielone"), _pierwsze(zestaw, "brak_kuwety_w_arkuszu")
    ex.zatwierdz(_poz(ex, q1), OSOBA)
    ex.zatwierdz(_poz(ex, q2), OSOBA)
    ex.pomin(_poz(ex, q3), OSOBA)
    with open(tmp_path / "log_excel.csv", encoding="utf-8-sig", newline="") as f:
        naglowek = next(csv.reader(f, delimiter=";"))
    assert tuple(naglowek[:8]) == EX.POLA_REGULY_6 and tuple(naglowek) == EX.POLA_LOGU
    w = _log(tmp_path)
    numer_b = ark.wartosc(q1.wiersz, KOL_B)
    assert w[0] == {"data": "2026-11-18", "godzina": "07:30:00", "kuweta": q1.kuweta, "folder": q1.folder,
                    "numer_zlecenia_b": EX.norm_numer(numer_b), "arkusz": "Zlecenia", "wiersz": str(q1.wiersz),
                    "kto_zatwierdzil": OSOBA, "skoroszyt": AS.SKOROSZYT, "regula": "2", "wynik": "zapisano", "tryb": "pytaj"}
    assert EX.norm_numer(numer_b) and "." not in w[0]["numer_zlecenia_b"]  # 40123.0 z COM -> "40123"
    assert (w[1]["wynik"], w[1]["regula"], w[1]["wiersz"]) == ("juz_odhaczone", "4", str(q2.wiersz))
    assert (w[2]["wynik"], w[2]["regula"], w[2]["wiersz"], w[2]["numer_zlecenia_b"]) == ("pominieto", "5", "", "")
    # nowy obiekt Excel dopisuje do tego samego pliku bez drugiego naglowka
    ex2 = _excel(ark, tmp_path)
    q4 = [q for q in zestaw.zapytania if q.pulapka == "prosty"][1]
    ex2.zatwierdz(_poz(ex2, q4), "Technik B")
    tekst = (tmp_path / "log_excel.csv").read_text(encoding="utf-8-sig")
    assert tekst.count("kto_zatwierdzil") == 1 and len(_log(tmp_path)) == 4 and _log(tmp_path)[3]["kto_zatwierdzil"] == "Technik B"


# --- kryterium 4: domyslnie "pytaj", "cien" nie zapisuje niczego ------------------------------------------------------
def test_k4_domyslnie_pytaj_przed_zapisem(zestaw, tmp_path):
    ust = UST.wczytaj_ustawienia(UST.PLIK_PRZYKLADU)
    konf = EX.Konfiguracja.z_ustawien(ust)
    assert konf.tryb == EX.TRYB_PYTAJ == EX.Konfiguracja().tryb == "pytaj" and konf.ostrzezenia == ()
    assert (konf.kolumna_daty, konf.kolumna_odhaczenia, konf.kolumna_kuwety, konf.kolumna_nazwy) == ("A", "B", "C", "H")
    assert konf.kolor == ZIELONY and konf.pierwszy_wiersz == 2 and konf.log == B.sciezka_z_ustawien(ust, "log_excel")
    assert konf.maks_wiek_dni == 60 == EX.Konfiguracja().maks_wiek_dni
    assert EX.TRYBY == ("pytaj", "cien")  # etap 3 (DW10): bez zapisu samodzielnego
    with pytest.raises(EX.BladExcela, match="tryb"):
        EX.Konfiguracja(tryb="auto")
    ust["excel"]["tryb_pytaj_przed_zapisem"] = False  # DW10: false nie wlacza zapisu samodzielnego
    konf2 = EX.Konfiguracja.z_ustawien(ust)
    assert konf2.tryb == "pytaj" and any("DW10" in o for o in konf2.ostrzezenia)
    ust["sciezki"]["log_excel"] = "C:/OneDrive/log_excel.csv"  # D11: log z nazwiskami poza dane/ = ostrzezenie
    assert any("dane/" in o for o in EX.Konfiguracja.z_ustawien(ust).ostrzezenia)
    # propozycje bez zatwierdzenia nie zmieniaja arkusza i nie pisza logu
    ark = _kopia(zestaw)
    ex = _excel(ark, tmp_path)
    przed = ark.zrzut()
    pozycje = [_poz(ex, q) for q in zestaw.zapytania]
    assert len(pozycje) == 200 and ark.zrzut() == przed and _zapisy(ark) == []
    assert not (tmp_path / "log_excel.csv").exists()


def test_k4_tryb_cien_nie_zapisuje_niczego(zestaw, tmp_path):
    ark = _kopia(zestaw)
    ex = _excel(ark, tmp_path, tryb=EX.TRYB_CIEN)
    przed = ark.zrzut()
    wyniki = Counter()
    for q in zestaw.zapytania:
        poz = _poz(ex, q)
        if poz.dopasowanie.klasa != EX.KLASA_WSKAZ_WIERSZ:
            wyniki[ex.zatwierdz(poz, OSOBA)["wynik"]] += 1
        elif q.prawdziwy is not None and q.pulapka != "pole_b_inny_kolor":
            wyniki[ex.zatwierdz(poz, OSOBA, wiersz=q.prawdziwy)["wynik"]] += 1
        else:
            wyniki[ex.pomin(poz, OSOBA)["wynik"]] += 1
    assert ark.zrzut() == przed and _zapisy(ark) == []
    log = _log(tmp_path)
    assert len(log) == 200 and {w["tryb"] for w in log} == {"cien"}
    wskazane = sum(1 for q in zestaw.zapytania if q.klasa == EX.KLASA_WSKAZ_WIERSZ and q.prawdziwy is not None and q.pulapka != "pole_b_inny_kolor")
    assert wskazane == 38
    # w trybie "pytaj" te same zatwierdzenia daja 110 + 38 zapisow koloru (test_k1_zero_zapisow_w_zlym_wierszu); tu: 0
    assert wyniki == {EX.WYNIK_TYLKO_LOG: 110 + wskazane, EX.WYNIK_JUZ_ODHACZONE: 19, EX.WYNIK_POMINIETO: 200 - 129 - wskazane}
    print(f"\ntryb cien: {dict(wyniki)}; zapisow koloru: {len(_zapisy(ark))}")


def test_k4_zapisz_cien_loguje_caly_piec(zestaw, tmp_path):
    ark = _kopia(zestaw)
    ex = _excel(ark, tmp_path, tryb=EX.TRYB_CIEN)
    przed = ark.zrzut()
    pozycje = [_poz(ex, q) for q in zestaw.zapytania[:40]]
    wpisy = ex.zapisz_cien(pozycje, OSOBA)
    assert len(wpisy) == 40 and ark.zrzut() == przed and _zapisy(ark) == []
    for q, poz, wpis in zip(zestaw.zapytania[:40], pozycje, wpisy):
        oczekiwany = EX.WYNIK_JUZ_ODHACZONE if poz.dopasowanie.klasa == EX.KLASA_JUZ_ODHACZONE else EX.WYNIK_TYLKO_LOG
        assert (wpis["wynik"], wpis["tryb"], wpis["wiersz"]) == (oczekiwany, "cien", poz.dopasowanie.wiersz)
        _bez_nazw(wpis, q.folder)
    with pytest.raises(EX.BladExcela, match="cien"):
        _excel(ark, tmp_path).zapisz_cien(pozycje, OSOBA)  # w trybie "pytaj" kazdy zapis zatwierdza czlowiek


# --- kryterium 5: zapis = kolor jednej komorki ------------------------------------------------------------------------
def test_k5_zapis_dotyka_tylko_koloru_jednej_komorki(zestaw, tmp_path):
    ark = _kopia(zestaw)
    ex = _excel(ark, tmp_path)
    q = _pierwsze(zestaw, "ta_sama_kuweta_inne_daty")
    poz = _poz(ex, q)
    w0, k0 = ark.zrzut()
    ark.operacje.clear()
    wpis = ex.zatwierdz(poz, OSOBA)
    w1, k1 = ark.zrzut()
    assert wpis["wynik"] == "zapisano" and w1 == w0
    assert {kl for kl in set(k0) | set(k1) if k0.get(kl) != k1.get(kl)} == {(q.wiersz, KOL_B)} and k1[(q.wiersz, KOL_B)] == ZIELONY
    assert _zapisy(ark) == [("ustaw_wypelnienie", q.wiersz, KOL_B, ZIELONY)]
    assert {op[0] for op in ark.operacje} <= {"odczytaj", "wiersz", "wypelnienie", "ustaw_wypelnienie"}  # poza zapisem tylko odczyty


# --- bezpieczenstwo zapisu: P1 swiezy odczyt, P2 ten sam skoroszyt i arkusz, wspoledycja -------------------------------
def test_arkusz_zmieniony_po_propozycji_odmowa_bez_zapisu(zestaw, tmp_path):
    ark = _kopia(zestaw)
    ex = _excel(ark, tmp_path)
    q = _pierwsze(zestaw, "prosty")
    poz = _poz(ex, q)
    ark.wstaw_wiersz(q.wiersz - 3, [dt.datetime(2026, 11, 17), 99999.0, 7.0, "", "", 1, "", "Abakowski 7 zs", ""])  # wspoledycja
    przed = ark.zrzut()
    with pytest.raises(EX.BladExcela, match="zmienil"):
        ex.zatwierdz(poz, OSOBA)
    assert ark.zrzut() == przed and _zapisy(ark) == []
    assert _log(tmp_path)[-1]["wynik"] == "blad"
    poz2 = _poz(ex, q)  # propozycja = swiezy odczyt
    assert poz2.dopasowanie.wiersz == q.wiersz + 1
    assert ex.zatwierdz(poz2, OSOBA)["wiersz"] == q.wiersz + 1 and ark.wartosc(q.wiersz + 1, 8) == q.folder


def test_p1_wiersz_zlecenia_dopisany_po_odczycie(tmp_path):
    """P1: propozycja z odczytu sprzed dopisania wiersza zlecenia wskazuje stary wiersz kuwety (puste H, w limicie wieku) -
    zatwierdzenie robi swiezy odczyt, widzi zmiane i odmawia; nowa propozycja wskazuje dopisany wiersz."""
    ark = _maly([(D1, 51001.0, 3263.0, "")])
    ex = _excel(ark, tmp_path)
    poz = ex.pozycja("3263", T, sesja_pieca_id=SESJA)
    assert (poz.dopasowanie.klasa, poz.dopasowanie.wiersz, poz.dopasowanie.regula) == (J, 2, 3)
    nr = ark.dopisz([D3, 51002.0, 3263.0, "Gabinet 01", "korona", 1, "A2", T, ""])
    with pytest.raises(EX.BladExcela, match="zmienil"):
        ex.zatwierdz(poz, OSOBA)
    assert _zapisy(ark) == [] and _log(tmp_path)[-1]["wynik"] == "blad"
    poz2 = ex.pozycja("3263", T, sesja_pieca_id=SESJA)
    assert (poz2.dopasowanie.klasa, poz2.dopasowanie.wiersz) == (J, nr)
    assert ex.zatwierdz(poz2, OSOBA)["wiersz"] == nr and _zapisy(ark) == [("ustaw_wypelnienie", nr, KOL_B, ZIELONY)]


def test_p2_zapis_tylko_do_skoroszytu_i_arkusza_z_propozycji(tmp_path):
    ark = _maly([(D3, 51001.0, 3263.0, T)])
    zrodla = [ark]
    ex = EX.Excel(EX.Konfiguracja(log=tmp_path / "log_excel.csv"), lambda: zrodla[-1], zegar=zegar, czekaj=bez_czekania)
    poz = ex.pozycja("3263", T, sesja_pieca_id=SESJA)
    assert (poz.skoroszyt, poz.arkusz) == (AS.SKOROSZYT, "Test")
    assert any(AS.SKOROSZYT in o and "Test" in o for o in ex.ostrzezenia)  # [excel] skoroszyt / arkusz puste = nazwy uzyte
    for kopia in (ark.kopia(nazwa="Test (2)"), ark.kopia(skoroszyt="Zlecenia - kopia.xlsx")):  # te same wartosci, inne miejsce
        zrodla.append(kopia)
        ex.rozlacz()
        with pytest.raises(EX.BladExcela, match="skoroszyt albo arkusz"):
            ex.zatwierdz(poz, OSOBA)
        assert _zapisy(kopia) == []
    zrodla.append(ark)
    ex.rozlacz()
    ark.skoroszyt = "Zlecenia zapisane jako.xlsx"  # "Zapisz jako" na tym samym obiekcie
    with pytest.raises(EX.BladExcela, match="skoroszyt albo arkusz"):
        ex.zatwierdz(poz, OSOBA)
    ark.skoroszyt = AS.SKOROSZYT
    assert _zapisy(ark) == [] and [w["wynik"] for w in _log(tmp_path)] == ["blad"] * 3
    assert ex.zatwierdz(poz, OSOBA)["wynik"] == "zapisano"
    assert _log(tmp_path)[-1]["skoroszyt"] == AS.SKOROSZYT and _log(tmp_path)[-1]["arkusz"] == "Test"


def test_pole_b_zazielenione_w_miedzyczasie_tylko_log(zestaw, tmp_path):
    ark = _kopia(zestaw)
    ex = _excel(ark, tmp_path)
    q = _pierwsze(zestaw, "prosty")
    poz = _poz(ex, q)
    ark.zaznacz(q.wiersz, KOL_B, ZIELONY)  # ktos odhaczyl recznie
    wpis = ex.zatwierdz(poz, OSOBA)
    assert (wpis["wynik"], wpis["regula"]) == (EX.WYNIK_JUZ_ODHACZONE, 4) and _zapisy(ark) == []


def test_wskaz_wiersz_tylko_z_listy_kandydatow(zestaw, tmp_path):
    ark = _kopia(zestaw)
    ex = _excel(ark, tmp_path)
    q = _pierwsze(zestaw, "inicjaly_zamiast_nazwiska")
    poz = _poz(ex, q)
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
    ark = _kopia(zestaw)
    ex = _excel(ark, tmp_path)
    q = _pierwsze(zestaw, "prosty")
    poz = _poz(ex, q)
    for zly in ("", "   ", None):
        with pytest.raises(EX.BladExcela, match="kto zatwierdza"):
            ex.zatwierdz(poz, zly)
    ex.zatwierdz(poz, OSOBA)
    with pytest.raises(EX.BladExcela, match="juz zalatwiona"):
        ex.zatwierdz(poz, OSOBA)
    with pytest.raises(EX.BladExcela, match="juz zalatwiona"):
        ex.pomin(poz, OSOBA)
    assert len(_zapisy(ark)) == 1 and len(_log(tmp_path)) == 1


def test_d3_x4_zapis_tylko_dla_pozycji_z_zamknietego_pieca(zestaw, tmp_path):
    ark = _kopia(zestaw)
    ex = _excel(ark, tmp_path)
    q = _pierwsze(zestaw, "prosty")
    poz = ex.pozycja(q.kuweta, q.folder)  # bez sesji pieca - tylko podglad
    with pytest.raises(EX.BladExcela, match="X4"):
        ex.zatwierdz(poz, OSOBA)
    assert _zapisy(ark) == [] and not poz.zalatwiona
    qz = _pierwsze(zestaw, "pole_b_zielone")  # "juz odhaczone" niczego nie zapisuje - wolno bez sesji
    assert ex.zaloguj_juz_odhaczone(ex.pozycja(qz.kuweta, qz.folder), OSOBA)["wynik"] == EX.WYNIK_JUZ_ODHACZONE
    with pytest.raises(EX.BladExcela, match="juz odhaczone"):
        ex.zaloguj_juz_odhaczone(_poz(ex, q), OSOBA)  # pozycja "jeden wiersz" - ta metoda nie zapisuje koloru
    assert _zapisy(ark) == []


def test_r3_d2_zaloguj_juz_odhaczone_odmawia_przy_do_sprawdzenia(tmp_path):
    """Runda 3, D2 (proba R7): zlecenie niewpisane, najnowszy wiersz kuwety sprzed 30 dni z pustym H i zielonym B = "juz
    odhaczone" z ``do_sprawdzenia`` - bez pytania nie wolno tego zalogowac; czlowiek zatwierdza ``zatwierdz``."""
    ex = _excel(_maly([(_d("2026-10-19"), 1.0, 3263.0, "")], ((2, ZIELONY),)), tmp_path)
    poz = ex.pozycja("3263", T, sesja_pieca_id=SESJA)
    assert (poz.dopasowanie.klasa, poz.dopasowanie.do_sprawdzenia) == (Z, True)
    with pytest.raises(EX.BladExcela, match="do sprawdzenia"):
        ex.zaloguj_juz_odhaczone(poz, OSOBA)
    assert not poz.zalatwiona and ex.zatwierdz(poz, OSOBA)["wynik"] == EX.WYNIK_JUZ_ODHACZONE


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
    ex.pozycja("3263", "Testowski 3263 zs")  # propozycja: zawsze swiezy odczyt (P1)
    assert sum(1 for op in ark.operacje if op[0] == "odczytaj") == 3


def test_excel_niedostepny_komunikat_bez_awarii(tmp_path):
    def brak():
        raise XC.BladCom("Excel nie jest uruchomiony")

    ex = EX.Excel(EX.Konfiguracja(log=tmp_path / "log.csv"), brak, zegar=zegar)
    with pytest.raises(EX.BladExcela, match="Excel niedostepny"):
        ex.odswiez()
    ark = _maly([(_d("2026-11-16"), 51001.0, 3263.0, "Testowski 3263 zs")])
    ex2 = EX.Excel(EX.Konfiguracja(log=tmp_path / "log.csv"), lambda: ark, zegar=zegar)  # polaczenie leniwe (fabryka)
    assert ex2.dopasuj("3263", "Testowski 3263 zs").wiersz == 2


def test_d1_repr_bez_nazwiska(tmp_path):
    ex = _excel(_maly([(D3, 51001.0, 3263.0, T)]), tmp_path)
    w = ex.indeks().po_nr[2]
    assert w.nazwa == "testowski 3263 zs" and "testowski" not in repr(w).lower()
    poz = ex.pozycja("3263", T)
    assert "testowski" not in repr(poz).lower()


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
D1, D2, D3 = _d("2026-10-01"), _d("2026-11-10"), _d("2026-11-16")  # w limicie 60 dni od 2026-11-18
STARA = _d("2026-08-01")  # 109 dni - ponad limit
PRZYPADKI = [
    # opis, wiersze (A, B, C, H), kolory B, kuweta, folder, klasa, wiersz, regula, kandydaci (None = nie sprawdzaj)
    ("r1 dokladnie, nie fragment", [(D3, 1.0, "13263", T), (D2, 2.0, 3263.0, T), (D3, 3.0, "3263/2", T)], (), "3263", T, J, 3, 2, (3,)),
    ("r2 nazwa rozstrzyga, nowszy wiersz innej osoby zielony", [(D3, 1.0, 3263.0, "Probny 3263 kor"), (D1, 2.0, 3263.0, T)], ((2, ZIELONY),),
     "3263", T, J, 3, 2, None),
    ("P3 r2 nowszy otwarty wiersz innej osoby", [(D3, 1.0, 3263.0, "Probny 3263 kor"), (D1, 2.0, 3263.0, T)], (), "3263", T, W, None, 5, (3, 2)),
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
    ("D8 data z przyszlosci = bez daty", [(D2, 1.0, 3263.0, ""), (_d("2027-11-16"), 2.0, 3263.0, "")], (), "3263", T, W, None, 5, None),
    ("r4 pole B juz zielone", [(D3, 1.0, 3263.0, T)], ((2, ZIELONY),), "3263", T, Z, 2, 4, None),
    ("r4 reklamacja: stary zielony, nowy otwarty", [(D1, 1.0, 3263.0, T), (D3, 2.0, 3263.0, T)], ((2, ZIELONY),), "3263", T, J, 3, 3, None),
    ("r4 reklamacja: oba zielone", [(D1, 1.0, 3263.0, T), (D3, 2.0, 3263.0, T)], ((2, ZIELONY), (3, ZIELONY)), "3263", T, Z, 3, 4, None),
    ("r4 bialy = bez wypelnienia", [(D3, 1.0, 3263.0, T)], ((2, (255, 255, 255)),), "3263", T, J, 2, 2, None),
    ("P3 reklamacja z innym H, stary otwarty", [(D1, 1.0, 3263.0, T), (D3, 2.0, 3263.0, "Testowski J. 3263 rekl.")], (), "3263", T, W, None, 5,
     (2, 3)),
    ("P3 reklamacja z innym H, stary zielony", [(D1, 1.0, 3263.0, T), (D3, 2.0, 3263.0, "Testowski J. 3263 rekl.")], ((2, ZIELONY),), "3263", T,
     W, None, 5, (2, 3)),
    ("P3 zlecenie niewpisane: stary wiersz, puste H", [(_d("2024-05-07"), 1.0, 3263.0, "")], (), "3263", T, W, None, 5, (2,)),
    ("P3 zlecenie niewpisane: stary wiersz, puste H, zielony", [(_d("2024-05-07"), 1.0, 3263.0, "")], ((2, ZIELONY),), "3263", T, W, None, 5,
     (2,)),
    ("limit wieku: H jak folder, ponad 60 dni", [(STARA, 1.0, 3263.0, T)], (), "3263", T, W, None, 5, (2,)),
    ("limit wieku: H jak folder, zielone, ponad 60 dni", [(STARA, 1.0, 3263.0, T)], ((2, ZIELONY),), "3263", T, W, None, 5, (2,)),
    ("limit wieku: wiersz bez daty", [(None, 1.0, 3263.0, T)], (), "3263", T, W, None, 5, (2,)),
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
    ("P3 prywatne: B zwyklego zlecenia z 2019", [(_d("2019-01-15"), 1234.0, 3263.0, "Probny 3263 kor")], (), "#1234", "#1234", W, None, 5, ()),
    ("P3 prywatne: B zwyklego zlecenia biezacego", [(D3, 1234.0, 3263.0, "Probny 3263 kor")], (), "#1234", "#1234", W, None, 5, ()),
    ("P3 prywatne: wiersz prywatny ponad limit", [(STARA, 1234.0, None, "Testowski")], (), "#1234", "#1234", W, None, 5, (2,)),
    # runda 3, D4 (proba R6): numer karteczki wraca - stary wiersz prywatny ponad limit + swiezy = swiezy (do_sprawdzenia - test nizej)
    ("D4 prywatne: wiersz ponad limit i swiezy", [(STARA, 1234.0, None, "Probny"), (D3, 1234.0, None, "Testowski")], (), "#1234", "#1234", J, 3,
     2, (3, 2)),
]


@pytest.mark.parametrize("opis, wiersze, kolory, kuweta, folder, klasa, wiersz, regula, kandydaci", PRZYPADKI, ids=[p[0] for p in PRZYPADKI])
def test_reguly_1_5_na_malym_arkuszu(tmp_path, opis, wiersze, kolory, kuweta, folder, klasa, wiersz, regula, kandydaci):
    ex = _excel(_maly(wiersze, kolory), tmp_path)
    d = ex.dopasuj(kuweta, folder)
    assert (d.klasa, d.wiersz, d.regula) == (klasa, wiersz, regula), d
    if kandydaci is not None:
        assert d.kandydaci == kandydaci, d
    assert "testowski" not in d.powod.lower() and "probny" not in d.powod.lower()


def test_p3_limit_wieku_wylaczony_i_do_sprawdzenia(tmp_path):
    """``maks_wiek_dni = 0`` = reguly doslownie (bez limitu); wybor reguly 3 i zlecenia prywatnego = ``do_sprawdzenia``
    (A12 pokazuje, nie zatwierdza w ciszy); wybor po nazwie (regula 2) - nie."""
    ex = _excel(_maly([(STARA, 1.0, 3263.0, T)]), tmp_path, maks_wiek_dni=0)
    assert (ex.dopasuj("3263", T).klasa, ex.dopasuj("3263", T).wiersz) == (J, 2)
    ex = _excel(_maly([(_d("2024-05-07"), 1.0, 3263.0, "")], ((2, ZIELONY),)), tmp_path, maks_wiek_dni=0)
    d = ex.dopasuj("3263", T)
    assert (d.klasa, d.wiersz, d.do_sprawdzenia) == (Z, 2, True)
    ex = _excel(_maly([(D3, 1.0, 3263.0, T), (D3, 1234.0, None, "Probny")]), tmp_path)
    assert ex.dopasuj("3263", T).do_sprawdzenia is False and ex.dopasuj("#1234", "#1234").do_sprawdzenia is True
    ex = _excel(_maly([(STARA, 1234.0, None, "Probny"), (D3, 1234.0, None, "Testowski")]), tmp_path)  # D4 (runda 3)
    d = ex.dopasuj("#1234", "#1234")
    assert (d.klasa, d.wiersz, d.do_sprawdzenia) == (J, 3, True)


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


def test_d9_kolumny_do_xfd():
    assert EX.numer_kolumny("A") == 1 and EX.numer_kolumny("H") == 8 and EX.numer_kolumny("XFD") == 16384
    with pytest.raises(EX.BladExcela):
        EX.numer_kolumny("XFE")


# --- propozycje z wyniku "Zamknij piec" (session_rano) i zapis w excel_zapisy ----------------------------------------
def _baza_z_piecem(tmp_path, zamkniety: bool = True):
    baza = B.otworz(tmp_path / "stanowisko.sqlite", zegar=zegar)
    zl = {}
    for folder, kuweta in (("Testowski 3263 zs", "3263"), ("Probna 412 kor", "412"), ("Atrapowicz 77 zs", "77")):
        zl[kuweta] = baza.wstaw("zlecenia", zrodlo="cyrkon", folder=folder, folder_norm=N.znormalizuj(folder), kuweta=kuweta)
    piec = baza.wstaw("sesje_pieca", data="2026-11-18", nr_w_dniu=1, otwarto="2026-11-18T06:40:00",
                      zamknieto="2026-11-18T07:25:00" if zamkniety else None, zamknal=OSOBA if zamkniety else None)
    return baza, zl, piec


def test_propozycje_z_wyniku_pieca_i_tabela_excel_zapisy(tmp_path):
    baza, zl, piec = _baza_z_piecem(tmp_path)
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
    wpisy = [ex.zatwierdz(pozycje[0], OSOBA), ex.zatwierdz(pozycje[1], OSOBA), ex.pomin(pozycje[2], OSOBA)]
    wpisy += ex.zaloguj_poprawki(wynik, OSOBA)
    assert [w["wynik"] for w in wpisy] == ["zapisano", "juz_odhaczone", "pominieto", "tylko_log"]
    for w, folder in zip(wpisy, ("Testowski 3263 zs", "Probna 412 kor", "Atrapowicz 77 zs", "Testowski 3263 zs")):
        _bez_nazw(w, folder)  # P4: wynik dla A12 bez nazwy folderu - tylko id wpisu, kuweta, wiersz, klasa ...
    assert _zapisy(ark) == [("ustaw_wypelnienie", 2, KOL_B, ZIELONY)]
    zapisy = baza.wiersze("SELECT * FROM excel_zapisy ORDER BY id")
    assert [w["id"] for w in wpisy] == [z["id"] for z in zapisy]
    # poprawka zlecenia juz odhaczonego: tylko log (SE5); wiersz zlecenia jest juz zielony (zapis wyzej) - regula 4
    assert [(w["wynik"], w["regula"], w["wiersz"]) for w in zapisy] == [("zapisano", 2, 2), ("juz_odhaczone", 4, 3), ("pominieto", 5, None),
                                                                        ("tylko_log", 4, 2)]
    assert {k: zapisy[0][k] for k in ("czas", "sesja_pieca_id", "zlecenie_id", "kuweta", "folder", "numer_zlecenia_b", "arkusz", "tryb", "operator")} == {
        "czas": "2026-11-18T07:30:00", "sesja_pieca_id": piec, "zlecenie_id": zl["3263"], "kuweta": "3263", "folder": "Testowski 3263 zs",
        "numer_zlecenia_b": "51001", "arkusz": f"{AS.SKOROSZYT}!Test", "tryb": "pytaj", "operator": OSOBA}
    assert len(_log(tmp_path)) == 4  # kazdy wiersz excel_zapisy idzie tez do log_excel.csv (plan 3.4)
    # DW2: nazwa folderu tylko w zlecenia i excel_zapisy
    zrzut = baza.zrzut()
    for tabela, wiersze in zrzut.items():
        if tabela not in ("zlecenia", "excel_zapisy"):
            assert "Testowski" not in json.dumps(wiersze, ensure_ascii=False), tabela
    # zapis tylko po "Zamknij piec" (X4)
    with pytest.raises(EX.BladExcela, match="Zamknij piec"):
        ex.propozycje({**wynik, "zamknieto": None})
    # D5: brak zlecenia w bazie nie przerywa propozycji calego pieca
    poz = ex.propozycje({**wynik, "kompletne": [{"zlecenie_id": 999, "kuweta": "1"}, wynik["kompletne"][0]]})
    assert [p.dopasowanie.klasa for p in poz] == [W, Z] and "zlecenia" in poz[0].dopasowanie.powod
    baza.zamknij()


def test_a6_wynik_zamknij_piec_z_sesji_rano_do_propozycji_i_zapisu(tmp_path):
    """Zgodnosc z obecnym API ``session_rano`` (A6 runda 5): prawdziwy ``SesjaRano`` (harness testow A6) - skan poranny obu prac
    zlecenia Y (kuweta 3301), "Zamknij piec" -> ``propozycje`` -> jeden wiersz. ``otworz_piec_ponownie`` przed zatwierdzeniem =
    odmowa X4 (piec znow otwarty); po ponownym zamknieciu ``wynik_pieca`` -> propozycja -> zapis i ``excel_zapisy`` z sesja pieca."""
    import test_session_rano as TSR

    st = TSR.Stanowisko(tmp_path)
    TSR.wypelnij_indeks(st.sesja.baza)
    st.skan(TSR.rano(4, "2026-11-18T07:00:00", [{"g": 2, "k": [["Y21", 0.95]]}, {"g": 3, "k": [["Y22", 0.95]]}]))
    wynik = st.rano.zamknij_piec()
    assert [z["kuweta"] for z in wynik["kompletne"]] == ["3301"] and wynik["zamknieto"]
    ark = _maly([(D1, 51001.0, 3301.0, "Inna Osoba 3301 zs"), (D3, 51002.0, 3301.0, "Przykladowy Jan 3301 ZR")], ((2, ZIELONY),))
    ex = EX.Excel(EX.Konfiguracja(log=tmp_path / "log_excel.csv"), ark, baza=st.sesja.baza, zegar=zegar, czekaj=bez_czekania)
    (poz,) = ex.propozycje(wynik)
    assert (poz.dopasowanie.klasa, poz.dopasowanie.wiersz, poz.sesja_pieca_id) == (J, 3, wynik["sesja_pieca_id"])
    st.rano.otworz_piec_ponownie(wynik["sesja_pieca_id"])  # pomylka przy zamykaniu - piec znow otwarty
    with pytest.raises(EX.BladExcela, match="X4"):
        ex.zatwierdz(poz, OSOBA)
    assert _zapisy(ark) == [] and ex.zaloguj_poprawki(wynik, OSOBA) == []
    st.rano.zamknij_piec()
    wynik2 = st.rano.wynik_pieca(wynik["sesja_pieca_id"])  # jak po restarcie programu
    (poz2,) = ex.propozycje(wynik2)
    wpis = ex.zatwierdz(poz2, OSOBA)
    assert (wpis["wynik"], wpis["wiersz"]) == ("zapisano", 3) and _zapisy(ark) == [("ustaw_wypelnienie", 3, KOL_B, ZIELONY)]
    z = st.sesja.baza.wiersz("SELECT * FROM excel_zapisy WHERE id = ?", (wpis["id"],))
    assert (z["sesja_pieca_id"], z["kuweta"], z["wynik"], z["folder"]) == (wynik["sesja_pieca_id"], "3301", "zapisano", "Przykladowy Jan 3301 ZR")
    st.sesja.baza.zamknij()


def test_p1_propozycje_robia_swiezy_odczyt(tmp_path):
    baza, zl, piec = _baza_z_piecem(tmp_path)
    ark = _maly([(D1, 51001.0, 3263.0, "")])
    ex = _excel(ark, tmp_path, baza=baza)  # odczyt sprzed dopisania
    nr = ark.dopisz([D3, 51002.0, 3263.0, "Gabinet 01", "korona", 1, "A2", "Testowski 3263 zs", ""])
    wynik = {"sesja_pieca_id": piec, "zamknieto": "2026-11-18T07:25:00", "kompletne": [{"zlecenie_id": zl["3263"], "kuweta": "3263"}], "poprawki": []}
    (poz,) = ex.propozycje(wynik)
    assert (poz.dopasowanie.klasa, poz.dopasowanie.wiersz) == (J, nr)
    baza.zamknij()


def test_d3_x4_pozycja_z_otwartego_pieca_odmowa(tmp_path):
    baza, zl, piec = _baza_z_piecem(tmp_path, zamkniety=False)
    ex = _excel(_maly([(D3, 51001.0, 3263.0, "Testowski 3263 zs")]), tmp_path, baza=baza)
    with pytest.raises(EX.BladExcela, match="X4"):
        ex.pozycja("3263", "Testowski 3263 zs", zlecenie_id=zl["3263"], sesja_pieca_id=piec)
    baza.zamknij()


def test_p5_blad_logu_csv_po_zapisie_koloru(tmp_path, monkeypatch):
    baza, zl, piec = _baza_z_piecem(tmp_path)
    ark = _maly([(D3, 51001.0, 3263.0, "Testowski 3263 zs")])
    ex = _excel(ark, tmp_path, baza=baza)
    poz = ex.pozycja("3263", "Testowski 3263 zs", zlecenie_id=zl["3263"], sesja_pieca_id=piec)

    def zajety(_wpis):
        raise PermissionError("plik zajety przez inny program")

    monkeypatch.setattr(ex, "_dopisz_csv", zajety)  # plik logu otwarty w Excelu PO kontroli przed zapisem
    with pytest.raises(EX.BladExcela, match="log_excel.csv"):
        ex.zatwierdz(poz, OSOBA)
    assert _zapisy(ark) == [("ustaw_wypelnienie", 2, KOL_B, ZIELONY)]
    assert poz.zalatwiona and poz.stan == EX.STAN_ZAPISANO_BEZ_CSV
    assert [(w["wynik"], w["wiersz"]) for w in baza.wiersze("SELECT * FROM excel_zapisy")] == [("zapisano", 2)]
    with pytest.raises(EX.BladExcela, match="zalatwiona"):
        ex.zatwierdz(poz, OSOBA)
    assert len(_zapisy(ark)) == 1
    baza.zamknij()


# --- warstwa COM (bez Excela: atrapa obiektow COM) -------------------------------------------------------------------
class _Interior:
    def __init__(self, komorka):
        object.__setattr__(self, "_k", komorka)

    def __getattr__(self, nazwa):
        if self._k.arkusz.odczyt_koloru_pada and nazwa in ("ColorIndex", "Color"):
            raise RuntimeError("polaczenie z Excelem zerwane (atrapa)")
        kolor = self._k.arkusz.kolory.get((self._k.row, self._k.column))
        if nazwa == "ColorIndex":
            return XC.XL_BRAK_WYPELNIENIA if kolor is None else 35
        if nazwa == "Color":
            return 16777215 if kolor is None else kolor
        raise AttributeError(nazwa)

    def __setattr__(self, nazwa, wartosc):
        a, kl = self._k.arkusz, (self._k.row, self._k.column)
        if nazwa == "Color":
            a.proby.append(kl)
            if a.przed_zapisem:  # wspoledytor zmienia arkusz miedzy kontrola a zapisem (to samo wywolanie)
                zdarzenie, a.przed_zapisem = a.przed_zapisem, None
                zdarzenie()
            if a.odrzuc_zapis > 0:  # Excel zajety (np. przyjmuje zmiany wspoledytora): RPC_E_CALL_REJECTED
                a.odrzuc_zapis -= 1
                if a.przy_odrzuceniu:
                    a.przy_odrzuceniu()
                raise RuntimeError("Call was rejected by callee (atrapa)")
            a.kolory[kl] = wartosc
            if a.zapisz_i_rzuc > 0:  # czesciowy sukces: kolor zapisany, wywolanie zwraca blad (runda 3, P1)
                a.zapisz_i_rzuc -= 1
                a.ustawienia.append((*kl, nazwa, wartosc))
                a.odczyt_koloru_pada = a.potem_odczyt_pada
                raise RuntimeError("polaczenie zerwane po zapisie (atrapa)")
        a.ustawienia.append((*kl, nazwa, wartosc))
        if nazwa == "Color" and a.po_zapisie:
            zdarzenie, a.po_zapisie = a.po_zapisie, None
            zdarzenie()


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
        self.Name, self.dane, self.kolory, self.ustawienia, self.proby = nazwa, dane, {}, [], []
        self.odrzuc_zapis, self.przy_odrzuceniu, self.po_zapisie = 0, None, None
        self.zapisz_i_rzuc, self.przed_zapisem, self.odczyt_koloru_pada, self.potem_odczyt_pada = 0, None, False, False

    @property
    def UsedRange(self):
        return _UzytyZakres(self)

    def Cells(self, r, c):
        return _Komorka(self, r, c)

    def Range(self, a, b):
        return _Zakres(self, a, b)

    def wstaw_wiersz(self, nr, wartosci):
        """Wspoledytor wstawia wiersz przed ``nr`` (wiersze i kolory nizej przesuwaja sie o 1)."""
        self.dane.insert(nr - 1, list(wartosci))
        self.kolory = {((r + 1 if r >= nr else r), c): k for (r, c), k in self.kolory.items()}


class _Zakazane:
    def __init__(self, dziennik, nazwa):
        self.dziennik, self.nazwa = dziennik, nazwa

    def __call__(self, *a, **k):
        self.dziennik.append(self.nazwa)
        raise AssertionError(f"wywolano zakazane {self.nazwa}")


class _Skoroszyt:
    def __init__(self, nazwa, arkusze, dziennik):
        self.Name, self.FullName, self._arkusze = nazwa, f"atrapa://firma/{nazwa}", {a.Name: a for a in arkusze}
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


WIERSZ_INNY = [D3, 59999.0, 7.0, "Gab", "korona", 1, "A2", "Abakowski 7 kor", ""]


def _aplikacja():
    dane = [list(AS.NAGLOWEK), [D2, 51001.0, 3263.0, "Gab", "korona", 1, "A2", "Testowski 3263 zs", ""],
            [D3, 51002.0, 412.0, "Gab", "most", 2, "A3", "Probna 412 kor", ""]]
    return _Aplikacja(lambda dz: [_Skoroszyt("Inny.xlsx", [_ArkuszCom("Arkusz1", [["x"]])], dz),
                                  _Skoroszyt("Zlecenia 2026.xlsx", [_ArkuszCom("Archiwum", [["y"]]), _ArkuszCom("2026", dane)], dz)])


def _excel_com(tmp_path, app, polaczen=None):
    def polacz():
        if polaczen is not None:
            polaczen.append(1)
        return XC.polacz("zlecenia", "2026", aplikacja=app)

    return EX.Excel(EX.Konfiguracja(log=tmp_path / "log_excel.csv", skoroszyt="zlecenia", arkusz="2026"), polacz, zegar=zegar, czekaj=bez_czekania)


def test_excel_com_atrapa_interfejsu_odczyt_i_kolor():
    app = _aplikacja()
    ark = XC.polacz("zlecenia", "2026", aplikacja=app)
    assert (ark.nazwa, ark.skoroszyt, ark.sciezka) == ("2026", "Zlecenia 2026.xlsx", "atrapa://firma/Zlecenia 2026.xlsx")
    assert ark.odczytaj(2, 9) == [tuple(r) for r in app.Workbooks[1].Worksheets("2026").dane[1:]]
    assert ark.wiersz(3, 9)[7] == "Probna 412 kor" and ark.wiersz(2, 3) == (D2, 51001.0, 3263.0)
    com = app.Workbooks[1].Worksheets("2026")
    assert ark.wypelnienie(2, 2) is None
    com.kolory[(3, 2)] = 206 * 65536 + 239 * 256 + 198  # COM: kolor = R + 256 G + 65536 B
    assert ark.wypelnienie(3, 2) == ZIELONY
    ark.ustaw_wypelnienie(2, 2, ZIELONY)
    assert com.ustawienia == [(2, 2, "Color", 198 + 239 * 256 + 206 * 65536)]  # jedna komorka, jedna wlasciwosc
    assert ark.wypelnienie(2, 2) == ZIELONY
    com.odrzuc_zapis = 1  # B1: warstwa COM NIE ponawia zapisu sama (ponowienie = caly krok z kontrola w excel.zatwierdz)
    with pytest.raises(XC.BladCom, match="odrzucil"):
        ark.ustaw_wypelnienie(3, 2, ZIELONY)
    assert com.proby[-1:] == [(3, 2)] and len(com.proby) == 2
    assert app.dziennik == []  # bez Open, Add, Save, SaveAs, SaveCopyAs, Close, Quit (X1)
    # domyslnie: aktywny skoroszyt i aktywny arkusz
    assert XC.polacz(aplikacja=app).nazwa == "Arkusz1"
    with pytest.raises(XC.BladCom, match="skoroszyt"):
        XC.polacz("nie ma takiego", aplikacja=app)
    with pytest.raises(XC.BladCom, match="arkusz"):
        XC.polacz("zlecenia", "1999", aplikacja=app)


def test_excel_com_pelny_przebieg_zmienia_tylko_kolor_jednej_komorki(tmp_path):
    app = _aplikacja()
    ex = _excel_com(tmp_path, app)
    com = app.Workbooks[1].Worksheets("2026")
    dane_przed = [list(r) for r in com.dane]
    poz = ex.pozycja("3263", "Testowski 3263 zs", sesja_pieca_id=SESJA)
    wpis = ex.zatwierdz(poz, OSOBA)
    assert (wpis["wynik"], wpis["wiersz"]) == ("zapisano", 2) and _log(tmp_path)[-1]["skoroszyt"] == "Zlecenia 2026.xlsx"
    assert com.ustawienia == [(2, 2, "Color", 198 + 239 * 256 + 206 * 65536)] and com.dane == dane_przed and app.dziennik == []


def test_b1_odrzucony_zapis_i_wstawiony_wiersz_zadnego_zapisu_w_zlym_wierszu(tmp_path):
    """B1 (proba P1 recenzenta): pierwsze wywolanie zapisu odrzucone, w tym czasie wspoledytor wstawia wiersz nad wierszem
    zlecenia. Ponowienie = caly krok (swiezy odczyt, kontrola, zapis) - widzi zmiane i odmawia; zaden kolor nie jest zapisany."""
    app = _aplikacja()
    ex = _excel_com(tmp_path, app)
    com = app.Workbooks[1].Worksheets("2026")
    poz = ex.pozycja("3263", "Testowski 3263 zs", sesja_pieca_id=SESJA)
    com.odrzuc_zapis = 1
    com.przy_odrzuceniu = lambda: com.wstaw_wiersz(2, WIERSZ_INNY)
    with pytest.raises(EX.BladExcela, match="zmienil"):
        ex.zatwierdz(poz, OSOBA)
    assert com.proby == [(2, 2)] and com.kolory == {} and not poz.zalatwiona
    assert _log(tmp_path)[-1]["wynik"] == "blad"


def test_b1_odrzucony_zapis_bez_zmian_ponowienie_udane(tmp_path):
    app = _aplikacja()
    ex = _excel_com(tmp_path, app)
    com = app.Workbooks[1].Worksheets("2026")
    poz = ex.pozycja("3263", "Testowski 3263 zs", sesja_pieca_id=SESJA)
    com.odrzuc_zapis = 1
    assert ex.zatwierdz(poz, OSOBA)["wynik"] == "zapisano"
    assert com.proby == [(2, 2), (2, 2)] and list(com.kolory) == [(2, 2)]
    poz2 = ex.pozycja("412", "Probna 412 kor", sesja_pieca_id=SESJA)
    com.odrzuc_zapis = EX.PONOWIENIA_ZAPISU  # wszystkie proby odrzucone
    with pytest.raises(EX.BladExcela, match=f"po {EX.PONOWIENIA_ZAPISU} probach"):
        ex.zatwierdz(poz2, OSOBA)
    assert com.proby[2:] == [(3, 2)] * EX.PONOWIENIA_ZAPISU and (3, 2) not in com.kolory and _log(tmp_path)[-1]["wynik"] == "blad"


def test_b1_wiersz_zmieniony_zaraz_po_zapisie_komunikat_i_blad(tmp_path):
    app = _aplikacja()
    ex = _excel_com(tmp_path, app)
    com = app.Workbooks[1].Worksheets("2026")
    poz = ex.pozycja("3263", "Testowski 3263 zs", sesja_pieca_id=SESJA)
    com.po_zapisie = lambda: com.wstaw_wiersz(2, WIERSZ_INNY)  # wspoledytor wstawia wiersz tuz po zapisie koloru
    with pytest.raises(EX.BladExcela, match="sprawdz recznie"):
        ex.zatwierdz(poz, OSOBA)
    assert poz.zalatwiona and _log(tmp_path)[-1]["wynik"] == "blad"  # bez drugiego zapisu
    with pytest.raises(EX.BladExcela, match="zalatwiona"):
        ex.zatwierdz(poz, OSOBA)
    assert len(com.proby) == 1


def test_r3_p1_czesciowy_sukces_zapisu_bez_falszywego_juz_odhaczone(tmp_path):
    """Runda 3, P1 (proba R2 recenzenta): wywolanie zapisalo kolor i zwrocilo blad, arkusz bez zmian - program odczytuje kolor
    komorki, widzi swoj zapis i po kontroli N-1..N+1 loguje "zapisano" (nie "juz_odhaczone"), bez drugiego wywolania."""
    app = _aplikacja()
    ex = _excel_com(tmp_path, app)
    com = app.Workbooks[1].Worksheets("2026")
    poz = ex.pozycja("3263", "Testowski 3263 zs", sesja_pieca_id=SESJA)
    com.zapisz_i_rzuc = 1
    wpis = ex.zatwierdz(poz, OSOBA)
    assert (wpis["wynik"], wpis["regula"], wpis["wiersz"]) == (EX.WYNIK_ZAPISANO, 2, 2) and poz.zalatwiona
    assert com.proby == [(2, 2)] and list(com.kolory) == [(2, 2)]
    assert [w["wynik"] for w in _log(tmp_path)] == ["zapisano"]


def test_r3_p1_czesciowy_sukces_przy_przesunietych_wierszach_wykryty(tmp_path):
    """Runda 3, P1 (proba R3): wspoledytor wstawia wiersz miedzy kontrola a zapisem, kolor trafia w komorke B innego zlecenia,
    wywolanie zwraca blad - program to wykrywa: "sprawdz recznie", wpis "blad", pozycja zalatwiona, nigdy "nic nie zapisano"."""
    app = _aplikacja()
    ex = _excel_com(tmp_path, app)
    com = app.Workbooks[1].Worksheets("2026")
    poz = ex.pozycja("3263", "Testowski 3263 zs", sesja_pieca_id=SESJA)
    com.przed_zapisem = lambda: com.wstaw_wiersz(2, WIERSZ_INNY)
    com.zapisz_i_rzuc = 1
    with pytest.raises(EX.BladExcela, match="sprawdz recznie") as blad:
        ex.zatwierdz(poz, OSOBA)
    assert "nic nie zapisano" not in str(blad.value)
    assert poz.zalatwiona and _log(tmp_path)[-1]["wynik"] == "blad" and com.proby == [(2, 2)]


def test_r3_p1_blad_zapisu_i_odczytu_koloru_zapis_mogl_dojsc(tmp_path):
    """Runda 3, P1: blad wywolania zapisu i nieudany odczyt koloru (Excel padl) = "zapis mogl dojsc - sprawdz recznie", wpis
    "blad" w logu, pozycja zalatwiona (bez ponowienia), nigdy "nic nie zapisano"."""
    app = _aplikacja()
    ex = _excel_com(tmp_path, app)
    com = app.Workbooks[1].Worksheets("2026")
    poz = ex.pozycja("3263", "Testowski 3263 zs", sesja_pieca_id=SESJA)
    com.zapisz_i_rzuc, com.potem_odczyt_pada = 1, True
    with pytest.raises(EX.BladExcela, match="zapis mogl dojsc") as blad:
        ex.zatwierdz(poz, OSOBA)
    assert "nic nie zapisano" not in str(blad.value) and "sprawdz recznie" in str(blad.value)
    assert poz.zalatwiona and com.proby == [(2, 2)] and _log(tmp_path)[-1]["wynik"] == "blad"


def test_r3_d5_powod_odmowy_zachowany_gdy_log_zawiedzie(tmp_path, monkeypatch):
    ark = _maly([(D3, 51001.0, 3263.0, T)], ((2, ZOLTY),))
    ex = _excel(ark, tmp_path)
    poz = ex.pozycja("3263", T, sesja_pieca_id=SESJA)

    def zajety(_wpis):
        raise PermissionError("plik zajety")

    monkeypatch.setattr(ex, "_dopisz_csv", zajety)
    with pytest.raises(EX.BladExcela, match="inne wypelnienie") as blad:
        ex.zatwierdz(poz, OSOBA, wiersz=2)
    assert "log" in str(blad.value) and _zapisy(ark) == []


def test_d2_rozlacz_zwalnia_obiekty_com_i_laczy_ponownie(tmp_path):
    app = _aplikacja()
    polaczen = []
    ex = _excel_com(tmp_path, app, polaczen)
    ex.odswiez()
    ark = ex.zrodlo()
    assert ark.nazwa == "2026" and polaczen == [1]
    ex.rozlacz()
    assert ark._ws is None and ark._wb is None and ark._app is None  # referencje COM zwolnione
    assert ex.dopasuj("3263", "Testowski 3263 zs").wiersz == 2 and polaczen == [1, 1]


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
    assert gora | srodek <= STDLIB | {"argparse", "random"}


def test_arkusz_syntetyczny_pulapki_i_fikcyjne_nazwy(zestaw):
    ark = zestaw.arkusz
    wiersze = ark.odczytaj(2, 9)
    assert len(wiersze) == 30000 and {len(w) for w in wiersze} == {9}
    assert Counter(q.pulapka for q in zestaw.zapytania) == {p: n for p, (n, _) in AS.PULAPKI.items()}
    assert Counter(q.klasa for q in zestaw.zapytania) == {J: 110, Z: 19, W: 71}
    assert all(N.kuweta(q.folder) == q.kuweta for q in zestaw.zapytania)  # kuweta jak z indeksu (A4)
    c = [w[2] for w in wiersze]
    h = [w[7] for w in wiersze]
    assert sum(1 for v in c if isinstance(v, str) and v.startswith("0")) > 50  # zera wiodace
    assert sum(1 for v in h if not v) > 500 and sum(1 for v in h if isinstance(v, str) and v[1:2] == ".") > 200  # puste H, inicjaly
    assert sum(1 for w in wiersze if w[8] == "reklamacja") > 10 and zestaw.liczniki["zielonych_b"] > 25000
    po_kuwecie = Counter(EX.norm_kuweta(v) for v in c)
    assert all(po_kuwecie[q.kuweta] >= 3 for q in zestaw.zapytania if q.pulapka == "ta_sama_kuweta_inne_daty")
    assert sum(1 for q in zestaw.zapytania if q.kuweta and q.kuweta[0].isdigit() and po_kuwecie[q.kuweta] >= 2) > 100  # kuweta w roznych datach
    # P6: przypadki P1 i P3 sa w arkuszu (dopisane po odczycie: 4, numery za ostatnim wierszem bazowym)
    assert [q.wiersz for q in zestaw.zapytania if q.pulapka == "dopisane_po_odczycie"] == [30002, 30003, 30004, 30005]
    assert {q.pulapka for q in zestaw.zapytania} >= {"niewpisane_stary_pusty_h", "reklamacja_inne_h", "prywatne_kolizja_b"}
    tekst = " ".join(str(v) for w in wiersze for v in (w[7], w[3])).lower() + " ".join(q.folder for q in zestaw.zapytania).lower()
    for prawdziwe in ("kowalsk", "nowak", "wisniewsk", "wojcik", "kowalczyk", "kaminsk", "lewandowsk", "zielinsk", "szymansk", "wozniak"):
        assert prawdziwe not in tekst
    druga = AS.zbuduj()
    assert druga.arkusz.zrzut() == ark.zrzut() and [vars(q) for q in druga.zapytania] == [vars(q) for q in zestaw.zapytania]
    assert druga.dopisania == zestaw.dopisania
