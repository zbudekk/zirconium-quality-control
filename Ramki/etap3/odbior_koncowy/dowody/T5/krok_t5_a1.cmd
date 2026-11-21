@echo off
rem T5 czesc A polecenie 1 (plan): test_indicate.py + test_ramka.py na kodzie z instalacji
set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe
set QT_QPA_PLATFORM=offscreen
set K=<PC-katalog>\t0\odbior\Stanowisko
set ST=<PC-katalog>\t0\repo\Ramki\stanowisko
set ODB=<PC-katalog>\t0\repo\Ramki\etap3\odbior_koncowy
set ROB=<PC-katalog>\koordynator\robocze\odbior\T5
echo t5_a1 START %DATE% %TIME% >> %ROB%\kody.txt
call %K%\Polecenie.cmd %ODB%\narzedzia\pytest_instalacja.py --st %ST% --wynik %ROB%\t5_zrodlo_kodu_1.txt -- %ST%\testy\test_indicate.py %ST%\testy\test_ramka.py -q -s -rA -p no:cacheprovider --rootdir %ST% -k "test_k1 or test_k2 or test_k4 or test_k5 or test_k6 or test_k7 or test_zz_k8" > %ROB%\t5_testy.log 2>&1 < NUL
echo t5_a1 KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo t5_a1 KONIEC %DATE% %TIME% >> %ROB%\kody.txt
