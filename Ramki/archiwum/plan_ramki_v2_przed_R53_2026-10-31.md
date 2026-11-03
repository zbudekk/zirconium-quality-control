# Plan budowy ramek świetlnych i płytek — plan_ramki_v2 (ŹRÓDŁO PRAWDY)

Wersja 2 planu z sesji 1. **Ten plik jest nadrzędny wobec wszystkich innych** (`sesja2_pliki.md`, `spec_3d_ramka.md`, `plan_ramki_v1.md`): przy rozbieżności obowiązuje ten plik, a wartości liczbowe obowiązują w postaci zapisanej w `parametry.json` (sekcja 13, R14). Wszystkie wymiary w mm, kąty w stopniach, jedna liczba na wymiar. Sekcja 13 zawiera rejestr rozstrzygnięć (R1…R51) z oznaczeniem `[ZAŁOŻENIE]` tam, gdzie decyzja wymaga zatwierdzenia przez właściciela projektu; sekcja 14 — listę zmian względem v1.

---

## 1. Założenia

| Id | Założenie | Uzasadnienie (jedno zdanie) |
|---|---|---|
| Z1 | Pole skanowania Aidite A‑IS Pro 3 ≥ 100 × 100 mm; płytka 96 × 96 zostaje. | Spec zakłada 100 × 100 do potwierdzenia; rozmiar płytki jest parametrem `plate_size`, więc zmiana to jedna liczba. |
| Z2 | Maksymalna wysokość pracy nad dnem gniazda: 14 mm (`max_work_height`). | Największe korony trzonowe w stanie zielonym (skurcz ~20–25 %) mają do ~13 mm, mosty na rynienkach leżą niżej. |
| Z3 | Strefa narożna wyłączona z gniazd: kwadrat 13 × 13 mm w każdym rogu płytki. | Mieści stożek ø5 (środek 6 mm od krawędzi), 3 dołki kodu, kieszeń magnesu, wycięcie 5 × 5 i numer, przy ściankach ≥ 1 mm do sąsiednich cech. |
| Z4 | Stożek znacznika i kieszeń magnesu są współosiowe (środek 6 mm od obu krawędzi rogu). | Między stożkiem (3 mm od góry) a kieszenią (2,2 mm od dołu) zostaje 2,8 mm materiału w płytce 8 mm, a czujnik Halla trafia dokładnie pod znacznik. |
| Z5 | Czujnik Halla: A3144 (cyfrowy, unipolarny, otwarty kolektor), zasilany 5 V, wyjście podciągane 10 kΩ do 3,3 V. | Pi nie ma ADC, a A3144 jest tani i dostępny w Polsce; próg ~35–45 mT osiąga się przy magnesie ø5 × 2 N35 do ~4 mm odległości. |
| Z6 | Płytka leży na 4 narożnych półkach wkładki (2,5 mm nad dyfuzorem), nie bezpośrednio na dyfuzorze. | Półki mieszczą czujniki Halla pod narożnikami płytki (pkt 0.3.2); 2,5 mm szczeliny nie psuje świecenia przez otwór ø3. |
| Z7 | Wysokość ramy wkładki 6 mm (spec: 3 mm). | Półki 2,5 mm + 3,5 mm ścianki prowadzącej płytkę; przy 3 mm płytka byłaby prowadzona tylko 0,5 mm. |
| Z8 | Stos Pi 4 + Bonnet od spodu PCB Pi do najwyższego elementu Bonnetu: 26 mm (`pi_stack_h`, DO ZMIERZENIA) **bez kabli; z wpiętą taśmą HUB75 do 31** — pokrywa to zapas `pi_clearance_top` 8 (R50‑1). | PCB 1,6 + złącze GPIO 11 + PCB Bonnetu 1,6 + gniazdo DC Bonnetu 11 = 25,2; złącze IDC 9 + wtyk taśmy 5 + zagięcie 3 → 28–31 (A‑4). |
| Z9 | Elementy od spodu panelu HUB75 (złącza, kondensatory) sięgają 12 mm poniżej PCB (`panel_bottom_parts_h`, DO ZMIERZENIA) i mogą być w dowolnym miejscu spodu; **z wpiętymi kablami do 17** — pokrywa to zapas R50‑1 (łącznie z Z8 do +5). | Bez pomiaru nie wolno zakładać wolnego miejsca pod panelem; stąd Pi mieści się pod panelem w całości poniżej złączy; typowo złącza HUB75 leżą przy bokach PCB, VH przy dolnej krawędzi (A‑2). |
| Z10 | Otwory montażowe panelu: 4 szt. M3 na kwadracie 120 × 120 mm wokół środka (`panel_hole_pitch`, DO ZMIERZENIA). **Korpus ma rowki po przekątnej na rozstaw 110…130 (R50‑2)**, więc pomiar nie blokuje zamówienia; wzór niekwadratowy/offset → wiercenie ø4 w dnie. | Brak normy (A‑3): spotykane 4 lub 8 otworów, rozstaw 110–136, zwykle symetrycznie wokół środka. |
| Z11 | Bonnet zasila Pi przez pin 5 V złącza GPIO; w obudowie jest jedno gniazdo DC. | Tak działa Adafruit RGB Matrix Bonnet; drugi zasilacz byłby zbędny. |
| Z12 | Wolne GPIO wyprowadzamy lutując kątową listwę do pinów złącza 2×20 od góry Bonnetu. | Bonnet nie ma listwy przelotowej, a potrzebujemy 7 sygnałów + zasilania. |
| Z13 | Gniazdo USB serwisowe w tylnej ściance to panelowe gniazdo USB‑A z zaślepką, kabel 30 cm do portu USB Pi. | Pi leży pod panelem, więc jego porty nie dochodzą do ściany; przedłużacz uniezależnia pozycję Pi. |
| Z14 | **[usunięte R50‑U6]** Karta SD: po zdjęciu blatu i panelu (4 wkręty od spodu); bez szczeliny w dnie. | Karta wyjmowana raz na rok; szczelina w dnie była jedynym wlotem pyłu do komory elektroniki od dołu; Pi po R50‑6 leży w całości pod panelem. |
| Z15 | Blat: 4 zatrzaski na kołnierzu + 2 wkręty M3 przez tylną ściankę (nie od dołu). | Wkręty od dołu wymagałyby słupków 55 mm; wkręty w tylnej ściance są niewidoczne od frontu i z góry. |
| Z16 | (uchylone przez Z28) | — |
| Z17 | Klawiatura numeryczna: 130 × 90 × 20 mm, odbiornik USB nano 19 × 15 × 6 (DO ZMIERZENIA). | Typowe wymiary bezprzewodowych klawiatur numerycznych 2,4 GHz. |
| Z18 | Napis na przedniej ściance jest parametrem tekstowym; korpus eksportuje się dwa razy (`_W`, `_P`), geometria identyczna. | Spec chce identycznych obudów i napisu nazwy jednocześnie; różni się tylko relief. |
| Z19 | Kolor: korpus, blat — PA12 barwiony na grafit; wkładka, płytki — PA12 naturalny biały; pokrywka — PETG FDM (druk własny); tulejka DC i podkładki panelu — żywica/PETG (druk własny). Rama dyfuzora i uchwyty kabli usunięte (R50‑U1, R50‑U8). | Zgodnie z 4.7; biały pod skaner, grafit na pokaz; materiały per część w `materials`. |
| Z20 | Gniazda w rzędach rosnąco od przodu, rynienki w dwóch tylnych rzędach. Wieczorna 24 (13 × ø9, 6 × ø12, 5 × ø15) + 2 rynienki; poranna 35 (22 × ø7,5, 7 × ø10, 6 × ø12,5) + 2 rynienki. | Uporządkowany układ jest czytelny dla technika i programu; tyle rzędów mieści się w 90 mm przy ściankach dokładnie 3 mm (rachunek w D6); wieczorna ma mniej ø12 niż w spec (6 zamiast 9), bo każdy dodatkowy rząd kosztuje 3 mm ścianki. |
| Z21 | Orientacja płytki: narożnik z wycięciem = przód‑prawy (D); czujniki Halla pod A (przód‑lewy), B (tył‑lewy), C (tył‑prawy). | Wycięcie z przodu po prawej jest dobrze widoczne dla praworęcznego technika. |
| Z22 | Ceny w liście zakupów są orientacyjne (wyszukiwanie nie zwróciło cen w zł). | Zaznaczone zgodnie z 0.1.5. |
| Z23 | Odstęp dioda–dyfuzor 4 mm (`led_gap`). | Środek zakresu 3–5 mm ze spec. |
| Z24 | Rynienki mają 4 otwory ø3 w dnie (rozstaw 12 mm wieczorna, 10 mm poranna). | Jeden otwór nie doświetliłby 60‑mm mostu. |
| Z25 | (uchylone przez Z28) | — |
| Z26 | Bez podstawki klawiatury i bez nalepki z legendą (odstępstwo od spec 4.6 i tabeli 6). Klawiatura leży luzem na stole; legenda klawiszy tylko w instrukcji programu. | Klawiatura ma własne stopki, a tacka to ok. 60 cm³ druku bez funkcji; użytkownik nie chce nalepki. |
| Z27 | Ramka poranna jest chowana do szafki, więc gniazdo DC siedzi w kieszeni wgłębionej w tylnej ściance (okno 51 × 24, głębokość 22, skrzynka do lewej ściany — R50‑4), **gniazdo w prawej ścianie skrzynki osią wzdłuż X (R50‑3)**; wtyk kątowy 5,5/2,1 wchodzi od wnętrza kieszeni w −X, kabel wychodzi przez okno; wtyk prosty też się mieści (do 40 + zagięcie). Wtyk nie wystaje poza obrys 200 × 200. Obudowy są identyczne, więc kieszeń ma też ramka wieczorna. | Wystający prosty wtyk łamałby się przy wsuwaniu ramki do szafki i wymuszał odpinanie zasilacza; gniazdo osią X nie celuje w dystans panelu (−60, 60) i nie zależy od długości korpusu gniazda ani wysięgu wtyku. |
| Z28 | **Decyzja właściciela (nadpisuje spec 1, 3.6, 4.5):** skan wieczorem uruchamia spacja na laptopie. Ramka wieczorna nie ma przycisku ani czujnika gestu: bez przycisku arkadowego, otworu w przedniej ściance, zaślepki, głowicy VL53L1X, ich kabli, przepustów, wkładek i pozycji w listach. Przednia ścianka obu korpusów gładka, bez otworów, tylko wytłoczony napis. Jedyna różnica między ramkami: odbiornik USB klawiatury w porannej (i napis). | Mniej części, mniej otworów w pyle, identyczne obudowy; stan ramki widać na matrycy. |

---

## 2. Decyzje projektowe

### D1. Wariant obudowy — rekomendacja: WYSOKI (Pi pod panelem)

| Kryterium | Wysoki 200 × 200 × 63,6 (R50‑1) | Niski 200 × 270 × 40 |
|---|---|---|
| Realna wysokość | łańcuch: 3 + 5 + 26 + **8** + 12 + 1,6 + 2 + 4 + 2 = **63,6** (zapas 8 nad stosem Pi pokrywa taśmę HUB75 i złącza panelu z kablami; przekracza spec 55–60 o 3,6 — decyzja właściciela, R50‑1) | stos Pi 26 + słupki 5 + dno 3 + luz 3 + blat 4 = 41 → nie 35, jak w spec |
| Zajęte miejsce na parapecie | 400 cm² | 540 cm² (+35 %) |
| Kabel HUB75 | ~150 mm, złożony pod panelem | ~250 mm przez przegrodę |
| Dostęp do karty SD | po zdjęciu blatu i panelu (R50‑U6) | od góry po zdjęciu blatu |
| Pył na elektronice | Pi zakryty panelem i blatem | osobna komora, jedna więcej przegroda |
| Sztywność blatu | okno 158 w blacie 200, ramiona 19 mm | blat 270 z oknem i komorą, więcej żeber |
| Objętość druku korpusu | ~225 cm³ | ~250 cm³ |
| Wygląd | kompaktowa kostka, identyczna z każdej strony | płaski, asymetryczny |

Rekomendacja: wariant wysoki. Wykonawca modeluje tylko jego. Wysokość jest ustalona z zapasem (R50‑1): po pomiarach `pi_stack_h` i `panel_bottom_parts_h` korpus się NIE zmienia — zmienia się tylko dobór dystansów/podkładek (R50‑7, R50‑8), o ile suma pomiarów nie przekroczy domyślnych o więcej niż 5.

### D2. Technologia i materiał każdej części
Części zamawiane (SLS/MJF PA12): korpus W/P i blat — PA12 barwiony na grafit (wariant pokazowy: barwienie + wygładzanie parowe); wkładka i płytki — PA12 naturalny biały, bez wygładzania wierzchu płytek (mat dla skanera); płytki wieczorne n1–n3 alternatywnie żywica matowa w firmie (po teście skanera). Druk własny: pokrywka — PETG FDM; tulejka DC i podkładki panelu — żywica w firmie lub PETG. Rama dyfuzora i uchwyty kabli usunięte (R50‑U1, R50‑U8). Alternatywa CNC z PMMA opal 8 mm tylko dla płytek, jeśli usługodawca nie ma PA12 — wtedy STEP przez FreeCAD (wykonawca dodaje notatkę w arkuszu).

### D3. Układ współrzędnych (globalny, dla wszystkich części)
Początek: środek obrysu korpusu w płaszczyźnie jego zewnętrznego dna (bez stopek). X w prawo (patrząc od użytkownika), Y do tyłu (od użytkownika), Z w górę. Przód ramki = −Y. Środek panelu, dyfuzora, wkładki i płytki = (0, 0). Płytka ma lokalny układ: środek górnej powierzchni, te same kierunki osi; narożniki: A = (−48, −48) przód‑lewy, B = (−48, +48) tył‑lewy, C = (+48, +48) tył‑prawy, D = (+48, −48) przód‑prawy (wycięcie).

### D4. Łańcuch wysokości (wariant wysoki), Z od zewnętrznego dna
| Poziom | Z [mm] | Składnik |
|---|---|---|
| wierzch dna korpusu | 3,0 | `floor_t` |
| spód PCB Pi | 8,0 | + `pi_standoff_h` 5 |
| szczyt stosu Pi+Bonnet | 34,0 | + `pi_stack_h` 26 (z taśmą do 39) |
| najniższy element spodu panelu | 42,0 | + `pi_clearance_top` 8 (R50‑1: zapas na taśmę HUB75 i złącza panelu z kablami, łącznie do +5) |
| spód PCB panelu | 54,0 | + `panel_bottom_parts_h` 12 → `panel_pcb_z` |
| lico diod | 57,6 | + `panel_pcb_t` 1,6 + `panel_led_h` 2 |
| spód dyfuzora | 61,6 | + `led_gap` 4 (przy fizycznym led_h 1…3 luz wynosi 5…3 — w spec 3–5) |
| wierzch dyfuzora = wierzch blatu | 63,6 | + `diffuser_t` 2 → `blat_top_z` |
| wierzch korpusu (pod blatem) | 59,6 | `blat_top_z` − `blat_t` 4 → `korpus_h` |
| wierzch półek wkładki | 66,1 | + `insert_shelf_h` 2,5 |
| wierzch ramy wkładki | 69,6 | + `insert_h` 6 |
| wierzch płytki | 74,1 | półka + `plate_thickness` 8 |
| szczyt najwyższej pracy | 84,1 | płytka − 4 + 14 |

Słupki panelu (R5, R50‑2, R50‑7): podkładka drukowana w kształcie stadionu 9 szer. × `panel_pad_h` 1 wzdłuż przekątnej od (±55, ±55) do (±65, ±65) na dnie + mosiężny dystans M3 **żeńsko‑żeński** `panel_standoff_l` 50 → 3 + 1 + 50 = 54 = `panel_pcb_z` ✓. Góra: wkręt dociskowy M3 × 5 (2,5 w gwint panelu + 2,5 w dystans; nic nie wystaje od strony diod); bez gwintu w panelu: tulejka F‑F M3 ø5 × 5 doklejona epoksydem do spodu PCB i dystans 45 (3 + 1 + 45 + 5 = 54 ✓). Dół: wkręt M3 × 10 z podkładką ø9 od spodu przez rowek 3,4 w dnie (bez pogłębienia, R50‑U20; łeb 2,5 pod dnem, stopki 4) w gwint dystansu. Wartości globalne związane z blatem wynikają z `korpus_h` (LICZONE): `snap_pocket_z` = korpus_h − 7 = 52,6; `snap_hook_z` = korpus_h − 6,75 = 52,85; `blat_screw_z` = korpus_h − 4,6 = 55; `label_pos_z` = korpus_h − 8,6 = 51.

### D5. Gniazdo płytki i czujniki Halla (pkt 0.3.2)
Wkładka = rama 4 mm szeroka × 6 mm wysoka wokół otworu 96,6 × 96,6, z 4 narożnymi półkami 12 × 12 × 2,5 mm wewnątrz otworu. Płytka leży na półkach; narożne strefy płytki 13 × 13 nie mają gniazd (Z3), więc półki nie zasłaniają żadnego otworu świetlnego. W półkach A, B, C kieszeń przelotowa 5,0 × 5,5 na czujnik A3144 (TO‑92 leżący płasko, lico do góry, stoi na dyfuzorze: wierzch obudowy 1,5 mm → 1,0 mm pod spodem płytki). Odległość magnes–czujnik: 0,2 (magnes cofnięty w kieszeni 2,2 przy grubości 2,0) + 1,0 (szczelina) + ~0,5 (głębokość struktury w TO‑92) = 1,7 mm ≤ 4 ✓. Pole na osi magnesu ø5 × 2 N35 (Br 1,2 T): przy 1,7 mm ~150 mT; przy 4 mm ~45 mT; próg A3144 ~40 mT → rezerwa > 3× ✓. Półka D niesie kołek orientacyjny 4,4 × 4,4 × 5 wchodzący w wycięcie 5 × 5 płytki. Zasłonięte piksele: rama 4 mm = 1,6 piksela na każdym boku; półki leżą pod strefami narożnymi bez gniazd → 0 pikseli użytkowych. Wolny pas marginesu: 32 − 0,3 − 4 = 27,7 mm = 11 pełnych pikseli z każdej strony (wystarcza na 2 cyfry 5 × 7).

### D6. Rozkład gniazd (pkt 0.3.1) — rachunek
Strefa gniazd: x, y ∈ [−45, 45]. Narożniki wyłączone: |x| > 35 i |y| > 35 jednocześnie. Rzędy od przodu (−y) rosnąco wg rozmiaru, rynienki w dwóch ostatnich rzędach (najdalej od użytkownika); ścianki między rzędami i gniazdami dokładnie 3 mm; gniazda w rzędzie rozłożone symetrycznie względem x = 0. Pierwszy i ostatni rząd (|y| > 35) mieszczą się w x ∈ [−35, 35].

Wieczorna (środki gniazd, mm):

| Rząd | y (zakres) | Zawartość | Szerokość | Limit |
|---|---|---|---|---|
| R1 | −40,5 (−45…−36) | ø9 ×6: x = −30, −18, −6, 6, 18, 30 | 69 | 70 (róg) |
| R2 | −28,5 (−33…−24) | ø9 ×7: x = −36, −24, −12, 0, 12, 24, 36 | 81 | 90 |
| R3 | −15 (−21…−9) | ø12 ×6: x = −37,5, −22,5, −7,5, 7,5, 22,5, 37,5 | 87 | 90 |
| R4 | +1,5 (−6…9) | ø15 ×5: x = −36, −18, 0, 18, 36 | 87 | 90 |
| R5 | +19,5 (12…27) | rynienka 60 × 15, środek x = 0 | 60 | 90 |
| R6 | +37,5 (30…45) | rynienka 60 × 15, środek x = 0 | 60 | 70 (róg) |

Suma wysokości rzędów: 9 + 9 + 12 + 15 + 15 + 15 + 5 × 3 = 90 ✓. Razem 24 gniazda + 2 rynienki (13 × ø9, 6 × ø12, 5 × ø15).

Poranna:

| Rząd | y (zakres) | Zawartość | Szerokość | Limit |
|---|---|---|---|---|
| R1 | −41,25 (−45…−37,5) | ø7,5 ×6: x = −26,25, −15,75, −5,25, 5,25, 15,75, 26,25 | 60 | 70 (róg) |
| R2 | −30,75 (−34,5…−27) | ø7,5 ×8: x = −36,75, −26,25, −15,75, −5,25, 5,25, 15,75, 26,25, 36,75 | 81 | 90 |
| R3 | −20,25 (−24…−16,5) | ø7,5 ×8: jak R2 | 81 | 90 |
| R4 | −8,5 (−13,5…−3,5) | ø10 ×7: x = −39, −26, −13, 0, 13, 26, 39 | 88 | 90 |
| R5 | +5,75 (−0,5…12) | ø12,5 ×6: x = −38,75, −23,25, −7,75, 7,75, 23,25, 38,75 | 90 | 90 |
| R6 | +21,5 (15…28) | rynienka 50 × 13, środek x = 0 | 50 | 90 |
| R7 | +37,5 (31…44) | rynienka 50 × 13, środek x = 0 | 50 | 70 (róg) |

Suma: 7,5 × 3 + 10 + 12,5 + 13 + 13 + 6 × 3 = 89 ≤ 90 ✓. Razem 35 gniazd + 2 rynienki (22 × ø7,5, 7 × ø10, 6 × ø12,5). Liczba 35 jest decyzją ostateczną (R40); zmiana tylko przez edycję D6 i JSON na bramce.

### D7. Czujnik Halla i elektryka (pkt 0.3.3)
A3144: VCC 5 V, GND, OUT otwarty kolektor → 10 kΩ do 3,3 V na płytce prototypowej + wejście GPIO. Logika: magnes obecny = stan niski. Biegun: południowy (S) skierowany w dół, do czujnika, we wszystkich płytkach — przed klejeniem oznaczyć S flamastrem (strony przyciągające się mają przeciwne bieguny; wzorzec: jeden magnes oznaczony raz, reszta względem niego). Alternatywa bez zmian w planie: Honeywell SS451A lub TI DRV5032 (omnipolarne, 3,3 V), ta sama obudowa TO‑92 i ten sam układ pinów VCC/GND/OUT; wtedy biegun dowolny.

### D8. Pokrywka płytki (pkt 0.3.4)
Luz liczony nad najwyższą pracą: `cover_inner_h` = `max_work_height` 14 − `socket_depth` 4 + 4 = 14 mm nad wierzchem płytki. Pokrywka to nakładka z kołnierzem schodzącym 4 mm poniżej wierzchu płytki, 4 zatrzaski (garby 0,7 mm: lewy i prawy bok na y = 0, przedni bok na x = +25, tylny bok na x = −25 — poza wycięciami palcowymi 30 mm na środkach przodu i tyłu, R42) wchodzą w rowek 1,0 × 0,8 mm wokół boków płytki, 2 mm pod jej wierzchem. Rowek nie koliduje z wkładką (jest cofnięty w głąb płytki).

### D9. Mocowanie blatu
Blat 4 mm z kołnierzem 10 mm wysokim (2 mm grubym, luz 0,5 do ścian, R48) wewnątrz korpusu; 4 haczyki zatrzaskowe (8 mm szerokie, występ 1,3, R48) w ślepe kieszenie ścian korpusu głębokości 1,0 (zostaje 1,5 mm ścianki, R6). Położenie haczyków i kieszeni: lewa ściana y = 0, prawa ściana y = 0, przednia ściana x = +50, tylna ściana x = −50 (omijają napis z przodu i kieszeń DC z tyłu). 2 wkręty M3 × 8 przez tylną ściankę w (±75, Z `blat_screw_z` 55) w otwory ø2,5 × 6 (gwint formowany, R49/R49a) w słupkach kołnierza (R7). Zero śrub na wierzchu. Właściciel (R50‑U2 odrzucone): wkręty zostają, bo ramka poranna jest codziennie noszona do szafki.

### D10. Położenie Pi
Pi 4 płasko na 4 bossach ø8 × 5 (otwór ø2,1 pod wkręt M2,5 formujący gwint, R49) pod panelem; narożnik PCB Pi (krawędź z kartą SD, przednia) w (**−50, −28**) (R50‑6); Pi zajmuje x −50…35, y −28…28; karta SD w kierunku −X, złącze GPIO wzdłuż krawędzi y = +28; porty USB w kierunku +X (x 35…37). Pi leży w całości pod panelem. Od krawędzi SD do lewej ściany (−97,5) jest 47,5, od przedniej krawędzi do ściany 69,5, od tylnej do bossa uchwytu… (uchwyty usunięte, R50‑U8) do skrzynki DC (y 78) 50 → wtyk DC Bonnetu 40 mm mieści się w kierunkach −X, −Y i +Y; +X (w porty USB Pi) wyklucza sam Bonnet.

### D11. Numeracja płytek i kod
Numer n = A + 2·B + 4·C (bit = magnes obecny w narożniku A, B, C). Dołki kodu w kolumnie przy lewej krawędzi obok narożnika A (R3): dołek 1 (bit A) y = −36, dołek 2 (bit B) y = −33, dołek 3 (bit C) y = −30, wszystkie x = −45,0, ø2 × 1 mm (ścianka do krawędzi płytki 2,0; do stożka A 3,2; do najbliższego gniazda ≥ 3,5; do rowka pokrywki 1,3 lokalnie, R47). Płytki wieczorne: nr 1, 2, 3; poranne: nr 4, 5, 6 (typ płytki wynika z numeru). 7 = rezerwa, 0 = brak płytki. Relief numeru (cyfra 5 mm wysoka, 0,6 mm) w narożniku D: środek (39,5, −44,5).

### D12. Wkładka w blacie: 2 kołki + 2 magnesy
Wkładka ma 2 tylne „uszy” 14 × 43,7 × 3 mm (od tylnej krawędzi ramy y = 52,3 do y = 96), środki x = ±58, każde z nasadą L 3 mm (x ±(44…52,3) od y 48,8; x ±(52,3…65) od y 52,3) zrośniętą ze ścianką ramy (R47, R51). W każdym uchu kołek ø3 × 3,5 w dół w (±58, 93,5) do otworu ø3,3 w blacie, magnes ø5 × 2 w otworze przelotowym ø5,4 w (±58, 86) naprzeciw magnesu w kieszeni blatu (bieguny przyciągające). Uszy zasłaniają po 14 × 28 mm tylnych narożników marginesu matrycy (dozwolone: w całości odsłonięte mają być pas przedni i prawy). Przewody Halla: rowek 2,5 szer. × 1,5 wys. (R50‑U9) na zewnętrznej dolnej krawędzi ramy (lewy, tylny, prawy bok), jedna bryła z przelotem w ściance narożnika, potem kanał 2 × 1,2 pod uchem, do szczeliny 4 × 8 w blacie w (±66, 90).

### D13. Panel (rama dyfuzora usunięta, R50‑U1)
Panel skręcony od dołu (R5, R50‑2, R50‑7): dystans M3 żeńsko‑żeński 50 mm stoi na podkładce‑stadionie 9 × 1 na dnie (oś wzdłuż przekątnej od (±55, ±55) do (±65, ±65)), wkręt M3 × 10 z podkładką ø9 od spodu korpusu przez rowek 3,4 szer. w dnie (bez pogłębienia, R50‑U20) w gwint dystansu; góra: wkręt dociskowy M3 × 5 w gwintowany otwór M3 panelu (pomiar #5a) albo tulejka F‑F M3 ø5 × 5 doklejona epoksydem do spodu PCB + dystans 45 (bez gwintu). Bez bossów pod panelem. Panel jest ustalony w XY przez 4 dystanse w otworach panelu (±0,2); **rama dyfuzora usunięta [usunięte R50‑U1]** — bez pianki ani innego uszczelnienia (decyzja właściciela); szczelina między PCB 160 a oknem blatu 158 (nakładka 1 na stronę) i luz kołnierza blatu 0,5 przepuszczają światło tylko do wnętrza obudowy, nie na zewnątrz. Dyfuzor 160 × 160 × 2 leży w kieszeni blatu 162 × 162 × 2 na półce 2 mm (otwór przelotowy 158 × 158; naroża kieszeni ostre, R50‑U15, pleksi bez fazowania), licowany; dociskany magnesami wkładki.

### D14. Wentylacja i pył
Wlot: 2 szczeliny 30 × 4 w dnie pod środkiem Pi (x −8, y ±10) (R50‑U19). Wylot: szczeliny 12 × 3 **bez daszków** (R50‑U4) nisko w ścianach: tylna 4 szt. (x −54, −18, 18, 54), boczne po 3 szt. (y −36, 0, 36), oś na Z = 8 (R50‑U19). Stopki gumowe 4 mm samoprzylepne na płaskim dnie (bez gniazd, R50‑U16). Gniazda w tylnej ściance: DC z nakrętką w kieszeni wgłębionej (Z27, R50‑3, R50‑4): okno w ścianie 51 × 24 (x −93…−42, Z 14…38, naroża ostre R50‑U15), za nim skrzynka x −97,5…−40 (lewa ściana skrzynki = lewa ściana korpusu), y 78…100, Z 12…40 (ściany 2 mm, zamknięta od dołu, góry i prawego boku, otwarta tylko na zewnątrz); **gniazdo DC w prawej ścianie skrzynki** (płaszczyzna x = −40, ściana −42…−40), oś (y 89, Z 30) wzdłuż X, otwór ø12 (gniazdo ø8 przez tulejkę redukcyjną ø12/ø8,2), flansza w kieszeni, nakrętka od strony wnętrza obudowy (x > −40), korpus gniazda w +X (wolne 50 mm); wtyk kątowy wchodzi od wnętrza kieszeni w −X (wysięg 18–26 od lica −42 → ≥ 27 do lewej ściany), kabel obrócony ku +Y wychodzi przez okno; wtyk prosty do 40 + zagięcie 12 też się mieści (−94 > −95,5). Skrzynka mija podkładkę/dystans panelu (−60, 55…65) o ≥ 9,8 mm w Y, szczeliny wentylacyjne (Z ≤ 9,5) o 2,5 mm. Gniazdo USB‑A panelowe z zaślepką w (60, Z 24): okno 16 × 9 + 2 rowki poziome 3,2 × 5,7 (rozstaw flanszy 23…28, R50‑5); żadnych odsłoniętych złącz Pi.

### D15. Przednia ścianka (Z28)
Przednia ścianka gładka: bez otworów, bez przycisku, bez głowicy. Jedyna cecha: napis wypukły 0,6, wysokość liter 8, środek x = 0, Z = `label_pos_z` 51 (= korpus_h − 8,6), treść `label_text_W` / `label_text_P` (zostaje; R50‑U14 dla korpusu odrzucone przez właściciela). Kieszeń zatrzasku przedniego na x = +50 (R6) nie koliduje z napisem (relief na zewnątrz, kieszeń wewnątrz, R47(17)). Dawne D15 (głowica, przycisk, zaślepka) uchylone.

### D16. Nazwy plików STL (R2, R17)
Sufiks wersji `v2`. Pliki bazowe (do sprawdzeń i do `.blend`, NIE do zamówienia): `ramka_plytka_wieczorna_v2.stl`, `ramka_plytka_poranna_v2.stl`. Pliki do zamówienia w drukarni: `ramka_plytka_wieczorna_n1_v2.stl`, `…_n2_v2.stl`, `…_n3_v2.stl`, `ramka_plytka_poranna_n4_v2.stl`, `…_n5_v2.stl`, `…_n6_v2.stl`, `ramka_korpus_W_v2.stl`, `ramka_korpus_P_v2.stl`, `ramka_blat_v2.stl`, `ramka_wkladka_v2.stl` (10 plików). Pliki do druku własnego: `ramka_pokrywka_v2.stl` (PETG FDM), `ramka_tulejka_dc_v2.stl`, `ramka_podkladka_panelu_05_v2.stl`, `…_1_v2.stl`, `…_2_v2.stl` (żywica/PETG). Razem 15 STL do druku + 2 bazowe = 17. Usunięte: `ramka_rama_dyfuzora_v2.stl` [R50‑U1], `ramka_uchwyt_kabli_v2.stl` [R50‑U8], głowica i zaślepka [Z28]. Pełna lista plików wynikowych: sekcja 12.1.

---
## 3. Tabela parametrów

Nazwy są kluczami w `parametry.json` i jedynym źródłem wartości dla skryptu (R14): skrypt wczytuje plik, nie ma własnych liczb. Źródło: `spec`, `Zn`, `Dn`, `Rn` albo `DO ZMIERZENIA` (wartość domyślna, podmienić po pomiarze; w JSON pole `"status": "DO_ZMIERZENIA"`). Wartości „liczone” (`korpus_h`, `blat_top_z`, `panel_pcb_z`) skrypt wylicza sam i porównuje z JSON — różnica = błąd.

### 3.1 Płytki i pokrywka

| Parametr | Wartość | Jedn. | Źródło | Opis |
|---|---|---|---|---|
| plate_size | 96 | mm | spec | bok płytki (kwadrat) |
| plate_thickness | 8 | mm | spec | grubość płytki |
| plate_corner_zone | 13 | mm | Z3 | bok kwadratu narożnego bez gniazd |
| socket_zone | 90 | mm | spec | bok strefy gniazd (środek płytki) |
| socket_wall_min | 3 | mm | spec | minimalna ścianka między gniazdami |
| socket_depth | 4 | mm | spec | głębokość gniazd i rynienek |
| socket_wall_angle | 15 | ° | spec | kąt ścianki stożka od pionu |
| socket_hole_d | 3 | mm | spec | otwór przelotowy w dnie gniazda |
| trough_hole_count | 4 | szt. | Z24 | otwory ø3 w dnie rynienki |
| ev_trough_hole_pitch | 12 | mm | Z24 | rozstaw otworów rynienki wieczornej |
| mo_trough_hole_pitch | 10 | mm | Z24 | rozstaw otworów rynienki porannej |
| marker_cone_d | 5 | mm | spec | średnica stożka znacznika |
| marker_cone_depth | 3 | mm | spec | głębokość stożka (wierzchołek w dół) |
| marker_offset | 6 | mm | Z4 | odległość osi znacznika od obu krawędzi rogu |
| notch_size | 5 | mm | spec | wycięcie orientacyjne w rogu D, przelotowe |
| code_dimple_d | 2 | mm | spec | średnica dołka kodu |
| code_dimple_depth | 1 | mm | spec | głębokość dołka kodu |
| code_dimple_x | −45.0 | mm | R3/R47 | x wszystkich dołków (układ płytki) |
| code_dimple_y0 | −36 | mm | R3 | y dołka bitu A (bit B: −33, bit C: −30) |
| code_dimple_pitch | 3 | mm | D11 | odstęp y między dołkami (w kierunku +y) |
| magnet_d | 5 | mm | spec | magnes |
| magnet_h | 2 | mm | spec | magnes |
| magnet_pocket_d | 5.2 | mm | spec | kieszeń magnesu od spodu |
| magnet_pocket_depth | 2.2 | mm | spec | kieszeń magnesu |
| number_relief_h | 0.6 | mm | spec | wysokość reliefu numeru |
| number_text_h | 5 | mm | D11 | wysokość cyfry |
| number_pos_x | 39.5 | mm | D11 | środek cyfry (układ płytki) |
| number_pos_y | −44.5 | mm | D11 | środek cyfry |
| cover_groove_w | 1.0 | mm | D8 | rowek zatrzaskowy na bokach płytki (wysokość) |
| cover_groove_depth | 0.8 | mm | D8 | głębokość rowka w bok płytki |
| cover_groove_z | 2 | mm | D8 | środek rowka poniżej wierzchu płytki |
| ev_socket_d_s | 9 | mm | spec | wieczorna, mała |
| ev_socket_d_m | 12 | mm | spec | wieczorna, średnia |
| ev_socket_d_l | 15 | mm | spec | wieczorna, duża |
| ev_trough_l | 60 | mm | spec | rynienka wieczorna, długość |
| ev_trough_w | 15 | mm | spec | rynienka wieczorna, szerokość |
| mo_socket_d_s | 7.5 | mm | spec | poranna, mała |
| mo_socket_d_m | 10 | mm | spec | poranna, średnia |
| mo_socket_d_l | 12.5 | mm | spec | poranna, duża |
| mo_trough_l | 50 | mm | spec | rynienka poranna, długość |
| mo_trough_w | 13 | mm | spec | rynienka poranna, szerokość |
| max_work_height | 14 | mm | Z2 | najwyższa praca nad dnem gniazda |
| cover_inner_h | 14 | mm | D8 | prześwit pokrywki nad wierzchem płytki |
| cover_top_t | 2 | mm | D8 | grubość wierzchu pokrywki |
| cover_skirt_t | 1.5 | mm | D8 | grubość kołnierza pokrywki |
| cover_skirt_below | 4 | mm | D8 | kołnierz poniżej wierzchu płytki |
| cover_clearance | 0.3 | mm | spec 4.8 | luz pokrywka–płytka na stronę |
| cover_snap_bump | 0.7 | mm | D8 | występ garbu zatrzasku |
| cover_snap_w | 10 | mm | D8 | szerokość garbu |
| cover_snap_front_x | 25 | mm | R42 | garb na przednim boku x = +25, na tylnym x = −25; boczne y = 0 |
| cover_snap_hgt | 0.8 | mm | R47 | wysokość garbu w Z (w rowku 1,0) |
| cover_snap_r | 0.4 | mm | R47/G2 | zaokrąglenie czubka garbu (półokrąg = cover_snap_hgt/2) |
| cover_snap_z | −18 | mm | R47 | środek garbu, lokalnie od wierzchu pokrywki (= rowek płytki 2 mm pod jej wierzchem) |
| ~~cover_vent_cols_x, cover_vent_rows_y, cover_vent_d, cover_vent_pitch~~ | — | — | [usunięte R50‑U17] | pokrywka bez otworów wentylacyjnych (pełny wierzch) |
| ~~cover_label_h~~ | — | — | [usunięte R50‑U14] | pokrywka bez reliefu „GÓRA” (druk FDM wierzchem w dół) |
| cover_corner_r | 3 | mm | spec 4.1 | promień zewnętrznych pionowych krawędzi |

### 3.2 Panel, dyfuzor, Pi

| Parametr | Wartość | Jedn. | Źródło | Opis |
|---|---|---|---|---|
| panel_size | 160 | mm | spec | bok PCB panelu |
| panel_pcb_t | 1.6 | mm | spec | grubość PCB panelu |
| panel_led_h | 2 | mm | DO ZMIERZENIA | wysokość diod/maski nad PCB; korpus od niej niezależny (luz dioda–dyfuzor = 6 − led_h, R50‑1) |
| panel_bottom_parts_h | 12 | mm | DO ZMIERZENIA | najniższy element spodu panelu poniżej PCB (z kablami do 17 w zapasie R50‑1) |
| panel_hole_pitch_x | 120 | mm | DO ZMIERZENIA | rozstaw otworów M3 panelu w X (używane tylko przez bryły zastępcze dystansów; korpus ma rowki R50‑2) |
| panel_hole_pitch_y | 120 | mm | DO ZMIERZENIA | rozstaw otworów M3 panelu w Y (j.w.) |
| panel_hole_offset_x | 0 | mm | DO ZMIERZENIA | przesunięcie środka wzoru otworów od środka panelu (j.w.) |
| panel_hole_offset_y | 0 | mm | DO ZMIERZENIA | j.w. |
| panel_slot_pitch_min | 110 | mm | R50‑2 | rowek podkładki panelu po przekątnej: od (±55, ±55) |
| panel_slot_pitch_max | 130 | mm | R50‑2 | do (±65, ±65) |
| panel_slot_w | 3.4 | mm | R50‑2 | szerokość rowka przelotowego w dnie (= panel_screw_hole_d) |
| panel_conn_zone_x | 0 | mm | DO ZMIERZENIA | środek strefy złączy HUB75 od spodu |
| panel_conn_zone_y | 0 | mm | DO ZMIERZENIA | j.w. |
| panel_conn_zone_w | 120 | mm | DO ZMIERZENIA | szerokość strefy złączy (X) |
| panel_conn_zone_h | 60 | mm | DO ZMIERZENIA | wysokość strefy złączy (Y) |
| led_pitch | 2.5 | mm | spec | raster |
| led_gap | 4 | mm | Z23 | lico diod → spód dyfuzora |
| diffuser_size | 160 | mm | spec | pleksi |
| diffuser_t | 2 | mm | spec | pleksi |
| diffuser_pocket | 162 | mm | spec | kieszeń w blacie |
| window_through | 158 | mm | D13 | otwór przelotowy w blacie |
| pi_l | 85 | mm | spec Pi 4 | długość PCB Pi |
| pi_w | 56 | mm | spec Pi 4 | szerokość PCB Pi |
| pi_hole_pitch_l | 58 | mm | spec Pi 4 | rozstaw otworów wzdłuż |
| pi_hole_pitch_w | 49 | mm | spec Pi 4 | rozstaw otworów w poprzek |
| pi_hole_edge | 3.5 | mm | spec Pi 4 | otwory od krawędzi SD i od krawędzi bocznej |
| pi_hole_d | 2.7 | mm | spec Pi 4 | otwór montażowy |
| pi_pos_x | −50 | mm | R50‑6 | narożnik PCB Pi (krawędź SD, przód), X; Pi x −50…35 |
| pi_pos_y | −28 | mm | D10 | j.w., Y |
| pi_standoff_h | 5 | mm | D4 | boss Pi (drukowany, otwór ø2,1 pod wkręt, R49) |
| pi_stack_h | 26 | mm | DO ZMIERZENIA | spód PCB Pi → szczyt stosu z Bonnetem (bez taśmy; z taśmą do 31 w zapasie R50‑1) |
| pi_clearance_top | 8 | mm | R50‑1 | zapas nad stosem Pi (taśma HUB75 + złącza panelu z kablami, łącznie do +5) |
| ~~sd_slot_l, sd_slot_w, sd_slot_x, sd_slot_y, sd_slot_r~~ | — | — | [usunięte R50‑U6] | bez szczeliny SD w dnie |
| bonnet_dc_pos_x | −50 | mm | DO ZMIERZENIA | środek gniazda DC Bonnetu na jego krawędzi (R50‑6/A‑4: domyślnie krawędź SD, wtyk w −X; korpus niezależny od kierunku) |
| bonnet_dc_pos_y | 22 | mm | DO ZMIERZENIA | j.w. |
| bonnet_dc_dir | −X | — | DO ZMIERZENIA | kierunek wtyku DC Bonnetu: −X, +X, −Y lub +Y |
| bonnet_dc_plug_len | 40 | mm | R50‑6 | wysięg wtyku DC Bonnetu poza krawędź PCB (wtyk ze śrubkami) |

### 3.3 Korpus

| Parametr | Wartość | Jedn. | Źródło | Opis |
|---|---|---|---|---|
| box_outer | 200 | mm | spec | bok zewnętrzny |
| wall_t | 2.5 | mm | spec 4.1 | grubość ścian |
| floor_t | 3 | mm | spec 4.1 | grubość dna |
| box_corner_r | 5 | mm | spec | promień pionowych krawędzi |
| box_edge_r | 3 | mm | spec | promień dolnej krawędzi |
| korpus_h | 59.6 | mm | D4/R50‑1 | wysokość korpusu bez blatu (liczona) |
| blat_top_z | 63.6 | mm | D4/R50‑1 | wierzch blatu (liczony) |
| panel_pcb_z | 54 | mm | D4/R50‑1 | spód PCB panelu (liczony) |
| panel_pad_h | 1 | mm | R5 | podkładka‑stadion na dnie pod dystansem panelu |
| panel_pad_d | 9 | mm | R5/R50‑2 | szerokość stadionu; oś wzdłuż przekątnej od (±55, ±55) do (±65, ±65) |
| panel_standoff_l | 50 | mm | R5/R50‑7 | dystans mosiężny M3 F‑F (liczony: panel_pcb_z − floor_t − panel_pad_h); bez gwintu w panelu: 45 + tulejka klejona 5 |
| panel_screw_hole_d | 3.4 | mm | R5 | szerokość rowka przelotowego w dnie pod wkręt M3 panelu (bez pogłębienia, R50‑U20) |
| ~~panel_screw_cbore_d, panel_screw_cbore_h~~ | — | — | [usunięte R50‑U20] | łeb M3 + podkładka pod dnem (2,5 < stopki 4) |
| insert_hole_m3 | 2.5 | mm | R49 | otwór pod wkręt M3 / PT 3,0 formujący gwint w PA12 (bez wkładki); po R50 tylko słupki blatu |
| insert_hole_m25 | 2.1 | mm | R49 | otwór pod wkręt M2,5 / PT 2,5 formujący gwint w PA12 (bez wkładki); bossy Pi |
| insert_depth_m3 | 7 | mm | R49 | nieużywane po R50‑U1/U8 (słupki blatu: `blat_post_hole_depth`) |
| insert_depth_m25 | 5 | mm | R49 | głębokość otworu (wkręt 6 mm przez PCB 1,6 + 4 mm gwintu) |
| vent_slot_w | 12 | mm | D14 | szczelina wylotowa |
| vent_slot_h | 3 | mm | D14 | j.w. |
| vent_slot_z | 8 | mm | D14 | oś szczelin nad dnem zewnętrznym |
| vent_slots_rear_x | −54, −18, 18, 54 | mm | R50‑U19 | 4 szczeliny tylne |
| vent_slots_side_y | −36, 0, 36 | mm | R50‑U19 | 3 szczeliny na ścianę boczną |
| ~~vent_hood_l, vent_hood_t, vent_hood_angle, vent_hood_side_margin~~ | — | — | [usunięte R50‑U4] | bez daszków; gabaryt korpusu 200 × 200 |
| floor_vent_l | 30 | mm | R50‑U19 | szczelina wlotowa w dnie (2 szt., y = ±10, x = −8) |
| floor_vent_w | 4 | mm | R50‑U19 | j.w. |
| floor_vent_x | −8 | mm | R50‑6 | środek Pi |
| foot_d | 10 | mm | zakup | stopka gumowa samoprzylepna (bryła zastępcza) |
| foot_h | 4 | mm | spec | stopka gumowa |
| ~~foot_pocket_depth, foot_pocket_d~~ | — | — | [usunięte R50‑U16] | stopki na płaskim dnie, środek 12 od krawędzi (`foot_edge_offset`, tylko proxy) |
| dc_hole_d | 12 | mm | R50‑3 | otwór gniazda DC w prawej ścianie skrzynki; ø8 przez tulejkę redukcyjną |
| dc_socket_axis | X | — | R50‑3 | oś gniazda wzdłuż X; flansza w kieszeni, nakrętka od wnętrza obudowy |
| dc_pos_x | −40 | mm | R50‑3 | płaszczyzna zewnętrzna prawej ściany skrzynki (ściana −42…−40) |
| dc_pos_y | 89 | mm | R50‑3 | oś gniazda (Y) |
| dc_pos_z | 30 | mm | Z27 | oś gniazda (Z) |
| dc_pocket_w | 51 | mm | R50‑4 | okno kieszeni w tylnej ścianie (X): x −93…−42 |
| dc_pocket_x_window | −67.5 | mm | R50‑4 | środek okna |
| dc_pocket_h | 24 | mm | Z27 | otwór kieszeni (Z), dolna krawędź Z 14 |
| dc_pocket_depth | 22 | mm | R50‑3 | głębokość skrzynki od lica ściany (do y = 78); w świetle 20; nie zależy od wtyku |
| dc_pocket_corner_r | 0 | mm | R50‑U15 | naroża okna ostre |
| dc_socket_body_d | 12 | mm | R47/R50‑3 | bryła zastępcza gniazda DC za nakrętką (walec osią X od x −40 w +X, oś (y 89, Z 30)) |
| dc_socket_body_l | 18 | mm | DO ZMIERZENIA | j.w., długość (proxy; wolne 50) |
| dc_nut_d | 15 | mm | R47 | nakrętka gniazda DC (bryła zastępcza), grubość 2, na ścianie x −40 od wnętrza |
| ~~sd_slot_r~~ | — | — | [usunięte R50‑U6] | — |
| standoff_d | 6.4 | mm | R47 | bryła zastępcza dystansu (sześciokąt 5,5) |
| usb_body_w | 16 | mm | R47 | bryła zastępcza gniazda USB (X), wysokość 14 |
| usb_body_h | 14 | mm | R47 | j.w. (Z) |
| bonnet_dc_plug_w | 10 | mm | R47 | bryła zastępcza wtyku Bonnetu, wysokość 11 |
| bonnet_dc_plug_h | 11 | mm | R47 | j.w. |
| hall_sensor_size | 4 × 5 × 1.5 | mm | R47 | bryła zastępcza czujnika Halla (X × Y × Z) |
| dc_pocket_wall | 2 | mm | Z27 | ścianki skrzynki kieszeni |
| usb_cut_w | 16 | mm | R50‑5 | okno gniazda USB‑A panelowego (największe typowe z ramką; pod flanszą) |
| usb_cut_h | 9 | mm | R50‑5 | j.w. |
| usb_slot_pitch_min | 23 | mm | R50‑5 | rowki poziome 3,2 × 5,7 zamiast otworów flanszy: osie od usb_pos_x ± 11,5 … (23, nie 20: ścianka do okna 1,9 ≥ 1,5; flansza 22 → spiłować 0,5) |
| usb_slot_pitch_max | 28 | mm | R50‑5 | … do ± 14; flansza z otworami pionowymi → wiercenie ø3,2 |
| usb_slot_w | 3.2 | mm | R50‑5 | szerokość rowka |
| usb_hole_pitch | 22 | mm | DO ZMIERZENIA | rozstaw 2 × ø3,2 flanszy USB (tylko bryła zastępcza) |
| usb_pos_x | 60 | mm | R10 | tylna ścianka (korpus gniazda wewnątrz: x 52…68, y 77…97,5) |
| usb_pos_z | 24 | mm | D | j.w. |
| label_text_h | 8 | mm | D15 | wysokość liter napisu |
| label_relief_h | 0.6 | mm | spec | relief napisu |
| label_pos_z | 51 | mm | D15/R50‑1 | środek napisu, x = 0 (liczony: korpus_h − 8,6) |
| snap_pocket_w | 10 | mm | D9 | ślepa kieszeń zatrzasku w ścianie |
| snap_pocket_h | 2.5 | mm | D9 | j.w. |
| snap_pocket_depth | 1.0 | mm | R6 | j.w., od wewnątrz (zostaje 1,5 ścianki) |
| snap_pocket_z | 52.6 | mm | D9/R50‑1 | dolna krawędź kieszeni (liczona: korpus_h − 7) |
| snap_side_y | 0 | mm | R6 | kieszeń/haczyk na lewej i prawej ścianie: y |
| snap_front_x | 50 | mm | R6 | kieszeń/haczyk na przedniej ścianie: x |
| snap_rear_x | −50 | mm | R6 | kieszeń/haczyk na tylnej ścianie: x |
| blat_screw_pitch | 150 | mm | R7 | 2 × M3 w tylnej ściance, x = ±75 |
| blat_screw_z | 55 | mm | D9/R50‑1 | j.w. (liczony: korpus_h − 4,6) |
| ~~holder_pos_x, holder_pos_y, holder_axis, holder_boss_d, holder_boss_h~~ | — | — | [usunięte R50‑U8] | bez uchwytów kabli i bossów; podstawki opasek samoprzylepne |
| ~~rib_w, rib_h, rib_start_r~~ | — | — | [usunięte R50‑U5] | bez żeber dna |

### 3.4 Blat, wkładka (rama dyfuzora usunięta, R50‑U1)

| Parametr | Wartość | Jedn. | Źródło | Opis |
|---|---|---|---|---|
| blat_t | 4 | mm | D9 | grubość płyty blatu |
| blat_skirt_h | 10 | mm | D9 | kołnierz pod blatem |
| blat_skirt_t | 2 | mm | D9 | grubość kołnierza |
| blat_skirt_clearance | 0.5 | mm | R48 | luz kołnierz–ściana na stronę (SLS ±0,3 na 200 mm) |
| blat_corner_r | 5 | mm | spec | jak korpus |
| snap_hook_w | 8 | mm | D9 | haczyk zatrzasku |
| snap_hook_h | 1.3 | mm | R48 | występ haczyka (zahacza 0,8 w kieszeni 1,0) |
| pi_boss_d | 8 | mm | R48/R49 | boss Pi (ścianka 2,95 wokół otworu ø2,1 pod wkręt formujący gwint) |
| blat_post_w | 8 | mm | R48 | słupek blatu w X (x ±71…79) |
| snap_hook_z | 52.85 | mm | R47/R50‑1 | dolna krawędź występu haczyka (globalnie, liczona: korpus_h − 6,75); lokalnie −10,75 |
| snap_hook_hgt | 2.0 | mm | R47 | wysokość występu haczyka (Z 52,85…54,85) |
| snap_hook_arm_l | 9 | mm | R47 | długość nacięć od dolnej krawędzi kołnierza (do Z 58,6; lokalnie −5) |
| snap_notch_w | 1 | mm | R47 | szerokość nacięcia obok haczyka |
| blat_post_y0 | 89.2 | mm | R47 | słupek blatu y 89,2…95,2 (po wewnętrznej stronie kołnierza) |
| blat_post_hole_depth | 6 | mm | R49a | otwór ø2,5 w słupku od lica 97,0 do 91,0 (dno 1,8) |
| blat_screw_csink_d | 6.3 | mm | R47 | pogłębienie stożkowe 90° otworu wkrętu blatu w ścianie korpusu |
| snap_hook_t | 1.5 | mm | D9 | grubość ramienia |
| ~~rama_outer, rama_inner, rama_h, rama_screw_pos, rama_ear_t, rama_ear_d, rama_ear_hole_d, rama_tab_size, rama_tab_inner, rama_boss_d, rama_boss_h~~ | — | — | [usunięte R50‑U1] | rama dyfuzora i bossy ramy w blacie usunięte |
| insert_opening | 96.6 | mm | spec | otwór wkładki |
| insert_wall_w | 4 | mm | spec | szerokość ramy |
| insert_h | 6 | mm | Z7 | wysokość ramy |
| insert_shelf | 12 | mm | D5 | bok półki narożnej |
| insert_shelf_h | 2.5 | mm | D5 | grubość półki |
| hall_pocket_w | 5.0 | mm | D5 | kieszeń TO‑92 (X) |
| hall_pocket_l | 5.5 | mm | D5 | kieszeń TO‑92 (Y), przelotowa |
| hall_lead_channel_w | 2.5 | mm | D5 | kanał wyprowadzeń pod półką |
| hall_lead_channel_h | 1.0 | mm | R20 | j.w. (nad kanałem zostaje 1,5 półki) |
| orient_post | 4.4 | mm | D5 | kołek kwadratowy, półka D |
| orient_post_h | 5 | mm | D5 | wysokość kołka nad półką |
| orient_post_gap | 0.5 | mm | D5 | odstęp kołka od ścian otworu |
| finger_cut_w | 30 | mm | spec | wycięcie palcowe, przedni bok ramy, pełna wysokość |
| tab_w | 14 | mm | D12 | ucho wkładki |
| tab_end_y | 96 | mm | D12 | koniec ucha (Y) |
| tab_t | 3 | mm | D12 | grubość ucha |
| tab_pos_x | 58 | mm | D12 | środki uszu x = ±58 |
| tab_pin_d | 3 | mm | D12 | kołek ustalający |
| tab_pin_h | 3.5 | mm | D12 | j.w. |
| tab_pin_y | 93.5 | mm | D12 | j.w. |
| tab_magnet_y | 86 | mm | D12 | magnes ucha i blatu |
| blat_pin_hole_d | 3.3 | mm | D12 | otwór kołka w blacie, ślepy od góry |
| blat_pin_hole_depth | 3.8 | mm | R8 | głębokość otworu kołka (blat 4,0 → zostaje 0,2 dna; pył nie wpada) |
| blat_magnet_pocket_d | 5.4 | mm | D12 | kieszeń magnesu w blacie, od góry |
| blat_magnet_pocket_depth | 2.3 | mm | D12 | j.w. |
| wire_slot_l | 8 | mm | D12 | szczelina kabla Halla w blacie (Y) |
| wire_slot_w | 4 | mm | D12 | j.w. (X), środek (±66, 90) |
| wire_rabbet | 1.5 | mm | D12 | rowek na kable, zewn. dolna krawędź ramy: wysokość |
| wire_rabbet_w | 2.5 | mm | R50‑U9 | rowek: szerokość (x 52,3 → 49,8; do otworu zostaje 1,5); jedna bryła z przelotem w ściance narożnika |
| tab_root_x_in | 44 | mm | R47 | nasada ucha: x od ±44 do ±65 |
| tab_root_y0 | 48.8 | mm | R47 | nasada ucha: y od 48,8 do 58 |
| tab_root_y1 | 58 | mm | R47 | j.w. |
| insert_opening_r | 0 | mm | R50‑U15 | naroża otworu wkładki ostre |
| orient_post_chamfer | 1 | mm | 4.6 | faza wierzchołka kołka orientacyjnego |
| tab_pin_chamfer | 0.5 | mm | 4.6/R50‑U10 | kołek ustalający jako jedna bryła: walec ø3 × 3,0 + stożek ścięty ø3 → ø2 na 0,5 |
| insert_label_h | 0 | mm | R51 | 0 = bez napisu „PRZÓD” (tylko strzałki) |
| insert_label_x | 32 | mm | R47 | środek napisu |
| insert_label_y | −51.15 | mm | R47 | j.w. |
| insert_arrow_x | ±32 | mm | R47/R51 | środki strzałek (oba segmenty przedniego boku) |
| insert_arrow_l | 2 | mm | R47 | strzałka: trójkąt, wymiar wzdłuż Y |
| insert_arrow_w | 3 | mm | R47 | strzałka: trójkąt, wymiar wzdłuż X |

### 3.5 Małe części: odbiornik, tulejka DC, podkładki panelu (uchwyt kabli usunięty, R50‑U8)

| Parametr | Wartość | Jedn. | Źródło | Opis |
|---|---|---|---|---|
| ~~holder_l, holder_w, holder_h, holder_foot_t, holder_slot_w, holder_slot_h, holder_comb_t, holder_board_groove_w, holder_board_groove_depth, proto_board_l, proto_board_w~~ | — | — | [usunięte R50‑U8] | uchwyt kabli → podstawki opasek samoprzylepne; płytka proto na taśmie VHB |
| receiver_l | 19 | mm | DO ZMIERZENIA | odbiornik USB nano (tylko bryła zastępcza, korpus P) |
| receiver_w | 15 | mm | DO ZMIERZENIA | j.w. |
| receiver_h | 6 | mm | DO ZMIERZENIA | j.w. |
| dc_bush_outer_d | 12 | mm | R50‑3 | tulejka redukcyjna DC: ø zewn. (= dc_hole_d) |
| dc_bush_inner_d | 8.2 | mm | R50‑3 | otwór pod gniazdo ø8 |
| dc_bush_t | 2 | mm | R50‑3 | długość części walcowej (= grubość ściany skrzynki) |
| dc_bush_flange_d | 15 | mm | R50‑3 | kołnierz po stronie kieszeni |
| dc_bush_flange_t | 1 | mm | R50‑3 | j.w. |
| panel_shim_d | 9 | mm | R50‑8 | podkładka dystansowa panelu (krążek) |
| panel_shim_hole_d | 3.4 | mm | R50‑8 | j.w. |
| panel_shim_t | 0.5 / 1 / 2 | mm | R50‑8 | trzy grubości → trzy STL |

### 3.6 Parametry sterujące skryptem

| Parametr | Wartość | Jedn. | Źródło | Opis |
|---|---|---|---|---|
| file_suffix | v2 | — | R17 | sufiks nazw plików STL |
| label_text_W | RAMKA WIECZORNA | — | Z18 | napis na korpusie W |
| label_text_P | RAMKA PORANNA | — | Z18 | napis na korpusie P |
| font_name | Inter | — | R22 | font wbudowany w Blender 5.2 (`datafiles/fonts/Inter.woff2`) |
| font_offset | 0.2 | mm | R22 | pogrubienie liter (`TextCurve.offset`); wykonawca dobiera tak, by trzon ≥ 1,0 i raportuje |
| fillet_outer_default | 3 | mm | R26 | promień zewnętrzny niewymieniony w planie |
| fillet_inner_default | 1 | mm | R26 | promień wewnętrzny niewymieniony w planie |
| color_graphite | #3b3e43 | — | R27 | kolor renderu PA12 grafit |
| color_white | #efede6 | — | R27 | kolor renderu PA12 naturalny |
| color_plexi | #e8ecef | — | R27 | pleksi mleczna (półprzezroczysta) |
| color_pcb | #1f6b3a | — | R27 | PCB |
| color_brass | #c8a24a | — | R27 | mosiądz (dystanse) |
| cost_rate_min | 0.9 | zł/cm³ | sekcja 11 | stawka wariantu najtańszego |
| cost_rate_max | 1.6 | zł/cm³ | sekcja 11 | stawka górna |
| cost_dye_factor | 1.2 | — | sekcja 11 | barwienie (+20 %) |
| cost_smooth_factor | 1.3 | — | sekcja 11 | wygładzanie (+30 %) |

---
## 4. Specyfikacja części do zamówienia

Układ współrzędnych: jak w D3 (globalny; płytki i pokrywka w układzie lokalnym płytki). Każda część modelowana w położeniu montażowym, a przed eksportem przesunięta tak, by największa płaska ściana leżała na Z = 0. Wszystkie luzy ruchome 0,3 mm na stronę, wciskane 0,15 mm, zapas na chropowatość SLS 0,3 mm wliczony w podane otwory.

### 4.1 `ramka_plytka_wieczorna_v2.stl` i `ramka_plytka_poranna_v2.stl`
- Funkcja: nośnik prac do skanera i do ramki; wspólna geometria, różne gniazda.
- Gabaryt: `plate_size` × `plate_size` × `plate_thickness` = 96 × 96 × 8; pionowe krawędzie R 1, górne krawędzie faza 0,5.
- Cechy wspólne (układ lokalny, wierzch płytki Z = 0, materiał w dół do Z = −8):
  1. Gniazda stożkowe: wierzch ø d, dno ø d − 2·4·tan15° = d − 2,14, głębokość 4, otwór ø3 przelotowy w osi. Pozycje: D6.
  2. Rynienki: obrys z zaokrąglonymi końcami (stadion) l × w, ścianki 15°, głębokość 4, 4 otwory ø3 na osi w rozstawie `ev_/mo_trough_hole_pitch`, symetrycznie względem środka rynienki. Pozycje: D6.
  3. Stożki znaczników ø5 × 3 (wierzchołek w dół) w A (−42, −42), B (−42, 42), C (42, 42).
  4. Wycięcie 5 × 5 przelotowe w D: x ∈ [43, 48], y ∈ [−48, −43].
  5. Dołki kodu ø2 × 1 (R3): bit A (−45,0, −36), bit B (−45,0, −33), bit C (−45,0, −30). Plik bazowy `ramka_plytka_<typ>_v2.stl`: wszystkie 3 dołki wycięte, BEZ cyfry reliefu (wzorzec do sprawdzeń). Warianty do zamówienia (R4): `_n1…_n3` (wieczorna), `_n4…_n6` (poranna) — dołki tylko dla bitów = 1 numeru (n = A + 2B + 4C), cyfra reliefu = n; po 1 szt. każdego wariantu.
  6. Kieszenie magnesów od spodu ø5,2 × 2,2, współosiowe ze znacznikami A, B, C (Z4). Wszystkie 3 kieszenie w każdej płytce (magnes wklejony lub nie).
  7. Numer: relief 0,6, cyfra 5 mm, środek (39,5, −44,5), font `font_name` (R22); tylko w wariantach numerowanych.
  8. Rowek pokrywki 1,0 wysoki × 0,8 głęboki wokół 4 boków, środek 2 mm pod wierzchem; przerwany w wycięciu D.
- Luzy: płytka w otworze wkładki 96,6 → 0,3 na stronę; wycięcie 5 × 5 na kołek 4,4 → 0,3.
- Łączy się z: wkładka (półki, kołek), pokrywka (rowek), magnesy, skaner.
- Orientacja do druku: gniazdami do góry, spód płaski na stole.
- Ilość: 3 + 3 (n1, n2, n3 wieczorne; n4, n5, n6 poranne). Materiał: PA12 naturalny biały, mat, bez wygładzania. Alternatywa: SLA półprzezroczysta (wieczorna), CNC PMMA opal (poranna; wtedy STEP przez FreeCAD).
- Plik JSON obok każdej płytki (R13): `uklad_gniazd_wieczorna.json`, `uklad_gniazd_poranna.json` — źródło prawdy układu gniazd: skrypt CZYTA je i z nich buduje gniazda; pierwszą wersję skrypt generuje z D6, gdy plik nie istnieje. Struktura:
  ```json
  {"plate":"wieczorna","version":"v2","units":"mm",
   "coords":{"origin":"środek górnej powierzchni płytki","x":"w prawo (od użytkownika)","y":"do tyłu","notch_corner":"D = (+48, -48), przód-prawy"},
   "size":96,"thickness":8,
   "markers":[{"corner":"A","x":-42,"y":-42,"d":5,"depth":3},{"corner":"B","x":-42,"y":42,"d":5,"depth":3},{"corner":"C","x":42,"y":42,"d":5,"depth":3}],
   "notch":{"corner":"D","x_min":43,"x_max":48,"y_min":-48,"y_max":-43},
   "code_dimples":[{"bit":"A","x":-45.0,"y":-36},{"bit":"B","x":-45.0,"y":-33},{"bit":"C","x":-45.0,"y":-30}],
   "magnet_pockets":[{"corner":"A","x":-42,"y":-42},{"corner":"B","x":-42,"y":42},{"corner":"C","x":42,"y":42}],
   "number_relief":{"x":39.5,"y":-44.5,"text_h":5},
   "sockets":[
     {"id":1,"type":"round","x":30,"y":-40.5,"d_top":9,"d_bottom":6.86,"depth":4,"hole_d":3},
     {"id":25,"type":"trough","x":0,"y":19.5,"l":60,"w":15,"angle":0,"depth":4,"hole_d":3,"hole_pitch":12,"hole_count":4}
   ],
   "leds":{}}
  ```
  `id` rzędami od przodu (R1, R2, …), w rzędzie od prawej (od strony narożnika D z wycięciem) do lewej; `d_bottom = d_top − 2·depth·tan(15°)` (9 → 6,86; 12 → 9,86; 15 → 12,86; 7,5 → 5,36; 10 → 7,86; 12,5 → 10,36). `leds` wypełnia kalibracja (sekcja 9).; `leds` wypełnia kalibracja (sekcja 9).

### 4.2 `ramka_pokrywka_v2.stl`
- Funkcja: osłona prac na czas przenoszenia; jedna na obie płytki.
- Gabaryt: (96 + 2·0,3 + 2·1,5) = 99,6 × 99,6 × (14 + 2 + 4) = 20 mm w STL (bez reliefu — R50‑U14); pionowe krawędzie R 3.
- Cechy: wnęka 96,6 × 96,6 × 18 (od dołu), wierzch 2 mm pełny; kołnierz 1,5 mm; 4 garby zatrzaskowe 10 (szer.) × 0,8 (wys. w Z) × 0,7 (występ), czubek półokrąg R 0,4 (`cover_snap_r`), na wewnętrznej stronie kołnierza, środek garbu 2 mm nad dolną krawędzią kołnierza (lokalnie Z −18 = rowek płytki 2 mm pod jej wierzchem), w położeniach R42 (lewy/prawy bok y = 0, przód x = +25, tył x = −25); wycięcie 30 × 3 na palec na dolnej krawędzi przedniego i tylnego boku. **[usunięte R50‑U17]** 6 otworów ø4 w wierzchu. **[usunięte R50‑U14]** napis „GÓRA” (druk FDM wierzchem w dół; góra jest oczywista — wierzch pełny, dół otwarty).
- Luzy: 0,3 na stronę do płytki; garb 0,7 w rowek 0,8.
- Rachunek wysokości: wierzch płytki 0 → najwyższa praca +10 (14 − 4) → prześwit 4 → spód wierzchu pokrywki +14 ✓.
- Orientacja: wierzchem w dół (największa płaska ściana). Ilość 4. **PETG FDM, druk własny (0,2 mm)**; nie w arkuszu drukarni.

### 4.3 `ramka_korpus_W_v2.stl`, `ramka_korpus_P_v2.stl`
- Funkcja: dno i ściany; niesie panel, Pi, gniazda tylne. Dwa pliki różnią się tylko napisem (Z28).
- Gabaryt: 200 × 200 × 59,6 (R50‑1; bez daszków, R50‑U4); ściany 2,5, dno 3, R 5 pionowe, R 3 dolna krawędź. Wnętrze 195 × 195.
- Cechy (globalne XYZ):
  1. 4 podkładki panelu w kształcie stadionu 9 szer. × 1 wys. na dnie (Z 3…4), oś wzdłuż przekątnej narożnika od (±55, ±55) do (±65, ±65) (`panel_slot_pitch_min/max` 110…130, R50‑2); w dnie pod każdą rowek przelotowy 3,4 szer. o tej samej osi (długość 14,1 + 3,4 = 17,5); bez pogłębienia (R50‑U20: wkręt M3 × 10 z podkładką ø9 od spodu, łeb 2,5 pod dnem, stopki 4). Dystans 50 F‑F na podkładce (R50‑7). Wzór otworów panelu niekwadratowy lub z offsetem → wiercenie ø4 w dnie w zmierzonym miejscu + podkładka R50‑8 (fallback bez nowego korpusu).
  2. 4 bossy Pi ø8 × 5 (R48) na dnie, osie: (−46,5, −24,5), (11,5, −24,5), (−46,5, 24,5), (11,5, 24,5) (R50‑6); otwór ø2,1 × 5 pod wkręt M2,5 formujący gwint (R49, bez wkładek).
  3. **[usunięte R50‑U6]** Szczelina SD w dnie.
  4. 2 szczeliny wlotowe w dnie 30 × 4, środki (−8, ±10) (R50‑U19, R50‑6).
  5. Szczeliny wylotowe 12 × 3 **bez daszków** (R50‑U4): tylna ścianka 4 szt., środki x = −54, −18, 18, 54, Z = 8; lewa i prawa ścianka po 3 szt., y = −36, 0, 36, Z = 8 (R50‑U19).
  6. Tylna ścianka: kieszeń DC — okno 51 × 24 (x −93…−42, Z 14…38, naroża ostre R50‑U15) i skrzynka za nim: zewnętrznie x −97,5…−40 (lewa ściana skrzynki = lewa ściana korpusu), y 78…100, Z 12…40, ściany 2, wnętrze otwarte tylko przez okno (R50‑4); **w prawej ścianie skrzynki** (płaszczyzna x = −40, ściana −42…−40) otwór gniazda DC ø12, oś (y 89, Z 30) wzdłuż X (R50‑3; gniazdo ø8 przez tulejkę 4.9); okno USB 16 × 9 w (60, Z 24) + 2 rowki poziome 3,2 × 5,7 o osiach od (60 ± 11,5) do (60 ± 14), Z 24 (R50‑5; rozstaw flanszy 23…28; rowek x 44,4…50,1 i 69,9…75,6 → ścianka do okna 1,9) (R10); 2 otwory ø3,2 z pogłębieniem stożkowym ø6,3 / 90° pod wkręt M3 w (±75, Z 55) (wkręty blatu, R7, R50‑1).
  7. Przednia ścianka: gładka, bez otworów (Z28); tylko napis relief 0,6 „RAMKA WIECZORNA” (W) / „RAMKA PORANNA” (P), litery 8 mm, środek (0, Z 51) (`label_pos_z` = korpus_h − 8,6).
  8. Kieszenie zatrzasków blatu (R6): 4 szt., 10 × 2,5 × 1,0 od wewnątrz, dolna krawędź Z 52,6 (`snap_pocket_z` = korpus_h − 7); lewa ściana y = 0, prawa ściana y = 0, przednia ściana x = +50, tylna ściana x = −50.
  9. **[usunięte R50‑U8]** Bossy uchwytów kabli. Zamiast nich: podstawki opasek samoprzylepne 20 × 20 (lista zakupów) na dnie przy lewej ścianie (trasa DC) i przy tylnej ścianie (Hall); płytka proto Halla na taśmie VHB na lewej ścianie Z 40.
  10. **[usunięte R50‑U16]** Gniazda stopek; stopki samoprzylepne na płaskim dnie, środek 12 od krawędzi.
  11. **[usunięte R50‑U5]** Żebra dna.
- Orientacja: dnem w dół. Ilość: 1 W + 1 P. PA12 grafit. Powierzchnie zewnętrzne pod wygładzanie (wariant pokazowy).

### 4.4 `ramka_blat_v2.stl`
- Funkcja: górna płyta z oknem i kieszenią dyfuzora, nosi wkładkę (rama dyfuzora usunięta, R50‑U1).
- Gabaryt: 200 × 200 × 4 + kołnierz 10 w dół = 14; R 5 pionowe, R 1,5 górna krawędź. Położenie globalne: wierzch Z 63,6, kołnierz do 49,6 (R50‑1); geometria lokalna bez zmian.
- Cechy:
  1. Kieszeń dyfuzora 162 × 162 × 2 od góry (środek 0,0), otwór przelotowy 158 × 158; naroża kieszeni ostre (R50‑U15; pleksi bez fazowania, R29 uchylone).
  2. Kołnierz: obrys 194,0 × 194,0 (195 − 2·0,5; luz 0,5 na stronę ze względu na dokładność SLS ±0,3 mm na 200 mm, R48), grubość 2, wysokość 10, R 4,5; 4 haczyki zatrzaskowe 8 szerokie, występ 1,3 (97,0 → 98,3; zahacza 0,8 w kieszeni 97,5…98,5), grubość ramienia 1,5, w położeniach R6 (lewa/prawa y = 0, przednia x = +50, tylna x = −50); występ haczyka zajmuje lokalnie Z −10,75…−8,75 (globalnie 52,85…54,85, `snap_hook_z`, `snap_hook_hgt` 2,0; luz 0,25 w kieszeni korpusu Z 52,6…55,1, R47, R50‑1) z rampą naprowadzającą od dołu; nacięcia `snap_notch_w` 1 mm po obu stronach każdego haczyka od dolnej krawędzi kołnierza (lokalnie −14) do lokalnie −5 (ramię `snap_hook_arm_l` 9 mm, 1 mm nasady pod płytą).
  3. 2 słupki 8 (X) × 6 (Y) × 10 po wewnętrznej stronie tylnego kołnierza: x ±71…79 (R48), y 89,2…95,2 (zrośnięte z kołnierzem 95,0…97,0 po R48), lokalnie Z −14…−4 (R7, R47); otwór ø2,5 × 6 pod wkręt M3 formujący gwint (R49, R49a) poziomo (oś Y) od zewnętrznego lica kołnierza y 97,0 (po R48) do 91,0, dno 1,8 ≥ 1,5, oś lokalnie Z −8,6 (globalnie 55 = `blat_screw_z`); wkręt M3 × 8: 2,5 w ścianie + 5,5 w gwincie. Zostają (R50‑U2 odrzucone przez właściciela).
  4. **[usunięte R50‑U1]** 4 bossy ø8 × 6 pod spodem w (±90, ±90) (rama dyfuzora). Spód blatu poza kołnierzem i słupkami płaski.
  5. Otwory kołków wkładki ø3,3 ślepe 3,8 głębokie od góry w (±58, 93,5) (R8); kieszenie magnesów ø5,4 × 2,3 od góry w (±58, 86); szczeliny kabli 4 (X) × 8 (Y) przelotowe w (±66, 90).
  6. Bez żebra obwodowego pod blatem (R41); sztywność daje kołnierz 10 mm.
- Rachunek „wkładka w oknie blatu”: rama wkładki 104,6 × 104,6 leży na dyfuzorze 160 → margines 27,7 mm wolnego dyfuzora z każdej strony; uszy (y 52,3…96) leżą częściowo na dyfuzorze (do y = 81) i częściowo na blacie (dyfuzor licowany z blatem, R30); kołki, magnesy i szczeliny kabli (y 86…94) leżą w litym blacie poza kieszenią (y > 81) i poza słupkami (x ±71…79) ✓.
- Łączy się z: korpus (kieszenie zatrzasków, wkręty tylne), dyfuzor (kieszeń), wkładka (kołki, magnesy, szczeliny).
- Orientacja: wierzchem w dół. Ilość 2. PA12 grafit.

### 4.5 `ramka_rama_dyfuzora_v2.stl` — usunięta [R50‑U1]
Brak pliku. Panel ustalają 4 dystanse M3 w jego otworach (±0,2); światło i pył z krawędzi panelu trafiają tylko do wnętrza obudowy (korpus zamknięty, luz kołnierza blatu 0,5 to zamierzony wylot D14). Bez pianki ani innego uszczelnienia (decyzja właściciela). Bossy ramy w blacie usunięte (4.4.4).

### 4.6 `ramka_wkladka_v2.stl`
- Funkcja: gniazdo płytki, nośnik 3 czujników Halla i kołka orientacji.
- Gabaryt: rama 104,6 × 104,6 × 6 + 2 uszy (x ±51…65) do y = 96 → obrys 130 × 148,3; wysokość z kołkiem orientacyjnym 7,5 i kołkami ustalającymi 3,5 pod spodem = 11,0 w STL; Z lokalne: spód ramy 0 (na dyfuzorze).
- Cechy:
  1. Otwór 96,6 × 96,6, naroża wewnętrzne ostre (R50‑U15); ścianka 4 szeroka, 6 wysoka, górna krawędź wewnętrzna faza 1 × 45° (naprowadzenie płytki).
  2. 4 półki narożne 12 × 12 × 2,5 wewnątrz otworu (naroża A, B, C, D), górna powierzchnia Z 2,5.
  3. Półki A, B, C: kieszeń przelotowa 5,0 × 5,5 (X × Y), środek pod osią magnesu płytki: A (−42, −42), B (−42, 42), C (42, 42); kanał 2,5 × 1,0 (R20) od kieszeni do ścianki ramy po przekątnej narożnika, pod półką (otwarty od dołu); w ściance ramy przelot 2,5 szer. × 1,5 wys. od spodu, po przekątnej narożnika od (−48,3, −48,3) do (−52,3, −52,3) (analogicznie B i C) — **jedna bryła tnąca ciągła z rowkiem zewnętrznym** (ten sam przekrój 2,5 × 1,5, R50‑U9).
  4. Półka D (42, −42): kołek 4,4 × 4,4 × 5 (nad półką), ścianki zewnętrzne kołka 0,5 od ścian otworu; wierzchołek sfazowany 1 mm.
  5. Wycięcie palcowe 30 × pełna wysokość w przednim boku ramy (x ∈ [−15, 15], y = −48,3 … −52,3).
  6. Rowek kablowy 2,5 szer. × 1,5 wys. (R50‑U9; `wire_rabbet_w` × `wire_rabbet`) na zewnętrznej dolnej krawędzi lewego, tylnego i prawego boku (od A do ucha lewego; od C do ucha prawego; B wprost do ucha lewego); od x 52,3 do 49,8 → do otworu 48,3 zostaje 1,5 ✓; 3 żyły AWG 28 ø0,9: 2 obok + 1 nad.
  7. Uszy: 14 × 43,7 × 3, od y = 52,3 do 96, środki x = ±58 (x ±51…65); **nasada ucha w kształcie L** (R47, U‑1, poprawka R51): płytka 3 mm grubości, Z 0…3: część wewnątrz obrysu ramy x ±(44…52,3), y 48,8…58 (zakładka 8,3 × 3,5 × 3 ze ścianką tylną) + część na pasie tylnym x ±(52,3…65), y 52,3…58; NIC poza obrysem ramy dla y < 52,3 (prawy pas marginesu odsłonięty, K‑56); kołek ø3 × 3,5 w dół w (±58, 93,5) jako jedna bryła: walec ø3 × 3,0 + stożek ścięty ø3 → ø2 na ostatnich 0,5 (R50‑U10); otwór ø5,4 przelotowy w (±58, 86); kanał kablowy 2 × 1,2 od spodu: pod nasadą od rowka tylnego boku ramy do x = ±64, dalej pod uchem wzdłuż x = ±64 od y = 52,3 do 90, wylot na krawędzi zewnętrznej ucha nad szczeliną blatu (±66, 90). Spód ramy i uszu (Z 0…3) jako jeden obrys, góra ramy (Z 3…6) jako pierścień.
  8. Bez napisu „PRZÓD” (R51: litery 2 mm nie dają trzonu ≥ 1,0 — nieczytelne; orientację wymusza kołek). Zostaje strzałka ku −Y: trójkąt ▼ `insert_arrow_l` 2 (Y) × `insert_arrow_w` 3 (X), relief 0,6, na obu segmentach przedniego boku: środki (−32, −51,15) i (32, −51,15).
- Luzy i rachunek „płytka we wkładce”: 96 + 2·0,3 = 96,6 ✓; powtarzalność ±0,3 (luz) + kołek 4,4 w 5 (±0,3) → ±0,5 wymagane ✓ (kołek dociska płytkę do narożnika D przy ułożeniu).
- Magnes–czujnik: D5, 1,7 mm ≤ 4 ✓.
- Orientacja: spodem w dół. Ilość 2 + 1 zapas. PA12 naturalny biały.

### 4.7 Głowica czujnika gestu — usunięta (Z28)
Brak pliku. Brak otworów w przedniej ściance.

### 4.8 Zaślepka otworu przycisku — usunięta (Z28)
Brak pliku; otworu przycisku nie ma.

### 4.9 `ramka_uchwyt_kabli_v2.stl` — usunięty [R50‑U8]; zamiast niego `ramka_tulejka_dc_v2.stl` i `ramka_podkladka_panelu_{05,1,2}_v2.stl`
- Uchwyt kabli: brak pliku. Wiązki trzymają podstawki opasek samoprzylepne 20 × 20 (6 szt., lista zakupów), płytka proto Halla 30 × 20 przyklejona taśmą VHB do lewej ściany korpusu na Z 40 (PA12 przemyć IPA przed klejeniem).
- `ramka_tulejka_dc_v2.stl` (R50‑3): tulejka redukcyjna gniazda DC — walec ø`dc_bush_outer_d` 11,85 (R52) × `dc_bush_t` 2 z otworem ø`dc_bush_inner_d` 8,2 i kołnierzem ø`dc_bush_flange_d` 15 × `dc_bush_flange_t` 1 po stronie kieszeni; wciskana w otwór ø12 ściany skrzynki, nakrętka gniazda ø8 dociska ścianę + tulejkę. Używana tylko gdy pomiar #16 da gwint ø8. Orientacja: kołnierzem w dół. Ilość 2. Żywica w firmie / PETG, druk własny.
- `ramka_podkladka_panelu_05_v2.stl`, `…_1_v2.stl`, `…_2_v2.stl` (R50‑8): krążki ø`panel_shim_d` 9 z otworem ø`panel_shim_hole_d` 3,4, grubości `panel_shim_t` 0,5 / 1 / 2; do wyrównania długości dystansu po pomiarach #4/#9 i jako podkładka pod słupek w wywierconym otworze fallbacku R50‑2. Ilość po 8. Żywica / PETG, druk własny.

### 4.10 Podstawka klawiatury — usunięta (Z26)
Klawiatura leży luzem na stole. Brak pliku, brak nalepki.

---
### 4.11 Rachunki spójności — zbiorczo
| Sprawdzenie | Rachunek | Wynik |
|---|---|---|
| Łańcuch wysokości (R50‑1) | 3 + 5 + 26 + 8 + 12 = 54 (spód PCB panelu); + 1,6 + 2 + 4 + 2 = 63,6 (wierzch blatu); korpus 63,6 − 4 = 59,6 | 63,6 > spec 60 o 3,6 — zaakceptowane przez właściciela (zapas na kable) |
| Zapas nad stosem Pi (R50‑1) | spód strefy złączy panelu 54 − 12 = 42; szczyt stosu 8 + 26 = 34 → 8; z taśmą (stos 31) i kablami panelu (17): 54 − 17 = 37 ≥ 8 + 31 = 39? NIE → łączny nadmiar ≤ 5 (np. 31 + 12 albo 26 + 17) ✓; większy nadmiar tylko w tym samym miejscu XY — unikać obrotem panelu (złącza nad kolumną słupków) | ✓ (warunkowo) |
| Luz dioda–dyfuzor (R50‑1) | 63,6 − 2 − (54 + 1,6 + led_h) = 6 − led_h → led_h 1/2/3 → 5/4/3 | w spec 3–5 ✓ |
| Panel na słupkach (R50‑7) | 3 (dno) + 1 (podkładka) + 50 (dystans F‑F) = 54 = `panel_pcb_z`; bez gwintu: 3 + 1 + 45 + 5 (tulejka) = 54 | ✓ |
| Rowki panelu vs sąsiedzi (R50‑2) | słupek ø6,4 skrajnie w (±65, ±65) → do 68,2: skrzynka DC y ≥ 78 (9,8), gniazdo USB wewn. y ≥ 77 (8,8), Pi y ≤ 28 / x ≤ 35 (≥ 21,8); skrajnie w (±55, ±55) → od 51,8: Pi x ≤ 35 (16,8); kołnierz blatu wewn. 95 ✓ | ✓ |
| Wkręt panelu pod dnem (R50‑U20) | łeb M3 2,0 + podkładka 0,5 = 2,5 < stopki 4 → 1,5 zapasu nad blatem stołu | ✓ |
| Dołki kodu (R3) | (−45,0, −36/−33/−30) ø2: do krawędzi płytki 48 − 46,0 = 2,0; do rowka pokrywki (x od −47,2, Z −1,5…−2,5): √(1,2² + 0,5²) = 1,3 → po przekątnej 1,3 ≥ 1,5? NIE przy −45,5 (0,86), TAK przy −45,0 w rzucie poziomym 1,2 + dołek kończy się na Z −1, rowek zaczyna na Z −1,5 → materiał między nimi 1,3 mm w najkrótszym kierunku (lokalnie, nie ścianka nośna, R47); do stożka A (−42, −42) ø5: √(3² + 6²) − 2,5 − 1 = 3,2; do gniazda wieczornej R2 (−36, −28,5) ø9: √(9² + 1,5²) − 4,5 − 1 = 3,6; do gniazda porannej R2 (−36,75, −30,75) ø7,5: √(8,25² + 0,75²) − 3,75 − 1 = 3,5 | ✓ |
| Słupki blatu i szczeliny kabli (R7, R47, R48) | słupki x ±71…79, y 89,2…95,2 (po wewnętrznej stronie kołnierza, nie w ścianie korpusu); szczeliny x ±64…68, y 86…94 → 3 mm odstępu; kieszenie magnesów ø5,4 w (±58, 86) → 10,3 mm od słupka | ✓ |
| Haczyki blatu a kieszenie korpusu (R47, R50‑1) | występ Z 52,85…54,85 w kieszeni Z 52,6…55,1 → 0,25 luzu z każdej strony; poniżej kieszeni haczyk nie wchodzi w ścianę | ✓ |
| Nasada ucha wkładki (R47, R51) | nasada L: x 44…52,3 od y 48,8, x 52,3…65 od y 52,3, Z 0…3 ze ścianką tylną ramy; nie zasłania pasa przedniego ani prawego | ✓ |
| Strzałki ▼ a kołnierz pokrywki (R47, R51) | relief do Z 6,6 (70,2 globalnie) na y −50,0…−52,3; kołnierz pokrywki y −48,3…−49,8, dół 70,1 → bez nakładania (wiersz „Napis PRZÓD” zastąpiony) | ✓ |
| Uchwyty kabli (R43) | **[usunięte R50‑U8]** — podstawki opasek samoprzylepne, bez bossów | — |
| Rama dyfuzora a bossy blatu (R44) | **[usunięte R50‑U1]** — bez ramy i bossów | — |
| Garby pokrywki a wycięcia palcowe (R42) | wycięcia x −15…15 na przodzie i tyle; garby przód x 20…30, tył x −30…−20 | ✓ |
| Płytka we wkładce | 96 + 2 × 0,3 = 96,6; wycięcie 5 vs kołek 4,4: w STL kołek stoi 0,5 od ściany wycięcia po stronie narożnika (4.6.4) → luz 0,4 na stronę otwartą (trzecie oko, R52); położenie płytki ustala otwór 96,6, nie kołek | ✓ (powtarzalność ±0,3 < ±0,5) |
| Wkładka w oknie blatu | rama 104,6 < dyfuzor 160; uszy do y = 96 < wnętrze kołnierza 97,0 (R48); kołki i magnesy na litym blacie (y 86–93,5, poza kieszenią 81) | ✓ |
| Magnes–czujnik | 0,2 + 1,0 + 0,5 = 1,7 ≤ 4 | ✓ |
| Odsłonięty margines | 32 − 0,3 − 4 = 27,7 mm = 11 pełnych pikseli; przód i prawy bok bez uszu | ✓ |
| Pokrywka nad pracą | 14 − 4 + 4 = 14 mm prześwitu nad płytką | ✓ |
| Zasady 4.8: ścianki | najcieńsze: kołnierz pokrywki 1,5; ramię zatrzasku 1,5; półka nad kanałem 2,5 − 1,0 = 1,5 (R20); ściana korpusu za kieszenią zatrzasku 2,5 − 1,0 = 1,5 (R6); dno blatu pod ślepym otworem kołka 0,2 (R8; dopuszczalne lokalnie — to nie ścianka nośna, a otwór może przebić się na wylot bez szkody) | ✓ |
| Zasady 4.8: otwory | najmniejszy ø2 (dołki kodu) ≥ 1,5 | ✓ |
| Zasady 4.8: relief | 0,6 | ✓ |
| Zasady 4.8: luzy | ruchome 0,3 (płytka, pokrywka) i 0,5 (kołnierz blatu na 195 mm, R48), wciskane 0,15 (kołek ø3 w ø3,3 → 0,15/stronę), magnesy 0,1–0,2 | ✓ |
| Zasady 4.8: pustki | korpus, blat, pokrywka otwarte; kieszenie magnesów i kanały kabli otwarte od spodu | ✓ |
| Zasady 4.8: gwinty (R49, R49a) | bez wkładek; wkręty formujące gwint w PA12: otwór ø2,5 pod M3/PT3,0 w słupkach blatu (głęb. 6, dno 1,8), ø2,1 pod M2,5/PT2,5 w bossach Pi (głęb. 5); ścianki wokół otworu ≥ 2,75 (bossy ø8, słupek 8 × 6) | ✓ |
| Kanały kabli wkładki (R50‑U9) | rowek 2,5 × 1,5 na zewnętrznej dolnej krawędzi: od 52,3 do 49,8 → do otworu 48,3 zostaje 1,5; nad rowkiem 4,5 ramy; 3 żyły ø0,9: 2 obok (1,8 < 2,5) + 1 nad (1,5) | ✓ |
| Wentylacja (R50‑U19) | wylot 10 szczelin × 36 = 360 mm² + luz kołnierza blatu 0,5 × 800 = 400 mm²; wlot 2 × 30 × 4 = 240 mm²; 10–13 W w 200 × 200 × 64 → Pi < 70 °C (krok 14) | ✓ |
| Gniazda wieczornej | 6 rzędów: 9+9+12+15+15+15 + 5 × 3 = 90; najszerszy rząd 87/90; rzędy skrajne 69 i 60 ≤ 70 | ✓ |
| Gniazda porannej | 7 rzędów: 7,5×3+10+12,5+13+13 + 6 × 3 = 89 ≤ 90; najszerszy rząd 90/90; rzędy skrajne 60 i 50 ≤ 70 | ✓ |
| Kieszeń DC w korpusie (R50‑3, R50‑4) | skrzynka x −97,5…−40, y 78…100, Z 12…40: podkładka‑stadion panelu (−55…−65, 55…65) → y ≤ 68,2 (9,8 zapasu); szczeliny lewej ściany (y ±36, Z ≤ 9,5) i tylnej (x −54, Z ≤ 9,5) pod skrzynką (2,5 zapasu); kołnierz blatu od Z 49,6 (9,6 zapasu); wkręt blatu (−75, Z 55) 15 nad skrzynką; kieszeń zatrzasku tylnego (x −50, Z 52,6) nad skrzynką; okno x −93…−42 kończy się 4,5 od narożnika wewn. (−97,5, 97,5) | ✓ |
| Gniazdo DC w ścianie skrzynki (R50‑3) | ściana x −42…−40, pole y 80…97,5 × Z 14…38; otwór ø12 w (89, 30): Z 24…36 → 2 do sufitu wewn.; nakrętka ø15 (y 81,5…96,5, Z 22,5…37,5) na ścianie ✓; wtyk ø11 w świetle: Z 24,5…35,5 ⊂ 14…38, y 83,5…94,5 ⊂ 80…97,5 ✓; wtyk kątowy 26 od lica −42 → −68 vs ściana korpusu −95,5 (27,5 zapasu); wtyk prosty 40 + zagięcie 12 → −94 ✓; korpus gniazda w +X od −40: wolne do x 52 (gniazdo USB) = 92 | ✓ |
| Kieszeń zatrzasku a napis | kieszeń przednia x 45…55, Z 52,6…55,1 (od wewnątrz); napis x −55…55, Z 47…55 (relief na zewnątrz); ściana 2,5 − kieszeń 1,0 = 1,5 + relief 0,6 → bez nakładania (R6, R47(17)) | ✓ |
| Wtyk DC Bonnetu (R50‑6) | wtyk 40 od krawędzi Bonnetu: −X od x −50 → −90 vs ściana −97,5 (7,5); −Y od y −28 → −68 vs ściana −97,5 i podkładka (−60, −55) tylko dla gniazda w x −63…−57 (gniazdo ≥ 5 od krawędzi SD → x ≥ −45 ✓); +Y od 28 → 68 vs skrzynka DC y 78 (10); +X wyklucza Bonnet (porty USB Pi) | ✓ |
| Okno USB vs rowki (R50‑5) | okno 16 × 9 w (60, 24): x 52…68, Z 19,5…28,5; rowki (osie 60 ± 11,5…14, szer. 3,2) x 44,4…50,1 i 69,9…75,6, Z 22,4…25,6 → ścianka okno–rowek 52 − 50,1 = 1,9 ≥ 1,5 (dlatego rozstaw min 23, nie 20); do szczelin tylnych (x 54, Z 6,5…9,5) ≥ 10; do wkrętów blatu (±75, Z 55) ≥ 28 | ✓ |
| Odbiornik USB (R50‑6) | porty Pi x 35…37, y −21…13; odbiornik do 25 → x 62; podkładka panelu (60, −55…−65) poza y; ściana 97,5 | ✓ |

---
## 5. Lista zakupów (na 2 ramki; ceny orientacyjne, Z22)

| Element | Model / kluczowe parametry | Ilość | Cena ok. [zł] | Gdzie |
|---|---|---|---|---|
| Panel HUB75 64 × 64 P2.5 | 160 × 160, 1/32 scan, 5 V, złącze zasilania VH4 + kabel, kabel HUB75 16‑pin w zestawie | 2 | 90–130/szt. | Botland, Kamami, AliExpress (Waveshare „RGB‑Matrix‑P2.5‑64x64”) |
| Raspberry Pi 4 B 2 GB | + radiator aluminiowy 3‑częściowy | 2 | 230–280/szt. | Botland, Kamami |
| Adafruit RGB Matrix Bonnet | ADA 3211; alternatywa RGB Matrix HAT + RTC (ADA 2345) | 2 | 90–130/szt. | Botland, Kamami, Pimoroni |
| Zasilacz 5 V 4 A | wtyk DC 5,5/2,1, wtyczka EU | 2 | 35–50/szt. | Botland |
| Gniazdo DC panelowe 5,5/2,1 | z nakrętką, gwint ø12 (lub ø8 → tulejka redukcyjna druk własny, R50‑3); montaż w prawej ścianie skrzynki kieszeni, nakrętka kluczem 14 od wnętrza | 2 | 5/szt. | Botland |
| Wtyk kątowy DC 5,5/2,1 | zasilacz z wtykiem kątowym 90° albo przejściówka kątowa (po R50‑4 mieści się też prosty, ale kątowy jest wygodniejszy w szafce) | 2 | 5–10/szt. | Botland, Allegro; wtyk prosty tylko z korpusem ≤ 37 mm od lica (R52) |
| Wtyk DC 5,5/2,1 ze śrubkami | do kabla gniazdo → Bonnet | 2 | 4/szt. | Botland |
| microSD 32 GB A1 | SanDisk / Samsung EVO | 2 | 25/szt. | dowolny |
| Pleksi mleczna 2 mm 160 × 160 | PMMA opal 2 mm, cięcie na wymiar | 2 (+1) | 10–20/szt. | plexi.pl, Allegro |
| Klawiatura numeryczna 2,4 GHz | odbiornik USB nano, NIE Bluetooth‑only; np. Logitech / Natec / Genesis | 1 | 60–120 | Allegro, x‑kom |
| Gniazdo USB‑A panelowe | USB 3.0/2.0 panel‑mount, flansza 2 × M3 **z otworami poziomo w rozstawie 23…28** (R50‑5; rozstaw 22 → spiłować koniec rowka 0,5; typ „D” z otworami pionowymi wymaga wiercenia), kabel 30 cm do USB‑A męskiego, z zaślepką | 2 | 15–25/szt. | Botland, AliExpress |
| Czujniki Halla A3144 | TO‑92; alternatywnie SS451A / DRV5032 (D7) | 10 (6 + zapas) | 1–3/szt. | Botland, AliExpress |
| Rezystory 10 kΩ 1/4 W | podciąganie Halla | 10 | 1 | Botland |
| Magnesy neodymowe ø5 × 2 N35 | paczka 30 szt. (potrzeba 9 w płytkach + 4 wkładki + 4 blaty = 17) | 30 | 15 | Allegro, AliExpress |
| Wkręty do tworzyw PT 3,0 × 8 (albo M3 × 8 z ostrym gwintem) | formują gwint w PA12 w otworze ø2,5 (R49); po R50 tylko słupki blatu (4 szt. + zapas) | 10 | 5 | Botland, Allegro |
| Wkręty do tworzyw PT 2,5 × 6 (albo M2,5 × 6) | otwór ø2,1 (R49) | 15 | 8 | j.w. |
| Dystanse mosiężne M3 **żeńsko‑żeńskie 50 mm** (gwint w panelu) ALBO **45 mm** (bez gwintu — kupić po pomiarze #5a) | panel (R5, R50‑7); `panel_pcb_z` 54 jest zamrożone, długość zawsze 50 = 3 + 1 + 50 albo 45 + tulejka 5; różnice ±0,5…2 wyrównać podkładkami R50‑8 | 8 | 30 | Botland, Allegro |
| Wkręty dociskowe (bez łba) M3 × 5, imbus | sprzęgają dystans F‑F z gwintem panelu / tulejki (R50‑7); nic nie wystaje od strony diod | 10 | 6 | Allegro |
| Tulejki mosiężne F‑F M3 ø5 × 5 (tylko gdy panel bez gwintu, #5a = NIE) | klejone epoksydem do spodu PCB panelu współosiowo z otworem (R50‑7) | 8 | 10 | Allegro |
| Epoksyd 2‑składnikowy 5 min | tulejki F‑F (R50‑7) | 1 | 12 | dowolny |
| Podkładki M3 ø9 (DIN 9021 powiększone) | pod łby wkrętów panelu w rowkach dna (R50‑2, R50‑U20) | 10 | 3 | Allegro |
| Podstawki opasek samoprzylepne 20 × 20 + taśma 3M VHB 10 mm | zamiast uchwytów kabli (R50‑U8): wiązki DC i Hall, płytka proto na ścianie | 6 + 1 m | 15 | Allegro |
| Wkręty M3 × 8 łeb stożkowy (blat tył) i M3 × 10 łeb walcowy (panel, od spodu przez dno 3 + podkładka 1 w dystans) | stal czarna; wkręty ramy i uchwytów zbędne (R50‑U1, R50‑U8) | 4 + 10 | 12 | Allegro |
| Śruby M2,5 × 6 (Pi) | | 10 | 6 | Allegro |
| Listwa kątowa goldpin 1 × 10 | do wyprowadzenia GPIO z Bonnetu (Z12) | 2 | 2 | Botland |
| Płytka prototypowa 30 × 20 (pads) | Halla + rezystory | 2 | 4 | Botland |
| Złącza JST‑XH 2,54: 5‑pin, 3‑pin + przewody Dupont F‑F 20 cm | | komplet | 20 | Botland |
| Przewód silikonowy AWG 28, 3 kolory | do czujników Halla (po 50 cm × 3 na czujnik) | 3 × 5 m | 20 | Botland |
| Przewód 2 × 1 mm² 30 cm | DC gniazdo → Bonnet | 1 m | 5 | |
| Stopki gumowe ø10 × 4 samoprzylepne | | 12 | 8 | Allegro |
| Opaski kablowe 2,5 × 100, rzep 20 mm | | komplet | 10 | |
| Klej CA (cyjanoakrylowy) żelowy | magnesy, czujniki Halla | 1 | 10 | |
| Przedłużacz USB 20 cm (opcja) | gdyby odbiornik klawiatury słabo odbierał w obudowie | 1 | 8 | |

Razem elektronika i drobne: ok. 1 200–1 680 zł.

---

## 6. Narzędzia

Lutownica (tylko do kabli; wkładek gwintowanych nie ma, R49); cyna 0,8; trzecia ręka; multimetr; wkrętaki PH1, PH0, torx T10; klucz płaski 14 (nakrętka DC); szczypce boczne; pęseta; papier 400; wiertła ø3,4 i ø5,5 (ewentualne poprawki otworów); pilnik igłowy; klej CA żelowy; marker; kompas lub magnes wzorcowy (bieguny); suwmiarka; laptop z czytnikiem SD; stacja do flashowania (Raspberry Pi Imager); mała wiertarka/dremel tylko do poprawek.

---

## 7. Struktura wewnętrzna obudowy (wariant wysoki)

Wszystkie pozycje globalne XY, Z od zewnętrznego dna.

| Element | Położenie | Wymiar | Gwint (R49: wkręt formujący w PA12) |
|---|---|---|---|
| Podkładki panelu (4) | stadion wzdłuż przekątnej od (±55, ±55) do (±65, ±65) (R50‑2); po pomiarze słupek staje w zmierzonym punkcie rowka | stadion 9 szer. × 1; w dnie rowek przelotowy 3,4 szer. o tej samej osi, bez pogłębienia (R50‑U20) | — (R5) |
| Dystanse panelu (4) | na podkładkach | M3 F‑F 50 mm, wkręt M3 × 10 + podkładka ø9 od spodu; góra: wkręt dociskowy M3 × 5 w gwint panelu (bez gwintu: tulejka F‑F ø5 × 5 klejona + dystans 45) (R50‑7) | — |
| Bossy Pi (4) | (−46,5, ±24,5), (11,5, ±24,5) (R50‑6) | ø8 × 5, otwór ø2,1 × 5 | M2,5 formowany (R49) |
| Bossy uchwytów kabli (2) | **[usunięte R50‑U8]** — podstawki opasek samoprzylepne 20 × 20 na dnie | — | — |
| Słupki blatu (2, w kołnierzu blatu) | x ±71…79, y 89,2…95,2, oś otworu Z 55 (R50‑1) | 8 × 6 × 10, otwór poziomy ø2,5 × 6 od lica 97,0 (R49a) | M3 formowany (R7, R47, R48, R49) |
| Bossy ramy dyfuzora (4, pod blatem) | **[usunięte R50‑U1]** | — | — |
| Kieszenie zatrzasków blatu (4) | lewa/prawa y = 0, przednia x = +50, tylna x = −50; Z 52,6–55,1 (R50‑1) | 10 × 2,5 × 1,0 | — (R6) |

Prowadzenie kabli:
1. Zasilanie: gniazdo DC w prawej ścianie skrzynki kieszeni (x −40, y 89, Z 30; nakrętka od wnętrza, korpus gniazda w +X) → przewód 2 × 1 mm² 25 cm → wtyk DC → gniazdo Bonnetu; z zewnątrz wtyk kątowy zasilacza wchodzi w kieszeń w −X, kabel wychodzi przez okno. Trasa po dnie wzdłuż tylnej i lewej ściany, podstawka opaski samoprzylepna.
2. HUB75: Bonnet → kabel taśmowy 16‑pin 150 mm → HUB75 IN panelu (złożony płasko pod panelem, nad Bonnetem; luz Z 34–42).
3. Zasilanie panelu: terminal śrubowy Bonnetu → kabel VH4 panelu (w zestawie) → panel.
4. Hall: 3 × 3 żyły AWG 28 od wkładki przez szczeliny blatu (±66, 90) → wzdłuż tylnej ściany → płytka proto na taśmie VHB na lewej ścianie (Z 40) → JST 5‑pin → Dupont do listwy na Bonnecie.
5. USB serwisowe: gniazdo panelowe (60, tył, Z 24) → kabel 30 cm → USB‑A Pi (górny lewy port). Odbiornik klawiatury: dolny lewy port USB Pi; jeśli zasięg < 3 m przez obudowę → przedłużacz 20 cm przyklejony rzepem do lewej ściany na Z 40.
Długości kabli: wszystkie ≤ 300 mm; zapas pętli 50 mm przy blacie, żeby blat dało się zdjąć i odłożyć obok bez odpinania Halla (złącze JST na płytce proto pozwala odpiąć).

Wentylacja: patrz D14. Powietrze wchodzi szczelinami w dnie pod Pi (konwekcja od radiatora Pi), wychodzi szczelinami w ścianach Z 8 (4 tył + 3 na bok, bez daszków — R50‑U4, R50‑U19) i przez szczelinę między panelem a ścianami do przestrzeni pod blatem — blat nie jest szczelny na kołnierzu (luz 0,5, R48), co daje wylot górny.

---

## 8. Elektronika i montaż

### 8.1 Piny zajęte przez RGB Matrix Bonnet (mapowanie `adafruit-hat`, biblioteka rpi‑rgb‑led‑matrix)
GPIO 4 (OE), 17 (CLK), 21 (LAT), 22 (A), 26 (B), 27 (C), 20 (D), 24 (E — na Bonnecie zworka lutownicza „E” → „8”, wymagana dla panelu 64 × 64), 5 (R1), 13 (G1), 6 (B1), 12 (R2), 16 (G2), 23 (B2). Zarezerwowany dodatkowo GPIO 18 (zworka jakości PWM „GPIO4–GPIO18”, mapowanie `adafruit-hat-pwm`; zalecana, bo usuwa migotanie). HAT + RTC używa ponadto I2C (GPIO 2, 3) dla zegara DS1307.

Wolne: GPIO 2, 3 (I2C1), 7, 8, 9, 10, 11 (SPI0), 14, 15 (UART), 19, 25. Używane przez ramkę: tylko 19, 25, 8 (Hall). Reszta wolna (Z28: brak przycisku i czujnika gestu).

### 8.2 Tabela połączeń
| Element | Sygnał | Pin Pi (BCM / fizyczny) | Przewód / złącze |
|---|---|---|---|
| Zasilacz 5 V 4 A | +5 V, GND | gniazdo DC Bonnetu (Bonnet → pin 2/4 5 V, pin 6 GND do Pi) | DC 5,5/2,1, 2 × 1 mm² |
| Panel HUB75 | 5 V, GND | terminal śrubowy Bonnetu | kabel VH4 panelu |
| Panel HUB75 | dane | złącze IDC 16 Bonnetu | taśma 16‑pin 150 mm |
| Hall A (bit 0) | OUT | GPIO 19 / pin 35, pull‑up 10 kΩ do 3,3 V (pin 17) | AWG 28 żółty |
| Hall B (bit 1) | OUT | GPIO 25 / pin 22, pull‑up 10 kΩ | AWG 28 zielony |
| Hall C (bit 2) | OUT | GPIO 8 / pin 24, pull‑up 10 kΩ (SPI wyłączony) | AWG 28 niebieski |
| Hall A, B, C | VCC | 5 V / pin 4 | AWG 28 czerwony |
| Hall A, B, C | GND | GND / pin 39 | AWG 28 czarny |
| Odbiornik klawiatury (tylko P) | USB | port USB‑A 2.0 Pi (dolny lewy) | — |
| USB serwisowe | USB | port USB‑A 3.0 Pi (górny) | kabel panelowy 30 cm |
| (rezerwa) | — | GPIO 2, 3, 7, 9, 10, 11, 14, 15 | — |

Konflikty: brak. Uwaga: wyjście A3144 przy zasilaniu 5 V jest otwartym kolektorem — NIGDY nie podciągać do 5 V; rezystory 10 kΩ wyłącznie do pinu 1 (3,3 V). W `config.txt` wyłączyć SPI (`dtparam=spi=off`), wyłączyć dźwięk (`dtparam=audio=off` — wymagane przez rpi‑rgb‑led‑matrix), `isolcpus=3` w `cmdline.txt`.

### 8.3 Płytka prototypowa Halla (30 × 20)
Złącze JST‑XH 5 (5 V, GND, A, B, C) od strony Pi; 3 × JST‑XH 3 (VCC, GND, OUT) od strony czujników; 3 × 10 kΩ między OUT a dodatkową żyłą 3,3 V (6. żyła osobnym Dupontem z pinu 17) — żeby nie mieszać 5 V i 3,3 V, wylutować pola i opisać markerem. Płytki proto obu ramek identyczne (Z28).

---

## 9. Kolejność składania i testy

| Krok | Czynność | Test / kryterium zaliczenia |
|---|---|---|
| 1 | Zamówienie BEZ pomiarów elektroniki (R50): korpus W/P, blat × 2, wkładka × 3, płytki n1–n6 po teście #12 (karton w skanerze); pomiary sekcji 10 służą potem tylko doborowi sprzętu (dystanse, tulejka) i przebiegowi ALL. | Arkusz zamówienia ma objętości wszystkich STL drukarni; usługodawca potwierdził PA12, kolory i gabaryt 200 × 200 × 60. |
| 2 | System na stole: Raspberry Pi Imager → Raspberry Pi OS Lite 64‑bit, SSH + Wi‑Fi firmowe; `apt install` zależności; kompilacja rpi‑rgb‑led‑matrix z powiązaniem Python; `config.txt` jak w 8.2; zworki Bonnetu (E, PWM). | `ssh` działa; `demo -D0 --led-rows=64 --led-cols=64 --led-gpio-mapping=adafruit-hat-pwm` daje stabilny obraz bez migotania. |
| 3 | Panel + Bonnet + zasilacz: wzór testowy, cyfry na marginesie, pomiar poboru prądu multimetrem w szereg. | Biel pełna < 3,5 A; typowy obraz ramki (zielone pola + cyfry) < 1,5 A; Pi nie restartuje się. |
| 4 | Klawiatura (ramka P): odbiornik w Pi, skrypt Python `evdev` czyta klawisze. Ramka W: test zdarzenia „Skanuj” wysyłanego z laptopa (spacja) przez Wi‑Fi do ramki. | Każdy klawisz daje właściwe zdarzenie; spacja na laptopie zmienia stan ramki W w < 1 s. |
| 5 | Elektronika Halla na stole: płytka proto, 3 czujniki na kablach 50 cm, test magnesem ø5 × 2 (biegun S do czujnika). | Każde wejście przechodzi 1 → 0 przy magnesie ≤ 4 mm, wraca do 1 po odsunięciu; przy odwróconym biegunie brak reakcji (to potwierdza, którą stroną kleić). |
| 6 | Części z druku: oględziny, wypłukanie proszku, próba pasowania na sucho: płytka we wkładce, wkładka na blacie, pokrywka na płytce, blat na korpusie. | Płytka wchodzi i wychodzi bez siły, luz wyczuwalny < 0,5 mm; pokrywka trzyma po odwróceniu; blat zatrzaskuje się i daje się zdjąć ręką. |
| 7 | Gwinty (R49, bez wkładek): każdy otwór ø2,5/ø2,1 przegwintować raz „na sucho” wkrętem PT (albo M3/M2,5) wkręcanym wkrętakiem, wolno, bez dokręcania na siłę: korpus (4 × Pi), blat (2 × słupki). | Wkręt wchodzi bez oporu i trzyma; gwint nie wyrobiony po 3 cyklach. |
| 8 | Montaż Pi + Bonnet na bossach (NAJPIERW wpiąć wtyk DC kabla wewnętrznego w gniazdo Bonnetu — przy kierunku −X jest tylko 7,5 mm do ściany, R52), listwa kątowa dolutowana do pinów 1, 3, 4, 5, 9, 17, 19, 22, 24, 26, 35, 39 Bonnetu. Panel (R50‑7): z gwintem — wkręty dociskowe M3 × 5 wkręcone 2,5 w otwory panelu, dystanse F‑F 50 nakręcone; bez gwintu — tulejki F‑F ø5 × 5 doklejone epoksydem do spodu PCB (centrowanie śrubą M3 × 10 przez otwór, wyjąć po utwardzeniu), dystanse F‑F 45 + wkręty dociskowe. Panel postawiony na podkładkach‑stadionach tak, by dystanse trafiły w rowki, 4 wkręty M3 × 10 z podkładkami ø9 od spodu. Przy wzorze otworów poza rowkami: wywiercić ø4 w dnie w zmierzonym miejscu, podkładka R50‑8 pod dystans. | Stos Pi nie dotyka spodu panelu (szczelina ≥ 2 mm, sprawdzić szczelinomierzem/kartą); panel równoległy do dna (różnica < 0,5 mm na rogach); nic nie wystaje od strony diod. |
| 9 | Dyfuzor w kieszeni blatu (rogi pleksi bez fazowania, R50‑U15), próba zamknięcia blatu na korpusie z panelem. | Blat zamyka się do końca; okno równo nad panelem (przesunięcie < 1 mm); PCB panelu nie dotyka spodu blatu. |
| 10 | Wkładka: czujniki Halla wklejone w kieszenie półek (lico do góry, kropla CA na bok obudowy, nie na lico), przewody w rowkach, wyprowadzenie przez uszy i szczeliny blatu do płytki proto. Magnesy w uszach i blacie (najpierw sprawdzić przyciąganie, potem CA). | Wkładka siada na kołkach i trzyma magnesami (nie przesuwa się przy pchnięciu palcem); płytka testowa wchodzi na kołek orientacyjny tylko w jednej orientacji. |
| 11 | Magnesy w płytkach wg kodów: nr 1 (A), 2 (B), 3 (A+B), 4 (C), 5 (A+C), 6 (B+C); biegun S w dół; CA. | Skrypt odczytu pokazuje 1…6 dla każdej płytki, 0 bez płytki, odczyt stabilny 60 s, zmiana < 100 ms po położeniu. |
| 12 | Okablowanie końcowe (gniazdo USB panelowe wkręcić PRZED montażem panelu — od wnętrza ma 14,3 mm do dystansu (60, 60), R52): gniazdo DC (przez okno kieszeni w otwór prawej ściany skrzynki; przy gwincie ø8 najpierw tulejka redukcyjna; nakrętka kluczem 14 od góry), USB panelowe (rowki; przy flanszy z otworami pionowymi wywiercić 2 × ø3,2), podstawki opasek samoprzylepne (PA12 przemyć IPA), płytka proto na VHB, opaski, opisy kabli; odbiornik klawiatury w porcie USB (P), stopki samoprzylepne 12 od krawędzi. | Żaden kabel nie dotyka diod ani radiatora; blat daje się zdjąć i odłożyć obok bez rozpinania; obudowa stoi stabilnie; wtyk DC nie wystaje poza obrys. |
| 13 | Kalibracja gniazdo → diody: program wyświetla kolejno blok 3 × 3 piksele pod obliczonym środkiem każdego gniazda, operator potwierdza lub przesuwa strzałkami; zapis `leds` do JSON. | Każde gniazdo z pracą świeci widocznie od góry przez otwór ø3, sąsiednie gniazda ciemne; JSON ma wpis dla każdego id. |
| 14 | Test 8 h: pełny wzór pracy ramki + cyfry; log temperatury Pi co minutę; po 8 h wyrwanie zasilania i ponowne włączenie. | Pi < 70 °C przez cały czas; zasilacz letni; po włączeniu ramka wstaje sama i pokazuje ekran gotowości w < 60 s; karta bez błędów (`dmesg`). |
| 15 | Druga ramka z poprawkami; lista zmian wpisana do planu v2. | Obie ramki przechodzą kroki 11–14. |

---
## 10. Formularz pomiarów (przed zamówieniem)

Czym: suwmiarka (S), linijka stalowa (L), karta katalogowa / sklep (K), test (T).

| # | Co zmierzyć | Czym | Parametr | Domyślnie | Wynik |
|---|---|---|---|---|---|
| 1 | Panel: bok PCB | S | panel_size | 160 | ______ |
| 2 | Panel: grubość PCB | S | panel_pcb_t | 1,6 | ______ |
| 3 | Panel: wysokość diod/maski nad PCB — kryterium: 1…3 → luz dioda–dyfuzor 5…3 w spec, korpus bez zmian (R50‑1) | S | panel_led_h | 2 | ______ |
| 4 | Panel: najniższy element od spodu (złącza, kondensatory) BEZ kabli i Z WPIĘTYMI kablami — kryterium: (#4 z kablami − 12) + (#9 z taśmą − 26) ≤ 5 → korpus bez zmian; inaczej obrócić panel tak, by złącza leżały nad kolumną słupków, awaryjnie bossy Pi 5 → 3 | S | panel_bottom_parts_h | 12 | ______ / ______ |
| 5 | Panel: rozstaw otworów M3 w X i Y (środek–środek) — kryterium: kwadrat 110…130 i offset ≤ 0,5 → słupki w rowkach bez wiercenia (R50‑2); inaczej wiercenie ø4 w dnie + podkładka R50‑8 | S/L | panel_hole_pitch_x / _y | 120 / 120 | ______ / ______ |
| 5a | Panel: czy otwory montażowe mają gwint M3 (wkręcić śrubę M3 palcami) — TAK = dystanse F‑F 50 + wkręty dociskowe; NIE = tulejki F‑F ø5 × 5 klejone + dystanse F‑F 45 (R50‑7); korpus bez zmian | T | (R5/R50‑7) | TAK | ______ |
| 6 | Panel: przesunięcie środka wzoru otworów względem środka PCB (kryterium jak #5) | L | panel_hole_offset_x / _y | 0 / 0 | ______ / ______ |
| 7 | Panel: prostokąt obejmujący złącza HUB75 IN/OUT i zasilania od spodu (środek, szer., wys.) | L | panel_conn_zone_* | 0, 0, 120, 60 | ______ |
| 8 | Panel: która krawędź to góra (strzałka na PCB) — zapisać, by ustawić HUB75 IN od strony Bonnetu | — | (orientacja w skrypcie) | IN przy x < 0 | ______ |
| 9 | Pi + Bonnet: spód PCB Pi → najwyższy element Bonnetu BEZ taśmy i Z WPIĘTĄ taśmą HUB75 (kryterium łączne w #4) | S | pi_stack_h | 26 | ______ / ______ |
| 10 | Bonnet: pozycja gniazda DC (która krawędź Pi, odległość od narożnika SD) i kierunek wtyku — kryterium: każdy z −X, −Y, +Y mieści wtyk 40 (R50‑6); tylko do `.blend` | L | bonnet_dc_pos_x / _y / bonnet_dc_dir | −50 / 22 / −X | ______ |
| 11 | Bonnet: pozycja złącza HUB75 (krawędź, odległość) | L | (notatka) | — | ______ |
| 12 | Skaner Aidite: czy płytka 96 × 96 z pracami skanuje się w całości (test na kartonowej makiecie 96 × 96 z 4 rogami zaznaczonymi) | T | plate_size | 96 | ______ |
| 13 | Klawiatura: model (tylko do notatki, bez podstawki) | K | — | — | ______ |
| 14 | Odbiornik USB: dł. × szer. × wys. | S | receiver_* | 19 / 15 / 6 | ______ |
| 15 | (skreślone, Z28) | — | — | — | — |
| 16 | Gniazdo DC panelowe: średnica gwintu — kryterium: ≤ 12 → bez tulejki (12) albo z tulejką redukcyjną (8); > 12 → rozwiercić ścianę skrzynki; długość korpusu za nakrętką tylko do `.blend` (wolne 50); wtyk zasilacza: kątowy (wysięg ≤ 36 od lica) albo prosty (korpus ≤ 37 + zagięcie 12; realne lico gniazda z kołnierzem tulejki i flanszą leży na x −45 — R52) — oba mieszczą się po R50‑3/R50‑4 | S | dc_hole_d, dc_socket_body_l | 12, 18 | ______ |
| 17 | Gniazdo USB‑A panelowe: okno (≤ 16 × 9 → bez zmian), rozstaw otworów flanszy — kryterium: 23…28 poziomo → rowki (R50‑5); 22 → spiłować 0,5; pionowo (typ D, 24) → wiercić 2 × ø3,2 | S | usb_cut_w / usb_cut_h / usb_hole_pitch | 16 / 9 / 22 | ______ |
| 18 | (skreślone, Z28) | — | — | — | — |
| 19 | Usługodawca: materiały i kolory PA12, max gabaryt, cena/cm³, czy robi CNC PMMA ze STL/STEP | K | (arkusz zamówienia) | — | ______ |
| 20 | Wkręty do tworzyw: średnica rdzenia i gwintu (PT 3,0: otwór 2,5; PT 2,5: otwór 2,1) — potwierdzić na kupionych wkrętach | S | insert_hole_m3 / _m25 | 2,5 / 2,1 | ______ |

Po R50 korpus jest zamówiony PRZED pomiarami, więc wpisanie pomiarów do `parametry.json` (status `ZMIERZONE`) **nie może zmienić `panel_pcb_z`, `korpus_h`, `blat_top_z`** — te zostają 54 / 59,6 / 63,6 (zamrożone geometrią druku). Pomiary #3, #4, #9 wpisuje się tylko do brył zastępczych (`.blend`, K‑44b sprawdza, że stos + złącza mieszczą się w zapasie); `pi_clearance_top` jest wtedy wielkością wynikową (= 54 − 3 − 5 − pi_stack_h − panel_bottom_parts_h ≥ 3 wymagane). Dobór sprzętu: dystans 50 F‑F (gwint) albo 45 + tulejka (bez gwintu); różnice ±0,5…2 wyrównać podkładkami R50‑8. Każda zmiana parametru = pełne ponowne uruchomienie skryptu i pełna weryfikacja (R28).

---

## 11. Wstępny koszt części zamawianych

Z gabarytów (objętość materiału, nie bryły); stawka orientacyjna MJF/SLS PA12 w Polsce 0,9–1,6 zł/cm³ przy tej skali zamówienia + opłata za gabaryt dużych części; barwienie grafit +15–25 %, wygładzanie parowe +25–40 %. Dokładnie policzy wykonawca z objętości STL (arkusz_zamowienia).

| Część | Obj. ok. [cm³] | Szt. | Obj. razem | Najtańszy (PA12 naturalny) [zł] | Pokazowy (barwienie + wygładzanie) [zł] |
|---|---|---|---|---|---|
| Płytka wieczorna | 62 | 3 | 186 | 170–300 | 170–300 (biała, bez barwienia; bez wygładzania wierzchu) |
| Płytka poranna | 61 | 3 | 183 | 165–290 | 165–290 |
| Pokrywka | 30 | 4 | 120 | druk własny PETG (ok. 15 zł filamentu) | — |
| Korpus (59,6 wys., bez daszków/żeber/bossów uchwytów, R50) | 225 | 2 | 450 | 405–720 | 620–1 100 |
| Blat (bez bossów ramy) | 83 | 2 | 166 | 150–265 | 235–410 |
| Rama dyfuzora | — | — | — | [usunięte R50‑U1] | — |
| Wkładka gniazda | 16 | 3 | 48 | 45–80 | 45–80 |
| Uchwyt kabli | — | — | — | [usunięte R50‑U8] | — |
| Tulejka DC, podkładki panelu | 1 + 3 | 2 + 24 | ~5 | druk własny (żywica) | — |
| **Razem drukarnia** | | | ~1 033 | **935–1 655 zł** | **1 235–2 180 zł** |

Największy koszt to korpus (ok. 40 %). Jeśli wycena przekroczy budżet: zmniejszyć `wall_t` do 2,0 i `floor_t` do 2,5 (−15 % korpusu) albo zamówić korpus w SLS zamiast MJF (często taniej dla dużych brył). Objętości korpusu i blatu są szacunkiem po R50 (+10 cm³ za 5 mm wysokości, −3 za daszki/żebra/bossy; blat −2 za bossy ramy) — obowiązują wartości z `arkusz_zamowienia`.

---

## 12. Przekazanie do wykonawcy (dawna „sesja 2”)

Wykonawca pracuje według `prompt_wykonawca.md`, recenzent według `prompt_recenzent.md`, właściciel według `00_PRZEPLYW_I_BRAMKI.md`. Ta sekcja definiuje wyłącznie listę plików wynikowych i sprawdzenia; wszystko inne jest w tamtych plikach.

### 12.1 Pliki wynikowe (R2, R16) — folder `wyniki_v2/`

| # | Plik | Treść | Etap |
|---|---|---|---|
| 1 | `ramka_generator.py` (w folderze głównym `Ramki/`, nie w `wyniki_v2/`) | jeden skrypt bpy: wczytuje `parametry.json` i `wyniki_v2/json/uklad_gniazd_*.json`, czyści scenę, buduje wszystkie części, eksportuje, liczy objętości, pisze arkusze, renderuje, uruchamia własne sprawdzenia; uruchomienie: `blender -b -P ramka_generator.py -- --etap A|B|C|ALL` | A |
| 2 | `wyniki_v2/json/uklad_gniazd_wieczorna.json`, `wyniki_v2/json/uklad_gniazd_poranna.json` | układ gniazd (struktura 4.1); generowane z D6 przy pierwszym uruchomieniu, potem czytane | A |
| 3 | `wyniki_v2/stl/ramka_plytka_wieczorna_v2.stl`, `…_poranna_v2.stl` (bazowe) oraz `…_wieczorna_n1_v2.stl` … `_n3_v2.stl`, `…_poranna_n4_v2.stl` … `_n6_v2.stl` | płytki | A |
| 4 | `wyniki_v2/stl/ramka_pokrywka_v2.stl` | pokrywka (druk własny PETG; bez reliefu i otworów, R50‑U14/U17) | A |
| 5 | `wyniki_v2/stl/ramka_wkladka_v2.stl` | wkładka | B |
| 6 | ~~`ramka_rama_dyfuzora_v2.stl`~~ | **[usunięte R50‑U1]** — nie powstaje | — |
| 7 | `wyniki_v2/stl/ramka_blat_v2.stl` | blat (bez bossów ramy) | B |
| 8 | `wyniki_v2/stl/ramka_korpus_W_v2.stl`, `ramka_korpus_P_v2.stl` | korpus z napisem W / P (R50‑1…6, R50‑U4/U5/U6/U8/U16/U19/U20) | B |
| 9 | `wyniki_v2/stl/ramka_tulejka_dc_v2.stl`, `ramka_podkladka_panelu_05_v2.stl`, `ramka_podkladka_panelu_1_v2.stl`, `ramka_podkladka_panelu_2_v2.stl` | małe części druku własnego (R50‑3, R50‑8); ~~`ramka_uchwyt_kabli_v2.stl`~~ **[usunięte R50‑U8]**; głowica i zaślepka usunięte (Z28) | C |
| 10 | `wyniki_v2/ramka_v2.blend` | wszystkie części jako nazwane obiekty w kolekcjach `plytki`, `obudowa`, `akcesoria`, `elementy_kupowane` (bryły zastępcze: panel, Pi+Bonnet, wtyk DC Bonnetu 40 w `bonnet_dc_dir`, dyfuzor, dystanse 50 w (±60, ±60) z `panel_hole_*`, gniazda DC (walec osią X od x −40) / USB, odbiornik USB, stopki, podkładki M3), w pozycji złożonej (układ D3) | C |
| 11 | `wyniki_v2/render/render_rozstrzelony.png`, `render_zlozony.png`, `render_plytki.png` | rozstrzelony z podpisami (izometria, rozsunięcie wzdłuż Z w kolejności montażu), złożony 3/4 od przodu z płytką wieczorną, obie płytki z góry (R15); Cycles CPU, ≥ 1600 × 1200 px | C |
| 12 | `wyniki_v2/arkusze/arkusz_zamowienia.csv`, `arkusz_zamowienia.md` | kolumny: plik STL; część; ilość; technologia; materiał (per część z `materials`); kolor; wykończenie; objętość cm³ (z siatki, 2 miejsca); gabaryt X × Y × Z mm (z siatki); koszt wariant najtańszy; koszt wariant pokazowy; uwagi (STEP/FreeCAD dla CNC). Koszt liczony tylko dla pozycji „PA12 drukarnia”; pozycje druku własnego (pokrywka, tulejka, podkładki) z objętością, bez kosztu, w osobnym bloku. Pod tabelą stawki z `parametry.json` i sumy. Objętości bazowych płytek NIE wchodzą do zamówienia. 15 wierszy (10 drukarnia + 5 własne) | C |
| 13 | `wyniki_v2/arkusze/arkusz_wymiarow.md` | wymiary główne każdej części z siatki, kluczowe pasowania z luzem nominalnym (tabela 4.11), pełny zrzut `parametry.json`, z którym zbudowano tę wersję | C |
| 14 | `wyniki_v2/arkusze/kody_plytek.md` | numer → typ → kieszenie z magnesem → dołki; instrukcja klejenia (biegun S w dół, sprawdzenie magnesem wzorcowym) | A |
| 15 | `wyniki_v2/raport/raport_wykonawcy_<etap>_iter<n>.md` | według `szablon_raport_wykonawcy.md`: wyniki sprawdzeń K‑xx z `protokol_weryfikacji_v2.md`, rejestr odstępstw, lista plików z sumami SHA‑256 | A, B, C |
| 16 | `wyniki_v2/README.md` | jak uruchomić (polecenia zaczynające się od `cd`), jak zmienić parametr (R14, R28), lista plików, rejestr odstępstw (skopiowany z raportów) | C |

Nie powstaje: `legenda_klawiatury.svg`, `ramka_podstawka_*.stl` (Z26), `ramka_glowica_*.stl`, `ramka_zaslepka_*.stl` (Z28), `ramka_rama_dyfuzora_v2.stl` (R50‑U1), `ramka_uchwyt_kabli_v2.stl` (R50‑U8).

### 12.2 Sprawdzenia
Pełna lista sprawdzeń z identyfikatorami K‑01…K‑60, metodą, tolerancją i wagą: `protokol_weryfikacji_v2.md`. Wykonawca wykonuje wszystkie sprawdzenia własnym kodem w `ramka_generator.py` (etap `--etap SPRAWDZ`) i raportuje je w raporcie; recenzent wykonuje te same sprawdzenia własnym, niezależnie napisanym skryptem na plikach z `wyniki_v2/`, nie czytając kodu wykonawcy przed pomiarem.

### 12.3 Kwestie rozstrzygnięte z góry (dawniej „do rozstrzygnięcia przez sesję 2”)
Wszystkie dawne kwestie otwarte są rozstrzygnięte w sekcji 13: font R22, żebra R23, daszki R24, promienie R26, kolory R27, kolejność id R13, garby pokrywki R21, nazwy kolekcji R16. Wykonawca nie ma kwestii do rozstrzygnięcia; każde odstępstwo zgłasza w rejestrze odstępstw raportu i NIE wdraża go bez zatwierdzenia na bramce, chyba że jest to poprawka błędu wykrytego sprawdzeniem K‑xx — wtedy wdraża i opisuje.

---

## 13. Rejestr rozstrzygnięć (R1…R51, R50‑1…R50‑8, R50‑U1…R50‑U20, A‑1…A‑9)

Oznaczenia: **[FAKT]** = wynika z rachunku lub spec, nie wymaga decyzji; **[ZAŁOŻENIE]** = wybór projektanta, do zatwierdzenia przez właściciela na bramce G0 (można zmienić jedną liczbą w `parametry.json` lub jednym zdaniem tutaj).

| Id | Problem (gdzie) | Rozstrzygnięcie | Typ |
|---|---|---|---|
| R1 | Trzy pliki wejściowe z różnymi regułami pierwszeństwa (sesja2_pliki.md 0.1.2 vs plan). | Kolejność: (1) `plan_ramki_v2.md`, (2) `parametry.json` dla liczb (musi być zgodny z planem; niezgodność = błąd do naprawy w JSON), (3) `protokol_weryfikacji_v2.md`, (4) `sesja2_pliki.md` tylko jako specyfikacja tła (sekcje 1–9), jego sekcja 0 NIE obowiązuje, (5) `spec_3d_ramka.md` nieautorytatywny (służy tylko do podglądu 3D). `plan_ramki_v1.md` nie jest czytany. | [FAKT] |
| R2 | Dwie różne listy plików wynikowych (plan 12.1 vs sesja2 0.2). | Jedna lista w 12.1 (nazwy z sesja2_pliki.md, bo są bardziej opisowe, + 3 rendery + warianty numerowane płytek). | [ZAŁOŻENIE] |
| R3 | Dołki kodu (−37, −45/−42/−39) kolidowały z gniazdem ø9 w (−30, −40,5): ścianka 1,66 mm. | Dołki w kolumnie x = −45,0, y = −36/−33/−30; rachunek w 4.11. Program skanera czyta pozycje z JSON `code_dimples`. | [FAKT] |
| R4 | Plan mówił raz o pliku bazowym z numerem, raz o wariantach. | Bazowy = 3 dołki, bez cyfry, nie do zamówienia; n1…n6 do zamówienia po 1 szt. | [ZAŁOŻENIE] |
| R5 | Mocowanie panelu było niewykonalne: wkręt M3 × 8 od spodu nie sięga przez dno 3 + boss 11 do dystansu. | Podkładka ø9 × 1 + dystans M‑F 45 wkręcony w gwint panelu + wkręt M3 × 8 od spodu w gwint dystansu. Wymaga gwintowanych otworów w panelu (pomiar #5a). | [ZAŁOŻENIE] |
| R6 | Kieszeń zatrzasku 1,2 w ścianie 2,5 zostawiała 1,3 < 1,5 (4.8); kieszeń przednia na x = 0 wypadała pod napisem, tylna nad kieszenią DC. | Głębokość 1,0, występ 1,0; przednia x = +50, tylna x = −50, boczne y = 0. | [FAKT] |
| R7 | Słupki blatu (±60) stały 1 mm od szczelin kabli (±66) i pod otworami kołków (±58). | Słupki i wkręty tylne na x = ±75. | [FAKT] |
| R8 | Otwory kołków wkładki w blacie „przelotowe” → pył do środka. | Ślepe 3,8 mm. | [ZAŁOŻENIE] |
| R9 | Bossy uchwytów (±40, 70) nachodziły na podkładkę panelu (60, 60) i korpus gniazda USB. | Przeniesione; ostateczne położenie w R43. | [FAKT] |
| R10 | Gniazdo USB (50) kolidowało z prawym uchwytem. | x = 60. | [FAKT] |
| R11 | Domyślne `bonnet_dc_pos` (−92, 0) z wtykiem 15 mm w −X przebijało lewą ścianę. | Domyślnie krawędź przednia (−60, −28), kierunek −Y; nowy parametr `bonnet_dc_dir`. Po pomiarze #10 wpisać prawdziwe. | [ZAŁOŻENIE] |
| R12 | Trasa kabli Halla z ucha do szczeliny blatu. | Kanał w uchu do krawędzi x = ±65, 1 mm po blacie do szczeliny (±64…68). Bez zmian. | [FAKT] |
| R13 | Numeracja id gniazd: plan „od przodu, od lewej” vs sesja2 „od narożnika z wycięciem”. | Rzędami od przodu, w rzędzie od prawej (od narożnika D). Pełna struktura JSON w 4.1. | [ZAŁOŻENIE] |
| R14 | Parametry „na górze skryptu” (sesja2) vs podmiana po pomiarze. | Jedyne źródło wartości: `parametry.json`. Skrypt wczytuje, waliduje (nieznany/brakujący klucz = błąd), nie ma własnych liczb. Pomiar = edycja JSON + pełny przebieg. | [FAKT] |
| R15 | Rendery: 1 (sesja2) vs 2 (plan). | 3: rozstrzelony, złożony, płytki. | [ZAŁOŻENIE] |
| R16 | Folder wyników `pliki_v1/` (sesja2). | `wyniki_v2/` z podfolderami `stl/`, `json/`, `render/`, `arkusze/`, `raport/`; kolekcje w .blend: `plytki`, `obudowa`, `akcesoria`, `elementy_kupowane`. | [ZAŁOŻENIE] |
| R17 | Sufiks `_v1` w nazwach STL (spec 4.8) przy planie v2. | `_v2`. | [ZAŁOŻENIE] |
| R18 | Napis na przedniej ściance vs kieszeń zatrzasku. | Po R6 brak kolizji; napis zostaje Z 46. | [FAKT] |
| R19 | Haczyki blatu — położenia. | Jak kieszenie (R6). | [FAKT] |
| R20 | Półka wkładki nad kanałem 1,3 < 1,5. | Kanał 2,5 × 1,0. | [FAKT] |
| R21 | Garby pokrywki: 4 czy 2. | 4 (spec), występ 0,7, rowek 0,8. | [FAKT] |
| R22 | Font napisów. | Blender 5.2.3 ma w `datafiles/fonts` tylko `Inter.woff2` i `DejaVuSansMono.woff2` (bez DejaVu Sans Bold). Font: **Inter** (`font_name`), pogrubienie przez `TextCurve.offset` (`font_offset` 0,2, dobrane tak, by trzon litery miał ≥ 1,0 mm); wysokość = wysokość wersalików po skalowaniu bbox; relief zanurzony 0,1 w podłoże przed unią. | [ZAŁOŻENIE] |
| R23 | Żebra korpusu i blatu „do rozstrzygnięcia”. | Korpus: 4 żebra 2 × 6 od podkładek panelu (od r = 8) po przekątnych do narożników ścian, przerwane tam, gdzie wchodzą w strefę Pi (x < −5, |y| < 30) lub kieszeń DC. Blat: bez żebra (R41). | [ZAŁOŻENIE] |
| R24 | Kształt daszków wentylacyjnych. | Pełny okap: płyta szerokości 14 (szczelina 12 + 1 z każdej strony), grubość 1,5 mierzona prostopadle do lica daszka; dolne lico zaczyna się na zewnętrznym licu ściany na górnej krawędzi szczeliny (Z 9,5) i schodzi 45° na zewnątrz przez wysięg 2 (do Z 7,5 na y = 102); nasada 1 mm w ścianie; na y = 101 daszek zajmuje Z 8,5…10,6. | [ZAŁOŻENIE] |
| R25 | (uchylone przez Z28 — głowica usunięta) | — | — |
| R26 | Promienie niewymienione. | Zewnętrzne 3, wewnętrzne 1 — stosowane tylko tam, gdzie plan pisze „zaokrąglone” bez wartości; pozostałe krawędzie ostre (zaokrąglanie każdej krawędzi to setki booleanów bez zysku dla druku SLS). | [ZAŁOŻENIE] |
| R27 | Kolory renderu. | Grafit #3b3e43, biały #efede6, pleksi #e8ecef półprzezroczysta, PCB #1f6b3a, mosiądz #c8a24a. | [ZAŁOŻENIE] |
| R28 | Jak podstawić parametry DO ZMIERZENIA bez przerabiania całości. | Edycja `parametry.json` (wartość + `"status": "ZMIERZONE"`), `blender -b -P ramka_generator.py -- --etap ALL`, pełna recenzja. Żadnej ręcznej edycji STL. | [FAKT] |
| R29 | Naroża kieszeni dyfuzora R 1 a pleksi cięta na ostro. | Pleksi: sfazować rogi 1 mm (instrukcja montażu krok 9). | [FAKT] |
| R30 | Uszy wkładki leżą częściowo na dyfuzorze, częściowo na blacie. | Dyfuzor licowany z blatem (Z 58,6), więc uszy leżą płasko; sprawdzenie K‑33. | [FAKT] |
| R31 | Ścianki kieszeni DC 2 mm a ściana 2,5. | Zostaje 2; kieszeń nie jest nośna. | [ZAŁOŻENIE] |
| R32 | Pole „kąt” rynienki w JSON. | `angle` 0 = oś rynienki wzdłuż X. | [FAKT] |
| R33 | Dwa korpusy różniące się napisem. | Dwa STL (`_W`, `_P`), w arkuszu po 1 szt. | [FAKT] |
| R34 | Uchwyt kabli: plan „ilość 2” przy 2 bossach na ramkę. | 4 szt. (2 na ramkę). | [FAKT] |
| R35 | Spec 4.3: rama wkładki 3 mm; plan 6 mm (Z7). | 6 mm; ścianka nad matrycą 4 mm szeroka (spec: ≤ 4) — spełnione. | [FAKT] |
| R36 | Spec tabela 6 vs ilości w arkuszu. | Płytki 3 + 3 (n1…n6), pokrywka 4, korpus 2 (W + P), blat 2, rama 2, wkładka 3, uchwyt 4 (głowica i zaślepka usunięte, Z28). | [FAKT] |
| R37 | sesja2 0.1.4 nakazuje instalować Blendera. | Wykonawca używa Blendera wskazanego przez właściciela w `prompt_wykonawca.md`; niczego nie instaluje. | [FAKT] |
| R38 | Zamknięte pustki: kieszeń DC zamknięta od dołu i boków. | Jest otwarta na zewnątrz przez otwór 36 × 24 → nie jest pustką zamkniętą. | [FAKT] |
| R39 | (uchylone przez Z28 — głowica usunięta) | — | — |
| R40 | Pozycje w rzędach a wymaganie „symetrycznie względem x = 0”. | Wszystkie rzędy w D6 symetryczne; sprawdzenie K‑05 liczy symetrię z JSON. | [FAKT] |
| R41 | Żebro obwodowe blatu 166 × 166 (Z 48,6…54,6) przenikało kołnierz ramy dyfuzora (161…170, Z 48,6…54,6) — wykryte przy budowie modelu 3D. | Żebro usunięte; sztywność daje kołnierz blatu 10 mm i rama przykręcona w 4 punktach. | [FAKT] |
| R42 | Garby pokrywki na środkach przodu i tyłu wypadały w wycięciach palcowych 30 × 3. | Garby: boki y = 0, przód x = +25, tył x = −25; parametr `cover_snap_front_x`. | [FAKT] |
| R43 | Uchwyt kabli (±25, 82) ze stopą 40 (X) × 20 (Y) wchodził 5 mm w skrzynkę kieszeni DC (x −80…−40). | Uchwyty obrócone osią długą wzdłuż Y, bossy w (±20, 75); stopa x ±(10…30), y 55…95. | [FAKT] |
| R44 | Uszy ramy dyfuzora (±86, ±86, Z 48,6…54,6) zajmowały tę samą przestrzeń co bossy blatu (±86, ±86, Z 48,6…54,6), a bossy przenikały narożnik kołnierza ramy (80,5…85). | Bossy i uszy w (±90, ±90); uszy na Z 44,6…48,6 pod bossami; wkręty M3 × 10. Kształt ucha: R46. | [FAKT] |
| R46 | Mostek 4 × 4 z R44 od (±85, ±85) dotykał kołnierza (80,5…85, Z od 48,6) tylko w punkcie narożnika — ucho nie było połączone z ramą (wykryte w modelu 3D). | Ucho = łapa narożna 13 × 13 × 4 (x, y ±81…±94, R 4 zewn.) na Z 44,6…48,6, nakładająca się pod kołnierz na polu 81…85 × 81…85 (zespolenie 4 × 4 mm w rzucie, pełna grubość 4); otwór ø3,4 w (±90, ±90). Luzy: do kołnierza blatu (95,2) 1,2; do dystansów panelu ≥ 20. | [FAKT] |
| R47 | Bramka G1 — rozbieżności zgłoszone przez wykonawcę (U‑1…U‑10) i recenzenta (uwagi 1–20). | (1) Ucho wkładki łączy się z ramą przez nasadę 3 mm x ±(44…65), y 48,8…58 [U‑1]. (2) Gabaryty w STL z reliefami i kołkami: pokrywka 99,6 × 99,6 × 20,6; wkładka 130 × 148,3 × 11,0; płytki n 8,6 [U‑2, U‑3]. (3) Garby pokrywki na lokalnym Z −18 (rowek płytki), wys. 0,8, R 0,5 [U‑4]. (4) Haczyk blatu: występ Z 47,85…49,85, luz 0,25 w kieszeni 47,6…50,1; nacięcia 1 mm od dołu kołnierza do Z 53,6 (ramię 9) [U‑5, U‑9]. (5) Słupki blatu y 89,2…95,2 po wewnętrznej stronie kołnierza, otwór ø4 × 6 od lica 97,2 [U‑6]. (6) K‑22, K‑32 odsyłają do K‑53 [U‑7]. (7) Kieszeń DC: skrzynka do y 78, w świetle 20 → kryterium pomiaru #16 ≤ 20; bryła gniazda ø12 × 12 [U‑8]. (8) Wszystkie liczby z tekstu planu dostały klucze w `parametry.json` (sekcja 3) [U‑10]. (9) Font Inter z offsetem (R22). (10) Dołki kodu x = −45,0 (materiał do rowka pokrywki 1,3 zamiast 0,86). (11) Daszki zdefiniowane w R24. (12) Napis PRZÓD 2 mm w pasie y −50,0…−52,3, strzałka na lewym segmencie. (13) Przelot Halla w ściance po przekątnej narożnika. (14) Otwory pokrywki: kolumny x ±15, rzędy y −30/0/30; GÓRA 5 mm. (15) Sondy protokołu poprawione wg listy recenzenta (K‑06, K‑17, K‑18, K‑21–K‑25, K‑29, K‑31, K‑32, K‑34, K‑37, K‑46, K‑47, K‑53, K‑54, tabela 1 z jawną osią obrotu blatu); pomiary reliefów i wysokości promieniami dopuszczone jako równoważne. (16) Wariantowe części w `.blend` odsunięte ≥ 250 mm od złożenia; K‑53 tylko na zestawie złożonym (korpus W, blat, rama, wkładka, płytka n1, pokrywka, bryły zastępcze); magnesy: A w n1, B i C w n6 obok. (17) Napis korpusu 8 mm ma ok. 110 mm szerokości — dopuszczone (relief na zewnątrz, kieszeń zatrzasku wewnątrz). | [FAKT] |
| R48 | Audyt tolerancji (pytanie właściciela): ścianki wokół wkładek gwintowanych i luzy dużych pasowań w SLS. | Żadna śruba nie wkręca się bezpośrednio w PA12 (wszędzie wkładki mosiężne lub gwint metalowy: dystanse, nakrętki). Otwory przelotowe M3: ø3,2/3,4 (klasa fine/medium), M2,5: ø2,7. Otwory pod wkładki: ø4,0 (M3, wkładka OD ~4,6 radełkowana) i ø3,4 (M2,5, OD ~4,0) — standard dla wtapiania. Za cienkie ścianki wokół wkładek (ryzyko pęknięcia przy wtapianiu i wkręcaniu) poprawione: boss Pi ø6 → **ø8** (ścianka 1,0 → 2,0), boss uchwytu ø7 → **ø8**, słupek blatu 6 → **8 w X** (ścianka 1,0 → 2,0); boss ramy ø8 (2,0) i słupek 6 w Y (otwór biegnie wzdłuż Y) bez zmian. Luzy: dokładność SLS/MJF to typowo ±0,3 mm na 200 mm (poza chropowatością), więc kołnierz blatu w korpusie 0,3 → **0,5 na stronę** (194,0 w 195), a haczyk 1,0 → **1,3** (zahacza 0,8 w kieszeni 1,0; ugięcie 1,3 na ramieniu 9 × 1,5 PA12 — OK). Pozostałe luzy bez zmian: płytka we wkładce 0,3/stronę (96 mm → ±0,15–0,3 → luz 0…0,6; kołek orientacyjny ustala położenie), pokrywka 0,3, dyfuzor 1,0, rama–panel 0,5, kołki ø3 w ø3,3 (0,15 — wcisk lekki wg 4.8), magnesy ø5 w ø5,2/5,4 (klejone). Na G4b karta pasowań mierzy wszystko z STL. | [FAKT] |
| R49 | Decyzja właściciela: bez wkładek gwintowanych (uproszczenie montażu). | Wkręty formujące gwint bezpośrednio w PA12 (dopuszczone w spec 4.8): otwory ø2,5 × 7 pod M3/PT 3,0 × 8 i ø2,1 × 5 pod M2,5/PT 2,5 × 6; bossy ø8 zostają (ścianka 2,75). Dotyczy: bossy Pi (4), bossy uchwytów (2), bossy ramy w blacie (4), słupki blatu (2). Nylon PA12 dobrze trzyma gwint formowany (≥ 10 cykli); przy serwisie nie przekręcać. Z listy zakupów znikają wkładki i grot do wtapiania. | [FAKT] |
| R49a | Otwór ø2,5 × 7 w słupku blatu zostawiał 1,0 mm dna (recenzent). | Głębokość 6 (`blat_post_hole_depth`): od lica kołnierza 97,0 (po R48) do 91,0, dno 1,8 ≥ 1,5. | [FAKT] |
| R51 | Etap B, odstępstwa wykonawcy #1, #2, #6: napis PRZÓD nieczytelny przy trzonie ≥ 1,0; żebra od r = 8 bez klucza; nasada ucha zasłaniała 12,7 × 3,5 mm prawego pasu (K‑56). | (1) Bez napisu „PRZÓD” — tylko strzałki ▼ na obu segmentach (`insert_label_h` 0, `insert_arrow_x` ±32); K‑31 sprawdza same strzałki. (2) Żebra od krawędzi podkładki (`rib_start_r` 4,5). (3) Nasada ucha w kształcie L: x ±(44…52,3) od y 48,8, x ±(52,3…65) od y 52,3 — prawy pas w całości odsłonięty; K‑29 sondy poprawione. Odstępstwa #3, #4 przyjęte informacyjnie; #5 → R49a. | [FAKT] |
| R52 | Trzecie oko (G4b, 27.10, 0 blokujących): uwagi U1–U7. | (U1) `dc_bush_outer_d` 12 → **11,85** (wcisk 0,15 w otworze ø12; tylko druk własny, pliki drukarni bez zmian). (U2) 4.11: luz kołka orientacyjnego 0,4 (zgodnie z 4.6.4), nie 0,3. (U3) Wtyk prosty DC: korpus ≤ 37 mm od lica (realne lico z kołnierzem tulejki i flanszą x −45); lista zakupów i sekcja 10 #16. (U4/U5) Sekcja 9: wtyk DC Bonnetu wpiąć przed przykręceniem Pi (−X: 7,5 mm); gniazdo USB panelowe przed panelem (14,3 mm do dystansu). (U6) Rampa haczyka = dolna 1,0 z występu 2,0, lico pionowe 1,0, zahaczenie 0,8 — zgodne z R48 (informacyjnie). (U7) Opisy kołnierza 95,0…97,0 poprawione. Raport: `recenzja_koncowa/raport_koncowy.md`. | [FAKT] |
| **R50 — odporność na pomiary** (analiza `analiza_odpornosc_R50.md`, właściciel: „[cytat usuniety]”) | | | |
| R50‑1 | Łańcuch wysokości zależał od 3 niezmierzonych parametrów (led_h, bottom_parts_h, pi_stack_h); korpus 400–700 zł nie dawał się zamówić bez elektroniki. | `pi_clearance_top` 3 → 8 ⇒ `panel_pcb_z` 54, `blat_top_z` 63,6, `korpus_h` 59,6, `panel_standoff_l` 50 (stock). Pokrywa stos z taśmą do 31 albo złącza panelu z kablami do 17 (łącznie +5) oraz led_h 1…3 (luz dioda–dyfuzor 5…3). Wartości globalne LICZONE: `snap_pocket_z` = korpus_h − 7, `snap_hook_z` = korpus_h − 6,75, `blat_screw_z` = korpus_h − 4,6, `label_pos_z` = korpus_h − 8,6. Wysokość 63,6 przekracza spec 55–60 o 3,6 — zaakceptowane. Po pomiarach wysokości są zamrożone (sekcja 10). | [ZAŁOŻENIE, zatwierdzone] |
| R50‑2 | Podkładki panelu w (±60, ±60) zależały od rozstawu otworów panelu (brak normy, 110–136). | Podkładki‑stadiony 9 × 1 i rowki przelotowe 3,4 w dnie wzdłuż przekątnych od (±55, ±55) do (±65, ±65) (`panel_slot_pitch_min/max` 110/130, `panel_slot_w`); wzór niekwadratowy/offset → wiercenie ø4 w dnie + podkładka R50‑8. `panel_hole_pitch_*`/`offset_*` tylko dla brył zastępczych. Odrzucone: siatka otworów, szyny panelu. | [ZAŁOŻENIE, zatwierdzone] |
| R50‑3 | Gniazdo DC w dnie kieszeni (oś Y) celowało w dystans panelu (−60, 60) i zależało od długości korpusu gniazda, średnicy (8/12) i wysięgu wtyku. | Gniazdo w prawej ścianie skrzynki (x = −40), oś (y 89, Z 30) wzdłuż X (`dc_socket_axis`, `dc_pos_x` −40, `dc_pos_y` 89); otwór ø12 + tulejka redukcyjna ø12/ø8,2 × 2 z kołnierzem ø15 × 1 (`ramka_tulejka_dc_v2.stl`, `dc_bush_*`) dla gniazd ø8; `dc_pocket_depth` 22 przestaje być DO_ZMIERZENIA. | [ZAŁOŻENIE, zatwierdzone] |
| R50‑4 | Wtyk prosty nie mieścił się w kieszeni 36. | Skrzynka do lewej ściany (x −97,5…−40), okno 51 (x −93…−42, `dc_pocket_w` 51, `dc_pocket_x_window` −67,5). | [ZAŁOŻENIE, zatwierdzone] |
| R50‑5 | Okno USB 15 × 8 i otwory flanszy w rozstawie 22 zależały od modelu gniazda. | Okno 16 × 9 (`usb_cut_w/h` ZALOZENIE) + rowki poziome 3,2 × 5,7 o osiach 60 ± 11,5…14 (`usb_slot_pitch_min/max` 23/28 — przy 20 ścianka do okna miałaby 0,4; `usb_slot_w`); rozstaw 22 → spiłować 0,5; flansza z otworami pionowymi → wiercenie. Odrzucone: ramka adaptera. | [ZAŁOŻENIE, zatwierdzone] |
| R50‑6 | Pi w (−92, −28): kierunek −X wtyku DC Bonnetu (najbardziej prawdopodobny, A‑4) był fizycznie niemożliwy (5,5 do ściany). | `pi_pos_x` −50 (Pi x −50…35), bossy (−46,5/11,5, ±24,5), `floor_vent_x` −8; `bonnet_dc_pos` domyślnie (−50, 22), `bonnet_dc_dir` −X, `bonnet_dc_plug_len` 40; kierunki −X/−Y/+Y mieszczą wtyk 40, +X wyklucza Bonnet. D10 bez „krawędź SD poza panelem”. | [ZAŁOŻENIE, zatwierdzone] |
| R50‑7 | R5 (dystans M‑F wkręcany w gwint panelu) nie działał bez gwintu, a 6‑mm trzpień wystawałby od strony diod. | Z gwintem: dystans F‑F 50 + wkręt dociskowy M3 × 5. Bez gwintu: tulejka F‑F M3 ø5 × 5 doklejona epoksydem do spodu PCB + dystans F‑F 45 (3 + 1 + 45 + 5 = 54). Nakrętka/nitonakrętka od strony diod wykluczone. Bez zmian geometrii drukowanej; lista zakupów i krok 8. | [ZAŁOŻENIE, zatwierdzone] |
| R50‑8 | Dobór długości dystansu po pomiarach wymagał zmiany korpusu (`panel_pad_h`). | Komplet podkładek ø9 × (0,5 / 1 / 2) z otworem 3,4 (`ramka_podkladka_panelu_05/_1/_2_v2.stl`, po 8 szt., druk własny; `panel_shim_*`). | [ZAŁOŻENIE, zatwierdzone] |
| A‑1…A‑9 | Założenia o typowym sprzęcie (panel HUB75 64 × 64 P2.5, Pi 4 + Bonnet, gniazda DC/USB, odbiornik, skaner, bramka G3) z `analiza_odpornosc_R50.md` sekcja 0. | Przyjęte jako [ZAŁOŻENIE]; pomiary sekcji 10 je potwierdzają albo uruchamiają fallbacki (wiercenie, tulejka, podkładki). | [ZAŁOŻENIE, zatwierdzone] |
| **R50‑U — uproszczenia** (analiza sekcja 6, właściciel: „[cytat usuniety]”, „[cytat usuniety]”) | | | |
| R50‑U1 | Rama dyfuzora jako osobna część (4.5) + 4 bossy ø8 × 6 w blacie. | **USUNIĘTE** (bez pianki ani uszczelnienia w zamian). Panel ustalają 4 dystanse M3 w jego otworach; światło/pył z krawędzi panelu tylko do wnętrza obudowy. Klucze `rama_*`, `rama_boss_*` usunięte z JSON; K‑48 uchylone; K‑49/K‑53/K‑54/K‑33/K‑47 bez ramy i bossów. | [ZAŁOŻENIE, zatwierdzone] |
| R50‑U2 | 2 wkręty tylne blatu i słupki. | **ZOSTAJĄ** (ramka poranna codziennie noszona do szafki; R49a bez zmian). | odrzucone |
| R50‑U3 | 4 zatrzaski vs tylko wkręty; nacięcia. | **ZOSTAJĄ** bez zmian. | odrzucone |
| R50‑U4 | Daszki nad szczelinami (R24, 20 brył po różnicy). | **USUNIĘTE**: `vent_hood_*` usunięte z JSON; gabaryt korpusu 200 × 200 × 59,6; K‑37 bez sond daszków; R24 bezprzedmiotowe. | [ZAŁOŻENIE, zatwierdzone] |
| R50‑U5 | Żebra dna (R23, R51(2)). | **USUNIĘTE**: `rib_*` usunięte; K‑44 bez żeber (zostaje R 3 dolnej krawędzi). | [ZAŁOŻENIE, zatwierdzone] |
| R50‑U6 | Szczelina SD w dnie (Z14). | **USUNIĘTA**: `sd_slot_*` usunięte; karta po zdjęciu blatu i panelu; K‑35 bez sond SD. | [ZAŁOŻENIE, zatwierdzone] |
| R50‑U7 | Kieszeń DC vs gniazdo w licu ściany. | **ZOSTAJE** kieszeń (Z27), w wersji R50‑3/R50‑4. | odrzucone |
| R50‑U8 | Uchwyty kabli drukowane (4.9) + 2 bossy. | **USUNIĘTE**: podstawki opasek samoprzylepne 20 × 20 + taśma VHB (lista zakupów); `holder_*`, `proto_board_*` usunięte; K‑52 uchylone; K‑36 bez bossów uchwytów; R9, R34, R43 bezprzedmiotowe. | [ZAŁOŻENIE, zatwierdzone] |
| R50‑U9 | Kanały kablowe wkładki: 11 brył (kanał pod półką + przelot + rowek) × 3 + 2. | **SCALONE**: rowek zewnętrzny 2,5 szer. × 1,5 wys. (`wire_rabbet_w` 2,5) i przelot w ściance narożnika o tym samym przekroju jako jedna bryła ciągła; kanał pod półką 2,5 × 1,0 bez zmian. Do otworu zostaje 1,5. K‑25/K‑30 sondy dostosowane. Przyklejanie przewodów zamiast kanałów odrzucone (wkładka leży płasko). | [ZAŁOŻENIE, zatwierdzone] |
| R50‑U10 | Uszy, kołki, magnesy wkładki. | **ZOSTAJĄ**; drobne: kołek ø3 × 3,5 jako jedna bryła (walec 3,0 + stożek ścięty ø3 → ø2 na 0,5) zamiast walca + fazy (`tab_pin_chamfer` opis). | [ZAŁOŻENIE, zatwierdzone] |
| R50‑U11 | Półki narożne z kieszeniami Halla vs czujniki pod dyfuzorem. | **ZOSTAJĄ** bez zmian (Z6, oparcie kołka, serwisowalność czujników). | odrzucone |
| R50‑U12 | Kołek orientacyjny. | **ZOSTAJE**. | odrzucone |
| R50‑U13 | Wycięcie palcowe wkładki. | **ZOSTAJE**. | odrzucone |
| R50‑U14 | Napisy reliefowe. | **CZĘŚCIOWO**: napis korpusu „RAMKA WIECZORNA/PORANNA” ZOSTAJE (2 STL W/P, Z28); strzałki ▼ wkładki ZOSTAJĄ; usunięty tylko relief „GÓRA” pokrywki (`cover_label_h`, `cover_label_text` usunięte; K‑21 uchylone; pokrywka 99,6 × 99,6 × 20,0). | [ZAŁOŻENIE, zatwierdzone] |
| R50‑U15 | Promienie wewnętrzne na cechach tnących. | **CZĘŚCIOWO**: naroża okna DC (`dc_pocket_corner_r` 0), kieszeni dyfuzora (`diffuser_pocket_r` 0; pleksi bez fazowania, R29 uchylone), otworu wkładki (`insert_opening_r` 0) → ostre. Promienie zewnętrzne (R 5, R 3, R 1,5, R 3 pokrywki) i kołnierz blatu R 4,5/2,7 bez zmian. `sd_slot_r` usunięty z U6. | [ZAŁOŻENIE, zatwierdzone] |
| R50‑U16 | Gniazda stopek ø10,5 × 0,5. | **USUNIĘTE**: `foot_pocket_*` usunięte; stopki samoprzylepne na płaskim dnie; K‑44 bez stopek. | [ZAŁOŻENIE, zatwierdzone] |
| R50‑U17 | 6 otworów ø4 w pokrywce. | **USUNIĘTE**: `cover_vent_*` usunięte; K‑19 uchylone. | [ZAŁOŻENIE, zatwierdzone] |
| R50‑U18 | Rowek pokrywki w płytce. | Bez zmian (płytki zamknięte; zatrzaski pokrywki zostają). | — |
| R50‑U19 | 20 szczelin wylotowych + wloty 2 × 20 × 3. | **ZMNIEJSZONE**: tył 4 (x −54, −18, 18, 54), boki po 3 (y −36, 0, 36); wloty 2 × 30 × 4 (`floor_vent_l/w` 30/4). Wylot 360 mm² + luz blatu 400 mm², wlot 240 mm². K‑37 sondy na nowych pozycjach. | [ZAŁOŻENIE, zatwierdzone] |
| R50‑U20 | Pogłębienia ø6,5 × 2 pod wkręty panelu od spodu. | **USUNIĘTE**: `panel_screw_cbore_*` usunięte; łeb M3 + podkładka ø9 pod dnem (2,5 < stopki 4); rowek 3,4 w pełnym dnie 3. K‑35 bez sond pogłębień. | [ZAŁOŻENIE, zatwierdzone] |
| R50‑JSON | Sposób zapisu usuniętych cech w `parametry.json`. | Jedna zasada: **cecha usunięta = jej klucze usunięte z JSON** (walidator wykonawcy musi je wykreślić z listy wymaganych); **cecha zmieniona = wartość zmieniona** (np. promień → 0). Pełna lista kluczy nowych/usuniętych: `R50_wdrozenie_zmiany.md`. | [FAKT] |
| R45 | Decyzja właściciela Z28: brak przycisku i czujnika gestu. | Usunięte: D15 (stare), 4.7, 4.8, parametry `button_*`, `head_*`, `tof_*`, `plug_*`, pozycje zakupów (VL53L1X, przycisk, tranzystor, rezystory LED, JST 4‑pin), trasy kabli 5–6, wiersze tabeli połączeń, pomiary #15 i #18, sprawdzenia K‑26, K‑40 (część), K‑41, K‑50, K‑51, bryła zastępcza `proxy_przycisk`; gabaryt korpusu bez zmian; obudowy W i P identyczne poza napisem. | [FAKT] |

---

## 14. Zmiany względem plan_ramki_v1.md
1. Nagłówek: plik nadrzędny, reguły pierwszeństwa (R1).
2. D4/D13: mocowanie panelu — podkładka 1 + dystans 45 zamiast boss 11 + dystans 35 (R5); parametry `panel_pad_h`, `panel_pad_d`, `panel_screw_*`; usunięty `panel_boss_h`.
3. D9: kieszenie i haczyki zatrzasków 1,0; położenia (R6); słupki i wkręty blatu ±75 (R7); parametry `snap_side_y`, `snap_front_x`, `snap_rear_x`, `blat_screw_pitch` 150.
4. D11/4.1: dołki kodu x = −45,0, y = −36/−33/−30 (R3); plik bazowy i warianty (R4); pełna struktura JSON i numeracja (R13).
5. D14/4.3: USB x = 60 (R10); uchwyty kabli (±25, 82) (R9); parametry `holder_pos_x/y` zamiast `cable_holder_pos`.
6. 3.2: `bonnet_dc_pos` domyślnie (−60, −28), nowy `bonnet_dc_dir` (R11).
7. 3.4: `hall_lead_channel_h` 1,0 (R20); `blat_pin_hole_depth` 3,8, otwór ślepy (R8).
8. 3.5: tylko uchwyt kabli i odbiornik (głowica, zaślepka i ich parametry usunięte, Z28/R45). Nowa 3.6: parametry sterujące (sufiks, napisy, font, promienie, kolory, stawki).
9. 4.9: uchwyt 4 szt. (R34). 4.11: nowe wiersze rachunków (dołki, słupki, uchwyty, napis, wtyk Bonnetu).
10. 5: dystanse 45. 7: tabela mocowań i trasy kabli. 9: krok 8. 10: pomiary #5a, #10, #18 i procedura podmiany (R28).
11. 12: nowa lista plików (R2, R16, R17), odwołanie do protokołu, brak kwestii otwartych. 13: rejestr rozstrzygnięć. 14: ta lista.
12. Po kontroli modelem 3D (R41–R44): bez żebra blatu; garby pokrywki przód x = +25, tył x = −25; uchwyty kabli obrócone, bossy (±20, 75); bossy blatu i uszy ramy dyfuzora w (±90, ±90), uszy ø8 × 4 na Z 44,6…48,6 pod bossami; parametry `rama_ear_t`, `blat_rib`, `holder_axis`, `cover_snap_front_x`.
13. Z28/R45 (decyzja właściciela): bez przycisku, zaślepki i głowicy; przednia ścianka gładka z napisem; usunięte parametry, zakupy, kable, pomiary #15 i #18, sprawdzenia K‑26, K‑41, K‑50, K‑51; K‑40 sprawdza gładkość ścianki; 13 plików do zamówienia.
14. R46: ucho ramy dyfuzora = łapa narożna 13 × 13 × 4 nakładająca się pod kołnierz (mostek z R44 nie łączył ucha z ramą).
15. R47 (bramka G1): nasada ucha wkładki, gabaryty STL z reliefami, garby pokrywki Z −18, haczyk blatu Z 47,85…49,85 i ramię 9, słupki y 89,2…95,2, dołki kodu x −45,0, font Inter, daszki, napis PRZÓD 2 mm, przelot Halla, nowe klucze parametrów, sondy protokołu.
16. R48 (tolerancje): boss Pi ø8, boss uchwytu ø8, słupek blatu 8 × 6, luz kołnierza blatu 0,5/stronę (194,0), haczyk 1,3.
17. R49: bez wkładek gwintowanych — wkręty formujące gwint w PA12, otwory ø2,5 (M3) i ø2,1 (M2,5).
18. R49a: otwór słupka blatu 6 głęboki (dno 1,8). R51 (etap B): bez napisu „PRZÓD” (strzałki ▼ na obu segmentach), żebra od krawędzi podkładki, nasada ucha L.
19. R50‑1…R50‑8 (odporność na pomiary, zatwierdzone przez właściciela): wysokość 63,6 / korpus 59,6 / dystans 50 F‑F; rowki panelu 110–130 po przekątnej; gniazdo DC w prawej ścianie skrzynki osią X, ø12 + tulejka ø8; kieszeń do lewej ściany, okno 51; okno USB 16 × 9 + rowki 23–28; Pi w (−50, −28); mocowanie panelu z gwintem i bez; podkładki 0,5/1/2. Założenia A‑1…A‑9. Wartości LICZONE: `snap_pocket_z`, `snap_hook_z`, `blat_screw_z`, `label_pos_z`.
20. R50‑U1…U20 (uproszczenia): usunięte rama dyfuzora i bossy blatu, daszki, żebra, szczelina SD, uchwyty kabli i bossy, pogłębienia wkrętów panelu, gniazda stopek, otwory i relief „GÓRA” pokrywki; scalone kanały kabli wkładki (rowek 2,5 × 1,5); ostre naroża okna DC, kieszeni dyfuzora, otworu wkładki; 4 + 3 + 3 szczeliny i wloty 30 × 4; kołek wkładki jedną bryłą. Zostają: wkręty tylne blatu, zatrzaski, kieszeń DC, półki Halla, kołek, wycięcie palcowe, napis korpusu, strzałki. Klucze usuniętych cech wykreślone z `parametry.json` (R50‑JSON). Pliki: 10 STL drukarnia + 5 druk własny (pokrywka, tulejka, 3 podkładki). Lista edycji: `R50_wdrozenie_zmiany.md`.
21. R52 (trzecie oko, 27.10): tulejka DC 11,85; opisy 4.11 (kołek 0,4), 9 (kolejność: wtyk Bonnetu przed Pi, USB przed panelem), 5/10 (wtyk prosty ≤ 37).
