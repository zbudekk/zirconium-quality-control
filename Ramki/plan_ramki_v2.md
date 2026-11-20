# Plan budowy ramek świetlnych i płytek — plan_ramki_v2 (ŹRÓDŁO PRAWDY)

Wersja 2 planu z sesji 1. **Ten plik jest nadrzędny wobec wszystkich innych** (`sesja2_pliki.md`, `spec_3d_ramka.md`, `plan_ramki_v1.md`): przy rozbieżności obowiązuje ten plik, a wartości liczbowe obowiązują w postaci zapisanej w `parametry.json` (sekcja 13, R14). Wszystkie wymiary w mm, kąty w stopniach, jedna liczba na wymiar. Sekcja 13 zawiera rejestr rozstrzygnięć (R1…R59) z oznaczeniem `[ZAŁOŻENIE]` tam, gdzie decyzja wymaga zatwierdzenia przez właściciela projektu; sekcja 14 — listę zmian względem v1.

---

## 1. Założenia

| Id | Założenie | Uzasadnienie (jedno zdanie) |
|---|---|---|
| Z1 | Pole skanowania Aidite A‑IS Pro 3 ≥ 100 × 100 mm; płytka 96 × 96 zostaje. **[R54]** Przy obrocie stolika pole „widzi” koło o średnicy `scan_field_d` 100 wokół osi, nie kwadrat: obrysy gniazd, rynienek i stożków znaczników leżą w kole o promieniu `socket_zone_r` 47 (Z29, D6); obrys płytki 96 × 96 bez zmian. | Spec zakłada 100 × 100 do potwierdzenia (pomiar #12 mierzy teraz `scan_field_d`); rozmiar płytki jest parametrem `plate_size`, a koło gniazd parametrem `socket_zone_r`, więc zmiana pola to jedna liczba i przeliczenie D6 skryptem. |
| Z2 | Maksymalna wysokość pracy nad dnem gniazda: 14 mm (`max_work_height`). | Największe korony trzonowe w stanie zielonym (skurcz ~20–25 %) mają do ~13 mm, mosty na rynienkach leżą niżej. |
| Z3 | Strefa narożna wyłączona z gniazd: kwadrat 13 × 13 mm w każdym rogu płytki. | Mieści stożek ø5 (środek 6 mm od krawędzi), 3 dołki kodu, kieszeń magnesu, wycięcie 5 × 5 i numer, przy ściankach ≥ 1 mm do sąsiednich cech. |
| Z4 | **[R54 UCHYLONE]** Kieszenie magnesów zostają w rogach (środek 6 mm od obu krawędzi, `marker_offset`; czujniki Halla wkładki bez zmian); stożki znaczników przesunięte do koła gniazd (`ev_marker_pos`, `mo_marker_pos`, D6) i NIE są współosiowe z magnesami. | Rogi leżą 59,4 mm od środka płytki i wypadają z pola przy obrocie (Z29); kieszeń magnesu 2,2 od dołu i stożek 3 od góry leżą w różnych miejscach XY — pod każdą cechą zostaje pełna reszta grubości 8 mm. |
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
| Z19 | Kolor: korpus, blat — PA12 barwiony na grafit; wkładka, płytki — PA12 naturalny biały; pokrywka — PETG FDM (druk własny); tulejka DC i podkładki panelu — PETG FDM (druk własny u kolegi; **[R55]** bez żywicy — drukarka żywiczna wycofana z planu). Rama dyfuzora i uchwyty kabli usunięte (R50‑U1, R50‑U8). | Zgodnie z 4.7; biały pod skaner, grafit na pokaz; materiały per część w `materials`. |
| Z20 | **[R59]** Gniazda w rzędach symetrycznych względem x = 0, w kole `socket_zone_r` 47; na każdej płytce JEDNA rynienka — przednia (decyzja właściciela 14.11.2026 na bramce G0: wieczorna wariant W‑b, poranna wariant P‑e, rynienka jedna długa D3‑a); w miejscu dawnej rynienki tylnej i małych gniazd są gniazda duże; rzędy gniazd przesunięte „[cytat usuniety]”, na porannej dwa rzędy mieszane (ø12,5 i ø15 obok siebie). Wieczorna 18 (6 × ø12, 12 × ø15) + 1 rynienka 60 × 15; poranna 23 (20 × ø12,5, 3 × ø15) + 1 rynienka 50 × 13; bez ø9, ø7,5 i ø10. Dawniej [R54]: wieczorna 18 (7 × ø9, 6 × ø12, 5 × ø15) + 2 rynienki, poranna 31 (18 × ø7,5, 7 × ø10, 6 × ø12,5) + 2 rynienki (przednia i tylna); jeszcze dawniej 24 + 2 / 35 + 2. | Zlecenie właściciela 14.11: w gniazda ø9 i ø7,5 nie weszła żadna z 17 prac próby, a na porannej 2 z 17 prac nie mieściły się w ø12,5 i szły do rynienki (wchodzą w ø15) — próba mała (`R59_propozycja_ukladu.md` pkt 2); układ policzony `narzedzia/uklad_kolo_R59.js` i sprawdzony `narzedzia/weryfikuj_uklad_R59.js` (rachunek i tabele w D6); stare płytki fizyczne z układem R54 będą jeszcze skanowane — program stanowiska dostaje je jako osobny układ (sesja R59‑P). |
| Z21 | Orientacja płytki: narożnik z wycięciem = przód‑prawy (D); czujniki Halla pod A (przód‑lewy), B (tył‑lewy), C (tył‑prawy). | Wycięcie z przodu po prawej jest dobrze widoczne dla praworęcznego technika. |
| Z22 | Ceny w liście zakupów są orientacyjne (wyszukiwanie nie zwróciło cen w zł). | Zaznaczone zgodnie z 0.1.5. |
| Z23 | Odstęp dioda–dyfuzor 4 mm (`led_gap`). | Środek zakresu 3–5 mm ze spec. |
| Z24 | Rynienki mają 4 otwory ø3 w dnie (rozstaw 12 mm wieczorna, 10 mm poranna). | Jeden otwór nie doświetliłby 60‑mm mostu. |
| Z25 | (uchylone przez Z28) | — |
| Z26 | Bez podstawki klawiatury i bez nalepki z legendą (odstępstwo od spec 4.6 i tabeli 6). Klawiatura leży luzem na stole; legenda klawiszy tylko w instrukcji programu. | Klawiatura ma własne stopki, a tacka to ok. 60 cm³ druku bez funkcji; użytkownik nie chce nalepki. |
| Z27 | Ramka poranna jest chowana do szafki, więc gniazdo DC siedzi w kieszeni wgłębionej w tylnej ściance (okno 51 × 24, głębokość 22, skrzynka do lewej ściany — R50‑4), **gniazdo w prawej ścianie skrzynki osią wzdłuż X (R50‑3)**; wtyk kątowy 5,5/2,1 wchodzi od wnętrza kieszeni w −X, kabel wychodzi przez okno; wtyk prosty też się mieści (do 40 + zagięcie). Wtyk nie wystaje poza obrys 200 × 200. Obudowy są identyczne, więc kieszeń ma też ramka wieczorna. | Wystający prosty wtyk łamałby się przy wsuwaniu ramki do szafki i wymuszał odpinanie zasilacza; gniazdo osią X nie celuje w dystans panelu (−60, 60) i nie zależy od długości korpusu gniazda ani wysięgu wtyku. |
| Z28 | **Decyzja właściciela (nadpisuje spec 1, 3.6, 4.5):** skan wieczorem uruchamia spacja na laptopie. Ramka wieczorna nie ma przycisku ani czujnika gestu: bez przycisku arkadowego, otworu w przedniej ściance, zaślepki, głowicy VL53L1X, ich kabli, przepustów, wkładek i pozycji w listach. Przednia ścianka obu korpusów gładka, bez otworów, tylko wytłoczony napis. Jedyna różnica między ramkami: odbiornik USB klawiatury w porannej (i napis). | Mniej części, mniej otworów w pyle, identyczne obudowy; stan ramki widać na matrycy. |
| Z29 | **[R54]** Pole skanowania przy obrocie = koło o średnicy `scan_field_d` 100 wokół osi stolika (DO_ZMIERZENIA, pomiar #12); zapas: ułożenie środka płytki względem osi ±1,5 (`scan_center_tol`) i wysięg korony poza obrys gniazda 1,5 (`work_overhang`) → `socket_zone_r` = 50 − 1,5 − 1,5 = 47 (LICZONE). | Stolik obraca płytkę wokół osi pionowej (ścieżka bez przechyłu), więc o widoczności pracy w całym obrocie decyduje jej odległość od osi, nie bok płytki; przy innym wyniku #12 zmienia się jedna liczba i D6 przelicza się skryptem. |
| Z30 | **[R57]** Drugi wariant płytki do testu skanera: PŁYTKA OKRĄGŁA ø`plate_round_d` 100 × 8 (= granica pola skanowania `scan_field_d`; zadanie zakładało 96, decyzja nadzoru 2.11: 100, ZATWIERDZONE przez właściciela 2.11.2026; 4.1a) z tym samym układem gniazd, rynienek, otworów i stożków co kwadrat tego typu (koło r 47; od R59 układ W‑b / P‑e), dołkami kodu i cyfrą wewnątrz koła, ścięciem orientacyjnym zamiast wycięcia D; bez kieszeni magnesów i rowka pokrywki. Numery n8 (wieczorna) i n9 (poranna) w kodzie 4‑bitowym n = A + 2B + 4C + 8D (bit D wstecznie zgodny: n1–n6 bez dołka D). | Właściciel 2.11: zamówienie płytek okrągłych jako drugiego wariantu do testu skanera; brak wystających rogów (mniej kolizji w komorze), dołki kodu w polu ø100 (na kwadracie leżą na promieniu 54–58, poza polem); użycie na ramce wymaga nowej wkładki i pokrywki (po teście, R58). |

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
Części zamawiane (SLS/MJF PA12): korpus W/P i blat — PA12 barwiony na grafit (wariant pokazowy: barwienie + wygładzanie parowe); wkładka i płytki — PA12 naturalny biały, bez wygładzania wierzchu płytek (mat dla skanera); **[R55]** bez alternatywy żywicznej dla płytek. Druk własny wyłącznie FDM PETG u kolegi: pokrywka, tulejka DC, podkładki panelu, płytka testowa n1 (test skanera) i prototypy pasowań. Rama dyfuzora i uchwyty kabli usunięte (R50‑U1, R50‑U8). Alternatywa CNC z PMMA opal 8 mm tylko dla płytek, jeśli usługodawca nie ma PA12 — wtedy STEP przez FreeCAD (wykonawca dodaje notatkę w arkuszu).

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
Wkładka = rama 4 mm szeroka × 6 mm wysoka wokół otworu 96,8 × 96,8 [R53: było 96,6; luz płytki 0,4/stronę], z 4 narożnymi półkami 12 × 12 × 2,5 mm wewnątrz otworu. Płytka leży na półkach; narożne strefy płytki 13 × 13 nie mają gniazd (Z3), więc półki nie zasłaniają żadnego otworu świetlnego. W półkach A, B, C kieszeń przelotowa 5,0 × 5,5 na czujnik A3144 (TO‑92 leżący płasko, lico do góry, stoi na dyfuzorze: wierzch obudowy 1,5 mm → 1,0 mm pod spodem płytki). Odległość magnes–czujnik: 0,2 (magnes cofnięty w kieszeni 2,2 przy grubości 2,0) + 1,0 (szczelina) + ~0,5 (głębokość struktury w TO‑92) = 1,7 mm ≤ 4 ✓. Pole na osi magnesu ø5 × 2 N35 (Br 1,2 T): przy 1,7 mm ~150 mT; przy 4 mm ~45 mT; próg A3144 ~40 mT → rezerwa > 3× ✓. Półka D niesie kołek orientacyjny 4,4 × 4,4 × 5 wchodzący w wycięcie 5 × 5 płytki. Zasłonięte piksele: rama 4 mm = 1,6 piksela na każdym boku; półki leżą pod strefami narożnymi bez gniazd → 0 pikseli użytkowych. Wolny pas marginesu: 32 − 0,4 − 4 = 27,6 mm = 11 pełnych pikseli z każdej strony [R53] (wystarcza na 2 cyfry 5 × 7). **[R58]** Wkładka okrągła (4.6a) pod płytkę okrągłą ramkową (4.1b): ten sam obrys ramy 104,8 × 6 i uszy; otwór ø100,8 (luz 0,4) ze ścięciem 49,756 od środka na −45°; płytka leży na ciągłym występie r 47…50 i na 4 półkach 10 × 10 w osiach A, B, C, D na promieniu 45 (przekątne: (±31,82; ±31,82)); kieszenie Halla 5,0 × 5,5 pod osiami magnesów A/B/C płytki (r 45, nie w rogach ±42); **[runda 2, B1 recenzji]** zamiast kołka ø3 × 2 (wchodził w pustą kieszeń magnesu na tym samym promieniu) na osi D przy ścięciu stoi żebro klucza 3,0 (od r 46,5 do lica ścięcia 49,756, poniżej Z 6 zrośnięte ze ścianą, wierzch Z 7,0 = 1,0 nad wkładką, faza 1,0), które wchodzi w rowek klucza 3,6 od spodu płytki (od r 46,0, wysokość 5,0); żebro sięga 2,16 poza kieszeń magnesu (r 47,6), więc w złym obrocie płytka nie siada płasko — leży na żebrze (przechył ok. 2,6°, krawędź +4,5). Ścięcie NIE blokuje obrotu (płytka wnika w ścięcie wkładki tylko 0,244 przy luzie 0,4) — jest znakiem wzrokowym i oparciem żebra. Odległość magnes–czujnik bez zmian 1,7 ≤ 4; ścianka ramy w osiach 52,4 − 50,4 = 2,0 ≥ 1,5.

### D6. Rozkład gniazd (pkt 0.3.1) — rachunek [R59: jedna rynienka i większe gniazda; R54: układ kołowy]
Dlaczego koło: skaner obraca płytkę wokół osi pionowej (ścieżka bez przechyłu, Z29), więc w całym obrocie widoczne jest koło o średnicy `scan_field_d` 100 wokół osi stolika, nie kwadrat 100 × 100. Z zapasem na ułożenie płytki (±1,5, `scan_center_tol`) i wysięg korony poza obrys gniazda (1,5, `work_overhang`) obrysy górne wszystkich gniazd, rynienek i stożków znaczników leżą w kole o promieniu `socket_zone_r` = 50 − 1,5 − 1,5 = 47 (od środka płytki). Dawne układy: sprzed R54 (24 + 2 / 35 + 2, promień do 54,9 / 52,6, stożki w rogach 61,9) — archiwum `plan_ramki_v2_przed_R54_2026-11-01.md`; R54 (18 + 2 / 31 + 2, dwie rynienki) — archiwum `plan_ramki_v2_przed_R59_2026-11-14.md` i `parametry_przed_R59_2026-11-14.json`.

Zasady: strefa gniazd x, y ∈ [−45, 45] (kwadrat `socket_zone` 90, ścianka 3 do krawędzi płytki) i koło r 47; każdy wpis rzędu symetryczny względem x = 0 (K‑05 b); ścianki ≥ 3 mm między wszystkimi obrysami — w rzędzie i po przekątnej między rzędami przesuniętymi „[cytat usuniety]”. **[R59]** Dokładnie jedna rynienka na płytce, jako pierwszy rząd od przodu (most leży najbliżej technika; usunięta rynienka tylna porannej była najciaśniejszym miejscem układu R54: 0,07 do koła). Rząd mieszany (dwie średnice obok siebie) zapisuje się w `ev_rows` / `mo_rows` jako dwa wpisy o różnym y; numery id gniazd (R13) idą wtedy po y wpisu. Warunek dla gniazda okrągłego: √(x² + y²) + d/2 ≤ 47; dla rynienki l × w: √(((l − w)/2)² + y²) + w/2 ≤ 47. Układ wybrał właściciel na bramce G0 (14.11.2026) spośród wariantów policzonych przeglądem kolejności rzędów (`narzedzia/uklad_kolo_R59.js`; `R59_propozycja_ukladu.md`: wieczorna W‑b, poranna P‑e wg szkicu właściciela) i sprawdzonych `narzedzia/weryfikuj_uklad_R59.js`. Pozycji nie zmienia się ręcznie: ścianki nie mają zapasu (3,000).

Wieczorna (środki gniazd, mm; wpisy rzędów od przodu, −y):

| Wpis | y (zakres) | Zawartość | id | Skrajny promień obrysu | Limit |
|---|---|---|---|---|---|
| 1 | −30,2 (−37,7…−22,7) | rynienka 60 × 15, środek x = 0 | 1 | √(22,5² + 30,2²) + 7,5 = 45,16 | 47 |
| 2 | −13,7 (−19,7…−7,7) | ø12 ×6: x = −37,5, −22,5, −7,5, 7,5, 22,5, 37,5 | 2–7 | √(37,5² + 13,7²) + 6 = 45,92 | 47 |
| 3 | +2,75 (−4,75…10,25) | ø15 ×5: x = −36, −18, 0, 18, 36 | 8–12 | √(36² + 2,75²) + 7,5 = 43,60 | 47 |
| 4 | +18,35 (10,85…25,85) | ø15 ×4: x = −27, −9, 9, 27 | 13–16 | √(27² + 18,35²) + 7,5 = 40,15 | 47 |
| 5 | +33,95 (26,45…41,45) | ø15 ×3: x = −18, 0, 18 | 17–19 | √(18² + 33,95²) + 7,5 = 45,93 | 47 |

Blok y −37,7…41,45 (79,15 ≤ 90). Ścianki: rynienka → ø12 w pionie 3,00 (−22,7 → −19,7); w rzędach 3,00 (rozstaw 15 przy ø12 i 18 przy ø15); po przekątnej między rzędami: ø12 → ø15 3,02 (środki (37,5, −13,7) i (36, 2,75)), ø15 → ø15 3,01 (rzędy co 15,6 przesunięte o 9: √(9² + 15,6²) = 18,01 = 7,5 + 7,5 + 3,01). Razem 18 gniazd + 1 rynienka (6 × ø12, 12 × ø15); dawniej [R54] 18 + 2 (7 × ø9, 6 × ø12, 5 × ø15), jeszcze dawniej 24 + 2. Znaczniki (`ev_marker_pos`): A (−35,5, −26,5) — bez zmian, B (−31, 31,5), C (42, 14,5) [R54: B (−35,5, 26,5), C (35,5, 26,5)] — promień środka 44,30 / 44,20 / 44,43 ≤ 44,5; ścianka do najbliższego gniazda 3,52 (A, rynienka) / 3,23 (B) / 3,19 (C); boki trójkąta AB 58,17, BC 74,95, AC 87,68 (różne o ≥ 5 — program przypisuje A/B/C jednoznacznie).

Poranna:

| Wpis | y (zakres) | Zawartość | id | Skrajny promień obrysu | Limit |
|---|---|---|---|---|---|
| 1 | −35,3 (−41,8…−28,8) | rynienka 50 × 13, środek x = 0 | 1 | √(18,5² + 35,3²) + 6,5 = 46,35 | 47 |
| 2 | −19,55 (−25,8…−13,3) | ø12,5 ×5: x = −31, −15,5, 0, 15,5, 31 | 2–6 | √(31² + 19,55²) + 6,25 = 42,90 | 47 |
| 3 | −6,1 (−12,35…0,15) | ø12,5 ×6: x = −38,75, −23,25, −7,75, 7,75, 23,25, 38,75 | 7–12 | √(38,75² + 6,1²) + 6,25 = 45,48 | 47 |
| 4 | +8 (1,75…14,25) | ø12,5 ×4: x = −32,25, −16,75, 16,75, 32,25 (rząd mieszany z wpisem 5) | 13–16 | √(32,25² + 8²) + 6,25 = 39,48 | 47 |
| 5 | +8,75 (1,25…16,25) | ø15 ×1: x = 0 (rząd mieszany z wpisem 4) | 17 | 8,75 + 7,5 = 16,25 | 47 |
| 6 | +22,85 (15,35…30,35) | ø15 ×2: x = −24,5, 24,5 (rząd mieszany z wpisem 7) | 18–19 | √(24,5² + 22,85²) + 7,5 = 41,00 | 47 |
| 7 | +23,6 (17,35…29,85) | ø12,5 ×2: x = −7,75, 7,75 (rząd mieszany z wpisem 6) | 20–21 | √(7,75² + 23,6²) + 6,25 = 31,09 | 47 |
| 8 | +37,05 (30,8…43,3) | ø12,5 ×3: x = −15,5, 0, 15,5 | 22–24 | √(15,5² + 37,05²) + 6,25 = 46,41 | 47 |

Blok y −41,8…43,3 (85,1 ≤ 90); rząd ø12,5 ×6 sięga granicy strefy ±45 (38,75 + 6,25 = 45,00). Rzędy mieszane: w trzecim rzędzie gniazd ø15 leży w środku między czterema ø12,5 (wpisy 4 i 5), w czwartym dwa ø15 leżą po bokach dwóch ø12,5 (wpisy 6 i 7); środki obu wpisów rzędu mieszanego różnią się w y o 0,75 (wynik ułożenia na ściankę 3 do sąsiednich rzędów). Ścianki (najmniejsza w parze wpisów): rynienka → ø12,5 w pionie 3,00 (−28,8 → −25,8); w rzędach 3,00 (rozstaw 15,5); po przekątnej 3,00…3,06 (wpisy 2–3: 3,02; 3–4: 3,03; 3–5: 3,00; 4–5: 3,02; 4–6: 3,00; 5–7: 3,00; 6–7: 3,02; 6–8: 3,06; 7–8: 3,02). Razem 23 gniazda + 1 rynienka (20 × ø12,5, 3 × ø15); dawniej [R54] 31 + 2 (18 × ø7,5, 7 × ø10, 6 × ø12,5), jeszcze dawniej 35 + 2 (liczba zmienia się tylko przez edycję D6 i `mo_rows` na bramce). Znaczniki (`mo_marker_pos`): A (−30,5, −32), B (−37,5, 23,5), C (41,5, 16) [R54: A (−34,5, −28), B (−30, 32,5), C (30, 32,5)] — promień środka 44,21 / 44,25 / 44,48 ≤ 44,5; ścianka do gniazd 3,45 (A, rynienka) / 3,02 (B) / 3,48 (C); boki trójkąta AB 55,94, BC 79,36, AC 86,53.

Sprawdzone (`weryfikuj_uklad_R59.js` na `parametry.json`, 14.11: 103 sprawdzenia OK, 0 błędów; te same liczby z JSON i siatek w K‑05 / K‑16 raportu R59): max promień obrysu 45,93 (wieczorna, ø15 w (±18, 33,95)) / 46,41 (poranna, ø12,5 w (±15,5, 37,05)) ≤ 47 — zapas 1,07 / 0,59 (R54: 0,61 / 0,07); max |x| + r i |y| + r = 43,5 / 45,0 ≤ 45; min ścianka gniazdo–gniazdo 3,00 / 3,00; dołek kodu kwadratu–gniazdo 8,27 / 8,61 ≥ 3; dołek–znacznik 6,01 / 11,03 ≥ 1,5; cyfra kwadratu–gniazdo 11,74 / 13,84; wycięcie D–gniazdo 16,67 / 19,18. Jeśli pomiar #12 zmieni `scan_field_d`, D6 przelicza się tymi skryptami, a liczby gniazd w K‑05 (a) wynikają z `ev_rows` / `mo_rows`. Warianty R59 nie wybrane (`R59_propozycja_ukladu.md`): wieczorna W‑a (16 × ø15), W‑c (21 gniazd z 7 × ø9); poranna P‑a, P‑b, P‑c, P‑d (z ø10), P‑e1, P‑e‑33, P‑e0; rynienka podzielona na dwie krótkie (D3‑b) — odrzucona; dwie prace w jednej rynience (D3‑c) — wymaga zmiany programu, odłożone. Alternatywy odrzucone w R54: płytka okrągła ø96–100 i mniejszy kwadrat — ta sama pojemność przy nowej wkładce i pokrywkach; płytka okrągła wraca, gdy #12 da pole < ~94 (od R57 istnieje jako drugi wariant do testu skanera, 4.1a).

### D7. Czujnik Halla i elektryka (pkt 0.3.3)
A3144: VCC 5 V, GND, OUT otwarty kolektor → 10 kΩ do 3,3 V na płytce prototypowej + wejście GPIO. Logika: magnes obecny = stan niski. Biegun: południowy (S) skierowany w dół, do czujnika, we wszystkich płytkach — przed klejeniem oznaczyć S flamastrem (strony przyciągające się mają przeciwne bieguny; wzorzec: jeden magnes oznaczony raz, reszta względem niego). Alternatywa bez zmian w planie: Honeywell SS451A lub TI DRV5032 (omnipolarne, 3,3 V), ta sama obudowa TO‑92 i ten sam układ pinów VCC/GND/OUT; wtedy biegun dowolny.

### D8. Pokrywka płytki (pkt 0.3.4)
Luz liczony nad najwyższą pracą: `cover_inner_h` = `max_work_height` 14 − `socket_depth` 4 + 4 = 14 mm nad wierzchem płytki. Pokrywka to nakładka z kołnierzem schodzącym 4 mm poniżej wierzchu płytki, 4 zatrzaski (garby 0,7 mm: lewy i prawy bok na y = 0, przedni bok na x = +25, tylny bok na x = −25 — poza wycięciami palcowymi 30 mm na środkach przodu i tyłu, R42) wchodzą w rowek 1,0 × 0,8 mm wokół boków płytki, 2 mm pod jej wierzchem. Rowek nie koliduje z wkładką (jest cofnięty w głąb płytki). **[R58]** Pokrywka okrągła (4.2a): kubek ø100,6 / ø103,6 × 20, wierzch pełny 2, 4 garby o przekroju jak wyżej wyciągnięte po łuku (10 po licu wewnętrznym) na 25°, 155°, 205°, 335° (pary przy osi X; omijają ścięcie −45° ± 9,2° i wycięcia palcowe), w rowku 1,0 × 0,8 na całym obwodzie płytki okrągłej ramkowej (przez ścięcie też — w środku cięciwy zostaje 0,156 głębokości); garb wchodzi w rowek na 0,4, dół kołnierza 0,5 nad ramą wkładki; **[runda 2, P2 recenzji]** po obu stronach każdego garbu pionowa szczelina 1,0 × 12 przez kołnierz (środki ±6,5 po licu od środka garbu) — garb siedzi na języku 12 × 12 × 1,5 (owalizacja kubka przy luzie 0,30 by nie wystarczyła).

### D9. Mocowanie blatu
Blat 4 mm z kołnierzem 10 mm wysokim (2 mm grubym, luz 0,7 do ścian, R48, [R53] T1) wewnątrz korpusu; 4 haczyki zatrzaskowe (8 mm szerokie, występ 1,5, czubek 98,3, R48, [R53] T2a) w ślepe kieszenie ścian korpusu 11 × 3,5 głębokości 1,3 (zostaje 1,2 mm ścianki lokalnie — odstępstwo od 4.8 przyjęte świadomie, R6, [R53] T2b/T3; luz Z 0,75/0,75, do dna 0,5, boczny 1,5). Położenie haczyków i kieszeni: lewa ściana y = 0, prawa ściana y = 0, przednia ściana x = +50, tylna ściana x = −50 (omijają napis z przodu i kieszeń DC z tyłu). 2 wkręty M3 × 8 przez tylną ściankę w (±75, Z `blat_screw_z` 55) w otwory ø2,5 × 6 (gwint formowany, R49/R49a) w słupkach kołnierza (R7). Zero śrub na wierzchu. Właściciel (R50‑U2 odrzucone): wkręty zostają, bo ramka poranna jest codziennie noszona do szafki.

### D10. Położenie Pi
Pi 4 płasko na 4 bossach ø8 × 5 (otwór ø2,1 pod wkręt M2,5 formujący gwint, R49) pod panelem; narożnik PCB Pi (krawędź z kartą SD, przednia) w (**−50, −28**) (R50‑6); Pi zajmuje x −50…35, y −28…28; karta SD w kierunku −X, złącze GPIO wzdłuż krawędzi y = +28; porty USB w kierunku +X (x 35…37). Pi leży w całości pod panelem. Od krawędzi SD do lewej ściany (−97,5) jest 47,5, od przedniej krawędzi do ściany 69,5, od tylnej do bossa uchwytu… (uchwyty usunięte, R50‑U8) do skrzynki DC (y 78) 50 → wtyk DC Bonnetu 40 mm mieści się w kierunkach −X, −Y i +Y; +X (w porty USB Pi) wyklucza sam Bonnet.

### D11. Numeracja płytek i kod
Numer n = A + 2·B + 4·C **[R57: + 8·D]** (bit A/B/C = magnes obecny w narożniku A, B, C; bit D bez kieszeni — tylko dołek, `code_bit_d_pos` (−45, −27) na kwadracie, na n1–n6 nie występuje). Dołki kodu w kolumnie przy lewej krawędzi obok narożnika A (R3): dołek 1 (bit A) y = −36, dołek 2 (bit B) y = −33, dołek 3 (bit C) y = −30 (dołek 4, bit D, y = −27), wszystkie x = −45,0, ø2 × 1 mm (ścianka do krawędzi płytki 2,0; **[R59]** do stożka A 6,01 / 11,03 (wieczorna / poranna), do najbliższego gniazda 8,27 / 8,61; do rowka pokrywki 1,3 lokalnie, R47). Płytki wieczorne: nr 1, 2, 3; poranne: nr 4, 5, 6 (typ płytki wynika z numeru); **[R57]** okrągłe: wieczorna n8 (tylko D), poranna n9 (A + D), dołki w kole w pozycjach `code_dimples_round` (per typ, 4.1a). 7 = rezerwa, 0 = brak płytki. Relief numeru (cyfra 5 mm wysoka, 0,6 mm) w narożniku D: środek (39,5, −44,5); okrągłe: `number_pos_round` (35, −26,5) / **[R59]** (−44, 5,5). **[R58]** Płytki okrągłe ramkowe (4.1b, decyzja właściciela 19.11.2026): numery jak kwadratowe — wieczorne n1–n3, poranne n4–n6 (`plate_numbers_round_frame`), kod n = A + 2B + 4C (bit D = 0; ramka czyta magnesy A/B/C w kieszeniach na r 45), dołki w pozycjach `code_dimples_round`, cyfra w `number_pos_round`; n8 i n9 zostają płytkami testowymi skanera (bez kieszeni). Ten sam numer n1–n6 ma płytka kwadratowa i okrągła ramkowa — program stanowiska rozróżni je dopiero po osobnej zmianie.

### D12. Wkładka w blacie: 2 kołki + 2 magnesy
Wkładka ma 2 tylne „uszy” 14 × 43,6 × 3 mm (od tylnej krawędzi ramy y = 52,4 do y = 96) [R53], środki x = ±58, każde z nasadą L 3 mm (x ±(44…52,4) od y 48,8; x ±(52,4…65) od y 52,4) zrośniętą ze ścianką ramy (R47, R51, [R53] T6b). W każdym uchu kołek ø3 × 3,5 w dół w (±58, 93,5) do otworu ø3,4 w blacie [R53: było 3,3; pasowanie ruchome 0,2, wkładkę trzymają magnesy], magnes ø5 × 2 w otworze przelotowym ø5,4 w (±58, 86) naprzeciw magnesu w kieszeni blatu (bieguny przyciągające). Uszy zasłaniają po 14 × 28 mm tylnych narożników marginesu matrycy (dozwolone: w całości odsłonięte mają być pas przedni i prawy). Przewody Halla: rowek 2,5 szer. × 1,5 wys. (R50‑U9) na zewnętrznej dolnej krawędzi ramy (lewy, tylny, prawy bok), jedna bryła z przelotem w ściance narożnika, potem kanał 2 × 1,2 pod uchem, do szczeliny 4 × 8 w blacie w (±66, 90). **[R58]** Wkładka okrągła (4.6a) ma ten sam obrys ramy, uszy, kołki, magnesy, rowek kablowy i kanały pod uszami (K‑65: mapy wysokości z góry i od spodu poza ramką = wkładka kwadratowa); od kieszeni Halla kanał biegnie po przekątnej przez pełny narożnik do naroża zewnętrznego i dalej rowkiem bocznym / tylnym jak dotąd.

### D13. Panel (rama dyfuzora usunięta, R50‑U1)
Panel skręcony od dołu (R5, R50‑2, R50‑7): dystans M3 żeńsko‑żeński 50 mm stoi na podkładce‑stadionie 9 × 1 na dnie (oś wzdłuż przekątnej od (±55, ±55) do (±65, ±65)), wkręt M3 × 10 z podkładką ø9 od spodu korpusu przez rowek 3,4 szer. w dnie (bez pogłębienia, R50‑U20) w gwint dystansu; góra: wkręt dociskowy M3 × 5 w gwintowany otwór M3 panelu (pomiar #5a) albo tulejka F‑F M3 ø5 × 5 doklejona epoksydem do spodu PCB + dystans 45 (bez gwintu). Bez bossów pod panelem. Panel jest ustalony w XY przez 4 dystanse w otworach panelu (±0,2); **rama dyfuzora usunięta [usunięte R50‑U1]** — bez pianki ani innego uszczelnienia (decyzja właściciela); szczelina między PCB 160 a oknem blatu 158 (nakładka 1 na stronę) i luz kołnierza blatu 0,5 przepuszczają światło tylko do wnętrza obudowy, nie na zewnątrz. Dyfuzor 160 × 160 × 2 leży w kieszeni blatu 162 × 162 × 2 na półce 2 mm (otwór przelotowy 158 × 158; naroża kieszeni ostre, R50‑U15, pleksi bez fazowania), licowany; dociskany magnesami wkładki.

### D14. Wentylacja i pył
Wlot: 2 szczeliny 30 × 4 w dnie pod środkiem Pi (x −8, y ±10) (R50‑U19). Wylot: szczeliny 12 × 3 **bez daszków** (R50‑U4) nisko w ścianach: tylna 4 szt. (x −54, −18, 18, 54), boczne po 3 szt. (y −36, 0, 36), oś na Z = 8 (R50‑U19). Stopki gumowe 4 mm samoprzylepne na płaskim dnie (bez gniazd, R50‑U16). Gniazda w tylnej ściance: DC z nakrętką w kieszeni wgłębionej (Z27, R50‑3, R50‑4): okno w ścianie 51 × 24 (x −93…−42, Z 14…38, naroża ostre R50‑U15), za nim skrzynka x −97,5…−40 (lewa ściana skrzynki = lewa ściana korpusu), y 78…100, Z 12…40 (ściany 2 mm, zamknięta od dołu, góry i prawego boku, otwarta tylko na zewnątrz); **gniazdo DC w prawej ścianie skrzynki** (płaszczyzna x = −40, ściana −42…−40), oś (y 89, Z 30) wzdłuż X, otwór ø12 (gniazdo ø8 przez tulejkę redukcyjną ø12/ø8,2), flansza w kieszeni, nakrętka od strony wnętrza obudowy (x > −40), korpus gniazda w +X (wolne 50 mm); wtyk kątowy wchodzi od wnętrza kieszeni w −X (wysięg 18–26 od lica −42 → ≥ 27 do lewej ściany), kabel obrócony ku +Y wychodzi przez okno; wtyk prosty do 40 + zagięcie 12 też się mieści (−94 > −95,5). Skrzynka mija podkładkę/dystans panelu (−60, 55…65) o ≥ 9,8 mm w Y, szczeliny wentylacyjne (Z ≤ 9,5) o 2,5 mm. Gniazdo USB‑A panelowe z zaślepką w (60, Z 24): okno 16 × 9 + 2 rowki poziome 3,2 × 5,7 (rozstaw flanszy 23…28, R50‑5); żadnych odsłoniętych złącz Pi.

### D15. Przednia ścianka (Z28)
Przednia ścianka gładka: bez otworów, bez przycisku, bez głowicy. Jedyna cecha: napis wypukły 0,6, wysokość liter 8, środek x = 0, Z = `label_pos_z` 51 (= korpus_h − 8,6), treść `label_text_W` / `label_text_P` (zostaje; R50‑U14 dla korpusu odrzucone przez właściciela). Kieszeń zatrzasku przedniego na x = +50 (R6) nie koliduje z napisem (relief na zewnątrz, kieszeń wewnątrz, R47(17)). Dawne D15 (głowica, przycisk, zaślepka) uchylone.

### D16. Nazwy plików STL (R2, R17)
Sufiks wersji `v2`. Pliki bazowe (do sprawdzeń i do `.blend`, NIE do zamówienia): `ramka_plytka_wieczorna_v2.stl`, `ramka_plytka_poranna_v2.stl`. Pliki do zamówienia w drukarni: `ramka_plytka_wieczorna_n1_v2.stl`, `…_n2_v2.stl`, `…_n3_v2.stl`, `ramka_plytka_poranna_n4_v2.stl`, `…_n5_v2.stl`, `…_n6_v2.stl`, `ramka_korpus_W_v2.stl`, `ramka_korpus_P_v2.stl`, `ramka_blat_v2.stl`, `ramka_wkladka_v2.stl` (10 plików). Pliki do druku własnego: `ramka_pokrywka_v2.stl` (PETG FDM), `ramka_tulejka_dc_v2.stl`, `ramka_podkladka_panelu_05_v2.stl`, `…_1_v2.stl`, `…_2_v2.stl` (PETG FDM [R55]). Razem 15 STL do druku + 2 bazowe = 17. Usunięte: `ramka_rama_dyfuzora_v2.stl` [R50‑U1], `ramka_uchwyt_kabli_v2.stl` [R50‑U8], głowica i zaślepka [Z28]. Pełna lista plików wynikowych: sekcja 12.1.

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
| trough_hole_count | 4 | szt. | Z24 | otwory ø3 w dnie rynienki (od R59 jedna rynienka na płytce; liczba i rozstaw otworów bez zmian) |
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
| code_bit_d_pos | (−45.0, −27) | mm | R57/D11 | 4. bit D kodu na płytce kwadratowej (w linii dołków); na n1–n6 nie występuje |
| plate_round_d | 100 | mm | R57 | średnica płytki okrągłej = granica pola skanowania (zadanie: 96 — ścianka do krawędzi 1,07 < 1,5; decyzja nadzoru 2.11: 100, ścianka 2,57; po R59 ścianka gniazdo–krawędź 4,07 / 3,59; 4.1a) |
| round_flat_w | 16 | mm | R57 | cięciwa ścięcia orientacyjnego płytki okrągłej (decyzja nadzoru 2.11; głębokość 0,644 ≥ `round_flat_depth_min`; ścianka do obrysów ≥ 3) |
| round_flat_depth_min | 0.6 | mm | R57 | najmniejsza głębokość ścięcia (widoczne po druku: > faza 0,5 i tolerancja ±0,3); K‑61 (e) |
| round_flat_angle | −45 | deg | R57 | kierunek normalnej ścięcia od +X (przód‑prawo, jak narożnik D) |
| code_dimples_round | per typ | mm | R57/R59 | dołki A/B/C/D okrągłych: wieczorna y −43,5, x −4,5/−1,5/1,5/4,5; poranna **[R59]** A (36,5, 18,5), B (36,5, 21,5), C (43, 6), D (43, 9) (dawniej x 30,5, y −31/−28/−25/−22) |
| number_pos_round | per typ | mm | R57/R59 | środek cyfry okrągłych: wieczorna (35, −26,5), poranna **[R59]** (−44, 5,5) (dawniej (36,5, −24,5)); `null` = bez cyfry |
| plate_numbers_round | {8}, {9} | — | R57/D11 | numery płytek okrągłych (wieczorna n8, poranna n9) |
| round_magnet_r | 45 | mm | R58 | promień osi cech kompletu okrągłego: kieszenie magnesów A/B/C płytki ramkowej, kieszenie Halla A/B/C i żebro klucza na osi D wkładki okrągłej (runda 2); osie na przekątnych (D = kierunek ścięcia), (±31,82; ±31,82) |
| round_key_slot_w | 3.6 | mm | R58 | rowek klucza od spodu płytki okrągłej ramkowej, oś na kierunku ścięcia: szerokość (**[runda 2]** żebro klucza 3,0 → luz 0,3/stronę) |
| round_key_slot_r0 | 46.0 | mm | R58/runda 2 | rowek klucza: promień płaskiego końca wewnętrznego (było 43); dalej na zewnątrz przez krawędź i ścięcie; czoło żebra r 46,5 → 0,5 |
| round_key_slot_h | 5.0 | mm | R58/runda 2 | rowek klucza: wysokość od spodu (Z −8…−3,0; było 2,5); ścianki 3D do gniazd z siatki (K‑64), nad żebrem 0,5 |
| plate_numbers_round_frame | {1, 2, 3}, {4, 5, 6} | — | R58/D11 | numery płytek okrągłych ramkowych (do ramki) — jak kwadratowe |
| cover_groove_w | 1.0 | mm | D8 | rowek zatrzaskowy na bokach płytki (wysokość) |
| cover_groove_depth | 0.8 | mm | D8 | głębokość rowka w bok płytki |
| cover_groove_z | 2 | mm | D8 | środek rowka poniżej wierzchu płytki |
| ev_socket_d_s | 9 | mm | spec | wieczorna, mała — typoszereg; od R59 nie występuje w układzie (średnice gniazd biorą się z pola `d` rzędów `ev_rows`) |
| ev_socket_d_m | 12 | mm | spec | wieczorna, średnia (R59: 6 gniazd) |
| ev_socket_d_l | 15 | mm | spec | wieczorna, duża (R59: 12 gniazd) |
| ev_trough_l | 60 | mm | spec | rynienka wieczorna, długość |
| ev_trough_w | 15 | mm | spec | rynienka wieczorna, szerokość |
| mo_socket_d_s | 7.5 | mm | spec | poranna, mała — typoszereg; od R59 nie występuje w układzie (średnice gniazd biorą się z pola `d` rzędów `mo_rows`) |
| mo_socket_d_m | 10 | mm | spec | poranna, średnia — typoszereg; od R59 nie występuje w układzie |
| mo_socket_d_l | 12.5 | mm | spec | poranna, duża (R59: 20 gniazd; dodatkowo 3 gniazda ø15 zapisane tylko w `mo_rows`, bez osobnego klucza) |
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
| round_cover_snap_angles | 25 / 155 / 205 / 335 | ° | R58 | kąty środków garbów pokrywki okrągłej od +X (omijają ścięcie płytki i wycięcia palcowe) |
| round_cover_slit_w | 1.0 | mm | R58/runda 2 | szerokość pionowych szczelin odciążających po obu stronach każdego garbu (8 szt., przelotowe przez kołnierz) |
| round_cover_slit_h | 15 | mm | R58/runda 3 | wysokość szczelin od dolnej krawędzi kołnierza do środka otworu końcowego (Z −20…−5; garb na języku 12 × 15 × 1,5; runda 2: 12) |
| round_cover_slit_offset | 6.5 | mm | R58/runda 2 | środek szczeliny od środka garbu po licu wewnętrznym r 50,3 (±7,4°) |
| round_cover_slit_end_d | 2.0 | mm | R58/runda 3 | otwór przelotowy na górnym końcu każdej szczeliny (środek na osi szczeliny, Z −5; „dziurka od klucza”); górny koniec Z −4, do spodu wierzchu 2,0 |

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
| panel_slot_w | 3.6 | mm | R50‑2/R53 | szerokość rowka przelotowego w dnie (= panel_screw_hole_d); [R53] T12: 3,4 → 3,6 (rowki i otwory MJF wychodzą mniejsze o 0,1–0,2) |
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
| panel_screw_hole_d | 3.6 | mm | R5/R53 | szerokość rowka przelotowego w dnie pod wkręt M3 panelu (bez pogłębienia, R50‑U20); [R53] T12: 3,4 → 3,6 |
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
| snap_pocket_w | 11 | mm | D9/R53 | ślepa kieszeń zatrzasku w ścianie; [R53] T3c: 10 → 11 (luz boczny haczyka 8: 1,5/stronę) |
| snap_pocket_h | 3.5 | mm | D9/R53 | j.w.; [R53] T3a: 2,5 → 3,5 (luz Z 0,75 pod i 0,75 nad występem haczyka 52,85…54,85) |
| snap_pocket_depth | 1.3 | mm | R6/R53 | j.w., od wewnątrz; [R53] T2b: 1,0 → 1,3 (dno kieszeni 98,8, luz czubek haczyka–dno 0,5; zostaje 1,2 ścianki lokalnie — odstępstwo od 4.8, 4 pola nienośne) |
| snap_pocket_z | 52.1 | mm | D9/R50‑1/R53 | dolna krawędź kieszeni (liczona: korpus_h − 7,5); [R53] T3b: 52,6 → 52,1 (kieszeń Z 52,1…55,6 symetrycznie wokół występu 52,85…54,85) |
| snap_side_y | 0 | mm | R6 | kieszeń/haczyk na lewej i prawej ścianie: y |
| snap_front_x | 50 | mm | R6 | kieszeń/haczyk na przedniej ścianie: x |
| snap_rear_x | −50 | mm | R6 | kieszeń/haczyk na tylnej ścianie: x |
| blat_screw_pitch | 150 | mm | R7 | 2 × M3 w tylnej ściance, x = ±75 |
| blat_screw_z | 55 | mm | D9/R50‑1 | j.w. (liczony: korpus_h − 4,6) |
| blat_screw_hole_d | 3.6 | mm | 4.3/R53 | otwór przelotowy wkrętu M3 blatu w tylnej ścianie (pogłębienie stożkowe ø6,3 / 90° bez zmian); [R53] T4: 3,2 → 3,6 (luz 0,3/stronę = położenie ±0,3 korpusu + ±0,3 słupka blatu na rozstawie 150; klasa „coarse” ISO 273) |
| ~~holder_pos_x, holder_pos_y, holder_axis, holder_boss_d, holder_boss_h~~ | — | — | [usunięte R50‑U8] | bez uchwytów kabli i bossów; podstawki opasek samoprzylepne |
| ~~rib_w, rib_h, rib_start_r~~ | — | — | [usunięte R50‑U5] | bez żeber dna |

### 3.4 Blat, wkładka (rama dyfuzora usunięta, R50‑U1)

| Parametr | Wartość | Jedn. | Źródło | Opis |
|---|---|---|---|---|
| blat_t | 4 | mm | D9 | grubość płyty blatu |
| blat_skirt_h | 10 | mm | D9 | kołnierz pod blatem |
| blat_skirt_t | 2 | mm | D9 | grubość kołnierza |
| blat_skirt_clearance | 0.7 | mm | R48/R53 | luz kołnierz–ściana na stronę (kołnierz 193,6 w 195); [R53] T1: 0,5 → 0,7 (±0,3 korpus + ±0,3 blat + 0,1 zapasu na wypaczenie ścian) |
| blat_corner_r | 5 | mm | spec | jak korpus |
| snap_hook_w | 8 | mm | D9 | haczyk zatrzasku |
| snap_hook_h | 1.5 | mm | R48/R53 | występ haczyka (lico kołnierza 96,8 → czubek 98,3; zahacza 0,8 w ścianie 97,5, luz do dna kieszeni 98,8 = 0,5); [R53] T2a: 1,3 → 1,5 |
| pi_boss_d | 8 | mm | R48/R49 | boss Pi (ścianka 2,95 wokół otworu ø2,1 pod wkręt formujący gwint) |
| blat_post_w | 8 | mm | R48 | słupek blatu w X (x ±71…79) |
| snap_hook_z | 52.85 | mm | R47/R50‑1 | dolna krawędź występu haczyka (globalnie, liczona: korpus_h − 6,75); lokalnie −10,75 |
| snap_hook_hgt | 2.0 | mm | R47 | wysokość występu haczyka (Z 52,85…54,85) |
| snap_hook_arm_l | 9 | mm | R47 | długość nacięć od dolnej krawędzi kołnierza (do Z 58,6; lokalnie −5) |
| snap_notch_w | 1 | mm | R47 | szerokość nacięcia obok haczyka |
| blat_post_y0 | 89.2 | mm | R47 | słupek blatu y 89,2…95,2 (po wewnętrznej stronie kołnierza) |
| blat_post_hole_depth | 6 | mm | R49a | otwór ø2,5 w słupku od lica 96,8 do 90,8 (dno 1,6 ≥ 1,5) [R53: lico kołnierza 96,8 po T1; gwint wkrętu M3 × 8 w słupku 4,8] |
| blat_screw_csink_d | 6.3 | mm | R47 | pogłębienie stożkowe 90° otworu wkrętu blatu w ścianie korpusu |
| snap_hook_t | 1.5 | mm | D9 | grubość ramienia |
| ~~rama_outer, rama_inner, rama_h, rama_screw_pos, rama_ear_t, rama_ear_d, rama_ear_hole_d, rama_tab_size, rama_tab_inner, rama_boss_d, rama_boss_h~~ | — | — | [usunięte R50‑U1] | rama dyfuzora i bossy ramy w blacie usunięte |
| insert_opening | 96.8 | mm | spec/R53 | otwór wkładki; [R53] T6: 96,6 → 96,8 (luz płytki 0,4/stronę: płytka ±0,29 + wkładka ±0,29 MJF; interfejs płytki bez zmian) |
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
| orient_post_gap | 0.6 | mm | D5/R53 | odstęp kołka od ścian otworu; [R53] T6c: 0,5 → 0,6 (kołek zostaje w (45,6, −45,6) jak przed R53; przy 0,5 naroże kołka zahaczało o R 1,5 wnęki pokrywki o 0,059) |
| finger_cut_w | 30 | mm | spec | wycięcie palcowe, przedni bok ramy, pełna wysokość |
| tab_w | 14 | mm | D12 | ucho wkładki |
| tab_end_y | 96 | mm | D12 | koniec ucha (Y) |
| tab_t | 3 | mm | D12 | grubość ucha |
| tab_pos_x | 58 | mm | D12 | środki uszu x = ±58 |
| tab_pin_d | 3 | mm | D12 | kołek ustalający |
| tab_pin_h | 3.5 | mm | D12 | j.w. |
| tab_pin_y | 93.5 | mm | D12 | j.w. |
| tab_magnet_y | 86 | mm | D12 | magnes ucha i blatu |
| blat_pin_hole_d | 3.4 | mm | D12/R53 | otwór kołka w blacie, ślepy od góry; [R53] T5: 3,3 → 3,4 (kołek ø3: pasowanie ruchome 0,2 zamiast wciskanego 0,15; wkładkę trzymają magnesy) |
| blat_pin_hole_depth | 3.8 | mm | R8 | głębokość otworu kołka (blat 4,0 → zostaje 0,2 dna; pył nie wpada) |
| blat_magnet_pocket_d | 5.4 | mm | D12 | kieszeń magnesu w blacie, od góry |
| blat_magnet_pocket_depth | 2.3 | mm | D12 | j.w. |
| wire_slot_l | 8 | mm | D12 | szczelina kabla Halla w blacie (Y) |
| wire_slot_w | 4 | mm | D12 | j.w. (X), środek (±66, 90) |
| wire_rabbet | 1.5 | mm | D12 | rowek na kable, zewn. dolna krawędź ramy: wysokość |
| wire_rabbet_w | 2.5 | mm | R50‑U9 | rowek: szerokość (x 52,4 → 49,9 [R53]; do otworu 48,4 zostaje 1,5); jedna bryła z przelotem w ściance narożnika |
| tab_root_x_in | 44 | mm | R47 | nasada ucha: x od ±44 do ±65 |
| tab_root_x_out | 52.4 | mm | R51/R53 | nasada L: x 44…52,4 od y 48,8; x 52,4…65 dopiero od y 52,4 (= zewnętrzna krawędź ramy insert_opening/2 + 4); [R53] T6b: 52,3 → 52,4 |
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
| round_insert_clearance | 0.4 | mm | R58 | luz promieniowy płytki okrągłej we wkładce okrągłej: otwór ø100,8, ścięcie 49,356 + 0,4 = 49,756 |
| round_insert_ledge_r | 47 | mm | R58 | promień wewnętrzny ciągłego występu wkładki okrągłej (Z 0…2,5) |
| round_insert_shelf | 10 | mm | R58 | bok 4 półek kwadratowych wkładki okrągłej (środki w osiach A–D, boki równoległe do osi) |
| ~~round_key_pin_d, round_key_pin_h, round_key_pin_chamfer~~ | — | — | [usunięte R58 runda 2] | kołek klucza ø3 × 2 wchodził w pustą kieszeń magnesu (B1 recenzji) — zastąpiony żebrem |
| round_key_rib_w | 3.0 | mm | R58/runda 2 | żebro klucza wkładki okrągłej na osi D: szerokość styczna (w rowku 3,6 → 0,3/stronę) |
| round_key_rib_r0 | 46.5 | mm | R58/runda 2 | żebro: początek (czoło) r 46,5; poniżej Z 6 do lica ścięcia wkładki 49,756, zrośnięte ze ścianą |
| round_key_rib_h | 4.5 | mm | R58/runda 2 | wysokość żebra nad półką (Z 2,5…7,0; 1,0 nad wierzchem wkładki) |
| round_key_rib_chamfer | 1.0 | mm | R58/runda 2 | faza górnych krawędzi żebra (boki i czoło wewnętrzne; runda 3 także krawędź zewnętrzna części górnej) |
| round_key_rib_top_r1 | 49.2 | mm | R58/runda 3 | koniec promieniowy części żebra nad wierzchem wkładki (Z 6…7; P1 recenzji rundy 2: kołnierz pokrywki w skrajnym ustawieniu schodzi do r 49,6) — zapas w rzucie 0,40 |

### 3.5 Małe części: odbiornik, tulejka DC, podkładki panelu (uchwyt kabli usunięty, R50‑U8)

| Parametr | Wartość | Jedn. | Źródło | Opis |
|---|---|---|---|---|
| ~~holder_l, holder_w, holder_h, holder_foot_t, holder_slot_w, holder_slot_h, holder_comb_t, holder_board_groove_w, holder_board_groove_depth, proto_board_l, proto_board_w~~ | — | — | [usunięte R50‑U8] | uchwyt kabli → podstawki opasek samoprzylepne; płytka proto na taśmie VHB |
| receiver_l | 19 | mm | DO ZMIERZENIA | odbiornik USB nano (tylko bryła zastępcza, korpus P) |
| receiver_w | 15 | mm | DO ZMIERZENIA | j.w. |
| receiver_h | 6 | mm | DO ZMIERZENIA | j.w. |
| dc_bush_outer_d | 11.85 | mm | R50‑3/R52 | tulejka redukcyjna DC: ø zewn. = dc_hole_d − 0,15 (celowo wciskowe 0,075/stronę, R52) [R53: tabela uzgodniona z JSON; T7: druk własny po zmierzeniu otworu ø12 w gotowym korpusie — wartość skorygować przed drukiem; **[R55]** FDM PETG: przy luzie/zacisku skalować XY w slicerze ±1 % zamiast zmieniać plik] |
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
| quantities_r58 | słownik | szt. | R58 | ilości kompletu okrągłego do ramki: płytki okrągłe ramkowe n1–n6 po 1, wkładka okrągła 3, pokrywka okrągła 4; osobno od `quantities` (arkusz zamówienia R59 i K‑57 bez zmian) |
| materials_r58 | słownik | — | R58 | materiały kompletu: płytki i wkładka „PA12 drukarnia” (naturalny biały, mat), pokrywka „PETG FDM (własny)” |

---
## 4. Specyfikacja części do zamówienia

Układ współrzędnych: jak w D3 (globalny; płytki i pokrywka w układzie lokalnym płytki). Każda część modelowana w położeniu montażowym, a przed eksportem przesunięta tak, by największa płaska ściana leżała na Z = 0. Wszystkie luzy ruchome 0,3 mm na stronę, wciskane 0,15 mm, zapas na chropowatość SLS 0,3 mm wliczony w podane otwory.

### 4.1 `ramka_plytka_wieczorna_v2.stl` i `ramka_plytka_poranna_v2.stl`
- Funkcja: nośnik prac do skanera i do ramki; wspólna geometria, różne gniazda.
- Gabaryt: `plate_size` × `plate_size` × `plate_thickness` = 96 × 96 × 8; pionowe krawędzie R 1, górne krawędzie faza 0,5.
- Cechy wspólne (układ lokalny, wierzch płytki Z = 0, materiał w dół do Z = −8):
  1. Gniazda stożkowe: wierzch ø d, dno ø d − 2·4·tan15° = d − 2,14, głębokość 4, otwór ø3 przelotowy w osi. Pozycje: D6.
  2. Rynienki: obrys z zaokrąglonymi końcami (stadion) l × w, ścianki 15°, głębokość 4, 4 otwory ø3 na osi w rozstawie `ev_/mo_trough_hole_pitch`, symetrycznie względem środka rynienki. Pozycje: D6; **[R59]** jedna rynienka na płytce (przednia).
  3. Stożki znaczników ø5 × 3 (wierzchołek w dół) **[R54]** w kole gniazd, osobno dla typu płytki (`ev_marker_pos` / `mo_marker_pos`, D6): **[R59]** wieczorna A (−35,5, −26,5), B (−31, 31,5), C (42, 14,5); poranna A (−30,5, −32), B (−37,5, 23,5), C (41,5, 16) (dawniej R54: wieczorna B (−35,5, 26,5), C (35,5, 26,5); poranna A (−34,5, −28), B (−30, 32,5), C (30, 32,5)). Promień środka ≤ `socket_zone_r` − 2,5 = 44,5; ścianka do gniazd ≥ 3; boki trójkąta ABC różne o ≥ 5 (jednoznaczne przypisanie znaczników w programie). Dawne rogi (±42, ±42) bez stożków.
  4. Wycięcie 5 × 5 przelotowe w D: x ∈ [43, 48], y ∈ [−48, −43].
  5. Dołki kodu ø2 × 1 (R3): bit A (−45,0, −36), bit B (−45,0, −33), bit C (−45,0, −30); **[R57]** bit D (−45,0, −27) (`code_bit_d_pos`). Plik bazowy `ramka_plytka_<typ>_v2.stl`: wszystkie 4 dołki wycięte (A + B + C + D; do R57 trzy), BEZ cyfry reliefu (wzorzec do sprawdzeń). Warianty do zamówienia (R4): `_n1…_n3` (wieczorna), `_n4…_n6` (poranna) — dołki tylko dla bitów = 1 numeru (n = A + 2B + 4C + 8D; na n1–n6 bit D = 0, więc dołka D nie ma), cyfra reliefu = n; po 1 szt. każdego wariantu.
  6. Kieszenie magnesów od spodu ø5,2 × 2,2 w rogach A (−42, −42), B (−42, 42), C (42, 42) (`marker_offset` 6 od obu krawędzi; **[R54]** nie są już współosiowe ze stożkami znaczników, Z4 uchylone; czujniki Halla wkładki bez zmian). Wszystkie 3 kieszenie w każdej płytce (magnes wklejony lub nie).
  7. Numer: relief 0,6, cyfra 5 mm, środek (39,5, −44,5), font `font_name` (R22); tylko w wariantach numerowanych.
  8. Rowek pokrywki 1,0 wysoki × 0,8 głęboki wokół 4 boków, środek 2 mm pod wierzchem; przerwany w wycięciu D.
- Luzy: płytka w otworze wkładki 96,8 → 0,4 na stronę [R53: było 96,6 / 0,3]; wycięcie 5 × 5 na kołek 4,4 → 0,3 (kołek 0,6 od ścian otworu, luz na stronę otwartą 0,4 — bez zmian).
- Łączy się z: wkładka (półki, kołek), pokrywka (rowek), magnesy, skaner.
- Orientacja do druku: gniazdami do góry, spód płaski na stole.
- Ilość: 3 + 3 (n1, n2, n3 wieczorne; n4, n5, n6 poranne). Materiał: PA12 naturalny biały, mat, bez wygładzania. Alternatywa **[R55: tylko]** CNC PMMA opal, jeśli usługodawca nie ma PA12 (wtedy STEP przez FreeCAD); żywica wykluczona.
- Plik JSON obok każdej płytki (R13): `uklad_gniazd_wieczorna.json`, `uklad_gniazd_poranna.json` — źródło prawdy układu gniazd: skrypt CZYTA je i z nich buduje gniazda; pierwszą wersję skrypt generuje z D6, gdy plik nie istnieje. Struktura:
  ```json
  {"plate":"wieczorna","version":"v2","units":"mm",
   "coords":{"origin":"środek górnej powierzchni płytki","x":"w prawo (od użytkownika)","y":"do tyłu","notch_corner":"D = (+48, -48), przód-prawy"},
   "size":96,"thickness":8,
   "markers":[{"corner":"A","x":-35.5,"y":-26.5,"d":5,"depth":3},{"corner":"B","x":-31,"y":31.5,"d":5,"depth":3},{"corner":"C","x":42,"y":14.5,"d":5,"depth":3}],
   "notch":{"corner":"D","x_min":43,"x_max":48,"y_min":-48,"y_max":-43},
   "code_dimples":[{"bit":"A","x":-45.0,"y":-36},{"bit":"B","x":-45.0,"y":-33},{"bit":"C","x":-45.0,"y":-30},{"bit":"D","x":-45.0,"y":-27}],
   "magnet_pockets":[{"corner":"A","x":-42,"y":-42},{"corner":"B","x":-42,"y":42},{"corner":"C","x":42,"y":42}],
   "number_relief":{"x":39.5,"y":-44.5,"text_h":5},
   "sockets":[
     {"id":1,"type":"trough","x":0,"y":-30.2,"l":60,"w":15,"angle":0,"depth":4,"hole_d":3,"hole_pitch":12,"hole_count":4},
     {"id":2,"type":"round","x":37.5,"y":-13.7,"d_top":12,"d_bottom":9.86,"depth":4,"hole_d":3}
   ],
   "leds":{}}
  ```
  `id` rzędami od przodu (R1, R2, …), w rzędzie od prawej (od strony narożnika D z wycięciem) do lewej; **[R59]** rząd mieszany = dwa wpisy o różnym y, id idą po y wpisu (poranna: id 13–16 ø12,5 w y 8, id 17 ø15 w y 8,75; id 18–19 ø15 w y 22,85, id 20–21 ø12,5 w y 23,6); `d_bottom = d_top − 2·depth·tan(15°)` (9 → 6,86; 12 → 9,86; 15 → 12,86; 7,5 → 5,36; 10 → 7,86; 12,5 → 10,36). `leds` wypełnia kalibracja (sekcja 9).; `leds` wypełnia kalibracja (sekcja 9).

### 4.1a `ramka_plytka_okragla_wieczorna_v2.stl` i `ramka_plytka_okragla_poranna_v2.stl` **[R57, Z30]** — płytka okrągła (drugi wariant do testu skanera)
- Funkcja: nośnik prac do skanera (tylko); **[R58]** do ramki służy płytka okrągła ramkowa (4.1b) z wkładką okrągłą (4.6a) i pokrywką okrągłą (4.2a); n8 i n9 zostają płytkami testowymi skanera.
- Gabaryt: walec ø`plate_round_d` 100 × `plate_thickness` 8; górna krawędź faza `plate_top_chamfer` 0,5; bez promienia krawędzi pionowych. **ZAŁOŻENIE (nadzór 2.11, ZATWIERDZONE przez właściciela 2.11.2026): ø100 = granica pola skanowania; gniazda jak kwadrat tego typu w kole 47.** Liczby decyzji 2.11 (układ R54): zadanie zakładało ø96 — wtedy obrys górny rynienki tylnej porannej (promień 46,93) i stożków znaczników (44,43 + 2,5) leżał 1,07 od ściany pionowej i 0,57 od początku fazy (< 1,5, zasada 4.8); ø98 dawało 1,57–2,07; przy ø100 ścianka obrysu gniazda/rynienki do ściany pionowej wynosiła 3,61 (wieczorna) / 3,07 (poranna), do początku fazy 3,11 / 2,57, stożki znaczników 3,20 / 3,07 (obie bazy wg recenzji R57‑B D3). **[R59]** Po zmianie układu (W‑b / P‑e): obrys gniazda do ściany pionowej wieczorna 4,07 (ø15 w (±18, 33,95)) / poranna 3,59 (ø12,5 w (±15,5, 37,05)), do początku fazy 3,57 / 3,09; stożki znaczników do ściany pionowej 3,07 / 3,02 (w obu C). Kwadrat ma rogi na promieniu 67,9, więc ø100 mieści się w skanerze wszędzie tam, gdzie kwadrat.
- Cechy wspólne z kwadratem (IDENTYCZNE, z tego samego JSON rzędów D6 i `ev_/mo_marker_pos`): gniazda stożkowe, rynienki, otwory ø3, stożki znaczników A/B/C (4.1 p. 1–3). Sprawdzenie K‑05 (h): lista `sockets` okrągłej = lista kwadratu tego typu.
- Ścięcie orientacyjne zamiast wycięcia D: płaszczyzna pionowa na całej grubości, cięciwa `round_flat_w` 16 na kierunku `round_flat_angle` −45° (przód‑prawo); odległość od środka √(50² − 8²) = 49,356, głębokość 0,644 ≥ `round_flat_depth_min` 0,6 (widoczne po druku: > faza 0,5 i tolerancja ±0,3). Warunek nadzoru: ścianka od płaszczyzny ścięcia do każdego obrysu gniazda, rynienki, dołka i stożka ≥ 3 (K‑61 f): **[R59]** wieczorna 4,59, poranna 4,81 (w obu koniec rynienki przedniej); cyfra wieczornej 2,83 od płaszczyzny (relief, informacyjnie), cyfra porannej leży po przeciwnej stronie płytki. [R54: 3,68 (rynienka przednia) / 4,87 (dołek A), cyfra 2,8 / 3,2.] Zadanie zakładało cięciwę 8 (głębokość 0,16, niewidoczne); 20 odpadało w decyzji 2.11 (ścianka 1,3 < 3 na układzie R54).
- Dołki kodu ø2 × 1, 4 bity (A, B, C, D) wewnątrz koła, pozycje per typ (`code_dimples_round`): wieczorna rząd przed rynienką przednią y = −43,5, x = −4,5 (A), −1,5 (B), 1,5 (C), 4,5 (D) — promień ≤ 43,73, **[R59]** ścianka do rynienki 4,80 (R54: 3,50); poranna **[R59, wariant P‑e]**: rynienka leży w y −35,3 (obrys do y −41,8), więc rząd przed nią się nie mieści — dwie pary z prawej strony: A (36,5, 18,5), B (36,5, 21,5), C (43, 6), D (43, 9) — promień 40,92…43,93, ścianka do gniazd 3,55…4,08, do stożka C 2,09…6,61 (dawniej R57: kolumna x = 30,5, y = −31…−22, promień ≤ 43,49, ścianka 3,62). Warunki (K‑62): promień środka ≤ `socket_zone_r` − 3 = 44; do gniazd ≥ 3; do stożków ≥ 1,5; do krawędzi ≥ 1,5 (**[R59]** najmniejsze: do krawędzi 5,27 / 5,07; do stożków 31,86 / 2,09; R57: 5,27 / 4,87 i 31,9 / 51,0). Pozycje wieczornej zaakceptowane przez nadzór 2.11 jako ZAŁOŻENIE; pozycje porannej — decyzja właściciela na bramce G0 14.11.2026 (wariant P‑e). Plik bazowy: wszystkie 4 dołki, bez cyfry; `_n8` (wieczorna): tylko D; `_n9` (poranna): A + D.
- Numer: relief 0,6, cyfra 5 mm, wewnątrz koła 47 (`number_pos_round`): wieczorna (35, −26,5) — bez zmian; poranna **[R59]** (−44, 5,5), z lewej strony (dawne miejsce (36,5, −24,5) koliduje z gniazdem ø12,5 układu P‑e). Obrys cyfry 5 × 3,6 (`weryfikuj_uklad_R59.js`): promień narożnika 46,85 / 46,49 ≤ 47, od gniazd 3,27 / 3,48 ≥ 3, od stożków 36,35 / 13,70, od dołków 31,15 / 78,40, od płaszczyzny ścięcia 2,83 (wieczorna; relief, informacyjnie); `null` = bez cyfry. Wieczorna zaakceptowana przez nadzór 2.11; poranna — bramka G0 14.11.2026.
- BEZ: wycięcia D, kieszeni magnesów (spód płaski, K‑63), rowka pokrywki. Orientacja do druku: gniazdami do góry, spód płaski na stole. Ilość: 1 + 1 (n8, n9). Materiał: PA12 naturalny biały, mat (jak kwadratowe).
- Pliki JSON: `uklad_gniazd_okragla_wieczorna.json`, `uklad_gniazd_okragla_poranna.json` — struktura jak w 4.1 plus `shape: "round"`, `d: 100`, `size: 100`, `flat: {corner, angle_deg, chord_w, dist}`, `code_dimples` z 4 bitami, `magnet_pockets: []`, bez `notch`; kwadratowe JSON dostają `shape: "square"` i 4. dołek D. Program stanowiska: nowe foldery `modele_plytek/okragla_*` (sesja P3), parser toleruje `shape` (P1).
- Sprawdzenia: K‑01…K‑09, K‑11, K‑13, K‑16 jak kwadrat (z uwagami R57) oraz K‑61 (obrys ø100 ± 0,05 z sond promieniowych, ścięcie: położenie, głębokość ≥ 0,6, ścianka do obrysów ≥ 3, faza), K‑62 (dołki w polu, bity = numer), K‑63 (brak kieszeni i rowka, spód płaski); K‑59 obejmuje nowe pliki; w R57 15 plików R56 bajtowo bez zmian; **[R59]** 12 plików płytek ma nowy układ gniazd i nowe SHA, 9 plików pozostałych części bajtowo jak R57.
- Wykonanie w generatorze: walec z fazą (`bm_z_pierscieni`), ścięcie jako półprzestrzeń obrócona o `round_flat_angle`; otwory ø3 cięte w drugiej różnicy (jedna różnica zostawiała w bazowej wieczornej 3 zbędne ściany na dnie otworów → K‑03); ściany poziome triangulowane Delaunayem z ograniczeniami (`triangulacja_cdt`); pliki kwadratowe budowane bez zmian w kolejności brył i triangulacji.

### 4.1b `ramka_plytka_okragla_ramkowa_wieczorna_v2.stl` i `ramka_plytka_okragla_ramkowa_poranna_v2.stl` **[R58]** — płytka okrągła do ramki
- Funkcja: nośnik prac do skanera i do ramki (decyzja właściciela 19.11.2026: pełny komplet okrągły — płytki, wkładka 4.6a, pokrywka 4.2a; korpus i blat bez zmian). Ryzyko przyjęte przez właściciela: średnica 100 zostaje, pole skanowania niezmierzone (`scan_field_d` DO_ZMIERZENIA).
- Bryła i wierzch IDENTYCZNE z płytką okrągłą tego typu (4.1a): walec ø100 × 8, faza 0,5, ścięcie (cięciwa 16 na −45°, 49,356 od środka), gniazda, rynienka, otwory ø3, stożki znaczników, pozycje dołków (`code_dimples_round`) i cyfry (`number_pos_round`), triangulacja CDT. K‑64 (g): mapa wysokości wierzchu z promieni co 0,25 = płytka okrągła tego typu (bazowa: 128 191 punktów, max |Δz| 0,0000; warianty bez otoczenia dołków i cyfry). Lista `sockets` = kwadrat tego typu (K‑05 h).
- Dodatkowo (od spodu i na boku):
  1. Kieszenie magnesów ø5,2 × 2,2 od spodu w osiach A (−31,82; −31,82), B (−31,82; 31,82), C (31,82; 31,82) na promieniu `round_magnet_r` 45 — wszystkie 3 w każdej płytce (magnes wklejony albo nie, jak kwadrat). Ścianki: do krawędzi 50 − 45 − 2,6 = 2,4 (zmierzone 2,40); do najbliższego otworu ø3 w rzucie 9,81 (wieczorna) / 7,48 (poranna); sufit kieszeni (Z −5,8) – dno gniazda (Z −4) 1,8; stożek znacznika – kieszeń w pionie 8 − 2,2 − 3 = 2,8 (w rzucie nakładają się: wieczorna B, poranna A).
  2. Rowek pokrywki 1,0 wysoki × 0,8 głęboki na całym obwodzie (od walca R 50 do R 49,2), środek 2 pod wierzchem (Z −1,5…−2,5), także przez ścięcie (w środku cięciwy zostaje 49,356 − 49,2 = 0,156 głębokości). Dno rowka do obrysów gniazd i stożków na Z −1,5 (stożki 15°): wieczorna 3,52 (stożek C), poranna 3,19 (gniazdo id 22) ≥ 1,5; dołki kodu kończą się 0,5 nad rowkiem.
  3. Rowek klucza od spodu **[runda 2: r0 46,0 i wysokość 5,0 — było 43 i 2,5]**: szerokość `round_key_slot_w` 3,6, oś na kierunku ścięcia (−45°), od promienia `round_key_slot_r0` 46,0 na zewnątrz przez krawędź i płaszczyznę ścięcia, wysokość `round_key_slot_h` 5,0 (Z −8…−3,0; sufit 3,0 pod wierzchem, wyżej niż dno gniazd Z −4), koniec wewnętrzny płaski. Ścianki 3D z siatki (K‑64 d): rowek – wnętrze 2,68 (wieczorna, do rynienki) / 6,36 (poranna, do gniazda ø12,5; rynienka 6,90 z rachunku); rowek – otwór ø3 w rzucie 12,2 / 10,5; pod rowkiem pokrywki (Z −2,5) zostaje 0,5 tylko w pasku 0,156 przy ścięciu (informacyjnie — tam rowek pokrywki i tak ma 0,156 głębokości). Żebro klucza wkładki 3,0 → luz 0,3/stronę, czoło żebra 0,5 od końca rowka, nad żebrem 0,5. Okno wejścia (K‑67: obrót 0…360° co 0,25° × przesunięcie w kole luzu 0,4 co 0,1 mm, każda z 8 płytek, puste kieszenie niezaklejone): płytka leży płasko tylko dla −0,75…+0,75° (1,5°); w −1,75…+1,75° krawędź rowka trafia na fazę żebra (naprowadzenie); poza tym leży na żebrze: uniesienie 4,48, przechył 2,59°, krawędź +4,5 — widoczne (P1 recenzji zamknięte rachunkiem). Ścięcie nie blokuje obrotu (wnikanie 0,244 < luz 0,4); stare płytki n8/n9 we wkładce okrągłej leżą na żebrze w każdym obrocie (ramka czyta 0 = brak płytki).
- Numery (D11): `plate_numbers_round_frame` — wieczorne n1, n2, n3, poranne n4, n5, n6; dołki wg bitów A/B/C (bit D = 0), cyfra reliefu = n w `number_pos_round`. Obrys cyfry z siatki (K‑64 f): wieczorna 3,26…3,57 × 5,00…5,06, do gniazda 3,28…3,44, narożnik r ≤ 46,88; poranna 3,35…3,79 × 5,00…5,06, do gniazda 3,45…3,47, narożnik r ≤ 46,59 (reguła R59: ≥ 3 od gniazd, w kole 47).
- Pliki: bazowe `ramka_plytka_okragla_ramkowa_<typ>_v2.stl` (4 dołki, bez cyfry) i warianty `_n1/_n2/_n3` (wieczorna), `_n4/_n5/_n6` (poranna); JSON `uklad_gniazd_okragla_ramkowa_<typ>.json` = jak okrągła + `magnet_pockets` (3 wpisy A/B/C z `angle_deg`), `cover_groove` {z, w, depth}, `key_slot` {angle_deg, r0, w, h}. Objętość 48,90 / 48,91 (wieczorna bazowa / n1–n3), 49,18 / 49,20 (poranna) [runda 2; runda 1: 49,19 / 49,20]; gabaryt 100 × 100 × 8 (warianty 8,6). Orientacja do druku: gniazdami do góry, spód płaski na stole (rowek klucza i kieszenie otwarte od spodu). Ilość 1 × n1…n6 (`quantities_r58`). PA12 naturalny biały, mat (drukarnia).
- Sprawdzenia: K‑01…K‑09, K‑11, K‑13, K‑16, K‑61 (b: na Z −4 i −7,5 promieniami równoległymi do osi ścięcia, odsuniętymi o ±4,9 — w osi leży rowek klucza do Z −3), K‑62 jak płytka okrągła; zamiast K‑63 sprawdzenie K‑64 (kieszenie, rowek pokrywki, rowek klucza, ścianki, sockets = kwadrat, obrys cyfry, mapa wierzchu), pasowania K‑67. Budowa i sprawdzenia: `--etap R58` (pliki etapów A–C nietknięte).

### 4.2 `ramka_pokrywka_v2.stl`
- Funkcja: osłona prac na czas przenoszenia; jedna na obie płytki.
- Gabaryt: (96 + 2·0,3 + 2·1,5) = 99,6 × 99,6 × (14 + 2 + 4) = 20 mm w STL (bez reliefu — R50‑U14); pionowe krawędzie R 3.
- Cechy: wnęka 96,6 × 96,6 × 18 (od dołu), wierzch 2 mm pełny; kołnierz 1,5 mm; 4 garby zatrzaskowe 10 (szer.) × 0,8 (wys. w Z) × 0,7 (występ), czubek półokrąg R 0,4 (`cover_snap_r`), na wewnętrznej stronie kołnierza, środek garbu 2 mm nad dolną krawędzią kołnierza (lokalnie Z −18 = rowek płytki 2 mm pod jej wierzchem), w położeniach R42 (lewy/prawy bok y = 0, przód x = +25, tył x = −25); wycięcie 30 × 3 na palec na dolnej krawędzi przedniego i tylnego boku. **[usunięte R50‑U17]** 6 otworów ø4 w wierzchu. **[usunięte R50‑U14]** napis „GÓRA” (druk FDM wierzchem w dół; góra jest oczywista — wierzch pełny, dół otwarty).
- Luzy: 0,3 na stronę do płytki; garb 0,7 w rowek 0,8.
- Rachunek wysokości: wierzch płytki 0 → najwyższa praca +10 (14 − 4) → prześwit 4 → spód wierzchu pokrywki +14 ✓.
- Orientacja: wierzchem w dół (największa płaska ściana). Ilość 4. **PETG FDM, druk własny (0,2 mm)**; nie w arkuszu drukarni.

### 4.2a `ramka_pokrywka_okragla_v2.stl` **[R58]** — pokrywka płytki okrągłej ramkowej
- Funkcja: osłona prac na płytce okrągłej ramkowej (4.1b) na czas przenoszenia; ta sama zasada co 4.2.
- Gabaryt: kubek średnica wewnętrzna 100 + 2 · 0,3 = 100,6, ścianka 1,5 (zewn. 103,6), wysokość 14 + 2 + 4 = 20; wierzch pełny 2 (bez otworów i napisów). W STL 103,6 × 103,6 × 20,0.
- Cechy: 4 garby zatrzaskowe na wewnętrznej ścianie, przekrój jak w 4.2 (występ 0,7, wysokość w Z 0,8, czubek półokrąg R 0,4), wyciągnięte PO ŁUKU o stałym przekroju na długości 10 mierzonej po licu wewnętrznym (±5,7°), środek Z −18 (2 nad dolną krawędzią kołnierza), kąty `round_cover_snap_angles` 25°, 155°, 205°, 335° — pary przy osi X (owalizacja wzdłuż X), omijają ścięcie płytki (−45° ± 9,2°; garb 335° kończy się 5,1° przed ścięciem) i wycięcia palcowe (±90° ± 17,4° na r 50,3). Wycięcia palcowe 30 × 3 na dolnej krawędzi z przodu (−90°) i z tyłu (+90°). **[runda 2, P2 recenzji; runda 3, P2 recenzji rundy 2]** Po obu stronach każdego garbu pionowa szczelina odciążająca przez kołnierz: szerokość `round_cover_slit_w` 1,0, od dolnej krawędzi w górę `round_cover_slit_h` 15 (Z −20…−5; runda 2: 12), zakończona otworem przelotowym ø`round_cover_slit_end_d` 2,0 o środku na osi szczeliny na Z −5 (kształt dziurki od klucza — zaokrąglony koniec zamiast ostrego naroża; górny koniec otworu Z −4,0, do spodu wierzchu Z −2 zostaje 2,0), środki `round_cover_slit_offset` ±6,5 po licu wewnętrznym od środka garbu (±7,4°) — 8 szczelin; garb siedzi na języku 12 × 15 × 1,5 (13 od nasady); od końca garbu do szczeliny 1,0 (do otworu 0,50 po kącie, ale otwór leży 12 wyżej niż garb), między szczelinami sąsiednich garbów ≥ 13,7°, od wycięć palcowych ≥ 39,1° (K‑66). Odkształcenie nasady języka z rachunku recenzenta: ok. 0,53 % nominalnie / 0,93 % w najgorszym przypadku (runda 2: 0,90 / 1,57 %) — **1 sztuka próbna przed serią**.
- Luzy: 0,3 promieniowo do płytki; garb wchodzi 0,4 w rowek 0,8 (do dna rowka zostaje 0,4; w Z 0,1 nad i pod garbem); dół kołnierza Z 6,5 nad ramą wkładki (Z 6,0) o 0,5 (K‑67). Pokrywka nie ma klucza — można ją założyć w dowolnym obrocie; garb nad ścięciem płytki nie zahacza (czubek r 49,6 > 49,356), zostają wtedy 3 garby. Siła zatrzasku do sprawdzenia na pierwszym wydruku FDM.
- Orientacja: wierzchem w dół. Ilość 4 (`quantities_r58`). **PETG FDM, druk własny**; objętość 25,06 cm³ (runda 2: 25,12; runda 1 bez szczelin: 25,26).
- Sprawdzenia: K‑01…K‑04b, K‑66 (średnice, wysokość, wierzch, 4 garby — kąt, występ, Z — wycięcia, 8 szczelin z otworem końcowym: szerokość, środek i ø otworu, górny koniec i odstęp do spodu wierzchu, rozłączność), K‑67 (na płytce; kołnierz w ustawieniach skrajnych).

### 4.3 `ramka_korpus_W_v2.stl`, `ramka_korpus_P_v2.stl`
- Funkcja: dno i ściany; niesie panel, Pi, gniazda tylne. Dwa pliki różnią się tylko napisem (Z28).
- Gabaryt: 200 × 200 × 59,6 (R50‑1; bez daszków, R50‑U4); ściany 2,5, dno 3, R 5 pionowe, R 3 dolna krawędź. Wnętrze 195 × 195.
- Cechy (globalne XYZ):
  1. 4 podkładki panelu w kształcie stadionu 9 szer. × 1 wys. na dnie (Z 3…4), oś wzdłuż przekątnej narożnika od (±55, ±55) do (±65, ±65) (`panel_slot_pitch_min/max` 110…130, R50‑2); w dnie pod każdą rowek przelotowy 3,6 szer. [R53: było 3,4] o tej samej osi (długość 14,1 + 3,6 = 17,7); bez pogłębienia (R50‑U20: wkręt M3 × 10 z podkładką ø9 od spodu, łeb 2,5 pod dnem, stopki 4). Dystans 50 F‑F na podkładce (R50‑7). Wzór otworów panelu niekwadratowy lub z offsetem → wiercenie ø4 w dnie w zmierzonym miejscu + podkładka R50‑8 (fallback bez nowego korpusu).
  2. 4 bossy Pi ø8 × 5 (R48) na dnie, osie: (−46,5, −24,5), (11,5, −24,5), (−46,5, 24,5), (11,5, 24,5) (R50‑6); otwór ø2,1 × 5 pod wkręt M2,5 formujący gwint (R49, bez wkładek).
  3. **[usunięte R50‑U6]** Szczelina SD w dnie.
  4. 2 szczeliny wlotowe w dnie 30 × 4, środki (−8, ±10) (R50‑U19, R50‑6).
  5. Szczeliny wylotowe 12 × 3 **bez daszków** (R50‑U4): tylna ścianka 4 szt., środki x = −54, −18, 18, 54, Z = 8; lewa i prawa ścianka po 3 szt., y = −36, 0, 36, Z = 8 (R50‑U19).
  6. Tylna ścianka: kieszeń DC — okno 51 × 24 (x −93…−42, Z 14…38, naroża ostre R50‑U15) i skrzynka za nim: zewnętrznie x −97,5…−40 (lewa ściana skrzynki = lewa ściana korpusu), y 78…100, Z 12…40, ściany 2, wnętrze otwarte tylko przez okno (R50‑4); **w prawej ścianie skrzynki** (płaszczyzna x = −40, ściana −42…−40) otwór gniazda DC ø12, oś (y 89, Z 30) wzdłuż X (R50‑3; gniazdo ø8 przez tulejkę 4.9); okno USB 16 × 9 w (60, Z 24) + 2 rowki poziome 3,2 × 5,7 o osiach od (60 ± 11,5) do (60 ± 14), Z 24 (R50‑5; rozstaw flanszy 23…28; rowek x 44,4…50,1 i 69,9…75,6 → ścianka do okna 1,9) (R10); 2 otwory ø3,6 [R53: było 3,2; luz 0,3/stronę] z pogłębieniem stożkowym ø6,3 / 90° pod wkręt M3 w (±75, Z 55) (wkręty blatu, R7, R50‑1).
  7. Przednia ścianka: gładka, bez otworów (Z28); tylko napis relief 0,6 „RAMKA WIECZORNA” (W) / „RAMKA PORANNA” (P), litery 8 mm, środek (0, Z 51) (`label_pos_z` = korpus_h − 8,6).
  8. Kieszenie zatrzasków blatu (R6): 4 szt., 11 × 3,5 × 1,3 od wewnątrz [R53: było 10 × 2,5 × 1,0], Z 52,1…55,6 (`snap_pocket_z` = korpus_h − 7,5); ściana za kieszenią 1,2 lokalnie (odstępstwo od 4.8, nienośne, [R53] T2b); lewa ściana y = 0, prawa ściana y = 0, przednia ściana x = +50, tylna ściana x = −50.
  9. **[usunięte R50‑U8]** Bossy uchwytów kabli. Zamiast nich: podstawki opasek samoprzylepne 20 × 20 (lista zakupów) na dnie przy lewej ścianie (trasa DC) i przy tylnej ścianie (Hall); płytka proto Halla na taśmie VHB na lewej ścianie Z 40.
  10. **[usunięte R50‑U16]** Gniazda stopek; stopki samoprzylepne na płaskim dnie, środek 12 od krawędzi.
  11. **[usunięte R50‑U5]** Żebra dna.
- Orientacja: dnem w dół. Ilość: 1 W + 1 P. PA12 grafit. Powierzchnie zewnętrzne pod wygładzanie (wariant pokazowy).

### 4.4 `ramka_blat_v2.stl`
- Funkcja: górna płyta z oknem i kieszenią dyfuzora, nosi wkładkę (rama dyfuzora usunięta, R50‑U1).
- Gabaryt: 200 × 200 × 4 + kołnierz 10 w dół = 14; R 5 pionowe, R 1,5 górna krawędź. Położenie globalne: wierzch Z 63,6, kołnierz do 49,6 (R50‑1); geometria lokalna bez zmian.
- Cechy:
  1. Kieszeń dyfuzora 162 × 162 × 2 od góry (środek 0,0), otwór przelotowy 158 × 158; naroża kieszeni ostre (R50‑U15; pleksi bez fazowania, R29 uchylone).
  2. Kołnierz: obrys 193,6 × 193,6 (195 − 2·0,7; luz 0,7 na stronę = ±0,3 korpus + ±0,3 blat + zapas, R48, [R53] T1), grubość 2, wysokość 10, R 4,3; 4 haczyki zatrzaskowe 8 szerokie, występ 1,5 (96,8 → 98,3; zahacza 0,8 w ścianie 97,5, luz do dna kieszeni 98,8 = 0,5, [R53] T2), grubość ramienia 1,5, w położeniach R6 (lewa/prawa y = 0, przednia x = +50, tylna x = −50); występ haczyka zajmuje lokalnie Z −10,75…−8,75 (globalnie 52,85…54,85, `snap_hook_z`, `snap_hook_hgt` 2,0; luz 0,75 w kieszeni korpusu Z 52,1…55,6 [R53] T3, R47, R50‑1) z rampą naprowadzającą od dołu; nacięcia `snap_notch_w` 1 mm po obu stronach każdego haczyka od dolnej krawędzi kołnierza (lokalnie −14) do lokalnie −5 (ramię `snap_hook_arm_l` 9 mm, 1 mm nasady pod płytą).
  3. 2 słupki 8 (X) × 6 (Y) × 10 po wewnętrznej stronie tylnego kołnierza: x ±71…79 (R48), y 89,2…95,2 (zrośnięte z kołnierzem 95,0…97,0 po R48), lokalnie Z −14…−4 (R7, R47); otwór ø2,5 × 6 pod wkręt M3 formujący gwint (R49, R49a) poziomo (oś Y) od zewnętrznego lica kołnierza y 96,8 (po R48, [R53] T1) do 90,8, dno 1,6 ≥ 1,5, oś lokalnie Z −8,6 (globalnie 55 = `blat_screw_z`); wkręt M3 × 8: 2,5 w ścianie + 0,7 luzu + 4,8 w gwincie [R53]. Zostają (R50‑U2 odrzucone przez właściciela).
  4. **[usunięte R50‑U1]** 4 bossy ø8 × 6 pod spodem w (±90, ±90) (rama dyfuzora). Spód blatu poza kołnierzem i słupkami płaski.
  5. Otwory kołków wkładki ø3,4 [R53: było 3,3; pasowanie ruchome 0,2] ślepe 3,8 głębokie od góry w (±58, 93,5) (R8); kieszenie magnesów ø5,4 × 2,3 od góry w (±58, 86); szczeliny kabli 4 (X) × 8 (Y) przelotowe w (±66, 90).
  6. Bez żebra obwodowego pod blatem (R41); sztywność daje kołnierz 10 mm.
- Rachunek „wkładka w oknie blatu”: rama wkładki 104,8 × 104,8 leży na dyfuzorze 160 → margines 27,6 mm wolnego dyfuzora z każdej strony [R53]; uszy (y 52,4…96) leżą częściowo na dyfuzorze (do y = 81) i częściowo na blacie (dyfuzor licowany z blatem, R30); kołki, magnesy i szczeliny kabli (y 86…94) leżą w litym blacie poza kieszenią (y > 81) i poza słupkami (x ±71…79) ✓.
- Łączy się z: korpus (kieszenie zatrzasków, wkręty tylne), dyfuzor (kieszeń), wkładka (kołki, magnesy, szczeliny).
- Orientacja: wierzchem w dół. Ilość 2. PA12 grafit.

### 4.5 `ramka_rama_dyfuzora_v2.stl` — usunięta [R50‑U1]
Brak pliku. Panel ustalają 4 dystanse M3 w jego otworach (±0,2); światło i pył z krawędzi panelu trafiają tylko do wnętrza obudowy (korpus zamknięty, luz kołnierza blatu 0,7 [R53] to zamierzony wylot D14). Bez pianki ani innego uszczelnienia (decyzja właściciela). Bossy ramy w blacie usunięte (4.4.4).

### 4.6 `ramka_wkladka_v2.stl`
- Funkcja: gniazdo płytki, nośnik 3 czujników Halla i kołka orientacji.
- Gabaryt: rama 104,8 × 104,8 × 6 + 2 uszy (x ±51…65) do y = 96 → obrys 130 × 148,4 [R53: było 104,6 / 148,3]; wysokość z kołkiem orientacyjnym 7,5 i kołkami ustalającymi 3,5 pod spodem = 11,0 w STL; Z lokalne: spód ramy 0 (na dyfuzorze).
- Cechy:
  1. Otwór 96,8 × 96,8 [R53: było 96,6; luz płytki 0,4/stronę], naroża wewnętrzne ostre (R50‑U15); ścianka 4 szeroka, 6 wysoka, górna krawędź wewnętrzna faza 1 × 45° (naprowadzenie płytki).
  2. 4 półki narożne 12 × 12 × 2,5 wewnątrz otworu (naroża A, B, C, D), górna powierzchnia Z 2,5.
  3. Półki A, B, C: kieszeń przelotowa 5,0 × 5,5 (X × Y), środek pod osią magnesu płytki: A (−42, −42), B (−42, 42), C (42, 42); kanał 2,5 × 1,0 (R20) od kieszeni do ścianki ramy po przekątnej narożnika, pod półką (otwarty od dołu); w ściance ramy przelot 2,5 szer. × 1,5 wys. od spodu, po przekątnej narożnika od (−48,4, −48,4) do (−52,4, −52,4) [R53] (analogicznie B i C) — **jedna bryła tnąca ciągła z rowkiem zewnętrznym** (ten sam przekrój 2,5 × 1,5, R50‑U9).
  4. Półka D (42, −42): kołek 4,4 × 4,4 × 5 (nad półką), ścianki zewnętrzne kołka 0,6 od ścian otworu [R53] T6c (kołek w (45,6, −45,6) — położenie jak przed R53; luz do wycięcia płytki 0,4 bez zmian); wierzchołek sfazowany 1 mm.
  5. Wycięcie palcowe 30 × pełna wysokość w przednim boku ramy (x ∈ [−15, 15], y = −48,4 … −52,4 [R53]).
  6. Rowek kablowy 2,5 szer. × 1,5 wys. (R50‑U9; `wire_rabbet_w` × `wire_rabbet`) na zewnętrznej dolnej krawędzi lewego, tylnego i prawego boku (od A do ucha lewego; od C do ucha prawego; B wprost do ucha lewego); od x 52,4 do 49,9 → do otworu 48,4 zostaje 1,5 ✓ [R53]; 3 żyły AWG 28 ø0,9: 2 obok + 1 nad.
  7. Uszy: 14 × 43,6 × 3, od y = 52,4 do 96 [R53], środki x = ±58 (x ±51…65); **nasada ucha w kształcie L** (R47, U‑1, poprawka R51): płytka 3 mm grubości, Z 0…3: część wewnątrz obrysu ramy x ±(44…52,4), y 48,8…58 (zakładka 8,4 × 3,6 × 3 ze ścianką tylną) + część na pasie tylnym x ±(52,4…65), y 52,4…58 [R53] T6b; NIC poza obrysem ramy dla y < 52,4 (prawy pas marginesu odsłonięty, K‑56); kołek ø3 × 3,5 w dół w (±58, 93,5) jako jedna bryła: walec ø3 × 3,0 + stożek ścięty ø3 → ø2 na ostatnich 0,5 (R50‑U10); otwór ø5,4 przelotowy w (±58, 86); kanał kablowy 2 × 1,2 od spodu: pod nasadą od rowka tylnego boku ramy do x = ±64, dalej pod uchem wzdłuż x = ±64 od y = 52,4 do 90, wylot na krawędzi zewnętrznej ucha nad szczeliną blatu (±66, 90). Spód ramy i uszu (Z 0…3) jako jeden obrys, góra ramy (Z 3…6) jako pierścień.
  8. Bez napisu „PRZÓD” (R51: litery 2 mm nie dają trzonu ≥ 1,0 — nieczytelne; orientację wymusza kołek). Zostaje strzałka ku −Y: trójkąt ▼ `insert_arrow_l` 2 (Y) × `insert_arrow_w` 3 (X), relief 0,6, na obu segmentach przedniego boku: środki (−32, −51,15) i (32, −51,15).
- Luzy i rachunek „płytka we wkładce”: 96 + 2·0,4 = 96,8 ✓ [R53] T6 (płytka ±0,29 + wkładka ±0,29 → najgorzej 0,1 luzu zamiast 0); powtarzalność ±0,4 (luz) ≤ ±0,5 wymagane ✓; kołek 4,4 w wycięciu 5 (0,5 od ścian) nadal blokuje obrót; kalibracja gniazdo → diody toleruje ±1,25 (kołek dociska płytkę do narożnika D przy ułożeniu).
- Magnes–czujnik: D5, 1,7 mm ≤ 4 ✓.
- Orientacja: spodem w dół. Ilość 2 + 1 zapas. PA12 naturalny biały.

### 4.6a `ramka_wkladka_okragla_v2.stl` **[R58]** — wkładka pod płytkę okrągłą ramkową
- Funkcja: gniazdo płytki okrągłej ramkowej (4.1b) w tym samym blacie; nośnik 3 czujników Halla i żebra klucza (runda 2). Korpus i blat bez zmian.
- Jak 4.6 (IDENTYCZNE, K‑65 i): obrys zewnętrzny ramy 104,8 × 104,8 × 6, uszy z nasadą L, kołki ustalające, otwory magnesów uszu, rowek kablowy 2,5 × 1,5 na lewym, tylnym i prawym boku, kanały pod uszami, strzałki ▼ — więc blat, margines matrycy (K‑56: nic poza obrysem ramy dla y < 52,4) i magnesy uszu bez zmian.
- Różnice:
  1. Otwór: koło ø(100 + 2 · `round_insert_clearance` 0,4) = 100,8 ze ścięciem — płaszczyzna prostopadła do kierunku −45° w odległości 49,356 + 0,4 = 49,756 (materiał wkładki wypełnia odcinek koła), na całej wysokości; faza 1 × 45° na górnej krawędzi całego obrysu otworu (koło + ścięcie). Ścianka ramy w osiach (lewo, prawo, tył) 52,4 − 50,4 = 2,0 ≥ 1,5 (4.8) — świadomie cieńsza niż 4 w kwadracie.
  2. Półka (Z 0…2,5): ciągły występ od obrysu otworu do promienia `round_insert_ledge_r` 47 + 4 kwadratowe półki `round_insert_shelf` 10 × 10 (boki równoległe do osi) o środkach w osiach A, B, C, D na r 45, przycięte do otworu. Od krawędzi najdalszego otworu ø3 płytki do występu 5,58 / 5,34 ≥ 3; od półek do otworów ø3 ≥ 3,10.
  3. Kieszenie Halla przelotowe 5,0 × 5,5 (X × Y) o środkach w osiach A, B, C (= osie magnesów płytki; K‑67: odchyłka 0,000); kanał wyprowadzeń po przekątnej na zewnątrz: pod półką 2,5 × 1,0 od kieszeni do okręgu otworu (r 50,4; nad kanałem 1,5 występu), dalej przelot 2,5 × 1,5 przez pełny narożnik do naroża zewnętrznego — jedna bryła ciągła z rowkiem kablowym (K‑65 j: sondy co 0,5 od każdej kieszeni do szczeliny przy uchu bez przerwy). Dno w osi po rowku kablowym 52,4 − 2,5 − 47 = 2,9.
  4. **[runda 2, B1 recenzji — zamiast kołka ø3 × 2]** Żebro klucza na osi D (kierunek ścięcia −45°): szerokość styczna `round_key_rib_w` 3,0; promieniowo od `round_key_rib_r0` 46,5 do lica ścięcia wkładki 49,756; poniżej Z 6 zrośnięte ze ścianą ścięcia (faza otworu za żebrem wypełniona — jedna bryła); **[runda 3, P1 recenzji rundy 2]** powyżej Z 6 kończy się promieniowo na `round_key_rib_top_r1` 49,2 (runda 2: na licu ścięcia 49,756 — kołnierz pokrywki przy płytce przesuniętej o luz 0,4 i pokrywce o 0,3 od strony żebra schodzi na osi żebra do r 49,6 i siadał na żebrze); wysokość `round_key_rib_h` 4,5 nad półką (Z 2,5…7,0 = 1,0 nad wierzchem wkładki, jak kołek kwadratowej 7,5); faza `round_key_rib_chamfer` 1,0 na górnych krawędziach (oba boki, czoło wewnętrzne i — runda 3 — krawędź zewnętrzna części górnej; wierzch 1,0 × 0,7, u 47,5…48,2); w rzucie zapas do lica kołnierza w najgorszym ustawieniu 0,40 na osi żebra, 0,375 na narożach żebra, odstęp 3D kołnierz–żebro 0,62 (K‑67); stoi na półce D i występie; bez kołka kwadratowego `orient_post`. Żebro (część dolna) sięga r 49,756, a kieszeń magnesu płytki kończy się na r 47,6 — w żadnym obrocie i przesunięciu w luzie się w niej nie mieści (płytka w złym obrocie leży na żebrze 4,5 nad półką; runda 3 bez zmian: uniesienie 4,48).
  5. Wycięcie palcowe z przodu 30, pełna wysokość, także przez występ (od krawędzi przedniej do okręgu występu na x ±15, y −44,54; bryła tnąca kończy się w wolnym otworze, y −44,04); nie narusza półek A i D.
- Gabaryt: 130 × 148,4 × 10,5 w STL (najwyżej wierzch żebra klucza Z 7,0; kołki ustalające 3,5 pod spodem); objętość 22,45 cm³ (runda 3: 22,446; runda 2: 22,448; runda 1 z kołkiem: 22,42). Orientacja: spodem w dół. Ilość 3 (`quantities_r58`). PA12 naturalny biały (drukarnia).
- Sprawdzenia: K‑01…K‑04b, K‑65 (otwór i ścięcie, występ, półki, kieszenie Halla, żebro klucza, ścianka w osiach, wycięcie palcowe, K‑56, zgodność obrysu / uszu / kołków / magnesów z wkładką kwadratową — sondy K‑29, K‑30 i mapy wysokości, ciągłość kanałów kablowych), K‑67 (płytka we wkładce, pokrywka nad wkładką).

### 4.7 Głowica czujnika gestu — usunięta (Z28)
Brak pliku. Brak otworów w przedniej ściance.

### 4.8 Zaślepka otworu przycisku — usunięta (Z28)
Brak pliku; otworu przycisku nie ma.

### 4.9 `ramka_uchwyt_kabli_v2.stl` — usunięty [R50‑U8]; zamiast niego `ramka_tulejka_dc_v2.stl` i `ramka_podkladka_panelu_{05,1,2}_v2.stl`
- Uchwyt kabli: brak pliku. Wiązki trzymają podstawki opasek samoprzylepne 20 × 20 (6 szt., lista zakupów), płytka proto Halla 30 × 20 przyklejona taśmą VHB do lewej ściany korpusu na Z 40 (PA12 przemyć IPA przed klejeniem).
- `ramka_tulejka_dc_v2.stl` (R50‑3): tulejka redukcyjna gniazda DC — walec ø`dc_bush_outer_d` 11,85 (R52) × `dc_bush_t` 2 z otworem ø`dc_bush_inner_d` 8,2 i kołnierzem ø`dc_bush_flange_d` 15 × `dc_bush_flange_t` 1 po stronie kieszeni; wciskana w otwór ø12 ściany skrzynki (pasowanie celowo wciskowe 0,075/stronę, [R53] T7), nakrętka gniazda ø8 dociska ścianę + tulejkę. Używana tylko gdy pomiar #16 da gwint ø8. [R53] Drukować dopiero po zmierzeniu otworu w gotowym korpusie (otwór MJF może wyjść 11,7…11,9, W‑11): `dc_bush_outer_d` = zmierzony otwór − 0,15, przebudowa tulejki generatorem. Orientacja: kołnierzem w dół. Ilość 2. Żywica w firmie / PETG, druk własny.
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
| Dołki kodu (R3) | (−45,0, −36/−33/−30) ø2: do krawędzi płytki 48 − 46,0 = 2,0; do rowka pokrywki (x od −47,2, Z −1,5…−2,5): √(1,2² + 0,5²) = 1,3 → po przekątnej 1,3 ≥ 1,5? NIE przy −45,5 (0,86), TAK przy −45,0 w rzucie poziomym 1,2 + dołek kończy się na Z −1, rowek zaczyna na Z −1,5 → materiał między nimi 1,3 mm w najkrótszym kierunku (lokalnie, nie ścianka nośna, R47); do stożka A (−42, −42) ø5: √(3² + 6²) − 2,5 − 1 = 3,2; do gniazda wieczornej R2 (−36, −28,5) ø9: √(9² + 1,5²) − 4,5 − 1 = 3,6; do gniazda porannej R2 (−36,75, −30,75) ø7,5: √(8,25² + 0,75²) − 3,75 − 1 = 3,5 | ✓ ([R54] stożek A przesunięty do (−35,5, −26,5) / (−34,5, −28): dołek–znacznik 6,62 / 7,19, dołek–gniazdo 9,77 / 11,56; [R59] stożek A (−35,5, −26,5) / (−30,5, −32): dołek–znacznik 6,01 / 11,03, dołek–gniazdo 8,27 / 8,61 — D6) |
| Słupki blatu i szczeliny kabli (R7, R47, R48) | słupki x ±71…79, y 89,2…95,2 (po wewnętrznej stronie kołnierza, nie w ścianie korpusu); szczeliny x ±64…68, y 86…94 → 3 mm odstępu; kieszenie magnesów ø5,4 w (±58, 86) → 10,3 mm od słupka | ✓ |
| Haczyki blatu a kieszenie korpusu (R47, R50‑1, [R53] T2/T3) | występ Z 52,85…54,85 w kieszeni Z 52,1…55,6 → 0,75 luzu z każdej strony (≥ ±0,3 + ±0,3); czubek 98,3 w kieszeni do dna 98,8 → luz 0,5, zahaczenie 0,8 w ścianie 97,5; haczyk 8 w kieszeni 11 → 1,5 na stronę; poniżej kieszeni haczyk nie wchodzi w ścianę | ✓ |
| Nasada ucha wkładki (R47, R51, [R53] T6b) | nasada L: x 44…52,4 od y 48,8, x 52,4…65 od y 52,4, Z 0…3 ze ścianką tylną ramy; nie zasłania pasa przedniego ani prawego | ✓ |
| Koło pola skanowania (R54, Z29; układ R59) | `socket_zone_r` = 100/2 − 1,5 − 1,5 = 47; **[R59]** wieczorna: max promień obrysu 45,93 (ø15 w (±18, 33,95)), ø12 w (±37,5, −13,7) 45,92, rynienka 45,16; poranna: 46,41 (ø12,5 w (±15,5, 37,05)), rynienka 46,35 (koniec (±18,5, −35,3)), ø12,5 w (±38,75, −6,1) 45,48; znaczniki: promień środka 44,30 / 44,20 / 44,43 (wieczorna) i 44,21 / 44,25 / 44,48 (poranna) ≤ 44,5, ścianka znacznik–gniazdo 3,52 / 3,23 / 3,19 i 3,45 / 3,02 / 3,48; min ścianka gniazdo–gniazdo 3,00 (oba typy); dołek kodu–gniazdo 8,27 / 8,61 ≥ 3; dołek–znacznik 6,01 / 11,03 ≥ 1,5; kwadrat: max (\|x\| + r, \|y\| + r) = 43,5 / 45,0 ≤ 45. Układ R54: 46,39 / 46,93 (rynienka tylna porannej); układ sprzed R54: 54,9 / 52,6, znaczniki 61,9 (poza 50) | ✓ |
| Płytka okrągła (R57, Z30; układ R59) | ø100: krawędź R 50; **[R59]** obrys górny gniazd do krawędzi (okrąg i ścięcie): do ściany pionowej wieczorna 4,07 (ø15 w (±18, 33,95), r 45,93), poranna 3,59 (ø12,5 w (±15,5, 37,05), r 46,41); do początku fazy (R − 0,5) 3,57 / 3,09; stożki znaczników: 50 − 44,43 − 2,5 = 3,07 / 50 − 44,48 − 2,5 = 3,02; dołki: wieczorna promień 43,73, do rynienki 4,80, do krawędzi 5,27; poranna promień ≤ 43,93, do gniazd 3,55, do stożka 2,09, do krawędzi 5,07; ścięcie (cięciwa 16): 49,356 od środka (głębokość 0,644 ≥ 0,6), ścianka do obrysów: wieczorna 4,59 (koniec rynienki: rzut (22,5, −30,2) na −45° = 37,27 + 7,5 = 44,77), poranna 4,81 (koniec rynienki: rzut (18,5, −35,3) = 38,04 + 6,5 = 44,54) ≥ 3. Układ R54: do ściany 3,61 / 3,07, ścięcie 3,68 / 4,87. Przy ø96 (układ R54): 1,61 / 1,07 i 1,20 / 1,07 (< 1,5); przy ø98: 2,61 / 2,07 — odrzucone przez nadzór na rzecz ø100 | ✓ |
| Strzałki ▼ a kołnierz pokrywki (R47, R51) | relief do Z 6,6 (70,2 globalnie) na y −50,0…−52,3; kołnierz pokrywki y −48,3…−49,8, dół 70,1 → bez nakładania (wiersz „Napis PRZÓD” zastąpiony) | ✓ |
| Uchwyty kabli (R43) | **[usunięte R50‑U8]** — podstawki opasek samoprzylepne, bez bossów | — |
| Rama dyfuzora a bossy blatu (R44) | **[usunięte R50‑U1]** — bez ramy i bossów | — |
| Garby pokrywki a wycięcia palcowe (R42) | wycięcia x −15…15 na przodzie i tyle; garby przód x 20…30, tył x −30…−20 | ✓ |
| Płytka we wkładce ([R53] T6) | 96 + 2 × 0,4 = 96,8; wycięcie 5 vs kołek 4,4: w STL kołek stoi 0,6 od ściany otworu, tj. 0,5 od ściany wycięcia po stronie narożnika (4.6.4) → luz 0,4 na stronę otwartą (trzecie oko, R52; bez zmian po R53); położenie płytki ustala otwór 96,8, nie kołek | ✓ (powtarzalność ±0,4 ≤ ±0,5) |
| Wkładka w oknie blatu | rama 104,8 < dyfuzor 160 [R53]; uszy do y = 96 < wnętrze kołnierza 96,8 (R48, [R53] T1); kołki i magnesy na litym blacie (y 86–93,5, poza kieszenią 81) | ✓ |
| Magnes–czujnik | 0,2 + 1,0 + 0,5 = 1,7 ≤ 4 | ✓ |
| Odsłonięty margines | 32 − 0,4 − 4 = 27,6 mm = 11 pełnych pikseli [R53]; przód i prawy bok bez uszu | ✓ |
| Płytka okrągła ramkowa [R58] | kieszenie ø5,2 w osiach na r 45: do krawędzi 50 − 45 − 2,6 = 2,4; ścianki 3D z siatki (K‑64 d): kieszeń – wnętrze ≥ 1,85; rowek klucza 3,6 × 5,0 od r 46 (runda 2) – wnętrze 2,68 / 6,36; dno rowka pokrywki – wnętrze 2,72 / 2,68 (do stożka C; do gniazd 3,55 / 3,08); rowek klucza – rowek pokrywki 0,5 tylko w pasku 0,156 przy ścięciu (informacyjnie); w ścięciu rowek pokrywki ma 0,156 głębokości | ✓ (K‑64) |
| Płytka okrągła we wkładce okrągłej [R58] | 100 + 2 × 0,4 = 100,8; ścięcie 49,356 + 0,4 = 49,756; spód płytki na występie r 47…50 i półkach (Z 2,5); **[runda 2]** żebro 3,0 w rowku 3,6 → 0,3/stronę, czoło 46,5 − 46,0 = 0,5, nad żebrem 5,0 − 4,5 = 0,5; oś magnesu nad osią kieszeni Halla (obie r 45); żebro sięga 49,756 − 47,6 = 2,16 poza kieszeń magnesu → w złym obrocie płytka leży na żebrze (okno płaskie −0,75…+0,75°, poza nim uniesienie 4,48, przechył 2,61° — runda 2: 2,59°); ścięcie nie blokuje (0,244 < 0,4); **[runda 3]** część żebra nad wierzchem wkładki do r 49,2 (faza 1,0 na krawędzi zewnętrznej): lico kołnierza w najgorszym ustawieniu 50,3 − 0,4 − 0,3 = 49,6 → zapas w rzucie 0,40 na osi żebra (z siatek 0,375 na narożach żebra), odstęp 3D 0,62; ustawienia skrajne 8 × 8 kierunków bez kolizji | ✓ (K‑67) |
| Wkładka okrągła [R58] | ścianka w osiach 52,4 − 50,4 = 2,0 ≥ 1,5; dno w osi po rowku 52,4 − 2,5 − 47 = 2,9; nad kanałem pod występem 2,5 − 1,0 = 1,5; margines matrycy i uszy jak 4.6 (obrys ramy bez zmian) | ✓ (K‑65) |
| Pokrywka okrągła [R58] | 100 + 2 × 0,3 = 100,6; garb 0,7 w rowku 0,8 (zagłębienie 0,4, do dna 0,4); dół kołnierza 8 + 2,5 − 4 = 6,5 nad ramą 6,0 → 0,5 ≥ 0,4; garby 25/155/205/335° ±5,7° poza ścięciem (±9,2° od −45°) i wycięciami (±17,4° od ±90°); **[runda 2]** 8 szczelin 1,0 przy garbach, od końca garbu 1,0, od wycięć ≥ 39,1°; **[runda 3]** szczeliny 1,0 × 15 z otworem końcowym ø2,0 (środek Z −5, górny koniec Z −4 → do spodu wierzchu 2,0 ≥ 1,5), język 12 × 15 × 1,5 | ✓ (K‑66, K‑67) |
| Pokrywka nad pracą | 14 − 4 + 4 = 14 mm prześwitu nad płytką | ✓ |
| Zasady 4.8: ścianki | najcieńsze: kołnierz pokrywki 1,5; ramię zatrzasku 1,5; półka nad kanałem 2,5 − 1,0 = 1,5 (R20); ściana korpusu za kieszenią zatrzasku 2,5 − 1,3 = 1,2 lokalnie (R6, [R53] T2b — odstępstwo od „≥ 1,5” przyjęte świadomie: 4 pola 11 × 3,5, nienośne, przednia ma dodatkowo relief +0,6; alternatywa zahaczenie 0,4 odrzucona); dno słupka blatu pod otworem wkrętu 1,6 [R53]; dno blatu pod ślepym otworem kołka 0,2 (R8; dopuszczalne lokalnie — to nie ścianka nośna, a otwór może przebić się na wylot bez szkody) | ✓ |
| Zasady 4.8: otwory | najmniejszy ø2 (dołki kodu) ≥ 1,5 | ✓ |
| Zasady 4.8: relief | 0,6 | ✓ |
| Zasady 4.8: luzy ([R53]) | zasada R53: luz nominalny ≥ suma tolerancji obu części w danym kierunku (MJF/SLS ±0,3 na każdej), chyba że pasowanie jest celowo wciskowe. Ruchome: 0,4 płytka we wkładce, 0,7 kołnierz blatu na 195 mm (R48), 0,75/0,75 haczyk w kieszeni (Z), 0,5 czubek–dno, 1,5 boczny, ø3,6 przelot wkrętu blatu, 0,2 kołek ø3 wkładki w ø3,4 (zmiana klasy z wciskanego 0,15); 0,3 pokrywka na płytce (FDM, skalowanie pierwszej sztuki, interfejs płytki poza R53). Celowo wciskowe: tulejka DC 11,85 w ø12 → 0,075/stronę (R52, druk własny po pomiarze otworu). Magnesy 0,1–0,2 | ✓ |
| Zasady 4.8: pustki | korpus, blat, pokrywka otwarte; kieszenie magnesów i kanały kabli otwarte od spodu | ✓ |
| Zasady 4.8: gwinty (R49, R49a) | bez wkładek; wkręty formujące gwint w PA12: otwór ø2,5 pod M3/PT3,0 w słupkach blatu (głęb. 6, dno 1,6 [R53]), ø2,1 pod M2,5/PT2,5 w bossach Pi (głęb. 5); ścianki wokół otworu ≥ 2,75 (bossy ø8, słupek 8 × 6). Proces ([R53] T8): przed pierwszym wkręceniem przewiercić ø2,1 / ø2,5 (proszek MJF w otworach), krok 7 sekcji 9 | ✓ |
| Kanały kabli wkładki (R50‑U9) | rowek 2,5 × 1,5 na zewnętrznej dolnej krawędzi: od 52,4 do 49,9 → do otworu 48,4 zostaje 1,5 [R53]; nad rowkiem 4,5 ramy; 3 żyły ø0,9: 2 obok (1,8 < 2,5) + 1 nad (1,5) | ✓ |
| Wentylacja (R50‑U19) | wylot 10 szczelin × 36 = 360 mm² + luz kołnierza blatu 0,7 × 800 = 560 mm² [R53]; wlot 2 × 30 × 4 = 240 mm²; 10–13 W w 200 × 200 × 64 → Pi < 70 °C (krok 14) | ✓ |
| Gniazda wieczornej [R59] | 5 wpisów rzędów: wysokości 15 + 12 + 15 + 15 + 15 = 72, blok y −37,7…41,45 = 79,15 ≤ 90 (rzędy przesunięte „w szachownicę” zachodzą na siebie w y); najszerszy rząd 87/90 (ø12 ×6 i ø15 ×5); w pasach narożnych rynienka 60 i rząd ø15 ×3 51 ≤ 70 | ✓ |
| Gniazda porannej [R59] | 8 wpisów rzędów (6 rzędów, w tym 2 mieszane): blok y −41,8…43,3 = 85,1 ≤ 90; najszerszy rząd 90/90 (ø12,5 ×6: 77,5 + 12,5); w pasach narożnych rynienka 50 i rząd ø12,5 ×3 43,5 ≤ 70 | ✓ |
| Kieszeń DC w korpusie (R50‑3, R50‑4) | skrzynka x −97,5…−40, y 78…100, Z 12…40: podkładka‑stadion panelu (−55…−65, 55…65) → y ≤ 68,2 (9,8 zapasu); szczeliny lewej ściany (y ±36, Z ≤ 9,5) i tylnej (x −54, Z ≤ 9,5) pod skrzynką (2,5 zapasu); kołnierz blatu od Z 49,6 (9,6 zapasu); wkręt blatu (−75, Z 55) 15 nad skrzynką; kieszeń zatrzasku tylnego (x −50, Z 52,1 [R53]) nad skrzynką; okno x −93…−42 kończy się 4,5 od narożnika wewn. (−97,5, 97,5) | ✓ |
| Gniazdo DC w ścianie skrzynki (R50‑3) | ściana x −42…−40, pole y 80…97,5 × Z 14…38; otwór ø12 w (89, 30): Z 24…36 → 2 do sufitu wewn.; nakrętka ø15 (y 81,5…96,5, Z 22,5…37,5) na ścianie ✓; wtyk ø11 w świetle: Z 24,5…35,5 ⊂ 14…38, y 83,5…94,5 ⊂ 80…97,5 ✓; wtyk kątowy 26 od lica −42 → −68 vs ściana korpusu −95,5 (27,5 zapasu); wtyk prosty 40 + zagięcie 12 → −94 ✓; korpus gniazda w +X od −40: wolne do x 52 (gniazdo USB) = 92 | ✓ |
| Kieszeń zatrzasku a napis | kieszeń przednia x 44,5…55,5, Z 52,1…55,6 (od wewnątrz) [R53]; napis x −55…55, Z 47…55 (relief na zewnątrz); ściana 2,5 − kieszeń 1,3 = 1,2 + relief 0,6 = 1,8 → bez nakładania (R6, R47(17), [R53] T2b) | ✓ |
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
| Podkładki panelu (4) | stadion wzdłuż przekątnej od (±55, ±55) do (±65, ±65) (R50‑2); po pomiarze słupek staje w zmierzonym punkcie rowka | stadion 9 szer. × 1; w dnie rowek przelotowy 3,6 szer. [R53] o tej samej osi, bez pogłębienia (R50‑U20) | — (R5) |
| Dystanse panelu (4) | na podkładkach | M3 F‑F 50 mm, wkręt M3 × 10 + podkładka ø9 od spodu; góra: wkręt dociskowy M3 × 5 w gwint panelu (bez gwintu: tulejka F‑F ø5 × 5 klejona + dystans 45) (R50‑7) | — |
| Bossy Pi (4) | (−46,5, ±24,5), (11,5, ±24,5) (R50‑6) | ø8 × 5, otwór ø2,1 × 5 | M2,5 formowany (R49) |
| Bossy uchwytów kabli (2) | **[usunięte R50‑U8]** — podstawki opasek samoprzylepne 20 × 20 na dnie | — | — |
| Słupki blatu (2, w kołnierzu blatu) | x ±71…79, y 89,2…95,2, oś otworu Z 55 (R50‑1) | 8 × 6 × 10, otwór poziomy ø2,5 × 6 od lica 96,8 (R49a, [R53]; dno 1,6) | M3 formowany (R7, R47, R48, R49) |
| Bossy ramy dyfuzora (4, pod blatem) | **[usunięte R50‑U1]** | — | — |
| Kieszenie zatrzasków blatu (4) | lewa/prawa y = 0, przednia x = +50, tylna x = −50; Z 52,1–55,6 (R50‑1, [R53]) | 11 × 3,5 × 1,3 [R53: było 10 × 2,5 × 1,0] | — (R6) |

Prowadzenie kabli:
1. Zasilanie: gniazdo DC w prawej ścianie skrzynki kieszeni (x −40, y 89, Z 30; nakrętka od wnętrza, korpus gniazda w +X) → przewód 2 × 1 mm² 25 cm → wtyk DC → gniazdo Bonnetu; z zewnątrz wtyk kątowy zasilacza wchodzi w kieszeń w −X, kabel wychodzi przez okno. Trasa po dnie wzdłuż tylnej i lewej ściany, podstawka opaski samoprzylepna.
2. HUB75: Bonnet → kabel taśmowy 16‑pin 150 mm → HUB75 IN panelu (złożony płasko pod panelem, nad Bonnetem; luz Z 34–42).
3. Zasilanie panelu: terminal śrubowy Bonnetu → kabel VH4 panelu (w zestawie) → panel.
4. Hall: 3 × 3 żyły AWG 28 od wkładki przez szczeliny blatu (±66, 90) → wzdłuż tylnej ściany → płytka proto na taśmie VHB na lewej ścianie (Z 40) → JST 5‑pin → Dupont do listwy na Bonnecie.
5. USB serwisowe: gniazdo panelowe (60, tył, Z 24) → kabel 30 cm → USB‑A Pi (górny lewy port). Odbiornik klawiatury: dolny lewy port USB Pi; jeśli zasięg < 3 m przez obudowę → przedłużacz 20 cm przyklejony rzepem do lewej ściany na Z 40.
Długości kabli: wszystkie ≤ 300 mm; zapas pętli 50 mm przy blacie, żeby blat dało się zdjąć i odłożyć obok bez odpinania Halla (złącze JST na płytce proto pozwala odpiąć).

Wentylacja: patrz D14. Powietrze wchodzi szczelinami w dnie pod Pi (konwekcja od radiatora Pi), wychodzi szczelinami w ścianach Z 8 (4 tył + 3 na bok, bez daszków — R50‑U4, R50‑U19) i przez szczelinę między panelem a ścianami do przestrzeni pod blatem — blat nie jest szczelny na kołnierzu (luz 0,7, R48, [R53]), co daje wylot górny.

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
| 6 | Części z druku: oględziny, wypłukanie proszku, próba pasowania na sucho: płytka we wkładce, wkładka na blacie, pokrywka na płytce, blat na korpusie. | Przed próbą: pomiar suwmiarką wg checklisty odbioru („Zakupy i druk”); odchyłka > ±0,5 mm = reklamacja [R53]. Płytka wchodzi i wychodzi bez siły, luz wyczuwalny ok. 0,4 mm na stronę (do ok. 1 mm łącznie) [R53]; pokrywka trzyma po odwróceniu; blat zatrzaskuje się i daje się zdjąć ręką. |
| 7 | Gwinty (R49, bez wkładek): [R53] T8 najpierw przewiercić otwory wiertłem ø2,1 (korpus: 4 × Pi) i ø2,5 (blat: 2 × słupki) — usuwa proszek MJF i zarośnięcie otworu (−0,1…−0,2); potem każdy otwór ø2,5/ø2,1 przegwintować raz „na sucho” wkrętem PT (albo M3/M2,5) wkręcanym wkrętakiem, wolno, bez dokręcania na siłę: korpus (4 × Pi), blat (2 × słupki). | Wkręt wchodzi bez oporu i trzyma; gwint nie wyrobiony po 3 cyklach. |
| 8 | Montaż Pi + Bonnet na bossach (NAJPIERW wpiąć wtyk DC kabla wewnętrznego w gniazdo Bonnetu — przy kierunku −X jest tylko 7,5 mm do ściany, R52), listwa kątowa dolutowana do pinów 1, 3, 4, 5, 9, 17, 19, 22, 24, 26, 35, 39 Bonnetu. Panel (R50‑7): z gwintem — wkręty dociskowe M3 × 5 wkręcone 2,5 w otwory panelu, dystanse F‑F 50 nakręcone; bez gwintu — tulejki F‑F ø5 × 5 doklejone epoksydem do spodu PCB (centrowanie śrubą M3 × 10 przez otwór, wyjąć po utwardzeniu), dystanse F‑F 45 + wkręty dociskowe. Panel postawiony na podkładkach‑stadionach tak, by dystanse trafiły w rowki, 4 wkręty M3 × 10 z podkładkami ø9 od spodu. Przy wzorze otworów poza rowkami: wywiercić ø4 w dnie w zmierzonym miejscu, podkładka R50‑8 pod dystans. | Stos Pi nie dotyka spodu panelu (szczelina ≥ 2 mm, sprawdzić szczelinomierzem/kartą); panel równoległy do dna (różnica < 0,5 mm na rogach); nic nie wystaje od strony diod. |
| 9 | Dyfuzor w kieszeni blatu (rogi pleksi bez fazowania, R50‑U15), próba zamknięcia blatu na korpusie z panelem. | Blat zamyka się do końca; okno równo nad panelem (przesunięcie < 1 mm); PCB panelu nie dotyka spodu blatu. |
| 10 | Wkładka: czujniki Halla wklejone w kieszenie półek (lico do góry, kropla CA na bok obudowy, nie na lico), przewody w rowkach, wyprowadzenie przez uszy i szczeliny blatu do płytki proto. Magnesy w uszach i blacie (najpierw sprawdzić przyciąganie, potem CA). | Wkładka siada na kołkach i trzyma magnesami (nie przesuwa się przy pchnięciu palcem); płytka testowa wchodzi na kołek orientacyjny tylko w jednej orientacji. |
| 11 | Magnesy w płytkach wg kodów: nr 1 (A), 2 (B), 3 (A+B), 4 (C), 5 (A+C), 6 (B+C); biegun S w dół; CA. | Skrypt odczytu pokazuje 1…6 dla każdej płytki, 0 bez płytki, odczyt stabilny 60 s, zmiana < 100 ms po położeniu. |
| 12 | Okablowanie końcowe (gniazdo USB panelowe wkręcić PRZED montażem panelu — od wnętrza ma 14,3 mm do dystansu (60, 60), R52): gniazdo DC (przez okno kieszeni w otwór prawej ściany skrzynki; przy gwincie ø8 najpierw tulejka redukcyjna — drukowana po zmierzeniu otworu ø12 w gotowym korpusie, [R53] T7; nakrętka kluczem 14 od góry), USB panelowe (rowki; przy flanszy z otworami pionowymi wywiercić 2 × ø3,2), podstawki opasek samoprzylepne (PA12 przemyć IPA), płytka proto na VHB, opaski, opisy kabli; odbiornik klawiatury w porcie USB (P), stopki samoprzylepne 12 od krawędzi. | Żaden kabel nie dotyka diod ani radiatora; blat daje się zdjąć i odłożyć obok bez rozpinania; obudowa stoi stabilnie; wtyk DC nie wystaje poza obrys. |
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
| 12 | Skaner Aidite **[R54]**: średnica koła wokół osi stolika widocznego w CAŁYM obrocie — makieta kartonowa 96 × 96 z narysowanymi okręgami ø90, ø94, ø100 (środek płytki) i 4 rogami; skan pełną ścieżką bez przechyłu; odczytać największy okrąg widoczny w całości w siatce. Kryterium: ≥ 100 → `scan_field_d` 100, układ D6 bez zmian; < 100 → wpisać wynik, `socket_zone_r` maleje, D6 przeliczyć `narzedzia/uklad_kolo_R54.js` (przy < ~94 wraca wariant płytki okrągłej, R54) | T | scan_field_d | 100 | ______ |
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
| Tulejka DC, podkładki panelu | 1 + 3 | 2 + 24 | ~5 | druk własny (PETG FDM, kolega) [R55] | — |
| **Razem drukarnia** | | | ~1 033 | **935–1 655 zł** | **1 235–2 180 zł** |

**[R59]** Tabela powyżej to szacunek sprzed R54 (płytki „62 / 61”) i nie jest przeliczana; obowiązuje arkusz zamówienia `R59_arkusz_zamowienia.md` (objętości z siatek STL układu R59): drukarnia 10 pozycji × ilości — 1008,05 cm³, wariant najtańszy 907–1613 zł, pokazowy 1216–2161 zł; z płytkami okrągłymi n8 i n9 (12 pozycji) — 1107,05 cm³, 996–1771 zł i 1305–2320 zł; płytki kwadratowe: wieczorna 59,66 cm³/szt. (n1–n3 razem 178,98), poranna 59,94–59,95 cm³/szt. (n4–n6 razem 179,84).

Największy koszt to korpus (ok. 40 %). Jeśli wycena przekroczy budżet: zmniejszyć `wall_t` do 2,0 i `floor_t` do 2,5 (−15 % korpusu) albo zamówić korpus w SLS zamiast MJF (często taniej dla dużych brył). Objętości korpusu i blatu są szacunkiem po R50 (+10 cm³ za 5 mm wysokości, −3 za daszki/żebra/bossy; blat −2 za bossy ramy) — obowiązują wartości z `arkusz_zamowienia`.

---

## 12. Przekazanie do wykonawcy (dawna „sesja 2”)

Wykonawca pracuje według `prompt_wykonawca.md`, recenzent według `prompt_recenzent.md`, właściciel według `00_PRZEPLYW_I_BRAMKI.md`. Ta sekcja definiuje wyłącznie listę plików wynikowych i sprawdzenia; wszystko inne jest w tamtych plikach.

### 12.1 Pliki wynikowe (R2, R16) — folder `wyniki_v2/`

| # | Plik | Treść | Etap |
|---|---|---|---|
| 1 | `ramka_generator.py` (w folderze głównym `Ramki/`, nie w `wyniki_v2/`) | jeden skrypt bpy: wczytuje `parametry.json` i `wyniki_v2/json/uklad_gniazd_*.json`, czyści scenę, buduje wszystkie części, eksportuje, liczy objętości, pisze arkusze, renderuje, uruchamia własne sprawdzenia; uruchomienie: `blender -b -P ramka_generator.py -- --etap A|B|C|ALL` | A |
| 2 | `wyniki_v2/json/uklad_gniazd_wieczorna.json`, `wyniki_v2/json/uklad_gniazd_poranna.json`, **[R57]** `uklad_gniazd_okragla_wieczorna.json`, `uklad_gniazd_okragla_poranna.json` | układ gniazd (struktura 4.1 / 4.1a); generowane z D6 przy pierwszym uruchomieniu, potem czytane | A |
| 3 | `wyniki_v2/stl/ramka_plytka_wieczorna_v2.stl`, `…_poranna_v2.stl` (bazowe) oraz `…_wieczorna_n1_v2.stl` … `_n3_v2.stl`, `…_poranna_n4_v2.stl` … `_n6_v2.stl`; **[R57]** `ramka_plytka_okragla_wieczorna_v2.stl`, `…_okragla_poranna_v2.stl` (bazowe) oraz `…_okragla_wieczorna_n8_v2.stl`, `…_okragla_poranna_n9_v2.stl` | płytki (kwadratowe i okrągłe, 4.1a) | A |
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
| 17 | **[R58]** `wyniki_v2/stl/ramka_plytka_okragla_ramkowa_wieczorna_v2.stl`, `…_poranna_v2.stl` (bazowe), `…_wieczorna_n1_v2.stl` … `_n3_v2.stl`, `…_poranna_n4_v2.stl` … `_n6_v2.stl`, `ramka_wkladka_okragla_v2.stl`, `ramka_pokrywka_okragla_v2.stl`; `wyniki_v2/json/uklad_gniazd_okragla_ramkowa_wieczorna.json`, `…_poranna.json`; raport `raport_wykonawcy_R58_iter<n>.md` | komplet okrągły do ramki (4.1b, 4.2a, 4.6a); osobny tryb `--etap R58` / `--etap R58_SPRAWDZ` — buduje i sprawdza tylko te pliki, pliki etapów A–C tylko czyta (odniesienie) | R58 |

Nie powstaje: `legenda_klawiatury.svg`, `ramka_podstawka_*.stl` (Z26), `ramka_glowica_*.stl`, `ramka_zaslepka_*.stl` (Z28), `ramka_rama_dyfuzora_v2.stl` (R50‑U1), `ramka_uchwyt_kabli_v2.stl` (R50‑U8).

### 12.2 Sprawdzenia
Pełna lista sprawdzeń z identyfikatorami K‑01…K‑60, metodą, tolerancją i wagą: `protokol_weryfikacji_v2.md`. Wykonawca wykonuje wszystkie sprawdzenia własnym kodem w `ramka_generator.py` (etap `--etap SPRAWDZ`) i raportuje je w raporcie; recenzent wykonuje te same sprawdzenia własnym, niezależnie napisanym skryptem na plikach z `wyniki_v2/`, nie czytając kodu wykonawcy przed pomiarem.

### 12.3 Kwestie rozstrzygnięte z góry (dawniej „do rozstrzygnięcia przez sesję 2”)
Wszystkie dawne kwestie otwarte są rozstrzygnięte w sekcji 13: font R22, żebra R23, daszki R24, promienie R26, kolory R27, kolejność id R13, garby pokrywki R21, nazwy kolekcji R16. Wykonawca nie ma kwestii do rozstrzygnięcia; każde odstępstwo zgłasza w rejestrze odstępstw raportu i NIE wdraża go bez zatwierdzenia na bramce, chyba że jest to poprawka błędu wykrytego sprawdzeniem K‑xx — wtedy wdraża i opisuje.

---

## 13. Rejestr rozstrzygnięć (R1…R59, R50‑1…R50‑8, R50‑U1…R50‑U20, A‑1…A‑9)

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
| R53 | Audyt 31.10 (DESIGN A 1.2 T1–T16, WYKONALNOŚĆ W‑04, DESIGN B §3.3): luzy w plikach ciaśniejsze niż tolerancja MJF/SLS ±0,3 na każdej z dwóch części naraz; korpus W+P i blat nie zamówione (D‑3), więc poprawka przed zamówieniem. Zasada: luz nominalny ≥ suma tolerancji obu części w danym kierunku, chyba że pasowanie jest celowo wciskowe. | **(T1)** `blat_skirt_clearance` 0,5 → **0,7** (kołnierz 193,6 w 195; lico 96,8, R 4,3; dno otworu słupka 90,8 → dno 1,6 ≥ 1,5, gwint wkrętu 4,8). **(T2)** `snap_hook_h` 1,3 → **1,5** (czubek 98,3 bez zmian, zahaczenie 0,8 utrzymane); `snap_pocket_depth` 1,0 → **1,3** (dno kieszeni 98,8, luz czubek–dno 0,5; ściana za kieszenią **1,2 lokalnie** — odstępstwo od 4.8, 4 pola 11 × 3,5 nienośne, przednia ma +0,6 reliefu). **(T3)** `snap_pocket_h` 2,5 → **3,5**, `snap_pocket_z` = korpus_h − 7,5 = **52,1** (kieszeń Z 52,1…55,6, występ 52,85…54,85 → luz Z **0,75/0,75**, dawniej 0,25 — przy −0,1 rampa siadała na krawędzi kieszeni i blat stał nad ścianą); `snap_pocket_w` 10 → **11** (luz boczny 1,5). **(T4)** `blat_screw_hole_d` 3,2 → **3,6** (przelot M3 coarse; luz 0,3 = ±0,3 + ±0,3 położenia w X na rozstawie 150; pogłębienie 6,3 bez zmian; rowek odrzucony — błąd jest w X). **(T5)** `blat_pin_hole_d` 3,3 → **3,4** — kołek ø3 wkładki: klasa **ruchome 0,2** zamiast „wciskane 0,15” (otwory MJF −0,1…−0,2; część zdejmowana codziennie; trzymają magnesy). **(T6)** `insert_opening` 96,6 → **96,8** (luz płytki 0,4/stronę: płytka ±0,29 + wkładka ±0,29 → najgorzej 0,1 zamiast 0; powtarzalność ±0,4 ≤ ±0,5; interfejs płytki bez zmian; rama 104,8, gabaryt wkładki 130 × 148,4, margines matrycy 27,6 → 11 px); `tab_root_x_out` 52,3 → **52,4** (= krawędź ramy); `orient_post_gap` 0,5 → **0,6**, żeby kołek orientacyjny został w (45,6, −45,6) jak przed R53 — przy 0,5 przesuwał się z otworem o 0,1 i jego naroże (47,9) zahaczało o R 1,5 wnęki pokrywki o 0,059 mm (wykryte kopią trzeciego oka; K‑53 generatora z kurczeniem 0,05 tego nie widzi). DESIGN B §3.3 p. 1 („96,6 zostaje”) rozstrzygnięte na korzyść zasady R53. **(T12)** `panel_slot_w`, `panel_screw_hole_d` 3,4 → **3,6** (rowek pod M3 dystansu; MJF −0,1…−0,2). **Bez zmian (jawnie):** T7 tulejka 11,85 w ø12 — **celowo wciskowe**, druk własny z żywicy po pomiarze otworu w gotowym korpusie (W‑11); T8 otwory ø2,1/ø2,5 pod wkręty formujące — geometria OK, proces: przewiercić przed pierwszym wkręceniem (krok 7, dokument osobno); T9 wypaczenie — specyfikacja zamówienia i odbiór (dokument osobno); T13 `cover_clearance` 0,3 — pokrywka FDM druk własny ze skalowaniem pierwszej sztuki, większy luz zmniejszyłby zahaczenie garbu 0,4 w rowku płytki (interfejs płytki poza R53); T10/T11/T14–T16 bez zmian; W‑04 kryterium odbioru „reklamacja ±0,3” → > ±0,5 (dokument osobno). **Nie zmienione:** 63,6 / 59,6 / 50, położenie Pi, pole skanowania, interfejs płytki, pokrywka. **Pliki:** przebudowane blat, korpus W, korpus P, wkładka; 13 pozostałych STL bajtowo identyczne z `archiwum/wyniki_v2_przed_R53_2026-10-31/`. Sondy protokołu dopasowane (K‑23, K‑27, K‑32, K‑42, K‑56 z parametrów; opisy K‑30, K‑35, K‑39, K‑46, K‑47, K‑49, K‑60, tabela 1). Tabela 3 i opisy 4.x: wartości sprzed R53 — obowiązują wartości z `parametry.json` (do naniesienia przez nadzór; generator zgłasza odstępstwa informacyjne „tabela 3 planu”). Projekt i weryfikacja: `sesje_2026-10-31/poprawki_pasowan/R53_projekt.md`, `weryfikacja_R53.md`. | [FAKT] |
| R54 | Właściciel 1.11: przy obrocie stolika skanera prace z gniazd skrajnych wychodzą poza pole skanowania. Przyczyna: przy obrocie wokół osi pionowej pole „[cytat usuniety]” koło (promień 50 przy polu ø100), a nie kwadrat 100 × 100 — dawny układ sięgał promienia 54,9 (wieczorna) / 52,6 (poranna), stożki znaczników w rogach 61,9, narożniki płytki 67,9. Rozważane: (1) ten sam obrys 96 × 96, gniazda i znaczniki w kole; (2) płytka okrągła ø96–100; (3) mniejszy kwadrat ~76. | **Wybrane (1).** BEZ ZMIAN: obrys płytki 96 × 96 × 8, wycięcie D, dołki kodu, numer, kieszenie magnesów w rogach, rowek pokrywki; wkładka, pokrywka, korpus, blat, czujniki Halla, panel, Pi. NOWE: Z29 (`scan_field_d` 100 DO_ZMIERZENIA — pomiar #12 przeformułowany; `scan_center_tol` 1,5; `work_overhang` 1,5 → `socket_zone_r` 47 LICZONE). D6 przeliczone (rzędy przycięte do koła, rynienki z przodu i z tyłu, największe gniazda w najszerszych cięciwach; przegląd wszystkich kolejności rzędów skryptem): wieczorna 18 + 2 (7 × ø9, 6 × ø12, 5 × ø15; blok y −39…39), poranna 31 + 2 (18 × ø7,5, 7 × ø10, 6 × ø12,5; dwa rzędy ø7,5 w szachownicę). Stożki znaczników przeniesione do koła, osobno dla typu: `ev_marker_pos` A (−35,5, −26,5) B (−35,5, 26,5) C (35,5, 26,5); `mo_marker_pos` A (−34,5, −28) B (−30, 32,5) C (30, 32,5) (promień ≤ 44,5, ścianka do gniazd ≥ 3; wspólne pozycje dla obu płytek nie mieszczą się — sprawdzone). Z4 uchylone (`marker_offset` 6 opisuje teraz tylko kieszenie magnesów), Z20 zastąpione, R40 bezprzedmiotowe. Protokół: K‑05 (a) 18/2 i 31/2 z `ev_/mo_rows`, (c) dodatkowo obrys w kole 47; K‑09 pozycje z JSON + kontrola odwrotna dawnych rogów; K‑16 znacznik–gniazdo ≥ 3, promień znacznika ≤ 44,5, znacznik–dołek ≥ 1,5. Wykonawca (etap A/B płytek, nowa iteracja + recenzja): `uklad_pochodne` czyta `*_marker_pos` (magnesy nadal z `marker_offset`), `sprawdz_uklad_json` liczy oczekiwane liczby z `ev_/mo_rows` i sprawdza koło, K‑09/K‑16 z JSON; stare `wyniki_v2/json/uklad_gniazd_*.json` do archiwum i usunięcia (skrypt odtworzy je z `ev_/mo_rows`); nowe STL płytek n1–n6 + bazowe; wkładka/pokrywka/korpus/blat bez zmian plików. Po plikach do aktualizacji: dokument stanowiska i „[cytat usuniety]” (24/35 → 18/31 i opis układu), `kody_plytek.md`/arkusze, model 3D i animacja, pakiet `Ramki_pakiet/`. Lista edycji: `R54_wdrozenie_zmiany.md`; narzędzia: `narzedzia/uklad_kolo_R54.js`, `narzedzia/weryfikuj_uklad_R54.js`. Odrzucone (2) i (3): wymagają nowej wkładki (otwór okrągły, półki jako wycinki, kołek i magnesy na przekątnych) i nowych pokrywek przy tej samej pojemności; (2) wraca, gdy #12 da pole < ~94. Koszt pojemności: −25 % wieczorna, −11 % poranna. | [ZAŁOŻENIE, zatwierdzone przez właściciela 1.11; `scan_field_d` DO_ZMIERZENIA #12] |
| R55 | Właściciel 1.11: „[cytat usuniety]”; wybór: wszystko, co własne, na FDM PETG u kolegi. | Drukarka żywiczna wycofana z planu. Druk własny (FDM PETG, kolega): pokrywka ×4, tulejka DC ×2, podkładki panelu 3 × 8, płytka testowa n1 do testu skanera, prototypy pasowań. Zamawiane (PA12): bez zmian — korpus W/P, blat, wkładka ×3, płytki n1–n6 (bez alternatywy żywicznej). `materials`: tulejka i podkładki → „[cytat usuniety]”, płytki wieczorne → „[cytat usuniety]”. Tulejka ø11,85 na FDM: wciskowe 0,075/stronę może nie wyjść — po wydruku sprawdzić w otworze ø12 korpusu; przy luzie/zacisku skalować XY w slicerze (±1 % ≈ ±0,12 mm), bez zmiany pliku. Podkładki 0,5 mm: FDM warstwa 0,1–0,2 → 3–5 warstw, dopuszczalne. Płytka testowa z PETG białego matowego (bez połysku). Pakiet: folder `03_Druk_wlasny/Zywica` → `03_Druk_wlasny/PETG_FDM`; dokumenty stanowiska i zakupów: usunąć ustawienia druku żywicy i koszt żywicy, `00_PRZEPLYW_I_BRAMKI.md` §11a dopisek. Geometria plików bez zmian. | [FAKT, decyzja właściciela 1.11] |
| R56 | Właściciel 1.11 (wieczór): dokumenty stanowiska mają opisywać stan, nie historię ani terminy; wykluczenia i powody w jednym miejscu; firmy przy pozycjach do zamówienia. | Tylko dokumenty, geometria i STL bez zmian. (1) „[cytat usuniety]”: bez ram czasowych (daty, tygodnie, „[cytat usuniety]”, godziny pracy) — zostają kolejność, warunki i bramki; usunięta sekcja „[cytat usuniety]”; wykluczenia zastąpione odnośnikiem; kolumna „[cytat usuniety]” z firmami. (2) „[cytat usuniety]”: zwięźlej (38,8 → 30,3 tys. znaków), bez dat i bez zapisów „[cytat usuniety]”, nowa sekcja „[cytat usuniety]” (drukarnie PA12: Cadxpert, Spes3D, P3DRC, Send3D, Laboratorium Druku 3D, zapas Xometry; pleksi: PlasticExpress, Plexigo, eplexi24, Plexinet; źródło `dostawcy_druk_i_pleksi.md`), sekcje „[cytat usuniety]” i „[cytat usuniety]” usunięte (treść w nowym dokumencie). (3) NOWY dokument „[cytat usuniety]” (.md + PDF): każdy element — jak jest, dlaczego, czy można zmienić, co to wymusza; tabela wszystkiego, z czego zrezygnowano (przycisk, czujnik gestu, wkładki gwintowane i grot, podstawka klawiatury, rama dyfuzora, uchwyty kabli, pianki i uszczelki, daszki, żebra, szczelina SD, żywica, projektor, NFC, szkło…). (4) Skrypt `narzedzia/buduj_plan_wdrozenia.py`: strona tytułowa „[cytat usuniety]” = data i godzina budowy, „[cytat usuniety]” na tytułowej i w stopce każdej strony, profil „[cytat usuniety]”. (5) Plan wdrożenia zał. B: rama wkładki 104,8 (było 104,6 sprzed R53). `00_PRZEPLYW_I_BRAMKI.md` §11–12 oznaczone jako historyczne. Pakiet `Ramki_pakiet` R56. Kopie sprzed: `archiwum/*_przed_dokumenty_R56_2026-11-01.*`. | [FAKT, decyzja właściciela 1.11] |
| R57 | Właściciel 2.11: zamówienie płytek OKRĄGŁYCH (wieczorna + poranna) jako drugiego wariantu do testu skanera; dołki kodu kwadratu leżą poza polem ø100 (promień 54–58); kod 3‑bitowy ma wolne tylko n7 i n0. Nadzór (plan sesji 2.11, sekcja 2) przyjął ZAŁOŻENIA: ø96 z fazą jak kwadrat, ścięcie orientacyjne o cięciwie 8 na −45°, dołki A/B/C/D w kole (promień ≤ 44, ≥ 3 od gniazd, ≥ 1,5 od stożków, „[cytat usuniety]”), 4. bit D także na kwadracie (−45, −27), numeracja n8 = D / n9 = A + D, cyfra w kole albo pominięta, bez kieszeni magnesów i rowka, pliki 15 z R56 bajtowo bez zmian. | Wykonawca R57‑A (2.11): generator `ramka_generator.py` z typami `okragla_wieczorna` / `okragla_poranna` (ten sam układ gniazd — K‑05 h), nowe klucze `parametry.json` (`plate_round_d`, `round_flat_w`, `round_flat_angle`, `code_bit_d_pos`, `code_dimples_round`, `number_pos_round`, `plate_numbers_round`), Z30, D11 (4 bity), 4.1a, 4.11, 12.1, protokół (K‑05 h, K‑08/K‑09/K‑11/K‑13/K‑16 uwagi, nowe K‑61/K‑62/K‑63, sekcja 3a, tabela 1, K‑58/K‑59), 4 STL + 2 JSON w `wyniki_v2/`, `--etap SPRAWDZ` 0 NIE, 15 plików R56 identyczne (n1–n6 bez bitu D; wkładka przywrócona po znanej różnicy znaku zera). Wykonawca zgłosił: przy ø96 ścianka obrysu rynienki tylnej porannej i stożków do krawędzi 1,07 (do fazy 0,57) < 1,5; cięciwa 8 daje głębokość 0,16 (niewidoczne po druku); brak wspólnej linii 4 dołków w kole r 44 (lewa krawędź zajęta przez gniazda do x −45). DECYZJE NADZORU 2.11 (ZAŁOŻENIA do zatwierdzenia przez właściciela): (1) **ø100 = granica pola skanowania; gniazda jak R54 w kole 47** (nie 96, nie 98; ścianka do krawędzi 2,57; kwadrat ma rogi na promieniu 67,9, więc ø100 mieści się w skanerze wszędzie tam, gdzie kwadrat); (2) **cięciwa ścięcia 16** (głębokość 0,644 ≥ 0,6; warunek: ścianka od płaszczyzny ścięcia do obrysów ≥ 3 — 3,68 / 4,87; 20 odpada, ścianka 1,3); (3) **dołki per typ** zaakceptowane (wieczorna y −43,5 przód‑środek, ścianki 3,50 / do krawędzi 5,27; poranna x 30,5 przód‑prawo, 3,62 / 4,87); (4) **cyfra w kole 47** zaakceptowana ((35, −26,5) / (36,5, −24,5)); (5) pliki bazowe kwadratowe dostały dołek D (bajty zmienione; n1–n6 nie). K‑61 rozszerzone o (e) głębokość ścięcia ≥ `round_flat_depth_min` 0,6 i (f) ściankę ścięcie–obrysy ≥ 3. Lista edycji: `R57_wdrozenie_zmiany.md`; raport `wyniki_v2/raport/raport_wykonawcy_R57_iter1.md`. Recenzja R57‑B i dokumenty/pakiet R57‑C — osobne sesje. | [ZAŁOŻENIE nadzoru 2.11 — do zatwierdzenia przez właściciela: ø100, cięciwa 16, dołki per typ, cyfra w kole] | **ZATWIERDZONE przez właściciela 2.11.2026 (po recenzji R57‑B ZALICZONY): ø100, cięciwa 16, dołki per typ, cyfra w kole, bit D (n8/n9).**
| R58 | Właściciel 19.11.2026: zamówienie płytek OKRĄGŁYCH pod produkt końcowy, czyli leżących na ramce (zarezerwowana zmiana „[cytat usuniety]”). Decyzje zamknięte: (1) pełny komplet — płytki okrągłe z magnesami i rowkiem pokrywki + okrągła wkładka + okrągła pokrywka, korpus i blat bez zmian; (2) numery jak kwadratowe: n1–n3 wieczorne, n4–n6 poranne (ramka czyta 3 magnesy A/B/C, program ramki bez zmian); dzisiejsze n8/n9 zostają płytkami testowymi skanera (ich pliki bez zmian); (3) średnica 100 zostaje (pole skanowania niezmierzone — ryzyko przyjęte przez właściciela). Projekt luzów koordynatora: `narzedzia/studium_R58.py` (0 błędów). | Wykonawca R58‑A (19.11): typy `okragla_ramkowa_wieczorna` / `okragla_ramkowa_poranna` (4.1b: bryła i wierzch jak okrągła; kieszenie magnesów ø5,2 × 2,2 w osiach A/B/C na r 45; rowek pokrywki 1,0 × 0,8 na całym obwodzie; rowek klucza 3,6 od spodu na −45°), wkładka okrągła (4.6a: otwór ø100,8 ze ścięciem 49,756, występ r 47 + 4 półki 10 × 10, kieszenie Halla w osiach A/B/C, klucz na osi D; obrys ramy, uszy, kołki, magnesy, rowek kablowy jak 4.6), pokrywka okrągła (4.2a: ø100,6 / 103,6 × 20, 4 garby po łuku na 25/155/205/335°, wycięcia 30 × 3). Nowe klucze `parametry.json` (ZAŁOŻENIE, źródło R58): `round_magnet_r`, `round_key_slot_w/r0/h`, `plate_numbers_round_frame`, `round_cover_snap_angles`, `round_insert_clearance`, `round_insert_ledge_r`, `round_insert_shelf`, `round_key_rib_w/r0/h/chamfer` (runda 2, żebro klucza zamiast kołka z rundy 1), `round_key_rib_top_r1` (runda 3), `round_cover_slit_w/h/offset` (runda 2; runda 3: `round_cover_slit_end_d`), `quantities_r58`, `materials_r58` (osobno od `quantities`, żeby arkusz zamówienia R59 i K‑57 zostały bez zmian). Generator: tryb `--etap R58` / `R58_SPRAWDZ` (buduje i sprawdza tylko 10 STL + 2 JSON; 21 STL i 4 JSON R59 bajtowo bez zmian; `--etap SPRAWDZ` starych plików 0 NIE). Protokół: tabela 1, K‑64…K‑67, uwagi w K‑60, K‑61, K‑63. Lista edycji i SHA: `R58_wdrozenie_zmiany.md`. **Runda 2 (recenzja R58 runda 1: B 1 / P 3 / D 8):** (B1) kołek klucza ø3 × 2 na r 45 wchodził w pustą kieszeń magnesu ø5,2 × 2,2 (ten sam promień, co 90°), a ścięcie nie blokuje obrotu (wnikanie 0,244 < luz 0,4) — płytka leżała płasko obrócona o 90/180/270° i ramka czytała zły numer; decyzja koordynatora: żebro klucza na osi D przy ścięciu 3,0 × (r 46,5 … lico ścięcia 49,756) × 4,5 nad półką, faza 1,0, poniżej Z 6 zrośnięte ze ścianą (`round_key_rib_*` zamiast kluczy kołka rundy 1), rowek płytki r0 43 → 46,0, wysokość 2,5 → 5,0; K‑67 przerobione: przeszukanie obrotu 0…360° co 0,25° × przesunięcia w kole luzu co 0,1 mm dla każdej z 8 płytek (z siatek) — płytka leży płasko tylko w oknie −0,75…+0,75°, poza nim leży na żebrze (uniesienie 4,48, przechył 2,59°); ta sama metoda na geometrii rundy 1 odtwarza okna przy 90/180/270° (kontrola czułości). (P1) zamknięte rachunkiem (okno, przechył). (P2) 8 szczelin odciążających 1,0 × 12 przy garbach pokrywki (`round_cover_slit_*`). (P3) przebiegi A/B/C/ALL nie kasują plików R58 (`wyczysc_wyniki` pomija `rdzenie_R58`). (D1) wyjątek K‑60 tylko dla zrzutu bez żadnego klucza R58; (D2, D3) ścianki K‑64 (d) i kołnierz K‑67 z siatek (ścianki 3D). **Runda 3 (recenzja R58 runda 2: B 0 / P 2 / D 6; płytki bez zmian):** (P1) kołnierz pokrywki (lico r 50,3, dół Z 6,5) przy płytce przesuniętej o luz 0,4 i pokrywce o 0,3 od strony żebra schodził do r 49,6 i siadał na części żebra nad wierzchem wkładki (do 49,756, wnikanie 0,16) — ta część kończy się teraz na `round_key_rib_top_r1` 49,2 z fazą 1,0 także na krawędzi zewnętrznej (poniżej Z 6 bez zmian); K‑67: kołnierz w ustawieniach skrajnych (płytka w luzie × pokrywka o luz, 8 × 8 kierunków, każda płytka) — 0 kolizji, odstęp 3D kołnierz–żebro 0,62, w rzucie 0,375…0,40; geometria rundy 2 tą samą metodą daje kolizję (kontrola czułości); okno płytki −0,75…+0,75° bez zmian. (P2) szczeliny pokrywki 15 (`round_cover_slit_h`, było 12) z otworem końcowym ø2,0 (`round_cover_slit_end_d`), górny koniec 2,0 pod spodem wierzchu; 1 sztuka próbna przed serią. (D3) wpis R58 i lista zmian poprawione; (D2) ostrzeżenie programu ramki przy numerze niezgodnym z rolą ramki — wymaganie dla paczki programu. | [ZAŁOŻENIE — decyzje właściciela 19.11.2026; wymiary wg studium koordynatora; runda 2 i 3: decyzje koordynatora po recenzji] |
| R59 | Właściciel 14.11: na płytce porannej mniej małych gniazd (ø7,5), w ich miejsce większe, w tym ø15; na wieczornej więcej ø15; na obu jedna rynienka zamiast dwóch; pytanie o dwa krótsze mosty w jednej rynience. Liczb docelowych nie podał — studium R59‑U (`R59_propozycja_ukladu.md`: warianty W‑a/b/c, P‑a/b/c oraz rodziny P‑d i P‑e; `narzedzia/uklad_kolo_R59.js`, `narzedzia/weryfikuj_uklad_R59.js`) i wybór na bramce G0. (Numer R58 był zarezerwowany dla wkładki i pokrywki płytki okrągłej — wpis R58 z 19.11.2026 wyżej.) | **Decyzje właściciela 14.11.2026 (G0):** wieczorna W‑b = 6 × ø12 + 12 × ø15 = 18 gniazd + 1 rynienka 60 × 15 (y −30,2); poranna P‑e (wg szkicu właściciela) = 20 × ø12,5 + 3 × ø15 = 23 gniazda + 1 rynienka 50 × 13 (y −35,3), bez ø7,5 i ø10, dwa rzędy mieszane; rynienka jedna długa z 4 otworami jak dotąd (D3‑a: jedna praca na rynienkę; dwie krótkie rynienki odrzucone, „[cytat usuniety]” odłożone — zmiana programu); stare płytki fizyczne z układem R54 będą jeszcze skanowane (D4 — program stanowiska zachowuje stary układ, sesja R59‑P); numery płytek bez zmian (D5‑A: n1–n3, n4–n6, n8, n9); `quantities` bez zmian (D6: decyzja o zamówieniu po odbiorze). Wykonawca R59‑A (14.11): `parametry.json` — wartości `ev_rows`, `mo_rows`, `ev_marker_pos` (B, C), `mo_marker_pos` (A, B, C), `code_dimples_round.poranna`, `number_pos_round.poranna` z plików wariantów (287 kluczy, liczba i statusy bez zmian) i opisy; generator — układ jest daną, więc geometria i sprawdzenia bez zmian kodu; zmienione: `OBJ_ORIENT`, teksty rejestru odstępstw, etykieta K‑05, wpis R59; plan: Z20, D6, D11, 3.1, 4.1, 4.1a, 4.11; protokół: tabela 1, K‑05, K‑08, K‑09, K‑11, K‑13, K‑16, K‑59, K‑61, K‑62. BEZ ZMIAN: obrys płytek, wycięcie D, dołki i cyfra kwadratu, kieszenie magnesów, rowek pokrywki, ø100 i ścięcie okrągłych, dołki i cyfra okrągłej wieczornej, liczba i rozstaw otworów rynienki; korpus, blat, wkładka, pokrywka, tulejka, podkładki (9 plików STL bajtowo jak R57). Zmienione: 12 STL płytek i 4 JSON układu (`--etap ALL` i `--etap SPRAWDZ`: 0 NIE). Skutek uboczny: numery id gniazd inne niż w R54 (rynienka ma id 1; w rzędach mieszanych porannej id idą po y wpisu). Lista edycji: `R59_wdrozenie_zmiany.md`; raport `wyniki_v2/raport/raport_wykonawcy_R59_iter2.md` (stan końcowy; iter 1 to wcześniejszy przebieg z innym znakiem zera normalnych wkładki). Recenzja z siatek R59‑B iter 1: **ZALICZONY** (B 0 / P 0 / D 5; `recenzja/raport_recenzenta_R59_iter1.md`). Program (R59‑P), dokumenty i model (R59‑D, R59‑M) — osobne sesje. | [DECYZJA właściciela 14.11.2026 (G0): W‑b, P‑e, D3‑a, D5‑A] |
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
22. R53 (poprawki pasowań, 31.10): kołnierz blatu 193,6 (luz 0,7), haczyk 1,5 (czubek 98,3, zahaczenie 0,8), kieszeń zatrzasku 11 × 3,5 × 1,3 na Z 52,1…55,6 (luz Z 0,75/0,75, do dna 0,5, boczny 1,5), otwór wkrętu blatu ø3,6, otwór kołka wkładki ø3,4 (ruchome 0,2), otwór wkładki 96,8 (luz płytki 0,4; rama 104,8, gabaryt 148,4; kołek orientacyjny 0,6 od ścian = położenie bez zmian), rowek panelu 3,6; tulejka 11,85 celowo wciskowa (druk własny po pomiarze); pokrywka, płytki, tulejka, podkładki bez zmian. Zmienione STL: blat, korpus W/P, wkładka. Sondy K‑23/K‑27/K‑32/K‑42, K‑56 z parametrów; tabela 1 wkładka 148,4. Tabela 3 i 4.x do naniesienia. Kopia sprzed R53: `archiwum/wyniki_v2_przed_R53_2026-10-31/`.
23. R54 (1.11, właściciel): pole skanowania przy obrocie = koło (Z29: `scan_field_d` 100 DO_ZMIERZENIA #12, `scan_center_tol` 1,5, `work_overhang` 1,5 → `socket_zone_r` 47); D6 przeliczone na rzędy przycięte do koła, rynienki z przodu i z tyłu: wieczorna 18 + 2 (7 × ø9, 6 × ø12, 5 × ø15), poranna 31 + 2 (18 × ø7,5, 7 × ø10, 6 × ø12,5); stożki znaczników do koła (`ev_marker_pos`, `mo_marker_pos`), kieszenie magnesów w rogach bez zmian (Z4 uchylone, Z20 zastąpione, R40 bezprzedmiotowe); K‑05 (a, c), K‑09, K‑16; 4.1 p. 3 i 6, 4.11; pomiar #12 mierzy `scan_field_d`. Obrys płytki, wycięcie, dołki, numer, rowek pokrywki oraz wkładka, pokrywka, korpus, blat — bez zmian. Lista edycji: `R54_wdrozenie_zmiany.md`.
24. R55 (1.11, właściciel): bez druku z żywicy — druk własny wyłącznie FDM PETG u kolegi (pokrywka, tulejka DC, podkładki, płytka testowa n1, prototypy); płytki tylko PA12 z drukarni; Z19, D2, 3.5 (dc_bush_outer_d — skalowanie w slicerze), 4.1, 11, `materials`; pakiet folder PETG_FDM zamiast Zywica; dokumenty bez ustawień żywicy. Pliki STL bez zmian.
25. R56 (1.11, właściciel): tylko dokumenty — plan wdrożenia bez ram czasowych i bez sekcji „[cytat usuniety]”, „[cytat usuniety]” zwięźlej z firmami („[cytat usuniety]”), nowy dokument „[cytat usuniety]” (powody, zamienniki, wykluczenia), strona tytułowa z datą i godziną oraz autorem Michał Budek. STL bez zmian.
26. R57 (2.11, właściciel/nadzór, wykonawca R57‑A): płytka OKRĄGŁA jako drugi wariant do testu skanera (Z30, 4.1a): walec ø100 × 8 (= granica pola skanowania; zadanie zakładało 96 — ścianka 1,07 < 1,5 do krawędzi; decyzja nadzoru 100), faza 0,5, ścięcie orientacyjne (cięciwa 16 na −45°, głębokość 0,644, ścianka do obrysów ≥ 3), gniazda/rynienki/otwory/stożki identyczne z kwadratem R54, dołki kodu A/B/C/D w kole per typ, cyfra w kole, bez wycięcia D, kieszeni magnesów i rowka; kod 4‑bitowy n = A + 2B + 4C + 8D (D11; bit D na kwadracie (−45, −27), n1–n6 bez zmian), okrągłe n8 / n9; nowe klucze `parametry.json` (8); protokół K‑05 h, K‑61…K‑63, sekcja 3a, tabela 1; pliki `ramka_plytka_okragla_*_v2.stl` (4) i `uklad_gniazd_okragla_*.json` (2); generator: typy płytek, `triangulacja_cdt`, otwory ø3 w drugiej różnicy (tylko okrągłe). 15 plików R56 bajtowo bez zmian. Lista edycji: `R57_wdrozenie_zmiany.md`.
27. R57‑C (2.11, nadzór): dokumenty R57 zaktualizowane — „Zakupy i druk” (kolejność zakupów: płytki okrągłe n8 / n9 od razu, specyfikacja zamówienia z SHA‑256, objętościami i wymiarami, wymagania dla drukarni: ścięcie orientacyjne nie wygładzać, checklista odbioru), plan wdrożenia v2 (poz. 7a, tabela „Co zamawiamy”, zał. A), „Budowa ramki — decyzje i zamienniki” (element „Płytka okrągła (n8, n9)”: R58 wkładka + pokrywka, jeśli test wskaże koło); PDF‑y odbudowane; tekst K‑08 [R57] w protokole (D1) i ścianki do krawędzi w obu bazach w 4.1a / 4.11 / K‑16 (D3) — liczby projektu bez zmian. Arkusz zamówienia w pakiecie: 17 pozycji (15 z generatora + n8 / n9 skryptem `narzedzia/arkusz_zamowienia_R57.py`; `wyniki_v2/arkusze` bez zmian, K‑57 = 15). Pakiet `narzedzia/zbuduj_pakiet_R57.sh` → `Ramki_pakiet/` (`SHA256SUMS_2026-11-02_R57.txt`; STL R56 bajtowo bez zmian). Kopie sprzed: `archiwum/*_przed_dokumenty_R57_2026-11-02.*`.
28. R59 (14.11, właściciel, wykonawca R59‑A): nowy układ gniazd — na każdej płytce jedna rynienka (przednia) zamiast dwóch i większe gniazda: wieczorna 18 + 1 (6 × ø12, 12 × ø15; było 7 × ø9, 6 × ø12, 5 × ø15 + 2 rynienki), poranna 23 + 1 (20 × ø12,5, 3 × ø15; było 18 × ø7,5, 7 × ø10, 6 × ø12,5 + 2 rynienki), w porannej dwa rzędy mieszane; stożki znaczników w nowych miejscach (wieczorna B i C, poranna A, B i C); płytka okrągła poranna: dołki kodu i cyfra w nowych miejscach; Z20, D6, D11, 3.1, 4.1 p. 2–3 i przykład JSON, 4.1a, 4.11; protokół: tabela 1 (objętości 59,6 / 59,9 / 49,3 / 49,6), K‑05, K‑08, K‑09, K‑11, K‑13, K‑16, K‑59, K‑61, K‑62; numery płytek, obrys, kod i pozostałe części bez zmian (9 STL bajtowo jak R57). Lista edycji: `R59_wdrozenie_zmiany.md`.
29. R58 (19.11, właściciel, wykonawca R58‑A): komplet okrągły do ramki — płytka okrągła ramkowa 4.1b (n1–n3 wieczorne, n4–n6 poranne; bryła i wierzch jak 4.1a, kieszenie magnesów w osiach A/B/C na r 45, rowek pokrywki na całym obwodzie, rowek klucza od spodu na −45°), pokrywka okrągła 4.2a, wkładka okrągła 4.6a (obrys ramy, uszy, kołki, magnesy, rowek kablowy jak 4.6; otwór ø100,8 ze ścięciem, występ r 47 + 4 półki, kieszenie Halla w osiach, kołek klucza); D5, D8, D11, D12, 3.1, 3.4, 3.6 (14 nowych kluczy), 4.1a (funkcja), 4.11, 12.1 (poz. 17), 13 (R58); protokół: tabela 1, K‑64…K‑67, uwagi K‑60 (zrzut parametrów sprzed R58), K‑61, K‑63; tryb generatora `--etap R58`; 21 STL i 4 JSON R59 bajtowo bez zmian. Lista edycji: `R58_wdrozenie_zmiany.md`.
30. R58 runda 2 (19.11, recenzja R58 runda 1 → poprawki wykonawcy R58‑A): klucz płytki okrągłej — żebro na osi D przy ścięciu zamiast kołka ø3 (kołek mieścił się w pustej kieszeni magnesu; ścięcie nie blokuje obrotu), rowek klucza płytki r0 46,0 / wysokość 5,0; szczeliny odciążające pokrywki okrągłej (8 × 1,0 × 12); D5, D8, 3.1, 3.4 (4 klucze żebra zamiast 3 kluczy kołka, 3 klucze szczelin), 4.1b p. 3, 4.2a, 4.6a p. 4, 4.11, 13 (R58); protokół: tabela 1, K‑64 (ścianki 3D), K‑65 (żebro), K‑66 (szczeliny), K‑67 (przeszukanie ułożeń), K‑60 (D1); generator: `wyczysc_wyniki` chroni pliki R58 (P3). Lista edycji: `R58_wdrozenie_zmiany.md`, sekcje R2‑0…R2‑9.
31. R58 runda 3 (19.11, recenzja R58 runda 2 → poprawki wykonawcy R58‑A; płytki bez zmian): część żebra klucza nad wierzchem wkładki do `round_key_rib_top_r1` 49,2 z fazą na krawędzi zewnętrznej (P1: kołnierz pokrywki w skrajnym ustawieniu siadał na żebrze); szczeliny pokrywki 15 z otworem końcowym ø2,0 (`round_cover_slit_h` 12 → 15, `round_cover_slit_end_d`; P2); 3.1, 3.4 (2 nowe klucze, 1 zmieniony), 4.2a, 4.6a p. 4, 4.11, 13 (R58: D3); protokół: tabela 1, K‑65 (e), K‑66 (otwór końcowy), K‑67 (kołnierz w ustawieniach skrajnych 8 × 8 kierunków, czułość na geometrii rundy 2); generator: `--r58-runda2`. Zmieniają się tylko `ramka_wkladka_okragla_v2.stl` i `ramka_pokrywka_okragla_v2.stl`; 8 STL płytek i 2 JSON bajtowo jak w rundzie 2. Lista edycji: `R58_wdrozenie_zmiany.md`, sekcje R3‑0…R3‑7.
