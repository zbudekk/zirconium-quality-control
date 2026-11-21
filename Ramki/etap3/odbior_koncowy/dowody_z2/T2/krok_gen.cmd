@echo off
rem T2 krok 1: skany plytek ramkowych scenariusza do wlasnego katalogu (lekki, ok. 80 s)
cd /d <PC-katalog>\qc-wt\integ\Ramki\stanowisko
echo gen START %DATE% %TIME% >> <PC-katalog>\koordynator\robocze\odbior2\final\T2\kody.txt
call <PC-katalog>\koordynator\narz\py.cmd narzedzia\symulator_skanera.py --tylko-generuj --scenariusz <PC-katalog>\qc-wt\integ\Ramki\etap3\odbior_koncowy\narzedzia\t2_scenariusz_okragle.json --katalog-generowanych <PC-katalog>\koordynator\robocze\odbior2\final\T2\robocze\gen --projekty <PC-katalog>\koordynator\robocze\odbior2\final\T2\robocze\Cyrkon > <PC-katalog>\koordynator\robocze\odbior2\final\T2\t2_gen.log 2>&1 < NUL
set KOD=%ERRORLEVEL%
echo gen KOD=%KOD% >> <PC-katalog>\koordynator\robocze\odbior2\final\T2\kody.txt
echo gen KONIEC %DATE% %TIME% >> <PC-katalog>\koordynator\robocze\odbior2\final\T2\kody.txt
exit /b %KOD%
