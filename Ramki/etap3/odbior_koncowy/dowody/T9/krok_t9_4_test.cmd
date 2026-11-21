@echo off
rem T9 krok 4 - test test_zz_k8 (polecenie planu doslownie + wejscie NUL i zapis do logu)
set QT_QPA_PLATFORM=offscreen
echo START %TIME% > <PC-katalog>\koordynator\robocze\odbior\T9\t9_test_zz_k8_czas.txt
call <PC-katalog>\t0\odbior\Stanowisko\Polecenie.cmd -m pytest <PC-katalog>\t0\repo\Ramki\stanowisko\testy\test_indicate.py <PC-katalog>\t0\repo\Ramki\stanowisko\testy\test_ramka.py -q -rA -p no:cacheprovider --rootdir <PC-katalog>\t0\repo\Ramki\stanowisko -k test_zz_k8 > <PC-katalog>\koordynator\robocze\odbior\T9\t9_test_zz_k8.log 2>&1 < NUL
set KOD=%ERRORLEVEL%
echo krok4_test_zz_k8 KOD=%KOD% >> <PC-katalog>\koordynator\robocze\odbior\T9\kody.txt
echo KONIEC %TIME% KOD=%KOD% >> <PC-katalog>\koordynator\robocze\odbior\T9\t9_test_zz_k8_czas.txt
exit /b %KOD%