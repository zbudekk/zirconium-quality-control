@echo off
rem Pokaz programu "Stanowisko" na DANYCH PROBNYCH (atrapa programu: 5 plytek wieczornych, osoba "Technik A") - plan B pokazu
rem 28.11 (E3-D1 r2). Dwuklik. Uruchamia zainstalowany program tak samo jak ikona "Stanowisko" (bez okna konsoli), z opcja --atrapa.
rem Dane probne sa tylko w pamieci programu i w folderze tymczasowym Windows (qc_atrapa_...), kasowanym przy zamknieciu okna:
rem bez bazy stanowiska, bez folderu skanow i projektow. Zwykla praca: zamknij to okno krzyzykiem i kliknij ikone "Stanowisko".
rem Inny katalog instalacji: set STANOWISKO_KATALOG=D:\Stanowisko przed uruchomieniem. Dodatkowe opcje przechodza dalej.
setlocal
set "ST=C:\Stanowisko"
if not "%STANOWISKO_KATALOG%"=="" set "ST=%STANOWISKO_KATALOG%"
set "WERSJA="
if exist "%ST%\wersja_biezaca.txt" set /p WERSJA=<"%ST%\wersja_biezaca.txt"
if "%WERSJA%"=="" goto :brak
set "CFG=%ST%\wersje\%WERSJA%\venv\pyvenv.cfg"
if not exist "%CFG%" goto :brak
rem pythonw.exe interpretera bazowego wersji (wiersz "home = ..." w pyvenv.cfg) - ten sam, ktory uruchamia ikona na pulpicie
set "PYH="
for /f "usebackq tokens=1,2,*" %%a in ("%CFG%") do if /i "%%a"=="home" set "PYH=%%c"
if not exist "%PYH%\pythonw.exe" goto :z_konsola
if not exist "%ST%\start_bez_konsoli.pyw" goto :z_konsola
start "" "%PYH%\pythonw.exe" -I -B "%ST%\start_bez_konsoli.pyw" stanowisko --atrapa %*
exit /b 0

:z_konsola
rem starsza instalacja bez startu bez konsoli: zwykly start z oknem konsoli (nie zamykaj czarnego okna, dopoki pokaz trwa)
call "%ST%\Stanowisko.cmd" --atrapa %*
exit /b %errorlevel%

:brak
echo BLAD: w %ST% nie ma zainstalowanego programu "Stanowisko".
echo CO ZROBIC: najpierw instalacja - dwuklik Instaluj.cmd w rozpakowanej paczce programu.
pause
exit /b 4
