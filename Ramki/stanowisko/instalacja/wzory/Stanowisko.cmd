@echo off
rem Program "Stanowisko": uruchamia wersje biezaca. Opcje programu przechodza dalej, np. --atrapa, --zamknij-po 5.
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
"%W%\venv\Scripts\python.exe" -m stanowisko.aplikacja --ustawienia "%KAT%ustawienia.toml" %*
set "KOD=%errorlevel%"
rem kod 3 = program juz dziala (komunikat byl w okienku); przy innym bledzie okno czeka, gdy uruchomiono dwuklikiem
if "%KOD%"=="3" exit /b 3
if not "%KOD%"=="0" if "%~1"=="" pause
exit /b %KOD%

:brak_wersji
echo BLAD: w tym katalogu nie ma gotowej wersji biezacej programu (wersja_biezaca.txt: "%WERSJA%").
echo CO ZROBIC: uruchom zainstaluj.cmd z rozpakowanej paczki wydania.
if "%~1"=="" pause
exit /b 4
