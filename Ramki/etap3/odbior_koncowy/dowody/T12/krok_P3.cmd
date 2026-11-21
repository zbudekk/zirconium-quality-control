@echo off
rem T12 przygotowanie (T0 krok 3 w katalogu odbior_t12): pierwsza instalacja 0.3.1, oczekiwany kod 10
set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe
set QT_QPA_PLATFORM=offscreen
set ROB=<PC-katalog>\koordynator\robocze\odbior\T12
set K=<PC-katalog>\t0\odbior_t12\Stanowisko
set P1=<PC-katalog>\t0\odbior\paczka_0.3.1
echo P3_zainstaluj_N_1 START %date% %time% >> %ROB%\czasy.txt
call %P1%\zainstaluj.cmd /katalog %K% /python %PY% /bez-sieci /bez-pauzy < NUL > %ROB%\t12_P3_zainstaluj_N_1.log 2>&1
set KOD=%ERRORLEVEL%
echo P3_zainstaluj_N_1 KOD=%KOD% >> %ROB%\kody.txt
echo P3_zainstaluj_N_1 KONIEC %date% %time% KOD=%KOD% >> %ROB%\czasy.txt
exit /b %KOD%
