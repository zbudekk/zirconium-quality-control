# Plan budowy ramek świetlnych i płytek — plan_ramki_v1

Sesja 1 z 2. Ten plik jest jedynym wejściem sesji 2 (obok specyfikacji). Wszystkie wymiary w mm, kąty w stopniach, jedna liczba na wymiar.

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
| Z8 | Stos Pi 4 + Bonnet od spodu PCB Pi do najwyższego elementu Bonnetu: 26 mm (`pi_stack_h`, DO ZMIERZENIA). | PCB 1,6 + złącze GPIO 11 + PCB Bonnetu 1,6 + gniazdo DC Bonnetu 11 = 25,2; zapas 0,8. |
| Z9 | Elementy od spodu panelu HUB75 (złącza, kondensatory) sięgają 12 mm poniżej PCB (`panel_bottom_parts_h`, DO ZMIERZENIA) i mogą być w dowolnym miejscu spodu. | Bez pomiaru nie wolno zakładać wolnego miejsca pod panelem; stąd Pi mieści się pod panelem w całości poniżej złączy. |
| Z10 | Otwory montażowe panelu: 4 szt. M3 na kwadracie 120 × 120 mm wokół środka (`panel_hole_pitch`, DO ZMIERZENIA). | Typowy rozstaw dla paneli 160 × 160; wartość domyślna tylko po to, by model powstał. |
| Z11 | Bonnet zasila Pi przez pin 5 V złącza GPIO; w obudowie jest jedno gniazdo DC. | Tak działa Adafruit RGB Matrix Bonnet; drugi zasilacz byłby zbędny. |
| Z12 | Wolne GPIO wyprowadzamy lutując kątową listwę do pinów złącza 2×20 od góry Bonnetu. | Bonnet nie ma listwy przelotowej, a potrzebujemy 7 sygnałów + zasilania. |
| Z13 | Gniazdo USB serwisowe w tylnej ściance to panelowe gniazdo USB‑A z zaślepką, kabel 30 cm do portu USB Pi. | Pi leży pod panelem, więc jego porty nie dochodzą do ściany; przedłużacz uniezależnia pozycję Pi. |
| Z14 | Karta SD dostępna przez szczelinę w dnie korpusu pod krawędzią Pi (obudowa położona na boku), bez demontażu. | Pi pod panelem nie da dostępu od góry po zdjęciu blatu; szczelina w dnie skierowana w dół spełnia wymóg pyłowy. |
| Z15 | Blat: 4 zatrzaski na kołnierzu + 2 wkręty M3 przez tylną ściankę (nie od dołu). | Wkręty od dołu wymagałyby słupków 55 mm; wkręty w tylnej ściance są niewidoczne od frontu i z góry. |
| Z16 | Przycisk arkadowy: otwór ø30, wersja z diodą LED 5 V. | Wersje 12 V wymagałyby przetwornicy; ø30 to wartość domyślna parametru `button_hole_d`. |
| Z17 | Klawiatura numeryczna: 130 × 90 × 20 mm, odbiornik USB nano 19 × 15 × 6 (DO ZMIERZENIA). | Typowe wymiary bezprzewodowych klawiatur numerycznych 2,4 GHz. |
| Z18 | Napis na przedniej ściance jest parametrem tekstowym; korpus eksportuje się dwa razy (`_W`, `_P`), geometria identyczna. | Spec chce identycznych obudów i napisu nazwy jednocześnie; różni się tylko relief. |
| Z19 | Kolor: korpus, blat, rama dyfuzora, głowica, zaślepka — PA12 barwiony na grafit; wkładka, płytki, pokrywka, uchwyty — PA12 naturalny biały. | Zgodnie z 4.7; biały pod skaner, grafit na pokaz. |
| Z20 | Gniazda w rzędach rosnąco od przodu, rynienki w dwóch tylnych rzędach. Wieczorna 24 (13 × ø9, 6 × ø12, 5 × ø15) + 2 rynienki; poranna 35 (22 × ø7,5, 7 × ø10, 6 × ø12,5) + 2 rynienki. | Uporządkowany układ jest czytelny dla technika i programu; tyle rzędów mieści się w 90 mm przy ściankach dokładnie 3 mm (rachunek w D6); wieczorna ma mniej ø12 niż w spec (6 zamiast 9), bo każdy dodatkowy rząd kosztuje 3 mm ścianki. |
| Z21 | Orientacja płytki: narożnik z wycięciem = przód‑prawy (D); czujniki Halla pod A (przód‑lewy), B (tył‑lewy), C (tył‑prawy). | Wycięcie z przodu po prawej jest dobrze widoczne dla praworęcznego technika. |
| Z22 | Ceny w liście zakupów są orientacyjne (wyszukiwanie nie zwróciło cen w zł). | Zaznaczone zgodnie z 0.1.5. |
| Z23 | Odstęp dioda–dyfuzor 4 mm (`led_gap`). | Środek zakresu 3–5 mm ze spec. |
| Z24 | Rynienki mają 4 otwory ø3 w dnie (rozstaw 12 mm wieczorna, 10 mm poranna). | Jeden otwór nie doświetliłby 60‑mm mostu. |
| Z25 | Rola przycisku (ramka wieczorna): krótkie naciśnięcie = „Skanuj / Potwierdź” (to samo zdarzenie co gest), przytrzymanie 2 s = wygaszenie i ponowne włączenie matrycy. LED przycisku: miga = czeka na skan, świeci = wynik wyświetlony, zgaszony = brak płytki. | Spec wymienia „jeden fizyczny przycisk” bez funkcji; ręczny zapas dla gestu jest potrzebny, gdy czujnik nie zadziała lub technik ma zajęte ręce. |
| Z26 | Bez podstawki klawiatury i bez nalepki z legendą (odstępstwo od spec 4.6 i tabeli 6). Klawiatura leży luzem na stole; legenda klawiszy tylko w instrukcji programu. | Klawiatura ma własne stopki, a tacka to ok. 60 cm³ druku bez funkcji; użytkownik nie chce nalepki. |
| Z27 | Ramka poranna jest chowana do szafki, więc gniazdo DC siedzi w kieszeni wgłębionej w tylnej ściance (36 × 24, głębokość 22), a zasilacz ma wtyk kątowy 5,5/2,1 — wtyk nie wystaje poza obrys 200 × 200. Obudowy są identyczne, więc kieszeń ma też ramka wieczorna. | Wystający prosty wtyk łamałby się przy wsuwaniu ramki do szafki i wymuszał odpinanie zasilacza. |

---

## 2. Decyzje projektowe

### D1. Wariant obudowy — rekomendacja: WYSOKI (Pi pod panelem)

| Kryterium | Wysoki 200 × 200 × 58,6 | Niski 200 × 270 × 40 |
|---|---|---|
| Realna wysokość | łańcuch: 3 + 5 + 26 + 3 + 12 + 1,6 + 2 + 4 + 2 = 58,6 | stos Pi 26 + słupki 5 + dno 3 + luz 3 + blat 4 = 41 → nie 35, jak w spec |
| Zajęte miejsce na parapecie | 400 cm² | 540 cm² (+35 %) |
| Kabel HUB75 | ~150 mm, złożony pod panelem | ~250 mm przez przegrodę |
| Dostęp do karty SD | szczelina w dnie (Z14) | od góry po zdjęciu blatu |
| Pył na elektronice | Pi zakryty panelem i blatem | osobna komora, jedna więcej przegroda |
| Sztywność blatu | okno 158 w blacie 200, ramiona 19 mm | blat 270 z oknem i komorą, więcej żeber |
| Objętość druku korpusu | ~215 cm³ | ~250 cm³ |
| Wygląd | kompaktowa kostka, identyczna z każdej strony | płaski, asymetryczny |

Rekomendacja: wariant wysoki. Sesja 2 modeluje tylko jego. Wysokość liczona z parametrów, więc po pomiarze `pi_stack_h` i `panel_bottom_parts_h` może zmaleć do ~52 mm.

### D2. Technologia i materiał każdej części
Wszystkie części zamawiane: SLS/MJF PA12. Płytki i pokrywka: PA12 naturalny biały, bez wygładzania wierzchu (mat dla skanera). Korpus, blat, rama dyfuzora, głowica, zaślepka: PA12 barwiony na grafit (wariant pokazowy: barwienie + wygładzanie parowe). Wkładka, uchwyty kabli: PA12 naturalny. Alternatywa CNC z PMMA opal 8 mm tylko dla płytek, jeśli usługodawca nie ma PA12 — wtedy STEP przez FreeCAD (sesja 2 dodaje notatkę w arkuszu).

### D3. Układ współrzędnych (globalny, dla wszystkich części)
Początek: środek obrysu korpusu w płaszczyźnie jego zewnętrznego dna (bez stopek). X w prawo (patrząc od użytkownika), Y do tyłu (od użytkownika), Z w górę. Przód ramki = −Y. Środek panelu, dyfuzora, wkładki i płytki = (0, 0). Płytka ma lokalny układ: środek górnej powierzchni, te same kierunki osi; narożniki: A = (−48, −48) przód‑lewy, B = (−48, +48) tył‑lewy, C = (+48, +48) tył‑prawy, D = (+48, −48) przód‑prawy (wycięcie).

### D4. Łańcuch wysokości (wariant wysoki), Z od zewnętrznego dna
| Poziom | Z [mm] | Składnik |
|---|---|---|
| wierzch dna korpusu | 3,0 | `floor_t` |
| spód PCB Pi | 8,0 | + `pi_standoff_h` 5 |
| szczyt stosu Pi+Bonnet | 34,0 | + `pi_stack_h` 26 |
| najniższy element spodu panelu | 37,0 | + `pi_clearance_top` 3 |
| spód PCB panelu | 49,0 | + `panel_bottom_parts_h` 12 → `panel_pcb_z` |
| lico diod | 52,6 | + `panel_pcb_t` 1,6 + `panel_led_h` 2 |
| spód dyfuzora | 56,6 | + `led_gap` 4 |
| wierzch dyfuzora = wierzch blatu | 58,6 | + `diffuser_t` 2 → `blat_top_z` |
| wierzch korpusu (pod blatem) | 54,6 | `blat_top_z` − `blat_t` 4 → `korpus_h` |
| wierzch półek wkładki | 61,1 | + `insert_shelf_h` 2,5 |
| wierzch ramy wkładki | 64,6 | + `insert_h` 6 |
| wierzch płytki | 69,1 | półka + `plate_thickness` 8 |
| szczyt najwyższej pracy | 79,1 | płytka − 4 + 14 |

Słupki panelu: `panel_boss_h` 11 (drukowany, z wkładką M3) + mosiężny dystans `panel_standoff_l` 35 → 3 + 11 + 35 = 49 = `panel_pcb_z` ✓.

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

Suma: 7,5 × 3 + 10 + 12,5 + 13 + 13 + 6 × 3 = 89 ≤ 90 ✓. Razem 35 gniazd + 2 rynienki (22 × ø7,5, 7 × ø10, 6 × ø12,5). Gdyby 35 gniazd było za dużo, sesja 2 usuwa R3 (zostaje 27 + 2) bez zmian pozostałych rzędów.

### D7. Czujnik Halla i elektryka (pkt 0.3.3)
A3144: VCC 5 V, GND, OUT otwarty kolektor → 10 kΩ do 3,3 V na płytce prototypowej + wejście GPIO. Logika: magnes obecny = stan niski. Biegun: południowy (S) skierowany w dół, do czujnika, we wszystkich płytkach — przed klejeniem oznaczyć S flamastrem (strony przyciągające się mają przeciwne bieguny; wzorzec: jeden magnes oznaczony raz, reszta względem niego). Alternatywa bez zmian w planie: Honeywell SS451A lub TI DRV5032 (omnipolarne, 3,3 V), ta sama obudowa TO‑92 i ten sam układ pinów VCC/GND/OUT; wtedy biegun dowolny.

### D8. Pokrywka płytki (pkt 0.3.4)
Luz liczony nad najwyższą pracą: `cover_inner_h` = `max_work_height` 14 − `socket_depth` 4 + 4 = 14 mm nad wierzchem płytki. Pokrywka to nakładka z kołnierzem schodzącym 4 mm poniżej wierzchu płytki, 4 zatrzaski (garby 0,7 mm na środkach boków) wchodzą w rowek 1,0 × 0,8 mm wokół boków płytki, 2 mm pod jej wierzchem. Rowek nie koliduje z wkładką (jest cofnięty w głąb płytki).

### D9. Mocowanie blatu
Blat 4 mm z kołnierzem 10 mm wysokim (2 mm grubym, luz 0,3 do ścian) wewnątrz korpusu; 4 haczyki zatrzaskowe (1 na bok, 8 mm szerokie, występ 1,2) w ślepe kieszenie ścian korpusu; 2 wkręty M3 × 8 przez tylną ściankę w wkładki M3 w słupkach kołnierza. Zero śrub na wierzchu.

### D10. Położenie Pi
Pi 4 płasko na 4 słupkach M2,5 (wkładki w drukowanych bossach 5 mm) pod panelem; narożnik PCB Pi (krawędź z kartą SD, przednia) w (−92, −28); karta SD w kierunku −X (lewa ścianka), złącze GPIO wzdłuż krawędzi y = +28; porty USB w kierunku +X (środek obudowy). Krawędź SD wystaje 12 mm poza obrys panelu (panel kończy się na x = −80).

### D11. Numeracja płytek i kod
Numer n = A + 2·B + 4·C (bit = magnes obecny w narożniku A, B, C). Dołki kodu przy narożniku A: dołek 1 (bit A) y = −45, dołek 2 (bit B) y = −42, dołek 3 (bit C) y = −39, wszystkie x = −37, ø2 × 1 mm. Płytki wieczorne: nr 1, 2, 3; poranne: nr 4, 5, 6 (typ płytki wynika z numeru). 7 = rezerwa, 0 = brak płytki. Relief numeru (cyfra 5 mm wysoka, 0,6 mm) w narożniku D: środek (39,5, −44,5).

### D12. Wkładka w blacie: 2 kołki + 2 magnesy
Wkładka ma 2 tylne „uszy” 14 × 43,7 × 3 mm (od tylnej krawędzi ramy y = 52,3 do y = 96), środki x = ±58. W każdym uchu kołek ø3 × 3,5 w dół w (±58, 93,5) do otworu ø3,3 w blacie, magnes ø5 × 2 w otworze przelotowym ø5,4 w (±58, 86) naprzeciw magnesu w kieszeni blatu (bieguny przyciągające). Uszy zasłaniają po 14 × 28 mm tylnych narożników marginesu matrycy (dozwolone: w całości odsłonięte mają być pas przedni i prawy). Przewody Halla: rowek 1,5 × 1,5 na zewnętrznej dolnej krawędzi ramy (lewy, tylny, prawy bok), potem kanał 2 × 1,2 pod uchem, do szczeliny 4 × 8 w blacie w (±66, 90).

### D13. Panel i rama dyfuzora
Panel skręcony od dołu: dystans M3 męsko‑żeński 35 mm wkręcony w gwintowany otwór tyłu panelu, od spodu korpusu wkręt M3 × 8 przez otwór w dnie w wkładkę M3 w bossie 11 mm. Rama dyfuzora = kołnierz 170 × 170 zewn., 161 × 161 wewn., 6 mm wysoki, przykręcony 4 × M3 od dołu do bossów blatu; otacza PCB panelu (luz 0,5 na stronę), ustala panel względem okna i zamyka szczelinę świetlną i pyłową. Dyfuzor 160 × 160 × 2 leży w kieszeni blatu 162 × 162 × 2 na półce 2 mm (otwór przelotowy 158 × 158), licowany; dociskany magnesami wkładki.

### D14. Wentylacja i pył
Wlot: 2 szczeliny 20 × 3 w dnie pod Pi. Wylot: szczeliny 12 × 3 z daszkiem 2 mm (45°) nisko w ścianach: tylna 8 szt., boczne po 6 szt., oś na Z = 8. Stopki gumowe 4 mm. Gniazda w tylnej ściance: DC z nakrętką w kieszeni wgłębionej (Z27): otwór w ścianie 36 × 24 (x −78…−42, Z 14…38), za nim skrzynka 40 × 22 × 28 (ściany 2 mm, zamknięta od dołu i boków, otwarta tylko na zewnątrz) sięgająca do y = 78; gniazdo DC w dnie kieszeni (y = 78), oś (−60, Z 30), nakrętka od strony wnętrza obudowy; wtyk kątowy wchodzi w kieszeń, kabel wychodzi dołem otworu. Kieszeń mija boss panelu (−60, 60) o 13,5 mm, szczeliny wentylacyjne (Z ≤ 9,5) o 2,5 mm i boss uchwytu kabli (−40, 70) o 4,5 mm. USB‑A panelowe z zaślepką; żadnych odsłoniętych złącz Pi.

### D15. Głowica gestu i przycisk
Głowica 34 × 26 × 16 na przedniej ściance, środek x = −70, Z 30–46, górna płaszczyzna pochylona 15° ku użytkownikowi, okienko 8 × 6, 2 × M2,5 od wewnątrz korpusu, kabel I2C przez otwór ø4. Przycisk ø30 w przedniej ściance: środek (30, −100, 22) — na prawo od środka, nie przy samej krawędzi, bo walec kolizyjny ø34 × 40 za przyciskiem musi minąć boss panelu w (60, −60): odległość osi 30 ≥ 17 + 4,5 ✓; w porannej zaślepka zatrzaskowa. Napis na przedniej ściance: relief 0,6, wysokość liter 8, środek x = 0, Z = 46 (dolna krawędź liter 42 > wierzch kołnierza przycisku 38,5 ✓; napis ±43 w X kończy się przed głowicą od −53 ✓).

### D16. Nazwy plików
`ramka_plytka_wieczorna_v1.stl`, `ramka_plytka_poranna_v1.stl`, `ramka_pokrywka_v1.stl`, `ramka_korpus_W_v1.stl`, `ramka_korpus_P_v1.stl`, `ramka_blat_v1.stl`, `ramka_rama_dyfuzora_v1.stl`, `ramka_wkladka_v1.stl`, `ramka_glowica_v1.stl`, `ramka_zaslepka_v1.stl`, `ramka_uchwyt_kabli_v1.stl` (11 plików; podstawka klawiatury usunięta, Z26).

---
## 3. Tabela parametrów

Nazwy są stałymi na górze skryptu sesji 2. Źródło: `spec`, `Zn`, `Dn` albo `DO ZMIERZENIA` (wartość domyślna, podmienić po pomiarze).

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
| code_dimple_x | −37 | mm | D11 | x wszystkich dołków (układ płytki) |
| code_dimple_y0 | −45 | mm | D11 | y dołka bitu A |
| code_dimple_pitch | 3 | mm | D11 | odstęp y między dołkami |
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
| cover_vent_d | 4 | mm | D8 | otwory w wierzchu pokrywki (6 szt.) |
| cover_corner_r | 3 | mm | spec 4.1 | promień zewnętrznych pionowych krawędzi |

### 3.2 Panel, dyfuzor, Pi

| Parametr | Wartość | Jedn. | Źródło | Opis |
|---|---|---|---|---|
| panel_size | 160 | mm | spec | bok PCB panelu |
| panel_pcb_t | 1.6 | mm | spec | grubość PCB panelu |
| panel_led_h | 2 | mm | DO ZMIERZENIA | wysokość diod/maski nad PCB |
| panel_bottom_parts_h | 12 | mm | DO ZMIERZENIA | najniższy element spodu panelu poniżej PCB |
| panel_hole_pitch_x | 120 | mm | DO ZMIERZENIA | rozstaw otworów M3 panelu w X |
| panel_hole_pitch_y | 120 | mm | DO ZMIERZENIA | rozstaw otworów M3 panelu w Y |
| panel_hole_offset_x | 0 | mm | DO ZMIERZENIA | przesunięcie środka wzoru otworów od środka panelu |
| panel_hole_offset_y | 0 | mm | DO ZMIERZENIA | j.w. |
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
| pi_pos_x | −92 | mm | D10 | narożnik PCB Pi (krawędź SD, przód), X |
| pi_pos_y | −28 | mm | D10 | j.w., Y |
| pi_standoff_h | 5 | mm | D4 | boss Pi (drukowany, wkładka M2,5) |
| pi_stack_h | 26 | mm | DO ZMIERZENIA | spód PCB Pi → szczyt stosu z Bonnetem |
| pi_clearance_top | 3 | mm | D4 | luz nad stosem Pi |
| sd_slot_l | 16 | mm | Z14 | szczelina w dnie pod kartę (wzdłuż Y) |
| sd_slot_w | 10 | mm | Z14 | j.w. (wzdłuż X), środek x = −91, y = 0 |
| bonnet_dc_pos_x | −92 | mm | DO ZMIERZENIA | gniazdo DC Bonnetu (na którą ściankę patrzy) |
| bonnet_dc_pos_y | 0 | mm | DO ZMIERZENIA | j.w. |

### 3.3 Korpus

| Parametr | Wartość | Jedn. | Źródło | Opis |
|---|---|---|---|---|
| box_outer | 200 | mm | spec | bok zewnętrzny |
| wall_t | 2.5 | mm | spec 4.1 | grubość ścian |
| floor_t | 3 | mm | spec 4.1 | grubość dna |
| box_corner_r | 5 | mm | spec | promień pionowych krawędzi |
| box_edge_r | 3 | mm | spec | promień dolnej krawędzi |
| korpus_h | 54.6 | mm | D4 | wysokość korpusu bez blatu (liczona) |
| blat_top_z | 58.6 | mm | D4 | wierzch blatu (liczony) |
| panel_pcb_z | 49 | mm | D4 | spód PCB panelu (liczony) |
| panel_boss_h | 11 | mm | D4 | boss panelu w dnie, ø9, wkładka M3 |
| panel_standoff_l | 35 | mm | D4 | dystans mosiężny M3 męsko‑żeński |
| insert_hole_m3 | 4.0 | mm | spec 4.8 | otwór pod wkładkę M3 |
| insert_hole_m25 | 3.4 | mm | spec 4.8 | otwór pod wkładkę M2,5 |
| insert_depth_m3 | 6 | mm | D | głębokość otworu pod wkładkę M3 |
| insert_depth_m25 | 5 | mm | D | głębokość otworu pod wkładkę M2,5 |
| vent_slot_w | 12 | mm | D14 | szczelina wylotowa |
| vent_slot_h | 3 | mm | D14 | j.w. |
| vent_slot_z | 8 | mm | D14 | oś szczelin nad dnem zewnętrznym |
| vent_slots_rear | 8 | szt. | D14 | rozstaw 18 mm, symetrycznie względem x = 0 |
| vent_slots_side | 6 | szt. | D14 | rozstaw 18 mm, symetrycznie względem y = 0 |
| vent_hood_l | 2 | mm | D14 | wysięg daszka |
| vent_hood_t | 1.5 | mm | D14 | grubość daszka |
| floor_vent_l | 20 | mm | D14 | szczelina wlotowa w dnie (2 szt., y = ±10, x = −60) |
| floor_vent_w | 3 | mm | D14 | j.w. |
| foot_d | 10 | mm | zakup | stopka gumowa |
| foot_h | 4 | mm | spec | stopka gumowa |
| foot_pocket_depth | 0.5 | mm | D | płytkie gniazdo stopki, środek 12 mm od krawędzi |
| dc_hole_d | 12 | mm | DO ZMIERZENIA | otwór gniazda DC (8 albo 12) |
| dc_pos_x | −60 | mm | D | tylna ścianka |
| dc_pos_z | 30 | mm | Z27 | oś gniazda w dnie kieszeni |
| dc_pocket_w | 36 | mm | Z27 | otwór kieszeni w tylnej ścianie (X) |
| dc_pocket_h | 24 | mm | Z27 | otwór kieszeni (Z), dolna krawędź Z 14 |
| dc_pocket_depth | 22 | mm | Z27 | głębokość kieszeni od lica ściany (do y = 78) |
| dc_pocket_wall | 2 | mm | Z27 | ścianki skrzynki kieszeni |
| usb_cut_w | 15 | mm | DO ZMIERZENIA | okno gniazda USB‑A panelowego |
| usb_cut_h | 8 | mm | DO ZMIERZENIA | j.w. |
| usb_hole_pitch | 22 | mm | DO ZMIERZENIA | rozstaw 2 × ø3,2 flanszy USB |
| usb_pos_x | 50 | mm | D | tylna ścianka |
| usb_pos_z | 24 | mm | D | j.w. |
| button_hole_d | 30 | mm | DO ZMIERZENIA | otwór przycisku (30 albo 24) |
| button_pos_x | 30 | mm | D15 | przednia ścianka |
| button_pos_z | 22 | mm | D15 | j.w. |
| button_body_d | 34 | mm | D | strefa kolizji za przyciskiem, walec |
| button_body_depth | 40 | mm | D | j.w., w głąb od ścianki |
| head_pos_x | −70 | mm | D15 | środek głowicy na przedniej ściance |
| head_pos_z | 38 | mm | D15 | środek głowicy |
| head_screw_pitch | 24 | mm | D15 | 2 × M2,5 w przedniej ściance: x = −82 i −58, Z = 38 |
| head_cable_hole_d | 4 | mm | D15 | otwór kabla I2C, (−70, Z 38) |
| label_text_h | 8 | mm | D15 | wysokość liter napisu |
| label_relief_h | 0.6 | mm | spec | relief napisu |
| label_pos_z | 46 | mm | D15 | środek napisu, x = 0 |
| snap_pocket_w | 10 | mm | D9 | ślepa kieszeń zatrzasku w ścianie |
| snap_pocket_h | 2.5 | mm | D9 | j.w. |
| snap_pocket_depth | 1.2 | mm | D9 | j.w., od wewnątrz |
| snap_pocket_z | 47.6 | mm | D9 | dolna krawędź kieszeni |
| blat_screw_pitch | 120 | mm | D9 | 2 × M3 w tylnej ściance, x = ±60 |
| blat_screw_z | 50 | mm | D9 | j.w. |
| cable_holder_pos | 60 | mm | D | 2 bossy M3 ø7 × 5: (40, 70) i (−40, 70) |

### 3.4 Blat, rama dyfuzora, wkładka

| Parametr | Wartość | Jedn. | Źródło | Opis |
|---|---|---|---|---|
| blat_t | 4 | mm | D9 | grubość płyty blatu |
| blat_skirt_h | 10 | mm | D9 | kołnierz pod blatem |
| blat_skirt_t | 2 | mm | D9 | grubość kołnierza |
| blat_skirt_clearance | 0.3 | mm | spec 4.8 | luz kołnierz–ściana na stronę |
| blat_corner_r | 5 | mm | spec | jak korpus |
| snap_hook_w | 8 | mm | D9 | haczyk zatrzasku |
| snap_hook_h | 1.2 | mm | D9 | występ haczyka |
| snap_hook_t | 1.5 | mm | D9 | grubość ramienia |
| rama_outer | 170 | mm | D13 | rama dyfuzora, bok zewnętrzny |
| rama_inner | 161 | mm | D13 | bok wewnętrzny (panel + 1) |
| rama_h | 6 | mm | D13 | wysokość |
| rama_screw_pos | 86 | mm | D13 | 4 × M3 w (±86, ±86), uszy ø8 |
| rama_boss_h | 6 | mm | D13 | boss M3 pod blatem |
| insert_opening | 96.6 | mm | spec | otwór wkładki |
| insert_wall_w | 4 | mm | spec | szerokość ramy |
| insert_h | 6 | mm | Z7 | wysokość ramy |
| insert_shelf | 12 | mm | D5 | bok półki narożnej |
| insert_shelf_h | 2.5 | mm | D5 | grubość półki |
| hall_pocket_w | 5.0 | mm | D5 | kieszeń TO‑92 (X) |
| hall_pocket_l | 5.5 | mm | D5 | kieszeń TO‑92 (Y), przelotowa |
| hall_lead_channel_w | 2.5 | mm | D5 | kanał wyprowadzeń pod półką |
| hall_lead_channel_h | 1.2 | mm | D5 | j.w. |
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
| blat_pin_hole_d | 3.3 | mm | D12 | otwór kołka w blacie, przelotowy |
| blat_magnet_pocket_d | 5.4 | mm | D12 | kieszeń magnesu w blacie, od góry |
| blat_magnet_pocket_depth | 2.3 | mm | D12 | j.w. |
| wire_slot_l | 8 | mm | D12 | szczelina kabla Halla w blacie (Y) |
| wire_slot_w | 4 | mm | D12 | j.w. (X), środek (±66, 90) |
| wire_rabbet | 1.5 | mm | D12 | rowek na kable, zewn. dolna krawędź ramy |

### 3.5 Głowica, zaślepka, uchwyt kabli, odbiornik

| Parametr | Wartość | Jedn. | Źródło | Opis |
|---|---|---|---|---|
| head_w | 34 | mm | D15 | głowica, X |
| head_d | 26 | mm | D15 | głowica, Y (wysięg przed ścianką) |
| head_h | 16 | mm | D15 | głowica, Z |
| head_tilt | 15 | ° | spec | pochylenie górnej płaszczyzny ku przodowi |
| head_window_w | 8 | mm | spec | okienko |
| head_window_h | 6 | mm | spec | okienko |
| head_wall_t | 1.5 | mm | spec 4.8 | ścianki głowicy |
| tof_pcb_w | 25 | mm | DO ZMIERZENIA | moduł VL53L1X |
| tof_pcb_l | 18 | mm | DO ZMIERZENIA | j.w. |
| tof_pcb_t | 4 | mm | DO ZMIERZENIA | j.w. z elementami |
| plug_flange_d | 34 | mm | D15 | zaślepka, kołnierz |
| plug_flange_t | 2.5 | mm | D15 | j.w. |
| plug_body_d | 29.5 | mm | D15 | korpus zaślepki w otworze ø30 |
| plug_body_l | 4 | mm | D15 | j.w. |
| plug_hook_h | 1.0 | mm | D15 | 2 haczyki za ścianką 2,5 |
| holder_l | 40 | mm | D | uchwyt kabli / płytki proto |
| holder_w | 20 | mm | D | j.w. |
| holder_h | 12 | mm | D | j.w. |
| holder_slot_w | 4 | mm | D | 3 szczeliny na wiązki kabli |
| proto_board_l | 30 | mm | zakup | płytka prototypowa Halla |
| proto_board_w | 20 | mm | zakup | j.w., grubość 1,6 → rowek 1,8 |
| receiver_l | 19 | mm | DO ZMIERZENIA | odbiornik USB nano |
| receiver_w | 15 | mm | DO ZMIERZENIA | j.w. |
| receiver_h | 6 | mm | DO ZMIERZENIA | j.w. |

---
## 4. Specyfikacja części do zamówienia

Układ współrzędnych: jak w D3 (globalny; płytki i pokrywka w układzie lokalnym płytki). Każda część modelowana w położeniu montażowym, a przed eksportem przesunięta tak, by największa płaska ściana leżała na Z = 0. Wszystkie luzy ruchome 0,3 mm na stronę, wciskane 0,15 mm, zapas na chropowatość SLS 0,3 mm wliczony w podane otwory.

### 4.1 `ramka_plytka_wieczorna_v1.stl` i `ramka_plytka_poranna_v1.stl`
- Funkcja: nośnik prac do skanera i do ramki; wspólna geometria, różne gniazda.
- Gabaryt: `plate_size` × `plate_size` × `plate_thickness` = 96 × 96 × 8; pionowe krawędzie R 1, górne krawędzie faza 0,5.
- Cechy wspólne (układ lokalny, wierzch płytki Z = 0, materiał w dół do Z = −8):
  1. Gniazda stożkowe: wierzch ø d, dno ø d − 2·4·tan15° = d − 2,14, głębokość 4, otwór ø3 przelotowy w osi. Pozycje: D6.
  2. Rynienki: obrys z zaokrąglonymi końcami (stadion) l × w, ścianki 15°, głębokość 4, 4 otwory ø3 na osi w rozstawie `ev_/mo_trough_hole_pitch`, symetrycznie względem środka rynienki. Pozycje: D6.
  3. Stożki znaczników ø5 × 3 (wierzchołek w dół) w A (−42, −42), B (−42, 42), C (42, 42).
  4. Wycięcie 5 × 5 przelotowe w D: x ∈ [43, 48], y ∈ [−48, −43].
  5. Dołki kodu ø2 × 1: (−37, −45), (−37, −42), (−37, −39); w STL wszystkie 3 wycięte (kod widzi skaner po dołkach, które są — sesja 2 generuje 6 wariantów płytek: `..._wieczorna_n1..n3`, `..._poranna_n4..n6`, z dołkami tylko dla bitów = 1 i właściwą cyfrą reliefu; plik bazowy bez numeru zostaje jako `_v1`).
  6. Kieszenie magnesów od spodu ø5,2 × 2,2, współosiowe ze znacznikami A, B, C (Z4). Wszystkie 3 kieszenie w każdej płytce (magnes wklejony lub nie).
  7. Numer: relief 0,6, cyfra 5 mm, środek (39,5, −44,5), font bezszeryfowy pogrubiony.
  8. Rowek pokrywki 1,0 wysoki × 0,8 głęboki wokół 4 boków, środek 2 mm pod wierzchem; przerwany w wycięciu D.
- Luzy: płytka w otworze wkładki 96,6 → 0,3 na stronę; wycięcie 5 × 5 na kołek 4,4 → 0,3.
- Łączy się z: wkładka (półki, kołek), pokrywka (rowek), magnesy, skaner.
- Orientacja do druku: gniazdami do góry, spód płaski na stole.
- Ilość: 3 + 3. Materiał: PA12 naturalny biały, mat, bez wygładzania. Alternatywa: SLA półprzezroczysta (wieczorna), CNC PMMA opal (poranna; wtedy STEP przez FreeCAD).
- Plik JSON obok każdej płytki (`plytka_wieczorna_gniazda.json`, `plytka_poranna_gniazda.json`): `{"plate":"wieczorna","size":96,"origin":"center_top","sockets":[{"id":1,"type":"round","d":9,"x":-30,"y":-40.5},…,{"id":25,"type":"trough","l":60,"w":15,"x":0,"y":19.5},{"id":26,"type":"trough","l":60,"w":15,"x":0,"y":37.5}],"leds":{}}` (id rzędami od przodu, od lewej); `leds` wypełnia kalibracja (sekcja 9).

### 4.2 `ramka_pokrywka_v1.stl`
- Funkcja: osłona prac na czas przenoszenia; jedna na obie płytki.
- Gabaryt: (96 + 2·0,3 + 2·1,5) = 99,6 × 99,6 × (14 + 2 + 4) = 20 mm; pionowe krawędzie R 3.
- Cechy: wnęka 96,6 × 96,6 × 18 (od dołu), wierzch 2 mm; kołnierz 1,5 mm; 4 garby zatrzaskowe 10 × 0,7 (promień zaokrąglenia 0,5) na wewnętrznej stronie kołnierza, środek boku, 2 mm nad dolną krawędzią kołnierza (trafiają w rowek płytki przy kołnierzu schodzącym 4 mm pod wierzch płytki); 6 otworów ø4 w wierzchu (siatka 2 × 3, rozstaw 30); wycięcie 30 × 3 na palec na dolnej krawędzi przedniego i tylnego boku; napis „GÓRA” relief 0,6 na wierzchu.
- Luzy: 0,3 na stronę do płytki; garb 0,7 w rowek 0,8.
- Rachunek wysokości: wierzch płytki 0 → najwyższa praca +10 (14 − 4) → prześwit 4 → spód wierzchu pokrywki +14 ✓.
- Orientacja: wierzchem w dół (największa płaska ściana). Ilość 4. PA12 naturalny.

### 4.3 `ramka_korpus_W_v1.stl`, `ramka_korpus_P_v1.stl`
- Funkcja: dno i ściany; niesie panel, Pi, gniazda, głowicę/przycisk. Dwa pliki różnią się tylko napisem.
- Gabaryt: 200 × 200 × 54,6; ściany 2,5, dno 3, R 5 pionowe, R 3 dolna krawędź. Wnętrze 195 × 195.
- Cechy (globalne XYZ):
  1. 4 bossy panelu ø9 × 11 na dnie, oś w (±60, ±60) (`panel_hole_pitch`/2), otwór ø4,0 × 6 pod wkładkę M3 od góry; w dnie pod każdym bossem otwór ø3,4 przelotowy z pogłębieniem ø6,5 × 2 od spodu.
  2. 4 bossy Pi ø6 × 5 na dnie, osie: (−88,5, −24,5), (−30,5, −24,5), (−88,5, 24,5), (−30,5, 24,5); otwór ø3,4 × 5 pod wkładkę M2,5.
  3. Szczelina SD w dnie 10 (X) × 16 (Y), środek (−91, 0), krawędzie zaokrąglone R 2.
  4. 2 szczeliny wlotowe w dnie 20 × 3, środki (−60, ±10).
  5. Szczeliny wylotowe 12 × 3 z daszkiem: tylna ścianka 8 szt., środki x = −63, −45, −27, −9, 9, 27, 45, 63, Z = 8; lewa i prawa ścianka po 6 szt., y = −45, −27, −9, 9, 27, 45, Z = 8. Daszek: półka 1,5 gruba, wysięg 2, nad górną krawędzią szczeliny, pochylona 45° w dół.
  6. Tylna ścianka: kieszeń DC — otwór 36 × 24 (x −78…−42, Z 14…38, naroża R 3) i skrzynka za nim: zewnętrznie x −80…−40, y 78…100, Z 12…40, ściany 2, wnętrze otwarte tylko przez otwór w ścianie; w dnie skrzynki (płaszczyzna y = 78) otwór gniazda DC ø12 w (−60, Z 30); okno USB 15 × 8 w (50, Z 24) + 2 otwory ø3,2 w (50 ± 11, Z 24); 2 otwory ø3,2 z pogłębieniem stożkowym pod wkręt M3 w (±60, Z 50) (wkręty blatu).
  7. Przednia ścianka: otwór przycisku ø30 w (30, Z 22); 2 otwory ø2,8 w (−82, Z 38) i (−58, Z 38) oraz otwór kabla ø4 w (−70, Z 38) (głowica); napis relief 0,6 „RAMKA WIECZORNA” (W) / „RAMKA PORANNA” (P), litery 8 mm, środek (0, Z 46).
  8. Kieszenie zatrzasków blatu: 4 szt., 10 × 2,5 × 1,2 od wewnątrz, dolna krawędź Z 47,6, środek każdego boku (x = 0 dla przedniej/tylnej, y = 0 dla bocznych).
  9. 2 bossy uchwytów kabli ø7 × 5, wkładka M3, w (40, 70) i (−40, 70).
  10. 4 gniazda stopek ø10,5 × 0,5 od spodu, środki 12 mm od krawędzi.
  11. Żebra: 4 żebra 2 × 6 mm na dnie od bossów panelu do ścian (po przekątnych), przerwane przy Pi.
- Strefa kolizji przycisku: walec ø34, oś (30, Z 22), od y = −100 do −60 (Z 5–39). Boss panelu (60, −60) ø9: odległość osi w X = 30 ≥ 17 + 4,5 = 21,5 ✓ (8,5 mm zapasu). Pi (x ≤ −7, y ≥ −28) ✓. Głowica x ≤ −53 ✓. Sesja 2 po wpisaniu zmierzonego `panel_hole_pitch` powtarza ten test; jeśli zapas < 3 mm, przesuwa `button_pos_x` ku x = 0.
- Orientacja: dnem w dół. Ilość: 1 W + 1 P. PA12 grafit. Powierzchnie zewnętrzne pod wygładzanie (wariant pokazowy).

### 4.4 `ramka_blat_v1.stl`
- Funkcja: górna płyta z oknem i kieszenią dyfuzora, nosi ramę dyfuzora i wkładkę.
- Gabaryt: 200 × 200 × 4 + kołnierz 10 w dół = 14; R 5 pionowe, R 1,5 górna krawędź.
- Cechy:
  1. Kieszeń dyfuzora 162 × 162 × 2 od góry (środek 0,0), otwór przelotowy 158 × 158; naroża kieszeni R 1 (pleksi cięta na ostro → sfazować rogi pleksi 1 mm).
  2. Kołnierz: obrys 194,4 × 194,4 (195 − 2·0,3), grubość 2, wysokość 10, R 4,7; 4 haczyki zatrzaskowe 8 szerokie, występ 1,2, grubość ramienia 1,5, na środkach boków, krawędź haczyka 1 mm nad dolną krawędzią kołnierza; nacięcia 1 mm po obu stronach każdego haczyka (sprężyste ramię 12 mm).
  3. 2 słupki 6 × 6 × 10 na wewnętrznej stronie tylnego kołnierza w x = ±60, otwór ø4,0 × 6 pod wkładkę M3 poziomo (oś Y), oś Z 50.
  4. 4 bossy ø8 × 6 pod spodem w (±86, ±86), otwór ø4,0 × 6 pod wkładkę M3 (rama dyfuzora).
  5. Otwory kołków wkładki ø3,3 przelotowe w (±58, 93,5); kieszenie magnesów ø5,4 × 2,3 od góry w (±58, 86); szczeliny kabli 4 × 8 w (±66, 90).
  6. Żebro obwodowe 2 × 6 pod spodem wokół kieszeni, 2 mm na zewnątrz od jej krawędzi (obwód 166 × 166), przerwane przy szczelinach kabli i bossach ramy.
- Rachunek „wkładka w oknie blatu”: rama wkładki 104,6 × 104,6 leży na dyfuzorze 160 → margines 27,7 mm wolnego dyfuzora z każdej strony; uszy sięgają y = 96 < 97,2 (wewnętrzna krawędź kołnierza) ✓.
- Łączy się z: korpus (kieszenie zatrzasków, wkręty tylne), rama dyfuzora (bossy), dyfuzor (kieszeń), wkładka (kołki, magnesy, szczeliny).
- Orientacja: wierzchem w dół. Ilość 2. PA12 grafit.

### 4.5 `ramka_rama_dyfuzora_v1.stl`
- Funkcja: kołnierz ustalający panel względem okna; uszczelnienie świetlne i pyłowe między panelem a blatem.
- Gabaryt: 170 × 170 × 6, ścianka 4,5 (zewn. 170, wewn. 161), 4 uszy narożne ø8 × 6 wokół otworów ø3,4 w (±86, ±86), połączone z ramą mostkiem 4 mm.
- Luz: 0,5 na stronę do PCB panelu 160.
- Łączy się z: blat (4 × M3 × 8 od dołu), panel (otacza PCB, Z 48,6–54,6).
- Rachunek: dół ramy Z 48,6 < spód PCB panelu 49 → rama obejmuje całą grubość PCB ✓; nie dotyka diod (lico Z 52,6, rama wewnątrz 161 > 160).
- Orientacja: płasko. Ilość 2. PA12 grafit.

### 4.6 `ramka_wkladka_v1.stl`
- Funkcja: gniazdo płytki, nośnik 3 czujników Halla i kołka orientacji.
- Gabaryt: rama 104,6 × 104,6 × 6 + 2 uszy do y = 96 (obrys 104,6 × 148,3), Z lokalne: spód 0 (na dyfuzorze).
- Cechy:
  1. Otwór 96,6 × 96,6, naroża wewnętrzne R 0,5; ścianka 4 szeroka, 6 wysoka, górna krawędź wewnętrzna faza 1 × 45° (naprowadzenie płytki).
  2. 4 półki narożne 12 × 12 × 2,5 wewnątrz otworu (naroża A, B, C, D), górna powierzchnia Z 2,5.
  3. Półki A, B, C: kieszeń przelotowa 5,0 × 5,5 (X × Y), środek pod osią magnesu płytki: A (−42, −42), B (−42, 42), C (42, 42); kanał 2,5 × 1,2 od kieszeni do ścianki ramy po przekątnej narożnika, pod półką (otwarty od dołu); w ściance ramy przelot 2,5 × 1,5 do rowka zewnętrznego.
  4. Półka D (42, −42): kołek 4,4 × 4,4 × 5 (nad półką), ścianki zewnętrzne kołka 0,5 od ścian otworu; wierzchołek sfazowany 1 mm.
  5. Wycięcie palcowe 30 × pełna wysokość w przednim boku ramy (x ∈ [−15, 15], y = −48,3 … −52,3).
  6. Rowek kablowy 1,5 × 1,5 na zewnętrznej dolnej krawędzi lewego, tylnego i prawego boku (od A do ucha lewego; od C do ucha prawego; B wprost do ucha lewego).
  7. Uszy: 14 × 43,7 × 3, od y = 52,3 do 96, środki x = ±58; kołek ø3 × 3,5 w dół w (±58, 93,5), faza 0,5; otwór ø5,4 przelotowy w (±58, 86); kanał kablowy 2 × 1,2 pod uchem wzdłuż zewnętrznej krawędzi (x = ±64) od y = 52,3 do 90, wylot na krawędzi zewnętrznej ucha nad szczeliną blatu (±66, 90).
  8. Napis relief 0,6 „PRZÓD” 4 mm na górnej powierzchni przedniego boku; strzałka.
- Luzy i rachunek „płytka we wkładce”: 96 + 2·0,3 = 96,6 ✓; powtarzalność ±0,3 (luz) + kołek 4,4 w 5 (±0,3) → ±0,5 wymagane ✓ (kołek dociska płytkę do narożnika D przy ułożeniu).
- Magnes–czujnik: D5, 1,7 mm ≤ 4 ✓.
- Orientacja: spodem w dół. Ilość 2 + 1 zapas. PA12 naturalny biały.

### 4.7 `ramka_glowica_v1.stl`
- Funkcja: obudowa VL53L1X na przedniej ściance ramki wieczornej.
- Gabaryt: 34 (X) × 26 (Y, przed ścianką) × 16 (Z), pochylona górna płaszczyzna 15° (przód niżej), R 3 pionowe. Tylna płaszczyzna płaska, przylega do przedniej ścianki korpusu; środek (−70, −100, 38).
- Cechy: wnęka 31 × 23 × 13 otwarta od tyłu (strona ścianki); 2 słupki ø5 × 4 z otworem ø2,2 na śruby modułu (rozstaw wg modułu, domyślnie 20 × 0 — DO ZMIERZENIA); okienko 8 × 6 w górnej płaszczyźnie, środek nad czujnikiem (domyślnie środek płaszczyzny); 2 bossy ø6 w tylnej płaszczyźnie z otworami ø3,4 × 5 pod wkładki M2,5 w (−82, 38) i (−58, 38); otwór kablowy wspólny ze ścianką.
- Orientacja: tylną płaszczyzną w dół. Ilość 1. PA12 grafit.

### 4.8 `ramka_zaslepka_v1.stl`
- Funkcja: zaślepia otwór przycisku w ramce porannej.
- Gabaryt: kołnierz ø34 × 2,5 (zewnętrzna krawędź R 1), korpus ø29,5 × 4, 2 haczyki 6 szerokie, występ 1,0, 2,5 za kołnierzem + 0,3 (łapią za ścianką 2,5); nacięcia 2 × 8 obok haczyków.
- Orientacja: kołnierzem w dół. Ilość 1. PA12 grafit.

### 4.9 `ramka_uchwyt_kabli_v1.stl`
- Funkcja: trzyma płytkę prototypową Halla i wiązki kabli przy dnie.
- Gabaryt: 40 × 20 × 12; stopa 40 × 20 × 2,5 z otworem ø3,4 (wkręt M3 do bossa); rowek 1,8 × 4 głęboki na płytkę proto 30 × 20 (pionowo); 3 szczeliny 4 × 8 w grzebieniu 1,5 grubym na opaski kablowe.
- Orientacja: stopą w dół. Ilość 2. PA12 naturalny.

### 4.10 Podstawka klawiatury — usunięta (Z26)
Klawiatura leży luzem na stole. Brak pliku, brak nalepki.

---
### 4.11 Rachunki spójności — zbiorczo
| Sprawdzenie | Rachunek | Wynik |
|---|---|---|
| Łańcuch wysokości | 3 + 5 + 26 + 3 + 12 = 49 (spód PCB panelu); + 1,6 + 2 + 4 + 2 = 58,6 (wierzch blatu); korpus 58,6 − 4 = 54,6 | mieści się w 55–60 ✓ |
| Panel na słupkach | 3 (dno) + 11 (boss) + 35 (dystans) = 49 = `panel_pcb_z` | ✓ |
| Płytka we wkładce | 96 + 2 × 0,3 = 96,6; wycięcie 5 vs kołek 4,4 + 2 × 0,3 = 5,0 | ✓ (powtarzalność ±0,3 < ±0,5) |
| Wkładka w oknie blatu | rama 104,6 < dyfuzor 160; uszy do y = 96 < wnętrze kołnierza 97,2; kołki i magnesy na litym blacie (y 86–93,5, poza kieszenią 81) | ✓ |
| Magnes–czujnik | 0,2 + 1,0 + 0,5 = 1,7 ≤ 4 | ✓ |
| Odsłonięty margines | 32 − 0,3 − 4 = 27,7 mm = 11 pełnych pikseli; przód i prawy bok bez uszu | ✓ |
| Pokrywka nad pracą | 14 − 4 + 4 = 14 mm prześwitu nad płytką | ✓ |
| Zasady 4.8: ścianki | najcieńsze: kołnierz pokrywki 1,5; ramię zatrzasku 1,5; ścianki głowicy 1,5; skin nad kanałem w półce 2,5 − 1,2 = 1,3 (lokalnie, nad kanałem 2,5 mm szerokim — akceptowalne, sesja 2 może dać 1,5 zmniejszając kanał do 1,0) | ✓ / uwaga |
| Zasady 4.8: otwory | najmniejszy ø2 (dołki kodu) ≥ 1,5 | ✓ |
| Zasady 4.8: relief | 0,6 | ✓ |
| Zasady 4.8: luzy | ruchome 0,3 (płytka, kołnierz blatu, pokrywka), wciskane 0,15 (kołek ø3 w ø3,3 → 0,15/stronę), magnesy 0,1–0,2 | ✓ |
| Zasady 4.8: pustki | korpus, blat, pokrywka, głowica otwarte; kieszenie magnesów i kanały kabli otwarte od spodu | ✓ |
| Zasady 4.8: wkładki gwintowane | ø4,0 pod M3, ø3,4 pod M2,5 | ✓ |
| Gniazda wieczornej | 6 rzędów: 9+9+12+15+15+15 + 5 × 3 = 90; najszerszy rząd 87/90; rzędy skrajne 69 i 60 ≤ 70 | ✓ |
| Gniazda porannej | 7 rzędów: 7,5×3+10+12,5+13+13 + 6 × 3 = 89 ≤ 90; najszerszy rząd 90/90; rzędy skrajne 60 i 50 ≤ 70 | ✓ |
| Kieszeń DC w korpusie | skrzynka x −80…−40, y 78…100, Z 12…40: boss panelu (−60, 60) ø9 → y ≤ 64,5 (13,5 zapasu); szczeliny wentylacyjne Z ≤ 9,5 (2,5 zapasu); boss uchwytu (−40, 70) ø7 → y ≤ 73,5 (4,5 zapasu); kołnierz blatu od Z 44,6 (4,6 zapasu) | ✓ |

---
## 5. Lista zakupów (na 2 ramki; ceny orientacyjne, Z22)

| Element | Model / kluczowe parametry | Ilość | Cena ok. [zł] | Gdzie |
|---|---|---|---|---|
| Panel HUB75 64 × 64 P2.5 | 160 × 160, 1/32 scan, 5 V, złącze zasilania VH4 + kabel, kabel HUB75 16‑pin w zestawie | 2 | 90–130/szt. | Botland, Kamami, AliExpress (Waveshare „RGB‑Matrix‑P2.5‑64x64”) |
| Raspberry Pi 4 B 2 GB | + radiator aluminiowy 3‑częściowy | 2 | 230–280/szt. | Botland, Kamami |
| Adafruit RGB Matrix Bonnet | ADA 3211; alternatywa RGB Matrix HAT + RTC (ADA 2345) | 2 | 90–130/szt. | Botland, Kamami, Pimoroni |
| Zasilacz 5 V 4 A | wtyk DC 5,5/2,1, wtyczka EU | 2 | 35–50/szt. | Botland |
| Gniazdo DC panelowe 5,5/2,1 | z nakrętką, otwór ø12 (lub ø8 — zmierzyć); montaż w dnie kieszeni 36 × 24 × 22 | 2 | 5/szt. | Botland |
| Wtyk kątowy DC 5,5/2,1 | zasilacz z wtykiem kątowym 90° albo przejściówka kątowa (wtyk prosty nie mieści się w kieszeni) | 2 | 5–10/szt. | Botland, Allegro |
| Wtyk DC 5,5/2,1 ze śrubkami | do kabla gniazdo → Bonnet | 2 | 4/szt. | Botland |
| microSD 32 GB A1 | SanDisk / Samsung EVO | 2 | 25/szt. | dowolny |
| Pleksi mleczna 2 mm 160 × 160 | PMMA opal 2 mm, cięcie na wymiar | 2 (+1) | 10–20/szt. | plexi.pl, Allegro |
| Klawiatura numeryczna 2,4 GHz | odbiornik USB nano, NIE Bluetooth‑only; np. Logitech / Natec / Genesis | 1 | 60–120 | Allegro, x‑kom |
| Gniazdo USB‑A panelowe | USB 3.0/2.0 panel‑mount, flansza 2 × M3, kabel 30 cm do USB‑A męskiego, z zaślepką | 2 | 15–25/szt. | Botland, AliExpress |
| VL53L1X moduł | Pololu 3415 lub Adafruit 3967 (I2C, 3,3 V) | 1 (+1) | 30–45 | Botland, Kamami |
| Przycisk arkadowy ø30 LED | podświetlenie 5 V, z mikroprzełącznikiem; otwór ø30 (zmierzyć) | 1 | 15–25 | Botland, Allegro |
| Czujniki Halla A3144 | TO‑92; alternatywnie SS451A / DRV5032 (D7) | 10 (6 + zapas) | 1–3/szt. | Botland, AliExpress |
| Rezystory 10 kΩ 1/4 W | podciąganie Halla, przycisk | 10 | 1 | Botland |
| Tranzystor 2N2222 + rezystory 1 kΩ, 100 Ω | sterowanie LED przycisku | 2 + 2 | 3 | Botland |
| Magnesy neodymowe ø5 × 2 N35 | paczka 30 szt. (potrzeba 9 w płytkach + 4 wkładki + 4 blaty = 17) | 30 | 15 | Allegro, AliExpress |
| Wkładki gwintowane M3 (ø4 × 5,7) | mosiężne do wtapiania | 30 | 20 | Botland, Allegro |
| Wkładki gwintowane M2,5 (ø3,5 × 4) | j.w. | 15 | 15 | j.w. |
| Dystanse mosiężne M3 męsko‑żeńskie 35 mm | panel; jeśli zmierzona `panel_bottom_parts_h` da inną długość — dobrać (30/35/40) | 8 | 25 | Botland, Allegro |
| Wkręty M3 × 8 łeb stożkowy (blat tył) i M3 × 8 łeb walcowy (panel, rama, uchwyty) | stal czarna | 40 | 15 | Allegro |
| Śruby M2,5 × 6 (Pi, głowica) | | 16 | 8 | Allegro |
| Listwa kątowa goldpin 1 × 10 | do wyprowadzenia GPIO z Bonnetu (Z12) | 2 | 2 | Botland |
| Płytka prototypowa 30 × 20 (pads) | Halla + rezystory | 2 | 4 | Botland |
| Złącza JST‑XH 2,54: 5‑pin, 4‑pin, 3‑pin + przewody Dupont F‑F 20 cm | | komplet | 25 | Botland |
| Przewód silikonowy AWG 28, 3 kolory | do czujników Halla (po 50 cm × 3 na czujnik) | 3 × 5 m | 20 | Botland |
| Przewód 2 × 1 mm² 30 cm | DC gniazdo → Bonnet | 1 m | 5 | |
| Stopki gumowe ø10 × 4 samoprzylepne | | 12 | 8 | Allegro |
| Opaski kablowe 2,5 × 100, rzep 20 mm | | komplet | 10 | |
| Klej CA (cyjanoakrylowy) żelowy | magnesy, czujniki Halla | 1 | 10 | |
| Przedłużacz USB 20 cm (opcja) | gdyby odbiornik klawiatury słabo odbierał w obudowie | 1 | 8 | |

Razem elektronika i drobne: ok. 1 250–1 750 zł.

---

## 6. Narzędzia

Lutownica z regulacją temperatury + grot do wkładek M3/M2,5 (zestaw grotów „insert tips”); cyna 0,8; trzecia ręka; multimetr; wkrętaki PH1, PH0, torx T10; klucz płaski 14 (nakrętka DC) i klucz do nakrętki przycisku (zwykle 32 — szczypce z osłoną); szczypce boczne; pęseta; papier 400; wiertła ø3,4 i ø5,5 (ewentualne poprawki otworów); pilnik igłowy; klej CA żelowy; marker; kompas lub magnes wzorcowy (bieguny); suwmiarka; laptop z czytnikiem SD; stacja do flashowania (Raspberry Pi Imager); mała wiertarka/dremel tylko do poprawek.

---

## 7. Struktura wewnętrzna obudowy (wariant wysoki)

Wszystkie pozycje globalne XY, Z od zewnętrznego dna.

| Element | Położenie | Wymiar | Wkładka |
|---|---|---|---|
| Bossy panelu (4) | (±60, ±60) — podmienić po pomiarze | ø9 × 11, otwór ø4,0 × 6 | M3 |
| Dystanse panelu (4) | na bossach | M3 M‑F 35 mm | — |
| Bossy Pi (4) | (−88,5, ±24,5), (−30,5, ±24,5) | ø6 × 5, otwór ø3,4 × 5 | M2,5 |
| Bossy uchwytów kabli (2) | (40, 70), (−40, 70) | ø7 × 5, otwór ø4,0 × 5 | M3 |
| Słupki blatu (2, w kołnierzu blatu) | (±60, 95,2), oś Z 50 | 6 × 6 × 10, otwór poziomy ø4,0 × 6 | M3 |
| Bossy ramy dyfuzora (4, pod blatem) | (±86, ±86) | ø8 × 6, otwór ø4,0 × 6 | M3 |
| Bossy głowicy (2, w głowicy) | (−82, 38), (−58, 38) | ø6, otwór ø3,4 × 5 | M2,5 |
| Kieszenie zatrzasków blatu (4) | środki boków, Z 47,6–50,1 | 10 × 2,5 × 1,2 | — |

Prowadzenie kabli:
1. Zasilanie: gniazdo DC w dnie kieszeni tylnej ścianki (−60, y 78, Z 30; nakrętka od wnętrza) → przewód 2 × 1 mm² 25 cm → wtyk DC → gniazdo Bonnetu; z zewnątrz wtyk kątowy zasilacza, kabel wychodzi dołem kieszeni. Trasa wzdłuż lewej ściany, opaska na uchwycie (−40, 70).
2. HUB75: Bonnet → kabel taśmowy 16‑pin 150 mm → HUB75 IN panelu (złożony w „Z” pod panelem, nad Bonnetem; luz Z 34–37).
3. Zasilanie panelu: terminal śrubowy Bonnetu → kabel VH4 panelu (w zestawie) → panel.
4. Hall: 3 × 3 żyły AWG 28 od wkładki przez szczeliny blatu (±66, 90) → wzdłuż tylnej ściany → płytka proto w uchwycie (40, 70) → JST 5‑pin → Dupont do listwy na Bonnecie.
5. Głowica: 4 żyły przez otwór (−70, przód, Z 38) → wzdłuż lewej ściany → listwa Bonnetu.
6. Przycisk: 4 żyły (2 styk + 2 LED) z (30, przód, Z 22) wprost do płytki proto i listwy Bonnetu (ok. 150 mm), opaska na bossie Pi (−30,5, −24,5).
7. USB serwisowe: gniazdo panelowe (50, tył, Z 24) → kabel 30 cm → USB‑A Pi (górny lewy port). Odbiornik klawiatury: dolny lewy port USB Pi; jeśli zasięg < 3 m przez obudowę → przedłużacz 20 cm przyklejony rzepem do lewej ściany na Z 40.
Długości kabli: wszystkie ≤ 300 mm; zapas pętli 50 mm przy blacie, żeby blat dało się zdjąć i odłożyć obok bez odpinania Halla (złącze JST na płytce proto pozwala odpiąć).

Wentylacja: patrz D14. Powietrze wchodzi szczelinami w dnie pod Pi (konwekcja od radiatora Pi), wychodzi szczelinami w ścianach Z 8 i przez szczelinę między panelem a ścianami do przestrzeni pod blatem — blat nie jest szczelny na kołnierzu (luz 0,3), co daje wylot górny; szczeliny ścian są zabezpieczone daszkiem.

---

## 8. Elektronika i montaż

### 8.1 Piny zajęte przez RGB Matrix Bonnet (mapowanie `adafruit-hat`, biblioteka rpi‑rgb‑led‑matrix)
GPIO 4 (OE), 17 (CLK), 21 (LAT), 22 (A), 26 (B), 27 (C), 20 (D), 24 (E — na Bonnecie zworka lutownicza „E” → „8”, wymagana dla panelu 64 × 64), 5 (R1), 13 (G1), 6 (B1), 12 (R2), 16 (G2), 23 (B2). Zarezerwowany dodatkowo GPIO 18 (zworka jakości PWM „GPIO4–GPIO18”, mapowanie `adafruit-hat-pwm`; zalecana, bo usuwa migotanie). HAT + RTC używa ponadto I2C (GPIO 2, 3) dla zegara DS1307 — magistrala współdzielona, bez konfliktu z VL53L1X (adres 0x29 vs 0x68).

Wolne: GPIO 2, 3 (I2C1), 7, 8, 9, 10, 11 (SPI0), 14, 15 (UART), 19, 25.

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
| VL53L1X | SDA | GPIO 2 / pin 3 | Dupont 4‑żył, JST 4 |
| VL53L1X | SCL | GPIO 3 / pin 5 | |
| VL53L1X | VIN, GND | 3,3 V / pin 1, GND / pin 9 | |
| VL53L1X | XSHUT, GPIO1 | niepodłączone | |
| Przycisk — styk | NO → GPIO, COM → GND | GPIO 7 / pin 26, wewnętrzny pull‑up | Dupont 2 |
| Przycisk — LED 5 V | anoda → 5 V przez 100 Ω; katoda → kolektor 2N2222; emiter → GND; baza ← GPIO 10 / pin 19 przez 1 kΩ | GPIO 10 | Dupont 2 + płytka proto |
| Odbiornik klawiatury | USB | port USB‑A 2.0 Pi (dolny lewy) | — |
| USB serwisowe | USB | port USB‑A 3.0 Pi (górny) | kabel panelowy 30 cm |
| (rezerwa) | — | GPIO 9, 11, 14, 15 | — |

Konflikty: brak. Uwaga: wyjście A3144 przy zasilaniu 5 V jest otwartym kolektorem — NIGDY nie podciągać do 5 V; rezystory 10 kΩ wyłącznie do pinu 1 (3,3 V). W `config.txt` wyłączyć SPI (`dtparam=spi=off`), włączyć I2C (`dtparam=i2c_arm=on`), wyłączyć dźwięk (`dtparam=audio=off` — wymagane przez rpi‑rgb‑led‑matrix), `isolcpus=3` w `cmdline.txt`.

### 8.3 Płytka prototypowa Halla (30 × 20)
Złącze JST‑XH 5 (5 V, GND, A, B, C) od strony Pi; 3 × JST‑XH 3 (VCC, GND, OUT) od strony czujników; 3 × 10 kΩ między OUT a dodatkową żyłą 3,3 V (6. żyła osobnym Dupontem z pinu 17) — żeby nie mieszać 5 V i 3,3 V, wylutować pola i opisać markerem. Tranzystor LED przycisku na tej samej płytce (ramka wieczorna).

---

## 9. Kolejność składania i testy

| Krok | Czynność | Test / kryterium zaliczenia |
|---|---|---|
| 1 | Pomiary (sekcja 10) → wpis do skryptu sesji 2 → eksport STL → wysłanie zapytania o wycenę do 2–3 usługodawców MJF/SLS; zamówienie w tygodniu zakupu elektroniki. | Arkusz zamówienia ma objętości wszystkich STL; usługodawca potwierdził PA12, kolory i gabaryt 200 × 200 × 55. |
| 2 | System na stole: Raspberry Pi Imager → Raspberry Pi OS Lite 64‑bit, SSH + Wi‑Fi firmowe; `apt install` zależności; kompilacja rpi‑rgb‑led‑matrix z powiązaniem Python; `config.txt` jak w 8.2; zworki Bonnetu (E, PWM). | `ssh` działa; `demo -D0 --led-rows=64 --led-cols=64 --led-gpio-mapping=adafruit-hat-pwm` daje stabilny obraz bez migotania. |
| 3 | Panel + Bonnet + zasilacz: wzór testowy, cyfry na marginesie, pomiar poboru prądu multimetrem w szereg. | Biel pełna < 3,5 A; typowy obraz ramki (zielone pola + cyfry) < 1,5 A; Pi nie restartuje się. |
| 4 | Klawiatura: odbiornik w Pi, skrypt Python `evdev` czyta klawisze. Gest: VL53L1X przez `python3-smbus` / biblioteka `vl53l1x`, próg 50–300 mm. | Każdy klawisz daje właściwe zdarzenie; machnięcie 5–30 cm nad czujnikiem = 1 zdarzenie, 0 fałszywych w 5 min. |
| 5 | Elektronika Halla na stole: płytka proto, 3 czujniki na kablach 50 cm, test magnesem ø5 × 2 (biegun S do czujnika). | Każde wejście przechodzi 1 → 0 przy magnesie ≤ 4 mm, wraca do 1 po odsunięciu; przy odwróconym biegunie brak reakcji (to potwierdza, którą stroną kleić). |
| 6 | Części z druku: oględziny, wypłukanie proszku, próba pasowania na sucho: płytka we wkładce, wkładka na blacie, pokrywka na płytce, blat na korpusie. | Płytka wchodzi i wychodzi bez siły, luz wyczuwalny < 0,5 mm; pokrywka trzyma po odwróceniu; blat zatrzaskuje się i daje się zdjąć ręką. |
| 7 | Wkładki gwintowane: korpus (4 × M3 panel, 4 × M2,5 Pi, 2 × M3 uchwyty), blat (4 × M3 rama, 2 × M3 słupki), głowica (2 × M2,5). Temperatura grotu 230 °C, prostopadle. | Każda wkładka licuje z powierzchnią ± 0,2; śruba wchodzi bez oporu. |
| 8 | Montaż Pi + Bonnet na bossach, listwa kątowa dolutowana do pinów 1, 3, 4, 5, 9, 17, 19, 22, 24, 26, 35, 39 Bonnetu. Panel: dystanse wkręcone w panel, panel wsunięty, 4 wkręty od spodu. | Stos Pi nie dotyka spodu panelu (szczelina ≥ 2 mm, sprawdzić szczelinomierzem/kartą); panel równoległy do dna (różnica < 0,5 mm na rogach). |
| 9 | Dyfuzor w kieszeni blatu, rama dyfuzora od spodu 4 × M3, próba zamknięcia blatu na korpusie z panelem. | Rama otacza panel bez nacisku; blat zamyka się do końca; okno równo nad panelem (przesunięcie < 1 mm). |
| 10 | Wkładka: czujniki Halla wklejone w kieszenie półek (lico do góry, kropla CA na bok obudowy, nie na lico), przewody w rowkach, wyprowadzenie przez uszy i szczeliny blatu do płytki proto. Magnesy w uszach i blacie (najpierw sprawdzić przyciąganie, potem CA). | Wkładka siada na kołkach i trzyma magnesami (nie przesuwa się przy pchnięciu palcem); płytka testowa wchodzi na kołek orientacyjny tylko w jednej orientacji. |
| 11 | Magnesy w płytkach wg kodów: nr 1 (A), 2 (B), 3 (A+B), 4 (C), 5 (A+C), 6 (B+C); biegun S w dół; CA. | Skrypt odczytu pokazuje 1…6 dla każdej płytki, 0 bez płytki, odczyt stabilny 60 s, zmiana < 100 ms po położeniu. |
| 12 | Okablowanie końcowe: gniazdo DC, USB panelowe, przycisk (W) / zaślepka (P), głowica (W), uchwyty kabli, opaski, opisy kabli; rzep na odbiornik, stopki. | Żaden kabel nie dotyka diod ani radiatora; blat daje się zdjąć i odłożyć obok bez rozpinania; obudowa stoi stabilnie. |
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
| 3 | Panel: wysokość diod/maski nad PCB | S | panel_led_h | 2 | ______ |
| 4 | Panel: najniższy element od spodu (złącza, kondensatory) | S | panel_bottom_parts_h | 12 | ______ |
| 5 | Panel: rozstaw otworów M3 w X i Y (środek–środek) | S/L | panel_hole_pitch_x / _y | 120 / 120 | ______ / ______ |
| 6 | Panel: przesunięcie środka wzoru otworów względem środka PCB | L | panel_hole_offset_x / _y | 0 / 0 | ______ / ______ |
| 7 | Panel: prostokąt obejmujący złącza HUB75 IN/OUT i zasilania od spodu (środek, szer., wys.) | L | panel_conn_zone_* | 0, 0, 120, 60 | ______ |
| 8 | Panel: która krawędź to góra (strzałka na PCB) — zapisać, by ustawić HUB75 IN od strony Bonnetu | — | (orientacja w skrypcie) | IN przy x < 0 | ______ |
| 9 | Pi + Bonnet: spód PCB Pi → najwyższy element Bonnetu | S | pi_stack_h | 26 | ______ |
| 10 | Bonnet: pozycja gniazda DC (która krawędź Pi, odległość od narożnika SD) | L | bonnet_dc_pos_x / _y | −92 / 0 | ______ |
| 11 | Bonnet: pozycja złącza HUB75 (krawędź, odległość) | L | (notatka) | — | ______ |
| 12 | Skaner Aidite: czy płytka 96 × 96 z pracami skanuje się w całości (test na kartonowej makiecie 96 × 96 z 4 rogami zaznaczonymi) | T | plate_size | 96 | ______ |
| 13 | Klawiatura: model (tylko do notatki, bez podstawki) | K | — | — | ______ |
| 14 | Odbiornik USB: dł. × szer. × wys. | S | receiver_* | 19 / 15 / 6 | ______ |
| 15 | Przycisk arkadowy: średnica otworu montażowego, długość korpusu za ścianką | S | button_hole_d, button_body_depth | 30, 40 | ______ |
| 16 | Gniazdo DC panelowe: średnica otworu; wtyk kątowy zasilacza: wysięg od lica gniazda i wysokość (musi być ≤ 22 i ≤ 24) | S | dc_hole_d, dc_pocket_depth, dc_pocket_h | 12, 22, 24 | ______ |
| 17 | Gniazdo USB‑A panelowe: okno, rozstaw otworów flanszy | S | usb_cut_w / usb_cut_h / usb_hole_pitch | 15 / 8 / 22 | ______ |
| 18 | Moduł VL53L1X: wymiary PCB, rozstaw otworów | S | tof_pcb_*, otwory głowicy | 25 / 18 / 4 | ______ |
| 19 | Usługodawca: materiały i kolory PA12, max gabaryt, cena/cm³, czy robi CNC PMMA ze STL/STEP | K | (arkusz zamówienia) | — | ______ |
| 20 | Wkładki gwintowane: średnica zewnętrzna M3 i M2,5 (zależnie od producenta) | S/K | insert_hole_m3 / _m25 | 4,0 / 3,4 | ______ |

Po wpisaniu: `panel_pcb_z`, `korpus_h`, `blat_top_z`, `panel_standoff_l` przeliczają się same; sprawdzić, czy `panel_standoff_l` wypada na dostępnej długości (30/35/40/45) — jeśli nie, zmienić `panel_boss_h` tak, by suma zgadzała się z `panel_pcb_z` − `floor_t`.

---

## 11. Wstępny koszt części zamawianych

Z gabarytów (objętość materiału, nie bryły); stawka orientacyjna MJF/SLS PA12 w Polsce 0,9–1,6 zł/cm³ przy tej skali zamówienia + opłata za gabaryt dużych części; barwienie grafit +15–25 %, wygładzanie parowe +25–40 %. Dokładnie policzy sesja 2 z objętości STL.

| Część | Obj. ok. [cm³] | Szt. | Obj. razem | Najtańszy (PA12 naturalny) [zł] | Pokazowy (barwienie + wygładzanie) [zł] |
|---|---|---|---|---|---|
| Płytka wieczorna | 62 | 3 | 186 | 170–300 | 170–300 (biała, bez barwienia; bez wygładzania wierzchu) |
| Płytka poranna | 61 | 3 | 183 | 165–290 | 165–290 |
| Pokrywka | 22 | 4 | 88 | 80–140 | 80–140 |
| Korpus | 215 | 2 | 430 | 390–690 | 600–1 050 |
| Blat | 85 | 2 | 170 | 155–270 | 240–420 |
| Rama dyfuzora | 18 | 2 | 36 | 35–60 | 50–90 |
| Wkładka gniazda | 16 | 3 | 48 | 45–80 | 45–80 |
| Głowica | 8 | 1 | 8 | 10–15 | 15–25 |
| Zaślepka | 3 | 1 | 3 | 5–10 | 8–15 |
| Uchwyt kabli | 6 | 2 | 12 | 12–20 | 12–20 |
| **Razem** | | | ~1 165 | **1 070–1 880 zł** | **1 390–2 430 zł** |

Największy koszt to korpus (ok. 35 %). Jeśli wycena przekroczy budżet: zmniejszyć `wall_t` do 2,0 i `floor_t` do 2,5 (−15 % korpusu) albo zamówić korpus w SLS zamiast MJF (często taniej dla dużych brył).

---

## 12. Przekazanie do sesji 2

### 12.1 Pliki do wytworzenia
1. `build_ramki.py` — skrypt Blendera (bpy, bez płatnych dodatków): stałe z sekcji 3 na górze, funkcja na każdą część, eksport STL w mm, każda część na Z = 0 największą płaską ścianą w dół.
2. STL: 11 plików z D16 + 6 numerowanych wariantów płytek (`ramka_plytka_wieczorna_n1_v1.stl` … `n3`, `ramka_plytka_poranna_n4_v1.stl` … `n6`).
3. `plytka_wieczorna_gniazda.json`, `plytka_poranna_gniazda.json` (format w 4.1).
4. (usunięte: nalepka legendy, Z26)
5. `render_ramka.png` — złożenie: korpus + blat + wkładka + płytka wieczorna + głowica + przycisk (bryły zastępcze dla elementów kupowanych), widok 3/4 od przodu, oraz `render_plytki.png` obie płytki z góry.
6. `arkusz_zamowienia.md` + `arkusz_zamowienia.csv`: część, plik, ilość, materiał, kolor, wykończenie, objętość cm³ (z Blendera), gabaryt, koszt w obu wariantach, uwaga o STEP/FreeCAD przy CNC.
7. `plan_ramki_v1.md` bez zmian (sesja 2 dopisuje tylko objętości i koszty w sekcji 11 jako `plan_ramki_v1_koszty.md`).

### 12.2 Sprawdzenia geometrii, które sesja 2 musi wykonać (asercje w skrypcie)
1. Każde gniazdo i rynienka w całości w strefie [−45, 45]² i poza narożnikami (|x| > 35 ∧ |y| > 35); minimalna odległość między krawędziami sąsiednich gniazd/rynienek ≥ 3,0 (liczona z górnych obrysów).
2. Żaden otwór ø3 ani gniazdo nie leży nad półką wkładki (12 × 12 w narożnikach otworu).
3. Łańcuch wysokości: `panel_pcb_z` − (`floor_t` + `pi_standoff_h` + `pi_stack_h`) ≥ `pi_clearance_top`; `blat_top_z` = `panel_pcb_z` + `panel_pcb_t` + `panel_led_h` + `led_gap` + `diffuser_t`; `korpus_h` = `blat_top_z` − `blat_t`; `floor_t` + `panel_boss_h` + `panel_standoff_l` = `panel_pcb_z`.
4. Walec kolizji przycisku (ø34 × 40, oś (`button_pos_x`, `button_pos_z`)) nie przecina bossów panelu, Pi ani głowicy; zapas ≥ 3 mm.
5. Stos Pi (85 × 56 × `pi_stack_h` od Z 8, plus 15 mm wysięg wtyku DC w stronę `bonnet_dc_pos`) nie przecina bossów panelu, ścian, szczelin wentylacyjnych ani skrzynki kieszeni DC (x −80…−40, y 78…100, Z 12…40).
6. Magnes–czujnik ≤ 4 mm: `magnet_pocket_depth` − `magnet_h` + (`insert_shelf_h` − 1,5) + 0,5 ≤ 4.
7. Wkładka w oknie: rama + uszy mieszczą się w kieszeni dyfuzora i na blacie; uszy kończą się przed kołnierzem blatu (y 96 < 97,2); szczeliny kabli nie wpadają w kieszeń dyfuzora (|y| 86–94 > 81 ✓).
8. Margines matrycy od przodu i z prawej: żadna część oprócz ramy wkładki (4 mm) nie zasłania pasa 32 mm; raport liczby odsłoniętych pełnych pikseli na każdy bok (oczekiwane 11).
9. Minimalna grubość ścianki każdej części ≥ 1,5 (próbkowanie wybranych przekrojów: ścianki między gniazdami, półki wkładki, kołnierz pokrywki, daszki wentylacyjne).
10. Brak zamkniętych pustek (każdy wolumen łączy się z zewnętrzem); manifold każdego STL (Blender „3D Print Toolbox”: 0 non‑manifold, 0 intersecting faces).
11. Objętość każdego STL w cm³ do arkusza; suma do sekcji 11.

### 12.3 Drobne kwestie do rozstrzygnięcia przez sesję 2
- Font napisów (dowolny bezszeryfowy pogrubiony dostępny w Blenderze; litery bez cienkich elementów < 1 mm).
- Dokładne położenie i kształt żeber na dnie korpusu i pod blatem (byle nie w strefach Pi, szczelin i bossów).
- Kształt daszków wentylacyjnych (pełny okap lub krótkie listki) — ważne tylko, by otwór patrzył w dół.
- Rozstaw otworów słupków w głowicy pod wybrany moduł VL53L1X (po pomiarze #18).
- Promienie zaokrągleń niewymienione w planie: zewnętrzne 3, wewnętrzne 1.
- Kolejność id gniazd w JSON (zalecane: rzędami od przodu, od lewej).
- Czy pokrywka ma garby na 4 bokach czy na 2 (jeśli 4 nie da się włożyć bez siły — 2 boki: przód i tył).
- Dokładne nazwy warstw/kolekcji w Blenderze i parametry renderu.
