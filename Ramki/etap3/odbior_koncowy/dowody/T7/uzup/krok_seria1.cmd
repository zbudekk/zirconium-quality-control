@echo off
set QT_QPA_PLATFORM=offscreen
call <PC-katalog>\t0\odbior_t12\Stanowisko\Polecenie.cmd <PC-katalog>\koordynator\robocze\odbior\T7\uzup\sonda_komunikaty.py --przypadek 4 --wariant a --powt 2 --limit 400 > <PC-katalog>\koordynator\robocze\odbior\T7\uzup\p4a_2.log 2>&1 < NUL
echo p4a_2 KOD=%ERRORLEVEL% %TIME% >> <PC-katalog>\koordynator\robocze\odbior\T7\uzup\kody.txt
call <PC-katalog>\t0\odbior_t12\Stanowisko\Polecenie.cmd <PC-katalog>\koordynator\robocze\odbior\T7\uzup\sonda_komunikaty.py --przypadek 4 --wariant b --powt 1 --limit 400 > <PC-katalog>\koordynator\robocze\odbior\T7\uzup\p4b_1.log 2>&1 < NUL
echo p4b_1 KOD=%ERRORLEVEL% %TIME% >> <PC-katalog>\koordynator\robocze\odbior\T7\uzup\kody.txt
call <PC-katalog>\t0\odbior_t12\Stanowisko\Polecenie.cmd <PC-katalog>\koordynator\robocze\odbior\T7\uzup\sonda_komunikaty.py --przypadek 4 --wariant b --powt 2 --skan --limit 700 > <PC-katalog>\koordynator\robocze\odbior\T7\uzup\p4b_2.log 2>&1 < NUL
echo p4b_2 KOD=%ERRORLEVEL% %TIME% >> <PC-katalog>\koordynator\robocze\odbior\T7\uzup\kody.txt
call <PC-katalog>\t0\odbior_t12\Stanowisko\Polecenie.cmd <PC-katalog>\koordynator\robocze\odbior\T7\uzup\sonda_komunikaty.py --przypadek 3 --powt 1 --limit 900 > <PC-katalog>\koordynator\robocze\odbior\T7\uzup\p3_1.log 2>&1 < NUL
echo p3_1 KOD=%ERRORLEVEL% %TIME% >> <PC-katalog>\koordynator\robocze\odbior\T7\uzup\kody.txt
call <PC-katalog>\t0\odbior_t12\Stanowisko\Polecenie.cmd <PC-katalog>\koordynator\robocze\odbior\T7\uzup\sonda_komunikaty.py --przypadek 3 --powt 2 --limit 900 > <PC-katalog>\koordynator\robocze\odbior\T7\uzup\p3_2.log 2>&1 < NUL
echo p3_2 KOD=%ERRORLEVEL% %TIME% >> <PC-katalog>\koordynator\robocze\odbior\T7\uzup\kody.txt
call <PC-katalog>\t0\odbior_t12\Stanowisko\Polecenie.cmd <PC-katalog>\koordynator\robocze\odbior\T7\uzup\sonda_komunikaty.py --przypadek 2 --powt 1 --limit 700 > <PC-katalog>\koordynator\robocze\odbior\T7\uzup\p2_1.log 2>&1 < NUL
echo p2_1 KOD=%ERRORLEVEL% %TIME% >> <PC-katalog>\koordynator\robocze\odbior\T7\uzup\kody.txt
call <PC-katalog>\t0\odbior_t12\Stanowisko\Polecenie.cmd <PC-katalog>\koordynator\robocze\odbior\T7\uzup\sonda_komunikaty.py --przypadek 2 --powt 2 --limit 700 > <PC-katalog>\koordynator\robocze\odbior\T7\uzup\p2_2.log 2>&1 < NUL
echo p2_2 KOD=%ERRORLEVEL% %TIME% >> <PC-katalog>\koordynator\robocze\odbior\T7\uzup\kody.txt
call <PC-katalog>\t0\odbior_t12\Stanowisko\Polecenie.cmd <PC-katalog>\koordynator\robocze\odbior\T7\uzup\sonda_komunikaty.py --przypadek 5 --wariant a --powt 1 --limit 400 > <PC-katalog>\koordynator\robocze\odbior\T7\uzup\p5a_1.log 2>&1 < NUL
echo p5a_1 KOD=%ERRORLEVEL% %TIME% >> <PC-katalog>\koordynator\robocze\odbior\T7\uzup\kody.txt
call <PC-katalog>\t0\odbior_t12\Stanowisko\Polecenie.cmd <PC-katalog>\koordynator\robocze\odbior\T7\uzup\sonda_komunikaty.py --przypadek 5 --wariant a --powt 2 --limit 400 > <PC-katalog>\koordynator\robocze\odbior\T7\uzup\p5a_2.log 2>&1 < NUL
echo p5a_2 KOD=%ERRORLEVEL% %TIME% >> <PC-katalog>\koordynator\robocze\odbior\T7\uzup\kody.txt
call <PC-katalog>\t0\odbior_t12\Stanowisko\Polecenie.cmd <PC-katalog>\koordynator\robocze\odbior\T7\uzup\sonda_komunikaty.py --przypadek 5 --wariant d --powt 1 --limit 400 > <PC-katalog>\koordynator\robocze\odbior\T7\uzup\p5d_1.log 2>&1 < NUL
echo p5d_1 KOD=%ERRORLEVEL% %TIME% >> <PC-katalog>\koordynator\robocze\odbior\T7\uzup\kody.txt
call <PC-katalog>\t0\odbior_t12\Stanowisko\Polecenie.cmd <PC-katalog>\koordynator\robocze\odbior\T7\uzup\sonda_komunikaty.py --przypadek 6 --powt 1 --limit 700 > <PC-katalog>\koordynator\robocze\odbior\T7\uzup\p6_1.log 2>&1 < NUL
echo p6_1 KOD=%ERRORLEVEL% %TIME% >> <PC-katalog>\koordynator\robocze\odbior\T7\uzup\kody.txt
call <PC-katalog>\t0\odbior_t12\Stanowisko\Polecenie.cmd <PC-katalog>\koordynator\robocze\odbior\T7\uzup\sonda_komunikaty.py --przypadek 6 --powt 2 --limit 700 > <PC-katalog>\koordynator\robocze\odbior\T7\uzup\p6_2.log 2>&1 < NUL
echo p6_2 KOD=%ERRORLEVEL% %TIME% >> <PC-katalog>\koordynator\robocze\odbior\T7\uzup\kody.txt
call <PC-katalog>\t0\odbior_t12\Stanowisko\Polecenie.cmd <PC-katalog>\koordynator\robocze\odbior\T7\uzup\sonda_komunikaty.py --przypadek 1 --powt 1 --limit 800 > <PC-katalog>\koordynator\robocze\odbior\T7\uzup\p1_1.log 2>&1 < NUL
echo p1_1 KOD=%ERRORLEVEL% %TIME% >> <PC-katalog>\koordynator\robocze\odbior\T7\uzup\kody.txt
call <PC-katalog>\t0\odbior_t12\Stanowisko\Polecenie.cmd <PC-katalog>\koordynator\robocze\odbior\T7\uzup\sonda_komunikaty.py --przypadek 1 --powt 2 --limit 800 > <PC-katalog>\koordynator\robocze\odbior\T7\uzup\p1_2.log 2>&1 < NUL
echo p1_2 KOD=%ERRORLEVEL% %TIME% >> <PC-katalog>\koordynator\robocze\odbior\T7\uzup\kody.txt
call <PC-katalog>\t0\odbior_t12\Stanowisko\Polecenie.cmd <PC-katalog>\koordynator\robocze\odbior\T7\uzup\sonda_komunikaty.py --przypadek 2 --wariant c --powt 1 --limit 700 > <PC-katalog>\koordynator\robocze\odbior\T7\uzup\p2c_1.log 2>&1 < NUL
echo p2c_1 KOD=%ERRORLEVEL% %TIME% >> <PC-katalog>\koordynator\robocze\odbior\T7\uzup\kody.txt
exit /b 0
