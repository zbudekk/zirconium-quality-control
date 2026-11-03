# Handout — sesja DOKUMENTY R53 (31.10.2026)

**STATUS: ZAKOŃCZONE.** Dokumenty projektu nanoszą R53, pakiet `Ramki_pakiet_2026-10-31_R53` gotowy do wgrania (z modelem 3D), nic nie wgrano, nic nie zamówiono, nic nie usunięto.

1. **Co zmieniono:** plan budowy ramek v2 (tabela 3 + opisy 4.x, D5/D9/D12, sekcje 7 i 9 — 60 zastąpień „[cytat usuniety]”, 12 odstępstw „[cytat usuniety]” zamknięte, 0 rozbieżności tabela 3 ↔ `parametry.json`), plan wdrożenia v2 (+PDF, 34 strony), Zakupy i druk (+PDF, 11 stron: specyfikacja zamówienia z SHA‑256, kryterium odbioru > ±0,5 = reklamacja, przewiercanie ø2,1/ø2,5, tulejka po pomiarze otworu, decyzje do wiadomości właściciela), R50 (dopisek sekcja 7).
2. **Pakiet:** `Ramki_pakiet/` (przebudowany) i `Ramki_do_wgrania/Ramki_pakiet_2026-10-31_R53/` (identyczne, 40 plików, 36 MB) + ZIP (16,3 MB) + `SHA256SUMS_2026-10-31_R53.txt` + nowa instrukcja `INSTRUKCJA_DLA_SESJI_WGRYWAJACEJ_2026-10-31_R53.md` z gotowym promptem. Folder 04 ma `ramka_3d_v3_R53.html` i `animacja_ramki_R53.html` z sesji modelu (SHA zgodne z jej handoutem).
3. **Co zostało (właściciel):** wgranie pakietu na serwer (prompt w instrukcji), zamówienie w drukarni według specyfikacji R53, zapytanie o pole skanowania. Stare pakiety `Ramki_pakiet_2026-10-27*` nietknięte.

## Zamknięte odstępstwa „tabela 3 planu” (raporty B/C/SPRAWDZ iter5, 12 pozycji)

| # | Klucz | Tabela 3 było | Jest (= `parametry.json`) | Gdzie w planie |
|---|---|---|---|---|
| 1 | `panel_slot_w` | 3,4 | 3,6 | 3.2 |
| 2 | `panel_screw_hole_d` | 3,4 | 3,6 | 3.3 |
| 3 | `snap_pocket_w` | 10 | 11 | 3.3 |
| 4 | `snap_pocket_h` | 2,5 | 3,5 | 3.3 |
| 5 | `snap_pocket_depth` | 1,0 | 1,3 | 3.3 |
| 6 | `snap_pocket_z` | 52,6 | 52,1 (korpus_h − 7,5) | 3.3 |
| 7 | `blat_skirt_clearance` | 0,5 | 0,7 | 3.4 |
| 8 | `snap_hook_h` | 1,3 | 1,5 | 3.4 |
| 9 | `insert_opening` | 96,6 | 96,8 | 3.4 |
| 10 | `orient_post_gap` | 0,5 | 0,6 | 3.4 |
| 11 | `blat_pin_hole_d` | 3,3 | 3,4 | 3.4 |
| 12 | `dc_bush_outer_d` | 12 | 11,85 (R52; tabela była nieuzgodniona od 27.10) | 3.5 |

Dodane wiersze tabeli 3 (klucze istniały tylko w JSON): `blat_screw_hole_d` 3,6 (3.3), `tab_root_x_out` 52,4 (3.4). Opisy uzgodnione dodatkowo: `blat_post_hole_depth` (lico 96,8 → 90,8, dno 1,6), `wire_rabbet_w` (52,4 → 49,9). Kontrola tą samą logiką co `porownaj_plan_z_json` w generatorze: **0 rozbieżności, 0 brakujących kluczy** (generator nie był uruchamiany — `wyniki_v2/` nietknięte; przy następnym `--etap SPRAWDZ` rejestr odstępstw „tabela 3 planu” powinien być pusty).

Opisy 4.x i pozostałe miejsca: 4.1 (luz 0,4), 4.3 (rowek 3,6, otwory ø3,6, kieszenie 11 × 3,5 × 1,3 na Z 52,1…55,6, ściana 1,2), 4.4 (kołnierz 193,6 / 0,7, R 4,3, haczyk 1,5, luz Z 0,75, słupek 96,8 → 90,8, dno 1,6, gwint 4,8, otwory ø3,4, rama 104,8, margines 27,6), 4.5 (wylot 0,7), 4.6 (104,8 / 148,4, otwór 96,8, 52,4/49,9/48,4, kołek 0,6, uszy 43,6, zakładka 8,4 × 3,6, rachunek 0,4), 4.9 (tulejka celowo wciskowa, druk po pomiarze), 4.11 (haczyki, nasada, płytka, wkładka w oknie, margines, ścianki 1,2 i 1,6, luzy, gwinty + przewiercanie, kanały, wentylacja 560 mm², kieszeń DC, kieszeń a napis 44,5…55,5 / 1,8), D5, D9, D12, sekcja 7 (rowek 3,6, słupki 96,8, kieszenie 11 × 3,5 × 1,3, luz 0,7), sekcja 9 (krok 6 pomiar/±0,5, krok 7 przewiercanie, krok 12 tulejka po pomiarze). Każda liczba sprawdzona z `parametry.json` (13 kluczy R53) i `weryfikacja_R53.md` (tabela 3: 118/118).

## Zmienione pliki projektu (kopie sprzed zmian w `archiwum/*_przed_dokumenty_R53_2026-10-31.*`)

| Plik | SHA‑256 po zmianie | Zmiana |
|---|---|---|
| `plan_ramki_v2.md` | `a63c964468e3c03dd4df4ee0a3a41dfbaf7fe49ae495c38b71627c46162c94bb` | tabela 3, 4.x, D5/D9/D12, sekcje 7 i 9; 56 znaczników „[R53” |
| `Stanowisko kontroli cyrkonii — plan wdrozenia v2.md` | `77cd30a9ef9e49f5b9d9bdd16683d10c6ba3ffdb06d5a7d95116fa608ac681ee` | nagłówek, wiersz R53 w „Co się zmieniło”, kroki 6/7/12 montażu, narzędzia (wiertła ø2,1/ø2,5), ryzyko tolerancji, decyzja otwarta 6, słowniczek (tulejka) |
| `Stanowisko kontroli cyrkonii — plan wdrozenia v2.pdf` | `7f586d6a412ef83de031ca8df1e25252d47bed0a6cadafa78f9ee76a3533e03b` | `py -3.14 narzedzia/buduj_plan_wdrozenia.py`, 34 strony |
| `Zakupy i druk — stanowisko kontroli cyrkonii.md` | `859b78c9d790a5ddbcf7c2fd4ed222f18809c026c7df7195696a8577212f01ae` | wersja 1.1: streszczenie, harmonogram (D‑3), objętości R53, **Specyfikacja zamówienia (15 STL, SHA‑256, szt., materiał)**, wymagania dla drukarni (tolerancja obu części, płaskość T9, otwory T8), tulejka po pomiarze (T7), checklista odbioru (±0,5 = reklamacja; nowe wiersze: otwory wkrętów ø3,6, kieszenie zatrzasków, przewiercanie, rama wkładki), **Decyzje do wiadomości właściciela**, tabela spójności |
| `Zakupy i druk — stanowisko kontroli cyrkonii.pdf` | `1322a726fd235d026a6fc9fafe55d27424ac4d40e411cfe4956fba263309b959` | `--md "Zakupy i druk — …md"`, 11 stron |
| `R50_wdrozenie_zmiany.md` | `52ea487de92d66e205d1edab6944bb945f3d8e9a7a1274b7845892bf8672e803` | sekcja 7: tabela „było R50 → jest R53” |
| `narzedzia/buduj_plan_wdrozenia.py` | — | tylko metadane strony tytułowej (data/wersja z dopiskiem R53) |
| `narzedzia/zbuduj_pakiet_R53.sh` | — | NOWY: buduje pakiet R53 (dokumenty `_R53`, STL z `wyniki_v2/`, model i animacja z `wyniki_model_R53/` jeśli istnieją; nie buduje modelu) |
| `Ramki_pakiet/` | — | przebudowany (kopia sprzed: `archiwum/Ramki_pakiet_przed_dokumenty_R53_2026-10-31/`) |

Nie zmieniono: `parametry.json` (SHA `f57f1d084bc1…`), `ramka_generator.py`, `wyniki_v2/`, `ramka_3d*.html`, `protokol_weryfikacji_v2.md`, `narzedzia/zbuduj_pakiet.sh`, `Ramki_pakiet_2026-10-27*`.

## Pakiet `Ramki_do_wgrania/`

| Plik | SHA‑256 |
|---|---|
| `Ramki_pakiet_2026-10-31_R53.zip` (16 310 034 B, 40 plików, test ZIP OK) | `c32bd84f2725886bf1b60535d4cf0a5faf2eb857caa36c85f08790b213e3f8a4` |
| `SHA256SUMS_2026-10-31_R53.txt` (40 wierszy; sprawdzone na obu pakietach: 0 niezgodnych) | `1ea5afadbb482eb5177debd8792687ee6b2143f6fb7e3e265fcd02758e945b0e` |
| `INSTRUKCJA_DLA_SESJI_WGRYWAJACEJ_2026-10-31_R53.md` | `a5685303440632ceb1e2cea58096d9c371ce61960244aaab8bf3c3645f06b5c6` |

STL w pakiecie (SHA jak `wyniki_v2/README.md` i `weryfikacja_R53.md`): blat `8c48856eb9ad…`, korpus W `bd55871c88cf…`, korpus P `aadb91c9364c…`, wkładka `f4196fbc6404…` (nowe); płytki n1–n6, pokrywka, tulejka, podkładki — identyczne z 27.10. Model `04_Model_i_animacje/ramka_3d_v3_R53.html` `4c710ea80b4d…` (7,0 MB), `animacja_ramki_R53.html` `ab208401e302…` — zgodne z `wyniki_model_R53/handout.md`; stara `animacja_ramki_v2.html` zostawiona tylko historycznie (README mówi, że sprzed R50).

Zawartość: 01 — 7 dokumentów (plan wdrożenia MD+PDF, Zakupy MD+PDF, plan budowy, projekt R53, weryfikacja R53); 02 — 10 STL + arkusz zamówienia CSV/MD; 03 — pokrywka, tulejka, 3 podkładki, płytka n1 do testu skanera; 04 — model R53, animacja R53, animacja stara, 3 rendery; 05 — parametry.json, protokół, generator, `.blend`, README wyników, arkusz wymiarów, kody płytek, raport SPRAWDZ iter5.

## Uwagi

- Odstępstwo #12 (`dc_bush_outer_d` 12 w tabeli 3) było nieuzgodnione od R52 (27.10), nie od R53 — teraz tabela mówi 11,85 z adnotacją.
- Kopie sprzed zmian zgodnie z zasadą sesji (użyty dopisek: `_przed_dokumenty_R53_2026-10-31`): wszystkie 7 plików + folder pakietu + skrypt PDF skopiowane do `archiwum/` przed zmianą.
- Pakiet zbudowany dwa razy (drugi raz po dodaniu `animacja_ramki_R53.html`); folder `Ramki_pakiet_2026-10-31_R53` i ZIP z pierwszego przebiegu zastąpione własnym drugim przebiegiem tej sesji (nic starszego nie ruszono).
