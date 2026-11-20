@echo off
rem Instalacja albo aktualizacja programu "Stanowisko" z rozpakowanej paczki wydania (E3-A11i, wariant B).
rem   zainstaluj.cmd [/katalog KATALOG] [/python SCIEZKA\python.exe] [/skrot] [/testy] [/bez-sieci] [/bez-pauzy]
rem Bez opcji: katalog C:\Stanowisko, Python 3.12 szukany sam. Na koncu okno czeka na klawisz - chyba ze podano /bez-pauzy.
rem Opis krokow i komunikatow: program\instrukcje\instalacja_i_aktualizacja.md
setlocal
set "PACZKA=%~dp0"
set "PY="
set "SKAD="
set "PAUZA=1"
rem Zmienne innego programu nie moga zepsuc startu Pythona (PYTHONHOME) ani podsunac mu cudzych pakietow (PYTHONPATH).
set "PYTHONHOME="
set "PYTHONPATH="

:argumenty
if "%~1"=="" goto :szukaj
if /i "%~1"=="/python" set "PY=%~2"
if /i "%~1"=="--python" set "PY=%~2"
if /i "%~1"=="/bez-pauzy" set "PAUZA="
if /i "%~1"=="--bez-pauzy" set "PAUZA="
shift
goto :argumenty

:szukaj
if not exist "%PACZKA%program\instalacja\instalator.py" goto :brak_instalatora
set "SKAD=opcja /python"
if not "%PY%"=="" goto :wskazany
set "SKAD=zmienna STANOWISKO_PYTHON"
set "PY=%STANOWISKO_PYTHON%"
if not "%PY%"=="" goto :wskazany
rem Kolejnosc szukania: py -3.12, typowe miejsca instalacji z python.org, python z PATH (kazdy kandydat musi byc 3.12).
for /f "delims=" %%P in ('py -3.12 -I -c "import sys; print(sys.executable)" 2^>nul') do call :kandydat "%%P"
call :kandydat "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
call :kandydat "%ProgramFiles%\Python312\python.exe"
call :kandydat "%SystemDrive%\Python312\python.exe"
if not "%PY%"=="" goto :instaluj
for /f "delims=" %%P in ('python -I -c "import sys; print(sys.executable)" 2^>nul') do call :kandydat "%%P"
if not "%PY%"=="" goto :instaluj
echo BLAD: nie znaleziono Pythona 3.12 (sprawdzono: py -3.12, typowe katalogi Python312, polecenie python).
echo CO ZROBIC: zainstaluj Pythona 3.12 (64-bit; sprawdzona wersja 3.12.10) z python.org albo wskaz go: zainstaluj.cmd /python SCIEZKA\python.exe
goto :blad_pythona

:wskazany
if exist "%PY%" goto :wskazany_jest
echo BLAD: brak Pythona - %SKAD% wskazuje plik, ktorego nie ma: "%PY%"
echo CO ZROBIC: podaj pelna sciezke do python.exe wersji 3.12, np. zainstaluj.cmd /python C:\Python312\python.exe
goto :blad_pythona
:wskazany_jest
"%PY%" -I -c "import sys; sys.exit(0 if sys.version_info[:2] == (3, 12) else 1)" >nul 2>nul
if not errorlevel 1 goto :instaluj
echo BLAD: zla wersja Pythona - %SKAD% wskazuje interpreter inny niz 3.12 (albo taki, ktory sie nie uruchamia): "%PY%"
echo CO ZROBIC: program wymaga Pythona 3.12 (64-bit; sprawdzona wersja 3.12.10) - zainstaluj go z python.org i wskaz opcja /python.
goto :blad_pythona

:instaluj
set "PYTHONUTF8=1"
"%PY%" -I "%PACZKA%program\instalacja\instalator.py" zainstaluj --paczka "%PACZKA%." --python "%PY%" %*
set "KOD=%errorlevel%"
goto :koniec

:brak_instalatora
echo BLAD: w paczce brakuje pliku program\instalacja\instalator.py.
echo CO ZROBIC: rozpakuj CALA paczke wydania (wszystkie pliki) i uruchom zainstaluj.cmd z rozpakowanego katalogu.
echo INSTALACJA: NIEUDANA (kod 3) - niczego nie zmieniono.
set "KOD=3"
goto :koniec

:blad_pythona
echo INSTALACJA: NIEUDANA (kod 4) - niczego nie zmieniono.
set "KOD=4"

:koniec
if defined PAUZA pause
exit /b %KOD%

:kandydat
if not "%PY%"=="" exit /b 0
if not exist "%~1" exit /b 0
"%~1" -I -c "import sys; sys.exit(0 if sys.version_info[:2] == (3, 12) else 1)" >nul 2>nul
if not errorlevel 1 set "PY=%~1"
exit /b 0
