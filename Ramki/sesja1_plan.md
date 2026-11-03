# Ramki świetlne i płytki do stanowiska kontroli cyrkonii — sesja 1 z 2: plan budowy

## 0. Jak masz pracować w tej sesji

Jesteś inżynierem mechanikiem i elektronikiem w jednej osobie. Projekt jest podzielony na dwie osobne sesje:

- **Sesja 1 (ta): plan budowy i wszystkie decyzje projektowe.**
- **Sesja 2 (później, w nowym kontekście): pliki** — skrypt Blendera, STL, render, arkusze. Sesja 2 dostanie wyłącznie Twój plan i tę samą specyfikację co Ty (sekcje 1–9 poniżej). Nie zobaczy tej rozmowy: czego nie zapiszesz w planie z konkretną liczbą, tego nie będzie wiedziała.

W tej sesji nie piszesz skryptu Blendera i nie tworzysz STL, renderów ani arkuszy zamówienia. Kończysz na planie.

### 0.1 Co masz oddać

Jeden plik **`plan_ramki_v1.md`** w folderze roboczym (jeśli nie możesz zapisywać plików — całość w odpowiedzi, w jednym bloku do skopiowania). Sekcje w tej kolejności:

1. **Założenia** — numerowane (Z1, Z2…), każde z jednym zdaniem uzasadnienia. Tu trafia wszystko, czego brakuje w specyfikacji.
2. **Decyzje projektowe** — numerowane (D1, D2…), w tym co najmniej: wariant obudowy (wysoki ok. 200 × 200 × 55–60 mm albo niski ok. 200 × 270 × 35 mm — tabela porównawcza i jedna rekomendacja; sesja 2 modeluje tylko rekomendowany), technologia i materiał każdej części, liczba i rozmiary gniazd obu płytek, sposób mocowania blatu, położenie Pi, system numeracji płytek, rozstrzygnięcia z pkt 0.3.
3. **Tabela parametrów** — każdy wymiar, od którego zależy geometria: nazwa w `snake_case` (sesja 2 użyje dokładnie tych nazw jako stałych na górze skryptu), wartość, jednostka, źródło (`spec`, `Zn` albo `DO ZMIERZENIA`), opis. Wymiary z sekcji 9 dostają wartość domyślną i znacznik `DO ZMIERZENIA` — model ma powstać na wartościach domyślnych, a po pomiarze wystarczy podmienić liczby.
4. **Specyfikacja części do zamówienia** — najważniejsza sekcja, bo sesja 2 modeluje wyłącznie z niej. Najpierw raz zdefiniuj układ współrzędnych (początek, osie, gdzie jest przód ramki). Potem dla każdej części z sekcji 6 osobny podrozdział: nazwa pliku `ramka_<część>_v1.stl`, funkcja, gabaryt, lista cech z wymiarami i położeniem (przez nazwy parametrów z tabeli), luzy i pasowania, z którą częścią i cechą się łączy, orientacja do druku, ilość, materiał, kolor, wykończenie.
5. **Lista zakupów** — element, model lub kluczowe parametry, ilość na 2 ramki, przybliżona cena w zł, gdzie kupić (sklepy polskie lub AliExpress). Jeśli masz dostęp do wyszukiwania, sprawdź aktualne ceny; jeśli nie — zaznacz, że są orientacyjne.
6. **Narzędzia.**
7. **Struktura wewnętrzna obudowy** — mocowania, gniazda na wkładki gwintowane, prowadzenie kabli, wentylacja; z wymiarami.
8. **Elektronika i jej montaż** — tabela połączeń (element → sygnał → pin Pi lub złącze → przewód) dla zasilania, panelu, 3 czujników Halla, VL53L1X, przycisku z podświetleniem i odbiornika klawiatury. Sprawdź, które piny GPIO zajmuje RGB Matrix Bonnet, i przydziel pozostałym elementom wyłącznie wolne piny; ewentualne konflikty wypisz.
9. **Kolejność składania i testy** — kroki z sekcji 8 rozpisane szczegółowo; po każdym etapie test z jasnym kryterium zaliczenia.
10. **Formularz pomiarów** — sekcja 9 jako lista do wypełnienia: co zmierzyć, czym, nazwa parametru z tabeli, wartość domyślna, pole na wynik.
11. **Wstępny koszt części zamawianych** — z gabarytów, w dwóch wariantach: najtańszy (PA12 naturalny, bez barwienia) i pokazowy (barwienie, wygładzanie). Dokładny koszt z objętości STL policzy sesja 2.
12. **Przekazanie do sesji 2** — lista plików, które sesja 2 ma wytworzyć, sprawdzenia geometrii, które musi wykonać, i drobne kwestie, które może rozstrzygnąć sama.

### 0.2 Zasady

- Nie zadawaj pytań — tam, gdzie brakuje danych, przyjmij rozsądne założenie i wpisz je do „Założeń”.
- Wszystko po polsku; jednostki metryczne; zero płatnych bibliotek i programów.
- Każdy wymiar w planie to jedna liczba („4 mm”, nie „3–5 mm”). Tam, gdzie specyfikacja podaje zakres, wybierz wartość i wpisz ją do tabeli parametrów. Zakresy zostają tylko przy cenach.
- Pokaż rachunki spójności: łańcuch wysokości w obudowie, płytka we wkładce, wkładka w oknie blatu, panel na słupkach, odległość magnes–czujnik ≤ 4 mm, szerokość odsłoniętego marginesu matrycy, zgodność z zasadami 4.8.

### 0.3 Do rozstrzygnięcia w planie (niespójności w specyfikacji)

1. **Ciasne narożniki.** Znaczniki ø5, wycięcie 5 × 5, kieszenie magnesów, dołki kodu i numer płytki trafiają w narożniki, a strefa gniazd 90 × 90 na płytce 96 × 96 zostawia tylko 3 mm brzegu. Wyznacz narożne pola wyłączone z gniazd i rachunkiem pokaż, że zakładana liczba gniazd i rynienek mieści się przy ściankach ≥ 3 mm. Jeśli nie — zmniejsz liczbę gniazd, nie zmieniaj rozmiaru płytki (wyznacza go skaner).
2. **Czujniki Halla pod płytką.** Wkładka gniazda to rama wokół płytki, a czujnik ma leżeć ≤ 4 mm od magnesu w spodzie narożnika płytki. Zaprojektuj, jak czujnik trafia pod narożnik (np. narożna półka wkładki pod płytką) i ile pikseli to zasłania.
3. **Typ czujnika Halla.** SS49E jest analogowy, a Raspberry Pi nie ma wejść analogowych — wybierz czujnik cyfrowy albo uzasadnij przetwornik ADC. A3144 (cyfrowy, otwarty kolektor) wymaga zasilania ≥ 4,5 V: zasilanie z 5 V, podciąganie wyjścia wyłącznie do 3,3 V.
4. **Wysokość pokrywki.** Ustal, czy 4 mm luzu liczy się nad gniazdami, czy nad najwyższą pracą — korony w gniazdach głębokości 4 mm wystają ponad płytkę. Przyjmij maksymalną wysokość pracy jako parametr i z niej wylicz wysokość pokrywki.

---

# Specyfikacja (wspólna dla obu sesji)

**Nic nie drukujemy sami.** Płytki i wszystkie części obudów zamawiamy zewnętrznie (usługa druku 3D lub CNC), więc nie ma ograniczenia pola roboczego drukarki, obudowa może być jednoczęściowa, a projekt ma być zgodny z zasadami projektowania pod SLS/MJF (sekcja 4.8). Potrzebujemy wyłącznie plików.

Ta specyfikacja ma pierwszeństwo przed załączonym planem wdrożenia, jeśli coś się różni (zmiany: brak paska LED, bezprzewodowa klawiatura, Raspberry Pi zamiast ESP32, magnesy i czujniki Halla zamiast NFC, obie płytki kwadratowe i zamawiane zewnętrznie).

## 1. Do czego służą ramki

Stanowisko kontroluje korony i mosty z cyrkonii. Prace leżą w gniazdach **płytki**; płytka jedzie do skanera laboratoryjnego, program na laptopie analizuje skan i decyduje, które gniazdo podświetlić. Ramka to „dom” płytki poza skanerem: pod płytką leży matryca diod, które świecą przez dno gniazd.

- **Ramka wieczorna** stoi na parapecie obok skanera. Po skanie świeci na czerwono gniazda z podejrzeniem ubytku (technik bierze do ręki tylko te), na zielono resztę. Ma czujnik gestu (machnięcie dłonią = „Skanuj”) i jeden fizyczny przycisk.
- **Ramka poranna** stoi w innym pomieszczeniu, gdzie rano rozkłada się spieczone prace do kuwet. Po położeniu płytki pokazuje numer bieżącej kuwety i liczbę jej prac na marginesie matrycy wokół płytki, a pod pracami tej kuwety świeci zielone diody. Obsługa z **bezprzewodowej klawiatury numerycznej** (Enter = następna kuweta, cyfry = wpisz numer kuwety, Backspace = cofnij, osobny klawisz = „Zamknij piec”).

Obie ramki rozmawiają z laptopem przez firmowe Wi‑Fi (laptop jest serwerem; ramka pyta o plan płytki i odsyła potwierdzenia). Obie mają identyczną obudowę; różnią się tylko modułami w gnieździe akcesoriów (czujnik gestu + przycisk albo odbiornik klawiatury).

**Czego nie ma:** paska LED po obwodzie, pedału, głosu, czytnika NFC (zastąpiony magnesami, 4.4). Ramka nigdy nie wjeżdża do skanera.

## 2. Twarde ograniczenia

- Prac (koron) nie wolno niczym znakować ani spryskiwać. Płytka i ramka mogą mieć dowolne oznaczenia.
- **Rozmiar płytki wyznacza pole skanowania skanera, nie ramka.** Do skanera wjeżdża sama płytka i wszystkie gniazda z pracami muszą mieścić się w polu skanowania (założenie: 100 × 100 mm, do potwierdzenia na egzemplarzu testowym skanera Aidite A‑IS Pro 3). Ramka ma gniazdo dopasowane do płytki, nie odwrotnie. Jeśli pole okaże się mniejsze, zmniejsza się płytkę, a w ramce wymienia się tylko wkładkę gniazda (4.3) — dlatego rozmiar płytki ma być parametrem skryptu.
- Prace spieczone wyjmowane z pieca mają 40–70 °C. Płytka poranna musi to znosić bez odkształceń; ramka nie dotyka prac.
- Pył z szlifowania cyrkonii w pomieszczeniu: obudowa zamknięta od dołu i z boków, otwory wentylacyjne skierowane w dół, elektronika bez odsłoniętych złącz.
- Sieć: firmowe Wi‑Fi 2,4 GHz; zapas: hotspot z laptopa. Zero chmury, zero kont zewnętrznych.
- Software ramki pisze Claude Code w Pythonie; wszystko open source.

## 3. Płytki (obie do zaprojektowania) i elementy, które ramka obsługuje

### 3.1 Płytki — wspólna geometria
- Obie **kwadratowe 96 × 96 mm** (parametr), grubość 8 mm, ten sam obrys, to samo gniazdo w ramce.
- Gniazda stożkowe (kąt ścianki ok. 15°, głębokość 4 mm), **dno z otworem przelotowym ø3 mm** — światło diody przechodzi prosto, pył spada na dyfuzor zamiast zalegać, a materiał nie musi być przezroczysty. Jeśli usługodawca ma materiał półprzezroczysty, otwór można zostawić i tak.
- 3 stożki ø5 × 3 mm w trzech narożnikach (znaczniki dla skanera; po nich program wyrównuje skan), wycięcie orientacyjne 5 × 5 mm w czwartym narożniku (wymusza ułożenie w skanerze i w ramce).
- **Kod płytki dla skanera**: 1–3 dołki ø2 × 1 mm w ustalonych pozycjach obok jednego znacznika (binarnie 1–7).
- **Magnesy dla ramki**: kieszenie ø5,2 × 2,2 mm od spodu w trzech narożnikach (poza narożnikiem z wycięciem); magnes ø5 × 2 mm wklejony lub nie — układ obecności = numer płytki (ten sam numer co kod dołków). Zaznacz w instrukcji: biegun jednakowy we wszystkich płytkach.
- Numer płytki wytłoczony (relief 0,6 mm) na wierzchu w rogu, poza strefą gniazd.
- Strefa gniazd 90 × 90 mm; między gniazdami ≥ 3 mm ścianki.
- **Pokrywka**: nakładka zatrzaskowa (4 zatrzaski na krawędziach) z 4 mm luzu nad gniazdami, na czas przenoszenia płytki między pomieszczeniami; jedna pokrywka pasuje do obu płytek.

### 3.2 Płytka wieczorna (prace zielone, zimne, większe o skurcz)
- 22 gniazda w trzech rozmiarach: ø9, ø12, ø15 mm (średnice górne), np. 8 × ø9, 9 × ø12, 5 × ø15, plus **2 rynienki 60 × 15 × 4 mm** z zaokrąglonymi końcami na mosty. Układ gniazd w pliku JSON obok modelu (program czyta współrzędne, więc zmiana układu nie wymaga zmiany kodu).

### 3.3 Płytka poranna (prace spieczone, 40–70 °C, mniejsze)
- 30–32 gniazda: ø7,5, ø10, ø12,5 mm, plus 1–2 rynienki 50 × 13 mm. Reszta jak wyżej.
- **Materiał odporny na temperaturę**: zalecany druk SLS lub MJF z PA12 (nylon; matowy, sztywny, długotrwale do ok. 80 °C, chwilowo wyżej), w kolorze naturalnym białym (skaner lubi mat). Alternatywy: CNC z PMMA 8 mm (opal/mleczny; Tg ok. 105 °C) albo SLA w żywicy wysokotemperaturowej. Nie: zwykła żywica modelowa, PLA.
- Płytkę wieczorną zamów w tym samym materiale (ten sam proces = te same tolerancje), chyba że usługodawca ma półprzezroczystą żywicę SLA w podobnej cenie — wtedy wieczorna może być z niej.

### 3.4 Matryca LED
- Panel HUB75 **64 × 64, raster P2.5**, pole świecące 160 × 160 mm, PCB ok. 160 × 160 mm, grubość ze złączami ok. 14–16 mm, otwory montażowe M3 (położenie **zmierz na prawdziwym panelu**; różni się między producentami). Zasilanie 5 V, realny pobór < 1,5 A.
- Nad panelem **dyfuzor**: mleczna pleksi 2 mm 160 × 160 (kupowana, nie zamawiana), odstęp dyfuzor–diody 3–5 mm. Płytka leży na dyfuzorze we wkładce gniazda.
- Marginesy: płytka 96 mm na matrycy 160 mm zostawia pas 32 mm (12–13 pikseli) z każdej strony — tam program rysuje cyfry (kuweta, liczba prac, numer płytki) i stan ramki kolorem tła. Pas od frontu i prawy muszą zostać odsłonięte w całości.

### 3.5 Sterownik i zasilanie
- **Raspberry Pi 4 B (2 GB)** + **Adafruit RGB Matrix Bonnet** (albo RGB Matrix HAT + RTC), biblioteka `rpi-rgb-led-matrix` (Python). Powód zamiast ESP32: klawiatura bezprzewodowa z odbiornikiem USB i czujnik gestu działają na Pi bez firmware, Wi‑Fi wbudowane, kod w Pythonie jak reszta stanowiska. Pi 5 odpada (biblioteka go nie wspiera).
- Zasilacz 5 V 4 A z wtykiem DC 5,5/2,1 do gniazda panelowego w obudowie → Bonnet (zasila panel i Pi).
- microSD 16–32 GB A1, system w trybie tylko do odczytu (overlay), żeby nagłe wyłączenie prądu nie psuło karty.
- Radiator pasywny na Pi; 10 mm nad procesorem i kanał powietrza.

### 3.6 Akcesoria
- **Klawiatura numeryczna bezprzewodowa 2,4 GHz z odbiornikiem USB** (nie Bluetooth‑only), 60–120 zł; odbiornik w gnieździe USB Pi wewnątrz obudowy (sygnał przechodzi przez plastik; w razie problemów krótki przedłużacz do bocznej ścianki). Klawiatura leży luzem na stole rozkładania w zamawianej podstawce.
- **Czujnik gestu** (ramka wieczorna): VL53L1X (ToF, I2C) w głowicy na przedniej krawędzi, patrzący w górę; machnięcie dłonią 5–30 cm = zdarzenie. Alternatywa: APDS‑9960.
- **Przycisk** (ramka wieczorna): arkadowy ø30 mm z podświetleniem; w porannej otwór zaślepiony, żeby obudowy były identyczne.
- **3 czujniki Halla** (A3144 lub SS49E, TO‑92) we wkładce gniazda → GPIO Pi.
- Gniazdo DC panelowe 5,5/2,1 mm z nakrętką, przepusty kablowe, stopki gumowe.

## 4. Konstrukcja obudowy — wytyczne do projektu

### 4.1 Gabaryt i układ
- Obudowa zamknięta, dwie główne części: **korpus** (dno + ściany) i **blat** (górna płyta z oknem na matrycę). Zewnętrznie ok. 200 × 200 mm, wysokość 55–60 mm (panel 16 + odstęp 4 + dyfuzor 2 + Pi z Bonnetem pod panelem 30 + luzy). Wariant niski: Pi obok panela → 200 × 270 × 35 mm. Plan porównuje oba warianty i rekomenduje jeden; modelowany jest tylko rekomendowany.
- Panel na 4–6 słupkach z wkładkami M3 w dnie korpusu, złączami w dół; nad nim rama dystansowa trzymająca dyfuzor; blat mocowany od spodu lub zatrzaskami + 2 śruby od dołu (bez widocznych śrub na blacie — ramka będzie pokazywana zarządowi).
- Pi na 4 słupkach M2,5 (wkładki wtapiane) pod panelem lub w komorze bocznej; w tylnej ściance: gniazdo DC, 1× USB serwisowo; slot karty SD dostępny po zdjęciu blatu.
- Wentylacja: szczeliny nisko w tylnej i bocznych ścianach z daszkiem od góry; dno podniesione 4 mm na stopkach.
- Grubość ścian 2,5–3 mm; żebra pod blatem; promienie 3–5 mm na krawędziach zewnętrznych.

### 4.2 Okno i margines matrycy
- Okno w blacie 162 × 162 mm (panel 160 + luz), z zagłębieniem 2 mm na dyfuzor, licowany z blatem.

### 4.3 Gniazdo płytki — wymienna wkładka
- Na dyfuzorze leży **wkładka gniazda**: rama 3 mm wysokości osadzona w blacie na 2 kołkach i 2 magnesach, która ustala położenie płytki z powtarzalnością ±0,5 mm i wymusza orientację (narożnik z wycięciem płytki wchodzi na kołek).
- Otwór wkładki 96,6 × 96,6 mm (parametr), 4 niskie narożne ograniczniki L; wnęki na 3 czujniki Halla w narożnikach i kanał na przewody do krawędzi blatu; ścianka wkładki nad matrycą ≤ 4 mm, żeby nie zabierać pikseli; wycięcie „palcowe” z jednej strony do podniesienia płytki bez dotykania prac.
- Jedna wkładka obsługuje obie płytki (ten sam obrys). Jest osobną częścią, bo przy zmianie rozmiaru płytki wymienia się tylko ją.

### 4.4 Rozpoznawanie płytki i jej obecności
- Pod płytką jest matryca, więc antena NFC nie mieści się bez zasłaniania diod. Zamiast tego: **magnesy w płytce + 3 czujniki Halla we wkładce**: 7 kodów płytek, 000 = brak płytki. Odległość magnes–czujnik ≤ 4 mm. A3144 ma otwarty kolektor — rezystory podciągające lub podciąganie wewnętrzne GPIO.
- Przewód 3‑żyłowy od każdego czujnika do małej płytki prototypowej przy Pi.
- Równolegle skaner czyta kod dołków ze skanu — to działa niezależnie od ramki.

### 4.5 Głowica czujnika gestu i przycisk (ramka wieczorna)
- Osobna „łódka” na przedniej krawędzi obudowy z VL53L1X skierowanym w górę pod kątem ~15° w stronę użytkownika; okienko 8 × 6 mm; kabel I2C 4‑żyłowy przez przepust.
- Przycisk arkadowy ø30 mm w przedniej ściance po prawej; w ramce porannej zaślepka.

### 4.6 Podstawka klawiatury (ramka poranna)
- Tacka pod klawiaturę numeryczną z 3 mm krawędzią i wycięciem na palec; nalepka z legendą klawiszy jako SVG (Enter = następna, cyfry = numer kuwety, Backspace = cofnij, `*` = zamknij piec).

### 4.7 Wygląd
- Jedna kolorystyka: korpus i blat w PA12 barwionym na grafit (albo naturalny szary), wkładki i płytki białe. Bez logo producentów. Napis „RAMKA WIECZORNA / PORANNA” wytłoczony na przedniej ściance.

### 4.8 Zasady projektowania pod zewnętrzny druk (SLS/MJF PA12) i CNC
- Minimalna grubość ścianki 1,5 mm (zalecane 2,5–3 mm), minimalny relief napisów 0,6 mm, otwory ≥ ø1,5 mm, luzy pasowań 0,2–0,3 mm (ruchome) i 0,1–0,15 mm (wciskane).
- Części puste w środku muszą mieć otwory na wysypanie proszku (≥ ø5 mm) — albo nie projektuj zamkniętych pustek.
- Cena rośnie z objętością materiału i objętością gabarytową: ściany cienkie, bez pełnych bloków, żebra zamiast masy.
- Wkładki gwintowane do wtapiania działają w PA12 (otwór ø4,0 pod M3, ø3,4 pod M2,5), alternatywnie gwintowanie w PA12 bezpośrednio.
- Powierzchnie pasowane (gniazdo płytki, dyfuzor) z zapasem 0,3 mm na chropowatość SLS.
- Do CNC z PMMA (jeśli zostanie wybrane dla płytek): promienie wewnętrzne ≥ 1,5 mm, stożki gniazd jako powierzchnie frezowane 3D; arkusz zamówienia zaznacza, że STL jest do druku, a do CNC usługodawca może potrzebować STEP — Blender nie eksportuje STEP, więc arkusz wskazuje konwersję przez FreeCAD (darmowy) jako krok dodatkowy.
- Każda część w pliku STL osobno, w milimetrach, zorientowana z największą płaską ścianą w dół, nazwa `ramka_<część>_v1.stl`.

## 5. Lista zakupów (elektronika i gotowe elementy)

| Element | Ilość na 2 ramki | Orientacyjna cena |
|---|---|---|
| Panel HUB75 64×64 P2.5 | 2 | 80–130 zł/szt. |
| Raspberry Pi 4 B 2 GB + radiator | 2 | 230–300 zł/szt. |
| Adafruit RGB Matrix Bonnet (lub HAT + RTC) | 2 | 70–130 zł/szt. |
| Zasilacz 5 V 4 A DC 5,5/2,1 + gniazdo panelowe | 2 | 40–60 zł/kpl. |
| microSD 32 GB A1 | 2 | 25 zł/szt. |
| Mleczna pleksi 2 mm 160×160 | 2 | 10–20 zł/szt. |
| Klawiatura numeryczna bezprzewodowa 2,4 GHz z odbiornikiem USB | 1 | 60–120 zł |
| VL53L1X (moduł) | 1 | 25–40 zł |
| Przycisk arkadowy ø30 LED | 1 | 15–25 zł |
| Czujniki Halla A3144/SS49E | 6 + zapas | 1–3 zł/szt. |
| Magnesy neodymowe ø5×2 | ok. 20 (9 w płytkach — tylko w kieszeniach, które wypadają w kodzie numeru 1–6 — i ok. 10 do mocowania wkładek w blatach); kupić paczkę 30 szt. | 0,5 zł/szt. |
| Wkładki gwintowane M3 i M2,5, śruby, słupki | komplet | 40–60 zł |
| Przewody, płytka prototypowa, złącza JST/Dupont, rzep, stopki gumowe | komplet | 40–60 zł |

Razem elektronika i drobne: ok. 1,1–1,7 tys. zł.

## 6. Lista części do zamówienia zewnętrznie (uzupełniana w arkuszu zamówienia)

| Część | Ilość | Zalecana technologia / materiał |
|---|---|---|
| Płytka wieczorna 96×96 | 3 | SLS/MJF PA12 biały (lub SLA półprzezroczysta) |
| Płytka poranna 96×96 | 3 | SLS/MJF PA12 biały (alternatywa: CNC PMMA opal) |
| Pokrywka płytki | 4 | SLS/MJF PA12 |
| Korpus ramki | 2 | SLS/MJF PA12 grafit |
| Blat ramki | 2 | SLS/MJF PA12 grafit |
| Rama dyfuzora | 2 | SLS/MJF PA12 |
| Wkładka gniazda płytki | 2 + 1 zapas | SLS/MJF PA12 biały |
| Głowica czujnika gestu | 1 | SLS/MJF PA12 grafit |
| Zaślepka otworu przycisku | 1 | SLS/MJF PA12 grafit |
| Uchwyt odbiornika / kabli | 2 | SLS/MJF PA12 |
| Podstawka klawiatury | 1 | SLS/MJF PA12 grafit |

Koszt szacuje się po objętości części: arkusz zamówienia podaje objętość każdego STL w cm³ (usługodawcy wyceniają po objętości i gabarycie) i dwa warianty — najtańszy (PA12 naturalny, bez barwienia) i pokazowy (barwienie, wygładzanie).

## 7. Narzędzia
Lutownica z grotem do wkładek gwintowanych, cyna, trzecia ręka; multimetr; wkrętaki krzyżowe i torx; klucz do nakrętki gniazda DC; szczypce; papier ścierny 400; klej CA do magnesów; laptop z czytnikiem kart SD. Bez drukarki — części przychodzą gotowe.

## 8. Kolejność budowy i testy

1. **Pomiary** (sekcja 9) → parametry skryptu → eksport STL → zamówienie części (czas realizacji usługodawcy 1–3 tygodnie; zamówić w tym samym tygodniu co elektronikę).
2. **Elektronika na stole, bez obudowy** (gdy części są w drodze): Pi + Bonnet + panel + zasilacz; system, `rpi-rgb-led-matrix`, test wzoru i cyfr na marginesie; pomiar poboru prądu; test klawiatury (odbiornik w Pi) i czujnika gestu w Pythonie.
3. **Montaż mechaniczny**: wkładki gwintowane w korpusie, słupki, panel, dyfuzor w ramie, próba zamknięcia blatu, wkładka gniazda z czujnikami Halla.
4. **Magnesy w płytkach** według kodów, test odczytu 000–111 na wkładce.
5. **Okablowanie i zamknięcie**: gniazdo DC, przycisk, głowica gestu, rzep na odbiornik; opis kabli.
6. **Kalibracja gniazdo → diody**: program wyświetla kolejno pole pod każdym gniazdem, operator potwierdza; wynik jako tabela gniazdo → piksele w JSON obok modelu płytki (osobno dla płytki wieczornej i porannej).
7. **Test 8 godzin** ciągłego świecenia (Pi < 70 °C, zasilacz chłodny) i test odłączenia prądu (system wstaje sam).
8. Druga ramka z poprawkami z pierwszej.

## 9. Do zmierzenia na prawdziwych elementach przed zamówieniem (parametry skryptu)
- Panel HUB75: rozmiar PCB, położenie i średnica otworów montażowych, wysokość złączy i kondensatorów od spodu, pozycje złączy zasilania i HUB75 IN/OUT.
- Pi 4 + Bonnet: łączna wysokość stosu, wystające złącza, pozycja gniazda zasilania Bonnetu.
- Skaner: pole skanowania (czy 96 × 96 wchodzi w całości) — z testu egzemplarza Aidite; jeśli nie, nowy rozmiar płytki.
- Klawiatura: model, rozmiar odbiornika USB, wymiary klawiatury do podstawki.
- Przycisk arkadowy: średnica otworu montażowego (ø30 lub ø24).
- Usługodawca: dostępne materiały i kolory, maksymalny gabaryt części, czy przyjmuje STL do CNC.
