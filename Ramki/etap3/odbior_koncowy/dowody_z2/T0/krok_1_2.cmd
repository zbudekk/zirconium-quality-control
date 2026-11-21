@echo off
rem T0 kroki 1-2: wolny RAM, suma SHA-256 paczki 0.3.3, rozpakowanie (tar.exe systemowy)
set ROB=<PC-katalog>\koordynator\robocze\odbior2\final\T0
set ZIP=<PC-katalog>\wydania\Stanowisko_0.3.3.zip
set P1=<PC-katalog>\t0\odbior2\paczka_0.3.3
echo %date% %time% > %ROB%\t0_1.log
call <PC-katalog>\koordynator\narz\ram.cmd >> %ROB%\t0_1.log 2>&1
echo krok1_ram KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo === certutil -hashfile %ZIP% SHA256 > %ROB%\t0_2.log
certutil -hashfile %ZIP% SHA256 >> %ROB%\t0_2.log 2>&1
echo krok2a_certutil KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo === type %ZIP%.sha256 >> %ROB%\t0_2.log
type %ZIP%.sha256 >> %ROB%\t0_2.log 2>&1
echo === findstr Stanowisko_0.3.3.zip <PC-katalog>\qc\Ramki\etap3\wydania\SHA256SUMS_wydania.txt >> %ROB%\t0_2.log
findstr /c:"Stanowisko_0.3.3.zip" <PC-katalog>\qc\Ramki\etap3\wydania\SHA256SUMS_wydania.txt >> %ROB%\t0_2.log 2>&1
echo krok2a_findstr_sumy_main KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo === findstr Stanowisko_0.3.3.zip <PC-katalog>\t0\repo2\Ramki\etap3\wydania\SHA256SUMS_wydania.txt >> %ROB%\t0_2.log
findstr /c:"Stanowisko_0.3.3.zip" <PC-katalog>\t0\repo2\Ramki\etap3\wydania\SHA256SUMS_wydania.txt >> %ROB%\t0_2.log 2>&1
echo krok2a_findstr_sumy_repo2 KOD=%ERRORLEVEL% (1 = 0 wierszy) >> %ROB%\kody.txt
echo START %date% %time% > %ROB%\t0_2b.log
echo === C:\Windows\System32\tar.exe -xf %ZIP% -C %P1% >> %ROB%\t0_2b.log
C:\Windows\System32\tar.exe -xf %ZIP% -C %P1% >> %ROB%\t0_2b.log 2>&1
set KOD=%ERRORLEVEL%
echo krok2b_tar KOD=%KOD% >> %ROB%\kody.txt
echo KONIEC %date% %time% KOD=%KOD% >> %ROB%\t0_2b.log
exit /b %KOD%
