@echo off
rem T12 czesc B - UZUPELNIENIE kontroli c1 (stan zaraz po kroku 4), ktorej pierwszy przebieg nie zapisal
rem (blad pliku krok_B.cmd: "The system cannot find the batch label specified - stan"). Druga, osobna instalacja K_B2: kroki 2, 3, 4 + stan.
set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe
set QT_QPA_PLATFORM=offscreen
set ROB=<PC-katalog>\koordynator\robocze\odbior\T12
set RB=%ROB%\robocze
set KB=%RB%\K_B2
set PM=%RB%\paczka_M
set P1=<PC-katalog>\t0\odbior\paczka_0.3.1
set ODB=<PC-katalog>\t0\repo\Ramki\etap3\odbior_koncowy
set SQL=%PY% -I %ODB%\narzedzia\sql_odczyt.py --baza
set SKROT=%PY% -I -c "import hashlib,sys;d=open(sys.argv[1],'rb').read();print(len(d),hashlib.sha256(d[100:]).hexdigest())"
set S=%ROB%\t12_B_uzup_stany.txt
echo == czesc B uzupelnienie (K_B2): kontrola c1 > %S%
echo Bu2a START %date% %time% >> %ROB%\czasy.txt
call %P1%\zainstaluj.cmd /katalog %KB% /python %PY% /bez-sieci /bez-pauzy < NUL > %ROB%\t12_B_uzup_2a.log 2>&1
echo Bu2a_zainstaluj_N_1 KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo Bu2a KONIEC %date% %time% >> %ROB%\czasy.txt
powershell -NoProfile -ExecutionPolicy Bypass -File %RB%\edytuj_KB2.ps1 >> %S% 2>&1
echo Bu2_edycja_ustawien KOD=%ERRORLEVEL% >> %ROB%\kody.txt
call %P1%\zainstaluj.cmd /katalog %KB% /python %PY% /bez-sieci /bez-pauzy < NUL > %ROB%\t12_B_uzup_2b.log 2>&1
echo Bu2b_zainstaluj_N_2 KOD=%ERRORLEVEL% >> %ROB%\kody.txt
call %KB%\Stanowisko.cmd --zamknij-po 5 < NUL > %ROB%\t12_B_uzup_3a.log 2>&1
echo Bu3a_start KOD=%ERRORLEVEL% >> %ROB%\kody.txt
call %KB%\Stanowisko.cmd --zamknij-po 5 < NUL > %ROB%\t12_B_uzup_3b.log 2>&1
echo Bu3b_start KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo ===== STAN po kroku 3 (PRZED aktualizacja probna) %date% %time% >> %S%
type %KB%\wersja_biezaca.txt >> %S%
certutil -hashfile %KB%\dane\stanowisko.sqlite SHA256 | findstr /v /c:"CertUtil" /c:"SHA256 hash" >> %S% 2>&1
%SKROT% %KB%\dane\stanowisko.sqlite >> %S% 2>&1
%SQL% %KB%\dane\stanowisko.sqlite "SELECT user_version FROM pragma_user_version" >> %S% 2>&1
%SQL% %KB%\dane\stanowisko.sqlite "SELECT count(*) FROM zdarzenia" >> %S% 2>&1
echo -- pliki w dane\kopie: >> %S%
dir /b %KB%\dane\kopie >> %S% 2>&1
echo Bu4 START %date% %time% >> %ROB%\czasy.txt
call %PM%\zainstaluj.cmd /katalog %KB% /python %PY% /bez-sieci /bez-pauzy < NUL > %ROB%\t12_B_uzup_4.log 2>&1
echo Bu4_zainstaluj_M KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo Bu4 KONIEC %date% %time% >> %ROB%\czasy.txt
echo ===== STAN po kroku 4 - kontrola c1 (po aktualizacji, PRZED startem wersji probnej) %date% %time% >> %S%
type %KB%\wersja_biezaca.txt >> %S%
certutil -hashfile %KB%\dane\stanowisko.sqlite SHA256 | findstr /v /c:"CertUtil" /c:"SHA256 hash" >> %S% 2>&1
%SKROT% %KB%\dane\stanowisko.sqlite >> %S% 2>&1
%SQL% %KB%\dane\stanowisko.sqlite "SELECT user_version FROM pragma_user_version" >> %S% 2>&1
%SQL% %KB%\dane\stanowisko.sqlite "SELECT count(*) FROM zdarzenia" >> %S% 2>&1
echo -- pliki w dane\kopie: >> %S%
dir /b %KB%\dane\kopie >> %S% 2>&1
for %%F in (%KB%\dane\kopie\*.sqlite) do (
  echo -- kopia %%~nxF rozmiar %%~zF >> %S%
  certutil -hashfile %%F SHA256 | findstr /v /c:"CertUtil" /c:"SHA256 hash" >> %S% 2>&1
  %SKROT% %%F >> %S% 2>&1
  %SQL% %%F "SELECT user_version FROM pragma_user_version" >> %S% 2>&1
  %SQL% %%F "SELECT count(*) FROM zdarzenia" >> %S% 2>&1
)
echo Bu_KONIEC %date% %time% >> %ROB%\czasy.txt
exit /b 0
