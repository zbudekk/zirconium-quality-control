@echo off
set QT_QPA_PLATFORM=offscreen
set K=<PC-katalog>\t0\odbior\Stanowisko
set ROB=<PC-katalog>\koordynator\robocze\odbior\T8
echo wieczor START %TIME% >> %ROB%\kody.txt
call %K%\Polecenie.cmd narzedzia\raport_metryk.py --baza %ROB%\robocze\baza_t2.sqlite --tryb wieczor --od 2026-11-20 --do 2026-11-21 --json %ROB%\t8_wieczor.json > %ROB%\t8_wieczor.txt 2> %ROB%\t8_wieczor_stderr.txt < NUL
echo t8_wieczor KOD=%ERRORLEVEL% KONIEC %TIME% >> %ROB%\kody.txt
echo rano START %TIME% >> %ROB%\kody.txt
call %K%\Polecenie.cmd narzedzia\raport_metryk.py --baza %ROB%\robocze\baza_t3.sqlite --tryb oba --od 2026-11-17 --do 2026-11-19 --json %ROB%\t8_rano.json > %ROB%\t8_rano.txt 2> %ROB%\t8_rano_stderr.txt < NUL
echo t8_rano KOD=%ERRORLEVEL% KONIEC %TIME% >> %ROB%\kody.txt
