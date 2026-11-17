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
- `[plytki]` — katalogi modeli płytek, względem katalogu programu (nie bieżącego katalogu). Od R59 osiem układów: cztery nowe i cztery poprzednie `*_r54` (patrz „Układy płytek”); `ustawienia.toml` założony przed R59 trzeba uzupełnić o cztery wiersze `*_r54` ze wzoru — bez nich program działa, ale starych płytek nie ma na liście i nie są rozpoznawane (strażnik układu podpowie wtedy, że brakuje tych wierszy), a część testów jest czerwona (`test_straznik.py`, `test_uklad.py::test_wszystkie_plytki_z_ustawien`, `test_ustawienia.py`).
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

**Od R59 (14.11.2026):** nazwy `okragla_wieczorna` itd. w tych poleceniach oznaczają układ gniazd R59, więc polecenia działają tak, jak są, na zestawie wygenerowanym od nowa. Zestaw `dane/syntetyczne_P2` wygenerowany PRZED R59 jest w układzie R54 — bez zmian skończyłby się „PŁYTKA NIE PASUJE DO WYBRANEGO UKŁADU” (w `metryki_P2.py`: „żaden z N skanów nie pasuje do układu”). Dla takiego zestawu: `porownaj … --plytka okragla_wieczorna_r54`, `metryki_P2.py … --sufiks-ukladu _r54`. Nowy zestaw w układzie R59 generuj do innego folderu (np. `--wyjscie dane/syntetyczne_R59_P2`) albo z `--nadpisz`. Szczegóły: „Układy płytek: R59 i poprzedni R54” niżej.

- `katalog_projektow.py` — tabela projektów bez nazw (id, zęby, typ, objętość, obrys, szczelność, brzeg, gniazdo na każdej płytce) → `dane/katalog.json`.
- `stanowisko.porownaj` — na skanie płytki: wyrównanie po 3 stożkach (`plate`), numer z dołków (na kwadracie dołki leżą poza polem ø100 → podaj `--numer`), cięcie na gniazda, identyfikacja każdego fragmentu w puli (`match`). Wynik: tabela gniazdo → id projektu → zęby → pokrycie → pewność → status na stdout, `<skan>_wynik.json`, `<skan>_mapa.png` (zielone / żółte / szare gniazda, fiolet = podwójne, czerwone = poza gniazdem). `--plytka wieczorna|poranna|okragla_wieczorna|okragla_poranna` (układ R59) albo te same nazwy z `_r54` (stare płytki), `--wspolczynnik` (domyślnie: poranna 1,0, wieczorna środek `[synth]`), `--prawda <json>` liczy metryki na sztucznym skanie, `--bez-filtru` dopasowuje wszystkie projekty.
- `metryki_P2.py` — plate + match na całym zestawie z prawdą, warianty puli (podstawowa / rozszerzona o atrapy, z filtrem / bez, czułość na współczynnik) → `dane/wyniki_P2/metryki_P2*.json`. Wyniki z 2.11.2026: `raporty/P2_2026-11-02.md`.
- Progi `[match]` (pokrycie, odległość, pewność, filtr) tylko w `ustawienia.toml`.

## Układy płytek: R59 i poprzedni R54 (14.11.2026)

Od R59 płytki mają nowy układ gniazd: wieczorna 18 gniazd (6 × ø12, 12 × ø15) + 1 rynienka 60 × 15, poranna 23 gniazda (20 × ø12,5, 3 × ø15) + 1 rynienka 50 × 13 — nazwy `wieczorna`, `poranna`, `okragla_wieczorna`, `okragla_poranna`. Płytki fizyczne zamówione wcześniej mają układ R54 (18 + 2 i 31 + 2) i będą nadal skanowane: ich układ jest w programie pod nazwami `wieczorna_r54`, `poranna_r54`, `okragla_wieczorna_r54`, `okragla_poranna_r54` (modele w `modele_plytek/*_r54`, bajtowo jak przed R59).

- **Numery płytek są w obu układach te same** (n1–n3, n4–n6, n8, n9), więc numer z dołków nie mówi, czy płytka jest stara, czy nowa. Układ wybiera człowiek: `--plytka wieczorna_r54` w `porownaj` / `synth`, lista „[cytat usuniety]” w oknie. Stare płytki warto opisać („[cytat usuniety]”) i trzymać osobno.
- **Strażnik układu** (`plate`, opis w `opisy_modulow/plate.md`): gdy zeskanowana płytka nie pasuje do wybranego układu, `porownaj` nie ocenia żadnego gniazda — wynik ma `uklad_zgodny: false`, `uklad_komunikat` („płytka nie pasuje do wybranego układu…”), `uklady_pasujace` (np. `wieczorna_r54`, `okragla_wieczorna_r54`), puste `gniazda`, wszystkie liczniki `statusy_gniazd` = 0, a mapa PNG i mapa w oknie są przekreślone. Kod wyjścia `porownaj` zostaje 0 — o niezgodności mówi JSON, wiersz „PŁYTKA NIE PASUJE…” i „UWAGA:” na stdout. `--bez-straznika` wyłącza tylko sprawdzenie gniazd (rozstaw stożków jest sprawdzany zawsze); okno nie ma takiego wyłącznika. Gdy żaden układ z `[plytki]` nie pasuje, a w lokalnym `ustawienia.toml` nie ma układów `*_r54`, komunikat podpowiada: „dopisz 4 wiersze *_r54 z ustawienia.przyklad.toml”. Ten sam komunikat „płytka nie pasuje…” daje fałszywy albo zabrudzony stożek znacznika na dobrze wybranej płytce — wtedy oczyścić stożki i zeskanować ponownie. Progi sprawdzenia gniazd są dobrane na skanach syntetycznych — lista do sprawdzenia na prawdziwym skanie: „Laptop firmowy” pkt 7.
- Jedna rynienka = jeden most na płytkę; drugi most generator zapisuje w `pominiete` (na następną płytkę).
- Numery `id` gniazd są w obu układach inne — wyników i danych syntetycznych nie porównuje się po numerze gniazda. Zestawy sztucznych skanów sprzed R59 (`dane/syntetyczne_P2`, `dane/syntetyczne_P3a`) mają w prawdzie `wieczorna` / `poranna` / `okragla_…`, a to był układ R54: `narzedzia/metryki_P3a.py … --sufiks-ukladu _r54` (to samo w `metryki_P2.py`; `rzut_z_gory.py --plytka wieczorna_r54`).

```
py -3.12 -m stanowisko.porownaj --skan <skan starej płytki>.stl --projekty <folder> --plytka okragla_wieczorna_r54 --wspolczynnik 1.22
py -3.12 narzedzia/metryki_P3a.py --skany dane/syntetyczne_P2 dane/syntetyczne_P3a --projekty <folder> --sufiks-ukladu _r54 --procesy 8
py -3.12 narzedzia/straznik_R59.py --projekty <folder> --seedy 10        (liczniki strażnika: płytki zgodne i niezgodne, puste / częściowe / pełne)
py -3.12 narzedzia/pojemnosc_R59.py --projekty <folder> --seedy 20       (ile prac mieści płytka: układ R59 i R54)
```

Liczby (testy, strażnik, metryki stary / nowy układ, pojemność): `raporty/R59_2026-11-14.md`.

## Ukruszenia i okno (P3a, 2.11.2026)

Pełny łańcuch plate → match → **inspect** (moduł `stanowisko/inspect.py`, opis `opisy_modulow/inspect.md`): metoda A (mapa odchyłek: plamy ≥ 0,08 mm pod powierzchnią projektu z ostrą krawędzią w pasie 1,5 mm od brzegu), metoda B (ciągłość linii brzegu: pas 0–1,5 mm projektu vs skan, wcięcie ≥ 0,2 mm), decyzja: czerwone, gdy obie metody wskazują to samo miejsce albo wcięcie ≥ 0,4 mm, żółte „sprawdź”, gdy jedna; drgnięcie (podwójna powierzchnia) → „skan ponownie”; gładka poprawka ręczna > 2 mm → pomarańczowe; brak danych w skanie nigdy nie jest ubytkiem; pokrycie z match poniżej progu → „popraw ułożenie”. Progi w `ustawienia.toml [inspect]`.

```
py -3.12 -m stanowisko.porownaj --skan dane/syntetyczne_P2/skan_okragla_wieczorna_n8_s0100.stl --projekty <PC>\Desktop\Prace_test --plytka okragla_wieczorna --wspolczynnik 1.22 --prawda dane/syntetyczne_P2/skan_okragla_wieczorna_n8_s0100.json --wyjscie dane/wyniki_P3a
py -3.12 -m stanowisko.synth --projekty <PC>\Desktop\Prace_test --plytka okragla_wieczorna --ile 4 --seed 300 --wspolczynnik 1.22 --drgniecie 0.1 --poza-uklad --pole 100 --bokiem 0.35 --pokrycie 0.35 --poprawka 0.15 --wyjscie dane/syntetyczne_P3a
py -3.12 narzedzia/metryki_P3a.py --skany dane/syntetyczne_P2 dane/syntetyczne_P3a --projekty <PC>\Desktop\Prace_test
uruchom_okno.bat
```

**Od R59 (14.11.2026):** zestawy `dane/syntetyczne_P2` i `dane/syntetyczne_P3a` wygenerowane PRZED R59 są w układzie R54 — dla nich `porownaj … --plytka okragla_wieczorna_r54` i `metryki_P3a.py … --sufiks-ukladu _r54` (bez tego: „PŁYTKA NIE PASUJE DO WYBRANEGO UKŁADU” / „żaden z N skanów nie pasuje do układu”); w oknie wybrać układ `…_r54`. Polecenia w bloku działają bez zmian na zestawach wygenerowanych od nowa (układ R59; inny folder `--wyjscie` albo `--nadpisz`).

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
4. **Sprawdzenie**: `set PYTHONUTF8=1` i `py -3.12 -m pytest testy -q` (ok. 3 min; testy okna i inspect używają atrap; test na `dane/syntetyczne_P2` jest pomijany, gdy nie ma danych). **Aktualizacja istniejącej instalacji (program sprzed R59, własny `ustawienia.toml`):** po podmianie folderu programu dopisać w lokalnym `ustawienia.toml`, w sekcji `[plytki]`, cztery wiersze `wieczorna_r54`, `poranna_r54`, `okragla_wieczorna_r54`, `okragla_poranna_r54` z `ustawienia.przyklad.toml`. Bez nich stare płytki fizyczne (układ R54) nie są rozpoznawane — nie ma ich na liście, a każdy ich skan kończy się „płytka nie pasuje do wybranego układu” z podpowiedzią o brakujących wierszach — i część testów jest czerwona (`test_straznik.py`, `test_uklad.py`, `test_ustawienia.py`). Świeża instalacja (`copy ustawienia.przyklad.toml ustawienia.toml`) ma te wiersze od razu.
5. **Okno**: dwuklik `uruchom_okno.bat` (albo `py -3.12 -m stanowisko.ui_test`). Wybrać skan (STL), folder projektów, płytkę (kwadrat `wieczorna`/`poranna` albo okrągła `okragla_wieczorna`/`okragla_poranna`; dla płytek fizycznych zamówionych przed R59 — te same nazwy z `_r54`; przy złym wyborze okno powie „Płytka nie pasuje do wybranego układu” i podpowie właściwy), współczynnik (wieczór: z raportu MillBox, np. 1,22; rano: 1,0), numer płytki (kwadrat: dołki kodu leżą poza polem ø100 — wpisać; okrągła: 0 = z dołków), „Porównaj”. Mapa: zielone / czerwone / żółte / szare / pomarańczowe; klik w gniazdo → obraz odchyłek; „Podgląd 3D” otwiera Open3D; „Zapisz JSON/PNG”; „Ukruszona” / „OK” zapisuje decyzję do `dane/decyzje.csv`.
6. **Test skanera (P3b) — przebieg**: (a) zeskanować pustą płytkę (kwadrat n1/n4 i okrągłą n8/n9) i zapisać STL; (b) płytkę z pracami całymi; (c) tę samą płytkę z 2–3 pracami celowo ukruszonymi (zaznaczyć na kartce gniazdo i miejsce); (d) tę samą płytkę z jedną pracą potrąconą w trakcie skanu (drgnięcie), jeśli skaner pozwala; (e) praca położona bokiem i praca częściowo zasłonięta. Każdy STL uruchomić w oknie i zapisać JSON/PNG do jednego folderu (np. `C:/stanowisko_dane/test_skanera`).
7. **Co zapisać** (do `raporty/P3b_<data>.md` i `ustawienia.toml`): σ szumu na płaskiej części płytki = `jakosc_wyrownania.plaszczyzna_rms_mm` z JSON wyniku (RMS odchyłki od płaszczyzny wierzchu); czy 3 stożki są widoczne (`jakosc_wyrownania.stozki_dopasowane` = 3, `znaczniki_reszta_mm` < 0,05); czy dołki kodu są widoczne (`bity` bez `null`, `numer_zrodlo` = `dolki`); pokrycie trafnych prac (`kandydaci[0].pokrycie` i `pokrycie_odwrotne`) osobno dla zielonych i spieczonych; czas na płytkę (`czas_s`); fałszywe i pominięte ubytki na pracach celowo ukruszonych; rozmiar STL ze skanera i liczba trójkątów. Z σ ustawić `[synth] szum_sigma_mm`; progi `[match]`/`[inspect]` stroić dopiero po porównaniu liczb z raportem P3a. **Strażnik układu (R59) — do sprawdzenia na prawdziwym skanie:** (a) dla starej płytki z układem `…_r54` i (gdy przyjdą) nowej płytki z układem R59, pustej i pełnej prac, zapisać `jakosc_wyrownania.uklad_zgodny`, `uklad_gniazdo_nad_pelnym_mm2` (K1; na skanach syntetycznych płytka zgodna ≤ 48, próg 150) i `uklad_dziura_w_pelnym_mm2` (K2; zgodna 0, próg 50) — progi są dobrane wyłącznie na skanach syntetycznych z 17 projektów; (b) ten sam skan porównać z celowo złym układem — ma być „płytka nie pasuje do wybranego układu” z nazwą właściwego układu; (c) przy fałszywym alarmie na płytce zgodnej: okno nie ma wyłącznika strażnika i technik nie przejdzie w nim dalej — najpierw oczyścić stożki i zeskanować ponownie, a gdy alarm zostaje, uruchomić `py -3.12 -m stanowisko.porownaj … --bez-straznika` z wiersza poleceń i zapisać K1, K2 z JSON; (d) granica na przyszłość: strażnik nie odróżni dwóch układów o tych samych stożkach różniących się tylko podziałem rynienki (odłożony wariant D3‑b; dziś takiej pary nie ma) — opis w `opisy_modulow/plate.md`.

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
| `modele_plytek/<wieczorna|poranna|okragla_wieczorna|okragla_poranna>/` | `uklad.json` (współrzędne gniazd, znaczników, dołków kodu) i `plytka_n<N>.stl` z projektu ramek v2, układ R59 (okrągłe: n8, n9 + `plytka_bazowa.stl`) |
| `modele_plytek/<…>_r54/` | to samo dla poprzedniego układu R54 — stare płytki fizyczne (pliki bajtowo jak przed R59) |
| `narzedzia/` | atrapy koron, rzut z góry, katalog projektów, metryki P2 i P3a, R59: liczniki strażnika układu i pojemność płytek; później kalibracja ramek |
| `testy/` | pytest, dane syntetyczne |
| `opisy_modulow/` | jeden plik na moduł: co robi, wejście, wyjście, kryterium „działa” — czytać przed zmianą kodu |
| `ustawienia.toml` | jedyny plik ustawień: ścieżki, progi, parametry (lokalny; wzór `ustawienia.przyklad.toml`) |
| `uruchom_okno.bat` | okno testowe jednym kliknięciem (`py -3.12 -m stanowisko.ui_test`) |
| `raporty/` | raporty z sesji naprawczych i testowych |
| `dane/` | lokalne: STL projektów, raporty MillBox, kopia Excela, skany syntetyczne, wyniki, `decyzje.csv` (poza repozytorium) |

## Układ współrzędnych

Plik układu płytki ma początek w środku **górnej** powierzchni płytki (x w prawo, y do tyłu). W STL płytki ta płaszczyzna leży na z = `thickness` z `uklad.json` (dziś 8 mm; `Gniazdo.z_top`), spód płytki na z = 0. Skany syntetyczne i wszystkie moduły pracują w układzie STL płytki; moduł plate ma sprowadzać prawdziwy skan do tego układu po trzech stożkach narożnych.
