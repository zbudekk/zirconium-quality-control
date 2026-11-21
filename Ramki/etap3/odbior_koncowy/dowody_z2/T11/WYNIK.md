WERDYKT T11: ZAL z odstepstwem NOWE (program z kopii repo 0fedbf6 = commit wydania 0.3.3 przez py.cmd, nie z instalacji z paczki - decyzja koordynatora nr 30; czesc A z przebiegu 17:48, czesc B i testy z powtorki 20:14 po przerwaniu o 18:29; seria rownolegle z T10) - N = 40 z 40 skanow *_r54 przez aplikacje; uklad rozpoznany 40 z 40 (P2 24 z 24, P3a 16 z 16), uklad_zrodlo auto 40 z 40; zielone przy zlym ukladzie 0 (0 z 0 skanow; T2 poz. 7: zielonych 0); skany.uklad zapisany 40 z 40; czesc A: bez_numeru 40 z 40, zle_ale_pewny 0 (z_numerem 16 z 16); krok 4: 45 passed / 0 failed; kody 0 (auto_uklad, symulator, program, testy); liczby i mianowniki rowne nocy 20/21.11 i 7ebb5cd; O6 = informacja

# T11 - powtorka koncowa na commicie wydania 0fedbf6 (21.11.2026) - WYNIK prowadzony przyrostowo

- 17:37:33 start sesji wykonawcy (konto <konto-PC>). Drzewo <PC-katalog>\qc-wt\integ: HEAD 0fedbf6e4f97dc68b2f4679061a960ac81edbdbd (detached), git status --short pusty (17:37).
- 17:38-17:40 przygotowanie <ROB> = <PC-katalog>\koordynator\robocze\odbior2\final$T: pliki .cmd = kopie z przebiegu 7ebb5cd (odbior2$T) ze zmieniona TYLKO sciezka katalogu roboczego (kontrola bajtowa: TAK), ustawienia_wzor.toml = kopia <ST>\ustawienia.przyklad.toml, robocze\Cyrkon = kopia <PC-katalog>\app\Prace_test (17 STL, 15 folderow, 42,83 MB).
- Serie NIE startuja przed plikiem final\T2\T2_KONIEC.txt (T2 mierzy czasy; f2 tor 2 START 17:38:20).
- 17:47:58 koniec T2 (ciezkie.log: KONIEC f2 tor 2 kod 0; plik T2_KONIEC.txt z 17:47:58, zobaczony 17:48:21 - czekanie na znak 10 min, limit 25 min nie zuzyty).
- 17:48:29 start procesu odlaczonego (PID powershell 2640): powershell -NoProfile -ExecutionPolicy Bypass -File <PC-katalog>\koordynator\narz\ciezki.ps1 -Tor 4 -Kto f3-t11 -Polecenie <PC-katalog>\koordynator\robocze\odbior2\final\T11\krok_t11.cmd
- 17:48:30 ciezkie.log: START f3-t11 tor 4 | RAM 67361 MB; kody.txt: t11 A START 17:48:30,59 (32 s po koncu T2). Przewidywany koniec ok. 18:45.
- Czesc A: 17:48:30,59 - 17:53:06 (4 min 36 s), kody.txt: t11 A auto_uklad KOD=0; auto_uklad.json podsumowanie: bez_numeru skanow 40, ok 40, ok_i_pewny 40, zle_ale_pewny 0; z_numerem skanow 16, ok 16, zle_ale_pewny 0 (jak noc i 7ebb5cd).
- Czesc B: t11 B START 17:53:06,46; program START 17:53:06,53 (--zamknij-po 3000 -> koniec programu ok. 18:43:10); symulator 20 s pozniej.
- 18:23:48 czesc B: symulator KOD=0 (40 plikow w eksport), w logu programu 40 wierszy 'przyjety jako'; program czeka do --zamknij-po 3000 (ok. 18:43:10). T10 wystartowal dopiero 18:23:31 (kolejka toru 3).

## Przerwanie 18:29 i powtorka czesci B + testow (wykonawca f5, zlecenie koordynatora 21.11 20:13)

- Ok. 18:29 zginely sesja koordynatora i wykonawca f3 (limit konta) - razem z nimi program czesci B (`--zamknij-po 3000`, mial sie zamknac ok. 18:43:10) i proces serii (tor 4). Stan zastany o 20:13: kody.txt konczy sie na "t11 B symulator KOD=0" (brak "t11 B program KOD", "t11 B KONIEC", krok testow nie ruszyl); w ciezkie.log brak "KONIEC f3-t11"; blokada CIEZKI4.lock po PID 2640 (proces nie zyje). Czesc B i krok testow przebiegu 17:53 = NIEWAZNE (przerwanie), nie FAIL. Czesc A (17:48:30 - 17:53:06, KOD=0) = WAZNA, zostaje (decyzja koordynatora).
- 20:13:31 kontrola startowa: `git -C <PC-katalog>\qc-wt\integ status --short` pusty, HEAD 0fedbf6e4f97dc68b2f4679061a960ac81edbdbd (detached). Dysk C: 21 GB wolnego, RAM 69631 MB wolnych.
- 20:13:55 dowod przerwania przeniesiony (nie skasowany) do `robocze\przerwany_1829\`: katalog `robocze\t11\` w calosci (eksport 40 skanow, dane: baza 184 320 B + blokada bazy, logi, wyniki, podglady, pula_cache), `t11_program_stdout.log`, `t11_symulator.json`, `t11_symulator.log`. Czesc A (`t11_auto\`, `t11_auto_uklad.log`, `t11_auto_uklad_podsumowanie.json`) i `t11_prawda.txt` zostaja na miejscu.
- Nowy plik `krok_t11_B.cmd` (CRLF) = `krok_t11.cmd` BEZ czesci A: 3 wiersze naglowka (`@echo off`, `cd /d <ST>`, `set QT_QPA_PLATFORM=offscreen`) + wiersze od "echo t11 B START" do konca; kontrola bajtowa (`sed -b` + `cmp`): naglowek i czesc B identyczne z `krok_t11.cmd`. Ten sam `krok_t11_program.cmd` (bez zmian), symulator `--ile 40 --odstep 45 --rownolegle 1 --seed 1`. `grep` na stare katalogi = 0, `grep -c '\$'` = 0 (oba pliki).
- Katalog roboczy czesci B swiezy, przygotowany tak samo jak w pierwszym przebiegu (`ust_t11.sh` = POLECENIA.md 4.0): `ustawienia_t11.toml` bez zmian (11 kluczy `[sciezki]` na `final\T11\robocze\t11\...` i `robocze\Cyrkon`; `diff` z wzorem = 11 wierszy); `mkdir -p robocze\t11\eksport robocze\t11\Prywatne robocze\t11\millbox robocze\t11\dane` - wszystkie 4 katalogi PUSTE przed startem (pusta baza = tryb wieczor, pula zimna). Sed nie byl uruchamiany ponownie (plik ustawien nie zmienil sie od 17:38). `robocze\Cyrkon` (kopia Prace_test) ten sam co w pierwszym przebiegu - program go tylko czyta.
- 20:14:16 dopisany do kody.txt wiersz "--- powtorka 21.11 20:14:16 ---".
- 20:14:20 start procesu odlaczonego (PID powershell 27896): `powershell -NoProfile -ExecutionPolicy Bypass -File <PC-katalog>\koordynator\narz\ciezki.ps1 -Tor 4 -Kto f5-t11 -Polecenie <PC-katalog>\koordynator\robocze\odbior2\final\T11\krok_t11_B.cmd` (przez `Start-Process -WindowStyle Hidden`).
- 20:14:21 ciezkie.log: "PRZEJECIE f5-t11 | blokada osierocona po PID 2640"; wiersza "START f5-t11 tor 4" w ciezkie.log NIE MA (w tej samej sekundzie pisaly oba procesy ciezki.ps1 - zapis jednego zginal; blokada CIEZKI4.lock ma kto.txt "f5-t11 20:14:21 ...krok_t11_B.cmd" i pid.txt 27896, wiec krok idzie pod blokada). kody.txt: "t11 B START 20:14:21,60", "t11 B program START 20:14:21,65"; log programu 20:14:22: "start, zadan wznowionych 0, plikow znanych 0" (pusta baza). Program zamknie sie ok. 21:04:22 (--zamknij-po 3000), potem testy -> koniec ok. 21:07.
- ODSTEPSTWO NOWE: czesc A z przebiegu 17:48 (drzewo 0fedbf6, ten sam plik ustawien wzoru), czesc B i krok testow z powtorki po przerwaniu 18:29 (20:14). Obie czesci na tym samym drzewie i tych samych danych; czesc B na swiezej bazie, wiec nie zalezy od przebiegu przerwanego.
- Rownolegle (jak w pierwszym przebiegu): T10 na torze 3 (f5-t10, start 20:14:21).
- 20:17:40 kontrola: eksport 4 pliki, w logu programu 4 x "przyjety jako". 20:22:12 kontrola: eksport 11, "przyjety jako" 10; RAM 61993 MB wolnych, C: 20 GB wolne. Obok: tor 3 - T10 (f5-t10), tor 2 - s2b4 (cudzy ciezki krok od 20:16:23).
- 20:33:22 kontrola: eksport 25 plikow, "przyjety jako" 25, Traceback / ERROR w logu programu 0; T10 skonczony 20:30:59 (tor 3 wolny); RAM 67146 MB wolnych, C: 19 GB wolne.
- 20:44:06 kontrola: kody.txt "t11 B symulator KOD=0" (po powtorce); eksport 40 plikow; "przyjety jako" 39 (ostatni skan w analizie); RAM 66398 MB wolnych, C: 18 GB wolne. Program czeka do --zamknij-po 3000 (ok. 21:04:22), potem krok testow.
- 20:44:27 w logu programu "skan c5d76faa2066aa63 przyjety jako 40" - 40 z 40 skanow przyjetych ok. 20 min przed zamknieciem programu. 20:55:10 kontrola: program czeka do --zamknij-po 3000; RAM 66469 MB wolnych, C: 18 GB wolne; w ciezkie.log od 20:31 brak nowych wpisow (tory 1-3 wolne).

## Wynik (czesc A z 17:48, czesc B i krok 4 z powtorki 20:14; zebral wykonawca f5 wg JAK_ZEBRAC_WYNIK.md; drzewo 0fedbf6, tylko odczyt)

### Przebieg (kody.txt, ciezkie.log, logi serii)

| Czesc | Start | Koniec | Kod | Wynik |
|---|---|---|---|---|
| A `auto_uklad.py` (przebieg 17:48, WAZNY) | 17:48:30,59 | 17:53:06 | 0 | bez_numeru ok 40 z 40; z_numerem ok 16 z 16 |
| B program (powtorka) | 20:14:21,65 (log programu: start 20:14:22, "zadan wznowionych 0, plikow znanych 0") | 21:04:24,44 (sam, `--zamknij-po 3000`) | 0 | "zamkniete, zadan niezakonczonych 0" |
| B symulator (powtorka) | ok. 20:14:41 (pierwszy skan 20:14:43) | 20:44:00 (ostatni skan) | 0 | "zapisano plikow: 40 (dobrych 40, zlych 0)" |
| krok 4 testy (powtorka) | 21:04:27,86 | 21:06:17,67 | 0 | "45 passed, 174 deselected, 1 warning in 108.16s (0:01:48)" |

- ciezkie.log: "20:14:21 PRZEJECIE f5-t11 | blokada osierocona po PID 2640"; wiersza "START f5-t11 tor 4" brak (opis wyzej); "21:06:17 KONIEC f5-t11 tor 4 | kod 0 | RAM 69923 MB" (plik krokow konczy sie `exit /b 0` - kody czesci z kody.txt: symulator 0, program 0, testy 0). Czesc B + testy: 20:14:21 - 21:06:17 = 51 min 56 s.
- Polecenia: pliki `krok_t11_B.cmd` i `krok_t11_program.cmd` (doslownie jak w `krok_t11.cmd` pierwszego przebiegu; tresc w POLECENIA.md 4.1 / 4.2 ze zmienionym `<ROB>`).
- Log programu (`robocze\t11\dane\logi\stanowisko.log`): "nowy skan nr" 40 (20:14:43 - 20:44:00), "przyjety jako" 40 (ostatni 20:44:27, 19 min 57 s przed zamknieciem), "nie dala wyniku" 0, Traceback 0, ERROR 0, WARNING 3 (brak pliku kalibracji ramek; 2 x "zgaszenie ramki W / P przy zamknieciu nie doszlo"; noc 3, 7ebb5cd 5). Kolejka: 2 z 40 razy nowy skan przyszedl, zanim poprzedni byl przyjety (skany nr 2 i 37; 7ebb5cd: 3 razy) - najwyzej 1 skan czekal. `t11_program_stdout.log` 308 B (3 wiersze Qt o czcionkach - znane dla kopii repo).
- Zdarzenia w bazie: scanner/nowy_skan 40, silnik/skan_przyjety 40, system/podglad 40, system/konflikt_projektu 7, program_start 1, program_stop 1 (jak noc i 7ebb5cd).
- 21:06 `Get-Process python`: procesow tej serii brak (zostaly 12560 - znany, 34952 - nie moj); blokada CIEZKI4.lock zdjeta; `git -C <PC-katalog>\qc-wt\integ status --short` pusty, HEAD 0fedbf6.

### Liczby kryterium wobec nocy i 7ebb5cd

| Czesc kryterium | Ten wynik (0fedbf6) | Noc 20/21.11 (paczka 0.3.1) | 7ebb5cd | Werdykt czesci |
|---|---|---|---|---|
| skany przez aplikacje (wiersz w `skany` dla sha16 z dziennika) | 40 z 40 (bez wiersza 0) | 40 z 40 | 40 z 40 | - |
| (a) uklad rozpoznany ALBO ostrzezenie z nazwa ukladu | rozpoznane 40 z 40 (P2 24 z 24, P3a 16 z 16); `uklad_zrodlo` auto 40 z 40; `niezgodny_uklad` 0 | 40 z 40, auto 40 z 40 | 40 z 40, auto 40 z 40 | ZAL (pierwsza galezia) |
| (b) 0 zielonych przy zlym ukladzie | 0 (0 z 0 skanow `niezgodny_uklad` / `uklad_zgodny` = 0 / uklad inny niz prawda); odsylacz wg planu: T2 na tym samym commicie (`final\T2`), pozycja 7 sha16 857369c6c1d3aef3: `niezgodny_uklad`, zielonych 0 | 0 | 0 | ZAL |
| (c) uklad zapisany w `skany` | 40 z 40 | 40 z 40 | 40 z 40 | ZAL |
| czesc A (`auto_uklad.py`, 17:48) | bez_numeru ok 40 z 40, ok_i_pewny 40, zle_ale_pewny 0; z_numerem ok 16 z 16, zle_ale_pewny 0 | 40 z 40 / 0; 16 z 16 / 0 | 40 z 40 / 0; 16 z 16 / 0 | zgodne |
| krok 4 (testy "zly uklad") | 45 passed, 0 failed, 174 deselected | 45 passed | 45 passed | zgodne |

- Po ukladach: okragla_poranna_r54 12 z 12, okragla_wieczorna_r54 12 z 12, poranna_r54 8 z 8, wieczorna_r54 8 z 8. Zaden skan `*_r54` nie zostal przypisany do ukladu okraglego ramkowego.
- Statusy (`t11_statusy.tsv`): plytka_nie_z_trybu 20 (okragla_poranna_r54 12, poranna_r54 8), do_powtorzenia 15, przyjety 5 - identyczne z noca i 7ebb5cd. Zjawiska znane (nie blad ukladu).
- Skan po skanie wobec 7ebb5cd (po sha16; status, uklad, uklad_zrodlo, uklad_zgodny, numer_plytki): 40 z 40 identycznych; prace na skan (`t11_zielone_prace.tsv`: prac / zielonych / zoltych / czerwonych / szarych): identyczne 40 z 40 (razem 413 / 114 / 186 / 67 / 38).
- Czesc A, podstawy (bez_numeru): numer_z_dolkow 24, ksztalt 15, dolki_wykluczaja 1; czas rozpoznania mediana 3,72 s, max 5,07 s (7ebb5cd 3,14 / 4,92 s; noc 2,45 / 2,86 s).
- Czasy (NIE kryterium): `skany.czas_s` min 12,4 s / mediana 25,2 s / max 50,6 s (= pierwszy skan, pula zimna; 7ebb5cd 12,6 / 23,9 / 65,4 s; noc 11,0 / 19,9 / 49,6 s); testy 108,16 s (7ebb5cd 118,51 s).

Zrodla (kod 0 kazdego polecenia; `PYEXE` = <PC>\AppData\Local\Programs\Python\Python312\python.exe; baza czytana po zamknieciu programu, 21:04-21:06):
1. narzedzie planu `sql_odczyt.py` (6 zapytan, skrypt `..\z2_robocze\zbierz_t11_baza.sh`; te same zapytania co na 7ebb5cd): `t11_skany.tsv` i `t11_zielone.tsv` (zapytania planu doslownie), `t11_skany_sha16.tsv`, `t11_zielone_prace.tsv`, `t11_statusy.tsv`, `t11_zdarzenia.tsv`; plus `cmd /c <ROB>\odczyt_t11.cmd <PC-katalog>\qc-wt\integ <ROB>\robocze\t11\dane\stanowisko.sqlite <ROB>\t11_baza.txt` ("KOD=0").
2. pomocnik `PYEXE -I <ROB>\zestaw_t11.py <ROB>\robocze\t11\dane\stanowisko.sqlite <ROB>\t11_symulator.json <r54_P2> <r54_P3a> > <ROB>\t11_zestaw.txt` -> prawda 40, dziennik 40 / 40 / spoza prawdy 0, (n) 40 z 40, (a) 40 z 40, auto 40 z 40, (b) 0, (c) 40 z 40.
3. skrypt `PYEXE -I <ROB>\sprawdz_t11.py <ROB>\t11_auto\auto_uklad.json <ROB>\t11_prawda.txt <ROB>\t11_symulator.json <ROB>\t11_skany_sha16.tsv <ROB>\t11_zielone.tsv <ROB>\t11_tabela.tsv > <ROB>\t11_liczniki.txt` -> te same liczby; czesc A z rekordow = podsumowanie narzedzia (TAK, TAK). `t11_prawda.txt` (17:49) = bajt w bajt plik prawdy z 7ebb5cd. `t11_wynik.md` = liczniki + tabela skan po skanie (skrypt `..\z2_robocze\t11_wynik_md.py`; na danych 7ebb5cd odtwarza tamten plik 1:1 poza naglowkiem).
- Uwaga wykonawcy: pierwsze uruchomienie `zbierz_t11_baza.sh` (21:05) mialo blad sciezki wyjscia w skrypcie Git Bash - 6 wynikow trafilo kolejno do jednego pliku obok katalogu T11 (usuniety); po poprawce (21:06) 6 z 6 plikow, kod 0. Pierwsze `sprawdz_t11.py` (bez plikow TSV) - kod 1, powtorzone po poprawce - kod 0.

### Co jeszcze liczylo na PC w czasie czesci B i testow (20:14:21 - 21:06:17; ciezkie.log)

- tor 3: T10 (f5-t10) 20:14:21 - 20:30:59 (kod 0) - w czasie pierwszych 22 skanow czesci B;
- tor 2: cudzy `s2b4` 20:16:23 - 20:28:50 (4 kroki: `seria_a.cmd` x 2, `proba_e.cmd`, `pytest_narzedzia.cmd`);
- tor 1: bez wpisow; od 20:31 do 21:06 zadnego innego ciezkiego kroku w ciezkie.log. Wolny RAM 69496 MB przy starcie, 61993 - 67146 MB w trakcie, 69923 MB na koncu.

### Dane osobowe

- Kontrola katalogu (BEZ `--dozwolone`), 21:06: `PYEXE -I <ODB>\narzedzia\t9_dane_osobowe.py --nazwy-z <PC-katalog>\app\Prace_test --nazwy-z <ROB>\robocze\Cyrkon --baza <ROB>\robocze\t11\dane\stanowisko.sqlite --cel <ROB> --wyklucz T11\robocze --wynik <ROB>\t11_t9.txt` -> kod 0; samotest "nieznalezionych 0"; szukanych nazw 32, czlonow 42; przeszukanych plikow 30 (w tym ten plik i `t11_auto\auto_uklad.json`), wykluczonych 309 (`robocze\`); trafien calych nazw 0; czlonow do wyjasnienia 0. W tym pliku tylko liczby, sha16 i nazwy skanow syntetycznych.

### Sprzatanie

- 21:06 usuniete: `robocze\t11\eksport` (40 kopii skanow powtorki, 1,9 GB), `robocze\Cyrkon` (kopia puli `Prace_test`, 43 MB).
- Zostaja: baza `robocze\t11\dane\stanowisko.sqlite` z katalogiem `dane\` (logi, wyniki, podglady, pula_cache; 141 MB), `t11_auto\`, wszystkie pliki wynikow; `robocze\przerwany_1829\` W CALOSCI (dowod przerwania wg zlecenia - w tym `t11\eksport` z 40 kopiami skanow przerwanego przebiegu, 1,9 GB; do usuniecia decyzja koordynatora).

### Odstepstwa

- NOWE (wspolne T2 / T10 / T11, decyzja koordynatora nr 30): program z kopii repo przez `py.cmd`, nie z instalacji z paczki; ustawienia = kopia wzoru z wlasnymi sciezkami (`operatorzy = []`, adresy ramek ze wzoru).
- NOWE: czesc A z przebiegu 17:48 (wazna), czesc B i krok testow z powtorki 20:14 po przerwaniu o ok. 18:29 (przebieg B 17:53 niewazny; jego baza i logi w `robocze\przerwany_1829\`). Obie czesci na tym samym drzewie i danych; czesc B na swiezej bazie, wiec od przebiegu przerwanego nie zalezy.
- NOWE: seria rownolegle z T10 (tor 3) i z cudzym krokiem toru 2; plan "B nie z T2, T4, T10". Kryterium T11 nie zalezy od czasu.
- O6 (INFORMACJA, nie obniza wyniku przy 40 z 40): komunikat `niezgodny_uklad` bez pola na nazwe ukladu (wzor w `stanowisko\statusy.py` commita 0fedbf6 bez zmian wobec 571e186 w tym wierszu); galaz nie byla potrzebna (0 skanow `niezgodny_uklad`).
- Powtorek w ramach powtorki: 0.

**WERDYKT T11: ZAL z odstepstwem NOWE** - (a) 40 z 40 ZAL; (b) 0 ZAL; (c) 40 z 40 ZAL; czesc A i krok 4 zgodne z noca i 7ebb5cd; O6 = informacja.

Do decyzji koordynatora: (1) usuniecie kopii skanow przerwanego przebiegu (`robocze\przerwany_1829\t11\eksport`, 1,9 GB); (2) tekst planu T11 krok 1 "z_numerem ok = 40 z 40" - faktycznie 16 z 16 (jak w nocy i na 7ebb5cd).
