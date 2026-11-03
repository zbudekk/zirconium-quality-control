# Stanowisko kontroli cyrkonii — program

Repozytorium programu stanowiska z planu wdrożenia v2 (`../Stanowisko kontroli cyrkonii — plan wdrozenia v2.md`). Jeden program w Pythonie na laptopie stanowiska, dziewięć modułów (`opisy_modulow/`), osobny program ramki na Raspberry Pi (później, `ramka/`).

## Uruchomienie (Windows, Python 3.12)

Wszystkie polecenia z katalogu `stanowisko/`. Na tym laptopie `py` bez numeru uruchamia Pythona 3.14 — zawsze `py -3.12`.

```
py -3.12 -m pip install -r requirements.txt
copy ustawienia.przyklad.toml ustawienia.toml
set PYTHONUTF8=1
py -3.12 -m pytest testy -q
```

## Ustawienia

`ustawienia.toml` to jedyny plik ustawień: ścieżki tej maszyny, progi match/inspect, parametry generatora, Excel, ramki. Nie trafia do repozytorium (`.gitignore`); wzór z tymi samymi kluczami to `ustawienia.przyklad.toml` — na nowym laptopie skopiuj go jako `ustawienia.toml` i popraw ścieżki w `[sciezki]`.

- Czyta go `stanowisko/ustawienia.py` (`wczytaj_ustawienia(plik) -> dict`, `tomllib`). Każdy klucz ma w `SCHEMAT` typ i moduł, który go używa; brak klucza, nieznany klucz, zły typ albo wartość spoza zakresu kończy się błędem z nazwą pliku i klucza, np. `ustawienia.toml: [synth] szum_sigma_mm: oczekiwano float, jest '0.03' (str)`.
- `[plytki]` — katalogi modeli płytek, względem katalogu programu (nie bieżącego katalogu).
- `[synth]` — szum i skurcz generatora; zakres średnic i pas brzegu ubytków generator bierze z `[inspect]`, więc dane syntetyczne mieszczą się w specyfikacji detektora.
- Parametry wiersza poleceń mają domyślnie `None` = „wartość z toml”; podanie parametru nadpisuje toml dla jednego uruchomienia. `--ustawienia PLIK` wskazuje inny plik.
- Progi stroi się w toml na próbie testowej, nie w kodzie.

## Fundament

Kod z 2.11.2026 przed poprawkami P1 jest zamrożony jako podstawa dalszej pracy:

- tag git `fundament-2026-11-02` (commit `d867542`) w tym repozytorium,
- kopia plików (bez `dane/`, `.git/`, `.pytest_cache/`, `__pycache__/`) w `../archiwum/stanowisko_fundament_2026-11-02/`.

Poprawki znalezisk z sesji testowej 31.10 (`../sesje_2026-10-31/kod_a_stanowisko/znaleziska.md`) są na tym fundamencie; co naprawiono i co zostało — `raporty/P1_2026-11-02.md`.

## Porównanie skanu z projektami (P2, 2.11.2026)

Sztuczne skany z `synth` są wyłącznie danymi do budowy i pomiaru kodu, bo skanera jeszcze nie ma; właściwy test skanera odbędzie się na prawdziwych płytkach i prawdziwych pracach w sesji P3.

Projekty STL z exocad leżą w folderze z podfolderami zleceń (np. `<PC>\Desktop\Prace_test\<zlecenie>\*.stl`; podfoldery `_*` są pomijane). Nazwy tych plików i folderów zawierają nazwiska pacjentów — program nigdzie ich nie zapisuje: projekt ma identyfikator = 16 znaków SHA‑256 pliku, mapowanie id → ścieżka leży tylko w `dane/mapa_sciezek.json` (poza repozytorium).

```
py -3.12 narzedzia/katalog_projektow.py --projekty <PC>\Desktop\Prace_test
py -3.12 -m stanowisko.synth --projekty <PC>\Desktop\Prace_test --plytka okragla_wieczorna --ile 3 --seed 100 --wspolczynnik 1.22 --drgniecie 0.1 --poza-uklad --pole 100 --wyjscie dane/syntetyczne_P2
py -3.12 -m stanowisko.porownaj --skan dane/syntetyczne_P2/skan_okragla_wieczorna_n8_s0100.stl --projekty <PC>\Desktop\Prace_test --plytka okragla_wieczorna --wspolczynnik 1.22 --prawda dane/syntetyczne_P2/skan_okragla_wieczorna_n8_s0100.json --wyjscie dane/wyniki_P2
py -3.12 narzedzia/metryki_P2.py --skany dane/syntetyczne_P2 --projekty <PC>\Desktop\Prace_test --dodatkowe dane/stl
```

- `katalog_projektow.py` — tabela projektów bez nazw (id, zęby, typ, objętość, obrys, szczelność, brzeg, gniazdo na każdej płytce) → `dane/katalog.json`.
- `stanowisko.porownaj` — na skanie płytki: wyrównanie po 3 stożkach (`plate`), numer z dołków (na kwadracie dołki leżą poza polem ø100 → podaj `--numer`), cięcie na gniazda, identyfikacja każdego fragmentu w puli (`match`). Wynik: tabela gniazdo → id projektu → zęby → pokrycie → pewność → status na stdout, `<skan>_wynik.json`, `<skan>_mapa.png` (zielone / żółte / szare gniazda, fiolet = podwójne, czerwone = poza gniazdem). `--plytka wieczorna|poranna|okragla_wieczorna|okragla_poranna`, `--wspolczynnik` (domyślnie: poranna 1,0, wieczorna środek `[synth]`), `--prawda <json>` liczy metryki na sztucznym skanie, `--bez-filtru` dopasowuje wszystkie projekty.
- `metryki_P2.py` — plate + match na całym zestawie z prawdą, warianty puli (podstawowa / rozszerzona o atrapy, z filtrem / bez, czułość na współczynnik) → `dane/wyniki_P2/metryki_P2*.json`. Wyniki z 2.11.2026: `raporty/P2_2026-11-02.md`.
- Progi `[match]` (pokrycie, odległość, pewność, filtr) tylko w `ustawienia.toml`.

## Ukruszenia i okno (P3a, 2.11.2026)

Pełny łańcuch plate → match → **inspect** (moduł `stanowisko/inspect.py`, opis `opisy_modulow/inspect.md`): metoda A (mapa odchyłek: plamy ≥ 0,08 mm pod powierzchnią projektu z ostrą krawędzią w pasie 1,5 mm od brzegu), metoda B (ciągłość linii brzegu: pas 0–1,5 mm projektu vs skan, wcięcie ≥ 0,2 mm), decyzja: czerwone, gdy obie metody wskazują to samo miejsce albo wcięcie ≥ 0,4 mm, żółte „sprawdź”, gdy jedna; drgnięcie (podwójna powierzchnia) → „skan ponownie”; gładka poprawka ręczna > 2 mm → pomarańczowe; brak danych w skanie nigdy nie jest ubytkiem; pokrycie z match poniżej progu → „popraw ułożenie”. Progi w `ustawienia.toml [inspect]`.

```
py -3.12 -m stanowisko.porownaj --skan dane/syntetyczne_P2/skan_okragla_wieczorna_n8_s0100.stl --projekty <PC>\Desktop\Prace_test --plytka okragla_wieczorna --wspolczynnik 1.22 --prawda dane/syntetyczne_P2/skan_okragla_wieczorna_n8_s0100.json --wyjscie dane/wyniki_P3a
py -3.12 -m stanowisko.synth --projekty <PC>\Desktop\Prace_test --plytka okragla_wieczorna --ile 4 --seed 300 --wspolczynnik 1.22 --drgniecie 0.1 --poza-uklad --pole 100 --bokiem 0.35 --pokrycie 0.35 --poprawka 0.15 --wyjscie dane/syntetyczne_P3a
py -3.12 narzedzia/metryki_P3a.py --skany dane/syntetyczne_P2 dane/syntetyczne_P3a --projekty <PC>\Desktop\Prace_test
uruchom_okno.bat
```

- `porownaj` ma teraz statusy gniazd: zielone (rozpoznane, bez ubytku), czerwone (ubytek), żółte (sprawdź / popraw ułożenie / skan ponownie), szare (bez projektu), pomarańczowe (poprawka ręczna); `--bez-inspekcji` = tylko plate + match. JSON wyniku ma dla każdego gniazda `inspekcja` (ubytki z położeniem w układzie płytki, średnicą, głębokością, metodą i kolorem; plamy; wcięcia; drgnięcie; linia brzegu), PNG zaznacza ubytki kółkami. Z `--prawda` także `metryki_inspekcji` (wykryte / fałszywe per metoda i scenariusz).
- Generator: `--bokiem p` (praca bokiem / do góry nogami, widziana z góry), `--pokrycie p` (30–60 % powierzchni usunięte w plamach), `--poprawka p` (gładka poprawka ręczna); prawda ma `ulozenie`, `pokrycie`, `poprawki`, a ubytek `widoczny`.
- `metryki_P3a.py` — cały łańcuch na zestawach P2 (24 skany) + P3a (16 skanów z trudnymi scenariuszami) → `dane/wyniki_P3a/metryki_P3a.json`; wyniki i decyzje: `raporty/P3a_2026-11-02.md`.
- Okno `stanowisko/ui_test.py` (PySide6) — opis `opisy_modulow/ui.md`; decyzje technika („Ukruszona” / „OK”) trafiają do `dane/decyzje.csv` (bez nazwisk: id projektu SHA‑16, ząb, gniazdo, czas).

## Laptop firmowy — instalacja i test skanera bez Excela i SharePointa

1. **Python 3.12** z python.org (zaznaczyć „Add python.exe to PATH” i „py launcher”). Sprawdzić w wierszu poleceń: `py -3.12 --version`. Inne wersje Pythona nie przeszkadzają — program zawsze woła `py -3.12`.
2. **Program**: skopiować cały folder `stanowisko/` (bez `dane/` — to dane lokalne) np. do `C:\stanowisko\`. W nim, w wierszu poleceń:
   ```
   py -3.12 -m pip install -r requirements.txt
   copy ustawienia.przyklad.toml ustawienia.toml
   ```
   `requirements.txt` ma przypięte wersje (numpy 2.5.4, scipy 1.18.1, trimesh 5.2.0, open3d 0.20.0, PySide6 6.12.0, pillow, pytest); instalacja trwa kilka minut. Bez internetu: na tym laptopie `py -3.12 -m pip download -r requirements.txt -d kola` i na firmowym `py -3.12 -m pip install --no-index --find-links kola -r requirements.txt`.
3. **Foldery** (wpisać w `ustawienia.toml [sciezki]` ścieżki z ukośnikami `/`):
   - projekty STL: skopiować z SharePointa folder zleceń z plikami `…_cad.stl` (podfoldery zleceń, nazwy mogą zawierać nazwiska — program ich nigdzie nie zapisuje) np. do `C:/stanowisko_dane/projekty` → `folder_cyrkon`;
   - eksport skanera: folder, do którego Aidite zapisuje STL płytki (np. `C:/Aidite/Scandata`) → `folder_eksportu_skanera`.
4. **Sprawdzenie**: `set PYTHONUTF8=1` i `py -3.12 -m pytest testy -q` (ok. 3 min; testy okna i inspect używają atrap; test na `dane/syntetyczne_P2` jest pomijany, gdy nie ma danych).
5. **Okno**: dwuklik `uruchom_okno.bat` (albo `py -3.12 -m stanowisko.ui_test`). Wybrać skan (STL), folder projektów, płytkę (kwadrat `wieczorna`/`poranna` albo okrągła `okragla_wieczorna`/`okragla_poranna`), współczynnik (wieczór: z raportu MillBox, np. 1,22; rano: 1,0), numer płytki (kwadrat: dołki kodu leżą poza polem ø100 — wpisać; okrągła: 0 = z dołków), „Porównaj”. Mapa: zielone / czerwone / żółte / szare / pomarańczowe; klik w gniazdo → obraz odchyłek; „Podgląd 3D” otwiera Open3D; „Zapisz JSON/PNG”; „Ukruszona” / „OK” zapisuje decyzję do `dane/decyzje.csv`.
6. **Test skanera (P3b) — przebieg**: (a) zeskanować pustą płytkę (kwadrat n1/n4 i okrągłą n8/n9) i zapisać STL; (b) płytkę z pracami całymi; (c) tę samą płytkę z 2–3 pracami celowo ukruszonymi (zaznaczyć na kartce gniazdo i miejsce); (d) tę samą płytkę z jedną pracą potrąconą w trakcie skanu (drgnięcie), jeśli skaner pozwala; (e) praca położona bokiem i praca częściowo zasłonięta. Każdy STL uruchomić w oknie i zapisać JSON/PNG do jednego folderu (np. `C:/stanowisko_dane/test_skanera`).
7. **Co zapisać** (do `raporty/P3b_<data>.md` i `ustawienia.toml`): σ szumu na płaskiej części płytki = `jakosc_wyrownania.plaszczyzna_rms_mm` z JSON wyniku (RMS odchyłki od płaszczyzny wierzchu); czy 3 stożki są widoczne (`jakosc_wyrownania.stozki_dopasowane` = 3, `znaczniki_reszta_mm` < 0,05); czy dołki kodu są widoczne (`bity` bez `null`, `numer_zrodlo` = `dolki`); pokrycie trafnych prac (`kandydaci[0].pokrycie` i `pokrycie_odwrotne`) osobno dla zielonych i spieczonych; czas na płytkę (`czas_s`); fałszywe i pominięte ubytki na pracach celowo ukruszonych; rozmiar STL ze skanera i liczba trójkątów. Z σ ustawić `[synth] szum_sigma_mm`; progi `[match]`/`[inspect]` stroić dopiero po porównaniu liczb z raportem P3a.

## Dane testowe bez skanera

Prawdziwe projekty STL z folderu „Cyrkon” wrzuć do `dane/stl/` (katalog `dane/` nie trafia do repozytorium). Dopóki ich nie ma, atrapy koron:

```
py -3.12 narzedzia/atrapy_koron.py --wyjscie dane/stl --ile 12
py -3.12 -m stanowisko.synth --projekty dane/stl --plytka wieczorna --ile 5 --seed 1
py -3.12 narzedzia/rzut_z_gory.py dane/syntetyczne/skan_wieczorna_n2_s0001.stl --prawda
```

Każdy sztuczny skan to `skan_<plytka>_n<numer>_s<seed>.stl` + `.json` z prawdą (gniazdo, skrót projektu, współczynnik, transformacja 4×4, ubytki z położeniem, rozmiarem i flagą `wykrywalny`, flaga drgnięcia, gniazda puste). Na tej prawdzie moduły plate, match i inspect liczą trafność i wykrywalność. Projekt jest w prawdzie zapisany jako 16 znaków SHA‑256 pliku, bez nazwy; mapowanie skrót → nazwa pliku leży w `dane/mapa_projektow.json`. Istniejące pliki nie są nadpisywane bez `--nadpisz`.

## Struktura

| Katalog | Co |
|---|---|
| `stanowisko/` | moduły programu: `uklad` (układ płytki), `synth` (generator), `katalog` (cechy projektów bez nazw), `plate` (wyrównanie, numer, cięcie), `match` (identyfikacja), `inspect` (ukruszenia, drgnięcie, poprawka), `porownaj` (CLI: cały łańcuch), `ui_test` (okno PySide6) + `podglad3d` (Open3D, osobny proces); dalej `session`, pełne `ui`, `indicate`, `excel`, `scanner` |
| `modele_plytek/<wieczorna|poranna|okragla_wieczorna|okragla_poranna>/` | `uklad.json` (współrzędne gniazd, znaczników, dołków kodu) i `plytka_n<N>.stl` z projektu ramek v2 (okrągłe R57: n8, n9 + `plytka_bazowa.stl`) |
| `narzedzia/` | atrapy koron, rzut z góry, katalog projektów, metryki P2 i P3a; później kalibracja ramek |
| `testy/` | pytest, dane syntetyczne |
| `opisy_modulow/` | jeden plik na moduł: co robi, wejście, wyjście, kryterium „działa” — czytać przed zmianą kodu |
| `ustawienia.toml` | jedyny plik ustawień: ścieżki, progi, parametry (lokalny; wzór `ustawienia.przyklad.toml`) |
| `uruchom_okno.bat` | okno testowe jednym kliknięciem (`py -3.12 -m stanowisko.ui_test`) |
| `raporty/` | raporty z sesji naprawczych i testowych |
| `dane/` | lokalne: STL projektów, raporty MillBox, kopia Excela, skany syntetyczne, wyniki, `decyzje.csv` (poza repozytorium) |

## Układ współrzędnych

Plik układu płytki ma początek w środku **górnej** powierzchni płytki (x w prawo, y do tyłu). W STL płytki ta płaszczyzna leży na z = `thickness` z `uklad.json` (dziś 8 mm; `Gniazdo.z_top`), spód płytki na z = 0. Skany syntetyczne i wszystkie moduły pracują w układzie STL płytki; moduł plate ma sprowadzać prawdziwy skan do tego układu po trzech stożkach narożnych.
