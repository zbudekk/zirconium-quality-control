@echo off
rem ==========================================================================
rem  buduj_pdf_R59.cmd - buduje trzy PDF dokumentow stanowiska po zmianie R59
rem  (nowy uklad gniazd plytek). Uruchom dwuklikiem albo z okna cmd.
rem
rem  Co robi: przechodzi do folderu Ramki (jeden poziom wyzej niz ten plik)
rem  i trzy razy wola  narzedzia\buduj_plan_wdrozenia.py --md "dokument.md".
rem  Kazdy PDF powstaje obok swojego pliku .md, pod ta sama nazwa. Stary PDF
rem  jest nadpisywany; kopie sprzed zmiany: archiwum\*_przed_dokumenty_R59_*.
rem
rem  Wymagania - konto wlasciciela na PC, tak jak przy R56 i R57: Python 3.14
rem  wolany przez  py -3.14  z pakietami markdown-it-py, beautifulsoup4,
rem  playwright z Chromium, pdfplumber, reportlab, pypdf. Ten plik niczego nie
rem  instaluje. Inny interpreter: przed uruchomieniem ustaw zmienna PYTHON_PDF,
rem  na przyklad:  set PYTHON_PDF=py -3.13
rem
rem  Nazwy dokumentow zawieraja pauze i polskie znaki. Ten plik jest w ASCII,
rem  wiec ich nie wpisuje: znajduje dokumenty wzorcem z gwiazdka.
rem
rem  Przed budowa sprawdza, czy w folderze sa pliki po R59: trzy dokumenty ze
rem  znacznikiem [R59], pliki ukladu gniazd z jedna rynienka i skrypt PDF po
rem  R59, ktory liczy podpisy rysunkow 4 i 5 z plikow ukladu gniazd. Starsza
rem  wersja skryptu ma te liczby wpisane na stale. Gdy czegos brakuje - pisze
rem  czego i konczy.
rem
rem  Jak sprawdzic wynik:
rem   1. Trzy linie  OK: nazwa.pdf, stron: N  - okolo 20 s na dokument.
rem   2. Na koncu lista trzech PDF z dzisiejsza data i godzina.
rem   3. W planie wdrozenia rysunki 4 i 5 pokazuja plytki z JEDNA rynienka:
rem      wieczorna 18 gniazd, poranna 23 gniazda; w tekscie jest znacznik [R59].
rem ==========================================================================
setlocal
set "CP_PRZED="
for /f "tokens=2 delims=:" %%C in ('chcp') do set "CP_PRZED=%%C"
chcp 65001 >nul
set PYTHONUTF8=1
if not defined PYTHON_PDF set "PYTHON_PDF=py -3.14"
set "BLAD="

cd /d "%~dp0.."
echo Folder roboczy: %CD%
echo Interpreter:    %PYTHON_PDF%
echo.

rem --- czy sa wszystkie pliki
if not exist "narzedzia\buduj_plan_wdrozenia.py" goto brak_skryptu
if not exist "wyniki_v2\json\uklad_gniazd_wieczorna.json" goto brak_json
if not exist "wyniki_v2\json\uklad_gniazd_poranna.json" goto brak_json
set N=0
for %%F in ("Stanowisko kontroli cyrkonii*plan wdrozenia v2.md" "Zakupy i druk*stanowisko kontroli cyrkonii.md" "Budowa ramki*decyzje i zamienniki.md") do set /a N+=1
if not "%N%"=="3" goto brak_md

rem --- czy to pliki po R59
set "STARE="
for %%F in ("Stanowisko kontroli cyrkonii*plan wdrozenia v2.md" "Zakupy i druk*stanowisko kontroli cyrkonii.md" "Budowa ramki*decyzje i zamienniki.md") do (
  type "%%F" | findstr /C:"[R59]" >nul
  if errorlevel 1 set "STARE=1"
)
if defined STARE goto stare_md
findstr /C:"\"d_top\": 9," "wyniki_v2\json\uklad_gniazd_wieczorna.json" >nul
if not errorlevel 1 goto stary_json
findstr /C:"\"d_top\": 7.5," "wyniki_v2\json\uklad_gniazd_poranna.json" >nul
if not errorlevel 1 goto stary_json
findstr /C:"opis_gniazd(jw)" "narzedzia\buduj_plan_wdrozenia.py" >nul
if errorlevel 1 goto stare_podpisy
findstr /C:"opis_gniazd(jp)" "narzedzia\buduj_plan_wdrozenia.py" >nul
if errorlevel 1 goto stare_podpisy

rem --- czy interpreter ma pakiety
%PYTHON_PDF% -c "import markdown_it, bs4, playwright, pdfplumber, reportlab, pypdf"
if errorlevel 1 goto brak_pakietow

rem --- budowa: trzy wywolania skryptu PDF
echo Buduje trzy PDF, okolo minuty...
echo.
for %%F in ("Stanowisko kontroli cyrkonii*plan wdrozenia v2.md") do %PYTHON_PDF% narzedzia\buduj_plan_wdrozenia.py --md "%%F"
if errorlevel 1 set "BLAD=1"
for %%F in ("Zakupy i druk*stanowisko kontroli cyrkonii.md") do %PYTHON_PDF% narzedzia\buduj_plan_wdrozenia.py --md "%%F"
if errorlevel 1 set "BLAD=1"
for %%F in ("Budowa ramki*decyzje i zamienniki.md") do %PYTHON_PDF% narzedzia\buduj_plan_wdrozenia.py --md "%%F"
if errorlevel 1 set "BLAD=1"

echo.
echo Pliki PDF w folderze - data, rozmiar w bajtach, nazwa:
for %%F in ("Stanowisko kontroli cyrkonii*plan wdrozenia v2.pdf" "Zakupy i druk*stanowisko kontroli cyrkonii.pdf" "Budowa ramki*decyzje i zamienniki.pdf") do echo   %%~tF  %%~zF  %%F
echo.
if defined BLAD goto blad_budowy
echo GOTOWE: trzy PDF zbudowane. Sprawdz date plikow i rysunki 4 i 5 w planie,
echo potem daj znac koordynatorowi paczki R59.
goto koniec

:brak_skryptu
echo BLAD: w folderze roboczym nie ma pliku narzedzia\buduj_plan_wdrozenia.py.
echo Ten plik .cmd musi lezec w podfolderze narzedzia folderu Ramki.
goto koniec

:brak_json
echo BLAD: brak plikow wyniki_v2\json\uklad_gniazd_wieczorna.json i _poranna.json.
echo Bez nich PDF nie mialby rysunkow plytek. Skopiuj je z repo - stan po R59.
goto koniec

:brak_md
echo BLAD: w folderze roboczym powinny byc trzy dokumenty .md, znaleziono: %N%.
echo Potrzebne: plan wdrozenia v2, Zakupy i druk, Budowa ramki.
goto koniec

:stare_md
echo BLAD: co najmniej jeden dokument .md nie ma znacznika [R59] - to wersja
echo sprzed zmiany ukladu gniazd. Skopiuj trzy dokumenty .md z repo - stan po R59.
goto koniec

:stary_json
echo BLAD: pliki wyniki_v2\json\uklad_gniazd_*.json opisuja STARY uklad gniazd,
echo sa w nich gniazda 9 albo 7,5 mm. Rysunki 4 i 5 pokazalyby stare plytki.
echo Skopiuj oba pliki z repo - stan po R59.
goto koniec

:stare_podpisy
echo BLAD: narzedzia\buduj_plan_wdrozenia.py to wersja sprzed R59. Podpisy
echo rysunkow 4 i 5 maja w niej liczby gniazd wpisane na stale, wiec PDF mialby
echo nowy rysunek ze starym podpisem. Skopiuj skrypt z repo - stan po R59.
goto koniec

:brak_pakietow
echo.
echo BLAD: interpreter %PYTHON_PDF% nie dziala albo brakuje mu pakietow
echo markdown_it, bs4, playwright, pdfplumber, reportlab, pypdf.
echo Uruchom ten plik na koncie, na ktorym budowano PDF przy R56 i R57,
echo albo wskaz inny interpreter zmienna PYTHON_PDF. Niczego nie zainstalowano.
goto koniec

:blad_budowy
echo BLAD: co najmniej jedno wywolanie skryptu PDF zakonczylo sie bledem -
echo komunikat jest wyzej. PDF z nowa data sa zbudowane, pozostale sa stare.
goto koniec

:koniec
if defined CP_PRZED chcp %CP_PRZED% >nul 2>nul
echo.
pause
endlocal
