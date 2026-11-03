# Handout — model 3D po R53, 31.10.2026

**STATUS: GOTOWE.** Pliki do skopiowania do folderów `04_Model_i_animacje` pakietów:

| Plik | Rozmiar | SHA‑256 |
|---|---|---|
| `ramka_3d_v3_R53.html` | 6 979 692 B (7,0 MB) | `4c710ea80b4d8fc8e06333ebecae2e507217a4bfb6d57602a866498a02ae0f13` |
| `animacja_ramki_R53.html` | 21 070 B | `ab208401e30280f395d32978dee246e8e98798cf5112bf945868f47b80c22951` |

Oba działają po dwukliku z dysku, bez internetu.

## 1. Skąd model bierze STL

- Źródło UI: `ramka_3d.html` (nietknięty). Builder `narzedzia/zbuduj_model_offline.js` wkleja three.js r128 (`narzedzia/vendor_three_r128/`) i 7 STL z `wyniki_v2/stl/` jako base64.
- 7 STL: `ramka_korpus_W_v2`, `ramka_korpus_P_v2`, `ramka_blat_v2`, `ramka_wkladka_v2`, `ramka_plytka_wieczorna_n1_v2`, `ramka_plytka_poranna_n4_v2`, `ramka_pokrywka_v2`.
- Po R53 zmienione 4 z nich (korpus W, korpus P, blat, wkładka); 3 bajtowo jak przed R53.
- Dotychczasowa `ramka_3d_v3.html` w pakietach = builder(`ramka_3d.html`) ze STL sprzed R53 (sprawdzone: identyczna poza blokiem STL).

## 2. Co zmieniono

**Builder** (kopia przed zmianą: `archiwum/zbuduj_model_offline_przed_R53_2026-10-31.js`):

1. Parametry: model miał w środku własną kopię `parametry.json` sprzed R53 (i starą tulejkę DC 12 zamiast 11,85). Builder wstawia teraz aktualny `parametry.json`. Etykiety, bryły zastępcze i „Kontrola położenia STL” liczą się z wartości R53.
2. Etykiety z liczbami wpisanymi na sztywno:
   - kołnierz blatu: `194` → **193,6 (luz 0,7)**, linia na ±96,8;
   - kieszeń zatrzasku: `zatrzask Z 52,6…55,1` → **kieszeń zatrzasku 11 × 3,5 × 1,3, Z 52,1…55,6**;
   - obrys wkładki z uszami: `130 × 148,3` → **130 × 148,4**; otwór wkładki **96,8**, rama **104,8** (z parametrów);
   - opis wkładki: „Rama 104,6 × 6” → „Rama 104,8 × 6, otwór 96,8”;
   - opis dystansów: „rowki 3,4” → „rowki 3,6”;
   - nagłówek: „po R50 / iteracja B3” → „po R53, 31.10.2026”.
3. Usunięte odwołania do Google Fonts (CSS ma czcionki zastępcze). Stara v3 miała je w nagłówku, więc przy włączonym internecie pobierała czcionki.
4. Builder wypisuje SHA‑256 każdego STL i zapisuje je w pliku jako `window.STL_SHA256`.

**Animacja** (`animacja_ramki.html` = plik sprzed R50, bez STL, ale z wymiarami 54,6/58,6, kołnierzem 97,2, ramą 104,6) → nowy `animacja_ramki_R53.html`:

- łańcuch wysokości po R50/R53: korpus 59,6, panel Z 54, blat 63,6, płytka 74,1, pokrywka 90,1;
- przekrój: kołnierz 193,6, haczyk 96,8 → 98,3 w kieszeni 97,5…98,8 × Z 52,1…55,6, wkładka z otworem 96,8, dystanse 50 na stadionach Z 4, bez ramy dyfuzora i szczeliny SD;
- legenda montażu i scena 1 z tymi samymi liczbami; usunięte Google Fonts.
- Scena 2 (schemat podłączeń) bez zmian merytorycznych, tylko napis „200 × 200 × 63,6”.

## 3. Wyniki sprawdzeń (headless Chrome, plik otwarty z dysku `file:///`)

| Sprawdzenie | Wynik |
|---|---|
| „Kontrola położenia STL” — wersja W | 7 × ✓, Δ 0,000 każdy |
| „Kontrola położenia STL” — wersja P | 7 × ✓, Δ 0,000 każdy (widoczny korpus P) |
| Żądania sieciowe poza samym plikiem | 0 (model i animacja) |
| Błędy / ostrzeżenia w konsoli | 0 (model i animacja) |
| SHA‑256 STL w HTML vs `wyniki_v2/stl/` | 7/7 zgodnych (liczone w przeglądarce i osobno w Node) |
| Łańcuch wysokości vs K‑54 | zgodny (brak ostrzeżenia) |
| Obrys wkładki w scenie | X −65…65, Y −52,4…96 (148,4), Z 60,1…71,1 = tabela 1 po R53 |

Wbudowane STL:

| STL | SHA‑256 | R53 |
|---|---|---|
| ramka_korpus_W_v2 | `bd55871c88cf2604c1c8efa5035148ba39c3803a0788015cc35548e8e9afff9a` | nowy |
| ramka_korpus_P_v2 | `aadb91c9364cf39f1f4062d328616aa518e474b957315ed4a941de4f935ab2b7` | nowy |
| ramka_blat_v2 | `8c48856eb9addee2b37cfa5a03e5686ab7670bd92b724e488ccc8d8dd3a4b418` | nowy |
| ramka_wkladka_v2 | `f4196fbc640450998634f50caa86051f89df2cbb2c218e317f5c2b193e3ef92b` | nowy |
| ramka_plytka_wieczorna_n1_v2 | `b2803c829885795b7a06e9d2597a1de6080bdec459e426238d8cd9c05a6e8b52` | bez zmian |
| ramka_plytka_poranna_n4_v2 | `3186d1ab86f2442302edf057d8bbbc227bbf7f691d4620304f79b377e6773089` | bez zmian |
| ramka_pokrywka_v2 | `ad23444483ac95733e92169af00e5271d8fc3b19a91854e8c8acddf06c8cd454` | bez zmian |

Zrzuty w tym folderze: `ramka_3d_v3_R53_W.png`, `ramka_3d_v3_R53_P.png`, `ramka_3d_v3_R53_wymiary_blat.png` (kołnierz 193,6, kieszeń zatrzasku), `ramka_3d_v3_R53_wymiary_wkl.png` (96,8, 104,8, 148,4), `animacja_ramki_R53_scena1.png`, `animacja_ramki_R53_scena3.png`.

Uwaga: panel przeglądarki aplikacji nie otwiera `file://`, dlatego test zrobiono w Chrome headless przez DevTools Protocol (skrypt testowy w katalogu roboczym sesji, nie w projekcie).

## 4. Dla sesji pakietu (ramki-dokumenty-r53)

- Skopiować oba pliki HTML do `04_Model_i_animacje/` nowego pakietu (nazwy wg uznania, np. bez `_R53`).
- `INSTRUKCJA_DLA_SESJI_WGRYWAJACEJ.md`, sekcja „Model 3D”: rozmiar 6,9 MB → 7,0 MB, dopisać „STL po R53”.
- Przebudowa w przyszłości: `node narzedzia/zbuduj_model_offline.js <wyjście.html>` (bierze aktualne `parametry.json` i `wyniki_v2/stl/`).

Nie zmieniono: `ramka_3d.html`, `parametry.json`, `ramka_generator.py`, `wyniki_v2/`, plan, zakupy, `Ramki_pakiet*`, `Ramki_do_wgrania`. Nic nie usunięto ani nie wgrano.
