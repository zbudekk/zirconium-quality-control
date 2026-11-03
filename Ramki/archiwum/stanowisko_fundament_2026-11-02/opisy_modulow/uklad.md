# uklad — układ płytki

**Co robi.** Wczytuje `modele_plytek/<nazwa>/uklad.json` (z projektu ramek v2, `wyniki_v2/json/`) do obiektów: gniazda (okrągłe stożkowe i rynienki), trzy znaczniki (stożkowe wgłębienia ø5 × 3 mm), wycięcie orientacyjne, dołki kodu, numery dostępnych płytek i ich STL. Jedno źródło geometrii płytki dla synth, plate, indicate i ui — zmiana układu gniazd nie wymaga zmiany kodu.

**Wejście.** Nazwa `wieczorna` | `poranna`.

**Wyjście.** `UkladPlytki` z metodami: `gniazdo(id)`, `gniazda_okragle()`, `rynienki()`, `najblizsze_gniazdo(x, y)`, `plik_stl(numer)`, kod płytki ↔ bity (n = A + 2B + 4C).

**Kryterium „działa”.** `testy/test_uklad.py`: 18 + 2 i 31 + 2 gniazd [R54, 1.11.2026: gniazda i znaczniki w kole r 47 — `uklad.json` i STL skopiowane z `wyniki_v2` po R54], ścianki ≥ 3 mm, dno gniazda na z = 4, promień dolny z kąta 15°, pliki STL nr 1–3 i 4–6 istnieją.

**Uwaga o układzie.** JSON: początek w środku górnej powierzchni. STL: góra płytki na z = `Z_TOP` = 8. Znaczniki są wgłębieniami (z 5…8), nie wypustkami — plate dopasowuje stożek do wgłębienia.
