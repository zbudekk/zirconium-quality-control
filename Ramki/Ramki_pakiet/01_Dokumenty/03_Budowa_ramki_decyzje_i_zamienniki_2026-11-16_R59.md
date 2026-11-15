# Budowa ramki — decyzje i zamienniki

14 listopada 2026 (R59: nowy układ gniazd płytek) · Autor: Michał Budek

## Po co ten dokument

Każdy element ramki świetlnej i płytki na prace ma swój powód: wymiar, materiał albo sposób mocowania wynika z czegoś, co leży obok, pod spodem albo w skanerze. Ten dokument opisuje stan obecny i dla każdego elementu mówi, dlaczego jest taki, czy można go zmienić (inny wymiar, materiał, kupny zamiennik, inny sprzęt) i co taka zmiana wymusza w pozostałych częściach oraz w plikach STL. Druga połowa zbiera wszystko, z czego świadomie zrezygnowano, razem z powodami — te zapisy znikają z pozostałych dokumentów, a tu zostają. Dokument towarzyszy trzem innym: „Stanowisko kontroli cyrkonii — plan wdrożenia v2”, „Zakupy i druk — stanowisko kontroli cyrkonii” i planowi budowy ramek v2 (`plan_ramki_v2.md`, pełna geometria z rachunkami).

Zasada: liczby pochodzą z pliku `parametry.json`, który jest jedynym źródłem wartości dla generatora plików STL — zmienia się liczbę w tym pliku, nie rysunek. Wartości bez źródła w plikach projektu są oznaczone „do ustalenia”.

## Zasady, które rządzą całą konstrukcją

- **Obudowa nie zależy od pomiarów elektroniki.** Korpus i blat można zamówić przed rozpakowaniem panelu i Raspberry Pi: 8 mm zapasu nad stosem Pi, rowki pod słupki panelu na rozstaw 110–130, otwór gniazda zasilania ø12 z tulejką dla gniazd ø8, okno USB 16 × 9 z rowkami na rozstaw flanszy 23–28, dystanse 50 albo 45 i podkładki 0,5 / 1 / 2. Gdy pomiar wyjdzie inaczej, poprawia się dobór kupnych części albo wierci otwór w ukrytym miejscu — nie zamawia się nowego korpusu.
- **Luz = suma tolerancji obu części.** Drukarnia (MJF/SLS, nylon PA12) daje ±0,3 mm na każdej części, więc pasowanie ruchome ma luz co najmniej 0,6 (±0,3 + ±0,3) w kierunku, w którym obie części mogą się rozminąć. Wyjątek: pasowania celowo wciskowe, zapisane jawnie (tulejka gniazda zasilania).
- **Części widoczne i nośne z drukarni, ukryte i robocze z PETG.** Korpus, blat, wkładka i płytki to nylon PA12 z drukarni (korpus i blat grafit, wkładka i płytki białe). Pokrywka, tulejka, podkładki, płytka testowa i prototypy pasowań to druk własny z PETG na drukarce FDM u kolegi. Niczego nie drukuje się z żywicy.
- **Gniazda płytki leżą w kole o promieniu 47**, bo skaner obraca płytkę wokół osi pionowej i w całym obrocie widzi koło ø100, nie kwadrat. Obrys płytki zostaje kwadratowy 96 × 96, bo wkładka, pokrywka i wycięcie orientacyjne tego potrzebują.
- **Ścianki co najmniej 1,5 mm**, otwory co najmniej ø1,5, reliefy 0,6. Wyjątki są wymienione na końcu sekcji 3.
- **Żadnych przycisków na ramce.** Skan wieczorem uruchamia spacja na laptopie, rano kuwety przełącza bezprzewodowa klawiatura numeryczna. Przednia ścianka jest gładka, z samym napisem; obie obudowy są identyczne poza napisem i odbiornikiem klawiatury.
- **Bez wkładek gwintowanych.** Wkręty formują gwint w nylonie: otwór ø2,5 pod M3, ø2,1 pod M2,5; przed pierwszym wkręceniem otwory przewierca się, bo zostaje w nich proszek z druku.

## Elementy ramki i płytki — jeden po drugim

### Obudowa jako całość

**Jak jest.** Kostka 200 × 200 × 63,6: korpus 200 × 200 × 59,6 i blat 4, wierzch blatu na 63,6. Wariant „wysoki”: Raspberry Pi leży na dnie pod panelem LED, panel pod blatem, w blacie okno z dyfuzorem i wkładką. Pliki: `ramka_korpus_W_v2.stl`, `ramka_korpus_P_v2.stl`, `ramka_blat_v2.stl`.

**Dlaczego tak.** Alternatywą był wariant niski 200 × 270 × 40 z Pi obok panelu. Wysoki zajmuje 400 cm² zamiast 540 cm², ma krótszą taśmę do panelu, chowa Pi pod panelem i blatem (mniej pyłu), ma sztywniejszy blat i mniej druku. Wysokość 63,6 przekracza zakładane 55–60 o 3,6 — to cena 8 mm zapasu nad stosem Pi, dzięki któremu korpus można zamówić przed pomiarami.

**Czy można zmienić.** Warunkowo. Bok zewnętrzny można zmniejszyć do około 180 (panel 160 plus ściany, dystanse do ±65 i skrzynka gniazda muszą się zmieścić) albo zwiększyć dowolnie. Wysokość jest liczona z łańcucha wysokości i zmienia się przez jego składniki. Wariant niski nie istnieje w plikach — to nowy projekt korpusu i blatu.

**Co to wymusza.** Zmiana boku przebudowuje korpus i blat (kołnierz, kieszenie zatrzasków, szczeliny, skrzynka gniazda, okno USB, napis); wkładka, płytki, pokrywka, tulejka, podkładki bez zmian. Zmiana wysokości przebudowuje korpus (kieszenie zatrzasków, wkręty blatu i napis liczą się od wierzchu korpusu) i zmienia długość kupnych dystansów; blat jest geometrycznie lokalny.

### Korpus (W i P)

**Jak jest.** Skorupa ze ścianami 2,5 i dnem 3, pionowe krawędzie R 5, dolna R 3, wnętrze 195 × 195. Dwa pliki różnią się tylko napisem na przedniej ściance: „RAMKA WIECZORNA” / „RAMKA PORANNA”, litery 8, relief 0,6, środek na Z 51 (8,6 pod wierzchem korpusu). Cechy:

| Cecha | Wymiary | Po co |
|---|---|---|
| Wentylacja | wylot: szczeliny 12 × 3 na Z 8: 4 z tyłu na x −54, −18, 18, 54, po 3 na bokach na y −36, 0, 36; wlot: 2 szczeliny 30 × 4 w dnie pod Pi (−8, ±10) | konwekcja od radiatora Pi (10–13 W); luz kołnierza blatu to dodatkowy wylot górny |
| Kieszeń gniazda zasilania | okno w tylnej ścianie 51 × 24, dolna krawędź Z 14, środek x −67,5; skrzynka 22 głęboka (do y 78), ściany 2; gniazdo w prawej ścianie skrzynki (x −40), oś wzdłuż X w (y 89, Z 30), otwór ø12 | ramka poranna jest chowana do szafki — wtyk nie może wystawać poza obrys; gniazdo osią X nie celuje w dystans panelu i nie zależy od długości gniazda ani wtyku; mieści się wtyk kątowy i prosty o korpusie do 37 |
| Okno USB serwisowe | 16 × 9 w tylnej ścianie w (x 60, Z 24) + 2 rowki poziome 3,2 × 5,7 na rozstaw flanszy 23–28 | panelowe gniazdo USB‑A z zaślepką i kablem 30 cm do Pi; żadne złącze Pi nie jest odsłonięte |
| Rowki pod słupki panelu | 4 podkładki‑stadiony 9 × 1 na przekątnych od (±55, ±55) do (±65, ±65), pod każdą rowek przelotowy 3,6 | rozstaw otworów panelu nie jest znormalizowany (110–136); słupek staje w zmierzonym punkcie; wzór poza rowkami → wiercenie ø4 w dnie |
| Bossy Pi | 4 × ø8 × 5, otwór ø2,1 × 5; narożnik Pi w (−50, −28), Pi zajmuje x −50…35, y −28…28 | Pi w całości pod panelem; z każdej strony Bonnetu jest miejsce na wtyk zasilania o wysięgu 40, bo kierunek wtyku nie jest znany przed zakupem |
| Kieszenie zatrzasków blatu | 4 ślepe kieszenie 11 × 3,5 × 1,3 od wewnątrz, dolna krawędź Z 52,1 (7,5 pod wierzchem korpusu); boki y 0, przód x +50, tył x −50 | haczyki blatu; położenia omijają napis z przodu i skrzynkę gniazda z tyłu |
| Otwory wkrętów blatu | 2 × ø3,6 z pogłębieniem ø6,3 / 90° w (±75, Z 55 — rozstaw 150, 4,6 pod wierzchem korpusu) | wkręty M3 × 8 trzymają blat przy noszeniu ramki porannej |

**Dlaczego tak.** Ściany 2,5 i dno 3 to minimum sztywności skorupy 200 z nylonu bez żeber (ugięcie dna pod 0,5 kg poniżej 0,3). Cechy od strony elektroniki są ruchome albo z zapasem, żeby korpus — około 40 % kosztu zamówienia — nie zależał od żadnego pomiaru.

**Czy można zmienić.** Napis: dowolnie; szerszy niż około 110 mm zacznie kolidować z kieszenią zatrzasku na x +50. Ściany 2,0 i dno 2,5 (około −15 % objętości korpusu): wtedy kieszeń zatrzasku 1,3 zostawia 0,7 ściany — zmniejszyć głębokość kieszeni i występ haczyka. Szczeliny: swobodnie, byle omijały skrzynkę gniazda i okno USB. Gniazdo zasilania: do ø12 bez zmian, powyżej rozwiercenie ściany skrzynki albo nowy otwór w pliku. Gniazdo USB z flanszą pionową: wiercenie 2 × ø3,2. Położenie Pi: dowolne, byle pod panelem z miejscem na wtyk Bonnetu.

**Co to wymusza.** Napis: tylko dwa pliki korpusu. Ściany: korpus i blat (kołnierz 193,6 liczy się od wnętrza 195). Wentylacja, Pi, okno USB, kieszeń gniazda: tylko korpus.

### Blat

**Jak jest.** Płyta 200 × 200 × 4 z kołnierzem 10 × 2 pod spodem, obrys kołnierza 193,6 (luz 0,7 na stronę), krawędzie R 5 i R 1,5 u góry. Okno przelotowe 158 × 158 z kieszenią dyfuzora 162 × 162 × 2 od góry, naroża ostre. 4 haczyki zatrzaskowe 8 szerokie, występ 1,5 i 2 wysoki na Z 52,85, ramię 1,5 × 9 z nacięciami 1. 2 słupki 8 × 6 × 10 po wewnętrznej stronie tylnego kołnierza (y 89,2…95,2) z otworem ø2,5 × 6 pod wkręt M3 × 8 z tylnej ściany. Pod wkładkę: 2 otwory ślepe ø3,4 × 3,8 w (±58, 93,5), 2 kieszenie magnesów ø5,4 × 2,3 w (±58, 86), 2 szczeliny kabli 4 × 8 w (±66, 90). Spód płaski. `ramka_blat_v2.stl`, 2 szt., PA12 grafit.

**Dlaczego tak.** Zero śrub na wierzchu: blat zdejmuje się palcami, a dwa wkręty z tyłu są niewidoczne i zabezpieczają blat przy noszeniu ramki porannej; od spodu wymagałyby słupków 55. Kołnierz 10 daje sztywność bez żebra. Otwory kołków są ślepe, żeby pył nie wpadał do środka; wkładkę trzymają magnesy, kołki tylko pozycjonują, więc ich pasowanie jest ruchome (0,2).

**Czy można zmienić.** Grubość blatu: tak, ale wchodzi w łańcuch wysokości (przy 5 korpus skraca się do 58,6). Wkręty tylne można usunąć (zatrzaski trzymają blat z dużym zapasem) — zostawiono je dla ramki noszonej codziennie. Zatrzaski zamienić na same wkręty: nie, każda regulacja czujników wymagałaby wkrętaka. Okno i kieszeń zależą od panelu i dyfuzora.

**Co to wymusza.** Grubość blatu → wysokość korpusu i korpus (dystanse bez zmian, bo spód panelu zostaje na 54). Usunięcie wkrętów → blat bez słupków i korpus bez otworów ø3,6. Zmiana okna → blat, wkładka (margines wokół ramy) i panel.

### Łańcuch wysokości

**Jak jest.** Z od zewnętrznego dna korpusu:

| Poziom | Z | Składnik |
|---|---|---|
| wierzch dna | 3,0 | dno 3 |
| spód PCB Pi | 8,0 | + bossy Pi 5 |
| szczyt stosu Pi + Bonnet | 34,0 | + stos 26 (z taśmą do 31) |
| najniższy element spodu panelu | 42,0 | + zapas 8 |
| spód PCB panelu | 54,0 | + elementy pod panelem 12 (z kablami do 17) |
| lico diod | 57,6 | + PCB 1,6 + diody 2 |
| spód dyfuzora | 61,6 | + odstęp 4 |
| wierzch dyfuzora = wierzch blatu | 63,6 | + pleksi 2 |
| wierzch korpusu | 59,6 | wierzch blatu − blat 4 |
| wierzch półek / ramy wkładki | 66,1 / 69,6 | + półka 2,5 / + rama 6 |
| wierzch płytki | 74,1 | półka + płytka 8 |
| szczyt najwyższej pracy | 84,1 | płytka − gniazdo 4 + praca 14 |

Panel stoi na 4 dystansach: dno 3 + podkładka 1 + dystans 50 = 54. Od wierzchu korpusu liczą się: dolna krawędź kieszeni zatrzasku (− 7,5), występ haczyka (− 6,75), oś wkrętów blatu (− 4,6), środek napisu (− 8,6).

**Dlaczego tak.** Trzy składniki nie są zmierzone: wysokość diod, elementów pod panelem i stosu Pi. Zamiast czekać na elektronikę, wbudowano 8 mm zapasu nad stosem: pokrywa taśmę HUB75 w Bonnecie (26 → 31) albo złącza panelu z kablami (12 → 17), łącznie do +5 ponad wartości domyślne. Diody wyższe lub niższe o 1 zmieniają luz dioda–dyfuzor w zakresie 3–5 — nadal w normie. Po zamówieniu korpusu wysokości 54 / 59,6 / 63,6 są zamrożone: pomiary wpisuje się do brył zastępczych w modelu, a różnice wyrównuje dobór dystansu (50 albo 45 z tulejką) i podkładek.

**Czy można zmienić.** Przed zamówieniem korpusu, przez składniki: zapas nad stosem (mniej = niższa ramka, ale ryzyko kolizji taśmy ze złączami panelu), odstęp diody–pleksi (3–5), bossy Pi (5 → 3 to awaryjne −2). Gdy panel albo stos okażą się wyższe o więcej niż 5 łącznie: obrócić panel tak, by złącza leżały nad kolumną dystansów, nie nad Bonnetem; w ostateczności bossy Pi 3. Inna nakładka na Pi: stos rośnie i łańcuch przelicza się w górę.

**Co to wymusza.** Każda zmiana łańcucha przebudowuje korpus i zmienia długość dystansów (jest liczona z łańcucha). Blat, wkładka, płytki, pokrywka — bez zmian w siatce.

### Panel LED 64 × 64 P2.5

**Jak jest.** Panel HUB75 160 × 160, raster 2,5, PCB 1,6, 4 otwory M3 na kwadracie około 120 (do zmierzenia), diody około 2 nad PCB, elementy pod PCB do 12. Zasilanie 5 V z Bonnetu kablem VH4 panelu, dane taśmą 16‑pin 150 mm. Pod płytką 96 leży 38 × 38 pikseli; rama wkładki 4 zasłania 1,6 piksela z boku; wolny margines wokół wkładki 27,6 = 11 pełnych pikseli na cyfry 5 × 7.

**Dlaczego tak.** 64 × 64 przy rastrze 2,5 to najmniejszy panel, który mieści płytkę 96 z marginesem na numer kuwety i liczbę prac. Pod najmniejszym gniazdem poprzedniego układu (ø7,5) leży blok 3 × 3 pikseli, więc każde gniazdo świeci osobno; od R59 najmniejsze gniazdo ma ø12 i leży nad blokiem 4 × 4 pikseli (12 / 2,5 = 4,8); kalibracja gniazdo → diody toleruje ±1,25 (pół piksela).

**Czy można zmienić.** Inny producent tego samego formatu: tak, bez zmian geometrii — różnice w otworach (rowki 110–130, gwint lub tulejka klejona), złączach (zapas 8) i wysokości diod (luz 3–5) są pokryte. P3 (192 × 192): raster nadal daje ≥ 2 × 2 piksele pod ø7,5, ale PCB nie mieści się w oknie 158 i między dystansami — okno blatu, pleksi, rozstaw rowków i bok korpusu do przeliczenia. P2 (128 × 128): za mały margines na cyfry. P4 i grubszy raster: pod ø7,5 nie zmieści się pełny piksel. Liczby dla ø7,5 dotyczą poprzedniego układu gniazd; płytki w tym układzie zostają w użyciu, więc ograniczenie obowiązuje nadal [R59].

**Co to wymusza.** Ten sam format: nic w plikach, ewentualnie dystans 45 + tulejka i podkładki. Inny raster przy PCB 160: tylko tabela kalibracji. Inne PCB: korpus, blat, dyfuzor, zwykle też bok korpusu; wkładka, płytki, pokrywka bez zmian, dopóki margines na cyfry wystarcza.

### Raspberry Pi 4 + RGB Matrix Bonnet

**Jak jest.** Pi 4 B 2 GB (PCB 85 × 56; otwory 58 × 49, ø2,7) z radiatorem, na 4 bossach ø8 × 5, wkręty M2,5 formujące gwint. Nakładka Adafruit RGB Matrix Bonnet na złączu GPIO; stos od spodu PCB Pi do szczytu Bonnetu 26, z taśmą do 31. Bonnet zasila Pi przez GPIO, więc obudowa ma jedno gniazdo. Gniazdo DC Bonnetu domyślnie przy krawędzi karty SD, wtyk w −X (do zmierzenia); wtyk 40 mieści się w −X, −Y i +Y. GPIO 19, 25, 8 (czujniki) wyprowadza kątowa listwa dolutowana do Bonnetu. Karta SD: po zdjęciu blatu i panelu.

**Dlaczego tak.** Bonnet to gotowy sterownik matrycy z zasilaniem panelu i Pi, obsługiwany przez bibliotekę rpi‑rgb‑led‑matrix bez pisania firmware; Pi ma Wi‑Fi do laptopa, USB dla odbiornika klawiatury i Python jak reszta stanowiska.

**Czy można zmienić.** Pi 3 B+: ten sam obrys i otwory, działa z biblioteką — bez zmian. Pi 5: ten sam obrys, ale wyższe aktywne chłodzenie i biblioteka matrycy nie jest na nim wspierana jak na Pi 4 — niezalecane. Pi Zero 2 W: za słabe dla 64 × 64 z PWM, inny obrys 65 × 30 — nowe bossy. RGB Matrix HAT + RTC zamiast Bonnetu: te same piny, wyższy stos — mieści się, jeśli z taśmą ≤ 31. Inny sterownik (np. ESP32): inne otwory i własny firmware — korpus i program do zmiany.

**Co to wymusza.** Pi 3 B+ / HAT: nic w plikach (sprawdzić stos z taśmą). Inny obrys sterownika: tylko korpus (bossy). Stos ponad zapas: łańcuch wysokości → korpus i dystanse.

### Zasilanie

**Jak jest.** Zasilacz 5 V 4 A z wtykiem DC 5,5/2,1, zalecany kątowy. W korpusie panelowe gniazdo DC 5,5/2,1 z nakrętką w prawej ścianie skrzynki kieszeni (otwór ø12), nakrętka od wnętrza, flansza w kieszeni. Dla gniazd z gwintem ø8 tulejka `ramka_tulejka_dc_v2.stl`: ø11,85 zewnętrzna (otwór − 0,15, celowo wciskowa), otwór ø8,2, walec 2, kołnierz ø15 × 1. Od gniazda do Bonnetu przewód 2 × 1 mm² z wtykiem ze śrubkami. Pobór: pełna biel poniżej 3,5 A, typowy obraz poniżej 1,5 A.

**Dlaczego tak.** Jedno gniazdo, bo Bonnet rozdziela 5 V na panel i Pi. Gniazdo w kieszeni, bo ramka poranna jest chowana do szafki i wystający wtyk łamałby gniazdo w nylonowej ścianie. Otwór ø12 z tulejką dla ø8 pokrywa obie typowe średnice gwintu gniazd panelowych.

**Czy można zmienić.** Zasilacz: każdy 5 V od 4 A z wtykiem 5,5/2,1 (albo inna para gniazdo–wtyk). Wtyk prosty: korpus wtyku ≤ 37 od lica gniazda. Gwint ø12: bez tulejki; ø8: z tulejką; inny ≤ 12: tulejka z nowym otworem. USB‑C PD: nie bez zmiany Bonnetu (ma gniazdo DC) i nowej kieszeni.

**Co to wymusza.** Inny zasilacz lub wtyk: nic. Inny gwint ≤ 12: tylko tulejka (drukowana po zmierzeniu otworu w gotowym korpusie). Gwint > 12: rozwiercenie w gotowym korpusie albo nowy korpus.

### Dyfuzor z pleksi mlecznej

**Jak jest.** PMMA opal 2, 160 × 160, cięty na wymiar, rogi ostre. Leży w kieszeni blatu 162 × 162 × 2 na półce 2 wokół okna 158, licowany z blatem, dociskany magnesami wkładki. Lico diod 4 pod pleksi. 2 szt. + zapas.

**Dlaczego tak.** Mleczna pleksi rozprasza diody w plamę widoczną od góry przez otwór ø3 w dnie gniazda i chroni panel przed pyłem. 2 mm to kompromis między rozproszeniem a jasnością; 4 odstępu leży w środku zakresu 3–5.

**Czy można zmienić.** Grubość 3: blat 4 zostawia pod kieszenią tylko 1 (za cienko), więc blat 5 i łańcuch rośnie o 1; albo odstęp od diod 3, by suma została 63,6 (wtedy tylko blat). Bok: tylko razem z panelem. Materiał: poliwęglan lub PETG opal 2 — nic w plikach; bezbarwna pleksi nie rozprasza. Jasność reguluje program.

**Co to wymusza.** Inna grubość: blat, a bez zmiany odstępu od diod także korpus i dystanse. Inny materiał tej samej grubości: nic.

### Wkładka gniazda płytki

**Jak jest.** `ramka_wkladka_v2.stl`, PA12 biały, 3 szt. (2 + zapas), gabaryt 130 × 148,4 × 11. Rama 4 szeroka i 6 wysoka wokół otworu 96,8, zewnętrznie 104,8; faza 1 × 45° u góry otworu, naroża ostre. 4 narożne półki 12 × 12 × 2,5 — płytka leży na nich, 2,5 nad dyfuzorem. W półkach A, B, C kieszeń przelotowa 5,0 × 5,5 na czujnik Halla TO‑92 leżący na dyfuzorze licem do góry; pod półką kanał 2,5 × 1,0, przelot w ściance 2,5 × 1,5 i rowek na zewnętrznej dolnej krawędzi 2,5 × 1,5 jako jedna bryła na przewody. Na półce D kołek 4,4 × 4,4 × 5, 0,6 od ścian otworu, faza 1 — wchodzi w wycięcie 5 × 5 płytki. Wycięcie palcowe 30 z przodu, strzałki ▼ 2 × 3 w x ±32. Dwa tylne uszy 14 × 43,6 × 3 (do y 96) na x ±58 z nasadą L (x 44…65, y 48,8…58); w uchu kołek ø3 × 3,5 w dół (y 93,5), otwór ø5,4 na magnes (y 86), kanał kablowy 2 × 1,2 od spodu wzdłuż x ±64.

**Dlaczego tak.** Płytka nie leży na pleksi, bo nylon z cyrkonią rysowałby dyfuzor, a czujniki muszą być pod narożnikami: półki 2,5 mieszczą TO‑92 (1,5) z 1,0 szczeliny do płytki. Magnes–czujnik: 0,2 + 1,0 + około 0,5 (struktura w obudowie) = 1,7; próg około 40 mT, pole około 150 mT — rezerwa ponad trzykrotna. Rama 6 prowadzi płytkę na 3,5 (przy 3 tylko 0,5). Kołek wymusza jedno ułożenie, bez niego kod magnesów czytałby się w złym rogu. Uszy leżą w litym blacie, bo w pleksi nie osadzi się magnesu; magnesy dociskają, kołki dają powtarzalność ±0,2. Przewód pod płasko leżącą ramą podniósłby ją o 1, stąd kanały.

**Czy można zmienić.** Inna płytka tego samego obrysu 96 (układ gniazd, grubość): wkładka bez zmian — wymaga tylko wolnych stref narożnych 13 × 13 i magnesów 6 od krawędzi. [R59] Tak przeszła zmiana układu gniazd: plik wkładki został ten sam (ta sama suma SHA‑256). Inny bok płytki: otwór = bok + 0,8, rama i uszy przeliczają się — nowa wkładka i pokrywka, korpus i blat bez zmian do boku około 140 (okno 158). Płytka okrągła: otwór okrągły, półki jako wycinki, kołek i magnesy na przekątnych — nowa wkładka i pokrywki. Inny czujnik TO‑92: bez zmian; czujnik SMD: nowa kieszeń w półce. Uszy bez kołków: odrzucone (wkładka „pływa” ±0,5 i przesuwa się przy wkładaniu płytki).

**Co to wymusza.** Zmiana otworu przelicza ramę, nasadę uszu, rowki i margines matrycy; blat bez zmian, jeśli kołki zostają w (±58, 93,5). Przesunięcie kołków lub magnesów uszu → blat.

### Płytki na prace (n1–n6)

**Jak jest.** Kwadrat 96 × 96 × 8, krawędzie R 1, faza górna 0,5, PA12 biały, mat, bez wygładzania. Pliki do zamówienia (po 1 szt.): `ramka_plytka_wieczorna_n1_v2.stl`, `…_n2_v2.stl`, `…_n3_v2.stl`, `ramka_plytka_poranna_n4_v2.stl`, `…_n5_v2.stl`, `…_n6_v2.stl`; pliki bazowe `ramka_plytka_wieczorna_v2.stl` i `ramka_plytka_poranna_v2.stl` służą tylko sprawdzeniom. [R59] Układ gniazd jest nowy: większe gniazda w miejscu małych i jedna rynienka zamiast dwóch (warianty W‑b i P‑e, wybór właściciela). Obrys, grubość, kod, magnesy, wycięcie i rowek pokrywki zostały bez zmian. Płytki wykonane w poprzednim układzie zostają w użyciu — patrz „[cytat usuniety]”.

| Cecha | Wymiary |
|---|---|
| Układ gniazd | obrysy górne gniazd, rynienki i stożków w kole r 47 (pole 100 / 2 − 1,5 ułożenia − 1,5 wysięgu korony) i w kwadracie 90; rzędy symetryczne względem osi x; ścianka ≥ 3 (najmniejsza 3,000, bez zapasu); największy promień obrysu 45,93 (wieczorna) i 46,41 (poranna) [R59] |
| Wieczorna [R59] | 18 gniazd + 1 rynienka. Od przodu: rynienka 60 × 15 (y −30,2), 6 × ø12 (y −13,7), 5 × ø15 (y 2,75), 4 × ø15 (y 18,35), 3 × ø15 (y 33,95) — razem 6 × ø12 i 12 × ø15; numery 1–3. Było [R54]: 18 gniazd + 2 rynienki (7 × ø9, 6 × ø12, 5 × ø15) |
| Poranna [R59] | 23 gniazda + 1 rynienka. Od przodu: rynienka 50 × 13 (y −35,3), 5 × ø12,5 (y −19,55), 6 × ø12,5 (y −6,1), 4 × ø12,5 (y 8) z jednym ø15 pośrodku (y 8,75), 2 × ø15 po bokach (y 22,85) z 2 × ø12,5 pośrodku (y 23,6), 3 × ø12,5 (y 37,05) — razem 20 × ø12,5 i 3 × ø15; numery 4–6. Było [R54]: 31 gniazd + 2 rynienki (18 × ø7,5, 7 × ø10, 6 × ø12,5) |
| Gniazdo | stożek 15° od pionu, głębokość 4, dno ø d − 2,14, otwór ø3 w osi na światło diody |
| Rynienka | stadion, ścianki 15°, głębokość 4, 4 otwory ø3 w rozstawie 12 / 10; jedna na płytkę, z przodu [R59] |
| Stożki znaczników | 3 × ø5 × 3 w kole [R59]: wieczorna A (−35,5, −26,5), B (−31, 31,5), C (42, 14,5); poranna A (−30,5, −32), B (−37,5, 23,5), C (41,5, 16); środki 44,20–44,48 od środka płytki (limit 44,5), do gniazd 3,02–3,52 (limit 3) |
| Magnesy | 3 kieszenie od spodu ø5,2 × 2,2 w rogach A, B, C, 6 od krawędzi, na magnesy ø5 × 2; magnes wklejony tam, gdzie bit = 1 |
| Kod i numer | 3 dołki ø2 × 1 w x −45, y −36, −33, −30; cyfra 5, relief 0,6, w (39,5, −44,5); n = A + 2·B + 4·C |
| Wycięcie orientacyjne | 5 × 5 przelotowe w rogu D, przód‑prawy |
| Rowek pokrywki | 1,0 × 0,8 wokół boków, 2 pod wierzchem |
| Najwyższa praca | 14 nad dnem gniazda |
| Numery gniazd [R59] | rynienka ma numer 1; dalej rzędami od przodu, w rzędzie od prawej (w rzędzie mieszanym płytki porannej najpierw gniazda bliższe przodu); numery są inne niż w poprzednim układzie |

**Dlaczego tak.** Bok 96 to największy kwadrat, który na pewno mieści się w polu skanera z marginesem na ułożenie. Koło r 47: skaner obraca płytkę, więc przez cały obrót widzi koło ø100 — gniazda w rogach kwadratu (do 61,9 od środka) wypadałyby z pola. Stożek 15° centruje koronę i pozwala ją wyjąć palcami; otwór ø3 pokazuje diodę przy pełnym gnieździe. Kod z 3 magnesów daje numery 1–6 (7 zapas, 0 brak płytki); dołki pokazują kod skanerowi, cyfra technikowi. Stożki znaczników wyrównują skan do wzorca i nie muszą leżeć nad magnesami.

**Dlaczego taki układ gniazd [R59].** Układ wynika z wielkości prac. W próbie 17 projektów najmniejsze gniazda (ø9 wieczorem, ø7,5 rano) nie przyjęły żadnej pracy: 0 z 17. Pięć prac wymagało co najmniej ø12 / ø10, cztery — ø15 / ø12,5, dwie były za duże na największe gniazdo, a sześć mostów wchodziło tylko do rynienki. Dlatego małe gniazda zniknęły, a dużych przybyło: wieczorem gniazd ø15 jest 12 zamiast 5, rano doszły 3 gniazda ø15 i wchodzą w nie obie prace, które rano były za duże. Próba jest mała i dobrana do testów programu, nie jest przekrojem produkcji. Rynienka jest jedna i leży z przodu, najbliżej technika. Usunięta tylna rynienka płytki porannej była najciaśniejszym miejscem układu: leżała 0,07 od granicy koła, a teraz najmniejszy zapas do koła to 0,59 (w wieczornej 1,07).

**Co to kosztuje [R59].** Jeden most na płytkę: rynienka jest jedna, a program przyjmuje jedną pracę w jednym gnieździe. Wieczorem rynienki wymaga 7–8 z 17 prac próby: 6 mostów, trzonowiec za duży na ø15 i drugi duży trzonowiec, który mieści się w ø15 nie zawsze — program ułożył go tam w 13 z 20 prób. Płytka poranna ma 23 gniazda zamiast 31: duży piec (40–60 prac) to 2–3 płytki zamiast 2. Najmniejsze gniazdo ma ø12 / ø12,5 — czy najmniejsze prace leżą w nim pewnie przy obrocie stolika, sprawdzi test skanera.

**Czy można zmienić.** Układ gniazd: tak, w listach rzędów i średnicach — w kole r 47 i kwadracie 90, ścianka ≥ 3, rzędy symetryczne, strefy narożne 13 × 13 wolne. [R59] Układ nie ma zapasu (ścianki 3,000), więc pozycje liczy narzędzie `narzedzia/uklad_kolo_R59.js`, a sprawdza `narzedzia/weryfikuj_uklad_R59.js` — nigdy ręcznie. Dwie krótkie rynienki zamiast jednej długiej policzono dla płytki wieczornej (2 × 28,5 × 15, mieszczą się w kole); wymagają zmiany generatora (po 2 otwory zamiast 4), a w próbie krótka rynienka przyjęła 3 z 6 długich prac. Dwa mosty w jednej długiej rynience to zmiana programu, nie płytki — osobna praca, bez ustalonego terminu. Pole skanowania ø94–100: zmienia się jedna liczba, promień koła przelicza się sam, układ do ułożenia na nowo (mniej gniazd) — tylko nowe płytki. Poniżej ø94: koło w kwadracie 96 marnuje materiał, wraca płytka okrągła ø96–100 — nowe płytki, wkładka i pokrywka; korpus, blat, panel bez zmian. Grubość: tak, łańcuch rośnie nad płytką, pokrywka bez zmian. Inny skaner: obracający stolik → to samo koło, zmierzyć pole; przechylający → głębsze gniazda (do ustalenia po skanie testowym); pole statyczne kwadratowe → wraca kwadrat 90 (promień koła ≥ 64). Materiał: PA12 biały; CNC z PMMA opal 8 tylko gdy usługodawca nie ma PA12.

**Co to wymusza.** Układ gniazd: tylko płytki, tabela kalibracji i plik układu w programie stanowiska; pliki pozostałych części zostają te same [R59]. Bok płytki: wkładka, pokrywka, wszystkie płytki (dołki, magnesy, numer, wycięcie liczą się od krawędzi). Grubość: płytki i łańcuch nad płytką, bez korpusu.

**Co zmieniło R59.**

1. Płytka wieczorna: 7 × ø9, 6 × ø12, 5 × ø15 i 2 rynienki → 6 × ø12, 12 × ø15 i 1 rynienka. Gniazd jest 18, jak wcześniej.
2. Płytka poranna: 18 × ø7,5, 7 × ø10, 6 × ø12,5 i 2 rynienki (31 gniazd) → 20 × ø12,5, 3 × ø15 i 1 rynienka (23 gniazda).
3. Stożki znaczników: w wieczornej przesunięte B i C, w porannej wszystkie trzy.
4. Płytka okrągła poranna: dołki kodu w dwóch parach z prawej strony, cyfra z lewej. Płytka okrągła wieczorna i obie kwadratowe: dołki i cyfra bez zmian.
5. Numery gniazd są inne niż w poprzednim układzie.
6. Osiem plików płytek (n1–n6, n8, n9) ma nowe sumy SHA‑256 przy tych samych nazwach. Objętości: wieczorna 59,31 → 59,66 cm³, poranna 60,87 → 59,95 cm³, okrągłe 49,01 → 49,36 i 50,56 → 49,64 cm³.
7. Bez zmian: gniazdo (stożek 15°, głębokość 4, otwór ø3), wymiary rynienek i ich 4 otwory, numery płytek oraz pliki korpusu, blatu, wkładki, pokrywki, tulejki i podkładek (te same sumy SHA‑256).
8. Stare płytki zostają w użyciu. Program zna oba układy — poprzedni pod nazwą z dopiskiem `_r54` — i ostrzega, gdy zeskanowana płytka nie pasuje do wybranego. Numery płytek są te same, więc stare płytki trzeba opisać i trzymać osobno. Ramka świetlna czyta numer z magnesów i sama nie odróżni starej płytki od nowej; to zostaje do ustalenia przy programie ramki.
9. Pliki sprawdzono niezależnie z siatek: 475 sprawdzeń, 0 niezgodnych.
10. Zamówienie: właściciel skłania się ku płytkom okrągłym; co i ile zamówić, zdecyduje po odbiorze plików. Ilości w arkuszu zamówienia bez zmian.

### Płytka okrągła (n8, n9) — drugi kształt płytki [R57], nowy układ gniazd [R59]

**Jak jest.** Walec ø100 × 8 (z cyfrą 100 × 100 × 8,6), faza 0,5 na górnej krawędzi, bez promienia krawędzi pionowych, spód płaski; PA12 biały, mat, bez wygładzania, ±0,3. Pliki do zamówienia (po 1 szt.): `ramka_plytka_okragla_wieczorna_n8_v2.stl` (49,36 cm³) i `ramka_plytka_okragla_poranna_n9_v2.stl` (49,64 cm³); pliki bazowe `…_okragla_wieczorna_v2.stl` i `…_okragla_poranna_v2.stl` (wszystkie 4 dołki, bez cyfry) służą tylko sprawdzeniom.

| Cecha | Wymiary |
|---|---|
| Układ gniazd | identyczny z płytką kwadratową tego typu: wieczorna 18 gniazd + 1 rynienka, poranna 23 gniazda + 1 rynienka (te same gniazda, rynienka, otwory ø3 i stożki znaczników A, B, C w kole r 47) [R59]; kształt płytki nie zmienia liczby gniazd |
| Krawędź | okrąg R 50; ścianka obrysu gniazd do ściany pionowej: wieczorna 4,07, poranna 3,59; do początku fazy 3,57 / 3,09; stożki do krawędzi 3,07 / 3,02 [R59] |
| Ścięcie orientacyjne | płaska ściana pionowa na całej grubości, cięciwa 16 na kierunku −45° (przód‑prawo), 49,356 od środka, głębokość 0,644; ścianka do obrysów ≥ 3 (wieczorna 4,59, poranna 4,81) [R59] |
| Kod i numer | 4 bity, n = A + 2·B + 4·C + 8·D; dołki ø2 × 1 w kole: wieczorna rząd y −43,5, x −4,5…4,5; poranna [R59] dwie pary z prawej strony: A (36,5, 18,5), B (36,5, 21,5), C (43, 6), D (43, 9); wieczorna = n8 (dołek D), poranna = n9 (A + D); cyfra 5, relief 0,6, w (35, −26,5), poranna [R59] w (−44, 5,5) |
| Czego nie ma | wycięcia 5 × 5, kieszeni magnesów, rowka pokrywki |

**Dlaczego tak.** Drugi kształt płytki powstał, żeby na skanerze porównać kwadrat i koło przy tych samych gniazdach — różni je tylko obrys. [R59] Właściciel skłania się teraz ku zamówieniu płytek okrągłych; zdecyduje po odbiorze plików nowego układu. Koło ø100 to granica pola skanowania przy obrocie: nie ma wystających rogów (mniej kolizji w komorze), a dołki kodu leżą w polu (na kwadracie na promieniu 54–58, poza polem). Średnicę 100 wybrano przy poprzednim układzie gniazd: ø96 dawało wtedy ściankę rynienki tylnej porannej i stożków do krawędzi 1,07 (< 1,5), ø98 — 1,57–2,07. [R59] W nowym układzie tylnej rynienki nie ma, a ścianki do krawędzi są większe (4,07 / 3,59; stożki 3,07 / 3,02); średnica zostaje. Na okrągłej porannej dołki kodu i cyfra przeszły na boki, bo rynienka jest dosunięta do przodu i rząd dołków przed nią już się nie mieści. Ścięcie zastępuje wycięcie: wymusza jedno ułożenie, a cięciwa 16 daje głębokość 0,644 — widoczną po druku (więcej niż faza 0,5 i tolerancja ±0,3). Kod 3‑bitowy miał wolne tylko 7 i 0, więc bit D: płytki 1–6 go nie mają i zostają bez zmian.

**Czy można zmienić.** Średnica: jedna liczba (`plate_round_d`); przy mniejszej niż 100 ścianki do krawędzi maleją o połowę różnicy (dziś 4,07 / 3,59, stożki 3,07 / 3,02, wymagane ≥ 1,5), więc każdą zmianę sprawdza generator [R59]. Cięciwa: 8 niewidoczna (głębokość 0,16), 20 odpadała przy poprzednim układzie (ścianka do obrysów 1,3 < 3); w nowym układzie do przeliczenia [R59]. Położenie dołków i cyfry: liczby w `parametry.json`, z warunkami ścianek (do gniazd ≥ 3, do stożków ≥ 1,5, do krawędzi ≥ 1,5). Każda zmiana: generator → protokół → nowe SHA.

**Co to wymusza.** Teraz nic poza samymi płytkami — to wariant tylko do skanera; wkładka (otwór 96,8 z kołkiem w rogu D i czujnikami pod narożnikami) i pokrywka (wnęka 96,6) go nie obsługują. Jeśli test wskaże koło: zmiana R58 — nowa wkładka (otwór okrągły, półki jako wycinki, kołek i magnesy na przekątnych — jak w „Czy można zmienić” wkładki) i nowe pokrywki, a płytki okrągłe dostają kieszenie magnesów; korpus, blat i panel bez zmian.

### Pokrywka

**Jak jest.** `ramka_pokrywka_v2.stl`, PETG FDM, 4 szt. Nakładka 99,6 × 99,6 × 20: bok = 96 + 2 × 0,3 + 2 × 1,5; wysokość = prześwit 14 (najwyższa praca 14 − gniazdo 4 + 4 zapasu) + wierzch 2 + kołnierz 4 pod wierzch płytki. Wierzch pełny, kołnierz 1,5 schodzi 4 pod wierzch płytki, krawędzie R 3. 4 garby 10 szerokie, występ 0,7, 0,8 wysokie, czubek R 0,4, na Z −18 od wierzchu, na bokach y 0, z przodu x +25, z tyłu x −25; wchodzą w rowek 1,0 × 0,8 płytki. Wycięcia na palec 30 × 3 z przodu i z tyłu. Bez otworów, bez napisu.

**Dlaczego tak.** Osłania prace na czas przenoszenia; 4 zatrzaski trzymają ją po odwróceniu, garby omijają wycięcia palcowe. Kołnierz kończy się 0,5 nad ramą wkładki, więc pokrywkę zakłada się na płytkę leżącą w ramce. PETG, bo zatrzaski sprężynują, a pokrywka bywa kładziona na płytkę prosto z pieca (40–70 °C).

**Czy można zmienić.** Wysokość: przez najwyższą pracę. Luz 0,3: zostawić — większy zmniejsza zahaczenie garbu 0,7 w rowku 0,8; pierwszą sztukę FDM mierzy się i skaluje w slicerze. 2 zatrzaski: nie trzymają po odwróceniu. Materiał: PETG, ASA, ABS; PLA nie (mięknie 55–60 °C). Napis i otwory: celowo ich nie ma.

**Co to wymusza.** Wysokość: tylko pokrywka. Bok płytki lub rowek: pokrywka i płytki razem.

### Tulejka gniazda zasilania i podkładki panelu

**Jak jest.** Druk własny PETG. Tulejka `ramka_tulejka_dc_v2.stl` (wymiary w „Zasilanie”), 2 szt. Podkładki `ramka_podkladka_panelu_05_v2.stl`, `…_1_v2.stl`, `…_2_v2.stl`: krążki ø9 z otworem ø3,4, grubości 0,5 / 1 / 2, po 8 szt.

**Dlaczego tak.** Tulejka: gniazda panelowe mają gwint ø8 albo ø12; otwór ø12 plus tulejka dla ø8 pokrywa oba bez zmiany korpusu. Pasowanie celowo wciskowe (0,15 na średnicy), bo tulejkę drukuje się po zmierzeniu otworu w gotowym korpusie (otwory z druku wychodzą o 0,1–0,2 mniejsze) i dopasowuje skalowaniem XY w slicerze ±1 % zamiast zmianą pliku. Podkładki wyrównują długość dystansu po pomiarach (±0,5…2) i podkładają słupek w otworze wierconym, gdy wzór otworów panelu wypadnie poza rowkami.

**Kiedy niepotrzebne.** Tulejka: gdy gniazdo ma gwint ø12. Podkładki: gdy spód panelu wypada dokładnie na 54 i otwory trafiają w rowki. Obie kosztują tyle co filament, więc drukuje się je i tak.

**Czy można zmienić / co to wymusza.** Inny gwint gniazda: tylko tulejka. Inne grubości: tylko podkładki. Kupne zamienniki (podkładki M3 ø9 z tworzywa lub stali, metalowa tulejka 12/8): bez plików.

### Dystanse panelu i mocowanie bez gwintu

**Jak jest.** Panel stoi na 4 mosiężnych dystansach M3 żeńsko‑żeńskich 50 (54 − dno 3 − podkładka 1). Dół: wkręt M3 × 10 z podkładką ø9 od spodu przez rowek 3,6, łeb 2,5 pod dnem, mniej niż stopki 4. Góra, gdy otwory panelu mają gwint M3: wkręt dociskowy M3 × 5 bez łba — 2,5 w panel, 2,5 w dystans, nic nie wystaje od strony diod. Bez gwintu: tulejka mosiężna F‑F M3 ø5 × 5 doklejona epoksydem do spodu PCB (centrowana śrubą przez otwór na czas klejenia) + dystans 45 (3 + 1 + 45 + 5 = 54). Rozstrzyga pomiar: wkręcić śrubę M3 palcami w otwór panelu.

**Dlaczego tak.** Dystans wkręcany w gwint panelu nie działa bez gwintu, a nakrętka od strony diod wystawałaby ku dyfuzorowi; tulejka klejona rozwiązuje to bez zmian w drukowanych częściach. Dystanse ustalają panel w XY (±0,2), więc rama wokół panelu nie jest potrzebna.

**Czy można zmienić / co to wymusza.** Długość: liczona, tylko przez łańcuch wysokości. Dystanse nylonowe M3 F‑F: tak (panel waży około 200 g). Wkręty dłuższe niż M3 × 10 od spodu: nie, przebiją dystans do PCB. M4: rowki 4,6 i otwory podkładek — korpus, podkładki, lista zakupów.

### Czujniki Halla i magnesy

**Jak jest.** 3 czujniki A3144 (cyfrowe, unipolarne, otwarty kolektor, TO‑92) w półkach A, B, C, zasilane 5 V, wyjście podciągnięte 10 kΩ do 3,3 V na płytce prototypowej 30 × 20, do GPIO 19, 25, 8; magnes obecny = stan niski. Magnesy ø5 × 2 N35: 9 w płytkach (wg kodu), 2 w uszach wkładki, 2 w blacie na ramkę; biegun S w dół, oznaczony przed klejeniem (klej CA). Kod płytki = układ 3 magnesów, n = A + 2·B + 4·C; odczyt stabilny, zmiana poniżej 100 ms po położeniu.

**Dlaczego tak.** Pi nie ma przetwornika analogowego, więc czujnik musi być cyfrowy; A3144 jest tani i dostępny w Polsce; 3 bity wystarczają na 6 płytek. NFC/RFID odrzucone: antena nie mieści się pod płytką bez zasłaniania pikseli, czytnik to kolejny moduł, kabel i biblioteka; magnesy są tanie, bezobsługowe i czytelne gołym okiem (dołki kodu).

**Czy można zmienić.** Inny czujnik TO‑92 o pinach VCC/GND/OUT (Honeywell SS451A, TI DRV5032, omnipolarne 3,3 V): bez zmian geometrii, biegun dowolny, rezystory wg karty. Czwarty bit: czujnik w półce D nie zmieści się obok kołka — zostają 3 bity. Magnes ø4 lub ø6: kieszenie w płytkach, uszach i blacie; ø3 za słaby na 1,7 z rezerwą.

**Co to wymusza.** Inny czujnik TO‑92: tylko schemat. Inny magnes: płytki, wkładka, blat.

### Klawiatura numeryczna 2,4 GHz

**Jak jest.** Jedna bezprzewodowa klawiatura numeryczna 2,4 GHz z odbiornikiem USB nano (około 19 × 15 × 6, do zmierzenia) w porcie USB Pi ramki porannej; leży luzem na stole. Enter potwierdza kuwetę, Backspace cofa, cyfry wybierają kuwetę, osobny klawisz zamyka piec. Ramka wieczorna nie ma klawiatury — skan uruchamia spacja na laptopie. Słaby zasięg przez obudowę: przedłużacz USB 20 cm na rzep do lewej ściany.

**Dlaczego tak.** Rano technik ma ręce przy kuwetach, a laptop stoi przy skanerze; odbiornik USB działa bez firmware i bez parowania (Bluetooth‑only odrzucone: parowanie po każdym restarcie Pi).

**Czy można zmienić / co to wymusza.** Dowolna klawiatura z odbiornikiem USB 2,4 GHz, także pełna; legenda klawiszy jest w programie. Odbiornik do około 25 mm mieści się przy portach Pi. Nic w plikach.

### Stopki

**Jak jest.** 4 stopki gumowe samoprzylepne ø10 × 4 na płaskim dnie, środek 12 od krawędzi; bez gniazd w dnie. Łby wkrętów panelu z podkładkami wystają pod dnem 2,5, czyli 1,5 mniej niż stopki.

**Dlaczego tak.** Wgłębienie 0,5 nie trzyma stopki lepiej niż klej, a przeszkadza przy wygładzaniu; nylon jest porowaty, dno przemywa się alkoholem przed klejeniem.

**Czy można zmienić / co to wymusza.** Każda stopka samoprzylepna ≥ 3 mm wysokości: nic w plikach. Stopki wkręcane: otwory w dnie — niepotrzebne.

### Prowadzenie kabli

**Jak jest.** Bez drukowanych uchwytów. Wiązki trzymają podstawki opasek samoprzylepne 20 × 20 (6 szt. na dwie ramki); płytka prototypowa 30 × 20 na taśmie 3M VHB na lewej ścianie na Z 40, ze złączami JST od Pi i od czujników. Przewody czujników AWG 28 idą z uszu wkładki przez szczeliny blatu (±66, 90). Kable ≤ 300, pętla 50 przy blacie, żeby blat dało się zdjąć i odłożyć obok bez rozpinania.

**Dlaczego tak.** Drukowane uchwyty z bossami to osobny plik, 4 części, 2 bossy i 2 otwory za funkcję, którą daje podstawka za kilkadziesiąt groszy; części są ukryte.

**Czy można zmienić / co to wymusza.** Dowolne podstawki, klipsy, rzepy: nic w plikach. Powrót do uchwytów drukowanych = bossy w korpusie, nowy korpus — niezalecany.

### Materiały

**Jak jest.** Plik `parametry.json` przypisuje materiał do każdego pliku STL: korpus W/P i blat — PA12 z drukarni barwiony na grafit (wariant pokazowy z wygładzaniem parowym); wkładka i płytki — PA12 naturalny biały, płytki bez wygładzania wierzchu (mat dla skanera); pokrywka, tulejka, podkładki, płytka testowa nr 1 i prototypy — PETG FDM u kolegi. Kolory w modelu dotyczą tylko renderów.

**Dlaczego tak i czego nie.** Nylon PA12 z drukarni: wytrzymały, bez podpór, ±0,3, trzyma gwint formowany (≥ 10 cykli), biały mat pod skaner, grafit na pokaz. PETG: ciągliwy (zatrzaski sprężynują), trzyma kształt do około 70 °C, mały skurcz. **Nie PLA** — mięknie przy 55–60 °C i pełza, a pokrywka i płytka poranna widzą 40–70 °C. **Nie żywica** — decyzja właściciela: wszystko własne na FDM z PETG; żywice są kruche przy zatrzaskach, a ±0,05 nie jest tu potrzebne. **Nie PMMA CNC jako podstawowy** materiał płytek — tylko droga zapasowa, gdy usługodawca nie ma PA12 (plik STEP przez FreeCAD, wyższa cena). **Nie barwienie ani wygładzanie płytek** — zmieniają mat wierzchu, który skanuje się bez pudru. **Nie płytki z PETG na FDM na stałe** — warstwy i połysk przeszkadzają skanerowi, ±0,5 psuje luz we wkładce; tylko płytka testowa.

**Czy można zmienić / co to wymusza.** Zmiana materiału nie przebudowuje geometrii, zmienia arkusz zamówienia. Kolor korpusu: dowolny barwnik, bez plików. SLS zamiast MJF: te same pliki, ta sama tolerancja, często taniej dla dużych brył.

### Luzy i tolerancje oraz świadome odstępstwa

**Jak jest.** Drukarnia ±0,3 na każdej części; otwory i rowki wychodzą o 0,1–0,2 mniejsze; FDM PETG ±0,5 % ze skalowaniem pierwszej sztuki. Luzy nominalne:

| Pasowanie | Wartość |
|---|---|
| kołnierz blatu w ścianie korpusu (193,6 w 195) | 0,7 na stronę |
| występ haczyka blatu (zahaczenie 0,8, luz do dna kieszeni 0,5) | 1,5 |
| kieszeń zatrzasku: głębokość / wysokość (luz 0,75 pod i nad) / szerokość (luz boczny 1,5) | 1,3 / 3,5 / 11 |
| otwór wkrętu blatu w ścianie (przelot M3, luz 0,3) | ø3,6 |
| kołek ø3 wkładki w blacie (ruchome 0,2) | ø3,4 |
| płytka 96 w otworze wkładki (0,4 na stronę) | 96,8 |
| rowek pod wkręt dystansu panelu | 3,6 |
| kołek orientacyjny od ścian otworu (luz do wycięcia 0,4) | 0,6 |
| pokrywka na płytce (FDM, skalowanie pierwszej sztuki) | 0,3 na stronę |
| tulejka w otworze ø12 — celowo wciskowe, 0,075 na stronę | ø11,85 |

Zasada: luz nominalny pasowania ruchomego ≥ 0,6 w kierunku, w którym obie części mogą się rozminąć; przy odbiorze druku odchyłka większa niż ±0,5 od nominału to podstawa reklamacji.

**Świadome odstępstwa** (do wiedzy przy odbiorze i montażu, nie wymagają działania):

1. **Ściana korpusu za kieszenią zatrzasku 1,2 lokalnie** (2,5 − 1,3) na 4 polach 11 × 3,5, nienośnych — odstępstwo od ścianki ≥ 1,5; alternatywa (zahaczenie 0,4) była za słaba. Przednia ściana ma tam dodatkowo relief napisu 0,6.
2. **Otwór wkładki 96,8 zamiast 96,6**: zasada sumy tolerancji; przy 96,6 najgorszy przypadek dawał luz 0 i klinowanie płytek. Obrys płytki, wycięcie, rowek, magnesy i pokrywka bez zmian.
3. **Tulejka gniazda zasilania celowo wciskowa** (0,15 na średnicy): druk własny po zmierzeniu otworu w gotowym korpusie; przy luzie lub zacisku skalowanie XY w slicerze ±1 %, bez zmiany pliku.
4. **Dno słupka blatu pod otworem wkrętu 1,6** (wymagane ≥ 1,5); gwint wkrętu M3 × 8 w słupku 4,8.
5. **Dno blatu pod ślepym otworem kołka 0,2** (otwór 3,8 w blacie 4): nie jest ścianką nośną, przebicie na wylot nie szkodzi.
6. **Półka wkładki nad kanałem przewodów 1,5** (2,5 − 1,0) i **ścianki skrzynki gniazda 2** (ściana 2,5) — nienośne, przyjęte.

**Czy można zmienić / co to wymusza.** Zwiększenie luzu jest bezpieczne dla montażu, ale zmniejsza powtarzalność (płytka ±0,4 ≤ ±0,5 wymagane) albo zahaczenie (pokrywka); zmniejszenie poniżej 0,6 wymaga lepszej tolerancji druku. Luz kołnierza i zatrzaski: korpus i blat razem; otwór wkładki i kołek orientacyjny: wkładka; otwór kołka: blat; luz pokrywki: pokrywka; tulejka: tulejka; rowek panelu: korpus.

## Czego nie ma w ramce i dlaczego

| Element | Dlaczego zrezygnowano | Co jest zamiast |
|---|---|---|
| Przycisk arkadowy z przodu i zaślepka otworu | decyzja właściciela: mniej części i otworów w pyle, identyczne obudowy; stan ramki widać na matrycy | skan uruchamia spacja na laptopie; przednia ścianka gładka, tylko napis |
| Czujnik gestu (VL53L1X) i jego głowica | jak wyżej: przepust, kabel, kalibracja i osobny plik za funkcję, którą pełni spacja | spacja na laptopie |
| Wkładki gwintowane mosiężne i grot do wtapiania | uproszczenie montażu; nylon trzyma gwint formowany (≥ 10 cykli), ścianki wokół otworów (bossy ø8, słupek 8 × 6) wystarczają | wkręty formujące gwint w otworach ø2,1 i ø2,5; przewiercić przed pierwszym wkręceniem; przy serwisie nie przekręcać |
| Podstawka (tacka) klawiatury i nalepka z legendą | około 60 cm³ druku bez funkcji, klawiatura ma własne stopki; właściciel nie chce nalepki | klawiatura luzem na stole; legenda w instrukcji programu |
| Rama dyfuzora jako osobna część i 4 bossy pod blatem | panel ustalają 4 dystanse w jego otworach (±0,2) — rama nic nie dodaje; minus plik, bossy, otwory, wkręty, czynność montażu | dystanse M3; dyfuzor w kieszeni blatu dociskany magnesami wkładki |
| Pianki, uszczelki, pasek EPDM wokół okna | decyzja właściciela „[cytat usuniety]”; światło i pył z krawędzi panelu trafiają tylko do wnętrza zamkniętej obudowy | luz kołnierza blatu 0,7 jest celowym wylotem powietrza |
| Uchwyty kabli drukowane i 2 bossy | osobny plik, 4 części, bossy i otwory za funkcję podstawki samoprzylepnej | podstawki opasek 20 × 20 + taśma VHB |
| Daszki nad szczelinami wentylacyjnymi | szczeliny leżą 8 nad parapetem, poziome, 3 wysokie — pył z góry spada obok; daszki to 20 kruchych brył, +2 gabarytu, problem przy wygładzaniu | szczeliny 12 × 3 bez daszków, gabaryt 200 × 200 |
| Żebra dna korpusu; żebro obwodowe pod blatem | dno 3 ugina się pod 0,5 kg poniżej 0,3; żebro blatu kolidowało z ramą dyfuzora, sztywność daje kołnierz 10 | płaskie dno 3; kołnierz 10 × 2 |
| Szczelina karty SD w dnie | karta wyjmowana raz na rok; szczelina była jedynym wlotem pyłu do elektroniki od dołu | karta po zdjęciu blatu i panelu; obraz systemu przez sieć |
| Otwory ø4 w wierzchu pokrywki; napis „GÓRA” | pył wpadałby na prace; kondensacja w minutach nie występuje; relief na wierzchu drukowanym w dół wymagałby podpór, a góra jest oczywista | wierzch pełny 2 mm |
| Napis „PRZÓD” na wkładce | litery 2 mm nie dają trzonu ≥ 1,0 — nieczytelne; orientację wymusza kołek | strzałki ▼ 2 × 3 na przednim boku |
| Gniazda stopek w dnie | wgłębienie 0,5 nie trzyma lepiej niż klej, przeszkadza przy wygładzaniu | stopki samoprzylepne na płaskim dnie |
| Pogłębienia pod łby wkrętów panelu od spodu | łeb z podkładką 2,5 mieści się pod stopkami 4; pogłębienie osłabiało dno | rowek 3,6 w pełnym dnie 3 |
| Zaokrąglone naroża okna gniazda, kieszeni dyfuzora i otworu wkładki; fazowanie rogów pleksi | osobne profile bez zysku; ostre naroże zwalnia z fazowania pleksi; płytka R 1 z luzem 0,4 nie dotyka narożnika | naroża ostre |
| 20 szczelin wylotowych i wloty 20 × 3 | 10 szczelin (360 mm²) plus luz blatu wystarcza dla 10–13 W; wlot był wąskim gardłem | 4 + 3 + 3 szczeliny, wloty 2 × 30 × 4 |
| Przewody wkładki przyklejane zamiast kanałów | przewód pod płasko leżącą ramą podniósłby wkładkę o 1 | kanał pod półką 2,5 × 1,0 + jedna bryła przelot‑rowek 2,5 × 1,5 |
| Druk z żywicy (tulejka, podkładki, prototypy, płytki jako alternatywa) | decyzja właściciela: albo zlecamy, albo drukujemy sami na FDM | PETG FDM u kolegi; płytki tylko PA12 z drukarni |
| Płytka ze szkła lub z przezroczystego tworzywa | przezroczystość nic nie daje: diody świecą przez otwór ø3 w dnie każdego gniazda, a skaner potrzebuje matowej bieli; szkło nie da się drukować z gniazdami stożkowymi, dołkami kodu i wycięciem | PA12 naturalny biały z drukarni, mat, otwory ø3 w dnach gniazd |
| Wysięgnik z projektorem do wskazywania prac | duży, wymaga ostrości, cierpi na paralaksę, słabo widoczny w dziennym świetle | diody matrycy pod gniazdami przez otwór ø3 |
| NFC/RFID do rozpoznawania płytki | antena nie mieści się pod płytką bez zasłaniania diod; dodatkowy moduł, kabel, biblioteka | 3 magnesy + 3 czujniki Halla; dołki kodu widoczne w skanie |
| Śruby na wierzchu blatu; wkręty od spodu | widoczne i wymagają wkrętaka przy każdej regulacji; od spodu wymagałyby słupków 55 | 4 zatrzaski + 2 wkręty M3 × 8 przez tylną ścianę |
| Dystans wkręcany w gwint panelu od góry; nakrętka lub nitonakrętka od strony diod | nie działa bez gwintu; nakrętka wystawałaby ku dyfuzorowi | dystans F‑F 50 + wkręt dociskowy M3 × 5, albo tulejka klejona ø5 × 5 + dystans 45 |
| Ramka adaptera gniazda USB | kolejna część zależna od modelu gniazda | okno 16 × 9 + rowki 23–28; wiercenie przy flanszy pionowej |
| Siatka otworów pod różne wzory panelu; szyny panelu | dno 3 z 12 pogłębieniami, a wzorów i tak nie znamy; szyny to 2 części i stałe otwory | rowki 110–130 po przekątnej + wiercenie ø4 awaryjnie |
| Gniazdo zasilania w licu tylnej ściany; kieszeń głębsza 30 z gniazdem osią Y | wtyk wystawałby 12–15 za obrys i wyłamywał gniazdo w szafce; głębsza kieszeń wpychała gniazdo w dystans panelu | kieszeń 51 × 24 × 22 z gniazdem w bocznej ścianie skrzynki, osią X |
| Wariant niski obudowy 200 × 270 × 40 | +35 % miejsca na parapecie, dłuższa taśma, dodatkowa przegroda, realnie 41 wysokości | wariant wysoki 200 × 200 × 63,6 |
| Płytka okrągła jako jedyny kształt; mniejszy kwadrat ~76 | ta sama pojemność w kole r 47, a okrągła wymaga nowej wkładki i nowych pokrywek (zmiana R58) | kwadrat 96 z gniazdami w kole pasuje do ramki; okrągła ø100 jest drugim kształtem, tylko do skanera [R57], a właściciel skłania się ku jej zamówieniu [R59] |
| Gniazda ø9 w płytce wieczornej, ø7,5 i ø10 w porannej [R59] | w próbie 17 projektów w ø9 i ø7,5 nie weszła żadna praca (0 z 17; próba mała, dobrana do testów programu); właściciel wybrał układ z samych większych gniazd | wieczorna 6 × ø12 i 12 × ø15; poranna 20 × ø12,5 i 3 × ø15 |
| Druga rynienka na płytce [R59] | decyzja właściciela: jej miejsce zajęły większe gniazda; tylna rynienka płytki porannej była najciaśniejszym miejscem układu (0,07 od granicy koła) | jedna rynienka z przodu, czyli jeden most na płytkę; dwa mosty na płytce dopiero po zmianie programu |
| Rynienka podzielona na dwie krótkie [R59] | krótka rynienka przyjęła w próbie 3 z 6 długich prac i wymaga zmiany generatora (po 2 otwory zamiast 4) | jedna długa rynienka 60 × 15 / 50 × 13 |
| Jeden plik korpusu bez napisu | właściciel zostawił napis: W i P mają być rozpoznawalne bez włączania | 2 pliki korpusu różniące się napisem |

## Jak przeprowadzić zmianę

Każda zmiana konstrukcji przebiega tą samą drogą:

1. Nowa wartość klucza w `parametry.json` (ze statusem `ZALOZENIE`, albo `ZMIERZONE` po pomiarze). Żadnej ręcznej edycji STL.
2. `ramka_generator.py` w Blenderze przebudowuje wszystkie części z pliku parametrów (polecenie w `wyniki_v2/README.md`, etap `ALL`); skrypt nie ma własnych liczb, odrzuca nieznane i brakujące klucze, a klucze liczone wylicza sam i porównuje z plikiem.
3. Pełna weryfikacja według `protokol_weryfikacji_v2.md`, sprawdzenia K‑01…K‑60 (gabaryty, pasowania, ścianki, kolizje w złożeniu), także dla części, które „nie powinny się zmienić” — porównanie sum SHA‑256 pokazuje, które STL naprawdę się zmieniły.
4. Nowe sumy SHA‑256, nowy arkusz zamówienia (objętości, ilości, materiały) i nowa kopia pakietu plików.

Zasada: kluczy `LICZONE` nie edytuje się ręcznie — wysokość korpusu, wierzch blatu, spód panelu, długość dystansu, prześwit pokrywki, położenia kieszeni zatrzasków, haczyków, wkrętów blatu i napisu, promień koła gniazd; zmienia się ich składniki, a skrypt zgłasza błąd, gdy wartość w pliku nie zgadza się ze wzorem. Klucze `ZALOZENIE` to wybory projektowe do zmiany jedną liczbą. Klucze `DO_ZMIERZENIA` to wymiary kupnego sprzętu z wartością domyślną (panel, stos Pi, wtyk Bonnetu, gniazda, odbiornik).

Uwaga: po zamówieniu korpusu pomiary stosu Pi, spodu panelu i diod nie mogą zmienić 54 / 59,6 / 63,6 — wpisuje się je do brył zastępczych w modelu złożenia, a różnice wyrównuje dobór dystansu i podkładek; zapas nad stosem Pi jest wtedy wielkością wynikową i ma zostać ≥ 3. Jedynym pomiarem przed zamówieniem płytek, wkładek i pokrywek jest pole skanowania (makieta z okręgami ø90 / 94 / 100).

**Bezpieczne bez ruszania pozostałych części** (jeden plik lub żaden): napis korpusu, ilości i materiały (tylko arkusz), numery płytek, układ gniazd w kole r 47 (płytki + kalibracja + plik układu w programie; tak przeszła zmiana R59), szczeliny wentylacyjne i położenie Pi (korpus), otwór tulejki, grubości podkładek, wysokość pokrywki przez najwyższą pracę, zasilacz, klawiatura, stopki, podstawki kabli, czujnik TO‑92 innego typu (nic w plikach).

**Pociąga łańcuch** (kilka plików i kupne części): każdy składnik wysokości → korpus i długość dystansów; panel innego PCB → korpus, blat, dyfuzor, zwykle bok korpusu; pole skanowania → płytki, a poniżej ø94 także wkładka i pokrywka; bok płytki → płytki, wkładka, pokrywka; grubość ścian → korpus i blat razem z głębokością kieszeni zatrzasku; luzy pasowań → obie części pasowania; magnes innej średnicy → płytki, wkładka, blat.
