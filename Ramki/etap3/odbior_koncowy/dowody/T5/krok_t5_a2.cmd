@echo off
rem T5 czesc A polecenie 2 (plan): test_aplikacja_rano.py na kodzie z instalacji
set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe
set QT_QPA_PLATFORM=offscreen
set K=<PC-katalog>\t0\odbior\Stanowisko
set ST=<PC-katalog>\t0\repo\Ramki\stanowisko
set ODB=<PC-katalog>\t0\repo\Ramki\etap3\odbior_koncowy
set ROB=<PC-katalog>\koordynator\robocze\odbior\T5
echo t5_a2 START %DATE% %TIME% >> %ROB%\kody.txt
call %K%\Polecenie.cmd %ODB%\narzedzia\pytest_instalacja.py --st %ST% --wynik %ROB%\t5_zrodlo_kodu_2.txt -- %ST%\testy\test_aplikacja_rano.py -q -s -rA -p no:cacheprovider --rootdir %ST% -k "test_a_ or test_k1_plan_ramki_porannej or test_k2_enter or test_k4_spacja" > %ROB%\t5_testy_2.log 2>&1 < NUL
echo t5_a2 KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo t5_a2 KONIEC %DATE% %TIME% >> %ROB%\kody.txt
