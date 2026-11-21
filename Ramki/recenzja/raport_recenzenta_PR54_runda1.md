# Raport recenzenta - PR #54 (E3-S1), runda 1

Data: 2026-11-21, 12:08-12:30. Zakres: `git -C <PC-katalog>\qc diff main...e3/sprzet`, HEAD 3e8d08f - 11 nowych
plikow (2283 wiersze), 0 zmian w kodzie programu. Kopia do prob: `<PC-katalog>\qc-wt\rec-s1` (detached 3e8d08f).

Metoda: (1) dokument i arkusz przeczytane w calosci "oczami wlasciciela z wydrukiem"; (2) 28 pozycji dokumentu
(polecenia, pliki, przyciski, komunikaty) sprawdzone w kodzie kopii, w instalacji 0.3.1 `<PC-katalog>\t0\s1\Stanowisko`
(tylko odczyt i uruchamianie) albo proba; (3) wlasne proby narzedzi: 26 testow paczki, 23 proby `pole_skanu` na skanach
sztucznych wykonawcy i wlasnych przerobkach, 18 prob `ramka_proba` na atrapie ramki w tym samym procesie, 7 prob plikow
`.cmd` z katalogu ze spacjami przez `Polecenie.cmd` instalacji, 6 wstrzykniec bledu (kazde cofniete), 3 przebiegi
`pole_skanu.py` na kodzie `main` 8001b55 (po scaleniu O1); (4) raport wykonawcy czytany na koncu.
Pliki robocze i logi: `<PC-katalog>\koordynator\robocze\rec-s1\` (`p01`...`p07`, `proby_*.py`, `proby_*.json`).
Pelnego pytest nie uruchamialem. Liczby ponizej sa z moich prob, chyba ze napisano "wg wykonawcy".

## 0. Werdykt

WERDYKT: do scalenia po poprawkach - B 0, P 9, D 13.

Wyjasnienie: paczka nie zmienia programu i niczego nie psuje (narzedzia pisza tylko do `..\wyniki` obok siebie i do
`<instalacja>\dane\dzien_skanera`), wiec sam szkic mozna scalic bez ryzyka dla stanowiska. Uwagi P dotycza tego, co
wlasciciel dostanie do reki: narzedzie `pole_skanu` w 3 sytuacjach podaje zdanie albo liczbe, ktore sa nieprawdziwe
(pole nie-kolowe, "cala plytka jest w skanie", licznik rowka), a dokument i arkusz maja 4 luki wazne dla decyzji po
weekendzie. Wszystkie P da sie zamknac w etapie 2 - warunek: dokument NIE trafia do wlasciciela przed ich zamknieciem.
Decyzja "scalic szkic teraz i zamknac P w etapie 2" albo "trzymac PR do etapu 2" nalezy do koordynatora.

Ocena ogolna dokumentu: kolejnosc jest sensowna, kazdy z 20 krokow mowi, co zrobic, po czym poznac sukces (19 z 20;
krok 1.4 opisowo), co zrobic przy porazce (22 akapity "Gdy ...", w wiekszosci z wyjsciem "idz do kroku X") i co wpisac do
arkusza (19 z 20). Pytania sa na poczatku i niczego nie zgaduja. Zgodnosc z programem: 28 z 28 pozycji istnieje,
3 nazwy nieprecyzyjne (U18). Slabosci: dlugosc (ok. 12 stron A4 + 4 strony arkusza), 19 miejsc (lista 1b) z jezykiem
koordynatora zamiast jezyka wlasciciela (akapity "Stan:"), forma (surowy plik .md).

## 1. Uwagi

| Nr | Waga | Plik:linia | Scenariusz | Propozycja |
|---|---|---|---|---|
| U1 | P | `narzedzia/pole_skanu.py:161,175-180,231,247`; dokument w.251-262; arkusz w.60-67 | Pole skanera nie jest kolem (np. prostokat). Plaski karton w polu 100 x 80 mm -> "Dane skanu mieszcza sie w kole o srednicy ok. 127,9 mm"; kwadrat w polu 130 x 90 mm -> "POLE SKANERA MA OK. 134,4 mm" (proby 9, 10). Wlasciciel wpisuje do arkusza 128 mm, a plytka 100 mm nie miesci sie w 80 mm. | Obok kola opisanego podawac najmniejsza szerokosc danych (najwezszy przekroj otoczki) i najwieksze kolo wpisane; zdanie "POLE SKANERA MA OK." tylko gdy obie liczby roznia sie o mniej niz 5 mm, inaczej "pole nie jest kolem: ... x ... mm". Arkusz: dwa pola (najwezej / najszerzej). Test na polu prostokatnym. |
| U2 | P | `narzedzia/pole_skanu.py:180,243-245`; dokument w.252 | Plytka okragla 100 mm, pole 120 mm przesuniete o 15 mm (5 mm plytki poza polem): wiersz 2 "Cala plytka (kolo opisane 100,0 mm) jest w skanie: pole skanera jest CO NAJMNIEJ takie", wiersz 3 "brzeg w 58 z 72 kierunkow" (2 z 2 prob; to samo na skanie wykonawcy plytki ramkowej nr 3: 51 z 72). Zdanie o calej plytce jest nieprawdziwe, a dokument powtarza je jako znaczenie wiersza 2. | "Cala plytka jest w skanie" pisac tylko przy brzegu 72 z 72; inaczej: "plytka wystaje poza pole w kierunkach ... - przesun plytke na stoliku i zeskanuj ponownie". Test: pole przesuniete. |
| U3 | P | `narzedzia/pole_skanu.py:38,210-216,268-271`; dokument w.255-256, w.267-270; arkusz w.65-66 | Licznik "punktow w miejscu rowka" ma byc dowodem, ze skaner widzi rowek pokrywki. Plytka KWADRATOWA bez rowka (pelny skan sztuczny): 21037 punktow; plytka okragla ramkowa z rowkiem: 19763 (proby 3, 16, 17). Licznik nie odroznia rowka od zwyklej scianki lezacej 0,25-1,0 mm wewnatrz obrysu nominalnego; na prawdziwej plytce wystarczy srednica mniejsza o 0,5 mm. Dokument (w.267-270) cytuje tylko 13,9-19,8 tys. i 0, pomija 21 tys. dla kwadratu (wykonawca zna te liczbe - raport A5). Dla plytki kwadratowej narzedzie mimo to pisze o rowku plytki okraglej ramkowej. | Rowek liczyc jako uskok promienia scianki (mediana promienia punktow 0,5-1,5 mm ponizej wierzchu minus mediana 1,5-2,5 mm; rowek = uskok >= 0,4 mm w >= 36 kierunkach) i tylko dla ukladow `okragla_ramkowa_*`; dla innych "nie dotyczy". Do czasu poprawki: z dokumentu i arkusza usunac licznik, zostawic "scianka widoczna do ... mm". |
| U4 | P | `narzedzia/pole_skanu.py:336-339`; `pole_skanu.cmd:8,25` | Program skanera nazywa pliki tak samo w kazdym zleceniu (albo wlasciciel przeciaga plik z dwoch folderow krokow sesji). Drugi wynik nadpisuje pierwszy bez ostrzezenia: 1 plik `_pole.txt` zamiast 2, w `.json` 110,3 -> 120,3 (proba 6). Skany wykonawcy maja wlasnie takie same nazwy w 10 folderach. | Do nazwy wyniku dodac date i godzine (`<skan>_<RRRRMMDD_GGMMSS>_pole.*`) albo nazwe folderu nadrzednego; test na dwoch plikach o tej samej nazwie. |
| U5 | P | dokument w.228-235, w.258-264, w.541-551; `pole_skanu.py:229-235` | Skaner zapisuje w skanie takze stolik / uchwyt wokol plytki. Proba 11: pelny skan sztuczny kwadratu nr 1 i okraglej nr 8 + plaski "stolik" 180 x 180 mm na poziomie spodu plytki -> program nie rozpoznaje plytki (`malo_stozkow`, znaleziono 0), `pole_skanu` pisze "ok. 254 mm". Dokument przy czerwonej ocenie prowadzi tylko tropem "pole za male" i mowi "ponowny skan nie pomoze"; lista niesprawdzonych nie ma pozycji "czy w skanie jest stolik". Uwaga: stolik sztuczny, zachowanie na prawdziwym skanie nieznane; to zachowanie programu (`rozpoznaj_uklad`), nie paczki. | Krok 2.3: "gdy czerwona, a wiersz 2 pokazuje wiecej niz ok. 140 mm albo `obrys` jest duzo wiekszy niz plytka - w skanie jest podloze; zrob zdjecie ekranu programu skanera i zapisz". Pozycja w liscie niesprawdzonych i w arkuszu ("w skanie widac stolik: tak / nie"). Dla koordynatora: POTRZEBUJE - sprawdzic rozpoznanie plytki ze stolikiem na pierwszym prawdziwym skanie. |
| U6 | P | dokument w.511-518; arkusz w.142-146 | Kroki 2.7 i 3.8: skan trafia do folderu programu skanera, okno "Dzien skanera" jest juz zamkniete i spakowane (2.6), program "Stanowisko" skanow nie kopiuje (w ustawieniach sa tylko `wyniki`, `podglady`, `logi`). Lista "co przywiezc" nie zawiera tych plikow skanow. Gdy program pokaze "Analiza skanu nie powiodla sie", jedyny dowod zostaje w laboratorium. | Czesc 5, nowy punkt: "folder zlecenia testowego z krokow 2.7 i 3.8 (pliki skanow, bez danych pacjentow)" + `C:\Stanowisko\ustawienia.toml`; podfolder `skany_program\` w ukladzie odbioru; wiersz w arkuszu. |
| U7 | P | dokument w.27-30, w.42-46 | Pytania maja byc odpowiedziane "PRZED testami" i wpisane do arkusza - czyli w dniu testow. Odpowiedz P3 "na karcie SD nie ma programu ramki" odkryta w sobote = cala czesc 3 od kroku 3.2 przepada (2 godziny planu). Brak terminu i adresata odpowiedzi. | Na poczatku sekcji 0: "Odpowiedz koordynatorowi do <data, np. 25.11> - od P1, P3 i P6 zalezy, co przygotujemy przed weekendem (karta SD, klucz, siec)". P3 pierwsze na liscie. |
| U8 | P | arkusz w.68-76 (tabela 2.5), w.58-59 | Decyzje po weekendzie (regula ksztaltu, wariant C) wymagaja dla KAZDEJ zeskanowanej plytki: jaki uklad rozpoznal program (kwadratowa / okragla, pewnie / niepewnie) i czy widac scianke boczna. Tabela 2.5 ma kolumny: plytka, prace, ocena okna, pole, dolki, brzeg, czas - ukladu i scianki nie ma; arkusz 2.4 notuje uklad tylko dla pierwszej plytki. | Tabela 2.5: kolumny "plytka naprawde (kwadr. / okr.)", "program mowi (uklad, pewnie?)", "scianka do mm"; wyrzucic "czas skanu" (jest w 2.3). 8 wierszy zamiast 6. |
| U9 | P | `narzedzia/test_pole_skanu.py`, `test_ramka_proba.py` | Luki w testach: (a) scianka boczna i licznik rowka nie sa sprawdzane przez zaden test - wstrzykniecia M2 (scianka nigdy niewidoczna) i M6 (licznik zawsze 0): 9 passed; (b) watek podtrzymania planu w `gniazda` - M4 (usuniety start watku): 17 passed; (c) brak testu ramki z kluczem (401) i ramki zajetej przez inny komputer (409 `inny_laptop`). Wiersz 6 raportu (jedyna odpowiedz na pytanie o scianke i rowek) jest bez testu. | Testy: pelny skan -> `scianka_boczna.kierunkow_z_danymi == 72` i tekst wiersza 6; pole 95 -> "NIE widac"; plytka ramkowa z rowkiem i bez; `gniazda --wszystkie` z `wazny_s` skroconym i czekaniem dluzszym niz waznosc; atrapa z kluczem; plan obcego komputera. |
| U10 | D | `narzedzia/pole_skanu.py:329-331` | Plik uciety, pusty, tekstowy albo sam naglowek (4 z 4): "BLAD: nie da sie policzyc pliku ...: ValueError: zero-size array to reduction operation maximum which has no identity" (proba 4). | "Plik jest pusty albo uszkodzony (0 trojkatow) - zapisz skan w programie skanera jeszcze raz"; szczegol techniczny tylko do `.json`. |
| U11 | D | `narzedzia/pole_skanu.cmd:21-28` | Na pytanie o numer wlasciciel wpisuje "nie wiem" albo litere: wypisuje sie angielskie `usage: ... error: argument --numer: invalid int value` i "Kod: 2 ... 2 = blad pliku" (proba C3). | W `.cmd` sprawdzic, czy odpowiedz to cyfra 1-9; inaczej traktowac jak pusty Enter. |
| U12 | D | `narzedzia/pole_skanu.py:198-203,253-258`; arkusz w.63 | Dla plytki kwadratowej wiersz 4 ma dwa podwiersze ("uklad wieczorna: 2 z 4", "uklad okragla_wieczorna: 4 z 4"); arkusz ma jedno pole "dolki ... z 4" - nie wiadomo, ktora liczbe wpisac. Dla `okragla_ramkowa_*` (kod `main`) drugiego podwiersza nie ma (nazwa "druga" liczona przez obciecie `okragla_`). | Na ekranie tylko uklad rozpoznany; porownanie z drugim ksztaltem w `.json` albo z dopiskiem "(gdyby to byla plytka okragla)". Mapowanie nazw dla `okragla_ramkowa_*`. |
| U13 | D | `narzedzia/ramka_proba.py:75-81,190-195,376-379`; `ramka.cmd` | Ramka z kluczem (proby R1): bez klucza i ze zlym kluczem "BRAK POLACZENIA Z RAMKA ... ramka wymaga klucza (odpowiedz 401) - podaj --klucz" + rada "Sprawdz: ramka ma prad..."; `test-led`: "RAMKA ODMOWILA testu diod: kod 401" bez rady. Menu `ramka.cmd` nie ma jak podac klucza. Po paczce O4 (instalator ramki wstawia losowy klucz) to bedzie przypadek podstawowy - patrz zadanie 3 etapu 2. | Osobny komunikat "RAMKA ODPOWIADA, ale wymaga klucza"; `ramka.cmd` czyta `klucz` i `port` z `[ramki]` w `<instalacja>\ustawienia.toml` (albo zmienna `RAMKA_KLUCZ`). |
| U14 | D | `narzedzia/ramka_proba.py:249-279` | Ramke trzyma inny komputer (wlasciciel nie zamknal programu "Stanowisko"; proba R3): `gniazda` po kolei wypisuje 19 odmow pod rzad bez czekania i zapisuje 19 wierszy "ODMOWA 409"; `--wszystkie`: "RAMKA ODMOWILA: kod 409 inny_laptop" bez rady; na koncu "Ramka zgaszona", choc plan drugiego komputera zostal (plan obcego nietkniety - to dobrze). | Po pierwszej odmowie `inny_laptop` przerwac z rada "zamknij program Stanowisko"; "Ramka zgaszona" tylko gdy `DELETE /plan` sie udal. |
| U15 | D | `narzedzia/ramka_proba.py:260-271` | `gniazda` po kolei, plytka zdjeta albo ramka gubi odczyt w trakcie (proba R5): narzedzie pyta dalej o kolejne gniazda i przy samym Enterze zapisuje "ok", choc plytki juz nie ma (plan przyjety kodem 200; wg regul ramki gniazda bez plytki nie swieca). | Przed kazdym pytaniem sprawdzic `plytka` w `/stan`; gdy inna niz na starcie: "RAMKA NIE CZYTA JUZ PLYTKI nr ..." i wiersz w CSV. |
| U16 | D | `narzedzia/ramka.cmd:27-29,52-55,59-63,75` | Adres ze spacja ("ramka w") albo przesuniecie "jeden": angielskie `usage: ... unrecognized arguments` (proby C7, R7). Uklad domyslny w pytaniu to zawsze `wieczorna`, takze dla ramki porannej. Lista ukladow wpisana na sztywno w tekscie pytania. | Cudzyslowy przy `--adres "%ADRES%"`; uklad domyslny z roli ramki (`/stan`), lista ukladow z kalibracji. |
| U17 | D | arkusz w.27, w.96, w.118, w.129, w.9-23 | Arkusz i dokument rozchodza sie: 1.1 "wersja wypisana przez `py -3.12 --version`" (dokument tego nie kaze); 3.3 "`ping` odpowiada" (dokument nie zna `ping`); "Temperatura po godzinie pracy" (brak kroku); 3.7 kierunki "do przodu / do tylu", narzedzie pyta "w prawo / w dol"; brak pola na odpowiedz P7. | Usunac albo dopisac krok; jeden slownik kierunkow ("w prawo / w lewo / w strone przodu ramki / w strone tylu"); pole P7. |
| U18 | D | dokument w.200, w.297, w.276-280, w.199 | Nazwy: przycisk to "Zrzut ekranu (za 3 s)"; ostatni krok okna nazywa sie "Na koniec: kopia CALEGO folderu zlecen programu skanera", nie "Skopiuj caly folder zlecen skanera"; tytul okna ma dopisek "(sesja ...)". Krok 2.5 punkt 2 (po jednym skanie kazdego rodzaju plytki) nie mowi, w ktorym kroku okna zapisac te skany (okno ma jeden krok "Skan 7: druga plytka"). | Poprawic nazwy; dopisac: "wszystkie skany dodatkowych plytek rob w kroku 12 okna (Skan 7), w polu notatki wpisz, ktora to plytka". |
| U19 | D | dokument w.135-141 | Notatnik: plik `.toml` nie otwiera sie dwuklikiem (trzeba "Otworz za pomoca"); wiersz `operatorzy` jest w w. 99 pliku, w innej sekcji niz foldery; w nowym Notatniku sa dwa kodowania "UTF-8" i "UTF-8 z BOM", a plik z BOM to blad samokontroli (`samokontrola.py:12`). | "Prawy klawisz -> Otworz za pomoca -> Notatnik"; "szukaj: Ctrl+F"; "kodowania nie zmieniaj; gdyby pytal: UTF-8, NIE 'UTF-8 z BOM'". |
| U20 | D | `PIERWSZE_TESTY_NA_SPRZECIE.md`, `ARKUSZ_OBSERWACJI.md` (calosc) | Wlasciciel dostaje plik `.md`: w Notatniku widac `**`, `###`, odwrotne apostrofy; 197 wierszy dokumentu ma ponad 90 znakow (zawijanie); tabele arkusza z kropek i kresek trzymaja sie tylko w czcionce o stalej szerokosci. Wydruki z sekcji 1 (w.80-81) wskazane sciezkami repo, ktorych wlasciciel nie zna. | Etap 2: PDF albo HTML gotowy do druku (jest `narzedzia/instrukcje_html.py`), arkusz jako tabele; wydruki dolaczone do tego samego pliku. |
| U21 | D | dokument w.177-183, w.243-247, w.379-380, w.419-430 | Znaczniki: brak przy rzeczach, ktorych nie dalo sie sprawdzic bez ekranu - przeciaganie pliku na `pole_skanu.cmd`, dwuklik `.cmd` z `C:\Sprzet_testy`, menu `ramka.cmd` z klawiatury (wg wykonawcy niesprawdzone; u mnie menu z pliku wejsciowego dziala - proba C6). Nadmiarowy: caly krok 3.6 oznaczony, a punkt (c) "NUMER SPOZA TEJ RAMKI" jest sprawdzony na atrapie. | Dopisac znacznik w 1.4 / 2.4 / 3.3 i pozycje w liscie zbiorczej ("dwuklik i przeciaganie plikow .cmd"); w 3.6 rozdzielic. |
| U22 | D | dokument - 19 akapitow "Stan:", w.539-582, w.585-613 | Dlugosc i jezyk - szczegoly w sekcjach 1a i 1b. | Jak w 1a i 1b. |

### 1a. Dlugosc dokumentu

Pomiar: 613 wierszy, 5376 slow, 34700 znakow. To ok. 12 stron A4 po zlozeniu (11 pt, ok. 450 slow na strone) albo
ok. 14-15 stron surowego tekstu z Notatnika (197 wierszy zawija sie). Arkusz: 158 wierszy, 1424 slowa = 3-4 strony.
Z karta "Dnia skanera", sciaga skanera i instrukcja instalacji wlasciciel ma w reku ponad 20 stron. Za duzo jak na
"prosty dokument do wydruku"; przy sprzecie potrzebne sa naraz najwyzej 3 strony.

Podzial wierszy: pytania 41, lista rzeczy 27, kolejnosc 13, czesc 1 - 79, czesc 2 - 158, czesc 3 - 141, czesc 4 - 23,
czesc 5 - 30, lista niesprawdzonych 32, lista etapu 2 - 14, zalacznik A - 29.

Co skrocic (lacznie ok. 150 wierszy, zostaje ok. 460 = 9 stron):

1. 19 akapitow "Stan: ..." (ok. 62 wiersze) - to wiadomosc dla koordynatora (liczby prob, "kod 0", "sumy 210 z 210").
   Przeniesc do zalacznika "Stan sprawdzenia" (osobny plik albo raport); przy kroku zostawic jeden wiersz
   "[NIE SPRAWDZONE BEZ SPRZETU: co dokladnie]".
2. "Zbiorcza lista: miejsca do domkniecia w etapie 2" (w.571-582, 14 wierszy) - po etapie 2 usunac w calosci.
3. Zalacznik A (w.585-613, 29 wierszy) - zastapic 3 wierszami z odwolaniem do instrukcji z paczki O4
   (`instrukcje/ramka_raspberry_pi.md`); to nie jest robota dla wlasciciela przy sprzecie.
4. Krok 1.3 punkt 2 (start `--atrapa`, w.161-165) - wyrzucic; start prawdziwy (punkt 3) wystarcza.
5. Krok 2.5 "Stan" (w.286-293) i krok 2.7 "Co program pokazuje w innych przypadkach" (w.324-334) - zamienic na
   tabelke 4 wierszy "widzisz to -> zrob to".
6. Czesc 5, uwaga o `Polecenie.cmd -m stanowisko.dzien_skanera` (w.532-535) - po O4 zbedna.
7. Uklad: 1 strona "skrot dnia" (kolejnosc, 3 liczby, wyjscia awaryjne), potem osobne karty "Komputer" (2 strony),
   "Skaner" (3 strony), "Ramka" (3 strony), "Pliki z powrotem" (1 strona) - kazda od nowej strony, zeby przy
   skanerze lezala tylko karta skanera i arkusz.

### 1b. Jezyk - miejsca do poprawy (cytaty doslowne)

Jezyk krokow ("Co zrobic", "Udalo sie, gdy", "Gdy sie nie uda") jest prosty. Zargon siedzi glownie w akapitach
"Stan:" i w odwolaniach do nazw wewnetrznych:

| Wiersz | Cytat | Co zrobic |
|---|---|---|
| 39-40 | "nie zna jeszcze plytek okraglych ramkowych 1-6 [ETAP 2: nazwy ukladow okraglych i ich obsluga na ramce]" | "uklad" -> "rodzaj plytki"; znacznik do usuniecia po etapie 2 |
| 70 | "format exFAT albo NTFS" | "zwykly pendrive; gdyby duzy plik nie dal sie skopiowac - zapisz to" |
| 150-151 | "kod 4 bez Pythona, potem kod 10, po zmianie 3 wierszy kod 0; sumy paczki 210 z 210; pakiety 73 z 73" | do zalacznika |
| 174 | "samokontrola ZIELONA: ok 14, ostrzezenia 7; oba starty kodem 0" | do zalacznika |
| 237-238 | "takie same z kopii programu i z instalacji: 10 z 10" | do zalacznika |
| 266-270 | "licznik 'punktow w miejscu rowka' dal 13,9-19,8 tys. ... sprawdzona tylko na plaskiej siatce sztucznej" | do zalacznika; patrz U3 |
| 286-290 | "okno nazywa je 'okragla_wieczorna' / 'okragla_poranna' i pisze 'dolki kodu odczytane jako 1 - to nie jest numer plytki tego ukladu ...'" | po O1 napisac od nowa prostym zdaniem |
| 303 | "sprawdzenie paczki: sumy 44 z 44" | do zalacznika |
| 313-314 | "bierze do analizy WSZYSTKIE pliki `.stl` ... (sprawdzone 21.11: 3 pliki zastane - 3 wziete do analizy)" | "program przeanalizuje takze stare skany, ktore juz leza w tym folderze" |
| 331-332 | "plik ma inne rozszerzenie niz `.stl` (program patrzy tylko na `*.stl`, takze w podfolderach)" | "plik nie konczy sie na .stl" |
| 340-341 | "czy program skanera zapisuje plik jednym ruchem ... i czy nie trzyma go otwartego" | do zalacznika |
| 390-391 | "to, czy program ramki slucha w sieci (a nie tylko 'u siebie')" | do zalacznika |
| 445-446 | "19 z 19 gniazd wieczornych i 24 z 24 porannych w swoich blokach diod" | do zalacznika |
| 455-456 | "w sekcji `[ramki]`, wpisz adres ...: `wieczorna_host = \"...\"`" | pokazac caly wiersz przed i po, jak w kroku 1.2 |
| 468-470 | "ramki polaczone 3,7 s po starcie programu, 'Test LED' dociera w 0,1 s" | do zalacznika |
| 490-494 | "findstr /c:\"KnownDlls\" /c:\"proces silnika\" ..." + "Policz wiersze" | dopisac jedno zdanie, co to sprawdza ("czy program analizy nie przerywal pracy") |
| 502 | "Sprawa 4 (czy zapis na dysk zatrzymuje okno ponad 0,2 s) wymaga plikow testowych" | wyrzucic z dokumentu wlasciciela |
| 532-534 | "poleceniem `Polecenie.cmd -m stanowisko.dzien_skanera`), sesja zapisze sie w `C:\Stanowisko\wersje\<wersja>\program\dane\dzien_skanera\`" | wyrzucic po O4 |
| 587-613 | caly Zalacznik A ("dtparam=spi=off", "isolcpus=3", "scp -r", "usluga systemowa") | zastapic odwolaniem do instrukcji O4 |

Slowa do zamiany w calym dokumencie: "uklad" (10 razy, w sensie "rodzaj plytki"), "atrapa" (11 razy; zostawic tylko we wstepie), "sesja",
"kod N", "sumy", "pakiety", "skan sztuczny" w krokach (zostaje w zalaczniku).

### 1c. Czy dokument obiecuje cos, czego program nie robi

Nie znalazlem obietnicy bez pokrycia. Trzy miejsca do pilnowania: (1) w.59 "Ramka nie ma hasla" - prawdziwe dla
programu ramki bez pliku konfiguracji, nieprawdziwe po instalacji skryptem O4 (losowy klucz); (2) w.103-104 "srednica
pola skanera - krok 2.4" - narzedzie podaje srednice kola opisanego, co jest polem tylko dla pola kolowego (U1);
(3) w.255-256 wiersz 6 jako odpowiedz na pytanie o rowek (U3). Rzeczy, ktorych program nie robi, sa nazwane wprost:
brak narzedzia zapisu kalibracji (w.449), brak ostrzezenia o plytce nie od tej ramki (w.428-430), przycisk pomiaru
szczegolowego (w.304-305), brak instalatora ramki (w.45-46, w.611-613).

## 2. Wlasne proby

| nr | polecenie / proba | wynik |
|---|---|---|
| 1 | `py.cmd -m pytest ..\etap3\testy_sprzet_2026-11-28\narzedzia -q -p no:cacheprovider` | 26 passed, 0 failed, 40,1 s, kod 0 |
| 2 | `pole_skanu.zmierz` na skanach sztucznych wykonawcy z polem kolowym (prawda w nazwie katalogu): kwadrat nr 1 pole 110; okragla nr 8 pole 95; kwadrat nr 1 pole 90 | 110,3 mm (rozpoznana, brzeg 26 z 72); 95,3 mm (rozpoznana, brzeg 0 z 72); 90,4 mm (NIE rozpoznana, 1 stozek) - blad 0,3-0,4 mm, 3 z 3 zgodne |
| 3 | pelne skany sztuczne (bez pola): kwadrat nr 1, okragla testowa nr 8 - wiersz 6 (scianka, rowek) | kwadrat: scianka 72 z 72 kierunkow do 7,8 mm, "punktow w miejscu rowka" 21037 (plytka kwadratowa NIE MA rowka); okragla testowa: 72 z 72, do 7,9 mm, punktow 0 |
| 4 | `pole_skanu.main` na plikach zlych: uciety w polowie, pusty (0 bajtow), tekst w .stl, sam naglowek 84 bajty | 4 z 4: kod 2, komunikat `BLAD: nie da sie policzyc pliku ...: ValueError: zero-size array to reduction operation maximum which has no identity`; plikow wyniku brak |
| 5 | `pole_skanu.main` na `nie_plytka.stl` (prostopadloscian 100 x 100 x 10); na katalogu zamiast pliku | kod 3, "NIE ROZPOZNANA", srednica ok. 141,0 mm (przekatna kwadratu 100 mm - poprawnie); katalog: kod 2 "nie ma pliku" |
| 6 | ta sama nazwa pliku skanu z dwoch folderow (`pole_110\skan_wieczorna_n1_s0011.stl`, potem `pole_120\...`) do jednego `--wynik` | 1 plik `_pole.txt` zamiast 2; `srednica_danych_mm` w `.json`: 110,3 -> 120,3 (pierwszy wynik nadpisany bez ostrzezenia) |
| 7 | okragla testowa nr 8 (100 mm), pole kolowe 120 mm przesuniete o 15 mm od srodka plytki (5 mm plytki poza polem); to samo z przesunieciem (-12, 9) | 2 z 2: wiersz 2 mowi "Cala plytka (kolo opisane 100,0 mm) jest w skanie: pole skanera jest CO NAJMNIEJ takie", a wiersz 3: brzeg w 58 z 72 kierunkow - zdanie "cala plytka jest w skanie" jest nieprawdziwe |
| 8 | kwadrat nr 1, pole kolowe 140 mm przesuniete o 30 mm | NIE rozpoznana (2 stozki), srednica ok. 134,7 mm (prawda 140; -5,3 mm) |
| 9 | plaski "karton" w polu PROSTOKATNYM 100 x 80 mm | "Dane skanu mieszcza sie w kole o srednicy ok. 127,9 mm" - wlasciciel zapisze pole 128 mm, a plytka 100 mm nie miesci sie w 80 mm |
| 10 | kwadrat nr 1 w polu prostokatnym 130 x 90 mm | "POLE SKANERA MA OK. 134,4 mm", brzeg 38 z 72 kierunkow - liczba nie opisuje pola 130 x 90 |
| 11 | pelny skan kwadratu nr 1 i okraglej nr 8 + plaski "stolik" 180 x 180 mm wokol plytki na poziomie spodu plytki (skaner widzi podloze) | 2 z 2: plytka NIE rozpoznana (`malo_stozkow`, stozkow znaleziono 0), srednica ok. 254 mm - zachowanie programu (`rozpoznaj_uklad`), nie paczki; dokument nie ma na to kroku |
| 12 | `--numer` pominiety (sam Enter w `pole_skanu.cmd`): kwadrat nr 1, okragla nr 8, skany pelne | 2 z 2 rozpoznane pewnie, numer z dolkow 1 i 8 (zrodlo: dolki) |
| 13 | `ramka_proba` na atrapie W z kluczem (R1): `stan` bez klucza / zly klucz / dobry klucz; `test-led` bez klucza | kod 2 "BRAK POLACZENIA ... ramka wymaga klucza (odpowiedz 401)"; kod 2 (to samo); kod 0 "RAMKA ODPOWIADA (2 ms)"; kod 1 "RAMKA ODMOWILA testu diod: kod 401" |
| 14 | brak polaczenia (R2): port zamkniety; nazwa `ramka-w.local` nie do znalezienia; `gniazda` przy zamknietym porcie; adres ze spacja | kod 2 po 2,1 s; kod 2 po 2,7 s ("getaddrinfo failed"); kod 2; wyjatek `InvalidURL` (z `.cmd`: usage po angielsku - proba C7) |
| 15 | ramke trzyma inny komputer waznym planem (R3): `test-led`, `gniazda --wszystkie`, `gniazda` po kolei, `plytki` | kod 1 z rada "zamknij program Stanowisko"; kod 1 "RAMKA ODMOWILA: kod 409 inny_laptop" bez rady; kod 1, 19 odmow pod rzad i "Ramka zgaszona"; kod 0 (sam odczyt). Plan obcego komputera po 4 probach nietkniety (4 z 4) |
| 16 | podtrzymanie planu (R4): ramka W, `gniazda --wszystkie`, 40 s bez odpowiedzi czlowieka (waznosc planu 30 s) | po 0 s swieci 19 z 19, po 40 s 19 z 19, stan `wynik` |
| 17 | plytka zdjeta w trakcie `gniazda` po kolei (R5) | narzedzie pyta dalej bez ostrzezenia; 2 kolejne gniazda (3 i 4) zapisane "ok", choc plytki na ramce juz nie bylo (wg regul ramki gniazda wtedy nie swieca - pikseli w tej probie nie liczylem); kod 0 |
| 18 | plytka 5 na ramce W -> `gniazda`; `gniazda` bez `--uklad`; `--przesun jeden 0` (R7) | kod 1 "NA RAMCE NIE LEZY PLYTKA TEJ RAMKI (odczyt: 5 ...)"; kod 1 z podpowiedzia; usage po angielsku (kod 2) |
| 19 | uklady w kalibracji domyslnej kopii (R6) | W: `wieczorna`, `wieczorna_r54`; P: `poranna`, `poranna_r54` - okraglych brak (zgodne z dokumentem w.447-448) |
| 20 | `pole_skanu.cmd` z katalogu "Sprzet testy" (spacja), plik "skany z odstepem\skan plytki (1).stl", przez `Polecenie.cmd` instalacji 0.3.1, numer 1 (C2) | kod 0, 6 wierszy numerowanych, 3 pliki wyniku w `Sprzet testy\wyniki\pole_skanu\`; wynik 110,3 mm jak z kopii repo |
| 21 | `pole_skanu.cmd` bez instalacji w `C:\Stanowisko` (C1); bez pliku (C4); numer "abc" (C3) | kod 4 "BLAD: nie ma pliku C:\Stanowisko\Polecenie.cmd - najpierw zainstaluj..."; kod 1 "Przeciagnij plik..."; kod 2 + usage po angielsku |
| 22 | `ramka.cmd 127.0.0.1 1` przy zamknietym porcie (C5); menu z pliku wejsciowego: adres, 1, 4 + uklad + 2 x Enter, 9, 0 (C6) | kod 2 "BRAK POLACZENIA"; menu przechodzi wszystkie pytania, zla cyfra wraca do menu, 0 konczy kodem 0, adres zapamietany w `wyniki\ramka\adres_ramki.txt` |
| 23 | wstrzykniecie M1: prog "cala plytka" `opis - 1.0` -> `opis - 30.0` | 2 failed, 7 passed - test lapie |
| 24 | wstrzykniecie M2: scianka boczna nigdy niewidoczna | 9 passed - test NIE lapie (U9) |
| 25 | wstrzykniecie M3: dolek nigdy "poza skanem" | 4 failed, 5 passed - test lapie |
| 26 | wstrzykniecie M4: `gniazda` bez watku podtrzymania planu | 17 passed - test NIE lapie (U9) |
| 27 | wstrzykniecie M5: bez dopisku "NUMER SPOZA TEJ RAMKI" | 2 failed, 15 passed - test lapie |
| 28 | wstrzykniecie M6: licznik punktow rowka zawsze 0 | 9 passed - test NIE lapie (U9) |
| 29 | po wstrzyknieciach: `git -C rec-s1 status --short` | pusty (6 z 6 cofnietych) |
| 30 | `pole_skanu.py` uruchomiony na kodzie `main` 8001b55 (katalog biezacy `<PC-katalog>\qc\Ramki\stanowisko`, tylko odczyt, wynik do `robocze\rec-s1`): skan wykonawcy plytki okraglej ramkowej nr 3 (pole 100) z numerem i bez; kwadrat nr 1 pelny | 3 z 3 kod 0. Ramkowa: "uklad okragla_ramkowa_wieczorna, pewnie", numer 3 (z dolkow, gdy niepodany), dolki 4 z 4, brzeg 51 z 72 i mimo to "Cala plytka ... jest w skanie", scianka 55 z 72 do 7,8 mm, punktow rowka 19763 / 19751. Kwadrat: punktow rowka 21037 |

Wstrzykniecia: 6, z czego 3 zlapane, 3 niezlapane. Pierwsze podejscie do proby 15 bylo niewazne (moj plan "obcego
komputera" mial blok diod poza plytka i ramka odrzucila go kodem 400) - proba powtorzona z blokiem z kalibracji, wynik
w tabeli pochodzi z powtorki (`p05_cmd.log`). Skanow plytek okraglych ramkowych sam nie generowalem - uzylem 1 skanu
wykonawcy (proba 30). Procesy python: po probach nie zostal zaden moj proces.

### 2a. Zgodnosc dokumentu z programem (28 pozycji)

| Nr | Co w dokumencie (wiersz) | Gdzie sprawdzone | Wynik |
|---|---|---|---|
| 1 | kroki `[1/9] ... [7/9]`, wiersz "INSTALACJA: WSTRZYMANA ... (kod 10)" (w.126-130) | log wykonawcy `inst_1.log` w.13-58 | zgodne (wg logu wykonawcy) |
| 2 | "INSTALACJA: GOTOWA - wersja biezaca ..." (w.144) | `inst_2.log` w.42 | zgodne (wg logu wykonawcy) |
| 3 | wiersze `folder_eksportu_skanera`, `folder_cyrkon`, `operatorzy` (w.137-139) | `ustawienia.przyklad.toml` w.6, 7, 99 | istnieja; `operatorzy` w innej sekcji (U19) |
| 4 | `SAMOKONTROLA: ZIELONA`, ostrzezenia `ramka_wieczorna`, `ramka_poranna`, `excel`, `baza`, `pula` (w.159-160) | `samokontrola.py:225`; `inst_2.log` w.28-34 | zgodne |
| 5 | `Stanowisko.cmd --atrapa` (w.163) | `Stanowisko.cmd` w.2 instalacji; `aplikacja.py:1659` | istnieje |
| 6 | "Kto teraz pracuje?", "Folder skanera: dostepny", "Ramki: W: brak polaczenia" (w.166-167) | `ui/napisy.py:20,21,55`; `ui/napisy_rano.py:141,143` | zgodne |
| 7 | `dzien_skanera.cmd` -> opcje `--ustawienia`, `--dane` (w.193) | `dzien_skanera.py:863,865`; plik `.cmd` | opcje istnieja; okna nie uruchamialem (brak ekranu) |
| 8 | okno: tytul, "Obserwuje:", "Dodaj folder...", "Nie wiem, gdzie skaner zapisuje - szukaj", "Otworz folder sesji", "Zakoncz i spakuj", "Nie udalo sie / pomijam, bo ..." (w.199-216, 243, 297) | `dzien_skanera.py:66,372,140,142,185,183,240` | zgodne; "Zrzut ekranu" = "Zrzut ekranu (za 3 s)" (w.226) |
| 9 | numery krokow okna: 5 pusta plytka, 6 prace cale, 7 to samo, 9 ukruszone, "kroki 6-13" (w.221, 274-280) | `dzien_skanera_kroki.toml`: 14 krokow | zgodne; tytul ostatniego kroku inny (U18) |
| 10 | "SKAN DOBRY: cala plytka, uklad ...; obrys ...", "TEN SKAN SIE NIE NADA, bo na plytce nie widac trzech stozkow znacznikow", "nie widac plaskiego wierzchu plytki" (w.227-229) | `dzien_skanera_rdzen.py:1331,1334,1143,1139,1114` | zgodne |
| 11 | "inna plytka niz w skanie", "TEN SAM plik", "ZROB TAK" (w.283-284) | `dzien_skanera_rdzen.py:1291,1283,1334` | zgodne |
| 12 | "dolki kodu odczytane jako 1 - to nie jest numer plytki tego ukladu (wpisz numer plytki w polu kroku)" (w.288-289); arkusz "numer plytki z dolkow" / "dolki poza polem skanera" | `dzien_skanera_rdzen.py:1155-1159` | zgodne |
| 13 | "Sesja spakowana: ... plikow" (w.299); pomijanie `*_cad.stl` (w.529) | `dzien_skanera.py:787`; `dzien_skanera_rdzen.py:66` | zgodne |
| 14 | przycisk "Pomiar szczegolowy zaznaczonego skanu" nie dziala w 0.3.1 (w.304-305) | `dzien_skanera.py:262` (przycisk istnieje) | awaria: wg wykonawcy, niesprawdzone |
| 15 | "Analiza skanu nie powiodla sie", "Plik nie jest skanem", "Plytka nie z tego trybu", "Podaj numer plytki", "bez projektu", "-> Poranek" (w.322-334) | `statusy.py:334,342,486,489,74`; `ui/napisy_rano.py:12` | zgodne |
| 16 | `[ramki]` `wieczorna_host` / `poranna_host` (w.455-456) | `ustawienia.przyklad.toml` w.91-94 (domyslnie `ramka-w.local`, port 8765) | zgodne |
| 17 | `OK ramka_wieczorna: ramka wieczorna odpowiada`, `OK folder_skanera` (w.457, 317) | `samokontrola.py:1083,476` | zgodne |
| 18 | "Ramki: W: gotowa (plytka 1)", "Test LED" (w.458-459) | `ui/napisy_rano.py:143,145,147` | zgodne |
| 19 | `ramka.cmd` -> 1: "RAMKA ODPOWIADA (... ms): ramka wieczorna (W), program ramki ...", "plytka na ramce: 0" (w.382-383) | proba 13 | zgodne |
| 20 | `ramka.cmd` -> 2: czerwony, zielony, niebieski, bialy, razem 8 s (w.397-398) | `ramka/logika.py:36,555`; `ramka/obraz.py:45` | zgodne |
| 21 | `ramka.cmd` -> 3: "plytka 0 -> 2", plik `plytki_<data>_<godzina>.csv`, "NUMER SPOZA TEJ RAMKI" (w.407-408, 426) | `ramka_proba.py:121,176-177`; test paczki | zgodne |
| 22 | `ramka.cmd` -> 4 / 5: pytania o uklad i przesuniecia, "NA RAMCE NIE LEZY PLYTKA TEJ RAMKI", 1 dioda = 2,5 mm (w.434-443) | proby 18, 22; `ramka/kalibracja.py:10` | zgodne |
| 23 | `ramka.cmd` -> 6: "Enter: kuweta potwierdzona 1111", "rodzaje: 5 z 5" (w.478-479) | `ramka_proba.py:283-285,342`; test paczki | zgodne |
| 24 | niebieski pierscien = ramka gotowa (w.366); napis numer + "BRAK" (w.411) | `ramka/obraz.py:35`; `ramka/logika.py:572` | zgodne |
| 25 | `findstr ... C:\Stanowisko\dane\logi\stanowisko.log` (w.492) | plik `dane\logi\stanowisko.log` jest w instalacji; wzorce: `aplikacja.py:998`, `silnik.py:1430,1597,1688,1745-1750` | istnieja; liczba 0 przy zwyklej pracy: wg wykonawcy, niesprawdzone |
| 26 | `C:\Stanowisko\dane\wyniki`, `dane\logi`, `dziennik_instalacji.txt`, `Wersje.cmd /usun` (w.515-516, 535) | `ustawienia.przyklad.toml` w.12, 15; katalog instalacji | zgodne; `dane\wyniki` powstaje dopiero po pierwszym wyniku (w instalacji probnej go nie ma) |
| 27 | Zalacznik A: `--rola W --sprzet rpi --host 0.0.0.0`, `/opt/ramka/ramka`, `apt install python3-gpiozero python3-evdev`, `isolcpus=3`, README punkty 5 i 6 (w.593-609) | `ramka/program.py:331-333` (host domyslny 127.0.0.1); `ramka/README.md` w.397-410 | zgodne z README; na Raspberry Pi nic nie uruchomiono (oznaczone) |
| 28 | w paczce nie ma `uruchom_dzien_skanera.bat` (w.195-196); jest `program\instrukcje\instalacja_i_aktualizacja.md` (w.81) | `wersje\0.3.1\program\` instalacji | zgodne |

## 3. Kryteria zlecenia

### 3a. Wymaganie wlasciciela -> miejsce w dokumencie -> ocena

| Punkt wymagania | Gdzie | Ocena |
|---|---|---|
| jeden dokument w `Ramki/etap3/`, prosty jezyk, do wydruku | `testy_sprzet_2026-11-28/PIERWSZE_TESTY_NA_SPRZECIE.md` | czesciowo: jeden dokument - tak; prosty jezyk - w krokach tak, w akapitach "Stan:" nie (1b); do wydruku - za dlugi (1a) i w formie `.md` (U20) |
| to, czego potrzebuje w rece | `narzedzia/` (3 pliki `.cmd`, 2 skrypty), arkusz | spelnione na 0.3.1; klucz ramki i skrot O4 - etap 2 |
| podstawa: `ODLOZONE.md` (T15, T16, sprawy laptopa) | czesc 3 (T15), czesc 2 (T16), czesc 4 (sprawy 4-6) | spelnione; sprawa 4 swiadomie odlozona (w.502-503) |
| podstawa: sekcja 6 planu plytek okraglych | 2.4 (pole, dolki, scianka, rowek), 3.5-3.6 (odczyt numeru, plytka na zebrze), 3.7 (diody pod wkladka) | spelnione co do zakresu; pomiar pola i rowka z zastrzezeniami U1-U3 |
| co przygotowac i zabrac | sekcja 1 (w.68-91), 14 pozycji do odhaczenia | spelnione; wydruki wskazane sciezkami repo (U20) |
| w jakiej kolejnosci (jedna ramka; skaner; laptop albo PC) | sekcja 2 (w.95-104), czesci 1-5, zasady 3 i 4 (w.21-23) | spelnione: czesci 2 i 3 niezalezne, jedna ramka wystarcza, czesc 4 tylko na laptopie |
| co zmierzyc: pole skanera | krok 2.4, arkusz 2.4 | czesciowo - liczba prawdziwa tylko dla pola kolowego (U1), zdanie o calej plytce (U2) |
| co zmierzyc: dolki numeru | krok 2.4 wiersz 4, 2.5 punkt 3, arkusz | spelnione (proby 2, 3, 12, 30); dwa podwiersze (U12) |
| co zmierzyc: rowek pokrywki | krok 2.4 wiersz 6 | NIE - licznik nie odroznia rowka (U3) |
| co zmierzyc: odczyt numeru plytki przez ramke | kroki 3.5, 3.6, arkusz tabela 3.5 | spelnione na atrapie (test paczki, proba 15) |
| co zmierzyc: kalibracja gniazdo -> diody | krok 3.7, arkusz 3.7 | czesciowo: obserwacja i zapis przesuniecia; narzedzia zapisu kalibracji nie ma (powiedziane wprost, w.449) |
| jakie pliki przywiezc i gdzie polozyc | czesc 5 (w.509-535), `<PC-katalog>\sprzet_2026-11-28\` z 5 podfolderami | czesciowo - brak skanow z krokow 2.7 / 3.8 (U6) |
| po czym poznac, ze krok sie udal | "Udalo sie, gdy" w 19 z 20 krokow | spelnione |
| arkusz obserwacji | `ARKUSZ_OBSERWACJI.md`, 158 wierszy, numery jak kroki | czesciowo - U8, U17 |
| narzedzia sprawdzone na atrapach i na instalacji z nowej paczki | raport wykonawcy tabela 2; moje proby 1-30 | atrapy i instalacja 0.3.1 - tak; nowa paczka - etap 2 (swiadomie) |
| wszystko niesprawdzone oznaczone wprost | 19 znacznikow + lista zbiorcza 17 pozycji | spelnione z 2 brakami (U21) i 1 brakiem tresci (U5) |
| pytania na poczatku, bez zgadywania | sekcja 0, P1-P7, kazde z "od odpowiedzi zalezy krok ..." | spelnione co do tresci (ramka i wkladka P1, plytki i magnesy P2, komputer P4 + P3, P5, P6, P7); brak terminu i adresata (U7) |

### 3b. Kryteria zlecenia `s1.md`

| Kryterium | Stan |
|---|---|
| A1 program ramki na atrapie, wymagania RPi, luka instrukcji | potwierdzone przegladem (raport wykonawcy + kod `ramka/`); atrapa: wlasna proba 13-19 |
| A2 "Dzien skanera" z instalacji, gdzie zapisuje | potwierdzone przegladem (`dzien_skanera.cmd`, opcje `--dane`); przebieg okna: wg wykonawcy, niesprawdzone (brak ekranu) |
| A3 instalacja probna | potwierdzone przegladem (logi `inst_1.log`, `inst_2.log`, katalog `t0\s1\Stanowisko`) |
| A4 obserwator + symulator, komunikaty | potwierdzone przegladem (napisy w kodzie - tabela 2a poz. 15); liczby: wg wykonawcy |
| A5 liczby pola skanera + narzedzie + test | potwierdzone wlasna proba dla pola kolowego (proba 2: 3 z 3); z zastrzezeniami U1-U5, U9 |
| B0 pytania na poczatku | potwierdzone przegladem; U7 |
| B1 co przygotowac | potwierdzone przegladem |
| B2 kolejnosc, kazdy krok: co / ile trwa / sukces / porazka / arkusz | potwierdzone przegladem (20 krokow, 19 "Udalo sie", 22 "Gdy", 19 "Arkusz") |
| B3 co zmierzyc | czesciowo - U1, U3, U8 |
| B4 pliki z powrotem | czesciowo - U6 |
| B5 znaczniki + lista zbiorcza | potwierdzone przegladem; U21 |
| styl: ASCII, LF, bez szerokich tabel, polecenia w ramkach | potwierdzone wlasna proba (sekcja 4); dlugosc i jezyk - U22 |
| zakaz zmian w programie | potwierdzone wlasna proba (`git diff --name-status`: 11 x A, wszystkie w zakresie) |
| higiena T13 | wg wykonawcy, niesprawdzone |

## 4. Zakres plikow i zasady

- Zakres: `git diff --name-status main...e3/sprzet` = 11 plikow dodanych: 10 w `Ramki/etap3/testy_sprzet_2026-11-28/`
  i raport `Ramki/stanowisko/raporty/E3-S1_2026-11-21.md`. Zmian w programie, testach programu, instrukcjach,
  `modele_plytek`, `odbior_koncowy`, `t14`: 0.
- ASCII: 0 znakow spoza ASCII w 11 plikach. Konce wierszy (`git ls-files --eol`): 3 pliki `.cmd` CRLF, pozostale 8 LF.
- Rozmiar: katalog paczki 109 kB lacznie; zadnych skanow, ZIP-ow ani obrazow.
- Dane osobowe: brak nazwisk, adresow, nazw zlecen; w dokumencie zasada "TEST1, TEST2" (w.20) i ostrzezenie przed
  przywozeniem folderu projektow (w.528-530). `pole_skanu` wpisuje do wynikow nazwe pliku skanu - gdy program skanera
  nazwie plik nazwiskiem, trafi ono do `wyniki\pole_skanu` (zasada w.20 to pokrywa; warto powtorzyc w kroku 2.4).
- Co narzedzia zapisuja: `pole_skanu` - tylko `..\wyniki\pole_skanu\` (albo `--wynik` / obok skanu); `ramka_proba` -
  tylko pliki CSV i `adres_ramki.txt` w `..\wyniki\ramka\`; `dzien_skanera.cmd` - zaklada
  `<instalacja>\dane\dzien_skanera`. Instalacji, ustawien i bazy zadne narzedzie nie zmienia (przeglad kodu + proby 20-22).
  Do ramki `ramka_proba` wysyla `PUT /plan`, `PUT /tryb test_led`, `DELETE /plan` pod wlasnym identyfikatorem;
  planu innego komputera nie rusza (proba 15: 4 z 4).
- Kopia `rec-s1` po probach: `git status --short` pusty.

## 5. Do decyzji wlasciciela

1. Kto i do kiedy przygotuje karte SD z programem ramki (pytanie P3)? Bez tego czesc 3 konczy sie na kroku 3.1.
   Propozycja: odpowiedzi na P1, P3, P6 do koordynatora najpozniej 25.11.
2. Ramka z kluczem czy bez na dzien testow? Skrypt z paczki O4 wstawia losowy klucz; wtedy klucz trzeba przepisac do
   `ustawienia.toml` na komputerze. Propozycja domyslna: z kluczem, a `ramka.cmd` czyta go z ustawien.
3. Dokument w jednym kawalku (ok. 12 stron) czy "skrot dnia" + 4 karty + zalacznik (propozycja 1a)?
4. Czy narzedzia dnia sprzetu maja wejsc do paczki wydania, czy zostac na pendrivie (w.183)?
5. Folder odbioru `<PC-katalog>\sprzet_2026-11-28\` - czy wlasciciel kopiuje tam sam (konto z prawem zapisu), czy
   zostawia pendrive koordynatorowi.

## 6. Lista zadan dla etapu 2

Kolejnosc = waga. "(zmiana a / b / c)" = wynika z tego, co zmienilo sie po szkicu (O1 scalona, O4 i O2 / O3 w toku) -
to nie jest blad szkicu.

### Najpierw - bez tego dokument nie powinien trafic do wlasciciela

1. **Plytki okragle po O1 (zmiana a).** Przepisac: P2 (w.36-40), krok 2.5 akapit "Stan" (w.286-293), lista etapu 2
   poz. 2. Nazwy `okragla_ramkowa_wieczorna` / `okragla_ramkowa_poranna` tylko w zalaczniku; w krokach "plytka okragla
   ramkowa". Dodac pomiar znanego ograniczenia (plytka okragla bez czytelnych dolkow i bez scianki bocznej w skanie =
   kwadrat, "pewny"): w kroku 2.5 trzy skany kazdej plytki okraglej - (i) pusta, (ii) z praca w gniezdzie obok dolkow,
   (iii) z dolkami zaklejonymi kawalkiem tasmy - i dla kazdego wpis "program mowi: kwadratowa / okragla; pewnie /
   niepewnie" (z okna i z wiersza 1 `pole_skanu`). To jest dana do decyzji o wariancie C
   (`Ramki/etap3/propozycja_wariant_C_regula_ksztaltu_2026-11-21.md`). Arkusz: U8.
2. **`pole_skanu`: U1, U2, U3** (pole nie-kolowe, "cala plytka", rowek) + testy z U9 (a). Sprawdzone przeze mnie na
   kodzie `main`: narzedzie dziala z ukladami O1 (proba 30), ale mapowanie drugiego ksztaltu (`pole_skanu.py:201`) dla
   `okragla_ramkowa_*` nie znajduje pary - poprawic albo usunac (U12).
3. **Klucz ramki (zmiana b).** Po instalacji skryptem O4 (`ramka/rpi/zainstaluj_ramke.sh`, wzor `ramka.json.wzor` z
   kluczem) kazda pozycja menu `ramka.cmd` skonczy sie "BRAK POLACZENIA ... podaj --klucz" (proba 13), a menu klucza
   nie przyjmuje. Zrobic: `ramka.cmd` czyta `klucz` i `port` z `[ramki]` w `<instalacja>\ustawienia.toml`; krok 3.3 /
   3.8: skad wziac klucz i gdzie go wpisac; w.59 "Ramka nie ma hasla" poprawic; komunikat 401 (U13); test z kluczem.
4. **Zalacznik A -> instrukcja O4 (zmiana b).** Zastapic w.585-613 odwolaniem do `instrukcje/ramka_raspberry_pi.md`
   i skryptow `ramka/rpi/` (`zainstaluj_ramke.sh`, `ramka.service`, `sprawdz_ramke.sh`); P3 (w.42-46), krok 3.2
   (w.368-369), lista niesprawdzonych poz. 8 i lista etapu 2 poz. 8 dopasowac; do sekcji 1 dopisac, co zabrac do
   przygotowania karty SD (czytnik kart, kto to robi i kiedy - U7).
5. **"Dzien skanera" (zmiana b).** Krok 2.1: `C:\Stanowisko\Dzien_skanera.cmd` zamiast `narzedzia\dzien_skanera.cmd`;
   usunac uwage w.195-197 i w.532-535; potwierdzic proba, ze sesje sa w `<instalacja>\dane\dzien_skanera\`;
   `narzedzia/dzien_skanera.cmd` usunac (dwa skroty do tego samego okna = dwa miejsca na pomylke). Przycisk "Pomiar
   szczegolowy" (w.304-305) i `Polecenie.cmd narzedzia\pomiar_skanu\pomiar_skanu.py` sprawdzic na nowej instalacji.
6. **Pytania z terminem i adresatem** (U7).
7. **Czesc 5 i arkusz: skany z krokow 2.7 / 3.8 i `ustawienia.toml`** (U6).
8. **Skan ze stolikiem** (U5): krok, pozycja listy niesprawdzonych, pole w arkuszu; zgloszenie dla programu.
9. **Nadpisywanie wynikow `pole_skanu`** (U4).

### Potem - poprawki tresci zalezne od nowego wydania

10. **O2 / O3 (zmiana c).** Krok 3.6 (w.428-430): nowy komunikat o numerze plytki niezgodnym z ramka - doslowny tekst
    i gdzie go widac; krok 3.7 (w.435-436, 445-448) i `ramka.cmd:63`: uklady okragle w kalibracji z geometrii - lista
    ukladow w menu pobierana z kalibracji, nie wpisana na sztywno (U16); krok 3.8 (w.465-466): "ramka ciemna dla
    plytki okraglej" przestaje byc normalne; krok 2.7: opis mapy okraglej ze scieciem.
11. **Powtorzenie prob na instalacji z nowej paczki:** 26 testow narzedzi po `git merge main` (uwaga:
    `test_gniazda_bez_plytki_i_zly_uklad` zaklada, ze ukladu `okragla_wieczorna` NIE MA w kalibracji - po O2 moze
    pasc; liczba ukladow 8 -> 10), 3 pliki `.cmd` przez `Polecenie.cmd` nowej instalacji, `ramka.cmd` na atrapie z
    kluczem. Na prawdziwym ekranie: dwuklik, przeciaganie pliku na `pole_skanu.cmd`, menu `ramka.cmd` z klawiatury,
    "Zrzut ekranu" (U21).
12. **Liczby i nazwy nowego wydania:** nazwa paczki (w.72, w.124), kroki i czasy instalatora (w.126-127, w.142),
    "ok 14, ostrzezenia 7" (w.174), "zna 8 ukladow" (w.286), czy `Stanowisko.cmd` / `Samokontrola.cmd` / `Polecenie.cmd`
    + `Dzien_skanera.cmd` sa w `C:\Stanowisko` (w.144-145).
13. **Sprawa 4 laptopa** (w.502-503) - gotowe polecenie albo usunac z dokumentu.
14. **Czy narzedzia wchodza do paczki** (w.183) - po decyzji 4 z sekcji 5.

### Na koniec - forma

15. **Skrocenie do ok. 9 stron i podzial na karty** (1a, punkty 1-7); PDF albo HTML do druku (U20).
16. **Jezyk** (1b): 19 cytatow + slownik ("uklad" -> "rodzaj plytki").
17. **Arkusz:** U8, U17, pole P7, pola "w skanie widac stolik", "pole: najwezej / najszerzej", wiersz na skany 2.7.
18. **Drobne w narzedziach:** U10, U11, U14, U15, U16; brakujace testy U9 (b), (c).
19. **Drobne w dokumencie:** U18 (nazwy przyciskow i krokow okna, w ktorym kroku okna robic skany dodatkowych
    plytek), U19 (Notatnik), w kroku 3.5 dopisac, jak skonczyc obserwacje przed uplywem 5 minut.
