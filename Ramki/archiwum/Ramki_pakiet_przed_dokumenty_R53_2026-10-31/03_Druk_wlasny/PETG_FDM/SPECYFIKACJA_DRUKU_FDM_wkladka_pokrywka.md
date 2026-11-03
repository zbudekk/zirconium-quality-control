# Specyfikacja druku FDM — ramka_wkladka_v2.stl i ramka_pokrywka_v2.stl

Data: 2026-10-27. Dwa pliki, oba PETG, dysza 0,4, warstwa 0,2. Oba drukują się **bez podpór** w podanej orientacji.

## Wspólne ustawienia (obie części)

| Parametr | Wartość | Uwaga |
|---|---|---|
| Materiał | PETG, kolor biały lub naturalny | **suszony** przed drukiem (mokry PETG = pęcherze, słabe warstwy, nitkowanie) |
| Dysza | 0,4 mm | |
| Warstwa | 0,2 mm; pierwsza 0,2–0,25 | |
| Temperatura dyszy | 230–245 °C | według karty filamentu; nitkowanie → obniżyć o 5 °C |
| Temperatura stołu | 75–85 °C | |
| Prędkość | ≤ 60 mm/s; obrysy zewnętrzne 30–40 mm/s; pierwsza warstwa 20 mm/s | |
| Chłodzenie | 30–50 % | nie 100 % — PETG traci spójność warstw |
| Obrysy (perimetry) | 4 | |
| Warstwy pełne góra / dół | 5 / 5 | |
| Wypełnienie | 40 % gyroid lub cubic | |
| Podpory | **wyłączone** | |
| Brim | 5 mm | obie części są płaskie i szerokie; brim pilnuje rogów przed unoszeniem |
| Kompensacja otworów XY („hole horizontal expansion”) | +0,1 mm | PETG zawęża otwory i wnęki; patrz kontrola po druku |
| Adhezja stołu | PEI / szkło + klej w sztyfcie | PETG na gołym PEI potrafi przykleić się za mocno — cienka warstwa kleju jako separator |
| Z-seam | z tyłu (aligned, rear) | żeby szew nie wypadł na zatrzaskach ani na kołku |

Stół: minimum **150 × 160 mm** (wkładka 130 × 148 + brim). Pokrywka 100 × 100 wejdzie wszędzie.

---

## 1. ramka_wkladka_v2.stl — wkładka (ramka na płytkę)

**Ilość: 2 + 1 zapas.** Czas ok. 2,5–3 h/szt., ok. 25 cm³ (ok. 32 g).

**Co to jest:** kwadratowa rama 104,6 × 104,6 × 6 mm z dwoma „uszami” z tyłu (obrys 130 × 148 mm). W narożnikach otworu 4 małe półki; na trzech kieszenie na czujniki, na czwartej kwadratowy kołek 4,4 × 4,4 × 5 mm. Od spodu rowki na kable i 2 kołki ø3 × 3,5 w uszach.

**Orientacja: spodem (płaską stroną) na stole, kołek 4,4 i półki do góry.**

**Problem do rozwiązania w slicerze:** pod spodem uszu sterczą 2 kołki ø3 × 3,5 mm (w punktach x = ±58, y = 93,5). Jeśli położysz część „jak jest”, slicer postawi ją na czubkach tych kołków i cała rama zawiśnie 3,5 mm nad stołem. Rozwiązanie (wybierz jedno):

- **Zalecane — odciąć kołki:** narzędzie *Cut* na wysokości **3,5 mm od dołu**, zostawić **górną** część (cała wkładka bez 2 kołków). Drukować płasko, bez podpór. Po druku wywiercić od spodu w każdym uchu otwór ø2,9 × 3 mm w (±58, 93,5) (miejsce po kołku będzie widoczne jako kółko w pierwszej warstwie) i wkleić CA kawałek filamentu ø3 (lub pręt ø3) długości 6,5 mm — 3 mm w otworze, 3,5 mm wystaje. Kołki tylko pozycjonują wkładkę w blacie, nie przenoszą siły.
- **Alternatywa — podpory malowane:** zostawić kołki, część na stole stoi na nich, podpory *paint‑on* tylko pod ramą i uszami (nie w kanałach). Gorsze: podpory zalewają kanały kabli i trzeba je potem czyścić.

**Krytyczne cechy, których nie wolno zgubić:**

| Cecha | Wymiar | Po co | Kontrola |
|---|---|---|---|
| Otwór wewnętrzny | 96,6 × 96,6 mm | płytka 96 × 96 ma mieć luz 0,3 na stronę | suwmiarka: 96,5–96,8 OK; < 96,5 → kompensacja +0,2 i jeszcze raz, albo papier 240 na ściankach |
| Półki narożne | 12 × 12 × 2,5 mm, góra na Z = 2,5 | płytka na nich leży | wszystkie 4 na tej samej wysokości ±0,1 |
| Kieszenie czujników (3 szt.) | 5,0 × 5,5 mm przelotowe, w półkach A, B, C | czujnik Halla TO‑92 (4 × 5 × 1,5) ma wejść lekko ciasno | wkładka czujnika / klocek 4 × 5 wchodzi palcem |
| Kołek kwadratowy | 4,4 × 4,4 × 5 mm, faza 1 mm na czubku | orientacja płytki (wycięcie 5 × 5) | 4,3–4,5 mm; grubszy → pilnik |
| Kanały kabli pod spodem | 2,5 × 1,0 (pod półkami), 2,5 × 1,5 (zewn. dolna krawędź ramy), 2 × 1,2 (pod uszami) | 3 żyły AWG 28 | drożne na całej długości, bez zalanych mostków w pierwszej warstwie — **elephant foot compensation 0,1–0,15 mm** |
| Otwory w uszach | ø5,4 przelotowe, w (±58, 86) | magnes ø5 × 2 wklejany | magnes wchodzi bez siły (5,3–5,5 OK) |
| Faza górnej krawędzi otworu | 1 × 45° | naprowadza płytkę | widoczna, równa |
| Wycięcie palcowe z przodu | 30 mm, pełna wysokość | | |
| Strzałki ▼ relief 0,6 | przód, 2 szt. | | czytelne, niezalane |

**Ustawienia specyficzne dla wkładki:**

- Elephant foot compensation: 0,1–0,15 mm (kanały kabli w pierwszej warstwie muszą zostać otwarte).
- „Detect thin walls” / „thin wall detection” włączone (ścianki 1,5 mm nad kanałami).
- Wypełnienie 40 % gyroid; obrysy 4 → ściany ramy 4 mm będą w praktyce prawie pełne, dobrze.
- Nie skalować. Nie „naprawiać” STL automatycznie bez sprawdzenia (plik jest poprawny).
- Pierwsza warstwa: szeroka płaska rama + 2 uszy po 14 mm, więc kontrola przyczepności uszu — brim 5 mm obowiązkowy.

**Po druku:** usunąć brim, przeczyścić 3 kieszenie i kanały (igła/wiertło 2,5), sprawdzić otwór 96,6 suwmiarką w dwóch osiach, sprawdzić, czy półki nie mają „garbów” na szwie Z.

---

## 2. ramka_pokrywka_v2.stl — pokrywka płytki

**Ilość: 4.** Czas ok. 3–4 h/szt., ok. 30 cm³ (ok. 38 g).

**Co to jest:** nakładka 99,6 × 99,6 × 20 mm: pełny wierzch 2 mm, ścianki (kołnierz) 1,5 mm, wnęka 96,6 × 96,6 × 18 od dołu. Na wewnętrznej stronie ścianek 4 garby zatrzaskowe (0,7 mm występu, 10 mm szerokie, 2 mm od dolnej krawędzi), które wskakują w rowek płytki. Na dole przodu i tyłu wycięcie 30 × 3 mm na palec.

**Orientacja: wierzchem (pełną płytą 2 mm) na stole, otwartą wnęką do góry.** Czyli jeśli slicer wczyta plik „jak pudełko dnem do góry”, to już jest dobrze. Zero podpór: garby zatrzasków są poziomymi guzkami o nawisie poniżej 45°, drukują się same.

**Krytyczne cechy:**

| Cecha | Wymiar | Po co | Kontrola |
|---|---|---|---|
| Wnęka wewnętrzna | 96,6 × 96,6 mm | płytka 96 × 96, luz 0,3 na stronę | suwmiarka 96,5–96,8; za ciasno → kompensacja +0,2 |
| Ścianka (kołnierz) | 1,5 mm, wysokość 18 | musi się sprężynować przy nakładaniu | **4 obrysy przy 0,4 → 1,6 mm, czyli ścianka = same obrysy, bez wypełnienia** — to zamierzone |
| Garby zatrzasków (4 szt.) | występ 0,7 mm, szer. 10, czubek R 0,4, 2 mm nad dolną krawędzią; lewy i prawy bok na środku, przód x = +25, tył x = −25 | wchodzą w rowek 1,0 × 0,8 w płytce | muszą być gładkie, bez nitek; szew Z nie na garbie |
| Wierzch | 2 mm pełny = 10 warstw | | bez dziur, 5 warstw dolnych + obrysy wystarczą |
| Wycięcia na palec | 30 × 3 mm, dolna krawędź przodu i tyłu | | |
| Wysokość całkowita | 20 mm | nad pracą zostaje 14 mm | |

**Ustawienia specyficzne dla pokrywki:**

- Obrysy 4 (ścianka 1,5 mm = ~4 linie 0,4; slicer może dać 3 linie + wąski gap fill — oba OK, byle bez pustki w środku ścianki).
- „Thin wall detection” / „gap fill” włączone.
- Z-seam: aligned, na jednym z rogów (nigdy na środku boku — tam są garby).
- Chłodzenie 30–50 % (sprężystość zatrzasków zależy od spójności warstw).
- Wypełnienie dotyczy tylko płyty wierzchu — i tak będzie pełna; można zostawić 40 %.
- Pierwsza warstwa to kwadrat 99,6 × 99,6 — równy stół, brim 5 mm, bez przeciągów.

**Po druku:** nałożyć na płytkę (albo na prototyp, albo na klocek 96 × 96 × 8 mm z rowkiem). Ma wejść bez siły i trzymać po odwróceniu. Za ciasno → garby przeszlifować papierem 400. Za luźno → ponowny druk z kompensacją +0,1 mniej (wnęka ciaśniejsza).

---

## Kolejność i test

1. **Najpierw 1 wkładka.** Sprawdzić otwór 96,6, kieszenie 5 × 5,5, kołek 4,4. Jeśli wymiary trafione → drukować resztę.
2. **Potem 1 pokrywka.** Sprawdzić wnękę 96,6 i zatrzaski.
3. Jeśli obie wyszły, **pełna seria: 3 wkładki + 4 pokrywki** (ok. 20 h łącznie).

Materiał na całość: ok. 250 g PETG (jedna szpulka 1 kg wystarczy z dużym zapasem).
