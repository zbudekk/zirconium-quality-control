# Raport recenzenta - PR #55 (E3-O2), runda 3 (recenzja przyrostowa, ostatnia)

Data: 21.11.2026 (17:17-17:30). Zakres: commity po 7ebb5cd na galezi `e3/o2`, HEAD = 1f02673: f5fe6f1 (kod, testy,
`indicate.md`), 1f02673 (raport). Metoda: przeglad `git diff 7ebb5cd e3/o2` (6 plikow), wlasne proby w kopii
`<PC-katalog>\qc-wt\rec-o2` (detached 1f02673), raport wykonawcy (sekcja 20 i sprostowania w 19.2, 19.5, 19.6) czytany
po przegladzie kodu i testow. Pliki robocze: `<PC-katalog>\koordynator\robocze\rec-o2\` (`proby_r3.py`, `okno_r3.py`,
`wstrzyk_r3.ps1`, `wstrzyk_r3b.ps1`, logi `*_r3*.log`, zrzuty `zrzuty\r3_*.png`). Uruchomiono: testy paczki (66),
6 plikow testow modulow dotknietych (260), 18 prob kontrolera z 2 atrapami ramek, 7 opisow bledu analizy, 5 zrzutow okna
offscreen 1536 x 864 (4 obejrzane), 9 wstrzykniec (7 nowych + 2 powtorzone z rundy 2). Pelnego pytest nie powtarzalem.

STAN: ZAKONCZONY.

## 0. Werdykt i liczby

WERDYKT: do scalenia (B 0, P 0, D 3 nowe: D9, D10, D11; D4 z rundy 1 bez zmian - decyzja wlasciciela).

- P2, P3, P4 rundy 2: zamkniete (dowody w 0a). D6, D7, D8 i dodatek koordynatora (stolik w bledzie analizy): zrobione.
- Jedyna zmiana zachowania w rundzie 3 (P4) nie wysyla do ramki niczego: 0 dodatkowych wywolan `wynik()` klienta ramki W
  przy "Zmien numer" 2 -> 3 -> 2 (proba Y2); zmienia sie tylko to, ktory komunikat widac. D7 zmienia, ktory z dwoch
  komunikatow rano widac przy skanie okraglej testowej bez numeru. Niczego innego na ramce runda 3 nie zmienia.
- Bledow wprowadzonych poprawkami nie znalazlem.
- **Stanowisko do decyzji koordynatora w sprawie P2 (wariant "dwie rozne plytki o tym samym numerze z roznymi pracami"
  zostaje bez zmiany kodu):** decyzji nie rozstrzygam ponownie i NIE uwazam, ze blokuje ona scalenie. Powody: (1) to
  mechanizm obecny na `main` dla kwadratow - scalenie paczki nie tworzy nowej klasy bledu, rozszerza znana na plytki
  okragle; (2) po rundzie 3 testy, opis modulu i raport mowia o nim prawde, bez lagodzenia (0a, wiersz P2); test stanu
  faktycznego pada, gdy zachowanie sie zmieni (wstrzykniecie K8); (3) program nie pracuje produkcyjnie. Zastrzezenie,
  ktore powinno trafic do dokumentu dnia sprzetu i do wlasciciela razem z zasada pracy: zasada "zdejmij poprzednia
  plytke z ramki przed skanem nastepnej" NIE wystarcza sama w jednym przypadku - okragla z dolkiem odczytanym jako numer
  innej plytki, a potem TAMTA plytka polozona z powrotem na ramce: swieci pod nia wynik nowego skanu, bez pytania i bez
  komunikatu (proba X1d: 120 px, 0 pytan, 0 komunikatow; mechanicznie to samo co "nowy wsad na tej samej plytce").
  Jedyny sygnal dla technika: na liscie plytek zmiany sa dwa kafelki z tym samym numerem. Dlatego pozycja nr 1 listy
  wlasciciela musi byc rozstrzygnieta przed praca produkcyjna z plytkami okraglymi, nie tylko "po testach na sprzecie".
- Pelny pytest na f5fe6f1: wg logu wykonawcy `robocze\o2\r3\pytest_f5fe6f1.log` (odczyt o 17:23, nie moj pomiar)
  ostatni wiersz "2506 passed, 9 skipped, 2 warnings in 1981.79s", 0 wierszy FAILED / ERROR; w `kody.txt` kod wyjscia
  -1073740791 (0xC0000409) - znane zjawisko PC po wierszu podsumowania; ocena nalezy do koordynatora.

## 0a. Uwagi rundy 2 (i rundy 1): zamknieta / otwarta + dowod

| Uwaga | Stan | Dowod (moje proby na 1f02673) |
|---|---|---|
| P2 | zamknieta (prawda w testach i opisach; zachowanie bez zmian - decyzja koordynatora, lista wlasciciela nr 1) | Test `test_r3_p2_inna_plytka_nr_2_z_innymi_pracami_..._mechanizm_zastany` (2 warianty: okragla z dolkiem odczytanym jako 2; kwadrat nr 2): 2 passed; wydruk z `-s`: w obu wariantach rozpoznane projekty 8 i 4, wspolne 0, pytan 0, komunikatow 0, 9 gniazd, 120 pikseli. Test sprawdza obraz ramki piksel po pikselu wobec wyniku NOWEGO skanu, `_w_wynik == (b, 2, "wyslany", None)`, 0 pytan i 0 komunikatow przez 0,8 s, oba skany aktywne z numerem 2 (liczby 9 / 120 nie sa wpisane w asercje - asercja to zgodnosc pikseli + `swieci >= 5`). Moje X1, X1b: 120 px, 0 pytan, 0 komunikatow (jak w rundzie 2). Wstrzykniecie K8 (twardsza regula: ramka wstrzymana przy kazdym innym aktywnym skanie o tym numerze): 2 failed - test padnie, gdy zachowanie sie zmieni. Opisy 3 testow `test_r2_b1_*`: dopisane "WARIANT Z PYTANIEM ... te same projekty skanu sztucznego" i odeslanie do testu bez pytania - prawdziwe. `indicate.md:218-243`: kiedy pytanie powstaje (ten sam plik / mniej niz 3 projekty / te same prace - zgodne z `session.py:957-970`), "dwie ROZNE plytki ... z ROZNYMI pracami NIE sa wstrzymywane", 4 warianty bez pytania + "Nie" bez zdjecia plytki, "wstrzymanie chroni tylko: ...", zasada pracy - komplet, bez lagodzenia. Raport: sprostowania w 19.2, 19.5 p. 1 ("zasada pracy obowiazuje ZAWSZE"), 19.6 poz. 1 i 7, sekcja 20.2 i 20.5 poz. 1 - prawdziwe (H2: R59 + R54 bez pytania takze przy tych samych projektach - potwierdzone, 0 pytan; H3: 27 px). Drobiazg: D10. |
| P3 | zamknieta | Tekst prawdziwy w 3 przypadkach (atrapa ramki): (1) te same prace drugi raz, plytka lezy -> komunikat, 0 px -> "Tak, to ponowny skan" -> 120 px wyniku nowego skanu, stary skan `zastapiony` (Y1c, G1); (2) nowy maly wsad (2 prace) na tej samej plytce nr 2 -> pytanie + komunikat, 0 px -> "Nie, to nowy wsad" -> 18 px = 2 gniazda nowego wsadu, poprzedni skan zostaje aktywny i `przyjety` (NIE zastapiony) - plytka zdjeta do skanu i polozona (Y1) i plytka lezaca caly czas (Y1b); (3) inna plytka na ramce -> zdjecie + "Nie" -> 0 px, takze po polozeniu plytki nr 2 i nr 3 (H1_nie_po_zdjeciu). Okno 1536 x 864 (`r3_w1`): panel 966 x 132 px, 4 wiersze, pod pytaniem z oboma przyciskami; mapa 19 gniazd, legenda, "Zmien numer" w calosci, bez obciec. Kryterium komunikatu = kryterium pytania ("te same prace"). Wstrzykniecie K1 (rada dla nowych prac prowadzi do "Tak"): 1 failed. |
| P4 | zamknieta | X5: po "Zmien numer" 2 -> 3 przy otwartym pytaniu: pytania [], komunikaty tylko `numer_niezgodny`, 0 px, `_w_wynik = (2, None, "bez_numeru", None)` (runda 2: zostawal `dwa_skany_numeru`). X5b: plytka 2 lezy / zdjeta / plytka 3 / plytka 2 ponownie - w kazdym kroku tylko `numer_niezgodny`, 0 falszywych rad "Poloz plytke nr 2", 0 px. Okno (`r3_w1b`): panelu "Dwa skany ..." nie ma, jest "Plytka 3: Numer plytki nie zgadza sie ze skanem". Y2: powrot numeru 3 -> 2: pytanie wraca, komunikat `dwa_skany_numeru` wraca, 0 px; liczba wywolan `wynik()` klienta W w calej drodze 2 -> 3 -> 2: 0; po "Tak": 1 wywolanie, 120 px. Y3: po zmianie numeru trzeci skan (plytka 1) - komunikat (b) mowi o plytce nr 1 (prawda), po polozeniu plytki 1 swieci jej wynik (75 px). Przeglad wszystkich uzyc `_w_wynik` (`kontroler_api.py:1279` poczatek, `:2196-2207` odczyt do komunikatow, `:2713-2714` poprawka, `:2718` zapis po wyslaniu): poprawka zmienia tylko pole [3], dziala tylko dla biezacego skanu i tylko gdy obraz sie nie zmienil (czyli numer None przed i po, odpowiedz ramki `bez_numeru`); pole [3] czyta wylacznie kod komunikatow (b) i `dwa_skany_numeru`. Wstrzykniecie K3 (zly warunek skanu): 2 failed. Luka: D9. |
| D6 | zamknieta | 2 testy `test_r3_d6_*`; powtorzylem swoje wstrzykniecia J2 i J9 z rundy 2 (wtedy 6 passed): teraz 1 failed kazde (padaja wlasnie testy D6). Test "spoza stanu doby" jest testem funkcji na obiektach zastepczych - wystarcza. |
| D7 | zamknieta | P1c (2 skany bez numeru): "sa skany bez numeru plytki: jesli jeden z nich to skan tej plytki ..." + "Jesli tej plytki jeszcze nie skanowano - zeskanuj ja."; po numerze dla 1. skanu liczba pojedyncza. P1f, Y6 (jedyny skan bez numeru = okragla testowa): `plytka_bez_skanu` "Zeskanuj plytke nr 6", 0 komunikatow `plytka_czeka_na_numer`; Y6 (testowa + 1 kwadrat): liczba pojedyncza (testowa sie nie liczy), (testowa + 2 kwadraty): mnoga; po podaniu numeru 51 px. Plan pieca i lista plytek, z ktorych liczy sie skany, pochodza z tego samego pieca (`kontroler_api.py:2584-2590`, `session_rano.py:1300-1304`). Wstrzykniecie K5 (zawsze liczba mnoga): 2 failed. Okno: D11. |
| D8 | zamknieta | `test_aplikacja_rano.py:867-870`, `:883-884` (asercje w `:868` i `:883`): 5 wierszy dodanych, 3 usuniete, tylko 2 miejsca latki; warunek zamieniony na asercje obecnosci pytania. Wstrzykniecie K7 (pytanie o ponowny skan przestaje powstawac dla tych samych prac): test k4 pada na `assert pyta == (i >= 3)` (`:868`). Plik w serii modulow: passed. |
| Dodatek (stolik) | zrobiony | Tekst z druga przyczyna tylko dla 0 z 3 (7 opisow: "znaleziono 0 ..." w zapisie bez i z polskimi znakami -> stolik; 1 z 3, 2 z 3, "wierzch", "pusty", opis nieznany -> bez stolika). Okno (`r3_b`): czerwony panel 966 x 111 px, 3 wiersze, tekst w calosci (331 znakow). Tresc: druga przyczyna podana jako mozliwosc ("albo w skanie jest stolik (podloze) wokol plytki"), rada "ustaw ciecie skanu powyzej stolika" - zgodna z dodatkiem koordynatora; prawdziwosc przyczyny opiera sie na pomiarze koordynatora (11 z 11), ktorego nie powtarzalem. Wstrzykniecie K6 (stolik takze dla 1 z 3): 2 failed. |
| B1 (runda 1) | bez zmian wobec rundy 2: zamknieta w wariancie Z pytaniem; wariant BEZ pytania = lista wlasciciela nr 1 | G1, H1, X6 jak w rundzie 2 (0 px do odpowiedzi; po "Tak" 120 px). |
| P1 (runda 1) | zamknieta | testy `test_r2_p1_*` w 66 passed; P1c, P1f wyzej. |

## 1. Uwagi rundy 3

| Nr | Waga | Plik:linia | Scenariusz -> co sie dzieje | Propozycja |
|---|---|---|---|---|
| D9 | D | `stanowisko/kontroler_api.py:2713-2714`; testy `test_r3_p4_*` | Poprawka P4 dziala w obu kierunkach (numer wstrzymany N -> brak i brak -> N), testy sprawdzaja tylko pierwszy. Wstrzykniecie K4 (aktualizacja tylko na "brak wstrzymania"): 16 passed. Drugi kierunek wystepuje, gdy technik poprawi numer na inny, a potem wroci do numeru z pytaniem (Y2: komunikat `dwa_skany_numeru` wraca - kod poprawny). Bez tego kierunku ramka i pytanie zachowuja sie tak samo, brakowaloby tylko komunikatu objasniajacego. | Jedna asercja wiecej w `test_r3_p4_zmien_numer_...`: powrot numeru na 2 -> komunikat wraca. Niekonieczne przed scaleniem. |
| D10 | D | `raporty/E3-O2_2026-11-21.md:591-603` (19.3), `:618-621` (19.5 p. 1, poczatek) | Sekcja 19.3 raportu nadal podaje teksty `dwa_skany_numeru` i `plytka_czeka_na_numer` w brzmieniu rundy 2 bez znaku "nieaktualne - patrz 20.3", a 19.5 p. 1 zaczyna sie od rady rundy 2 ("jesli to ta sama plytka zeskanowana drugi raz - Tak") i dopiero nizej ma sprostowanie. Kto przepisze 19.3 / poczatek 19.5 p. 1 do dokumentu dnia sprzetu, wezmie stary tekst (ten z wada P3). | Dokument dnia sprzetu brac z 20.3 i ze sprostowan; ewentualnie dopisek "nieaktualne" w 19.3 (sam raport). |
| D11 | D (do oceny na sprzecie; `ui/**` poza zakresem) | `stanowisko/statusy.py:466-469`; okno - obszar paneli | Rano, 2 skany bez numeru + plytka na ramce P: dwa pytania "Podaj numer plytki" (po 145 px) zajmuja obszar paneli; z komunikatu `plytka_czeka_na_numer` (111 px, o 21 px wyzszy niz w rundzie 2) widac tytul "Plytka na ramce czeka na numer skanu" i gorna czesc 1. wiersza, reszta po przewinieciu (zrzut `r3_r2`; obszar ma pasek przewijania). Zachowanie okna zastane - przy 2 pytaniach tekst rundy 2 tez by sie nie miescil. Waga D, bo to, co technik ma zrobic (wybrac numer), jest w pytaniach widocznych w calosci, tytul komunikatu jest widoczny, a blokada "Zamknij piec" mowi to samo. Przy 1 skanie bez numeru komunikat widac w calosci (`r3_r1`: 966 x 111 px pod 1 pytaniem). | Zostawic; obserwowac na sprzecie (lista wlasciciela nr 7). |

## 2. Wlasne proby

| Nr | Polecenie / proba | Wynik |
|---|---|---|
| 1 | `py.cmd -m pytest -q -p no:cacheprovider testy\test_okragle_sesja.py testy\test_okragle_ramka.py` (log `p1_testy_paczki_r3.log`) | 66 passed w 65,8 s (kod 0) |
| 2 | `py.cmd -m pytest -q -p no:cacheprovider testy\test_ponowny_skan.py testy\test_okragle_ekran.py testy\test_o4_test_led.py testy\test_instrukcje.py testy\test_aplikacja_rano.py testy\test_ramka.py` (log `moduly_rec_r3.log`) | 260 passed w 68,4 s (kod 0); `test_kontroler_api.py` nie uruchamialem (wg wykonawcy w serii 344 passed - niesprawdzone) |
| 3 | `py.cmd -m pytest -q -s ... -k r3_p2` (log `p2_wydruk_r3.log`) | 2 passed; wydruk: 9 gniazd, 120 pikseli, pytan 0, komunikatow 0 w obu wariantach |
| 4 | `proby_r3.py` - kontroler `AtrapaKontrolera` + prawdziwi klienci ramek + 2 atrapy ramek, 18 prob (11 powtorzonych z rundy 2 + X1d + 6 nowych Y*), log `proby_r3.log` | P2: X1, X1b - 120 px wyniku nowego skanu pod plytka lezaca, 0 pytan, 0 komunikatow; H2 (R59 + R54) i H3 (numer z bledem, 27 px) bez zmian; X1d (plytka nr 2 zdjeta przed skanem, skan z numerem 2 i innymi pracami, plytka nr 2 polozona) - 120 px wyniku nowego skanu, 0 pytan, 0 komunikatow. P3: Y1c, G1 ("Tak") 120 px; Y1, Y1b ("Nie", nowy maly wsad) 18 px, poprzedni skan aktywny; H1_nie_po_zdjeciu 0 px. P4: X5, X5b - 0 komunikatow `dwa_skany_numeru` i 0 komunikatow (b) po "Zmien numer"; Y2 - 0 wywolan `wynik()` w drodze 2 -> 3 -> 2, komunikat wraca z pytaniem; Y3 - nastepny skan dziala zwyczajnie. X6 (kwadrat, numer wpisany recznie, te same prace): komunikat + 0 px jak w rundzie 2. D7: P1c, P1f, Y6 - tabela 0a. |
| 5 | `proby_r3.py`, czesc "BLAD": 7 opisow bledu analizy przez `_blad_analizy` | stolik tylko dla 0 z 3 (2 z 2 zapisow), 5 pozostalych bez stolika; dlugosc tekstu 331 znakow (bylo 244) |
| 6 | `okno_r3.py` - okno offscreen 1536 x 864, `QT_QPA_FONTDIR=C:\Windows\Fonts` (log `okno_r3.log`; zrzuty `zrzuty\r3_w1`, `r3_w1b`, `r3_r2`, `r3_b` obejrzane, `r3_r1` tylko pomiar) | `dwa_skany_numeru` 966 x 132 px, 4 wiersze, 3 panele naraz, wszystko widoczne; po "Zmien numer" panelu nie ma; blad analizy 0 z 3: 966 x 111 px, 3 wiersze; `plytka_czeka_na_numer`: 1 skan bez numeru - 966 x 111 px w calosci, 2 skany - pod dwoma pytaniami, widoczny tytul (D11) |
| 7 | Wstrzykniecia (`wstrzyk_r3.ps1`, `wstrzyk_r3b.ps1`, log `wstrzykniecia_rec_r3.log`; kazde cofniete `git checkout`, po kazdym 0 plikow zmienionych) - 9 | Wykryte 8: K1 (P3: rada dla nowych prac -> "Tak" - 1 failed), K3 (P4: zly warunek skanu - 2 failed), K5 (D7: zawsze liczba mnoga - 2 failed), K6 (stolik takze dla 1 z 3 - 2 failed), K7 (D8: brak pytania przy tych samych pracach - test k4 failed na nowej asercji), K8 (P2: twardsza regula - 2 failed), J2 i J9 z rundy 2 (D6 - po 1 failed; w rundzie 2 nie wykryte). NIE wykryte 1: K4 (P4, kierunek "brak -> N" - 16 passed; uwaga D9). |
| 8 | Bajty 6 plikow rundy 3 z obiektow git (`git cat-file blob 1f02673:<plik>`), `git diff --check 7ebb5cd 1f02673`, `git diff --numstat` | 0 bajtow CR w 6 z 6; 0 wierszy nie-ASCII w 5 z 6, `statusy.py` - polskie znaki jak dotad (styl pliku istniejacego); `diff --check`: 0 wpisow; numstat: `indicate.md` 23 / 3, raport 221 / 1, `kontroler_api.py` 11 / 2, `statusy.py` 17 / 7, `test_aplikacja_rano.py` 5 / 3, `test_okragle_ramka.py` 236 / 7 |

Dwa istniejace testy ze zmienionym oczekiwanym tekstem (`test_okragle_ramka.py`). W `test_r2_p1_rano_skan_bez_numeru_...`
do oczekiwanego tekstu dopisane jest pole `jest_skan` i komentarz; asercja "ani Zeskanuj, ani Zmien numer" bez zmian (nowa
rada warunkowa "zeskanuj ja" jest pisana mala litera - komentarz to wyjasnia); `test_s1_blad_analizy_podaje_przyczyne_...`
ma klucz oczekiwanego tekstu `znaczniki_0` dla n = 0. W obu zmienil sie tylko oczekiwany tekst, 0 usunietych asercji.

## 3. Punkty zlecenia rundy 3 (`o2-r3.md`)

| Nr | Punkt | Ocena |
|---|---|---|
| 1 | P2: test stanu faktycznego (2 warianty), opisy testow `test_r2_b1_*`, raport, `indicate.md` | potwierdzone wlasna proba (proby 3, 4, wstrzykniecie K8) i przegladem opisow; drobiazg D10 |
| 2 | P3: tekst `dwa_skany_numeru`, 3 przypadki, 1536 x 864, test | potwierdzone wlasna proba (Y1, Y1b, Y1c, H1, zrzut `r3_w1`, K1) |
| 3 | P4: `_w_wynik` aktualizowany bez zmiany obrazu; 2 testy | potwierdzone wlasna proba (X5, X5b, Y2, Y3, zrzut `r3_w1b`, K3); luka testu D9 |
| 4 | D6, D7, D8 | potwierdzone wlasna proba (J2, J9, K5, K7, P1c, P1f, Y6); D11 do obserwacji |
| 5 | Dodatek: blad analizy 0 z 3 - stolik | potwierdzone wlasna proba (7 opisow, zrzut `r3_b`, K6); pomiar "11 z 11" - wg koordynatora, niesprawdzone |
| 6 | Testy paczki i modulow 0 failed; wstrzykniecia min. 4 | potwierdzone wlasna proba: 66 passed, 260 passed (6 plikow); wstrzykniecia wykonawcy 10 z 10 - wg wykonawcy, nie powtarzalem (poza odpowiednikami J2, J9) |
| 7 | Pelny pytest uruchomiony odlaczony, wynik wpisze koordynator | potwierdzone przegladem (raport 20.7); log wykonawcy o 17:23: 2506 passed / 9 skipped, kod 0xC0000409 po wierszu podsumowania - odczyt koordynatora |

## 4. Zakres plikow i zasady

- `git diff --name-only 7ebb5cd 1f02673`: 6 plikow, wszystkie z listy rundy 3 (`opisy_modulow/session.md` i
  `test_okragle_sesja.py` nie zmienione - dozwolone). `test_aplikacja_rano.py`: tylko 2 miejsca latki k4.
- Nietykalne (`match.py`, `inspect.py`, `plate.py`, `synth.py`, `uklad.py`, `modele_plytek/**`), `session*.py`,
  `indicate.py`, `aplikacja.py`, `ui/**`, schemat bazy: 0 zmian w rundzie 3.
- Nowe tresci ASCII + LF (proba 8); 0 plikow binarnych; danych osobowych nie znalazlem (dane sztuczne).
- Raport wykonawcy (sekcja 20): rzetelny - liczby 66 passed, 9 gniazd / 120 px, rozmiary paneli 966 x 132 i 966 x 111
  zgadzaja sie z moimi pomiarami; uczciwie zglasza komunikat pod dwoma pytaniami (D11) i to, ze 4 z 10 testow
  przechodzily przed zmiana kodu. Lista 20.5: 8 pozycji, komplet wobec mojej listy rundy 2, kolejnosc wg wagi, nr 1 =
  wariant z P2 z zasada pracy. Dla wlasciciela (nie programisty) pozycja nr 1 mowi, co program robi, ale nie mowi, czym
  to grozi przy stole, i nie wymienia przypadku, ktorego zasada pracy nie obejmuje (sekcja 0) - uzupelnilem w sekcji 5.
- Moja kopia: `git -C qc-wt\rec-o2 status --short` pusty, HEAD 1f02673; w worktree wykonawcy niczego nie uruchamialem
  (tylko odczyt logow w `robocze\o2\r3\`). Procesy python o 17:26: 1 (PID 12560 - znany, niczyj), 0 moich; kazda moja
  proba byla jednym procesem i skonczyla sie przed nastepna.

## 5. Do decyzji wlasciciela (pelna lista z trzech rund, wg wagi)

1. **Wynik innej plytki pod plytka lezaca na ramce wieczornej - bez pytania i bez ostrzezenia.** Ramka wieczorna
   rozpoznaje plytke tylko po numerze. Jesli w jednej zmianie sa dwa skany z tym samym numerem plytki i z roznymi
   pracami, diody pod plytka lezaca na ramce pokazuja wynik OSTATNIEGO skanu - czyli moga pokazywac kolory prac z innej
   plytki. Skutek przy stole: technik moze odlozyc jako dobra prace, ktora program oznaczyl do obejrzenia, albo
   odwrotnie. Kiedy to sie zdarza: (a) dwie plytki o tym samym numerze w jednej zmianie (kwadrat R59 i R54; kwadrat
   i okragla); (b) plytka okragla, ktorej numer program odczytal zle z dolkow (zabrudzony / zasloniety dolek) jako numer
   innej plytki; (c) numer kwadratu wpisany z bledem; (d) odpowiedz "Nie, to nowy wsad" bez zdjecia plytki z ramki;
   (e) "cofnij zastapienie" po "Tak". Program pyta i wstrzymuje ramke tylko wtedy, gdy oba skany maja te same prace
   albo ktorys ma mniej niz 3 rozpoznane prace. Tak bylo juz przed ta paczka dla kwadratow; paczka wprowadza plytki
   okragle, wiec dotyczy to teraz takze ich. Zasada pracy do czasu decyzji: **przed skanem nastepnej plytki zdejmij
   poprzednia z ramki wieczornej; w jednej zmianie nie uzywaj dwoch plytek z tym samym numerem.** Zasada nie obejmuje
   przypadku (b), gdy plytka o "pozyczonym" numerze wroci potem na ramke - jedyny sygnal to dwa kafelki z tym samym
   numerem na liscie plytek zmiany (program nie odrozni tego od zwyklego nowego wsadu na tej samej plytce; tu pomaga
   tylko czytelnosc dolkow). Do decyzji: zostawic zasade pracy czy wprowadzic twardsza regule w programie (ramka
   ciemna + komunikat, gdy plytka o numerze wyniku lezala na ramce w chwili startu skanu). Regula wymaga wiedzy z dni
   28-29.11, kiedy naprawde zaczyna sie skan i kiedy technik zdejmuje plytke. Moja rekomendacja: rozstrzygnac przed
   praca produkcyjna z plytkami okraglymi.
2. **Numer poprawiony recznie a dolki plytki okraglej:** gdy technik poprawi numer na inny niz odczytany z dolkow,
   ramka dla tej plytki zostaje ciemna (pracuje sie wg ekranu) i jest komunikat. Alternatywy: swiecic, gdy numer podany
   zgadza sie z numerem z magnesow ramki, albo przycisk potwierdzenia. Bez zmian od rundy 1.
3. **Ponowny skan tych samych prac:** ramka wieczorna swieci dopiero po odpowiedzi "Tak, to ponowny skan"; plytka zdjeta
   z ramki po starcie skanu zostaje ciemna takze po odpowiedzi, choc komunikat mowi "ramka zaswieci". Ocenic na
   sprzecie, czy technik nie odbiera tego jako awarii ramki.
4. **Komunikat "Na ramce lezy inna plytka niz zeskanowana" w zwyklej pracy wieczorem** (poprzednia plytka zostaje na
   ramce w czasie skanu nastepnej) - prawdziwy, znika sam; ocenic uciazliwosc na sprzecie.
5. **Komunikat o niezgodnym numerze i ciemna ramka takze dla kwadratow,** gdyby skan objal ich dolki (D4 z rundy 1) -
   zostawic czy ograniczyc do plytek okraglych.
6. **Kalibracja ukladow okraglych wyliczona z geometrii:** ostrzezenie tylko przy 1. starcie; czy potrzebne trwale
   przypomnienie do czasu kalibracji na ramce.
7. **Brzmienie komunikatow do akceptacji:** 4 z rundy 1; przyczyny bledu analizy, w tym nowa dla "0 z 3 znacznikow"
   (stolik w skanie, rada "ustaw ciecie skanu powyzej stolika" - sprawdzic, czy technik zna to ustawienie w programie
   skanera); "Dwa skany z numerem plytki ..." w brzmieniu rundy 3 (3 rady); "Plytka na ramce czeka na numer skanu"
   w brzmieniu rundy 3. Rano przy 2 skanach bez numeru ten ostatni komunikat lezy pod dwoma pytaniami i widac go
   w calosci dopiero po przewinieciu (D11) - ocenic na sprzecie.
8. **Odstepstwo z rundy 1** (2 zmienione asercje testow przez pole `ramkowa`) - do przyjecia.
