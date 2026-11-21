@echo off
rem T7 czesc B: proba 2 (zakonczenie programu), potem proba 3 (zakonczenie silnika) - sterownik proba_b.ps1 (pwsh 7)
set ROB=<PC-katalog>\koordynator\robocze\odbior\T7
"C:\Program Files\PowerShell\7\pwsh.exe" -NoProfile -ExecutionPolicy Bypass -File %ROB%\robocze\proba_b.ps1 -N b2 -Tryb program -Ile 4 > %ROB%\robocze\b2_sterownik.log 2>&1
echo B2_sterownik KOD=%ERRORLEVEL% %time% >> %ROB%\kody.txt
exit /b 0
