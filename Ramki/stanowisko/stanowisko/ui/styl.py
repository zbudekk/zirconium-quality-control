"""styl - czcionki, rozmiary i kolory obramowan ekranu wieczornego.

Tu NIE MA kolorow ani napisow statusow prac (jedyne zrodlo: ``statusy`` i pola stanu). Sa tylko barwy tla, ramek i trzech
poziomow komunikatu (info / ostrzezenie / blad). Zadna z nich nie jest zielona - zielony na ekranie znaczy wylacznie
"praca sprawdzona, cala" i pochodzi ze stanu.
"""
from __future__ import annotations

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

WYSOKOSC_PRZYCISKU_DECYZJI = 68
WYSOKOSC_PRZYCISKU = 44
SZEROKOSC_LISTY_PLYTEK = 250
SZEROKOSC_PRAWEJ = 540


def jasnosc(hex_: str) -> float:
    """Jasnosc koloru ``#rrggbb`` (0-255) - do wyboru czarnego albo bialego tekstu na tle w tym kolorze."""
    r, g, b = int(hex_[1:3], 16), int(hex_[3:5], 16), int(hex_[5:7], 16)
    return 0.299 * r + 0.587 * g + 0.114 * b


def tekst_na(hex_: str) -> str:
    return "#111111" if jasnosc(hex_) > 140 else "#ffffff"


def przycisk_w_kolorze(hex_: str) -> str:
    """Arkusz stylu duzego przycisku w kolorze ``hex_`` (kolor podaje wolajacy - ze ``statusy``)."""
    return (f"QPushButton {{ background: {hex_}; color: {tekst_na(hex_)}; border: 2px solid #20242a; border-radius: 8px; "
            f"font-size: 22px; font-weight: 700; padding: 4px 12px; min-height: {WYSOKOSC_PRZYCISKU_DECYZJI - 12}px; }}"
            f"QPushButton:disabled {{ background: {NIEAKTYWNY_TLO}; color: {NIEAKTYWNY_TEKST}; border: 2px dashed {NIEAKTYWNY_TEKST}; }}")


ARKUSZ = f"""
QWidget#okno_wieczor {{ background: {TLO}; }}
QWidget {{ color: {TEKST}; font-family: "{CZCIONKA}"; font-size: {ROZMIAR_PODSTAWOWY_PX}px; }}
QFrame[rola="panel"] {{ background: {TLO_PANELU}; border: 1px solid {RAMKA}; border-radius: 8px; }}
QFrame[rola="pasek"] {{ background: {TLO_PANELU}; border: 1px solid {RAMKA}; border-radius: 8px; }}
QLabel {{ background: transparent; border: none; }}
QLabel[rola="podpis"] {{ color: {TEKST_SLABY}; font-size: 13px; }}
QLabel[rola="wartosc"] {{ font-size: 18px; font-weight: 600; }}
QLabel[rola="naglowek"] {{ font-size: 20px; font-weight: 700; }}
QLabel[rola="tytul"] {{ font-size: 24px; font-weight: 700; }}
QLabel[rola="duzy"] {{ font-size: 20px; font-weight: 600; }}
QLabel[rola="slaby"] {{ color: {TEKST_SLABY}; font-size: 14px; }}
QLabel[rola="uwaga"] {{ background: {POZIOMY["ostrzezenie"][0]}; border: 1px solid {POZIOMY["ostrzezenie"][1]}; border-radius: 6px;
                        padding: 6px 8px; font-size: 15px; font-weight: 600; }}
QLabel[rola="informacja"] {{ background: {POZIOMY["info"][0]}; border: 1px solid {POZIOMY["info"][1]}; border-radius: 6px;
                             padding: 6px 8px; font-size: 15px; }}
QPushButton {{ background: {TLO_PANELU}; border: 2px solid {AKCENT}; border-radius: 6px; padding: 6px 14px; font-size: 16px;
               font-weight: 600; color: {AKCENT}; }}
QPushButton:hover {{ background: {AKCENT_JASNY}; }}
QPushButton:pressed {{ background: {AKCENT}; color: #ffffff; }}
QPushButton:checked {{ background: {AKCENT}; color: #ffffff; }}
QPushButton:disabled {{ background: {NIEAKTYWNY_TLO}; color: {NIEAKTYWNY_TEKST}; border: 2px dashed {NIEAKTYWNY_TEKST}; }}
QPushButton[rola="glowny"] {{ background: {AKCENT}; color: #ffffff; font-size: 18px; font-weight: 700; }}
QPushButton[rola="glowny"]:hover {{ background: #163d70; }}
QPushButton[rola="glowny"]:disabled {{ background: {NIEAKTYWNY_TLO}; color: {NIEAKTYWNY_TEKST}; }}
QPushButton[rola="cyfra"] {{ font-size: 22px; font-weight: 700; min-width: 44px; min-height: 44px; padding: 2px; }}
QPushButton[rola="osoba"] {{ font-size: 20px; font-weight: 700; min-height: 48px; padding: 4px 22px; }}
QPushButton[rola="lacze"] {{ border: 1px solid #8a929c; font-size: 15px; font-weight: 600; color: {TEKST}; padding: 4px 10px; }}
QFrame[rola="kafelek"] {{ background: {TLO_PANELU}; border: 2px solid {RAMKA}; border-radius: 8px; }}
QFrame[rola="kafelek"][wybrany="true"] {{ background: {AKCENT_JASNY}; border: 3px solid {AKCENT}; }}
QTableWidget {{ background: {TLO_PANELU}; border: 1px solid {RAMKA}; gridline-color: {RAMKA}; font-size: 16px; }}
QHeaderView::section {{ background: #e3e7ec; border: none; border-right: 1px solid {RAMKA}; border-bottom: 1px solid {RAMKA};
                        padding: 4px 6px; font-size: 14px; font-weight: 700; }}
QProgressBar {{ border: 1px solid {RAMKA}; border-radius: 5px; background: #e3e7ec; text-align: center; font-size: 13px; min-height: 18px; }}
QProgressBar::chunk {{ background: {AKCENT}; border-radius: 4px; }}
QScrollArea {{ border: none; background: transparent; }}
"""
