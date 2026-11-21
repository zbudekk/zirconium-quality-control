@echo off
rem T2 - Wieczor od poczatku do konca: sterownik t2_wieczor.py, PELNY scenariusz (10 pozycji co 60 s) - polecenie planu doslownie
set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe
set QT_QPA_PLATFORM=offscreen
set K=<PC-katalog>\t0\odbior\Stanowisko
set ODB=<PC-katalog>\t0\repo\Ramki\etap3\odbior_koncowy
set ROB=<PC-katalog>\koordynator\robocze\odbior\T2
echo t2_sterownik START %DATE% %TIME% >> %ROB%\kody.txt
call %K%\Polecenie.cmd %ODB%\narzedzia\t2_wieczor.py --ustawienia-wzor %K%\ustawienia.toml --roboczy %ROB%\t2 --projekty %ROB%\robocze\Cyrkon > %ROB%\t2_sterownik.log 2>&1 < NUL
set KOD=%ERRORLEVEL%
echo t2_sterownik KOD=%KOD% %DATE% %TIME% >> %ROB%\kody.txt
exit /b %KOD%
