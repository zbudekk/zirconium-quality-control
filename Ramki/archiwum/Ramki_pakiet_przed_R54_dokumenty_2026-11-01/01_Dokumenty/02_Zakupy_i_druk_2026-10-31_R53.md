# Zakupy i druk — stanowisko kontroli cyrkonii

27 października 2026 · Michał · wersja 1 (towarzyszy planowi wdrożenia v2) · aktualizacja R53 z 31 października 2026 (nowe pliki do druku, specyfikacja zamówienia, kryterium odbioru; zmiany oznaczone „[R53]”)

## Streszczenie: co kupujemy, w jakiej kolejności i dlaczego

Do stanowiska (poza skanerem, który ma własny test i zamówienie opisane w planie wdrożenia) potrzebujemy dwóch ramek świetlnych i sześciu płytek na prace. Składają się na to trzy grupy zakupów:

1. **Elektronika i drobnica** (ok. 1 200–1 680 zł): panele LED, Raspberry Pi z nakładkami, zasilacze, gniazda, czujniki, magnesy, śruby, kable. Nic z tego nie zależy od żadnego testu ani pomiaru — zamawiamy od razu.
2. **Druk w drukarni** (nylon PA12, 904–1 607 zł w wariancie najtańszym, 1 212–2 155 zł w pokazowym): korpusy, blaty, wkładki, płytki. Pliki są ostateczne, zweryfikowane trzykrotnie (generator, recenzent, niezależna kontrola pasowań); [R53] 31 października luzy w plikach poprawiono pod tolerancję druku MJF/SLS (nowe pliki blatu, korpusów W i P oraz wkładki; 11 pozostałych bez zmian) i zweryfikowano ponownie w całości (0 niezgodności) — zamawiać tylko pliki z sumami SHA‑256 ze „Specyfikacji zamówienia”; do drukarni: korpus W, korpus P, blat × 2 — od razu; wkładka × 3, płytki n1–n6 — po potwierdzeniu pola skanowania; pokrywki (druk własny) też po potwierdzeniu pola.
3. **Druk własny** (koszt materiału): pokrywki z PETG u kolegi; tulejki gniazda zasilania, podkładki pod słupki panelu, płytka do testu skanera i prototypy pasowań z żywicy w firmie.

Dlaczego w tej kolejności: obudowa została zaprojektowana tak, by nie zależała od wymiarów kupowanej elektroniki (zapas 8 mm nad Raspberry Pi, rowki pod słupki panelu na rozstaw 110–130 mm, otwór gniazda zasilania ø12 mm z tulejką dla gniazda ø8, okno USB 16 × 9 mm z rowkami na rozstaw 23–28 mm, mocowanie panelu działające z gwintem i bez, komplet podkładek). Dlatego korpus i blat — najdroższe i najdłużej drukowane części — można zamówić, zanim elektronika dotrze. Płytki natomiast muszą w całości, ze znacznikami, mieścić się w polu skanowania skanera (założenie 100 × 100 mm), a skanera jeszcze nie ma — więc płytki, pasująca do nich wkładka i pokrywka czekają na odpowiedź producenta o zakresie skanowania albo na skan płytki na egzemplarzu testowym. Pomiary kupionej elektroniki decydują już tylko o drobnym sprzęcie: długości dystansów, tulejce, podkładkach i ewentualnym wierceniu.

Trzy zależności, które wyznaczają kolejność:

- **pliki → korpus i blat** (pliki są ostateczne, zweryfikowane trzykrotnie, więc korpusy i blaty zamawiamy od razu),
- **pole skanowania → płytki, wkładka, pokrywka** (rozmiar płytki jest jedną liczbą w plikach; jeśli pole okaże się mniejsze, płytki maleją, a w ramce wymienia się tylko wkładkę),
- **pomiary elektroniki → sprzęt mocujący** (dystanse 50 czy 45 mm z tulejkami, tulejka gniazda, podkładki, wiercenie).

## Harmonogram zakupów

| Kiedy | Co | U kogo / gdzie | Warunek | Dlaczego teraz, a nie wcześniej lub później |
|---|---|---|---|---|
| 27 października | Elektronika i drobnica (sekcja 3, grupy A–G) | Botland, Kamami, Allegro, AliExpress (panele) | brak | nic nie zależy od pomiarów; dostawa 2–7 dni, a pomiary tej elektroniki odblokowują drobny sprzęt mocujący |
| 27 października | Dystanse panelu: 8 × 50 mm żeńsko‑żeńskie i 8 × 45 mm żeńsko‑żeńskie (albo tylko jedna długość po sprawdzeniu gwintu panelu) | Botland, Allegro | brak (obie długości) lub pomiar 5a | kupno obu długości kosztuje ok. 30 zł i oszczędza tydzień czekania na pomiar gwintu |
| od razu (31 października; 27 października nie zamówiono — decyzja D‑3) [R53] | Korpus „RAMKA WIECZORNA”, korpus „RAMKA PORANNA”, 2 blaty (PA12 grafit) | drukarnia MJF/SLS (wycena u 2–3) | brak — pliki R53 z 31 października, sumy SHA‑256 w „Specyfikacji zamówienia” | geometria obudowy nie zależy od pomiarów elektroniki ani od skanera; to najdłuższy druk (1–3 tygodnie) i największy koszt, więc idzie pierwszy |
| od razu | Płytka wieczorna nr 1 z matowej żywicy (test skanera), prototyp wkładki z żywicy, pokrywka i próbka zatrzasku z PETG | drukarka żywiczna w firmie, FDM u kolegi | drukarka żywiczna: pole robocze ≥ 100 × 100 mm, żywica matowa | test pasowań za kilka złotych materiału, zanim pójdzie zamówienie do drukarni; płytka testowa czeka gotowa na egzemplarz skanera |
| po potwierdzeniu pola skanowania (odpowiedź Aidite lub dystrybutora o „scanning range”, albo pierwszy dzień testu egzemplarza — ok. 9 listopada) | Płytki poranne nr 4–6, płytki wieczorne nr 1–3 (albo z żywicy w firmie), 3 wkładki (PA12 biały) | drukarnia | pole skanowania mieści 96 × 96 mm ze znacznikami | wszystkie te części mają obrys płytki 96 mm; przy mniejszym polu zmienia się jedna liczba w plikach i wszystko trzeba wydrukować od nowa — stąd czekanie |
| po potwierdzeniu pola skanowania | 4 pokrywki (PETG) | FDM u kolegi | jak wyżej | pokrywka obejmuje płytkę, więc dzieli jej los |
| po pomiarach elektroniki (ok. 2–6 listopada, gdy dotrze) i po odbiorze korpusów [R53] | 2 tulejki gniazda zasilania, podkładki 3 × 8 (żywica) | drukarka żywiczna w firmie | pomiar 16 (gwint gniazda) i zmierzony otwór ø12 w gotowym korpusie [R53], pomiary 4 i 9 (wysokości) | druk w minuty; dopiero pomiar mówi, czy w ogóle są potrzebne |
| po pomiarach elektroniki | Ewentualnie: tulejki F‑F klejone + epoksyd (panel bez gwintu), wiercenie dna lub flanszy USB | Allegro / warsztat | pomiary 5a, 5, 6, 17 | zakup lub czynność tylko przy nietypowym sprzęcie (sekcja 7) |
| przed tygodniem uruchomienia | Osłona z czarnej płyty, pokrowce, hub USB 3.0, kable, listwa, ściereczki | sklep budowlany / Allegro | brak | nie wpływają na montaż ramek; ważne dopiero przy skanerze na parapecie |

## Lista zakupów: elektronika i drobnica (na 2 ramki)

Liczby i ilości z planu budowy ramek v2 (sekcja 5). Ceny orientacyjne z października 2026. Zawsze 2 ramki, chyba że podano inaczej.

### A. Zasilanie

| Element | Parametry do wyszukania w sklepie | Ilość | Cena ok. [zł] | Do czego |
|---|---|---|---|---|
| Zasilacz 5 V 4 A | wtyk DC 5,5/2,1 mm, wtyczka EU; najlepiej z wtykiem kątowym 90° | 2 | 35–50/szt. | zasila panel LED i Raspberry Pi przez nakładkę |
| Wtyk kątowy DC 5,5/2,1 | zalecany kątowy; jeśli zasilacz ma wtyk prosty: przejściówka kątowa 90°; wtyk prosty tylko z korpusem ≤ 37 mm od lica (wtedy mieści się w kieszeni) | 2 | 5–10/szt. | wtyk w kieszeni tylnej ścianki nie wystaje poza obrys ramki |
| Gniazdo DC panelowe 5,5/2,1 | z nakrętką; gwint ø12 mm (pasuje bez niczego) lub ø8 mm (wtedy drukowana tulejka redukcyjna); montaż w ścianie bocznej kieszeni, nakrętka kluczem 14 od wnętrza | 2 | 5/szt. | gniazdo zasilania ramki |
| Wtyk DC 5,5/2,1 ze śrubkami | lutowany/skręcany, do kabla wewnętrznego | 2 | 4/szt. | kabel od gniazda do nakładki; wpiąć w nakładkę przed przykręceniem Pi (po przykręceniu zostaje 7,5 mm do ściany) |
| Przewód 2 × 1 mm² | 1 m (po 25–30 cm na ramkę) | 1 m | 5 | gniazdo → nakładka |

### B. Raspberry Pi, nakładka, panel LED

| Element | Parametry do wyszukania w sklepie | Ilość | Cena ok. [zł] | Do czego |
|---|---|---|---|---|
| Panel LED HUB75 64 × 64, raster P2.5 | 160 × 160 mm, skan 1/32, 5 V, złącze zasilania VH4 + kabel, kabel HUB75 16‑pin w zestawie; np. Waveshare „RGB‑Matrix‑P2.5‑64x64” | 2 | 90–130/szt. | matryca diod pod płytką |
| Raspberry Pi 4 B 2 GB | + radiator aluminiowy 3‑częściowy | 2 | 230–280/szt. | sterownik ramki (Pi 5 nie działa z biblioteką matrycy) |
| Adafruit RGB Matrix Bonnet | ADA 3211; alternatywa RGB Matrix HAT + RTC (ADA 2345) | 2 | 90–130/szt. | nakładka sterująca panelem i zasilająca Pi |
| Karta microSD 32 GB A1 | SanDisk / Samsung EVO | 2 | 25/szt. | system ramki |
| Listwa kątowa goldpin 1 × 10 | raster 2,54 mm | 2 | 2 | wyprowadzenie wolnych pinów z nakładki (czujniki) |
| Klawiatura numeryczna bezprzewodowa 2,4 GHz | z odbiornikiem USB nano; NIE tylko Bluetooth; np. Logitech / Natec / Genesis | 1 | 60–120 | obsługa ramki porannej (Enter, cyfry, Backspace, „zamknij piec”) |
| Przedłużacz USB 20 cm (opcja) | USB‑A męski–żeński | 1 | 8 | gdyby odbiornik klawiatury słabo odbierał przez obudowę |

### C. Czujniki Halla i magnesy

| Element | Parametry do wyszukania w sklepie | Ilość | Cena ok. [zł] | Do czego |
|---|---|---|---|---|
| Czujniki Halla A3144 | obudowa TO‑92, cyfrowe, otwarty kolektor; alternatywnie SS451A lub DRV5032 (omnipolarne, 3,3 V) | 10 (6 + zapas) | 1–3/szt. | 3 na ramkę, czytają numer płytki z magnesów |
| Rezystory 10 kΩ 1/4 W | przewlekane | 10 | 1 | podciąganie wyjść czujników do 3,3 V |
| Magnesy neodymowe ø5 × 2 mm N35 | paczka 30 szt. | 30 | 15 | 9 w płytkach (kod numeru) + 4 we wkładkach + 4 w blatach = 17 |
| Płytka prototypowa 30 × 20 mm | pady, raster 2,54 | 2 | 4 | czujniki + rezystory; klejona taśmą VHB do ściany korpusu |
| Złącza JST‑XH 2,54: 5‑pin i 3‑pin + przewody Dupont F‑F 20 cm | komplet | komplet | 20 | odpinane połączenie wkładka → płytka prototypowa → nakładka |
| Przewód silikonowy AWG 28, 3 kolory | po 5 m z koloru (po 50 cm × 3 na czujnik) | 3 × 5 m | 20 | przewody czujników w rowkach wkładki |

### D. Gniazda i kable

| Element | Parametry do wyszukania w sklepie | Ilość | Cena ok. [zł] | Do czego |
|---|---|---|---|---|
| Gniazdo USB‑A panelowe z zaślepką | USB 3.0 lub 2.0 panel‑mount; flansza 2 × M3 z otworami **poziomo** w rozstawie 23–28 mm (rozstaw 22 → spiłować koniec rowka 0,5 mm; typ „D” z otworami pionowymi → wiercenie 2 × ø3,2); kabel 30 cm do USB‑A męskiego | 2 | 15–25/szt. | USB serwisowe w tylnej ściance; wkręcić przed montażem panelu (od wnętrza 14,3 mm do dystansu) |
| Opaski kablowe 2,5 × 100 mm, rzep 20 mm | komplet | komplet | 10 | wiązki |
| Podstawki opasek samoprzylepne 20 × 20 mm + taśma 3M VHB 10 mm | 6 podstawek + 1 m taśmy | 6 + 1 m | 15 | zamiast drukowanych uchwytów kabli: wiązki zasilania i czujników na dnie, płytka prototypowa na ścianie (powierzchnie przemyć alkoholem) |

### E. Śruby, wkręty, dystanse

| Element | Parametry do wyszukania w sklepie | Ilość | Cena ok. [zł] | Do czego |
|---|---|---|---|---|
| Dystanse mosiężne M3 żeńsko‑żeńskie 50 mm | sześciokątne, gwint M3 z obu stron | 8 | 30 | słupki panelu, gdy panel ma gwintowane otwory (3 mm dno + 1 mm podkładka + 50 = spód panelu na 54 mm) |
| Dystanse mosiężne M3 żeńsko‑żeńskie 45 mm | jak wyżej | 8 | 30 | słupki panelu, gdy panel NIE ma gwintu (45 + tulejka 5 mm); kupić od razu albo po sprawdzeniu gwintu |
| Wkręty dociskowe M3 × 5 (bez łba, imbus) | stal, gniazdo imbusowe | 10 | 6 | sprzęgają dystans z gwintem panelu lub tulejki; nic nie wystaje od strony diod |
| Tulejki mosiężne F‑F M3 ø5 × 5 mm | gwint wewnętrzny M3 | 8 | 10 | tylko gdy panel bez gwintu: klejone epoksydem do spodu panelu współosiowo z otworem |
| Epoksyd 2‑składnikowy 5 min | dowolny | 1 | 12 | klejenie tulejek |
| Podkładki M3 ø9 mm (DIN 9021, powiększone) | stal | 10 | 3 | pod łby wkrętów panelu w rowkach dna |
| Wkręty M3 × 10 łeb walcowy | stal czarna | 10 | 8 | mocowanie dystansów panelu od spodu przez dno (3 mm) i podkładkę (1 mm) |
| Wkręty M3 × 8 łeb stożkowy | stal czarna | 4 | 4 | 2 wkręty tylne blatu na ramkę |
| Wkręty do tworzyw PT 3,0 × 8 (albo M3 × 8 z ostrym gwintem) | formujące gwint | 10 | 5 | gwint w otworach ø2,5 mm słupków blatu (4 szt. + zapas) |
| Wkręty do tworzyw PT 2,5 × 6 (albo M2,5 × 6) | formujące gwint | 15 | 8 | Raspberry Pi do słupków korpusu (otwory ø2,1 mm) |
| Śruby M2,5 × 6 | zapas do Pi | 10 | 6 | alternatywa dla PT 2,5 |

### F. Pleksi, stopki, kleje

| Element | Parametry do wyszukania w sklepie | Ilość | Cena ok. [zł] | Do czego |
|---|---|---|---|---|
| Pleksi mleczna (opal) 2 mm, 160 × 160 mm | PMMA opal 2 mm, cięcie laserem/CNC na wymiar; rogi ostre (kieszeń blatu ma ostre naroża), bez fazowania | 2 (+1 zapas) | 10–20/szt. | dyfuzor nad panelem, licowany z blatem |
| Stopki gumowe ø10 × 4 mm samoprzylepne | | 12 | 8 | 4 na ramkę, klejone 12 mm od krawędzi na płaskim dnie |
| Klej CA (cyjanoakrylowy) żelowy | | 1 | 10 | magnesy w płytkach, wkładkach i blatach; czujniki w kieszeniach wkładki |

### G. Narzędzia (jeśli brak)

Lutownica do kabli, cyna 0,8, trzecia ręka; multimetr; wkrętaki PH1, PH0, torx T10, imbus do wkrętów dociskowych; klucz płaski 14 (nakrętka gniazda); szczypce boczne; pęseta; papier ścierny 400; wiertła ø3,2, ø3,4, ø4 (tylko poprawki); pilnik igłowy; marker; kompas lub magnes wzorcowy (bieguny); suwmiarka; laptop z czytnikiem kart SD; alkohol do odtłuszczania.

Razem elektronika i drobnica (grupy A–F): ok. 1 200–1 680 zł.

Nie kupujemy: przycisku, czujnika gestu, wkładek gwintowanych ani grotu do ich wtapiania, podstawki klawiatury, ramy dyfuzora, uchwytów kabli, pianek ani uszczelek.

## Druk w drukarni (PA12, MJF lub SLS)

### Części do zamówienia

Pliki i ilości z planu budowy v2 (sekcja 12.1 i plik parametrów); objętości zmierzone na siatkach STL i ceny z arkusza zamówienia (stawka 0,9–1,6 zł/cm³ z sekcji 11 planu; barwienie × 1,2, wygładzanie × 1,3; drukarnia może doliczyć opłatę za gabaryt).

| Plik STL | Część | Ilość | Materiał / kolor | Objętość [cm³] | Cena ok. [zł] (najtańszy / pokazowy) | Kiedy |
|---|---|---|---|---|---|---|
| ramka_korpus_W_v2.stl [R53] | Korpus z napisem „RAMKA WIECZORNA” | 1 | PA12 grafit | 233,5 | 210–374 / 328–583 | od razu |
| ramka_korpus_P_v2.stl [R53] | Korpus z napisem „RAMKA PORANNA” | 1 | PA12 grafit | 233,5 | 210–374 / 328–583 | od razu |
| ramka_blat_v2.stl [R53] | Blat z oknem i kieszenią dyfuzora | 2 | PA12 grafit | 72,5 | 131–232 / 204–362 | od razu |
| ramka_wkladka_v2.stl [R53] | Wkładka gniazda płytki | 3 (2 + zapas) | PA12 naturalny biały | 12,4 | 34–60 | po potwierdzeniu pola skanowania |
| ramka_plytka_poranna_n4_v2.stl, _n5_, _n6_ | Płytki poranne nr 4, 5, 6 | 3 (po 1 z każdym numerem) | PA12 naturalny biały, wierzch bez wygładzania | 60,2 | 162–288 | po potwierdzeniu pola skanowania |
| ramka_plytka_wieczorna_n1_v2.stl, _n2_, _n3_ | Płytki wieczorne nr 1, 2, 3 | 3 (po 1 z każdym numerem) | PA12 naturalny biały (alternatywa: matowa żywica w firmie) | 58,0 | 156–279 | po potwierdzeniu pola skanowania |
| **Razem** | 10 plików | 13 szt. | | 1 004 | **904–1 607 / 1 212–2 155** | |

Wariant najtańszy: wszystko w PA12 naturalnym (korpusy i blaty szare, bez barwienia i wygładzania). Wariant pokazowy: korpusy i blaty barwione na grafit i wygładzane parowo (+15–25 % za barwienie, +25–40 % za wygładzanie); wkładki i płytki zawsze bez wygładzania. Największy koszt to korpusy (ok. 45 %); jeśli wycena przekroczy budżet, korpus można zamówić w SLS zamiast MJF (często taniej dla dużych brył).

### Specyfikacja zamówienia [R53, 31 października 2026]

Zamawiać wyłącznie pliki o poniższych sumach SHA‑256 (folder `wyniki_v2/stl/` z 31 października; w pakiecie `Ramki_pakiet_2026-10-31_R53`). Pliki blatu, korpusów W i P oraz wkładki są nowe (poprawki luzów R53, pełna ponowna weryfikacja: generator, kopie recenzenta, niezależna kontrola pasowań, pomiar z siatek 118/118 — 0 niezgodności); 11 pozostałych jest bajtowo identycznych z plikami z 27 października. Jeśli drukarnia ma starsze pliki (z 27 października), należy je zastąpić — sumy się różnią.

| Plik STL | Szt. | Materiał / technologia | Kiedy | SHA‑256 | Status |
|---|---|---|---|---|---|
| ramka_korpus_W_v2.stl | 1 | PA12 grafit (MJF/SLS) | od razu | `bd55871c88cf2604c1c8efa5035148ba39c3803a0788015cc35548e8e9afff9a` | nowy plik R53 |
| ramka_korpus_P_v2.stl | 1 | PA12 grafit (MJF/SLS) | od razu | `aadb91c9364cf39f1f4062d328616aa518e474b957315ed4a941de4f935ab2b7` | nowy plik R53 |
| ramka_blat_v2.stl | 2 | PA12 grafit (MJF/SLS) | od razu | `8c48856eb9addee2b37cfa5a03e5686ab7670bd92b724e488ccc8d8dd3a4b418` | nowy plik R53 |
| ramka_wkladka_v2.stl | 3 (2 + zapas) | PA12 naturalny biały (MJF/SLS) | po potwierdzeniu pola skanowania | `f4196fbc640450998634f50caa86051f89df2cbb2c218e317f5c2b193e3ef92b` | nowy plik R53 |
| ramka_plytka_wieczorna_n1_v2.stl | 1 | PA12 naturalny biały, mat (MJF/SLS) | po potwierdzeniu pola skanowania | `b2803c829885795b7a06e9d2597a1de6080bdec459e426238d8cd9c05a6e8b52` | bez zmian od 27.10 |
| ramka_plytka_wieczorna_n2_v2.stl | 1 | PA12 naturalny biały, mat (MJF/SLS) | po potwierdzeniu pola skanowania | `8bab264ca661b8d95f8d5f99a76a63956b6722f8d330d60b52bc1f0d4585b82e` | bez zmian od 27.10 |
| ramka_plytka_wieczorna_n3_v2.stl | 1 | PA12 naturalny biały, mat (MJF/SLS) | po potwierdzeniu pola skanowania | `d3a44e8d7122d167e068d885db53ad485c441dc85b747764bd185bd2d53183cf` | bez zmian od 27.10 |
| ramka_plytka_poranna_n4_v2.stl | 1 | PA12 naturalny biały, mat (MJF/SLS) | po potwierdzeniu pola skanowania | `3186d1ab86f2442302edf057d8bbbc227bbf7f691d4620304f79b377e6773089` | bez zmian od 27.10 |
| ramka_plytka_poranna_n5_v2.stl | 1 | PA12 naturalny biały, mat (MJF/SLS) | po potwierdzeniu pola skanowania | `70bd4dd499506e38c9973bd50fb66e133d9a2ff34b71cf2494df8d7727866cbb` | bez zmian od 27.10 |
| ramka_plytka_poranna_n6_v2.stl | 1 | PA12 naturalny biały, mat (MJF/SLS) | po potwierdzeniu pola skanowania | `562d23f69b9bb3f4b015df6e2afdee2ee6aaddc39dfe08370aa418e3d5edcefb` | bez zmian od 27.10 |
| ramka_pokrywka_v2.stl | 4 | PETG, FDM u kolegi | po potwierdzeniu pola skanowania | `ad23444483ac95733e92169af00e5271d8fc3b19a91854e8c8acddf06c8cd454` | bez zmian od 27.10 |
| ramka_tulejka_dc_v2.stl | 2 | żywica w firmie (albo PETG) | po pomiarze 16 i po zmierzeniu otworu ø12 w gotowym korpusie | `b393256cd8cafdac6d125d6f9f25647c5f94840d1bc5eb87941b436f510bcc00` | bez zmian od 27.10 |
| ramka_podkladka_panelu_05_v2.stl | 8 | żywica w firmie (albo PETG) | po pomiarach 4 i 9 | `4260d1f1957f32d101cae5da2cf4634e24239caf738592edd7007fc0728ec6b4` | bez zmian od 27.10 |
| ramka_podkladka_panelu_1_v2.stl | 8 | żywica w firmie (albo PETG) | po pomiarach 4 i 9 | `e79a805121499f8d65b7d23ef6d2ae255549b4f55579ded7061b8996b91c9b78` | bez zmian od 27.10 |
| ramka_podkladka_panelu_2_v2.stl | 8 | żywica w firmie (albo PETG) | po pomiarach 4 i 9 | `9c47aea4fbc946c16dab3813561d936745b88afde6092542de1d67a21656d5b5` | bez zmian od 27.10 |

Do zamówienia dołączyć: ten dokument (sekcja „Czego wymagać od drukarni”), arkusz zamówienia z pakietu (`arkusz_zamowienia.csv`) i wymaganie pomiaru przy odbiorze: **odchyłka większa niż ±0,5 mm od wymiaru nominalnego = reklamacja** (W‑04; wcześniej ±0,3 — luzy w plikach R53 przenoszą ±0,5).

### Czego wymagać od drukarni

- **Materiał:** PA12 (nylon) MJF lub SLS; dla płytek kolor naturalny biały, matowy (skaner nie lubi połysku); dla korpusów i blatów naturalny lub barwiony na grafit.
- **Tolerancja [R53]:** ±0,3 mm (standard MJF/SLS: ±0,3 % z dolnym limitem ±0,3 mm). Luzy w plikach są policzone na ±0,3 mm na **każdej z dwóch współpracujących części**: 0,4 mm na stronę płytka we wkładce (otwór 96,8), 0,7 mm kołnierz blatu (193,6 w 195), 0,75 mm zatrzaski w pionie i 1,5 mm na boki, otwory wkrętów blatu ø3,6, otwór kołka wkładki ø3,4, rowki pod słupki panelu 3,6. **Kryterium odbioru: odchyłka większa niż ±0,5 mm od nominału = reklamacja** (do ±0,5 pliki to przenoszą).
- **Płaskość [R53]:** blaty, wkładki i płytki drukować płasko w XY, chłodzenie w złożu bez przyspieszania; wypaczenie większe niż 0,5 mm na 200 mm = reklamacja.
- **Otwory ø2,1 i ø2,5 pod wkręty formujące [R53]:** zostawić jak w plikach (drukarnia nie powiększa ani nie „naprawia”); u nas przed pierwszym wkręceniem każdy jest przewiercany wiertłem ø2,1 / ø2,5 (proszek i zarośnięcie otworu z druku).
- **Minimalna ścianka 1,5 mm** — pliki jej nie schodzą poniżej; usługodawca nie może „pogrubiać” ani „naprawiać” siatek bez pytania.
- **Wygładzanie parowe** (wariant pokazowy): tylko powierzchnie zewnętrzne korpusów i blatów; **nie** wygładzać kołnierza blatu, haczyków zatrzaskowych ani kieszeni zatrzasków w korpusie (zmienia wymiar pasowania) — jeśli drukarnia nie może tego wyłączyć miejscowo, zamówić bez wygładzania.
- **Barwienie** nie zmienia wymiarów; dopuszczalne na korpusach i blatach.
- **Wypłukanie proszku** z kieszeni, rowków i otworów (kieszeń gniazda zasilania, rowki w dnie, kanały przewodów we wkładce, otwory ø3 w dnach gniazd płytek).
- **Gabaryt:** korpus 200 × 200 × 59,6 mm, blat 200 × 200 × 14 mm — potwierdzić, że mieści się w komorze i czy jest dopłata za gabaryt.
- **Orientacja:** korpus dnem w dół, blat wierzchem w dół, wkładka spodem w dół, płytki gniazdami do góry — zgodnie z plikami (największa płaska ściana leży na Z = 0).
- **Osobno wyceniać:** pozycje „od razu” (korpusy, blaty) i „po potwierdzeniu pola” (wkładki, płytki), żeby drugie zamówienie nie wstrzymało pierwszego.

Do wyceny wysyłamy pliki STL i arkusz zamówienia (objętości, ilości, materiał per część). Przy zamówieniu CNC z PMMA (tylko gdy drukarnia nie ma PA12 dla płytek) potrzebny jest plik STEP — konwersja przez FreeCAD.

## Druk własny: FDM z PETG (u kolegi)

Części: **pokrywka × 4** (plik ramka_pokrywka_v2.stl, 99,6 × 99,6 × 20 mm, ok. 30 cm³ każda). Zapasowo PETG nadaje się też na tulejkę i podkładki (sekcja 6), jeśli drukarka żywiczna będzie niedostępna; na próbkę zatrzasku blatu do testu pasowań, jeśli zostanie wyeksportowana.

Dlaczego PETG, nie PLA ani żywica: pokrywka ma 4 zatrzaski o występie 0,7 mm, które muszą się sprężynować — PETG jest ciągliwy, standardowa żywica krucha. Pokrywka bywa kładziona na płytkę z pracami prosto z pieca (40–70 °C): PETG trzyma kształt, PLA mięknie już około 55–60 °C i pełza pod obciążeniem. PETG ma też mały skurcz, więc wnęka 96,6 mm trafia w luz 0,3 mm wokół płytki.

Zalecenie ogólne: ustawienia poniżej to punkt startowy, do dopasowania do konkretnej drukarki i filamentu (w planie budowy ramek są tylko: materiał PETG, warstwa 0,2 mm i orientacja).

| Parametr | Wartość startowa | Uwagi |
|---|---|---|
| Dysza | 0,4 mm | |
| Warstwa | 0,2 mm (pierwsza 0,2–0,25) | |
| Temperatura dyszy / stołu | 230–245 °C / 80 °C | według producenta filamentu; za gorąco = nitkowanie |
| Prędkość | ≤ 60 mm/s, obrysy zewnętrzne 30–40 mm/s | zatrzaski i kołnierz 1,5 mm wymagają spokojnego druku |
| Obrysy | 4 | kołnierz 1,5 mm = pełne obrysy, bez wypełnienia |
| Warstwy góra / dół | 5 / 5 | wierzch pokrywki 2 mm = ok. 10 warstw pełnych |
| Wypełnienie | 30–40 % gyroid | |
| Chłodzenie | 30–50 % | PETG nie lubi pełnego chłodzenia (słaba spójność warstw) |
| Podpory | bez | przy orientacji poniżej nie są potrzebne |
| Orientacja pokrywki | wierzchem do stołu, kołnierzem w górę | największa płaska ściana na stole; zatrzaski i wycięcia na palce drukują się bez podpór; otwarta wnęka u góry |
| Kompensacja otworów / wnęk | +0,1–0,2 mm w poziomie | PETG lekko zawęża wnęki; wnęka 96,6 mm ma luz 0,3 mm na stronę do płytki 96 mm — sprawdzić na pierwszej sztuce suwmiarką |
| Pierwsza warstwa | skontrolować przyczepność (szkło/PEI, ewentualnie klej w sztyfcie) | kołnierz 99,6 mm — brzegi nie mogą się unosić |
| Filament | suszony (PETG chłonie wilgoć) | mokry PETG = pęcherze i słabe zatrzaski |

Po wydruku: sprawdzić, czy pokrywka wchodzi na płytkę (albo na prototyp żywiczny) bez siły i trzyma po odwróceniu; garby zatrzasków 0,7 mm w rowek 0,8 mm — jeśli za ciasno, przeszlifować garby papierem 400, jeśli za luźno, zwiększyć kompensację i wydrukować ponownie (pokrywka to ok. 15 zł filamentu).

## Druk własny: żywica (drukarka firmowa)

Części:

| Część | Plik | Ilość | Kiedy |
|---|---|---|---|
| Tulejka redukcyjna gniazda zasilania (ø11,85 zewn. — celowo wciskowa, 0,075 mm na stronę w otworze ø12; ø8,2 wewn.; 2 mm; kołnierz ø15 × 1) | ramka_tulejka_dc_v2.stl | 2 | po pomiarze 16 (tylko gdy gniazdo ma gwint ø8) **i po zmierzeniu otworu ø12 w gotowym korpusie** [R53]: otwór z druku może wyjść 11,7–11,9 mm; przed drukiem wpisać do `dc_bush_outer_d` w `parametry.json` wartość = zmierzony otwór − 0,15 i przebudować tulejkę generatorem (etap C) |
| Podkładki pod dystanse panelu ø9, otwór 3,4, grubość 0,5 / 1 / 2 mm | ramka_podkladka_panelu_05_v2.stl, _1_, _2_ | po 8 (24) | po pomiarach 4 i 9 (albo od razu, to minuty druku) |
| Płytka wieczorna nr 1 — test skanera | ramka_plytka_wieczorna_n1_v2.stl | 1 | od razu; czeka na egzemplarz testowy skanera |
| Prototypy pasowań: wkładka (+ ewentualnie płytka nr 1 jak wyżej) | ramka_wkladka_v2.stl | 1 | od razu, przed zamówieniem wkładek w drukarni |

Rodzaj żywicy: standardowa lub „tough” (bardziej ciągliwa) do tulejki, podkładek i prototypu wkładki. Do płytki testowej **żywica matowa** (dentystyczna żywica modelowa jest matowa) — skaner nie lubi połysku; jeśli dostępna jest tylko błyszcząca, zmatowić sprayem skanerskim (to płytka testowa, nie praca — spray na płytce jest dozwolony). Żywica standardowa odkształca się w temperaturze prac z pieca, dlatego płytki poranne zawsze z PA12.

Zalecenie ogólne (ustawienia drukarki żywicznej — punkt startowy, naświetlanie według karty żywicy i drukarki):

| Parametr | Wartość startowa | Uwagi |
|---|---|---|
| Warstwa | 0,05 mm | stożki gniazd i dołki kodu ø2 mm wymagają drobnej warstwy |
| Naświetlanie | według producenta żywicy dla danej drukarki | za długie = zarastanie otworów ø3 w dnach gniazd i ø3,4 w podkładkach |
| Orientacja płytki | gniazdami do góry, przechył 10–15°, podpory tylko od spodu | podpory nie mogą dotykać gniazd ani stożków znaczników; dno płytki po oderwaniu podpór zeszlifować na płasko |
| Orientacja tulejki | kołnierzem do stołu (albo na lekkich podporach), bez podpór w otworze | otwór ø8,2 nie może mieć śladów podpór |
| Orientacja podkładek | płasko na stole | 24 sztuki w jednym wydruku |
| Orientacja wkładki (prototyp) | spodem w dół, lekki przechył, podpory pod uszami | kołek orientacyjny i półki do góry |
| Mycie | IPA, 2 kąpiele, przedmuchać otwory | żywica w otworach ø3 zarasta je po utwardzeniu |
| Utwardzanie | UV według producenta, obie strony | niedotwardzona żywica jest lepka i miękka |
| Skurcz | ok. 0,2–0,5 % | na 96 mm to 0,2–0,5 mm: płytka może wyjść 95,5–95,8 mm — dla testu skanera bez znaczenia, dla pasowania we wkładce daje większy luz; otwory zawężają się — w razie potrzeby rozwiercić ø3 i ø3,4 |
| Kompensacja | otwory +0,1 mm w ustawieniach slicera (jeśli slicer pozwala) | gniazdo ø8 ma wejść w otwór tulejki; otwór po druku żywicznym może wymagać przewiercenia 8,2; zewnętrzną ø11,85 sprawdzić suwmiarką przed wciśnięciem w otwór ø12 |

Uwaga: żywiczna płytka to **test skanera** (pole skanowania, widoczność stożków i dołków kodu, ułożenie prac) i prototyp pasowania — nie część produkcyjna. Płytki wieczorne z żywicy do codziennej pracy tylko wtedy, gdy pole robocze drukarki pozwala, żywica jest matowa i sztywna, a właściciel tak zdecyduje po teście.

## Po pomiarach elektroniki: co dokupić zależnie od wyniku

Pomiary według sekcji 10 planu budowy (suwmiarka, ok. 30 min, gdy elektronika dotrze). Żaden z nich nie zmienia korpusu ani blatu.

| Pomiar | Wynik | Co kupić / zrobić |
|---|---|---|
| 5a — otwory panelu mają gwint M3? | TAK | dystanse 50 mm F‑F + wkręty dociskowe M3 × 5 (nic więcej) |
| | NIE | tulejki F‑F ø5 × 5 klejone epoksydem do spodu panelu + dystanse 45 mm F‑F + wkręty dociskowe |
| 5, 6 — rozstaw i położenie otworów panelu | kwadrat 110–130 mm, przesunięcie ≤ 0,5 mm | nic — dystanse trafiają w rowki dna |
| | inny wzór | wywiercić ø4 w dnie w zmierzonym miejscu, podkładka drukowana pod dystans |
| 4 + 9 — elementy pod panelem i stos Pi z taśmą | razem nie więcej niż 5 mm ponad wartości domyślne (12 i 26) | nic — zapas 8 mm wystarcza |
| | więcej | obrócić panel tak, by złącza leżały nad kolumną słupków; awaryjnie skrócić słupki Pi pilnikiem |
| 3 — wysokość diod nad płytką panelu | 1–3 mm | nic — luz do szybki 5–3 mm |
| 16 — gwint gniazda zasilania | ø12 | nic |
| | ø8 | najpierw zmierzyć otwór ø12 w ścianie kieszeni gotowego korpusu [R53]; wydrukować tulejkę redukcyjną × 2 (ø zewnętrzna = zmierzony otwór − 0,15, nominalnie 11,85; ø8,2 wewn.; otwór w razie potrzeby przewiercić 8,2, zewnętrzną sprawdzić suwmiarką przed wciśnięciem) |
| | większy niż 12 | rozwiercić otwór w ścianie kieszeni |
| 17 — flansza gniazda USB | otwory poziomo, rozstaw 23–28 mm | nic |
| | rozstaw 22 mm | spiłować koniec rowka 0,5 mm |
| | otwory pionowo (typ D) | wywiercić 2 × ø3,2 w tylnej ściance |
| różnice długości słupków ±0,5–2 mm | po złożeniu | podkładki drukowane 0,5 / 1 / 2 mm pod dystanse |

## Checklista odbioru druku

Każdą część z drukarni zmierzyć suwmiarką przed montażem (tolerancja druku ±0,3 mm na 200 mm). Wartości nominalne z planu budowy v2 po R53. **[R53] Kryterium reklamacji: odchyłka od nominału większa niż ±0,5 mm** (wcześniej ±0,3; luzy w plikach R53 przenoszą ±0,5). Odchyłka do ±0,5 mm: bez działania albo drobna poprawka z kolumny „Gdy nie pasuje”. Przed pomiarem wypłukać i przedmuchać proszek.

| Część | Co zmierzyć | Nominał | Dopuszczalnie | Gdy nie pasuje |
|---|---|---|---|---|
| Korpus | obrys zewnętrzny (mierzyć poza napisem; napis z przodu wystaje 0,6 mm) | 200 × 200 mm | ±0,5 [R53] | odchyłka większa: reklamacja; do ±0,5: bez wpływu |
| Korpus | wysokość | 59,6 mm | ±0,5 [R53] | blat ma luz 0,75 na zatrzaskach w pionie [R53] — do ±0,5 zatrzaski trafiają; większa odchyłka: reklamacja |
| Korpus | wnętrze (między ścianami, mierzyć w połowie wysokości i przy górnej krawędzi — wypaczenie) | 195 × 195 mm | ±0,5 [R53] | kołnierz blatu 193,6 musi wejść z luzem 0,7 na stronę [R53]; większa odchyłka lub wypaczenie do wewnątrz > 0,5: reklamacja; za ciasno mimo to — papier ścierny na kołnierzu blatu |
| Korpus | otwór gniazda zasilania w ścianie kieszeni | ø12 mm | +0,2 / −0 | za mały: rozwiercić ø12 |
| Korpus | okno kieszeni | 51 × 24 mm | ±0,3 | |
| Korpus | rowki w dnie pod słupki | szerokość 3,6 mm [R53] | +0,2 / −0,2 | za wąskie (< 3,3): pilnik |
| Korpus | otwory wkrętów blatu w tylnej ściance [R53] | ø3,6 mm, rozstaw 150 mm (x ±75), oś 55 mm nad dnem | ±0,3 | wkręt M3 ma luz 0,3 na stronę; za mały otwór: wiertło ø3,6; rozstaw poza ±0,5: reklamacja |
| Korpus | kieszenie zatrzasków (4, od wewnątrz) [R53] | 11 × 3,5 mm, głębokość 1,3; dolna krawędź 52,1 mm nad dnem zewnętrznym | ±0,3 | zarośnięte proszkiem: wypłukać; poza ±0,5: reklamacja |
| Korpus i blat | otwory pod wkręty formujące [R53] | ø2,1 (4 × Raspberry Pi), ø2,5 (2 słupki blatu, głębokość 6) | — | zawsze przewiercić wiertłem ø2,1 / ø2,5 przed pierwszym wkręceniem (krok 7 montażu) |
| Blat | obrys | 200 × 200 mm, grubość 4 mm + kołnierz 10 mm (razem 14) | ±0,3 | |
| Blat | kołnierz zewnętrzny | 193,6 × 193,6 mm [R53] | ±0,5 | ponad 194,1: reklamacja albo szlifować kołnierz; poniżej 193,1: blat luźny, ale zatrzaski i wkręty trzymają |
| Blat | kieszeń dyfuzora / okno | 162 × 162 mm, głębokość 2 / 158 × 158 mm | ±0,3 | pleksi 160 nie wchodzi: szlifować pleksi, nie blat |
| Blat | otwory kołków wkładki | ø3,4 mm [R53], rozstaw 116 mm (±58) | ±0,15 | kołki ø3 wkładki, pasowanie ruchome 0,2 na stronę [R53]: za ciasno (< 3,2) — rozwiercić ø3,4 |
| Wkładka | otwór na płytkę | 96,8 × 96,8 mm [R53] | +0,3 / −0,3 | płytka 96 ma mieć luz 0,4 na stronę [R53]; za ciasno (< 96,4) — papier 400 na ścianach otworu; > 97,3: reklamacja |
| Wkładka | rama i obrys [R53] | rama 104,8 × 104,8 × 6 mm; obrys z uszami 130 × 148,4 mm | ±0,5 | płasko (wypaczenie < 0,3 na 148) — inaczej reklamacja |
| Wkładka | kołek orientacyjny | 4,4 × 4,4 mm | ±0,1 | wchodzi w wycięcie płytki 5 × 5 |
| Wkładka | kołki do blatu | ø3 mm, rozstaw 116 mm | ±0,1 | |
| Płytka | obrys | 96,0 × 96,0 mm, grubość 8 mm | ±0,3 [R53] | ponad 96,5: nie wejdzie we wkładkę (luz 0,4 na stronę) — szlifować boki; > ±0,5: reklamacja; wycięcie orientacyjne 5 × 5 |
| Płytka | otwory w dnach gniazd | ø3 mm, przelotowe | | zarośnięte proszkiem: przedmuchać, przebić wiertłem ø3 |
| Płytka | stożki znaczników | ø5, wysokość 3 mm, 3 szt. | | uszkodzone: płytka do wymiany (program wyrównuje po nich skan) |
| Płytka | dołki kodu i kieszenie magnesów | dołki ø2 × 1; kieszenie ø5,2 × 2,2 od spodu | | magnes ø5 × 2 ma wejść z luzem na klej |
| Pokrywka (PETG) | wnęka | 96,6 × 96,6 mm, wysokość 20 mm | +0,3 / −0 | trzyma na płytce po odwróceniu |
| Wszystkie | próba na sucho | płytka we wkładce, wkładka na blacie, pokrywka na płytce, blat na korpusie | | według kroku 6 montażu w planie wdrożenia |

Przy odchyłce poza tolerancją w części z drukarni: najpierw sprawdzić, czy to nie resztki proszku (przedmuchać, wypłukać), potem reklamacja z pomiarem i plikiem — wymiary nominalne są w arkuszu wymiarów dołączonym do plików.

## Decyzje do wiadomości właściciela [R53]

Zapisane w projekcie R53 (`sesje_2026-10-31/poprawki_pasowan/handout.md`), nie wymagają działania — tylko wiedzy przy odbiorze i montażu:

1. **Ściana korpusu za kieszenią zatrzasku 1,2 mm lokalnie** (4 pola 11 × 3,5 mm, nienośne) — odstępstwo od zasady „ścianka ≥ 1,5 mm”, przyjęte świadomie; alternatywa (zahaczenie haczyka 0,4 mm) była za słaba. Przednia ściana ma dodatkowo relief napisu 0,6 mm.
2. **Otwór wkładki 96,8 mm** (zamiast 96,6 z opisu DESIGN B) — zasada sumy tolerancji obu części; obrys płytki, wycięcie, rowek, magnesy i pokrywka bez zmian.
3. **Tulejka gniazda zasilania ø11,85 w otworze ø12 — celowo wciskowa**, drukowana z żywicy dopiero po zmierzeniu otworu w gotowym korpusie. Pokrywka (luz 0,3) bez zmian: PETG z FDM, pierwsza sztuka mierzona i skalowana; rowek płytki ogranicza większy luz.
4. **Dno słupka blatu pod otworem wkrętu 1,6 mm** (było 1,8; wymagane ≥ 1,5), gwint wkrętu M3 × 8 w słupku 4,8 mm (było 5,0).

## Spójność: jedna wersja każdej nazwy i liczby

Poniższe nazwy i wartości są użyte w tym dokumencie, w planie wdrożenia v2 i w planie budowy ramek v2 w tej samej postaci.

| Pozycja | Wartość |
|---|---|
| Ramka: wymiary zewnętrzne | 200 × 200 × 63,6 mm (korpus 59,6 + blat 4) |
| Ramka: ściany / dno | 2,5 mm / 3 mm; wnętrze 195 × 195 mm |
| Zapas nad stosem Raspberry Pi | 8 mm (stos 26 mm bez taśmy, do 31 z taśmą; spód panelu na 54 mm) |
| Dystanse panelu | M3 żeńsko‑żeńskie 50 mm (panel z gwintem) albo 45 mm + tulejka ø5 × 5 (bez gwintu); wkręt dociskowy M3 × 5; wkręt M3 × 10 z podkładką ø9 od spodu |
| Rowki pod słupki panelu | rozstaw 110–130 mm po przekątnych, szerokość 3,6 mm [R53] |
| Gniazdo zasilania | DC 5,5/2,1 w ścianie bocznej kieszeni, otwór ø12 mm; tulejka ø11,85/ø8,2 × 2 z kołnierzem ø15 × 1 (celowo wciskowa, 0,15 mm na średnicy; drukowana po zmierzeniu otworu w gotowym korpusie [R53]) dla gniazda ø8 |
| Kieszeń zasilania | okno 51 × 24 mm, głębokość 22 mm; mieści wtyk kątowy (zalecany) i prosty o korpusie ≤ 37 mm od lica |
| Gniazdo USB | okno 16 × 9 mm, rowki na rozstaw flanszy 23–28 mm |
| Wentylacja | 4 szczeliny z tyłu + 3 na bok (12 × 3 mm), 2 wloty w dnie 30 × 4 mm; bez daszków |
| Blat | 200 × 200 × 4 mm + kołnierz 10 mm (193,6 × 193,6, luz 0,7 na stronę [R53]); okno 158 × 158; kieszeń pleksi 162 × 162 × 2; 4 zatrzaski (haczyk 1,5, kieszeń 11 × 3,5 × 1,3, luz 0,75 w pionie [R53]) + 2 wkręty M3 × 8 z tyłu (otwory ø3,6 [R53]) |
| Pleksi | 160 × 160 × 2 mm, mleczna (opal), rogi bez fazowania |
| Wkładka | rama 104,8 × 104,8 × 6 mm, otwór 96,8 × 96,8 (luz płytki 0,4 na stronę) [R53], 4 półki 2,5 mm, kołek 4,4 × 4,4 × 5, 2 uszy z kołkami ø3 (otwory w blacie ø3,4 [R53]) i magnesami; 3 szt. (2 + zapas) |
| Kryterium odbioru druku [R53] | odchyłka większa niż ±0,5 mm od nominału = reklamacja; otwory ø2,1 / ø2,5 przewiercane przed pierwszym wkręceniem; tulejka drukowana po pomiarze otworu |
| Płytki | 96 × 96 × 8 mm; wieczorna 24 gniazda (13 × ø9, 6 × ø12, 5 × ø15) + 2 rynienki 60 × 15; poranna 35 gniazd (22 × ø7,5, 7 × ø10, 6 × ø12,5) + 2 rynienki 50 × 13; numery 1–3 wieczorne, 4–6 poranne |
| Pokrywka | 99,6 × 99,6 × 20 mm, 4 zatrzaski, bez otworów i napisu; 4 szt., PETG |
| Podkładki panelu | ø9, otwór 3,4, grubości 0,5 / 1 / 2 mm, po 8 szt. |
| Magnesy | ø5 × 2 N35; 17 potrzebnych (9 + 4 + 4), paczka 30 |
| Czujniki Halla | A3144 × 6 (+ zapas), rezystory 10 kΩ do 3,3 V |
| Pliki do druku | 10 do drukarni (2 korpusy, blat, wkładka, 6 płytek) + 5 własne (pokrywka, tulejka, 3 podkładki) = 15 |
| Objętości (z siatek STL, arkusz zamówienia) | korpus 233,7, blat 72,6, wkładka 12,4, płytka wieczorna 58,0, poranna 60,2, pokrywka 30,1 cm³; razem drukarnia 1 004 cm³ |
| Koszt drukarni | 904–1 607 zł (najtańszy) / 1 212–2 155 zł (pokazowy) |
| Koszt elektroniki i drobnicy | 1 200–1 680 zł |
| Tolerancje | druk ±0,3 mm na 200 mm; luzy 0,3 mm (płytka, pokrywka), 0,5 mm (kołnierz blatu), 0,25 mm (zatrzaski) |
| Pole skanowania | założenie ≥ 100 × 100 mm, niepotwierdzone; warunek zamówienia płytek, wkładek i pokrywek |
| Wkręty w nylonie | bez wkładek gwintowanych: PT 3,0 × 8 w otwory ø2,5 (słupki blatu), PT 2,5 × 6 w otwory ø2,1 (Raspberry Pi) |
| Usunięte z projektu | rama dyfuzora, uchwyty kabli, daszki, żebra, szczelina karty pamięci, gniazda stopek, otwory i napis w pokrywce, przycisk, czujnik gestu, podstawka klawiatury, wkładki gwintowane, pianki |
