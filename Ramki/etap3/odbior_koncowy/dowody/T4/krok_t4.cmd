@echo off
rem T4 - Pula: trzy polecenia planu (PLAN_TESTOW.md, sekcja T4), doslownie; tor 2 przez ciezki.ps1
set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe
set QT_QPA_PLATFORM=offscreen
set ROB=<PC-katalog>\koordynator\robocze\odbior\T4
set K=<PC-katalog>\t0\odbior\Stanowisko
echo czas_zimna START %DATE% %TIME% >> %ROB%\kody.txt
call %K%\Polecenie.cmd narzedzia\metryki_pula.py czas --katalog <PC-katalog>\e3\a5\pomiary\pula400 --wpisow 400 --pamiec %ROB%\pamiec --linie %ROB%\linie --wyjscie %ROB%\t4 --nazwa t4_surowe_czas_zimna.json --procesy 1 --ustawienia %K%\ustawienia.toml > %ROB%\t4_czas_zimna.log 2>&1 < NUL
echo czas_zimna KOD=%ERRORLEVEL% %DATE% %TIME% >> %ROB%\kody.txt
echo czas_ciepla START %DATE% %TIME% >> %ROB%\kody.txt
call %K%\Polecenie.cmd narzedzia\metryki_pula.py czas --katalog <PC-katalog>\e3\a5\pomiary\pula400 --wpisow 400 --pamiec %ROB%\pamiec --linie %ROB%\linie --wyjscie %ROB%\t4 --nazwa t4_surowe_czas_ciepla.json --procesy 1 --ustawienia %K%\ustawienia.toml > %ROB%\t4_czas_ciepla.log 2>&1 < NUL
echo czas_ciepla KOD=%ERRORLEVEL% %DATE% %TIME% >> %ROB%\kody.txt
echo jakosc START %DATE% %TIME% >> %ROB%\kody.txt
call %K%\Polecenie.cmd narzedzia\metryki_pula.py jakosc --katalog <PC-katalog>\e3\a5\pomiary\pula400 --wpisow 400 --pamiec %ROB%\pamiec --linie %ROB%\linie --wyjscie %ROB%\t4 --nazwa t4_surowe_jakosc.json --procesy 1 --ustawienia %K%\ustawienia.toml > %ROB%\t4_jakosc.log 2>&1 < NUL
echo jakosc KOD=%ERRORLEVEL% %DATE% %TIME% >> %ROB%\kody.txt
exit /b 0
