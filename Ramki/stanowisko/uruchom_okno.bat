@echo off
rem Okno testowe stanowiska (PySide6): plate -> match -> inspect. Wymaga Pythona 3.12 (py -3.12) i pip install -r requirements.txt
cd /d "%~dp0"
set PYTHONUTF8=1
py -3.12 -m stanowisko.ui_test %*
if errorlevel 1 pause
