@echo off
rem T7 czesc B proba 1: brak folderu "Cyrkon" - program i samokontrola z instalacji WSPOLNEJ z WLASNYM plikiem ustawien (zasada 3)
set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe
set QT_QPA_PLATFORM=offscreen
set ROB=<PC-katalog>\koordynator\robocze\odbior\T7
set RB=%ROB%\robocze
set K=<PC-katalog>\t0\odbior\Stanowisko
set U=%ROB%\ustawienia_b1.toml
set ODB=<PC-katalog>\t0\repo\Ramki\etap3\odbior_koncowy
set SQL=%PY% -I %ODB%\narzedzia\sql_odczyt.py --baza %RB%\b1\dane\stanowisko.sqlite
set C=%ROB%\t7_b1_czasy.txt
echo b1_0 samokontrola z folderem START %date% %time% > %C%
call %K%\Polecenie.cmd -m stanowisko.samokontrola --ustawienia %U% --bez-sieci < NUL > %ROB%\t7_b1_0_samokontrola_z_folderem.log 2>&1
echo B1_0_samokontrola_z_folderem KOD=%ERRORLEVEL% >> %ROB%\kody.txt
ren %RB%\Cyrkon Cyrkon_x
echo B1_ren_Cyrkon_x KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo b1_1 program bez folderu START %date% %time% >> %C%
call %K%\Polecenie.cmd -m stanowisko.aplikacja --ustawienia %U% --zamknij-po 30 < NUL > %ROB%\t7_b1_1_program_bez_folderu.log 2>&1
echo B1_1_program_bez_folderu KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo b1_1 program bez folderu KONIEC %date% %time% >> %C%
copy /y %RB%\b1\dane\logi\stanowisko.log %RB%\b1\stanowisko_po_1.log > NUL
%SQL% "SELECT count(*) FROM zdarzenia" > %ROB%\t7_b1_baza.txt 2>&1
call %K%\Polecenie.cmd -m stanowisko.samokontrola --ustawienia %U% --bez-sieci < NUL > %ROB%\t7_b1_2_samokontrola_bez_folderu.log 2>&1
echo B1_2_samokontrola_bez_folderu KOD=%ERRORLEVEL% >> %ROB%\kody.txt
ren %RB%\Cyrkon_x Cyrkon
echo B1_ren_Cyrkon KOD=%ERRORLEVEL% >> %ROB%\kody.txt
call %K%\Polecenie.cmd -m stanowisko.samokontrola --ustawienia %U% --bez-sieci < NUL > %ROB%\t7_b1_3_samokontrola_po_przywroceniu.log 2>&1
echo B1_3_samokontrola_po_przywroceniu KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo b1_4 program po przywroceniu START %date% %time% >> %C%
call %K%\Polecenie.cmd -m stanowisko.aplikacja --ustawienia %U% --zamknij-po 30 < NUL > %ROB%\t7_b1_4_program_po_przywroceniu.log 2>&1
echo B1_4_program_po_przywroceniu KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo b1_4 program po przywroceniu KONIEC %date% %time% >> %C%
%SQL% "SELECT count(*) FROM zdarzenia" >> %ROB%\t7_b1_baza.txt 2>&1
%SQL% "SELECT typ, count(*) FROM zdarzenia GROUP BY typ" >> %ROB%\t7_b1_baza.txt 2>&1
exit /b 0
