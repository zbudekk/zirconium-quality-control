@echo off
set ROB=<PC-katalog>\koordynator\robocze\odbior\T7
"C:\Program Files\PowerShell\7\pwsh.exe" -NoProfile -ExecutionPolicy Bypass -File %ROB%\robocze\proba_b1b.ps1 > %ROB%\robocze\b1b_sterownik.log 2>&1
echo B1b_sterownik KOD=%ERRORLEVEL% %time% >> %ROB%\kody.txt
exit /b 0
