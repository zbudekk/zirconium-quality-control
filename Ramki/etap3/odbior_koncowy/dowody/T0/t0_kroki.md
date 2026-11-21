# T0 - kroki (21.11.2026, PC, konto <konto-PC>)

Oznaczenia: `PY` = `<PC>\AppData\Local\Programs\Python\Python312\python.exe`, `<ZIP>` = `<PC-katalog>\wydania\Stanowisko_0.3.1.zip`,
`<P1>` = `<PC-katalog>\t0\odbior\paczka_0.3.1`, `<K>` = `<PC-katalog>\t0\odbior\Stanowisko`, `<ROB>` = `<PC-katalog>\koordynator\robocze\odbior\T0`.
Kody krokow 3-9 pochodza z plikow `.cmd` (`echo ... KOD=%ERRORLEVEL%` w osobnym wierszu po `call`) - plik `kody.txt`.

| Krok | Godzina | Polecenie | Kod | Czas | Wynik | Dowod |
|---|---|---|---|---|---|---|
| 1 | 02:47:43 | `<PC-katalog>\koordynator\narz\ram.cmd` | 0 | <1 s | 78599 MB wolne z 95652 | `t0_1.log` |
| 2a | 02:47:43 | `certutil -hashfile <ZIP> SHA256` | 0 ("completed successfully") | ok. 2 s | f5affa81...4eec8 = `.zip.sha256` = zlecenie = `SHA256SUMS_wydania.txt` (main c399482); 1 z 1 | `t0_2.log`, `t0_sha256.txt` |
| 2b proba 1 | 02:47:53 | `powershell -NoProfile -Command "Expand-Archive -LiteralPath <ZIP> -DestinationPath <P1>"` (z sesji wykonawcy: PowerShell 7 jako proces nadrzedny) | blad polecenia | 0,9 s | NIE ZADZIALALO: `Cannot find an overload for "ExtractToDirectory" and the argument count: "3"`; 0 plikow (pusty katalog `<P1>`) | `t0_2b.log` |
| 2b proba 2 | 02:48:09 | `set PSModulePath=& powershell -NoProfile -Command "Expand-Archive -LiteralPath <ZIP> -DestinationPath <P1>"` | bez bledu | 2,9 s | rozpakowane 211 plikow, 462922182 bajtow (`kola`, `kola_testy`, `program`, `CZYTAJ.txt`, `SHA256SUMS`, `wydanie.json`, `zainstaluj.cmd`) | `t0_2b_proba2.log` |
| 3 | 02:48:30 | przez `ciezki.ps1 -Tor 1 -Kto odb-T0` plik `krok_3.cmd`: `call <P1>\zainstaluj.cmd /katalog <K> /python %PY% /bez-sieci /bez-pauzy < NUL > <ROB>\t0_zainstaluj_1.log 2>&1` | **10** | 65,5 s | sumy "zgodne 210 z 210"; program 131 plikow; pakiety "73 z 73"; samokontrola CZERWONA (ok 11, ostrzezenia 8, bledy 2: `folder_skanera`, `folder_cyrkon`); `INSTALACJA: WSTRZYMANA - uzupelnij ustawienia.toml i uruchom zainstaluj.cmd ponownie (kod 10)` | `t0_zainstaluj_1.log`, `t0_3_czas.txt` |
| 4 | 02:49:57 | zalozenie `<PC-katalog>\t0\odbior\dane\{eksport,Prywatne,millbox}`; `robocopy <PC-katalog>\app\Prace_test <PC-katalog>\t0\odbior\dane\Cyrkon /E /NFL /NDL /NJH /NP`; edycja `<K>\ustawienia.toml` (5 wierszy: 4 foldery w `[sciezki]`, `[sesja] operatorzy = ["Technik A"]`; UTF-8 bez BOM, konce linii jak we wzorze) | robocopy: 17 z 17 plikow, 0 FAILED | <1 s | Cyrkon: 15 folderow, 17 STL; `eksport`, `Prywatne`, `millbox` puste | `t0_4_robocopy.log`, `t0_4_ustawienia_zmiany.txt` |
| 5 | 02:50:12 | przez `ciezki.ps1 -Tor 1 -Kto odb-T0` plik `krok_5.cmd`: to samo polecenie co krok 3, log `t0_zainstaluj_2.log` | **0** | 3,3 s | "wersja 0.3.1 jest juz zainstalowana i zgodna z paczka - pliki bez zmian"; `SAMOKONTROLA: ZIELONA (ok 17, ostrzezenia 4)`; `INSTALACJA: GOTOWA - wersja biezaca 0.3.1 (poprzednia: brak)` | `t0_zainstaluj_2.log`, `t0_5_czas.txt` |
| 6a | 02:50:40 | `call <K>\Samokontrola.cmd --bez-sieci < NUL > <ROB>\t0_samokontrola.txt 2>&1` | **0** | 2,0 s | `SAMOKONTROLA: ZIELONA (ok 17, ostrzezenia 4)`; wierszy `BLAD`: 0; ostrzezenia: `baza` (powstanie przy pierwszym starcie), `ramka_wieczorna`, `ramka_poranna` (pominiete), `excel` | `t0_samokontrola.txt` |
| 6b | 02:50:42 | `call <K>\Samokontrola.cmd --json < NUL > <ROB>\t0_samokontrola.json` (stderr osobno: pusty) | **0** | 4,7 s (wg JSON 4,3 s) | pelna samokontrola z proba polaczenia z ramkami: `kod_wyjscia` 0, ok 17, ostrzezenia 4, bledy 0, 21 sprawdzen, "SAMOKONTROLA: ZIELONA (ok 17, ostrzezenia 4)"; ramki nieobecne (`gaierror`) = ostrzezenie | `t0_samokontrola.json` |
| 7a | 02:50:47 | `set QT_QPA_PLATFORM=offscreen`; `call <K>\Stanowisko.cmd --atrapa --zamknij-po 5 < NUL` | **0** | 6,5 s | start i samodzielne zamkniecie; konsola: 0 wierszy | `t0_start.txt` |
| 7b | 02:50:54 | `call <K>\Stanowisko.cmd --zamknij-po 20 < NUL` (prawdziwy kontroler) | **0** | 22,5 s | start i samodzielne zamkniecie; konsola: 0 wierszy; powstala baza `dane\stanowisko.sqlite` (86016 B); log programu 7 wierszy: "start, zadan wznowionych 0, plikow znanych 0" ... "zamkniete, zadan niezakonczonych 0" | `t0_start.txt` |
| 7c | 02:51:16 | `find /c "Traceback" <K>\dane\logi\stanowisko.log` | 1 (= 0 trafien) | <1 s | **0** wierszy `Traceback` | `t0_start.txt` |
| 8 | 02:51:16 | `call <K>\Polecenie.cmd -c "import stanowisko, sys; print(sys.modules.get('_wmi', 'brak'))" < NUL` | 0 | <1 s | `None` | `t0_8.log` |
| 9a | 02:51:17 | `findstr /c:"Ignoring indexes" /c:"Looking in links" <K>\wersje\0.3.1\pip.log` | 0 | <1 s | **2 wiersze**: `Ignoring indexes: https://pypi.org/simple`, `Looking in links: <PC-katalog>\t0\odbior\paczka_0.3.1\kola` | `t0_pip_bez_sieci.txt` |
| 9b | 02:51:17 | `findstr /c:"bez sieci" <K>\dziennik_instalacji.txt` | 0 | <1 s | 1 wiersz: "instalacja 73 pakietow z kol paczki (bez sieci) - to trwa kilka minut..." | `t0_pip_bez_sieci.txt` |
| 9c (dodatkowo) | 02:51:47 | zliczenie w `pip.log`: wiersze z `http://` / `https://` oraz z `Downloading` | - | <1 s | adresy: 1 wiersz (ten sam `Ignoring indexes`); `Downloading`: 0 wierszy | - |

Po kroku 9 wykonany krok 1 z T1 (`/testy`, kod 0, 6,2 s, pakiety 76 z 76, samokontrola ZIELONA ok 18 / ostrzezenia 3) i krok 3 z T1
(`_wmi` -> `None`) - dowody w `..\T1\t1_zainstaluj_testy.log`, `..\T1\t1_3_wmi.log`; o 02:51:47 zapisany `GOTOWE.txt`.

Procesy po krokach: `powershell Get-Process python` - wlasnych procesow brak (zostal PID 12012 z 01:37 - znany, niczyj - i procesy innych
wykonawcow: `t0\odbior_t12\...` = T12).
