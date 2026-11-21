@echo off
rem T12 czesc B na wydaniu 0.3.3: paczka probna 0.3.9-migracja (schemat + 1), aktualizacja, powrot po migracji
set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe
set QT_QPA_PLATFORM=offscreen
set ROB=<PC-katalog>\koordynator\robocze\odbior2\final\T12
set RB=%ROB%\robocze
set KB=%RB%\K_B
set PM=%RB%\paczka_M
set P1=<PC-katalog>\t0\odbior2_t12\paczka_0.3.3
set REPO=<PC-katalog>\t0\repo2
set ODB=%REPO%\Ramki\etap3\odbior_koncowy
set S=%ROB%\t12_B_stany.txt
echo B START %date% %time% >> %ROB%\czasy.txt
echo == czesc B: stany instalacji %KB% > %S%
if not exist %P1%\zainstaluj.cmd exit /b 2

rem --- krok 1: budowa paczki probnej i rozpakowanie (tar.exe systemowy)
echo B1_budowa START %date% %time% >> %ROB%\czasy.txt
%PY% -I %ODB%\narzedzia\t12_paczka_migracja.py --repo %REPO% --roboczy %RB% --wersja 0.3.9-migracja --wyjscie %RB%\paczki --kola <PC-katalog>\wydania\kola > %ROB%\t12_B_paczka.txt 2>&1 < NUL
echo B1_budowa_paczki KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo B1_budowa KONIEC %date% %time% >> %ROB%\czasy.txt
mkdir %PM%
mkdir %RB%\wej\eksport
mkdir %RB%\wej\Cyrkon
mkdir %RB%\wej\Prywatne
mkdir %RB%\wej\millbox
C:\Windows\System32\tar.exe -xf %RB%\paczki\Stanowisko_0.3.9-migracja.zip -C %PM% >> %ROB%\t12_B_paczka.txt 2>&1
echo B1_rozpakowanie KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo B1_rozpakowanie KONIEC %date% %time% >> %ROB%\czasy.txt
if not exist %PM%\zainstaluj.cmd exit /b 2

rem --- krok 2: instalacja wersji N (0.3.3) w nowym katalogu
echo B2a_zainstaluj START %date% %time% >> %ROB%\czasy.txt
call %P1%\zainstaluj.cmd /katalog %KB% /python %PY% /bez-sieci /bez-pauzy < NUL > %ROB%\t12_B_2a.log 2>&1
echo B2a_zainstaluj_N_1 KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo B2a_zainstaluj KONIEC %date% %time% >> %ROB%\czasy.txt
powershell -NoProfile -ExecutionPolicy Bypass -File %ROB%\edytuj.ps1 -Plik %KB%\ustawienia.toml -Wej <PC-katalog>/koordynator/robocze/odbior2/final/T12/robocze/wej > %ROB%\t12_B_2_edycja.log 2>&1
echo B2_edycja_ustawien KOD=%ERRORLEVEL% >> %ROB%\kody.txt
call %P1%\zainstaluj.cmd /katalog %KB% /python %PY% /bez-sieci /bez-pauzy < NUL > %ROB%\t12_B_2b.log 2>&1
echo B2b_zainstaluj_N_2 KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo B2b_zainstaluj KONIEC %date% %time% >> %ROB%\czasy.txt

rem --- krok 3: baza z wpisami
call %KB%\Stanowisko.cmd --zamknij-po 5 < NUL > %ROB%\t12_B_3a.log 2>&1
echo B3a_start KOD=%ERRORLEVEL% >> %ROB%\kody.txt
call %KB%\Stanowisko.cmd --zamknij-po 5 < NUL > %ROB%\t12_B_3b.log 2>&1
echo B3b_start KOD=%ERRORLEVEL% >> %ROB%\kody.txt
call %ROB%\stan.cmd %KB% %S% "po kroku 3 (PRZED aktualizacja probna)"

rem --- krok 4: aktualizacja paczka probna
echo B4_zainstaluj_M START %date% %time% >> %ROB%\czasy.txt
call %PM%\zainstaluj.cmd /katalog %KB% /python %PY% /bez-sieci /bez-pauzy < NUL > %ROB%\t12_B_4.log 2>&1
echo B4_zainstaluj_M KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo B4_zainstaluj_M KONIEC %date% %time% >> %ROB%\czasy.txt
call %ROB%\stan.cmd %KB% %S% "po kroku 4 (c1: po aktualizacji, przed startem wersji probnej)"

rem --- krok 5: pierwszy start wersji probnej (migracja)
call %KB%\Stanowisko.cmd --zamknij-po 5 < NUL > %ROB%\t12_B_5.log 2>&1
echo B5_start_M KOD=%ERRORLEVEL% >> %ROB%\kody.txt
call %ROB%\stan.cmd %KB% %S% "po kroku 5 (c2: po pierwszym starcie wersji probnej)"

rem --- krok 6: powrot bez zgody na przywrocenie kopii (oczekiwany kod 8)
call %KB%\Wroc_do_poprzedniej.cmd /tak /bez-pauzy < NUL > %ROB%\t12_B_6.log 2>&1
echo B6_wroc_tak KOD=%ERRORLEVEL% >> %ROB%\kody.txt
call %ROB%\stan.cmd %KB% %S% "po kroku 6 (powrot bez zgody - oczekiwany kod 8)"

rem --- krok 7: powrot z przywroceniem kopii
echo B7_wroc_przywroc START %date% %time% >> %ROB%\czasy.txt
call %KB%\Wroc_do_poprzedniej.cmd /przywroc-kopie /bez-pauzy < NUL > %ROB%\t12_B_7.log 2>&1
echo B7_wroc_przywroc_kopie KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo B7_wroc_przywroc KONIEC %date% %time% >> %ROB%\czasy.txt
call %ROB%\stan.cmd %KB% %S% "po kroku 7 (e: po powrocie z przywroceniem kopii)"

rem --- krok 8: start wersji N na przywroconej bazie
call %KB%\Stanowisko.cmd --zamknij-po 5 < NUL > %ROB%\t12_B_8.log 2>&1
echo B8_start_N KOD=%ERRORLEVEL% >> %ROB%\kody.txt
call %ROB%\stan.cmd %KB% %S% "po kroku 8 (start wersji N na przywroconej bazie)"
call %KB%\Wersje.cmd /bez-pauzy < NUL >> %S% 2>&1
echo B KONIEC %date% %time% >> %ROB%\czasy.txt
exit /b 0
