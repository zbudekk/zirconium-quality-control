"""Klatka matrycy 64 x 64 (RGB) i rysowanie: bloki gniazd, pierscien stanu, napisy na marginesie.

Uklad wspolrzednych klatki: x = kolumna 0..63 od lewej (patrzac od uzytkownika), y = wiersz
0..63 od tylu ramki (y = 63 to krawedz przy uzytkowniku). Srodek plytki = srodek matrycy.
Raster 2,5 mm: plytka 96 mm (otwor wkladki 96,8 mm) zajmuje ok. 38,7 piksela, wiec obszar
plytki to kolumny i wiersze 12..51; margines 11 pikseli z kazdej strony (plan_ramki_v2 D5).
Uszy wkladki zaslaniaja tylne narozniki marginesu (D12), dlatego napisy sa z przodu i z prawej.
Obrot / odbicie fizycznego panelu ustawia sie w `sprzet_rpi` (C1), nie tutaj.
"""
from __future__ import annotations

from . import czcionka

SZEROKOSC = 64
WYSOKOSC = 64
RASTER_MM = 2.5
OBSZAR_PLYTKI = (12, 12, 40, 40)  # x, y, szerokosc, wysokosc - bloki gniazd tylko tutaj

CZARNY = (0, 0, 0)

# Kolory gniazd (nazwy w protokole). Pelna skala; jasnosc ustawia sprzet_rpi.
KOLORY = {
    "czerwony": (255, 0, 0),
    "zielony": (0, 255, 0),
    "zolty": (255, 190, 0),
    "bursztyn": (255, 110, 0),
    "bialy": (255, 255, 255),
    "niebieski": (0, 60, 255),
    "fioletowy": (170, 0, 255),
    "szary": (80, 80, 80),
}

# Kolory stanu ramki (pierscien na brzegu matrycy i ikona lacznosci) - I2, I12.
KOLORY_STANU = {
    "gotowa": (0, 60, 255),
    "skanowanie": (255, 190, 0),
    "analiza": (170, 0, 255),
    "wynik": (0, 255, 0),
    "blad": (255, 0, 0),
    "brak_planu": (255, 60, 0),
    "brak_lacznosci": (255, 0, 0),
    "lacznosc": (0, 255, 0),
}
KOLOR_TEKSTU = (255, 255, 255)
KOLORY_TEST_LED = ((255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255))

# Uklad marginesu
TEKST_Y = 55          # wiersz gornej krawedzi napisu z przodu (wiersze 55..61)
TEKST_X0 = 7          # napis z przodu wysrodkowany w kolumnach 7..61
TEKST_SZER = 55
PRAWY_X = 55          # prawy margines: numery innych plytek kuwety, kolumny 55..59
PRAWY_Y0 = 14
PRAWY_KROK = 9
IKONA = (2, 57, 3, 3)  # ikona lacznosci z przodu po lewej: x, y, w, h


class Klatka:
    """Bufor RGB SZEROKOSC x WYSOKOSC (bajty r, g, b wierszami)."""

    __slots__ = ("szerokosc", "wysokosc", "dane")

    def __init__(self, dane=None, szerokosc: int = SZEROKOSC, wysokosc: int = WYSOKOSC):
        self.szerokosc = szerokosc
        self.wysokosc = wysokosc
        n = szerokosc * wysokosc * 3
        if dane is None:
            self.dane = bytearray(n)
        else:
            if len(dane) != n:
                raise ValueError("zla dlugosc danych klatki")
            self.dane = bytearray(dane)

    def ustaw(self, x: int, y: int, rgb) -> None:
        if 0 <= x < self.szerokosc and 0 <= y < self.wysokosc:
            i = (y * self.szerokosc + x) * 3
            self.dane[i] = rgb[0]
            self.dane[i + 1] = rgb[1]
            self.dane[i + 2] = rgb[2]

    def piksel(self, x: int, y: int) -> tuple:
        i = (y * self.szerokosc + x) * 3
        return (self.dane[i], self.dane[i + 1], self.dane[i + 2])

    def blok(self, x: int, y: int, w: int, h: int, rgb) -> None:
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.ustaw(xx, yy, rgb)

    def wypelnij(self, rgb) -> None:
        self.dane[:] = bytes(rgb) * (self.szerokosc * self.wysokosc)

    def zapalone(self) -> dict:
        """{(x, y): (r, g, b)} dla pikseli innych niz czarne."""
        wynik = {}
        d = self.dane
        w = self.szerokosc
        for i in range(0, len(d), 3):
            if d[i] or d[i + 1] or d[i + 2]:
                p = i // 3
                wynik[(p % w, p // w)] = (d[i], d[i + 1], d[i + 2])
        return wynik

    def kopia(self) -> "Klatka":
        return Klatka(self.dane, self.szerokosc, self.wysokosc)

    def do_hex(self) -> str:
        return self.dane.hex()

    @classmethod
    def z_hex(cls, tekst: str, szerokosc: int = SZEROKOSC, wysokosc: int = WYSOKOSC) -> "Klatka":
        return cls(bytes.fromhex(tekst), szerokosc, wysokosc)

    def __eq__(self, inna) -> bool:
        return (isinstance(inna, Klatka) and self.szerokosc == inna.szerokosc
                and self.wysokosc == inna.wysokosc and self.dane == inna.dane)

    def __ne__(self, inna) -> bool:
        return not self.__eq__(inna)

    __hash__ = None


def w_obszarze_plytki(x: int, y: int, w: int = 1, h: int = 1) -> bool:
    """Czy blok [x, x+w) x [y, y+h) lezy w calosci w obszarze plytki."""
    ox, oy, ow, oh = OBSZAR_PLYTKI
    return ox <= x and oy <= y and x + w <= ox + ow and y + h <= oy + oh


def szerokosc_tekstu(tekst: str) -> int:
    return czcionka.szerokosc(tekst)


def rysuj_tekst(klatka: Klatka, tekst: str, x: int, y: int, rgb=KOLOR_TEKSTU) -> int:
    """Rysuje napis od (x, y) (lewy gorny rog); zwraca szerokosc w pikselach."""
    xx = x
    for znak in tekst:
        for dy, wiersz in enumerate(czcionka.glif(znak)):
            for dx, c in enumerate(wiersz):
                if c == "#":
                    klatka.ustaw(xx + dx, y + dy, rgb)
        xx += czcionka.SZER + czcionka.ODSTEP
    return czcionka.szerokosc(tekst)


def rysuj_tekst_przod(klatka: Klatka, tekst: str, rgb=KOLOR_TEKSTU) -> None:
    """Napis wysrodkowany w pasie przed plytka (wiersze TEKST_Y..TEKST_Y+6)."""
    if not tekst:
        return
    w = czcionka.szerokosc(tekst)
    x = TEKST_X0 + max(0, (TEKST_SZER - w) // 2)
    rysuj_tekst(klatka, tekst, x, TEKST_Y, rgb)


def rysuj_prawy(klatka: Klatka, numery, rgb=KOLOR_TEKSTU) -> None:
    """Pojedyncze cyfry jedna pod druga na prawym marginesie (maks. 4)."""
    for n, num in enumerate(list(numery)[:4]):
        rysuj_tekst(klatka, str(num)[:1], PRAWY_X, PRAWY_Y0 + n * PRAWY_KROK, rgb)


def rysuj_pierscien(klatka: Klatka, rgb) -> None:
    """Pierscien 1 piksel na brzegu matrycy - kolor stanu ramki (I2)."""
    w, h = klatka.szerokosc, klatka.wysokosc
    for x in range(w):
        klatka.ustaw(x, 0, rgb)
        klatka.ustaw(x, h - 1, rgb)
    for y in range(h):
        klatka.ustaw(0, y, rgb)
        klatka.ustaw(w - 1, y, rgb)


def rysuj_ikone(klatka: Klatka, rgb) -> None:
    x, y, w, h = IKONA
    klatka.blok(x, y, w, h, rgb)
