# T7 czesc A - testy z `<REPO>` na kodzie programu z instalacji wspolnej (odbior 21.11.2026)

Instalacja WSPOLNA `<K>` = `<PC-katalog>\t0\odbior\Stanowisko` (wersja 0.3.1, commit 571e186cb817, z pytest po kroku `/testy`;
znak `<PC-katalog>\koordynator\robocze\odbior\T0\GOTOWE.txt` z 02:51:47 - sprawdzony przed startem, czekania nie bylo).
`<ST>` = `<PC-katalog>\t0\repo\Ramki\stanowisko`, `<ODB>` = `<PC-katalog>\t0\repo\Ramki\etap3\odbior_koncowy`,
`<ROB>` = `<PC-katalog>\koordynator\robocze\odbior\T7`. Jeden plik `krok_A.cmd` (15 polecen, kazde z `call`, wejscie `< NUL`,
`set QT_QPA_PLATFORM=offscreen`) pod blokada `ciezki.ps1 -Tor 4 -Kto odb-T7`: 03:03:56-03:08:06 (4 min 10 s). Kody: `kody.txt`
(wiersze `A_*`), godziny: `czasy.txt`.

Postac kazdego polecenia (doslownie z planu):
`<K>\Polecenie.cmd <ODB>\narzedzia\pytest_instalacja.py --st <ST> --wynik <ROB>\t7_<nr>_zrodlo_kodu.txt -- <ST>\testy\<plik> -q -rA -p no:cacheprovider --rootdir <ST> -k "<nazwy>" > <ROB>\t7_<nr>.log 2>&1`
(dla `test_p14_baza_zajeta.py` bez `-k` - caly plik).

| Nr | Przypadek | Plik testow | `-k` | Kod | Wiersz podsumowania pytest | PASSED | Zrodlo kodu | Moduly z instalacji / z repo | Czas |
|---|---|---|---|---|---|---|---|---|---|
| 1a | zabicie silnika | `test_aplikacja.py` | `test_zabity_proces_analizy_komunikat_i_nastepny_skan or test_silnik_nie_startuje_skan_czeka_i_wraca_po_restarcie` | 0 | 2 passed, 27 deselected in 3.71s | 2 | INSTALACJA | 42 / 0 | 6,3 s |
| 1b | zabicie silnika | `test_silnik.py` | `test_zabicie_procesu_z_zewnatrz or test_awarie_zly_plik_zabity_proces_brak_pliku or test_awaria_prawdziwej_analizy_i_nastepne_zadanie` | 0 | 3 passed, 66 deselected in 111.99s (0:01:51) | 3 | INSTALACJA | 34 / 0 | 114,7 s |
| 2a | zamkniecie w polowie wieczoru | `test_aplikacja.py` | `test_e_zamkniecie_w_trakcie_analizy_i_ponowny_start or test_e_awaria_bez_zamkniecia_nadrabianie_folderu or test_e_dodatkowe_punkty_awarii` | 0 | 3 passed, 26 deselected in 8.82s | 3 | INSTALACJA | 42 / 0 | 11,2 s |
| 2b | zamkniecie w polowie wieczoru | `test_ui_wieczor.py` | `test_5_restart_programu_odtwarza_plytki_i_decyzje_na_ekranie` | 0 | 1 passed, 88 deselected in 5.14s | 1 | INSTALACJA | 54 / 0 | 7,8 s |
| 3a | brak folderu "Cyrkon" | `test_aplikacja.py` | `test_g_bez_projektow_skany_czekaja_do_odswiezenia_puli or test_folder_skanera_pojawia_sie_pozniej` | 0 | 2 passed, 27 deselected in 3.73s | 2 | INSTALACJA | 42 / 0 | 6,3 s |
| 3b | brak folderu "Cyrkon" | `test_pula_aplikacja_r3.py` | `test_r3_d8_nieudane_odswiezenie_ponawiane` | 0 | 1 passed, 3 deselected in 4.68s | 1 | INSTALACJA | 22 / 0 | 7,7 s |
| 4a | brak sieci | `test_indicate.py` | `test_k5_utrata_sieci_5_potwierdzen_100_powtorzen` | 0 | 1 passed, 34 deselected in 31.03s | 1 | INSTALACJA | 17 / 0 | 33,5 s |
| 4b | brak sieci | `test_ramka.py` | `test_k5_utrata_sieci or test_ramka_poranna_bez_sieci_trzyma_plan_do_limitu` | 0 | 2 passed, 82 deselected in 5.14s | 2 | INSTALACJA | 16 / 0 | 7,0 s |
| 4c | brak sieci | `test_excel.py` | `test_excel_niedostepny_komunikat_bez_awarii` | 0 | 1 passed, 128 deselected in 0.16s | 1 | INSTALACJA | 10 / 0 | 2,0 s |
| 5a | brak ramki | `test_aplikacja_rano.py` | `test_k5_wylaczona_ramka_i_brak_excela_ostrzezenie_i_dalsza_praca` | 0 | 1 passed, 27 deselected in 4.71s | 1 | INSTALACJA | 57 / 0 | 6,6 s |
| 5b | brak ramki | `test_ui_rano.py` | `test_k5_bez_ramki_i_excela_komunikat_program_dziala_dalej` | 0 | 1 passed, 31 deselected in 1.89s | 1 | INSTALACJA | 48 / 0 | 3,8 s |
| 6a | baza zajeta | `test_aplikacja.py` | `test_baza_zajeta_wynik_nie_ginie or test_p8_blad_analizy_przy_zajetej_bazie` | 0 | 2 passed, 27 deselected in 3.17s | 2 | INSTALACJA | 42 / 0 | 5,1 s |
| 6b | baza zajeta | `test_baza.py` | `test_d1_baza_zajeta_przez_inny_proces_daje_czytelny_komunikat` | 0 | 1 passed, 69 deselected in 0.59s | 1 | INSTALACJA | 6 / 0 | 2,5 s |
| 6c | baza zajeta | `test_aplikacja_rano.py` | `test_d2_baza_zajeta_zdarzenia_ramki_czekaja_i_wracaja` | 0 | 1 passed, 27 deselected in 2.19s | 1 | INSTALACJA | 38 / 0 | 4,1 s |
| 6d | baza zajeta | `test_p14_baza_zajeta.py` | (caly plik) | 0 | 27 passed in 29.09s | 27 | INSTALACJA | 54 / 0 | 31,2 s |

## Liczniki czesci A

- Polecen 15 z 15 z kodem 0; testow **49 passed, 0 failed, 0 error, 0 skipped** (wybranych `-k`: 22 + caly plik P14: 27).
- Na przypadek: 1 - 5 passed (2 + 3); 2 - 4 (3 + 1); 3 - 3 (2 + 1); 4 - 4 (1 + 2 + 1); 5 - 2 (1 + 1); 6 - 31 (2 + 1 + 1 + 27).
  Liczby zgodne z proba na instalacji probnej z planu ("Stan sprawdzenia polecen": 2: 4; 3: 3; 4: 3 + `test_k5` z `test_indicate.py`;
  5: 2; 6: 1 + 30; 1: 2 + 3).
- `WERDYKT ZRODLA KODU: INSTALACJA` w 15 z 15 przebiegow; modulow programu zaladowanych z repo: 0 w kazdym; "pliki *.py instalacji
  (stanowisko, ramka, narzedzia) = repo: 79 z 79" w kazdym; plik ustawien domyslnych w testach: `<ST>\ustawienia.toml`.
  Odstepstwo O14 NIE zachodzi (zaden werdykt "REPO", zaden kod 3).
- Ograniczenie z planu (przypadek 1, `test_silnik.py`): proces silnika zaklada test - importuje kod sam; zgodnosc kodu potwierdza
  wiersz "pliki instalacji = repo: 79 z 79".
- Zjawiska PC (0xC0000409, 0xC0000142): nie wystapily (kody wyjscia 15 x 0).
- W logu `t7_1a.log` slowa "ERROR" / "WARNING" to przechwycony log programu w tescie (zamierzona awaria silnika), nie blad testu.
- Co jeszcze liczylo na PC w tym czasie (`ciezkie.log`): tor 1 - T1 pelny pytest (od 02:53:21), tor 2 - T10 (do 03:06:49), tor 3 - T5
  (do 03:03:56). Testy czesci A nie maja wlasnych progow czasu w kryterium T7.

Komunikaty i asercje "dalsza praca" / "stan z bazy": `t7_komunikaty.md`. Proby reczne czesci B: `t7_proby_reczne.md`.
