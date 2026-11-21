@echo off
rem T0 kroki 6-9 na instalacji 0.3.3: samokontrola, starty programu, kontrola _wmi, dowod "bez internetu"
set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe
set QT_QPA_PLATFORM=offscreen
set ROB=<PC-katalog>\koordynator\robocze\odbior2\final\T0
set K=<PC-katalog>\t0\odbior2\Stanowisko

echo krok6a START %time% >> %ROB%\t0_czasy_6_9.txt
call %K%\Samokontrola.cmd --bez-sieci < NUL > %ROB%\t0_samokontrola.txt 2>&1
echo krok6a_samokontrola_bez_sieci KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo krok6a KONIEC %time% >> %ROB%\t0_czasy_6_9.txt

echo krok6b START %time% >> %ROB%\t0_czasy_6_9.txt
call %K%\Samokontrola.cmd --json < NUL > %ROB%\t0_samokontrola.json 2> %ROB%\t0_samokontrola_json_stderr.txt
echo krok6b_samokontrola_json KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo krok6b KONIEC %time% >> %ROB%\t0_czasy_6_9.txt

echo krok7a START %time% >> %ROB%\t0_czasy_6_9.txt
echo === %K%\Stanowisko.cmd --atrapa --zamknij-po 5 > %ROB%\t0_start.txt
call %K%\Stanowisko.cmd --atrapa --zamknij-po 5 < NUL >> %ROB%\t0_start.txt 2>&1
set KOD7A=%ERRORLEVEL%
echo KOD=%KOD7A% >> %ROB%\t0_start.txt
echo krok7a_start_atrapa KOD=%KOD7A% >> %ROB%\kody.txt
echo krok7a KONIEC %time% >> %ROB%\t0_czasy_6_9.txt

echo krok7b START %time% >> %ROB%\t0_czasy_6_9.txt
echo === %K%\Stanowisko.cmd --zamknij-po 20 >> %ROB%\t0_start.txt
call %K%\Stanowisko.cmd --zamknij-po 20 < NUL >> %ROB%\t0_start.txt 2>&1
set KOD7B=%ERRORLEVEL%
echo KOD=%KOD7B% >> %ROB%\t0_start.txt
echo krok7b_start_kontroler KOD=%KOD7B% >> %ROB%\kody.txt
echo krok7b KONIEC %time% >> %ROB%\t0_czasy_6_9.txt

echo === find /c "Traceback" %K%\dane\logi\stanowisko.log >> %ROB%\t0_start.txt
find /c "Traceback" %K%\dane\logi\stanowisko.log >> %ROB%\t0_start.txt 2>&1
echo krok7c_find_traceback KOD=%ERRORLEVEL% (1 = 0 wierszy) >> %ROB%\kody.txt

call %K%\Polecenie.cmd -c "import stanowisko, sys; print(sys.modules.get('_wmi', 'brak'))" < NUL > %ROB%\t0_8.log 2>&1
echo krok8_wmi KOD=%ERRORLEVEL% >> %ROB%\kody.txt

echo === findstr /c:"Ignoring indexes" /c:"Looking in links" %K%\wersje\0.3.3\pip.log > %ROB%\t0_pip_bez_sieci.txt
findstr /c:"Ignoring indexes" /c:"Looking in links" %K%\wersje\0.3.3\pip.log >> %ROB%\t0_pip_bez_sieci.txt 2>&1
echo krok9a_findstr_pip KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo === findstr /c:"bez sieci" %K%\dziennik_instalacji.txt >> %ROB%\t0_pip_bez_sieci.txt
findstr /c:"bez sieci" %K%\dziennik_instalacji.txt >> %ROB%\t0_pip_bez_sieci.txt 2>&1
echo krok9b_findstr_dziennik KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo === find /c "Downloading" %K%\wersje\0.3.3\pip.log >> %ROB%\t0_pip_bez_sieci.txt
find /c "Downloading" %K%\wersje\0.3.3\pip.log >> %ROB%\t0_pip_bez_sieci.txt 2>&1
echo krok9c_find_downloading KOD=%ERRORLEVEL% (1 = 0 wierszy) >> %ROB%\kody.txt
echo === find /c "http" %K%\wersje\0.3.3\pip.log >> %ROB%\t0_pip_bez_sieci.txt
find /c "http" %K%\wersje\0.3.3\pip.log >> %ROB%\t0_pip_bez_sieci.txt 2>&1
exit /b 0
