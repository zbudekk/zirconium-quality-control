@echo off
rem T6: 3 polecenia planu (arkusz, test_excel.py, test_aplikacja_rano.py -k k3_excel) na instalacji wspolnej
set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe
set QT_QPA_PLATFORM=offscreen
set K=<PC-katalog>\t0\odbior\Stanowisko
set ST=<PC-katalog>\t0\repo\Ramki\stanowisko
set ODB=<PC-katalog>\t0\repo\Ramki\etap3\odbior_koncowy
set ROB=<PC-katalog>\koordynator\robocze\odbior\T6
echo t6_arkusz START %DATE% %TIME% >> %ROB%\kody.txt
call %K%\Polecenie.cmd narzedzia\arkusz_syntetyczny.py --wierszy 30000 --zapytan 200 > %ROB%\t6_arkusz.txt 2>&1 < NUL
echo t6_arkusz KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo t6_excel START %DATE% %TIME% >> %ROB%\kody.txt
call %K%\Polecenie.cmd %ODB%\narzedzia\pytest_instalacja.py --st %ST% --wynik %ROB%\t6_zrodlo_kodu.txt -- %ST%\testy\test_excel.py -q -s -rA -p no:cacheprovider --rootdir %ST% > %ROB%\t6_excel.log 2>&1 < NUL
echo t6_excel KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo t6_aplikacja START %DATE% %TIME% >> %ROB%\kody.txt
call %K%\Polecenie.cmd %ODB%\narzedzia\pytest_instalacja.py --st %ST% --wynik %ROB%\t6_zrodlo_kodu_2.txt -- %ST%\testy\test_aplikacja_rano.py -q -s -rA -p no:cacheprovider --rootdir %ST% -k "test_k3_excel_pytaj or test_k3_excel_cien" > %ROB%\t6_aplikacja.log 2>&1 < NUL
echo t6_aplikacja KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo t6 KONIEC %DATE% %TIME% >> %ROB%\kody.txt
