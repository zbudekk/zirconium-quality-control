# T12 czesc A - kroki (odbior 21.11.2026, wykonawca testow koncowych, tor 4)

Oznaczenia: `<K>` = `<PC-katalog>\t0\odbior_t12\Stanowisko`, `<P1>` = `<PC-katalog>\t0\odbior\paczka_0.3.1` (paczka rozpakowana
przez T0, tylko czytana), `<P2>` = `<PC-katalog>\t0\odbior_t12\paczka_0.3.2`, `<ROB>` = `<PC-katalog>\koordynator\robocze\odbior\T12`,
`PY` = `<PC>\AppData\Local\Programs\Python\Python312\python.exe`, `<ODB>` = `<PC-katalog>\t0\repo\Ramki\etap3\odbior_koncowy`.
Kazde polecenie z pliku `.cmd` (z `call`, wejscie `< NUL`, `set QT_QPA_PLATFORM=offscreen`) pod blokada
`ciezki.ps1 -Tor 4 -Kto odb-T12`. Pliki polecen: `krok_P3.cmd`, `krok_A1.cmd`, `krok_A2.cmd`, `krok_A4.cmd`, `krok_B.cmd` (poczatek).
Kody: `kody.txt`; godziny: `czasy.txt`. PELNE wyjscie konsoli kazdego polecenia: plik z kolumny "log".

## Przygotowanie (kroki 2-5 i 7 z T0 w katalogu odbior_t12)

| Krok | Godz. | Polecenie | Kod | Czas | Wynik (ostatni wiersz / liczby) | Log |
|---|---|---|---|---|---|---|
| T0-2 | 02:49:49 | `certutil -hashfile <PC-katalog>\wydania\Stanowisko_0.3.1.zip SHA256` (i `_0.3.2.zip`) | 0 | - | 0.3.1: f5affa81...3e24eec8 = plik `.sha256` = zlecenie; 0.3.2: 030c72d8...42abad96c = plik `.sha256` = zlecenie (2 z 2 zgodne) | `t12_sha256_zip.txt` |
| T0-2 | 02:49:50 | `powershell -NoProfile -Command "Expand-Archive -LiteralPath <PC-katalog>\wydania\Stanowisko_0.3.2.zip -DestinationPath <PC-katalog>\t0\odbior_t12\paczka_0.3.2"` | 0 | 2,7 s | 211 plikow (210 + SHA256SUMS) | - |
| T0-3 | 02:49:55 | `<P1>\zainstaluj.cmd /katalog <K> /python %PY% /bez-sieci /bez-pauzy` | 10 | 51,2 s | sumy "zgodne 210 z 210", pakiety "73 z 73", samokontrola CZERWONA (ok 11, ostrzezenia 8, bledy 2: folder_skanera, folder_cyrkon), `INSTALACJA: WSTRZYMANA - uzupelnij ustawienia.toml i uruchom zainstaluj.cmd ponownie (kod 10)` | `t12_P3_zainstaluj_N_1.log` |
| T0-4 | 02:51:19 | edycja `<K>\ustawienia.toml` (UTF-8 bez BOM): 4 foldery `[sciezki]` -> `<PC-katalog>/t0/odbior_t12/dane/{eksport,Cyrkon,Prywatne,millbox}` (Cyrkon = kopia `<PC-katalog>\app\Prace_test`: 15 folderow, 17 STL, `robocopy /E`), `operatorzy = ["Technik A"]` | - | - | zmienionych wierszy 5 z 5 | - |
| T0-5 | 02:51:20 | `<P1>\zainstaluj.cmd /katalog <K> /python %PY% /bez-sieci /bez-pauzy` | 0 | 3,1 s | samokontrola ZIELONA (ok 17, ostrzezenia 4), `INSTALACJA: GOTOWA - wersja biezaca 0.3.1 (poprzednia: brak)` | `t12_P5_zainstaluj_N_2.log` |
| T0-7 | 02:51:23 | `<K>\Stanowisko.cmd --atrapa --zamknij-po 5` | 0 | 6,4 s | (program nic nie pisze na konsole - log 0 bajtow) | `t12_P7a_start_atrapa.log` |
| T0-7 | 02:51:30 | `<K>\Stanowisko.cmd --zamknij-po 20` | 0 | 22,5 s | start prawdziwego kontrolera; baza zalozona | `t12_P7b_start.log` |

## T12 czesc A

| Krok | Godz. | Polecenie | Kod | Czas | Wynik | Log |
|---|---|---|---|---|---|---|
| 1 | 02:51:53 | `certutil -hashfile <K>\ustawienia.toml SHA256` | 0 | - | 1274f09de600273b69713fd327e1bfa1ba5fa76d098c3e6a50c114ab6da4d022 | `t12_ustawienia_przed.txt` |
| 1 | 02:51:53 | `<K>\Wersje.cmd /bez-pauzy` | 0 | - | 1 wersja: 0.3.1 BIEZACA, schemat bazy 1 | `t12_A1_wersje_przed.log` |
| 1 | 02:51:53 | `PY -I <ODB>\narzedzia\sql_odczyt.py --baza <K>\dane\stanowisko.sqlite "SELECT count(*) FROM skany"` (oraz `zdarzenia`, `user_version`); `certutil` bazy; rozmiar i skrot bez naglowka (`PY -I -c ...` z planu) | 0, 0, 0 | - | skany 0, zdarzenia 2, user_version 1; SHA-256 bazy 99f3203a...eb3463b0; 86016 B, skrot od 100. bajtu 3d7d9168...ef95d761; w `dane\kopie` 0 plikow | `t12_A1_baza_przed.txt` |
| 2 | 02:52:15 | **`<P2>\zainstaluj.cmd /katalog <K> /python %PY% /bez-sieci /bez-pauzy`** (aktualizacja, 1 polecenie) | **0** | **60,4 s** | sumy 210 z 210 (wersja 0.3.2, commit 571e186cb817); "istniejacy ustawienia.toml zostaje bez zmian (SHA-256 1274f09de600273b...)"; pakiety 73 z 73; "kopia bazy: kopie/stanowisko_przed_0.3.2_20261121_025311_v1.sqlite - sprawdzona (quick_check ok, schemat bazy 1; program 0.3.2: 1)"; samokontrola ZIELONA (ok 18, ostrzezenia 3); `INSTALACJA: GOTOWA - wersja biezaca 0.3.2 (poprzednia: 0.3.1)` | `t12_zainstaluj_N1.log` |
| 2 | 02:53:16 | kontrola po aktualizacji, przed startem 0.3.2: `type <K>\wersja_biezaca.txt`, `certutil` bazy i kopii, skrot bez naglowka, `sql_odczyt.py` na kopii | 0 | - | `wersja_biezaca.txt` = 0.3.2; baza bez zmian (SHA-256 99f3203a...eb3463b0 = krok 1); w `dane\kopie` 1 plik; kopia: 86016 B i skrot bez naglowka 3d7d9168...ef95d761 = baza z kroku 1 (rowne), SHA-256 calego pliku kopii d8831d3f...4181c770 (inne niz bazy - naglowek, O2), user_version 1, zdarzenia 2, skany 0 (jak baza z kroku 1) | `t12_A2_baza_po_aktualizacji.txt` |
| 3 | 02:53:16 | `<K>\Samokontrola.cmd --bez-sieci` | 0 | 2,5 s | `SAMOKONTROLA: ZIELONA (ok 18, ostrzezenia 3)`; sumy programu 130 z 130 | `t12_A3_samokontrola_N1.log` |
| 3 | 02:53:19 | `<K>\Stanowisko.cmd --zamknij-po 20` | 0 | 22,9 s | program 0.3.2 dziala | `t12_A3_start_N1.log` |
| 3 | 02:53:42 | `certutil -hashfile <K>\ustawienia.toml SHA256` | 0 | - | 1274f09d...6da4d022 = krok 1 | `t12_ustawienia_po_N1.txt` |
| 3 | 02:53:42 | `<K>\Wersje.cmd /bez-pauzy`; liczby bazy | 0 | - | 0.3.1 poprzednia, 0.3.2 BIEZACA; skany 0, zdarzenia 4 (+2 = start programu), user_version 1 | `t12_A3_wersje_po_N1.log`, `t12_A3_baza_po_starcie_N1.txt` |
| 4a | 02:54:09 | `<K>\Wroc_do_poprzedniej.cmd /bez-pauzy < NUL` (brak odpowiedzi) | 11 | 0,2 s | `POWROT: ANULOWANY (kod 11) - wersja biezaca bez zmian: 0.3.2`; `wersja_biezaca.txt` = 0.3.2 | `t12_wroc.log` |
| 4b | 02:54:09 | `echo N| <K>\Wroc_do_poprzedniej.cmd /bez-pauzy` (odpowiedz N) | 11 | 0,3 s | `POWROT: ANULOWANY (kod 11) - wersja biezaca bez zmian: 0.3.2`; `wersja_biezaca.txt` = 0.3.2 | `t12_wroc.log` |
| 4c | 02:54:10 | **`echo T| <K>\Wroc_do_poprzedniej.cmd /bez-pauzy`** (odpowiedz T; powrot, 1 polecenie) | **0** | **2,6 s** | "schemat zgodny - baza zostaje bez zmian"; samokontrola ZIELONA (ok 18, ostrzezenia 3); `POWROT: GOTOWY - wersja biezaca 0.3.1 (poprzednia: 0.3.2)`; `wersja_biezaca.txt` = 0.3.1 | `t12_wroc.log` |
| 5 | 02:54:12 | `<K>\Samokontrola.cmd --bez-sieci` | 0 | 2,7 s | `SAMOKONTROLA: ZIELONA (ok 18, ostrzezenia 3)` | `t12_A5_samokontrola_N.log` |
| 5 | 02:54:15 | liczby bazy przed startem 0.3.1 | 0 | - | skany 0, zdarzenia 4, user_version 1; SHA-256 bazy 72085474...d9050f41 = stan po starcie 0.3.2 (powrot bazy nie ruszyl) | `t12_A5_baza_po_powrocie.txt` |
| 5 | 02:54:15 | `<K>\Stanowisko.cmd --zamknij-po 20` | 0 | 23,2 s | program 0.3.1 dziala po powrocie | `t12_A5_start_N.log` |
| 5 | 02:54:39 | `certutil -hashfile <K>\ustawienia.toml SHA256` | 0 | - | 1274f09d...6da4d022 = krok 1 | `t12_ustawienia_po_powrocie.txt` |
| 5 | 02:54:39 | `<K>\Wersje.cmd /bez-pauzy`; liczby bazy | 0 | - | 0.3.1 BIEZACA, 0.3.2 poprzednia; skany 0 (= krok 1), zdarzenia 6, user_version 1; w `dane\kopie` 1 plik | `t12_A5_wersje_po_powrocie.log`, `t12_A5_baza_po_powrocie.txt` |

## Dodatkowo: polecenie planu z kroku 4 doslownie (`/tak`)

Zlecenie kazalo sprawdzic powrot z odpowiedziami na pytanie `[T/N]` (kroki 4a-4c). Polecenie z planu
(`Wroc_do_poprzedniej.cmd /tak /bez-pauzy`) wykonano potem osobno, w dodatkowym cyklu (0.3.1 -> 0.3.2 -> 0.3.1):

| Krok | Godz. | Polecenie | Kod | Czas | Wynik | Log |
|---|---|---|---|---|---|---|
| 4d | 02:55:37 | `<K>\Wroc_do_poprzedniej.cmd /tak /bez-pauzy` (z 0.3.1 na 0.3.2) | 0 | 3,1 s | `POWROT: GOTOWY - wersja biezaca 0.3.2 (poprzednia: 0.3.1)` | `t12_wroc_tak.log` |
| 4e | 02:55:40 | `<K>\Wroc_do_poprzedniej.cmd /tak /bez-pauzy` (z 0.3.2 na 0.3.1 - krok 4 planu doslownie) | 0 | 3,3 s | `POWROT: GOTOWY - wersja biezaca 0.3.1 (poprzednia: 0.3.2)`; `wersja_biezaca.txt` = 0.3.1 | `t12_wroc_tak.log` |
| 6 | 02:55:43 | `<K>\Samokontrola.cmd --bez-sieci`; `<K>\Stanowisko.cmd --zamknij-po 20` | 0; 0 | - | ZIELONA (ok 18, ostrzezenia 3); program dziala | `t12_A6_samokontrola_koniec.log`, `t12_A6_start_koniec.log` |
| 6 | 02:56:10 | stan koncowy: `certutil` ustawien, `Wersje.cmd /bez-pauzy`, liczby bazy, `find /c "Traceback" <K>\dane\logi\stanowisko.log` | 0 | - | suma ustawien 1274f09d...6da4d022 (bez zmian); 0.3.1 BIEZACA, 0.3.2 poprzednia; skany 0, zdarzenia 8, user_version 1; `dane\kopie` 1 plik; `Traceback` 0 wierszy (log 28 wierszy) | `t12_A6_stan_koncowy.txt` |

## Liczby

- Kody polecen programu w czesci A (przygotowanie + kroki 1-5): 10, 0, 0, 0 (przygotowanie) oraz 0 (aktualizacja), 0, 0 (krok 3),
  11, 11, 0 (krok 4a-4c), 0, 0 (krok 5) - wszystkie zgodne z oczekiwanymi (12 z 12); dodatkowy cykl `/tak`: 0, 0, 0, 0 (4 z 4).
- Sumy `ustawienia.toml`: przed / po 0.3.2 / po powrocie / stan koncowy = 4 z 4 identyczne (plan wymaga 3 z 3).
- Zdarzenia w bazie: 2 -> 4 -> 6 -> 8 (po 2 na kazdy start programu z kontrolerem; nic nie ubylo); skany 0 -> 0 -> 0 -> 0.
- Co jeszcze liczylo na PC (z `<PC-katalog>\koordynator\log\ciezkie.log`): tor 1 - T0 do 02:50:15, potem T1 (pelny pytest od
  02:53:21); tor 2 - T10 (regresja silnika od 02:52:26); tor 3 - brak wpisu w tym czasie. Wolny RAM 73-78 GB.
