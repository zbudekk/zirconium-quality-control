@echo off
rem T0 krok 3: pierwsza instalacja z paczki 0.3.1 (oczekiwany kod 10)
set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe
set QT_QPA_PLATFORM=offscreen
set ROB=<PC-katalog>\koordynator\robocze\odbior\T0
echo START %date% %time% > %ROB%\t0_3_czas.txt
call <PC-katalog>\t0\odbior\paczka_0.3.1\zainstaluj.cmd /katalog <PC-katalog>\t0\odbior\Stanowisko /python %PY% /bez-sieci /bez-pauzy < NUL > %ROB%\t0_zainstaluj_1.log 2>&1
set KOD=%ERRORLEVEL%
echo krok3_zainstaluj_1 KOD=%KOD% >> %ROB%\kody.txt
echo KONIEC %date% %time% KOD=%KOD% >> %ROB%\t0_3_czas.txt
exit /b %KOD%