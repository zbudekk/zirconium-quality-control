# Pomiary STL płytek n1–n6 i interfejsu wkładka↔płytka (DESIGN B, 31.10.2026)

Skrypt: `pomiary_stl.py` (trimesh 5.2.0, `py -3.12`, ray‑casting cięciw i trafień; niezależny od `ramka_generator.py` i od `trzecie_oko.py`). Surowe liczby: `pomiary_stl.json`. Układ STL płytki: spód z = 0, wierzch z = 8, XY jak `uklad.json` (środek 0,0; +x prawo, +y tył). Tolerancja oceny: 0,05 mm.

Pliki: `wyniki_v2/stl/ramka_plytka_{wieczorna,poranna}_v2.stl` (bazowe, 3 dołki, bez cyfry) i `_n1…_n6_v2.stl`; `ramka_wkladka_v2.stl`. **`stanowisko/modele_plytek/*/plytka_n*.stl` są bajtowo identyczne z `wyniki_v2/stl/*_n*_v2.stl`** (SHA‑256 zgodne dla n1–n6) — program i drukarnia dostają tę samą geometrię.

## 1. Wynik zbiorczy

| Co | Wynik | Nominał | Werdykt |
|---|---|---|---|
| Siatki | 8/8 zamknięte (watertight), objętości 57,94–57,95 (W) / 60,22–60,23 (P) cm³, 21 956–26 272 trójkątów | — | OK |
| Gabaryt | 96,000 × 96,000 × 8,000 (bazowe) / 8,600 (n: cyfra 0,6) | 96 × 96 × 8 (+0,6) | OK |
| Grubość w 5 punktach obrzeża | 8,000 wszędzie | 8 | OK |
| Płaskość wierzchu / spodu (15 punktów poza gniazdami) | 8,000…8,000 / 0,000…0,000 | płaskie | OK (model; druk — patrz §7) |
| Gniazda okrągłe: środki vs `uklad.json` | max odchyłka 0,0010 mm (P), 0,0006 (W) | ≤ 0,05 | OK |
| Gniazda okrągłe: ø wierzch (po korekcie cięciwy z = 7,95) | odchyłka ≤ 0,002 | d_top | OK |
| Gniazda: ø dna (z = 4,05), kąt ścianki | d_top − 2,14 (+0,027 z wys. pomiaru); 14,97–14,98° | d − 2·4·tan 15°; 15° | OK |
| Gniazda: dno z, otwór ø3 przelotowy | 4,000; 3,000, przelot 24+35/24+35 | 4; 3 | OK |
| Rynienki (W 60 × 15, P 50 × 13) | 59,97 × 14,97 na z = 7,95; dno 4,000; 4 otwory ø2,99 przelotowe w rozstawie 12 / 10 | zgodne (−0,027 z wys. pomiaru) | OK |
| Ścianki między gniazdami (30 par W, 57 par P, wszystkie nominalnie < 3,6) | min 3,027 na z = 7,95 (= 3,000 na wierzchu + 2·0,05·tan 15°); max odchyłka 0,030 | ≥ 3,0 | OK |
| Stożki znaczników A, B, C | ø 4,914 na z = 7,95 (= 5,0 − 2·0,05·tan 39,8°); wierzchołek z = 5,000 (głębokość 3,000); kąt półwierzchołkowy 39,8°; środek ±0,001 mm | ø5 × 3, (±42, ±42) | OK |
| Wycięcie D | x od 43,000, y do −43,000, przelotowe | 5 × 5 | OK |
| Dołki kodu | tylko dla bitów = 1: n1 A; n2 B; n3 A+B; n4 C; n5 A+C; n6 B+C; ø2,000 × 1,000, środek x = −45,000 | n = A + 2B + 4C | OK |
| Kieszenie magnesów A, B, C (od spodu) | ø5,200, sufit z = 2,200; do wierzchołka stożka zostaje 2,800 | ø5,2 × 2,2; 2,8 | OK |
| Cyfra reliefu | 0,600 nad wierzchem (n1–n6); bazowe bez cyfry | 0,6 | OK |
| Rowek pokrywki (bok +x, y = 20) | dno x = 47,200 (głęb. 0,8); z 5,55…6,45 (wys. 1,0; środek 2,0 pod wierzchem) | 0,8 / 1,0 / 2,0 | OK |
| Dołek A → krawędź płytki | 2,000 | 2,0 | OK |
| Dołek A → stożek A (na z = 7,5) | 3,63 (na wierzchu 3,21) | 3,2 (D11) | OK |
| Dołki → najbliższe gniazdo (ścianka nominalna) | W: id 13, 4,56; P: id 14, 3,80 | ≥ 3,5 | OK |

**Wniosek:** geometria STL = `uklad.json` = `parametry.json` co do 0,002 mm na wszystkich cechach, które program czyta (gniazda, stożki, dołki, wycięcie). Zgodność z G4b (raport końcowy) potwierdzona niezależnie.

## 2. Rzeczy, których arkusz i trzecie oko nie pokazały (nie błędy, ale do świadomej decyzji)

| Nr | Obserwacja | Liczby | Skutek |
|---|---|---|---|
| P‑1 | **Faza 0,5 górnych krawędzi zjada ściankę do krawędzi płytki.** Rząd R1 (y = −40,5, ø9 / y = −41,25, ø7,5) ma nominalnie 3,0 mm do przedniej krawędzi; na wierzchu zostaje 2,565 (faza 0,45 na z = 7,95). Poranna: gniazda 30/35 (ø12,5, x = ±38,75) do bocznej krawędzi 2,563. | 3,0 → 2,56 | Bez wpływu na wytrzymałość (PA12 8 mm), ale ścianka‑lico 2,5 mm na obrzeżu; przy frezowaniu CNC bez fazy wraca 3,0. |
| P‑2 | **Dołki kodu mają pionowe ścianki i płaskie dno** (walec ø2 × 1). Skaner światła strukturalnego widzi dno z kamery pod kątem ~25° tylko na ~1,5 mm szerokości, ścianek nie widzi; automatyczne „wypełnianie otworów” DentalScan może dołek zamknąć (promień wypełniania 2/4/6 mm > ø2). | ø2 × 1, 25°: widoczne dno 2 − 1·tan 25° = 1,53 | Ryzyko dla odczytu numeru; patrz propozycja A2 w `znaleziska.md` (dołek sferyczny/stożkowy, większy). |
| P‑3 | **Stożki znaczników: ścianka 39,8° od pionu** (ø5 × 3). Normalna ścianki jest 50° od pionu; kamera pod ~25° od osi projektora widzi bliższą ściankę pod 25°, dalszą pod 75° (prawie stycznie). Przy obrocie stolika 4–6 pozycji każda ścianka trafia pod dobry kąt co najmniej raz. Wierzchołek (ostrze) w skanie zawsze zaokrąglony — program ma dopasowywać stożek do ścianek, nie szukać wierzchołka. | 39,8° / 50° / 25…75° | OK, pod warunkiem dopasowania po powierzchni stożka (ICP na wgłębieniu), nie po wierzchołku. |
| P‑4 | **Jednoznaczność trzech stożków.** A(−42,−42), B(−42,42), C(42,42): trójkąt prostokątny równoramienny, kąt prosty w B; ramiona 84,0, przeciwprostokątna 118,8. Obroty o 90°/180°/270° przenoszą zbiór na pozycje z pustym narożnikiem D → ani jeden obrót nie pasuje. Jedyna niejednoznaczność to lustro (zamiana A↔C) = obrót o 180° wokół przekątnej, czyli płytka do góry nogami — fizycznie wykluczone (wgłębienia od góry, korony). | 84,0 / 84,0 / 118,8 | Jednoznaczne, jeśli program identyfikuje B jako wierzchołek kąta prostego (dwa ramiona 84). |
| P‑5 | **Cień koron na stożki.** Najbliższe gniazdo od stożka A: id 6 (W, ø9, x = −30) — 12,0 mm od osi stożka, krawędź gniazda 7,5 mm; praca 14 mm nad dnem = 10 mm nad płytką → kąt zasłonięcia atan(10/7,5) = 53° od poziomu. Stożek B/C: koniec rynienki 12 mm od osi, most do 10 mm nad płytką → to samo. Kamery patrzą z elewacji ~60–65°, więc stożek jest widoczny, ale z marginesem < 10°. | 53° vs 60–65° | W teście skanera (kryterium 8) ułożyć najwyższe prace w gniazdach przy stożkach. |
| P‑6 | **Korona nie stoi w okrągłym gnieździe, jeśli nie trzyma jej ścianka.** Ścianka 15° trzyma pracę tylko wtedy, gdy jej największa szerokość (równik) mieści się między ø dna i ø wierzchu (d − 2,14 … d). Praca węższa niż dno leży luźno na dnie ø(d − 2,14) i przy obrocie stolika może się przesunąć lub przewrócić (siekacze, kły). Praca szersza niż wierzch opiera się o fazę i nie jest trzymana. Tabela luzów w §3. | — | Patrz §3 i wniosek W‑2 w `znaleziska.md`. |
| P‑7 | **Cyfra „4” ma otwór w środku** (relief 0,6 to kontur cyfry) — pomiar z = 8,0 w (39,5, −44,5); to poprawne, cyfra leży obok, ale napis 5 mm w PA12 bez barwienia jest słabo widoczny (biały na białym). | — | Patrz Część 3: grawer/kontrast. |
| P‑8 | **Brak w projekcie adaptera płytka ↔ stolik skanera.** Płytka ma płaski spód z 3 otwartymi kieszeniami magnesów; nic nie ustala jej na talerzu skanera (interfejs stolika nieznany — pytanie 12 do Aidite). Przy samym obrocie trzyma ją tarcie; przy przechyle spadnie. | — | Wymaganie dla osobnej części (adapter), nie dla płytki; magnesy A/B/C mogą trzymać płytkę na stalowym adapterze (patrz `znaleziska.md`). |

## 3. Luz koron w gniazdach (model geometryczny)

Założenia: praca leży powierzchnią żującą w dół; o utrzymaniu decyduje największa szerokość korony (max z MD, BL) względem stożka ø_dna = d − 2,14 … ø_wierzchu = d; skala zielonej cyrkonii ×1,23 (skurcz 20–25 %). Wymiary koron: wartości średnie z tabel anatomii zębów (Wheeler/Nelson) — MD × BL × wysokość korony [mm]; realne prace laboratoryjne bywają o 0,5–1 mm inne, więc tabela to ocena jakościowa, nie pomiar.

Wieczorna (zielone ×1,23): 13 × ø9 (dno 6,86), 6 × ø12 (dno 9,86), 5 × ø15 (dno 12,86)

| ząb | MD × BL × H po skali | ø9 (×13) | ø12 (×6) | ø15 (×5) |
|---|---|---|---|---|
| siekacz dolny | 6,2 × 7,4 × 11,1 | trzyma, 3,0 pod wierzchem | luźno na dnie (luz 2,5) | luźno (luz 5,5) |
| siekacz boczny górny | 8,0 × 7,4 × 11,1 | trzyma, 1,9 pod wierzchem | luźno (1,9) | luźno (4,9) |
| siekacz centralny górny | 10,5 × 8,6 × 12,9 | **NIE mieści się** | trzyma, 2,9 | luźno (2,4) |
| kieł górny | 9,2 × 9,8 × 12,3 | **NIE** | na granicy dna (0,0) | luźno (3,0) |
| przedtrzonowy górny | 8,6 × 11,1 × 10,5 | **NIE** | trzyma, 1,7 | luźno (1,8) |
| przedtrzonowy dolny | 8,6 × 9,2 × 9,8 | **NIE** | luźno (0,6) | luźno (3,6) |
| trzonowy 1. górny | 12,3 × 13,5 × 9,2 | NIE | NIE | trzyma, 2,7 |
| trzonowy 1. dolny | 13,5 × 12,9 × 9,2 | NIE | NIE | trzyma, 2,7 |
| trzonowy 2. dolny | 12,9 × 12,3 × 8,6 | NIE | NIE | trzyma, 3,9 |

Poranna (spieczone ×1,00): 22 × ø7,5 (dno 5,36), 7 × ø10 (dno 7,86), 6 × ø12,5 (dno 10,36)

| ząb | MD × BL × H | ø7,5 (×22) | ø10 (×7) | ø12,5 (×6) |
|---|---|---|---|---|
| siekacz dolny | 5,0 × 6,0 × 9,0 | trzyma, 2,8 | luźno (1,9) | luźno (4,4) |
| siekacz boczny górny | 6,5 × 6,0 × 9,0 | trzyma, 1,9 | luźno (1,4) | luźno (3,9) |
| siekacz centralny górny | 8,5 × 7,0 × 10,5 | **NIE** | trzyma, 2,8 | luźno (1,9) |
| kieł górny | 7,5 × 8,0 × 10,0 | **NIE** | trzyma, 3,7 | luźno (2,4) |
| przedtrzonowy górny | 7,0 × 9,0 × 8,5 | **NIE** | trzyma, 1,9 | luźno (1,4) |
| przedtrzonowy dolny | 7,0 × 7,5 × 8,0 | **NIE** | luźno (0,4) | luźno (2,9) |
| trzonowy 1. górny | 10,0 × 11,0 × 7,5 | NIE | NIE | trzyma, 2,8 |
| trzonowy 1. dolny | 11,0 × 10,5 × 7,5 | NIE | NIE | trzyma, 2,8 |
| trzonowy 2. dolny | 10,5 × 10,0 × 7,0 | NIE | NIE | trzyma, 3,7 |

Wniosek z tabel (do potwierdzenia na 20 realnych pracach suwmiarką — 10 min):
- **Najmniejsze gniazda (W ø9 ×13 = 54 % gniazd; P ø7,5 ×22 = 63 %) mieszczą tylko siekacze** (dolne i górne boczne). Trzonowce i przedtrzonowce, czyli typowo 60–75 % prac w laboratorium, wymagają W ø12/ø15 (11 gniazd) i P ø10/ø12,5 (13 gniazd).
- Proporcja gniazd wygląda na odwrotną do proporcji prac; pojemność „użyteczna” płytki może być bliższa 11–13 niż 24–35. To nie błąd geometrii, tylko założenie spec (Z20), którego nikt nie sprawdził na rozkładzie prac.
- Stożek 15° trzyma koronę w wąskim pasie 2,14 mm szerokości; praca węższa o > 2 mm od wierzchu leży luźno na dnie. Gniazdo uniwersalne (patrz Część 2) jest realną alternatywą.

## 4. Interfejs płytka ↔ wkładka (pomiar `ramka_wkladka_v2.stl`; w STL spód ramy na z = 3,5, kołki ustalające 0…3,5)

| Cecha | Zmierzone | Nominał | Werdykt |
|---|---|---|---|
| Otwór wkładki (x, y na z = 8) | 96,600 × 96,600 | 96,6 | luz 0,300 na stronę ✓ |
| Rama zewn. | 99,6 (x, w pasie z rowkiem) / 104,6 (bbox) | 104,6 | ✓ |
| Wysokość ramy | 6,000 | 6 | ✓ |
| Półki narożne A–D: wierzch | 2,500 nad spodem ramy; krawędzie wewn. ±36,3 (12 × 12) | 2,5; 12 | ✓ |
| Faza naprowadzająca otworu | od z = 5,0 do 6,0 nad spodem ramy, 48,3 → 49,3 (1 × 45°) | 1 × 45° | ✓ |
| Kołek orientacyjny D | x 43,4…47,8, y −43,4…−47,8 (4,4 × 4,4), szczyt 7,5 nad spodem ramy (5,0 nad półką); 0,5 od ścian otworu | 4,4 × 4,4 × 5 | ✓ |
| Kołek w wycięciu 5 × 5 | luz 0,3 na stronę (43,0…48,0 vs 43,4…47,8) | 0,3 | ✓ (4.11 pisze 0,3; R52‑U2 0,4 — geometrycznie 0,3 w x i y od ścian wycięcia, 0,6 przy dociśnięciu do rogu) |
| Kieszenie Halla A, B, C | 5,0 × 5,5, przelotowe; D bez kieszeni | 5,0 × 5,5 | ✓ |
| Wycięcie palcowe | 30,0 (x) | 30 | ✓ |
| **Obrót płytki o 180° / 90°** | kołek tylko na półce D (A, B, C: wierzch 2,5, bez kołka); płytka obrócona ma pełny narożnik nad kołkiem → leży 5 mm wyżej, przekrzywiona, nie wchodzi w otwór | — | **Nie da się włożyć obrócona** (blokada mechaniczna, widoczna gołym okiem) ✓ |
| Powtarzalność położenia | luz otworu 0,3/stronę + luz kołka 0,3 → ±0,3 mm w x, y; obrót ≤ atan(0,6/96) = 0,36°; na krawędzi płytki ≤ 0,3 mm | ±0,5 (4.6) | ✓ (diody P2.5: 1/8 piksela) |
| Grubość materiału płytki nad czujnikiem | magnes cofnięty 0,2 + szczelina 1,0 → 1,7 do struktury | ≤ 4 | ✓ |

Wymagania interfejsu, które DESIGN A musi utrzymać (jeśli zmienia wkładkę): otwór = bok płytki + 0,6; kołek 4,4 w wycięciu 5 × 5 w narożniku D (+48, −48); półki ≤ 13 × 13 (strefa bez gniazd); kieszenie Halla pod (±42, ±42) z wyjątkiem D; wysokość półki tak, by spód płytki był ≤ 4 mm od lica czujnika (A3144 ~40 mT przy magnesie ø5 × 2).

## 5. Dołki kodu vs rozdzielczość skanera

- Rozdzielczość: 5 MP (2448 × 2048) na polu ~100 mm → piksel ~0,04–0,05 mm na obiekcie; gęstość siatki eksportu typowo 0,05–0,1 mm. Dołek ø2 = 20–40 punktów średnicy; głębokość 1 mm = 12–25 × dokładność 8 µm. **Rozdzielczość nie jest problemem.**
- Problemem jest kształt (P‑2): pionowa ścianka i wąskie dno. Bezpieczniejszy dołek: czasza kulista R 1,5 (ø3 × 0,9) lub stożek 90° ø3 × 1,5 — każdy punkt widoczny z kamery pod 25–30°, brak „dziury” do wypełnienia, łatwiejsze czyszczenie z pyłu.
- Odczyt binarny z 3 pozycji wymaga, by program odróżnił „dołek” od „brak dołka” po lokalnym zagłębieniu ≥ 0,5 mm w promieniu 1 mm od pozycji z `uklad.json` — przy wyrównaniu < 0,05 mm po stożkach to pewne.

## 6. Pole skanowania — geometria płytki do zmieszczenia

Skrajne cechy, które program MUSI widzieć: stożki na (±42, ±42) → promień od środka 59,4 mm; narożniki płytki 67,9 mm; prace do 10 mm nad wierzchem (18 mm nad spodem). Minimalne pole w jednym skanie: **≥ 90 × 90 mm w rzucie** (stożki z zapasem 3 mm) i **≥ 20 mm w z**; preferowane ≥ 100 × 100 (cała płytka, w tym wycięcie D i cyfra, dla kontroli ułożenia). Szczegóły w `skaner_aidite.md`.

## 7. Czego STL nie mówi (do sprawdzenia na wydruku)

- Płaskość po druku: PA12 MJF/SLS 96 × 96 × 8 wygina się typowo 0,1–0,3 mm (zależnie od orientacji w komorze); w ramce bez znaczenia, w skanerze też (płytka to tylko nośnik, program wyrównuje po stożkach), ale płytka kołysząca się na stoliku skanera przy obrocie przesuwa prace. Wymóg odbioru: płaskość ≤ 0,2 mm na szczelinomierzu na szkle.
- Chropowatość SLS/MJF (Ra 5–10 µm) w stożkach znaczników: zaokrągla wierzchołek, ale dopasowanie po ściankach pozostaje; dołki ø2 w MJF często zarastają proszkiem (przedmuchać).
- Otwory ø3 w dnach gniazd: PA12 spieczony proszek — przebić wiertłem ø3 (checklista odbioru już to ma).
