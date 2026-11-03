# Brief sesji „POPRAWKI PASOWAŃ (R53)” — do uruchomienia z aplikacji desktop

Koordynator nie mógł uruchomić sesji przez Remote Control (31.10.2026). Wklej poniższy prompt do nowej sesji (Fable 5.1, effort high, folder `<PC>\Desktop\Ramki`) albo napisz do koordynatora z aplikacji desktop: „uruchom sesję poprawek pasowań”.

## Tło
Projekt „[cytat usuniety]”: stanowisko kontroli koron z cyrkonii; ramki W/P z korpusem PA12 (Pi, panel, DC), blatem na 4 zatrzaskach + 2 wkrętach tylnych, wkładką, pokrywką, płytkami n1–n6 (skaner Aidite A‑IS Pro 3). Geometria z `ramka_generator.py` (Blender) i `parametry.json`; wynik `wyniki_v2/` (17 STL). Weryfikacja: `protokol_weryfikacji_v2.md` K‑01…K‑60, `recenzja/sprawdz_*.py`, `recenzja_koncowa/trzecie_oko.py`. Plan `plan_ramki_v2.md` (sekcja 3, 13 rejestr R1–R52, 14 zmiany). 31.10: korpus W+P i blat NIE zamówione (D‑3) → poprawki tanie. Znaleziska audytu: `sesje_2026-10-31/*/znaleziska.md`; decyzje: `sesje_2026-10-31/decyzje_wlasciciela_2026-10-31.md`. Zasada: zero tolerancji błędów geometrii — po zmianie pełna ponowna weryfikacja wszystkich plików z siatek.

## Prompt
Zadanie: wprowadź POPRAWKI PASOWAŃ jako R53, wygeneruj nowe STL i w pełni je zweryfikuj. Zakres = tylko luzy/tolerancje (bez przeprojektowania: bez magnesów zamiast zatrzasków, bez jednej bryły).

Krok 0 — przeczytaj: `00_NADZOR_STAN.md`, `plan_ramki_v2.md` sekcje 3/13/14, `parametry.json`, `protokol_weryfikacji_v2.md`, `wyniki_v2/README.md`, `wyniki_v2/raport/notatki_wykonawcy.md`, `prompt_wykonawca.md`; znaleziska: `sesje_2026-10-31/design_a_korpus/znaleziska.md` 1.2 (T1–T15: T1 `blat_skirt_clearance` 0,5→0,7; T2 zahaczenie haczyka 0,8 / dno kieszeni; T3 luz Z haczyka 0,25/0,3 → szczelina blat–korpus; T4 wkręty tylne ø3,2→ø3,6 lub rowek), `sesje_2026-10-31/wykonalnosc/znaleziska.md` W‑04 (MJF ±0,3 %, HP Z ±0,42–0,60; płytka 0,3 w 96,6; kołek ø3/3,3), `sesje_2026-10-31/design_b_plytki/znaleziska.md` §3.3 (interfejs płytka↔wkładka: 96,6 zostaje przy MJF), `sesje_2026-10-31/kod_b_generator/znaleziska.md` (G‑02 `wyczysc_wyniki` kasuje STL; G‑04/G‑05 sprawdzenia liczą oczekiwane z tego samego `P`; S‑06…S‑09 trzecie oko bez znaku luzu; S‑02 G4b na starej tulejce).

Krok 1 — KOPIA: `wyniki_v2/` → `archiwum/wyniki_v2_przed_R53_2026-10-31/`, `parametry.json` → `archiwum/parametry_przed_R53_2026-10-31.json`. Niczego nie usuwaj.

Krok 2 — projekt R53: dla T1–T15 i W‑04 nowa wartość luzu z uzasadnieniem (luz nominalny ≥ suma tolerancji obu części w danym kierunku; wcisk tylko jawnie — tulejka DC). Nie zmieniaj wysokości 63,6/59,6/50, położenia Pi, interfejsu z płytką poza luzem. Tabela (klucz, stara, nowa, uzasadnienie, K‑xx) → `sesje_2026-10-31/poprawki_pasowan/R53_projekt.md` + wpis R53 w `plan_ramki_v2.md` sekcje 13/14 stylem R50–R52. Nowe klucze do `parametry.json` z opisem; zmiany kodu generatora minimalne z `# R53`.

Krok 3 — generacja: sprawdź Blender (`where blender`, `C:\Program Files\Blender Foundation\`); etap B → C → SPRAWDZ wg `prompt_wykonawca.md`/`wyniki_v2/README.md`. Brak Blendera → stop po kroku 2, w handoucie komenda i status „CZEKA NA BLENDER”.

Krok 4 — pełna weryfikacja: wszystkie `recenzja/sprawdz_*.py`, `recenzja_koncowa/trzecie_oko.py` na 17 STL (z tulejką 11,85 i podkładkami); własny skrypt trimesh: każde pasowanie T1–T15 ZE ZNAKIEM luzu vs R53 i `wyniki_v2/arkusze/arkusz_wymiarow.md`; części poza R53 identyczne z kopią (lista różnic per plik). Wynik `weryfikacja_R53.md` (pasowanie, przed, po, zmierzone, status). Zaktualizuj `wyniki_v2/arkusze/*`, `wyniki_v2/README.md`. Każdy NIE → popraw i powtórz.

Pliki własne: `sesje_2026-10-31/poprawki_pasowan/` (`handout.md` aktualizowany po każdym kroku, `R53_projekt.md`, `weryfikacja_R53.md`, skrypty). Dozwolone poza nim: `parametry.json`, `plan_ramki_v2.md` 13/14, `protokol_weryfikacji_v2.md` (tylko nowa sonda), `ramka_generator.py` (minimalnie), `wyniki_v2/` (po kopii). NIE dotykaj `stanowisko/`, PDF/MD planu wdrożenia i zakupów, Google Drive; niczego nie usuwaj. Done = handout „ZAKOŃCZONE” (lub „CZEKA NA BLENDER”), weryfikacja 0 NIE, na górze 3 linie: co zmieniono, czy STL gotowe do zamówienia, co zostało.
