"""Wczytanie i walidacja pliku ustawień ``ustawienia.toml`` (jedyne źródło progów i ścieżek).

Plik leży w katalogu głównym programu (obok ``README.md``); wzór z opisem
kluczy: ``ustawienia.przyklad.toml``. Ścieżki względne w ``[plytki]`` liczone
są od katalogu programu, nie od bieżącego katalogu.

Każdy klucz ma w ``SCHEMAT`` typ i moduł, który go czyta (albo „przyszły moduł”),
więc literówka albo brakujący klucz kończy się błędem z nazwą pliku i klucza.
"""
from __future__ import annotations

import copy
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
        "folder_eksportu_skanera": (str, "aplikacja"),
        "folder_cyrkon": (str, "aplikacja"),
        "folder_prywatne": (str, PRZYSZLY),
        "folder_millbox": (str, PRZYSZLY),
        "baza": (str, "baza"),
        "log_excel": (str, "excel"),
        "wyniki": (str, "session"),  # E3-A1, opcjonalny (DOMYSLNE_NOWYCH)
        "podglady": (str, "aplikacja"),  # E3-A3a, opcjonalne (DOMYSLNE_NOWYCH)
        "pula_cache": (str, "aplikacja"),
        "logi": (str, "aplikacja"),
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
        "filtr_wysokosc_min_udzial": (float, "match"),
        "korekta_skali": (bool, "match"),
        "korekta_skali_okno_proc": (float, "match"),
        "korekta_skali_ostrzezenie_proc": (float, "match"),
        "korekta_skali_pas_brzegu_mm": (float, "match"),
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
        "kolumna_kuwety": (str, "excel"),
        "kolumna_nazwy": (str, "excel"),
        "kolumna_odhaczenia": (str, "excel"),
        "kolor_rgb": (list, "excel"),
        "tryb_pytaj_przed_zapisem": (bool, "excel"),
        # E3-A9 (18.11.2026): klucze opcjonalne (DOMYSLNE_NOWYCH) - zalozenia o arkuszu do potwierdzenia na kopii pliku (D2)
        "kolumna_daty": (str, "excel"),
        "pierwszy_wiersz": (int, "excel"),
        "skoroszyt": (str, "excel"),
        "arkusz": (str, "excel"),
        "tryb": (str, "excel"),
        "odswiez_co_min": (float, "excel"),
    },
    "ramki": {
        "port": (int, PRZYSZLY),
        "wieczorna_host": (str, PRZYSZLY),
        "poranna_host": (str, PRZYSZLY),
    },
    # E3-A1 (etap 3): sekcja w całości opcjonalna — wszystkie klucze mają wartość w DOMYSLNE_NOWYCH, plik sprzed etapu 3 jej nie ma
    "sesja": {
        "operatorzy": (list, "session"),
        "przechowuj_skany_dni": (int, PRZYSZLY),
        "granica_doby_godz": (int, "session"),
        "zmiany_start_godz": (list, "session"),
        "ponowny_skan_okno_min": (int, "session"),
        "ponowny_skan_min_wspolnych": (float, "session"),  # E3-A1p (18.11.2026)
    },
    # E3-A3a (etap 3): sekcje w całości opcjonalne — parametry modułów scanner i silnik (wartości domyślne = stałe tych modułów)
    "scanner": {
        "stabilizacja_ms": (float, "aplikacja"),
        "min_rozmiar_mb": (float, "aplikacja"),
        "min_trojkatow": (int, "aplikacja"),
        "wzorzec_pliku": (str, "aplikacja"),
        "rekurencyjnie": (bool, "aplikacja"),
        "obserwator": (str, "aplikacja"),
    },
    "silnik": {
        "limit_zadania_s": (float, "aplikacja"),
        "czekaj_na_plik_s": (float, "aplikacja"),
        "pamiec_linii": (bool, "aplikacja"),
        "ponow_plik_niedostepny": (int, "aplikacja"),
    },
}


# Układy płytek dostarczane z programem. Układ, którego nie ma w [plytki] lokalnego ustawienia.toml (plik sprzed R59 nie ma
# wierszy *_r54), jest dopisywany przy wczytaniu, jeśli jego katalog z uklad.json istnieje — stare płytki fizyczne działają
# bez ręcznej zmiany pliku, a automatyczne rozpoznanie układu (porownaj: --plytka auto) widzi wszystkie układy.
UKLADY_WBUDOWANE = ("wieczorna", "poranna", "okragla_wieczorna", "okragla_poranna",
                    "wieczorna_r54", "poranna_r54", "okragla_wieczorna_r54", "okragla_poranna_r54")
KATALOG_MODELI_WZGLEDNY = "modele_plytek"


# Klucze dodane po R59 (16.11.2026). Lokalny ustawienia.toml założony wcześniej ich nie ma — brakujący klucz z tej listy
# dostaje wartość ze wzoru (ustawienia.przyklad.toml; zgodność sprawdza test), zamiast błędu „brak klucza”. Klucz wpisany
# w pliku ma pierwszeństwo. Klucze sprzed R59 nadal są wymagane.
DOMYSLNE_NOWYCH = {
    "match": {"filtr_wysokosc_min_udzial": 0.5, "korekta_skali": True, "korekta_skali_okno_proc": 1.0, "korekta_skali_ostrzezenie_proc": 0.3,
              "korekta_skali_pas_brzegu_mm": 2.0},
    "inspect": {"pas_brzegu_od": "linia_i_plaszczyzna", "brzeg_min_sprawdzony": 0.9, "brzeg_max_przerwa_mm": 1.5},
    "synth": {"odstep_ubytku_mm": 0.05, "krawedz_rozmiar_min_mm": 0.08, "krawedz_rozmiar_max_mm": 0.40},
    # E3-A9 (18.11.2026): [excel] - kolumna daty (regula 3), pierwszy wiersz danych, skoroszyt i arkusz ("" = aktywny),
    # tryb ("pytaj" = zapis po zatwierdzeniu, "cien" = bez zapisu; DW10: bez zapisu samodzielnego), odswiezanie odczytu (min).
    "excel": {"kolumna_daty": "A", "pierwszy_wiersz": 2, "skoroszyt": "", "arkusz": "", "tryb": "pytaj", "odswiez_co_min": 5.0},
    # Etap 3 (E3-A1, 17.11.2026; plan etapu 3 sekcja 3.7): nowe klucze są wyłącznie opcjonalne — tu wartości domyślne.
    # [sesja] operatorzy: lista osób do wyboru na początku zmiany (DW3; lista jest wymagana do decyzji — przy pustej plik się
    # wczytuje, ale session odrzuca „Ukruszona” / „OK”); przechowuj_skany_dni: po ilu dniach wolno usuwać pliki skanów
    # (DW4; 0 = nie usuwać — tryb cienia); granica_doby_godz: początek doby roboczej (6 = zmiany 1, 2, 3 jednego dnia);
    # zmiany_start_godz: początki zmian; ponowny_skan_okno_min: do ilu minut ta sama płytka to „ponowny skan”, a nie nowy wsad.
    # E3-A1p (18.11.2026): ponowny_skan_min_wspolnych - pytanie o ponowny skan tylko, gdy wspolne projekty prac rozpoznanych
    # nowego i poprzedniego skanu to co najmniej taki udzial mniejszego zbioru projektow (0 = bez tego warunku, regula sprzed E3-A1p).
    # E3-A3a (17.11.2026): [sciezki] podglady — pliki *_podglad.npz z silnika (punkty i odchyłki gniazd do obrazu odchyłek);
    # pula_cache — pamięć linii brzegu projektów na dysku (silnik: pamiec_linii); logi — log programu i procesu analizy.
    # [scanner] i [silnik]: parametry konstruktorów Scanner / Silnik; wartości domyślne równe stałym tych modułów (test).
    "sciezki": {"wyniki": "dane/wyniki", "podglady": "dane/podglady", "pula_cache": "dane/pula_cache", "logi": "dane/logi"},
    "sesja": {"operatorzy": [], "przechowuj_skany_dni": 0, "granica_doby_godz": 6, "zmiany_start_godz": [6, 14, 22],
              "ponowny_skan_okno_min": 60, "ponowny_skan_min_wspolnych": 0.5},
    "scanner": {"stabilizacja_ms": 300, "min_rozmiar_mb": 0.0, "min_trojkatow": 1, "wzorzec_pliku": "*.stl", "rekurencyjnie": True,
                "obserwator": "watchdog"},
    # pamiec_linii domyslnie False - tak samo jak w silnik (pamiec_linii=None); recenzja PR #20, D11
    "silnik": {"limit_zadania_s": 600.0, "czekaj_na_plik_s": 60.0, "pamiec_linii": False, "ponow_plik_niedostepny": 3},
}

# Sekcje, których może nie być w pliku: każdy ich klucz ma wartość domyślną (dziś: [sesja], [scanner], [silnik]).
SEKCJE_OPCJONALNE = tuple(s for s, klucze in SCHEMAT.items() if klucze and set(klucze) <= set(DOMYSLNE_NOWYCH.get(s, {})))


def uzupelnij_domyslne(d: dict) -> list[str]:
    """Dopisuje brakujące klucze z ``DOMYSLNE_NOWYCH`` i brakujące sekcje opcjonalne; zwraca ``[sekcja] klucz`` dopisanych.

    Sekcja wymagana, której nie ma w pliku, nie jest zakładana (walidacja zgłosi „brak sekcji”).
    """
    dopisane = []
    for sekcja, klucze in DOMYSLNE_NOWYCH.items():
        if sekcja not in d and sekcja in SEKCJE_OPCJONALNE:
            d[sekcja] = {}
        if not isinstance(d.get(sekcja), dict):
            continue
        for k, v in klucze.items():
            if k not in d[sekcja]:
                d[sekcja][k] = copy.deepcopy(v)  # lista domyślna nie może być wspólna między wczytaniami
                dopisane.append(f"[{sekcja}] {k}")
    return dopisane


def uzupelnij_uklady_wbudowane(d: dict) -> list[str]:
    """Dopisuje do ``d["plytki"]`` brakujące układy wbudowane, których katalog istnieje; zwraca nazwy dopisanych."""
    dopisane = []
    for nazwa in UKLADY_WBUDOWANE:
        if nazwa not in d["plytki"] and (KORZEN / KATALOG_MODELI_WZGLEDNY / nazwa / "uklad.json").exists():
            d["plytki"][nazwa] = f"{KATALOG_MODELI_WZGLEDNY}/{nazwa}"
            dopisane.append(nazwa)
    return dopisane


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
    warunek(i["pas_brzegu_od"] in ("linia_i_plaszczyzna", "linia", "plaszczyzna"), "inspect", "pas_brzegu_od", "dopuszczalne: linia_i_plaszczyzna, linia, plaszczyzna")
    warunek(0 <= i["brzeg_min_sprawdzony"] <= 1, "inspect", "brzeg_min_sprawdzony", "udział z [0, 1]")
    warunek(i["brzeg_max_przerwa_mm"] >= 0, "inspect", "brzeg_max_przerwa_mm", "musi być >= 0")
    warunek(0 < m["prog_akceptacji_pokrycie"] <= 1, "match", "prog_akceptacji_pokrycie", "udział z przedziału (0, 1]")
    warunek(m["odleglosc_max_mm"] > 0, "match", "odleglosc_max_mm", "musi być > 0")
    warunek(0 < m["prog_ostrzezenia_pokrycie"] <= m["prog_akceptacji_pokrycie"], "match", "prog_ostrzezenia_pokrycie", "udział z (0, prog_akceptacji_pokrycie]")
    warunek(0 <= m["pewnosc_min"] <= 1, "match", "pewnosc_min", "udział z [0, 1]")
    warunek(m["filtr_wymiar_mm"] >= 0 and m["filtr_wymiar_udzial"] >= 0 and m["filtr_objetosc_udzial"] >= 0, "match", "filtr_wymiar_mm", "tolerancje filtru ≥ 0")
    warunek(0 <= m["filtr_wysokosc_min_udzial"] <= 1, "match", "filtr_wysokosc_min_udzial", "udział z [0, 1]")
    warunek(0 < m["korekta_skali_okno_proc"] <= 5, "match", "korekta_skali_okno_proc", "okno korekty skali w procentach, z (0, 5]")
    warunek(0 <= m["korekta_skali_ostrzezenie_proc"] <= m["korekta_skali_okno_proc"], "match", "korekta_skali_ostrzezenie_proc", "próg ostrzeżenia z [0, korekta_skali_okno_proc]")
    warunek(m["korekta_skali_pas_brzegu_mm"] >= 0, "match", "korekta_skali_pas_brzegu_mm", "musi być >= 0")
    warunek(1 <= d["ramki"]["port"] <= 65535, "ramki", "port", "port 1…65535")
    rgb = d["excel"]["kolor_rgb"]
    warunek(len(rgb) == 3 and all(_typ_zgodny(c, int) and 0 <= c <= 255 for c in rgb), "excel", "kolor_rgb", "trzy liczby 0…255")
    e = d["excel"]  # E3-A9: kolumny arkusza, tryb (DW10), odczyt
    kolumny = ("kolumna_daty", "kolumna_odhaczenia", "kolumna_kuwety", "kolumna_nazwy")
    for k in kolumny:
        warunek(e[k].isascii() and e[k].isalpha() and 1 <= len(e[k]) <= 3, "excel", k, "litera kolumny Excela, np. C (A…ZZZ)")
    warunek(len({e[k].upper() for k in kolumny}) == len(kolumny), "excel", "kolumna_daty",
            "kolumny daty, odhaczenia, kuwety i nazwy musza byc rozne")
    warunek(e["pierwszy_wiersz"] >= 1, "excel", "pierwszy_wiersz", "musi być >= 1 (wiersz 1 = naglowek -> 2)")
    warunek(e["tryb"] in ("pytaj", "cien"), "excel", "tryb", "dopuszczalne: pytaj, cien (etap 3, DW10: bez zapisu samodzielnego)")
    warunek(e["odswiez_co_min"] > 0, "excel", "odswiez_co_min", "musi być > 0 (minuty)")
    osoby = d["sesja"]["operatorzy"]
    warunek(all(isinstance(o, str) and o.strip() for o in osoby) and len(set(osoby)) == len(osoby), "sesja", "operatorzy",
            "lista niepustych, różnych nazw osób (może być pusta)")
    warunek(d["sesja"]["przechowuj_skany_dni"] >= 0, "sesja", "przechowuj_skany_dni", "musi być >= 0 (0 = nie usuwać skanów)")
    warunek(0 <= d["sesja"]["granica_doby_godz"] <= 23, "sesja", "granica_doby_godz", "godzina 0…23")
    zmiany = d["sesja"]["zmiany_start_godz"]
    warunek(bool(zmiany) and all(_typ_zgodny(g, int) and 0 <= g <= 23 for g in zmiany) and zmiany == sorted(set(zmiany)),
            "sesja", "zmiany_start_godz", "niepusta lista rosnących godzin 0…23")
    warunek(zmiany[0] == d["sesja"]["granica_doby_godz"], "sesja", "zmiany_start_godz",
            f"pierwsza zmiana musi zaczynać się o granicy doby (granica_doby_godz = {d['sesja']['granica_doby_godz']})")
    warunek(d["sesja"]["ponowny_skan_okno_min"] > 0, "sesja", "ponowny_skan_okno_min", "musi być > 0 (minuty)")
    warunek(0 <= d["sesja"]["ponowny_skan_min_wspolnych"] <= 1, "sesja", "ponowny_skan_min_wspolnych",
            "udzial z [0, 1] (0 = pytanie o ponowny skan bez warunku zgodnosci prac)")
    sc, si = d["scanner"], d["silnik"]
    warunek(sc["stabilizacja_ms"] >= 0, "scanner", "stabilizacja_ms", "musi być >= 0 (milisekundy)")
    warunek(sc["min_rozmiar_mb"] >= 0, "scanner", "min_rozmiar_mb", "musi być >= 0 (0 = bez progu)")
    warunek(sc["min_trojkatow"] >= 1, "scanner", "min_trojkatow", "musi być >= 1")
    warunek(bool(sc["wzorzec_pliku"].strip()), "scanner", "wzorzec_pliku", "niepusty wzorzec nazwy pliku, np. *.stl")
    warunek(sc["obserwator"] in ("watchdog", "odpytywanie"), "scanner", "obserwator", "dopuszczalne: watchdog, odpytywanie")
    warunek(si["limit_zadania_s"] > 0, "silnik", "limit_zadania_s", "musi być > 0 (sekundy)")
    warunek(si["czekaj_na_plik_s"] >= 0, "silnik", "czekaj_na_plik_s", "musi być >= 0 (sekundy)")
    warunek(si["ponow_plik_niedostepny"] >= 0, "silnik", "ponow_plik_niedostepny", "musi być >= 0 (liczba ponowień)")
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
    uzupelnij_domyslne(d)
    osoby = d.get("sesja", {}).get("operatorzy") if isinstance(d.get("sesja"), dict) else None
    if isinstance(osoby, list):  # nazwy osób bez białych znaków na końcach (inaczej osoby z listy nie da się wybrać)
        d["sesja"]["operatorzy"] = [o.strip() if isinstance(o, str) else o for o in osoby]
    d = _waliduj(d, plik)
    uzupelnij_uklady_wbudowane(d)
    return d


@functools.lru_cache(maxsize=1)
def domyslne() -> dict:
    """Ustawienia z domyślnego pliku, wczytane raz na proces (wartości domyślne ``synth.Opcje``)."""
    return wczytaj_ustawienia()


def katalog_plytki(ust: dict, nazwa: str) -> Path:
    """Katalog modeli płytki z ``[plytki]``, względem katalogu programu."""
    if nazwa not in ust["plytki"]:
        raise BladUstawien(f"[plytki]: brak płytki {nazwa!r} (są: {', '.join(ust['plytki'])})")
    return (KORZEN / ust["plytki"][nazwa]).resolve()
