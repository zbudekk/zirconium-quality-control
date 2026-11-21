@echo off
rem T12: (1) dodatkowy cykl z poleceniem planu "Wroc_do_poprzedniej.cmd /tak /bez-pauzy" na instalacji czesci A; (2) czesc B w calosci
set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe
set QT_QPA_PLATFORM=offscreen
set ROB=<PC-katalog>\koordynator\robocze\odbior\T12
set RB=%ROB%\robocze
set K=<PC-katalog>\t0\odbior_t12\Stanowisko
set KB=%RB%\K_B
set PM=%RB%\paczka_M
set P1=<PC-katalog>\t0\odbior\paczka_0.3.1
set REPO=<PC-katalog>\t0\repo
set ODB=%REPO%\Ramki\etap3\odbior_koncowy
set SQL=%PY% -I %ODB%\narzedzia\sql_odczyt.py --baza
set SKROT=%PY% -I -c "import hashlib,sys;d=open(sys.argv[1],'rb').read();print(len(d),hashlib.sha256(d[100:]).hexdigest())"

rem ---------- (1) dodatkowy cykl /tak na instalacji czesci A
set L=%ROB%\t12_wroc_tak.log
echo ===== 4d: Wroc_do_poprzedniej.cmd /tak /bez-pauzy (0.3.1 - 0.3.2) %date% %time% > %L%
call %K%\Wroc_do_poprzedniej.cmd /tak /bez-pauzy < NUL >> %L% 2>&1
echo A4d_wroc_tak_do_N1 KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo wersja_biezaca po 4d: >> %L%
type %K%\wersja_biezaca.txt >> %L%
echo ===== 4e: Wroc_do_poprzedniej.cmd /tak /bez-pauzy (0.3.2 - 0.3.1; polecenie planu, krok 4) %date% %time% >> %L%
echo A4e_wroc_tak START %date% %time% >> %ROB%\czasy.txt
call %K%\Wroc_do_poprzedniej.cmd /tak /bez-pauzy < NUL >> %L% 2>&1
echo A4e_wroc_tak_do_N KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo A4e_wroc_tak KONIEC %date% %time% >> %ROB%\czasy.txt
echo wersja_biezaca po 4e: >> %L%
type %K%\wersja_biezaca.txt >> %L%
echo wersja_poprzednia po 4e: >> %L%
type %K%\wersja_poprzednia.txt >> %L%
call %K%\Samokontrola.cmd --bez-sieci < NUL > %ROB%\t12_A6_samokontrola_koniec.log 2>&1
echo A6_samokontrola_koniec KOD=%ERRORLEVEL% >> %ROB%\kody.txt
call %K%\Stanowisko.cmd --zamknij-po 20 < NUL > %ROB%\t12_A6_start_koniec.log 2>&1
echo A6_start_koniec KOD=%ERRORLEVEL% >> %ROB%\kody.txt
set W=%ROB%\t12_A6_stan_koncowy.txt
echo == stan KONCOWY instalacji czesci A: %date% %time% > %W%
certutil -hashfile %K%\ustawienia.toml SHA256 >> %W% 2>&1
call %K%\Wersje.cmd /bez-pauzy < NUL >> %W% 2>&1
%SQL% %K%\dane\stanowisko.sqlite "SELECT count(*) FROM skany" >> %W% 2>&1
%SQL% %K%\dane\stanowisko.sqlite "SELECT count(*) FROM zdarzenia" >> %W% 2>&1
%SQL% %K%\dane\stanowisko.sqlite "SELECT user_version FROM pragma_user_version" >> %W% 2>&1
echo pliki w dane\kopie: >> %W%
dir /b %K%\dane\kopie >> %W% 2>&1
echo wiersze Traceback w dane\logi\stanowisko.log: >> %W%
find /c "Traceback" %K%\dane\logi\stanowisko.log >> %W% 2>&1

rem ---------- (2) czesc B
set S=%ROB%\t12_B_stany.txt
echo == czesc B: stany bazy K_B > %S%
echo B1_budowa START %date% %time% >> %ROB%\czasy.txt
%PY% -I %ODB%\narzedzia\t12_paczka_migracja.py --repo %REPO% --roboczy %RB% --wersja 0.3.9-migracja --wyjscie %RB%\paczki --kola <PC-katalog>\wydania\kola > %ROB%\t12_B_paczka.txt 2>&1
echo B1_budowa_paczki KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo B1_budowa KONIEC %date% %time% >> %ROB%\czasy.txt
powershell -NoProfile -Command "Expand-Archive -LiteralPath %RB%\paczki\Stanowisko_0.3.9-migracja.zip -DestinationPath %PM%" >> %ROB%\t12_B_paczka.txt 2>&1
echo B1_rozpakowanie KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo B1_rozpakowanie KONIEC %date% %time% >> %ROB%\czasy.txt
if not exist %PM%\zainstaluj.cmd exit /b 2

echo B2a_zainstaluj START %date% %time% >> %ROB%\czasy.txt
call %P1%\zainstaluj.cmd /katalog %KB% /python %PY% /bez-sieci /bez-pauzy < NUL > %ROB%\t12_B_2a.log 2>&1
echo B2a_zainstaluj_N_1 KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo B2a_zainstaluj KONIEC %date% %time% >> %ROB%\czasy.txt
powershell -NoProfile -ExecutionPolicy Bypass -File %RB%\edytuj_KB.ps1 >> %S% 2>&1
echo B2_edycja_ustawien KOD=%ERRORLEVEL% >> %ROB%\kody.txt
call %P1%\zainstaluj.cmd /katalog %KB% /python %PY% /bez-sieci /bez-pauzy < NUL > %ROB%\t12_B_2b.log 2>&1
echo B2b_zainstaluj_N_2 KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo B2b_zainstaluj KONIEC %date% %time% >> %ROB%\czasy.txt

call %KB%\Stanowisko.cmd --zamknij-po 5 < NUL > %ROB%\t12_B_3a.log 2>&1
echo B3a_start KOD=%ERRORLEVEL% >> %ROB%\kody.txt
call %KB%\Stanowisko.cmd --zamknij-po 5 < NUL > %ROB%\t12_B_3b.log 2>&1
echo B3b_start KOD=%ERRORLEVEL% >> %ROB%\kody.txt
call :stan "po kroku 3 (PRZED aktualizacja probna)"

echo B4_zainstaluj_M START %date% %time% >> %ROB%\czasy.txt
call %PM%\zainstaluj.cmd /katalog %KB% /python %PY% /bez-sieci /bez-pauzy < NUL > %ROB%\t12_B_4.log 2>&1
echo B4_zainstaluj_M KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo B4_zainstaluj_M KONIEC %date% %time% >> %ROB%\czasy.txt
call :stan "po kroku 4 (c1: po aktualizacji, przed startem wersji probnej)"

call %KB%\Stanowisko.cmd --zamknij-po 5 < NUL > %ROB%\t12_B_5.log 2>&1
echo B5_start_M KOD=%ERRORLEVEL% >> %ROB%\kody.txt
call :stan "po kroku 5 (c2: po pierwszym starcie wersji probnej)"

call %KB%\Wroc_do_poprzedniej.cmd /tak /bez-pauzy < NUL > %ROB%\t12_B_6.log 2>&1
echo B6_wroc_tak KOD=%ERRORLEVEL% >> %ROB%\kody.txt
call :stan "po kroku 6 (powrot bez zgody - oczekiwany kod 8)"

echo B7_wroc_przywroc START %date% %time% >> %ROB%\czasy.txt
call %KB%\Wroc_do_poprzedniej.cmd /przywroc-kopie /bez-pauzy < NUL > %ROB%\t12_B_7.log 2>&1
echo B7_wroc_przywroc_kopie KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo B7_wroc_przywroc KONIEC %date% %time% >> %ROB%\czasy.txt
call :stan "po kroku 7 (e: po powrocie z przywroceniem kopii)"

call %KB%\Stanowisko.cmd --zamknij-po 5 < NUL > %ROB%\t12_B_8.log 2>&1
echo B8_start_N KOD=%ERRORLEVEL% >> %ROB%\kody.txt
call :stan "po kroku 8 (start wersji N na przywroconej bazie)"
call %KB%\Wersje.cmd /bez-pauzy < NUL >> %S% 2>&1
echo B_KONIEC %date% %time% >> %ROB%\czasy.txt
exit /b 0

:stan
echo. >> %S%
echo ===== STAN %~1 %date% %time% >> %S%
echo wersja_biezaca: >> %S%
type %KB%\wersja_biezaca.txt >> %S%
echo -- baza dane\stanowisko.sqlite (SHA-256; rozmiar i skrot bez naglowka; user_version; zdarzenia; skany): >> %S%
certutil -hashfile %KB%\dane\stanowisko.sqlite SHA256 | findstr /v /c:"CertUtil" /c:"SHA256 hash" >> %S% 2>&1
%SKROT% %KB%\dane\stanowisko.sqlite >> %S% 2>&1
%SQL% %KB%\dane\stanowisko.sqlite "SELECT user_version FROM pragma_user_version" >> %S% 2>&1
%SQL% %KB%\dane\stanowisko.sqlite "SELECT count(*) FROM zdarzenia" >> %S% 2>&1
%SQL% %KB%\dane\stanowisko.sqlite "SELECT count(*) FROM skany" >> %S% 2>&1
echo -- pliki w dane\kopie: >> %S%
dir /b %KB%\dane\kopie >> %S% 2>&1
for %%F in (%KB%\dane\kopie\*.sqlite) do (
  echo -- kopia %%~nxF rozmiar %%~zF >> %S%
  certutil -hashfile %%F SHA256 | findstr /v /c:"CertUtil" /c:"SHA256 hash" >> %S% 2>&1
  %SKROT% %%F >> %S% 2>&1
  %SQL% %%F "SELECT user_version FROM pragma_user_version" >> %S% 2>&1
  %SQL% %%F "SELECT count(*) FROM zdarzenia" >> %S% 2>&1
)
exit /b 0
