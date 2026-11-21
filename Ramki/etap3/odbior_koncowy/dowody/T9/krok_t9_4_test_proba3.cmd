@echo off
rem T9 krok 4 - proba 3: POLECENIE ZMIENIONE (tylko -k): test_zz_k8 razem z testami test_k1 i test_k2 obu plikow,
rem zeby zapis ruchu mial objetosc wymagana przez test (uruchomiony sam: 16 komunikatow, prog testu 20).
set QT_QPA_PLATFORM=offscreen
echo START %TIME% > <PC-katalog>\koordynator\robocze\odbior\T9\t9_test_zz_k8_proba3_czas.txt
call <PC-katalog>\t0\odbior\Stanowisko\Polecenie.cmd -m pytest <PC-katalog>\t0\repo\Ramki\stanowisko\testy\test_indicate.py <PC-katalog>\t0\repo\Ramki\stanowisko\testy\test_ramka.py -q -rA -p no:cacheprovider --rootdir <PC-katalog>\t0\repo\Ramki\stanowisko -k "test_k1 or test_k2 or test_zz_k8" > <PC-katalog>\koordynator\robocze\odbior\T9\t9_test_zz_k8_proba3.log 2>&1 < NUL
set KOD=%ERRORLEVEL%
echo krok4_test_zz_k8_proba3_k1_k2_zz_k8 KOD=%KOD% >> <PC-katalog>\koordynator\robocze\odbior\T9\kody.txt
echo KONIEC %TIME% KOD=%KOD% >> <PC-katalog>\koordynator\robocze\odbior\T9\t9_test_zz_k8_proba3_czas.txt
exit /b %KOD%