# Raport recenzenta - R58 (komplet okragly do ramki), runda 1

Data: 2026-11-19. Recenzowany stan: commit `f429605` wzgledem `f08136e` (galaz `r58/plytki-okragle-ramka`), 10 STL R58 w `Ramki/wyniki_v2/stl/` worktree (poza gitem), 2 JSON ukladow, `parametry.json`, `plan_ramki_v2.md`, `protokol_weryfikacji_v2.md`, `R58_wdrozenie_zmiany.md`, raporty wykonawcy R58_iter4, R58_SPRAWDZ_iter3, SPRAWDZ_iter15.
Metoda: wlasny kod (numpy, bez Blendera i bez funkcji generatora) w `recenzja/r58_runda1/` - `siatka.py` (wczytanie binarnego STL, topologia, objetosc, promienie Moller-Trumbore, parzystosc), `rastr.py` (mapy wysokosci przez rasteryzacje trojkatow, krok 0,1), `kolizje.py` (przeciecia krawedz-trojkat w siatce przestrzennej), skrypty `r1...r24` (czesc wynikow w `log_*.txt` tamze; mapy `*.npy` usuniete po pomiarze - odtwarzalne skryptami r2, r3, r7, r8). Wszystko liczone na MSI (PC nie byl potrzebny).

## 0. Werdykt

**Do zamowienia po poprawkach** - obecne pliki NIE sa do zamowienia: kolek klucza wkladki wchodzi w pusta kieszen magnesu plytki, wiec kazda plytka n1...n6 lezy plasko we wkladce takze w co najmniej jednym zlym obrocie (90 / 180 / 270 st.) i ramka czyta wtedy zly numer (B1); po poprawce geometrii trzeba powtorzyc pasowania (K-67) i recenzje tej zmiany.

Uwagi: **B 1 / P 3 / D 8**.

Poza B1 wszystkie wymiary z planu 4.1b / 4.2a / 4.6a zmierzone z siatek sa zgodne (tabela w sekcji 2), siatki szczelne, sumy SHA zgodne, stare 25 plikow bez zmian.

## 1. Uwagi

### B1 - Klucz nie dziala: kolek o3 x 2 wchodzi w PUSTA kieszen magnesu o5,2 x 2,2 - plytka lezy plasko w zlym obrocie, ramka czyta zly numer

- Gdzie: `parametry.json` `round_key_pin_d` 3,0 / `round_key_pin_h` 2,0 / `round_magnet_r` 45 / `magnet_pocket_d` 5,2 / `magnet_pocket_depth` 2,2; `ramka_generator.py` `sprawdz_pasowania_R58` (proba "plytka obrocona" tylko bez przesuniecia); `plan_ramki_v2.md` 4.1b p. 3 ("Plytka obrocona o 90/180/270 st. nie wchodzi (sciecie wkladki i kolek)"), 4.11 wiersz "Plytka okragla we wkladce okraglej" ("obrot o 90/180/270 st. blokuje sciecie i kolek"); `narzedzia/studium_R58.py` w. 116-121 ("blokada zgrubna obrotu").
- Dowod (z siatek):
  1. Kolek klucza (os D, r 45, o3,000, wierzch Z 4,500 = 2,0 nad polka) i kieszenie magnesow (osie A/B/C, r 45,000, o5,196, glebokosc 2,200) leza na TYM SAMYM promieniu i co 90 st. Po obrocie plytki o 90 / 180 / 270 st. kieszen A / B / C trafia nad kolek; kolek (2,0) jest nizszy niz kieszen (2,2), a promien kieszeni minus promien kolka = 1,098.
  2. Sciecie nie blokuje obrotu: wnikanie obrysu plytki w sciecie wkladki 50,000 - 49,756 = 0,244 mm jest mniejsze od luzu promieniowego 0,397 - plytka obrocona przesuwa sie o 0,25...0,4 od sciecia i miesci sie w otworze. Rachunek w studium i w K-67 zaklada plytke wyposrodkowana.
  3. Proba 3D (przeciecia krawedz-trojkat obu siatek, plytka podniesiona o 0,002 nad polke, `r12_zle_polozenie.py`): plytka bazowa wieczorna i poranna obrocona o 90, 180 i 270 st. i przesunieta o 0,30 od sciecia (dx -0,212, dy +0,212) - **0 przeciec** (6 z 6 ulozen). Kontrole czulosci tej samej metody: obrot 90 st. bez przesuniecia 56 / 9 przeciec (to, co K-67 raportuje jako "nie wchodzi"), obrot 45 / 135 st. z przesunieciem 2-6 / 76 (kolek pod pelnym spodem), 91,5 st. 27 / 31, plytka opuszczona 0,05 w polke 1153 / 1208.
  4. Okno chwytu: rachunek z wymiarow zmierzonych (`r15_zle_polozenie_analiza.py`) - kolek wchodzi w pusta kieszen dla obrotu 88,3...91,7 / 178,3...181,7 / 268,3...271,7 st. (+-1,7 st.; promien kieszeni - promien kolka 1,098 + przesuniecie styczne do 0,31). Wlasciwy rowek lapie tylko -0,85...+0,85 st. (luz 0,3 na strone + przesuniecie); niezaleznie potwierdzone drugim skryptem `r24_okna.py`. Uzytkownik obracajacy plytke "az wpadnie" ma WIEKSZE okno na zla kieszen niz na rowek.
  5. Kazda plytka n1...n6 ma 1-2 puste kieszenie (magnes tylko w kieszeniach bitow), wiec kazda ma zle plaskie ulozenie. Odczyt ramki (kieszen z magnesem po obrocie trafia nad inny czujnik; czujniki A 225, B 135, C 45 st.; wynik `r15` dla kazdego n, kieszenie z magnesem traktowane jako pelne):
     - n1 (magnes A): obrot 180 -> ramka czyta n4; obrot 270 -> n2;
     - n2 (B): 90 -> n1; 270 -> n4;
     - n3 (A+B): 270 -> n6;
     - n4 (C): 90 -> n2; 180 -> n1;
     - n5 (A+C): 180 -> n5 (numer ten sam, ale plytka obrocona o 180 st. - gniazda pod innymi diodami);
     - n6 (B+C): 90 -> n3.
     Plytka lezy plasko na wystepie i polkach, magnesy sa nad czujnikami w odleglosci nominalnej - odczyt jest pewny, a numer i typ (wieczorna/poranna) zly; ramka swieci gniazda innego ukladu.
  6. Kwadrat nie mial tej wady: kolek 4,4 x 4,4 x 5 nie miesci sie w kieszeni o5,2 x 2,2 (przekatna 6,2 > 5,2, wysokosc 5 > 2,2), a kwadrat ma tylko 4 polozenia.
- Skutek: blad odczytu numeru plytki przy normalnej obsludze (plytka okragla zacheca do obracania), niewykryty przez program; zamowione 6 plytek + 3 wkladki (325...579 zl) z wadliwym kluczem.
- Proponowana poprawka (do wyboru, kazda wymaga przebudowy i ponownego K-67; liczby do sprawdzenia generatorem):
  a) najprostsza w geometrii: w plikach n1...n6 ciac TYLKO kieszenie bitow (n1: A; n2: B; n3: A, B; n4: C; n5: A, C; n6: B, C); plik bazowy bez zmian. Wtedy w kazdym zlym obrocie kolek trafia albo w pelny spod, albo w kieszen z magnesem (wolne 0,2 < 2,0) - plytka nie lezy plasko. Zmienia JSON (kieszenie per numer albo pole `magnet_pockets` z bitami) i K-11/K-64(a);
  b) albo kolek, ktory nie miesci sie w kieszeni: kolek o5,8 (rowek `round_key_slot_w` 6,4) albo kolek wydluzony promieniowo 3,0 x 6,0 (rowek od r0 41,5) - sprawdzic scianke rowka do rynienki wieczornej (dzis 0,37 w poziomie);
  c) albo kolek poza promieniem kieszeni: |r_kolka - 45| >= 2,0 (np. kolek na r 42,5, `round_key_slot_r0` 40,5) - kieszen nie obejmie kolka nawet przy luzie 0,4;
  d) minimum organizacyjne (bez zmiany STL, swiadoma decyzja wlasciciela): kazda pusta kieszen zalepiona krazkiem niemagnetycznym o5 x 2,0 (PETG) - zapis w `kody_plytek.md`; zostaje wtedy tylko przechyl z P1.
  Dodatkowo: K-67 "plytka obrocona" liczyc z przeszukaniem przesuniecia w kole luzu (co najmniej 0,05 krok, |d| <= luz) i dla kazdego wariantu n osobno (kieszenie z magnesem = pelne); poprawic zdania w 4.1b, 4.11, D5 i w studium.

### P1 - Plytka "prawie dobrze" lezy krzywo na kolku, a ramka nadal czyta magnesy

- Gdzie: `round_key_pin_h` 2,0, `round_key_pin_chamfer` 0,5, `round_key_slot_w` 3,6; plan 4.1b p. 3.
- Dowod: poza oknem rowka (+-0,85 st. bez fazy; z faza kolka 0,5 ok. +-1,5 st.) i poza oknami z B1 plytka obrocona o dowolny kat miesci sie w otworze (B1 p. 2) i lezy na wierzcholku kolka: podniesienie 2,0 przy kolku (1,8 nad kieszenia z magnesem), przechyl atan(2,0 / 94,7) = 1,2 st., krawedz plytki przy kolku +2,1 mm, czujniki A i C +1,05 mm (magnes-czujnik ok. 2,75 mm), B +0,1 mm. Wg D5 (prog A3144 przy 4 mm) magnesy nadal sa wykrywane -> ramka czyta numer, a plytka jest obrocona. W kwadracie zle ulozenie podnosilo naroznik o 5 mm (kolek 5) i bylo oczywiste.
- Proponowana poprawka / decyzja: (1) przyjac swiadomie (plytka wystaje 6,6 zamiast 4,5 nad rame i sie kolysze) albo (2) zwiekszyc faze kolka do 1,0 x 45 st. (wierzcholek o1,0) - samoczynne naprowadzenie do ok. +-2 st. (dzis ok. +-1,5 st.; uwaga: faza poszerza tez okno zlej kieszeni z B1, wiec tylko razem z poprawka B1), oraz w programie ramki ostrzezenie, gdy numer nie pasuje do roli ramki (n1-n3 na ramce P, n4-n6 na W - dzis typ wynika z numeru). Wysokosci kolka nie da sie zwiekszyc bez zlamania scianki 1,5 nad rowkiem (sufit rowka - dno gniazd).

### P2 - Zatrzask pokrywki okraglej niesprawdzony; owalizacja kubka blokowana przez plytke

- Gdzie: `ramka_pokrywka_okragla_v2.stl`, `round_cover_snap_angles` [25, 155, 205, 335], `cover_snap_bump` 0,7, plan 4.2a ("Sila zatrzasku do sprawdzenia na pierwszym wydruku").
- Dowod: garb (wystep 0,700, Z -18, luk 11 st.) musi przejsc nad krawedzia plytki r 50,000 przy licu r 50,300 - wcisk 0,40 mm na kazdym garbie. Przy garbach parami przy osi X owalizacja (n = 2) wymagalaby w0 = 0,40 / cos 50 st. = 0,62 mm, czyli zejscia scianki przy +-90 st. o 0,62 do srodka; tam luz do plytki jest 0,30 (pas Z -17...-16 nad wycieciami palcowymi i faza plytki). Zostaje lokalne odgiecie scianki walca 1,5 (sztywniejsze niz plaski bok kwadratu). Nie ma obliczenia ani proby.
- Skutek: pokrywki moze nie dac sie zalozyc albo garb sie scina (PETG). Nie wplywa na zamowienie PA12 (pokrywka to druk wlasny, poprawka tylko w pokrywce).
- Proponowana poprawka: przed drukiem 4 sztuk wydrukowac 1 i sprawdzic na plytce; jesli za sztywno - dwie szczeliny 1,0 x 10 od dolnej krawedzi po obu stronach kazdego garbu (jezyczek ok. 14 mm). Przy okazji: FDM PETG zwykle zaniza otwor o 0,2...0,3 na srednicy - luz 0,3/strone moze spasc do ok. 0,15 (jak przy tulejce R55: skala XY w slicerze).

### P3 - Przebieg `--etap A/B/C/ALL` kasuje 10 STL kompletu R58 i ich nie odtwarza

- Gdzie: `ramka_generator.py` `main` -> `wyczysc_wyniki(out)` (usuwa wszystkie pliki z `wyniki_v2/stl`), `etap_R58` wolany tylko z `main_R58`; `R58_wdrozenie_zmiany.md` 8 ("takze przyszly przebieg ALL zbuduje pliki etapow A-C tak jak dotad") i 12 p. 2 (planowany przebieg ALL koordynatora).
- Dowod: `wyczysc_wyniki` (w. ok. 5181) kasuje pliki w `stl/`, a TYPY_PLYTEK_R58, wkladka i pokrywka okragla nie sa w ETAPY. `ramka_wkladka_okragla_v2.stl` nie odtwarza sie bajtowo (wariant 9187827b... w 1 z 4 przebiegow).
- Skutek: po zapowiedzianym przebiegu ALL plikow do zamowienia nie bedzie, a przebudowa moze dac inna wkladke niz zrecenzowana.
- Proponowana poprawka: przed jakimkolwiek przebiegiem A/B/C/ALL zabezpieczyc 10 STL (kopia + SHA z `sha256_stl_po_R58.txt`) albo dopisac do `wyczysc_wyniki` pomijanie plikow `*_okragla_ramkowa_*`, `*_wkladka_okragla_*`, `*_pokrywka_okragla_*`; do zamowienia brac wylacznie pliki o SHA z `R58_wdrozenie_zmiany.md`.

### D (drobne / dokumentacja)

- D1 `zrzut_parametrow_zgodny` (K-60): wyjatek jest waski, ale przepuszcza zrzut, w ktorym czesc kluczy R58 jest z BLEDNA wartoscia, jesli brakuje choc jednego klucza R58 (`bez_r58` usuwa klucze R58 z obu stron). Poprawka: zgodny tylko gdy w zrzucie nie ma ZADNEGO klucza z KLUCZE_R58 (`brak` = wszystkie klucze R58 z `parametry.json`). Innych roznic wyjatek nie maskuje.
- D2 K-64 (d) i K-67 "kolnierz": scianki pionowe (sufit kieszeni / rowka - dno gniazd, stozek - kieszen) to stale z parametrow (8 - 4 - 2,2 itd.), a kolnierz to jeden punkt (0; 51,5) - te pozycje przechodza zawsze przy niezmienionych parametrach. Moje pomiary z siatek (sekcja 2) je potwierdzaja (np. sufit kieszeni - najblizsza powierzchnia wewnetrzna >= 2,078; sufit rowka klucza >= 1,73; pod kolnierzem max Z wkladki 6,000 w calym pierscieniu r 50,25...51,85).
- D3 Plan 4.1b / K-64: "dno rowka pokrywki - obrysy na Z -1,5: 3,52 / 3,19" to odleglosc pozioma do obrysu; najmniejsza scianka 3D z dna rowka do wnetrza (promienie do +-30 st. elewacji) wynosi 2,915 (wieczorna) / 2,884 (poranna) - nadal >= 1,5; uscislic opis.
- D4 Rowek pokrywki przechodzi przez sciecie z glebokoscia 0,156 w srodku cieciwy - ponizej rozdzielczosci MJF (detal < 0,8), w praktyce zaniknie; nieszkodliwe (garb nad scieciem i tak nie trzyma), ale moze wyjsc jako nierowny pasek - informacja dla drukarni ("nie wygladzac sciecia").
- D5 Program: `stanowisko/ramka/kalibracja.py` w. 33 i 73 pomija uklady z `shape` != "square" i `plate` spoza {"wieczorna", "poranna"} - JSON R58 (`okragla_ramkowa_*`) nie dostanie kalibracji startowej. Poniewaz `sockets` = kwadrat tego typu, a srodek otworu wkladki okraglej = srodek kwadratowej (obrys identyczny, zmierzone), ramka moze uzyc kalibracji kwadratu po numerze - do zapisania w paczce programu (ryzyko 3 wykonawcy).
- D6 Montaz czujnika: kanal wychodzi z naroza kieszeni 5,0 x 5,5 po przekatnej; A3144 (obudowa ok. 4,1 x 3,0) obrocony o 45 st. potrzebuje 5,0 x 5,0 - nie zmiesci sie (5,0 w X), wiec wyprowadzenia trzeba zagiac o 45 st. przy obudowie - tak samo jak we wkladce kwadratowej; kanal do naroza jest dluzszy o ok. 14 mm (29 zamiast 15) - przewody wiazki dla wkladki okraglej dluzsze. Dopisac do instrukcji budowy.
- D7 Stara plytka okragla n8/n9 we wkladce okraglej: miesci sie w otworze, lezy na kolku (przechyl jak P1), ramka czyta 0 (brak magnesow) - poprawnie "brak plytki". Plytka kwadratowa: nie wchodzi w otwor w zadnym obrocie (polprzekatna ok. 67 > 50,4), lezy na ramie (Z 6,0), magnesy na r 59,4 poza czujnikami (r 45) - odczyt 0 (rachunek z wymiarow, bez proby 3D). Plytka ramkowa w starej wkladce kwadratowej: o100 > 96,8, nie wchodzi. Informacyjnie.
- D8 Arkusz zamowienia, `kody_plytek.md` (z instrukcja bieguna dla kieszeni na r 45), `arkusz_wymiarow.md` bez kompletu R58 (odstepstwa 2 i 5) - przed zamowieniem potrzebny arkusz z 7 pozycjami R58.

## 2. Wymiary - plan / zmierzone (siatki STL, uklady z protokolu: plytka wierzch Z 0; wkladka spod ramy Z 0; pokrywka wierzch Z 0)

| Wymiar | Plan / parametry | Zmierzone (recenzent) | Zgodne |
|---|---|---|---|
| Plytki: szczelnosc, rozmaitosc | kazda krawedz w 2 trojkatach, przeciwne zwroty | 8/8 plytek: krawedzi != 2: 0, zdublowanych zwrotow 0, trojkatow zdegenerowanych 0, przeciec wlasnych 0, normalne zapisane = kolejnosc wierzcholkow, 1 skladowa; genus 22 / 27 = liczba otworow (18 + 4 / 23 + 4) | tak |
| Objetosc plytek [cm3] | 48,90 / 48,91 / 49,19 / 49,20 | 48,8989; n1 48,9133; n2 48,9142; n3 48,9114 / 49,1865; n4 49,2014; n5 49,1993; n6 49,1984 | tak |
| Gabaryt plytek | 100 x 100 x 8 (n: 8,6) | 100,000 x 100,000 x 8,000 / 8,600 | tak |
| Obrys o100 | R 50 +-0,05 | 49,996...50,000 (Z -1, -3, -4, -7,5, -7,95; 720 kierunkow) | tak |
| Faza wierzchu 0,5 | r 49,75 na Z -0,25 | 49,746...49,750 | tak |
| Sciecie | 49,356 na -45 st., cieciwa 16 | 49,356 (Z -0,25...-7,5; na Z -7,5 przy v +-2,5...+-6); sektor 306...324 st. | tak |
| Rowek pokrywki | 1,0 x 0,8, srodek Z -2, caly obwod | dno r 49,196...49,200 (Z -1,55 / -2 / -2,45, 720 kier.), gora Z -1,500, dol Z -2,500; w scieciu dno 49,200, Z -1,5...-2,5, glebokosc 0,156 | tak |
| Kieszenie magnesow - osie | A (-31,82; -31,82), B (-31,82; 31,82), C (31,82; 31,82), r 45 | (-31,8198; -31,8198), (-31,8198; 31,8198), (31,8198; 31,8198); r 45,000; katy 225 / 135 / 45 | tak |
| Kieszenie - srednica / glebokosc | 5,2 / 2,2 | 5,196 (wielobok 5,194...5,200) przy wejsciu i suficie / 2,200 | tak |
| Kieszen - krawedz plytki | 2,4 | 2,402 | tak |
| Rowek klucza | 3,6 x 2,5 od r 43, os -45 st., przez krawedz i sciecie | 3,600 (os przesunieta 0,000) na u 43,5...49; wys. 2,500; r0 43,000; wychodzi przez sciecie | tak |
| Dolki = bity | n1 A, n2 B, n3 A+B, n4 C, n5 A+C, n6 B+C; bazowe A+B+C+D | mapa wierzchu: zapelnione dokladnie dolki pozostalych bitow i D; bazowe wszystkie 4 | tak |
| Cyfra | n w (35; -26,5) / (-44; 5,5), relief 0,6 | 1...6 czytelne (mapa 0,1), max Z 0,600; relief n1 = relief kwadratowej n1 (3276 / 3272 pikseli przy kroku 0,05, 4 rozne); obszar x 33,3...36,7 y -29,0...-24,0 / x -45,8...-42,2 y 3,0...7,9 | tak |
| Wierzch = plytka okragla R59 | identyczny poza dolkami i cyfra | bazowe: 769 162 / 765 666 pkt, rozbieznosci trafien 0, max dz 0,0000; warianty: roznice tylko w 3 dolkach i obszarze cyfry | tak |
| Spod = plytka okragla R59 + cechy | tylko kieszenie i rowek klucza | roznice wylacznie w 3 kieszeniach i rowku klucza (0 punktow poza nimi) | tak |
| Scianka: sufit kieszeni - wnetrze | >= 1,8 (rachunek) | min 2,078 (wieczorna A, do dna gniazda Z -4), poranna 2,975 | tak |
| Scianka: stozek znacznika - kieszen | 2,8 (pion) | wieczorna B 2,899, poranna A 2,975 | tak |
| Scianka: sufit rowka klucza - wnetrze | 1,5 (pion), 1,54 po przekatnej do rynienki | min 1,73 (wieczorna, promien 60 st.; probkowanie co 15 st.), poranna 5,59 | tak (>= 1,5) |
| Scianka: boki rowka klucza - wnetrze | - | 1,905 / 5,103 | tak |
| Scianka: boki kieszeni - wnetrze | >= 7,48 do o3 w rzucie | 3,38 (3D, do stozka) / 3,73 | tak |
| Scianka: dno rowka pokrywki - wnetrze | 3,52 / 3,19 (poziomo) | 2,915 / 2,884 (3D) - patrz D3 | tak (>= 1,5) |
| Wkladka: szczelnosc, objetosc, gabaryt | 22,42; 130 x 148,4 x 10,1 | 0 bledow topologii, przeciec wlasnych 0, normalne zgodne, 1 skladowa; 22,4198; 130,000 x 148,400 x 10,100 | tak |
| Otwor wkladki | o100,8 | r 50,397...50,400 (Z 2,6...4,95) | tak |
| Sciecie wkladki | 49,756 | 49,756 (Z 2,6...4,95, v -4...4); sektor 306...324 st. | tak |
| Faza otworu 1 x 45 | r 50,4 -> 51,4 na Z 5...6 | Z 5,25: 50,65; 5,5: 50,90; 5,9: 51,30 (tez na scieciu) | tak |
| Wystep | r 47, Z 0...2,5 | r 46,997...47,000 (Z 0,3 / 1,25 / 2,3); wierzch 2,500 | tak |
| Polki 10 x 10 | srodki w osiach A-D, boki | boki wewn. +-26,820 (= 31,82 - 5); wierzch 2,500 | tak |
| Kieszenie Halla | 5,0 x 5,5 przelotowe w osiach A/B/C | 5,000 x 5,500, srodki = osie (0,000), przelotowe | tak |
| Kolek klucza | o3,0 x 2,0, faza 0,5, os D | srodek (31,8198; -31,8198), o3,000 (wielobok 2,99), wierzch Z 4,500, faza: r 1,0 na 4,45-4,5; brak kolka kwadratowego | tak |
| Scianka ramy w osiach | 2,0 | 2,001...2,003 (+X, +Y, -X) | tak |
| Dno w osi po rowku kablowym | 2,9 | 2,903 | tak |
| Kanaly Halla | 2,5 x 1,0 pod polka, 2,5 x 1,5 do naroza, ciagle | szer. 2,5; sufit 1,0 (do r 50,4), 1,5 (do naroza); A, B, C dochodza do szczeliny przy uchu (+-64; 89) przy suficie >= 0,9 | tak |
| Wyciecie palcowe | 30 | 30,000 (y -48,7 / -50,5 / -52; Z 1,25 i 4) | tak |
| K-56 | 0 | 0 wierzcholkow | tak |
| Interfejs do blatu = wkladka kwadratowa | identyczny poza otworem | mapy z gory i od spodu 132 x 151 mm krok 0,1: 0 roznic poza |x|, |y| > 51,3 (uszy, kolki, magnesy, rowek kablowy, obrys); roznice tylko w ramie/otworze i naroznych przelotach (1,0 -> 1,5) | tak |
| Pokrywka: srednice, wysokosc, wierzch | 100,6 / 103,6; 20; 2 | 100,593...100,600 / 103,592...103,600; Z -20...0; spod wierzchu Z -2,000; topologia 0 bledow, przeciec wlasnych 0, normalne zgodne; 25,2621 cm3 | tak |
| Garby | 25/155/205/335 st., 0,7, Z -18, luk 10 | sektory o srodkach 25,00 / 155,00 / 205,00 / 335,00, luk 11,0 st. (9,7 mm), wystep 0,700, Z -18,39...-17,61 na r 49,95 | tak |
| Wyciecia palcowe pokrywki | 30 x 3 przod i tyl | 30,000 x 3,000 (gora Z -17), os x 0,000, +-17,35 st. na r 50,3 | tak |
| Luz plytka - otwor | 0,4 | 0,397...0,400 (720 kier., bez wyciecia), w osi sciecia 0,400 | tak |
| Spod plytki na polce | 2,5 = 2,5 | 2,500 / 2,500 | tak |
| Magnes nad czujnikiem | 0 | 0,0000 (A, B, C) | tak |
| Kolek w rowku | 0,3/strone, nad kolkiem 0,5 | 0,304 / 0,304; 0,500; koniec rowka - kolek 0,504 | tak |
| Magnes - czujnik (D5) | 1,7 | spod plytki 2,5, sufit kieszeni 4,7 -> magnes 2,7; czujnik 1,5 -> 1,2 + 0,5 = 1,7 (jak kwadrat) | tak |
| Pokrywka - plytka | 0,3; garb 0,4 w rowku; kolnierz 0,5 nad rama | lico 50,300 - 50,000 = 0,30; czubek 49,600 -> 0,40 w rowek, 0,40 do dna; srodek garbu Z 8,5 = srodek rowka 8,5; max Z wkladki pod kolnierzem 6,000 -> 0,500 (strzalki 6,6 na r >= 58,8 poza kolnierzem) | tak |
| Kolizje w ukladzie nominalnym | 0 | plytka (+0,002) - wkladka 0, plytka - pokrywka 0, wkladka - pokrywka 0 (wieczorna bazowa, poranna n4); kontrole czulosci wykrywaja | tak |
| Otwory o3 - polki / wystep / kolek | >= 3,10 / 5,58-5,34 | 6,97 / 3,10; 5,58 / 5,34; 10,91 / 9,30 | tak |
| Plytka obrocona 90/180/270 st. "nie wchodzi" | plan 4.1b, 4.11 | WCHODZI plasko (0 przeciec) przy przesunieciu 0,3 - B1 | **nie** |
| Sciecie jako blokada obrotu | studium R58 | wnikanie 0,244 < luz 0,397 - nie blokuje | **nie** |

## 3. Kod (`ramka_generator.py`)

- Stare czesci: zmiany we wspolnych funkcjach sa warunkowe (`okragla and uklad.get('cover_groove'/'key_slot')`, nowe nazwy czesci w `M_druk`, `zero_dodatnie=False` domyslnie, K-09 `rogi` puste tylko dla okraglych - dla R57/R59 i tak puste, K-13 nowa galaz tylko dla zmax < -0,02, K-61 (b) / K-63 tylko gdy `key_slot`); listy SONDY_K29 / SONDY_K30 = dawne literaly (porownalem). `raport_wykonawcy_SPRAWDZ_iter15.md` vs `iter12`: 20 linii roznych - tylko naglowek, sumy SHA, nazwy rzutow i dopisek K-60. Nie znalazlem zmiany zachowania etapow A/B/C/SPRAWDZ poza P3 (kasowanie plikow R58 przy budowie).
- `zero_dodatnie`: `x + 0.0` daje +0,0 dla -0,0 (IEEE), pozostale liczby bez zmian; w 10 plikach R58 0 liczb -0,0.
- K-13: poprawka metody sensowna (fallback na promienie z gory, gdy w obszarze cyfry sa tylko wierzcholki cech spodu); brak cyfry w wariancie nadal da NIE.
- K-60: patrz D1.
- K-64...K-67 a "przechodzace zawsze": K-64 (d) czesc scianek i K-67 kolnierz (D2); K-67 "plytka obrocona" mierzy co innego niz deklaruje plan (B1). Pozostale pozycje sa pomiarami na siatkach z tolerancjami z parametrow; zgodne z moimi pomiarami.
- Liczby: wszystkie wymiary R58 w kodzie biora sie z `parametry.json` (14 nowych kluczy + istniejace), poza krokiem map (narzedziowy) i stalymi sond (+-0,15 / 0,2).

## 4. Spojnosc

- `parametry.json` (14 kluczy) = tabele 3.1 / 3.4 / 3.6 planu = protokol 3b = `R58_wdrozenie_zmiany.md` 2 = JSON ukladow (`magnet_pockets` 3 wpisy z `angle_deg`, `cover_groove` {2; 1,0; 0,8}, `key_slot` {-45; 43; 3,6; 2,5}; `sockets` = kwadrat, `markers` i `code_dimples` = okragla R59) = siatki (sekcja 2): tak.
- `quantities_r58` / `materials_r58`: 8 pozycji, wkladka 3, pokrywka 4 PETG - zgodne z dokumentem.
- SHA: 10 STL + 2 JSON = `R58_wdrozenie_zmiany.md` = `sha256_stl_po_R58.txt` (12 / 12). Stare 21 STL (glowne repo) + 4 JSON = sekcja 8 dokumentu = `SHA256SUMS_2026-11-16_R59.txt` (25 / 25; jedyna pozycja SUMS bez pliku to kopia `03_Druk_wlasny/..._TEST_SKANERA.stl` z hashem n1 - poza zakresem). `git diff f08136e f429605 -- Ramki/wyniki_v2/json`: tylko 2 nowe pliki.

## 5. Projekt (ocena konstruktora) - poza B1/P1-P3

- Drukowalnosc MJF/SLS: najmniejsze scianki z siatek >= 1,73 (plytka), 2,0 (rama wkladki w osiach, L z wystepem 3,4 x 2,5), 1,5 (polka nad kanalem); wszystkie wneki otwarte (kieszenie i rowek klucza od spodu, kanaly od spodu, rowek pokrywki z boku) - odpylenie bez problemu; jedyny detal < 0,8: D4. FDM pokrywki jak kwadratowej (garby u gory wydruku).
- Lancuch magnes-czujnik identyczny z kwadratem (polka 2,5, kieszen 2,2) - 1,7 mm.
- Polki i wystep nie zaslaniaja otworow o3 (>= 3,10).
- Korpus, blat, elektronika: bez zmian (obrys wkladki i interfejs identyczne, zmierzone). Program ramki: numer z magnesow dziala bez zmian, kalibracja - D5; B1 dotyczy wlasnie programu (nie odrozni zlego ulozenia).
- Wkladka okragla jest pierscieniem "C" (wyciecie palcowe przez pelna wysokosc z przodu, jak kwadratowa) ze scianka 2,0 na ok. +-11 st. wokol osi X/Y - przy PA12 wystarczy (wystep dodaje przekroj L), ale wkladke wyjmowac za uszy, nie za przod.

## 6. Czego NIE sprawdzilem

- Powtarzalnosci (K-59) - nie uruchamialem generatora ani Blendera; zgodnosc SPRAWDZ_iter15 = iter12 tylko z porownania raportow.
- Sily zatrzasku pokrywki (brak MES; P2 to ocena geometryczna) ani rzeczywistych tolerancji MJF/FDM.
- Pola magnetycznego przy przechyle (P1) - przyjete wg D5 (prog przy 4 mm).
- Wymiarow A3144 - z pamieci katalogowej (obudowa UA ok. 4,1 x 3,0 x 1,5), nie z karty w repo.
- Kolizji 3D wszystkich 8 plytek (zrobione dla wieczornej bazowej i porannej n4; pozostale maja identyczny spod i bok - mapy spodu, wierzchu i promienie obrysu - wiec wynik ten sam).
- Rzutow PNG wykonawcy i raportow R58_iter1-3 (tylko iter4, SPRAWDZ_iter3 / iter15 w zakresie K-67 i K-60).
- Wariantu wkladki `9187827b...` z przebiegu #9 (nie ma go w worktree) - recenzowany jest wylacznie `0ca13cd7...`.
- Plytki kwadratowej i n8/n9 we wkladce okraglej (D7) - tylko rachunek z wymiarow.
- Zachowania programu ramki z plytka okragla (kod tylko czytany: `kalibracja.py`, `sprzet_rpi.py`, `program.py`).