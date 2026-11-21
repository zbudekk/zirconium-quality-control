@echo off
rem T11 czesc B: program (polecenie z "Ustalen koordynatora", zasada 3); --zamknij-po 3000 wg planu
set ROB=<PC-katalog>\koordynator\robocze\odbior\T11
set K=<PC-katalog>\t0\odbior\Stanowisko
echo B program START %date% %time% >> %ROB%\czasy.txt
call %K%\Polecenie.cmd -m stanowisko.aplikacja --ustawienia %ROB%\ustawienia.toml --zamknij-po 3000 < NUL > %ROB%\robocze\t11_program_stdout.log 2>&1
echo B program KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo B program KONIEC %date% %time% >> %ROB%\czasy.txt
echo koniec > %ROB%\robocze\program_koniec.txt