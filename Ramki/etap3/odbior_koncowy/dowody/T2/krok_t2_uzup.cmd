@echo off
rem T2 - testy uzupelniajace (PO sterowniku): A = przez pytest_instalacja.py (kod programu z instalacji; polecenie koordynatora),
rem B = polecenia planu doslownie (Polecenie.cmd -m pytest; kod programu z repo przez conftest)
set PY=<PC>\AppData\Local\Programs\Python\Python312\python.exe
set QT_QPA_PLATFORM=offscreen
set K=<PC-katalog>\t0\odbior\Stanowisko
set ST=<PC-katalog>\t0\repo\Ramki\stanowisko
set ODB=<PC-katalog>\t0\repo\Ramki\etap3\odbior_koncowy
set ROB=<PC-katalog>\koordynator\robocze\odbior\T2
set E3A3_DANE_REF=<PC-katalog>\app\dane_ref\syntetyczne_R59_P2
set E3A3_PROJEKTY=%ROB%\robocze\Cyrkon
echo uzup_A1 START %DATE% %TIME% >> %ROB%\kody.txt
call %K%\Polecenie.cmd %ODB%\narzedzia\pytest_instalacja.py --st %ST% --wynik %ROB%\t2_zrodlo_kodu_1.txt -- %ST%\testy\test_aplikacja.py -q -s -p no:cacheprovider --rootdir %ST% -k "test_skany_odniesienia_przez_cala_aplikacje_w_petli_qt or test_f_petla_qt_bez_przerw_podczas_analizy_10_plytek" > %ROB%\t2_petla.log 2>&1 < NUL
echo uzup_A1 test_aplikacja.py KOD=%ERRORLEVEL% %DATE% %TIME% >> %ROB%\kody.txt
call %K%\Polecenie.cmd %ODB%\narzedzia\pytest_instalacja.py --st %ST% --wynik %ROB%\t2_zrodlo_kodu_2.txt -- %ST%\testy\test_ui_wieczor.py -q -s -p no:cacheprovider --rootdir %ST% -k "test_6_petla_okna_bez_przerw_10_plytek_po_19_prac" >> %ROB%\t2_petla.log 2>&1 < NUL
echo uzup_A2 test_ui_wieczor.py KOD=%ERRORLEVEL% %DATE% %TIME% >> %ROB%\kody.txt
echo uzup_B1 START %DATE% %TIME% >> %ROB%\kody.txt
call %K%\Polecenie.cmd -m pytest %ST%\testy\test_aplikacja.py -q -s -p no:cacheprovider --rootdir %ST% -k "test_skany_odniesienia_przez_cala_aplikacje_w_petli_qt or test_f_petla_qt_bez_przerw_podczas_analizy_10_plytek" > %ROB%\t2_petla_plan.log 2>&1 < NUL
echo uzup_B1 test_aplikacja.py KOD=%ERRORLEVEL% %DATE% %TIME% >> %ROB%\kody.txt
call %K%\Polecenie.cmd -m pytest %ST%\testy\test_ui_wieczor.py -q -s -p no:cacheprovider --rootdir %ST% -k "test_6_petla_okna_bez_przerw_10_plytek_po_19_prac" >> %ROB%\t2_petla_plan.log 2>&1 < NUL
echo uzup_B2 test_ui_wieczor.py KOD=%ERRORLEVEL% %DATE% %TIME% >> %ROB%\kody.txt
exit /b 0
