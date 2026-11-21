@echo off
rem T5 czesc B krok 1: atrapa ramki P z konsola polecen (wejscie = potok z pliku polecen)
set K=<PC-katalog>\t0\odbior\Stanowisko
call %K%\Polecenie.cmd narzedzia\atrapa_ramki.py --rola P --host <adres-IP> --port 8767 --sterowanie
echo ATRAPA_P KOD=%ERRORLEVEL%
