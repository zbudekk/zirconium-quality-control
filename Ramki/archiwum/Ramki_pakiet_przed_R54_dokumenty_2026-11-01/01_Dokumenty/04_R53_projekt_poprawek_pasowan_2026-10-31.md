# R53 — poprawki pasowań pod tolerancje MJF/SLS (projekt, 31.10.2026)

Sesja „POPRAWKI PASOWAŃ”. Zakres: wyłącznie luzy i tolerancje (bez przeprojektowania: zatrzaski, wkręty tylne, osobny blat, tulejka zostają). Źródła: `sesje_2026-10-31/design_a_korpus/znaleziska.md` 1.2 (T1–T16), `wykonalnosc/znaleziska.md` W‑04, `design_b_plytki/znaleziska.md` §3.3, `kod_b_generator/znaleziska.md` (G‑02, G‑04/05, S‑06…S‑09, S‑02). Kopia zapasowa przed zmianami: `archiwum/wyniki_v2_przed_R53_2026-10-31/`, `archiwum/parametry_przed_R53_2026-10-31.json`, SHA w `archiwum/sha256_stl_przed_R53.txt`.

## 1. Założenia tolerancji (do rachunku „najgorszy przypadek”)

- MJF/SLS PA12 (drukarnia): **±0,3 mm** w XY na każdej części (drukarnie: ±0,3 % z dolnym limitem ±0,3; na 200 mm realnie do ±0,6, ale obie ramki idą do jednej drukarni, więc wymiary globalne korpusu i blatu skalują się razem; lokalnie liczymy ±0,3). W Z: ±0,3 dla cech odległych od siebie o kilka mm w tej samej części przyjmujemy ±0,2 (ten sam wydruk, ta sama warstwa), łącznie dwie części → 0,4–0,6.
- Otwory i rowki w MJF wychodzą **mniejsze o 0,1–0,2** (proszek, piaskowanie).
- Żywica (druk własny: tulejka, podkładki): ±0,05. FDM PETG (pokrywka): ±0,5 % / min ±0,5, z kalibracją skali na pierwszej sztuce.
- Zasada R53: **luz nominalny ≥ suma tolerancji obu części w danym kierunku**, chyba że pasowanie jest celowo wciskowe (wtedy zapisane jawnie).

## 2. Tabela R53 — decyzje

| # | Klucz `parametry.json` | Stara | Nowa | Uzasadnienie (funkcja + rachunek) | Dotyka (K‑xx / sondy / pasowania) |
|---|---|---|---|---|---|
| T1 | `blat_skirt_clearance` | 0,5 | **0,7** | Kołnierz blatu 193,6 w 195 (0,7/stronę). Tolerancja: ±0,3 (korpus) + ±0,3 (blat) = 0,6 ≤ 0,7; zapas 0,1 na wypaczenie ścian 200 mm do wewnątrz. Centrowanie blatu przejmują haczyki (luz boczny T3c), nie kołnierz. Pochodne: lico kołnierza 96,8 (94,8…96,8), R kołnierza 4,3; dno otworu słupka 96,8 − 6 = 90,8 → dno słupka 1,6 ≥ 1,5 (było 1,8); gwint wkrętu M3 × 8 w słupku 4,8 (było 5,0). | K‑46 (opis), K‑47 (opis: lico 96,8, dno 90,8), K‑49 (0,7/stronę), pasowanie „kołnierz blatu – ściana korpusu”, trzecie oko 1d |
| T2a | `snap_hook_h` | 1,3 | **1,5** | Czubek haczyka zostaje na 98,3 (96,8 + 1,5) → zahaczenie 0,8 w ścianie 97,5 utrzymane mimo większego luzu kołnierza. Ugięcie montażowe ramienia = zahaczenie 0,8 (najgorzej 1,4; ramię 9 × 1,5 PA12 — jak w R48). | K‑46 (sondy bez zmian: czubek 98,3), pasowanie „zahaczenie” |
| T2b | `snap_pocket_depth` | 1,0 | **1,3** | Dno kieszeni 98,8 → luz czubek–dno 0,5 (było 0,2). Najgorszy przypadek (±0,3 + ±0,3 w X) daje −0,1, co przejmuje sprężyste ramię (ugina się 0,8 przy montażu) — haczyk nie podnosi blatu. **Odstępstwo od zasady 4.8 „ścianka ≥ 1,5”: ściana za kieszenią 2,5 − 1,3 = 1,2 mm lokalnie** (4 pola 11 × 3,5 mm, nienośne; MJF drukuje ścianki od 0,6; przednia ściana ma dodatkowo relief napisu +0,6 od zewnątrz). Alternatywa odrzucona: zmniejszenie `snap_hook_h` do 1,1 (zahaczenie 0,4 — za mało). | K‑42 (sonda 98,9 → 99,2: ścianka 98,8…100), pasowanie „luz do dna kieszeni” 0,5, trzecie oko (ścianka „za kieszenią zatrzasku” 1,2 — min_req obniżone do 1,2 z adnotacją R53) |
| T3a | `snap_pocket_h` | 2,5 | **3,5** | Luz Z haczyka w kieszeni 0,25/0,25 → **0,75 pod i 0,75 nad** występem (≥ 0,6 = ±0,3 korpus + ±0,3 blat). Przy −0,1 w starym stanie rampa haczyka siadała na dolnej krawędzi kieszeni → szczelina blat–korpus na całym obwodzie; teraz zapas 0,75 (do rampy w płaszczyźnie ściany: 1,2). Luz pionowy blatu do góry 0,75 (blat trzymają 2 wkręty z tyłu + ciężar). | K‑42 (sondy Z: 52 → 51,6; 55,6 → 56,1), K‑60 (LICZONE), pasowanie „luz nad występem (z)” 0,75, trzecie oko (hz0/pz0) |
| T3b | `snap_pocket_z` (LICZONE) | `korpus_h − 7` = 52,6 | **`korpus_h − 7,5` = 52,1** | Kieszeń rozszerzona symetrycznie: Z 52,1…55,6 (występ 52,85…54,85 bez zmian). Nad kieszenią zostaje 4,0 ściany do wierzchu 59,6; wkręty blatu (±75, Z 55) poza kieszeniami (x −55,5…−44,5 / 44,5…55,5 / y). | K‑42, K‑60, README (wzór) |
| T3c | `snap_pocket_w` | 10 | **11** | Luz boczny haczyka 8 w kieszeni 1,0 → **1,5/stronę** (położenie haczyka ±0,3 i kieszeni ±0,3 na rozstawie 100–200 mm). | K‑42 (sonda 4,5 POZA / 6 W bez zmian: 5,5 półszerokości), pasowanie „szerokość 8 w kieszeni” (trzecie oko) |
| T4 | `blat_screw_hole_d` | 3,2 | **3,6** | Przelot M3 w ścianie tylnej: luz 0,3/stronę = ±0,3 położenia (korpus) + ±0,3 (słupek blatu) w X na rozstawie 150 (klasa „coarse” ISO 273 dla M3 = 3,6). Pogłębienie 90° ø6,3 bez zmian: stożek 1,35 głęboki, część walcowa 1,15 w ścianie 2,5; łeb DIN 965 ø6 siedzi w stożku. Rowek odrzucony (błąd położenia jest głównie w X, nie w Z). | K‑39 (sonda (75, 98,75, 52) W bez zmian: 3,0 od osi > r 1,9 na głębokości 1,25), trzecie oko „ø w ścianie”, „współosiowość” |
| T5 | `blat_pin_hole_d` | 3,3 | **3,4** | Kołek ø3 wkładki w blacie: otwór MJF wychodzi 3,2…3,3, kołek 2,9…3,1 → luz 0,05…0,25 (stary: od wcisku 0,15 do luzu 0,15 — zła klasa dla części zdejmowanej codziennie). **Klasa pasowania zmieniona z „wciskane 0,1–0,15” na „ruchome 0,2”**; wkładkę trzymają 2 magnesy, kołki tylko pozycjonują (powtarzalność ±0,2 ≤ ±0,5). | K‑47 (ø z JSON), pasowanie „kołek wkładki w otworze blatu” (reguła w arkuszu), trzecie oko (reguła R_WCISK → ruchome) |
| T6 | `insert_opening` | 96,6 | **96,8** | Płytka 96 we wkładce: luz 0,3 → **0,4/stronę**. Płytka MJF ±0,29 + wkładka ±0,29 → najgorzej 0,1 (było 0 → klinowanie, szlifowanie 6 płytek). Przy płytce CNC Al (±0,05): 0,35…0,65. Powtarzalność położenia płytki ±0,4 ≤ ±0,5 (4.6); kołek 4,4 w wycięciu 5 (0,5 od ścian) nadal blokuje obrót; kalibracja gniazdo → diody toleruje ±1,25. **Interfejs płytki bez zmian** (96 × 96, wycięcie 5, rowek, magnesy, pokrywka 96,6). Pochodne: rama 104,8, półki od 36,4, kołek orientacyjny w (45,7, −45,7), rowek kablowy 49,9…52,4 (ścianka do otworu 1,5 bez zmian), uszy od y 52,4, gabaryt wkładki 130 × **148,4** × 11, margines matrycy 27,6 → 11 pikseli (bez zmian). Rozbieżność z DESIGN B §3.3 p. 1 („96,6 zostaje przy MJF”) rozstrzygnięta na korzyść zasady R53 (suma tolerancji obu części). | tabela 1 protokołu (148,4), K‑23/K‑32 (sondy 48,2 POZA / 48,6 W; 52,6 POZA), K‑27 (48,15), K‑30 (opis), K‑56 (27,6), pasowanie „płytka w otworze wkładki” 0,4, trzecie oko (bbox, 52,3 → 52,4) |
| T6b | `tab_root_x_out` | 52,3 | **52,4** | = zewnętrzna krawędź ramy (96,8/2 + 4). Geometria nasady L liczy się z krawędzi ramy; klucz służy walidacji i opisowi — zmiana tylko dla spójności. | — |
| T6c | `orient_post_gap` | 0,5 | **0,6** | Kołek orientacyjny ma zostać w (45,6, −45,6) jak przed R53: przy 0,5 przesuwał się razem z otworem o 0,1 i jego naroże (47,9, −47,9) zahaczało o zaokrąglone R 1,5 naroże wnęki pokrywki (środek R w (46,8, −46,8): 1,556 > 1,5) o 0,059 mm — wykryte kopią trzeciego oka w 1. przebiegu R53 (K‑53 generatora z kurczeniem wierzchołków 0,05 tego nie wykrywa). Luz kołek–wycięcie płytki 0,4 bez zmian. | K‑27 (opis: luz 0,6), trzecie oko (montaż pokrywki), K‑53 |
| T12 | `panel_slot_w`, `panel_screw_hole_d` | 3,4 | **3,6** | Rowek przelotowy w dnie pod M3 dystansu: MJF −0,1…−0,2 → 3,4…3,5 ≥ M3 + 0,2. Stadion 9 → 2,7/stronę materiału zostaje. Podkładki panelu (żywica, ø3,4) bez zmian. | K‑35 (sondy: 2,8 i 2,1 od osi > 1,8 — bez zmian), K‑36, arkusz „rowek wkrętu panelu (cięciwa 5,091)” |
| T7 | `dc_bush_outer_d` / `dc_hole_d` | 11,85 / 12 | bez zmian | **CELOWO WCISKOWE** 0,075/stronę: tulejka to druk własny z żywicy, drukowana po pomiarze otworu w gotowym korpusie (W‑11: otwór MJF 11,7…11,9 → skorygować `dc_bush_outer_d` przed drukiem). Otwór ø12 w korpusie bez zmian. | — |
| T8 | `insert_hole_m3` 2,5 / `insert_hole_m25` 2,1 | — | bez zmian | Średnice są w normie dla wkrętów formujących w PA12 (0,8–0,85·d). Ryzyko to proszek w otworze MJF → **proces**: przewiercić ø2,1 / ø2,5 przed pierwszym wkręceniem (do kroku 7 planu wdrożenia — osobna sesja dokumentów). | — |
| T9 | — | — | bez zmian geometrii | Wypaczenie płaskich płyt: specyfikacja zamówienia („płasko w XY, chłodzenie w złożu”) i pomiar przy odbiorze — dokumenty (osobna sesja). | — |
| T10, T11, T14, T15, T16 | — | — | bez zmian | Luzy wystarczające (4 ±0,4 w spec 3–5; rozstaw USB 23…28; podkładki żywica; zapas Pi; serwis wtyku Bonnetu). | — |
| T13 | `cover_clearance` | 0,3 | bez zmian | Pokrywka FDM PETG = druk własny, pierwsza sztuka mierzona i skalowana (spec 4.2). Większy luz zmniejszyłby zahaczenie garbu (0,4 w rowku 0,8), a rowek jest interfejsem płytki (poza R53). Pokrywka bajtowo bez zmian. | — |
| W‑04 | — | — | → T1, T3, T5, T6 | Kryterium odbioru „reklamacja przy ±0,3” → przesunąć na > ±0,5 w dokumencie zakupów (osobna sesja). | — |

Niezmienione (wymóg zadania): wysokości 63,6 / 59,6 / 50, położenie Pi, pole skanowania, interfejs płytki (96 × 96 × 8, wycięcie, rowek, magnesy, stożki), pokrywka.

## 3. Pasowania po R53 (wartości nominalne do weryfikacji z siatek)

| Pasowanie | Przed | Po R53 | Kierunek / reguła |
|---|---|---|---|
| kołnierz blatu – ściana korpusu | 0,500 | **0,700** | X i Y, ruchome |
| haczyk: zahaczenie (czubek 98,3 − ściana 97,5) | −0,800 | **−0,800** | X, zatrzask (bez zmian) |
| haczyk: luz czubek – dno kieszeni | 0,200 | **0,500** | X, zatrzask |
| haczyk: luz pod występem (52,85 − dolna krawędź kieszeni) | 0,250 | **0,750** | Z |
| haczyk: luz nad występem (sufit kieszeni − 54,85) | 0,250 | **0,750** | Z |
| haczyk 8 w kieszeni (boczny) | 1,000 | **1,500** | wzdłuż ściany |
| wkręt blatu: otwór w ścianie ø | 3,200 | **3,600** | przelot M3 |
| kołek ø3 wkładki w otworze blatu | 0,150 | **0,200** | X/Y, ruchome (zmiana klasy) |
| płytka 96 w otworze wkładki | 0,300 | **0,400** | X/Y, ruchome |
| rowek panelu w dnie (szer.) | 3,400 | **3,600** | — |
| kołek orientacyjny w wycięciu płytki | 0,400 | **0,400** | bez zmian (kołek 0,6 od ściany otworu 96,8 = to samo położenie co 0,5 od 96,6; płytka wycentrowana) |
| pokrywka na płytce | 0,300 | 0,300 | bez zmian |
| tulejka DC w otworze ø12 | 0,075 (wcisk) | 0,075 (wcisk) | celowo wciskowe, druk własny |
| ściana korpusu za kieszenią zatrzasku | 1,500 | **1,200** | odstępstwo od 4.8, lokalne, nienośne |
| dno słupka blatu pod otworem wkrętu | 1,800 | **1,600** | ≥ 1,5 ✓ |

## 4. Pliki, które R53 zmienia

- STL przebudowane: `ramka_blat_v2.stl` (T1, T2a, T5), `ramka_korpus_W_v2.stl`, `ramka_korpus_P_v2.stl` (T2b, T3, T4, T12), `ramka_wkladka_v2.stl` (T6).
- STL bez zmian (muszą być bajtowo identyczne z kopią zapasową): 8 płytek, pokrywka, tulejka DC, 3 podkładki (13 plików).
- `parametry.json`: 13 kluczy (tabela 2; T6c dopisane po 1. przebiegu weryfikacji). `ramka_generator.py`: tylko sondy K‑23/K‑27/K‑32/K‑42 dopasowane do nowej geometrii, K‑56 liczone z parametrów zamiast literału 27,7, opisy reguł pasowań (`# R53`). `protokol_weryfikacji_v2.md`: tabela 1 (wkładka 148,4), sondy i opisy K‑23, K‑27, K‑30, K‑32, K‑35, K‑39, K‑42, K‑46, K‑47, K‑49, K‑56, K‑60 (oznaczone „[R53]”). `plan_ramki_v2.md`: sekcja 13 (R53), sekcja 14 (p. 22). Tabela 3 i opisy 4.x planu NIE są edytowane (poza mandatem sesji) — generator zgłosi odstępstwa informacyjne „tabela 3 planu” dla 10 kluczy; lista do naniesienia przez nadzór w `handout.md`.
- Skrypty recenzenta i trzecie oko: oryginały w `recenzja/` i `recenzja_koncowa/` nietknięte; kopie z oczekiwaniami R53 w `sesje_2026-10-31/poprawki_pasowan/skrypty/` (każda zmiana literału opisana w nagłówku kopii).
