# Raport koncowy etapu 3 - WYPELNIONY CZESCIOWO (testy wykonane 21.11.2026; reszta w toku)

Stan: **21.11.2026 (paczka E3-ODBIOR): wypelnione wiersze testow WYKONANYCH - T0, T1, T3, T5, T6, T7, T10, T12, T13
(pierwszy przebieg) - oraz kontrola zestawu T14.** T2, T4, T8, T9, T11 i drugi przebieg T13 sa w toku: ich pola maja
znacznik `[W TOKU: T<nr>]` (uzupelni je kolejny etap); liczniki koncowe: `[W TOKU: liczniki]`. Kazda liczba ponizej jest
przepisana z `dowody/T<nr>/WYNIK.md` (kopie plikow wykonawcow; opis katalogu: `dowody/README.md`). Puste pola = decyzja
albo wpis koordynatora / wlasciciela. Dokument dla wlasciciela o instalacji i aktualizacji: `POKAZ_G3.md`.
Przepis testow: `PLAN_TESTOW.md`; odlozone: `ODLOZONE.md`; proba z czlowiekiem: `T14/README.md`.
Etap 2 paczki E3-ODB (20.11 wieczor): wpisane decyzje koordynatora do 6 pytan z etapu 1 (sekcja 8, pozycje 12-17),
zaktualizowane odstepstwa O3-O7, nowe O11 i O12, braki B1, B2, B4-B6 z decyzja; liczniki T2, T3, T4, T7, T11, T13 w
tabeli 2 dopasowane do decyzji.

Runda 1 recenzji PR #44 (21.11): "ZAL z odstepstwem" jest OSOBNA wartoscia wyniku z wlasnym licznikiem (decyzja
koordynatora nr 7 po recenzji, pozycja 18 w sekcji 8); nowe odstepstwa O13, O14, poprawione O1, O4, O6, O8, O10; lista
odstepstw do decyzji wlasciciela w sekcji 4a; liczniki T2, T3, T11 dopasowane do poprawionych narzedzi.

Zasady wypelniania: wynik tylko `ZAL` / `ZAL z odstepstwem O<n>` / `FAIL` / `ODLOZONE` / `NIE ZMIERZONO` (czesc kryterium).
**"ZAL z odstepstwem" NIE jest "ZAL"**: wpisuje sie je zawsze z numerem odstepstwa z sekcji 4, liczy w osobnym liczniku
(podsumowanie pod tabela 2 i sekcja 3) i kazde takie odstepstwo trafia na liste decyzji wlasciciela (sekcja 4a). Test,
ktorego kryterium zmierzono inaczej niz doslownie (odstepstwo w sekcji 4), moze miec najwyzej "ZAL z odstepstwem" - takze
gdy wszystkie liczby sa w normie. Liczniki, nie procenty;
kazdy FAIL zostaje w tabeli "FAIL i poprawki" takze po poprawce; dowody = sciezki wzgledem
`Ramki/etap3/odbior_koncowy/dowody/`.

Runda 2 recenzji PR #44 (21.11): odstepstwo nie jest juz przypisane testom, ktore da sie wykonac doslownie wg sekcji 7
planu etapu (T1, T8, T9, T10, T6, T11; warunkowo T4 i T7) - podsumowanie pod tabela 2, sekcja 4 (O6, O9, O14) i 4a;
O2 uzupelnione o sposob porownania kopii bazy, O7 o pomiar pamieci, O13 o zalozenie o pracach zoltych.

## 1. Wydanie

| Pole | Wartosc |
|---|---|
| Numer wersji (N) | 0.3.1 |
| Plik paczki | `Stanowisko_0.3.1.zip` (na PC: `<PC-katalog>\wydania\`; poza repo) |
| SHA-256 paczki | `f5affa81aea9969c6c42bf8e9e56ed6ad564dc948b15e92b8c7989383e24eec8` (certutil = plik `.zip.sha256` = wiersz `SHA256SUMS_wydania.txt`: 1 z 1 - `dowody/T0/t0_sha256.txt`) |
| Rozmiar, liczba plikow programu, liczba kol | ZIP 444 935 199 bajtow (424,3 MB); w paczce 210 plikow + `SHA256SUMS` (po rozpakowaniu 211 plikow, 462 922 182 bajtow - `dowody/T0/WYNIK.md`); program 131 plikow, kola 73, kola testowe 3 (`Ramki/etap3/wydania/README.md`; instalator: "zgodne 210 z 210", "program: skopiowano 131 plikow" - `dowody/T0/t0_zainstaluj_1.log`) |
| Commit `main`, z ktorego zbudowano paczke | `571e186cb8178209da670dde244dfc56bba5e300` |
| Data budowy | 2026-11-21 (`Ramki/etap3/wydania/README.md`) |
| Paczka N+1 do T12 (numer, SHA-256) | 0.3.2 (ten sam commit, `--wersja 0.3.2`; nieopublikowana), `030c72d86420e9461a3de93b47d7a68baa80bfbb52aa0078bf1907c42abad96c` (certutil = `.zip.sha256`: `dowody/T12/t12_sha256_zip.txt`) |
| Wiersz w `Ramki/etap3/wydania/SHA256SUMS_wydania.txt` dopisany | tak - w `main` c399482 (PR #48), czyli PO commicie paczki; w commicie paczki 571e186 wiersza 0.3.1 nie ma (potkniecie 8 w `dowody/T0/WYNIK.md`, potkniecie 5 w `dowody/T12/WYNIK.md`) |
| Pelny pytest na commicie wydania (interpreter bazowy) | 2213 passed / 9 skipped / 0 failed, kod wyjscia 0 (T1 przebieg 2: `dowody/T1/t1_pytest_bazowy.log`); srodowisko wersji z paczki: 2213 / 9 / 0, kod 0 (`dowody/T1/t1_pytest.log`) |
| Scalone paczki (PR, commit scalenia) | A11s: PR #38, 9e0190b; A11i: PR #39, 3cc1e3c; A11w: PR #43, b533653; P14: PR #42, 2d1e010; A11d: PR #40, 3078ec9; P15: PR #45, 8753439; ODB: PR #44, 571e186 (z `git log --merges main`) |

## 2. Tabela testow T0-T17

| Nr | Test | Wynik | Liczniki (kryterium -> zmierzone) | Wykonawca, data | Dowody |
|---|---|---|---|---|---|
| T0 | Czysta instalacja | **ZAL z odstepstwem O1** | start programu 2 z 2 (kody 0 i 0: `Stanowisko.cmd --atrapa --zamknij-po 5` 6,5 s; `Stanowisko.cmd --zamknij-po 20` 22,5 s; `Traceback` w logu programu: 0 wierszy); samokontrola: ok 17 / ostrzezenia 4 / bledy 0 (kod 0, `SAMOKONTROLA: ZIELONA (ok 17, ostrzezenia 4)`, 21 sprawdzen; po kroku `/testy`: ok 18 / ostrzezenia 3); SHA-256 zgodne: ZIP 1 z 1, pliki paczki wg instalatora 210 z 210 (obie instalacje), pliki programu wg samokontroli 130 z 130 (nadmiarowych 0); instalacje: pierwsza kod 10 `WSTRZYMANA` (65,5 s), po uzupelnieniu ustawien kod 0 `GOTOWA` (3,3 s); "bez internetu" (O1): `pip.log` 2 wiersze z 2, 0 wierszy `Downloading`, pakiety 73 z 73; "czyste konto" (O1): swiezy katalog na koncie `<konto-PC>`, sieci fizycznie nie odcinano | sesja testow koncowych (tor 1), 21.11.2026 02:47-02:52 | `T0/WYNIK.md`, `T0/t0_kroki.md`, `T0/t0_sha256.txt`, `T0/t0_zainstaluj_1.log`, `T0/t0_zainstaluj_2.log`, `T0/t0_samokontrola.txt`, `T0/t0_samokontrola.json`, `T0/t0_start.txt`, `T0/t0_pip_bez_sieci.txt`, `T0/kody.txt` |
| T1 | Testy programu | **ZAL** | wiersz podsumowania - przebieg 1 (srodowisko wersji z paczki): `2213 passed, 9 skipped, 1 warning in 1773.05s (0:29:33)`; przebieg 2 (interpreter bazowy): `2213 passed, 9 skipped, 1 warning in 1554.25s (0:25:54)`; w obu: passed 2213 / skipped 9 / failed 0 / errors 0 (zebranych `--collect-only`: 2222 w obu interpreterach; 2213 + 9 + 0 = 2222); kod wyjscia procesu: 0 i 0; pominiete spoza punktu odniesienia: 0 (9 z 9 znanych); kazdy przebieg 1 raz, bez powtorek; przebieg 1 pod obciazeniem (T10, T12, T5 B4, T7) | sesja testow koncowych (tor 1), 21.11.2026 02:51-03:48 | `T1/WYNIK.md`, `T1/t1_wynik.md`, `T1/t1_pytest.log`, `T1/t1_pytest_bazowy.log`, `T1/t1_collect.txt`, `T1/t1_pominiete.txt`, `T1/kody.txt` |
| T2 | Wieczor od poczatku do konca | `[W TOKU: T2]` | sterownik `t2_wieczor.py` na programie z paczki: zgodnosc obslugi _ z 10; start analizy ponizej 1 s: _ z 9 (maks. _ s; czekalo w kolejce _); mapa mediana _ s (maks. _ s; plytka 1, pula zimna: _ s; do 40 s: _ z 1 i _ z 8) - gorne ograniczenie; przerwa okna maks. _ ms, przekroczen 200 ms: _; ubytki wg prawdy _: czerwonych _ / zoltych _ / zielonych (przeoczonych) _; prace cale na czerwono (falszywe alarmy): _ z _; lista "do dofrezowania" = prawda: TAK / NIE (brakuje _, nadmiarowych _); klikniecia "Ukruszona" _ z _, "OK" _ z _, ponowien _; T2 LACZNIE: _; platforma Qt: _ | `[W TOKU: T2]` | `T2/` |
| T3 | Poranek od poczatku do konca | **ZAL z odstepstwem O5** | sterownik `t3_poranek.py` na programie z paczki (kod 0 z `--wymagaj-100`, 10,1 s, 1 proba), wiersz "WERDYKT T3": `WERDYKT T3: ZAL z odstepstwem O5 (32 z 32; ekran: tak 8, czesciowo 1, nie dotyczy 1, nie 0, nie odczytano 0)`; wiersze tabeli SE10 zgodne (liczone z ekranu) 32 z 32, wg samego API 32 z 32, "FAIL (ekran)" 0; listy kompletnych i brakow odczytane z ekranu: tak 8 / czesciowo 1 (R31) / nie 0 / nie dotyczy 1 (R17) / nie odczytano 0 (z 10 wierszy); pytanie przed "Zamknij piec": piec 1 - oczekiwane nie, bylo nie; piec 2 - oczekiwane TAK, bylo NIE; piec 3 - oczekiwane nie, bylo nie; R22: napisu ekranu z liczba prac nierozstrzygnietych brak (ta czesc wiersza tylko z API); testy uzupelniajace: SE10 sesja 33 z 33 (`33 passed, 40 deselected`, kod 0; kod programu z repo - wg planu), ekran 60 passed (kod 0) | sesja T3 / T6 / T5 (tor 3), 21.11.2026 02:52-02:53 | `T3/WYNIK.md`, `T3/t3_wynik.txt`, `T3/t3_wynik.json`, `T3/t3_sterownik.log`, `T3/t3_se10.log`, `T3/t3_ekran.log`, `T3/kody.txt` |
| T4 | Pula | `[W TOKU: T4]` | top-1 "dobrze" _ z _; zimna, plytka 1: _ s (do 40 s: _ z 1); zimna, plytki 2-10: maks. _ s (do 40 s: _ z 9); ciepla, plytki 1-10: maks. _ s (do 40 s: _ z 10); pamiec szczyt _ GB | `[W TOKU: T4]` | `T4/` |
| T5 | Ramka na atrapie w sieci lokalnej | **ZAL z odstepstwem O8** | (127.0.0.1, O8) potwierdzenia 5 z 5 (seria 100 z 100 powtorzen = 500 z 500 zdarzen; strona ramki 500 z 500), powtorek 0, luk 0; plan po restarcie maks. 0,52 s od startu ramki (0,03 / 0,03 / 0,52 s; 0,22 / 0,23 / 0,74 s od zabicia procesu ramki; 3 z 3; strona ramki 0,06 s); Spacja maks. 9 ms (10 Spacji, mediana 7 ms; strona ramki maks. 4 ms; program + okno maks. 36 ms w 5 probach; prawdziwa aplikacja 69 ms); zmiana plytki 40 z 40 przelaczen ponizej 100 ms (mediana 38 ms, maks. 48 ms); plan 1115 pol zgodnych, 0 roznych; testy `20 passed, 99 deselected` i `4 passed, 24 deselected`, kody 0 i 0, po 1 probie, pod obciazeniem (T1, T10, T12); zrodlo kodu w testach: INSTALACJA 2 z 2 (modulow z instalacji 20 i 60 / z repo 0 i 0; pliki `*.py` instalacji = repo 79 z 79) - O14 nie zachodzi; adres karty PC <adres-IP>: ramka W z 3 skanami: plan i kolory w 3 z 3 skanow (10 x `PUT /plan -> 200`, kolory = mapa 27 z 27 gniazd), posredniki: 57 polaczen (W) i 20 (P), nieudanych 0; na adresie LAN 5 potwierdzen, restart ramki i Spacja NIE ZMIERZONO (tak stanowi plan, O8); czesc B wykonana skryptem w sesji bez okien (NOWE - sposob wykonania, liczb nie zmienia) | sesja T3 / T6 / T5 (tor 3), 21.11.2026 02:57-03:05 | `T5/WYNIK.md`, `T5/t5_testy.log`, `T5/t5_testy_2.log`, `T5/t5_zrodlo_kodu_1.txt`, `T5/t5_zrodlo_kodu_2.txt`, `T5/t5_wieczor.log`, `T5/t5_siec_lokalna.md`, `T5/kody.txt` |
| T6 | Excel na sztucznym arkuszu | **ZAL** (O9 - informacja) | zapytania 200 z 200 (arkusz 30000 wierszy; wlasciwa klasa 200 z 200); zle wiersze 0 (zapisow 148: z wyboru programu 110, wiersz wskazany przez test 38; w zlym wierszu 0); log regula 6: zgodny - naglowek w 6 z 6 plikow logu, 476 wierszy danych sprawdzonych (pole `kuweta` puste w 4 z 476 - wpisy `pominieto` zlecen bez numeru kuwety; `wiersz` i `numer_zlecenia_b` puste w kazdym wpisie `pominieto`); tryb "pytaj": 200 z 200 obsluzonych; tryb "cien": 200 z 200 wpisow logu, zapisow koloru 0; testy `129 passed` i `2 passed, 26 deselected`, kody 0, 0, 0, po 1 probie; zrodlo kodu: INSTALACJA 2 z 2 (z repo 0 modulow; pliki 79 z 79) - O14 nie zachodzi | sesja T3 / T6 / T5, 21.11.2026 02:54-02:55 | `T6/WYNIK.md`, `T6/t6_arkusz.txt`, `T6/t6_excel.log`, `T6/t6_aplikacja.log`, `T6/t6_zrodlo_kodu.txt`, `T6/t6_zrodlo_kodu_2.txt`, `T6/t6_log_regula6.txt`, `T6/kody.txt` |
| T7 | Odpornosc | **ZAL z odstepstwem O12** (z zastrzezeniem do przypadku 4 - do decyzji koordynatora, sekcja 4a poz. 21) | przypadki 6 z 6 (silnik 1, zamkniecie 1, brak "Cyrkon" 1, brak sieci 1, brak ramki 1, baza zajeta 1), w tym "ZAL z odstepstwem O12 (komunikat spoza zal. F)": 6; FAIL 0; zrodlo kodu w testach: INSTALACJA (15 z 15 przebiegow, 0 modulow z repo, pliki 79 z 79) - O14 nie zachodzi; komunikaty zgodne z zal. F: 0 z 6 (zgodne z tabela technika `instrukcje\co_robic_gdy_nie_dziala.md`: 6 z 6); czesc A: 15 polecen z 15 z kodem 0, 49 passed / 0 failed / 0 error / 0 skipped; proby na programie z paczki: B1 (samokontrola kod 1 z wierszem `BLAD folder_cyrkon`; komunikat `pula_brak_folderu` w logu 0 wierszy), B1b (1 skan z 1 przeanalizowany po przywroceniu folderu), B2 (4 skany z 4 w bazie po zakonczeniu i ponownym starcie programu), B3 (3 skany z 3 ze statusem w bazie, w tym 1 `blad`; `blad_analizy` 1) - kody programu 0; przypadek 4: w testach brak asercji komunikatu tekstowego programu (wariant surowy = FAIL przypadku, T7 = FAIL 1 z 6) | sesja T12 / T7 / T13 (tor 4), 21.11.2026 03:03-03:35 | `T7/WYNIK.md`, `T7/t7_wynik.md`, `T7/t7_komunikaty.md`, `T7/t7_proby_reczne.md`, `T7/t7_<nr><a-d>.log` i `T7/t7_<nr><a-d>_zrodlo_kodu.txt` (15 par), `T7/t7_b2_pid.txt`, `T7/t7_b2_symulator.json`, `T7/kody.txt` |
| T8 | Metryki | `[W TOKU: T8]` | metryki zgodne z liczeniem recznym: _ z _ (wieczor _ z _, rano _ z _) | `[W TOKU: T8]` | `T8/` |
| T9 | Dane osobowe | `[W TOKU: T9]` | trafienia calych nazw: repo _, logi _, wyniki _, ruch do ramki _; czlony wyjasnione _ z _; nazwy w `dane/`: _ (skan katalogu `dowody/` przed `git add`, bez `--dozwolone`, wykonany przy zbieraniu dowodow: 0 trafien calych nazw, kod 0 - `dowody/README.md`; to nie jest wynik T9) | `[W TOKU: T9]` | `T9/` |
| T10 | Regresja silnika | **ZAL** | wyrownanie 40 z 40 (najwiekszy blad 0,0143 mm, prog 0,05 mm); top-1 "dobrze" 276 z 276 (mianownik z plikow prawdy); falszywe czerwone na pracach calych 0 z 127 (wpisow wg definicji narzedzia = 0 z 126 prac liczonych raz); kod 0, 1 przebieg bez powtorek, 14 min 23 s; liczby rowne R59 pkt 6.2 (40 z 40, 276 z 276, 0 z 127) | sesja "T10" (tor 2), 21.11.2026 02:52-03:10 | `T10/WYNIK.md`, `T10/t10_wynik.md`, `T10/t10_licz.json`, `T10/t10.log`, `T10/t10_t9.txt`, `T10/kody.txt` (`t10_metryki.json`, 1586 KB, poza repo - `T10/POMINIETE.txt`) |
| T11 | Stare plytki | `[W TOKU: T11]` | uklad rozpoznany _ z 40 (P2: _ z 24, P3a: _ z 16); skany FAIL (ostrzezenie bez nazwy wlasciwego ukladu): _; zielone przy zlym ukladzie _ (wiecej niz 0 = FAIL testu; gdy 0 z 0: pozycja 7 z T2: zielonych _); uklad zapisany w `skany` _ z _ | `[W TOKU: T11]` | `T11/` |
| T12 | Aktualizacja | **ZAL z odstepstwem O2** | N -> N+1 (0.3.1 -> 0.3.2): polecen 1, kod 0 (60,4 s; `INSTALACJA: GOTOWA - wersja biezaca 0.3.2 (poprzednia: 0.3.1)`); powrot: polecen 1, kod 0 (`Wroc_do_poprzedniej.cmd /bez-pauzy` z odpowiedzia `T`, 2,6 s; odpowiedz `N` i brak odpowiedzi: kod 11, wersja bez zmian; `/tak /bez-pauzy` z planu: kod 0, 3,3 s); samokontrola ZIELONA (ok 18, ostrzezenia 3) kod 0 - 3 z 3, start programu kod 0 - 3 z 3; ustawienia: sumy rowne 4 z 4 (plan wymaga 3 z 3); baza (czesc A, schemat bez zmian): kopia 1 plik, 86016 B = baza, skrot bez naglowka rowny, `user_version` 1 = 1, zdarzen 2 = 2; migracja probna (czesc B, paczka `0.3.9-migracja`): schemat 1 -> 2, kopia = baza sprzed (rozmiar 86016 B rowny, skrot bez naglowka rowny, `user_version` 1 -> 2 -> 1, zdarzen 4 -> 7 -> 4 - przepadly 3 wpisy wersji probnej), powrot po migracji: polecen 2 (kody 8 / 0); kody czesci B zgodne 11 z 11; SHA-256 bazy po przywroceniu = SHA-256 kopii | sesja T12 / T7 / T13 (tor 4), 21.11.2026 02:49-03:03 | `T12/WYNIK.md`, `T12/t12_kroki.md`, `T12/t12_ustawienia_sumy.txt`, `T12/t12_wersje_przed_po.txt`, `T12/t12_zainstaluj_N1.log`, `T12/t12_wroc.log`, `T12/t12_wroc_tak.log`, `T12/t12_migracja_B.md`, `T12/t12_B_stany.txt`, `T12/kody.txt` |
| T13 | Higiena repo | pierwszy przebieg (commit paczki 571e186): **ZAL z odstepstwem O11 i O10**; drugi przebieg (po dodaniu dowodow): `[W TOKU: T13 drugi przebieg]` | pierwszy przebieg: naruszen 0 (poza listami 0 z 662 zmienionych sciezek, nie ASCII poza lista O11 0, konce linii 0, STL / dane 0, duze pliki 0); odstepstwo O11 (napisy ekranu nie-ASCII): 7 plikow z 7, wierszy 807 (6452 bajty); grupa E3: 245 nowych / 24 zmienione / 0 usunietych, 238 z 245 nowych bez bajtu nie-ASCII; kontrola na poziomie katalogow paczek (O10: 6 przedrostkow E3); uwagi w grupach R58 / R59 poza wynikiem: 126; kontrola reczna 3 z 3 zgodne; kod 0, 1,1 s; drugi przebieg: `[W TOKU: T13 drugi przebieg]` | sesja T12 / T7 / T13, 21.11.2026 03:07-03:16; drugi przebieg: `[W TOKU: T13 drugi przebieg]` | `T13/WYNIK.md`, `T13/t13_wynik.txt`, `T13/t13_wynik.json`, `T13/t13_diff_stat.txt`, `T13/t13_kontrola_reczna.txt`, `T13/t13_kontrola_niezalezna.txt` |
| T14 | Proba "technik obsluguje bez instrukcji" (czlowiek) | **ZADANIE WLASCICIELA** (test czlowieka: NIE ZMIERZONO) | zadania _ z 11; interwencje _; zawahania ponad 10 s: _ (poprawione _, zostawione _); zestaw gotowy: `Ramki/etap3/t14/`; kontrola zestawu na instalacji z paczki 0.3.1 (to NIE jest test T14): `SPRAWDZENIE T14 BEZ EKRANU: zgodne 22 z 22 krokow`, kod 0, 8,1 s | wlasciciel, _ (kontrola zestawu: wykonawca T0 / T1, 21.11.2026 02:52) | `T14/README.md` (opis proby); kontrola zestawu: `dowody/T14/WYNIK.md`, `dowody/T14/t14_sprawdz_paczka.txt` |
| T15 | Ramki na sprzecie | ODLOZONE (wg `ODLOZONE.md`: brak sprzetu) | - | - | `ODLOZONE.md` |
| T16 | Prawdziwy skaner | ODLOZONE (wg `ODLOZONE.md`: brak sprzetu i danych) | - | - | `ODLOZONE.md` |
| T17 | Excel i MillBox na prawdziwych danych | ODLOZONE (wg `ODLOZONE.md`: brak danych) | - | - | `ODLOZONE.md` |

Podsumowanie T0-T13 (14 testow, cztery osobne liczniki, suma = 14): `[W TOKU: liczniki]` - **ZAL _ ; ZAL z odstepstwem _
(numery: O_ ...) ; FAIL _ ; NIE ZMIERZONO / niewykonane _**. T14: ZADANIE WLASCICIELA (test czlowieka niewykonany; zestaw
sprawdzony 22 z 22). T15-T17: ODLOZONE 3 z 3 (powod i warunek wznowienia w `ODLOZONE.md`).
Stan CZESCIOWY na 21.11 (to nie sa liczniki koncowe): wykonanych 9 z 14 testow T0-T13 - ZAL 3 (T1, T6, T10); ZAL z
odstepstwem 6 (T0: O1; T3: O5; T5: O8; T7: O12; T12: O2; T13 pierwszy przebieg: O10 i O11); FAIL 0; w toku 5 (T2, T4, T8,
T9, T11) oraz drugi przebieg T13. Zastrzezenie: T7 ma pozycje do decyzji koordynatora (przypadek 4, sekcja 4a poz. 21),
ktora w wariancie surowym zmienia wynik T7 na FAIL.
Wg planu testow (stan 21.11, po rundzie 2 recenzji) bez odstepstwa moga byc zaliczone: T1, T8, T9, T10 oraz T6
(sekcja 7: "na sztucznym arkuszu" - arkusz w pamieci jest takim arkuszem) i T11 (40 z 40 rozpoznanych spelnia "albo"
pierwsza galezia) - razem 6 testow; warunkowo T4 i T7 - gdy nie zajdzie przypadek z O7 (pierwsza plytka po zimnym
starcie ponad 40 s) ani z O12 (komunikat spoza zal. F). Najwyzej "ZAL z odstepstwem" ma 6 testow, ktorych kryterium nie
da sie na tym PC wykonac doslownie: T0 (O1), T12 (O2), T2 (O3, O4, O13), T3 (O5), T5 (O8), T13 (O10, O11). O14 dziala
tylko wtedy, gdy przebieg T5, T6 albo T7 czesc A ma werdykt zrodla kodu "REPO" (albo kod 3). O6 i O9 zostaja w sekcji 4
jako informacja i pozycje do decyzji wlasciciela (4a), ale nie obnizaja wyniku T11 i T6.

## 3. Definicja "koniec etapu 3 = gotowe do trybu cienia" (plan, sekcja 7)

| Warunek | Stan | Dowod |
|---|---|---|
| T0-T14 zaliczone (regula do decyzji wlasciciela, sekcja 4a poz. 1: czy "ZAL z odstepstwem" liczy sie jako zaliczenie konca etapu; koordynator wpisuje tu osobno: ZAL _ / ZAL z odstepstwem _ / FAIL _) | `[W TOKU: liczniki]` (stan czesciowy 21.11: ZAL 3 / ZAL z odstepstwem 6 / FAIL 0 / w toku 5; T14 - zadanie wlasciciela, niewykonane) | tabela 2 |
| T15-T17 zaliczone albo jawnie odlozone z powodem i warunkiem wznowienia | jawnie odlozone 3 z 3 (kazdy: powod, warunek wznowienia, pierwszy krok) - do potwierdzenia przez wlasciciela | `ODLOZONE.md` |
| Instrukcje jednostronicowe gotowe (wieczor, poranek) | pliki sa w `main` 5f962dd (2 z 2); ocena tresci = proba T14 (zadanie wlasciciela) | `Ramki/stanowisko/instrukcje/wieczor.html`, `poranek.html` (A11d) |
| Tabela "co robic, gdy nie dziala" gotowa | plik jest w `main` 5f962dd; T7: komunikaty 6 przypadkow zgodne z ta tabela 6 z 6 (z PW zal. F: 0 z 6 - O12) | `Ramki/stanowisko/instrukcje/co_robic_gdy_nie_dziala.html` (A11d); `dowody/T7/t7_komunikaty.md` |
| Kroki 1-5 z PW "Uruchomienie" da sie wykonac bez programisty przy klawiaturze | do oceny wlasciciela na podstawie `POKAZ_G3.md`: instalacja wg instrukcji wykonana w T0 (9 krokow, kody 10 i 0; ZAL z odstepstwem O1), aktualizacja i powrot w T12 (po 1 poleceniu, kody 0 i 0; ZAL z odstepstwem O2); na laptopie stanowiska niewykonane (`ODLOZONE.md`, otwarte 4-6) | `instrukcje/instalacja_i_aktualizacja.md`, `dowody/T0/`, `dowody/T12/`, `POKAZ_G3.md` |

## 4. Odstepstwa (przyjete interpretacje kryteriow)

Lista wyjsciowa z `PLAN_TESTOW.md` - koordynator potwierdza albo zmienia kazda pozycje i dopisuje te, ktore wyjda w testach.

| Nr | Test | Odstepstwo | Potwierdzone (tak / nie / zmienione) |
|---|---|---|---|
| O1 | T0 | "czyste konto" = swiezy katalog na koncie `<konto-PC>`; "bez internetu" = instalator zawsze instaluje pakiety tylko z kol paczki (pip `--no-index`, dowod: 2 wiersze w `pip.log`), sieci fizycznie nie odcinano (opcja `/bez-sieci` wylacza tylko probe polaczenia samokontroli z ramkami - poprawione po probie generalnej 21.11) | |
| O2 | T12 | "baza zmigrowana z kopia" sprawdzona na paczce probnej z dodatkowa pozycja `MIGRACJE` (schemat wydan N i N+1 jest ten sam); powrot po migracji wymaga 2 polecen (kod 8, potem `/przywroc-kopie`) - "jedno polecenie" ocenia czesc A; kopia bazy sprzed migracji porownywana z baza co do rozmiaru i SHA-256 bajtow od 100. (naglowek SQLite: w kopii inne sa 3 liczniki - zmian pliku, zmian schematu i `version-valid-for`, czyli 3 bajty naglowka; tresc od 100. bajtu identyczna; sumy calych plikow sa rozne) oraz `user_version` i liczby zdarzen osobnym zapytaniem; po powrocie z przywroceniem suma calego pliku bazy = suma pliku kopii | |
| O3 | T2 | (zmienione w etapie 2, decyzja nr 12) program z paczki biegnie w procesie sterownika `t2_wieczor.py` (funkcja `aplikacja.main`, interpreter i katalog programu wersji przez `Polecenie.cmd`, opcja `--zamknij-po` jako bezpiecznik), a nie przez plik `Stanowisko.cmd`; dostaje kopie `ustawienia.toml` z `[sciezki]` w katalogu roboczym; start analizy mierzony doslownie (`analiza.od` stanu programu); czas do mapy = gorne ograniczenie (odczyt stanu co 20 ms); start programu przed pokazaniem okna poza pomiarem przerw petli | |
| O4 | T2 | (zmienione w etapie 2) okno `offscreen` (sesja bez ekranu); zegar sterownika w watku okna (odczyt stanu, klikniecia) wlicza sie do przerw petli (takze jednorazowy odczyt obrazu mapy kazdej plytki); przerwy petli mierzone bez kosztu rysowania na prawdziwym ekranie | |
| O5 | T3 | (zmienione w etapie 2, decyzja nr 13) SE10 przez okno prawdziwego kontrolera (`t3_poranek.py`, klikniecia po nazwach obiektow), ale wyniki skanow sztuczne (SE10 nie ma plikow STL - wchodza funkcja sesji wolana po analizie), zegar staly ustawiany przez sterownik, zlecenia SE10 wpisane do bazy funkcja testu, okno `offscreen`, ramki i Excel wylaczone; 2 z 10 wierszy z listami ekran pokazuje tylko czesciowo albo wcale (R31, R17) | |
| O6 | T11 | (INFORMACJA - nie obniza wyniku: przy 40 z 40 rozpoznanych T11 = ZAL, ustalenie koordynatora 21.11 po rundzie 2 recenzji) (decyzja nr 15) kryterium ma "albo": plytka z ukladem rozpoznanym = zaliczona; ostrzezenie bez nazwy wlasciwego ukladu = FAIL tego skanu (licznik); zielona przy zlym ukladzie = FAIL calego testu. Druga galaz kryterium ("ostrzezenie z nazwa wlasciwego ukladu") jest w programie NIESPELNIALNA (komunikat `niezgodny_uklad` nie zawiera nazwy ukladu - brak B5): kryterium liczone tylko pierwsza galezia, na 40 skanach `*_r54` | |
| O7 | T4 | (decyzja nr 17) mierzone i podane oba: pierwsza plytka po starcie (pula zimna) i kolejne (pula ciepla), osobne liczniki "do 40 s: n z m"; kryterium liczone dla wszystkich plytek; przekroczenie tylko przez pierwsza plytke po zimnym starcie = "ZAL z odstepstwem" z liczba sekund i pozycja do decyzji wlasciciela; przekroczenie przy puli cieplej = FAIL; wszystkie plytki do 40 s = ZAL bez odstepstwa (O7 dziala tylko w przypadku pierwszej plytki); pamiec: w odbiorze mierzony szczyt JEDNEGO procesu (`szczyt_mb`); szczyt procesu okna niemierzony - do sumy liczba z raportu E3-A5 (ok. 1,0 GB) | |
| O8 | T5 | wszystkie liczby kryterium T5 (5 z 5, 0 powtorek, plan do 5 s, Spacja ponizej 1 s) pochodza z testow pytest na 127.0.0.1 - atrapa ramki i program na TYM SAMYM komputerze (adres wpisany w testach); kod programu w tych testach z instalacji (`pytest_instalacja.py`, patrz O14). Na adresie karty sieciowej PC i programie z paczki tylko przebieg ramki W z 3 skanami - bez pomiaru 5 potwierdzen bez sieci, restartu ramki i Spacji; ramka P tylko w testach; takze ta czesc to jeden komputer (ruch przez stos sieciowy, nie przez kabel ani Wi-Fi). Prawdziwa siec = T15 (odlozony) | |
| O9 | T6 | (INFORMACJA - nie obniza wyniku: kryterium sekcji 7 mowi "na sztucznym arkuszu", ustalenie koordynatora 21.11 po rundzie 2 recenzji) arkusz w pamieci (atrapa), bez programu Excel; Excel przez COM = T17 | |
| O10 | T13 | "tylko pliki z list paczek" sprawdzane na poziomie KATALOGOW paczek, nie list pojedynczych plikow: jeden przedrostek `Ramki/stanowisko/` obejmuje caly program, wiec kontrola nie rozroznia, ktora paczka zmienila ktory plik, i NIE wyroznia plikow nietykalnych zmienionych od poczatku etapu (wg recenzji: `match.py` 9 commitow, `inspect.py` 7, `synth.py` 1 - zmiany z paczek, ktore mialy je w zakresie; do potwierdzenia przez koordynatora z historii PR); prace R58 / R59 (wg recenzji: 2 STL, 7 plikow danych, 11 duzych) liczone osobno i poza wynikiem | |
| O11 | T13 | (decyzja nr 16) 7 nowych plikow nie-ASCII z napisami ekranu (polskie znaki widziane przez technika - styl programu przyjety przez wlasciciela w paczkach A3 / A6): `stanowisko/dzien_skanera.py` (109 wierszy nie-ASCII), `stanowisko/dzien_skanera_kroki.toml` (134), `stanowisko/dzien_skanera_rdzen.py` (102), `stanowisko/statusy.py` (240), `stanowisko/ui/napisy.py` (66), `stanowisko/ui/napisy_rano.py` (111), `testy/test_dzien_skanera.py` (45) - liczby z proby na kopii integracyjnej a2236c1 (wpisac stan z commita wydania); lista w `narzedzia/t13_wyjatki_ascii.txt`; kazdy INNY nowy plik nie-ASCII = naruszenie (proba a2236c1: 1 taki plik - `stanowisko/ui/kandydaci.py`, 2 bajty - do rozstrzygniecia przed odbiorem) | |
| O12 | T7 | (decyzja nr 14; warunkowe - dziala tylko, gdy wystapi komunikat spoza zal. F) przypadek z komunikatem i dalsza praca, ale z tekstem komunikatu spoza PW zal. F = "ZAL z odstepstwem O12 (komunikat spoza zal. F: <tekst>)" + pozycja w zadaniach wlasciciela; brak komunikatu albo brak dalszej pracy albo stan nieodtworzony = FAIL | |
| O13 | T2 | (decyzja nr 18, po recenzji PR #44) lista "do dofrezowania" powstaje z klikniec sterownika, ktory - jak technik - klika "Ukruszona" tylko na pracach z ubytkiem wg pliku prawdy pokazanych przez program na czerwono albo zolto (kolor czytany z obrazu mapy przed kliknieciem); praca z ubytkiem pokazana na zielono nie jest klikana i daje FAIL listy. T2 mierzy wiec, czy wieczor z programem daje prawdziwa liste na 6 plytkach przyjetych scenariusza (skany sztuczne; 26 prac z ubytkiem wg prawdy, kazda z ubytkiem oznaczonym jako wykrywalny i widoczny); wykrywalnosc ubytkow jako taka mierza T10 / T16. Prac zoltych calych sterownik nie klika. Sterownik zaklada, ze technik ogladajacy prace zolta zawsze zauwazy ubytek (w probach wiekszosc ubytkow byla zolta, nie czerwona: 7 z 12 i 2 z 3) - liczby czerwonych / zoltych / zielonych sa w wierszu T2 | |
| O14 | T5, T6, T7 czesc A (T1: informacja, nie odstepstwo) | (warunkowe - obniza wynik tylko przy werdykcie zrodla kodu "REPO" albo kodzie 3) testy pytest pochodza z `<REPO>` (ten sam commit co paczka). T5, T6, T7 czesc A: kod programu ladowany z INSTALACJI przez `narzedzia/pytest_instalacja.py` (wynik podaje liczbe modulow z instalacji i z repo oraz "pliki *.py instalacji = repo: a z b"); procesy potomne testow (ramka w osobnym procesie, proces silnika) importuja kod sami i moga brac go z repo - tego licznik nie obejmuje. T1 (caly pytest): kod z `<REPO>`, z paczki tylko interpreter i pakiety; zgodnosc plikow instalacji z paczka potwierdza licznik sum w T0 | |

## 4a. Odstepstwa i sprawy do decyzji wlasciciela (kazde "ZAL z odstepstwem" musi tu miec wiersz)

| Nr | Sprawa | Odstepstwo / zrodlo | Decyzja wlasciciela |
|---|---|---|---|
| 1 | Czy "ZAL z odstepstwem" liczy sie jako zaliczenie konca etapu 3 (wg planu testow 6 z 14 testow T0-T13 ma odstepstwo zawsze: T0, T2, T3, T5, T12, T13; 2 warunkowo: T4, T7; 6 moze byc zaliczonych doslownie: T1, T6, T8, T9, T10, T11) | sekcja 2, 3; uwaga 26 recenzji rundy 1, uwaga 36 rundy 2 | |
| 2 | T2: technik-sterownik klika tylko prace czerwone / zolte; wykrywalnosc ubytkow mierza T10 / T16 | O13 | |
| 3 | T2 / T4: pierwsza plytka po zimnym starcie ponad 40 s (zmierzone w probach: 41,96-47,5 s; raporty A5: 63-68 s); przy odstepie 60 s druga plytka moze przez to czekac w kolejce i dac FAIL "start analizy ponizej 1 s" | O7 (tylko gdy wystapi; wszystkie plytki do 40 s = T4 ZAL bez odstepstwa) | |
| 4 | T2: przerwy petli okna mierzone w oknie `offscreen` (bez kosztu rysowania na ekranie) | O4 | |
| 5 | T3: po restarcie ekran pokazuje tylko ostatni zamkniety piec (R31), listy "do dofrezowania" ekran poranny nie pokazuje (R17) | O5 | |
| 6 | T3: okno nie pyta przed "Zamknij piec", gdy praca nieznana ma decyzje "bez projektu" (sesja liczy ja jako nierozstrzygnieta) - zamierzone czy poprawka P14 | obserwacja z prob T3 (3 z 3 przebiegow); uwaga 20 recenzji | |
| 7 | T5: liczby kryterium z testow na 127.0.0.1, atrapa i program na jednym komputerze | O8 | |
| 8 | T6: arkusz w pamieci; Excel przez COM jest na PC, a zostal przeniesiony do T17 | O9 - informacja; wyniku T6 nie obniza (kryterium: "na sztucznym arkuszu") | |
| 9 | T7: komunikaty spoza PW zal. F - uzupelnic zalacznik albo zmienic napisy | O12 (tylko gdy wystapi taki komunikat) | |
| 10 | T11: druga galaz kryterium (ostrzezenie z nazwa wlasciwego ukladu) niespelnialna w programie | O6, brak B5 - informacja; przy 40 z 40 rozpoznanych wyniku T11 nie obniza | |
| 11 | T12: powrot po migracji bazy w 2 poleceniach (kod 8 + `/przywroc-kopie`); kopia bazy porownywana z baza bez 100-bajtowego naglowka SQLite | O2 | |
| 12 | T13: kontrola na poziomie katalogow; pliki nietykalne niewyroznione; 7 plikow napisow nie-ASCII | O10, O11 | |
| 13 | T0: "czyste konto" = swiezy katalog, nie nowe konto Windows; sieci fizycznie nie odcinano | O1 | |
| 14 | T5-T7: testy z repo, kod programu z instalacji (odstepstwo tylko przy werdykcie "REPO"); T1: testy i kod programu z repo, z paczki interpreter i pakiety - informacja, nie odstepstwo (kryterium T1 to "pytest caly") | O14 | |
| 15 | Skan zestawu P3a bez drgniecia w prawdzie dostal od programu status "do_powtorzenia" (falszywe "skan ponownie"; proba doboru scenariusza T2, 20.11) - zestawic z wynikiem T10 (R59 pkt 6.2: 2 falszywe "skan ponownie") | uwaga 15 recenzji | |

### 4a.1 Odstepstwa O1-O14 - co FAKTYCZNIE zaszlo w testach wykonanych (stan 21.11, liczby z `dowody/T<nr>/WYNIK.md`)

| Nr | Test | Zaszlo? | Z jaka liczba (zrodlo) |
|---|---|---|---|
| O1 | T0 | zaszlo - T0 = ZAL z odstepstwem O1 | swiezy katalog `<PC-katalog>\t0\odbior\` na koncie `<konto-PC>` (nie nowe konto Windows); sieci fizycznie nie odcinano; `pip.log`: 2 wiersze z 2 (`Ignoring indexes`, `Looking in links`), 0 wierszy `Downloading`; pakiety 73 z 73 z kol paczki (`dowody/T0/WYNIK.md`, `t0_pip_bez_sieci.txt`) |
| O2 | T12 | zaszlo - T12 = ZAL z odstepstwem O2 | migracja sprawdzona na paczce probnej `0.3.9-migracja` (schemat 1 -> 2), kody 11 z 11; kopia sprzed migracji: 1 plik, 86016 B i skrot bez naglowka = baza sprzed (sumy calych plikow rozne - naglowek SQLite); powrot po migracji: 2 polecenia (kod 8, potem `/przywroc-kopie` kod 0), przepadly 3 wpisy dopisane po aktualizacji (zdarzenia 4 -> 7 -> 4); "jedno polecenie" ocenione w czesci A: 1 i 1, kody 0 i 0 (`dowody/T12/WYNIK.md`, `t12_migracja_B.md`) |
| O3 | T2 | `[W TOKU: T2]` | |
| O4 | T2 | `[W TOKU: T2]` | |
| O5 | T3 | zaszlo - T3 = ZAL z odstepstwem O5 | 32 z 32 wierszy z ekranu (wg API 32 z 32); wyniki skanow sztuczne, zegar staly, okno `offscreen`, ramki i Excel wylaczone; 2 z 10 wierszy z listami: R31 "czesciowo" (po restarcie ekran pokazuje tylko ostatni zamkniety piec 3), R17 "nie dotyczy" (`dowody/T3/WYNIK.md`) |
| O6 | T11 | `[W TOKU: T11]` (informacja - nie obniza wyniku) | |
| O7 | T4 (T2) | `[W TOKU: T4]` | informacja spoza T4 (nie jest wynikiem T4 ani T2): w T5 krok B4 (sterownik T2, 3 skany, pod obciazeniem T1 / T10 / T12) mapa pierwszej plytki przy puli zimnej po 54,12 s, kolejne 26,26 s i 25,31 s (`dowody/T5/WYNIK.md`) |
| O8 | T5 | zaszlo - T5 = ZAL z odstepstwem O8 | wszystkie liczby kryterium z testow na 127.0.0.1 (500 z 500 potwierdzen, 0 powtorek; plan maks. 0,52 s; Spacja maks. 9 ms); na adresie karty <adres-IP> tylko ramka W z 3 skanami (3 z 3; posredniki 57 i 20 polaczen); na adresie LAN 5 potwierdzen, restart ramki, Spacja i ramka P z planem: NIE ZMIERZONO; nadal jeden komputer (`dowody/T5/WYNIK.md`, `t5_siec_lokalna.md`) |
| O9 | T6 | zaszlo jako INFORMACJA - wyniku nie obniza (T6 = ZAL) | arkusz w pamieci 30000 wierszy, bez programu Excel; 200 z 200; Excel przez COM = T17 (`dowody/T6/WYNIK.md`) |
| O10 | T13 | zaszlo - T13 pierwszy przebieg = ZAL z odstepstwem O10 i O11 | kontrola na poziomie katalogow (6 przedrostkow E3): 0 sciezek poza listami z 662; pliki nietykalne niewyroznione; uwagi w grupach R58 / R59 poza wynikiem: 126 (w tym 2 STL poza `modele_plytek`, 7 plikow danych, 11 duzych) (`dowody/T13/WYNIK.md`) |
| O11 | T13 | zaszlo - jw. | 7 plikow z 7 na liscie, razem 807 wierszy / 6452 bajty nie-ASCII (109 + 134 + 102 + 240 + 66 + 111 + 45 - liczby wierszy jak w probie a2236c1); innych nowych plikow nie-ASCII: 0 (`ui/kandydaci.py` z proby a2236c1 nie jest juz zglaszany) (`dowody/T13/WYNIK.md`, `t13_wynik.txt`) |
| O12 | T7 | zaszlo - T7 = ZAL z odstepstwem O12 | 6 z 6 przypadkow z komunikatem spoza PW zal. F (teksty w zal. F: 0 z 6; zal. F to 12 objawow bez tekstow komunikatow); teksty: poz. 9 w 4a.2 i `dowody/T7/t7_komunikaty.md` |
| O13 | T2 | `[W TOKU: T2]` | informacja spoza T2: w T5 krok B4 (proba skrocona, 3 skany) 1 praca z ubytkiem wg prawdy pokazana na zielono - poz. 19 w 4a.3 |
| O14 | T5, T6, T7 czesc A | **nie zaszlo** | werdykt zrodla kodu INSTALACJA: T5 2 z 2, T6 2 z 2, T7 15 z 15 przebiegow; 0 modulow programu z repo; pliki `*.py` instalacji = repo 79 z 79; kody 0 (`dowody/T5/t5_zrodlo_kodu_*.txt`, `dowody/T6/t6_zrodlo_kodu*.txt`, `dowody/T7/t7_*_zrodlo_kodu.txt`). T1 i testy uzupelniajace T3: kod programu z repo - tak stanowi plan (informacja) |

### 4a.2 Pozycje 1-15 tabeli 4a - stan po testach wykonanych (21.11)

| Nr | Test | Stan / liczba z testu (zrodlo: `dowody/T<nr>/WYNIK.md`) | Kto decyduje |
|---|---|---|---|
| 1 | T0-T13 | stan czesciowy: "ZAL z odstepstwem" ma 6 z 9 testow wykonanych (T0, T3, T5, T7, T12, T13), "ZAL" 3 (T1, T6, T10), FAIL 0; `[W TOKU: liczniki]`. Pytanie bez zmian: czy "ZAL z odstepstwem" jako osobna wartosc zalicza koniec etapu 3 | wlasciciel |
| 2 | T2 | `[W TOKU: T2]` | wlasciciel |
| 3 | T2 / T4 | `[W TOKU: T4]`, `[W TOKU: T2]`; informacja z T5 B4: pierwsza plytka (pula zimna) 54,12 s pod obciazeniem; z T10: pierwszy skan 50,88 s (czasy T10 nie sa miara czasu plytki) | wlasciciel |
| 4 | T2 | `[W TOKU: T2]` | wlasciciel |
| 5 | T3 | potwierdzone w odbiorze: R31 "czesciowo", R17 "nie dotyczy" (2 z 10 wierszy z listami) | wlasciciel |
| 6 | T3 | potwierdzone w odbiorze (1 przebieg): okno NIE zadalo pytania przed "Zamknij piec" 2 - oczekiwane wg zlecenia TAK, bylo NIE (sesja: nieznane 1; prace bez decyzji wg stanu okna 0; praca ma decyzje "bez projektu"); piece 1 i 3: oczekiwane nie, bylo nie. Zamierzone czy poprawka | wlasciciel |
| 7 | T5 | potwierdzone: wszystkie liczby kryterium z 127.0.0.1 (4a.1, O8) | wlasciciel |
| 8 | T6 | informacja: T6 = ZAL na arkuszu w pamieci (200 z 200) | wlasciciel (informacja) |
| 9 | T7 | WYSTAPILO: 6 komunikatow spoza PW zal. F - uzupelnic zalacznik albo zmienic napisy. Teksty doslowne (tytul / tresc, przepisane bez znakow diakrytycznych): (1) "Analiza skanu nie powiodla sie" / "Program nie przeanalizowal tego skanu (analiza zostala przerwana). Zeskanuj plytke ponownie."; (2) "Program wznowil prace" / "Po ponownym uruchomieniu program dokancza zalegle skany: {ile}."; (3) "Brak folderu projektow" / "Program nie widzi folderu projektow - skany czekaja ({czeka}). Sprawdz, czy dysk z folderem projektow jest podlaczony, i kliknij 'Odswiez pule'. Jesli folder jest inny - zglos to."; (4) brak sieci: ikona stanu "brak lacznosci" na ramce, teksty programu "Ramka wieczorna nie odpowiada" / "Program dziala bez ramki - wynik plytki pokazuje ekran. Sprawdz zasilanie ramki i siec stanowiska; ramka dolaczy sama."; (5) "Ramka poranna nie jest podlaczona" / "Program dziala bez ramki - rozkladaj prace wedlug ekranu: kuweta po kuwecie (Enter = rozlozona, Backspace = cofnij, cyfry i Enter = wybor kuwety)." oraz "Excel nie jest podlaczony"; (6) "Baza jest zajeta" / "Inny program trzyma baze stanowiska - niczego nie zapisano. Sprobuj ponownie za chwile.", "Decyzja NIE zostala zapisana" / "{co} - decyzja NIE jest zapisana: baza stanowiska byla zajeta przez inny program. Kliknij 'Ponow teraz'; ...", "Polecenie NIE zostalo wykonane - baza zajeta" (`dowody/T7/t7_komunikaty.md`) | wlasciciel |
| 10 | T11 | `[W TOKU: T11]` | wlasciciel (informacja) |
| 11 | T12 | WYSTAPILO: powrot po migracji schematu = 2 polecenia (`Wroc_do_poprzedniej.cmd` konczy kodem 8, potem `/przywroc-kopie` kod 0) i utrata wpisow dopisanych po aktualizacji - w probie 3 (zdarzenia 4 -> 7 -> 4); program wypisuje liczbe traconych wpisow PRZED zgoda. Zachowanie zamierzone - czy do przyjecia | wlasciciel |
| 12 | T13 | potwierdzone: O10 i O11 (4a.1); uwagi R58 / R59: 126, poza wynikiem | wlasciciel |
| 13 | T0 | potwierdzone: O1 (4a.1); pelne T0 na laptopie stanowiska = `ODLOZONE.md` (D4) | wlasciciel |
| 14 | T5-T7, T1 | O14 nie zaszlo (INSTALACJA 2 z 2, 2 z 2, 15 z 15) | informacja |
| 15 | T10 (T2) | T10: falszywe "skan ponownie" = 2 prace (obie bokiem, zestaw P3a, obie z ubytkami w prawdzie; sha16 066fcc6858e01759 i 6570c1796f152c01) - tyle samo co w R59 pkt 6.2; drgniecie wykryte 36 z 39; zestawienie z T2: `[W TOKU: T2]` | wlasciciel |

### 4a.3 Pozycje "do decyzji" zebrane ze wszystkich `WYNIK.md` testow wykonanych (ciag dalszy numeracji 4a; bez powtorzen)

| Nr | Test | Sprawa (liczba, zrodlo) | Kto decyduje | Decyzja |
|---|---|---|---|---|
| 16 | T3 | wiersz R22: napisu ekranu z liczba prac nierozstrzygnietych (`rano_nierozstrzygniete`, liczba 1) na ekranie BRAK - ta czesc wiersza odczytana tylko z API; wyniku T3 nie obniza | wlasciciel | |
| 17 | T5 | czesc B (atrapa na adresie karty PC) wykonana skryptem w sesji bez okien: polecenia konsoli atrap wpisywal skrypt wykonawcy (potok z pliku), posrednik ruchu uruchomiony przez pomocnik wlaczajacy Ctrl+C, posrednik ramki P na 127.0.0.1:8766 zamiast `<adres PC>:8768` (NOWE - sposob wykonania, liczb nie zmienia) - czy to wystarcza, czy czesc B powtorzyc recznie w sesji z oknami | wlasciciel / koordynator | |
| 18 | T5 | zapora Windows: nasluch na adresie karty <adres-IP> bez pytania; dostep z INNEGO komputera niesprawdzony (to T15) | informacja | |
| 19 | T5 (do T2) | obserwacja z kroku B4 (sterownik T2, proba skrocona 3 skany - to nie jest wynik T2): 1 praca z ubytkiem wg prawdy pokazana na ZIELONO (pozycja 8 scenariusza, sha16 247ee785f428396f); lista do dofrezowania ROZNA (oczekiwanych 13, w programie 12, brakuje 1; ubytki wg prawdy 13: czerwone 5, zolte 7, zielone 1); te same skany sa w pelnym scenariuszu T2 - `[W TOKU: T2]` | wlasciciel (po wyniku T2) | |
| 20 | T6 | regula 6 a wpisy `pominieto` logu Excela: puste pole `kuweta` w 2 wpisach na 200 w kazdym trybie (4 z 476 sprawdzonych wierszy; zlecenia bez numeru kuwety), a kazdy wpis `pominieto` (33 na 200) ma puste `wiersz` i `numer_zlecenia_b` (zaden wiersz arkusza nie zostal wskazany); test i wykonawca licza to jako zgodne z regula 6 - czy tak ma zostac | wlasciciel | |
| 21 | T7 | przypadek 4 (brak sieci): testy przypadku nie maja asercji komunikatu TEKSTOWEGO programu (sa: ikona "brak lacznosci" na ramce, komunikaty przypadku 5, ostrzezenie samokontroli); przyjeto "ZAL z odstepstwem O12"; wariant surowy: "brak komunikatu" = FAIL przypadku, wtedy T7 = FAIL (1 z 6) | koordynator | |
| 22 | T7 | przypadek 3 (brak folderu "Cyrkon"): komunikat ekranu `pula_brak_folderu` na programie z paczki NIE ZMIERZONY (w logu 0 wierszy w probach B1 i B1b - program nie zapisuje komunikatow ekranu do logu); potwierdzaja go test czesci A i wiersz samokontroli `BLAD folder_cyrkon` (kod 1); krok B1 planu do poprawienia | koordynator | |
| 23 | T7 | proby B2 / B3: wszystkie skany ze zrodla planu dostaly status `plytka_nie_z_trybu` (program startuje w trybie "Wieczor", plytki poranne); analiza byla pelna (23-56 s, 12 prac) - czy powtorzyc proby na skanach wieczornych | koordynator | |
| 24 | T7 | skan, ktorego analize przerwano zabiciem silnika, po restarcie programu NIE jest analizowany ponownie (status `blad`, "plikow znanych 3") - zgodnie z trescia komunikatu technik skanuje plytke ponownie | informacja (wlasciciel) | |
| 25 | T10 | poza kryterium T10: statusy gniazd rozne od tabeli R59 - zielony / czerwony / zolty / szary / pomaranczowy 116 / 66 / 201 / 26 / 4 wobec 150 / 65 / 161 / 33 / 4; glownie 22 gniazda "ok" -> "nie sprawdzono" (prace czesciowo widoczne / bokiem); 4 gniazda na slabsza strone (3 x czerwony -> zolty na pracach z ubytkami, 1 x zielony -> szary); w scenariuszu "dobrze" zielonych 111 (R59: 111) | wlasciciel / koordynator | |
| 26 | T12 | ocena "jedno polecenie" powrotu oparta na `Wroc_do_poprzedniej.cmd /bez-pauzy` z odpowiedzia `T` (kod 0) - wg zlecenia; polecenie planu `/tak /bez-pauzy` tez kod 0 (dodatkowy cykl) | koordynator | |
| 27 | T0 | czego T0 nie sprawdzil: dwuklik w Eksploratorze i pauza na koncu (uzyto `/bez-pauzy`), opcja `/skrot`, samodzielne szukanie Pythona (na tym PC `/python <sciezka>` jest obowiazkowe - Python lezy w profilu innego konta), instalacja Pythona z python.org, rozpakowanie Eksploratorem - przyjac do wizyty przy laptopie (`ODLOZONE.md`) albo zlecic probe | wlasciciel | |
| 28 | T0, T12 | poprawki PLANU: (a) polecenie `Expand-Archive` z kroku 2 zawodzi z sesji PowerShell 7 (zadzialalo z `set PSModulePath=&`); (b) `SHA256SUMS_wydania.txt` w commicie paczki (571e186) nie ma wiersza 0.3.1 ani 0.3.2 - plan powinien wskazac `main` | koordynator | |
| 29 | T1, T10 | informacje: (a) log punktu odniesienia `pytest_bazowy_bf00921.log` jest bez `-rs` - lista 9 pominietych odtworzona droga posrednia, wynik jednoznaczny; (b) w `<REPO>` po testach 2 pozycje ignorowane przez git (`ustawienia.toml`, `ramka/__pycache__/`); (c) czasy T10 (mediana 20,7 s na skan) mierzone pod obciazeniem - nie sa odniesieniem czasu plytki | informacja | |
| 30 | T10 | `t10_metryki.json` (pozycja listy dowodow planu) ma 1586 KB i nie przechodzi `dowody_lf.py` (limit 1024 KB) | koordynator - ROZSTRZYGNIETE w zleceniu E3-ODBIOR: plik nie idzie do repo, w repo `t10_wynik.md` + `t10_licz.json` (`dowody/T10/POMINIETE.txt`) | rozstrzygniete |

Do decyzji wlasciciela (stan 21.11, testy wykonane): pozycje 1, 5-9, 11-13, 15-17, 19, 20, 24, 25, 27 oraz po zakonczeniu testow w
toku 2-4, 10. Do decyzji koordynatora: 21-23, 26, 28. Informacje: 14, 18, 29; rozstrzygniete: 30.

## 5. FAIL i poprawki

Stan 21.11: w 9 testach wykonanych (T0, T1, T3, T5, T6, T7, T10, T12, T13 pierwszy przebieg) FAIL: 0. Testy w toku:
`[W TOKU: T2]`, `[W TOKU: T4]`, `[W TOKU: T8]`, `[W TOKU: T9]`, `[W TOKU: T11]`, `[W TOKU: T13 drugi przebieg]`.

| Nr | Test | Co nie przeszlo (liczba, log) | Paczka poprawki (galaz, PR) | Powtorka: wynik, data, dowod |
|---|---|---|---|---|
| | | | | |

## 6. Braki narzedzi stwierdzone przy planowaniu (stan na 20.11 - uzupelnic, co z nimi zrobiono)

| Nr | Brak | Skutek dla testu | Decyzja / paczka |
|---|---|---|---|
| B1 | sterownik T2 (program z paczki + pomiar petli okna + decyzje wg prawdy + zapis startu analizy) | T2: lista "do dofrezowania" i przerwy okna nie byly mierzone w jednym przebiegu przez program z paczki | USUNIETY: `narzedzia/t2_wieczor.py` + `t2_scenariusz.json` (E3-ODB etap 2, decyzja nr 12; po recenzji: kolory z ekranu, decyzja nr 18); proby skrocone na kopii repo i na instalacji probnej z paczki (21.11); pelnego przebiegu 10 x 60 s nie bylo |
| B2 | scenariusz SE10 przez ekran / kontroler aplikacji | T3: "przez ekran" niezmierzone | USUNIETY: `narzedzia/t3_poranek.py` (E3-ODB etap 2, decyzja nr 13); proba 20.11 na kopii integracyjnej: 32 z 32 |
| B3 | 200 zapytan przez prawdziwy Excel (COM) | T6 tylko na atrapie arkusza (dalej: T17) | |
| B4 | porownanie tekstow komunikatow z PW zal. F | T7: tabela sporzadzana recznie | zostaje (tabela reczna); regula wyniku: decyzja nr 14 (O12) |
| B5 | ostrzezenie z nazwa wlasciwego ukladu w aplikacji | T11: druga galaz kryterium niespelnialna | zostaje; regula wyniku: decyzja nr 15 (O6) |
| B6 | pliki napisow ekranu ze znakami spoza ASCII (7 nowych plikow) | T13: 7 naruszen na `main` 9ba9e91 | odstepstwo jawne O11 (decyzja nr 16); `t13_higiena.py` raportuje je osobno |

## 7. Zadania wlasciciela

| Nr | Zadanie | Co dostaje | Ile trwa | Stan |
|---|---|---|---|---|
| 1 | Proba T14 z osoba, ktora nie widziala programu | `T14/README.md`, zestaw `Ramki/etap3/t14/` | ok. 1 h | do wykonania; zestaw gotowy, kontrola zestawu na instalacji z paczki 0.3.1: zgodne 22 z 22 krokow, kod 0 (`dowody/T14/WYNIK.md`) |
| 2 | Wizyta przy laptopie stanowiska (T0, T2, T3 na laptopie; otwarte 4-6) | `ODLOZONE.md`, paczka wydania | 1-2 h | |
| 3 | Skaner: "Dzien skanera" i pierwsze skany (T16) | `ODLOZONE.md` | | |
| 4 | Ramki: zlozenie i siec (T15) | `ODLOZONE.md` | | |
| 5 | Raporty MillBox i kopia pliku Excela (T17) | `ODLOZONE.md` | | |
| 6 | Decyzje otwarte: tabela `testy_wykrywalnosci` (M2), waxup w folderze zlecenia, wygasanie listy brakow, kolory pola B, uwagi do pokazu G2 | `Ramki/00_NADZOR_STAN.md` | | |
| 7 | (jesli wyjdzie w T7) komunikaty spoza PW zal. F: uzupelnic zal. F albo zmienic napis - lista tekstow z `T7/t7_komunikaty.md` | decyzja nr 14, O12 | | WYSZLO w T7: 6 z 6 przypadkow (teksty: sekcja 4a.2 poz. 9, `dowody/T7/t7_komunikaty.md`) - do wykonania |
| 8 | (jesli wyjdzie w T4 / T2) pierwsza plytka po zimnym starcie programu ponad 40 s: przyjac albo zlecic poprawke - liczba sekund z `T4/t4_wynik.md` i `T2/t2_wynik.txt` | decyzja nr 17, O7 | | `[W TOKU: T4]`, `[W TOKU: T2]` |
| 9 | Decyzje do odstepstw i spraw z testow: lista w sekcji 4a (30 pozycji: 1-15 ze stanem w 4a.2, 16-30 w 4a.3; dla wlasciciela 17 pozycji z testow wykonanych + 4 po testach w toku) - kazda "przyjmuje" / "poprawic" / "powtorzyc test" | sekcja 4a, 4a.1-4a.3 | 30-45 min | czeka na komplet testow (`[W TOKU: liczniki]`) |
| 10 | Pokaz G3 "po fakcie": przeczytac opis instalacji, aktualizacji i powrotu z testow T0 i T12 i odpowiedziec na pytania z jego sekcji 7 | `POKAZ_G3.md` | 15-20 min | do wykonania |

## 8. Decyzje koordynatora przyjete domyslnie (do odwolania przez wlasciciela)

Z `Ramki/00_NADZOR_STAN.md` (19.11 i 20.11) - przepisac stan koncowy i dopisac decyzje z testow koncowych.

| Nr | Decyzja | Skad | Nadal obowiazuje |
|---|---|---|---|
| 1 | Pierwsza instalacja: wersja nie jest przelaczana przy czerwonej samokontroli ("wstrzymana - uzupelnij ustawienia", kod 10) | 20.11 nr 1 | |
| 2 | Folder danych w OneDrive / SharePoint: zmienne srodowiska i rejestr = BLAD, sama nazwa katalogu = OSTRZEZENIE | 20.11 nr 2 | |
| 3 | Brak folderu MillBox = OSTRZEZENIE | 20.11 nr 3 | |
| 4 | `Wroc_do_poprzedniej.cmd` bez argumentow pyta T / N | 20.11 nr 4 | |
| 5 | Python 3.12.10 wskazany; inne 3.12.x z ostrzezeniem | 20.11 nr 5 | |
| 6 | Numeracja wydan `0.3.<n>`; katalog domyslny `C:\Stanowisko`; skrot tylko na zadanie | 20.11 nr 6 | |
| 7 | Paczka nie jest odchudzana z zaleznosci nieuzywanych | 20.11 nr 7 | |
| 8 | Stare wersje i kopie bazy nie sa kasowane automatycznie | 20.11 nr 8 | |
| 9 | Obrazki instrukcji wpisane w strony `.html`; instrukcje dla `pula_wpisow = false` | 20.11 nr 9 | |
| 10 | Proba T14 w etapie 3 na atrapie kontrolera; powtorka na prawdziwym skanerze przed praca produkcyjna | 20.11 nr 10 | |
| 11 | Regula ponownego skanu (zbiory projektow >= 0,5); ramka W tylko ostatni skan; Enter na ramce = kuweta rozlozona; `maks_wiek_dni` 60; sprzatanie puli 30 dni; pusta pula = skany czekaja; kalibracja ramki obowiazkowa od C2 | 19.11 | |
| 12 | T2: kryterium mierzone na programie z paczki sterownikiem `t2_wieczor.py` (prawdziwy program, okno - offscreen dopuszczalny jako odstepstwo, prawdziwy silnik, decyzje kliknieciami wg tabeli prawdy), nie zastapione testami jednostkowymi | 20.11 wieczor, odpowiedz nr 1 na pytania E3-ODB | |
| 13 | T3: SE10 (32 wiersze, dane i tabela z `test_session_rano.py`) przeprowadzony przez okno programu sterownikiem `t3_poranek.py`; na pytanie przed "Zamknij piec" sterownik odpowiada wg scenariusza | 20.11 wieczor, nr 2 | |
| 14 | T7: komunikat i dalsza praca, ale tekst spoza PW zal. F = "ZAL z odstepstwem (komunikat spoza zal. F: <tekst>)" + zadanie wlasciciela; brak komunikatu / dalszej pracy / stanu = FAIL | 20.11 wieczor, nr 3 | |
| 15 | T11: uklad rozpoznany = zaliczone; ostrzezenie bez nazwy wlasciwego ukladu = FAIL tego skanu (licznik); zielona przy zlym ukladzie = FAIL calego testu | 20.11 wieczor, nr 4 | |
| 16 | T13: 7 plikow nie-ASCII z napisami ekranu = odstepstwo jawne O11 z lista plikow i liczba wierszy; skrypt raportuje je osobno i zglasza kazdy inny plik | 20.11 wieczor, nr 5 | |
| 17 | T4: podawane oba pomiary (pula zimna - pierwsza plytka; pula ciepla - kolejne) z licznikami "do 40 s: n z m"; tylko pierwsza po zimnym starcie ponad 40 s = "ZAL z odstepstwem" + decyzja wlasciciela; ktorakolwiek przy cieplej = FAIL | 20.11 wieczor, nr 6 | |
| 18 | T2 "lista = prawda": sterownik klika "Ukruszona" / "OK" wylacznie na pracach, ktore program pokazal na czerwono albo zolto (kolor z ekranu przed kliknieciem, zapisany w wyniku); praca z ubytkiem pokazana na zielono = przeoczona, nieklikana, FAIL listy z licznikiem; praca cala na czerwono = falszywy alarm, klikniecie "OK", licznik osobno | 21.11, decyzja nr 1 po recenzji PR #44 | |
| 19 | T9: szukanie nazw bez wielkosci liter i znakow diakrytycznych, w UTF-8, cp1250, UTF-16 LE, `\uXXXX`; dowod bez zadnego czlonu nazwy | 21.11, nr 2 | |
| 20 | T3: "n z 32" liczone z tego, co pokazuje ekran; rozbieznosc ekran / stan = wiersz niezgodny | 21.11, nr 3 | |
| 21 | T5, T6, T7 czesc A: testy na programie zainstalowanym z paczki; T5 "siec lokalna" - odstepstwo O8 w pelnym brzmieniu, prawdziwa siec = T15 | 21.11, nr 4 | |
| 22 | T11: wszystkie 40 skanow `*_r54` przez aplikacje; kryterium liczone pierwsza galezia, druga - do decyzji wlasciciela | 21.11, nr 5 | |
| 23 | "ZAL z odstepstwem" = osobna wartosc i osobny licznik; kazde odstepstwo O<n> na liscie decyzji wlasciciela | 21.11, nr 7 | |
| 24 | Odstepstwa nie przypisuje sie testom wykonalnym doslownie wg sekcji 7: T1, T8, T9, T10, T6, T11 moga dostac ZAL; T4 i T7 - ZAL, gdy nie zajdzie przypadek z O7 / O12 | 21.11, runda 2 recenzji PR #44 (uwaga 36) | |
| 25 | Wykonanie odbioru: paczki `Stanowisko_0.3.1.zip` i `Stanowisko_0.3.2.zip` (T12); T0 w `<PC-katalog>\t0\odbior\` = potem instalacja wspolna dla T1-T11 (kazdy test wlasny katalog danych w `robocze\odbior\T<nr>\`), T12 na wlasnej instalacji `<PC-katalog>\t0\odbior_t12\`; fale T-A / T-B / T-C; dowod kazdego testu z plikiem `WYNIK.md` | 21.11, zlecenie rundy 2; `PLAN_TESTOW.md`, sekcja "Ustalenia koordynatora do wykonania odbioru" | |
| 26 | Dowody w repo: `t10_metryki.json` (1586 KB, ponad limit 1024 KB) NIE idzie do repo - w repo zostaja `t10_wynik.md` + `t10_licz.json`; pliki pominiete kazdego testu wypisane w `dowody/T<nr>/POMINIETE.txt` | 21.11, zlecenie E3-ODBIOR | |
| | (dalsze decyzje z testow koncowych - po testach w toku) | | |

## 9. Podpis

Koordynator: ____ ; data: ____ ; `main` po odbiorze: ____ ; koniec etapu 3: TAK / NIE (powod).
