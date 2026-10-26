"""Wczytywanie i walidacja ustawien stanowiska (ustawienia.toml + ustawienia.lokalne.toml).

Kolejnosc wyboru pliku: zmienna QC_USTAWIENIA > argument `sciezka` > ustawienia.toml w katalogu
roboczym > ustawienia.toml w katalogu repo. Potem nakladka ustawienia.lokalne.toml obok wybranego
pliku (moze tylko nadpisywac istniejace klucze). Sciezki wzgledne liczone sa wzgledem katalogu pliku.
"""

import os
import tomllib
from pathlib import Path

ZMIENNA_SRODOWISKA = "QC_USTAWIENIA"
NAZWA_PLIKU = "ustawienia.toml"
NAZWA_LOKALNEGO = "ustawienia.lokalne.toml"

# Schemat: sekcja -> klucz -> typ. Path = tekst w pliku, w obiekcie sciezka bezwzgledna.
SCHEMAT: dict[str, dict[str, type]] = {
    "sciezki": {
        "cyrkon": Path,
        "prywatne": Path,
        "raporty_millbox": Path,
        "eksport_skanera": Path,
        "baza": Path,
        "log_excela": Path,
        "wspolczynniki": Path,
    },
    "plytki": {
        "wieczorna": Path,
        "poranna": Path,
    },
    "skaner": {
        "gestosc_mm": float,
    },
    "dopasowanie": {
        "tolerancja_objetosci": float,
        "tolerancja_wymiarow_mm": float,
        "odleglosc_mm": float,
        "min_pokrycie_wieczor": float,
        "min_pokrycie_rano": float,
        "margines_pewnosci": float,
        "voxel_fpfh_mm": float,
        "max_kandydatow": int,
    },
    "ubytki": {
        "min_glebokosc_mm": float,
        "min_srednica_mm": float,
        "max_srednica_mm": float,
        "pas_brzegu_mm": float,
        "poprawka_min_srednica_mm": float,
        "drgniecie_udzial": float,
        "drgniecie_odleglosc_mm": float,
    },
    "plytka": {
        "max_blad_wyrownania_mm": float,
        "margines_gniazda_mm": float,
        "min_pole_pracy_mm2": float,
    },
    "pula": {
        "dni_rano": int,
        "dni_wieczor": int,
        "usuwaj_po_dniach": int,
    },
}


OPIS_TYPU = {float: "liczby", int: "liczby calkowitej", str: "tekstu", Path: "sciezki"}


class BladUstawien(Exception):
    """Bledny lub niekompletny plik ustawien."""


class Sekcja:
    """Sekcja ustawien tylko do odczytu; klucze dostepne jako atrybuty."""

    def __init__(self, nazwa: str, wartosci: dict):
        object.__setattr__(self, "_nazwa", nazwa)
        object.__setattr__(self, "_wartosci", dict(wartosci))

    def __getattr__(self, klucz: str):
        try:
            return self._wartosci[klucz]
        except KeyError:
            raise AttributeError(f"sekcja [{self._nazwa}] nie ma klucza {klucz}") from None

    def __setattr__(self, klucz: str, wartosc) -> None:
        raise AttributeError("ustawienia sa tylko do odczytu")

    def jako_slownik(self) -> dict:
        return dict(self._wartosci)

    def __repr__(self) -> str:
        return f"Sekcja({self._nazwa}, {self._wartosci!r})"


class Ustawienia:
    """Komplet ustawien: atrybuty sciezki, plytki, skaner, dopasowanie, ubytki, plytka, pula."""

    def __init__(self, plik: Path, sekcje: dict[str, Sekcja]):
        self.plik = plik
        for nazwa, sekcja in sekcje.items():
            setattr(self, nazwa, sekcja)

    def __repr__(self) -> str:
        return f"Ustawienia({self.plik})"


def katalog_repo() -> Path:
    """Katalog repo: rodzic katalogu pakietu qc/."""
    return Path(__file__).resolve().parent.parent


def _wybierz_plik(sciezka: str | Path | None) -> Path:
    z_env = os.environ.get(ZMIENNA_SRODOWISKA)
    if z_env:
        plik = Path(z_env)
        if not plik.is_file():
            raise BladUstawien(f"{ZMIENNA_SRODOWISKA} wskazuje nieistniejacy plik ustawien: {plik}")
        return plik.resolve()
    if sciezka is not None:
        plik = Path(sciezka)
        if not plik.is_file():
            raise BladUstawien(f"brak pliku ustawien: {plik}")
        return plik.resolve()
    for kandydat in (Path.cwd() / NAZWA_PLIKU, katalog_repo() / NAZWA_PLIKU):
        if kandydat.is_file():
            return kandydat.resolve()
    raise BladUstawien(f"nie znaleziono {NAZWA_PLIKU} w katalogu roboczym ani w {katalog_repo()}")


def _czytaj_toml(plik: Path) -> dict:
    try:
        with plik.open("rb") as f:
            return tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise BladUstawien(f"bledny TOML w {plik}: {e}") from e


def _sprawdz_typ(sekcja: str, klucz: str, wartosc, typ: type, plik: Path):
    nazwa = f"[{sekcja}] {klucz}"
    if isinstance(wartosc, bool):
        raise BladUstawien(f"{nazwa} w {plik}: oczekiwano {OPIS_TYPU[typ]}, jest wartosc logiczna")
    if typ is float:
        if not isinstance(wartosc, (int, float)):
            raise BladUstawien(f"{nazwa} w {plik}: oczekiwano liczby, jest {type(wartosc).__name__}")
        return float(wartosc)
    if typ is int:
        if not isinstance(wartosc, int):
            raise BladUstawien(f"{nazwa} w {plik}: oczekiwano liczby calkowitej, jest {type(wartosc).__name__}")
        return wartosc
    if typ in (str, Path):
        if not isinstance(wartosc, str) or not wartosc.strip():
            raise BladUstawien(f"{nazwa} w {plik}: oczekiwano niepustego tekstu")
        return wartosc
    raise BladUstawien(f"{nazwa}: nieobslugiwany typ w schemacie")


def _sprawdz_zawartosc(dane: dict, plik: Path, wymagaj_wszystkich: bool) -> dict[str, dict]:
    """Sprawdza sekcje i klucze wzgledem SCHEMAT; zwraca wartosci po kontroli typow."""
    wynik: dict[str, dict] = {}
    for sekcja, wartosci in dane.items():
        if sekcja not in SCHEMAT:
            raise BladUstawien(f"nieznana sekcja [{sekcja}] w {plik}")
        if not isinstance(wartosci, dict):
            raise BladUstawien(f"[{sekcja}] w {plik} musi byc sekcja, nie pojedyncza wartoscia")
        for klucz in wartosci:
            if klucz not in SCHEMAT[sekcja]:
                raise BladUstawien(f"nieznany klucz {klucz} w sekcji [{sekcja}] w {plik}")
        wynik[sekcja] = {
            klucz: _sprawdz_typ(sekcja, klucz, wartosc, SCHEMAT[sekcja][klucz], plik)
            for klucz, wartosc in wartosci.items()
        }
    if wymagaj_wszystkich:
        for sekcja, klucze in SCHEMAT.items():
            if sekcja not in wynik:
                raise BladUstawien(f"brak sekcji [{sekcja}] w {plik}")
            for klucz in klucze:
                if klucz not in wynik[sekcja]:
                    raise BladUstawien(f"brak klucza {klucz} w sekcji [{sekcja}] w {plik}")
    return wynik


def wczytaj(sciezka: str | Path | None = None) -> Ustawienia:
    """Wczytuje ustawienia (z nakladka lokalna) i zwraca obiekt Ustawienia."""
    plik = _wybierz_plik(sciezka)
    wartosci = _sprawdz_zawartosc(_czytaj_toml(plik), plik, wymagaj_wszystkich=True)

    lokalny = plik.parent / NAZWA_LOKALNEGO
    if lokalny.is_file():
        nakladka = _sprawdz_zawartosc(_czytaj_toml(lokalny), lokalny, wymagaj_wszystkich=False)
        for sekcja, nowe in nakladka.items():
            wartosci[sekcja].update(nowe)

    katalog = plik.parent
    sekcje = {}
    for sekcja, klucze in SCHEMAT.items():
        gotowe = {}
        for klucz, typ in klucze.items():
            wartosc = wartosci[sekcja][klucz]
            if typ is Path:
                wartosc = (katalog / Path(wartosc).expanduser()).resolve()
            gotowe[klucz] = wartosc
        sekcje[sekcja] = Sekcja(sekcja, gotowe)
    return Ustawienia(plik, sekcje)
