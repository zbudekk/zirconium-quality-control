# Raport recenzenta - PR #54 (E3-S1 / E3-S2), runda 3 (recenzja przyrostowa po etapach S2b-1 i S2b-2)

Data: 2026-11-21, 17:18-17:40. Zakres: `git -C <PC-katalog>\qc diff d8e7087 e3/sprzet -- Ramki/etap3/testy_sprzet_2026-11-28
Ramki/stanowisko/raporty/E3-S2_2026-11-21.md Ramki/sciaga_skaner_DentalScan_2026-11-16.md`, HEAD df141de (13 plikow,
+800 / -241). Kopia do prob: `<PC-katalog>\qc-wt\rec-s1` (detached df141de).

Metoda: (1) dokument, arkusz, pytania, zalaczniki i README przeczytane w calosci "oczami wlasciciela z wydrukiem";
(2) obejrzane strony do druku wykonawcy: PDF dokumentu (8 stron) i PDF arkusza (3 strony) z `robocze\s2\b2\druk\pdf\`;
(3) 57 testow narzedzi w kopii `rec-s1`, 7 wstrzykniec bledu w zmianach S2b-1 (kazde cofniete), 10 wlasnych prob
`pole_skanu` z kartonem nieidealnie plaskim; (4) 31 pozycji dokumentu i zalacznikow sprawdzonych w kodzie galezi `e3/o2`
(1f02673, po rundzie 3 paczki O2): `statusy.py`, `kontroler_api.py`, `indicate.py`, `dzien_skanera.py`,
`dzien_skanera_kroki.toml`, `ui/napisy*.py`, `samokontrola.py`; (5) `t13_higiena.py` z kopii `integ` na kopii `rec-s1`;
(6) raport wykonawcy (sekcje S2b-1, S2b-2) czytany po wlasnym przegladzie. Pelnego pytest nie uruchamialem; instalacji
z paczki nie powtarzalem (wyniki S2b-2 - "wg wykonawcy"). Liczby ponizej sa z moich prob, chyba ze napisano "wg wykonawcy".
Pliki robocze: `<PC-katalog>\koordynator\robocze\rec-s1\` (`*_r3*`).

## 0. Werdykt i liczby

WERDYKT: do scalenia po poprawkach - B 0, P 3, D 13 (uwagi P rundy 2: N1-N8 zamkniete 8 z 8; wszystkie P tej rundy sa nowe).

Wyjasnienie. Tresc po dwoch etapach jest dobra: 8 z 8 uwag P rundy 2 zamknietych, krok 3.8 zgodny z programem (wszystkie
tytuly komunikatow cytowane w dokumencie zgadzaja sie z `statusy.py` galezi `e3/o2` - 0 roznic w dokumencie, 3 roznice
w pelnych tekstach zalacznika C po rundzie 3 paczki O2), narzedzia: 57 passed, 7 z 7 wstrzykniec zlapanych. Paczka dalej
nie zmienia programu - scalenie stanu df141de niczego nie psuje. Trzy uwagi P da sie zamknac w S2b-3 bez nowych prob:
(R1) pytania P1-P9 wypadly z sekcji 0 dokumentu - sprzeczne z wymaganiem wlasciciela "zbierz na poczatku dokumentu";
(R2) wiersz awaryjny kroku 3.8 dla stanu "drugi laptop" / "zly klucz" podaje rade, ktora nie zadziala; (R3) strona do
druku ARKUSZA (poza repo) zlewa pola w akapity i ma wiersze tabel wysokosci jednej linii pisma - nie da sie jej wypelnic
dlugopisem; wydruk dokumentu glownego jest czytelny. Warunek jak w rundach 1 i 2: dokument NIE trafia do wlasciciela jako
"gotowy" przed zamknieciem P; strona pytan `PYTANIA_DO_WLASCICIELA.md` moze (i powinna) isc od razu - termin 25.11.2026.

## 1. Uwagi

### 1.0 Uwagi rundy 2 (P): stan

| Uwaga | Stan | Dowod |
|---|---|---|
| N1 skan z podlozem | zamknieta | przeglad tekstu: krok 2.3 "Co zrobic" w.161-165 (linia ciecia POWYZEJ stolika i co najmniej 3 mm PONIZEJ wierzchu; "stolik i podstawke odetnij"), wiersz tabeli w.173-175 ("znaleziono 0" -> podglad skanu -> SKAN Z PODLOZEM), akapit w.179-187 (nazwane "najwieksze ryzyko dnia"; jak rozpoznac: podglad + `pole_skanu.cmd` "UWAGA: ... PODLOZE"; jak obejsc; DWA skany A / B tej samej plytki), pole 90 mm jako druga przyczyna w.189-190, znacznik w.191-192; krok 2.7 w.291-293 "N = 0: najpierw ... skan z podlozem"; arkusz w.56-60 (stolik w podgladzie, czy linie da sie ustawic, skany A / B). Sciaga skanera w.94 i w.98: to samo brzmienie co dokument (powyzej stolika, co najmniej 3 mm ponizej wierzchu); `git diff --numstat`: 2 / 2 wiersze - zmieniono tylko te dwa. Narzedzie nazywa podloze: testy `test_u5...`, `test_n5_plytka_ze_stolikiem...`, `test_n17...` (wstrzykniecie W2: 2 failed). Zgodnosc z nowym tekstem bledu analizy O2 r3 ("... albo w skanie jest stolik (podloze) wokol plytki; ... i ustaw ciecie skanu powyzej stolika"): dokument niczego sprzecznego nie mowi, ale cytuje jeszcze stary tekst - pozycje 5 i 6 listy S2b-3 (D2). Drobne: D9 (sciaga w.167) |
| N2 dwie plytki o tym samym numerze | zamknieta | krok 3.8: dwie zasady w.393-394 (decyzja (a) koordynatora), punkt 8 w.419-423 (pytanie "Ponowny skan tej samej plytki?", panel "Dwa skany z numerem plytki N - ramka czeka na odpowiedz", "Tak, to ponowny skan"), wiersz awaryjny w.437-439 ("Pod plytka swieci wynik INNEJ plytki o tym samym numerze (program nie zawsze pyta ...)"), krok 2.7 p. 5 w.278-279, arkusz w.158-159. Napisy: `statusy.py` (e3/o2) w.473, w.532, w.226-227 - zgodne. Przejscie w oknie: 9 z 9 punktow wg wykonawcy (niepowtarzane). Drobne: D3 (punkt 5 konczy sie plytka lezaca na ramce) |
| N3 proba (c) | zamknieta | w.414-418: tylko plytka OKRAGLA z numerem odczytanym z dolkow, "Zmien numer", panel "Plytka 3: Numer plytki nie zgadza sie ze skanem" ("Podany numer plytki to 3, a program odczytal ze skanu numer 2" = `statusy.py` w.480-481), "Na plytce kwadratowej tej proby nie rob"; decyzja (b): w.435-436 ("to wynik pomiaru ..., nie awaria. Zapisz numer wybity i odczytany, zeskanuj plytke ponownie"); kolejnosc (c) przed ponownym skanem uzasadniona (w.422-423, "Nie mozna tego zrobic" = `statusy.py` w.380); arkusz w.156-157 |
| N4 ramka poranna | zamknieta | akapit w.443-448: "-> Poranek" (`ui/napisy_rano.py` w.12), ciemno bez skanu, swieci bez projektow i pliku zlecen, wynik WRACA, "Plytka na ramce czeka na numer skanu" (`statusy.py` w.466), "Na ramce lezy plytka, ktorej nie ma w planie pieca" (w.460), ponowny skan po przelaczeniu; arkusz w.162-163; 6 z 6 zdan w oknie wg wykonawcy. Drobne: D4 (stare pytanie ze sprzecznym zdaniem) |
| N5 karton w duzym polu | zamknieta dla kartonu plaskiego; reszta = D1 | wlasne proby K1-K3, K6, K7 (karton plaski, ugiety o 1 i 2 mm, szum 0,3 mm, fala 0,5 mm; pole kolowe 150 mm): 5 z 5 "Dane sa PLASKIE ...", bez slowa "PODLOZE", `podloze w skanie: nie dotyczy (plaski arkusz ...)`; wstrzykniecia W1 i W2 zlapane. Karton ugiety o 3 i 5 mm albo fala 1,2 mm (K4, K5, K8): 3 z 3 znowu "UWAGA: ... PODLOZE" - D1 |
| N6 dane pacjentow | zamknieta | zasada 2 w.19-20; krok 2.1 w.139-142 ("folder ... skany TESTOWE", "nigdy caly folder zlecen"); krok 2.6 w.257-263 (ostrzezenie na poczatku, kopia calego folderu TYLKO przy samych zleceniach testowych, inaczej "pomijam: dane pacjentow"); czesc 5 w.499-501; pytanie P9: `PYTANIA_DO_WLASCICIELA.md` w.47-51, arkusz w.28-29 i w.108. Pytanie P9 NIE jest w dokumencie glownym - R1 |
| N7 powiazanie wyniku z prawda | zamknieta | `pole_skanu.cmd` w.25-30: pytanie "Co lezy na stoliku? ..." -> `--opis`; `pole_skanu.py`: pole `opis_czlowieka` w `.json` i drugi wiersz `.txt`; wstrzykniecia W3 i W4 zlapane; dokument w.224-226 i w.240-246 (7 minut na skan, minimum 7 skanow = ok. 50 minut, pelna wersja 24 skany), "co wynik znaczy" w.247-250; arkusz: kolumna "godz. wyniku" w.74-76, tabela 2.5a 6 wierszy w.96-104. Drobne: D5 (jak odczytac godzine z wiersza "Zapisano:"), R3 (wiersze tabel na wydruku) |
| N8 pole z plytki | zamknieta | krok 2.4: karton NAJPIERW i jako glowny pomiar w.198-203, plytka "pomocniczy, przyblizony" w.204-208, 4 warianty wiersza 2 w dokumencie i arkuszu (w.64-68); narzedzie: "Konce danych pasuja do okregu o srednicy ok. ... mm w N z M kierunkow" i "Wymiar pola liczony z plytki jest PRZYBLIZONY ..."; wstrzykniecia W5 i W6 zlapane. Uwaga: test `test_n8...` wymusza galaz "nie kolowe" przez `monkeypatch` progu - samo bledne "POLE NIE JEST KOLEM" przy polu 110 mm zostalo, ale ma teraz obok srednice okregu i dopisek "przyblizony" (zgodnie z propozycja rundy 2) |

Uwagi D rundy 2 (N9-N21): zrobione wg wykonawcy 11 z 13, sprawdzone przegladem 8 (N9 w.282-283, N10 test + W7, N11 w.335,
N12 `.gitignore`, N13 zalaczniki w.21-22, w.33-37, N15 pytania w.42, N16 w.398 i w.433-434 - patrz R2, N18 0 trafien
"sztuczn" poza wstepem, N21 znaczniki w.157 i w.267); odlozone: N20, czesc N19 (D12).

### 1.1 Uwagi tej rundy

| Nr | Waga | Plik:linia | Scenariusz | Propozycja |
|---|---|---|---|---|
| R1 | P | `PIERWSZE_TESTY_NA_SPRZECIE.md` w.26-31 | Pytania do wlasciciela. Sekcja 0 ma dzis 4 wiersze: odsyla do `PYTANIA_DO_WLASCICIELA.md` i wymienia 5 pytan jednym slowem ("P1 (ktora ramka), P6 (siec) ..."); tresci pytan P2, P4, P5, P7 nie ma w dokumencie wcale (P2 i P4 nie maja nawet odsylacza). Wymaganie wlasciciela: "[cytat usuniety]". Wlasciciel z wydrukiem dokumentu (bez strony pytan) nie wie, o co jest pytany; odsylacze "(P5, P9)", "(P6)", "(P8)", "(P3)" w krokach 2.1, 2.6, 3.2, 3.3 prowadza do tresci, ktorej w dokumencie nie ma. | Tabela 9 wierszy w sekcji 0 - gotowy tekst w sekcji 6 (pozycja 1). Plik `PYTANIA_DO_WLASCICIELA.md` zostaje jako wersja szersza do wyslania od razu. Koszt: ok. +180 slow (0,4 strony). |
| R2 | P | `PIERWSZE_TESTY_NA_SPRZECIE.md` w.433-434 | Pasek programu pokazuje "W: drugi laptop" (wlasciciel uruchomil program "Stanowisko" w ciagu pol minuty po pozycji 4 / 5 `ramka.cmd` albo przy otwartym `ramka.cmd`). Dokument: "zamknij `ramka.cmd` i poczekaj pol minuty". Z przegladu kodu `indicate.py` (e3/o2) w.1006-1010 i w.1176-1180 oraz testu programu `test_indicate.py::test_p2_inny_laptop_bez_automatycznego_przejecia_ramki_do_wznow`: po odmowie `inny_laptop` program NIE ponawia planu sam - czeka na klikniecie "Przejmij ramke W" (`ui/napisy_rano.py` w.149; `statusy.py` w.497: "... albo kliknij 'Przejmij ramke'"). Czekanie niczego nie zmieni: ramka zostaje ciemna do klikniecia albo ponownego uruchomienia programu. To samo dla "zly klucz" (w.496: po poprawce ustawien "kliknij 'Przejmij ramke'"; ustawienia program czyta przy starcie) - dokument mowi tylko "sprawdz adres i klucz w ustawieniach". Dowod: przeglad kodu + ten test programu uruchomiony w kopii `rec-s1` (proba 16: 2 passed - po 4 s ciszy pierwszego komputera drugi dalej ma `blad == "inny_laptop"`, plan idzie dopiero po `wznow()`); w oknie programu nie probowalem. W glownej sciezce stan jest malo prawdopodobny (punkt 1 kroku kaze poczekac pol minuty) - to poprawka wiersza awaryjnego. | Gotowy tekst w sekcji 6 (pozycja 2): zamknij program -> popraw ustawienia -> uruchom ponownie; "drugi laptop": zamknij `ramka.cmd`, poczekaj pol minuty, kliknij w pasku "Przejmij ramke W". |
| R3 | P | strona do druku arkusza: `robocze\s2\b2\druk\pdf\druk_ARKUSZ_OBSERWACJI.pdf`, skrypt `robocze\s2\b2\druk.py` (poza repo); zrodlo `ARKUSZ_OBSERWACJI.md` bez zarzutu | Wlasciciel dostaje wydruk arkusza i wypelnia go dlugopisem. W PDF wykonawcy: (a) wiersze kontynuacji punktow sa zlane w jeden akapit - np. punkt 2.3 (8 pol z 8 wierszy zrodla) to 5 wierszy ciaglego tekstu, punkt 3.8 (14 wierszy zrodla, 12 kratek) to blok 9 wierszy bez podzialu; skany (A) i (B) stoja w jednym zdaniu; (b) tabele 2.5, 2.5a i 3.5 sa blokiem pisma stalej szerokosci z wierszami wysokosci jednej linii (ok. 4 mm) i kolumnami po 7-9 znakow ("dolki z 4", "brzeg z 72") - nie da sie w nich pisac recznie, a to glowne tabele dnia (kazdy skan = 1 wiersz, 7 pol); (c) linie "Uwagi" maja 1/3 szerokosci strony. Arkusz w tej postaci nie spelnia "arkusz obserwacji do wypelniania". PDF dokumentu glownego (8 stron) jest czytelny - drobiazgi w D10. | W `druk.py` dla ukladu "arkusz": zachowac podzial na wiersze zrodla (kazdy wiersz kontynuacji jako osobna linia), tabele jako prawdziwe tabele z wierszem co najmniej 8 mm (albo `<pre>` z interlinia 2,2 i pismem 10 pt, orientacja pozioma dla tabeli 2.5), linie uwag na cala szerokosc; obejrzec PDF po zmianie. Dopuszczalne 4-5 stron. |
| D1 | D | `PIERWSZE_TESTY_NA_SPRZECIE.md` w.198-203, w.211-212; `narzedzia/pole_skanu.py` w.49-50 (`PLASKIE_PAS_MM = 1.0`) | Karton nieidealnie plaski w duzym polu. Wlasne proby (pole kolowe 150 mm): ugiecie 3 mm i 5 mm, fala 1,2 mm (K4, K5, K8) - 3 z 3 "Dane sa wieksze niz jakakolwiek plytka ... UWAGA: w skanie jest prawdopodobnie PODLOZE", `podloze w skanie: PRAWDOPODOBNIE TAK`, zdania "Dane sa PLASKIE" nie ma; karton 150 x 150 mm na stoliku w polu 200 mm (K10) - to samo (tu slusznie); pole 120 mm z kartonem ugietym (K9) - ani "PLASKIE", ani "PODLOZE". Wymiary pola dobre w 10 z 10 prob (149,9 x 151,2; 120,0; 200,0 mm). Dokument obiecuje przy kartonie zdanie "Dane sa PLASKIE", a wiersz "Gdy sie nie uda" zna uwage o podlozu tylko "przy skanie PLYTKI". | Jedno zdanie w kroku 2.4 (pozycja 4 listy). Narzedzia nie trzeba zmieniac (arkusz w.63 ma kratke "Dane sa PLASKIE"). |
| D2 | D | `ZALACZNIKI.md` w.63-81; `PIERWSZE_TESTY_NA_SPRZECIE.md` w.13-14, w.180-181, w.291-293, w.299, w.421 | Teksty po rundzie 3 paczki O2 (1f02673) - 3 roznice, wszystkie w zalaczniku C (wypisane doslownie w sekcji 2a); zmienily sie TRZY teksty, nie dwa: takze `plytka_czeka_na_numer` (zalacznik w.72-76, bez znacznika). Tytuly paneli sie nie zmienily, wiec dokument glowny jest zgodny; krok 2.3 w.180-181 "komunikaty mowia o polu skanera i brudnych stozkach" po 0.3.3 jest prawda juz tylko dla okna "Dzien skanera" (program "Stanowisko" przy 0 z 3 sam wymienia stolik). | Pozycje 5 i 6 listy S2b-3. |
| D3 | D | `PIERWSZE_TESTY_NA_SPRZECIE.md` w.409-412 | Punkt 5 kroku 3.8 konczy sie na "Poloz jeszcze raz: ... zostaje ciemno" - plytka nr 1 lezy na ramce, a punkt 6 zaczyna sie od "Zeskanuj plytke okragla ... (np. 2)". Kto idzie po numerach, zlamie pierwsza zasade kroku (w.393) tekstem samego kroku: po skanie plytki 2 pojawi sie komunikat (b) "Na ramce lezy inna plytka niz zeskanowana" bez proby celowej. | Na koncu punktu 5 dopisac "Zdejmij ja." |
| D4 | D | `PIERWSZE_TESTY_NA_SPRZECIE.md` w.294-295, w.447-448 | "Plytka nie z tego trybu": po "-> Poranek" stare pytanie zostaje i ma zdanie sprzeczne "To plytka poranna, a program pracuje w trybie 'Poranek'. Skan jest zablokowany ..." (POTRZEBUJE 1 wykonawcy; `statusy.py` w.534-536, pole trybu z trybu biezacego). Dokument mowi tylko "(stare pytanie zostaje)" - wlasciciel przeczyta zdanie bez sensu i uzna przelaczenie za nieudane. | Pozycja 7 listy. |
| D5 | D | `PIERWSZE_TESTY_NA_SPRZECIE.md` w.225-226; `ARKUSZ_OBSERWACJI.md` w.71 | "godzine z wiersza 'Zapisano:'" - wiersz narzedzia to `Zapisano: C:\Sprzet_testy\wyniki\pole_skanu\<skan>_<data>_<godzina>_pole.txt (+ .json, .png)` (`pole_skanu.py` w.600); godzina jest 6 cyframi w nazwie pliku, osobno jej nie ma. | Pozycja 9 listy (przyklad). |
| D6 | D | `ARKUSZ_OBSERWACJI.md` w.87 | "Wiersz `podloze w skanie:` inny niz 'nie'" - narzedzie pisze tylko "nie widac", "nie dotyczy (plaski arkusz ...)" albo "PRAWDOPODOBNIE TAK (...)" (`pole_skanu.py` w.394-395, w.415); samego "nie" nie ma, a dwa z trzech napisow zaczynaja sie od "nie". | "Wiersz `podloze w skanie: PRAWDOPODOBNIE TAK` - w ktorych skanach: ..." |
| D7 | D | `PIERWSZE_TESTY_NA_SPRZECIE.md` w.262-263, w.267 | Pytanie okna przy pakowaniu: napisy przyciskow "Yes" / "Tak" nie byly widziane na ekranie (POTRZEBUJE 3 wykonawcy; kod: `QMessageBox.Yes / No`, domyslnie No - `dzien_skanera.py` w.107-109, w.763-766 - zgodne z tekstem "sam Enter znaczy NIE"). Znacznik kroku 2.6 tego nie obejmuje. | Do znacznika w.267 dopisac "; napisy przyciskow w pytaniu przy pakowaniu". |
| D8 | D | `PIERWSZE_TESTY_NA_SPRZECIE.md` w.339-343 | Menu `ramka.cmd` z klawiatury w jednym uruchomieniu nie bylo sprawdzone (POTRZEBUJE 4 wykonawcy: wymaga prawdziwej konsoli); sprawdzone sa pozycje uruchamiane osobno (`ramka.cmd ADRES WYBOR`, `ramka.cmd` w.5). Dokument ma znacznik ("menu z klawiatury"), ale nie ma wyjscia. | Pozycja 8 listy: jedno zdanie w "Gdy sie nie uda" kroku 3.3. |
| D9 | D | `Ramki/sciaga_skaner_DentalScan_2026-11-16.md` w.167 (poza 2 dozwolonymi wierszami - dla koordynatora) | Lista pytan sciagi: "Czy plaszczyzne ciecia po skanie mozna pominac albo ustawic ponizej plytki?" - po poprawce w.94 i w.98 to pytanie ciagnie w zla strone (ciecie ponizej plytki = stolik w skanie). | "... Czy da sie ja ustawic miedzy stolikiem a wierzchem plytki i zapamietac w zleceniu?" |
| D10 | D | PDF dokumentu, strony 5-6; `PIERWSZE_TESTY_NA_SPRZECIE.md` w.3, w.29, w.293, w.332-333 | Wydruk dokumentu: (a) tabela "Gdy sie nie uda" kroku 2.7: wiersz zrodla w.293 ma 104 znaki i lamie sie - "2.4" laduje samotnie w lewej kolumnie; (b) `ramka-p.local` zlamane po lacznku na koncu wiersza ("ramka-" / "p.local") - wlasciciel moze wpisac bez kreski; (c) dokument kaze drukowac i otwierac pliki `.md` ("Wydrukuj go razem z `ARKUSZ_OBSERWACJI.md`", "na osobnej stronie: `PYTANIA_DO_WLASCICIELA.md`") - wlasciciel dostanie PDF / kartki. | Pozycja 12 listy. |
| D11 | D | `PIERWSZE_TESTY_NA_SPRZECIE.md` w.4, w.29-30, w.292, w.497 | Jezyk - nowe miejsca: "(kod paczki 0.3.3)" w.4; "N = 0:" w tabeli w.292 (po "w skanie widac N z 3"); "sesji prowadzacej projekt" w.29-30 i w.497 (bylo juz w rundzie 2 - zostaje, jesli wlasciciel tak nazywa rozmowe z koordynatorem). Poza tym nowych slow technicznych nie znalazlem; "kafelek" (w.281, w.413) i "niebieski panel" (w.415) sa opisem ekranu. | w.4: "na probnej instalacji wersji 0.3.3 programu"; w.292: "Gdy w nawiasie jest '0 z 3': ...". |
| D12 | D | calosc | Dlugosc: dokument 511 wierszy, 4754 slowa = 10,6 strony wg miary 450 slow (cel zlecenia S2b-2 "ok. 10 albo mniej" niespelniony ta miara), ale wydruk ma 8 stron A4 pismem 10,5 pt (PDF policzony przeze mnie: 8); arkusz 196 wierszy, 1800 slow = 4,0 strony (PDF 3 strony - patrz R3). Z tabela pytan (R1) dokument urosnie do ok. 4930 slow = 8-9 stron wydruku. Dalszy skrot dopiero po odpowiedziach P1-P9. | Bez zmian teraz; po odpowiedziach wykreslic kroki, ktore odpadly. |
| D13 | D | `ZALACZNIKI.md` w.117; `narzedzia/dzien_skanera.cmd`; `narzedzia/ramka_proba.py` | Drobne zastane: zalacznik E "narzedzia ... - 51 testow" (dzis 57); N20 (skrot awaryjny `narzedzia/dzien_skanera.cmd`, przesuniecie wpisane slowem) i N11 w narzedziu dalej odlozone; POTRZEBUJE 5 wykonawcy (sam Enter na "Wpisz uwage" = obserwacja pusta) obejscie tekstem jest (w.379 "wpisz `ok`"). | "51 testow (stan z 21.11 rano; dzis 57)". Reszta po dniu sprzetu. |

### 1a. Wydruk (strony do druku wykonawcy, `robocze\s2\b2\druk\`)

Dokument glowny, PDF 8 stron: naglowki krokow niebieskie, etykiety "Co zrobic / Udalo sie, gdy / Zanotuj / Gdy sie nie
uda" pogrubione i kazda od nowego wiersza, cytaty z ekranu pogrubione, polecenia i nazwy plikow pismem stalej szerokosci,
tabele "Widzisz / Zrob" jako bloki stalej szerokosci - czytelne (1 zlamany wiersz, D10a). Kratki listy "co zabrac" sa.
Krok 3.8 miesci sie na przelomie stron 6-7 (punkty 1-3 na stronie 6, 4-9 na stronie 7) - do przyjecia.
Arkusz, PDF 3 strony: nie nadaje sie do wypelniania (R3). Strony pytan i zalacznikow nie ogladalem w PDF (pliki sa).

### 1b. Znaczniki

`[DO POTWIERDZENIA NA 0.3.3]`: dokument 3 miejsca (w.39 nazwa paczki, w.299 tekst w nawiasie bledu analizy, w.421 tekst
panelu "Dwa skany ...") + legenda w.13; zalaczniki 2 (w.63, w.77) + zdanie wstepu w.50 - zgodne z raportem wykonawcy
i README. Brakuje znacznika przy trzecim tekscie zmienionym w rundzie 3 O2 (zalacznik w.72-76, D2). Tytul panelu z w.421
w rundzie 3 O2 sie NIE zmienil - znacznik w.421 mozna zdjac po samym potwierdzeniu na 0.3.3.

`[NIE SPRAWDZONE BEZ SPRZETU]`: 22 znaczniki = kazdy z 21 krokow (1.1-1.4, 2.1-2.7 z 2.5a, 3.1-3.9) + czesc 4; lista
zbiorcza w.505-511 mowi to wprost i wymienia 11 najwazniejszych pozycji - wszystkie zgodne z trescia krokow (sprawdzone
11 z 11). Braki: D7 (przyciski pytania przy pakowaniu) i - po poprawce R2 - przycisk "Przejmij ramke" (nie byl klikany
w zadnej probie paczki; dopisac do znacznika kroku 3.8).

### 1c. Rozbieznosci wykonawcy z instalacji (R1-R9 raportu S2b-2) i POTRZEBUJE

Poprawki dokumentu sprawdzone z kodem `e3/o2`: R1 "Nowy wynik czeka: Plytka N" (`ui/napisy.py` w.43, w.48) - zgodne,
dokument w.283-285 i w.412-413; R2 tytul z numerem podanym - zgodne z opisem ekranu wykonawcy (kod: `statusy.py` w.480);
R3 pytanie przy pakowaniu - zgodne (`dzien_skanera.py` w.762-766, domyslnie NIE); R4 lista ostrzezen samokontroli - wg
wykonawcy, niesprawdzone; R5 "Wpisz uwage ..." - zgodne z `ramka.cmd` / narzedziem (runda 2); R6 "Ten sam projekt w dwoch
gniazdach" (`statusy.py` w.396) - zgodne; R7 pytanie zostaje po "-> Poranek" - zgodne co do faktu, brak slowa o tresci
(D4); R8 zdanie o sciadze - zgodne ze sciaga po poprawce; R9 drugi wariant "czeka na numer" (`statusy.py` w.516) - zgodne,
ale tekst zmieniony w rundzie 3 O2 (D2). Razem: 8 z 9 sprawdzonych, 0 poprawek sprzecznych z programem.

POTRZEBUJE (5 pozycji S2b-2) - co dokument powinien obejsc tekstem: nr 1 (zdanie sprzeczne) - TAK, D4; nr 2 (blad
analizy bez slowa o stoliku) - zalatwione w programie (O2 runda 3, `znaczniki_0`), dokument do uaktualnienia (D2);
nr 3 (przyciski "Yes" / "Tak") - tekst jest, dopisac znacznik (D7); nr 4 (`ramka.cmd` z klawiatury) - TAK, D8;
nr 5 (sam Enter na "Wpisz uwage") - tekst jest (w.379).

## 2. Wlasne proby

| nr | polecenie / proba | wynik |
|---|---|---|
| 1 | `py.cmd -m pytest ..\etap3\testy_sprzet_2026-11-28\narzedzia -q -p no:cacheprovider` (kopia `rec-s1`, df141de) | 57 passed, 0 failed, 144,6 s, kod 0 (`p01_testy_narzedzi_r3.log`) |
| 2 | `proby_karton_r3.py`: `pole_skanu.zmierz` + `raport`, karton w polu kolowym 150 mm: plaski (K1), ugiety o 1 / 2 mm (K2, K3), szum 0,3 mm (K6), fala 0,5 mm (K7) | 5 z 5: "Dane sa PLASKIE", brak "PODLOZE", `podloze w skanie: nie dotyczy (plaski arkusz albo sam stolik - wymiary to pole skanera)`; wymiary 149,9 x 151,2 mm, kolo 151,3 mm |
| 3 | to samo: ugiecie 3 mm (K4), 5 mm (K5), fala 1,2 mm (K8) | 3 z 3: brak "PLASKIE", jest "UWAGA: ... PODLOZE", `podloze w skanie: PRAWDOPODOBNIE TAK (dane wieksze niz plytka)`; wymiary dobre (149,9 x 151,2) - D1 |
| 4 | karton ugiety o 3 mm w polu 120 mm (K9); karton 150 x 150 mm na stoliku 3 mm nizej, pole 200 mm (K10) | K9: ani "PLASKIE", ani "PODLOZE", 120,0 x 120,0; K10: "PODLOZE" (slusznie - stolik jest w skanie), 200,0 x 200,0 |
| 5 | wstrzykniecie W1 (N5): dane nigdy nie sa plaskie | 1 failed (`test_n5_karton_w_duzym_polu...`), 4 passed - zlapane |
| 6 | W2 (N5 / N1): kazde dane nierozpoznane sa "plaskie" (stolik z plytka bez uwagi o podlozu) | 2 failed (`test_u5_podloze_w_skanie_jest_nazwane`, `test_n5_plytka_ze_stolikiem...`) - zlapane |
| 7 | W3 (N7): opis czlowieka nie trafia do wyniku | 1 failed (`test_n7_opis_czlowieka...`) - zlapane |
| 8 | W4 (N7): opis bez zamiany na ASCII i bez limitu 120 znakow | 1 failed - zlapane |
| 9 | W5 (N8): bez zdania o okregu dopasowanym | 1 failed (`test_n8_kwadrat_w_polu_kolowym_110...`) - zlapane |
| 10 | W6 (N8): zdanie "PRZYBLIZONY" takze przy calej plytce w skanie | 1 failed - zlapane |
| 11 | W7 (N10): klucz z litera spoza ASCII bez kontroli | 1 failed (`test_n10_klucz_z_litera_spoza_ascii...`) - zlapane |
| 12 | po wstrzyknieciach: `git -C rec-s1 status --short` | pusty (7 z 7 cofnietych; `p06_mutacje_r3.log`) |
| 13 | `py.cmd <integ>\Ramki\etap3\odbior_koncowy\narzedzia\t13_higiena.py --repo <PC-katalog>\qc-wt\rec-s1 --do HEAD --json ...` | kod 0; "NARUSZENIA (grupa E3 i sciezki poza listami): 0"; "WYNIK T13: ZAL z odstepstwem O11"; 0 wierszy o plikach paczki |
| 14 | `git ls-files --eol`, bajty spoza ASCII, `git diff --numstat` (16 plikow zakresu) | 3 pliki `.cmd` CRLF, 13 LF; 0 bajtow spoza ASCII w 16 z 16; sciaga 2 / 2 wiersze |
| 15 | pomiar dlugosci (metoda rund 1 i 2) | dokument 511 wierszy, 4754 slowa = 10,6 strony; arkusz 196 / 1800 = 4,0; pytania 51 / 465 = 1,0; zalaczniki 129 / 1545 = 3,4; PDF: dokument 8 stron, arkusz 3 strony |

| 16 | `py.cmd -m pytest testy\test_indicate.py -q -p no:cacheprovider -k "p2_inny_laptop or drugi_laptop"` (kopia `rec-s1`; test programu, dowod do R2) | 2 passed, 33 deselected, 4,4 s, kod 0 (`p09_indicate_r3.log`) |

Proby niewazne: brak. Serie krotsze niz 3 min (bez `ciezki.ps1`); 1 proces python naraz. Po probach nie zostal zaden
moj proces python.

### 2a. Zgodnosc z kodem `e3/o2` (1f02673) - 31 pozycji; roznice doslownie

Komunikaty ramki cytowane w kroku 3.8 dokumentu (wszystkie): "Plytka lezy na zlej ramce" (`statusy.py` w.453),
"Na ramce lezy inna plytka niz zeskanowana" (w.456), "Plytka 3: Numer plytki nie zgadza sie ze skanem" (w.480 + numer
plytki z ekranu), "Podany numer plytki to 3, a program odczytal ze skanu numer 2" (w.481), "Ponowny skan tej samej
plytki?" (w.532), "Tak, to ponowny skan" (w.226), "Dwa skany z numerem plytki N - ramka czeka na odpowiedz" (w.473),
"Nie mozna tego zrobic" (w.380), "Plytka na ramce czeka na numer skanu" (w.466), "Na ramce lezy plytka, ktorej nie ma
w planie pieca" (w.460), "Plytka nie z tego trybu" (w.534), napisy paska "gotowa", "brak polaczenia", "zly klucz",
"drugi laptop" (`ui/napisy_rano.py` w.143), "Test LED" (w.147), "-> Poranek" (w.12), "Zmien numer" (`ui/napisy.py`
w.94): 18 z 18 napisow zgodnych co do slowa (bez znakow diakrytycznych), 0 roznic w dokumencie glownym.

Pozostale pozycje: "Analiza skanu nie powiodla sie" + "w skanie widac N z 3 znacznikow plytki - ..." (w.334-335, w.574,
w.577) - zgodne; "Ten sam projekt w dwoch gniazdach" (w.396); "Nowy wynik czeka: Plytka N" (`ui/napisy.py` w.43);
"PRZOD PLYTKI" (w.85); okno "Dzien skanera": "Nie wiem, gdzie skaner zapisuje - szukaj", "Zrzut ekranu (za 3 s)",
"Obserwuje:", "Brakuje wymaganych krokow ... Spakowac teraz?", "Sesja spakowana: ... plikow" (`dzien_skanera.py` w.142,
w.226, w.372, w.762-764, w.789) i numery krokow okna 5, 6, 7, 9, 12, 14 (`dzien_skanera_kroki.toml`) - zgodne;
"w ciagu godziny" = `ponowny_skan_okno_min = 60` (`ustawienia.przyklad.toml` w.108); `OK ramka_wieczorna: ramka wieczorna
odpowiada` (`samokontrola.py` w.1097); przycisk "Przejmij ramke W" (`ui/napisy_rano.py` w.149 - w dokumencie go BRAK, R2).
Razem 31 pozycji (18 napisow kroku 3.8 + 13 innych): 30 z 30 cytowanych istnieje w kodzie co do slowa, 1 brakuje
w dokumencie (R2).

Roznice (tylko `ZALACZNIKI.md`, czesc C - pelne teksty):

1. Panel "Dwa skany z numerem plytki N ..." (zalacznik w.66-69).
   W dokumencie: "... dopoki nie odpowiesz na pytanie o ponowny skan. Jesli to ta sama plytka zeskanowana drugi raz -
   kliknij "Tak, to ponowny skan", ramka zaswieci. Jesli to dwie rozne plytki - najpierw zdejmij z ramki te, ktora lezy,
   potem kliknij "Nie, to nowy wsad"; wynik ostatniego skanu pokaze wtedy ekran."
   W programie: "... dopoki nie odpowiesz na pytanie o ponowny skan. Te same prace zeskanowane drugi raz - kliknij "Tak,
   to ponowny skan", ramka zaswieci. Nowe prace na tej samej plytce - kliknij "Nie, to nowy wsad", ramka zaswieci. Na
   ramce lezy inna plytka niz ta z ostatniego skanu - najpierw zdejmij z ramki te, ktora lezy, potem kliknij "Nie, to nowy
   wsad"; wynik ostatniego skanu pokaze wtedy ekran."
2. Panel "Plytka na ramce czeka na numer skanu" (zalacznik w.72-76; BEZ znacznika).
   W dokumencie: "... - ramka nie swieci. W tym piecu jest skan bez numeru plytki: jesli to skan tej plytki, wybierz numer
   4 w pytaniu "Podaj numer plytki" - ramka zaswieci sama."
   W programie: "... - ramka nie swieci. W tym piecu jest skan bez numeru plytki: jesli to skan tej plytki, wybierz numer
   4 w pytaniu "Podaj numer plytki" - ramka zaswieci sama. Jesli tej plytki jeszcze nie skanowano - zeskanuj ja."
   (drugi wariant srodka: "sa skany bez numeru plytki: jesli jeden z nich to skan tej plytki").
3. Blad analizy przy 0 z 3 znacznikow (zalacznik w.77-81; dokument w.291-293 cytuje tylko poczatek - zgodny).
   W dokumencie: jeden tekst dla kazdego N: "w skanie widac 1 z 3 znacznikow plytki - plytka nie miesci sie w polu
   skanera albo lezy poza srodkiem; ustaw plytke na srodku i sprawdz, czy pole skanowania obejmuje cala plytke".
   W programie: dla N = 1, 2 jak wyzej; dla N = 0 osobny tekst: "w skanie widac 0 z 3 znacznikow plytki - plytka nie
   miesci sie w polu skanera albo lezy poza srodkiem, albo w skanie jest stolik (podloze) wokol plytki; ustaw plytke na
   srodku, sprawdz, czy pole skanowania obejmuje cala plytke, i ustaw ciecie skanu powyzej stolika".

## 3. Kryteria zlecen `s2b1.md` i `s2b2.md`

| Zlecenie | Kryterium | Stan |
|---|---|---|
| S2b-1 (1) | testy narzedzi 0 failed, nowe padaja bez poprawek | potwierdzone wlasna proba: 57 passed; 7 wstrzykniec w zmianach N5, N7, N8, N10 - 7 zlapanych |
| S2b-1 (2) | N1-N8 zamkniete z dowodem | potwierdzone: 8 z 8 (tabela 1.0), 5 przegladem tekstu z numerami wierszy, 3 takze wlasna proba (N5, N7, N8) |
| S2b-1 (3) | krok 3.8 na atrapach wg tekstu | wg wykonawcy 7 z 9 (atrapy) i 9 z 9 (okno, instalacja) - niepowtarzane; potwierdzone przegladem: 18 z 18 napisow kroku w kodzie `e3/o2` |
| S2b-1 (4), S2b-2 (4) | dlugosc | czesciowo: 10,6 strony miara 450 slow (cel ok. 10), wydruk 8 stron; arkusz 4,0 (limit 4) - D12 |
| S2b-2 (1) | testy narzedzi 0 failed | potwierdzone wlasna proba (57 passed) |
| S2b-2 (2) | 14 miejsc `[DO POTWIERDZENIA NA 0.3.3]` | potwierdzone przegladem: w plikach zostaja 3 + 2 (sekcja 1b); 13 potwierdzen na instalacji - wg wykonawcy |
| S2b-2 (3) | krok 3.8 w oknie na instalacji | wg wykonawcy 9 z 9 + 6 z 6; niepowtarzane (brak instalacji - usunieta zgodnie ze zleceniem) |
| S2b-2 (5) | instalacja usunieta, galaz czysta | stan galezi sprawdza koordynator; kopia `rec-s1` = df141de, czysta |
| S2b-2 p. 6 | sciaga: tylko 2 wiersze | potwierdzone: `git diff --numstat` 2 / 2, wiersze 94 i 98 |
| S2b-2 p. 7 | forma do druku | czesciowo: dokument - dobrze; arkusz - R3 |

Wymaganie wlasciciela (glowna miara):

| Punkt | Ocena po S2b-2 |
|---|---|
| jeden dokument, prosty jezyk, do wydruku | spelnione dla dokumentu (8 stron, czytelny wydruk); 3 drobne miejsca jezyka (D11) |
| to, czego potrzebuje w rece | narzedzia sprawdzone na atrapach (ja, rundy 2 i 3) i na instalacji z paczki probnej (wg wykonawcy); na prawdziwym 0.3.3 - S2b-3 |
| co przygotowac i zabrac | spelnione (sekcja 1) |
| kolejnosc; jedna ramka; skaner; laptop albo PC | spelnione (zasada 4, skrot dnia, akapit o ramce porannej) |
| co zmierzyc: pole skanera, dolki, rowek, numer plytki przez ramke, gniazdo -> diody | spelnione (2.4 karton pierwszy, 2.5, 2.5a, 3.5, 3.7); D1 |
| jakie pliki przywiezc i gdzie polozyc | spelnione (czesc 5; dane pacjentow - N6 zamknieta) |
| po czym poznac, ze krok sie udal | 21 z 21 krokow ma "Udalo sie, gdy" i "Gdy sie nie uda"; 1 bledna rada awaryjna (R2) |
| arkusz obserwacji do wypelniania | tresc spelniona; wydruk nie (R3) |
| narzedzia sprawdzone na atrapach i na instalacji z nowej paczki | atrapy: tak; instalacja z paczki probnej (kod 7ebb5cd): wg wykonawcy; prawdziwe 0.3.3: S2b-3 |
| niesprawdzone oznaczone wprost | spelnione: 22 znaczniki + lista zbiorcza; 2 dopiski (D7, R2) |
| pytania ZEBRANE NA POCZATKU DOKUMENTU, bez zgadywania | NIESPELNIONE - R1 (pytania sa tylko w osobnym pliku); bez zgadywania: tak |

## 4. Zakres plikow i zasady

- Zakres: `git diff --name-only d8e7087 e3/sprzet` = 13 plikow: 11 w `Ramki/etap3/testy_sprzet_2026-11-28/`, raport
  `E3-S2_2026-11-21.md`, sciaga skanera (2 wiersze: 94 i 98). Zmian w programie, testach programu, instrukcjach: 0.
- ASCII: 0 bajtow spoza ASCII w 16 z 16 plikow zakresu. Konce wierszy: 3 pliki `.cmd` CRLF, 13 plikow LF.
- Dane osobowe: brak nazwisk i nazw zlecen w plikach paczki i w raporcie; przyklady "TEST1", "TEST5", "Tester". Opis
  wpisywany przez czlowieka w `pole_skanu.cmd` ma dopisek "Bez nazwisk" i trafia tylko do `wyniki\` (ignorowane przez
  `.gitignore` paczki).
- `t13_higiena.py`: 0 naruszen.
- Kopia `rec-s1` po probach: `git status --short` pusty, HEAD df141de; w katalogu paczki nie ma `wyniki\` ani
  `klucz_ramki.txt`. Kopia `integ`: tylko uruchomienie `t13_higiena.py`, bez zapisu.

## 5. Do decyzji wlasciciela

1. PILNE: strona pytan P1-P9 (termin 25.11.2026) - wyslac od razu, nie czekajac na S2b-3. Od P3 / P8 zalezy, czy ktos
   zdazy wgrac program ramki i odczytac klucz; od P9 - czy wolno kopiowac folder zlecen skanera.
2. Dwie plytki o tym samym numerze w jednej zmianie: program nie wstrzymuje ramki, gdy prace sa inne (pod plytka
   lezaca swieci wynik nowego skanu, bez pytania). Na dzien sprzetu obowiazuje zasada z kroku 3.8; czy po dniu sprzetu
   zmienic program - decyzja po pomiarach.
3. Karton do pomiaru pola (krok 2.4): lepsza bylaby sztywna plaska plyta (np. podkladka do pisania, plyta z szuflady)
   niz karton z pudelka - wygiecie 3 mm na 15 cm zmienia komunikat narzedzia (D1), choc liczby zostaja dobre.
4. Program po dniu sprzetu (nie blokuje): sprzeczne zdanie w pytaniu "Plytka nie z tego trybu" po przelaczeniu trybu;
   okno "Dzien skanera" przy 0 stozkach dalej wskazuje pole i brudne stozki (o stoliku mowi juz tylko program
   "Stanowisko"); ostatni krok okna proponuje kopie CALEGO folderu zlecen bez slowa o danych pacjentow.
5. Forma: wlasciciel dostaje PDF (dokument 8-9 stron, arkusz 4-5 stron, strona pytan) - kto drukuje i czy arkusz ma byc
   w 2 egzemplarzach (sobota / niedziela).
6. Z rund 1 i 2, dalej otwarte: czy narzedzia dnia sprzetu wchodza do paczki 0.3.3, czy zostaja na pendrivie; kto
   kopiuje wyniki do `<PC-katalog>\sprzet_2026-11-28\`.

## 6. Lista dla S2b-3

Pliki w `Ramki/etap3/testy_sprzet_2026-11-28/`, numery wierszy wg df141de. "[0.3.3]" = wymaga prawdziwej paczki.

1. **[P, R1] `PIERWSZE_TESTY_NA_SPRZECIE.md` w.26-31 (cala sekcja 0).** Jest: 4 wiersze z odsylaczem do pliku pytan.
   Ma byc (gotowy tekst):

       ## 0. Pytania do wlasciciela - odpowiedz najpozniej do srody 25.11.2026

       Nie znamy odpowiedzi i nie zgadujemy. Wpisz odpowiedz w tabeli ("nie wiem" to tez odpowiedz) i przekaz sesji
       prowadzacej projekt. Te same pytania z szerszym wyjasnieniem: osobna strona pytan. Najpilniejsze: P3, P1, P6, P8, P9.

       | Nr | Pytanie | Od odpowiedzi zalezy | Odpowiedz |
       |---|---|---|---|
       | P1 | Ktora ramka przyszla: wieczorna, poranna czy obie? Wkladka kwadratowa czy okragla? | plytki 1-3 albo 4-6; klawiatura (krok 3.9) tylko przy porannej; wkladka okragla: krok 3.7 na plytce okraglej | .......... |
       | P2 | Ktore plytki sa na miejscu (kwadratowe 1-6, okragle ramkowe 1-6, okragle testowe 8 i 9, stare) i czy maja wklejone magnesy? | co skanujesz (bez okraglych krok 2.5a odpada); bez magnesow ramka nie odczyta numeru (krok 3.5) | .......... |
       | P3 | Czy Raspberry Pi w ramce jest zlozone, ma karte SD i czy ktos wgral na nia program ramki? | cala czesc 3; bez programu ktos musi go wgrac PRZED sobota (kilka godzin) - kto i kiedy? | .......... |
       | P4 | Na jakim komputerze uruchomisz program (Windows 10 albo 11, 30 GB wolnego miejsca)? | laptop stanowiska: dochodzi czesc 4 | .......... |
       | P5 | Czy skaner stoi przy tym samym komputerze? Do jakiego folderu program skanera zapisuje skany? | inny komputer: skany przenosisz pendrivem, krok 2.7 odpada | .......... |
       | P6 | Jaka siec laczy komputer z ramka (router, hotspot)? Jaka siec Wi-Fi jest wpisana w ramce? | bez wspolnej sieci z czesci 3 zostaja kroki 3.1 i 3.2 | .......... |
       | P7 | Czy masz projekty STL (z exocad) prac probnych? | bez nich prace w kroku 2.7 beda szare "bez projektu" | .......... |
       | P8 | Czy ramka ma ustawiony klucz (haslo ramki) i czy go znasz? Dwie ramki musza miec TEN SAM klucz. | bez klucza odpadaja kroki 3.4-3.9; klucz przywiez na kartce, tu go NIE wpisuj | znam / nie znam / bez klucza |
       | P9 | Czy w programie skanera sa juz zlecenia pacjentow? Gdzie zalozyc osobny folder na skany testowe? | sa albo nie wiesz: osobny folder (krok 2.1), kopie calego folderu zlecen (krok 2.6) pomijamy | .......... |

   Tabele `| a | b |` obsluguje narzedzie stron (`instrukcje_html.md_na_html`), a `druk.py` przepuszcza wiersze
   zaczynajace sie od `|` bez zmian - po wygenerowaniu obejrzec szerokosc kolumny "Odpowiedz" (w razie potrzeby
   `<!-- kolumny -->` narzedzia). `ARKUSZ_OBSERWACJI.md` w.11: "(plik `PYTANIA_DO_WLASCICIELA.md`)" -> "(sekcja 0
   dokumentu)". Tresc 9 pytan ma byc ta sama w 3 miejscach: sekcja 0, plik pytan, arkusz w.13-29.
2. **[P, R2] `PIERWSZE_TESTY_NA_SPRZECIE.md` w.433-434.** Jest: `- Pasek "brak polaczenia" albo "zly klucz": sprawdz
   adres i klucz w ustawieniach. "drugi laptop": zamknij `ramka.cmd` i poczekaj pol minuty.` Ma byc:
   `- Pasek "brak polaczenia" albo "zly klucz": zamknij program, popraw adres i klucz w ustawieniach (punkt 1), uruchom
   program jeszcze raz. "drugi laptop": zamknij `ramka.cmd`, poczekaj pol minuty i kliknij w pasku "Przejmij ramke W"
   (rano: "Przejmij ramke P") - program sam ramki nie przejmuje.` Do znacznika w.449 dopisac "; przycisk 'Przejmij
   ramke'". Opcjonalnie [0.3.3]: 1 proba w sterowniku `okno38.py` (plan obcego komputera -> pasek "drugi laptop" ->
   klikniecie -> ramka swieci).
3. **[P, R3] strona do druku arkusza: `robocze\s2\b2\druk.py` (poza repo), uklad "arkusz".** Jest: punkty zlane
   w akapity, tabele z wierszami ok. 4 mm, linie uwag na 1/3 strony. Ma byc: kazdy wiersz zrodla w osobnej linii;
   tabele 2.5, 2.5a, 3.5 z wierszem co najmniej 8 mm i kolumnami na cala szerokosc strony; linie uwag na cala
   szerokosc; PDF obejrzany (podac liczbe stron). Wszystkie 4 strony wygenerowac ponownie po poprawkach 1-12.
4. **[D, D1] `PIERWSZE_TESTY_NA_SPRZECIE.md` w.211-212 ("Gdy sie nie uda" kroku 2.4).** Dopisac na poczatku: `Przy
   KARTONIE nie ma zdania "Dane sa PLASKIE" albo jest uwaga o podlozu: karton byl wygiety albo wokol niego widac
   stolik - liczby z wiersza 2 sa mimo to wymiarem pola; przepisz je, kratki "Dane sa PLASKIE" nie zaznaczaj.`
   W sekcji 1 w.53: "plaski karton" -> "plaski, sztywny karton albo plyta".
5. **[0.3.3, D2] `ZALACZNIKI.md` czesc C** - po potwierdzeniu poleceniami z raportu S2b-2 (sekcja 7, pozycje 3 i 4;
   dodac to samo dla `KOMUNIKATY['plytka_czeka_na_numer']`, `JEST_SKAN_BEZ_NUMERU` i
   `PRZYCZYNY_BLEDU_ANALIZY['znaczniki_0']`): w.66-69, w.72-76, w.77-81 zastapic tekstami "W programie" z sekcji 2a
   tego raportu (3 teksty), w.49-50 zrodlo cytatow = wydanie 0.3.3, zdjac 2 znaczniki i zdanie wstepu.
6. **[0.3.3, D2] `PIERWSZE_TESTY_NA_SPRZECIE.md`:** w.291-293 prawa kolumna -> `przepisz nawias. Gdy jest "0 z 3":
   program sam dopisuje "albo w skanie jest stolik (podloze) wokol plytki" - najpierw sprawdz to (krok 2.3). Inaczej
   plytka nie miesci sie w polu albo lezy z boku: ustaw ja na srodku, plik sprawdz krokiem 2.4` (wiersze najwyzej 96
   znakow - D10a); w.299 zdjac znacznik i zdanie o N = 0 skrocic; w.180-181 "a komunikaty mowia" -> "a komunikaty okna
   "Dzien skanera" mowia"; w.421 zdjac znacznik (tytul panelu bez zmian); w.39 nazwa paczki; w.13-14 usunac wiersz
   legendy; w.3-4 "Stan:".
7. **[D, D4] w.294-295 (i w.447-448).** Jest: `i zeskanuj ja JESZCZE RAZ (stare pytanie zostaje)`. Ma byc: `i zeskanuj
   ja JESZCZE RAZ. Stare pytanie zostaje i ma teraz zdanie bez sensu ("plytka poranna ... tryb Poranek") - to znany
   blad napisu, liczy sie nowy skan`.
8. **[D, D8] w.339-341 ("Gdy sie nie uda" kroku 3.3).** Dopisac: `Menu nie przyjmuje klawiszy albo samo sie zamyka:
   Windows + R, wpisz cmd i Enter, a w czarnym oknie uruchamiaj jedna pozycje naraz, np.
   C:\Sprzet_testy\narzedzia\ramka.cmd ramka-w.local 7 (klucz), potem ... ramka-w.local 1.`
9. **[D, D5] w.225-226 i `ARKUSZ_OBSERWACJI.md` w.71.** Dopisac przyklad: `godzina to 6 cyfr przed "_pole" w nazwie
   pliku z wiersza "Zapisano:", np. ..._20261128_101502_pole.txt = 10:15:02; wpisz 101502`.
10. **[D, D6] `ARKUSZ_OBSERWACJI.md` w.87.** Jest: `Wiersz `podloze w skanie:` inny niz "nie" - w ktorych skanach`.
    Ma byc: `Wiersz `podloze w skanie: PRAWDOPODOBNIE TAK` - w ktorych skanach`.
11. **[D, D3, D7] `PIERWSZE_TESTY_NA_SPRZECIE.md`:** w.411 na koncu punktu 5 dopisac `Zdejmij ja.`; w.267 znacznik:
    dopisac `; napisy przyciskow w pytaniu przy pakowaniu`.
12. **[D, D10, D11] wydruk i jezyk:** w.3 i w.29 nazwy plikow `.md` -> "arkusz obserwacji", "strona pytan" (albo nazwy
    PDF, ktore wlasciciel dostanie); w.332-333 `ramka-p.local` bez lamania po lacznku (w `druk.py`: `white-space:
    nowrap` dla kodu) ; w.4 "(kod paczki 0.3.3)" -> "wersji 0.3.3 programu"; `ZALACZNIKI.md` w.117 "51 testow" ->
    "51 testow (dzis 57)".
13. **[0.3.3] potwierdzenia z listy wykonawcy (raport S2b-2, sekcja 7, pozycje 1-4):** nazwa, rozmiar i sumy paczki
    `Stanowisko_0.3.3.zip`; kody 10 i 0 instalatora; 57 testow narzedzi na kodzie wydania; `README.md` w.17-20 "Stan".
14. **[D, D9 - dla koordynatora, plik poza zakresem wykonawcy] `Ramki/sciaga_skaner_DentalScan_2026-11-16.md` w.167.**
    Jest: "Czy plaszczyzne ciecia po skanie mozna pominac albo ustawic ponizej plytki? Czy da sie to zapamietac
    w zleceniu?" Ma byc: "Czy plaszczyzne ciecia po skanie da sie ustawic miedzy stolikiem a wierzchem plytki (co
    najmniej 3 mm ponizej wierzchu)? Czy da sie to zapamietac w zleceniu?"

Odlozone bez terminu (po dniu sprzetu): N20, N11 w narzedziu, D13, dalszy skrot po odpowiedziach P1-P9 (D12).

### Do decyzji wlasciciela / koordynatora (nie dla wykonawcy S2b-3)

Sekcja 5, punkty 1-6.
