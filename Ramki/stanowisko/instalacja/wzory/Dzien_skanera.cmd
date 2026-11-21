@echo off
rem Okno "Dzien skanera - krok po kroku" wersji biezacej: ustawienia z ustawienia.toml tego katalogu, sesje w dane\dzien_skanera
rem tego katalogu (katalog sesji podany wprost opcja --dane: takze wersja 0.3.1, po powrocie do niej, zapisuje sesje tutaj,
rem a nie w katalogu wersji; wlasne --dane podane przy uruchomieniu ma pierwszenstwo).
rem Opcje okna przechodza dalej, np. --nowa, --sprawdz <folder sesji albo plik zip>, --zamknij-po 5 (nie w wersji 0.3.1).
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
"%W%\venv\Scripts\python.exe" -m stanowisko.dzien_skanera --ustawienia "%KAT%ustawienia.toml" --dane "%KAT%dane\dzien_skanera" %*
set "KOD=%errorlevel%"
if not "%KOD%"=="0" if "%~1"=="" pause
exit /b %KOD%

:brak_wersji
echo BLAD: w tym katalogu nie ma gotowej wersji biezacej programu (wersja_biezaca.txt: "%WERSJA%").
echo CO ZROBIC: uruchom zainstaluj.cmd z rozpakowanej paczki wydania.
if "%~1"=="" pause
exit /b 4
