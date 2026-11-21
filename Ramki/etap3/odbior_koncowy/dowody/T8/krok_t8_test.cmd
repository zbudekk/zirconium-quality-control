@echo off
set QT_QPA_PLATFORM=offscreen
set K=<PC-katalog>\t0\odbior\Stanowisko
set ST=<PC-katalog>\t0\repo\Ramki\stanowisko
set ROB=<PC-katalog>\koordynator\robocze\odbior\T8
echo test_metryki START %TIME% >> %ROB%\kody.txt
call %K%\Polecenie.cmd -m pytest %ST%\testy\test_metryki.py -q -p no:cacheprovider --rootdir %ST% > %ROB%\t8_test_metryki.log 2>&1 < NUL
echo t8_test_metryki KOD=%ERRORLEVEL% KONIEC %TIME% >> %ROB%\kody.txt
