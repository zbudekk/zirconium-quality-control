"""motyw - kolory, czcionki, rozmiary i arkusz Qt okna programu "Stanowisko" (paczka E3-U1a; ``etap3/nowy_interfejs/SPEC.md`` p. 2).

JEDNO miejsce wygladu okna: zadna inna czesc ``ui/`` nie wpisuje wlasnych barw, czcionek, promieni ani odstepow. Kolorow
STATUSOW prac tutaj NIE MA - sa wylacznie w ``statusy`` i w polach stanu (``rgb``); motyw podaje tylko kolor napisu na kolorze
statusu (``tekst_na``) i sposob, w jaki status odroznia sie nie tylko barwa (obwodka gniazda z ubytkiem, obwodka przerywana
pustego gniazda, pierscien wybranego gniazda).

Modul nie importuje Qt na poziomie modulu (test kontrastu i ``import stanowisko.ui`` dzialaja bez PySide6); ``czcionka``
laduje ``QFont`` dopiero przy wywolaniu.

Kontrast: kazda para "napis / tlo" uzywana w oknie jest w ``PARY_KONTRASTU`` (i ``pary_statusow()`` - napis na kolorze kazdego
statusu ze ``statusy``); test ``testy/test_ui_motyw.py`` wymaga co najmniej ``KONTRAST_MIN`` : 1 dla kazdej.
"""
from __future__ import annotations

import dataclasses

# --- kolory (SPEC p. 2) -----------------------------------------------------------------------------------------------
TLO = "#191919"  # tlo okna
POWIERZCHNIA = "#303030"  # paski, panel pracy
WGLEBIENIE = "#242424"  # kafelki, pola, pasek stanu, plytka na mapie
AKCENT = "#338CED"  # wybor, glowna akcja, fokus
AKCENT_JASNY = "#4A9BF0"  # glowna akcja pod kursorem myszy
NA_AKCENCIE = "#0F1720"  # napis na akcencie
AKCENT_TEKST = "#9CC9F9"  # akcent jako tekst na powierzchni
AKCENT_FOKUS = "#6FB0F5"  # obwodka elementu z fokusem klawiatury, kursor gniazda
WYBOR_TLO = "#1D2733"  # tlo wybranej pozycji i pytania (z obwodka w kolorze akcentu)
SEGMENT = "#3A3A3A"  # wybrana czesc przelacznika zakresu listy, przycisk pod kursorem myszy
LINIA = "#3F3F3F"  # linie na powierzchni
LINIA_TLA = "#2B2B2B"  # linie na tle okna
OBWODKA = "#4A4A4A"  # obwodki pol i zwyklych przyciskow
OBWODKA_MOCNA = "#6A6A6A"  # przycisk "OK", obwodka przerywana pustego gniazda
OBWODKA_SKROTU = "#8A8A8A"  # ramka skrotu klawiszowego na przycisku neutralnym
TEKST = "#F2F2F2"
TEKST_POMOCNICZY = "#B8B8B8"
TEKST_PRZYGASZONY = "#9E9E9E"  # tylko na TLO i WGLEBIENIE
NA_STATUSIE = "#111111"  # napis na kolorze statusu - zawsze ten sam
OBWODKA_UBYTKU = "#F2F2F2"  # jasna obwodka 2 px gniazda z ubytkiem (status nie tylko barwa)
TLO_MINIATURY = "#000000"  # E3-U1b: tlo miniatury projektu (obraz z indeksu ma czarne tlo - ramka w tym samym kolorze)

# poziom komunikatu -> (tlo, obwodka); napis zawsze TEKST / TEKST_POMOCNICZY. Bez paskow z lewej strony, bez zieleni:
# zielone na ekranie znaczy wylacznie "praca sprawdzona, cala" i pochodzi ze stanu
POZIOMY = {
    "pytanie": (WYBOR_TLO, AKCENT),  # pytanie do technika: tlo wybranej pozycji z obwodka akcentu (SPEC p. 2)
    "info": (WYBOR_TLO, AKCENT),
    "ostrzezenie": ("#2B2616", "#C9A227"),
    "blad": ("#2E1C1D", "#D9575B"),
}
POZIOM_DOMYSLNY = "ostrzezenie"

KONTRAST_MIN = 4.5

# --- czcionka i ksztalt -----------------------------------------------------------------------------------------------
CZCIONKI = ("Segoe UI Variable Text", "Segoe UI")  # druga = zapas (takze tryb bez ekranu: Qt nie zna tam nazwanej odmiany "Text")
PX_POMOCNICZY = 12
PX_TRESC = 13
PX_PODSTAWOWY = 14
PX_PRZYCISK_DECYZJI = 15
PX_NUMER_PLYTKI = 15
PX_TYTUL_PRACY = 18
PX_WARTOSC = 18
PX_NAGLOWEK_PLYTKI = 20
PX_KUWETA = 64  # numer biezacej kuwety (poranek, U1b)
PX_KUWETA_ZWARTY = 48  # E3-U1b: numer biezacej kuwety w ukladzie zwartym (okno 1280 x 720 - miejsce na mapy plytek)
PX_POLE_KUWETY = 20  # E3-U1b: wpisywany numer kuwety (pole "Inna kuweta")
PX_MINIATURY = 11  # E3-U1b: napis "brak miniatury" w ramce miniatury
MINIATURA_KANDYDATA = 72  # E3-U1b: bok miniatury kandydata w kolumnie "Praca" (makieta 72 px; uklad zwarty 56)
MINIATURA_KANDYDATA_ZWARTY = 56
PROMIEN = 4
PROMIEN_ZNACZNIKA = 3
SIATKA = (4, 8, 12, 16, 20)  # odstepy
CEL_KLIKNIECIA = 44  # najmniejsza wysokosc przycisku akcji (przyciski paska stanu sa mniejsze - makieta)
# wysokosc przycisku wg roli (piksele): akcje 44 (SPEC), przyciski pomocnicze nizsze - jak na makiecie (pasek stanu 22-24, przelaczniki 30-34)
WYSOKOSCI = {"zakladka": 40, "lacze": 30, "stan": 22, "stan_blad": 22, "cyfra": 40, "osoba": 40, "segment_lewy": 34, "segment_prawy": 34, "zakres_lewy": 28,
             "zakres_prawy": 28, "czekanie": 34}
WYSOKOSC_PRZYCISKU = 36  # przycisk bez wlasnej roli w ``WYSOKOSCI``, ktoremu wolajacy nie podal wysokosci
SZEROKOSC_CYFRY = 44

WYSOKOSC_PASKA_GORNEGO = 52
WYSOKOSC_PASKA_STANU = 32
PROG_ZWARTEGO = (1500, 860)  # okno wezsze albo nizsze = uklad zwarty (kolumny 240 / 320, odstepy 12)
PROG_WYSOKIEGO = 1000  # od tej wysokosci okna: wiecej wierszy listy "do dofrezowania"
MINIMUM_OKNA = (1240, 640)  # okno zmaksymalizowane na ekranie 1920 x 1080 ze skalowaniem 150 % (1280 x 720 minus pasek zadan i belka)


@dataclasses.dataclass(frozen=True)
class Uklad:
    """Rozmiary jednego ukladu okna (piksele logiczne). Wszystkie wysokosci nad i pod mapa sa STALE dla ukladu - mapa zmienia
    miejsce i wielkosc tylko przy zmianie rozmiaru okna, nigdy przy zmianie stanu."""

    nazwa: str
    zwarty: bool
    lewa: int  # kolumna "Plytki tej zmiany"
    prawa: int  # kolumna "Praca"
    bok: int  # odstep tresci od krawedzi kolumny
    odstep: int
    strefa: int  # stala wysokosc strefy pytan i komunikatow
    naglowek: int  # stala wysokosc naglowka plytki (dwa wiersze: numer plytki i znak poprzedniej plytki; opis skanu)
    wiersze_listy: int  # widoczne wiersze listy "do dofrezowania" (reszta przewijana)
    wiersz_tabeli: int
    naglowek_tabeli: int
    naglowek_listy: int  # wiersz z tytulem listy i przelacznikiem zakresu
    boczny: int  # panel obok mapy: legenda, prace poza gniazdami, polecenia plytki
    decyzja: int  # wysokosc "Ukruszona" / "OK"
    przycisk: int  # wysokosc pozostalych przyciskow akcji
    mapa_min: tuple
    obraz_min: int
    # E3-U1b (tryb poranny): stale wysokosci nad mapami plytek - pasek zakladek i wiersz "Teraz rozkladasz"
    zakladki: int = 50
    kuweta: int = 128
    mapa_rano_min: tuple = (150, 140)
    prawa_rano: int = 340  # kolumna "Praca" rano (SPEC: 340-360 px) - wiecej miejsca na trzy mapy plytek pieca obok siebie
    bok_rano: int = 12  # odstep map i wiersza kuwety od krawedzi srodka

    @property
    def lista(self) -> int:
        """Stala wysokosc sekcji "Do dofrezowania" (naglowek, naglowek tabeli, wiersze, odstep pod tabela)."""
        return self.naglowek_listy + self.naglowek_tabeli + self.wiersze_listy * self.wiersz_tabeli + self.odstep


UKLAD_WYSOKI = Uklad("wysoki", False, lewa=280, prawa=360, bok=20, odstep=16, strefa=148, naglowek=56,
                     wiersze_listy=4, wiersz_tabeli=30, naglowek_tabeli=28, naglowek_listy=48, boczny=208, decyzja=52, przycisk=44,
                     mapa_min=(300, 280), obraz_min=110)
UKLAD_ZWYKLY = dataclasses.replace(UKLAD_WYSOKI, nazwa="zwykly", wiersze_listy=3, obraz_min=70)
UKLAD_ZWARTY = Uklad("zwarty", True, lewa=240, prawa=320, bok=12, odstep=12, strefa=148, naglowek=54,
                     wiersze_listy=2, wiersz_tabeli=26, naglowek_tabeli=26, naglowek_listy=44, boczny=176, decyzja=48, przycisk=44,
                     mapa_min=(220, 180), obraz_min=36, zakladki=36, kuweta=84, mapa_rano_min=(120, 110), prawa_rano=320)


def uklad_dla(szerokosc: int, wysokosc: int) -> Uklad:
    """Uklad dla okna ``szerokosc`` x ``wysokosc`` punktow: zwarty ponizej ``PROG_ZWARTEGO``, wysoki od ``PROG_WYSOKIEGO``."""
    if szerokosc < PROG_ZWARTEGO[0] or wysokosc < PROG_ZWARTEGO[1]:
        return UKLAD_ZWARTY
    return UKLAD_WYSOKI if wysokosc >= PROG_WYSOKIEGO else UKLAD_ZWYKLY


# --- kontrast ---------------------------------------------------------------------------------------------------------
def _liniowa(skladowa: int) -> float:
    c = skladowa / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def jasnosc_wzgledna(hex_: str) -> float:
    """Jasnosc wzgledna koloru ``#rrggbb`` (0-1) jak w zaleceniach dostepnosci WCAG."""
    r, g, b = int(hex_[1:3], 16), int(hex_[3:5], 16), int(hex_[5:7], 16)
    return 0.2126 * _liniowa(r) + 0.7152 * _liniowa(g) + 0.0722 * _liniowa(b)


def kontrast(hex_a: str, hex_b: str) -> float:
    a, b = jasnosc_wzgledna(hex_a), jasnosc_wzgledna(hex_b)
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


def tekst_na(hex_: str) -> str:
    """Kolor napisu na tle ``hex_`` (kolor statusu ze stanu): ``NA_STATUSIE`` zawsze, gdy ma kontrast co najmniej
    ``KONTRAST_MIN`` (kazdy kolor ze ``statusy`` - pilnuje tego test); dla ciemnego koloru spoza tabeli - ``TEKST``."""
    return NA_STATUSIE if kontrast(hex_, NA_STATUSIE) >= KONTRAST_MIN else TEKST


def tekst_pustego(hex_: str) -> str:
    """Kolor numeru gniazda bez pracy (wypelnienie ``hex_`` ze stanu - zwykle kolor plytki): napis pomocniczy albo ciemny."""
    return TEKST_POMOCNICZY if kontrast(hex_, TEKST_POMOCNICZY) >= KONTRAST_MIN else NA_STATUSIE


# (opis, napis, tlo) - kazda para napis / tlo uzyta w arkuszu i w rysowaniu; test wymaga KONTRAST_MIN dla kazdej
PARY_KONTRASTU = (
    ("tekst glowny na tle okna", TEKST, TLO),
    ("tekst glowny na powierzchni", TEKST, POWIERZCHNIA),
    ("tekst glowny na wglebieniu", TEKST, WGLEBIENIE),
    ("tekst glowny na tle wybranej pozycji", TEKST, WYBOR_TLO),
    ("tekst glowny na wybranej czesci przelacznika", TEKST, SEGMENT),
    ("tekst pomocniczy na tle okna", TEKST_POMOCNICZY, TLO),
    ("tekst pomocniczy na powierzchni", TEKST_POMOCNICZY, POWIERZCHNIA),
    ("tekst pomocniczy na wglebieniu", TEKST_POMOCNICZY, WGLEBIENIE),
    ("tekst pomocniczy na tle wybranej pozycji", TEKST_POMOCNICZY, WYBOR_TLO),
    ("tekst pomocniczy na przycisku pod kursorem", TEKST_POMOCNICZY, SEGMENT),
    ("tekst przygaszony na tle okna", TEKST_PRZYGASZONY, TLO),
    ("tekst przygaszony na wglebieniu (takze przycisk nieaktywny)", TEKST_PRZYGASZONY, WGLEBIENIE),
    ("tekst przygaszony na tle wybranej pozycji", TEKST_PRZYGASZONY, WYBOR_TLO),
    ("napis na akcencie", NA_AKCENCIE, AKCENT),
    ("napis na akcencie pod kursorem", NA_AKCENCIE, AKCENT_JASNY),
    ("akcent jako tekst na powierzchni", AKCENT_TEKST, POWIERZCHNIA),
    ("akcent jako tekst na wglebieniu", AKCENT_TEKST, WGLEBIENIE),
    ("akcent jako tekst na tle okna", AKCENT_TEKST, TLO),
    ("kolor fokusu jako tekst na powierzchni", AKCENT_FOKUS, POWIERZCHNIA),
    ("napis pomocniczy w ramce miniatury", TEKST_POMOCNICZY, TLO_MINIATURY),
    ("obwodka gniazd biezacej kuwety na plytce (mapa poranna)", TEKST, WGLEBIENIE),
    ("pierscien wybranego gniazda na plytce", AKCENT, WGLEBIENIE),
) + tuple((f"tekst glowny na tle komunikatu ({poziom})", TEKST, tlo) for poziom, (tlo, _) in POZIOMY.items()) + tuple(
    (f"tekst pomocniczy na tle komunikatu ({poziom})", TEKST_POMOCNICZY, tlo) for poziom, (tlo, _) in POZIOMY.items())


def pary_statusow() -> tuple:
    """(opis, napis, tlo) dla KAZDEGO koloru ekranu ze ``statusy`` (wieczor i poranek): napis ``tekst_na`` / ``tekst_pustego``
    na kolorze statusu. Kolory statusow sa w ``statusy`` - tutaj tylko sprawdzenie czytelnosci napisu na nich."""
    from .. import statusy as ST  # noqa: PLC0415 - modul bez Qt; import tutaj, zeby motyw dalo sie czytac bez pakietu

    pary = []
    for wiersz in tuple(ST.STATUSY.values()) + tuple(ST.STATUSY_RANO_WIERSZE.values()):
        napis = tekst_pustego(wiersz.hex) if wiersz.klucz == "pusty" else NA_STATUSIE
        pary.append((f"napis na kolorze statusu {wiersz.klucz}", napis, wiersz.hex))
    return tuple(pary)


# --- czcionka do rysowania (mapa, przyciski ze skrotem) -----------------------------------------------------------------
def czcionka(px: float, pogrubiona: bool = False):
    """``QFont`` ekranu o wysokosci ``px`` pikseli: rodziny ``CZCIONKI`` (z zapasem), cyfry tabelaryczne."""
    from PySide6.QtGui import QFont  # noqa: PLC0415 - Qt dopiero przy rysowaniu

    f = QFont()
    f.setFamilies(list(CZCIONKI))
    f.setPixelSize(max(7, int(px)))
    if pogrubiona:
        f.setWeight(QFont.Weight.DemiBold)
    try:
        f.setFeature(QFont.Tag("tnum"), 1)  # cyfry tabelaryczne (Qt od 6.7); starsze Qt: cyfry Segoe UI sa i tak rownej szerokosci
    except (AttributeError, TypeError, ValueError):
        pass
    return f


RODZINY_CSS = ", ".join(f'"{nazwa}"' for nazwa in CZCIONKI)


def styl_znacznika(hex_: str, px: int = PX_TRESC, wysokosc: int | None = None) -> str:
    """Arkusz znacznika statusu: prostokat w kolorze ``hex_`` (kolor podaje wolajacy - ze stanu albo ze ``statusy``)."""
    minimum = f" min-height: {wysokosc}px;" if wysokosc else ""
    return (f"background: {hex_}; color: {tekst_na(hex_)}; border: none; border-radius: {PROMIEN_ZNACZNIKA}px; padding: 2px 10px; "
            f"font-size: {px}px; font-weight: 600;{minimum}")


def styl_znaczka_poziomu(poziom: str, px: int = PX_POMOCNICZY) -> str:
    """Arkusz malego znaczka w barwach poziomu komunikatu (np. "plytka poranna - dopuszczona swiadomie")."""
    tlo, obwodka = POZIOMY.get(poziom, POZIOMY[POZIOM_DOMYSLNY])
    return (f"background: {tlo}; color: {TEKST}; border: 1px solid {obwodka}; border-radius: {PROMIEN_ZNACZNIKA}px; padding: 1px 6px; "
            f"font-size: {px}px; font-weight: 600;")


def styl_miniatury(px: int = PX_MINIATURY) -> str:
    """E3-U1b: arkusz ramki miniatury projektu (poranek): czarne tlo obrazu z indeksu, obwodka pola, napis "brak miniatury"."""
    return (f"background: {TLO_MINIATURY}; border: 1px solid {OBWODKA}; border-radius: {PROMIEN}px; color: {TEKST_POMOCNICZY}; "
            f"font-size: {px}px;")


def styl_przycisku_statusu(hex_: str) -> str:
    """Arkusz przycisku wypelnionego kolorem statusu ``hex_`` ze ``statusy`` ("Ukruszona" = czerwony statusu)."""
    return (f"QPushButton {{ background: {hex_}; color: {tekst_na(hex_)}; border: 1px solid {hex_}; border-radius: {PROMIEN}px; "
            f"font-size: {PX_PRZYCISK_DECYZJI}px; font-weight: 600; }}"
            f"QPushButton:focus {{ border: 2px solid {TEKST}; }}"
            f"QPushButton:disabled {{ background: {WGLEBIENIE}; color: {TEKST_PRZYGASZONY}; border: 1px dashed {OBWODKA}; }}")


def arkusz(u: Uklad = UKLAD_WYSOKI) -> str:
    """Arkusz Qt calego okna dla ukladu ``u``. Role (wlasciwosc ``rola``) nadaja czesci okna; kolorow statusow tu nie ma.
    Wysokosci i najmniejsze szerokosci przyciskow ustawia kod (``czesci.przycisk``, ``WYSOKOSCI``), nie arkusz: wlasciwosc
    ``min-height`` arkusza nadpisywalaby ``setMinimumHeight`` przy kazdym odswiezeniu stylu."""
    return f"""
QWidget#okno_stanowiska {{ background: {TLO}; }}
QWidget {{ color: {TEKST}; font-family: {RODZINY_CSS}; font-size: {PX_PODSTAWOWY}px; }}
QToolTip {{ background: {POWIERZCHNIA}; color: {TEKST}; border: 1px solid {LINIA}; padding: 4px 6px; font-size: {PX_TRESC}px; }}
QLabel {{ background: transparent; border: none; }}
QLabel[rola="pomocniczy"] {{ color: {TEKST_POMOCNICZY}; font-size: {PX_POMOCNICZY}px; }}
QLabel[rola="przygaszony"] {{ color: {TEKST_PRZYGASZONY}; font-size: {PX_POMOCNICZY}px; }}
QLabel[rola="tresc"] {{ color: {TEKST_POMOCNICZY}; font-size: {PX_TRESC}px; }}
QLabel[rola="tresc_glowna"] {{ color: {TEKST}; font-size: {PX_TRESC}px; }}
QLabel[rola="wyrozniony"] {{ color: {TEKST}; font-size: {PX_PODSTAWOWY}px; font-weight: 600; }}
QLabel[rola="naglowek_sekcji"] {{ color: {TEKST_POMOCNICZY}; font-size: {PX_TRESC}px; font-weight: 600; }}
QLabel[rola="naglowek"] {{ font-size: {PX_PODSTAWOWY}px; font-weight: 600; }}
QLabel[rola="nazwa_programu"] {{ font-size: {PX_NUMER_PLYTKI}px; font-weight: 600; }}
QLabel[rola="numer_plytki"] {{ font-size: {PX_NUMER_PLYTKI}px; font-weight: 600; }}
QLabel[rola="tytul"] {{ font-size: {PX_NAGLOWEK_PLYTKI}px; font-weight: 600; }}
QLabel[rola="tytul_pracy"] {{ font-size: {PX_TYTUL_PRACY - 2 if u.zwarty else PX_TYTUL_PRACY}px; font-weight: 600; }}
QLabel[rola="wartosc"] {{ font-size: {PX_WARTOSC}px; font-weight: 600; }}
QLabel[rola="stan"] {{ color: {TEKST_POMOCNICZY}; font-size: {PX_POMOCNICZY}px; }}
QLabel[rola="stan_wartosc"] {{ color: {TEKST}; font-size: {PX_POMOCNICZY}px; }}
QLabel[rola="stan_uwaga"] {{ color: {TEKST}; font-size: {PX_POMOCNICZY}px; font-weight: 600; background: {POZIOMY["ostrzezenie"][0]};
                             border: 1px solid {POZIOMY["ostrzezenie"][1]}; border-radius: {PROMIEN_ZNACZNIKA}px; padding: 0px 5px; }}
QLabel[rola="osoba"] {{ font-size: {PX_PODSTAWOWY}px; font-weight: 600; }}
QLabel[rola="osoba_brak"] {{ font-size: {PX_PODSTAWOWY}px; font-weight: 600; background: {POZIOMY["ostrzezenie"][0]};
                             border: 1px solid {POZIOMY["ostrzezenie"][1]}; border-radius: {PROMIEN_ZNACZNIKA}px; padding: 2px 8px; }}
QLabel[rola="uwaga"] {{ color: {TEKST}; font-size: {PX_TRESC}px; background: {POZIOMY["ostrzezenie"][0]};
                        border: 1px solid {POZIOMY["ostrzezenie"][1]}; border-radius: {PROMIEN}px; padding: 4px 8px; }}
QLabel[rola="informacja"] {{ color: {TEKST}; font-size: {PX_TRESC}px; background: {POZIOMY["info"][0]};
                             border: 1px solid {POZIOMY["info"][1]}; border-radius: {PROMIEN}px; padding: 4px 8px; }}
QLabel[rola="znaczek_nowa"] {{ background: {AKCENT}; color: {NA_AKCENCIE}; border-radius: {PROMIEN_ZNACZNIKA}px; padding: 1px 6px;
                               font-size: {PX_POMOCNICZY}px; font-weight: 600; }}
QLabel[rola="znaczek_uwaga"] {{ color: {TEKST}; background: {POZIOMY["ostrzezenie"][0]}; border: 1px solid {POZIOMY["ostrzezenie"][1]};
                                border-radius: {PROMIEN_ZNACZNIKA}px; padding: 1px 6px; font-size: {PX_POMOCNICZY}px; font-weight: 600; }}

QLabel[rola="kuweta_numer"] {{ font-size: {PX_KUWETA_ZWARTY if u.zwarty else PX_KUWETA}px; font-weight: 600; }}
QLabel[rola="kuweta_opis"] {{ color: {TEKST_POMOCNICZY}; font-size: {PX_PODSTAWOWY if u.zwarty else 16}px; }}
QLabel[rola="pole"] {{ background: {WGLEBIENIE}; color: {TEKST}; border: 1px solid {OBWODKA}; border-radius: {PROMIEN}px; padding: 0px 14px;
                      font-size: {PX_POLE_KUWETY}px; }}
QLabel[rola="pole_puste"] {{ background: {WGLEBIENIE}; color: {TEKST_PRZYGASZONY}; border: 1px solid {OBWODKA}; border-radius: {PROMIEN}px;
                            padding: 0px 14px; font-size: {PX_POLE_KUWETY}px; }}

QFrame#pasek_gorny {{ background: {POWIERZCHNIA}; border: none; border-bottom: 1px solid {LINIA}; }}
QFrame#pasek_gorny[blysk="true"] {{ border-bottom: 2px solid {AKCENT}; }}
QFrame#pasek_stanu {{ background: {WGLEBIENIE}; border: none; border-top: 1px solid {LINIA}; }}
QFrame#lista_plytek {{ background: {TLO}; border: none; border-right: 1px solid {LINIA_TLA}; }}
QFrame#ramka_pracy {{ background: {POWIERZCHNIA}; border: none; border-left: 1px solid {LINIA}; }}
QFrame#rano_piec {{ background: {TLO}; border: none; border-right: 1px solid {LINIA_TLA}; }}
QFrame#rano_prawa_kolumna {{ background: {POWIERZCHNIA}; border: none; border-left: 1px solid {LINIA}; }}
QFrame#rano_zakladki {{ background: {TLO}; border: none; border-bottom: 1px solid {LINIA_TLA}; }}
QFrame#strefa_komunikatow, QFrame#rano_strefa_komunikatow {{ background: {TLO}; border: none; border-bottom: 1px solid {LINIA_TLA}; }}
QFrame#lista_dofrezowania {{ background: {TLO}; border: none; border-top: 1px solid {LINIA_TLA}; }}
QFrame[rola="przegroda"] {{ background: {LINIA}; border: none; max-height: 1px; min-height: 1px; }}
QFrame[rola="nakladka"] {{ background: {POWIERZCHNIA}; border: 1px solid {OBWODKA}; border-radius: {PROMIEN}px; }}
QFrame[rola="kafelek"] {{ background: {WGLEBIENIE}; border: 1px solid {LINIA}; border-radius: {PROMIEN}px; }}
QFrame[rola="kafelek"][wybrany="true"] {{ background: {WYBOR_TLO}; border: 1px solid {AKCENT}; }}
QFrame[rola="kafelek"]:focus {{ border: 2px solid {AKCENT_FOKUS}; }}
QFrame[rola="karta_mapy"] {{ background: transparent; border: 1px solid transparent; border-radius: {PROMIEN}px; }}
QFrame[rola="karta_mapy"][wybrany="true"] {{ border: 1px solid {AKCENT}; }}
QFrame[rola="kafelek_niezapisany"] {{ background: {POZIOMY["blad"][0]}; border: 1px dashed {POZIOMY["blad"][1]}; border-radius: {PROMIEN}px; }}
QFrame[rola="uwaga_panel"] {{ border-radius: {PROMIEN}px; }}
QFrame[rola="uwaga_panel"][poziom="pytanie"] {{ background: {POZIOMY["pytanie"][0]}; border: 1px solid {POZIOMY["pytanie"][1]}; }}
QFrame[rola="uwaga_panel"][poziom="info"] {{ background: {POZIOMY["info"][0]}; border: 1px solid {POZIOMY["info"][1]}; }}
QFrame[rola="uwaga_panel"][poziom="ostrzezenie"] {{ background: {POZIOMY["ostrzezenie"][0]}; border: 1px solid {POZIOMY["ostrzezenie"][1]}; }}
QFrame[rola="uwaga_panel"][poziom="blad"] {{ background: {POZIOMY["blad"][0]}; border: 1px solid {POZIOMY["blad"][1]}; }}
QFrame[rola="pole_obrazu"] {{ background: {WGLEBIENIE}; border: 1px dashed {OBWODKA_MOCNA}; border-radius: {PROMIEN}px; }}

QPushButton {{ background: transparent; color: {TEKST}; border: 1px solid {OBWODKA}; border-radius: {PROMIEN}px; padding: 4px 14px;
               font-size: {PX_PODSTAWOWY}px; }}
QPushButton:hover {{ background: {SEGMENT}; }}
QPushButton:pressed {{ background: {WYBOR_TLO}; border-color: {AKCENT}; }}
QPushButton:focus {{ border: 2px solid {AKCENT_FOKUS}; padding: 3px 13px; }}
QPushButton:disabled {{ background: {WGLEBIENIE}; color: {TEKST_PRZYGASZONY}; border: 1px dashed {OBWODKA}; }}
QPushButton[rola="glowny"] {{ background: {AKCENT}; color: {NA_AKCENCIE}; border: 1px solid {AKCENT}; font-weight: 600; }}
QPushButton[rola="glowny"]:hover {{ background: {AKCENT_JASNY}; border-color: {AKCENT_JASNY}; }}
QPushButton[rola="glowny"]:pressed {{ background: {AKCENT}; }}
QPushButton[rola="glowny"]:focus {{ border: 2px solid {TEKST}; }}
QPushButton[rola="glowny"]:disabled {{ background: {WGLEBIENIE}; color: {TEKST_PRZYGASZONY}; border: 1px dashed {OBWODKA}; }}
QPushButton[rola="wglebiony"] {{ background: {WGLEBIENIE}; }}
QPushButton[rola="wglebiony"]:hover {{ background: {SEGMENT}; }}
QPushButton[rola="ok"] {{ background: {WGLEBIENIE}; border: 1px solid {OBWODKA_MOCNA}; font-size: {PX_PRZYCISK_DECYZJI}px; font-weight: 600; }}
QPushButton[rola="ok"]:hover {{ background: {SEGMENT}; }}
QPushButton[rola="ok"]:focus {{ border: 2px solid {AKCENT_FOKUS}; }}
QPushButton[rola="ok"]:disabled {{ background: {WGLEBIENIE}; color: {TEKST_PRZYGASZONY}; border: 1px dashed {OBWODKA}; }}
QPushButton[rola="akcent"] {{ color: {AKCENT_TEKST}; border: 1px solid {AKCENT}; }}
QPushButton[rola="akcent"]:focus {{ border: 2px solid {AKCENT_FOKUS}; }}
QPushButton[rola="akcent"]:disabled {{ background: {WGLEBIENIE}; color: {TEKST_PRZYGASZONY}; border: 1px dashed {OBWODKA}; }}
QPushButton[rola="cyfra"] {{ background: {WGLEBIENIE}; font-size: {PX_PRZYCISK_DECYZJI}px; font-weight: 600; padding: 4px 8px; }}
QPushButton[rola="cyfra"]:hover {{ background: {SEGMENT}; }}
QPushButton[rola="cyfra"]:focus {{ padding: 3px 7px; }}
QPushButton[rola="cyfra"]:disabled {{ background: {WGLEBIENIE}; color: {TEKST_PRZYGASZONY}; border: 1px dashed {OBWODKA}; }}
QPushButton[rola="osoba"] {{ background: {WGLEBIENIE}; font-size: {PX_PRZYCISK_DECYZJI}px; font-weight: 600;
                            padding: 4px 18px; }}
QPushButton[rola="osoba"]:hover {{ background: {SEGMENT}; }}
QPushButton[rola="osoba"]:checked {{ background: {AKCENT}; color: {NA_AKCENCIE}; border: 1px solid {AKCENT}; }}
QPushButton[rola="osoba"]:focus {{ border: 2px solid {AKCENT_FOKUS}; padding: 3px 17px; }}
QPushButton[rola="lacze"] {{ color: {TEKST_POMOCNICZY}; border: 1px solid {LINIA}; font-size: {PX_TRESC}px; padding: 3px 12px; }}
QPushButton[rola="lacze"]:hover {{ color: {TEKST}; background: {SEGMENT}; }}
QPushButton[rola="lacze"]:focus {{ border: 2px solid {AKCENT_FOKUS}; padding: 2px 11px; }}
QPushButton[rola="lacze"]:disabled {{ background: {WGLEBIENIE}; color: {TEKST_PRZYGASZONY}; border: 1px dashed {OBWODKA}; }}
QPushButton[rola="stan"] {{ color: {TEKST_POMOCNICZY}; border: 1px solid {OBWODKA}; border-radius: {PROMIEN_ZNACZNIKA}px;
                           font-size: {PX_POMOCNICZY}px; padding: 0px 8px; }}
QPushButton[rola="stan"]:hover {{ color: {TEKST}; background: {SEGMENT}; }}
QPushButton[rola="stan"]:focus {{ border: 2px solid {AKCENT_FOKUS}; padding: 0px 7px; }}
QPushButton[rola="stan"]:disabled {{ background: {WGLEBIENIE}; color: {TEKST_PRZYGASZONY}; border: 1px dashed {OBWODKA}; }}
QPushButton[rola="stan_blad"] {{ color: {TEKST}; background: {POZIOMY["blad"][0]}; border: 1px solid {POZIOMY["blad"][1]};
                                border-radius: {PROMIEN_ZNACZNIKA}px; font-size: {PX_POMOCNICZY}px; font-weight: 600; padding: 0px 8px; }}
QPushButton[rola="stan_blad"]:focus {{ border: 2px solid {AKCENT_FOKUS}; padding: 0px 7px; }}
QPushButton[rola="czekanie"] {{ color: {TEKST_POMOCNICZY}; border: 1px dashed {OBWODKA}; font-size: {PX_TRESC}px; }}
QPushButton[rola="czekanie"]:focus {{ border: 2px solid {AKCENT_FOKUS}; }}
QPushButton[rola="segment_lewy"], QPushButton[rola="segment_prawy"] {{ background: {POWIERZCHNIA}; color: {TEKST_POMOCNICZY};
                           border: 1px solid {OBWODKA}; padding: 4px 16px; }}
QPushButton[rola="segment_lewy"] {{ border-top-right-radius: 0px; border-bottom-right-radius: 0px; }}
QPushButton[rola="segment_prawy"] {{ border-top-left-radius: 0px; border-bottom-left-radius: 0px; }}
QPushButton[rola="segment_lewy"]:checked, QPushButton[rola="segment_prawy"]:checked {{ background: {AKCENT}; color: {NA_AKCENCIE};
                           border-color: {AKCENT}; font-weight: 600; }}
QPushButton[rola="segment_lewy"]:focus, QPushButton[rola="segment_prawy"]:focus {{ border: 2px solid {AKCENT_FOKUS}; padding: 3px 15px; }}
QPushButton[rola="zakladka"] {{ background: transparent; color: {TEKST_POMOCNICZY}; border: none; border-bottom: 2px solid transparent;
                              border-radius: 0px; padding: 0px 14px; }}
QPushButton[rola="zakladka"]:hover {{ color: {TEKST}; background: transparent; }}
QPushButton[rola="zakladka"]:checked {{ color: {TEKST}; border-bottom: 2px solid {AKCENT}; font-weight: 600; }}
QPushButton[rola="zakladka"]:focus {{ border: 2px solid {AKCENT_FOKUS}; padding: 0px 12px; }}
QPushButton[rola="zakladka"]:disabled {{ color: {TEKST_PRZYGASZONY}; background: transparent; border: none; border-bottom: 2px solid transparent; }}
QPushButton[rola="zakres_lewy"], QPushButton[rola="zakres_prawy"] {{ background: transparent; color: {TEKST_POMOCNICZY};
                           border: 1px solid {OBWODKA}; font-size: {PX_TRESC}px; padding: 2px 12px; }}
QPushButton[rola="zakres_lewy"] {{ border-top-right-radius: 0px; border-bottom-right-radius: 0px; }}
QPushButton[rola="zakres_prawy"] {{ border-top-left-radius: 0px; border-bottom-left-radius: 0px; }}
QPushButton[rola="zakres_lewy"]:checked, QPushButton[rola="zakres_prawy"]:checked {{ background: {SEGMENT}; color: {TEKST}; }}
QPushButton[rola="zakres_lewy"]:focus, QPushButton[rola="zakres_prawy"]:focus {{ border: 2px solid {AKCENT_FOKUS}; padding: 1px 11px; }}

QTableWidget {{ background: {TLO}; alternate-background-color: {TLO}; border: none; gridline-color: {LINIA_TLA}; font-size: {PX_TRESC}px;
                selection-background-color: {WYBOR_TLO}; selection-color: {TEKST}; }}
QTableWidget::item {{ border-bottom: 1px solid {LINIA_TLA}; padding: 0px 12px 0px 0px; }}
QTableWidget::item:selected {{ background: {WYBOR_TLO}; color: {TEKST}; }}
QHeaderView {{ background: {TLO}; }}
QHeaderView::section {{ background: {TLO}; color: {TEKST_PRZYGASZONY}; border: none; border-bottom: 1px solid {LINIA};
                        padding: 0px 12px 0px 0px; font-size: {PX_TRESC}px; font-weight: 500; }}
QTableCornerButton::section {{ background: {TLO}; border: none; }}
QProgressBar {{ background: {SEGMENT}; border: none; border-radius: 3px; min-height: 6px; max-height: 6px; }}
QProgressBar::chunk {{ background: {AKCENT}; border-radius: 3px; }}
QScrollArea {{ background: transparent; border: none; }}
QScrollBar:vertical {{ background: transparent; width: 10px; margin: 0px; }}
QScrollBar::handle:vertical {{ background: {OBWODKA}; border-radius: 4px; min-height: 28px; }}
QScrollBar::handle:vertical:hover {{ background: {OBWODKA_MOCNA}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}
QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 0px; }}
QScrollBar::handle:horizontal {{ background: {OBWODKA}; border-radius: 4px; min-width: 28px; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0px; }}
QLineEdit {{ background: {WGLEBIENIE}; color: {TEKST}; border: 1px solid {OBWODKA}; border-radius: {PROMIEN}px; padding: 4px 8px;
             selection-background-color: {AKCENT}; selection-color: {NA_AKCENCIE}; }}
QLineEdit:focus {{ border: 2px solid {AKCENT_FOKUS}; }}
"""
