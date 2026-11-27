"""E3-R1 (26.11.2026): przelacznik ``[ramki] wlaczone`` - program bez elektroniki ramek (instalacja na pokaz 28.11).

Brak klucza = ``true`` (zachowanie sprzed E3-R1, stare instalacje bez zmian). ``false``: program nie tworzy klientow ramek i nie
probuje sie z nimi laczyc (licznik polaczen na atrapie = 0), pasek stanu pokazuje neutralne "Ramki: wylaczone" (zwykly kolor
tekstu, bez przyciskow ramek), bez komunikatow "ramka nie jest podlaczona / nie odpowiada" w strefie pytan i na liscie bledow
programu. Samokontrola: ``test_samokontrola.py``; instalator: ``test_instalacja_i1.py``. Siec tylko 127.0.0.1, pliki w tmp_path.
"""
from __future__ import annotations

import copy
import logging
import socket
import threading
import time
import tomllib

import pytest

import test_kontroler_api as TK
from test_aplikacja_rano import _qt, ekrany  # noqa: F401 - QApplication offscreen dla modulu (autouse) i fixture okna

from stanowisko import indicate as IND
from stanowisko import kontroler_api as K
from stanowisko import ustawienia as UST
from stanowisko.ui import napisy_rano as NR


class LicznikPolaczen:
    """Atrapa ramki na 127.0.0.1: gniazdo TCP, ktore tylko liczy przyjete polaczenia (kazda proba klienta ramki = +1)."""

    def __init__(self):
        self.gniazdo = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.gniazdo.bind(("127.0.0.1", 0))
        self.gniazdo.listen(16)
        self.gniazdo.settimeout(0.1)
        self.port = self.gniazdo.getsockname()[1]
        self.polaczenia = 0
        self._stop = threading.Event()
        self._watek = threading.Thread(target=self._przyjmuj, daemon=True)
        self._watek.start()

    def _przyjmuj(self) -> None:
        while not self._stop.is_set():
            try:
                pol, _ = self.gniazdo.accept()
            except (TimeoutError, socket.timeout, OSError):
                continue
            self.polaczenia += 1
            pol.close()

    def zamknij(self) -> None:
        self._stop.set()
        self._watek.join(2.0)
        self.gniazdo.close()


@pytest.fixture
def licznik():
    lp = LicznikPolaczen()
    yield lp
    lp.zamknij()


@pytest.fixture
def klienci(monkeypatch):
    """Licznik obiektow ``KlientRamki`` utworzonych w tescie (kazdy klient = watki odpytujace ramke)."""
    utworzone = []
    oryginal = IND.KlientRamki.__init__

    def init(self, *a, **kw):
        utworzone.append(a[0] if a else kw.get("rola"))
        oryginal(self, *a, **kw)

    monkeypatch.setattr(IND.KlientRamki, "__init__", init)
    return utworzone


def ust_z_ramkami(tmp_path, port: int, wlaczone) -> dict:
    """Ustawienia probne programu; ramki W i P na 127.0.0.1:``port``; ``wlaczone`` None = klucza nie ma w slowniku."""
    ust = TK.ustawienia_probne(tmp_path)
    ust["ramki"].update(wieczorna_host="127.0.0.1", poranna_host="127.0.0.1", port=port)
    ust["sciezki"]["kalibracja_ramek"] = (tmp_path / "brak" / "kalibracja_ramek.json").as_posix()
    if wlaczone is None:
        ust["ramki"].pop("wlaczone", None)
    else:
        ust["ramki"]["wlaczone"] = wlaczone
    return ust


def plik_ustawien(tmp_path, wiersz_wlaczone: str | None, nazwa: str = "ustawienia.toml"):
    """Wzor ``ustawienia.przyklad.toml`` z wierszem ``wlaczone`` zamienionym na ``wiersz_wlaczone`` (None = wiersz usuniety)."""
    wiersze = UST.PLIK_PRZYKLADU.read_text(encoding="utf-8").splitlines(keepends=True)
    i = next(n for n, w in enumerate(wiersze) if w.startswith("wlaczone"))
    wiersze[i:i + 1] = [] if wiersz_wlaczone is None else [wiersz_wlaczone + "\n"]
    plik = tmp_path / nazwa
    plik.write_text("".join(wiersze), encoding="utf-8")
    return plik


# ----------------------------------------------------------------------------- ustawienia

def test_wzor_ma_klucz_wlaczone_true_z_komentarzem_jak_wlaczyc():
    tekst = UST.PLIK_PRZYKLADU.read_text(encoding="utf-8")
    sekcja = tekst.split("[ramki]", 1)[1].split("\n[", 1)[0]
    wiersz = next(w for w in sekcja.splitlines() if w.startswith("wlaczone"))
    assert tomllib.loads(tekst)["ramki"]["wlaczone"] is True  # wzor = zachowanie sprzed E3-R1 (brak klucza tez = true)
    assert "#" in wiersz and "false" in wiersz and "true" in wiersz.split("#", 1)[1], wiersz  # komentarz: co znaczy false, jak wlaczyc
    assert UST.DOMYSLNE_NOWYCH["ramki"]["wlaczone"] is True and UST.SCHEMAT["ramki"]["wlaczone"][0] is bool


def test_brak_klucza_wlaczone_to_true_jak_dotad(tmp_path):
    ust = UST.wczytaj_ustawienia(plik_ustawien(tmp_path, None))
    assert ust["ramki"]["wlaczone"] is True and UST.ramki_wlaczone(ust) is True
    assert UST.ramki_wlaczone({"ramki": {"port": 8765}}) is True and UST.ramki_wlaczone({}) is True  # slownik bez klucza / bez sekcji


def test_wlaczone_false_i_zly_typ(tmp_path):
    ust = UST.wczytaj_ustawienia(plik_ustawien(tmp_path, "wlaczone = false"))
    assert ust["ramki"]["wlaczone"] is False and UST.ramki_wlaczone(ust) is False
    with pytest.raises(UST.BladUstawien, match=r"\[ramki\] wlaczone"):
        UST.wczytaj_ustawienia(plik_ustawien(tmp_path, 'wlaczone = "nie"'))


# ----------------------------------------------------------------------------- indicate

def test_indicate_z_ustawien_wylaczone_bez_klientow(tmp_path, licznik, klienci):
    ind = IND.Indicate.z_ustawien(ust_z_ramkami(tmp_path, licznik.port, False), katalog_danych=tmp_path / "dane")
    ind.uruchom()
    time.sleep(0.5)
    assert ind.klienci() == [] and ind.wieczorna is None and ind.poranna is None and ind.wylaczone
    assert klienci == [] and licznik.polaczenia == 0 and ind.stan() == {} and ind.zatrzymaj() == {}
    wl = IND.Indicate.z_ustawien(ust_z_ramkami(tmp_path, licznik.port, None), katalog_danych=tmp_path / "dane")  # brak klucza
    assert [k.rola for k in wl.klienci()] == ["W", "P"] and not wl.wylaczone and klienci == ["W", "P"]


# ----------------------------------------------------------------------------- program (Aplikacja z ramkami z ustawien)

def _komunikaty_ramek(stan) -> list:
    return [k.id for k in stan.komunikaty if k.id.startswith("ramka")]


def _start(tmp_path, ust):
    return TK.StanowiskoAplikacji(tmp_path, ust=ust, ramki=True)


def test_program_wylaczone_zero_prob_polaczenia_stan_wylaczone_bez_komunikatow(tmp_path, licznik, klienci, caplog):
    caplog.set_level(logging.INFO, logger="stanowisko")
    st = _start(tmp_path, ust_z_ramkami(tmp_path, licznik.port, False))
    try:
        k = st.k
        koniec = time.monotonic() + K.CZAS_NA_POLACZENIE_RAMEK_S + 1.0  # dluzej niz czas na polaczenie (komunikaty "po czasie")
        while time.monotonic() < koniec:
            k.przetworz()
            time.sleep(0.05)
        s = k.stan()
        assert licznik.polaczenia == 0 and klienci == [] and k.ramki is None
        assert s.ramki == K.StanRamek(wylaczone=True) and _komunikaty_ramek(s) == []
        assert k.wybierz_operatora("Technik A") and k.przelacz_tryb("rano")
        for _ in range(5):
            k.przetworz()
            time.sleep(0.05)
        s = k.stan()
        assert s.rano is not None and not s.rano.ramka  # rozkladanie wedlug ekranu (jak bez ramki)
        assert _komunikaty_ramek(s) == [] and K.ID_RAMKA_PORANNA not in [x.id for x in s.komunikaty]
        assert not [x for x in s.komunikaty if x.poziom == "blad"]
        assert licznik.polaczenia == 0
    finally:
        st.k.zamknij()
    ostrzezenia = [r.getMessage() for r in caplog.records if r.levelno >= logging.WARNING and "ramk" in r.getMessage().lower()]
    assert ostrzezenia == [] and any("ramki wylaczone" in r.getMessage() for r in caplog.records)


@pytest.mark.parametrize("wlaczone", [True, None], ids=["true", "brak_klucza"])
def test_program_wlaczone_albo_brak_klucza_laczy_sie_jak_dotad(tmp_path, licznik, klienci, wlaczone):
    st = _start(tmp_path, ust_z_ramkami(tmp_path, licznik.port, wlaczone))
    try:
        st.czekaj(lambda: licznik.polaczenia >= 1, 10.0, "proba polaczenia klienta ramki")
        s = st.k.stan()
        assert sorted(klienci) == ["P", "W"] and st.k.ramki is not None
        assert s.ramki is not None and not s.ramki.wylaczone and s.ramki.wieczorna is not None and s.ramki.poranna is not None
    finally:
        st.k.zamknij()


def test_kontroler_wylacz_ramki_po_podlaczeniu_i_ponowne_podlaczenie(tmp_path):
    """``wylacz_ramki`` (program bez ramek z woli ustawien) i ``podlacz_ramki`` - kazde ustawia stan ramek od nowa."""
    k = K.AtrapaKontrolera(tmp_path / "k")
    try:
        assert k.stan().ramki is None  # program bez ramek (atrapa, testy): jak przed E3-R1
        k.wylacz_ramki()
        assert k.ramki is None and k.stan().ramki == K.StanRamek(wylaczone=True)
        k.podlacz_ramki(None)
        assert k.stan().ramki is None
        k.wylacz_ramki()
        assert k.stan().ramki.wylaczone and not k.test_led()  # bez ramek: polecenie odrzucone, bez wyjatku
    finally:
        k.zamknij()


# ----------------------------------------------------------------------------- okno: pasek stanu, strefa pytan, lista bledow

def _bez_ramek_w_strefie(e) -> None:
    pozycje, bledy = e.okno.pozycje_strefy(e.okno._stan, e.okno._plytka())
    assert not [u.nazwa for u in pozycje if "ramk" in u.nazwa], [u.nazwa for u in pozycje]
    assert not [b.id for b in bledy if "ramk" in b.id] and not e.jest("lista_bledow")


def test_okno_pasek_ramki_wylaczone_neutralny_wieczor_i_rano(tmp_path, ekrany):  # noqa: F811
    k = K.AtrapaKontrolera(tmp_path / "k")
    try:
        k.wylacz_ramki()
        assert k.wybierz_operatora("Technik A")
        e = ekrany(k)
        for tryb in ("wieczor", "rano"):
            if tryb == "rano":
                assert k.przelacz_tryb("rano")
            e.odczekaj(int((K.CZAS_NA_POLACZENIE_RAMEK_S + 0.5) * 1000))  # po czasie na polaczenie: komunikaty ramek bylyby juz widoczne
            assert e.jest("napis_ramki"), tryb
            napis = e.w("napis_ramki")
            assert napis.text() == NR.RAMKI_WYLACZONE == "wyłączone", (tryb, napis.text())
            assert napis.property("rola") == "stan_wartosc", tryb  # zwykly kolor tekstu (nie "stan_uwaga" z tlem ostrzezenia)
            assert e.okno.pasek_stanu.kropka_ramek._hex is None  # kropka bez barwy (nie akcent "gotowa", nie kolor uwagi)
            assert not e.jest("przycisk_test_led") and not e.jest("przycisk_przejmij_ramke")
            assert NR.RAMKI_WYLACZONE_OPIS in napis.toolTip()  # podpowiedz: jak wlaczyc ramki
            assert not e.jest("komunikat_ramka_niedostepna") and not e.jest("komunikat_ramka_wieczorna_niedostepna")
            _bez_ramek_w_strefie(e)
    finally:
        k.zamknij()


def test_okno_bez_ramek_bez_przelacznika_jak_dotad(tmp_path, ekrany):  # noqa: F811
    """Program bez ramek, ale NIE wylaczonych w ustawieniach (atrapa / testy): pole ramek ukryte, rano komunikat jak dotad."""
    k = K.AtrapaKontrolera(tmp_path / "k")
    try:
        assert k.wybierz_operatora("Technik A") and k.przelacz_tryb("rano")
        e = ekrany(k)
        e.odczekaj(100)
        assert not e.jest("napis_ramki") and e.jest("komunikat_ramka_niedostepna")
    finally:
        k.zamknij()


def test_main_atrapa_z_ustawieniami_wylaczonymi_pokazuje_wylaczone(tmp_path, monkeypatch):
    """``aplikacja.main --atrapa`` na instalacji z ``wlaczone = false`` (proba startu, zrzuty): stan ramek "wylaczone"; brak klucza
    albo brak pliku ustawien - atrapa jak dotad (bez ramek; plik nie jest wymagany). Okno nie powstaje (petla Qt nie startuje)."""
    from stanowisko import aplikacja as AP

    class Stop(Exception):
        pass

    widziane = []

    def okno(kontroler, lacznik):
        widziane.append(kontroler.stan().ramki)
        lacznik.zatrzymaj()
        kontroler.zamknij()
        raise Stop

    monkeypatch.setattr(AP, "utworz_okno", okno)
    for plik in (plik_ustawien(tmp_path, "wlaczone = false", "u_false.toml"), plik_ustawien(tmp_path, None, "u_bez.toml"), tmp_path / "nie_ma.toml"):
        with pytest.raises(Stop):
            AP.main(["--atrapa", "--ustawienia", str(plik), "--zamknij-po", "0.1"])
    assert widziane == [K.StanRamek(wylaczone=True), None, None]


def test_ust_slownik_nie_jest_zmieniany(tmp_path, licznik):
    ust = ust_z_ramkami(tmp_path, licznik.port, False)
    kopia = copy.deepcopy(ust)
    assert UST.ramki_wlaczone(ust) is False and ust == kopia
