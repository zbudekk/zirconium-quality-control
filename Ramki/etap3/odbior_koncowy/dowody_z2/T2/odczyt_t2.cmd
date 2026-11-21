@echo off
rem Odczyt bazy po T2 (tylko odczyt; bez kolumny plik). Uzycie: odczyt_t2.cmd <DRZEWO> <baza> <plik wyniku>
set ODB=%~1\Ramki\etap3\odbior_koncowy
set PYEXE=<PC>\AppData\Local\Programs\Python\Python312\python.exe
echo == skany > %3
%PYEXE% -I %ODB%\narzedzia\sql_odczyt.py --baza %2 "SELECT id, sha16, status, tryb, uklad, uklad_zrodlo, uklad_zgodny, numer_plytki, numer_zrodlo, czas_s FROM skany ORDER BY id" >> %3 2>&1 < NUL
echo == prace plytek okraglych ramkowych wg status_gniazda >> %3
%PYEXE% -I %ODB%\narzedzia\sql_odczyt.py --baza %2 "SELECT s.id, s.sha16, s.uklad, p.status_gniazda, count(*) AS prac FROM skany s JOIN prace p ON p.skan_id = s.id WHERE substr(s.uklad, 1, 15) = 'okragla_ramkowa' GROUP BY s.id, p.status_gniazda ORDER BY s.id, p.status_gniazda" >> %3 2>&1 < NUL
echo == gniazda plytek okraglych ramkowych >> %3
%PYEXE% -I %ODB%\narzedzia\sql_odczyt.py --baza %2 "SELECT s.id, p.gniazdo, p.status_gniazda, p.status_inspekcji FROM skany s JOIN prace p ON p.skan_id = s.id WHERE substr(s.uklad, 1, 15) = 'okragla_ramkowa' ORDER BY s.id, p.gniazdo" >> %3 2>&1 < NUL
echo == zdarzenia >> %3
%PYEXE% -I %ODB%\narzedzia\sql_odczyt.py --baza %2 "SELECT zrodlo, typ, count(*) FROM zdarzenia GROUP BY zrodlo, typ ORDER BY 1, 2" >> %3 2>&1 < NUL
echo KOD=%ERRORLEVEL% >> %3
