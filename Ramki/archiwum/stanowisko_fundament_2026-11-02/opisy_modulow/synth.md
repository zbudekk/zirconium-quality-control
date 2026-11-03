# synth — generator sztucznych skanów

**Co robi.** Z projektów STL (prawdziwych lub atrap) buduje skan całej płytki: projekt × współczynnik skurczu, obrót brzegiem do góry, losowe ułożenie w gnieździe (obrót, przechył do 4°, przesunięcie, oparcie o stożek gniazda), ubytki brzegu (kula ø0,2–0,6 mm wycięta w górnym pasie 2 mm, głębokość 0,7 r), szum pomiarowy wzdłuż normalnych (σ 0,02–0,04 mm), opcjonalnie podwójna powierzchnia (drgnięcie: kopia 50% siatki przesunięta o 0,08–0,15 mm). Płytka: STL z `modele_plytek`, zagęszczona wokół znaczników i dołków kodu, bez spodu.

**Wejście.** Folder STL, nazwa płytki (`wieczorna`/`poranna`), numer płytki, seed, opcje (`Opcje`).

**Wyjście.** `skan_*.stl` (jedna siatka, ok. 1–1,5 mln trójkątów, 60–75 MB) + `skan_*.json` (`PrawdaPlytki`): dla każdej pracy gniazdo, plik projektu, współczynnik, transformacja 4×4 (projekt × współczynnik → układ skanu), lista ubytków (x, y, z, średnica, głębokość), drgnięcie; gniazda puste.

**Kryterium „działa”.** `pytest testy/test_synth.py` zielone: praca w gnieździe nie przebija stożka, ubytek leży pod pierwotną powierzchnią w pasie brzegu, szum ma zadane σ, transformacja z prawdy nakłada projekt na gniazdo, zapis/odczyt JSON zwraca to samo.

**Założenia i granice.**
- Orientacja brzegiem do góry z heurystyki (środek ciężkości powierzchni vs środek obrysu); na prawdziwych STL z exocad sprawdzić na 30 plikach i w razie potrzeby dodać opcję `--orientacja`.
- Brak symulacji przesłonięć (skaner widzi też to, czego nie widziałby z góry) i brak dziur w skanie spieczonej cyrkonii — do dodania, gdy inspect/match będą na to czułe (`--pokrycie`).
- Dwie prace w jednym gnieździe i praca poza gniazdem: jeszcze nie generowane (pole `poza_gniazdem` zarezerwowane).
- Mosty tylko w rynienkach, wzdłuż nich.

**Jak stroić.** Wszystkie zakresy w `Opcje` / parametrach CLI; prawdziwe skany z testu skanera zastąpią szum syntetyczny (zmierzyć σ na płaskiej części płytki i wpisać do `ustawienia.toml [synth]`).
