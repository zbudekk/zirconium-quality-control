# R54 — gniazda i znaczniki w kole pola skanowania (lista edycji w źródle prawdy)

Data: 2026‑11‑01. Decyzja właściciela: „[cytat usuniety]” (ten sam obrys płytki 96 × 96, gniazda i znaczniki przestawione do koła; ramka bez zmian).
Zakres edycji: `parametry.json`, `plan_ramki_v2.md`, `protokol_weryfikacji_v2.md`, `00_NADZOR_STAN.md`, nowe `narzedzia/uklad_kolo_R54.js`, `narzedzia/weryfikuj_uklad_R54.js`.
NIE dotknięto: `ramka_generator.py`, `wyniki_v2/`, `recenzja/`, dokumentów stanowiska i zakupów, modelu 3D, pakietu. Kopie sprzed edycji: `archiwum/*_przed_R54_2026-11-01.*`.

## 0. Problem i rozstrzygnięcie

Skaner obraca płytkę wokół osi pionowej (ścieżka bez przechyłu), więc w całym obrocie widoczne jest **koło** wokół osi stolika, nie kwadrat 100 × 100. Przy polu ø100 (promień 50):

| Element dawnego układu | Promień od środka płytki |
|---|---|
| gniazda skrajne wieczorne (x ±30, y −40,5, ø9; x ±36, y 1,5, ø15) | 54,9 |
| gniazda skrajne poranne | 52,6 |
| rynienki tylne (R6 / R7) | 51,2 / 48,3 |
| stożki znaczników w rogach (±42, ±42) | 61,9 |
| narożniki płytki | 67,9 |

Wybrane: **wariant (1)** — obrys płytki, wycięcie, dołki, numer, kieszenie magnesów, rowek pokrywki bez zmian; wkładka, pokrywka, korpus, blat, czujniki Halla bez zmian. Zmienia się tylko układ gniazd i położenie stożków znaczników, czyli dane w `parametry.json` (`ev_rows`, `mo_rows`, `ev_marker_pos`, `mo_marker_pos`) i pliki płytek.
Odrzucone: (2) płytka okrągła ø96–100 i (3) mniejszy kwadrat — ta sama pojemność, a wymagają nowej wkładki (otwór okrągły, półki jako wycinki, kołek i magnesy na przekątnych) i nowych pokrywek. (2) wraca, jeśli pomiar #12 da pole < ~94.

Zapas: `socket_zone_r` = `scan_field_d`/2 − `scan_center_tol` − `work_overhang` = 50 − 1,5 − 1,5 = **47** (obrysy górne gniazd, rynienek i stożków znaczników w kole r 47 od środka płytki).

## 1. `parametry.json` — klucze NOWE (6) — do dopisania w walidatorze (R14)

| Sekcja | Klucz | Wartość | Status | Źródło |
|---|---|---|---|---|
| plytka | scan_field_d | 100 | DO_ZMIERZENIA (#12) | Z29 |
| plytka | scan_center_tol | 1.5 | ZALOZENIE | Z29 |
| plytka | work_overhang | 1.5 | ZALOZENIE | Z29 |
| plytka | socket_zone_r | 47 | LICZONE: `scan_field_d / 2 - scan_center_tol - work_overhang` | Z29 |
| plytka | ev_marker_pos | {"A": [−35.5, −26.5], "B": [−35.5, 26.5], "C": [35.5, 26.5]} | ZALOZENIE | D6 |
| plytka | mo_marker_pos | {"A": [−34.5, −28], "B": [−30, 32.5], "C": [30, 32.5]} | ZALOZENIE | D6 |

## 2. `parametry.json` — wartości / opisy ZMIENIONE

| Klucz | Było | Jest |
|---|---|---|
| ev_rows | 6 rzędów: ø9 ×6 (y −40,5), ø9 ×7 (−28,5), ø12 ×6 (−15), ø15 ×5 (1,5), rynienka (19,5), rynienka (37,5) = 24 + 2 | 5 rzędów: rynienka 60 × 15 (y −31,5), ø12 ×6 (−15), ø9 ×7 (−1,5), ø15 ×5 (13,5), rynienka (31,5) = **18 + 2** |
| mo_rows | 7 rzędów = 35 + 2 | 7 rzędów: ø7,5 ×3 (y −41,25), rynienka 50 × 13 (−28), ø10 ×7 (−13,5), ø12,5 ×6 (0,75), ø7,5 ×8 (13,6), ø7,5 ×7 (22,7), rynienka (35,95) = **31 + 2** |
| marker_offset | opis: oś znacznika od krawędzi rogu | opis: oś **kieszeni magnesu** od krawędzi rogu (6 → ±42); stożki znaczników osobno |
| socket_zone | opis: bok strefy gniazd | opis: kwadrat; od R54 dodatkowo koło `socket_zone_r` |

Liczby bez zmian: `plate_size` 96, `socket_zone` 90, `socket_wall_min` 3, `socket_depth` 4, średnice gniazd, rynienki 60 × 15 / 50 × 13, otwory ø3, `marker_cone_d/depth` 5/3, `marker_offset` 6, dołki kodu, wycięcie, numer, rowek pokrywki.

Pełne wartości rzędów (środki, mm):

Wieczorna: R1 rynienka y −31,5; R2 ø12 y −15, x ±7,5, ±22,5, ±37,5; R3 ø9 y −1,5, x 0, ±12, ±24, ±36; R4 ø15 y 13,5, x 0, ±18, ±36; R5 rynienka y 31,5. Blok y −39…39.
Poranna: R1 ø7,5 y −41,25, x 0, ±10,5; R2 rynienka y −28; R3 ø10 y −13,5, x 0, ±13, ±26, ±39; R4 ø12,5 y 0,75, x ±7,75, ±23,25, ±38,75; R5 ø7,5 y 13,6, x ±5,25, ±15,75, ±26,25, ±36,75; R6 ø7,5 y 22,7, x 0, ±10,5, ±21, ±31,5; R7 rynienka y 35,95. Blok y −45…42,45. Rzędy R4→R5→R6 w szachownicę (odstęp osi 13,00 i 10,51 = suma promieni + 3).

## 3. `plan_ramki_v2.md` — edycje

| Miejsce | Zmiana |
|---|---|
| 1. Założenia: Z1 | dopisek [R54]: pole przy obrocie = koło; `socket_zone_r` 47; obrys płytki bez zmian; #12 mierzy `scan_field_d` |
| Z4 | **UCHYLONE**: stożki znaczników i kieszenie magnesów już nie współosiowe |
| Z20 | zastąpione: układ kołowy, rynienki z przodu i z tyłu, 18 + 2 / 31 + 2 |
| Z29 (nowe) | koło pola skanowania, zapasy, `socket_zone_r` |
| D6 | przepisane w całości: uzasadnienie, zasady, warunek koła, tabele rzędów z promieniami skrajnymi, szachownica, znaczniki, wyniki sprawdzenia, odrzucone alternatywy |
| 4.1 p. 3 | pozycje stożków znaczników per typ (`ev_/mo_marker_pos`) |
| 4.1 p. 6 | kieszenie magnesów w rogach (`marker_offset`), nie współosiowe |
| 4.1 JSON | przykład `markers` i `sockets` wg nowego układu |
| 4.11 | nowy wiersz „Koło pola skanowania (R54, Z29)” z liczbami |
| 10. Pomiar #12 | przeformułowany: makieta z okręgami ø90/94/100, kryterium ≥ 100; klucz `scan_field_d` |
| 13. Rejestr | wiersz R54 (po R53); nagłówek R1…R54 |
| 14. Zmiany | punkt 23 |

## 4. `protokol_weryfikacji_v2.md` — edycje

| Sprawdzenie | Zmiana |
|---|---|
| K‑05 (a) | 18/2 i 31/2 — liczby z `ev_rows` / `mo_rows`, nie stałe w skrypcie |
| K‑05 (c) | dodatkowo: dla obu końców osi obrysu √(x² + y²) + r ≤ `socket_zone_r` 47 |
| K‑09 | pozycje znaczników z `markers` JSON (= `*_marker_pos`); kontrola odwrotna: dawne rogi (±42, ±42, −1) W BRYLE |
| K‑16 | dodatkowo: promień znacznika ≤ 44,5; znacznik–gniazdo ≥ 3; znacznik–dołek ≥ 1,5; znacznik–kieszeń magnesu (XY) ≥ 1,5 zamiast dawnego „stożek–kieszeń (Z)” |

Bez zmian: K‑06, K‑07, K‑08 (sondy liczone z JSON), K‑10, K‑11, K‑12 (kieszenie magnesów nadal w rogach), K‑17…K‑22 (pokrywka), K‑23…K‑32 (wkładka, luz płytki), K‑53 (złożenie; płytka n1 w zestawie — nowy STL), K‑55 (magnes–czujnik, bez zmian geometrii).

## 5. `ramka_generator.py` — co ma zmienić WYKONAWCA (nie zrobione tu)

1. `uklad_pochodne`: `markers` z `ev_marker_pos` / `mo_marker_pos` (zależnie od typu — funkcja potrzebuje argumentu `typ`); `magnet_pockets` nadal z `marker_offset`. Walidator kluczy (R14): dodać 6 nowych kluczy.
2. `sprawdz_uklad_json` (K‑05): oczekiwane liczby round/trough liczyć z `ev_rows` / `mo_rows`; dodać warunek (c) koła: dla obu końców osi obrysu `hypot(x, y) + r ≤ socket_zone_r`; warunek (d) narożników zostaje (koło go implikuje). Uwaga: rzędy w szachownicę — warunek (e) ścianki 3 mierzy odległość obrysów (już tak działa).
3. K‑09: sondy z pozycji `markers` JSON zamiast stałych ±42; dodać kontrolę odwrotną dawnych rogów (W BRYLE).
4. `sprawdz_scianki_naroznikow` (K‑16): dodać promień znacznika ≤ `socket_zone_r` − d/2, znacznik–gniazdo ≥ 3, znacznik–dołek ≥ 1,5, znacznik–kieszeń magnesu (XY) ≥ 1,5; usunąć „stożek–kieszeń magnesu (Z)”.
5. Przed przebiegiem: `wyniki_v2/json/uklad_gniazd_wieczorna.json` i `_poranna.json` przenieść do `archiwum/` (stary układ 24 + 2 / 35 + 2) i usunąć z `wyniki_v2/json/` — skrypt wygeneruje nowe z `ev_rows` / `mo_rows` (`leds` puste). `id` rzędami od przodu: wieczorna id 1 = rynienka przednia, 2–7 ø12, 8–14 ø9, 15–19 ø15, 20 rynienka tylna; poranna id 1–3 ø7,5, 4 rynienka, 5–11 ø10, 12–17 ø12,5, 18–25 ø7,5, 26–32 ø7,5, 33 rynienka.
6. Nowe STL: `ramka_plytka_wieczorna_v2.stl`, `_poranna_v2.stl` i warianty n1–n6; `kody_plytek.md`, arkusz wymiarów i zamówienia (objętości płytek). Wkładka, pokrywka, korpus, blat: pliki bez zmian (SHA jak po C2).
7. Bramki: etap A (płytki) → recenzent K‑05…K‑16 → etap B/C tylko w zakresie płytek i K‑53 (zestaw z nową płytką n1); potem trzecie oko dla płytek.
8. Kontrola szybka na parametrach: `node narzedzia/weryfikuj_uklad_R54.js` (musi dać „układ zgodny z R54”).

## 6. Po plikach — dokumenty i model do aktualizacji (osobne zadanie)

- `Stanowisko kontroli cyrkonii — plan wdrozenia v2.md/.pdf`: „do 24 koron i 2 mostów / do 35 koron i 2 mostów” → 18 / 31; punkt 11 założeń (koło przy obrocie); test #12; opis płytki (znaczniki w kole).
- `Zakupy i druk — stanowisko kontroli cyrkonii.md/.pdf`: wzmianka 24/35; test skanera (makieta z okręgami).
- `wyniki_v2/arkusze/kody_plytek.md`, `arkusz_wymiarow.md`, `arkusz_zamowienia.*` — generuje wykonawca.
- Model 3D `ramka_3d.html` / animacja (artefakt v3 R53) — płytki z nowym układem; pakiet `Ramki_pakiet/` i wgranie na Drive (nowe pliki, nic nie usuwać).

## 7. Co się NIE zmienia (dla recenzenta i trzeciego oka)

Obrys płytki 96 × 96 × 8 (R 1, faza 0,5), wycięcie D 5 × 5, dołki kodu (−45, −36/−33/−30), numer (39,5, −44,5), rowek pokrywki, kieszenie magnesów (±42, ±42), luz płytki we wkładce 0,4, kołek orientacyjny, półki i kieszenie Halla wkładki, pokrywka 99,6 × 99,6 × 20, korpus 200 × 200 × 59,6, blat, panel, Pi, zasilanie, wentylacja.

## SPÓJNOŚĆ SPRAWDZONA (1.11)

`node narzedzia/weryfikuj_uklad_R54.js`: wieczorna max promień 46,389 ≤ 47 (ø12 w (±37,5, −15)), poranna 46,931 ≤ 47 (rynienka tylna); kwadrat 43,5 / 45,0 ≤ 45; min ścianka 3,000 / 3,000; znaczniki: promień 44,30 / 44,43 / 44,23 ≤ 44,5, ścianka do gniazd 3,17 / 3,01 / 3,01 (wieczorna) i 7,00 / 3,01 / 3,01 (poranna); dołek–gniazdo 9,77 / 11,56 ≥ 3; dołek–znacznik 6,62 / 7,19 ≥ 1,5. `parametry.json` parsuje (279 kluczy; `socket_zone_r` = wzór). Wspólne pozycje znaczników dla obu płytek: niemożliwe przy ściance 3 (sprawdzone — stąd osobne klucze).
