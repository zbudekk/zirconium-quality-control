WERDYKT T6: ZAL (200 z 200 w trybie "pytaj" i 200 z 200 w trybie "cien"; 0 zapisow w zlym wierszu; log zgodny z regula 6 - sprawdzony na faktycznych plikach logu; zrodlo kodu: INSTALACJA w 2 z 2 przebiegow pytest; O9 jako informacja)

# T6 - Excel na sztucznym arkuszu - WYNIK (odbior 21.11.2026)

Wykonawca: sesja T3/T6/T5. `<K>` = `<PC-katalog>\t0\odbior\Stanowisko` (instalacja wspolna 0.3.1, GOTOWE 02:51:47),
`<ST>` = `<PC-katalog>\t0\repo\Ramki\stanowisko`, `<ODB>` = `<PC-katalog>\t0\repo\Ramki\etap3\odbior_koncowy`,
`<ROB>` = `<PC-katalog>\koordynator\robocze\odbior\T6`.

## Polecenia (plik `krok_t6.cmd`, uruchomiony `cmd /c` o 02:54:31; polecenia planu bez zmian, dodane tylko `< NUL`)

    set QT_QPA_PLATFORM=offscreen
    call <K>\Polecenie.cmd narzedzia\arkusz_syntetyczny.py --wierszy 30000 --zapytan 200 > <ROB>\t6_arkusz.txt 2>&1 < NUL
    call <K>\Polecenie.cmd <ODB>\narzedzia\pytest_instalacja.py --st <ST> --wynik <ROB>\t6_zrodlo_kodu.txt -- <ST>\testy\test_excel.py -q -s -rA -p no:cacheprovider --rootdir <ST> > <ROB>\t6_excel.log 2>&1 < NUL
    call <K>\Polecenie.cmd <ODB>\narzedzia\pytest_instalacja.py --st <ST> --wynik <ROB>\t6_zrodlo_kodu_2.txt -- <ST>\testy\test_aplikacja_rano.py -q -s -rA -p no:cacheprovider --rootdir <ST> -k "test_k3_excel_pytaj or test_k3_excel_cien" > <ROB>\t6_aplikacja.log 2>&1 < NUL

| Krok | Czas (zegar `.cmd`) | Kod | Wynik |
|---|---|---|---|
| `arkusz_syntetyczny.py` | 2:54:31,55 - 2:54:31,85 | 0 | `wierszy 30000 (scenariusze 297, tlo 29703); zapytan 200: jeden_wiersz 110, juz_odhaczone 19, wskaz_wiersz 71` |
| `test_excel.py` przez `pytest_instalacja.py` | 2:54:31,85 - 2:55:17,54 | 0 | `129 passed in 43.03s`; wierszy `PASSED` 129, `FAILED` / `ERROR` 0; `WERDYKT ZRODLA KODU: INSTALACJA` |
| `test_aplikacja_rano.py -k ...` przez `pytest_instalacja.py` | 2:55:17,54 - 2:55:24,24 | 0 | `2 passed, 26 deselected in 4.07s`; `WERDYKT ZRODLA KODU: INSTALACJA` |

Jedna proba kazdego polecenia, bez powtorek.

## Zrodlo kodu (warunek planu: INSTALACJA w kazdym przebiegu)

- `t6_zrodlo_kodu.txt`: wersja programu 0.3.1; z instalacji 17 modulow, z repo poza testami 0 modulow, modulow testow z
  repo 3; pliki `*.py` instalacji = repo: 79 z 79; `WERDYKT ZRODLA KODU: INSTALACJA`.
- `t6_zrodlo_kodu_2.txt`: z instalacji 51 modulow, z repo poza testami 0, modulow testow z repo 4; pliki 79 z 79;
  `WERDYKT ZRODLA KODU: INSTALACJA`.
- Plik ustawien domyslnych w testach: `<ST>\ustawienia.toml` (stala ustawiona w procesie testow - wg narzedzia).
- Odstepstwo O14 NIE zachodzi (0 modulow programu z repo, kod 0 w obu przebiegach).

## Liczby kryterium (policzone z plikow wyniku, nie tylko z `PASSED`)

1. **200 zapytan na 30 tys. wierszy, wlasciwa klasa: 200 z 200.** Z wyjscia `-s` testu
   `test_k1_200_zapytan_wlasciwa_klasa` w `t6_excel.log`: tabela pulapek ma 31 wierszy `ok / razem`; suma kolumn policzona
   przez wykonawce (awk): ok 200, razem 200; wiersz testu `RAZEM: 200 z 200`; klasy i reguly:
   `('jeden_wiersz', 2): 76, ('jeden_wiersz', 3): 34, ('juz_odhaczone', 4): 19, ('wskaz_wiersz', 5): 71` (suma 200).
   Arkusz: 30000 wierszy (`t6_arkusz.txt`).
2. **Tryb "pytaj": 200 z 200, 0 zlych wierszy.** `test_k1_zero_zapisow_w_zlym_wierszu` (wyjscie `-s`):
   `wyniki: {'zapisano': 110, 'wskazano_recznie': 38, 'juz_odhaczone': 19, 'pominieto': 33}` (suma 200);
   `zapisow 148: z wyboru programu 110, wiersz wskazany przez test 38; w zlym wierszu 0`.
   Faktyczny plik logu tego testu (`log_excel.csv`, 204 wiersze danych): zapisano 110, wskazano_recznie 38, juz_odhaczone
   19, pominieto 33 (= 200 wpisow koncowych, 200 roznych par zlecenie-kuweta) + 4 wpisy `blad` (odmowa zapisu "pole B w
   innym kolorze" po wskazaniu wiersza - potem `pominieto`; test oczekuje dokladnie 4); tryb `pytaj` w 204 z 204 wierszy.
   Dodatkowo `test_k5_zapis_dotyka_tylko_koloru_jednej_komorki` PASSED, `test_k4_domyslnie_pytaj_przed_zapisem` PASSED,
   `test_aplikacja_rano.py::test_k3_excel_pytaj_propozycje_rowne_kompletnym_i_tylko_kolor_wlasciwych_komorek` PASSED
   (log tego testu: 25 wierszy, tryb `pytaj` 25).
3. **Tryb "cien": 200 z 200, 0 zapisow.** `test_k4_tryb_cien_nie_zapisuje_niczego` (wyjscie `-s`):
   `tryb cien: {'tylko_log': 148, 'juz_odhaczone': 19, 'pominieto': 33}; zapisow koloru: 0` (suma 200).
   Faktyczny plik logu: 200 wierszy danych, tylko_log 148, juz_odhaczone 19, pominieto 33, tryb `cien` 200 z 200,
   200 roznych par zlecenie-kuweta. `test_k4_zapisz_cien_loguje_caly_piec` PASSED (log: 40 wierszy `tylko_log`, tryb `cien`),
   `test_aplikacja_rano.py::test_k3_excel_cien_tylko_log_i_restart_okna_excela` PASSED.
4. **Log zgodny z regula 6** (pola `data;godzina;kuweta;folder;numer_zlecenia_b;arkusz;wiersz;kto_zatwierdzil`):
   `test_k3_log_csv_ma_pola_reguly_6` PASSED ORAZ kontrola wykonawcy na 6 faktycznych plikach `log_excel.csv` z tego
   przebiegu (skopiowane z katalogow `tmp_path` pytest zaraz po tescie do `<ROB>\robocze\logi_excel\` - poza dowodami;
   wynik kontroli: `t6_log_regula6.txt`, same liczniki):
   - naglowek: 8 pierwszych pol = pola reguly 6 w tej kolejnosci w 6 z 6 plikow (potem `skoroszyt;regula;wynik;tryb`);
   - 476 wierszy danych lacznie (204 + 4 + 200 + 40 + 3 + 25): `data` w postaci RRRR-MM-DD, `godzina` GG:MM:SS, `folder`,
     `arkusz` i `kto_zatwierdzil` niepuste w 476 z 476; `wiersz` (liczba) i `numer_zlecenia_b` niepuste we wszystkich
     wpisach wskazujacych wiersz (zapisano / wskazano_recznie / juz_odhaczone / tylko_log / blad); puste tylko w wpisach
     `pominieto` (zaden wiersz nie zostal wskazany);
   - `kuweta` pusta w 4 z 476 wierszy: po 2 wpisy `pominieto` w logu trybu "pytaj" i trybu "cien" - to 2 zapytania pulapki
     `brak_numeru` (zlecenie bez numeru kuwety w danych sztucznych; program niczego nie zapisal). Patrz "Do decyzji".

## Co jeszcze liczylo na PC (kryterium T6 nie jest czasowe)

02:54-02:55: T1 `krok_4.cmd` (pelny pytest, tor 1, od 02:53:21), T10 `krok_t10.cmd` (tor 2, od 02:52:26), T12 `krok_A4.cmd`
(tor 4, od 02:54:09); wolny RAM 74822 MB. Wartosci czasowe z wyjscia testu (informacyjnie): odczyt i indeks 30 tys.
wierszy pierwszy 203 ms, ponowny 21 ms; zapytanie mediana 0,012 ms, max 0,094 ms (200 zapytan).

## Procesy po tescie

`powershell Get-Process python` po tescie: zadnego procesu tej sesji (cudze: T1, T10, T12 i znany PID 12012).

## Werdykt czesci kryterium

| Czesc kryterium | Liczba | Werdykt |
|---|---|---|
| 200 zapytan na 30 tys. wierszy - wlasciwa klasa | 200 z 200 (30000 wierszy) | ZAL |
| tryb "pytaj" | 200 z 200 obsluzonych; 148 zapisow, w zlym wierszu 0 | ZAL |
| tryb "cien" | 200 z 200 wpisow logu; zapisow koloru 0 | ZAL |
| 0 zlych wierszy | 0 | ZAL |
| log zgodny z regula 6 | 6 z 6 plikow: naglowek zgodny; 476 wierszy sprawdzonych (uwaga o 4 pustych `kuweta`) | ZAL |
| zrodlo kodu = INSTALACJA | 2 z 2 przebiegow pytest, kod 0 | spelnione (bez O14) |

Odstepstwa: brak obnizajacych wynik. **O9 - informacja** (arkusz w pamieci, bez programu Excel; Excel przez COM = T17);
wg ustalenia koordynatora 21.11 wynik T6 przy liczbach w normie i werdykcie INSTALACJA = ZAL. Nowych odstepstw brak.
Polecen planu nie trzeba bylo zmieniac.

## Do decyzji koordynatora

- Regula 6 a zlecenie bez numeru kuwety: w faktycznym logu wpis `pominieto` takiego zlecenia ma PUSTE pole `kuweta`
  (2 wpisy na 200 w kazdym trybie), a kazdy wpis `pominieto` (33 na 200) ma puste `wiersz` i `numer_zlecenia_b` (zaden
  wiersz arkusza nie zostal wskazany). Test `test_k3_log_csv_ma_pola_reguly_6` uznaje to za zgodne (sprawdza `pominieto`
  z pustym wierszem); wykonawca policzyl to jako zgodne z regula 6 (pola sa, wartosci brak, bo nie istnieja).
- Krokow dodatkowych (poza planem) uzyto tylko do odczytu: `robocze\sprawdz_log.py`, `robocze\sprawdz_log2.py` (liczniki z
  kopii logow; bez wartosci kolumny `folder`).

## Dowody (w `<ROB>`)

`t6_arkusz.txt`, `t6_excel.log`, `t6_aplikacja.log`, `t6_zrodlo_kodu.txt`, `t6_zrodlo_kodu_2.txt`, `t6_log_regula6.txt`
(liczniki kontroli logu), `kody.txt`, `krok_t6.cmd`, `WYNIK.md`, `t6_wynik.md` (kopia `WYNIK.md` pod nazwa z planu).
Kopie logow Excela (dane sztuczne, kolumna `folder`) sa w `<ROB>\robocze\logi_excel\` - NIE ida do dowodow (plan).
