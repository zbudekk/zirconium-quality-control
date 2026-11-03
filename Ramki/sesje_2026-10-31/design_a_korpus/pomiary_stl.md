# Pomiary STL — DESIGN A (31.10.2026)

Skrypt: `pomiar_stl.py` (trimesh 5.2, promienie na siatkach; cięciwa = suma odległości do pierwszych trafień w obie strony; trafienie = współrzędna pierwszej powierzchni). Tolerancja porównania 0,05 mm. Niezależnie od generatora i trzeciego oka (inne punkty sond).

## 1. Gabaryty, objętości, szczelność

| Plik | min | max | rozmiar | objętość [cm³] | szczelna |
|---|---|---|---|---|---|
| `ramka_korpus_W_v2` | [-100.0, -100.6, 0.0] | [100.0, 100.0, 59.6] | [200.0, 200.6, 59.6] | 233.66 | True |
| `ramka_korpus_P_v2` | [-100.0, -100.6, 0.0] | [100.0, 100.0, 59.6] | [200.0, 200.6, 59.6] | 233.63 | True |
| `ramka_blat_v2` | [-100.0, -100.0, 0.0] | [100.0, 100.0, 14.0] | [200.0, 200.0, 14.0] | 72.57 | True |
| `ramka_wkladka_v2` | [-65.0, -52.3, 0.0] | [65.0, 96.0, 11.0] | [130.0, 148.3, 11.0] | 12.41 | True |
| `ramka_pokrywka_v2` | [-49.8, -49.8, 0.0] | [49.8, 49.8, 20.0] | [99.6, 99.6, 20.0] | 30.06 | True |
| `ramka_tulejka_dc_v2` | [-7.5, -7.5, 0.0] | [7.5, 7.5, 3.0] | [15.0, 15.0, 3.0] | 0.24 | True |
| `ramka_podkladka_panelu_05_v2` | [-4.5, -4.5, 0.0] | [4.5, 4.5, 0.5] | [9.0, 9.0, 0.5] | 0.03 | True |
| `ramka_podkladka_panelu_1_v2` | [-4.5, -4.5, 0.0] | [4.5, 4.5, 1.0] | [9.0, 9.0, 1.0] | 0.05 | True |
| `ramka_podkladka_panelu_2_v2` | [-4.5, -4.5, 0.0] | [4.5, 4.5, 2.0] | [9.0, 9.0, 2.0] | 0.11 | True |
| `ramka_plytka_wieczorna_n1_v2` | [-48.0, -48.0, 0.0] | [48.0, 48.0, 8.6] | [96.0, 96.0, 8.6] | 57.95 | True |
| `ramka_plytka_poranna_n4_v2` | [-48.0, -48.0, 0.0] | [48.0, 48.0, 8.6] | [96.0, 96.0, 8.6] | 60.23 | True |

## 2. Wymiary (zmierzone vs nominał z `parametry.json` / planu)

| Plik | Cecha | Metoda | Zmierzone | Nominał | Δ | OK | Źródło nominału |
|---|---|---|---|---|---|---|---|
| `ramka_korpus_W_v2` | gabaryt X / Y / Z (bbox) | bbox | 200.0 | 200 | 0.0 | ✓ | box_outer |
| `ramka_korpus_W_v2` | gabaryt Y z napisem | bbox | 200.6 | 200.6 | 0.0 | ✓ | +label_relief_h 0,6 |
| `ramka_korpus_W_v2` | wysokość korpusu | bbox Z | 59.6 | 59.6 | 0.0 | ✓ | korpus_h |
| `ramka_korpus_W_v2` | objętość [cm³] | mesh | 233.661 | None |  | — | arkusz 233,66/233,63 |
| `ramka_korpus_W_v2` | wnętrze X (y 20, Z 30) | cięciwa | 195.0 | 195 | 0.0 | ✓ | box_outer-2·wall_t |
| `ramka_korpus_W_v2` | wnętrze Y (x 20, Z 30) | cięciwa | 195.0 | 195 | 0.0 | ✓ |  |
| `ramka_korpus_W_v2` | ściana prawa grubość (98,75, 20, 30) | cięciwa w materiale | 2.5 | 2.5 | 0.0 | ✓ | wall_t |
| `ramka_korpus_W_v2` | ściana przednia grubość (20, −98,75, 30) | cięciwa w materiale | 2.5 | 2.5 | 0.0 | ✓ | wall_t |
| `ramka_korpus_W_v2` | ściana tylna grubość (20, 98,75, 45) | cięciwa w materiale | 2.5 | 2.5 | 0.0 | ✓ | wall_t |
| `ramka_korpus_W_v2` | dno grubość (20, −20, 1,5) | cięciwa w materiale | 3.0 | 3.0 | 0.0 | ✓ | floor_t |
| `ramka_korpus_W_v2` | wierzch ściany Z (98,75, 20) | trafienie −Z | 59.6 | 59.6 | 0.0 | ✓ | korpus_h |
| `ramka_korpus_W_v2` | naroże pionowe R5: x lica przy y=−99 | trafienie −X | 97.999 | 98.0 | -0.001 | ✓ | box_corner_r 5 → 98,0 |
| `ramka_korpus_W_v2` | dolna krawędź R3: z lica przy x=99,5 | trafienie +Z | 1.343 | 1.3416876048223 | 0.001 | ✓ | box_edge_r 3 → 1,34 |
| `ramka_korpus_W_v2` | stadion panelu (60,60): wierzch Z | trafienie −Z | 4.0 | 4.0 | 0.0 | ✓ | floor_t+panel_pad_h (sonda 4,24 od osi rowka) |
| `ramka_korpus_W_v2` | stadion szerokość prostopadle do przekątnej: lico z zewnątrz (z (66,54,3,5) w −N) | trafienie −N | 3.985 | 3.9852813742385713 | -0.0 | ✓ | odl. 8,49 od osi − 4,5 = 3,99 |
| `ramka_korpus_W_v2` | rowek panelu szer. (60,60, Z 1,5) prostopadle do przekątnej | cięciwa N | 3.4 | 3.4 | 0.0 | ✓ | panel_slot_w |
| `ramka_korpus_W_v2` | rowek panelu długość wzdłuż przekątnej (60,60, Z 1,5) | cięciwa D | 17.542 | 17.54213562373095 | -0.0 | ✓ | (55→65)·√2 + 3,4 = 17,54 |
| `ramka_korpus_W_v2` | rowek panelu przelotowy przez dno i stadion: trafienie +Z z (60,60,−5) | trafienie +Z | None | None |  | — (przelot ✓) | brak = przelot (wkręt M3 przechodzi przez dno i stadion do dystansu) |
| `ramka_korpus_W_v2` | rowek: półdługość od (60,60,3,5) w +D (koniec rowka R1,7) | trafienie +D | 8.771 | 8.771067811865475 | -0.0 | ✓ | 5·√2 + 1,7 = 8,77 |
| `ramka_korpus_W_v2` | stadion: koniec od zewnątrz (z (80,80,3,5) w −D) | trafienie −D | 16.715 | 16.713203435596427 | 0.002 | ✓ | koniec stadionu 65 + R4,5 → 16,71 |
| `ramka_korpus_W_v2` | boss Pi (−46,5,−24,5): wierzch Z | trafienie −Z | 8.0 | 8.0 | 0.0 | ✓ | floor_t+pi_standoff_h |
| `ramka_korpus_W_v2` | boss Pi: otwór ø (Z 7) | cięciwa X | 2.1 | 2.1 | 0.0 | ✓ | insert_hole_m25 |
| `ramka_korpus_W_v2` | boss Pi: dno otworu Z | trafienie −Z | 3.0 | 3.0 | 0.0 | ✓ | 8 − insert_depth_m25 5 |
| `ramka_korpus_W_v2` | boss Pi: lico zewn. x (z (−30,−24,5,6) w −X) | trafienie −X | -42.5 | -42.5 | 0.0 | ✓ | ø8 → −46,5+4 |
| `ramka_korpus_W_v2` | boss Pi (11,5, 24,5): wierzch Z | trafienie −Z | 8.0 | 8.0 | 0.0 | ✓ |  |
| `ramka_korpus_W_v2` | wlot w dnie (−8,−10): X | cięciwa | 30.0 | 30 | 0.0 | ✓ | floor_vent_l |
| `ramka_korpus_W_v2` | wlot w dnie (−8,−10): Y | cięciwa | 4.0 | 4 | 0.0 | ✓ | floor_vent_w |
| `ramka_korpus_W_v2` | szczelina tylna (−54, Z 8): X | cięciwa | 12.0 | 12 | 0.0 | ✓ | vent_slot_w |
| `ramka_korpus_W_v2` | szczelina tylna (−54, Z 8): Z | cięciwa | 3.0 | 3 | 0.0 | ✓ | vent_slot_h |
| `ramka_korpus_W_v2` | szczelina boczna prawa (y 36, Z 8): Y | cięciwa | 12.0 | 12 | 0.0 | ✓ |  |
| `ramka_korpus_W_v2` | szczelina boczna lewa (y −36, Z 8): Z | cięciwa | 3.0 | 3 | 0.0 | ✓ |  |
| `ramka_korpus_W_v2` | okno DC (−67,5, Z 26): X | cięciwa | 51.0 | 51 | 0.0 | ✓ | dc_pocket_w |
| `ramka_korpus_W_v2` | okno DC: Z | cięciwa | 24.0 | 24 | 0.0 | ✓ | dc_pocket_h |
| `ramka_korpus_W_v2` | okno DC: dolna krawędź Z | trafienie −Z | 14.0 | 14 | 0.0 | ✓ | dc_pocket_z0 |
| `ramka_korpus_W_v2` | skrzynka DC wnętrze X (y 87,75, Z 16) | cięciwa | 53.5 | 53.5 | 0.0 | ✓ | −95,5…−42 |
| `ramka_korpus_W_v2` | skrzynka DC: ściana przednia w świetle y | trafienie −Y z zewnątrz | 80.0 | 80 | 0.0 | ✓ | 100 − dc_pocket_depth 22 + wall 2 |
| `ramka_korpus_W_v2` | skrzynka DC: sufit Z (z wnętrza) | trafienie +Z | 38.0 | 38 | 0.0 | ✓ | 40 − 2 |
| `ramka_korpus_W_v2` | skrzynka DC: dno Z (z wnętrza) | trafienie −Z | 14.0 | 14 | 0.0 | ✓ | 12 + 2 |
| `ramka_korpus_W_v2` | otwór DC ø (Y) w prawej ścianie skrzynki (x −41) | cięciwa | 11.999 | 12 | -0.001 | ✓ | dc_hole_d |
| `ramka_korpus_W_v2` | otwór DC ø (Z) | cięciwa | 11.998 | 12 | -0.002 | ✓ | dc_hole_d |
| `ramka_korpus_W_v2` | prawa ściana skrzynki grubość (−41, 81, 30) | cięciwa w materiale X | 2.0 | 2.0 | 0.0 | ✓ | dc_pocket_wall |
| `ramka_korpus_W_v2` | ścianka otwór DC – wierzch prawej ściany skrzynki (−41, 89, 37) | cięciwa w materiale Z | 4.001 | 4.0 | 0.001 | ✓ | otwór do Z 36, wierzch skrzynki Z 40 → 4,0 |
| `ramka_korpus_W_v2` | skrzynka: lewa ściana (= ściana korpusu) grubość (−96,5, 88, 26) | cięciwa w materiale X | 4.5 | 4.5 | 0.0 | ✓ | 2,5 + 2 |
| `ramka_korpus_W_v2` | okno USB (60, Z 24): X | cięciwa | 16.0 | 16 | 0.0 | ✓ | usb_cut_w |
| `ramka_korpus_W_v2` | okno USB: Z | cięciwa | 9.0 | 9 | 0.0 | ✓ | usb_cut_h |
| `ramka_korpus_W_v2` | rowek flanszy USB prawy (72,75): X | cięciwa | 5.691 | 5.7 | -0.009 | ✓ | (14−11,5)+3,2 |
| `ramka_korpus_W_v2` | rowek flanszy USB prawy: Z | cięciwa | 3.2 | 3.2 | 0.0 | ✓ | usb_slot_w |
| `ramka_korpus_W_v2` | ścianka okno USB – rowek (68,95) | cięciwa w materiale X | 1.904 | 1.9 | 0.004 | ✓ | 52−50,1 |
| `ramka_korpus_W_v2` | kieszeń zatrzasku prawa (98, 0): szerokość | cięciwa | 10.0 | 10 | 0.0 | ✓ | snap_pocket_w |
| `ramka_korpus_W_v2` | kieszeń zatrzasku prawa (98, 0): wysokość Z | cięciwa | 2.5 | 2.5 | 0.0 | ✓ | snap_pocket_h |
| `ramka_korpus_W_v2` | kieszeń zatrzasku prawa (98, 0): dolna krawędź Z | trafienie −Z | 52.6 | 52.6 | 0.0 | ✓ | snap_pocket_z |
| `ramka_korpus_W_v2` | kieszeń zatrzasku prawa (98, 0): górna krawędź Z | trafienie +Z | 55.1 | 55.1 | 0.0 | ✓ | 52,6+2,5 |
| `ramka_korpus_W_v2` | kieszeń zatrzasku lewa (−98, 0): szerokość | cięciwa | 10.0 | 10 | 0.0 | ✓ | snap_pocket_w |
| `ramka_korpus_W_v2` | kieszeń zatrzasku lewa (−98, 0): wysokość Z | cięciwa | 2.5 | 2.5 | 0.0 | ✓ | snap_pocket_h |
| `ramka_korpus_W_v2` | kieszeń zatrzasku lewa (−98, 0): dolna krawędź Z | trafienie −Z | 52.6 | 52.6 | 0.0 | ✓ | snap_pocket_z |
| `ramka_korpus_W_v2` | kieszeń zatrzasku lewa (−98, 0): górna krawędź Z | trafienie +Z | 55.1 | 55.1 | 0.0 | ✓ | 52,6+2,5 |
| `ramka_korpus_W_v2` | kieszeń zatrzasku przednia (50, −98): szerokość | cięciwa | 10.0 | 10 | 0.0 | ✓ | snap_pocket_w |
| `ramka_korpus_W_v2` | kieszeń zatrzasku przednia (50, −98): wysokość Z | cięciwa | 2.5 | 2.5 | 0.0 | ✓ | snap_pocket_h |
| `ramka_korpus_W_v2` | kieszeń zatrzasku przednia (50, −98): dolna krawędź Z | trafienie −Z | 52.6 | 52.6 | 0.0 | ✓ | snap_pocket_z |
| `ramka_korpus_W_v2` | kieszeń zatrzasku przednia (50, −98): górna krawędź Z | trafienie +Z | 55.1 | 55.1 | 0.0 | ✓ | 52,6+2,5 |
| `ramka_korpus_W_v2` | kieszeń zatrzasku tylna (−50, 98): szerokość | cięciwa | 10.0 | 10 | 0.0 | ✓ | snap_pocket_w |
| `ramka_korpus_W_v2` | kieszeń zatrzasku tylna (−50, 98): wysokość Z | cięciwa | 2.5 | 2.5 | 0.0 | ✓ | snap_pocket_h |
| `ramka_korpus_W_v2` | kieszeń zatrzasku tylna (−50, 98): dolna krawędź Z | trafienie −Z | 52.6 | 52.6 | 0.0 | ✓ | snap_pocket_z |
| `ramka_korpus_W_v2` | kieszeń zatrzasku tylna (−50, 98): górna krawędź Z | trafienie +Z | 55.1 | 55.1 | 0.0 | ✓ | 52,6+2,5 |
| `ramka_korpus_W_v2` | kieszeń prawa: dno x (z (80,0,53,8) +X) | trafienie +X | 98.5 | 98.5 | 0.0 | ✓ | 97,5 + snap_pocket_depth 1,0 |
| `ramka_korpus_W_v2` | kieszeń przednia: dno y | trafienie −Y | -98.5 | -98.5 | 0.0 | ✓ |  |
| `ramka_korpus_W_v2` | ściana za kieszenią prawą (99,25, 0, 53,85) | cięciwa w materiale X | 1.5 | 1.5 | 0.0 | ✓ | 2,5 − 1,0 |
| `ramka_korpus_W_v2` | otwór wkrętu blatu (75, Z 55): ø w ścianie (y 98,2) | cięciwa X | 3.195 | 3.2 | -0.005 | ✓ | blat_screw_hole_d |
| `ramka_korpus_W_v2` | otwór wkrętu blatu: ø przy licu zewn. (y 99,9) | cięciwa X | 6.1 | 6.1 | 0.0 | ✓ | pogłębienie ø6,3/90° → 6,1 na y 99,9 |
| `ramka_korpus_W_v2` | otwór wkrętu blatu (−75, Z 55): ø w ścianie | cięciwa X | 3.195 | 3.2 | -0.005 | ✓ |  |
| `ramka_korpus_W_v2` | otwór wkrętu blatu: ø pionowo (Z) przy y 98,2 | cięciwa Z | 3.193 | 3.2 | -0.007 | ✓ |  |
| `ramka_korpus_W_v2` | napis: lico reliefu min y (bbox) | bbox | -100.6 | -100.6 | 0.0 | ✓ | label_relief_h 0,6 |
| `ramka_korpus_W_v2` | napis: najdalszy punkt reliefu y (skan x −55…55 co 0,5, Z 51) | trafienie +Y | -100.6 | -100.6 | 0.0 | ✓ |  |
| `ramka_korpus_W_v2` | napis: zakres Z reliefu (skan) | skan | 8.0 | 8.0 | 0.0 | ✓ | label_text_h 8 (Z 47.0…55.0) |
| `ramka_korpus_P_v2` | gabaryt X / Y / Z (bbox) | bbox | 200.0 | 200 | 0.0 | ✓ | box_outer |
| `ramka_korpus_P_v2` | gabaryt Y z napisem | bbox | 200.6 | 200.6 | 0.0 | ✓ | +label_relief_h 0,6 |
| `ramka_korpus_P_v2` | wysokość korpusu | bbox Z | 59.6 | 59.6 | 0.0 | ✓ | korpus_h |
| `ramka_korpus_P_v2` | objętość [cm³] | mesh | 233.632 | None |  | — | arkusz 233,66/233,63 |
| `ramka_korpus_P_v2` | wnętrze X (y 20, Z 30) | cięciwa | 195.0 | 195 | 0.0 | ✓ | box_outer-2·wall_t |
| `ramka_korpus_P_v2` | wnętrze Y (x 20, Z 30) | cięciwa | 195.0 | 195 | 0.0 | ✓ |  |
| `ramka_korpus_P_v2` | ściana prawa grubość (98,75, 20, 30) | cięciwa w materiale | 2.5 | 2.5 | 0.0 | ✓ | wall_t |
| `ramka_korpus_P_v2` | ściana przednia grubość (20, −98,75, 30) | cięciwa w materiale | 2.5 | 2.5 | 0.0 | ✓ | wall_t |
| `ramka_korpus_P_v2` | ściana tylna grubość (20, 98,75, 45) | cięciwa w materiale | 2.5 | 2.5 | 0.0 | ✓ | wall_t |
| `ramka_korpus_P_v2` | dno grubość (20, −20, 1,5) | cięciwa w materiale | 3.0 | 3.0 | 0.0 | ✓ | floor_t |
| `ramka_korpus_P_v2` | wierzch ściany Z (98,75, 20) | trafienie −Z | 59.6 | 59.6 | 0.0 | ✓ | korpus_h |
| `ramka_korpus_P_v2` | naroże pionowe R5: x lica przy y=−99 | trafienie −X | 97.999 | 98.0 | -0.001 | ✓ | box_corner_r 5 → 98,0 |
| `ramka_korpus_P_v2` | dolna krawędź R3: z lica przy x=99,5 | trafienie +Z | 1.343 | 1.3416876048223 | 0.001 | ✓ | box_edge_r 3 → 1,34 |
| `ramka_korpus_P_v2` | stadion panelu (60,60): wierzch Z | trafienie −Z | 4.0 | 4.0 | 0.0 | ✓ | floor_t+panel_pad_h (sonda 4,24 od osi rowka) |
| `ramka_korpus_P_v2` | stadion szerokość prostopadle do przekątnej: lico z zewnątrz (z (66,54,3,5) w −N) | trafienie −N | 3.985 | 3.9852813742385713 | -0.0 | ✓ | odl. 8,49 od osi − 4,5 = 3,99 |
| `ramka_korpus_P_v2` | rowek panelu szer. (60,60, Z 1,5) prostopadle do przekątnej | cięciwa N | 3.4 | 3.4 | 0.0 | ✓ | panel_slot_w |
| `ramka_korpus_P_v2` | rowek panelu długość wzdłuż przekątnej (60,60, Z 1,5) | cięciwa D | 17.542 | 17.54213562373095 | -0.0 | ✓ | (55→65)·√2 + 3,4 = 17,54 |
| `ramka_korpus_P_v2` | rowek panelu przelotowy przez dno i stadion: trafienie +Z z (60,60,−5) | trafienie +Z | None | None |  | — (przelot ✓) | brak = przelot (wkręt M3 przechodzi przez dno i stadion do dystansu) |
| `ramka_korpus_P_v2` | rowek: półdługość od (60,60,3,5) w +D (koniec rowka R1,7) | trafienie +D | 8.771 | 8.771067811865475 | -0.0 | ✓ | 5·√2 + 1,7 = 8,77 |
| `ramka_korpus_P_v2` | stadion: koniec od zewnątrz (z (80,80,3,5) w −D) | trafienie −D | 16.715 | 16.713203435596427 | 0.002 | ✓ | koniec stadionu 65 + R4,5 → 16,71 |
| `ramka_korpus_P_v2` | boss Pi (−46,5,−24,5): wierzch Z | trafienie −Z | 8.0 | 8.0 | 0.0 | ✓ | floor_t+pi_standoff_h |
| `ramka_korpus_P_v2` | boss Pi: otwór ø (Z 7) | cięciwa X | 2.1 | 2.1 | 0.0 | ✓ | insert_hole_m25 |
| `ramka_korpus_P_v2` | boss Pi: dno otworu Z | trafienie −Z | 3.0 | 3.0 | 0.0 | ✓ | 8 − insert_depth_m25 5 |
| `ramka_korpus_P_v2` | boss Pi: lico zewn. x (z (−30,−24,5,6) w −X) | trafienie −X | -42.5 | -42.5 | 0.0 | ✓ | ø8 → −46,5+4 |
| `ramka_korpus_P_v2` | boss Pi (11,5, 24,5): wierzch Z | trafienie −Z | 8.0 | 8.0 | 0.0 | ✓ |  |
| `ramka_korpus_P_v2` | wlot w dnie (−8,−10): X | cięciwa | 30.0 | 30 | 0.0 | ✓ | floor_vent_l |
| `ramka_korpus_P_v2` | wlot w dnie (−8,−10): Y | cięciwa | 4.0 | 4 | 0.0 | ✓ | floor_vent_w |
| `ramka_korpus_P_v2` | szczelina tylna (−54, Z 8): X | cięciwa | 12.0 | 12 | 0.0 | ✓ | vent_slot_w |
| `ramka_korpus_P_v2` | szczelina tylna (−54, Z 8): Z | cięciwa | 3.0 | 3 | 0.0 | ✓ | vent_slot_h |
| `ramka_korpus_P_v2` | szczelina boczna prawa (y 36, Z 8): Y | cięciwa | 12.0 | 12 | 0.0 | ✓ |  |
| `ramka_korpus_P_v2` | szczelina boczna lewa (y −36, Z 8): Z | cięciwa | 3.0 | 3 | 0.0 | ✓ |  |
| `ramka_korpus_P_v2` | okno DC (−67,5, Z 26): X | cięciwa | 51.0 | 51 | 0.0 | ✓ | dc_pocket_w |
| `ramka_korpus_P_v2` | okno DC: Z | cięciwa | 24.0 | 24 | 0.0 | ✓ | dc_pocket_h |
| `ramka_korpus_P_v2` | okno DC: dolna krawędź Z | trafienie −Z | 14.0 | 14 | 0.0 | ✓ | dc_pocket_z0 |
| `ramka_korpus_P_v2` | skrzynka DC wnętrze X (y 87,75, Z 16) | cięciwa | 53.5 | 53.5 | 0.0 | ✓ | −95,5…−42 |
| `ramka_korpus_P_v2` | skrzynka DC: ściana przednia w świetle y | trafienie −Y z zewnątrz | 80.0 | 80 | 0.0 | ✓ | 100 − dc_pocket_depth 22 + wall 2 |
| `ramka_korpus_P_v2` | skrzynka DC: sufit Z (z wnętrza) | trafienie +Z | 38.0 | 38 | 0.0 | ✓ | 40 − 2 |
| `ramka_korpus_P_v2` | skrzynka DC: dno Z (z wnętrza) | trafienie −Z | 14.0 | 14 | 0.0 | ✓ | 12 + 2 |
| `ramka_korpus_P_v2` | otwór DC ø (Y) w prawej ścianie skrzynki (x −41) | cięciwa | 11.999 | 12 | -0.001 | ✓ | dc_hole_d |
| `ramka_korpus_P_v2` | otwór DC ø (Z) | cięciwa | 11.998 | 12 | -0.002 | ✓ | dc_hole_d |
| `ramka_korpus_P_v2` | prawa ściana skrzynki grubość (−41, 81, 30) | cięciwa w materiale X | 2.0 | 2.0 | 0.0 | ✓ | dc_pocket_wall |
| `ramka_korpus_P_v2` | ścianka otwór DC – wierzch prawej ściany skrzynki (−41, 89, 37) | cięciwa w materiale Z | 4.001 | 4.0 | 0.001 | ✓ | otwór do Z 36, wierzch skrzynki Z 40 → 4,0 |
| `ramka_korpus_P_v2` | skrzynka: lewa ściana (= ściana korpusu) grubość (−96,5, 88, 26) | cięciwa w materiale X | 4.5 | 4.5 | 0.0 | ✓ | 2,5 + 2 |
| `ramka_korpus_P_v2` | okno USB (60, Z 24): X | cięciwa | 16.0 | 16 | 0.0 | ✓ | usb_cut_w |
| `ramka_korpus_P_v2` | okno USB: Z | cięciwa | 9.0 | 9 | 0.0 | ✓ | usb_cut_h |
| `ramka_korpus_P_v2` | rowek flanszy USB prawy (72,75): X | cięciwa | 5.691 | 5.7 | -0.009 | ✓ | (14−11,5)+3,2 |
| `ramka_korpus_P_v2` | rowek flanszy USB prawy: Z | cięciwa | 3.2 | 3.2 | 0.0 | ✓ | usb_slot_w |
| `ramka_korpus_P_v2` | ścianka okno USB – rowek (68,95) | cięciwa w materiale X | 1.904 | 1.9 | 0.004 | ✓ | 52−50,1 |
| `ramka_korpus_P_v2` | kieszeń zatrzasku prawa (98, 0): szerokość | cięciwa | 10.0 | 10 | 0.0 | ✓ | snap_pocket_w |
| `ramka_korpus_P_v2` | kieszeń zatrzasku prawa (98, 0): wysokość Z | cięciwa | 2.5 | 2.5 | 0.0 | ✓ | snap_pocket_h |
| `ramka_korpus_P_v2` | kieszeń zatrzasku prawa (98, 0): dolna krawędź Z | trafienie −Z | 52.6 | 52.6 | 0.0 | ✓ | snap_pocket_z |
| `ramka_korpus_P_v2` | kieszeń zatrzasku prawa (98, 0): górna krawędź Z | trafienie +Z | 55.1 | 55.1 | 0.0 | ✓ | 52,6+2,5 |
| `ramka_korpus_P_v2` | kieszeń zatrzasku lewa (−98, 0): szerokość | cięciwa | 10.0 | 10 | 0.0 | ✓ | snap_pocket_w |
| `ramka_korpus_P_v2` | kieszeń zatrzasku lewa (−98, 0): wysokość Z | cięciwa | 2.5 | 2.5 | 0.0 | ✓ | snap_pocket_h |
| `ramka_korpus_P_v2` | kieszeń zatrzasku lewa (−98, 0): dolna krawędź Z | trafienie −Z | 52.6 | 52.6 | 0.0 | ✓ | snap_pocket_z |
| `ramka_korpus_P_v2` | kieszeń zatrzasku lewa (−98, 0): górna krawędź Z | trafienie +Z | 55.1 | 55.1 | 0.0 | ✓ | 52,6+2,5 |
| `ramka_korpus_P_v2` | kieszeń zatrzasku przednia (50, −98): szerokość | cięciwa | 10.0 | 10 | 0.0 | ✓ | snap_pocket_w |
| `ramka_korpus_P_v2` | kieszeń zatrzasku przednia (50, −98): wysokość Z | cięciwa | 2.5 | 2.5 | 0.0 | ✓ | snap_pocket_h |
| `ramka_korpus_P_v2` | kieszeń zatrzasku przednia (50, −98): dolna krawędź Z | trafienie −Z | 52.6 | 52.6 | 0.0 | ✓ | snap_pocket_z |
| `ramka_korpus_P_v2` | kieszeń zatrzasku przednia (50, −98): górna krawędź Z | trafienie +Z | 55.1 | 55.1 | 0.0 | ✓ | 52,6+2,5 |
| `ramka_korpus_P_v2` | kieszeń zatrzasku tylna (−50, 98): szerokość | cięciwa | 10.0 | 10 | 0.0 | ✓ | snap_pocket_w |
| `ramka_korpus_P_v2` | kieszeń zatrzasku tylna (−50, 98): wysokość Z | cięciwa | 2.5 | 2.5 | 0.0 | ✓ | snap_pocket_h |
| `ramka_korpus_P_v2` | kieszeń zatrzasku tylna (−50, 98): dolna krawędź Z | trafienie −Z | 52.6 | 52.6 | 0.0 | ✓ | snap_pocket_z |
| `ramka_korpus_P_v2` | kieszeń zatrzasku tylna (−50, 98): górna krawędź Z | trafienie +Z | 55.1 | 55.1 | 0.0 | ✓ | 52,6+2,5 |
| `ramka_korpus_P_v2` | kieszeń prawa: dno x (z (80,0,53,8) +X) | trafienie +X | 98.5 | 98.5 | 0.0 | ✓ | 97,5 + snap_pocket_depth 1,0 |
| `ramka_korpus_P_v2` | kieszeń przednia: dno y | trafienie −Y | -98.5 | -98.5 | 0.0 | ✓ |  |
| `ramka_korpus_P_v2` | ściana za kieszenią prawą (99,25, 0, 53,85) | cięciwa w materiale X | 1.5 | 1.5 | 0.0 | ✓ | 2,5 − 1,0 |
| `ramka_korpus_P_v2` | otwór wkrętu blatu (75, Z 55): ø w ścianie (y 98,2) | cięciwa X | 3.195 | 3.2 | -0.005 | ✓ | blat_screw_hole_d |
| `ramka_korpus_P_v2` | otwór wkrętu blatu: ø przy licu zewn. (y 99,9) | cięciwa X | 6.1 | 6.1 | 0.0 | ✓ | pogłębienie ø6,3/90° → 6,1 na y 99,9 |
| `ramka_korpus_P_v2` | otwór wkrętu blatu (−75, Z 55): ø w ścianie | cięciwa X | 3.195 | 3.2 | -0.005 | ✓ |  |
| `ramka_korpus_P_v2` | otwór wkrętu blatu: ø pionowo (Z) przy y 98,2 | cięciwa Z | 3.193 | 3.2 | -0.007 | ✓ |  |
| `ramka_korpus_P_v2` | napis: lico reliefu min y (bbox) | bbox | -100.6 | -100.6 | 0.0 | ✓ | label_relief_h 0,6 |
| `ramka_korpus_P_v2` | napis: najdalszy punkt reliefu y (skan x −55…55 co 0,5, Z 51) | trafienie +Y | -100.6 | -100.6 | 0.0 | ✓ |  |
| `ramka_korpus_P_v2` | napis: zakres Z reliefu (skan) | skan | 8.0 | 8.0 | 0.0 | ✓ | label_text_h 8 (Z 47.0…55.0) |
| `korpus W vs P` | wierzchołki poza przednią ścianą (y > −99,9): różnica zbiorów | zbiory | 0.0 | 0 | 0.0 | ✓ | R33: różnica tylko napisem |
| `ramka_blat_v2` | gabaryt X / Y | bbox | 200.0 | 200 | 0.0 | ✓ | box_outer |
| `ramka_blat_v2` | gabaryt Z | bbox | 14.0 | 14 | 0.0 | ✓ | blat_t+blat_skirt_h |
| `ramka_blat_v2` | objętość [cm³] | mesh | 72.569 | None |  | — | arkusz 72,57 |
| `ramka_blat_v2` | wierzch blatu: Z lica (99, 0) | trafienie +Z z −10 | 0.0 | 0.0 | 0.0 | ✓ | STL wierzchem w dół (sonda 3 od krawędzi R1,5) |
| `ramka_blat_v2` | płyta grubość (99, 0, 2) | cięciwa w materiale Z | 4.0 | 4.0 | 0.0 | ✓ | blat_t |
| `ramka_blat_v2` | płyta grubość (90, 90, 2) — bez bossa ramy | cięciwa w materiale Z | 4.0 | 4.0 | 0.0 | ✓ | R50‑U1 |
| `ramka_blat_v2` | kieszeń dyfuzora X (y 20, Z 1) | cięciwa | 162.0 | 162 | 0.0 | ✓ | diffuser_pocket |
| `ramka_blat_v2` | kieszeń dyfuzora głębokość: półka Z (z (80, 0, −10) +Z) | trafienie +Z | 2.0 | 2.0 | 0.0 | ✓ | diffuser_t |
| `ramka_blat_v2` | kieszeń dyfuzora: naroże ostre — x lica przy y 80,8 | trafienie +X | 81.0 | 81.0 | 0.0 | ✓ | diffuser_pocket_r 0 |
| `ramka_blat_v2` | okno przelotowe X (y 20, Z 3) | cięciwa | 158.0 | 158 | 0.0 | ✓ | window_through |
| `ramka_blat_v2` | kołnierz zewn. x (z (150,20,9) −X) | trafienie −X | 97.0 | 97.0 | 0.0 | ✓ | 194/2 |
| `ramka_blat_v2` | kołnierz zewn. y (z (20,150,9) −Y) | trafienie −Y | 97.0 | 97.0 | 0.0 | ✓ |  |
| `ramka_blat_v2` | kołnierz wewn. X (cięciwa 0,20,9) | cięciwa | 190.0 | 190 | 0.0 | ✓ | 2·95 |
| `ramka_blat_v2` | kołnierz grubość (96, 20, 9) | cięciwa w materiale X | 2.0 | 2.0 | 0.0 | ✓ | blat_skirt_t |
| `ramka_blat_v2` | kołnierz: dolna krawędź Z (96,20) | trafienie −Z z 30 | 14.0 | 14.0 | 0.0 | ✓ |  |
| `ramka_blat_v2` | kołnierz naroże R4,5: x lica przy y 96 | trafienie −X | 95.326 | 95.32842712474618 | -0.002 | ✓ | → 95,33 |
| `ramka_blat_v2` | górna krawędź R1,5: z lica przy x 99,5 | trafienie +Z | 0.388 | 0.3819660112501051 | 0.006 | ✓ | blat_top_edge_r → 0,38 |
| `ramka_blat_v2` | haczyk prawy (y 0): czubek | trafienie X | 98.3 | 98.3 | 0.0 | ✓ | 97,0 + snap_hook_h 1,3 |
| `ramka_blat_v2` | haczyk lewy: czubek | trafienie X | 98.3 | 98.3 | 0.0 | ✓ | 97,0 + snap_hook_h 1,3 |
| `ramka_blat_v2` | haczyk przedni (x 50; STL +Y): czubek | trafienie Y | 98.3 | 98.3 | 0.0 | ✓ | 97,0 + snap_hook_h 1,3 |
| `ramka_blat_v2` | haczyk tylny (x −50; STL −Y): czubek | trafienie Y | 98.3 | 98.3 | 0.0 | ✓ | 97,0 + snap_hook_h 1,3 |
| `ramka_blat_v2` | haczyk prawy: szerokość (y) na czubku | cięciwa w materiale Y (98, 0, 9.75) | 8.0 | 8.0 | 0.0 | ✓ | snap_hook_w |
| `ramka_blat_v2` | nacięcie obok haczyka (96, 4,5, 10): szer. Y | cięciwa | 1.0 | 1.0 | 0.0 | ✓ | snap_notch_w |
| `ramka_blat_v2` | nacięcie: górny koniec Z (z (96,4,5,13) −Z... = pierwsze trafienie w górę) | trafienie −Z (w kierunku wierzchu) | 5.0 | 5.0 | 0.0 | ✓ | snap_hook_arm_l 9 → lokalnie −5 |
| `ramka_blat_v2` | ramię haczyka grubość (96,8, 0, 13) | cięciwa w materiale X | 1.5 | 1.5 | 0.0 | ✓ | snap_hook_t |
| `ramka_blat_v2` | słupek (75, y 89,2…95,2): otwór ø (Z 8,6) | cięciwa X (75, 94, 8.6) | 2.5 | 2.5 | 0.0 | ✓ | insert_hole_m3 (STL y −94) |
| `ramka_blat_v2` | słupek: otwór ø pionowo | cięciwa Z | 2.5 | 2.5 | 0.0 | ✓ |  |
| `ramka_blat_v2` | słupek: dno otworu y | trafienie −Y | -91.0 | -91.0 | 0.0 | ✓ | 97 − blat_post_hole_depth 6 (STL −91) |
| `ramka_blat_v2` | słupek: wylot otworu y (+Y) | trafienie +Y | None | None |  | — (przelot ✓) | otwarty na zewnątrz (brak trafienia = przelot) |
| `ramka_blat_v2` | słupek: szerokość X (y 92, Z 10) | cięciwa w materiale X | 8.0 | 8.0 | 0.0 | ✓ | blat_post_w |
| `ramka_blat_v2` | słupek: przednie lico y (z (75,80,10) +Y) | trafienie +Y | -89.2 | -89.2 | 0.0 | ✓ | blat_post_y0 (STL −89,2) |
| `ramka_blat_v2` | słupek: dno pod otworem (75, 90,1, 8,6) | cięciwa w materiale Y | 1.8 | 1.8 | 0.0 | ✓ | 91,0 − 89,2 |
| `ramka_blat_v2` | słupek −75: otwór ø | cięciwa X | 2.5 | 2.5 | 0.0 | ✓ |  |
| `ramka_blat_v2` | otwór kołka (58, 93,5): ø | cięciwa X (Z 2) | 3.3 | 3.3 | 0.0 | ✓ | blat_pin_hole_d (STL y −93,5) |
| `ramka_blat_v2` | otwór kołka: dno Z | trafienie +Z z (58,93,5,1) | 3.8 | 3.8 | 0.0 | ✓ | blat_pin_hole_depth |
| `ramka_blat_v2` | otwór kołka −58: ø | cięciwa X | 3.3 | 3.3 | 0.0 | ✓ |  |
| `ramka_blat_v2` | kieszeń magnesu (58, 86): ø | cięciwa X (Z 1) | 5.4 | 5.4 | 0.0 | ✓ | blat_magnet_pocket_d |
| `ramka_blat_v2` | kieszeń magnesu: dno Z | trafienie +Z | 2.3 | 2.3 | 0.0 | ✓ | blat_magnet_pocket_depth |
| `ramka_blat_v2` | szczelina kabla (66, 90): X | cięciwa | 4.0 | 4 | 0.0 | ✓ | wire_slot_w |
| `ramka_blat_v2` | szczelina kabla: Y | cięciwa | 8.0 | 8 | 0.0 | ✓ | wire_slot_l |
| `ramka_blat_v2` | szczelina kabla: przelot (trafienie z (66,90,−5) +Z) | trafienie +Z | None | None |  | — (przelot ✓) | brak trafienia = przelot przez płytę |
| `ramka_wkladka_v2` | gabaryt X / Y / Z | bbox | 130.0 | 130 | 0.0 | ✓ | 2·65 |
| `ramka_wkladka_v2` | gabaryt Y | bbox | 148.3 | 148.3 | 0.0 | ✓ | −52,3…96 |
| `ramka_wkladka_v2` | gabaryt Z | bbox | 11.0 | 11.0 | 0.0 | ✓ | 3,5 + 6 + 1,5 kołek |
| `ramka_wkladka_v2` | objętość [cm³] | mesh | 12.406 | None |  | — | arkusz 12,41 |
| `ramka_wkladka_v2` | rama zewn. X (y 0, Z 6,5) | zewn. (trafienia z ±150) | 104.6 | 104.6 | 0.0 | ✓ | 96,6 + 2·4 |
| `ramka_wkladka_v2` | otwór X (0,0,6,5) | cięciwa | 96.6 | 96.6 | 0.0 | ✓ | insert_opening |
| `ramka_wkladka_v2` | otwór Y (20,0,6,5) | cięciwa | 96.6 | 96.6 | 0.0 | ✓ |  |
| `ramka_wkladka_v2` | otwór: naroże ostre, x lica przy y 48,1 | trafienie +X | 48.3 | 48.3 | 0.0 | ✓ | insert_opening_r 0 |
| `ramka_wkladka_v2` | spód ramy Z (−40, −50,3) | trafienie +Z z −10 | 3.5 | 3.5 | 0.0 | ✓ | kołki 3,5 w dół |
| `ramka_wkladka_v2` | wierzch ramy Z | trafienie −Z z 20 | 9.5 | 9.5 | 0.0 | ✓ | 3,5 + insert_h 6 |
| `ramka_wkladka_v2` | rama szerokość (y −50,3): Y | cięciwa w materiale | 4.0 | 4.0 | 0.0 | ✓ | insert_wall_w |
| `ramka_wkladka_v2` | faza otworu 1×45°: z lica przy x 48,8 | trafienie −Z z 20 | 9.0 | 9.0 | 0.0 | ✓ | insert_chamfer 1 → 9,5 − 0,5 |
| `ramka_wkladka_v2` | półka A (−38,−38): wierzch Z | trafienie −Z | 6.0 | 6.0 | 0.0 | ✓ | 3,5 + insert_shelf_h 2,5 |
| `ramka_wkladka_v2` | półka A grubość | cięciwa w materiale Z (−38,−38,4,5) | 2.5 | 2.5 | 0.0 | ✓ | insert_shelf_h |
| `ramka_wkladka_v2` | półka A: bok (x lica od środka) | trafienie −X z (0,−38,5) | -36.3 | -36.3 | 0.0 | ✓ | 48,3 − 12 |
| `ramka_wkladka_v2` | kieszeń Halla A (−42,−42): X | cięciwa | 5.0 | 5.0 | 0.0 | ✓ | hall_pocket_w |
| `ramka_wkladka_v2` | kieszeń Halla A: Y | cięciwa | 5.5 | 5.5 | 0.0 | ✓ | hall_pocket_l |
| `ramka_wkladka_v2` | kieszeń Halla A: przelot (z (−42,−42,−5) +Z) | trafienie +Z | None | None |  | — (przelot ✓) | brak = przelot |
| `ramka_wkladka_v2` | kanał pod półką A (−45,−45, Z 3,5…4,5)? szer. prostopadle do przekątnej | cięciwa N (−45,−45,4) | 2.5 | 2.5 | 0.0 | ✓ | hall_lead_channel_w |
| `ramka_wkladka_v2` | kanał pod półką A: sufit Z (z (−45,−45,0) +Z) | trafienie +Z | 4.5 | 4.5 | 0.0 | ✓ | 3,5 + 1,0 |
| `ramka_wkladka_v2` | przelot w ściance A (−50,−50): sufit Z | trafienie +Z | 5.0 | 5.0 | 0.0 | ✓ | 3,5 + hall_wall_pass_h 1,5 |
| `ramka_wkladka_v2` | półka nad kanałem A (−45,−45, Z 5,25) | cięciwa w materiale Z | 1.5 | 1.5 | 0.0 | ✓ | 2,5 − 1,0 |
| `ramka_wkladka_v2` | kołek orientacyjny (45,6,−45,6): X | cięciwa w materiale X (Z 8) | 4.4 | 4.4 | 0.0 | ✓ | orient_post |
| `ramka_wkladka_v2` | kołek orientacyjny: Y | cięciwa w materiale Y | 4.4 | 4.4 | 0.0 | ✓ |  |
| `ramka_wkladka_v2` | kołek orientacyjny: szczyt Z | trafienie −Z z 20 | 11.0 | 11.0 | 0.0 | ✓ | 6 + orient_post_h 5 |
| `ramka_wkladka_v2` | kołek orientacyjny: lico zewn. x (z (0,−45,6,8) +X) | trafienie +X | 43.4 | 43.4 | 0.0 | ✓ | ściana 48,3 − gap 0,5 − 4,4 = 43,4 |
| `ramka_wkladka_v2` | kołek orientacyjny: faza — szczyt przy x 43,6 | trafienie −Z | 10.2 | 10.2 | 0.0 | ✓ | orient_post_chamfer 1 → 10,2 |
| `ramka_wkladka_v2` | wycięcie palcowe (0,−50,3, 6,5): X | cięciwa | 30.0 | 30 | 0.0 | ✓ | finger_cut_w |
| `ramka_wkladka_v2` | rowek kablowy prawy: dno x (z (57,3,0,4,25) −X) | trafienie −X | 49.8 | 49.8 | 0.0 | ✓ | 52,3 − wire_rabbet_w 2,5 |
| `ramka_wkladka_v2` | rowek kablowy prawy: sufit Z (z (51,05,0,0) +Z) | trafienie +Z | 5.0 | 5.0 | 0.0 | ✓ | 3,5 + wire_rabbet 1,5 |
| `ramka_wkladka_v2` | rowek kablowy tylny: dno y (z (0,57,3,4,25) −Y) | trafienie −Y | 49.8 | 49.8 | 0.0 | ✓ |  |
| `ramka_wkladka_v2` | rowek kablowy lewy: dno x | trafienie +X z (−57,3,0,4,25) | -49.8 | -49.8 | 0.0 | ✓ |  |
| `ramka_wkladka_v2` | rowek kablowy przedni (nie ma): sufit Z (0? z (−30,−51,05,0) +Z) | trafienie +Z | 3.5 | 3.5 | 0.0 | ✓ | przód bez rowka → spód ramy 3,5 |
| `ramka_wkladka_v2` | ścianka rowek–otwór (49,05, 0, 4,25) | cięciwa w materiale X | 1.5 | 1.5 | 0.0 | ✓ | 49,8 − 48,3 |
| `ramka_wkladka_v2` | ucho prawe (58, 80): wierzch Z | trafienie −Z z 20 | 6.5 | 6.5 | 0.0 | ✓ | 3,5 + tab_t 3 |
| `ramka_wkladka_v2` | ucho prawe: szerokość X (y 80, Z 5) | cięciwa w materiale X | 14.0 | 14 | 0.0 | ✓ | tab_w |
| `ramka_wkladka_v2` | ucho prawe: koniec y (z (58,150,5) −Y) | trafienie −Y | 96.0 | 96 | 0.0 | ✓ | tab_end_y |
| `ramka_wkladka_v2` | kołek ustalający (58, 93,5): ø (Z 1,5) | cięciwa X | 3.0 | 3.0 | 0.0 | ✓ | tab_pin_d |
| `ramka_wkladka_v2` | kołek ustalający: ø przy końcu (Z 0,25) | cięciwa X | 2.5 | 2.5 | 0.0 | ✓ | stożek ø3→ø2 na 0,5: na Z 0,25 ≈ 2,5 |
| `ramka_wkladka_v2` | kołek ustalający: koniec Z | trafienie +Z z −5 | 0.0 | 0.0 | 0.0 | ✓ | tab_pin_h 3,5 pod spodem |
| `ramka_wkladka_v2` | kołek ustalający −58: ø | cięciwa X | 3.0 | 3.0 | 0.0 | ✓ |  |
| `ramka_wkladka_v2` | otwór magnesu ucha (58, 86): ø | cięciwa X (Z 5) | 5.4 | 5.4 | 0.0 | ✓ | tab_magnet_hole_d |
| `ramka_wkladka_v2` | otwór magnesu: przelot | trafienie +Z z (58,86,−5) | None | None |  | — (przelot ✓) | brak = przelot |
| `ramka_wkladka_v2` | kanał pod uchem (64, 70): ścianka wewn. x (z (64,70,4) −X) | trafienie −X | 63.0 | 63.0 | 0.0 | ✓ | kanał 63…65 = otwarty na zewnętrznej krawędzi ucha |
| `ramka_wkladka_v2` | kanał pod uchem: otwarty w +X (z (64,70,4) +X) | trafienie +X | None | None |  | — | brak = kanał otwarty bokiem (rabbet) |
| `ramka_wkladka_v2` | kanał pod uchem: sufit Z (z (64,70,0) +Z) | trafienie +Z | 4.7 | 4.7 | 0.0 | ✓ | tab_cable_channel_h 1,2 → 4,7 |
| `ramka_wkladka_v2` | nasada L: koniec y części wewn. (x 48, z (48,70,5) −Y) | trafienie −Y | 58.0 | 58.0 | 0.0 | ✓ | tab_root_y1 |
| `ramka_wkladka_v2` | nasada L: brak materiału poza ramą dla x 60, y 50 (z (60,50,5) +Z) | trafienie +Z z (60,50,−5) | None | None |  | — | brak = prawy pas odsłonięty (K‑56) |
| `ramka_wkladka_v2` | nasada L: lico y części zewn. (x 60, z (60,0,5) +Y) | trafienie +Y | 52.3 | 52.3 | 0.0 | ✓ | x 52,3…65 od y 52,3 |
| `ramka_wkladka_v2` | strzałka ▼ (32, −51,15): szczyt Z | trafienie −Z z 20 | 10.1 | 10.1 | 0.0 | ✓ | relief 0,6 na wierzchu ramy → 10,1 |
| `ramka_wkladka_v2` | strzałka ▼ (−32, −51,15): szczyt Z | trafienie −Z z 20 | 10.1 | 10.1 | 0.0 | ✓ |  |
| `ramka_pokrywka_v2` | gabaryt X | bbox | 99.6 | 99.6 | 0.0 | ✓ | 96,6 + 2·1,5 |
| `ramka_pokrywka_v2` | gabaryt Z | bbox | 20.0 | 20.0 | 0.0 | ✓ | 14 + 2 + 4 |
| `ramka_pokrywka_v2` | objętość [cm³] | mesh | 30.064 | None |  | — | arkusz 30,06 |
| `ramka_pokrywka_v2` | wierzch: Z lica z zewnątrz (15,0) | trafienie +Z z −10 | 0.0 | 0.0 | 0.0 | ✓ | wierzchem w dół |
| `ramka_pokrywka_v2` | wierzch grubość (15,0,1) | cięciwa w materiale Z | 2.0 | 2.0 | 0.0 | ✓ | cover_top_t |
| `ramka_pokrywka_v2` | wnęka X (0,20,10) | cięciwa | 96.6 | 96.6 | 0.0 | ✓ | plate_size + 2·cover_clearance |
| `ramka_pokrywka_v2` | wnęka Y (20,0,10) | cięciwa | 96.6 | 96.6 | 0.0 | ✓ |  |
| `ramka_pokrywka_v2` | wnęka: naroże — x lica przy y 48,1 | trafienie +X | 47.546 | 47.548331477354786 | -0.002 | ✓ | naroże wnęki R1,5 (= R3 − 1,5) → 47,55 |
| `ramka_pokrywka_v2` | kołnierz grubość (49,05, 20, 10) | cięciwa w materiale X | 1.5 | 1.5 | 0.0 | ✓ | cover_skirt_t |
| `ramka_pokrywka_v2` | kołnierz grubość za garbem (49,05, 0, 18) | cięciwa w materiale X | 2.2 | 2.2 | 0.0 | ✓ | 1,5 + garb 0,7 |
| `ramka_pokrywka_v2` | garb prawy (y 0): czubek x (z (0,0,18) +X) | trafienie +X | 47.6 | 47.6 | 0.0 | ✓ | 48,3 − cover_snap_bump 0,7 |
| `ramka_pokrywka_v2` | garb przedni (x 25): czubek y | trafienie −Y z (25,0,18) | 47.6 | 47.6 | 0.0 | ✓ | cover_snap_front_x 25 (przód = STL +Y po obrocie) |
| `ramka_pokrywka_v2` | garb tylny (x −25): czubek y | trafienie +Y z (−25,0,18) | -47.6 | -47.6 | 0.0 | ✓ |  |
| `ramka_pokrywka_v2` | garb lewy (y 0): czubek x | trafienie −X z (0,0,18) | -47.6 | -47.6 | 0.0 | ✓ |  |
| `ramka_pokrywka_v2` | garb prawy: szerokość Y (cięciwa w materiale przy x 47,8, Z 18) | cięciwa w materiale Y | 10.0 | 10.0 | 0.0 | ✓ | cover_snap_w |
| `ramka_pokrywka_v2` | wycięcie palcowe przód (y −49,05, Z 19): X | cięciwa | 30.0 | 30 | 0.0 | ✓ | cover_finger_w |
| `ramka_pokrywka_v2` | wycięcie palcowe przód: górna krawędź Z (z (0,−49,05,10) +Z) | trafienie +Z | 17.0 | 17.0 | 0.0 | ✓ | 20 − cover_finger_h 3 |
| `ramka_pokrywka_v2` | wycięcie palcowe tył (y 49,05, Z 19): X | cięciwa | 30.0 | 30 | 0.0 | ✓ |  |
| `ramka_pokrywka_v2` | naroże R3: x lica przy y −49,0 | trafienie −X z (150,−49,10) | 48.839 | 48.83960780543711 | -0.001 | ✓ | cover_corner_r 3 → 48,84 |
| `ramka_pokrywka_v2` | dolna krawędź kołnierza Z (49,05, 20) | trafienie −Z z 30 | 20.0 | 20.0 | 0.0 | ✓ |  |
| `ramka_tulejka_dc_v2` | kołnierz ø (bbox X) | bbox | 14.999 | 15 | -0.001 | ✓ | dc_bush_flange_d (tesselacja) |
| `ramka_tulejka_dc_v2` | walec: promień zewn. (z (10,0,2) −X) | trafienie −X | 5.925 | 5.925 | 0.0 | ✓ | dc_bush_outer_d 11,85 / 2 |
| `ramka_tulejka_dc_v2` | walec: promień zewn. w −X | trafienie +X z (−10,0,2) | -5.924 | -5.925 | 0.001 | ✓ |  |
| `ramka_tulejka_dc_v2` | walec: promień zewn. (Y) | trafienie −Y z (0,10,2) | 5.924 | 5.925 | -0.001 | ✓ |  |
| `ramka_tulejka_dc_v2` | otwór ø (0,0,1) | cięciwa X | 8.2 | 8.2 | 0.0 | ✓ | dc_bush_inner_d |
| `ramka_tulejka_dc_v2` | otwór ø (0,0,2,5) | cięciwa Y | 8.2 | 8.2 | 0.0 | ✓ |  |
| `ramka_tulejka_dc_v2` | wysokość całkowita | bbox Z | 3.0 | 3.0 | 0.0 | ✓ | dc_bush_t 2 + flange_t 1 |
| `ramka_tulejka_dc_v2` | kołnierz grubość (6,7, 0, 0,5) | cięciwa w materiale Z | 1.0 | 1.0 | 0.0 | ✓ | dc_bush_flange_t |
| `ramka_tulejka_dc_v2` | ścianka walca (5, 0, 2) | cięciwa w materiale X | 1.825 | 1.8250000000000002 | -0.0 | ✓ | 1,825 |
| `ramka_podkladka_panelu_05_v2` | ø zewn. (bbox X) | bbox | 9.0 | 9 | 0.0 | ✓ | panel_shim_d |
| `ramka_podkladka_panelu_05_v2` | otwór ø | cięciwa X (0,0,t/2) | 3.395 | 3.4 | -0.005 | ✓ | panel_shim_hole_d |
| `ramka_podkladka_panelu_05_v2` | grubość | bbox Z | 0.5 | 0.5 | 0.0 | ✓ | panel_shim_t |
| `ramka_podkladka_panelu_1_v2` | ø zewn. (bbox X) | bbox | 9.0 | 9 | 0.0 | ✓ | panel_shim_d |
| `ramka_podkladka_panelu_1_v2` | otwór ø | cięciwa X (0,0,t/2) | 3.395 | 3.4 | -0.005 | ✓ | panel_shim_hole_d |
| `ramka_podkladka_panelu_1_v2` | grubość | bbox Z | 1.0 | 1.0 | 0.0 | ✓ | panel_shim_t |
| `ramka_podkladka_panelu_2_v2` | ø zewn. (bbox X) | bbox | 9.0 | 9 | 0.0 | ✓ | panel_shim_d |
| `ramka_podkladka_panelu_2_v2` | otwór ø | cięciwa X (0,0,t/2) | 3.395 | 3.4 | -0.005 | ✓ | panel_shim_hole_d |
| `ramka_podkladka_panelu_2_v2` | grubość | bbox Z | 2.0 | 2.0 | 0.0 | ✓ | panel_shim_t |
| `ramka_plytka_wieczorna_n1_v2` | bok X / Y | bbox | 96.0 | 96 | 0.0 | ✓ | plate_size |
| `ramka_plytka_wieczorna_n1_v2` | grubość z reliefem cyfry | bbox Z | 8.6 | 8.6 | 0.0 | ✓ | 8 + number_relief_h 0,6 |
| `ramka_plytka_wieczorna_n1_v2` | grubość płytki (0, −46,5, 4) | cięciwa w materiale Z | 8.0 | 8.0 | 0.0 | ✓ | plate_thickness |
| `ramka_plytka_wieczorna_n1_v2` | wycięcie D: otwarte na zewnątrz (z (45,5,−45,5,4) +X) | trafienie +X | None | None |  | — | brak = wycięcie narożne otwarte |
| `ramka_plytka_wieczorna_n1_v2` | wycięcie D: lico y od środka (z (45,5,0,4) −Y) | trafienie −Y | -43.0 | -43.0 | 0.0 | ✓ | notch y −48…−43 |
| `ramka_plytka_wieczorna_n1_v2` | wycięcie D: lico x od środka (z (0,−45,5,4) +X) | trafienie +X | 43.0 | 43.0 | 0.0 | ✓ |  |
| `ramka_plytka_wieczorna_n1_v2` | rowek pokrywki: dno x (z (60,20,6) −X) | trafienie −X | 47.2 | 47.2 | 0.0 | ✓ | 48 − cover_groove_depth 0,8 |
| `ramka_plytka_wieczorna_n1_v2` | kieszeń magnesu A (−42,−42): ø | cięciwa X (Z 1) | 5.2 | 5.2 | 0.0 | ✓ | magnet_pocket_d |
| `ramka_plytka_wieczorna_n1_v2` | kieszeń magnesu A: sufit Z | trafienie +Z z (−42,−42,−5) | 2.2 | 2.2 | 0.0 | ✓ | magnet_pocket_depth |
| `ramka_plytka_wieczorna_n1_v2` | faza górna 0,5: z lica przy x 47,8 | trafienie −Z z 20 | 7.7 | 7.7 | 0.0 | ✓ | plate_top_chamfer → 7,7 |
| `ramka_plytka_wieczorna_n1_v2` | krawędź pionowa R1: x lica przy y −47,5 | trafienie −X z (150,−47,5,4) | 47.859 | 47.86602540378444 | -0.007 | ✓ | plate_edge_r → 47,87 (róg C, bez wycięcia) |
| `ramka_plytka_wieczorna_n1_v2` | stożek znacznika A: dno Z | trafienie −Z z (−42,−42,20) | 5.0 | 5.0 | 0.0 | ✓ | 8 − marker_cone_depth 3 |

Różnic > 0.05 mm: **0**.

## 3. Profil haczyka blatu (prawy, y 0): x czubka w funkcji Z lokalnego STL (wierzch blatu Z 0; globalnie Z_g = 63,6 − Z)

| Z STL | x | Z globalne |
|---|---|---|
| 8.0 | 97.0 | 55.6 |
| 8.05 | 97.0 | 55.55 |
| 8.1 | 97.0 | 55.5 |
| 8.15 | 97.0 | 55.45 |
| 8.2 | 97.0 | 55.4 |
| 8.25 | 97.0 | 55.35 |
| 8.3 | 97.0 | 55.3 |
| 8.35 | 97.0 | 55.25 |
| 8.4 | 97.0 | 55.2 |
| 8.45 | 97.0 | 55.15 |
| 8.5 | 97.0 | 55.1 |
| 8.55 | 97.0 | 55.05 |
| 8.6 | 97.0 | 55.0 |
| 8.65 | 97.0 | 54.95 |
| 8.7 | 97.0 | 54.9 |
| 8.75 | 98.3 | 54.85 |
| 8.8 | 98.3 | 54.8 |
| 8.85 | 98.3 | 54.75 |
| 8.9 | 98.3 | 54.7 |
| 8.95 | 98.3 | 54.65 |
| 9.0 | 98.3 | 54.6 |
| 9.05 | 98.3 | 54.55 |
| 9.1 | 98.3 | 54.5 |
| 9.15 | 98.3 | 54.45 |
| 9.2 | 98.3 | 54.4 |
| 9.25 | 98.3 | 54.35 |
| 9.3 | 98.3 | 54.3 |
| 9.35 | 98.3 | 54.25 |
| 9.4 | 98.3 | 54.2 |
| 9.45 | 98.3 | 54.15 |
| 9.5 | 98.3 | 54.1 |
| 9.55 | 98.3 | 54.05 |
| 9.6 | 98.3 | 54.0 |
| 9.65 | 98.3 | 53.95 |
| 9.7 | 98.3 | 53.9 |
| 9.75 | 98.3 | 53.85 |
| 9.8 | 98.235 | 53.8 |
| 9.85 | 98.17 | 53.75 |
| 9.9 | 98.105 | 53.7 |
| 9.95 | 98.04 | 53.65 |
| 10.0 | 97.975 | 53.6 |
| 10.05 | 97.91 | 53.55 |
| 10.1 | 97.845 | 53.5 |
| 10.15 | 97.78 | 53.45 |
| 10.2 | 97.715 | 53.4 |
| 10.25 | 97.65 | 53.35 |
| 10.3 | 97.585 | 53.3 |
| 10.35 | 97.52 | 53.25 |
| 10.4 | 97.455 | 53.2 |
| 10.45 | 97.39 | 53.15 |
| 10.5 | 97.325 | 53.1 |
| 10.55 | 97.26 | 53.05 |
| 10.6 | 97.195 | 53.0 |
| 10.65 | 97.13 | 52.95 |
| 10.7 | 97.065 | 52.9 |
| 10.75 | 97.0 | 52.85 |
| 10.8 | 97.0 | 52.8 |
| 10.85 | 97.0 | 52.75 |
| 10.9 | 97.0 | 52.7 |
| 10.95 | 97.0 | 52.65 |
| 11.0 | 97.0 | 52.6 |
| 11.05 | 97.0 | 52.55 |
| 11.1 | 97.0 | 52.5 |
| 11.15 | 97.0 | 52.45 |
| 11.2 | 97.0 | 52.4 |
| 11.25 | 97.0 | 52.35 |
| 11.3 | 97.0 | 52.3 |
| 11.35 | 97.0 | 52.25 |
| 11.4 | 97.0 | 52.2 |
| 11.45 | 97.0 | 52.15 |
| 11.5 | 97.0 | 52.1 |
| 11.55 | 97.0 | 52.05 |
| 11.6 | 97.0 | 52.0 |
| 11.65 | 97.0 | 51.95 |
| 11.7 | 97.0 | 51.9 |
| 11.75 | 97.0 | 51.85 |
| 11.8 | 97.0 | 51.8 |
| 11.85 | 97.0 | 51.75 |
| 11.9 | 97.0 | 51.7 |
| 11.95 | 97.0 | 51.65 |
| 12.0 | 97.0 | 51.6 |

## 4. Profil garbu pokrywki (prawy, y 0): x czubka w funkcji Z STL (wierzch Z 0; garb nominalnie Z 17,6…18,4, czubek 47,6)

| Z STL | x |
|---|---|
| 16.5 | 48.3 |
| 16.55 | 48.3 |
| 16.6 | 48.3 |
| 16.65 | 48.3 |
| 16.7 | 48.3 |
| 16.75 | 48.3 |
| 16.8 | 48.3 |
| 16.85 | 48.3 |
| 16.9 | 48.3 |
| 16.95 | 48.3 |
| 17.0 | 48.3 |
| 17.05 | 48.3 |
| 17.1 | 48.3 |
| 17.15 | 48.3 |
| 17.2 | 48.3 |
| 17.25 | 48.3 |
| 17.3 | 48.3 |
| 17.35 | 48.3 |
| 17.4 | 48.3 |
| 17.45 | 48.3 |
| 17.5 | 48.3 |
| 17.55 | 48.3 |
| 17.6 | 48.3 |
| 17.65 | 47.813 |
| 17.7 | 47.754 |
| 17.75 | 47.704 |
| 17.8 | 47.654 |
| 17.85 | 47.64 |
| 17.9 | 47.627 |
| 17.95 | 47.613 |
| 18.0 | 47.6 |
| 18.05 | 47.613 |
| 18.1 | 47.627 |
| 18.15 | 47.64 |
| 18.2 | 47.654 |
| 18.25 | 47.704 |
| 18.3 | 47.754 |
| 18.35 | 47.813 |
| 18.4 | 48.3 |
| 18.45 | 48.3 |
| 18.5 | 48.3 |
| 18.55 | 48.3 |
| 18.6 | 48.3 |
| 18.65 | 48.3 |
| 18.7 | 48.3 |
| 18.75 | 48.3 |
| 18.8 | 48.3 |
| 18.85 | 48.3 |
| 18.9 | 48.3 |
| 18.95 | 48.3 |
| 19.0 | 48.3 |
| 19.05 | 48.3 |
| 19.1 | 48.3 |
| 19.15 | 48.3 |
| 19.2 | 48.3 |
| 19.25 | 48.3 |
| 19.3 | 48.3 |
| 19.35 | 48.3 |
| 19.4 | 48.3 |
| 19.45 | 48.3 |
| 19.5 | 48.3 |

## 5. Profil rowka pokrywki w płytce n1 (bok +X, y 20): x dna w funkcji Z STL (wierzch Z 8; rowek nominalnie Z 5,5…6,5, dno 47,2)

| Z STL | x |
|---|---|
| 5.0 | 48.0 |
| 5.05 | 48.0 |
| 5.1 | 48.0 |
| 5.15 | 48.0 |
| 5.2 | 48.0 |
| 5.25 | 48.0 |
| 5.3 | 48.0 |
| 5.35 | 48.0 |
| 5.4 | 48.0 |
| 5.45 | 48.0 |
| 5.5 | 48.0 |
| 5.55 | 47.2 |
| 5.6 | 47.2 |
| 5.65 | 47.2 |
| 5.7 | 47.2 |
| 5.75 | 47.2 |
| 5.8 | 47.2 |
| 5.85 | 47.2 |
| 5.9 | 47.2 |
| 5.95 | 47.2 |
| 6.0 | 47.2 |
| 6.05 | 47.2 |
| 6.1 | 47.2 |
| 6.15 | 47.2 |
| 6.2 | 47.2 |
| 6.25 | 47.2 |
| 6.3 | 47.2 |
| 6.35 | 47.2 |
| 6.4 | 47.2 |
| 6.45 | 47.2 |
| 6.5 | 48.0 |
| 6.55 | 48.0 |
| 6.6 | 48.0 |
| 6.65 | 48.0 |
| 6.7 | 48.0 |
| 6.75 | 48.0 |
| 6.8 | 48.0 |
| 6.85 | 48.0 |
| 6.9 | 48.0 |
| 6.95 | 48.0 |
| 7.0 | 48.0 |

## 6. Pasowania policzone z wartości zmierzonych

| Para | Rachunek | Zmierzone | Nominał | Δ | OK | Reguła |
|---|---|---|---|---|---|---|
| blat kołnierz ↔ korpus wnętrze (na stronę) | (195 − 2·97,0)/2 | 0.5 | 0.5 | 0.0 | ✓ | R48: 0,3 + SLS ±0,3/200 → 0,5 |
| haczyk blatu: zahaczenie w kieszeni | czubek 98,3 − ściana wewn. 97,5 | 0.8 | 0.8 | 0.0 | ✓ | zatrzask (R48) |
| haczyk blatu: luz do dna kieszeni | dno 98,5 − czubek 98,3 | 0.2 | 0.2 | 0.0 | ✓ | zatrzask |
| haczyk blatu: dół rampy występu Z globalnie (profil, x > 97,05) | 63,6 − Z_STL | 52.9 | 52.85 | 0.05 | ✓ | snap_hook_z; góra występu 54.85; lico pionowe (x > 98,25) Z 53.85…54.85 = zahaczenie pionowe 1,0 + rampa 1,0 (U6 trzeciego oka) |
| haczyk blatu: luz pod występem | 52,85 − kieszeń dolna 52,6 | 0.3 | 0.25 | 0.05 | ✓ | R47 |
| haczyk blatu: luz nad występem | kieszeń górna 55,1 − 54,85 | 0.25 | 0.25 | 0.0 | ✓ | R47 |
| haczyk 8 w kieszeni 10 (na stronę) | (10 − 8)/2 | 1.0 | 1.0 | 0.0 | ✓ | ruchome |
| kołek wkładki ø3 w otworze blatu ø3,3 (na stronę) | (3,3 − 3,0)/2 | 0.15 | 0.15 | 0.0 | ✓ | wciskane 0,1–0,15 (4.8) |
| kołek wkładki: luz osiowy | głębokość 3,8 − długość 3,5 | 0.3 | 0.3 | 0.0 | ✓ | R8 |
| magnes ø5 w kieszeni blatu ø5,4 (na stronę) | (5,4 − 5)/2 | 0.2 | 0.2 | 0.0 | ✓ | magnesy 0,1–0,2 (klejone) |
| magnes ø5 w otworze ucha ø5,4 (na stronę) | (5,4 − 5)/2 | 0.2 | 0.2 | 0.0 | ✓ |  |
| magnes ø5 × 2 w kieszeni płytki ø5,2 × 2,2 | (5,2 − 5)/2; cofnięcie 2,2 − 2 | 0.1 | 0.1 | 0.0 | ✓ | cofnięcie 0.2 |
| płytka 96 w otworze wkładki 96,6 (na stronę) | (96,6 − 96)/2 | 0.3 | 0.3 | 0.0 | ✓ | ruchome 0,2–0,3 |
| płytka 96 we wnęce pokrywki 96,6 (na stronę) | (96,6 − 96)/2 | 0.3 | 0.3 | 0.0 | ✓ | ruchome 0,2–0,3 |
| kołek orientacyjny 4,4 w wycięciu 5 (luz po stronie otwartej, płytka wycentrowana) | lico kołka 43,4 − lico wycięcia 43,0 | 0.4 | 0.4 | 0.0 | ✓ | 4.11/R52 U2: 0,4 |
| garb pokrywki: zahaczenie w rowku płytki | bok płytki 48,0 − czubek 47,6 | 0.4 | 0.4 | 0.0 | ✓ | zatrzask |
| garb pokrywki: luz do dna rowka | czubek 47,6 − dno 47,2 | 0.4 | 0.4 | 0.0 | ✓ | zatrzask |
| garb pokrywki: wysokość Z (profil, x < 48,25) | zakres Z STL | 0.75 | 0.8 | -0.05 | ✓ | cover_snap_hgt; Z 17.65…18.35 |
| rowek płytki: wysokość Z (profil, x < 47,95) | zakres Z STL | 0.95 | 1.0 | -0.05 | ✓ | cover_groove_w; Z 5.55…6.45 (wierzch 8 → 2 pod wierzchem = 6,0) |
| tulejka ø11,85 w otworze korpusu ø12 (na stronę) | (12 − 2·5,925)/2 | 0.075 | 0.075 | 0.0 | ✓ | wciskane 0,1–0,15 (R52: 0,075 w żywicy bez skurczu) |
| gwint gniazda ø8 w tulejce ø8,2 (na stronę) | (8,2 − 8)/2 | 0.1 | 0.1 | 0.0 | ✓ | R50‑3 |
| tulejka: długość walca 2 vs ściana skrzynki 2 | 3 − 1 vs 2,0 | 0.0 | 0.0 | 0.0 | ✓ | walec kończy się w licu ściany (nakrętka dociska ścianę) |
| podkładka: otwór 3,4 vs M3 (na stronę) | (3,4 − 3)/2 | 0.198 | 0.2 | -0.002 | ✓ | ø zewn. 9 = stadion 9 |
| dyfuzor 160 × 2 w kieszeni 162 × 2 (na stronę) | (162 − 160)/2 | 1.0 | 1.0 | 0.0 | ✓ | licowanie: głębokość 2.0 − 2 = 0.0 |
| czujnik Halla TO‑92 (4 × 5 × 1,5 proxy) w kieszeni 5,0 × 5,5: luz łączny X | 5,0 − 4 | 1.0 | 1.0 | 0.0 | ✓ | Y: 0.5 |
| łańcuch: wierzch blatu = korpus_h + blat_t | 59,6 + 4 | 63.6 | 63.6 | 0.0 | ✓ | blat_top_z |
| łańcuch: półki wkładki | 63,6 + 2,5 | 66.1 | 66.1 | 0.0 | ✓ | D4 |
| łańcuch: wierzch ramy wkładki | 63,6 + 6 | 69.6 | 69.6 | 0.0 | ✓ | D4 |
| łańcuch: wierzch płytki | 66,1 + 8 | 74.1 | 74.1 | 0.0 | ✓ | D4 |
| pokrywka: dół kołnierza nad ramą wkładki | 74,1 − (20 − 2 − 14) = 70,1 vs rama 69,6 | 0.5 | 0.5 | 0.0 | ✓ | 4.11 bez styku |
| pokrywka: prześwit nad płytką | wnęka 18 − kołnierz pod wierzch 4 | 14.0 | 14.0 | 0.0 | ✓ | cover_inner_h |
| panel: stadion 4,0 + dystans 50 = spód PCB | 4 + 50 | 54.0 | 54.0 | 0.0 | ✓ | panel_pcb_z |
| Pi: boss 8 + stos 26 = szczyt stosu | 8 + 26 | 34.0 | 34.0 | 0.0 | ✓ | zapas do strefy złączy 42 − 34 = 8 |
| wkręt blatu M3×8: zapas do dna otworu słupka | koniec wkrętu 100 − 8 = 92; dno 91 | 1.0 | 1.0 | 0.0 | ✓ | gwint w PA12 97 → 92 = 5,0 |
| wkręt Pi M2,5×6: zapas do dna otworu bossa | otwór 5 − (6 − 1,6) | 0.6 | 0.6 | 0.0 | ✓ |  |
