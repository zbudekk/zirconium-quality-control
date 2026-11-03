# Specyfikacja interaktywnego modelu 3D ramki (dla subagenta)

Źródło prawdy: `plan_ramki_v1.md` (sekcje 2, 3, 4, 7). Poniżej wyciąg geometrii gotowy do kodowania. Wszystkie wymiary w mm.

## Układ współrzędnych planu → three.js
Plan: X w prawo (od użytkownika), Y do tyłu, Z w górę; początek = środek obrysu korpusu na płaszczyźnie jego zewnętrznego dna; przód ramki = −Y.
three.js (Y‑up): `three.x = plan.x`, `three.y = plan.z`, `three.z = −plan.y` (przód ramki = +Z, w stronę kamery domyślnej).

## Materiały (wygląd „jak w rzeczywistości”)
- PA12 grafit (korpus, blat, rama dyfuzora, głowica, zaślepka): matowy, lekko ziarnisty, kolor #3b3e43, roughness 0,9, metalness 0.
- PA12 naturalny biały (wkładka, płytki, pokrywka, uchwyty kabli): #efede6, roughness 0,95.
- PCB zielone (#1f6b3a, roughness 0,6); PCB Bonnetu niebieskie (#1d4ea3); czarne złącza (#15161a).
- Dystanse mosiężne: #c8a24a, metalness 0,8, roughness 0,35.
- Dyfuzor: mleczna pleksi, MeshPhysicalMaterial transmission ~0,6 / opacity 0,75, #e8ecef.
- Diody: siatka 64 × 64 (raster 2,5) jako InstancedMesh małych kostek 1,8 × 1,8 × 0,8, emissive zielony/czerwony/zgaszony wg scenariusza (zielone pod gniazdami z pracami, 2–3 czerwone w wieczornej; cyfry „K 12” na przednim marginesie i „7” na prawym w porannej).
- Magnesy: #6b6f76 metaliczne; czujniki Halla TO‑92: czarne 4 × 1,5 × 5 z 3 nóżkami.
- Przycisk arkadowy: kołnierz chromowy ø34, grzyb ø30 żółty podświetlony (emissive) w wieczornej.
- Stopki gumowe: #202020.
- Kable: TubeGeometry po krzywych CatmullRom, grubość 1,2–2,5; kolory: DC czerwony/czarny 2 żyły, HUB75 taśma szara 20 mm szeroka (BoxGeometry zgięta w „Z” lub Tube płaski), Hall 3 cienkie (żółty/zielony/niebieski + czerwony/czarny), I2C 4 żyły, USB czarny.

## Części (nazwy = id w UI) i geometria

### 1. korpus (PA12 grafit) — 2 warianty napisu: W „RAMKA WIECZORNA”, P „RAMKA PORANNA”
- Obrys 200 × 200, wysokość 54,6 (Z 0…54,6); ściany 2,5; dno 3; pionowe krawędzie R 5; dolna krawędź R 3.
- Bossy panelu ø9 × 11 na dnie (Z 3…14) w (±60, ±60), otwór ø4 w górze (wkładka M3 mosiężna widoczna).
- Bossy Pi ø6 × 5 (Z 3…8) w (−88,5, ±24,5), (−30,5, ±24,5), wkładki M2,5.
- Bossy uchwytów kabli ø7 × 5 w (40, 70), (−40, 70).
- Szczelina karty SD w dnie 10 (X) × 16 (Y), środek (−91, 0), przelotowa.
- 2 szczeliny wlotowe w dnie 20 × 3, środki (−60, ±10).
- Szczeliny wentylacyjne 12 × 3 z daszkiem (półka 1,5 gruba, wysięg 2, pochylona 45° w dół nad górną krawędzią): tylna ścianka x = −63, −45, −27, −9, 9, 27, 45, 63 na Z 8 (oś); lewa i prawa ścianka y = −45, −27, −9, 9, 27, 45 na Z 8.
- Tylna ścianka (y = +100): kieszeń DC — otwór 36 × 24 (x −78…−42, Z 14…38, naroża R 3), za nim skrzynka zewn. x −80…−40, y 78…100, Z 12…40, ściany 2, otwarta tylko przez otwór; w dnie skrzynki (płaszczyzna y = 78) gniazdo DC panelowe ø12 oś (−60, Z 30), nakrętka po stronie wnętrza. Okno USB‑A panelowe 15 × 8 środek (50, Z 24) + 2 otwory ø3,2 w (50 ± 11, Z 24). 2 otwory ø3,2 (wkręty blatu) w (±60, Z 50).
- Przednia ścianka (y = −100): otwór przycisku ø30 środek (30, Z 22); 2 otwory ø2,8 w (−82, Z 38), (−58, Z 38) i otwór kabla ø4 (−70, Z 38) (głowica); napis wypukły 0,6 mm, litery 8 mm, środek (0, Z 46).
- Kieszenie zatrzasków blatu (od wewnątrz) 10 × 2,5 × 1,2 na środku każdej ściany, dolna krawędź Z 47,6.
- Stopki gumowe ø10 × 4 pod spodem, środki 12 mm od krawędzi (Z −4…0).
- 4 żebra 2 × 6 na dnie od bossów panelu ku narożnikom (po przekątnych), przerwane w strefie Pi.

### 2. pi (Raspberry Pi 4 B) + 3. bonnet (Adafruit RGB Matrix Bonnet)
- Pi PCB 85 × 56 × 1,6, narożnik (x −92, y −28) → PCB zajmuje x −92…−7, y −28…28, Z 8…9,6. Krawędź z kartą SD przy x = −92 (karta wystaje 2 mm w −X, Z 8…9), porty USB (2 × podwójne, 15 × 17 × 16) i Ethernet przy x = −7 krawędzi, złącze GPIO 2 × 20 (51 × 5 × 8,5) wzdłuż y = +25 (od x −88 do −37), procesor z radiatorem 15 × 15 × 6 w (−60, 0), gniazdo USB‑C i HDMI przy y = −28.
- Bonnet: listwa żeńska GPIO 51 × 5 × 11 na pinach Pi (Z 9,6…20,6), PCB 65 × 56 × 1,6 na Z 20,6…22,2 (x −88…−23, y −28…28), złącze HUB75 IDC 16 (20 × 9 × 9) na PCB przy x −85…−65, y 10…19; gniazdo DC 5,5/2,1 (9 × 14 × 11) na krawędzi x = −88, y −20; terminal śrubowy 2‑pin (10 × 8 × 10) obok; stos kończy się na Z 34. Kątowa listwa goldpin 1 × 10 dolutowana przy y = +25 (wyprowadzenie GPIO).
- W porannej: odbiornik USB nano 19 × 15 × 6 w dolnym porcie USB Pi; w obu: kabel USB 30 cm z górnego portu do gniazda USB panelowego w tylnej ściance.

### 4. dystanse (4 szt.) — mosiądz M3 męsko‑żeński, ø5 (sześciokąt) × 35, Z 14…49 w (±60, ±60); wkręty M3 × 8 od spodu korpusu (łeb ø5,5 widoczny w pogłębieniu dna).

### 5. panel (HUB75 64 × 64 P2.5)
- PCB 160 × 160 × 1,6 na Z 49…50,6 (środek 0,0), czarna maska + diody 64 × 64 raster 2,5 na Z 50,6…52,6 (lico diod Z 52,6).
- Od spodu: 2 złącza HUB75 IDC 16 (20 × 9 × 9) w (−45, 0) i (45, 0), złącze zasilania VH4 (15 × 8 × 10) w (0, 40), 6 kondensatorów ø6 × 10 wzdłuż y = −40; najniższy element sięga Z 37 (12 mm pod PCB). Otwory montażowe ø3 w (±60, ±60).
- Taśma HUB75 16‑pin od Bonnetu do złącza IN (−45, 0), złożona w „Z” między Z 34 a 37.
- Kabel zasilania VH4 od terminalu Bonnetu do (0, 40).

### 6. rama_dyfuzora (PA12 grafit) — kołnierz 170 zewn. / 161 wewn., wysokość 6, Z 48,6…54,6; 4 uszy ø8 × 6 w (±86, ±86) z otworem ø3,4, połączone mostkiem 4 mm; wkręty M3 × 8 od dołu w bossy blatu.

### 7. blat (PA12 grafit)
- Płyta 200 × 200 × 4, Z 54,6…58,6, R 5 pionowe, R 1,5 górna krawędź.
- Kieszeń dyfuzora 162 × 162 × 2 od góry (Z 56,6…58,6), otwór przelotowy 158 × 158.
- Kołnierz pod spodem: obrys 194,4 × 194,4, grubość 2, wysokość 10 (Z 44,6…54,6), R 4,7; 4 haczyki zatrzaskowe 8 szer., występ 1,2 na zewnątrz, na środkach boków, 1 mm nad dolną krawędzią; nacięcia 1 mm po bokach haczyka.
- 2 słupki 6 × 6 × 10 wewnątrz tylnego kołnierza w x = ±60 (y ≈ 95), otwór poziomy ø4 na Z 50 (wkręty z tylnej ścianki).
- 4 bossy ø8 × 6 pod spodem w (±86, ±86) (rama dyfuzora).
- Otwory kołków wkładki ø3,3 w (±58, 93,5); kieszenie magnesów ø5,4 × 2,3 od góry w (±58, 86) z magnesem ø5 × 2; szczeliny kabli 4 (X) × 8 (Y) w (±66, 90).
- Żebro obwodowe 2 × 6 pod spodem wokół kieszeni (obwód 166 × 166).

### 8. dyfuzor — mleczna pleksi 160 × 160 × 2, Z 56,6…58,6, rogi sfazowane 1 mm.

### 9. wkladka (PA12 biały)
- Rama: zewn. 104,6 × 104,6, otwór 96,6 × 96,6, wysokość 6 (Z 58,6…64,6), faza 1 × 45° na górnej krawędzi wewnętrznej.
- 4 półki narożne 12 × 12 × 2,5 wewnątrz otworu (Z 58,6…61,1) w narożach A (−48,3…−36,3, −48,3…−36,3), B (lewy tył), C (prawy tył), D (prawy przód).
- Półki A, B, C: kieszeń przelotowa 5 (X) × 5,5 (Y) ze środkiem (−42, −42), (−42, 42), (42, 42); w niej czujnik Halla TO‑92 leżący płasko licem do góry; kanał 2,5 × 1,2 pod półką po przekątnej do ścianki i przelot w ściance.
- Półka D: kołek 4,4 × 4,4 × 5 nad półką (Z 61,1…66,1) przy narożniku (42, −42), ścianki kołka 0,5 od ścian otworu; faza 1 na wierzchołku.
- Wycięcie palcowe 30 szer. (x −15…15) w przednim boku ramy (y −48,3…−52,3), pełna wysokość.
- Rowek kablowy 1,5 × 1,5 na zewnętrznej dolnej krawędzi lewego, tylnego i prawego boku.
- 2 uszy 14 (X) × 43,7 (Y) × 3 od y = 52,3 do 96, środki x = ±58 (Z 58,6…61,6); w każdym kołek ø3 × 3,5 w dół w (±58, 93,5), otwór ø5,4 z magnesem ø5 × 2 w (±58, 86); kanał kablowy 2 × 1,2 pod uchem przy x = ±64 do (±66, 90).
- Napis wypukły „PRZÓD” 4 mm + strzałka na górze przedniego boku.
- 3 kable Halla (3 żyły każdy) od czujników rowkiem do uszu i w dół przez szczeliny blatu (±66, 90), dalej wzdłuż tylnej ściany do płytki proto w uchwycie (40, 70).

### 10. plytka_wieczorna i 11. plytka_poranna (PA12 biały), 96 × 96 × 8, wierzch na Z 69,1 (spód Z 61,1 na półkach). Układ lokalny: środek wierzchu, x w prawo, y do tyłu.
- Wspólne: 3 stożki znaczników ø5 × 3 (wierzchołek w dół) w A (−42, −42), B (−42, 42), C (42, 42); wycięcie 5 × 5 przelotowe w D: x 43…48, y −48…−43; dołki kodu ø2 × 1 w (−37, −45), (−37, −42), (−37, −39) (pokazać wszystkie 3); kieszenie magnesów od spodu ø5,2 × 2,2 współosiowe ze znacznikami A, B, C (magnes ø5 × 2 w A dla nr 1); numer wypukły 0,6 (cyfra 5 mm) w (39,5, −44,5): wieczorna „1”, poranna „4”; rowek 1 × 0,8 na bokach 2 mm pod wierzchem; krawędzie pionowe R 1, górne faza 0,5.
- Gniazda: stożek, ścianka 15° od pionu, głębokość 4, dno ø (d − 2,14), otwór przelotowy ø3 w osi. Rynienki: obrys stadion l × w, ścianki 15°, głębokość 4, 4 otwory ø3 na osi w rozstawie 12 (wieczorna) / 10 (poranna) symetrycznie.
- Wieczorna (środki, y od przodu ujemne):
  - y −40,5: ø9 x = −30, −18, −6, 6, 18, 30
  - y −28,5: ø9 x = −36, −24, −12, 0, 12, 24, 36
  - y −15: ø12 x = −37,5, −22,5, −7,5, 7,5, 22,5, 37,5
  - y +1,5: ø15 x = −36, −18, 0, 18, 36
  - y +19,5: rynienka 60 × 15, x = 0
  - y +37,5: rynienka 60 × 15, x = 0
- Poranna:
  - y −41,25: ø7,5 x = −26,25, −15,75, −5,25, 5,25, 15,75, 26,25
  - y −30,75: ø7,5 x = ±5,25, ±15,75, ±26,25, ±36,75
  - y −20,25: ø7,5 jak wyżej
  - y −8,5: ø10 x = −39, −26, −13, 0, 13, 26, 39
  - y +5,75: ø12,5 x = ±7,75, ±23,25, ±38,75
  - y +21,5: rynienka 50 × 13, x = 0
  - y +37,5: rynienka 50 × 13, x = 0
- Prace (opcjonalnie, przełącznik): uproszczone korony (LatheGeometry, kremowe #f3efe3) w części gniazd, most na rynience.

### 12. pokrywka (PA12 biały) — 99,6 × 99,6 × 20, wierzch 2, kołnierz 1,5, wnęka 96,6 × 96,6 × 18; 4 garby zatrzaskowe 10 × 0,7 wewnątrz kołnierza na środkach boków 2 mm nad dolną krawędzią; 6 otworów ø4 w wierzchu (siatka 2 × 3, rozstaw 30); wycięcia palcowe 30 × 3 na dolnej krawędzi przedniego i tylnego boku; napis „GÓRA”. Położenie na płytce: dół kołnierza Z 65,1, wierzch Z 85,1.

### 13. glowica (PA12 grafit, tylko W) — 34 (X) × 26 (Y, przed ścianką) × 16 (Z), środek (−70, −100 … −126, 38), górna płaszczyzna pochylona 15° (przód niżej), R 3; okienko 8 × 6 w górnej płaszczyźnie; wewnątrz moduł VL53L1X 25 × 18 × 4 (PCB niebieskie, czujnik 5 × 3 czarny pod okienkiem); 2 bossy ø6 w tylnej płaszczyźnie; kabel I2C 4 żyły przez otwór ø4 w ściance do listwy Bonnetu.

### 14. przycisk (tylko W) — arkadowy ø30 w (30, −100, 22): grzyb ø30 wystaje 8 mm przed ścianę, kołnierz ø34 × 2, korpus za ścianą ø29 × 35 z mikroprzełącznikiem i LED; 4 przewody do płytki proto.
### 15. zaslepka (tylko P, PA12 grafit) — kołnierz ø34 × 2,5, korpus ø29,5 × 4, 2 haczyki.

### 16. uchwyt_kabli (2 szt., PA12 biały) — 40 × 20 × 12 na bossach (40, 70), (−40, 70): stopa 40 × 20 × 2,5 z wkrętem M3, rowek 1,8 × 4 trzymający pionowo płytkę proto 30 × 20 (zielona, z 3 rezystorami i złączami JST) — tylko w uchwycie (40, 70); grzebień 1,5 z 3 szczelinami 4 × 8 na opaski.

### 17. gniazda tylne — gniazdo DC panelowe (czarny walec ø8 × 14 + nakrętka sześciokątna 11 od wnętrza) w dnie kieszeni; gniazdo USB‑A panelowe (flansza 24 × 14, czarne, z zaślepką gumową) w oknie (50, Z 24); od zewnątrz: wtyk kątowy DC 5,5/2,1 (czarny, 10 × 14 korpus, kabel w dół) wchodzący w kieszeń.

### 18. kable (grupa) — DC: od gniazda (−60, 78, 30) wzdłuż lewej ściany do gniazda Bonnetu (−88, −20, 27); HUB75 taśma: Bonnet (−75, 15, 30) → panel IN (−45, 0, 37); VH4: terminal Bonnetu (−85, −10, 27) → panel (0, 40, 37); USB: Pi górny port (−7, 10, 20) → gniazdo tylne (50, 100, 24); Hall ×3: uszy wkładki → szczeliny blatu (±66, 90, 58) → uchwyt (40, 70, 12) → listwa Bonnetu (−60, 25, 23); I2C: listwa → otwór (−70, −100, 38); przycisk: (30, −100, 22) → uchwyt (40, 70) → listwa.

## Wymagane funkcje strony
1. **Dwa tryby:** „Z zewnątrz” (złożona ramka na blacie‑stole, realistyczne oświetlenie: światło kierunkowe + hemisphere + lekkie AO przez ciemniejszy spód; płytka z pracami we wkładce, diody świecą) i „Rozbiórka”.
2. **Obrót całości:** OrbitControls (obrót, zoom, przesuwanie), damping; przyciski widoków: przód, tył, lewo, prawo, góra, spód, izometria. W trybie „Z zewnątrz” spód też musi być dostępny (stopki, szczeliny, śruby panelu, szczelina SD).
3. **Rozbiórka:** suwak „Rozłożenie 0–100 %” rozsuwa części w pionie w kolejności montażu (pokrywka → płytka → wkładka → blat+dyfuzor+rama → panel → dystanse → Pi+Bonnet → kable → korpus), z liniami prowadzącymi (przerywane) od części do jej miejsca; przyciski „Krok ◀ ▶” z opisem kroku (z sekcji 9 planu); lista części z checkboxami widoczności i przyciskiem „izoluj”.
4. **Wybór części:** klik (raycaster) podświetla część (emissive) i otwiera panel: nazwa, materiał, gabaryt, położenie Z, krótki opis funkcji; przyciski „Obróć X/Y/Z ±90°” i suwaki obrotu (−180…180°) działające na wybraną część; „Centruj kamerę na części”; „Przywróć położenie”; podwójny klik = izolacja (inne części półprzezroczyste 15 %).
5. **Przekrój:** suwak płaszczyzny tnącej (X lub Y) z `clippingPlanes` włączany przełącznikiem — żeby zajrzeć do środka bez rozbierania.
6. **Wariant W/P:** przełącznik; zmienia napis, przycisk/zaślepkę, głowicę, płytkę (wieczorna/poranna), odbiornik USB, scenariusz diod.
7. **Etykiety:** przełącznik etykiet (sprite z nazwą części, zawsze zwrócone do kamery), skalowane z odległością.
8. **Wymiary:** przełącznik „Wymiary” rysuje główne wymiary (200, 58,6, 96, 160) jako linie z tekstem.
9. UI po polsku, czytelna na telefonie (panel boczny zwija się pod przyciskiem), tryb jasny/ciemny (tokeny CSS), 60 fps na laptopie (InstancedMesh na diody, kable z niewielką segmentacją, BufferGeometry.merge gdzie się da).

## Zasady techniczne strony (kontrakt artefaktu Claude)
- Plik `.html` BEZ `<!doctype>`, `<html>`, `<head>`, `<body>` (hosting dodaje szkielet). Na początku pliku: `<title>Ramka 3D</title>` i `<meta name="claude:viewport-fit-sides" content="cover">`, potem `<style>`, markup, `<script>`.
- Skrypty zewnętrzne WYŁĄCZNIE z cdnjs.cloudflare.com (lub cdn.jsdelivr.net/npm/, unpkg.com), z dokładną wersją. Zalecane: `https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js` + `https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/examples/js/controls/OrbitControls.js` (globalne `THREE`, bez modułów ES). Brak CSG — otwory robić przez `THREE.Shape` z `holes` + `ExtrudeGeometry` (ściany, blat, płytka), stożki gniazd przez `LatheGeometry`/`CylinderGeometry` wstawione w otwory, zaokrąglenia przez `Shape.absarc`/`RoundedBoxGeometry` (examples/js/geometries/RoundedBoxGeometry.js w r128).
- Żadnych fetch/XHR, obrazów z sieci, iframe; wszystko inline. `alert/confirm/prompt` nie działają.
- Kolory jako tokeny CSS na `:root`, wersja ciemna pod `@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){…}}` i `:root[data-theme="dark"]{…}`; `body` z jawnym tłem z tokenu. Gutter boczny `padding-left:max(16px,env(safe-area-inset-left,0px))` i analogicznie prawy; bez poziomego scrolla.
- Canvas three.js dopasowany do kontenera (ResizeObserver), `devicePixelRatio` ≤ 2.
- Strona kompletna po załadowaniu (scena widoczna od razu, bez czekania na interakcję).
