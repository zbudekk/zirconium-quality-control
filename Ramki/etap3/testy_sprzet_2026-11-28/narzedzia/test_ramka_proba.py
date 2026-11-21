"""Testy narzedzia ramka_proba.py (E3-S1) na atrapie ramki programu (127.0.0.1, port losowy). Pisza tylko do tmp_path.

Uruchomienie (katalog Ramki/stanowisko):
    python -m pytest ../etap3/testy_sprzet_2026-11-28/narzedzia -q -p no:cacheprovider
"""
from __future__ import annotations

import sys
import threading
import time
from pathlib import Path

STANOWISKO = Path(__file__).resolve().parents[3] / "stanowisko"
for _p in (STANOWISKO, STANOWISKO / "narzedzia", Path(__file__).resolve().parent):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import stanowisko  # noqa: E402, F401, I001 - przed innymi pakietami (E3-A11w)

import pytest  # noqa: E402

import ramka_proba as RP  # noqa: E402
from atrapa_ramki import uruchom_atrape  # noqa: E402
from ramka import kalibracja as K  # noqa: E402
from ramka import obraz  # noqa: E402

MODELE = STANOWISKO / "modele_plytek"


@pytest.fixture(params=["W", "P"])
def ramka(request):
    program, atrapa = uruchom_atrape(request.param, port=0)
    port = program.serwer.server_address[1]
    yield request.param, program, atrapa, RP.Ramka("127.0.0.1", port)
    program.zatrzymaj()


def _czekaj(warunek, limit=3.0):
    t0 = time.time()
    while time.time() - t0 < limit:
        if warunek():
            return True
        time.sleep(0.01)
    return False


def _swieci(atrapa, blok, kolor) -> bool:
    x, y, w, h = blok
    return all(atrapa.klatka.piksel(xx, yy) == obraz.KOLORY[kolor] for yy in range(y, y + h) for xx in range(x, x + w))


def test_stan_wypisuje_role_i_plytke(ramka):
    rola, program, atrapa, r = ramka
    nr = RP.RODZINY[rola][0]
    atrapa.poloz_plytke(nr)
    assert _czekaj(lambda: r.stan()["plytka"] == nr and r.stan()["plytka_pewna"])
    linie = []
    assert RP.polecenie_stan(r, linie.append) == 0
    tekst = "\n".join(linie)
    assert "RAMKA ODPOWIADA" in tekst and f"plytka na ramce: {nr}" in tekst and ("wieczorna" if rola == "W" else "poranna") in tekst


def test_brak_polaczenia_kod_2(capsys):
    assert RP.main(["stan", "--adres", "127.0.0.1", "--port", "9"]) == 2
    assert "BRAK POLACZENIA" in capsys.readouterr().out


def test_test_led_przelacza_ramke(ramka):
    rola, program, atrapa, r = ramka
    linie = []
    assert RP.polecenie_test_led(r, linie.append) == 0
    assert r.stan()["tryb"] == "test_led" and "TEST DIOD WYSLANY" in linie[0]


def test_plytki_zapisuje_kazda_zmiane(ramka, tmp_path):
    rola, program, atrapa, r = ramka
    a, obca = RP.RODZINY[rola][1], RP.RODZINY["P" if rola == "W" else "W"][0]

    def technik():
        for n in (a, 0, obca, 0):
            time.sleep(0.25)
            atrapa.poloz_plytke(n)

    threading.Thread(target=technik, daemon=True).start()
    linie = []
    assert RP.polecenie_plytki(r, 2.5, tmp_path, linie.append) == 0  # katalog: plik plytki_<data>_<godzina>.csv
    (plik,) = list(tmp_path.glob("plytki_*.csv"))
    wiersze = [w.split(";") for w in plik.read_text(encoding="ascii").splitlines()]
    assert wiersze[0][2] == "zdarzenie"
    zmiany = [(w[3], w[4]) for w in wiersze[1:] if w[2] == "plytka"]
    assert zmiany == [("0", str(a)), (str(a), "0"), ("0", str(obca)), (str(obca), "0")]
    assert [w[5] for w in wiersze[1:] if w[2] == "plytka"][2] == "NUMER SPOZA TEJ RAMKI"
    assert "Zmian odczytu plytki: 4" in linie[-1]


def test_gniazda_wszystkie_swieca_w_swoich_blokach(ramka, tmp_path):
    rola, program, atrapa, r = ramka
    uklad, nr = ("wieczorna", 2) if rola == "W" else ("poranna", 5)
    atrapa.poloz_plytke(nr)
    assert _czekaj(lambda: r.stan()["plytka"] == nr and r.stan()["plytka_pewna"])
    bloki = RP.bloki_ukladu(K.domyslna(MODELE), rola, uklad)
    widziane = {}

    def pytaj(_tekst):
        assert _czekaj(lambda: r.stan()["tryb"] == "wynik")
        time.sleep(0.1)
        widziane["dobre"] = sum(_swieci(atrapa, b, RP.KOLORY_NA_ZMIANE[i % 4]) for i, (_, b) in enumerate(bloki))
        return "wszystko dobrze"

    plik = tmp_path / "g.csv"
    assert RP.polecenie_gniazda(r, uklad, None, MODELE, True, (0, 0), plik, lambda *_: None, pytaj) == 0
    assert widziane["dobre"] == len(bloki) == (19 if rola == "W" else 24)
    assert r.stan()["plan_id"] is None  # na koniec ramka zgaszona
    assert "wszystko dobrze" in plik.read_text(encoding="ascii")


def test_gniazda_po_kolei_jedno_naraz_z_przesunieciem(ramka, tmp_path):
    rola, program, atrapa, r = ramka
    uklad, nr = ("wieczorna", 1) if rola == "W" else ("poranna", 4)
    atrapa.poloz_plytke(nr)
    assert _czekaj(lambda: r.stan()["plytka"] == nr and r.stan()["plytka_pewna"])
    bloki = RP.bloki_ukladu(K.domyslna(MODELE), rola, uklad, (1, -1))
    stan = {"i": 0, "dobre": 0, "inne_ciemne": 0}

    def pytaj(_tekst):
        g, b = bloki[stan["i"]]
        assert _czekaj(lambda: _swieci(atrapa, b, "bialy"))
        stan["dobre"] += 1
        inne = [bb for gg, bb in bloki if gg != g]
        stan["inne_ciemne"] += all(atrapa.klatka.piksel(bb[0], bb[1]) == (0, 0, 0) for bb in inne)
        stan["i"] += 1
        if stan["i"] == 4:  # zapis wiersz po wierszu: 3 obserwacje sa juz w pliku, zanim narzedzie skonczy
            stan["w_trakcie"] = len(plik.read_text(encoding="ascii").splitlines()) - 1
        return "k" if stan["i"] == 5 else ("" if stan["i"] != 2 else "za bardzo w lewo")

    plik = tmp_path / "g.csv"
    assert RP.polecenie_gniazda(r, uklad, None, MODELE, False, (1, -1), plik, lambda *_: None, pytaj) == 0
    assert stan["dobre"] == 5 and stan["inne_ciemne"] == 5 and stan["w_trakcie"] == 3
    wiersze = [w.split(";") for w in plik.read_text(encoding="ascii").splitlines()][1:]
    assert len(wiersze) == 4 and [w[8] for w in wiersze] == ["ok", "za bardzo w lewo", "ok", "ok"]
    assert all(w[6] == "1" and w[7] == "-1" for w in wiersze)


def test_gniazda_bez_plytki_i_zly_uklad(ramka):
    rola, program, atrapa, r = ramka
    linie = []
    assert RP.polecenie_gniazda(r, "wieczorna" if rola == "W" else "poranna", None, MODELE, True, (0, 0), None, linie.append, lambda _t: "") == 1
    assert "NIE LEZY PLYTKA" in linie[-1]
    assert RP.polecenie_gniazda(r, "okragla_wieczorna", None, MODELE, True, (0, 0), None, linie.append, lambda _t: "") == 1
    assert "BRAK ukladu" in linie[-1]
    atrapa.poloz_plytke(RP.RODZINY[rola][0])
    assert _czekaj(lambda: r.stan()["plytka"] == RP.RODZINY[rola][0] and r.stan()["plytka_pewna"])
    assert RP.polecenie_gniazda(r, "wieczorna" if rola == "W" else "poranna", None, MODELE, True, (40, 0), None, linie.append, lambda _t: "") == 1
    assert "PRZESUNIECIE" in linie[-1]


def test_dwa_uruchomienia_pod_rzad_nie_koliduja(ramka, tmp_path):
    """Proba na instalacji (21.11): drugie uruchomienie w tej samej sekundzie dawalo 409 konflikt_wersji (ten sam plan_id)."""
    rola, program, atrapa, r = ramka
    uklad, nr = ("wieczorna", 3) if rola == "W" else ("poranna", 6)
    atrapa.poloz_plytke(nr)
    assert _czekaj(lambda: r.stan()["plytka"] == nr and r.stan()["plytka_pewna"])
    for _ in range(3):
        linie = []
        assert RP.polecenie_gniazda(r, uklad, None, MODELE, True, (0, 0), tmp_path, linie.append, lambda _t: "widze") == 0
        assert not any("ODMOWILA" in x for x in linie)
    assert len(list(tmp_path.glob("gniazda_*.csv"))) == 3  # zapis w tej samej sekundzie nie nadpisuje poprzedniego pliku


def test_klawiatura_ramki_porannej_piec_rodzajow_zdarzen(ramka, tmp_path):
    rola, program, atrapa, r = ramka
    linie = []
    if rola == "W":
        assert RP.polecenie_klawiatura(r, "poranna", None, MODELE, 1.0, None, linie.append) == 1
        assert "tylko ramka poranna" in linie[-1]
        return
    assert RP.polecenie_klawiatura(r, "poranna", None, MODELE, 1.0, None, linie.append) == 1  # bez plytki
    atrapa.poloz_plytke(5)
    assert _czekaj(lambda: r.stan()["plytka"] == 5 and r.stan()["plytka_pewna"])

    def technik():
        assert _czekaj(lambda: r.stan()["tryb"] == "wynik")
        for k in ("enter", "backspace", "2", "2", "2", "2", "enter", "9", "enter", "zamknij_piec", "enter"):
            time.sleep(0.12)
            atrapa.nacisnij(k)

    threading.Thread(target=technik, daemon=True).start()
    assert RP.polecenie_klawiatura(r, "poranna", None, MODELE, 8.0, tmp_path, linie.append) == 0
    (plik,) = list(tmp_path.glob("klawiatura_*.csv"))
    wiersze = [w.split(";") for w in plik.read_text(encoding="ascii").splitlines()][1:]
    assert [w[1] for w in wiersze] == ["potwierdzenie", "cofniecie", "kuweta_wybrana", "kuweta_nieznana", "zamknij_piec"]
    assert wiersze[2][2] == "2222" and wiersze[3][2] == "9"
    assert "rodzaje: 5 z 5" in linie[-1] and r.stan()["plan_id"] is None
