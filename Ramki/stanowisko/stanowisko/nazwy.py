"""nazwy - nazwa folderu zlecenia -> numer kuwety; normalizacja nazw; zeby i typ pracy z nazwy pliku STL (E3-A4).

Regula kuwety (plan wdrozenia v2, "Dane i integracje"; przeniesione z wczesniejszej linii ``qc/catalog/nazwy.py``, H;
runda 2 recenzji PR #18 - P1): kandydat na numer kuwety to samodzielna liczba do 4 cyfr znaczacych w nazwie folderu, zera
wiodace usuwane (decyzja robocza 1: 3 = 03 = 003 -> "3", "0412" = "00412" -> "412"; stala ``KUWETA_BEZ_ZER``). Liczba moze
byc z prawej sklejona z kodem literowym ("Nazwisko 1784PG" -> "1784"), ale nie z cyframi ("12345" -> nie kuweta) ani
z literami z lewej ("PG1784" -> nie kuweta). Kropka i podkreslnik sa separatorami ("J.3263", "_88_"). Kandydatami NIE sa:
- daty z poprawnymi zakresami (dzien 1-31, miesiac 1-12, rok 19xx / 20xx albo 2 cyfry): 2026-11-16, 2026_11_16, 16.11.2026,
  16-11-26 - "3263_16_11_2026" to kuweta 3263 i data (wczesniej wzor bez zakresow zjadal numer kuwety); wyjatek (runda 3,
  D19): lancuch z lacznikiem albo podkreslnikiem z rokiem sprzed ``ROK_DATY_MIN`` (2020), w ktorym dwie liczby po pierwszej
  to numery zebow FDI, nie jest data, tylko numerem + zebami ("2012_11_21" -> kuweta 2012, most 11-21; "5-11-12" -> 5);
  granica: "12-11-21" (most 12-11-21 albo kuweta 12 + 11-21) i rok od 2020 ("2021-11-21") - bez kuwety (licznik);
- numery zebow FDI dopisane po numerze kuwety lacznikiem albo podkreslnikiem ("3263-24-25", "3263_24_25": kuweta 3263,
  zeby 24-25); sam lancuch numerow zebow ("24-25-26") to zeby, nie kuweta.
"#1234" = zlecenie prywatne, kandydat "#1234" (numer zlecenia z maila - cyfry bez zmian). Ten sam numer kilka razy = jeden
kandydat. Dokladnie jeden kandydat = kuweta; zaden = brak (None); KILKU = kuweta NIEJEDNOZNACZNA: program nie wybiera po
cichu pierwszego, tylko zapisuje oznaczenie ``"?" + kandydaci po przecinku`` (np. "?46,3263") - takiej wartosci nie ma
na zadnej kuwecie, wiec nic sie z nia nie zgodzi, a ekran pokazuje kandydatow (licznik "foldery z niejednoznaczna kuweta").
Nazwy porownywane sa w postaci Unicode NFC (OneDrive zapisuje czasem litery z ogonkami jako litera + znak laczacy, NFD).

DANE OSOBOWE: nazwy folderow i plikow zawieraja nazwiska. Funkcje tego modulu nie wyciagaja nazwiska (zwracaja tylko kuwete,
postac znormalizowana do porownan z kolumna H Excela, zeby i typ); wynik ``znormalizuj`` i ``klucz_pliku`` to nadal nazwa
- wolno go trzymac tylko w kolumnach z nazwami (``baza.KOLUMNY_Z_NAZWAMI``). Tylko biblioteka standardowa (typ i zeby
z nazwy exocad bierze ``katalog.typ_i_zeby_z_nazwy``, importowany dopiero przy wywolaniu). Opis: ``opisy_modulow/pula.md``.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import PurePath

KUWETA_BEZ_ZER = True  # decyzja robocza 1 (17.11.2026): zera wiodace usuwane, porownanie i pokazywanie bez zer
KUWETA_MAX_CYFR = 4  # numer kuwety: do 4 cyfr znaczacych (1-9999)
ROK_DATY_MIN = 2020  # D19: data z rokiem wczesniejszym i zebami FDI w miejscu miesiaca i dnia = numer kuwety + zeby
NIEJEDNOZNACZNA = "?"  # poczatek oznaczenia kuwety niejednoznacznej: "?46,3263"
PRYWATNE = "#"

# samodzielna liczba: bez liter i cyfr tuz obok (spacja, kropka, podkreslnik, lacznik = separator)
_LICZBA = re.compile(r"(?<![^\W_])\d+(?![^\W_])")
# kandydat na numer kuwety ("1784PG": z prawej wolno przylegac literom kodu) albo numer prywatny "#1234"
_KANDYDAT = re.compile(r"#\s*(\d+)|(?<![^\W_])(\d+)(?!\d)")
# granica liczba -> litery ("1784PG" -> "1784 PG") w postaci do porownan
_LICZBA_LITERY = re.compile(r"(?<=\d)(?=[^\W\d_])")
# daty w nazwie folderu (tylko poprawne zakresy): RRRR-MM-DD (tez z "_" albo "."), DD-MM-RRRR i DD-MM-RR
_DZIEN, _MIESIAC, _ROK, _SEP = r"(?:0?[1-9]|[12]\d|3[01])", r"(?:0?[1-9]|1[0-2])", r"(?:19|20)\d{2}", r"[-_.]"
_DATA = re.compile(rf"(?<!\d)(?:{_ROK}{_SEP}{_MIESIAC}{_SEP}{_DZIEN}|{_DZIEN}{_SEP}{_MIESIAC}{_SEP}(?:{_ROK}|\d{{2}}))(?!\d)")
# lancuch liczb sklejonych lacznikiem albo podkreslnikiem ("3263-24-25", "3263_24_25", "24-25-26")
_LANCUCH = re.compile(r"(?<![^\W_])\d+(?:[-_]\d+)+(?![^\W_])")
_ZEBY_FDI = {f"{c}{z}" for c in range(1, 5) for z in range(1, 9)}
TYP_NIEZNANY = "nieznany"


def postac_numeru(cyfry: str) -> str:
    """Postac numeru do porownan i pokazywania (decyzja robocza 1): bez zer wiodacych ("0412" -> "412", "0" -> "0")."""
    return str(int(cyfry)) if KUWETA_BEZ_ZER else cyfry


def nfc(tekst: str) -> str:
    """Postac NFC (litera z ogonkiem jako jeden znak)."""
    return unicodedata.normalize("NFC", tekst)


@dataclass(frozen=True)
class Zlecenie:
    """Wynik rozbioru nazwy folderu zlecenia: kuweta (albo oznaczenie niejednoznacznej "?a,b"), czy prywatne, postac do
    porownan, kandydaci na kuwete (bez wydzielonego nazwiska)."""
    kuweta: str | None
    prywatne: bool
    folder_norm: str
    kandydaci: tuple[str, ...] = ()

    @property
    def niejednoznaczna(self) -> bool:
        return len(self.kandydaci) > 1


def _bez_daty(m: re.Match) -> str:
    """Data -> spacja. D19: lancuch bez kropek z rokiem sprzed ``ROK_DATY_MIN``, ktorego dwie ostatnie liczby to zeby FDI
    ("2012_11_21", "5-11-12"), zostaje - to numer kuwety z zebami (rozbiera go ``_bez_zebow``), nie data zlecenia."""
    tekst = m.group()
    if "." not in tekst:
        liczby = re.split(r"[-_]", tekst)
        rok = int(liczby[0]) if len(liczby[0]) == 4 else int(liczby[2]) if len(liczby[2]) == 4 else 2000 + int(liczby[2])
        if rok < ROK_DATY_MIN and liczby[1] in _ZEBY_FDI and liczby[2] in _ZEBY_FDI:
            return tekst
    return " "


def _bez_zebow(m: re.Match) -> str:
    """Lancuch "3263-24-25": numery zebow FDI po pierwszej liczbie nie sa kandydatami; sam lancuch zebow ("24-25") tez nie."""
    liczby = re.split(r"[-_]", m.group())
    if not all(x in _ZEBY_FDI for x in liczby[1:]):
        return m.group()
    return " " if liczby[0] in _ZEBY_FDI else f" {liczby[0]} "


def kandydaci_z_nazwy(folder: str) -> tuple[str, ...]:
    """Kandydaci na numer kuwety w nazwie folderu (w kolejnosci wystapienia, bez powtorzen): "3263", "41", "#1234"."""
    tekst = _LANCUCH.sub(_bez_zebow, _DATA.sub(_bez_daty, nfc(folder)))
    wynik: list[str] = []
    for m in _KANDYDAT.finditer(tekst):
        if m.group(1) is not None:
            k = PRYWATNE + m.group(1)
        elif len(m.group(2).lstrip("0") or "0") <= KUWETA_MAX_CYFR:
            k = postac_numeru(m.group(2))
        else:
            continue
        if k not in wynik:
            wynik.append(k)
    return tuple(wynik)


def _kuweta_z_kandydatow(kandydaci: tuple[str, ...]) -> str | None:
    if not kandydaci:
        return None
    return kandydaci[0] if len(kandydaci) == 1 else NIEJEDNOZNACZNA + ",".join(kandydaci)


def kuweta(folder: str) -> str | None:
    """Numer kuwety z nazwy folderu (tekst: "3263", "41", "#1234"), oznaczenie kuwety niejednoznacznej ("?46,3263") albo None."""
    return _kuweta_z_kandydatow(kandydaci_z_nazwy(folder))


def czy_niejednoznaczna(kuweta_: str | None) -> bool:
    """Czy wartosc ``zlecenia.kuweta`` / ``Wpis.kuweta`` to oznaczenie kuwety niejednoznacznej."""
    return bool(kuweta_) and kuweta_.startswith(NIEJEDNOZNACZNA)


def kandydaci_kuwety(kuweta_: str | None) -> tuple[str, ...]:
    """Kandydaci zapisani w wartosci kuwety: "?46,3263" -> ("46", "3263"); "3263" -> ("3263",); None -> ()."""
    if not kuweta_:
        return ()
    return tuple(kuweta_[len(NIEJEDNOZNACZNA):].split(",")) if czy_niejednoznaczna(kuweta_) else (kuweta_,)


def znormalizuj(tekst: str) -> str:
    """Postac do porownan (kolumna H Excela): NFC, male litery, pojedyncze spacje, liczby bez zer wiodacych, spacja miedzy
    liczba a sklejonymi z nia z prawej literami ("Nazwisko 1784PG" i "nazwisko 1784 pg" -> "nazwisko 1784 pg")."""
    tekst = " ".join(_LICZBA_LITERY.sub(" ", nfc(tekst)).lower().split())
    return re.sub(r"\d+", lambda m: postac_numeru(m.group()), tekst)


def rozbierz(folder: str) -> Zlecenie:
    """Folder zlecenia -> ``Zlecenie(kuweta, prywatne, folder_norm, kandydaci)``; prywatne = jedyny kandydat to "#NNNN"."""
    kandydaci = kandydaci_z_nazwy(folder)
    k = _kuweta_z_kandydatow(kandydaci)
    return Zlecenie(kuweta=k, prywatne=len(kandydaci) == 1 and k.startswith(PRYWATNE), folder_norm=znormalizuj(folder),
                    kandydaci=kandydaci)


def numer_zeba(plik: str) -> str | None:
    """Pierwszy numer FDI (11-18, 21-28, 31-38, 41-48) jako samodzielna liczba w nazwie pliku (bez rozszerzenia)."""
    for m in _LICZBA.finditer(PurePath(nfc(plik)).stem):
        if m.group() in _ZEBY_FDI:
            return m.group()
    return None


def zeby_i_typ(plik: str) -> tuple[str | None, str]:
    """(zeby "24-25-26" albo None, typ pracy) z nazwy pliku STL.

    Nazwa exocad (``...-24-25-26-bridge_cad.stl``): zeby i typ jak w ``katalog`` (korona, most, waxup, bez_lacznika);
    inna nazwa: typ "nieznany", zab = pierwszy samodzielny numer FDI ("zab 46.stl" -> "46").
    """
    from . import katalog as K  # ciezkie zaleznosci katalogu (numpy, trimesh) dopiero tutaj

    typ, zeby = K.typ_i_zeby_z_nazwy(nfc(PurePath(plik).name))
    if zeby:
        return "-".join(zeby), typ
    return numer_zeba(plik), TYP_NIEZNANY


def klucz_pliku(nazwa: str) -> str:
    """Postac nazwy pliku (albo sciezki "folder/plik") do porownan: NFC, ``\\`` -> ``/``, bez ``/`` i spacji na koncach,
    bez wielkosci liter. Uzywana do laczenia wierszy CSV / raportu z plikami indeksu."""
    return "/".join(c.strip() for c in nfc(nazwa).replace("\\", "/").strip().strip("/").split("/")).casefold()


def normalizuj_krazek(krazek: str | None) -> str | None:
    """Oznaczenie krazka: bez spacji na koncach, pojedyncze spacje, wielkie litery ("k-1101" -> "K-1101"); puste -> None."""
    if krazek is None:
        return None
    k = " ".join(nfc(str(krazek)).split()).upper()
    return k or None
