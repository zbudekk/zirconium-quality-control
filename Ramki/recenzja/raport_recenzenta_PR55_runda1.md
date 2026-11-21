# Raport recenzenta - PR #55 (E3-O2), runda 1

Data: 21.11.2026 (13:28-13:45). Zakres: `git diff main...e3/o2`, main = 8001b55, HEAD = 2c79335 (7 commitow, 15 plikow;
ostatni commit z kodem cb1eeef). Metoda: przeglad calego diffu kodu (842 wiersze), wlasne proby w kopii
`<PC-katalog>\qc-wt\rec-o2` (detached 2c79335; na koncu `git status --short` pusty), raport wykonawcy czytany po
wlasnych probach. Pliki robocze: `<PC-katalog>\koordynator\robocze\rec-o2\` (skrypty `proby1.py` ... `proby6.py`,
`wstrzyk.ps1`, logi `*.log`, zrzuty `zrzuty\*.png`). Uruchomiono: testy paczki (45), 6 skryptow prob (kontroler +
2 atrapy ramek w procesie, plik kalibracji, okno offscreen 1536 x 864), 14 wstrzykniec. Pelnego pytest nie powtarzano
(2334 passed / 9 skipped / 0 failed, kod 0 - wg wykonawcy, niesprawdzone przeze mnie; wiersz logu sprawdzil koordynator).

STAN: ZAKONCZONY.

## 0. Werdykt i liczby

WERDYKT: do scalenia po poprawkach (B 1, P 1, D 5).

- B1: wieczorem ramka W swieci wynik INNEJ plytki, gdy plytka o tym samym numerze lezy na ramce w czasie skanu drugiej
  (okragla n2 + kwadrat n2; okragla z dolkiem odczytanym jako inny WAZNY numer) - bez komunikatu. Mechanizm jest
  ZASTANY (na `main` identycznie dla kwadratow - proba H2 / H3 na zrodlach 8001b55), ale paczka otwiera go dla plytek
  okraglych w zwyklej pracy i nie daje ostrzezenia, ktore dala dla numerow ROZNYCH (kryterium 4b). Waga B wg wskazania
  koordynatora ("wynik innej plytki na ramce = B"); koordynator moze ja obnizyc do P / decyzji wlasciciela, jesli
  uzna, ze blad zastany nie blokuje tej paczki - opis faktow nizej wystarcza do tej decyzji.
- P1: rano komunikat `plytka_bez_skanu` kaze "Zeskanuj plytke nr N" albo uzyc "Zmien numer", gdy plytka JEST
  zeskanowana i czeka tylko na numer (zwykla droga kwadratow R59 / R54: numer zawsze wpisywany recznie).
- Reszta paczki: kryteria 1-6 i 8 potwierdzone wlasnymi probami; zakres plikow i zakazy zachowane; 0 przypadkow
  utraty skanu / danych; plik kalibracji bezpieczny (7 z 7 prob uszkodzen bez zmiany pliku).

## 1. Uwagi

| Nr | Waga | Plik:linia | Scenariusz -> co sie dzieje | Propozycja |
|---|---|---|---|---|
| B1 | B | `stanowisko/kontroler_api.py:2649-2685` (`_synchronizuj_ramke_w`: wynik ostatniego skanu idzie do ramki bez wzgledu na otwarte pytanie o ponowny skan), `:2191` (komunikat (b) tylko gdy numery ROZNE) | Wieczor. Plytka okragla n2 zeskanowana, lezy na ramce W i swieci swoj wynik (4 gniazda). Technik skanuje druga plytke, ktorej skan dostaje numer 2: (G1) kwadrat n2 z innymi pracami (oba ksztalty w obiegu - decyzja 4) albo (H1) okragla n3 z zaslonietym dolkiem, odczytana jako 2 (tryb pomylki opisany w raporcie O1 p. 9.3). Wynik: pod plytka LEZACA na ramce zapala sie wynik NOWEGO skanu (9 gniazd w kolorach drugiej plytki; proby G1, H1: "pod_plytka_lezaca_swieci_wynik_b" = true), 0 nowych komunikatow, na ekranie tylko pytanie "Ponowny skan tej samej plytki?" - ramka nie czeka na odpowiedz. Technik pracujacy wedlug ramki oglada / odklada nie te prace. Rano ten sam uklad zdarzen jest bezpieczny (dwa skany z jednym numerem = plytka poza planem, ramka ciemna - proba G2). Na `main` to samo dla kwadratow R59 + R54 i dla pomylki numeru wpisanego recznie (H2, H3 na zrodlach 8001b55: wynik drugiego skanu pod plytka lezaca, 0 pytan, 0 komunikatow) - mechanizm zastany. | Minimum w zakresie paczki (`kontroler_api.py`): dopoki skan ma otwarte pytanie o ponowny skan wobec INNEGO aktywnego skanu o tym samym numerze (`Plytka.moze_zastapic`), wysylac do ramki W wynik "bez numeru" (ramka ciemna, jak rano dla `zdublowane_plytki`) + komunikat "dwa skany z numerem N - odpowiedz na pytanie; jesli to dwie rozne plytki, zdejmij z ramki te, ktora lezy" ; test z atrapa ramki (plytka lezy, drugi skan o tym samym numerze -> 0 swiecacych pikseli do odpowiedzi). Warianty bez pytania (R59 + R54, numer wpisany z bledem - H2, H3) sa poza kryteriami paczki: do decyzji wlasciciela (sekcja 5 p. 1). |
| P1 | P | `stanowisko/kontroler_api.py:2196-2203`, tekst `stanowisko/statusy.py:460-463` | Rano, kwadrat R59 / R54 (numer zawsze wpisywany recznie) albo okragla z nieczytelnymi dolkami: technik skanuje plytke, kladzie ja na ramce P i dopiero potem odpowiada na "Podaj numer plytki". Na ekranie pojawia sie ostrzezenie "Na ramce lezy plytka, ktorej nie ma w planie pieca ... Zeskanuj plytke nr 4. Jesli byla juz skanowana, to numer jej skanu jest zly - popraw go przyciskiem 'Zmien numer' przy tej plytce" (proba C2, zrzut `r1_plytka_bez_skanu_kwadrat_bez_numeru_1536.png`). Plytka BYLA skanowana, a kafelek "Plytka bez numeru" nie ma przycisku "Zmien numer" (ma go tylko INNA plytka pieca). Rada jest falszywa w zwyklej pracy: ponowny skan = zdublowany skan; "Zmien numer" na sasiedniej plytce kwadratowej = jej wynik pod zla plytka. Wieczorem tego nie ma (skan bez numeru = brak komunikatu (b)). | Gdy plan ma `pominiete.bez_numeru` niepuste: nie pokazywac `plytka_bez_skanu` (pytanie "Podaj numer plytki" juz mowi, co zrobic) albo osobny tekst "jesli to plytka z ostatniego skanu - podaj jej numer w pytaniu wyzej"; test: skan bez numeru + plytka na ramce P -> brak rady "Zeskanuj". |
| D1 | D | `ramka/kalibracja.py:209-211`; `testy/test_okragle_ramka.py:257` | Zapis przez plik tymczasowy i `os.replace` dziala (proby K5: przerwany zapis i nieudana podmiana = plik bez zmian), ale zaden test tego nie pilnuje: wstrzykniecie I6b (zapis wprost do pliku kalibracji) - 6 passed z 6 testow `k6`. | Test: `zapisz` pisze polowe i zglasza blad -> plik kalibracji bajtowo bez zmian. |
| D2 | D | `stanowisko/kontroler_api.py:3206`, `:2197` | Dwa warunki ochronne bez testu: I7 (przyczyna bledu analizy doklejana przy kazdym rodzaju bledu, nie tylko "analiza") - 2 passed; I8 (komunikat `plytka_bez_skanu` takze w czasie analizy / skanowania) - 10 passed. Zachowanie kodu poprawne (proba `blad`: opis "znaleziono 3 stozki..." i obcy wyjatek = tekst ogolny). | Po jednym tescie na warunek. |
| D3 | D | `ramka/kalibracja.py:205-207` | Plik kalibracji tylko do odczytu (atrybut R): uklady sa w pamieci + ostrzezenie (dobrze), ale przy KAZDYM starcie obok powstaje kopia `.przed_uzupelnieniem` rowna plikowi (proba K3) - plik-smiec, mylacy przy pozniejszym prawdziwym uzupelnieniu (kopii sie nie nadpisuje). | Kopie robic dopiero po udanym zapisie pliku tymczasowego albo usuwac ja, gdy podmiana sie nie udala. |
| D4 | D | `stanowisko/kontroler_api.py:3240-3257`, `:2679` | Komunikat (c) i "ramka ciemna" dzialaja dla KAZDEGO ukladu, takze kwadratu: wynik kwadratu z waznym `numer_z_dolkow` innym niz numer podany = ramka ciemna (proba A1: R59 i R54, 0 pikseli), choc przed paczka swiecila wg numeru podanego. Dzis kwadrat nie ma dolkow w polu skanu o100 (dolki na promieniu 52,5-57,6 mm - policzone z `uklad.json`), wiec w praktyce nie wystapi; przy wiekszym polu skanera stanie sie regula. Zgodne z brzmieniem kryterium 4c (bez ograniczenia do okraglych). | Zostawic; dopisac zdanie w opisie / dokumencie dnia sprzetu (raport wykonawcy 10.1 pisze "kwadratu nie dotyczy" - to prawda tylko dla pola o100). |
| D5 | D | `opisy_modulow/aplikacja.md` (poza lista plikow paczki) | Wersja kontraktu 6 (pola `Plytka.numer_niezgodny` / `numer_z_dolkow`, 4 rodzaje komunikatow) nie ma wpisu w opisie kontraktu - wykonawca zglasza to jako POTRZEBUJE 5 (slusznie nie ruszal pliku). | Koordynator: dopisac przy scalaniu albo w paczce porzadkowej. |

## 2. Wlasne proby

| Nr | Polecenie / proba | Wynik |
|---|---|---|
| 1 | `py.cmd -m pytest -q -p no:cacheprovider testy\test_okragle_sesja.py testy\test_okragle_ramka.py` (log `p1_testy_paczki.log`) | 45 passed w 18,0 s |
| 2 | `proby1.py` - kontroler `AtrapaKontrolera` + prawdziwi klienci `KlientRamki` + 2 atrapy ramek (program ramki), 9 scenariuszy (log `proby1.log`, 30 wierszy) | A1: kwadrat R59 i R54, numer podany 2, `numer_z_dolkow` 1 -> ramka ciemna (0 px) + `numer_niezgodny` (2 z 2). A2: kwadrat bez dolkow i z dolkami zgodnymi -> swieci dokladnie bloki kwadratu (2 z 2), 0 nowych komunikatow; zmiana numeru 2 -> 3 przy plytce 2 na ramce -> ciemno. B1 / B2: okragla n2 + kwadrat n2 -> pytanie `ponowny_skan`, 0 zastapien bez potwierdzenia. C1: plytka polozona PRZED skanem -> 0 komunikatow, po skanie swieci; poprzednia plytka zostaje na ramce w czasie skanu nastepnej -> komunikat (b), po "Zamknij" nie wraca, po zdjeciu znika. C2: rano plytka przed 1. skanem -> 0 komunikatow (brak planu); skan kwadratu bez numeru + plytka na ramce -> komunikat `plytka_bez_skanu` (uwaga P1); po podaniu numeru znika i ramka swieci (51 px); plytka testowa n9: `na_ramce` False, poza planem, 0 nowych komunikatow. D1: zatrzymanie ramki W -> komunikat (a) znika po 0,9 s. E1: plytka 2 na ramce P i 4 na ramce W -> komunikat (a) z wlasciwa rada, 0 px; plytka 5 na ramce P wieczorem (bez planu) -> 0 komunikatow. F1: okragla z dolkow 1, na ramce 3 -> (b); po "Zmien numer" na 3 -> (c), ramka ciemna (0 px). |
| 3 | `proby2.py` - plik kalibracji, bloki, umowy sesji (log `proby2.log`, 14 prob) | K0: bloki ukladu ramkowego = bloki kwadratu: wieczorna 57 z 57 (19 gniazd x 3 numery), poranna 72 z 72 (24 x 3); gniazda w `uklad.json` rowne 19 z 19 i 24 z 24; uklad wieczorny tylko w ramce W, poranny tylko w P. K1: stary plik (3 wpisy `kalibracja`, 1 `geometria`) -> 2 dopisane, 4 z 4 starych wpisow jako identyczny ciag bajtow w nowym pliku, kopia = stary plik (5969 bajtow), 2. start: plik bez zmian, 0 ostrzezen. K2: plik w innym formatowaniu (CRLF, wciecie 2) -> wartosci 4 z 4 rowne, plik przepisany w formacie programu (LF), kopia bajtowa starego. K3: tylko do odczytu -> plik bez zmian, 2 uklady w pamieci, ostrzezenie (uwaga D3). K4: uciety / wersja 2 / nieznany klucz / pusty -> kalibracja None + ostrzezenie, plik bez zmian, 0 plikow obok (4 z 4). K5: zapis przerwany w polowie i nieudana podmiana -> plik bez zmian, brak `.tmp`, uklady w pamieci (2 z 2). K6: istniejaca kopia nie jest nadpisywana, stary `.tmp` znika. K7: brak katalogu modeli -> kalibracja z pliku zostaje, plik bez zmian. U1: 18 nazw - 8 dotychczasowych ukladow ma te same `okragla` / `typ` / `wersja` / rodzine / numery / `na_ramce` co przed paczka + `ramkowa` False; 2 ramkowe: rodzina kwadratu, numery (1, 2, 3) / (4, 5, 6), `na_ramce` True tylko poranna. |
| 4 | `proby3.py`, `proby4.py` - okno programu offscreen 1536 x 864, `QT_QPA_FONTDIR=C:\Windows\Fonts` (5 zrzutow; 3 obejrzane: `w1`, `w3`, `r1`; `w2`, `w4` - tylko pomiar / tekst) | Komunikaty w zoltych panelach nad mapa, szerokosc 966 px: (a) 3 wiersze (111 px), (b) wieczor 111 px, (b) rano 2 wiersze (90 px), (c) 3 wiersze; 3 komunikaty naraz (praca niesprawdzona + (c) + (a)) mieszcza sie, mapa 19 gniazd widoczna w calosci, przycisk "Zmien numer" widoczny. Tytul (c) na ekranie: "Plytka 2: Numer plytki nie zgadza sie ze skanem". Okno obsluguje nowe rodzaje bez zmian w `ui/**`. |
| 5 | `proby4.py` (blad analizy) | "znaleziono 1 stozki znacznikow, potrzeba 3" -> "w skanie widac 1 z 3 znacznikow plytki ..."; "znaleziono 3 stozki ..." i obcy wyjatek z podobnym slowem -> tekst ogolny "blad analizy" (2 z 2 bez mylacej przyczyny) |
| 6 | `proby5.py`, `proby6.py` (ta sama liczba na ramce i w skanie; log `proby5.log`, `proby6.log`) | G1 (HEAD): okragla n2 lezy i swieci, skan kwadratu n2 -> pod lezaca plytka swieci wynik kwadratu (9 gniazd), pytanie `ponowny_skan`, 0 komunikatow. H1 (HEAD): to samo dla okraglej z dolkami odczytanymi jako 2. H2, H3 (HEAD i zrodla `main` 8001b55 podstawione na czas proby, potem przywrocone): R59 + R54 i dwa skany R59 z numerem podanym 2 -> wynik drugiego skanu pod plytka lezaca, 0 pytan, 0 komunikatow - na `main` tak samo. G2 (rano): okragla n4 swieci (51 px), kwadrat z numerem 4 -> plan pusty, 0 px, `zdublowane_plytki` [4], blokada "Zamknij piec". |
| 7 | Wstrzykniecia (`wstrzyk.ps1`, log `wstrzykniecia_rec.log`; kazde cofniete `git checkout`, po kazdym 0 plikow zmienionych) - 14 | Wykryte 11: I1 (kryt. 1: numery ramkowe zamienione - 3 failed), I2 (kryt. 2: role ukladow W / P zamienione - 5 failed), I2b (kryt. 3: plytka testowa `na_ramce` - 2 failed), I3 (4a: numery ramki W dla obu ramek - 1 failed), I4 (4b W: komunikat nie znika - 1 failed), I4b (4b P: klucz planu liczba zamiast tekstu - 1 failed), I5 (4c: numer spoza ukladu jako niezgodny - 1 failed), I5b (4c rano: brak wstrzymania - 1 failed), I5c (4c wieczor: numer podany do ramki - 1 failed), I6 (kryt. 6: program dostaje kalibracje sprzed uzupelnienia - 2 failed), I6c (kryt. 6: brak kopii starego pliku - 1 failed). NIE wykryte 3: I6b (zapis nieatomowy), I7 (przyczyna bledu przy kazdym rodzaju), I8 (komunikat w czasie analizy) - uwagi D1, D2. |
| 8 | Zgodnosc z O3 / O4: `git diff --name-only main...e3/o3` i `...e3/o4` wobec 15 plikow O2; `git merge-tree --write-tree e3/o2 e3/o3` i `e3/o2 e3/o4`; wyszukanie uzyc `czesci_ukladu(` / `WERSJA_KONTRAKTU` / `numer_niezgodny` w `aplikacja.py`, `ui/*.py`, `samokontrola.py`, `porownaj.py` | 0 wspolnych plikow z O3 i z O4; oba scalenia probne bez konfliktu; 0 uzyc zmienionych elementow kontraktu w oknie i w plikach O3 / O4 (okno nie sprawdza numeru wersji kontraktu); `test_led.py` z O4 ma nadal `--kalibracja`, `--rola`, `--uklad`, `--sprzet`, `--wszystkie`; `ramka.service` z O4 ma `--sprzet rpi` - zgodne z README paczki. |
| 9 | Bajty 15 plikow z obiektow git (`git cat-file blob e3/o2:<plik>`), `git diff --check` | 14 plikow: 0 bajtow nie-ASCII, 0 CR; `statusy.py`: polskie znaki jak dotad (plik istniejacy), 0 CR; `diff --check` pusty; 0 plikow binarnych. |

## 3. Kryteria zlecenia

| Nr | Kryterium | Ocena |
|---|---|---|
| 1 | Wieczor: 3 skany n1-n3 przyjete, 0 blokad trybu | potwierdzone wlasna proba (testy paczki + I1; proby 2: skany okragle przyjete, `numer_zrodlo` dolki, ramka swieci bloki kwadratu) |
| 2 | Rano n4-n6 w planie, 24 z 24 gniazd, bloki = kwadrat (72 z 72); wieczor 57 z 57 | potwierdzone wlasna proba (K0: 72 z 72 i 57 z 57; I2; proby 2 i 6: klatka atrapy = bloki kwadratu) |
| 3 | n8 / n9 i kwadraty jak dzis; 0 zmienionych asercji | potwierdzone z zastrzezeniami: zachowanie n8 / n9 bez zmian (C2, I2b, U1); kwadraty: swiecenie bez zmian (A2), NOWE sa komunikaty (a) / (b) i - tylko gdy wynik ma wazny `numer_z_dolkow` - (c) z ciemna ramka (D4). 2 zmienione asercje - ocena nizej |
| 4 | Ostrzezenia a / b / c w 6 z 6, ramka ciemna, skan zostaje; numer spoza ukladu = pytanie | potwierdzone wlasna proba (E1, C1, F1, A1, I3-I5c; skan `przyjety` w kazdej probie); zastrzezenia: P1 (falszywa rada rano), B1 (brak ostrzezenia przy numerach ROWNYCH - poza brzmieniem kryterium) |
| 5 | Ponowny skan: okragla nie zastepuje kwadratu bez pytania (i odwrotnie) | potwierdzone wlasna proba na poziomie sesji (B1, B2, G1: pytanie, zastapienie dopiero po potwierdzeniu); na poziomie ramki W wynik nowego skanu swieci przed odpowiedzia (B1) |
| 6 | Stary plik kalibracji: 2 nowe uklady, skalibrowane bajtowo bez zmian; `test_led` na atrapie | potwierdzone wlasna proba (K1-K7; I6, I6c); `test_led` - potwierdzone testem paczki (w 45 passed), wlasnej osobnej proby nie robiono |
| 7 | Pelny pytest 0 failed | wg wykonawcy, niesprawdzone (2334 / 9 / 0 na cb1eeef; koordynator sprawdzil wiersz logu) |
| 8 | Wstrzykniecia min. 6 | potwierdzone wlasna proba: moje 14, w tym po co najmniej 1 wykrytym na kryteria 1, 2, 4a, 4b, 4c, 6 (11 wykrytych, 3 nie - D1, D2); wykonawcy 17 z 17 - wg wykonawcy |
| dod. | S1 poz. 3 (przyczyna bledu analizy) | potwierdzone wlasna proba (proba 5): liczba znacznikow pochodzi z tekstu wyjatku `plate.py:306` / `:814` (0-2), inne bledy bez przyczyny |
| dod. | S1 poz. 8 (`tryb_ramki` po tescie diod), README, sledzenie numeru (10.1) | potwierdzone przegladem (kod `:2117-2119`; README zgodny z plikami O4; opis 10.1 zgodny z tym, co widac w probach: numer z ramki nie trafia do skanu) |

Dwie zmienione istniejace asercje:
- `testy/test_ramka.py:1504-1508` - lista i liczby ukladow kalibracji startowej (4 -> 6 ukladow, liczby 4 starych bez
  zmian): zmiana dopuszczona zleceniem, nic nie oslabia.
- `testy/test_session_wieczor.py:782-783` - slownik `czesci_ukladu` ma dodatkowy klucz `"ramkowa": False`; trzy
  dotychczasowe klucze i wartosci bez zmian (proba U1: 8 z 8 dotychczasowych ukladow), 0 odbiorcow slownika poza
  `session.py` / `session_rano.py` / `kontroler_api.py`. To ROZSZERZENIE UMOWY wymagane planem, nie zmiana zachowania
  kwadratow ani n8 / n9 - do przyjecia.

Ocena dwoch zdan wykonawcy:
- "komunikaty o plytce na ramce dzialaja tez dla kwadratow" - zachowanie zamierzone i potrzebne ((a) nie da sie
  ograniczyc - ramka nie zna ksztaltu; (b) wieczorem jest prawdziwy), z jednym bledem: P1.
- "po poprawieniu numeru odczytanego z zaslonietego dolka ramka zostaje ciemna" - zgodne z decyzja 5 doslownie i
  bezpieczne (proba F1: 0 px), ale to slepa uliczka dla technika; do decyzji wlasciciela (sekcja 5 p. 2).

## 4. Zakres plikow i zasady

- 15 plikow, wszystkie z listy zlecenia (10 zmienianych + 2 nowe testy + raport + 2 istniejace testy w dopuszczonym
  zakresie). Nietykalne (`match.py`, `inspect.py`, `plate.py`, `synth.py`, `uklad.py`, `modele_plytek/**`), schemat
  bazy, `aplikacja.py`, `ui/**`, `ustawienia.py`, `porownaj.py`, `samokontrola.py`, `test_led.py`, `ramka/rpi/**`,
  `instrukcje/**`, `Ramki/etap3/**`: 0 zmian (lista nazw z `git diff --name-only`).
- Nowe pliki ASCII + LF; 0 plikow binarnych / duzych; danych osobowych nie znaleziono (testy na danych sztucznych,
  raport bez nazw zlecen).
- Kontrakt kontroler - okno: zmiana addytywna (2 pola na koncu `Plytka` z wartosciami domyslnymi, 4 rodzaje
  komunikatow, klucz `pominiete.numer_niezgodny`); okno pokazuje nowe komunikaty bez zmian w `ui/**` (zrzuty).
  `opisy_modulow/aplikacja.md` bez wpisu o wersji 6 (D5).
- Odstepstwa zgloszone przez wykonawce uczciwie (kolejnosc test / kod dla kontrolera, `fullmatch`, 2 asercje).
- Moja kopia: `git -C qc-wt\rec-o2 status --short` pusty, HEAD 2c79335; zrodla `main` byly podstawione tylko na czas
  proby 6 (7 plikow) i przywrocone. Procesow python po moich probach nie zostawilem (kazda proba konczyla sie przed
  nastepna; `Get-Process python` o 13:45: 2 procesy, oba nie moje - PID 27544 ze startem 13:25:43, przed moim startem,
  i PID 12560 bez czasu startu, "wydmuszka" opisana w raporcie wykonawcy).

## 5. Do decyzji wlasciciela

1. Dwie plytki z tym samym numerem (kwadrat i okragla; R59 i R54) w jednej zmianie wieczornej: ramka W rozpoznaje
   plytke tylko po numerze, wiec plytka LEZACA na ramce w czasie skanu drugiej dostaje jej wynik (B1; dla kwadratow
   tak jest juz dzis). Poza poprawka B1 potrzebna zasada pracy na dni 28-29.11: przed skanem nastepnej plytki zdjac
   poprzednia z ramki W; nie mieszac w jednej zmianie dwoch plytek o tym samym numerze - albo zgoda na twardsza regule
   w programie (ramka ciemna, gdy plytka lezala na ramce w chwili startu skanu).
2. Numer poprawiony recznie a dolki (sprawa 3 wykonawcy): po poprawce numeru odczytanego z zaslonietego dolka ramka
   zostaje ciemna dla tej plytki (rano = sortowanie do kuwet tylko wedlug ekranu). Propozycja: gdy numer podany =
   numer z magnesow ramki, a rozny tylko od dolkow (2 z 3 zrodel zgodne) - swiecic; albo przycisk potwierdzenia.
3. Komunikat (b) wieczorem pojawia sie w zwyklej pracy, gdy poprzednia plytka zostaje na ramce w czasie skanu
   nastepnej (proba C1) - jest prawdziwy i znika sam; ocenic uciazliwosc na sprzecie.
4. Komunikat (c) i ciemna ramka takze dla kwadratow, gdy skan obejmie ich dolki (D4) - zostawic czy ograniczyc do
   plytek okraglych.
5. Kalibracja ukladow okraglych z geometrii: ostrzezenie tylko przy 1. starcie, w podpowiedzi paska ramek (sprawa 4
   wykonawcy); czy potrzebne trwale przypomnienie, dopoki `zrodlo` = "geometria".
6. Brzmienie 4 komunikatow i 3 przyczyn bledu analizy (raport wykonawcy, sekcja 13) - teksty sa proste, mowia co
   zrobic, mieszcza sie na 1536 x 864; do akceptacji poza rada z P1.
