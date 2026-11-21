@echo off
rem Odczyt bazy po T11 czesc B (tylko odczyt). Uzycie: odczyt_t11.cmd <DRZEWO> <baza> <plik wyniku>
set ODB=%~1\Ramki\etap3\odbior_koncowy
set PYEXE=<PC>\AppData\Local\Programs\Python\Python312\python.exe
echo == skany (zapytanie planu + sha16, numer) > %3
%PYEXE% -I %ODB%\narzedzia\sql_odczyt.py --baza %2 "SELECT id, sha16, status, tryb, uklad, uklad_zrodlo, uklad_zgodny, numer_plytki, numer_zrodlo, czas_s FROM skany ORDER BY id" >> %3 2>&1 < NUL
echo == zielone (zapytanie planu) >> %3
%PYEXE% -I %ODB%\narzedzia\sql_odczyt.py --baza %2 "SELECT s.id, s.status, s.uklad, sum(p.status_gniazda='zielony') AS zielonych FROM skany s LEFT JOIN prace p ON p.skan_id = s.id GROUP BY s.id" >> %3 2>&1 < NUL
echo == zdarzenia >> %3
%PYEXE% -I %ODB%\narzedzia\sql_odczyt.py --baza %2 "SELECT zrodlo, typ, count(*) FROM zdarzenia GROUP BY zrodlo, typ ORDER BY 1, 2" >> %3 2>&1 < NUL
echo KOD=%ERRORLEVEL% >> %3
