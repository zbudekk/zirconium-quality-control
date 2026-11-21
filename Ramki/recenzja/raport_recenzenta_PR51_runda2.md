# Raport recenzenta - PR #51 (E3-O1), runda 2 (recenzja przyrostowa)

Data: 21.11.2026. Zakres: `git -C <PC-katalog>\qc diff 43d78e1 e3/o1`, HEAD = 5036dfa (3 commity: ed4861a, 29893ae,
5036dfa; 4 pliki). Recenzent niezalezny; kopia do prob `<PC-katalog>\qc-wt\rec-o1` (detached 5036dfa), pliki robocze
`<PC-katalog>\koordynator\robocze\rec-o1\` (nowe z przyrostkiem `_r2`; wynikow rundy 1 nie nadpisano).

Metoda: przeglad diffu (narzedzie, testy, `plate.md`) przed lektura raportu wykonawcy; caly plik testow paczki z
czasami; przeliczenie surowych wynikow rundy 1 opcja `--z-przebiegow`; przeliczenie surowych wynikow pomiaru "granice"
wykonawcy wlasnym skryptem PowerShell (bez `ocen_g`); wlasna probka pomiaru "granice" na nowych ziarnach (kandydaci
wczytani wprost `uklad.wczytaj`, skan bez scianki wlasna konstrukcja z rundy 1); 6 wstrzykniec w kopii (kazde cofniete
`git checkout`, `git status --short` pusty). Pelnego pytest nie powtarzano (wynik 2289 / 9 / 0 na ed4861a sprawdzil
koordynator w logu). Kazda liczba ponizej pochodzi z pomiaru recenzenta, chyba ze napisano "wg wykonawcy".

## 0. Werdykt i liczby B / P / D

WERDYKT: do scalenia - B 0, P 0, D 2 (uwagi 6 i 7, nowe). Uwagi rundy 1: 1 (B) zamknieta W ZAKRESIE PACZKI przy decyzji
domyslnej (a) koordynatora; 2 (P) zamknieta; 3 (P) zamknieta; 4 (D) i 5 (D) zamkniete.

- Uwaga 1 - odpowiedz wprost: przy decyzji (a) paczka robi wszystko, co da sie zrobic bez `plate.py`. Ograniczenie jest
  zmierzone uczciwie (liczby wykonawcy 36 z 90 / 36 z 48 / 8 z 32 odtworzone co do sztuki z jego surowych przebiegow;
  wlasna probka na innych ziarnach daje ten sam obraz: pole 98 i skan bez scianki - zawsze, pole 99 - czasem), utrwalone
  testami, ktore padaja przy zmianie zachowania w obie strony (wstrzykniecia R5 i R6), i opisane bez lagodzenia
  (`plate.md`, raport sekcje 1, 6, 9.3, 13, 20). Samo zachowanie ("plytka okragla testowa bez waznego numeru z dolkow
  i bez scianki bocznej w skanie = KWADRAT, pewny") ZOSTAJE w programie - to nie jest naprawa, tylko jawne ograniczenie.
  Wybor "ograniczenie czy wariant C" nalezy do wlasciciela (sekcja 5 punkt 1).
- Ocena niezalezna od decyzji koordynatora: nie widze powodu, zeby mimo decyzji (a) wstrzymywac scalenie. Skutek
  ograniczenia to zla NAZWA ukladu w bazie i pytanie o numer plytki, mapa gniazd jest ta sama (test sprawdza rownosc
  `sockets`); dotyczy plytek probnych n8 / n9 oraz - po O2 - plytek ramkowych tylko przy 4 dolkach nieczytelnych naraz
  i braku scianki w skanie. Zastrzezenie: decyzja wlasciciela powinna zapasc przed WYDANIEM obslugi plytek okraglych
  ramkowych do laboratorium (po O2 / O3), bo na prawdziwym skanerze nie zmierzono, czy scianka boczna i dolki sa
  widoczne - jesli nie sa, kazda plytka okragla bez czytelnych dolkow bedzie zapisywana jako kwadrat.
- Wlasne potwierdzenie pomiaru "granice" (nowe ziarna, 36 skanow / 68 przebiegow + 24 skany dodatkowe): plytki testowe
  z zaslonietym dolkiem - pogorszenie wobec 8 kandydatow 11 z 20 par (w warunkach granicznych 11 z 16: pole 98 - 4 z 4,
  pole 100 bez scianki - 4 z 4, pole 99 - 1 z 4, pole 97 - 2 z 4, a pozostale 2 z 4 zle takze przy 8 kandydatach;
  pole 100 ze scianka - 0 z 4); pewny zly przy 10 kandydatach 13 z 20; dolki czytelne - 0 z 4 par. Plytki ramkowe
  z 4 dolkami zaslonietymi: bez scianki "kwadrat, pewny" 8 z 8 przebiegow; pole 100 ze scianka 0 z 4; pole 98 - 2 z 16
  przebiegow (1 z 14 skanow - u wykonawcy 0 z 8, uwaga 6); pole 99 - 0 z 12. Kwadraty kontrolne 4 z 4 dobrze.
- Czas pliku `testy/test_auto_uklad_r58.py`: 52 passed w 169,55 s (PC obciazony rownoleglym krokiem innego recenzenta);
  przyrost wobec rundy 1 szacowany z czasow testow na ok. 1 min (14 testow wiecej; 5 przypadkow pola 96 / 94 po 6,5-7,4 s, test plytki ramkowej bez scianki 6,8 s, reszta krotsza) - ok. 3 %
  pelnego pytest (1718 s wg wykonawcy). Nie jest to nadmierne.

## 1. Uwagi

### 1a. Uwagi rundy 1: zamknieta / otwarta + dowod

| Nr | Waga | Stan | Dowod (wlasna proba) |
|---|---|---|---|
| 1 | B | zamknieta w zakresie paczki przy decyzji domyslnej (a); zachowanie zostaje jako opisane ograniczenie, decyzja o wariancie C u wlasciciela | Pomiar: R3 (przeliczenie surowych przebiegow wykonawcy: 36 z 90, 36 z 48, 8 z 32, kwadraty 10 z 10 - identycznie), R4 (wlasna probka na nowych ziarnach: ten sam mechanizm i te same pola). Testy: R2 (52 passed), R8 (3 testy 2 z 2 przebiegow czystych; u wykonawcy 5 z 5 wg logu), R5 (wstrzykniecie W10: 3 z 3 testow granic PADA), R6 (wstrzykniecie "ksztalt kolo / kwadrat", czyli kierunek wariantu C: 2 z 2 testow `test_ograniczenie_znane_*` PADA, 25 pozostalych przechodzi). Zapasy w testach sa duze (miara ksztaltu 2,1 mm2 wobec progu 40 przy polu 98; 60,2 wobec 40 przy polu 100; 0,0 dla ramkowej bez scianki) - test nie lezy na granicy progu. Opis: `plate.md` akapit "Granice rozpoznania plytek okraglych ... OGRANICZENIE ZNANE" mowi wprost: kiedy (dolki bez waznego numeru + brak scianki), ze `pewny` = True tego nie sygnalizuje i ze program glowny `pewny` nie czyta, ze przed paczka plytka testowa byla rozpoznawana dobrze ("jedyne znalezione pogorszenie wprowadzone paczka"), co to znaczy dla technika (mapa gniazd ta sama, zla nazwa ukladu w bazie, pytanie o numer), ze poprawka = wariant C i ze na prawdziwym skanerze nie zmierzono; raport: sekcja 1 zastrzezenie 3, sekcje 6, 9.3, 13 punkt 3, 20. Niedokladnosci liczb - uwaga 6 (D). |
| 2 | P | zamknieta | Stary test zastapiony dwoma (5 + 5 przypadkow). R5: po wstrzyknieciu W10 `test_male_pole_96_i_94_uklad_dobry_i_pewny` PADA w 3 z 5 przypadkow (kwadrat 96, okragla testowa 96, kwadrat poranny 94; 2 przypadki plytek ramkowych przechodza, bo W10 wybiera ostatniego kandydata = uklad ramkowy); w rundzie 1 padalo 0 z 5. `test_male_pole_90_i_80_brak_wyniku_blad_wyrownania` (asercja wprost: `brak_wyniku`, `wybrany` None, `BladWyrownania`, 10 i 8 kandydatow) 5 z 5 przechodzi takze po W10 - slusznie, bo tam nie ma wyniku. Razem po W10: 16 failed / 11 passed (runda 1: 10 failed / 9 passed). |
| 3 | P | zamknieta | R7: cofniecie poprawki `ocen_k3` -> `test_narzedzie_ocena_par_brak_wyniku_to_para_zla` PADA (1 failed / 10 passed); cofniecie poprawki `ocen_k4` -> `test_narzedzie_ocena_bramki_wymaga_wyniku_przy_polu_100` PADA (1 / 10); oba naraz 2 failed / 9 passed. R2a: `--z-przebiegow` na surowych wynikach rundy 1 (oba pliki): K3 80 z 80 skanow, 160 z 160 par, pary bez wyniku 0 z 160; K4 pewny zly 0 (pole 100: bez wyniku 0 z 88, 96: 2 z 88, 94: 12 z 88, 90: 88 z 88, 80: 88 z 88 - czyli 0 z 264 na polach zlecenia i 0 z 176 na posrednich); K2 48 z 48; BRAMKA SPELNIONA, kod 0 - te same liczby co w rundzie 1 (W6a). |
| 4 | D | zamknieta | R7: `bez_sciezek` zamienione na przepuszczanie tekstu -> 2 testy padaja (`..._ostrzezenia_i_bledy_bez_sciezek`, `..._ocena_z_pliku_przebiegow`). Wynik: 9 wierszy ze sciezka w surowym `pomiar\przebiegi.jsonl` -> 0 wystapien `modele_plytek` / nazwy konta w 3 przeliczonych wynikach recenzenta (`.json` i `.txt`) i 0 w wyniku "granice" wykonawcy. |
| 5 | D | zamknieta | `plate.md` (wiersz o numerze 8 / 9): dopisane "to samo zdarza sie takze przy polu 100 mm, gdy miara ksztaltu wypada ponizej progu 40 mm2 (1 z 62 ... 1 z 44 ...; w probie recenzenta ... 1 z 5)". |

### 1b. Uwagi nowe (runda 2)

| Nr | Waga | Plik:linia | Scenariusz | Propozycja |
|---|---|---|---|---|
| 6 | D | `opisy_modulow/plate.md` (akapit "Granice rozpoznania plytek okraglych", punkt "Liczby"), raport paczki sekcje 1, 9.3, 13 punkt 3, 20.2; zrodlo: `narzedzia/auto_uklad_r58.py` `zadania_granice` (ramkowe: 1 ziarno, testowe: to samo ziarno we wszystkich polach i zaslonach) | Czlowiek czyta liczby "plytki ramkowe: kwadrat, pewny - pole 98: 0 z 8 ... wszystkie przy skanie bez scianki" i "pewny zly przy 8 kandydatach: 0 z 90" jak wlasnosc programu. Sa to liczby dla 1 ziarna na plytke ramkowa i 3 ziaren na plytke testowa (6 niezaleznych polozen pola na wiersz - wykonawca pisze to w raporcie 20.2 i 18, w `plate.md` tego nie ma). Wlasna probka: (a) plytka RAMKOWA n1, 4 dolki zasloniete, pole 98 mm ZE scianka ucieta polem (ziarno 6501): KWADRAT `wieczorna`, `pewny` = True, `dolki_wykluczaja` - bez numeru i z numerem 1 (2 z 2 przebiegow; miara ksztaltu ramkowa wobec testowej 0,1 mm2, kwadrat 58,9); 12 dalszych skanow przy polu 98 (4 plytki x 3 ziarna): 0 z 12 - razem 1 z 14 skanow, wobec 0 z 4 skanow u wykonawcy; (b) plytka testowa z zaslonietym dolkiem przy polu 97: przy 8 kandydatach (stan sprzed paczki) kwadrat pewny w 2 z 4 par (runda 1: 2 z 4) - czyli przy polu 97 czesc bledow istniala przed paczka, a "przy 8: 0 z 90" zalezy od ziaren. Zdanie ogolne w `plate.md` ("pole 98 mm i mniejsze ... dotyczy plytki testowej i ramkowej") jest prawdziwe i ostrozne - niedokladne sa tylko liczby; nic nie jest zlagodzone co do mechanizmu. | W `plate.md` i w sekcji 13 raportu dopisac jedno zdanie: liczby sa dla 3 / 1 ziarna; plytce ramkowej zdarza sie to takze przy polu 98 mm (recenzja runda 2: 1 z 14 skanow), a plytka testowa przy polu 97 mm bywala kwadratem juz przy 8 kandydatach (4 z 8 par recenzenta). Przy okazji nastepnego pomiaru: `--ziarna-g` takze dla plytek ramkowych (3 ziarna). Mozna zrobic przy O2 / O3 albo w pliku stanu - nie blokuje scalenia. |
| 7 | D | `narzedzia/auto_uklad_r58.py:324-329` (`ocen_k4`), `:483` (wiersz werdyktu), `:776` (`--pola`) | Koordynator powtarza po O2 / O3 pomiar tylko dla pol posrednich (`--kryteria 4 --pola 96,94`, jak wykonawca w rundzie 1). Wynik: "pewny ze zlym ukladem 0 -> NIESPELNIONE (brak wyniku przy polu 100 - bramki nie da sie orzec)", kod wyjscia 1 (R2a: plik pol posrednich, kod 1). Zachowanie jest rozsadne (bramki bez pola 100 nie wolno orzec) i opisane (naglowek narzedzia, raport 9 "Runda 2", 20.3, 20.5), ale ten sam tekst pada w dwoch roznych sytuacjach: "pola 100 nie bylo w pomiarze" i "przy polu 100 wszystkie przebiegi bez wyniku" (ta druga to awaria wyrownania), a pomoc `--pola` o wymaganiu nie mowi. | Rozroznic komunikat ("pola 100 nie ma w pomiarze - bramki nie orzeka sie" / "pole 100: 0 wynikow z N") i dopisac do pomocy `--pola`, ze bez 100 kryterium 4 wypada NIESPELNIONE z kodem 1. |

## 2. Wlasne proby

| Nr | Polecenie / metoda | Wynik |
|---|---|---|
| R1 | `git diff --stat 43d78e1 e3/o1`; `git diff --stat ed4861a 5036dfa`; `git diff --stat 43d78e1 e3/o1 -- stanowisko modele_plytek ustawienia.przyklad.toml` | 4 pliki (`narzedzia/auto_uklad_r58.py`, `testy/test_auto_uklad_r58.py`, `opisy_modulow/plate.md`, `raporty/E3-O1_2026-11-21.md`) - wszystkie z zakresu rundy 2; po ed4861a zmienione tylko `plate.md` i raport (2 pliki), wiec kod i testy z pelnego pytest = kod i testy HEAD; kod programu, modele, wzor ustawien: 0 zmian |
| R2 | `ciezki.ps1 -Tor 1` -> `krok_a_r2.cmd`: `py.cmd -m pytest -q -p no:cacheprovider --durations=12 testy\test_auto_uklad_r58.py` (11:41:59-11:44:50, `testy_r2.log`) | 52 passed w 169,55 s, kod 0. Najwolniejsze: przygotowanie 10 skanow modulu 44,6 s (bylo w rundzie 1), nowe testy pola 96 / 94 po 6,5-7,4 s (5 przypadkow), `test_ograniczenie_znane_ramkowa_...` 6,8 s; pozostale nowe ponizej 4,9 s |
| R2a | ten sam krok: `py.cmd narzedzia\auto_uklad_r58.py --wyjscie <rec-o1>\przelicz_*_r2 --z-przebiegow ...` na (1) `o1\pomiar\przebiegi.jsonl` + `o1\pomiar_posrednie\przebiegi.jsonl`, (2) samym `pomiar_posrednie`, (3) `o1\r2\granice\przebiegi.jsonl` | (1) kod 0: K2 48 z 48; K3 80 z 80 skanow, pary 160 z 160, bez wyniku 0 z 160, przejscia `powod` jak w rundzie 1 (14 + 2); K4 pewny zly 0, bez wyniku 0 / 2 / 12 / 88 / 88 z 88 (pola 100 / 96 / 94 / 90 / 80); BRAMKA SPELNIONA. (2) kod 1: K4 "NIESPELNIONE (brak wyniku przy polu 100 - bramki nie da sie orzec)", BRAMKA "nie zmierzono" (uwaga 7). (3) kod 0: BRAMKA "nie zmierzono w tym przebiegu", wiersz OGRANICZENIE po wierszu BRAMKA: 36 z 90, 36 z 48, 8 z 32, kwadraty 10 z 10 - czesc "granice" nie zmienia wiersza BRAMKA ani kodu (ocena `g` nie ma pola `spelnione`; kod = `all(o.get("spelnione", True))`). Plikow wejsciowych nie zmieniono, `przebiegi.jsonl` w wyjsciu nie powstal; 0 sciezek w 6 plikach wyniku |
| R3 | PowerShell (`ConvertFrom-Json`, wlasne liczenie klas i par, bez narzedzia wykonawcy) na `o1\r2\granice\przebiegi.jsonl` | 222 wiersze, 116 skanow, 0 bledow; testowe 180 przebiegow = 90 par pelnych; przy 8 kand. dobry_pewny 90 z 90; przy 10: dobry_pewny 54, zly_pewny 36; pogorszenie 36 z 90; z zaslona i bez pola 100 ze scianka: 36 z 48 (pole 98: 12 z 12, 97: 12 z 12, 100 bez scianki: 12 z 12, 99: 0 z 12); pole 100 ze scianka i zaslona 0 z 12; dolki czytelne 0 z 30. Ramkowe 32 przebiegi (10 kand.): kwadrat pewny 8 (wszystkie "100 bez scianki": bez numeru numer nieznany x 4, z numerem numer podany x 4), dobry pewny 24. Kwadraty 10 z 10. Roznica miary ksztaltu "model ramkowy - model testowy" dla skanu testowej z zaslona: pole 100: 59,2-63,6; 99: 42,7-48,6 (tuz nad progiem 40); 98: 19,4-33,4; 97: 0-3,6; bez scianki: 0. Liczby wykonawcy zgodne co do sztuki |
| R4 | `ciezki.ps1 -Tor 1` -> `krok_g_r2.cmd` -> `proba_g_r2.py` (11:50:32-11:54:01, 36 skanow / 68 przebiegow, 0 bledow; ziarna 6380-6605 - inne niz wykonawcy i niz runda 1): G1 testowa n8 / n9, zaslona D i ABCD, 5 wariantow pola, 8 vs 10; G2 testowa bez zaslony (pole 98, 100 bez scianki); G3 ramkowa n1, n2, n4, n5 z 4 dolkami zaslonietymi (bez scianki: 4 plytki; pole 100 i 98: n1, n5), bez numeru i z numerem; G4 kwadraty n2 / n5 | G1 (20 par): pogorszenie 11, pewny zly przy 10: 13, przy 8: 2. Wg pola: 100 ze scianka 0 z 4; 100 bez scianki 4 z 4; 98: 4 z 4; 99: 1 z 4 (n8 ziarno 6380); 97: pogorszenie 2 z 4, pewny zly przy 10: 4 z 4, przy 8: 2 z 4. G2 (4 pary): 4 z 4 dobrze i pewnie przy 8 i 10 (`numer_z_dolkow`). G3: bez scianki 8 z 8 KWADRAT pewny (numer nieznany x 4; numer podany 1 / 2 / 4 / 5 ze zrodlem `podany` x 4); pole 100 ze scianka 4 z 4 dobrze i pewnie; pole 98: n5 dobrze (2 z 2), **n1 (ziarno 6501) KWADRAT pewny 2 z 2** (uwaga 6). G4: 4 z 4 dobrze i pewnie. Usunietych trojkatow scianki co najmniej 996 na skan |
| R4a | `ciezki.ps1 -Tor 1` -> `krok_h_r2.cmd` -> `proba_h_r2.py` (11:54:42-11:56:19): ramkowa n1, n2, n4, n5, 4 dolki zasloniete, pola 98 i 99 ze scianka ucieta polem, 3 ziarna (6710-6752), 10 kandydatow, bez numeru; 24 skany | pole 98: 12 z 12 dobrze i pewnie (`ksztalt`; ramkowa wobec modelu testowej 196-273 mm2); pole 99: 12 z 12 (311-374 mm2). Przypadek z R4 (0,1 mm2) jest wiec rzadki: 1 z 14 skanow plytki ramkowej przy polu 98 w probach rundy 2 |
| R5 | wstrzykniecie W10 z rundy 1 (`plate.py`: przed `uk, wyr, stan, wpis, ostrzezenia = wybrany` wiersz `wybrany, powod, pewny = przeszly[-1], "numer_podany", True`; `perl`, konce linii CRLF zachowane - `git diff --stat`: 1 wiersz dodany), `wstrz_r2_a.cmd`: `pytest testy\test_auto_uklad_r58.py -k "male_pole or kazdy_z_dziesieciu or okragla_testowa or kwadrat_r59 or ograniczenie or testowa_z_zaslonietym"`; potem `git checkout`, `status --short` pusty | 16 failed, 11 passed (27 wybranych): padaja 10 testow jak w rundzie 1 + `test_male_pole_96_i_94_uklad_dobry_i_pewny` 3 z 5 + 3 z 3 testow granic (oba `test_ograniczenie_znane_*` i `test_testowa_z_zaslonietym_dolkiem_pole_100_...`); przechodza: 5 x pole 90 / 80 (brak wyniku), 2 x pole 96 / 94 plytek ramkowych, 4 x `kazdy_z_dziesieciu` dla ukladow, ktore sa ostatnim kandydatem rodziny |
| R6 | wstrzykniecie "kierunek wariantu C" (`plate.py:831`: `ksztalt_rozstrzyga` liczone miedzy najlepszym ukladem a najlepszym ukladem DRUGIEGO ksztaltu - `wstrz_c_r2.pl`, 2 wiersze dodane, 1 usuniety), ten sam wybor testow; cofniete, `status --short` pusty | 2 failed, 25 passed: padaja dokladnie oba `test_ograniczenie_znane_*` (wynik `okragla_wieczorna`, `pewny` True, `ksztalt` zamiast kwadratu) - testy wykryja zmiane reguly i trzeba je bedzie odwrocic, jak mowi ich opis; test granicy "pole 100 ze scianka" i testy pola 96 / 94 przechodza |
| R7 | wstrzykniecia w `narzedzia/auto_uklad_r58.py` (`wstrz_u3_r2.pl`), `wstrz_r2_b.cmd`: `pytest ... -k narzedzie` (11 testow): (a) `ocen_k3` i `ocen_k4` jak w rundzie 1; (b) samo `ocen_k3`; (c) samo `ocen_k4`; (d) `bez_sciezek` = `str(tekst)`; kazde cofniete | (a) 2 failed / 9 passed; (b) 1 failed (`..._par_brak_wyniku_to_para_zla`); (c) 1 failed (`..._bramki_wymaga_wyniku_przy_polu_100`); (d) 2 failed (`..._ostrzezenia_i_bledy_bez_sciezek`, `..._ocena_z_pliku_przebiegow`) |
| R8 | `testy_ogr_r2.cmd`: 2 x `pytest ... -k "ograniczenie or testowa_z_zaslonietym"` na czystej kopii | 2 z 2 przebiegow: "3 passed, 49 deselected" (16,38 s i 16,39 s), kod 0; razem z R2 trzy czyste przebiegi recenzenta z tym samym wynikiem (u wykonawcy 5 z 5 wg logu) |
| R9 | przeglad: bajty nie-ASCII i CR w 4 plikach (`git show e3/o1:...`), stopki commitow, `skip` / `xfail` w dodanych wierszach, sciezki kont w diffie, `git -C qc-wt\o1 status --short`, `git rev-parse origin/e3/o1 e3/o1` | narzedzie, testy, raport: 0 wierszy nie-ASCII, 0 CR; `plate.md` (plik istniejacy, mieszany): tekst dodany ASCII, 0 CR, jedyny dotkniety wiersz z polskimi znakami to istniejacy akapit "Granice rozpoznania" z dopisanym punktem (7); stopka `Co-Authored-By` 3 z 3; 0 `skip` / `xfail` w kodzie testow (6 trafien to slowo "skipped" w raporcie); 0 sciezek kont; worktree wykonawcy czysty, HEAD 5036dfa = `origin/e3/o1` |

Stan po probach: `git -C <PC-katalog>\qc-wt\rec-o1 status --short` pusty, HEAD 5036dfa; 0 procesow python recenzenta
(`Get-Process python*` puste). Ciezkie kroki recenzenta w `log\ciezkie.log` (tor 1, kody 0): 11:41:59-11:44:54,
11:50:32-11:54:01, 11:54:42-11:56:19. Proby R5-R8 (kazda ponizej 2 min) uruchamiane pojedynczo, bez blokady.

## 3. Kryteria zlecenia rundy 2

| Nr | Kryterium | Ocena | Podstawa |
|---|---|---|---|
| 1 | Uwaga 1: pomiar "granice" wykonany, testy utrwalajace 5 z 5, opis w `plate.md` i raporcie | potwierdzone wlasna proba | R3 (36 z 90; 36 z 90; 8 z 32 - zgodne), R4 / R4a (wlasna probka), R2 + R8 (testy), R5 / R6 (padaja przy zmianie zachowania); 5 z 5 powtorek - wg wykonawcy (`o1\r2\powtorka_5x.txt` przeczytany: 5 x "3 passed"). Zestaw zgodny ze zleceniem: testowe n8 / n9 x 3 zaslony x 5 wariantow pola x 3 ziarna, ramkowe n1 / n2 / n4 / n5 x 4 warianty x 2 tryby, kwadraty n2 / n5; wynik w JSON i tabeli, osobno od BRAMKI. Niedokladnosc liczb: uwaga 6 (D) |
| 2 | Uwaga 2: nowy test pada po wstrzyknieciu W10 | potwierdzone wlasna proba | R5: 3 z 5 przypadkow nowego testu pada (runda 1: 0 z 5); calosc 16 failed / 11 passed wobec 10 / 9 |
| 3 | Uwaga 3: 2 nowe testy padaja bez poprawki; przeliczenie = te same liczby | potwierdzone wlasna proba | R7 (a)-(c); R2a: K3 160 z 160 par, K4 0 z 264 (i 0 z 176 na polach posrednich), kod 0 |
| 4 | Uwagi 4 i 5 zrobione | potwierdzone wlasna proba (4) i przegladem (5) | R7 (d), R2a (0 sciezek); tekst w `plate.md` |
| 5 | Pelny pytest 0 failed | niepowtarzane (sprawdzil koordynator: 2289 / 9 / 0 na ed4861a, kod 0xC0000409 po podsumowaniu) | R1: po ed4861a zmienione tylko 2 pliki tekstowe; R2: plik paczki 52 passed na HEAD (38 + 14 = roznica 2275 -> 2289) |
| 6 | Tylko pliki z zakresu; `status --short` pusty; galaz wypchnieta | potwierdzone przegladem | R1, R9 |

Bledy wprowadzone poprawkami - sprawdzone i nie znalezione: (1) czesc "granice" nie wchodzi do wiersza BRAMKA ani do kodu
wyjscia (R2a punkt 3; `bramka` liczona tylko z kryteriow 3 i 4); (2) `--z-przebiegow` niczego nie mierzy i nie kasuje
(`mierzone = ()`, dziennik bez pliku; R2a); (3) nowe sciezki oceny nie zmienily wyniku rundy 1 (R2a); (4) `usun_scianke_boczna`
daje ten sam obraz co niezalezna konstrukcja recenzenta (R3 wobec R4: bez scianki 12 z 12 i 4 z 4; ramkowe 8 z 8 i 8 z 8);
(5) domyslne `--kryteria` zawiera teraz `g` - pelny pomiar domyslny trwa ok. 15 min dluzej (wg wykonawcy 14 min 41 s) -
opisane w naglowku i raporcie; (6) K4 bez pola 100 = NIESPELNIONE i kod 1 - rozsadne i opisane, drobiazg w uwadze 7.

## 4. Zakres plikow i zasady

- Zakres: 4 pliki, wszystkie z listy rundy 2; `testy/test_uklad_r58.py` bez zmian (dozwolone "gdy potrzeba").
- Nietykalne: `plate.py`, `match.py`, `inspect.py`, `synth.py`, `uklad.py`, `modele_plytek/**`, wzor ustawien - 0 zmian
  (R1). Wariantu C nie zaczeto. Wstrzykniecie W10 wykonawcy w jego kopii zmienilo na chwile konce linii `plate.py`
  (opisane w raporcie 20.5); w commitach i w worktree sladu nie ma (R1, R9).
- ASCII / LF: R9. Commity: 3, przedrostek `E3-O1: runda 2 - `, stopka 3 z 3.
- Dane osobowe i duze dane: brak w diffie; wyniki pomiarow poza repo; sciezki katalogow usuniete z wynikow narzedzia.
- Testy: zadnej asercji nie oslabiono - stary test pola 90 / 80 (pusty) zastapiony dwoma mocniejszymi; 0 skip / xfail.
- T13 (informacja z rundy 1, bez zmian): 12 naruszen w 10 kopiach bajtowych R58 - nadal potrzebny wyjatek; runda 2 nie
  dodaje nowych (pliki rundy 2 sa ASCII / LF) - nie powtarzano `t13_higiena.py`.

## 5. Do decyzji wlasciciela

1. **Ograniczenie czy wariant C (uwaga 1 rundy 1).** Stan po rundzie 2: plytka okragla TESTOWA n8 / n9, gdy dolki kodu
   nie daja waznego numeru i w skanie nie ma scianki bocznej, jest zapisywana jako KWADRAT z `pewny` = True; przed
   paczka byla rozpoznawana dobrze (36 z 48 par u wykonawcy, 11 z 16 w probce recenzenta; przy czytelnych dolkach i przy
   polu 100 ze scianka 0 z 42 i 0 z 8). Koordynator przyjal to domyslnie jako ograniczenie - recenzent uznaje paczke za
   kompletna przy tej decyzji, ale decyzja jest wlasciciela i powinna zapasc przed wydaniem obslugi plytek okraglych
   ramkowych. Pomiar "co by bylo" (`koordynator\robocze\wariant_c\WYNIK.md`, poza PR, przeczytany, niesprawdzony): zmiana
   reguly usuwa pewny kwadrat, ale daje "uklad dobry, NIEPEWNY" (24 z 32), a program glowny `pewny` nie czyta - wariant C
   wymaga wiec osobnej paczki z pelna regresja, nie jest prosta poprawka.
2. **Plytki ramkowe (po O2):** z 4 dolkami nieczytelnymi i bez scianki w skanie - kwadrat pewny 8 z 8 (wykonawca) i 8 z 8
   (recenzent); numer z ramki zostaje numerem wyniku, gniazda te same. Przy polu 98 mm zdarza sie to takze ze scianka
   ucieta polem: 1 z 14 skanow recenzenta (u wykonawcy 0 z 4 skanow) - uwaga 6.
3. **Prawdziwy skaner:** nie zmierzono, czy widzi scianke boczna plytki okraglej i czy dolki kodu sa czytelne. Od tego
   zalezy, czy ograniczenie jest rzadkim przypadkiem, czy regula - do sprawdzenia na pierwszym skanie plytki R58 (T16).
4. **Narzedzie pomiarowe:** pomiar domyslny zawiera teraz czesc "granice" (ok. 15 min wiecej); pomiar bez pola 100
   konczy sie kodem 1 (uwaga 7).
5. Punkty 3-6 sekcji 5 raportu rundy 1 (numer drugiego ksztaltu, pole 90 / 80 bez wyniku, wyjatek T13, wydanie dopiero
   po O2) - bez zmian.
