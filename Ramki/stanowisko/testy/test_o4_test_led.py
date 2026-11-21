"""E3-O4 punkt 3: `python -m ramka.test_led` czyta plik konfiguracji ramki tak samo jak `python -m ramka`.

Zrodlo: raport E3-S1 (POTRZEBUJE 4): `--sprzet rpi` tworzyl sprzet z wartosciami domyslnymi (pomijal `obrot`,
`lustro`, `jasnosc`, `piny_halla`, `mapowanie` z pliku ramki), opcji `--konfiguracja` nie bylo, a brak biblioteki
sprzetu konczyl sie sladem wyjatku (Traceback, kod 1) zamiast komunikatu i kodu 2.
Prawdziwej matrycy tu nie ma: klase `SprzetRpi` zastepuje atrapa, ktora zapisuje argumenty konstruktora.
"""
from __future__ import annotations

import json
import secrets
import subprocess
import sys
from pathlib import Path

import pytest

STANOWISKO = Path(__file__).resolve().parent.parent
if str(STANOWISKO) not in sys.path:
    sys.path.insert(0, str(STANOWISKO))

from ramka import kalibracja, sprzet_rpi, test_led  # noqa: E402
from ramka import program as program_ramki  # noqa: E402
from ramka.sprzet_atrapa import SprzetAtrapa  # noqa: E402

MODELE = STANOWISKO / "modele_plytek"
POLA_SPRZETU = ("piny_halla", "jasnosc", "obrot", "lustro", "mapowanie", "spowolnienie_gpio", "klawisz_zamknij_piec")


class RpiUdawany(SprzetAtrapa):
    """Zamiast `sprzet_rpi.SprzetRpi`: pamieta argumenty konstruktora, klatki zbiera jak atrapa."""
    utworzone: list = []

    def __init__(self, **argumenty):
        super().__init__()
        self.argumenty = argumenty
        RpiUdawany.utworzone.append(self)


@pytest.fixture
def rpi(monkeypatch):
    RpiUdawany.utworzone = []
    monkeypatch.setattr(sprzet_rpi, "SprzetRpi", RpiUdawany)
    return RpiUdawany


@pytest.fixture
def plik_kal(tmp_path):
    wyj = tmp_path / "kal.json"
    assert kalibracja.main(["--domyslna", "--modele", str(MODELE), "--wyjscie", str(wyj)]) == 0
    return wyj


def _konfiguracja(tmp_path, **pola) -> Path:
    plik = tmp_path / "ramka.json"
    plik.write_text(json.dumps(pola), encoding="ascii")
    return plik


def test_test_led_ma_opcje_konfiguracja_jak_program_ramki(capsys):
    for wejscie in (test_led.main, program_ramki.parsuj_argumenty):
        with pytest.raises(SystemExit) as e:
            wejscie(["--help"])
        assert e.value.code == 0
        assert "--konfiguracja" in capsys.readouterr().out, wejscie


def test_test_led_rpi_czyta_plik_konfiguracji_ramki(tmp_path, plik_kal, rpi, capsys):
    """Pola sprzetu z pliku ramki trafiaja do matrycy testu tak samo jak do programu ramki (`utworz_sprzet`)."""
    plik = _konfiguracja(tmp_path, rola="W", sprzet="rpi", host="0.0.0.0", klucz=secrets.token_hex(16), obrot=180, lustro=True,
                         jasnosc=35, piny_halla=[5, 6, 7], mapowanie="adafruit-hat", spowolnienie_gpio=2,
                         klawisz_zamknij_piec="KEY_KPPLUS")
    kod = test_led.main(["--kalibracja", str(plik_kal), "--uklad", "wieczorna", "--czas", "0", "--konfiguracja", str(plik)])
    assert kod == 0
    assert len(rpi.utworzone) == 1
    test = rpi.utworzone[0]
    assert test.argumenty == {"rola": "W", "piny_halla": (5, 6, 7), "jasnosc": 35, "obrot": 180, "lustro": True,
                              "mapowanie": "adafruit-hat", "spowolnienie_gpio": 2, "klawisz_zamknij_piec": "KEY_KPPLUS",
                              "z_klawiatura": False}
    # to samo dostaje program ramki z tego samego pliku (test LED tylko nie czyta klawiatury)
    konf = program_ramki.konfiguracja_z_argumentow(program_ramki.parsuj_argumenty(["--konfiguracja", str(plik)]))
    programowy = program_ramki.utworz_sprzet(konf)
    assert {k: v for k, v in test.argumenty.items() if k != "z_klawiatura"} == programowy.argumenty
    assert set(POLA_SPRZETU) <= set(test.argumenty)
    # rola i sprzet wziete z pliku: 19 gniazd ukladu wieczornego ramki W + klatka gaszaca, matryca zamknieta
    assert len(test.historia) == 19 + 1 and test.zamknieta
    assert "19 gniazd" in capsys.readouterr().out


def test_test_led_wiersz_polecen_ma_pierwszenstwo_przed_plikiem(tmp_path, plik_kal, rpi, capsys):
    plik = _konfiguracja(tmp_path, rola="W", sprzet="rpi", obrot=90)
    # --rola P przy pliku ramki W: jak w `python -m ramka` wygrywa wiersz polecen
    assert test_led.main(["--kalibracja", str(plik_kal), "--rola", "P", "--uklad", "poranna", "--czas", "0",
                          "--konfiguracja", str(plik)]) == 0
    assert rpi.utworzone[-1].argumenty["rola"] == "P" and rpi.utworzone[-1].argumenty["obrot"] == 90
    assert "24 gniazd" in capsys.readouterr().out
    # --sprzet atrapa przy pliku ze sprzetem rpi: matrycy nikt nie otwiera
    ile = len(rpi.utworzone)
    assert test_led.main(["--kalibracja", str(plik_kal), "--uklad", "wieczorna", "--sprzet", "atrapa",
                          "--konfiguracja", str(plik)]) == 0
    assert len(rpi.utworzone) == ile


def test_test_led_bez_pliku_konfiguracji_wartosci_domyslne_z_kodu(plik_kal, rpi, capsys):
    domyslna = program_ramki.Konfiguracja()
    assert test_led.main(["--kalibracja", str(plik_kal), "--rola", "P", "--uklad", "poranna", "--czas", "0", "--sprzet", "rpi"]) == 0
    argumenty = rpi.utworzone[0].argumenty
    for pole in POLA_SPRZETU:
        assert argumenty[pole] == getattr(domyslna, pole), pole
    wyjscie = capsys.readouterr()
    assert "24 gniazd" in wyjscie.out
    assert "--konfiguracja" in wyjscie.err  # uwaga dla czlowieka: matryca testu moze byc ustawiona inaczej niz w usludze
    # atrapa bez opcji - jak przed zmiana (bez uwagi, bez matrycy)
    assert test_led.main(["--kalibracja", str(plik_kal), "--rola", "W", "--uklad", "wieczorna"]) == 0
    wyjscie = capsys.readouterr()
    assert "19 gniazd" in wyjscie.out and wyjscie.err == "" and len(rpi.utworzone) == 1


def test_test_led_brak_biblioteki_sprzetu_komunikat_i_kod_2(tmp_path, plik_kal, monkeypatch, capsys):
    monkeypatch.setitem(sys.modules, "rgbmatrix", None)  # import konczy sie ImportError takze tam, gdzie biblioteka jest
    kod = test_led.main(["--kalibracja", str(plik_kal), "--rola", "W", "--uklad", "wieczorna", "--sprzet", "rpi"])
    blad = capsys.readouterr().err
    assert kod == 2
    assert "sprzet niedostepny" in blad and "brak biblioteki rgbmatrix" in blad
    # to samo przez plik konfiguracji (tak uruchamia sie test na ramce)
    plik = _konfiguracja(tmp_path, rola="W", sprzet="rpi")
    assert test_led.main(["--kalibracja", str(plik_kal), "--uklad", "wieczorna", "--konfiguracja", str(plik)]) == 2
    assert "brak biblioteki rgbmatrix" in capsys.readouterr().err


def test_test_led_brak_biblioteki_w_osobnym_procesie_bez_sladu_wyjatku(plik_kal):
    """Jak w raporcie S1: `python -m ramka.test_led ... --sprzet rpi` na komputerze bez biblioteki matrycy."""
    skrypt = ("import sys\nsys.modules['rgbmatrix'] = None\nimport runpy\n"
              "sys.argv = ['test_led'] + sys.argv[1:]\nrunpy.run_module('ramka.test_led', run_name='__main__')\n")
    r = subprocess.run([sys.executable, "-c", skrypt, "--kalibracja", str(plik_kal), "--rola", "W", "--uklad", "wieczorna",
                        "--sprzet", "rpi"], cwd=STANOWISKO, capture_output=True, text=True, timeout=120)
    assert r.returncode == 2, r.stderr
    assert "Traceback" not in r.stderr and "brak biblioteki rgbmatrix" in r.stderr


def test_test_led_zly_plik_konfiguracji_komunikat_i_kod_1(tmp_path, plik_kal, rpi, capsys):
    brak = tmp_path / "nie_ma.json"
    zly_json = tmp_path / "zly.json"
    zly_json.write_text("{\"rola\": ", encoding="ascii")
    nieznany = _konfiguracja(tmp_path, rola="W", obroty=90)
    for plik in (brak, zly_json, nieznany):
        kod = test_led.main(["--kalibracja", str(plik_kal), "--rola", "W", "--uklad", "wieczorna", "--sprzet", "rpi",
                             "--konfiguracja", str(plik)])
        assert kod == 1, plik.name
        assert "blad: konfiguracja" in capsys.readouterr().err, plik.name
    assert rpi.utworzone == []  # ze zla konfiguracja matrycy nikt nie otwiera


def test_test_led_bez_roli_w_wierszu_i_bez_pliku_blad_skladni(plik_kal, capsys):
    with pytest.raises(SystemExit) as e:
        test_led.main(["--kalibracja", str(plik_kal), "--uklad", "wieczorna"])
    assert e.value.code == 2
    assert "--rola" in capsys.readouterr().err
