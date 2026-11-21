@echo off
rem T12 czesc B, PROBA 2: jak krok_B.cmd kroki 2-8, ale instalacja w KROTSZYM katalogu (proba 1: kod 6 - sciezka K_B za dluga dla wersji 0.3.9-migracja)
rem Paczka probna z proby 1 (ten sam ZIP, juz rozpakowany w robocze\paczka_M) - bez ponownej budowy.
set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe
set QT_QPA_PLATFORM=offscreen
set ROB=<PC-katalog>\koordynator\robocze\odbior2\final\T12
set RB=%ROB%\robocze
set BK=<PC-katalog>\t0\odbior2_t12\B
set KB=%BK%\K_B
set PM=%RB%\paczka_M
set P1=<PC-katalog>\t0\odbior2_t12\paczka_0.3.3
set S=%ROB%\t12_B2_stany.txt
echo BB START %date% %time% >> %ROB%\czasy.txt
echo == czesc B proba 2: stany instalacji %KB% > %S%
if not exist %P1%\zainstaluj.cmd exit /b 2
if not exist %PM%\zainstaluj.cmd exit /b 2
mkdir %BK%\wej\eksport
mkdir %BK%\wej\Cyrkon
mkdir %BK%\wej\Prywatne
mkdir %BK%\wej\millbox

rem --- krok 2: instalacja wersji N (0.3.3) w nowym katalogu
echo BB_2a_zainstaluj START %date% %time% >> %ROB%\czasy.txt
call %P1%\zainstaluj.cmd /katalog %KB% /python %PY% /bez-sieci /bez-pauzy < NUL > %ROB%\t12_B2_2a.log 2>&1
echo BB_2a_zainstaluj_N_1 KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo BB_2a_zainstaluj KONIEC %date% %time% >> %ROB%\czasy.txt
powershell -NoProfile -ExecutionPolicy Bypass -File %ROB%\edytuj.ps1 -Plik %KB%\ustawienia.toml -Wej <PC-katalog>/t0/odbior2_t12/B/wej > %ROB%\t12_B2_2_edycja.log 2>&1
echo BB_2_edycja_ustawien KOD=%ERRORLEVEL% >> %ROB%\kody.txt
call %P1%\zainstaluj.cmd /katalog %KB% /python %PY% /bez-sieci /bez-pauzy < NUL > %ROB%\t12_B2_2b.log 2>&1
echo BB_2b_zainstaluj_N_2 KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo BB_2b_zainstaluj KONIEC %date% %time% >> %ROB%\czasy.txt

rem --- krok 3: baza z wpisami
call %KB%\Stanowisko.cmd --zamknij-po 5 < NUL > %ROB%\t12_B2_3a.log 2>&1
echo BB_3a_start KOD=%ERRORLEVEL% >> %ROB%\kody.txt
call %KB%\Stanowisko.cmd --zamknij-po 5 < NUL > %ROB%\t12_B2_3b.log 2>&1
echo BB_3b_start KOD=%ERRORLEVEL% >> %ROB%\kody.txt
call %ROB%\stan.cmd %KB% %S% "po kroku 3 (PRZED aktualizacja probna)"

rem --- krok 4: aktualizacja paczka probna
echo BB_4_zainstaluj_M START %date% %time% >> %ROB%\czasy.txt
call %PM%\zainstaluj.cmd /katalog %KB% /python %PY% /bez-sieci /bez-pauzy < NUL > %ROB%\t12_B2_4.log 2>&1
echo BB_4_zainstaluj_M KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo BB_4_zainstaluj_M KONIEC %date% %time% >> %ROB%\czasy.txt
call %ROB%\stan.cmd %KB% %S% "po kroku 4 (c1: po aktualizacji, przed startem wersji probnej)"

rem --- krok 5: pierwszy start wersji probnej (migracja)
call %KB%\Stanowisko.cmd --zamknij-po 5 < NUL > %ROB%\t12_B2_5.log 2>&1
echo BB_5_start_M KOD=%ERRORLEVEL% >> %ROB%\kody.txt
call %ROB%\stan.cmd %KB% %S% "po kroku 5 (c2: po pierwszym starcie wersji probnej)"

rem --- krok 6: powrot bez zgody na przywrocenie kopii (oczekiwany kod 8)
call %KB%\Wroc_do_poprzedniej.cmd /tak /bez-pauzy < NUL > %ROB%\t12_B2_6.log 2>&1
echo BB_6_wroc_tak KOD=%ERRORLEVEL% >> %ROB%\kody.txt
call %ROB%\stan.cmd %KB% %S% "po kroku 6 (powrot bez zgody - oczekiwany kod 8)"

rem --- krok 7: powrot z przywroceniem kopii
echo BB_7_wroc_przywroc START %date% %time% >> %ROB%\czasy.txt
call %KB%\Wroc_do_poprzedniej.cmd /przywroc-kopie /bez-pauzy < NUL > %ROB%\t12_B2_7.log 2>&1
echo BB_7_wroc_przywroc_kopie KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo BB_7_wroc_przywroc KONIEC %date% %time% >> %ROB%\czasy.txt
call %ROB%\stan.cmd %KB% %S% "po kroku 7 (e: po powrocie z przywroceniem kopii)"

rem --- krok 8: start wersji N na przywroconej bazie
call %KB%\Stanowisko.cmd --zamknij-po 5 < NUL > %ROB%\t12_B2_8.log 2>&1
echo BB_8_start_N KOD=%ERRORLEVEL% >> %ROB%\kody.txt
call %ROB%\stan.cmd %KB% %S% "po kroku 8 (start wersji N na przywroconej bazie)"
call %KB%\Wersje.cmd /bez-pauzy < NUL >> %S% 2>&1
echo BB KONIEC %date% %time% >> %ROB%\czasy.txt
exit /b 0
