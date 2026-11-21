# Dowody testow koncowych etapu 3 - co tu jest, skad i jak sprawdzone

Paczka E3-ODBIOR, 21.11.2026, galaz `e3/odbior`. Katalog zawiera KOPIE plikow, ktore wykonawcy testow koncowych zapisali
na PC w `<PC-katalog>\koordynator\robocze\odbior\T<nr>\` (poza repo). Pliki zrodlowe na PC zostaly nietkniete - wszystkie
naprawy (konce linii, ASCII) robiono tylko na kopiach w tym katalogu. Wyniki testow: `../RAPORT.md`; przepis: `../PLAN_TESTOW.md`.

Stan: testy WYKONANE - T0, T1, T3, T5, T6, T7, T10, T12, T13 (pierwszy przebieg) - oraz kontrola zestawu T14. Katalogow
T2, T4, T8, T9, T11 jeszcze nie ma (testy w toku albo przed startem) - dojda w kolejnym etapie, tak samo jak drugi przebieg T13.

## Zawartosc

W kazdym `T<nr>/`: `WYNIK.md` wykonawcy (werdykt w pierwszym wierszu, polecenia, kody, liczby), pliki z listy "Dowody" planu
i pozostale male pliki tekstowe testu (pliki polecen `krok_*.cmd`, `kody.txt`, czasy, logi), `dowody_lf.txt` (wynik kontroli
ASCII + LF - powstal tutaj) oraz `POMINIETE.txt` (gdy cos pominieto - powstal tutaj).

| Test | Plikow | Rozmiar | W tym skopiowanych z PC | `dowody_lf.py --napraw`: kod; naprawionych plikow; CR usunietych; bajtow spoza ASCII; znakow zamienionych na `?` |
|---|---|---|---|---|
| T0 | 26 | 46 KB | 25 | 0; 16; 313; 6; 0 |
| T1 | 22 | 44 KB | 20 | 0; 10; 192; 46; 2 |
| T3 | 13 | 85 KB | 11 | 0; 4; 406; 0; 0 |
| T5 | 22 | 98 KB | 20 | 0; 8; 208; 0; 0 |
| T6 | 12 | 41 KB | 10 | 0; 4; 200; 0; 0 |
| T7 | 79 | 208 KB | 77 | 0; 38; 1248; 2636; 32 |
| T10 | 12 | 105 KB | 10 | 0; 0; 0; 0; 0 |
| T12 | 57 | 133 KB | 55 | 0; 33; 1010; 0; 0 |
| T13 | 13 | 78 KB | 12 | 0; 3; 30; 0; 0 |
| T14 | 5 | 5 KB | 4 | 0; 3; 53; 0; 0 |
| razem | 261 | 843 KB | 244 | 10 katalogow z 10 z kodem 0; 119; 3660; 2688; 34 |

Poza katalogami testow: ten plik i `t9_dowody_zbior.txt` (skan danych osobowych calego katalogu - nizej).

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
4. **Kontrola koncowa:** `dowody_lf.py --katalog dowody` BEZ `--napraw` na calym katalogu (tak, jak zrobi to drugi przebieg
   T13) - kod 0.

## Pominiete (zostaja na PC, poza repo)

Regula: do repo nie ida bazy, STL, ZIP, zapisy ruchu `*.bin`, katalogi robocze (`robocze\`, `t3\`, `t3_tmp\`, `t5_wieczor\`,
`t10\`) ani pliki wieksze niz 1024 KB. Lista z rozmiarami i powodem: `T<nr>/POMINIETE.txt` (T1, T3, T5, T6, T7, T10, T12;
w T0, T13, T14 niczego nie pominieto).

| Test | Pominiete pliki | Pominiete katalogi |
|---|---|---|
| T1 | - | `robocze\` (2 pliki, 382 KB - pelne listy `--collect-only`) |
| T3 | - | `t3\` (17 plikow, w tym baza SE10 potrzebna do T8 i T9), `t3_tmp\` (10 plikow, baza testu) |
| T5 | `ruch_ramka_w.bin` (37 KB), `ruch_ramka_p.bin` (10 KB) - zapisy ruchu, do T9; `ustawienia.toml` (13 KB - wykonawca: nie do repo); `posrednik_w.err`, `posrednik_p.err` (0 B, rozszerzenie spoza listy tekstowych) | `robocze\` (26 plikow, 45 MB), `t5_wieczor\` (34 pliki, 173 MB - baza, skany STL) |
| T6 | - | `robocze\` (8 plikow, 57 KB - kopie logow Excela, plan: nie kopiowac) |
| T7 | - | `robocze\` (111 plikow, 527 MB - bazy, skany STL, kopia folderu projektow) |
| T10 | `t10_metryki.json` (1 623 926 B = 1586 KB, ponad limit; decyzja koordynatora: w repo zostaja `t10_wynik.md` i `t10_licz.json`); `t10_surowe.log` (59 KB - plik surowy, w repo jest jego kopia `t10.log`) | `robocze\` (22 pliki, 1,9 MB), `t10\` (surowy wynik narzedzia, 1586 KB) |
| T12 | - | `robocze\` (instalacje probne czesci B, paczka probna ZIP; wg `T12/WYNIK.md` ok. 6,2 GB - rozmiaru nie liczono ponownie) |

## Uwagi dla czytajacego dowody

- Sciezki `<ROB>`, `<K>`, `<REPO>` w plikach `WYNIK.md` odnosza sie do PC (`PLAN_TESTOW.md`, "Oznaczenia"); pliki, do ktorych
  `WYNIK.md` odsyla w katalogach pominietych, sa tylko na PC.
- `T3/t3_wynik.md`, `T5/t5_wynik.md`, `T6/t6_wynik.md` to kopie `WYNIK.md` pod nazwa z listy dowodow planu (tak zapisali
  wykonawcy). `T14/` to kontrola zestawu na instalacji (22 z 22 krokow), nie test T14 - ten wykonuje czlowiek.
- Logi z przekierowania `cmd >` mialy na PC konce CRLF; tu maja LF. Pliki `.cmd` i `.ps1` maja CRLF.
