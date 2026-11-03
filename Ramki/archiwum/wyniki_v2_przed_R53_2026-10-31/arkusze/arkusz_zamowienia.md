# Arkusz zamówienia — części drukowane (v2)

Wygenerowany przez `ramka_generator.py`. Objętości i gabaryty zmierzone na siatkach STL (gabaryt w orientacji druku). Ilości z `parametry.json → quantities`, materiały per część z `materials` (R50). 15 pozycji: 10 do drukarni, 5 druku własnego (bez płytek bazowych, Z28). Ten sam arkusz w `arkusz_zamowienia.csv` (separator `;`, przecinek dziesiętny, UTF‑8; koszty puste = druk własny).

## A. Do zamówienia w drukarni (materiał „PA12 drukarnia…”)

| Plik STL | Część | Szt. | Technologia | Materiał | Kolor | Wykończenie | Obj. [cm³] | Gabaryt X × Y × Z [mm] | Najtańszy [zł] | Pokazowy [zł] | Uwagi |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `ramka_plytka_wieczorna_n1_v2.stl` | płytka wieczorna n1 | 1 | MJF/SLS (D2) | PA12 drukarnia (alt. żywica firma) | biały (naturalny) | mat, bez wygładzania wierzchu | 57,95 | 96,0 × 96,0 × 8,6 | 52–93 | 52–93 | alternatywa CNC PMMA opal: STEP przez FreeCAD (D2) |
| `ramka_plytka_wieczorna_n2_v2.stl` | płytka wieczorna n2 | 1 | MJF/SLS (D2) | PA12 drukarnia (alt. żywica firma) | biały (naturalny) | mat, bez wygładzania wierzchu | 57,95 | 96,0 × 96,0 × 8,6 | 52–93 | 52–93 | alternatywa CNC PMMA opal: STEP przez FreeCAD (D2) |
| `ramka_plytka_wieczorna_n3_v2.stl` | płytka wieczorna n3 | 1 | MJF/SLS (D2) | PA12 drukarnia (alt. żywica firma) | biały (naturalny) | mat, bez wygładzania wierzchu | 57,95 | 96,0 × 96,0 × 8,6 | 52–93 | 52–93 | alternatywa CNC PMMA opal: STEP przez FreeCAD (D2) |
| `ramka_plytka_poranna_n4_v2.stl` | płytka poranna n4 | 1 | MJF/SLS (D2) | PA12 drukarnia | biały (naturalny) | mat, bez wygładzania wierzchu | 60,23 | 96,0 × 96,0 × 8,6 | 54–96 | 54–96 | alternatywa CNC PMMA opal: STEP przez FreeCAD (D2) |
| `ramka_plytka_poranna_n5_v2.stl` | płytka poranna n5 | 1 | MJF/SLS (D2) | PA12 drukarnia | biały (naturalny) | mat, bez wygładzania wierzchu | 60,23 | 96,0 × 96,0 × 8,6 | 54–96 | 54–96 | alternatywa CNC PMMA opal: STEP przez FreeCAD (D2) |
| `ramka_plytka_poranna_n6_v2.stl` | płytka poranna n6 | 1 | MJF/SLS (D2) | PA12 drukarnia | biały (naturalny) | mat, bez wygładzania wierzchu | 60,23 | 96,0 × 96,0 × 8,6 | 54–96 | 54–96 | alternatywa CNC PMMA opal: STEP przez FreeCAD (D2) |
| `ramka_korpus_W_v2.stl` | korpus W (napis „RAMKA WIECZORNA”) | 1 | MJF/SLS (D2) | PA12 drukarnia | grafit | barwienie na grafit; pokazowy: + wygładzanie parowe | 233,66 | 200,0 × 200,6 × 59,6 | 210–374 | 328–583 | geometria W i P identyczna poza napisem (Z18) |
| `ramka_korpus_P_v2.stl` | korpus P (napis „RAMKA PORANNA”) | 1 | MJF/SLS (D2) | PA12 drukarnia | grafit | barwienie na grafit; pokazowy: + wygładzanie parowe | 233,63 | 200,0 × 200,6 × 59,6 | 210–374 | 328–583 | geometria W i P identyczna poza napisem (Z18) |
| `ramka_blat_v2.stl` | blat | 2 | MJF/SLS (D2) | PA12 drukarnia | grafit | barwienie na grafit; pokazowy: + wygładzanie parowe | 72,57 | 200,0 × 200,0 × 14,0 | 131–232 | 204–362 | — |
| `ramka_wkladka_v2.stl` | wkładka gniazda płytki | 3 | MJF/SLS (D2) | PA12 drukarnia | biały (naturalny) | surowe (naturalne) | 12,41 | 130,0 × 148,3 × 11,0 | 34–60 | 34–60 | — |

## B. Druk własny (bez kosztu drukarni)

| Plik STL | Część | Szt. | Technologia | Materiał | Obj. [cm³] | Gabaryt X × Y × Z [mm] | Uwagi |
|---|---|---|---|---|---|---|---|
| `ramka_pokrywka_v2.stl` | pokrywka płytki | 4 | FDM (druk własny) | PETG FDM (własny) | 30,060 | 99,6 × 99,6 × 20,0 | — |
| `ramka_tulejka_dc_v2.stl` | tulejka redukcyjna gniazda DC | 2 | SLA/DLP żywica lub FDM PETG (druk własny) | żywica firma / PETG | 0,240 | 15,0 × 15,0 × 3,0 | tylko gdy pomiar #16 da gniazdo ø8 (R50-3) |
| `ramka_podkladka_panelu_05_v2.stl` | podkładka panelu 0,5 mm | 8 | SLA/DLP żywica lub FDM PETG (druk własny) | żywica firma / PETG | 0,030 | 9,0 × 9,0 × 0,5 | do wyrównania dystansu po pomiarach #4/#9 (R50-8) |
| `ramka_podkladka_panelu_1_v2.stl` | podkładka panelu 1 mm | 8 | SLA/DLP żywica lub FDM PETG (druk własny) | żywica firma / PETG | 0,050 | 9,0 × 9,0 × 1,0 | do wyrównania dystansu po pomiarach #4/#9 (R50-8) |
| `ramka_podkladka_panelu_2_v2.stl` | podkładka panelu 2 mm | 8 | SLA/DLP żywica lub FDM PETG (druk własny) | żywica firma / PETG | 0,110 | 9,0 × 9,0 × 2,0 | do wyrównania dystansu po pomiarach #4/#9 (R50-8) |

## Sumy (tylko drukarnia)

| Zakres | Objętość [cm³] | Najtańszy [zł] | Pokazowy [zł] |
|---|---|---|---|
| 10 pozycji × ilości | 1004,20 | 904–1607 | 1212–2155 |

Druk własny: 122,2 cm³ (pokrywka płytki × 4, tulejka redukcyjna gniazda DC × 2, podkładka panelu 0,5 mm × 8, podkładka panelu 1 mm × 8, podkładka panelu 2 mm × 8).

## Stawki i wzory (z `parametry.json`)

- Stawka PA12: `cost_rate_min` 0,90 – `cost_rate_max` 1,60 zł/cm³; barwienie `cost_dye_factor` ×1,20; wygładzanie `cost_smooth_factor` ×1,30.
- Koszt tylko dla pozycji z materiałem zaczynającym się od „PA12 drukarnia” (K‑57, R50); druk własny bez kosztu.
- Wariant najtańszy (PA12 naturalne, bez barwienia): koszt = objętość × ilość × stawka (min…max).
- Wariant pokazowy: części grafitowe (korpus, blat — Z19) = objętość × ilość × stawka × 1,20 × 1,30; części białe bez mnożników.
- Płytki wieczorne n1–n3 liczone do drukarni; alternatywa żywica w firmie po teście skanera (decyzja G4).

## Uwaga dla CNC (STEP / FreeCAD)

Usługodawca CNC (płytki z PMMA opal, D2) potrzebuje pliku STEP: FreeCAD → Part → „Utwórz kształt z siatki” (tolerancja 0,01) → „Przekształć w bryłę” → Eksport `.step`. STL pozostaje plikiem wzorcowym; STEP nie jest generowany przez skrypt.
