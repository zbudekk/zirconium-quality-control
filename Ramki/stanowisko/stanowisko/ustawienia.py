"""Wczytanie i walidacja pliku ustawień ``ustawienia.toml`` (jedyne źródło progów i ścieżek).

Plik leży w katalogu głównym programu (obok ``README.md``); wzór z opisem
kluczy: ``ustawienia.przyklad.toml``. Ścieżki względne w ``[plytki]`` liczone
są od katalogu programu, nie od bieżącego katalogu.

Każdy klucz ma w ``SCHEMAT`` typ i moduł, który go czyta (albo „przyszły moduł”),
więc literówka albo brakujący klucz kończy się błędem z nazwą pliku i klucza.
"""
from __future__ import annotations

import functools
import math
import tomllib
from pathlib import Path

KORZEN = Path(__file__).resolve().parent.parent
PLIK_USTAWIEN = KORZEN / "ustawienia.toml"
PLIK_PRZYKLADU = KORZEN / "ustawienia.przyklad.toml"

PRZYSZLY = "przyszły moduł"
# sekcja → klucz → (typ, moduł czytający)
SCHEMAT: dict[str, dict[str, tuple[type, str]]] = {
    "sciezki": {
        "folder_eksportu_skanera": (str, PRZYSZLY),
        "folder_cyrkon": (str, PRZYSZLY),
        "folder_prywatne": (str, PRZYSZLY),
        "folder_millbox": (str, PRZYSZLY),
        "baza": (str, PRZYSZLY),
        "log_excel": (str, PRZYSZLY),
    },
    # dowolne nazwy układów płytek → katalog modeli: wieczorna, poranna, okragla_wieczorna, okragla_poranna (układ R59)
    # oraz wieczorna_r54, poranna_r54, okragla_wieczorna_r54, okragla_poranna_r54 (poprzedni układ R54, stare płytki);
    # wymagane są tylko dwa pierwsze, reszta jest dostępna, gdy jest wpisana w [plytki]
    "plytki": {
        "wieczorna": (str, "ustawienia"),
        "poranna": (str, "ustawienia"),
    },
    "match": {
        "prog_akceptacji_pokrycie": (float, "match"),
        "odleglosc_max_mm": (float, "match"),
        "prog_ostrzezenia_pokrycie": (float, "match"),
        "pewnosc_min": (float, "match"),
        "filtr_wymiar_mm": (float, "match"),
        "filtr_wymiar_udzial": (float, "match"),
        "filtr_objetosc_udzial": (float, "match"),
        "pula_wieczor_dni": (int, PRZYSZLY),
        "pula_rano_dni_roboczych": (int, PRZYSZLY),
        "usun_z_puli_po_dniach": (int, PRZYSZLY),
    },
    "inspect": {
        "prog_glebokosci_mm": (float, "inspect, synth"),
        "srednica_min_mm": (float, "inspect, synth"),
        "srednica_max_mm": (float, "inspect, synth"),
        "pas_brzegu_mm": (float, "inspect, synth"),
        "poprawka_min_mm": (float, "inspect"),
        "krawedz_pas_mm": (float, "inspect"),
        "min_punktow_plamy": (int, "inspect"),
        "drgniecie_odchylka_mm": (float, "inspect"),
        "drgniecie_udzial_w_komorce": (float, "inspect"),
        "drgniecie_udzial_obszaru": (float, "inspect"),
        "wciecie_min_mm": (float, "inspect"),
        "wciecie_pewne_mm": (float, "inspect"),
        "linia_min_udzial": (float, "inspect"),
        "pas_brzegu_od": (str, "inspect"),
        "brzeg_min_sprawdzony": (float, "inspect"),
        "brzeg_max_przerwa_mm": (float, "inspect"),
    },
    "synth": {
        "szum_sigma_mm": (float, "synth"),
        "wspolczynnik_min": (float, "synth"),
        "wspolczynnik_max": (float, "synth"),
        "odstep_ubytku_mm": (float, "synth"),
        "krawedz_rozmiar_min_mm": (float, "synth"),
        "krawedz_rozmiar_max_mm": (float, "synth"),
    },
    "excel": {
        "kolumna_kuwety": (str, PRZYSZLY),
        "kolumna_nazwy": (str, PRZYSZLY),
        "kolumna_odhaczenia": (str, PRZYSZLY),
        "kolor_rgb": (list, PRZYSZLY),
        "tryb_pytaj_przed_zapisem": (bool, PRZYSZLY),
    },
    "ramki": {
        "port": (int, PRZYSZLY),
        "wieczorna_host": (str, PRZYSZLY),
        "poranna_host": (str, PRZYSZLY),
    },
}


class BladUstawien(ValueError):
    """Zły plik ustawień; komunikat zaczyna się od nazwy pliku i klucza."""


def _typ_zgodny(v, typ: type) -> bool:
    if typ is float:  # liczba całkowita w miejscu ułamka jest w porządku, bool nie
        return isinstance(v, (int, float)) and not isinstance(v, bool)
    if typ is int:
        return isinstance(v, int) and not isinstance(v, bool)
    return isinstance(v, typ)


def _waliduj(d: dict, plik: Path) -> dict:
    nazwa = plik.name

    def blad(klucz: str, co: str) -> BladUstawien:
        return BladUstawien(f"{nazwa}: {klucz}: {co}")

    for sekcja in d:
        if sekcja not in SCHEMAT:
            raise blad(f"[{sekcja}]", f"nieznana sekcja (znane: {', '.join(SCHEMAT)})")
    for sekcja, klucze in SCHEMAT.items():
        if not isinstance(d.get(sekcja), dict):
            raise blad(f"[{sekcja}]", "brak sekcji")
        for k in d[sekcja]:
            if k not in klucze and sekcja != "plytki":  # [plytki]: nazwy płytek są dowolne
                raise blad(f"[{sekcja}] {k}", "nieznany klucz (literówka?)")
            if sekcja == "plytki" and not isinstance(d[sekcja][k], str):
                raise blad(f"[{sekcja}] {k}", f"oczekiwano str, jest {d[sekcja][k]!r}")
        for k, (typ, _) in klucze.items():
            if k not in d[sekcja]:
                raise blad(f"[{sekcja}] {k}", "brak klucza")
            v = d[sekcja][k]
            if not _typ_zgodny(v, typ):
                raise blad(f"[{sekcja}] {k}", f"oczekiwano {typ.__name__}, jest {v!r} ({type(v).__name__})")
            if isinstance(v, float) and not math.isfinite(v):
                raise blad(f"[{sekcja}] {k}", f"wartość nieskończona/NaN: {v!r}")

    def warunek(ok: bool, sekcja: str, k: str, co: str) -> None:
        if not ok:
            raise blad(f"[{sekcja}] {k}", f"{co} (jest {d[sekcja][k]!r})")

    for sekcja in ("sciezki", "plytki"):
        for k, v in d[sekcja].items():
            warunek("\\" not in v, sekcja, k, "ścieżka z ukośnikami / (nie \\)")
    s, i, m = d["synth"], d["inspect"], d["match"]
    warunek(s["szum_sigma_mm"] >= 0, "synth", "szum_sigma_mm", "musi być >= 0")
    warunek(0 < s["wspolczynnik_min"] <= s["wspolczynnik_max"], "synth", "wspolczynnik_min", "musi być 0 < min <= wspolczynnik_max")
    warunek(s["odstep_ubytku_mm"] > 0, "synth", "odstep_ubytku_mm", "musi być > 0")
    warunek(0 < s["krawedz_rozmiar_min_mm"] <= s["krawedz_rozmiar_max_mm"], "synth", "krawedz_rozmiar_min_mm", "musi być 0 < min <= krawedz_rozmiar_max_mm")
    warunek(0 < i["srednica_min_mm"] <= i["srednica_max_mm"], "inspect", "srednica_min_mm", "musi być 0 < min <= srednica_max_mm")
    warunek(i["prog_glebokosci_mm"] > 0, "inspect", "prog_glebokosci_mm", "musi być > 0")
    warunek(i["pas_brzegu_mm"] > 0, "inspect", "pas_brzegu_mm", "musi być > 0")
    warunek(i["poprawka_min_mm"] >= i["srednica_max_mm"], "inspect", "poprawka_min_mm", "musi być >= srednica_max_mm")
    warunek(i["min_punktow_plamy"] >= 1, "inspect", "min_punktow_plamy", "musi być >= 1")
    warunek(i["drgniecie_odchylka_mm"] > 0 and 0 < i["drgniecie_udzial_w_komorce"] <= 1 and 0 < i["drgniecie_udzial_obszaru"] <= 1, "inspect", "drgniecie_udzial_obszaru", "odchyłka > 0, udziały z (0, 1]")
    warunek(0 < i["wciecie_min_mm"] <= i["wciecie_pewne_mm"], "inspect", "wciecie_min_mm", "musi być 0 < wciecie_min_mm <= wciecie_pewne_mm")
    warunek(0 <= i["linia_min_udzial"] <= 1, "inspect", "linia_min_udzial", "udział z [0, 1]")
    warunek(i["pas_brzegu_od"] in ("linia", "plaszczyzna"), "inspect", "pas_brzegu_od", "dopuszczalne: linia, plaszczyzna")
    warunek(0 <= i["brzeg_min_sprawdzony"] <= 1, "inspect", "brzeg_min_sprawdzony", "udział z [0, 1]")
    warunek(i["brzeg_max_przerwa_mm"] >= 0, "inspect", "brzeg_max_przerwa_mm", "musi być >= 0")
    warunek(0 < m["prog_akceptacji_pokrycie"] <= 1, "match", "prog_akceptacji_pokrycie", "udział z przedziału (0, 1]")
    warunek(m["odleglosc_max_mm"] > 0, "match", "odleglosc_max_mm", "musi być > 0")
    warunek(0 < m["prog_ostrzezenia_pokrycie"] <= m["prog_akceptacji_pokrycie"], "match", "prog_ostrzezenia_pokrycie", "udział z (0, prog_akceptacji_pokrycie]")
    warunek(0 <= m["pewnosc_min"] <= 1, "match", "pewnosc_min", "udział z [0, 1]")
    warunek(m["filtr_wymiar_mm"] >= 0 and m["filtr_wymiar_udzial"] >= 0 and m["filtr_objetosc_udzial"] >= 0, "match", "filtr_wymiar_mm", "tolerancje filtru ≥ 0")
    warunek(1 <= d["ramki"]["port"] <= 65535, "ramki", "port", "port 1…65535")
    rgb = d["excel"]["kolor_rgb"]
    warunek(len(rgb) == 3 and all(_typ_zgodny(c, int) and 0 <= c <= 255 for c in rgb), "excel", "kolor_rgb", "trzy liczby 0…255")
    return d


def wczytaj_ustawienia(plik: Path | None = None) -> dict:
    """Wczytuje i sprawdza plik ustawień (domyślnie ``ustawienia.toml`` w katalogu programu)."""
    plik = Path(plik) if plik is not None else PLIK_USTAWIEN
    if not plik.exists():
        raise FileNotFoundError(
            f"brak pliku ustawień: {plik} — skopiuj {PLIK_PRZYKLADU.name} jako {PLIK_USTAWIEN.name} i uzupełnij ścieżki"
        )
    try:
        with open(plik, "rb") as f:
            d = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise BladUstawien(f"{plik.name}: błąd składni TOML: {e}") from e
    return _waliduj(d, plik)


@functools.lru_cache(maxsize=1)
def domyslne() -> dict:
    """Ustawienia z domyślnego pliku, wczytane raz na proces (wartości domyślne ``synth.Opcje``)."""
    return wczytaj_ustawienia()


def katalog_plytki(ust: dict, nazwa: str) -> Path:
    """Katalog modeli płytki z ``[plytki]``, względem katalogu programu."""
    if nazwa not in ust["plytki"]:
        raise BladUstawien(f"[plytki]: brak płytki {nazwa!r} (są: {', '.join(ust['plytki'])})")
    return (KORZEN / ust["plytki"][nazwa]).resolve()
