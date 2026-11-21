KONTROLA ZESTAWU T14 NA INSTALACJI: zgodne 22 z 22 krokow, kod 0 (to NIE jest test T14 - test T14 wykonuje czlowiek)

# T14 - kontrola zestawu na instalacji z paczki (21.11.2026 02:52)

Jedno polecenie z planu ("Podzial na wykonawcow i kolejnosc", punkt 1), wykonane zaraz po T0 i kroku `/testy` przez wykonawce T0 / T1,
na instalacji wspolnej `<K>` = `<PC-katalog>\t0\odbior\Stanowisko` (wersja 0.3.1, commit 571e186), skrypt z `<REPO>` =
`<PC-katalog>\t0\repo` (ten sam commit): `set QT_QPA_PLATFORM=offscreen` i
`call <K>\Polecenie.cmd <REPO>\Ramki\etap3\t14\symulator_t14.py --sprawdz --program . < NUL > <ROB>\t14_sprawdz_paczka.txt 2>&1`
(z pliku `..\T1\krok_2_collect.cmd`; polecenie planu bez zmian poza `call` i `< NUL`). Wynik: kod wyjscia 0 (`kody.txt`), czas 8,1 s
(02:52:07,34 - 02:52:15,46, `t14_czas.txt`; proba generalna 8,3 s), wyjscie 50 wierszy, wierszy `NIEZGODNE` / `BLAD` / `Traceback`: 0,
ostatni wiersz: `SPRAWDZENIE T14 BEZ EKRANU: zgodne 22 z 22 krokow` - zgodnie z oczekiwaniem planu. Dowod: `t14_sprawdz_paczka.txt`.
W tym czasie na PC biegla instalacja T12 (tor 4); kontrola nie ma kryterium czasowego. Sam test T14 (czlowiek przy ekranie): NIE ZMIERZONO
w tej sesji - poza zakresem wykonawcy.
