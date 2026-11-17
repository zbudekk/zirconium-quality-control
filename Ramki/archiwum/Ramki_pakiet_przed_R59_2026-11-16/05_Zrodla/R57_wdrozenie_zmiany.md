# R57 — płytka okrągła do testu skanera (lista edycji w źródle prawdy)

Data: 2026‑11‑02. Decyzja właściciela 2.11: jutro zamówienie płytek OKRĄGŁYCH (wieczorna + poranna) jako drugiego wariantu do testu skanera. Założenia nadzoru: `plan_sesji_testowych_programu_2026-11-02.md` sekcje 0 i 2 oraz zadanie sesji R57‑A.
Zakres edycji (sesja R57‑A, wykonawca): `ramka_generator.py`, `parametry.json`, `plan_ramki_v2.md`, `protokol_weryfikacji_v2.md`, `00_NADZOR_STAN.md`, `wyniki_v2/` (4 STL + 2 JSON + raport), ten plik.
NIE dotknięto: `Ramki_pakiet/`, Google Drive, `stanowisko/`, dokumentów PDF, modelu 3D/animacji, `narzedzia/`. Kopie sprzed edycji: `archiwum/*_przed_R57_2026-11-02.*`, `archiwum/wyniki_v2_przed_R57_2026-11-02/` (stl + json), `archiwum/sha256_stl_przed_R57_2026-11-02.txt`.

## 0. Wynik

4 STL + 2 JSON w `wyniki_v2/`; `--etap ALL --iter 2 --raport R57` i `--etap SPRAWDZ --iter 8`: B 0 / P 0 / D 0; 15 plików STL z `Ramki_pakiet/SHA256SUMS_2026-11-01_R56.txt` bajtowo identyczne (wkładka przywrócona z archiwum po znanej różnicy znaku zera normalnych). Raport: `wyniki_v2/raport/raport_wykonawcy_R57_iter2.md` (sekcja 7 = uzupełnienie wykonawcy, SHA, założenia).

| Plik | SHA‑256 | Objętość [cm³] |
|---|---|---|
| `ramka_plytka_okragla_wieczorna_v2.stl` (bazowy) | 3ca8178262f7f1f253480ca1d49adbbccf2db3648647814ec2390311e5553ace | 48,99 |
| `ramka_plytka_okragla_wieczorna_n8_v2.stl` (zamówienie) | c4c8a18d0b83fd2a2903f5d782188a8de4827ee07c55dca9df7bd0d8e4a37d32 | 49,01 |
| `ramka_plytka_okragla_poranna_v2.stl` (bazowy) | 713aef6c0cef1dc2fc3b3809ce3756557b41b0cc4268c85166e985f18f74e0dd | 50,55 |
| `ramka_plytka_okragla_poranna_n9_v2.stl` (zamówienie) | a87bc6c5f8f0323bc202e5ebfeab6be6d7c8432beba6aafe4a8372d70666e2be | 50,56 |
| `uklad_gniazd_okragla_wieczorna.json` | 260f807c630211dcd3c1b552cded03838d1367156c856fc51f3a3f7ec12f0743 | — |
| `uklad_gniazd_okragla_poranna.json` | 5adcc977dd9b456e5261d1e2225bc386def23a165d79de124b5733fb9ef43d53 | — |

Stan końcowy (iteracja 2, 17:10, po decyzjach nadzoru ø100 / cięciwa 16): `raport_wykonawcy_R57_iter2.md`, `raport_wykonawcy_SPRAWDZ_iter8.md`. Iteracja 1 (ø98, cięciwa 8; SHA d97a67ec…/f8eb9b2f…/eba3279a…/a3ece3ba…) zastąpiona.

## 1. Założenia zadania a wykonanie — decyzje nadzoru 2.11 (ZATWIERDZONE przez właściciela 2.11.2026 po recenzji R57‑B)

| # | Założenie zadania | Wykonanie (decyzja nadzoru 2.11) | Powód |
|---|---|---|---|
| 1 | `plate_round_d` 96 | **100** (= granica pola skanowania; gniazda jak R54 w kole 47) | przy 96 ścianka obrysu rynienki tylnej porannej (r 46,93) i stożków (44,43 + 2,5) do ściany pionowej 1,07, do początku fazy 0,57 (< 1,5, zasada 4.8, K‑16); wykonawca proponował 98 (2,07); nadzór: 100 — ścianka do krawędzi 2,57 (poranna rynienka) / 3,07 (poranna stożki) / 3,61 / 3,20 (wieczorna); kwadrat ma rogi na promieniu 67,9, więc ø100 mieści się w skanerze wszędzie tam, gdzie kwadrat |
| 2 | `round_flat_w` 8 (cięciwa ścięcia na −45°) | **16** (głębokość 0,644 ≥ `round_flat_depth_min` 0,6) | 8 dawało głębokość 0,16 < faza 0,5 i tolerancja ±0,3 (niewidoczne); warunek nadzoru: ścianka od płaszczyzny ścięcia do każdego obrysu gniazda, rynienki, dołka i stożka ≥ 3 → wieczorna 3,68 (koniec rynienki przedniej), poranna 4,87 (dołek A) ✓ (przy ø98 wychodziło 2,66 — za mało); 20 odpada (ścianka 1,3); K‑61 (e), (f) |
| 3 | dołki A/B/C/D „wzdłuż lewej krawędzi”, promień ≤ 44, ≥ 3 od gniazd, ≥ 1,5 od stożków | per typ (zaakceptowane przez nadzór): wieczorna y −43,5, x −4,5/−1,5/1,5/4,5 (przód‑środek; promień 43,73, do rynienki 3,50, do stożków 31,9, do krawędzi 5,27); poranna x 30,5, y −31/−28/−25/−22 (przód‑prawo; promień 43,49, do gniazd 3,62, do stożków 51,0, do krawędzi 4,87) | przegląd siatki 0,5 mm: żadna linia 4 dołków o rozstawie 3 nie mieści się w kole r 44 wspólnie dla obu układów; lewa krawędź zajęta przez gniazda do x −45; wybrane miejsca mają największy zapas |
| 4 | cyfra w kole albo pominięta | w kole 47 (zaakceptowane): wieczorna (35, −26,5), poranna (36,5, −24,5) | wolne miejsce z zapasem ≥ 3,0 od gniazd, ≥ 3,2 od dołków, 2,8 / 3,2 od płaszczyzny ścięcia, obrys cyfry w promieniu ≤ 46,9; `null` = bez cyfry |
| 5 | `code_bit_d_pos` (−45, −27), pliki kwadratowe bajtowo identyczne | (−45, −27); n1–n6 identyczne; **pliki bazowe kwadratowe** (`_wieczorna_v2`, `_poranna_v2`, nie w pakiecie) dostały dołek D i zmieniły bajty | zasada „bazowy = wszystkie dołki” (4.1 p. 5, K‑11) rozszerzona o D; alternatywa: bazowe bez D |
| 6 | n8 = D, n9 = A + D | tak (`plate_numbers_round`) | — |
| 7 | bez kieszeni magnesów, bez rowka, spód płaski | tak (K‑63) | — |

## 2. `parametry.json` — klucze NOWE (8), sekcja `plytka` (walidator R14 rozszerzony)

| Klucz | Wartość | Status | Opis |
|---|---|---|---|
| code_bit_d_pos | [−45.0, −27] | ZALOZENIE | 4. bit D na kwadracie (w linii dołków); n1–n6 bez D |
| plate_round_d | 100 | ZALOZENIE | średnica płytki okrągłej = granica pola skanowania (zadanie 96 → nadzór 100, #1) |
| round_flat_w | 16 | ZALOZENIE | cięciwa ścięcia orientacyjnego (zadanie 8 → nadzór 16, #2) |
| round_flat_depth_min | 0.6 | ZALOZENIE | najmniejsza głębokość ścięcia (K‑61 e) |
| round_flat_angle | −45 | ZALOZENIE | kierunek normalnej ścięcia od +X (przód‑prawo) |
| code_dimples_round | {wieczorna: {A…D}, poranna: {A…D}} | ZALOZENIE | dołki kodu okrągłych per typ |
| number_pos_round | {wieczorna: [35, −26.5], poranna: [36.5, −24.5]} | ZALOZENIE | cyfra okrągłych (null = bez cyfry) |
| plate_numbers_round | {wieczorna: [8], poranna: [9]} | ZALOZENIE | numery okrągłych |

Bez zmian: wszystkie dotychczasowe klucze i wartości (287 kluczy, parsuje; LICZONE zgodne).

## 3. `ramka_generator.py` — zmiany

1. `TYPY_PLYTEK` = wieczorna, poranna, okragla_wieczorna, okragla_poranna; `typ_bazowy`, `plytka_okragla`, `numery_plytek`, `sciecie_okraglej`, `dolki_kodu` (kwadrat: A/B/C + D z `code_bit_d_pos`; okrągła: `code_dimples_round`), `BITY` = ABCD, `bity(n)` z bitem D (None = wszystkie), `bity_tekst`.
2. `uklad_pochodne`: `shape` square/round; okrągła: `d`, `size`, `flat` {corner, angle_deg, chord_w, dist}, `magnet_pockets: []`, bez `notch`, `number_relief` z `number_pos_round` (null → None); `wczytaj_uklad`: `coords.flat` zamiast `notch_corner`; `generuj_gniazda` z rzędów typu bazowego (układ nie jest przeliczany).
3. `zbuduj_plytke`: okrągła = walec ø`plate_round_d` z fazą (`bm_z_pierscieni`), ścięcie = półprzestrzeń za cięciwą obrócona o `round_flat_angle`; bez wycięcia D, kieszeni, rowka; cyfra tylko gdy `number_relief` nie jest None. Otwory ø3 okrągłych cięte w drugiej różnicy (`zbuduj_z_operacji(..., tnace_po=)`): jedna różnica zostawiała w bazowej wieczornej 3 zbędne ściany na dnie otworów (K‑03: 514 przecięć). Po booleanie `triangulacja_cdt(ob)`: ściany poziome (|n_z| > 0,999) odbudowane z pętli brzegowych triangulacją Delaunaya z ograniczeniami (tryb 1 + reguła parzystości dla otworów), kontrola liczby wierzchołków i pola. Kwadratowe: ta sama kolejność brył i triangulacja co dotąd (SHA R56 bez zmian).
4. `etap_A`: pętle po `TYPY_PLYTEK`; `ogolne_stl` z gabarytem ø dla okrągłych; `sprawdz_uklad_json(..., wzorzec=JSON kwadratu)` (K‑05 h); `sprawdz_plytke`: K‑10/K‑12/K‑14/K‑15 tylko kwadrat, K‑09 bez kontroli odwrotnej rogów na okrągłych, K‑11 4 bity, K‑13 obszar z JSON (null → max Z całej płytki), K‑08 sonda końca rynienki na 45° (okrągłe); nowe `sprawdz_okragla` (K‑61 a–f: obrys, ścięcie, faza, bbox, głębokość ścięcia ≥ `round_flat_depth_min`, ścianka ścięcie–obrysy ≥ `socket_wall_min`; K‑62, K‑63); K‑13 z promieniami, gdy w obszarze cyfry nie ma wierzchołka; `sprawdz_scianki_naroznikow` (K‑16): krawędź = okrąg + ścięcie, nowy wiersz gniazdo/rynienka–krawędź, bez kieszeni/rowka; `rzut_cyfry(nr)`.
5. `zapisz_kody_plytek`/`sprawdz_kody` (K‑58): 8 wierszy, bity A–D, okrągłe „brak kieszeni”; `lista_wymiarow`: wiersze n8/n9 (cięciwy zewnętrzne, grubość, grubość przy ścięciu, gniazdo, dołek, stożek A); `zapisz_arkusz_wymiarow` czyta 4 JSON; `RDZENIE_ETAPU['A']` i `etapy_istniejace` z okrągłymi (SPRAWDZ wymaga ich obecności); `k_raportu('A')` + K‑61…K‑63 (K‑60 sprawdza kompletność); `OBJ_ORIENT` 49/51; `odstepstwa_informacyjne_R57` (rejestr #1–#7); README: opis etapu A.
6. Walidator kluczy: + 8 kluczy. Bez zmian: wkładka, pokrywka, blat, korpus, tulejka, podkładki, arkusz zamówienia (okrągłe poza `quantities`; K‑57 nadal 15 wierszy).

## 4. `plan_ramki_v2.md` — edycje

| Miejsce | Zmiana |
|---|---|
| 1. Założenia: Z30 (nowe) | płytka okrągła ø100 (granica pola skanowania) jako drugi wariant do testu skanera; kod 4‑bitowy; bez wkładki/pokrywki do testu |
| D11 | n = A + 2B + 4C + 8D; bit D (−45, −27) na kwadracie; okrągłe n8 / n9; cyfra okrągłych `number_pos_round` |
| 3.1 | 8 nowych wierszy (code_bit_d_pos, plate_round_d, round_flat_w, round_flat_depth_min, round_flat_angle, code_dimples_round, number_pos_round, plate_numbers_round) |
| 4.1a (nowy) | pełna specyfikacja płytki okrągłej: gabaryt ø100 (decyzja nadzoru), cechy identyczne z kwadratem, ścięcie 16, dołki, cyfra, czego nie ma, JSON, sprawdzenia, wykonanie w generatorze |
| 4.11 | wiersz „Płytka okrągła (R57, Z30)” z liczbami ścianek przy ø100 (i odrzuconych ø96 / ø98) |
| 12.1 | p. 2 i 3: nowe JSON i STL |
| 13. Rejestr | wiersz R57 (po R56); nagłówek R1…R57; wstęp planu R1…R57 |
| 14. Zmiany | punkt 26 |

## 5. `protokol_weryfikacji_v2.md` — edycje

| Sprawdzenie | Zmiana |
|---|---|
| Tabela 1 | 2 wiersze: okrągła wieczorna (+ n8) 100 × 100 × 8 / 8,6, 49 [49,0]; okrągła poranna (+ n9), 51 [50,6] |
| §2 nagłówek | 21 plików (12 płytek) |
| K‑05 | (h) okrągłe: `sockets` identyczne z JSON kwadratu tego typu |
| K‑08 | okrągłe: sonda zaokrąglonego końca na 45° (narożnik prostokąta poza obrysem) |
| K‑09 | okrągłe: bez kontroli odwrotnej dawnych rogów |
| K‑10, K‑12, K‑14, K‑15 | tylko kwadratowe (okrągłe: K‑61 / K‑63) |
| K‑11 | 4 bity, pozycje z JSON, bazowy = wszystkie 4, n8 D, n9 A+D |
| K‑13 | okrągłe: obszar wokół `number_relief` z JSON; null → max Z całej płytki |
| K‑16 | okrągłe: krawędź = okrąg i ścięcie; gniazdo/rynienka–krawędź ≥ 1,5; liczby przy ø100 (i ø96 / ø98) |
| §3a (nowa) | opis płytki okrągłej + K‑61 (obrys ø100 ± 0,05 z sond promieniowych, ścięcie: położenie, głębokość ≥ 0,6, ścianka do obrysów ≥ 3, faza, bbox), K‑62 (dołki w polu, bity = numer), K‑63 (brak kieszeni/rowka, spód płaski) |
| K‑58 | 8 wierszy, bity A–D, okrągłe „brak kieszeni” |
| K‑59 | obejmuje pliki okrągłe; 15 plików R56 bajtowo bez zmian; wkładka — znak zera |

## 6. Pliki wynikowe i archiwum

- Nowe: `wyniki_v2/stl/ramka_plytka_okragla_{wieczorna,poranna}_v2.stl`, `…_okragla_wieczorna_n8_v2.stl`, `…_okragla_poranna_n9_v2.stl`; `wyniki_v2/json/uklad_gniazd_okragla_{wieczorna,poranna}.json`; `wyniki_v2/raport/raport_wykonawcy_R57_iter2.md` (iter1 = ø98, zastąpiony; + `raport_wykonawcy_SPRAWDZ_iter6/7/8.md`), `wyniki_v2/raport/sha256_stl_po_R57_iter2.txt`; rzuty cyfr n8/n9 w `wyniki_v2/raport/rzuty/`.
- Zmienione przez przebieg ALL (jak zawsze): `.blend`, rendery, arkusze (`kody_plytek.md` z n8/n9; `arkusz_wymiarow.md` z okrągłymi w §1–§2; `arkusz_zamowienia.*` bez zmian treści poza datą), README, `do_v3.md`; bazowe kwadratowe STL (dołek D). JSON kwadratowe: `shape`, dołek D.
- Bez zmian bajtowych: 15 plików R56 (n1–n6, korpusy, blat, wkładka, pokrywka, tulejka, podkładki).
- Archiwum: `archiwum/{ramka_generator,parametry,plan_ramki_v2,protokol_weryfikacji_v2}_przed_R57_2026-11-02.*`, `archiwum/wyniki_v2_przed_R57_2026-11-02/`, `archiwum/sha256_stl_przed_R57_2026-11-02.txt`, `archiwum/ramka_wkladka_v2_po_R57_iter1_znak_zera.stl`.

## 7. Co dalej (poza R57‑A)

1. Właściciel: zatwierdzić / cofnąć ZAŁOŻENIA #1–#5 z sekcji 1 (każde = jedna wartość w `parametry.json` + przebieg `--etap ALL`, ~40 s, + przywrócenie wkładki z archiwum).
2. R57‑B: recenzja z siatek (`recenzja/raport_recenzenta_R57_iter1.md`), w tym kontrola SHA 15 plików R56.
3. R57‑C: „Zakupy i druk” (wiersz płytek okrągłych: n8 49,01 cm³, n9 50,56 cm³, ø100 × 8, PA12 biały mat, ±0,3), plan wdrożenia (pomiar #12 + wariant okrągły), „Budowa ramki” (wkładka/pokrywka okrągła po teście), pakiet `Ramki_pakiet/` i Drive (tylko nowe pliki).
4. Program stanowiska: P1 (`shape` w `uklad.py`), P3 (foldery `modele_plytek/okragla_*`).
