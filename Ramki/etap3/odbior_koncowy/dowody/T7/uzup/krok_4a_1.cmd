@echo off
set QT_QPA_PLATFORM=offscreen
call <PC-katalog>\t0\odbior_t12\Stanowisko\Polecenie.cmd <PC-katalog>\koordynator\robocze\odbior\T7\uzup\sonda_komunikaty.py --przypadek 4 --wariant a --powt 1 --limit 400 > <PC-katalog>\koordynator\robocze\odbior\T7\uzup\p4a_1.log 2>&1 < NUL
echo p4a_1 KOD=%ERRORLEVEL% %TIME% >> <PC-katalog>\koordynator\robocze\odbior\T7\uzup\kody.txt
exit /b 0
