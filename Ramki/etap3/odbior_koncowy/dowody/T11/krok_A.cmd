@echo off
rem T11 czesc A: krok 1 (auto_uklad na 40 skanach *_r54) i krok 4 (testy "zly uklad"): polecenie planu doslownie + to samo przez pytest_instalacja.py
set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe
set QT_QPA_PLATFORM=offscreen
set ROB=<PC-katalog>\koordynator\robocze\odbior\T11
set K=<PC-katalog>\t0\odbior\Stanowisko
set ST=<PC-katalog>\t0\repo\Ramki\stanowisko
set ODB=<PC-katalog>\t0\repo\Ramki\etap3\odbior_koncowy
echo A1 START %date% %time% >> %ROB%\czasy.txt
call %K%\Polecenie.cmd narzedzia\auto_uklad.py --skany <PC-katalog>\app\dane_ref\syntetyczne_r54_P2 <PC-katalog>\app\dane_ref\syntetyczne_r54_P3a --wyjscie %ROB%\t11_auto --procesy 1 --ustawienia %K%\ustawienia.toml < NUL > %ROB%\t11_auto_uklad.log 2>&1
echo A1 auto_uklad KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo A1 KONIEC %date% %time% >> %ROB%\czasy.txt
echo A4 START %date% %time% >> %ROB%\czasy.txt
call %K%\Polecenie.cmd -m pytest %ST%\testy\test_session_wieczor.py %ST%\testy\test_straznik.py %ST%\testy\test_kontroler_api.py %ST%\testy\test_auto_uklad.py -q -rA -p no:cacheprovider --rootdir %ST% -k "niezgodny_uklad or niezgodna_z_ukladem or auto or innego_ukladu" < NUL > %ROB%\t11_testy.log 2>&1
echo A4 testy_polecenie_planu KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo A4 KONIEC %date% %time% >> %ROB%\czasy.txt
echo A4i START %date% %time% >> %ROB%\czasy.txt
call %K%\Polecenie.cmd %ODB%\narzedzia\pytest_instalacja.py --st %ST% --wynik %ROB%\t11_testy_zrodlo_kodu.txt -- %ST%\testy\test_session_wieczor.py %ST%\testy\test_straznik.py %ST%\testy\test_kontroler_api.py %ST%\testy\test_auto_uklad.py -q -rA -p no:cacheprovider --rootdir %ST% -k "niezgodny_uklad or niezgodna_z_ukladem or auto or innego_ukladu" < NUL > %ROB%\t11_testy_instalacja.log 2>&1
echo A4i testy_pytest_instalacja KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo A4i KONIEC %date% %time% >> %ROB%\czasy.txt
exit /b 0