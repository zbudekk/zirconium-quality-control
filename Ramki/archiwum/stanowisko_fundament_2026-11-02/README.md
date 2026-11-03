# Stanowisko kontroli cyrkonii — program

Repozytorium programu stanowiska z planu wdrożenia v2 (`../Stanowisko kontroli cyrkonii — plan wdrozenia v2.md`). Jeden program w Pythonie na laptopie stanowiska, dziewięć modułów (`opisy_modulow/`), osobny program ramki na Raspberry Pi (później, `ramka/`).

## Uruchomienie (Windows, Python 3.12)

```
python -m pip install -r requirements.txt
python -m pytest testy -q
```

## Dane testowe bez skanera

Prawdziwe projekty STL z folderu „Cyrkon” wrzuć do `dane/stl/` (katalog `dane/` nie trafia do repozytorium). Dopóki ich nie ma, atrapy koron:

```
python narzedzia/atrapy_koron.py --wyjscie dane/stl --ile 12
python -m stanowisko.synth --projekty dane/stl --plytka wieczorna --ile 5 --seed 1
python narzedzia/rzut_z_gory.py dane/syntetyczne/*.stl --prawda
```

Każdy sztuczny skan to `skan_<plytka>_n<numer>_s<seed>.stl` + `.json` z prawdą (gniazdo, projekt, współczynnik, transformacja 4×4, ubytki z położeniem i rozmiarem, flaga drgnięcia, gniazda puste). Na tej prawdzie moduły plate, match i inspect liczą trafność i wykrywalność.

## Struktura

| Katalog | Co |
|---|---|
| `stanowisko/` | moduły programu: `uklad` (układ płytki), `synth` (generator); dalej `catalog`, `plate`, `match`, `inspect`, `session`, `ui`, `indicate`, `excel`, `scanner` |
| `modele_plytek/<wieczorna|poranna>/` | `uklad.json` (współrzędne gniazd, znaczników, dołków kodu) i `plytka_n<N>.stl` z projektu ramek v2 |
| `narzedzia/` | atrapy koron, rzut z góry, później: raport metryk, kalibracja ramek |
| `testy/` | pytest, dane syntetyczne |
| `opisy_modulow/` | jeden plik na moduł: co robi, wejście, wyjście, kryterium „działa” — czytać przed zmianą kodu |
| `ustawienia.toml` | jedyny plik ustawień: ścieżki, progi, parametry |
| `dane/` | lokalne: STL projektów, raporty MillBox, kopia Excela, skany syntetyczne (poza repozytorium) |

## Układ współrzędnych

Plik układu płytki ma początek w środku **górnej** powierzchni płytki (x w prawo, y do tyłu). W STL płytki ta płaszczyzna leży na z = 8 (`uklad.Z_TOP`), spód płytki na z = 0. Skany syntetyczne i wszystkie moduły pracują w układzie STL płytki; moduł plate ma sprowadzać prawdziwy skan do tego układu po trzech stożkach narożnych.
