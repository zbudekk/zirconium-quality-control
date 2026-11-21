@echo off
rem T13 - higiena repo na commicie wydania 0.3.3 (polecenia planu; tylko odczyt <REPO>)
set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe
set ROB=<PC-katalog>\koordynator\robocze\odbior2\final\T1
set REPO=<PC-katalog>\t0\repo2
set ODB=<PC-katalog>\t0\repo2\Ramki\etap3\odbior_koncowy
set DO=0fedbf6e4f97dc68b2f4679061a960ac81edbdbd
echo t13 START %date% %time% > %ROB%\t13_czasy.txt
%PY% -I %ODB%\narzedzia\t13_higiena.py --repo %REPO% --od 2537f6f --do %DO% --json %ROB%\t13_wynik.json > %ROB%\t13_wynik.txt 2> %ROB%\t13_wynik_stderr.txt
echo t13_higiena KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo t13 KONIEC %date% %time% >> %ROB%\t13_czasy.txt
git -C %REPO% diff --stat 2537f6f %DO% > %ROB%\t13_diff_stat.txt 2>&1
echo t13_diff_stat KOD=%ERRORLEVEL% >> %ROB%\kody.txt
git -C %REPO% merge-base --is-ancestor 2537f6f %DO%
echo t13_is_ancestor KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo === git -C %REPO% status --short (po T13) > %ROB%\t13_repo_stan.txt
git -C %REPO% status --short >> %ROB%\t13_repo_stan.txt 2>&1
git -C %REPO% rev-parse HEAD >> %ROB%\t13_repo_stan.txt 2>&1
exit /b 0
