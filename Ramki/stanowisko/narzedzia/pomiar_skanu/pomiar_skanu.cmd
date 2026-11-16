@echo off
rem T10 - pomiar wlasciwosci skanu. Uzycie: przeciagnij plik skanu (STL albo PLY) na ten plik.
rem Dwa pliki naraz (ten sam skan powtorzony bez ruszania plytki) = dodatkowo pomiar powtarzalnosci.
rem Projekty koron: folder "projekty" obok pliku skanu (pliki STL z exocad tych koron, ktore leza na plytce).
rem Wymaga programu stanowiska (dwa katalogi wyzej) i plikow pomiar_skanu.py + c_wspolne.py obok tego pliku.
rem Kopia z raporty\testy_krawedz\T10\skrypty (06.11.2026); zmienione tylko sciezki: program stanowiska jest
rem szukany wzgledem tego pliku, Python przez "py -3.12" (albo .venv programu, jesli jest).
setlocal
for %%I in ("%~dp0..\..") do set STANOWISKO=%%~fI
set PYTHONUTF8=1
set PYTHONDONTWRITEBYTECODE=1
set PYTHONPATH=%STANOWISKO%
if exist "%STANOWISKO%\.venv\Lib\site-packages\" set PYTHONPATH=%STANOWISKO%;%STANOWISKO%\.venv\Lib\site-packages
set PY=py -3.12
if exist "%STANOWISKO%\.venv\Scripts\python.exe" set PY="%STANOWISKO%\.venv\Scripts\python.exe"
if "%~1"=="" (
  echo Przeciagnij plik skanu STL na ten plik.
  pause
  exit /b 1
)
set WSP=1.22
set /p WSP=Wspolczynnik z bloku cyrkonu (np. 1.2234), Enter = 1.22:
set PROJ=
if exist "%~dp1projekty\" set PROJ=--projekty "%~dp1projekty"
set POWT=
if not "%~2"=="" set POWT=--powtorka "%~f2"
echo.
echo Licze... (zwykle 2-6 minut)
cd /d "%STANOWISKO%"
%PY% "%~dp0pomiar_skanu.py" "%~f1" --wspolczynnik %WSP% %PROJ% %POWT% --wyj "%~dpn1_pomiar"
echo.
if exist "%~dpn1_pomiar\raport.txt" start notepad "%~dpn1_pomiar\raport.txt"
pause
