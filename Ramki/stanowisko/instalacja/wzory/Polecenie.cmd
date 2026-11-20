@echo off
rem Python wersji biezacej w katalogu programu, np. Polecenie.cmd -m stanowisko.dzien_skanera albo Polecenie.cmd narzedzia\symulator_skanera.py
rem Plik zapisany przez instalator (wzor: program\instalacja\wzory) - nie zmieniaj; ustawienia sa w ustawienia.toml.
setlocal
set "KAT=%~dp0"
set "WERSJA="
if exist "%KAT%wersja_biezaca.txt" set /p WERSJA=<"%KAT%wersja_biezaca.txt"
if "%WERSJA%"=="" goto :brak_wersji
set "W=%KAT%wersje\%WERSJA%"
if not exist "%W%\venv\Scripts\python.exe" goto :brak_wersji
if exist "%W%\NIEDOKONCZONA.txt" goto :brak_wersji
set "PYTHONUTF8=1"
set "PYTHONDONTWRITEBYTECODE=1"
set "PYTHONNOUSERSITE=1"
set "PYTHONPATH="
set "PYTHONHOME="
cd /d "%W%\program"
"%W%\venv\Scripts\python.exe" %*
exit /b %errorlevel%

:brak_wersji
echo BLAD: w tym katalogu nie ma gotowej wersji biezacej programu (wersja_biezaca.txt: "%WERSJA%").
echo CO ZROBIC: uruchom zainstaluj.cmd z rozpakowanej paczki wydania.
if "%~1"=="" pause
exit /b 4
