WERDYKT T0: ZAL z odstepstwem O1 (program startuje 2 z 2, samokontrola ZIELONA kod 0 / bledy 0, sumy 1 z 1 + 210 z 210, pip tylko z kol paczki)

# T0 - Czysta instalacja z paczki wydania 0.3.1 - WYNIK

Wykonawca: sesja testow koncowych (tor 1), PC, konto `<konto-PC>`, 21.11.2026 02:47-02:52. Przedmiot: paczka
`<PC-katalog>\wydania\Stanowisko_0.3.1.zip` (444935199 bajtow, commit 571e186cb8178209da670dde244dfc56bba5e300).
Plan: `<REPO>\Ramki\etap3\odbior_koncowy\PLAN_TESTOW.md`, sekcja "T0 - Czysta instalacja" + "Ustalenia koordynatora".
Instrukcja osoby instalujacej: `Ramki/stanowisko/instrukcje/instalacja_i_aktualizacja.md` (w paczce `program\instrukcje\`).

Katalogi: swiezy `<PC-katalog>\t0\odbior\` (przed testem nie istnial); `<P1>` = `<PC-katalog>\t0\odbior\paczka_0.3.1`;
`<K>` = `<PC-katalog>\t0\odbior\Stanowisko`; foldery wejsciowe `<PC-katalog>\t0\odbior\dane\{eksport,Cyrkon,Prywatne,millbox}`.

## Kryterium (sekcja 7 planu etapu)

"Paczka wydania na czystym koncie PC, wg instrukcji, bez internetu - program startuje; samokontrola zielona; sumy SHA-256 zgodne."

| Czesc kryterium | Liczba | Dowod | Werdykt |
|---|---|---|---|
| (a) program startuje | 2 z 2 startow z kodem 0: `Stanowisko.cmd --atrapa --zamknij-po 5` kod 0 (6,5 s); `Stanowisko.cmd --zamknij-po 20` (prawdziwy kontroler) kod 0 (22,5 s); `Traceback` w `dane\logi\stanowisko.log`: 0 wierszy (log: 7 wierszy, "start, zadan wznowionych 0" ... "zamkniete, zadan niezakonczonych 0") | `t0_start.txt`, `kody.txt` | ZAL |
| (b) samokontrola zielona | `Samokontrola.cmd --bez-sieci`: kod 0, `SAMOKONTROLA: ZIELONA (ok 17, ostrzezenia 4)`, bledy 0; pelna (`--json`, z proba polaczenia z ramkami): kod 0, ok 17 / ostrzezenia 4 / bledy 0, 21 sprawdzen | `t0_samokontrola.txt`, `t0_samokontrola.json` | ZAL |
| (c) sumy SHA-256 zgodne | ZIP: 1 z 1 (certutil = `.zip.sha256` = wartosc ze zlecenia = wiersz `SHA256SUMS_wydania.txt` z `main` c399482); pliki paczki wg instalatora: "zgodne 210 z 210" (obie instalacje); pliki programu wg samokontroli: 130 z 130, nadmiarowych 0 | `t0_sha256.txt`, `t0_2.log`, `t0_zainstaluj_1.log`, `t0_zainstaluj_2.log` | ZAL |
| (d) "bez internetu" (odstepstwo O1) | `pip.log`: 2 wiersze z 2 (`Ignoring indexes: https://pypi.org/simple`, `Looking in links: <PC-katalog>\t0\odbior\paczka_0.3.1\kola`); dziennik instalacji: wiersz "instalacja 73 pakietow z kol paczki (bez sieci)"; pakiety "73 z 73"; dodatkowo w `pip.log` 0 wierszy `Downloading` i 1 wiersz z adresem (ten sam `Ignoring indexes`) | `t0_pip_bez_sieci.txt` | ZAL z odstepstwem O1 |
| "czyste konto PC" (odstepstwo O1) | swiezy katalog na koncie `<konto-PC>`, nie nowe konto Windows; sieci fizycznie nie odcinano | ten plik | ZAL z odstepstwem O1 |
| "wg instrukcji" | przebieg zgodny z instrukcja p. 2: 9 krokow, pierwsza instalacja kod 10 `WSTRZYMANA`, po uzupelnieniu `ustawienia.toml` kod 0 `GOTOWA`; komunikaty jak w instrukcji (tabela nizej) | `t0_zainstaluj_1.log`, `t0_zainstaluj_2.log` | ZAL |

Calosc: **ZAL z odstepstwem O1** (O1 = przyjeta interpretacja "czystego konta" i "bez internetu" z `RAPORT.md` 4a; nowych odstepstw brak).
Pelne T0 na czystym komputerze (laptop stanowiska) = poza tym testem (`ODLOZONE.md`, D4).

## Kody i czasy instalacji

| Instalacja | Godzina | Kod | Czas | Wiersz koncowy |
|---|---|---|---|---|
| pierwsza (krok 3) | 02:48:30 | 10 | 65,5 s | `INSTALACJA: WSTRZYMANA - uzupelnij ustawienia.toml i uruchom zainstaluj.cmd ponownie (kod 10)` |
| po uzupelnieniu ustawien (krok 5) | 02:50:12 | 0 | 3,3 s | `INSTALACJA: GOTOWA - wersja biezaca 0.3.1 (poprzednia: brak). Uruchamianie: <PC-katalog>\t0\odbior\Stanowisko\Stanowisko.cmd` |
| z `/testy` (T1 krok 1, zaraz po T0) | 02:51:29 | 0 | 6,2 s | `INSTALACJA: GOTOWA - wersja biezaca 0.3.1 (poprzednia: brak). ...`; "zestaw testowy (pytest): 3 pakietow", "pakiety zgodne z lista zamrozona: 76 z 76" |

Czasy z `echo %time%` przed i po `call zainstaluj.cmd` (`t0_3_czas.txt`, `t0_5_czas.txt`, `..\T1\t1_1_czas.txt`); wpisy `ciezkie.log`:
`02:48:30 START odb-T0 tor 1 | RAM 78332 MB` / `02:49:35 KONIEC odb-T0 tor 1 | kod 10 | RAM 77652 MB`.
Proba generalna: 52,5 s / 5,8 s. Co jeszcze liczylo na PC w czasie kroku 3: rownolegla instalacja T12 (`t0\odbior_t12`, tor 4,
procesy `python` widoczne w `Get-Process` o 02:50) - inne ciezkie kroki nie (T10 wystartowal 02:52:26). Wolny RAM przed: 78599 MB z 95652.

Wiersz koncowy samokontroli: `SAMOKONTROLA: ZIELONA (ok 17, ostrzezenia 4)` (kod 0). Ostrzezenia (4): `baza` (brak pliku bazy przed
pierwszym startem - powstala w kroku 7b), `ramka_wieczorna`, `ramka_poranna` (bez ramek w sieci), `excel` (Excel nie jest uruchomiony).
Po kroku `/testy` (baza juz istnieje): `SAMOKONTROLA: ZIELONA (ok 18, ostrzezenia 3)`.

Pelna tabela krokow (polecenie / kod / czas / wynik): `t0_kroki.md`.

## Co widzi osoba instalujaca (material do "pokaz G3")

Pelne wyjscie konsoli kazdego polecenia jest w plikach dowodu (nic nie wycinano): `t0_2.log` (certutil), `t0_zainstaluj_1.log`,
`t0_zainstaluj_2.log`, `t0_samokontrola.txt`, `t0_samokontrola.json`, `t0_start.txt`, `t0_8.log`, `t0_pip_bez_sieci.txt`,
`..\T1\t1_zainstaluj_testy.log`. Skrot:

1. Rozpakowana paczka: `kola\` (73 pliki), `kola_testy\` (3), `program\`, `CZYTAJ.txt`, `SHA256SUMS`, `wydanie.json`, `zainstaluj.cmd`
   - razem 211 plikow, 462922182 bajtow. `CZYTAJ.txt` (7 wierszy): Python 3.12, "rozpakuj CALA paczke i uruchom zainstaluj.cmd (bez
   internetu)", wskazanie instrukcji, "zainstaluj.cmd sam liczy sumy z pliku SHA256SUMS; niezgodnosc zatrzymuje instalacje".
2. Pierwsze uruchomienie `zainstaluj.cmd` (65,5 s) - 7 z 9 krokow na ekranie:
   - `[1/9] Sumy SHA-256 paczki ... zgodne 210 z 210; wersja 0.3.1, commit 571e186cb817`
   - `[2/9] Python 3.12... <sciezka>: 3.12.10`
   - `[3/9] Katalog instalacji ... wersja biezaca: brak (pierwsza instalacja)`
   - `[4/9] Ustawienia... zalozono ustawienia.toml ze wzoru (sciezki danych: .../Stanowisko/dane/...) - UZUPELNIJ foldery pracy w
     [sciezki] i osoby w [sesja] operatorzy`; `baza: jeszcze jej nie ma; program 0.3.1 obsluguje schemat 1`
   - `[5/9] Katalog wersji 0.3.1... miejsce na dysku: potrzeba ok. 1860 MB, wolne 64580 MB`; `program: skopiowano 131 plikow, sumy
     zgodne`; `srodowisko wirtualne zalozone i startuje`; `instalacja 73 pakietow z kol paczki (bez sieci) - to trwa kilka minut...`
     (tu: 40 s wg znacznikow czasu `pip.log`: 02:48:51-02:49:31); `pakiety zgodne z lista zamrozona: 73 z 73`
   - `[6/9] Kopia bazy... bazy jeszcze nie ma - program zalozy ja przy pierwszym uruchomieniu`
   - `[7/9] Samokontrola wersji 0.3.1...` 21 wierszy `OK` / `OSTRZEZENIE` / `BLAD`; `SAMOKONTROLA: CZERWONA (ok 11, ostrzezenia 8, bledy 2)`
   - potem: "Wersja 0.3.1 jest zainstalowana, ale jeszcze NIE jest wersja biezaca - samokontrola wskazala, co uzupelnic:", 2 wiersze
     `BLAD folder_skanera: ...` i `BLAD folder_cyrkon: ...` (kazdy z rada: ktory klucz w ktorym pliku poprawic), `Plik ustawien: <K>\ustawienia.toml`,
     `CO ZROBIC: otworz plik ustawien w Notatniku, wpisz w [sciezki] foldery tej maszyny (z ukosnikami /) i osoby w [sesja] operatorzy,
     zapisz (UTF-8) i uruchom zainstaluj.cmd JESZCZE RAZ - pakiety nie instaluja sie drugi raz, to trwa kilka sekund.`
   - wiersz koncowy: `INSTALACJA: WSTRZYMANA - uzupelnij ustawienia.toml i uruchom zainstaluj.cmd ponownie (kod 10)`
   - w `<K>` po tym kroku: `dane\`, `wersje\`, `dziennik_instalacji.txt`, `instalator.blokada`, `ustawienia.toml` (jeszcze bez `Stanowisko.cmd`).
3. Uzupelnienie `ustawienia.toml`: 5 wierszy (wiersze 6-9 w `[sciezki]`, wiersz 99 `operatorzy`) - `t0_4_ustawienia_zmiany.txt`.
4. Drugie uruchomienie `zainstaluj.cmd` (3,3 s) - 9 z 9 krokow: `[4/9] istniejacy ustawienia.toml zostaje bez zmian (SHA-256 4303ec76c74fb4a2...)`,
   `[5/9] wersja 0.3.1 jest juz zainstalowana i zgodna z paczka - pliki bez zmian`, `[7/9] ... SAMOKONTROLA: ZIELONA (ok 17, ostrzezenia 4)`,
   `[8/9] Przelaczenie wersji biezacej... wersja biezaca: 0.3.1; poprzednia: brak`, `[9/9] Skrot na pulpicie... pominiety (opcja /skrot
   zaklada skrot Stanowisko na pulpicie)`, wiersz koncowy `INSTALACJA: GOTOWA - wersja biezaca 0.3.1 (poprzednia: brak). Uruchamianie:
   <PC-katalog>\t0\odbior\Stanowisko\Stanowisko.cmd`.
   - w `<K>` doszly: `Stanowisko.cmd`, `Samokontrola.cmd`, `Polecenie.cmd`, `Wersje.cmd`, `Wroc_do_poprzedniej.cmd`, `wersja_biezaca.txt`.
5. `Samokontrola.cmd --bez-sieci` (2,0 s): 21 wierszy, ostatni `SAMOKONTROLA: ZIELONA (ok 17, ostrzezenia 4)`.
6. `Stanowisko.cmd` (oba starty): w konsoli NIC sie nie wypisuje (0 wierszy) - program to okno; tu okno `offscreen` (sesja bez ekranu),
   zamkniecie samoczynne przez `--zamknij-po`. Po pierwszym prawdziwym starcie w `dane\`: `stanowisko.sqlite`, `logi\`, `pula_cache\`,
   `do_dofrezowania_biezaca.csv`, `ramki_laptop_id.txt`.

Zgodnosc z instrukcja (p. 2.3, 2.4, tabela 6): liczba krokow 9, kod 10 i tresc wiersza `WSTRZYMANA`, wiersze `BLAD ...` nad wierszem
koncowym z pelna sciezka pliku ustawien, "pakiety nie instaluja sie drugi raz, trwa to kilka sekund" (3,3 s) - zgodne. Roznic miedzy
instrukcja a ekranem nie stwierdzono. Czego T0 NIE sprawdza: dwuklik w Eksploratorze i pauza na koncu (uzyto `/bez-pauzy`), opcja `/skrot`,
samodzielne szukanie Pythona (na tym PC `/python` jest obowiazkowe - Python lezy w profilu innego konta), instalacja Pythona z python.org.

## Polecenia planu zmienione / potkniecia (to tez jest wynik)

1. Krok 2, rozpakowanie. Polecenie planu `powershell -NoProfile -Command "Expand-Archive -LiteralPath <ZIP_N> -DestinationPath ..."`
   uruchomione z sesji wykonawcy NIE zadzialalo: `Cannot find an overload for "ExtractToDirectory" and the argument count: "3"`
   (0 plikow, `t0_2b.log`). Komunikat wskazuje modul `C:\program files\powershell\7\Modules\Microsoft.PowerShell.Archive` - sesja wykonawcy
   to PowerShell 7 i przekazuje swoje `PSModulePath` do `powershell` 5.1. Zadzialalo: to samo polecenie poprzedzone `set PSModulePath=&`
   (2,9 s, 211 plikow, `t0_2b_proba2.log`). To wlasnosc sesji wykonawcy, nie paczki; w zwyklym oknie `cmd.exe` NIE sprawdzano
   (osoba instalujaca rozpakowuje Eksploratorem - tez nie sprawdzano w tym tescie).
2. Kroki 1, 2: wiersz `KOD=0` w `t0_1.log`, `t0_2.log`, `t0_2b.log`, `t0_2b_proba2.log`, `t0_4_robocopy.log` pochodzi z `echo KOD=%errorlevel%`
   w TEJ SAMEJ linii `cmd /c` co polecenie - `%errorlevel%` jest wtedy rozwijany przed wykonaniem i NIE jest kodem polecenia. Wynik tych
   krokow czytac z tresci wyjscia (certutil: "completed successfully"; robocopy: 17 z 17, FAILED 0). Od kroku 3 kody sa z plikow `.cmd`
   (`kody.txt`) i z `ciezki.ps1` (`ciezkie.log`) - wiarygodne.
3. Nazwy logow: instalacje pod nazwami z listy "Dowody" (`t0_zainstaluj_1.log`, `t0_zainstaluj_2.log`) zamiast `t0_3.log`, `t0_5.log`.
4. Krok 4: `robocopy ... /E` z dodatkowymi `/NFL /NDL /NJH /NP` (bez nazw folderow i plikow zlecen w dowodzie).
5. Krok 6: `Samokontrola.cmd --json` - stderr skierowany do osobnego pliku `t0_samokontrola_json_stderr.txt` (pusty), zeby nie zepsuc JSON.
6. Krok 7: liczba wierszy `Traceback` policzona `find /c "Traceback" <K>\dane\logi\stanowisko.log` (plan nie podaje polecenia).
7. Krok 9: wiersz dziennika znaleziony przez `findstr /c:"bez sieci" <K>\dziennik_instalacji.txt` (plan nie podaje polecenia).
8. Krok 2: w `<REPO>` (commit wydania 571e186) plik `SHA256SUMS_wydania.txt` NIE ma wiersza 0.3.1 - wiersz jest w `main` (c399482, po
   zbudowaniu paczki); porownanie wykonano z plikiem w `<PC-katalog>\qc` (tylko odczyt).

## Uwagi o srodowisku (opis, nie wynik testu)

- Sesja wykonawcy ma w srodowisku `PYTHONUTF8=1` i `PYTHONIOENCODING=utf-8:surrogateescape`; dziedzicza je wszystkie uruchomione polecenia.
  `zainstaluj.cmd` uruchamia Pythona z `-I` (zmienne `PYTHON*` pominiete) i sam ustawia `PYTHONUTF8=1`; `Stanowisko.cmd` / `Samokontrola.cmd` /
  `Polecenie.cmd` ida przez srodowisko wersji - zwykle okno `cmd.exe` osoby instalujacej nie ma `PYTHONIOENCODING`. Wplywu na wynik nie widac
  (wyjscie ASCII), ale nie bylo to mierzone osobno.
- Python bazowy na tym PC ma w `Lib\site-packages` pakiety programu (numpy, scipy, PySide6...). Srodowisko wersji jest od nich odciete:
  `<K>\wersje\0.3.1\venv\pyvenv.cfg`: `include-system-site-packages = false`; pip zainstalowal 73 pakiety z kol paczki ("73 z 73").
- Zjawisk `0xC0000142` / `0xc000070a` w T0 nie bylo.

## Do decyzji koordynatora / wlasciciela

- O1: "czyste konto" = swiezy katalog, siec nieodcieta - decyzja wlasciciela jak w `RAPORT.md` 4a (pelne T0 na laptopie stanowiska: D4).
- Plan, krok 2: polecenie `Expand-Archive` zawodzi z sesji PowerShell 7 (potkniecie 1) - do dopisania w planie (`set PSModulePath=` albo `tar -xf`).
- Plan, krok 2: `SHA256SUMS_wydania.txt` z `<REPO>` nie zawiera paczki koncowej (potkniecie 8) - plan powinien wskazac `main`.

## Stan po tescie

`<K>` = instalacja WSPOLNA dla T1-T11 (z pytest, 76 pakietow); znak gotowosci `GOTOWE.txt` zapisany 02:51:47. Po `GOTOWE.txt` wykonawca T0
niczego w `<K>` nie zmienia. Wlasnych procesow `python` nie zostawiono.
