# S3 - dowod z uruchomienia testow (2026-11-23)

Katalog: <PC-katalog>\qc-wt\analiza-s3\Ramki\stanowisko (worktree galezi analiza/s3, bez zmian w kodzie).
Polecenie (dla kazdego pliku, z katalogu stanowisko):

    <PC-katalog>\koordynator\narz\py.cmd -m pytest testy\<plik> -q -p no:cacheprovider

Czas mierzony stoperem wokol calego polecenia (z uruchomieniem interpretera), wiec jest o 1.5-2.5 s
dluzszy niz czas podany przez pytest. Limit narzedzia 180000 ms na kazde polecenie - zaden plik go nie przekroczyl.
Pliki 1-7 uruchomione po kolei, pojedynczo. Pliki 8-9 zostaly wyslane w jednym kroku narzedzia (dwa
wywolania w jednej wiadomosci) - nie moge wykluczyc, ze przez ok. 4 s dzialaly rownolegle (test_session_rano
trwal 3.9 s); czas test_ui_rano mogl byc przez to minimalnie zawyzony. Nie powtarzano.

| plik | czas s | passed | failed | skipped | errors | ostatni wiersz pytest |
|---|---|---|---|---|---|---|
| testy\test_okragle_ramka.py | 57.6 | 47 | 0 | 0 | 0 | 47 passed in 55.71s |
| testy\test_indicate.py | 66.4 | 35 | 0 | 0 | 0 | 35 passed in 64.80s (0:01:04) |
| testy\test_ramka.py | 16.4 | 84 | 0 | 0 | 0 | 84 passed in 14.85s |
| testy\test_excel.py | 27.1 | 129 | 0 | 0 | 0 | 129 passed in 25.52s |
| testy\test_session_wieczor.py | 10.9 | 63 | 1 (srodowisko) | 0 | 0 | 1 failed, 63 passed in 9.27s |
| testy\test_ui_wieczor.py | 84.0 | 89 | 0 | 0 | 0 | 89 passed in 81.73s (0:01:21) |
| testy\test_o4_ramka_rpi.py | 18.6 | 18 | 0 | 0 | 0 | 18 passed in 17.02s |
| testy\test_session_rano.py | 3.9 | 73 | 0 | 0 | 0 | 73 passed in 2.30s |
| testy\test_ui_rano.py | 38.0 | 32 | 0 | 0 | 0 | 32 passed in 36.38s |
| RAZEM | 322.9 | 570 | 1 | 0 | 0 | - |

Kody wyjscia: 0 dla wszystkich plikow poza test_session_wieczor.py (1).

## Szczegoly niepowodzen

### 1. testy/test_session_wieczor.py::test_wynik_prawdziwego_porownaj_wchodzi_do_bazy

Klasyfikacja: **srodowisko (brak ustawienia.toml)** - nie blad programu.

Przyczyna (wiersz E z pytest, znaki polskie zamienione na ASCII):

    E   FileNotFoundError: brak pliku ustawien: <PC-katalog>\qc-wt\analiza-s3\Ramki\stanowisko\ustawienia.toml - skopiuj ustawienia.przyklad.toml jako ustawienia.toml i uzupelnij sciezki

Sciezka wywolan: testy\test_session_wieczor.py:1602 synth.Opcje.z_toml(...) -> stanowisko\synth.py:865
_z_ustawien(UST.domyslne() ...) -> stanowisko\ustawienia.py:372 domyslne() -> wczytaj_ustawienia() ->
stanowisko\ustawienia.py:352 raise FileNotFoundError. Test wola synth.Opcje.z_toml bez argumentu ust,
wiec siega po domyslny plik ustawienia.toml, ktorego w swiezym worktree nie ma (.gitignore).

Pierwsze 15 wierszy komunikatu bledu (doslownie, po naglowku testu):

    korony = [WindowsPath('<PC>/AppData/Local/Temp/pytest-of-<uzytkownik>/pytest-10/stl0/a0_siekacz.stl'), WindowsPath('C:/Users...1_przedtrzonowy.stl'), WindowsPath('<PC>/AppData/Local/Temp/pytest-of-<uzytkownik>/pytest-10/stl0/a2_trzonowy.stl')]
    tmp_path = WindowsPath('<PC>/AppData/Local/Temp/pytest-of-<uzytkownik>/pytest-10/test_wynik_prawdziwego_porowna0')

        def test_wynik_prawdziwego_porownaj_wchodzi_do_bazy(korony, tmp_path):
            """Skan sztucznej plytki (3 atrapy koron) -> porownaj.porownaj -> session: te same klucze co w danych testowych, prace 1:1."""
            import shutil
            import warnings

            import numpy as np

            from stanowisko import porownaj as PO, synth, uklad as U, ustawienia as UST

            proj = tmp_path / "projekty"
            proj.mkdir()
            for i, p in enumerate(korony):

Dalsza czesc (skrot): wiersz `>       op = synth.Opcje.z_toml(plytka=uk.nazwa, prace_na_plytce=3, wspolczynnik=(1.22, 1.22), ubytki_na_prace=(0, 1), srednica_ubytku=(0.8, 1.4), poza_uklad=True, pole=100.0)`
w testy\test_session_wieczor.py:1602, nastepnie FileNotFoundError jak wyzej.
Podsumowanie pytest: `FAILED testy/test_session_wieczor.py::test_wynik_prawdziwego_porownaj_wchodzi_do_bazy`.

Bledow programu (failed/error niezwiazanych ze srodowiskiem): 0. Testow czasowych, ktore padly pod obciazeniem: 0.

## git status po testach

Polecenie: `git -C <PC-katalog>\qc-wt\analiza-s3 status --short`

    ?? Ramki/analiza_kodu_2026-11-23/S3/

(katalog S3 byl niesledzony juz przed uruchomieniem testow; zawiera proba_s3.py, proba_s3_bledy.txt,
proba_s3_wynik.txt oraz ten plik). Poza S3 brak nowych lub zmienionych plikow sledzonych / niesledzonych.

Uwaga (plik ignorowany, niewidoczny w zwyklym status): `git status --short --ignored -- Ramki/stanowisko`
pokazuje `!! Ramki/stanowisko/ramka/__pycache__/` - 12 plikow .pyc utworzonych 23.11.2026 17:35:43, czyli
w trakcie tego przebiegu. Najpewniejsze zrodlo: testy\test_ramka.py:1097 uruchamia podproces
`sys.executable -I -S -c ...` importujacy moduly ramka; flaga -I pomija zmienne PYTHON*, wiec ustawione w
py.cmd PYTHONDONTWRITEBYTECODE=1 nie dziala i Python zapisuje .pyc. Katalog jest w .gitignore; nic nie usunieto.
