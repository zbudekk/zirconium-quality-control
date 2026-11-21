# T5 czesc B - atrapa ramki na adresie sieci lokalnej PC + zapis ruchu (odbior 21.11.2026, pierwsze wykonanie)

## Adres i porty

- Adres sieci lokalnej PC (`ipconfig`): karta Ethernet **<adres-IP>** (ta sama karta ma tez <adres-IP>; inne karty:
  Tailscale 100.77.167.23, Ethernet 2 <adres-IP>; Wi-Fi rozlaczone). Uzyto <adres-IP>.
- Atrapa ramki W: nasluch <adres-IP>:8765. Atrapa ramki P: nasluch <adres-IP>:8767.
- Posrednik ramki W: nasluch <adres-IP>:8766 -> cel <adres-IP>:8765, zapis `<ROB>\ruch_ramka_w.bin`.
- Posrednik ramki P: nasluch **127.0.0.1:8766** -> cel <adres-IP>:8767, zapis `<ROB>\ruch_ramka_p.bin` (wg kroku 3 planu:
  `[ramki] port` jest jeden dla obu ramek, wiec posrednik P slucha na tym samym porcie pod innym adresem; port 8768 z kroku 2
  planu NIE zostal uzyty).
- Kopia ustawien `<ROB>\ustawienia.toml` (z `<K>\ustawienia.toml`, rozni sie 3 wierszami `[ramki]`): `port = 8766`,
  `wieczorna_host = "<adres-IP>"`, `poranna_host = "127.0.0.1"`; `klucz` pusty. Plik `<K>\ustawienia.toml` NIE zmieniony
  (SHA-256 przed i po: 4303ec76c74fb4a2925fa93056a3bf8b58639119117554795cd30b143e144e4d).
- Zapora Windows: nasluch pod adresem karty udal sie bez pytania i bez odmowy (4 gniazda `LISTENING` w `netstat`);
  polaczenia byly z tego samego komputera - czy zapora wpusci INNY komputer, tego ta proba nie mierzy.
- To nadal jeden komputer: ruch idzie przez stos sieciowy (adres karty), nie przez kabel ani Wi-Fi (O8). Prawdziwa siec = T15.

## Przebieg (godziny z logow)

| Godzina | Krok | Co |
|---|---|---|
| 02:59:30 | B3 | kopia ustawien z 3 zmienionymi wierszami `[ramki]` (zrobiona przed startem atrap) |
| 03:00:13 | B1 | atrapa W: `ramka W (program 0.1.3) slucha na <adres-IP>:8765, start_id 837fac54`; `ATRAPA_RAMKI port=8765 ... rola=W` |
| 03:00:15 | B1 | atrapa P: `ramka P (program 0.1.3) slucha na <adres-IP>:8767, start_id b25bb967`; `ATRAPA_RAMKI port=8767 ... rola=P` |
| 03:00:21 | B1 | konsola obu atrap: `stan` -> tryb `gotowa`, plytka 0, bez planu, `wlasciciel` false |
| 03:00:33 | B2 | 2 posredniki: `POSREDNIK port=8766 cel=<adres-IP>:8765 ...` i `POSREDNIK port=8766 cel=<adres-IP>:8767 ...` |
| 03:01:18 | B4 | start sterownika T2 (`ciezki.ps1 -Tor 3 -Kto odb-T5`, plik `krok_t5_b4.cmd`) |
| 03:01:23 | B4 | ramka W: `lacznosc` true (program polaczyl sie przez posrednik) |
| 03:01:25 | B4 | skan 1: `PUT /tryb` x 2 (`skanowanie`, `analiza`) -> stan ramki `analiza`, `wlasciciel` true |
| 03:02:18,96-19,52 | B4 | wynik skanu 1: `PUT /tryb` (`gotowa`; wg kodu programu: wynik jeszcze bez numeru plytki - program pyta technika o numer) + `PUT /plan` x 5 (wersje 1-5, plytka 1; pierwszy plan 21 ms po `gotowa`) -> stan `wynik`, `plytki_planu [1]` |
| 03:02:21 | B4 | konsola W: `plytka 1`; `stan`: plytka 1, plan wazny (wersja 5, `plan_pozostalo_s` 29,0 z 30), tryb `wynik` |
| 03:02:23 | B4 | konsola W: `klawisz enter`; `stan`: bez zmiany (nr zdarzenia 10 -> 10; ramka W nie ma klawiszy - zgodnie z planem) |
| 03:02:25,53 | B4 | skan 2: `PUT /tryb` x 2 -> stan `analiza`, plan zgaszony (`plan_id` null) |
| 03:02:51,36-52,59 | B4 | wynik skanu 2: `PUT /tryb` (`gotowa`) + `PUT /plan` x 2 (wersje 6-7, plytka 3) -> stan `wynik`, `plytki_planu [3]`; konsola: `plytka 3` (03:02:57), `stan`: plytka 3, plan wazny |
| 03:03:26,49 | B4 | skan 3: `PUT /tryb` x 2 -> stan `analiza`, plan zgaszony |
| 03:03:51,43-52,94 | B4 | wynik skanu 3: `PUT /tryb` (`gotowa`) + `PUT /plan` x 3 (wersje 8-10, plytka 2) -> stan `wynik`, `plytki_planu [2]`; konsola: `plytka 2` (03:03:54), `stan`: plytka 2, plan wazny |
| 03:03:55,99 | B4 | program zamykajac sie wyslal `DELETE /plan` do obu ramek -> stan `gotowa`, bez planu; 03:03:56 koniec sterownika (kod 0) |
| 03:04:27 | B4 | ramka W: `lacznosc` false, `wlasciciel` false (program zamkniety) |
| 03:04:45 | B5 | Ctrl+C do obu posrednikow - oba zakonczone, wiersze `POSREDNIK koniec` nizej |
| 03:04:57 | - | konsola obu atrap: `stan`, `koniec` -> `ATRAPA_W KOD=0`, `ATRAPA_P KOD=0` |

## Liczby z posrednikow (krok 5 planu)

- Ramka W: `POSREDNIK koniec: polaczen 57, nieudanych polaczen z celem 0, bajtow do ramki 14265, bajtow z ramki 20794`
  (N = 57 > 0 - program szedl przez posrednik; proba wazna).
- Ramka P: `POSREDNIK koniec: polaczen 20, nieudanych polaczen z celem 0, bajtow do ramki 2681, bajtow z ramki 6625` (N = 20 > 0).
- Rozbior zapisu ruchu (`t5_ruch_liczniki.txt`, same liczniki):
  - W: 56 polaczen z danymi (57. bez danych - polaczenie zerwane przy zamykaniu programu), zadania: `PUT /plan` 10,
    `PUT /tryb` 9, `GET /zdarzenia` 35, `GET /stan` 1, `DELETE /plan` 1; odpowiedzi: 55 x kod 200 (ostatnie odpytanie
    `GET /zdarzenia` przerwane zamknieciem programu - w logu atrapy 1 x "klient rozlaczyl sie przed odpowiedzia");
    naglowki zadan: `host`, `connection`, `x-laptop-id`, przy tresci `content-type`, `content-length`; naglowka klucza brak
    (klucz pusty - zgodnie z planem).
  - P: 19 polaczen z danymi, zadania: `GET /zdarzenia` 17, `GET /stan` 1, `DELETE /plan` 1; odpowiedzi 18 x 200; planu
    brak (program w trybie wieczornym; ramka P w programie z paczki bez czlowieka przy ekranie nie jest sprawdzana - plan).

## Co widziala atrapa ramki W (plan i kolory)

Log atrapy (`atrapa_w.log`): `PUT /plan -> 200` 10 razy, `PUT /tryb -> 200` 9 razy, `DELETE /plan -> 200` 1 raz; adres
klienta w logu: <adres-IP> (posrednik). Kolejnosc `PUT /tryb`: skanowanie, analiza, gotowa - 3 razy (po jednym cyklu
na skan). Plany (z zapisu ruchu; `plan_id` 2026-11-21-w-9a7168, `tryb` wieczor, `wazny_s` 30, po 9 gniazd):

| Skan (poz. scenariusza, sha16) | Plytka w planie | Wersje planu | Kolory pierwszej wersji | Kolory ekranu wg sterownika (przed kliknieciami) | Kolory ostatniej wersji (po decyzjach "Ukruszona") |
|---|---|---|---|---|---|
| 1 (df2e6a790700131d) | 1 | 1-5 | czerwony 2, zolty 4, zielony 3 | czerwone 2, zolte 4, zielone 3 | czerwony 6, zielony 3 |
| 3 (9cc2bd761deb672b) | 3 | 6-7 | czerwony 2, zolty 1, zielony 6 | czerwone 2, zolte 1, zielone 6 | czerwony 3, zielony 6 |
| 8 (247ee785f428396f) | 2 | 8-10 | czerwony 1, zolty 2, zielony 6 | czerwone 1, zolte 2, zielone 6 | czerwony 3, zielony 6 |

- Plan i kolory doszly do ramki W w **3 z 3 skanow**; liczby kolorow pierwszej wersji planu = liczby kolorow mapy
  odczytane z ekranu przez sterownik w 3 z 3 skanow (27 z 27 gniazd wg licznikow klas koloru); kazda decyzja "Ukruszona"
  (4 + 1 + 2 = 7 zmian zolty -> czerwony na pracach zoltych) dala nowa wersje planu.
- Ramka W pokazuje tylko ostatni skan: nowy skan (`PUT /tryb skanowanie`) gasi plan poprzedniego (stan `analiza`,
  `plan_id` null) - widoczne 3 z 3 razy.
- Polozenie plytki w konsoli (`plytka 1`, `plytka 3`, `plytka 2`): plan pozostal wazny (`plan_pozostalo_s` 29,0 z 30,0 s
  w 3 z 3 odczytow po polozeniu), stan `wynik`.
- Konsola: 63 x `stan`, 3 x `plytka <n>`, 1 x `klawisz enter`, 1 x `koniec` (dziennik: `t5_konsola_w.log`); polecenia
  wpisywal skrypt-"technik" (`robocze\konsola_w_petla.sh`: `stan` co ok. 3 s; gdy ramka ma plan plytki n - `plytka n`).
- Czego ta proba NIE mierzy (O8): 5 potwierdzen bez sieci, restart ramki, Spacja, ramka P z planem - tylko testy czesci A.

## Wynik sterownika T2 w tej probie (3 skany; to NIE jest wynik T2 ani kryterium T5)

`t5_wieczor.log`: kod 0; "PROBA SKROCONA"; obsluzone zgodnie z prawda 3 z 3; start analizy od zapisu 0,442 / 0,446 /
0,381 s (3 z 3 ponizej 1 s); mapa od zapisu: pierwsza plytka (pula zimna) 54,12 s, kolejne 26,26 i 25,31 s; petla okna:
najdluzsza przerwa 50,6 ms, przekroczen 200 ms 0; pytania programu: 3 x `brak_numeru_plytki` (numer podal technik);
log programu: WARNING 1 ("Brak pliku kalibracji ramek - wartosci startowe z geometrii plytek"), ERROR 0.
**Lista do dofrezowania: ROZNA** - oczekiwanych 13, w programie 12; 1 praca z ubytkiem wg prawdy pokazana na ZIELONO
(pozycja 8, sha16 247ee785f428396f); wiersz sterownika "T2 LACZNIE: FAIL (4 z 5 kryteriow ZAL, 1 FAIL)". Do wiadomosci
koordynatora przed T2 (te same skany sa w pelnym scenariuszu T2).

Co jeszcze liczylo na PC w czasie kroku B4 (03:01:18-03:03:56): T1 `krok_4.cmd` (pelny pytest, ok. 22 % o 03:00 - przed
`test_silnik.py`), T10 `krok_t10.cmd` (tor 2), T12 `krok_B_uzup.cmd` (tor 4, do 03:03:55); wolny RAM 69349 MB na starcie.

## Potkniecia pierwszego wykonania (krok po kroku)

1. Sesja wykonawcy nie ma okien. "2 okna" atrap zastapione procesami w tle: konsola atrapy czyta polecenia z potoku
   (`tail -f robocze\konsola_w.txt | cmd /c krok_t5_b1_atrapa_w.cmd`), wyjscie do `atrapa_w.log` / `atrapa_p.log`. Polecenie
   atrapy z planu bez zmian (`call <K>\Polecenie.cmd narzedzia\atrapa_ramki.py --rola W --host <adres-IP> --port 8765
   --sterowanie`; P: `--rola P ... --port 8767`), ale BEZ `< NUL` (konsola musi czytac polecenia).
2. Ctrl+C dla posrednika: proces uruchomiony w sesji bez okna dziedziczy "ignoruj Ctrl+C" - proba o 02:50 (posrednik z
   planu, port 8768, `Start-Process`): po wyslaniu zdarzenia Ctrl+C proces zyl dalej, wiersza `POSREDNIK koniec` nie bylo
   (proces zakonczony `Stop-Process`). Rozwiazanie: posrednik startuje przez `robocze\posrednik_ctrlc.py` (wlacza obsluge
   Ctrl+C w procesie i uruchamia NIEZMIENIONY `<ODB>\narzedzia\posrednik_ruchu.py` z jego opcjami), a Ctrl+C wysyla
   `robocze\ctrlc.py <pid>`. Polecenie faktyczne: `PY -I <ROB>\robocze\posrednik_ctrlc.py <ODB>\narzedzia\posrednik_ruchu.py
   --sluchaj <adres-IP>:8766 --cel <adres-IP>:8765 --zapis <ROB>\ruch_ramka_w.bin` (P: `--sluchaj 127.0.0.1:8766
   --cel <adres-IP>:8767 --zapis <ROB>\ruch_ramka_p.bin`). Proba na sucho o 02:51: kod 0 i wiersz `POSREDNIK koniec`.
3. Plan podaje dla posrednika P dwa rozne adresy nasluchu (krok 2: `<adres PC>:8768`, krok 3: `127.0.0.1:8766`) -
   dziala tylko wariant z kroku 3 (jeden `[ramki] port`); port 8768 nieuzyty.
4. Pierwsza edycja kopii ustawien (`sed -i`) zamienila konce linii CRLF na LF w calym pliku; kopia zrobiona ponownie z
   `sed -b` - rozni sie od pliku instalacji tylko 3 wierszami `[ramki]` (`diff`).
5. `t5_wieczor.log` jest pusty az do konca sterownika (sterownik wypisuje wynik na koncu) - postep widac tylko w logu atrapy.
6. `klawisz enter` na ramce W nie daje zadnego zdarzenia (ramka W nie obsluguje klawiszy) - krok planu wykonany, bez skutku.
7. Sterownik bierze `[ramki]` z pliku wzoru bez zmian; plik kalibracji ramek w katalogu roboczym sterownika nie istnieje -
   program uzyl wartosci startowych z geometrii plytek (ostrzezenie w logu), plany przeszly walidacje ramki (10 x 200).
8. Zapis ruchu W ma 57 polaczen, z czego 56 z danymi (1 puste przy zamykaniu programu).
9. Liczba procesow python wykonawcy w kroku B4: 5 (2 atrapy, 2 posredniki, sterownik z programem) + proces silnika i
   symulator sterownika - wiecej niz "2 procesy w krokach lekkich" z zasad wspolnych; wymaga tego plan (krok ciezki
   pod blokada toru 3, atrapy i posredniki to procesy bezczynne).

## Po tescie

`netstat`: 0 gniazd `LISTENING` na portach 8765-8768; `Get-Process python`: zadnego procesu tej sesji (atrapy PID 34260
i 39404, posredniki PID 29584 i 35112 - zakonczone). Zapisy `ruch_ramka_w.bin` (37 678 bajtow) i `ruch_ramka_p.bin`
(10 157 bajtow) zostaja w `<ROB>` do T9 - NIE ida do repo.
