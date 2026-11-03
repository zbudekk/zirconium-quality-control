# Mail do Aidite — pełne zapytanie techniczne i handlowe przed testem A-IS Pro 3

Wersja polska (dystrybutor) i angielska (inżynier aplikacyjny Aidite/Shining). Pytania są ponumerowane, żeby odpowiedź mogła iść punkt po punkcie. Źródła pytań: plan wdrożenia v2 (sekcja „Test przed zakupem”, kryteria 1–8), dokumentacja DentalScan 3.0.4, notatki_dokumentacja_skanera.md.

---

**Temat:** A-IS Pro 3 — egzemplarz testowy i pytania techniczne (ścieżka skanu, pole, eksport, licencja)

Dzień dobry,

planujemy stanowisko kontroli prac z cyrkonii oparte na skanerze laboratoryjnym i rozważamy A-IS Pro 3 jako pierwszy wybór. Zastosowanie jest nietypowe: zamiast modelu skanujemy **płytkę 96 × 96 mm z 24–35 koronami i do 2 mostów ułożonymi luźno w gniazdach**, jednym skanem, 7–10 razy dziennie, a plik STL analizuje nasz własny program. Przed decyzją chcemy przeprowadzić dwutygodniowy test u nas. Poniżej pytania, na które nie znaleźliśmy odpowiedzi w dokumentacji DentalScan 3.0.4. Prosimy o odpowiedź punkt po punkcie; przy pytaniach o ustawienia wystarczy zrzut ekranu lub krótkie nagranie.

**A. Test i warunki handlowe**

1. Czy możecie udostępnić egzemplarz testowy A-IS Pro 3 na 2 tygodnie (od 9 listopada) z aktualnym oprogramowaniem i kompletem stolików? Na jakich warunkach (kaucja, transport, ubezpieczenie)?
2. Czy w czasie testu będzie dostępny inżynier aplikacyjny (telefon / zdalny pulpit), nie tylko opiekun handlowy?
3. Prosimy o ofertę: cena skanera z oprogramowaniem, co dokładnie jest w zestawie (stoliki, wzorzec kalibracyjny, klucz USB, kable, hub), termin dostawy po zamówieniu, warunki płatności, cena drugiej licencji / klucza i rocznej umowy serwisowej, jeśli istnieje.
4. Która wersja sprzętu trafi do nas: A-IS Pro 3, A-IS Pro (IPBA) czy (IPWA)? Czym się różnią (kamery, dokładność, regulacja osi Z)?

**B. Ścieżka skanu i mechanika stolika**

5. Czy da się ustawić strategię skanu z **samym obrotem wokół osi pionowej** (4–6 pozycji) przy osi przechyłu (swing) zablokowanej w 0°? Luźne prace przesuwają się przy przechyle. Jeśli tak: gdzie się to ustawia i czy strategię można zapisać na stałe w zleceniu (tryb Multidie)?
6. Czy prędkość obrotu stolika jest regulowana i czy start/stop jest łagodny (rampa), bez szarpnięć? Jaka jest minimalna prędkość?
7. Jakie są kąty i liczba pozycji w strategiach basic / medium / advanced (6 / 9 / 12 pozycji) — obrót i przechył dla każdej? Czy użytkownik może zdefiniować własną listę pozycji?
8. Czy w trybie „Manual Add-scan” użytkownik zadaje kąt obrotu i przechyłu liczbowo, czy tylko przez obrót modelu na ekranie?
9. Jaka jest powtarzalność dwóch kolejnych skanów tego samego, nieruszonego obiektu (oczekujemy < 0,03 mm)?

**C. Pole skanowania i mocowanie**

10. Jaki jest maksymalny wymiar obiektu (X × Y × Z), który mieści się w jednym skanie bez sklejania? Potrzebujemy całej płytki 96 × 96 mm razem ze znacznikami w narożnikach, wysokość prac do 14 mm nad płytką.
11. Jaki jest prześwit komory przy pełnym obrocie stolika i maksymalna masa obiektu na stoliku?
12. Prosimy o rysunek lub plik STEP/STL interfejsu stolika (talerz, kołki, magnesy, gwinty) — chcemy wydrukować własny adapter pod płytkę; czy własny adapter nie narusza gwarancji?
13. Czy skaner poprawnie skanuje matowy biały nylon PA12 (płytka drukowana MJF/SLS) i czy płytka może być w kadrze w całości (czy program nie usuwa jej jako „uchwytu”/szumu)?

**D. Oprogramowanie: zlecenia, eksport, obróbka**

14. Czy istnieje tryb szybkiego skanu bez zakładania zlecenia w DentalManager? Jeśli nie: czy jedno zapisane zlecenie Multidie można skanować wielokrotnie w ciągu dnia i co się dzieje z poprzednim skanem (nadpisanie, nowy plik)?
15. Czy po zakończeniu skanu STL zapisuje się **automatycznie** do wskazanego folderu (Order Save Path) bez klikania w eksport? Jaka jest struktura folderu zlecenia i nazwa pliku (Order File Naming Rule)? Ile kliknięć od „Scan” do pliku STL na dysku?
16. Formaty eksportu: STL binarny / ASCII, PLY z normalnymi, OBJ? Czy eksportowana siatka jest w **stałym układzie współrzędnych stolika** (ten sam układ w kolejnych skanach), czy w układzie dopasowanym do modelu?
17. Które operacje program wykonuje **automatycznie** na danych przed eksportem (wypełnianie otworów, wygładzanie, upraszczanie, usuwanie drobnych fragmentów, AI Detection) i czy każdą z nich da się wyłączyć? Chcemy surową siatkę.
18. Jaka jest gęstość punktów / średnia długość krawędzi trójkąta w eksportowanym STL i czy da się ją ustawić?
19. Płaszczyzna cięcia (cutting plane): czy jej wysokość zapisuje się w zleceniu, żeby nie trzeba było ustawiać jej przy każdym skanie?
20. Skróty klawiszowe: Spacja startuje skan — czy są też skróty do „Apply/Next” i eksportu, tak by cały przebieg dało się wykonać z klawiatury (albo z naszego programu)?
21. Czas: ile trwa skan płytki w strategii basic (obrót, 4–6 pozycji) i ile trwa obliczenie i zapis STL dla obiektu ok. 1–2 mln trójkątów?
22. Czy opcja „Save Image” zapisuje surowe zdjęcia z obu kamer w pełnej rozdzielczości (5 MP)? W jakim formacie i folderze?
23. Ile zleceń dziennie / rocznie „wytrzymuje” baza DentalManager i jak archiwizować stare zlecenia?

**E. Materiał: zielona i spieczona cyrkonia**

24. Zielona (presynteryzowana) cyrkonia, biała, matowa: czy skanuje się bez sprayu z pełnym pokryciem brzegu i wnętrza korony ułożonej brzegiem do góry?
25. Spieczona, przezierna cyrkonia (w tym 5Y) bez sprayu: jakie pokrycie powierzchni można realnie uzyskać i które tryby polecacie (HDR, High Quality / Add details, „Mental tooth”, „reduce high brightness”)? Czy macie przykładowe skany?
26. Czy drobne ubytki brzegu rzędu 0,25–0,4 mm są widoczne w skanie przy deklarowanej dokładności 8 µm? Jaka jest rzeczywista rozdzielczość przestrzenna (najmniejszy odwzorowany szczegół)?

**F. Licencja, aktualizacje, integracja**

27. Czy autoryzacja jest bezterminowa, czy wymaga okresowego przedłużania („Authorization Remaining Days”)? Co się dzieje po upływie terminu?
28. Czy program działa bez dostępu do internetu? Czy wymaga logowania do konta?
29. Czy dostępny jest drugi klucz USB / druga instalacja na laptop deweloperski (bez skanera, do pracy na plikach)? Koszt?
30. Czy aktualizacje są bezpłatne, czy można je zablokować na sprawdzonej wersji i czy program DentalScan to własne oprogramowanie Aidite, czy OEM (czyje, jaka wersja)?
31. Czy istnieje SDK, API albo wywołanie z linii poleceń (start skanu, parametry, folder wyjściowy)? Jak wygląda integracja z exocad („wspólna baza danych”) — czy z niej można odczytać status zlecenia?
32. Wymagania komputera: czy wspierany jest Windows 11 i laptop z kartą RTX (dokumentacja podaje Win10 i GTX 1060Ti)? Konkretna lista zalecanych konfiguracji.

**G. Kalibracja, serwis, gwarancja, szkolenie**

33. Czy wzorzec kalibracyjny jest w zestawie, czy kalibrację robimy sami i jak często (praca w pomieszczeniu z pyłem ze szlifowania)?
34. Certyfikat dokładności (ISO 12836) i deklaracja CE — prosimy o dokumenty.
35. Gwarancja: długość (oczekujemy 2 lat), urządzenie zastępcze na czas naprawy, czas reakcji serwisu, serwis w Polsce czy wysyłka.
36. Zalecenia na pracę w pomieszczeniu frezarki/szlifowania: filtry, pokrowce, czyszczenie optyki, dopuszczalna temperatura i wilgotność.
37. Szkolenie i instrukcja w języku polskim; wsparcie zdalne — godziny i język.

Pytania 5, 10 i 12 decydują o rozmiarze naszej płytki, więc odpowiedź na nie przed testem oszczędzi czas obu stronom. Pozostałe sprawdzimy w czasie testu, ale chętnie poznamy odpowiedzi wcześniej.

Z pozdrowieniami,
Michał Budek
[firma, telefon]

---

**Subject:** A-IS Pro 3 — evaluation unit and technical questions (scan path, scan volume, export, license)

Dear Aidite team,

we plan a zirconia quality-control station built around a lab scanner and consider the A-IS Pro 3 as our first choice. The use case is unusual: instead of a model we scan a **96 × 96 mm plate holding 24–35 loose crowns and up to 2 bridges in sockets**, in one scan, 7–10 times a day, and our own software analyses the STL. Before deciding we would like a two-week on-site evaluation. The DentalScan 3.0.4 documentation does not answer the questions below; please reply point by point, a screenshot or short screen recording is enough for settings questions.

**A. Evaluation and commercial terms**

1. Can you provide an A-IS Pro 3 evaluation unit for 2 weeks (from 9 November) with current software and the full set of fixtures? On what terms (deposit, shipping, insurance)?
2. Will an application engineer (phone / remote desktop) be available during the evaluation, not only a sales contact?
3. Please quote: scanner with software, exact box contents (fixtures, calibration plate, USB dongle, cables, hub), lead time after order, payment terms, price of a second license / dongle and of an annual service contract, if offered.
4. Which hardware version would we receive: A-IS Pro 3, A-IS Pro (IPBA) or (IPWA)? What are the differences (cameras, accuracy, Z-axis adjustment)?

**B. Scan path and turntable mechanics**

5. Can a scan strategy use **rotation only** (4–6 positions) with the swing/tilt axis locked at 0°? Loose parts shift when the table tilts. If yes: where is it set, and can the strategy be saved permanently in a Multidie order?
6. Is the turntable speed adjustable, and is start/stop ramped (no jerk)? What is the minimum speed?
7. What are the angles and positions of the basic / medium / advanced strategies (6 / 9 / 12 positions), rotation and tilt for each? Can the user define a custom list of positions?
8. In "Manual Add-scan", does the user enter rotation and tilt angles numerically, or only by rotating the model on screen?
9. What is the repeatability of two consecutive scans of the same untouched object (we expect < 0.03 mm)?

**C. Scan volume and fixture**

10. What is the maximum object size (X × Y × Z) captured in one scan without stitching? We need the whole 96 × 96 mm plate including corner markers, parts up to 14 mm above the plate.
11. What is the chamber clearance at full rotation and the maximum load on the table?
12. Please send a drawing or STEP/STL of the turntable interface (plate, pins, magnets, threads); we want to print our own adapter. Does a custom adapter affect the warranty?
13. Does the scanner capture matte white PA12 nylon (MJF/SLS printed plate) correctly, and can the plate stay fully in frame (is it not removed automatically as "jig" or noise)?

**D. Software: orders, export, processing**

14. Is there a quick-scan mode without creating an order in DentalManager? If not: can one saved Multidie order be scanned repeatedly during the day, and what happens to the previous scan (overwrite, new file)?
15. After a scan completes, is the STL written **automatically** to the Order Save Path without clicking export? What is the order folder structure and file name (Order File Naming Rule)? How many clicks from "Scan" to an STL on disk?
16. Export formats: binary / ASCII STL, PLY with normals, OBJ? Is the exported mesh in a **fixed turntable coordinate system** (same frame in consecutive scans) or in a model-fitted frame?
17. Which operations run **automatically** before export (hole filling, smoothing, decimation, small-fragment removal, AI Detection) and can each be switched off? We want the raw mesh.
18. What is the point density / mean triangle edge of the exported STL, and is it adjustable?
19. Cutting plane: is its height stored in the order so it need not be set at every scan?
20. Shortcuts: Space starts a scan — are there shortcuts for "Apply/Next" and export, so the whole workflow can run from the keyboard (or from our software)?
21. Timing: scan time of the plate in the basic strategy (rotation, 4–6 positions), and processing + STL save time for an object of 1–2 million triangles?
22. Does "Save Image" store raw full-resolution (5 MP) images from both cameras? Format and folder?
23. How many orders per day / year can the DentalManager database handle, and how are old orders archived?

**E. Material: green and sintered zirconia**

24. Green (pre-sintered) zirconia, matte white: does it scan without spray with full coverage of margin and intaglio when placed margin-up?
25. Sintered translucent zirconia (incl. 5Y) without spray: what surface coverage is realistic and which modes do you recommend (HDR, High Quality / Add details, "Mental tooth", "reduce high brightness")? Sample scans?
26. Are small margin chips of 0.25–0.4 mm visible at the stated 8 µm accuracy? What is the actual spatial resolution (smallest reproduced detail)?

**F. License, updates, integration**

27. Is the authorization perpetual or does it require periodic renewal ("Authorization Remaining Days")? What happens when it expires?
28. Does the software work offline? Does it require an account login?
29. Is a second dongle / second installation for a development laptop (no scanner, file work only) available? Cost?
30. Are updates free, can we lock a proven version, and is DentalScan Aidite's own software or OEM (whose, which version)?
31. Is there an SDK, API or command-line launch (start scan, parameters, output folder)? How does the exocad integration ("shared database") work — can order status be read from it?
32. PC requirements: is Windows 11 and a laptop RTX GPU supported (docs state Win10 and GTX 1060Ti)? Please list recommended configurations.

**G. Calibration, service, warranty, training**

33. Is the calibration plate included, do we calibrate ourselves, and how often (room with grinding dust)?
34. Accuracy certificate (ISO 12836) and CE declaration — please send the documents.
35. Warranty: length (we expect 2 years), loaner unit during repair, service response time, service in Poland or shipping.
36. Recommendations for operation in a milling/grinding room: filters, covers, optics cleaning, allowed temperature and humidity.
37. Training and manual in Polish; remote support — hours and language.

Points 5, 10 and 12 determine the size of our plate, so answering them before the evaluation saves time on both sides. The rest we can verify during the test, but we would welcome answers earlier.

Best regards,
Michał Budek
[company, phone]
