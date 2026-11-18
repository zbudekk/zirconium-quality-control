@echo off
rem Program "Stanowisko" (etap 3): folder skanera -> analiza -> mapa plytki i decyzje technika. Wymaga Pythona 3.12 (py -3.12) i pip install -r requirements.txt
rem Opcje: --ustawienia PLIK (inny plik ustawien), --atrapa (pokaz na danych sztucznych, bez skanera)
cd /d "%~dp0"
set PYTHONUTF8=1
py -3.12 -m stanowisko.aplikacja %*
set KOD=%errorlevel%
rem kod 3 = program juz dziala (drugi egzemplarz) - komunikat byl w okienku, konsola nie czeka
if "%KOD%"=="3" exit /b 3
if not "%KOD%"=="0" pause
