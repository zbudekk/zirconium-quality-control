@echo off
rem T5 czesc B krok 1: atrapa ramki W z konsola polecen (wejscie = potok z pliku polecen; bez "< NUL", bo konsola czyta polecenia)
set K=<PC-katalog>\t0\odbior\Stanowisko
call %K%\Polecenie.cmd narzedzia\atrapa_ramki.py --rola W --host <adres-IP> --port 8765 --sterowanie
echo ATRAPA_W KOD=%ERRORLEVEL%
