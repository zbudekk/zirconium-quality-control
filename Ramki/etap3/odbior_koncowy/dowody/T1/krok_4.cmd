@echo off
rem T1 krok 4: pelny pytest interpreterem srodowiska wersji (polecenie planu, jedna linia + zapis kodu)
set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe
set QT_QPA_PLATFORM=offscreen
set ROB=<PC-katalog>\koordynator\robocze\odbior\T1
set K=<PC-katalog>\t0\odbior\Stanowisko
set ST=<PC-katalog>\t0\repo\Ramki\stanowisko
echo przebieg1 START %date% %time% >> %ROB%\t1_czasy.txt
call %K%\Polecenie.cmd -X faulthandler -m pytest %ST%\testy -q -rs -p no:cacheprovider --rootdir %ST% -o faulthandler_timeout=900 < NUL > %ROB%\t1_pytest.log 2>&1
set KOD=%ERRORLEVEL%
echo krok4_pytest_wersja KOD=%KOD% >> %ROB%\kody.txt
echo przebieg1 KONIEC %date% %time% KOD=%KOD% >> %ROB%\t1_czasy.txt
exit /b %KOD%