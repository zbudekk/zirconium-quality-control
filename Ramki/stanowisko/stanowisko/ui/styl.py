"""styl - czcionki, rozmiary i kolory obramowan ekranu wieczornego.

Tu NIE MA kolorow ani napisow statusow prac (jedyne zrodlo: ``statusy`` i pola stanu). Sa tylko barwy tla, ramek i trzech
poziomow komunikatu (info / ostrzezenie / blad). Zadna z nich nie jest zielona - zielony na ekranie znaczy wylacznie
"praca sprawdzona, cala" i pochodzi ze stanu.

Dwa zestawy rozmiarow (A-P1 recenzji PR #21): ``ZWYKLE`` (okno od 1500 x 860 punktow, np. 1600 x 900 przy skalowaniu
100 %) i ``ZWARTE`` (mniejsze okno: 1366 x 768, laptop 1920 x 1080 przy skalowaniu 150 % = 1280 x 720 punktow) - mniejsze
odstepy, czcionki pomocnicze i wysokosci przyciskow; okno przelacza je samo przy zmianie rozmiaru (``okno.OknoWieczor``).
"""
from __future__ import annotations

import dataclasses

CZCIONKA = "Segoe UI"
ROZMIAR_PODSTAWOWY_PX = 16

TLO = "#eef0f3"
TLO_PANELU = "#ffffff"
RAMKA = "#c3c9d1"
TEKST = "#15191e"
TEKST_SLABY = "#4d5661"
AKCENT = "#1d4f91"  # przyciski neutralne, zaznaczenie
AKCENT_JASNY = "#dbe7f6"
NIEAKTYWNY_TLO = "#d9dce1"
NIEAKTYWNY_TEKST = "#7b838d"

# poziom komunikatu -> (tlo, pasek z lewej, tekst)
POZIOMY = {
    "info": ("#e6eef8", "#1d4f91", TEKST),
    "ostrzezenie": ("#fdf1d6", "#b06a00", TEKST),
    "blad": ("#fbe3e1", "#a3211b", TEKST),
}

# okno mniejsze niz to (szerokosc albo wysokosc) = uklad zwarty
PROG_ZWARTEGO = (1500, 860)
# najmniejsze okno, przy ktorym caly ekran sie miesci (test ``test_ap1_*``): okno zmaksymalizowane na laptopie 1920 x 1080
# ze skalowaniem 150 % ma ok. 1280 x 650 punktow (ekran 1280 x 720 minus pasek zadan i belka tytulu)
MINIMUM_OKNA = (1240, 640)


@dataclasses.dataclass(frozen=True)
class Rozmiary:
    """Rozmiary jednego trybu ukladu (piksele logiczne)."""

    zwarty: bool
    margines: int  # brzeg okna
    odstep: int  # odstep pionowy miedzy czesciami
    odstep_kolumn: int
    szerokosc_listy_plytek: int
    szerokosc_prawej: int
    wysokosc_decyzji: int  # "Ukruszona" / "OK"
    wysokosc_przycisku: int  # przyciski pytan i komunikatow
    wysokosc_drugiego_rzedu: int  # "Cofnij decyzje" / "Nastepna" / "Zamknij"
    wysokosc_skanuj: int
    mapa_min: tuple
    obraz_min: int
    wiersz_tabeli: int
    # czcionki (px)
    podstawowa: int
    podpis: int
    wartosc: int
    naglowek: int
    tytul: int
    duzy: int
    slaby: int
    uwaga: int
    przycisk: int
    glowny: int
    cyfra: int
    osoba: int
    lacze: int
    naglowek_tabeli: int
    decyzja: int
    znaczek: int
    status_pracy: int
    # dopelnienia (padding) przyciskow
    dopelnienie: str
    dopelnienie_lacza: str
    dopelnienie_osoby: str
    min_cyfry: int
    min_osoby: int


ZWYKLE = Rozmiary(zwarty=False, margines=10, odstep=8, odstep_kolumn=10, szerokosc_listy_plytek=250, szerokosc_prawej=540,
                  wysokosc_decyzji=68, wysokosc_przycisku=44, wysokosc_drugiego_rzedu=56, wysokosc_skanuj=56, mapa_min=(380, 300),
                  obraz_min=90, wiersz_tabeli=30,
                  podstawowa=16, podpis=13, wartosc=18, naglowek=20, tytul=24, duzy=20, slaby=14, uwaga=15, przycisk=16, glowny=17, cyfra=22,
                  osoba=20, lacze=15, naglowek_tabeli=14, decyzja=22, znaczek=15, status_pracy=18,
                  dopelnienie="6px 14px", dopelnienie_lacza="4px 10px", dopelnienie_osoby="4px 22px", min_cyfry=44, min_osoby=48)
ZWARTE = Rozmiary(zwarty=True, margines=6, odstep=5, odstep_kolumn=6, szerokosc_listy_plytek=206, szerokosc_prawej=468,
                  wysokosc_decyzji=48, wysokosc_przycisku=34, wysokosc_drugiego_rzedu=36, wysokosc_skanuj=46, mapa_min=(300, 190),
                  obraz_min=56, wiersz_tabeli=25,
                  podstawowa=14, podpis=12, wartosc=15, naglowek=16, tytul=19, duzy=15, slaby=12, uwaga=13, przycisk=14, glowny=14, cyfra=17,
                  osoba=16, lacze=13, naglowek_tabeli=12, decyzja=18, znaczek=12, status_pracy=14,
                  dopelnienie="3px 9px", dopelnienie_lacza="2px 7px", dopelnienie_osoby="2px 12px", min_cyfry=34, min_osoby=34)


def rozmiary(zwarty: bool) -> Rozmiary:
    return ZWARTE if zwarty else ZWYKLE


def jasnosc(hex_: str) -> float:
    """Jasnosc koloru ``#rrggbb`` (0-255, wzor "luma")."""
    r, g, b = int(hex_[1:3], 16), int(hex_[3:5], 16), int(hex_[5:7], 16)
    return 0.299 * r + 0.587 * g + 0.114 * b


def _liniowa(skladowa: int) -> float:
    c = skladowa / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def jasnosc_wzgledna(hex_: str) -> float:
    """Jasnosc wzgledna koloru (0-1) jak w zaleceniach dostepnosci WCAG."""
    r, g, b = int(hex_[1:3], 16), int(hex_[3:5], 16), int(hex_[5:7], 16)
    return 0.2126 * _liniowa(r) + 0.7152 * _liniowa(g) + 0.0722 * _liniowa(b)


def kontrast(hex_a: str, hex_b: str) -> float:
    a, b = jasnosc_wzgledna(hex_a), jasnosc_wzgledna(hex_b)
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


def tekst_na(hex_: str) -> str:
    """Kolor napisu na tle ``hex_``: bialy, gdy ma kontrast co najmniej 4 : 1, inaczej prawie czarny (A-D7: czarny na
    zielonym ma ok. 7,8 : 1, bialy tylko 2,7 : 1; na czerwonym zostaje bialy)."""
    return "#ffffff" if kontrast(hex_, "#ffffff") >= 4.0 else "#111111"


def przycisk_w_kolorze(hex_: str, r: Rozmiary = ZWYKLE) -> str:
    """Arkusz stylu duzego przycisku w kolorze ``hex_`` (kolor podaje wolajacy - ze ``statusy``)."""
    return (f"QPushButton {{ background: {hex_}; color: {tekst_na(hex_)}; border: 2px solid #20242a; border-radius: 8px; "
            f"font-size: {r.decyzja}px; font-weight: 700; padding: 2px 10px; }}"
            f"QPushButton:focus {{ border: 3px dashed #101418; }}"
            f"QPushButton:disabled {{ background: {NIEAKTYWNY_TLO}; color: {NIEAKTYWNY_TEKST}; border: 2px dashed {NIEAKTYWNY_TEKST}; }}")


def arkusz(r: Rozmiary = ZWYKLE) -> str:
    """Arkusz stylu calego okna w trybie ``r``."""
    return f"""
QWidget#okno_wieczor {{ background: {TLO}; }}
QWidget {{ color: {TEKST}; font-family: "{CZCIONKA}"; font-size: {r.podstawowa}px; }}
QFrame[rola="panel"] {{ background: {TLO_PANELU}; border: 1px solid {RAMKA}; border-radius: 8px; }}
QFrame[rola="pasek"] {{ background: {TLO_PANELU}; border: 1px solid {RAMKA}; border-radius: 8px; }}
QFrame[rola="pasek"][blysk="true"] {{ background: {AKCENT_JASNY}; border: 2px solid {AKCENT}; }}
QLabel {{ background: transparent; border: none; }}
QLabel[rola="podpis"] {{ color: {TEKST_SLABY}; font-size: {r.podpis}px; }}
QLabel[rola="wartosc"] {{ font-size: {r.wartosc}px; font-weight: 600; }}
QLabel[rola="wartosc_uwaga"] {{ font-size: {r.wartosc}px; font-weight: 600; background: {POZIOMY["ostrzezenie"][0]};
                                border: 1px solid {POZIOMY["ostrzezenie"][1]}; border-radius: 4px; padding: 0px 6px; }}
QLabel[rola="naglowek"] {{ font-size: {r.naglowek}px; font-weight: 700; }}
QLabel[rola="tytul"] {{ font-size: {r.tytul}px; font-weight: 700; }}
QLabel[rola="duzy"] {{ font-size: {r.duzy}px; font-weight: 600; }}
QLabel[rola="slaby"] {{ color: {TEKST_SLABY}; font-size: {r.slaby}px; }}
QLabel[rola="uwaga"] {{ background: {POZIOMY["ostrzezenie"][0]}; border: 1px solid {POZIOMY["ostrzezenie"][1]}; border-radius: 6px;
                        padding: {"3px 6px" if r.zwarty else "6px 8px"}; font-size: {r.uwaga}px; font-weight: 600; }}
QLabel[rola="informacja"] {{ background: {POZIOMY["info"][0]}; border: 1px solid {POZIOMY["info"][1]}; border-radius: 6px;
                             padding: {"3px 6px" if r.zwarty else "6px 8px"}; font-size: {r.uwaga}px; }}
QPushButton {{ background: {TLO_PANELU}; border: 2px solid {AKCENT}; border-radius: 6px; padding: {r.dopelnienie}; font-size: {r.przycisk}px;
               font-weight: 600; color: {AKCENT}; }}
QPushButton:hover {{ background: {AKCENT_JASNY}; }}
QPushButton:pressed {{ background: {AKCENT}; color: #ffffff; }}
QPushButton:checked {{ background: {AKCENT}; color: #ffffff; }}
QPushButton:focus {{ border-style: dashed; border-color: #101418; }}
QPushButton:disabled {{ background: {NIEAKTYWNY_TLO}; color: {NIEAKTYWNY_TEKST}; border: 2px dashed {NIEAKTYWNY_TEKST}; }}
QPushButton[rola="glowny"] {{ background: {AKCENT}; color: #ffffff; font-size: {r.glowny}px; font-weight: 700; padding: 2px 12px; }}
QPushButton[rola="glowny"]:hover {{ background: #163d70; }}
QPushButton[rola="glowny"]:disabled {{ background: {NIEAKTYWNY_TLO}; color: {NIEAKTYWNY_TEKST}; }}
QPushButton[rola="nowa"] {{ background: {AKCENT}; color: #ffffff; border: 2px solid {AKCENT}; font-size: {r.lacze}px; font-weight: 700;
                           padding: {r.dopelnienie_lacza}; }}
QPushButton[rola="nowa"]:focus {{ border: 2px dashed #ffffff; }}
QPushButton[rola="cyfra"] {{ font-size: {r.cyfra}px; font-weight: 700; min-width: {r.min_cyfry}px; min-height: {r.min_cyfry}px; padding: 2px; }}
QPushButton[rola="osoba"] {{ font-size: {r.osoba}px; font-weight: 700; min-height: {r.min_osoby}px; padding: {r.dopelnienie_osoby}; }}
QPushButton[rola="lacze"] {{ border: 1px solid #8a929c; font-size: {r.lacze}px; font-weight: 600; color: {TEKST}; padding: {r.dopelnienie_lacza}; }}
QPushButton[rola="lacze"]:focus {{ border: 2px dashed #101418; }}
QFrame[rola="kafelek"] {{ background: {TLO_PANELU}; border: 2px solid {RAMKA}; border-radius: 8px; }}
QFrame[rola="kafelek"][wybrany="true"] {{ background: {AKCENT_JASNY}; border: 3px solid {AKCENT}; }}
QFrame[rola="kafelek"]:focus {{ border: 3px dashed #101418; }}
QTableWidget {{ background: {TLO_PANELU}; border: 1px solid {RAMKA}; gridline-color: {RAMKA}; font-size: {r.podstawowa}px; }}
QHeaderView::section {{ background: #e3e7ec; border: none; border-right: 1px solid {RAMKA}; border-bottom: 1px solid {RAMKA};
                        padding: {"2px 2px" if r.zwarty else "4px 6px"}; font-size: {r.naglowek_tabeli}px; font-weight: 700; }}
QProgressBar {{ border: 1px solid {RAMKA}; border-radius: 5px; background: #e3e7ec; text-align: center; font-size: {r.podpis}px;
                min-height: {14 if r.zwarty else 18}px; }}
QProgressBar::chunk {{ background: {AKCENT}; border-radius: 4px; }}
QScrollArea {{ border: none; background: transparent; }}
"""


ARKUSZ = arkusz(ZWYKLE)
# zgodnosc wstecz (stale z rundy 1)
WYSOKOSC_PRZYCISKU_DECYZJI = ZWYKLE.wysokosc_decyzji
WYSOKOSC_PRZYCISKU = ZWYKLE.wysokosc_przycisku
SZEROKOSC_LISTY_PLYTEK = ZWYKLE.szerokosc_listy_plytek
SZEROKOSC_PRAWEJ = ZWYKLE.szerokosc_prawej
