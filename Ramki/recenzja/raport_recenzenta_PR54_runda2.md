# Raport recenzenta - PR #54 (E3-S1 / E3-S2), runda 2 (recenzja przyrostowa po etapie S2a)

Data: 2026-11-21, 14:21-14:50. Zakres: `git -C <PC-katalog>\qc diff 3e8d08f e3/sprzet -- Ramki/etap3/testy_sprzet_2026-11-28
Ramki/stanowisko/raporty/E3-S2_2026-11-21.md`, HEAD d8e7087 (12 plikow, +1657 / -696; zmiany wniesione przez `main` 8001b55
poza recenzja). Kopia do prob: `<PC-katalog>\qc-wt\rec-s1` (detached d8e7087).

Metoda: (1) dokument, arkusz, zalaczniki i README przeczytane w calosci "oczami wlasciciela z wydrukiem"; (2) wlasne proby
narzedzi z kopii `rec-s1` na kodzie programu z kopii integracyjnej `<PC-katalog>\qc-wt\integ` (O1 + O2 + O3 + O4; tylko
uruchamianie, zapis w `robocze\rec-s1`): 44 proby `pole_skanu`, 34 proby `ramka_proba` na atrapie programu
ramki w tym samym procesie; (3) 51 testow narzedzi na kodzie kopii `rec-s1` (O1) i 8 wstrzykniec bledu (kazde cofniete);
(4) 30 pozycji dokumentu sprawdzonych w kodzie `integ` / `main` 1fce3fe; (5) `t13_higiena.py` z `integ` na kopii; (6) raport
wykonawcy czytany po wlasnym przegladzie dokumentu i narzedzi. Pelnego pytest nie uruchamialem. Liczby ponizej sa z moich
prob, chyba ze napisano "wg wykonawcy". Pliki robocze i logi: `<PC-katalog>\koordynator\robocze\rec-s1\` (pliki `*_r2*`,
katalog `pole_r2\` z tekstami wynikow narzedzia).

Uwaga o wlasnych probach: pierwsza seria prob pola (etap U w `proby_pole_r2.py`) ciela siatke wg srodkow trojkatow; duze
trojkaty plaskiego wierzchu plytki zostawaly poza polem i proby PLYTEK w polu prostokatnym / przesunietym z tej serii sa
niewazne (proby kartonu, skanow pelnych i skanow z podlozem sa wazne - siatka o oczku 1 mm albo bez ciecia). Powtorzylem je
z dokladnym cieciem (`proby_pole2_r2.py`: plaszczyzny / `synth.przytnij_do_kola`); w tabelach sa tylko wyniki wazne.

## 0. Werdykt i liczby

WERDYKT: do scalenia po poprawkach - B 0, P 8, D 13 (uwagi rundy 1: U1-U9 zamkniete 9 z 9; wszystkie P tej rundy sa nowe).

Wyjasnienie. Narzedzia po S2a sa wyraznie lepsze: 9 z 9 uwag P rundy 1 zamknietych wlasnymi probami, 8 z 8 wstrzykniec
zlapanych, klucz ramki dziala i nie wycieka. Paczka dalej nie zmienia programu, wiec scalenie stanu d8e7087 niczego nie
psuje. Uwagi P tej rundy dotycza glownie TRESCI dokumentu i arkusza (N5, N7, N8 takze drobnych zmian w `pole_skanu`) - miejsc, w ktorych wlasciciel sam przy sprzecie zostanie bez
drogi wyjscia albo dostanie wynik inny niz obiecany. Wszystkie da sie zamknac w S2b razem z potwierdzeniem na 0.3.3.
Warunek jak w rundzie 1: dokument NIE trafia do wlasciciela jako "gotowy" przed zamknieciem P. Wyjatek pilny: sekcja 0
(pytania P1-P8, termin 25.11.2026) powinna trafic do wlasciciela od razu - nie zalezy od S2b (patrz sekcja 5, p. 1).

Najwazniejsze ryzyko calego dnia - "skan z podlozem" (N1, sekcja 2b): potwierdzone na kodzie `integ`, 11 z 11 skanow
sztucznych z podlozem o srednicy >= 150 mm nierozpoznanych; dokument i wydrukowana sciaga skanera razem PROWADZA do takiego
skanu ("bez obcinania", "linia ciecia najlepiej ponizej calej plytki"), a obejscie (linia / plaszczyzna ciecia programu
skanera miedzy stolikiem a wierzchem plytki) nie jest nazwane.

Ocena dokumentu po przepisaniu: kolejnosc dobra; 21 z 21 krokow ma "Co zrobic", "Udalo sie, gdy", "Zanotuj", "Gdy sie nie
uda" (czesc 4: wspolne); pytania P1-P8 sa na poczatku, z terminem, adresatem i skutkiem kazdej odpowiedzi, bez zgadywania;
jezyk krokow prosty (19 z 19 cytatow zargonu rundy 1 usunietych, 3 nowe miejsca - sekcja 1b). Dlugosc: dokument 492 wiersze,
4331 slow = 9,6 strony A4 (metoda rundy 1: 450 slow na strone; bylo 12), arkusz 178 wierszy, 1527 slow = 3,4 strony.

## 1. Uwagi

### 1.0 Uwagi rundy 1 (B i P): stan

| Uwaga | Stan | Dowod (wlasna proba, kod `integ`, o ile nie napisano inaczej) |
|---|---|---|
| U1 pole nie-kolowe | zamknieta; reszta = N8 (P) | pole prostokatne 100 x 80: karton -> "DANE NIE SA KOLEM: 80,0 x 100,0 mm. Do arkusza wpisz OBIE liczby; liczy sie mniejsza" (bylo: "kolo ok. 127,9 mm"); kwadrat -> "Plytka NIE jest cala w skanie: brzeg widac w 35 z 72 kierunkow. POLE NIE JEST KOLEM (albo plytka lezy z boku pola): dane najwezej 80,0 mm x 96,0 mm". Pole 130 x 90: karton "90,0 x 130,0", kwadrat "90,0 mm x 96,0 mm" (bylo: "POLE SKANERA MA OK. 134,4 mm"), okragla ramkowa "90,0 mm x 100,1 mm". Zdania prawdziwe w 5 z 5 prob pola prostokatnego (druga liczba przy plytce to wymiar plytki, nie pola - narzedzie pisze "dane", nie "pole"). Pole kolowe: karton 120 -> "kolo ok. 121,2 mm". Slabosc dopasowania okregu przy polu kolowym - N8 |
| U2 "cala plytka w skanie" | zamknieta | okragla testowa nr 8, pole kolowe 120 mm przesuniete o 15 mm (5 mm plytki poza polem): "Plytka NIE jest cala w skanie: brzeg widac w 52 z 72 kierunkow. ... POLE SKANERA MA OK. 119,2 mm (srodek pola 14,5 mm od srodka plytki). Plytka lezy z boku pola - przesun plytke na srodek pola i zeskanuj ponownie."; przesuniecie (-12, 9): brzeg 53 z 72, pole 120,0 mm, srodek 14,9 mm (prawda 120 / 15). Zdania "Cala plytka jest w skanie" nie ma (2 z 2); pojawia sie tylko przy brzegu 72 z 72 (6 z 6 skanow pelnych, pole 140 x 110, pole kolowe 104 mm) |
| U3 licznik rowka | zamknieta | kwadrat pelny: `rowek pokrywki: nie dotyczy (ten rodzaj plytki nie ma rowka pokrywki)`; okragla testowa pelna: to samo; okragla ramkowa pelna: "scianka cofa sie o 0,77 mm (projekt: 0,8 mm); cofniecie co najmniej 0,4 mm w 70 z 72 policzonych kierunkow - narzedzie NIE rozstrzyga"; okragla ramkowa bez scianki: "NIE widac - skan nie siega 2,5 mm ponizej wierzchu". Narzedzie nie sugeruje rowka na kwadracie (3 z 3); dokument w.245-246 i arkusz w.81-84 mowia "liczby, nie rozstrzyga" |
| U4 nadpisywanie wynikow | zamknieta | dwa pliki `skan.stl` z dwoch folderow do jednego `--wynik`: 2 pliki `skan_20261121_142927_pole.json` i `skan_20261121_142933_pole.json` (bylo: 1) |
| U5 skan z podlozem | zamknieta w zakresie rundy 1; ciag dalszy = N1 (P) | narzedzie: 11 z 11 skanow z duzym podlozem -> "UWAGA: w skanie jest prawdopodobnie PODLOZE (stolik / uchwyt wokol plytki)" i `podloze w skanie: PRAWDOPODOBNIE TAK`; dokument w.208, w.229-230, lista zbiorcza poz. 3; arkusz w.56 i w.80; POTRZEBUJE nr 1 w raporcie wykonawcy. Brakuje konkretnego obejscia - N1 |
| U6 skany z krokow 2.7 / 3.8 | zamknieta (przeglad) | czesc 5 p. 3 i 4 (w.455-458), podfolder `skany_program\` (w.467), arkusz w.106, w.146, w.161-162 |
| U7 termin i adresat pytan | zamknieta (przeglad) | w.25-28: "odpowiedz najpozniej do srody 25.11.2026", adresat, P3 pierwsze, kolejnosc P3, P1, P6, P8; przy kazdym z 8 pytan skutek odpowiedzi (ktory krok odpada albo dochodzi); 0 zgadnietych odpowiedzi |
| U8 tabela skanow w arkuszu | zamknieta; ciag dalszy = N7 (P) | arkusz w.67-78: kolumny "plytka naprawde", "co na niej", "program mowi (rodzaj; pewnie T/N)", "nr z dolkow", "dolki z 4", "scianka T/N, do mm", "brzeg z 72"; 8 wierszy; rowek osobno w.81-84 |
| U9 luki w testach | zamknieta | 8 z 8 wstrzykniec zlapanych (sekcja 2, proby 33-40): scianka nigdy niewidoczna - 1 failed (w rundzie 1: 9 passed); miara rowka zawsze 0 - 1 failed (bylo: 9 passed); bez watku podtrzymania planu - 2 failed (bylo: 17 passed); odpowiedz 401 nierozpoznana - 3 failed; ramka zajeta bez przerwania - 2 failed. Zachowanie tez sprawdzone proba: plan swieci 19 z 19 gniazd po 40 s (waznosc 30 s); ramke trzyma inny komputer - 1 odmowa z rada zamiast 19, "Ramki NIE zgaszono tym narzedziem", plan obcego nietkniety |

### 1.1 Uwagi tej rundy

| Nr | Waga | Plik:linia | Scenariusz | Propozycja |
|---|---|---|---|---|
| N1 | P | dokument w.193-194, w.207-208, w.229-230; wydruk `Ramki/sciaga_skaner_DentalScan_2026-11-16.md` w.94, w.98 (poza paczka) | Skan z podlozem. Wlasciciel robi pierwszy skan wg kroku 2.3 ("zapisz ... bez wygladzania i obcinania") i wg wydrukowanej sciagi ("linia ciecia ... najlepiej ponizej calej plytki"; po skanie "plaszczyzna ciecia ... ponizej wierzchu plytki") - w pliku zostaje stolik / podstawka wokol plytki. Wlasne proby: 11 z 11 takich skanow (3 rodzaje plytek; podloze kolo 150 i 200 mm albo kwadrat 180 mm; na wysokosci spodu plytki, 10 i 25 mm nizej) = `malo_stozkow`, 0 z 3 stozkow. Okno "Dzien skanera" pisze wtedy "... nie widac trzech stozkow znacznikow (znaleziono 0) ... ZROB TAK: sprawdz, czy stozki ... sa czyste ..., czy cala plytka miesci sie w polu skanera ...", program "Stanowisko": "w skanie widac 0 z 3 znacznikow plytki - plytka nie miesci sie w polu skanera albo lezy poza srodkiem" - oba teksty wskazuja ZLA przyczyne. Dokument: tabela kroku 2.3 odsyla do 2.4 "poda wymiar pola", a dopiero wiersz "Gdy sie nie uda" kroku 2.4 mowi "poszukaj ... ustawienia, ktore obcina podloze" - sprzecznie z "bez obcinania" z 2.3 i bez nazwy tego ustawienia. Kazdy kolejny skan dnia bedzie czerwony tak samo. | Krok 2.3, tabela "Widzisz / Zrob": osobny wiersz "czerwone 'nie widac trzech stozkow (znaleziono 0)', a w podgladzie programu skanera wokol plytki widac stolik / podstawke" -> "ustaw linie wysokosci ciecia (okno kamery) albo plaszczyzne ciecia po skanie POWYZEJ stolika i co najmniej 3 mm PONIZEJ wierzchu plytki (zostaje wierzch, stozki, scianka z rowkiem), zeskanuj / zapisz jeszcze raz". W "Co zrobic" zamiast "bez obcinania": "nie obcinaj wierzchu plytki; stolik i podstawke obetnij linia ciecia". Zdanie w.207-208 odwrocic: najpierw podloze (sprawdzalne okiem w podgladzie), potem pole. Lista zbiorcza poz. 3 i arkusz w.56 zostaja. Dla koordynatora: poprawic zdanie w.94 sciagi ("najlepiej ponizej calej plytki" -> "ponizej wierzchu, powyzej stolika") przed wydrukiem; rozwazyc poprawke programu przed 0.3.3 (sekcja 5 p. 2). |
| N2 | P | dokument w.284, w.407-409; arkusz w.140-146 | Dwie plytki o tym samym numerze. Wlasciciel ma plytki kwadratowe 1-6 i okragle ramkowe 1-6 (P2). Krok 2.7 p. 5 i krok 3.8 p. 5: "zeskanuj plytke z pracami ... Powtorz z plytka okragla (ramkowa)". Kwadrat nr 1, potem okragla nr 1 w ciagu 60 minut (`ponowny_skan_okno_min = 60`): program pyta "Ponowny skan tej samej plytki?" (przyciski "Tak, to ponowny skan" / "Nie, to nowy wsad") - dokument tego pytania nie zna. Gorzej: gdy kwadrat nr 1 lezy jeszcze na ramce W, pod nim zapala sie wynik NOWEGO skanu, bez komunikatu (recenzja PR #55, uwaga B1: mechanizm zastany, takze na `main`; poprawka O2 w toku). Wlasciciel zapisze "gniazda swieca w kolorach mapy" przy zlej plytce. | Krok 3.8 (i 2.7): zasada "przed skanem nastepnej plytki ZDEJMIJ poprzednia z ramki" i "uzyj plytek o roznych numerach (np. kwadratowa 1, okragla 2); gdy numer ten sam - program zapyta 'Ponowny skan tej samej plytki?': kliknij 'Nie, to nowy wsad'". Wiersz w arkuszu 3.8: "pytanie o ponowny skan: [ ]". S2b: potwierdzic na atrapie po poprawce B1 paczki O2, co ramka robi do czasu odpowiedzi. |
| N3 | P | dokument w.408-409, w.413-415; arkusz w.144 | (Z przegladu kodu `integ`, bez proby na atrapie.) Proba celowa (c): "przy plytce kwadratowej podaj inny numer niz wybity" -> obiecany zolty panel "Plytka N: Numer plytki nie zgadza sie ze skanem". Komunikat powstaje tylko, gdy numer jest PODANY recznie, a w pliku wyniku jest wazny numer z dolkow, rozny od podanego (`kontroler_api.py:3240-3257`). Kwadrat, o ktorego numer program pyta, to kwadrat BEZ odczytanych dolkow (dolki kwadratu leza 52,5-57,6 mm od srodka; wg recenzji PR #55 D4 "w praktyce nie wystapi") - komunikatu (c) nie bedzie; zamiast niego (plytka na ramce) wyjdzie (b) "Na ramce lezy inna plytka niz zeskanowana" albo pytanie "Plytka nie z tego trybu". Gdy dolki kwadratu sa w skanie, program o numer nie pyta wcale. Wlasciciel zapisze "komunikat (c): nie dziala". | Probe (c) robic na plytce OKRAGLEJ ramkowej, ktorej numer program odczytal sam: "kliknij 'Zmien numer' przy tej plytce i podaj inny numer" -> (c); potem "Zmien numer" z powrotem -> komunikat znika, ramka swieci. Dopisac zdanie z decyzji recenzji O2: "gdy poprawiasz numer ZLE odczytany z dolkow, ramka zostaje ciemna i komunikat (c) zostaje - to wazny wynik, zapisz numer wybity i odczytany". S2b: 3 proby celowe na atrapie (pozycja 13 listy wykonawcy) wykonac doslownie wg tekstu kroku. |
| N4 | P | dokument w.36-39, w.397-419 | Ramka poranna jako jedyna (odpowiedz P1 "poranna"). Krok 3.8 opisuje prace wieczorna ("wieczorem wynik nie wraca", tytuly komunikatow wieczornych). Plytka 4-6 zeskanowana w trybie wieczornym = "Plytka nie z tego trybu" (tabela kroku 2.7), a krok 3.8 nie mowi, ze trzeba przelaczyc program na "Poranek", ani co wtedy ma swiecic na ramce P (rano ramka pracuje wg planu pieca: kuwety, "Zamknij piec"; tytul (b) rano brzmi "Na ramce lezy plytka, ktorej nie ma w planie pieca" i - wg recenzji PR #55 P1 - jego tresc bedzie zmieniona). Zaden wiersz "Udalo sie, gdy" nie opisuje ramki porannej. Nie sprawdzalem przebiegu porannego na atrapie (brak czasu) - stad "nieudowodnione". | S2b: przejsc krok 3.8 na atrapie ramki P ze skanem sztucznym plytki 4 (kwadrat i okragla ramkowa) w trybie "Poranek" i dopisac 4-6 wierszy "Ramka poranna: ..." (przelaczenie trybu, co swieci bez projektow i bez pliku zlecen, jaki komunikat przy plytce bez numeru - nowy tekst O2). Jesli bez pliku zlecen ramka P nie zaswieci niczego - napisac to wprost i odeslac do kroku 3.7 (pozycje 4 / 5 menu) jako jedynej proby diod ramki porannej. |
| N5 | P | `narzedzia/pole_skanu.py:48,270,432-433`; dokument w.224-230; arkusz w.61 | Proba z kartonem przy DUZYM polu skanera (czyli w dobrym przypadku). Karton w polu kolowym 150 mm: "Dane mieszcza sie w kole o srednicy ok. 151,2 mm. ... Dane sa wieksze niz jakakolwiek plytka (ponad 140 mm). UWAGA: w skanie jest prawdopodobnie PODLOZE (stolik / uchwyt wokol plytki). ... Program moze nie rozpoznac plytki zeskanowanej razem z podlozem." i `podloze w skanie: PRAWDOPODOBNIE TAK`; to samo dla kartonu 150 x 150 calego w polu i kartonu w polu 130 x 90 (3 z 3 prob z danymi > 140 mm). Dokument dwa wiersze nizej podaje ten sam napis jako objaw porazki ("Gdy sie nie uda: narzedzie pisze 'w skanie jest prawdopodobnie PODLOZE' ..."). Wlasciciel uzna udany pomiar pola za nieudany albo zacznie szukac obcinania podloza. | Narzedzie: gdy plytki nie rozpoznano, a dane sa plaskie (np. 98 % punktow w pasie 1 mm wokol plaszczyzny) - zamiast uwagi o podlozu: "to plaski arkusz (karton) albo sam stolik - wymiary ponizej to pole skanera"; test: karton w polu 150 mm bez slowa "PODLOZE". Minimum: zdanie w kroku 2.4 "przy kartonie uwage o podlozu pomin - liczy sie wiersz 2". |
| N6 | P | dokument w.174-176, w.269-272, w.453, w.471-472; arkusz w.159 | Dane pacjentow. Krok 2.1 kaze wskazac oknu folder, do ktorego zapisuje program skanera (P5), krok 2.6 - wykonac "Na koniec: kopia CALEGO folderu zlecen programu skanera" i spakowac. Jesli skaner pracuje juz w laboratorium, w tym folderze leza zlecenia pacjentow (nazwy folderow = nazwiska); trafia do ZIP-a, a ZIP wg czesci 5 p. 1 jedzie na PC do `<PC-katalog>\sprzet_2026-11-28\skaner\`. Czesc 5 mowi "czego NIE przywozic: ... zlecen z danymi pacjentow ... przejrzyj nazwy plikow" - ale paczka jest juz spakowana. Zasada 2 dokumentu dotyczy tylko nazw NOWYCH zlecen. Nie wiemy, czy w programie skanera sa zlecenia pacjentow (nie ma takiego pytania). | Pytanie P5 rozszerzyc: "czy w programie skanera sa juz zlecenia pacjentow?". Krok 2.1: "jesli tak - zaloz osobny folder na zlecenia testowe (albo wskaz tylko folder zlecenia TEST1) i tylko jego pokaz oknu"; krok 2.6: "kopie calego folderu rob tylko wtedy, gdy w folderze sa wylacznie zlecenia testowe; inaczej pomin z powodem ('dane pacjentow')". Sekcja 5 p. 3. |
| N7 | P | arkusz w.62-97; dokument w.251-265; `narzedzia/pole_skanu.cmd:20-26` | Powiazanie "co naprawde lezalo" z plikiem wyniku. Wszystko, co wypisuje `pole_skanu`, i tak wraca w plikach `wyniki\pole_skanu\*.json`; jedyna rzecz, ktorej w plikach NIE MA, to prawda: jaka plytka lezala i co na niej bylo (pusta / praca przy dolkach / dolki zaklejone). Tabela 2.5 ma numer kolejny, ale nie ma godziny ani nazwy pliku; tabela 2.5a nie ma nawet kolejnosci (3 kratki na plytke). Program skanera moze nazywac pliki tak samo w kazdym zleceniu (U4), a skan z zaklejonymi dolkami nie ma numeru - po weekendzie nie da sie przypisac pliku do plytki, czyli sprawdzic, DLACZEGO okragla zostala kwadratem (dane do wariantu C). Do tego skala: krok 2.5a "30 minut", a P2 dopuszcza 8 plytek okraglych x 3 skany = 24 skany (krok 2.4 liczy "5 minut na plik"); tabela 2.5a ma 4 wiersze. | `pole_skanu.cmd`: drugie pytanie "Co lezy na stoliku? (np. okr-ramk 2, dolki zaklejone; sam Enter = pomin)" zapisywane do `.json` i `.txt` (pole `opis_czlowieka`); test. Arkusz: w tabelach 2.5 i 2.5a kolumna / dopisek "godzina wyniku (z wiersza 'Zapisano: ...')". Krok 2.5a: "wystarcza 2 plytki ramkowe (jedna 1-3, jedna 4-6) i 1 testowa = 9 skanow, ok. 60 minut; wiecej - jesli jest czas"; tabela 2.5a 6 wierszy; dopisac 3 wiersze "co wynik znaczy" (sekcja 5 p. 4). |
| N8 | P | dokument w.217-227; arkusz w.57-61; `pole_skanu.py:43-46,325-335,461-465` | Wymiar pola z PLYTKI bywa bledny, a probe z kartonem dokument kaze robic tylko przy wierszu "Cala plytka jest w skanie". Proby pola KOLOWEGO na plytce rozpoznanej (5): kwadrat, pole 100 mm w srodku -> "POLE SKANERA MA OK. 100,1 mm" (dobrze); okragla testowa, pole 120 przesuniete o 15 mm -> 119,2 i 120,0 mm (dobrze, 2 proby); kwadrat, pole 120 przesuniete o 10 mm -> "POLE SKANERA MA OK. 124,7 mm (srodek pola 13,0 mm ...)" (blad +4,7 mm; okrag dopasowany do 17 kierunkow); kwadrat, pole 110 mm DOKLADNIE w srodku -> "POLE NIE JEST KOLEM (albo plytka lezy z boku pola): dane najwezej 94,6 mm x 95,4 mm" - nieprawda (pole jest kolem 110 mm; na okregu 22 z 26 koncow danych = 84,6 %, prog 85 %), a rada "przesun plytke na srodek i zeskanuj jeszcze raz" niczego nie zmieni. Wlasciciel wpisze do arkusza "pole nie jest kolem: 94,6 x 95,4 mm". Karton daje wynik dobry w 5 z 5 prob (prostokat 100 x 80 i 130 x 90, kolo 120 i 150, karton 150 x 150). Do tego wiersz 2 ma 4 warianty, a dokument i arkusz 3: brakuje "Skan konczy sie tuz przy brzegu plytki (albo brzeg jest zasloniety): wielkosci pola z tego skanu nie da sie podac" (okragla ramkowa w polu 98 mm: brzeg 3 z 72). | Krok 2.4: proba z kartonem ZAWSZE, jako pierwszy i glowny pomiar pola (arkusz: wiersz kartonu na gorze); wynik z plytki jako drugi, z dopiskiem "przyblizony". Dopisac czwarty wariant wiersza 2 i kratke w arkuszu. Narzedzie (tanie): przy `nie_kolowe` wypisac tez srednice okregu dopasowanego ("konce danych pasuja do okregu ok. 109,7 mm w 22 z 26 kierunkow") zamiast samego "nie jest kolem"; test: kwadrat w polu 110 mm bez przesuniecia. |
| N9 | D | dokument w.287 | "Plytka kwadratowa: program pyta 'Podaj numer plytki'" - prawda tylko, gdy dolki kwadratu sa poza polem skanera; gdy pole obejmuje dolki (wg recenzji PR #55 leza 52,5-57,6 mm od srodka, czyli pole ok. 116 mm i wiecej), program czyta numer sam (skan pelny kwadratu nr 1: "Numer plytki wg programu: 1 (zrodlo: dolki)"; pole kolowe 100 i 110 mm: "nie odczytany"). | "program pyta ..., jesli sam nie odczytal numeru (zalezy od pola skanera)". Arkusz w.100 ma juz kratke. |
| N10 | D | `narzedzia/ramka_proba.py:124-143,388-397` | Klucz wpisany z litera spoza ASCII (np. "a" z ogonkiem przez prawy Alt): wyjatek `UnicodeEncodeError: 'latin-1' codec can't encode characters` zamiast "ZLY KLUCZ" (proba K14) - w menu slad bledu po angielsku. | W `polecenie_klucz`: klucz ze znakiem spoza ASCII = "ZLY KLUCZ (klucz ma tylko litery bez polskich znakow i cyfry)"; test. |
| N11 | D | `narzedzia/ramka_proba.py:67-75,101-107`; dokument w.336-337, w.341-342 | Klucz jest zapamietywany dla ADRESU. Wlasciciel wpisuje klucz przy `ramka-w.local`, potem (rada kroku 3.3) przechodzi na adres z cyfr - narzedzie pyta o klucz drugi raz (proba K11: ten sam program ramki pod innym adresem = kod 5), a dokument obiecuje "wiecej o klucz nie pyta". | Zapisywac takze wiersz wspolny (sam klucz), gdy plik nie ma jeszcze zadnego; albo zdanie w dokumencie "po zmianie adresu zapyta jeszcze raz". |
| N12 | D | `narzedzia/.gitignore`; `narzedzia/*.cmd` (`WYN=%TU%..\wyniki\...`) | Narzedzie uruchomione z kopii repo (S2b, koordynator) zaklada `Ramki/etap3/testy_sprzet_2026-11-28/wyniki/` - katalog NIE jest ignorowany (`git check-ignore`: tylko `klucz_ramki.txt`), a wyniki zawieraja nazwy plikow skanow i `adres_ramki.txt`. | `.gitignore` w katalogu paczki: `wyniki/`. |
| N13 | D | `ZALACZNIKI.md` w.19, w.25-30, w.32-34 | (a) `sprawdz_ramke.sh` przypisany do krokow 8-9 instrukcji; w instrukcji jest w kroku 11 (w.363) i w uwadze kroku 1 (w.59); krok 9 to "Kontrola z laptopa". (b) Tabela B ma 8 nazw, samokontrola liczy 10 (`okragla_wieczorna_r54`, `okragla_poranna_r54` pominiete) - a dokument w.149 kaze czekac na "10 z 10". (c) "Okno programu nie wypisuje nazwy rodzaju plytki" - okno "Dzien skanera" wypisuje ("cala plytka, uklad okragla_ramkowa_wieczorna", `dzien_skanera_rdzen.py:1154`). | Poprawic 3 miejsca. |
| N14 | D | dokument w.149, w.262, w.403 | 3 z 13 miejsc `[DO POTWIERDZENIA NA 0.3.3]` da sie sprawdzic juz dzis (nie zaleza od paczki): w.262 napisy `program mowi:` pochodza z narzedzia (sprawdzone: "okragla ramkowa (do ramki), wieczorna [okragla_ramkowa_wieczorna], PEWNIE", "okragla testowa (poza ramka), ...", "kwadratowa, ..."); w.403 wiersze `[ramki]` sa w `ustawienia.przyklad.toml` od dawna (`wieczorna_host = "ramka-w.local"`, `klucz = ""`); w.149 `ustawienia.przyklad.toml` na `integ` ma 10 ukladow w `[plytki]` (samokontroli nie uruchamialem). Pozostale 10 + 4 zaleza od paczki / scalenia O2 - znaczniki uzasadnione. | S2b: te 3 potwierdzic jako pierwsze; w.262 mozna zdjac od razu. |
| N15 | D | dokument w.45-49; `ZALACZNIKI.md` w.17-18 | "Druga ramka musi dostac TEN SAM klucz" jest tylko w zalaczniku. Przy odpowiedzi P1 "obie" i dwoch ramkach instalowanych skryptem bez opcji `--klucz` druga ramka pokaze w programie "zly klucz". | Jedno zdanie w P8. |
| N16 | D | dokument w.397, w.405, w.417 | Po `ramka.cmd` (pozycje 4 / 5) program "Stanowisko" moze przez chwile widziec ramke jako zajeta: na atrapie inny komputer dostaje odmowe `inny_laptop` przez 30 s po zakonczeniu pozycji 4 (proby co 5 s: 6 odmow, przyjecie w 30. sekundzie), mimo ze narzedzie zgasilo swoj plan. Dokument: "W pasku u gory: 'Ramki: W: gotowa'" bez slowa o stanie "drugi laptop". | "Gdy sie nie uda": "'drugi laptop' w pasku - zamknij `ramka.cmd`, poczekaj pol minuty". |
| N17 | D | `narzedzia/test_pole_skanu.py` | Galaz "podloze przy plytce ROZPOZNANEJ" jest bez testu (wykonawca: "nie ma czym sprawdzic"). Da sie: plytka okragla + podloze kolo 120 mm = rozpoznana i `podloze_prawdopodobne` True (proby S: 2 z 2). | Test z podlozem 120 mm. |
| N18 | D | dokument w.207, w.265, w.46 | Jezyk - nowe miejsca: "na skanach sztucznych przy polu skanera 90 mm ..." (w.207), "[... na skanach sztucznych bez scianki i dolkow: 4 z 4 'kwadratowa']" (w.265), "zapisuje go na ramce w pliku `/etc/ramka/ramka.json`" (w.46). | "w naszych probach bez skanera"; sciezke pliku zostawic w zalaczniku, w P8 "w pliku ustawien ramki (zna go osoba, ktora wgrywala program)". |
| N19 | D | dokument (calosc), arkusz | Dlugosc 9,6 strony (cel: ok. 9); 155 wierszy dokumentu i 71 wierszy arkusza ma ponad 90 znakow; tabele arkusza trzymaja sie tylko w czcionce o stalej szerokosci; forma do druku (PDF / HTML, U20) odlozona do S2b. | Po odpowiedziach P1-P8 zastapic sekcje 0 ustaleniami (ok. -0,9 strony wg wykonawcy) i wykreslic kroki, ktore odpadly; PDF / HTML. |
| N20 | D | `narzedzia/dzien_skanera.cmd`; `ramka.cmd` | Drobne zastane: skrot awaryjny `narzedzia/dzien_skanera.cmd` zostaje (decyzja S2b po potwierdzeniu `Dzien_skanera.cmd`); przesuniecie wpisane slowem w menu `ramka.cmd` dalej daje `usage` po angielsku (wg wykonawcy, U16 odlozone); "Ramka W zna 3 rodzajow plytek" (odmiana). | S2b. |
| N21 | D | dokument w.184-189, w.267-273 | Znaczniki `[NIE SPRAWDZONE BEZ SPRZETU]`: 20 przy krokach + lista 18 pozycji; bez znacznika sa kroki 2.2 (ustawienia prawdziwego programu skanera) i 2.6 (kopia prawdziwego folderu zlecen: rozmiar, czas, pliki trzymane przez program skanera). Lista zbiorcza poz. 1 i 8 pokrywa to tylko posrednio. | Dopisac 2 znaczniki. |

### 1a. Dlugosc

Pomiar wlasny (ta sama metoda co w rundzie 1): dokument 492 wiersze, 4331 slow, 27908 znakow = 9,6 strony A4 (450 slow na
strone); arkusz 178 wierszy, 1527 slow = 3,4 strony; zalaczniki 96 wierszy, 1057 slow = 2,3 strony (nie dla wlasciciela).
Liczby wykonawcy potwierdzone co do slowa. Z karta "Dnia skanera" i sciaga skanera wlasciciel ma w reku ok. 13 stron
tresci + arkusz - o ok. 5 mniej niz w rundzie 1. Najdluzsze czesci: sekcja 0 (pytania) i czesc 3 (ramka).

### 1b. Jezyk

19 z 19 cytatow z tabeli 1b rundy 1 usunietych albo przepisanych (wyszukiwanie w dokumencie: "exFAT", "sumy", "pakiety",
"isolcpus", "dtparam", "usluga systemowa", "ETAP 2", "jednym ruchem", "slucha w sieci", "w swoich blokach", "Sprawa 4",
"-m stanowisko", "rozszerzenie", "Zalacznik A" - po 0 trafien; "Stan:" 1 raz, w naglowku "Stan: 21.11.2026"; "uklad" 1 raz,
w doslownym wierszu samokontroli w.149; "atrap" 1 raz, we wstepie z wyjasnieniem). `wieczorna_host` pokazany jako wiersz
"przed -> po" (w.400-401), `findstr` ma zdanie "po co" (w.438). Nowe miejsca: 3 (N18). Nazwy `okragla_ramkowa_wieczorna` /
`okragla_ramkowa_poranna` w kroku 3.7 (w.379) sa potrzebne - wlasciciel przepisuje je z ekranu.

### 1c. Czy dokument obiecuje cos, czego program nie robi

Tak, w 3 miejscach: proba (c) kroku 3.8 (N3), "plytka kwadratowa: program pyta o numer" (N9), "narzedzie wiecej o klucz
nie pyta" (N11). Przemilcza 2 zachowania wazne tego dnia: pytanie o ponowny skan i wynik pod zla plytka przy dwoch plytkach
o tym samym numerze (N2), praca ramki porannej (N4). Zgodne z decyzjami recenzji O2: "wieczorem wynik nie wraca - trzeba
nowego skanu" (w.412-413), ramka ciemna + zolty panel w 3 sytuacjach (w.413-415), tytul poranny (b) w zalaczniku C.
Rzeczy, ktorych program nie robi, nazwane wprost: brak zapisu kalibracji ("Dzis tylko notujemy liczby", w.388), program
nie kopiuje skanow (w.301-302, w.455-456), miara rowka nie rozstrzyga (w.245-246).

## 2. Wlasne proby

| nr | polecenie / proba | wynik |
|---|---|---|
| 1 | `py.cmd -m pytest ..\etap3\testy_sprzet_2026-11-28\narzedzia -q -p no:cacheprovider` (kopia `rec-s1`, kod O1) | 51 passed, 0 failed, 116,5 s, kod 0 |
| 2 | `pole_skanu.zmierz`: plaski karton (siatka 1 mm) w polu prostokatnym 100 x 80 mm | nierozpoznana (dobrze); "Dane skanu: najwezej 80,0 mm, w poprzek 100,0 mm ... DANE NIE SA KOLEM: 80,0 x 100,0 mm"; podloze: nie widac |
| 3 | karton w polu prostokatnym 130 x 90 mm | "najwezej 90,0 mm, w poprzek 130,0 mm", DANE NIE SA KOLEM; kolo opisane 158 mm -> "UWAGA: w skanie jest prawdopodobnie PODLOZE" (N5) |
| 4 | karton w polu kolowym 120 mm | "120,0 x 120,0", "Dane mieszcza sie w kole o srednicy ok. 121,2 mm" (blad +1,2 mm); bez uwagi o podlozu |
| 5 | karton w polu kolowym 150 mm | "149,9 x 151,1", "kolo ok. 151,2 mm" + "Dane sa wieksze niz jakakolwiek plytka (ponad 140 mm). UWAGA: ... PODLOZE"; `podloze w skanie: PRAWDOPODOBNIE TAK` (N5) |
| 6 | karton 150 x 150 mm caly w polu | "150,0 x 150,0", DANE NIE SA KOLEM + uwaga o podlozu (N5) |
| 7 | kwadrat nr 1 w polu prostokatnym 130 x 90 mm (ciecie plaszczyznami) | rozpoznana; brzeg 36 z 72; "Plytka NIE jest cala w skanie"; "POLE NIE JEST KOLEM (albo plytka lezy z boku pola): dane najwezej 90,0 mm x 96,0 mm"; okrag wpisany 90,2 mm |
| 8 | kwadrat nr 1 w polu prostokatnym 100 x 80 mm | rozpoznana; brzeg 35 z 72; "POLE NIE JEST KOLEM ...: 80,0 mm x 96,0 mm"; okrag wpisany 80,2 mm |
| 9 | kwadrat nr 1 w polu prostokatnym 140 x 110 mm (cala plytka w polu) | brzeg 72 z 72; "Cala plytka jest w skanie ...: pole skanera jest CO NAJMNIEJ takie jak plytka" |
| 10 | okragla ramkowa nr 1 w polu prostokatnym 130 x 90 mm | rozpoznana, numer 1 z dolkow; brzeg 56 z 72; "POLE NIE JEST KOLEM ...: 90,0 mm x 100,1 mm" |
| 11 | kwadrat nr 1, pole kolowe 100 mm w srodku plytki (`synth.przytnij_do_kola`) | rozpoznana (powod: ksztalt), dolki 0 z 4, numer nie odczytany; "POLE SKANERA MA OK. 100,1 mm (srodek pola 0,0 mm ...)"; do tego "UWAGA: program mowi 'kwadratowa', a dane skanu sa kolem ok. 100,1 mm - tyle, ile ma plytka OKRAGLA" (uwaga falszywa dla prawdziwego kwadratu w polu ok. 100 mm; sformulowana jako "mozliwe", kaze zapisac prawde) |
| 12 | kwadrat nr 1, pole kolowe 110 mm w srodku plytki | rozpoznana, dolki 2 z 4, brzeg 27 z 72; "POLE NIE JEST KOLEM (albo plytka lezy z boku pola): dane najwezej 94,6 mm x 95,4 mm" - NIEPRAWDA (N8); okrag dopasowany 109,7 mm, na okregu 22 z 26 koncow |
| 13 | kwadrat nr 1, pole kolowe 120 mm przesuniete o 10 mm | brzeg 48 z 72; "POLE SKANERA MA OK. 124,7 mm (srodek pola 13,0 mm od srodka plytki). Plytka lezy z boku pola ..." - blad +4,7 mm (N8) |
| 14 | kwadrat nr 1, pole kolowe 140 mm przesuniete o 30 mm | NIE rozpoznana (2 z 3 stozkow); "DANE NIE SA KOLEM: 88,1 x 96,1 mm"; zadnego zdania o srednicy pola (w rundzie 1: "ok. 134,7 mm") |
| 15 | okragla testowa nr 8, pole kolowe 120 mm przesuniete o 15 mm | rozpoznana, numer 8; brzeg 52 z 72; "Plytka NIE jest cala w skanie"; "POLE SKANERA MA OK. 119,2 mm (srodek pola 14,5 mm ...)"; "Plytka lezy z boku pola - przesun ..." |
| 16 | okragla testowa nr 8, pole kolowe 120 mm, srodek (-12, 9) | brzeg 53 z 72; "POLE SKANERA MA OK. 120,0 mm (srodek pola 14,9 mm ...)" |
| 17 | okragla ramkowa nr 1, pole kolowe 110 mm przesuniete o 12 mm | NIE rozpoznana (1 z 3 stozkow); "DANE NIE SA KOLEM: 93,0 x 100,0 mm" |
| 18 | okragla ramkowa nr 1, pole kolowe 98 mm w srodku | rozpoznana, numer 1; brzeg 3 z 72; "Skan konczy sie tuz przy brzegu plytki (albo brzeg jest zasloniety): wielkosci pola z tego skanu nie da sie podac" (czwarty wariant - N8) |
| 19 | okragla ramkowa nr 1, pole kolowe 104 mm w srodku | brzeg 72 z 72; "Cala plytka jest w skanie ..." |
| 20 | skany pelne: kwadrat nr 1, okragla ramkowa nr 1, okragla testowa nr 8 - wiersz 6 i blok "DO ARKUSZA" | 3 z 3 rozpoznane PEWNIE, numer z dolkow; scianka "widac (72 z 72 kierunkow, do 7,8-7,9 mm ponizej wierzchu)"; rowek: "nie dotyczy" / "scianka cofa sie o 0,77 mm (projekt: 0,8 mm); ... w 70 z 72 policzonych kierunkow - narzedzie NIE rozstrzyga" / "nie dotyczy" |
| 21 | okragla ramkowa nr 1 bez scianki; okragla ramkowa nr 2 bez scianki i z zaslonietymi dolkami A-D | pierwsza: "okragla ramkowa (do ramki) ..., PEWNIE", scianka "NIE widac (slady w 2 z 72 kierunkow)", rowek "NIE widac - skan nie siega 2,5 mm ponizej wierzchu"; druga: "kwadratowa, wieczorna [wieczorna], PEWNIE, powod: dolki_wykluczaja - UWAGA: dane sa kolem jak plytka OKRAGLA" (ograniczenie O1 odtworzone na `integ`, narzedzie je sygnalizuje) |
| 22 | `pole_skanu.main` dwa razy: plik `skan.stl` z folderu `a` i z folderu `b` do jednego `--wynik` | 2 x kod 0; 2 pliki `.json` (`skan_20261121_142927_pole.json`, `skan_20261121_142933_pole.json`) |
| 23 | `pole_skanu.main` na pliku pustym (0 bajtow) | kod 2; "BLAD: plik pusty.stl jest pusty albo uszkodzony - nie da sie go wczytac jako skanu. Zapisz skan w programie skanera jeszcze raz ..." (U10 poprawiona) |
| 24 | skany pelne 3 rodzajow plytek z plaskim podlozem - 15 prob + 3 bez podloza (tabela 2b) | podloze >= 150 mm: 11 z 11 nierozpoznanych (`malo_stozkow`, 0 z 3), narzedzie: "UWAGA: ... PODLOZE" 11 z 11; podloze <= 120 mm: 4 z 4 rozpoznane; bez podloza 3 z 3 |
| 25 | `ramka_proba` na atrapie ramki W Z KLUCZEM (kod `integ`): `stan` bez klucza / ze zlym kluczem (`--klucz`) / z dobrym | kod 5 "RAMKA ODPOWIADA, ale wymaga klucza (odpowiedz 401): nie podano klucza." + 3 wiersze rady; kod 5 "... podany klucz NIE pasuje do ramki (klucz zzzz..., zrodlo: opcja --klucz)"; kod 0 "RAMKA ODPOWIADA (2 ms): ramka wieczorna (W), program ramki 0.1.3 ..." |
| 26 | `test-led`, `gniazda --uklad auto --wszystkie`, `uklady` bez klucza | 3 z 3 kod 5 z tym samym komunikatem (menu `ramka.cmd` przechodzi wtedy do pytania o klucz) |
| 27 | polecenie `klucz`: sam Enter; zly klucz; dobry klucz wpisany w cudzyslowie i ze spacjami | kod 5 "Nie podano klucza - nic nie zapisano"; kod 5 "ZLY KLUCZ (zly-...): ramka go nie przyjela - nic nie zapisano" (pliku nie ma); kod 0 "KLUCZ DOBRY (Ab3d...) - zapamietany w pliku klucz_ramki.txt obok narzedzi" (plik: naglowek + wiersz `127.0.0.1 <klucz>`) |
| 28 | po zapisie: `stan` bez opcji; ta sama ramka pod adresem `localhost` | kod 0; kod 5 "nie podano klucza" (klucz zapamietany dla adresu - N11) |
| 29 | klucz tylko w `[ramki]` pliku ustawien programu (`--ustawienia`); zly klucz w pliku `klucz_ramki.txt` + dobry w ustawieniach | kod 0; kod 5 "... (klucz star..., zrodlo: plik klucz_ramki.txt)" - plik ma pierwszenstwo, menu zapyta o klucz ponownie |
| 30 | polecenie `klucz`, wpisany klucz z litera spoza ASCII | wyjatek `UnicodeEncodeError` zamiast "ZLY KLUCZ" (N10) |
| 31 | atrapa BEZ klucza: polecenie `klucz`; `stan --klucz <cokolwiek>`; `uklady`; `gniazda --wszystkie` dla 3 rodzajow plytek ramki W | "Ta ramka NIE wymaga klucza - nic nie trzeba wpisywac" (kod 0); kod 0; "Ramka W zna 3 rodzajow plytek: okragla_ramkowa_wieczorna, wieczorna, wieczorna_r54 / DOMYSLNY: wieczorna"; swieci 19 z 19, 19 z 19, 20 z 20 gniazd |
| 32 | ramke trzyma inny komputer (plan obcego wyslany PIERWSZY, kod 200): `gniazda --wszystkie`, `gniazda` po kolei, `test-led`, `stan`; potem: podtrzymanie planu 40 s; plytka zdjeta w trakcie `gniazda` po kolei; ile trwa blokada po narzedziu | kod 1 "RAMKA ODMOWILA: kod 409 inny_laptop - ramke obsluguje teraz inny komputer: zamknij program Stanowisko ..." + "Ramki NIE zgaszono tym narzedziem"; kod 1, 1 odmowa i koniec (bylo 19); kod 1 z rada; kod 0; plan obcego nietkniety. Podtrzymanie: 19 z 19 po 0 s i po 40 s. Plytka zdjeta: "RAMKA NIE CZYTA JUZ PLYTKI nr 1 (odczyt teraz: 0) - gniazda nie swieca ...", w CSV "BRAK PLYTKI (odczyt 0)", kod 1. Blokada: inny komputer dostaje 409 przez 30 s po zakonczeniu narzedzia (N16) |
| 33 | wstrzykniecie W1: odpowiedz 401 nierozpoznana (`e.code == 4010`) | 3 failed, 28 passed - zlapane |
| 34 | W2: `gniazda` bez watku podtrzymania planu | 2 failed, 29 passed - zlapane (runda 1: 17 passed) |
| 35 | W3: brak przerwania po odmowie `inny_laptop` | 2 failed, 29 passed - zlapane |
| 36 | W4: scianka boczna nigdy niewidoczna | 1 failed, 19 passed - zlapane (runda 1: 9 passed) |
| 37 | W5: miara rowka (uskok scianki) zawsze 0 | 1 failed, 19 passed - zlapane |
| 38 | W6 (U1): pole kolowe bez sprawdzenia, czy konce danych leza na okregu | 1 failed, 19 passed - zlapane |
| 39 | W7 (U2): "cala plytka" takze przy brakach brzegu | 1 failed, 19 passed - zlapane |
| 40 | W8 (U4): nazwa wyniku bez licznika | 1 failed, 19 passed - zlapane |
| 41 | po wstrzyknieciach: `git -C rec-s1 status --short` | pusty (8 z 8 cofnietych) |
| 42 | `py.cmd <integ>\Ramki\etap3\odbior_koncowy\narzedzia\t13_higiena.py --repo <PC-katalog>\qc-wt\rec-s1 --do HEAD --json ...` | kod 0; "NARUSZENIA (grupa E3 i sciezki poza listami): 0"; "WYNIK T13: ZAL z odstepstwem O11 (0 naruszen; 7 plikow napisow ekranu nie-ASCII; 10 kopii bajtowych R58 ...)"; 0 wpisow dotyczacych plikow paczki |
| 43 | pomiar dlugosci, ASCII, koncow wierszy, `git check-ignore` | sekcje 1a i 4 |

Proby niewazne (nie licza sie): 7 prob plytek w polu prostokatnym / przesunietym z pierwszej serii (ciecie wg srodkow
trojkatow) i 4 proby "ramka zajeta" z pierwszej serii (plan "obcego komputera" zostal odrzucony kodem 409, bo chwile
wczesniej ramke obslugiwalo narzedzie - stad pomiar blokady 30 s w probie 32); druga seria pola przerwala sie raz na
braku pakietu `shapely` (ciecie plaszczyznami przepisane na `slice_faces_plane`). Wszystkie powtorzone, wyniki w tabeli
z powtorek. Proby wazne: 44 `pole_skanu`, 34 `ramka_proba`. Ciezkie serie szly przez `ciezki.ps1 -Tor 4`
(3 uruchomienia, 14:26-14:42). Po probach nie zostal zaden moj proces python.

### 2a. Zgodnosc dokumentu z kodem `integ` (9f6d6a3) / `main` (1fce3fe) - 30 pozycji

| Nr | Co w dokumencie (wiersz) | Gdzie sprawdzone | Wynik |
|---|---|---|---|
| 1 | `C:\Stanowisko\Dzien_skanera.cmd` (w.174); sesje w `dane\dzien_skanera\` (w.272) | `instalacja/wzory/Dzien_skanera.cmd` (`main`): `--ustawienia "%KAT%ustawienia.toml" --dane "%KAT%dane\dzien_skanera"` | zgodne (instalacji z paczki nie uruchamialem - S2b) |
| 2 | okno "Dzien skanera - krok po kroku" (w.177) | `dzien_skanera.py:66` (tytul z dopiskiem "(sesja ...)") | zgodne |
| 3 | "Dodaj folder...", "Nie wiem, gdzie skaner zapisuje - szukaj", "Zrzut ekranu (za 3 s)" (w.174-176) | `dzien_skanera.py:140,142,226` | zgodne |
| 4 | "Otworz folder sesji", "Zakoncz i spakuj", "Nie udalo sie / pomijam, bo ..." (w.189, w.213, w.269) | `dzien_skanera.py:185,183,240` | zgodne |
| 5 | "Pomiar szczegolowy zaznaczonego skanu" (w.270) | `dzien_skanera.py:262` (pelny napis: "... (osobne okno)...") | zgodne |
| 6 | kroki okna 1-4 ustawienia, 5 pusta plytka, 6 prace cale, 7 to samo, 9 ukruszone, 12 "Skan 7: druga plytka", ostatni "Na koniec: kopia CALEGO folderu zlecen programu skanera" (w.184, w.193, w.237-240, w.269) | `dzien_skanera_kroki.toml`: 14 krokow w tej kolejnosci | zgodne; krok 12 przyjmuje wiecej niz 1 plik ("Oba pliki trafia do tego kroku") |
| 7 | "SKAN DOBRY: cala plytka, ...; obrys ... x ... x ... mm" (w.195-196) | `dzien_skanera_rdzen.py:1154,1115,1332` | zgodne (miedzy nimi "... mln trojkatow") |
| 8 | "... nie widac trzech stozkow znacznikow", "... nie widac plaskiego wierzchu plytki" (w.202-205) | `dzien_skanera_rdzen.py:1144,1140` | zgodne |
| 9 | "inna plytka niz w skanie ...", "TEN SAM plik", "ZROB TAK" (w.247-248) | `dzien_skanera_rdzen.py:1292,1284,1335` | zgodne |
| 10 | "Sesja spakowana: ... plikow", folder `paczka` (w.271-272) | `dzien_skanera.py:789`; `dzien_skanera_rdzen.py:58` | zgodne |
| 11 | `--nowa --zamknij-po 5`, wiersz "DZIEN SKANERA: sesja ...; ustawienia ...; foldery obserwowane: ..." (zalacznik D) | `dzien_skanera.py:868,873,917` | zgodne |
| 12 | `Polecenie.cmd narzedzia\pomiar_skanu\pomiar_skanu.py <skan.stl>` (zalacznik D) | plik `narzedzia/pomiar_skanu/pomiar_skanu.py` jest na `integ` | plik jest; uruchomienie z instalacji - S2b |
| 13 | "INSTALACJA: WSTRZYMANA - uzupelnij ustawienia.toml i uruchom zainstaluj.cmd ponownie (kod 10)", "INSTALACJA: GOTOWA - wersja biezaca ..." (w.124, w.137) | `instalacja/instalator.py:1409,1447` | zgodne |
| 14 | `SAMOKONTROLA: ZIELONA`, `OK modele: uklady plytek z [plytki]: poprawne 10 z 10` (w.148-149) | `samokontrola.py:225,887`; `[plytki]` w `ustawienia.przyklad.toml`: 10 pozycji | zgodne |
| 15 | `OK folder_skanera`, `OK ramka_wieczorna: ramka wieczorna odpowiada` (w.282, w.404) | `samokontrola.py:476,1097` (dalej nawias z adresem i rola) | zgodne |
| 16 | `[ramki]`: `wieczorna_host = "ramka-w.local"`, `poranna_host`, `klucz = ""` (w.397-401) | `ustawienia.przyklad.toml` | zgodne (za `klucz = ""` jest dlugi komentarz) |
| 17 | "Kto teraz pracuje?", "Folder skanera: dostepny", "Ramki: W: brak polaczenia", "W: gotowa (plytka 1)", "Test LED" (w.147, w.150-151, w.405-406) | `ui/napisy.py:20,55`; `ui/napisy_rano.py:143,147` | zgodne |
| 18 | "Podaj numer plytki", "Plytka nie z tego trybu", "-> Poranek", "bez projektu" (w.287, w.290, w.298) | `statusy.py:519,516,74`; `ui/czesci.py:426` | zgodne co do napisow; warunek pytania - N9 |
| 19 | mapa kolem, sciecie = plaska krawedz z kreska z przodu po prawej, "PRZOD PLYTKI" (w.288-289) | `ui/mapa.py:9-11,37`; `ui/napisy.py:85` | zgodne (koloru kreski nie sprawdzalem) |
| 20 | "Analiza skanu nie powiodla sie", "w skanie widac N z 3 znacznikow plytki - ..." (w.295-297; zalacznik C) | `statusy.py:334-335,556-559` | zgodne co do slowa (3 nawiasy z zalacznika C) |
| 21 | (a) "Plytka lezy na zlej ramce" + tresc (w.414; zalacznik C) | `statusy.py:453-455`; raport O2 13.2 | zgodne |
| 22 | (b) "Na ramce lezy inna plytka niz zeskanowana" + tresc; rano "Na ramce lezy plytka, ktorej nie ma w planie pieca" | `statusy.py:456-463` | zgodne; tresc poranna bedzie zmieniona (recenzja PR #55 P1) - S2b |
| 23 | (c) "Plytka N: Numer plytki nie zgadza sie ze skanem" + tresc, przycisk "Zmien numer" (w.415; zalacznik C) | `statusy.py:465-468`; `ui/napisy.py:94` | napisy zgodne; warunek powstania - N3 |
| 24 | "wieczorem wynik nie wraca - trzeba nowego skanu" (w.412-413) | raport O2 13.1 (zachowanie zastane) | zgodne (przegladem) |
| 25 | `ramka\rpi\`: `zainstaluj_ramke.sh`, `sprawdz_ramke.sh`, `ramka.service`, `ramka.json.wzor`; `/etc/ramka/ramka.json`; `sudo grep klucz /etc/ramka/ramka.json` (w.46; zalacznik A) | katalog `ramka/rpi` (`main`); `instrukcje/ramka_raspberry_pi.md` w.20, w.240 | zgodne |
| 26 | instrukcja `ramka_raspberry_pi.md`: 12 krokow; kroki 1-7, 10, 11 jak w zalaczniku A | naglowki "Krok 1" ... "Krok 12" | zgodne; `sprawdz_ramke.sh` w zlym kroku - N13 |
| 27 | `ramka.cmd` pozycja 1: "RAMKA ODPOWIADA (... ms): ramka wieczorna (W), program ramki ...", "plytka na ramce: 0" (w.339-340) | proba K3 | zgodne |
| 28 | "RAMKA ODPOWIADA, ale wymaga klucza", pozycja 7, "KLUCZ DOBRY ...", "ZLY KLUCZ", plik `klucz_ramki.txt` (w.336-344) | proby K1, K8, K9; `ramka.cmd:90-92` | zgodne |
| 29 | pozycja 4: lista rodzajow plytek z `okragla_ramkowa_wieczorna`, sam Enter = kwadratowa (w.377-380) | proba B3: "Ramka W zna 3 rodzajow plytek: okragla_ramkowa_wieczorna, wieczorna, wieczorna_r54 / DOMYSLNY: wieczorna" | zgodne na `integ` |
| 30 | wiersz 2 `pole_skanu`: "Cala plytka jest w skanie ... CO NAJMNIEJ takie jak plytka", "POLE SKANERA MA OK. ... mm", "POLE NIE JEST KOLEM (albo plytka lezy z boku pola): dane najwezej ... mm x ... mm"; karton: "PLYTKA NIE ROZPOZNANA"; blok "DO ARKUSZA (przepisz):" (w.215-225) | proby pola | zgodne; czwarty wariant - N8 |

Wynik: 30 z 30 napisow, nazw i sciezek istnieje w kodzie; 3 pozycje (18, 23, 26) z zastrzezeniem tresci (N9, N3, N13).

### 2b. Skan z podlozem - ocena ryzyka

Co zmierzylem (kod `integ`, narzedzie z `rec-s1`, skany sztuczne pelne + plaskie podloze widziane z gory, tylko poza
obrysem plytki):

| Podloze | Kwadrat nr 1 | Okragla ramkowa nr 1 | Okragla testowa nr 8 |
|---|---|---|---|
| brak | rozpoznana | rozpoznana | rozpoznana |
| kolo 110 mm, poziom spodu plytki | rozpoznana | - | - |
| kolo 120 mm, poziom spodu | rozpoznana | rozpoznana (narzedzie: podloze TAK) | rozpoznana (podloze TAK) |
| kolo 150 mm, poziom spodu | NIE (0 z 3 stozkow) | NIE | NIE |
| kolo 150 mm, 10 mm ponizej spodu | NIE | - | - |
| kolo 150 mm, 25 mm ponizej spodu | NIE | NIE | NIE |
| kolo 200 mm, 25 mm ponizej spodu | NIE | - | - |
| kwadrat 180 x 180 mm, poziom spodu | NIE | NIE | NIE |

Razem: podloze o srednicy >= 150 mm - 11 z 11 nierozpoznanych; podloze <= 120 mm - 4 z 4 rozpoznane. Wysokosc podloza nie
ma znaczenia (0, -10, -25 mm), liczy sie jego widoczna powierzchnia wobec plaskiego wierzchu plytki. To zachowanie
programu (`plate.rozpoznaj_uklad`, plik nietykalny), nie paczki.

Czy prawdziwy skaner oddaje podloze - czego nie wiemy:

1. Program skanera MA mechanizm odcinania podloza (sciaga skanera, w.94 i w.98: linia wysokosci ciecia w oknie kamery -
   "Only the range above the cutting line is to be scanned"; po skanie plaszczyzna ciecia, czerwona czesc "jig data" jest
   odcinana). Domyslne polozenie linii i to, czy da sie ja ustawic miedzy stolikiem a wierzchem plytki o grubosci ok. 8 mm,
   jest nieznane ("[DO SPRAWDZENIA NA EGZEMPLARZU]").
2. Nieznane: wymiar pola skanera (przy polu do ok. 120 mm podloza w skanie jest za malo, zeby szkodzilo), czy plytka
   lezy na podstawce mniejszej od siebie, czy czarny stolik w ogole daje punkty.
3. Nasze wlasne materialy pchaja w strone skanu Z podlozem: sciaga w.94 "linia ma byc PONIZEJ wierzchu plytki (najlepiej
   ponizej calej plytki)", okno "Dzien skanera" krok 5 "NIE obcinaj wierzchu plytki: plaszczyzna ma zostac ponizej
   wierzchu", dokument w.194 "bez wygladzania i obcinania". Wlasciciel, ktory chce pokazac scianke boczna i rowek (kroki
   2.5 i 2.5a tego wymagaja), zjedzie linia jak najnizej.

Ocena: ryzyko REALNE i o najwiekszym skutku w calym dniu - jesli wystapi, kazdy skan czesci 2 jest czerwony, program
"Stanowisko" nie pokaze zadnej mapy (krok 2.7), a krok 3.8 traci sens; komunikaty programu wskazuja zla przyczyne (pole,
brudne stozki). Prawdopodobienstwa nie da sie podac bez sprzetu; przy polu skanera ponad ok. 140 mm i linii ciecia
ponizej plytki uwazam je za wysokie. Obejscie jest tanie i dostepne na miejscu (linia / plaszczyzna ciecia powyzej
stolika, 3 mm albo wiecej ponizej wierzchu) - ale dokument go nie podaje (N1). Rozpoznanie przez czlowieka: narzedzie
`pole_skanu` nazywa podloze poprawnie (11 z 11), dokument prowadzi do niego dopiero w drugim kroku i w wierszu "Gdy sie
nie uda". Po poprawce N1 (i zdaniu w sciadze) ryzyko spada do "15 minut straty przy pierwszym skanie".

## 3. Kryteria zlecenia `s2a.md`

| Nr | Kryterium | Stan |
|---|---|---|
| 1 | testy narzedzi 0 failed; nowe testy padaja bez poprawek; min. 5 wstrzykniec (U1, U2, U3, U4, klucz) | potwierdzone wlasna proba: 51 passed; 8 wlasnych wstrzykniec, 8 zlapanych (U1, U2, U3 / rowek, U4, klucz, scianka, podtrzymanie planu, ramka zajeta) |
| 2 | tabela wymaganie wlasciciela -> miejsce w dokumencie: 8 z 8 | potwierdzone przegladem z zastrzezeniami: "co zmierzyc" i "po czym poznac sukces" - N2, N3, N4; "jakie pliki przywiezc" - N6; "arkusz" - N7 |
| 3 | dokument <= ok. 9 stron, arkusz <= 4 | czesciowo: 9,6 strony (N19); arkusz 3,4 - potwierdzone wlasnym pomiarem |
| 4 | kazda uwaga P (9) zamknieta albo odlozona | potwierdzone wlasna proba: 9 z 9 zamknietych (tabela 1.0) |
| 5 | `t13_higiena.py`: brak nowych naruszen w plikach paczki | potwierdzone wlasna proba: `--repo rec-s1 --do HEAD` (skrypt z `integ`): "NARUSZENIA: 0", "WYNIK T13: ZAL z odstepstwem O11"; 0 wpisow o `testy_sprzet_2026-11-28` i o raporcie S2 |
| 6 | `git status --short` pusty, galaz wypchnieta | stan galezi sprawdza koordynator; kopia `rec-s1` = d8e7087 |

Wymaganie wlasciciela (glowna miara):

| Punkt | Ocena po S2a |
|---|---|
| jeden dokument, prosty jezyk, do wydruku | spelnione co do tresci i jezyka; forma do druku (PDF / HTML) - S2b; 9,6 strony |
| to, czego potrzebuje w rece | narzedzia `pole_skanu.cmd`, `ramka.cmd` z kluczem, arkusz - spelnione na atrapach; na instalacji 0.3.3 - S2b |
| co przygotowac i zabrac | spelnione (sekcja 1; doszla kartka z kluczem, tasma papierowa, karton) |
| kolejnosc; jedna ramka; skaner; laptop albo PC | spelnione (zasada 4, skrot dnia, P4, P5); ramka poranna jako jedyna - N4 |
| co zmierzyc: pole skanera | czesciowo: liczby z kartonu dobre (5 z 5), z plytki zawodne przy polu kolowym (N8); karton przy duzym polu = uwaga o podlozu (N5) |
| co zmierzyc: dolki numeru, rowek pokrywki | spelnione (blok "DO ARKUSZA"; rowek jako liczby bez wniosku - uczciwie) |
| co zmierzyc: ograniczenie rozpoznania plytek okraglych | spelnione co do zasady (krok 2.5a: po co, trzy skany, co jest wynikiem zlym); N7 (skala, powiazanie z plikiem, "co wynik znaczy") |
| odczyt numeru plytki przez ramke; kalibracja gniazdo -> diody | spelnione (kroki 3.5-3.7); proby celowe kroku 3.8 - N2, N3 |
| jakie pliki przywiezc i gdzie polozyc | spelnione (czesc 5: 6 punktow, 6 podfolderow); N6 |
| po czym poznac, ze krok sie udal | 21 z 21 krokow; tresc bledna w 3.8 (c) - N3 |
| arkusz obserwacji | spelnione: da sie wypelnic dlugopisem, pola = kroki (1.1-3.9, czesc 4, czesc 5, P1-P8); N7, N8 |
| narzedzia sprawdzone na atrapach i na instalacji z nowej paczki | atrapy: tak (wlasne proby na `integ`); instalacja 0.3.3: S2b (swiadomie otwarte) |
| niesprawdzone oznaczone wprost | 20 znacznikow + lista 18 pozycji; 2 braki (N21) |
| pytania na poczatku, bez zgadywania | spelnione (P1-P8, termin 25.11, skutki); brakuje pytania o zlecenia pacjentow w programie skanera (N6) |

## 4. Zakres plikow i zasady

- Zakres: `git diff --name-only 8001b55...e3/sprzet` = 14 plikow: 12 w `Ramki/etap3/testy_sprzet_2026-11-28/` i raporty
  `E3-S1_2026-11-21.md`, `E3-S2_2026-11-21.md`. Zmian w programie, testach programu, instrukcjach, `modele_plytek`: 0.
- ASCII: 0 bajtow spoza ASCII w 12 plikach katalogu i w raporcie S2. Konce wierszy (`git ls-files --eol`): 3 pliki `.cmd`
  CRLF, pozostale 10 LF.
- Dane osobowe: brak nazwisk, adresow i nazw zlecen w plikach paczki; przyklady "TEST1", "TEST5", "Tester". Ryzyko
  przywiezienia danych pacjentow w paczce "Dnia skanera" - N6.
- Klucz ramki: narzedzie zapisuje go tylko w `narzedzia\klucz_ramki.txt` obok siebie (proba K9: plik powstaje dopiero po
  dobrym kluczu; po zlym i po pustym nic nie powstaje); plik jest w `narzedzia/.gitignore` (`git check-ignore`: trafiony);
  do `wyniki\` klucz nie trafia (w wynikach tylko `adres_ramki.txt` i pliki CSV); na ekranie pokazywane sa 4 pierwsze
  znaki. Lista "co przywiezc" obejmuje `C:\Sprzet_testy\wyniki`, nie `narzedzia` - klucz z narzedzia nie wraca. Wraca
  natomiast w `C:\Stanowisko\ustawienia.toml` (czesc 5 p. 4) - dokument mowi o tym wprost (w.472-473); po odbiorze plik
  trafia do `<PC-katalog>\sprzet_2026-11-28\program\` (poza repo). W moich probach klucz szedl tylko do
  `robocze\rec-s1\klucz_r2\` (opcja `--plik-klucza`); w kopii `rec-s1` pliku klucza nie ma.
- `wyniki/` przy uruchomieniu z kopii repo nie jest ignorowany - N12.
- `t13_higiena.py`: 0 naruszen (kryterium 5).
- Kopia `rec-s1` po probach: `git status --short` pusty, HEAD d8e7087; w katalogu paczki nie ma `klucz_ramki.txt` ani
  `wyniki\`. Kopia `integ`: `git status --short` pusty (tylko uruchamianie kodu).

## 5. Do decyzji wlasciciela

1. PILNE: pytania P1-P8 maja termin 25.11.2026, a dokument czeka na S2b. Propozycja: wyslac wlascicielowi sama sekcje 0
   juz teraz (z dopiskiem do P5 o zleceniach pacjentow - N6). Od P3 / P8 zalezy, czy ktos zdazy wgrac program ramki
   (12 krokow, kilka godzin) i odczytac klucz.
2. Skan z podlozem: czy przed wydaniem 0.3.3 zmienic program - minimum: przy `malo_stozkow` i danych wiekszych niz
   plytka komunikat "w skanie jest stolik / podstawka - ustaw linie ciecia powyzej stolika" w oknie "Dzien skanera"
   i w "Analiza skanu nie powiodla sie"; pelniej: rozpoznanie odporne na podloze (zmiana w pliku nietykalnym `plate.py` -
   wymaga zgody). Bez zmiany programu zostaje poprawka dokumentu i sciagi (N1).
3. Zlecenia pacjentow w programie skanera: czy wolno kopiowac caly folder zlecen (krok 2.6); jesli sa tam dane
   pacjentow - propozycja: tylko folder zlecen testowych (N6).
4. Krok 2.5a - co wynik znaczy dla reguly rozpoznania (propozycja do wpisania w dokument): (i) albo (ii) "kwadratowa"
   choc raz = skaner nie widzi ani dolkow, ani scianki - regule trzeba zmienic przed praca z plytkami okraglymi;
   tylko (iii) "kwadratowa" = scianki bocznej nie ma w skanie, numer z dolkow jest jedyna ochrona - zmiana zalecana
   (wariant C); wszedzie "okragla" = regula zostaje. Ile plytek skanowac (propozycja: 3 plytki, 9 skanow).
5. Dwie plytki o tym samym numerze w dniu testow (kwadratowa i okragla): zasada "rozne numery, poprzednia plytka zdjeta
   z ramki przed skanem nastepnej" (N2; decyzja 1 z recenzji PR #55).
6. Forma dokumentu: PDF / HTML do druku; czy 9,6 strony wystarcza, czy skracac dalej (N19).
7. Czy narzedzia dnia sprzetu wchodza do paczki 0.3.3, czy zostaja na pendrivie; kto kopiuje wyniki do
   `<PC-katalog>\sprzet_2026-11-28\` (z rundy 1, dalej otwarte).

## 6. Lista zadan dla S2b

Kolejnosc = waga. "[0.3.3]" = wymaga instalacji z nowej paczki; reszte mozna zrobic od razu na kodzie `integ`.

### P - przed przekazaniem dokumentu wlascicielowi

1. **N1 skan z podlozem.** `PIERWSZE_TESTY_NA_SPRZECIE.md` krok 2.3: w "Co zrobic" (w.193-194) zamienic "bez wygladzania
   i obcinania" na "bez wygladzania; nie obcinaj wierzchu plytki, a stolik i podstawke odetnij linia ciecia programu
   skanera (powyzej stolika, co najmniej 3 mm ponizej wierzchu plytki)"; w tabeli "Widzisz / Zrob" nowy wiersz dla
   "znaleziono 0" + stolik w podgladzie; w.207-208 - podloze jako pierwsza przyczyna; krok 2.4 "Gdy sie nie uda"
   (w.229-230): nazwac ustawienie jak w sciadze ("linia wysokosci ciecia" w oknie kamery, "cutting plane" po skanie).
   Zglosic koordynatorowi poprawke `Ramki/sciaga_skaner_DentalScan_2026-11-16.md` w.94 (poza zakresem paczki).
2. **N2 dwie plytki o tym samym numerze.** Kroki 2.7 p. 5 i 3.8 p. 5: rozne numery, zdjac poprzednia plytke z ramki,
   pytanie "Ponowny skan tej samej plytki?" -> "Nie, to nowy wsad"; arkusz 3.8: kratka. Na atrapie (kod O2 po poprawce B1):
   kwadrat nr 1 na ramce W + skan plytki okraglej nr 1 - opisac, co widac.
3. **N3 proba (c).** Krok 3.8 p. 6 (w.408-409) i "Udalo sie, gdy" (w.413-415): proba na plytce okraglej ramkowej przez
   "Zmien numer"; zdanie o ramce ciemnej po poprawce numeru zle odczytanego z dolkow. Wykonac 3 proby celowe na atrapie
   doslownie wg tekstu [0.3.3 albo `integ`].
4. **N4 ramka poranna.** Przejsc krok 3.8 z atrapa ramki P w trybie "Poranek" (plytka 4 kwadratowa i okragla ramkowa)
   i dopisac akapit "Ramka poranna"; nowy tekst komunikatu porannego z O2 do zalacznika C.
5. **N5 karton.** `narzedzia/pole_skanu.py` (galaz "plytka nierozpoznana", w.426-436): dane plaskie = "plaski arkusz /
   sam stolik", bez uwagi o podlozu; test z kartonem w polu 150 mm; krok 2.4 dokumentu - jedno zdanie.
6. **N6 dane pacjentow.** P5 (w.59-61): dopisac pytanie; kroki 2.1 (w.174-176) i 2.6 (w.269-273): osobny folder zlecen
   testowych, kopia calego folderu tylko bez danych pacjentow; czesc 5 (w.471-472) bez zmian.
7. **N7 powiazanie wynikow z prawda.** `narzedzia/pole_skanu.cmd` + `pole_skanu.py`: pytanie "Co lezy na stoliku?"
   zapisane w `.json` / `.txt`, test; arkusz tabele 2.5 i 2.5a: godzina wyniku, 2.5a 6 wierszy; krok 2.5a: liczba plytek,
   czas, "co wynik znaczy" (po decyzji 4).
8. **N8 pole skanera.** Krok 2.4 (w.211-231): proba z kartonem zawsze i jako pierwsza; wynik z plytki "przyblizony";
   czwarty wariant wiersza 2 ("wielkosci pola z tego skanu nie da sie podac") w dokumencie i w arkuszu 2.4;
   `pole_skanu.py`: przy `nie_kolowe` dopisac srednice okregu dopasowanego i liczbe kierunkow; test: kwadrat w polu
   kolowym 110 mm bez przesuniecia.
9. **[0.3.3] 13 + 4 miejsca `[DO POTWIERDZENIA NA 0.3.3]`** wg tabeli S2b w raporcie wykonawcy (w.72, 138, 149, 164, 174,
   262, 272, 290, 301, 380, 403, 412, 414 + zalaczniki A, C, D x 2); najpierw 3 sprawdzalne dzis (N14). Po kazdym
   potwierdzeniu zdjac znacznik. Tresc komunikatow brac z kodu wydania (zmiany po recenzji PR #55: B1, P1).
10. **[0.3.3] Powtorzyc** 51 testow narzedzi na kodzie wydania, 3 pliki `.cmd` przez `Polecenie.cmd` nowej instalacji
   z katalogu ze spacja (takze odpowiedz "abc" na pytanie o numer - U11), `ramka.cmd` na atrapie z kluczem: zly klucz ->
   dobry klucz -> pozycja 1 w jednym uruchomieniu menu.

### D - gdy tanie

11. N9 (warunek pytania o numer kwadratu), N15 (ten sam klucz
    na obu ramkach - P8), N16 ("drugi laptop"), N18 (3 miejsca jezyka), N21 (znaczniki w 2.2 i 2.6).
12. N10 (klucz z litera spoza ASCII), N11 (klucz dla adresu), N12 (`wyniki/` w `.gitignore`), N17 (test podloza przy
    plytce rozpoznanej), N20 (U16 - przesuniecie slowem; `narzedzia/dzien_skanera.cmd` usunac po potwierdzeniu skrotu).
13. N13 (`ZALACZNIKI.md`: krok `sprawdz_ramke.sh`, tabela B 10 nazw, zdanie o oknie).
14. N19: po odpowiedziach P1-P8 zastapic sekcje 0 ustaleniami i wykreslic kroki, ktore odpadly; PDF / HTML do druku
    (arkusz jako prawdziwe tabele); cel 9 stron.
15. Na prawdziwym ekranie (jesli bedzie): dwuklik, przeciaganie pliku na `pole_skanu.cmd`, menu `ramka.cmd` z klawiatury,
    "Zrzut ekranu" (z rundy 1, dalej otwarte).

### Do decyzji wlasciciela / koordynatora (nie dla wykonawcy S2b)

Sekcja 5, punkty 1-7.
