@echo off
rem T12 na wydaniu 0.3.3: przygotowanie (T0 kroki 2-5 i 7 w odbior2_t12) + czesc A (0.3.3 - 0.3.4-t12 - powrot)
set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe
set QT_QPA_PLATFORM=offscreen
set ROB=<PC-katalog>\koordynator\robocze\odbior2\final\T12
set T=<PC-katalog>\t0\odbior2_t12
set K=%T%\Stanowisko
set P1=%T%\paczka_0.3.3
set P2=%T%\paczka_0.3.4-t12
set ZIP1=<PC-katalog>\wydania\Stanowisko_0.3.3.zip
set ZIP2=<PC-katalog>\wydania\Stanowisko_0.3.4-t12.zip
set S=%ROB%\t12_A_stany.txt
echo A START %date% %time% >> %ROB%\czasy.txt

rem --- T0-2: sumy i rozpakowanie (tar.exe systemowy)
echo === certutil -hashfile %ZIP1% SHA256 > %ROB%\t12_sha256_zip.txt
certutil -hashfile %ZIP1% SHA256 >> %ROB%\t12_sha256_zip.txt 2>&1
echo P2_certutil_N KOD=%ERRORLEVEL% >> %ROB%\kody.txt
type %ZIP1%.sha256 >> %ROB%\t12_sha256_zip.txt 2>&1
echo === certutil -hashfile %ZIP2% SHA256 >> %ROB%\t12_sha256_zip.txt
certutil -hashfile %ZIP2% SHA256 >> %ROB%\t12_sha256_zip.txt 2>&1
echo P2_certutil_N1 KOD=%ERRORLEVEL% >> %ROB%\kody.txt
type %ZIP2%.sha256 >> %ROB%\t12_sha256_zip.txt 2>&1
mkdir %P1%
mkdir %P2%
mkdir %T%\dane\eksport
mkdir %T%\dane\Prywatne
mkdir %T%\dane\millbox
echo P2_tar_N START %date% %time% >> %ROB%\czasy.txt
C:\Windows\System32\tar.exe -xf %ZIP1% -C %P1% > %ROB%\t12_P2_tar.log 2>&1
echo P2_tar_N KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo P2_tar_N1 START %date% %time% >> %ROB%\czasy.txt
C:\Windows\System32\tar.exe -xf %ZIP2% -C %P2% >> %ROB%\t12_P2_tar.log 2>&1
echo P2_tar_N1 KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo P2_tar KONIEC %date% %time% >> %ROB%\czasy.txt
robocopy <PC-katalog>\app\Prace_test %T%\dane\Cyrkon /E /NFL /NDL /NJH /NP >> %ROB%\t12_P2_tar.log 2>&1
echo P2_robocopy_cyrkon KOD=%ERRORLEVEL% (1 = skopiowano) >> %ROB%\kody.txt
if not exist %P1%\zainstaluj.cmd exit /b 2
if not exist %P2%\zainstaluj.cmd exit /b 2

rem --- T0-3: pierwsza instalacja 0.3.3 (oczekiwany kod 10)
echo P3_zainstaluj_N_1 START %date% %time% >> %ROB%\czasy.txt
call %P1%\zainstaluj.cmd /katalog %K% /python %PY% /bez-sieci /bez-pauzy < NUL > %ROB%\t12_P3_zainstaluj_N_1.log 2>&1
set KOD=%ERRORLEVEL%
echo P3_zainstaluj_N_1 KOD=%KOD% >> %ROB%\kody.txt
echo P3_zainstaluj_N_1 KONIEC %date% %time% >> %ROB%\czasy.txt
if not "%KOD%"=="10" exit /b 3
copy /y %K%\ustawienia.toml %ROB%\robocze\ustawienia_po_pierwszej_instalacji.toml > NUL

rem --- T0-4: foldery i operatorzy
powershell -NoProfile -ExecutionPolicy Bypass -File %ROB%\edytuj.ps1 -Plik %K%\ustawienia.toml -Wej <PC-katalog>/t0/odbior2_t12/dane > %ROB%\t12_P4_edycja.log 2>&1
set KOD=%ERRORLEVEL%
echo P4_edycja_ustawien KOD=%KOD% >> %ROB%\kody.txt
if not "%KOD%"=="0" exit /b 4

rem --- T0-5: druga instalacja (oczekiwany kod 0)
echo P5_zainstaluj_N_2 START %date% %time% >> %ROB%\czasy.txt
call %P1%\zainstaluj.cmd /katalog %K% /python %PY% /bez-sieci /bez-pauzy < NUL > %ROB%\t12_P5_zainstaluj_N_2.log 2>&1
set KOD=%ERRORLEVEL%
echo P5_zainstaluj_N_2 KOD=%KOD% >> %ROB%\kody.txt
echo P5_zainstaluj_N_2 KONIEC %date% %time% >> %ROB%\czasy.txt
if not "%KOD%"=="0" exit /b 5

rem --- T0-7: starty programu
echo P7a_start_atrapa START %date% %time% >> %ROB%\czasy.txt
call %K%\Stanowisko.cmd --atrapa --zamknij-po 5 < NUL > %ROB%\t12_P7a_start_atrapa.log 2>&1
echo P7a_start_atrapa KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo P7b_start START %date% %time% >> %ROB%\czasy.txt
call %K%\Stanowisko.cmd --zamknij-po 20 < NUL > %ROB%\t12_P7b_start.log 2>&1
echo P7b_start KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo P7b_start KONIEC %date% %time% >> %ROB%\czasy.txt

rem --- T12 krok 1: stan przed aktualizacja
certutil -hashfile %K%\ustawienia.toml SHA256 > %ROB%\t12_ustawienia_przed.txt 2>&1
echo A1_certutil_ustawienia KOD=%ERRORLEVEL% >> %ROB%\kody.txt
call %K%\Wersje.cmd /bez-pauzy < NUL > %ROB%\t12_A1_wersje_przed.log 2>&1
echo A1_wersje KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo == czesc A: stany instalacji %K% > %S%
call %ROB%\stan.cmd %K% %S% "krok 1 (PRZED aktualizacja, po 1 starcie programu 0.3.3)"

rem --- T12 krok 2: aktualizacja JEDNYM poleceniem
echo A2_zainstaluj_N1 START %date% %time% >> %ROB%\czasy.txt
call %P2%\zainstaluj.cmd /katalog %K% /python %PY% /bez-sieci /bez-pauzy < NUL > %ROB%\t12_zainstaluj_N1.log 2>&1
set KOD=%ERRORLEVEL%
echo A2_zainstaluj_N1 KOD=%KOD% >> %ROB%\kody.txt
echo A2_zainstaluj_N1 KONIEC %date% %time% >> %ROB%\czasy.txt
call %ROB%\stan.cmd %K% %S% "krok 2 (PO aktualizacji, PRZED pierwszym startem 0.3.4-t12)"
if not "%KOD%"=="0" exit /b 6

rem --- T12 krok 3
echo A3_samokontrola START %date% %time% >> %ROB%\czasy.txt
call %K%\Samokontrola.cmd --bez-sieci < NUL > %ROB%\t12_A3_samokontrola_N1.log 2>&1
echo A3_samokontrola_N1 KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo A3_start START %date% %time% >> %ROB%\czasy.txt
call %K%\Stanowisko.cmd --zamknij-po 20 < NUL > %ROB%\t12_A3_start_N1.log 2>&1
echo A3_start_N1 KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo A3_start KONIEC %date% %time% >> %ROB%\czasy.txt
certutil -hashfile %K%\ustawienia.toml SHA256 > %ROB%\t12_ustawienia_po_N1.txt 2>&1
call %K%\Wersje.cmd /bez-pauzy < NUL > %ROB%\t12_A3_wersje_po_N1.log 2>&1
echo A3_wersje KOD=%ERRORLEVEL% >> %ROB%\kody.txt
call %ROB%\stan.cmd %K% %S% "krok 3 (PO starcie programu 0.3.4-t12)"

rem --- T12 krok 4: powrot JEDNYM poleceniem (polecenie planu doslownie)
echo ===== krok 4: Wroc_do_poprzedniej.cmd /tak /bez-pauzy %date% %time% > %ROB%\t12_wroc.log
echo A4_wroc_tak START %date% %time% >> %ROB%\czasy.txt
call %K%\Wroc_do_poprzedniej.cmd /tak /bez-pauzy < NUL >> %ROB%\t12_wroc.log 2>&1
set KOD=%ERRORLEVEL%
echo A4_wroc_tak KOD=%KOD% >> %ROB%\kody.txt
echo A4_wroc_tak KONIEC %date% %time% >> %ROB%\czasy.txt
call %ROB%\stan.cmd %K% %S% "krok 4 (PO powrocie, PRZED startem 0.3.3)"

rem --- T12 krok 5
call %K%\Samokontrola.cmd --bez-sieci < NUL > %ROB%\t12_A5_samokontrola_N.log 2>&1
echo A5_samokontrola_N KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo A5_start START %date% %time% >> %ROB%\czasy.txt
call %K%\Stanowisko.cmd --zamknij-po 20 < NUL > %ROB%\t12_A5_start_N.log 2>&1
echo A5_start_N KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo A5_start KONIEC %date% %time% >> %ROB%\czasy.txt
certutil -hashfile %K%\ustawienia.toml SHA256 > %ROB%\t12_ustawienia_po_powrocie.txt 2>&1
call %K%\Wersje.cmd /bez-pauzy < NUL > %ROB%\t12_A5_wersje_po_powrocie.log 2>&1
echo A5_wersje KOD=%ERRORLEVEL% >> %ROB%\kody.txt
call %ROB%\stan.cmd %K% %S% "krok 5 (PO starcie 0.3.3 po powrocie = stan koncowy)"
echo wiersze Traceback w dane\logi\stanowisko.log: >> %S%
find /c "Traceback" %K%\dane\logi\stanowisko.log >> %S% 2>&1
echo A KONIEC %date% %time% >> %ROB%\czasy.txt
exit /b 0
