WERDYKT T10: ZAL z odstepstwem NOWE (program z kopii repo 0fedbf6 = commit wydania 0.3.3 przez py.cmd, nie z instalacji z paczki - decyzja koordynatora nr 30; przebieg 18:23 przerwany o 18:29 i powtorzony w calosci 20:14; seria rownolegle z T11) - wyrownanie 40 z 40; top-1 "dobrze" 276 z 276; falszywe czerwone na pracach calych 0 z 127; kod 0; liczby i mianowniki rowne nocy 20/21.11 (0.3.1) i przebiegowi na 7ebb5cd

# T10 - powtorka koncowa na commicie wydania 0fedbf6 (21.11.2026) - WYNIK prowadzony przyrostowo

- 17:37:33 start sesji wykonawcy (konto <konto-PC>). Drzewo <PC-katalog>\qc-wt\integ: HEAD 0fedbf6e4f97dc68b2f4679061a960ac81edbdbd (detached), git status --short pusty (17:37).
- 17:38-17:40 przygotowanie <ROB> = <PC-katalog>\koordynator\robocze\odbior2\final$T: pliki .cmd = kopie z przebiegu 7ebb5cd (odbior2$T) ze zmieniona TYLKO sciezka katalogu roboczego (kontrola bajtowa: TAK), ustawienia_wzor.toml = kopia <ST>\ustawienia.przyklad.toml, robocze\Cyrkon = kopia <PC-katalog>\app\Prace_test (17 STL, 15 folderow, 42,83 MB).
- Serie NIE startuja przed plikiem final\T2\T2_KONIEC.txt (T2 mierzy czasy; f2 tor 2 START 17:38:20).
- 17:47:58 koniec T2 (ciezkie.log: KONIEC f2 tor 2 kod 0; plik T2_KONIEC.txt z 17:47:58, zobaczony 17:48:21 - czekanie na znak 10 min, limit 25 min nie zuzyty).
- 17:48:29 start procesu odlaczonego (PID powershell 13756): powershell -NoProfile -ExecutionPolicy Bypass -File <PC-katalog>\koordynator\narz\ciezki.ps1 -Tor 3 -Kto f3-t10 -Polecenie <PC-katalog>\koordynator\robocze\odbior2\final\T10\krok_t10.cmd
- 17:48:50 tor 3 ZAJETY od 17:45:58 przez f1 (final\T1\krok_5.cmd, pelny pytest innego wykonawcy) - ciezki.ps1 T10 czeka w kolejce toru 3 (sprawdza co 30 s); serii T10 jeszcze nie ma (brak kody.txt).
- 18:23:07 ciezkie.log: KONIEC f1 tor 3 (kod -1073740791); 18:23:31 START f3-t10 tor 3 | RAM 63158 MB; kody.txt: t10 START 18:23:31,40. Czekanie w kolejce toru 3: 17:48:29 - 18:23:31 = 35 min 2 s (start 35 min 33 s po koncu T2). Przewidywany koniec ok. 18:40.

## Przerwanie 18:29 i powtorka (wykonawca f5, zlecenie koordynatora 21.11 20:13)

- Ok. 18:29 zginely sesja koordynatora i wykonawca f3 (limit konta) - razem z nimi proces serii T10 (tor 3, start 18:23:31). Stan zastany o 20:13: `t10\` pusty (brak t10_surowe_metryki.json), `t10_surowe.log` urwany (28 371 bajtow, ostatni zapis 18:31), `kody.txt` tylko "t10 START 18:23:31,40", brak "t10 KONIEC"; w ciezkie.log brak "KONIEC f3-t10"; blokada CIEZKI3.lock po PID 13756 (proces nie zyje). Wynik przebiegu 18:23 = NIEWAZNY (przerwanie), nie FAIL.
- 20:13:31 kontrola startowa: `git -C <PC-katalog>\qc-wt\integ status --short` pusty, HEAD 0fedbf6e4f97dc68b2f4679061a960ac81edbdbd (detached). Dysk C: 21 GB wolnego (df -h /c), RAM 69631 MB wolnych (narz\ram.cmd). Procesy python: 12560 (znany, niczyj), 34952 (nie moj, nie ruszany); PID 13756 i 2640 nie istnieja.
- 20:13:55 dowod przerwania przeniesiony (nie skasowany): `t10_surowe.log` i `kody.txt` -> `robocze\przerwany_1829\`.
- Kontrola `krok_t10.cmd` (bez zmian od 17:38, CRLF): sciezki robocze tylko `...\odbior2\final\T10\...`; `grep` na stare katalogi (`odbior2\T10`, `odbior2\T11`, `odbior2\T2`, `odbior2\proba`) = 0 trafien; `grep -c '\$'` = 0.
- 20:14:20 start procesu odlaczonego (PID powershell 21132): `powershell -NoProfile -ExecutionPolicy Bypass -File <PC-katalog>\koordynator\narz\ciezki.ps1 -Tor 3 -Kto f5-t10 -Polecenie <PC-katalog>\koordynator\robocze\odbior2\final\T10\krok_t10.cmd` (przez `Start-Process -WindowStyle Hidden`).
- 20:14:21 ciezkie.log: "PRZEJECIE f5-t10 | blokada osierocona po PID 13756", "START f5-t10 tor 3 | RAM 69496 MB"; kody.txt: "t10 START 20:14:21,57". Rownolegle (jak w pierwszym przebiegu): T11 czesc B + testy na torze 4 (f5-t11, start 20:14:21). Tory 1 i 2 w chwili startu wolne (ostatnie wpisy toru 1 i 2 w ciezkie.log: KONIEC 18:23:30 i 18:03:29).
- 20:17:40 kontrola: 7 z 40 skanow w logu, Traceback 0. 20:22:12 kontrola: 18 z 40, Traceback 0; RAM 61993 MB wolnych, C: 20 GB wolne. Obok w ciezkie.log: tor 2 - s2b4 (`s2\b4\seria_a.cmd`, START 20:16:23 kod 1, ponownie START 20:16:34) - cudzy ciezki krok; tor 4 - T11 czesc B (f5-t11).

## Wynik powtorki 20:14 (zebrany przez wykonawce f5 wg JAK_ZEBRAC_WYNIK.md; drzewo 0fedbf6, tylko odczyt)

### Przebieg

- kody.txt: "t10 START sob. 21.11.2026 20:14:21,57", "t10 KOD=0", "t10 KONIEC sob. 21.11.2026 20:30:59,38"; ciezkie.log: "20:14:21 START f5-t10 tor 3 | RAM 69496 MB", "20:30:59 KONIEC f5-t10 tor 3 | kod 0 | RAM 67700 MB". Czas scienny 16 min 37,8 s; `czas_calosci_s` narzedzia 996,2 s. Kod wyjscia narzedzia 0. Jeden przebieg (to jest wynik), bez powtorek (przebieg 18:23 = przerwany, niewazny - wyzej).
- Polecenie pomiaru (plik `krok_t10.cmd`, doslownie; katalog biezacy `<ST>` = <PC-katalog>\qc-wt\integ\Ramki\stanowisko):
  `call <PC-katalog>\koordynator\narz\py.cmd narzedzia\metryki_P3a.py --skany <PC-katalog>\app\dane_ref\syntetyczne_R59_P2 <PC-katalog>\app\dane_ref\syntetyczne_R59_P3a --projekty <PC-katalog>\koordynator\robocze\odbior2\final\T10\robocze\Cyrkon --wyjscie <PC-katalog>\koordynator\robocze\odbior2\final\T10\t10 --nazwa t10_surowe_metryki.json --procesy 1 --ustawienia <PC-katalog>\koordynator\robocze\odbior2\final\T10\ustawienia_wzor.toml > <PC-katalog>\koordynator\robocze\odbior2\final\T10\t10_surowe.log 2>&1 < NUL`
- Log `t10_surowe.log`: 437 wierszy (40 skanow + podsumowanie + 382 ostrzezenia Open3D "Too few correspondences" - nie blad), "Traceback" 0, "NIE PASUJE" 0; SHA-256 dbddad19b1864604... Plik wyniku `t10\t10_surowe_metryki.json`: 1 622 818 B, SHA-256 036a619f21f12ba0..., zapis 20:30.
- 20:31 `Get-Process python`: procesow T10 brak (zostaly: 33072, 27452, 26132 - T11 czesc B z 20:14:21-41; 12560 znany; 34952 z 18:22-18:24, nie moj); blokada CIEZKI3.lock zdjeta.

### Liczby kryterium wobec nocy i 7ebb5cd

| Czesc kryterium | Ten przebieg (0fedbf6, 20:14) | Noc 20/21.11 (paczka 0.3.1) | 7ebb5cd (16:05) | Werdykt czesci |
|---|---|---|---|---|
| wyrownanie 40 z 40 | 40 z 40 (40 skanow, `uklad_niezgodny` [], najwiekszy blad 0,0143 mm) | 40 z 40 (0,0143 mm) | 40 z 40 (0,0143 mm) | ZAL |
| top-1 "dobrze" 100 % | 276 z 276 (bledne 0; mianownik z plikow prawdy) | 276 z 276 | 276 z 276 | ZAL |
| falszywe czerwone na pracach calych 0 | 0 z 127 wpisow (0 z 126 prac liczonych raz); szerszy licznik 0 z 150 | 0 z 127 | 0 z 127 | ZAL |

Zrodla (kod 0 kazdego polecenia; `PYEXE` = <PC>\AppData\Local\Programs\Python\Python312\python.exe; skrypt `..\z2_robocze\zbierz_t10.sh`):
1. pomocnik `PYEXE -I <ROB>\zestaw_t10.py <ROB>\t10\t10_surowe_metryki.json <ROB>\t10_surowe.log > <ROB>\t10_zestaw.txt` -> WYROWNANIE 40 z 40 (max 0,0143 mm); TOP-1 dobrze 276 z 276 (bokiem 38 z 59, czesciowo 35 z 37, drgniecie 39 z 41 - poza kryterium); FALSZYWE CZERWONE 0 z 127; wiersz logu "PRACE CALE: 127, z czerwonym 0 ... nie sprawdzono 9".
2. skrypt nocy `PYEXE -I <PC-katalog>\koordynator\robocze\odbior\T10\t10_licz.py --wynik-json <ROB>\t10\t10_surowe_metryki.json --log <ROB>\t10_surowe.log --skany <P2> <P3a> --md <ROB>\t10_wynik.md --json <ROB>\t10_licz.json` -> wyrownanie 40 z 40, top-1 dobrze 276 z 276, czerwone na calych 0 z 126 (wpisy 0 z 127), szerszy 0 z 150; "moje_liczby_zgodne_z_narzedziem_i_logiem": true. `t10_wynik.md` rozni sie od pliku z 7ebb5cd tylko 2 wierszami (czasy; statusy gniazd - nizej).
3. `PYEXE -I <ROB>\sprawdz_t10.py <ROB>\t10\t10_surowe_metryki.json <noc>\t10\t10_surowe_metryki.json > <ROB>\sprawdz_t10.txt` (i to samo z plikiem 7ebb5cd -> `sprawdz_t10_7ebb5cd.txt`) -> z rekordow: skanow 40, wyrownanie_ok 40, dobrze_prac 276, top1_bledny 0, prac_calych 127, z czerwonym 0; "rekordy = zbiorczo (6 pol): TAK".

### Roznice poza kryterium (informacja)

- Gniazdo po gniezdzie (413 wpisow w kazdym wyniku, 4 pola): wobec nocy 2 z 413, wobec 7ebb5cd 1 z 413. Wspolna roznica: P3a / `skan_okragla_wieczorna_n8_s0300.stl` / gniazdo 11 wpis 1 (drugi fragment w gniezdzie, scenariusz "bokiem", praca z ubytkiem w prawdzie, sha16 066fcc6858e01759): teraz status gniazda SZARY (noc i 7ebb5cd: zolty). Druga roznica wobec nocy (jak na 7ebb5cd): P3a / `skan_okragla_wieczorna_n8_s0341.stl` / gniazdo 8 wpis 1 - inny pierwszy kandydat (oba rozne od prawdy). Plan T10: rozrzut 1 gniazda miedzy przebiegami (RANSAC).
- Statusy gniazd zielony / czerwony / zolty / szary / pomaranczowy: 116 / 66 / 200 / 27 / 4 (noc i 7ebb5cd: 116 / 66 / 201 / 26 / 4). Falszywe "skan ponownie" (drgniecie): 1 (7ebb5cd 1, noc 2); drgniecie wykryte 36 z 39 (jak noc).
- Czasy (NIE kryterium; inne obciazenie): czas na skan min 12,51 s / mediana 23,16 s / max 51,32 s, suma 983,9 s (7ebb5cd: 11,05 / 22,45 / 53,7 s, suma 926,7 s; noc: 9,9 / 20,7 / 50,88 s, suma 849,6 s); mediany etapow plate 2,83 s, match 19,11 s, inspect 1,67 s.

### Co jeszcze liczylo na PC w czasie 20:14:21 - 20:30:59 (ciezkie.log)

- tor 4: T11 czesc B (f5-t11, program + symulator, skan co 45 s) - caly czas T10;
- tor 2: cudzy `s2b4`: `seria_a.cmd` 20:16:23 (kod 1, 0 s), `seria_a.cmd` 20:16:34 - 20:23:55 (kod 0), `proba_e.cmd` 20:24:09 - 20:25:27, `pytest_narzedzia.cmd` 20:25:50 - 20:28:50;
- tor 1: bez wpisow. Wolny RAM: 69496 MB przy starcie, 61993 MB o 20:22, 67700 MB przy koncu.

### Dane osobowe i dowody

- Kontrola plikow surowych (plan T10 "Dowody", BEZ `--dozwolone`), 20:31: `PYEXE -I <ODB>\narzedzia\t9_dane_osobowe.py --nazwy-z <PC-katalog>\app\Prace_test --nazwy-z <ROB>\robocze\Cyrkon --cel <ROB>\t10\t10_surowe_metryki.json --cel <ROB>\t10_surowe.log --wynik <ROB>\t10_t9.txt` -> kod 0; samotest "nieznalezionych 0"; szukanych nazw 32, czlonow 42; przeszukanych plikow 2; trafien calych nazw 0; czlonow do wyjasnienia 0.
- Kopie po kontroli: `t10_metryki.json` = kopia bajt w bajt surowego wyniku (SHA-256 036a619f21f12ba0... obu; 1585 KB - ponad limit 1024 KB, do repo NIE idzie, jak w nocy); `t10.log` = kopia logu po `dowody_lf.py --napraw` w `robocze\lf` (kod 0: CR 437 -> 0, bajtow spoza ASCII 154 -> 0, "?" 0). Pliki surowe nietkniete.
- Dowody przerwanego przebiegu 18:23: `robocze\przerwany_1829\` (kody.txt, t10_surowe.log 28 371 B) - zostaja na PC.

### Odstepstwa

- NOWE (wspolne T2 / T10 / T11, decyzja koordynatora nr 30): program z kopii repo przez `py.cmd`, nie z instalacji z paczki; `--ustawienia` = kopia `ustawienia.przyklad.toml`, `--projekty` = kopia `Prace_test`.
- NOWE: seria rownolegle z T11 (tor 4) i z cudzym krokiem toru 2; plan "nie z T2, T4, T11". Kryterium T10 nie zalezy od czasu.
- NOWE: przebieg 18:23:31 przerwany o ok. 18:29 (smierc sesji, limit konta) - NIEWAZNY; ten wynik = powtorka 20:14 w calosci.
- Odstepstw O<n> z RAPORT.md 4a dla T10: brak.

**WERDYKT T10: ZAL z odstepstwem NOWE** - wyrownanie 40 z 40 ZAL; top-1 "dobrze" 276 z 276 ZAL; falszywe czerwone 0 z 127 ZAL; kod 0; liczby i mianowniki rowne nocy i 7ebb5cd.
- 20:32 sprzatanie: usunieta `robocze\Cyrkon` (kopia puli `Prace_test`, 17 STL, 43 MB - POLECENIA.md sekcja 5); zostaja `t10\t10_surowe_metryki.json`, `t10_metryki.json`, `t10_surowe.log`, `robocze\lf\`, `robocze\przerwany_1829\`. Kopia dowodow do repo: `Ramki/etap3/odbior_koncowy/dowody_z2/T10/` (galaz e3/odbior2; lista pominietych: tam `POMINIETE.txt`).
