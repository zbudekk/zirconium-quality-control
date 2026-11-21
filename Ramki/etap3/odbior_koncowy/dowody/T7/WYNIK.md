WERDYKT T7: ZAL z odstepstwem O12 (przypadki 6 z 6 z wynikiem "ZAL z odstepstwem O12" - komunikat jest, program pracuje dalej, stan odtworzony, ale tekst komunikatu w PW zal. F: 0 z 6; czesc A 49 passed / 0 failed, zrodlo kodu INSTALACJA 15 z 15; proby B1, B2, B3 wykonane; zastrzezenie do przypadku 4 - do decyzji koordynatora)

# T7 - Odpornosc - wynik odbioru 21.11.2026

Wykonawca: sesja wykonawcy testow koncowych (T12, T7, T13), tor 4 ciezkich krokow. Godziny: 03:03:17 (B1) - 03:35 (kontrola koncowa).
Paczka: `Stanowisko_0.3.1.zip` (commit 571e186). Czesc A i proby B1 / B1b: instalacja WSPOLNA `<PC-katalog>\t0\odbior\Stanowisko`
(znak `T0\GOTOWE.txt` z 02:51:47 sprawdzony - czekania nie bylo; w `<K>` niczego nie zmieniono, tylko `Polecenie.cmd`). Proby B2 i B3:
instalacja `<PC-katalog>\t0\odbior_t12\Stanowisko` po zakonczeniu T12 (wersja 0.3.1 po powrocie), program z WLASNYM plikiem ustawien.

## Kryterium (plan etapu, sekcja 7)

Zabicie silnika w trakcie analizy; zamkniecie programu w polowie wieczoru; brak folderu "Cyrkon"; brak sieci; brak ramki; baza
zajeta - za kazdym razem komunikat z PW zal. F i dalsza praca; stan odtworzony z bazy.

## Tabela 6 przypadkow

| Nr | Przypadek | Testy czesci A (PASSED, zrodlo kodu) | Komunikat (doslowny tekst, bez znakow diakrytycznych) | W PW zal. F | Program pracuje dalej | Stan odtworzony z bazy (liczby) | Wynik |
|---|---|---|---|---|---|---|---|
| 1 | zabicie silnika w trakcie analizy | 5 z 5 (2 + 3), INSTALACJA | "Analiza skanu nie powiodla sie" / "Program nie przeanalizowal tego skanu (analiza zostala przerwana). Zeskanuj plytke ponownie." (rodzaj `blad_analizy`; asercja `test_aplikacja.py:502-503`). B3: log "analiza skanu <sha16> nie dala wyniku (proces)", zdarzenie `blad_analizy` z opisem "... analiza przerwana" | NIE | TAK - B3: nowy proces silnika w tej samej sekundzie, 3. skan przyjety (34,0 s), program do konca `--zamknij-po 600`, kod 0; testy: nastepny skan "przyjety" | TAK - B3: 3 skany z 3 maja status w bazie (2 z wynikiem + 1 `blad`); zdarzenia `blad_analizy` 1, `blad_analizy_rodzaj` 1 (`{"rodzaj": "proces"}`); start kontrolny: "plikow znanych 3", skany nadal 3 | ZAL z odstepstwem O12 |
| 2 | zamkniecie programu w polowie wieczoru | 4 z 4 (3 + 1), INSTALACJA | "Program wznowil prace" / "Po ponownym uruchomieniu program dokancza zalegle skany: {ile}." (rodzaj `wznowiono`; asercje `test_aplikacja.py:220`, `:259`). B2: komunikat tylko na ekranie (w logu 0 razy - jak w planie); slady: log "(plik zastany - nadrabianie)", zdarzenie `nowy_skan` z `"zastany": true` | NIE | TAK - B2: po `Stop-Process` programu (3 z 3 procesow nie zyje po 1,5 s) i ponownym starcie program przyjal skany 2, 3, 4; kod 0 | TAK - B2: **4 skany z 4** w bazie; przy starcie "plikow znanych 1" (1. skan z bazy, nieliczony drugi raz); `nowy_skan` z `zastany` true: 1; `zadania_niezakonczone.json`: brak; testy: plytki i decyzje odtworzone (`test_aplikacja.py:214`, `test_ui_wieczor.py:1284`) | ZAL z odstepstwem O12 |
| 3 | brak folderu "Cyrkon" | 3 z 3 (2 + 1), INSTALACJA | "Brak folderu projektow" / "Program nie widzi folderu projektow - skany czekaja ({czeka}). Sprawdz, czy dysk z folderem projektow jest podlaczony, i kliknij 'Odswiez pule'. Jesli folder jest inny - zglos to." (rodzaj `pula_brak_folderu`; asercja `test_aplikacja.py:410`). B1: samokontrola kod 1, `BLAD folder_cyrkon: brak folderu projektow Cyrkon: <sciezka> - pula projektow jest pusta i skany czekaja bez wyniku; ...`. Na programie z paczki komunikat ekranu NIE ZMIERZONY (w logu `pula_brak_folderu` 0 wierszy - B1 i B1b) | NIE (zblizony objaw: "Wszystkie gniazda szare (brak projektow)") | TAK - B1: program 30 s bez folderu, kod 0; B1b: program 90 s bez folderu z czekajacym skanem, kod 0, skan nie ginie | TAK - B1b: po przywroceniu folderu "zadan wznowionych 1, plikow znanych 1", 1 skan z 1 przeanalizowany (56,3 s), `nowy_skan` 1 (bez duplikatu); B1: zdarzenia 2 -> 4 | ZAL z odstepstwem O12 |
| 4 | brak sieci | 4 z 4 (1 + 2 + 1), INSTALACJA | w testach przypadku brak asercji komunikatu tekstowego programu; sygnal: ikona stanu "brak lacznosci" na ramce (`test_ramka.py:1128-1130`), tekst wyjatku "Excel niedostepny" (`test_excel.py:450`). Samokontrola programu z paczki: `OSTRZEZENIE ramka_wieczorna: ramka wieczorna nieobecna: brak polaczenia z ramka-w.local:8765 (gaierror); wlacz ramke, sprawdz Wi-Fi ..., bez ramek program dziala - rozkladanie wedlug podpisow na ekranie`. Komunikat programu dla tego stanu (z przypadku 5): "Ramka wieczorna nie odpowiada" / "Ramka poranna nie jest podlaczona" | NIE (zal. F opisuje zachowanie: "Ramka poranna nie laczy sie z laptopem - Ramka trzyma ostatni plan i potwierdzenia w pamieci i dosyla je po powrocie sieci ...") | TAK - testy: 500 potwierdzen z 500 doslanych bez luki i powtorki (100 powtorzen x 5), plan trzymany na ramce, po bledzie Excela kolejne dopasowanie dziala; proby B: program pracowal przy nieosiagalnych ramkach | nie dotyczy bazy programu (stan trzyma ramka: 500 z 500 potwierdzen po powrocie sieci); asercji restartu brak (plan liczy stan z bazy w przypadkach 1, 2, 6 i probach B) | ZAL z odstepstwem O12 - z zastrzezeniem (nizej) |
| 5 | brak ramki | 2 z 2 (1 + 1), INSTALACJA | "Ramka poranna nie jest podlaczona" / "Program dziala bez ramki - rozkladaj prace wedlug ekranu: kuweta po kuwecie (Enter = rozlozona, Backspace = cofnij, cyfry i Enter = wybor kuwety)."; "Excel nie jest podlaczony" (rodzaje `ramka_niedostepna`, `excel_niedostepny`; asercje `test_ui_rano.py:387`, `:391`, `test_aplikacja_rano.py:940`) | NIE (zblizone objawy: "Diody nie swieca ... bez diod poranek dziala po podpisach na ekranie laptopa", "Excel nie zapisuje") | TAK - piec zamkniety mimo wylaczonej ramki i braku Excela (`test_aplikacja_rano.py:943`), nowy piec otwarty, okno dziala (`test_ui_rano.py:398`) | asercji restartu brak (jak w przypadku 4) | ZAL z odstepstwem O12 |
| 6 | baza zajeta | 31 z 31 (2 + 1 + 1 + 27), INSTALACJA | "Baza jest zajeta" / "Inny program trzyma baze stanowiska - niczego nie zapisano. Sprobuj ponownie za chwile."; "Decyzja NIE zostala zapisana" / "{co} - decyzja NIE jest zapisana: baza stanowiska byla zajeta przez inny program. Kliknij 'Ponow teraz'; ..."; "Polecenie NIE zostalo wykonane - baza zajeta" (rodzaje `baza_zajeta`, `decyzja_niezapisana`, `polecenie_niezapisane`; asercje `test_aplikacja.py:528`, `:866`, `test_p14_baza_zajeta.py:147`) | NIE (zal. F nie ma wiersza o bazie) | TAK - po zwolnieniu bazy zapis udany przy 3. probie, komunikat znika (`test_aplikacja.py:530`); "Ponow teraz" zapisuje decyzje (`test_p14_baza_zajeta.py:158`, `:303-304`) | TAK (asercje): wynik w bazie dokladnie 1 raz (`len(skany_w_bazie(st)) == 1`, `test_aplikacja.py:530`, `:870`); `count(*) FROM skany == 1` po zwolnieniu blokady (`test_baza.py:407`); 3 zdarzenia ramki zapisane po zwolnieniu (`test_aplikacja_rano.py:1335`). Proby recznej plan nie przewiduje | ZAL z odstepstwem O12 |

Liczniki: **przypadki 6 z 6** (silnik 1, zamkniecie 1, brak "Cyrkon" 1, brak sieci 1, brak ramki 1, baza zajeta 1), w tym "ZAL z
odstepstwem O12 (komunikat spoza zal. F)": **6**; FAIL: 0; komunikaty zgodne z zal. F: **0 z 6** (zgodne z tabela technika
`instrukcje\co_robic_gdy_nie_dziala.md`: 6 z 6); zrodlo kodu w testach: INSTALACJA (15 z 15 przebiegow, 0 modulow z repo, pliki
`*.py` instalacji = repo 79 z 79) - O14 nie zachodzi. Teksty komunikatow i wiersze zal. F: `t7_komunikaty.md` (lista do zadania
wlasciciela "uzupelnic zal. F albo zmienic napis").

## Czesci testu

| Czesc | Werdykt | Liczby | Dowod |
|---|---|---|---|
| A - testy na kodzie z instalacji | ZAL | 15 polecen z 15 z kodem 0; 49 passed, 0 failed, 0 error, 0 skipped; `WERDYKT ZRODLA KODU: INSTALACJA` 15 z 15; 4 min 10 s | `t7_wynik.md`, `t7_<nr>.log`, `t7_<nr>_zrodlo_kodu.txt` (15 par), `krok_A.cmd` |
| B1 - brak folderu "Cyrkon" | wykonana; samokontrola kod 1 z wierszem o folderze: TAK; komunikat `pula_brak_folderu` w logu: 0 wierszy (oczekiwanie planu niespelnione doslownie - program nie loguje komunikatow ekranu, a ten pokazuje tylko przy czekajacym skanie) | kody 0, 0 (program), 0 / 1 / 0 (samokontrola) | `t7_proby_reczne.md`, `t7_b1_*` |
| B1b - uzupelnienie (spoza planu): brak folderu + czekajacy skan | zgodna z oczekiwaniem | kody 0, 0; skan czeka 78 s, po przywroceniu folderu 1 z 1 przeanalizowany | `t7_b1b_*` |
| B2 - zakonczenie programu w polowie wieczoru | zgodna z planem | regula PID: 0 wierszy przed, 1 po; 3 z 3 procesow nie zyje po 1,5 s; 4 skany z 4; `zastany` true 1 raz; kod 0 | `t7_b2_pid.txt`, `t7_b2_przebieg.txt`, `t7_b2_baza.txt`, `t7_b2_symulator.json`, `t7_b2_log_programu.txt` |
| B3 - zabicie silnika w trakcie analizy (pierwsze wykonanie) | zgodna z planem | regula PID: dokladnie 2 procesy Pythona bazowego w 5 s po posredniku (2 odczyty), zgodna z lancuchem rodzic-potomek; `blad_analizy` w logu i zdarzeniach; 3. skan przyjety; kod 0 | `t7_b3_pid.txt`, `t7_b3_przebieg.txt`, `t7_b3_baza.txt`, `t7_b3_symulator.json`, `t7_b3_log_programu.txt` |

## Co NIE ZMIERZONO

1. Komunikaty na EKRANIE programu z paczki w probach B (`pula_brak_folderu`, `wznowiono`, tekst `blad_analizy`): program nie zapisuje
   komunikatow ekranu do logu ani do zdarzen - w probach B widac tylko ich slady (log, zdarzenia, samokontrola); sam komunikat
   potwierdzaja testy czesci A na kodzie z instalacji.
2. Przypadek 4 (brak sieci): komunikat tekstowy programu przy utracie sieci nie ma asercji w testach przypadku 4; sieci fizycznie nie
   odcinano; proby recznej plan nie przewiduje.
3. Przypadki 4, 5, 6: brak prob recznych na programie z paczki (plan: tylko testy czesci A); wyjatek - samokontrola z proba polaczenia
   i praca programu przy nieosiagalnych ramkach we wszystkich probach B.
4. Proby B2 / B3 ze skanami o statusie "przyjety": wszystkie skany ze zrodla planu (`syntetyczne_R59_P2`, plytki poranne) dostaly
   status `plytka_nie_z_trybu` (program startuje w trybie "Wieczor"); analiza byla pelna (23-56 s, 12 prac).
5. "Stan odtworzony z bazy" dla przypadkow 4 i 5: brak asercji restartu (plan liczy go w przypadkach 1, 2, 6 i probach B).

## Odstepstwa

- **O12** (decyzja koordynatora nr 14): 6 z 6 przypadkow - tekst komunikatu spoza PW zal. F (zal. F to 12 objawow, bez tekstow
  komunikatow programu). Pozycja do zadan wlasciciela: uzupelnic zal. F albo zmienic napisy - lista w `t7_komunikaty.md`.
- O14: nie zachodzi. Nowych odstepstw brak.

## Polecenia planu zmienione / potkniecia

Pelna lista (9 pozycji): `t7_proby_reczne.md`, sekcja "Potkniecia i zmiany wobec planu". Najwazniejsze:
1. B1: szukanie `pula_brak_folderu` w `stanowisko.log` - 0 wierszy (komunikat nie trafia do logu i wymaga czekajacego skanu) -> proba B1b.
2. B2 / B3: dziennik symulatora (`--dziennik`) powstaje dopiero po jego zakonczeniu - chwile "po zapisie 2. skanu" ustalono po
   plikach w folderze eksportu (2. plik `*.stl`, rozmiar staly 2,5 s).
3. Proby B2 / B3 / B1b prowadzil sterownik PowerShell 7 pod blokada tor 4 (polecenia planu bez zmian; PID wylacznie z reguly planu).
4. Program i samokontrola przez `Polecenie.cmd ... --ustawienia <ROB>\ustawienia_<proba>.toml` (zasada 3); dane prob w `robocze\`.
5. Czesc A: 15 polecen doslownie z planu - bez zmian.

## Do decyzji koordynatora / wlasciciela

1. (wlasciciel, O12) 6 komunikatow spoza PW zal. F - uzupelnic zalacznik albo zmienic napisy (`t7_komunikaty.md`).
2. (koordynator) Przypadek 4: czy ikona "brak lacznosci" na ramce + komunikaty przypadku 5 + ostrzezenie samokontroli wystarczaja jako
   "komunikat" przy braku sieci (przyjeto: tak, "ZAL z odstepstwem O12"), czy brak asercji komunikatu tekstowego w testach przypadku 4
   liczyc jako "brak komunikatu" = FAIL przypadku (wtedy T7 = FAIL 1 z 6).
3. (koordynator) Przypadek 3: komunikat `pula_brak_folderu` na programie z paczki niezmierzony (tylko test czesci A i wiersz
   samokontroli) - czy to wystarcza; krok B1 planu do poprawienia (log nie zawiera komunikatow ekranu).
4. (koordynator) Zrodlo skanow w probach B2 / B3 daje status `plytka_nie_z_trybu` - czy powtorzyc proby na skanach wieczornych.
5. (informacja) Skan, ktorego analize przerwano zabiciem silnika, po restarcie programu NIE jest analizowany ponownie (status `blad`,
   "plikow znanych 3") - zgodnie z trescia komunikatu technik ma zeskanowac plytke ponownie.

## Dowody w tym katalogu

Lista z planu: `t7_<nr><a-d>.log` i `t7_<nr><a-d>_zrodlo_kodu.txt` (15 par), `t7_proby_reczne.md`, `t7_b2_pid.txt`,
`t7_b2_symulator.json`, `t7_komunikaty.md`, `t7_wynik.md`. Dodatkowo: `t7_b1_*`, `t7_b1b_*`, `t7_b2_*`, `t7_b3_*`,
`t7_45_samokontrola_z_proba_polaczenia.log`, `ustawienia_b1.toml`, `_b1b`, `_b2`, `_b3`, `krok_*.cmd`, `kody.txt`, `czasy.txt`.
Pliki robocze (bazy, skany STL 53-58 MB, kopia folderu projektow, sterowniki) w `robocze\` - NIE kopiowac do repo. Pliki z
przekierowania `cmd >` maja CRLF, a `ustawienia_*.toml` znaki spoza ASCII (komentarze wzoru) - przed `git add`: `dowody_lf.py --napraw`.
W plikach dowodow (142 pliki T7 + T12 + T13) 0 trafien nazw folderow / plikow z `Prace_test` (32 nazwy sprawdzone).

Co jeszcze liczylo na PC (`ciezkie.log`): tor 1 - T1 (pelny pytest do 03:22:57, potem krok 5); tor 2 - T10 do 03:06:49; tor 3 - T5 do
03:03:56. Kroki T4 / T2 (pomiary czasowe) w czasie prob B nie trwaly. Po testach: 0 wlasnych procesow `python`.
