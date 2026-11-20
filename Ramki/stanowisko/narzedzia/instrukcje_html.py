"""instrukcje_html - strony do druku (jedna strona A4) z instrukcji dla technika i sprawdzenie cytatow (paczka E3-A11d).

Instrukcje sa pisane w Markdown (``instrukcje/*.md``, zestaw proby T14 w ``Ramki/etap3/t14``), po polsku bez znakow
diakrytycznych. Umowa zapisu:

* tekst w cudzyslowie prostym ("...") to DOSLOWNY napis programu: przycisk, tytul albo tresc komunikatu, podpis gniazda.
  Kazdy taki cytat musi istniec w kodzie programu (``stanowisko/*.py``, ``stanowisko/ui/*.py``) - pilnuje tego
  ``testy/test_instrukcje.py``. Trzy kropki na poczatku albo na koncu cytatu ("... juz dziala na tym komputerze ...")
  znacza, ze to fragment dluzszego napisu. Liczba albo numer w miejscu pola wzoru jest dozwolona ("Do dofrezowania: 1"
  pasuje do wzoru "Do dofrezowania: {n}").
* tekst w odwrotnych apostrofach (`...`) to nazwa pliku albo polecenia - nie jest sprawdzany z kodem.
* innych cudzyslowow w instrukcjach nie ma.

Strona do druku (``*.html``) jest plikiem ASCII i nie potrzebuje innych plikow: obrazki sa wpisane w strone, a cytaty sa
wypisane DOKLADNIE jak na ekranie (z polskimi znakami, zapisanymi jako encje) i pogrubione.

Uzycie (z katalogu stanowisko/):
    py -3.12 narzedzia/instrukcje_html.py                 zloz wszystkie strony do druku
    py -3.12 narzedzia/instrukcje_html.py --sprawdz       kod 1, gdy cytat nie istnieje w programie albo strona jest nieaktualna
    py -3.12 narzedzia/instrukcje_html.py --cytaty        tabela: dokument, cytat, plik programu (zrodlo)
    py -3.12 narzedzia/instrukcje_html.py --pdf KATALOG [--chrome SCIEZKA]   druk do PDF przegladarka i liczba stron
"""
from __future__ import annotations

import argparse
import ast
import base64
import html
import re
import subprocess
import sys
from pathlib import Path

STANOWISKO = Path(__file__).resolve().parent.parent
RAMKI = STANOWISKO.parent
INSTRUKCJE = STANOWISKO / "instrukcje"
T14 = RAMKI / "etap3" / "t14"
KOD_PROGRAMU = STANOWISKO / "stanowisko"
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")

# dokument -> (plik md, uklad strony, szerokosci obrazkow wg nazwy pliku)
DOKUMENTY = {
    "wieczor": (INSTRUKCJE / "wieczor.md", "pion",
                {"wieczor_ekran.png": "100%", "wieczor_praca.png": "70%", "wieczor_popraw.png": "100%", "wieczor_ponowny.png": "100%",
                 "wieczor_lista.png": "70%"}),
    "poranek": (INSTRUKCJE / "poranek.md", "pion",
                {"rano_ekran.png": "100%", "rano_kandydaci.png": "52%", "rano_braki.png": "56%", "rano_excel.png": "92%"}),
    "co_robic_gdy_nie_dziala": (INSTRUKCJE / "co_robic_gdy_nie_dziala.md", "poziom", {}),
    "t14_jedna_strona": (T14 / "jedna_strona.md", "poziom2",
                         {"wieczor_ekran.png": "100%", "rano_ekran.png": "100%", "wieczor_praca.png": "100%", "rano_kandydaci.png": "100%"}),
    "t14_arkusz_obserwacji": (T14 / "arkusz_obserwacji.md", "arkusz", {}),
}

# znak z ekranu -> zapis w instrukcji (ASCII); klucze zapisane kodami, bo ten plik jest w ASCII
ZNAKI = {"\u0105": "a", "\u0107": "c", "\u0119": "e", "\u0142": "l", "\u0144": "n", "\u00f3": "o", "\u015b": "s", "\u017a": "z",
         "\u017c": "z", "\u0104": "A", "\u0106": "C", "\u0118": "E", "\u0141": "L", "\u0143": "N", "\u00d3": "O", "\u015a": "S",
         "\u0179": "Z", "\u017b": "Z",
         "\u201e": '"', "\u201d": '"', "\u201c": '"', "\u2019": "'", "\u2014": "-", "\u2013": "-", "\u2026": "...", "\u00b7": "-",
         "\u2192": "->", "\u2581": "_", "\u25c0": "<", "\u00d7": "x", "\u00f8": "o", "\u00a0": " "}
WZOR_CYTATU = re.compile(r'"([^"\n]+)"')
WZOR_KODU = re.compile(r"`[^`\n]*`")
WZOR_OBRAZKA = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)")
POLE = "\x00"  # miejsce pola wzoru ({n}, {kuweta}, wyrazenie f-napisu) w napisie programu


# ----------------------------------------------------------------------------
# napisy programu i cytaty
# ----------------------------------------------------------------------------
def zloz(tekst: str) -> tuple[str, list[int]]:
    """Napis bez polskich znakow i znakow typograficznych (ASCII) z odstepami sprowadzonymi do jednej spacji oraz - dla
    kazdego znaku wyniku - polozenie znaku zrodlowego (do odtworzenia pisowni z ekranu)."""
    wynik, skad = [], []
    for i, znak in enumerate(tekst):
        zamiennik = ZNAKI.get(znak, znak if ord(znak) < 128 else "?")
        for z in zamiennik:
            if z.isspace():
                if wynik and wynik[-1] == " ":
                    continue
                z = " "
            wynik.append(z)
            skad.append(i)
    return "".join(wynik), skad


def ascii_napis(tekst: str) -> str:
    return zloz(tekst)[0].strip()


def _napis_wezla(wezel) -> str | None:
    """Tekst stalej napisowej albo f-napisu (pola jako ``POLE``); None dla innych wezlow."""
    if isinstance(wezel, ast.Constant) and isinstance(wezel.value, str):
        return wezel.value
    if isinstance(wezel, ast.JoinedStr):
        return "".join(c.value if isinstance(c, ast.Constant) and isinstance(c.value, str) else POLE for c in wezel.values)
    return None


def napisy_programu(katalog: Path = KOD_PROGRAMU) -> list[tuple[str, str]]:
    """Wszystkie napisy kodu programu: (napis, plik wzgledem katalogu programu). Bez opisow funkcji, klas i modulow
    (docstring) - cytat ma trafic w napis, ktory program naprawde pokazuje."""
    wynik = []
    pierwsze = ("statusy.py", "ui/napisy.py", "ui/napisy_rano.py")  # tu sa napisy ekranu - one pierwsze jako zrodlo cytatu
    pliki = sorted(katalog.rglob("*.py"), key=lambda p: (p.relative_to(katalog).as_posix() not in pierwsze, p.relative_to(katalog).as_posix()))
    for plik in pliki:
        drzewo = ast.parse(plik.read_text(encoding="utf-8"))
        opisy = set()
        for wezel in ast.walk(drzewo):
            if isinstance(wezel, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and wezel.body:
                pierwszy = wezel.body[0]
                if isinstance(pierwszy, ast.Expr) and isinstance(pierwszy.value, ast.Constant) and isinstance(pierwszy.value.value, str):
                    opisy.add(id(pierwszy.value))
        w_f_napisie = {id(c) for w in ast.walk(drzewo) if isinstance(w, ast.JoinedStr) for c in ast.walk(w) if c is not w}
        for wezel in ast.walk(drzewo):
            if id(wezel) in opisy or id(wezel) in w_f_napisie:
                continue
            napis = _napis_wezla(wezel)
            if napis and napis.strip():
                wynik.append((napis, plik.relative_to(katalog).as_posix()))
    return wynik


def _czesci_wzoru(napis: str) -> list[str]:
    """Napis programu pociety na czesci stale; miedzy nimi pola (``{nazwa}`` wzoru ``str.format`` albo pole f-napisu)."""
    return re.split(r"\x00|\{[a-z_0-9]*(?:![rs])?(?::[^{}]*)?\}", napis)


def _litery(tekst: str) -> int:
    return sum(1 for z in tekst if z.isalpha())


class Indeks:
    """Napisy programu przygotowane do wyszukiwania cytatow."""

    def __init__(self, napisy: list[tuple[str, str]] | None = None):
        self.napisy = napisy if napisy is not None else napisy_programu()
        self._wpisy = []  # (plik, czesci stale jak na ekranie, te same czesci zlozone do ASCII z polozeniami znakow)
        for napis, plik in self.napisy:
            czesci = _czesci_wzoru(napis)
            self._wpisy.append((plik, czesci, [zloz(c) for c in czesci]))

    def znajdz(self, cytat: str) -> tuple[str, str] | None:
        """(napis jak na ekranie, plik programu) dla cytatu z instrukcji albo None, gdy program takiego napisu nie ma.

        1. caly napis programu (bez pol) rowny cytatowi; 2. wzor z polami pasujacy do calego cytatu (w polach dowolny tekst;
        wzor musi miec dosc liter stalych - wzor z samych pol pasowalby do wszystkiego); 3. cytat z trzema kropkami: fragment
        jednej czesci stalej napisu (bez kropek z lewej - od poczatku napisu, bez kropek z prawej - do konca napisu)."""
        cytat = cytat.strip()
        rowne = [(" ".join(czesci[0].split()), plik) for plik, czesci, zlozone in self._wpisy
                 if len(czesci) == 1 and zlozone[0][0].strip() == cytat]
        if rowne:  # ten sam napis bywa tez kluczem bez polskich znakow ("sprawdz") - pierwszenstwo ma pisownia z ekranu
            return next((r for r in rowne if not r[0].isascii()), rowne[0])
        z_lewej = cytat.startswith("...")
        z_prawej = cytat.endswith("...") and len(cytat) > 3
        rdzen = cytat[3 if z_lewej else 0: len(cytat) - 3 if z_prawej else len(cytat)].strip()
        if not rdzen:
            return None
        if not (z_lewej or z_prawej):
            for plik, czesci, zlozone in self._wpisy:
                if len(czesci) == 1:
                    continue
                stale = "".join(t for t, _ in zlozone)
                if _litery(stale) < 4 or 2 * _litery(stale) < _litery(rdzen):
                    continue
                teksty = [t for t, _ in zlozone]
                teksty[0], teksty[-1] = teksty[0].lstrip(), teksty[-1].rstrip()
                m = re.fullmatch("(.+?)".join(re.escape(t) for t in teksty), rdzen)
                if m is not None:
                    wynik = "".join(czesc + (m.group(i + 1) if i < len(czesci) - 1 else "") for i, czesc in enumerate(czesci))
                    return " ".join(wynik.split()), plik
            return None
        if _litery(rdzen) < 5:
            return None
        for plik, czesci, zlozone in self._wpisy:
            for i, (tekst, skad) in enumerate(zlozone):
                start = tekst.find(rdzen)
                while start >= 0:
                    koniec = start + len(rdzen)
                    od_poczatku = i == 0 and not tekst[:start].strip()
                    do_konca = i == len(zlozone) - 1 and not tekst[koniec:].strip()
                    if (z_lewej or od_poczatku) and (z_prawej or do_konca):
                        wycinek = " ".join(czesci[i][skad[start]: skad[koniec - 1] + 1].split())
                        return ("" if od_poczatku else "... ") + wycinek + ("" if do_konca else " ..."), plik
                    start = tekst.find(rdzen, start + 1)
        return None


def tekst_bez_kodu(md: str) -> str:
    """Tresc instrukcji bez nazw plikow i polecen (`...`) oraz bez sciezek obrazkow - tam cudzyslow nie jest cytatem."""
    md = WZOR_OBRAZKA.sub(lambda m: m.group(1), md)
    return WZOR_KODU.sub(" ", md)


def cytaty(md: str) -> list[str]:
    """Cytaty (teksty w cudzyslowie prostym) w kolejnosci wystapienia, bez powtorzen."""
    wynik = []
    for c in WZOR_CYTATU.findall(tekst_bez_kodu(md)):
        if c not in wynik:
            wynik.append(c)
    return wynik


def obrazki(md: str) -> list[str]:
    """Sciezki obrazkow wskazanych w instrukcji (wzgledem pliku instrukcji), bez powtorzen."""
    wynik = []
    for _, sciezka in WZOR_OBRAZKA.findall(md):
        if sciezka not in wynik:
            wynik.append(sciezka)
    return wynik


def brakujace_cytaty(md: str, indeks: Indeks) -> list[str]:
    return [c for c in cytaty(md) if indeks.znajdz(c) is None]


# ----------------------------------------------------------------------------
# Markdown (podzbior uzywany w instrukcjach) -> HTML do druku
# ----------------------------------------------------------------------------
STYL = """
@page { size: A4 %(orientacja)s; margin: %(margines)s; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: "Segoe UI", Arial, Helvetica, sans-serif; font-size: %(pismo)s; line-height: 1.28; color: #111; margin: 0; }
h1 { font-size: 15pt; margin: 0 0 3pt 0; border-bottom: 1.5pt solid #1e4e8c; padding-bottom: 2pt; }
h2 { font-size: 10.5pt; margin: 6pt 0 2pt 0; color: #1e4e8c; break-after: avoid; }
p { margin: 2pt 0 3pt 0; }
ol, ul { margin: 2pt 0 3pt 0; padding-left: 15pt; }
li { margin: 0 0 2.5pt 0; break-inside: avoid; }
img { display: block; max-width: 100%%; height: auto; margin: 2pt 0 3pt 0; border: 0.5pt solid #9aa3ad; border-radius: 3pt; }
b.n { font-weight: 700; white-space: normal; }
code { font-family: Consolas, "Courier New", monospace; font-size: 95%%; background: #eef1f5; padding: 0 2pt; border-radius: 2pt; }
table { border-collapse: collapse; width: 100%%; margin: 2pt 0 4pt 0; }
th, td { border: 0.5pt solid #7d8792; padding: 1.5pt 3pt; vertical-align: top; text-align: left; }
th { background: #e3e8ee; }
tr { break-inside: avoid; }
.kolumny { column-count: 2; column-gap: 6mm; }
.obok { display: flex; gap: 4mm; align-items: flex-start; }
.obok img, .obok table, .obok h2 { margin-top: 0; }
.stopka { font-size: 7pt; color: #555; margin-top: 3pt; }
%(dodatki)s
@media screen { body { max-width: %(szerokosc)s; margin: 8mm auto; } }
"""
UKLADY = {
    "pion": {"orientacja": "portrait", "margines": "8mm 9mm", "pismo": "8.4pt", "szerokosc": "192mm",
             "dodatki": ".obok table { font-size: 7.7pt; }"},
    "poziom": {"orientacja": "landscape", "margines": "7mm 8mm", "pismo": "7.3pt", "szerokosc": "279mm",
               "dodatki": "th, td { padding: 1pt 2.5pt; } h1 { font-size: 13pt; } p { margin: 1pt 0 2pt 0; }"},
    "poziom2": {"orientacja": "landscape", "margines": "8mm 9mm", "pismo": "9.6pt", "szerokosc": "279mm",
                "dodatki": ".kolumny { column-gap: 9mm; } h2 { font-size: 13pt; } li { margin-bottom: 3pt; }"},
    "arkusz": {"orientacja": "portrait", "margines": "10mm 11mm", "pismo": "9pt", "szerokosc": "188mm",
               "dodatki": "td { height: 21pt; } li { margin-bottom: 1pt; }"},
}


def _encje(tekst: str) -> str:
    """Tekst HTML zapisany w ASCII: znaki spoza ASCII jako encje liczbowe."""
    return "".join(z if ord(z) < 128 else f"&#{ord(z)};" for z in html.escape(tekst, quote=False))


def _w_linii(tekst: str, indeks: Indeks | None, zrodla: dict, katalog: Path, szerokosci: dict, wpisane: dict) -> str:
    """Formatowanie w linii: obrazek, `kod`, **pogrubienie**, cytat "..." (pisownia z ekranu), <br>."""
    kawalki = []

    def schowaj(html_: str) -> str:
        kawalki.append(html_)
        return f"\x01{len(kawalki) - 1}\x02"

    def obrazek(m) -> str:
        opis, sciezka = m.group(1), m.group(2)
        nazwa = Path(sciezka).name
        dane = wpisane.get(nazwa)
        plik = katalog / sciezka
        if plik.is_file():
            dane = base64.b64encode(plik.read_bytes()).decode("ascii")
        if dane is None:
            raise FileNotFoundError(f"brak obrazka {sciezka} (uruchom narzedzia/zrzuty_instrukcji.py)")
        styl = f' style="width:{szerokosci[nazwa]}"' if nazwa in szerokosci else ""
        return schowaj(f'<img data-plik="{nazwa}" alt="{_encje(opis)}"{styl} src="data:image/png;base64,{dane}">')

    def cytat(m) -> str:
        tresc = m.group(1)
        trafienie = indeks.znajdz(tresc) if indeks is not None else None
        if trafienie is not None:
            zrodla[tresc] = trafienie[1]
            tresc = trafienie[0]
        elif indeks is not None:
            zrodla[tresc] = None
        tresc = tresc.replace("...", "\u2026")
        return schowaj(f'<b class="n">&#8222;{_encje(tresc)}&#8221;</b>')

    tekst = WZOR_OBRAZKA.sub(obrazek, tekst)
    tekst = WZOR_KODU.sub(lambda m: schowaj(f"<code>{_encje(m.group(0)[1:-1])}</code>"), tekst)
    tekst = WZOR_CYTATU.sub(cytat, tekst)
    tekst = tekst.replace("<br>", "\x03")
    tekst = _encje(tekst)
    tekst = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", tekst)
    tekst = tekst.replace("\x03", "<br>")
    return re.sub(r"\x01(\d+)\x02", lambda m: kawalki[int(m.group(1))], tekst)


def md_na_html(md: str, *, tytul: str, uklad: str, katalog: Path, indeks: Indeks | None = None, szerokosci: dict | None = None,
               wpisane: dict | None = None) -> tuple[str, dict]:
    """Strona HTML (ASCII, obrazki wpisane) z instrukcji w Markdown; zwraca (html, {cytat: plik programu albo None}).

    Obslugiwane: ``# tytul``, ``## naglowek``, akapity, listy ``1.`` i ``-`` (wiersze wciete naleza do punktu), tabele
    ``| a | b |``, obrazki, **pogrubienie**, `kod`, cytaty; wiersze ``<!-- kolumny -->`` / ``<!-- koniec kolumn -->`` otaczaja
    czesc skladana w dwoch kolumnach (``<!-- nowa kolumna -->`` - przejscie do drugiej); ``<!-- obok 62 -->`` /
    ``<!-- dalej -->`` / ``<!-- koniec obok -->`` - dwie czesci obok siebie (lewa 62 % szerokosci); wiersz
    ``<!-- stopka: tekst -->`` daje drobny tekst na dole strony."""
    zrodla: dict = {}
    szerokosci, wpisane = szerokosci or {}, wpisane or {}

    def linia(t: str) -> str:
        return _w_linii(t, indeks, zrodla, katalog, szerokosci, wpisane)

    wyjscie, akapit, lista, tabela = [], [], None, []

    def zamknij_akapit() -> None:
        if akapit:
            wyjscie.append(f"<p>{linia(' '.join(akapit))}</p>")
            akapit.clear()

    def zamknij_liste() -> None:
        nonlocal lista
        if lista is not None:
            znacznik, punkty = lista
            wyjscie.append(f"<{znacznik}>" + "".join(f"<li>{linia(' '.join(p))}</li>" for p in punkty) + f"</{znacznik}>")
            lista = None

    def zamknij_tabele() -> None:
        if tabela:
            wiersze = [[k.strip() for k in w.strip().strip("|").split("|")] for w in tabela]
            cialo = [w for w in wiersze[1:] if not all(re.fullmatch(r":?-+:?", k) for k in w)]
            szer = [k for k in wiersze[1] if re.fullmatch(r":?-+:?", k)] if len(wiersze) > 1 else []
            razem = sum(len(k) for k in szer) or 1
            kolumny = "".join(f'<col style="width:{100 * len(k) / razem:.1f}%">' for k in szer)
            wyjscie.append("<table>" + (f"<colgroup>{kolumny}</colgroup>" if kolumny else "")
                           + "<tr>" + "".join(f"<th>{linia(k)}</th>" for k in wiersze[0]) + "</tr>"
                           + "".join("<tr>" + "".join(f"<td>{linia(k)}</td>" for k in w) + "</tr>" for w in cialo) + "</table>")
            tabela.clear()

    def zamknij() -> None:
        zamknij_akapit()
        zamknij_liste()
        zamknij_tabele()

    for wiersz in md.splitlines():
        goly = wiersz.strip()
        if goly.startswith("<!--") and goly.endswith("-->"):
            zamknij()
            tresc = goly[4:-3].strip()
            if tresc == "kolumny":
                wyjscie.append('<div class="kolumny">')
            elif tresc == "koniec kolumn":
                wyjscie.append("</div>")
            elif tresc == "nowa kolumna":
                wyjscie.append('<div style="break-before: column"></div>')
            elif tresc.startswith("obok"):  # dwie czesci obok siebie; liczba = szerokosc lewej w procentach
                wyjscie.append(f'<div class="obok"><div style="flex: 0 0 {int(tresc.split()[1]) if len(tresc.split()) > 1 else 60}%">')
            elif tresc == "dalej":
                wyjscie.append('</div><div style="flex: 1 1 0">')
            elif tresc == "koniec obok":
                wyjscie.append("</div></div>")
            elif tresc.startswith("stopka:"):
                wyjscie.append(f'<p class="stopka">{linia(tresc[7:].strip())}</p>')
            continue
        if not goly:
            zamknij_akapit()
            zamknij_tabele()
            continue
        if goly.startswith("|"):
            zamknij_akapit()
            zamknij_liste()
            tabela.append(goly)
            continue
        zamknij_tabele()
        m = re.match(r"(#{1,2})\s+(.*)", goly)
        if m and not wiersz.startswith(" "):
            zamknij()
            poziom = len(m.group(1))
            wyjscie.append(f"<h{poziom}>{linia(m.group(2))}</h{poziom}>")
            continue
        m = re.match(r"(\d+\.|-)\s+(.*)", goly)
        if m and not wiersz.startswith("  "):
            zamknij_akapit()
            znacznik = "ul" if m.group(1) == "-" else "ol"
            if lista is None or lista[0] != znacznik:
                zamknij_liste()
                lista = (znacznik, [])
            lista[1].append([m.group(2)])
            continue
        if lista is not None and wiersz.startswith("  "):
            lista[1][-1].append(goly)
            continue
        zamknij_liste()
        akapit.append(goly)
    zamknij()
    styl = STYL % UKLADY[uklad]
    strona = ("<!DOCTYPE html>\n<html lang=\"pl\">\n<head>\n<meta charset=\"utf-8\">\n"
              f"<title>{_encje(tytul)}</title>\n<style>{styl}</style>\n</head>\n<body>\n" + "\n".join(wyjscie) + "\n</body>\n</html>\n")
    strona.encode("ascii")
    return strona, zrodla


def _wpisane_obrazki(plik_html: Path) -> dict:
    """Obrazki wpisane w istniejaca strone (nazwa pliku -> base64) - uzywane, gdy pliku PNG nie ma na dysku (PNG w katalogu
    programu nie sa w repozytorium; strona do druku niesie je w sobie)."""
    if not plik_html.is_file():
        return {}
    tekst = plik_html.read_text(encoding="ascii")
    return dict(re.findall(r'<img data-plik="([^"]+)"[^>]*? src="data:image/png;base64,([A-Za-z0-9+/=]+)"', tekst))


def zloz_dokument(nazwa: str, indeks: Indeks | None = None) -> tuple[Path, str, dict]:
    """(plik html, tresc, zrodla cytatow) dla dokumentu z ``DOKUMENTY``; niczego nie zapisuje."""
    plik_md, uklad, szerokosci = DOKUMENTY[nazwa]
    md = plik_md.read_text(encoding="ascii")
    plik_html = plik_md.with_suffix(".html")
    tytul = next((w[2:].strip() for w in md.splitlines() if w.startswith("# ")), plik_md.stem)
    strona, zrodla = md_na_html(md, tytul=ascii_napis(tytul), uklad=uklad, katalog=plik_md.parent, indeks=indeks or Indeks(),
                                szerokosci=szerokosci, wpisane=_wpisane_obrazki(plik_html))
    return plik_html, strona, zrodla


def liczba_stron_pdf(plik: Path) -> int:
    """Liczba stron PDF (QtPdf; bez niego - liczba obiektow strony w pliku)."""
    try:
        from PySide6.QtPdf import QPdfDocument

        dokument = QPdfDocument(None)
        dokument.load(str(plik))
        n = dokument.pageCount()
        dokument.close()
        if n > 0:
            return n
    except ImportError:
        pass
    return len(re.findall(rb"/Type\s*/Page(?![s\w])", plik.read_bytes()))


def drukuj_pdf(plik_html: Path, katalog: Path, chrome: Path = CHROME) -> tuple[Path, int]:
    """Druk strony do PDF przegladarka bez okna (to samo, co "Drukuj" w przegladarce: A4 wg ``@page``); zwraca (plik, stron)."""
    katalog.mkdir(parents=True, exist_ok=True)
    pdf = katalog / (plik_html.parent.name + "_" + plik_html.stem + ".pdf")
    profil = katalog / "_profil_przegladarki"
    subprocess.run([str(chrome), "--headless=new", "--disable-gpu", "--no-first-run", f"--user-data-dir={profil}",
                    "--no-pdf-header-footer", f"--print-to-pdf={pdf}", plik_html.resolve().as_uri()],
                   check=True, capture_output=True, timeout=180)
    return pdf, liczba_stron_pdf(pdf)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Strony do druku z instrukcji dla technika; sprawdzenie cytatow z programem.")
    parser.add_argument("--sprawdz", action="store_true", help="niczego nie zapisuj; kod 1 przy brakujacym cytacie albo nieaktualnej stronie")
    parser.add_argument("--cytaty", action="store_true", help="wypisz cytaty z plikiem programu, z ktorego pochodza")
    parser.add_argument("--pdf", type=Path, metavar="KATALOG", help="wydrukuj strony do PDF (przegladarka bez okna) i policz strony")
    parser.add_argument("--chrome", type=Path, default=CHROME, help="program przegladarki do --pdf")
    args = parser.parse_args(argv)
    indeks = Indeks()
    bledy = 0
    for nazwa in DOKUMENTY:
        plik_html, strona, zrodla = zloz_dokument(nazwa, indeks)
        brak = [c for c, z in zrodla.items() if z is None]
        for c in brak:
            print(f"BLAD {nazwa}: cytatu nie ma w programie: \"{c}\"", file=sys.stderr)
        bledy += len(brak)
        if args.cytaty:
            for c, z in zrodla.items():
                print(f"{nazwa}\t\"{c}\"\t{z or 'BRAK'}")
            continue
        if args.sprawdz:
            aktualna = plik_html.is_file() and plik_html.read_text(encoding="ascii") == strona
            print(f"{nazwa}: cytatow {len(zrodla)}, brakujacych {len(brak)}, strona {'aktualna' if aktualna else 'NIEAKTUALNA'}")
            bledy += 0 if aktualna else 1
            continue
        plik_html.write_text(strona, encoding="ascii", newline="\n")
        print(f"{plik_html.relative_to(RAMKI).as_posix()}: {len(strona)} B, cytatow {len(zrodla)}, brakujacych {len(brak)}")
        if args.pdf is not None:
            pdf, stron = drukuj_pdf(plik_html, args.pdf, args.chrome)
            print(f"  druk: {pdf.name}, stron {stron}")
    return 1 if bledy else 0


if __name__ == "__main__":
    raise SystemExit(main())
