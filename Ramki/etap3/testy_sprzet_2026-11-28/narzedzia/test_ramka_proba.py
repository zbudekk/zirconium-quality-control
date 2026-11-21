"""Testy narzedzia ramka_proba.py (E3-S1 / E3-S2a) na atrapie ramki programu (127.0.0.1, port losowy). Pisza tylko do tmp_path.

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
    assert RP.polecenie_gniazda(r, "nie_ma_takiego_rodzaju", None, MODELE, True, (0, 0), None, linie.append, lambda _t: "") == 1  # E3-S2a: bez zalozenia, ze kalibracja nie zna plytek okraglych (po paczce O2 zna)
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


# ----------------------------------------------------------------------------- E3-S2a: klucz ramki, U9 (b, c), U13-U16
KLUCZ = "klucz-probny-0123456789"
ZLY = "zly-klucz-000000000000"


@pytest.fixture
def z_kluczem(monkeypatch):
    """Atrapa ramki wieczornej Z KLUCZEM (jak po instalacji skryptem ramka/rpi/zainstaluj_ramke.sh)."""
    monkeypatch.delenv("RAMKA_KLUCZ", raising=False)
    program, atrapa = uruchom_atrape("W", port=0, klucz=KLUCZ)
    yield program.serwer.server_address[1], program, atrapa
    program.zatrzymaj()


def test_klucz_brak_i_zly_daja_kod_5_dobry_dziala(z_kluczem, tmp_path, capsys):
    """Recenzja PR #54 proba 13 (U13): bylo 'BRAK POLACZENIA ... podaj --klucz' + rada 'sprawdz, czy ramka ma prad'."""
    port = z_kluczem[0]
    wspolne = ["--adres", "127.0.0.1", "--port", str(port), "--plik-klucza", str(tmp_path / "klucz_ramki.txt")]
    assert RP.main(["stan", *wspolne]) == 5
    tekst = capsys.readouterr().out
    assert "RAMKA ODPOWIADA, ale wymaga klucza (odpowiedz 401): nie podano klucza" in tekst
    assert "/etc/ramka/ramka.json" in tekst and "pozycja 7" in tekst
    assert "BRAK POLACZENIA" not in tekst and "ramka ma prad" not in tekst
    assert RP.main(["stan", *wspolne, "--klucz", ZLY]) == 5
    tekst = capsys.readouterr().out
    assert "podany klucz NIE pasuje" in tekst and "zly-..." in tekst and "opcja --klucz" in tekst and ZLY not in tekst
    assert RP.main(["test-led", *wspolne]) == 5 and "wymaga klucza" in capsys.readouterr().out
    assert RP.main(["plytki", *wspolne, "--czas", "0.2"]) == 5 and RP.main(["uklady", *wspolne]) == 5
    capsys.readouterr()
    assert RP.main(["stan", *wspolne, "--klucz", KLUCZ]) == 0
    tekst = capsys.readouterr().out
    assert "RAMKA ODPOWIADA (" in tekst and "wymaga klucza" not in tekst and KLUCZ not in tekst
    assert RP.main(["test-led", *wspolne, "--klucz", KLUCZ]) == 0 and "TEST DIOD WYSLANY" in capsys.readouterr().out


def test_klucz_ze_zmiennej_z_pliku_obok_narzedzi_i_z_ustawien(z_kluczem, tmp_path, monkeypatch, capsys):
    port = z_kluczem[0]
    plik, ust = tmp_path / "klucz_ramki.txt", tmp_path / "ustawienia.toml"
    wspolne = ["stan", "--adres", "127.0.0.1", "--port", str(port), "--plik-klucza", str(plik)]
    monkeypatch.setenv("RAMKA_KLUCZ", KLUCZ)
    assert RP.main(wspolne) == 0                                      # zmienna srodowiska
    monkeypatch.delenv("RAMKA_KLUCZ")
    assert RP.main(wspolne) == 5
    plik.write_text(f"# klucze\nramka-p.local {ZLY}\n127.0.0.1 {KLUCZ}\n", encoding="ascii")
    assert RP.main(wspolne) == 0                                      # plik: wiersz ADRES KLUCZ tej ramki
    plik.write_text(f"ramka-p.local {ZLY}\n", encoding="ascii")
    assert RP.main(wspolne) == 5                                      # klucz innej ramki nie jest brany
    plik.write_text(f"{KLUCZ}\n", encoding="ascii")
    assert RP.main(wspolne) == 0                                      # plik: sam KLUCZ = dla kazdej ramki
    plik.unlink()
    ust.write_text(f'[ramki]\nport = 8765\nklucz = "{KLUCZ}"\n', encoding="utf-8")
    assert RP.main([*wspolne, "--ustawienia", str(ust)]) == 0         # [ramki] klucz z ustawien programu
    assert RP.main([*wspolne, "--ustawienia", str(ust), "--klucz", ZLY]) == 5   # opcja ma pierwszenstwo
    assert RP.main([*wspolne, "--ustawienia", str(tmp_path / "nie_ma.toml")]) == 5
    capsys.readouterr()
    srod = {"RAMKA_KLUCZ": "ze-zmiennej"}
    plik.write_text("z-pliku\n", encoding="ascii")
    assert RP.znajdz_klucz("a", "z-opcji", plik, ust, srod) == ("z-opcji", "opcja --klucz")
    assert RP.znajdz_klucz("a", None, plik, ust, srod) == ("ze-zmiennej", "zmienna RAMKA_KLUCZ")
    assert RP.znajdz_klucz("a", None, plik, ust, {}) == ("z-pliku", "plik klucz_ramki.txt")
    assert RP.znajdz_klucz("a", None, tmp_path / "brak.txt", ust, {}) == (KLUCZ, "plik ustawien ustawienia.toml")
    assert RP.znajdz_klucz("a", None, None, None, {}) == ("", "brak")


def test_polecenie_klucz_pyta_raz_i_zapisuje_tylko_dobry(z_kluczem, tmp_path, capsys):
    port = z_kluczem[0]
    plik = tmp_path / "klucz_ramki.txt"
    linie = []
    assert RP.polecenie_klucz("127.0.0.1", port, plik, linie.append, lambda _t: ZLY) == 5
    assert not plik.exists() and "ZLY KLUCZ (zly-...)" in linie[-1] and "nic nie zapisano" in linie[-1]
    assert RP.polecenie_klucz("127.0.0.1", port, plik, linie.append, lambda _t: "") == 5 and not plik.exists()
    pytania = []
    assert RP.polecenie_klucz("127.0.0.1", port, plik, linie.append, lambda t: pytania.append(t) or f'  "{KLUCZ}" ') == 0
    assert len(pytania) == 1 and f"127.0.0.1 {KLUCZ}" in plik.read_text(encoding="ascii").splitlines()
    assert "KLUCZ DOBRY (kluc...)" in linie[-1] and KLUCZ not in "\n".join(linie)   # klucza nie wypisujemy w calosci
    assert "/etc/ramka/ramka.json" in "\n".join(linie)
    assert RP.main(["stan", "--adres", "127.0.0.1", "--port", str(port), "--plik-klucza", str(plik)]) == 0   # potem juz bez pytania
    assert "RAMKA ODPOWIADA (" in capsys.readouterr().out
    RP.zapisz_klucz(plik, "ramka-p.local", "inny-klucz-1111111111")
    RP.zapisz_klucz(plik, "127.0.0.1", KLUCZ + "x")
    wiersze = [w for w in plik.read_text(encoding="ascii").splitlines() if not w.startswith("#")]
    assert wiersze == ["ramka-p.local inny-klucz-1111111111", f"127.0.0.1 {KLUCZ}x"]


def test_n10_klucz_z_litera_spoza_ascii_to_zly_klucz_a_nie_wyjatek(z_kluczem, tmp_path):
    """Recenzja runda 2, N10: klucz z polska litera (prawy Alt) konczyl sie wyjatkiem UnicodeEncodeError zamiast 'ZLY KLUCZ'."""
    port = z_kluczem[0]
    plik = tmp_path / "klucz_ramki.txt"
    linie = []
    assert RP.polecenie_klucz("127.0.0.1", port, plik, linie.append, lambda _t: KLUCZ[:-1] + chr(261)) == 5
    assert not plik.exists() and "ZLY KLUCZ" in linie[-1] and "bez polskich znakow" in linie[-1] and "nic nie zapisano" in linie[-1]
    assert "\n".join(linie).isascii()


def test_polecenie_klucz_na_ramce_bez_klucza_o_nic_nie_pyta(ramka, tmp_path):
    rola, program, atrapa, r = ramka
    linie = []
    port = int(r.baza.rsplit(":", 1)[1])
    assert RP.polecenie_klucz("127.0.0.1", port, tmp_path / "k.txt", linie.append, lambda _t: pytest.fail("pytanie o klucz")) == 0
    assert "NIE wymaga klucza" in linie[-1] and not (tmp_path / "k.txt").exists()


def test_adres_ze_spacja_daje_zdanie_po_polsku(capsys):
    assert RP.main(["stan", "--adres", "ramka w"]) == 1
    assert "ZLY ADRES RAMKI" in capsys.readouterr().out


def test_u9_plan_jest_podtrzymywany_dluzej_niz_jego_waznosc(ramka, tmp_path):
    """Recenzja PR #54 (U9 b, wstrzykniecie M4): usuniecie watku podtrzymania nie bylo lapane. Waznosc planu skrocona do 2 s,
    czlowiek 'mysli' 5 s - gniazda maja dalej swiecic."""
    rola, program, atrapa, r = ramka
    uklad, nr = ("wieczorna", 2) if rola == "W" else ("poranna", 5)
    atrapa.poloz_plytke(nr)
    assert _czekaj(lambda: r.stan()["plytka"] == nr and r.stan()["plytka_pewna"])
    r.wazny_s = {"W": 2, "P": 2}
    r.podtrzymanie_s = 0.4
    bloki = RP.bloki_ukladu(K.domyslna(MODELE), rola, uklad)
    widziane = {}

    def pytaj(_tekst):
        assert _czekaj(lambda: r.stan()["tryb"] == "wynik")
        widziane["na_poczatku"] = sum(_swieci(atrapa, b, RP.KOLORY_NA_ZMIANE[i % 4]) for i, (_, b) in enumerate(bloki))
        t0 = time.time()
        while time.time() - t0 < 5.0:   # bez wlasnych zapytan do ramki: podtrzymuje tylko watek narzedzia
            time.sleep(0.1)
        widziane["po_5_s"] = sum(_swieci(atrapa, b, RP.KOLORY_NA_ZMIANE[i % 4]) for i, (_, b) in enumerate(bloki))
        return "swieci"

    linie = []
    assert RP.polecenie_gniazda(r, uklad, None, MODELE, True, (0, 0), tmp_path / "g.csv", linie.append, pytaj) == 0
    assert widziane["na_poczatku"] == len(bloki) and widziane["po_5_s"] == len(bloki)
    assert "Ramka zgaszona." in linie[-1] and r.stan()["plan_id"] is None


def test_u9_u14_ramka_zajeta_przez_inny_komputer(ramka, tmp_path):
    """Recenzja PR #54 proba 15 (U9 c, U14): 19 odmow pod rzad i 'Ramka zgaszona'. Teraz: jedna odmowa, rada, plan obcego nietkniety."""
    rola, program, atrapa, r = ramka
    uklad, nr = ("wieczorna", 1) if rola == "W" else ("poranna", 4)
    atrapa.poloz_plytke(nr)
    assert _czekaj(lambda: r.stan()["plytka"] == nr and r.stan()["plytka_pewna"])
    bloki = RP.bloki_ukladu(K.domyslna(MODELE), rola, uklad)
    obcy = RP.Ramka("127.0.0.1", int(r.baza.rsplit(":", 1)[1]))
    obcy.laptop_id = "inny-komputer-1"
    kod, _, _ = obcy.wyslij_plan("plan-obcy-1", 1, rola, nr, [{"id": bloki[0][0], "px": bloki[0][1], "kolor": "zielony"}])
    assert kod == 200 and r.stan()["plan_id"] == "plan-obcy-1"
    linie, pytania, plik = [], [], tmp_path / "g.csv"
    assert RP.polecenie_gniazda(r, uklad, None, MODELE, False, (0, 0), plik, linie.append, lambda t: pytania.append(t) or "") == 1
    tekst = "\n".join(linie)
    assert tekst.count("RAMKA ODMOWILA") == 1 and "zamknij program Stanowisko" in tekst and not pytania
    assert "Ramka zgaszona" not in tekst and "Ramki NIE zgaszono" in tekst
    wiersze = plik.read_text(encoding="ascii").splitlines()[1:]
    assert len(wiersze) == 1 and "ODMOWA 409 inny komputer" in wiersze[0]
    linie.clear()
    assert RP.polecenie_gniazda(r, uklad, None, MODELE, True, (0, 0), None, linie.append, lambda t: pytania.append(t) or "") == 1
    assert "inny_laptop" in linie[-2] and "zamknij program Stanowisko" in linie[-2] and "Ramka zgaszona" not in linie[-1] and not pytania
    linie.clear()
    assert RP.polecenie_test_led(r, linie.append) == 1 and "zamknij program Stanowisko" in linie[-1]
    assert r.stan()["plan_id"] == "plan-obcy-1"   # plan drugiego komputera zostal


def test_u15_plytka_zdjeta_w_trakcie_przerywa_probe(ramka, tmp_path):
    """Recenzja PR #54 proba 17 (U15): po zdjeciu plytki narzedzie pytalo dalej i zapisywalo 'ok'."""
    rola, program, atrapa, r = ramka
    uklad, nr = ("wieczorna", 3) if rola == "W" else ("poranna", 6)
    atrapa.poloz_plytke(nr)
    assert _czekaj(lambda: r.stan()["plytka"] == nr and r.stan()["plytka_pewna"])
    licznik = {"n": 0}

    def pytaj(_tekst):
        licznik["n"] += 1
        if licznik["n"] == 2:
            atrapa.poloz_plytke(0)
            assert _czekaj(lambda: r.stan()["plytka"] == 0)
        return ""

    linie, plik = [], tmp_path / "g.csv"
    assert RP.polecenie_gniazda(r, uklad, None, MODELE, False, (0, 0), plik, linie.append, pytaj) == 1
    obserwacje = [w.split(";")[8] for w in plik.read_text(encoding="ascii").splitlines()[1:]]
    assert licznik["n"] == 2 and obserwacje[:2] == ["ok", "ok"] and obserwacje[2].startswith("BRAK PLYTKI") and len(obserwacje) == 3
    assert any(f"RAMKA NIE CZYTA JUZ PLYTKI nr {nr}" in x for x in linie)


def test_u16_uklady_ramki_z_kalibracji_i_uklad_domyslny(ramka, capsys):
    rola, program, atrapa, r = ramka
    linie = []
    assert RP.polecenie_uklady(r, None, MODELE, linie.append) == 0
    znane = sorted(K.domyslna(MODELE)["ramki"][rola])
    domyslny = "wieczorna" if rola == "W" else "poranna"
    assert linie[0] == f"Ramka {rola} zna {len(znane)} rodzajow plytek: {', '.join(znane)}" and linie[1] == f"DOMYSLNY: {domyslny}"
    assert domyslny in znane and RP.uklad_domyslny(rola) == domyslny
    port = r.baza.rsplit(":", 1)[1]   # `--uklad auto` (sam Enter w menu) = uklad domyslny dla roli tej ramki
    assert RP.main(["gniazda", "--adres", "127.0.0.1", "--port", port, "--uklad", "auto", "--wszystkie", "--modele", str(MODELE)]) == 1
    assert "NA RAMCE NIE LEZY PLYTKA TEJ RAMKI" in capsys.readouterr().out
