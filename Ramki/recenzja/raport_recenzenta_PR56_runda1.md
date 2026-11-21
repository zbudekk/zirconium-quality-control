# Raport recenzenta PR #56 (E3-O3), runda 1

Data: 2026-11-21, 13:29-13:52 (zegar PC). Zakres: `git -C <PC-katalog>\qc diff main...e3/o3`, `main` = 8001b55,
HEAD = 10a6e22 (6 commitow, 14 plikow, +2062 / -29; ostatni commit z kodem e7bec67).
Metoda: najpierw wlasny przeglad diffu i wlasne proby w kopii `<PC-katalog>\qc-wt\rec-o3` (detached 10a6e22), raport
wykonawcy czytany na koncu. Pliki robocze i logi: `<PC-katalog>\koordynator\robocze\rec-o3\`.
Uruchomiono: porownanie map z kodem `main` (112 map), testy paczki (105), 15 wstrzykniec w kod (16 przebiegow), T13 na galezi
+ 6 wstrzykniec w klonie jednorazowym, samokontrole na odtworzonym ukladzie instalacji (9 wariantow), generowanie 2 skanow
ramkowych, klikniecia w oknie po 4 zmianach rozmiaru. Pelnego pytest i paczki probnej nie powtarzalem (zgodnie ze zleceniem).
Stan po pracy: `git -C <PC-katalog>\qc-wt\rec-o3 status --short` pusty; klon T13, kopia instalacji i skany generowane
usuniete; nic nie zacommitowane ani wypchniete.
STAN: ZAKONCZONA.

## 0. Werdykt

WERDYKT: do scalenia (B 0 / P 0 / D 4)

- Bledow dajacych zly wynik u technika nie znalazlem. Mapa kwadratowa: obraz i trafianie identyczne z kodem `main` (40 z 40).
  Mapa okragla: sciecie po stronie przod-prawo (zgodnie z `flat` i opisem osi w `uklad.json`), klik w kazde gniazdo trafia
  (72 z 72 map na widzecie, 10 z 10 ukladow okna, takze po zmianie rozmiaru okna).
- Samokontrola po aktualizacji z 0.3.1 (stary `ustawienia.toml`): zielona "10 z 10" w 4 z 4 wariantow pliku ustawien.
- Uwagi D nie blokuja scalenia; D1 warto zamknac przy najblizszej zmianie `mapa.py`.

## 1. Uwagi

| Nr | Waga | Plik:linia | Scenariusz | Propozycja |
|---|---|---|---|---|
| D1 | D | `Ramki/stanowisko/testy/test_okragle_ekran.py:107` (`StaryObrys`), `:286` (`test_mapa_kwadratowa_bez_zmian`), `:30` (`GNIAZD` - tylko uklady okragle) | Test "kwadrat: 0 zmian" porownuje obraz z rysunkiem, w ktorym "przed" to kopia samego rysowania obrysu, a przeliczenie mm -> piksele i gniazda pochodza z TEGO SAMEGO badanego kodu; test klikniec z polozeniem niezaleznym obejmuje tylko 4 uklady okragle. Wstrzykniecie J14 (cala mapa kwadratowa odbita lewo-prawo: gniazda i wyciety naroznik po zlej stronie, okragle bez zmian): testy paczki 74 passed, 0 failed. Te sama usterke w testach istniejacych lapie 1 test z 154 (`test_klawiatura_strzalki_enter_tab`, J15) - przypadkiem. Kod paczki jest dobry (W1: obraz i trafianie = `main` 40 z 40) - luka dotyczy przyszlych zmian. Nie P, bo paczka nie zmienila przeliczenia ani gniazd kwadratu, a zmieniona czesc (skladanie obrysu) test lapie (J5: 16 failed). | Dopisac 4 uklady kwadratowe do `test_klik_w_kazde_gniazdo_trafia_w_dobre_gniazdo` (polozenie z mm ukladu na prostokacie plytki, klik = numer gniazda) i asercje, ze wyciecie `notch` lezy po stronie prawo-dol ekranu. |
| D2 | D | `Ramki/stanowisko/stanowisko/samokontrola.py:887`, `:890` | Stary plik ustawien (bez wierszy ramkowych) + niepelny katalog programu: wiersz brzmi "uklady plytek z [plytki]: poprawne 9 z 10 - okragla_ramkowa_poranna: brak katalogu modelu dostarczanego z programem (...)", a rada konczy sie "albo popraw [plytki] w pliku ustawien" - tego ukladu w `[plytki]` nie ma i poprawka pliku nic nie da (S5 w W6). Nazwa ukladu i katalog sa podane, wiec osoba instalujaca wie, czego brakuje. | Przy braku modelu dostarczanego z programem sama rada "zainstaluj program ponownie z paczki wydania"; etykieta "uklady plytek: poprawne N z M". |
| D3 | D | `Ramki/etap3/odbior_koncowy/narzedzia/t2_wieczor.py:224` | Koordynator podaje `--dane-generowane` z plikiem o innym sha16 (np. inna pula projektow): komunikat mowi "sha16 pliku w danych odniesienia (...) inne niz w scenariuszu", choc plik lezy w katalogu skanow generowanych. Kod 2, przebieg nie startuje - bez falszywego wyniku. | Uzyc zmiennej `gdzie` takze w tym komunikacie. |
| D4 | D | `Ramki/stanowisko/instrukcje/wieczor.md:7`, `poranek.md` (obrazek ekranu) - pliki bez zmian | Technik z plytka okragla widzi w instrukcji ekran z mapa kwadratowa (2 obrazki), tekst nie mowi o ksztalcie. Kroki instrukcji (rynienka z przodu, klik w gniazdo, kolory) sa prawdziwe dla obu ksztaltow, a mapa na ekranie ma napis "PRZOD PLYTKI" i sciecie - nie znalazlem zdania, ktore przy okraglej prowadzi do zlej czynnosci. Decyzja wykonawcy "bez zmian" jest dopuszczona zleceniem (punkt 6). | Po testach na sprzecie 28-29.11 wymienic obrazek albo dopisac zdanie kosztem innego (sekcja 5, sprawa 1). |

## 2. Wlasne proby

| Nr | Polecenie / proba | Wynik (liczby z wlasnego pomiaru) |
|---|---|---|
| W1 | `py.cmd robocze\rec-o3\proba_mapa.py` (log `proba_mapa.txt`): `mapa.py` i `mapa_rano.py` z `main` (git show 8001b55) zaladowane obok kodu galezi; 4 uklady kwadratowe x wieczor / rano x rozmiary (700x640, 430x400 - oba takze po zmianie rozmiaru z 900x820, 523x611) | obraz `grab()` identyczny piksel w piksel 40 z 40; siatka trafien `gniazdo_w_punkcie` (co 4 px, caly widzet) identyczna 40 z 40; `sciecie()` None 40 z 40 |
| W2 | to samo narzedzie, 6 ukladow okraglych (testowe R59 / R54, ramkowe) x wieczor / rano x 4 rozmiary (2 takze po zmianie rozmiaru) = 72 mapy | klik w srodek gniazda liczony niezaleznie (mm z ukladu na prostokat plytki z kodu `main`): 19 z 19 (24 mapy), 24 z 24 (24), 20 z 20 (12, R54 wieczorna), 33 z 33 (12, R54 poranna); siatka trafien identyczna z `main` 72 z 72; cieciwa: kat ekranu 45,0 st. (prawo-dol), 49,356 mm od srodka, dlugosc 16,00 mm w 72 z 72; pikseli zmienionych wobec `main` wewnatrz gniazd: 0 w 72 z 72 (najblizszy zmieniony piksel 10,2 px od krawedzi gniazda; najblizsze gniazdo 13,6 mm od cieciwy) |
| W3 | Read: `robocze\rec-o3\mapa_okragla_ramkowa_wieczorna_wieczor.png`, `mapa_okragla_ramkowa_poranna_rano.png` (700x640) | sciecie = gruba kreska w prawym dolnym rogu kola, nad napisem "PRZOD PLYTKI", po tej samej stronie co rynienka nr 1 (przod) i gniazdo 2 (prawo); nie dotyka gniazd ani numerow |
| W4 | `py.cmd -m pytest testy\test_okragle_ekran.py -q -p no:cacheprovider` z `E3_ZRZUTY=robocze\rec-o3\zrzuty` (log `pytest_ekran.log`) | 74 passed w 8,2 s, kod 0; 6 zrzutow okna (wieczor testowa / ramkowa, rano obie; 1920x1080 i 1536x864) |
| W5 | Read: `zrzuty\o3_wieczor_okragla_ramkowa_wieczorna_1536x864.png`, `zrzuty\o3_rano_okragle_1536x864.png` | wieczor: kolo ze scieciem w prawym dolnym rogu nad "PRZOD PLYTKI", 19 gniazd, nic nie uciete; rano: 2 male mapy (n4 ramkowa, n9 testowa), sciecie widoczne w prawym dolnym rogu obu, nie zaslania gniazd 2 / 7 ani rynienki; plytka ramkowa pokazana jako "zablokowana (plytka nie z tego trybu)" - oczekiwane na galezi bez O2 |
| W6 | uklad instalacji odtworzony w `robocze\rec-o3\inst\prog` (kopie `stanowisko/`, `modele_plytek/` 38 plikow, wzor, WERSJA), `py.cmd -m stanowisko.samokontrola --ustawienia <plik> --bez-sieci` uruchamiane Z TEGO katalogu; pliki ustawien: wzor sprzed O1 (`git show 8ae6474^1:...ustawienia.przyklad.toml`, 8 wierszy `[plytki]`), wariant 2 wiersze, wariant 8 sciezek bezwzglednych do innego katalogu, nowy wzor (log `proba_samokontrola.txt`) | program kompletny: `OK modele ... poprawne 10 z 10` w 4 z 4 wariantow pliku ustawien (S1-S4); brak katalogu `okragla_ramkowa_poranna`: `BLAD ... 9 z 10` z nazwa ukladu w 3 z 3 (S5-S7; przy starym pliku z dopiskiem "modelu dostarczanego z programem (modele_plytek/okragla_ramkowa_poranna)"); brak `wieczorna_r54` przy pliku bez wierszy `*_r54`: BLAD 9 z 10 (S8 - nowe zachowanie); katalog ramkowy bez `plytka_n*.stl`: BLAD 9 z 10 (S9). Oceniany tylko wiersz `modele` (pozostale sprawdzenia w katalogu tymczasowym sa czerwone z natury: brak folderow skanera itd.) |
| W7 | T13 na galezi: klon jednorazowy `robocze\rec-o3\t13klon` (`git clone --shared`, bez zdalnego, HEAD 10a6e22), `py.cmd <klon>\...\t13_higiena.py --repo <klon> --do HEAD` (log `proba_t13.txt`, `t13_T0_galaz.txt`) | kod 0, NARUSZENIA 0; "kopie bajtowe R58 ... odstepstwo: decyzja wlasciciela nr 1 z 21.11.2026 ... 10 plikow z 10 na liscie"; wiersz `WYNIK T13: ZAL z odstepstwem O11 (0 naruszen; 7 plikow napisow ekranu nie-ASCII; 10 kopii bajtowych R58 - decyzja wlasciciela nr 1 z 21.11.2026)` |
| W8 | wstrzykniecia T13 w klonie (commit w klonie, po kazdym `reset --hard 10a6e22`): T1 1 bajt w `okragla_ramkowa_poranna/plytka_n5.stl`; T2 1 bajt w `okragla_ramkowa_wieczorna/uklad.json`; T3 11. plik `plytka_n7.stl` w katalogu ramkowym; T4b `plytka_n1.stl` (ta sama tresc i nazwa) w `dane_x/okragla_ramkowa_wieczorna/` i w `modele_plytek/okragla_wieczorna/`; T5 1 bajt + suma w wierszu `KOPIA_R58` dopasowana do zmienionego pliku (lista R58 bez zmian); T6 zmiana kopii po dodaniu, `--od HEAD~1` (status M) | naruszenie wraca w 6 z 6: T1 kod 1, 2 naruszenia ("kopia bajtowa R58: suma ..." + "duzy plik"), odstepstwo 9 z 10; T2 kod 1, 3 naruszenia (suma + nie ASCII + CRLF); T3 kod 1, 1 naruszenie (duzy plik); T4b kod 1, 3 naruszenia (STL poza modele_plytek, 2 x duzy plik), odstepstwo nadal 10 z 10; T5 kod 1, 2 naruszenia; T6 kod 1, 1 naruszenie (status M) |
| W9 | `py.cmd narzedzia\symulator_skanera.py --tylko-generuj --scenariusz ..\etap3\odbior_koncowy\narzedzia\t2_scenariusz_okragle.json --katalog-generowanych robocze\rec-o3\gen --projekty <PC-katalog>\app\Prace_test` (17 STL; inna sciezka puli niz u wykonawcy; log `generowanie.log`) | kod 0, "skany generowane zgodne ze scenariuszem: 2 z 2"; sha16 a7e5c5c7674cc140 (nr 1) i 13a7fc0c4e281de4 (nr 10) = scenariusz = kopie wykonawcy w `robocze\o3\t2_ramkowe` (sha256sum 4 plikow STL: 2 pary identyczne) |
| W10 | wstrzykniecia seria 1 (`robocze\rec-o3\wstrz.ps1 -Seria 1`, log `proba_wstrzykniecia.txt`; po kazdym `git checkout -- plik`, test: `testy\test_okragle_ekran.py`) | WYKRYTE 8 z 8: J1 sciecie odbite lewo-prawo (33 failed), J2 obrys z krotszego luku (42 failed), J3 gniazda odbite przod-tyl (22 failed - tylko testy map okraglych), J4 srodek gniazda przesuniety o 12 mm (16 failed), J5 kwadrat: promien zaokraglenia 6 -> 9 px (16 failed), J6 kreska sciecia 60 px (4 failed), J7 opis ramkowa / testowa zamienione (1 failed), J7b sciecie tylko dla ramkowych (23 failed) |
| W11 | wstrzykniecia seria 2 (`wstrz.ps1 -Seria 2`; test: `testy\test_okragle_wydanie.py -k ...`) | WYKRYTE 6 z 6: J8 samokontrola pomija uklady ramkowe (3 failed), J9 brakujacy uklad poza licznikiem (3 failed), J10 T13 bez liczenia sumy pliku (2 failed), J11 T13 wyjatek takze dla 11. pliku `plytka_n7.stl` (2 failed), J12 symulator: tabela prawdy liczy kazda prace jako ubytek (2 failed), J13 sterownik T2: pozycje bez `zrodlo` z `--dane-generowane` (1 failed); kontrola po cofnieciu: oba pliki testow paczki 105 passed w 33,4 s |
| W12 | `py.cmd robocze\rec-o3\prawda.py` - plik prawdy generatora z mojego generowania (W9) czytany niezaleznie od `tabela_prawdy` symulatora (log `proba_prawda.txt`) | nr 1: 9 prac, z ubytkiem gniazda [1, 2, 3, 4, 6, 8] (11 ubytkow), bez [5, 9, 10] - tabela scenariusza zgodna; nr 10: 10 prac, 0 z ubytkiem - zgodna; 8 z 8 pozostalych pozycji = stary scenariusz slowo w slowo; nr 8 sha16 247ee785f428396f jest; stary `t2_scenariusz.json`: sha256 na `main` = na galezi (700b84fb...) |
| W13 | wstrzykniecia seria 3 pod blokada (`ciezki.ps1 -Tor 2 -Kto rec-o3 -Polecenie robocze\rec-o3\seria3.cmd`, log `seria3.log`): cala mapa kwadratowa odbita lewo-prawo (zmiana w funkcji mm -> piksele tylko dla `shape != "round"`) | J14 testy paczki (`test_okragle_ekran.py`): NIEWYKRYTE - 74 passed, 0 failed; J15 ta sama zmiana, testy istniejace (`test_ui_wieczor.py`, `test_ui_rano.py`, `test_p14_ekran.py`): WYKRYTE - 1 failed (`test_klawiatura_strzalki_enter_tab`), 153 passed w 159 s. Uwaga D1 |
| W14 | `py.cmd robocze\rec-o3\proba_okno.py` (log `proba_okno.txt`): okno wieczorne z plytka okragla ramkowa n1 i testowa n8, start 1920x1080, potem zmiany rozmiaru okna 1536x864 -> 1280x720 -> 1920x1080 -> 1366x768; po kazdej klik w kazde gniazdo, polozenie z mm ukladu | klik 19 z 19 w 10 z 10 ukladow okna (2 plytki x 5 rozmiarow); sciecie w cwiartce prawo-dol 10 z 10; cala plytka w widzecie mapy 10 z 10; `sprawdz_uklad` bez usterek 10 z 10. (Pierwszy przebieg proby dal 17 z 19 przy starcie plytki ramkowej - blad mojej proby: polozenia policzone raz, zanim okno skonczylo sie ukladac; po liczeniu polozenia przy kazdym kliknieciu, jak w tescie paczki, 19 z 19.) |
| W15 | przeglad statyczny: `git diff --name-status`, `git ls-files --eol`, Grep | 14 plikow, wszystkie z listy zlecenia; 0 plikow PNG / ZIP / STL; konce linii w indeksie: LF 13 z 14, `porownaj.py` CRLF jak na `main` (plik istniejacy); nie-ASCII tylko `porownaj.py` (plik istniejacy z polskimi znakami); `porownaj.py`: 1 fragment zmian, caly w `opis_ukladu`; stary `t2_scenariusz.json` bez zmian (sha256 rowne); testow istniejacych zmienionych: 0; `metryki.py`: 3 trafienia slowa "uklad" (nazwy statusow), 0 odwolan do kolumny `skany.uklad`; `opis_ukladu` trafia w 2 miejsca: `porownaj.py:688` (konsola) i `ui_test.py:422` (okno proby); 6 commitow `E3-O3: ...`, stopka Co-Authored-By 6 z 6 |

Wstrzykniecia w kod razem (W10, W11, W13): 15 roznych zmian, 16 przebiegow. Testy paczki wykryly 14 z 15; pietnasta (J14 -
odbicie mapy kwadratowej) przeszla testy paczki i zostala wykryta dopiero przez 1 test istniejacy (J15) - uwaga D1.
Wymagane minimum 5 (sciecie, trafianie klikow, opis ukladu, samokontrola, wyjatek T13): 5 z 5 wykryte testami paczki.

## 3. Kryteria zlecenia

| Nr | Kryterium | Ocena | Dowod |
|---|---|---|---|
| 1 | Mapa okragla ze scieciem przod-prawo z pola `flat`; klik 19 z 19 i 24 z 24; kwadrat 0 zmian | potwierdzone wlasna proba | W1 (kwadrat = `main` 40 z 40 obrazow i 40 z 40 siatek trafien), W2 (72 mapy okragle: kliki, cieciwa 45,0 st. / 49,356 mm / 16,00 mm, 0 pikseli w gniazdach), W3 i W5 (zrzuty), W14 (okno po zmianie rozmiaru), J1-J6, J7b. Orientacja: `flat.angle_deg` = -45 st. od +X, os y "do tylu" (`coords` w `uklad.json`: "przod-prawo, jak dawny naroznik D"; `R57_wdrozenie_zmiany.md:42` "kierunek normalnej sciecia od +X (przod-prawo)"; `R58_wdrozenie_zmiany.md:199` sciecie 49,356), mapa rysuje y w gore ekranu - sciecie wypada w prawym dolnym rogu, tam gdzie wyciety naroznik kwadratu (`notch` x 43..48, y -48..-43) i nad napisem "PRZOD PLYTKI"; ta sama funkcja dla mapy wieczornej i porannej (`MapaRano` dziedziczy obrys, `mapa_rano.py` bez zmian). Kreska 5 px: nie zmienia trafiania (siatka trafien = `main` 72 z 72) i nie zaslania gniazd ani numerow |
| 2 | `opis_ukladu` odroznia ramkowa od testowej; teksty nie obcinaja sie przy 1536 x 864 | potwierdzone wlasna proba | W4 (testy paczki, w tym okno proby 1536 x 864), J7, W15 (2 miejsca uzycia). Teksty: "okragla ramkowa (do ramki)" / "okragla testowa (poza ramka)" - proste; kwadrat bez zmian |
| 3 | Samokontrola "10 z 10", test na 10 ukladow, komunikat z nazwa brakujacego modelu | potwierdzone wlasna proba | W6 (S1-S9), J8, J9; log instalacji probnej wykonawcy `robocze\o3\samokontrola_instalacji.txt`: "OK modele ... poprawne 10 z 10", "SAMOKONTROLA: ZIELONA" |
| 4 | Symulator podaje skan ramkowy; scenariusz 10 plytek z 2 ramkowymi i tabela prawdy; nr 8 zostaje; skany powtarzalne; sterownik - opcja, domyslnie bez zmian | potwierdzone wlasna proba (pelny T2 - poza ta galezia, robi koordynator) | W9 (te same sha16 z innej sciezki puli), W12 (tabela prawdy = plik generatora; 8 z 8 pozycji bez zmian; nr 8 jest), J12, J13, W15. Falszywe zaliczenie: w probie skroconej wykonawcy (`robocze\o3\t2_proba1.log`) 2 plytki ramkowe zablokowane przez sesje maja "zgodne: NIE" i werdykt "FAIL (1 z 3)" - sterownik nie liczy plytki zablokowanej jako obsluzonej; brak `--dane-generowane`, inne sha16 albo inna tabela prawdy = kod 2 przed startem (przeglad kodu + testy paczki). Symulator bez nowych opcji: przeglad diffu (`--folder` nadal wymagany poza `--tylko-generuj`, kod 2; lista zrodel bez zmian, gdy nie ma `--generuj` / `--scenariusz`) |
| 5 | Metryki i raporty: nowa wartosc `skany.uklad` niczego nie psuje; test na bazie z 2 skanami ramkowymi | potwierdzone przegladem + testy paczki | W15 (Grep), W11 (2 testy metryk w 105 passed) |
| 6 | Instrukcje: przeglad obrazkow, zmiana tylko gdy wprowadzaja w blad | potwierdzone przegladem | D4; decyzja "bez zmian" dopuszczona zleceniem; tekst `wieczor.md` przeszukany - 0 zdan zaleznych od ksztaltu plytki; obejrzalem 1 obrazek (`robocze\o3\instrukcje_obrazki\wieczor_1.png`: mapa kwadratowa, wyciety naroznik w prawym dolnym rogu nad "PRZOD PLYTKI" - ta sama strona co sciecie na mapie okraglej); pozostale wg wykonawcy (2 z 9 pokazuja plytke kwadratowa) |
| 7 | T13: wyjatek waski, 0 naruszen, odstepstwo z nazwa decyzji, 1 bajt = naruszenie | potwierdzone wlasna proba | W7, W8 (6 z 6), J10, J11 |
| 8 | Paczka: 38 plikow modeli; instalacja probna 10 -> 0, samokontrola zielona | potwierdzone przegladem logow wykonawcy (nie powtarzane - zakaz budowy) | `robocze\o3\zip_proba.txt` (222 wpisy, `program/modele_plytek/` 38 plikow w 10 katalogach), `instalacja_1.log` (kod 10), `instalacja_2.log` ("INSTALACJA: GOTOWA"), `kody.txt` (trzeci przebieg: 10, potem 0), `<PC-katalog>\t0\o3` usuniety (sprawdzone: brak katalogu); testy skladu paczki przechodza u mnie (W11). Liczby 222 / 142 / 141 sa "wg wykonawcy". Instalacja probna byla PIERWSZA instalacja - aktualizacji z 0.3.1 instalatorem nikt w tej paczce nie probowal (moje W6 to sama samokontrola) |
| 9 | Pelny pytest 0 failed | wg wykonawcy i koordynatora, niesprawdzone przeze mnie | 2394 passed / 9 skipped / 0 failed na e7bec67 (ostatni wiersz `robocze\o3\pytest_e7bec67.log` przeczytany: "2394 passed, 9 skipped, 1 warning in 1990.46s"); moje: testy paczki 105 passed |
| 10 | Wstrzykniecia min. 5 | potwierdzone wlasna proba | wykonawca: 19 z 19 wg `robocze\o3\wstrzykniecia.txt` i `wstrzykniecia2.txt` (1 niewykonane w pierwszym skrypcie, powtorzone w drugim); moje: 15 zmian, w tym 5 z 5 wymaganych rodzajow wykryte |

Zgodnosc z paczkami rownoleglymi (punkt 7 prosby koordynatora): listy plikow O3 i O2 oraz O3 i O4 sa rozlaczne (0 wspolnych
plikow w `git diff --name-only`). `test_okragle_wydanie.py` liczy tylko wpisy `modele_plytek/` (38) - pliki `ramka/rpi/*`
i `instalacja/wzory/Dzien_skanera.cmd` z O4 ich nie zmieniaja; funkcje `zbuduj_wydanie` uzywane w tescie (`pliki_z_gita`,
`zbuduj`, `sprawdz_zip`, `wczytaj_liste`, `LISTA_PROGRAMU`) maja na `e3/o4` te same sygnatury co na `main`. W testach
`e3/o2`, `e3/o4` i instalatora nie ma asercji na tekst "poprawne 8 z 8". Testow O3 na drzewie scalonym nie uruchamialem
(w `qc-wt\integ` biegnie pelny pytest koordynatora: o 13:43 57 %, 0 niepowodzen w logu).

## 4. Zakres plikow i zasady

- Zakres: 14 z 14 plikow na liscie zlecenia (w tym `t2_wieczor.py` - opcja `--dane-generowane`, zachowanie domyslne bez zmian).
  Nietykalne (`match.py`, `inspect.py`, `plate.py`, `synth.py`, `uklad.py`, `modele_plytek/**`, schemat bazy), `instrukcje/**`,
  `Ramki/etap3/wydania/**`, `Ramki/etap3/t14/**`, `t2_scenariusz.json`, `WERSJA`: 0 zmian. Pliki O2 i O4: 0 zmian.
- Testy istniejace: 0 zmienionych. Nowe testy: 105 (74 + 31), 0 skip / xfail.
- ASCII / LF: 4 nowe pliki kodu i testow oraz raport - ASCII i LF; pliki zmieniane w swoim stylu. PNG / ZIP / STL w diffie: 0.
  Skany, zrzuty, paczka probna - poza repo.
- Dane osobowe: w diffie i w raporcie paczki tylko sha16, nazwy ukladow i dane sztuczne - nazw zlecen nie znalazlem.
- Commity: 6, przedrostek `E3-O3:`, po polsku bez znakow diakrytycznych, stopka 6 z 6. Commit 2be3322 zawieral testy przed
  kodem (opisane w raporcie paczki) - stan koncowy zielony.
- Raport paczki zgodny z tym, co zmierzylem (sha16 skanow, liczby T13, "10 z 10", opis zrzutow); odstepstwa opisane wprost.

## 5. Do decyzji wlasciciela

1. Instrukcje technika pokazuja tylko plytke kwadratowa (D4): zostawic do testow na sprzecie i wtedy wymienic obrazek /
   dopisac zdanie (zalecenie wykonawcy i moje), czy zmieniac juz teraz (wymaga skrocenia innego zdania: wg wykonawcy
   625 slow przy limicie 630).
2. Wyglad sciecia na mapie: pogrubiona kreska 5 px na cieciwie (prawdziwe 0,64 mm to 2-4 px w skali mapy). Na zrzutach
   czytelne takze na malej mapie porannej; czy tak ma zostac - do obejrzenia na laptopie stanowiska.
3. Samokontrola: brak modelu ukladu dostarczanego z programem = BLAD, takze dla `*_r54` (wczesniej przy pliku ustawien bez
   tych wierszy bylo zielono). Przy instalacji z paczki nie tworzy to nowych "czerwonych" przypadkow: brak pliku modelu i tak
   zglasza sprawdzenie `sumy` ("brak <plik>", `samokontrola.py:1241`). Do potwierdzenia jako zachowanie docelowe.
4. Pozycja 8 scenariusza T2 (znany FAIL czesci e) zostaje takze w nowym scenariuszu - nowy T2 moze nie dac kompletu.

Dla koordynatora (nie wymaga wlasciciela): po scaleniu O2 + O3 + O4 proba aktualizacji 0.3.1 -> nowe wydanie na prawdziwej
paczce ze starym `ustawienia.toml` (u mnie tylko samokontrola na odtworzonym ukladzie katalogow: "10 z 10"); pozycje
"POTRZEBUJE" z raportu paczki (`POKAZ_G3.md:140` "8 z 8", `README.md:23` "osiem ukladow", liczby paczki w `PLAN_TESTOW.md`).
