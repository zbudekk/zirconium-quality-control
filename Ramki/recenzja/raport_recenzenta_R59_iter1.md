# Raport recenzenta - etap R59 (subsesja R59-B, recenzja z siatek), iteracja 1

Plik: `recenzja/raport_recenzenta_R59_iter1.md`. Data: 2026-11-14. Stan recenzowany: commit `bc76f9f` ("R59-A: uklad gniazd w parametrach i generatorze").
Przedmiot: 12 plikow STL plytek (4 bazowe, n1-n6, n8, n9) i 4 pliki JSON ukladu z R59-A; zgodnosc z `parametry.json`, decyzjami wlasciciela (G0, 14.11.2026) i protokolem.
Skrypty recenzenta (9, te same pliki dzialaly na PC - SHA-256 worktree = PC, 9 z 9): `recenzja/sprawdz_R59_wspolne.py` (model oczekiwany z `parametry.json`), `sprawdz_R59.py` (pomiar jednej siatki, Blender), `sprawdz_R59_uruchom.py` (12 procesow rownolegle, limit czasu), `sprawdz_R59_liczby.py` (rachunek + JSON + G0), `sprawdz_R59_sha.py`, `sprawdz_R59_K53.py`, `sprawdz_R59_K59.py`, `sprawdz_R59_normalne.py`, `sprawdz_R59_podglad.py`. Log: `recenzja/log_R59_iter1.txt` (8 czesci).

## 0. Werdykt

**ETAP R59 (pliki plytek i JSON ukladu z R59-A): ZALICZONY** - B = 0, P = 0, D = 5.
Wszystkie punkty 1-8 sekcji 8 planu sesji wykonane; dodatkowo K-59 (powtarzalnosc) i dwie kontrole czulosci metody. Sprawdzen z wynikiem NIE: 0 z 475 (384 na 12 siatkach, 53 rachunkowe / JSON / G0, 13 SHA, 12 w zlozeniu K-53, 12 normalnych zapisanych w STL, 1 K-59).

Liczba sond (ostatni przebieg):
- sondy punktowe "w bryle / poza" (parzystosc przeciec w 3 kierunkach): **13 923** (13 901 na 12 plytkach + 22 w zlozeniu K-53), niezgodnych 0, niestabilnych 0;
- promienie pomiarowe (promien gniazda na 3 glebokosciach, dno, otwor, scianka, obrys okragly): **38 170** (38 021 + 149);
- promienie map wierzchu i spodu (krok 0,05 mm, 2041 x 2041 na mape): **199 952 688**, z tego 99 976 344 na 12 nowych siatkach (ocenionych punktow 97 603 446, niezgodnych z modelem 0) i 99 976 344 na 12 starych siatkach z archiwum (kontrola odwrotna);
- K-53: 262 236 punktow (wierzcholki i srodki trojkatow) sprawdzonych "czy w bryle drugiej czesci".

## 1. Niezaleznosc pomiaru

- Sumy SHA-256 sprawdzanych plikow zgodne z raportem wykonawcy i z `R59_wdrozenie_zmiany.md`: **TAK** - 12 / 12 STL plytek, 4 / 4 JSON, 9 / 9 plikow nieplytkowych = `Ramki_pakiet/SHA256SUMS_2026-11-02_R57.txt`; raport wykonawcy sekcja 2: 25 / 25; kopia MSI = PC: 25 / 25; `parametry.json` PC = git HEAD = `8434aafe...`. Archiwum starego ukladu (zrodlo kontroli odwrotnej): 21 / 21 STL = `sha256_stl_przed_R59.txt`, 10 / 10 starych plytek i 4 / 4 stare JSON = SHA256SUMS R57, `parametry_przed_R59` = `b7b52942...` (pakiet R57).
- Skrypt recenzenta napisany bez czytania `ramka_generator.py`: **TAK**. Diff generatora otwarto dopiero po zakonczeniu pomiarow, wylacznie do oceny zleconej w zadaniu (pkt 5 tego raportu). Sekcje 3 raportu wykonawcy przeczytano po pomiarach.
- Wartosci oczekiwane: wylacznie `parametry.json` z git HEAD (rzedy `ev_rows` / `mo_rows`, `ev_/mo_marker_pos`, `code_dimples_round`, `number_pos_round`, klucze geometrii). JSON ukladu byl przedmiotem sprawdzenia (pole po polu wzgledem modelu z parametrow), nie zrodlem.
- Powtarzalnosc (K-59, dodatkowo do planu): przebieg generatora w czystej kopii (`<PC-katalog>\r59\recenzja\powtorka`: 4 pliki z git HEAD, bez `wyniki_v2`, `--etap ALL --bez-renderow`, kod wyjscia 0): **TAK**; STL identyczne bajt w bajt: **20 / 21** (12 / 12 plytek), JSON ukladu 4 / 4; roznica: `ramka_wkladka_v2.stl` (SHA `e363b006...` zamiast `f4196fbc...`) - 1806 / 1806 trojkatow, 0 roznych, objetosc bez roznicy (znana roznica znaku zera normalnych, uwaga D4).
- Kontrola czulosci metody (czy sprawdzenia w ogole potrafia dac NIE): (1) dwa STARE pliki z archiwum zmierzone tym samym skryptem wzgledem nowych parametrow: `poranna_n4` 17 NIE z 31, `okragla_wieczorna_n8` 16 NIE z 30 (w tym oba sprawdzenia odwrotne, spis petli, mapy, K-06...K-09); (2) K-53: plytka przesunieta o 0,6 mm (luz 0,4) i pokrywka opuszczona o 1,0 mm (luz 0,5) - przenikanie wykryte (79 i 368 par przeciec siatek skurczonych).
- Bledy WLASNE skryptow recenzenta poprawione w trakcie (bez zmiany progow i wartosci oczekiwanych): parser tabeli SHA raportu wykonawcy (kolumna rozmiaru), typ calkowity tablicy modelu spodu (strop kieszeni -5,8 obciety do -5), promien scianki dolek A - dolek C przechodzacy przez dolek B, klasyfikacja par stykowych K-53. Kazda dawala falszywe NIE po stronie recenzenta, nie po stronie plikow.

## 2. Wyniki sprawdzen

Uklad pomiaru: tabela 1 protokolu (STL: spod na z = 0, przesuniecie z - 8, srodek XY = 0; zmierzone: spod surowego STL z = 0,0000, srodek XY (0,00000; 0,00000) w 12 / 12 plikach). "Zadeklarowane" = raport wykonawcy R59 iter2 sekcja 3 i `R59_wdrozenie_zmiany.md`.

### 2.1 Punkt 1 - 12 STL: szczelnosc, jedna bryla, normalne, gabaryt, objetosc

| Id | Wynik | Zmierzone przez recenzenta | Zadeklarowane | Oczekiwane | Waga | Uwaga |
|---|---|---|---|---|---|---|
| K-01 | ZAL 12/12 | 18 930...22 576 trojkatow na plik (razem 248 858), NaN 0 | te same liczby trojkatow 12/12 | > 100, bez NaN | B | |
| K-02 | ZAL 12/12 | kwadratowe 96,0000 x 96,0000 x 8,0000 (n1-n6: 8,6000); okragle 100,0000 x 100,0000 x 8,0000 (n8, n9: 8,6000) | to samo | tabela 1 +-0,1 | B | |
| K-03 | ZAL 12/12 | krawedzie o liczbie scian rozne od 2: 0; luzne wierzcholki: 0; przeciecia wlasne (bez sasiadow): 0; krawedzie o niezgodnym zwrocie scian: 0; trojkaty zdegenerowane: 0 | 0 / 0 / 0 | 0 / 0 / 0 | B | |
| K-04 | ZAL 12/12 | 1 skladowa spojna w kazdym pliku (brak zamknietych pustek) | 1 | 1 | B | |
| K-04b | ZAL 12/12 | objetosci dodatnie [cm3]: wieczorna 59,6447 / n1 59,6591 / n2 59,6600 / n3 59,6572; poranna 59,9324 / n4 59,9472 / n5 59,9451 / n6 59,9442; okragla wieczorna 49,3385 / n8 49,3551; okragla poranna 49,6262 / n9 49,6380 | 59,64 / 59,66 / 59,66 / 59,66; 59,93 / 59,95 / 59,95 / 59,94; 49,34 / 49,36; 49,63 / 49,64 | tabela 1 (60 / 60 / 49 / 50) +-30 %; raport +-0,01 | B | max roznica 0,0049 cm3 (zaokraglenie do 0,01) |
| normalne w pliku | ZAL 12/12 | normalne ZAPISANE w STL niezgodne z kolejnoscia wierzcholkow: 0 z 248 858; normalne zerowe 0; rozmiar pliku = 84 + 50 n; bajty atrybutow 0; naglowek pusty | - | zgodne | B | `sprawdz_R59_normalne.py` |

### 2.2 Punkt 2 - kazde gniazdo i rynienka (polozenie, srednice, kat 15 st., glebokosc 4, otwor fi 3)

Metoda glowna: spis petli krawedzi siatki na 5 plaszczyznach (wierzch z = 0, dna gniazd z = -4, spod z = -8, dna dolkow z = -1, stropy kieszeni z = -5,8). Kazda petla musi lezec na obrysie dokladnie jednej cechy oczekiwanej z `parametry.json` (odchylka kazdego wierzcholka <= 0,02 mm), kazda cecha musi miec dokladnie jedna petle. Petla bez cechy = cos wycietego ponad plan; cecha bez petli = brak wyciecia.

| Id | Wynik | Zmierzone przez recenzenta | Zadeklarowane | Oczekiwane | Waga | Uwaga |
|---|---|---|---|---|---|---|
| SPIS petli | ZAL 12/12 | 1280 petli w 12 plikach: 1244 dopasowane do 1244 cech oczekiwanych, 24 obrysy zewnetrzne (wierzch + spod), 12 petli cyfr; **nieoczekiwanych 0, brakujacych 0, zdublowanych 0**; max odchylka wierzcholka od obrysu oczekiwanego 0,0051 mm; max odchylka srodka okregu (dopasowanie) 0,00025 mm | - | kazda petla = jedna cecha | B | wieczorna: 19 gniazd/rynienek + 3 stozki + dolki wg bitow na wierzchu, 19 den + 22 otwory na z = -4, 22 otwory (+ 3 kieszenie) na spodzie; poranna: 24 + 3 + dolki, 24 + 27, 27 (+ 3) |
| srednica gorna | ZAL | promien petli wierzchu = d/2: 6,00000 (fi 12, 6 szt.), 7,50000 (fi 15, 12 szt.) - wieczorna; 6,25000 (fi 12,5, 20 szt.), 7,50000 (fi 15, 3 szt.) - poranna; 151...195 wierzcholkow na okrag | JSON d_top 12 / 15; 12,5 / 15 | `d` z rzedow | B | |
| srednica dolna, kat | ZAL | promien petli dna 4,93 / 6,43 (wieczorna), 5,18 / 6,43 (poranna) = d_bottom 9,86 / 12,86 / 10,36; kat scianki z petli 14,976 st. we wszystkich gniazdach okraglych (18 na plik wieczorny, 23 na plik poranny, 12 plikow) | JSON d_bottom 9,86 / 12,86 / 10,36 | d - 2 * 4 * tan 15 st. = d - 2,1436 +-0,01 | B | d_bottom zaokraglone do 0,01 (roznica promienia 0,0018) |
| promien na 3 glebokosciach | ZAL 12/12 | 24 (okragle) / 36 x 3 (rynienka) promieni poziomych z osi na z = -0,05 / -2 / -3,95: max odchylka od d/2 + z * tan 15 st. = 0,0029 mm | K-07 12/12 sond | +-0,1 | B | 30 312 promieni |
| glebokosc | ZAL 12/12 | dno z = -4,0000 w kazdym gniezdzie (4 punkty) i rynience (7 punktow), odchylka 0,0000 | - | -4 +-0,02 | B | |
| otwor fi 3 | ZAL 12/12 | 22 (wieczorna) / 27 (poranna) otworow na plik: promien pionowy z gory i z dolu bez trafienia (przelot), promien otworu na z = -6 i -7,9: odchylka od 1,5 max 0,0051 | - | fi 3 na wylot | B | |
| rynienka: stadion | ZAL 12/12 | petla wierzchu na obrysie stadionu (max odchylka 0,0002): wieczorna x -29,999...29,999, y -37,7...-22,7 (60 x 15, srodek (0; -30,2)); poranna x -25,0...25,0, y -41,8...-28,8 (50 x 13, srodek (0; -35,3)); jedna rynienka na plik, przednia | JSON id 1 | `ev_rows` / `mo_rows` | B | |
| rynienka: otwory | ZAL 12/12 | 4 petle otworow na z = -4 i 4 na z = -8 w x = -18, -6, 6, 18 (rozstaw 12, wieczorna) / -15, -5, 5, 15 (rozstaw 10, poranna); miedzy otworami dno -4 | 4, rozstaw 12 / 10 | `trough_hole_count` 4, `ev_/mo_trough_hole_pitch` | B | D3-a: bez zmian |
| K-06 | ZAL 12/12 | 90/90 sond (wieczorna, 18 gniazd x 5), 115/115 (poranna, 23 x 5); razem 1230 | 90/90, 115/115 | wszystkie | B | |
| K-07 | ZAL 12/12 | 72/72 i 92/92 (wszystkie gniazda, 4 sondy: +x, +-y); razem 984 | 12/12 (3 na rozmiar) | tak | B | |
| K-08 | ZAL 12/12 | 14/14 na plik (srodek, 2 konce, 2 za koncami, miedzy otworami, 4 otwory, 4 sondy na 45 st.) + sonda naroznika prostokata 4/4 na plik, TAKZE na okraglych (16/16) | 10/10; okragle bez sondy naroznika | tak | B | patrz D1 |

### 2.3 Punkt 3 - kontrola odwrotna (stary uklad R54 / R57 z archiwum)

Trzy niezalezne drogi, kazda na wszystkich 12 plikach:

| Id | Wynik | Zmierzone przez recenzenta | Oczekiwane | Waga | Uwaga |
|---|---|---|---|---|---|
| ODWROTNA / mapa nowej siatki | ZAL 12/12 | mapa wierzchu (krok 0,05): 48 167 352 punktow ocenionych, **0 niezgodnych** z modelem z `parametry.json` (plaski wierzch z = 0 +-0,005 wszedzie poza nowymi cechami; cechy +-0,25 w z, max odchylka 0,0067; przeloty bez trafienia; poza obrysem bez trafienia); mapa spodu: 49 436 094 punktow, **0 niezgodnych** (spod z = -8 wszedzie poza nowymi otworami fi 3, kieszeniami magnesow i wycieciem D) | pelny material wszedzie, gdzie nowy uklad nie ma cechy | B | pas +-0,06 mm wokol obrysow pominiety |
| ODWROTNA / roznica ze starym STL | ZAL 12/12 | stare siatki (te same nazwy plikow z archiwum) zmapowane tym samym rastrem: 17 196 176 punktow starych zaglebien i przelotow na wierzchu, z tego 6 351 603 lezy tam, gdzie nowy uklad ma plaski wierzch - **nowa siatka nieplaska: 0**; spod: 1 365 172 punktow starych przelotow, 993 336 w miejscu nowego pelnego spodu - **nowa siatka inna niz z = -8: 0**; stary relief cyfry poza strefa nowej cyfry (n9: cyfra przeniesiona): 0 punktow z > 0 | 0 | B | definicja "starego" z siatki, nie z rachunku |
| ODWROTNA / sondy ze starych parametrow | ZAL 12/12 | pozycje ze `parametry_przed_R59` (model starego ukladu): 370 cech starych w 12 plikach (gniazda, rynienki, stozki; okragle: takze stare dolki), 11 identycznych z nowa cecha (stozek A wieczornej, dolki okraglej wieczornej), 325 sprawdzonych, 34 w calosci pod nowa cecha; 10 999 punktow, 7342 pod nowa cecha, 3657 sprawdzonych: wierzch z = 0 w kazdym; **10 811 sond punktowych W BRYLE (z = -0,5 / -2 / -3,9; stare otwory z = -6 / -7,5): 10 811 / 10 811**; stare otwory fi 3: 390, z tego 294 poza nowymi otworami - spod z = -8 w kazdym | W BRYLE, wierzch 0, spod -8 | B | stare stozki: wieczorna B (-35,5; 26,5), C (35,5; 26,5), poranna A (-34,5; -28), B (-30; 32,5), C (30; 32,5) - po 17 / 17 punktow pelnych; dawne rogi (+-42; +-42): K-09 |
| stare dolki i cyfra okraglej porannej | ZAL | stare dolki (30,5; -31) i (30,5; -28): pelny material (17 / 17 punktow); (30,5; -25) i (30,5; -22) leza w nowym gniezdzie fi 12,5 (31; -19,55); stara cyfra (36,5; -24,5): brak reliefu (mapa) | pelny material albo nowa cecha | B | |

### 2.4 Punkt 4 - kolo, strefa, scianki, stozki, dolki, cyfra

| Id | Wynik | Zmierzone przez recenzenta (siatka) | Rachunek recenzenta z `parametry.json` | Zadeklarowane | Oczekiwane | Waga |
|---|---|---|---|---|---|---|
| K-05 c: max promien obrysu | ZAL | wieczorna 45,9266 (fi 15 w (+-18; 33,95)); poranna 46,4107 (fi 12,5 w (+-15,5; 37,05)); stozki 46,9304 / 46,9771 | 45,9266 / 46,4116; stozki 46,933 / 46,978 | 45,927 / 46,412 | <= 47 | B |
| K-05 c: strefa +-45 | ZAL | wieczorna max abs(x) 43,5000, abs(y) 41,4497; poranna 45,0000 / 43,2988 | 43,5 / 41,45; 45,0 / 43,3 | 43,50 / 45,00 | <= 45 | B |
| K-05 d: kwadraty narozne | ZAL | wierzcholkow obrysow gniazd z abs(x) > 35 i abs(y) > 35: 0 | min odleglosc 5,89 / 8,56 | - | 0 | B |
| K-05 e: min scianka (wszystkie pary) | ZAL | 621 pomiarow par o odstepie < 4,5 mm w 12 plikach: z wierzcholkow petli min 3,0003 (wieczorna, rynienka - fi 12) i 3,0000 (poranna, fi 12,5 - fi 12,5 w rzedzie); promieniem poziomym na z = -0,01 (po korekcie stozka): min 3,0007 / 3,0000; max roznica pomiar - rachunek 0,0059 | 3,0000 (18 par w wieczornej, 25 par w porannej o sciance < 3,005) | 3,000 (id 1 - 3) | >= 3 | B |
| K-09 / stozki | ZAL | 3 petle fi 5,00000 w pozycjach z `ev_/mo_marker_pos` (odchylka srodka <= 0,0001); promien na z = -0,05 / -1 / -2 zgodny ze stozkiem do 0,0029; glebokosc przy osi -2,9354 (oczek. -2,9354 w odleglosci 0,054 od osi, czyli wierzcholek -3,0); K-09 sondy 15/15 (kwadrat, z dawnymi rogami), 12/12 (okragle) | - | 15/15, 12/12 | fi 5 x 3 | B |
| K-16: stozek - gniazdo | ZAL | wieczorna A 3,517 / B 3,229 / C 3,194; poranna A 3,446 / B 3,019 / C 3,480 | 3,516 / 3,229 / 3,193; 3,445 / 3,016 / 3,480 | 3,52 / 3,23 / 3,19; 3,45 / 3,02 / 3,48 | >= 3 | B |
| K-16: promien srodka stozka | ZAL | 44,300 / 44,196 / 44,433; 44,207 / 44,255 / 44,478 | to samo | max 44,43 / 44,48 | <= 44,5 | B |
| K-16: kwadrat, dolki | ZAL | pliki bazowe (4 dolki): dolek - gniazdo 8,27 / 8,61, dolek - stozek 6,01 / 11,03 (z petli, zgodnosc z rachunkiem +-0,03) | 8,269 / 8,609; 6,013 / 11,034 | 8,27 / 8,61; 6,01 / 11,03 | >= 3; >= 1,5 | B |
| K-11 / K-62: bity = numer | ZAL 12/12 | petle dolkow fi 2,00000 x 1,0000 tylko dla bitow numeru: bazowe A+B+C+D, n1 A, n2 B, n3 A+B, n4 C, n5 A+C, n6 B+C, n8 D, n9 A+D; dla bitow = 0 wierzch z = 0; K-11 sondy 76/76 | - | te same bity | n = A + 2B + 4C + 8D | B |
| K-13: cyfra | ZAL 12/12 | bazowe: max z = 0,0000; numerowane: max z = 0,6000, wysokosc cyfry 5,0...5,15 (raster 0,05), srodek w (39,5; -44,5) +-0,05 (kwadrat), (35,0; -26,5) (n8), (-44,0; 5,5) (n9); tresc z obrazu: 1, 2, 3, 4, 5, 6, 8, 9 - nieodbite | - | max Z 0,000 / 0,600 | 0,00 / 0,60; cyfra = n | B |
| cyfra okraglych: kolo i odstep | ZAL | z rzeczywistego obrysu cyfry: n8 promien max 46,245, odstep od cech 3,508 (rynienka), od sciecia 3,46; n9 promien max 46,134, odstep 3,939 (fi 12,5 w (-32,25; 8)) | prostokat 5 x 3,6: 46,85 / 46,49; 3,27 / 3,48; sciecie 2,83 | generator nie sprawdza (rejestr #4) | <= 47; >= 3 | B |
| K-10, K-12, K-14, K-15 (kwadrat, cechy bez zmian) | ZAL 8/8 | 4/4, 13/13, 16/16, 3/3 sond w kazdym z 8 plikow; kieszenie fi 5,2 x 2,2 w (+-42; +-42) A, B, C (petle na spodzie i stropy na z = -5,8) | - | to samo | tak | B / D |

### 2.5 Punkt 5 - plytki okragle (K-61 a-f, K-62, K-63, `sockets` = kwadrat)

| Id | Wynik | Zmierzone przez recenzenta (siatka) | Rachunek z `parametry.json` | Zadeklarowane | Oczekiwane | Waga |
|---|---|---|---|---|---|---|
| K-61 a | ZAL 4/4 | 72 sondy promieniowe na plik (z = -4 i -7,5, co 10 st. poza sektorem sciecia): promien 49,9963...50,0000 | 50 (wielobok: 49,996) | 49,996...50,000 | 50 +-0,05 | B |
| K-61 b | ZAL 4/4 | sciecie na -45 st.: 49,3559 / 49,3559 (z = -4 / -7,5); 3 st. za sektorem sciecia: promien 50 +-0,05 | 49,3559 | 49,356 | 49,356 +-0,05 | B |
| K-61 c | ZAL 4/4 | faza i krawedz na 90 st.: 5/5 sond; petla wierzchu obrysu 0,5 od okregu (faza 0,5), na scieciu krawedz ostra (plaszczyzna na calej grubosci) | - | 5/5 | tak | B |
| K-61 d | ZAL 4/4 | bbox x, y -50,0000...50,0000; z_min -8,0000 | - | to samo | +-R +-0,01; -8 +-0,01 | B |
| K-61 e | ZAL 4/4 | glebokosc sciecia 0,6441 | 0,6441 | 0,644 | >= 0,6 | B |
| K-61 f | ZAL 4/4 | scianka plaszczyzna sciecia - obrysy (z wierzcholkow petli i zmierzonej plaszczyzny): wieczorna 4,592 (koniec rynienki), stozki 27,41, dolki 14,41; poranna 4,815 (koniec rynienki), stozki 28,82, dolki 22,19 | 4,591 / 4,814 | 4,59 / 4,81 | >= 3 | B |
| K-16 okragle: do krawedzi | ZAL 4/4 | gniazdo - sciana pionowa: wieczorna 4,073 (fi 15 tylne), poranna 3,589 (fi 12,5 tylne); stozek - krawedz 3,070 / 3,023 (C); dolek - krawedz 5,272 / 5,068 | 4,073 / 3,588; 3,067 / 3,022; 5,268 / 5,068; do poczatku fazy 3,573 / 3,088 | 4,07 / 3,59; 3,07 / 3,02; 5,27 / 5,07 | >= 1,5 | B |
| K-62: dolki w polu | ZAL 4/4 | pozycje petli = `code_dimples_round` (wieczorna y -43,5, x -4,5 / -1,5 / 1,5 / 4,5; poranna A (36,5; 18,5), B (36,5; 21,5), C (43; 6), D (43; 9)); dolek - gniazdo 4,800 (wieczorna, rynienka) / 3,552 (poranna, D - fi 12,5); dolek - stozek 31,86 / 2,096 (A - C); bity: bazowe A+B+C+D, n8 D, n9 A+D | promien srodka 43,53...43,73 / 40,92...43,93 (<= 44); 4,800 / 3,546; 31,855 / 2,090; krawedz 5,268 / 5,068 | 43,73; 4,80; 31,86; 5,27 / 43,93; 3,55; 2,09; 5,07 | <= 44; >= 3; >= 1,5; >= 1,5 | B |
| K-63 | ZAL 4/4 | wszystkie sciany zwrocone w dol leza na z = -8,000 (pole 7691,55 / 7656,37 mm2), skosnych w dol 0; petle na spodzie: tylko otwory fi 3 (22 / 27) i obrys; sondy 27/27 W BRYLE (r 45,5 co 30 st. na z = -7 i -7,9; r 49,5 na z = -2 w 0 / 90 / 180 st.) | - | 27/27, z = -8 | spod plaski, bez kieszeni i rowka | B |
| K-05 h | ZAL 2/2 | lista `sockets` JSON okraglej = lista kwadratu tego typu (19 i 24 pozycje, wszystkie pola); `markers` identyczne; siatki: te same cechy i odchylki w plikach okraglych i kwadratowych | - | tak | identyczne | B |

### 2.6 Punkt 6 - SHA-256

| Id | Wynik | Zmierzone | Oczekiwane | Waga |
|---|---|---|---|---|
| 12 STL plytek | ZAL 12/12 | = tabela w `R59_wdrozenie_zmiany.md` pkt 0 i = raport wykonawcy sekcja 2 | to samo | P |
| 4 JSON ukladu | ZAL 4/4 | = `R59_wdrozenie_zmiany.md`, = raport, PC = git HEAD = MSI | to samo | P |
| 9 plikow nieplytkowych | ZAL 9/9 | korpus W `bd55871c`, korpus P `aadb91c9`, blat `8c48856e`, wkladka `f4196fbc`, pokrywka `ad234444`, tulejka DC `b393256c`, podkladki `4260d1f1` / `e79a8051` / `9c47aea4` = `SHA256SUMS_2026-11-02_R57.txt` i = archiwum sprzed R59 | bajtowo bez zmian | B |
| zmiana plytek | ZAL 12/12 | kazdy z 12 plikow plytek ma inne SHA niz przed R59; 12 SHA parami roznych | nowy uklad we wszystkich | B |

### 2.7 Punkt 7 - K-53 (wlasne zlozenie z STL, bez `ramka_v2.blend` i bez wyniku generatora)

Zlozenie: wkladka wg tabeli 1 (12 / 12 sond orientacji K-23, K-24, K-27, K-28 zgodnych; 4 polki na z = 2,5000; wierzch ramy 6,0000), plytka spodem na polkach, pokrywka obrocona o 180 st. wokol X (10 / 10 sond K-17, K-18, K-20 zgodnych), wierzch pokrywki = wierzch plytki + `cover_inner_h` 14 + `cover_top_t` 2.

| Para | Wynik | Zmierzone | Zadeklarowane | Oczekiwane | Waga |
|---|---|---|---|---|---|
| plytka wieczorna n1 - wkladka | ZAL | przeciecia siatek skurczonych o 0,05: 0; punkty jednej czesci w drugiej glebiej niz 0,02: 0 z 13 186; pary stykowe siatek surowych: 311, wszystkie w plaszczyznie polek z = 2,5 (poza nia 0); luz plytka - otwor 0,4000 z 4 stron | 0 przeciec; 311 par stykowych | 0 | B |
| pokrywka - plytka wieczorna n1 | ZAL | skurczone 0, surowe 0, punkty 0 z 15 331; luz wneka - plytka 0,3000 z 4 stron; garb pokrywki x 47,6 w rowku plytki o dnie x 47,2 (luz 0,4) | 0 | 0 | B |
| pokrywka - wkladka (K-22) | ZAL | skurczone 0, surowe 0, punkty 0; dol kolnierza z 6,5 nad rama 6,0 (luz 0,5) | 0 | 0 | B |
| pozostale 7 plytek kwadratowych (n2-n6, 2 bazowe) - wkladka i pokrywka | ZAL 7/7 | to samo: 0 przeciec, 311 (wieczorne) / 314 (poranne) par stykowych tylko na polkach, luzy 0,4 / 0,3 / 0,4 | nie w zestawie generatora | 0 | B |
| kontrola czulosci | ZAL | plytka +0,6 mm w x: 79 przeciec skurczonych, 22 punkty w bryle; pokrywka -1,0 mm: 368 przeciec | - | wykrycie | - |

### 2.8 Punkt 8 - zgodnosc `parametry.json` <-> `plan_ramki_v2.md` <-> `protokol_weryfikacji_v2.md` <-> G0

Liczby policzone przez recenzenta z `parametry.json` (log, czesc 2) porownane z kazdym miejscem dokumentow oznaczonym R59:

| Co | Wynik | Szczegoly |
|---|---|---|
| G0 D1 (W-b) | ZAL | `ev_rows`: 6 x fi 12 + 12 x fi 15 = 18 gniazd + 1 rynienka 60 x 15 w y -30,2 (przednia, id 1); wartosci `ev_rows`, `ev_marker_pos` = `R59_szkice/parametry_wariant_W-b.json` |
| G0 D2 (P-e) | ZAL | `mo_rows`: 20 x fi 12,5 + 3 x fi 15 = 23 gniazda + 1 rynienka 50 x 13 w y -35,3; brak fi 7,5 i fi 10; rzedy mieszane = osobne wpisy (8 wpisow, 8 roznych y: 8 / 8,75 i 22,85 / 23,6); `mo_rows`, `mo_marker_pos`, `code_dimples_round.poranna`, `number_pos_round.poranna` = `parametry_wariant_P-e.json` (6 / 6 kluczy identycznych) |
| G0 D3-a, D5-A, D6 | ZAL | klucze o zmienionej wartosci wzgledem `parametry_przed_R59`: dokladnie 6 (`ev_rows`, `mo_rows`, `ev_marker_pos`, `mo_marker_pos`, `code_dimples_round`, `number_pos_round`); `trough_hole_count` 4, rozstawy 12 / 10, `plate_numbers_*`, `quantities` i pozostale 281 kluczy bez zmian; kluczy 287 |
| JSON ukladu = parametry | ZAL 4/4 | `sockets` (19 / 24 pozycje: id, x, y, typ, d_top, d_bottom, l, w, depth, hole_d, hole_pitch, hole_count), `markers`, `code_dimples`, `number_relief`, `flat` / `notch` / `magnet_pockets`: 0 roznic; K-05 a-g z JSON: 4/4 plikow |
| plan Z20 (linia 30), 00_PRZEPLYW (wiersz Z20/D6) | ZAL | 18 + 1 / 23 + 1, srednice, jedna rynienka przednia |
| plan D6 (linie 89-121) | ZAL | tabele wpisow (y, zakres, x, id, skrajny promien: 45,16 / 45,92 / 43,60 / 40,15 / 45,93 i 46,35 / 42,90 / 45,48 / 39,48 / 16,25 / 41,00 / 31,09 / 46,41), bloki y 79,15 / 85,1, scianki po przekatnej (3,02 / 3,01; 3,02 / 3,03 / 3,00 / 3,02 / 3,00 / 3,00 / 3,02 / 3,06 / 3,02), stozki (promienie, scianki, boki trojkata 58,17 / 74,95 / 87,68 i 55,94 / 79,36 / 86,53), linia 121 (zapas 1,07 / 0,59; 43,5 / 45,0; 8,27 / 8,61; 6,01 / 11,03; 11,74 / 13,84; 16,67 / 19,18): 0 roznic |
| plan D11 (136), 3.1 (170, 191, 195, 196, 201-208), 4.1 (460, 461, 476, 481-483, 487), 4.1a (491-498), 4.11 (583, 587, 588, 606, 607) | ZAL | 0 roznic liczbowych (m.in. 4,07 / 3,59; 3,57 / 3,09; 3,07 / 3,02; 4,59 / 4,81; 43,73; 4,80; 40,92...43,93; 3,55...4,08; 2,09...6,61; 5,27 / 5,07; cyfra 46,85 / 46,49; 3,27 / 3,48; 36,35 / 13,70; 31,15 / 78,40; 2,83; rzuty 37,27 + 7,5 = 44,77 i 38,04 + 6,5 = 44,54); tabela 3.1: 249 wierszy z kluczem, 0 roznic wartosci |
| protokol tabela 1 (linie 19-22) | ZAL | 60 [59,6] / 60 [59,9] / 49 [49,3] / 50 [49,6] - pomiar 59,64 / 59,93 / 49,34 / 49,63 |
| protokol K-05 (46), K-08 (49), K-09 (50), K-11 (52), K-13 (54), K-16 (57), K-61 (65), K-62 (66), K-59 (150) | ZAL | 18/1 i 23/1; 45,93 / 46,41; narozniki 37,5 / 38,2 (pomiar: punkty sondy w promieniu 37,53 / 38,19); pozycje stozkow; (-44; 5,5); K-16: 3,52 / 3,23 / 3,19, 3,45 / 3,02 / 3,48, 8,27 / 8,61, 6,01 / 11,03, 4,07 / 3,59, 3,57 / 3,09, 3,07 / 3,02, 4,80 / 3,55, 31,86 / 2,09, 5,27 / 5,07; K-61: 4,59 / 4,81; K-62: pozycje i liczby: 0 roznic; zaden prog nie zostal zmieniony (diff protokolu: 13 linii, same liczby odniesienia i opisy) |
| plan rejestr R59 (linia 890), pkt 28 (linia 955) | ZAL z uwaga D3 | tresc decyzji G0 i zakres zgodne; linia 890 odsyla do `raport_wykonawcy_R59_iter1.md` (obowiazuje iter2); linie 890 i 955 pomijaja K-11 i K-13 na liscie zmienionych sprawdzen protokolu |
| opisy kluczy w `parametry.json` (linie 31, 32, 60-76 oraz `plate_round_d`, `round_flat_w`, `code_dimples_round`, `number_pos_round`) | ZAL | liczby w polach `opis` zgodne z rachunkiem recenzenta (45,927; 46,412; 3,000; promienie i scianki stozkow; boki trojkata; 4,07 / 3,59; 3,07 / 3,02; 4,59 / 4,81; 4,80; 3,55...4,08; 2,09...6,61; 5,07...8,08; 46,85 / 46,49; 3,27 / 3,48; 13,70) |

## 3. Uwagi do poprawy (tylko NIE)

Brak. Zadne sprawdzenie o wadze B ani P nie dalo wyniku NIE.

| Nr uwagi | K-xx | Waga | Plik / cecha | Co jest | Co ma byc |
|---|---|---|---|---|---|
| - | - | - | - | - | - |

## 4. Rozbieznosci miedzy raportem wykonawcy a pomiarem recenzenta

Brak rozbieznosci. Porownane: liczby trojkatow 12 / 12, gabaryty 12 / 12, objetosci 12 / 12 (max roznica 0,0049 cm3 - zaokraglenie raportu), K-05 (max promien 45,927 / 46,412, min scianka 3,000, liczby 18/1 i 23/1), K-06 (90 / 115 sond), K-09, K-11 (bity), K-13 (max Z), K-16 (wszystkie wartosci), K-61 (promien, sciecie 49,356, glebokosc 0,644, scianki 4,59 / 4,81), K-62, K-63, K-53 (para plytka n1 - wkladka: 311 par stykowych u wykonawcy i u recenzenta, 0 przeciec), SHA 25 / 25.

## 5. Ocena rejestru odstepstw wykonawcy i dwoch spraw zgloszonych przez wykonawce

Rejestr = sekcja 4 raportu `raport_wykonawcy_R59_iter2.md`; oceniono wpisy zwiazane z plytkami (#1-#8) i #15. Wpisy #9-#14, #16 dotycza czesci nietknietych w R59 (bez zmian tresci).

| # odstepstwa | Zasadne? | Wymaga decyzji wlasciciela? | Komentarz |
|---|---|---|---|
| 1 (`plate_round_d` 100) | tak | nie (zatwierdzone 2.11) | po R59 scianki do krawedzi wieksze niz przy R54: pomiar 4,07 / 3,59 (gniazda), 3,07 / 3,02 (stozki) |
| 2 (`round_flat_w` 16) | tak | nie (zatwierdzone 2.11) | pomiar: glebokosc 0,6441, scianka do obrysow 4,59 / 4,81 |
| 3 (`code_dimples_round`) | tak | nie - poranna zmieniona decyzja G0 (P-e) | wartosci = plik wariantu P-e; pomiar K-62 w normie (3,55 do gniazda, 2,10 do stozka C, 5,07 do krawedzi) |
| 4 (`number_pos_round`) | tak | nie - poranna zmieniona decyzja G0 (P-e) | generator nie sprawdza odstepu cyfry od gniazd; recenzent zmierzyl z rzeczywistego obrysu cyfry: 3,51 (n8) i 3,94 (n9) >= 3, promien 46,25 / 46,13 <= 47 |
| 5 (K-08 na okraglych) | tak (informacyjnie) | nie | patrz (a) ponizej i D1 |
| 6 (bazowe kwadratowe z dolkiem D) | tak | bez zmian od R57 | pliki bazowe nie ida do druku; pomiar: bazowe maja 4 dolki, n1-n6 bez D |
| 7 (boolean, triangulacja okraglych) | tak | nie | K-03 12/12: 0 przeciec wlasnych, 0 zbednych scian |
| 8 (R59: `ev_rows`, `mo_rows`, id w rzedach mieszanych) | tak | nie (decyzja G0) | liczby i kolejnosc id potwierdzone (K-05 g z JSON: id po y wpisu, w wpisie malejace x; poranna id 13-16 fi 12,5 w y 8, id 17 fi 15 w y 8,75, id 18-19 fi 15 w y 22,85, id 20-21 fi 12,5 w y 23,6) |
| 15 (wkladka: znak zera normalnych) | tak | nie | potwierdzone w K-59 recenzenta: trzeci wariant SHA (`e363b006...`), siatka identyczna; plik oddany = `f4196fbc...` (pakiet R57) |

**(a) Sonda naroznika prostokata w K-08 na plytkach okraglych - to nie jest wada R59, tylko uwaga informacyjna (D1).**
Protokol (linia 49) wymienia dla plytek okraglych obie sondy od R57-C (2.11.2026): zapis "sonda naroznika jest wykonalna i daje W BRYLE jak na kwadracie" jest juz w protokole sprzed R59 (`archiwum/protokol_weryfikacji_v2_przed_R59_2026-11-14.md`, SHA = `origin/main`). Generator od tamtej pory robi na okraglych tylko sonde na 45 st.; R59 tego nie zmienil i nie pogorszyl, a wykonawca wpisal to jawnie do rejestru (#5) i do sekcji 7.4. Recenzent wykonal sonde naroznika sam, na wszystkich 4 plikach okraglych i 4 naroznikach rynienki: 16 / 16 W BRYLE (punkty w promieniu 37,53 i 47,48 - wieczorna, 38,19 i 48,02 - poranna, czyli w plytce R 50); razem z kwadratowymi 48 / 48. Koniec rynienki jest zaokraglony takze wg petli krawedzi (odchylka od stadionu <= 0,0002) i 4 sond na 45 st. Zalecenie: przy najblizszej zmianie generatora dodac sonde naroznika dla okraglych (jedna linia) albo dopisac w protokole, ze na okraglych wykonuje ja recenzent. Komentarz w generatorze (linia 2119) "jedna metoda dla okraglych (protokol K-08)" nie odpowiada tresci protokolu.

**(b) Zmiany generatora (diff 42+ / 18-) - zadna nie oslabia sprawdzenia; jedna uwaga D2 o liczbach wpisanych w teksty.**
- `OBJ_ORIENT` (linie 61-62): 62 -> 60, 61 -> 60, 51 -> 50 (okragla wieczorna 49 bez zmian). To stale K-04b (+-30 %) zapisane w kodzie takze przed R59, rownolegle do tabeli 1 protokolu (teraz 60 / 60 / 49 / 50 - zgodne). Zakresy 42...78 i 34,3...63,7 / 35...65 obejmuja zmierzone 59,6 / 59,9 / 49,3 / 49,6 z duzym zapasem; sprawdzenie nie jest slabsze niz przed zmiana. Nie sa to liczby ukladu z `parametry.json`.
- `generuj_gniazda`: zmieniony tylko docstring; kod sortuje wpisy po y i w wpisie po x malejaco - tak samo jak model recenzenta; JSON = model 4 / 4.
- K-05: zmieniony tylko tekst etykiety ("rzedow" -> "wpisow rzedow (roznych y)"); warunki (a)-(h) bez zmian; liczby oczekiwane nadal z `ev_rows` / `mo_rows`.
- K-08 (linia 2119): dodany komentarz, kod sondy bez zmian (patrz a).
- `odstepstwa_informacyjne_R57` / nowa `odstepstwa_informacyjne_R59`: teksty rejestru; pozycje dolkow i cyfry okraglych oraz liczby gniazd ida teraz z parametrow (poprawa). W tekstach zostaly trzy liczby zalezne od obecnego ukladu wpisane na stale: "y -35,3" (linia 4228), "(31; -19,55)" (linia 4233), "37,5 / 38,2" (linia 4236) - przy nastepnej zmianie rzedow stana sie nieprawdziwe tak jak teksty poprawiane teraz (D2). Nie wplywaja na zadne sprawdzenie.
- K-59 recenzenta potwierdza, ze generator z git HEAD z `parametry.json` z git HEAD odtwarza 12 / 12 plikow plytek i 4 / 4 JSON bajt w bajt.

## 6. Lista drobnych (D) - nie blokuja etapu

| Nr | Dotyczy | Miejsce | Co jest | Propozycja |
|---|---|---|---|---|
| U-R59B1-1 (D1) | K-08, plytki okragle | `ramka_generator.py` linia 2119 i sonda ponizej; `protokol_weryfikacji_v2.md` linia 49 | generator wykonuje na okraglych tylko sonde na 45 st., protokol wymienia tez sonde naroznika prostokata (stan od R57-C, nie wprowadzony przez R59; wpis #5 rejestru); pomiar recenzenta sondy naroznika: 16 / 16 W BRYLE | dodac sonde przy najblizszej zmianie generatora albo doprecyzowac protokol; poprawic komentarz w linii 2119 |
| U-R59B1-2 (D2) | teksty rejestru odstepstw | `ramka_generator.py` linie 4228, 4233, 4236 | liczby zalezne od ukladu wpisane na stale: "y -35,3", "(31; -19,55)", "37,5 / 38,2" | liczyc z `P` albo usunac z tekstu |
| U-R59B1-3 (D3) | rejestr R59 w planie | `plan_ramki_v2.md` linia 890; linie 890 i 955 | odeslanie do `raport_wykonawcy_R59_iter1.md` (obowiazuje iter2; iter1 ma w sekcji 2 SHA wkladki `de0d26c5...` zamiast oddanego `f4196fbc...`, pozostale 24 SHA i wynik 58 / 5 / 0 takie same); lista zmienionych sprawdzen protokolu bez K-11 i K-13 | poprawic przy edycji dokumentow (R59-D) |
| U-R59B1-4 (D4) | K-59, wkladka | `ramka_wkladka_v2.stl` | plik nie odtwarza sie bajtowo (przebieg recenzenta: `e363b006...`; 1806 / 1806 trojkatow identycznych); znane (`do_v3.md` #9), poza zakresem R59; oddany plik = pakiet R57 | bez dzialan w R59; przy pakiecie brac plik `f4196fbc...` jak dotad |
| U-R59B1-5 (D5) | opis plytki kwadratowej | `plan_ramki_v2.md` linie 463 i 478 | tekst "wszystkie 3 dolki" i przyklad JSON z 3 dolkami (A, B, C), choc od R57 sa 4 bity (D) - pozostalosc sprzed R59 w akapicie edytowanym w R59 (przyklad `markers` / `sockets` zaktualizowano) | uzupelnic przy edycji dokumentow |

Uzasadnienie wagi D dla U-R59B1-3: to odeslanie do pliku, ktory istnieje i ma te same wyniki plytek; liczby i decyzje w planie sa poprawne. Gdyby nadzor uznawal kazda niespojnosc odeslan za P, jest to jedyna pozycja, ktora moglaby zmienic werdykt - recenzent ocenia ja jako kosmetyke (tak jak uwagi D1 i D3 recenzji R57).

Uwagi do planu (informacyjnie, bez wagi): uklad nie ma zapasu - zmierzone minimum scianki 3,0000 (limit 3), rzad fi 12,5 x 6 porannej siega dokladnie abs(x) = 45,0000 (limit 45), obrys stozka C porannej ma promien 46,977 (limit 47), stozek B porannej - gniazdo 3,019 (limit 3). Wszystko w limitach i zgodne z D6 ("scianki nie maja zapasu"); kazda przyszla korekta pozycji tylko narzedziem i z ponownym pomiarem.

## 7. Czego nie sprawdzono i dlaczego

- Arkusze (`arkusz_zamowienia`, `arkusz_wymiarow`, `kody_plytek.md`), rendery, `ramka_v2.blend`, `README.md` - poza sekcja 8 planu (K-57, K-58, K-60 naleza do przebiegu generatora). Tylko rzut oka: objetosci 6 plytek kwadratowych w `arkusz_zamowienia.csv` = pomiar +-0,01; pozycje dolkow w `kody_plytek.md` = parametry.
- Pelne zlozenie K-53 (korpus, blat, panel, bryly zastepcze: 24 obiekty, 276 par) - punkt 7 planu obejmuje pary plytka - wkladka i pokrywka - plytka (dodano pokrywka - wkladka i wszystkie 8 plytek kwadratowych). Plytki okragle nie maja wkladki ani pokrywki (R58) - bez testu zlozenia.
- 9 plikow nieplytkowych: tylko SHA (bajtowo = R57) oraz 22 sondy orientacji wkladki i pokrywki w K-53; bez ponownego pomiaru geometrii.
- `narzedzia/weryfikuj_uklad_R59.js` (103 linie OK u wykonawcy i koordynatora) - nie uruchamiano; zastapione wlasnym rachunkiem z `parametry.json` (`sprawdz_R59_liczby.py`, 53 sprawdzenia).
- Mapy pomijaja pas +-0,06 mm wokol obrysow cech oraz pas 0,56 mm przy krawedzi (faza); te miejsca pokrywa spis petli (odchylka <= 0,0051), sondy K-14 / K-15 / K-61 c i promienie scianek.
- Program stanowiska (`stanowisko/**`, R59-P), dokumenty stanowiska, model 3D, pakiet - poza zakresem R59-B.
- Zadne sprawdzenie zaplanowane w sekcji 8 nie zostalo pominiete ani nie skonczylo sie bledem przebiegu (12 / 12 procesow Blendera z kodem 0, czas 25,5 s).

## 8. Pliki recenzenta

- Worktree: `Ramki/recenzja/sprawdz_R59_wspolne.py`, `sprawdz_R59.py`, `sprawdz_R59_uruchom.py`, `sprawdz_R59_liczby.py`, `sprawdz_R59_sha.py`, `sprawdz_R59_K53.py`, `sprawdz_R59_K59.py`, `sprawdz_R59_normalne.py`, `sprawdz_R59_podglad.py`, `log_R59_iter1.txt`, `raport_recenzenta_R59_iter1.md`.
- PC (tylko katalog recenzenta): `<PC-katalog>\r59\recenzja\` - skrypty, `run.cmd`, `ref\` (kopia plikow z git HEAD), `wyniki\` (12 x `wynik_*.json` ze wszystkimi sondami, mapy i obrazy cyfr PNG, logi, `kontrola\`), `powtorka\` (czysty przebieg generatora do K-59). Poza tym katalogiem na PC niczego nie zapisano; niczego nie instalowano.
- Odtworzenie: `run.cmd sprawdz_R59_sha.py`; `run.cmd sprawdz_R59_liczby.py`; `run.cmd sprawdz_R59_uruchom.py --krok 0.05`; `blender -b -P sprawdz_R59_K53.py -- --stl <stl> --par ref\Ramki\parametry.json --wyn wyniki`; `run.cmd sprawdz_R59_normalne.py`; `run.cmd sprawdz_R59_K59.py` (po przebiegu generatora w `powtorka\Ramki`).
