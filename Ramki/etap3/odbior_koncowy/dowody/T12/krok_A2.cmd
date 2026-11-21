@echo off
rem T12 czesc A kroki 2 i 3: aktualizacja 0.3.1 -> 0.3.2 JEDNYM poleceniem, kontrole
set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe
set QT_QPA_PLATFORM=offscreen
set ROB=<PC-katalog>\koordynator\robocze\odbior\T12
set K=<PC-katalog>\t0\odbior_t12\Stanowisko
set P2=<PC-katalog>\t0\odbior_t12\paczka_0.3.2
set ODB=<PC-katalog>\t0\repo\Ramki\etap3\odbior_koncowy
set SQL=%PY% -I %ODB%\narzedzia\sql_odczyt.py --baza
set SKROT=%PY% -I -c "import hashlib,sys;d=open(sys.argv[1],'rb').read();print(len(d),hashlib.sha256(d[100:]).hexdigest())"
echo A2_zainstaluj_N1 START %date% %time% >> %ROB%\czasy.txt
call %P2%\zainstaluj.cmd /katalog %K% /python %PY% /bez-sieci /bez-pauzy < NUL > %ROB%\t12_zainstaluj_N1.log 2>&1
echo A2_zainstaluj_N1 KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo A2_zainstaluj_N1 KONIEC %date% %time% >> %ROB%\czasy.txt
set W=%ROB%\t12_A2_baza_po_aktualizacji.txt
echo == stan PO aktualizacji, PRZED pierwszym startem 0.3.2: %date% %time% > %W%
echo wersja_biezaca.txt: >> %W%
type %K%\wersja_biezaca.txt >> %W%
echo wersja_poprzednia.txt: >> %W%
type %K%\wersja_poprzednia.txt >> %W%
echo -- baza: >> %W%
certutil -hashfile %K%\dane\stanowisko.sqlite SHA256 >> %W% 2>&1
%SKROT% %K%\dane\stanowisko.sqlite >> %W% 2>&1
echo -- pliki w dane\kopie: >> %W%
dir /b %K%\dane\kopie >> %W% 2>&1
for %%F in (%K%\dane\kopie\*.sqlite) do (
  echo -- kopia %%~nxF rozmiar %%~zF >> %W%
  certutil -hashfile %%F SHA256 >> %W% 2>&1
  %SKROT% %%F >> %W% 2>&1
  %SQL% %%F "SELECT user_version FROM pragma_user_version" >> %W% 2>&1
  %SQL% %%F "SELECT count(*) FROM zdarzenia" >> %W% 2>&1
  %SQL% %%F "SELECT count(*) FROM skany" >> %W% 2>&1
)
echo A3_samokontrola START %date% %time% >> %ROB%\czasy.txt
call %K%\Samokontrola.cmd --bez-sieci < NUL > %ROB%\t12_A3_samokontrola_N1.log 2>&1
echo A3_samokontrola_N1 KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo A3_start START %date% %time% >> %ROB%\czasy.txt
call %K%\Stanowisko.cmd --zamknij-po 20 < NUL > %ROB%\t12_A3_start_N1.log 2>&1
echo A3_start_N1 KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo A3_start KONIEC %date% %time% >> %ROB%\czasy.txt
certutil -hashfile %K%\ustawienia.toml SHA256 > %ROB%\t12_ustawienia_po_N1.txt 2>&1
call %K%\Wersje.cmd /bez-pauzy < NUL > %ROB%\t12_A3_wersje_po_N1.log 2>&1
echo A3_wersje KOD=%ERRORLEVEL% >> %ROB%\kody.txt
set W=%ROB%\t12_A3_baza_po_starcie_N1.txt
echo == stan PO starcie programu 0.3.2: %date% %time% > %W%
%SQL% %K%\dane\stanowisko.sqlite "SELECT count(*) FROM skany" >> %W% 2>&1
%SQL% %K%\dane\stanowisko.sqlite "SELECT count(*) FROM zdarzenia" >> %W% 2>&1
%SQL% %K%\dane\stanowisko.sqlite "SELECT user_version FROM pragma_user_version" >> %W% 2>&1
certutil -hashfile %K%\dane\stanowisko.sqlite SHA256 >> %W% 2>&1
%SKROT% %K%\dane\stanowisko.sqlite >> %W% 2>&1
dir /b %K%\dane\kopie >> %W% 2>&1
exit /b 0
