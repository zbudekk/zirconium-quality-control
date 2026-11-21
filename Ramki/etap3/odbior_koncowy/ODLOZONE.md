# Testy i sprawy odlozone (T15, T16, T17 i otwarte 4-6 z 19.11.2026)

Paczka E3-ODB, 20.11.2026. Plan etapu 3, sekcja 7: "T15-T17 zaliczone albo jawnie odlozone z powodem brak sprzetu / danych
i z nazwanym warunkiem wznowienia". Ten plik jest takim odlozeniem. Kazda pozycja: czego brakuje, co musi sie stac, zeby
wznowic, co jest juz gotowe i od czego zaczac. Napisane dla wlasciciela - prostym jezykiem.

Stan "gotowe po stronie programu" opisuje `main` po scaleniu paczek A11s, A11i, A11w, P14, A11d; koordynator potwierdza
go w `RAPORT.md` po testach T0-T13.

## T15 - Ramki na prawdziwym sprzecie

**Kryterium (plan):** PR 9 kroki 11-14 + T5 na prawdziwych ramkach - odczyt plytki 100 % ponizej 100 ms; 8 h bez
restartu; start ponizej 60 s.

| | |
|---|---|
| Powod odlozenia | brak sprzetu: nie ma zlozonej ramki wieczornej ani porannej (Raspberry Pi, matryca diod, czujniki Halla, klawiatura, wkladka, plytki z magnesami). Czesci drukowane dopiero zamawiane (pakiety R59 i R58 z 19.11) |
| Czego dokladnie brakuje | 2 zlozone ramki wg dokumentu "Budowa ramki - decyzje i zamienniki"; plytki z magnesami (kazdy uklad, ktory bedzie w uzyciu); siec lokalna albo hotspot, w ktorej laptop widzi obie ramki |
| Warunek wznowienia | wlasciciel zglasza: "[cytat usuniety]" (wystarczy jedna ramka, zeby zaczac paczki C1 i C2) |
| Co jest gotowe | program ramki (`Ramki/stanowisko/ramka/`, opis `ramka/README.md`) sprawdzony na atrapie sprzetu; strona laptopa (`indicate.py`); test T5 na atrapie (wynik w `RAPORT.md`): 5 z 5 potwierdzen, plan po restarcie, Spacja; raporty `E3-A8-ramka`, `E3-A8i`, `E3-A8p`, `E3-A12` |
| Czego program jeszcze nie umie | kalibracja gniazdo -> diody na prawdziwej matrycy (paczka C2); program nie zna plytek okraglych ramkowych n1-n6 z R58 (otwarte po R58 nr 1) - osobna paczka programu przed T15, jesli ramki beda okragle |
| Pierwszy krok po wznowieniu | paczka C1: uruchomic `python -m ramka --rola W --sprzet rpi` na Raspberry Pi i powtorzyc testy A8 na sprzecie (kazdy klawisz, odczyt plytki, start po wlaczeniu pradu); potem C2 (kalibracja), C3 = T15 |

## T16 - Prawdziwy skaner

**Kryterium (plan):** PW "Uruchomienie" kroki 1-2 - skan testowej plytki laduje w folderze i program go rozpoznaje;
trafnosc na 40 pracach co najmniej 85 %; z 10 znanych ubytkow co najmniej 8.

| | |
|---|---|
| Powod odlozenia | brak sprzetu i danych: skaner nie stoi przy stanowisku z naszym programem; nie ma ani jednego prawdziwego skanu plytki z pracami - wszystkie pomiary etapu 3 sa na skanach sztucznych |
| Czego dokladnie brakuje | (1) skaner z programem skanera na laptopie stanowiska i potwierdzony folder eksportu; (2) plytki fizyczne (stare R54 albo nowe R59 / okragle); (3) 40 prac z projektami STL i wspolczynnikami; (4) 10 prac ze znanymi ubytkami (opisane, gdzie i jak duze) |
| Warunek wznowienia | wlasciciel wykonuje "Dzien skanera" (karta `Ramki/dzien_skanera_karta_2026-11-16.md`, program `uruchom_dzien_skanera.bat`) i przekazuje folder skanow razem z projektami tych prac |
| Co jest gotowe | obserwator folderu skanera i symulator skanera (`narzedzia/symulator_skanera.py`); program "Dzien skanera"; rozpoznawanie ukladu plytki bez wybierania; regresja na 40 skanach sztucznych (T10) i stare plytki (T11) - wyniki w `RAPORT.md`; proba "Spacja uruchamia skan" czeka na prawdziwy program skanera (paczka B2) |
| Pierwszy krok po wznowieniu | paczka B1 (pierwsze dane: szum, 3 stozki, pokrycie, czas), potem B2 (30 kolejnych skanow: 30 zdarzen, 0 zgubionych) i B3 (progi i trafnosc na 40 pracach) |

## T17 - Excel i MillBox na prawdziwych danych

**Kryterium (plan):** D1 i D2 - 10 z 10 raportow; 50 z 50 kuwet.

| | |
|---|---|
| Powod odlozenia | brak danych: nie mamy 10 prawdziwych raportow MillBox ani kopii firmowego pliku Excela z historia kuwet; nie bylo proby na prawdziwym programie Excel (sterowanie przez COM wymaga zwyklej sesji przy ekranie) |
| Czego dokladnie brakuje | (1) 10 raportow MillBox (HTML albo PDF) skopiowanych na PC poza repozytorium; (2) kopia pliku produkcyjnego Excela (nie oryginal) i lista 50 kuwet z historii z wlasciwymi wierszami; (3) komputer z Excelem i zalogowana osoba przy ekranie; (4) decyzja o kolorach pola B (otwarta u wlasciciela od 19.11) |
| Warunek wznowienia | wlasciciel kopiuje raporty i kopie pliku do katalogu poza repo (np. `<PC-katalog>\d1`, `<PC-katalog>\d2`) i mowi, kto usiadzie przy Excelu na ok. 1 godzine |
| Co jest gotowe | modul Excela w trybie "pytaj" i "cien" sprawdzony na sztucznym arkuszu 30 tys. wierszy (T6: 200 z 200, 0 zlych wierszy); wspolczynniki z pliku CSV i wpis reczny (paczka A4); log Excela wg reguly 6. Parser raportow MillBox (`millbox.py`) NIE istnieje - to paczka D1 |
| Pierwszy krok po wznowieniu | D2: uruchomic program w trybie "cien" na kopii pliku (nic nie zapisuje, tylko loguje, co by zrobil) i porownac 50 kuwet z lista; D1: napisac parser na 10 raportach, w testach tylko wersje zanonimizowane |

## Otwarte 4-6 z 19.11.2026 - laptop stanowiska (plan: paczka D4)

Wspolny powod: **brak sprzetu - laptop stanowiska nie byl dostepny**; wszystkie pomiary sa z PC wlasciciela. Wspolny
warunek wznowienia: laptop firmowy z Pythonem 3.12 (instrukcja wskazuje 3.12.10), paczka wydania na pendrivie, 1-2
godziny przy laptopie. Pierwszy krok wspolny: instalacja wg `Ramki/stanowisko/instrukcje/instalacja_i_aktualizacja.md`
i `Samokontrola.cmd` (= T0 na laptopie), potem T2 i T3 na laptopie.

| Nr | Sprawa | Czego brakuje | Co jest gotowe | Pierwszy krok na laptopie |
|---|---|---|---|---|
| 4 | Zapis do bazy w watku okna moze zatrzymac okno na ponad 200 ms przy wolnym dysku | pomiar na dysku laptopa (na PC: najdluzszy zapis 226 ms w 1500 probach, raport `E3-T0p`) | testy petli okna z progiem 200 ms; narzedzie pomiaru `testy/pomiar_czasu.py` | uruchomic testy `test_aplikacja.py -k test_f` i `test_ui_wieczor.py -k test_6` interpreterem z instalacji; wynik powyzej 200 ms = paczka poprawki (zapis poza watkiem okna) |
| 5 | Zjawisko PC: proces analizy ginie z kodem 0xC0000142 (znika uchwyt `\KnownDlls`); podejrzane programy ochronne na PC | sprawdzenie, czy wystepuje na laptopie | program wykrywa nieudany start procesu analizy i ponawia; czujka w logu (paczki A2p, A5i); srodowisko wersji bez zapytan WMI (A11w) | po T2 na laptopie policzyc w `dane\logi\stanowisko.log` wiersze "KnownDlls" i "proces silnika" (ma byc 0) |
| 6 | Strojenie stalej `RATUNEK_PLYTKA_MAX` (60 dopasowan ratunkowych na plytke) | czas analizy plytki na laptopie (wolniejszy procesor) | wartosc 60 dobrana na PC (paczka A5); wynik deterministyczny | zmierzyc T4 na laptopie; plytka powyzej 40 s = zmniejszyc stala osobna paczka (plik `match.py` jest nietykalny bez zgody) |

Do tej samej wizyty przy laptopie naleza: uprawnienia i program antywirusowy (czy pozwala uruchomic `zainstaluj.cmd`),
skalowanie ekranu 1920 x 1080 (100 / 125 / 150 %), folder OneDrive "Cyrkon" zsynchronizowany lokalnie, proba T14 na
prawdziwym stanowisku (plan: przed praca produkcyjna).

## Inne sprawy czekajace na wlasciciela (nie blokuja konca etapu 3)

- Proba T14 (czlowiek): `T14/README.md`.
- Tabela `testy_wykrywalnosci` (metryka M2) - wymaga zmiany schematu bazy; decyzja wlasciciela.
- Waxup w folderze zlecenia = punkt? Wygasanie listy brakow. Kolory pola B w Excelu. Uwagi do pokazu G2.
- Pole skanowania o srednicy 100 mm niezmierzone (R58); pokrywka okragla - 1 sztuka probna przed seria.
