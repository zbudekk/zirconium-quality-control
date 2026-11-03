# Protokół weryfikacji v2 — sprawdzenia na wygenerowanych plikach

Obowiązuje wykonawcę (samokontrola, etap `--etap SPRAWDZ` skryptu) i recenzenta (niezależny skrypt). Każde sprawdzenie ma identyfikator K‑xx, metodę, wartość oczekiwaną, tolerancję i wagę. Wynik każdego K‑xx trafia do raportu jako `ZAL` / `NIE` / `N/D` (nie dotyczy etapu) z liczbą zmierzoną.

## 0. Zasady wspólne

1. **Pomiar, nie deklaracja.** Każda liczba w raporcie pochodzi z pliku z `wyniki_v2/` (STL, JSON, CSV, PNG), nie z kodu ani z parametrów. Recenzent nie czyta `ramka_generator.py` przed wykonaniem własnych pomiarów (czyta go dopiero przy analizie przyczyny błędu).
2. **Narzędzie:** Blender w trybie `-b` (ten sam, którego używa wykonawca; ścieżka w `00_PRZEPLYW_I_BRAMKI.md`), skrypt Pythona uruchamiany `blender -b -P <skrypt> -- <argumenty>`. Żadnych innych instalacji. Import STL: `bpy.ops.wm.stl_import` (Blender ≥ 4.0) lub `bpy.ops.import_mesh.stl` (starsze).
3. **Układ współrzędnych pomiaru.** STL są w orientacji do druku (Blender 5.2.3 LTS: `C:Program FilesBlender FoundationBlender 5.2blender.exe`) (największa płaska ściana na Z = 0). Sondy w tym protokole podano w **układzie montażowym** części (jak w planie, sekcja 4): płytka i pokrywka — środek górnej powierzchni płytki, Z w dół ujemne; korpus — układ globalny D3; blat — środek, wierzch blatu Z = 0, kołnierz w dół ujemny; wkładka — środek otworu, spód ramy Z = 0; tulejka DC — oś, kołnierz na Z = 0; podkładki panelu — oś, spód Z = 0 (rama dyfuzora i uchwyt kabli usunięte, R50‑U1/U8). Skrypt weryfikujący najpierw przekształca zaimportowany STL do układu montażowego (**transformacja jest zapisana w tabeli 1 i jest sama w sobie sprawdzeniem K‑02**: jeśli gabaryt po transformacji nie zgadza się z oczekiwanym, orientacja eksportu jest zła).
4. **Sonda „w bryle / poza bryłą”:** test punktu wewnątrz zamkniętej siatki metodą promienia (parzystość przecięć w 3 niezależnych kierunkach, np. +X, +Y, +Z; wynik = większość) albo `BVHTree.find_nearest` + znak iloczynu skalarnego z normalną. Punkt leży ≥ 0,1 mm od każdej ściany — sondy dobrano tak, by tak było.
5. **Tolerancje:** wymiar liniowy ±0,1 mm (chyba że podano inaczej); objętość ±0,01 cm³ między STL a arkuszem; gabaryt ±0,1.
6. **Waga:** **B** = blokujący (zły druk lub brak pliku: etap nie zaliczony), **P** = poważny (niespójność dokumentów, odstępstwo bez wpisu: etap nie zaliczony), **D** = drobny (kosmetyka: etap zaliczony z listą do v3).
7. **Kryterium zaliczenia etapu:** 0 × B i 0 × P w raporcie recenzenta; wszystkie K‑xx etapu wykonane (brak `N/D` tam, gdzie etap ich wymaga).

## 1. Tabela gabarytów i transformacji do układu montażowego

| Plik STL | Gabaryt oczekiwany X × Y × Z [mm] | Objętość orient. [cm³] (±30 %) | Orientacja w STL (druk) → układ montażowy | Etap |
|---|---|---|---|---|
| ramka_plytka_wieczorna_v2 (+ n1…n3) | 96 × 96 × 8 (n‑warianty: 96 × 96 × 8,6 z reliefem) | 62 | gniazdami w górę, spód na Z = 0 → przesunięcie Z −8 (wierzch na 0), środek XY na 0 | A |
| ramka_plytka_poranna_v2 (+ n4…n6) | 96 × 96 × 8 (n‑warianty: 8,6) | 61 | j.w. | A |
| ramka_pokrywka_v2 | 99,6 × 99,6 × 20,0 (bez reliefu i otworów, R50‑U14/U17) | 30 (wierzch 19,8 + kołnierz ~10,8) | wierzchem w dół (wierzch płaski na Z = 0) → obrót dokładnie 180° wokół osi X (y → −y, z → −z); w sondach: wierzch zewnętrzny Z = 0, kołnierz w dół do −20 | A |
| ramka_wkladka_v2 | 130 × 148,3 × 11,0 (uszy x ±51…65; kołek orientacyjny do Z 7,5 + kołki ustalające 3,5 pod spodem) | 16 | spodem w dół: STL leży na końcach kołków (Z = 0), spód ramy na Z = 3,5 → przesunięcie Z −3,5; środek XY = środek otworu (y_środka = y_min + 52,3; x_środka = środek obrysu ramy, nie uszu) | B |
| ~~ramka_rama_dyfuzora_v2~~ | **[usunięte R50‑U1]** — plik nie powstaje | — | — | — |
| ramka_blat_v2 | 200 × 200 × 14 (bez bossów ramy, R50‑U1) | 83 | wierzchem w dół (wierzch na Z = 0, kołnierz w górę do +14) → obrót DOKŁADNIE o 180° wokół osi X (y → −y, z → −z; NIE wokół Y) → wierzch Z = 0, kołnierz do −14; test rozpoznawczy: jeśli K‑47 nie przechodzi, a przechodzi po dodatkowym obrocie 180° wokół Z → zła oś eksportu (B wg K‑02), część nieodbita | B |
| ramka_korpus_W_v2, ramka_korpus_P_v2 | 200 × 200,6 × 59,6 (bez daszków R50‑U4; relief napisu +0,6 w −Y; R50‑1) | 225 | dnem w dół, Z = 0 = zewnętrzne dno; środek XY = środek obrysu ścian 200 × 200 (nie obrysu z reliefem) | B |
| ~~ramka_uchwyt_kabli_v2~~ | **[usunięte R50‑U8]** — plik nie powstaje | — | — | — |
| ramka_tulejka_dc_v2 | 15 × 15 × 3 (kołnierz ø15 × 1 + walec ø12 × 2, otwór ø8,2) | 0,30 | kołnierzem w dół, Z = 0; środek XY = oś | C |
| ramka_podkladka_panelu_05_v2 / _1_v2 / _2_v2 | 9 × 9 × 0,5 / 1 / 2 (otwór ø3,4) | 0,03 / 0,05 / 0,11 | płasko, Z = 0; środek XY = oś | C |

## 2. Sprawdzenia ogólne każdego STL (wykonać dla każdego z 17 plików: 8 płytek, pokrywka, wkładka, blat, 2 korpusy, tulejka, 3 podkładki)

| Id | Sprawdzenie | Metoda | Oczekiwane | Waga |
|---|---|---|---|---|
| K‑01 | Plik istnieje, importuje się, > 0 trójkątów, brak NaN | import, `len(mesh.polygons)` | > 100 | B |
| K‑02 | Gabaryt po transformacji do układu montażowego | bbox | tabela 1 ± 0,1 | B |
| K‑03 | Manifold | bmesh: krawędzie z ≠ 2 ścianami = 0; luźne wierzchołki = 0; `BVHTree.overlap(self, self)` po usunięciu sąsiadów = 0 | 0 / 0 / 0 | B |
| K‑04 | Jedna bryła, brak zamkniętych pustek | liczba spójnych składowych siatki (`mesh.calc_loop_triangles` + BFS po krawędziach) | 1 (wyjątek: żaden) | B |
| K‑04b | Objętość i orientacja normalnych | objętość ze wzoru dywergencji > 0; wartość w zakresie tabeli 1 ± 30 % | tak | B |

## 3. Płytki (etap A) — układ: środek wierzchu płytki, Z w dół ujemne

| Id | Sprawdzenie | Metoda / sondy | Oczekiwane | Waga |
|---|---|---|---|---|
| K‑05 | Układ gniazd w JSON: liczba, symetria, strefa, ścianki, narożniki | z `uklad_gniazd_*.json`: (a) liczba round/trough = wieczorna 24/2, poranna 35/2; (b) dla każdego rzędu (grupa po `y`) zbiór `x` symetryczny względem 0 (±0,01); (c) każdy obrys górny w [−45, 45]²; (d) żaden obrys nie wchodzi w kwadrat narożny (|x| > 35 ∧ |y| > 35); (e) min odległość między obrysami górnymi (okrąg–okrąg, okrąg–stadion, stadion–stadion) ≥ 3,0; (f) `d_bottom` = `d_top` − 2·4·tan 15° ± 0,01; (g) id = 1…N ciągłe, rzędami od przodu, w rzędzie malejące x | wszystkie | B |
| K‑06 | JSON ↔ STL: każde gniazdo istnieje w bryle | dla każdego round: sonda (x, y, −2) POZA; (x, y, −3,9) POZA (jest dno? nie — dno na −4, więc −3,9 jeszcze w gnieździe) ; (x, y, −6) POZA (otwór ø3 przelotowy); (x + 2,0, y, −6) W BRYLE (poza otworem r 1,5 — dno); (x + d/2 + 1,6, y, −2) W BRYLE (ścianka ≥ 3 → punkt 1,6 od krawędzi górnej jest w materiale) | wszystkie | B |
| K‑07 | Kąt stożka | dla 3 gniazd każdego rozmiaru: promień na Z = −2 z sond: (x + (d − 1,07)/2 − 0,15, y, −2) POZA, (x + (d − 1,07)/2 + 0,15, y, −2) W BRYLE | tak | B |
| K‑08 | Rynienki | dla każdej: (x, y, −2) POZA; (x ± (l/2 − 1), y, −2) POZA (końce); (x + l/2 − 0,5, y + w/2 − 0,5, −2) W BRYLE (zaokrąglony koniec: narożnik prostokąta jest materiałem); (x + l/2 + 1,6, y, −2) W BRYLE; otwory: (x + k·pitch, y, −6) POZA dla k = −1,5, −0,5, 0,5, 1,5; (x + 0,5·pitch + 2,5, y, −6)… nie — między otworami: (x, y, −6) → to środek rynienki, między otworami k = −0,5 i 0,5 → W BRYLE | tak | B |
| K‑09 | Znaczniki A, B, C | (±42, ±42 wg rogu, −1) POZA; (…, −3,3) W BRYLE; promień na −1: (x + 1,5, y, −1) POZA, (x + 2,7, y, −1) W BRYLE (stożek 2,5 → na 2/3 głębokości r ≈ 1,67; 2,7 to materiał) | tak | B |
| K‑10 | Wycięcie D | (45,5, −45,0, −4) POZA; (45,5, −45,0, −7,9) POZA (przelotowe); (41,5, −45,0, −4) W BRYLE; (45,5, −41,5, −4) W BRYLE | tak | B |
| K‑11 | Dołki kodu | bazowy: (−45,0, −36/−33/−30, −0,5) POZA, (−45,0, y, −1,3) W BRYLE; warianty n: dla bitu = 1 POZA, bitu = 0 W BRYLE na (−45,0, y, −0,5); n1: A; n2: B; n3: A+B; n4: C; n5: A+C; n6: B+C | tak | B |
| K‑12 | Kieszenie magnesów | dla A, B, C: (x, y, −7) POZA; (x, y, −5,6) W BRYLE (dno kieszeni na −5,8); (x + 2,45, y, −7) POZA (ø5,2); (x + 2,8, y, −7) W BRYLE; D: (42, −42, −7) W BRYLE | tak | B |
| K‑13 | Relief numeru | obszar x ∈ [36, 43], y ∈ [−48, −41]: max Z wierzchołków: bazowy = 0,00 ± 0,02; warianty = 0,60 ± 0,05; cyfra = n (recenzent: podgląd `render_plytki.png` i rzut XY siatki reliefu zapisany jako PNG przez skrypt weryfikujący) | tak | B |
| K‑14 | Rowek pokrywki | na 4 bokach: (47,5, 0, −2) POZA; (46,9, 0, −2) W BRYLE; (47,5, 0, −0,8) W BRYLE (nad rowkiem); (47,5, 0, −3,2) W BRYLE; w wycięciu D: brak materiału i tak (pomijane) | tak | B |
| K‑15 | Krawędzie: R 1 pionowe, faza 0,5 górna | (47,8, 47,8, −4) POZA (narożnik zaokrąglony); (47,9, 0, −0,05) POZA (faza); (47,9, 0, −1) W BRYLE | tak | D |
| K‑16 | Ścianki wokół cech narożnych ≥ 1,5 i gniazdo–dołek ≥ 3 (z JSON i parametrów: rachunek 4.11) | obliczenie odległości obrysów | ≥ 1,5 / ≥ 3,0 | B |

## 4. Pokrywka (etap A) — układ: wierzch zewnętrzny Z = 0, w dół ujemne, środek XY

| Id | Sprawdzenie | Sondy | Oczekiwane | Waga |
|---|---|---|---|---|
| K‑17 | Wierzch 2, wnęka 96,6 × 96,6 × 18 | (0, 0, −1) W; (0, 0, −2,5) POZA; (48,1, 0, −10) POZA; (48,5, 0, −10) W (kołnierz 48,3…49,8); (50, 0, −10) POZA; (0, 0, −19,9) POZA | tak | B |
| K‑18 | Garby zatrzaskowe ×4 (występ 0,7, szer. 10, wys. 0,8, środek 2 mm nad dolną krawędzią kołnierza → Z −18 = rowek płytki; położenia R42, R47) | (47,8, 0, −18) W; (47,8, 20, −18) POZA; (−47,8, 0, −18) W; (25, −47,8, −18) W (przód x = +25); (0, −47,8, −18) POZA (środek przodu = wycięcie palcowe); (−25, 47,8, −18) W (tył x = −25); (25, 47,8, −18) POZA; (47,8, 0, −16,5) POZA (nad garbem) | tak | B |
| K‑19 | (uchylone R50‑U17: pokrywka bez otworów) — kontrola odwrotna w K‑17: (15, 0, −1) W; (15, 30, −1) W; (−15, −30, −1) W | — | — | — |
| K‑20 | Wycięcia palcowe 30 × 3 na dolnej krawędzi przodu i tyłu | (0, −49, −19) POZA; (20, −49, −19) W; (0, 49, −19) POZA; (0, −49, −16) W | tak | P |
| K‑21 | (uchylone R50‑U14: pokrywka bez reliefu „GÓRA”) — kontrola odwrotna: mapa wysokości z góry w |x| ≤ 40, |y| ≤ 40: max = 0,00 ± 0,02 | — | — | — |
| K‑22 | Luz pokrywka–płytka = 0,3/stronę; kołnierz nie dotyka wkładki | wnęka z K‑17: (48,1 POZA, 48,5 W) → 96,6 ± 0,2; w złożeniu dół kołnierza Z 70,1 vs wierzch ramy wkładki 69,6 (R50‑1) → test przecięcia pokrywka–wkładka = 0 (K‑53; w etapie A część złożeniowa N/D) | tak | B |

## 5. Wkładka (etap B) — układ: środek otworu, spód ramy Z = 0

| Id | Sprawdzenie | Sondy | Oczekiwane | Waga |
|---|---|---|---|---|
| K‑23 | Rama 96,6 / 104,6 × 6, faza 1 na górze wewnątrz | (48,1, 0, 3) POZA; (48,5, 0, 3) W; (52,5, 0, 3) POZA; (48,5, 0, 5,9) POZA (faza 1 × 45° ścina narożnik 48,3…49,3 na Z 5…6 → punkt 48,5/5,9 jest ścięty); (49,5, 0, 5,9) W; (0, 0, 3) POZA | tak | B |
| K‑24 | Półki 12 × 12 × 2,5 w A, B, C, D (sondy poza kieszeniami Halla 39,5…44,5) | (−38, −38, 1,5) W; (−38, −38, 3) POZA; (38, 38, 1,5) W; (−38, 38, 1,5) W; (38, −38, 1,5) W (D bez kieszeni); (−30, −30, 1,5) POZA; (−35,5, −35,5, 1,5) POZA (półka kończy się na 36,3) | tak | B |
| K‑25 | Kieszenie Halla A, B, C przelotowe 5 × 5,5; kanał 2,5 × 1,0 pod półką; przelot w ściance 2,5 × 1,5 jako jedna bryła z rowkiem zewnętrznym (R50‑U9) | (−42, −42, 1,5) POZA; (−42, 42, 1,5) POZA; (42, 42, 1,5) POZA; (42, −42, 1,5) W (D bez kieszeni); kanał po przekątnej od (−42, −42) do narożnika (−48,3, −48,3): (−45, −45, 0,5) POZA; (−45, −45, 1,8) W; przelot w ściance 2,5 × 1,5 po przekątnej narożnika od (−48,3, −48,3) do (−52,3, −52,3) (R47): (−50, −50, 0,7) POZA; (−50, −50, 2,2) W; ciągłość do rowka: (−51,5, −51,5, 0,7) POZA | tak | B |
| K‑26 | (uchylone, Z28) | — | — | — |
| K‑27 | Kołek orientacyjny na półce D | (45,6, −45,6, 5) W; (45,6, −45,6, 8) POZA (szczyt 7,5); (45,6, −45,6, 7,2) W; luz 0,5 do ścian: (48,05, −45,6, 5) POZA | tak | B |
| K‑28 | Wycięcie palcowe 30 w przednim boku, pełna wysokość | (0, −50,3, 3) POZA; (0, −50,3, 0,3) POZA; (20, −50,3, 3) W; (−20, −50,3, 3) W | tak | B |
| K‑29 | Uszy 14 × 43,7 × 3 z nasadą x ±(44…65), y 48,8…58 (R47), kołki, otwory magnesów, kanał kablowy | (58, 80, 1,5) W; (58, 80, 4) POZA; (−58, 80, 1,5) W; nasada L (R51): (47, 55, 1,5) W; (47, 55, 3,5) POZA; (62, 55, 1,5) W (nasada na pasie tylnym); (62, 50, 1,5) POZA (prawy pas wolny — K‑56); (47, 59, 1,5) POZA (za nasadą, przed uchem x < 51); kanał pod nasadą: (56, 55, 0,5) POZA; (56, 55, 2) W; (48, 50,5, 0,5) POZA (kanał w dnie ścianki ramy do rowka); (58, 93,5, −2) W (kołek ø3 w dół); (58, 93,5, −3,8) POZA (kołek 3,5 → koniec na −3,5; faza 0,5); (58, 86, 1,5) POZA (otwór ø5,4); (58, 86 + 3, 1,5) W; (64, 70, 0,5) POZA (kanał 2 × 1,2 od spodu przy x = 64, y 52,3…90); (64, 70, 2) W; (64, 89, 0,5) POZA; ucho kończy się: (58, 95,5, 1,5) W; (58, 96,5, 1,5) POZA | tak | B |
| K‑30 | Rowek kablowy 2,5 szer. × 1,5 wys. (R50‑U9; x 49,8…52,3) na zewnętrznej dolnej krawędzi (lewy, tylny, prawy bok; NIE przedni) | (51,5, 0, 0,7) POZA; (50,2, 0, 0,7) POZA (rowek do 49,8); (49,4, 0, 0,7) W (ścianka 1,5 do otworu 48,3); (51,5, 0, 2,0) W (nad rowkiem 1,5); (−51,5, 0, 0,7) POZA; (0, 51,5, 0,7) POZA; (20, −51,5, 0,7) W (przód bez rowka; x = 20 poza wycięciem palcowym) | tak | P |
| K‑31 | Strzałki ▼ 2 × 3, relief 0,6, środki (±32, −51,15); bez napisu (R51) | mapa wysokości promieniami z góry w obszarach x ∈ [−34, −30] ∪ [30, 34], y ∈ [−52,3, −50,0]: max = 6,6 ± 0,05; w pasie y ∈ [−50,0, −48,3] max = 6,0 ± 0,05 (bez reliefu pod kołnierzem pokrywki); kształt z rzutu PNG | tak | P |
| K‑32 | Płytka we wkładce: luz 0,3/stronę i powtarzalność | otwór z K‑23 (48,1 POZA / 48,5 W) → 96,6 ± 0,2; w złożeniu przecięcie płytka–wkładka = 0 (K‑53; w etapie B część złożeniowa z brył zastępczych) | tak | B |

## 6. Korpus (etap B) — układ globalny D3 (środek obrysu ścian, zewnętrzne dno Z = 0)

| Id | Sprawdzenie | Sondy | Oczekiwane | Waga |
|---|---|---|---|---|
| K‑26 | (uchylone, Z28: brak przycisku) | — | — | — |
| K‑33 | (blat — sekcja 7; numer zarezerwowany) | — | — | — |
| K‑34 | Dno i ściany, promienie (R50‑1: korpus_h 59,6) | (0, 0, 1,5) W; (0, 0, 10) POZA; (98,75, 0, 20) W; (96, 0, 20) POZA; (0, 98,75, 20) W; (99, 99, 20) POZA (R 5); (0, 0, 59,5) POZA; (98,75, 0, 59,4) W; (98,75, 0, 59,7) POZA; R 3 dolna: (99,9, 0, 0,3) POZA | tak | B |
| K‑35 | Otwory w dnie: rowki wkrętów panelu 3,4 szer. po przekątnych od (±55, ±55) do (±65, ±65) bez pogłębień (R50‑2, R50‑U20), wloty 30 × 4 w (−8, ±10) (R50‑U19), brak szczeliny SD (R50‑U6) | rowki: (60, 60, 1,5) POZA; (55, 55, 1,5) POZA; (65, 65, 1,5) POZA; (−60, 60, 1,5) POZA; (−60, −60, 1,5) POZA; (60, −60, 1,5) POZA; (52, 52, 1,5) W (przed końcem rowka: 4,2 od (55, 55) > 1,7); (68, 68, 1,5) W; (58, 62, 1,5) W (2,8 od osi > 1,7); (63, 60, 0,5) W (brak pogłębienia: 2,1 od osi, Z 0,5 w dnie); SD: (−91, 0, 1,5) W; (−49, 0, 1,5) W (bez szczeliny); wloty: (−8, 10, 1,5) POZA (x −23…7, y 8…12); (−8, −10, 1,5) POZA; (−8, 13, 1,5) W; (−25, 10, 1,5) W; (−60, 10, 1,5) W (dawne miejsce wlotu) | tak | B |
| K‑36 | Podkładki‑stadiony panelu 9 × 1 (oś po przekątnej (±55, ±55)…(±65, ±65)), bossy Pi w (−46,5/11,5, ±24,5) ø8 × 5 z otworem ø2,1 (R50‑6, R49), brak bossów uchwytów (R50‑U8) | stadiony: (64, 60, 3,5) W (2,8 od osi: poza rowkiem 1,7, w stadionie 4,5); (64, 60, 4,5) POZA; (−64, 60, 3,5) W; (64, −60, 3,5) W; (−64, −60, 3,5) W; (53, 53, 3,5) W (koniec stadionu: 2,8 od (55, 55) < 4,5, poza rowkiem); (69, 69, 3,5) POZA (5,7 od (65, 65) > 4,5); (60, 60, 3,5) POZA (rowek przechodzi przez stadion); bossy Pi: (−43,5, −24,5, 6) W (r 3 z 4); (−46,5, −24,5, 6) POZA (otwór ø2,1); (−46,5, −24,5, 8,5) POZA; (14,5, 24,5, 6) W; (11,5, 24,5, 6) POZA; (−88,5, −24,5, 6) POZA (dawne miejsce bossa — powietrze); uchwyty: (23, 75, 6) POZA; (−17, 75, 6) POZA | tak | B |
| K‑37 | Szczeliny wentylacyjne 12 × 3 bez daszków: tył x −54, −18, 18, 54; boki y −36, 0, 36; Z 8 (R50‑U4, R50‑U19) | tył: (−54, 98,75, 8) POZA; (−54, 98,75, 6,2) W; (−54, 98,75, 9,8) W; (−36, 98,75, 8) W (między szczelinami); (−63, 98,75, 8) W (dawna pozycja — ściana); (−54, 101, 9,6) POZA (brak daszka); boki: (98,75, −36, 8) POZA; (−98,75, 36, 8) POZA; (98,75, 0, 8) POZA; (98,75, −45, 8) W (dawna pozycja — ściana); (101, 0, 9,6) POZA (brak daszka); przód: (0, −98,75, 8) W | tak | B |
| K‑38 | Kieszeń DC: okno 51 × 24 (x −93…−42, Z 14…38, naroża ostre), skrzynka x −97,5…−40, y 78…100, Z 12…40; gniazdo ø12 w prawej ścianie skrzynki (x −42…−40), oś (y 89, Z 30) wzdłuż X (R50‑3, R50‑4, R50‑U15) | wnętrze: (−60, 90, 26) POZA; (−85, 90, 26) POZA (dawna ściana −80 nie istnieje); (−79, 85, 26) POZA; okno: (−60, 99, 15) POZA; (−60, 99, 13) W; (−43, 99, 26) POZA; (−40,5, 99, 26) W; (−90, 99, 26) POZA; (−95, 99, 26) W (ściana między oknem a narożnikiem); naroże okna ostre: (−92,5, 99, 14,5) POZA; lewa ściana skrzynki = ściana korpusu: (−96, 85, 26) W; dno/sufit: (−60, 85, 13) W (dno Z 12…14); (−60, 85, 10) POZA; (−60, 85, 39) W (sufit 38…40); (−60, 85, 41) POZA; tylna ściana skrzynki (y 78…80) bez otworu: (−60, 79, 30) W; (−60, 77, 30) POZA (wnętrze obudowy); gniazdo w prawej ścianie: (−41, 89, 30) POZA (otwór ø12); (−41, 89, 37) W (ściana nad otworem: 36…40); (−41, 81,5, 30) W; (−41, 96,5, 30) W; (−41, 89, 23) W (pod otworem 24; ściana od 12); (−39, 89, 30) POZA (wnętrze obudowy za ścianą); (−43, 89, 30) POZA (wnętrze kieszeni) | tak | B |
| K‑39 | Okno USB 16 × 9 w (60, Z 24), rowki flanszy 3,2 × 5,7 (osie 60 ± 11,5…14, Z 24), wkręty blatu (±75, Z 55) (R50‑5, R50‑1) | okno: (60, 98,75, 24) POZA; (60, 98,75, 29,5) W (okno Z 19,5…28,5); (60, 98,75, 18,5) W; (67, 98,75, 24) POZA; (69, 98,75, 24) W (ścianka okno–rowek 68…69,9); (51, 98,75, 24) W (ścianka 50,1…52); rowki: (47, 98,75, 24) POZA (x 44,4…50,1); (73, 98,75, 24) POZA (x 69,9…75,6); (47, 98,75, 26,5) W (nad rowkiem Z 22,4…25,6); (43, 98,75, 24) W; wkręty blatu: (75, 98,75, 55) POZA; (−75, 98,75, 55) POZA; (75, 98,75, 52) W | tak | B |
| K‑40 | Przednia ścianka gładka (Z28): żadnych otworów poza reliefem napisu | (30, −98,75, 22) W; (−70, −98,75, 38) W; (−82, −98,75, 38) W; (−58, −98,75, 38) W; (0, −98,75, 20) W; (60, −98,75, 30) W; (−60, −98,75, 30) W; siatka promieni co 5 mm w X ∈ [−95, 95] × Z ∈ [5, 57]: promień wzdłuż +Y z y = −110 trafia w ścianę przy y ∈ [−100,6, −100,0] dla KAŻDEGO punktu (brak przelotu) | tak | B |
| K‑41 | (uchylone, Z28: brak głowicy) | — | — | — |
| K‑42 | Kieszenie zatrzasków 10 × 2,5 × 1,0 od wewnątrz, Z 52,6…55,1 (R50‑1); ścianka 1,5 zostaje | prawa: (98,0, 0, 53,8) POZA; (98,0, 4,5, 53,8) POZA; (98,0, 6, 53,8) W; (98,0, 0, 52) W; (98,0, 0, 55,6) W; (98,9, 0, 53,8) W (ścianka 98,5…100); lewa: (−98,0, 0, 53,8) POZA; przód: (50, −98,0, 53,8) POZA; (0, −98,0, 53,8) W; tył: (−50, 98,0, 53,8) POZA; (50, 98,0, 53,8) W; dawna wysokość: (98,0, 0, 48,8) W | tak | B |
| K‑43 | Napis W / P: relief 0,6, położenie (środek Z 51, R50‑1), różnica plików | min Y wierzchołków (lub promieniami) w obszarze x ∈ [−45, 45], Z ∈ [46, 56] = −100,6 ± 0,05 dla obu plików; obszar x ∈ [−45, 45], Z ∈ [35, 41] min Y = −100,0 (brak reliefu); SHA‑256 `korpus_W` ≠ `korpus_P`; różnica objętości W − P ≠ 0 i < 0,5 cm³; treść napisu: rzut siatki reliefu na XZ zapisany do PNG i obejrzany przez recenzenta | tak | B |
| K‑44 | Brak żeber (R50‑U5), brak gniazd stopek (R50‑U16), promień dolnej krawędzi (w K‑34) | (75, 75, 6) POZA (bez żebra); (70, 70, 6) POZA; stopki: (88, 88, 0,2) W (dno pełne, bez gniazda); (88, 88, 0,8) W | tak | P |
| K‑44b | Strefa Pi + Bonnet i wtyk DC Bonnetu (R50‑1, R50‑6) | w `.blend`: `proxy_pi_bonnet` (85 × 56 × 26 od Z 8, narożnik (−50, −28)) + `proxy_wtyk_bonnet` (40 × 10 × 11 w kierunku `bonnet_dc_dir` od `bonnet_dc_pos`, domyślnie −X od (−50, 22)): overlap z korpusem (ściany, stadiony, bossy, skrzynka DC) i `proxy_dystans_*` = 0, z `proxy_panel` (spód strefy złączy na Z 42) = 0; luz Z: 42 − 34 ≥ 8 (domyślne; po pomiarach ≥ 3); dodatkowo test 3 kierunków: wtyk 40 w −X, −Y i +Y od `bonnet_dc_pos` — każdy overlap = 0 | 0 / ≥ 8 | B |

## 7. Blat (etap B) — blat: środek, wierzch Z = 0, w dół ujemne (rama dyfuzora usunięta, R50‑U1)

| Id | Sprawdzenie | Sondy | Oczekiwane | Waga |
|---|---|---|---|---|
| K‑33 | Uszy wkładki leżą płasko; wkładka osadzona | w `.blend`: dolna płaszczyzna wkładki (ramy i uszu) na Z 63,6 ± 0,02 (min Z wierzchołków wkładki poza kołkami; R50‑1); dyfuzor wierzch = 63,6 ± 0,02 = wierzch blatu; przecięcie wkładka–blat = 0, wkładka–dyfuzor = 0; kołki wkładki wchodzą w otwory blatu: (±58, 93,5) w otworze (K‑47) | tak | B |
| K‑45 | Kieszeń dyfuzora 162 × 162 × 2, okno 158, naroża ostre (R50‑U15) | (80,5, 0, −1) POZA; (80,5, 0, −3) W; (81,5, 0, −1) W; (0, 0, −3) POZA; (78, 0, −3) POZA; (80,5, 80,5, −1) POZA (naroże ostre: 0,5 od obu ścian kieszeni); (81,5, 81,5, −1) W | tak | B |
| K‑46 | Kołnierz 194,0 × 2 × 10 (R48: 95,0…97,0), haczyki ×4 (występ 1,3 → 98,3, globalnie Z 52,85…54,85 → lokalnie −10,75…−8,75, R47, R50‑1), nacięcia 1 mm od dołu kołnierza do globalnie Z 58,6 (lokalnie −14…−5) | (96,0, 0, −9) W; (94, 0, −9) POZA; (97,8, 20, −9) POZA (poza haczykiem, za kołnierzem); (97,8, 0, −9,75) W (haczyk na prawej ścianie, y = 0); (97,8, 20, −9,75) POZA; (97,8, 0, −12,5) POZA (poniżej haczyka — nie wchodzi w ścianę korpusu); (0, −97,8, −9,75) POZA (przód: haczyk na x = +50); (50, −97,8, −9,75) W; (−50, 97,8, −9,75) W; (50, 97,8, −9,75) POZA; (−97,8, 0, −9,75) W; nacięcia: (96,0, 4,5, −9) POZA; (96,0, 7, −9) W; (96,0, 4,5, −4,5) W (nad nacięciem, nasada 1 mm) | tak | B |
| K‑47 | Słupki x ±71…79 (R48), y 89,2…95,2 (R47), otwór ø2,5 × 6 od lica 97,0 do 91,0 (R49a), oś globalnie Z 55 = lokalnie −8,6 (R50‑1); otwory kołków ślepe 3,8, kieszenie magnesów, szczeliny kabli, brak bossów ramy (R50‑U1), brak żebra | słupki: (75, 93, −8,6) POZA (w otworze ø2,5); (75, 89,6, −8,6) W (1,4 za dnem otworu, 0,4 przed czołem słupka 89,2); (75, 90,5, −8,6) W (0,5 za dnem otworu — obie sondy obowiązują); (75, 88, −8,6) POZA (powietrze przed słupkiem); (75, 93, −6) W; (75, 93, −12) W; (78, 92, −8,6) W (ścianka słupka 2,0 obok otworu); (70, 96,0, −9) W (kołnierz poza słupkiem); kołki: (58, 93,5, −2) POZA; grubość dna otworu promieniem: z góry pierwsze trafienie Z −3,8 ± 0,05, z dołu −4,0 ± 0,05 (zamiast sondy parzystości); (58, 93,5, −4,2) POZA (pod blatem powietrze); magnesy: (58, 86, −1) POZA; (58, 86, −3) W; szczeliny: (66, 90, −2) POZA; (66, 90, −3,95) POZA (przelot); (66, 90, −4,3) POZA; brak bossów: (90, 90, −6) POZA; (92,5, 90, −6) POZA; (90, 90, −3) W (płyta); (84, 0, −7) POZA (bez żebra, R41) | tak | B |
| K‑48 | (uchylone R50‑U1: rama dyfuzora usunięta) | — | — | — |
| K‑49 | Pasowania blat–korpus, dyfuzor–kieszeń, panel–okno, dystanse–rowki | kołnierz 194,0 vs wnętrze korpusu 195 → 0,5/stronę (R48; z K‑46 i K‑34); dyfuzor 160 vs kieszeń 162 → 1,0; w `.blend`: blat–korpus = 0; `proxy_panel` PCB (Z 54…55,6) vs spód blatu 59,6 → 4,0 ≥ 2; PCB 160 pod oknem 158 (nakładka 1/stronę); `proxy_dystans_*` ø6,4 × 50 w (±`panel_hole_pitch`/2 + offset) stoją na stadionach (Z 4…54) i leżą w rowkach (K‑53 para dystans–korpus = 0); `proxy_panel`–blat = 0 | tak | B |

## 8. Małe części (etap C)

| Id | Sprawdzenie | Sondy / metoda | Oczekiwane | Waga |
|---|---|---|---|---|
| K‑50 | (uchylone, Z28: brak głowicy) | — | — | — |
| K‑51 | (uchylone, Z28: brak zaślepki) | — | — | — |
| K‑52 | (uchylone R50‑U8: uchwyt kabli usunięty) | — | — | — |
| K‑52b | Tulejka DC (R50‑3): kołnierz ø15 × 1, walec ø12 × 2, otwór ø8,2 | układ: kołnierzem w dół, Z = 0, środek = oś: (0, 0, 1,5) POZA (otwór); (3,5, 0, 1,5) POZA (otwór r 4,1); (4,8, 0, 1,5) W; (5,5, 0, 2) W (walec r 6); (6,8, 0, 2) POZA (poza walcem, nad kołnierzem); (6,8, 0, 0,5) W (kołnierz r 7,5); (8, 0, 0,5) POZA; gabaryt 15 × 15 × 3 ± 0,1 | tak | P |
| K‑52c | Podkładki panelu (R50‑8): ø9, otwór ø3,4, t = 0,5 / 1 / 2 | układ: płasko, Z = 0: (0, 0, t/2) POZA; (1,5, 0, t/2) POZA (otwór r 1,7); (3, 0, t/2) W; (4,7, 0, t/2) POZA; gabaryt 9 × 9 × t ± 0,05 | tak | P |

## 9. Złożenie w `.blend` (etap C, ale K‑44/K‑33 już w B)

| Id | Sprawdzenie | Metoda | Oczekiwane | Waga |
|---|---|---|---|---|
| K‑53 | Brak przenikań między wszystkimi parami części i brył zastępczych ZESTAWU ZŁOŻONEGO (R47, R50: korpus_W, blat, wkladka, plytka_wieczorna_n1, pokrywka, tulejka_dc (w otworze prawej ściany skrzynki, z `proxy_gniazdo_dc` ø8 w tulejce) + wszystkie `proxy_*`; części wariantowe — korpus_P, pozostałe płytki, 3 podkładki panelu (przy domyślnych wymiarach nieużywane) — leżą w `.blend` odsunięte ≥ 250 mm i NIE wchodzą do testu) | dla każdej pary obiektów zestawu złożonego: `BVHTree.FromObject` na kopiach z wierzchołkami przesuniętymi o −0,05 mm wzdłuż normalnych → `overlap` = 0; raport z listą par i liczbą przecięć; pary stykowe (dystanse–stadiony na Z 4, panel–dystanse na 54, wkładka–dyfuzor na 63,6, płytka–półki na 66,1, tulejka–ściana skrzynki, gniazdo DC–tulejka) muszą dać 0 | 0 dla każdej pary | B |
| K‑54 | Łańcuch wysokości z siatek (pomiar promieniem z góry w punkcie poza reliefami i kołkami; R47, R50‑1) | blat (90, 0) → 63,6; dyfuzor (0, 70) → 63,6; rama wkładki (0, 50,3) → 69,6 (poza kołkiem na półce D, którego szczyt = 71,1); płytka n1 (0, −46,5) → 74,1 (płaski pas między rzędem R1 a fazą; relief cyfry → 74,7 w (39,5, −44,5)); pokrywka (40, 40) → 90,1 (bez reliefu); min Z pokrywki 70,1; max Z `proxy_pi_bonnet` 34; min Z `proxy_panel` (strefa złączy) 42; PCB panelu 54…55,6; szczyt dystansów 54; stadiony 3…4; stopki (bryły zastępcze) −4…0; korpus wierzch 59,6 | ± 0,05 | B |
| K‑55 | Magnes–czujnik | z siatek: spód magnesu (bryła zastępcza w kieszeni A płytki n1) − wierzch bryły zastępczej czujnika Halla (1,5 nad dyfuzorem) = 1,2 ± 0,05; + 0,5 = 1,7 ≤ 4 | 1,2 | B |
| K‑56 | Margines matrycy | odsłonięty pas dyfuzora od frontu i z prawej: od krawędzi ramy wkładki (y = −52,3 / x = 52,3) do krawędzi panelu (80) = 27,7 → ⌊27,7 / 2,5⌋ = 11 pełnych pikseli; żadna inna część (uszy, blat) nie leży nad pasem przednim ani prawym nad panelem | 27,7 / 11 | B |

## 10. Dokumenty, spójność, powtarzalność (etap C)

| Id | Sprawdzenie | Metoda | Oczekiwane | Waga |
|---|---|---|---|---|
| K‑57 | Arkusz zamówienia ↔ STL (R50) | dla każdego wiersza CSV: plik istnieje; objętość z własnego pomiaru = CSV ± 0,01 cm³; gabaryt = STL ± 0,1; ilości = `parametry.json → quantities`; materiał = `materials` **per część** (nie „wszystko PA12”); koszt liczony tylko dla pozycji z materiałem zaczynającym się od „PA12 drukarnia”: koszt_min = obj × szt × `cost_rate_min`, koszt_max = obj × szt × `cost_rate_max` × (`cost_dye_factor` dla grafitu) × (`cost_smooth_factor` dla korpusu/blatu w wariancie pokazowym) → przeliczyć według wzoru zapisanego pod tabelą arkusza; pozycje druku własnego (pokrywka, tulejka, podkładki) z objętością i gabarytem, bez kosztu, w osobnym bloku; sumy tylko dla drukarni; brak wierszy bazowych płytek; dokładnie 15 wierszy (10 drukarnia + 5 własne); obecność uwagi STEP/FreeCAD | wszystko | P |
| K‑58 (etap A) | `kody_plytek.md` ↔ warianty STL ↔ JSON | tabela n → magnesy → dołki zgodna z K‑11 i D11; instrukcja bieguna obecna (słowa „biegun”, „S”, „jednakowy”) | tak | P |
| K‑59 | Powtarzalność | recenzent uruchamia polecenie z `README.md` w czystej kopii folderu (`wyniki_v2` usunięty) → wszystkie pliki powstają; SHA‑256 każdego STL = SHA z raportu wykonawcy (jeśli różne: objętość ± 0,001 cm³ i gabaryt ± 0,01 — wtedy ZAL z uwagą D) | tak | B |
| K‑60 | Rendery i raport | 3 PNG istnieją, ≥ 1600 × 1200; na renderze rozstrzelonym widać i podpisano wszystkie części z 12.1 (lista kontrolna recenzenta); raport wykonawcy ma wszystkie K‑xx etapu z wartościami; `arkusz_wymiarow.md` ma pełny zrzut `parametry.json`; `parametry.json` wartości `LICZONE` zgodne ze wzorami (przeliczyć: korpus_h 59,6, blat_top_z 63,6, panel_pcb_z 54, panel_standoff_l 50, cover_inner_h 14, snap_pocket_z 52,6, snap_hook_z 52,85, blat_screw_z 55, label_pos_z 51) | tak | P |

## 11. Lista kontrolna renderu rozstrzelonego (K‑60)
Na obrazie muszą być widoczne i podpisane: korpus (W), blat, dyfuzor (zastępczy), panel (zastępczy), Pi + Bonnet (zastępczy) z wtykiem DC (zastępczy, 40 w −X), 4 dystanse (zastępcze, 50) na stadionach, wkładka, płytka wieczorna n1, pokrywka, gniazdo DC (zastępcze) w prawej ścianie skrzynki kieszeni, tulejka DC (obok, opcjonalna), gniazdo USB (zastępcze). Rama dyfuzora i uchwyty kabli nie istnieją (R50‑U1, R50‑U8). Przednia ścianka gładka z napisem (Z28). Kolory: grafit/biały/pleksi/PCB/mosiądz jak w R27 (`color_*`).

## 12. Uwagi do sond z poprawkami
W tabelach kilka sond ma dopisek „poprawka” — obowiązuje wartość po słowie „poprawka”; wartość przed nim jest pozostawiona celowo, by pokazać tok rozumowania (recenzent może usunąć te zapisy w swoim skrypcie). Każda sonda, która w praktyce wypadnie bliżej niż 0,1 mm od ściany (wynik niestabilny w 3 kierunkach), ma być przesunięta o 0,1 mm w głąb oczekiwanego obszaru i tak zapisana w raporcie.
