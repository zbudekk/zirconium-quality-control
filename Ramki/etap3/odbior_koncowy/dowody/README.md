# Dowody testow koncowych etapu 3 - co tu jest, skad i jak sprawdzone

Paczka E3-ODBIOR, 21.11.2026, galaz `e3/odbior`. Katalog zawiera KOPIE plikow, ktore wykonawcy testow koncowych zapisali
na PC w `<PC-katalog>\koordynator\robocze\odbior\T<nr>\` (poza repo). Pliki zrodlowe na PC zostaly nietkniete - wszystkie
naprawy (konce linii, ASCII) robiono tylko na kopiach w tym katalogu. Wyniki testow: `../RAPORT.md`; przepis: `../PLAN_TESTOW.md`.

Stan: komplet testow T0-T13 (etap 1: T0, T1, T3, T5, T6, T7, T10, T12, T13 pierwszy przebieg, kontrola zestawu T14;
etap 2: T2, T4, T8, T11, uzupelnienie T7 w `T7/uzup/`, drugi przebieg T13 w `T13/drugi_przebieg/`, T9 w `T9/`).

## Zawartosc

W kazdym `T<nr>/`: `WYNIK.md` wykonawcy (werdykt w pierwszym wierszu, polecenia, kody, liczby), pliki z listy "Dowody" planu
i pozostale male pliki tekstowe testu (pliki polecen `krok_*.cmd`, `kody.txt`, czasy, logi), `dowody_lf.txt` (wynik kontroli
ASCII + LF - powstal tutaj) oraz `POMINIETE.txt` (gdy cos pominieto - powstal tutaj).

| Test | Plikow | Rozmiar | W tym skopiowanych z PC | `dowody_lf.py --napraw`: kod; naprawionych plikow; CR usunietych; bajtow spoza ASCII; znakow zamienionych na `?` |
|---|---|---|---|---|
| T0 | 26 | 46 KB | 25 | 0; 16; 313; 6; 0 |
| T1 | 22 | 44 KB | 20 | 0; 10; 192; 46; 2 |
| T2 | 19 | 101 KB | 17 | 0; 9; 2372; 0; 0 |
| T3 | 13 | 85 KB | 11 | 0; 4; 406; 0; 0 |
| T4 | 14 | 132 KB | 12 | 0; 8; 2445; 0; 0 |
| T5 | 22 | 98 KB | 20 | 0; 8; 208; 0; 0 |
| T6 | 12 | 41 KB | 10 | 0; 4; 200; 0; 0 |
| T7 (bez `uzup/`) | 79 | 208 KB | 77 | 0; 38; 1248; 2636; 32 |
| T7/uzup | 44 | 734 KB | 42 | 0; 0; 0; 0; 0 |
| T8 | 16 | 70 KB | 14 | 0; 8; 514; 0; 0 |
| T9 | 43 | 682 KB | 41 | 0; 7; 120; 0; 0 |
| T10 | 12 | 105 KB | 10 | 0; 0; 0; 0; 0 |
| T11 | 27 | 107 KB | 25 | 0; 7; 630; 14; 0 |
| T12 | 57 | 133 KB | 55 | 0; 33; 1010; 0; 0 |
| T13 (bez `drugi_przebieg/`) | 13 | 78 KB | 12 | 0; 3; 30; 0; 0 |
| T13/drugi_przebieg | 11 | 131 KB | 0 (powstal tutaj) | 0; 3; 442; 0; 0 |
| T14 | 5 | 5 KB | 4 | 0; 3; 53; 0; 0 |
| razem | 435 | 2,7 MB | 395 | 17 katalogow z 17 z kodem 0; 161; 10183; 2702; 34 |

Poza katalogami testow: ten plik i `t9_dowody_zbior.txt` (skan danych osobowych calego katalogu - nizej).

## Werdykty: tabela `RAPORT.md` a pierwszy wiersz `WYNIK.md` (kontrola koncowa etapu 2)

| Test | Pierwszy wiersz `dowody/T<nr>/WYNIK.md` (poczatek) | Wynik w tabeli `RAPORT.md` | Zgodne |
|---|---|---|---|
| T0 | `WERDYKT T0: ZAL z odstepstwem O1` | ZAL z odstepstwem O1 | TAK |
| T1 | `WERDYKT T1: ZAL` | ZAL | TAK |
| T2 | `WERDYKT T2: FAIL - czesc (e) lista "do dofrezowania" = prawda: NIE` | FAIL | TAK |
| T3 | `WERDYKT T3: ZAL z odstepstwem O5` | ZAL z odstepstwem O5 | TAK |
| T4 | `WERDYKT T4: ZAL z odstepstwem O7` | ZAL z odstepstwem O7 | TAK |
| T5 | `WERDYKT T5: ZAL z odstepstwem O8` | ZAL z odstepstwem O8 i O15 | TAK; O15 = numer nadany przez koordynatora odstepstwu "NOWE" opisanemu w tym samym `WYNIK.md` |
| T6 | `WERDYKT T6: ZAL` | ZAL (O9 - informacja) | TAK |
| T7 | `WERDYKT T7: ZAL z odstepstwem O12`; `T7/uzup/WYNIK.md`: `WERDYKT T7 UZUPELNIENIE: ZAL z odstepstwem O12` | ZAL z odstepstwem O12 | TAK |
| T8 | `WERDYKT T8: ZAL` | ZAL | TAK |
| T9 | `WERDYKT T9: ZAL z odstepstwem NOWE` | ZAL z odstepstwem O16 i O17 (wariant doslowny planu: FAIL - do decyzji) | TAK; O16 i O17 = numery nadane przy zestawianiu raportu dwom odstepstwom "NOWE" (T9-a, T9-b) z tego `WYNIK.md` - do potwierdzenia przez koordynatora |
| T10 | `WERDYKT T10: ZAL (bez odstepstwa)` | ZAL | TAK |
| T11 | `WERDYKT T11: ZAL` | ZAL (O6 - informacja) | TAK |
| T12 | `WERDYKT T12: ZAL z odstepstwem O2` | ZAL z odstepstwem O2 | TAK |
| T13 | `WERDYKT T13 (pierwszy przebieg, commit paczki 571e186): ZAL z odstepstwem O11 i O10`; `T13/drugi_przebieg/WYNIK.md`: `WERDYKT T13 (drugi przebieg ...): ZAL z odstepstwem O11 i O10` | ZAL z odstepstwem O11 i O10 | TAK |
| T14 | `KONTROLA ZESTAWU T14 NA INSTALACJI: zgodne 22 z 22 krokow, kod 0 (to NIE jest test T14 ...)` | ZADANIE WLASCICIELA (test niewykonany) | TAK |

Zgodne 15 z 15 porownanych (T0-T13 i kontrola T14); T15-T17 nie maja `WYNIK.md` (ODLOZONE - `../ODLOZONE.md`).

## Jak sprawdzone

1. **ASCII + LF** (`../narzedzia/dowody_lf.py`, wg `PLAN_TESTOW.md`, "Zasady wykonania"): dla kazdego katalogu
   `python.exe -I ..\narzedzia\dowody_lf.py --katalog dowody\T<nr> --napraw --wynik dowody\T<nr>\dowody_lf.txt` - kod 0 w 10 z 10
   katalogow; liczby zamian w tabeli wyzej, wiersze `NAPRAWIONY` w kazdym `dowody_lf.txt`. Transliteracja zmienia tresc
   dowodu: bajty spoza ASCII byly w `T0/t0_4_robocopy.log` (6), `T1/t1_pytest.log` i `t1_pytest_bazowy.log` (po 23; po 1
   znaku zamienionym na `?`), `T7/ustawienia_b1.toml`, `_b1b`, `_b2`, `_b3` (po 659; po 8 znakow na `?` - komentarze wzoru
   ustawien z polskimi znakami).
2. **Pliki polecen `.cmd` - naprawa reczna.** Pierwsze przejscie `dowody_lf.py` dalo kod 1 w T7 (5 naruszen), T12 (6) i
   T13 (1): 12 plikow `krok_*.cmd` mialo konce linii LF zamiast CRLF, a narzedzie plikow polecen nie naprawia ("napraw
   recznie"). W kopiach doprowadzono je do CRLF (dopisano 402 znaki CR: T7 55, T12 330, T13 17; tresc wierszy bez zmian),
   po czym katalogi skopiowano i sprawdzono od nowa - kod 0. Pliki na PC maja nadal konce LF.
3. **Dane osobowe** (`../narzedzia/t9_dane_osobowe.py`, wg T9 krok 1 planu: skan katalogu `dowody\` BEZ `--dozwolone` przed
   `git add`): nazwy z 4 katalogow (`--nazwy-z`: pula do testow `Prace_test`, sztuczne drzewo a5i, foldery "Cyrkon" instalacji
   T0 i T12) i z bazy SE10 testu T3 (`--baza`, nazwy sztuczne). Wynik w `t9_dowody_zbior.txt`: samotest "nieznalezionych
   0"; szukanych nazw 449, czlonow 61; **trafien calych nazw: 0 w 0 plikach, kod 0**; zaden plik nie zostal z tego
   powodu wycofany. Ostatni przebieg (po dodaniu tego opisu): przeszukanych plikow 263, nieprzeszukanych 0; czlony nazw
   "do wyjasnienia": 121 w 39 plikach.
   Czlony nazw "do wyjasnienia" to 4 rozne czlony (sha16 414777f6c840fa40, b78cb9ce56d5b7e2, 5054e1b14a2e813f,
   6d223affc23ef544). Wyjasnienie bez wypisywania czlonow: osobny skrypt policzyl, z ktorego zrodla nazw pochodzi kazdy z
   nich - wszystkie 4 pochodza WYLACZNIE z danych sztucznych (2 z nazw sztucznych bazy SE10: po 1 nazwie; 2 ze zmyslonych
   nazw drzewa a5i: 34 i 47 nazw), zaden nie wystepuje w puli `Prace_test` (0 nazw z 15 folderow). Sa to wiec slowa z nazw
   zmyslonych, ktore wystepuja tez w zwyklym tekscie dowodow; czlonow nie ogladano. To nie jest wynik testu T9 - T9
   wykona osobny wykonawca po komplecie dowodow.
4. **Kontrola koncowa etapu 1:** `dowody_lf.py --katalog dowody` BEZ `--napraw` na calym katalogu - kod 0.

Etap 2 (T2, T4, T8, T11, `T7/uzup/`, `T13/drugi_przebieg/`) - te same kroki, liczby:

5. **ASCII + LF:** `dowody_lf.py --napraw` - kod 0 w 5 z 5 nowych katalogow za pierwszym razem (liczby w tabeli wyzej). Pliki
   polecen `.cmd` (11 sztuk) mialy juz konce CRLF - napraw recznych: 0. Bajty spoza ASCII tylko w `T11/t11_testy.log` i
   `T11/t11_testy_instalacja.log` (po 7; znakow zamienionych na `?`: 0).
6. **Dane osobowe:** to samo polecenie co w kroku 3 (te same 4 katalogi nazw i baza SE10, BEZ `--dozwolone`) na calym `dowody/`
   przed `git add`: samotest "nieznalezionych 0"; szukanych nazw 449; przeszukanych plikow 383, nieprzeszukanych 0;
   **trafien calych nazw: 0 w 0 plikach, kod 0**; zaden plik nie zostal wycofany. Czlony "do wyjasnienia": 220 w 86 plikach
   (w nowych katalogach: T2 1 plik, T4 1, T8 4, T11 2, T7/uzup 39) - to te same 4 czlony co w kroku 3 (sha16 414777f6c840fa40
   87 trafien, b78cb9ce56d5b7e2 29, 5054e1b14a2e813f 99, 6d223affc23ef544 5; lista z `--json` w katalogu roboczym poza repo),
   wyjasnione w kroku 3: pochodza wylacznie z nazw sztucznych; nowego czlonu nie ma. Wynik: `t9_dowody_zbior.txt` (zastapil
   plik z etapu 1; poprzedni stan w commicie 31ded7b). To nie jest wynik testu T9.
7. **T13 a rozszerzenie `.csv`:** pierwsza proba drugiego przebiegu T13 (commit 807aa83) dala 2 naruszenia - `t13_higiena.py`
   liczy `.csv` jako plik danych, a `dowody_lf.py` je przepuszcza. Poprawiono dowod, nie narzedzie: kopie przemianowano na
   `T2/t2_procesy_csv.txt` i `T4/t4_procesy_csv.txt` (tresc bez zmian; na PC nadal `t2_procesy.csv`, `t4_procesy.csv`; `WYNIK.md`
   i `dowody_lf.txt` obu katalogow podaja stara nazwe). Proba 2 (16f209d): 0 naruszen. Opis: `T13/drugi_przebieg/WYNIK.md`.
8. **Kontrola koncowa etapu 2:** `dowody_lf.py --katalog dowody` BEZ `--napraw` na calym katalogu - kod 0; liczba plikow i
   godzina: ostatni akapit tego pliku.
9. **Dowody T9 (dodane na koncu, po werdykcie T9 o 06:25):** 41 plikow skopiowanych z PC; `krok_t9.ps1` mial konce LF -
   w kopii doprowadzony recznie do CRLF (dopisano 31 znakow CR, tresc wierszy bez zmian; na PC nadal LF); `dowody_lf.py
   --napraw` na `T9/`: kod 0, naprawionych 7 plikow, CR usunietych 120, bajtow spoza ASCII 0. Skan danych osobowych calego
   `dowody/` BEZ `--dozwolone` powtorzony po dodaniu `T9/` (to samo polecenie co w krokach 3 i 6): przeszukanych plikow 437,
   nieprzeszukanych 0; **trafien calych nazw: 0 w 0 plikach, kod 0**; czlony "do wyjasnienia" 265 w 95 plikach - te same 4
   czlony co wyzej (nowego czlonu nie ma); wynik w `t9_dowody_zbior.txt`. Wykonawca T9 skanowal ten katalog osobno, z
   szersza lista zrodel nazw (`T9/t9_dowody.txt`, `T9/t9_dowody_2.txt`: 394 pliki, 0 trafien, kod 0).

## Pominiete (zostaja na PC, poza repo)

Regula: do repo nie ida bazy, STL, ZIP, zapisy ruchu `*.bin`, katalogi robocze (`robocze\`, `t3\`, `t3_tmp\`, `t5_wieczor\`,
`t10\`, `t2\`, `t4\`, `t11_auto\`) ani pliki wieksze niz 1024 KB; od etapu 2 takze zrzuty PNG. Lista z rozmiarami i powodem:
`T<nr>/POMINIETE.txt` (T1, T2, T3, T4, T5, T6, T7, T7/uzup, T8, T9, T10, T11, T12; w T0, T13, T14 niczego nie pominieto).

| Test | Pominiete pliki | Pominiete katalogi |
|---|---|---|
| T1 | - | `robocze\` (2 pliki, 382 KB - pelne listy `--collect-only`) |
| T3 | - | `t3\` (17 plikow, w tym baza SE10 potrzebna do T8 i T9), `t3_tmp\` (10 plikow, baza testu) |
| T5 | `ruch_ramka_w.bin` (37 KB), `ruch_ramka_p.bin` (10 KB) - zapisy ruchu, do T9; `ustawienia.toml` (13 KB - wykonawca: nie do repo); `posrednik_w.err`, `posrednik_p.err` (0 B, rozszerzenie spoza listy tekstowych) | `robocze\` (26 plikow, 45 MB), `t5_wieczor\` (34 pliki, 173 MB - baza, skany STL) |
| T6 | - | `robocze\` (8 plikow, 57 KB - kopie logow Excela, plan: nie kopiowac) |
| T7 | - | `robocze\` (111 plikow, 527 MB - bazy, skany STL, kopia folderu projektow) |
| T10 | `t10_metryki.json` (1 623 926 B = 1586 KB, ponad limit; decyzja koordynatora: w repo zostaja `t10_wynik.md` i `t10_licz.json`); `t10_surowe.log` (59 KB - plik surowy, w repo jest jego kopia `t10.log`) | `robocze\` (22 pliki, 1,9 MB), `t10\` (surowy wynik narzedzia, 1586 KB) |
| T12 | - | `robocze\` (instalacje probne czesci B, paczka probna ZIP; wg `T12/WYNIK.md` ok. 6,2 GB - rozmiaru nie liczono ponownie) |
| T2 | - | `robocze\` (44 pliki, 43 MB - kopia folderu projektow, 3 powtorki skanu, probnik), `t2\` (54 pliki, 565 MB - eksport ze skanami STL, baza potrzebna T8 i T9, wyniki, log programu) |
| T4 | - | `robocze\` (441 plikow, 2,1 GB - pamiec puli, linie brzegu), `t4\` (3 pliki surowe, 25 KB - w repo sa ich kopie `t4_czas_zimna.json`, `t4_czas_ciepla.json`, `t4_jakosc.json`) |
| T7/uzup | - | `robocze\` (404 pliki, 1,1 GB - przebiegi ze skanami i bazami, 53 zrzuty), `zrzuty_dowody\` (12 zrzutow PNG, 1638 KB - decyzja koordynatora: nie ida do repo; kazdy opisany jednym zdaniem w `T7/uzup/WYNIK.md`) |
| T8 | - | `robocze\` (17 plikow, 255 KB - kopie baz T2 i T3) |
| T9 | - | `robocze\` (18 plikow, 62 MB - pliki `.json` przebiegow z listami plikow wykluczonych, pomocniki wykonawcy) |
| T11 | `ustawienia.toml` (13 KB - kopia pliku ustawien instalacji ze znakami spoza ASCII; wykonawca: nie do repo) | `robocze\` (170 plikow, 2,0 GB - eksport 40 skanow STL, kopia folderu projektow, baza, wyniki, logi), `t11_auto\` (1 plik, 36 KB - pelny `auto_uklad.json`; w repo wyciag `t11_auto_uklad_podsumowanie.json`) |

## Uwagi dla czytajacego dowody

- Sciezki `<ROB>`, `<K>`, `<REPO>` w plikach `WYNIK.md` odnosza sie do PC (`PLAN_TESTOW.md`, "Oznaczenia"); pliki, do ktorych
  `WYNIK.md` odsyla w katalogach pominietych, sa tylko na PC.
- `T3/t3_wynik.md`, `T5/t5_wynik.md`, `T6/t6_wynik.md` to kopie `WYNIK.md` pod nazwa z listy dowodow planu (tak zapisali
  wykonawcy). `T14/` to kontrola zestawu na instalacji (22 z 22 krokow), nie test T14 - ten wykonuje czlowiek.
- Logi z przekierowania `cmd >` mialy na PC konce CRLF; tu maja LF. Pliki `.cmd` i `.ps1` maja CRLF.
- `T2/t2_wynik.md`, `T4/t4_wynik.md`, `T11/t11_wynik.md` to pliki z listy dowodow planu zapisane przez wykonawcow obok `WYNIK.md`
  (tabele liczb); werdykt testu jest w pierwszym wierszu `WYNIK.md`.
- `T7/uzup/` to osobny pomiar (tresc komunikatow na ekranie programu z paczki, 16 przebiegow) wykonany po pierwszym przebiegu
  T7; wynik T7 w `RAPORT.md` opiera sie na obu. Pliki `p<nr>_<k>_odczyty_<etap>.txt` to zapisy sondy (wiersze JSON).
- `T13/drugi_przebieg/proba_1_807aa83/` to wynik NIEUDANEJ pierwszej proby drugiego przebiegu (2 naruszenia) - zostaje jako dowod.


## Kontrola koncowa etapu 2 (21.11.2026, po dodaniu dowodow T9)

- `PY -I ..\narzedzia\dowody_lf.py --katalog dowody` BEZ `--napraw` na calym katalogu: kod 0, "plikow 437, naruszen 0".
- Skan danych osobowych calego katalogu (krok 9): 437 plikow, 0 trafien calych nazw, kod 0.
- `grep "W TOKU" ../RAPORT.md`: 0 wierszy (wszystkie znaczniki usuniete; T9 i liczniki koncowe wpisane).
- Werdykty tabeli `RAPORT.md` = pierwsze wiersze `WYNIK.md`: 15 z 15 porownanych (tabela wyzej).
- Kontrola dodatkowa (poza planem): `t13_higiena.py` na stanie galezi z dowodami T9 - wynik w ostatniej wiadomosci wykonawcy
  do koordynatora (tego pliku nie da sie sprawdzic commitem, ktory go zawiera).
