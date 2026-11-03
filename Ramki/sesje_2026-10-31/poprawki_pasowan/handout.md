# Handout — sesja POPRAWKI PASOWAŃ (R53), 31.10.2026

**STATUS: ZAKOŃCZONE**

1. **Co zmieniono:** R53 = 13 kluczy `parametry.json` (kołnierz blatu luz 0,7; haczyk 1,5 przy czubku 98,3; kieszeń zatrzasku 11 × 3,5 × 1,3 na Z 52,1…55,6; otwór wkrętu blatu ø3,6; otwór kołka wkładki ø3,4; otwór wkładki 96,8 + kołek orientacyjny 0,6 od ścian; rowek panelu 3,6), nowe STL: blat, korpus W, korpus P, wkładka (13 pozostałych bajtowo bez zmian); wpis R53 w planie (sekcje 13/14), sondy protokołu, minimalne poprawki generatora (`# R53`).
2. **Czy STL gotowe do zamówienia:** TAK — `wyniki_v2/stl/` (17 plików, przebieg C iter5 + SPRAWDZ iter5, B=0 P=0 D=0); weryfikacja 0 NIE (`weryfikacja_R53.md`): generator, kopie recenzenta A/B/C, trzecie oko (0 blokujących), pomiar własny ze znakiem 118/118.
3. **Co zostało (poza mandatem sesji):** nanieść wartości R53 do tabeli 3 i opisów 4.x planu (12 odstępstw informacyjnych „tabela 3 planu” w raporcie); dokumenty wdrożenia/zakupów (przewiercanie ø2,1/ø2,5, specyfikacja zamówienia, kryterium odbioru > ±0,5, tulejka po pomiarze otworu); przebudować `Ramki_pakiet/`, `Ramki_do_wgrania/` i model 3D (mają STL sprzed R53).

## Wynik w liczbach

| Sprawdzenie | Wynik |
|---|---|
| `--etap B --iter 5` / `--etap C --iter 5` / `--etap SPRAWDZ --iter 5` | B=0 P=0 D=0 (28 s / 38 s / 3 s) |
| Kopie recenzenta: `sprawdz_A_R53` 125 / `sprawdz_B_R53` 73 / `sprawdz_C_R53` 27 / kanały Halla A,B,C | 0 NIE / 0 NIE / 0 NIE / ciągłe |
| `sprawdz_A_R53` z pokrywką (tylko dla objętości K‑57) | 3 NIE = znane fałszywe S‑05 (K‑02/K‑19/K‑21; pokrywka bajtowo bez zmian) |
| Trzecie oko (`trzecie_oko_R53.py`, 17 STL + bryły zastępcze) | 671 pasowań, 781 wymiarów, 107 ścianek, 76 kroków montażu; 0 blokujących (8 „INFORMACYJNIE” jak 27.10) |
| Pomiar własny trimesh ze znakiem (`pomiar_R53.py`) | po R53: 118/118 zgodnych; przed R53 (stare STL + stare parametry): 118/118 |
| STL vs kopia zapasowa | zmienione dokładnie 4 (blat, korpus W, korpus P, wkładka); 13 identycznych bajtowo |

Pasowania po R53 (z siatek): kołnierz 0,700; zahaczenie haczyka 0,800; luz do dna kieszeni 0,500; luz Z 0,750/0,750; boczny 1,500; wkręt ø3,600; kołek 0,200; płytka 0,400; rowek 3,600; tulejka 0,075 (celowo wciskowe); ściana za kieszenią 1,200; dno słupka 1,600.

## Co wykryła weryfikacja i co poprawiono w trakcie

- 1. przebieg kopii trzeciego oka: **kołek orientacyjny wkładki przesunął się z otworem o 0,1 i jego naroże zahaczało o R 1,5 wnęki pokrywki o 0,059 mm** (K‑53 generatora z kurczeniem 0,05 tego nie widzi). Poprawka T6c: `orient_post_gap` 0,5 → 0,6 (kołek wraca w (45,6, −45,6) jak przed R53), regeneracja B5/C4, pełna ponowna weryfikacja.
- Opis reguły „płytka w otworze wkładki” w arkuszu pasowań („ruchome 0,2–0,3”) → „ruchome 0,4 (R53)”, regeneracja C5 + SPRAWDZ5, ponowne kopie B/C i trzecie oko na C5.
- Literały w skryptach recenzenta i trzeciego oka (97,0; 52,3; 27,7; 96,6; 148,3; 96,9; R 4,5) — zmienione tylko w KOPIACH w `skrypty/` (oryginały w `recenzja/`, `recenzja_koncowa/` nietknięte); każda zmiana opisana w nagłówku kopii.

## Pliki sesji (`sesje_2026-10-31/poprawki_pasowan/`)

- `R53_projekt.md` — tabela decyzji T1–T16, W‑04 (klucz, stara, nowa, uzasadnienie, K‑xx).
- `weryfikacja_R53.md` — tabela pasowań przed/po/zmierzone/status + wyniki wszystkich metod.
- `skrypty/` — `pomiar_R53.py` (trimesh), `zloz_weryfikacje.py`, kopie `sprawdz_A/B/C/B_kanaly_R53.py`, `trzecie_oko_R53.py`; wyniki w `skrypty/wyniki/`, `skrypty/wyniki_3oko/` (`tabele_auto.md`).
- `logi/` — logi generatora i skryptów, SHA‑256 po każdym przebiegu; `stl_etapB/` — STL z B iter4 (przed T6c, tylko do porównań).
- Kopie sprzed R53: `archiwum/wyniki_v2_przed_R53_2026-10-31/`, `archiwum/parametry_przed_R53_2026-10-31.json`, `archiwum/sha256_stl_przed_R53.txt`, `archiwum/*_przed_R53_2026-10-31.*` (generator, protokół, plan). Nic nie usunięto.

## Zmienione pliki projektu

- `parametry.json` — 13 kluczy (każdy z opisem „R53 (Tx)”): `blat_skirt_clearance`, `snap_hook_h`, `snap_pocket_depth`, `snap_pocket_h`, `snap_pocket_z` (wzór `korpus_h - 7.5`), `snap_pocket_w`, `blat_screw_hole_d`, `blat_pin_hole_d`, `insert_opening`, `tab_root_x_out`, `orient_post_gap`, `panel_slot_w`, `panel_screw_hole_d`.
- `plan_ramki_v2.md` — sekcja 13 wiersz R53, sekcja 14 p. 22.
- `protokol_weryfikacji_v2.md` — tabela 1 (wkładka 148,4), K‑23, K‑27, K‑30, K‑32, K‑35, K‑39, K‑42, K‑46, K‑47, K‑49, K‑56, K‑60 („[R53]”).
- `ramka_generator.py` — sondy K‑23/K‑27/K‑32/K‑42, K‑56 z parametrów, 5 opisów reguł pasowań (komentarze `# R53`).
- `wyniki_v2/` — przebudowane w całości przez generator (STL, `.blend`, rendery, arkusze, README, raporty B iter4/5, C iter3/4/5, SPRAWDZ iter3/4/5).

## Środowisko i komendy

- Blender 5.2: `"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"`. Python: `py -3.12 -X utf8` (numpy, trimesh 5.2; `-I` ignoruje `PYTHONUTF8`, stąd `-X utf8`). Generator kasuje `wyniki_v2/` przed budową (G‑02).

```
cd <PC>\Desktop\Ramki
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b -P ramka_generator.py -- --etap C --iter 6
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b -P ramka_generator.py -- --etap SPRAWDZ --iter 6
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b -P sesje_2026-10-31\poprawki_pasowan\skrypty\sprawdz_B_R53.py -- --iter R53
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b -P sesje_2026-10-31\poprawki_pasowan\skrypty\trzecie_oko_R53.py
py -3.12 -X utf8 -I sesje_2026-10-31\poprawki_pasowan\skrypty\pomiar_R53.py wyniki_v2\stl sesje_2026-10-31\poprawki_pasowan\skrypty\wyniki\pomiar_R53_po.json
```

## Decyzje do wiadomości właściciela (zapisane w R53, nie wymagają działania)

- Ściana korpusu za kieszenią zatrzasku 1,2 mm lokalnie (4 pola 11 × 3,5, nienośne) — odstępstwo od zasady 4.8 „≥ 1,5”, przyjęte świadomie (alternatywa: zahaczenie 0,4 — za mało).
- Otwór wkładki 96,8 wbrew DESIGN B §3.3 p. 1 („96,6 zostaje przy MJF”) — zasada sumy tolerancji obu części; interfejs płytki bez zmian.
- Tulejka DC 11,85 w ø12 — celowo wciskowe, druk własny po pomiarze otworu. Pokrywka 0,3 — bez zmian (FDM, skalowanie pierwszej sztuki; rowek płytki ogranicza).
- Dno słupka blatu pod otworem wkrętu 1,6 (było 1,8; ≥ 1,5), gwint wkrętu M3 × 8 w słupku 4,8 (było 5,0).
