@echo off
rem Proba ramki swietlnej z komputera - menu (narzedzie dnia sprzetu, E3-S1). Program Stanowisko ma byc ZAMKNIETY.
rem Obserwacje trafiaja do katalogu ..\wyniki\ramka obok tego katalogu.
rem Dwuklik = menu z pytaniami. Bez pytan (jedno polecenie i koniec):
rem   ramka.cmd ADRES WYBOR [UKLAD DX DY]      np.  ramka.cmd <adres-IP> 1     albo  ramka.cmd ramka-w.local 4 wieczorna 0 0
setlocal
set "ST=C:\Stanowisko"
if not "%STANOWISKO_KATALOG%"=="" set "ST=%STANOWISKO_KATALOG%"
set "TU=%~dp0"
set "WYN=%TU%..\wyniki\ramka"
set "PORT=8765"
if not "%RAMKA_PORT%"=="" set "PORT=%RAMKA_PORT%"
set "KOD=0"
set "PUSTE=0"
if exist "%ST%\Polecenie.cmd" goto :jest
echo BLAD: nie ma pliku %ST%\Polecenie.cmd - najpierw zainstaluj program Stanowisko (zainstaluj.cmd z paczki).
pause
exit /b 4
:jest
if not exist "%WYN%" mkdir "%WYN%"
set "ADRES=%~1"
set "W=%~2"
if not "%W%"=="" goto :wykonaj
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
echo.
echo ===== RAMKA %ADRES% =====
echo 1 = czy ramka odpowiada i jaka plytke czyta
echo 2 = test diod: cala matryca, 8 sekund
echo 3 = odczyt numeru plytek przez 5 minut, kazda zmiana do pliku
echo 4 = gniazda: wszystkie naraz
echo 5 = gniazda: po kolei, jedno naraz
echo 6 = klawiatura ramki porannej, 2 minuty
echo 0 = koniec
set "W="
set /p W=Wybierz cyfre i Enter: 
if "%W%"=="" set /a PUSTE+=1
if %PUSTE% GEQ 20 exit /b 0
:wykonaj
if "%W%"=="0" exit /b 0
if "%W%"=="4" goto :gniazda
if "%W%"=="5" goto :gniazda
if "%W%"=="1" call "%ST%\Polecenie.cmd" "%TU%ramka_proba.py" stan --adres %ADRES% --port %PORT%
if "%W%"=="2" call "%ST%\Polecenie.cmd" "%TU%ramka_proba.py" test-led --adres %ADRES% --port %PORT%
if "%W%"=="3" call "%ST%\Polecenie.cmd" "%TU%ramka_proba.py" plytki --adres %ADRES% --port %PORT% --czas 300 --zapis "%WYN%"
if "%W%"=="6" call "%ST%\Polecenie.cmd" "%TU%ramka_proba.py" klawiatura --adres %ADRES% --port %PORT% --uklad poranna --czas 120 --zapis "%WYN%"
set "KOD=%errorlevel%"
goto :po
:gniazda
set "UKLAD=wieczorna"
set "DX=0"
set "DY=0"
if not "%~2"=="" goto :gniazda_z_wiersza
set /p UKLAD=Uklad plytki: wieczorna / poranna / wieczorna_r54 / poranna_r54 [%UKLAD%]: 
set /p DX=Przesuniecie w prawo, w diodach; sam Enter = 0, w lewo = liczba ujemna: 
set /p DY=Przesuniecie w dol, w diodach; sam Enter = 0, w gore = liczba ujemna: 
goto :gniazda_start
:gniazda_z_wiersza
if not "%~3"=="" set "UKLAD=%~3"
if not "%~4"=="" set "DX=%~4"
if not "%~5"=="" set "DY=%~5"
:gniazda_start
set "TRYB="
if "%W%"=="4" set "TRYB=--wszystkie"
call "%ST%\Polecenie.cmd" "%TU%ramka_proba.py" gniazda --adres %ADRES% --port %PORT% --uklad %UKLAD% %TRYB% --przesun %DX% %DY% --zapis "%WYN%"
set "KOD=%errorlevel%"
:po
if not "%~2"=="" exit /b %KOD%
goto :menu
