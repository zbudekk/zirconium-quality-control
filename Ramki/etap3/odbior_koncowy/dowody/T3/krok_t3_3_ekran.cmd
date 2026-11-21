@echo off
rem T3 krok 3: testy uzupelniajace ekranu porannego (polecenie planu)
set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe
set QT_QPA_PLATFORM=offscreen
set K=<PC-katalog>\t0\odbior\Stanowisko
set ST=<PC-katalog>\t0\repo\Ramki\stanowisko
set ODB=<PC-katalog>\t0\repo\Ramki\etap3\odbior_koncowy
set ROB=<PC-katalog>\koordynator\robocze\odbior\T3
echo t3_ekran START %DATE% %TIME% >> %ROB%\kody.txt
call %K%\Polecenie.cmd -m pytest %ST%\testy\test_ui_rano.py %ST%\testy\test_aplikacja_rano.py -q -rA -p no:cacheprovider --rootdir %ST% > %ROB%\t3_ekran.log 2>&1 < NUL
echo t3_ekran KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo t3_ekran KONIEC %DATE% %TIME% >> %ROB%\kody.txt
