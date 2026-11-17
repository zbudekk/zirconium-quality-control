"""Sprzet prawdziwej ramki: Raspberry Pi 4 + Adafruit RGB Matrix Bonnet + panel HUB75 64 x 64 P2.5
+ 3 czujniki Halla A3144 + (ramka poranna) klawiatura numeryczna 2,4 GHz z odbiornikiem USB.

NAPISANY WG DOKUMENTOW, NIE URUCHAMIANY W PACZCE E3-A8 (sprawdzi paczka C1 na sprzecie):
- plan_ramki_v2 8.1: matryca przez rpi-rgb-led-matrix, mapowanie "adafruit-hat-pwm" (zworka
  GPIO4-GPIO18), zworka E -> 8 dla 64 x 64; 8.2: Hall A / B / C na GPIO 19 / 25 / 8 (BCM),
  wyjscie otwarty kolektor podciagniete 10 kOhm do 3,3 V, magnes obecny = stan niski;
  config.txt: dtparam=spi=off, dtparam=audio=off; cmdline.txt: isolcpus=3;
- plan_ramki_v2 9 krok 4: klawiatura czytana przez evdev; D11: n = A + 2B + 4C, 0 = brak plytki.
Biblioteki sprzetowe (rgbmatrix, gpiozero, evdev) sa importowane WYLACZNIE w konstruktorze
i watku klawiatury, wiec reszta pakietu i funkcje czyste ponizej dzialaja na Windows.
Uruchamiac jako root (rgbmatrix); `drop_privileges = False`, bo po zrzuceniu uprawnien
nie byloby dostepu do /dev/input (klawiatura) ani GPIO.
"""
from __future__ import annotations

import queue
import threading

from .sprzet import BladSprzetu, Sprzet

MAPA_KLAWISZY = {
    "KEY_KPENTER": "enter", "KEY_ENTER": "enter",
    "KEY_BACKSPACE": "backspace",
    "KEY_KPASTERISK": "zamknij_piec",
}
for _c in "0123456789":
    MAPA_KLAWISZY["KEY_KP" + _c] = _c
    MAPA_KLAWISZY["KEY_" + _c] = _c
del _c

PLIK_TEMPERATURY = "/sys/class/thermal/thermal_zone0/temp"


def numer_z_poziomow(poziomy, aktywny_niski: bool = True) -> int:
    """Numer plytki z poziomow wejsc [A, B, C]: bit i = magnes nad czujnikiem i."""
    n = 0
    for i, v in enumerate(poziomy):
        aktywny = (v == 0) if aktywny_niski else (v == 1)
        if aktywny:
            n |= 1 << i
    return n


def klawisz_z_nazwy(nazwa, mapa=None):
    """Nazwa kodu evdev (albo lista aliasow) -> logiczny klawisz albo None."""
    mapa = MAPA_KLAWISZY if mapa is None else mapa
    nazwy = nazwa if isinstance(nazwa, (list, tuple)) else [nazwa]
    for n in nazwy:
        if n in mapa:
            return mapa[n]
    return None


def przeksztalc(x: int, y: int, obrot: int, lustro: bool, szer: int = 64, wys: int = 64):
    """Wspolrzedne klatki -> wspolrzedne panelu: najpierw odbicie w poziomie, potem obrot zgodnie
    z ruchem wskazowek zegara (90 / 180 / 270). Ustawienie dobiera C1 na zlozonej ramce."""
    if lustro:
        x = szer - 1 - x
    if obrot == 0:
        return x, y
    if obrot == 90:
        return wys - 1 - y, x
    if obrot == 180:
        return szer - 1 - x, wys - 1 - y
    if obrot == 270:
        return y, szer - 1 - x
    raise ValueError("obrot: 0, 90, 180 albo 270")


class SprzetRpi(Sprzet):
    def __init__(self, rola: str = "P", piny_halla=(19, 25, 8), jasnosc: int = 60, obrot: int = 0,
                 lustro: bool = False, mapowanie: str = "adafruit-hat-pwm", spowolnienie_gpio: int = 4,
                 klawisz_zamknij_piec: str = "KEY_KPASTERISK", z_klawiatura=None):
        if obrot not in (0, 90, 180, 270):
            raise BladSprzetu("obrot: 0, 90, 180 albo 270")
        self.rola = rola
        self.obrot = obrot
        self.lustro = lustro
        self._mapa = {k: v for k, v in MAPA_KLAWISZY.items() if v != "zamknij_piec"}
        self._mapa[klawisz_zamknij_piec] = "zamknij_piec"
        self._kolejka = queue.Queue()
        self._stop = threading.Event()
        self._watek = None
        self._temp = None
        self._temp_licznik = 0
        try:
            from rgbmatrix import RGBMatrix, RGBMatrixOptions
        except ImportError as e:
            raise BladSprzetu("brak biblioteki rgbmatrix (rpi-rgb-led-matrix z powiazaniem Python)") from e
        try:
            from gpiozero import InputDevice
        except ImportError as e:
            raise BladSprzetu("brak biblioteki gpiozero (python3-gpiozero)") from e
        opcje = RGBMatrixOptions()
        opcje.rows = 64
        opcje.cols = 64
        opcje.chain_length = 1
        opcje.parallel = 1
        opcje.hardware_mapping = mapowanie
        opcje.gpio_slowdown = spowolnienie_gpio
        opcje.brightness = max(1, min(100, int(jasnosc)))
        opcje.drop_privileges = False
        try:
            self._matryca = RGBMatrix(options=opcje)
            self._plotno = self._matryca.CreateFrameCanvas()
            # pull_up=None: podciaganie 10 kOhm do 3,3 V jest na plytce proto; active_state=False:
            # stan niski = magnes obecny (A3144, otwarty kolektor)
            self._czujniki = [InputDevice(p, pull_up=None, active_state=False) for p in piny_halla]
        except Exception as e:  # noqa: BLE001 - wszystko z inicjalizacji sprzetu = BladSprzetu
            raise BladSprzetu(f"inicjalizacja sprzetu nie powiodla sie: {type(e).__name__}") from e
        if z_klawiatura is None:
            z_klawiatura = rola == "P"
        if z_klawiatura:
            self._watek = threading.Thread(target=self._petla_klawiatury, name="ramka-klawiatura", daemon=True)
            self._watek.start()

    # ------------------------------------------------------------ czujniki Halla

    def odczytaj_plytke(self) -> int:
        n = 0
        for i, c in enumerate(self._czujniki):
            if c.is_active:
                n |= 1 << i
        return n

    # ------------------------------------------------------------ klawiatura (evdev)

    def _znajdz_klawiature(self):
        import evdev
        for sciezka in evdev.list_devices():
            try:
                d = evdev.InputDevice(sciezka)
                klawisze = d.capabilities().get(evdev.ecodes.EV_KEY, [])
                if evdev.ecodes.KEY_KPENTER in klawisze or evdev.ecodes.KEY_KP0 in klawisze:
                    return d
                d.close()
            except OSError:
                continue
        return None

    def _petla_klawiatury(self) -> None:
        try:
            import select

            import evdev
        except ImportError:
            return  # brak evdev: ramka dziala bez klawiatury (blad widac w logu programu)
        while not self._stop.is_set():
            d = self._znajdz_klawiature()
            if d is None:
                self._stop.wait(2.0)  # odbiornik USB moze zostac wpiety pozniej
                continue
            try:
                d.grab()  # klawisze nie trafiaja do konsoli systemu
                while not self._stop.is_set():
                    r, _, _ = select.select([d.fd], [], [], 0.5)
                    if not r:
                        continue
                    for ev in d.read():
                        if ev.type == evdev.ecodes.EV_KEY and ev.value == 1:  # 1 = nacisniecie, 2 = powtorzenie
                            k = klawisz_z_nazwy(evdev.ecodes.KEY.get(ev.code), self._mapa)
                            if k is not None:
                                self._kolejka.put(k)
            except OSError:
                pass  # odbiornik wyjety - szukamy ponownie
            finally:
                try:
                    d.close()
                except OSError:
                    pass

    def pobierz_klawisze(self) -> list:
        wynik = []
        while True:
            try:
                wynik.append(self._kolejka.get_nowait())
            except queue.Empty:
                return wynik

    # ------------------------------------------------------------ matryca

    def pokaz(self, klatka) -> None:
        p = self._plotno
        for y in range(klatka.wysokosc):
            for x in range(klatka.szerokosc):
                r, g, b = klatka.piksel(x, y)
                px, py = przeksztalc(x, y, self.obrot, self.lustro, klatka.szerokosc, klatka.wysokosc)
                p.SetPixel(px, py, r, g, b)
        self._plotno = self._matryca.SwapOnVSync(p)

    def temperatura(self):
        self._temp_licznik -= 1
        if self._temp_licznik <= 0:
            self._temp_licznik = 500  # odczyt co ok. 5 s przy petli 10 ms
            try:
                with open(PLIK_TEMPERATURY, encoding="ascii") as f:
                    self._temp = round(int(f.read().strip()) / 1000.0, 1)
            except (OSError, ValueError):
                self._temp = None
        return self._temp

    def zamknij(self) -> None:
        self._stop.set()
        if self._watek is not None:
            self._watek.join(2)
        try:
            self._matryca.Clear()
        except Exception:  # noqa: BLE001
            pass
        for c in self._czujniki:
            try:
                c.close()
            except Exception:  # noqa: BLE001
                pass
