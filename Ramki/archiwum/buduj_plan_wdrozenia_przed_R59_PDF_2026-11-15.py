#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Buduje PDF z pliku .md w jednym stylu (strona tytułowa, spis treści, nagłówki bieżące):
  - „Stanowisko kontroli cyrkonii — plan wdrozenia v2.md” → .pdf (domyślnie)
  - „Zakupy i druk — stanowisko kontroli cyrkonii.md” → .pdf
  - „Budowa ramki — decyzje i zamienniki.md” → .pdf

Uruchomienie (z folderu Ramki):
    python narzedzia/buduj_plan_wdrozenia.py
    python narzedzia/buduj_plan_wdrozenia.py --md "Zakupy i druk — stanowisko kontroli cyrkonii.md"
    python narzedzia/buduj_plan_wdrozenia.py --md "Budowa ramki — decyzje i zamienniki.md"
    (plik .pdf powstaje obok .md pod tą samą nazwą; --pdf zmienia cel; --html zachowuje HTML do podglądu)
Metadane strony tytułowej dobierane są po nazwie pliku .md (słownik PROFILE poniżej);
opcje --tytul, --podtytul, --opis, --nadtytul je nadpisują.
Wiersz „Wersja” na stronie tytułowej to data i godzina budowy PDF (np. „1 listopada 2026, 18:05”),
ta sama data trafia do stopki każdej strony obok nazwiska autora.

Wejście:  „Stanowisko kontroli cyrkonii — plan wdrozenia v2.md” (ten sam folder)
          wyniki_v2/json/uklad_gniazd_wieczorna.json i _poranna.json (rysunki płytek;
          gdy ich brak, rysunki płytek są pomijane)
Wyjście:  „Stanowisko kontroli cyrkonii — plan wdrozenia v2.pdf” (nadpisywany)

Zależności (wszystkie darmowe; na tym komputerze już zainstalowane w Pythonie 3.14):
    pip install markdown-it-py beautifulsoup4 playwright pypdf reportlab pdfplumber
    python -m playwright install chromium        (jednorazowo pobiera Chromium)
Font: Segoe UI z C:\\Windows\\Fonts (standard w Windows). Na innym systemie podmień
FONT_FILES poniżej na dowolny TTF z polskimi znakami.

Jak to działa (dwa przebiegi):
  1. Markdown → HTML (markdown-it) → przebudowa drzewa (BeautifulSoup): numeracja sekcji,
     strona tytułowa, spis treści, ramki „Uwaga/Decyzja/Do sprawdzenia”, checklisty jako
     tabele, wyrównanie liczb, rysunki SVG (schematy rysowane w tym skrypcie, płytki z JSON).
  2. Chromium (playwright) drukuje HTML do PDF; pdfplumber odczytuje, na której stronie
     zaczyna się każda sekcja; HTML dostaje numery stron w spisie treści i jest drukowany
     ponownie; na koniec reportlab + pypdf nakładają na każdą stronę stopkę („Autor: … · data
     i godzina” po lewej, „strona / liczba stron” po prawej od strony 2) oraz od strony 2
     nagłówek bieżący (tytuł dokumentu / nazwa sekcji).
Treść merytoryczna pochodzi wyłącznie z pliku .md — skrypt niczego nie dopisuje poza
stroną tytułową, spisem treści, etykietami ramek i podpisami rysunków.
"""
import argparse
import base64
import io
import json
import re
import sys
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString
from markdown_it import MarkdownIt

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MD = ROOT / "Stanowisko kontroli cyrkonii — plan wdrozenia v2.md"
DEFAULT_PDF = ROOT / "Stanowisko kontroli cyrkonii — plan wdrozenia v2.pdf"
JSON_DIR = ROOT / "wyniki_v2" / "json"
FONT_FILES = {
    "regular": Path(r"C:\Windows\Fonts\segoeui.ttf"),
    "bold": Path(r"C:\Windows\Fonts\segoeuib.ttf"),
    "semibold": Path(r"C:\Windows\Fonts\seguisb.ttf"),
}

ACCENT = "#1f5f6b"      # ciemny zielono-niebieski
ACCENT_LIGHT = "#e4eef0"
GREY = "#5a5f63"
RULE = "#c9ced1"

DOC_TITLE = "Stanowisko kontroli cyrkonii — plan wdrożenia"
DOC_SUBTITLE = "Stanowisko ze skanerem laboratoryjnym: kontrola ukruszeń wieczorem, identyfikacja prac rano, automatyczne odhaczanie zleceń"
DOC_KICKER = "Laboratorium protetyczne · frezownia cyrkonii"
DOC_AUTHOR = "Michał Budek"
DOC_STATUS = "do prezentacji i decyzji o teście skanera"
DOC_ABSTRACT = (
    "Dokument opisuje planowane stanowisko kontroli koron i mostów z cyrkonii: wybór skanera, "
    "sposób pracy techników wieczorem i rano, program na laptopie, dwie ramki świetlne z płytkami "
    "na prace, listę zakupów, podział na części zamawiane i drukowane samodzielnie, "
    "koszty, ryzyka i decyzje otwarte. Uwzględnia zamknięty projekt ramek (konstrukcja odporna "
    "na pomiary elektroniki) oraz stan plików do druku."
)
# Data i godzina budowy PDF: ustawiana raz w main(), wspólna dla strony tytułowej, stopki i metadanych
BUILD_STAMP = ""
PROFILE = {
    "Zakupy": dict(
        DOC_TITLE="Zakupy i druk — stanowisko kontroli cyrkonii",
        DOC_SUBTITLE="Co kupujemy, w jakiej kolejności i dlaczego; co drukujemy w drukarni, a co sami, i jak",
        DOC_KICKER="Laboratorium protetyczne · ramki świetlne i płytki",
        DOC_STATUS="lista do zamówień; liczby z planu budowy ramek v2",
        DOC_ABSTRACT=(
            "Dokument zbiera w jednym miejscu wszystko, co trzeba kupić lub wydrukować do dwóch ramek świetlnych "
            "i płytek na prace: kolejność zakupów z uzasadnieniem każdej zależności, pełną listę elektroniki i drobnicy "
            "z parametrami do wyszukania w sklepie, części do drukarni z objętościami i wymaganiami wobec usługodawcy, "
            "części drukowane samodzielnie z PETG na FDM wraz z ustawieniami drukarki, zakupy zależne od pomiarów "
            "oraz checklistę odbioru druku. Zawiera też listę firm: drukarnie PA12 i dostawców pleksi na wymiar. "
            "Każda liczba pochodzi z planu budowy ramek v2 i pliku parametrów."
        ),
    ),
    "Budowa": dict(
        DOC_TITLE="Budowa ramki — decyzje i zamienniki",
        DOC_SUBTITLE="Dlaczego każdy element ramki i płytki jest taki, jaki jest; co można zmienić i co to wymusza; czego nie kupujemy i dlaczego",
        DOC_KICKER="Laboratorium protetyczne · ramki świetlne i płytki",
        DOC_STATUS="dokument towarzyszący planowi wdrożenia v2 i dokumentowi „Zakupy i druk”",
        DOC_ABSTRACT=(
            "Dokument wyjaśnia, dlaczego każdy element ramki świetlnej i płytki na prace jest taki, jaki jest: "
            "skąd wzięły się wymiary, materiały i sposób montażu oraz jakie pomiary i założenia za nimi stoją. "
            "Dla każdego elementu podaje, co można zmienić, jakie zamienniki wchodzą w grę i co taka zmiana wymusza "
            "w pozostałych częściach. Osobno zbiera to, czego nie kupujemy, z uzasadnieniem."
        ),
    ),
}


MIESIACE = ("stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca", "lipca",
            "sierpnia", "września", "października", "listopada", "grudnia")


def build_stamp(now):
    """„1 listopada 2026, 18:05” — polska nazwa miesiąca w dopełniaczu, bez sekund."""
    return f"{now.day} {MIESIACE[now.month - 1]} {now.year}, {now:%H:%M}"

# Akapity zaczynające się od tych fraz stają się ramkami (etykieta, klasa)
CALLOUTS = [
    ("Czego stanowisko nie zrobi:", "Uwaga"),
    ("Gdzie jesteśmy (", "Stan prac"),
    ("Stan prac:", "Stan prac"),
    ("Co jest warunkowe:", "Do sprawdzenia"),
    ("Czego nie kupujemy:", "Uwaga"),
    ("Czego nie da się obejść planem B:", "Uwaga"),
    ("Kiedy wracamy do tablicy:", "Decyzja"),
    ("Jak liczyć wykrywalność uczciwie:", "Uwaga"),
    ("Co może przesunąć tydzień:", "Uwaga"),
    ("Jeśli drukarka FDM nie będzie dostępna:", "Uwaga"),
    ("Co nie jest kryterium odbioru:", "Uwaga"),
    ("Razem bez opcji:", "Razem"),
    ("Model 3D ramki do obejrzenia", "Do obejrzenia"),
    ("Bez wkładek gwintowanych:", "Decyzja"),
    ("Zasada: części widoczne", "Zasada"),
    ("Zasada:", "Zasada"),
    ("Uwaga:", "Uwaga"),
    ("Decyzja:", "Decyzja"),
    ("Do sprawdzenia:", "Do sprawdzenia"),
    ("Dlaczego w tej kolejności:", "Dlaczego"),
    ("Zalecenie ogólne:", "Zalecenie ogólne"),
    ("Rozstrzygnięte", "Rozstrzygnięte"),
]
CHECKLIST_HEADINGS = ("D. Checklista dnia (wieczór)", "E. Checklista dnia (poranek)")
NUM_RE = re.compile(
    r"^(ok\.\s|≈\s?|≥\s?|≤\s?|<\s?|>\s?|±\s?)?\d[\d\s.,–\-/×:%()+]*"
    r"(\s?(zł|szt\.|mm|cm|tys\. zł|tys\.|h|min|s|°C|cm³|MP|Mpx|µm|A|V|GB|kg|%|px|m|USD|pkt|szt))?"
    r"(\s?\(.*\))?\s*$"
)


# ----------------------------------------------------------------------------- SVG
def svg_box(x, y, w, h, title, sub="", fill="#ffffff", stroke=RULE, bold=True, fs=11):
    t = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{fill}" stroke="{stroke}" stroke-width="1.2"/>'
    cy = y + h / 2 + (0 if sub else 4)
    t += f'<text x="{x + w/2}" y="{cy - (7 if sub else 0)}" text-anchor="middle" font-size="{fs}" font-weight="{600 if bold else 400}" fill="#1a1a1a">{title}</text>'
    if sub:
        t += f'<text x="{x + w/2}" y="{cy + 9}" text-anchor="middle" font-size="{fs-1.5}" fill="{GREY}">{sub}</text>'
    return t


def svg_arrow(x1, y1, x2, y2, label="", above=True):
    t = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{GREY}" stroke-width="1.2" marker-end="url(#ar)"/>'
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2 + (-5 if above else 12)
        t += f'<text x="{mx}" y="{my}" text-anchor="middle" font-size="9.5" fill="{GREY}">{label}</text>'
    return t


def svg_wrap(w, h, body, font="Segoe UI, Arial, sans-serif"):
    defs = (f'<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{GREY}"/></marker></defs>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" '
            f'font-family="{font}">{defs}{body}</svg>')


def fig_architektura():
    b = ""
    left = [("Skaner laboratoryjny", "STL każdej płytki, 60–90 s"), ("SharePoint „Cyrkon”", "projekty STL (OneDrive)"),
            ("Raporty MillBox", "lista STL i współczynnik"), ("Outlook (prywatne)", "STL z załączników")]
    right = [("Ekran: mapa płytki", "czerwone gniazda, widok 3D"), ("Diody pod gniazdami", "kuweta po kuwecie"),
             ("Excel na SharePoint", "zielone pole w kolumnie B")]
    for i, (t, s) in enumerate(left):
        y = 20 + i * 62
        b += svg_box(10, y, 190, 46, t, s)
        b += svg_arrow(200, y + 23, 250, y + 23)
    b += svg_box(252, 20, 216, 232, "", fill=ACCENT_LIGHT, stroke=ACCENT)
    b += f'<text x="360" y="46" text-anchor="middle" font-size="12" font-weight="600">Program stanowiska</text>'
    b += f'<text x="360" y="62" text-anchor="middle" font-size="9.5" fill="{GREY}">na laptopie, Python</text>'
    for i, s in enumerate(["Wyrównanie do znaczników", "Podział na gniazda", "Dopasowanie 3D do projektu",
                           "Wykrywanie ubytków", "Identyfikacja kuwety", "Sterowanie diodami i ekranem",
                           "Odhaczanie w Excelu"]):
        b += f'<text x="268" y="{88 + i*22}" font-size="10">{s}</text>'
    for i, (t, s) in enumerate(right):
        y = 40 + i * 76
        b += svg_arrow(468, y + 23, 518, y + 23)
        b += svg_box(520, y, 190, 46, t, s)
    return svg_wrap(720, 272, b)


def fig_wieczor():
    b = ""
    b += svg_box(10, 30, 150, 50, "Wycięcie z krążka", "szlif pinów jak dziś")
    b += svg_arrow(160, 55, 188, 55)
    b += svg_box(190, 30, 150, 50, "Prace na płytkę", "skan i analiza, 90 s")
    b += svg_arrow(340, 55, 370, 55)
    # romb
    b += f'<polygon points="430,25 490,55 430,85 370,55" fill="#ffffff" stroke="{RULE}" stroke-width="1.2"/>'
    b += '<text x="430" y="59" text-anchor="middle" font-size="10.5">Czerwone?</text>'
    b += svg_arrow(490, 55, 548, 55, "nie")
    b += svg_box(550, 30, 150, 50, "Opaker i pojemnik", "do pieca jak dziś")
    b += svg_arrow(430, 85, 430, 128, "tak")
    b += svg_box(355, 130, 150, 50, "Oględziny w ręku", "podgląd 3D na ekranie")
    b += svg_arrow(505, 155, 625, 155, "fałszywy alarm")
    b += f'<line x1="625" y1="155" x2="625" y2="82" stroke="{GREY}" stroke-width="1.2" marker-end="url(#ar)"/>'
    b += svg_arrow(355, 155, 162, 155, "ukruszenie")
    b += svg_box(10, 130, 150, 50, "Do dofrezowania", "lista: zlecenie, ząb", fill="#fbeaea", stroke="#b14a4a")
    return svg_wrap(720, 195, b)


def fig_poranek():
    b = ""
    b += svg_box(10, 30, 150, 50, "Pojemnik z pieca", "prace na płytkę, skan")
    b += svg_arrow(160, 55, 188, 55)
    b += svg_box(190, 30, 150, 50, "Identyfikacja", "kuweta każdej pracy")
    b += svg_arrow(340, 55, 370, 55)
    b += f'<polygon points="430,25 490,55 430,85 370,55" fill="#ffffff" stroke="{RULE}" stroke-width="1.2"/>'
    b += '<text x="430" y="59" text-anchor="middle" font-size="10.5">Pewna?</text>'
    b += svg_arrow(490, 55, 548, 55, "tak")
    b += svg_box(550, 30, 160, 50, "Diody: kuweta", "Enter = następna", fill="#e9f3ea", stroke="#3f7d4a")
    b += svg_arrow(430, 85, 430, 128, "nie")
    b += svg_box(355, 130, 150, 50, "Dwóch kandydatów", "podgląd STL i kolor")
    b += svg_arrow(355, 155, 162, 155, "brak kandydata")
    b += svg_box(10, 130, 150, 50, "Praca nieznana", "przymiarka jak dziś")
    b += svg_arrow(630, 80, 630, 128, "po ostatniej płytce", above=False)
    b += svg_box(550, 130, 160, 50, "Zatwierdź: Excel", "komplety na zielono", fill=ACCENT_LIGHT, stroke=ACCENT)
    return svg_wrap(720, 195, b)


def fig_parapet():
    S = 3.4  # px na cm
    b = f'<rect x="10" y="30" width="{200*S}" height="{45*S}" fill="#f6f6f4" stroke="{GREY}" stroke-width="1.5"/>'
    b += f'<text x="{10+100*S}" y="22" text-anchor="middle" font-size="10" fill="{GREY}">okno (zasłona przy skanie) · parapet 200 × 45 cm, widok z góry</text>'
    x = 14
    b += svg_box(x, 40, 38*S, 26*S, "Skaner", "38 × 26 cm", fill="#e4eef0", stroke=ACCENT); x += 38*S + 8
    b += f'<rect x="{x-4}" y="36" width="{20*S+8}" height="{20*S+8}" fill="none" stroke="{RULE}" stroke-dasharray="4 3"/>'
    b += svg_box(x, 40, 20*S, 20*S, "Ramka", "20 × 20 cm", fill="#e9f3ea", stroke="#3f7d4a")
    b += f'<text x="{x+10*S}" y="{40+20*S+22}" text-anchor="middle" font-size="9" fill="{GREY}">osłona od góry</text>'
    x += 20*S + 14
    b += svg_box(x, 40, 36*S, 25*S, "Laptop", "36 × 25 cm", fill="#ececea"); x += 36*S + 12
    b += f'<rect x="{x}" y="40" width="{10+200*S-x-4}" height="{38*S}" fill="none" stroke="{RULE}" stroke-dasharray="5 4" rx="4"/>'
    b += f'<text x="{(x+10+200*S)/2}" y="{40+19*S}" text-anchor="middle" font-size="11" font-weight="600">Wolne ≥ 100 cm</text>'
    b += f'<text x="{(x+10+200*S)/2}" y="{40+19*S+15}" text-anchor="middle" font-size="9.5" fill="{GREY}">opaker, kuwety z całego dnia</text>'
    b += f'<text x="{10+100*S}" y="{30+45*S+16}" text-anchor="middle" font-size="9.5" fill="{GREY}">skaner + ramka + laptop ≈ 100 cm; skan uruchamia spacja na laptopie, ramka bez przycisków</text>'
    return svg_wrap(10 + 200*S + 10, 30 + 45*S + 26, b)


def fig_ramka_przekroj():
    """Przekrój ramki (łańcuch wysokości z planu v2, D4) i rzut z góry. Wszystkie liczby z planu."""
    S = 2.6  # px na mm (pion)
    W = 200 * 1.6
    x0, y0 = 175, 20
    H = 76  # mm wysokości rysunku
    def Y(z): return y0 + (H - z) * S
    b = ""
    # korpus: dno i ściany
    b += f'<rect x="{x0}" y="{Y(3)}" width="{W}" height="{3*S}" fill="#d9dcdf" stroke="{GREY}"/>'
    b += f'<rect x="{x0}" y="{Y(59.6)}" width="{2.5*1.6}" height="{(59.6-3)*S}" fill="#d9dcdf" stroke="{GREY}"/>'
    b += f'<rect x="{x0+W-4}" y="{Y(59.6)}" width="{2.5*1.6}" height="{(59.6-3)*S}" fill="#d9dcdf" stroke="{GREY}"/>'
    # Pi + Bonnet (8..34)
    b += f'<rect x="{x0+30}" y="{Y(34)}" width="{85*1.6}" height="{26*S}" fill="#dfe8df" stroke="{GREY}"/>'
    b += f'<text x="{x0+30+85*0.8}" y="{Y(21)+4}" text-anchor="middle" font-size="9">Raspberry Pi + nakładka (26 mm, z taśmą do 31)</text>'
    # panel PCB 54..55.6, diody do 57.6, elementy od spodu do 42 (zapas 8 nad stosem Pi, R50-1)
    b += f'<rect x="{x0+20*1.6}" y="{Y(54)}" width="{160*1.6}" height="{12*S}" fill="none" stroke="{GREY}" stroke-dasharray="3 2"/>'
    b += f'<text x="{x0+100*1.6}" y="{Y(48)+3}" text-anchor="middle" font-size="8.5" fill="{GREY}">złącza i kondensatory od spodu panelu (12 mm)</text>'
    b += f'<rect x="{x0+20*1.6}" y="{Y(55.6)}" width="{160*1.6}" height="{1.6*S}" fill="#2f6b3a" stroke="{GREY}"/>'
    b += f'<rect x="{x0+20*1.6}" y="{Y(57.6)}" width="{160*1.6}" height="{2*S}" fill="#b9c7bb" stroke="{GREY}"/>'
    b += f'<text x="{x0+100*1.6}" y="{Y(56)+3}" text-anchor="middle" font-size="8.5" fill="#ffffff">panel LED 160 × 160</text>'
    # dystanse
    for xx in (x0+40*1.6, x0+160*1.6):
        b += f'<rect x="{xx-2}" y="{Y(54)}" width="4" height="{50*S}" fill="#c8a24a" stroke="{GREY}" stroke-width="0.6"/>'
    # dyfuzor 61.6..63.6
    b += f'<rect x="{x0+20*1.6}" y="{Y(63.6)}" width="{160*1.6}" height="{2*S}" fill="#eef2f4" stroke="{GREY}"/>'
    # blat 59.6..63.6 (po bokach okna)
    for xx, ww in ((x0, 21*1.6), (x0+179*1.6, 21*1.6)):
        b += f'<rect x="{xx}" y="{Y(63.6)}" width="{ww}" height="{4*S}" fill="#d9dcdf" stroke="{GREY}"/>'
    # wkładka (rama 4 mm szeroka, 6 wysoka) na dyfuzorze, otwór 96.6
    for xx in (x0+(100-52.3)*1.6, x0+(100+48.3)*1.6):
        b += f'<rect x="{xx}" y="{Y(69.6)}" width="{4*1.6}" height="{6*S}" fill="#f4f1ea" stroke="{GREY}"/>'
    # płytka 8 mm na półkach (66.1..74.1)
    b += f'<rect x="{x0+52*1.6}" y="{Y(74.1)}" width="{96*1.6}" height="{8*S}" fill="#f4f1ea" stroke="{GREY}"/>'
    b += f'<text x="{x0+100*1.6}" y="{Y(70)+3}" text-anchor="middle" font-size="8.5">płytka 96 × 96 × 8</text>'
    # wymiary po prawej
    def dim(z1, z2, label, side="r", off=0, ty=None):
        nonlocal b
        dx = (x0 + W + 18 + off) if side == "r" else (x0 - 18 - off)
        mid = (Y(z1) + Y(z2)) / 2
        b += f'<line x1="{dx}" y1="{Y(z1)}" x2="{dx}" y2="{Y(z2)}" stroke="{GREY}" stroke-width="0.8"/>'
        for z in (z1, z2):
            b += f'<line x1="{dx-4}" y1="{Y(z)}" x2="{dx+4}" y2="{Y(z)}" stroke="{GREY}" stroke-width="0.8"/>'
        if side == "r":
            b += f'<text x="{dx+8}" y="{mid+3}" font-size="8.5" fill="{GREY}">{label}</text>'
        else:
            ty = mid if ty is None else ty
            lx = x0 - 100  # wspólna kolumna opisów
            b += f'<line x1="{dx-4}" y1="{mid}" x2="{lx+4}" y2="{ty}" stroke="{GREY}" stroke-width="0.6"/>'
            b += f'<text x="{lx}" y="{ty+3}" font-size="8.5" fill="{GREY}" text-anchor="end">{label}</text>'
    dim(0, 3, "dno 3")
    dim(8, 34, "stos Pi 26")
    dim(34, 42, "zapas 8")
    dim(42, 54, "spód panelu 12")
    # lewa strona: odnośniki rozsunięte co 12 px (od góry: płytka, wkładka, szybka, diody)
    top = Y(74.1)
    dim(66.1, 74.1, "płytka 8", "l", 0, top + 4)
    dim(63.6, 69.6, "wkładka 6", "l", 14, top + 17)
    dim(61.6, 63.6, "szybka 2", "l", 28, top + 30)
    dim(57.6, 61.6, "diody–szybka 4", "l", 42, top + 43)
    b += f'<text x="{x0}" y="{Y(H)+ -4}" font-size="9" fill="{GREY}">Przekrój przez środek ramki (wysokości w mm od zewnętrznego dna; wierzch blatu 63,6; wierzch płytki 74,1)</text>'
    return svg_wrap(x0 + W + 120, Y(0) + 12, b)


def fig_ramka_rzut():
    S = 1.7
    x0, y0 = 30, 24
    def R(x, y, w, h, fill, stroke=GREY, dash=""):
        yy = 200 - y - h  # tył (+y) u góry rysunku
        return f'<rect x="{x0+x*S}" y="{y0+yy*S}" width="{w*S}" height="{h*S}" fill="{fill}" stroke="{stroke}" {("stroke-dasharray=\"" + dash + "\"") if dash else ""}/>'
    b = R(0, 0, 200, 200, "#d9dcdf")                                   # blat 200×200
    b += R(20, 20, 160, 160, "#eef2f4")                                  # szybka 160
    b += R(21, 21, 158, 158, "none", RULE, "3 2")                       # okno 158
    b += R(100-52.3, 100-52.3, 104.6, 104.6, "#f4f1ea")                  # wkładka
    b += R(100-48.3, 100-48.3, 96.6, 96.6, "#eef2f4")                    # otwór wkładki
    b += R(52, 52, 96, 96, "#f8f6f1")                                    # płytka
    b += R(100-65, 100+52.3, 14, 43.7, "#f4f1ea")                         # ucho lewe
    b += R(100+51, 100+52.3, 14, 43.7, "#f4f1ea")                         # ucho prawe
    b += f'<text x="{x0+100*S}" y="{y0+100*S+4}" text-anchor="middle" font-size="10">płytka 96 × 96</text>'
    b += f'<text x="{x0+100*S}" y="{y0+(100-50.3)*S-4}" text-anchor="middle" font-size="8.5" fill="{GREY}">wkładka 104,6 × 104,6 (rama 4 mm)</text>'
    b += f'<text x="{x0+100*S}" y="{y0+16*S}" text-anchor="middle" font-size="8.5" fill="{GREY}">szybka 160 × 160 · okno 158 × 158</text>'
    b += f'<text x="{x0+100*S}" y="{y0+190*S}" text-anchor="middle" font-size="9" fill="{GREY}">PRZÓD · napis na ściance · bez przycisków</text>'
    b += f'<text x="{x0+100*S}" y="{y0+36*S}" text-anchor="middle" font-size="8.5" fill="{GREY}">margines matrycy 27,7 mm = 11 pikseli na cyfry (z każdej strony)</text>'
    b += f'<text x="{x0+(100-58)*S}" y="{y0+(100-78)*S}" text-anchor="middle" font-size="8" fill="{GREY}">ucho</text>'
    b += f'<text x="{x0+(100+58)*S}" y="{y0+(100-78)*S}" text-anchor="middle" font-size="8" fill="{GREY}">ucho</text>'
    b += f'<text x="{x0}" y="{y0-8}" font-size="9" fill="{GREY}">Rzut z góry 200 × 200 mm (blat, szybka, wkładka, płytka; tył u góry)</text>'
    return svg_wrap(x0*2 + 200*S, y0 + 200*S + 10, b)


def opis_gniazd(json_path):
    """„18 gniazd i 1 rynienka” — liczby do podpisu rysunku płytki, z tego samego pliku układu co rysunek."""
    def odmiana(n, jedna, kilka, wiele):
        if n == 1:
            return jedna
        return kilka if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14) else wiele
    gniazda = json.loads(Path(json_path).read_text(encoding="utf-8"))["sockets"]
    okragle = sum(1 for s in gniazda if s["type"] == "round")
    rynienki = len(gniazda) - okragle
    return (f"{okragle} {odmiana(okragle, 'gniazdo', 'gniazda', 'gniazd')} i "
            f"{rynienki} {odmiana(rynienki, 'rynienka', 'rynienki', 'rynienek')}")


def fig_plytka(json_path, title):
    d = json.loads(Path(json_path).read_text(encoding="utf-8"))
    S = 3.2
    pad = 16
    W = 96 * S + 2 * pad
    def X(x): return pad + (x + 48) * S
    def Y(y): return pad + (48 - y) * S
    o = f'<rect x="{pad}" y="{pad}" width="{96*S}" height="{96*S}" rx="4" fill="#f4f1ea" stroke="{GREY}" stroke-width="1.2"/>'
    n = d["notch"]
    o += f'<rect x="{X(n["x_min"])}" y="{Y(n["y_max"])}" width="{(n["x_max"]-n["x_min"])*S}" height="{(n["y_max"]-n["y_min"])*S}" fill="#ffffff" stroke="{GREY}"/>'
    zr = d.get("socket_zone_r", 47)
    o += f'<circle cx="{X(0)}" cy="{Y(0)}" r="{zr*S}" fill="none" stroke="{ACCENT}" stroke-width="0.8" stroke-dasharray="4 3"/>'
    for m in d["markers"]:
        o += f'<circle cx="{X(m["x"])}" cy="{Y(m["y"])}" r="{m["d"]/2*S}" fill="{ACCENT_LIGHT}" stroke="{ACCENT}" stroke-width="1.2"/>'
    for c in d["code_dimples"]:
        o += f'<circle cx="{X(c["x"])}" cy="{Y(c["y"])}" r="{c["d"]/2*S}" fill="#ffffff" stroke="{GREY}"/>'
    seen = set()
    for s in d["sockets"]:
        if s["type"] == "round":
            o += f'<circle cx="{X(s["x"])}" cy="{Y(s["y"])}" r="{s["d_top"]/2*S}" fill="#e6e3dc" stroke="{GREY}"/>'
            o += f'<circle cx="{X(s["x"])}" cy="{Y(s["y"])}" r="{s["hole_d"]/2*S}" fill="#ffffff" stroke="{RULE}" stroke-width="0.7"/>'
            if s["d_top"] not in seen:
                seen.add(s["d_top"])
                lab = f'ø{s["d_top"]:g}'.replace(".", ",")
                o += f'<text x="{X(s["x"])}" y="{Y(s["y"])-s["d_top"]/2*S-2}" font-size="8" text-anchor="middle" fill="{GREY}">{lab}</text>'
        else:
            l, w = s["l"], s["w"]
            o += f'<rect x="{X(s["x"]-l/2)}" y="{Y(s["y"]+w/2)}" width="{l*S}" height="{w*S}" rx="{w/2*S}" fill="#e6e3dc" stroke="{GREY}"/>'
            p, nh = s["hole_pitch"], s["hole_count"]
            for i in range(nh):
                hx = s["x"] - p * (nh - 1) / 2 + i * p
                o += f'<circle cx="{X(hx)}" cy="{Y(s["y"])}" r="{s["hole_d"]/2*S}" fill="#ffffff" stroke="{RULE}" stroke-width="0.7"/>'
            o += f'<text x="{X(s["x"])}" y="{Y(s["y"]+w/2)-3}" font-size="8" text-anchor="middle" fill="{GREY}">rynienka {l:g} × {w:g}</text>'
    nr = d["number_relief"]
    o += f'<text x="{X(nr["x"])}" y="{Y(nr["y"])+3}" font-size="9" font-weight="600" text-anchor="middle" fill="{GREY}">n</text>'
    o += f'<text x="{W/2}" y="{96*S + 2*pad + 12}" font-size="10" text-anchor="middle" fill="#1a1a1a">{title}</text>'
    return svg_wrap(W, 96 * S + 2 * pad + 20, o)


# ----------------------------------------------------------------------------- HTML
def build_html(md_text, toc_pages=None, landscape=False):
    md = MarkdownIt("commonmark").enable("table")
    soup = BeautifulSoup(md.render(md_text), "html.parser")

    # --- usuń h1 i wiersz metadanych (zastępuje je strona tytułowa)
    h1 = soup.find("h1")
    meta_p = h1.find_next_sibling("p") if h1 else None
    if meta_p and "·" in meta_p.get_text() and ("Autor:" in meta_p.get_text() or "wersja" in meta_p.get_text()):
        meta_p.decompose()
    if h1:
        h1.decompose()

    # --- numeracja sekcji i identyfikatory
    toc = []  # (level, number, text, id)
    n2 = 0
    n3 = 0
    in_appendix = False
    for h in soup.find_all(["h2", "h3"]):
        if h.name == "h2":
            n2 += 1
            n3 = 0
            in_appendix = h.get_text(strip=True) == "Załączniki"
            num = f"{n2}."
            hid = f"s{n2}"
            h.string = f"{num} {h.get_text(strip=True)}"
            toc.append((2, h.get_text(strip=True), hid))
        else:
            n3 += 1
            txt = h.get_text(strip=True)
            if in_appendix:
                hid = f"s{n2}-{n3}"
                h.string = txt
            else:
                hid = f"s{n2}-{n3}"
                h.string = f"{n2}.{n3} {txt}"
            toc.append((3, h.get_text(strip=True), hid))
        h["id"] = hid

    # --- ramki
    for p in soup.find_all("p"):
        txt = p.get_text()
        for prefix, label in CALLOUTS:
            if txt.startswith(prefix):
                box = soup.new_tag("div", attrs={"class": "callout"})
                lab = soup.new_tag("div", attrs={"class": "callout-label"})
                lab.string = label
                box.append(lab)
                p.insert_before(box)
                box.append(p.extract())
                # lista bezpośrednio po akapicie z dwukropkiem należy do ramki
                nxt = box.find_next_sibling()
                if txt.rstrip().endswith(":") and nxt is not None and nxt.name in ("ul", "ol"):
                    box.append(nxt.extract())
                break

    # --- checklisty D/E jako tabele z pustą kolumną
    for h in soup.find_all("h3"):
        if h.get_text(strip=True) in CHECKLIST_HEADINGS:
            ul = h.find_next_sibling()
            if ul is None or ul.name != "ul":
                continue
            table = soup.new_tag("table", attrs={"class": "checklist"})
            thead = soup.new_tag("thead")
            tr = soup.new_tag("tr")
            for name, cls in (("Nr", "num"), ("Pozycja", ""), ("Odhaczone", "tick")):
                th = soup.new_tag("th", attrs={"class": cls} if cls else {})
                th.string = name
                tr.append(th)
            thead.append(tr)
            table.append(thead)
            tbody = soup.new_tag("tbody")
            for i, li in enumerate(ul.find_all("li", recursive=False), 1):
                tr = soup.new_tag("tr")
                td = soup.new_tag("td", attrs={"class": "num"}); td.string = str(i); tr.append(td)
                td = soup.new_tag("td")
                for c in list(li.contents):
                    td.append(c.extract() if not isinstance(c, NavigableString) else NavigableString(str(c)))
                tr.append(td)
                td = soup.new_tag("td", attrs={"class": "tick"}); td.append(soup.new_tag("span", attrs={"class": "box"})); tr.append(td)
                tbody.append(tr)
            table.append(tbody)
            ul.replace_with(table)

    # --- tabele: klasy, liczby do prawej, szerokie w poziomie
    for t in soup.find_all("table"):
        rows = t.find_all("tr")
        ncols = max(len(r.find_all(["td", "th"])) for r in rows)
        cls = set(t.get("class", []))
        if len(rows) <= 9 and len(t.get_text()) < 900:
            cls.add("short")
        cells = [td.get_text() for r in rows for td in r.find_all("td")]
        avg_len = sum(map(len, cells)) / max(1, len(cells))
        total = sum(map(len, cells))
        if landscape and ncols >= 5 and total > 4000:
            cls.add("wide")
        elif ncols >= 5 or avg_len > 60:
            cls.add("dense")
        if any(len(c) > 600 for c in cells):
            cls.add("tallrows")
        t["class"] = " ".join(sorted(cls))
        for r in rows:
            for td in r.find_all("td"):
                s = td.get_text(strip=True)
                if s and NUM_RE.match(s) and len(s) <= 28:
                    td["class"] = "num"
                if s in ("—", "–"):
                    td["class"] = "num"
        # szerokości kolumn proporcjonalne do ilości tekstu (bez tego długie komórki zwężają sąsiednie)
        if ncols >= 3 and "checklist" not in cls and len(rows) > 1:
            lens = [0.0] * ncols
            for r in rows[1:]:
                for i, td in enumerate(r.find_all(["td", "th"])[:ncols]):
                    lens[i] += len(td.get_text())
            heads = [th.get_text(strip=True) for th in rows[0].find_all(["td", "th"])]
            w = []
            for i in range(ncols):
                avg = lens[i] / max(1, len(rows) - 1)
                w.append(max(avg, len(heads[i]) * 1.2 if i < len(heads) else 6) ** 0.65)
            tot = sum(w)
            pct = [max(7.0, 100 * x / tot) for x in w]
            pct = [100 * x / sum(pct) for x in pct]
            cg = soup.new_tag("colgroup")
            for pc in pct:
                col = soup.new_tag("col", attrs={"style": f"width:{pc:.1f}%"})
                cg.append(col)
            t.insert(0, cg)
        # pozycja kroków / numerów w pierwszej kolumnie
        first = rows[0].find(["th", "td"])
        if first and first.get_text(strip=True) in ("Krok", "Nr", "Dzień", "Id", "Nr uwagi"):
            for r in rows[1:]:
                c = r.find("td")
                if c:
                    c["class"] = "num"

    # --- rysunki
    def put_fig(marker, svg, caption, replace_text=None):
        for p in soup.find_all("p"):
            if p.get_text().startswith(marker):
                fig = soup.new_tag("figure")
                fig.append(BeautifulSoup(svg, "html.parser"))
                cap = soup.new_tag("figcaption"); cap.string = caption
                fig.append(cap)
                p.replace_with(fig)
                return True
        return False

    put_fig("architektura · 4 źródła danych", fig_architektura(), "Rys. 1. Jeden program łączy skaner, projekty i Excel: cztery źródła danych, jeden program, trzy wyjścia.")
    put_fig("wieczór · 5 kroków", fig_wieczor(), "Rys. 2. Wieczór: technik bierze do ręki tylko czerwone gniazda.")
    put_fig("stanowisko na parapecie · widok z góry", fig_parapet(), "Rys. 6. Stanowisko zajmuje lewą połowę parapetu, prawa zostaje wolna.")

    # poranek: po pierwszym akapicie sekcji „Przepływ poranny”
    for h in soup.find_all("h2"):
        if "Przepływ poranny" in h.get_text():
            p = h.find_next_sibling("p")
            fig = soup.new_tag("figure")
            fig.append(BeautifulSoup(fig_poranek(), "html.parser"))
            cap = soup.new_tag("figcaption"); cap.string = "Rys. 3. Rano diody prowadzą rękę kuweta po kuwecie; Excel po zamknięciu pieca."
            fig.append(cap)
            p.insert_after(fig)
    # płytki: po liście w załączniku A
    for p in soup.find_all("p"):
        if p.get_text().startswith("Układ gniazd (rysunki w wersji PDF;"):
            p.string = p.get_text().replace("(rysunki w wersji PDF;", "(rysunki 4 i 5;")
            ul = p.find_next_sibling("ul")
            wrap = soup.new_tag("div", attrs={"class": "plates"})
            jw = JSON_DIR / "uklad_gniazd_wieczorna.json"
            jp = JSON_DIR / "uklad_gniazd_poranna.json"
            if jw.exists() and jp.exists():
                for jp_, title, cap in ((jw, "Płytka wieczorna", f"Rys. 4. Płytka wieczorna: {opis_gniazd(jw)} w kole o promieniu 47 mm (linia przerywana); przód u dołu, wycięcie orientacyjne w narożniku przód‑prawym."),
                                        (jp, "Płytka poranna", f"Rys. 5. Płytka poranna: {opis_gniazd(jp)} w kole o promieniu 47 mm; układ z pliku współrzędnych gniazd.")):
                    fig = soup.new_tag("figure", attrs={"class": "plate"})
                    fig.append(BeautifulSoup(fig_plytka(jp_, title), "html.parser"))
                    c = soup.new_tag("figcaption"); c.string = cap
                    fig.append(c)
                    wrap.append(fig)
                (ul or p).insert_after(wrap)
            else:
                print("UWAGA: brak plików JSON układu gniazd — rysunki płytek pominięte")
    # ramka: po pierwszym akapicie załącznika B
    for h in soup.find_all("h3"):
        if h.get_text(strip=True).startswith("B. Ramka świetlna"):
            p = h.find_next_sibling("p")
            wrap = soup.new_tag("div", attrs={"class": "ramka-figs"})
            for svg, cap in ((fig_ramka_przekroj(), "Rys. 7. Przekrój ramki: łańcuch wysokości z planu budowy v2 po R50 (dno 3, stos Pi 26, zapas 8, spód panelu 12, panel, odstęp 4, szybka 2, wkładka 6, płytka 8; razem 63,6)."),
                             (fig_ramka_rzut(), "Rys. 8. Rzut z góry: blat 200 × 200, szybka 160 × 160, wkładka 104,6 × 104,6 z uszami, płytka 96 × 96.")):
                fig = soup.new_tag("figure")
                fig.append(BeautifulSoup(svg, "html.parser"))
                c = soup.new_tag("figcaption"); c.string = cap
                fig.append(c)
                wrap.append(fig)
            p.insert_after(wrap)
    for p in soup.find_all("p"):
        if "(schemat w wersji PDF)" in p.get_text():
            p.string = p.get_text().replace(" (schemat w wersji PDF)", "")

    # --- akapit-zapowiedź („Decyzje:”, „Moduły:”) razem z tabelą lub listą
    for p in soup.find_all("p"):
        if p.get_text(strip=True).endswith(":") and len(p.get_text(strip=True)) < 60 and p.parent.name != "div":
            nxt = p.find_next_sibling()
            if nxt is not None and nxt.name in ("table", "ul", "ol"):
                if len(nxt.find_all(["tr", "li"])) <= 6 and len(nxt.get_text()) < 1200:
                    keep = soup.new_tag("div", attrs={"class": "keep"})
                    p.insert_before(keep)
                    keep.append(p.extract())
                    keep.append(nxt.extract())
                else:
                    p["class"] = "lead"

    # --- nagłówek + następny element razem (brak sierot)
    for h in soup.find_all(["h2", "h3"]):
        nxt = h.find_next_sibling()
        if nxt is None:
            continue
        if nxt.find("table") is not None or nxt.name == "table":
            if len(nxt.find_all("tr")) > 6 or len(nxt.get_text()) > 1200:
                continue  # duża tabela: wystarczy break-after: avoid na nagłówku
        keep = soup.new_tag("div", attrs={"class": "keep"})
        h.insert_before(keep)
        keep.append(h.extract())
        keep.append(nxt.extract())

    # --- strona tytułowa i spis treści
    pages = toc_pages or {}
    toc_html = '<section class="toc"><h2 class="toc-title">Spis treści</h2>'
    for level, text, hid in toc:
        pg = pages.get(hid, "")
        toc_html += f'<div class="toc-row l{level}"><span class="toc-text">{text}</span><span class="toc-dots"></span><span class="toc-page">{pg}</span></div>'
    toc_html += "</section>"
    title_html = f'''
<section class="title-page">
  <div class="title-rule"></div>
  <div class="title-kicker">{DOC_KICKER}</div>
  <h1 class="title-main">{DOC_TITLE}</h1>
  <div class="title-sub">{DOC_SUBTITLE}</div>
  <table class="title-meta">
    <tr><td>Wersja</td><td>{BUILD_STAMP}</td></tr>
    <tr><td>Autor</td><td>{DOC_AUTHOR}</td></tr>
    <tr><td>Status</td><td>{DOC_STATUS}</td></tr>
  </table>
  <div class="title-abstract"><div class="callout-label">O dokumencie</div>{DOC_ABSTRACT}</div>
</section>'''
    body = title_html + toc_html + '<section class="content">' + str(soup) + "</section>"

    css = f"""
@font-face {{ font-family: "Segoe UI"; src: local("Segoe UI"); }}
@page {{ size: A4; margin: 20mm 18mm 20mm 18mm; }}
@page wide {{ size: A4 landscape; margin: 18mm 18mm 20mm 18mm; }}
@page title {{ margin: 0; }}
html {{ font-size: 10.3pt; }}
body {{ font-family: "Segoe UI", "Noto Sans", Arial, sans-serif; line-height: 1.32; color: #1a1a1a; margin: 0; }}
section.content {{ max-width: 100%; }}
p {{ margin: 0 0 7pt; text-align: left; hyphens: auto; }}
p.lead {{ break-after: avoid; }}
h2 {{ font-size: 15pt; font-weight: 600; color: {ACCENT}; margin: 22pt 0 7pt; padding-bottom: 3pt; border-bottom: 1px solid {ACCENT}; break-after: avoid; }}
h3 {{ font-size: 11.6pt; font-weight: 600; color: {ACCENT}; margin: 14pt 0 5pt; break-after: avoid; }}
.keep {{ break-inside: avoid; }}
ul, ol {{ margin: 0 0 8pt; padding-left: 20pt; }}
li {{ margin: 0 0 3pt; }}
ol > li {{ padding-left: 3pt; }}
strong {{ font-weight: 600; }}
a {{ color: {ACCENT}; text-decoration: none; word-break: break-all; }}
table {{ border-collapse: collapse; width: 100%; margin: 6pt 0 12pt; font-size: 9pt; line-height: 1.28; }}
th, td {{ padding: 4pt 6pt; vertical-align: top; text-align: left; border: 0; border-bottom: 0.6pt solid {RULE}; }}
th {{ background: {ACCENT_LIGHT}; font-weight: 600; color: #163f47; border-bottom: 1pt solid {ACCENT}; }}
thead {{ display: table-header-group; }}
tr {{ break-inside: avoid; }}
table.tallrows tr {{ break-inside: auto; }}
table.short {{ break-inside: avoid; }}
table.dense {{ font-size: 8.4pt; }}
td.num, th.num {{ text-align: right; white-space: nowrap; }}
th.tick, td.tick {{ width: 60pt; text-align: center; }}
td.tick .box {{ display: inline-block; width: 11pt; height: 11pt; border: 0.9pt solid {GREY}; vertical-align: middle; }}
table.wide {{ page: wide; font-size: 8.8pt; }}
.callout {{ border-left: 3pt solid {ACCENT}; background: #f4f7f8; padding: 6pt 10pt 4pt 10pt; margin: 8pt 0 10pt; break-inside: avoid; }}
.callout p {{ margin-bottom: 4pt; }}
.callout ul, .callout ol {{ margin-bottom: 2pt; }}
.callout-label {{ font-size: 8pt; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: {ACCENT}; margin-bottom: 2pt; }}
figure {{ margin: 10pt 0 12pt; break-inside: avoid; text-align: center; }}
figure svg {{ max-width: 100%; height: auto; }}
figcaption {{ font-size: 8.6pt; color: {GREY}; margin-top: 3pt; text-align: left; }}
.plates {{ display: flex; gap: 14pt; align-items: flex-start; break-inside: avoid; }}
.plates figure {{ width: 50%; margin: 6pt 0; }}
.ramka-figs figure {{ margin: 8pt 0; }}
.ramka-figs figure:first-child svg {{ width: 100%; }}
.ramka-figs figure:last-child svg {{ width: 62%; }}
/* strona tytułowa */
.title-page {{ page: title; height: 297mm; box-sizing: border-box; padding: 60mm 24mm 24mm 24mm; break-after: page; position: relative; }}
.title-rule {{ width: 40mm; height: 2.2pt; background: {ACCENT}; margin-bottom: 16pt; }}
.title-kicker {{ font-size: 10pt; letter-spacing: 0.12em; text-transform: uppercase; color: {GREY}; margin-bottom: 10pt; }}
.title-main {{ font-size: 28pt; font-weight: 600; line-height: 1.15; color: #163f47; margin: 0 0 14pt; }}
.title-sub {{ font-size: 13pt; color: #333; line-height: 1.35; max-width: 140mm; margin-bottom: 28pt; }}
.title-meta {{ width: auto; font-size: 10pt; margin-bottom: 30pt; }}
.title-meta td {{ border: 0; padding: 2pt 18pt 2pt 0; }}
.title-meta td:first-child {{ color: {GREY}; }}
.title-abstract {{ position: absolute; left: 24mm; right: 24mm; bottom: 28mm; font-size: 9.6pt; color: #333; line-height: 1.4; border-top: 0.6pt solid {RULE}; padding-top: 8pt; }}
/* spis treści */
.toc {{ break-after: page; }}
.toc-title {{ margin-top: 0; }}
.toc-row {{ display: flex; align-items: baseline; margin: 0 0 3pt; }}
.toc-row.l2 {{ font-weight: 600; margin-top: 7pt; }}
.toc-row.l3 {{ padding-left: 16pt; font-size: 9.6pt; }}
.toc-text {{ white-space: nowrap; }}
.toc-dots {{ flex: 1; border-bottom: 0.6pt dotted {GREY}; margin: 0 4pt 3pt; min-width: 12pt; }}
.toc-page {{ white-space: nowrap; min-width: 18pt; text-align: right; }}
"""
    return f'<!doctype html><html lang="pl"><head><meta charset="utf-8"><title>{DOC_TITLE}</title><style>{css}</style></head><body>{body}</body></html>', toc


# ----------------------------------------------------------------------------- PDF
def print_pdf(html, html_path, pdf_path):
    from playwright.sync_api import sync_playwright
    html_path.write_text(html, encoding="utf-8")
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.goto(html_path.resolve().as_uri())
        pg.wait_for_timeout(300)
        pg.pdf(path=str(pdf_path), prefer_css_page_size=True, print_background=True, display_header_footer=False)
        b.close()


def heading_pages(pdf_path, toc):
    """Mapa id nagłówka → numer strony (1 = strona tytułowa)."""
    import logging
    import pdfplumber
    logging.getLogger("pdfminer").setLevel(logging.ERROR)
    pages = {}
    texts = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for p in pdf.pages:
            texts.append((p.extract_text() or "").replace("\n", " "))
    start = 2  # pomijamy stronę tytułową; spis treści też zawiera nazwy, więc szukamy od końca spisu
    # strony spisu: te, które zawierają „Spis treści” lub kolejne, zanim pojawi się pierwsza sekcja z treścią
    for i, t in enumerate(texts):
        if "Spis treści" in t:
            start = i + 1
    # koniec spisu: pierwsza strona po start, na której nie ma wielu wierszy spisu
    while start < len(texts) and texts[start].count("....") > 3:
        start += 1
    for level, text, hid in toc:
        needle = re.sub(r"\s+", " ", text)
        for i in range(start, len(texts)):
            if needle in texts[i]:
                pages[hid] = i + 1
                start = i
                break
    return pages


def overlay(pdf_path, toc, pages):
    """Stopka (autor · data) na każdej stronie; nagłówek bieżący i numer strony od strony 2."""
    from pypdf import PdfReader, PdfWriter
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm

    pdfmetrics.registerFont(TTFont("UI", str(FONT_FILES["regular"])))
    bold = FONT_FILES["semibold"] if FONT_FILES["semibold"].exists() else FONT_FILES["bold"]
    pdfmetrics.registerFont(TTFont("UIB", str(bold)))

    reader = PdfReader(str(pdf_path))
    n = len(reader.pages)
    # nazwa sekcji (h2) obowiązująca na stronie
    h2_starts = sorted((pages[hid], text) for level, text, hid in toc if level == 2 and hid in pages)
    def section_for(pn):
        name = None
        for start, text in h2_starts:
            if start < pn:
                name = text
        if name is None:
            same = [text for start, text in h2_starts if start == pn]
            name = same[0] if same else "Spis treści"
        return name

    writer = PdfWriter()
    r, g, b_ = (int(ACCENT[1:3], 16) / 255, int(ACCENT[3:5], 16) / 255, int(ACCENT[5:7], 16) / 255)
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    for i, page in enumerate(reader.pages):
        pn = i + 1
        w = float(page.mediabox.width)
        h = float(page.mediabox.height)
        c.setPageSize((w, h))
        if pn > 1:
            c.setFont("UI", 7.8)
            c.setFillGray(0.38)
            c.drawString(18 * mm, h - 12.5 * mm, DOC_TITLE)
            c.setFont("UIB", 7.8)
            c.setFillColorRGB(r, g, b_)
            sec = section_for(pn)
            c.drawRightString(w - 18 * mm, h - 12.5 * mm, sec[:90])
            c.setStrokeColorRGB(0.79, 0.81, 0.82)
            c.setLineWidth(0.5)
            c.line(18 * mm, h - 14 * mm, w - 18 * mm, h - 14 * mm)
            c.setFont("UI", 8)
            c.setFillGray(0.38)
            c.drawRightString(w - 18 * mm, 11 * mm, f"{pn} / {n}")
        # stopka z autorem i datą budowy — na każdej stronie, także tytułowej
        c.setFont("UI", 7)
        c.setFillGray(0.45)
        c.drawString(18 * mm, 11 * mm, f"Autor: {DOC_AUTHOR} · {BUILD_STAMP}")
        c.showPage()
    c.save()
    buf.seek(0)
    over = PdfReader(buf)
    for i, page in enumerate(reader.pages):
        page.merge_page(over.pages[i])
        writer.add_page(page)
    writer.add_metadata({"/Title": DOC_TITLE, "/Author": DOC_AUTHOR, "/Subject": DOC_SUBTITLE})
    # po scaleniu strumienie treści są nieskompresowane (3,6 MB) — najpierw kompresja, potem deduplikacja (→ ok. 0,8 MB)
    for p in writer.pages:
        p.compress_content_streams(level=9)
    writer.compress_identical_objects(remove_duplicates=True, remove_unreferenced=True)
    with open(pdf_path, "wb") as f:
        writer.write(f)
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", default=str(DEFAULT_MD))
    ap.add_argument("--pdf", default=str(DEFAULT_PDF))
    ap.add_argument("--html", default="", help="zapisz też HTML (do podglądu)")
    for opt in ("tytul", "podtytul", "opis", "nadtytul"):
        ap.add_argument("--" + opt, default="")
    args = ap.parse_args()
    md_path = Path(args.md)
    pdf_path = Path(args.pdf) if (args.pdf != str(DEFAULT_PDF) or md_path.resolve() == DEFAULT_MD.resolve()) else md_path.with_suffix(".pdf")
    g = globals()
    for key, prof in PROFILE.items():
        if md_path.name.startswith(key):
            g.update(prof)
    for opt, var in (("tytul", "DOC_TITLE"), ("podtytul", "DOC_SUBTITLE"), ("opis", "DOC_ABSTRACT"), ("nadtytul", "DOC_KICKER")):
        if getattr(args, opt):
            g[var] = getattr(args, opt)
    g["BUILD_STAMP"] = build_stamp(datetime.now())
    md_text = md_path.read_text(encoding="utf-8")
    tmp_html = Path(args.html) if args.html else pdf_path.with_suffix(".tmp.html")

    # przebieg 1: bez numerów stron
    html, toc = build_html(md_text)
    print_pdf(html, tmp_html, pdf_path)
    pages = heading_pages(pdf_path, toc)
    # przebieg 2: z numerami stron w spisie (spis ma tę samą długość, więc numery się nie przesuwają)
    html, toc = build_html(md_text, toc_pages=pages)
    print_pdf(html, tmp_html, pdf_path)
    pages2 = heading_pages(pdf_path, toc)
    if pages2 != pages:
        # rzadkie: zmiana szerokości numerów przesunęła łamanie — trzeci przebieg
        html, toc = build_html(md_text, toc_pages=pages2)
        print_pdf(html, tmp_html, pdf_path)
        pages = heading_pages(pdf_path, toc)
    else:
        pages = pages2
    n = overlay(pdf_path, toc, pages)
    if not args.html:
        tmp_html.unlink(missing_ok=True)
    missing = [t for l, t, h in toc if h not in pages]
    print(f"OK: {pdf_path.name}, stron: {n}")
    if missing:
        print("UWAGA: nie znaleziono strony dla nagłówków:", missing)


if __name__ == "__main__":
    main()
