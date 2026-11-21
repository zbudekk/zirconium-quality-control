@echo off
rem Proba ramki swietlnej z komputera - menu (narzedzie dnia sprzetu, E3-S1). Program Stanowisko ma byc ZAMKNIETY.
rem Obserwacje trafiaja do katalogu ..\wyniki\ramka obok tego katalogu.
setlocal
set "ST=C:\Stanowisko"
if not "%STANOWISKO_KATALOG%"=="" set "ST=%STANOWISKO_KATALOG%"
set "TU=%~dp0"
set "WYN=%TU%..\wyniki\ramka"
if exist "%ST%\Polecenie.cmd" goto :jest
echo BLAD: nie ma pliku %ST%\Polecenie.cmd - najpierw zainstaluj program Stanowisko (zainstaluj.cmd z paczki).
pause
exit /b 4
:jest
if not exist "%WYN%" mkdir "%WYN%"
set "ADRES="
if exist "%WYN%\adres_ramki.txt" set /p ADRES=<"%WYN%\adres_ramki.txt"
echo Adres ramki w sieci, np. ramka-w.local albo <adres-IP>
set "NOWY="
set /p NOWY=Adres [%ADRES%] (sam Enter = bez zmiany): 
if not "%NOWY%"=="" set "ADRES=%NOWY%"
if not "%ADRES%"=="" goto :menu
echo Nie podano adresu ramki.
pause
exit /b 1
:menu
>"%WYN%\adres_ramki.txt" echo %ADRES%
set "PORT=8765"
if not "%RAMKA_PORT%"=="" set "PORT=%RAMKA_PORT%"
echo.
echo ===== RAMKA %ADRES% =====
echo 1 = czy ramka odpowiada i jaka plytke czyta
echo 2 = test diod (cala matryca, 8 sekund)
echo 3 = odczyt numeru plytek przez 5 minut (kazda zmiana do pliku)
echo 4 = gniazda: wszystkie naraz
echo 5 = gniazda: po kolei, jedno naraz
echo 0 = koniec
set "W="
set /p W=Wybierz cyfre i Enter: 
if "%W%"=="0" exit /b 0
if "%W%"=="1" call "%ST%\Polecenie.cmd" "%TU%ramka_proba.py" stan --adres %ADRES% --port %PORT%
if "%W%"=="2" call "%ST%\Polecenie.cmd" "%TU%ramka_proba.py" test-led --adres %ADRES% --port %PORT%
if "%W%"=="3" call "%ST%\Polecenie.cmd" "%TU%ramka_proba.py" plytki --adres %ADRES% --port %PORT% --czas 300 --zapis "%WYN%"
if "%W%"=="4" goto :gniazda
if "%W%"=="5" goto :gniazda
goto :menu
:gniazda
set "UKLAD=wieczorna"
set /p UKLAD=Uklad plytki: wieczorna / poranna / wieczorna_r54 / poranna_r54 [%UKLAD%]: 
set "DX=0"
set "DY=0"
set /p DX=Przesuniecie w prawo, w diodach (sam Enter = 0; w lewo = liczba ujemna): 
set /p DY=Przesuniecie w dol, w diodach (sam Enter = 0; w gore = liczba ujemna): 
set "TRYB="
if "%W%"=="4" set "TRYB=--wszystkie"
call "%ST%\Polecenie.cmd" "%TU%ramka_proba.py" gniazda --adres %ADRES% --port %PORT% --uklad %UKLAD% %TRYB% --przesun %DX% %DY% --zapis "%WYN%"
goto :menu
