WERDYKT T3: ZAL z odstepstwem O5 (32 z 32 wierszy z ekranu; ekran list: tak 8, czesciowo 1, nie dotyczy 1, nie 0; sterownik kod 0, 10,1 s; testy uzupelniajace 33 passed i 60 passed)

# T3 - Poranek od poczatku do konca (SE10 przez ekran) - WYNIK (odbior 21.11.2026)

Wykonawca: sesja T3/T6/T5 (tor ciezkich krokow 3). Plik prowadzony przyrostowo.

## Stan wejsciowy

- Znak gotowosci: `<PC-katalog>\koordynator\robocze\odbior\T0\GOTOWE.txt` z 2026-11-21 02:51:47 (instalacja wspolna 0.3.1,
  commit 571e186cb817, z `/testy`). Plan przeczytany w czasie oczekiwania (02:48-02:51).
- `<K>` = `<PC-katalog>\t0\odbior\Stanowisko`, `<REPO>` = `<PC-katalog>\t0\repo`, `<ST>` = `<REPO>\Ramki\stanowisko`,
  `<ODB>` = `<REPO>\Ramki\etap3\odbior_koncowy`, `<ROB>` = `<PC-katalog>\koordynator\robocze\odbior\T3`.
- Kroki jako pliki `.cmd` w `<ROB>` (kazde `Polecenie.cmd` z `call`, wejscie `< NUL`, `set QT_QPA_PLATFORM=offscreen`,
  kod do `<ROB>\kody.txt`): `krok_t3_1_sterownik.cmd`, `krok_t3_2_se10.cmd`, `krok_t3_3_ekran.cmd`.

## Przebieg

### Krok 1 - sterownik (02:52:10-02:52:21)

Polecenie (plik `krok_t3_1_sterownik.cmd`; wobec planu DODANA opcja `--wymagaj-100` - tak kaze plan dla odbioru):

    set QT_QPA_PLATFORM=offscreen
    call <PC-katalog>\t0\odbior\Stanowisko\Polecenie.cmd <PC-katalog>\t0\repo\Ramki\etap3\odbior_koncowy\narzedzia\t3_poranek.py --testy <PC-katalog>\t0\repo\Ramki\stanowisko\testy --wyjscie <PC-katalog>\koordynator\robocze\odbior\T3\t3 --ustawienia-wzor <PC-katalog>\t0\odbior\Stanowisko\ustawienia.toml --wymagaj-100 > <PC-katalog>\koordynator\robocze\odbior\T3\t3_sterownik.log 2>&1 < NUL

- Kod wyjscia: **0** (`kody.txt`: `t3_sterownik KOD=0`). Jedna proba, bez powtorek.
- Czas: 10,1 s wg sterownika (`czas_s` w `t3_wynik.json`); zegar pliku `.cmd`: 2:52:10,91 -> 2:52:21,25 = 10,3 s.
- Program: wersja 0.3.1, interpreter `<K>\wersje\0.3.1\venv\Scripts\python.exe`, platforma Qt `offscreen` (z `t3_wynik.json`).
- Dwa ostatnie wiersze wyjscia (`t3_sterownik.log`, to samo w `t3_wynik.txt`):
  - `SE10 przez ekran: 32 z 32 wierszy zgodnych (wiersz z odczytem ekranu 'nie' / 'nie odczytano' = niezgodny); wg samego API sesji 32 z 32; listy kompletnych i brakow z ekranu: 8 z 9`
  - `WERDYKT T3: ZAL z odstepstwem O5 (32 z 32; ekran: tak 8, czesciowo 1, nie dotyczy 1, nie 0, nie odczytano 0)`
- Policzone z pliku `t3_wynik.txt` (nie z wiersza podsumowania): wierszy `R.. PASS` 32, wierszy `R.. FAIL` 0;
  `t3_wynik.json` `liczniki`: wierszy 32, zgodnych 32, niezgodnych 0, zgodnych_wg_api 32, niezgodnych_tylko_ekran 0,
  nie_policzono 0.
- Kolumna "ekran" 10 wierszy z listami kompletnych i brakow: "tak" 8 (R11, R14, R15, R21, R22, R28, R29, R30),
  "czesciowo" 1 (R31: po restarcie ekran pokazuje tylko ostatni zamkniety piec 3; piece 1 i 2 tylko z API),
  "nie dotyczy" 1 (R17: listy "do dofrezowania" ekran poranny nie pokazuje), "nie" 0, "nie odczytano" 0.
  R22: lista brakow z ekranu "tak"; druga czesc wiersza (1 praca nieznana nierozstrzygnieta) tylko z API - napisu
  `rano_nierozstrzygniete` z liczba 1 na ekranie BRAK (opis w wierszu "ekran R22" pliku wyniku).
- Pytanie okna przed "Zamknij piec" (P14): piec 1 - oczekiwane nie, bylo nie; piec 2 - oczekiwane wg zlecenia TAK, bylo
  NIE (sesja: nieznane 1; prace bez decyzji wg stanu okna 0); piec 3 - oczekiwane nie, bylo nie. To ta sama obserwacja,
  co w planie ("Do oceny koordynatora") i w RAPORT.md 4a wiersz 6 - nie jest roznica wobec tabeli SE10.
- Co jeszcze liczylo na PC (kryterium T3 nie jest czasowe): T12 `krok_A2.cmd` (tor 4, start 02:52:15); wolny RAM 76936 MB.

### Krok 2 - test uzupelniajacy SE10 na poziomie sesji (02:52:24-02:52:26)

    call <K>\Polecenie.cmd -m pytest <ST>\testy\test_session_rano.py -q -rA -p no:cacheprovider --rootdir <ST> -k "se10" --basetemp <ROB>\t3_tmp > <ROB>\t3_se10.log 2>&1 < NUL

(polecenie planu bez zmian; pelne sciezki w `krok_t3_2_se10.cmd`). Kod **0**; wiersz podsumowania
`33 passed, 40 deselected in 0.39s`; wierszy `PASSED` w logu 33 (oczekiwane 33). Kod programu w tym tescie pochodzi z
`<REPO>` (zwykly `-m pytest`; z paczki interpreter i pakiety) - tak stanowi plan dla testow uzupelniajacych T3.

### Krok 3 - testy uzupelniajace ekranu porannego (02:52:30-02:53:35)

    call <K>\Polecenie.cmd -m pytest <ST>\testy\test_ui_rano.py <ST>\testy\test_aplikacja_rano.py -q -rA -p no:cacheprovider --rootdir <ST> > <ROB>\t3_ekran.log 2>&1 < NUL

(polecenie planu bez zmian). Kod **0**; wiersz podsumowania `60 passed in 64.01s (0:01:04)`; wierszy `PASSED` 60,
`FAILED` 0. 3 wiersze logu zaczynajace sie od `ERROR` to przechwycone wpisy dziennika programu w testach zaliczonych
(sekcja `-rA`), nie bledy testow. Co jeszcze liczylo: T10 `krok_t10.cmd` (tor 2, od 02:52:26), T12 `krok_A2.cmd` (tor 4),
T1 `krok_4.cmd` (tor 1, od 02:53:21); testy czasowe tego pliku przeszly (0 nieudanych).

## Procesy po tescie

`powershell Get-Process python` o 02:53:40: zadnego procesu tej sesji (widoczne cudze: T10, T1, T12 oraz znany PID 12012).

## Baza SE10 dla T8 i T9 (ZOSTAJE)

- **`<PC-katalog>\koordynator\robocze\odbior\T3\t3\baza\stanowisko.sqlite`** (94 208 bajtow, SHA-256
  6d67ba9db8b1cfd284a294b7c3dbcdf651efa7ca9b4779f0c7926843b1fc83e7 po zakonczeniu sterownika). Katalog do T9:
  `<PC-katalog>\koordynator\robocze\odbior\T3\t3\baza`.
- Caly katalog wyjscia sterownika `<ROB>\t3\` zostaje (baza, `dane\wyniki`, `logi\`, `ustawienia_t3.toml`).
- Katalog `<ROB>\t3_tmp\` (z `--basetemp`) zostaje; baza `t3_tmp\se100\dane\stanowisko.sqlite` to INNA baza (test pytest)
  - do T8 jej nie uzywac.
- Uwaga dla zbierajacego dowody: `<ROB>\t3\` i `<ROB>\t3_tmp\` zawieraja bazy - NIE ida do repo. Plan kaze trzymac je
  wlasnie pod tymi sciezkami (T8, T9), wiec nie przeniesiono ich do `robocze\`. Dowody to tylko pliki z listy nizej.

## Dowody (w `<ROB>`)

`t3_wynik.txt`, `t3_wynik.json` (kopie z `<ROB>\t3\`), `t3_sterownik.log`, `t3_se10.log`, `t3_ekran.log`, `kody.txt`,
`krok_t3_*.cmd`, `WYNIK.md`, `t3_wynik.md` (kopia `WYNIK.md` pod nazwa z listy dowodow planu). Logi z przekierowania
`cmd >` maja CRLF i znaki spoza ASCII - przed `git add` przejda przez `dowody_lf.py --napraw` (plan); wykonawca ich nie zmienial.

## Werdykt czesci kryterium

| Czesc kryterium | Liczba | Werdykt |
|---|---|---|
| SE10 przez ekran (3 piece, dofrezowany zab, poprawka, dwuznaczna, nieznana): wiersze zgodne z tabela oczekiwan | 32 z 32 (liczone z ekranu; wg API 32 z 32), kod 0 z `--wymagaj-100` | ZAL z odstepstwem O5 |
| listy kompletnych i brakow z ekranu (10 wierszy) | tak 8, czesciowo 1 (R31), nie dotyczy 1 (R17), nie 0, nie odczytano 0 | ZAL z odstepstwem O5 |
| testy uzupelniajace | 33 passed (kod 0); 60 passed (kod 0) | zgodne z planem |

Odstepstwa: **O5** (wyniki skanow sztuczne, zegar staly, zlecenia wpisane funkcja testu, okno `offscreen`, ramki i Excel
wylaczone; R31 "czesciowo", R17 "nie dotyczy"). Nowych odstepstw brak. Polecen planu nie trzeba bylo zmieniac (dodano
tylko `--wymagaj-100` - wg planu - oraz `< NUL`).

Do decyzji koordynatora / wlasciciela (nie obniza wyniku T3): okno NIE zadalo pytania przed "Zamknij piec" 2, choc sesja
liczy 1 prace nieznana jako nierozstrzygnieta (praca ma decyzje "bez projektu") - RAPORT.md 4a wiersz 6; R22: napisu
ekranu z liczba prac nierozstrzygnietych brak (ta czesc wiersza tylko z API).
