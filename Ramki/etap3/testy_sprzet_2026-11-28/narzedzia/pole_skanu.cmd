@echo off
rem Pole skanera z pliku skanu plytki: przeciagnij plik STL na ten plik (narzedzie dnia sprzetu, E3-S1 / E3-S2a).
rem Wynik: ekran + pliki ^<skan^>_^<data_godzina^>_pole.txt / .json / .png (nic sie nie nadpisuje) w katalogu ..\wyniki\pole_skanu obok tego katalogu.
setlocal
set "ST=C:\Stanowisko"
if not "%STANOWISKO_KATALOG%"=="" set "ST=%STANOWISKO_KATALOG%"
set "TU=%~dp0"
set "WYN=%TU%..\wyniki\pole_skanu"
if exist "%ST%\Polecenie.cmd" goto :jest
echo BLAD: nie ma pliku %ST%\Polecenie.cmd - najpierw zainstaluj program Stanowisko (zainstaluj.cmd z paczki).
pause
exit /b 4
:jest
if not "%~1"=="" goto :plik
echo Przeciagnij plik skanu plytki (STL) na ten plik.
pause
exit /b 1
:plik
if not exist "%WYN%" mkdir "%WYN%"
set "NR="
set /p NR=Numer wybity na plytce, cyfra 1-9 (sam Enter = nie wiem): 
set "OPCJA="
for %%D in (1 2 3 4 5 6 7 8 9) do if "%NR%"=="%%D" set "OPCJA=--numer %%D"
if not "%NR%"=="" if "%OPCJA%"=="" echo To nie jest cyfra 1-9 - licze bez numeru plytki.
echo Licze... (kilkanascie sekund)
call "%ST%\Polecenie.cmd" "%TU%pole_skanu.py" "%~f1" %OPCJA% --ustawienia "%ST%\ustawienia.toml" --wynik "%WYN%"
set "KOD=%errorlevel%"
echo.
echo Kod: %KOD% (0 = plytka rozpoznana, 3 = plytki nie rozpoznano - liczby zgrubne, 2 = blad pliku)
pause
exit /b %KOD%
