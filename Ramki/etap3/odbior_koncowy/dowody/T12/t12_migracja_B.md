# T12 czesc B - "baza zmigrowana z kopia" na paczce PROBNEJ (odstepstwo O2), odbior 21.11.2026

Oznaczenia: `<ROB>` = `<PC-katalog>\koordynator\robocze\odbior\T12`, `<RB>` = `<ROB>\robocze` (katalog roboczy czesci B - patrz
"Zmiany wobec planu"), `<KB>` = `<RB>\K_B` (OSOBNA instalacja), `<PM>` = `<RB>\paczka_M`, `<M>` = `0.3.9-migracja`,
`<P1>` = `<PC-katalog>\t0\odbior\paczka_0.3.1`, `<REPO>` = `<PC-katalog>\t0\repo` (571e186), `<ODB>` = `<REPO>\Ramki\etap3\odbior_koncowy`,
`PY` = `<PC>\AppData\Local\Programs\Python\Python312\python.exe`.
Calosc jako jeden plik `krok_B.cmd` (kazde polecenie z `call`, wejscie `< NUL`, `set QT_QPA_PLATFORM=offscreen`) pod blokada
`ciezki.ps1 -Tor 4 -Kto odb-T12`, 02:55:37-02:59:47 (czesc B: 02:56:11-02:59:47 = 3 min 37 s samych polecen). Kody: `kody.txt`
(wiersze `B...`), godziny: `czasy.txt`, stany bazy: `t12_B_stany.txt`.

## Kroki

| Krok | Polecenie | Kod (oczek.) | Czas | Ostatni wiersz / wynik | Log |
|---|---|---|---|---|---|
| 1 | `PY -I <ODB>\narzedzia\t12_paczka_migracja.py --repo <REPO> --roboczy <RB> --wersja 0.3.9-migracja --wyjscie <RB>\paczki --kola <PC-katalog>\wydania\kola` | 0 (0) | 6,9 s | commit 571e186cb817...; "schemat bazy w kopii: 1 -> 2 (MIGRACJE[2] = CREATE TABLE proba_migracji_odbior ...)"; ZIP 444 935 282 B, 210 plikow + SHA256SUMS; SHA-256 ed97a4b0a5c5c4f1bf3555821c4272ee1f79096d6d56e4dc39f136145340ccea; "repo zrodlowe bez zmian (git status --short: 0 wierszy przed i po)" | `t12_B_paczka.txt` |
| 1 | `powershell -NoProfile -Command "Expand-Archive -LiteralPath <RB>\paczki\Stanowisko_0.3.9-migracja.zip -DestinationPath <PM>"` | 0 (0) | 4,5 s | `<PM>\zainstaluj.cmd` istnieje | `t12_B_paczka.txt` |
| 2 | `<P1>\zainstaluj.cmd /katalog <KB> /python %PY% /bez-sieci /bez-pauzy` | 10 (10) | 82,1 s | `INSTALACJA: WSTRZYMANA - uzupelnij ustawienia.toml i uruchom zainstaluj.cmd ponownie (kod 10)` | `t12_B_2a.log` |
| 2 | edycja `<KB>\ustawienia.toml`: 4 foldery `[sciezki]` = puste `<RB>\wej\{eksport,Cyrkon,Prywatne,millbox}` (ukosniki `/`), `operatorzy = ["Technik A"]` (skrypt `robocze\edytuj_KB.ps1`) | 0 | - | zmienionych wierszy 5 z 5 | `t12_B_stany.txt` (1. wiersz) |
| 2 | to samo polecenie `zainstaluj.cmd` ponownie | 0 (0) | 4,6 s (z edycja) | `INSTALACJA: GOTOWA - wersja biezaca 0.3.1 (poprzednia: brak)` | `t12_B_2b.log` |
| 3 | `<KB>\Stanowisko.cmd --zamknij-po 5` (1. raz) | 0 (0) | ok. 8 s | (brak wyjscia na konsole) | `t12_B_3a.log` |
| 3 | `<KB>\Stanowisko.cmd --zamknij-po 5` (2. raz) | 0 (0) | ok. 8 s | (brak wyjscia na konsole) | `t12_B_3b.log` |
| 4 | `<PM>\zainstaluj.cmd /katalog <KB> /python %PY% /bez-sieci /bez-pauzy` | 0 (0) | 78,7 s | "baza: schemat 1; program 0.3.9-migracja obsluguje schemat 2"; "kopia bazy: kopie/stanowisko_przed_0.3.9-migracja_20261121_025918_v1.sqlite - sprawdzona (quick_check ok, schemat bazy 1; program 0.3.9-migracja: 2)"; `INSTALACJA: GOTOWA - wersja biezaca 0.3.9-migracja (poprzednia: 0.3.1)` | `t12_B_4.log` |
| 5 | `<KB>\Stanowisko.cmd --zamknij-po 5` (wersja probna - migracja) | 0 (0) | ok. 8 s | (brak wyjscia na konsole) | `t12_B_5.log` |
| 6 | `<KB>\Wroc_do_poprzedniej.cmd /tak /bez-pauzy` | 8 (8) | 1,3 s | "UWAGA: wersja 0.3.9-migracja zmienila schemat bazy - wersja 0.3.1 tej bazy NIE otworzy."; "Po przywroceniu z bazy roboczej zniknie wszystko, co zapisano po tej chwili: 3 wpisow w 1 tabelach. tabela zdarzenia: 4 w kopii, 7 teraz (+3)"; `BLAD: powrot do 0.3.1 wymaga przywrocenia kopii bazy sprzed aktualizacji`; `POWROT: NIEUDANA (kod 8) - wersja biezaca bez zmian: 0.3.9-migracja` | `t12_B_6.log` |
| 7 | `<KB>\Wroc_do_poprzedniej.cmd /przywroc-kopie /bez-pauzy` | 0 (0) | 3,2 s | "przywrocono kopie stanowisko.kopia_v1_20261121_025926.sqlite; dotychczasowa baza odlozona jako kopie/stanowisko_odlozona_v2_20261121_025935.sqlite"; samokontrola ZIELONA (ok 17, ostrzezenia 4); `POWROT: GOTOWY - wersja biezaca 0.3.1 (poprzednia: 0.3.9-migracja)` | `t12_B_7.log` |
| 8 | `<KB>\Stanowisko.cmd --zamknij-po 5` (wersja N na przywroconej bazie) | 0 (0) | ok. 8 s | (brak wyjscia na konsole); `Traceback` w `<KB>\dane\logi\stanowisko.log`: 0 | `t12_B_8.log` |

Kody 9 polecen programu (kroki 2-8): 10, 0, 0, 0, 0, 0, 8, 0, 0 = **9 z 9 zgodnych**; razem z 2 poleceniami kroku 1: **11 z 11**.

## Stany bazy `<KB>\dane\stanowisko.sqlite` (z `t12_B_stany.txt`)

Polecenia: `certutil -hashfile <plik> SHA256`; `PY -I -c "import hashlib,sys;d=open(sys.argv[1],'rb').read();print(len(d),hashlib.sha256(d[100:]).hexdigest())" <plik>`;
`PY -I <ODB>\narzedzia\sql_odczyt.py --baza <plik> "SELECT user_version FROM pragma_user_version"` i `"SELECT count(*) FROM zdarzenia"`.

| Chwila | Wersja biezaca | SHA-256 pliku bazy | Rozmiar | Skrot od 100. bajtu | user_version | zdarzenia | Pliki w `dane\kopie` |
|---|---|---|---|---|---|---|---|
| po kroku 3 (przed aktualizacja) | 0.3.1 | fbe081c3...b31ceded | 86016 | 4c38ce10...09595748 | 1 | 4 | 0 |
| po kroku 4 (kontrola c1) | - | NIE ZAPISANO w tym przebiegu (blad pliku `krok_B.cmd`, patrz nizej) - zmierzone w uzupelnieniu | | | | | |
| po kroku 5 (kontrola c2) | 0.3.9-migracja | 56970a11...290a5ecf | 90112 | fda9bd55...2482678a | 2 | 7 | 1 |
| po kroku 6 (kod 8) | 0.3.9-migracja | 56970a11...290a5ecf (bez zmian) | 90112 | fda9bd55...2482678a | 2 | 7 | 1 |
| po kroku 7 (kontrola e) | 0.3.1 | ef6a2bc7...eddf15e3 | 86016 | 4c38ce10...09595748 | 1 | 4 | 2 |
| po kroku 8 | 0.3.1 | 6a7f8317...2b25304c | 86016 | 55ba0533...ed1f5314 | 1 | 6 | 2 |

Kopie:

| Plik | Rozmiar | SHA-256 calego pliku | Skrot od 100. bajtu | user_version | zdarzenia |
|---|---|---|---|---|---|
| `dane\kopie\stanowisko_przed_0.3.9-migracja_20261121_025918_v1.sqlite` (kopia instalatora, krok 4) | 86016 | ef6a2bc7...eddf15e3 | 4c38ce10...09595748 | 1 | 4 |
| `dane\stanowisko.kopia_v1_20261121_025926.sqlite` (kopia zrobiona przez program przy migracji, krok 5; lezy OBOK bazy) | 86016 | fbe081c3...b31ceded (= baza z kroku 3 co do bajta) | (nie liczono) | (nie czytano) | (nie czytano) |
| `dane\kopie\stanowisko_odlozona_v2_20261121_025935.sqlite` (baza zmigrowana odlozona w kroku 7) | 90112 | 69773e9c...68e8f900 | fda9bd55...2482678a | 2 | 7 |

## Kontrole kryterium czesci B

| Kontrola | Wynik | Liczby |
|---|---|---|
| kody polecen | ZGODNE | 9 z 9 (z krokiem 1: 11 z 11) |
| kopia sprzed migracji: 1 plik w `dane\kopie`, rozmiar i skrot tresci bez naglowka = baza z kroku 3 | TAK | 86016 = 86016; 4c38ce10...09595748 = 4c38ce10...09595748; user_version 1 = 1; zdarzenia 4 = 4; SHA-256 calego pliku kopii ef6a2bc7... != fbe081c3... bazy (naglowek SQLite - O2, to nie FAIL) |
| c1: baza bez zmian zaraz po aktualizacji (przed startem wersji probnej) | TAK - w uzupelnieniu (nizej): SHA-256 bazy po kroku 4 = SHA-256 po kroku 3 | 8904d20a...3c0aefcd = 8904d20a...3c0aefcd (instalacja `K_B2`); w przebiegu glownym stan w tej chwili niezapisany |
| c2: `user_version` po kroku 5 > po kroku 3; zdarzenia rosna; w `kopie` nadal 1 plik | TAK | 2 > 1; 4 -> 7; 1 plik |
| krok 6: wersja biezaca i baza bez zmian | TAK | 0.3.9-migracja; SHA-256 56970a11... = 56970a11... |
| e: po kroku 7 SHA-256 bazy = SHA-256 kopii z kroku 4; `user_version` = wartosc z kroku 3; zdarzenia = liczba z kopii; baza zmigrowana odlozona (2 pliki w `kopie`) | TAK | ef6a2bc7... = ef6a2bc7... (cale pliki rowne, 1 z 1); 1 = 1; 4 = 4; przepadly 3 wpisy dopisane przez wersje probna (7 -> 4; instalator zapowiedzial "+3" przed zgoda); `stanowisko_odlozona_v2_...sqlite` jest |
| krok 8: wersja N dziala na przywroconej bazie | TAK | kod 0; zdarzenia 4 -> 6; `Traceback` 0 |

**Wynik czesci B: "baza zmigrowana z kopia": ZAL** (wg liczb wyzej; sposob porownania kopii = odstepstwo O2).
**Do decyzji wlasciciela (O2, `RAPORT.md` 4a poz. 11):** powrot po migracji bazy = 2 polecenia (kod 8, potem `/przywroc-kopie`);
przy powrocie przepadaja wpisy zrobione po aktualizacji (tu 3 zdarzenia; skrypt wypisuje to przed zgoda).

## Uzupelnienie kontroli c1 (druga instalacja `<RB>\K_B2`, plik `krok_B_uzup.cmd`, 03:00:51-03:03:55)

Przyczyna: w `krok_B.cmd` jedno z 6 wywolan podprogramu `call :stan` (to po kroku 4) skonczylo sie bledem cmd.exe
"The system cannot find the batch label specified - stan" (blad narzedzia wykonawcy, nie programu; pozostale 5 wywolan zadzialalo).
Stan bazy zaraz po kroku 4 nie zostal wiec zapisany. Kroki 2-4 powtorzono w nowym katalogu, bez podprogramu:

| Krok | Polecenie | Kod | Czas | Log |
|---|---|---|---|---|
| 2 | `<P1>\zainstaluj.cmd /katalog <RB>\K_B2 /python %PY% /bez-sieci /bez-pauzy` | 10 | 81,0 s | `t12_B_uzup_2a.log` |
| 2 | edycja ustawien (5 z 5 wierszy), to samo polecenie ponownie | 0 | - | `t12_B_uzup_2b.log` |
| 3 | `<RB>\K_B2\Stanowisko.cmd --zamknij-po 5` dwa razy | 0, 0 | - | `t12_B_uzup_3a.log`, `t12_B_uzup_3b.log` |
| 4 | `<PM>\zainstaluj.cmd /katalog <RB>\K_B2 /python %PY% /bez-sieci /bez-pauzy` | 0 | 80,7 s | `t12_B_uzup_4.log` |

Stany (`t12_B_uzup_stany.txt`): po kroku 3: SHA-256 8904d20a...3c0aefcd, 86016 B, skrot od 100. bajtu a18a01fc...4618cc61,
user_version 1, zdarzenia 4, `kopie` 0 plikow. **Po kroku 4 (c1): baza SHA-256 8904d20a...3c0aefcd (bez zmian), user_version 1,
zdarzenia 4; w `kopie` 1 nowy plik `stanowisko_przed_0.3.9-migracja_20261121_030348_v1.sqlite`: 86016 B, skrot od 100. bajtu
a18a01fc...4618cc61 (= baza), SHA-256 calego pliku 62207351...7725b634 (inne niz bazy - naglowek), user_version 1, zdarzenia 4.**
Instalacji `K_B2` dalej nie uzywano (wersja biezaca 0.3.9-migracja, baza niezmigrowana - program wersji probnej nie byl uruchomiony).

## Zmiany wobec planu i obserwacje

1. Katalog roboczy czesci B: `<ROB>\robocze` zamiast `<ROB>` (zasada 3 zlecenia wspolnego: duze pliki robocze - drzewo, ZIP 424 MB,
   instalacje, bazy - w podkatalogu `robocze\`, zeby katalog dowodow nie zawieral baz i ZIP-ow). Polecenia poza sciezka bez zmian.
2. Kontrola c1 zmierzona w drugiej instalacji (`K_B2`), nie w `K_B` (wyzej).
3. Obserwacja (nie ma jej w planie): przy pierwszym starcie wersji probnej program sam robi DRUGA kopie bazy obok pliku bazy
   (`dane\stanowisko.kopia_v1_<data>.sqlite`, bajt w bajt rowna bazie sprzed migracji: SHA-256 fbe081c3...). `Wroc_do_poprzedniej.cmd
   /przywroc-kopie` przywrocil wlasnie te kopie ("najnowsza sprawdzona"; kopia instalatora wymieniona jako "starszych kopii: 1").
   Baza po przywroceniu ma mimo to SHA-256 rowne kopii INSTALATORA z kroku 4 (ef6a2bc7...) i tresc od 100. bajtu rowna bazie sprzed
   migracji - kontrola e planu jest spelniona.
4. Paczki probnej nie publikowano i nie wpisano do `SHA256SUMS_wydania.txt`; lezy w `<RB>\paczki\` (poza repo).
