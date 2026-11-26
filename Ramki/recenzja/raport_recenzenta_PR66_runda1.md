# Raport recenzenta - paczka E3-D1 (dokument dnia testu 28.11, laptop i skaner), PR #66, runda 1

- Data: 26.11.2026 (04:15-05:00), recenzent: konto 3 na PC (zlecenie `rec-d1-r1`), tor ciezkich krokow 4.
- Zakres: commity `origin/e3/r1..origin/e3/d1` (82f68aa..90ad932, 4 commity, 6 plikow) oraz pliki w
  `<PC-katalog>\konto3\DLA_WLASCICIELA_2026-11-28\` (2 x PDF, 2 x HTML, CZYTAJ.txt).
- Miara: `<PC-katalog>\konto3\zlecenia\d1.md` i `WARIANT_LAPTOP_I_SKANER.md` (galaz `analiza/plan`), p. "Kolejnosc dnia".
- Metoda: dokument czytany jak wlasciciel (bez terminala, pendrive z paczka, laptop bez Pythona). Wlasna instalacja probna
  z paczki `<PC-katalog>\wydania\Stanowisko_0.3.9-rc2.zip` do `<PC-katalog>\konto3\robocze\rec-d1-r1\proba` Z OKNA
  instalatora (Qt offscreen, Python z paczki, PATH bez Pythona), potem prawdziwy start programu i 3 uruchomienia okna
  "Dzien skanera" z ustawien tej instalacji - wszystko jednym procesem odlaczonym z przynety
  `robocze\rec-d1-r1\przyneta\proba.cmd` przez `ciezki.ps1 -Tor 4` (04:23:05-04:35:42). Napisy odczytane z drzewa
  widzetow (JSON + PNG w `robocze\rec-d1-r1\logi\`), skrypty w `robocze\rec-d1-r1\skrypty\`. Kod programu nie byl
  w zakresie - czytany tylko po to, zeby sprawdzic zdania dokumentu. Raport wykonawcy przeczytany na koncu.
- Uruchomiono: instalacja z okna (1 przebieg), program "Stanowisko" 2 starty, okno "Dzien skanera" 3 starty, QtPdf na
  2 plikach PDF, porownanie HTML z MD, T13 (wlasne uruchomienie), kontrola ASCII / LF, wyszukiwanie danych osobowych.

## 0. Werdykt

**Do scalenia po poprawkach.** B 0 / P 5 / D 9.

Czesc A (instalacja, pierwszy start, okno "Dzien skanera") przeszla na mojej instalacji krok po kroku zgodnie
z dokumentem: kazdy napis czesci A zgadza sie z ekranem (poza konwencja ASCII, D1), instalacja z okna kod 0 w 64,1 s.
Poprawki dotycza czesci B-C: odeslan do materialow, ktorych wlasciciel nie bedzie mial (P1, P2), instrukcji sprzecznej
z komunikatem programu (P3), danych, ktore okno "Dzien skanera" ma za wymagane, a dokument pomija (P4), i braku planu,
gdy prawdziwy skan nie da mapy do pokazu (P5).

## 1. Uwagi

Plik `DZIEN` = `Ramki/etap3/testy_sprzet_2026-11-28/DZIEN_TESTU_LAPTOP_I_SKANER.md`, `ARKUSZ` = `ARKUSZ_LAPTOP_I_SKANER.md`
tego katalogu, `CZYTAJ` = `<PC-katalog>\konto3\DLA_WLASCICIELA_2026-11-28\CZYTAJ.txt`.

| Nr | Waga | Plik:linia | Scenariusz | Propozycja |
|---|---|---|---|---|
| 1 | P | DZIEN:19-20 (A2), CZYTAJ:1-3 | A2 kaze miec na pendrivie folder `testy_sprzet_2026-11-28` i skopiowac go jako `C:\Sprzet_testy` (narzedzie `pole_skanu.cmd` do 2.4 / 2.5a, D2 przywozi `C:\Sprzet_testy\wyniki`). Wlasciciel nie ma skad go wziac: w ZIP paczki 0 plikow tego folderu (`unzip -l`), w `DLA_WLASCICIELA_2026-11-28` go nie ma, w kopii wlasciciela `<PC>\Desktop\Ramki` (przeszukane 3 poziomy) tez nie; CZYTAJ.txt o nim milczy. Krok nie do wykonania bez wiedzy spoza dokumentu. | Polozyc kopie folderu (z `narzedzia/`) w `DLA_WLASCICIELA_2026-11-28\testy_sprzet_2026-11-28\` i dopisac jedno zdanie w CZYTAJ.txt i w A2 ("lezy obok PDF-ow"). |
| 2 | P | DZIEN:68-69 (B2), 76-77 (B3), 4; CZYTAJ:1 | B2 przy skanie z podlozem odsyla do "stary dokument, krok 2.3", a 2.4 i 2.5a robi "tylko gdy jest czas" bez opisu (opis jest tylko w `PIERWSZE_TESTY_NA_SPRZECIE.md`). CZYTAJ.txt kaze drukowac wylacznie 2 nowe PDF-y, wiec w sobote wlasciciel starego dokumentu nie ma: nie zrobi procedury A/B skanow z podlozem ani krokow 2.4 / 2.5a. Do tego miara (`WARIANT...`, "Kolejnosc dnia" p. 2 i 3) wlicza 2.4 i 2.5a do dnia, a stary dokument stawia je wsrod 5 najwazniejszych wynikow (2.4 - wymiar pola, 2.5a - czy program poznaje plytke okragla; plytka glowna nr 8 JEST okragla). Wykonawca przyjal "opcjonalne" domyslnie (raport, "Przyjete domyslnie"), bez decyzji wlasciciela. | Albo dopisac w B2 / B3 po 2-3 zdania procedury (skany A i B z podlozem; 2.4 karton + `pole_skanu.cmd`; 2.5a trzy skany nr 8, numer = sam Enter), albo dopisac do CZYTAJ.txt druk stron 2.3-2.5a starego dokumentu. Opcjonalnosc 2.4 / 2.5a - do decyzji wlasciciela (sekcja 5), w dokumencie wprost. |
| 3 | P | DZIEN:95 (B4, tabela) | Wiersz "Ten sam projekt w dwoch gniazdach" -> "dwie prace z jednego pliku STL - to nie blad; 'Zamknij'". Program mowi co innego: tresc komunikatu to "Ten sam projekt pasuje do {miejsc} prac - sprawdz, ktora praca jest ktora." (`statusy.py:399-400` w paczce). Gdy na plytce leza dwie ROZNE prace (np. brak STL jednej z nich w `C:\Projekty_STL`), komunikat oznacza pomylke rozpoznania - wlasciciel, idac za dokumentem, uzna to za "nie blad", zamknie i nie zapisze wyniku, ktory jest wlasnie przedmiotem dnia. | "Sprawdz, czy to naprawde dwie prace z jednego pliku STL. Jesli nie - zapisz oba gniazda w arkuszu (pomylka rozpoznania), potem 'Zamknij'." |
| 4 | P | DZIEN:65-77 (B2, B3); ARKUSZ:28-37 | Kroki okna "Dzien skanera" maja pola wymagane, ktorych dokument nie wymienia: krok 5 "Numer plytki *", krok 6 "Wspolczynnik z etykiety bloku", krok 9 "Gniazda z pracami ukruszonymi i miejsce ukruszenia", krok 11 "W ktorych gniazdach leza prace" (moja proba: lista brakow w `paczka.json` sesji i w okienku "Brakuje wymaganych krokow"). Dokument kaze tylko "ocena i notatka do arkusza B3", a w B6 "Spakowac teraz? - Tak" mimo brakow; arkusz nie ma miejsca na wspolczynnik bloku. Skutek: paczka ZIP bez numeru plytki, wspolczynnika i gniazd - danych, z ktorych "sesja odczyta potem liczby" (D2). | W B2 / B3 jedno zdanie: "w kazdym kroku okna wpisz pola z gwiazdka: numer plytki (8), wspolczynnik z etykiety bloku, gniazda prac / ukruszen"; w arkuszu B3 kolumna "wspolczynnik". |
| 5 | P | DZIEN:117-136 (C) | Caly pokaz (C1 "skan z naszego skanera", C2 "kliknij czerwone gniazdo", C4 lista po "Ukruszona") wymaga, by w B4-B5 prawdziwy skan plytki nr 8 dal mape z co najmniej jedna praca czerwona. To stoi na rzeczach [NIE SPRAWDZONE BEZ SPRZETU] (B2: stolik w skanie; B4: odczyt numeru, kolory), a stary dokument nazywa skan z podlozem "najwiekszym ryzykiem dnia" (wtedy KAZDY skan jest czerwony / analiza nie powiodla sie - tak wyszlo tez na moim pliku probnym). Gdy tak sie stanie, dokument milczy, co pokazac szefowi - wlasciciel zostaje przed szefem bez planu. | Dopisac w C 2-3 zdania "gdy w B4 nie bylo mapy plytki 8 albo zadnej pracy czerwonej": pokaz kafelek z komunikatem i jego powodem (program mowi, co jest nie tak ze skanem), pasek stanu, przelaczenie Poranek; powiedz wprost, ze dzis zbieramy prawdziwe skany, a wynik bedzie po analizie paczki. |
| 6 | D | DZIEN:6-7, 22, 67 | Konwencja mowi tylko o polskich literach, a ekran ma tez pauze, wielokropek i cudzyslowy drukarskie (tytul okna instalatora z pauza U+2014, przycisk "Wybierz" z wielokropkiem U+2026, nazwa programu w cudzyslowie U+201E / U+201D). Zielona ocena na ekranie to "SKAN DOBRY: ..." (etykieta) / "Skan dobry" (tabela); dokument cytuje "skan dobry" za instrukcja kroku 1 okna. Wlasciciel sie nie pomyli, ale zasada "slowo w slowo" jest szersza, niz mowi naglowek. | W drugim akapicie: "pauza, wielokropek i cudzyslowy na ekranie wygladaja inaczej"; w B2 "SKAN DOBRY: ...". |
| 7 | D | DZIEN:59-60, 109, 112, 115 | Przyciski okienek "Dnia skanera" sprawdzilem na instalacji PC: "Tak" / "Nie" (polskie tlumaczenie Qt z paczki, wiec na laptopie tak samo); domyslny: "Tak" przy "Niedokonczona sesja", "Nie" przy "Brakuje wymaganych krokow" (zgodnie z "sam Enter znaczy NIE"). Znacznik "[NIE SPRAWDZONE BEZ SPRZETU: napisy przyciskow Yes / No]" i warianty *No* / *Yes* sa zbedne. | Pisac "Nie" / "Tak" i zdjac te czesc znacznika z B6 (czas pakowania zostaje). |
| 8 | D | DZIEN:19 (A2) | Wlasciciel ma na pendrivie ZIP; dokument mowi "rozpakowana paczka", ale nie jak. Wejscie w ZIP i dwuklik `Instaluj.cmd` z podgladu archiwum konczy sie komunikatem z samego `Instaluj.cmd` ("rozpakuj CALA paczke (prawy klawisz - 'Wyodrebnij wszystkie')"), wiec sciezka bledu jest opisana przez program. | W A2: "prawy klawisz na ZIP -> Wyodrebnij wszystkie -> pendrive (kilka minut)". |
| 9 | D | DZIEN:30 (A3, wiersz 3) | Po bledzie instalacji "Sprobuj ponownie" wraca do kroku 1 "Wskaz foldery" (`okno_instalatora._ponow`), trzeba znow "Dalej" i "Instaluj" - dokument tego nie mowi. | "...'Sprobuj ponownie' (wraca na poczatek: 'Dalej', 'Instaluj')". |
| 10 | D | DZIEN:84 (B4) | Stoper dla "nowej plytki nr 8" jest wlaczany, gdy program moze jeszcze liczyc zalegle skany z B2-B3 - zmierzony czas obejmie kolejke. | "Zanim zapiszesz nowy skan, poczekaj, az pasek pokaze 'Analiza:' 'nic nie czeka'". |
| 11 | D | DZIEN:112-114 (B6), 143 (D2) | Po spakowaniu okno samo pokazuje okienko "Sesja spakowana" i otwiera Eksplorator na folderze `paczka` (`dzien_skanera._po_spakowaniu`, `_otworz_folder`) - na PC wlasnie otwieranie przez powloke wywolywalo reakcje programu ochronnego. ZIP zawiera kazdy skan dwa razy (krok skanu + kopia folderu w kroku 14; moja proba: ten sam plik w `k05_pusta` i `k14_kopia_folderu`), a D2 kaze przywiezc jeszcze caly `C:\Skany_test` - przy prawdziwych skanach to moga byc GB; o pojemnosci pendrive'a dokument milczy. | B6: "po spakowaniu okno samo otworzy folder z ZIP"; D2: "pendrive co najmniej ... GB". |
| 12 | D | DZIEN:15, 36 (A1, A4) | Okno instalatora mowi przy folderze projektow "Pliki STL z exocad, w podfolderach zlecen", a dokument kaze wrzucic pliki luzem - dziala (moja proba: 3 pliki luzem -> pasek "plikow projektow: 3"), ale wlasciciel moze sie zawahac. A4 przy "0 plikow" kaze tylko zrobic zdjecie, choc dzien wczesniej da sie to naprawic (skopiowac STL, przycisk "Odswiez pule" na pasku). | A1: "okno mowi o podfolderach - pliki luzem tez sa dobre"; A4: "0 plikow: skopiuj STL do `C:\Projekty_STL`, kliknij 'Odswiez pule'". |
| 13 | D | ARKUSZ:3, 65-69; DZIEN:3 | Arkusz str. 2: "Uwagi / co poszlo inaczej" (wg arkusza "najcenniejsze") ma 3 linie na pol szerokosci, a pol strony jest puste. Oba dokumenty odsylaja do plikow `.md`, wlasciciel ma wydruk PDF. | Wydluzyc linie uwag do konca strony; nazwy bez `.md` ("arkusz", "dokument dnia"). |
| 14 | D | DZIEN:12-20 (A), 15 | Miara (`WARIANT...`, "Co przygotowac") wymienia: tylko `*_cad.stl`, 2-3 prace celowo ukruszone z kartka, tasma / plastelina, pendrive, plytki; dokument nie ma listy "na sobote przygotuj", a A1 mowi ogolnie "pliki STL z exocad" (w folderach exocad sa tez inne STL, ktore trafilyby do puli). | W A jedna linia "Na sobote przygotuj: ..."; w A1 "tylko pliki konczace sie na `_cad.stl`". |

## 2. Wlasne proby

| # | Polecenie / proba | Wynik |
|---|---|---|
| 1 | `sha256sum Stanowisko_0.3.9-rc2.zip`, `unzip -l` | ee72ec0b...18ada6 = plik `.sha256`; 1595 plikow, 556 975 956 B po rozpakowaniu; w korzeniu `Instaluj.cmd`, `zainstaluj.cmd`, `CZYTAJ.txt`, `SHA256SUMS`, `wydanie.json` + 5 folderow |
| 2 | `Instaluj.cmd` (odczyt) | `start "" python\pythonw.exe ... okno_instalatora.py` i `exit` - konsola znika od razu ("Mignie czarne okno" - zgodne); bez plikow paczki: komunikat "rozpakuj CALA paczke ... Wyodrebnij wszystkie" + `pause` |
| 3 | `rec_okno.py` (Python paczki `-I -B`, `QT_QPA_PLATFORM=offscreen`, PATH bez Pythona): klikniecia jak w A3 tabeli, w tym 3 sciezki bledu | 10 stanow okna zapisanych; "Dalej" bez folderu -> "Wskaz folder ze skanami."; folder nieistniejacy -> "Folder ze skanami nie istnieje: ... Wybierz istniejacy folder przyciskiem 'Wybierz...'."; "Instaluj" bez osoby -> "Dodaj co najmniej jedna osobe."; "Potrzeba 1,9 GB wolnego miejsca. Jest 67,6 GB."; instalacja **kod 0, 64,1 s** (krok 5 od 4,0 do 58,4 s, "trwa... 0:02" z rosnacym czasem), 9 z 9 wierszy "gotowe"; strona "Gotowe": opis wersji i katalogu, "Na pulpicie sa ikony: 'Stanowisko', 'Dzien skanera'.", "Ramki sa wylaczone - ..."; przyciski "Uruchom program", "Otworz 'Dzien skanera'", "Zamknij"; skroty 2 z 2 (`Stanowisko.lnk`, `Dzien skanera.lnk`) |
| 4 | `rec_program.py start1` - prawdziwy start z `ustawienia.toml` instalacji, odczyty po 3/8/15/20/30 s, klik "Tester" po 16 s | 46 napisow; tryb "Wieczor" zaznaczony (PNG); po prawej "Kto teraz pracuje?" + "Tester"; po lewej "Jeszcze nie ma skanow."; pasek: "Folder skanera:" "dostepny", "Analiza:" "nic nie czeka", "Folder projektow:" "plikow projektow: 3", "Ramki:" "wylaczone", "wersja 0.3.9-rc2"; po kliknieciu: "Tester", "Zmien"; kod 0 |
| 5 | `rec_dzien.py pierwszy` | tytul "Dzien skanera - krok po kroku (sesja 2026-11-26_0424)"; "Obserwuje:" + folder skanow; 14 krokow, pierwszy "1. Zanim zaczniesz"; kod 0 |
| 6 | `rec_dzien.py drugi` (+ model `okragla_wieczorna_r54/plytka_n8.stl` wrzucony do folderu skanow na kroku 5) | okienko "Niedokonczona sesja": "Znaleziono niedokonczona sesje z 2026-11-26T04:24:41 (0 plikow). ... Wznowic ja? (Tak = ...; Nie = ...)", przyciski "Tak" / "Nie", domyslny "Tak"; "Nie" -> nowa sesja `_2`; plik skopiowany po 1 s, ocena po ok. 4 s: "TEN SKAN SIE NIE NADA, bo na plytce nie widac trzech stozkow znacznikow (znaleziono 0). ZROB TAK: ..." (model CAD, nie skan - wynik oczekiwany, rzeczywistej oceny nie da sie tu sprawdzic) |
| 7 | `rec_program.py start2` (proba f: plik z p. 6 zapisany przy zamknietym programie), odczyty do 170 s | plik wziety sam; kafelek "Plytka bez numeru" "analiza nie powiodla sie"; strefa: "Plytka bez numeru - skan z 04:25: Analiza skanu nie powiodla sie" + przycisk "i jeszcze 1"; tresc "Program nie przeanalizowal tego skanu (w skanie widac 0 z 3 znacznikow plytki - ... albo w skanie jest stolik (podloze) ...)"; osoba znow do wyboru po restarcie |
| 8 | `rec_dzien.py trzeci` | "Niedokonczona sesja" (1 plikow) -> "Tak" -> ta sama sesja `_2`; krok 14: przycisk "Skopiuj caly folder zlecen skanera" -> "Skopiowano 1 z 1 plikow"; "Zakoncz i spakuj" -> "Brakuje wymaganych krokow" ("... Spakowac teraz?"), przyciski "Tak" / "Nie", domyslny **"Nie"**; "Tak" -> ZIP `dane\dzien_skanera\2026-11-26_0424_2\paczka\dzien_skanera_2026-11-26_0424_2.zip` (585 035 B, 9 plikow, ten sam skan 2 razy); potem modalne okienko "Sesja spakowana" - moj skrypt go nie obslugiwal (po nim program otwiera Eksplorator); proces zatrzymalem sam po 7 min (kod -1 w przebiegu), ZIP byl juz gotowy (04:28) |
| 9 | program ochronny | przynety 2 z 2 na miejscu; kwarantanna Bitdefendera: 0 nowych wpisow od 04:20 (ostatni 25.11 20:59) |
| 10 | `pdf_png.py` (QtPdf) na 2 PDF | DZIEN 3 strony, ARKUSZ 2 strony, kazda 595 x 842 pt (A4); obraz stron obejrzany: czytelne (ok. 10 pt), tabela A3 i B4 sie mieszcza; arkusz - patrz uwaga 13 |
| 11 | HTML vs MD (sekwencja slow) | zgodne (HTML dodaje tylko tytul i numeracje listy C); PDF metadane: tytul, Chrome/Skia - bez nazw osob i kont |
| 12 | `cytaty.py` + `bilans.py` - kazdy cytat "..." dokumentu wobec zrzutow mojej instalacji i plikow napisow paczki (po sprowadzeniu do ASCII) | 111 cytatow (A 44, B 38, C 28, D 1): 86 w zrzutach mojej instalacji, 21 tylko w plikach napisow (stany niewywolane: blad instalacji, decyzje, poranek, pytania analizy), 4 z wzorow skladanych (`Plytka {numer}`, `{plytka} - gniazdo {gniazdo}`, `Decyzja: {decyzja} - {osoba}, {godzina}`); niezgodnosci tresci 0 (konwencja ASCII - uwaga 6) |
| 13 | T13: `t13_higiena.py --repo <PC-katalog>\qc --od origin/e3/r1 --do origin/e3/d1` (skrypt z galezi, kopia w `robocze\rec-d1-r1\t13`) | "WYNIK T13: ZAL (0 naruszen)" |
| 14 | ASCII / LF z blobow (`git cat-file -p`) | 5 plikow (2 nowe, README, 2 stare z dopiskiem) + raport: 0 bajtow spoza ASCII, 0 znakow CR |
| 15 | dane osobowe: grep diffu, HTML, CZYTAJ, PDF | nazwisk, e-maili, nazw zlecen: 0 (nazwisko jest tylko w polu autora commitow - jak w calym repo) |

## 3. Kryteria zlecenia d1

| Nr | Kryterium | Ocena |
|---|---|---|
| 1 | dokument do 4 stron A4; A/B/C/D; krok = co kliknac + co widac + gdy inaczej | A - potwierdzone wlasna proba (3 strony, A3-A5 zgodne z ekranem). B - potwierdzone przegladem z odstepstwami: odeslania do starego dokumentu (uwaga 2), pola wymagane okna (uwaga 4), wiersz tabeli B4 (uwaga 3). C - 5 punktow i 3 zdania sa; brak planu na niepowodzenie (uwaga 5). D - jest. Kolejnosc dnia zgodna z miara poza 2.4 / 2.5a "opcjonalnymi" (uwaga 2) i proba f) bez pytania "Przelicz / Pomin" (opisane uczciwie, sekcja 5). |
| 2 | kazdy napis sprawdzony na instalacji 0.3.9-rc2, niezgodnosci 0 | potwierdzone wlasna proba (111 cytatow, 0 niezgodnosci tresci); znaczniki [NIE SPRAWDZONE BEZ SPRZETU] - 6 miejsc, w tym jedno zbedne (uwaga 7) |
| 3 | nowy arkusz 1-2 strony, numery jak w dokumencie, stary zostaje | potwierdzone (2 strony; `ARKUSZ_OBSERWACJI.md` bez zmian w diffie); brak kolumny na wspolczynnik (uwaga 4), malo miejsca na uwagi (uwaga 13) |
| 4 | stare pliki: zdanie na gorze, tresc bez zmian; README | potwierdzone przegladem (po 2 linie dodane, 0 usunietych) |
| 5 | HTML + PDF poza repo, CZYTAJ.txt, liczba stron | potwierdzone wlasna proba (3 i 2 strony); CZYTAJ.txt nie mowi o folderze `testy_sprzet` i o starym dokumencie (uwagi 1, 2) |
| 6 | pliki tylko z listy, kod bez zmian, bez danych osobowych, T13 | potwierdzone wlasna proba (6 plikow w dozwolonych katalogach, T13 0 naruszen) |
| 7 | raport, push, PR roboczy, bez scalania | potwierdzone przegladem (90ad932 na `origin/e3/d1`; PR #66 wg wykonawcy - nie sprawdzalem `gh`) |

## 4. Zakres plikow i zasady

- Zmienione: `DZIEN_TESTU_LAPTOP_I_SKANER.md` (A), `ARKUSZ_LAPTOP_I_SKANER.md` (A), `PIERWSZE_TESTY_NA_SPRZECIE.md` (M, +2),
  `PYTANIA_DO_WLASCICIELA.md` (M, +2), `README.md` (M, +13), `Ramki/stanowisko/raporty/E3-D1_2026-11-26.md` (A) - wszystkie
  z listy zlecenia; `narzedzia/` i kod programu nietkniete; nietykalne pliki - 0 zmian.
- ASCII i LF - zgodne; jezyk polski bez diakrytykow; duzych danych 0; 4 commity z przedrostkiem `E3-D1:` i stopka Opus 5.5.
- Dlugosc: dokument 3 strony A4 (limit 4), arkusz 2 (limit 2).

## 5. Do decyzji wlasciciela

1. Kroki 2.4 (pole skanera) i 2.5a (czy program poznaje plytke okragla nr 8) - w mierze sa czescia dnia, w dokumencie
   "tylko gdy jest czas". Obowiazkowe czy nie? (od tego zalezy czesc uwagi 2).
2. Proba f): wersja 0.3.9-rc2 nie ma pytania "Przelicz / Pomin" z miary; dokument zamienia probe na pomiar czasu
   przeliczania starych skanow. Czy tak zostaje na sobote?
3. Czesc C mowi szefowi "pytanie, czy przeliczac stare skany, bedzie w nastepnej wersji" - to zobowiazanie wobec szefa;
   i zdanie "a rano bez folderow zlecen i bez Excela nie podpowie numerow kuwet - po to jest ten dzien" laczy brak
   Excela z celem dnia (dzien sprawdza skaner) - do przeformulowania wedlug uznania wlasciciela.
