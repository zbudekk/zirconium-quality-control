@echo off
cd /d <PC-katalog>\qc-wt\integ\Ramki\stanowisko
echo t10 START %DATE% %TIME% >> <PC-katalog>\koordynator\robocze\odbior2\final\T10\kody.txt
call <PC-katalog>\koordynator\narz\py.cmd narzedzia\metryki_P3a.py --skany <PC-katalog>\app\dane_ref\syntetyczne_R59_P2 <PC-katalog>\app\dane_ref\syntetyczne_R59_P3a --projekty <PC-katalog>\koordynator\robocze\odbior2\final\T10\robocze\Cyrkon --wyjscie <PC-katalog>\koordynator\robocze\odbior2\final\T10\t10 --nazwa t10_surowe_metryki.json --procesy 1 --ustawienia <PC-katalog>\koordynator\robocze\odbior2\final\T10\ustawienia_wzor.toml > <PC-katalog>\koordynator\robocze\odbior2\final\T10\t10_surowe.log 2>&1 < NUL
set KOD=%ERRORLEVEL%
echo t10 KOD=%KOD% >> <PC-katalog>\koordynator\robocze\odbior2\final\T10\kody.txt
echo t10 KONIEC %DATE% %TIME% >> <PC-katalog>\koordynator\robocze\odbior2\final\T10\kody.txt
exit /b %KOD%
