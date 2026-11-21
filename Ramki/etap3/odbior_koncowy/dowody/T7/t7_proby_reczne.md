# T7 czesc B - proby reczne na programie z paczki (odbior 21.11.2026)

Oznaczenia: `<K>` = `<PC-katalog>\t0\odbior\Stanowisko` (instalacja WSPOLNA, wersja 0.3.1), `<K12>` = `<PC-katalog>\t0\odbior_t12\Stanowisko`
(instalacja T12 po zakonczeniu T12: wersja biezaca 0.3.1 po powrocie), `<ROB>` = `<PC-katalog>\koordynator\robocze\odbior\T7`,
`PY` = `<PC>\AppData\Local\Programs\Python\Python312\python.exe`, `<ODB>` = `<PC-katalog>\t0\repo\Ramki\etap3\odbior_koncowy`.
Kazda proba ma WLASNY plik ustawien `<ROB>\ustawienia_<proba>.toml` (kopia `ustawienia.toml` instalacji, 11 z 11 kluczy `[sciezki]`
przestawionych na `<ROB>\robocze\<proba>\...`; `folder_cyrkon` = `<ROB>\robocze\Cyrkon` = wlasna kopia `<PC-katalog>\app\Prace_test`:
15 folderow, 17 STL) i wlasna, pusta na starcie baze `<ROB>\robocze\<proba>\dane\stanowisko.sqlite`. Wszedzie `set QT_QPA_PLATFORM=offscreen`.
Odczyt bazy: `PY -I <ODB>\narzedzia\sql_odczyt.py --baza <baza> "<SELECT>"`. Wyciagi logow programu: `t7_<proba>_log_programu.txt`.

## Podsumowanie

| Proba | Zdarzenie | Slad komunikatu na programie z paczki | Dalsza praca | Stan odtworzony (liczby) | Wynik proby |
|---|---|---|---|---|---|
| B1 | brak folderu "Cyrkon" (bez skanu) | samokontrola: kod 1, `BLAD folder_cyrkon: brak folderu projektow Cyrkon ...`; w logu programu `pula_brak_folderu`: 0 wierszy (program nie pisze komunikatow ekranu do logu, a ten komunikat pokazuje tylko, gdy czeka skan) | program 30 s bez folderu: kod 0, `Traceback` 0; po przywroceniu folderu samokontrola kod 0 (ZIELONA), program kod 0 | zdarzenia 2 -> 4 (program_start 2, program_stop 2) | wykonana; oczekiwanie planu "komunikat w logu" NIESPELNIONE doslownie (0 wierszy) - patrz B1b |
| B1b (uzupelnienie) | brak folderu "Cyrkon" + 1 skan czeka | komunikat ekranu NIE ZMIERZONY (nie ma go w logu ani w zdarzeniach); slady: skan przyjety do kolejki (`nowy_skan` 1), bez wyniku przez 78 s, `program_stop {"niezakonczone": 1}` | program dziala 90 s bez folderu (kod 0), skan nie ginie | po przywroceniu folderu i starcie: "start, zadan wznowionych 1, plikow znanych 1", skan przeanalizowany (56,3 s): 1 z 1 ma status w bazie; `nowy_skan` nadal 1 (bez duplikatu); pliku `zadania_niezakonczone.json` nie ma | zgodna z oczekiwaniem (skan czeka i wraca) |
| B2 | `Stop-Process` procesu programu po zapisie 2. skanu | `wznowiono` tylko na ekranie (w logu 0 razy - jak w planie); w logu `nowy skan nr 1: ... (plik zastany - nadrabianie)` dla 2. skanu; w bazie `nowy_skan` z `"zastany": true` (1 raz) | po ponownym starcie program przyjal skany 2, 3, 4; kod wyjscia 0 po `--zamknij-po 600` | **4 skany z 4** maja status w bazie (po 3 min 45 s od startu symulatora); przy starcie "plikow znanych 1" (1. skan z bazy - nieliczony drugi raz); `zadania_niezakonczone.json`: brak; 3 z 3 procesow programu nie zyje po 1,5 s | zgodna z oczekiwaniem planu |
| B3 | `Stop-Process` procesu silnika w 8. sekundzie analizy 2. skanu | log: `analiza skanu <sha16> nie dala wyniku (proces)`; baza: zdarzenie `blad_analizy` z opisem "proces: proces silnika zakonczyl sie w trakcie analizy (kod wyjscia 4294967295); analiza przerwana" i `blad_analizy_rodzaj` `{"rodzaj": "proces"}`; skan 2 status `blad` | nowy proces silnika wystartowal w tej samej sekundzie (03:21:29); **3. skan przyjety** (wynik po 34,0 s); program dziala do `--zamknij-po 600`, kod 0 | 3 skany z 3 maja status w bazie (2 z wynikiem, 1 `blad`); start kontrolny po probie: "plikow znanych 3", skany nadal 3, nic nie analizowane ponownie | zgodna z oczekiwaniem planu (pierwsze wykonanie) |

Status wszystkich przeanalizowanych skanow: `plytka_nie_z_trybu` - skany z `<PC-katalog>\app\dane_ref\syntetyczne_R59_P2` (zrodlo z planu) to
plytki poranne, a program startuje w trybie "Wieczor". Analiza jest pelna (23-56 s, `"prace": 12`), ale proby NIE obejmuja skanu ze
statusem "przyjety" - do wiadomosci koordynatora (kryterium proby w planie: "4 skany z 4" / "3. skan ma status w bazie").

## B1 - brak folderu "Cyrkon" (plik `krok_B1.cmd`, 03:03:17-03:04:32, krok lekki bez blokady, instalacja wspolna `<K>`)

| Nr | Polecenie | Kod | Wynik | Log |
|---|---|---|---|---|
| 0 | `<K>\Polecenie.cmd -m stanowisko.samokontrola --ustawienia <ROB>\ustawienia_b1.toml --bez-sieci` (stan wyjsciowy, folder jest) | 0 | `SAMOKONTROLA: ZIELONA (ok 17, ostrzezenia 4)` - pierwsze wykonanie polecenia w tej postaci (zasada 3) | `t7_b1_0_samokontrola_z_folderem.log` |
| 1 | `ren <ROB>\robocze\Cyrkon Cyrkon_x` | 0 | | |
| 2 | `<K>\Polecenie.cmd -m stanowisko.aplikacja --ustawienia <ROB>\ustawienia_b1.toml --zamknij-po 30` | 0 | 33,2 s; konsola pusta; log programu: start, zamkniecie "zadan niezakonczonych 0", `Traceback` 0; **`pula_brak_folderu` w logu: 0 wierszy**; zdarzenia w bazie: 2 | `t7_b1_1_program_bez_folderu.log`, `t7_b1_log_programu.txt`, `t7_b1_baza.txt` |
| 3 | `<K>\Polecenie.cmd -m stanowisko.samokontrola --ustawienia <ROB>\ustawienia_b1.toml --bez-sieci` (folderu nie ma) | **1** | `BLAD folder_cyrkon: brak folderu projektow Cyrkon: <PC-katalog>/koordynator/robocze/odbior/T7/robocze/Cyrkon - pula projektow jest pusta i skany czekaja bez wyniku; otworz plik ustawien ...\ustawienia_b1.toml i popraw klucz [sciezki] folder_cyrkon (wiersz folder_cyrkon = "...", sciezka z ukosnikami /) albo utworz / podlacz ten folder`; `SAMOKONTROLA: CZERWONA (ok 16, ostrzezenia 4, bledy 1)` | `t7_b1_2_samokontrola_bez_folderu.log` |
| 4 | `ren <ROB>\robocze\Cyrkon_x Cyrkon` | 0 | | |
| 5 | samokontrola jak w 0 | 0 | `SAMOKONTROLA: ZIELONA (ok 18, ostrzezenia 3)` | `t7_b1_3_samokontrola_po_przywroceniu.log` |
| 6 | program jak w 2 (`--zamknij-po 30`) | 0 | 33,2 s; zdarzenia w bazie: 4 (`program_start` 2, `program_stop` 2) | `t7_b1_4_program_po_przywroceniu.log`, `t7_b1_baza.txt` |

- O sumach (zasada 3: `Samokontrola.cmd` dodaje `--sumy`, tu pominiete): samokontrola wypisala mimo to
  `OK sumy: sumy SHA-256 plikow programu zgodne 130 z 130 (SUMY_PROGRAMU.sha256), plikow nadmiarowych 0` (3 z 3 przebiegow samokontroli w B1 i 1 z 1 w przebiegu z proba polaczenia).
- Potkniecie planu: krok kaze szukac `pula_brak_folderu` w `stanowisko.log`. Program komunikatow ekranu do logu nie pisze, a
  `pula_brak_folderu` ustawia tylko, gdy skany czekaja na pule (`kontroler_api.py`, `_komunikat_puli`: warunek `czeka`). Przy pustym
  folderze eksportu komunikatu nie ma wcale. Stad uzupelnienie B1b. Komunikat na ekranie potwierdza test czesci A
  (`test_aplikacja.py:410`, kod z instalacji).

## B1b - brak folderu "Cyrkon" przy czekajacym skanie (UZUPELNIENIE spoza planu; `krok_B1b.cmd` -> `robocze\proba_b1b.ps1`, blokada tor 4, 03:30:26-03:34:41, instalacja wspolna `<K>`)

| Godz. | Krok | Wynik |
|---|---|---|
| 03:30:26 | `Cyrkon` -> `Cyrkon_x`; start: `<K>\Polecenie.cmd -m stanowisko.aplikacja --ustawienia <ROB>\ustawienia_b1b.toml --zamknij-po 90` | program dziala |
| 03:30:38-40 | `<K>\Polecenie.cmd narzedzia\symulator_skanera.py --folder <ROB>\robocze\b1b\eksport --zrodla <PC-katalog>\app\dane_ref\syntetyczne_R59_P2 --ile 1 --seed 1 --dziennik <ROB>\t7_b1b_symulator.json` | kod 0; log programu 03:30:40 `nowy skan nr 1: ... sha16=c85504f17628ac3f` |
| 03:31:05 | odczyt bazy 25 s po zapisie skanu | `skany`: 0 wierszy; zdarzenia: `nowy_skan` 1, `program_start` 1 - skan czeka, wyniku nie ma |
| 03:31:59 | program konczy sie sam (`--zamknij-po 90`) | **kod 0**; log: "zamkniete, zadan niezakonczonych 1"; `program_stop {"niezakonczone": 1}`; plik `zadania_niezakonczone.json`: JEST; `skany`: 0 wierszy |
| 03:31:59 | `Cyrkon_x` -> `Cyrkon`; start: ten sam program z `--zamknij-po 150` | log 03:32:00: "start, zadan wznowionych 1, plikow znanych 1" |
| 03:32:58 | wynik | log: "skan c85504f17628ac3f przyjety jako 1 (56.3 s)"; `skany`: 1 wiersz (`plytka_nie_z_trybu`); `zadania_niezakonczone.json`: brak |
| 03:34:32 | program konczy sie sam | **kod 0**; "zamkniete, zadan niezakonczonych 0" |

Baza po probie (`t7_b1b_baza.txt`): `skany` 1; zdarzenia: `nowy_skan` 1, `skan_przyjety` 1, `podglad` 1, `program_start` 2, `program_stop` 2.
W logu i w zdarzeniach nie ma wpisu o braku folderu projektow (0 wierszy ze slowem "folder") - komunikat `pula_brak_folderu` na
programie z paczki NIE ZMIERZONY (jest tylko na ekranie); zmierzono zachowanie: skan czeka, nie ginie i wraca po przywroceniu folderu.

## B2 - zakonczenie procesu programu w polowie wieczoru (`krok_B2.cmd` -> `robocze\proba_b.ps1 -N b2 -Tryb program -Ile 4`, blokada tor 4, 03:08:16-03:20:02, instalacja `<K12>`)

Okno 1 (`robocze\b2_okno1.cmd`): `<K12>\Polecenie.cmd -m stanowisko.aplikacja --ustawienia <ROB>\ustawienia_b2.toml --zamknij-po 600`.
Okno 2 (`robocze\b2_okno2.cmd`): `<K12>\Polecenie.cmd narzedzia\symulator_skanera.py --folder <ROB>\robocze\b2\eksport --zrodla <PC-katalog>\app\dane_ref\syntetyczne_R59_P2 --ile 4 --odstep 60 --rownolegle 1 --seed 1 --dziennik <ROB>\t7_b2_symulator.json`.
Regula PID (plan): `Get-Process python | Where-Object { $_.Path -like '<K12>\wersje\*' }` - odczyty w `t7_b2_pid.txt`; przebieg: `t7_b2_przebieg.txt`.

| Godz. | Krok | Wynik |
|---|---|---|
| 03:08:17 | ODCZYT 1 przed startem okna 1 | **0 wierszy** (oczekiwane 0) |
| 03:08:17 | start okna 1 | posrednik srodowiska wersji PID 29100, StartTime 03:08:17.717 |
| 03:08:30 | ODCZYT 2 po starcie okna 1, przed oknem 2 | **1 wiersz** (PID 29100) - regula spelniona; potomkowie: interpreter 32888, silnik 18536 (sciezka Pythona bazowego) |
| 03:08:32 | start okna 2 (symulator) | 1. skan zapisany 03:08:34-36; log programu 03:08:36 `nowy skan nr 1` |
| 03:09:32 | 1. analiza | "skan c85504f17628ac3f przyjety jako 1 (56.0 s)" |
| 03:09:34-36 | 2. skan zapisany (dziennik symulatora: `zapisy[1]`, koniec 03:09:36,56) | log programu 03:09:36,90 `nowy skan nr 2: ... sha16=edb739f16b06e032` (zdarzenie `nowy_skan`, `"zastany": false`) |
| 03:09:39 | odczyt przed zakonczeniem | `skany`: 1 wiersz; plikow STL w eksporcie 2; `zadania_niezakonczone.json`: brak |
| **03:09:39,54** | **`Stop-Process -Id 29100 -Force`** (3,0 s po koncu zapisu 2. skanu; analiza 2. skanu trwala 2,6 s) | okno 1: kod -1 |
| 03:09:41 | po 1,5 s | **nie zyje 3 z 3** procesow programu (29100, 32888, 18536) |
| 03:09:41 | odczyt po zakonczeniu | `skany`: 1 wiersz; `zadania_niezakonczone.json`: brak (program nie zdazyl niczego zapisac) |
| 03:09:44 | okno 1 PONOWNIE (to samo polecenie); symulator zostawiony | log 03:09:45: "start, zadan wznowionych 0, plikow znanych 1"; **`nowy skan nr 1: ... sha16=edb739f16b06e032 ... (plik zastany - nadrabianie)`**; zdarzenie `nowy_skan` id 7 z **`"zastany": true`** |
| 03:10:10 | 2. skan | "przyjety jako 2 (23.5 s)" |
| 03:10:34-38 / 03:11:03 | 3. skan zapisany / wynik | "przyjety jako 3 (25.0 s)" |
| 03:11:34-38 / 03:12:04 | 4. skan zapisany / wynik | "przyjety jako 4 (26.2 s)"; symulator: kod 0, "zapisano plikow: 4 (dobrych 4, zlych 0)" |
| 03:12:17 | odczyt | **`skany`: 4 z 4** (`plytka_nie_z_trybu` 4) - 3 min 45 s po starcie symulatora (plan: "po ok. 6 min") |
| 03:19:46 | okno 1 konczy sie samo (`--zamknij-po 600`) | **kod 0**; log: "zamkniete, zadan niezakonczonych 0" |
| 03:20:02 | ODCZYT koncowy | 0 wierszy; `zadania_niezakonczone.json`: brak |

Baza po probie (`t7_b2_baza.txt`): `skany` 4 (id 1-4, 4 rozne `sha16`); zdarzenia: `nowy_skan` 5 (2. skan dwa razy: `zastany` false przed
zakonczeniem programu i `zastany` true po starcie), `skan_przyjety` 4, `podglad` 4, `program_start` 2, `program_stop` 1 (pierwszy
egzemplarz zakonczony `Stop-Process` - bez wpisu). Slowo "wznowiono" w logu: 0 razy (komunikat tylko na ekranie - potwierdza go test
czesci A `test_e_awaria_bez_zamkniecia_nadrabianie_folderu`, PASSED). `Traceback` w logu: 0.

## B3 - zakonczenie procesu silnika w trakcie analizy (`krok_B3.cmd` -> `robocze\proba_b.ps1 -N b3 -Tryb silnik -Ile 3`, blokada tor 4, 03:20:03-03:30:25, instalacja `<K12>`) - PIERWSZE WYKONANIE

Okna jak w B2 (`ustawienia_b3.toml`, `--ile 3`). Odczyty PID: `t7_b3_pid.txt`; przebieg: `t7_b3_przebieg.txt`; baza: `t7_b3_baza.txt`.

| Godz. | Krok | Wynik |
|---|---|---|
| 03:20:04 | ODCZYT 1 przed startem okna 1 | **0 wierszy** |
| 03:20:05 | start okna 1 | posrednik PID 35620, StartTime 03:20:05.050 |
| 03:20:17 | ODCZYT 2 | **1 wiersz** (PID 35620) |
| 03:20:18 | ODCZYT 3 - regula proby 3: procesy Pythona bazowego ze `StartTime` w ciagu 5 s po posredniku | **dokladnie 2**: 35156 (03:20:05.104, interpreter programu) i 33092 (03:20:06.380, mlodszy = silnik); kontrola lancuchem rodzic-potomek: 35620 -> 35156 -> 33092 (zgodne). Na PC bylo wtedy 6 procesow `python` |
| 03:20:19 | start okna 2 (symulator, 3 skany co 60 s) | log 03:20:21 `nowy skan nr 1` |
| 03:21:16 | 1. analiza | "przyjety jako 1 (54.4 s)" |
| 03:21:22 | 2. skan zgloszony (`nowy skan nr 2: ... sha16=edb739f16b06e032`) | analiza 2. skanu rusza |
| 03:21:28 | odczyt tuz przed zakonczeniem; ODCZYT 4 (regula ponownie) | `skany`: 1 wiersz, wynikow w logu 1 (= trwa analiza 2. skanu); regula: 2 wiersze, te same PID-y |
| **03:21:29,62** | **`Stop-Process -Id 33092 -Force`** (7,4 s po zgloszeniu 2. skanu; 5 s po stwierdzeniu "2. skan zapisany") | |
| 03:21:29,73 | log programu | **`WARNING ... stanowisko: analiza skanu edb739f16b06e032 nie dala wyniku (proces)`** |
| 03:21:29 | baza | zdarzenie `blad_analizy` (zrodlo `silnik`, skan 2): `{"opis": "proces: proces silnika zakonczyl sie w trakcie analizy (kod wyjscia 4294967295); analiza przerwana", "typ": null}`; `blad_analizy_rodzaj`: `{"rodzaj": "proces"}`; skan 2 status **`blad`** |
| 03:21:31 | po 2 s | silnik nie zyje; posrednik i interpreter ZYJA (program pracuje) |
| 03:21:39 | po 10 s | nowy potomek interpretera (nowy proces silnika): PID 33448, start 03:21:29 |
| 03:22:24 | 3. skan zgloszony | `nowy skan nr 3: ... sha16=0b1286719e932bbd` |
| **03:22:58** | **3. skan przyjety** | "skan 0b1286719e932bbd przyjety jako 3 (34.0 s)"; `skany`: 3 wiersze (`plytka_nie_z_trybu` 2, `blad` 1) |
| 03:30:07 | okno 1 konczy sie samo (`--zamknij-po 600`) | **kod 0**; "zamkniete, zadan niezakonczonych 0"; symulator kod 0 |
| 03:30:25 | ODCZYT koncowy | 0 wierszy |
| 03:30:43-03:31:05 | DODATKOWO (spoza planu): start kontrolny `<K12>\Polecenie.cmd -m stanowisko.aplikacja --ustawienia <ROB>\ustawienia_b3.toml --zamknij-po 20` | kod 0; log: **"start, zadan wznowionych 0, plikow znanych 3"**; `skany` nadal 3 (te same statusy); skan z bledem nie jest analizowany ponownie (technik ma go zeskanowac ponownie - tresc komunikatu) |

Tekst komunikatu dla technika przy tym bledzie (`statusy.py`, rodzaj `blad_analizy`, powod `"proces"`): "Analiza skanu nie powiodla sie" /
"Program nie przeanalizowal tego skanu (analiza zostala przerwana). Zeskanuj plytke ponownie." - na ekranie; w probie widac jego
zrodlo (zdarzenie `blad_analizy_rodzaj` = "proces" - z niego kontroler bierze powod) i opis "analiza przerwana" w zdarzeniu `blad_analizy`.

## Dodatkowo: samokontrola z proba polaczenia z ramkami (przypadki 4 i 5, program z paczki, 03:20:26)

`<K>\Polecenie.cmd -m stanowisko.samokontrola --ustawienia <ROB>\ustawienia_b1.toml` (bez `--bez-sieci`): kod 0, ZIELONA (ok 18,
ostrzezenia 3): `OSTRZEZENIE ramka_wieczorna: ramka wieczorna nieobecna: brak polaczenia z ramka-w.local:8765 (gaierror); wlacz ramke,
sprawdz Wi-Fi i [ramki] wieczorna_host w pliku ustawien, bez ramek program dziala - rozkladanie wedlug podpisow na ekranie`; to samo dla
`ramka_poranna`; `OSTRZEZENIE excel: Excel nie jest uruchomiony ...; bez Excela program dziala - zlecenia odhacza sie wtedy recznie`
(`t7_45_samokontrola_z_proba_polaczenia.log`). We wszystkich probach B program pracowal przy nieosiagalnych ramkach (w logu przy
zamknieciu: "kontroler: zgaszenie ramki W przy zamknieciu nie doszlo ...") - analizy wykonane, kody wyjscia 0.

## Potkniecia i zmiany wobec planu (wszystkie)

1. B1: w logu nie ma `pula_brak_folderu` (0 wierszy) - opis wyzej; dodano probe B1b (spoza planu).
2. B2 / B3: plan kaze czekac na "2 pozycje w `zapisy`" dziennika symulatora - plik `--dziennik` powstaje dopiero PO zakonczeniu
   symulatora (zapis na koncu `main`). Chwile "po zapisie 2. skanu" ustalono po folderze eksportu: 2. plik `*.stl` o rozmiarze stalym
   przez 2,5 s (5 odczytow co 0,5 s). Dziennik po zakonczeniu ma 4 (B2) i 3 (B3) pozycje `zapisy`.
3. B2 / B3 / B1b: zamiast dwoch okien `cmd` obslugiwanych recznie - sterownik `robocze\proba_b.ps1` / `proba_b1b.ps1` (PowerShell 7,
   pod blokada tor 4), ktory uruchamia oba "okna" jako ukryte procesy `cmd /c` z poleceniami planu, robi odczyty PID i konczy proces
   poleceniem planu (`Stop-Process -Id <pid> -Force`). PID wylacznie z reguly planu (0 wierszy przed, 1 po; w B3 dokladnie 2 procesy
   Pythona bazowego w 5 s po posredniku) - w obu probach regula dala wynik jednoznaczny; lancuch rodzic-potomek tylko jako kontrola.
4. Blad sterownika w B2: 1 wiersz informacyjny ("ODCZYT 3a", tabela potomkow) nie zapisal sie w `t7_b2_pid.txt` (blad PowerShell
   "op_Addition" przy laczeniu list - `robocze\b2_sterownik.log`); bez wplywu na probe (potomkowie sa w "ODCZYT 4"). Poprawione przed B3.
5. `<K>\Stanowisko.cmd --zamknij-po <s>` z planu wykonane jako `Polecenie.cmd -m stanowisko.aplikacja --ustawienia <plik> --zamknij-po <s>`
   (zasada 3); zamiast jednego `<ROB>\ustawienia.toml` - osobny plik na probe (`ustawienia_b1.toml`, `_b1b`, `_b2`, `_b3`), dane prob w
   `<ROB>\robocze\<proba>\` (zasada 3 zlecenia wspolnego: bazy i STL poza katalogiem dowodow).
6. B1 na instalacji wspolnej `<K>` (zasada 3), B2 i B3 na `<K12>` (zasada 5a, decyzja koordynatora w zleceniu), B1b na `<K>`.
7. Skany ze zrodla planu dostaja status `plytka_nie_z_trybu` (plytki poranne w trybie "Wieczor") - opis wyzej.
8. Kolejnosc: B1 wykonano w czasie uzupelnienia T12 czesc B (krok lekki), czesc A po nim; T13 w czasie proby B2.
9. Przed B3 i B1b sprawdzono w `ciezkie.log`, ze nie trwa krok T4 / T2 (pomiary czasowe): nie trwal (`robocze\kolejka.txt`).

Po probach: `Get-Process python` - 0 procesow ze sciezka `<K12>\wersje\*` i 0 wlasnych; folder `robocze\Cyrkon` przywrocony;
instalacja `<K12>` i jej dane bez zmian (suma `ustawienia.toml` 1274f09d...6da4d022, zdarzenia 8, skany 0, wersja biezaca 0.3.1).
