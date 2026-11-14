# Stanowisko kontroli cyrkonii — plan wdrożenia v2 (skaner laboratoryjny)

14 listopada 2026 (R59: nowy układ gniazd płytek) · Autor: Michał Budek

## Streszczenie po ludzku

Budujemy na parapecie frezowni jedno stanowisko z laboratoryjnym skanerem 3D, które wieczorem wyłapuje ukruszone prace z cyrkonii zanim trafią do pieca, a rano mówi, która praca należy do której kuwety, i samo odhacza zlecenia w firmowym Excelu. Obsługa sprowadza się do ułożenia prac w gniazdach płytki i naciśnięcia spacji na laptopie; resztę robi program.

Jak to działa w jednym zdaniu: skaner mierzy całą płytkę prac naraz (do 18 koron i 1 mostu wieczorem, do 23 koron i 1 mostu rano), program nakłada każdą zmierzoną pracę na jej projekt z SharePointa i zaznacza miejsca, gdzie brakuje materiału; rano ten sam skan służy do rozpoznania, do którego zlecenia praca należy, a diody pod gniazdami podświetlają prace bieżącej kuwety.

Trzy cele i co dostajemy:

1. **Kontrola ukruszeń wieczorem** — automatyczna mapa płytki z czerwonymi gniazdami; technik bierze do ręki tylko oznaczone prace. Cel: większość ukruszeń brzegów od ok. 0,3 mm wykryta przed piecem; wykrywalność mierzymy na próbie testowej, nie zakładamy 100%.
2. **Szybsze rozkładanie rano** — program wskazuje kuwetę dla każdej pracy, a diody prowadzą rękę kuweta po kuwecie. Cel: duży piec z ok. 40 min do ok. 20–25 min.
3. **Excel** — zlecenia, których wszystkie punkty wyszły z pieca, odhaczają się same (zielone pole w kolumnie B), z logiem każdej zmiany. Cel: 10–15 min na piec do zera.

Co kupujemy: skaner laboratoryjny Aidite A-IS Pro 3 (ok. 20–25 tys. zł, przez istniejącą relację z Aidite; zamiennie Shining AutoScan-DS-EX Pro(H), DOF Freedom lub 3Shape F8), dwa komplety płytek z gniazdami (6 sztuk: 3 wieczorne i 3 poranne; o kształcie — okrągłe czy kwadratowe — właściciel decyduje po odbiorze plików nowego układu [R59]), dwie ramki świetlne (przy skanerze i w pokoju rozkładania) na Raspberry Pi z matrycą LED, bezprzewodową klawiaturę numeryczną, osłonę, drobne. Części ramek i płytek drukujemy w zewnętrznej drukarni z gotowych plików, a część ukrytych lub testowych elementów sami. Laptop daje firma. Oprogramowanie piszemy sami, bez płatnych bibliotek i subskrypcji.

Stan prac: projekt ramek i płytek jest zamknięty w planie budowy v2, a obudowa została tak zaprojektowana, by nie zależała od wymiarów kupowanej elektroniki (zapasy, rowki i podkładki zamiast dopasowania po pomiarach). Pliki do druku są ostateczne, zweryfikowane trzykrotnie (generator, recenzent, niezależna kontrola pasowań); do drukarni: korpus W, korpus P, blat × 2 — od razu; wkładka × 3, płytki n1–n6 — po potwierdzeniu pola skanowania; pokrywki × 4 drukujemy sami po potwierdzeniu pola. Elektronikę ramek można zamawiać od razu. [R59] Płytki mają nowy układ gniazd: wieczorna 18 gniazd i 1 rynienkę, poranna 23 gniazda i 1 rynienkę; płytki wykonane wcześniej zostają w użyciu, a program zna oba układy (sekcja „Nowy układ gniazd płytek”). Model 3D ramki z wymiarami do pomiaru: https://claude.ai/artifact/N1W9QKGcXq87t3GPhFp5Sf (wersja online pokazuje płytki w poprzednim układzie gniazd; model z nowym układem jest w pakiecie plików). Szczegółowa lista zakupów i instrukcje druku są w osobnym dokumencie „Zakupy i druk — stanowisko kontroli cyrkonii”; powody wyboru każdego elementu ramki, możliwe zamienniki i elementy, z których świadomie zrezygnowano, opisuje dokument „Budowa ramki — decyzje i zamienniki”.

Kolejność: zakup skanera poprzedza test na egzemplarzu testowym na naszych pracach (20 zielonych i 10 spieczonych prac na płytkach), który rozstrzyga wybór skanera. Potem decyzja, zamówienie i oczekiwanie na dostawę — w tym czasie powstają oprogramowanie i obie ramki. Po dostawie: uruchomienie, tryb cienia (do spełnienia kryteriów odbiorczych) i tryb pełny.

Czego stanowisko nie zrobi: nie rozróżni dwóch niemal identycznych prac implantologicznych (różnią się tylko kolorem, którego nie ma w danych — pokaże obu kandydatów, decyduje człowiek) i nie zagwarantuje wykrycia każdego ukruszenia wielkości pół kryształu cukru.

## Co wybraliśmy i dlaczego

Wybrany wariant to skaner laboratoryjny ze światłem strukturalnym (światło niebieskie, dwie kamery 5 MP) i porównanie każdej zmierzonej pracy z jej projektem. Spośród czterech rozważanych podejść tylko to naprawdę mierzy ubytek, a nie tylko go pokazuje, i tylko ono daje rano identyfikację z tych samych danych co wieczorem.

Decyzje:

| Decyzja | Wybór | Dlaczego |
|---|---|---|
| Urządzenie pomiarowe | Skaner laboratoryjny Aidite A-IS Pro 3 (klasa Shining DS-EX Pro(H)) | Dokładność 8 µm i gęstość punktów wystarczają na ubytki 0,25–0,5 mm; relacja z Aidite daje test u nas i wsparcie inżynierów; cena w budżecie 20–25 tys. zł |
| Alternatywy, jeśli test nie przejdzie | DOF Freedom X5/UHD (model nieruchomy, kamera jeździ), 3Shape F8 (skan bez przechyłu) | Rozwiązują problem przechyłu stolika konstrukcyjnie; ceny tylko na zapytanie |
| Ułożenie prac | Brzegiem do góry (powierzchnią żującą w dół), w gniazdach drukowanej płytki | Brzegi i wnętrze widoczne z góry; gniazda trzymają prace przy ruchu stolika |
| Ścieżka skanu | Tylko obrót wokół osi pionowej, przechył 0° | Obrót nie przemieszcza prac; przesunięcie 0,1 mm między pozycjami wyglądałoby jak ukruszenie |
| Wskazywanie prac | Diody RGB pod gniazdami (matryca LED 64 × 64 pod płytką) | Małe, widoczne w dziennym świetle, bez ostrości i paralaksy; wysięgnik z projektorem odpadł |
| Sterownik ramki | Raspberry Pi 4 z nakładką RGB Matrix Bonnet, program w Pythonie | Odbiornik klawiatury USB działa bez własnego firmware, Wi‑Fi wbudowane, ten sam język co reszta stanowiska |
| Rozpoznawanie płytki w ramce | Magnesy w spodzie płytki + 3 czujniki Halla we wkładce | Pod płytką jest matryca, antena NFC nie mieści się bez zasłaniania diod; magnesy są tanie i czytelne |
| Start skanu wieczorem | Spacja na laptopie; przednia ścianka ramki gładka | Mniej części i otworów w pyle, identyczne obudowy; stan ramki widać na matrycy (elementy sterujące, z których zrezygnowano: „Budowa ramki — decyzje i zamienniki”) |
| Poranek | Ten sam skaner (tryb do błyszczących prac), kamera 20 Mpx jako plan B | Jedno urządzenie, jeden program; plan B, gdy spieczona cyrkonia skanuje się za słabo |
| Excel | Excel na laptopie z Autozapisem + sterowanie programem (COM) | Zero infrastruktury i zgód IT; współedycja działa; plan B: Office Script jednym kliknięciem; plan C: Microsoft Graph przez IT |
| Dane | OneDrive synchronizuje folder „Cyrkon” na laptop; raporty MillBox z folderu; zlecenia prywatne z folderu „Prywatne” | Wszystko lokalnie, w firmowym M365, bez chmur zewnętrznych |
| Oprogramowanie | Python + Open3D/trimesh + PySide6, pisane w Claude Code | Darmowe, bez subskrypcji, sprawdzone w pomiarach 3D |

Jawne założenia (każde da się obalić testem lub rozmową i wtedy plan dostaje poprawkę):

1. Kontrola wieczorna może dodać technikowi łącznie do ok. 15–20 min na zmianę; powyżej tego będzie pomijana.
2. Pula prac wieczorem = prace z raportów MillBox z dzisiaj i wczoraj (znany współczynnik skurczu dla każdej); pula rano = wszystkie zlecenia frezowane w ostatnich 3–4 dniach roboczych według raportów MillBox i folderu „Cyrkon”, także te już odhaczone w Excelu, bo poprawki i dofrezowane zęby wracają do zleceń formalnie zamkniętych.
3. Technicy czasem poprawiają prace ręcznie w stanie zielonym, więc odchyłki od projektu nie zawsze są ukruszeniem; program odróżnia ostry, mały ubytek od gładkiej, rozległej poprawki.
4. Raporty MillBox (HTML lub PDF) są dostępne z laptopa stanowiska — z folderu sieciowego albo kopiowane raz dziennie.
5. Ktoś zapisuje STL zleceń prywatnych z Outlooka do folderu „Prywatne/#numer” (ok. 10 s na zlecenie); bez tego prace prywatne identyfikuje się ręcznie.
6. Laptop firmowy: Windows 11, procesor klasy i7/i9, 32 GB RAM, dedykowana karta graficzna, dwa porty USB 3.0, Excel, Outlook i OneDrive na koncie firmowym.
7. Gęstość spieczonej cyrkonii jest stała (ok. 6,05 g/cm³) — używana tylko pomocniczo do zawężania kandydatów.
8. Prezes akceptuje, że wykrywalność mierzymy na próbie i raportujemy liczbą, a nie obietnicą 100%.
9. Pył ze szlifowania: skaner i ramka przy nim dostają pokrowce, płytki są wycierane przed skanem; obudowy ramek są zamknięte, a szczeliny wentylacyjne są nisko przy dnie, z dala od płytki.
10. Zakres prac: korony i mosty do 4 punktów (rynienka 60 × 15 mm wieczorem, 50 × 13 mm rano); mosty powyżej 4 punktów są poza zakresem stanowiska. [R59] Płytka ma jedną rynienkę, więc mieści jeden most; kolejny most idzie na następną płytkę.
11. [R54] Skaner obraca płytkę wokół osi pionowej, więc w całym obrocie widzi koło wokół osi stolika, nie kwadrat — założenie: koło o średnicy 100 mm. Dlatego wszystkie gniazda, rynienka i stożki znaczników leżą w kole o promieniu 47 mm od środka płytki (50 mm minus 1,5 mm na ułożenie płytki względem osi i 1,5 mm na wysięg korony poza gniazdo); obrys płytki 96 × 96 mm bez zmian. Średnica pola jest jedną liczbą w plikach projektu; jeśli okaże się mniejsza, gniazda przelicza się do mniejszego koła i drukuje nowe płytki, a ramka, wkładka i pokrywka zostają; dopiero przy polu poniżej ok. 94 mm płytka stałaby się okrągła i wymagała nowej wkładki i pokrywki.
12. Panel LED i Raspberry Pi mają typowe wymiary (rozstaw otworów panelu 110–130 mm, elementy od spodu do 12 mm, stos Raspberry Pi z nakładką 26 mm). Obudowa ma na to zapasy (8 mm nad stosem, rowki pod słupki, okno USB z rowkami, otwór gniazda z tulejką), więc pomiary kupionej elektroniki nie zmieniają korpusu; przy nietypowym sprzęcie wystarczy wiercenie w dnie, tulejka lub podkładki.

Co jest warunkowe:

- Zakup konkretnego skanera zależy od testu z sekcji „Test przed zakupem”. Kryteria są liczbowe; skaner, który ich nie spełni, nie wchodzi w grę niezależnie od ceny.
- Poranek przez skaner zależy od jakości skanu spieczonych prac bez sprayu; jeśli pokrycie jest zbyt niskie, kamera nad ramką LED przejmuje poranek (koszt ok. 2 tys. zł, osobny moduł programu).
- Zamówienie płytek, wkładek i pokrywek zależy od potwierdzenia pola skanowania skanera ([R54] założenie: koło ø100 mm wokół osi stolika widoczne w całym obrocie): odpowiedź Aidite lub dystrybutora o zakres skanowania albo skan kartonowej makiety z okręgami na egzemplarzu testowym (kryterium 8). Korpusy i blaty nie zależą ani od tego, ani od pomiarów elektroniki.
- Automatyczne klikanie w programie producenta (bez dotykania myszki) zależy od tego, czy jego okna są stabilne; w razie czego technik klika sam „nowy skan → skanuj → zapisz”.

## Lista zakupów z parametrami

Skaner to ok. 85–90% kosztu; reszta to elektronika ramek, druk 3D i osłona. Ceny są orientacyjne, do potwierdzenia ofertą. Pełna lista zakupów i druku jest w osobnym dokumencie „Zakupy i druk — stanowisko kontroli cyrkonii”; uzasadnienie każdego elementu ramki i jego zamienniki — w dokumencie „Budowa ramki — decyzje i zamienniki”.

### Skaner i laptop

| Pozycja | Parametry, które mają znaczenie | Ilość | Cena orientacyjna | Uwagi |
|---|---|---|---|---|
| Skaner laboratoryjny Aidite A-IS Pro 3 | 2 kamery 5 MP, dokładność 8 µm, światło niebieskie, eksport STL/PLY/OBJ, USB 3.0, 385 × 260 × 270 mm, 5 kg; wymagany tryb ręczny lub własna ścieżka skanu (obrót bez przechyłu); spokojny obrót stolika, bez szarpnięć przy starcie i zatrzymaniu (regulowana prędkość albo potwierdzenie w teście, kryterium 2); pole skanowania przy obrocie stolika: koło ø100 mm wokół osi ([R54] założenie, do potwierdzenia na egzemplarzu testowym, kryterium 8) — gniazda i znaczniki płytki leżą w kole o promieniu 47 mm | 1 | 20–25 tys. zł (oferta Aidite) | Warunek: pozytywny test z sekcji „Test przed zakupem” |
| Zamiennik 1: Shining AutoScan-DS-EX Pro(H) | Ta sama klasa: 2 × 5 MP, ≤ 8 µm, łuk 14 s, licencja wieczysta | — | ok. 7 tys. USD (USA), z Chin taniej | Gdy Aidite nie da trybu bez przechyłu |
| Zamiennik 2: DOF Freedom X5/UHD | Kamera jeździ wokół nieruchomego modelu, 5 MP, bez uchwytów | — | na zapytanie | Zdejmuje problem przechyłu konstrukcyjnie |
| Zamiennik 3: 3Shape F8 | Skan bez przechyłu, 4 × 5 MP, 4 µm, łuk 9 s, ScanIt Dental w zestawie, LabCare opcjonalny | — | na zapytanie, raczej ponad budżet | Najlepszy sprzęt, najwyższa cena |
| Laptop (daje firma) | Windows 11, i7/i9, 32 GB RAM, karta graficzna RTX, 1 TB SSD, 2 × USB 3.0, Excel/Outlook/OneDrive | 1 | — | Wymagania producentów skanerów: 16–32 GB, dedykowana karta |
| Opcja: kamera przemysłowa | 20 Mpx USB3 (Sony IMX183), np. Hikrobot MV-CS200-10UC + obiektyw 25 mm C-mount, panel LED podświetlający | 1 | 1,8–2,5 tys. zł | Tylko jeśli skan spieczonych prac wypadnie słabo (plan B poranka) |

### Ramki i płytki — streszczenie (pełna lista w dokumencie „Zakupy i druk”, uzasadnienia w „Budowa ramki — decyzje i zamienniki”)

Szczegółowa lista zakupów (parametry do wyszukania w sklepie, ilości, ceny), tabela części do drukarni z objętościami, ustawienia drukarek i checklista odbioru są w osobnym dokumencie „Zakupy i druk — stanowisko kontroli cyrkonii” (tam też linki do sklepów i drukarni); dlaczego każdy element jest taki, czy można go zmienić i z czego zrezygnowano — w dokumencie „Budowa ramki — decyzje i zamienniki”. Tu tylko streszczenie w 10 pozycjach (ceny orientacyjne z planu budowy v2):

| Nr | Pozycja | Co obejmuje | Gdzie | Kiedy zamawiać | Cena orientacyjna |
|---|---|---|---|---|---|
| 1 | Elektronika dwóch ramek | 2 panele LED 64 × 64 (P2.5), 2 Raspberry Pi 4 B 2 GB z radiatorami, 2 nakładki RGB Matrix Bonnet, 2 zasilacze 5 V 4 A, 2 karty 32 GB, klawiatura numeryczna 2,4 GHz z odbiornikiem USB | Botland, Kamami, Allegro, AliExpress (panele) | od razu | ok. 1 000–1 300 zł |
| 2 | Gniazda, kable, czujniki, drobne | 2 gniazda DC panelowe i wtyki, 2 gniazda USB panelowe, 10 czujników Halla, rezystory, 30 magnesów ø5 × 2, przewody, złącza, płytki prototypowe, podstawki opasek i taśma VHB, stopki, klej | Botland, Kamami, Allegro | od razu | ok. 150–250 zł |
| 3 | Sprzęt mocujący panel i blat | 8 dystansów M3 żeńsko‑żeńskich 50 mm (albo 45 mm + tulejki klejone, gdy panel nie ma gwintu), wkręty dociskowe M3 × 5, wkręty M3 × 10 z podkładkami ø9, wkręty M3 × 8, wkręty do tworzyw, śruby M2,5, epoksyd | Botland, Kamami, Allegro | od razu (dystanse w obu długościach albo po sprawdzeniu gwintu panelu) | ok. 80–120 zł |
| 4 | Pleksi mleczna 2 mm 160 × 160 | 2 szt. + 1 zapas, cięcie na wymiar | pleksi mleczna na wymiar, cięcie laserem: PlasticExpress, Plexigo, eplexi24, Plexinet | od razu | 10–20 zł/szt. |
| 5 | Korpusy i blaty (drukarnia, PA12 grafit) | korpus „RAMKA WIECZORNA”, korpus „RAMKA PORANNA”, 2 blaty | drukarnia MJF/SLS PA12, np. Cadxpert (Poznań), Spes3D (Wrocław), P3DRC, Send3D, Laboratorium Druku 3D (Gliwice); wyceny u 2–3 | od razu — pliki ostateczne (nie zależą od pomiarów ani od skanera) | 551–980 zł (najtańszy) / 860–1 528 zł (pokazowy) |
| 6 | Płytki poranne nr 4–6 (drukarnia, PA12 biały) | 3 szt., 23 gniazda + 1 rynienka [R59] | drukarnia jak w poz. 5 (to samo zamówienie lub ta sama firma) | po potwierdzeniu pola skanowania i decyzji właściciela o kształcie płytek [R59] | 162–288 zł |
| 7 | Płytki wieczorne nr 1–3 (drukarnia, PA12 biały) | 3 szt., 18 gniazd + 1 rynienka [R59] [R55] | drukarnia jak w poz. 5 | po potwierdzeniu pola skanowania i decyzji właściciela o kształcie płytek [R59] | 161–286 zł |
| 7a | Płytki okrągłe nr 8 (wieczorna) i 9 (poranna) — drugi kształt płytki [R57], nowy układ gniazd [R59] (drukarnia, PA12 biały mat, bez wygładzania) | 2 szt., ø100 × 8 mm, te same gniazda i stożki co nr 1–3 / 4–6 (18 gniazd i 1 rynienka / 23 gniazda i 1 rynienka), ścięcie orientacyjne na obwodzie; tylko do skanera — nie pasują do wkładki ramki | drukarnia jak w poz. 5 | po decyzji właściciela, który skłania się ku okrągłym [R59] | 89–158 zł |
| 8 | Wkładki gniazda płytki (drukarnia, PA12 biały) | 2 + 1 zapas; prototyp z PETG (FDM u kolegi) przed zamówieniem [R55] | drukarnia jak w poz. 5 | po potwierdzeniu pola skanowania | 34–60 zł |
| 9 | Druk własny [R55: wszystko PETG, FDM u kolegi] | 4 pokrywki; 2 tulejki gniazda zasilania i 3 × 8 podkładek panelu (po pomiarach); płytka do testu skanera (PETG biały matowy) i prototypy pasowań | drukarka FDM u kolegi | pokrywki po potwierdzeniu pola; tulejka i podkładki po pomiarach; prototypy od razu | koszt filamentu |
| 10 | Osłona, pokrowce, drobne stanowiska | osłona z czarnej płyty nad ramką przy skanerze (ok. 30 × 30 × 35 cm), pokrowce, hub USB 3.0, kable, listwa, ściereczki | Allegro, sklepy budowlane (płyta na osłonę) | przed uruchomieniem | 300–600 zł |

Razem bez skanera: elektronika i drobne 1 200–1 680 zł, drukarnia 907–1 613 zł (najtańszy, PA12 naturalny i grafit bez wygładzania) lub 1 216–2 161 zł (pokazowy: korpusy i blaty barwione i wygładzane), osłona i drobne stanowiska 300–600 zł — razem ok. 2,4–3,9 tys. zł (do 4,4 tys. zł w wariancie pokazowym). [R57] Płytki okrągłe nr 8 i 9 (poz. 7a) dokładają do drukarni 89–158 zł: razem z nimi drukarnia 996–1 771 zł (najtańszy) / 1 305–2 320 zł (pokazowy); sumy ogółem w tym dokumencie rosną o mniej niż 0,2 tys. zł. [R59] Kwoty druku pochodzą z arkusza zamówienia nowego układu gniazd.

Razem bez opcji: skaner 20–25 tys. zł + ramki, płytki, osłona i drobne 2,4–3,9 tys. zł = ok. 22,4–29 tys. zł. Z kamerą (plan B poranka): dodatkowo ok. 2 tys. zł.

Czego nie kupujemy: żadnego oprogramowania (program producenta jest w zestawie ze skanerem; reszta własna, na bibliotekach otwartych), żadnych subskrypcji, żadnych sprayów ani znaczników na prace. Elementy, z których świadomie zrezygnowano, i powody są opisane w dokumencie „Budowa ramki — decyzje i zamienniki”.

## Architektura rozwiązania prostym językiem

Skaner dostarcza tylko pliki STL; cała logika siedzi w jednym programie na laptopie, który czyta projekty i raporty z lewej strony, a steruje ekranem, diodami i arkuszem z prawej.

architektura · 4 źródła danych, 1 program, 3 wyjścia (schemat w wersji PDF)

Żadne dane nie opuszczają firmowego laptopa ani firmowego Microsoft 365, a prace nie dostają żadnych oznaczeń.

Elementy i ich rola:

1. **Skaner laboratoryjny** — mierzy całą płytkę naraz i zapisuje jeden plik STL (siatka trójkątów ze wszystkimi pracami i płytką). Jego własny program obsługuje skan i eksport; nasz program czeka na plik w folderze.
2. **Płytka z gniazdami** — nadaje pracom znane miejsca: program wie, gdzie na płytce jest gniazdo numer 13, więc może powiedzieć „czerwone jest 13” i zapalić diodę dokładnie pod nim. Trzy stożki w narożnikach pozwalają programowi wyrównać skan do rysunku płytki z dokładnością poniżej 0,1 mm; współrzędne gniazd leżą w pliku obok modelu, więc zmiana układu nie wymaga zmiany kodu. [R59] Program zna dwa układy gniazd — nowy i poprzedni — bo płytki wykonane wcześniej zostają w użyciu; gdy zeskanowana płytka nie pasuje do wybranego układu, ostrzega.
3. **Projekty STL** — wzorzec, do którego porównujemy. Wieczorem projekt jest powiększony o współczynnik skurczu krążka (z raportu MillBox), rano w wymiarach 1:1.
4. **Dopasowanie 3D** — program najpierw zgaduje, który projekt pasuje (objętość, wymiary, kształt), potem nakłada go na pomiar z dokładnością do setnych milimetra (algorytm ICP, otwarta biblioteka Open3D).
5. **Wykrywanie ubytków** — po nałożeniu liczymy, gdzie pomiar leży pod powierzchnią projektu. Mały, ostry, lokalny ubytek przy brzegu to ukruszenie; gładka, rozległa różnica to ręczna poprawka technika albo luz pasowania i nie jest zgłaszana.
6. **Identyfikacja** — rano to samo dopasowanie, ale do puli zleceń z ostatnich dni; wynik to numer kuwety i nazwa zlecenia (nazwa folderu, równa kolumnie H w Excelu).
7. **Ramki świetlne** — dwie: przy skanerze (wieczór: czerwone gniazda do sprawdzenia) i w pokoju rozkładania (poranek: zielone gniazda bieżącej kuwety, jej numer na marginesie matrycy wokół płytki). Każda rozpoznaje płytkę po magnesach w jej spodzie i rozmawia z laptopem przez Wi‑Fi. Czerwień = sprawdź, zieleń = bieżąca kuweta, bursztyn = poprawka, biel = praca nieznana. Stan ramki pokazuje kolor marginesu matrycy; skan uruchamia spacja na laptopie, rano kuwety przełącza bezprzewodowa klawiatura numeryczna. Ramki obsługuje się wyłącznie z laptopa i tej klawiatury.
8. **Excel** — program steruje Excelem otwartym na laptopie (plik z SharePointa, Autozapis włączony), więc zmiana koloru pola wygląda tak, jakby zrobił ją człowiek i natychmiast widzą ją inni.

Gdzie co mieszka:

- Na laptopie: program stanowiska, lokalna baza (SQLite) ze skanami, decyzjami i logiem odhaczeń, kopie STL z OneDrive, folder eksportu skanera.
- W firmowym M365: Excel produkcyjny (tylko kolor pola B), foldery STL. Program niczego tam nie tworzy poza zmianą koloru.
- Nigdzie w chmurach zewnętrznych: zero wysyłania danych, zero kont u dostawców oprogramowania.

## Przepływ wieczorny krok po kroku

Wieczór zmienia się w jednym miejscu: zamiast odkładać wycięte prace na tackę, technik odkłada je do gniazd płytki, a przed opakerem ogląda tylko te, które program oznaczył na czerwono.

wieczór · 5 kroków, 1 decyzja, pętla fałszywego alarmu (schemat w wersji PDF)

Decyzja o każdym czerwonym gnieździe należy do technika; program zapamiętuje jego werdykt, co z czasem obniża liczbę fałszywych alarmów.

Krok po kroku (technik):

1. Wycina prace z krążka i szlifuje piny jak dziś. Każdą gotową pracę odkłada do wolnego gniazda płytki brzegiem do góry (powierzchnią żującą w dół); most do rynienki. [R59] Rynienka jest jedna, więc na płytkę przypada jeden most; drugi czeka na następną płytkę. Do rynienki idzie też praca za duża na gniazdo ø15 mm. Rozmiar gniazda dobiera na oko — program nie dba, które gniazdo. Płytka ma z przodu rynienkę, za nią rząd gniazd ø12 mm i trzy rzędy gniazd ø15 mm.
2. Gdy płytka jest pełna albo krążek skończony: wsuwa płytkę do skanera do oporu (wycięcie orientacyjne wymusza jedno ułożenie) i naciska spację na laptopie. Zaczyna ładować drugą płytkę albo wraca do wycinania.
3. Po 60–90 s ekran pokazuje mapę płytki: zielone gniazda bez uwag, czerwone z podejrzeniem ubytku, szare „bez projektu” (program nie dopasował żadnego STL — ogląda się jak dziś, gołym okiem). Ramka przy skanerze świeci to samo pod płytką, gdy technik ją na niej położy.
4. Wyjmuje płytkę. Czerwone prace bierze do ręki; kliknięcie czerwonego gniazda na ekranie laptopa pokazuje pracę w 3D z mapą odchyłek (od turkusu do czerwieni) i powiększeniem miejsca ubytku z jego rozmiarem.
5. Decyzja jednym przyciskiem na ekranie: „Ukruszona” — praca idzie na bok, program dopisuje do dziennej listy „do dofrezowania” zlecenie, ząb i krążek i zapamiętuje, że tego punktu zabraknie rano (dofrezowany ząb wyjdzie z innego pieca, zwykle następnego dnia); „OK” — fałszywy alarm, praca wraca do obiegu.
6. Reszta prac idzie do opakera i pojemników do pieca dokładnie jak dziś. Nic nie jest zapisywane o tym, która praca do którego pieca.

Co robi program w tle:

- Czeka na nowy plik STL w folderze eksportu skanera i zaczyna analizę w ciągu sekundy od zapisu.
- Wyrównuje skan do rysunku płytki po trzech stożkach znaczników, odczytuje numer płytki z dołków kodu i tnie skan na gniazda.
- Dla każdego gniazda szuka projektu w puli dnia (lista STL z raportów MillBox, każdy powiększony o współczynnik swojego krążka): najpierw po objętości i wymiarach (odrzuca 90% kandydatów w ułamku sekundy), potem po kształcie (dopasowanie 3D). Próg akceptacji: co najmniej 85% powierzchni skanu w odległości do 0,05 mm od projektu.
- Liczy mapę odchyłek i wyszukuje ubytki: obszary, gdzie skan leży co najmniej 0,08 mm pod powierzchnią projektu, o średnicy 0,2–1,5 mm, z ostrą krawędzią, w pasie do 1,5 mm od brzegu lub na krawędziach. Progi są w ustawieniach i stroi się je na próbie testowej.
- Odróżnia poprawkę ręczną: gładka różnica na obszarze większym niż 2 mm bez ostrej krawędzi nie jest zgłaszana.
- Zapisuje w lokalnej bazie: plik skanu, gniazdo, dopasowany projekt, wynik, decyzję technika, czas.

Czas na płytkę (do 18 koron i 1 mostu): ułożenie w gniazdach zastępuje odkładanie na tackę (bez dodatkowego czasu), zaniesienie i start 15 s, skan 30–60 s i analiza 20–40 s w tle, spojrzenie na ekran i wyjęcie czerwonych 30–60 s. Netto 1–2 min pracy technika na płytkę, czyli 10–20 min na typowy wieczór z 7–10 płytkami.

Sytuacje szczególne:

- Praca bez projektu w puli (np. dofrezowana z innego krążka, którego raport nie dotarł): gniazdo szare, komunikat „sprawdź ręcznie”; program próbuje także puli z poprzedniego dnia.
- Poprawka z obróbki (jeden ząb dofrezowany do zlecenia, które już wyszło z pieca): program dopasowuje go jak każdą inną pracę, bo jego STL jest w dzisiejszym raporcie MillBox; na ekranie dopisek „poprawka: zlecenie już odhaczone”, żeby rano nikt nie czekał na resztę zlecenia. Nikt niczego nie musi zapisywać przy przyjęciu poprawki.
- Dwie prace w jednym gnieździe albo praca poza gniazdem: gniazdo żółte „popraw ułożenie”, skan do powtórzenia.
- Podwójna powierzchnia w skanie (praca drgnęła w czasie skanu): program to wykrywa i prosi o ponowny skan tej płytki zamiast zgłaszać fałszywe ubytki.
- Most 4-punktowy w rynience: analiza jak dla korony, brzegi każdego punktu i łączniki osobno.
- Prace implantologiczne: wyznacznikiem są brzeg przy łączniku i krawędzie kanału śruby; sam kanał jest wyłączony z analizy.
- [R59] Drugi most na tej samej płytce: nie ma na niego miejsca (jedna rynienka, a w jednym gnieździe jedna praca) — czeka na następną płytkę. Dwa mosty w jednej rynience będą możliwe dopiero po zmianie programu.
- [R59] Ostrzeżenie, że płytka nie pasuje do wybranego układu: na skanerze leży płytka starego układu przy wybranym nowym albo odwrotnie — sprawdzić opis na płytce i wybrać w programie właściwy układ.

## Przepływ poranny krok po kroku

Rano znika szukanie: każda praca z pojemnika dostaje numer kuwety w ciągu minuty od skanu, a diody pod gniazdami pokazują, które prace zabrać do kuwety trzymanej właśnie w ręku.

Przymierzanie na modelach zostaje tam, gdzie jest potrzebne do korekty; przestaje być sposobem na rozpoznanie, do kogo należy korona.

Krok po kroku (osoba rozkładająca piece):

1. Otwiera pojemniki z pieca i przekłada prace (40–70 °C) do gniazd płytek porannych brzegiem do góry. [R59] Płytka poranna ma 23 gniazda i 1 rynienkę: duży piec (40–60 prac) to 2–3 płytki, mały — jedna, w razie potrzeby druga. Na płytkę przypada jeden most.
2. Skanuje wszystkie płytki pieca po kolei: płytka do skanera, spacja na laptopie, w czasie skanu ładuje następną. Po ostatnim skanie program zna cały piec: która praca leży na której płytce i które zlecenia są kompletne.
3. Ekran przy skanerze pokazuje każdą płytkę z podpisami: numer kuwety, nazwisko, numer zęba, miniatura projektu. Gniazda pewne na zielono, dwuznaczne na żółto (dwóch kandydatów), poprawki na bursztynowo („poprawka: 3263”), nieznane na biało. Dwuznaczne rozstrzyga kliknięciem już tutaj (podgląd STL obu kandydatów, kolor z karty zlecenia).
4. Zabiera do pokoju rozkładania to, co dziś: kuwety z szafki pieca oraz płytki z nałożonymi pokrywkami. Wyjmuje z szafki ramkę poranną, stawia na stole i wpina wtyk zasilacza czekający w klipsie przy krawędzi stołu (gniazdo jest wgłębione w tylnej ściance, wtyk kątowy nie wystaje poza obrys ramki); ramka startuje sama w 30–40 s i łączy się z Wi‑Fi. Klawiatura numeryczna leży obok. Po rozłożeniu pieców ramka wraca do szafki.
5. Kładzie płytkę na ramce porannej (kołek orientacyjny wchodzi w wycięcie płytki, więc leży tylko w jednej orientacji). Ramka rozpoznaje ją po magnesach w spodzie i pobiera jej plan z laptopa. Na marginesie matrycy wokół płytki świeci numer bieżącej kuwety i liczba prac („3263 · 4”), pod tymi pracami zielone diody. Prace idą do kuwety, Enter na bezprzewodowej klawiaturze potwierdza i przełącza na kolejną kuwetę (Backspace cofa).
6. Sposób wyboru kuwet ustawia się raz i zmienia w każdej chwili: program proponuje kolejne (od najliczniejszej albo według numeru) albo osoba sama wpisuje numer kuwety na klawiaturze (bierze kuwetę z półki, wpisuje 3263, świecą jej prace; jeśli prace tej kuwety leżą też na innej płytce, ramka to pokazuje).
7. Po płytce 1 zdejmuje ją (ramka widzi brak płytki i czeka) i kładzie płytkę 2 — ramka sama przełącza się na jej plan. Prace nieznane (brak kandydata) zostają na płytce na koniec, podświetlone na biało: przymiarka na modelach jak dziś, a ramka pokazuje numery zleceń, którym brakuje prac.
8. Po ostatniej płytce pieca: „Zamknij piec” (osobny klawisz na klawiaturze ramki porannej albo przycisk na laptopie). Zlecenia, których wszystkie punkty zostały rozpoznane — dziś albo w poprzednich dniach i piecach — odhaczają się w Excelu; niepełne trafiają na listę braków „brakuje: 3263 ząb 46” (praca w innym piecu, dofrezowywana po wieczornym ukruszeniu, została w pojemniku albo zaginęła). Poprawki pojedynczych zębów nie czekają na komplet: Excel bez zmian, wpis w logu. Następny piec od kroku 1; lista braków uzupełnia się sama, gdy brakująca praca wyjdzie z kolejnego pieca.

Co robi program w tle:

- Pula kandydatów: wszystkie zlecenia cyrkoniowe, których pliki frezowano w ostatnich 3–4 dniach roboczych (według raportów MillBox i folderu „Cyrkon”; weekendy liczone jako jeden dzień), także te z zielonym już polem B w Excelu, bo poprawki i dofrezowane zęby wracają do zleceń formalnie zamkniętych; plus folder „Prywatne”. Pula odświeża się co noc; miniatury i cechy kształtu są policzone z góry.
- Dopasowanie w wymiarach 1:1 (spieczona praca równa się projektowi); skan spieczonej pracy bywa dziurawy, więc próg pewności jest niższy niż wieczorem, a wynik to ranking: pewny, gdy drugi kandydat pasuje wyraźnie gorzej.
- Sesja pieca: program trzyma listę płytek jednego pieca i zlicza, ile punktów każdego zlecenia już rozpoznał.
- Pamięć między piecami i dniami: lista braków i stan zleceń są trwałe (lokalna baza). Ząb odłożony wieczorem jako „Ukruszona” od razu trafia na listę braków swojego zlecenia; gdy dofrezowany wyjdzie z dowolnego pieca, program rozpozna go po tym samym STL, domknie zlecenie i dopiero wtedy odhaczy Excel.
- Ramki i płytki: każda płytka ma magnesy w spodzie (kod dla ramki) i kod geometryczny (dołki przy lewej krawędzi) czytany ze skanu, więc program wie, która płytka została zeskanowana i która leży na ramce. Ramka poranna dostaje przez Wi‑Fi plan płytki (gniazdo → kuweta), odsyła potwierdzenia i wpisane numery; przy braku sieci trzyma ostatni plan w pamięci i dosyła potwierdzenia po powrocie łączności.
- Excel: tylko po „Zamknij piec”, tylko zlecenia kompletne; jeśli pole B jest już zielone (poprawka, dofrezowanie, reklamacja), program nic nie zapisuje i tylko loguje; każda zmiana w logu z datą, numerem kuwety i nazwą folderu.

Czas (duży piec, 40–60 prac, 2–3 płytki poranne [R59]): przełożenie do gniazd zastępuje wyjmowanie na blat; skany 2–3 × 90 s w tle przy piecu; w pokoju rozkładania ok. 8–12 s na pracę według diod, dwuznaczne i nieznane 20–30 s na pracę. Cel: 20–25 min na duży piec zamiast 40, bez osobnego odhaczania w Excelu.

Plan B poranka: jeśli skan spieczonej, przeziernej cyrkonii bez sprayu daje mniej niż ok. 70% powierzchni, poranek przejmuje kamera 20 Mpx nad ramką LED: jedno zdjęcie płytki, identyfikacja po obrysie i widoku wnętrza, te same diody i ten sam Excel. Decyzja po teście z sekcji „Test przed zakupem”.

## Ramki świetlne i płytki — projekt, zakupy, montaż

### Co to jest i jak działa

Ramka to „dom” płytki poza skanerem: zamknięta kostka 200 × 200 × 63,6 mm (korpus 59,6 mm + blat 4 mm) z matrycą 64 × 64 diod pod mleczną szybką. Wysokość jest ustalona z zapasem 8 mm nad elektroniką, więc nie zmienia się po zmierzeniu kupionych części. Płytka leży na środku we wkładce; wokół niej zostaje pas matrycy ok. 28 mm (11 pikseli) z każdej strony na cyfry i kolor stanu. Diody świecą przez otwory w dnie gniazd. W środku: Raspberry Pi 4 z nakładką sterującą matrycą (pod środkiem panelu), panel na 4 mosiężnych dystansach, zasilacz 5 V. Z zewnątrz: z tyłu kieszeń wgłębiona (okno 51 × 24 mm) z gniazdem zasilania w jej bocznej ścianie — wtyk kątowy (zalecany) ani prosty o korpusie do 37 mm od lica nie wystaje poza obrys, więc ramkę można wsuwać do szafki — oraz gniazdo USB serwisowe z zaślepką; szczeliny wentylacyjne nisko w ścianach (4 z tyłu, po 3 z boków) i 2 wloty w dnie; stopki klejone na płaskim dnie; karta pamięci dostępna po zdjęciu blatu i panelu. Z przodu tylko wytłoczony napis. Wierzch blatu jest gładki: blat trzymają 4 zatrzaski i 2 wkręty w tylnej ściance. Dlaczego każdy z tych elementów jest taki i co można zmienić, opisuje dokument „Budowa ramki — decyzje i zamienniki”.

Obie ramki mają identyczną obudowę i elektronikę. Różnią się tylko:

- odbiornikiem USB klawiatury numerycznej wpiętym do Raspberry Pi w ramce porannej,
- napisem na przedniej ściance: „RAMKA WIECZORNA” / „RAMKA PORANNA”.

Ramka wieczorna stoi przy skanerze pod osłoną i po skanie pokazuje czerwone i zielone gniazda. Ramka poranna między porankami leży w szafce, rano stawia się ją na stole w pokoju rozkładania. Obie rozmawiają z laptopem przez firmowe Wi‑Fi (zapas: hotspot laptopa).

Wkładka gniazda (biała rama na blacie) jest osobną, tanią częścią: ustala położenie płytki z powtarzalnością ±0,5 mm, niesie 3 czujniki magnetyczne pod narożnikami płytki i kołek orientacyjny, który wchodzi w wycięcie płytki. Jeśli test skanera wymusi mniejszą płytkę, wymienia się tylko wkładkę, nie ramkę.

Płytki: obie 96 × 96 × 8 mm, ten sam obrys, więc ta sama wkładka. Każda ma 3 stożki narożne dla skanera, wycięcie orientacyjne w czwartym narożniku, dołki kodu przy lewej krawędzi (skaner czyta numer płytki ze skanu), kieszenie na magnesy od spodu (ramka czyta numer przez czujniki), wytłoczoną cyfrę i rowek na pokrywkę. Numery 1–3 to płytki wieczorne, 4–6 poranne; brak magnesów = brak płytki. Pokrywka (jedna na obie płytki) zatrzaskuje się w rowek i zostawia 14 mm prześwitu nad płytką.

| Część | Ile | Materiał | Skąd |
|---|---|---|---|
| Płytka wieczorna nr 1, 2, 3 | 3 | PA12 biały, mat [R55] | drukarnia |
| Płytka poranna nr 4, 5, 6 | 3 | PA12 biały, mat (znosi 40–70 °C) | drukarnia |
| Pokrywka | 4 | PETG | sami (FDM u kolegi) |
| Korpus (napis W / P) | 2 | PA12 grafit | drukarnia |
| Blat | 2 | PA12 grafit | drukarnia |
| Wkładka gniazda | 2 + 1 zapas | PA12 biały | drukarnia (prototyp z PETG u kolegi [R55]) |
| Tulejka redukcyjna gniazda zasilania (gdy gniazdo ma gwint ø8) | 2 | PETG [R55] | sami (FDM u kolegi) |
| Podkładki pod dystanse panelu 0,5 / 1 / 2 mm | 3 × 8 | PETG [R55] | sami (FDM u kolegi) |

### Nowy układ gniazd płytek [R59]

Płytki mają nowy układ gniazd: większe gniazda w miejscu małych i jedną rynienkę zamiast dwóch. Obrys płytki, ramka, wkładka i pokrywka zostają bez zmian — zmieniły się tylko pliki płytek.

| Płytka | Było | Jest |
|---|---|---|
| Wieczorna (nr 1–3, okrągła nr 8) | 18 gniazd: 7 × ø9, 6 × ø12, 5 × ø15; 2 rynienki 60 × 15 mm | 18 gniazd: 6 × ø12, 12 × ø15; 1 rynienka 60 × 15 mm |
| Poranna (nr 4–6, okrągła nr 9) | 31 gniazd: 18 × ø7,5, 7 × ø10, 6 × ø12,5; 2 rynienki 50 × 13 mm | 23 gniazda: 20 × ø12,5, 3 × ø15; 1 rynienka 50 × 13 mm |

Po co. Prace są większe, niż zakładał poprzedni układ. W próbie 17 projektów w najmniejsze gniazda (ø9 wieczorem, ø7,5 rano) nie weszła żadna praca — 0 z 17 — a 2 z 17 były za duże na największe gniazdo i zajmowały rynienkę. W nowym układzie w każde gniazdo wchodzi któraś praca z próby: wieczorem gniazd ø15 jest 12 zamiast 5, rano doszły 3 gniazda ø15, których wcześniej nie było. Próba jest mała i dobrana do testów programu, nie jest przekrojem produkcji — układ sprawdzi dopiero codzienna praca.

Co to kosztuje:

- Jeden most na płytkę. Rynienka jest jedna, a program przyjmuje jedną pracę w jednym gnieździe. Drugi most czeka na następną płytkę.
- W próbie rynienki wymagało 6 z 17 prac (dłuższe niż 20 mm). Wieczorem dochodzą 2 prace, które nie mieszczą się w gnieździe ø15, więc rynienki wymaga wtedy 8 z 17.
- Płytka poranna ma 23 gniazda zamiast 31. Duży piec (40–60 prac) to 2–3 płytki zamiast 2.
- Najmniejsze gniazdo ma ø12 mm wieczorem i ø12,5 mm rano. Czy najmniejsze prace leżą w nim pewnie przy obrocie stolika, sprawdzi test skanera (kryterium 2).
- Dwa mosty na jednej płytce wymagają zmiany programu. To osobna praca, bez ustalonego terminu.

Co ze starymi płytkami:

- Płytki wykonane w poprzednim układzie zostają w użyciu. Na płytce wieczornej poprzedniego układu idą pierwsze skany, gdy tylko skaner będzie na miejscu; nowe płytki zamawiamy w tym czasie.
- Program zna oba układy: nowy i poprzedni (pod nazwą z dopiskiem `_r54`). Układ wybiera się w programie ręcznie. Gdy zeskanowana płytka nie pasuje do wybranego układu, program ostrzega.
- Numery płytek są te same w obu układach: 1–3 wieczorne, 4–6 poranne, 8 i 9 okrągłe. Numer z dołków kodu nie odróżnia więc starej płytki od nowej.
- Dlatego stare płytki trzeba opisać trwałym napisem na boku (na przykład „stary układ”) i trzymać osobno od nowych.

Co zamawiamy:

- Właściciel skłania się ku płytkom okrągłym. Co i ile zamówić, zdecyduje po odbiorze plików nowego układu. Ilości w arkuszu zamówienia zostają bez zmian.
- Płytka okrągła ma te same gniazda co kwadratowa tego samego typu: wieczorna 18 gniazd i 1 rynienkę, poranna 23 gniazda i 1 rynienkę. Kształt płytki nie zmienia liczby gniazd.
- Płytka okrągła działa dziś tylko w skanerze. Żeby leżała na ramce świetlnej, potrzebna jest zmiana R58 (okrągła wkładka i pokrywka).
- Do drukarni idą wyłącznie pliki o sumach SHA‑256 z dokumentu „Zakupy i druk”. Pliki poprzedniego układu mają te same nazwy, ale inne sumy.

### Co zamawiamy w drukarni, a co drukujemy sami — i dlaczego

Zasada: części widoczne i nośne zamawiamy (MJF/SLS, nylon PA12), części ukryte lub robocze drukujemy sami z PETG na drukarce FDM u kolegi (nie z PLA, bo pokrywka i płytka poranna widzą 40–70 °C). [R55] Druk własny wyłącznie z PETG; technologie i materiały odrzucone wraz z powodami opisuje „Budowa ramki — decyzje i zamienniki”.

Drukarnie do wyceny części PA12 (MJF lub SLS, od 1 sztuki): Cadxpert (Poznań), Spes3D (Wrocław), P3DRC, Send3D, Laboratorium Druku 3D (Gliwice) — wyceny u 2–3 z nich; pleksi mleczna na wymiar z cięciem laserem: PlasticExpress, Plexigo, eplexi24, Plexinet. Pełna lista z linkami i uwagami (minimalne zamówienie, kalkulatory) jest w dokumencie „Zakupy i druk”.

| Część | Decyzja | Dlaczego |
|---|---|---|
| Korpus W i P, blat | zamówić (PA12 grafit) | największe części, gładki grafit na pokaz; zatrzaski i kieszenie wymagają dokładności; kołnierz 194 mm w FDM się wypacza |
| Płytki poranne nr 4–6 | zamówić (PA12 biały) | prace 40–70 °C; mat biały dla skanera |
| Płytki wieczorne nr 1–3 | zamówić (PA12 biały) [R55] | mat biały dla skanera, sztywność i dokładność stożków jak w porannych |
| Wkładka gniazda | zamówić 2 (PA12 biały) + wydrukować 1 prototyp z PETG u kolegi przed zamówieniem [R55] | tania, ale to ona decyduje o pasowaniu płytki; prototyp sprawdza kołek, półki i kieszenie czujników |
| Pokrywka × 4 | sami (PETG, FDM u kolegi) | oszczędność ok. 110–190 zł; zatrzaski wymagają ciągliwości PETG; gładki wierzch, drukowana wierzchem do stołu |
| Tulejka gniazda zasilania × 2, podkładki panelu 3 × 8 | sami (PETG, FDM u kolegi, po pomiarach) [R55] | małe części, druk w minuty; potrzebne tylko gdy gniazdo ma gwint ø8 lub dystans wymaga wyrównania; tulejka ø11,85 po wydruku sprawdzana w otworze ø12 korpusu — przy luzie lub zacisku skalowanie XY w slicerze ±1 %, bez zmiany pliku; podkładka 0,5 mm to 3–5 warstw 0,1–0,2 mm |
| Prototypy pasowań | sami przed zamówieniem: 1 płytka, 1 wkładka, 1 pokrywka, próbka zatrzasku blatu | test realnych luzów za kilka złotych materiału, zanim pójdzie ok. 1 500 zł do drukarni |
| Płytki okrągłe nr 8 i 9 [R57] | zamówić po decyzji właściciela, który skłania się ku okrągłym [R59] (PA12 biały mat, bez wygładzania, ±0,3 mm) | drugi kształt płytki: te same gniazda i stożki co w kwadratowej tego samego typu, więc różni je tylko obrys; okrągła nie ma wystających rogów, a jej dołki kodu leżą w polu ø100; nie pasuje do wkładki ramki — do użycia na ramce potrzebna przyszła zmiana R58 (wkładka i pokrywka okrągłe) |
| Płytka do testu skanera | 1 płytka wieczorna nr 1 z PETG białego matowego (FDM u kolegi) [R55], gotowa na test egzemplarza skanera | rozstrzyga, czy program widzi 3 stożki i dołki kodu oraz czy prace zostają w gniazdach; pole skanowania mierzy osobno kartonowa makieta z okręgami (kryterium 8) [R54]; skanera jeszcze nie ma, więc test odbędzie się na egzemplarzu testowym (albo wystarczy pisemna odpowiedź producenta o zakresie skanowania); [R59] płytka wydrukowana przed zmianą układu ma poprzedni układ gniazd — program go zna, a płytkę trzeba opisać jak pozostałe stare płytki |

Jeśli drukarka FDM nie będzie dostępna: zamówić wszystko, a prototypy pasowań zlecić w tej samej drukarni jako tanie próbki przed głównym zamówieniem.

### Montaż i testy (z planu budowy v2, sekcja 9)

Decyzja: wkręty formujące gwint do tworzyw (PT 3,0 × 8 w słupkach blatu i PT 2,5 × 6 pod Raspberry Pi) wkręca się wprost w otwory w nylonie, raz „na sucho” przed montażem (R49; uzasadnienie i zamienniki w „Budowa ramki — decyzje i zamienniki”). Panel trzymają mosiężne dystanse, blat — zatrzaski i 2 wkręty. Każdy krok ma kryterium zaliczenia.

| Krok | Czynność | Kryterium zaliczenia |
|---|---|---|
| 1 | Zamówienie bez pomiarów elektroniki: korpusy i blaty od razu (pliki ostateczne); wkładki i płytki po potwierdzeniu pola skanowania; pomiary elektroniki służą potem tylko doborowi dystansów, tulejki i podkładek | arkusz zamówienia ma objętości wszystkich plików; drukarnia potwierdziła PA12, kolory i gabaryt 200 × 200 × 60 |
| 2 | System na stole: karta z systemem, Wi‑Fi firmowe, biblioteka matrycy, konfiguracja nakładki | zdalne logowanie działa; obraz testowy stabilny bez migotania |
| 3 | Panel + nakładka + zasilacz: wzór testowy, cyfry na marginesie, pomiar poboru prądu | pełna biel < 3,5 A; typowy obraz ramki < 1,5 A; Pi nie restartuje się |
| 4 | Klawiatura (ramka P): odbiornik w Pi, odczyt klawiszy. Ramka W: zdarzenie „Skanuj” wysyłane z laptopa (spacja) przez Wi‑Fi | każdy klawisz daje właściwe zdarzenie; spacja na laptopie zmienia stan ramki W w < 1 s |
| 5 | Czujniki Halla na stole: płytka prototypowa, 3 czujniki, test magnesem | każde wejście reaguje na magnes ≤ 4 mm; odwrócony biegun = brak reakcji (to mówi, którą stroną kleić) |
| 6 | Części z druku: oględziny, wypłukanie proszku, pomiar suwmiarką według checklisty odbioru (dokument „Zakupy i druk”; odchyłka większa niż ±0,5 mm = reklamacja [R53]), pasowanie na sucho: płytka we wkładce, wkładka na blacie, pokrywka na płytce, blat na korpusie | płytka wchodzi i wychodzi bez siły, luz ok. 0,4 mm na stronę [R53]; pokrywka trzyma po odwróceniu; blat zatrzaskuje się i daje się zdjąć ręką |
| 7 | Gwinty: najpierw przewiercić otwory wiertłem ø2,1 (korpus: 4 otwory Raspberry Pi) i ø2,5 (blat: 2 słupki) — usuwa proszek z druku i zarośnięcie otworu [R53]; potem każdy otwór przegwintować raz wkrętem, wolno, bez siły | wiertło przechodzi bez oporu; wkręt wchodzi bez oporu i trzyma; gwint nie wyrobiony po 3 cyklach |
| 8 | Najpierw wpiąć wtyk DC kabla wewnętrznego w gniazdo nakładki (po przykręceniu Pi zostaje tylko 7,5 mm do ściany), potem Pi + nakładka na słupkach, listwa wyprowadzeń. Przed postawieniem panelu wkręcić gniazdo USB panelowe w rowki (od wnętrza jest tylko 14,3 mm do dystansu). Panel: z gwintem — wkręty dociskowe M3 × 5 w otwory panelu, dystanse 50 mm nakręcone; bez gwintu — tulejki klejone epoksydem do spodu panelu + dystanse 45 mm; panel postawiony tak, by dystanse trafiły w rowki dna, 4 wkręty M3 × 10 z podkładkami ø9 od spodu; przy otworach panelu poza rowkami: wiercenie ø4 w dnie w zmierzonym miejscu + podkładka | stos Pi nie dotyka panelu (szczelina ≥ 2 mm); panel równoległy do dna (< 0,5 mm na rogach); nic nie wystaje od strony diod |
| 9 | Pleksi w kieszeni blatu (rogi bez fazowania), próba zamknięcia blatu na korpusie z panelem | blat zamyka się do końca; okno równo nad panelem (< 1 mm); panel nie dotyka spodu blatu |
| 10 | Wkładka: czujniki wklejone w kieszenie półek, przewody w rowkach do płytki prototypowej; magnesy w uszach wkładki i w blacie | wkładka siada na kołkach i trzyma magnesami; płytka testowa wchodzi na kołek tylko w jednej orientacji |
| 11 | Magnesy w płytkach według kodów (nr 1: A; 2: B; 3: A+B; 4: C; 5: A+C; 6: B+C), biegun S w dół, klej | odczyt pokazuje 1…6 dla każdej płytki, 0 bez płytki; stabilny 60 s; zmiana < 100 ms po położeniu |
| 12 | Okablowanie końcowe: gniazdo zasilania przez okno kieszeni w otwór jej bocznej ściany (przy gwincie ø8 najpierw tulejka — drukowana dopiero po zmierzeniu otworu ø12 w gotowym korpusie [R53]), USB panelowe już wkręcone w kroku 8 (flansza z otworami pionowymi: wywiercić 2 × ø3,2 przed krokiem 8), podstawki opasek i płytka prototypowa na taśmie VHB (powierzchnie przemyć alkoholem), opaski, opisy; odbiornik klawiatury (P); stopki 12 mm od krawędzi | żaden kabel nie dotyka diod ani radiatora; blat daje się zdjąć bez rozpinania; obudowa stoi stabilnie; wtyk nie wystaje poza obrys |
| 13 | Kalibracja gniazdo → diody: program zapala kolejno pole pod każdym gniazdem, operator potwierdza lub przesuwa; wynik do pliku obok płytki (osobno wieczorna i poranna) | każde gniazdo z pracą świeci widocznie przez otwór, sąsiednie ciemne |
| 14 | Test 8 h pełnego świecenia z logiem temperatury; po 8 h wyrwanie zasilania | Pi < 70 °C; zasilacz letni; po włączeniu ramka wstaje sama w < 60 s; karta bez błędów |
| 15 | Druga ramka z poprawkami z pierwszej; lista zmian wpisana do planu | obie ramki przechodzą kroki 11–14 |

Narzędzia: lutownica (tylko do kabli), multimetr, wkrętaki (w tym imbus do wkrętów dociskowych), klucz 14 do nakrętki gniazda, pęseta, papier ścierny, klej CA, epoksyd, alkohol do odtłuszczenia, marker, magnes wzorcowy lub kompas (bieguny), suwmiarka, wiertła ø2,1 i ø2,5 (przewiercenie otworów pod wkręty formujące przed pierwszym wkręceniem [R53]), ø3,2 i ø4 (tylko do ewentualnych poprawek), laptop z czytnikiem kart.

## Oprogramowanie: moduły i jak powstanie

Jeden program w Pythonie na laptopie, podzielony na dziewięć modułów, z których każdy da się napisać i przetestować osobno, zanim skaner dotrze — na sztucznych skanach wygenerowanych z prawdziwych projektów STL. Do tego osobny, mały program ramki na Raspberry Pi.

Technologie (wszystkie darmowe, bez subskrypcji):

| Zadanie | Biblioteka | Licencja | Po co |
|---|---|---|---|
| Wczytywanie i geometria siatek | trimesh, numpy | MIT / BSD | STL w pamięci, objętość, wymiary, skalowanie o współczynnik |
| Dopasowanie 3D | Open3D | MIT | Zgrubne dopasowanie (cechy FPFH + RANSAC), dokładne (ICP), odległości skan–projekt |
| Interfejs | PySide6 (Qt) | LGPL | Duże kafelki, mapa płytki, podgląd 3D |
| Baza lokalna | SQLite (wbudowane w Pythona) | public domain | Skany, decyzje, log Excela, metryki |
| Obserwacja folderów | watchdog | Apache 2.0 | Reakcja na nowy STL ze skanera |
| Excel | pywin32 (COM) | PSF | Sterowanie Excelem otwartym na laptopie |
| Raporty MillBox | BeautifulSoup4 (HTML), pypdf (PDF) | MIT / BSD | Lista STL, krążek, współczynnik skurczu |
| Klikanie w program skanera | pyautogui | BSD | Automat „nowy skan → skanuj → zapisz” (opcjonalnie) |
| Diody | Python na Raspberry Pi 4 z nakładką RGB Matrix Bonnet (biblioteka rpi-rgb-led-matrix); klawiatura przez evdev; czujniki Halla na 3 wolnych pinach; łączność z laptopem przez Wi‑Fi w sieci lokalnej (HTTP/WebSocket) | BSD / MIT | Zapalanie gniazd kolorem, cyfry na marginesie, odczyt płytki |
| Testy | pytest | MIT | Testy każdego modułu na danych syntetycznych |

Moduły:

| Moduł | Co robi | Wejście → wyjście | Trudność |
|---|---|---|---|
| catalog | Indeksuje projekty: folder „Cyrkon” (OneDrive), folder „Prywatne”, raporty MillBox; liczy cechy każdego STL (objętość, wymiary, deskryptor kształtu, miniatura) i trzyma je w bazie | foldery → tabela projektów z cechami | średnia |
| plate | Zna rysunek płytki z pliku układu gniazd: współrzędne gniazd, znaczników i dołków kodu; wyrównuje skan do płytki (ICP na stożkach), czyta numer płytki, tnie skan na gniazda, wykrywa gniazda puste, podwójne i prace poza gniazdem; [R59] zna nowy i poprzedni układ gniazd i ostrzega, gdy zeskanowana płytka nie pasuje do wybranego | STL płytki → lista fragmentów z numerem gniazda | średnia |
| match | Identyfikuje fragment: filtr po objętości i wymiarach, zgrubne dopasowanie, ICP, ocena dopasowania; wieczorem pula dnia ze skalą z raportu, rano pula 3–4 dni w skali 1:1; zwraca ranking kandydatów z pewnością | fragment + pula → kandydat(ci) + transformacja | wysoka |
| inspect | Mapa odchyłek skan–projekt; wyszukuje ubytki (ostre, małe, przy brzegu lub krawędzi); odrzuca gładkie poprawki ręczne; wykrywa podwójne powierzchnie (praca drgnęła) | fragment + projekt → lista ubytków z położeniem i rozmiarem | wysoka |
| session | Logika wieczoru i poranka: stan płytki, decyzje technika, sesja pieca, zliczanie punktów zleceń (trwałe, między piecami i dniami), lista braków, lista „do dofrezowania”, oznaczanie poprawek | zdarzenia → stan | niska |
| ui | Ekran wieczorny (mapa płytki, czerwone gniazda, widok 3D z mapą odchyłek i powiększeniem ubytku), ekran poranny (podpisy, kandydaci, kuweta po kuwecie), ustawienia progów, start skanu spacją, obsługa klawiatury ramki porannej | stan → ekran | średnia |
| indicate | Mapowanie gniazdo → diody, komunikaty do obu ramek przez Wi‑Fi (plan płytki, stan, potwierdzenia z klawiatury) | polecenia → światło | niska |
| excel | Znajduje wiersz zlecenia i koloruje pole B na zielono; log; tryb „pytaj przed zapisem” | zlecenie → zmiana w Excelu + wpis w logu | niska, ale wrażliwa |
| scanner | Obserwuje folder eksportu; opcjonalnie klika w programie producenta; waliduje plik (rozmiar, liczba trójkątów) | plik → zdarzenie „nowy skan” | niska |

Struktura repozytorium: program stanowiska (moduły powyżej), program ramki na Raspberry Pi (matryca, Wi‑Fi, klawiatura, czujniki Halla), modele płytek z plikami układu gniazd (nowy układ i poprzedni, pod nazwą z dopiskiem `_r54`) [R59], testy na danych syntetycznych z prawdziwych STL, narzędzia (generator sztucznych ubytków, raport metryk, kalibracja ramek), jeden plik ustawień (ścieżki, progi, parametry skanera) i instrukcja (uruchomienie, codzienna obsługa, co robić gdy nie działa).

Jak to powstanie z Claude Code (kolejność ma znaczenie):

1. Najpierw generator danych testowych: z 30 prawdziwych projektów STL program tworzy „sztuczne skany” — projekt powiększony o współczynnik, z dodanym szumem pomiarowym (0,02–0,04 mm), z wyciętymi ubytkami o znanym położeniu i rozmiarze (0,2–0,6 mm) i z losowym ułożeniem w gniazdach. Dzięki temu match i inspect da się zbudować i zmierzyć bez skanera.
2. Potem catalog, plate, match, inspect z testami: każda zmiana progu widoczna w liczbach (wykryte / pominięte / fałszywe).
3. Potem session, ui, indicate, excel — na kopii Excela i na ramce.
4. Na końcu scanner i integracja na prawdziwych plikach z testu u dostawcy.

Każdy moduł ma plik z opisem dla Claude Code (co robi, wejście, wyjście, kryterium „działa”), żeby poprawki po miesiącach nie wymagały czytania całego kodu. Kod jest w prywatnym repozytorium; na laptopie stanowiska działa wersja zamrożona, a aktualizacja to jedno polecenie.

## Dane i integracje

Wszystkie dane wchodzą do programu przez zwykłe foldery na laptopie, a jedyny zapis na zewnątrz to kolor jednego pola w Excelu — dlatego nie trzeba żadnej zgody IT na dostęp programowy, a wszystko dzieje się wewnątrz firmowego Microsoft 365.

SharePoint, folder „Cyrkon” (projekty STL):

- Na laptopie stanowiska włączona jest synchronizacja OneDrive dla biblioteki z folderem materiałów; folder „Cyrkon” ma ustawienie „zawsze zachowuj na tym urządzeniu”. Program czyta pliki lokalnie.
- Nazwa folderu zlecenia (np. „Kowalski 3263 zs”) jest kluczem: program wyciąga z niej numer kuwety jako ciąg 1–4 cyfr i normalizuje zera wiodące (3 = 03 = 003), a całą nazwę zachowuje do porównania z kolumną H Excela.
- Pula poranna: foldery zmodyfikowane w ostatnich 3–4 dniach roboczych (piątek obejmuje weekend); każdy STL w folderze to jeden punkt pracy; nazwa pliku STL daje numer zęba, jeśli jest w nazwie.
- Co noc program liczy cechy nowych STL (objętość, wymiary, deskryptor, miniatura) i usuwa z puli zlecenia starsze niż 10 dni.

Raporty zadań MillBox (HTML/PDF):

- Z raportu program bierze: nazwy plików STL w zadaniu, identyfikator krążka, współczynnik skurczu, datę. Współczynnik przypisany jest do każdego STL z tego zadania.
- Folder raportów: udostępniony folder sieciowy albo kopia robiona raz dziennie (skrypt lub ręcznie). Założenie 4.
- Pula wieczorna = STL z raportów z dzisiaj i wczoraj (prace czasem leżą dzień przed wycięciem), każdy w skali ze swojego raportu. Ząb dofrezowany na innym krążku pojawia się w nowym raporcie z nowym współczynnikiem — program trzyma obie wersje.

Zlecenia prywatne (STL w Outlooku):

- Folder „Prywatne/#1234/” z plikami STL, tworzony przez osobę przyjmującą zlecenie (zapis załączników z maila, 10 s). Numer po „#” odpowiada karteczce na kuwecie.
- Program traktuje go jak folder zlecenia z numerem kuwety „#1234”; w Excelu szuka wiersza po numerze zlecenia z maila w kolumnie B lub H (założenie do potwierdzenia na pierwszych trzech zleceniach prywatnych).

Excel produkcyjny (ok. 30 tys. wierszy, wiele arkuszy):

- Plik jest otwarty w Excelu na laptopie stanowiska z Autozapisem (współedycja z innymi użytkownikami działa jak zwykle). Program steruje tym Excelem przez COM; nie otwiera pliku drugi raz i nie zapisuje kopii.
- Program czyta kolumny A–I bieżącego arkusza raz na kilka minut do pamięci (szybkie wyszukiwanie), a zapis robi tylko w jednym polu: kolumna B, wypełnienie stałym zielonym (RGB 198, 239, 206).

Reguły znalezienia wiersza (odwzorowanie tego, co dziś robi człowiek po Ctrl+F):

1. Kandydaci: wiersze, w których kolumna C po normalizacji równa się numerowi kuwety (dokładnie, nie fragment).
2. Zawężenie: kolumna H po normalizacji (małe litery, bez podwójnych spacji, bez zer wiodących w numerze) równa się nazwie folderu z SharePointa. Jeśli pasuje dokładnie jeden wiersz — to on.
3. Jeśli H nie pasuje nigdzie (inicjały zamiast nazwiska, pusta komórka): najnowsza data w kolumnie A spośród kandydatów, pod warunkiem, że nazwisko z nazwy folderu występuje w H albo H jest puste.
4. Jeśli wybrany wiersz ma już zielone pole B: program nic nie zapisuje, tylko loguje „już odhaczone”. Daty w kolumnie A nie da się użyć do rozróżnienia poprawki od reklamacji, bo przy zgłoszeniu poprawki nikt jej nie zmienia. Reklamacja z nowym wierszem (ta sama kuweta, nowa data, pole B puste) łapie się regułami 1–3 i jest odhaczana normalnie.
5. Jeśli po regułach 1–3 zostaje więcej niż jeden wiersz albo żaden: komunikat „Excel: wskaż wiersz” z listą kandydatów; zapis dopiero po wyborze.
6. Każdy zapis trafia do lokalnego logu CSV: data, godzina, numer kuwety, nazwa folderu, numer zlecenia z kolumny B, arkusz, wiersz, kto zatwierdził. Log jest podstawą audytu w pierwszych tygodniach.

Plany B dla Excela: Office Script uruchamiany jednym kliknięciem w Excelu w przeglądarce (program przygotowuje listę kuwet do schowka); docelowo Microsoft Graph po rejestracji aplikacji przez IT — ten sam dostęp przyda się każdej następnej automatyzacji w firmie.

RODO i bezpieczeństwo: nazwiska pacjentów są tylko w nazwach folderów i w Excelu, czyli tam, gdzie są dziś; program nie kopiuje ich nigdzie poza laptop stanowiska, nie wysyła niczego do internetu, a zdjęć i skanów prac nie da się powiązać z osobą bez Excela. Ramki dostają przez Wi‑Fi tylko numery gniazd i kuwet. Laptop jest zalogowany na firmowe konto, z szyfrowaniem dysku i blokadą ekranu.

## Test przed zakupem

Jeden test rozstrzyga wszystko naraz: czy skaner widzi ubytki wielkości pół kryształu cukru na zielonej cyrkonii, czy prace zostają w gniazdach w czasie skanu, czy spieczone prace skanują się bez sprayu, czy ścieżkę skanu da się ustawić bez przechyłu i czy pole skanowania mieści całą płytkę. Skaner, który nie przejdzie kryteriów, nie wchodzi w grę niezależnie od ceny.

Gdzie i z kim: najlepiej egzemplarz testowy Aidite A-IS Pro 3 u nas (relacja dużego klienta); równolegle zapytanie do DOF (Freedom X5/UHD) i 3Shape (F8) o wycenę i ten sam test u dystrybutora. Wcześniej, bez kupowania czegokolwiek, próba ze skanerem wewnątrzustnym Medit i700/i900 z firmy: ten sam zestaw prac, ręczny skan, ocena w CloudCompare — odpowiada na pytanie o widoczność ubytków w świetle strukturalnym.

Do uzgodnienia z Aidite (przed testem i w umowie):

- Egzemplarz testowy z aktualnym oprogramowaniem i kontakt do inżyniera aplikacyjnego, nie handlowca.
- Nagranie ekranu lub pisemne potwierdzenie skanu z samym obrotem (bez przechyłu) i spokojnym, najlepiej regulowanym obrotem stolika.
- Lista automatycznej obróbki siatki (wypełnianie otworów, wygładzanie, upraszczanie, usuwanie drobnych fragmentów) i możliwość wyłączenia każdej z nich; gęstość punktów w eksportowanym pliku.
- Tryb szybkiego skanu bez zakładania zlecenia; skróty klawiszowe do startu i eksportu; automatyczny eksport do wskazanego folderu z ustaloną nazwą pliku.
- Wymiary i interfejs mocowania stolika (plik STEP lub STL adaptera) oraz prześwit komory przy pełnym obrocie; wymiar pola skanowania.
- Dokumentacja integracji z exocad (wywołanie programu z parametrami, folder wyjściowy) albo SDK/API, jeśli istnieje.
- Druga lub przenośna licencja na laptop deweloperski; praca bez internetu; aktualizacje bez opłat; informacja, czy program jest własny Aidite czy OEM (czyj, która wersja).
- Wzorzec kalibracyjny w zestawie, kalibracja po naszej stronie, certyfikat dokładności (ISO 12836), gwarancja 2 lata z urządzeniem zastępczym, instrukcja i szkolenie przed dostawą.

Zestaw testowy (przygotowuję przed testem):

| Próbka | Ilość | Po co |
|---|---|---|
| Zielone korony pełnokonturowe, różne zęby | 12 | pokrycie brzegu, dopasowanie do projektu |
| Zielone korony z celowo wykonanym ubytkiem na brzegu (0,25 mm, 0,4 mm, 0,6 mm; zmierzonym pod mikroskopem lub lupą z podziałką) | 3 | wykrywalność, dolna granica |
| Zielony siekacz dolny (najmniejsza praca) | 1 | pokrycie; czy mała praca leży pewnie w gnieździe ø12 mm — mniejszych w nowym układzie nie ma [R59] |
| Zielony most 4-punktowy | 1 | rynienka, łączniki |
| Zielone korony implantologiczne, w tym dwie niemal identyczne | 3 | kanał śruby, bliźniaki |
| Spieczone korony (różna przezierność, w tym 5Y) | 8 | skan bez sprayu, poranek |
| Spieczony most | 2 | jak wyżej |
| Projekty STL wszystkich powyższych + współczynniki z raportów MillBox | komplet | porównanie |
| Płytka wieczorna nr 1 wydrukowana z PETG białego matowego u kolegi (z gotowego pliku) [R55] | 1–2 | ułożenie prac, znaczniki, dołki kodu; [R59] egzemplarz wydrukowany przed zmianą ma poprzedni układ gniazd — w programie wybiera się wtedy układ poprzedni |
| Kartonowa makieta 96 × 96 mm z narysowanymi okręgami ø90, ø94 i ø100 (środek płytki) i zaznaczonymi rogami [R54] | 1 | pole skanowania przy obrocie stolika (kryterium 8) |

Przebieg:

1. Skan kartonowej makiety z okręgami (kryterium 8, pole przy obrocie) i pustej płytki testowej z PETG [R55]: czy program widzi 3 stożki i dołki kodu. To rozstrzyga zamówienie płytek w drukarni.
2. Ułożenie 20 zielonych prac na płytce, brzegiem do góry — w razie potrzeby w dwóch turach (płytka mieści 18 koron i 1 most w nowym układzie [R59], 18 koron i 2 mosty w poprzednim). Zdjęcie telefonem (dokumentacja ułożenia).
3. Skan w trybie ręcznym lub własnej ścieżce: obrót 4–6 pozycji, przechył 0°, obrót spokojny (jeśli program pozwala zmieniać prędkość: osobno najniższa i domyślna). Zapis STL. Jeśli program nie ma takiego trybu: skan automatyczny i odnotowanie tego faktu (kryterium 1).
4. Powtórzenie skanu bez dotykania płytki (powtarzalność).
5. Ten sam skan dla 10 spieczonych prac, w trybie do błyszczących obiektów, jeśli jest.
6. Dodatkowo skan automatyczną ścieżką producenta (z przechyłem) — czy prace zostały na miejscu.
7. Eksport STL i ocena: w CloudCompare (darmowy) albo moim wczesnym skryptem: skalowanie projektu, dopasowanie ICP, mapa odległości.
8. Pomiar czasu każdej operacji i liczby kliknięć.

Kryteria go/no-go:

| Nr | Kryterium | Próg „go” | Co, jeśli nie |
|---|---|---|---|
| 1 | Ścieżka skanu bez przechyłu (ręczna lub własna) | istnieje i da się zapisać jako strategia | skaner odpada, chyba że kryterium 2 przejdzie na ścieżce automatycznej |
| 2 | Prace nie drgnęły przy obrocie stolika: brak podwójnych powierzchni na żadnej z 20 prac; różnica dwóch skanów tej samej płytki < 0,03 mm; obrót bez szarpnięć przy starcie i zatrzymaniu | 20/20 | wolniejszy obrót (jeśli regulowany), głębsze gniazda i powtórka; drugi raz — skaner odpada |
| 3 | Pokrycie brzegu (pierścień 1,5 mm) i wnętrza każdej zielonej pracy | ≥ 95% powierzchni | skaner odpada |
| 4 | Ubytki testowe widoczne w mapie odległości jako odchyłka ≥ 0,08 mm o właściwym położeniu | 3/3 (0,25 mm może być graniczne: wtedy 2/3 z zapisem, że dolna granica to 0,4 mm) | skaner odpada |
| 5 | Spieczone prace bez sprayu | pokrycie ≥ 70%, kształt rozpoznawalny | poranek przez kamerę (plan B), skaner zostaje |
| 6 | Czas skanu płytki z eksportem | ≤ 90 s | ≤ 150 s do przyjęcia przy dwóch płytkach na zmianę; powyżej — przepustowość do przeliczenia |
| 7 | Eksport STL | automatyczny do folderu albo ≤ 3 kliknięcia | wyłącznie ręcznie i więcej kliknięć — do przeliczenia czasu |
| 8 | Pole skanowania przy obrocie stolika [R54] | skan makiety 96 × 96 z okręgami ø90, ø94, ø100 pełną ścieżką bez przechyłu: największy okrąg widoczny w całości w siatce ma ø100 (wtedy układ gniazd bez zmian) | ø94–100: gniazda przeliczone do mniejszego koła — jedna liczba w plikach, nowe pliki płytek, ramka bez zmian; poniżej ø94: płytka okrągła z nową wkładką i pokrywką |

Wynik testu to jedna strona: tabela kryteriów z wynikami, 3 zrzuty map odległości (ubytki), czasy. Na tej podstawie zamówienie skanera i płytek — i jednocześnie pierwsze prawdziwe skany do strojenia programu.

## Co przygotowuję, czekając na dostawę

W dniu dostawy skanera ma być gotowe wszystko poza samym podłączeniem: program przetestowany na sztucznych skanach i na plikach z testu u dostawcy, płytki i obudowy ramek dostarczone i złożone, obie ramki działające, Excel sprawdzony na kopii. Praca po godzinach, etapami zależnymi od zdarzeń (dostawy, test), nie od kalendarza.

Przed testem skanera (i przed prezentacją dla firmy):

- Ramki: wycena u 2–3 drukarni i zamówienie korpusów (W i P) oraz 2 blatów — pliki ostateczne, nie zależą od pomiarów elektroniki ani od skanera.
- Zamówienie elektroniki ramek i drobnych (dokument „Zakupy i druk”); dystanse panelu w obu długościach (50 i 45 mm) albo po sprawdzeniu gwintu panelu.
- Druk u kolegi z PETG [R55]: płytka wieczorna nr 1 do testu skanera, prototyp wkładki, pokrywka i próbka zatrzasku blatu — test pasowań na sucho. Pytanie do Aidite lub dystrybutora o zakres skanowania (czy mieści 96 × 96 mm).
- Zestaw testowy prac, ubytki wykonane i zmierzone.
- Próba ze skanerem wewnątrzustnym z firmy + CloudCompare: pierwsze mapy odległości.
- Zapytania: Aidite (egzemplarz testowy, tryb bez przechyłu, pole skanowania, cena), DOF i 3Shape (wycena, test).
- Na laptopie: OneDrive z folderem „Cyrkon”, Excel z plikiem produkcyjnym (Autozapis), sprawdzenie, że COM widzi otwarty skoroszyt.
- Repozytorium, środowisko Pythona, pliki opisu modułów dla Claude Code.

Po dostawie elektroniki (równolegle pierwsze moduły programu):

- Pomiary elektroniki (panel, stos Pi, gniazda) — służą tylko doborowi sprzętu: długość dystansów, tulejka gniazda, podkładki, ewentualne wiercenie; druk tulejek i podkładek z PETG u kolegi [R55].
- Elektronika ramki na stole (kroki 2–5 montażu): system, matryca, klawiatura, czujniki.
- Generator danych syntetycznych: sztuczne skany z 30 prawdziwych STL.
- catalog: indeks folderów, parser nazw, parser raportów MillBox (na 10 prawdziwych raportach), cechy STL, baza. plate: wyrównanie po znacznikach, odczyt kodu płytki, cięcie na gniazda — testy na danych syntetycznych z prawdziwym układem gniazd z gotowych plików płytek.

W czasie testu skanera u nas:

- Pierwszego dnia testu: skan makiety z okręgami i płytki testowej z PETG (kryterium 8) → zamówienie płytek i wkładek w drukarni (poranne i wieczorne, PA12 [R55]) i pokrywek u kolegi — chyba że producent potwierdzi zakres skanowania wcześniej, wtedy zamówienie od razu. [R59] Pierwsze skany idą na płytce wieczornej poprzedniego układu; nowe płytki zamawia się w tym czasie, a o tym, które i ile, decyduje właściciel po odbiorze plików nowego układu.
- match: filtr po objętości i wymiarach, zgrubne dopasowanie, ICP, ranking; metryka: trafność top-1 i top-2 na 200 sztucznych fragmentach.
- inspect: mapa odchyłek, wykrywanie ubytków, odrzucanie gładkich poprawek, wykrywanie podwójnych powierzchni; metryka: wykryte / pominięte / fałszywe na 100 sztucznych ubytków.

Po dostawie korpusów i blatów:

- Montaż pierwszej ramki (kroki 6–14), oprogramowanie ramki (Wi‑Fi, protokół „płytka, gniazdo, kolor”, „stan”, potwierdzenia); wkładki i płytki dochodzą po potwierdzeniu pola skanowania; kalibracja gniazdo → diody; indicate.
- ui: ekran wieczorny i poranny z dużymi kafelkami, widok 3D z mapą odchyłek, start skanu spacją; przegląd z technikiem na sztucznych danych (czy rozumie bez instrukcji).
- excel: reguły wyszukiwania wiersza przetestowane na kopii pliku (50 kuwet z historii, porównanie z tym, co zaznaczył człowiek); tryb „[cytat usuniety]”.

Po teście, przed dostawą skanera (skaner zamówiony, pliki z testu w ręku):

- Druga ramka z poprawkami z pierwszej; płytki z drukarni: magnesy według kodów, test odczytu, kalibracja diod dla obu kompletów.
- match i inspect dostrojone na prawdziwych skanach z testu; progi zapisane w ustawieniach.
- session: sesja pieca, lista braków, lista „do dofrezowania”, log. scanner: obserwacja folderu; próba automatu klikającego na wersji demo programu producenta (jeśli dostępna).
- Instrukcja jednostronicowa dla technika (obrazki, 6 kroków) i dla poranka; checklista uruchomienia.
- Osłona i pokrowce; miejsce na parapecie wymierzone i oklejone (schemat w załączniku).

Zasada: każdy etap kończy się działającą, przetestowaną wersją, którą da się pokazać na ekranie, nawet bez skanera.

## Uruchomienie: kolejność kroków

Uruchomienie kończy się stanowiskiem pracującym w trybie cienia: program ocenia i wskazuje, a ludzie robią jeszcze wszystko po staremu, żeby porównać wyniki bez ryzyka dla produkcji. Pełne przejście następuje po trybie cienia i po spełnieniu kryteriów z sekcji „Testy odbiorcze”. Kroki idą po kolei; następny zaczyna się po spełnieniu kryterium końca poprzedniego.

| Krok | Co robię | Kto jest potrzebny | Kryterium końca kroku |
|---|---|---|---|
| 1 | Rozpakowanie, ustawienie skanera na parapecie, instalacja programu producenta na laptopie, kalibracja, strategia skanu „płytka: obrót, przechył 0”, eksport STL do folderu obserwowanego; ustawienie ramki wieczornej przy skanerze i osłony; ramka poranna w pokoju rozkładania z klipsem kabla przy stole | ja; serwis Aidite zdalnie, jeśli trzeba | Skan testowej płytki ląduje jako plik w folderze i program go rozpoznaje |
| 2 | Pierwsze prawdziwe płytki zielonych prac: wyrównanie po znacznikach, cięcie na gniazda, dopasowanie do projektów z raportów; kalibracja progów na 10 pracach ze znanymi ubytkami | ja, 1 h technika | Trafność dopasowania na 40 pracach ≥ 85%; 10 znanych ubytków: wykryte ≥ 8 |
| 3 | Wieczorny pilotaż z technikiem w trybie cienia (technik ogląda jak dziś, a ekran dodatkowo pokazuje czerwone); rano pilotaż identyfikacji na jednym piecu bez zapisu do Excela (log porównawczy z tym, co zaznaczył człowiek) | technik wieczorny, ja rano | Technik obsługuje bez pomocy; lista różnic do przejrzenia |
| 4 | Poprawki po pilotażu; włączenie diod; Excel w trybie „pytaj przed zapisem” na jednym piecu; pomiar czasów stoperem | ja, druga osoba poranna jako audytor Excela | 0 błędnych wierszy w Excelu; czas pieca zmierzony |
| 5 | Pełny dzień w trybie cienia: wszystkie piece, wszystkie płytki; przegląd metryk; instrukcje wywieszone przy stanowisku; przekazanie checklisty „co robić, gdy” | wszyscy, 15 min odprawy | Metryki z dnia zapisane; decyzja: start trybu cienia |

W trybie cienia (do spełnienia kryteriów odbiorczych):

- Wieczorem technik zaznacza na ekranie także prace, które sam uznał za ukruszone, a program nie — to daje liczbę pominięć.
- Rano porównanie: rozpoznanie programu vs. przymiarka; Excel: zapis programu vs. zaznaczenie człowieka (druga osoba nadal odhacza, tylko sprawdza).
- Co tydzień 30 min: przegląd metryk, korekta progów, lista poprawek.

Przejście na tryb pełny (po spełnieniu kryteriów odbiorczych): technik ogląda tylko czerwone, poranek według diod, Excel zapisuje sam z logiem; audyt Excela raz w tygodniu na próbie 20 wierszy przez pierwszy miesiąc.

Uwaga: co może opóźnić uruchomienie — brak trybu bez przechyłu w dostarczonym programie (wraca się do gniazd głębszych i testu na ścieżce automatycznej), laptop bez dedykowanej karty graficznej (program producenta nie uruchomi się płynnie), brak dostępu do folderu raportów MillBox (kopia ręczna na czas uruchomienia), opóźniona dostawa druku obudów (ramki działają na stole bez obudowy, poranek według podpisów na ekranie).

## Testy odbiorcze i kryteria „działa”

„Działa” znaczy: liczby z trybu cienia przekraczają progi poniżej. Każdą metrykę program liczy sam z własnego logu; raport to jedno polecenie i jedna strona.

| Obszar | Metryka | Jak mierzona | Próg odbioru | Cel po 3 miesiącach |
|---|---|---|---|---|
| Ukruszenia | Wykrywalność ubytków brzegu ≥ 0,3 mm | Zestaw 30 prac ze znanymi ubytkami (część z produkcji, część wykonana celowo), skanowane na płytkach między zwykłymi pracami | ≥ 80% wykrytych | ≥ 90% |
| Ukruszenia | Fałszywe alarmy | Udział czerwonych gniazd, które technik uznał za OK, w całości prac | ≤ 15% prac | ≤ 8% |
| Ukruszenia | Prace ukruszone, które przeszły do pieca | Rano: ukruszenia wykryte gołym okiem po piecu, przeliczone na wieczorne skany (tryb cienia) | spadek o ≥ 60% wobec 2 tygodni przed wdrożeniem | ≥ 80% |
| Identyfikacja | Trafność top-1 | Rozpoznanie programu vs. przymiarka/decyzja człowieka, bez bliźniaczych prac implantologicznych | ≥ 85% | ≥ 92% |
| Identyfikacja | Trafność top-2 (właściwa kuweta wśród dwóch kandydatów) | jak wyżej | ≥ 95% | ≥ 98% |
| Identyfikacja | Prace nieznane | Udział gniazd „brak kandydata” | ≤ 10% | ≤ 5% |
| Czas | Rozłożenie dużego pieca (40–60 prac) | Stoper od otwarcia pojemnika do odłożenia ostatniej pracy, 5 pomiarów | ≤ 25 min (dziś ok. 40) | ≤ 20 min |
| Czas | Rozłożenie małego pieca | jak wyżej | ≤ 8 min (dziś 10–15) | ≤ 6 min |
| Czas | Dodatkowy czas technika wieczorem | Suma czasów przy stanowisku z logu (start skanu → decyzje) | ≤ 20 min na zmianę | ≤ 15 min |
| Excel | Poprawność wiersza | Audyt 50 kolejnych zapisów przez drugą osobę | 50/50, zero zapisów w złym wierszu | utrzymane, audyt co miesiąc |
| Excel | Czas odhaczania | Czas drugiej osoby na odhaczanie | 0 min (tylko audyt) | 0 min |
| Ramki | Rozpoznanie płytki | Odczyt numeru płytki po położeniu na ramce | 100% w < 100 ms, 0 bez płytki | utrzymane |
| Stabilność | Dni bez awarii wymagającej restartu | Log programu | 5 kolejnych dni | 20 kolejnych dni |
| Stabilność | Skany do powtórzenia (praca drgnęła, zła płytka) | Udział płytek skanowanych ponownie | ≤ 5% | ≤ 2% |
| Obsługa | Technik radzi sobie bez pytań | Obserwacja 3 wieczorów po instruktażu | 0 interwencji w ostatni wieczór | — |

Jak liczyć wykrywalność uczciwie: zestaw prac ze znanymi ubytkami jest numerowany i trzymany osobno; raz w tygodniu 5 z nich trafia na zwykłe płytki bez wiedzy programu (technik wie, która), a wynik zapisuje się w tabeli testów. Dzięki temu metryka nie zależy od tego, co technik akurat zauważył.

Co nie jest kryterium odbioru: wykrywanie ubytków na guzkach i ścianach bocznych (ułożenie brzegiem do góry ich nie pokazuje), rozróżnianie bliźniaczych prac implantologicznych, prace prywatne bez zapisanych STL.

Kiedy wracamy do tablicy: wykrywalność poniżej 60% po strojeniu, trafność identyfikacji poniżej 70%, albo czas technika powyżej 30 min na zmianę przez tydzień — wtedy zmiana ułożenia, gniazd lub progów, a w ostateczności plan B z sekcji „Ryzyka”.

## Ryzyka i plany B

Największe ryzyka siedzą w trzech miejscach: w mechanice skanera (przechył i pole skanowania), w jakości skanu spieczonych prac i w zachowaniu technika, gdy alarmów jest za dużo. Do tego dochodzą ryzyka budowy ramek: wymiary elektroniki znane dopiero po dostawie i druk własny na drukarce FDM u kolegi (dostępność, dokładność małych części) [R55]. Każde ma plan B, który nie wymaga wyrzucenia reszty.

| Ryzyko | Prawdopodobieństwo | Skutek | Jak je zmniejszamy | Plan B |
|---|---|---|---|---|
| Program skanera nie pozwala na ścieżkę bez przechyłu | średnie | prace drgają, fałszywe ubytki | kryterium 1 testu; prośba do Aidite o strategię | gniazda głębsze (50% wysokości pracy) + test na ścieżce automatycznej; w ostateczności DOF Freedom (model nieruchomy) lub 3Shape F8 |
| Pole skanowania przy obrocie mniejsze niż koło ø100 (założenie Z1) [R54] | średnie | prace ze skrajnych gniazd wychodzą poza pole w części obrotu | skan kartonowej makiety z okręgami pierwszego dnia testu, przed zamówieniem płytek; średnica pola jest jedną liczbą w plikach projektu; układ gniazd już liczony do koła o promieniu 47 mm (zapas 3 mm na ułożenie i wysięg koron) | ø94–100: gniazda przeliczone do mniejszego koła, nowe pliki płytek po pełnej weryfikacji, ramka bez zmian; poniżej ø94: płytka okrągła, nowa wkładka i pokrywka |
| Wymiary elektroniki (panel, stos Pi, gniazda) inne niż domyślne | średnie (wartości domyślne z katalogów) | panel lub gniazdo nie trafia w przygotowane miejsce | obudowa ma zapasy: 8 mm nad stosem Pi, rowki pod słupki na rozstaw 110–130 mm, okno USB z rowkami 23–28 mm, otwór gniazda ø12 z tulejką dla ø8, dystanse w dwóch długościach, podkładki 0,5/1/2 | wiercenie ø4 w dnie w zmierzonym miejscu, obrót panelu, rozwiercenie otworu gniazda, wiercenie flanszy USB — wszystko bez nowego korpusu |
| Drukarka FDM u kolegi niedostępna albo PETG nie trzyma wymiaru małych części (tulejka ø11,85, podkładki 0,5 mm, stożki płytki testowej) [R55] | średnie | brak taniej płytki testowej, prototypów, tulejki i podkładek | pierwsza sztuka mierzona suwmiarką; tulejka sprawdzana w otworze ø12 korpusu, skalowanie XY w slicerze ±1 %; podkładka 0,5 mm = 3–5 warstw 0,1–0,2 mm | płytka testowa, tulejka i podkładki jako tanie próbki w tej samej drukarni (PA12); pokrywki też z drukarni (ok. 110–190 zł więcej) |
| Drukarnia nie trzyma tolerancji (±0,3 mm na 200 mm) | średnie | płytka ciasna we wkładce, blat nie zatrzaskuje się | [R53] luzy liczone na ±0,3 mm na każdej z dwóch współpracujących części: 0,4 mm płytka we wkładce, 0,7 mm kołnierz blatu, 0,75 mm zatrzaski w pionie, otwory wkrętów ø3,6; pomiar przy odbiorze (checklista w „Zakupy i druk”): odchyłka większa niż ±0,5 mm = reklamacja; prototypy pasowań przed zamówieniem; wkładka tania i wymienna | poprawka papierem ściernym; nowa wkładka |
| Za dużo fałszywych alarmów na starcie, technik ignoruje czerwone | wysokie w 1. miesiącu | kontrola staje się pozorna | tryb cienia, progi strojone co tydzień, decyzje technika zapisywane jako dane do strojenia; klasyfikator poprawek ręcznych | start od wyższego progu (mniej alarmów, więcej pominięć), stopniowe obniżanie |
| Spieczona, przezierna cyrkonia skanuje się za słabo bez sprayu | średnie | poranna identyfikacja zawodzi | kryterium 5 testu; tryby do błyszczących obiektów | kamera 20 Mpx nad ramką LED: identyfikacja po obrysie i wnętrzu, ten sam program, koszt ok. 2 tys. zł |
| Ręczne poprawki zielonych prac wyglądają jak ubytki | wysokie | fałszywe alarmy | kształt odchyłki: gładka i rozległa = poprawka, ostra i mała = ukruszenie; strefa brzegu ważona | próg rozmiaru i wyłączenie obszarów oznaczonych przez technika jako „poprawione” |
| Bliźniacze prace implantologiczne | pewne | dwuznaczna identyfikacja | ekran pokazuje obu kandydatów + kolor z karty | człowiek decyduje; pozostaje na zawsze |
| Automat klikający w programie producenta zawodzi po aktualizacji | średnie | ręczne 3 kliknięcia na płytkę | zablokowane aktualizacje programu skanera; automat opcjonalny od początku | technik klika sam; +15 s na płytkę |
| Współedycja Excela: konflikt zapisu, plik zablokowany | niskie | brak odhaczenia | zapis tylko koloru, jednej komórki, z ponowieniem; log; tryb „pytaj” | Office Script jednym kliknięciem; Microsoft Graph przez IT |
| Brak dostępu do raportów MillBox z laptopa | średnie | brak współczynników, brak puli wieczornej | kopia folderu raz dziennie (skrypt na komputerze MillBoxa) | współczynnik wpisywany ręcznie raz na krążek (lista krążków dnia) |
| Zlecenia prywatne bez STL w folderze | wysokie na początku | prace nieznane rano | 10-sekundowy nawyk osoby przyjmującej zlecenie | identyfikacja ręczna jak dziś |
| Pył na płytce, w skanerze i w ramce | pewne | artefakty, zabrudzone znaczniki | pokrowce, wycieranie płytek, kalibracja co tydzień; obudowa ramki zamknięta, szczeliny w dół, otwory w dnach gniazd przepuszczają pył na szybkę, którą się wyciera | — |
| Ramka poranna nie łączy się z Wi‑Fi | niskie | brak diod rano | ramka trzyma ostatni plan w pamięci; hotspot laptopa jako zapas | poranek według podpisów na ekranie laptopa |
| Laptop bez odpowiedniej karty graficznej | niskie (firma obiecała mocny) | program producenta wolny lub niestabilny | wymagania w liście zakupów | wymiana laptopa |
| Ja jako jedyna osoba znająca program | pewne | zależność | instrukcje, opisy modułów, pliki ramek odtwarzalne jednym poleceniem, kod w repozytorium firmy po przekazaniu praw | druga osoba przeszkolona w obsłudze i restarcie; poprawki zdalnie |
| Czas technika wieczorem przekracza 20 min w ciężkie dni | średnie | pomijanie kontroli | płytka zastępuje tackę; dwie płytki; skan w tle | priorytet dla prac o cienkich brzegach i implantologicznych; drugi skaner, jeśli ciężkie dni to norma |
| Dostawa skanera opóźniona | średnie | przesunięcie uruchomienia | zamówienie od razu po teście; oprogramowanie i ramki nie czekają na sprzęt | uruchomienie przesuwa się 1:1 z dostawą, bez innych skutków |
| [R59] Płytka starego układu wzięta za nową albo odwrotnie (numery płytek są te same) | średnie, dopóki stare płytki są w użyciu | prace przypisane do złych gniazd | stare płytki opisane i trzymane osobno; program zna oba układy i ostrzega, gdy zeskanowana płytka nie pasuje do wybranego | wycofanie starych płytek po dostawie nowych |
| [R59] Mostów jest więcej niż płytek pod ręką (jedna rynienka, czyli jeden most na płytkę) | nieznane; w próbie 17 projektów rynienki wymagało wieczorem 8 prac: 6 dłuższych niż 20 mm i 2 za duże na gniazdo ø15 (próba mała, dobrana do testów programu) | mosty czekają na następną płytkę; więcej skanów | po 3 płytki każdego rodzaju; mosty układane po jednym na płytkę | zmiana programu: dwie prace w jednej rynience (osobna praca, bez ustalonego terminu) |

Czego nie da się obejść planem B: gwarancji wykrycia każdego ubytku 0,25 mm (fizyka rozdzielczości skanera), zapisu „która kuweta w którym piecu” (świadomie wykluczone), oznaczania prac (zakaz).

## Decyzje otwarte

| Nr | Punkt | Co trzeba zrobić | Warunek / kto |
|---|---|---|---|
| 1 | Pole skanowania (założenie Z1 [R54]: koło ø100 mm wokół osi stolika, widoczne w całym obrocie) — skanera jeszcze nie ma | pytanie do Aidite lub dystrybutora o zakres skanowania przy obrocie; potwierdzenie na egzemplarzu testowym skanem kartonowej makiety z okręgami ø90/94/100 (kryterium 8); przy polu ø94–100 gniazda przeliczone do mniejszego koła (jedna liczba) i nowe pliki płytek, ramka bez zmian; poniżej ø94 płytka okrągła z nową wkładką i pokrywką | przed zamówieniem płytek, wkładek i pokrywek; korpusów i blatów nie blokuje |
| 2 | Pomiary elektroniki (panel, stos Pi i nakładki, gniazda, odbiornik klawiatury, wkręty) | po dostawie zamówionej elektroniki, suwmiarką, ok. 30 min; wynik decyduje tylko o doborze sprzętu: dystanse 50 czy 45 mm z tulejkami, tulejka gniazda, podkładki, ewentualne wiercenie dna lub flanszy USB | po dostawie elektroniki; nie blokuje żadnego zamówienia |
| 3 | Wysokość ramki 63,6 mm (przekracza pierwotne 55–60 mm o 3,6 mm) | przyjęta przez właściciela razem z konstrukcją odporną na pomiary; nie wraca do dyskusji, chyba że zmierzona elektronika przekroczy zapas (stos Pi z taśmą ponad 31 mm lub złącza panelu z kablami ponad 17 mm) | rozstrzygnięte; kontrola po pomiarach |
| 4 | Drukarka FDM u kolegi [R55] | sprawdzić pole robocze (≥ 100 × 100 mm na płytkę testową) i filament PETG biały matowy; pierwsza sztuka każdej części mierzona suwmiarką | przed drukiem płytki testowej |
| 5 | Płytki wieczorne: materiał i wykonawca | [R55] rozstrzygnięte: wszystkie 6 płytek z drukarni (PA12); technologie odrzucone i powody w „Budowa ramki — decyzje i zamienniki” | rozstrzygnięte |
| 6 | Wybór drukarni i wariant wykończenia (najtańszy vs pokazowy: barwienie i wygładzanie korpusów) | wyceny z 2–3 drukarni na gotowych plikach; zamawiać wyłącznie pliki o sumach SHA‑256 ze specyfikacji zamówienia w dokumencie „Zakupy i druk” [R53] | przed zamówieniem obudów |
| 7 | Skaner: tryb bez przechyłu, pole skanowania, eksport | test u nas, kryteria 1–8 | egzemplarz testowy od Aidite; ja |
| 8 | [R59] Które płytki nowego układu zamawiamy: okrągłe, kwadratowe czy obie, i ile sztuk | właściciel skłania się ku okrągłym; ilości w arkuszu zamówienia bez zmian (po 3 kwadratowe wieczorne i poranne, po 1 okrągłej); okrągłe nie pasują do wkładki ramki — żeby leżały na ramce świetlnej, potrzebna jest zmiana R58 (okrągła wkładka i pokrywka) | właściciel, po odbiorze plików nowego układu |
| 9 | [R59] Dwa mosty na jednej płytce | dziś jedna rynienka i jedna praca w gnieździe, czyli jeden most na płytkę; dwa mosty w jednej rynience wymagają zmiany programu | osobna praca nad programem, bez ustalonego terminu |
| 10 | [R59] Stare płytki na ramce świetlnej | ramka czyta numer płytki z magnesów, a numery są te same w obu układach, więc sama nie odróżni starej płytki od nowej; do ustalenia przy pisaniu programu ramki, skąd ramka bierze układ gniazd | przed użyciem starych płytek na ramkach |

## Koszty i kolejność

Cały projekt to ok. 22,4–29 tys. zł sprzętu (skaner 20–25 tys. zł plus ramki, płytki, osłona i drobne 2,4–3,9 tys. zł) i zero wydatków na oprogramowanie. Najdłużej trwają test skanera i oczekiwanie na jego dostawę; ramki i płytki powstają w tym samym czasie co oprogramowanie, więc nie wydłużają drogi do uruchomienia.

Koszty:

| Pozycja | Kwota | Uwagi |
|---|---|---|
| Skaner laboratoryjny (Aidite A-IS Pro 3 lub zamiennik) | 20–25 tys. zł | oferta po teście; DOF i 3Shape na zapytanie |
| Elektronika dwóch ramek: 2 panele LED, 2 Raspberry Pi 4 z nakładkami, zasilacze, pleksi, klawiatura, czujniki, magnesy, wkręty, drobne | 1,2–1,7 tys. zł | lista w sekcji „Lista zakupów”; można zamawiać od razu |
| Druk w drukarni (PA12): 2 korpusy, 2 blaty, 3 wkładki, 6 płytek | 907–1 613 zł (najtańszy) / 1 216–2 161 zł (pokazowy) [R59] | 10 plików, 1 008 cm³ z arkusza zamówienia (objętości zmierzone na siatkach; po zmianie układu gniazd płytka wieczorna ma 59,66 cm³, poranna 59,95 cm³ — było 59,31 i 60,87); druk w drukarni to najdłuższy etap budowy ramek, dlatego korpusy i blaty idą do drukarni od razu; pokrywki, tulejki i podkładki drukowane samemu z PETG za koszt filamentu [R55: wszystkie płytki z drukarni] |
| Osłona, pokrowce, drobne stanowiska | 0,3–0,6 tys. zł | |
| Opcja: kamera 20 Mpx (plan B poranka) | 1,8–2,5 tys. zł | tylko po negatywnym kryterium 5 testu |
| Laptop | 0 zł | daje firma |
| Oprogramowanie, licencje, subskrypcje | 0 zł | własne, biblioteki otwarte, program producenta w zestawie |
| Mój czas | po godzinach (oprogramowanie, montaż ramek, uruchomienie) | rozliczany według ustaleń z firmą |

Co firma zyskuje w liczbach (do potwierdzenia metrykami): ponowne frezowanie prac ukruszonych wykrywanych dopiero po piecu spada o co najmniej 60%; rozkładanie dużego pieca krótsze o 15–20 min (2–3 piece dziennie, czyli 40–60 min dziennie wcześniej uwolnionych dla działów czekających na prace); odhaczanie w Excelu z ok. 40–90 min dziennie (10–15 min na piec, 4–6 pieców rano) do zera.

Kolejność i bramki (tor skanera przesuwa się 1:1 z jego dostawą; kroki po stronie ramek i oprogramowania biegną równolegle):

| Krok | Warunek / bramka | Co odblokowuje |
|---|---|---|
| Zamówienie elektroniki ramek i drobnych; wycena i zamówienie korpusów (W, P) i 2 blatów w drukarni | pliki ostateczne, zweryfikowane trzykrotnie (obudowa nie zależy od pomiarów ani od skanera) | pomiary elektroniki po jej dostawie; montaż ramek po dostawie druku |
| Pytanie do Aidite o zakres skanowania; próba skanerem wewnątrzustnym z firmy; zestaw testowy prac; druk płytki testowej i prototypów pasowań z PETG u kolegi [R55] | drukarka FDM: pole robocze i PETG biały matowy sprawdzone | test skanera; pisemne potwierdzenie zakresu skanowania odblokowuje zamówienie płytek bez czekania na test |
| Dostawa elektroniki → pomiary → dobór dystansów, tulejki, podkładek; druk tulejek i podkładek z PETG u kolegi [R55] | pomiary w zapasie konstrukcji (inaczej wiercenie lub obrót panelu) | elektronika ramki na stole (kroki 2–5 montażu) |
| Prezentacja dla firmy — ten dokument | decyzja zarządu o teście skanera | test skanera u nas |
| Test skanera u nas na egzemplarzu testowym; pierwszego dnia skan makiety z okręgami i płytki testowej z PETG [R55] | kryteria 1–8 | kryterium 8 → zamówienie płytek, wkładek i pokrywek; wynik całego testu → zamówienie skanera |
| Oprogramowanie stanowiska i ramek (etapy z sekcji „Co przygotowuję, czekając na dostawę”) | każdy etap kończy się działającą wersją | gotowość na dzień dostawy skanera |
| Dostawa korpusów i blatów → montaż i testy obu ramek; płytki i wkładki z drukarni, magnesy, kalibracja diod | kroki 6–15 montażu zaliczone | obie ramki gotowe przed dostawą skanera |
| Zamówienie skanera | pozytywny test; alternatywy (Shining, DOF, 3Shape) tylko przy wyniku negatywnym | dostawa skanera |
| Dostawa skanera | oprogramowanie przetestowane, obie ramki złożone, Excel sprawdzony na kopii | uruchomienie |
| Uruchomienie (kroki 1–5 z sekcji „Uruchomienie: kolejność kroków”) | kryteria końca każdego kroku | tryb cienia |
| Tryb cienia | metryki odbiorcze spełnione | tryb pełny |
| Tryb pełny | kryteria z sekcji „Testy odbiorcze” spełnione | — |

Kamienie milowe i co je warunkuje:

1. Zamówienie elektroniki oraz korpusów i blatów — pliki ostateczne.
2. Prezentacja dla firmy — ten dokument; decyzja o teście.
3. Potwierdzenie pola skanowania (odpowiedź producenta albo pierwszy dzień testu) → zamówienie płytek, wkładek i pokrywek.
4. Test skanera u nas — egzemplarz testowy od Aidite; wynik w jednej tabeli.
5. Zamówienie skanera — po pozytywnym teście; alternatywy uruchamiane tylko przy wyniku negatywnym.
6. Obie ramki złożone i przetestowane — przed dostawą skanera.
7. Uruchomienie — po dostawie skanera; oprogramowanie gotowe wcześniej.
8. Tryb pełny — po trybie cienia i spełnieniu kryteriów odbiorczych.

## Załączniki

### A. Specyfikacja płytki z gniazdami

Płytka ma 96 × 96 × 8 mm. [R54] Skaner obraca ją wokół osi pionowej, więc w całym obrocie widzi koło wokół osi stolika — założenie: ø100 mm, do potwierdzenia na egzemplarzu testowym. Dlatego wszystkie gniazda, rynienka i stożki znaczników leżą w kole o promieniu 47 mm od środka płytki (zapas 1,5 mm na ułożenie płytki względem osi i 1,5 mm na wysięg korony poza obrys gniazda), a obrys płytki, wycięcie, numer, dołki kodu i kieszenie magnesów zostały bez zmian. Razem 6 płytek, każda z własnym numerem: wieczorne 1, 2, 3 (dwie w obiegu, jedna zapasowa) i poranne 4, 5, 6 (dwie albo trzy na duży piec [R59]: dwie mieszczą 46 koron i 2 mosty, trzy — 69 koron i 3 mosty). Między skanerem przy piecach a ramką w pokoju rozkładania płytki wędrują z pokrywką.

Układ gniazd (rysunki w wersji PDF; współrzędne każdego gniazda są w pliku obok modelu, więc program i ramka czytają je bez zmiany kodu):

- **Płytka wieczorna** (prace zielone, większe o skurcz) [R59]: 18 gniazd w 4 rzędach i 1 rynienka 60 × 15 mm pod most do 4 punktów. Od przodu: rynienka, 6 × ø12 mm, 5 × ø15 mm, 4 × ø15 mm, 3 × ø15 mm — razem 6 × ø12 i 12 × ø15. Poprzedni układ [R54]: 18 gniazd (7 × ø9, 6 × ø12, 5 × ø15) i 2 rynienki.
- **Płytka poranna** (prace spieczone, 40–70 °C) [R59]: 23 gniazda w 5 rzędach i 1 rynienka 50 × 13 mm. Od przodu: rynienka, 5 × ø12,5 mm, 6 × ø12,5 mm, rząd 4 × ø12,5 z jednym ø15 pośrodku, rząd 2 × ø12,5 z dwoma ø15 po bokach, 3 × ø12,5 mm — razem 20 × ø12,5 i 3 × ø15; gniazd ø7,5 i ø10 już nie ma. Poprzedni układ [R54]: 31 gniazd (18 × ø7,5, 7 × ø10, 6 × ø12,5) i 2 rynienki.

Gniazda: stożkowe, kąt ścianek 15°, głębokość 4 mm (ok. 40% wysokości korony), w dnie otwór przelotowy ø3 mm (rynienka ma 4 otwory); między gniazdami i rzędami ścianki co najmniej 3 mm (najmniejsza ma dokładnie 3,00 mm, bez zapasu — układu nie poprawia się ręcznie) [R59]; [R54] strefa gniazd: koło o promieniu 47 mm wokół środka płytki (wewnątrz dawnego kwadratu 90 × 90 mm); narożniki wolne od gniazd (tam są kod, magnesy, wycięcie i numer).

Znaczniki i orientacja: trzy stożki ø5 mm, wysokość 3 mm, [R54] przesunięte z narożników do koła gniazd, tuż za skrajnymi gniazdami (44,20–44,48 mm od środka płytki [R59], czyli w kole 44,5 mm; wieczorna i poranna mają własne położenia stożków, bo układy gniazd są różne) — dawne stożki w narożnikach leżały 61,9 mm od środka i wypadały z pola przy obrocie; czwarty narożnik (przód‑prawy) ma wycięcie 5 × 5 mm, które wymusza to samo ułożenie w skanerze i na kołku ramki. Trzy stożki są jedynym elementem, który program mierzy na płytce: po nich wyrównuje skan do rysunku.

Identyfikacja płytki, trzy sposoby na ten sam numer: cyfra wytłoczona (0,6 mm, 5 mm wysoka) w narożniku z wycięciem dla ludzi; 1–3 dołki ø2 × 1 mm przy lewej krawędzi dla skanera (program czyta je ze skanu); magnesy ø5 × 2 mm wklejone w kieszenie w spodzie trzech narożników dla ramek ([R54] kieszenie magnesów zostają w narożnikach, już nie pod stożkami znaczników; czujniki ramki bez zmian) (3 czujniki Halla: układ obecności magnesów = numer płytki; brak magnesów = brak płytki). Biegun magnesów jednakowy we wszystkich płytkach.

Pokrywka: nakładka 99,6 × 99,6 × 20 mm, jedna na obie płytki; 4 zatrzaski wchodzą w rowek wokół boków płytki 2 mm pod jej wierzchem; 14 mm prześwitu nad płytką (najwyższa praca 14 mm nad dnem gniazda plus 4 mm luzu); wycięcia na palce z przodu i z tyłu; gładki wierzch (drukowana z PETG wierzchem do stołu).

Materiał: nylon PA12 z zewnętrznej drukarni (SLS lub MJF), biały, naturalnie matowy — dobry dla skanera, sztywny, znosi temperaturę prac z pieca; przezroczystość nie jest potrzebna, bo gniazda mają otwór w dnie. [R55] Wszystkie 6 płytek z drukarni; jedynie płytka do testu skanera powstaje z PETG u kolegi. Inne materiały płytki i powody ich odrzucenia: „Budowa ramki — decyzje i zamienniki”.

[R57] Drugi kształt płytki — płytka okrągła: walec ø100 × 8 mm (ø100 = granica pola skanowania przy obrocie), faza 0,5 mm na górnej krawędzi, spód płaski. [R59] Gniazda, rynienka, otwory ø3 i stożki znaczników są takie same jak w płytce kwadratowej tego samego typu: wieczorna 18 gniazd i 1 rynienka, poranna 23 gniazda i 1 rynienka, w kole o promieniu 47 mm. Kształt płytki nie zmienia liczby gniazd. Zamiast wycięcia 5 × 5 — ścięcie orientacyjne na obwodzie (płaska ściana pionowa, cięciwa 16 mm, głębokość 0,644 mm, przód‑prawo). Dołki kodu ø2 × 1 mm leżą w kole (na kwadracie leżą poza polem ø100), kod 4‑bitowy: płytka okrągła wieczorna = nr 8 (dołek D), poranna = nr 9 (dołki A + D); cyfra 8 / 9 wytłoczona w kole. [R59] Na okrągłej porannej dołki leżą w dwóch parach z prawej strony, a cyfra z lewej, bo rynienka jest dosunięta do przodu i przed nią nie ma już miejsca. Bez kieszeni magnesów i rowka pokrywki, więc działa tylko w skanerze: wkładka i pokrywka ramki jej nie obsługują. Ścianka obrysu gniazd do krawędzi [R59]: wieczorna 4,07 mm, poranna 3,59 mm (do początku fazy 3,57 / 3,09 mm). Pliki `ramka_plytka_okragla_wieczorna_n8_v2.stl` (49,36 cm³) i `ramka_plytka_okragla_poranna_n9_v2.stl` (49,64 cm³), PA12 biały mat z drukarni (sumy SHA‑256 w „[cytat usuniety]”). [R59] O zamówieniu decyduje właściciel po odbiorze plików; skłania się ku okrągłym. Żeby płytka okrągła leżała także na ramce, potrzebna jest zmiana R58 (okrągła wkładka i pokrywka; korpus, blat i panel bez zmian).

Wersja następna (po teście): głębsze gniazda, jeśli prace drgają; mniejsze koło gniazd, jeśli pole skanowania przy obrocie jest mniejsze niż ø100 [R54] — obie zmiany to pojedyncze liczby w plikach projektu i pełny, automatyczny przebieg weryfikacji (płytka okrągła z nową wkładką dopiero poniżej ok. ø94).

### B. Ramka świetlna — wymiary i budowa

Obudowa (obie identyczne): 200 × 200 × 63,6 mm (korpus 59,6 mm + blat 4 mm), nylon PA12 barwiony na grafit, ściany 2,5 mm, dno 3 mm, promienie na krawędziach. Blat z oknem 158 × 158 mm i mleczną pleksi 160 × 160 × 2 mm licowaną z blatem; blat trzyma się na 4 zatrzaskach i 2 wkrętach w tylnej ściance, wierzch blatu jest gładki. W środku od dołu: Raspberry Pi 4 z nakładką na 4 słupkach pod środkiem panelu, 8 mm zapasu nad nim, panel LED 160 × 160 mm na 4 mosiężnych dystansach 50 mm (stojących na podkładkach dna, przykręconych od spodu przez rowki na rozstaw 110–130 mm), nad panelem 4 mm odstępu i szybka. Tylna ścianka: kieszeń wgłębiona z oknem 51 × 24 mm i głębokości 22 mm; gniazdo zasilania w jej bocznej ścianie (otwór ø12 mm, dla gniazda ø8 drukowana tulejka ø11,85/8,2 wciskana w otwór), wtyk kątowy (zalecany) lub prosty o korpusie do 37 mm od lica chowa się w kieszeni; gniazdo USB serwisowe z zaślepką (okno 16 × 9 mm z rowkami na rozstaw 23–28 mm). Dno: 2 szczeliny wlotowe 30 × 4 mm, 4 stopki gumowe klejone. Ściany: 10 szczelin wylotowych 12 × 3 mm nisko (4 z tyłu, po 3 z boków). Przód: gładki, tylko napis wytłoczony 8 mm. Karta pamięci dostępna po zdjęciu blatu i panelu.

Wkładka gniazda (biała, na blacie): rama 104,8 × 104,8 × 6 mm; płytka leży na 4 narożnych półkach 2,5 mm nad szybką (żaden otwór gniazda nie jest zasłonięty, bo narożniki płytki nie mają gniazd); pod trzema narożnikami czujniki Halla 1,7 mm od magnesów płytki; na czwartej półce kołek 4,4 × 4,4 mm wchodzący w wycięcie płytki; z przodu wycięcie palcowe do podniesienia płytki bez dotykania prac i dwie wytłoczone strzałki wskazujące przód; 2 tylne uszy z kołkami i magnesami trzymają wkładkę na blacie. Rama zabiera 4 mm (1,6 piksela) z każdego boku matrycy; wolny pas 27,7 mm = 11 pikseli na cyfry; pas przedni i prawy całkiem odsłonięte.

Elektronika (na ramkę): panel HUB75 64 × 64 P2.5, Raspberry Pi 4 B 2 GB z radiatorem, Adafruit RGB Matrix Bonnet, zasilacz 5 V 4 A (typowy pobór ramki < 1,5 A), karta 32 GB z systemem w trybie tylko do odczytu (nagłe wyłączenie prądu nie psuje karty), 3 czujniki Halla A3144 na małej płytce prototypowej przyklejonej taśmą VHB do ściany, kable na podstawkach opasek samoprzylepnych, w ramce porannej odbiornik USB klawiatury numerycznej 2,4 GHz. Czujniki używają trzech wolnych pinów Raspberry Pi; nakładka zajmuje resztę. Łączność: firmowe Wi‑Fi 2,4 GHz; zapas: hotspot laptopa.

### C. Schemat stanowiska na parapecie

stanowisko na parapecie · widok z góry (schemat w wersji PDF)

Parapet ma 200 × 45 cm; stanowisko zajmuje lewe 100 cm (skaner 38 × 26 cm, ramka 20 × 20 cm pod osłoną, laptop 36 × 25 cm), prawa połowa zostaje na opaker i kuwety. Skan uruchamia spacja na laptopie, ramki nie trzeba dotykać, a na podłodze nic nie leży.

Pomieszczenie pieców: długie, wejście krótką ścianą; wzdłuż lewej ściany szafki laboratoryjne, wzdłuż prawej jeden długi stalowy stół z ośmioma piecami do spiekania. Wymiary ok. 10 × 4 m, podział na 3 duże i 5 małych pieców oraz okna z parapetem na przeciwległym końcu to założenia do potwierdzenia na miejscu. Na szafce dużego pieca stoi ok. 30 kuwet jednego wsadu. Przy piecach nie ma miejsca na rozkładanie, więc prace rozkłada się do kuwet w osobnym pomieszczeniu. Tam używa się drugiej ramki (porannej): między porankami leży w szafce, rano stawia się ją na stole i wpina do kabla zasilacza czekającego w klipsie przy krawędzi stołu (gniazdo w kieszeni wgłębionej w tylnej ściance, wtyk kątowy); klawiatura numeryczna leży obok; płytki przenosi się z pokrywkami. Firmowe Wi‑Fi jest dostępne; hotspot laptopa stanowiska zostaje jako zapas.

### D. Checklista dnia (wieczór)

- Laptop włączony, program stanowiska i program skanera uruchomione, Excel otwarty z Autozapisem; ramka przy skanerze świeci kolor gotowości.
- Płytki czyste, znaczniki bez pyłu; szybka ramki przetarta.
- Dopóki w użyciu są płytki poprzedniego układu: układ wybrany w programie zgadza się z płytką na stanowisku (stare płytki są opisane) [R59].
- Pula dnia widoczna na ekranie (liczba STL z raportów MillBox); jeśli 0 — skopiować raporty.
- Po ostatniej płytce: lista „do dofrezowania” wydrukowana lub wysłana; pokrowce nałożone.

### E. Checklista dnia (poranek)

- Program w trybie „Poranek”, pula 3–4 dni załadowana (liczba zleceń na ekranie).
- Ramka poranna wyjęta z szafki, wpięta do zasilacza, pokazuje kolor gotowości i ikonę Wi‑Fi; klawiatura obok.
- Każdy piec zamknięty klawiszem „Zamknij piec”; lista braków przejrzana.
- Log Excela z dnia zapisany; w pierwszym miesiącu audyt 20 wierszy w piątek. Ramka z powrotem do szafki.

### F. Co robić, gdy nie działa

| Objaw | Co zrobić |
|---|---|
| Skan nie pojawia się w programie | Sprawdzić folder eksportu w programie skanera; kliknij „zapisz STL” ręcznie |
| Wszystkie gniazda szare (brak projektów) | Raporty MillBox nie dotarły: skopiować folder, przycisk „Odśwież pulę” |
| Komunikat „praca drgnęła” | Poprawić ułożenie, skanować ponownie; jeśli powtarza się na tej samej płytce — wymienić płytkę |
| Program nie rozpoznaje numeru płytki ze skanu | Dołki kodu przy lewej krawędzi zapylone — przetrzeć; numer można wskazać ręcznie na ekranie |
| Program ostrzega, że płytka nie pasuje do wybranego układu [R59] | Na skanerze leży płytka starego układu przy wybranym nowym albo odwrotnie: sprawdzić opis na płytce i wybrać w programie właściwy układ |
| Diody nie świecą | Zasilanie ramki (wtyk w kieszeni z tyłu), przycisk „Test LED” na laptopie, ikona Wi‑Fi na matrycy; bez diod poranek działa po podpisach na ekranie laptopa |
| Ramka nie widzi płytki (margines nie zmienia koloru) | Płytka nie leży na kołku orientacyjnym — docisnąć do narożnika z wycięciem; sprawdzić, czy magnesy w spodzie są na miejscu |
| Ramka poranna nie łączy się z laptopem | Ramka trzyma ostatni plan i potwierdzenia w pamięci i dosyła je po powrocie sieci; sprawdzić Wi‑Fi, w ostateczności włączyć hotspot laptopa |
| Klawiatura nie reaguje | Baterie; odbiornik siedzi w porcie USB wewnątrz ramki porannej — jeśli zasięg za słaby, przedłużacz do ścianki (opcja z listy zakupów) |
| Excel nie zapisuje | Czy plik jest otwarty w Excelu na laptopie z Autozapisem; tryb „pytaj” pokazuje wiersz — zaznaczyć ręcznie, log zapisze „ręcznie” |
| Program nie startuje | Restart laptopa; skrót „Stanowisko” na pulpicie; jeśli nadal — praca po staremu, telefon do mnie |
| Ramka nie wstaje po włączeniu prądu | Odczekać 60 s; jeśli nadal ciemna — karta pamięci (po zdjęciu blatu i panelu): wgrać obraz systemu ponownie z laptopa |

### G. Słowniczek

- **Praca zielona** — cyrkonia przed synteryzacją: biała, miękka, większa o współczynnik skurczu.
- **Współczynnik skurczu** — liczba z raportu MillBox (ok. 1,20–1,25), o którą praca jest powiększona przed piecem.
- **STL** — plik z kształtem 3D (siatka trójkątów); projekt z SharePointa, skan ze skanera i pliki do druku ramek są w tym samym formacie.
- **ICP** — algorytm, który nakłada skan na projekt tak, by odległości były najmniejsze.
- **Mapa odchyłek** — obraz, na którym każdy punkt skanu ma kolor zależny od odległości od projektu; ubytek to plama „pod powierzchnią”.
- **Pula** — lista projektów, wśród których program szuka dopasowania (dzień wieczorem, 3–4 dni rano).
- **Tryb cienia** — program ocenia i wskazuje, ale ludzie robią wszystko po staremu; służy do pomiaru skuteczności.
- **Top-1 / top-2** — trafność identyfikacji: właściwa kuweta jako pierwszy kandydat / wśród dwóch pierwszych.
- **Ramka świetlna** — obudowa z matrycą diod pod płytką; świeci przez otwory w dnach gniazd. Dwie: wieczorna przy skanerze, poranna w pokoju rozkładania.
- **Wkładka gniazda** — biała rama na blacie ramki, w której leży płytka; niesie czujniki i kołek orientacyjny; wymienna.
- **Układ gniazd** — rozmieszczenie gniazd, rynienki i stożków znaczników na płytce. [R59] Są dwa: nowy (wieczorna 18 gniazd i 1 rynienka, poranna 23 gniazda i 1 rynienka) i poprzedni, który zostaje w programie dla płytek wykonanych wcześniej.
- **Rynienka** — podłużne gniazdo na most; od R59 jedna na płytkę, czyli jeden most na płytkę.
- **PA12 (SLS/MJF)** — nylon drukowany w zewnętrznej drukarni z proszku; matowy, sztywny, znosi 70 °C.
- **PETG / FDM** — tworzywo i technologia drukarki z filamentu (u kolegi); [R55] na wszystko, co drukujemy sami: pokrywki, tulejki, podkładki, płytkę do testu skanera, prototypy pasowań.
- **Tulejka redukcyjna** — drukowany pierścień (zewnątrz ø11,85 mm, wcisk 0,15 mm; otwór ø8,2 mm) wciskany w otwór ø12 mm gniazda zasilania, gdy kupione gniazdo ma gwint ø8 mm; drukowana dopiero po zmierzeniu otworu w gotowym korpusie, bo otwór z druku może wyjść 11,7–11,9 mm [R53].
- **Podkładki dystansowe** — drukowane krążki 0,5 / 1 / 2 mm pod słupki panelu, wyrównują długość dystansów po pomiarach.
