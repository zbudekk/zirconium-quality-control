# Raport recenzenta — etap B, iteracja 3 (po R50)

Plik: `recenzja/raport_recenzenta_B_iter3.md`. Pomiary własnym skryptem `recenzja/sprawdz_B.py` (przepisanym na geometrię R50; wersja z iteracji 2 zachowana jako `recenzja/sprawdz_B_iter2.py`; uruchomienie: `"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b -P recenzja/sprawdz_B.py -- --iter 3`) oraz `recenzja/sprawdz_B_kanaly.py`. Wyniki: `recenzja/wyniki_B_iter3.json` (73 sprawdzeń, 529 sond, 41 par K‑53), `recenzja/wyniki_B_iter3_kanaly.json`, log `recenzja/log_B_iter3.txt`, rzuty `recenzja/relief_ramka_wkladka_v2_strzalki.png`, `recenzja/relief_ramka_korpus_{W,P}_v2_napis.png`, `recenzja/spod_wkladki_kanaly.png`.
Przed pomiarem przeczytane: `R50_wdrozenie_zmiany.md`, aktualny `protokol_weryfikacji_v2.md` (tabela 1, K‑17…K‑56 po R50), `parametry.json` (273 klucze), plan v2 sekcje 4.2–4.6, 4.9, D4, D14. Żadne wyniki z iteracji 2 nie zostały użyte.

## 0. Werdykt
**ETAP B: ZALICZONY** — B = 0, P = 0, D = 0. Wykonane: K‑01…K‑04b dla 5 STL etapu (pokrywka po ponownym eksporcie, wkładka, blat, korpus W, korpus P) + potwierdzenie braku plików ramy i uchwytu; K‑17, K‑18, K‑20, K‑22 (pokrywka ponownie) z kontrolami odwrotnymi K‑19/K‑21; K‑23…K‑25, K‑27…K‑40, K‑42…K‑47, K‑44b, K‑33, K‑49, K‑53, K‑54, K‑55, K‑56. Uchylone (R50): K‑19, K‑21, K‑48, K‑52 — N/D zgodnie z protokołem. Brak N/D tam, gdzie etap wymaga.

## 1. Niezależność pomiaru
- SHA‑256 zgodne z raportem wykonawcy (sekcja 2): **TAK** — 13/13 STL (8 płytek niezmienionych + pokrywka `ad2344…`, wkładka `89124d…`, blat `060b43…`, korpus W `7e7c92…`, korpus P `9c31c1…`) i `ramka_v2.blend` `23f4a6…`; rozmiary zgodne. Pliki `ramka_rama_dyfuzora_v2.stl` i `ramka_uchwyt_kabli_v2.stl` nie istnieją (R50‑U1/U8) ✓.
- Skrypt recenzenta napisany bez czytania `ramka_generator.py`: **TAK** (kodu wykonawcy nie otwierano; jedyny NIE w pierwszym przebiegu — „stadiony Z min” w K‑54 — był błędem mojego filtra wierzchołków, zastąpiony pomiarem promieniem; część bez zmian).
- Sondy: 529, niestabilnych **0**; najmniejsza odległość od ściany 0,10 (K‑23 (49,5, 0, 5,9), K‑34 (98,75, 0, 59,7) — zgodne z protokołem, stabilne).
- Transformacje: pokrywka i blat — z_min → 0, obrót 180° wokół X (wierzch na Z = 0); wkładka (−cx, −(y_min + 52,3), −(z_min + 3,5)); korpus: z_min → 0, środek Y z obrysu dna (Z ≈ 0), nie z obrysu z reliefem. Surowe STL: pokrywka ±49,8, Z 0…20; wkładka X ±65, Y −52,3…96, Z 0…11; blat ±100, Z 0…14; korpusy X ±100, Y −100,6…100, Z 0…59,6 — zgodne z tabelą 1 po R50. Test rozpoznawczy osi eksportu blatu niepotrzebny (K‑47 ZAL).
- `.blend`: 33 obiekty; zestaw złożony 23 obiekty (|x|,|y| ≤ 150): korpus_W, blat, wkladka, plytka_wieczorna_n1, pokrywka + 18 `proxy_*`; odsunięte: korpus_P (x 160…360), 7 płytek, `proxy_magnes_B/C`, `proxy_odbiornik_usb` — najmniejsza |współrzędna| 160 ≥ 150. Brak `rama_dyfuzora` i uchwytów w `.blend` ✓.
- `parametry.json` po R50: 273 klucze; wszystkie 9 wartości LICZONE przeliczone ze wzorów: panel_pcb_z 54, blat_top_z 63,6, korpus_h 59,6, panel_standoff_l 50, cover_inner_h 14, snap_pocket_z 52,6, snap_hook_z 52,85, blat_screw_z 55, label_pos_z 51 — zgodne (różnica 0).

## 2. Wyniki sprawdzeń
| Id | Wynik | Zmierzone przez recenzenta | Zadeklarowane przez wykonawcę | Oczekiwane | Waga | Uwaga |
|---|---|---|---|---|---|---|
| K‑01 | ZAL | trójkąty: pokrywka 820, wkładka 1806, blat 5716, korpus W 18220, korpus P 17324; NaN brak; rama/uchwyt: brak plików ✓ | identycznie | > 100 | B | |
| K‑02 | ZAL | pokrywka 99,600 × 99,600 × 20,000 (Z −20…0); wkładka 130,000 × 148,300 × 11,000 (Z −3,5…7,5); blat 200,000 × 200,000 × 14,000; korpus W/P 200,000 × 200,600 × 59,600 (Y −100,6…100) | identycznie | tabela 1 (R50) ± 0,1 | B | |
| K‑03 | ZAL | 5 × (0 / 0 / 0) | 0/0/0 | 0/0/0 | B | |
| K‑04 | ZAL | 5 × 1 składowa | 1 | 1 | B | |
| K‑04b | ZAL | pokrywka 30,064; wkładka 12,406; blat 72,569; korpus W 233,661; korpus P 233,633 cm³ | 30,06 / 12,41 / 72,57 / 233,66 / 233,63 | 30 / 16 / 83 / 225 ± 30 % | B | |
| K‑17 | ZAL | 12/12 (6 z protokołu + 6 kontrolnych: dawne otwory ø4 (±15, −30/0/30) → W) | 6/6 + K‑19 3/3 W | tak | B | |
| K‑18 | ZAL | 8/8 (garby Z −18) | 8/8 | tak | B | |
| K‑19 | N/D | kontrola odwrotna w K‑17: 6/6 W | — | uchylone R50‑U17 | — | |
| K‑20 | ZAL | 4/4 | 4/4 | tak | P | |
| K‑21 | N/D | kontrola odwrotna: wierzch |x|,|y| ≤ 40 z promieni (krok 0,5): Z min −0,000, max 0,000 | 0,000 | uchylone R50‑U14 | — | |
| K‑22 | ZAL | sondy 48,1 POZA / 48,5 W na 4 bokach 8/8; wnęka z promieni X 96,600, Y 96,600; para pokrywka–wkładka w K‑53: 0 | 96,6; 0 | 96,6 ± 0,2; 0 | B | dół kołnierza 70,1 vs rama wkładki 69,6 (K‑54) ✓ |
| K‑23 | ZAL | 10/10 | 6/6 | tak | B | |
| K‑24 | ZAL | 7/7 | 7/7 | tak | B | |
| K‑25 | ZAL | 19/19 (A z protokołu + ciągłość (−51,5, −51,5, 0,7) + kanały/przeloty B, C) | 9/9 | tak | B | |
| K‑27 | ZAL | 4/4 | 4/4 | tak | B | |
| K‑28 | ZAL | 4/4 | 4/4 | tak | B | |
| K‑29 | ZAL | 38/38 (R51, oba uszy) | 20/20 | tak | B | |
| K‑30 | ZAL | 11/11 (rowek 2,5 × 1,5: 50,2 POZA, 49,4 W, 51,5/2,0 W; lewy, tylny, prawy; przód bez rowka) | 7/7 | tak | P | |
| K‑31 | ZAL | strzałki: max Z lewa 6,600, prawa 6,600; pas y −50,0…−48,3 max 6,000; rzut: dwa ▼ na obu segmentach | 6,600 / 6,000 | 6,6 / 6,0 ± 0,05 | P | |
| K‑32 | ZAL | otwór z promieni X 96,600, Y 96,600; para płytka n1–wkładka w K‑53: 0 | 96,6; 0 | 96,6 ± 0,2; 0 | B | |
| K‑33 | ZAL | min Z wkładki poza kołkami 63,600; wierzch dyfuzora 63,600; kołki (±58, 93,5) w otworach blatu 4/4 | identycznie | 63,6 ± 0,02 | B | |
| K‑34 | ZAL | W 10/10, P 10/10 (59,5 / 59,4 / 59,7; R 3 dolna) | 10/10 | tak | B | |
| K‑35 | ZAL | W 33/33, P 33/33 (17 z protokołu: rowki po przekątnych, brak pogłębienia, brak SD, wloty (−8, ±10) 30 × 4; + rowki 3 pozostałych narożników, krawędzie wlotów) | 17/17 | tak | B | |
| K‑36 | ZAL | W 29/29, P 29/29 (16 z protokołu: stadiony, bossy Pi (−46,5/11,5, ±24,5) ø8 z otworem ø2,1, brak bossów uchwytów; + osie 4 bossów, stadiony 3 pozostałych narożników) | 16/16 | tak | B | |
| K‑37 | ZAL | W 18/18, P 18/18 (12 z protokołu + pozostałe szczeliny −18/18/54 i boczne) | 12/12 | tak | B | |
| K‑38 | ZAL | W 28/28, P 28/28 (24 z protokołu: okno −93…−42, skrzynka do lewej ściany, tylna ściana pełna, gniazdo ø12 w prawej ścianie (−41, 89, 30); + krawędzie okna Z 38 i otworu ø12 y 83/95) | 24/24 | tak | B | |
| K‑39 | ZAL | W 20/20, P 20/20 (13 z protokołu: okno 16 × 9, rowki 44,4…50,1 / 69,9…75,6, ścianki 1,9, wkręty blatu Z 55; + krawędzie okna i rowków) | 13/13 | tak | B | |
| K‑40 | ZAL | W i P: 7/7 sond; 429 promieni (Z 5…57): y ∈ [−100,600, −100,000], 0 poza zakresem | identycznie | brak przelotu | B | |
| K‑42 | ZAL | W 12/12, P 12/12 (kieszenie Z 52,6…55,1; dawna wysokość 48,8 → W) | 12/12 | tak | B | |
| K‑43 | ZAL | W i P: min Y (x ±45, Z 46…56) −100,600; (Z 35…41) −100,000; SHA różne; objętość W − P = 0,0287 cm³; rzuty: „RAMKA WIECZORNA” / „RAMKA PORANNA” | −100,600 / −100,000; 0,029 | −100,6 / −100,0 ± 0,05; ≠; < 0,5 | B | |
| K‑44 | ZAL | W 8/8, P 8/8 (brak żeber: (75, 75, 6), (70, 70, 6), (−75, −75, 6) POZA; dno pełne pod 4 stopkami) | 4/4 | tak | P | |
| K‑44b | ZAL | przecięcia Pi/wtyk z korpusem, panelem i 4 dystansami: 12 × 0; luz Z 42,0 − 34,0 = 8,000 (≥ 8); Pi X −50…35, Y ±28, Z 8…34; wtyk X −90…−50, Y 17…27, Z 23…34; test 3 kierunków wtyku 40 od (−50, 22) (−X, −Y, +Y) wobec korpusu, panelu, dystansów i gniazda DC: wszystkie 0 | 0; 8,000 | 0 / ≥ 8 | B | |
| K‑45 | ZAL | 13/13 (naroża ostre: (80,5, 80,5, −1) POZA, (81,5, 81,5, −1) W w 4 narożach) | 7/7 | tak | B | |
| K‑46 | ZAL | 14/14 (kołnierz 95,0…97,0, haczyk do 98,3, lokalnie −10,75…−8,75) | 14/14 | tak | B | |
| K‑47 | ZAL | 43/43 (oba słupki: (75, 93) POZA, (75, 89,6) W, (75, 90,5) W, (78, 92) W; kołki, magnesy, szczeliny obustronnie; brak bossów w 4 narożach: (90, 90, −6) POZA, (90, 90, −3) W); dno otworów kołków −3,800 / −4,000 | 19/19; −3,8 / −4,0 | tak | B | |
| K‑48 | N/D | plik nie istnieje ✓ | N/D | uchylone R50‑U1 | — | |
| K‑49 | ZAL | wnętrze korpusu 195,000 × 195,000; kołnierz blatu zewn. 194,000 × 194,000 → 0,500/stronę; kieszeń 162,000 vs dyfuzor 160,000 → 1,000; PCB wierzch 55,60 vs spód płyty blatu 59,60 → 4,00; PCB 160 pod oknem 158 → nakładka 1,00/stronę; dystanse ø6,4 w (±60, ±60) Z 4…54 na stadionach (wierzch stadionu 4,0); przecięcia blat–korpus 0, panel–blat 0, dystanse–korpus 4 × 0 | identycznie | 0,5 / 1,0 / 4,0 / 1,0; 0 | B | |
| K‑53 | ZAL | 23 obiekty; 41 par z nakładającymi się bbox po skurczu −0,05: 0 przecięć (pozostałe 212 par rozłączne w bbox); kontrola czułości bez skurczu: blat–korpus 469, wkładka–dyfuzor 180, płytka–wkładka 314, dystans–korpus 104, panel–dystans 162 (styki wykrywane) | 253 par, 0 | 0 | B | |
| K‑54 | ZAL | blat (90,0) 63,600; dyfuzor (0,70) 63,600; wkładka (0,50,3) 69,600, max 71,100; płytka n1 (0,−46,5) 74,100, relief 74,700; pokrywka (40,40) 90,100 = max, min 70,100; Pi max 34,000; panel min 42,000, PCB 54,000…55,600; dystanse 4,000…54,000; stadiony: wierzch 4,000, dno obok 3,000; stopki −4,000…0,000; korpus 0…59,600; blat 49,6…63,6; kołki wkładki do 60,100; płytka min 66,100 | identycznie | ± 0,05 | B | |
| K‑55 | ZAL | spód magnesu A 66,300 − wierzch Halla A 65,100 = 1,200; + 0,5 = 1,70 ≤ 4 | 1,200 | 1,2 ± 0,05 | B | |
| K‑56 | ZAL | krawędź wkładki przód y −52,300, prawa x 52,300 → pasy 27,700 / 27,700 → 11 px; siatka 2 mm nad pasami (Z > 63,65): 0 trafień | 27,70 / 27,71; 11; 0 | 27,7 / 11 | B | prawy pas w zasięgu Y ramy; tylne narożniki = strefa uszu (D12) |

## 3. Uwagi do poprawy (tylko NIE), z numerami
| Nr uwagi | K‑xx | Waga | Plik / cecha | Co jest | Co ma być |
|---|---|---|---|---|---|
| — | — | — | brak sprawdzeń NIE | — | — |

## 4. Rozbieżności między raportem wykonawcy a pomiarem recenzenta
Brak. Liczby trójkątów, gabaryty, objętości (do 0,01 cm³), liczby sond protokołu, min Y reliefów, luzy K‑49, wartości K‑54/K‑55/K‑56, K‑44b (luz 8,000) i K‑53 (0 przecięć) identyczne; moje liczby sond większe tam, gdzie rozszerzyłem je na symetryczne cechy.

## 5. Ocena rejestru odstępstw wykonawcy
| # odstępstwa | Zasadne? | Wymaga decyzji właściciela? | Komentarz |
|---|---|---|---|
| 1 (grubość nakrętki DC = `dc_pocket_wall` 2,0) | TAK | NIE (R51) | bryła zastępcza; w `.blend` nakrętka ø15 × 2 na x −40…−38 ✓ |
| 2 (`proxy_odbiornik_usb` x 35…54, y ±7,5, Z 8…14 w korpusie P) | TAK | NIE (R51) | poza zestawem złożonym; po R50‑6 odbiornik (x 35…54) mija stadion (55, 55) o 1 mm w X — wartość nie jest mierzona w K‑53 (uwaga D poniżej) |

## 6. Lista drobnych (D) do v3
1. Odbiornik USB (korpus P) poza testem K‑53: po przesunięciu Pi (R50‑6) jego bryła x 35…54, Z 8…14 kończy się 1,0 mm przed krawędzią stadionu (54,5…) i 1,8 mm przed dystansem (56,8); warto dodać parę w K‑53 (zestaw W z odbiornikiem „hipotetycznym”) w etapie C.
2. `insert_depth_m3` 7 w `parametry.json` opisane jako nieużywane (R50) — do usunięcia w v3 (kosmetyka).

## 7. Sprawdzenia dodatkowe (poza protokołem)
- **Ciągłość kanałów Halla w spodzie wkładki** (rowek 2,5 × 1,5 z przelotem jedną bryłą, R50‑U9): mapa spodu promieniami (0,25 mm), BFS po komórkach kanału: **A, B, C → wyloty (±64, 89): ciągłe** (głębokości 1,0…1,5; 17 010 komórek kanałowych). Rzut `recenzja/spod_wkladki_kanaly.png`.
- K‑44b rozszerzone o pary wtyk/Pi z 4 dystansami i o 3 kierunki wtyku (−X, −Y, +Y) także wobec `proxy_gniazdo_dc`: wszystkie 0.
- Sondy rozszerzone na wszystkie symetryczne wystąpienia cech (4 stadiony z rowkami, 4 bossy Pi, wszystkie 10 szczelin, 4 naroża kieszeni dyfuzora, oba słupki, oba uszy, 4 dawne bossy ramy).
