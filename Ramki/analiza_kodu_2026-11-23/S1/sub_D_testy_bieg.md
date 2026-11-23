# S1 / sub D - bieg wybranych plikow testow (2026-11-23)

Katalog roboczy: <PC-katalog>\qc-wt\analiza-s1\Ramki\stanowisko (worktree git, galaz analiza/s1, HEAD 480359f)
Interpreter: <PC-katalog>\koordynator\narz\py.cmd (pliki uruchamiane po kolei, jeden proces python naraz, bez -n)
Polecenie (dla kazdego <plik>), w PowerShell z katalogu roboczego:

    cmd /c "<PC-katalog>\koordynator\narz\py.cmd -m pytest testy\<plik> -q -p no:cacheprovider --durations=5 > <PC-katalog>\qc-wt\analiza-s1\Ramki\analiza_kodu_2026-11-23\S1\log_<plik>.txt 2>&1"

Logi: <PC-katalog>\qc-wt\analiza-s1\Ramki\analiza_kodu_2026-11-23\S1\log_<plik>.txt (np. log_test_inspect.py.txt).
Czas scienny mierzony Stopwatch wokol polecenia cmd /c (z uruchomieniem interpretera).

## Tabela

| # | plik | polecenie | kod wyjscia | wiersz podsumowania pytest | czas scienny [s] | failed / error |
|---|------|-----------|-------------|----------------------------|------------------|----------------|
| 1 | testy\test_porownaj_bledy.py | jak wyzej, log_test_porownaj_bledy.py.txt | 1 | 5 errors in 0.57s | 2.4 | 5 error (setup), wszystkie FileNotFoundError brak pliku ustawien |
| 2 | testy\test_inspect.py | jak wyzej, log_test_inspect.py.txt | 1 | 5 passed, 21 errors in 3.14s | 5.0 | 21 error (setup), wszystkie FileNotFoundError brak pliku ustawien |
| 3 | testy\test_krawedz.py | jak wyzej, log_test_krawedz.py.txt | 0 | 15 passed in 14.42s | 16.2 | brak |
| 4 | testy\test_skala.py | jak wyzej, log_test_skala.py.txt | 1 | 3 passed, 11 errors in 1.37s | 3.2 | 11 error (setup), wszystkie FileNotFoundError brak pliku ustawien |
| 5 | testy\test_auto_uklad_r58.py | jak wyzej, log_test_auto_uklad_r58.py.txt | 0 | 52 passed in 174.46s (0:02:54) | 176.5 (uwaga ponizej) | brak |
| 6 | testy\test_straznik.py | jak wyzej, log_test_straznik.py.txt | 1 | 4 passed, 26 errors in 4.69s | 6.6 | 26 error (setup), wszystkie FileNotFoundError brak pliku ustawien |

Suma: 79 passed, 0 failed, 63 errors (wszystkie 63 to ten sam FileNotFoundError), 0 skipped.

Uwaga do pliku 5: polecenie przekroczylo limit narzedzia 175 s (narzedzie przenioslo je w tlo po 175 s), ale proces skonczyl sie sam po 176.5 s (pytest: 174.46 s), z kodem 0 i pelnym logiem - ponizej 3 min (180 s). Nie bylo ponowienia. Sprawdzenie zaraz potem (Get-CimInstance / Get-Process python): brak procesu python z test_auto_uklad_r58 - nic nie zatrzymywano. W tym czasie nie uruchamiano zadnego innego polecenia.

## Pierwszy wiersz bledu (identyczny dla wszystkich 63 errors)

    E   FileNotFoundError: brak pliku ustawien: <PC-katalog>\qc-wt\analiza-s1\Ramki\stanowisko\ustawienia.toml - skopiuj ustawienia.przyklad.toml jako ustawienia.toml i uzupelnij sciezki
    (stanowisko\ustawienia.py:352)

Miejsce wywolania w testach:
- test_porownaj_bledy.py:24 - fixture `ust` (scope=module): `UST.wczytaj_ustawienia()`
- test_inspect.py:19 - fixture `ust`: `UST.wczytaj_ustawienia()`
- test_skala.py:21 - fixture `ust`: `UST.wczytaj_ustawienia()`
- test_straznik.py:49 fixture `skany` -> :34 `_skan` -> `synth.Opcje.z_toml(...)` -> stanowisko\synth.py:865 `UST.domyslne()` -> stanowisko\ustawienia.py:372 `wczytaj_ustawienia()`

## Nazwy testow z bledem (error at setup)

1. test_porownaj_bledy.py (5):
   test_blad_inspekcji_jednego_gniazda_nie_kladzie_plytki;
   test_cli_zapisuje_wynik_mimo_bledu_inspekcji;
   test_przerwanie_i_brak_pamieci_nie_sa_lapane[wyjatek0], [wyjatek1], [wyjatek2]

2. test_inspect.py (21):
   test_ubytki_z_prawdy_sa_wykrywane; test_ubytek_w_ukladzie_plytki_blisko_prawdy; test_praca_cala_bez_alarmu;
   test_drgniecie_daje_skan_ponownie; test_niskie_pokrycie_to_popraw_ulozenie;
   test_poprawka_reczna_bez_ostrej_krawedzi_to_pomaranczowe; test_brak_danych_w_skanie_nie_jest_ubytkiem;
   test_praca_bokiem_nigdy_czerwona; test_progi_z_ustawien_steruja_wynikiem;
   test_wykryj_drgniecie_na_sztucznych_odchylkach; test_plamy_ostra_vs_lagodna; test_json_wyniku_bez_tablic;
   test_pas_od_linii_obejmuje_brzeg_ponizej_plaszczyzny; test_tryb_sumy_pasow_obejmuje_brzeg_gleboki_i_stary_pas;
   test_praca_cala_z_glebokim_brzegiem_jest_zielona; test_brak_danych_przy_linii_brzegu_to_nie_sprawdzono;
   test_brak_danych_i_ukruszenie_obok_nigdy_czerwone_z_braku_danych;
   test_linia_projektu_niepewna_albo_brak_linii_to_nie_sprawdzono;
   test_projekt_bez_linii_z_wcieciem_w_trybie_sumy_dziala_jak_przed_p2;
   test_filar_z_niecka_bez_linii_nie_znika_po_cichu;
   test_prace_bokiem_i_czesciowe_nie_sa_zielone_bez_sprawdzonego_brzegu

4. test_skala.py (11):
   test_estymata_skali_i_korekta[-1.0], [0.0], [0.5]; test_poza_oknem_bez_korekty_z_ostrzezeniem;
   test_plytka_poranna_tylko_pomiar; test_ustawienia_steruja_korekta; test_strefa_brzegu_nie_wplywa_na_skale;
   test_inspekcja_w_skali_skorygowanej_praca_cala; test_korekta_nie_zjada_ukruszen;
   test_estymata_niepewna_bez_ostrzezenia; test_porownaj_pola_skali_i_tabela

6. test_straznik.py (26):
   test_plytka_innego_ukladu_konczy_sie_niezgodny_uklad[stara_plytka_nowy_uklad-{wieczorna, poranna, okragla_wieczorna, okragla_poranna}] (4);
   test_plytka_innego_ukladu_konczy_sie_niezgodny_uklad[nowa_plytka_stary_uklad-{wieczorna, poranna, okragla_wieczorna, okragla_poranna}] (4);
   test_plytka_zgodna_bez_falszywego_alarmu[{wieczorna, poranna, okragla_wieczorna, okragla_poranna, wieczorna_r54, poranna_r54, okragla_wieczorna_r54, okragla_poranna_r54}] (8);
   test_stozki_pasuja_ale_gniazda_inne[wieczorna-wieczorna_r54], [wieczorna_r54-wieczorna], [poranna-poranna_r54], [poranna_r54-poranna] (4);
   test_porownaj_niezgodny_uklad_zadnych_gniazd; test_porownaj_zgodny_uklad_ma_flage;
   test_cli_porownaj_niezgodny_zapisuje_wynik_bez_metryk; test_okno_lista_ukladow_i_komunikat_straznika;
   test_stary_plik_ustawien_podpowiada_brakujace_uklady_r54; test_okno_podpowiada_brak_ukladow_r54

## 5 najwolniejszych (z --durations=5)

1. test_porownaj_bledy.py: 0.09s setup test_blad_inspekcji_jednego_gniazda_nie_kladzie_plytki (pozostale 4 < 0.005s, ukryte)
2. test_inspect.py: 1.02s call test_polozenie_ubytku_starej_prawdy_z_linii_projektu; 0.81s setup test_pas_od_linii_obejmuje_brzeg_ponizej_plaszczyzny; 0.43s setup test_ubytki_z_prawdy_sa_wykrywane (2 < 0.005s, ukryte)
3. test_krawedz.py: 6.14s call test_most_ma_petle_na_kazdy_filar; 2.15s call test_pamiec_w_module_i_na_dysku; 2.12s call test_filar_z_niecka_bez_linii_jest_jawny; 1.26s call test_skala_i_przesuniecie_nie_zmieniaja_linii; 1.17s setup test_korona_ma_jedna_petle_na_brzegu
4. test_skala.py: 0.44s setup test_estymata_skali_i_korekta[-1.0]; 0.34s call test_pula_wspolczynnik_dla_projektu (3 < 0.005s, ukryte)
5. test_auto_uklad_r58.py: 46.83s setup test_rozpoznaje_kazdy_z_dziesieciu_ukladow_bez_numeru[wieczorna]; 7.75s call test_male_pole_96_i_94_uklad_dobry_i_pewny[poranna-4-94.0]; 7.59s call test_male_pole_96_i_94_uklad_dobry_i_pewny[wieczorna-1-96.0]; 7.42s call test_narzedzie_maly_przebieg_zapisuje_wyniki; 7.14s call test_male_pole_96_i_94_uklad_dobry_i_pewny[okragla_ramkowa_poranna-5-94.0]
6. test_straznik.py: 0.83s call test_zgodnosc_ukladu_na_pustych_plytkach[poranna]; 0.83s call [okragla_poranna]; 0.82s call [okragla_wieczorna]; 0.79s call [wieczorna]; 0.08s setup test_plytka_innego_ukladu_konczy_sie_niezgodny_uklad[stara_plytka_nowy_uklad-wieczorna]

## Ustalenia o ustawienia.toml (tylko odczyt kodu i Test-Path; nic nie utworzono)

- Test-Path:
  - <PC-katalog>\qc-wt\analiza-s1\Ramki\stanowisko\ustawienia.toml - False (jest tylko ustawienia.przyklad.toml)
  - <PC-katalog>\qc\Ramki\stanowisko\ustawienia.toml - False (glowny worktree, galaz main, b856b9e)
  - <PC>\Desktop\Ramki\stanowisko\ustawienia.toml - True
- stanowisko\ustawienia.py:19-21: `KORZEN = Path(__file__).resolve().parent.parent` (katalog Ramki\stanowisko tego samego drzewa, z ktorego importowany jest pakiet), `PLIK_USTAWIEN = KORZEN / "ustawienia.toml"`, `PLIK_PRZYKLADU = KORZEN / "ustawienia.przyklad.toml"`.
- stanowisko\ustawienia.py:348-354: `wczytaj_ustawienia(plik=None)` bierze `PLIK_USTAWIEN`; gdy plik nie istnieje - FileNotFoundError. Brak przejscia na PLIK_PRZYKLADU i brak zmiennej srodowiskowej (w ustawienia.py nie ma `environ`/`getenv`).
- stanowisko\ustawienia.py:369-372: `domyslne()` (lru_cache) = `wczytaj_ustawienia()` - ta sama sciezka; uzywa jej m.in. `synth.Opcje.z_toml` (synth.py:865), gdy nie podano `ust`.
- testy\conftest.py: tylko sys.path (STANOWISKO, STANOWISKO\narzedzia), import pakietu `stanowisko`, fixture `korony`, `korona_siekacz`, `uklad_tmp` (monkeypatch U.KATALOG_MODELI) i `zapisz_ascii_stl`. Nie ma fixture ustawien, nie podmienia PLIK_USTAWIEN, nie ustawia zmiennych srodowiskowych.
- W Ramki\stanowisko brak pytest.ini / pyproject.toml / setup.cfg / tox.ini.
- Ramki\stanowisko\.gitignore:10 `ustawienia.toml` - plik nie jest w repozytorium, wiec swiezy worktree go nie ma (git check-ignore potwierdza).
- README.md:11-15 (stanowisko): procedura `copy ustawienia.przyklad.toml ustawienia.toml`, `set PYTHONUTF8=1`, potem `py -3.12 -m pytest testy -q`; README.md:168 to samo w "Sprawdzenie". Czyli wg kodu i README testy z `wczytaj_ustawienia()` / `UST.domyslne()` biora ustawienia z lokalnego, nieskladowanego w git pliku `<KORZEN>\ustawienia.toml`, ktory ma byc wczesniej skopiowany ze wzoru.
- Czesc testow czyta wprost wzor: `UST.wczytaj_ustawienia(UST.PLIK_PRZYKLADU)` - np. test_auto_uklad_r58.py:39 (stad 52 passed), test_skala.py:261 (jeden test). test_krawedz.py w ogole nie siega do ustawien.
- W calym katalogu testy (59 plikow test_*.py): 18 plikow odwoluje sie do pliku domyslnego (`wczytaj_ustawienia()`, `UST.domyslne()` lub `PLIK_USTAWIEN`): test_aplikacja, test_auto_uklad, test_dzien_skanera, test_edge_synth, test_inspect, test_match, test_o4_instalacja_dzien_skanera, test_okragle_wydanie, test_porownaj_bledy, test_pula_match, test_samokontrola, test_session_wieczor, test_skala, test_straznik, test_ui, test_uklad_r58, test_uklad, test_ustawienia; 13 plikow uzywa `wczytaj_ustawienia(UST.PLIK_PRZYKLADU)` (czesc z nich w obu wariantach). Tych pozostalych plikow nie uruchamiano.
- test_straznik.py:156 tez wola `UST.wczytaj_ustawienia()` bez argumentu (dodatkowo do sciezki przez skany/_skan).

## Czas i RAM

- Laczny czas scienny testow: 2.4 + 5.0 + 16.2 + 3.2 + 176.5 + 6.6 = 209.9 s (ok. 3.5 min); od startu pliku 1 (15:58:52) do konca pliku 6 (ok. 16:03:11) ok. 4 min 20 s z narzutem.
- Po plikach 1-4: 26.8 s (< 9 min), wiec pliki 5 i 6 uruchomione.
- Wolny RAM przed (ram.cmd, 15:58:47): 73719 MB wolne z 95652
- Wolny RAM po (ram.cmd, po pliku 6): 73505 MB wolne z 95652

## Niewykonane / ograniczenia

- 63 testy (pliki 1, 2, 4, 6) nie doszly do ciala testu - blad w setup fixture z powodu braku ustawienia.toml; ich wynik merytoryczny nieznany.
- Zgodnie z zasadami: nie tworzono ustawienia.toml, nie powtarzano zadnego pliku (bledy to setup, nie bledy zbierania/importu), brak zmian w kodzie i testach, brak commitow.
- Plik 5 przekroczyl limit narzedzia 175 s o ok. 1.5 s (zakonczyl sie sam przed 180 s, kod 0) - patrz uwaga pod tabela.
- pytest zapisywal pliki tymczasowe w swoim domyslnym katalogu <PC>\AppData\Local\Temp\pytest-of-<uzytkownik>\ (poza repozytorium).
