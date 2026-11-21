@echo off
rem T0 krok 5: ponowna instalacja po uzupelnieniu ustawien (oczekiwany kod 0)
set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe
set QT_QPA_PLATFORM=offscreen
set ROB=<PC-katalog>\koordynator\robocze\odbior\T0
echo START %date% %time% > %ROB%\t0_5_czas.txt
call <PC-katalog>\t0\odbior\paczka_0.3.1\zainstaluj.cmd /katalog <PC-katalog>\t0\odbior\Stanowisko /python %PY% /bez-sieci /bez-pauzy < NUL > %ROB%\t0_zainstaluj_2.log 2>&1
set KOD=%ERRORLEVEL%
echo krok5_zainstaluj_2 KOD=%KOD% >> %ROB%\kody.txt
echo KONIEC %date% %time% KOD=%KOD% >> %ROB%\t0_5_czas.txt
exit /b %KOD%