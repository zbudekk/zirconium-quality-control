# R50 — wdrożenie zatwierdzonych zmian do źródła prawdy (lista edycji)

Data: 2026‑10‑26. Zakres: `parametry.json`, `plan_ramki_v2.md`, `protokol_weryfikacji_v2.md`. NIE dotknięto: `ramka_generator.py`, `wyniki_v2/`, `recenzja/`. Decyzje właściciela: R50‑1…R50‑8 wszystkie TAK (wariant podstawowy); uproszczenia TAK: U‑1 (bez pianki), U‑4, U‑5, U‑6, U‑8, U‑9, U‑10 (drobne), U‑15 (tylko naroża wewnętrzne), U‑16, U‑17, U‑19, U‑20; U‑14 tylko relief „[cytat usuniety]”; NIE: U‑2, U‑3, U‑7, U‑11, U‑12, U‑13. Źródło analiz: `analiza_odpornosc_R50.md`.

Zasada zapisu w JSON (R50‑JSON): **cecha usunięta = klucze usunięte**; **cecha zmieniona = wartość zmieniona** (promień → 0). Walidator wykonawcy (R14) musi: wykreślić 49 kluczy usuniętych z listy wymaganych, dodać 21 nowych, dopisać 4 nowe wzory LICZONE.

---

## 1. `parametry.json` — klucze NOWE (21) — do dopisania w walidatorze

| Sekcja | Klucz | Wartość | Status | Źródło |
|---|---|---|---|---|
| panel_dyfuzor_pi | panel_slot_pitch_min | 110 | ZALOZENIE | R50‑2 |
| panel_dyfuzor_pi | panel_slot_pitch_max | 130 | ZALOZENIE | R50‑2 |
| panel_dyfuzor_pi | panel_slot_w | 3.4 | ZALOZENIE | R50‑2 |
| korpus | dc_socket_axis | "X" | ZALOZENIE | R50‑3 |
| korpus | dc_pos_y | 89 | ZALOZENIE | R50‑3 |
| korpus | dc_pocket_x_window | −67.5 | ZALOZENIE | R50‑4 |
| korpus | usb_slot_pitch_min | 23 | ZALOZENIE | R50‑5 (23, nie 20 z analizy: ścianka do okna 1,9) |
| korpus | usb_slot_pitch_max | 28 | ZALOZENIE | R50‑5 |
| korpus | usb_slot_w | 3.2 | ZALOZENIE | R50‑5 |
| blat_rama_wkladka | wire_rabbet_w | 2.5 | ZALOZENIE | R50‑U9 |
| male_czesci | dc_bush_outer_d | 12 | ZALOZENIE | R50‑3 |
| male_czesci | dc_bush_inner_d | 8.2 | ZALOZENIE | R50‑3 |
| male_czesci | dc_bush_t | 2 | ZALOZENIE | R50‑3 |
| male_czesci | dc_bush_flange_d | 15 | ZALOZENIE | R50‑3 |
| male_czesci | dc_bush_flange_t | 1 | ZALOZENIE | R50‑3 |
| male_czesci | panel_shim_d | 9 | ZALOZENIE | R50‑8 |
| male_czesci | panel_shim_hole_d | 3.4 | ZALOZENIE | R50‑8 |
| male_czesci | panel_shim_t | [0.5, 1, 2] | ZALOZENIE | R50‑8 |
| sterowanie | color_plexi | "#e8ecef" | ZALOZENIE | R27 |
| sterowanie | color_pcb | "#1f6b3a" | ZALOZENIE | R27 |
| sterowanie | color_brass | "#c8a24a" | ZALOZENIE | R27 |

## 2. `parametry.json` — klucze USUNIĘTE (49) — do wykreślenia z walidatora

| Sekcja | Klucze | Powód |
|---|---|---|
| pokrywka | cover_label_h, cover_vent_d, cover_vent_pitch, cover_vent_cols_x, cover_vent_rows_y | R50‑U14 (relief „GÓRA”), R50‑U17 (otwory) |
| panel_dyfuzor_pi | sd_slot_l, sd_slot_w, sd_slot_x, sd_slot_y, sd_slot_r | R50‑U6 |
| korpus | panel_screw_cbore_d, panel_screw_cbore_h | R50‑U20 |
| korpus | vent_hood_l, vent_hood_t, vent_hood_angle, vent_hood_side_margin | R50‑U4 |
| korpus | foot_pocket_depth, foot_pocket_d | R50‑U16 |
| korpus | holder_pos_x, holder_pos_y, holder_axis, holder_boss_d, holder_boss_h | R50‑U8 |
| korpus | rib_w, rib_h, rib_start_r | R50‑U5 |
| blat_rama_wkladka | rama_outer, rama_inner, rama_h, rama_screw_pos, rama_ear_t, rama_ear_d, rama_ear_hole_d, rama_tab_size, rama_tab_inner, rama_boss_d, rama_boss_h | R50‑U1 |
| male_czesci | holder_l, holder_w, holder_h, holder_foot_t, holder_slot_w, holder_slot_h, holder_comb_t, holder_board_groove_w, holder_board_groove_depth, proto_board_l, proto_board_w | R50‑U8 |
| sterowanie | cover_label_text | R50‑U14 |

Liczba kluczy (bez `_meta`): 301 → **273** (−49 + 21).

## 3. `parametry.json` — wartości / statusy ZMIENIONE

| Klucz | Było → Jest | Źródło |
|---|---|---|
| pi_clearance_top | 3 → **8** | R50‑1 |
| panel_pcb_z (LICZONE) | 49 → **54** | R50‑1 |
| blat_top_z (LICZONE) | 58.6 → **63.6** | R50‑1 |
| korpus_h (LICZONE) | 54.6 → **59.6** | R50‑1 |
| panel_standoff_l (LICZONE) | 45 → **50** | R50‑1/R50‑7 |
| snap_pocket_z | 47.6 ZALOZENIE → **52.6 LICZONE** (wzor `korpus_h - 7`) | R50‑1 |
| snap_hook_z | 47.85 ZALOZENIE → **52.85 LICZONE** (wzor `korpus_h - 6.75`) | R50‑1 |
| blat_screw_z | 50 ZALOZENIE → **55 LICZONE** (wzor `korpus_h - 4.6`) | R50‑1 |
| label_pos_z | 46 ZALOZENIE → **51 LICZONE** (wzor `korpus_h - 8.6`) | R50‑1 |
| pi_pos_x | −92 → **−50** | R50‑6 |
| floor_vent_x | −60 → **−8** | R50‑6 |
| bonnet_dc_pos_x / _y | −60 / −28 → **−50 / 22** (DO_ZMIERZENIA) | R50‑6 / A‑4 |
| bonnet_dc_dir | "−Y" → **"−X"** (DO_ZMIERZENIA) | R50‑6 / A‑4 |
| bonnet_dc_plug_len | 15 → **40** | R50‑6 |
| dc_hole_d | 12 DO_ZMIERZENIA → **12 ZALOZENIE** | R50‑3 |
| dc_pos_x | −60 → **−40** (płaszczyzna prawej ściany skrzynki) | R50‑3 |
| dc_pocket_depth | 22 DO_ZMIERZENIA → **22 ZALOZENIE** | R50‑3 |
| dc_pocket_w | 36 → **51** | R50‑4 |
| dc_pocket_corner_r | 3 → **0** | R50‑U15 |
| dc_socket_body_l | 12 → **18** (DO_ZMIERZENIA, tylko proxy) | R50‑3 |
| usb_cut_w / usb_cut_h | 15 / 8 DO_ZMIERZENIA → **16 / 9 ZALOZENIE** | R50‑5 |
| vent_slots_rear_x | [−63, −45, −27, −9, 9, 27, 45, 63] → **[−54, −18, 18, 54]** | R50‑U19 |
| vent_slots_side_y | [−45, −27, −9, 9, 27, 45] → **[−36, 0, 36]** | R50‑U19 |
| floor_vent_l / floor_vent_w | 20 / 3 → **30 / 4** | R50‑U19 |
| diffuser_pocket_r | 1 → **0** | R50‑U15 |
| insert_opening_r | 0.5 → **0** | R50‑U15 |
| quantities | −ramka_rama_dyfuzora, −ramka_uchwyt_kabli; +ramka_tulejka_dc 2, +ramka_podkladka_panelu_05/_1/_2 po 8 | R50‑U1/U8/3/8 |
| materials | per część: korpusy, blat, wkładka, płytki n4–n6 „[cytat usuniety]”; n1–n3 „[cytat usuniety]”; pokrywka „[cytat usuniety]”; tulejka, podkładki „[cytat usuniety]” | decyzja właściciela |
| opisy (bez zmiany wartości) | pi_boss_d (wkręt w PA12 zamiast wkładki), pi_stack_h, panel_pad_d (stadion), panel_screw_hole_d, insert_depth_m3 (nieużywane), foot_d, foot_edge_offset, dc_socket_body_d, dc_nut_d, usb_hole_pitch (tylko proxy), blat_rib, hall_wall_pass_h (jedna bryła), tab_pin_chamfer (stożek jedną bryłą), wire_rabbet, receiver_l | R49, R50 |

Klucze DO_ZMIERZENIA po R50 (od żadnego nie zależy część drukowana): panel_led_h, panel_bottom_parts_h, panel_hole_pitch_x/y, panel_hole_offset_x/y, panel_hole_threaded, panel_conn_zone_x/y/w/h, pi_stack_h, bonnet_dc_pos_x/y, bonnet_dc_dir, dc_socket_body_l, usb_hole_pitch, receiver_l/w/h (19 kluczy).

Nowe wzory LICZONE dla skryptu (oprócz dotychczasowych korpus_h, blat_top_z, panel_pcb_z, panel_standoff_l, cover_inner_h): `snap_pocket_z = korpus_h − 7`, `snap_hook_z = korpus_h − 6,75`, `blat_screw_z = korpus_h − 4,6`, `label_pos_z = korpus_h − 8,6`.

---

## 4. `plan_ramki_v2.md` — edycje (sekcja: było → jest)

| Sekcja | Zmiana |
|---|---|
| 1 / Z8, Z9 | dopisany zapas R50‑1 (stos z taśmą do 31, złącza z kablami do 17, łącznie +5), A‑2/A‑4 |
| 1 / Z10 | rowki 110…130 po przekątnej (R50‑2), fallback wiercenie |
| 1 / Z14 | **[usunięte R50‑U6]** — karta SD po zdjęciu blatu i panelu |
| 1 / Z19 | materiały per część; rama i uchwyty usunięte |
| 1 / Z27 | okno 51, skrzynka do lewej ściany, gniazdo w prawej ścianie osią X (R50‑3/4) |
| D1 | tabela: 63,6; łańcuch z 8; SD po zdjęciu panelu; objętość 225; wysokość zamrożona po pomiarach |
| D2 | materiały i technologia per część; rama/uchwyty usunięte |
| D4 | łańcuch 54 / 63,6 / 59,6; słupki panelu F‑F 50, wkręt dociskowy, tulejka, rowek bez pogłębienia; 4 wartości LICZONE |
| D9 | luz 0,5, występ 1,3 (R48), Z 55, otwory ø2,5 × 6 (R49/R49a); U‑2 odrzucone |
| D10 | Pi w (−50, −28); usunięte „krawędź SD wystaje 12 mm”; zapasy 4 kierunków |
| D12 | rowek 2,5 × 1,5 jedną bryłą z przelotem |
| D13 | tytuł „Panel (rama dyfuzora usunięta)”; mocowanie R50‑7; **[usunięte R50‑U1]** rama, bez pianki; naroża kieszeni ostre |
| D14 | wloty 30 × 4 w (−8, ±10); 4 + 3 + 3 szczeliny bez daszków; stopki bez gniazd; kieszeń 51 do lewej ściany; gniazdo w prawej ścianie (−40, 89, 30) osią X, ø12 + tulejka; USB 16 × 9 + rowki 23…28 |
| D15 | Z 51 (= korpus_h − 8,6); napis zostaje (U‑14 dla korpusu odrzucone) |
| D16 | lista plików: 10 drukarnia + 5 druk własny; usunięte rama, uchwyt |
| 3.1 | ~~cover_vent_*~~, ~~cover_label_h~~ |
| 3.2 | panel_* opisy; panel_slot_*; pi_pos_x −50; pi_clearance_top 8; ~~sd_slot_*~~; bonnet_dc_* (−50, 22, −X, 40) |
| 3.3 | korpus_h 59,6, blat_top_z 63,6, panel_pcb_z 54, panel_pad_d stadion, panel_standoff_l 50, ~~panel_screw_cbore_*~~, insert_depth_m3 nieużywane, vent_slots 4/3, ~~vent_hood_*~~, floor_vent 30/4/−8, ~~foot_pocket_*~~, dc_hole_d, dc_socket_axis, dc_pos_x/y/z, dc_pocket_w 51, dc_pocket_x_window, dc_pocket_corner_r 0, dc_socket_body_* , ~~sd_slot_r~~, usb_cut 16/9, usb_slot_*, label_pos_z 51, snap_pocket_z 52,6, blat_screw_z 55, ~~holder_*~~, ~~rib_*~~ |
| 3.4 | tytuł bez ramy; pi_boss_d opis; snap_hook_z 52,85; snap_hook_arm_l opis; ~~rama_*~~; wire_rabbet_w; insert_opening_r 0; tab_pin_chamfer stożek |
| 3.5 | tytuł; ~~holder_*, proto_board_*~~; dc_bush_*; panel_shim_* |
| 3.6 | color_plexi, color_pcb, color_brass |
| 4.2 | pokrywka 20,0 bez reliefu i otworów; PETG FDM |
| 4.3 | gabaryt 59,6; cecha 1 stadiony + rowki bez pogłębień; 2 bossy Pi (−46,5/11,5, ±24,5); 3 **[usunięte U6]**; 4 wloty 30 × 4; 5 szczeliny 4/3 bez daszków; 6 kieszeń 51, skrzynka do ściany, gniazdo w prawej ścianie, USB 16 × 9 + rowki, wkręty blatu Z 55; 7 napis Z 51; 8 kieszenie Z 52,6; 9 **[usunięte U8]**; 10 **[usunięte U16]**; 11 **[usunięte U5]** |
| 4.4 | funkcja bez ramy; położenie globalne 63,6; naroża ostre; haczyk lokalnie −10,75 (globalnie 52,85); słupki oś −8,6 (= 55), zostają; 4 **[usunięte U1]**; rachunek słupki ±71…79 |
| 4.5 | **usunięta [R50‑U1]** — treść zastąpiona uzasadnieniem |
| 4.6 | naroża ostre; przelot + rowek jedną bryłą; rowek 2,5 × 1,5; kołek stożkiem |
| 4.9 | **uchwyt usunięty [R50‑U8]**; w zamian specyfikacja tulejki DC i 3 podkładek |
| 4.11 | łańcuch 54/63,6/59,6; nowe wiersze: zapas nad stosem, luz dioda–dyfuzor, panel na słupkach 50, rowki vs sąsiedzi, wkręt pod dnem, kanały U9, wentylacja U19, gniazdo DC w ścianie, okno USB vs rowki, odbiornik; zmienione: słupki ±71…79, haczyki 52,85…54,85, nasada L, strzałki (zamiast „Napis PRZÓD”), kieszeń DC, kieszeń zatrzasku a napis, wtyk Bonnetu; usunięte: uchwyty, rama; gwinty R49a |
| 5 | gniazdo DC (ścianka skrzynki, tulejka), wtyk kątowy, USB rozstaw 23…28, dystanse F‑F 50/45, wkręty dociskowe, tulejki F‑F, epoksyd, podkładki ø9, podstawki opasek + VHB, wkręty M3 × 10, PT 3,0 × 8 tylko 10 szt. |
| 7 | tabela: stadiony/rowki, dystanse F‑F, bossy Pi nowe, uchwyty **[usunięte]**, słupki ø2,5 × 6 lico 97,0 oś Z 55, bossy ramy **[usunięte]**, kieszenie Z 52,6; kable 1 i 4; wentylacja luz 0,5 bez daszków |
| 9 | krok 1 (zamówienie bez pomiarów), 7 (bez wkładek; tylko Pi i słupki), 8 (montaż panelu w obu wariantach + wiercenie fallback), 9 (bez ramy), 12 (gniazdo w ścianie skrzynki, tulejka, podstawki, stopki) |
| 10 | #3, #4, #5, #5a, #6, #9, #10, #16, #17 z kryteriami „korpus bez zmian / fallback”; akapit końcowy: wysokości zamrożone, `pi_clearance_top` wynikowy |
| 11 | tabela kosztów: korpus 225, blat 83, pokrywka/tulejka/podkładki druk własny, rama/uchwyt usunięte; suma 935–1 655 / 1 235–2 180 |
| 12.1 | wiersze 4, 6 (usunięty), 7, 8, 9 (tulejka + podkładki), 10 (proxy), 12 (arkusz 15 wierszy, koszt tylko drukarnia); „Nie powstaje” + rama, uchwyt |
| 13 | nagłówek; wpisy R50‑1…R50‑8, A‑1…A‑9, R50‑U1…R50‑U20 (z werdyktem), R50‑JSON |
| 14 | pozycje 18 (R49a, R51), 19 (R50), 20 (R50‑U) |

Pozostawione celowo (historia): wpisy R5–R49 w rejestrze i sekcja 14 poz. 1–17 w brzmieniu pierwotnym; 12.3 (odwołania do R23/R24 jako historycznych).

---

## 5. `protokol_weryfikacji_v2.md` — edycje

| Miejsce | Zmiana |
|---|---|
| 0.3 | układy: tulejka i podkładki zamiast ramy i uchwytu |
| Tabela 1 | pokrywka 99,6 × 99,6 × 20,0 (bez reliefu); rama **[usunięte]**; blat 83 cm³ bez bossów; korpus 200 × 200,6 × 59,6, 225 cm³; uchwyt **[usunięte]**; + tulejka 15 × 15 × 3 (0,30); + podkładki 9 × 9 × t (0,03/0,05/0,11); nagłówek sekcji 2: 17 plików |
| K‑19 | uchylone (R50‑U17), kontrola odwrotna w K‑17 |
| K‑21 | uchylone (R50‑U14), kontrola odwrotna: wierzch płaski 0,00 |
| K‑22 | 70,1 vs 69,6 |
| K‑25 | jedna bryła z rowkiem; sonda ciągłości (−51,5, −51,5, 0,7) POZA |
| K‑30 | rowek 2,5 × 1,5: (50,2, 0, 0,7) POZA; (49,4, 0, 0,7) W; (51,5, 0, 2,0) W |
| K‑34 | 59,5 / 59,4 / 59,7; + R 3 dolna (z K‑44) |
| K‑35 | rowki po przekątnych (6 POZA, 3 W), brak pogłębienia (63, 60, 0,5) W, SD brak (W), wloty (−8, ±10) 30 × 4 |
| K‑36 | stadiony (sondy 2,8 od osi), bossy Pi (−46,5/11,5, ±24,5), brak bossów uchwytów (POZA) |
| K‑37 | szczeliny tył −54/−18/18/54, boki −36/0/36, brak daszków (POZA), dawne pozycje W |
| K‑38 | okno −93…−42, brak ściany −80, lewa ściana korpusu, tylna ściana skrzynki pełna, gniazdo w prawej ścianie (−41, 89, 30) POZA + 5 sond ściany |
| K‑39 | okno 16 × 9, rowki 44,4…50,1 / 69,9…75,6, ścianki 1,9, wkręty blatu Z 55 |
| K‑40 | siatka Z ∈ [5, 57] |
| K‑42 | Z 53,8 / 52 / 55,6; dawna 48,8 → W |
| K‑43 | obszar Z ∈ [46, 56]; brak reliefu Z ∈ [35, 41] |
| K‑44 | brak żeber (POZA), brak gniazd stopek (W); R 3 przeniesione do K‑34 |
| K‑44b | proxy (−50, −28), wtyk 40 od (−50, 22) w `bonnet_dc_dir`, luz 42 − 34 ≥ 8, test 3 kierunków |
| sekcja 7 tytuł | „Blat (rama usunięta)” |
| K‑33 | 63,6 |
| K‑45 | naroża ostre: (80,5, 80,5, −1) POZA; (81,5, 81,5, −1) W |
| K‑46 | opis: globalnie 52,85…54,85, nacięcia do 58,6; sondy lokalne bez zmian |
| K‑47 | otwór ø2,5 × 6 od 97,0 do 91,0, oś lokalnie −8,6 (= 55); obie sondy (75, 89,6, −8,6) W i (75, 90,5, −8,6) W; brak bossów (90, 90, −6) POZA, (92,5, 90, −6) POZA, (90, 90, −3) W |
| K‑48 | uchylone (R50‑U1) |
| K‑49 | bez ramy; panel–blat 4,0; PCB pod oknem; dystanse na stadionach i w rowkach |
| K‑52 | uchylone (R50‑U8); nowe K‑52b (tulejka) i K‑52c (podkładki), waga P |
| K‑53 | zestaw bez ramy/uchwytu, + tulejka; pary stykowe nowe (dystanse–stadiony Z 4, panel–dystanse 54, wkładka–dyfuzor 63,6, płytka–półki 66,1) |
| K‑54 | 63,6 / 63,6 / 69,6 (71,1) / 74,1 (74,7) / 90,1 / 70,1 / 34 / 42 / 54…55,6 / 54 / 3…4 / −4…0 / 59,6 |
| K‑57 | materiał per część; koszt tylko „PA12 drukarnia”; 15 wierszy (10 + 5) |
| K‑60 | lista LICZONE: 9 wartości |
| 11 | lista renderu bez ramy i uchwytów; + wtyk DC, stadiony, tulejka; kolory `color_*` |

K‑xx uchylone przez R50: **K‑19, K‑21, K‑48, K‑52**. Nowe: **K‑52b, K‑52c**. Zmienione: K‑22, K‑25, K‑30, K‑33, K‑34, K‑35, K‑36, K‑37, K‑38, K‑39, K‑40, K‑42, K‑43, K‑44, K‑44b, K‑45, K‑46, K‑47, K‑49, K‑53, K‑54, K‑57, K‑60 (23).

---

## 6. Uwagi dla wykonawcy (etap B w toku)

1. Korpus: podstawa 200 × 200 × 59,6; podkładki jako stadiony (profil 9 szer., oś po przekątnej 14,1 długa) i rowki 3,4 (ten sam profil, węższy), bez pogłębień, bez daszków, żeber, szczeliny SD, gniazd stopek, bossów uchwytów; skrzynka DC od lewej ściany do x −40 (unia z lewą ścianą), okno 51; otwór ø12 w prawej ścianie skrzynki osią X; okno USB 16 × 9 + 2 rowki 3,2 × 5,7 (osie 48,5→46 i 71,5→74); kieszenie zatrzasków Z 52,6; wkręty blatu Z 55; napis Z 51.
2. Blat: bez 4 bossów ramy; naroża kieszeni dyfuzora ostre; reszta bez zmian (lokalnie).
3. Wkładka: naroża otworu ostre; rowek zewnętrzny 2,5 × 1,5 i przelot w ściance jako jedna bryła; kołki ø3 ze stożkiem ściętym jedną bryłą.
4. Pokrywka: bez otworów ø4 i bez „GÓRA” (etap A do ponownego eksportu pokrywki: K‑17, K‑18, K‑20, K‑22 bez zmian; K‑19, K‑21 uchylone; gabaryt 20,0).
5. Nowe STL (etap C): `ramka_tulejka_dc_v2.stl`, `ramka_podkladka_panelu_05_v2.stl`, `…_1_v2.stl`, `…_2_v2.stl`; arkusz zamówienia: 15 wierszy, koszt tylko dla „PA12 drukarnia”.
6. Bryły zastępcze: `proxy_pi_bonnet` od (−50, −28); `proxy_wtyk_bonnet` 40 × 10 × 11 w −X od (−50, 22); `proxy_dystans_1..4` ø6,4 × 50 na Z 4…54 w (±60, ±60) (z `panel_hole_*`); `proxy_panel` PCB Z 54…55,6, strefa złączy od Z 42; `proxy_gniazdo_dc` walec ø12 × 18 osią X od x −40 w +X, nakrętka ø15 × 2 na x −40…−38; `proxy_gniazdo_usb` bez zmian; `proxy_odbiornik_usb` przy portach Pi x 35…37; stopki na płaskim dnie; bez `proxy_rama`, bez uchwytów.
7. Walidator kluczy: sekcje 1–2 tego pliku; wzory LICZONE: sekcja 3.

---

## SPÓJNOŚĆ SPRAWDZONA

**Łańcuch wysokości (D4, nowe liczby):** floor_t 3 + pi_standoff_h 5 = 8 (spód PCB Pi); + pi_stack_h 26 = 34 (szczyt stosu); + pi_clearance_top 8 = 42 (spód strefy złączy panelu); + panel_bottom_parts_h 12 = **54 = panel_pcb_z**; + panel_pcb_t 1,6 + panel_led_h 2 = 57,6 (lico diod); + led_gap 4 = 61,6 (spód dyfuzora); + diffuser_t 2 = **63,6 = blat_top_z**; − blat_t 4 = **59,6 = korpus_h**; + insert_shelf_h 2,5 = 66,1 (półki); + insert_h 6 = 69,6 (rama wkładki); 66,1 + 8 = 74,1 (wierzch płytki); 74,1 − 4 + 14 = 84,1 (najwyższa praca); pokrywka: dół kołnierza 74,1 − 4 = 70,1 > rama 69,6 ✓, wierzch 74,1 + 14 + 2 = 90,1 ✓.
**Słupki panelu:** 3 + 1 + 50 = 54 ✓ (bez gwintu: 3 + 1 + 45 + 5 = 54 ✓).
**Wartości LICZONE (przeliczone skryptem z pliku):** panel_pcb_z 54 ✓, blat_top_z 63,6 ✓, korpus_h 59,6 ✓, panel_standoff_l 50 ✓, snap_pocket_z 59,6 − 7 = 52,6 ✓, snap_hook_z 59,6 − 6,75 = 52,85 ✓, blat_screw_z 59,6 − 4,6 = 55 ✓, label_pos_z 59,6 − 8,6 = 51 ✓, cover_inner_h 14 ✓. JSON parsuje się (273 klucze).
**4.11 na nowych liczbach:** haczyk 52,85…54,85 w kieszeni 52,6…55,1 → luz 0,25 ✓; kieszeń DC Z 12…40 vs kołnierz blatu od 49,6 → 9,6 ✓; wkręt blatu Z 55 vs skrzynka 40 → 15 ✓; napis Z 47…55 vs kieszeń zatrzasku Z 52,6…55,1 (relief na zewnątrz) ✓; luz dioda–dyfuzor 6 − led_h ∈ {5, 4, 3} ✓; rowki panelu (±55…65) vs skrzynka y 78 → 9,8 ✓, vs Pi x ≤ 35 / y ≤ 28 → ≥ 16,8 ✓, vs USB y 77 → 8,8 ✓; gniazdo DC ø12 w ścianie 22 × 28 (Z 24…36, y 83…95) ✓, nakrętka ø15 ✓, wtyk kątowy 26 → −68 vs −95,5 ✓, prosty 40 + 12 → −94 ✓; okno USB vs rowki 1,9 ✓ (rozstaw min 23); wtyk Bonnetu 40: −X → −90 (7,5 do ściany) ✓, −Y → −68 ✓, +Y → 68 vs skrzynka 78 ✓; rowek wkładki 2,5: ścianka do otworu 1,5 ✓; wentylacja 360 + 400 mm² wylot / 240 mm² wlot ✓; wkręt pod dnem 2,5 < stopki 4 ✓; zasady 4.8: ścianki ≥ 1,5 (pokrywka 1,5, ramię 1,5, półka 1,5, ściana za kieszenią 1,5, ścianka okno–rowek USB 1,9, dno słupka 1,8), otwory ≥ 1,5, relief 0,6, luzy 0,3/0,5/0,15 ✓, pustki otwarte (kieszeń DC otwarta oknem) ✓.

---

## 7. Dopisek [R53] (31.10.2026) — co w tym dokumencie jest już nieaktualne

Ten dokument opisuje edycje R50 (26.10). Sesja R53 (`sesje_2026-10-31/poprawki_pasowan/R53_projekt.md`, `weryfikacja_R53.md`) zmieniła 13 kluczy `parametry.json` i 4 STL; poniższe liczby z sekcji 3–6 i „SPÓJNOŚĆ SPRAWDZONA” zastępuje `parametry.json` (jedyne źródło liczb):

| Pozycja w tym dokumencie | Było (R50) | Jest (R53) |
|---|---|---|
| `snap_pocket_z` = korpus_h − 7 = 52,6; kieszenie zatrzasków 10 × 2,5 × 1,0, Z 52,6…55,1, luz 0,25 | 52,6 / 0,25 | `korpus_h − 7,5` = **52,1**; kieszeń **11 × 3,5 × 1,3**, Z 52,1…55,6, luz Z **0,75/0,75**, do dna 0,5, boczny 1,5 |
| luz kołnierza blatu 0,5 (D9, sekcja 4 p. 7, wentylacja 400 mm²) | 0,5 | **0,7** (kołnierz 193,6; wylot kołnierza 560 mm²) |
| występ haczyka 1,3 | 1,3 | **1,5** (czubek 98,3 bez zmian, zahaczenie 0,8) |
| ściana za kieszenią zatrzasku 1,5 | 1,5 | **1,2 lokalnie** (odstępstwo od 4.8, nienośne) |
| otwór wkrętu blatu w ścianie ø3,2 | 3,2 | **ø3,6** |
| słupki blatu: otwór ø2,5 × 6 od lica 97,0 do 91,0, dno 1,8 (K‑47) | 97,0 / 1,8 | od lica **96,8** do **90,8**, dno **1,6**, gwint wkrętu 4,8 |
| otwór kołka wkładki ø3,3 (wciskane 0,15) | 3,3 | **ø3,4**, pasowanie **ruchome 0,2** |
| otwór wkładki 96,6, luz płytki 0,3, rama 104,6, gabaryt 148,3, margines 27,7 | 96,6 | **96,8**, luz **0,4**, rama 104,8, gabaryt 148,4, margines 27,6; `tab_root_x_out` 52,4; `orient_post_gap` 0,6 |
| rowki pod wkręty panelu 3,4 (sekcja 6 p. 1, R50‑U20) | 3,4 | **3,6** (`panel_slot_w`, `panel_screw_hole_d`) |
| zasady 4.8 luzy 0,3/0,5/0,15 | — | ruchome 0,4 / 0,7 / 0,2; tulejka DC 11,85 w ø12 celowo wciskowa (R52) |

Proces (R53 T8, krok 7 planu wdrożenia): przed pierwszym wkręceniem przewiercić otwory ø2,1 (bossy Pi) i ø2,5 (słupki blatu). Kryterium odbioru druku: odchyłka > ±0,5 mm = reklamacja (W‑04). Tulejka DC drukowana po zmierzeniu otworu ø12 w gotowym korpusie (T7).
