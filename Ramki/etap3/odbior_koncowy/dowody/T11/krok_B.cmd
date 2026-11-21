@echo off
rem T11 czesc B: program z instalacji wspolnej z WLASNYM plikiem ustawien (okno offscreen) + symulator skanera: 40 skanow *_r54 co 45 s
set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe
set QT_QPA_PLATFORM=offscreen
set ROB=<PC-katalog>\koordynator\robocze\odbior\T11
set K=<PC-katalog>\t0\odbior\Stanowisko
echo B START %date% %time% >> %ROB%\czasy.txt
start "" /b cmd /c %ROB%\krok_B_program.cmd
ping -n 21 127.0.0.1 > NUL
echo B symulator START %date% %time% >> %ROB%\czasy.txt
call %K%\Polecenie.cmd narzedzia\symulator_skanera.py --folder %ROB%\robocze\eksport --zrodla <PC-katalog>\app\dane_ref\syntetyczne_r54_P2 <PC-katalog>\app\dane_ref\syntetyczne_r54_P3a --ile 40 --odstep 45 --rownolegle 1 --seed 1 --dziennik %ROB%\t11_symulator.json < NUL > %ROB%\t11_symulator.log 2>&1
echo B symulator KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo B symulator KONIEC %date% %time% >> %ROB%\czasy.txt
set N=0
:czekaj
if exist %ROB%\robocze\program_koniec.txt goto koniec
set /a N+=1
if %N% GEQ 200 goto za_dlugo
ping -n 11 127.0.0.1 > NUL
goto czekaj
:za_dlugo
echo B program NIE ZAKONCZYL SIE w 2000 s po koncu symulatora %date% %time% >> %ROB%\kody.txt
:koniec
echo B KONIEC %date% %time% >> %ROB%\czasy.txt
exit /b 0