# Zakupy i druk — stanowisko kontroli cyrkonii

2 listopada 2026 (R57: płytka okrągła) · Autor: Michał Budek

## Streszczenie: co kupujemy i dlaczego

Do stanowiska (poza skanerem, opisanym w planie wdrożenia) potrzebujemy dwóch ramek świetlnych i sześciu płytek na prace; do testu skanera dochodzą dwie płytki okrągłe ø100 (n8 wieczorna, n9 poranna) jako drugi wariant kształtu [R57]. Trzy grupy zakupów:

1. **Elektronika i drobnica** (ok. 1 200–1 680 zł): panele LED, Raspberry Pi z nakładkami, zasilacze, gniazda, czujniki, magnesy, śruby, kable. Nic z tego nie zależy od żadnego pomiaru — zamawiamy od razu.
2. **Druk w drukarni** (nylon PA12, 909–1 616 zł w wariancie najtańszym, 1 217–2 164 zł w pokazowym): korpusy, blaty, wkładki, płytki. Pliki są ostateczne i zweryfikowane (generator, recenzent, niezależna kontrola pasowań z siatek); zamawiać wyłącznie pliki z sumami SHA‑256 ze „Specyfikacji zamówienia”. Korpus W, korpus P i 2 blaty — od razu; płytki okrągłe n8 i n9 (90–159 zł) — od razu [R57]; 3 wkładki i płytki nr 1–6 — po potwierdzeniu pola skanowania. Z płytkami okrągłymi drukarnia kosztuje 998–1 775 zł (najtańszy) / 1 307–2 323 zł (pokazowy).
3. **Druk własny** (koszt filamentu): wszystko z PETG na drukarce FDM u kolegi — pokrywki × 4, tulejki gniazda zasilania × 2, podkładki pod słupki panelu 3 × 8, płytka do testu skanera (nr 1) i prototypy pasowań.

Dlaczego w tej kolejności: obudowa nie zależy od wymiarów kupowanej elektroniki (zapas 8 mm nad Raspberry Pi, rowki pod słupki panelu i flanszę USB, tulejka gniazda zasilania, mocowanie panelu z gwintem i bez, podkładki), więc korpusy i blaty — najdroższe i najdłużej drukowane — zamawiamy, zanim elektronika dotrze. Płytki mają gniazda i znaczniki w kole, które skaner widzi w całym obrocie stolika (założenie: ø100 mm wokół osi; gniazda w kole o promieniu 47 mm), a skanera jeszcze nie ma — więc płytki, wkładka i pokrywka czekają na potwierdzenie pola skanowania: przy polu ø94–100 nowe są tylko pliki płytek, poniżej ø94 płytka byłaby okrągła, z nową wkładką i pokrywką. Pomiary elektroniki decydują już tylko o drobnym sprzęcie mocującym (dystanse 50 czy 45 mm z tulejkami, tulejka gniazda, podkładki, ewentualne wiercenie).

Elementy, z których świadomie zrezygnowano, oraz powody każdej decyzji konstrukcyjnej są w dokumencie „Budowa ramki — decyzje i zamienniki”.

## Kolejność zakupów

| Warunek | Co | U kogo / gdzie | Dlaczego w tej kolejności |
|---|---|---|---|
| od razu — nic nie zależy od pomiarów | Elektronika i drobnica (grupy A–G); dystanse panelu w obu długościach (8 × 50 i 8 × 45 mm) | Botland, Kamami, Allegro, AliExpress (panele) — sekcja „Gdzie zamawiać” | pomiary tej elektroniki odblokowują drobny sprzęt mocujący; obie długości dystansów (ok. 30 zł) zdejmują zależność od pomiaru gwintu panelu |
| od razu — pliki ostateczne, sumy SHA‑256 w „Specyfikacji zamówienia” | Korpus „RAMKA WIECZORNA”, korpus „RAMKA PORANNA”, 2 blaty (PA12 grafit) | drukarnia MJF/SLS: Cadxpert, Spes3D, P3DRC, Send3D, Laboratorium Druku 3D (wycena u 2–3) — sekcja „Gdzie zamawiać” | geometria obudowy nie zależy od pomiarów elektroniki ani od skanera; najdłuższy etap i największy koszt, dlatego pierwszy |
| od razu — drugi wariant do testu skanera [R57]; pliki zweryfikowane i zatwierdzone (recenzja R57‑B, właściciel 2.11), sumy SHA‑256 w „[cytat usuniety]” | Płytki okrągłe n8 (wieczorna) i n9 (poranna), ø100 × 8 mm, PA12 biały mat, bez wygładzania, ±0,3 mm | drukarnia MJF/SLS jak korpusy (to samo zamówienie albo osobna pozycja) — sekcja „[cytat usuniety]” | porównanie kwadrat vs koło na egzemplarzu skanera: ten sam układ gniazd i stożków co płytki 1–6, więc różni je tylko kształt; okrągła nie ma wystających rogów (dołki kodu leżą w polu ø100, na kwadracie poza nim); nie pasuje do wkładki ramki — do użycia na ramce potrzebna przyszła zmiana R58 (wkładka i pokrywka okrągłe) |
| od razu — drukarka FDM z polem ≥ 100 × 100 mm i PETG biały matowy | Płytka wieczorna nr 1 (test skanera), prototyp wkładki, pokrywka i próbka zatrzasku | FDM u kolegi | test pasowań za kilka złotych filamentu przed zamówieniem w drukarni; płytka testowa czeka gotowa na egzemplarz skanera |
| po potwierdzeniu pola skanowania (odpowiedź producenta o „scanning range” albo skan kartonowej makiety 96 × 96 z okręgami ø90/94/100 na egzemplarzu testowym; koło przy obrocie ≥ ø100 mm — kryterium 8 planu) | Płytki wieczorne nr 1–3, poranne nr 4–6, 3 wkładki (PA12 biały); 4 pokrywki (PETG) | drukarnia MJF/SLS — sekcja „Gdzie zamawiać”; pokrywki: FDM u kolegi | wszystkie mają obrys płytki 96 mm i dzielą jej los: przy polu ø94–100 nowe są tylko pliki płytek, poniżej ø94 płytka okrągła z nową wkładką i pokrywką |
| po pomiarach elektroniki i odbiorze korpusów | 2 tulejki gniazda zasilania, podkładki 3 × 8 (PETG); ewentualnie tulejki F‑F klejone + epoksyd, wiercenie dna lub flanszy USB | FDM u kolegi; Allegro / warsztat | tulejka: pomiar 16 i zmierzony otwór ø12 w korpusie; podkładki: pomiary 4 i 9; reszta: pomiary 5a, 5, 6, 17 — dopiero pomiar mówi, czy są potrzebne (sekcja „Po pomiarach elektroniki”) |
| przed uruchomieniem stanowiska | Osłona z czarnej płyty, pokrowce, hub USB 3.0, kable, listwa, ściereczki | sklep budowlany / Allegro | nie wpływają na montaż ramek; potrzebne dopiero przy skanerze na parapecie |

## Gdzie zamawiać

Drukarnie poniżej przyjmują zamówienia od 1 sztuki przez formularz lub kalkulator online (plik STL); korpus 200 × 200 × 59,6 mm mieści się w komorze każdej z nich.

### Drukarnie PA12 (MJF lub SLS) — korpusy, blaty, wkładki, płytki

| Firma | Technologia | Uwagi | Wycena |
|---|---|---|---|
| Cadxpert (Poznań) | MJF i SLS PA12 | od 1 sztuki, bez minimum, wycena tego samego dnia; o barwienie na grafit i wygładzanie parowe dopytać | https://cadxpert.pl/druk-3d-na-zamowienie/ |
| Spes3D (Wrocław) | MJF PA12 | specjalista MJF, komora 380 × 284 × 380 mm, barwienie chemiczne | https://spes3d.pl/druk-3d-mjf-w-tworzywach-sztucznych-poliamid-pa12/ (kalkulator: wycena.spes3d.pl) |
| P3DRC | MJF i SLS PA12 | minimalna wartość zamówienia 210 zł netto (korpus W + korpus P + 2 blaty to przekracza) | https://www.p3drc.pl/zamow-wycene/ |
| Send3D | SLS PA12 (Formlabs Fuse 1+) | kalkulator liczy cenę od razu, płatność BLIK; tylko SLS, bez MJF | https://send3d.eu/en/wycena-online/ |
| Laboratorium Druku 3D (Gliwice) | SLS PA12 | od jednego elementu, wycena mailowa; malowanie RAL jako wykończenie | https://laboratoriumdruku3d.pl/cennik-druku-3d/ |
| Xometry Europe (zapas) | MJF PA12 | wycena natychmiastowa, barwienie na czarno, wysyłka do Polski; strona niezweryfikowana | https://xometry.eu/pl/ |

### Pleksi mleczna 2 mm, 160 × 160 mm, cięcie laserem — dyfuzor

| Firma | Uwagi | Link |
|---|---|---|
| PlasticExpress | konfigurator online, cięcie laser/piła, cena po wpisaniu wymiarów | https://plasticexpress.pl/configurator/20-plexi-mleczna/24-30-przepuszczalnosci/27-2-mm |
| Plexigo | docinanie na zamówienie, ok. 110 zł/m² | https://plexigo.pl/pleksi-mleczne-2-mm/ |
| eplexi24 | od 10 × 10 cm, cięcie laserowe | https://eplexi24.pl/pl/p/Plexi-Pleksi-Plexa-Pleksa-opal-2mm-na-wymiar-plyta-akrylowa-PMMA/171 |
| Plexinet | laser + polerowanie; wymiar i cenę potwierdzić mailem tworzywa@plexinet.pl | https://plexinet.pl/plexi-mleczna |

Pominięta: Allmedia (tylko piła, odchyłka ±1 mm, minimalny bok 30 cm) — nie da ostrych naroży kieszeni blatu.

### Elektronika i drobnica

| Sklep | Co tam kupujemy |
|---|---|
| Botland (botland.com.pl), Kamami (kamami.pl) | Raspberry Pi, nakładka Adafruit, zasilacze, gniazda i wtyki DC, czujniki Halla, rezystory, dystanse, złącza JST, przewody, karta microSD, płytki prototypowe |
| Allegro | magnesy, wkręty, podkładki, gniazdo USB panelowe, opaski i podstawki, taśma VHB, stopki, kleje, klawiatura, hub USB, kable |
| AliExpress | panele LED HUB75 64 × 64 P2.5 (najtaniej; najdłuższa dostawa z całej elektroniki — zamawiać jako pierwsze) |

## Lista zakupów: elektronika i drobnica (na 2 ramki)

Ilości z planu budowy ramek v2 (sekcja 5). Ceny orientacyjne. Zawsze 2 ramki, chyba że podano inaczej.

### A. Zasilanie

| Element | Parametry do wyszukania w sklepie | Ilość | Cena ok. [zł] | Do czego |
|---|---|---|---|---|
| Zasilacz 5 V 4 A | wtyk DC 5,5/2,1 mm, wtyczka EU; najlepiej z wtykiem kątowym 90° | 2 | 35–50/szt. | zasila panel LED i Raspberry Pi przez nakładkę |
| Wtyk kątowy DC 5,5/2,1 | przejściówka kątowa 90°, gdy zasilacz ma wtyk prosty; wtyk prosty tylko z korpusem ≤ 37 mm od lica (mieści się w kieszeni) | 2 | 5–10/szt. | wtyk w kieszeni tylnej ścianki nie wystaje poza obrys ramki |
| Gniazdo DC panelowe 5,5/2,1 | z nakrętką; gwint ø12 mm (pasuje od razu) lub ø8 mm (wtedy drukowana tulejka redukcyjna); nakrętka kluczem 14 od wnętrza kieszeni | 2 | 5/szt. | gniazdo zasilania ramki |
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
| Czujniki Halla A3144 | TO‑92, cyfrowe, otwarty kolektor; alternatywnie SS451A lub DRV5032 (omnipolarne, 3,3 V) | 10 (6 + zapas) | 1–3/szt. | 3 na ramkę, czytają numer płytki z magnesów |
| Rezystory 10 kΩ 1/4 W | przewlekane | 10 | 1 | podciąganie wyjść czujników do 3,3 V |
| Magnesy neodymowe ø5 × 2 mm N35 | paczka 30 szt. | 30 | 15 | 9 w płytkach (kod numeru) + 4 we wkładkach + 4 w blatach = 17 |
| Płytka prototypowa 30 × 20 mm | pady, raster 2,54 | 2 | 4 | czujniki + rezystory; klejona taśmą VHB do ściany korpusu |
| Złącza JST‑XH 2,54: 5‑pin i 3‑pin + przewody Dupont F‑F 20 cm | komplet | komplet | 20 | odpinane połączenie wkładka → płytka prototypowa → nakładka |
| Przewód silikonowy AWG 28, 3 kolory | po 5 m z koloru (po 50 cm × 3 na czujnik) | 3 × 5 m | 20 | przewody czujników w rowkach wkładki |

### D. Gniazda i kable

| Element | Parametry do wyszukania w sklepie | Ilość | Cena ok. [zł] | Do czego |
|---|---|---|---|---|
| Gniazdo USB‑A panelowe z zaślepką | USB 3.0 lub 2.0 panel‑mount; flansza 2 × M3 z otworami **poziomo** w rozstawie 23–28 mm (rozstaw 22 → spiłować koniec rowka 0,5 mm; typ „D” z otworami pionowymi → wiercenie 2 × ø3,2); kabel 30 cm do USB‑A męskiego | 2 | 15–25/szt. | USB serwisowe w tylnej ściance; wkręcić przed montażem panelu |
| Opaski kablowe 2,5 × 100 mm, rzep 20 mm | komplet | komplet | 10 | wiązki |
| Podstawki opasek samoprzylepne 20 × 20 mm + taśma 3M VHB 10 mm | 6 podstawek + 1 m taśmy | 6 + 1 m | 15 | prowadzenie wiązek zasilania i czujników po dnie, płytka prototypowa na ścianie (powierzchnie przemyć alkoholem) |

### E. Śruby, wkręty, dystanse

| Element | Parametry do wyszukania w sklepie | Ilość | Cena ok. [zł] | Do czego |
|---|---|---|---|---|
| Dystanse mosiężne M3 żeńsko‑żeńskie 50 mm | sześciokątne, gwint M3 z obu stron | 8 | 30 | słupki panelu, gdy panel ma gwintowane otwory (3 mm dno + 1 mm podkładka + 50 = spód panelu na 54 mm) |
| Dystanse mosiężne M3 żeńsko‑żeńskie 45 mm | jak wyżej | 8 | 30 | słupki panelu, gdy panel NIE ma gwintu (45 + tulejka 5 mm) |
| Wkręty dociskowe M3 × 5 (bez łba, imbus) | stal, gniazdo imbusowe | 10 | 6 | sprzęgają dystans z gwintem panelu lub tulejki; nic nie wystaje od strony diod |
| Tulejki mosiężne F‑F M3 ø5 × 5 mm | gwint wewnętrzny M3 | 8 | 10 | tylko gdy panel bez gwintu: klejone epoksydem do spodu panelu współosiowo z otworem |
| Epoksyd 2‑składnikowy 5 min | dowolny | 1 | 12 | klejenie tulejek |
| Podkładki M3 ø9 mm (DIN 9021, powiększone) | stal | 10 | 3 | pod łby wkrętów panelu w rowkach dna |
| Wkręty M3 × 10 łeb walcowy | stal czarna | 10 | 8 | mocowanie dystansów panelu od spodu przez dno (3 mm) i podkładkę (1 mm) |
| Wkręty M3 × 8 łeb stożkowy | stal czarna | 4 | 4 | 2 wkręty tylne blatu na ramkę |
| Wkręty do tworzyw PT 3,0 × 8 (albo M3 × 8 z ostrym gwintem) | formujące gwint, wkręcane wprost w PA12 | 10 | 5 | gwint w otworach ø2,5 mm słupków blatu (4 szt. + zapas) |
| Wkręty do tworzyw PT 2,5 × 6 (albo M2,5 × 6) | formujące gwint, wkręcane wprost w PA12 | 15 | 8 | Raspberry Pi do słupków korpusu (otwory ø2,1 mm) |
| Śruby M2,5 × 6 | zapas do Pi | 10 | 6 | alternatywa dla PT 2,5 |

### F. Pleksi, stopki, kleje

| Element | Parametry do wyszukania w sklepie | Ilość | Cena ok. [zł] | Do czego |
|---|---|---|---|---|
| Pleksi mleczna (opal) 2 mm, 160 × 160 mm | PMMA opal 2 mm, cięcie laserem/CNC na wymiar; rogi ostre, bez fazowania (kieszeń blatu ma ostre naroża) — firmy w sekcji „Gdzie zamawiać” | 2 (+1 zapas) | 10–20/szt. | dyfuzor nad panelem, licowany z blatem |
| Stopki gumowe ø10 × 4 mm samoprzylepne | | 12 | 8 | 4 na ramkę, klejone 12 mm od krawędzi na płaskim dnie |
| Klej CA (cyjanoakrylowy) żelowy | | 1 | 10 | magnesy w płytkach, wkładkach i blatach; czujniki w kieszeniach wkładki |

### G. Narzędzia (jeśli brak)

Lutownica do kabli, cyna 0,8, trzecia ręka; multimetr; wkrętaki PH1, PH0, torx T10, imbus do wkrętów dociskowych; klucz płaski 14 (nakrętka gniazda); szczypce boczne; pęseta; papier ścierny 400; wiertła ø2,1, ø2,5, ø3,2, ø3,4, ø4; pilnik igłowy; marker; kompas lub magnes wzorcowy (bieguny); suwmiarka; laptop z czytnikiem kart SD; alkohol do odtłuszczania.

Razem elektronika i drobnica (grupy A–F): ok. 1 200–1 680 zł.

## Druk w drukarni (PA12, MJF lub SLS)

### Części do zamówienia

Objętości zmierzone na siatkach STL, ceny z arkusza zamówienia (stawka 0,9–1,6 zł/cm³; barwienie × 1,2, wygładzanie × 1,3; drukarnia może doliczyć opłatę za gabaryt). Drukarnie: sekcja „Gdzie zamawiać”.

| Plik STL | Część | Ilość | Materiał / kolor | Objętość [cm³] | Cena ok. [zł] (najtańszy / pokazowy) | Warunek |
|---|---|---|---|---|---|---|
| ramka_korpus_W_v2.stl | Korpus z napisem „RAMKA WIECZORNA” | 1 | PA12 grafit | 233,5 | 210–374 / 328–583 | od razu |
| ramka_korpus_P_v2.stl | Korpus z napisem „RAMKA PORANNA” | 1 | PA12 grafit | 233,5 | 210–374 / 328–583 | od razu |
| ramka_blat_v2.stl | Blat z oknem i kieszenią dyfuzora | 2 | PA12 grafit | 72,5 | 131–232 / 204–362 | od razu |
| ramka_wkladka_v2.stl | Wkładka gniazda płytki | 3 (2 + zapas) | PA12 naturalny biały | 12,4 | 34–60 | po potwierdzeniu pola skanowania |
| ramka_plytka_poranna_n4_v2.stl, _n5_, _n6_ | Płytki poranne nr 4, 5, 6 (31 gniazd + 2 rynienki) | 3 (po 1 z każdym numerem) | PA12 naturalny biały, bez wygładzania | 60,9 | 164–292 | po potwierdzeniu pola skanowania |
| ramka_plytka_wieczorna_n1_v2.stl, _n2_, _n3_ | Płytki wieczorne nr 1, 2, 3 (18 gniazd + 2 rynienki) | 3 (po 1 z każdym numerem) | PA12 naturalny biały, bez wygładzania | 59,3 | 160–285 | po potwierdzeniu pola skanowania |
| **Razem** | 10 plików | 13 szt. | | 1 010 | **909–1 616 / 1 217–2 164** | |
| ramka_plytka_okragla_wieczorna_n8_v2.stl [R57] | Płytka okrągła wieczorna nr 8, ø100 (18 gniazd + 2 rynienki, jak nr 1–3) — test skanera | 1 | PA12 naturalny biały, mat, bez wygładzania | 49,0 | 44–78 | od razu |
| ramka_plytka_okragla_poranna_n9_v2.stl [R57] | Płytka okrągła poranna nr 9, ø100 (31 gniazd + 2 rynienki, jak nr 4–6) — test skanera | 1 | PA12 naturalny biały, mat, bez wygładzania | 50,6 | 46–81 | od razu |
| **Razem z płytkami okrągłymi** | 12 plików | 15 szt. | | 1 109 | **998–1 775 / 1 307–2 323** | |

Wariant najtańszy: wszystko w PA12 naturalnym (korpusy i blaty szare). Wariant pokazowy: korpusy i blaty barwione na grafit i wygładzane parowo; wkładki i płytki zawsze bez wygładzania. Korpusy to ok. 45 % kosztu; jeśli wycena przekroczy budżet, korpus można zamówić w SLS zamiast MJF (często taniej dla dużych brył).

### Specyfikacja zamówienia

Zamawiać wyłącznie pliki o poniższych sumach SHA‑256 (folder `wyniki_v2/stl/`, te same pliki w pakiecie `Ramki_pakiet/`). Pliki korpusów, blatu i wkładki mają luzy policzone pod tolerancję druku MJF/SLS; pliki płytek mają gniazda, rynienki i stożki znaczników w kole o promieniu 47 mm; płytki okrągłe n8 i n9 [R57] mają ten sam układ gniazd i stożków co płytki 1–3 i 4–6, obrys ø100 i są tylko do skanera (bez kieszeni magnesów, spód płaski). Jeśli drukarnia ma starsze pliki, należy je zastąpić — sumy się różnią.

| Plik STL | Szt. | Materiał / technologia | Warunek | SHA‑256 |
|---|---|---|---|---|
| ramka_korpus_W_v2.stl | 1 | PA12 grafit (MJF/SLS) | od razu | `bd55871c88cf2604c1c8efa5035148ba39c3803a0788015cc35548e8e9afff9a` |
| ramka_korpus_P_v2.stl | 1 | PA12 grafit (MJF/SLS) | od razu | `aadb91c9364cf39f1f4062d328616aa518e474b957315ed4a941de4f935ab2b7` |
| ramka_blat_v2.stl | 2 | PA12 grafit (MJF/SLS) | od razu | `8c48856eb9addee2b37cfa5a03e5686ab7670bd92b724e488ccc8d8dd3a4b418` |
| ramka_wkladka_v2.stl | 3 (2 + zapas) | PA12 naturalny biały (MJF/SLS) | po potwierdzeniu pola skanowania | `f4196fbc640450998634f50caa86051f89df2cbb2c218e317f5c2b193e3ef92b` |
| ramka_plytka_wieczorna_n1_v2.stl | 1 | PA12 naturalny biały, mat (MJF/SLS) | po potwierdzeniu pola skanowania | `515d32d3dd8a69ae0a94d293a639b201f2d9ce9af19df664ad1b44b59408f775` |
| ramka_plytka_wieczorna_n2_v2.stl | 1 | PA12 naturalny biały, mat (MJF/SLS) | po potwierdzeniu pola skanowania | `360cff9ddd6bbcf8a84b463fed930532612a38118006f1550c2df01b02fa852d` |
| ramka_plytka_wieczorna_n3_v2.stl | 1 | PA12 naturalny biały, mat (MJF/SLS) | po potwierdzeniu pola skanowania | `2fc7040e212ace4a8efda17f61909ca09563009513adcd82ecf5bcaac3e98aaf` |
| ramka_plytka_poranna_n4_v2.stl | 1 | PA12 naturalny biały, mat (MJF/SLS) | po potwierdzeniu pola skanowania | `a8d07cbeb0dafc0e55d3fe2fe516c7d3e854a6259bce587785b796d34b54c65e` |
| ramka_plytka_poranna_n5_v2.stl | 1 | PA12 naturalny biały, mat (MJF/SLS) | po potwierdzeniu pola skanowania | `159503ca4cd66b90a1e2441cae64016901ed83390b48a27345f9484ac1a05830` |
| ramka_plytka_poranna_n6_v2.stl | 1 | PA12 naturalny biały, mat (MJF/SLS) | po potwierdzeniu pola skanowania | `0d5d712d42084a19846f24d385484d01b2254c5c1ec3945d71cfd3493816f15e` |
| ramka_plytka_okragla_wieczorna_n8_v2.stl [R57] — ø100 × 8 (100 × 100 × 8,6 z cyfrą), 49,01 cm³ | 1 | PA12 naturalny biały, mat, bez wygładzania (MJF/SLS) | od razu (test skanera) | `c4c8a18d0b83fd2a2903f5d782188a8de4827ee07c55dca9df7bd0d8e4a37d32` |
| ramka_plytka_okragla_poranna_n9_v2.stl [R57] — ø100 × 8 (100 × 100 × 8,6 z cyfrą), 50,56 cm³ | 1 | PA12 naturalny biały, mat, bez wygładzania (MJF/SLS) | od razu (test skanera) | `a87bc6c5f8f0323bc202e5ebfeab6be6d7c8432beba6aafe4a8372d70666e2be` |
| ramka_pokrywka_v2.stl | 4 | PETG, FDM u kolegi | po potwierdzeniu pola skanowania | `ad23444483ac95733e92169af00e5271d8fc3b19a91854e8c8acddf06c8cd454` |
| ramka_tulejka_dc_v2.stl | 2 | PETG, FDM u kolegi | po pomiarze 16 i po zmierzeniu otworu ø12 w gotowym korpusie | `b393256cd8cafdac6d125d6f9f25647c5f94840d1bc5eb87941b436f510bcc00` |
| ramka_podkladka_panelu_05_v2.stl | 8 | PETG, FDM u kolegi | po pomiarach 4 i 9 | `4260d1f1957f32d101cae5da2cf4634e24239caf738592edd7007fc0728ec6b4` |
| ramka_podkladka_panelu_1_v2.stl | 8 | PETG, FDM u kolegi | po pomiarach 4 i 9 | `e79a805121499f8d65b7d23ef6d2ae255549b4f55579ded7061b8996b91c9b78` |
| ramka_podkladka_panelu_2_v2.stl | 8 | PETG, FDM u kolegi | po pomiarach 4 i 9 | `9c47aea4fbc946c16dab3813561d936745b88afde6092542de1d67a21656d5b5` |

Do zamówienia dołączyć: ten dokument (sekcja „Czego wymagać od drukarni”), arkusz zamówienia z pakietu (`arkusz_zamowienia.csv`) i wymaganie pomiaru przy odbiorze: **odchyłka większa niż ±0,5 mm od wymiaru nominalnego = reklamacja**.

### Czego wymagać od drukarni

Przy zapytaniu o wycenę podać: pliki STL z pakietu (sumy SHA‑256 ze „Specyfikacji zamówienia”), arkusz zamówienia (objętości, ilości, materiał per część), tolerancję ±0,3 mm, bez wygładzania kołnierza blatu i zatrzasków, PA12 biały mat dla płytek i wkładek, PA12 grafit (barwiony) dla korpusów i blatów. Pozycje „od razu” (korpusy, blaty) i „po potwierdzeniu pola” (wkładki, płytki) wyceniać osobno, żeby drugie zamówienie nie wstrzymało pierwszego.

- **Materiał:** PA12 (nylon) MJF lub SLS; płytki naturalny biały, matowy (skaner nie lubi połysku); korpusy i blaty naturalny lub barwiony na grafit.
- **Tolerancja:** ±0,3 mm (standard MJF/SLS). Luzy w plikach są policzone na ±0,3 mm na **każdej z dwóch współpracujących części** (0,4 mm na stronę płytka we wkładce, 0,7 mm kołnierz blatu, 0,75 mm zatrzaski w pionie; nominały w checkliście odbioru). **Kryterium odbioru: odchyłka większa niż ±0,5 mm od nominału = reklamacja.**
- **Płaskość:** blaty, wkładki i płytki drukować płasko w XY, chłodzenie w złożu bez przyspieszania; wypaczenie > 0,5 mm na 200 mm = reklamacja.
- **Otwory ø2,1 i ø2,5 pod wkręty formujące:** zostawić jak w plikach; u nas przed pierwszym wkręceniem każdy jest przewiercany wiertłem ø2,1 / ø2,5.
- **Minimalna ścianka 1,5 mm** — pliki jej nie schodzą poniżej; usługodawca nie „pogrubia” ani nie „naprawia” siatek bez pytania.
- **Wygładzanie parowe** (wariant pokazowy): tylko zewnętrzne powierzchnie korpusów i blatów; **nie** wygładzać kołnierza blatu, haczyków ani kieszeni zatrzasków (zmienia wymiar pasowania) — jeśli nie da się wyłączyć miejscowo, zamówić bez wygładzania.
- **Barwienie** nie zmienia wymiarów; dopuszczalne na korpusach i blatach.
- **Wypłukanie proszku** z kieszeni, rowków i otworów (kieszeń gniazda zasilania, rowki w dnie, kanały przewodów we wkładce, otwory ø3 w dnach gniazd płytek).
- **Gabaryt:** korpus 200 × 200 × 59,6 mm, blat 200 × 200 × 14 mm — potwierdzić komorę i ewentualną dopłatę.
- **Orientacja:** korpus dnem w dół, blat wierzchem w dół, wkładka spodem w dół, płytki gniazdami do góry — jak w plikach (największa płaska ściana na Z = 0).
- **Płytki okrągłe n8 i n9 [R57]:** na obwodzie jest celowe ścięcie orientacyjne (płaska ściana pionowa, cięciwa 16 mm, głębokość 0,644 mm, przód‑prawo) — to znak ułożenia płytki w skanerze, **nie wygładzać, nie zaokrąglać i nie „naprawiać”**; obrys ø100 z fazą 0,5 mm na górnej krawędzi; spód płaski (bez kieszeni magnesów); PA12 biały mat, bez wygładzania, ±0,3 mm.

Przy zamówieniu CNC z PMMA (tylko gdy drukarnia nie ma PA12 dla płytek) potrzebny jest plik STEP — konwersja przez FreeCAD.

## Druk własny: FDM z PETG (u kolegi)

Wszystkie części druku własnego to FDM z PETG na drukarce kolegi. Filament: jeden PETG na wszystko; do płytki testowej **PETG biały matowy** (skaner nie lubi połysku; jeśli jest tylko błyszczący, zmatowić sprayem skanerskim — to płytka testowa, nie praca).

| Plik STL | Część | Ilość | Warunek |
|---|---|---|---|
| ramka_pokrywka_v2.stl | Pokrywka (99,6 × 99,6 × 20 mm, ok. 30 cm³) | 4 | po potwierdzeniu pola skanowania |
| ramka_tulejka_dc_v2.stl | Tulejka redukcyjna gniazda zasilania (ø11,85 zewn. — celowo wciskowa, 0,075 mm na stronę w otworze ø12; ø8,2 wewn.; 2 mm; kołnierz ø15 × 1) | 2 | po pomiarze 16 (tylko gdy gniazdo ma gwint ø8) **i po zmierzeniu otworu ø12 w gotowym korpusie** (z druku może wyjść 11,7–11,9 mm) |
| ramka_podkladka_panelu_05_v2.stl, _1_, _2_ | Podkładki pod dystanse panelu ø9, otwór 3,4, grubość 0,5 / 1 / 2 mm | po 8 (24) | po pomiarach 4 i 9 (albo od razu — minuty druku) |
| ramka_plytka_wieczorna_n1_v2.stl | Płytka wieczorna nr 1 — test skanera (PETG biały matowy) | 1 | od razu; czeka na egzemplarz testowy skanera |
| ramka_wkladka_v2.stl | Prototyp wkładki (+ płytka nr 1 jak wyżej, próbka zatrzasku blatu) | 1 | od razu, przed zamówieniem wkładek w drukarni |

Dlaczego PETG, nie PLA: pokrywka ma 4 zatrzaski o występie 0,7 mm, które muszą się sprężynować — PETG jest ciągliwy. Pokrywka bywa kładziona na płytkę z pracami prosto z pieca (40–70 °C): PETG trzyma kształt, PLA mięknie już około 55–60 °C. PETG ma też mały skurcz, więc wnęka 96,6 mm trafia w luz 0,3 mm wokół płytki.

Zalecenie ogólne: ustawienia poniżej to punkt startowy, do dopasowania do konkretnej drukarki i filamentu (plan budowy ramek narzuca tylko: PETG, warstwa 0,2 mm, orientacja). Kolumna „Małe części i płytka testowa” podaje tylko różnice względem pokrywki.

| Parametr | Pokrywka | Małe części i płytka testowa | Uwagi |
|---|---|---|---|
| Dysza; warstwa | 0,4 mm; 0,2 mm (pierwsza 0,2–0,25) | warstwa 0,1–0,15 mm | stożki gniazd 15°, stożki znaczników ø5 i dołki kodu ø2 wymagają drobnej warstwy; podkładka 0,5 mm = 3–5 warstw |
| Temperatura dyszy / stołu | 230–245 °C / 80 °C | tak samo | według producenta filamentu; za gorąco = nitkowanie |
| Prędkość | ≤ 60 mm/s, obrysy zewnętrzne 30–40 mm/s | tak samo | zatrzaski i kołnierz 1,5 mm wymagają spokojnego druku |
| Obrysy; warstwy góra / dół; wypełnienie | 4; 5 / 5; 30–40 % gyroid | tak samo | kołnierz 1,5 mm = pełne obrysy; wierzch pokrywki 2 mm = ok. 10 warstw pełnych |
| Chłodzenie | 30–50 % | tak samo | pełne chłodzenie = słaba spójność warstw PETG |
| Orientacja (bez podpór) | wierzchem do stołu, kołnierzem w górę | płytka: gniazdami do góry; tulejka: kołnierzem do stołu; podkładki: płasko (24 szt. w jednym wydruku); wkładka: spodem w dół | największa płaska ściana na stole; zatrzaski, stożki gniazd (15° od pionu) i znaczników drukują się bez podpór |
| Kompensacja otworów / wnęk | +0,1–0,2 mm w poziomie | tak samo | PETG zawęża wnęki i otwory: wnęka 96,6 ma mieć luz 0,3 na stronę do płytki 96; otwory ø3 w dnach gniazd i ø3,4 w podkładkach w razie potrzeby rozwiercić |
| Tulejka ø11,85 w otworze ø12 | — | sprawdzić w otworze korpusu; przy luzie lub zacisku skalować XY w slicerze ±1 % (ok. ±0,12 mm) | wcisk 0,075 mm na stronę może na FDM nie wyjść; pliku nie zmieniamy; otwór ø8,2 w razie potrzeby przewiercić |
| Pierwsza sztuka | zmierzyć wnękę 96,6 suwmiarką | zmierzyć: bok płytki 96, stożek znacznika ø5, grubość podkładki, tulejka ø11,85 | dopiero potem reszta sztuk |
| Pierwsza warstwa; filament | przyczepność (szkło/PEI, ewentualnie klej w sztyfcie); filament suszony | tak samo | kołnierz 99,6 mm nie może się unosić; mokry PETG = pęcherze i słabe zatrzaski |

Po wydruku pokrywki: ma wejść na płytkę (albo płytkę testową z PETG) bez siły i trzymać po odwróceniu; garby zatrzasków 0,7 mm w rowek 0,8 mm — za ciasno: przeszlifować garby papierem 400; za luźno: zwiększyć kompensację i wydrukować ponownie (ok. 15 zł filamentu).

Uwaga: płytka testowa z PETG to **test skanera** (widoczność stożków i dołków kodu, ułożenie prac; samo pole skanowania przy obrocie mierzy kartonowa makieta 96 × 96 z okręgami ø90/94/100 — kryterium 8 planu) i prototyp pasowania — nie część produkcyjna. Płytki do codziennej pracy (nr 1–6) zawsze z PA12 z drukarni.

## Po pomiarach elektroniki: co dokupić zależnie od wyniku

Pomiary według sekcji 10 planu budowy (suwmiarka, ok. 30 min, gdy elektronika dotrze). Żaden z nich nie zmienia korpusu ani blatu.

| Pomiar | Wynik | Co kupić / zrobić |
|---|---|---|
| 5a — otwory panelu mają gwint M3? | TAK | dystanse 50 mm F‑F + wkręty dociskowe M3 × 5 (nic więcej) |
| | NIE | tulejki F‑F ø5 × 5 klejone epoksydem do spodu panelu + dystanse 45 mm F‑F + wkręty dociskowe |
| 5, 6 — rozstaw i położenie otworów panelu | kwadrat 110–130 mm, przesunięcie ≤ 0,5 mm | nic — dystanse trafiają w rowki dna |
| | inny wzór | wywiercić ø4 w dnie w zmierzonym miejscu, podkładka drukowana pod dystans |
| 4 + 9 — elementy pod panelem i stos Pi z taśmą | nie więcej niż 5 mm ponad wartości domyślne (12 i 26) | nic — zapas 8 mm wystarcza |
| | więcej | obrócić panel tak, by złącza leżały nad kolumną słupków; awaryjnie skrócić słupki Pi pilnikiem |
| 3 — wysokość diod nad płytką panelu | 1–3 mm | nic — luz do szybki 5–3 mm |
| 16 — gwint gniazda zasilania | ø12 | nic |
| | ø8 | zmierzyć otwór ø12 w ścianie kieszeni gotowego korpusu; wydrukować tulejkę redukcyjną × 2 (nominalnie ø11,85 zewn., ø8,2 wewn.; przy luzie lub zacisku skalować XY w slicerze; zewnętrzną sprawdzić suwmiarką przed wciśnięciem) |
| | większy niż 12 | rozwiercić otwór w ścianie kieszeni |
| 17 — flansza gniazda USB | otwory poziomo, rozstaw 23–28 mm | nic |
| | rozstaw 22 mm | spiłować koniec rowka 0,5 mm |
| | otwory pionowo (typ D) | wywiercić 2 × ø3,2 w tylnej ściance |
| różnice długości słupków ±0,5–2 mm | po złożeniu | podkładki drukowane 0,5 / 1 / 2 mm pod dystanse |

## Checklista odbioru druku

Każdą część z drukarni zmierzyć suwmiarką przed montażem (tolerancja druku ±0,3 mm na 200 mm). **Kryterium reklamacji: odchyłka od nominału większa niż ±0,5 mm.** Do ±0,5 mm: bez działania albo drobna poprawka z kolumny „Gdy nie pasuje”. Przed pomiarem wypłukać i przedmuchać proszek.

| Część | Co zmierzyć | Nominał | Dopuszczalnie | Gdy nie pasuje |
|---|---|---|---|---|
| Korpus | obrys zewnętrzny (poza napisem, wystaje 0,6 mm) | 200 × 200 mm | ±0,5 | |
| Korpus | wysokość | 59,6 mm | ±0,5 | zatrzaski blatu mają luz 0,75 w pionie |
| Korpus | wnętrze (w połowie wysokości i przy górnej krawędzi — wypaczenie) | 195 × 195 mm | ±0,5 | kołnierz blatu 193,6 ma luz 0,7 na stronę; wypaczenie do wewnątrz > 0,5: reklamacja; za ciasno mimo to: papier ścierny na kołnierzu |
| Korpus | otwór gniazda zasilania | ø12 mm | +0,2 / −0 | za mały: rozwiercić ø12 |
| Korpus | okno kieszeni | 51 × 24 mm | ±0,3 | |
| Korpus | rowki w dnie pod słupki | szerokość 3,6 mm | ±0,2 | za wąskie (< 3,3): pilnik |
| Korpus | otwory wkrętów blatu w tylnej ściance | ø3,6 mm, rozstaw 150 mm, oś 55 mm nad dnem | ±0,3 | za mały: wiertło ø3,6 |
| Korpus | kieszenie zatrzasków (4, od wewnątrz) | 11 × 3,5 mm, głębokość 1,3; dolna krawędź 52,1 mm nad dnem | ±0,3 | zarośnięte proszkiem: wypłukać |
| Korpus i blat | otwory pod wkręty formujące | ø2,1 (4 × Raspberry Pi), ø2,5 (2 słupki blatu, głębokość 6) | — | zawsze przewiercić ø2,1 / ø2,5 przed pierwszym wkręceniem |
| Blat | obrys | 200 × 200 mm, grubość 4 + kołnierz 10 (razem 14) | ±0,3 | |
| Blat | kołnierz zewnętrzny | 193,6 × 193,6 mm | ±0,5 | ponad 194,1: reklamacja albo szlifować; poniżej 193,1: blat luźny, ale zatrzaski i wkręty trzymają |
| Blat | kieszeń dyfuzora / okno | 162 × 162 mm, głębokość 2 / 158 × 158 mm | ±0,3 | pleksi 160 nie wchodzi: szlifować pleksi, nie blat |
| Blat | otwory kołków wkładki | ø3,4 mm, rozstaw 116 mm | ±0,15 | kołki ø3, luz 0,2 na stronę; < 3,2: rozwiercić ø3,4 |
| Wkładka | otwór na płytkę | 96,8 × 96,8 mm | ±0,3 | płytka 96 ma mieć luz 0,4 na stronę; < 96,4: papier 400 na ścianach; > 97,3: reklamacja |
| Wkładka | rama i obrys | rama 104,8 × 104,8 × 6 mm; obrys z uszami 130 × 148,4 mm | ±0,5 | wypaczenie > 0,3 na 148: reklamacja |
| Wkładka | kołek orientacyjny; kołki do blatu | 4,4 × 4,4 mm; ø3 mm, rozstaw 116 | ±0,1 | kołek ma wejść w wycięcie płytki 5 × 5 |
| Płytka | obrys | 96,0 × 96,0 mm, grubość 8 mm; wycięcie 5 × 5 | ±0,3 | ponad 96,5: nie wejdzie we wkładkę — szlifować boki |
| Płytka | otwory w dnach gniazd | ø3 mm, przelotowe | | zarośnięte: przebić wiertłem ø3 |
| Płytka | stożki znaczników | ø5, wysokość 3 mm, 3 szt. | | uszkodzone: płytka do wymiany (program wyrównuje po nich skan) |
| Płytka | dołki kodu; kieszenie magnesów | dołki ø2 × 1; kieszenie ø5,2 × 2,2 od spodu | | magnes ø5 × 2 ma wejść z luzem na klej |
| Płytka okrągła n8 / n9 [R57] | średnica, grubość; ścięcie orientacyjne | ø100,0 mm, grubość 8 mm (8,6 z cyfrą); ścięcie: płaska ściana, cięciwa 16 mm, przód‑prawo | ±0,3 | ścięcie zaokrąglone albo niewidoczne: reklamacja (program i technik układają płytkę po nim) |
| Pokrywka (PETG) | wnęka | 96,6 × 96,6 mm, wysokość 20 mm | +0,3 / −0 | ma trzymać na płytce po odwróceniu |
| Wszystkie | próba na sucho | płytka we wkładce, wkładka na blacie, pokrywka na płytce, blat na korpusie | | według kroku 6 montażu w planie wdrożenia |

Przy odchyłce poza tolerancją: najpierw sprawdzić, czy to nie resztki proszku, potem reklamacja z pomiarem i plikiem (wymiary nominalne są w arkuszu wymiarów dołączonym do plików).

Odstępstwa konstrukcyjne, o których warto wiedzieć przy odbiorze i montażu (ściana korpusu 1,2 mm za kieszenią zatrzasku, otwór wkładki 96,8 mm, wciskowa tulejka gniazda, układ gniazd płytek w kole o promieniu 47 mm), są opisane wraz z powodami w dokumencie „Budowa ramki — decyzje i zamienniki”.
