# Raport recenzenta — etap A, iteracja 1

Plik: `recenzja/raport_recenzenta_A_iter1.md`. Pomiary własnym skryptem `recenzja/sprawdz_A.py` (uruchomienie: `"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b -P recenzja/sprawdz_A.py -- --iter 1`), wyniki w `recenzja/wyniki_A_iter1.json` (1943 sondy, 136 sprawdzeń), log `recenzja/log_A_iter1.txt`, rzuty reliefów `recenzja/relief_*.png`.

## 0. Werdykt
**ETAP A: ZALICZONY** — B = 0, P = 0, D = 0 (liczba sprawdzeń NIE w każdej wadze). Wszystkie K‑xx etapu A wykonane (K‑22 część złożeniowa N/D zgodnie z protokołem — należy do K‑53, etap C).
Warunek bramki G2: decyzja właściciela w sprawie odstępstwa #2 wykonawcy (`cover_snap_r` 0,4 zamiast 0,5 — sekcja 5). Zatwierdzenie = brak zmian w plikach; odrzucenie = nowa iteracja pokrywki.

## 1. Niezależność pomiaru
- Sumy SHA‑256 sprawdzanych plików zgodne z raportem wykonawcy (sekcja 2): **TAK** — 9 STL, 2 JSON, `kody_plytek.md`: 12/12 zgodnych, rozmiary plików zgodne.
- Skrypt recenzenta napisany bez czytania `ramka_generator.py`: **TAK** (kodu wykonawcy nie otwierano w ogóle — żadne sprawdzenie nie wypadło NIE).
- Powtarzalność (K‑59): nie dotyczy etapu A.
- Metoda sond: parzystość przecięć promienia w 3 kierunkach (≈+X, ≈+Y, ≈+Z, odchylone o ~0,1°), wynik większościowy + kontrola `find_nearest`; sond niestabilnych: **0 / 1943**; najmniejsza odległość sondy od ściany 0,10 mm (K‑15, sonda (47,9, 0, −1) — zgodnie z protokołem). Reliefy: mapa wysokości promieniami z góry, siatka 0,1 mm, zapis PNG własnym koderem.
- Transformacja do układu montażowego: płytki — przesunięcie (−cx, −cy, −(z_min + 8)); pokrywka — obrót 180° wokół X i przesunięcie tak, by płaski wierzch (promień w (±40, ±40)) był na Z = 0 (zmierzony wierzch płaski po obrocie: −0,600 → relief 0,6 ✓). Surowe STL: płytki X,Y ∈ [−48, 48], Z ∈ [0, 8 | 8,6]; pokrywka X,Y ∈ [−49,8, 49,8], Z ∈ [0, 20,6] — zgodne z tabelą 1.

## 2. Wyniki sprawdzeń
| Id | Wynik | Zmierzone przez recenzenta | Zadeklarowane przez wykonawcę | Oczekiwane | Waga | Uwaga |
|---|---|---|---|---|---|---|
| K‑01 | ZAL | trójkąty: wieczorna 21992 / n1 21956 / n2 22136 / n3 22338; poranna 25866 / n4 25896 / n5 26272 / n6 26128; pokrywka 3988; NaN: brak | identycznie | > 100 | B | |
| K‑02 | ZAL | płytki bazowe 96,000 × 96,000 × 8,000; n1…n6 96,000 × 96,000 × 8,600; pokrywka 99,600 × 99,600 × 20,600; bbox montażowy płytek Z −8…0 (n: …0,6), pokrywki Z −20…+0,6 | identycznie | tabela 1 ± 0,1 | B | |
| K‑03 | ZAL | 9 × (0 krawędzi niemanifold / 0 luźnych / 0 samoprzecięć) po zszyciu wierzchołków STL (1e‑5) | 0/0/0 | 0/0/0 | B | |
| K‑04 | ZAL | 9 × 1 składowa | 1 | 1 | B | |
| K‑04b | ZAL | wieczorna 57,941 / n1 57,952 / n2 57,953 / n3 57,950; poranna 60,222 / n4 60,234 / n5 60,232 / n6 60,231; pokrywka 29,943 cm³ (normalne na zewnątrz) | 57,94…57,95 / 60,22…60,23 / 29,94 | 62 / 61 / 30 ± 30 % | B | pokrywka wg poprawionej tabeli 1 (30 cm³, komunikat właściciela) |
| K‑05 | ZAL | wieczorna 24/2, poranna 35/2; wszystkie rzędy symetryczne; obrysy w [−45, 45]²; narożniki wolne; min ścianka 3,000 (para 1–2) w obu; d_bottom zgodne ± 0,01; id 1…26 / 1…37 rzędami od przodu, malejące x | identycznie | (a)–(g) | B | |
| K‑06 | ZAL | wieczorna 120/120 sond (×4 pliki), poranna 175/175 (×4 pliki) | identycznie | wszystkie | B | |
| K‑07 | ZAL | 18/18 w każdym z 8 plików; promień na Z −2 = d/2 − 0,536 | 18/18 | tak | B | |
| K‑08 | ZAL | 20/20 w każdym z 8 plików | 20/20 | tak | B | |
| K‑09 | ZAL | 12/12 ×8 | 12/12 | tak | B | |
| K‑10 | ZAL | 4/4 ×8 (wycięcie D w x 43…48, y −48…−43, przelotowe) | 4/4 | tak | B | |
| K‑11 | ZAL | baza 6/6 (A+B+C); n1 A, n2 B, n3 A+B, n4 C, n5 A+C, n6 B+C — dołki obecne dokładnie dla bitów = 1, brak dla bitów = 0; x = −45,0 | identycznie | D11 | B | |
| K‑12 | ZAL | 13/13 ×8 (kieszenie A, B, C ø5,2 dno −5,8; D pełny) | 13/13 | tak | B | |
| K‑13 | ZAL | max Z: bazowe 0,000 / 0,000; n1…n6 0,600 (wszystkie); środki reliefu (39,4…39,6, −44,5…−44,9); cyfry odczytane z PNG: n1 „1”, n2 „2”, n3 „3”, n4 „4”, n5 „5”, n6 „6”; rzut narożnika D: cyfra między gniazdami a wycięciem, wycięcie przód‑prawe | max Z 0,000 / 0,600 | 0 ± 0,02 / 0,6 ± 0,05; cyfra = n | B | |
| K‑14 | ZAL | 16/16 ×8 (rowek na 4 bokach: 47,5 POZA, 46,9 W, nad/pod rowkiem W) | 16/16 | tak | B | |
| K‑15 | ZAL | 3/3 ×8 | 3/3 | tak | D | sonda (47,9, 0, −1) dokładnie 0,10 od ściany, stabilna |
| K‑16 | ZAL | gniazdo–dołek min 3,62 (wieczorna, id 13–C) / 3,53 (poranna, id 14–C); gniazdo–cecha narożna min 1,52 (wieczorna id 1 – obszar reliefu numeru) / 3,53 (poranna); dołek–krawędź 2,00; dołek A–znacznik A 3,21; dołek–rowek pokrywki 1,30 | 3,62 / 3,53; 2,00; 3,21; 1,30 | ≥ 3,0 / ≥ 1,5 | B | 1,30 < 1,5 przyjęte w R47(10) → D do v3 (sekcja 6) |
| K‑17 | ZAL | 6/6 | 6/6 | tak | B | |
| K‑18 | ZAL | 8/8 (garby na Z −18: boki y = 0, przód x = +25, tył x = −25; nad garbem POZA) | 8/8 | tak | B | |
| K‑19 | ZAL | 10/10 (4 z protokołu + wszystkie 6 otworów (±15, −30/0/30) POZA) | 4/4 | tak | P | |
| K‑20 | ZAL | 4/4 | 4/4 | tak | P | |
| K‑21 | ZAL | max Z 0,600, min 0,000 w |x| ≤ 12, |y| ≤ 4; treść z PNG: „GÓRA” (z kreską nad Ó) | 0,600 | 0,6 ± 0,05 | D | |
| K‑22 | ZAL | sondy 48,1 POZA / 48,5 W na 4 bokach: 8/8; wnęka z promieni: X 96,600, Y 96,600; część złożeniowa N/D (K‑53, etap C) | 96,6 ± 0,2 | 96,6 ± 0,2 | B | |
| K‑58 | ZAL | tabela n → typ → magnesy → dołki: 6 wierszy zgodne z D11/K‑11, nazwy plików zgodne; instrukcja bieguna: „biegun”, „S”, „jednakowy” obecne; x dołków −45 | identycznie | tak | P | |

## 3. Uwagi do poprawy (tylko NIE), z numerami
| Nr uwagi | K‑xx | Waga | Plik / cecha | Co jest | Co ma być |
|---|---|---|---|---|---|
| — | — | — | brak sprawdzeń NIE | — | — |

## 4. Rozbieżności między raportem wykonawcy a pomiarem recenzenta
Brak. Wszystkie liczby z sekcji 3 raportu wykonawcy (liczby trójkątów, gabaryty, objętości do 0,01 cm³, liczby sond, max Z reliefów, min ścianki, rachunki K‑16) są identyczne z moim pomiarem.
Uwaga procesowa (nie rozbieżność): wykonawca w K‑04b zmienił wynik pokrywki z NIE na ZAL ręcznie w raporcie po poprawie tabeli 1 przez właściciela, i napisał to wprost. Raport jest deklarowany jako „[cytat usuniety]”; proszę, by w kolejnych etapach taka zmiana była wynikiem ponownego przebiegu `--etap SPRAWDZ`, nie edycji.

## 5. Ocena rejestru odstępstw wykonawcy
| # odstępstwa | Zasadne? | Wymaga decyzji właściciela? | Komentarz |
|---|---|---|---|
| 1 (`code_dimple_x` −45,0 zamiast −45,5 z tabeli 3.1 planu) | TAK | NIE (uwaga do planu) | `parametry.json`, D11, 4.1, 4.11, R47(10) i protokół mają −45,0; tylko tabela 3.1 planu (wiersz `code_dimple_x`) została przy −45,5. Wykonawca postąpił zgodnie z R1/R14. **Uwaga do planu:** poprawić tabelę 3.1 na −45,0. |
| 2 (`cover_snap_r` 0,4 zamiast 0,5) | TAK (geometrycznie wymuszone: garb 0,8 wysoki nie mieści dwóch zaokrągleń R 0,5; czubek = półokrąg R 0,4) | **TAK** — zmienia wartość z planu v2 bez decyzji właściciela | Proponuję zatwierdzić i wpisać `cover_snap_r` 0,4 do `parametry.json` i tabeli 3.1 (albo zdefiniować „[cytat usuniety]”). Sondy K‑18 (występ 0,7 na Z −18, brak materiału na −16,5) przechodzą; zmiana nie wpływa na pasowanie garb–rowek (0,7 w 0,8). Jeśli właściciel odrzuci — pokrywka do ponownego wygenerowania (iteracja 2). |
| 3 (objętość pokrywki 22 → 30 w tabeli 1) | TAK | rozstrzygnięte przez właściciela (komunikat R‑1) | Rachunek wykonawcy 30,4 cm³ i mój pomiar 29,94 cm³ potwierdzają; sekcja 11 planu (koszt pokrywki 22 cm³ × 4) do poprawy przy okazji — uwaga do planu, bez wpływu na pliki. |

## 6. Lista drobnych (D) do v3
1. Dołek kodu a rowek pokrywki: 1,3 mm materiału po przekątnej (< 1,5 z zasady 4.8), lokalnie, przyjęte w R47(10). Do rozważenia w v3: dołki na x = −44,5 (wtedy 1,7) albo rowek pokrywki przerwany na odcinku y −38…−28 lewego boku.
2. Dołek–dołek: 1,0 mm ścianki między dołkami ø2 w rozstawie 3 (głębokość 1 mm, informacyjnie — bez wpływu na odczyt skanera).
3. Dokumentacja: tabela 3.1 planu (`code_dimple_x` −45,5) i sekcja 11 (objętość pokrywki 22) niezgodne z resztą planu — do poprawy przez sesję 1.

## 7. Sprawdzenia dodatkowe (poza protokołem)
- Rzut całego narożnika D (`recenzja/relief_*_naroznik.png`): cyfra leży między gniazdami rzędu R1 a wycięciem, wycięcie w narożniku przód‑prawym (+x, −y), brak lustrzanego odbicia.
- K‑19 rozszerzone na wszystkie 6 otworów ø4 — wszystkie przelotowe.
- Pokrywka: wnęka zmierzona promieniem poziomym na Z −10 w obu osiach: 96,600 / 96,600.
