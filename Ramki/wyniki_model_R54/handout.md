# Handout — model 3D po R54, 1.11.2026

**STATUS: GOTOWE.** Model online opublikowany jako nowa wersja tego samego artefaktu: https://claude.ai/artifact/N1W9QKGcXq87t3GPhFp5Sf (wersja 8; wersja 7 = to samo bez `<meta charset>`). Kopia offline w tym folderze.

| Plik | Rozmiar | SHA‑256 |
|---|---|---|
| `ramka_3d_v3_R54.html` | 6 594 208 B (6,6 MB) | `0be7676472351be7b42558967121500e989a85904ad8f8ae92555448b00706ca` |
| `animacja_ramki_R53.html` (bez zmian — nie pokazuje układu gniazd, tylko schemat) | 21 070 B | `ab208401e30280f395d32978dee246e8e98798cf5112bf945868f47b80c22951` |

## 1. Co zmieniono w `ramka_3d.html` (źródło UI; kopia sprzed: `archiwum/ramka_3d_przed_R54_dokumenty_2026-11-01.html`)

1. Blok `params` = aktualny `parametry.json` (R54: `ev_rows` 5 rzędów, `mo_rows` 7, `ev_/mo_marker_pos`, `scan_field_d`, `socket_zone_r` 47). Dotąd online był `parametry.json` sprzed R53.
2. Nagłówek: „model 3D v3 (po R54, 1.11.2026)”, podtytuł „płytki po R54: gniazda i znaczniki w kole r 47; korpus, blat, wkładka po R53”; `<meta charset="utf-8">` (plik z dysku pokazywał krzaczki przy serwowaniu bez nagłówka kodowania).
3. Etykiety R53, które builder poprawiał tylko w kopii offline, przeniesione do źródła (kołnierz 193,6 / luz 0,7, kieszeń zatrzasku 11 × 3,5 × 1,3 Z 52,1…55,6, obrys wkładki 130 × 148,4, rowki 3,6, rama 104,8 / otwór 96,8).
4. Świecenie diod pod gniazdami płytki W: indeksy rzędów dopasowane do nowego `ev_rows` (0 = rynienka przednia, 1 = ø12 ×6, 2 = ø9 ×7, 3 = ø15 ×5, 4 = rynienka tylna).
5. Pomiar #12 (nota i formularz): „średnica koła widocznego w całym obrocie (makieta 96 × 96 z okręgami ø90/94/100)”, parametr `scan_field_d` (DO_ZMIERZENIA, domyślnie 100), kryterium ≥ 100 → bez zmian; < 100 → przeliczyć D6; < ~94 → płytka okrągła.
6. Nowa grupa w zakładce „Wymiary”: **Płytka: koło gniazd i znaczniki (R54)** — pierścień r 47 na wierzchu płytki, 6 stożków znaczników (W A/B/C, P A/B/C) z `*_marker_pos`, kieszeń magnesu A (−42; −42). 8 etykiet (limit grupy).
7. Opis części „Płytka”: 18 + 2 / 31 + 2 w kole r 47, kieszenie magnesów w rogach.

**Builder** `narzedzia/zbuduj_model_offline.js` (kopia sprzed: `archiwum/zbuduj_model_offline_przed_R54_dokumenty_2026-11-01.js`): usunięte podmiany etykiet R53 (są w źródle), kontrola „ramka_3d.html musi być po R54”, reszta jak R53 (parametry, bez Google Fonts, three.js r128 + 7 STL base64).

**Artefakt online:** strona = `ramka_3d.html`; 7 plików `stl/*.stl` wgrane ponownie jako ASCII STL (text/plain) z aktualnych `wyniki_v2/stl/` — poprzednia wersja online (6, 27.10) miała STL sprzed R53 (korpusy, blat, wkładka) i sprzed R54 (płytki).

## 2. Wyniki sprawdzeń (kopia offline przez `http://127.0.0.1` w przeglądarce aplikacji; `file://` panel nie otwiera)

| Sprawdzenie | Wynik |
|---|---|
| „Kontrola położenia STL” W + P | 7 × ✓, Δ 0,000 każdy |
| Żądania sieciowe poza samym plikiem | 0 |
| Błędy w konsoli | 0 |
| Składnia bloków `<script>` (Node `new Function`) | OK (źródło 1 blok, offline 5) |
| SHA‑256 STL w HTML vs `wyniki_v2/stl/` | 7/7 = `wyniki_v2/README.md` |
| Tryb „Zmierz” | 15 pozycji, #10 sprawdzony (zrzut), formularz 16 wierszy z #12 → `scan_field_d` 100 |
| Grupy wymiarów | gab 7, zdol 8, zgora 8, tyl 7, panel 8, blat 7, wkl 8, kolo 8 (≤ 8) |
| Łańcuch wysokości vs K‑54 | bez ostrzeżenia |

Wbudowane STL (SHA‑256): korpus W `bd55871c…`, korpus P `aadb91c9…`, blat `8c48856e…`, wkładka `f4196fbc…` (R53, bez zmian); **płytka wieczorna n1 `515d32d3…`, poranna n4 `a8d07cbe…` (NOWE R54)**; pokrywka `ad234444…`.

Zrzuty: `ramka_3d_v3_R54_W_kolo_gniazd.jpg` (wieczorna 18 + 2, pierścień r 47, znaczniki), `ramka_3d_v3_R54_P_kolo_gniazd.jpg` (poranna 31 + 2, rzędy ø7,5 w szachownicę), `ramka_3d_v3_R54_zmierz_10.jpg` (tryb Zmierz).

Nie obejrzano: strony online pod adresem artefaktu (panel przeglądarki niezalogowany — jak przy R53); treść strony jest identyczna z kopią offline poza osadzeniem bibliotek i STL.

## 3. Przebudowa w przyszłości

```
node narzedzia/zbuduj_model_offline.js wyniki_model_R54/ramka_3d_v3_R54.html
```
(bierze aktualne `parametry.json` i `wyniki_v2/stl/`; online: Artifact tool, ten sam URL, strona `ramka_3d.html` + `stl/*.stl` jako ASCII).
