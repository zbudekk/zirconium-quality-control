@echo off
rem T3 krok 1: sterownik t3_poranek.py na instalacji wspolnej (polecenie planu + --wymagaj-100)
set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe
set QT_QPA_PLATFORM=offscreen
set K=<PC-katalog>\t0\odbior\Stanowisko
set ST=<PC-katalog>\t0\repo\Ramki\stanowisko
set ODB=<PC-katalog>\t0\repo\Ramki\etap3\odbior_koncowy
set ROB=<PC-katalog>\koordynator\robocze\odbior\T3
echo t3_sterownik START %DATE% %TIME% >> %ROB%\kody.txt
call %K%\Polecenie.cmd %ODB%\narzedzia\t3_poranek.py --testy %ST%\testy --wyjscie %ROB%\t3 --ustawienia-wzor %K%\ustawienia.toml --wymagaj-100 > %ROB%\t3_sterownik.log 2>&1 < NUL
echo t3_sterownik KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo t3_sterownik KONIEC %DATE% %TIME% >> %ROB%\kody.txt
