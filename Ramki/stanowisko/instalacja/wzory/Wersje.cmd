@echo off
rem Lista zainstalowanych wersji; Wersje.cmd /usun WERSJA usuwa wersje, ktora nie jest biezaca ani poprzednia.
rem   /bez-pauzy      na koncu nie czekaj na klawisz
rem Plik zapisany przez instalator (wzor: program\instalacja\wzory) - nie zmieniaj; ustawienia sa w ustawienia.toml.
setlocal
set "KAT=%~dp0"
set "PAUZA=1"
:argumenty
if "%~1"=="" goto :start
if /i "%~1"=="/bez-pauzy" set "PAUZA="
if /i "%~1"=="--bez-pauzy" set "PAUZA="
shift
goto :argumenty
:start
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
"%W%\venv\Scripts\python.exe" -I "%W%\program\instalacja\instalator.py" wersje --katalog "%KAT%." %*
set "KOD=%errorlevel%"
if defined PAUZA pause
exit /b %KOD%

:brak_wersji
echo BLAD: w tym katalogu nie ma gotowej wersji biezacej programu (wersja_biezaca.txt: "%WERSJA%").
echo CO ZROBIC: uruchom zainstaluj.cmd z rozpakowanej paczki wydania.
if defined PAUZA pause
exit /b 4
