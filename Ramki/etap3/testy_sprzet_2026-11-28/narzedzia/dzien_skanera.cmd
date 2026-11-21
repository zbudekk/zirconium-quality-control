@echo off
rem Okno "Dzien skanera" z instalacji programu Stanowisko (narzedzie dnia sprzetu, E3-S1).
rem Ustawienia i dane w katalogu instalacji (nie w katalogu wersji programu). Inny katalog instalacji:
rem   set STANOWISKO_KATALOG=D:\Stanowisko   przed uruchomieniem.
setlocal
set "ST=C:\Stanowisko"
if not "%STANOWISKO_KATALOG%"=="" set "ST=%STANOWISKO_KATALOG%"
if exist "%ST%\Polecenie.cmd" goto :jest
echo BLAD: nie ma pliku %ST%\Polecenie.cmd - najpierw zainstaluj program Stanowisko (zainstaluj.cmd z paczki).
pause
exit /b 4
:jest
if not exist "%ST%\dane\dzien_skanera" mkdir "%ST%\dane\dzien_skanera"
call "%ST%\Polecenie.cmd" -m stanowisko.dzien_skanera --ustawienia "%ST%\ustawienia.toml" --dane "%ST%\dane\dzien_skanera" %*
set "KOD=%errorlevel%"
if not "%KOD%"=="0" pause
exit /b %KOD%
