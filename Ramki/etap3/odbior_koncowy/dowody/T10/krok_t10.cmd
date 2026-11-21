@echo off
rem T10 - Regresja silnika (odbior koncowy etapu 3, paczka 0.3.1). Polecenie z PLAN_TESTOW.md sekcja T10, doslownie; pelne 40 skanow, 1 proces.
set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe
set QT_QPA_PLATFORM=offscreen
echo t10_metryki START %DATE% %TIME% >> <PC-katalog>\koordynator\robocze\odbior\T10\kody.txt
call <PC-katalog>\t0\odbior\Stanowisko\Polecenie.cmd narzedzia\metryki_P3a.py --skany <PC-katalog>\app\dane_ref\syntetyczne_R59_P2 <PC-katalog>\app\dane_ref\syntetyczne_R59_P3a --projekty <PC-katalog>\app\Prace_test --wyjscie <PC-katalog>\koordynator\robocze\odbior\T10\t10 --nazwa t10_surowe_metryki.json --procesy 1 --ustawienia <PC-katalog>\t0\odbior\Stanowisko\ustawienia.toml > <PC-katalog>\koordynator\robocze\odbior\T10\t10_surowe.log 2>&1 < NUL
echo t10_metryki KOD=%ERRORLEVEL% >> <PC-katalog>\koordynator\robocze\odbior\T10\kody.txt
set KOD=%ERRORLEVEL%
echo t10_metryki KONIEC %DATE% %TIME% >> <PC-katalog>\koordynator\robocze\odbior\T10\kody.txt
exit /b %KOD%
