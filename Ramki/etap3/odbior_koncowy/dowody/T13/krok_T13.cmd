@echo off
rem T13 pierwszy przebieg: higiena repo na commicie paczki 571e186 (polecenia planu)
set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe
set ROB=<PC-katalog>\koordynator\robocze\odbior\T13
set REPO=<PC-katalog>\t0\repo
set ODB=%REPO%\Ramki\etap3\odbior_koncowy
echo t13_higiena START %date% %time% > %ROB%\czasy.txt
%PY% -I %ODB%\narzedzia\t13_higiena.py --repo %REPO% --od 2537f6f --do 571e186cb8178209da670dde244dfc56bba5e300 --json %ROB%\t13_wynik.json > %ROB%\t13_wynik.txt 2> %ROB%\t13_wynik_stderr.txt
echo t13_higiena KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo t13_higiena KONIEC %date% %time% >> %ROB%\czasy.txt
git -C %REPO% diff --stat 2537f6f 571e186cb8178209da670dde244dfc56bba5e300 > %ROB%\t13_diff_stat.txt 2>&1
echo t13_diff_stat KOD=%ERRORLEVEL% >> %ROB%\kody.txt
git -C %REPO% rev-parse HEAD > %ROB%\t13_repo_stan.txt 2>&1
git -C %REPO% status --short >> %ROB%\t13_repo_stan.txt 2>&1
git -C %REPO% merge-base --is-ancestor 2537f6f 571e186cb8178209da670dde244dfc56bba5e300
echo t13_is_ancestor KOD=%ERRORLEVEL% >> %ROB%\kody.txt
git -C %REPO% log --follow --format="%%h %%ad %%s" --date=iso -- Ramki/plan_etap3_pelna_aplikacja_2026-11-16.md > %ROB%\t13_poczatek_etapu.txt 2>&1
exit /b 0
