@echo off
set ROB=<PC-katalog>\koordynator\robocze\odbior\T7
"C:\Program Files\PowerShell\7\pwsh.exe" -NoProfile -ExecutionPolicy Bypass -File %ROB%\robocze\proba_b.ps1 -N b3 -Tryb silnik -Ile 3 > %ROB%\robocze\b3_sterownik.log 2>&1
echo B3_sterownik KOD=%ERRORLEVEL% %time% >> %ROB%\kody.txt
exit /b 0
