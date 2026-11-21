@echo off
rem T1 krok 5: pelny pytest interpreterem bazowym na <REPO> = t0\repo2 (polecenie planu + zapis kodu)
set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe
set QT_QPA_PLATFORM=offscreen
set ROB=<PC-katalog>\koordynator\robocze\odbior2\final\T1
set ST=<PC-katalog>\t0\repo2\Ramki\stanowisko
echo przebieg2 START %date% %time% >> %ROB%\t1_czasy.txt
cd /d %ST%
call <PC-katalog>\koordynator\narz\py.cmd -m pytest -q -p no:cacheprovider -rs < NUL > %ROB%\t1_pytest_bazowy.log 2>&1
set KOD=%ERRORLEVEL%
echo krok5_pytest_bazowy KOD=%KOD% >> %ROB%\kody.txt
echo przebieg2 KONIEC %date% %time% KOD=%KOD% >> %ROB%\t1_czasy.txt
exit /b %KOD%
