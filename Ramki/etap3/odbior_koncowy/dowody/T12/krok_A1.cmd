@echo off
rem T12 przygotowanie c.d.: T0 kroki 5 i 7 w odbior_t12, potem T12 krok 1 (stan przed aktualizacja)
set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe
set QT_QPA_PLATFORM=offscreen
set ROB=<PC-katalog>\koordynator\robocze\odbior\T12
set K=<PC-katalog>\t0\odbior_t12\Stanowisko
set P1=<PC-katalog>\t0\odbior\paczka_0.3.1
set ODB=<PC-katalog>\t0\repo\Ramki\etap3\odbior_koncowy
echo P5_zainstaluj_N_2 START %date% %time% >> %ROB%\czasy.txt
call %P1%\zainstaluj.cmd /katalog %K% /python %PY% /bez-sieci /bez-pauzy < NUL > %ROB%\t12_P5_zainstaluj_N_2.log 2>&1
echo P5_zainstaluj_N_2 KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo P5_zainstaluj_N_2 KONIEC %date% %time% >> %ROB%\czasy.txt
echo P7a_start_atrapa START %date% %time% >> %ROB%\czasy.txt
call %K%\Stanowisko.cmd --atrapa --zamknij-po 5 < NUL > %ROB%\t12_P7a_start_atrapa.log 2>&1
echo P7a_start_atrapa KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo P7a_start_atrapa KONIEC %date% %time% >> %ROB%\czasy.txt
echo P7b_start START %date% %time% >> %ROB%\czasy.txt
call %K%\Stanowisko.cmd --zamknij-po 20 < NUL > %ROB%\t12_P7b_start.log 2>&1
echo P7b_start KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo P7b_start KONIEC %date% %time% >> %ROB%\czasy.txt
rem --- T12 krok 1: stan przed aktualizacja
certutil -hashfile %K%\ustawienia.toml SHA256 > %ROB%\t12_ustawienia_przed.txt 2>&1
echo A1_certutil_ustawienia KOD=%ERRORLEVEL% >> %ROB%\kody.txt
call %K%\Wersje.cmd /bez-pauzy < NUL > %ROB%\t12_A1_wersje_przed.log 2>&1
echo A1_wersje KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo == stan bazy PRZED aktualizacja %date% %time% > %ROB%\t12_A1_baza_przed.txt
%PY% -I %ODB%\narzedzia\sql_odczyt.py --baza %K%\dane\stanowisko.sqlite "SELECT count(*) FROM skany" >> %ROB%\t12_A1_baza_przed.txt 2>&1
echo A1_sql_skany KOD=%ERRORLEVEL% >> %ROB%\kody.txt
%PY% -I %ODB%\narzedzia\sql_odczyt.py --baza %K%\dane\stanowisko.sqlite "SELECT count(*) FROM zdarzenia" >> %ROB%\t12_A1_baza_przed.txt 2>&1
echo A1_sql_zdarzenia KOD=%ERRORLEVEL% >> %ROB%\kody.txt
%PY% -I %ODB%\narzedzia\sql_odczyt.py --baza %K%\dane\stanowisko.sqlite "SELECT user_version FROM pragma_user_version" >> %ROB%\t12_A1_baza_przed.txt 2>&1
echo A1_sql_user_version KOD=%ERRORLEVEL% >> %ROB%\kody.txt
certutil -hashfile %K%\dane\stanowisko.sqlite SHA256 >> %ROB%\t12_A1_baza_przed.txt 2>&1
echo rozmiar i skrot tresci bez naglowka (bajty od 100.): >> %ROB%\t12_A1_baza_przed.txt
%PY% -I -c "import hashlib,sys;d=open(sys.argv[1],'rb').read();print(len(d),hashlib.sha256(d[100:]).hexdigest())" %K%\dane\stanowisko.sqlite >> %ROB%\t12_A1_baza_przed.txt 2>&1
echo pliki w dane\kopie: >> %ROB%\t12_A1_baza_przed.txt
dir /b %K%\dane\kopie >> %ROB%\t12_A1_baza_przed.txt 2>&1
type %K%\wersja_biezaca.txt >> %ROB%\t12_A1_baza_przed.txt
exit /b 0
