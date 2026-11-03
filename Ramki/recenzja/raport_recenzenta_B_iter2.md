# Raport recenzenta — etap B, iteracja 2

Plik: `recenzja/raport_recenzenta_B_iter2.md`. Pomiary własnym skryptem `recenzja/sprawdz_B.py` (uruchomienie: `"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b -P recenzja/sprawdz_B.py -- --iter 2`) oraz `recenzja/sprawdz_B_kanaly.py` (sprawdzenie dodatkowe). Wyniki: `recenzja/wyniki_B_iter2.json` (67 sprawdzeń, 413 sond, 49 par K‑53), `recenzja/wyniki_B_iter2_kanaly.json`, log `recenzja/log_B_iter2.txt`, rzuty `recenzja/relief_ramka_wkladka_v2_strzalki.png`, `recenzja/relief_ramka_korpus_{W,P}_v2_napis.png`, `recenzja/spod_wkladki_kanaly.png`.
Iteracji 1 etapu B nie recenzowałem (właściciel przekazał od razu iterację 2 po R51).

## 0. Werdykt
**ETAP B: ZALICZONY** — B = 0, P = 0, D = 0. Wykonane: K‑01…K‑04b (5 STL etapu B), K‑23…K‑25, K‑27…K‑40, K‑42…K‑49, K‑44b, K‑33, K‑53 (pary zestawu złożonego), K‑54, K‑55, K‑56; brak N/D. Części złożeniowe K‑22 i K‑32 zamknięte przez K‑53 (pary pokrywka–wkładka i płytka n1–wkładka = 0 przecięć).

## 1. Niezależność pomiaru
- SHA‑256 zgodne z raportem wykonawcy (sekcja 2): **TAK** — `ramka_wkladka_v2`, `ramka_rama_dyfuzora_v2`, `ramka_blat_v2`, `ramka_korpus_W_v2`, `ramka_korpus_P_v2`, `ramka_v2.blend`, oraz niezmienione pliki etapu A (`…_n1_v2`, `ramka_pokrywka_v2`): 8/8; rozmiary zgodne.
- Skrypt recenzenta napisany bez czytania `ramka_generator.py`: **TAK** (kodu wykonawcy nie otwierano; trzy pierwsze wyniki NIE w moim przebiegu były błędami mojego pomiaru — promień przez wycięcie palcowe, pomiar szerokości wewnętrznej zamiast zewnętrznej kołnierza, błędny początek promienia — poprawione w skrypcie, część bez zmian).
- Metoda sond jak w etapie A; sond niestabilnych **0 / 413**; najmniejsza odległość sondy od ściany 0,10 (K‑23 (49,5, 0, 5,9), K‑34 (98,75, 0, 54,7), K‑48 (82, 0, 10,1) — wszystkie zgodne z protokołem, stabilne).
- Transformacje: wkładka (−cx, −(y_min + 52,3), −(z_min + 3,5)); rama (−cx, −cy, −z_min); blat: przesunięcie z_min → 0, potem obrót 180° wokół X; korpus: z_min → 0, środek Y z obrysu dna (Z ≈ 0), nie z obrysu z daszkami. Surowe STL: wkładka X ±65, Y −52,3…96, Z 0…11; rama ±94, Z 0…10; blat ±100, Z 0…14; korpusy X ±102, Y −100,6…102, Z 0…54,6 — zgodne z tabelą 1. Test rozpoznawczy osi eksportu blatu nie był potrzebny (K‑47 ZAL bez obrotu Rz).
- `.blend`: 34 obiekty w kolekcjach `plytki`, `obudowa`, `akcesoria`, `elementy_kupowane`; zestaw złożony 24 obiekty (|x|,|y| ≤ 150); odsunięte: `korpus_P` (x 158…362), 7 płytek wariantowych/bazowych (y −308…−212), `proxy_magnes_B/C` (w n6), `proxy_odbiornik_usb` (w korpusie P) — najmniejsza |współrzędna| odsuniętych 158 ≥ 150, odsunięcie środków ≥ 260.

## 2. Wyniki sprawdzeń
| Id | Wynik | Zmierzone przez recenzenta | Zadeklarowane przez wykonawcę | Oczekiwane | Waga | Uwaga |
|---|---|---|---|---|---|---|
| K‑01 | ZAL | trójkąty: wkładka 2242, rama 1244, blat 7978, korpus W 23610, korpus P 22714; NaN brak | identycznie | > 100 | B | |
| K‑02 | ZAL | wkładka 130,000 × 148,300 × 11,000 (Z montażowe −3,5…7,5); rama 188,000 × 188,000 × 10,000; blat 200,000 × 200,000 × 14,000 (Z −14…0); korpus W/P 204,000 × 202,600 × 54,600 | identycznie | tabela 1 ± 0,1 | B | |
| K‑03 | ZAL | 5 × (0 / 0 / 0) | 0/0/0 | 0/0/0 | B | |
| K‑04 | ZAL | 5 × 1 składowa | 1 | 1 | B | |
| K‑04b | ZAL | wkładka 12,831; rama 20,378; blat 73,640; korpus W 225,658; korpus P 225,629 cm³ | 12,83 / 20,38 / 73,64 / 225,66 / 225,63 | 16 / 20 / 85 / 215 ± 30 % | B | |
| K‑23 | ZAL | 10/10 (6 z protokołu + lewy/tylny bok) | 6/6 | tak | B | |
| K‑24 | ZAL | 7/7 | 7/7 | tak | B | |
| K‑25 | ZAL | 16/16 (A z protokołu + kanały i przeloty B, C) | 8/8 | tak | B | |
| K‑27 | ZAL | 4/4 | 4/4 | tak | B | |
| K‑28 | ZAL | 4/4 | 4/4 | tak | B | |
| K‑29 | ZAL | 38/38 (sondy R51 na obu uszach: nasada L, kanał pod nasadą, kołki, otwory magnesów, kanał x = ±64, koniec ucha) | 20/20 | tak | B | |
| K‑30 | ZAL | 5/5 | 5/5 | tak | P | |
| K‑31 | ZAL | strzałki: max Z lewa 6,600, prawa 6,600; pas y −50,0…−48,3 max 6,000; rzut PNG: dwa trójkąty ▼ na obu segmentach, poza wycięciem palcowym | 6,600 / 6,000 | 6,6 ± 0,05 / 6,0 ± 0,05 | P | |
| K‑32 | ZAL | otwór z promieni X 96,600, Y 96,600; para płytka n1–wkładka w K‑53: 0 | 96,6; 0 | 96,6 ± 0,2; 0 | B | |
| K‑33 | ZAL | min Z wkładki poza kołkami 58,600; wierzch dyfuzora 58,600; kołki (±58, 93,5) w otworach blatu 4/4; wkładka–blat, wkładka–dyfuzor: 0 (K‑53) | identycznie | 58,6 ± 0,02; 0 | B | |
| K‑34 | ZAL | W 9/9, P 9/9 | 9/9 | tak | B | |
| K‑35 | ZAL | W 12/12, P 12/12 (9 z protokołu + pozostałe otwory panelu i drugi wlot) | 9/9 | tak | B | |
| K‑36 | ZAL | W 14/14, P 14/14 (10 z protokołu + osie 3 pozostałych bossów Pi i bossa (−20, 75)) | 10/10 | tak | B | |
| K‑37 | ZAL | W 27/27, P 27/27 (10 z protokołu + wszystkie 20 szczelin na osi Z 8) | 10/10 | tak | B | |
| K‑38 | ZAL | W 17/17, P 17/17 (13 z protokołu + krawędzie otworu kieszeni x −78 i Z 38) | 13/13 | tak | B | |
| K‑39 | ZAL | W 11/11, P 11/11 (7 z protokołu + krawędzie okna USB 52,5/67,5 i Z 20) | 7/7 | tak | B | |
| K‑40 | ZAL | W i P: 7/7 sond; 390 promieni, trafienia y ∈ [−100,600, −100,000], 0 poza zakresem | identycznie | brak przelotu | B | |
| K‑42 | ZAL | W 11/11, P 11/11 | 11/11 | tak | B | |
| K‑43 | ZAL | W i P: min Y (x ±45, Z 41…51) −100,600; (Z 30…36) −100,000; SHA różne; objętość W − P = 0,0291 cm³; rzuty PNG: „RAMKA WIECZORNA” (W), „RAMKA PORANNA” (P), litery niezlustrzane | −100,600 / −100,000; 0,029 | −100,6 ± 0,05 / −100,0; ≠; < 0,5 | B | |
| K‑44 | ZAL | W 11/11, P 11/11 (6 z protokołu + żebro (66, 66) od krawędzi podkładki, żebro (−75, −75), 3 pozostałe gniazda stopek) | 6/6 | tak | P | |
| K‑44b | ZAL | przecięcia korpus–Pi 0, korpus–wtyk 0, panel–Pi 0, panel–wtyk 0; luz Z 37,000 − 34,000 = 3,000; Pi X −92…−7, Y ±28, Z 8…34; wtyk X −65…−55, Y −43…−28, Z 23…34 | identycznie | 0 / ≥ 3 | B | |
| K‑45 | ZAL | 6/6 | 6/6 | tak | B | |
| K‑46 | ZAL | 14/14 (R48: kołnierz 95,0…97,0, haczyk do 98,3) | 14/14 | tak | B | |
| K‑47 | ZAL | 41/41 (sondy protokołu na obu słupkach, obu kołkach/magnesach/szczelinach i 4 bossach); dno otworów kołków: z góry −3,800, z dołu −4,000 (oba) | 18/18; −3,8 / −4,0 | tak | B | |
| K‑48 | ZAL | 26/26 (14 z protokołu + otwory i łapy 3 pozostałych narożników) | 14/14 | tak | B | |
| K‑49 | ZAL | wnętrze korpusu 195,000 × 195,000; kołnierz blatu zewn. 194,000 × 194,000 → 0,500/stronę; rama wewn. 161,000 vs panel 160,000 → 0,500; kieszeń 162,000 vs dyfuzor 160,000 → 1,000; wierzch łap ramy 48,600 = spód bossów blatu 48,600; przecięcia rama–blat 0, rama–panel 0, blat–korpus 0 | identycznie | 0,5 / 0,5 / 1,0; 48,6; 0 | B | |
| K‑53 | ZAL | 24 obiekty zestawu złożonego; 49 par z nakładającymi się bbox sprawdzone po skurczu −0,05 (pozostałe 227 par rozłączne już w bbox): 0 par z przecięciem; w tym pary stykowe rama–blat, wkładka–dyfuzor, płytka n1–wkładka, płytka n1–półki, pokrywka–wkładka, Pi–bossy | 276 par, 0 przecięć | 0 | B | |
| K‑54 | ZAL | blat (90,0) 58,600; dyfuzor (0,70) 58,600; wkładka (0,50,3) 64,600, max Z 66,100; płytka n1 (0,−46,5) 69,100, relief 69,700; pokrywka (40,40) 85,100, max 85,700, min 65,100; Pi max 34,000; panel min 37,000, PCB 49,000…50,600; stopki −4,000…0,000; blat 44,6…58,6; korpus 0…54,6; rama 44,6…54,6; kołki wkładki do 55,100; płytka min 61,100 | identycznie | ± 0,05 | B | |
| K‑55 | ZAL | spód magnesu A 61,300 − wierzch Halla A 60,100 = 1,200; + 0,5 = 1,70 ≤ 4 | 1,200 | 1,2 ± 0,05 | B | |
| K‑56 | ZAL | krawędź wkładki przód y −52,300, prawa x 52,300 → pas przedni 27,700, prawy 27,700 → 11 pikseli; siatka 2 mm nad pasami (x −79…79 × y −79…−53; x 53…79 × y −79…51) nad Z 58,65: 0 trafień w żadną część poza dyfuzorem/panelem | 27,70 / 27,71; 11; 0 | 27,7 / 11 | B | prawy pas liczony w zasięgu Y ramy (−52,3…52,3); tylne narożniki y > 52,3 = strefa uszu dozwolona w D12 |

## 3. Uwagi do poprawy (tylko NIE), z numerami
| Nr uwagi | K‑xx | Waga | Plik / cecha | Co jest | Co ma być |
|---|---|---|---|---|---|
| — | — | — | brak sprawdzeń NIE | — | — |

## 4. Rozbieżności między raportem wykonawcy a pomiarem recenzenta
Brak. Liczby trójkątów, gabaryty, objętości (do 0,01 cm³), liczby sond protokołu, min Y reliefów, luzy K‑49, wartości K‑54/K‑55/K‑56 i wynik K‑53 identyczne. Moje liczby sond są większe tam, gdzie rozszerzyłem sondy na symetryczne cechy (drugi słupek, 4 bossy, 20 szczelin itd.) — wszystkie zgodne.

## 5. Ocena rejestru odstępstw wykonawcy
| # odstępstwa | Zasadne? | Wymaga decyzji właściciela? | Komentarz |
|---|---|---|---|
| 1 (grubość nakrętki DC = `dc_pocket_wall` 2,0) | TAK | NIE (przyjęte informacyjnie, R51) | wartość równa planowi; brak wpływu na STL (bryła zastępcza) |
| 2 (położenie `proxy_odbiornik_usb`: x −7…12, y ±7,5, Z 8…14 w korpusie P) | TAK | NIE (R51) | bryła zastępcza poza zestawem złożonym (korpus P odsunięty); do K‑53 nie wchodzi. **Uwaga do planu:** jeśli właściciel chce mieć kolizję odbiornika sprawdzoną, zestaw złożony musiałby zawierać korpus P z odbiornikiem — w obecnym kształcie pozycja odbiornika nie jest weryfikowana (sekcja 6, D). |

## 6. Lista drobnych (D) do v3
1. Odbiornik USB klawiatury (tylko P) leży poza testem K‑53 (korpus P odsunięty); jego zasięg x −7…12, Z 8…14 mija dystans panelu (−60…) i bossy Pi, ale nie jest to zmierzone. Propozycja v3: dodać proxy do zestawu złożonego W (jako „pozycja hipotetyczna”) albo osobną parę w K‑53.
2. Nazwy w `parametry.json`: `rama_ear_d` 8 / `rama_ear_t` 4 pozostają obok `rama_tab_size` 13 (R46) — klucz `rama_ear_d` nie opisuje już geometrii (łapa 13 × 13); kosmetyka dokumentacji.

## 7. Sprawdzenia dodatkowe (poza protokołem)
- **Ciągłość kanałów przewodów Halla w spodzie wkładki** (`sprawdz_B_kanaly.py`): mapa spodu promieniami z dołu (siatka 0,25 mm, 128 tys. promieni); komórka „kanał” = pierwsze trafienie na Z 0,9…1,7 nad płaszczyzną spodu. BFS po komórkach kanału: **A → (−64, 89): ciągły; B → (−64, 89): ciągły; C → (64, 89): ciągły** (głębokości kanałów na trasach 1,0…1,5). Rzut `recenzja/spod_wkladki_kanaly.png`: rowek na lewym, tylnym i prawym boku, brak na przednim; kanały po przekątnych A, B, C; narożnik D bez kanału; nasady L i kanały x = ±64 w uszach.
- K‑53 obejmuje parę pokrywka–wkładka (zamyka K‑22) i płytka n1–wkładka (zamyka K‑32): 0 przecięć.
- Sondy rozszerzone na wszystkie symetryczne wystąpienia cech (oba słupki, 4 bossy ramy i blatu, 20 szczelin wentylacyjnych, 4 gniazda stopek, 4 bossy Pi, oba uszy wkładki, kanały B i C).
