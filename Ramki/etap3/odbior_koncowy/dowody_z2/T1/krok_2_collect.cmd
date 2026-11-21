@echo off
rem T1 krok 2 (kontrola <REPO>, zalozenie ustawienia.toml) + --collect-only obydwoma interpreterami
set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe
set QT_QPA_PLATFORM=offscreen
set ROB=<PC-katalog>\koordynator\robocze\odbior2\final\T1
set K=<PC-katalog>\t0\odbior2\Stanowisko
set REPO=<PC-katalog>\t0\repo2
set ST=<PC-katalog>\t0\repo2\Ramki\stanowisko

echo %date% %time% > %ROB%\t1_2_repo.txt
echo === git -C %REPO% config --get core.autocrlf >> %ROB%\t1_2_repo.txt
git -C %REPO% config --get core.autocrlf >> %ROB%\t1_2_repo.txt 2>&1
echo KOD=%ERRORLEVEL% >> %ROB%\t1_2_repo.txt
echo === git -C %REPO% status --short >> %ROB%\t1_2_repo.txt
git -C %REPO% status --short >> %ROB%\t1_2_repo.txt 2>&1
echo KOD=%ERRORLEVEL% >> %ROB%\t1_2_repo.txt
echo === git -C %REPO% rev-parse HEAD >> %ROB%\t1_2_repo.txt
git -C %REPO% rev-parse HEAD >> %ROB%\t1_2_repo.txt 2>&1
echo === if exist %ST%\ustawienia.toml (przed copy) >> %ROB%\t1_2_repo.txt
if exist %ST%\ustawienia.toml (echo JEST >> %ROB%\t1_2_repo.txt) else (echo BRAK >> %ROB%\t1_2_repo.txt)
echo === copy %ST%\ustawienia.przyklad.toml %ST%\ustawienia.toml >> %ROB%\t1_2_repo.txt
copy %ST%\ustawienia.przyklad.toml %ST%\ustawienia.toml >> %ROB%\t1_2_repo.txt 2>&1
echo KOD=%ERRORLEVEL% >> %ROB%\t1_2_repo.txt
echo === git -C %REPO% status --short (po copy) >> %ROB%\t1_2_repo.txt
git -C %REPO% status --short >> %ROB%\t1_2_repo.txt 2>&1
echo KOD=%ERRORLEVEL% >> %ROB%\t1_2_repo.txt

call %K%\Polecenie.cmd -m pytest %ST%\testy -q --collect-only -p no:cacheprovider --rootdir %ST% < NUL > %ROB%\robocze\t1_collect_wersja_pelny.txt 2>&1
echo collect_wersja KOD=%ERRORLEVEL% >> %ROB%\kody.txt
cd /d %ST%
call <PC-katalog>\koordynator\narz\py.cmd -m pytest -q --collect-only -p no:cacheprovider < NUL > %ROB%\robocze\t1_collect_bazowy_pelny.txt 2>&1
echo collect_bazowy KOD=%ERRORLEVEL% >> %ROB%\kody.txt
exit /b 0
