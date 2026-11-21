@echo off
cd /d <PC-katalog>\qc-wt\integ\Ramki\stanowisko
set QT_QPA_PLATFORM=offscreen
echo t11 B program START %DATE% %TIME% >> <PC-katalog>\koordynator\robocze\odbior2\final\T11\kody.txt
call <PC-katalog>\koordynator\narz\py.cmd -m stanowisko.aplikacja --ustawienia <PC-katalog>\koordynator\robocze\odbior2\final\T11\ustawienia_t11.toml --zamknij-po 3000 > <PC-katalog>\koordynator\robocze\odbior2\final\T11\t11_program_stdout.log 2>&1 < NUL
echo t11 B program KOD=%ERRORLEVEL% >> <PC-katalog>\koordynator\robocze\odbior2\final\T11\kody.txt
echo t11 B program KONIEC %DATE% %TIME% >> <PC-katalog>\koordynator\robocze\odbior2\final\T11\kody.txt
echo koniec > <PC-katalog>\koordynator\robocze\odbior2\final\T11\robocze\t11\program_koniec.txt
