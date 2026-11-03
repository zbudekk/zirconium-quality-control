# Handout — DESIGN B: płytki n1–n6 (wymiary, design, zgodność ze skanerem, uproszczenia, premium)

Status: **ZAKOŃCZONE** (31.10.2026, 6/6 kamieni).

## Pliki (wszystkie w `sesje_2026-10-31/design_b_plytki/`)
- `znaleziska.md` — 5 wniosków na górze; Część 1 (rozbieżności z liczbami), Część 2 (tabela 12 propozycji A1–A12 z wpływem na program i wkładkę), Część 3 (tabela zlecić/samemu/materiał/wykończenie/koszt/czas/uzasadnienie + 9 wymagań interfejsu dla DESIGN A + kolejność działań)
- `pomiary_stl.md` — pomiary 8 STL płytek + wkładki; §2 obserwacje P‑1…P‑8; §3 luz koron w gniazdach; §4 interfejs wkładki
- `pomiary_stl.py`, `pomiary_stl.json` — skrypt (trimesh, `py -3.12`) i surowe liczby; uruchomienie z katalogu Ramki: `PYTHONUTF8=1 py -3.12 sesje_2026-10-31/design_b_plytki/pomiary_stl.py`
- `skaner_aidite.md` — co ustalono o A‑IS Pro 3 / DS‑EX Pro(H) ze źródłami (pole 100 × 100 × 75, multi‑die ≤ 8, stolik, optyka, materiały, eksport, ceny) + lista „nadal do potwierdzenia”

## Zakres
Wyłącznie płytki n1–n6, ich oznaczenia (stożki, dołki, cyfra, magnesy) i interfejs płytka↔wkładka (pomiar + wymagania). Korpus/blat/wkładka/pokrywka/elektronika = DESIGN A. Nie modyfikowano żadnego pliku projektu ani STL; nie dotykano Google Drive.

**Korekta 31.10: repo GitHub wycofane ze źródeł; źródła wyłącznie lokalne.** Żaden wniosek nie opierał się na repozytorium.

**Decyzja D‑2: płytki szare — uwzględniona** (`znaleziska.md` §3.1a: tabela zawężona do wariantów szarych, odcienie, mat, trwałość przy IPA, rekomendacja końcowa: Al 6061 piaskowane + anoda twarda grafit/ciemnoszara + grawer; budżet: MJF PA12 surowy średnioszary).

## Kamienie milowe
1. Lektura — `plan_ramki_v2.md` (1, D2–D12, 3.1, 3.4, 4.1, 4.6, 13), `parametry.json` (sekcja `plytka`, klucze zgodne z 3.1), arkusze, `raport_koncowy.md`, `uklad.json` ×2, `uklad.md`/`uklad.py`, notatki skanera, mail, plan wdrożenia (wybory, płytki, test, ryzyka, decyzje otwarte, zał. A), „Zakupy i druk”, handout KOD A.
2. Pomiary STL — wszystko = JSON = parametry co do ≤ 0,002 mm; siatki zamknięte; `modele_plytek/*.stl` bajtowo identyczne z `wyniki_v2/stl`. Obserwacje P‑1…P‑8 (faza zjada ściankę do 2,56; dołki z pionową ścianką; cień koron na stożki z marginesem < 10°; małe gniazda tylko dla siekaczy; brak adaptera stolika).
3. Skaner — agent sieciowy (84 odwołania): A‑IS Pro 3 ≈ DS‑EX Pro(H); pole 100 × 100 × 75 (OEM); stożki r 59,4 poza ø100; multi‑die ≤ 8 prac → skan jako model; brak danych o kącie kamer/przechyle; szary mat jedyna udokumentowana klasa „bez sprayu”; cena odpowiednika w PL 35–36 tys. zł brutto.
4. Część 2 — 12 propozycji; rekomendowane: A1 (jedna geometria + numer po obróbce, przy CNC), A2 (dołki sferyczne), A3 (czasze R3 zamiast stożków — mała zmiana `uklad.json` + plate), A5 (2 rozmiary gniazd, stożek 25°, głębokość 5 — po pomiarze 20 prac), A9 (adapter stolika), A11 (żywice standardowe odpadają na produkcję). Plan B pola: `plate_size` 90 lub A4.
5. Część 3 — rekomendacja: teraz płytka testowa z szarej matowej żywicy modelowej (samemu); po teście skanera próbka A (CNC Al 6061 piaskowane, anoda ciemnoszara mat, grawer) i B (MJF PA12 jasnoszary); seria 6 po porównaniu na skanerze (Al 3,5–7 tys. zł / MJF 0,9–1,8 tys. zł). Czarny mat ryzykowny, czarny połysk wykluczony, biały bez kontrastu dla oka.
6. Handout — ten plik.

## Dla sesji nadrzędnej / DESIGN A
- Interfejs wkładki: 9 wymagań w `znaleziska.md` §3.3 (otwór 96,6, kołek D 4,4, półki ≤ 13 × 13, Hall ≤ 4 mm, magnesy (±42, ±42), grubość 8, rowek pokrywki, rozdzielenie magnesów od znaczników przy A4, masa Al 160 g).
- Do maila Aidite: poprawić pyt. 5/14 (skan modelu, nie Multidie), dodać kąt kamer / wysokość nad stolikiem, obciążenie stolika, globalne wyłączenie „Fill holes”.
- Decyzje właściciela: (a) pomiar 20 prac → czy zmieniać rozkład gniazd (A5) przed drukiem testowym; (b) Al premium vs MJF; (c) czy wdrażać A2/A3 w programie przed testem.
