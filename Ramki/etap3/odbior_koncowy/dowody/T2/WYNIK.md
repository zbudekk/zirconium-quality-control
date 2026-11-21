WERDYKT T2: FAIL - czesc (e) lista "do dofrezowania" = prawda: NIE (1 z 26 prac z ubytkiem pokazana na zielono: poz. 8, gniazdo 4, sha16 247ee785f428396f; lista 25 z 26); (a) 10 z 10 ZAL; (b) start analizy max 0,428 s, 9 z 9 ponizej 1 s ZAL; (c) mapa mediana 15,04 s, max 39,54 s ZAL; (d) przerwy petli max 34,7 ms, 0 ponad 200 ms ZAL; kod programu 0; odstepstwa pomiaru O3, O4, O13

# T2 - Wieczor od poczatku do konca (odbior, 21.11.2026) - WYNIK wykonawcy

Paczka 0.3.1 (commit 571e186), instalacja wspolna <K> = <PC-katalog>\t0\odbior\Stanowisko (GOTOWE.txt 02:51:47).
<ROB> = <PC-katalog>\koordynator\robocze\odbior\T2; katalog sterownika --roboczy = <ROB>\t2 (nowy, nie istnial przed startem).
Tor ciezkich krokow: 2. Ta sama sesja wykonala przed T2 test T4 (koniec 04:17:18).

## Przygotowanie

- --projekty = <ROB>\robocze\Cyrkon: wlasna kopia <PC-katalog>\app\Prace_test (robocopy /E 04:17:36, kod 1 = skopiowano;
  15 folderow, 17 STL, 42,83 MB) - plan: "--projekty = kopia Prace_test"; folderu instalacji nie uzywam.
- Proba skrocona z pulapek planu ("pierwsze uruchomienie przez Polecenie.cmd zacznij od proby skroconej") NIE zostala
  wykonana przez te sesje: sterownik byl juz uruchomiony przez <K>\Polecenie.cmd na tej instalacji w T5 krok B4
  (03:01-03:03, 3 pozycje, kod 0), a zlecenie mowi: JEDEN przebieg wlasciwy = wynik testu.
- Stan przed startem (04:17:36): ciezkie.log - ostatni wpis "04:17:18 KONIEC T4 tor 2 | kod 0", brak blokad CIEZKI*.lock;
  Get-Process python: tylko PID 12012 (znany, niczyj, CPU 0,00 s); wolny RAM 74578 MB z 95652.

## Polecenie (plik krok_t2.cmd, przez blokade; polecenie planu doslownie, pelny scenariusz 10 pozycji co 60 s)

powershell -NoProfile -ExecutionPolicy Bypass -File <PC-katalog>\koordynator\narz\ciezki.ps1 -Tor 2 -Kto T2 -Polecenie <PC-katalog>\koordynator\robocze\odbior\T2\krok_t2.cmd

W pliku: set QT_QPA_PLATFORM=offscreen;
call <PC-katalog>\t0\odbior\Stanowisko\Polecenie.cmd <PC-katalog>\t0\repo\Ramki\etap3\odbior_koncowy\narzedzia\t2_wieczor.py --ustawienia-wzor <PC-katalog>\t0\odbior\Stanowisko\ustawienia.toml --roboczy <PC-katalog>\koordynator\robocze\odbior\T2\t2 --projekty <PC-katalog>\koordynator\robocze\odbior\T2\robocze\Cyrkon > <PC-katalog>\koordynator\robocze\odbior\T2\t2_sterownik.log 2>&1 < NUL
Probnik procesow python co 5 s (lekki, osobny powershell): t2_procesy.csv.

## Przebieg wlasciwy sterownika (JEDEN, bez powtorek): 04:17:52,78 - 04:27:21,54

- ciezkie.log: "04:17:52 START T2 tor 2 | RAM 74626 MB", "04:27:21 KONIEC T2 tor 2 | kod 0 | RAM 74831 MB".
- Kod wyjscia procesu sterownika (= procesu PROGRAMU, program biegnie w procesie sterownika - O3): **0** (kody.txt:
  "t2_sterownik KOD=0"; NIE 0xC0000409, NIE 0xC0000142). `kod_programu` w wyniku (wartosc zwrocona przez
  `aplikacja.main` przy zamknieciu): **0**. przerwano: nie; blad sterownika: brak; pomiar_caly: true.
- Platforma Qt: offscreen (O4). Plikow 10, odstep 60,0 s (starty plikow w dzienniku symulatora co 60,000 s:
  04:17:57,170 ... 04:26:57,173). Czas calosci 9 min 29 s (plan szacowal 11-13 min; program liczyl plytki szybciej:
  11-39 s).
- Zdarzenia srodowiska: 0 (log programu: WARNING 4, ERROR 0, slowa kluczowe srodowiska 0; plytki ze statusem blad 0;
  komunikaty bledow 0). 4 ostrzezenia (t2_log_ostrzezenia.txt): brak pliku kalibracji ramek; "ukladu auto nie da sie
  wczytac (FileNotFoundError) - mapa bez pustych gniazd" (plytka z niezgodnym ukladem, poz. 7); 2 x "zgaszenie ramki
  przy zamknieciu nie doszlo" (ramek nie ma).
- Procesy potomne po sprzataniu: []. Get-Process python po przebiegu (04:27:3x): tylko PID 12012 (znany, niczyj).

### (a) Obsluzone zgodnie z prawda: 10 z 10 -> ZAL

| Poz. | Kolejnosc | sha16 | Oczekiwane | Faktyczne | Uklad | Numer | Prac program / prawda | Zgodne |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 | df2e6a790700131d | przyjety | przyjety | wieczorna | 1 (podal technik) | 9 / 9 | TAK |
| 2 | 2 | 75db8c4f9ead0dab | przyjety | przyjety | okragla_wieczorna | 8 (odczytal program) | 9 / 9 | TAK |
| 3 | 3 | 9cc2bd761deb672b | przyjety | przyjety | wieczorna_r54 | 3 (podal technik) | 9 / 9 | TAK |
| 4 | 4 | 9d5eeb980330c768 | przyjety | przyjety | okragla_wieczorna_r54 | 8 (odczytal program) | 11 / 11 | TAK |
| 5 | 5 | 6b0e98d5073f7c98 | plik_odrzucony | plik_odrzucony (brak plytki, 1 zdarzenie scanner/plik_odrzucony) | - | - | - | TAK |
| 6 | 6 | 769e0fd025693694 | do_powtorzenia | do_powtorzenia, 0 zielonych | wieczorna | 2 (podal technik) | 8 / 8 | TAK |
| 7 | 7 | 857369c6c1d3aef3 (plik pochodny; zrodlo 297bb695e2e69db0) | niezgodny_uklad | niezgodny_uklad, 0 zielonych | auto | - | 0 / 10 | TAK |
| 8 | 8 | 247ee785f428396f | przyjety | przyjety | wieczorna | 2 (podal technik) | 9 / 9 | TAK |
| 9 | 9 | c21b3b21066fab83 | plytka_nie_z_trybu | plytka_nie_z_trybu, 0 zielonych, pytanie plytka_nie_z_trybu | poranna | - | 10 / 10 | TAK |
| 10 | 10 | 8358e17160a25742 | przyjety | przyjety | okragla_wieczorna_r54 | 8 (odczytal program) | 10 / 10 | TAK |

Numery plytek: odczytane przez program 3 (okragle), podane przez technika na pytanie programu 4 (kwadratowe), brak 2
(poz. 7 i 9 - program nie pyta) z 9 plikow dobrych. Pytania programu: 4 x brak_numeru_plytki, 2 x ponowny_skan
(odpowiedz "to nowy wsad"), 1 x plytka_nie_z_trybu (bez odpowiedzi - wg planu); odpowiedzi udzielonych 6.

### (b) Start analizy od zapisu (prog 1 s): max 0,428 s; ponizej 1 s: 9 z 9 plikow dobrych -> ZAL

Wartosci [s] (kolejnosc podawania): 0,428 / 0,413 / 0,422 / 0,414 / 0,423 / 0,368 / 0,372 / 0,417 / 0,380.
Plikow zapisanych, gdy program liczyl poprzednia plytke: 0 (kolejka przy zapisie 0 w 9 z 9).

### (c) Mapa od zapisu (prog 40 s, mediana): mediana 15,04 s; max 39,54 s -> ZAL

- pierwsza plytka (pula zimna): 39,54 s (do 40 s: 1 z 1; czas analizy wg programu 38,96 s) - zapas do progu 0,46 s;
- kolejne: 19,10 / 15,04 / 22,05 / 11,57 / 2,85 / 15,04 / 24,39 / 14,45 s (do 40 s: 8 z 8; max 24,39 s);
- mapa w oknie (okno samo pokazalo plytke): zmierzono 3 z 9 (39,54 / 2,85 / 15,04 s); w 6 z 9 okno pokazywalo inna
  plytke (technik ogladal poprzednia) - NIE ZMIERZONO wg definicji sterownika.
- Pomiar = gorne ograniczenie (odczyt stanu co 20 ms) - O3.

### (d) Przerwy petli okna (prog 200 ms): najdluzsza 34,7 ms; ponad 200 ms: 0 -> ZAL

Tykniec 28281 (co 20 ms), 0 w srodku klikniecia; najdluzsze tykniecie sterownika w trakcie pomiaru 27,5 ms (klik
przycisk_ukruszona). Poza pomiarem (wg definicji sterownika i O3): start programu przed pokazaniem okna oraz tykniecie
zamykajace program = 1331,6 ms (odczyt stanu koncowego + QApplication.quit(); w T5 B4 bylo 350,2 ms) - podaje do
wiadomosci, nie jest przerwa petli w trakcie pracy. Okno offscreen (O4).

### (e) Lista "do dofrezowania" wobec prawdy: lista = prawda NIE -> **FAIL** (1 przeoczona z 26)

- ubytki wg prawdy (prace z ubytkiem na 6 plytkach przyjetych): 26; program pokazal: czerwono 10, zolto 15,
  ZIELONO (przeoczone) 1; inne / brak pracy / plytka nieobejrzana 0.
- przeoczona: pozycja scenariusza 8, gniazdo 4, sha16 skanu 247ee785f428396f (piksel #3cb44b, klasa "zielony",
  klasa w stanie programu "zielony").
- prace cale wg prawdy: 31; falszywe alarmy (cale na czerwono): 0 z 31; cale na zolto: 0; cale na zielono: 31.
- kolor z ekranu inny niz klasa w stanie programu: 0 z 57 prac.
- lista programu: 25 pozycji; oczekiwanych 26; brakuje 1 ([247ee785f428396f, gniazdo 4]); nadmiarowych 0.
- klikniecia: "Ukruszona" wykonanych 25 z 26 zaplanowanych (1 nieklikniete - praca zielona); "OK" na falszywym
  alarmie 0 z 0; **ponowien klikniec przez ochrone klikniec: 0**; czekan na zdjecie ochrony mapy: 5.
- per plytka (U = z ubytkiem wg prawdy: czerwone / zolte / zielone; C = cale: zielone): poz. 1: U 2/4/0, C 3;
  poz. 2: U 1/2/0, C 6; poz. 3: U 2/1/0, C 6; poz. 4: U 1/3/0, C 7; poz. 8: U 1/2/1, C 5; poz. 10: U 3/3/0, C 4.
- Wynik jest ten sam co sygnal z T5 krok B4 (03:03, 3 skany: ta sama praca, gniazdo 4 zielone).

### Werdykty sterownika (t2_wynik.txt, doslownie)

  10 z 10 zgodnie z prawda: ZAL (10 z 10)
  start analizy < 1 s: ZAL
  mapa do 40 s (mediana): ZAL
  okno bez przerw > 200 ms: ZAL
  lista do dofrezowania = prawda: FAIL (lista = prawda: NIE; ubytki wg prawdy 26: czerwone 10, zolte 15, zielone
    (przeoczone) 1; nieklikniete przez technika 1 z 26; falszywe alarmy 0 z 31)
  T2 LACZNIE: FAIL (4 z 5 kryteriow ZAL, 1 FAIL, 0 NIE ZMIERZONO)

## Baza i wyniki T2 (ZOSTAJA - potrzebne T8 i T9)

- baza: <PC-katalog>\koordynator\robocze\odbior\T2\t2\dane\stanowisko.sqlite (106496 bajtow; skany 9, zdarzenia:
  scanner/nowy_skan 9, scanner/plik_odrzucony 1, silnik/skan_przyjety 9, system/konflikt_projektu 5, system/podglad 8,
  system/program_start 1, system/program_stop 1, ui/ponowny_skan_odrzucony 2)
- log programu: ...\T2\t2\dane\logi\stanowisko.log (+ silnik.log); wyniki analiz: ...\T2\t2\dane\wyniki\ (9 plikow JSON);
  lista: ...\T2\t2\dane\do_dofrezowania_biezaca.csv; ustawienia przebiegu: ...\T2\t2\ustawienia_t2.toml.

## Testy uzupelniajace (PO sterowniku; krok_t2_uzup.cmd przez ciezki.ps1 -Tor 2; 04:27:40 - 04:31:49; nie zastepuja sterownika)

A. Przez `pytest_instalacja.py` (polecenie koordynatora: kod programu z INSTALACJI) - log t2_petla.log:
- `call <K>\Polecenie.cmd <ODB>\narzedzia\pytest_instalacja.py --st <ST> --wynik <ROB>\t2_zrodlo_kodu_1.txt -- <ST>\testy\test_aplikacja.py -q -s -p no:cacheprovider --rootdir <ST> -k "test_skany_odniesienia_przez_cala_aplikacje_w_petli_qt or test_f_petla_qt_bez_przerw_podczas_analizy_10_plytek"`
  -> kod 0; "2 passed, 27 deselected in 107.17s"; WERDYKT ZRODLA KODU: INSTALACJA (43 moduly z instalacji, 0 z repo;
  pliki *.py instalacji = repo: 79 z 79); kryterium f: najdluzsza przerwa petli Qt 49 ms (prog 200 ms); skany
  odniesienia w petli Qt: najdluzsza przerwa 17 ms.
- `... --wynik <ROB>\t2_zrodlo_kodu_2.txt -- <ST>\testy\test_ui_wieczor.py -q -s -p no:cacheprovider --rootdir <ST> -k "test_6_petla_okna_bez_przerw_10_plytek_po_19_prac"`
  -> kod 0; "1 passed, 88 deselected in 9.94s"; INSTALACJA (54 moduly, 0 z repo); najdluzsza przerwa petli okna 49 ms
  (prog 200 ms), odswiezenie ekranu maks. 8 ms (prog 100 ms).

B. Polecenia planu DOSLOWNIE (`call <K>\Polecenie.cmd -m pytest <ST>\testy\... --rootdir <ST> -k ...`; kod programu z repo
   przez conftest - ten sam commit) - log t2_petla_plan.log:
- test_aplikacja.py: kod 0; "2 passed, 27 deselected in 114.99s"; przerwa petli Qt 49 ms / 17 ms.
- test_ui_wieczor.py: kod 0; "1 passed, 88 deselected in 9.91s"; przerwa petli okna 72 ms.

Zmienne: E3A3_DANE_REF=<PC-katalog>\app\dane_ref\syntetyczne_R59_P2, E3A3_PROJEKTY=<ROB>\robocze\Cyrkon. Razem 6 z 6
passed (3 + 3), 4 kody 0, zjawisk 0xC0000409 / 0xC0000142 nie bylo.

## Praca przeoczona - fakty (tylko odczyt; niczego nie zmieniano w kodzie, progach, scenariuszu ani prawdzie)

Przedmiot: pozycja 8 scenariusza, skan sha16 247ee785f428396f (zestaw syntetyczne_R59_P2, plytka "wieczorna" nr 2,
ziarno 102), gniazdo 4 (klasa fi 12), projekt sha16 2e15189ef6d12701. Program pokazal prace na ZIELONO.

### 1. Co mowi prawda i skad pochodzi

- Plik prawdy obok skanu (JSON z 14.11.2026 20:36) zapisal generator skanow sztucznych programu (`stanowisko/synth.py`,
  `generuj_plytke` -> `wytnij_ubytek`) w chwili tworzenia skanu - zestawy raportu R59, przed uruchomieniem programu.
  Ubytki generator wycial w siatce; nikt ich nie ocenial recznie.
- Praca w gniezdzie 4 ma w prawdzie 2 ubytki, oba `wykrywalny: true`, `widoczny: true`:
  (1) srednica 0,926 mm, glebokosc 0,324 mm, klasa "sciana", odleglosc od linii brzegu 1,5049 mm (wg rekordu T10);
  (2) srednica 0,241 mm, glebokosc 0,084 mm, klasa "krawedz", odleglosc od linii brzegu 0,0131 mm.
- Znacznik `wykrywalny` generatora = glebokosc >= [inspect] prog_glebokosci_mm (0,08) i srednica w zakresie [inspect]
  srednica_min / max (0,2-1,5 mm) i ubytek widoczny; NIE uwzglednia polozenia wzgledem pasa brzegu (kod
  `Opcje.wykrywalny`). Ubytek (2) jest tuz nad dolnymi granicami specyfikacji (0,241 wobec 0,2 mm; 0,084 wobec 0,08 mm).
- Na tej plytce prawda ma 4 prace z ubytkiem (gniazda 1, 4, 6, 9): program pokazal 1 zolto, 6 czerwono, 9 zolto,
  4 zielono.

### 2. Jak te prace ocenia silnik

- T10 z dzisiaj (`...\odbior\T10\t10\t10_surowe_metryki.json`, rekord skanu / gniazdo 4): status gniazda "zielony",
  inspekcja "ok", wykrytych ubytkow 0, top-1 trafny; odchylki: punkty 19143, rms 0,0513 mm, mediana -0,0012 mm,
  udzial_pod 0,0413, udzial_nad 0,004; linia brzegu "wiarygodna" (filar 1, 18,28 mm, sprawdzony 1,0); oba ubytki
  prawdy: status_inspekcji "ok", trafione: A nie, B nie, dowolny nie.
- Wynik analizy W PROGRAMIE (T2: `...\T2\t2\dane\wyniki\20261121_042515_247ee785f428396f_wynik.json`, gniazdo 4):
  status "zielony", inspekcja "ok", ubytki [] - ale silnik ZNALAZL plame w miejscu ubytku (1): srednica 0,839 mm,
  glebokosc 0,394 mm, 726 punktow, ostra krawedz, odleglosc od brzegu 1,569 mm, **rodzaj "poza_pasem"**; oraz wciecie
  0,2456 mm o szerokosci 0,178 mm, rodzaj "za_male" (w tym samym miejscu). Ubytku (2) nie ma ani w plamach, ani we
  wcieciach.
- Regula w kodzie (`stanowisko/inspect.py`, odczyt): plama z odlegloscia od brzegu > [inspect] pas_brzegu_mm i nie na
  krawedzi dostaje rodzaj "poza_pasem" (nie jest ubytkiem); wciecie wezsze niz srednica_min_mm = "za_male". Ustawienia
  instalacji: pas_brzegu_mm = 1,5; srednica_min_mm = 0,2; prog_glebokosci_mm = 0,08; wciecie_min_mm = 0,2.
  Czyli: ubytek (1) lezy 0,069 mm poza pasem brzegu sprawdzanym przez inspekcje (1,569 wobec 1,5 mm) - silnik go
  widzi, ale wg progu nie zglasza; prawda oznacza go jako wykrywalny, bo znacznik nie zalezy od polozenia.
- Raport R59 (`<REPO>\Ramki\stanowisko\raporty\R59_2026-11-14.md`): przeoczenia sa udokumentowane na poziomie UBYTKOW,
  nie prac: pkt 6.1 / 6.2 - wykrycie "dowolna metoda" w scenariuszu "dobrze" 219 z 245 (26 ubytkow niewykrytych;
  "o 0,1 pkt za nisko ... progow nie ruszano"); pkt 6.3 wniosek 2: "5 z 7 pominietych ubytkow [fi 12] nalezy do
  jednego projektu (2e15189ef6d12701, w fi 12: 12 / 17)" - to TEN projekt i ta klasa gniazda. Listy "niewykryte" z
  nazwa skanu / gniazda w raporcie nie ma (szukanie "s0102", "niewykryt", "poza_pasem": 0 trafien); raport nie podaje
  tez licznika "praca z ubytkiem cala na zielono".
- Policzone z rekordow T10 (40 skanow R59, scenariusz "dobrze"): 165 prac z ubytkiem w prawdzie -> czerwone 64,
  zolte 99, ZIELONE 2 (obie z ubytkiem wykrywalnym): ta praca oraz zestaw P2, plytka poranna nr 5, ziarno 205,
  gniazdo 18 (fi 15; 1 ubytek 0,37 mm na krawedzi). Kryterium T10 (wyrownanie, top-1, falszywe czerwone) tego nie
  obejmuje.

### 3. Powtarzalnosc i roznica T10 / program

- Ten sam skan przez narzedzie pomiarowe T10 3 razy (krok_t2_powt.cmd, 04:31:55 - 04:34:09, 3 kody 0;
  `call <K>\Polecenie.cmd narzedzia\metryki_P3a.py --skany <PC-katalog>\app\dane_ref\syntetyczne_R59_P2 --wzorzec
  skan_wieczorna_n2_s0102.stl --projekty <PC-katalog>\app\Prace_test --wyjscie <ROB>\robocze\powt --nazwa powt_<i>.json
  --procesy 1 --ustawienia <K>\ustawienia.toml`): gniazdo 4 "zielony" / inspekcja "ok" **3 z 3**; liczby identyczne
  w 3 probach i z T10 (rms 0,0513 mm, udzial_pod 0,0413; statusy plytki: zielony 6, czerwony 1, zolty 2).
- W programie: zielone 2 z 2 przebiegow (T5 krok B4 03:03 i T2 04:25), wynik gniazda 4 identyczny co do cyfry (plama
  0,839 / 0,394 / 1,569 mm "poza_pasem").
- Roznice sciezki T10 (narzedzie) wobec programu: wspolczynnik 1,22 (srednia z prawdy) wobec 1,225 w programie (korekta
  skali -0,39 %, ostrzezenie o skali w uwagach gniazda); uklad z prawdy wobec rozpoznania "auto" (wybrany "wieczorna",
  pewny); numer plytki: narzedzie go nie podaje, w programie podal go technik na pytanie; pula: te same 17 STL (folder
  wobec kopii folderu). Skutek dla gniazda 4: BRAK roznicy statusu (zielony / ok w obu), odchylki rms 0,0513 wobec 0,0515 mm,
  udzial_pod 0,0413 wobec 0,0415. Statusy pozostalych 8 gniazd plytki tez te same (1 czerwone, 2 zolte, 5 zielonych).
- Wniosek z faktow (bez oceny): wynik jest powtarzalny (6 z 6 analiz: T10, 3 powtorki narzedziem, 2 przebiegi programu) i nie zalezy od sciezki; praca jest na zielono,
  bo jedyny ubytek o rozmiarze wyraznie ponad progi lezy 0,07 mm poza pasem brzegu 1,5 mm, a drugi (0,24 x 0,08 mm)
  nie zostal znaleziony.

## Co jeszcze liczylo na PC

- Sterownik (04:17:52 - 04:27:21), probnik t2_procesy.csv (501 probek co 5 s): procesy tego kroku - sterownik = program
  PID 18548 (szczyt zbioru roboczego 264 MB), proces silnika PID 10720 (szczyt 3081 MB, CPU 1300 s), symulator PID 16120
  (128 MB), procesy posrednie venv 11052 i 28720 (po 8 MB). Probnik oznacza interpreter bazowy jako "INNE" (proces
  potomny python.exe z venv instalacji) - to procesy T2. Obce: PID 12012 (znany, niczyj, CPU 0,00 s); PID 36564 -
  1 probka o 04:17:52 (13 MB, CPU 0,0 s, bez sciezki), przed pierwszym plikiem symulatora. Zadnego obcego procesu
  python liczacego w trakcie pomiaru. ciezkie.log: w czasie T2 zaden inny ciezki krok (inne tory puste od 03:48:55).
- Wolny RAM: 74626 MB na starcie, minimum 71699 MB. Ta sesja w trakcie sterownika: tylko odczyty plikow i zapis
  plikow wyniku T4 (PowerShell / bash), bez pythona.
- Testy uzupelniajace i 3 powtorki skanu: bez probnika; przed kazdym krokiem Get-Process python = tylko PID 12012.
- Po wszystkich krokach (04:35:30): Get-Process python = tylko PID 12012; swoich procesow nie zostawilem.

## Odstepstwa i polecenia planu

- O3 (program w procesie sterownika, kopia ustawien, mapa = gorne ograniczenie, start programu poza pomiarem petli),
  O4 (okno offscreen; zegar sterownika wliczony w przerwy), O13 (technik klika tylko czerwone / zolte; zalozenie, ze
  prace zolta technik zawsze zauwazy: 15 z 25 kliknietych ubytkow bylo zoltych, 10 czerwonych) - dotycza czesci
  (a)-(d) i sposobu liczenia (e). Sprawa 3 z RAPORT.md 4a (pierwsza plytka ponad 40 s, druga czeka w kolejce) NIE
  wystapila w T2: pierwsza plytka 39,54 s, zadna plytka nie czekala w kolejce.
- NOWE odstepstwa: brak.
- Polecenia planu zmienione: sterownik - bez zmian (doslownie). Testy uzupelniajace - wykonane w OBU postaciach:
  przez pytest_instalacja.py (zlecenie koordynatora) i doslownie wg planu. Proba skrocona z "pulapek" pominieta (powod
  w sekcji "Przygotowanie").
- Roznica wobec tekstu planu: czas sterownika 9 min 29 s zamiast 11-13 min (bez wplywu na wynik).

## Do decyzji koordynatora / wlasciciela

1. T2 = FAIL w czesci (e): 1 z 26 prac z ubytkiem pokazana na zielono (poz. 8, gniazdo 4). Fakty wyzej. Do decyzji
   wlasciciela: czy to wada programu (pas brzegu 1,5 mm), czy wada prawdy scenariusza (znacznik "wykrywalny" generatora
   nie zna pasa brzegu; ubytek na granicy pasa) - wykonawca niczego nie zmienial i nie rozstrzyga.
2. Na 40 skanach R59 (T10) sa 2 prace z ubytkiem wykrywalnym cale na zielono (2 z 165 w scenariuszu "dobrze"); raport
   R59 podaje tylko liczniki ubytkow (219 z 245), nie prac - do rozwazenia jako osobna liczba dla wlasciciela.
3. Pierwsza plytka T2 po zimnym starcie: 39,54 s - 0,46 s ponizej progu 40 s (w T5 B4 ta sama plytka: 54,12 s; w T4
   pierwsza plytka z pula 400 wpisow: 65,16 s). Mediana i tak ZAL; informacja do sprawy 3 w RAPORT.md 4a.
4. Tykniecie zamykajace program 1331,6 ms (poza pomiarem wg O3; w T5 B4: 350,2 ms) - zamykanie programu trwa ponad 1 s.
5. T9 na plikach T2: 0 trafien calych nazw; 1 "czlon do wyjasnienia" w WYNIK.md (zwykle slowo bedace czescia nazwy -
   narzedzie nie podaje ktore; t2_t9.txt).

## Dowody w <ROB> (bez STL / baz: te zostaja w <ROB>\t2 i <ROB>\robocze)

t2_wynik.json, t2_wynik.txt, t2_sterownik.log, t2_symulator.json, t2_log_ostrzezenia.txt (kopie z <ROB>\t2 po kontroli T9),
t2_petla.log, t2_petla_plan.log, t2_zrodlo_kodu_1.txt, t2_zrodlo_kodu_2.txt, t2_wynik.md, t2_procesy.csv, t2_t9.txt,
kody.txt, krok_t2.cmd, krok_t2_uzup.cmd, krok_t2_powt.cmd, WYNIK.md. Robocze (nie dowody): <ROB>\t2\ (eksport ze skanami,
baza, podglady, wyniki, log programu - 565 MB), <ROB>\robocze\ (Cyrkon - kopia projektow, powt\ - 3 powtorki, probnik).

## Kontrola dowodow (kopia w robocze\dowody_kontrola; oryginaly w <ROB> bez zmian) - 04:38

- t9_dane_osobowe.py na kopii 17 plikow dowodow, BEZ --dozwolone: kod 0, 0 trafien calych nazw, 2 trafienia jednego
  czlonu do wyjasnienia (WYNIK.md) -> ZAL (robocze\t9_dowody.txt). Wczesniej (04:35) te same pliki zrodlowe z <ROB>\t2:
  kod 0, 0 trafien (t2_t9.txt).
- dowody_lf.py --napraw na kopii: kod 0, "plikow 17, naruszen 0 (po naprawie)"; CRLF -> LF w 9 plikach, bajtow spoza
  ASCII 0 w 17 z 17 (robocze\dowody_lf.txt). W <ROB> logi maja nadal CRLF - przed `git add` trzeba wykonac
  `dowody_lf.py --napraw` wg planu.
