@echo off
rem T1 krok 1: doinstalowanie pytest (/testy) na instalacji wspolnej 0.3.3 (oczekiwany kod 0); krok 3: _wmi -> None
set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe
set QT_QPA_PLATFORM=offscreen
set ROB=<PC-katalog>\koordynator\robocze\odbior2\final\T1
set K=<PC-katalog>\t0\odbior2\Stanowisko
echo START %date% %time% > %ROB%\t1_1_czas.txt
call <PC-katalog>\t0\odbior2\paczka_0.3.3\zainstaluj.cmd /katalog %K% /python %PY% /bez-sieci /bez-pauzy /testy < NUL > %ROB%\t1_zainstaluj_testy.log 2>&1
set KOD=%ERRORLEVEL%
echo krok1_zainstaluj_testy KOD=%KOD% >> %ROB%\kody.txt
echo KONIEC %date% %time% KOD=%KOD% >> %ROB%\t1_1_czas.txt
call %K%\Polecenie.cmd -c "import stanowisko, sys; print(sys.modules.get('_wmi', 'brak'))" < NUL > %ROB%\t1_3_wmi.log 2>&1
echo krok3_wmi KOD=%ERRORLEVEL% >> %ROB%\kody.txt
exit /b %KOD%
