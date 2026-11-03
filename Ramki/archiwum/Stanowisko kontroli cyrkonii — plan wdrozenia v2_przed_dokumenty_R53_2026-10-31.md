# Stanowisko kontroli cyrkonii — plan wdrożenia v2 (skaner laboratoryjny)

27 października 2026 · Michał · wersja 2 (zastępuje dokument z 25 października 2026)

## Streszczenie po ludzku

Budujemy na parapecie frezowni jedno stanowisko z laboratoryjnym skanerem 3D, które wieczorem wyłapuje ukruszone prace z cyrkonii zanim trafią do pieca, a rano mówi, która praca należy do której kuwety, i samo odhacza zlecenia w firmowym Excelu. Obsługa sprowadza się do ułożenia prac w gniazdach płytki i naciśnięcia spacji na laptopie; resztę robi program.

Jak to działa w jednym zdaniu: skaner mierzy całą płytkę prac naraz (do 24 koron i 2 mostów wieczorem, do 35 koron i 2 mostów rano), program nakłada każdą zmierzoną pracę na jej projekt z SharePointa i zaznacza miejsca, gdzie brakuje materiału; rano ten sam skan służy do rozpoznania, do którego zlecenia praca należy, a diody pod gniazdami podświetlają prace bieżącej kuwety.

Trzy cele i co dostajemy:

1. **Kontrola ukruszeń wieczorem** — automatyczna mapa płytki z czerwonymi gniazdami; technik bierze do ręki tylko oznaczone prace. Cel: większość ukruszeń brzegów od ok. 0,3 mm wykryta przed piecem; wykrywalność mierzymy na próbie testowej, nie zakładamy 100%.
2. **Szybsze rozkładanie rano** — program wskazuje kuwetę dla każdej pracy, a diody prowadzą rękę kuweta po kuwecie. Cel: duży piec z ok. 40 min do ok. 20–25 min.
3. **Excel** — zlecenia, których wszystkie punkty wyszły z pieca, odhaczają się same (zielone pole w kolumnie B), z logiem każdej zmiany. Cel: 10–15 min na piec do zera.

Co kupujemy: skaner laboratoryjny Aidite A-IS Pro 3 (ok. 20–25 tys. zł, przez istniejącą relację z Aidite; zamiennie Shining AutoScan-DS-EX Pro(H), DOF Freedom lub 3Shape F8), dwa komplety płytek z gniazdami (6 sztuk: 3 wieczorne i 3 poranne), dwie ramki świetlne (przy skanerze i w pokoju rozkładania) na Raspberry Pi z matrycą LED, bezprzewodową klawiaturę numeryczną, osłonę, drobne. Części ramek i płytek drukujemy w zewnętrznej drukarni z gotowych plików, a część ukrytych lub testowych elementów sami. Laptop daje firma. Oprogramowanie piszemy sami, bez płatnych bibliotek i subskrypcji.

Gdzie jesteśmy (27 października 2026): projekt ramek i płytek jest zamknięty w planie budowy v2, a obudowa została tak zaprojektowana, by nie zależała od wymiarów kupowanej elektroniki (zapasy, rowki i podkładki zamiast dopasowania po pomiarach). Pliki do druku są ostateczne, zweryfikowane trzykrotnie (generator, recenzent, niezależna kontrola pasowań); do drukarni: korpus W, korpus P, blat × 2 — od razu; wkładka × 3, płytki n1–n6 — po potwierdzeniu pola skanowania; pokrywki × 4 drukujemy sami po potwierdzeniu pola. Elektronikę ramek można zamawiać od razu. Aktualny model 3D z wymiarami do pomiaru: https://claude.ai/artifact/N1W9QKGcXq87t3GPhFp5Sf. Szczegółowa lista zakupów i instrukcje druku są w osobnym dokumencie „Zakupy i druk — stanowisko kontroli cyrkonii”.

Kiedy: zakup skanera poprzedza dwutygodniowy test na naszych pracach (płytka z 20 zielonymi i 10 spieczonymi pracami), który rozstrzyga wybór skanera. Potem 2–4 tygodnie dostawy, w tym czasie powstaje oprogramowanie i obie ramki, i tydzień uruchomienia. Realistycznie: stanowisko pracuje w trybie próbnym w połowie grudnia 2026, na pełnych obrotach w styczniu 2027.

Czego stanowisko nie zrobi: nie rozróżni dwóch niemal identycznych prac implantologicznych (różnią się tylko kolorem, którego nie ma w danych — pokaże obu kandydatów, decyduje człowiek) i nie zagwarantuje wykrycia każdego ukruszenia wielkości pół kryształu cukru.

## Co się zmieniło względem v1

Wszystkie poniższe zmiany wynikają z planu budowy ramek v2 i z decyzji właściciela; tam, gdzie poprzedni dokument podawał inne liczby lub elementy, obowiązuje plan v2.

| Obszar | Było (v1, 25 października) | Jest (v2) |
|---|---|---|
| Liczba gniazd | wieczorna 22 gniazda + 2 rynienki; poranna 30–32 gniazda | wieczorna 24 gniazda (13 × ø9, 6 × ø12, 5 × ø15) + 2 rynienki 60 × 15 mm; poranna 35 gniazd (22 × ø7,5, 7 × ø10, 6 × ø12,5) + 2 rynienki 50 × 13 mm; gniazda w rzędach, ścianki dokładnie 3 mm |
| Obudowa ramki | ok. 20 × 20 × 5,5 cm, szczegóły w osobnym opracowaniu | 200 × 200 × 63,6 mm (korpus 59,6 + blat 4); wysokość ustalona z zapasem 8 mm nad elektroniką i nie zmienia się po pomiarach; Raspberry Pi pod środkiem panelu; blat na 4 zatrzaskach i 2 wkrętach z tyłu, bez śrub na wierzchu; gniazdo zasilania w ścianie bocznej kieszeni wgłębionej w tylnej ściance (okno 51 × 24 mm), pasuje wtyk kątowy (zalecany) i prosty o korpusie do 37 mm od lica |
| Konstrukcja odporna na pomiary (R50) | obudowa do zamówienia dopiero po zmierzeniu panelu, Raspberry Pi i gniazd | korpus i blat niezależne od pomiarów: zapas 8 mm nad stosem Raspberry Pi, rowki pod słupki panelu na rozstaw 110–130 mm, otwór gniazda zasilania ø12 mm z drukowaną tulejką redukcyjną dla gniazda ø8, okno USB 16 × 9 mm z rowkami na rozstaw 23–28 mm, mocowanie panelu z gwintem (dystanse 50 mm + wkręty dociskowe) i bez gwintu (tulejki klejone + dystanse 45 mm), komplet podkładek 0,5/1/2 mm; pomiary elektroniki służą tylko doborowi sprzętu |
| Usunięte części | rama dyfuzora, uchwyty kabli, daszki nad szczelinami, żebra dna, szczelina karty pamięci, gniazda stopek, otwory i napis „GÓRA” w pokrywce | bez nich: panel ustalają 4 dystanse, kable trzymają podstawki opasek samoprzylepne i taśma VHB, stopki klejone na płaskim dnie, karta pamięci po zdjęciu blatu i panelu; bez pianek; napis na korpusie i wkręty tylne blatu zostają |
| Przycisk i czujnik gestu | brak przycisków z przodu (już w v1) | potwierdzone i rozszerzone: żadnego przycisku ani czujnika gestu w żadnej ramce; skan wieczorem uruchamia spacja na laptopie; przednia ścianka gładka, tylko wytłoczony napis |
| Różnice między ramkami | identyczne obudowy | identyczne; jedyna różnica to odbiornik USB klawiatury w ramce porannej i napis na przedniej ściance („RAMKA WIECZORNA” / „RAMKA PORANNA”) |
| Podstawka klawiatury | — | zrezygnowano; klawiatura leży luzem na stole, legenda klawiszy tylko w instrukcji programu |
| Wkładki gwintowane | wkładki mosiężne wtapiane | bez wkładek: wkręty formujące gwint wkręcane bezpośrednio w nylon PA12 (R49) |
| Płytki: materiał i druk | wszystko w zewnętrznej drukarni (SLS/MJF PA12) | w drukarni (PA12): korpus W i P, 2 blaty, 3 wkładki, płytki poranne nr 4–6 i wieczorne nr 1–3 (wieczorne alternatywnie z matowej żywicy w firmie, jeśli drukarka ma pole ≥ 100 × 100 mm); sami: 4 pokrywki z PETG u kolegi, 2 tulejki gniazda zasilania i 3 × 8 podkładek z żywicy w firmie, płytka do testu skanera i prototypy pasowań z żywicy |
| Kolejność zakupów | wszystko po teście skanera | elektronika ramek od razu; korpusy i blaty od razu (pliki ostateczne, nie zależą od pomiarów); płytki, wkładki i pokrywki po potwierdzeniu pola skanowania (pytanie do Aidite lub dystrybutora o zakres skanowania albo test na egzemplarzu testowym); tulejka i podkładki po pomiarach kupionej elektroniki |
| Pliki do druku | „w osobnym opracowaniu” | 15 plików do druku (10 do drukarni, 5 do druku własnego): pliki ostateczne, zweryfikowane trzykrotnie (generator, recenzent, niezależna kontrola pasowań); do drukarni: korpus W, korpus P, blat × 2 — od razu; wkładka × 3, płytki n1–n6 — po potwierdzeniu pola skanowania; pomiary elektroniki nie zmieniają już obudowy |
| Koszt akcesoriów | ok. 2–3,5 tys. zł | ok. 2,4–3,9 tys. zł (elektronika ramek 1,2–1,7 tys. zł, druk w drukarni 0,9–1,6 tys. zł w wariancie najtańszym lub 1,2–2,2 tys. zł w pokazowym, osłona 0,2–0,4, drobne 0,1–0,2); pokrywki, tulejki i podkładki drukowane samemu za koszt materiału |
| Identyfikacja płytki | magnesy + czujniki Halla (już w v1) | doprecyzowane: numer płytki = układ 3 magnesów w spodzie (płytki 1–3 wieczorne, 4–6 poranne), ten sam numer w dołkach kodu czytanych ze skanu i wytłoczonej cyfrze |

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
| Start skanu wieczorem | Spacja na laptopie; ramka bez przycisku i czujnika gestu | Mniej części i otworów w pyle, identyczne obudowy; stan ramki widać na matrycy |
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
10. Zakres prac: korony i mosty do 4 punktów (rynienki 60 × 15 mm); mosty powyżej 4 punktów są poza zakresem stanowiska.
11. Pole skanowania Aidite A-IS Pro 3 mieści płytkę 96 × 96 mm w całości (założenie 100 × 100 mm). Rozmiar płytki jest jedną liczbą w plikach projektu; jeśli pole okaże się mniejsze, płytki maleją, a w ramce wymienia się tylko wkładkę gniazda.
12. Panel LED i Raspberry Pi mają typowe wymiary (rozstaw otworów panelu 110–130 mm, elementy od spodu do 12 mm, stos Raspberry Pi z nakładką 26 mm). Obudowa ma na to zapasy (8 mm nad stosem, rowki pod słupki, okno USB z rowkami, otwór gniazda z tulejką), więc pomiary kupionej elektroniki nie zmieniają korpusu; przy nietypowym sprzęcie wystarczy wiercenie w dnie, tulejka lub podkładki.

Co jest warunkowe:

- Zakup konkretnego skanera zależy od testu z sekcji „Test przed zakupem”. Kryteria są liczbowe; skaner, który ich nie spełni, nie wchodzi w grę niezależnie od ceny.
- Poranek przez skaner zależy od jakości skanu spieczonych prac bez sprayu; jeśli pokrycie jest zbyt niskie, kamera nad ramką LED przejmuje poranek (koszt ok. 2 tys. zł, osobny moduł programu).
- Zamówienie płytek, wkładek i pokrywek zależy od potwierdzenia pola skanowania skanera (założenie 100 × 100 mm): odpowiedź Aidite lub dystrybutora o zakres skanowania albo skan płytki na egzemplarzu testowym. Korpusy i blaty nie zależą ani od tego, ani od pomiarów elektroniki.
- Automatyczne klikanie w programie producenta (bez dotykania myszki) zależy od tego, czy jego okna są stabilne; w razie czego technik klika sam „nowy skan → skanuj → zapisz”.

## Lista zakupów z parametrami

Skaner to ok. 85–90% kosztu; reszta to elektronika ramek, druk 3D i osłona. Ceny są orientacyjne (źródła z października 2026), do potwierdzenia ofertą. Pełna lista zakupów i druku jest w osobnym dokumencie „Zakupy i druk — stanowisko kontroli cyrkonii”.

### Skaner i laptop

| Pozycja | Parametry, które mają znaczenie | Ilość | Cena orientacyjna | Uwagi |
|---|---|---|---|---|
| Skaner laboratoryjny Aidite A-IS Pro 3 | 2 kamery 5 MP, dokładność 8 µm, światło niebieskie, eksport STL/PLY/OBJ, USB 3.0, 385 × 260 × 270 mm, 5 kg; wymagany tryb ręczny lub własna ścieżka skanu (obrót bez przechyłu); spokojny obrót stolika, bez szarpnięć przy starcie i zatrzymaniu (regulowana prędkość albo potwierdzenie w teście, kryterium 2); pole skanowania obejmujące całą płytkę 96 × 96 mm ze znacznikami narożnymi (założenie 100 × 100 mm, do potwierdzenia na egzemplarzu testowym, kryterium 8) | 1 | 20–25 tys. zł (oferta Aidite) | Warunek: pozytywny test z sekcji „Test przed zakupem” |
| Zamiennik 1: Shining AutoScan-DS-EX Pro(H) | Ta sama klasa: 2 × 5 MP, ≤ 8 µm, łuk 14 s, licencja wieczysta | — | ok. 7 tys. USD (USA), z Chin taniej | Gdy Aidite nie da trybu bez przechyłu |
| Zamiennik 2: DOF Freedom X5/UHD | Kamera jeździ wokół nieruchomego modelu, 5 MP, bez uchwytów | — | na zapytanie | Zdejmuje problem przechyłu konstrukcyjnie |
| Zamiennik 3: 3Shape F8 | Skan bez przechyłu, 4 × 5 MP, 4 µm, łuk 9 s, ScanIt Dental w zestawie, LabCare opcjonalny | — | na zapytanie, raczej ponad budżet | Najlepszy sprzęt, najwyższa cena |
| Laptop (daje firma) | Windows 11, i7/i9, 32 GB RAM, karta graficzna RTX, 1 TB SSD, 2 × USB 3.0, Excel/Outlook/OneDrive | 1 | — | Wymagania producentów skanerów: 16–32 GB, dedykowana karta |
| Opcja: kamera przemysłowa | 20 Mpx USB3 (Sony IMX183), np. Hikrobot MV-CS200-10UC + obiektyw 25 mm C-mount, panel LED podświetlający | 1 | 1,8–2,5 tys. zł | Tylko jeśli skan spieczonych prac wypadnie słabo (plan B poranka) |

### Ramki i płytki — streszczenie (pełna lista w dokumencie „Zakupy i druk”)

Szczegółowa lista zakupów (parametry do wyszukania w sklepie, ilości, ceny), tabela części do drukarni z objętościami, ustawienia drukarek i checklista odbioru są w osobnym dokumencie „Zakupy i druk — stanowisko kontroli cyrkonii”. Tu tylko streszczenie w 10 pozycjach (ceny orientacyjne z planu budowy v2):

| Nr | Pozycja | Co obejmuje | Kiedy zamawiać | Cena orientacyjna |
|---|---|---|---|---|
| 1 | Elektronika dwóch ramek | 2 panele LED 64 × 64 (P2.5), 2 Raspberry Pi 4 B 2 GB z radiatorami, 2 nakładki RGB Matrix Bonnet, 2 zasilacze 5 V 4 A, 2 karty 32 GB, klawiatura numeryczna 2,4 GHz z odbiornikiem USB | od razu | ok. 1 000–1 300 zł |
| 2 | Gniazda, kable, czujniki, drobne | 2 gniazda DC panelowe i wtyki, 2 gniazda USB panelowe, 10 czujników Halla, rezystory, 30 magnesów ø5 × 2, przewody, złącza, płytki prototypowe, podstawki opasek i taśma VHB, stopki, klej | od razu | ok. 150–250 zł |
| 3 | Sprzęt mocujący panel i blat | 8 dystansów M3 żeńsko‑żeńskich 50 mm (albo 45 mm + tulejki klejone, gdy panel nie ma gwintu), wkręty dociskowe M3 × 5, wkręty M3 × 10 z podkładkami ø9, wkręty M3 × 8, wkręty do tworzyw, śruby M2,5, epoksyd | od razu (dystanse w obu długościach albo po sprawdzeniu gwintu panelu) | ok. 80–120 zł |
| 4 | Pleksi mleczna 2 mm 160 × 160 | 2 szt. + 1 zapas, cięcie na wymiar | od razu | 10–20 zł/szt. |
| 5 | Korpusy i blaty (drukarnia, PA12 grafit) | korpus „RAMKA WIECZORNA”, korpus „RAMKA PORANNA”, 2 blaty | od razu — pliki ostateczne (nie zależą od pomiarów ani od skanera) | 551–980 zł (najtańszy) / 860–1 528 zł (pokazowy) |
| 6 | Płytki poranne nr 4–6 (drukarnia, PA12 biały) | 3 szt., 35 gniazd + 2 rynienki | po potwierdzeniu pola skanowania | 162–288 zł |
| 7 | Płytki wieczorne nr 1–3 | 3 szt., 24 gniazda + 2 rynienki; drukarnia PA12 biały albo matowa żywica w firmie | po potwierdzeniu pola skanowania | 156–279 zł (drukarnia) |
| 8 | Wkładki gniazda płytki (drukarnia, PA12 biały) | 2 + 1 zapas; prototyp z żywicy przed zamówieniem | po potwierdzeniu pola skanowania | 34–60 zł |
| 9 | Druk własny | 4 pokrywki (PETG u kolegi); 2 tulejki gniazda zasilania i 3 × 8 podkładek panelu (żywica w firmie, po pomiarach); płytka do testu skanera i prototypy pasowań (żywica) | pokrywki po potwierdzeniu pola; tulejka i podkładki po pomiarach; prototypy od razu | koszt materiału |
| 10 | Osłona, pokrowce, drobne stanowiska | osłona z czarnej płyty nad ramką przy skanerze (ok. 30 × 30 × 35 cm), pokrowce, hub USB 3.0, kable, listwa, ściereczki | przed tygodniem uruchomienia | 300–600 zł |

Razem bez skanera: elektronika i drobne 1 200–1 680 zł, drukarnia 904–1 607 zł (najtańszy, PA12 naturalny i grafit bez wygładzania) lub 1 212–2 155 zł (pokazowy: korpusy i blaty barwione i wygładzane), osłona i drobne stanowiska 300–600 zł — razem ok. 2,4–3,9 tys. zł (do 4,4 tys. zł w wariancie pokazowym).

Razem bez opcji: skaner 20–25 tys. zł + ramki, płytki, osłona i drobne 2,4–3,9 tys. zł = ok. 22,4–29 tys. zł. Z kamerą (plan B poranka): dodatkowo ok. 2 tys. zł.

Czego nie kupujemy: żadnego oprogramowania (program producenta jest w zestawie ze skanerem; reszta własna, na bibliotekach otwartych), żadnych subskrypcji, żadnych sprayów ani znaczników na prace; z części ramek — przycisku, czujnika gestu, wkładek gwintowanych, podstawki klawiatury, ramy dyfuzora, uchwytów kabli ani pianek.

## Architektura rozwiązania prostym językiem

Skaner dostarcza tylko pliki STL; cała logika siedzi w jednym programie na laptopie, który czyta projekty i raporty z lewej strony, a steruje ekranem, diodami i arkuszem z prawej.

architektura · 4 źródła danych, 1 program, 3 wyjścia (schemat w wersji PDF)

Żadne dane nie opuszczają firmowego laptopa ani firmowego Microsoft 365, a prace nie dostają żadnych oznaczeń.

Elementy i ich rola:

1. **Skaner laboratoryjny** — mierzy całą płytkę naraz i zapisuje jeden plik STL (siatka trójkątów ze wszystkimi pracami i płytką). Jego własny program obsługuje skan i eksport; nasz program czeka na plik w folderze.
2. **Płytka z gniazdami** — nadaje pracom znane miejsca: program wie, gdzie na płytce jest gniazdo numer 13, więc może powiedzieć „czerwone jest 13” i zapalić diodę dokładnie pod nim. Trzy stożki w narożnikach pozwalają programowi wyrównać skan do rysunku płytki z dokładnością poniżej 0,1 mm; współrzędne gniazd leżą w pliku obok modelu, więc zmiana układu nie wymaga zmiany kodu.
3. **Projekty STL** — wzorzec, do którego porównujemy. Wieczorem projekt jest powiększony o współczynnik skurczu krążka (z raportu MillBox), rano w wymiarach 1:1.
4. **Dopasowanie 3D** — program najpierw zgaduje, który projekt pasuje (objętość, wymiary, kształt), potem nakłada go na pomiar z dokładnością do setnych milimetra (algorytm ICP, otwarta biblioteka Open3D).
5. **Wykrywanie ubytków** — po nałożeniu liczymy, gdzie pomiar leży pod powierzchnią projektu. Mały, ostry, lokalny ubytek przy brzegu to ukruszenie; gładka, rozległa różnica to ręczna poprawka technika albo luz pasowania i nie jest zgłaszana.
6. **Identyfikacja** — rano to samo dopasowanie, ale do puli zleceń z ostatnich dni; wynik to numer kuwety i nazwa zlecenia (nazwa folderu, równa kolumnie H w Excelu).
7. **Ramki świetlne** — dwie: przy skanerze (wieczór: czerwone gniazda do sprawdzenia) i w pokoju rozkładania (poranek: zielone gniazda bieżącej kuwety, jej numer na marginesie matrycy wokół płytki). Każda rozpoznaje płytkę po magnesach w jej spodzie i rozmawia z laptopem przez Wi‑Fi. Czerwień = sprawdź, zieleń = bieżąca kuweta, bursztyn = poprawka, biel = praca nieznana. Stan ramki pokazuje kolor marginesu matrycy; skan uruchamia spacja na laptopie, rano kuwety przełącza bezprzewodowa klawiatura numeryczna. Ramki nie mają żadnych przycisków.
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

1. Wycina prace z krążka i szlifuje piny jak dziś. Każdą gotową pracę odkłada do wolnego gniazda płytki brzegiem do góry (powierzchnią żującą w dół); mosty do rynienek. Rozmiar gniazda dobiera na oko — program nie dba, które gniazdo. Płytka ma gniazda w rzędach od najmniejszych z przodu do rynienek z tyłu.
2. Gdy płytka jest pełna albo krążek skończony: wsuwa płytkę do skanera do oporu (wycięcie orientacyjne wymusza jedno ułożenie) i naciska spację na laptopie. Zaczyna ładować drugą płytkę albo wraca do wycinania.
3. Po 60–90 s ekran pokazuje mapę płytki: zielone gniazda bez uwag, czerwone z podejrzeniem ubytku, szare „bez projektu” (program nie dopasował żadnego STL — ogląda się jak dziś, gołym okiem). Ramka przy skanerze świeci to samo pod płytką, gdy technik ją na niej położy.
4. Wyjmuje płytkę. Czerwone prace bierze do ręki; kliknięcie czerwonego gniazda na ekranie laptopa pokazuje pracę w 3D z mapą odchyłek (od turkusu do czerwieni) i powiększeniem miejsca ubytku z jego rozmiarem.
5. Decyzja jednym przyciskiem na ekranie: „Ukruszona” — praca idzie na bok, program dopisuje do dziennej listy „do dofrezowania” zlecenie, ząb i krążek i zapamiętuje, że tego punktu zabraknie rano (dofrezowany ząb wyjdzie z innego pieca, zwykle następnego dnia); „OK” — fałszywy alarm, praca wraca do obiegu.
6. Reszta prac idzie do opakera i pojemników do pieca dokładnie jak dziś. Nic nie jest zapisywane o tym, która praca do którego pieca.

Co robi program w tle:

- Czeka na nowy plik STL w folderze eksportu skanera i zaczyna analizę w ciągu sekundy od zapisu.
- Wyrównuje skan do rysunku płytki po trzech znacznikach narożnych, odczytuje numer płytki z dołków kodu i tnie skan na gniazda.
- Dla każdego gniazda szuka projektu w puli dnia (lista STL z raportów MillBox, każdy powiększony o współczynnik swojego krążka): najpierw po objętości i wymiarach (odrzuca 90% kandydatów w ułamku sekundy), potem po kształcie (dopasowanie 3D). Próg akceptacji: co najmniej 85% powierzchni skanu w odległości do 0,05 mm od projektu.
- Liczy mapę odchyłek i wyszukuje ubytki: obszary, gdzie skan leży co najmniej 0,08 mm pod powierzchnią projektu, o średnicy 0,2–1,5 mm, z ostrą krawędzią, w pasie do 1,5 mm od brzegu lub na krawędziach. Progi są w ustawieniach i stroi się je na próbie testowej.
- Odróżnia poprawkę ręczną: gładka różnica na obszarze większym niż 2 mm bez ostrej krawędzi nie jest zgłaszana.
- Zapisuje w lokalnej bazie: plik skanu, gniazdo, dopasowany projekt, wynik, decyzję technika, czas.

Czas na płytkę (do 24 koron i 2 mostów): ułożenie w gniazdach zastępuje odkładanie na tackę (bez dodatkowego czasu), zaniesienie i start 15 s, skan 30–60 s i analiza 20–40 s w tle, spojrzenie na ekran i wyjęcie czerwonych 30–60 s. Netto 1–2 min pracy technika na płytkę, czyli 10–20 min na typowy wieczór z 7–10 płytkami.

Sytuacje szczególne:

- Praca bez projektu w puli (np. dofrezowana z innego krążka, którego raport nie dotarł): gniazdo szare, komunikat „sprawdź ręcznie”; program próbuje także puli z poprzedniego dnia.
- Poprawka z obróbki (jeden ząb dofrezowany do zlecenia, które już wyszło z pieca): program dopasowuje go jak każdą inną pracę, bo jego STL jest w dzisiejszym raporcie MillBox; na ekranie dopisek „poprawka: zlecenie już odhaczone”, żeby rano nikt nie czekał na resztę zlecenia. Nikt niczego nie musi zapisywać przy przyjęciu poprawki.
- Dwie prace w jednym gnieździe albo praca poza gniazdem: gniazdo żółte „popraw ułożenie”, skan do powtórzenia.
- Podwójna powierzchnia w skanie (praca drgnęła w czasie skanu): program to wykrywa i prosi o ponowny skan tej płytki zamiast zgłaszać fałszywe ubytki.
- Most 4-punktowy w rynience: analiza jak dla korony, brzegi każdego punktu i łączniki osobno.
- Prace implantologiczne: wyznacznikiem są brzeg przy łączniku i krawędzie kanału śruby; sam kanał jest wyłączony z analizy.

## Przepływ poranny krok po kroku

Rano znika szukanie: każda praca z pojemnika dostaje numer kuwety w ciągu minuty od skanu, a diody pod gniazdami pokazują, które prace zabrać do kuwety trzymanej właśnie w ręku.

Przymierzanie na modelach zostaje tam, gdzie jest potrzebne do korekty; przestaje być sposobem na rozpoznanie, do kogo należy korona.

Krok po kroku (osoba rozkładająca piece):

1. Otwiera pojemniki z pieca i przekłada prace (40–70 °C) do gniazd płytek porannych brzegiem do góry. Duży piec to 2 płytki po 35 gniazd i 2 rynienki, mały — jedna.
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

Czas (duży piec, 40–60 prac, 2 płytki poranne): przełożenie do gniazd zastępuje wyjmowanie na blat; skany 2 × 90 s w tle przy piecu; w pokoju rozkładania ok. 8–12 s na pracę według diod, dwuznaczne i nieznane 20–30 s na pracę. Cel: 20–25 min na duży piec zamiast 40, bez osobnego odhaczania w Excelu.

Plan B poranka: jeśli skan spieczonej, przeziernej cyrkonii bez sprayu daje mniej niż ok. 70% powierzchni, poranek przejmuje kamera 20 Mpx nad ramką LED: jedno zdjęcie płytki, identyfikacja po obrysie i widoku wnętrza, te same diody i ten sam Excel. Decyzja po teście z sekcji „Test przed zakupem”.

## Ramki świetlne i płytki — projekt, zakupy, montaż

### Co to jest i jak działa

Ramka to „dom” płytki poza skanerem: zamknięta kostka 200 × 200 × 63,6 mm (korpus 59,6 mm + blat 4 mm) z matrycą 64 × 64 diod pod mleczną szybką. Wysokość jest ustalona z zapasem 8 mm nad elektroniką, więc nie zmienia się po zmierzeniu kupionych części. Płytka leży na środku we wkładce; wokół niej zostaje pas matrycy ok. 28 mm (11 pikseli) z każdej strony na cyfry i kolor stanu. Diody świecą przez otwory w dnie gniazd. W środku: Raspberry Pi 4 z nakładką sterującą matrycą (pod środkiem panelu), panel na 4 mosiężnych dystansach, zasilacz 5 V. Z zewnątrz: z tyłu kieszeń wgłębiona (okno 51 × 24 mm) z gniazdem zasilania w jej bocznej ścianie — wtyk kątowy (zalecany) ani prosty o korpusie do 37 mm od lica nie wystaje poza obrys, więc ramkę można wsuwać do szafki — oraz gniazdo USB serwisowe z zaślepką; szczeliny wentylacyjne nisko w ścianach (4 z tyłu, po 3 z boków) i 2 wloty w dnie; stopki klejone na płaskim dnie; karta pamięci dostępna po zdjęciu blatu i panelu. Z przodu nic poza wytłoczonym napisem. Żadnych śrub na wierzchu: blat trzymają 4 zatrzaski i 2 wkręty w tylnej ściance.

Obie ramki mają identyczną obudowę i elektronikę. Różnią się tylko:

- odbiornikiem USB klawiatury numerycznej wpiętym do Raspberry Pi w ramce porannej,
- napisem na przedniej ściance: „RAMKA WIECZORNA” / „RAMKA PORANNA”.

Ramka wieczorna stoi przy skanerze pod osłoną i po skanie pokazuje czerwone i zielone gniazda. Ramka poranna między porankami leży w szafce, rano stawia się ją na stole w pokoju rozkładania. Obie rozmawiają z laptopem przez firmowe Wi‑Fi (zapas: hotspot laptopa).

Wkładka gniazda (biała rama na blacie) jest osobną, tanią częścią: ustala położenie płytki z powtarzalnością ±0,5 mm, niesie 3 czujniki magnetyczne pod narożnikami płytki i kołek orientacyjny, który wchodzi w wycięcie płytki. Jeśli test skanera wymusi mniejszą płytkę, wymienia się tylko wkładkę, nie ramkę.

Płytki: obie 96 × 96 × 8 mm, ten sam obrys, więc ta sama wkładka. Każda ma 3 stożki narożne dla skanera, wycięcie orientacyjne w czwartym narożniku, dołki kodu przy lewej krawędzi (skaner czyta numer płytki ze skanu), kieszenie na magnesy od spodu (ramka czyta numer przez czujniki), wytłoczoną cyfrę i rowek na pokrywkę. Numery 1–3 to płytki wieczorne, 4–6 poranne; brak magnesów = brak płytki. Pokrywka (jedna na obie płytki) zatrzaskuje się w rowek i zostawia 14 mm prześwitu nad płytką.

| Część | Ile | Materiał | Skąd |
|---|---|---|---|
| Płytka wieczorna nr 1, 2, 3 | 3 | PA12 biały, mat (alternatywa: matowa żywica z firmy) | drukarnia albo firma |
| Płytka poranna nr 4, 5, 6 | 3 | PA12 biały, mat (znosi 40–70 °C) | drukarnia |
| Pokrywka | 4 | PETG | sami (FDM u kolegi) |
| Korpus (napis W / P) | 2 | PA12 grafit | drukarnia |
| Blat | 2 | PA12 grafit | drukarnia |
| Wkładka gniazda | 2 + 1 zapas | PA12 biały | drukarnia (prototyp z żywicy w firmie) |
| Tulejka redukcyjna gniazda zasilania (gdy gniazdo ma gwint ø8) | 2 | żywica (albo PETG) | sami (firma) |
| Podkładki pod dystanse panelu 0,5 / 1 / 2 mm | 3 × 8 | żywica (albo PETG) | sami (firma) |

### Co zamawiamy w drukarni, a co drukujemy sami — i dlaczego

Zasada: części widoczne i nośne zamawiamy (MJF/SLS, nylon PA12), części ukryte lub robocze drukujemy sami: z PETG (nie z PLA, bo pokrywka i płytka poranna widzą 40–70 °C) albo z żywicy. Dostępne drukarki: FDM u kolegi, żywiczna (SLA/DLP) w firmie.

| Część | Decyzja | Dlaczego |
|---|---|---|
| Korpus W i P, blat | zamówić (PA12 grafit) | największe części, gładki grafit na pokaz; zatrzaski i kieszenie wymagają dokładności; kołnierz 194 mm w FDM się wypacza |
| Płytki poranne nr 4–6 | zamówić (PA12 biały) | prace 40–70 °C; standardowa żywica modelowa się odkształci; mat biały dla skanera |
| Płytki wieczorne nr 1–3 | zamówić w PA12 **albo** wydrukować w firmie z matowej, sztywnej żywicy (biała / kość słoniowa), jeśli drukarka ma pole robocze ≥ 100 × 100 mm | prace zielone, zimne; oszczędność ok. 156–279 zł; decyzja po teście skanera |
| Wkładka gniazda | zamówić 2 (PA12 biały) + wydrukować 1 prototyp z żywicy w firmie przed zamówieniem | tania, ale to ona decyduje o pasowaniu płytki; prototyp sprawdza kołek, półki i kieszenie czujników |
| Pokrywka × 4 | sami (PETG, FDM u kolegi) | oszczędność ok. 110–190 zł; zatrzaski wymagają ciągliwości, więc nie żywica; bez otworów i napisu, drukowana wierzchem do stołu |
| Tulejka gniazda zasilania × 2, podkładki panelu 3 × 8 | sami (żywica w firmie, po pomiarach) | małe, dokładne części; potrzebne tylko gdy gniazdo ma gwint ø8 lub dystans wymaga wyrównania; druk w minuty |
| Prototypy pasowań | sami przed zamówieniem: 1 płytka, 1 wkładka, 1 pokrywka, próbka zatrzasku blatu | test realnych luzów za kilka złotych materiału, zanim pójdzie ok. 1 500 zł do drukarni |
| Płytka do testu skanera | 1 płytka wieczorna z matowej żywicy w firmie, gotowa na test egzemplarza skanera | rozstrzyga założenie o polu skanowania 100 × 100 mm i czy program widzi 3 stożki i dołki kodu; skanera jeszcze nie ma, więc test odbędzie się na egzemplarzu testowym (albo wystarczy pisemna odpowiedź producenta o zakresie skanowania) |

Jeśli drukarka FDM nie będzie dostępna: zamówić wszystko, a prototypy pasowań zlecić w tej samej drukarni jako tanie próbki przed głównym zamówieniem.

### Montaż i testy (z planu budowy v2, sekcja 9)

Bez wkładek gwintowanych: wkręty formujące gwint do tworzyw (PT 3,0 × 8 w słupkach blatu i PT 2,5 × 6 pod Raspberry Pi) wkręca się wprost w otwory w nylonie, raz „na sucho” przed montażem. Panel trzymają mosiężne dystanse, blat — zatrzaski i 2 wkręty. Każdy krok ma kryterium zaliczenia.

| Krok | Czynność | Kryterium zaliczenia |
|---|---|---|
| 1 | Zamówienie bez pomiarów elektroniki: korpusy i blaty od razu (pliki ostateczne); wkładki i płytki po potwierdzeniu pola skanowania; pomiary elektroniki służą potem tylko doborowi dystansów, tulejki i podkładek | arkusz zamówienia ma objętości wszystkich plików; drukarnia potwierdziła PA12, kolory i gabaryt 200 × 200 × 60 |
| 2 | System na stole: karta z systemem, Wi‑Fi firmowe, biblioteka matrycy, konfiguracja nakładki | zdalne logowanie działa; obraz testowy stabilny bez migotania |
| 3 | Panel + nakładka + zasilacz: wzór testowy, cyfry na marginesie, pomiar poboru prądu | pełna biel < 3,5 A; typowy obraz ramki < 1,5 A; Pi nie restartuje się |
| 4 | Klawiatura (ramka P): odbiornik w Pi, odczyt klawiszy. Ramka W: zdarzenie „Skanuj” wysyłane z laptopa (spacja) przez Wi‑Fi | każdy klawisz daje właściwe zdarzenie; spacja na laptopie zmienia stan ramki W w < 1 s |
| 5 | Czujniki Halla na stole: płytka prototypowa, 3 czujniki, test magnesem | każde wejście reaguje na magnes ≤ 4 mm; odwrócony biegun = brak reakcji (to mówi, którą stroną kleić) |
| 6 | Części z druku: oględziny, wypłukanie proszku, pasowanie na sucho: płytka we wkładce, wkładka na blacie, pokrywka na płytce, blat na korpusie | płytka wchodzi i wychodzi bez siły, luz < 0,5 mm; pokrywka trzyma po odwróceniu; blat zatrzaskuje się i daje się zdjąć ręką |
| 7 | Gwinty: każdy otwór przegwintować raz wkrętem, wolno, bez siły (korpus: 4 otwory Raspberry Pi; blat: 2 słupki) | wkręt wchodzi bez oporu i trzyma; gwint nie wyrobiony po 3 cyklach |
| 8 | Najpierw wpiąć wtyk DC kabla wewnętrznego w gniazdo nakładki (po przykręceniu Pi zostaje tylko 7,5 mm do ściany), potem Pi + nakładka na słupkach, listwa wyprowadzeń. Przed postawieniem panelu wkręcić gniazdo USB panelowe w rowki (od wnętrza jest tylko 14,3 mm do dystansu). Panel: z gwintem — wkręty dociskowe M3 × 5 w otwory panelu, dystanse 50 mm nakręcone; bez gwintu — tulejki klejone epoksydem do spodu panelu + dystanse 45 mm; panel postawiony tak, by dystanse trafiły w rowki dna, 4 wkręty M3 × 10 z podkładkami ø9 od spodu; przy otworach panelu poza rowkami: wiercenie ø4 w dnie w zmierzonym miejscu + podkładka | stos Pi nie dotyka panelu (szczelina ≥ 2 mm); panel równoległy do dna (< 0,5 mm na rogach); nic nie wystaje od strony diod |
| 9 | Pleksi w kieszeni blatu (rogi bez fazowania), próba zamknięcia blatu na korpusie z panelem | blat zamyka się do końca; okno równo nad panelem (< 1 mm); panel nie dotyka spodu blatu |
| 10 | Wkładka: czujniki wklejone w kieszenie półek, przewody w rowkach do płytki prototypowej; magnesy w uszach wkładki i w blacie | wkładka siada na kołkach i trzyma magnesami; płytka testowa wchodzi na kołek tylko w jednej orientacji |
| 11 | Magnesy w płytkach według kodów (nr 1: A; 2: B; 3: A+B; 4: C; 5: A+C; 6: B+C), biegun S w dół, klej | odczyt pokazuje 1…6 dla każdej płytki, 0 bez płytki; stabilny 60 s; zmiana < 100 ms po położeniu |
| 12 | Okablowanie końcowe: gniazdo zasilania przez okno kieszeni w otwór jej bocznej ściany (przy gwincie ø8 najpierw tulejka), USB panelowe już wkręcone w kroku 8 (flansza z otworami pionowymi: wywiercić 2 × ø3,2 przed krokiem 8), podstawki opasek i płytka prototypowa na taśmie VHB (powierzchnie przemyć alkoholem), opaski, opisy; odbiornik klawiatury (P); stopki 12 mm od krawędzi | żaden kabel nie dotyka diod ani radiatora; blat daje się zdjąć bez rozpinania; obudowa stoi stabilnie; wtyk nie wystaje poza obrys |
| 13 | Kalibracja gniazdo → diody: program zapala kolejno pole pod każdym gniazdem, operator potwierdza lub przesuwa; wynik do pliku obok płytki (osobno wieczorna i poranna) | każde gniazdo z pracą świeci widocznie przez otwór, sąsiednie ciemne |
| 14 | Test 8 h pełnego świecenia z logiem temperatury; po 8 h wyrwanie zasilania | Pi < 70 °C; zasilacz letni; po włączeniu ramka wstaje sama w < 60 s; karta bez błędów |
| 15 | Druga ramka z poprawkami z pierwszej; lista zmian wpisana do planu | obie ramki przechodzą kroki 11–14 |

Narzędzia: lutownica (tylko do kabli), multimetr, wkrętaki (w tym imbus do wkrętów dociskowych), klucz 14 do nakrętki gniazda, pęseta, papier ścierny, klej CA, epoksyd, alkohol do odtłuszczenia, marker, magnes wzorcowy lub kompas (bieguny), suwmiarka, wiertła ø3,2 i ø4 (tylko do ewentualnych poprawek), laptop z czytnikiem kart. Bez grotu do wkładek.

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
| plate | Zna rysunek płytki z pliku układu gniazd: współrzędne gniazd, znaczników i dołków kodu; wyrównuje skan do płytki (ICP na stożkach), czyta numer płytki, tnie skan na gniazda, wykrywa gniazda puste, podwójne i prace poza gniazdem | STL płytki → lista fragmentów z numerem gniazda | średnia |
| match | Identyfikuje fragment: filtr po objętości i wymiarach, zgrubne dopasowanie, ICP, ocena dopasowania; wieczorem pula dnia ze skalą z raportu, rano pula 3–4 dni w skali 1:1; zwraca ranking kandydatów z pewnością | fragment + pula → kandydat(ci) + transformacja | wysoka |
| inspect | Mapa odchyłek skan–projekt; wyszukuje ubytki (ostre, małe, przy brzegu lub krawędzi); odrzuca gładkie poprawki ręczne; wykrywa podwójne powierzchnie (praca drgnęła) | fragment + projekt → lista ubytków z położeniem i rozmiarem | wysoka |
| session | Logika wieczoru i poranka: stan płytki, decyzje technika, sesja pieca, zliczanie punktów zleceń (trwałe, między piecami i dniami), lista braków, lista „do dofrezowania”, oznaczanie poprawek | zdarzenia → stan | niska |
| ui | Ekran wieczorny (mapa płytki, czerwone gniazda, widok 3D z mapą odchyłek i powiększeniem ubytku), ekran poranny (podpisy, kandydaci, kuweta po kuwecie), ustawienia progów, start skanu spacją, obsługa klawiatury ramki porannej | stan → ekran | średnia |
| indicate | Mapowanie gniazdo → diody, komunikaty do obu ramek przez Wi‑Fi (plan płytki, stan, potwierdzenia z klawiatury) | polecenia → światło | niska |
| excel | Znajduje wiersz zlecenia i koloruje pole B na zielono; log; tryb „pytaj przed zapisem” | zlecenie → zmiana w Excelu + wpis w logu | niska, ale wrażliwa |
| scanner | Obserwuje folder eksportu; opcjonalnie klika w programie producenta; waliduje plik (rozmiar, liczba trójkątów) | plik → zdarzenie „nowy skan” | niska |

Struktura repozytorium: program stanowiska (moduły powyżej), program ramki na Raspberry Pi (matryca, Wi‑Fi, klawiatura, czujniki Halla), modele płytek z plikami układu gniazd, testy na danych syntetycznych z prawdziwych STL, narzędzia (generator sztucznych ubytków, raport metryk, kalibracja ramek), jeden plik ustawień (ścieżki, progi, parametry skanera) i instrukcja (uruchomienie, codzienna obsługa, co robić gdy nie działa).

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

Gdzie i z kim: najlepiej egzemplarz Aidite A-IS Pro 3 u nas na 2 tygodnie (relacja dużego klienta); równolegle zapytanie do DOF (Freedom X5/UHD) i 3Shape (F8) o wycenę i ten sam test u dystrybutora. Wcześniej, bez kupowania czegokolwiek, próba ze skanerem wewnątrzustnym Medit i700/i900 z firmy: ten sam zestaw prac, ręczny skan, ocena w CloudCompare — odpowiada na pytanie o widoczność ubytków w świetle strukturalnym.

Do uzgodnienia z Aidite (przed testem i w umowie):

- Egzemplarz testowy na 2 tygodnie z aktualnym oprogramowaniem i kontakt do inżyniera aplikacyjnego, nie handlowca.
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
| Zielony siekacz dolny (najmniejsza praca) | 1 | najmniejsze gniazdo, pokrycie |
| Zielony most 4-punktowy | 1 | rynienka, łączniki |
| Zielone korony implantologiczne, w tym dwie niemal identyczne | 3 | kanał śruby, bliźniaki |
| Spieczone korony (różna przezierność, w tym 5Y) | 8 | skan bez sprayu, poranek |
| Spieczony most | 2 | jak wyżej |
| Projekty STL wszystkich powyższych + współczynniki z raportów MillBox | komplet | porównanie |
| Płytka wieczorna wydrukowana w firmie z matowej żywicy (z gotowych plików) | 1–2 | pole skanowania, ułożenie, znaczniki, dołki kodu |

Przebieg:

1. Skan pustej żywicznej płytki: czy cała płytka 96 × 96 mm ze stożkami narożnymi mieści się w jednym skanie i czy program widzi 3 stożki i dołki kodu (kryterium 8). To rozstrzyga zamówienie płytek w drukarni.
2. Ułożenie 20 zielonych prac na płytce, brzegiem do góry. Zdjęcie telefonem (dokumentacja ułożenia).
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
| 8 | Pole skanowania | mieści całą płytkę 96 × 96 mm ze znacznikami narożnymi w jednym skanie | mniejsza płytka (np. 80 × 80) i mniej gniazd; w ramce wymienia się tylko wkładkę gniazda, nowe pliki płytek powstają z jednej zmienionej liczby |

Wynik testu to jedna strona: tabela kryteriów z wynikami, 3 zrzuty map odległości (ubytki), czasy. Na tej podstawie zamówienie skanera i płytek — i jednocześnie pierwsze prawdziwe skany do strojenia programu.

## Co przygotowuję, czekając na dostawę

W dniu dostawy skanera ma być gotowe wszystko poza samym podłączeniem: program przetestowany na sztucznych skanach i na plikach z testu u dostawcy, płytki i obudowy ramek dostarczone i złożone, obie ramki działające, Excel sprawdzony na kopii. Praca po godzinach, ok. 6–10 h tygodniowo.

Tydzień 0 (27 października – 1 listopada, przed testem i prezentacją):

- Ramki: wycena u 2–3 drukarni i zamówienie korpusów (W i P) oraz 2 blatów — pliki ostateczne, nie zależą od pomiarów elektroniki ani od skanera.
- Zamówienie elektroniki ramek i drobnych (dokument „Zakupy i druk”); dystanse panelu w obu długościach (50 i 45 mm) albo po sprawdzeniu gwintu panelu.
- Druk w firmie z żywicy: płytka wieczorna do testu skanera i prototyp wkładki; u kolegi z PETG: pokrywka i próbka zatrzasku blatu — test pasowań na sucho. Pytanie do Aidite lub dystrybutora o zakres skanowania (czy mieści 96 × 96 mm).
- Zestaw testowy prac, ubytki wykonane i zmierzone.
- Próba ze skanerem wewnątrzustnym z firmy + CloudCompare: pierwsze mapy odległości.
- Zapytania: Aidite (egzemplarz testowy, tryb bez przechyłu, pole skanowania, cena), DOF i 3Shape (wycena, test).
- Na laptopie: OneDrive z folderem „Cyrkon”, Excel z plikiem produkcyjnym (Autozapis), sprawdzenie, że COM widzi otwarty skoroszyt.
- Repozytorium, środowisko Pythona, pliki opisu modułów dla Claude Code.

Tydzień 1 (2–8 listopada):

- Po dostawie elektroniki: pomiary (panel, stos Pi, gniazda) — służą tylko doborowi sprzętu: długość dystansów, tulejka gniazda, podkładki, ewentualne wiercenie; druk tulejek i podkładek z żywicy w firmie.
- Elektronika ramki na stole (kroki 2–5 montażu): system, matryca, klawiatura, czujniki.
- Generator danych syntetycznych: sztuczne skany z 30 prawdziwych STL.
- catalog: indeks folderów, parser nazw, parser raportów MillBox (na 10 prawdziwych raportach), cechy STL, baza. plate: wyrównanie po znacznikach, odczyt kodu płytki, cięcie na gniazda — testy na danych syntetycznych z prawdziwym układem gniazd z gotowych plików płytek.

Tydzień 2 (9–15 listopada, test skanera u nas):

- Pierwszego dnia testu: skan żywicznej płytki (kryterium 8) → zamówienie płytek i wkładek w drukarni (poranne na pewno; wieczorne w drukarni albo z żywicy w firmie) i pokrywek u kolegi — chyba że producent potwierdzi zakres skanowania wcześniej, wtedy zamówienie od razu.
- match: filtr po objętości i wymiarach, zgrubne dopasowanie, ICP, ranking; metryka: trafność top-1 i top-2 na 200 sztucznych fragmentach.
- inspect: mapa odchyłek, wykrywanie ubytków, odrzucanie gładkich poprawek, wykrywanie podwójnych powierzchni; metryka: wykryte / pominięte / fałszywe na 100 sztucznych ubytków.

Tydzień 3 (16–22 listopada):

- Dostawa korpusów i blatów: montaż pierwszej ramki (kroki 6–14), oprogramowanie ramki (Wi‑Fi, protokół „płytka, gniazdo, kolor”, „stan”, potwierdzenia); wkładki i płytki dochodzą po potwierdzeniu pola skanowania; kalibracja gniazdo → diody; indicate.
- ui: ekran wieczorny i poranny z dużymi kafelkami, widok 3D z mapą odchyłek, start skanu spacją; przegląd z technikiem na sztucznych danych (czy rozumie bez instrukcji).
- excel: reguły wyszukiwania wiersza przetestowane na kopii pliku (50 kuwet z historii, porównanie z tym, co zaznaczył człowiek); tryb „[cytat usuniety]”.

Tydzień 4 (23–29 listopada, zamówienie skanera, pliki z testu w ręku):

- Druga ramka z poprawkami z pierwszej; płytki z drukarni: magnesy według kodów, test odczytu, kalibracja diod dla obu kompletów.
- match i inspect dostrojone na prawdziwych skanach z testu; progi zapisane w ustawieniach.
- session: sesja pieca, lista braków, lista „do dofrezowania”, log. scanner: obserwacja folderu; próba automatu klikającego na wersji demo programu producenta (jeśli dostępna).
- Instrukcja jednostronicowa dla technika (obrazki, 6 kroków) i dla poranka; checklista uruchomienia.
- Osłona i pokrowce; miejsce na parapecie wymierzone i oklejone (schemat w załączniku).

Zasada: każdy tydzień kończy się działającą, przetestowaną wersją, którą da się pokazać na ekranie, nawet bez skanera.

## Tydzień uruchomienia: dzień po dniu

Tydzień kończy się stanowiskiem pracującym w trybie cienia: program ocenia i wskazuje, a ludzie robią jeszcze wszystko po staremu, żeby porównać wyniki bez ryzyka dla produkcji. Pełne przejście następuje po dwóch tygodniach cienia i po spełnieniu kryteriów z sekcji „Testy odbiorcze”.

| Dzień | Co robię | Kto jest potrzebny | Kryterium końca dnia |
|---|---|---|---|
| 1 (pon.) | Rozpakowanie, ustawienie skanera na parapecie, instalacja programu producenta na laptopie, kalibracja, strategia skanu „płytka: obrót, przechył 0”, eksport STL do folderu obserwowanego; ustawienie ramki wieczornej przy skanerze i osłony; ramka poranna w pokoju rozkładania z klipsem kabla przy stole | ja; serwis Aidite zdalnie, jeśli trzeba | Skan testowej płytki ląduje jako plik w folderze i program go rozpoznaje |
| 2 (wt.) | Pierwsze prawdziwe płytki zielonych prac: wyrównanie po znacznikach, cięcie na gniazda, dopasowanie do projektów z raportów; kalibracja progów na 10 pracach ze znanymi ubytkami | ja, 1 h technika | Trafność dopasowania na 40 pracach ≥ 85%; 10 znanych ubytków: wykryte ≥ 8 |
| 3 (śr.) | Wieczorny pilotaż z technikiem w trybie cienia (technik ogląda jak dziś, a ekran dodatkowo pokazuje czerwone); rano pilotaż identyfikacji na jednym piecu bez zapisu do Excela (log porównawczy z tym, co zaznaczył człowiek) | technik wieczorny, ja rano | Technik obsługuje bez pomocy; lista różnic do przejrzenia |
| 4 (czw.) | Poprawki po pilotażu; włączenie diod; Excel w trybie „pytaj przed zapisem” na jednym piecu; pomiar czasów stoperem | ja, druga osoba poranna jako audytor Excela | 0 błędnych wierszy w Excelu; czas pieca zmierzony |
| 5 (pt.) | Pełny dzień w trybie cienia: wszystkie piece, wszystkie płytki; przegląd metryk; instrukcje wywieszone przy stanowisku; przekazanie checklisty „co robić, gdy” | wszyscy, 15 min odprawy | Metryki z dnia zapisane; decyzja: cień przez 2 tygodnie |

Przez 2 tygodnie trybu cienia:

- Wieczorem technik zaznacza na ekranie także prace, które sam uznał za ukruszone, a program nie — to daje liczbę pominięć.
- Rano porównanie: rozpoznanie programu vs. przymiarka; Excel: zapis programu vs. zaznaczenie człowieka (druga osoba nadal odhacza, tylko sprawdza).
- Co tydzień 30 min: przegląd metryk, korekta progów, lista poprawek.

Przejście na tryb pełny (po spełnieniu kryteriów odbiorczych): technik ogląda tylko czerwone, poranek według diod, Excel zapisuje sam z logiem; audyt Excela raz w tygodniu na próbie 20 wierszy przez pierwszy miesiąc.

Co może przesunąć tydzień: brak trybu bez przechyłu w dostarczonym programie (wraca się do gniazd głębszych i testu na ścieżce automatycznej), laptop bez dedykowanej karty graficznej (program producenta nie uruchomi się płynnie), brak dostępu do folderu raportów MillBox (kopia ręczna na czas uruchomienia), opóźniona dostawa druku obudów (ramki działają na stole bez obudowy, poranek według podpisów na ekranie).

## Testy odbiorcze i kryteria „działa”

„Działa” znaczy: liczby z dwóch tygodni trybu cienia przekraczają progi poniżej. Każdą metrykę program liczy sam z własnego logu; raport to jedno polecenie i jedna strona.

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

Największe ryzyka siedzą w trzech miejscach: w mechanice skanera (przechył i pole skanowania), w jakości skanu spieczonych prac i w zachowaniu technika, gdy alarmów jest za dużo. Do tego dochodzą ryzyka budowy ramek: wymiary elektroniki znane dopiero po dostawie i drukarka żywiczna, której pole robocze i żywica nie są jeszcze sprawdzone. Każde ma plan B, który nie wymaga wyrzucenia reszty.

| Ryzyko | Prawdopodobieństwo | Skutek | Jak je zmniejszamy | Plan B |
|---|---|---|---|---|
| Program skanera nie pozwala na ścieżkę bez przechyłu | średnie | prace drgają, fałszywe ubytki | kryterium 1 testu; prośba do Aidite o strategię | gniazda głębsze (50% wysokości pracy) + test na ścieżce automatycznej; w ostateczności DOF Freedom (model nieruchomy) lub 3Shape F8 |
| Pole skanowania mniejsze niż 100 × 100 mm (założenie Z1) | średnie | płytka 96 × 96 nie mieści się w jednym skanie | test na żywicznej płytce pierwszego dnia testu, przed zamówieniem płytek; rozmiar płytki jest jedną liczbą w plikach projektu | mniejsza płytka i mniej gniazd; w ramce wymienia się tylko wkładkę; nowe pliki po pełnej weryfikacji |
| Wymiary elektroniki (panel, stos Pi, gniazda) inne niż domyślne | średnie (wartości domyślne z katalogów) | panel lub gniazdo nie trafia w przygotowane miejsce | obudowa ma zapasy: 8 mm nad stosem Pi, rowki pod słupki na rozstaw 110–130 mm, okno USB z rowkami 23–28 mm, otwór gniazda ø12 z tulejką dla ø8, dystanse w dwóch długościach, podkładki 0,5/1/2 | wiercenie ø4 w dnie w zmierzonym miejscu, obrót panelu, rozwiercenie otworu gniazda, wiercenie flanszy USB — wszystko bez nowego korpusu |
| Drukarka żywiczna w firmie: pole robocze < 100 × 100 mm albo żywica błyszcząca / krucha | średnie | brak taniej płytki testowej i płytek wieczornych z firmy | sprawdzić pole i żywicę przed drukiem; dentystyczna żywica modelowa jest matowa | płytka testowa i wieczorne z drukarni (PA12), ok. 156–279 zł więcej; prototypy pasowań jako tanie próbki w drukarni |
| Drukarnia nie trzyma tolerancji (±0,3 mm na 200 mm) | średnie | płytka ciasna we wkładce, blat nie zatrzaskuje się | luzy 0,3 mm na pasowaniach ruchomych i 0,5 mm na kołnierzu blatu; prototypy pasowań przed zamówieniem; wkładka tania i wymienna | poprawka papierem ściernym; nowa wkładka |
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

Czego nie da się obejść planem B: gwarancji wykrycia każdego ubytku 0,25 mm (fizyka rozdzielczości skanera), zapisu „która kuweta w którym piecu” (świadomie wykluczone), oznaczania prac (zakaz).

## Decyzje otwarte

| Nr | Punkt | Co trzeba zrobić | Kiedy / kto |
|---|---|---|---|
| 1 | Pole skanowania (założenie Z1: 100 × 100 mm) — skanera jeszcze nie ma | pytanie do Aidite lub dystrybutora o zakres skanowania; potwierdzenie na egzemplarzu testowym skanem pustej płytki z żywicy; jeśli pole jest mniejsze, nowy rozmiar płytki (jedna liczba) i pełny przebieg plików, w ramce wymienia się tylko wkładkę | przed zamówieniem płytek, wkładek i pokrywek; korpusów i blatów nie blokuje |
| 2 | Pomiary elektroniki (panel, stos Pi i nakładki, gniazda, odbiornik klawiatury, wkręty) | po dostawie zamówionej elektroniki, suwmiarką, ok. 30 min; wynik decyduje tylko o doborze sprzętu: dystanse 50 czy 45 mm z tulejkami, tulejka gniazda, podkładki, ewentualne wiercenie dna lub flanszy USB | tydzień po zamówieniu elektroniki; nie blokuje żadnego zamówienia |
| 3 | Wysokość ramki 63,6 mm (przekracza pierwotne 55–60 mm o 3,6 mm) | przyjęta przez właściciela razem z konstrukcją odporną na pomiary; nie wraca do dyskusji, chyba że zmierzona elektronika przekroczy zapas (stos Pi z taśmą ponad 31 mm lub złącza panelu z kablami ponad 17 mm) | rozstrzygnięte; kontrola po pomiarach |
| 4 | Drukarka żywiczna w firmie | sprawdzić pole robocze (≥ 100 × 100 mm potrzebne na płytkę) i rodzaj żywicy: matowa, sztywna do płytki testowej i wieczornych; wysokotemperaturowa (HDT ≥ 100 °C) byłaby potrzebna do porannych, inaczej poranne z drukarni | przed drukiem płytki testowej |
| 5 | Płytki wieczorne: drukarnia czy żywica w firmie | po teście skanera i oględzinach żywicznej płytki (mat, sztywność, dokładność stożków) | przy zamówieniu płytek |
| 6 | Wybór drukarni i wariant wykończenia (najtańszy vs pokazowy: barwienie i wygładzanie korpusów) | wyceny z 2–3 drukarni na gotowych plikach | przed zamówieniem obudów |
| 7 | Skaner: tryb bez przechyłu, pole skanowania, eksport | test u nas, kryteria 1–8 | 2 tygodnie testu |

## Koszty i harmonogram

Cały projekt to ok. 22,4–29 tys. zł sprzętu (skaner 20–25 tys. zł plus ramki, płytki, osłona i drobne 2,4–3,9 tys. zł), zero wydatków na oprogramowanie i ok. 11 tygodni od próby do trybu pełnego, z czego 2–4 tygodnie to oczekiwanie na dostawę skanera. Ramki i płytki powstają w tym samym czasie co oprogramowanie, więc nie wydłużają harmonogramu.

Koszty:

| Pozycja | Kwota | Uwagi |
|---|---|---|
| Skaner laboratoryjny (Aidite A-IS Pro 3 lub zamiennik) | 20–25 tys. zł | oferta po teście; DOF i 3Shape na zapytanie |
| Elektronika dwóch ramek: 2 panele LED, 2 Raspberry Pi 4 z nakładkami, zasilacze, pleksi, klawiatura, czujniki, magnesy, wkręty, drobne | 1,2–1,7 tys. zł | lista w sekcji „Lista zakupów”; można zamawiać od razu |
| Druk w drukarni (PA12): 2 korpusy, 2 blaty, 3 wkładki, 6 płytek | 904–1 607 zł (najtańszy) / 1 212–2 155 zł (pokazowy) | 10 plików, 1 004 cm³ z arkusza zamówienia (objętości zmierzone na siatkach); realizacja 1–3 tygodnie; pokrywki, tulejki i podkładki drukowane samemu za koszt materiału; płytki wieczorne z firmowej żywicy oszczędzają dalsze 156–279 zł |
| Osłona, pokrowce, drobne stanowiska | 0,3–0,6 tys. zł | |
| Opcja: kamera 20 Mpx (plan B poranka) | 1,8–2,5 tys. zł | tylko po negatywnym kryterium 5 testu |
| Laptop | 0 zł | daje firma |
| Oprogramowanie, licencje, subskrypcje | 0 zł | własne, biblioteki otwarte, program producenta w zestawie |
| Mój czas | ok. 70–110 h po godzinach do trybu pełnego (6–10 h tygodniowo przez ok. 11 tygodni) + ok. 20–30 h montażu ramek | rozliczany według ustaleń z firmą |

Co firma zyskuje w liczbach (do potwierdzenia metrykami): ponowne frezowanie prac ukruszonych wykrywanych dopiero po piecu spada o co najmniej 60%; rozkładanie dużego pieca krótsze o 15–20 min (2–3 piece dziennie, czyli 40–60 min dziennie wcześniej uwolnionych dla działów czekających na prace); odhaczanie w Excelu z ok. 40–90 min dziennie (10–15 min na piec, 4–6 pieców rano) do zera.

Harmonogram z bramkami (daty orientacyjne; tor skanera przesuwa się 1:1 z dostawą):

| Termin | Krok | Bramka / warunek |
|---|---|---|
| 27 października | Zamówienie elektroniki ramek i drobnych; wycena i zamówienie korpusów (W, P) i 2 blatów w drukarni | pliki ostateczne, zweryfikowane trzykrotnie (obudowa nie zależy od pomiarów ani od skanera) |
| 27 października – 1 listopada | Pytanie do Aidite o zakres skanowania; próba skanerem wewnątrzustnym z firmy; zestaw testowy prac; druk żywicznej płytki testowej i prototypów pasowań | drukarka żywiczna: pole i żywica sprawdzone |
| 2–6 listopada | Dostawa elektroniki → pomiary → dobór dystansów, tulejki, podkładek; druk tulejek i podkładek z żywicy | pomiary w zapasie konstrukcji (inaczej wiercenie lub obrót panelu) |
| 4 listopada | Prezentacja dla firmy — ten dokument; decyzja o teście skanera | decyzja zarządu |
| 9–20 listopada | Test skanera u nas (2 tygodnie); pierwszego dnia skan żywicznej płytki | kryteria 1–8; kryterium 8 → zamówienie płytek, wkładek i pokrywek (ok. 10 listopada, albo wcześniej po pisemnym potwierdzeniu zakresu skanowania) |
| 2 listopada – 11 grudnia | Oprogramowanie stanowiska i ramek (tygodnie 1–4) | co tydzień działająca wersja |
| 16–29 listopada | Dostawa korpusów i blatów; montaż i testy obu ramek; płytki i wkładki z drukarni, magnesy, kalibracja diod | kroki 6–15 montażu zaliczone |
| 23 listopada | Zamówienie skanera | dzień po pozytywnym teście; alternatywy tylko przy wyniku negatywnym |
| 23 listopada – 14 grudnia | Dostawa skanera (2–3 tygodnie) | |
| 14–18 grudnia | Tydzień uruchomienia | kryteria końca dnia 1–5 |
| 21 grudnia – 8 stycznia | Tryb cienia (3 tygodnie kalendarzowe z przerwą świąteczną) | metryki odbiorcze |
| 11 stycznia 2027 | Tryb pełny | kryteria z sekcji „Testy odbiorcze” spełnione |

Kamienie milowe i co je warunkuje:

1. Zamówienie elektroniki oraz korpusów i blatów (27 października) — pliki ostateczne.
2. Prezentacja dla firmy (4 listopada) — ten dokument; decyzja o teście.
3. Potwierdzenie pola skanowania (odpowiedź producenta albo pierwszy dzień testu) → zamówienie płytek, wkładek i pokrywek.
4. Test skanera u nas (2 tygodnie) — egzemplarz od Aidite; wynik w jednej tabeli.
5. Zamówienie skanera — dzień po pozytywnym teście; alternatywy uruchamiane tylko przy wyniku negatywnym.
6. Obie ramki złożone i przetestowane (koniec listopada) — przed dostawą skanera.
7. Tydzień uruchomienia — tydzień po dostawie; oprogramowanie gotowe wcześniej.
8. Tryb pełny — po dwóch tygodniach cienia i spełnieniu kryteriów odbiorczych.

## Załączniki

### A. Specyfikacja płytki z gniazdami

Płytka ma 96 × 96 × 8 mm i musi w całości, ze znacznikami, mieścić się w polu skanowania — założenie 100 × 100 mm do potwierdzenia na egzemplarzu testowym. Razem 6 płytek, każda z własnym numerem: wieczorne 1, 2, 3 (dwie w obiegu, jedna zapasowa) i poranne 4, 5, 6 (dwie na duży piec, jedna zapasowa). Między skanerem przy piecach a ramką w pokoju rozkładania płytki wędrują z pokrywką.

Układ gniazd (rysunki w wersji PDF; współrzędne każdego gniazda są w pliku obok modelu, więc program i ramka czytają je bez zmiany kodu):

- **Płytka wieczorna** (prace zielone, większe o skurcz): 24 gniazda w 4 rzędach od przodu — 13 × ø9 mm (dwa rzędy), 6 × ø12 mm, 5 × ø15 mm — i 2 rynienki 60 × 15 mm w dwóch tylnych rzędach pod mosty do 4 punktów.
- **Płytka poranna** (prace spieczone, 40–70 °C): 35 gniazd w 5 rzędach — 22 × ø7,5 mm (trzy rzędy), 7 × ø10 mm, 6 × ø12,5 mm — i 2 rynienki 50 × 13 mm.

Gniazda: stożkowe, kąt ścianek 15°, głębokość 4 mm (ok. 40% wysokości korony), w dnie otwór przelotowy ø3 mm (rynienki mają 4 otwory); między gniazdami i rzędami ścianki dokładnie 3 mm; strefa gniazd 90 × 90 mm; narożniki 13 × 13 mm wolne od gniazd (tam są znaczniki, kod, magnesy, wycięcie i numer).

Znaczniki i orientacja: trzy stożki ø5 mm, wysokość 3 mm, w trzech narożnikach; czwarty narożnik (przód‑prawy) ma wycięcie 5 × 5 mm, które wymusza to samo ułożenie w skanerze i na kołku ramki. Trzy stożki są jedynym elementem, który program mierzy na płytce: po nich wyrównuje skan do rysunku.

Identyfikacja płytki, trzy sposoby na ten sam numer: cyfra wytłoczona (0,6 mm, 5 mm wysoka) w narożniku z wycięciem dla ludzi; 1–3 dołki ø2 × 1 mm przy lewej krawędzi dla skanera (program czyta je ze skanu); magnesy ø5 × 2 mm wklejone w kieszenie w spodzie trzech narożników dla ramek (3 czujniki Halla: układ obecności magnesów = numer płytki; brak magnesów = brak płytki). Biegun magnesów jednakowy we wszystkich płytkach.

Pokrywka: nakładka 99,6 × 99,6 × 20 mm, jedna na obie płytki; 4 zatrzaski wchodzą w rowek wokół boków płytki 2 mm pod jej wierzchem; 14 mm prześwitu nad płytką (najwyższa praca 14 mm nad dnem gniazda plus 4 mm luzu); wycięcia na palce z przodu i z tyłu; bez otworów i napisów (drukowana z PETG wierzchem do stołu).

Materiał: nylon PA12 z zewnętrznej drukarni (SLS lub MJF), biały, naturalnie matowy — dobry dla skanera, sztywny, znosi temperaturę prac z pieca; przezroczystość nie jest potrzebna, bo gniazda mają otwór w dnie. Płytki wieczorne mogą alternatywnie powstać w firmie z matowej, sztywnej żywicy. Szkło odpada: nie da się w nim zrobić gniazd, odbija światło skanera i tłucze się.

Wersja następna (po teście): głębsze gniazda, jeśli prace drgają; inny rozmiar płytki, jeśli pole skanowania jest mniejsze — obie zmiany to pojedyncze liczby w plikach projektu i pełny, automatyczny przebieg weryfikacji.

### B. Ramka świetlna — wymiary i budowa

Obudowa (obie identyczne): 200 × 200 × 63,6 mm (korpus 59,6 mm + blat 4 mm), nylon PA12 barwiony na grafit, ściany 2,5 mm, dno 3 mm, promienie na krawędziach. Blat z oknem 158 × 158 mm i mleczną pleksi 160 × 160 × 2 mm licowaną z blatem; blat trzyma się na 4 zatrzaskach i 2 wkrętach w tylnej ściance — bez śrub na wierzchu. W środku od dołu: Raspberry Pi 4 z nakładką na 4 słupkach pod środkiem panelu, 8 mm zapasu nad nim, panel LED 160 × 160 mm na 4 mosiężnych dystansach 50 mm (stojących na podkładkach dna, przykręconych od spodu przez rowki na rozstaw 110–130 mm), nad panelem 4 mm odstępu i szybka. Tylna ścianka: kieszeń wgłębiona z oknem 51 × 24 mm i głębokości 22 mm; gniazdo zasilania w jej bocznej ścianie (otwór ø12 mm, dla gniazda ø8 drukowana tulejka ø11,85/8,2 wciskana w otwór), wtyk kątowy (zalecany) lub prosty o korpusie do 37 mm od lica chowa się w kieszeni; gniazdo USB serwisowe z zaślepką (okno 16 × 9 mm z rowkami na rozstaw 23–28 mm). Dno: 2 szczeliny wlotowe 30 × 4 mm, 4 stopki gumowe klejone. Ściany: 10 szczelin wylotowych 12 × 3 mm nisko (4 z tyłu, po 3 z boków). Przód: gładki, tylko napis wytłoczony 8 mm. Karta pamięci dostępna po zdjęciu blatu i panelu.

Wkładka gniazda (biała, na blacie): rama 104,6 × 104,6 × 6 mm; płytka leży na 4 narożnych półkach 2,5 mm nad szybką (żaden otwór gniazda nie jest zasłonięty, bo narożniki płytki nie mają gniazd); pod trzema narożnikami czujniki Halla 1,7 mm od magnesów płytki; na czwartej półce kołek 4,4 × 4,4 mm wchodzący w wycięcie płytki; z przodu wycięcie palcowe do podniesienia płytki bez dotykania prac i dwie wytłoczone strzałki wskazujące przód; 2 tylne uszy z kołkami i magnesami trzymają wkładkę na blacie. Rama zabiera 4 mm (1,6 piksela) z każdego boku matrycy; wolny pas 27,7 mm = 11 pikseli na cyfry; pas przedni i prawy całkiem odsłonięte.

Elektronika (na ramkę): panel HUB75 64 × 64 P2.5, Raspberry Pi 4 B 2 GB z radiatorem, Adafruit RGB Matrix Bonnet, zasilacz 5 V 4 A (typowy pobór ramki < 1,5 A), karta 32 GB z systemem w trybie tylko do odczytu (nagłe wyłączenie prądu nie psuje karty), 3 czujniki Halla A3144 na małej płytce prototypowej przyklejonej taśmą VHB do ściany, kable na podstawkach opasek samoprzylepnych, w ramce porannej odbiornik USB klawiatury numerycznej 2,4 GHz. Czujniki używają trzech wolnych pinów Raspberry Pi; nakładka zajmuje resztę. Łączność: firmowe Wi‑Fi 2,4 GHz; zapas: hotspot laptopa.

### C. Schemat stanowiska na parapecie

stanowisko na parapecie · widok z góry (schemat w wersji PDF)

Parapet ma 200 × 45 cm; stanowisko zajmuje lewe 100 cm (skaner 38 × 26 cm, ramka 20 × 20 cm pod osłoną, laptop 36 × 25 cm), prawa połowa zostaje na opaker i kuwety. Skan uruchamia spacja na laptopie; ramka nie ma przycisków, a na podłodze nic nie leży.

Pomieszczenie pieców: długie, wejście krótką ścianą; wzdłuż lewej ściany szafki laboratoryjne, wzdłuż prawej jeden długi stalowy stół z ośmioma piecami do spiekania. Wymiary ok. 10 × 4 m, podział na 3 duże i 5 małych pieców oraz okna z parapetem na przeciwległym końcu to założenia do potwierdzenia na miejscu. Na szafce dużego pieca stoi ok. 30 kuwet jednego wsadu. Przy piecach nie ma miejsca na rozkładanie, więc prace rozkłada się do kuwet w osobnym pomieszczeniu. Tam używa się drugiej ramki (porannej): między porankami leży w szafce, rano stawia się ją na stole i wpina do kabla zasilacza czekającego w klipsie przy krawędzi stołu (gniazdo w kieszeni wgłębionej w tylnej ściance, wtyk kątowy); klawiatura numeryczna leży obok; płytki przenosi się z pokrywkami. Firmowe Wi‑Fi jest dostępne; hotspot laptopa stanowiska zostaje jako zapas.

### D. Checklista dnia (wieczór)

- Laptop włączony, program stanowiska i program skanera uruchomione, Excel otwarty z Autozapisem; ramka przy skanerze świeci kolor gotowości.
- Płytki czyste, znaczniki bez pyłu; szybka ramki przetarta.
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
- **PA12 (SLS/MJF)** — nylon drukowany w zewnętrznej drukarni z proszku; matowy, sztywny, znosi 70 °C.
- **PETG / FDM** — tworzywo i technologia drukarki z filamentu; na pokrywki.
- **Żywica (SLA/DLP)** — druk w firmowej drukarce żywicznej; na płytkę do testu skanera, prototypy pasowań, tulejki i podkładki.
- **Tulejka redukcyjna** — drukowany pierścień (zewnątrz ø11,85 mm, wcisk 0,15 mm; otwór ø8,2 mm) wciskany w otwór ø12 mm gniazda zasilania, gdy kupione gniazdo ma gwint ø8 mm.
- **Podkładki dystansowe** — drukowane krążki 0,5 / 1 / 2 mm pod słupki panelu, wyrównują długość dystansów po pomiarach.
