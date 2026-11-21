@echo off
rem kontrola zestawu T14 na instalacji z paczki 0.3.3 (plan: "Podzial na wykonawcow", zaraz po T0)
set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe
set QT_QPA_PLATFORM=offscreen
set R14=<PC-katalog>\koordynator\robocze\odbior2\final\T0
set K=<PC-katalog>\t0\odbior2\Stanowisko
set REPO=<PC-katalog>\t0\repo2
echo START %date% %time% > %R14%\t14_czas.txt
call %K%\Polecenie.cmd %REPO%\Ramki\etap3\t14\symulator_t14.py --sprawdz --program . < NUL > %R14%\t14_sprawdz_paczka.txt 2>&1
set KOD=%ERRORLEVEL%
echo t14_sprawdz KOD=%KOD% >> %R14%\kody.txt
echo KONIEC %date% %time% KOD=%KOD% >> %R14%\t14_czas.txt
exit /b %KOD%
