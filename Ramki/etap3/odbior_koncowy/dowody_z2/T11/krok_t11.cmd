@echo off
cd /d <PC-katalog>\qc-wt\integ\Ramki\stanowisko
set QT_QPA_PLATFORM=offscreen
echo t11 A START %DATE% %TIME% >> <PC-katalog>\koordynator\robocze\odbior2\final\T11\kody.txt
call <PC-katalog>\koordynator\narz\py.cmd narzedzia\auto_uklad.py --skany <PC-katalog>\app\dane_ref\syntetyczne_r54_P2 <PC-katalog>\app\dane_ref\syntetyczne_r54_P3a --wyjscie <PC-katalog>\koordynator\robocze\odbior2\final\T11\t11_auto --procesy 1 --ustawienia <PC-katalog>\koordynator\robocze\odbior2\final\T11\ustawienia_wzor.toml > <PC-katalog>\koordynator\robocze\odbior2\final\T11\t11_auto_uklad.log 2>&1 < NUL
echo t11 A auto_uklad KOD=%ERRORLEVEL% >> <PC-katalog>\koordynator\robocze\odbior2\final\T11\kody.txt
echo t11 B START %DATE% %TIME% >> <PC-katalog>\koordynator\robocze\odbior2\final\T11\kody.txt
start "" /b cmd /c <PC-katalog>\koordynator\robocze\odbior2\final\T11\krok_t11_program.cmd
ping -n 21 127.0.0.1 > NUL
call <PC-katalog>\koordynator\narz\py.cmd narzedzia\symulator_skanera.py --folder <PC-katalog>\koordynator\robocze\odbior2\final\T11\robocze\t11\eksport --zrodla <PC-katalog>\app\dane_ref\syntetyczne_r54_P2 <PC-katalog>\app\dane_ref\syntetyczne_r54_P3a --ile 40 --odstep 45 --rownolegle 1 --seed 1 --dziennik <PC-katalog>\koordynator\robocze\odbior2\final\T11\t11_symulator.json > <PC-katalog>\koordynator\robocze\odbior2\final\T11\t11_symulator.log 2>&1 < NUL
echo t11 B symulator KOD=%ERRORLEVEL% >> <PC-katalog>\koordynator\robocze\odbior2\final\T11\kody.txt
set N=0
:czekaj
if exist <PC-katalog>\koordynator\robocze\odbior2\final\T11\robocze\t11\program_koniec.txt goto koniec
set /a N+=1
if %N% GEQ 200 goto za_dlugo
ping -n 11 127.0.0.1 > NUL
goto czekaj
:za_dlugo
echo t11 B program NIE ZAKONCZYL SIE w 2000 s po koncu symulatora >> <PC-katalog>\koordynator\robocze\odbior2\final\T11\kody.txt
:koniec
echo t11 B KONIEC %DATE% %TIME% >> <PC-katalog>\koordynator\robocze\odbior2\final\T11\kody.txt
echo t11 testy START %DATE% %TIME% >> <PC-katalog>\koordynator\robocze\odbior2\final\T11\kody.txt
call <PC-katalog>\koordynator\narz\py.cmd -m pytest testy\test_session_wieczor.py testy\test_straznik.py testy\test_kontroler_api.py testy\test_auto_uklad.py -q -rA -p no:cacheprovider -k "niezgodny_uklad or niezgodna_z_ukladem or auto or innego_ukladu" > <PC-katalog>\koordynator\robocze\odbior2\final\T11\t11_testy.log 2>&1 < NUL
echo t11 testy KOD=%ERRORLEVEL% >> <PC-katalog>\koordynator\robocze\odbior2\final\T11\kody.txt
echo t11 testy KONIEC %DATE% %TIME% >> <PC-katalog>\koordynator\robocze\odbior2\final\T11\kody.txt
exit /b 0
