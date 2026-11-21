WERDYKT T12: ZAL z odstepstwem O2 (czesc A: aktualizacja 0.3.1 -> 0.3.2 i powrot do 0.3.1 po 1 poleceniu, kody 0 i 0; ustawienia 4 z 4 sum identyczne; czesc B: baza zmigrowana z kopia - kody 11 z 11, powrot po migracji = 2 polecenia - do decyzji wlasciciela)

# T12 - Aktualizacja (N = 0.3.1, N+1 = 0.3.2) - wynik odbioru 21.11.2026

Wykonawca: sesja wykonawcy testow koncowych (T12, T7, T13), tor 4 ciezkich krokow. Godziny: 02:48 (start czytania planu) -
02:49:49 (pierwsze polecenie) - 03:03:55 (ostatnie polecenie, uzupelnienie czesci B).
Paczki: `<PC-katalog>\wydania\Stanowisko_0.3.1.zip` (SHA-256 f5affa81aea9969c6c42bf8e9e56ed6ad564dc948b15e92b8c7989383e24eec8) i
`Stanowisko_0.3.2.zip` (030c72d86420e9461a3de93b47d7a68baa80bfbb52aa0078bf1907c42abad96c) - obie sumy policzone `certutil`, zgodne z
plikami `.sha256` i ze zleceniem (2 z 2; `t12_sha256_zip.txt`). Instalator: sumy paczki "zgodne 210 z 210" (obie paczki), commit
571e186cb817. Instalacja WLASNA T12: `<K>` = `<PC-katalog>\t0\odbior_t12\Stanowisko`; paczka 0.3.1 czytana z
`<PC-katalog>\t0\odbior\paczka_0.3.1` (rozpakowana przez T0 - istniala przed startem T12), paczka 0.3.2 rozpakowana do
`<PC-katalog>\t0\odbior_t12\paczka_0.3.2`. Instrukcja: `instrukcje\instalacja_i_aktualizacja.md` (punkty 2, 3, 4).

## Kryterium (plan etapu, sekcja 7): wersja N -> N+1 -> powrot do N: jedno polecenie; ustawienia zachowane; baza zmigrowana z kopia

| Czesc kryterium | Werdykt | Liczby | Dowod |
|---|---|---|---|
| aktualizacja N -> N+1 jednym poleceniem | ZAL | 1 wywolanie `<P2>\zainstaluj.cmd /katalog <K> /python %PY% /bez-sieci /bez-pauzy`: kod 0, 60,4 s, `INSTALACJA: GOTOWA - wersja biezaca 0.3.2 (poprzednia: 0.3.1)`, `wersja_biezaca.txt` = 0.3.2 | `t12_zainstaluj_N1.log`, `t12_A2_baza_po_aktualizacji.txt` |
| powrot do N jednym poleceniem | ZAL | 1 wywolanie `<K>\Wroc_do_poprzedniej.cmd /bez-pauzy` z odpowiedzia `T`: kod 0, 2,6 s, `POWROT: GOTOWY - wersja biezaca 0.3.1 (poprzednia: 0.3.2)`; odpowiedz `N`: kod 11; brak odpowiedzi (wejscie NUL): kod 11 - w obu wersja bez zmian (0.3.2). Polecenie planu `/tak /bez-pauzy` (dodatkowy cykl): kod 0, 3,3 s | `t12_wroc.log`, `t12_wroc_tak.log` |
| program dziala po aktualizacji i po powrocie | ZAL | `Samokontrola.cmd --bez-sieci`: kod 0 i ZIELONA (ok 18, ostrzezenia 3) - 3 z 3 (po 0.3.2, po powrocie, stan koncowy); `Stanowisko.cmd --zamknij-po 20`: kod 0 - 3 z 3; `Traceback` w logu programu: 0 | `t12_A3_*.log`, `t12_A5_*.log`, `t12_A6_*` |
| ustawienia zachowane | ZAL | SHA-256 `ustawienia.toml`: przed / po 0.3.2 / po powrocie / stan koncowy = 4 z 4 identyczne (1274f09de600273b69713fd327e1bfa1ba5fa76d098c3e6a50c114ab6da4d022); plan wymaga 3 z 3 | `t12_ustawienia_sumy.txt` |
| dane nietkniete (czesc A) | ZAL | skany 0 -> 0 -> 0 -> 0 (instalacja swieza); zdarzenia 2 -> 4 -> 6 -> 8 (po 2 na start programu, nic nie ubylo); `user_version` 1 caly czas; powrot nie zmienil pliku bazy (SHA-256 przed i po powrocie 72085474...d9050f41) | `t12_A1_baza_przed.txt`, `t12_A3_baza_po_starcie_N1.txt`, `t12_A5_baza_po_powrocie.txt`, `t12_A6_stan_koncowy.txt` |
| kopia bazy przy aktualizacji (czesc A, schemat bez zmian) | ZAL (sposob porownania: O2) | 1 plik `dane\kopie\stanowisko_przed_0.3.2_20261121_025311_v1.sqlite` "sprawdzona (quick_check ok)": 86016 B = baza; skrot tresci bez naglowka 3d7d9168...ef95d761 = baza sprzed aktualizacji; `user_version` 1 = 1; zdarzenia 2 = 2; SHA-256 calego pliku rozne (naglowek SQLite) | `t12_A2_baza_po_aktualizacji.txt` |
| baza zmigrowana z kopia (czesc B, paczka probna `0.3.9-migracja`, schemat 1 -> 2) | ZAL z odstepstwem O2 | kody 11 z 11 zgodne (10, 0, 0, 0, 0, 0, 8, 0, 0 + budowa 0, 0); kopia sprzed migracji: 1 plik, 86016 B i skrot bez naglowka = baza sprzed migracji; `user_version` 1 -> 2 -> 1; zdarzenia 4 -> 7 -> 4 (przepadly 3 wpisy wersji probnej); SHA-256 bazy po przywroceniu = SHA-256 kopii (ef6a2bc7...); baza zmigrowana odlozona w `dane\kopie` | `t12_migracja_B.md`, `t12_B_stany.txt`, `t12_B_uzup_stany.txt`, `t12_B_*.log` |

Wynik calego testu wg reguly planu ("Liczby kryterium" T12): **ZAL z odstepstwem O2** - migracje sprawdzono na paczce probnej, kopie
porownano bez 100-bajtowego naglowka SQLite, a powrot po migracji wymaga 2 polecen (kod 8, potem `/przywroc-kopie`).

## Czasy (pod obciazeniem - patrz "Co jeszcze liczylo")

| Polecenie | Kod | Czas |
|---|---|---|
| pierwsza instalacja 0.3.1 (`zainstaluj.cmd`, 73 pakiety z kol) | 10 | 51,2 s |
| druga instalacja 0.3.1 po uzupelnieniu ustawien | 0 | 3,1 s |
| aktualizacja do 0.3.2 | 0 | 60,4 s |
| powrot do 0.3.1 (odpowiedz `T`) | 0 | 2,6 s |
| powrot `/tak` (dodatkowy cykl: na 0.3.2 i z powrotem) | 0, 0 | 3,1 s i 3,3 s |
| czesc B: budowa paczki probnej / rozpakowanie | 0, 0 | 6,9 s / 4,5 s |
| czesc B: instalacja 0.3.1 w `<KB>` / aktualizacja paczka probna / powrot z przywroceniem kopii | 10, 0, 0 | 82,1 s / 78,7 s / 3,2 s |
| czesc B uzupelnienie: instalacja 0.3.1 w `K_B2` / aktualizacja paczka probna | 10, 0 | 81,0 s / 80,7 s |

Co jeszcze liczylo na PC (`<PC-katalog>\koordynator\log\ciezkie.log`): tor 1 - T0 (do 02:50:15), potem T1 (pelny pytest od 02:53:21);
tor 2 - T10 regresja silnika (02:52:26-03:06:49); tor 3 - T5 (koniec 03:03:56). Wolny RAM 68-78 GB z 96 GB.

## Kroki i dowody

- Czesc A krok po kroku (polecenia DOKLADNE, godziny, kody, liczby): `t12_kroki.md`. Kody wszystkich polecen: `kody.txt`
  (wiersze P*, A*); godziny: `czasy.txt`. Pliki polecen: `krok_P3.cmd`, `krok_A1.cmd`, `krok_A2.cmd`, `krok_A4.cmd`, `krok_B.cmd`.
- PELNE wyjscie konsoli (do dokumentu "pokaz G3"): instalacja `t12_P3_zainstaluj_N_1.log` (kod 10), `t12_P5_zainstaluj_N_2.log`
  (kod 0); aktualizacja `t12_zainstaluj_N1.log`; powrot `t12_wroc.log` (brak odpowiedzi, `N`, `T`), `t12_wroc_tak.log` (`/tak`);
  samokontrole `t12_A3_samokontrola_N1.log`, `t12_A5_samokontrola_N.log`, `t12_A6_samokontrola_koniec.log`; listy wersji
  `t12_wersje_przed_po.txt`; sumy ustawien `t12_ustawienia_sumy.txt`. Logi startow programu maja 0 bajtow (program nic nie pisze na
  konsole; kody w `kody.txt`).
- Czesc B: `t12_migracja_B.md`, `t12_B_paczka.txt`, `t12_B_2a.log` ... `t12_B_8.log`, `t12_B_stany.txt`; uzupelnienie c1:
  `krok_B_uzup.cmd`, `t12_B_uzup_*.log`, `t12_B_uzup_stany.txt`.
- Duze pliki robocze (poza dowodami): `robocze\` (drzewo_M, paczki\Stanowisko_0.3.9-migracja.zip, paczka_M, K_B, K_B2, wej) - ok. 6,2 GB.

## Odstepstwa

- **O2** (z `RAPORT.md`): jak w planie - migracja na paczce probnej; kopia porownana co do rozmiaru i skrotu bajtow od 100.; powrot
  po migracji 2 polecenia. Nowych odstepstw brak.

## Polecenia planu zmienione / potkniecia (wszystkie)

1. Krok 4 planu (`Wroc_do_poprzedniej.cmd /tak /bez-pauzy`): zlecenie koordynatora kazalo sprawdzic odpowiedzi na pytanie `[T/N]`
   - wykonano 3 wywolania bez `/tak`: wejscie NUL (kod 11), `echo N|` (kod 11), `echo T|` (kod 0 - to jest powrot oceniany jako
   "jedno polecenie"). Polecenie planu doslownie wykonano potem w dodatkowym cyklu 0.3.1 -> 0.3.2 -> 0.3.1 (kody 0, 0).
2. `<P1>`: uzyto `<PC-katalog>\t0\odbior\paczka_0.3.1` (wg "Ustalen koordynatora"; istniala) - wlasnej kopii nie rozpakowywano.
3. Czesc B: katalog roboczy `<ROB>\robocze` zamiast `<ROB>` (zasada 3 zlecenia wspolnego - bez baz i ZIP-ow w katalogu dowodow);
   `<KB>` = `<ROB>\robocze\K_B`. Instalator przyjal dluzsza sciezke bez uwag.
4. Czesc B, kontrola c1 (stan zaraz po kroku 4): w pliku `krok_B.cmd` 1 z 6 wywolan `call :stan` dalo blad cmd.exe "The system
   cannot find the batch label specified - stan" (blad pliku wykonawcy; kody programu bez wplywu). Stan po kroku 4 zmierzono w
   uzupelnieniu na drugiej instalacji `K_B2` (kody 10, 0, 0, 0, 0): baza bez zmian po aktualizacji - TAK.
5. Krok T0-2 "porownaj z wierszem w `SHA256SUMS_wydania.txt`": w `<REPO>` (571e186) plik `Ramki/etap3/wydania/SHA256SUMS_wydania.txt`
   nie ma wiersza 0.3.1 ani 0.3.2 (0 trafien) - sumy ZIP porownano z plikami `.sha256` i ze zleceniem. To sprawa T0 / koordynatora
   (wiersz dopisano w commicie pozniejszym niz commit paczki), nie wynik T12.

## Obserwacje (nie zmieniaja wyniku)

- Dodatkowy cykl `Wroc_do_poprzedniej.cmd /tak` przy niezmienionym schemacie NIE zaklada kolejnej kopii bazy (w `dane\kopie` nadal
  1 plik) - pulapka planu "+1 plik" dotyczy powrotu do wersji o nowszym schemacie.
- W czesci B program wersji probnej zalozyl przy migracji wlasna kopie bazy obok bazy (`dane\stanowisko.kopia_v1_<data>.sqlite`) i to
  ja przywrocil powrot z `/przywroc-kopie`; szczegoly: `t12_migracja_B.md`, "Zmiany wobec planu i obserwacje" p. 3.
- Powrot po migracji wypisuje PRZED zgoda, ile wpisow przepadnie ("3 wpisow w 1 tabelach ... tabela zdarzenia: 4 w kopii, 7 teraz (+3)").

## Do decyzji koordynatora / wlasciciela

1. (wlasciciel, O2) Czy powrot po migracji bazy w 2 poleceniach (kod 8, potem `/przywroc-kopie`, z utrata wpisow zrobionych po
   aktualizacji - tu 3) jest do przyjecia. Zachowanie zamierzone programu.
2. (koordynator) Krok 4: ocena "jedno polecenie" oparta na powrocie z odpowiedzia `T` (wg zlecenia); `/tak` z planu tez kod 0.

## Stan instalacji po tescie (zostawione, nic nie skasowano)

- `<PC-katalog>\t0\odbior_t12\Stanowisko`: wersja biezaca **0.3.1**, poprzednia 0.3.2 (obie w `wersje\`); `ustawienia.toml` SHA-256
  1274f09d...6da4d022 (foldery `<PC-katalog>/t0/odbior_t12/dane/...`, `operatorzy = ["Technik A"]`); baza `dane\stanowisko.sqlite`:
  skany 0, zdarzenia 8, `user_version` 1; `dane\kopie`: 1 plik (`stanowisko_przed_0.3.2_20261121_025311_v1.sqlite`); razem z paczka
  0.3.2 i folderami wejsciowymi ok. 3,1 GB w `<PC-katalog>\t0\odbior_t12\`.
- Po T12 z tej instalacji uruchamiano proby B2 i B3 testu T7 (program z WLASNYM plikiem ustawien w katalogu T7) - danych T12 nie
  dotykaja. Kontrola koncowa po T7 (03:35:14): wersja biezaca 0.3.1, poprzednia 0.3.2; suma `ustawienia.toml` 1274f09d...6da4d022
  (bez zmian); zdarzenia 8, skany 0 (bez zmian); `dane\kopie` 1 plik; folder eksportu instalacji pusty; 0 procesow `python` ze
  sciezka `odbior_t12`.
- `<PC-katalog>\koordynator\robocze\odbior\T12\robocze\K_B`: 0.3.1 biezaca, 0.3.9-migracja poprzednia (po czesci B nie nadaje sie
  do innych testow); `K_B2`: 0.3.9-migracja biezaca, baza niezmigrowana. Sprzata koordynator.
- Procesy: po kazdym kroku `Get-Process python` - zadnych procesow ze sciezka `odbior_t12` ani `T12\robocze`.
