WERDYKT T12: ZAL z odstepstwem O2 + NOWE (czesc A na wydaniu: aktualizacja 0.3.3 -> 0.3.4-t12 i powrot do 0.3.3 po 1 poleceniu, kody 0 i 0; ustawienia 5 z 5 sum identyczne; baza: skany 0 = 0, plik bazy nietkniety, kopia przy aktualizacji = baza; czesc B: baza zmigrowana z kopia - kody 11 z 11 w PROBIE 2, powrot po migracji = 2 polecenia (kod 8, potem /przywroc-kopie) - do decyzji wlasciciela; NOWE: proba 1 czesci B niewazna - instalator odmowil paczki probnej kodem 6, bo katalog wykonawcy mial 63 znaki, za duzo dla nazwy wersji 0.3.9-migracja - do oceny koordynatora; dodatek NOWY: aktualizacja ze starego wydania 0.3.1 -> 0.3.3 kod 0, samokontrola zielona, uklady plytek 10 z 10, 6 skrotow z Dzien_skanera.cmd, start kod 0, powrot do 0.3.1 kod 0 - kody 9 z 9)

# T12 - Aktualizacja na WYDANIU (N = 0.3.3, N+1 = 0.3.4-t12) - wynik 21.11.2026

Pomiar, nie naprawa. Niczego w programie, testach, planie i narzedziach nie zmieniono; zadnych commitow.

- Paczki: `<PC-katalog>\wydania\Stanowisko_0.3.3.zip` (SHA-256 b6049229848afb124771944a3a3037664a0ec68aaeaa18a09da76f05103b1377) i
  `Stanowisko_0.3.4-t12.zip` (42d3e33c3d15c3c0c004b8d924095d128b5563283f235d7b97affaa5ffc70f6a) - obie sumy policzone `certutil`
  17:48:14, zgodne z plikami `.sha256` i ze zleceniem (2 z 2; `t12_sha256_zip.txt`). Instalator: sumy paczki "zgodne 227 z 227" (obie
  paczki; plan podaje 210), commit 0fedbf6e4f97; program 148 plikow (plan: 131), pakiety 73 z 73.
- Instalacja WLASNA T12: `<K>` = `<PC-katalog>\t0\odbior2_t12\Stanowisko`; `<P1>` = `<PC-katalog>\t0\odbior2_t12\paczka_0.3.3`,
  `<P2>` = `<PC-katalog>\t0\odbior2_t12\paczka_0.3.4-t12` (obie rozpakowane przez te sesje: 228 plikow kazda = 227 + SHA256SUMS);
  foldery wejsciowe `<PC-katalog>\t0\odbior2_t12\dane\{eksport,Cyrkon,Prywatne,millbox}` (Cyrkon = kopia `<PC-katalog>\app\Prace_test`,
  17 STL). `<ROB>` = `<PC-katalog>\koordynator\robocze\odbior2\final\T12`; `<REPO>` = `<PC-katalog>\t0\repo2` (0fedbf6, tylko odczyt),
  `<ODB>` = `<REPO>\Ramki\etap3\odbior_koncowy`; `PY` = `<PC>\AppData\Local\Programs\Python\Python312\python.exe`.
- Kazdy krok ciezki przez `powershell -NoProfile -ExecutionPolicy Bypass -File <PC-katalog>\koordynator\narz\ciezki.ps1 -Tor 2 -Kto f2
  -Polecenie <ROB>\krok_<A|Z|B>.cmd` (po T2; kolejka `<ROB>\kolejka.ps1` jako proces odlaczony - 3 wywolania po kolei, przed kazdym
  kontrola wolnego miejsca, wpisy w `<ROB>\kolejka.txt`). Pliki `.cmd`: CRLF, `call` przed kazdym skryptem, wejscie `< NUL`,
  `set QT_QPA_PLATFORM=offscreen`. Kody: `kody.txt`; godziny: `czasy.txt`; stany instalacji i bazy po kazdym kroku (`<ROB>\stan.cmd`):
  `t12_A_stany.txt`, `t12_Z_stany.txt`, `t12_B_stany.txt`.
- Wolne na C: 36 GB na starcie sesji (17:37), 31,9 GB przed krokiem A (17:42), 27,7 GB przed krokiem Z (17:53).

## Czesc A - 0.3.3 -> 0.3.4-t12 -> powrot do 0.3.3 (krok_A.cmd: 17:48:14 - 17:53:23, kod 0)

### Przygotowanie (T0 kroki 2-5 i 7 w katalogu odbior2_t12)

| Krok | Godz. | Polecenie | Kod | Czas | Wynik | Log |
|---|---|---|---|---|---|---|
| T0-2 | 17:48:14 | `certutil -hashfile <PC-katalog>\wydania\Stanowisko_0.3.3.zip SHA256` (i `_0.3.4-t12.zip`) | 0, 0 | - | 2 z 2 zgodne z `.sha256` | `t12_sha256_zip.txt` |
| T0-2 | 17:48:15 | `C:\Windows\System32\tar.exe -xf <ZIP> -C <P1>` (i `<P2>`) - ZMIANA wobec planu (`Expand-Archive`) | 0, 0 | 1,3 s i 1,4 s | 228 plikow w kazdym katalogu | `t12_P2_tar.log` |
| T0-3 | 17:48:18 | `<P1>\zainstaluj.cmd /katalog <K> /python %PY% /bez-sieci /bez-pauzy` | 10 | 105,7 s | sumy "zgodne 227 z 227; wersja 0.3.3, commit 0fedbf6e4f97", "program: skopiowano 148 plikow", pakiety "73 z 73", samokontrola CZERWONA (ok 11, ostrzezenia 8, bledy 2: folder_skanera, folder_cyrkon), `INSTALACJA: WSTRZYMANA ... (kod 10)` | `t12_P3_zainstaluj_N_1.log` |
| T0-4 | 17:50:04 | edycja `<K>\ustawienia.toml` (`<ROB>\edytuj.ps1`, UTF-8 bez BOM): 4 foldery `[sciezki]` -> `<PC-katalog>/t0/odbior2_t12/dane/...`, `operatorzy = ["Technik A"]` | 0 | - | zmienionych wierszy 5 z 5 | `t12_P4_edycja.log` |
| T0-5 | 17:50:04 | `<P1>\zainstaluj.cmd /katalog <K> /python %PY% /bez-sieci /bez-pauzy` | 0 | 4,9 s | samokontrola ZIELONA (ok 17, ostrzezenia 4); "uklady plytek z [plytki]: poprawne 10 z 10"; `INSTALACJA: GOTOWA - wersja biezaca 0.3.3 (poprzednia: brak)` | `t12_P5_zainstaluj_N_2.log` |
| T0-7 | 17:50:09 | `<K>\Stanowisko.cmd --atrapa --zamknij-po 5` | 0 | 7,4 s | na konsoli 3 wiersze Qt o czcionkach (311 bajtow) | `t12_P7a_start_atrapa.log` |
| T0-7 | 17:50:16 | `<K>\Stanowisko.cmd --zamknij-po 20` | 0 | 23,6 s | start prawdziwego kontrolera; baza zalozona | `t12_P7b_start.log` |

### Kroki T12 czesc A

| Krok | Godz. | Polecenie | Kod | Czas | Wynik | Log |
|---|---|---|---|---|---|---|
| 1 | 17:50:40 | `certutil -hashfile <K>\ustawienia.toml SHA256` | 0 | - | afc8042112adad1506538fdfc712e645ad666ddda20bd869101f23686f96123c | `t12_ustawienia_przed.txt` |
| 1 | 17:50:40 | `<K>\Wersje.cmd /bez-pauzy` | 0 | - | 1 wersja: 0.3.3 BIEZACA, commit 0fedbf6e4f97, schemat bazy 1 | `t12_A1_wersje_przed.log` |
| 1 | 17:50:40 | `PY -I <ODB>\narzedzia\sql_odczyt.py --baza <K>\dane\stanowisko.sqlite "SELECT count(*) FROM skany"` (oraz `zdarzenia`, `user_version`); `certutil` bazy; rozmiar i skrot bez naglowka | 0 | - | skany 0, zdarzenia 2, user_version 1; SHA-256 bazy d10654b3...7607f408; 86016 B, skrot od 100. bajtu 38f4322a...30cfbf62; `dane\kopie` nie istnieje (0 plikow) | `t12_A_stany.txt` |
| 2 | 17:50:41 | **`<P2>\zainstaluj.cmd /katalog <K> /python %PY% /bez-sieci /bez-pauzy`** (aktualizacja, 1 polecenie) | **0** | **100,5 s** | sumy 227 z 227 (wersja 0.3.4-t12, commit 0fedbf6e4f97); "istniejacy ustawienia.toml zostaje bez zmian (SHA-256 afc8042112adad15...)"; "baza: schemat 1; program 0.3.4-t12 obsluguje schemat 1"; pakiety 73 z 73; "kopia bazy: kopie/stanowisko_przed_0.3.4-t12_20261121_175214_v1.sqlite - sprawdzona (quick_check ok, schemat bazy 1; program 0.3.4-t12: 1)"; samokontrola ZIELONA (ok 18, ostrzezenia 3); `INSTALACJA: GOTOWA - wersja biezaca 0.3.4-t12 (poprzednia: 0.3.3)` | `t12_zainstaluj_N1.log` |
| 2 | 17:52:21 | stan po aktualizacji, przed startem 0.3.4-t12 | - | - | `wersja_biezaca.txt` = 0.3.4-t12, `wersja_poprzednia.txt` = 0.3.3; baza bez zmian (SHA-256 d10654b3...7607f408 = krok 1); w `dane\kopie` 1 plik: 86016 B i skrot bez naglowka 38f4322a...30cfbf62 = baza z kroku 1 (rowne); SHA-256 calego pliku kopii 36bf2f0b...71bb8df0 (inne niz bazy - naglowek, O2); kopia: user_version 1, zdarzenia 2, skany 0 (jak baza) | `t12_A_stany.txt` |
| 3 | 17:52:23 | `<K>\Samokontrola.cmd --bez-sieci` | 0 | 3,0 s | `SAMOKONTROLA: ZIELONA (ok 18, ostrzezenia 3)`; uklady plytek 10 z 10; sumy programu 147 z 147 | `t12_A3_samokontrola_N1.log` |
| 3 | 17:52:26 | `<K>\Stanowisko.cmd --zamknij-po 20` | 0 | 23,7 s | program 0.3.4-t12 dziala | `t12_A3_start_N1.log` |
| 3 | 17:52:49 | `certutil -hashfile <K>\ustawienia.toml SHA256`; `<K>\Wersje.cmd /bez-pauzy`; liczby bazy | 0, 0 | - | suma afc80421...6f96123c = krok 1; 0.3.3 poprzednia, 0.3.4-t12 BIEZACA; skany 0, zdarzenia 4 (+2 = start programu), user_version 1 | `t12_ustawienia_po_N1.txt`, `t12_A3_wersje_po_N1.log`, `t12_A_stany.txt` |
| 4 | 17:52:51 | **`<K>\Wroc_do_poprzedniej.cmd /tak /bez-pauzy`** (powrot, 1 polecenie - polecenie planu doslownie) | **0** | **3,5 s** | "Baza: schemat 1; wersja 0.3.3 obsluguje schemat do 1 - schemat zgodny - baza zostaje bez zmian"; samokontrola ZIELONA (ok 18, ostrzezenia 3); `POWROT: GOTOWY - wersja biezaca 0.3.3 (poprzednia: 0.3.4-t12)`; `wersja_biezaca.txt` = 0.3.3; plik bazy bez zmian (SHA-256 5cf06775...d8cecfc2 przed i po powrocie) | `t12_wroc.log`, `t12_A_stany.txt` |
| 5 | 17:52:54 | `<K>\Samokontrola.cmd --bez-sieci` | 0 | - | `SAMOKONTROLA: ZIELONA (ok 18, ostrzezenia 3)`; uklady plytek 10 z 10; sumy 147 z 147 | `t12_A5_samokontrola_N.log` |
| 5 | 17:52:58 | `<K>\Stanowisko.cmd --zamknij-po 20` | 0 | 23,2 s | program 0.3.3 dziala po powrocie | `t12_A5_start_N.log` |
| 5 | 17:53:22 | `certutil` ustawien; `<K>\Wersje.cmd /bez-pauzy`; liczby bazy; `find /c "Traceback" <K>\dane\logi\stanowisko.log` | 0, 0 | - | suma afc80421...6f96123c = krok 1; 0.3.3 BIEZACA, 0.3.4-t12 poprzednia; skany 0 (= krok 1), zdarzenia 6, user_version 1; `dane\kopie` 1 plik; `Traceback` 0 wierszy | `t12_ustawienia_po_powrocie.txt`, `t12_A5_wersje_po_powrocie.log`, `t12_A_stany.txt` |

### Liczby czesci A (wobec nocy: paczki 0.3.1 / 0.3.2)

- Kody polecen programu: przygotowanie 10, 0, 0, 0; czesc A: 0 (aktualizacja), 0, 0 (krok 3), 0 (powrot), 0, 0 (krok 5) - 10 z 10 zgodnych
  z oczekiwanymi (noc: 12 z 12, w tym 2 dodatkowe proby odpowiedzi N / brak odpowiedzi z kodem 11 - tu NIE powtarzane).
- "Jedno polecenie": aktualizacja 1 wywolanie, kod 0, 100,5 s (noc 60,4 s); powrot 1 wywolanie `/tak`, kod 0, 3,5 s (noc 2,6 - 3,3 s).
- Ustawienia zachowane: SHA-256 `ustawienia.toml` przed / po aktualizacji przed startem / po starcie 0.3.4-t12 / po powrocie / stan koncowy
  = 5 z 5 identyczne (afc8042112adad1506538fdfc712e645ad666ddda20bd869101f23686f96123c); plan wymaga 3 z 3 (noc: 4 z 4).
- Baza (czesc A): skany 0 -> 0 -> 0 -> 0 -> 0; zdarzenia 2 -> 2 -> 4 -> 4 -> 6 (po 2 na start programu, nic nie ubylo); user_version 1 caly
  czas; aktualizacja i powrot nie zmienily pliku bazy (SHA-256 rowne przed / po w obu krokach). Kopia przy aktualizacji: 1 plik
  `dane\kopie\stanowisko_przed_0.3.4-t12_20261121_175214_v1.sqlite`, 86016 B i skrot bez naglowka = baza sprzed aktualizacji (noc: tak samo).
- Samokontrola: ZIELONA 3 z 3 (po aktualizacji, po powrocie + w instalatorze / powrocie), ok 18, ostrzezenia 3 (2 x ramka pominieta
  `--bez-sieci`, Excel) - jak w nocy; NOWE wobec nocy: "uklady plytek: poprawne 10 z 10" (noc 8 z 8), sumy programu 147 z 147 (noc 130 z 130).
- Skroty w `<K>`: 6 plikow `.cmd` (Dzien_skanera.cmd, Polecenie.cmd, Samokontrola.cmd, Stanowisko.cmd, Wersje.cmd, Wroc_do_poprzedniej.cmd);
  noc: 5 (bez Dzien_skanera.cmd).
- Start programu: kod 0 - 4 z 4 (atrapa, 0.3.3, 0.3.4-t12, 0.3.3 po powrocie); `Traceback` w logu programu: 0. Na konsoli kazdego startu
  3 wiersze Qt ("QFontDatabase: Cannot find font directory ...", "Note that Qt no longer ships fonts ...", "This plugin does not support
  propagateSizeHints()" - 311-315 bajtow); w nocy logi startow mialy 0 bajtow - obserwacja, nie blad (platforma offscreen).

Co jeszcze liczylo na PC (ciezkie.log): tor 1 - T1 `krok_4.cmd` (od 17:46:00), tor 3 - T1 `krok_5.cmd` (od 17:45:58), tor 4 - T11
`krok_t11.cmd` (od 17:48:30). Czasy instalacji (105,7 s / 100,5 s wobec 51,2 s / 60,4 s w nocy) sa z PC pod tym obciazeniem.

## NOWE dla tego wydania: aktualizacja ze STAREGO wydania 0.3.1 -> 0.3.3 -> powrot do 0.3.1 (krok_Z.cmd: 17:53:24 - 17:57:22, kod 0)

Osobna instalacja: `<KZ>` = `<PC-katalog>\t0\odbior2_t12\z031\Stanowisko`; `<PZ>` = `<PC-katalog>\t0\odbior2_t12\z031\paczka_0.3.1`
(rozpakowana `tar.exe` z `<PC-katalog>\wydania\Stanowisko_0.3.1.zip`, SHA-256 f5affa81...3e24eec8 = plik `.sha256`, 1 z 1); foldery
wejsciowe `<PC-katalog>\t0\odbior2_t12\z031\dane\{eksport,Cyrkon,Prywatne,millbox}` (Cyrkon = kopia `Prace_test`, 17 STL); paczka 0.3.3 =
`<P1>` z czesci A (tylko czytana). Ustawienia zalozyl instalator 0.3.1 ze SWOJEGO wzoru: 120 wierszy, w `[plytki]` 8 ukladow (wzor 0.3.3:
10 ukladow); zmieniono w nich tylko 4 foldery i `operatorzy` (5 wierszy z 5), jak w czesci A.

| Krok | Godz. | Polecenie | Kod | Czas | Wynik | Log |
|---|---|---|---|---|---|---|
| Z1 | 17:53:25 | `<PZ>\zainstaluj.cmd /katalog <KZ> /python %PY% /bez-sieci /bez-pauzy` | 10 | 81,5 s | sumy "zgodne 210 z 210; wersja 0.3.1, commit 571e186cb817", program 131 plikow, pakiety 73 z 73, samokontrola CZERWONA (bledy 2: foldery), `INSTALACJA: WSTRZYMANA (kod 10)` | `t12_Z1_zainstaluj_031_1.log` |
| Z1 | 17:54:47 | edycja `<KZ>\ustawienia.toml` (`edytuj.ps1`) | 0 | - | zmienionych wierszy 5 z 5 | `t12_Z1_edycja.log` |
| Z2 | 17:54:47 | `<PZ>\zainstaluj.cmd /katalog <KZ> /python %PY% /bez-sieci /bez-pauzy` | 0 | 4,6 s | samokontrola ZIELONA (ok 17, ostrzezenia 4), "uklady plytek z [plytki]: poprawne 8 z 8", `INSTALACJA: GOTOWA - wersja biezaca 0.3.1 (poprzednia: brak)` | `t12_Z2_zainstaluj_031_2.log` |
| Z2 | 17:54:52 | `<KZ>\Stanowisko.cmd --zamknij-po 20` (baza zalozona przez 0.3.1) | 0 | 23,0 s | stan: skany 0, zdarzenia 2, user_version 1; SHA-256 ustawien 6fb7a03097fd3eebf4513115877626a2fd5216f6dedd8902b6cf76bff711740b; w `<KZ>` 5 skrotow `.cmd`; `Wersje.cmd`: 0.3.1 BIEZACA | `t12_Z2_start_031.log`, `t12_Z2_wersje_przed.log`, `t12_Z_stany.txt` |
| Z3 | 17:55:16 | **`<P1>\zainstaluj.cmd /katalog <KZ> /python %PY% /bez-sieci /bez-pauzy`** (aktualizacja 0.3.1 -> 0.3.3, 1 polecenie) | **0** | **70,6 s** | sumy 227 z 227 (0.3.3, commit 0fedbf6e4f97); "istniejacy ustawienia.toml zostaje bez zmian (SHA-256 6fb7a03097fd3eeb...)"; "baza: schemat 1; program 0.3.3 obsluguje schemat 1"; program 148 plikow, pakiety 73 z 73; "kopia bazy: kopie/stanowisko_przed_0.3.3_20261121_175622_v1.sqlite - sprawdzona (quick_check ok ...)"; samokontrola ZIELONA (ok 18, ostrzezenia 3); `INSTALACJA: GOTOWA - wersja biezaca 0.3.3 (poprzednia: 0.3.1)` | `t12_Z3_zainstaluj_033.log` |
| Z3 | 17:56:26 | stan po aktualizacji | - | - | ustawienia bez zmian (suma 6fb7a030...f711740b); baza bez zmian (SHA-256 90cd5a97...a02e9079 przed i po); kopia: 1 plik, 86016 B, skrot bez naglowka dfa0dc2c...cb8b7339 = baza sprzed aktualizacji, user_version 1, zdarzenia 2; w `<KZ>` 6 skrotow `.cmd` - doszedl `Dzien_skanera.cmd`; doszly `wersja_poprzednia.txt` i `wersje\0.3.3` | `t12_Z_stany.txt` |
| Z4 | 17:56:27 | **`<KZ>\Samokontrola.cmd --bez-sieci`** (0.3.3 na ustawieniach ze starym wzorem) | **0** | 2,0 s | **`SAMOKONTROLA: ZIELONA (ok 18, ostrzezenia 3)`**; "OK ustawienia: plik ustawien wczytany i poprawny ... - 2 klucze z wartoscia domyslna ([plytki] okragla_ramkowa_wieczorna, [plytki] okragla_ramkowa_poranna)"; **"OK modele: uklady plytek z [plytki]: poprawne 10 z 10"**; sumy programu 147 z 147; ostrzezenia: 2 x ramka pominieta (`--bez-sieci`), Excel | `t12_Z4_samokontrola_033.log` |
| Z5 | 17:56:29 | **`<KZ>\Stanowisko.cmd --zamknij-po 20`** (start 0.3.3 i zamkniecie) | **0** | 22,8 s | program 0.3.3 dziala na starych ustawieniach i bazie zalozonej przez 0.3.1; zdarzenia 2 -> 4, skany 0, user_version 1; `Wersje.cmd`: 0.3.1 poprzednia, 0.3.3 BIEZACA | `t12_Z5_start_033.log`, `t12_Z5_wersje_po_033.log` |
| Z6 | 17:56:53 | **`<KZ>\Wroc_do_poprzedniej.cmd /tak /bez-pauzy`** (powrot do 0.3.1, 1 polecenie) | **0** | 2,3 s | "Baza: schemat 1; wersja 0.3.1 obsluguje schemat do 1 - schemat zgodny - baza zostaje bez zmian"; samokontrola 0.3.1 ZIELONA (ok 18, ostrzezenia 3); `POWROT: GOTOWY - wersja biezaca 0.3.1 (poprzednia: 0.3.3)`; plik bazy bez zmian (SHA-256 051e766a...77d5e4c2 przed i po) | `t12_Z6_wroc.log` |
| Z7 | 17:56:55 | `<KZ>\Samokontrola.cmd --bez-sieci`; `<KZ>\Stanowisko.cmd --zamknij-po 20`; `<KZ>\Wersje.cmd /bez-pauzy` (0.3.1 po powrocie) | 0, 0, 0 | - | ZIELONA (ok 18, ostrzezenia 3), "0 kluczy z wartoscia domyslna", uklady plytek 8 z 8, sumy 130 z 130; program 0.3.1 dziala (zdarzenia 4 -> 6); 0.3.1 BIEZACA, 0.3.3 poprzednia; `Traceback` w logu programu: 0 | `t12_Z7_samokontrola_031.log`, `t12_Z7_start_031.log`, `t12_Z7_wersje_po_powrocie.log` |

Liczby dodatku:

- Kody 9 polecen programu: 10, 0, 0 (instalacja 0.3.1 i start), 0 (aktualizacja), 0 (samokontrola), 0 (start 0.3.3), 0 (powrot), 0, 0
  (samokontrola i start 0.3.1) - 9 z 9 zgodnych z oczekiwanymi.
- Oczekiwania zlecenia: samokontrola zielona - TAK; "uklady plytek: poprawne 10 z 10" - TAK (10 z 10 przy 8 ukladach w pliku ustawien:
  2 brakujace klucze `[plytki]` dostaja wartosc domyslna, samokontrola wypisuje je z nazwy); 6 skrotow w tym `Dzien_skanera.cmd` - TAK
  (Dzien_skanera.cmd, Polecenie.cmd, Samokontrola.cmd, Stanowisko.cmd, Wersje.cmd, Wroc_do_poprzedniej.cmd); start programu i zamkniecie
  kod 0 - TAK; powrot do 0.3.1 kod 0 - TAK.
- Ustawienia: SHA-256 `ustawienia.toml` w 5 stanach (przed / po aktualizacji / po starcie 0.3.3 / po powrocie / koniec) = 5 z 5 identyczne
  (6fb7a03097fd3eebf4513115877626a2fd5216f6dedd8902b6cf76bff711740b) - aktualizacja NIE dopisuje nowych ukladow do pliku.
- Baza: skany 0 w 5 z 5 stanow; zdarzenia 2 -> 2 -> 4 -> 4 -> 6; user_version 1; aktualizacja i powrot nie zmienily pliku bazy.
- CO ZOSTAJE w `<KZ>` po powrocie do 0.3.1 (nic nie jest kasowane): katalog `wersje\0.3.3` (cala wersja; `wersja_poprzednia.txt` = 0.3.3 -
  ponowne `Wroc_do_poprzedniej.cmd` wraca do 0.3.3), skrot `Dzien_skanera.cmd` (6 skrotow zamiast 5 sprzed aktualizacji; plik sam pisze
  w komentarzu, ze dziala takze z wersja 0.3.1 "po powrocie do niej" i ze opcja `--zamknij-po` nie dziala w 0.3.1; modul
  `stanowisko\dzien_skanera.py` jest w `wersje\0.3.1\program` - skrotu po powrocie NIE uruchamialem: poza zleceniem, NIE ZMIERZONO),
  kopia bazy `dane\kopie\stanowisko_przed_0.3.3_20261121_175622_v1.sqlite` (1 plik), wpisy w `dziennik_instalacji.txt`; `ustawienia.toml`
  bez zmian (8 ukladow).
- Czasy: instalacja 0.3.1 81,5 s, aktualizacja do 0.3.3 70,6 s, powrot 2,3 s (obok: T1 na torach 1 i 3, T11 na torze 4).

## Czesc B - "baza zmigrowana z kopia" (O2): paczka probna 0.3.9-migracja (schemat 1 -> 2), N = 0.3.3

DWIE proby - obie zapisane. Paczka probna zbudowana raz (krok 1), uzyta w obu probach.

### Krok 1 (17:57:23 - 17:57:33): budowa i rozpakowanie paczki probnej - kody 0, 0

- `PY -I <ODB>\narzedzia\t12_paczka_migracja.py --repo <PC-katalog>\t0\repo2 --roboczy <ROB>\robocze --wersja 0.3.9-migracja --wyjscie <ROB>\robocze\paczki --kola <PC-katalog>\wydania\kola`
  - kod 0, 9,5 s (`t12_B_paczka.txt`): "commit zrodlowy: 0fedbf6e4f97... ; plikow w drzewo_M: 291", "schemat bazy w kopii: 1 -> 2
  (MIGRACJE[2] = CREATE TABLE proba_migracji_odbior ...)", ZIP 447 318 753 B, 227 plikow + SHA256SUMS (program 148, kola 73, kola
  testowe 3), SHA-256 9472fbd1523426af38dd3395dc3bcbbd351f151ab9863775a8c4fdd68fd8f6dd, "repo zrodlowe bez zmian (git status --short:
  0 wierszy przed i po)". (Plan / noc: 444 935 009 B, 210 plikow.)
- `C:\Windows\System32\tar.exe -xf <ROB>\robocze\paczki\Stanowisko_0.3.9-migracja.zip -C <ROB>\robocze\paczka_M` - kod 0, 0,9 s, 228 plikow
  (ZMIANA wobec planu: `Expand-Archive`).

### Proba 1 (krok_B.cmd, 17:57:33 - 17:59:30): `<KB>` = `<ROB>\robocze\K_B` (63 znaki) - NIE ZMIERZONO migracji: instalator odmowil (kod 6)

| Krok | Polecenie | Kod (oczekiwany) | Wynik |
|---|---|---|---|
| 2 | `<P1>\zainstaluj.cmd /katalog <KB> /python %PY% /bez-sieci /bez-pauzy` (2 razy, miedzy nimi edycja ustawien: 5 z 5) | 10, 0 (10, 0) | 0.3.3 zainstalowana w 76,2 s i 4,9 s - ta sama sciezka 63 znaki dla wersji 0.3.3 PRZESZLA |
| 3 | `<KB>\Stanowisko.cmd --zamknij-po 5` (2 razy) | 0, 0 (0, 0) | zdarzenia 4, user_version 1 |
| 4 | `<PM>\zainstaluj.cmd /katalog <KB> /python %PY% /bez-sieci /bez-pauzy` | **6 (0)** | po 0,7 s: "BLAD: sciezka katalogu instalacji jest za dluga (63 znakow; pliki pakietow przekroczylyby 259 znakow) / CO ZROBIC: Wybierz krotszy katalog, np. zainstaluj.cmd /katalog C:\Stanowisko. / INSTALACJA: NIEUDANA (kod 6) - wersja biezaca bez zmian: 0.3.3" (`t12_B_4.log`) |
| 5 | `<KB>\Stanowisko.cmd --zamknij-po 5` | 0 | wystartowala nadal wersja 0.3.3 (nie probna): user_version 1, zdarzenia 6 |
| 6, 7 | `Wroc_do_poprzedniej.cmd /tak /bez-pauzy`; `... /przywroc-kopie /bez-pauzy` | 9, 9 (8, 0) | "BLAD: nie ma poprzedniej wersji, do ktorej mozna wrocic (biezaca: 0.3.3)" - nastepstwo kroku 4 |
| 8 | `<KB>\Stanowisko.cmd --zamknij-po 5` | 0 (0) | 0.3.3 dziala; zdarzenia 8; `dane\kopie` nie powstal; ustawienia bez zmian (6 z 6 sum rownych) |

Przyczyna: katalog wybrany przez wykonawce. Plan pisze `<KB>` = `<ROB>\K_B`; w nocy `<ROB>\robocze\K_B` mialo 56 znakow i paczka
`0.3.9-migracja` instalowala sie; tu `<ROB>` jest dluzszy o 7 znakow (`odbior2\final`) -> 63 znaki. Instalator sprawdza dlugosc sciezki z
NAZWA WERSJI: dla `0.3.3` (5 znakow) 63 znaki przechodza, dla `0.3.9-migracja` (14 znakow) nie. Odmowa jest czytelna, nic nie zostalo
zmienione (wersja biezaca, baza, ustawienia - bez zmian). Wg reguly planu ("kod inny niz oczekiwany w ktorymkolwiek kroku = FAIL czesci
B") ta proba formalnie nie spelnia oczekiwan - opisuje ja jako probe NIEWAZNA z winy katalogu wykonawcy i powtarzam w krotszym katalogu;
ocena tej decyzji: do koordynatora.

### Proba 2 (krok_B2.cmd, 18:00:21 - 18:03:29): `<KB>` = `<PC-katalog>\t0\odbior2_t12\B\K_B` (34 znaki) - kody 9 z 9 zgodnych

Foldery wejsciowe: wlasne puste `<PC-katalog>\t0\odbior2_t12\B\wej\{eksport,Cyrkon,Prywatne,millbox}`; `<P1>` i `<PM>` jak wyzej.

| Krok | Godz. | Polecenie | Kod (oczekiwany) | Czas | Wynik | Log |
|---|---|---|---|---|---|---|
| 2 | 18:00:22 | `<P1>\zainstaluj.cmd /katalog <KB> /python %PY% /bez-sieci /bez-pauzy` | 10 (10) | 67,8 s | 0.3.3 zainstalowana, czeka na foldery | `t12_B2_2a.log` |
| 2 | 18:01:29 | edycja ustawien (`edytuj.ps1`: 4 foldery + `operatorzy`), to samo polecenie ponownie | 0; 0 (0) | 3,9 s | zmienionych wierszy 5 z 5; samokontrola ZIELONA (ok 16, ostrzezenia 5 - w tym pusta pula i brak bazy); `INSTALACJA: GOTOWA - wersja biezaca 0.3.3` | `t12_B2_2_edycja.log`, `t12_B2_2b.log` |
| 3 | 18:01:33 | `<KB>\Stanowisko.cmd --zamknij-po 5` dwa razy | 0, 0 (0, 0) | - | stan "przed": SHA-256 bazy 601f23ce...d75bbd90; 86016 B, skrot bez naglowka 6ad5420b...bd50d8a1; user_version 1; zdarzenia 4; skany 0; plikow w `dane\kopie` 0 | `t12_B2_3a.log`, `t12_B2_3b.log`, `t12_B2_stany.txt` |
| 4 | 18:01:50 | `<PM>\zainstaluj.cmd /katalog <KB> /python %PY% /bez-sieci /bez-pauzy` (aktualizacja paczka probna) | 0 (0) | 75,1 s | "baza: schemat 1; program 0.3.9-migracja obsluguje schemat 2"; "kopia bazy: kopie/stanowisko_przed_0.3.9-migracja_20261121_180301_v1.sqlite - sprawdzona (quick_check ok, schemat bazy 1; program 0.3.9-migracja: 2)"; samokontrola ZIELONA (ok 16, ostrzezenia 5, w tym "baza starsza niz program: wersja schematu 1, program ma 2 - migracja z kopia przy starcie programu"); `INSTALACJA: GOTOWA - wersja biezaca 0.3.9-migracja (poprzednia: 0.3.3)` | `t12_B2_4.log` |
| c1 | 18:03:05 | stan po kroku 4 | - | - | baza BEZ ZMIAN (SHA-256 601f23ce...d75bbd90 = krok 3); w `dane\kopie` 1 nowy plik: 86016 B = baza, skrot bez naglowka 6ad5420b...bd50d8a1 = baza z kroku 3 (ROWNE), user_version 1, zdarzenia 4; SHA-256 calego pliku kopii 069f496f...943e45ae (inne niz bazy - naglowek SQLite, jak w planie) | `t12_B2_stany.txt` |
| 5 | 18:03:06 | `<KB>\Stanowisko.cmd --zamknij-po 5` (pierwszy start wersji probnej - migracja) | 0 (0) | - | c2: user_version 1 -> 2; zdarzenia 4 -> 7; baza 90112 B; w `dane\kopie` nadal 1 plik; obok bazy program zalozyl wlasna kopie `dane\stanowisko.kopia_v1_20261121_180307.sqlite` (86016 B) | `t12_B2_5.log` |
| 6 | 18:03:14 | `<KB>\Wroc_do_poprzedniej.cmd /tak /bez-pauzy` (powrot bez zgody) | 8 (8) | - | "UWAGA: wersja 0.3.9-migracja zmienila schemat bazy - wersja 0.3.3 tej bazy NIE otworzy ... Po przywroceniu z bazy roboczej zniknie wszystko, co zapisano po tej chwili: 3 wpisow w 1 tabelach. tabela zdarzenia: 4 w kopii, 7 teraz (+3) ... Niczego nie zmieniono. POWROT: NIEUDANA (kod 8) - wersja biezaca bez zmian: 0.3.9-migracja"; baza bez zmian (SHA-256 58e95720...cf296600 przed i po) | `t12_B2_6.log` |
| 7 | 18:03:15 | `<KB>\Wroc_do_poprzedniej.cmd /przywroc-kopie /bez-pauzy` | 0 (0) | 2,8 s | "przywrocono kopie stanowisko.kopia_v1_20261121_180307.sqlite; dotychczasowa baza odlozona jako kopie/stanowisko_odlozona_v2_20261121_180316.sqlite"; samokontrola ZIELONA (ok 17, ostrzezenia 4); `POWROT: GOTOWY - wersja biezaca 0.3.3 (poprzednia: 0.3.9-migracja)`. Kontrola e: SHA-256 bazy 069f496f...943e45ae = SHA-256 pliku kopii z kroku 4 (cale pliki ROWNE, 1 z 1); user_version 1; zdarzenia 4 (= krok 3; 3 wpisy wersji probnej przepadly); w `dane\kopie` 2 pliki (kopia sprzed aktualizacji + baza odlozona: 90112 B, user_version 2, zdarzenia 7) | `t12_B2_7.log` |
| 8 | 18:03:19 | `<KB>\Stanowisko.cmd --zamknij-po 5` | 0 (0) | - | wersja 0.3.3 dziala na przywroconej bazie: zdarzenia 6, user_version 1; `Wersje.cmd`: 0.3.3 BIEZACA (schemat bazy 1), 0.3.9-migracja poprzednia (schemat bazy 2); `Traceback` w logu programu: 0 | `t12_B2_8.log`, `t12_B2_stany.txt` |

Liczby kryterium czesci B (proba 2): kody 9 polecen programu = 10, 0, 0, 0, 0, 0, 8, 0, 0 - 9 z 9 zgodnych; z 2 poleceniami kroku 1:
11 z 11 (noc: 11 z 11). Kopia sprzed migracji: 1 plik, rozmiar 86016 B i skrot bez naglowka = baza z kroku 3; user_version 1 -> 2 -> 1;
zdarzenia 4 -> 7 -> 4 (przepadly 3 wpisy - tyle samo co w nocy); SHA-256 bazy po kroku 7 = suma kopii; baza zmigrowana odlozona, nie
skasowana. Ustawienia `<KB>\ustawienia.toml`: 6 z 6 sum identycznych (345d65ca...f42fab8d). Powrot po migracji = 2 polecenia (kod 8,
potem `/przywroc-kopie`) - zachowanie zamierzone, pozycja do decyzji wlasciciela (O2), jak w nocy.

## Wynik wg kryterium (plan etapu, sekcja 7): wersja N -> N+1 -> powrot do N: jedno polecenie; ustawienia zachowane; baza zmigrowana z kopia

| Czesc kryterium | Werdykt | Liczby |
|---|---|---|
| aktualizacja N -> N+1 jednym poleceniem | ZAL | 1 wywolanie `zainstaluj.cmd`, kod 0, 100,5 s, `wersja_biezaca.txt` = 0.3.4-t12 |
| powrot do N jednym poleceniem | ZAL | 1 wywolanie `Wroc_do_poprzedniej.cmd /tak /bez-pauzy`, kod 0, 3,5 s, `wersja_biezaca.txt` = 0.3.3 |
| program dziala po aktualizacji i po powrocie | ZAL | samokontrola kod 0 i ZIELONA 2 z 2; start programu kod 0 - 2 z 2; `Traceback` 0 |
| ustawienia zachowane | ZAL | SHA-256 `ustawienia.toml` 5 z 5 identyczne (plan: 3 z 3) |
| dane nietkniete (czesc A) | ZAL | skany 0 = 0; zdarzenia tylko rosna (2 -> 6); plik bazy niezmieniony przez aktualizacje i przez powrot |
| baza zmigrowana z kopia (czesc B) | ZAL z odstepstwem O2 - w PROBIE 2; proba 1 niewazna (kod 6: sciezka instalacji wykonawcy za dluga) | proba 2: kody 11 z 11; kopia = baza sprzed migracji (rozmiar + skrot bez naglowka); user_version 1 -> 2 -> 1; zdarzenia 4 -> 7 -> 4; powrot po migracji 2 polecenia |
| NOWE: aktualizacja ze starego wydania 0.3.1 -> 0.3.3 -> powrot | zgodnie z oczekiwaniami zlecenia 5 z 5 | kody 9 z 9; samokontrola zielona, uklady 10 z 10, 6 skrotow, start kod 0, powrot kod 0; ustawienia 5 z 5 sum |

Wynik calego testu wg reguly planu: **ZAL z odstepstwem O2** (migracja na paczce probnej, kopia porownana bez 100-bajtowego naglowka,
powrot po migracji w 2 poleceniach) **+ NOWE** (nizej).

## Odstepstwa

- **O2** (RAPORT.md 4a): jak w planie i w nocy.
- **O1** (swiezy katalog zamiast czystego konta) - dotyczy instalacji przygotowawczych, jak w T0.
- **NOWE 1**: czesc B udala sie dopiero w PROBIE 2 - w probie 1 instalator odmowil aktualizacji paczka probna (kod 6) z powodu dlugosci
  sciezki katalogu wybranego przez wykonawce (63 znaki + nazwa wersji 14 znakow). Obie proby i wszystkie logi zostaja.
- **NOWE 2**: dodatek "aktualizacja ze starego wydania 0.3.1" (poza planem T12; zlecenie koordynatora).
- **NOWE 3**: instalacja czesci B (proba 2) w `<PC-katalog>\t0\odbior2_t12\B\K_B` zamiast `<ROB>\K_B` z planu; czesc B w katalogu
  `<ROB>\robocze` zamiast `<ROB>` (jak w nocy: bez baz i ZIP-ow w katalogu dowodow).

## Polecenia planu zmienione / potkniecia (wszystkie)

1. Rozpakowanie ZIP: `C:\Windows\System32\tar.exe -xf <zip> -C <katalog>` zamiast `Expand-Archive` (4 paczki: 0.3.3, 0.3.4-t12, 0.3.1,
   0.3.9-migracja; kody 0; wg zlecenia - znane zjawisko PC).
2. Krok 4 planu wykonany doslownie (`/tak /bez-pauzy`); prob z odpowiedzia `T` / `N` / brak odpowiedzi (noc) NIE powtarzano.
3. Liczby w planie nieaktualne dla tego wydania: sumy paczki 227 z 227 (plan 210), program 148 plikow (plan 131), sumy programu
   w samokontroli 147 z 147 (noc 130 z 130), uklady plytek 10 z 10 (noc 8 z 8).
4. Czesc B: `<KB>` z planu przy tym `<ROB>` za dlugi dla wersji `0.3.9-migracja` (kod 6) - patrz proba 1.
5. Blad wykonawcy bez wplywu na wynik: pierwsza kolejka krokow (17:42:15) nie wystartowala zadnego kroku - kontrola wolnego miejsca
   `(Get-PSDrive C).Free` w powershell 5.1 dala 0 GB (`kolejka_proba1_nieudana.txt`); poprawione na `System.IO.DriveInfo` i uruchomione
   ponownie 17:42:42 (kolejka czekala na koniec T2; START krok_A 17:48:14).
6. Stan bazy po kazdym kroku zbiera osobny plik `stan.cmd` (w nocy etykieta `:stan` w pliku kroku zawiodla 1 raz na 6) - tu 22 z 22
   wywolan (A 5, dodatek 5, B proba 1: 6, B proba 2: 6) dalo komplet danych.

## Obserwacje (nie zmieniaja wyniku)

- Instalator liczy limit dlugosci sciezki RAZEM z nazwa wersji: katalog, w ktorym wersja `0.3.3` zainstalowala sie i dzialala (63
  znaki), odrzucil aktualizacje do wersji o dluzszej nazwie (`0.3.9-migracja`, kod 6, czytelny komunikat, nic nie zmienione). Dla nazw
  wydan tej samej dlugosci (0.3.3 -> 0.3.4) nie ma to znaczenia; instalacja czesci A (39 znakow) przyjela wersje `0.3.4-t12` (9 znakow), instalacja
  dodatku (44 znaki) wersje 0.3.1 i 0.3.3, instalacja czesci B proba 2 (34 znaki) wersje `0.3.9-migracja` - bez uwag. W nocy 56 znakow
  z `0.3.9-migracja` przeszlo; granica lezy wiec miedzy 56 a 63 znakami dla nazwy 14-znakowej (dokladnej NIE mierzylem).
- Po aktualizacji ze starego wydania plik ustawien NIE dostaje nowych ukladow `[plytki]` - program bierze je z wartosci domyslnych i
  samokontrola mowi o tym wprost ("2 klucze z wartoscia domyslna").
- Po powrocie do 0.3.1 w katalogu zostaje skrot `Dzien_skanera.cmd` (zalozony przez 0.3.3) - nieuruchamiany w tym tescie.
- Kazdy start programu w tej sesji (0.3.1, 0.3.3, 0.3.4-t12, 0.3.9-migracja; 15 z 15 logow startu, 306-335 bajtow) wypisuje na konsole
  3 wiersze Qt o czcionkach; w nocy logi startow mialy 0 bajtow takze dla 0.3.1 - roznica sesji / srodowiska, nie wersji programu.

## Do decyzji koordynatora / wlasciciela

1. (wlasciciel, O2) Powrot po migracji bazy w 2 poleceniach (kod 8, potem `/przywroc-kopie`, z utrata wpisow zrobionych po
   aktualizacji - tu 3) - jak w nocy.
2. (koordynator) Jak liczyc probe 1 czesci B (kod 6 przez dlugosc sciezki katalogu wykonawcy): przyjalem "proba niewazna + powtorka w
   krotszym katalogu, obie zapisane"; wg litery planu kod inny niz oczekiwany = FAIL proby.
3. (koordynator / wlasciciel) Czy limit dlugosci sciezki zalezny od nazwy wersji wymaga wzmianki w instrukcji (katalog dobry dla wersji
   N moze byc za dlugi dla wersji o dluzszej nazwie) - obserwacja, nie wynik T12.
4. (koordynator) Skrot `Dzien_skanera.cmd` po powrocie do 0.3.1: dzialanie NIE ZMIERZONE.

## Stan po tescie (zostawione, nic nie skasowano)

- `<PC-katalog>\t0\odbior2_t12\` (9,7 GB razem): `Stanowisko` - biezaca **0.3.3**, poprzednia 0.3.4-t12, suma ustawien afc80421...6f96123c,
  baza: skany 0, zdarzenia 6, user_version 1, `dane\kopie` 1 plik; `paczka_0.3.3`, `paczka_0.3.4-t12`, `dane\`; `z031\Stanowisko` - biezaca
  **0.3.1**, poprzednia 0.3.3, suma ustawien 6fb7a030...f711740b, zdarzenia 6, `dane\kopie` 1 plik; `z031\paczka_0.3.1`, `z031\dane\`;
  `B\K_B` - biezaca 0.3.3, poprzednia 0.3.9-migracja (po czesci B nie nadaje sie do innych testow), `B\wej\`.
- `<ROB>\robocze` (2,3 GB; poza dowodami): `K_B` (proba 1: sama 0.3.3, 1,4 GB), `paczka_M`, `paczki\Stanowisko_0.3.9-migracja.zip`,
  `drzewo_M`, `wej`, kopie ustawien (`ustawienia_po_pierwszej_instalacji.toml`, `z031_ustawienia_przed.toml`), `proba_stan.txt` (proba
  skladni `stan.cmd` na instalacji z nocy `t0\odbior_t12` - TYLKO ODCZYT, 17:42:09). Sprzata koordynator.
- Procesy (18:04): 0 procesow python tej sesji; zyjace python naleza do T1 (PID 15568, 29124, 21228) i T11 (PID 15796, 6308, 16940 -
  rodzic: `ciezki.ps1` wykonawcy T11) oraz PID 12560 (znany, niczyj). Kolejki powershell tej sesji zakonczone.
- Repo: `git status --short` pusty w `<PC-katalog>\t0\repo2`, `<PC-katalog>\qc-wt\integ` (HEAD 0fedbf6) i `<PC-katalog>\qc`; zadnych commitow.
- Wolne na C: 36 GB (17:37) -> 17 GB (18:04; w tym czasie instalowaly takze T0 / T1 i T11 dopisuje skany).
- Godziny T12: 17:48:14 (START krok_A) - 18:03:29 (KONIEC krok_B2). Kontroli `t9_dane_osobowe.py` i `dowody_lf.py` NIE uruchamialem
  (logi instalatora maja CRLF; nazw zlecen w dowodach T12 nie ma - puste bazy, 0 skanow).
