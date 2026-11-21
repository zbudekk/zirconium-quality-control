# T8 - liczenie reczne metryk (21.11.2026, 04:42-04:50)

Zrodla: zapytania `PY -I <ODB>\narzedzia\sql_odczyt.py --baza <kopia> "<SELECT>"` (pelne teksty i wyniki: `t8_sql_t2.log` -
23 zapytania, `t8_sql_t3.log` - 26 zapytan; 48 z kodem 0, 1 odrzucone przez narzedzie - opis w WYNIK.md), pliki wyniku
sterownikow (`...\odbior\T2\t2_wynik.txt`, `...\odbior\T3\WYNIK.md`). Definicje: `opisy_modulow/metryki.md` (tabela
"Definicje"), klasy prac porannych i "skan aktywny": `opisy_modulow/session.md`. Kodu `metryki.py` nie czytano.
Oznaczenia: Q-T2 / Q-T3 = zapytanie w odpowiednim logu (szukaj po przytoczonym poczatku). "Wariant planu" = wzor skrocony
z tabeli "Liczenie reczne" w PLAN_TESTOW.md T8, gdy rozni sie od definicji z `metryki.md`.

## A. Baza T2 (wieczor; kopia robocze\baza_t2.sqlite; raport: tryb wieczor, okres 2026-11-20 .. 2026-11-21)

Dane surowe: skany 9, wszystkie tryb `wieczor` (id 1-9): `przyjety` 6 (id 1, 2, 3, 4, 7, 9), `do_powtorzenia` 1 (id 5),
`niezgodny_uklad` 1 (id 6, 0 prac), `plytka_nie_z_trybu` 1 (id 8). Prace skanow przyjetych: 9 + 9 + 9 + 11 + 9 + 10 = 57
(czerwone 2+1+2+1+1+3 = 10, zolte 4+2+1+3+2+3 = 15, zielone 32). Decyzje (29): `ukruszona` 10, `ukruszona_niewykryta` 15,
`numer_plytki` 4; ZADNEJ decyzji "OK" ani cofniecia. Zdarzenia (36): scanner/nowy_skan 9 (zastany: false 9 z 9),
scanner/plik_odrzucony 1, silnik/skan_przyjety 9, system/konflikt_projektu 5, system/podglad 8, system/program_start 1,
system/program_stop 1, ui/ponowny_skan_odrzucony 2 (skan 7 wobec 5; skan 9 wobec 4). Tabele `projekty` i `zlecenia`:
po 0 wierszy; `sesje_pieca`: 0.

### A1. Wiersze tabeli metryk (6 wierszy raportu: 5 z wartoscia + M2 bez wartosci)

| Nr | Metryka (klucz) | Raport | Recznie (wg metryki.md) | Zrodlo | Zgodne |
|---|---|---|---|---|---|
| 1 | falszywe_alarmy | 0,0 %; 0 / 57 | licznik: czerwone z obowiazujaca decyzja "OK" = 0 (decyzji "OK" w bazie 0; 10 czerwonych ma po 1 decyzji `ukruszona`); mianownik: wszystkie prace skanow przyjetych = 57 (skan 5 `do_powtorzenia` poza; obie pary "ponowny skan?" odrzucone = licza sie oba skany: 4 i 9 sa w mianowniku, 5 i tak poza); 0 / 57 = 0,0 % | Q-T2 "SELECT s.id AS skan, s.status, count(p.id)..."; "SELECT p.status_gniazda, coalesce(...ostatnia_decyzja..."; zdarzenia ui | TAK |
| 2 | nieznane_wieczor | 100,0 %; 57 / 57 | regula 3-czlonowa: (a) brak 1. kandydata: 0 z 57; (b) 1. kandydat ponizej 0,6: 0 z 57 (minimum 0,8867); (c) zaden z 2 kandydatow w indeksie: 57 z 57, bo `projekty` ma 0 wierszy; razem 57 / 57 = 100,0 % | Q-T2 "SELECT count(*) AS prac, sum(p.kandydat1_sha16 IS NULL..."; "SELECT count(*) FROM projekty" | TAK (wg metryki.md); wariant planu (tylko a + b): 0 / 57 = 0,0 % - NIE zgadza sie z raportem (p. sekcja C) |
| 3 | czas_wieczor | 9,3 min (JSON 9.3) | chwile aktywnosci: czas_analizy 9 skanow (04:18:39-04:27:15), decyzje 29 (04:18:39-04:27:17), ui 2 (04:25:15, 04:27:15), scanner/nowy_skan 9 nie-zastanych (04:17:59-04:27:01); razem 49 chwil, najdluzsza przerwa 95 s (< 10 min) = 1 posiedzenie 04:17:59 -> 04:27:17 = 558 s = 9,300 min; 1 zmiana (doba 2026-11-20, zmiana od 22:00); srednia 9,300 | Q-T2 "WITH ch(t) AS ..." | TAK (roznica 0,000 min) |
| 4 | powtorzone_wieczor | 33,3 %; 3 / 9 (JSON 0.3333333333333333) | zastapiony 0 + do_powtorzenia 1 + niezgodny_uklad 1 + plytka_nie_z_trybu 1 + blad 0 = 3; skany 9; 3 / 9 = 0,33333 | Q-T2 "SELECT status, tryb, count(*) FROM skany..." | TAK (roznica 0) |
| 5 | dni_bez_awarii | 1 dni; ocena "za krotki okres" | doby z wpisami dziennika: 1 (2026-11-20, 36 wpisow); program_start 1, po nim program_stop 1 (ostatni wpis) = 0 awarii; silnik_nie_startuje 0; seria do konca okresu 1; seria < 5 bez awarii w historii i dni pracy < 5 = "za krotki okres" | Q-T2 "SELECT strftime('%Y-%m-%d', czas, '-6 hours')..."; "SELECT zrodlo, typ, count(*)..." | TAK |
| 6 | m2 | bez wartosci ("wymaga zmiany schematu") | tabeli `testy_wykrywalnosci` w bazie nie ma (lista tabel: 11) - nie ma czego liczyc | Q-T2 "SELECT type, name, tbl_name FROM sqlite_master" | nie dotyczy (wiersz bez wartosci; poza licznikiem) |

Wynik A1: **5 z 5 metryk z wartoscia zgodnych** (wartosc, licznik i mianownik), 0 rozbieznosci, 0 NIE ZMIERZONO.

### A2. Wartosci informacyjne strony / JSON (27 pozycji)

| Pole JSON | Raport | Recznie | Zgodne |
|---|---|---|---|
| wieczor.skany | 9 | 9 wierszy `skany` w okresie | TAK |
| wieczor.skany_aktywne | 7 | 9 - nieaktywne (niezgodny_uklad 1, plytka_nie_z_trybu 1; zastapiony 0, blad 0) = 7 | TAK |
| wieczor.skany_mianownik | 6 | przyjete 6 | TAK |
| wieczor.skany_do_powtorzenia | 1 | 1 (id 5) | TAK |
| wieczor.skany_do_potwierdzenia | 0 | pytan "ponowny skan?" 2 (plik sterownika T2), oba z odpowiedzia "to nowy wsad" (2 zdarzenia ui) - bez odpowiedzi 0 | TAK |
| wieczor.ponowny_skan_odrzucony | 2 | ui/ponowny_skan_odrzucony: 2 | TAK |
| wieczor.prace | 57 | 57 | TAK |
| wieczor.czerwone | 10 | 10 | TAK |
| wieczor.czerwone_ukruszone | 10 | czerwone z decyzja `ukruszona`: 10 | TAK |
| wieczor.czerwone_bez_decyzji | 0 | 0 | TAK |
| wieczor.niewykryte_cien | 15 | decyzje `ukruszona_niewykryta` na pracach nieczerwonych: 15 (wszystkie na ZOLTYCH) | TAK |
| wieczor.wykrywalnosc_cien | 0,4 (10/25) | 10 / (10 + 15) = 0,400 | TAK |
| wieczor.dwuznaczne | 0 | prace szare: 0 | TAK |
| wieczor.powtorzone.statusy | do_powt. 1, niezgodny 1, nie z trybu 1 | 1 / 1 / 1 | TAK |
| wieczor.czas.posiedzen | 1 | 1 | TAK |
| wieczor.czas.posiedzen_bez_startu | 1 | zdarzen ui/start_skanu: 0 = 1 posiedzenie bez startu | TAK |
| wieczor.czas.zmian | 1 | 1 | TAK |
| wieczor.czas.zmian_bez_danych | 0 | 0 | TAK |
| wieczor.czas.suma_min | 9,3 | 9,300 | TAK |
| wieczor.czas.max_min | 9,3 | 9,300 | TAK |
| wieczor.czas.zmian_ponad_prog | 0 | 0 (9,3 < 20) | TAK |
| stabilnosc.dni_pracy | 1 | 1 | TAK |
| stabilnosc.dni_historii | 1 | 1 | TAK |
| stabilnosc.awarie / dni_z_awaria / restart_bez_zamkniecia / awarie_w_historii | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | TAK |
| stabilnosc.silnik_nie_startuje / silnik_wrocil_sam | 0 / 0 | zdarzen `silnik_nie_startuje`: 0 | TAK |
| stabilnosc.najdluzsza_seria / obecna_seria | 1 / 1 | 1 / 1 | TAK |
| stabilnosc.uruchomiony_na_koniec | false | ostatni wpis dziennika = program_stop | TAK |

Wynik A2: 27 z 27 zgodnych.

### A3. Praca z ubytkiem niezgloszona przez program (skan sha16 247ee785f428396f = id 7, gniazdo 4) - co liczy raport

- W bazie: praca id 50 (skan 7, gniazdo 4): `status_gniazda` zielony, `status_inspekcji` ok, `ubytki` 0, decyzji 0.
- Raport NIE zna prawdy scenariusza. Liczy wylacznie ocene programu wobec decyzji technika:
  "czerwone 10: OK 0, Ukruszona 10"; "ukruszone, ktorych program nie wskazal 15" = 15 prac ZOLTYCH kliknietych
  "Ukruszona" (rodzaj `ukruszona_niewykryta`); "wykrywalnosc wzgledem technika 40,0 % (10/25)".
- Praca przeoczona nie wystepuje w zadnym liczniku raportu (technik - sterownik - jej nie kliknal, bo byla zielona).
- Wobec prawdy (plik sterownika T2, poza raportem): prace z ubytkiem 26 = czerwone 10 + zolte 15 + zielone 1; "pokazane
  czerwono albo zolto" 25 z 26; "pokazane czerwono" 10 z 26; cale na czerwono 0 z 31. Zadna z tych liczb nie jest
  wartoscia raportu: 40,0 % (10/25) to inna wielkosc (czerwone wsrod prac oznaczonych przez technika; zolte licza sie
  jako "program nie wskazal") - zgodna z definicja z metryki.md ("NIE zastepuje M2").

## B. Baza T3 (SE10; kopia robocze\baza_t3.sqlite; raport: tryb oba, okres 2026-11-17 .. 2026-11-19)

Dane surowe: skany 9: wieczor `przyjety` 3 (id 1, 2, 8), rano `przyjety` 5 (id 3, 5, 6, 7, 9), rano `zastapiony` 1
(id 4, zastapiony przez 5). Piece 3, wszystkie zamkniete, daty 18.11 (2) i 19.11 (1). Prace 19: wieczor 8 (5 + 2 + 1),
rano w skanach aktywnych 9 (id 8, 9, 10, 13, 14, 15, 16, 18, 19), w skanie zastapionym 2 (id 11, 12 - poza).
Decyzje 6. Zdarzenia 27. `projekty` 9 wierszy (9 roznych sha16, usunietych 0), `zlecenia` 5 (5 roznych kuwet).

Prace poranne (Q-T3 "SELECT p.id, p.skan_id, p.status_gniazda, p.kandydat1_pokrycie..." i pelna lista prac):

| Praca | Skan / piec | 1. kandydat | Projekt | Decyzja | Klasa (session.md) | Propozycja programu | Top-1 |
|---|---|---|---|---|---|---|---|
| 8 | 3 / 1 | 0,95 | tak | - | pewna | tak | trafienie |
| 9 | 3 / 1 | 0,94 | tak | - | pewna | tak | trafienie |
| 10 | 3 / 1 | 0,96 | tak | - | pewna | tak | trafienie |
| 13 | 5 / 1 | 0,90 | tak | - | pewna | tak | trafienie |
| 14 | 5 / 1 | 0,45 (< 0,6) | tak | przypisanie_reczne (projekt = 1. kandydat) | przypisana | NIE = nieznana wg metryki | poza mianownikiem |
| 15 | 6 / 2 | 0,93 | tak | - | pewna | tak | trafienie |
| 16 | 7 / 2 | 0,91 | brak | przypisanie_reczne bez projektu ("bez projektu") | nieznana | tak - odrzucona | chybienie |
| 18 | 9 / 3 | 0,95 | tak | - | pewna | tak | trafienie |
| 19 | 9 / 3 | 0,94 | tak (projekt rozpoznany juz w piecu 1) | - | poprawka | tak | trafienie |

### B1. Wiersze tabeli metryk (10 wierszy raportu: 9 z wartoscia + M2 bez wartosci)

| Nr | Metryka (klucz) | Raport | Recznie (wg metryki.md) | Zrodlo | Zgodne |
|---|---|---|---|---|---|
| 1 | falszywe_alarmy | 0,0 %; 0 / 8 | czerwone 1 (praca 3), decyzja `ukruszona` = falszywych 0; prace skanow wieczornych przyjetych 5 + 2 + 1 = 8; 0 / 8 | Q-T3 lista prac, lista decyzji | TAK |
| 2 | top1 | 87,5 %; 7 / 8 | mianownik: prace z propozycja programu i projektem 7 (8, 9, 10, 13, 15, 18, 19) + odrzucona "bez projektu" 1 (16) = 8; praca 14 poza (bez propozycji); licznik: projekt = 1. kandydat: 7; 7 / 8 = 0,875 | Q-T3 "SELECT count(DISTINCT p.id) FROM prace p JOIN projekty pr ON pr.id=p.projekt_id WHERE ... AND pr.sha16=p.kandydat1_sha16" (7); to samo bez warunku sha16 (7) | TAK (roznica 0) |
| 3 | top2 | 87,5 %; 7 / 8 | kuweta projektu pracy = kuweta projektu 1. albo 2. kandydata: 7 (praca 16 bez projektu = chybienie); 7 / 8 | Q-T3 "... JOIN zlecenia z ... JOIN zlecenia zk ... AND zk.kuweta=z.kuweta" (7) | TAK |
| 4 | nieznane_wieczor | 0,0 %; 0 / 8 | 8 prac wieczornych: 1. kandydat jest, pokrycie 0,91-0,95, wszystkie w indeksie (8 z 8) = 0 nieznanych; 0 / 8 | Q-T3 "... k.sha16=p.kandydat1_sha16 WHERE p.skan_id IN (1,2,8) AND p.kandydat1_pokrycie>=0.6" (8) | TAK |
| 5 | nieznane_rano | 11,1 %; 1 / 9 (JSON 0.1111111111111111) | 9 prac zamknietych piecow; bez propozycji: praca 14 (1. kandydat 0,45 < 0,6) = 1; praca 16 ("bez projektu" po propozycji) nie jest nieznana; 1 / 9 = 0,11111 | Q-T3 "... WHERE p.skan_id IN (3,5,6,7,9) AND p.kandydat1_pokrycie>=0.6" (8 z 9 w indeksie i ponad progiem) | TAK (roznica 0) |
| 6 | czas_wieczor | 1,0 min (JSON 0.9833333333333333) | chwile trybu wieczor: 17.11 19:00:00, 19:20:00, 19:30:02 (decyzja), 18.11 19:59:01 (ui/tryb_zmieniony, najblizszy skan = wieczorny 20:00:00), 20:00:00; przerwy 1200 s, 602 s, 88139 s, 59 s = 4 posiedzenia, mierzalne 1: 59 s = 0,98333 min; zmiany 2 (17.11 zm. 2 - same pojedyncze chwile = bez danych; 18.11 zm. 2 = 0,98333); srednia ze zmian z czasem = 0,98333 | Q-T3 "WITH ch(t) AS (SELECT czas_analizy FROM skany WHERE tryb='wieczor'..." | TAK (roznica 0,00000 min; strona zaokragla do 1,0) |
| 7 | powtorzone_wieczor | 0,0 %; 0 / 3 | 3 skany wieczorne, wszystkie `przyjety`; 0 / 3 | Q-T3 "SELECT status, tryb, count(*)..." | TAK |
| 8 | powtorzone_rano | 16,7 %; 1 / 6 (JSON 0.16666666666666666) | skany zamknietych piecow: 6 (id 3, 4, 5, 6, 7, 9); `zastapiony` 1 (id 4); 1 / 6 = 0,16667 | Q-T3 lista skanow | TAK (roznica 0) |
| 9 | dni_bez_awarii | 3 dni; "za krotki okres" | doby z wpisami: 3 (17.11: 3 wpisy, 18.11: 14, 19.11: 10); program_start 4 (id 1, 11, 22, 26), przed kazdym kolejnym startem jest program_stop (id 10, 21, 25), ostatni wpis = program_stop (id 27) = 0 awarii; seria 3 | Q-T3 lista zdarzen; "SELECT strftime(...)" | TAK |
| 10 | m2 | bez wartosci | tabeli testow w bazie nie ma | - | nie dotyczy (poza licznikiem) |

Wynik B1: **9 z 9 metryk z wartoscia zgodnych**, 0 rozbieznosci, 0 NIE ZMIERZONO. Zakres wymagany planem dla SE10
(top-1, top-2, nieznane rano): 3 z 3.

Uwaga do nr 5: liczby "klasy: nieznana 1" (praca 16, klasa sesji) i "prace nieznane 1 / 9" (praca 14, regula metryki)
dotycza ROZNYCH prac, a sa rowne - sama liczba 1 / 9 nie rozstrzyga, ktora prace policzyl raport. Rozstrzyga top-1:
mianownik 8 z "odrzucone 1" jest mozliwy tylko wtedy, gdy praca 16 jest chybieniem top-1, a praca 14 jest poza top-1
(metryki rozlaczne) - czyli nieznana = praca 14, jak w definicji.

### B2. Wartosci informacyjne strony / JSON (45 pozycji)

| Pole JSON | Raport | Recznie | Zgodne |
|---|---|---|---|
| wieczor.skany / skany_aktywne / skany_mianownik | 3 / 3 / 3 | 3 / 3 / 3 | TAK (3 pozycje) |
| wieczor.skany_do_powtorzenia / skany_do_potwierdzenia / ponowny_skan_odrzucony | 0 / 0 / 0 | 0 / 0 / 0 (ta sama plytka nr 2 w dwoch roznych dobach - bez pary) | TAK (3) |
| wieczor.prace / czerwone / czerwone_ukruszone / czerwone_bez_decyzji | 8 / 1 / 1 / 0 | 8 / 1 / 1 / 0 | TAK (4) |
| wieczor.niewykryte_cien / wykrywalnosc_cien / dwuznaczne | 0 / 1,0 (1/1) / 0 | 0 / 1 z 1 / 0 | TAK (3) |
| wieczor.powtorzone.statusy | puste | brak statusow powtorzenia | TAK (1) |
| wieczor.czas: posiedzen / bez_startu / zmian / zmian_bez_danych | 4 / 4 / 2 / 1 | 4 / 4 (start_skanu: 0) / 2 / 1 | TAK (4) |
| wieczor.czas: suma_min / max_min / zmian_ponad_prog | 0,98333 / 0,98333 / 0 | 0,98333 / 0,98333 / 0 | TAK (3) |
| rano.piece / piece_otwarte / prace | 3 / 0 / 9 | 3 / 0 / 9 | TAK (3) |
| rano.klasy | pewna 6, przypisana 1, nieznana 1, poprawka 1 | 6 (8, 9, 10, 13, 15, 18) / 1 (14) / 1 (16) / 1 (19; zdarzen `poprawka_rano`: 1) | TAK (1) |
| rano.z_prawda / top2_projekt / odrzucone / dwuznaczne | 8 / 7 / 1 / 0 | 8 / 7 (projekt wsrod 2 kandydatow: 7) / 1 / 0 | TAK (4) |
| rano.powtorzone.statusy | zastapiony 1 | 1 | TAK (1) |
| rano.czas: posiedzen / bez_startu / zmian / zmian_bez_danych | 5 / 5 / 2 / 0 | 5 (granice: przerwy 956 s, 7199 s, 76440 s, 1202 s) / 5 / 2 / 0 | TAK (4) |
| rano.czas: suma_min / srednio_min / max_min | 31,0667 / 15,5333 / 30,0833 | 904 s + 0 + 901 s + 59 s + 0 = 1864 s = 31,0667; / 2 zmiany = 15,5333; zmiana 18.11: 1805 s = 30,0833 | TAK (3; roznice 0,0000) |
| rano.czas_pieca_min: mediana / max | 20,0333 / 30,0167 | piece: 901 s, 1202 s, 1801 s = 15,0167 / 20,0333 / 30,0167 min; mediana 20,0333, max 30,0167 | TAK (2) |
| stabilnosc: dni_pracy / dni_historii / awarie (4 pola) / silnik (2 pola) / serie (2 pola) / uruchomiony_na_koniec | 3 / 3 / 0 / 0 / 3 i 3 / false | 3 / 3 / 0 / 0 / 3 i 3 / ostatni wpis = program_stop | TAK (6) |

Wynik B2: 45 z 45 zgodnych.

## C. Wzory skrocone z tabeli "Liczenie reczne" PLAN_TESTOW.md wobec definicji z metryki.md (do decyzji)

Raport zgadza sie z definicjami `metryki.md` (wyzej). Tabela skrocona w planie testow daje INNE liczby w 3 miejscach:

| Metryka | Baza | Wzor skrocony planu | Wynik wzoru planu | Raport (= metryki.md) |
|---|---|---|---|---|
| falszywe alarmy - mianownik | T2 | "/ wszystkie takie prace czerwone z decyzja" | 0 / 10 (0,0 %) | 0 / 57 (0,0 %) |
| falszywe alarmy - mianownik | T3 | jw. | 0 / 1 (0,0 %) | 0 / 8 (0,0 %) |
| prace nieznane wieczor | T2 | "pusty kandydat1_sha16 albo pokrycie < 0,6" (bez czlonu "zaden kandydat w indeksie") | 0 / 57 (0,0 %) | 57 / 57 (100,0 %) |
| top-1 / top-2 | T3 | "kandydat1_sha16 = sha16 projektu potwierdzonego / prace rozstrzygniete" (bez wylaczenia pracy bez propozycji i bez chybienia "bez projektu") | 8 / 8 (prace z projektem; praca 14 trafiona, 16 poza) | 7 / 8 |

Fakt do oceny wlasciciela (nie rozbieznosc liczb): na bazie T2 metryka "prace nieznane - wieczor" = 100 % (PONIZEJ
progu 10 %) wynika WYLACZNIE z pustego indeksu projektow w bazie (tabele `projekty` i `zlecenia`: 0 wierszy, choc
folder projektow przebiegu T2 mial 15 folderow) - program dopasowal wszystkie 57 prac (pokrycie 1. kandydata >= 0,8867).
