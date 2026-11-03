# Znaleziska DESIGN B — płytki n1–n6: wymiary, design, skaner, uproszczenia, premium (31.10.2026)

Pliki towarzyszące: `pomiary_stl.md` (+ `pomiary_stl.py`, `pomiary_stl.json`), `skaner_aidite.md`, `handout.md`. Zakres: wyłącznie płytki, ich oznaczenia i interfejs do wkładki (wymagania). Korpus/blat/wkładka/pokrywka/elektronika = DESIGN A.

## 5 najważniejszych wniosków

1. **Geometria STL jest bezbłędna** — wszystkie cechy czytane przez program (gniazda, 3 stożki, dołki kodu, wycięcie) zgadzają się z `uklad.json` i `parametry.json` co do ≤ 0,002 mm (wymagane 0,05); siatki zamknięte; `stanowisko/modele_plytek/*.stl` bajtowo identyczne z plikami do drukarni. Nic nie blokuje druku pod względem wymiarów.
2. **Pole skanowania jest na granicy, a nie „≥ 100 × 100”**: jedyna potwierdzona liczba (producent OEM, rodzina DS‑EX = A‑IS Pro 3) to 100 × 100 × 75 mm. Stożki znaczników leżą 59,4 mm od osi obrotu (poza walcem ø100 o 9,4 mm), narożniki 67,9 mm. W osiach stolika mieści się z 2 mm zapasu; przy obrocie o 45° stożki wychodzą z pola. Test kryterium 8 pozostaje obowiązkowy; plan B (`plate_size` 90 lub znaczniki do r ≤ 50) trzeba mieć policzony w D6 PRZED testem, nie po.
3. **Tryb multi‑die obsługuje ≤ 8 prac** — płytkę skanuje się jako „model/Range Scan”, nie jako Multidie. Pytania 5 i 14 w `mail_aidite_zapytanie.md` i tabela w `notatki_dokumentacja_skanera.md` zakładają Multidie — do przeformułowania przed wysyłką.
4. **Rozkład gniazd nie pasuje do rozkładu prac** (model geometryczny na średnich wymiarach zębów): najmniejsze gniazda (W ø9 — 13 z 24; P ø7,5 — 22 z 35) trzymają tylko siekacze; trzonowce i przedtrzonowce (zwykle 60–75 % prac) wymagają 11 (W) / 13 (P) większych gniazd. Pojemność użyteczna może być bliższa 11–13 niż 24–35. Do potwierdzenia suwmiarką na 20 realnych pracach (10 min) — zanim pójdzie zamówienie.
5. **Pod skaner: szary mat, nie czarny i nie biały‑na‑pokaz.** Wszystkie dowody „bez sprayu” dotyczą jasno‑/średnioszarego matu; czerń matowa = ryzyko średnie, czerń z połyskiem = wykluczona; biały PA12 skanuje się, ale nie daje kontrastu dla oka. Rekomendacja premium: frezowane Al 6061, piaskowane szklanie, anodowane na ciemnoszary/grafitowy mat (nie barwione na czarny), numer grawerowany laserem — po próbie 1 szt. na skanerze obok 1 szt. MJF szary.

---

## Część 1 — weryfikacja (rozbieżności z liczbami)

### 1.1 STL vs `uklad.json` vs `parametry.json` (wymagane ≤ 0,05 mm)

| Cecha | Max odchyłka STL–JSON | Uwagi |
|---|---|---|
| Środki 24 + 35 gniazd okrągłych | 0,0010 mm | — |
| ø wierzchu / dna gniazd, kąt 15° | 0,002 mm / 14,97–14,98° | cięciwa 0,05 pod wierzchem = −0,027 (tan 15°) — uwzględnione |
| Rynienki 60 × 15 / 50 × 13, 4 otwory ø3 | 0,03 mm (ten sam efekt cięciwy) | otwory przelotowe, rozstaw 12 / 10 |
| Stożki A, B, C (±42, ±42) ø5 × 3 | środek 0,001; głębokość 3,000; kąt półwierzchołkowy 39,8° | wgłębienia (program: OK) |
| Dołki kodu x = −45, y = −36/−33/−30, ø2 × 1 | 0,000; obecne tylko dla bitów = 1 (n1 A; n2 B; n3 AB; n4 C; n5 AC; n6 BC) | kod n = A + 2B + 4C ✓ |
| Wycięcie D 43…48 × −48…−43 | 0,000 | przelotowe |
| Kieszenie magnesów ø5,2 × 2,2, 2,8 mm do wierzchołka stożka | 0,000 | — |
| Rowek pokrywki 0,8 głęb., 1,0 wys., 2,0 pod wierzchem | 0,000 | — |
| Cyfra relief 0,6 | 0,000 | tylko n1–n6 |
| Ścianki między gniazdami (87 par) | min 3,000 na wierzchu | ≥ 3 ✓ |

**Rozbieżności STL–JSON: brak.** Potwierdzenie G4b niezależną metodą.

### 1.2 Rozbieżności dokument–dokument i dokument–rzeczywistość

| Nr | Gdzie | Co mówi | Co ustalono | Liczby |
|---|---|---|---|---|
| R‑1 | `plan_ramki_v2.md` Z1; plan wdrożenia zał. 11, Decyzje otwarte 1 | Pole skanowania ≥ 100 × 100 „do potwierdzenia” | Producent OEM: 100 × 100 × 75 — płytka mieści się tylko w osiach, stożki poza ø100 | stożki r = 59,4 > 50; narożniki 67,9; margines w osiach 2,0 |
| R‑2 | `notatki_dokumentacja_skanera.md` (Multidie), mail pyt. 5/14 | Skan płytki w trybie Multidie | Multidie ≤ 8 stempli; płytka = skan modelu / Range Scan | 8 < 24…35 |
| R‑3 | Plan wdrożenia zał. A i checklista odbioru („stożki ø5, **wysokość** 3 mm”) vs 4.1 / `uklad.md` („wgłębienie, wierzchołek w dół”) | Słownictwo sugeruje wypustki | STL: wgłębienia; program dopasowuje do wgłębienia | apex z = 5,0 (3 mm pod wierzchem) |
| R‑4 | Z20 / D6 (proporcje gniazd ze spec) | 13 × ø9, 6 × ø12, 5 × ø15 / 22 × ø7,5, 7 × ø10, 6 × ø12,5 | Ścianka 15° trzyma pracę tylko w pasie 2,14 mm szerokości; małe gniazda = tylko siekacze (`pomiary_stl.md` §3) | W: 54 % gniazd dla ~20 % prac; P: 63 % |
| R‑5 | 4.11 (luz kołka 0,3) vs R52‑U2 (0,4) | sprzeczne liczby | Oba prawdziwe: kołek 43,4…47,8 w wycięciu 43…48 → 0,4 do ścian wewnętrznych wycięcia przy płytce dociśniętej do narożnika D; 0,3 to nominalne (5 − 4,4)/2 | 0,4 / 0,3 |
| R‑6 | 4.1 „faza 0,5 górnych krawędzi” | — | Faza zjada ściankę brzegową przy gniazdach R1 i P 30/35 na wierzchu | 3,0 → 2,56 |
| R‑7 | D11 / 4.1 dołki ø2 × 1 (walec) | „program czyta ze skanu” | Walec z pionową ścianką: dno widoczne z kamery 25° na 1,5 mm; „Fill holes” (promień 2/4/6) może zamknąć | ø2 < 4 mm promienia wypełniania |
| R‑8 | Plan: brak części | — | Nie ma adaptera płytka ↔ stolik skanera (interfejs stolika nieznany, pyt. 12); płytka ma płaski spód i trzyma ją tylko tarcie | — |
| R‑9 | Plan wdrożenia: skaner 20–25 tys. zł | — | Odpowiednik DS‑EX Pro(H) w PL 34,9–36 tys. zł brutto; A‑IS Pro (1,3 MP) 31 tys. | +10–15 tys. zł vs budżet |
| R‑10 | Plan: „biały PA12 pod skaner” + „premium” | — | Biały = brak kontrastu dla oka; czarny = ryzyko skanu; dowody tylko dla szarego matu | — |
| R‑11 | Mail do Aidite | 37 pytań | Brakuje: kąt triangulacji / wysokość kamer (ocena widoczności ścianek 40° stożków i 15° gniazd); „Fill holes” globalnie off (jest w pyt. 17) | — |

### 1.3 Pozostałe oceny z Części 1 (wynik pozytywny)

- **Jednoznaczność 3 stożków**: trójkąt prostokątny równoramienny (84 / 84 / 118,8), kąt prosty w B; żaden obrót o 90°/180°/270° nie pasuje (narożnik D pusty), lustro = płytka do góry nogami (wykluczone). Wymóg dla modułu plate: wykryć B jako wierzchołek z dwoma ramionami 84 mm, potem ICP na ściankach stożków (nie na wierzchołku — zaokrąglony w skanie).
- **Widoczność stożków z góry**: ścianka 39,8° od pionu; przy kamerach ~25° od osi bliższa ścianka 25°, dalsza 75°; 4 pozycje obrotu pokrywają każdą ściankę. Cień koron: najbliższe gniazdo 12 mm od osi stożka, praca 10 mm nad płytką → 53° od poziomu vs elewacja kamer ~60–65° — margines < 10°, do sprawdzenia w teście z najwyższą pracą przy stożku.
- **Dołki kodu vs 8 µm**: ø2 = ~50 px, głębokość 1 = 125 × dokładność — rozdzielczość nie jest problemem (kształt jest, R‑7).
- **Pasowanie płytka ↔ wkładka**: luz 0,300/stronę; kołek D 4,4 × 4,4 × 5 (0,5 od ścian otworu); płytka obrócona o 90°/180° **nie wchodzi** (pełny narożnik ląduje na kołku 5 mm — widoczne gołym okiem); powtarzalność ±0,3 mm, obrót ≤ 0,36°; czujniki Halla 1,7 mm od magnesu.
- **Grubość i płaskość**: 8,000 w 5 punktach, model idealnie płaski; po druku PA12 wymagać płaskości ≤ 0,2 mm (szczelinomierz na szkle) — płytka kołysząca się na stoliku przesuwa prace.
- **Kolor/połysk materiału**: patrz `skaner_aidite.md` §5 — PA12 biały mat OK dla skanera, bez dowodu wprost; żywica tylko matowa szara; spray na płytce dozwolony (nie na pracach), ale to krok dziennie — lepiej materiał bez sprayu.
- **Odbicia od cyrkonii**: spieczona przezierna — producent zaleca opaker/spray przy błyszczących półprzeziernych; tryby HDR / Reduce High Brightness do testu (kryterium 5). Zielona matowa — bez sygnałów ostrzegawczych.

---

## Część 2 — projekt alternatywny (propozycje)

Legenda „program”: U = zmiana `uklad.json`, P = zmiana modułu plate, 0 = bez zmian. „Wkładka”: wymaganie dla DESIGN A.

| Nr | Propozycja | Co zmienia | Zysk | Ryzyko | Program | Wkładka (DESIGN A) | Rekomendacja |
|---|---|---|---|---|---|---|---|
| A1 | **Jedna geometria bazowa + numer nadawany po wykonaniu** (frezowanie/grawer dołków i cyfry z szablonu; magnesy i tak klejone wg numeru) | 1 plik STL/STEP zamiast 6 (+2 bazowe); wariant = instrukcja obróbki | 1 weryfikacja zamiast 6; dowolny numer później (zapas bez numeru); mniej plików u wykonawcy | Dołek po obróbce musi trafić w ±0,2 mm pozycji z `uklad.json` (wiertło w przyrządzie — łatwe w CNC, trudniejsze ręcznie w PA12) | 0 | brak | TAK przy CNC; przy MJF zostawić 6 plików (drukarnia nie dopłaca za warianty) |
| A2 | **Dołki kodu sferyczne R 1,5 (ø3 × 0,9) zamiast walca ø2 × 1**; opcjonalnie kod pozycyjny: 1 dołek na jednej z 6 pozycji (y = −36 … −21 co 3) = numer czytelny dla człowieka (policz od rogu) | kształt i (opcjonalnie) kodowanie | Każdy punkt dołka widoczny z kamery 25–30°, brak „[cytat usuniety]” do wypełnienia, czyszczenie z pyłu; kod pozycyjny czytelny bez tabeli | Ścianka do krawędzi płytki 2,0 → 1,5 przy ø3 (przesunąć x na −44,5); kod pozycyjny wymaga 6 pozycji (18 mm kolumny) — jest miejsce (y −36…−21, gniazdo id 13 W / 14 P ≥ 3 mm) | U (+ P: wykrywanie zagłębienia sferycznego — trywialne) | brak | TAK (kształt); kod pozycyjny — opcja, jeśli właściciel chce czytać numer bez cyfry |
| A3 | **Stożki znaczników → czasze kuliste R 3 (ø6 × 1,5)** | kształt znacznika | Normalne ścianek 0–60° (zawsze ≥ 1 kamera pod dobrym kątem), brak ostrza, dopasowanie sfery = najprostszy i najpewniejszy ICP, frez kulisty w CNC natywny, łatwe czyszczenie; materiał nad kieszenią magnesu 4,3 zamiast 2,8 | Płytsza cecha = mniejszy sygnał w z (1,5 mm = 190 × dokładność — wystarczy); test syntetyczny w `synth` do powtórzenia | U (markers: shape/r) + P (fit sfery zamiast stożka) | brak | TAK, jeśli zmiana programu zmieści się przed testem; inaczej zostawić ø5 × 3 (działa) |
| A4 | **Znaczniki bliżej osi** (np. (±36, ±36) → r 50,9 lub mid‑krawędź (0, ±45)/(±45, 0) → r 45) | pozycja znaczników | Mieszczą się w ø100 przy każdym kącie obrotu | Kolizja z rzędami skrajnymi (R1 x ±34,5; W R4 x ±43,5) → rzędy tracą 1–2 gniazda; przeliczyć D6 | U | kieszenie Halla pod magnesami — jeśli magnesy zostają współosiowe ze znacznikami, DESIGN A musi przesunąć kieszenie; lepiej ROZDZIELIĆ magnesy (zostają w (±42, ±42)) od znaczników | tylko jako plan B po negatywnym teście kryterium 8 |
| A5 | **Gniazda uniwersalne**: dwa rozmiary zamiast trzech, stożek 25° i głębokość 5 (pas trzymania 4,7 mm zamiast 2,14): W: ø16/ø11 (trzyma 11,3–16 / 6,3–11), P: ø13/ø9 (8,3–13 / 4,3–9) | rozmiary gniazd, kąt, głębokość | Każda praca trafia w 1 z 2 gniazd i jest trzymana ścianką (dziś 3 rozmiary i pas 2,14); technik nie dobiera „[cytat usuniety]” | Mniej gniazd w rzędzie (W: 4 × ø16 + 2 rzędy × 7 × ø11 ≈ 18 + 2 rynienki; P: 6 × ø13 + 3 × 9 × ø9 ≈ 33); głębsze gniazdo zasłania więcej ściany bocznej korony (brzeg i wnętrze nadal odsłonięte) | U (nowe D6) + 0 w plate | brak (otwory ø3 pod diodami: pozycje z `uklad.json`) | TAK po pomiarze 20 prac (wniosek 4) — decyzja właściciela |
| A6 | **Rzędy‑rynienki zamiast gniazd** (5 rynienek 84 × 15, prace kładzione dowolnie) | cały układ | Zero decyzji o rozmiarze, pojemność ~30–35 niezależnie od mieszanki | Prace mogą się stykać → segmentacja po skanie zamiast cięcia po gniazdach (duża zmiana plate), wskazywanie diodami po pozycji x (możliwe, 2,5 mm raster), prace przesuwają się wzdłuż rynienki przy obrocie | U + **P duże** | brak | NIE teraz (zmienia program i test); zanotować na v3 |
| A7 | **Mniej wariantów: ten sam układ gniazd W i P** (po A5: jeden układ z 2 rozmiarami dla obu, skala zielona/spieczona różni się 23 % — za dużo na jeden rozmiar, więc nadal 2 geometrie) | — | — | — | — | — | Nie da się sensownie zejść poniżej 2 geometrii (W/P); liczba sztuk 3 + 3 zostaje (2 w obiegu + zapas) |
| A8 | **Orientacja: wycięcie D + kołek** | bez zmian | już blokuje obrót 90°/180° | — | 0 | utrzymać kołek 4,4 w D | TAK (bez zmian) |
| A9 | **Adapter płytki na stolik skanera** (nowa część): stalowa/aluminiowa płyta z ramką 96,6 (jak wkładka) i 3 stalowe wkładki pod magnesy A/B/C płytki (własne magnesy płytki trzymają ją), interfejs do talerza wg STEP Aidite | nowa część | Płytka nie ślizga się przy obrocie, zawsze to samo położenie w skanerze (program i tak wyrównuje po stożkach, ale powtarzalne położenie = stałe cięcie „jig”) | n1/n2/n4 mają 1 magnes — trzyma słabo; dodać 4. kieszeń „zawsze z magnesem” w narożniku D (x 40,5, y −40,5, od spodu): w rzucie zachodzi 1,1 mm na cyfrę (39,5, −44,5), ale cyfra to relief na wierzchu, a kieszeń 2,2 od spodu — 5,8 mm materiału między nimi, bez kolizji | 0 (adapter) / U jeśli 4. magnes | 4. magnes w D nie koliduje z kołkiem (kołek 43,4…47,8) — DESIGN A: półka D bez czujnika, bez zmian | TAK, po otrzymaniu STEP stolika (poza zakresem płytki; czeka na pyt. 12) |
| A10 | **Faza 0,5 → 0,3** górnych krawędzi lub bez fazy przy CNC | faza | Ścianka brzegowa 2,56 → 2,76 / 3,0 | kosmetyczne | 0 | brak | opcjonalne |
| A11 | **Materiał z możliwością czyszczenia IPA/wycierania**: realna potrzeba to wycieranie IPA i pył, nie autoklaw | materiał | Al anodowane: pełna odporność; PA12: OK („limited swell”); żywice Grey Pro/Tough: nasiąkają IPA (+1,6 / +3,7–4,2 % masy) → odpadają na stałe | — | 0 | brak | TAK: wyklucza żywice standardowe jako płytki produkcyjne (zostają jako test/prototyp) |
| A12 | **Płytki frezowane zamiast drukowanych** | technologia | ±0,05 mm, bez fazy, sferyczne dołki/czasze natywne, numer grawerowany, anoda; A1 za darmo | koszt 3–6 × MJF; termin 2–3 tyg.; masa Al 160 g vs 60 g (obciążenie stolika — pyt. 11); ciemna anoda = test skanu | 0 | brak (te same wymiary zewnętrzne; magnesy w kieszeniach jak dziś) | TAK dla serii premium — po próbie 1 szt. (Część 3) |

Uwagi do programu zbiorczo: A2 + A3 to jedna mała zmiana w `uklad.json` (pola `shape`, `r`) i w `plate` (fit sfery). Reszta (A5, A9) to tylko dane w JSON. Nic z Części 2 nie wymaga zmian w `uklad.py` (czyta pola generycznie, ale `Znacznik`/`Dolek` mają stałe pola `d`, `depth` — dodać `shape`, `r` jako opcjonalne).

---

## Część 3 — PREMIUM i wykonanie

### 3.1 Tabela decyzji

Koszty: szacunki z publicznych cenników (31.10.2026, netto), źródła w `skaner_aidite.md` §5 i poniżej; „oferta” = trzeba zapytać. Czas = od zamówienia do odbioru.

| Element | Zlecić / samemu | Technologia, materiał | Wykończenie | Koszt (1 szt. / 6 szt.) | Czas | Uzasadnienie pod skaner i premium |
|---|---|---|---|---|---|---|
| **Płytka testowa skanera + prototyp pasowań** (teraz) | SAMEMU (drukarka żywiczna w firmie) | DLP/LCD, żywica modelowa dentystyczna **matowa szara** (np. BlueCast Model Grey, Liqcreate Model Pro Grey, Rodin TruModel — deklarowane „scan without spray”) | bez wygładzania; dno zeszlifować na płasko | ~25–40 zł materiału / — | 1 dzień | Rozstrzyga kryterium 8 (pole), widoczność stożków i dołków, pasowanie we wkładce; nie jest częścią produkcyjną (żywice nasiąkają IPA, HDT 60–80 °C) |
| **Próbka A: płytka premium** (po teście skanera, przed serią) | ZLECIĆ (frezarnia CNC + anodownia) | CNC Al 6061‑T6, 96 × 96 × 8, frez kulisty na czasze/dołki (A2/A3) lub stożkowy na ø5 × 3 | piaskowanie szklane → anoda **twarda bez barwnika (ciemnoszara, lekko matowa)** albo anoda dekoracyjna barwiona na grafit (NIE czarny połysk); numer i napis grawer laserowy (biały znak na anodzie) | CNC 500–1200 zł + anoda partia 100–300 zł + grawer 35–100 zł → **~700–1600 zł za 1**; seria 6: **~3,5–7 tys. zł** | 2–3 tyg. (CNC 5–10 dni + anoda 4–6 dni + grawer) | ±0,05–0,1 mm (Al CTE 23,6 → 0,11 mm na 50 K), pełna odporność IPA/temp., czyszczenie bez wchłaniania pyłu, waga 160 g = „solidne” w ręce, kontrast ciemny/biała cyrkonia dla oka; ryzyko: ciemna anoda pochłania światło — stąd próba 1 szt. i ciemnoszary (nie czarny) |
| **Próbka B: płytka tania** (równolegle z A) | ZLECIĆ (drukarnia PL: Cubic Inch / Laboratorium Druku 3D Gliwice / CadXpert / Materialise / Xometry; tanio: JLC3DP ~70 zł + wysyłka/cło) | MJF PA12 **naturalny jasnoszary** (nie barwiony) | standard (piaskowanie), bez wygładzania parowego (zwiększa połysk) | 150–300 zł / 900–1 800 zł (PL); JLC3DP ~400 zł + transport | 3–7 dni (PL), 2–3 tyg. (JLC) | Najbezpieczniejsza powierzchnia pod skaner (szary mat), ±0,3 mm, HDT 175 °C; wygląd „techniczny” (2/5); barwienie na czarno = ryzyko skanu i wytarcia barwnika (0,25–0,5 mm) |
| **Seria 6 szt.** (po porównaniu A i B na skanerze) | ZLECIĆ | wybór: Al (premium) albo MJF szary (budżet) | jak wyżej | Al 3,5–7 tys. zł; MJF 0,9–1,8 tys. zł | 2–3 tyg. / 1 tydz. | Decyzja właściciela po próbie; przy Al stosować A1 (jedna geometria, numer grawerem, dołki z przyrządu) |
| **Numeracja i napisy** | ZLECIĆ (z płytką) | grawer laserowy (włóknowy na anodzie: biały trwały; na PA12: CO₂, ciemny ślad) | — | 35–100 zł za 6 szt. (+25 zł ustawienie) | w cenie terminu | Relief 0,6 w białym PA12 jest słabo widoczny dla oka; grawer daje kontrast; relief zostaje dla skanera, jeśli program ma go czytać (nie ma — czyta dołki) → relief można usunąć przy grawerze |
| **Pokrywka** (nie płytka, tylko interfejs) | wg DESIGN A | — | — | — | — | Rowek 1,0 × 0,8 w Al bez zmian (frez tarczowy); wymaganie: pokrywka nie rysuje anody (PETG OK) |
| **Adapter stolika skanera** (A9) | SAMEMU prototyp (żywica) → ZLECIĆ (stal/Al) | zależnie od STEP Aidite | — | 100–400 zł | po odpowiedzi Aidite | Powtarzalne położenie, brak ślizgania |
| **Alternatywy odrzucone** | — | POM‑C czarny CNC (półpołysk, CTE 130, 500–1000 zł) — gorszy od Al w każdym punkcie poza ceną; PEEK (beż, 1,2–2,5 tys. zł); Corian ciemny (400–900 zł, rysy widoczne, brak danych IPA); Macor/Al₂O₃ (> 1,5 tys. zł/szt., biały, 3–6 tyg.); SLM Al (1,7–3,6 tys. zł/szt. + i tak frezowanie); żywice SLA Formlabs (Grey Pro HDT 78 °C, nasiąka IPA; Rigid 10K biały; Tough 2000 nasiąka 4 %) | | | | |

Źródła kosztów (wybór): MJF PL — https://cubicinch.pl/cennik/ , https://laboratoriumdruku3d.pl/cennik-druku-3d/ , https://cadxpert.pl/cennik-druku-3d/ ; JLC3DP 0,275 $/g — https://jlc3dp.com/help/article/PA12-HP-Nylon ; CNC PL 135–250 zł/h — https://jakubowski-mechanika.pl/cennik/ , https://anbi-tech.pl/anbi-tech-produkcja/frezowanie-cnc/ ; Hubs POM ±0,125 — https://www.hubs.com/cnc-machining/plastic/pom-delrin/ ; anodowanie — https://zobaluslugi.pl/anodowanie-aluminium-cennik/ , http://galw.pl/uslugi-galwaniczne/ ; grawer — https://laserkrakow.pl/cennik/ , https://laserbielsko.pl/cennik/ , https://3dls.pl/grawerowanie-laserowe/grawerowanie/ ; Al 6061 CTE — https://www.gabrian.com/wp-content/uploads/2018/09/6061-Aluminum-Alloy-Properties.pdf ; PA12 MJF — https://www.materialise.com/en/industrial/3d-printing-materials/pa12-mjf ; Formlabs IPA — https://formlabs.com/eu/support/solvent-compatibility/ ; żywice modelowe szare — https://imakr.com/eu/bluecast-resin/4005-bluecast-model-grey-dental-gray-lcddlp ; czerń a skan — https://www.insvision3d.com/en/news/industry-articles/when-black-surfaces-break-the-scanner-3d-scanning-reflective-and-dark-parts-without-spray/ , https://www.matterandform.net/products/three ; anoda twarda odcień — https://www.finishing.com/427/54.shtml .

### 3.1a Decyzja D‑2 (właściciel, 31.10): płytki SZARE, mat — tabela zawężona do wariantów szarych

Tabela 3.1 zostaje jako pełne porównanie; wybór ogranicza się do poniższych. Odcienie w skali: jasnoszary ≈ RAL 7035/7047, średnioszary ≈ RAL 7042/7045, grafit ≈ RAL 7024/7016. Dla skanera najbezpieczniejszy jest jasno‑/średnioszary; grafit nadal „szary” (nie czarny), ale wymaga próby ekspozycji.

| Technologia | Odcień (jak go uzyskać) | Jak uzyskać mat | Trwałość koloru przy IPA / wycieraniu | Koszt 1 / 6 szt. | Czas | Uwagi |
|---|---|---|---|---|---|---|
| **PA12 MJF surowy** (HP, drukarnia) | **średnioszary** z natury (proszek MJF z czynnikiem fuzyjnym daje kamienno‑szary, w środku czarny); odcień nie do wyboru, ale powtarzalny | mat z natury (Ra 4–6 µm po piaskowaniu); NIE zamawiać wygładzania parowego (daje połysk) | kolor jest w całej masie → nie ściera się; IPA: PA12 odporny („limited swell”); pory wchłaniają pył i tłuste ślady → z czasem plamy, czyścić IPA + miękka szczotka | 150–300 zł / 0,9–1,8 tys. zł (PL); JLC3DP ~70 zł + transport | 3–7 dni | Najbezpieczniejszy pod skaner; wygląd „wydruk” (2/5); cyfra reliefowa 0,6 w tym samym szarym = słabo widoczna → grawer CO₂ (ciemniejszy ślad) albo zostawić relief |
| **PA12 SLS surowy** (drukarnia) | **biały/kremowy** z natury — NIE spełnia D‑2 bez barwienia; barwienie na szary (kąpiel) daje jasno‑/średnioszary, ale barwnik wnika 0,25–0,5 mm | mat z natury (bardziej porowaty niż MJF) | barwnik w warstwie wierzchniej: rysy i intensywne tarcie IPA mogą odsłonić biel po roku; sam PA12 odporny | jak MJF + 10 % za barwienie | +1–2 dni | Wybierać MJF (szary w masie) zamiast SLS barwionego |
| **Al 6061 CNC + anoda** (frezarnia + anodownia) | trzy drogi: (a) **anoda twarda bez barwnika** → naturalnie ciemnoszara/grafit (odcień zależy od grubości warstwy i stopu; 6061 daje równą szarość), (b) **anoda dekoracyjna barwiona na szary** (jasno/średnio/grafit do wyboru na próbce u anodowni; w PL ZOBAL/IBF barwią „szary” i „grafit”), (c) anoda bezbarwna na piaskowanym Al → jasnoszary metaliczny (najjaśniejszy) | **piaskowanie szklane (lub korund drobny) PRZED anodą** — anoda powtarza fakturę podłoża; bez piaskowania frezowane lico jest półbłyszczące; po anodzie nie polerować | anoda = tlenek 10–25 µm (dekoracyjna) / 25–50 µm (twarda) z uszczelnieniem: IPA obojętny, kolor barwionej anody uszczelnionej trwały przy wycieraniu (blaknie tylko w UV po latach; grafit/czarny organiczny najmniej odporny — stąd przewaga anody twardej bez barwnika lub barwnika nieorganicznego); rysy nie odsłaniają innego koloru poza głęboką rysą do metalu | 700–1 600 zł / 3,5–7 tys. zł | 2–3 tyg. | Premium 5/5; grawer laserowy włóknowy daje biały trwały znak przez anodę; masa 160 g (pyt. 11 do Aidite) |
| **Żywica (DLP/LCD w firmie lub usługa)** | **jasno‑/średnioszara z pigmentu w masie**: dentystyczne żywice modelowe (BlueCast Model Grey, Liqcreate Model Pro Grey, Rodin TruModel) — pigment w całej objętości; Formlabs Grey Pro = szary mat, ale nasiąka IPA | mat z natury dla żywic modelowych („scan without spray”); bez lakierowania; po utwardzeniu UV nie polerować | kolor w masie → nie ściera się; **IPA**: Grey Pro +1,6 %, Tough 2000 +3,7–4,2 % masy (pęcznienie, zmiana wymiaru) → tylko do testu/prototypu; żywice modelowe — brak danych IPA, producenci przewidują mycie IPA świeżych wydruków, ale nie codzienne wycieranie; HDT 60–80 °C (płytki poranne 40–70 °C na granicy) | 25–40 zł materiału / — (samemu) | 1 dzień | Tylko płytka testowa skanera i prototypy pasowań — nie produkcja |

**Rekomendacja końcowa (D‑2):** produkcyjne n1–n6 = **CNC Al 6061, piaskowane szklanie, anoda twarda bez barwnika (grafit/ciemnoszary mat) z numerem grawerowanym laserem**; jeśli próba na skanerze pokaże zbyt małe pokrycie przy grafitowym odcieniu, ten sam proces z anodą dekoracyjną barwioną na **średnioszary** (odcień dobrany na próbce). Uzasadnienie: (1) skaner — mat z piaskowania i szary (nie czarny) odcień mieszczą się w jedynej udokumentowanej klasie „bez sprayu”, a anoda nie przeświecza i nie zmienia się z czasem; (2) czyszczenie — tlenek uszczelniony jest obojętny na IPA, nieporowaty (brak plam jak w PA12), kolor w warstwie 25–50 µm, nie na powierzchni; (3) stabilność — ±0,05 mm i 0,11 mm rozszerzalności na 50 K; (4) wygląd — ciężka, chłodna, jednolicie szara płyta z białym grawerem, biała cyrkonia kontrastuje, nic nie wygląda na wydruk. Wariant budżetowy spełniający D‑2 bez zmian w planie: **MJF PA12 surowy (średnioszary w masie)**, 0,9–1,8 tys. zł za 6 — jeśli próba Al nie przejdzie na skanerze albo koszt zostanie odrzucony. SLS biały barwiony i żywice odpadają z produkcji.

### 3.2 Uzasadnienie wyboru (Al 6061 anodowane ciemnoszare, mat)

- **Matowość**: piaskowanie szklane przed anodą daje równomierny mat; anoda twarda bez barwnika jest „slightly matte, dark grey” — to najbliższe udokumentowanej klasie „szary mat bez sprayu”. Barwienie na czarny i polerowanie wykluczone.
- **Brak przeświecania**: metal; żywice i cienki PA12 przy 5 MP i świetle niebieskim nie przeświecają w 8 mm, ale krawędzie dołków w żywicy bywają „miękkie” w skanie.
- **Stabilność wymiarowa**: ±0,05 mm z CNC, CTE 23,6 µm/m·K (0,11 mm na 96 mm przy 50 K; PA12 0,5 mm, POM 0,6 mm — odwracalnie, ale płytka poranna bywa ciepła przy skanie).
- **Czyszczenie**: IPA i wycieranie bez ograniczeń; brak porów (MJF wchłania pył w pory, biała płytka szarzeje).
- **Wygląd i odczucie**: ciemny, chłodny, ciężki (160 g) — „przyrząd pomiarowy”, nie „wydruk”; biała cyrkonia kontrastuje; grawer laserowy biały.
- **Ryzyka i ich obsługa**: (1) ciemna powierzchnia pochłania światło projektora → próba 1 szt. na skanerze z ustawieniem ekspozycji, w razie czego anoda jaśniejsza (szara barwiona) — anodownia dobiera odcień na próbce; (2) masa 160 g na stoliku — pyt. 11 do Aidite; (3) magnesy w kieszeniach Al klejone CA jak w planie (Al niemagnetyczny, Hall działa); (4) cena 3,5–7 tys. zł za 6 vs 0,9–1,8 tys. MJF — decyzja właściciela; (5) rowek pokrywki i faza — CNC bez problemu.

### 3.3 Wymagania dla interfejsu z wkładką (do DESIGN A)

1. Obrys płytki 96,0 × 96,0 (CNC ±0,05; MJF ±0,3) → otwór wkładki 96,6 zostaje; przy CNC luz można zmniejszyć do 96,3 (0,15/stronę) dla lepszej powtarzalności — tylko jeśli wkładka też CNC/dokładna; przy MJF wkładki zostawić 96,6.
2. Wycięcie D 5 × 5 w (+48, −48), przelotowe; kołek 4,4 × 4,4 × 5 na półce D, 0,5 od ścian otworu — bez zmian (blokuje obrót 90°/180°).
3. Półki narożne ≤ 13 × 13 (strefa płytki bez gniazd), wierzch półek tak, by spód płytki był ≤ 4 mm od lica czujnika Halla; dziś 2,5 (płytka) + 1,0 szczelina → 1,7 mm do struktury A3144.
4. Magnesy ø5 × 2 w kieszeniach ø5,2 × 2,2 od spodu w (±42, ±42) poza D; biegun S w dół; jeśli A9 (adapter skanera) dostanie 4. magnes w D (40,5, −40,5) — półka D bez czujnika, kołek nie koliduje (43,4…47,8).
5. Grubość płytki 8,0 — zmiana wysokości (np. Al 6 mm dla masy 120 g) przesuwa wierzch płytki o −2 i prześwit pokrywki; nie zalecam bez przeliczenia D4/D8.
6. Spód płytki płaski (bez stopek); płaskość ≤ 0,2 mm; brak reliefu od spodu.
7. Rowek pokrywki 1,0 × 0,8 na 4 bokach, środek 2,0 pod wierzchem, przerwany w D — bez zmian; garby pokrywki PETG nie rysują anody.
8. Jeśli znaczniki zmienią kształt (A3) lub dołki (A2) — wkładki NIE dotyczy; jeśli znaczniki zmienią pozycję (A4) — magnesy i kieszenie Halla zostają w (±42, ±42) (rozdzielić magnes od znacznika).
9. Masa płytki z pracami: PA12 60 g / Al 160 g + prace ≤ 100 g — półki 12 × 12 × 2,5 PA12 wytrzymują (naprężenie pomijalne).

### 3.4 Kolejność działań (propozycja)

1. Dziś: pomiar 20 realnych prac (zielone i spieczone) suwmiarką → potwierdzić lub obalić wniosek 4; jeśli potwierdzony — nowy D6 (A5) PRZED drukiem testowym.
2. Dziś: wydruk płytki testowej z szarej matowej żywicy (z bieżących plików lub z A5) — czeka na skaner.
3. Mail do Aidite: poprawić pyt. 5/14 (model, nie Multidie), dodać kąt kamer, „Fill holes” off, obciążenie stolika; nie czekać z resztą.
4. Po teście kryterium 8: zamówić próbkę A (Al ciemnoszary) i B (MJF szary) — 1 + 1 szt.
5. Po porównaniu na skanerze: seria 6 w wybranej technologii; przy Al — jedna geometria + numer grawerem (A1), dołki sferyczne (A2), czasze (A3) jeśli program gotowy.
