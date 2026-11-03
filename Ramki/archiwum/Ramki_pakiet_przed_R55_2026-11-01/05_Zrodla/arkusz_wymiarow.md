# Arkusz wymiarów (v2)

Wygenerowany przez `ramka_generator.py`. Wszystkie wartości zmierzone promieniami na siatkach STL wczytanych z `stl/` (układy montażowe części jak w protokole 0.3) albo w złożeniu (`ramka_v2.blend`, układ D3). Nominał = wartość z `parametry.json`. „✓” = |różnica| ≤ 0,05 mm.

## 1. Gabaryty i objętości (orientacja druku)

| Plik STL | Gabaryt X × Y × Z [mm] | Objętość [cm³] |
|---|---|---|
| `ramka_plytka_wieczorna_v2.stl` | 96,000 × 96,000 × 8,000 | 59,30 |
| `ramka_plytka_wieczorna_n1_v2.stl` | 96,000 × 96,000 × 8,600 | 59,31 |
| `ramka_plytka_wieczorna_n2_v2.stl` | 96,000 × 96,000 × 8,600 | 59,31 |
| `ramka_plytka_wieczorna_n3_v2.stl` | 96,000 × 96,000 × 8,600 | 59,31 |
| `ramka_plytka_poranna_v2.stl` | 96,000 × 96,000 × 8,000 | 60,86 |
| `ramka_plytka_poranna_n4_v2.stl` | 96,000 × 96,000 × 8,600 | 60,87 |
| `ramka_plytka_poranna_n5_v2.stl` | 96,000 × 96,000 × 8,600 | 60,87 |
| `ramka_plytka_poranna_n6_v2.stl` | 96,000 × 96,000 × 8,600 | 60,87 |
| `ramka_pokrywka_v2.stl` | 99,600 × 99,600 × 20,000 | 30,06 |
| `ramka_wkladka_v2.stl` | 130,000 × 148,400 × 11,000 | 12,41 |
| `ramka_blat_v2.stl` | 200,000 × 200,000 × 14,000 | 72,52 |
| `ramka_korpus_W_v2.stl` | 200,000 × 200,600 × 59,600 | 233,49 |
| `ramka_korpus_P_v2.stl` | 200,000 × 200,600 × 59,600 | 233,47 |
| `ramka_tulejka_dc_v2.stl` | 14,999 × 14,999 × 3,000 | 0,24 |
| `ramka_podkladka_panelu_05_v2.stl` | 9,000 × 8,997 × 0,500 | 0,03 |
| `ramka_podkladka_panelu_1_v2.stl` | 9,000 × 8,997 × 1,000 | 0,05 |
| `ramka_podkladka_panelu_2_v2.stl` | 9,000 × 8,997 × 2,000 | 0,11 |

## 2. Wymiary główne części (z siatek)

### `ramka_plytka_wieczorna_n1_v2.stl`

| Wymiar | Metoda (punkt, oś) | Zmierzone [mm] | Nominał [mm] | Różnica |
|---|---|---|---|---|
| bok X | zewn. (0, 20, -4) X | 96,000 | 96,000 | 0,000 ✓ |
| bok Y | zewn. (20, 0, -4) Y | 96,000 | 96,000 | 0,000 ✓ |
| grubość | zewn. (0, -46.5, -4) Z | 8,000 | 8,000 | 0,000 ✓ |
| gniazdo id 2: ø na Z −2 (d − 2·2·tan 15°) | cięciwa (37.5, -15, -2) X | 10,929 | 10,928 | 0,001 ✓ |
| gniazdo id 2: otwór w dnie ø | cięciwa (37.5, -15, -6) X | 3,000 | 3,000 | 0,000 ✓ |
| gniazdo id 2: dno (Z) | trafienie (39.5, -15, 1) -Z | -4,000 | -4,000 | 0,000 ✓ |
| dołek kodu A ø | cięciwa (-45, -36, -0.5) X | 2,000 | 2,000 | 0,000 ✓ |
| kieszeń magnesu A ø | cięciwa (-42, -42, -7) X | 5,200 | 5,200 | 0,000 ✓ |
| kieszeń magnesu A: sufit (Z) | trafienie (-42, -42, -7) Z | -5,800 | -5,800 | 0,000 ✓ |
| rowek pokrywki: dno (x) | trafienie (60, 20, -2) -X | 47,200 | 47,200 | 0,000 ✓ |
| stożek znacznika A (-35.5, -26.5) ø na wierzchu (R54) | cięciwa (-35.5, -26.5, -0.05) X | 4,914 | 4,917 | -0,003 ✓ |

### `ramka_plytka_poranna_n4_v2.stl`

| Wymiar | Metoda (punkt, oś) | Zmierzone [mm] | Nominał [mm] | Różnica |
|---|---|---|---|---|
| bok X | zewn. (0, 20, -4) X | 96,000 | 96,000 | 0,000 ✓ |
| bok Y | zewn. (20, 0, -4) Y | 96,000 | 96,000 | 0,000 ✓ |
| grubość | zewn. (0, -46.5, -4) Z | 8,000 | 8,000 | 0,000 ✓ |
| gniazdo id 1: ø na Z −2 (d − 2·2·tan 15°) | cięciwa (10.5, -41.25, -2) X | 6,428 | 6,428 | 0,000 ✓ |
| gniazdo id 1: otwór w dnie ø | cięciwa (10.5, -41.25, -6) X | 3,000 | 3,000 | 0,000 ✓ |
| gniazdo id 1: dno (Z) | trafienie (12.5, -41.25, 1) -Z | -4,000 | -4,000 | 0,000 ✓ |
| dołek kodu C ø | cięciwa (-45, -30, -0.5) X | 2,000 | 2,000 | 0,000 ✓ |
| kieszeń magnesu A ø | cięciwa (-42, -42, -7) X | 5,200 | 5,200 | 0,000 ✓ |
| kieszeń magnesu A: sufit (Z) | trafienie (-42, -42, -7) Z | -5,800 | -5,800 | 0,000 ✓ |
| rowek pokrywki: dno (x) | trafienie (60, 20, -2) -X | 47,200 | 47,200 | 0,000 ✓ |
| stożek znacznika A (-34.5, -28) ø na wierzchu (R54) | cięciwa (-34.5, -28, -0.05) X | 4,914 | 4,917 | -0,003 ✓ |

### `ramka_pokrywka_v2.stl`

| Wymiar | Metoda (punkt, oś) | Zmierzone [mm] | Nominał [mm] | Różnica |
|---|---|---|---|---|
| bok X | zewn. (0, 20, -10) X | 99,600 | 99,600 | 0,000 ✓ |
| wnęka X | cięciwa (0, 20, -10) X | 96,600 | 96,600 | 0,000 ✓ |
| wnęka Y | cięciwa (20, 0, -10) Y | 96,600 | 96,600 | 0,000 ✓ |
| wysokość kołnierza | zewn. (49, 20, -10) Z | 20,000 | 20,000 | 0,000 ✓ |
| grubość wierzchu (pełny, R50‑U17) | zewn. (15, 0, -1) Z | 2,000 | 2,000 | 0,000 ✓ |
| wierzch płaski (R50‑U14) | trafienie (0, 0, 5) -Z | 0,000 | 0,000 | 0,000 ✓ |
| garb prawy: czubek (x) | trafienie (0, 0, -18) X | 47,600 | 47,600 | 0,000 ✓ |

### `ramka_wkladka_v2.stl`

| Wymiar | Metoda (punkt, oś) | Zmierzone [mm] | Nominał [mm] | Różnica |
|---|---|---|---|---|
| rama zewn. X | zewn. (0, 0, 4) X | 104,800 | 104,800 | 0,000 ✓ |
| otwór X | cięciwa (0, 0, 4) X | 96,800 | 96,800 | 0,000 ✓ |
| otwór Y (x = 20, poza wycięciem palcowym) | cięciwa (20, 0, 4) Y | 96,800 | 96,800 | 0,000 ✓ |
| otwór: naroże ostre (x przy y = 48,1) | trafienie (0, 48.2, 4) X | 48,400 | 48,400 | 0,000 ✓ |
| wysokość ramy | zewn. (-40, -50.3, 3) Z | 6,000 | 6,000 | 0,000 ✓ |
| półka A: grubość | zewn. (-38, -38, 1) Z | 2,500 | 2,500 | 0,000 ✓ |
| rowek kablowy prawy: dno (x) | trafienie (57.4, 0, 0.75) -X | 49,900 | 49,900 | 0,000 ✓ |
| rowek kablowy prawy: sufit (Z) | trafienie (51.15, 0, -5) Z | 1,500 | 1,500 | 0,000 ✓ |
| kołek orientacyjny X | cięciwa (45.6, -45.6, 5) X | 4,400 | 4,400 | 0,000 ✓ |
| kołek orientacyjny: szczyt (Z) | trafienie (45.6, -45.6, 5) Z | 7,500 | 7,500 | 0,000 ✓ |
| kieszeń Halla A X | cięciwa (-42, -42, 1.5) X | 5,000 | 5,000 | 0,000 ✓ |
| kieszeń Halla A Y | cięciwa (-42, -42, 1.5) Y | 5,500 | 5,500 | 0,000 ✓ |
| wycięcie palcowe X | cięciwa (0, -50.3, 3) X | 30,000 | 30,000 | 0,000 ✓ |
| ucho: grubość | zewn. (58, 80, 1) Z | 3,000 | 3,000 | 0,000 ✓ |
| kołek ustalający ø | cięciwa (58, 93.5, -2) X | 3,000 | 3,000 | 0,000 ✓ |
| kołek ustalający: koniec (Z) | trafienie (58, 93.5, -1) -Z | -3,500 | -3,500 | 0,000 ✓ |
| otwór magnesu ucha ø | cięciwa (58, 86, 1.5) X | 5,400 | 5,400 | 0,000 ✓ |

### `ramka_blat_v2.stl`

| Wymiar | Metoda (punkt, oś) | Zmierzone [mm] | Nominał [mm] | Różnica |
|---|---|---|---|---|
| bok X | zewn. (0, 20, -2) X | 200,000 | 200,000 | 0,000 ✓ |
| kieszeń dyfuzora X | cięciwa (0, 20, -1) X | 162,000 | 162,000 | 0,000 ✓ |
| kieszeń dyfuzora: naroże ostre (x przy y = 80,8) | trafienie (0, 80.8, -1) X | 81,000 | 81,000 | 0,000 ✓ |
| okno X | cięciwa (0, 20, -3) X | 158,000 | 158,000 | 0,000 ✓ |
| grubość płyty | zewn. (90, 0, -2) Z | 4,000 | 4,000 | 0,000 ✓ |
| płyta pod dawnym bossem ramy (R50‑U1): spód (Z) | trafienie (90, 90, -20) Z | -4,000 | -4,000 | 0,000 ✓ |
| kołnierz zewn. X | zewn. (0, 20, -9) X | 193,600 | 193,600 | 0,000 ✓ |
| kołnierz + płyta: wysokość | zewn. (96, 20, -9) Z | 14,000 | 14,000 | 0,000 ✓ |
| haczyk prawy: czubek (x) | trafienie (110, 0, -9.5) -X | 98,300 | 98,300 | 0,000 ✓ |
| otwór słupka ø | cięciwa (75, 94, -8.6) X | 2,500 | 2,500 | 0,000 ✓ |
| otwór słupka: dno (y) | trafienie (75, 94, -8.6) -Y | 90,800 | 90,800 | 0,000 ✓ |
| otwór kołka ø | cięciwa (58, 93.5, -2) X | 3,395 | 3,400 | -0,005 ✓ |
| otwór kołka: dno (Z) | trafienie (58, 93.5, -1) -Z | -3,800 | -3,800 | 0,000 ✓ |
| kieszeń magnesu ø | cięciwa (58, 86, -1) X | 5,400 | 5,400 | 0,000 ✓ |
| szczelina kabla X | cięciwa (66, 90, -2) X | 4,000 | 4,000 | 0,000 ✓ |
| szczelina kabla Y | cięciwa (66, 90, -2) Y | 8,000 | 8,000 | 0,000 ✓ |

### `ramka_korpus_W_v2.stl`

| Wymiar | Metoda (punkt, oś) | Zmierzone [mm] | Nominał [mm] | Różnica |
|---|---|---|---|---|
| bok X | zewn. (0, 20, 20) X | 200,000 | 200,000 | 0,000 ✓ |
| bok Y | zewn. (20, 0, 20) Y | 200,000 | 200,000 | 0,000 ✓ |
| wnętrze X | cięciwa (0, 20, 20) X | 195,000 | 195,000 | 0,000 ✓ |
| wnętrze Y | cięciwa (20, 0, 20) Y | 195,000 | 195,000 | 0,000 ✓ |
| ściana: wierzch (Z) | trafienie (98.75, 20, 200) -Z | 59,600 | 59,600 | 0,000 ✓ |
| dno | zewn. (20, -20, 1) Z | 3,000 | 3,000 | 0,000 ✓ |
| stadion panelu: wierzch (Z) | trafienie (64, 60, 20) -Z | 4,000 | 4,000 | 0,000 ✓ |
| rowek wkrętu panelu: cięciwa wzdłuż X (= szer. × √2) | cięciwa (60, 60, 1.5) X | 5,091 | 5,091 | 0,000 ✓ |
| boss Pi: wierzch (Z) | trafienie (-43.5, -24.5, 20) -Z | 8,000 | 8,000 | 0,000 ✓ |
| boss Pi: otwór ø | cięciwa (-46.5, -24.5, 7) X | 2,100 | 2,100 | 0,000 ✓ |
| boss Pi: krawędź (y) | trafienie (-46.5, -9.5, 5) -Y | -20,501 | -20,500 | -0,001 ✓ |
| wlot w dnie X | cięciwa (-8, -10, 1.5) X | 30,000 | 30,000 | 0,000 ✓ |
| wlot w dnie Y | cięciwa (-8, -10, 1.5) Y | 4,000 | 4,000 | 0,000 ✓ |
| kieszeń DC: okno X | cięciwa (-67.5, 98.75, 26) X | 51,000 | 51,000 | 0,000 ✓ |
| kieszeń DC: okno Z | cięciwa (-67.5, 98.75, 26) Z | 24,000 | 24,000 | 0,000 ✓ |
| kieszeń DC: wnętrze X (lewa ściana skrzynki → prawa) | cięciwa (-67.5, 87.75, 16) X | 53,500 | 53,500 | 0,000 ✓ |
| kieszeń DC: dno w świetle (y) | trafienie (-67.5, 110, 16) -Y | 80,000 | 80,000 | 0,000 ✓ |
| gniazdo DC: otwór ø w prawej ścianie skrzynki (oś X) | cięciwa (-41, 89, 30) Y | 11,999 | 12,000 | -0,001 ✓ |
| okno USB X | cięciwa (60, 98.75, 24) X | 16,000 | 16,000 | 0,000 ✓ |
| okno USB Z | cięciwa (60, 98.75, 24) Z | 9,000 | 9,000 | 0,000 ✓ |
| rowek flanszy USB prawy X | cięciwa (72.75, 98.75, 24) X | 5,691 | 5,700 | -0,009 ✓ |
| rowek flanszy USB prawy Z | cięciwa (72.75, 98.75, 24) Z | 3,200 | 3,200 | 0,000 ✓ |
| kieszeń zatrzasku prawa Y | cięciwa (98, 0, 53.3) Y | 11,000 | 11,000 | 0,000 ✓ |
| kieszeń zatrzasku prawa Z | cięciwa (98, 0, 53.3) Z | 3,500 | 3,500 | 0,000 ✓ |
| kieszeń zatrzasku: dno (x) | trafienie (80, 0, 53.3) X | 98,800 | 98,800 | 0,000 ✓ |
| szczelina tylna X | cięciwa (-54, 98.75, 8) X | 12,000 | 12,000 | 0,000 ✓ |
| szczelina tylna Z | cięciwa (-54, 98.75, 8) Z | 3,000 | 3,000 | 0,000 ✓ |
| otwór wkrętu blatu ø (w ścianie) | cięciwa (75, 97.8, 55) X | 3,600 | 3,600 | 0,000 ✓ |

### `ramka_tulejka_dc_v2.stl`

| Wymiar | Metoda (punkt, oś) | Zmierzone [mm] | Nominał [mm] | Różnica |
|---|---|---|---|---|
| kołnierz ø | zewn. (0, 0, 0.5) X | 14,999 | 15,000 | -0,001 ✓ |
| walec: promień zewn. (x) | trafienie (10, 0, 2) -X | 5,925 | 5,925 | 0,000 ✓ |
| otwór ø | cięciwa (0, 0, 1) X | 8,200 | 8,200 | 0,000 ✓ |
| wysokość | zewn. (5.0125, 0, 1) Z | 3,000 | 3,000 | 0,000 ✓ |
| kołnierz: grubość | zewn. (6.7125, 0, 0.5) Z | 1,000 | 1,000 | 0,000 ✓ |

### `ramka_podkladka_panelu_05_v2.stl`

| Wymiar | Metoda (punkt, oś) | Zmierzone [mm] | Nominał [mm] | Różnica |
|---|---|---|---|---|
| ø zewn. | zewn. (0, 0, 0.25) X | 9,000 | 9,000 | 0,000 ✓ |
| otwór ø | cięciwa (0, 0, 0.25) X | 3,395 | 3,400 | -0,005 ✓ |
| grubość | zewn. (3.1, 0, 0.25) Z | 0,500 | 0,500 | 0,000 ✓ |

### `ramka_podkladka_panelu_1_v2.stl`

| Wymiar | Metoda (punkt, oś) | Zmierzone [mm] | Nominał [mm] | Różnica |
|---|---|---|---|---|
| ø zewn. | zewn. (0, 0, 0.5) X | 9,000 | 9,000 | 0,000 ✓ |
| otwór ø | cięciwa (0, 0, 0.5) X | 3,395 | 3,400 | -0,005 ✓ |
| grubość | zewn. (3.1, 0, 0.5) Z | 1,000 | 1,000 | 0,000 ✓ |

### `ramka_podkladka_panelu_2_v2.stl`

| Wymiar | Metoda (punkt, oś) | Zmierzone [mm] | Nominał [mm] | Różnica |
|---|---|---|---|---|
| ø zewn. | zewn. (0, 0, 1) X | 9,000 | 9,000 | 0,000 ✓ |
| otwór ø | cięciwa (0, 0, 1) X | 3,395 | 3,400 | -0,005 ✓ |
| grubość | zewn. (3.1, 0, 1) Z | 2,000 | 2,000 | 0,000 ✓ |

## 3. Pasowania (tabela 4.11, zasady 4.8) zmierzone w złożeniu

Luz dodatni = szczelina; ujemny = zahaczenie zatrzasku; 0 = styk. Pomiar: pierwsze trafienie promienia w każdą z dwóch części wzdłuż osi.

| Pasowanie | Zmierzone [mm] | Nominał [mm] | Różnica | Reguła |
|---|---|---|---|---|
| płytka w otworze wkładki (x) | 0,400 | 0,400 | 0,000 ✓ | ruchome 0,4 (R53; było 0,2–0,3) |
| płytka w otworze wkładki (y, przód) | 0,400 | 0,400 | 0,000 ✓ | ruchome 0,4 (R53; było 0,2–0,3) |
| pokrywka na płytce (x) | 0,300 | 0,300 | 0,000 ✓ | ruchome 0,2–0,3 |
| garb pokrywki: zahaczenie w rowku płytki (x) | -0,400 | -0,400 | 0,000 ✓ | zatrzask (ujemny = zahaczenie) |
| garb pokrywki: luz do dna rowka (x) | 0,400 | 0,400 | 0,000 ✓ | zatrzask |
| kołek orientacyjny w wycięciu płytki (x) | 0,400 | 0,400 | 0,000 ✓ | ruchome (4.11: wycięcie 5, kołek 4,4) |
| kołek orientacyjny w wycięciu płytki (y) | 0,400 | 0,400 | 0,000 ✓ | ruchome (4.11: wycięcie 5, kołek 4,4) |
| magnes A w kieszeni płytki (x) | 0,100 | 0,100 | 0,000 ✓ | magnesy 0,1–0,2 (klejone) |
| kołek wkładki w otworze blatu (x) | 0,200 | 0,200 | 0,000 ✓ | ruchome 0,2 (R53: było wciskane 0,1–0,15) |
| kołnierz blatu – ściana korpusu (x) | 0,700 | 0,700 | 0,000 ✓ | ruchome 0,7 = ±0,3 + ±0,3 MJF (R48/R53) |
| haczyk blatu: zahaczenie w kieszeni korpusu (x) | -0,800 | -0,800 | 0,000 ✓ | zatrzask (ujemny = zahaczenie) |
| haczyk blatu: luz do dna kieszeni (x) | 0,500 | 0,500 | 0,000 ✓ | zatrzask (R53: 0,5) |
| haczyk blatu: luz nad występem (z) | 0,750 | 0,750 | 0,000 ✓ | zatrzask (R53: 0,75; było R47: 0,25) |
| dyfuzor w kieszeni blatu (x) | 1,000 | 1,000 | 0,000 ✓ | luz 1,0 (D13) |
| PCB panelu – spód blatu przy oknie (z) | 4,000 | 4,000 | 0,000 ✓ | K‑49: ≥ 2 (R50‑1) |
| wkładka na dyfuzorze (z) | 0,000 | 0,000 | 0,000 ✓ | styk (R30) |
| płytka na półce wkładki (z) | 0,000 | 0,000 | 0,000 ✓ | styk (D5) |
| kołnierz pokrywki nad ramą wkładki (z) | 0,500 | 0,500 | 0,000 ✓ | bez styku |
| Pi + Bonnet – spód elementów panelu (z) | 8,000 | 8,000 | 0,000 ✓ | D4/R50‑1: ≥ 8 |
| dystans na stadionie korpusu (z) | 0,000 | 0,000 | 0,000 ✓ | styk (R5, R50‑2) |
| PCB panelu na dystansie (z) | 0,000 | 0,000 | 0,000 ✓ | styk (R50‑7) |
| tulejka DC w otworze ściany skrzynki (y) | 0,076 | 0,075 | 0,001 ✓ | wciskane 0,075/stronę (R52, 4.8) |
| tulejka DC: kołnierz na ścianie skrzynki (x) | 0,000 | 0,000 | 0,000 ✓ | styk (R50‑3) |
| wtyk DC Bonnetu (−X) – lewa ściana korpusu (x) | 7,500 | 7,500 | 0,000 ✓ | D10/R50‑6: zapas 7,5 (tylko kierunek −X) |

## 4. Małe części druku własnego (R50‑3, R50‑8)

- Tulejka DC: kołnierz ø15 × 1 (strona kieszeni) + walec ø11,85 × 2, otwór ø8,2; w złożeniu kołnierz na licu x = -42 prawej ściany skrzynki, walec w otworze ø12 (oś y 89, Z 30 wzdłuż X). Sondy K‑52b z protokołu.
- Podkładki panelu: krążki ø9 z otworem ø3,4, grubości 0,5 / 1,0 / 2,0 mm (pliki `ramka_podkladka_panelu_05_v2.stl`, `ramka_podkladka_panelu_1_v2.stl`, `ramka_podkladka_panelu_2_v2.stl`); przy domyślnych wymiarach nieużywane — w `.blend` obok zestawu. Sondy K‑52c z protokołu.

## 6. Pełny zrzut `parametry.json` użytego w tym przebiegu

SHA‑256: `e8e5fb7f665328f54f2dea4f7d00f6b675c0b86ac0b25e2d328de20083449afc`

```json
{
  "_meta": {
    "plan": "plan_ramki_v2.md",
    "version": "v2",
    "units": "mm (długości), deg (kąty), zł/cm3 (stawki)",
    "status_values": ["SPEC", "ZALOZENIE", "DO_ZMIERZENIA", "ZMIERZONE", "LICZONE"],
    "zasada": "Jedyne źródło wartości dla ramka_generator.py (R14). Skrypt wczytuje ten plik, odrzuca nieznane klucze i brak kluczy, a wartości LICZONE wylicza sam i porównuje z tym plikiem (różnica > 0,01 = błąd). Pomiar: wpisz wartość, zmień status na ZMIERZONE, uruchom cały skrypt ponownie (R28)."
  },

  "plytka": {
    "plate_size":            {"value": 96,    "status": "SPEC",   "opis": "bok płytki"},
    "plate_thickness":       {"value": 8,     "status": "SPEC",   "opis": "grubość płytki"},
    "plate_corner_zone":     {"value": 13,    "status": "ZALOZENIE", "zrodlo": "Z3", "opis": "kwadrat narożny bez gniazd"},
    "plate_edge_r":          {"value": 1,     "status": "ZALOZENIE", "zrodlo": "4.1", "opis": "promień pionowych krawędzi płytki"},
    "plate_top_chamfer":     {"value": 0.5,   "status": "ZALOZENIE", "zrodlo": "4.1", "opis": "faza górnej krawędzi płytki"},
    "socket_zone":           {"value": 90,    "status": "SPEC",   "opis": "bok strefy gniazd (kwadrat); od R54 dodatkowo koło socket_zone_r"},
    "scan_field_d":          {"value": 100,   "status": "DO_ZMIERZENIA", "zrodlo": "Z29/R54", "opis": "średnica koła wokół osi stolika skanera widocznego w całym obrocie (pole skanowania przy ścieżce bez przechyłu); pomiar #12; dawniej założenie 100 x 100"},
    "scan_center_tol":       {"value": 1.5,   "status": "ZALOZENIE", "zrodlo": "Z29/R54", "opis": "błąd ułożenia środka płytki względem osi obrotu stolika (na stronę)"},
    "work_overhang":         {"value": 1.5,   "status": "ZALOZENIE", "zrodlo": "Z29/R54", "opis": "wysięg pracy poza obrys górny gniazda (korona szersza od gniazda)"},
    "socket_zone_r":         {"value": 47,    "status": "LICZONE", "wzor": "scan_field_d / 2 - scan_center_tol - work_overhang", "opis": "promień koła (od środka płytki), w którym leżą obrysy górne wszystkich gniazd, rynienek i stożków znaczników (R54, D6); K-05 (c)"},
    "socket_wall_min":       {"value": 3,     "status": "SPEC",   "opis": "min. ścianka między gniazdami"},
    "socket_depth":          {"value": 4,     "status": "SPEC",   "opis": "głębokość gniazd i rynienek"},
    "socket_wall_angle":     {"value": 15,    "status": "SPEC",   "opis": "kąt ścianki stożka od pionu [deg]"},
    "socket_hole_d":         {"value": 3,     "status": "SPEC",   "opis": "otwór przelotowy w dnie gniazda"},
    "trough_hole_count":     {"value": 4,     "status": "ZALOZENIE", "zrodlo": "Z24", "opis": "otwory w dnie rynienki"},
    "ev_trough_hole_pitch":  {"value": 12,    "status": "ZALOZENIE", "zrodlo": "Z24"},
    "mo_trough_hole_pitch":  {"value": 10,    "status": "ZALOZENIE", "zrodlo": "Z24"},
    "marker_cone_d":         {"value": 5,     "status": "SPEC"},
    "marker_cone_depth":     {"value": 3,     "status": "SPEC"},
    "marker_offset":         {"value": 6,     "status": "ZALOZENIE", "zrodlo": "Z4/R54", "opis": "oś KIESZENI MAGNESU od obu krawędzi rogu → A(-42,-42) B(-42,42) C(42,42); od R54 stożki znaczników leżą osobno (ev_marker_pos / mo_marker_pos), Z4 uchylone"},
    "ev_marker_pos":         {"value": {"A": [-35.5, -26.5], "B": [-35.5, 26.5], "C": [35.5, 26.5]}, "status": "ZALOZENIE", "zrodlo": "R54/D6", "opis": "środki stożków znaczników płytki wieczornej; promień 44,30 ≤ socket_zone_r − 2,5; ścianka do gniazd ≥ 3 (3,17 / 3,01 / 3,01)"},
    "mo_marker_pos":         {"value": {"A": [-34.5, -28], "B": [-30, 32.5], "C": [30, 32.5]}, "status": "ZALOZENIE", "zrodlo": "R54/D6", "opis": "środki stożków znaczników płytki porannej; promień 44,43 / 44,23 ≤ 44,5; ścianka do gniazd ≥ 3 (7,00 / 3,01 / 3,01)"},
    "notch_size":            {"value": 5,     "status": "SPEC",   "opis": "wycięcie przelotowe w rogu D: x 43..48, y -48..-43"},
    "code_dimple_d":         {"value": 2,     "status": "SPEC"},
    "code_dimple_depth":     {"value": 1,     "status": "SPEC"},
    "code_dimple_x":         {"value": -45.0, "status": "ZALOZENIE", "zrodlo": "R3"},
    "code_dimple_y0":        {"value": -36,   "status": "ZALOZENIE", "zrodlo": "R3", "opis": "bit A; bit B = y0 + pitch; bit C = y0 + 2*pitch"},
    "code_dimple_pitch":     {"value": 3,     "status": "ZALOZENIE", "zrodlo": "D11"},
    "magnet_d":              {"value": 5,     "status": "SPEC"},
    "magnet_h":              {"value": 2,     "status": "SPEC"},
    "magnet_pocket_d":       {"value": 5.2,   "status": "SPEC"},
    "magnet_pocket_depth":   {"value": 2.2,   "status": "SPEC"},
    "number_relief_h":       {"value": 0.6,   "status": "SPEC"},
    "number_text_h":         {"value": 5,     "status": "ZALOZENIE", "zrodlo": "D11"},
    "number_pos_x":          {"value": 39.5,  "status": "ZALOZENIE", "zrodlo": "D11"},
    "number_pos_y":          {"value": -44.5, "status": "ZALOZENIE", "zrodlo": "D11"},
    "cover_groove_w":        {"value": 1.0,   "status": "ZALOZENIE", "zrodlo": "D8", "opis": "wysokość rowka na bokach płytki"},
    "cover_groove_depth":    {"value": 0.8,   "status": "ZALOZENIE", "zrodlo": "D8"},
    "cover_groove_z":        {"value": 2,     "status": "ZALOZENIE", "zrodlo": "D8", "opis": "środek rowka poniżej wierzchu"},
    "ev_socket_d_s":         {"value": 9,     "status": "SPEC"},
    "ev_socket_d_m":         {"value": 12,    "status": "SPEC"},
    "ev_socket_d_l":         {"value": 15,    "status": "SPEC"},
    "ev_trough_l":           {"value": 60,    "status": "SPEC"},
    "ev_trough_w":           {"value": 15,    "status": "SPEC"},
    "mo_socket_d_s":         {"value": 7.5,   "status": "SPEC"},
    "mo_socket_d_m":         {"value": 10,    "status": "SPEC"},
    "mo_socket_d_l":         {"value": 12.5,  "status": "SPEC"},
    "mo_trough_l":           {"value": 50,    "status": "SPEC"},
    "mo_trough_w":           {"value": 13,    "status": "SPEC"},
    "ev_rows": {"value": [
        {"y": -31.5, "type": "trough", "l": 60, "w": 15, "x": [0]},
        {"y": -15,   "type": "round", "d": 12, "x": [-37.5, -22.5, -7.5, 7.5, 22.5, 37.5]},
        {"y": -1.5,  "type": "round", "d": 9,  "x": [-36, -24, -12, 0, 12, 24, 36]},
        {"y": 13.5,  "type": "round", "d": 15, "x": [-36, -18, 0, 18, 36]},
        {"y": 31.5,  "type": "trough", "l": 60, "w": 15, "x": [0]}
      ], "status": "ZALOZENIE", "zrodlo": "D6/R54", "opis": "R54: rzędy od przodu przycięte do koła socket_zone_r 47, rynienki z przodu i z tyłu; 18 gniazd + 2 rynienki; używane TYLKO do wygenerowania uklad_gniazd_wieczorna.json, gdy go nie ma (stary plik z układu 24 + 2 usunąć, R54)"},
    "mo_rows": {"value": [
        {"y": -41.25, "type": "round", "d": 7.5,  "x": [-10.5, 0, 10.5]},
        {"y": -28,    "type": "trough", "l": 50, "w": 13, "x": [0]},
        {"y": -13.5,  "type": "round", "d": 10,   "x": [-39, -26, -13, 0, 13, 26, 39]},
        {"y": 0.75,   "type": "round", "d": 12.5, "x": [-38.75, -23.25, -7.75, 7.75, 23.25, 38.75]},
        {"y": 13.6,   "type": "round", "d": 7.5,  "x": [-36.75, -26.25, -15.75, -5.25, 5.25, 15.75, 26.25, 36.75]},
        {"y": 22.7,   "type": "round", "d": 7.5,  "x": [-31.5, -21, -10.5, 0, 10.5, 21, 31.5]},
        {"y": 35.95,  "type": "trough", "l": 50, "w": 13, "x": [0]}
      ], "status": "ZALOZENIE", "zrodlo": "D6/R54", "opis": "R54: 31 gniazd + 2 rynienki; rzędy y 0,75 → 13,6 → 22,7 w szachownicę (ścianka 3 po przekątnej: 13,00 i 10,51 między osiami); stary plik uklad_gniazd_poranna.json (35 + 2) usunąć"},
    "plate_numbers_ev":      {"value": [1, 2, 3], "status": "ZALOZENIE", "zrodlo": "D11"},
    "plate_numbers_mo":      {"value": [4, 5, 6], "status": "ZALOZENIE", "zrodlo": "D11"}
  },

  "pokrywka": {
    "max_work_height":   {"value": 14,  "status": "ZALOZENIE", "zrodlo": "Z2"},
    "cover_inner_h":     {"value": 14,  "status": "LICZONE", "wzor": "max_work_height - socket_depth + 4"},
    "cover_top_t":       {"value": 2,   "status": "ZALOZENIE", "zrodlo": "D8"},
    "cover_skirt_t":     {"value": 1.5, "status": "ZALOZENIE", "zrodlo": "D8"},
    "cover_skirt_below": {"value": 4,   "status": "ZALOZENIE", "zrodlo": "D8"},
    "cover_clearance":   {"value": 0.3, "status": "SPEC", "zrodlo": "4.8"},
    "cover_snap_bump":   {"value": 0.7, "status": "ZALOZENIE", "zrodlo": "D8/R21"},
    "cover_snap_w":      {"value": 10,  "status": "ZALOZENIE", "zrodlo": "D8"},
    "cover_snap_hgt":    {"value": 0.8, "status": "ZALOZENIE", "zrodlo": "R47", "opis": "wysokość garbu w Z (w rowku 1,0)"},
    "cover_snap_r":      {"value": 0.4, "status": "ZALOZENIE", "zrodlo": "R47/G2", "opis": "czubek garbu = półokrąg cover_snap_hgt/2"},
    "cover_snap_z":      {"value": -18, "status": "ZALOZENIE", "zrodlo": "R47", "opis": "środek garbu, lokalnie od wierzchu pokrywki"},
    "cover_snap_front_x": {"value": 25, "status": "ZALOZENIE", "zrodlo": "R42", "opis": "garb przód x=+25, tył x=-25, boki y=0"},
    "cover_snap_count":  {"value": 4,   "status": "SPEC", "zrodlo": "R21"},
    "cover_finger_w":    {"value": 30,  "status": "ZALOZENIE", "zrodlo": "4.2", "opis": "wycięcie 30 x 3 na dolnej krawędzi przodu i tyłu"},
    "cover_finger_h":    {"value": 3,   "status": "ZALOZENIE", "zrodlo": "4.2"},
    "cover_corner_r":    {"value": 3,   "status": "SPEC", "zrodlo": "4.1"}
  },

  "panel_dyfuzor_pi": {
    "panel_size":            {"value": 160,  "status": "SPEC"},
    "panel_pcb_t":           {"value": 1.6,  "status": "SPEC"},
    "panel_led_h":           {"value": 2,    "status": "DO_ZMIERZENIA", "pomiar": 3},
    "panel_bottom_parts_h":  {"value": 12,   "status": "DO_ZMIERZENIA", "pomiar": 4},
    "panel_hole_pitch_x":    {"value": 120,  "status": "DO_ZMIERZENIA", "pomiar": 5},
    "panel_hole_pitch_y":    {"value": 120,  "status": "DO_ZMIERZENIA", "pomiar": 5},
    "panel_hole_offset_x":   {"value": 0,    "status": "DO_ZMIERZENIA", "pomiar": 6},
    "panel_hole_offset_y":   {"value": 0,    "status": "DO_ZMIERZENIA", "pomiar": 6},
    "panel_hole_threaded":   {"value": true, "status": "DO_ZMIERZENIA", "pomiar": "5a", "opis": "czy otwory panelu mają gwint M3 (R5)"},
    "panel_conn_zone_x":     {"value": 0,    "status": "DO_ZMIERZENIA", "pomiar": 7},
    "panel_conn_zone_y":     {"value": 0,    "status": "DO_ZMIERZENIA", "pomiar": 7},
    "panel_conn_zone_w":     {"value": 120,  "status": "DO_ZMIERZENIA", "pomiar": 7},
    "panel_conn_zone_h":     {"value": 60,   "status": "DO_ZMIERZENIA", "pomiar": 7},
    "led_pitch":             {"value": 2.5,  "status": "SPEC"},
    "led_gap":               {"value": 4,    "status": "ZALOZENIE", "zrodlo": "Z23"},
    "diffuser_size":         {"value": 160,  "status": "SPEC"},
    "diffuser_t":            {"value": 2,    "status": "SPEC"},
    "diffuser_pocket":       {"value": 162,  "status": "SPEC"},
    "diffuser_pocket_r":     {"value": 0,    "status": "ZALOZENIE", "zrodlo": "R50-U15", "opis": "naroża kieszeni dyfuzora ostre; pleksi bez fazowania (R29 uchylone)"},
    "window_through":        {"value": 158,  "status": "ZALOZENIE", "zrodlo": "D13"},
    "pi_l":                  {"value": 85,   "status": "SPEC"},
    "pi_w":                  {"value": 56,   "status": "SPEC"},
    "pi_hole_pitch_l":       {"value": 58,   "status": "SPEC"},
    "pi_hole_pitch_w":       {"value": 49,   "status": "SPEC"},
    "pi_hole_edge":          {"value": 3.5,  "status": "SPEC"},
    "pi_hole_d":             {"value": 2.7,  "status": "SPEC"},
    "pi_pos_x":              {"value": -50,  "status": "ZALOZENIE", "zrodlo": "R50-6", "opis": "narożnik PCB Pi (krawędź SD, przód); Pi x -50..35, y -28..28; każdy kierunek wtyku DC Bonnetu ma miejsce"},
    "pi_pos_y":              {"value": -28,  "status": "ZALOZENIE", "zrodlo": "D10"},
    "pi_standoff_h":         {"value": 5,    "status": "ZALOZENIE", "zrodlo": "D4"},
    "pi_boss_d":             {"value": 8,    "status": "ZALOZENIE", "zrodlo": "R48/R49", "opis": "ścianka 2,95 wokół otworu ø2,1 pod wkręt M2,5 formujący gwint w PA12 (bez wkładek)"},
    "pi_stack_h":            {"value": 26,   "status": "DO_ZMIERZENIA", "pomiar": 9, "opis": "bez taśmy; z wpiętą taśmą HUB75 do 31 mieści się w zapasie R50-1"},
    "pi_clearance_top":      {"value": 8,    "status": "ZALOZENIE", "zrodlo": "R50-1", "opis": "zapas nad stosem Pi: pokrywa taśmę HUB75 w IDC Bonnetu i złącza panelu z kablami (do +5 łącznie)"},
    "standoff_d":            {"value": 6.4,  "status": "ZALOZENIE", "zrodlo": "R47", "opis": "bryła zastępcza dystansu (sześciokąt 5,5)"},
    "bonnet_dc_pos_x":       {"value": -50,  "status": "DO_ZMIERZENIA", "pomiar": 10, "zrodlo": "R50-6/A-4", "opis": "domyślnie krawędź SD Bonnetu; korpus od tego niezależny"},
    "bonnet_dc_pos_y":       {"value": 22,   "status": "DO_ZMIERZENIA", "pomiar": 10, "zrodlo": "R50-6/A-4"},
    "bonnet_dc_dir":         {"value": "-X", "status": "DO_ZMIERZENIA", "pomiar": 10, "zrodlo": "R50-6/A-4", "opis": "-X, +X, -Y lub +Y; po R50-6 każdy kierunek mieści wtyk 40"},
    "bonnet_dc_plug_len":    {"value": 40,   "status": "ZALOZENIE", "zrodlo": "R50-6", "opis": "wysięg wtyku DC Bonnetu poza krawędź PCB (wtyk ze śrubkami, najdłuższy z listy zakupów)"},
    "bonnet_dc_plug_w":      {"value": 10,   "status": "ZALOZENIE", "zrodlo": "R47"},
    "bonnet_dc_plug_h":      {"value": 11,   "status": "ZALOZENIE", "zrodlo": "R47"},
    "panel_slot_pitch_min":  {"value": 110,  "status": "ZALOZENIE", "zrodlo": "R50-2", "opis": "rowek podkładki panelu po przekątnej od (±55, ±55)"},
    "panel_slot_pitch_max":  {"value": 130,  "status": "ZALOZENIE", "zrodlo": "R50-2", "opis": "do (±65, ±65); wzór niekwadratowy/offset -> wiercenie ø4 w dnie (fallback)"},
    "panel_slot_w":          {"value": 3.6,  "status": "ZALOZENIE", "zrodlo": "R50-2/R53", "opis": "szerokość rowka przelotowego w dnie (= panel_screw_hole_d); bez pogłębienia (R50-U20); R53 (T12): 3,4 -> 3,6 (otwory MJF wychodzą mniejsze o 0,1-0,2)"}
  },

  "korpus": {
    "box_outer":        {"value": 200,  "status": "SPEC"},
    "wall_t":           {"value": 2.5,  "status": "SPEC", "zrodlo": "4.1"},
    "floor_t":          {"value": 3,    "status": "SPEC", "zrodlo": "4.1"},
    "box_corner_r":     {"value": 5,    "status": "SPEC"},
    "box_edge_r":       {"value": 3,    "status": "SPEC"},
    "korpus_h":         {"value": 59.6, "status": "LICZONE", "wzor": "blat_top_z - blat_t"},
    "blat_top_z":       {"value": 63.6, "status": "LICZONE", "wzor": "panel_pcb_z + panel_pcb_t + panel_led_h + led_gap + diffuser_t"},
    "panel_pcb_z":      {"value": 54,   "status": "LICZONE", "wzor": "floor_t + pi_standoff_h + pi_stack_h + pi_clearance_top + panel_bottom_parts_h"},
    "panel_pad_h":      {"value": 1,    "status": "ZALOZENIE", "zrodlo": "R5"},
    "panel_pad_d":      {"value": 9,    "status": "ZALOZENIE", "zrodlo": "R5/R50-2", "opis": "szerokość podkładki-stadionu wzdłuż przekątnej od (±55,±55) do (±65,±65), wys. panel_pad_h"},
    "panel_standoff_l": {"value": 50,   "status": "LICZONE", "wzor": "panel_pcb_z - floor_t - panel_pad_h", "opis": "50 F-F przy gwincie panelu; 45 F-F + tulejka klejona 5 bez gwintu (R50-7)"},
    "panel_screw_hole_d":  {"value": 3.6, "status": "ZALOZENIE", "zrodlo": "R5/R53", "opis": "= szerokość rowka w dnie (R50-2); łeb M3 + podkładka pod dnem, bez pogłębienia (R50-U20); R53 (T12): 3,4 -> 3,6"},
    "insert_hole_m3":   {"value": 2.5,  "status": "ZALOZENIE", "zrodlo": "R49", "opis": "otwór pod wkręt M3/PT3,0 formujący gwint w PA12; bez wkładek"},
    "insert_hole_m25":  {"value": 2.1,  "status": "ZALOZENIE", "zrodlo": "R49", "opis": "otwór pod wkręt M2,5/PT2,5 formujący gwint"},
    "insert_depth_m3":  {"value": 7,    "status": "ZALOZENIE", "zrodlo": "R49", "opis": "po R50-U1/U8 nieużywane (bossy ramy i uchwytów usunięte); słupki blatu mają blat_post_hole_depth"},
    "insert_depth_m25": {"value": 5,    "status": "ZALOZENIE", "zrodlo": "R49"},
    "vent_slot_w":      {"value": 12,   "status": "ZALOZENIE", "zrodlo": "D14"},
    "vent_slot_h":      {"value": 3,    "status": "ZALOZENIE", "zrodlo": "D14"},
    "vent_slot_z":      {"value": 8,    "status": "ZALOZENIE", "zrodlo": "D14"},
    "vent_slots_rear_x":  {"value": [-54, -18, 18, 54], "status": "ZALOZENIE", "zrodlo": "R50-U19", "opis": "4 szczeliny tylne, rozstaw 36; bez daszków (R50-U4)"},
    "vent_slots_side_y":  {"value": [-36, 0, 36], "status": "ZALOZENIE", "zrodlo": "R50-U19", "opis": "3 szczeliny na ścianę boczną"},
    "floor_vent_l":     {"value": 30,   "status": "ZALOZENIE", "zrodlo": "R50-U19", "opis": "wlot 30 x 4 w dnie, 2 szt., pod środkiem Pi"},
    "floor_vent_w":     {"value": 4,    "status": "ZALOZENIE", "zrodlo": "R50-U19"},
    "floor_vent_x":     {"value": -8,   "status": "ZALOZENIE", "zrodlo": "R50-6", "opis": "środek Pi po R50-6 (x -50..35)"},
    "floor_vent_y":     {"value": [-10, 10], "status": "ZALOZENIE", "zrodlo": "D14"},
    "foot_d":           {"value": 10,   "status": "ZALOZENIE", "zrodlo": "zakup", "opis": "stopka samoprzylepna na płaskim dnie (gniazda usunięte R50-U16); bryła zastępcza"},
    "foot_h":           {"value": 4,    "status": "SPEC"},
    "foot_edge_offset": {"value": 12,   "status": "ZALOZENIE", "zrodlo": "4.3", "opis": "środek stopki 12 od krawędzi (tylko bryła zastępcza)"},
    "dc_hole_d":        {"value": 12,   "status": "ZALOZENIE", "zrodlo": "R50-3", "opis": "otwór w prawej ścianie skrzynki; gniazdo ø8 przez tulejkę redukcyjną (dc_bush_*)"},
    "dc_socket_axis":   {"value": "X",  "status": "ZALOZENIE", "zrodlo": "R50-3", "opis": "oś gniazda wzdłuż X; flansza wewnątrz kieszeni, nakrętka od wnętrza obudowy (x > -40); korpus gniazda w +X"},
    "dc_pos_x":         {"value": -40,  "status": "ZALOZENIE", "zrodlo": "R50-3", "opis": "płaszczyzna zewnętrzna prawej ściany skrzynki (ściana x -42..-40)"},
    "dc_pos_y":         {"value": 89,   "status": "ZALOZENIE", "zrodlo": "R50-3", "opis": "oś gniazda w ścianie skrzynki (y)"},
    "dc_pos_z":         {"value": 30,   "status": "ZALOZENIE", "zrodlo": "Z27/R50-3"},
    "dc_pocket_w":      {"value": 51,   "status": "ZALOZENIE", "zrodlo": "R50-4", "opis": "okno w tylnej ścianie x -93..-42; skrzynka x -97,5..-40 (lewa ściana skrzynki = ściana korpusu)"},
    "dc_pocket_x_window": {"value": -67.5, "status": "ZALOZENIE", "zrodlo": "R50-4", "opis": "środek okna w tylnej ścianie"},
    "dc_pocket_h":      {"value": 24,   "status": "ZALOZENIE", "zrodlo": "Z27", "opis": "dolna krawędź otworu Z 14"},
    "dc_pocket_z0":     {"value": 14,   "status": "ZALOZENIE", "zrodlo": "Z27"},
    "dc_pocket_depth":  {"value": 22,   "status": "ZALOZENIE", "zrodlo": "R50-3", "opis": "skrzynka do y 78 (w świetle 20); nie zależy od wtyku (wtyk wzdłuż X)"},
    "dc_pocket_wall":   {"value": 2,    "status": "ZALOZENIE", "zrodlo": "Z27/R31"},
    "dc_pocket_corner_r": {"value": 0,  "status": "ZALOZENIE", "zrodlo": "R50-U15", "opis": "naroża okna ostre"},
    "usb_cut_w":        {"value": 16,   "status": "ZALOZENIE", "zrodlo": "R50-5", "opis": "okno pod największe typowe gniazdo USB-A z ramką; zakryte flanszą"},
    "usb_cut_h":        {"value": 9,    "status": "ZALOZENIE", "zrodlo": "R50-5"},
    "usb_hole_pitch":   {"value": 22,   "status": "DO_ZMIERZENIA", "pomiar": 17, "opis": "używane tylko przez bryłę zastępczą flanszy; korpus ma rowki usb_slot_*"},
    "usb_slot_pitch_min": {"value": 23, "status": "ZALOZENIE", "zrodlo": "R50-5", "opis": "23 (nie 20): koniec rowka 50,1 vs okno 52 -> ścianka 1,9 >= 1,5; flansza o rozstawie 22 -> spiłować 0,5"},
    "usb_slot_pitch_max": {"value": 28, "status": "ZALOZENIE", "zrodlo": "R50-5", "opis": "rowki poziome 3,2 x 5,7, osie od usb_pos_x ± 11,5 do ± 14, Z usb_pos_z; flansza z otworami pionowymi -> wiercenie (fallback)"},
    "usb_slot_w":       {"value": 3.2,  "status": "ZALOZENIE", "zrodlo": "R50-5", "opis": "= usb_hole_d"},
    "usb_hole_d":       {"value": 3.2,  "status": "ZALOZENIE", "zrodlo": "4.3"},
    "usb_pos_x":        {"value": 60,   "status": "ZALOZENIE", "zrodlo": "R10"},
    "usb_pos_z":        {"value": 24,   "status": "ZALOZENIE"},
    "usb_body_depth":   {"value": 20,   "status": "ZALOZENIE", "zrodlo": "R10", "opis": "korpus gniazda wewnątrz od ściany (strefa kolizji 16 x 20 x 14)"},
    "usb_body_w":       {"value": 16,   "status": "ZALOZENIE", "zrodlo": "R47"},
    "usb_body_h":       {"value": 14,   "status": "ZALOZENIE", "zrodlo": "R47"},
    "dc_socket_body_d": {"value": 12,   "status": "ZALOZENIE", "zrodlo": "R47/R50-3", "opis": "bryła zastępcza gniazda DC za nakrętką: walec osią X od x -40 w +X, oś (y 89, Z 30)"},
    "dc_socket_body_l": {"value": 18,   "status": "DO_ZMIERZENIA", "pomiar": 16, "zrodlo": "R50-3", "opis": "długość korpusu gniazda za nakrętką (proxy); wolne 50 w +X, korpus od tego niezależny"},
    "dc_nut_d":         {"value": 15,   "status": "ZALOZENIE", "zrodlo": "R47", "opis": "nakrętka, grubość 2, na ścianie x -40 od strony wnętrza"},
    "label_text_h":     {"value": 8,    "status": "ZALOZENIE", "zrodlo": "D15"},
    "label_relief_h":   {"value": 0.6,  "status": "SPEC"},
    "label_pos_z":      {"value": 51,   "status": "LICZONE", "wzor": "korpus_h - 8.6", "zrodlo": "D15/R50-1", "opis": "środek napisu 8,6 pod górną krawędzią korpusu"},
    "snap_pocket_w":    {"value": 11,   "status": "ZALOZENIE", "zrodlo": "D9/R53", "opis": "R53 (T3c): 10 -> 11; luz boczny haczyka 8 -> 1,5/stronę (położenie ±0,3 obu części)"},
    "snap_pocket_h":    {"value": 3.5,  "status": "ZALOZENIE", "zrodlo": "D9/R53", "opis": "R53 (T3a): 2,5 -> 3,5; kieszeń Z 52,1..55,6, występ haczyka 52,85..54,85 -> luz Z 0,75 pod i nad (>= ±0,3 + ±0,3)"},
    "snap_pocket_depth": {"value": 1.3, "status": "ZALOZENIE", "zrodlo": "R6/R53", "opis": "R53 (T2b): 1,0 -> 1,3; dno kieszeni 98,8, luz czubek haczyka (98,3) - dno 0,5; ściana za kieszenią 1,2 lokalnie (odstępstwo od 4.8, nienośna)"},
    "snap_pocket_z":    {"value": 52.1, "status": "LICZONE", "wzor": "korpus_h - 7.5", "zrodlo": "D9/R50-1/R53", "opis": "dolna krawędź kieszeni zatrzasku; R53 (T3b): korpus_h - 7 -> korpus_h - 7,5 (kieszeń 3,5 symetrycznie wokół występu 52,85..54,85)"},
    "snap_side_y":      {"value": 0,    "status": "ZALOZENIE", "zrodlo": "R6"},
    "snap_front_x":     {"value": 50,   "status": "ZALOZENIE", "zrodlo": "R6"},
    "snap_rear_x":      {"value": -50,  "status": "ZALOZENIE", "zrodlo": "R6"},
    "blat_screw_pitch": {"value": 150,  "status": "ZALOZENIE", "zrodlo": "R7"},
    "blat_screw_z":     {"value": 55,   "status": "LICZONE", "wzor": "korpus_h - 4.6", "zrodlo": "D9/R50-1", "opis": "oś wkrętów blatu w tylnej ścianie i w słupkach"},
    "blat_screw_hole_d": {"value": 3.6, "status": "ZALOZENIE", "zrodlo": "4.3/R53", "opis": "R53 (T4): 3,2 -> 3,6 (przelot M3 klasa coarse; luz 0,3/stronę = położenie ±0,3 korpusu + ±0,3 słupka blatu na rozstawie 150); pogłębienie 6,3 bez zmian"},
    "blat_screw_csink_d": {"value": 6.3, "status": "ZALOZENIE", "zrodlo": "R47", "opis": "pogłębienie stożkowe 90°"},
    "tab_root_x_out":   {"value": 52.4, "status": "ZALOZENIE", "zrodlo": "R51/R53", "opis": "nasada L: x 44..52,4 od y 48,8; x 52,4..65 dopiero od y 52,4 (= krawędź ramy insert_opening/2 + 4; R53 T6b)"}
  },

  "blat_rama_wkladka": {
    "blat_t":               {"value": 4,     "status": "ZALOZENIE", "zrodlo": "D9"},
    "blat_skirt_h":         {"value": 10,    "status": "ZALOZENIE", "zrodlo": "D9"},
    "blat_skirt_t":         {"value": 2,     "status": "ZALOZENIE", "zrodlo": "D9"},
    "blat_skirt_clearance": {"value": 0.7,   "status": "ZALOZENIE", "zrodlo": "R48/R53", "opis": "kołnierz 193,6 w 195 (0,7/stronę); R53 (T1): 0,5 -> 0,7 = ±0,3 korpus + ±0,3 blat + zapas na wypaczenie ścian"},
    "blat_corner_r":        {"value": 5,     "status": "SPEC"},
    "blat_top_edge_r":      {"value": 1.5,   "status": "ZALOZENIE", "zrodlo": "4.4"},
    "snap_hook_w":          {"value": 8,     "status": "ZALOZENIE", "zrodlo": "D9"},
    "snap_hook_h":          {"value": 1.5,   "status": "ZALOZENIE", "zrodlo": "R48/R53", "opis": "występ 96,8 -> 98,3; zahacza 0,8 w kieszeni 97,5..98,8 (R53 T2a: 1,3 -> 1,5, czubek 98,3 bez zmian przy luzie kołnierza 0,7)"},
    "snap_hook_t":          {"value": 1.5,   "status": "ZALOZENIE", "zrodlo": "D9"},
    "snap_hook_arm_l":      {"value": 9,     "status": "ZALOZENIE", "zrodlo": "R47", "opis": "nacięcia od dołu kołnierza do Z 53,6"},
    "snap_hook_z":          {"value": 52.85, "status": "LICZONE", "wzor": "korpus_h - 6.75", "zrodlo": "R47/R50-1", "opis": "dolna krawędź występu haczyka (globalnie); lokalnie -10,75 bez zmian"},
    "snap_hook_hgt":        {"value": 2.0,   "status": "ZALOZENIE", "zrodlo": "R47"},
    "snap_notch_w":         {"value": 1,     "status": "ZALOZENIE", "zrodlo": "R47"},
    "blat_post_y0":         {"value": 89.2,  "status": "ZALOZENIE", "zrodlo": "R47", "opis": "słupek y 89,2..95,2"},
    "blat_post_hole_depth": {"value": 6,     "status": "ZALOZENIE", "zrodlo": "R49a", "opis": "otwór ø2,5 od lica 97,0 do 91,0; dno 1,8"},
    "blat_post_size":       {"value": 6,     "status": "ZALOZENIE", "zrodlo": "4.4", "opis": "słupek: wymiar w Y (89,2..95,2)"},
    "blat_post_w":          {"value": 8,     "status": "ZALOZENIE", "zrodlo": "R48", "opis": "słupek: wymiar w X (x ±71..79)"},
    "blat_rib":             {"value": false, "status": "ZALOZENIE", "zrodlo": "R41", "opis": "bez żebra obwodowego pod blatem; po R50-U1 także bez bossów ramy (spód blatu płaski poza kołnierzem i słupkami)"},
    "insert_opening":       {"value": 96.8,  "status": "SPEC", "zrodlo": "spec/R53", "opis": "R53 (T6): 96,6 -> 96,8; luz płytki 0,4/stronę (płytka ±0,29 + wkładka ±0,29 MJF); interfejs płytki bez zmian"},
    "insert_wall_w":        {"value": 4,     "status": "SPEC"},
    "insert_h":             {"value": 6,     "status": "ZALOZENIE", "zrodlo": "Z7"},
    "insert_chamfer":       {"value": 1,     "status": "ZALOZENIE", "zrodlo": "4.6"},
    "insert_shelf":         {"value": 12,    "status": "ZALOZENIE", "zrodlo": "D5"},
    "insert_shelf_h":       {"value": 2.5,   "status": "ZALOZENIE", "zrodlo": "D5"},
    "hall_pocket_w":        {"value": 5.0,   "status": "ZALOZENIE", "zrodlo": "D5"},
    "hall_pocket_l":        {"value": 5.5,   "status": "ZALOZENIE", "zrodlo": "D5"},
    "hall_lead_channel_w":  {"value": 2.5,   "status": "ZALOZENIE", "zrodlo": "D5"},
    "hall_lead_channel_h":  {"value": 1.0,   "status": "ZALOZENIE", "zrodlo": "R20"},
    "hall_wall_pass_h":     {"value": 1.5,   "status": "ZALOZENIE", "zrodlo": "4.6/R47/R50-U9", "opis": "przelot 2,5 x 1,5 w ściance ramy po przekątnej narożnika; JEDNA bryła tnąca ciągła z rowkiem zewnętrznym (wire_rabbet_w x wire_rabbet)"},
    "hall_sensor_size":     {"value": [4, 5, 1.5], "status": "ZALOZENIE", "zrodlo": "R47", "opis": "bryła zastępcza czujnika Halla"},
    "insert_opening_r":     {"value": 0,     "status": "ZALOZENIE", "zrodlo": "R50-U15", "opis": "naroża otworu wkładki ostre (płytka ma R 1, luz 0,4 po R53)"},
    "orient_post":          {"value": 4.4,   "status": "ZALOZENIE", "zrodlo": "D5"},
    "orient_post_h":        {"value": 5,     "status": "ZALOZENIE", "zrodlo": "D5"},
    "orient_post_gap":      {"value": 0.6,   "status": "ZALOZENIE", "zrodlo": "D5/R53", "opis": "R53 (T6c): 0,5 -> 0,6, żeby kołek został w (45,6; -45,6) jak przed R53 (otwór 96,8): przy 0,5 naroże kołka (47,9) zahaczało o R 1,5 wnęki pokrywki o 0,059 mm (trzecie oko R53)"},
    "orient_post_chamfer":  {"value": 1,     "status": "ZALOZENIE", "zrodlo": "4.6"},
    "finger_cut_w":         {"value": 30,    "status": "SPEC"},
    "tab_w":                {"value": 14,    "status": "ZALOZENIE", "zrodlo": "D12"},
    "tab_end_y":            {"value": 96,    "status": "ZALOZENIE", "zrodlo": "D12"},
    "tab_t":                {"value": 3,     "status": "ZALOZENIE", "zrodlo": "D12"},
    "tab_pos_x":            {"value": 58,    "status": "ZALOZENIE", "zrodlo": "D12"},
    "tab_pin_d":            {"value": 3,     "status": "ZALOZENIE", "zrodlo": "D12"},
    "tab_pin_h":            {"value": 3.5,   "status": "ZALOZENIE", "zrodlo": "D12"},
    "tab_pin_y":            {"value": 93.5,  "status": "ZALOZENIE", "zrodlo": "D12"},
    "tab_pin_chamfer":      {"value": 0.5,   "status": "ZALOZENIE", "zrodlo": "4.6/R50-U10", "opis": "kołek jako jedna bryła: walec ø3 x 3,0 + stożek ścięty ø3,0 -> ø2,0 na ostatnich 0,5 (bez osobnej bryły fazy)"},
    "tab_root_x_in":        {"value": 44,    "status": "ZALOZENIE", "zrodlo": "R47", "opis": "nasada ucha x od 44 do 65"},
    "tab_root_y0":          {"value": 48.8,  "status": "ZALOZENIE", "zrodlo": "R47"},
    "tab_root_y1":          {"value": 58,    "status": "ZALOZENIE", "zrodlo": "R47"},
    "tab_magnet_y":         {"value": 86,    "status": "ZALOZENIE", "zrodlo": "D12"},
    "tab_magnet_hole_d":    {"value": 5.4,   "status": "ZALOZENIE", "zrodlo": "D12"},
    "tab_cable_channel_w":  {"value": 2,     "status": "ZALOZENIE", "zrodlo": "D12"},
    "tab_cable_channel_h":  {"value": 1.2,   "status": "ZALOZENIE", "zrodlo": "D12"},
    "tab_cable_channel_x":  {"value": 64,    "status": "ZALOZENIE", "zrodlo": "D12"},
    "blat_pin_hole_d":      {"value": 3.4,   "status": "ZALOZENIE", "zrodlo": "D12/R53", "opis": "R53 (T5): 3,3 -> 3,4; kołek ø3 pasowanie ruchome 0,2 (było wciskane 0,15); otwory MJF -0,1..-0,2; wkładkę trzymają magnesy"},
    "blat_pin_hole_depth":  {"value": 3.8,   "status": "ZALOZENIE", "zrodlo": "R8"},
    "blat_magnet_pocket_d": {"value": 5.4,   "status": "ZALOZENIE", "zrodlo": "D12"},
    "blat_magnet_pocket_depth": {"value": 2.3, "status": "ZALOZENIE", "zrodlo": "D12"},
    "wire_slot_l":          {"value": 8,     "status": "ZALOZENIE", "zrodlo": "D12"},
    "wire_slot_w":          {"value": 4,     "status": "ZALOZENIE", "zrodlo": "D12"},
    "wire_slot_x":          {"value": 66,    "status": "ZALOZENIE", "zrodlo": "D12"},
    "wire_slot_y":          {"value": 90,    "status": "ZALOZENIE", "zrodlo": "D12"},
    "wire_rabbet":          {"value": 1.5,   "status": "ZALOZENIE", "zrodlo": "D12", "opis": "wysokość rowka kablowego na zewnętrznej dolnej krawędzi ramy"},
    "wire_rabbet_w":        {"value": 2.5,   "status": "ZALOZENIE", "zrodlo": "R50-U9", "opis": "szerokość rowka (od x 52,3 do 49,8; do otworu 48,3 zostaje 1,5); ten sam przekrój co przelot w ściance"}
  },

  "male_czesci": {
    "receiver_l":      {"value": 19,  "status": "DO_ZMIERZENIA", "pomiar": 14, "opis": "tylko bryła zastępcza w porcie USB Pi (korpus P)"},
    "receiver_w":      {"value": 15,  "status": "DO_ZMIERZENIA", "pomiar": 14},
    "receiver_h":      {"value": 6,   "status": "DO_ZMIERZENIA", "pomiar": 14},
    "dc_bush_outer_d": {"value": 11.85,  "status": "ZALOZENIE", "zrodlo": "R50-3/R52", "opis": "tulejka redukcyjna gniazda DC: średnica zewnętrzna = dc_hole_d − 0,15 (pasowanie wciskane 0,1–0,15 wg 4.8; trzecie oko U1)"},
    "dc_bush_inner_d": {"value": 8.2, "status": "ZALOZENIE", "zrodlo": "R50-3", "opis": "otwór pod gniazdo z gwintem ø8"},
    "dc_bush_t":       {"value": 2,   "status": "ZALOZENIE", "zrodlo": "R50-3", "opis": "długość części walcowej (= dc_pocket_wall)"},
    "dc_bush_flange_d": {"value": 15, "status": "ZALOZENIE", "zrodlo": "R50-3", "opis": "kołnierz po stronie kieszeni"},
    "dc_bush_flange_t": {"value": 1,  "status": "ZALOZENIE", "zrodlo": "R50-3"},
    "panel_shim_d":    {"value": 9,   "status": "ZALOZENIE", "zrodlo": "R50-8", "opis": "podkładka dystansowa panelu (krążek)"},
    "panel_shim_hole_d": {"value": 3.4, "status": "ZALOZENIE", "zrodlo": "R50-8"},
    "panel_shim_t":    {"value": [0.5, 1, 2], "status": "ZALOZENIE", "zrodlo": "R50-8", "opis": "trzy grubości -> trzy STL (ramka_podkladka_panelu_05/_1/_2)"}
  },

  "sterowanie": {
    "file_suffix":          {"value": "v2", "status": "ZALOZENIE", "zrodlo": "R17"},
    "label_text_W":         {"value": "RAMKA WIECZORNA", "status": "ZALOZENIE", "zrodlo": "Z18"},
    "label_text_P":         {"value": "RAMKA PORANNA", "status": "ZALOZENIE", "zrodlo": "Z18"},
    "insert_label_text":    {"value": "PRZÓD", "status": "ZALOZENIE", "zrodlo": "4.6"},
    "insert_label_h":       {"value": 0,     "status": "ZALOZENIE", "zrodlo": "R51", "opis": "0 = bez napisu PRZÓD; tylko strzałki"},
    "insert_label_x":       {"value": 32,    "status": "ZALOZENIE", "zrodlo": "R47"},
    "insert_label_y":       {"value": -51.15, "status": "ZALOZENIE", "zrodlo": "R47"},
    "insert_arrow_x":       {"value": [-32, 32], "status": "ZALOZENIE", "zrodlo": "R47/R51", "opis": "środki strzałek na obu segmentach"},
    "insert_arrow_l":       {"value": 2,     "status": "ZALOZENIE", "zrodlo": "R47", "opis": "trójkąt ▼, wymiar wzdłuż Y"},
    "insert_arrow_w":       {"value": 3,     "status": "ZALOZENIE", "zrodlo": "R47", "opis": "trójkąt ▼, wymiar wzdłuż X"},
    "font_name":            {"value": "Inter", "status": "ZALOZENIE", "zrodlo": "R22", "opis": "datafiles/fonts/Inter.woff2 z instalacji Blendera 5.2"},
    "font_offset":          {"value": 0.2,   "status": "ZALOZENIE", "zrodlo": "R22", "opis": "TextCurve.offset; trzon litery >= 1,0 mm"},
    "fillet_outer_default": {"value": 3,   "status": "ZALOZENIE", "zrodlo": "R26"},
    "fillet_inner_default": {"value": 1,   "status": "ZALOZENIE", "zrodlo": "R26"},
    "color_graphite":       {"value": "#3b3e43", "status": "ZALOZENIE", "zrodlo": "R27"},
    "color_white":          {"value": "#efede6", "status": "ZALOZENIE", "zrodlo": "R27"},
    "color_plexi":          {"value": "#e8ecef", "status": "ZALOZENIE", "zrodlo": "R27", "opis": "pleksi mleczna, półprzezroczysta"},
    "color_pcb":            {"value": "#1f6b3a", "status": "ZALOZENIE", "zrodlo": "R27"},
    "color_brass":          {"value": "#c8a24a", "status": "ZALOZENIE", "zrodlo": "R27", "opis": "dystanse"},
    "cost_rate_min":        {"value": 0.9, "status": "ZALOZENIE", "zrodlo": "sekcja 11"},
    "cost_rate_max":        {"value": 1.6, "status": "ZALOZENIE", "zrodlo": "sekcja 11"},
    "cost_dye_factor":      {"value": 1.2, "status": "ZALOZENIE", "zrodlo": "sekcja 11"},
    "cost_smooth_factor":   {"value": 1.3, "status": "ZALOZENIE", "zrodlo": "sekcja 11"},
    "quantities": {"value": {
        "ramka_plytka_wieczorna_n1": 1, "ramka_plytka_wieczorna_n2": 1, "ramka_plytka_wieczorna_n3": 1,
        "ramka_plytka_poranna_n4": 1, "ramka_plytka_poranna_n5": 1, "ramka_plytka_poranna_n6": 1,
        "ramka_pokrywka": 4, "ramka_korpus_W": 1, "ramka_korpus_P": 1, "ramka_blat": 2,
        "ramka_wkladka": 3,
        "ramka_tulejka_dc": 2,
        "ramka_podkladka_panelu_05": 8, "ramka_podkladka_panelu_1": 8, "ramka_podkladka_panelu_2": 8
      }, "status": "ZALOZENIE", "zrodlo": "R36/Z28/R50-U1/R50-U8/R50-3/R50-8", "opis": "rama dyfuzora i uchwyt kabli usunięte; tulejka i podkładki to druk własny (poza arkuszem drukarni)"},
    "materials": {"value": {
        "ramka_plytka_wieczorna_n1": "PA12 drukarnia (alt. żywica firma)", "ramka_plytka_wieczorna_n2": "PA12 drukarnia (alt. żywica firma)", "ramka_plytka_wieczorna_n3": "PA12 drukarnia (alt. żywica firma)",
        "ramka_plytka_poranna_n4": "PA12 drukarnia", "ramka_plytka_poranna_n5": "PA12 drukarnia", "ramka_plytka_poranna_n6": "PA12 drukarnia",
        "ramka_pokrywka": "PETG FDM (własny)", "ramka_korpus_W": "PA12 drukarnia", "ramka_korpus_P": "PA12 drukarnia", "ramka_blat": "PA12 drukarnia",
        "ramka_wkladka": "PA12 drukarnia",
        "ramka_tulejka_dc": "żywica firma / PETG",
        "ramka_podkladka_panelu_05": "żywica firma / PETG", "ramka_podkladka_panelu_1": "żywica firma / PETG", "ramka_podkladka_panelu_2": "żywica firma / PETG"
      }, "status": "ZALOZENIE", "zrodlo": "Z19/D2/R50", "opis": "kolory: korpus, blat grafit; wkładka, płytki, pokrywka naturalny biały (jak Z19); K-57 liczy koszt tylko dla pozycji 'PA12 drukarnia'"}
  }
}
```
