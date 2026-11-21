"""T9 - dane osobowe: szukanie nazw folderow zlecen (i nazw plikow projektow) w repo, logach, wynikach i zapisie ruchu.

ZASADA: lista nazw istnieje tylko w pamieci tego procesu. Skrypt NIGDY nie wypisuje nazwy, czlonu nazwy ani fragmentu
pliku z trafieniem - tylko liczby trafien i ``sha16`` (pierwsze 16 znakow SHA-256 nazwy w UTF-8, jak w programie).
W wypisywanej sciezce kazdy czlon sciezki (katalog / plik), ktory zawiera szukana nazwe albo czlon nazwy, jest
zastapiony przez ``<sha16:...>`` (skrot tego czlonu sciezki); reszta sciezki zostaje. Znaki spoza ASCII w sciezce sa
wypisywane jako ``\\uXXXX``; wyjscie i pliki ``--wynik`` / ``--json`` sa ASCII z koncami linii LF.

Skad nazwy (mozna laczyc):
  --nazwy-z KATALOG   nazwy podfolderow KATALOGU (folder "Cyrkon" / "Prywatne" / pula testowa) i nazwy plikow STL w nich;
  --baza PLIK         tabele ``zlecenia.folder`` i ``projekty.plik`` bazy programu (otwierana tylko do odczytu).

Gdzie szukac (mozna laczyc):
  --repo KATALOG      pliki sledzone przez git (tresc i sciezki) oraz historia ``--od..HEAD``: opis, autor i tresc zmian
                      kazdego commita (``git log -p -U0 --cc``; ``--od poczatek`` = cala historia);
  --cel SCIEZKA       plik albo katalog (rekurencyjnie): logi, pliki wynikow, zapis ruchu do ramki;
  --dozwolone WZOR    miejsce, w ktorym nazwy WOLNO trzymac (np. stanowisko.sqlite, log_excel.csv) - pliki sa
                      przeszukiwane, trafienia liczone osobno i nie psuja wyniku;
  --wyklucz WZOR      pliki NIE sa czytane (np. duze kopie zrodel) - liczone jako "wykluczone".
WZOR = podciag sciezki bez rozrozniania wielkosci liter, ``\\`` i ``/`` rownowazne; ``*`` i ``?`` zastepuja znaki w obrebie
jednego czlonu sciezki (np. ``t4_*.json``). Uwaga: ``stanowisko.`` objeloby takze ``stanowisko.log`` - podawaj
``stanowisko.sqlite`` i ``stanowisko.kopia_``.

Wynik: --wynik PLIK (to samo, co na ekranie; ASCII, LF - zamiast przekierowania ``>``), --json PLIK (liczby i sha16).

Jak szuka. Szukane sa: cala nazwa (kryterium T9) oraz czlony nazwy (slowa z litera, co najmniej ``--min-czlon`` znakow) -
trafienia czlonow sa liczone osobno "do wyjasnienia" (czlon moze byc zwyklym slowem) i tylko w plikach bez trafienia calej
nazwy. Porownanie znak po znaku, bez rozrozniania wielkosci liter (takze liter spoza ASCII) i znakow diakrytycznych
(rozklad NFKD + mapa reczna, np. l z kreska = l; litery z cp1250), w postaciach: UTF-8, cp1250, UTF-16 LE, ``\\uXXXX``
(JSON ensure_ascii, cyfry szesnastkowe male i wielkie); spacja nazwy pasuje takze do ``_`` i ``%20``. Trafienia sa liczone
od kazdego miejsca poczatku (nazwa zawarta w innej nazwie liczy sie osobno). Nazwy o tej samej postaci po uproszczeniu
maja wspolny ``sha16`` (pierwszej z nich w kolejnosci). UTF-16 BE i pliki spakowane (zip, npz, pdf, png...) nie sa
przeszukiwane - spakowane liczone jako "nieprzeszukane" (sama sciezka jest sprawdzana); zmiany plikow binarnych w
historii git maja nieprzeszukana tresc (liczba w wyniku).
Czlony krotkie: czlon 1-2 znakowy i czlon bez litery (sam numer) nie jest ani szukany, ani maskowany; czlon z litera o
dlugosci od ``--min-czlon-maski`` (3) do ``--min-czlon`` - 1 jest tylko maskowany w sciezkach (nie liczony); cala nazwa
krotsza niz ``--min-nazwa`` nie jest szukana (liczba w pierwszym wierszu).

Samotest na starcie: kazda nazwa (i kazdy czlon) musi zostac znaleziona we wlasnych bajtach UTF-8, cp1250 (gdy da sie
zakodowac), UTF-16 LE, w ``json.dumps`` (cyfry male i wielkie), w postaci .upper() / .lower() i w transliteracji ASCII.
Inaczej wynik = "NIE ZMIERZONO", kod 2.

Kod wyjscia: 0 = 0 trafien calych nazw poza miejscami dozwolonymi (werdykt "ZAL (0 trafien)" albo "ZAL - czlony do
wyjasnienia: N"), 1 = sa trafienia (FAIL), 2 = NIE ZMIERZONO (blad wywolania, brak nazw, nieudany samotest, blad git).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import subprocess
import sys
import unicodedata
from pathlib import Path

SPAKOWANE = {".zip", ".npz", ".7z", ".whl", ".gz", ".xlsx", ".xlsm", ".docx", ".pdf", ".png", ".jpg"}
MAKS_MB = 300
ZNACZNIK_COMMITA = b"\x00T9COMMIT "
# litery, ktorych rozklad NFKD nie sprowadza do litery podstawowej
MAPA_RECZNA = {"\u0142": "l", "\u0141": "L", "\u0111": "d", "\u0110": "D", "\u00f8": "o", "\u00d8": "O"}
# wzorzec kontrolny samotestu (zdanie ze wszystkimi polskimi literami, nie nazwa) i jego wymagana transliteracja
KONTROLNY = "Za\u017c\u00f3\u0142\u0107 g\u0119\u015bl\u0105 ja\u017a\u0144 \u0141\u00d3D\u0179"
KONTROLNY_ASCII = "Zazolc gesla jazn LODZ"


def sha16(tekst: str) -> str:
    return hashlib.sha256(tekst.encode("utf-8", "surrogatepass")).hexdigest()[:16]


def nazwy_z_katalogu(katalog: Path) -> set[str]:
    nazwy = set()
    for pozycja in katalog.iterdir():
        if pozycja.is_dir():
            nazwy.add(pozycja.name)
            for plik in pozycja.rglob("*"):
                if plik.is_file() and plik.suffix.lower() == ".stl":
                    nazwy.add(plik.stem)
    return nazwy


def nazwy_z_bazy(plik: Path) -> set[str]:
    nazwy = set()
    baza = sqlite3.connect(f"file:{plik.as_posix()}?mode=ro", uri=True)
    try:
        for zapytanie in ("SELECT folder FROM zlecenia", "SELECT plik FROM projekty"):
            try:
                for (wartosc,) in baza.execute(zapytanie):
                    if wartosc:
                        nazwy.add(Path(str(wartosc)).stem if zapytanie.endswith("projekty") else str(wartosc))
            except sqlite3.Error:
                pass
    finally:
        baza.close()
    return nazwy


def czlony(nazwa: str, min_znakow: int) -> set[str]:
    return {c for c in re.split(r"[\s_\-.,;()\[\]]+", nazwa) if len(c) >= min_znakow and re.search(r"[^\W\d_]", c)}


def transliteracja(tekst: str) -> str:
    """Litery ze znakami diakrytycznymi -> litery podstawowe (mapa reczna + rozklad NFKD bez znakow laczacych)."""
    wynik = []
    for znak in tekst:
        if znak in MAPA_RECZNA:
            wynik.append(MAPA_RECZNA[znak])
        elif znak.isascii():
            wynik.append(znak)
        else:
            rozklad = "".join(MAPA_RECZNA.get(z, z) for z in unicodedata.normalize("NFKD", znak) if not unicodedata.combining(z))
            wynik.append(rozklad or znak)
    return "".join(wynik)


def klucz_znaku(znak: str) -> str:
    """Postac uproszczona znaku: bez wielkosci liter i bez znakow diakrytycznych."""
    return transliteracja(transliteracja(znak).casefold())


def _klasy_liter() -> dict[str, set[str]]:
    """Klucz (litera podstawowa) -> litery o tym kluczu: ASCII oraz wszystkie litery strony kodowej cp1250."""
    klasy: dict[str, set[str]] = {}
    znaki = [chr(k) for k in range(ord("a"), ord("z") + 1)] + [chr(k) for k in range(ord("A"), ord("Z") + 1)]
    for bajt in range(0x80, 0x100):
        try:
            znak = bytes([bajt]).decode("cp1250")
        except UnicodeDecodeError:
            continue
        if znak.isalpha():
            znaki.append(znak)
    for znak in znaki:
        klucz = klucz_znaku(znak)
        if len(klucz) == 1:
            klasy.setdefault(klucz, set()).add(znak)
    return klasy


KLASY = _klasy_liter()


def alternatywy(znak: str) -> frozenset[str]:
    """Napisy, ktore w danych uznajemy za ten sam znak nazwy (wielkosc liter, znaki diakrytyczne, odstep)."""
    klucz = klucz_znaku(znak)
    zbior = {znak, znak.lower(), znak.upper(), znak.casefold(), klucz, klucz.upper(), transliteracja(znak),
             transliteracja(znak.upper()), transliteracja(znak.lower())}
    if len(klucz) == 1:
        zbior |= KLASY.get(klucz, set())
    if znak == " ":
        zbior |= {"_", "%20"}
    return frozenset(z for z in zbior if z)


def _zbior_bajtow(bajty: set[int]) -> bytes:
    return b"[" + b"".join(re.escape(bytes([b])) for b in sorted(bajty)) + b"]"


def _ucieczka_json(napis: str) -> bytes:
    """Wzorzec postaci JSON ensure_ascii: znaki ASCII doslownie, pozostale jako \\uXXXX (cyfry male albo wielkie)."""
    czesci = []
    for znak in napis:
        if znak.isascii():
            czesci.append(re.escape(znak.encode("ascii")))
            continue
        jednostki = znak.encode("utf-16-be", "surrogatepass")
        for i in range(0, len(jednostki), 2):
            czesci.append(b"\\\\u")
            for cyfra in f"{jednostki[i]:02x}{jednostki[i + 1]:02x}":
                czesci.append(cyfra.encode("ascii") if cyfra.isdigit() else f"[{cyfra}{cyfra.upper()}]".encode("ascii"))
    return b"".join(czesci)


_PAMIEC_FRAGMENTOW: dict[frozenset[str], tuple[bytes, frozenset[int]]] = {}


def fragment(napisy: frozenset[str]) -> tuple[bytes, frozenset[int]]:
    """Wzorzec bajtowy jednego znaku nazwy we wszystkich postaciach + zbior mozliwych pierwszych bajtow."""
    if napisy in _PAMIEC_FRAGMENTOW:
        return _PAMIEC_FRAGMENTOW[napisy]
    pojedyncze: set[int] = set()
    utf16: dict[int, set[int]] = {}
    utf8: dict[int, set[int]] = {}
    doslowne: set[bytes] = set()
    json_ascii: set[bytes] = set()
    for napis in napisy:
        b8 = napis.encode("utf-8", "surrogatepass")
        if len(b8) == 1:
            pojedyncze.add(b8[0])
        elif len(napis) == 1 and len(b8) == 2:
            utf8.setdefault(b8[0], set()).add(b8[1])
        else:
            doslowne.add(b8)
        try:
            b1250 = napis.encode("cp1250")
        except UnicodeEncodeError:
            b1250 = b8
        if b1250 != b8:
            if len(b1250) == 1:
                pojedyncze.add(b1250[0])
            else:
                doslowne.add(b1250)
        b16 = napis.encode("utf-16-le", "surrogatepass")
        if len(b16) == 2:
            utf16.setdefault(b16[1], set()).add(b16[0])
        else:
            doslowne.add(b16)
        if not napis.isascii():
            json_ascii.add(_ucieczka_json(napis))
    czesci: list[bytes] = []
    pierwsze: set[int] = set(pojedyncze)
    for bajty in sorted(doslowne, key=lambda b: (-len(b), b)):
        czesci.append(re.escape(bajty))
        pierwsze.add(bajty[0])
    z_ukosnikiem = sorted(w[3:] for w in json_ascii if w.startswith(b"\\\\u"))
    if z_ukosnikiem:
        czesci.append(b"\\\\u(?:" + b"|".join(z_ukosnikiem) + b")")
        pierwsze.add(0x5C)
    for wzor in sorted(w for w in json_ascii if not w.startswith(b"\\\\u")):
        czesci.append(wzor)
        pierwsze.add(wzor[1] if wzor[:1] == b"\\" else wzor[0])
    for starszy, mlodsze in sorted(utf16.items()):
        czesci.append(_zbior_bajtow(mlodsze) + re.escape(bytes([starszy])))
        pierwsze |= mlodsze
    for pierwszy, dalsze in sorted(utf8.items()):
        czesci.append(re.escape(bytes([pierwszy])) + _zbior_bajtow(dalsze))
        pierwsze.add(pierwszy)
    if pojedyncze:
        czesci.append(_zbior_bajtow(pojedyncze))
    wynik = (b"(?:" + b"|".join(czesci) + b")", frozenset(pierwsze))
    _PAMIEC_FRAGMENTOW[napisy] = wynik
    return wynik


class Szukacz:
    """Jeden wzorzec bajtowy (drzewo wspolnych poczatkow) dla zbioru tekstow; trafienie -> lista tekstow."""

    def __init__(self, teksty: set[str]) -> None:
        self.koncowki: list[list[str]] = [[]]  # numer grupy wzorca -> teksty (grupa 0 nieuzywana)
        korzen: dict = {"dzieci": {}, "teksty": []}
        for tekst in sorted(teksty):
            wezel = korzen
            for znak in tekst:
                wezel = wezel["dzieci"].setdefault(fragment(alternatywy(znak)), {"dzieci": {}, "teksty": []})
            wezel["teksty"].append(tekst)
        self.wz: re.Pattern[bytes] | None = None
        if not korzen["dzieci"]:
            return
        pierwsze: set[int] = set()
        for _wzor, bajty in korzen["dzieci"]:
            pierwsze |= bajty
        drzewo = self._galezie(korzen)
        # pierwszy bajt jako zbior (szybkie pomijanie), reszta sprawdzana od tego samego miejsca; trafienie ma dlugosc 1
        self.wz = re.compile(_zbior_bajtow(pierwsze) + b"(?s:(?<=(?=" + drzewo + b").))")

    def _galezie(self, wezel: dict) -> bytes:
        czesci = []
        for (wzor, _bajty), dziecko in sorted(wezel["dzieci"].items(), key=lambda p: p[0][0]):
            czesc = wzor
            if dziecko["teksty"]:
                self.koncowki.append(dziecko["teksty"])
                czesc += b"()"
            if dziecko["dzieci"]:
                czesc += self._galezie(dziecko) + (b"?" if dziecko["teksty"] else b"")
            czesci.append(czesc)
        return b"(?:" + b"|".join(czesci) + b")"

    def trafienia(self, dane: bytes) -> dict[int, int]:
        """Numer koncowki -> liczba miejsc w danych."""
        wynik: dict[int, int] = {}
        if self.wz is not None:
            for dopasowanie in self.wz.finditer(dane):
                numer = dopasowanie.lastindex or 0
                wynik[numer] = wynik.get(numer, 0) + 1
        return wynik

    def szukaj(self, dane: bytes) -> dict[str, int]:
        """Tekst (pierwszy z koncowki) -> liczba trafien."""
        return {self.koncowki[numer][0]: ile for numer, ile in self.trafienia(dane).items()}

    def zawiera(self, dane: bytes) -> bool:
        return self.wz is not None and self.wz.search(dane) is not None


def postacie_samotestu(tekst: str) -> dict[str, bytes]:
    """Postacie, w ktorych tekst MUSI zostac znaleziony."""
    json_male = json.dumps(tekst, ensure_ascii=True).encode("ascii")
    postacie = {
        "utf8": tekst.encode("utf-8", "surrogatepass"),
        "utf16le": tekst.encode("utf-16-le", "surrogatepass"),
        "json": json_male,
        "json_wielkie_cyfry": re.sub(rb"\\u[0-9a-f]{4}", lambda d: b"\\u" + d.group(0)[2:].upper(), json_male),
        "wielkie": tekst.upper().encode("utf-8", "surrogatepass"),
        "male": tekst.lower().encode("utf-8", "surrogatepass"),
    }
    try:
        postacie["cp1250"] = tekst.encode("cp1250")
    except UnicodeEncodeError:
        pass
    try:
        postacie["ascii"] = transliteracja(tekst).encode("ascii")
    except UnicodeEncodeError:
        pass
    return postacie


def samotest(teksty: set[str], szukacz: Szukacz) -> tuple[int, list[tuple[str, str]]]:
    """Zwraca (liczba sprawdzonych postaci, lista nieznalezionych: (sha16 tekstu, postac))."""
    sprawdzone = 0
    braki: list[tuple[str, str]] = []
    for tekst in sorted(teksty):
        for postac, bajty in postacie_samotestu(tekst).items():
            sprawdzone += 1
            znalezione = szukacz.trafienia(b"\n" + bajty + b"\n")
            if not any(tekst in szukacz.koncowki[numer] for numer in znalezione):
                braki.append((sha16(tekst), postac))
    return sprawdzone, braki


def wzor_sciezki(wzor: str) -> re.Pattern[str]:
    """--dozwolone / --wyklucz: podciag sciezki; * i ? w obrebie jednego czlonu sciezki."""
    czesci = []
    for znak in wzor.lower().replace("\\", "/"):
        czesci.append("[^/]*" if znak == "*" else "[^/]" if znak == "?" else re.escape(znak))
    return re.compile("".join(czesci))


def pasuje(wzory: list[re.Pattern[str]], opis: str) -> bool:
    sciezka = opis.lower().replace("\\", "/")
    return any(wzor.search(sciezka) for wzor in wzory)


def ascii_bezpieczny(tekst: str) -> str:
    return tekst.encode("ascii", "backslashreplace").decode("ascii")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--nazwy-z", type=Path, action="append", default=[], metavar="KATALOG", help="katalog nadrzedny folderow zlecen")
    parser.add_argument("--baza", type=Path, action="append", default=[], metavar="PLIK", help="baza programu (zlecenia.folder, projekty.plik)")
    parser.add_argument("--repo", type=Path, action="append", default=[], metavar="KATALOG", help="repo git: pliki sledzone + historia --od..HEAD")
    parser.add_argument("--od", default="2537f6f", help="historia (opisy, autorzy, tresc zmian) od tego commita; domyslnie poczatek etapu 3; 'poczatek' = cala")
    parser.add_argument("--cel", type=Path, action="append", default=[], metavar="SCIEZKA", help="plik albo katalog (rekurencyjnie)")
    parser.add_argument("--dozwolone", action="append", default=[], metavar="WZOR", help="miejsce, gdzie nazwy wolno trzymac (liczone osobno)")
    parser.add_argument("--wyklucz", action="append", default=[], metavar="WZOR", help="pliki nieczytane (liczone jako wykluczone)")
    parser.add_argument("--min-nazwa", type=int, default=4, help="najkrotsza szukana cala nazwa (krotsze sa liczone jako pominiete)")
    parser.add_argument("--min-czlon", type=int, default=5, help="najkrotszy szukany czlon nazwy; 0 = bez czlonow")
    parser.add_argument("--min-czlon-maski", type=int, default=3, help="najkrotszy czlon nazwy (z litera) maskowany w wypisywanych sciezkach")
    parser.add_argument("--json", type=Path, default=None, help="zapisz wynik (liczby i sha16, bez nazw) do pliku JSON")
    parser.add_argument("--wynik", type=Path, default=None, help="zapisz wiersze wyniku do pliku (ASCII, LF) - zamiast przekierowania >")
    args = parser.parse_args(argv)

    wiersze: list[str] = []

    def pisz(tekst: str) -> None:
        wiersz = ascii_bezpieczny(tekst)
        wiersze.append(wiersz)
        print(wiersz, flush=True)

    def koniec(kod: int) -> int:
        if args.wynik:
            args.wynik.write_bytes(("\n".join(wiersze) + "\n").encode("ascii"))
        return kod

    nazwy: set[str] = set()
    try:
        for katalog in args.nazwy_z:
            nazwy |= nazwy_z_katalogu(katalog)
        for plik in args.baza:
            nazwy |= nazwy_z_bazy(plik)
    except (OSError, sqlite3.Error) as blad:
        pisz(f"BLAD: nie da sie odczytac zrodla nazw ({type(blad).__name__})")
        pisz("WYNIK T9 (cale nazwy): NIE ZMIERZONO")
        return koniec(2)
    wszystkie = set(nazwy)
    krotkie = {n for n in nazwy if len(n) < args.min_nazwa}
    nazwy -= krotkie
    if not nazwy:
        pisz("BLAD: brak nazw do szukania (podaj --nazwy-z albo --baza)")
        pisz("WYNIK T9 (cale nazwy): NIE ZMIERZONO")
        return koniec(2)
    slowa: set[str] = set()
    if args.min_czlon:
        for nazwa in nazwy:
            slowa |= czlony(nazwa, args.min_czlon)
        slowa -= nazwy
    do_maski: set[str] = set(nazwy)
    for nazwa in wszystkie:
        do_maski |= czlony(nazwa, max(1, args.min_czlon_maski))
    sys.setrecursionlimit(max(sys.getrecursionlimit(), 20000))
    szukacz_nazw = Szukacz(nazwy)
    szukacz_slow = Szukacz(slowa)
    szukacz_maski = Szukacz(do_maski)

    sprawdzone_n, braki_n = samotest(nazwy, szukacz_nazw)
    sprawdzone_s, braki_s = samotest(slowa, szukacz_slow)
    sprawdzone_m, braki_m = samotest(do_maski, szukacz_maski)
    sprawdzone_k, braki_k = samotest({KONTROLNY}, Szukacz({KONTROLNY}))
    sprawdzone, braki = sprawdzone_n + sprawdzone_s + sprawdzone_m + sprawdzone_k + 1, braki_n + braki_s + braki_m + braki_k
    if transliteracja(KONTROLNY) != KONTROLNY_ASCII or not Szukacz({KONTROLNY}).zawiera(KONTROLNY_ASCII.swapcase().encode("ascii")):
        braki.append(("wzorzec-kontrolny", "ascii"))
    bez_ascii = sum(1 for tekst in nazwy if not transliteracja(tekst).isascii())
    pisz(f"Samotest: nazw {len(nazwy)}, czlonow {len(slowa)}, tekstow maski {len(do_maski)}, wzorzec kontrolny 1; postaci sprawdzonych {sprawdzone}, "
         f"nieznalezionych {len(braki)}; nazw bez postaci ASCII (transliteracja niemozliwa, postac niesprawdzana): {bez_ascii}")
    if braki:
        for skrot, postac in braki[:20]:
            pisz(f"  nieznaleziona postac {postac}: sha16 {skrot}")
        pisz(f"WYNIK T9 (cale nazwy): NIE ZMIERZONO (samotest: {len(braki)} z {sprawdzone} postaci nieznalezionych)")
        return koniec(2)

    def maska(opis: str) -> str:
        """Sciezka do wypisania: czlony sciezki z nazwa albo czlonem nazwy zastapione skrotem."""
        if opis.startswith("repo:<historia "):
            return opis  # opis wlasny skryptu: zakres i skrot commita
        przedrostek = "repo:" if opis.startswith("repo:") else ""
        czesci = re.split(r"([\\/])", opis[len(przedrostek):])
        for i in range(0, len(czesci), 2):
            if czesci[i] and szukacz_maski.zawiera(czesci[i].encode("utf-8", "surrogatepass")):
                czesci[i] = f"<sha16:{sha16(czesci[i])}>"
        return przedrostek + "".join(czesci)

    binarne_w_historii = 0
    commitow = 0
    pliki: list[tuple[str, Path | None, bytes | None]] = []  # (opis, plik, dane gotowe)
    try:
        for repo in args.repo:
            lista = subprocess.run(["git", "-C", str(repo), "ls-files", "-z"], capture_output=True, check=True).stdout.split(b"\0")
            for surowa in lista:
                if surowa:
                    wzgledna = surowa.decode("utf-8", "replace")
                    pliki.append((f"repo:{wzgledna}", repo / wzgledna, None))
            zakres = "HEAD" if args.od.lower() in ("", "poczatek") else f"{args.od}..HEAD"
            historia = subprocess.run(
                ["git", "-C", str(repo), "-c", "core.quotepath=false", "log", "-p", "-U0", "--cc", "--no-color", "--no-ext-diff",
                 "--no-textconv", "--format=%x00T9COMMIT %H%n%B%n%an", zakres], capture_output=True, check=True).stdout
            for kawalek in historia.split(ZNACZNIK_COMMITA)[1:]:
                commitow += 1
                binarne_w_historii += kawalek.count(b"\nBinary files ")
                pliki.append((f"repo:<historia {zakres}: commit {kawalek[:12].decode('ascii', 'replace')}>", None, kawalek[40:]))
    except (OSError, subprocess.CalledProcessError) as blad:
        pisz(f"BLAD: git nie odczytal repo ({type(blad).__name__})")
        pisz("WYNIK T9 (cale nazwy): NIE ZMIERZONO")
        return koniec(2)
    for cel in args.cel:
        if cel.is_dir():
            for plik in sorted(cel.rglob("*")):
                if plik.is_file():
                    pliki.append((str(plik), plik, None))
        elif cel.is_file():
            pliki.append((str(cel), cel, None))
        else:
            pisz(f"BLAD: nie ma celu {maska(str(cel))}")
            pisz("WYNIK T9 (cale nazwy): NIE ZMIERZONO")
            return koniec(2)

    dozwolone = [wzor_sciezki(w) for w in args.dozwolone]
    wykluczone = [wzor_sciezki(w) for w in args.wyklucz]
    wynik = {"nazw": len(nazwy), "nazw_pominietych_krotkich": len(krotkie), "czlonow": len(slowa), "samotest_postaci": sprawdzone,
             "plikow": 0, "commitow_historii": commitow, "binarne_w_historii": binarne_w_historii, "nieprzeszukane": [],
             "wykluczone": [], "trafienia": [], "trafienia_dozwolone": [], "czlony_do_wyjasnienia": []}

    def skroty(trafione: dict[str, int]) -> dict[str, int]:
        return {sha16(n): k for n, k in sorted(trafione.items(), key=lambda p: sha16(p[0]))}

    for opis, plik, dane in pliki:
        if pasuje(wykluczone, opis):
            wynik["wykluczone"].append(maska(opis))
            continue
        dozwolony = pasuje(dozwolone, opis)
        tylko_sciezka = False
        if dane is None:
            assert plik is not None
            try:
                if plik.suffix.lower() in SPAKOWANE or not plik.exists() or plik.stat().st_size > MAKS_MB * 1024 * 1024:
                    tylko_sciezka = True
                else:
                    dane = plik.read_bytes()
            except OSError:
                tylko_sciezka = True
        if tylko_sciezka or dane is None:
            wynik["nieprzeszukane"].append(maska(opis))
            calosc = opis.encode("utf-8", "surrogatepass")
        else:
            wynik["plikow"] += 1
            calosc = dane + b"\n" + opis.encode("utf-8", "surrogatepass")
        trafione = szukacz_nazw.szukaj(calosc)
        if trafione:
            wpis = {"gdzie": maska(opis), "nazwy": skroty(trafione)}
            if tylko_sciezka:
                wpis["w_sciezce"] = True
            wynik["trafienia_dozwolone" if dozwolony else "trafienia"].append(wpis)
        elif not dozwolony:
            slowne = szukacz_slow.szukaj(calosc)
            if slowne:
                wynik["czlony_do_wyjasnienia"].append({"gdzie": maska(opis), "czlony": skroty(slowne)})

    def suma(lista: list[dict], pole: str) -> int:
        return sum(sum(wpis[pole].values()) for wpis in lista)

    def wypisz(lista: list[dict], pole: str) -> None:
        for wpis in lista[:40]:
            pisz(f"  {wpis['gdzie']}: " + ", ".join(f"{skrot} x{ile}" for skrot, ile in wpis[pole].items()))
        if len(lista) > 40:
            pisz(f"  ... i jeszcze {len(lista) - 40} plikow (pelna lista: --json)")

    pisz(f"T9 dane osobowe: szukanych nazw {wynik['nazw']} (pominietych krotszych niz {args.min_nazwa} znaki: {wynik['nazw_pominietych_krotkich']}), "
         f"czlonow {wynik['czlonow']}; przeszukanych plikow {wynik['plikow']}, nieprzeszukanych (spakowane / za duze) {len(wynik['nieprzeszukane'])}, "
         f"wykluczonych (--wyklucz) {len(wynik['wykluczone'])}")
    if args.repo:
        pisz(f"Historia git: commitow {commitow} (opis, autor, tresc zmian); zmian plikow binarnych z nieprzeszukana trescia: {binarne_w_historii}")
    pisz(f"TRAFIENIA calych nazw poza miejscami dozwolonymi: {suma(wynik['trafienia'], 'nazwy')} w {len(wynik['trafienia'])} plikach")
    wypisz(wynik["trafienia"], "nazwy")
    pisz(f"Trafienia w miejscach dozwolonych: {suma(wynik['trafienia_dozwolone'], 'nazwy')} w {len(wynik['trafienia_dozwolone'])} plikach")
    ile_czlonow = suma(wynik["czlony_do_wyjasnienia"], "czlony")
    pisz(f"Czlony nazw do wyjasnienia (bez calej nazwy): {ile_czlonow} w {len(wynik['czlony_do_wyjasnienia'])} plikach")
    wypisz(wynik["czlony_do_wyjasnienia"], "czlony")
    zaliczony = not wynik["trafienia"]
    if not zaliczony:
        werdykt = "FAIL"
    elif ile_czlonow:
        werdykt = f"ZAL - czlony do wyjasnienia: {ile_czlonow}"
    else:
        werdykt = "ZAL (0 trafien)"
    wynik["werdykt"] = werdykt
    if args.json:
        args.json.write_bytes((json.dumps(wynik, ensure_ascii=True, indent=1) + "\n").encode("ascii"))
    pisz(f"WYNIK T9 (cale nazwy): {werdykt}")
    return koniec(0 if zaliczony else 1)


if __name__ == "__main__":
    sys.exit(main())
