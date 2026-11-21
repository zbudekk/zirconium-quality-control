@echo off
rem kontrola zestawu T14 na instalacji + T1 krok 2 + --collect-only obydwoma interpreterami
set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe
set QT_QPA_PLATFORM=offscreen
set ROB=<PC-katalog>\koordynator\robocze\odbior\T1
set R14=<PC-katalog>\koordynator\robocze\odbior\T14
set K=<PC-katalog>\t0\odbior\Stanowisko
set REPO=<PC-katalog>\t0\repo
set ST=<PC-katalog>\t0\repo\Ramki\stanowisko

echo START %time% > %R14%\t14_czas.txt
call %K%\Polecenie.cmd %REPO%\Ramki\etap3\t14\symulator_t14.py --sprawdz --program . < NUL > %R14%\t14_sprawdz_paczka.txt 2>&1
echo t14_sprawdz KOD=%ERRORLEVEL% >> %R14%\kody.txt
echo KONIEC %time% >> %R14%\t14_czas.txt

echo === git -C %REPO% config --get core.autocrlf > %ROB%\t1_2_repo.txt
git -C %REPO% config --get core.autocrlf >> %ROB%\t1_2_repo.txt 2>&1
echo KOD=%ERRORLEVEL% >> %ROB%\t1_2_repo.txt
echo === git -C %REPO% status --short >> %ROB%\t1_2_repo.txt
git -C %REPO% status --short >> %ROB%\t1_2_repo.txt 2>&1
echo KOD=%ERRORLEVEL% >> %ROB%\t1_2_repo.txt
echo === git -C %REPO% rev-parse HEAD >> %ROB%\t1_2_repo.txt
git -C %REPO% rev-parse HEAD >> %ROB%\t1_2_repo.txt 2>&1
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