@echo off
rem T2 (t2): sterownik t2_wieczor.py z kopii repo przez py.cmd, scenariusz t2_scenariusz_okragle.json
cd /d <PC-katalog>\qc-wt\integ\Ramki\stanowisko
set QT_QPA_PLATFORM=offscreen
echo t2 START %DATE% %TIME% >> <PC-katalog>\koordynator\robocze\odbior2\final\T2\kody.txt
call <PC-katalog>\koordynator\narz\py.cmd <PC-katalog>\qc-wt\integ\Ramki\etap3\odbior_koncowy\narzedzia\t2_wieczor.py --scenariusz <PC-katalog>\qc-wt\integ\Ramki\etap3\odbior_koncowy\narzedzia\t2_scenariusz_okragle.json --dane-generowane <PC-katalog>\koordynator\robocze\odbior2\final\T2\robocze\gen --ustawienia-wzor <PC-katalog>\koordynator\robocze\odbior2\final\T2\ustawienia_wzor.toml --roboczy <PC-katalog>\koordynator\robocze\odbior2\final\T2\t2 --projekty <PC-katalog>\koordynator\robocze\odbior2\final\T2\robocze\Cyrkon  > <PC-katalog>\koordynator\robocze\odbior2\final\T2\t2_sterownik.log 2>&1 < NUL
set KOD=%ERRORLEVEL%
echo t2 KOD=%KOD% >> <PC-katalog>\koordynator\robocze\odbior2\final\T2\kody.txt
echo t2 KONIEC %DATE% %TIME% >> <PC-katalog>\koordynator\robocze\odbior2\final\T2\kody.txt
exit /b %KOD%
