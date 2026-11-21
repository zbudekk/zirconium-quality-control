@echo off
rem Stan instalacji i bazy (tylko odczyt). Uzycie: call stan.cmd <katalog instalacji> <plik wyniku> "<opis>"
set SK=%~1
set SW=%~2
set SPY=<PC>\AppData\Local\Programs\Python\Python312\python.exe
set SSQL=%SPY% -I <PC-katalog>\t0\repo2\Ramki\etap3\odbior_koncowy\narzedzia\sql_odczyt.py --baza
set SSKROT=%SPY% -I -c "import hashlib,sys;d=open(sys.argv[1],'rb').read();print(len(d),hashlib.sha256(d[100:]).hexdigest())"
echo. >> %SW%
echo ===== STAN %~3 %date% %time% >> %SW%
echo wersja_biezaca: >> %SW%
type %SK%\wersja_biezaca.txt >> %SW% 2>&1
echo. >> %SW%
echo wersja_poprzednia: >> %SW%
type %SK%\wersja_poprzednia.txt >> %SW% 2>&1
echo. >> %SW%
echo -- ustawienia.toml SHA-256: >> %SW%
certutil -hashfile %SK%\ustawienia.toml SHA256 | findstr /v /c:"CertUtil" /c:"SHA256 hash" >> %SW% 2>&1
echo -- baza dane\stanowisko.sqlite (SHA-256; rozmiar i skrot bez naglowka; user_version; zdarzenia; skany): >> %SW%
certutil -hashfile %SK%\dane\stanowisko.sqlite SHA256 | findstr /v /c:"CertUtil" /c:"SHA256 hash" >> %SW% 2>&1
%SSKROT% %SK%\dane\stanowisko.sqlite >> %SW% 2>&1 < NUL
%SSQL% %SK%\dane\stanowisko.sqlite "SELECT user_version FROM pragma_user_version" >> %SW% 2>&1 < NUL
%SSQL% %SK%\dane\stanowisko.sqlite "SELECT count(*) FROM zdarzenia" >> %SW% 2>&1 < NUL
%SSQL% %SK%\dane\stanowisko.sqlite "SELECT count(*) FROM skany" >> %SW% 2>&1 < NUL
echo -- pliki w dane\kopie: >> %SW%
dir /b %SK%\dane\kopie >> %SW% 2>&1
for %%F in (%SK%\dane\kopie\*.sqlite) do (
  echo -- kopia %%~nxF rozmiar %%~zF >> %SW%
  certutil -hashfile %%F SHA256 | findstr /v /c:"CertUtil" /c:"SHA256 hash" >> %SW% 2>&1
  %SSKROT% %%F >> %SW% 2>&1 < NUL
  %SSQL% %%F "SELECT user_version FROM pragma_user_version" >> %SW% 2>&1 < NUL
  %SSQL% %%F "SELECT count(*) FROM zdarzenia" >> %SW% 2>&1 < NUL
  %SSQL% %%F "SELECT count(*) FROM skany" >> %SW% 2>&1 < NUL
)
echo -- pliki w dane (inne kopie obok bazy): >> %SW%
dir /b %SK%\dane\*.sqlite >> %SW% 2>&1
echo -- katalog instalacji: >> %SW%
dir /b %SK% >> %SW% 2>&1
echo -- katalog wersje: >> %SW%
dir /b %SK%\wersje >> %SW% 2>&1
exit /b 0
