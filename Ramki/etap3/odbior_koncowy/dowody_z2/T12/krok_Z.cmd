@echo off
rem T12 dodatek NOWY: aktualizacja ze STAREGO wydania 0.3.1 (ustawienia ze starym wzorem) do 0.3.3 i powrot do 0.3.1
set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe
set QT_QPA_PLATFORM=offscreen
set ROB=<PC-katalog>\koordynator\robocze\odbior2\final\T12
set T=<PC-katalog>\t0\odbior2_t12
set Z=%T%\z031
set KZ=%Z%\Stanowisko
set PZ=%Z%\paczka_0.3.1
set P1=%T%\paczka_0.3.3
set ZIP0=<PC-katalog>\wydania\Stanowisko_0.3.1.zip
set ZIP1=<PC-katalog>\wydania\Stanowisko_0.3.3.zip
set S=%ROB%\t12_Z_stany.txt
echo Z START %date% %time% >> %ROB%\czasy.txt
echo == dodatek Z: stany instalacji %KZ% > %S%

echo === certutil -hashfile %ZIP0% SHA256 > %ROB%\t12_Z_sha256_zip.txt
certutil -hashfile %ZIP0% SHA256 >> %ROB%\t12_Z_sha256_zip.txt 2>&1
echo Z0_certutil_031 KOD=%ERRORLEVEL% >> %ROB%\kody.txt
type %ZIP0%.sha256 >> %ROB%\t12_Z_sha256_zip.txt 2>&1
mkdir %PZ%
mkdir %Z%\dane\eksport
mkdir %Z%\dane\Prywatne
mkdir %Z%\dane\millbox
C:\Windows\System32\tar.exe -xf %ZIP0% -C %PZ% > %ROB%\t12_Z0_tar.log 2>&1
echo Z0_tar_031 KOD=%ERRORLEVEL% >> %ROB%\kody.txt
if not exist %P1%\zainstaluj.cmd (
  mkdir %P1%
  C:\Windows\System32\tar.exe -xf %ZIP1% -C %P1% >> %ROB%\t12_Z0_tar.log 2>&1
)
robocopy <PC-katalog>\app\Prace_test %Z%\dane\Cyrkon /E /NFL /NDL /NJH /NP >> %ROB%\t12_Z0_tar.log 2>&1
echo Z0_robocopy_cyrkon KOD=%ERRORLEVEL% (1 = skopiowano) >> %ROB%\kody.txt
echo Z0 KONIEC %date% %time% >> %ROB%\czasy.txt
if not exist %PZ%\zainstaluj.cmd exit /b 2
if not exist %P1%\zainstaluj.cmd exit /b 2

rem --- Z1: instalacja 0.3.1 (oczekiwany kod 10), ustawienia, ponownie (kod 0)
echo Z1_zainstaluj_031_1 START %date% %time% >> %ROB%\czasy.txt
call %PZ%\zainstaluj.cmd /katalog %KZ% /python %PY% /bez-sieci /bez-pauzy < NUL > %ROB%\t12_Z1_zainstaluj_031_1.log 2>&1
set KOD=%ERRORLEVEL%
echo Z1_zainstaluj_031_1 KOD=%KOD% >> %ROB%\kody.txt
echo Z1_zainstaluj_031_1 KONIEC %date% %time% >> %ROB%\czasy.txt
if not "%KOD%"=="10" exit /b 3
powershell -NoProfile -ExecutionPolicy Bypass -File %ROB%\edytuj.ps1 -Plik %KZ%\ustawienia.toml -Wej <PC-katalog>/t0/odbior2_t12/z031/dane > %ROB%\t12_Z1_edycja.log 2>&1
set KOD=%ERRORLEVEL%
echo Z1_edycja_ustawien KOD=%KOD% >> %ROB%\kody.txt
if not "%KOD%"=="0" exit /b 4
echo Z2_zainstaluj_031_2 START %date% %time% >> %ROB%\czasy.txt
call %PZ%\zainstaluj.cmd /katalog %KZ% /python %PY% /bez-sieci /bez-pauzy < NUL > %ROB%\t12_Z2_zainstaluj_031_2.log 2>&1
set KOD=%ERRORLEVEL%
echo Z2_zainstaluj_031_2 KOD=%KOD% >> %ROB%\kody.txt
echo Z2_zainstaluj_031_2 KONIEC %date% %time% >> %ROB%\czasy.txt
if not "%KOD%"=="0" exit /b 5
call %KZ%\Stanowisko.cmd --zamknij-po 20 < NUL > %ROB%\t12_Z2_start_031.log 2>&1
echo Z2_start_031 KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo Z2_start_031 KONIEC %date% %time% >> %ROB%\czasy.txt
call %KZ%\Wersje.cmd /bez-pauzy < NUL > %ROB%\t12_Z2_wersje_przed.log 2>&1
echo Z2_wersje KOD=%ERRORLEVEL% >> %ROB%\kody.txt
copy /y %KZ%\ustawienia.toml %ROB%\robocze\z031_ustawienia_przed.toml > NUL
call %ROB%\stan.cmd %KZ% %S% "Z2 (0.3.1 po 1 starcie programu, PRZED aktualizacja do 0.3.3)"

rem --- Z3: aktualizacja 0.3.1 - 0.3.3 JEDNYM poleceniem
echo Z3_zainstaluj_033 START %date% %time% >> %ROB%\czasy.txt
call %P1%\zainstaluj.cmd /katalog %KZ% /python %PY% /bez-sieci /bez-pauzy < NUL > %ROB%\t12_Z3_zainstaluj_033.log 2>&1
set KOD=%ERRORLEVEL%
echo Z3_zainstaluj_033 KOD=%KOD% >> %ROB%\kody.txt
echo Z3_zainstaluj_033 KONIEC %date% %time% >> %ROB%\czasy.txt
call %ROB%\stan.cmd %KZ% %S% "Z3 (PO aktualizacji do 0.3.3, PRZED startem)"

rem --- Z4: samokontrola 0.3.3 na starych ustawieniach
echo Z4_samokontrola START %date% %time% >> %ROB%\czasy.txt
call %KZ%\Samokontrola.cmd --bez-sieci < NUL > %ROB%\t12_Z4_samokontrola_033.log 2>&1
echo Z4_samokontrola_033 KOD=%ERRORLEVEL% >> %ROB%\kody.txt

rem --- Z5: start programu 0.3.3 i zamkniecie
echo Z5_start START %date% %time% >> %ROB%\czasy.txt
call %KZ%\Stanowisko.cmd --zamknij-po 20 < NUL > %ROB%\t12_Z5_start_033.log 2>&1
echo Z5_start_033 KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo Z5_start KONIEC %date% %time% >> %ROB%\czasy.txt
call %KZ%\Wersje.cmd /bez-pauzy < NUL > %ROB%\t12_Z5_wersje_po_033.log 2>&1
echo Z5_wersje KOD=%ERRORLEVEL% >> %ROB%\kody.txt
call %ROB%\stan.cmd %KZ% %S% "Z5 (PO starcie programu 0.3.3)"

rem --- Z6: powrot do 0.3.1 JEDNYM poleceniem
echo ===== Z6: Wroc_do_poprzedniej.cmd /tak /bez-pauzy %date% %time% > %ROB%\t12_Z6_wroc.log
echo Z6_wroc_tak START %date% %time% >> %ROB%\czasy.txt
call %KZ%\Wroc_do_poprzedniej.cmd /tak /bez-pauzy < NUL >> %ROB%\t12_Z6_wroc.log 2>&1
echo Z6_wroc_tak KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo Z6_wroc_tak KONIEC %date% %time% >> %ROB%\czasy.txt
call %ROB%\stan.cmd %KZ% %S% "Z6 (PO powrocie do 0.3.1, PRZED startem)"

rem --- Z7: samokontrola i start 0.3.1 po powrocie
call %KZ%\Samokontrola.cmd --bez-sieci < NUL > %ROB%\t12_Z7_samokontrola_031.log 2>&1
echo Z7_samokontrola_031 KOD=%ERRORLEVEL% >> %ROB%\kody.txt
call %KZ%\Stanowisko.cmd --zamknij-po 20 < NUL > %ROB%\t12_Z7_start_031.log 2>&1
echo Z7_start_031 KOD=%ERRORLEVEL% >> %ROB%\kody.txt
call %KZ%\Wersje.cmd /bez-pauzy < NUL > %ROB%\t12_Z7_wersje_po_powrocie.log 2>&1
echo Z7_wersje KOD=%ERRORLEVEL% >> %ROB%\kody.txt
call %ROB%\stan.cmd %KZ% %S% "Z7 (PO starcie 0.3.1 po powrocie = stan koncowy)"
echo wiersze Traceback w dane\logi\stanowisko.log: >> %S%
find /c "Traceback" %KZ%\dane\logi\stanowisko.log >> %S% 2>&1
echo Z KONIEC %date% %time% >> %ROB%\czasy.txt
exit /b 0
