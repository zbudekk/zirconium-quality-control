@echo off
rem Okno "Dzien skanera - krok po kroku": zbiera pierwsze skany i dane z programu skanera (kopiuje, niczego nie kasuje).
rem Wymaga Pythona 3.12 (py -3.12) i pip install -r requirements.txt. Sesje: dane\dzien_skanera\<data_godzina>\
rem Sprawdzenie paczki bez okna: uruchom_dzien_skanera.bat --sprawdz <folder sesji albo plik zip>
rem TYLKO kopia repo. W instalacji z paczki wydania tego pliku nie ma: uruchom Dzien_skanera.cmd z katalogu instalacji
rem (np. C:\Stanowisko\Dzien_skanera.cmd); sesje sa wtedy w <katalog instalacji>\dane\dzien_skanera\<data_godzina>\
cd /d "%~dp0"
set PYTHONUTF8=1
py -3.12 -m stanowisko.dzien_skanera %*
if errorlevel 1 pause
