@echo off
rem T7 czesc A: testy z <REPO> na kodzie programu z instalacji WSPOLNEJ (pytest_instalacja.py); osobne polecenie na kazdy plik testow
set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe
set QT_QPA_PLATFORM=offscreen
set ROB=<PC-katalog>\koordynator\robocze\odbior\T7
set K=<PC-katalog>\t0\odbior\Stanowisko
set ST=<PC-katalog>\t0\repo\Ramki\stanowisko
set ODB=<PC-katalog>\t0\repo\Ramki\etap3\odbior_koncowy
echo A_1a START %date% %time% >> %ROB%\czasy.txt
call %K%\Polecenie.cmd %ODB%\narzedzia\pytest_instalacja.py --st %ST% --wynik %ROB%\t7_1a_zrodlo_kodu.txt -- %ST%\testy\test_aplikacja.py -q -rA -p no:cacheprovider --rootdir %ST% -k "test_zabity_proces_analizy_komunikat_i_nastepny_skan or test_silnik_nie_startuje_skan_czeka_i_wraca_po_restarcie" < NUL > %ROB%\t7_1a.log 2>&1
echo A_1a test_aplikacja.py KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo A_1a KONIEC %date% %time% >> %ROB%\czasy.txt
echo A_1b START %date% %time% >> %ROB%\czasy.txt
call %K%\Polecenie.cmd %ODB%\narzedzia\pytest_instalacja.py --st %ST% --wynik %ROB%\t7_1b_zrodlo_kodu.txt -- %ST%\testy\test_silnik.py -q -rA -p no:cacheprovider --rootdir %ST% -k "test_zabicie_procesu_z_zewnatrz or test_awarie_zly_plik_zabity_proces_brak_pliku or test_awaria_prawdziwej_analizy_i_nastepne_zadanie" < NUL > %ROB%\t7_1b.log 2>&1
echo A_1b test_silnik.py KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo A_1b KONIEC %date% %time% >> %ROB%\czasy.txt
echo A_2a START %date% %time% >> %ROB%\czasy.txt
call %K%\Polecenie.cmd %ODB%\narzedzia\pytest_instalacja.py --st %ST% --wynik %ROB%\t7_2a_zrodlo_kodu.txt -- %ST%\testy\test_aplikacja.py -q -rA -p no:cacheprovider --rootdir %ST% -k "test_e_zamkniecie_w_trakcie_analizy_i_ponowny_start or test_e_awaria_bez_zamkniecia_nadrabianie_folderu or test_e_dodatkowe_punkty_awarii" < NUL > %ROB%\t7_2a.log 2>&1
echo A_2a test_aplikacja.py KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo A_2a KONIEC %date% %time% >> %ROB%\czasy.txt
echo A_2b START %date% %time% >> %ROB%\czasy.txt
call %K%\Polecenie.cmd %ODB%\narzedzia\pytest_instalacja.py --st %ST% --wynik %ROB%\t7_2b_zrodlo_kodu.txt -- %ST%\testy\test_ui_wieczor.py -q -rA -p no:cacheprovider --rootdir %ST% -k "test_5_restart_programu_odtwarza_plytki_i_decyzje_na_ekranie" < NUL > %ROB%\t7_2b.log 2>&1
echo A_2b test_ui_wieczor.py KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo A_2b KONIEC %date% %time% >> %ROB%\czasy.txt
echo A_3a START %date% %time% >> %ROB%\czasy.txt
call %K%\Polecenie.cmd %ODB%\narzedzia\pytest_instalacja.py --st %ST% --wynik %ROB%\t7_3a_zrodlo_kodu.txt -- %ST%\testy\test_aplikacja.py -q -rA -p no:cacheprovider --rootdir %ST% -k "test_g_bez_projektow_skany_czekaja_do_odswiezenia_puli or test_folder_skanera_pojawia_sie_pozniej" < NUL > %ROB%\t7_3a.log 2>&1
echo A_3a test_aplikacja.py KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo A_3a KONIEC %date% %time% >> %ROB%\czasy.txt
echo A_3b START %date% %time% >> %ROB%\czasy.txt
call %K%\Polecenie.cmd %ODB%\narzedzia\pytest_instalacja.py --st %ST% --wynik %ROB%\t7_3b_zrodlo_kodu.txt -- %ST%\testy\test_pula_aplikacja_r3.py -q -rA -p no:cacheprovider --rootdir %ST% -k "test_r3_d8_nieudane_odswiezenie_ponawiane" < NUL > %ROB%\t7_3b.log 2>&1
echo A_3b test_pula_aplikacja_r3.py KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo A_3b KONIEC %date% %time% >> %ROB%\czasy.txt
echo A_4a START %date% %time% >> %ROB%\czasy.txt
call %K%\Polecenie.cmd %ODB%\narzedzia\pytest_instalacja.py --st %ST% --wynik %ROB%\t7_4a_zrodlo_kodu.txt -- %ST%\testy\test_indicate.py -q -rA -p no:cacheprovider --rootdir %ST% -k "test_k5_utrata_sieci_5_potwierdzen_100_powtorzen" < NUL > %ROB%\t7_4a.log 2>&1
echo A_4a test_indicate.py KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo A_4a KONIEC %date% %time% >> %ROB%\czasy.txt
echo A_4b START %date% %time% >> %ROB%\czasy.txt
call %K%\Polecenie.cmd %ODB%\narzedzia\pytest_instalacja.py --st %ST% --wynik %ROB%\t7_4b_zrodlo_kodu.txt -- %ST%\testy\test_ramka.py -q -rA -p no:cacheprovider --rootdir %ST% -k "test_k5_utrata_sieci or test_ramka_poranna_bez_sieci_trzyma_plan_do_limitu" < NUL > %ROB%\t7_4b.log 2>&1
echo A_4b test_ramka.py KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo A_4b KONIEC %date% %time% >> %ROB%\czasy.txt
echo A_4c START %date% %time% >> %ROB%\czasy.txt
call %K%\Polecenie.cmd %ODB%\narzedzia\pytest_instalacja.py --st %ST% --wynik %ROB%\t7_4c_zrodlo_kodu.txt -- %ST%\testy\test_excel.py -q -rA -p no:cacheprovider --rootdir %ST% -k "test_excel_niedostepny_komunikat_bez_awarii" < NUL > %ROB%\t7_4c.log 2>&1
echo A_4c test_excel.py KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo A_4c KONIEC %date% %time% >> %ROB%\czasy.txt
echo A_5a START %date% %time% >> %ROB%\czasy.txt
call %K%\Polecenie.cmd %ODB%\narzedzia\pytest_instalacja.py --st %ST% --wynik %ROB%\t7_5a_zrodlo_kodu.txt -- %ST%\testy\test_aplikacja_rano.py -q -rA -p no:cacheprovider --rootdir %ST% -k "test_k5_wylaczona_ramka_i_brak_excela_ostrzezenie_i_dalsza_praca" < NUL > %ROB%\t7_5a.log 2>&1
echo A_5a test_aplikacja_rano.py KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo A_5a KONIEC %date% %time% >> %ROB%\czasy.txt
echo A_5b START %date% %time% >> %ROB%\czasy.txt
call %K%\Polecenie.cmd %ODB%\narzedzia\pytest_instalacja.py --st %ST% --wynik %ROB%\t7_5b_zrodlo_kodu.txt -- %ST%\testy\test_ui_rano.py -q -rA -p no:cacheprovider --rootdir %ST% -k "test_k5_bez_ramki_i_excela_komunikat_program_dziala_dalej" < NUL > %ROB%\t7_5b.log 2>&1
echo A_5b test_ui_rano.py KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo A_5b KONIEC %date% %time% >> %ROB%\czasy.txt
echo A_6a START %date% %time% >> %ROB%\czasy.txt
call %K%\Polecenie.cmd %ODB%\narzedzia\pytest_instalacja.py --st %ST% --wynik %ROB%\t7_6a_zrodlo_kodu.txt -- %ST%\testy\test_aplikacja.py -q -rA -p no:cacheprovider --rootdir %ST% -k "test_baza_zajeta_wynik_nie_ginie or test_p8_blad_analizy_przy_zajetej_bazie" < NUL > %ROB%\t7_6a.log 2>&1
echo A_6a test_aplikacja.py KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo A_6a KONIEC %date% %time% >> %ROB%\czasy.txt
echo A_6b START %date% %time% >> %ROB%\czasy.txt
call %K%\Polecenie.cmd %ODB%\narzedzia\pytest_instalacja.py --st %ST% --wynik %ROB%\t7_6b_zrodlo_kodu.txt -- %ST%\testy\test_baza.py -q -rA -p no:cacheprovider --rootdir %ST% -k "test_d1_baza_zajeta_przez_inny_proces_daje_czytelny_komunikat" < NUL > %ROB%\t7_6b.log 2>&1
echo A_6b test_baza.py KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo A_6b KONIEC %date% %time% >> %ROB%\czasy.txt
echo A_6c START %date% %time% >> %ROB%\czasy.txt
call %K%\Polecenie.cmd %ODB%\narzedzia\pytest_instalacja.py --st %ST% --wynik %ROB%\t7_6c_zrodlo_kodu.txt -- %ST%\testy\test_aplikacja_rano.py -q -rA -p no:cacheprovider --rootdir %ST% -k "test_d2_baza_zajeta_zdarzenia_ramki_czekaja_i_wracaja" < NUL > %ROB%\t7_6c.log 2>&1
echo A_6c test_aplikacja_rano.py KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo A_6c KONIEC %date% %time% >> %ROB%\czasy.txt
echo A_6d START %date% %time% >> %ROB%\czasy.txt
call %K%\Polecenie.cmd %ODB%\narzedzia\pytest_instalacja.py --st %ST% --wynik %ROB%\t7_6d_zrodlo_kodu.txt -- %ST%\testy\test_p14_baza_zajeta.py -q -rA -p no:cacheprovider --rootdir %ST% < NUL > %ROB%\t7_6d.log 2>&1
echo A_6d test_p14_baza_zajeta.py KOD=%ERRORLEVEL% >> %ROB%\kody.txt
echo A_6d KONIEC %date% %time% >> %ROB%\czasy.txt
exit /b 0
