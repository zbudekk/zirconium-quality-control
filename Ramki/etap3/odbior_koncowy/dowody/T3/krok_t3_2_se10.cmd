@echo off
rem T3 krok 2: test uzupelniajacy SE10 na poziomie sesji (polecenie planu)
set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe
set QT_QPA_PLATFORM=offscreen
set K=<PC-katalog>\t0\odbior\Stanowisko
set ST=<PC-katalog>\t0\repo\Ramki\stanowisko
set ODB=<PC-katalog>\t0\repo\Ramki\etap3\odbior_koncowy
set ROB=<PC-katalog>\koordynator\robocze\odbior\T3
echo t3_se10 START %DATE% %TIME% >> %ROB%\kody.txt
call %K%\Polecenie.cmd -m pytest %ST%\testy\test_session_rano.py -q -rA -p no:cacheprovider --rootdir %ST% -k "se10" --basetemp %ROB%\t3_tmp > %ROB%\t3_se10.log 2>&1 < NUL
echo t3_se10 KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo t3_se10 KONIEC %DATE% %TIME% >> %ROB%\kody.txt
