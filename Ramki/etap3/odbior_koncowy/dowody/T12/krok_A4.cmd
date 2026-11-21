@echo off
rem T12 czesc A kroki 4 i 5: powrot do 0.3.1 - Wroc_do_poprzedniej.cmd z odpowiedziami: brak (NUL), N, T; kontrole po powrocie
set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe
set QT_QPA_PLATFORM=offscreen
set ROB=<PC-katalog>\koordynator\robocze\odbior\T12
set K=<PC-katalog>\t0\odbior_t12\Stanowisko
set ODB=<PC-katalog>\t0\repo\Ramki\etap3\odbior_koncowy
set SQL=%PY% -I %ODB%\narzedzia\sql_odczyt.py --baza
set SKROT=%PY% -I -c "import hashlib,sys;d=open(sys.argv[1],'rb').read();print(len(d),hashlib.sha256(d[100:]).hexdigest())"
set L=%ROB%\t12_wroc.log
echo ===== 4a: Wroc_do_poprzedniej.cmd /bez-pauzy z wejsciem NUL (brak odpowiedzi) %date% %time% > %L%
call %K%\Wroc_do_poprzedniej.cmd /bez-pauzy < NUL >> %L% 2>&1
echo A4a_wroc_brak_odpowiedzi KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo wersja_biezaca po 4a: >> %L%
type %K%\wersja_biezaca.txt >> %L%
echo ===== 4b: echo N^| Wroc_do_poprzedniej.cmd /bez-pauzy %date% %time% >> %L%
echo N| call %K%\Wroc_do_poprzedniej.cmd /bez-pauzy >> %L% 2>&1
echo A4b_wroc_N KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo wersja_biezaca po 4b: >> %L%
type %K%\wersja_biezaca.txt >> %L%
echo ===== 4c: echo T^| Wroc_do_poprzedniej.cmd /bez-pauzy %date% %time% >> %L%
echo A4c_wroc_T START %date% %time% >> %ROB%\czasy.txt
echo T| call %K%\Wroc_do_poprzedniej.cmd /bez-pauzy >> %L% 2>&1
echo A4c_wroc_T KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo A4c_wroc_T KONIEC %date% %time% >> %ROB%\czasy.txt
echo wersja_biezaca po 4c: >> %L%
type %K%\wersja_biezaca.txt >> %L%
echo wersja_poprzednia po 4c: >> %L%
type %K%\wersja_poprzednia.txt >> %L%
rem --- krok 5
call %K%\Samokontrola.cmd --bez-sieci < NUL > %ROB%\t12_A5_samokontrola_N.log 2>&1
echo A5_samokontrola_N KOD=%ERRORLEVEL% >> %ROB%\kody.txt
set W=%ROB%\t12_A5_baza_po_powrocie.txt
echo == stan PO powrocie, PRZED startem 0.3.1: %date% %time% > %W%
%SQL% %K%\dane\stanowisko.sqlite "SELECT count(*) FROM skany" >> %W% 2>&1
%SQL% %K%\dane\stanowisko.sqlite "SELECT count(*) FROM zdarzenia" >> %W% 2>&1
%SQL% %K%\dane\stanowisko.sqlite "SELECT user_version FROM pragma_user_version" >> %W% 2>&1
certutil -hashfile %K%\dane\stanowisko.sqlite SHA256 >> %W% 2>&1
%SKROT% %K%\dane\stanowisko.sqlite >> %W% 2>&1
dir /b %K%\dane\kopie >> %W% 2>&1
echo A5_start START %date% %time% >> %ROB%\czasy.txt
call %K%\Stanowisko.cmd --zamknij-po 20 < NUL > %ROB%\t12_A5_start_N.log 2>&1
echo A5_start_N KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo A5_start KONIEC %date% %time% >> %ROB%\czasy.txt
certutil -hashfile %K%\ustawienia.toml SHA256 > %ROB%\t12_ustawienia_po_powrocie.txt 2>&1
call %K%\Wersje.cmd /bez-pauzy < NUL > %ROB%\t12_A5_wersje_po_powrocie.log 2>&1
echo A5_wersje KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo == stan PO starcie 0.3.1 po powrocie: %date% %time% >> %W%
%SQL% %K%\dane\stanowisko.sqlite "SELECT count(*) FROM skany" >> %W% 2>&1
%SQL% %K%\dane\stanowisko.sqlite "SELECT count(*) FROM zdarzenia" >> %W% 2>&1
%SQL% %K%\dane\stanowisko.sqlite "SELECT user_version FROM pragma_user_version" >> %W% 2>&1
dir /b %K%\dane\kopie >> %W% 2>&1
exit /b 0
