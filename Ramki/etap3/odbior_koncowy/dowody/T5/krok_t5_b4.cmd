@echo off
rem T5 czesc B krok 4 (plan): 3 skany wieczorne przez program z paczki (sterownik T2), ramki z kopii ustawien w ROB
set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe
set QT_QPA_PLATFORM=offscreen
set K=<PC-katalog>\t0\odbior\Stanowisko
set ST=<PC-katalog>\t0\repo\Ramki\stanowisko
set ODB=<PC-katalog>\t0\repo\Ramki\etap3\odbior_koncowy
set ROB=<PC-katalog>\koordynator\robocze\odbior\T5
echo t5_b4 START %DATE% %TIME% >> %ROB%\kody.txt
call %K%\Polecenie.cmd %ODB%\narzedzia\t2_wieczor.py --ustawienia-wzor %ROB%\ustawienia.toml --roboczy %ROB%\t5_wieczor --projekty %ROB%\robocze\Cyrkon --wybierz 1,3,8 --odstep 60 > %ROB%\t5_wieczor.log 2>&1 < NUL
set KOD=%ERRORLEVEL%
echo t5_b4 KOD=%KOD% >> %ROB%\kody.txt
echo t5_b4 KONIEC %DATE% %TIME% >> %ROB%\kody.txt
exit /b %KOD%
