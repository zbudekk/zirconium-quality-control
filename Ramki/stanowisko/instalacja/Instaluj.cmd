@echo off
rem Instalacja programu "Stanowisko" w oknie (E3-I1): dwuklik tego pliku w ROZPAKOWANEJ paczce wydania.
rem Otwiera okno instalatora (Python z paczki - nie trzeba go instalowac) i od razu zamyka to okno konsoli.
rem Instalacja z wiersza polecen, aktualizacja z opcjami i testy: zainstaluj.cmd (opis: program\instrukcje\instalacja_i_aktualizacja.md).
setlocal
set "PACZKA=%~dp0"
set "PYTHONHOME="
set "PYTHONPATH="
if not exist "%PACZKA%python\pythonw.exe" goto :brak
if not exist "%PACZKA%program\instalacja\okno_instalatora.py" goto :brak
start "" "%PACZKA%python\pythonw.exe" -I -B "%PACZKA%program\instalacja\okno_instalatora.py" --paczka "%PACZKA%."
exit /b 0

:brak
echo BLAD: w paczce brakuje plikow okna instalatora (python\pythonw.exe albo program\instalacja\okno_instalatora.py).
echo CO ZROBIC: rozpakuj CALA paczke wydania (prawy klawisz - "Wyodrebnij wszystkie") i uruchom Instaluj.cmd z rozpakowanego folderu.
pause
exit /b 3
