# Raport recenzenta - PR #51 (E3-O1), runda 1

Data: 21.11.2026. Zakres: `git -C <PC-katalog>\qc diff main...e3/o1`, `main` = beddde7, HEAD = 43d78e1 (4 commity,
22 pliki). Recenzent niezalezny; kopia do prob `<PC-katalog>\qc-wt\rec-o1` (detached 43d78e1), pliki robocze
`<PC-katalog>\koordynator\robocze\rec-o1\`.

Metoda: przeglad diffu (kod, testy, wzor ustawien, narzedzie pomiarowe); wlasne sumy SHA-256 obiektow git; wlasne proby
rozpoznania 8 vs 10 kandydatow (kandydaci wczytani wprost `uklad.wczytaj`, bez narzedzia wykonawcy); przeliczenie
surowych wynikow wykonawcy wlasnym skryptem; wstrzykniecia bledow w kopii (3, kazde cofniete); `t13_higiena.py`.
Pelnego pytest nie powtarzano (wynik sprawdzil koordynator w logu).

Recenzje prowadzilo dwoch recenzentow: pierwszy zginal po ok. 8 minutach (limit konta) i zostawil proby W1-W5;
nastepca (ten sam plik, ta sama kopia) zrobil reszte: W6-W12, uwagi, ocene kryteriow, werdykt. Raport wykonawcy
nastepca przeczytal po przegladzie kodu i narzedzia, przed wlasnymi probami (proby W6-W9 zaprojektowane z kodu
`plate.py:826-850`, nie z raportu). Kazda liczba ponizej pochodzi z pomiaru recenzenta, chyba ze napisano
"wg wykonawcy".

## 0. Werdykt i liczby B / P / D

WERDYKT: do scalenia po poprawkach - B 1, P 2, D 2. Uwaga 1 (B) nie da sie usunac w zakresie plikow O1 (wymaga
`plate.py`): przed scaleniem potrzebna decyzja wlasciciela - przyjac jako opisane ograniczenie albo wariant C.

- BRAMKA w brzmieniu zlecenia (kryteria 3 i 4 na zestawach ze zlecenia): POTWIERDZONA wlasna proba. Kryterium 3:
  32 z 32 skanow odniesienia, 64 z 64 par (wlasna proba) + 160 z 160 par w surowych wynikach wykonawcy (przeliczone).
  Kryterium 4: 0 "pewny ze zlym ukladem" w 56 wlasnych przebiegach z wynikiem (pole 100 / 96 / 94; bez numeru i z
  numerem zgodnym), pola 90 i 80: 32 z 32 bez wyniku przy 10 kandydatach i 24 z 24 bez wyniku przy 8.
- POZA zestawem zlecenia jest pogorszenie wprowadzone paczka (uwaga 1): plytka okragla testowa n8 / n9 z dolkiem kodu
  zaslonietym, gdy w skanie nie ma scianki bocznej plytki (pole 99-97 mm albo skan bez scianki): 17 z 26 par
  "8 kandydatow: uklad dobry i pewny -> 10 kandydatow: KWADRAT, pewny". Przy czytelnych dolkach (10 par, pola 100-97
  i skan bez scianki) oraz przy polu 100 ze scianka boczna mimo zaslony (4 pary) pogorszenia nie ma: 0 z 14 par.
- Plytki pracujace dzis w ramkach (kwadraty R59 i R54) i cala rodzina R54: bez pogorszenia w zadnej probie.

## 1. Uwagi

| Nr | Waga | Plik:linia | Scenariusz | Propozycja |
|---|---|---|---|---|
| 1 | B | `stanowisko/ustawienia.py:147-149`, `ustawienia.przyklad.toml:35-36` (2 nowe uklady wbudowane) -> skutek w `stanowisko/plate.py:830-850` (kod bez zmian) | Technik skanuje plytke okragla TESTOWA n8 / n9 (obslugiwana dzis). Dolki kodu nie daja waznego numeru (jeden dolek zasloniety albo nieczytelny -> numer 0 albo 1), a skan nie zawiera scianki bocznej plytki (pole 99-97 mm albo skaner nie widzi scianki). Przed paczka (8 kandydatow): uklad `okragla_wieczorna` / `okragla_poranna`, `pewny` = True, `powod` = `ksztalt` (kolo wobec kwadratu: 53-435 mm2 niewyjasnione, prog 40). Po paczce (10 kandydatow): uklad KWADRAT `wieczorna` / `poranna`, `pewny` = True, `powod` = `dolki_wykluczaja`, numer nieznany. Liczby (W7, W9): pole 100 ze scianka - 0 z 4 par; pole 99 - 3 z 10; pole 98 - 10 z 10; pole 97 - 2 z 4 (pozostale 2 zle takze przy 8); pole 100 bez scianki bocznej - 2 z 2; razem 17 z 26 par "8 dobrze i pewnie -> 10 zle i pewnie" (poza polem 100 ze scianka). Mechanizm: regula ksztaltu (`plate.py:830-831`) porownuje DWA najlepsze uklady; po paczce sa nimi dwa uklady okragle (testowa i ramkowa), ktore dla skanu plytki testowej roznia sie tylko o rowek pokrywki na sciance bocznej (58,2-64,1 mm2 przy polu 100; 0-50 mm2 przy 99-97), wiec ksztalt przestaje rozstrzygac, a regula `dolki_wykluczaja` (`plate.py:845-847`) odrzuca OBA uklady okragle (dolki widac, numer niewazny) i zostawia kwadrat - choc ksztalt mowi "kolo" z przewaga 53-435 mm2. Skutek w programie: plytka testowa zapisana jako plytka ramki bez numeru (zly uklad w bazie, pytanie o numer plytki); mapa gniazd ta sama. Program glowny nie czyta `pewny` (0 uzyc w `aplikacja.py`, `kontroler_api.py`, `session*.py`), wiec flaga niczego tu nie lagodzi. Raport wykonawcy (sekcje 6 i 13.3) i `opisy_modulow/plate.md:30` opisuja tylko "rozroznienie ramkowa / testowa zalezy od scianki bocznej, zapas maly" - nie mowia, ze skutkiem jest pewny KWADRAT, ze dotyczy to plytek n8 / n9 rozpoznawanych przed paczka dobrze, ani ze wystarcza pole 99 mm; pomiar dolkow zaslonietych (kryterium `z`) objal tylko plytki ramkowe przy polu 100. | Poprawka kodu lezy poza zakresem O1 (`plate.py` nietykalny): regula ksztaltu powinna porownywac KSZTALTY (najlepszy uklad okragly wobec najlepszego kwadratowego) i dopiero w obrebie wygranego ksztaltu stosowac numer / dolki. Decyzja wlasciciela przed scaleniem: (a) przyjac jako znane ograniczenie plytek testowych n8 / n9 - wtedy w O1: pomiar w `auto_uklad_r58.py` (plytki testowe R59 z zaslonietym dolkiem, pola 100 / 99 / 98 / 97, 8 vs 10 kandydatow, wynik liczony wprost jako "pogorszenie wobec 8"), test utrwalajacy zachowanie (jak testy "numer niezgodny"), opis w `plate.md` (granice rozpoznania) i w raporcie paczki (sekcje 1, 6, 13); albo (b) wariant C w osobnej paczce przed O2 / O3. |
| 2 | P | `testy/test_auto_uklad_r58.py:198-206` (`test_male_pole_skanu_nie_daje_pewnego_zlego_ukladu`) | Test ma pilnowac kryterium 4 w pytest, ale wszystkie 5 przypadkow to pola 90 i 80 mm, przy ktorych rozpoznanie konczy sie `BladWyrownania` (brak 3 stozkow) - klasa zawsze `brak_wyniku`, asercja `!= "zly_pewny"` nie moze pasc. Wstrzykniecie W10: wybor ukladu zepsuty w `plate.py` (zawsze ostatni kandydat, `pewny` = True) -> 5 z 5 przypadkow tego testu PRZECHODZI (10 innych testow pada). Test niczego nie sprawdza. | Pola 96 i 94 mm (tam jest wynik: u wykonawcy 162 z 176, u recenzenta 32 z 32) z asercja `dobry_pewny`; dla 90 / 80 osobna asercja wprost: `brak_wyniku` i `BladWyrownania` (to jest zachowanie do utrwalenia). Po decyzji do uwagi 1 (a): dodatkowo przypadek plytki testowej z zaslonietym dolkiem. |
| 3 | P | `narzedzia/auto_uklad_r58.py:205`, `:227` (`ocen_k3`), `:273` (`ocen_k4`) | Narzedzie bramki uznaje brak wyniku za spelnienie. `ocen_k3`: para, w ktorej 8 i 10 kandydatow koncza sie wyjatkiem, ma `ten_sam_uklad` = True i `pewnosc_nie_gorsza` = True. `ocen_k4`: pole 100 z samymi `brak_wyniku` daje `spelnione` = True. Proba W11: 4 przebiegi bez wyniku -> `ocen_k3` "1 z 1 skanow, SPELNIONE"; 4 z 4 `brak_wyniku` przy polu 100 -> `ocen_k4` SPELNIONE. Koordynator ma uzyc narzedzia po O2 / O3 (i ewentualnie po wariancie C): zmiana, ktora zepsuje wyrownanie wszystkich skanow, da "BRAMKA SPELNIONA", kod 0. W pomiarze wykonawcy tego nie bylo (zgodny z prawda 160 z 160 - przeliczone, W6a), wiec wynik paczki nie jest podwazony. Test `test_narzedzie_ocena_par_8_i_10_kandydatow` nie ma przypadku "oba bez wyniku". | `ocen_k3`: para dobra tylko, gdy oba przebiegi maja wynik (brak wyniku w ktorymkolwiek = para zla, liczona osobno) - albo wprost warunek "zgodny z prawda przy 8"; `ocen_k4`: `spelnione` wymaga co najmniej jednego wyniku przy polu 100, a wiersz werdyktu podaje "bez wyniku N z N" dla kazdego pola; test na oba przypadki. |
| 4 | D | `narzedzia/auto_uklad_r58.py:155` (`ostrzezenia`) | Wynik narzedzia zawiera pelna sciezke katalogu programu w tekstach ostrzezen `plate` ("numer plytki z dolkow 0 nie ma modelu w C:\...\modele_plytek\..."): 9 z 974 wierszy `robocze\o1\pomiar\przebiegi.jsonl`. Na PC wlasciciela sciezka zawiera nazwe konta. Nazw plikow projektow w wyniku nie ma (sprawdzone). | Ostrzezenia przepuszczac przez `baza.bez_sciezek` albo zapisywac tylko ich liczbe i pierwszy czlon. |
| 5 | D | `opisy_modulow/plate.md:32` | Zdanie o numerze drugiego ksztaltu mowi "gdy w skanie nie ma brzegu plytki, wynik jest pewny mimo zlego ukladu (pole 96 / 94)". To samo zdarza sie przy polu 100, gdy miara ksztaltu wypada ponizej progu 40: u wykonawcy 1 z 62 (kwadrat R54), w probie recenzenta W8 kwadrat R59 n1 z podanym 8 -> `okragla_wieczorna`, `pewny` = True przy 8 i przy 10 kandydatach (1 z 5 przebiegow przy polu 100). Zachowanie istniejace, opis niepelny. | Dopisac "takze przy polu 100, gdy miara ksztaltu jest ponizej progu (1 z 62)". |

## 2. Wlasne proby

| Nr | Polecenie / metoda | Wynik |
|---|---|---|
| W1 | `git show e3/o1:<sciezka> \| sha256sum` dla 10 nowych plikow `modele_plytek/okragla_ramkowa_*/**` wobec `Ramki/wyniki_v2/raport/sha256_stl_po_R58.txt` | 10 z 10 zgodnych (8 STL + 2 JSON) |
| W2 | `sha256sum` 8 STL w `<PC-katalog>\r58\Ramki\wyniki_v2\stl\` i 2 JSON w `Ramki/wyniki_v2/json/` (takze `git show main:`) wobec obiektow git galezi | 10 z 10 identycznych sum zrodlo = obiekt git; rozmiary 5044 / 5840 B (JSON), 1105084-1275984 B (STL) |
| W3 | `sha256sum` 10 plikow w drzewie roboczym kopii `rec-o1` (`core.autocrlf` = false) | 10 z 10 zgodnych z lista R58 |
| W4 | `git ls-tree -r main Ramki/stanowisko/modele_plytek` wobec `git ls-tree -r e3/o1 ...` bez `okragla_ramkowa` (`cmp`) | 28 z 28 obiektow (tryb, blob, sciezka) identycznych; razem 38 plikow na galezi |
| W5 | `git diff --stat main e3/o1 -- match.py inspect.py plate.py synth.py uklad.py baza.py raporty/testy_krawedz` | 0 zmian |
| W1-W5 wyrywkowo | (nastepca) powtorzone: `git show e3/o1:` 3 pliki (`wieczorna/plytka_n2.stl`, `poranna/uklad.json`, `poranna/plytka_bazowa.stl`) wobec listy R58, `git show main:` JSON R58 i pliku STL w `<PC-katalog>\r58\`; `git diff --name-status main e3/o1 -- modele_plytek`; lista 22 plikow wobec listy plikow zakazanych | 3 z 3 sum zgodnych; 10 plikow `A`, 0 zmienionych; 0 plikow zakazanych w diffie |
| W6 | `ciezki.ps1 -Tor 1` -> `krok_bramka_k3.cmd` -> `proba_bramka.py` (skrypt poprzednika, przejrzany): 32 skany odniesienia (po 2 na typ plytki w kazdym z 4 folderow: 16 R59 + 16 R54; 8 typow po 4 skany), 8 kandydatow (lista nazw z `main`, wczytane wprost `uklad.wczytaj`) vs 10, bez numeru i z numerem z prawdy, kolejnosc 8 / 10 na przemian; 128 przebiegow, 10:08-10:14, kod 0; wynik `bramka_k3.jsonl` | 32 z 32 skanow, 64 z 64 par: ten sam uklad, `pewny` 8 / 10 kand. = 64 / 64, zgodny z prawda 64 / 64, numer i zrodlo te same 64, bledow 0, macierz rozni sie najwyzej o 1,8e-15. Przejscia `powod`: bez numeru 0 zmian (ksztalt 13, dolki_wykluczaja 3, numer_z_dolkow 16); z numerem `numer_podany` -> `ksztalt` 6, -> `dolki_wykluczaja` 2 (8 z 8 kwadratow R59), bez zmiany 24. Czas R59 (16 skanow, jeden proces recenzenta): mediana 2,14 -> 2,85 s bez numeru (+ 0,71), 2,05 -> 2,74 s z numerem (+ 0,69). Miara ksztaltu skanu okraglej testowej R59 wobec modelu ramkowej: 58,7-63,9 mm2 (8 skanow; prog 40), wobec kwadratu 498-536 |
| W6a | przeliczenie surowych wynikow wykonawcy wlasnym skryptem PowerShell (bez narzedzia wykonawcy): `robocze\o1\pomiar\przebiegi.jsonl` (974 wiersze) i `pomiar_posrednie\przebiegi.jsonl` (388) | K2 48 z 48 (24 skany x 2 tryby, gniazda zgodne 48, numer = prawda 48); K3 320 przebiegow = 160 par na 80 skanach (24 + 16 + 24 + 16), 160 z 160 ten sam uklad i pewny, zgodny z prawda 160 / 160, numer podany = numer z prawdy 80 z 80, przejscia `powod` jak w raporcie (14 + 2 zmian); K4 zestaw zgodny: pole 100 - 88 dobry_pewny; 96 - 86 + 2 brak; 94 - 76 + 12 brak; 90 i 80 - 88 z 88 brak wyniku (takze 44 z 44 przy 8 kandydatach); kazde pole 10 ukladow; numer niezgodny "pewny zly": 10 kand. 1 / 16 / 15 z 62, 8 kand. 1 / 16 / 16 z 44 - wszystkie `numer_drugiego_ksztaltu`; dolki zasloniete: 24 z 24 uklad dobry i pewny, numer inny wazny 3 z 6 (n3 -> 2, n5 -> 4, n6 -> 4); miary ksztaltu: skan ramkowej wobec modelu testowej 361,9-601,3 (36 skanow), skan testowej wobec modelu ramkowej 58,2-64,1 (28). Liczby raportu wykonawcy zgodne z surowymi danymi |
| W7 | `ciezki.ps1 -Tor 1` -> `krok_proba_k4.cmd` -> `proba_k4.py B` (skrypt nastepcy; skan z `auto_uklad_r58.skan_syntetyczny`, prawda = uklad i numer zadane przez recenzenta, kandydaci 8 / 10 wczytani wprost): okragla testowa R59 n8 (ziarno 9508) i n9 (9509), pola 100 / 99 / 98 / 97 mm, bez numeru podanego, 3 warianty: bez zaslony, dolek D zasloniety (numer z dolkow 0 albo 1 - niewazny), wszystkie 4 dolki zasloniete; 8 vs 10 kandydatow; 48 przebiegow; kontrola `B2`: kwadraty R59 n2 / n5, pola 99 / 98 / 97, bez numeru i z numerem, 24 przebiegi; wynik `proba_k4.jsonl` | Bez zaslony (8 par): 8 z 8 dobrze i pewnie przy 8 i przy 10 (`numer_z_dolkow`). Z zaslona, pole 100 (4 pary): 4 z 4 dobrze i pewnie przy 8 i 10 (`ksztalt`; miara wobec modelu ramkowej 59,5-64,1). **Z zaslona, pola 99 / 98 / 97 (12 par): 8 kandydatow - 10 dobrze i pewnie (`ksztalt`), 2 zle i pewnie (n8 pole 97); 10 kandydatow - 2 dobrze i pewnie (n9 pole 99, miara 46,7 / 48,2), 10 ZLE I PEWNIE (kwadrat, `dolki_wykluczaja`; miara wobec modelu ramkowej 0-36,5 < 40). 8 z 12 par: przy 8 kandydatach uklad dobry i pewny, przy 10 - zly i pewny.** Kwadraty (`B2`): 24 z 24 dobrze i pewnie; 8 kand. `dolki_wykluczaja` 6 + `numer_podany` 6, 10 kand. `dolki_wykluczaja` 12 |
| W8 | ten sam krok, `proba_k4.py AC` (156 przebiegow): A1 - plytki ramkowe, 6 numerow x 2 ziarna (9110-9161, inne niz wykonawcy), pole 100, 10 kandydatow, bez numeru i z numerem zgodnym; A2 - pola 96 / 94 / 90 / 80, 8 plytek (ramkowa n2 i n5, kwadrat R59 n1 i n4, testowa n8 i n9, kwadrat R54 n3, testowa R54 n9), 10 kandydatow oraz 8 dla ukladow sprzed paczki; C - numer drugiego ksztaltu i inne numery niezgodne, pola 100 i 96 | A1: 24 z 24 uklad dobry i pewny, `numer_z_dolkow` 24, numer = prawda 24 (12 skanow). A2: pole 96 - 16 z 16 dobry i pewny (10 kand.), 12 z 12 (8 kand.); pole 94 - 16 z 16 i 12 z 12; pole 90 - 16 z 16 i 12 z 12 BEZ WYNIKU (`BladWyrownania`: znaleziono 1 albo 2 stozki); pole 80 - 16 z 16 i 12 z 12 bez wyniku (0 stozkow); 48 z 48 par 8 / 10 z ta sama klasa i ukladem; "pewny zly" 0 z 112. C (20 przebiegow): kwadrat R59 z podanym 8 / 9 - 4 z 4 par identycznie przy 8 i 10 (zly uklad; pewny 3 z 4); testowa n8 z podanym 1 - przy 8 kand. zly (kwadrat; pole 96 pewny), przy 10 dobry i pewny (2 z 2 - poprawa); ramkowa n1 z podanym 8 - zly (testowa), pole 100 niepewny, pole 96 PEWNY; ramkowa n6 z podanym 9 - zly niepewny 2 z 2; ramkowa n1 z podanym 2 - dobry, numer wyniku 2 (`podany`), z dolkow 1; z podanym 4 - dobry, numer 1 (`dolki`) |
| W9 | `ciezki.ps1 -Tor 1` -> `krok_proba_d.cmd` -> `proba_d.py` (48 przebiegow, 10:23-10:26): D1 - okragla testowa n8 / n9, dolek D zasloniety, pola 99 i 98, po 3 nowe ziarna, 8 vs 10; D2 - ramkowa n1 / n4, 4 dolki zasloniete, pola 99 i 98, 10 kandydatow; D4 - pole 100, ze skanu usunieta scianka boczna plytki (trojkaty o srodku r >= 49,0 ponizej wierzchu; konstrukcja recenzenta - "skaner patrzacy z gory", nie pomiar skanera): testowa n8 / n9 z zaslona D i bez (8 vs 10), ramkowa n2 / n5 z zaslona 4 dolkow i bez (10) | D1 (12 par): 8 kand. 12 z 12 dobrze i pewnie; 10 kand. pole 99 - 5 dobrze, 1 zle i pewnie; pole 98 - 6 z 6 ZLE I PEWNIE (kwadrat). 7 z 12 par pogorszonych. D2: 8 z 8 dobrze i pewnie (`ksztalt`; skan ramkowej wobec modelu testowej 221-336 mm2 - w te strone roznica jest duza takze bez scianki przy polu 99 / 98). D4 testowa: bez zaslony 2 z 2 par dobrze (`numer_z_dolkow`); z zaslona D: 8 kand. 2 z 2 dobrze i pewnie, 10 kand. 2 z 2 ZLE I PEWNIE (kwadrat). D4 ramkowa: dolki czytelne 4 z 4 dobrze; 4 dolki zasloniete - 4 z 4 KWADRAT, `pewny` = True (z numerem podanym: `wieczorna` nr 2 / `poranna` nr 5 ze zrodlem `podany`) |
| W9a | ten sam krok: `py.cmd -m pytest -q -p no:cacheprovider testy\test_ustawienia.py::test_repo_nie_sledzi_danych_ani_ustawien_maszyny testy\test_uklad_r58.py` (u poprzednika 1 failed / 171 passed w testach paczki: `git ls-files` zakonczone 0xC0000142 - znane zjawisko PC) | 25 passed, kod 0 - blad poprzedniego przebiegu byl srodowiskowy |
| W9b | ten sam krok: `py.cmd Ramki\etap3\odbior_koncowy\narzedzia\t13_higiena.py --repo <PC-katalog>\qc-wt\rec-o1 --od 2537f6f --do HEAD` oraz `--do beddde7` | HEAD 43d78e1: "FAIL (12 naruszen)", kod 1 - 8 x STL > 1024 KB (1079-1246 KB), 2 x `uklad.json` nie-ASCII (71 bajtow kazdy), 2 x CRLF (315 i 365 wierszy); wszystkie w `modele_plytek/okragla_ramkowa_*`. `main` beddde7: "ZAL z odstepstwem O11 (0 naruszen)", kod 0. Zgodne z POTRZEBUJE 1 wykonawcy |
| W10 | wstrzykniecie 1 (kopia `rec-o1`, `plate.py`: przed `uk, wyr, ... = wybrany` wiersz `wybrany, powod, pewny = przeszly[-1], "numer_podany", True`), `pytest testy\test_auto_uklad_r58.py -k "male_pole or kazdy_z_dziesieciu or okragla_testowa or kwadrat_r59"`; potem `git checkout`, `status --short` pusty | 10 failed, 9 passed: padaja testy rozpoznania (6 x `kazdy_z_dziesieciu`, 2 x `kwadrat_r59`, 2 x `okragla_testowa`) - dobrze; `test_male_pole_skanu_nie_daje_pewnego_zlego_ukladu` 5 z 5 PRZECHODZI mimo zepsutego wyboru (uwaga 2) |
| W10a | wstrzykniecie 2 (`ustawienia.py`: uklady ramkowe na POCZATKU `UKLADY_WBUDOWANE`), `pytest testy\test_uklad_r58.py` + `test_kandydaci...` + `test_sciezki_plytek_jedno_zrodlo`; cofniete | 3 failed (2 testy ustawien w `test_uklad_r58.py`, `test_kandydaci_to_wszystkie_uklady_wbudowane`), 23 passed - kolejnosc kandydatow jest pilnowana |
| W10b | wstrzykniecie 3 (1 bajt dopisany do `okragla_ramkowa_poranna/uklad.json` i do `wieczorna_r54/uklad.json`), te same testy; cofniete (`git checkout`; suma pliku znow `ab6e02a0...`) | 2 failed (`test_nowy_plik_modelu_jest_kopia_bajtowa_r58[...poranna/uklad.json]`, `test_dotychczasowe_pliki_modeli_bajtowo_bez_zmian`), 24 passed - sumy sa pilnowane |
| W11 | `py.cmd proba_e.py` (jeden proces, ok. 20 s): plik ustawien bez wierszy ramkowych (8 ukladow - jak instalacja 0.3.1) i tylko z 2 wymaganymi; `samokontrola.main(--ustawienia ... --bez-sieci --json)`; nazwy ramkowe w `session` / `session_rano`; `ocen_k3` / `ocen_k4` na przebiegach bez wyniku | Oba pliki: `[plytki]` po wczytaniu 10 ukladow, ramkowe na 2 ostatnich miejscach, kandydaci w tej samej kolejnosci; samokontrola: "ustawienia" OK ("2 klucze z wartoscia domyslna ([plytki] okragla_ramkowa_wieczorna, [plytki] okragla_ramkowa_poranna)"; dla pliku z 2 ukladami 8 kluczy), "modele" OK "poprawne 10 z 10" (kod samokontroli 1 pochodzi z innych sprawdzen - plik probny ma przykladowe sciezki folderow). `powod_nie_z_trybu("okragla_ramkowa_*", wieczor / rano)` = "nieznany uklad plytki ...", `numery_plytki` None, `na_ramce` False; `opis_ukladu` ramkowej = tekst plytki okraglej testowej. `ocen_k3` (4 przebiegi bez wyniku): `spelnione` True, "1 z 1"; `ocen_k4` (pole 100, 4 z 4 `brak_wyniku`): `spelnione` True (uwaga 3) |
| W12 | przeglad kodu: uzycia `pewny`, `uklad_auto`, `powod` rozpoznania w `aplikacja.py`, `kontroler_api.py`, `session.py`, `session_rano.py`, `indicate.py`, `statusy.py`, `ui/*.py` (Grep) | 0 uzyc - program glowny bierze tylko `wynik["plytka"]`; `pewny` i `powod` czytaja wylacznie `porownaj` (wydruk CLI), `ui_test.py` i `dzien_skanera_rdzen.py`. Zmiana `powod` kwadratow R59 (`numer_podany` -> `ksztalt` / `dolki_wykluczaja`) nie zmienia wiec zachowania programu; z tego samego powodu "niepewny" nie jest dla technika zadna ochrona |

Stan po probach: `git -C <PC-katalog>\qc-wt\rec-o1 status --short` pusty, HEAD 43d78e1; 0 procesow python recenzenta
(`Get-Process python*` puste). Ciezkie kroki recenzenta w `log\ciezkie.log`: 10:08:44-10:14:18, 10:14:41-10:23:31,
10:23:42-10:26:08 (tor 1, kody 0).

## 3. Kryteria zlecenia

| Nr | Kryterium | Ocena | Podstawa |
|---|---|---|---|
| 1 | 10 z 10 sum zgodnych (plik roboczy i obiekt git) | potwierdzone wlasna proba | W1-W3 (10 z 10 w obiekcie git, w zrodle R58 i w drzewie roboczym), 3 z 3 wyrywkowo, W4 (28 z 28 bez zmian), W10b (test pada po zmianie 1 bajtu), W9a |
| 2 | 48 skanow ramkowych: uklad dobry, `pewny`, gniazda = prawda | potwierdzone wlasna proba na probce (uklad, pewnosc, numer) i przeliczeniem surowych wynikow (gniazda) | W8 A1: 24 z 24 na 12 wlasnych skanach (bez ciecia na gniazda); W6a: 48 z 48 z `gniazda_zgodne` w surowych wynikach wykonawcy |
| 3 | BRAMKA: 80 z 80 skanow odniesienia, ten sam uklad i nie gorsza pewnosc, oba tryby | potwierdzone wlasna proba (probka 32 z 80) i przeliczeniem (80 z 80) | W6: 32 z 32 skanow, 64 z 64 par, kandydaci niezaleznie od narzedzia; W6a: 160 z 160 par, zgodny z prawda 160 / 160, zmiana `powod` w 16 parach (14 + 2). Narzedzie liczy uczciwie na tych danych: "8" to 8 dotychczasowych nazw w kolejnosci z `main` (test + W6 na liscie wpisanej recznie), para = ten sam skan i ta sama siatka w pamieci, prawda z pliku `.json` generatora. Slabosc oceny przy braku wyniku: uwaga 3 (nie wystapila) |
| 4 | BRAMKA: 0 "pewny ze zlym ukladem" przy polu 100 / 90 / 80; niepewni wprost | potwierdzone wlasna proba W ZAKRESIE zestawu zlecenia; poza zestawem - uwaga 1 | W8: pole 100 - 24 z 24 dobry i pewny (ramkowe); pola 96 / 94 - 32 z 32 dobry i pewny przy 10 kand.; pola 90 / 80 - 32 z 32 bez wyniku przy 10 i 24 z 24 przy 8; niepewnych 0; W6a: 0 z 264 (i 0 z 176 przy 96 / 94), `brak_wyniku` NIE jest liczony jako dobry (osobna klasa; `spelnione` = brak `zly_pewny` + pelny zestaw). "BEZ WYNIKU przy 90 / 80" opisane uczciwie jako ograniczenie: raport sekcja 1 (zastrzezenie 1: "prawdziwe, ale puste"), sekcja 6, `plate.md:39` punkt (5); dotyczy takze stanu sprzed paczki. Numer niezgodny: liczby 1 / 16 / 15 z 62 i 1 / 16 / 16 z 44 zgodne (W6a), zachowanie istniejace (W8 C: 4 z 4 par kwadratow identycznie przy 8 i 10). NIEUDOWODNIONE i nieprawdziwe poza zestawem: plytka testowa z zaslonietym dolkiem przy polu 99-97 (uwaga 1) |
| 5 | T10: wyrownanie 40 z 40 | potwierdzone przegladem pliku wyniku wykonawcy | `robocze\o1\t10\t10_surowe_metryki.json`: `skanow` 40, `wyrownanie_ok` 40, max 0,014 mm, `uklad_niezgodny` 0; top-1 276 z 276 i falszywe czerwone 0 z 127 - wg wykonawcy, niesprawdzone. T10 nie powtarzano |
| 6 | czas rozpoznania R59: mediana + najwyzej 1,0 s | potwierdzone wlasna proba | W6: + 0,71 s bez numeru, + 0,69 s z numerem (16 skanow R59, kolejnosc na przemian); wykonawca + 0,81 / + 0,75 s (plik `pomiar_k6\auto_uklad_r58.txt` przeczytany) |
| 7 | pelny pytest 0 failed | niepowtarzane (sprawdza koordynator); testy paczki potwierdzone | log wykonawcy: "2275 passed, 9 skipped" (odczyt ostatniego wiersza); testy paczki u poprzednika 171 passed + 1 failed srodowiskowy, powtorka W9a 25 passed. Luka w tescie: uwaga 2 |

Zmiany liczbowe w istniejacych testach (przeglad diffu): `test_auto_uklad.py:220` i `:225`, `test_straznik.py:248`,
`test_uklad.py:78` - we wszystkich 4 miejscach rownosc zbiorow zostala rownoscia, prawa strona rozszerzona o 2 nazwy;
`test_ustawienia.py:47-49` - lista nazw rozszerzona o 2. Zadnej asercji nie oslabiono, 0 skip / xfail, 0 innych zmian
w tych plikach (5 wierszy zmienionych w 4 plikach).

## 4. Zakres plikow i zasady

- Zakres: 22 pliki = 14 nowych z listy zlecenia + 5 zmienianych z listy + 3 testy dopuszczone przez koordynatora
  (`test_auto_uklad.py`, `test_straznik.py`, `test_uklad.py`). 0 plikow spoza zlecenia. `session*.py`, `ramka/**`,
  `indicate.py`, `kontroler_api.py`, `statusy.py`, `ui/**`, `porownaj.py`, `samokontrola.py`, symulator,
  `zbuduj_wydanie.py`, `instrukcje/**`, `Ramki/etap3/**`: 0 zmian.
- Nietykalne: `match.py`, `inspect.py`, `plate.py`, `synth.py`, `uklad.py`, `baza.py`, `raporty/testy_krawedz/**` -
  0 zmian (W5); `ustawienia.przyklad.toml` - jedyna zmiana to 5 dodanych wierszy w `[plytki]` (3 komentarza + 2 uklady),
  sekcje `[match]` / `[inspect]` bez zmian; 28 dotychczasowych plikow `modele_plytek/**` bez zmian (W4); schemat bazy
  bez zmian. Wariantu C nie zaczeto.
- Kopie bajtowe: 10 z 10 = zrodla R58 (W1-W3). 2 x `uklad.json` sa nie-ASCII i CRLF - tak jak zrodla (decyzja
  wlasciciela nr 1).
- Nowe pliki tekstowe (`test_uklad_r58.py`, `test_auto_uklad_r58.py`, `auto_uklad_r58.py`, raport paczki): 0 bajtow
  nie-ASCII, 0 znakow CR (LF). Pliki istniejace zachowaly swoje konce linii (CRLF w `ustawienia.py`: 379 z 379 wierszy).
- Duze dane: 8 STL (ok. 9,2 MB) w `modele_plytek/**` - objete decyzja nr 1; poza tym 0 STL, 0 wynikow pomiarow w gicie.
- Dane osobowe: w diffie i w komunikatach 4 commitow brak nazw zlecen i plikow projektow; raport paczki podaje tylko
  nazwy skanow syntetycznych. Wyniki narzedzia (poza repo) zawieraja sciezke katalogu programu - uwaga 4.
- Commity: 4, przedrostek `E3-O1:`, ASCII, stopka `Co-Authored-By` w 4 z 4.
- **Informacja dla koordynatora (nie uwaga do O1): T13.** `t13_higiena.py` na HEAD 43d78e1 = FAIL, 12 naruszen
  (8 STL > 1024 KB, 2 JSON nie-ASCII, 2 JSON CRLF), na `main` 0 (W9b). Wszystkie w 10 kopiach bajtowych - potrzebny
  wyjatek w T13 dla `Ramki/stanowisko/modele_plytek/okragla_ramkowa_` albo odstepstwo; plikow nie wolno "naprawiac".
- Skutki samej O1 przed O2 (punkt 5 zlecenia recenzji): start z istniejacym `ustawienia.toml` bez nowych wierszy -
  dziala, uklady dopisywane przy wczytaniu na koncu (W11); plik ustawien instalacji lezy poza katalogiem wersji i przy
  aktualizacji nie jest ruszany (`instalacja/instalator.py:9`) - migracji nie trzeba; samokontrola: "modele" 10 z 10,
  "ustawienia" OK z 2 kluczami domyslnymi (W11); kwadraty R59 / R54 i okragle n8 / n9 w warunkach nominalnych - ten
  sam uklad, numer i macierz (W6), czas rozpoznania plytki rodziny R59 + ok. 0,7-0,8 s; zmiana `powod` bez skutku
  w programie (W12). Jedyny znaleziony skutek uboczny: uwaga 1. Plytka okragla ramkowa zeskanowana po O1, a przed O2:
  status "plytka nie z trybu" z powodem "nieznany uklad plytki" (W11) - zachowanie przejsciowe, opisane w raporcie
  wykonawcy (sekcja 9.4, POTRZEBUJE 2).

## 5. Do decyzji wlasciciela

1. **Uwaga 1 (przed scaleniem):** po dodaniu ukladow ramkowych plytka okragla testowa n8 / n9 z nieczytelnym albo
   zaslonietym dolkiem kodu jest rozpoznawana jako KWADRAT z `pewny` = True, gdy skan nie pokazuje scianki bocznej
   plytki (17 z 26 par przy polu 99-97 mm albo bez scianki; przed paczka dobrze). Przy polu 100 ze scianka boczna
   i przy czytelnych dolkach - bez zmiany. Do wyboru: (a) przyjac jako ograniczenie plytek testowych (opis, pomiar
   i test w O1) - wtedy trzeba wiedziec, ze na prawdziwym skanerze, ktory nie widzi scianki bocznej albo dolkow,
   plytki okragle beda rozpoznawane jako kwadraty; (b) wariant C: zmiana reguly ksztaltu w `plate.py` (porownanie
   kolo / kwadrat zamiast dwoch najlepszych ukladow) z pelna regresja - przed O2 / O3 albo razem z nimi.
2. **To samo dla plytek ramkowych po O2 (informacja):** gdy 4 dolki sa nieczytelne i scianki bocznej nie ma w skanie,
   plytka ramkowa jest rozpoznawana jako kwadrat `wieczorna` / `poranna` z `pewny` = True (4 z 4, W9 D4). Gniazda
   i numery sa te same, wiec ramka zaswieci dobrze, ale w bazie bedzie uklad kwadratowy. Przy polu 99 / 98 ze scianka
   ucieta plytka ramkowa byla rozpoznana dobrze (8 z 8).
3. **Zastrzezenia wykonawcy - potwierdzone jako zachowanie istniejace:** (a) numer drugiego ksztaltu wpisany recznie
   (8 / 9 przy n1-n6 albo odwrotnie) = pewny zly uklad 1 / 16 / 15 z 62 (10 kand.) wobec 1 / 16 / 16 z 44 (8 kand.) -
   liczby zgodne z surowymi wynikami, paczka tego nie pogarsza (3 przypadki nowe - plytka ramkowa z wpisanym 8 / 9,
   4 zniknely); (b) zasloniety dolek plytki ramkowej = inny wazny numer 3 z 6 - zgodne; ochrona to porownanie numeru
   z ramki z `numer_z_dolkow` w O2.
4. **Pole skanera:** przy polu 90 mm i mniejszym program nie rozpoznaje zadnej plytki (brak 3 stozkow) - takze dzis
   przy 8 ukladach (24 z 24 w probie recenzenta). Kryterium 4 dla pol 90 / 80 jest wiec spelnione pusto; wykonawca
   opisal to wprost. Pole prawdziwego skanera pozostaje niezmierzone.
5. **T13:** wyjatek dla 10 kopii bajtowych R58 (sekcja 4).
6. **Wydanie:** sama O1 nie nadaje sie do wydania jako "obsluga plytek okraglych ramkowych" - skan takiej plytki jest
   blokowany do czasu O2.

Informacje dla paczek O2 / O3 (z prob recenzenta): (1) `wynik["numer"]` plytki ramkowej bywa 0 ze zrodlem `dolki`
(dolki zasloniete: 4 z 4 w W9 D2 bez numeru podanego; w surowych wynikach wykonawcy 9 z 12 przebiegow bez numeru) -
O2 musi traktowac numer spoza `numery` ukladu jak nieznany;
(2) `pewny` / `powod` nie docieraja do sesji ani ekranu (W12) - ostrzezenie o niezgodnosci numeru trzeba budowac z
`numer`, `numer_zrodlo`, `numer_z_dolkow`; (3) kwadrat R59 z numerem z ramki ma `powod` = `ksztalt` albo
`dolki_wykluczaja` (8 z 8 w W6); (4) `opis_ukladu` nie odroznia plytki ramkowej od testowej (W11); (5) po poprawce
uwagi 3 narzedzie `auto_uklad_r58.py` mozna uzyc ponownie bez zmian - do tego czasu przy ponownym pomiarze czytac
kolumne "zgodny z prawda 8/10 kand.", nie sam wiersz BRAMKA.
