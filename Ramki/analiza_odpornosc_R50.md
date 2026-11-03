# Analiza odporności konstrukcji na parametry DO_ZMIERZENIA — propozycje R50

Sesja analityczna (bez modelowania, bez edycji planu i `parametry.json`). Wejście: `plan_ramki_v2.md` (1–4, 7, 10, 13), `parametry.json`, `00_PRZEPLYW_I_BRAMKI.md` (11, 11a, 12), `protokol_weryfikacji_v2.md`. Data: 2026‑10‑26. Wszystkie liczby w mm, układ D3 (środek dna korpusu, Z w górę, przód = −Y).

Cel: jutro zamówić (MJF/SLS PA12) albo wydrukować samemu jak najwięcej części bez pomiarów prawdziwej elektroniki, ale tylko tam, gdzie błąd nie marnuje druku.

## 0. Założenia tej analizy (oznaczone A‑n; do zatwierdzenia razem z R50)

| Id | Założenie | Skąd |
|---|---|---|
| A‑1 | Panel: „generic”/Waveshare HUB75 64 × 64 P2.5, PCB 160 × 160 × 1,6; diody SMD2121 (1,1 nad PCB) z maską plastikową → lico 1,5–3,0 nad PCB. | wiedza o typowych panelach |
| A‑2 | Spód panelu bez kabli: złącza HUB75 2 × 8 w obudowie 9,0; gniazdo VH 4‑pin 10; kondensatory 6–8 → 10–11. **Z wpiętymi kablami**: wtyk IDC taśmy 13–15 + zagięcie taśmy 2–3; wtyk VH 4 + wyjście przewodów 15–19. Złącza HUB75 IN/OUT leżą zwykle przy lewej i prawej krawędzi PCB (środek wysokości), VH przy dolnej krawędzi; środek spodu (pod Pi) ma tylko kondensatory i układy. | j.w. |
| A‑3 | Otwory montażowe panelu: brak normy; spotykane 4 lub 8 otworów M3, rozstaw 110–136, zwykle symetrycznie wokół środka (offset 0 ± 3), zwykle gwint M3 (nakrętka wciskana od tyłu albo tulejka mosiężna na spodzie pod zestaw magnesów); prawdopodobieństwo gwintu ok. 80 %. | j.w. |
| A‑4 | Pi 4 + Bonnet (ADA 3211): PCB Pi 1,6 + złącze GPIO 11,0 + PCB Bonnetu 1,6 + gniazdo DC 11 = 25,2 (bez kabli); złącze IDC HUB75 Bonnetu 9 + wtyk taśmy 5 + zagięcie 3 → **28–31 z wpiętą taśmą**. Gniazdo DC Bonnetu leży na krótkiej krawędzi od strony karty SD i wtyk wychodzi w stronę karty SD (w układzie D10: −X); pewność ok. 75 %. Wtyk DC do kabla wewnętrznego: molded kątowy 25 × 11, albo „ze śrubkami” (lista zakupów) 38–45 długi. | wiedza o Bonnecie; R11 przyjął −Y arbitralnie |
| A‑5 | Gniazdo DC panelowe 5,5/2,1 z nakrętką: dwie rodziny — gwint ø8 (DC‑099, korpus 14–17 z lutami) i gwint ø11–12 (DC‑022B, korpus 16–22 z lutami, nakrętka ø14–15, płaski klucz 14). Wtyk kątowy: wysięg od lica gniazda 18–26, korpus ø/wys. 10–12; wtyk prosty: 30–40 + zagięcie kabla ≥ 12. | j.w. |
| A‑6 | Gniazdo USB‑A panelowe z kablem: otwór pod korpus 14 × 7 (ekran) → z ramką 15–16 × 8–9; flansza 26–32 × 16–18; 2 otwory ø3,2 w rozstawie 19–28 **poziomo** (większość tanich) albo 24 **pionowo** (typ „D” Neutrik). Korpus za flanszą 18–25 + kabel. | j.w. |
| A‑7 | Odbiornik nano: 14–25 × 12–16 × 5–7, wpięty w port USB Pi (wystaje 10–20 poza krawędź PCB Pi). | j.w. |
| A‑8 | Z1 (pole skanera ≥ 100 × 100): sprawdzalne JUTRO kartonową makietą 96 × 96 (pomiar #12, 10 min, bez elektroniki). | plan 10 |
| A‑9 | Etap B jeszcze nie jest zaliczony (G3). „Zamów jutro” znaczy: pliki z R50 wygenerowane i zaliczone przez recenzenta w nocy/rano; bez G3 nic nie idzie do drukarni — to warunek procesu, nie pomiaru. | 00_PRZEPLYW 2 |

---

## 1. Macierz zależności: część × parametr DO_ZMIERZENIA

Legenda: **—** brak zależności geometrii; **W** zależność przez łańcuch wysokości (D4); **P** zależność położenia cechy; **K** tylko kolizja w złożeniu (bryła zastępcza, K‑44b/K‑53), geometria części bez zmian; **Z1** zależność od pola skanera. W nawiasie: skutek, gdy prawdziwa wartość różni się o typowy rozrzut (sekcja 1.1).

| Parametr (pomiar #) | Korpus W/P | Blat | Rama dyfuzora | Wkładka | Płytki n1–n6 | Pokrywka | Uchwyt |
|---|---|---|---|---|---|---|---|
| panel_led_h (#3) | **W** (korpus_h = f(led_h); +1 → luz dioda–dyfuzor 4 → 3, −1 → 5; poza 1–3 → luz poza 3–5) | — (blat lokalnie niezależny; tylko jego Z globalne) | — (rama otacza PCB 0,4 pod spodem PCB niezależnie od led_h) | — | — | — | — |
| panel_bottom_parts_h (#4) | **W** (+4…8 z kablami → stos Pi uderza w złącza panelu; bez zapasu = korpus nieużyteczny) | — | — | — | — | — | — |
| panel_hole_pitch_x/y (#5) | **P** (podkładki i otwory w dnie (±60, ±60); ±5–8 → otwory nie trafiają → wiercenie w dnie albo nowy korpus) | — | — | — | — | — | — |
| panel_hole_offset_x/y (#6) | **P** (j.w., ±3) | — | — | — | — | — | — |
| panel_hole_threaded (#5a) | — (geometria dna nie zależy; zależy sposób mocowania: R50‑7) | — | — | — | — | — | — |
| panel_conn_zone_* (#7) | **K** (tylko proxy; złącza panelu nie mogą kolidować ze słupkami panelu z definicji — otwory są w PCB poza złączami; ze stosem Pi: przez W) | — | — (rama leży poza obrysem PCB) | — | — | — | — |
| pi_stack_h (#9) | **W** (+2…5 z taśmą → jak #4) | — | — | — | — | — | — |
| bonnet_dc_pos_x/y, bonnet_dc_dir (#10) | **K** (kierunek −X przy Pi w (−92): wtyk przebija lewą ścianę → kolizja nieusuwalna bez przesunięcia Pi; pozostałe kierunki OK) | — | — | — | — | — | — |
| dc_hole_d (#16) | **P** (ø8 vs ø12: gniazdo ø8 w otworze ø12 nie da się skręcić; ø12 w ø8 → rozwiercić w dnie kieszeni, wykonalne) | — | — | — | — | — | — |
| dc_pocket_depth (#16) | **P** (wtyk kątowy 26 > 20 w świetle → wtyk wystaje poza obrys; wtyk prosty nie wchodzi w ogóle) | — | — | — | — | — | — |
| dc_socket_body_l (#16) | **K** (korpus gniazda od y 78 w −Y: > 14,8 trafia w dystans panelu (−60, 60); z rowkiem R50‑2 dystans może być na y 65 → zostaje 9,8) | — | — | — | — | — | — |
| usb_cut_w/h (#17) | **P** (okno 15 × 8 za małe dla gniazda z ramką 16 × 9 → pilnik; za duże → zakryte flanszą, bez skutku) | — | — | — | — | — | — |
| usb_hole_pitch (#17) | **P** (22 vs 19–28 → otwory nie trafiają → wiercenie ø3,2 w tylnej ścianie, wykonalne, ukryte) | — | — | — | — | — | — |
| receiver_l/w/h (#14) | **K** (tylko proxy w korpusie P; odbiornik 25 długi sięga x 62 przy portach Pi y −21…13 — nic tam nie ma) | — | — | — | — | — | — |
| Z1 pole skanera (#12) | — | — | — | **Z1** (otwór 96,6 = plate_size + 0,6) | **Z1** (plate_size 96; geometria zamknięta, etap A zaliczony) | **Z1** (99,6 = plate_size + 3,6) | — |

Wniosek z macierzy: **wszystkie zależności od elektroniki siedzą w korpusie** (W: 3 parametry, P: 6, K: 4). Blat, rama, uchwyt są od pomiarów niezależne. Wkładka, płytki, pokrywka zależą wyłącznie od Z1, który sprawdza się jutro kartonem.

### 1.1 Typowy rozrzut i jego skutek przy obecnej geometrii

| Parametr | Domyślnie | Typowy zakres (A‑1…A‑7) | Skutek przy domyślnej geometrii, gdy wartość jest skrajna |
|---|---|---|---|
| panel_led_h | 2 | 1,0–3,0 | luz dioda–dyfuzor 4 ± 1 → w spec 3–5 ✓ (korpus niezmieniony) |
| panel_bottom_parts_h | 12 | 10–11 bez kabli; **15–19 z wpiętymi kablami** w strefie złączy | z kablami: złącza panelu 3–7 niżej niż spód strefy 37; nad Pi (szczyt 34) zostaje 0…−4 → **kolizja**, jeśli złącze panelu leży nad Bonnetem |
| panel_hole_pitch_x/y | 120 | 110–136 (4 lub 8 otworów) | otwory ±5–8 od podkładek → wiercenie ø4 w dnie 3 mm (wykonalne, niewidoczne) albo nowy korpus |
| panel_hole_offset_x/y | 0 | 0 ± 3 | j.w. |
| panel_hole_threaded | TAK | TAK ~80 % | NIE: R5 nie działa; mocowanie bez geometrii (R50‑7) |
| panel_conn_zone | 0,0,120,60 | IN/OUT 20 × 9 przy bokach PCB (x ≈ ±60…70), VH 12 × 10 przy dolnej krawędzi; strefa do 150 × 150 | tylko przez wysokość (wiersz #4) |
| pi_stack_h | 26 | 25–26 bez taśmy; **28–31 z wpiętą taśmą HUB75** | luz nad stosem 3 → 0…−2 → **kolizja z proxy‑panelem na Z 37** |
| bonnet_dc_pos / dir | (−60, −28), −Y | krawędź SD, −X (75 %) | przy Pi w x = −92: od krawędzi SD do ściany 5,5 → **żaden wtyk nie wchodzi** |
| dc_hole_d | 12 | 8 albo 11–12,5 | ø8: luz 2 na stronę, nakrętka M8 nie dociśnie → tulejka; 12,5 → rozwiercić |
| dc_pocket_depth | 22 (20 w świetle) | wtyk kątowy 18–26 | 26 > 20 → wtyk wystaje 6 poza obrys 200 |
| dc_socket_body_l | 12 | 14–22 z lutami | > 14,8 → dotyka dystansu panelu (−60, 60) |
| usb_cut_w/h | 15 × 8 | 15–16 × 8–9 | 16 × 9 nie wejdzie → pilnik 0,5 na stronę (ukryte, wykonalne) |
| usb_hole_pitch | 22 | 19–28 poziomo, 24 pionowo | otwory nie trafiają → wiercenie ø3,2 (ukryte) |
| receiver_* | 19 × 15 × 6 | 14–25 × 12–16 × 5–7 | brak (tylko proxy) |
| Z1 | ≥ 100 × 100 | nieznane | < 96: plate_size ↓ → płytki + wkładka + pokrywka do przeprojektowania (v3) |

---

## 2. Werdykt per część

Kwoty z sekcji 11 planu (wariant najtańszy / pokazowy, obie ramki). „Jutro” zakłada A‑9 (pliki po R50 zaliczone na G3).

| Część | Werdykt | Uzasadnienie | Kwota ryzyka |
|---|---|---|---|
| Korpus W/P (2 szt.) | **ZAMÓW JUTRO po zmianie R50‑1, R50‑2, R50‑3, R50‑5, R50‑6** (R50‑4 opcjonalnie) | Dziś korpus zależy od 13 niezmierzonych parametrów; po R50 każda pozostała rozbieżność w typowym zakresie jest usuwalna wiertłem/pilnikiem w ukrytym miejscu albo doborem kupnych dystansów. Bez R50: CZEKAJ na pomiary #3, #4, #5, #6, #9, #10, #16, #17. | 390–690 zł / 600–1 050 zł — największe w projekcie |
| Blat (2 szt.) | **ZAMÓW JUTRO bez zmian** | Geometria blatu jest lokalna (wierzch Z 0); żaden parametr DO_ZMIERZENIA ani Z1 na nią nie wpływa; po R50‑1 zmienia się tylko jego położenie globalne (liczby w opisach, nie w siatce). | 155–270 zł / 240–420 zł |
| Rama dyfuzora (2 szt.) | **ZAMÓW JUTRO bez zmian** (albo FDM PETG u kolegi wg 11a, bez decyzji) | Otacza PCB 160 (SPEC) i stoi na bossach blatu; po R50‑1 spód ramy (blat_top − 10 = 53,6) leży 0,4 pod spodem PCB (54) niezależnie od `panel_led_h`, bo panel_pcb_z wynika z dystansu 50, nie z pomiaru. | 35–60 zł / 50–90 zł |
| Wkładka (3 szt.) | **ZAMÓW JUTRO po teście #12** (karton 96 × 96 w skanerze, 10 min) + prototyp żywiczny wg 11a jeśli czas pozwala | Zależy tylko od `plate_size` (otwór 96,6). Od elektroniki niezależna. | 45–80 zł |
| Płytki n1–n6 (6 szt.) | **ZAMÓW JUTRO po teście #12** | Geometria zamknięta (etap A zaliczony); jedyna zależność to Z1. Nie proponuję zmian. | 335–590 zł |
| Pokrywka (4 szt.) | **DRUKUJ SAM (FDM PETG) po teście #12**; nie zamawiać | Zależy od plate_size (99,6); druk własny wg sekcji 11 → ryzyko ≈ koszt filamentu. | 0 zł (własny druk) / 110–190 zł gdy zamawiana |
| Uchwyt kabli (4 szt.) | **DRUKUJ SAM bez zmian** (dowolny termin) | Bez pasowań, bez zależności (odbiornik USB nie dotyka uchwytu). | ≈ 0 zł |

Podsumowanie: po R50 **nic nie musi czekać na elektronikę**. Jedyny pomiar przed zamówieniem to #12 (pole skanera) — bez elektroniki, w firmie, jutro rano.

---

## 3. Propozycje R50‑1 … R50‑8

Każda: co zmienić (parametry + wartości), koszt, rachunek 4.8 / 4.11, bezpieczeństwo („bezpieczna” = nie pogarsza niczego, gdy pomiar potwierdzi domyślne), rekomendacja. Numery (a)–(h) odwołują się do listy z zadania.

### R50‑1 — Zapas wysokości nad stosem Pi + Bonnet (b) — **REKOMENDUJĘ**

- **Zmiana:** `pi_clearance_top` 3 → **8**. Wynika: `panel_pcb_z` 49 → **54**, `blat_top_z` 58,6 → **63,6**, `korpus_h` 54,6 → **59,6**, `panel_standoff_l` 45 → **50** (stock 50, podkładka 1 bez zmian). Parametry globalne związane z blatem przesuwają się o +5: `snap_pocket_z` 47,6 → **52,6**, `snap_hook_z` 47,85 → **52,85** (lokalnie −10,75 bez zmian), `blat_screw_z` 50 → **55**, `label_pos_z` 46 → **51** (zachowuje 8,6 od górnej krawędzi; może zostać 46). Bez zmian: `dc_pos_z`, `usb_pos_z`, `vent_slot_z` (liczone od dna), cała geometria lokalna blatu, ramy, wkładki.
- **Co pokrywa:** stos Pi do 31 (taśma wpięta w IDC Bonnetu + zagięcie) przy spodzie panelu 12; albo spód panelu z kablami do 17 przy stosie 26; albo dowolna suma +5. Przy obróceniu panelu tak, by złącza HUB75 leżały nad kolumną słupków (x ≈ ±60…70, nie nad Bonnetem), realna suma wynosi ok. 3 + 5 + 28 + 8 (kondensatory) = 44 < 54 (zapas 10).
- **Koszt:** wysokość ramki 63,6 (+ stopki 4) zamiast 58,6 — **przekracza spec 55–60 o 3,6 mm**; korpus +5 × 2,5 × 800 ≈ 10 cm³/szt. → +20 cm³ ≈ **+20–35 zł** na obie ramki; sztywność bez zmian (ściana 2,5, kołnierz blatu ten sam); wygląd: kostka 200 × 200 × 67,6 ze stopkami.
- **Rachunek 4.8 / 4.11:** łańcuch 3 + 5 + 26 + 8 + 12 = 54; + 1,6 + 2 + 4 + 2 = 63,6; korpus 63,6 − 4 = 59,6 ✓; słupki 3 + 1 + 50 = 54 ✓; haczyk w kieszeni: Z 52,85…54,85 w 52,6…55,1 → 0,25 luzu ✓ (bez zmian lokalnie); kieszeń DC Z 12…40 vs kołnierz blatu od 49,6 → 9,6 zapasu ✓; wkręt blatu (±75, 55) 15 nad skrzynką ✓; napis Z 47…55 vs kieszeń przednia x 45…55, Z 52,6…55,1 → jak R47(17), relief na zewnątrz ✓; luz dioda–dyfuzor = 6 − led_h → 5/4/3 dla led_h 1/2/3 → zawsze w spec 3–5 ✓ (to drugi zysk: led_h przestaje mieć znaczenie).
- **Bezpieczna:** TAK — gdy pomiary potwierdzą 26/12, zostaje 5 mm powietrza nad stosem; nic nie koliduje. Jeśli pomiar wykaże więcej niż +5: awaryjnie zeszlifować bossy Pi z 5 do 3 (+2) i przełożyć taśmę płasko.
- **Wariant R50‑1b (NIE rekomenduję, tylko gdy właściciel upiera się przy ≤ 60):** `pi_standoff_h` 5 → 3 i `panel_pad_h` 1 → 4 (dystans 45): panel_pcb_z 52, blat_top 61,6; dodatkowo `led_gap` 4 → 3: 60,6. Kosztem: bossy Pi 3 mm z otworem 5 (→ `insert_depth_m25` 4), gorsze chłodzenie od spodu, luz dioda–dyfuzor 2…4.

### R50‑2 — Rowki pod słupki panelu zamiast otworów (a) — **REKOMENDUJĘ wariant rowka po przekątnej**

- **Zmiana (4.3 cecha 1):** zamiast 4 podkładek ø9 × 1 z otworem ø3,4 w (±60, ±60): 4 podkładki w kształcie **stadionu 9 szer. × 1 wys.** wzdłuż przekątnej od punktu (±55, ±55) do (±65, ±65), w dnie **rowek 3,4 szer.** o tej samej osi (długość 14,1 + 3,4 = 17,5), od spodu **pogłębienie‑rowek 6,5 szer. × 2 gł.** o tej samej osi. Nowe parametry: `panel_slot_pitch_min` 110, `panel_slot_pitch_max` 130, `panel_slot_w` 3,4 (= `panel_screw_hole_d`), `panel_slot_cbore_w` 6,5 (= `panel_screw_cbore_d`). `panel_hole_pitch_x/y`, `panel_hole_offset_x/y` zostają DO_ZMIERZENIA, ale używa ich już tylko bryła zastępcza dystansów w `.blend` (K‑44b/K‑53), nie korpus.
- **Co pokrywa:** rozstaw 110…130 w obu osiach przy px = py i offset 0 (otwór panelu leży wtedy na przekątnej). Rozstaw niekwadratowy albo offset: punkt schodzi z osi rowka o |px − py|/(2√2) → 3 mm różnicy = 1,06 mm → nie wchodzi. **Fallback bez nowego korpusu:** wiercenie ø4 w dnie 3 mm w zmierzonym miejscu (10 min, niewidoczne od góry; podkładkę 1 mm zastępuje drukowana/mosiężna podkładka ø9 × 1 z R50‑8). Dlatego nie proponuję siatki otworów dla 2–3 wzorów (osłabia dno pod kołnierzem, zyskuje tyle co wiertło) ani „szyn” panelu (osobne listwy przykręcane do stałych otworów w dnie — pokrywają wszystko, ale wymagają 2 nowych części, przesunięcia żeber i zmiany kieszeni DC; za dużo zmian w trakcie etapu B).
- **Koszt:** wygląd dna (rowki 17,5 × 6,5 od spodu, niewidoczne w użyciu); objętość −0,5 cm³; sztywność dna bez zmian (żebra R51 startują od krawędzi podkładki, teraz od końca stadionu w stronę narożnika: `rib_start_r` liczone od punktu (65, 65) → żebro od (69,5, 69,5) do narożnika; przy rozstawie 110 słupek stoi na początku stadionu i żebro nadal podpiera).
- **Rachunek 4.8/4.11:** ścianka dna pod pogłębieniem 1 + podkładka 1 = 2 ≥ 1,5 ✓ (jak dziś); kolizje przy skrajnym położeniu (±65, ±65) ø6,4 → x,y do 68,2: Pi po R50‑6 y ≤ 28 ✓, skrzynka DC y ≥ 78 ✓ (9,8), uchwyt (±20, 75) stopa x 10…30 ✓, gniazdo USB y ≥ 77 ✓ (8,8), łapy ramy (±81…94) ✓ (12,8), wloty w dnie ✓; przy (±55, ±55): Pi x ≤ 35 ✓, kołnierz blatu wewn. 95 ✓.
- **Bezpieczna:** TAK — przy 120/120 słupek stoi w środku stadionu, pasowanie identyczne jak dziś (otwór 3,4 na M3).

### R50‑3 — Gniazdo DC w bocznej ścianie kieszeni, otwór ø12 + tulejka redukcyjna ø8 (c, e) — **REKOMENDUJĘ**

- **Problem dziś:** oś gniazda (−60, Z 30) w dnie kieszeni (y 78) celuje w słupek panelu (−60, 60): korpus gniazda > 14,8 (z lutami typowo 16–22) go dotyka; z R50‑2 słupek może stać na y 65 → zostaje 9,8. Do tego ø8 vs ø12 i głębokość kieszeni vs wysięg wtyku.
- **Zmiana (4.3 cecha 6, D14, Z27):** gniazdo w **prawej ścianie skrzynki** (płaszczyzna x = −40, ściana −42…−40), oś (**y 89, Z 30**), osią wzdłuż X; flansza gniazda wewnątrz kieszeni, nakrętka od strony wnętrza obudowy (x > −40), korpus gniazda biegnie w +X w wolną przestrzeń (do bossa uchwytu (−20, 75) jest 20 mm w X i 6 w Y; do prawego uchwytu x ≥ 10 jest 50). Otwór **ø12** (`dc_hole_d` 12, status ZALOZENIE) + osobna część **tulejka redukcyjna** ø12/ø8,2 × 2 z kołnierzem ø15 × 1 po stronie kieszeni (`ramka_tulejka_dc_v2.stl`, 2 szt., żywica w firmie, 1 cm³) — używana tylko gdy pomiar #16 da ø8. Wtyk kątowy wchodzi od wnętrza kieszeni w −X: wysięg 18–26 od lica −42 → do −68, ściana lewa skrzynki −78 → ≥ 10 zapasu ✓; kabel wtyku kątowego obrócić ku +Y → wychodzi prosto przez okno 36 × 24. `dc_pocket_depth` 22 zostaje (potrzebne tylko ≥ ø wtyku 11 + 2 × 5) → **przestaje być DO_ZMIERZENIA**. Nowe parametry: `dc_socket_axis` "X", `dc_pos_y` 89, `dc_pos_x` −40 (płaszczyzna ściany); `dc_socket_body_l` używany tylko przez proxy (w +X od −40, bez ograniczenia do 50).
- **Koszt:** zero objętości; montaż: gniazdo wkłada się przez okno, nakrętkę dokręca kluczem 14 od góry (blat zdjęty) — dostęp swobodny; wygląd bez zmian (wszystko w kieszeni).
- **Rachunek 4.8/4.11:** ściana skrzynki 2 mm z otworem ø12 w polu 22 (Y) × 28 (Z): od otworu do krawędzi ściany ≥ 2 (Z 36 → sufit wewn. 38) ✓; nakrętka ø15 (Z 22,5…37,5, y 81,5…96,5) mieści się na ścianie (y 80…97,5, Z 14…38) ✓; wtyk ø11 w świetle kieszeni Z 24,5…35,5 w 14…38 ✓, y 83,5…94,5 w 80…97,5 ✓; słupek panelu (−60, 55…65) od skrzynki (y ≥ 78) ≥ 9,8 ✓; rowek R50‑2 nie dochodzi do skrzynki ✓.
- **Bezpieczna:** TAK — przy ø12 tulejka nie jest używana; przy wtyku kątowym 18–26 wszystko mieści się w obrysie 200. Wtyk prosty nadal NIE wchodzi (jak Z27) — patrz R50‑4.

### R50‑4 — Kieszeń DC poszerzona do lewej ściany (e: wtyk prosty) — **REKOMENDUJĘ jako darmowe ubezpieczenie**

- **Zmiana:** skrzynka x −80…−40 → **−97,5…−40** (lewa ściana skrzynki = lewa ściana korpusu), okno w tylnej ścianie x −78…−42 → **−93…−42** (`dc_pocket_w` 36 → **51**, środek okna `dc_pos_x_window` −67,5; naroża R 3 bez zmian), Z 14…38 bez zmian. Wtyk prosty 30–40 od lica −42 → do −82, zagięcie kabla 12 → −94 < −95,5 (wnętrze) ✓.
- **Koszt:** −1 cm³ (znika ściana −80, dochodzi 17,5 × 22 × 2 × 2 dna i sufitu); okno 51 szer. w tylnej ścianie (ukryte); ściana tylna nad oknem Z 38…59,6 = 21,6 ✓.
- **Rachunek:** szczeliny lewej ściany (y ±45, Z 6,5…9,5) poza skrzynką (y 78…100, Z 12…40) ✓; żebro (−60,60)→(−97,6, 97,6) na Z 3…9 pod skrzynką (Z ≥ 12) ✓; kieszeń zatrzasku tylna x −50, Z 52,6…55,1 nad skrzynką ✓; wkręt blatu (−75, 55) ✓; narożnik wewn. R 2,5 przy (−97,5, 97,5) — okno kończy się 4,5 od narożnika ✓.
- **Bezpieczna:** TAK (jedynie większy otwór z tyłu, nic nie traci funkcji).

### R50‑5 — Okno USB 16 × 9 i rowki zamiast otworów flanszy (d) — **REKOMENDUJĘ**

- **Zmiana (4.3 cecha 6):** `usb_cut_w` 15 → **16**, `usb_cut_h` 8 → **9** (status ZALOZENIE; największe typowe gniazdo z ramką); zamiast 2 otworów ø3,2 w (60 ± 11, Z 24): 2 **rowki poziome 3,2 × 7,2** o osiach od x 60 ± 10 do 60 ± 14 (rozstaw 20…28). Nowe parametry: `usb_slot_pitch_min` 20, `usb_slot_pitch_max` 28, `usb_slot_w` 3,2; `usb_hole_pitch` przestaje być używany przez korpus (zostaje jako wartość do proxy). Flansza 26–32 szer. zakrywa rowki (x 44…76) i okno ✓. Gniazdo typu „D” z otworami pionowymi (rozstaw 24): **fallback = 2 otwory ø3,2 wywiercone w tylnej ścianie** (ukryte), rowki poziome nie przeszkadzają.
- **Koszt:** 0 cm³; ściana 2,5 z rowkami 7,2 × 3,2 — bez wpływu na sztywność; ukryte z tyłu.
- **Rachunek:** okno 16 × 9 w (60, Z 24): Z 19,5…28,5; rowki Z 22,4…25,6, x 48,4…55,6 i 64,4…71,6 → ścianka okno–rowek 55,6 → 52 = **2,4 ≥ 1,5** ✓; do szczelin wentylacyjnych tylnych (x 45, 63; Z 6,5…9,5) ≥ 10 ✓; korpus gniazda 16 × 14 × 20 za ścianą (x 52…68, y 77…97,5, Z 17…31) vs słupek panelu (60, ≤ 68,2) → 8,8 ✓ (dla R50‑2 skrajnego), vs uchwyt prawy stopa x 10…30 ✓. Alternatywa „ramka adaptera” (płytka z otworami drukowana po pomiarze, przykręcana do 2 stałych otworów) — NIE: więcej części, a wiercenie 2 × ø3,2 w PA12 jest trywialne.
- **Bezpieczna:** TAK (przy 15 × 8 i rozstawie 22 wszystko pasuje jak dziś; okno większe o 0,5 na stronę jest pod flanszą).

### R50‑6 — Pi przesunięty do środka: zapas dla każdego z 4 kierunków wtyku DC Bonnetu (f) — **REKOMENDUJĘ**

- **Problem dziś:** krawędź SD Pi w x = −92, ściana w −97,5 → kierunek −X (A‑4: najbardziej prawdopodobny!) jest fizycznie niemożliwy; R11 ratował się przyjęciem −Y.
- **Zmiana (D10, 4.3 cechy 2–4):** `pi_pos_x` −92 → **−50** (Pi x −50…35, y −28…28, karta SD nadal w −X); bossy Pi w (−46,5, ±24,5), (11,5, ±24,5); `sd_slot_x` −91 → **−49**; `floor_vent_x` −60 → **−8** (wloty 20 × 3 na y ±10 pod środkiem Pi; z dala od rowków R50‑2 i szczeliny SD). Bryły zastępcze: `proxy_pi_bonnet` narożnik (−50, −28); `bonnet_dc_pos` domyślnie (**−50, 22**), `bonnet_dc_dir` domyślnie **−X** (A‑4; nadal DO_ZMIERZENIA, ale geometria korpusu jest od niego niezależna); `bonnet_dc_plug_len` 15 → **40** (wtyk ze śrubkami z listy zakupów jest najdłuższy).
- **Zapas dla kierunków (wtyk 40):** −X: od −50 do −90, ściana −97,5 → 7,5 ✓ (szczeliny lewej ściany Z ≤ 9,5, wtyk Z 20…31 ✓; szczelina SD w dnie pod wtykiem ✓); −Y: od −28 do −68, słupek (−60, −55…−65) ø6,4 tylko gdy gniazdo byłoby w x −63…−57 — gniazdo Bonnetu leży ≥ 5 od krawędzi SD (x ≥ −45) ✓, ściana −97,5 ✓; +Y: od 28 do 68, boss uchwytu (−20, 75) ø8 od y 71 → 3 ✓ (wtyk kątowy daje więcej); +X: gniazdo na krawędzi Bonnetu x = 15 celowałoby w porty USB/Ethernet Pi (x 35…37, Z 9,6…25,6 vs wtyk Z 11,7…22,7) — wykluczone przez sam Bonnet, nie przez korpus. Wniosek: 3 kierunki pewne, czwarty nie istnieje na realnym sprzęcie.
- **Inne skutki:** Pi w całości pod panelem (A‑2: środek spodu to kondensatory 6–8, bezpieczne przy R50‑1); krawędź SD nie wystaje poza panel (D10 do poprawy — dostęp do karty przez szczelinę w dnie bez zmian); porty USB Pi (x 35…37) → kabel USB serwisowy i odbiornik mają 20 mm do kolumny słupków (x ≥ 56,8) i leżą w y −21…13 (kolumna słupków y ±55…65) ✓; USB‑C/HDMI Pi na y −28…−30 ✓; żebra przekątne (|x|,|y| ≥ 65) nie wchodzą w strefę Pi ✓; uchwyt lewy (−20, 75) ✓.
- **Koszt:** 0 cm³; zero zmian wyglądu; 3 liczby w `parametry.json`.
- **Rachunek 4.11 (wiersz „Wtyk DC Bonnetu”):** nowy: −X 40 → −90 ≥ −97,5 ✓ (7,5); −Y 40 → −68 ≥ −97,5 ✓; +Y 40 → 68 ≤ 71 ✓.
- **Bezpieczna:** TAK (przy −Y jak dziś nic się nie psuje).

### R50‑7 — Mocowanie panelu działające z gwintem i bez (h) — **REKOMENDUJĘ (bez zmian geometrii drukowanej)**

- **Z gwintem (pomiar #5a = TAK):** jak R5, ale dystans **F‑F 50** (nie M‑F) + **wkręt dociskowy M3 × 5** (bez łba) wkręcony 2,5 w gwint panelu i 2,5 w dystans. Powód: trzpień męski standardowego dystansu M‑F ma 6 mm, a gwint panelu (nakrętka wciskana 2–2,5 + PCB 1,6) ma 3–4 mm → trzpień wyszedłby 2–3 mm od strony diod. Wkręt dociskowy nic nie wystawia.
- **Bez gwintu (#5a = NIE):** **tulejka mosiężna F‑F M3 ø5 × 5 doklejona epoksydem** do spodu PCB współosiowo z otworem (centrowanie: śruba M3 × 10 przełożona przez otwór na czas klejenia, wyjęta po utwardzeniu — od strony diod nic nie zostaje). Dystans **45** + tulejka 5 = 50 → 3 + 1 + 45 + 5 = 54 = `panel_pcb_z` ✓ (obie długości to stock: 45 i 50). Nakrętka od strony diod — wykluczona; nitonakrętka — wykluczona (rozprężenie po stronie diod); PEM — nie klinczuje w FR4.
- **Zmiana w planie:** D13/R5 tekst, lista zakupów (dystanse F‑F 50 × 8 **i** F‑F 45 × 8, wkręty dociskowe M3 × 5 × 10, tulejki F‑F M3 × 5 × 8, epoksyd 2‑składnikowy), krok 8 montażu. `parametry.json`: `panel_standoff_l` LICZONE 50 (opis: „50 F‑F przy gwincie; 45 + tulejka 5 bez gwintu”). `panel_hole_threaded` zostaje DO_ZMIERZENIA, ale żadna część drukowana od niego nie zależy.
- **Koszt:** +40 zł sprzętu (dystanse w dwóch długościach kupić po pomiarze — nie blokuje zamówienia druku).
- **Bezpieczna:** TAK.

### R50‑8 — Komplet podkładek dystansowych panelu (uzupełnienie R50‑2/R50‑7) — **REKOMENDUJĘ (druk własny, później)**

- **Nowa część:** `ramka_podkladka_panelu_v2.stl` — krążki ø9 z otworem ø3,4, grubości **0,5 / 1 / 2** (po 8 szt.), żywica/FDM, etap C lub poza przepływem. Służą do: (1) wyrównania długości dystansu, gdy pomiar #4/#9 wykaże potrzebę ±1…3 mm (panel niżej = krótszy dystans + podkładki), (2) podkładki pod słupek w wywierconym otworze fallbacku R50‑2.
- **Koszt:** ≈ 0. **Bezpieczna:** TAK (nieużywane, gdy pomiar = domyślne).

### Pomysły rozważone i odrzucone
- **(a) siatka otworów 2–3 wzorów w dnie** — NIE: dno 3 mm z 12 pogłębieniami ø6,5 pod kołnierzem blatu, a wzorów i tak nie znamy; wiertło daje to samo.
- **(a) szyny panelu (osobne listwy)** — NIE w etapie B (wymaga przesunięcia żeber, 2 części, stałe otwory); zostaje jako plan v3, jeśli panel okaże się egzotyczny.
- **(e) kieszeń głębsza (dc_pocket_depth 22 → 30)** — NIE: przy osi gniazda wzdłuż Y kieszeń 30 wpycha gniazdo na y 70 → w słupek panelu; rozwiązane przez obrót osi (R50‑3) i poszerzenie (R50‑4).
- **(d) ramka adaptera USB** — NIE (R50‑5).
- **(g) strefa złączy panelu** — bez zmian geometrii: złącza są na PCB poza otworami panelu z definicji, słupki stoją ≥ 6,8 od Pi (po R50‑6) i ≥ 9,8 od skrzynki DC; jedyna interakcja to wysokość (R50‑1).

---

## 4. Lista „jutro” i lista „czekaj”

### 4.1 Do zamówienia / druku jutro (przy wdrożeniu R50‑1…R50‑8 i zaliczeniu G3 na nowych plikach)

| Kolejność | Część | Gdzie | Warunek przed wysłaniem |
|---|---|---|---|
| 1 | Korpus W + P | drukarnia MJF/SLS PA12 grafit | pliki po R50 zaliczone (G3); `arkusz_zamowienia` z objętością (korpus ≈ 225 cm³/szt.) |
| 2 | Blat × 2 | drukarnia, grafit | bez zmian geometrii; G3 |
| 3 | Rama dyfuzora × 2 | drukarnia (grafit) **albo** FDM PETG u kolegi | bez zmian; jeśli FDM — nie blokuje niczego, drukować po G3 |
| 4 | Wkładka × 3 | drukarnia, naturalny biały | **pomiar #12** (karton 96 × 96 w skanerze) = TAK; zalecany prototyp żywiczny wkładka + 1 płytka (11a) — jeśli czas na to nie pozwala, zamawiać mimo to (ryzyko 45–80 zł) |
| 5 | Płytki n1…n6 | drukarnia, naturalny biały | **pomiar #12** = TAK (jedyny warunek) |
| 6 | Pokrywka × 4 | FDM PETG u kolegi | pomiar #12 = TAK |
| 7 | Uchwyt kabli × 4 | FDM dowolny | brak |
| 8 | Tulejka DC × 2, podkładki panelu 24 szt. | żywica w firmie, po pomiarach #4/#9/#16 | nic nie blokują; drukować gdy elektronika w ręku |

### 4.2 Co i tak czeka

| Co | Na co czeka | Minimalny zestaw pomiarów (sekcja 10) |
|---|---|---|
| Zakup dystansów (50 F‑F vs 45 F‑F + tulejka) i wkrętów dociskowych | gwint panelu | #5a |
| Decyzja „tulejka DC czy nie” | średnica gniazda | #16 |
| Ewentualne wiercenie dna (fallback R50‑2) | wzór otworów panelu | #5, #6 |
| Ewentualne wiercenie flanszy USB (gniazdo typu D) | rozstaw | #17 |
| Przebieg ALL + recenzja ALL (bramka G5) | wszystkie pomiary | #3–#10, #14, #16, #17 — **ale po R50 G5 nie blokuje już żadnej części**, tylko potwierdza złożenie w `.blend` |

Bez R50 (dla porównania): korpus czekałby na #3, #4, #5, #6, #9, #10, #16, #17 (8 pomiarów, wszystkie wymagają elektroniki w ręku).

### 4.3 Pozostałe ryzyko po R50 (co może jeszcze pójść źle i jak to naprawić bez nowego korpusu)

| Ryzyko | Prawdop. (A‑n) | Naprawa |
|---|---|---|
| Wzór otworów panelu niekwadratowy / offset > 1 / 8 otworów poza 110–130 | ~30 % | wiercenie ø4 w dnie + podkładka R50‑8 (10 min) |
| Suma stos + złącza panelu > +5 w tym samym miejscu XY | ~15 % | obrót panelu (złącza nad kolumną słupków), taśma płasko; awaryjnie bossy Pi 5 → 3 (pilnik) |
| Gniazdo DC gwint > 12 (12,5) | ~10 % | rozwiercić ø12,5 w ścianie skrzynki (2 mm PA12) |
| Gniazdo USB typu D (otwory pionowe) | ~25 % | 2 × ø3,2 wiercone w tylnej ścianie |
| Wtyk DC Bonnetu +X | ~0 % | — |
| Pole skanera < 96 | nieznane | test #12 PRZED zamówieniem płytek/wkładki/pokrywki; korpus i blat niezależne |

---

## 5. Zmiany w `parametry.json` i sekcje planu do edycji (NIE wdrożone — do zatwierdzenia)

### 5.1 Blok JSON (tylko klucze zmieniane/dodawane; sekcja wg struktury pliku)

```json
{
  "panel_dyfuzor_pi": {
    "pi_clearance_top":    {"value": 8,    "status": "ZALOZENIE", "zrodlo": "R50-1", "opis": "zapas nad stosem Pi: pokrywa taśmę HUB75 w IDC Bonnetu i złącza panelu z kablami"},
    "pi_pos_x":            {"value": -50,  "status": "ZALOZENIE", "zrodlo": "R50-6", "opis": "narożnik PCB Pi (krawędź SD, przód); Pi x -50..35"},
    "sd_slot_x":           {"value": -49,  "status": "ZALOZENIE", "zrodlo": "R50-6"},
    "bonnet_dc_pos_x":     {"value": -50,  "status": "DO_ZMIERZENIA", "pomiar": 10, "zrodlo": "R50-6", "opis": "domyślnie krawędź SD Bonnetu; korpus od tego niezależny"},
    "bonnet_dc_pos_y":     {"value": 22,   "status": "DO_ZMIERZENIA", "pomiar": 10, "zrodlo": "R50-6"},
    "bonnet_dc_dir":       {"value": "-X", "status": "DO_ZMIERZENIA", "pomiar": 10, "zrodlo": "R50-6 (A-4)", "opis": "-X, +X, -Y lub +Y; po R50-6 każdy kierunek mieści wtyk 40"},
    "bonnet_dc_plug_len":  {"value": 40,   "status": "ZALOZENIE", "zrodlo": "R50-6", "opis": "wtyk DC ze śrubkami (najdłuższy z listy zakupów)"},
    "panel_slot_pitch_min": {"value": 110, "status": "ZALOZENIE", "zrodlo": "R50-2", "opis": "rowek podkładki panelu po przekątnej: od (±55, ±55)"},
    "panel_slot_pitch_max": {"value": 130, "status": "ZALOZENIE", "zrodlo": "R50-2", "opis": "do (±65, ±65)"},
    "panel_slot_w":         {"value": 3.4, "status": "ZALOZENIE", "zrodlo": "R50-2", "opis": "szerokość rowka w dnie (= panel_screw_hole_d)"},
    "panel_slot_cbore_w":   {"value": 6.5, "status": "ZALOZENIE", "zrodlo": "R50-2", "opis": "szerokość pogłębienia-rowka od spodu x 2 gł. (= panel_screw_cbore_d)"}
  },
  "korpus": {
    "korpus_h":         {"value": 59.6, "status": "LICZONE", "wzor": "blat_top_z - blat_t"},
    "blat_top_z":       {"value": 63.6, "status": "LICZONE", "wzor": "panel_pcb_z + panel_pcb_t + panel_led_h + led_gap + diffuser_t"},
    "panel_pcb_z":      {"value": 54,   "status": "LICZONE", "wzor": "floor_t + pi_standoff_h + pi_stack_h + pi_clearance_top + panel_bottom_parts_h"},
    "panel_standoff_l": {"value": 50,   "status": "LICZONE", "wzor": "panel_pcb_z - floor_t - panel_pad_h", "opis": "50 F-F przy gwincie panelu; 45 F-F + tulejka 5 bez gwintu (R50-7)"},
    "floor_vent_x":     {"value": -8,   "status": "ZALOZENIE", "zrodlo": "R50-6", "opis": "wloty 20 x 3 pod środkiem Pi"},
    "snap_pocket_z":    {"value": 52.6, "status": "LICZONE", "wzor": "korpus_h - 7", "zrodlo": "R50-1"},
    "blat_screw_z":     {"value": 55,   "status": "LICZONE", "wzor": "korpus_h - 4.6", "zrodlo": "R50-1"},
    "label_pos_z":      {"value": 51,   "status": "LICZONE", "wzor": "korpus_h - 8.6", "zrodlo": "R50-1"},
    "dc_hole_d":        {"value": 12,   "status": "ZALOZENIE", "zrodlo": "R50-3", "opis": "otwór w prawej ścianie skrzynki; ø8 przez tulejkę redukcyjną"},
    "dc_socket_axis":   {"value": "X",  "status": "ZALOZENIE", "zrodlo": "R50-3", "opis": "oś gniazda wzdłuż X, flansza w kieszeni, nakrętka od wnętrza obudowy (x > -40)"},
    "dc_pos_x":         {"value": -40,  "status": "ZALOZENIE", "zrodlo": "R50-3", "opis": "płaszczyzna zewnętrzna prawej ściany skrzynki (ściana -42..-40)"},
    "dc_pos_y":         {"value": 89,   "status": "ZALOZENIE", "zrodlo": "R50-3", "opis": "oś gniazda w ścianie skrzynki"},
    "dc_pos_z":         {"value": 30,   "status": "ZALOZENIE", "zrodlo": "Z27/R50-3"},
    "dc_pocket_depth":  {"value": 22,   "status": "ZALOZENIE", "zrodlo": "R50-3", "opis": "już nie zależy od wtyku (wtyk wzdłuż X)"},
    "dc_pocket_w":      {"value": 51,   "status": "ZALOZENIE", "zrodlo": "R50-4", "opis": "okno x -93..-42; skrzynka x -97.5..-40 (lewa ściana skrzynki = ściana korpusu)"},
    "dc_pocket_x_window": {"value": -67.5, "status": "ZALOZENIE", "zrodlo": "R50-4", "opis": "środek okna w tylnej ścianie"},
    "dc_socket_body_l": {"value": 18,   "status": "DO_ZMIERZENIA", "pomiar": 16, "zrodlo": "R50-3", "opis": "proxy: walec ø12 od x -40 w +X; wolne 50"},
    "dc_bush_inner_d":  {"value": 8.2,  "status": "ZALOZENIE", "zrodlo": "R50-3", "opis": "tulejka redukcyjna ø12/ø8,2 x 2, kołnierz ø15 x 1 (ramka_tulejka_dc_v2.stl)"},
    "usb_cut_w":        {"value": 16,   "status": "ZALOZENIE", "zrodlo": "R50-5"},
    "usb_cut_h":        {"value": 9,    "status": "ZALOZENIE", "zrodlo": "R50-5"},
    "usb_slot_pitch_min": {"value": 20, "status": "ZALOZENIE", "zrodlo": "R50-5"},
    "usb_slot_pitch_max": {"value": 28, "status": "ZALOZENIE", "zrodlo": "R50-5"},
    "usb_slot_w":       {"value": 3.2,  "status": "ZALOZENIE", "zrodlo": "R50-5", "opis": "rowki poziome 3,2 x 7,2 w (60 ± 10..14, Z 24)"},
    "usb_hole_pitch":   {"value": 22,   "status": "DO_ZMIERZENIA", "pomiar": 17, "opis": "używane tylko przez proxy flanszy; korpus ma rowki (R50-5)"}
  },
  "blat_rama_wkladka": {
    "snap_hook_z":      {"value": 52.85, "status": "LICZONE", "wzor": "korpus_h - 6.75", "zrodlo": "R50-1", "opis": "globalnie; lokalnie -10,75 bez zmian"}
  },
  "sterowanie": {
    "quantities": {"value": {"ramka_tulejka_dc": 2, "ramka_podkladka_panelu_05": 8, "ramka_podkladka_panelu_1": 8, "ramka_podkladka_panelu_2": 8}, "status": "ZALOZENIE", "zrodlo": "R50-3/R50-8", "opis": "DOPISAĆ do istniejącego słownika; druk własny, nie w arkuszu zamówienia drukarni"},
    "materials":  {"value": {"ramka_tulejka_dc": "żywica (firma)", "ramka_podkladka_panelu_05": "żywica/PETG", "ramka_podkladka_panelu_1": "żywica/PETG", "ramka_podkladka_panelu_2": "żywica/PETG"}, "status": "ZALOZENIE", "zrodlo": "R50-3/R50-8", "opis": "DOPISAĆ"}
  }
}
```

Klucze, które po R50 zostają DO_ZMIERZENIA, ale **żadna część drukowana od nich nie zależy** (używa ich tylko `.blend`/proxy i dobór sprzętu): `panel_led_h`, `panel_bottom_parts_h` (do +5), `pi_stack_h` (do +5), `panel_hole_pitch_x/y` (110–130, kwadrat), `panel_hole_offset_x/y` (0), `panel_hole_threaded`, `panel_conn_zone_*`, `bonnet_dc_*`, `dc_socket_body_l`, `usb_hole_pitch` (20–28 poziomo), `receiver_*`.

### 5.2 Sekcje planu do edycji

| Sekcja | Zmiana |
|---|---|
| 1: Z8, Z9, Z10, Z27 | dopisać zapas +5 (Z8/Z9), rowek 110–130 (Z10), gniazdo w bocznej ścianie kieszeni + okno 51 (Z27) |
| D1, D4 | łańcuch: 3 + 5 + 26 + **8** + 12 = 54; … = 63,6; korpus 59,6; dystans 50; uwaga „[cytat usuniety]” |
| D10 | Pi w (−50, −28); usunąć „krawędź SD wystaje 12 mm poza panel” |
| D13 / R5 | F‑F 50 + wkręt dociskowy M3 × 5; wariant bez gwintu: tulejka klejona + F‑F 45 (R50‑7) |
| D14 | kieszeń: okno x −93…−42, skrzynka do lewej ściany; gniazdo w prawej ścianie skrzynki (−40, 89, 30) osią X; tulejka ø8 |
| 3.2, 3.3 | nowe/zmienione klucze z 5.1 |
| 4.3 | cecha 1 (stadiony + rowki), 2 (bossy Pi (−46,5/11,5, ±24,5)), 3 (SD (−49, 0)), 4 (wloty (−8, ±10)), 6 (kieszeń, gniazdo, okno USB 16 × 9 + rowki), 7 (napis Z 51), gabaryt 200 × 200 × 59,6 |
| 4.11 | wiersze: łańcuch, panel na słupkach, kieszeń DC, wtyk Bonnetu, uchwyty (bez zmian), nowy wiersz „rowki panelu vs sąsiedzi”, „okno USB vs rowki 2,4” |
| 5 | dystanse F‑F 50 × 8 + F‑F 45 × 8, wkręty dociskowe M3 × 5, tulejki F‑F M3 × 5, epoksyd, podkładki M3 |
| 7 | tabela: podkładki panelu (stadion, rowek), bossy Pi, kieszenie zatrzasków Z 52,6…55,1, słupki blatu oś Z 55 |
| 9 | krok 8 (montaż panelu w obu wariantach), krok 12 (tulejka DC) |
| 10 | #5/#6: kryterium „kwadrat 110–130, offset ≤ 0,5 → bez wiercenia”; #9: „≤ 31 z taśmą”; #4: „≤ 17 z kablami”; #16: tylko ø (8 → tulejka); #17: „rozstaw 20–28 poziomo → bez wiercenia” |
| 11 | korpus 215 → ~225 cm³ |
| 12.1 | dodać `ramka_tulejka_dc_v2.stl`, `ramka_podkladka_panelu_{05,1,2}_v2.stl` (etap C, druk własny; poza arkuszem drukarni) |
| 13 | wpisy R50‑1…R50‑8 |
| Protokół | tabela 1: korpus 204 × 202,6 × **59,6**; K‑34 (54,4/54,7 → 59,4/59,7); K‑35 (SD −49, wloty −8; rowki: (60, 60, 1,5) POZA, (55, 55, 1,5) POZA, (65, 65, 1,5) POZA, (58, 62, 1,5) W (obok rowka: odległość od osi 2,8 > 1,7), pogłębienie (62,5, 60, 0,5)… → (60, 60, 0,5) POZA, (60, 56, 0,5)…); K‑36 (stadion: (62, 62, 3,5) W; bossy Pi (−46,5, −24,5)…); K‑38 (gniazdo: (−41, 89, 30) POZA, (−41, 89, 37) W, (−41, 83…95, 30) POZA; okno x −93…−42: (−90, 99, 26) POZA, (−95, 99, 26) W; skrzynka: (−96, 85, 26) W (ściana korpusu), (−79, 85, 26) POZA (brak ściany −80)); K‑39 (okno 16 × 9: (60, 98,75, 28,4) POZA, (60, 98,75, 29) W; rowki: (50, 98,75, 24) POZA, (56, 98,75, 24) W (ścianka 2,4), (71, 98,75, 24) POZA; wkręty (±75, 55)); K‑42 (Z 52,8…55,1); K‑43 (Z 46…56 / 35…41); K‑44b (proxy (−50, −28); luz 42 − 34 ≥ 8; wtyk 40 w −X od (−50, 22)); K‑46/K‑47 (uwagi globalne +5); K‑49; K‑54 (blat 63,6, dyfuzor 63,6, rama wkładki 69,6, płytka 74,1, pokrywka 90,1, min Z pokrywki 70,1, proxy panel 42, PCB 54…55,6) |

---

## 6. Uproszczenia konstrukcji — co można bezpiecznie usunąć lub uprościć

Rozszerzenie zadania (sesja nadzorująca). Oceniam każdą cechę obudowy i wkładki (4.3–4.6, 7) wg: funkcja → co bez niej → ile upraszcza (booleany / części / czynności montażu / cm³) → czy bezpieczne → **TAK/NIE**. Płytek nie zmieniam. Uwzględniam R49 (bez wkładek gwintowanych) i R51 (napis „PRZÓD” już usunięty, nasada L, żebra od krawędzi podkładki). Oznaczenia U‑n = uproszczenie.

### 6.1 Tabela ocen

| U‑n | Cecha (gdzie) | Funkcja | Co się stanie bez niej | Zysk | Bezpieczne? | Rekomendacja |
|---|---|---|---|---|---|---|
| U‑1 | **Rama dyfuzora jako osobna część** (4.5, D13) | ustala panel w XY względem okna (luz 0,5), zamyka szczelinę świetlną/pyłową panel–blat, dociska? nie (panel na słupkach) | Panel ustalają 4 słupki M3 w otworach panelu (±0,2) — rama nic nie dodaje w XY. Szczelina świetlna: między PCB 160 a oknem blatu 158 jest nakładka 1 na stronę, dyfuzor 160 leży w kieszeni 162 → światło z krawędzi diod (lico 2 nad PCB, 4 pod dyfuzorem) może wyjść bokiem pod blat: blat ma spód na Z 59,6 (po R50‑1), PCB na 54…55,6 → szczelina 4 mm wysokości wokół panelu, otwarta do wnętrza obudowy; **przez tę szczelinę światło i pył idą pod blat, nie na zewnątrz** (korpus zamknięty). Jedyny zewnętrzny wyciek: luz kołnierza blatu 0,5 — to już dziś istnieje (D14 traktuje go jako wylot). | −1 część × 2 (20 cm³, 35–90 zł), −4 bossy ø8 × 6 pod blatem, −4 otwory ø2,5 × 7, −4 wkręty M3 × 10, −1 czynność montażu, −K‑48, −K‑49 (część), −K‑33 (część); 1 bryła mniej w K‑53 | TAK pod warunkiem R50‑1 (panel na słupkach jest ustalony niezależnie od ramy) | **TAK** — usunąć ramę i 4 bossy pod blatem (czysty spód blatu; K‑47 „[cytat usuniety]” znika). Jeśli właściciel chce uszczelnić światło: pasek pianki EPDM 5 × 3 samoprzylepny na spodzie blatu wokół okna (lista zakupów, 5 zł) — lepszy niż sztywna rama na SLS ±0,3 |
| U‑2 | **2 wkręty tylne blatu** (D9, R7: słupki 8 × 6 × 10, otwory ø2,5 × 6, pogłębienia stożkowe w ścianie) | zabezpieczają blat przed zdjęciem bez narzędzia (dzieci, przenoszenie) | 4 zatrzaski (haczyk 1,3 w kieszeni 1,0, 0,8 zahaczenia) trzymają blat 200 × 200 z wkładką i płytką (ok. 250 g) z dużym zapasem; ramka stoi na parapecie, nie jest przenoszona za blat. Bez wkrętów blat zdejmuje się palcami, co i tak wymaga plan 9 (wkładka, płytka, Hall). | −2 słupki, −2 otwory poziome (trudne booleany: oś Y w kołnierzu, R49a), −2 otwory stożkowe w ścianie korpusu, −2 wkręty, −K‑39 (część), −K‑47 (słupki), −wiersz 4.11 „słupki a szczeliny” | TAK | **TAK** — usunąć słupki i wkręty; `blat_screw_*` → 0 szt. Zostaje 4 × zatrzask |
| U‑3 | **4 zatrzaski vs tylko wkręty** | j.w., bez narzędzi | Odwrotny wariant (tylko wkręty): 4 wkręty M3 przez ścianę w słupki kołnierza — każda regulacja Halla = wkrętak; haczyki wymagają nacięć (8 cięć) i rampy — to są najtrudniejsze booleany blatu (U‑5/U‑9 wykonawcy) | − | — | **NIE** — zatrzaski zostają (U‑2 usuwa wkręty, nie zatrzaski). Uproszczenie w obrębie zatrzasków: **nacięcia `snap_notch_w` można usunąć**, jeśli ramię sprężyste zastąpić samym ugięciem kołnierza 2 mm × 10 wys. na długości 8: ugięcie 1,3 przy PA12 i ramieniu 10 bez nacięć wymaga siły ~ 15–20 N na haczyk — za sztywno (blat trzeszczy przy zdejmowaniu). Zostawić nacięcia |
| U‑4 | **Daszki nad szczelinami** (R24, 20 szt.) | chronią szczeliny wylotowe (Z 8) przed pyłem opadającym z góry i zalaniem | Szczeliny są 8 mm nad parapetem na bocznych i tylnej ścianie, 3 mm wysokie, otwarte poziomo; pył z góry spada na parapet, nie do szczeliny; woda z podlewania — ramka nie stoi w donicy. Daszki to 20 unii po różnicy (osobny etap w planie wykonawcy), +2 mm gabarytu z każdej strony (204 × 202,6), kolizja z wygładzaniem parowym (cienkie 1,5). | −20 brył, gabaryt 200 × 200 (prostsze K‑02), −K‑37 (część daszkowa), ~ −1,5 cm³ | TAK | **TAK** — usunąć daszki (`vent_hood_l` 0). Alternatywa z tą samą funkcją i bez brył: szczeliny **pochylone** 45° w dół na zewnątrz (jedna bryła tnąca obrócona zamiast prostokąta) — NIE rekomenduję, tnące pod kątem w ścianie 2,5 dają ostrza; po prostu usunąć |
| U‑5 | **Żebra korpusu** (R23/R51, 4 × 2 × 6 po przekątnych) | sztywność dna 3 mm 195 × 195 (ugięcie pod ciężarem panelu ~ 200 g + Pi) | Dno 3 mm PA12 na 195: ugięcie pod 0,5 kg rozłożonym < 0,3 mm (E ≈ 1,7 GPa); panel i tak stoi na 4 słupkach przy (±60, ±60), blat opiera się na ścianach; dno nie jest widoczne; stopki w narożnikach. Żebra po R50‑2 zaczynają się od końca stadionu i są przerwane niczym (R23) — 4 bryły + styk z podkładką. | −4 bryły, −K‑44 (żebra), −~2 cm³ | TAK | **TAK** — usunąć (`rib_h` 0 / flaga `ribs` false). Zysk mały, ryzyko zero |
| U‑6 | **Szczelina SD w dnie** (Z14, 10 × 16 R2) | wyjęcie karty bez demontażu (obudowa na boku) | Bez szczeliny: karta = zdjąć blat (zatrzaski, bez narzędzi po U‑2), odpiąć taśmę, wyjąć panel (4 wkręty od spodu) — ok. 5 min; karta wyjmowana raz na rok (reinstalacja); alternatywa: `ssh` i obraz z sieci. Szczelina to 1 bryła tnąca + 1 sonda K‑35, ale **jest jedynym miejscem, gdzie pył wchodzi do komory elektroniki z dołu** (D14 mówi „skierowana w dół spełnia wymóg pyłowy” — dyskusyjne). | −1 bryła, −1 sonda, +pył chroniony | TAK | **TAK** — usunąć (`sd_slot` 0). Pi po R50‑6 leży pod środkiem panelu i tak; dostęp do karty = zdjęcie panelu |
| U‑7 | **Kieszeń DC** (Z27: skrzynka 36/51 × 24 × 22, okno, R50‑3/4) vs **gniazdo w licu tylnej ściany + wtyk kątowy wystający 15** | wtyk nie wystaje poza obrys 200 (ramka poranna chowana do szafki) | Z gniazdem w licu ściany wtyk kątowy wystaje 12–15 za tył ramki; w szafce to on obiera uderzenia i wyłamuje gniazdo z PA12 (ściana 2,5). Decyzja Z27 jest właściciela i ma powód. Skrzynka to 1 unia + 2 różnice + otwór; po R50‑4 bez ścianki −80 → jeszcze prostsza. | −3 bryły, −K‑38, −~4 cm³ | NIE (łamie Z27) | **NIE** — zostaje; przyjąć R50‑3/R50‑4 (prostsza niż dziś: gniazdo w płaskiej ścianie skrzynki, bez osi w dnie) |
| U‑8 | **Uchwyty kabli drukowane** (4.9, 4 szt. + 2 bossy ø8 × 5 w korpusie + 2 wkręty) vs **podstawki opasek samoprzylepne** + płytka proto na taśmie dwustronnej | trzymają płytkę proto Halla (30 × 20 w rowku) i 3 wiązki | Podstawka samoprzylepna 20 × 20 (0,5 zł) + opaska = ta sama funkcja; płytka proto przyklejona taśmą 3M VHB do dna albo do ściany na Z 40. PA12 jest chłonny/porowaty — klej samoprzylepny trzyma słabiej (przemyć IPA, docisnąć); w razie czego kropla CA. | −1 STL, −4 części, −2 bossy, −2 otwory, −K‑52, −K‑36 (część), −6 cm³ × 4 | TAK (części ukryte) | **TAK** — usunąć uchwyty i bossy; lista zakupów: 6 podstawek opasek samoprzylepnych 20 × 20, taśma VHB |
| U‑9 | **Rowki i kanały kablowe we wkładce** (4.6.6–7: rowek 1,5 × 1,5 na 3 bokach, kanał 2 × 1,2 pod uchem, przelot 2,5 × 1,5 w narożniku, kanał 2,5 × 1,0 pod półką) vs przewody przyklejone | prowadzą 3 × 3 żyły AWG 28 od czujników do szczelin blatu bez podniesienia wkładki | Wkładka leży płasko na dyfuzorze (R30, K‑33): przewód AWG 28 (ø 0,9–1,2 z izolacją) pod ramą **podniósłby ją o 1 mm** → luz płytka–półka i magnes–czujnik się zmieniają; dlatego kanały są potrzebne tam, gdzie przewód przechodzi pod ramą. Ale: kanał pod półką (2,5 × 1,0) + przelot w ściance narożnika + rowek zewnętrzny to 3 bryły na narożnik × 3 + 2 kanały uszu = 11 brył; wszystkie sondy K‑25/K‑29/K‑30. **Uproszczenie bez utraty funkcji:** jeden **rowek 2,0 × 1,2 od spodu** biegnący od kieszeni Halla prosto (po przekątnej narożnika) do zewnętrznej krawędzi ramy i dalej wzdłuż zewnętrznej dolnej krawędzi do ucha — tj. scalić „kanał pod półką + przelot + rowek” w jedną bryłę tnącą o stałym przekroju (ścieżka L lub przekątna + prosta). | 11 → 8 brył (kanał pod półką zostaje; przelot + rowek = 1 bryła na narożnik), −sondy K‑25 (przelot), K‑30 prostsze | TAK (przekrój 2,5 × 1,5: 2 żyły AWG 28 ø0,9 obok + 1 nad; półka nad kanałem 1,5 ✓ R20; ścianka ramy do otworu 52,3 − 2,5 − 48,3 = 1,5 ✓) | **TAK w wersji scalonej:** kanał pod półką 2,5 × 1,0 bez zmian; przelot w ściance i rowek zewnętrzny jako **jedna bryła 2,5 szer. × 1,5 wys.** (rowek 1,5 → 2,5 szer.). Przyklejanie przewodów zamiast kanałów → NIE: ucho i rama leżą płasko (R30), przewód pod nimi podniósłby wkładkę o 1 mm |
| U‑10 | **Uszy wkładki z kołkami ø3 i magnesami + nasada L** (D12, R47, R51) vs **wkładka trzymana tylko magnesami bez kołków** | kołki = powtarzalność ±0,15 położenia wkładki (→ płytki → kalibracji gniazdo→dioda); magnesy = docisk; uszy = miejsce na jedno i drugie poza dyfuzorem (w litym blacie) | Bez kołków: magnesy ø5 w kieszeniach 5,4 centrują wkładkę z dokładnością ~ ±0,5 (magnes–magnes przyciąga, ale nie prowadzi); wkładka na gładkim dyfuzorze może przesunąć się przy wkładaniu płytki (kołek orientacyjny dociska płytkę do narożnika D → siła boczna na wkładkę). Kalibracja (krok 13) toleruje ±1,25 (pół piksela) — ±0,5 by przeszło, ale wkładka „pływa” przy każdym użyciu i gniazdo ø3 (światło) ma na to tylko 0,5 zapasu nad pikselem 2,5. Uszy są też jedynym miejscem na magnesy (rama 4 mm szeroka leży na dyfuzorze — magnes w dyfuzorze nie). | −2 kołki, −2 otwory ślepe w blacie (R8), −K‑47 (kołki), −sondy K‑29 | NIE (powtarzalność) | **NIE** — uszy, kołki i magnesy zostają. Dopuszczalne mniejsze: **kołki ø3 → stożkowe pełne (bez fazy jako osobnej bryły)**: wykonawca robi stożek ścięty 3,0 → 2,4 jedną bryłą (−2 bryły fazy) |
| U‑11 | **Półki narożne z kieszeniami Halla** (D5: 4 półki 12 × 12 × 2,5, 3 kieszenie 5 × 5,5 przelotowe, czujnik stoi na dyfuzorze) vs **czujniki wklejone w kieszenie blatu pod dyfuzorem** | czujnik 1,0 pod spodem płytki → magnes–czujnik 1,7 ≤ 4 | Czujnik pod dyfuzorem (2 mm) w kieszeni blatu: od magnesu (0,2 cofnięty) przez płytkę… płytka leży na czym? Bez półek płytka leży **bezpośrednio na dyfuzorze** (Z6 odrzucone) → magnes 0,2 + dyfuzor 2,0 + czujnik w kieszeni blatu pod dyfuzorem: lico czujnika na spodzie dyfuzora → 0,2 + 2,0 + 0,5 = 2,7 ≤ 4 ✓ (pole na osi ~ 80 mT > próg 40 — rezerwa 2×, wystarcza). Ale narożniki (±42, ±42) leżą **w oknie blatu** (158 → ±79) nad panelem — nie ma tam blatu ani kieszeni; czujnik musiałby stać na PCB panelu (Z 55,6) pod dyfuzorem (spód 61,6): 6 mm przestrzeni, czujnik TO‑92 leżący 1,5 + nóżki → można go przykleić do dyfuzora od spodu (kropla CA na obudowę, lico do dyfuzora). Wtedy: magnes 0,2 + dyfuzor 2 + 0,5 = 2,7 ✓, przewody 3 × 3 pod dyfuzorem po panelu (nad diodami! zasłaniają piksele na trasie do krawędzi: 3 przewody × ~1 mm na 40 mm → kilka pikseli przyciemnionych pod ramą 4 mm — trasa wzdłuż narożnika pod ramą wkładki (4 mm) i dalej pod uszami → nic widocznego). Półki znikają, kołek orientacyjny stoi wtedy na… musi stać na czymś → zostawić **półkę D** (bez kieszeni) albo kołek wyrastający z ramy (narożnik wewnętrzny ramy 4 mm szeroki → kołek 4,4 nie mieści się w 4 − 0,3; **kołek 3,0 × 3,0 w narożniku ramy** przy wycięciu 5 × 5 płytki → luz 1,0, powtarzalność ±1 ✗). | −4 półki, −3 kieszenie, −3 kanały pod półką (U‑9), −K‑24, −K‑25, −K‑55 (zmiana), wkładka = czysty pierścień + uszy (ok. −6 brył) | NIE: traci Z6 (płytka 2,5 nad dyfuzorem = ochrona dyfuzora przed rysowaniem przez płytkę PA12 z cyrkonią na wierzchu), kołek orientacyjny traci oparcie, przewody pod dyfuzorem nad diodami, czujnik klejony do pleksi (wymiana = oderwać) | **NIE** — półki i kieszenie zostają (to serce funkcji „który numer płytki”). Mniejsze: **półka D bez zmian, półki A/B/C: kieszeń przelotowa może być kwadratem 5,5 × 5,5** (jedna bryła tnąca dla wszystkich, obrót zbędny) — kosmetyka |
| U‑12 | **Kołek orientacyjny 4,4 × 4,4 × 5 na półce D** | wymusza orientację płytki (wycięcie 5 × 5) i dociska ją do narożnika D | Bez niego płytka wchodzi w 4 orientacjach → kod magnesów A/B/C czytany w złym rogu → zły numer; kalibracja gniazd nieważna. | −1 bryła, −K‑27 | NIE | **NIE** |
| U‑13 | **Wycięcie palcowe 30 w przednim boku ramy wkładki** (4.6.5) | palec pod krawędź płytki (leży 0,5 nad wierzchem półek… płytka wierzch 69,1→74,1, rama 64,6→69,6: płytka wystaje 4,5 nad ramę) | Płytka wystaje 4,5 nad ramę — da się chwycić za boki bez wycięcia? Pokrywka z kołnierzem 1,5 schodzi 4 pod wierzch płytki → między ramą a pokrywką 0,5 → **bez wycięcia pokrywki nie da się założyć na płytkę leżącą we wkładce**? Kołnierz pokrywki y −48,3…−49,8 vs rama od −48,3 → kołnierz wchodzi w otwór ramy nad fazą 1 (K‑22: dół kołnierza 65,1 vs wierzch ramy 64,6 → 0,5 nad ramą) → pokrywka NIE wchodzi w ramę, kończy się 0,5 nad nią ✓. Wycięcie służy palcowi; bez niego płytkę podważa się przez wycięcie D (5 × 5) albo chwyta za boki (4,5 mm wystaje). Technik w rękawiczkach, płytka z pracami — wycięcie 30 jest realnie wygodne. | −1 bryła, −K‑28 | TAK technicznie | **NIE** — zostaje (ergonomia technika w rękawiczkach; koszt 1 bryły) |
| U‑14 | **Napisy reliefowe**: „RAMKA WIECZORNA/PORANNA” (korpus, 0,6), „GÓRA” (pokrywka), strzałki ▼ (wkładka, R51), cyfry płytek (zamknięte) | identyfikacja W/P (Z18/Z28: jedyna różnica korpusów), góra pokrywki, przód wkładki | Napis korpusu: najdroższa cecha (K‑43, font Inter z własnym offsetem, 110 mm szer., SHA W ≠ P, 2 pliki STL). Bez niego: korpusy identyczne (1 STL, 2 szt. — prostszy arkusz), W/P oznacza naklejka albo… **matryca sama pokazuje nazwę** (ekran gotowości). Pokrywka „GÓRA”: pokrywka jest symetryczna góra/dół? nie — wierzch pełny, dół otwarty; „GÓRA” jest oczywista. Strzałki wkładki: uszy z tyłu już mówią, gdzie tył. | −K‑43, −K‑21, −K‑31, −1 STL korpusu (1 plik, qty 2), −cały moduł fontu z etapu B/C dla korpusu i wkładki (pozostaje tylko dla cyfr płytek — już zrobione) | TAK | **TAK** dla korpusu (usunąć napis; 1 STL `ramka_korpus_v2.stl` × 2; Z18 → „różnica tylko w odbiorniku USB”) i dla strzałek wkładki; **TAK** dla „GÓRA” (pokrywka jest FDM i tak — relief w FDM na wierzchu drukowanym w dół wymaga podpór/odwrócenia). Cyfry płytek bez zmian |
| U‑15 | **Promienie** (R 5 pionowe korpus/blat, R 3 dolna, R 1,5 górna blatu, R 3 pokrywka, R 1 płytka, R 2 SD, R 3 kieszeń DC, R 4,5 kołnierz, R 1 kieszeń dyfuzora, R 0,5 otwór wkładki, R 4 łapy ramy) | wygląd (zewnętrzne), unikanie karbów (wewnętrzne), pasowanie pleksi (R 1) | Wykonawca robi bryły bazowe loftem (miejsce 1) — zewnętrzne R 5/R 3/R 1,5 są już „za darmo” w bmesh; **wewnętrzne promienie na cechach tnących** (R 2 SD, R 3 okno DC, R 4,5/R 2,7 kołnierz, R 1 kieszeń dyfuzora, R 0,5 otwór wkładki) to osobne profile w każdej bryle tnącej. R 1 kieszeni dyfuzora wymaga fazowania pleksi (R29) — ostre naroże kieszeni usuwa tę czynność. | ~ −6 profili zaokrąglonych → prostokąty; −R29 (fazowanie pleksi); K‑45 (naroże) | TAK (R 2,5 wnęki korpusu zostaje w loft) | **TAK częściowo:** ostre naroża w: oknie DC, szczelinie SD (jeśli zostaje), kieszeni dyfuzora (R 1 → 0; pleksi bez fazowania), otworze wkładki (R 0,5 → 0; płytka R 1 ma luz 0,3 → naroże płytki i tak nie dotyka). **NIE** dla promieni zewnętrznych (R 5, R 3, R 1,5, R 3 pokrywki) — to wygląd, a w loft nic nie kosztują; **NIE** dla R 4,5/R 2,7 kołnierza blatu (musi pasować do wnęki R 2,5 korpusu — zostawić) |
| U‑16 | **Gniazda stopek ø10,5 × 0,5 od spodu** (4.3.10) | pozycjonują stopki samoprzylepne | Stopki samoprzylepne trzymają na płaskim; 0,5 mm wgłębienie nie trzyma ich lepiej (klej trzyma), a utrudnia wygładzanie parowe. | −4 bryły, −K‑44 (stopki) | TAK | **TAK** — usunąć (`foot_pocket_depth` 0) |
| U‑17 | **Otwory wentylacyjne ø4 × 6 w pokrywce** (4.2) | odparowanie / brak kondensacji pod pokrywką na pracach? pokrywka służy do przenoszenia (minuty) | 6 otworów ø4 w wierzchu 2 mm — w FDM to 6 mostków/obrysów, zero problemu; funkcja: pył wpada przez otwory na prace (!) podczas przenoszenia. Bez nich pokrywka jest szczelniejsza. | −6 brył, −K‑19 | TAK | **TAK** — usunąć (pokrywka pełna; kondensacja nie występuje w minutach przenoszenia) |
| U‑18 | **Rowek pokrywki w płytce** (4.1.8) | zatrzask pokrywki | **Płytki zamknięte** — stwierdzenie: rowek zależy od pokrywki (garby 0,7). Gdyby kiedyś usunąć zatrzaski pokrywki (pokrywka luźno nałożona, trzyma tarciem 0,3 luzu? nie trzyma po odwróceniu), rowek w płytkach stałby się zbędny, ale płytek nie zmieniamy → zatrzaski pokrywki zostają, żeby rowek miał sens. | — | — | **bez zmian** (stwierdzenie) |
| U‑19 | **Szczeliny wentylacyjne w ścianach (20 szt.) + wloty w dnie (2)** (D14) | konwekcja: Pi 4 pod panelem w zamkniętej obudowie; panel 64 × 64 przy typowym obrazie ramki ~ 5–8 W | Bez szczelin ścian: wlot dnem (2 × 20 × 3) i wylot luzem kołnierza blatu (0,5 × 800 = 400 mm²) — wylot większy niż 20 szczelin (20 × 36 = 720 mm²)? mniejszy, ale blat nie jest szczelny i ciepłe powietrze wychodzi górą przy ścianach. Pi 4 bez obciążenia ~ 3 W, z rpi‑rgb‑led‑matrix ~ 4–5 W (jeden rdzeń 100 %), panel 5–8 W → 10–13 W w 200 × 200 × 60 → bez wentylacji ΔT wnętrza ~ 25–30 K → Pi ~ 55–65 °C — na granicy (krok 14: < 70 °C). | −20 brył (+20 daszków, U‑4), −K‑37 | NIE do końca | **NIE** dla szczelin bocznych/tylnych (zostają, bez daszków U‑4); **TAK** zmniejszyć liczbę: tylna 8 → **4**, boczne 6 → **3** na ścianę (10 zamiast 20; 360 mm² wylotu + luz blatu) — wystarcza dla 13 W; −10 brył |
| U‑20 | **Pogłębienia ø6,5 × 2 pod wkręty panelu od spodu** (4.3.1) | łeb M3 schowany w dnie (stopki 4 mm i tak unoszą dno) | Łeb walcowy M3 2,0 + podkładka 0,5 = 2,5 < 4 (stopki) → łby mogą wystawać pod dnem; pogłębienia zbędne. Z R50‑2 pogłębienie jest rowkiem 6,5 × 17,5 — jego usunięcie upraszcza rowek do jednej bryły. | −4 bryły (rowki pogłębień), dno pod słupkiem 3 + 1 (pełne) zamiast 1 + 1 | TAK (łby 2,5 pod dnem, 1,5 zapasu do blatu stołu) | **TAK** — usunąć pogłębienia (`panel_screw_cbore_h` 0); zostaje rowek 3,4 w dnie + stadion 9 × 1 na górze |

### 6.2 Gotowe zmiany dla pozycji „TAK”

| U‑n | Parametry / sekcje planu | Rachunek 4.8 / 4.11 | Protokół: znika / zmienia się |
|---|---|---|---|
| U‑1 rama dyfuzora | `rama_*` → usunąć (lub `rama_enabled` false); `rama_boss_*` → 0; 4.5 skreślona; D13: „panel ustalony słupkami M3; szczelinę świetlną zamyka pianka EPDM 5 × 3 na spodzie blatu (opcja)”; 12.1 bez pozycji 6; R36 ilości; 11: −36 cm³; lista zakupów: −4 × M3 × 10, +pianka | luz panel–okno: PCB 160 pod oknem 158 → nakładka 1/stronę ✓ (było to samo); wysokość: rama nie była w łańcuchu ✓; K‑56 margines bez zmian; blat bez bossów: spód płaski, nic nie zachodzi na kołnierz (R44 bezprzedmiotowe) | K‑48 N/D; K‑49 → tylko blat–korpus i dyfuzor–kieszeń; K‑47 bez „bossy”; K‑33 bez „rama”; K‑53 bez pary rama–x; K‑54 bez wiersza ramy; K‑60 lista renderu bez ramy; tabela 1 bez wiersza |
| U‑2 wkręty blatu | `blat_screw_pitch`, `blat_screw_z`, `blat_screw_hole_d`, `blat_screw_csink_d`, `blat_post_*`, `blat_post_hole_depth` → usunąć; D9 „4 zatrzaski, zero wkrętów”; Z15 skreślone; 4.3.6 bez „2 otwory ø3,2 z pogłębieniem”; 4.4.3 skreślona; 7: wiersz słupków; 4.11 wiersz „słupki blatu i szczeliny kabli” → skreślony; R7, R49a bezprzedmiotowe; lista zakupów −2 M3 × 8 stożkowe | zatrzaski: 4 × 0,8 zahaczenia × 8 szer.; siła wyrwania ~ 4 × 10 N ≫ 2,5 N ciężaru; rozłączenie ręką ✓ | K‑39 bez „wkręty blatu”; K‑47 bez „słupki”; K‑53 bez wkrętów |
| U‑4 daszki | `vent_hood_*` → usunąć; R24 bezprzedmiotowe; 4.3.5 bez daszków; gabaryt korpusu 200 × 200 × 59,6 | — | K‑02 tabela 1: 200 × 200 (× 59,6 po R50‑1); K‑37 bez sond daszków |
| U‑5 żebra | `rib_w`, `rib_h`, `rib_start_r` → usunąć; R23, R51(2) bezprzedmiotowe; 4.3.11 skreślona | ugięcie dna < 0,3 (rachunek w U‑5) | K‑44 bez żeber (zostaje tylko R 3 dolnej krawędzi → przenieść do K‑34) |
| U‑6 szczelina SD | `sd_slot_*` → usunąć; Z14 → „karta po zdjęciu panelu (4 wkręty)”; 4.3.3 skreślona; D14 bez „szczelina w dnie” | — | K‑35 bez sond SD |
| U‑8 uchwyty | `holder_*`, `male_czesci.holder_*`, `proto_board_*` → usunąć; 4.9 skreślona; 4.3.9 skreślona; 7: wiersz bossów; R9, R34, R43 bezprzedmiotowe; 12.1 bez pozycji 9 (etap C = tylko .blend/rendery/arkusze); lista zakupów: +6 podstawek opasek 20 × 20, +taśma VHB; 4.11 wiersz „uchwyty kabli” skreślony | — | K‑52 N/D; K‑36 bez bossów uchwytów; tabela 1 bez wiersza |
| U‑9 kanały (scalenie) | `wire_rabbet` 1,5 → rowek zewn. **2,5 szer. × 1,5 wys.** (nowy klucz `wire_rabbet_w` 2,5); przelot w ściance (`hall_lead_channel_w` 2,5 × `hall_wall_pass_h` 1,5) = ten sam przekrój, jedna bryła ciągła od kieszeni Halla po przekątnej do rowka; 4.6.3/4.6.6 | półka nad kanałem 2,5 − 1,0 = 1,5 ✓ (R20); rowek od x 52,3 do 49,8 → do otworu 48,3 zostaje 1,5 ✓; ścianka ramy nad rowkiem 6 − 1,5 = 4,5 ✓; 3 żyły ø0,9: 2 obok (1,8 < 2,5) + 1 nad (1,5 wys.) ✓ | K‑25 (jedna sonda przelotu), K‑30 (sondy na 2,5 szer.: (50,5, 0, 0,7) POZA, (49,5, 0, 0,7) W) |
| U‑14 napisy | `label_*`, `insert_arrow_*`, `insert_label_*`, `cover_label_*` → usunąć; Z18 → „korpusy identyczne, 1 STL × 2”; D15 „ścianka gładka”; 4.2, 4.3.7, 4.6.8; R22 tylko dla cyfr płytek; R33 → 1 plik; 12.1 pozycja 8: `ramka_korpus_v2.stl`; R36 ilości; `quantities`/`materials` klucze korpusu | — | K‑43 N/D; K‑21 N/D; K‑31 N/D; K‑40 (ścianka gładka — zostaje, prostsze); tabela 1 korpus bez „+0,6 relief”; K‑54 bez reliefów |
| U‑15 promienie wewn. | `sd_slot_r` (jeśli U‑6 nie), `dc_pocket_corner_r` 3 → 0, `diffuser_pocket_r` 1 → 0, `insert_opening_r` 0,5 → 0; R29 skreślone (pleksi bez fazowania); 4.4.1, 4.6.1 | pleksi 160 w kieszeni 162 z ostrymi narożami ✓ (luz 1); płytka R 1 w otworze ostrym: naroże płytki cofnięte 0,29 od ostrego narożnika → luz ✓ | K‑45 sonda naroża (80,9, 80,9, −1) → W nadal (ostre = więcej materiału); K‑23 bez R |
| U‑16 stopki | `foot_pocket_*` → usunąć; 4.3.10 | — | K‑44 bez stopek |
| U‑17 otwory pokrywki | `cover_vent_*` → usunąć; 4.2; D8 | — | K‑19 N/D |
| U‑19 mniej szczelin | `vent_slots_rear_x` [−54, −18, 18, 54]; `vent_slots_side_y` [−36, 0, 36] | wylot 10 × 36 = 360 mm² + luz blatu 400 mm² vs wlot 2 × 60 = 120 mm² (wlot jest wąskim gardłem — **powiększyć wloty do 2 × 30 × 4 = 240 mm²**, `floor_vent_l` 30, `floor_vent_w` 4) | K‑37 sondy na nowych x/y |
| U‑20 pogłębienia | `panel_screw_cbore_d/h` → usunąć; 4.3.1 | dno 3 pod słupkiem pełne ✓; łeb 2,5 pod dnem vs stopki 4 ✓ | K‑35 bez sond pogłębień |

Suma zysku (TAK): −2 STL (rama, uchwyt) i −1 plik korpusu (W = P), ok. **−60 brył** w korpusie i blacie, −3 części kupne, −6 sprawdzeń K‑xx w całości (K‑19, K‑21, K‑31, K‑43, K‑48, K‑52) i ok. 40 sond mniej, −~45 cm³ druku (rama 36 + uchwyty 24 − bez zmian w korpusie) ≈ −60–120 zł.

### 6.3 Pięć uproszczeń o największym zysku przy zerowym ryzyku

1. **U‑14 napis korpusu** — jeden STL korpusu zamiast dwóch, znika K‑43 i cały moduł fontu dla korpusu; W/P pokazuje matryca.
2. **U‑1 rama dyfuzora** — minus cała część (2 szt., 36 cm³), 4 bossy, 4 wkręty, K‑48; panel i tak stoi na 4 słupkach M3.
3. **U‑8 uchwyty kabli** — minus STL, 4 części, 2 bossy, K‑52; podstawki opasek 20 × 20 za 3 zł.
4. **U‑4 daszki** — minus 20 brył po różnicy (najbardziej kruche miejsce booleanów korpusu), gabaryt 200 × 200.
5. **U‑2 wkręty tylne blatu** — minus słupki z poziomymi otworami (R49a), pogłębienia stożkowe, K‑39/K‑47 część; 4 zatrzaski wystarczają.

Pozostałe TAK (U‑5, U‑6, U‑9, U‑15, U‑16, U‑17, U‑19, U‑20) to drobne; warto je wziąć razem, bo każde usuwa bryły, ale żadne osobno nie jest warte kolejnej iteracji etapu B.

---

## 7. Wiadomość do sesji nadzorującej (8 linijek)

1. JUTRO (po G3 na plikach z R50): korpus W/P, blat × 2, rama dyfuzora × 2 (albo FDM) — bez pomiarów elektroniki; wkładka × 3, płytki n1–n6 i pokrywka (FDM) — po 10‑min teście #12 (karton 96 × 96 w skanerze); uchwyty FDM kiedykolwiek.
2. CZEKAJ tylko na zakupy sprzętu po pomiarach: dystanse 50 F‑F vs 45 F‑F + tulejka (#5a), tulejka DC ø8 (#16), ewentualne wiercenie dna/flanszy USB (#5/#6, #17). Żadna część drukowana nie czeka.
3. R50‑1 (najważniejsze): `pi_clearance_top` 3 → 8 ⇒ panel_pcb_z 54, blat_top 63,6, korpus_h 59,6, dystans 50 (stock); koszt: +5 mm wysokości (63,6 > spec 60 o 3,6 — decyzja właściciela), +20–35 zł; pokrywa taśmę HUB75 i złącza panelu z kablami oraz led_h 1–3.
4. R50‑6: Pi z (−92) na (−50, −28) ⇒ każdy kierunek wtyku DC Bonnetu (wtyk 40 mm) ma miejsce; koszt 0 zł, 3 liczby (pi_pos_x, sd_slot_x, floor_vent_x).
5. R50‑3/4: gniazdo DC w prawej ścianie skrzynki (−40, 89, 30) osią X, otwór ø12 + tulejka redukcyjna ø8 (druk własny), okno kieszeni 51 do lewej ściany ⇒ kieszeń i dystans panelu niezależne od gniazda/wtyku; koszt 0 zł.
6. Ponadto: R50‑2 rowki 3,4 po przekątnej (rozstaw 110–130) zamiast otworów (±60,±60) + fallback wiertło; R50‑5 okno USB 16 × 9 i rowki 20–28; R50‑7 F‑F + wkręt dociskowy / tulejka klejona; R50‑8 podkładki 0,5/1/2.
7. Sekcja 6 (uproszczenia): TOP‑5 zero ryzyka — bez napisu korpusu (1 STL), bez ramy dyfuzora, bez uchwytów kabli, bez daszków, bez wkrętów tylnych blatu; razem ok. −60 brył, −6 K‑xx, −60–120 zł. NIE: kieszeń DC, kołek, półki Halla, uszy/kołki wkładki, zatrzaski.
8. Wszystko w `analiza_odpornosc_R50.md` (sekcje 1–7, blok JSON w 5.1, lista sekcji planu i sond w 5.2/6.2). Nic nie wdrożone; parametry.json i plan nietknięte.
