"""styl - rozmiary i arkusz ekranu PORANNEGO w jego dotychczasowym ukladzie (do etapu U1b nowego okna).

Od paczki E3-U1a wyglad okna jest w ``motyw`` (kolory, czcionki, arkusz nowego szkieletu i trybu wieczornego). Ten plik
zostaje tylko dla ``ekran_rano`` / ``kandydaci`` / ``mapa_rano`` / ``okno_excela``: dwa zestawy rozmiarow (``ZWYKLE``,
``ZWARTE``) i arkusz ``arkusz(r)`` nakladany na ekran poranny - z barwami WYLACZNIE z ``motyw`` (ekran poranny jest
"pokolorowany nowym motywem", uklad i wielkosci zostaja). Po etapie U1b plik znika.

Tu NIE MA kolorow ani napisow statusow prac (jedyne zrodlo: ``statusy`` i pola stanu).
"""
from __future__ import annotations

import dataclasses

from . import motyw

CZCIONKA = motyw.CZCIONKI[-1]  # rodzina zapasowa - znana takze w trybie bez ekranu (pomiary ukladu w testach)
ROZMIAR_PODSTAWOWY_PX = 16

# barwy ekranu porannego = barwy motywu
TLO = motyw.TLO
TLO_PANELU = motyw.WGLEBIENIE
RAMKA = motyw.OBWODKA
TEKST = motyw.TEKST
TEKST_SLABY = motyw.TEKST_POMOCNICZY
AKCENT = motyw.AKCENT
AKCENT_JASNY = motyw.WYBOR_TLO
NIEAKTYWNY_TLO = motyw.WGLEBIENIE
NIEAKTYWNY_TEKST = motyw.TEKST_PRZYGASZONY

# poziom komunikatu -> (tlo, obwodka, tekst)
POZIOMY = {poziom: (tlo, obwodka, motyw.TEKST) for poziom, (tlo, obwodka) in motyw.POZIOMY.items()}

# okno mniejsze niz to (szerokosc albo wysokosc) = uklad zwarty
PROG_ZWARTEGO = motyw.PROG_ZWARTEGO
MINIMUM_OKNA = motyw.MINIMUM_OKNA


@dataclasses.dataclass(frozen=True)
class Rozmiary:
    """Rozmiary jednego trybu ukladu ekranu porannego (piksele logiczne)."""

    zwarty: bool
    margines: int  # brzeg okna
    odstep: int  # odstep pionowy miedzy czesciami
    odstep_kolumn: int
    szerokosc_listy_plytek: int
    szerokosc_prawej: int
    wysokosc_decyzji: int
    wysokosc_przycisku: int  # przyciski pytan i komunikatow
    wysokosc_drugiego_rzedu: int
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


def kontrast(hex_a: str, hex_b: str) -> float:
    return motyw.kontrast(hex_a, hex_b)


def tekst_na(hex_: str) -> str:
    """Kolor napisu na tle ``hex_`` (kolor statusu ze stanu) - jak w ``motyw.tekst_na``."""
    return motyw.tekst_na(hex_)


def arkusz(r: Rozmiary = ZWYKLE) -> str:
    """Arkusz ekranu porannego w trybie ``r`` (barwy z ``motyw``, wielkosci dotychczasowe). Zawiera tez role paneli pytan
    i komunikatow z ``czesci.PanelUwagi`` - w wielkosciach ekranu porannego."""
    m = motyw
    uwaga_tlo, uwaga_obwodka = m.POZIOMY["ostrzezenie"]
    info_tlo, info_obwodka = m.POZIOMY["info"]
    return f"""
QWidget {{ color: {m.TEKST}; font-family: {m.RODZINY_CSS}; font-size: {r.podstawowa}px; }}
QFrame[rola="panel"] {{ background: {m.WGLEBIENIE}; border: 1px solid {m.LINIA}; border-radius: {m.PROMIEN}px; }}
QLabel {{ background: transparent; border: none; }}
QLabel[rola="podpis"] {{ color: {m.TEKST_POMOCNICZY}; font-size: {r.podpis}px; }}
QLabel[rola="wartosc"] {{ font-size: {r.wartosc}px; font-weight: 600; }}
QLabel[rola="naglowek"] {{ font-size: {r.naglowek}px; font-weight: 600; }}
QLabel[rola="tytul"] {{ font-size: {r.tytul}px; font-weight: 600; }}
QLabel[rola="duzy"] {{ font-size: {r.duzy}px; font-weight: 600; }}
QLabel[rola="slaby"] {{ color: {m.TEKST_POMOCNICZY}; font-size: {r.slaby}px; }}
QLabel[rola="tresc"] {{ color: {m.TEKST_POMOCNICZY}; font-size: {r.podstawowa}px; }}
QLabel[rola="tresc_glowna"] {{ color: {m.TEKST}; font-size: {r.duzy}px; font-weight: 600; }}
QLabel[rola="uwaga"] {{ color: {m.TEKST}; background: {uwaga_tlo}; border: 1px solid {uwaga_obwodka}; border-radius: {m.PROMIEN}px;
                        padding: {"3px 6px" if r.zwarty else "6px 8px"}; font-size: {r.uwaga}px; font-weight: 600; }}
QLabel[rola="informacja"] {{ color: {m.TEKST}; background: {info_tlo}; border: 1px solid {info_obwodka}; border-radius: {m.PROMIEN}px;
                             padding: {"3px 6px" if r.zwarty else "6px 8px"}; font-size: {r.uwaga}px; }}
QPushButton {{ background: transparent; color: {m.TEKST}; border: 1px solid {m.OBWODKA}; border-radius: {m.PROMIEN}px;
               padding: {r.dopelnienie}; font-size: {r.przycisk}px; font-weight: 600; }}
QPushButton:hover {{ background: {m.SEGMENT}; }}
QPushButton:pressed {{ background: {m.WYBOR_TLO}; border-color: {m.AKCENT}; }}
QPushButton:checked {{ background: {m.AKCENT}; color: {m.NA_AKCENCIE}; border: 1px solid {m.AKCENT}; }}
QPushButton:focus {{ border: 1px solid {m.AKCENT_FOKUS}; padding: {r.dopelnienie}; }}
QPushButton:disabled {{ background: {m.WGLEBIENIE}; color: {m.TEKST_PRZYGASZONY}; border: 1px dashed {m.OBWODKA}; }}
QPushButton[rola="glowny"] {{ background: {m.AKCENT}; color: {m.NA_AKCENCIE}; border: 1px solid {m.AKCENT}; font-size: {r.glowny}px;
                             font-weight: 600; padding: 2px 12px; }}
QPushButton[rola="glowny"]:hover {{ background: {m.AKCENT_JASNY}; }}
QPushButton[rola="glowny"]:focus {{ border: 1px solid {m.TEKST}; padding: 2px 12px; }}
QPushButton[rola="glowny"]:disabled {{ background: {m.WGLEBIENIE}; color: {m.TEKST_PRZYGASZONY}; border: 1px dashed {m.OBWODKA}; }}
QPushButton[rola="wglebiony"] {{ background: {m.WGLEBIENIE}; }}
QPushButton[rola="wglebiony"]:hover {{ background: {m.SEGMENT}; }}
QPushButton[rola="cyfra"] {{ background: {m.WGLEBIENIE}; font-size: {r.cyfra}px; font-weight: 600; min-width: {r.min_cyfry}px;
                            min-height: {r.min_cyfry}px; padding: 2px; }}
QPushButton[rola="cyfra"]:focus {{ padding: 2px; }}
QPushButton[rola="lacze"] {{ border: 1px solid {m.LINIA}; font-size: {r.lacze}px; font-weight: 600; color: {m.TEKST};
                            padding: {r.dopelnienie_lacza}; }}
QPushButton[rola="lacze"]:focus {{ border: 1px solid {m.AKCENT_FOKUS}; padding: {r.dopelnienie_lacza}; }}
QPushButton[rola="lacze"]:disabled {{ background: {m.WGLEBIENIE}; color: {m.TEKST_PRZYGASZONY}; border: 1px dashed {m.OBWODKA}; }}
QFrame[rola="kafelek"] {{ background: {m.WGLEBIENIE}; border: 1px solid {m.LINIA}; border-radius: {m.PROMIEN}px; }}
QFrame[rola="kafelek"][wybrany="true"] {{ background: {m.WYBOR_TLO}; border: 1px solid {m.AKCENT}; }}
QFrame[rola="kafelek"]:focus {{ border: 1px solid {m.AKCENT_FOKUS}; }}
QTableWidget {{ background: {m.WGLEBIENIE}; alternate-background-color: {m.WGLEBIENIE}; border: 1px solid {m.LINIA}; gridline-color: {m.LINIA};
                font-size: {r.podstawowa}px; selection-background-color: {m.WYBOR_TLO}; selection-color: {m.TEKST}; }}
QTableWidget::item {{ border: none; padding: 0px; }}
QTableWidget::item:selected {{ background: {m.WYBOR_TLO}; color: {m.TEKST}; }}
QHeaderView {{ background: {m.POWIERZCHNIA}; }}
QHeaderView::section {{ background: {m.POWIERZCHNIA}; color: {m.TEKST_POMOCNICZY}; border: none; border-right: 1px solid {m.LINIA};
                        border-bottom: 1px solid {m.LINIA}; padding: {"2px 2px" if r.zwarty else "4px 6px"};
                        font-size: {r.naglowek_tabeli}px; font-weight: 600; }}
QProgressBar {{ border: 1px solid {m.LINIA}; border-radius: {m.PROMIEN}px; background: {m.SEGMENT}; text-align: center;
                font-size: {r.podpis}px; min-height: {14 if r.zwarty else 18}px; max-height: {14 if r.zwarty else 18}px; }}
QProgressBar::chunk {{ background: {m.AKCENT}; border-radius: 3px; }}
QScrollArea {{ border: none; background: transparent; }}
QLineEdit {{ background: {m.WGLEBIENIE}; color: {m.TEKST}; border: 1px solid {m.OBWODKA}; border-radius: {m.PROMIEN}px; padding: 4px 8px;
             font-size: {r.podstawowa}px; selection-background-color: {m.AKCENT}; selection-color: {m.NA_AKCENCIE}; }}
QLineEdit:focus {{ border: 1px solid {m.AKCENT_FOKUS}; }}
"""


ARKUSZ = arkusz(ZWYKLE)
