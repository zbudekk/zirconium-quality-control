WERDYKT T2: FAIL - tylko czesc (e): lista "do dofrezowania" 19 z 20, brakuje 1 = znany blad pozycji 8 (sha16 247ee785f428396f, gniazdo 4: praca z ubytkiem pokazana na zielono - ta sama przyczyna co w nocy 20/21.11 i na 7ebb5cd, czeka na decyzje wlasciciela; to JEDYNY brak); lista BEZ pozycji 8: 16 z 16 (lista = prawda); (a) 10 z 10 ZAL; (b) start analizy max 0,443 s, 9 z 9 ponizej 1 s ZAL; (c) mapa mediana 17,85 s ZAL, max 48,66 s = pierwsza plytka (okragla ramkowa, pula zimna; do 40 s: 0 z 1), kolejne 8 z 8 do 40 s (max 29,57 s); (d) przerwy petli max 67,4 ms, 0 ponad 200 ms ZAL; 2 plytki okragle ramkowe: 2 z 2 przyjete, uklad okragla_ramkowa_wieczorna, numery 1 i 3 z dolkow, kolory = prawda; JEDEN przebieg na commicie wydania 0fedbf6, kod sterownika 0, kod programu 0; obok liczyla instalacja T0 (tor 1), a w ostatnich 2 min takze T1 (tory 1 i 3); odstepstwa pomiaru O3, O4, O13 + NOWE (kopia repo zamiast paczki; testy uzupelniajace niewykonane)

# T2 KONCOWY - Wieczor od poczatku do konca - drzewo z repo na commicie wydania 0fedbf6 (21.11.2026), scenariusz t2_scenariusz_okragle.json

Pomiar, nie naprawa. Niczego w repo, testach, planie i narzedziach nie zmieniono; zadnych commitow.

- <DRZEWO> = <PC-katalog>\qc-wt\integ (detached 0fedbf6 = commit wydania 0.3.3; `git rev-parse --short HEAD` = 0fedbf6, `git status --short`
  o 17:37 pusty i o 17:48 pusty), <ST> = <DRZEWO>\Ramki\stanowisko, <ODB> = <DRZEWO>\Ramki\etap3\odbior_koncowy. Program NIE z paczki:
  `<PC-katalog>\koordynator\narz\py.cmd` z katalogu <ST> (decyzja koordynatora nr 30).
- <ROB> = <PC-katalog>\koordynator\robocze\odbior2\final\T2. Tor ciezkich krokow: 2 (`-Kto f2`).
- Start sesji: 17:37:10. Wolne na C na starcie: 36 GB (df -h /c: 931G / 896G / 36G, 97 %).
- Procesy python na starcie (17:37:26): tylko PID 12560 (znany, niczyj, 1 MB, bez sciezki). Wolny RAM 72602 MB z 95652.
- Znak konca dla serii T10 / T11: <ROB>\T2_KONIEC.txt zapisany 17:47:58 ("T2 KONIEC 2026-11-21 17:47:58 kod ciezki.ps1 (= kod sterownika) 0").

## 1. Przygotowanie (17:37:20 - 17:37:30)

- Pula projektow: `robocopy <PC-katalog>\app\Prace_test <ROB>\robocze\Cyrkon /E /NFL /NDL /NJH /NP` -> 17 plikow, 42,83 MB, 0 bledow.
- Wzor ustawien: <ROB>\ustawienia_wzor.toml = kopia <ST>\ustawienia.przyklad.toml; wierszy `^okragla_ramkowa`: 2.
- Pliki krokow: <ROB>\krok_gen.cmd, <ROB>\krok_t2.cmd = kopie plikow z przebiegu na 7ebb5cd (robocze\odbior2\T2) ze zmienionym TYLKO
  katalogiem roboczym (`robocze\odbior2\T2\` -> `robocze\odbior2\final\T2\`; zamiana w PowerShell `String.Replace`); kontrola: 0 wystapien
  starej sciezki, 6 i 8 wystapien nowej, 0 znakow `$`, konce linii CRLF (9 i 10 wierszy); katalog <ROB>\t2 przed startem nie istnial.
- Probnik procesow python co 5 s: <ROB>\robocze\narz\probnik.ps1 (kopia) -> <ROB>\t2_procesy.csv (powershell PID 20076; 125 probek
  17:37:32 - 17:47:55, w oknie przebiegu 115).

## 2. Krok generowania skanow plytek ramkowych (lekki, 1 proces): 17:37:31,80 - 17:38:09,20 (37,4 s) - kod 0

Polecenie (plik <ROB>\krok_gen.cmd, z katalogu <ST>):
`call <PC-katalog>\koordynator\narz\py.cmd narzedzia\symulator_skanera.py --tylko-generuj --scenariusz <ODB>\narzedzia\t2_scenariusz_okragle.json --katalog-generowanych <ROB>\robocze\gen --projekty <ROB>\robocze\Cyrkon > <ROB>\t2_gen.log 2>&1 < NUL`

- Log <ROB>\t2_gen.log: 2 wiersze "... zgodny ze scenariuszem" i "skany generowane zgodne ze scenariuszem: 2 z 2".
- nr 1: skan_okragla_ramkowa_wieczorna_n1_s5801, sha16 a7e5c5c7674cc140 (47 772 034 bajtow; numer 1, prac 9 w gniazdach
  1, 2, 3, 4, 5, 6, 8, 9, 10; z ubytkiem 6: gniazda 1, 2, 3, 4, 6, 8); nr 10: skan_okragla_ramkowa_wieczorna_n3_s5803, sha16
  13a7fc0c4e281de4 (45 478 784 bajtow; numer 3, prac 10 w gniazdach 1-6, 8-11; z ubytkiem 0).
- Kontrola `sha256sum` po przebiegu (17:48): STL 2 z 2 = sha16 ze scenariusza; pliki prawdy JSON d84a17e964e5de2b i 0cf82e7397858e21 =
  te same co w przebiegu na 7ebb5cd (2 z 2) - skany i prawda bajt w bajt jak poprzednio.

## 3. Przebieg pelny 10 x 60 s (JEDEN, bez powtorek): 17:38:20,78 - 17:47:58,57 (9 min 38 s), tor 2 - kod sterownika 0, kod programu 0

`powershell -NoProfile -ExecutionPolicy Bypass -File <PC-katalog>\koordynator\narz\ciezki.ps1 -Tor 2 -Kto f2 -Polecenie <ROB>\krok_t2.cmd`
(proces odlaczony: `Start-Process powershell ... -File <ROB>\robocze\narz\start_t2.ps1 -WindowStyle Hidden`, PID 13412; skrypt po powrocie
`ciezki.ps1` sam zapisal <ROB>\T2_KONIEC.txt i zatrzymal probnik). W pliku krok_t2.cmd (z katalogu <ST>, QT_QPA_PLATFORM=offscreen):
`call <PC-katalog>\koordynator\narz\py.cmd <ODB>\narzedzia\t2_wieczor.py --scenariusz <ODB>\narzedzia\t2_scenariusz_okragle.json --dane-generowane <ROB>\robocze\gen --ustawienia-wzor <ROB>\ustawienia_wzor.toml --roboczy <ROB>\t2 --projekty <ROB>\robocze\Cyrkon > <ROB>\t2_sterownik.log 2>&1 < NUL`

- ciezkie.log: "17:38:20 START f2 tor 2 | RAM 72666 MB", "17:47:58 KONIEC f2 tor 2 | kod 0 | RAM 68679 MB". kody.txt: "t2 KOD=0".
- przerwano: nie; blad sterownika: brak; pomiar_caly: true; platforma Qt offscreen; plikow 10 (dobrych 9, uciety 1 na pozycji 5); starty
  plikow w dzienniku symulatora co 59,999-60,000 s (17:38:23 ... 17:47:23). Zdarzenia srodowiska: 0 (log WARNING 4, ERROR 0; plytki ze
  statusem blad 0). 4 ostrzezenia (<ROB>\t2\t2_log_ostrzezenia.txt): brak pliku kalibracji ramek; "ukladu auto nie da sie wczytac
  (FileNotFoundError) - mapa bez pustych gniazd" (poz. 7); 2 x "zgaszenie ramki W / P przy zamknieciu nie doszlo" - te same 4 co w nocy
  i na 7ebb5cd.
- Procesy potomne po sprzataniu: []. Wynik: <ROB>\t2\t2_wynik.txt, t2_wynik.json; odczyt bazy (17:48, kod 0): <ROB>\t2_baza.txt
  (`<ROB>\odczyt_t2.cmd <DRZEWO> <ROB>\t2\dane\stanowisko.sqlite <ROB>\t2_baza.txt` = 4 zapytania przez `python.exe -I <ODB>\narzedzia\sql_odczyt.py`).

### (a) Obsluzone zgodnie z prawda: 10 z 10 - ZAL

| Poz. | sha16 | Oczekiwane | Faktyczne | Uklad (skany.uklad) | Numer (numer_zrodlo w bazie) | Prac program / prawda | start [s] | mapa [s] | czas_s (baza) | Zgodne |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | a7e5c5c7674cc140 | przyjety | przyjety | okragla_ramkowa_wieczorna | 1 (dolki) | 9 / 9 | 0,376 | 48,66 | 48,13 | TAK |
| 2 | 75db8c4f9ead0dab | przyjety | przyjety | okragla_wieczorna | 8 (dolki) | 9 / 9 | 0,414 | 16,10 | 15,58 | TAK |
| 3 | 9cc2bd761deb672b | przyjety | przyjety | wieczorna_r54 | 3 (podany) | 9 / 9 | 0,425 | 15,14 | 14,62 | TAK |
| 4 | 9d5eeb980330c768 | przyjety | przyjety | okragla_wieczorna_r54 | 8 (dolki) | 11 / 11 | 0,411 | 26,04 | 25,39 | TAK |
| 5 | 7ac82aa3d8bb0b63 | plik_odrzucony | plik_odrzucony (brak plytki, 1 zdarzenie scanner/plik_odrzucony) | - | - | - | - | - | - | TAK |
| 6 | 769e0fd025693694 | do_powtorzenia | do_powtorzenia, 0 zielonych | wieczorna | 2 (podany) | 8 / 8 | 0,399 | 12,64 | 12,12 | TAK |
| 7 | 857369c6c1d3aef3 | niezgodny_uklad | niezgodny_uklad, 0 zielonych | auto (uklad_zgodny 0) | - (nieznany) | 0 / 10 | 0,378 | 2,98 | 2,48 | TAK |
| 8 | 247ee785f428396f | przyjety | przyjety | wieczorna | 2 (podany) | 9 / 9 | 0,428 | 17,85 | 17,28 | TAK |
| 9 | c21b3b21066fab83 | plytka_nie_z_trybu | plytka_nie_z_trybu, 0 zielonych, pytanie plytka_nie_z_trybu | poranna | - (nieznany) | 10 / 10 | 0,443 | 29,57 | 28,97 | TAK |
| 10 | 13a7fc0c4e281de4 | przyjety | przyjety | okragla_ramkowa_wieczorna | 3 (dolki) | 10 / 10 | 0,419 | 25,59 | 25,02 | TAK |

Wszystkie 9 skanow w bazie: tryb wieczor, uklad_zrodlo = auto. Numery: odczytane przez program 4 (2 okragle testowe + 2 okragle
ramkowe), podane przez technika na pytanie programu 3 (kwadratowe), brak 2 (poz. 7 i 9) z 9 plikow dobrych. Pytania programu:
3 x brak_numeru_plytki, 1 x ponowny_skan (skan_id 7 = poz. 8, numer 2 po poz. 6; odpowiedz "to nowy wsad", zdarzenie
ui/ponowny_skan_odrzucony 1), 1 x plytka_nie_z_trybu (bez odpowiedzi - wg planu); odpowiedzi 4. Przy plytce ramkowej n3 (poz. 10) po
kwadratowej R54 n3 (poz. 3) pytania "ponowny skan" NIE bylo (jak na 7ebb5cd i w probie generalnej).
Zdarzenia w bazie: scanner/nowy_skan 9, scanner/plik_odrzucony 1, silnik/skan_przyjety 9, system/konflikt_projektu 5, system/podglad 8,
system/program_start 1, system/program_stop 1, ui/ponowny_skan_odrzucony 1 - liczby identyczne jak na 7ebb5cd (8 z 8 wierszy).

### (b) Start analizy od zapisu (prog 1 s): max 0,443 s; ponizej 1 s 9 z 9 plikow dobrych - ZAL

Wartosci [s]: 0,376 / 0,414 / 0,425 / 0,411 / 0,399 / 0,378 / 0,428 / 0,443 / 0,419. Plikow czekajacych w kolejce: 0 z 9.
(7ebb5cd: max 0,435 s, 9 z 9; noc: max 0,428 s, 9 z 9; proba generalna: max 0,459 s, 9 z 9.)

### (c) Mapa od zapisu (prog 40 s, mediana): mediana 17,85 s - ZAL; max 48,66 s

- PIERWSZA plytka (pula zimna; plytka okragla RAMKOWA n1): 48,66 s - do 40 s: 0 z 1 (czas analizy wg bazy 48,13 s; ta sama plytka na
  7ebb5cd: 51,60 s; proba generalna: 47,80 s i 47,65 s; noc - pierwsza plytka kwadratowa n1: 39,54 s). Ponizej odstepu 60 s - druga
  plytka nie czekala (start analizy poz. 2: 0,414 s).
- kolejne: 16,10 / 15,14 / 26,04 / 12,64 / 2,98 / 17,85 / 29,57 / 25,59 s - do 40 s: 8 z 8 (max 29,57 s; mediana kolejnych 16,98 s).
- wszystkie 9: mediana 17,85 s, max 48,66 s; do 40 s: 8 z 9.
- mapa w oknie (okno samo pokazalo plytke): zmierzono 3 z 9 (poz. 1, 7, 8: mediana 17,85 s, max 48,66 s); 6 z 9 NIE ZMIERZONO wg
  definicji sterownika (okno pokazywalo inna plytke przed kliknieciem sterownika).
- Kryterium mowi o medianie -> ZAL (7ebb5cd: mediana 18,63 s, max 51,60 s; noc: mediana 15,04 s, max 39,54 s; proba: 19,97 s, max 47,80 s).
  Pierwsza plytka ponad 40 s = sprawa znana (RAPORT.md 4a poz. 6: pierwsza plytka po zimnym starcie) - czwarty pomiar z rzedu ponad 40 s
  na plytce ramkowej (47,65 / 47,80 / 51,60 / 48,66 s): do decyzji koordynatora / wlasciciela, kryterium T2 jej nie obejmuje.

### (d) Przerwy petli okna (prog 200 ms): najdluzsza 67,4 ms; ponad 200 ms: 0 - ZAL

Tykniec 28703 (co 20 ms), 0 w srodku klikniecia; najdluzsze tykniecie sterownika 23,9 ms (klik przycisk_ukruszona).
Poza pomiarem: tykniecie zamykajace program 1619,2 ms. (7ebb5cd: 42,3 ms; noc: 34,7 ms; proba: 52,0 ms; we wszystkich 0 ponad 200 ms.)

### (e) Lista "do dofrezowania" wobec prawdy: 19 z 20 - lista = prawda NIE - FAIL (jedyny brak: znany blad pozycji 8)

- ubytki wg prawdy (prace z ubytkiem na 6 plytkach przyjetych): 20; program pokazal: czerwono 7, zolto 12, ZIELONO 1; inne 0;
  bez pracy w programie 0; na plytce nieobejrzanej 0.
- przeoczona: pozycja 8, gniazdo 4, sha16 247ee785f428396f (klasa z ekranu zielony, klasa w stanie programu zielony) - TA SAMA praca i
  ta sama przyczyna co w nocy 20/21.11 (noc: "1 z 26 prac z ubytkiem pokazana na zielono: poz. 8, gniazdo 4"), w probie i na 7ebb5cd.
- lista programu 19 pozycji; oczekiwanych 20; brakuje 1 ([247ee785f428396f, gniazdo 4]); nadmiarowych 0. To JEDYNY brak.
- OSOBNO, lista BEZ pozycji 8: pozycja 8 ma wg prawdy 4 prace z ubytkiem (czerwona 1: gniazdo 6, zolte 2: gniazda 1 i 9, zielona 1:
  gniazdo 4), z czego na liscie programu 3; pozostale 5 plytek przyjetych: oczekiwanych 16, w programie 16, brakuje 0, nadmiarowych 0
  -> 16 z 16, lista = prawda TAK (czerwone 6, zolte 10, zielone 0).
- prace cale wg prawdy 37: czerwone (falszywe alarmy) 0, zolte 0, zielone 37. Kolor z ekranu inny niz klasa w stanie programu: 0 z 57.
- klikniecia: "Ukruszona" 19 z 20 zaplanowanych; "OK" na falszywym alarmie 0 z 0; ponowien klikniec 0; czekan na ochrone mapy 5.
- per plytka (U czerwone / zolte / zielone; C zielone): poz. 1: U 2/4/0, C 3; poz. 2: U 1/2/0, C 6; poz. 3: U 2/1/0, C 6;
  poz. 4: U 1/3/0, C 7; poz. 8: U 1/2/1, C 5; poz. 10: U 0/0/0, C 10.

### Werdykty sterownika (t2_wynik.txt, doslownie)

  10 z 10 zgodnie z prawda: ZAL (10 z 10)
  start analizy < 1 s: ZAL
  mapa do 40 s (mediana): ZAL
  okno bez przerw > 200 ms: ZAL
  lista do dofrezowania = prawda: FAIL (lista = prawda: NIE; ubytki wg prawdy 20: program pokazal czerwone 7, zolte 12, zielone
    (przeoczone) 1, inne / brak pracy / nieobejrzane 0; nieklikniete przez technika 1 z 20; falszywe alarmy - cale wg prawdy na czerwono: 0 z 37)
  T2 LACZNIE: FAIL (4 z 5 kryteriow ZAL, 1 FAIL, 0 NIE ZMIERZONO)

### Dwie plytki okragle ramkowe (osobno)

| | Poz. 1 (n1, ziarno 5801) | Poz. 10 (n3, ziarno 5803) |
|---|---|---|
| sha16 | a7e5c5c7674cc140 | 13a7fc0c4e281de4 |
| status skanu | przyjety (oczekiwany przyjety) | przyjety (oczekiwany przyjety) |
| skany.uklad / uklad_zrodlo / uklad_zgodny | okragla_ramkowa_wieczorna / auto / 1 | okragla_ramkowa_wieczorna / auto / 1 |
| numer / numer_zrodlo (baza) | 1 / dolki (sterownik: "odczytany przez program"; pytan o numer 0) | 3 / dolki (pytan o numer 0) |
| prac program / prawda | 9 / 9 | 10 / 10 |
| kolory z ekranu wobec prawdy | z ubytkiem 6 z 6 wskazane: czerwone 2 (gniazda 4, 6), zolte 4 (gniazda 1, 2, 3, 8), zielone 0; cale 3 z 3 zielone (gniazda 5, 9, 10) | cale 10 z 10 zielone (gniazda 1-6, 8-11); czerwone 0, zolte 0 |
| baza prace.status_gniazda | czerwony 2 (gniazda 4, 6: ubytek), zolty 4 (1, 2, 3, 8: sprawdz), zielony 3 (5, 9, 10: ok) = ekran | zielony 10 (ok) = ekran |
| na liscie "do dofrezowania" | 6 z 6 (gniazda 1, 2, 3, 4, 6, 8; klikniecia "Ukruszona" wykonane) | 0 z 0 |
| start analizy / mapa / czas_s | 0,376 s / 48,66 s / 48,13 s (pierwsza, pula zimna) | 0,419 s / 25,59 s / 25,02 s |
| pytanie "ponowny skan" | nie (pierwszy skan) | NIE - mimo numeru 3 jak kwadratowa R54 n3 z pozycji 3 |

- Wynik 2 z 2 zgodny z prawda; wobec 7ebb5cd: statusy, uklad, numery, zrodlo numeru i kolor KAZDEGO gniazda bez roznic (19 z 19 gniazd).
- Ramka W: sterownik T2 nie uzywa atrapy ramki; program zglosil komunikat `ramka_wieczorna_niedostepna` (1 raz, 2,98 s po starcie).
  Czy ramka W dostala wynik plytki ramkowej: NIE ZMIERZONO w T2 (zakres T5 / proby na atrapie).

### Porownanie z przebiegiem na 7ebb5cd (16:05) i z noca (paczka 0.3.1, t2_scenariusz.json)

| Liczba | KONCOWY 0fedbf6 (17:47) | 7ebb5cd (16:05) | noc 20/21.11 |
|---|---|---|---|
| (a) zgodnie z prawda | 10 z 10 | 10 z 10 | 10 z 10 |
| (b) start analizy max; ponizej 1 s | 0,443 s; 9 z 9 | 0,435 s; 9 z 9 | 0,428 s; 9 z 9 |
| (c) mapa mediana / max | 17,85 s / 48,66 s | 18,63 s / 51,60 s | 15,04 s / 39,54 s |
| (c) pierwsza plytka / kolejne do 40 s | 48,66 s (ramkowa n1) / 8 z 8 (max 29,57 s) | 51,60 s (ramkowa n1) / 8 z 8 (max 26,71 s) | 39,54 s (kwadratowa n1) / 8 z 8 |
| (d) petla max; ponad 200 ms | 67,4 ms; 0 | 42,3 ms; 0 | 34,7 ms; 0 |
| (e) lista | 19 z 20 (brak: poz. 8 gniazdo 4) | 19 z 20 (ten sam brak) | 25 z 26 (ten sam brak) |
| (e) bez pozycji 8 | 16 z 16 | 16 z 16 | - |
| ubytki: czerwone / zolte / zielone | 7 / 12 / 1 | 7 / 12 / 1 | - |
| falszywe alarmy | 0 z 37 | 0 z 37 | - |
| kod sterownika / programu | 0 / 0 | 0 / 0 | - / 0 |

Wobec 7ebb5cd, plytka po plytce (10 z 10): status, uklad, numer, zrodlo numeru, liczba prac, liczba zielonych - 0 roznic; kolory gniazd
z ekranu - 0 roznic na 57 pracach; pytania programu ta sama piatka w tej samej kolejnosci. Czasy map plytek 9 i 10 dluzsze o 2,9 i 2,5 s
(29,57 wobec 26,71 s; 25,59 wobec 23,07 s) - obie liczone, gdy obok wystartowal T1 (patrz nizej); pozostale 7 w granicach -1,6 ... +0,4 s.

### Co jeszcze liczylo na PC w czasie przebiegu (17:38:20 - 17:47:58)

- Moje procesy (t2\t2_pid.txt + probnik): sterownik = program PID 29468 (szczyt 191 MB, CPU 10,6 s), silnik PID 2348 (szczyt 2541 MB,
  CPU 1416 s na 578 s zegara - analiza liczy na wiecej niz 2 watkach), symulator PID 668 (108 MB), PID 17092 (z t2_pid.txt, w probniku
  niewidoczny - krotki).
- CUDZE, tor 1 (`-Kto f1`, wykonawca T0 / T1; ciezkie.log): 17:38:41 - 17:39:42 `final\T0\krok_3.cmd` = INSTALACJA 0.3.3 w t0\odbior2
  (kod 10; pip 73 kol - w oknie pierwszej plytki 17:38:25 - 17:39:14); 17:40:19 - 17:40:22 `T0\krok_5.cmd` (kod 0); 17:44:26 - 17:44:32
  `T1\krok_1_3.cmd` (kod 0); od 17:46:00 `T1\krok_4.cmd` (bez wpisu KONIEC do 17:47:58) oraz na torze 3 od 17:45:58 `T1\krok_5.cmd`
  (bez wpisu KONIEC do 17:47:58). Poza ciezkie.log: krotkie procesy z instalacji t0\odbior2 (samokontrola / starty programu T0) o
  17:40:56 - 17:41:27 i 17:44:27 - 17:45:49.
- Probnik w oknie przebiegu: 72 rozne PID-y python, z tego 3 moje i PID 12560 (znany, niczyj, 1 MB, 0 s CPU) = 68 cudzych, w tym 15
  ze sciezka `t0\odbior2\Stanowisko\wersje\0.3.3\venv`. Najwieksze: PID 18208 (17:38:50 - 17:39:32, 28,6 s CPU - w oknie instalacji T0, najpewniej jej instalator);
  od 17:45:58 PID 29124 (39,5 s CPU do 17:47:55, 805 MB), PID 15568 (37,0 s CPU, 689 MB), PID 34364 (od 17:46:30, 128 s CPU, 1305 MB)
  i ok. 40 procesow krotkich (1 probka, do 1,6 s CPU) - wygladaja na T1 (pytest z procesami potomnymi); czyje dokladnie - nie ustalalem.
- Tor 4: w oknie przebiegu bez wpisow. Wolny RAM: 72666 MB na starcie, 68679 MB na koncu.
- Ta sesja w trakcie przebiegu: czytanie planu i wynikow (pliki tekstowe), zapis plikow .cmd T12, ok. 12 krotkich odczytow python
  (17:42:09 - 17:43:46: proba skryptu stanu bazy na instalacji z nocy - tylko odczyt, 2 x odczyt JSON przebiegu 7ebb5cd; kazdy ponizej
  1 s), 3 procesy powershell czekajace (probnik, start T2, kolejka T12 - czekala na tor 2 od 17:42:43, START krok_A 17:48:14, po T2).
- Wniosek: liczby czasowe (b), (c), (d) sa z przebiegu z instalacja T0 obok (pierwsze 1,5 min) i T1 obok (ostatnie 2 min); w nocy T2
  szedl sam. Wszystkie trzy mieszcza sie w kryterium, wiec powtorki nie zglaszam. Petla 67,4 ms (wobec 42,3 i 34,7 ms) i mapy plytek
  9 - 10 sa najpewniej pod wplywem T1; pierwsza plytka 48,66 s - liczona w czasie instalacji T0 (pip).

## 4. Odstepstwa

- O3, O4, O13 (RAPORT.md 4a) - sposob pomiaru sterownika, jak w nocy: program w procesie sterownika; okno offscreen; technik klika
  "Ukruszona" tylko na pracach czerwonych / zoltych (19 kliknietych: 7 czerwonych, 12 zoltych).
- NOWE (decyzja koordynatora nr 30, wspolne dla T2 / T10 / T11): program z kopii repo (0fedbf6 = commit wydania) przez `py.cmd`, nie z
  instalacji z paczki; ustawienia = kopia `ustawienia.przyklad.toml` zamiast `<K>\ustawienia.toml`; scenariusz
  `t2_scenariusz_okragle.json` + krok generowania skanow ramkowych (plan T2 opisuje `t2_scenariusz.json`).
- NOWE: testy uzupelniajace z planu T2 (`t2_petla.log`: 3 testy pytest) NIE WYKONANE - nie bylo ich w zleceniu tego przebiegu; plik
  `t2_wynik.md` z listy dowodow planu zastepuje ten WYNIK.md; kontroli `t9_dane_osobowe.py` i `dowody_lf.py` NIE uruchamialem.
- Polecenia planu zmienione: polecenie z sekcji T2 planu (`<K>\Polecenie.cmd ... --ustawienia-wzor <K>\ustawienia.toml`) zastapione
  poleceniem z POLECENIA.md sekcja 2 (wyzej, doslownie); nic poza tym.

## 5. Do decyzji koordynatora / wlasciciela

1. Czesc (e): FAIL przez znany blad pozycji 8 (praca z ubytkiem na zielono) - jak w nocy i na 7ebb5cd; bez pozycji 8 lista 16 z 16.
2. Pierwsza plytka (okragla ramkowa, pula zimna) 48,66 s > 40 s - czwarty pomiar z rzedu ponad 40 s, kazdy z cudzym ciezkim krokiem
   obok; kryterium T2 (mediana) spelnione. Liczba "na wolnym PC" nadal NIE ZMIERZONA.
3. Brak pytania "ponowny skan" przy plytce ramkowej n3 po kwadratowej R54 n3 (0 z 1 mozliwego) - jak poprzednio.
4. Ramka W przy plytce ramkowej: w T2 NIE ZMIERZONO.

## 6. Sprzatanie i stan koncowy

- Usuniete o 17:48 (duze pliki robocze): <ROB>\t2\eksport (10 kopii skanow, 468 MB), <ROB>\t2\zrodla (57 MB), <ROB>\robocze\gen
  (2 skany generowane + 2 pliki prawdy, 89 MB - odtwarzalne krokiem 2 w 40 s albo z `robocze\o3\t2_ramkowe`), <ROB>\robocze\Cyrkon
  (kopia puli projektow, 43 MB). <ROB> po sprzataniu: 29 MB.
- ZOSTAJA: baza <ROB>\t2\dane\stanowisko.sqlite (106 496 bajtow; potrzebna T8 / T9) z katalogiem `dane\` (logi programu, wyniki,
  podglady, pula_cache), t2_wynik.json, t2_wynik.txt, t2_symulator.json, t2_symulator.log, t2_log_ostrzezenia.txt, t2_pid.txt,
  ustawienia_t2.toml, <ROB>\t2_sterownik.log, t2_gen.log, t2_baza.txt, t2_procesy.csv, kody.txt, T2_KONIEC.txt, krok_gen.cmd,
  krok_t2.cmd, odczyt_t2.cmd, ustawienia_wzor.toml, robocze\narz\ (probnik.ps1, start_t2.ps1, zestaw_t2.py - pomocnik zestawiajacy
  wykonawcy, tylko odczyt JSON).
- Dane osobowe: w tym pliku tylko sha16 i nazwy skanow syntetycznych; kontrola automatyczna (t9) niewykonana.
- Procesy po T2 (17:48:40): 0 moich procesow python z T2 (sterownik, silnik, symulator zakonczone; probnik i start_t2 zakonczone);
  `git -C <PC-katalog>\qc-wt\integ status --short` o 17:48: pusty; HEAD 0fedbf6. Zadnych commitow.
