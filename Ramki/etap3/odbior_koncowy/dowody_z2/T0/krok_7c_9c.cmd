@echo off
rem T0 kroki 7c i 9c ponownie: zliczenia przez C:\Windows\System32\find.exe (pierwsze wykonanie zlapalo "find" z Git Bash)
set ROB=<PC-katalog>\koordynator\robocze\odbior2\final\T0
set K=<PC-katalog>\t0\odbior2\Stanowisko
set F=C:\Windows\System32\find.exe
echo === %F% /c "Traceback" %K%\dane\logi\stanowisko.log >> %ROB%\t0_start.txt
%F% /c "Traceback" %K%\dane\logi\stanowisko.log >> %ROB%\t0_start.txt 2>&1
echo krok7c_find_traceback_powtorka KOD=%ERRORLEVEL% (1 = 0 wierszy) >> %ROB%\kody.txt
echo === %F% /c "Downloading" %K%\wersje\0.3.3\pip.log >> %ROB%\t0_pip_bez_sieci.txt
%F% /c "Downloading" %K%\wersje\0.3.3\pip.log >> %ROB%\t0_pip_bez_sieci.txt 2>&1
echo krok9c_find_downloading_powtorka KOD=%ERRORLEVEL% (1 = 0 wierszy) >> %ROB%\kody.txt
echo === %F% /c "http" %K%\wersje\0.3.3\pip.log >> %ROB%\t0_pip_bez_sieci.txt
%F% /c "http" %K%\wersje\0.3.3\pip.log >> %ROB%\t0_pip_bez_sieci.txt 2>&1
echo krok9c_find_http_powtorka KOD=%ERRORLEVEL% >> %ROB%\kody.txt
exit /b 0
