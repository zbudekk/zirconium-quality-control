# Stanowisko kontroli cyrkonii — program

Repozytorium programu stanowiska z planu wdrożenia v2 (`../Stanowisko kontroli cyrkonii — plan wdrozenia v2.md`). Jeden program w Pythonie na laptopie stanowiska, dziewięć modułów (`opisy_modulow/`), osobny program ramki na Raspberry Pi (później, `ramka/`).

## Uruchomienie (Windows, Python 3.12)

**Na stanowisku program instaluje się z paczki wydania** (jedno polecenie, bez internetu) — sekcja „Instalacja z paczki wydania” niżej. Poniższe polecenia dotyczą pracy programisty na kopii repozytorium.

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
- `[plytki]` — katalogi modeli płytek, względem katalogu programu (nie bieżącego katalogu). Od R59 osiem układów: cztery nowe i cztery poprzednie `*_r54` (patrz „Układy płytek”); `ustawienia.toml` założony przed R59 nie wymaga zmian: od 15.11.2026 układy dostarczane z programem (cztery nowe i cztery `*_r54`), których w pliku nie ma, są dopisywane przy wczytaniu ustawień (`ustawienia.uzupelnij_uklady_wbudowane`); wiersz wpisany w pliku ma pierwszeństwo.
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

- **Numery płytek są w obu układach te same** (n1–n3, n4–n6, n8, n9), więc numer z dołków nie mówi, czy płytka jest stara, czy nowa. Od 15.11.2026 układ rozpoznaje program po rozstawie stożków znaczników (patrz „Rozpoznanie płytki”); ręcznie: `--plytka wieczorna_r54` w `porownaj` / `synth`, lista „Płytka” w oknie po wyłączeniu „rozpoznaj automatycznie”. Stare płytki warto opisać („R54”) i trzymać osobno.
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

## Rozpoznanie płytki bez wybierania układu (15.11.2026)

Pierwsze prawdziwe skany będą na starych płytkach (układ R54), a zamawiane są już nowe (R59) — program sam rozpoznaje, którą płytkę zeskanowano: `porownaj` ma `--plytka auto` jako wartość domyślną, okno ma zaznaczone „rozpoznaj automatycznie”.

```
py -3.12 -m stanowisko.porownaj --skan <skan>.stl --projekty <folder>
py -3.12 narzedzia/auto_uklad.py --skany dane/syntetyczne_P2 dane/syntetyczne_P3a --procesy 8
```

- Rodzinę (wieczorna / poranna × R59 / R54) wybiera rozstaw trzech stożków znaczników; kwadrat od koła odróżnia numer płytki (podany albo z dołków kodu), a bez numeru kształt brzegu płytki. Opis: `opisy_modulow/plate.md`, „Automatyczne rozpoznanie układu”.
- Wynik (`<skan>_wynik.json`): `plytka` = rozpoznany układ, `plytka_wybor` = `auto`, `uklad_auto` (podstawa decyzji, flaga `pewny`, kandydaci). Współczynnik bez `--wspolczynnik`: domyślny dla rozpoznanego typu (poranna 1,0; wieczorna środek `[synth]`).
- Rozpoznanie niepewne (ostrzeżenie „układ płytki rozpoznany niepewnie”) albo brak pasującego układu („nie rozpoznano układu płytki”, żadne gniazdo nie jest oceniane): podać `--numer` albo `--plytka`.
- Pomiar 15.11.2026 na 80 skanach syntetycznych (cztery typy płytek, R59 i R54): 80/80 poprawnie bez numeru, 32/32 z numerem; czas rozpoznania z wyrównaniem ok. 5 s (zamiast ok. 2,5 s). Na prawdziwym skanie jeszcze niesprawdzone.

## Dopasowanie i krawędź brzegu przed skanerem (15–16.11.2026)

**Filtr wymiarów i korekta skali (P1, P3).** `match` porównuje fragment skanu z projektem przyciętym do wysokości fragmentu: praca, której dół jest schowany w gnieździe albo niewidoczny z góry, nie gubi już właściwego projektu (`[match] filtr_wysokosc_min_udzial` — najmniejsza widoczna część wysokości, 0,5). Dla rozpoznanej pracy program wyznacza ze skanu poprawkę skali względem projektu × współczynnik (punkty bliżej brzegu niż `korekta_skali_pas_brzegu_mm` nie biorą udziału, więc ukruszenie brzegu skali nie zmienia) i — gdy mieści się w oknie ±`korekta_skali_okno_proc` (1 %) — porównuje skan z projektem w skali skorygowanej. Poprawka ponad `korekta_skali_ostrzezenie_proc` (0,3 %) daje ostrzeżenie „sprawdź współczynnik / krążek”: w JSON pole `skala` każdego gniazda (`poprawka_proc`, `zastosowana`, `powod`, `ostrzezenie`, `niepewna`, `wspolczynnik_ze_skanu`), w tabeli kolumna „skala %” („(…)” = zmierzona, niezastosowana; „!” = ostrzeżenie; „?” = estymata niepewna) i wiersz „OSTRZEŻENIE SKALI”. Na płytkach porannych (prace spieczone) poprawka jest tylko mierzona. Wyłącznik: `[match] korekta_skali = false`. Liczby: `raporty/czesc_A_filtr_i_skala_2026-11-15.md`.

**Krawędź brzegu (P2, P4).** Moduł `stanowisko/krawedz.py` wyznacza linię krawędzi brzegu KAŻDEGO filaru projektu (korona — 1 pętla, most — pętla na filar, korona implantowa bez łącznika — obwód powierzchni przylegania). Pas brzegu (`[inspect] pas_brzegu_mm`) w trybie domyślnym `pas_brzegu_od = "linia_i_plaszczyzna"` jest sumą pasa od tych linii i pasa sprzed P2 (od najwyższego punktu pracy): zasięg kontroli nigdy nie jest mniejszy niż przed P2, a dochodzi brzeg filarów leżący głęboko (mosty). Gdy przy linii brzegu któregoś filaru brakuje danych skanu, gniazdo jest ŻÓŁTE „nie sprawdzono” (status inspect `nie_sprawdzono`), nigdy zielone i nigdy czerwone; `inspekcja.brzeg` w JSON mówi, który filar, jaka część linii i dlaczego. Niepewna linia projektu (np. przy łącznikach mostu) trafia tylko do uwag. Progi: `brzeg_min_sprawdzony`, `brzeg_max_przerwa_mm`; `pas_brzegu_od = "linia"` — sam pas od linii (niepewna linia też daje „nie sprawdzono”), `"plaszczyzna"` — sposób sprzed P2 (do porównań). Generator: ubytek wycina materiał poprawnie (czasza kuli leży w materiale); ukruszenia celowe na samej krawędzi: `--krawedz 1-2 --krawedz-rozmiary 0.08,0.10,0.15 --krawedz-polozenie srodek,zewn,wewn` (rozmiar = promień kuli o środku na powierzchni); `--wersja-ubytkow 1` odtwarza bajt w bajt zestawy sprzed 15.11.2026. Pomiary: `narzedzia/metryki_krawedz.py`, raport `raporty/P2_P4_krawedz_brzegu_2026-11-16.md`.

**Aktualizacja istniejącej instalacji:** lokalnego `ustawienia.toml` nie trzeba zmieniać — klucze dodane po R59 (`[match]` filtr i korekta skali, `[inspect]` pas brzegu, `[synth]` krawędź) dostają przy wczytaniu wartość ze wzoru (`ustawienia.DOMYSLNE_NOWYCH`); wpis w pliku ma pierwszeństwo.

**Do zapisania na pierwszym prawdziwym skanie (P3b):** pole `skala` z JSON (poprawka ze skanu, `niepewna`) dla zielonych koron obok współczynnika z raportu MillBox; ile gniazd ma „nie sprawdzono” i z jakiego powodu.

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

## Dzień skanera — zbieranie pierwszych skanów (16.11.2026)

Okno „[cytat usuniety]”: w instalacji z paczki wydania dwuklik `C:\Stanowisko\Dzien_skanera.cmd` (ustawienia z `C:\Stanowisko\ustawienia.toml`, sesje w `C:\Stanowisko\dane\dzien_skanera\<data_godzina>\`; E3‑O4, 21.11.2026); w kopii roboczej programu dwuklik `uruchom_dzien_skanera.bat` (albo `py -3.12 -m stanowisko.dzien_skanera`). Prowadzi przez 14 kroków testu skanera (lista w `stanowisko/dzien_skanera_kroki.toml`) i samo kopiuje KAŻDY nowy albo zmieniony plik z folderu eksportu skanera (`[sciezki] folder_eksportu_skanera`; w oknie „[cytat usuniety]” albo „[cytat usuniety]”) do sesji `dane/dzien_skanera/<data_godzina>/` (kopia robocza; w instalacji — katalog podany wyżej) — oryginałów nie zmienia. Każdy skan STL dostaje ocenę prostym językiem (zielone / żółte / czerwone „[cytat usuniety]”), z automatycznie rozpoznaną płytką (`plate.rozpoznaj_uklad`); „[cytat usuniety]” dokumentuje ekrany programu skanera; każdy krok można pominąć z powodem. Po awarii albo zamknięciu okno wznawia sesję bez strat. „[cytat usuniety]” tworzy `RAPORT_dzien_skanera.md`, `SHA256SUMS.txt` i archiwum ZIP w `paczka/` (bez projektów `*_cad.stl`). Sprawdzenie otrzymanej paczki: `py -3.12 -m stanowisko.dzien_skanera --sprawdz <folder sesji albo zip>` (kod 0 = komplet, 3 = sumy zgodne, ale brakuje wymaganych kroków, 1 = błąd integralności). Instrukcje dla człowieka: `../sciaga_skaner_DentalScan_2026-11-16.md`, `../dzien_skanera_karta_2026-11-16.md`. Opis modułu: `opisy_modulow/dzien_skanera.md`. Pomiar szczegółowy skanu (narzędzie T10): `narzedzia/pomiar_skanu/`.

## Program „Stanowisko” — rdzeń aplikacji (etap 3, E3‑A3a, 17.11.2026)

Docelowy program: dwuklik `uruchom_stanowisko.bat` (albo `py -3.12 -m stanowisko.aplikacja [--ustawienia PLIK]`). Sam obserwuje folder skanera (`[sciezki] folder_eksportu_skanera`), każdy nowy skan analizuje w osobnym procesie (`silnik`), wynik zapisuje w bazie (`session`) i prowadzi stan wieczoru: mapa płytki z kolorami po decyzjach technika, pytania (ponowny skan tej samej płytki, płytka nie z tego trybu, brak numeru płytki), komunikaty (skan do powtórzenia, płytka niezgodna z układem, plik zajęty, błędy) i lista „do dofrezowania”. Po ponownym uruchomieniu sam dokańcza skany zapisane, gdy nie działał, i zadania, które czekały w kolejce — żaden skan nie ginie i żaden nie jest liczony dwa razy.

- Po E3‑A3a program ma kontroler (`stanowisko/aplikacja.py`), kontrakt dla okna (`stanowisko/kontroler_api.py`) i tabelę statusów (`stanowisko/statusy.py`); **ekran wieczorny buduje paczka A3b** — do tego czasu `uruchom_stanowisko.bat` pokazuje okno zastępcze z tekstem stanu. `py -3.12 -m stanowisko.aplikacja --atrapa` uruchamia program na danych sztucznych, bez skanera i analizy.
- Przed pierwszym uruchomieniem wpisz w `ustawienia.toml` osoby: `[sesja] operatorzy = ["…", "…"]` — bez wybranej osoby program przyjmuje skany, ale nie zapisuje decyzji. Osobę wybiera się na zmianę (06–14, 14–22, 22–06).
- Pula projektów na tym etapie: jeden folder (domyślnie `[sciezki] folder_cyrkon`) i współczynnik skurczu wpisany ręcznie albo dobierany przez program; katalog i pule z bazy dojdą w paczkach A4 / A5. Gdy w folderze nie ma plików STL, skany czekają na „Odśwież pulę” (program liczy pule od nowa przy kazdym skanie i po bledzie analizy - folder oprozniony po starcie tez daje "skany czekaja", nie "blad analizy").
- Start skanu (Spacja) to na razie interfejs z atrapą — program nie klika w programie skanera (decyzja DW5; prawdziwa akcja po próbach na skanerze).
- Program dziala w jednym egzemplarzu na dana baze: drugie uruchomienie (np. dwuklik dwa razy) konczy sie komunikatem "program juz dziala" (plik `dane/stanowisko.sqlite.blokada`, zwalniany przez system takze po awarii). Wynik, ktorego nie da sie zapisac (pelny dysk, baza zajeta), nie znika: zostaje na ekranie jako "nie zapisano" i jest zapisywany ponownie sam albo przyciskiem.
- Nowe klucze ustawień są opcjonalne (`[scanner]`, `[silnik]`, `[sciezki] podglady / pula_cache / logi`) — plik sprzed etapu 3 działa bez zmian. Dane programu: `dane/stanowisko.sqlite`, `dane/wyniki/`, `dane/podglady/`, `dane/logi/` (log bez nazw plikow skanow - zamiast nich skrot `sha16`), `dane/do_dofrezowania_biezaca.csv` (lista "do dofrezowania" zapisywana po kazdej zmianie, bez nazw zlecen).
- Opis, kontrakt dla okna i granice: `opisy_modulow/aplikacja.md`; liczby: `raporty/E3-A3a_2026-11-17.md`.

## Instalacja z paczki wydania (E3‑A11i, 20.11.2026 — wariant B)

Program trafia na stanowisko jako jeden plik `Stanowisko_<wersja>.zip` (ok. 430 MB: program, koła pip wszystkich pakietów dla Windows x64 i Pythona 3.12, instalator, sumy SHA‑256). Instrukcja na jedną stronę: `instrukcje/instalacja_i_aktualizacja.md`; opis mechanizmu, kroków i kodów wyjścia: `opisy_modulow/instalacja.md`.

```
py -3.12 narzedzia/zbuduj_wydanie.py --wyjscie C:\wydania --kola C:\wydania\kola        (budowa paczki z commita HEAD, bez internetu)
py -3.12 narzedzia/zbuduj_wydanie.py --pobierz-kola --kola C:\wydania\kola              (raz, z internetem: koła + listy zamrożone)
zainstaluj.cmd [/katalog C:\Stanowisko] [/python <python.exe>] [/skrot] [/testy] [/bez-pauzy]   (z rozpakowanej paczki: instalacja i aktualizacja)
C:\Stanowisko\Stanowisko.cmd [--atrapa] [--zamknij-po 5]                                (program — wersja bieżąca)
C:\Stanowisko\Samokontrola.cmd
C:\Stanowisko\Wroc_do_poprzedniej.cmd [/tak] [/przywroc-kopie] [/bez-pauzy]             (bez opcji pyta T / N)
C:\Stanowisko\Wersje.cmd [/usun <wersja>]
```

- **Raz, ręcznie:** Python 3.12 (64‑bit) z python.org — sprawdzona wersja to 3.12.10; inne 3.12.x instalator przyjmuje z wierszem ostrzeżenia w dzienniku, inne wersje (3.11, 3.13) odrzuca. Reszta bez internetu i bez zmian w systemie: każda wersja ma własny katalog `wersje\<wersja>\` z programem i własnym środowiskiem wirtualnym (pakiety tylko z kół paczki, w wersjach z `instalacja/zamrozone.txt`); `pytest` instaluje się tylko na żądanie (`/testy`).
- **Ustawienia i dane leżą poza katalogiem wersji:** `C:\Stanowisko\ustawienia.toml` (przy pierwszej instalacji ze wzoru, ze ścieżkami danych bezwzględnymi `C:/Stanowisko/dane/...`; przy aktualizacji nietknięty) i `C:\Stanowisko\dane\`. Pierwsza instalacja kończy się zwykle wierszem „INSTALACJA: WSTRZYMANA - uzupelnij ustawienia.toml i uruchom zainstaluj.cmd ponownie” (kod 10; to zamierzony etap, nie błąd): uzupełnij w pliku foldery pracy i osoby i uruchom `zainstaluj.cmd` jeszcze raz (kilka sekund, pakiety nie instalują się drugi raz) — samokontrola musi być zielona, zanim wersja stanie się bieżąca.
- **Aktualizacja:** rozpakuj nową paczkę i uruchom jej `zainstaluj.cmd`. Kolejność: sumy paczki → Python → nowy katalog wersji → sprawdzona kopia bazy (`dane\kopie\`; mechanizm kopii SQLite + `PRAGMA quick_check`, bez dobrej kopii wersja nie jest przełączana) → samokontrola → dopiero wtedy przełączenie wskaźnika `wersja_biezaca.txt`. Każdy błąd zostawia wersję bieżącą bez zmian i mówi, co zrobić.
- **Powrót:** `Wroc_do_poprzedniej.cmd` przełącza wskaźnik na poprzednią wersję; bez opcji pyta T / N i pokazuje, z jakiej wersji na jaką (`/tak` pomija pytanie — skrypty, test T12). Gdy nowsza wersja zmigrowała bazę, powrót zatrzymuje się z ostrzeżeniem (która kopia wróci — najnowsza sprawdzona — ile wpisów i od kiedy przepadnie) i wymaga `/przywroc-kopie`; bieżąca baza zostaje wtedy w `dane\kopie\` jako kopia „odłożona”, a przywrócenie to plik tymczasowy i jedna zamiana atomowa — plik bazy nie znika w żadnej chwili.
- Numer wersji `0.3.<n>`: plik `WERSJA` (albo `--wersja` przy budowie); każda opublikowana budowa dostaje nowy numer (suma do `../etap3/wydania/SHA256SUMS_wydania.txt`, potem zwiększ `WERSJA`). Katalog domyślny `C:\Stanowisko`, skrót na pulpicie tylko z `/skrot`; stare wersje i kopie bazy nie są kasowane automatycznie (`Wersje.cmd`); paczka nie jest odchudzana z zależności nieużywanych. Paczka jest powtarzalna bajtowo (ten sam commit + te same koła = ten sam SHA‑256); sumy zbudowanych wydań: `../etap3/wydania/`. Paczki ZIP i koła pip nie trafiają do repozytorium.
- **Znane ograniczenia** (szczegóły: `opisy_modulow/instalacja.md`, „Założenia i granice”): (a) do wydania 0.3.1 włącznie `stanowisko/dzien_skanera_rdzen.py` (sesje „Dnia skanera”) i `stanowisko/ui_test.py` (`decyzje.csv`) piszą do `dane/` w katalogu WERSJI — te dane nie przechodzą do nowej wersji; poprawione w E3‑O4 (21.11.2026): od następnego wydania oba piszą do `C:\Stanowisko\dane\`, a sesje i decyzje zapisane przez 0.3.1 zostają w `wersje\0.3.1\program\dane\` i nie są przenoszone automatycznie (skopiuj je ręcznie przed `Wersje.cmd /usun 0.3.1`); (b) przyszły klucz `[sciezki]` z domyślną ścieżką względną zatrzyma aktualizację (kod 7) do ręcznej edycji `ustawienia.toml`; (c) instalacji nie sprawdzono na laptopie firmowym (WDAC, antywirus, ostrzeżenie Windows przy uruchomieniu pliku `.cmd` z paczki pobranej z sieci).

## Laptop firmowy — instalacja i test skanera bez Excela i SharePointa

**Od 20.11.2026 program „Stanowisko” instaluje się z paczki wydania (sekcja wyżej) — kroki 1 i 2 poniżej opisują dawny sposób (kopia folderu + pip z internetu) i zostają dla pracy programisty oraz okna testu skanera.**

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
4. **Sprawdzenie**: `set PYTHONUTF8=1` i `py -3.12 -m pytest testy -q` (ok. 3 min; testy okna i inspect używają atrap; test na `dane/syntetyczne_P2` jest pomijany, gdy nie ma danych). **Aktualizacja istniejącej instalacji (program sprzed R59, własny `ustawienia.toml`):** wystarczy podmienić folder programu — brakujące układy `*_r54` program dopisuje sam przy wczytaniu ustawień (15.11.2026); pliku nie trzeba zmieniać.
5. **Okno**: dwuklik `uruchom_okno.bat` (albo `py -3.12 -m stanowisko.ui_test`). Wybrać skan (STL) i folder projektów. Płytki wybierać nie trzeba: pole „rozpoznaj automatycznie” jest zaznaczone i program sam rozpoznaje ze skanu, czy płytka jest wieczorna czy poranna, stara (R54) czy nowa (R59), kwadratowa czy okrągła — wynik podpisuje pod numerem płytki (ręczny wybór z listy: odznaczyć pole; przy złym wyborze okno powie „Płytka nie pasuje do wybranego układu” i podpowie właściwy). Współczynnik: „auto” = domyślny dla rozpoznanej płytki (wieczorna 1,225, poranna 1,0); wieczorem lepiej wpisać wartość z raportu MillBox, np. 1,22. Numer płytki: kwadrat — dołki kodu leżą poza polem ø100, wpisać (bez numeru mapa gniazd i tak jest poprawna); okrągła: 0 = z dołków. „Porównaj”. Mapa: zielone / czerwone / żółte / szare / pomarańczowe; klik w gniazdo → obraz odchyłek; „Podgląd 3D” otwiera Open3D; „Zapisz JSON/PNG”; „Ukruszona” / „OK” zapisuje decyzję do `dane/decyzje.csv`.
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
| `narzedzia/` | atrapy koron, rzut z góry, katalog projektów, metryki P2 i P3a, R59: liczniki strażnika układu i pojemność płytek; później kalibracja ramek; `zbuduj_wydanie.py` — paczka wydania (E3‑A11i) |
| `instalacja/` | instalator paczki wydania: `zainstaluj.cmd`, `instalator.py` (instalacja, aktualizacja, powrót), wzory skryptów uruchamiających, listy wersji zamrożonych (`zamrozone.txt`, `zamrozone_testy.txt`) |
| `instrukcje/` | instrukcje jednostronicowe dla ludzi (instalacja i aktualizacja; instrukcje technika — paczka A11d) |
| `WERSJA` | numer wersji programu (jeden wiersz) — nazwa paczki `Stanowisko_<wersja>.zip` i katalogu wersji |
| `testy/` | pytest, dane syntetyczne |
| `opisy_modulow/` | jeden plik na moduł: co robi, wejście, wyjście, kryterium „działa” — czytać przed zmianą kodu |
| `ustawienia.toml` | jedyny plik ustawień: ścieżki, progi, parametry (lokalny; wzór `ustawienia.przyklad.toml`) |
| `uruchom_okno.bat` | okno testowe jednym kliknięciem (`py -3.12 -m stanowisko.ui_test`) |
| `uruchom_stanowisko.bat` | program „Stanowisko” (etap 3) jednym kliknięciem (`py -3.12 -m stanowisko.aplikacja`): `aplikacja` (kontroler: scanner → silnik → session), `kontroler_api` (kontrakt dla okna, atrapa), `statusy` (tabela statusów i kolorów); pod spodem `scanner`, `silnik`, `session`, `baza` |
| `raporty/` | raporty z sesji naprawczych i testowych |
| `dane/` | lokalne: STL projektów, raporty MillBox, kopia Excela, skany syntetyczne, wyniki, `decyzje.csv` (poza repozytorium) |

## Układ współrzędnych

Plik układu płytki ma początek w środku **górnej** powierzchni płytki (x w prawo, y do tyłu). W STL płytki ta płaszczyzna leży na z = `thickness` z `uklad.json` (dziś 8 mm; `Gniazdo.z_top`), spód płytki na z = 0. Skany syntetyczne i wszystkie moduły pracują w układzie STL płytki; moduł plate ma sprowadzać prawdziwy skan do tego układu po trzech stożkach narożnych.
