@echo off
rem T2 - "Praca przeoczona - fakty", pkt 3: ten sam skan (poz. 8 scenariusza, sha16 247ee785f428396f) 3 razy przez narzedzie
rem pomiarowe T10 (metryki_P3a.py) - tylko odczyt danych, wyniki w robocze\powt; to NIE jest przebieg kryterium T2
set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe
set QT_QPA_PLATFORM=offscreen
set K=<PC-katalog>\t0\odbior\Stanowisko
set ROB=<PC-katalog>\koordynator\robocze\odbior\T2
for %%i in (1 2 3) do (
  call %K%\Polecenie.cmd narzedzia\metryki_P3a.py --skany <PC-katalog>\app\dane_ref\syntetyczne_R59_P2 --wzorzec skan_wieczorna_n2_s0102.stl --projekty <PC-katalog>\app\Prace_test --wyjscie %ROB%\robocze\powt --nazwa powt_%%i.json --procesy 1 --ustawienia %K%\ustawienia.toml > %ROB%\robocze\powt\powt_%%i.log 2>&1 < NUL
  call echo powt_%%i KOD=%%ERRORLEVEL%% %%TIME%% >> %ROB%\kody.txt
)
exit /b 0
