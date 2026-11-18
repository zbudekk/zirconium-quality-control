# Raport recenzenta PR #19 - runda 1

Data: 2026-11-17. Recenzent: swieza subsesja (Fable 5.2), niezalezna od wykonawcy i koordynatora.
Stan recenzowany: HEAD `46ea1b6`, PR #19 (`e3/a8-ramka` -> `e3/fala2-baza`), zakres
`git diff origin/e3/fala2-baza...origin/e3/a8-ramka` (17 plikow, wszystkie nowe, +4 032 / -0, pod `Ramki/stanowisko/`).
Metoda: przeczytane w calosci `ramka/logika.py`, `protokol.py`, `program.py`, `serwer.py`, `sprzet.py`,
`sprzet_rpi.py`, `sprzet_atrapa.py`, `obraz.py`, `kalibracja.py`, `test_led.py`, `README.md`,
`narzedzia/atrapa_ramki.py`, raport wykonawcy; `testy/test_ramka.py` - pomocnicze, K4-K9 i sprzatanie w calosci,
reszta po nazwach i asercjach kluczowych; plan etapu 3: fakt 8, I1-I13, sekcja 3.6, 4.1 (E3-A8).
Uruchomienia (tylko PC, `<PC-katalog>\e3\r19`, wolny RAM 16 GB): 1 przebieg `testy\test_ramka.py`
(44 passed, 12,7 s) i 1 wlasny skrypt `scen_r19.py` (12 scenariuszy S1-S12 na `LogikaRamki` / `ProgramRamki.krok`
z czasem sztucznym - bez sieci, bez portow). Po przebiegach: 0 procesow python konta `<konto-PC>`, 0 nasluchow
na 8765, 0 plikow `.pyc`. Na MSI nie uruchamiano pytest ani obliczen. Kodu nie zmienialem.

## 0. Werdykt

**do scalenia po poprawkach** - B 1 / P 7 / D 12.

Program jest porzadnie zbudowany (logika bez watkow i sprzetu, scisla walidacja, czas sztuczny w testach) i w
podstawowych sytuacjach zachowuje sie bezpiecznie: inna plytka niz w planie = "n BRAK" bez gniazd, restart = brak
planu, utrata sieci = wygasniecie, zly JSON = odrzucenie. Znalazlem jednak jedna sciezke, na ktorej CZERWONE
gniazdo nigdy sie nie zapali (B1), i kilka, na ktorych zostaje albo wraca OBRAZ NIEAKTUALNY (P1-P5, P7) - czyli
wbrew zasadzie "w razie watpliwosci nic nie swieci". Wszystkie poprawki sa male (po kilka-kilkanascie linii w
`logika.py` / `program.py` + test) i warto je zrobic TERAZ, bo `README.md` jest kontraktem dla wykonawcy 2
(`indicate`) - pozniej trzeba by zmieniac obie strony.

## 1. Uwagi (B = blokujaca, P = poprawic przed scaleniem, D = drobna / moze zostac jako znana)

Sciezki wzgledem `Ramki/stanowisko/`. "Uruchomione" = skrypt `scen_r19.py` na PC (numer scenariusza w nawiasie).

| Nr | Waga | Plik:linia | Scenariusz (wejscie -> zly wynik) | Sprawdzone | Oczekiwane |
|---|---|---|---|---|---|
| B1 | B | `ramka/logika.py:408-412` (regula swiecenia), `:290` (ramka W ignoruje klawisze), `ramka/protokol.py:185-187` (pole `kuweta` przyjmowane bez wzgledu na role) | Plan WIECZORNY, w ktorym laptop wypelni pole `kuweta` przy gniazdach (prace wieczorem tez maja numery kuwet; README mowi tylko w nawiasie, ze wieczorem gniazda sa bez kuwety - nigdzie tego nie zabrania). Ramka W stosuje wtedy regule poranna "swieci tylko biezaca kuweta": swieca gniazda pierwszej kuwety z listy, a czerwone gniazdo ("sprawdz") innej kuwety jest CIEMNE i nie da sie go wywolac, bo ramka W nie ma klawiatury. Ukruszona praca nie jest wskazana, plan przyjety kodem 200. | **Uruchomione (S3):** 3 gniazda: zielone kuweta 100, czerwone kuweta 200, czerwone bez kuwety -> swieci 9 px zielonych + 9 czerwonych zamiast 18 czerwonych; Enter nic nie zmienia. | Ramka W: `kuweta` w gniezdzie = 400 (albo pole ignorowane i wszystkie gniazda swieca). Zdanie w README + test. |
| P1 | P | `ramka/logika.py:166-176` (wersja sprawdzana tylko wzgledem zapamietanej; ta sama wersja przyjmowana ponownie, gdy planu juz nie ma), `:199-215` (`usun_plan` nie zapamietuje, ze wersje skasowano), `:190` | Spozniony PUT /plan. (a) Laptop wysyla plan v1, odpowiedz ginie w Wi-Fi; skan okazuje sie nieprzyjety -> `DELETE /plan` (ciemno); ponowienie albo opozniona kopia PUT v1 dociera po DELETE -> 200 `przyjety`, gniazda swieca znowu. (b) To samo po Spacji: `PUT /tryb skanowanie`, potem dociera spozniony plan poprzedniego skanu -> stan `wynik`, stary obraz. Ochrona "plan_starszy" dziala tylko dla wersji NIZSZEJ niz ostatnia. | **Uruchomione (S1, S2):** po DELETE ten sam PUT v1 -> `przyjety`, 9 px swieci; po `skanowanie` spozniony PUT -> `przyjety`, tryb `wynik`, 9 px. | DELETE i `PUT /tryb skanowanie / blad` zapamietuja wersje jako zamknieta: ten sam `plan_id` wymaga potem wersji WYZSZEJ (inaczej 409 `plan_starszy`). Ponowne przyjecie tej samej wersji tylko po `plan_wygasl`. Prosciej: jeden rosnacy numer polecenia laptopa wspolny dla PUT /plan, PUT /tryb, DELETE. |
| P2 | P | `ramka/logika.py:217-229` (`ustaw_tryb`), `ramka/README.md:116-117` ("plan zostaje") | `skanowanie`, `analiza`, `blad`, `gotowa` gasza gniazda, ale plan zostaje w pamieci tak dlugo, jak laptop odpytuje (czyli bez konca). Kazdy pozniejszy `PUT /tryb wynik` zapala STARY plan. Wieczorem: plytka 1 obejrzana i zdjeta; nowe prace na plytce 1; Spacja; skan zablokowany -> `tryb blad` (zgodnie z kontraktem pkt 5); plytka 1 lezy na ramce; laptop (albo blad w nim) wysyla `tryb wynik` -> kolory poprzedniego skanu pod nowymi pracami. | **Uruchomione (S2):** po `blad` plan w pamieci = tak; po `PUT /tryb wynik` 9 px swieci. | `PUT /tryb` ze stanem `wynik` odrzucac (stan `wynik` ustawia wylacznie przyjety plan). Na ramce W `skanowanie` i `blad` kasuja plan (nowy skan z definicji uniewaznia stary wynik). Test. |
| P3 | P | `ramka/logika.py:240-241`, `ramka/protokol.py:237` (`usun_po_zdjeciu` domyslnie `false`), `ramka/logika.py:171-176` | Ta sama plytka z nowymi pracami (otwarte pytanie wykonawcy). (a) Domyslnie: plytka 1 zdjeta, nowe prace, polozona bez skanu -> stare kolory swieca, dopoki laptop zyje. (b) Z `usun_po_zdjeciu = true` wpis plytki znika, ale ponowny PUT tej samej wersji dostaje 200 `powtorzony` i wpis NIE wraca - laptop mysli, ze ramka pokazuje plan, a `plytki_planu` jest puste (kierunek bezpieczny, ale pulapka w kontrakcie; README: "powtorzony = nic sie nie zmienia"). To samo po krotkim falszywym "brak plytki" dluzszym niz 30 ms. | **Uruchomione (S4):** (a) po 5 min i ponownym polozeniu 9 px swieci; (b) `powtorzony`, `plytki_planu` = []. | Ramka W: wpis plytki kasowany po zdjeciu ZAWSZE (nie zalezy od pola z laptopa). Ramka P: zostaje wg pola. `powtorzony` tylko wtedy, gdy plan w pamieci jest nienaruszony; inaczej przyjac ponownie albo 409 z jasnym kodem. Opis w README, test. |
| P4 | P | `ramka/program.py:102-108` (odczyty sprzetu przed logika), `:128-136` (`_petla`: log i `sleep 0.5`, matryca bez zmian) | Wyjatek w `odczytaj_plytke` / `pobierz_klawisze` (np. blad gpiozero, odlaczony czujnik) powtarza sie w kazdym obiegu: petla loguje i probuje dalej, a matryca pokazuje OSTATNIA klatke bez konca - takze po zdjeciu plytki i po wygasnieciu planu (`tick` z petli sie nie wykonuje, obraz nie jest rysowany). | **Uruchomione (S6):** `krok()` z atrapa rzucajaca `OSError`: po 100 s (plan `wazny_s` = 30, plytka zdjeta) na matrycy dalej 9 px gniazd; `logika.plan` nadal jest, `logika.plytka` = 1. | W `except` petli: pokazac klatke awaryjna (czarna + czerwony pierscien / "BLAD"), ustawic w logice stan bledu sprzetu widoczny w `GET /stan`; gniazda wracaja dopiero po udanym obiegu. Test z atrapa rzucajaca wyjatek. |
| P5 | P | `ramka/logika.py:154-180` (odrzucenie planu nie zmienia stanu) | Odrzucony PUT /plan od wlasciciela zostawia poprzedni obraz. Skan moze ruszyc bez wiedzy laptopa (Spacja w programie skanera, laptop tylko obserwuje folder - fakt 7), wiec `tryb skanowanie` nie poprzedza planu; nowy plan zostaje odrzucony (blad kalibracji `px_poza_plytka`, plytka spoza rodziny, 413...) -> ramka dalej pokazuje wynik POPRZEDNIEGO skanu tej plytki. Dotyczy tez wymagania z 17.11: plan plytki porannej wyslany do ramki W jest odrzucany (dobrze), ale stary obraz zostaje. | **Uruchomione (S5):** 4 odrzucenia (400 `px_poza_plytka`, 400 `zla_plytka`, 409 `plan_innej_ramki`, 400 `zly_json`) - po kazdym 9 px starego planu swieci, tryb `wynik`. | Odrzucenie tresci planu (400, `plan_innej_ramki`, `konflikt_wersji`) od laptopa-wlasciciela = stan `blad` bez gniazd (albo skasowanie planu). Bez zmiany stanu zostaja tylko: `powtorzony`, `plan_starszy`, `inny_laptop`, `inny_start`, `zdarzenia_nieodebrane`. |
| P6 | P | `ramka/serwer.py:146-150`, `ramka/logika.py:106-111`, `:357` (pole `laptop` w `GET /stan`), `ramka/program.py:278` (na Pi nasluch `0.0.0.0`) | Brak uwierzytelnienia. Dowolne urzadzenie w tej samej sieci: (a) czyta `GET /stan` bez naglowka i dostaje identyfikator laptopa-wlasciciela; (b) z tym identyfikatorem podmienia plan (czerwone -> zielone) albo gasi; (c) z wlasnym identyfikatorem przejmuje wolna ramke i odpytujac co kilka sekund blokuje prawdziwy laptop kodem 409 `inny_laptop` bez konca; (d) samym GET z cudzym identyfikatorem przedluza waznosc planu po awarii laptopa. | **Uruchomione (S9):** podmiana -> `przyjety`, 9 px zielonych; prawdziwy laptop przez 10 min tylko `409 inny_laptop`. | Do decyzji wlasciciela (pkt 4.3). Minimum przed wlaczeniem ramki do sieci firmowej (paczka C1): wspolny klucz w konfiguracji ramki i w ustawieniach laptopa, wysylany w naglowku, porownywany `hmac.compare_digest`; bez klucza tylko `GET /stan` w wersji okrojonej (bez pola `laptop`). W tej paczce: opisac ograniczenie w README jawnie ("X-Laptop-Id to nie zabezpieczenie"). |
| P7 | P | `ramka/sprzet.py:53-69` (`Odbijanie.podaj`), `ramka/program.py:111-113` | Odbijanie jest symetryczne: dopoki surowy odczyt sie zmienia czesciej niz co 30 ms, ramka trzyma STARY numer i swieci jego gniazda - bez ograniczenia czasu. Plytka 5 zdjeta albo zamieniona na krzywo polozona, jeden czujnik drga (magnes na granicy zadzialania) -> gniazda plytki 5 swieca dalej. | **Uruchomione (S7):** ustalona 5, potem 10 s odczytow 4 / 0 co 20 ms -> ustalona dalej 5, 0 zdarzen. Na prawdziwych A3144 (maja histereze) czestosc zjawiska nieznana - do C1. | Gaszenie natychmiast, zapalanie po ustaleniu: gdy odczyt surowy != ustalony, gniazda nie swieca (np. numer "niepewny" w logice); zapalenie dopiero po 30 ms stalego odczytu. Skraca tez czas reakcji I5. Test. |
| D1 | D | `ramka/logika.py:156-157, 201-202, 219-220`; `ramka/program.py:148-149, 169-170` | (a) `kontakt()` jest wolany przed `tick()`: gdy petla sprzetu nie zdazyla (albo stoi jak w P4), zadanie wlasciciela po terminie ozywia plan bez `plan_wygasl`. (b) Dlugie odpytywanie zapisuje kontakt takze na KONCU czekania, nawet gdy klient juz zniknal: plan zyje do `wazny_s` x 4/3 (30 s -> do 40 s). | (a) **Uruchomione (S12)** na samej logice; w programie okno to ok. 10 ms. (b) czytane. | `tick()` przed `kontakt()`; kontakt tylko na poczatku zadania. |
| D2 | D | `ramka/logika.py:59, 77-86`; `:345-361` (`stan` bez listy potwierdzonych) | Przepelnienie dziennika (2000): drgajacy czujnik daje 2 zdarzenia `plytka` na drgniecie, w ok. 90 s wypycha zdarzenia klawiatury. Laptop widzi `utracone`, ale nie ma skad wziac stanu potwierdzen (nie ma go w `GET /stan`); wysyla plan ze swoja lista -> potwierdzenia przepadaja (kuwety trzeba potwierdzic drugi raz - kierunek bezpieczny). | **Uruchomione (S11):** utracone 201, potwierdzenie poza dziennikiem, po nowej wersji planu `potwierdzone` = []. | `GET /stan` z lista `potwierdzone` / `wybrane` albo osobny, nieusuwany dziennik zdarzen klawiatury; ograniczenie tempa zdarzen `plytka`. |
| D3 | D | `ramka/logika.py:287-341` | Klawiatura: (a) dwa Entery jeden po drugim (5 ms) potwierdzaja DWIE kuwety - brak minimalnego odstepu; (b) wpisana cyfra nie wygasa: zablakane "7" po 6,5 min + Enter = wybor kuwety 7 zamiast potwierdzenia biezacej (na marginesie widac "7_", wiec da sie zauwazyc); (c) `zamknij_piec` idzie zawsze: 3 nacisniecia = 3 zdarzenia, takze bez planu i bez plytki. Backspace cofa poprawnie, nieznany numer daje "?7777" na 3 s i zdarzenie - bez zastrzezen. | **Uruchomione (S10).** | (a) pomijac Enter potwierdzajacy w ciagu ok. 0,3 s od poprzedniego; (b) kasowac wpisywane cyfry po ok. 10 s; (c) patrz pytanie 4.2. |
| D4 | D | `ramka/protokol.py:144` (`_numer_plytki`), `ramka/serwer.py:53, 110` (`isdigit`) | `str.isdigit()` przyjmuje cyfry spoza ASCII: klucz plytki "\u0664" jest przyjmowany jako 4, "\u00b2" daje `ValueError` -> 500 `blad_wewnetrzny` zamiast 400. Niegrozne. | **Uruchomione (S8).** | `isascii() and isdigit()`. |
| D5 | D | `ramka/protokol.py:43, 45, 207, 236, 311-314`; `ramka/README.md:171-173` | Zdanie "nazwisko nie przejdzie walidacji" jest prawdziwe tylko dla kuwet. Pola `plan_id`, `uklad` i naglowek `X-Laptop-Id` przyjmuja litery (np. `plan_id` = "2026-11-17-kowalski"), a `plan_id` i `laptop` wracaja w `GET /stan` i zdarzeniach. | Czytane. | Zawezic `plan_id` (cyfry, myslnik, litery p / w) albo zapisac w README, ze te pola wypelnia program, nigdy czlowiek. |
| D6 | D | `ramka/protokol.py:37, 211` | `wazny_s` do 3600 s takze dla ramki W - o czasie swiecenia po awarii laptopa decyduje wylacznie laptop. | Czytane. | Gorna granica w konfiguracji ramki zalezna od roli (np. W 60 s, P 900 s). |
| D7 | D | `ramka/sprzet_rpi.py:129-171` (klawiatura), `:183-190` (`pokaz`), `ramka/program.py:40, 58-61` | Czytaniem (kod nie byl uruchamiany): numery GPIO 19 / 25 / 8, kolejnosc bitow n = A + 2B + 4C, stan aktywny niski (`InputDevice(pull_up=None, active_state=False)`), import bibliotek tylko w konstruktorze i watku - POPRAWNE; piny nie koliduja z mapowaniem `adafruit-hat-pwm`. Drobne: (a) `OSError` z `d.grab()` daje petle bez przerwy (100 % jednego rdzenia); (b) inny wyjatek w watku klawiatury konczy go po cichu, brak `evdev` tez (komentarz obiecuje wpis w logu, ktorego nie ma); (c) 4096 x `SetPixel` na klatke w Pythonie, przy braku lacznosci 2 klatki / s; (d) `piny_halla` o dlugosci innej niz 3 przechodzi; (e) 3 bity bez kontroli: uszkodzony czujnik A zmienia plytke 5 w 4 (obie w planie porannym) - wynika z projektu ramki, do opisu ryzyka w C1; (f) po zabiciu procesu panel moze trzymac ostatni wiersz - sprawdzic w C1. | Czytane; test `test_sprzet_rpi_...` przeszedl (import bez bibliotek = `BladSprzetu`, tryb atrapy nie laduje modulu). | (a) `self._stop.wait(2.0)` po bledzie; (b) `log.exception`; reszta do C1. |
| D8 | D | `ramka/serwer.py:78, 104-126, 218-221` | Kazde polaczenie = osobny watek, bez limitu liczby; limit 15 s dotyczy pojedynczego odczytu, wiec klient wysylajacy po 1 bajcie trzyma watek godzinami; dlugie odpytywanie trzyma watek do 25 s. Jedno wolne polaczenie NIE blokuje innych. Tresc ograniczona do 64 KiB (do 1 MiB czytane i wyrzucane) - dobrze. Na Windows `allow_reuse_address = True` pozwala dwom atrapom sluchac na tym samym porcie bez bledu. | Czytane. | Limit jednoczesnych polaczen (np. 16) i calkowity czas odczytu zadania; `allow_reuse_address` tylko poza Windows. |
| D9 | D | `ramka/logika.py:199-207`; `ramka/program.py:158-160`; `ramka/logika.py:174-176` | (a) Spozniony `DELETE /plan?plan_id=X` kasuje takze NOWSZA wersje planu X (kierunek bezpieczny). (b) `start_id` w `/zdarzenia` jest opcjonalny: bez niego po restarcie ramki laptop z kursorem 500 dostaje puste odpowiedzi od razu, w petli. (c) `powtorzony` nie przywraca stanu `wynik` po `tryb gotowa` (ciemno, laptop mysli, ze swieci). | Czytane. | (a) `DELETE` z wersja; (b) `start_id` wymagany; (c) w odpowiedzi `powtorzony` podawac biezacy `tryb`. |
| D10 | D | `testy/test_ramka.py:562-587, 836-866, 900-960, 1442-1466, 765-800` | Testy: K1-K5, K7, K9 sprawdzaja to, co mowi kryterium (porownanie piksel po pikselu, lista zdarzen dokladna, 500 potwierdzen przez posrednika TCP gubiacego odpowiedzi). Zastrzezenia: K4 ma maly zapas (limit 100 ms, u mnie maks 61 ms, u wykonawcy do 79 ms; odbijanie 30 ms + petla 10 ms + zegar Windows) - w pelnym pytest pod obciazeniem moze byc czerwony; K7 u mnie maks 264 ms (raport: 4 ms), limit 1 s; K6 sprawdza klienta testowego, nie `indicate` (raport to przyznaje); K8 jest czesciowo tautologiczny - klienci testowi sami nie wysylaja nazw, wiec test dowodzi tylko, ze ramka ich nie odsyla i ze odrzuca zle pola. Sprzatanie: `zatrzymaj()` w fixture / `finally`, proces potomny K7 konczony przez EOF + `kill` - po przebiegu 0 procesow i portow (sprawdzone). Brak testow dla B1, P1-P5, P7. | **Uruchomione:** 44 passed w 12,67 s. | Testy do poprawek; K4: limit na medianie + luzniejszy maks albo czas sztuczny. |
| D11 | D | `ramka/protokol.py:217-219, 250`; `ramka/logika.py` (brak uzycia) | Pola przyjmowane i nieuzywane: `kolejnosc` (ramka idzie po liscie `kuwety`), `kuwety[].prac` (liczba na marginesie liczona z gniazd lezacej plytki), `uklad` (informacyjne). | Czytane. | Usunac albo opisac jako informacyjne. |
| D12 | D | `raporty/E3-A8-ramka_2026-11-17.md` | Raport rzetelny co do zakresu i tego, czego nie sprawdzono. Rozbieznosci: "K7 maks 4 ms" (u mnie 264 ms), "1478 komunikatow" (u mnie 1482) - bez znaczenia. Zdanie "blad / DELETE = zgas" pomija, ze po `blad` plan zostaje (P2), a pkt 3 odstepstw przerzuca problem tej samej plytki na laptop (P3). | Porownanie z przebiegiem. | Uzupelnic po poprawkach. |

## 2. Bezpieczenstwo wskazan - przeglad stanow (pkt 1 zlecenia)

| Sytuacja | Zachowanie | Ocena |
|---|---|---|
| Zmiana plytki w trakcie (4 -> 0 -> 5) | obraz przelaczany po 30 ms odbijania; plan plytki 4 nie swieci pod 5 (test K4 sprawdza klatki) | dobrze; wyjatek: drgajacy czujnik (P7) |
| Plytka o numerze spoza planu | "n BRAK", pomaranczowy pierscien, 0 gniazd | dobrze |
| Ta sama plytka z nowymi pracami | stary plan swieci (domyslnie) | P3, P2 |
| Plan dla innego numeru plytki / spoza rodziny ramki | 400 `zla_plytka` | odrzucenie dobre, ale stary obraz zostaje (P5) |
| Plan dla drugiej ramki | 409 `plan_innej_ramki` (tryb) i 409 `inny_start` (kazda ramka ma swoj `start_id`) | dobrze; stary obraz zostaje (P5) |
| Plan starszy / powtorzony | 409 `plan_starszy` / 200 `powtorzony` | dobrze, poza powtorka po DELETE i po `skanowanie` (P1) oraz pulapka `powtorzony` (P3) |
| Dwa laptopy | drugi dostaje 409, dopoki pierwszy odzywa sie w 30 s | logika poprawna; bez uwierzytelnienia latwe do naduzycia (P6) |
| Restart ramki | plan tylko w RAM -> brak planu, nowy `start_id`, stary plan = 409 `inny_start` | dobrze |
| Utrata sieci | po `wazny_s` plan kasowany, `plan_wygasl`, pierscien miga na czerwono | dobrze (D1: do 4/3 czasu) |
| Krotkie falszywe "brak plytki" | < 30 ms ignorowane; dluzsze = zdarzenia `plytka 0` i powrot, plan zostaje (z `usun_po_zdjeciu` znika) | dobrze; P3 (b) |
| Zly / niepelny JSON, gniazdo spoza zakresu, piksele poza plytka, nakladanie | 400, szczegolowy kod, opis bez wartosci z zadania | odrzucenie dobre; stary obraz zostaje (P5) |
| Blad sprzetu w petli | ostatnia klatka zostaje | P4 |
| Plan wieczorny z kuwetami | czesc gniazd ciemna | B1 |

Zegar: `time.perf_counter` jest monotoniczny (na Linuksie CLOCK_MONOTONIC, niewrazliwy na zmiane godziny) - bez
zastrzezen. Watki: caly stan logiki pod jedna blokada (`Condition(RLock)`), sprzet tylko z watku petli, `pokaz`
poza blokada - wyscigu nie znalazlem; opoznienie reakcji na zadanie HTTP do ok. 10 ms.

## 3. Protokol (pkt 2 zlecenia)

"Kazde zdarzenie raz": numeracja ciagla od startu, laptop pyta o `od` = ostatni odebrany, wiec zgubiona odpowiedz
= to samo pytanie jeszcze raz; sprawdzone testem K5 (500 z 500, 0 powtorek, 0 luk, 240 nieudanych odpytan) i
testem 2 klientow rownoleglych. Gwarancja konczy sie przy przepelnieniu dziennika (D2).
Zakleszczenie: nie znalazlem. `zdarzenia_nieodebrane` ma wyjscie zawsze (laptop odpytuje i podaje
`zdarzenia_do` = biezacy numer; nowy `plan_id` w ogole nie podlega temu sprawdzeniu); `inny_start` -> `GET /stan`;
`inny_laptop` mija po 30 s ciszy wlasciciela (ale patrz P6 c); `konflikt_wersji` -> wyzsza wersja.

Ocena rozszerzen wzgledem sekcji 3.6 planu:

| Rozszerzenie | Ocena | Uwagi |
|---|---|---|
| `wersja` | potrzebne | chroni przed starszym planem; niepelne bez P1 |
| `start_id` w planie i w `/zdarzenia` | potrzebne | jedyna pewna ochrona po restarcie i przed planem dla drugiej ramki; w `/zdarzenia` powinno byc wymagane (D9) |
| `zdarzenia_do` | potrzebne (rano) | chroni potwierdzenia przed nadpisaniem; dla ramki W bez znaczenia, ale nie szkodzi |
| `wazny_s` | potrzebne | realizuje wymaganie z 17.11; ryzyko: wartosc ustala laptop (D6) |
| `X-Laptop-Id` | przydatne, ryzykowne jako "ochrona" | porzadkuje dwa laptopy; nie jest zabezpieczeniem i umozliwia zablokowanie ramki (P6) |
| `potwierdzone`, `wybrane` | potrzebne | odtworzenie stanu po restarcie ramki i przy nowej wersji planu |
| `usun_po_zdjeciu` | potrzebne, ale zle ustawione | wieczorem powinno byc zachowaniem stalym ramki, nie polem opcjonalnym (P3) |
| zdarzenie `plan_wygasl` | potrzebne | laptop wie, ze ramka zgasla |
| zdarzenie `kuweta_nieznana` | zbedne dla dzialania, nieszkodliwe | przydatne do komunikatu na ekranie laptopa; niesie tylko wpisane cyfry |
| `kolejnosc`, `kuwety[].prac`, `uklad` | zbedne w ramce | D11 |
| `PUT /tryb wynik` | ryzykowne | P2 |

## 4. Rekomendacje do pytan wykonawcy (prostym jezykiem)

1. **Ile ramka trzyma plan bez sieci (propozycja: rano 600 s, wieczorem 30 s).** Rekomendacja: przyjac obie
   wartosci, a w ramce dodac twarda gorna granice zalezna od roli (D6). Ryzyko wyboru domyslnego: wieczorem po
   zawieszeniu laptopa stare kolory swieca jeszcze do 30-40 s (D1); rano po awarii laptopa ramka przez 10 minut
   pracuje na ostatnim planie i nie zobaczy zmian zrobionych w tym czasie na laptopie - widac to po migajacym
   czerwonym pierscieniu. Krotszy czas rano = ramka gasnie w polowie rozkladania przy slabym Wi-Fi.
2. **Klawisz "Zamknij piec" (propozycja: jedno nacisniecie `*`, bez potwierdzenia).** Rekomendacja: dwa kroki na
   ramce - `*` pokazuje na marginesie pytanie, Enter w ciagu ok. 5 s potwierdza, kazdy inny klawisz anuluje;
   bez planu klawisz nic nie robi. Ryzyko wyboru domyslnego: `*` lezy na klawiaturze numerycznej tuz obok
   Backspace i minusa; jedno przypadkowe nacisniecie zamyka sesje pieca w polowie rozkladania (laptop kasuje plan,
   ramka gasnie), a 3 nacisniecia daja 3 zdarzenia (D3).
3. **Wyglad marginesu.** Rekomendacja: przyjac jako roboczy i ocenic na zlozonej ramce (bramka G2) - na atrapie
   nie da sie ocenic czytelnosci. Ryzyko: male; uwaga - napis to "3263 3" (liczba prac kuwety na LEZACEJ plytce),
   a zrodlo I3 podaje "3263 - 4" (liczba prac kuwety); prawy margines miesci po jednej cyfrze na plytke.
4. **Ta sama plytka z nowymi pracami.** Rekomendacja: wieczorem ramka sama kasuje wynik plytki w chwili jej
   zdjecia (zawsze, bez pola z laptopa), a laptop dodatkowo gasi przy Spacji; rano plan zostaje (plytki wracaja na
   ramke w trakcie rozkladania). Ryzyko wyboru domyslnego (plan zostaje): technik naklada nowe prace na plytke 1
   i kladzie ja na ramce bez skanu albo po nieudanym skanie - swieca zielone i czerwone z POPRZEDNIEGO skanu
   (S4, P2, P3). Koszt rekomendacji: po kazdym podniesieniu plytki wieczorem trzeba ja zeskanowac ponownie albo
   laptop musi wyslac plan jeszcze raz (nowa wersja).
5. **Rozszerzenia protokolu.** Rekomendacja: zatwierdzic wszystkie z tabeli w pkt 3 z poprawkami B1, P1-P3, P5
   i dopisac jawna zasade "kazde odrzucenie i kazda niepewnosc = gniazda ciemne". Ryzyko zatwierdzenia bez
   poprawek: wykonawca 2 zbuduje `indicate` na kontrakcie, w ktorym zgaszenie nie jest ostateczne (P1, P2).
6. **(dodatkowe) Siec firmowa.** Rekomendacja: w sieci, w ktorej sa wylacznie laptop stanowiska i ramki (osobna
   siec albo hotspot laptopa z I13), obecny stan jest do przyjecia; w zwyklej sieci firmowej przed uruchomieniem
   prawdziwej ramki dodac wspolny klucz (P6) i ograniczyc ruch do adresu laptopa (zapora na Raspberry Pi).
   Ryzyko stanu obecnego: kazdy komputer w sieci moze zmienic kolory albo zablokowac ramke; podsluch nie ujawnia
   danych osobowych (sa tylko numery).

## 5. Higiena (pkt 7 zlecenia)

- 17 plikow, wszystkie ze statusem "A" (nowe); 0 zmian w istniejacych plikach, w tym 0 w `modele_plytek/*/uklad.json`
  (`kalibracja.py` tylko czyta; test `test_kalibracja_domyslna_..._nie_zmienia_ukladow` przeszedl).
- Wszystkie 17 plikow: 0 bajtow spoza ASCII, 0 znakow CR (sprawdzone `grep` na MSI i testem
  `test_pliki_ramki_skladnia_python_311_ascii_lf`).
- Tryb atrapy tylko na bibliotece standardowej: importy przeczytane; test K9 (`python -I -S`) przeszedl.
- Python 3.11: nie znalazlem `match`, `type`, `except*`, `tomllib`, zagniezdzonych cudzyslowow w f-napisach ani
  modulow z 3.12; test z `ast.parse(feature_version=(3, 11))` jest slabym dowodem (nie wykrywa np. nowej skladni
  f-napisow) - uruchomienie na 3.11 dopiero na Raspberry Pi.
- Nazwiska: 6 fikcyjnych w `testy/test_ramka.py` (celowo, jako dane do sprawdzenia K8); w kodzie, README i
  raporcie 0. Sciezek z nazwa konta w nowych plikach nie znalazlem.

## 6. Czego NIE sprawdzilem

- Niczego na prawdziwym sprzecie: `sprzet_rpi.py` tylko czytaniem (matryca, czujniki, klawiatura, start < 60 s,
  8 h pracy, Wi-Fi, `.local`); zgodnosc z Pythonem 3.11 tylko czytaniem.
- Pelnego pytest (724 / 8 / 0 wg wykonawcy) nie uruchamialem - zgodnie z ograniczeniem; `test_ramka.py` 1 raz.
- Scenariuszy P1-P5, P7 nie odtwarzalem przez siec z prawdziwymi opoznieniami - sa odtworzone na logice z czasem
  sztucznym (kolejnosc wywolan taka, jaka da spozniony pakiet); P6 rowniez na logice. D1 (b), D7-D9, D11 tylko
  czytaniem.
- Czcionki i ukladu marginesu (`czcionka.py`, `rysuj_*`) nie ocenialem wizualnie; `test_led.py` i `kalibracja.py`
  przeczytane bez prob na plikach innych niz w testach.
- Strony laptopa (`indicate`) nie ma w tej paczce - nie wiem, czy bedzie wysylac kuwety wieczorem (B1), `tryb wynik`
  (P2) ani jak ponawia zadania (P1); uwagi zakladaja, ze ramka ma byc bezpieczna niezaleznie od bledow laptopa.
- Obciazenia serwera (wiele polaczen, wolny klient) nie mierzylem.
