# Raport recenzenta PR #19 - runda 2 (przyrostowa)

Data: 2026-11-17. Recenzent: swieza subsesja, niezalezna od wykonawcy i koordynatora; werdyktu rundy 2 nie znalem.
Stan recenzowany: `origin/e3/a8-ramka` HEAD `fe7dac1`, zakres `git diff 46ea1b6..fe7dac1 -- Ramki/stanowisko`
(12 plikow: `ramka/**`, `narzedzia/atrapa_ramki.py`, `testy/test_ramka.py`, raport wykonawcy).
Metoda: przeczytane w calosci `ramka/logika.py`, `protokol.py`, `serwer.py`, `program.py`, `sprzet.py`, diff
`sprzet_rpi.py`, `sprzet_atrapa.py`, `czcionka.py`, `atrapa_ramki.py`, `README.md`, raport wykonawcy (rozdzial
"Runda 2"), raport rundy 1; `testy/test_ramka.py` - wszystkie testy rundy 2 w calosci, testy rundy 1 przez diff
`46ea1b6..45f959f` i `45f959f..fe7dac1` (czy nic nie oslabiono).
Uruchomienia (tylko PC, konto zadan, `<PC-katalog>\e3\r19b`, wolny RAM przed startem 17-18 GB, przebiegi po kolei):
1. `testy\test_ramka.py` na `fe7dac1`: **63 passed w 12,93 s**.
2. `testy\test_ramka.py` na `45f959f` (testy czerwone + kod rundy 1, katalog `r19b\red`): **26 failed / 36 passed**
   (14,05 s) - zgodnie z raportem; dodatkowo 1 przebieg 11 testow B1/P1-P7 z `--tb=line` (2,9 s): czerwone z powodu
   zachowania (piksele swieca, plan przyjety, wyjatek), P7-odbijanie przez brak atrybutu `pewna`.
3. Wlasny skrypt `<PC-katalog>\e3\r19b\scen_r19b.py`: 15 scenariuszy N1-N21 na `LogikaRamki` / `ProgramRamki.krok`
   z czasem sztucznym + 1 serwer na 127.0.0.1 (port 0) dla N11.
Po przebiegach: 0 wlasnych procesow python (widoczne 4 procesy python innych uzytkownikow PC, bez dostepu do nich),
0 nasluchow na 8765, 0 plikow `.pyc` i `.pytest_cache`. Na MSI nie uruchamialem pytest ani obliczen. Kodu nie zmienialem.

## 0. Werdykt

**do scalenia po poprawkach** - nowe uwagi: **B 0 / P 2 / D 13**.

Runda 2 zalatwia B1 i P2, P4-P7 rzetelnie (testy odtwarzaja scenariusze rundy 1 i na starym kodzie sa czerwone),
README dostal jawna zasade "kazde odrzucenie i kazda niepewnosc = gniazda ciemne" i tabele samoczynnego gaszenia.
Zostaja dwie dziury, obie typu "stary obraz wraca przez nowe polecenie laptopa", i obie wynikaja glownie z
KONTRAKTU (README), ktory jest wejsciem dla wykonawcy 2 - dlatego P, a nie D:
- **P-N1** (reszta P3): ramka W kasuje wynik zdjetej plytki tylko wtedy, gdy plan jest w pamieci i tylko do
  nastepnej wersji; README kaze laptopowi "wyslac plan ponownie" po `plan_wygasl` / restarcie i pozwala pokazac
  wynik ponownie "nowa wersja" - wynik plytki zdjetej i polozonej z nowymi pracami wraca (uruchomione N1, N2).
- **P-N2** (reszta P1): zgaszenie po wygasnieciu planu nie zamyka jego wersji (README twierdzi, ze zamyka -
  uruchomione N3); znana luka "nowe polaczenie po zgaszeniu" jest realna przy typowych implementacjach ponowien,
  a zdanie README o `plan_zgaszony` ("nie ponawiaj tej wersji") wrecz zacheca do ponowienia z `wersja + 1` (N4).
Poprawki sa male: kilka zdan w README + 2 krotkie zmiany w `logika.py` + testy (propozycje nizej). Nie znalazlem
sekwencji, w ktorej gniazda swieca wg starego planu BEZ nowego `PUT /plan` od laptopa.

## 1. Uwagi rundy 1 -> stan

Sciezki wzgledem `Ramki/stanowisko/`.

| Nr | Stan | Dowod / uwagi |
|---|---|---|
| B1 | zalatwiona | plan W z `kuweta` / polami porannymi = 400 `pole_tylko_rano` i ciemno; obraz W swieci wszystkie gniazda niezaleznie od pola (`logika.py:531`); `test_b1_...` czerwony na 45f959f, zielony na fe7dac1 (uruchomione) |
| P1 | **czesciowo** | S1, S2 i "wolny PUT przed DELETE" zamkniete (testy uruchomione); po wygasnieciu planu DELETE / PUT /tryb nie zamykaja wersji (N3), znana luka realna przy ponowieniach laptopa (N4) -> **P-N2** |
| P2 | zalatwiona | kazdy `PUT /tryb` usuwa plan, `wynik` usuniety z `PUT /tryb` (400 `zly_stan`, od wlasciciela gasi); przeplyw skanowanie -> analiza -> plan (wyzsza wersja) dziala bez mrugania (nowy plan ustawiany w jednym obiegu); skutki uboczne: D-N3, D-N8 |
| P3 | **czesciowo** | ramka W kasuje wynik plytki przy zdjeciu i zamyka wersje (`logika.py:326-328`), test S4 uruchomiony; ale tylko gdy plan jest w pamieci i tylko do nastepnej wersji; kontrakt pozwala przywrocic wynik -> **P-N1**; rano plan zostaje (decyzja) -> D-N12 |
| P4 | zalatwiona | wyjatek w obiegu = klatka awaryjna albo `wygas()`, plan usuniety, `blad_sprzetu` raz, 409 `blad_sprzetu`, `sprzet_dziala` po udanym obiegu; rano plan odzyskiwany nowa wersja z `potwierdzone` z wlasnego stanu laptopa (N21 uruchomione); uwagi: D-N7 (migotanie awarii), D-N10 (zawieszenie zamiast wyjatku) |
| P5 | zalatwiona | 400 / 411 / 413 / `plan_innej_ramki` / `konflikt_wersji` / zly `PUT /tryb` od wlasciciela gasza; od innego laptopa przy aktywnym wlascicielu nie (testy uruchomione); blad pola w planie plytki 5 gasi lezaca plytke 4, odpowiedz podaje kod i sciezke pola (N14); luki: D-N6 |
| P6 | zalatwiona (w zakresie paczki) | klucz z lokalnego pliku, `hmac.compare_digest`, 401 bez tresci i bez zmiany stanu dla kazdego zasobu (takze nieznanego i `/atrapa/*`), `GET /stan` bez id laptopa (`wlasciciel` bool), klucz nie trafia do logow / zdarzen / stanu, test losuje klucz (`secrets.token_hex`); bez pliku: bez klucza i nasluch 127.0.0.1; adres sieci przez `host` (README 50-51); ograniczenie HTTP opisane (README "Siec i klucz"); uwagi C1: D-N10 |
| P7 | zalatwiona | `Odbijanie` gasi przy pierwszym innym odczycie, zapala po 30 ms stalego odczytu, odczyt ciagle rozny > 30 ms = `plytka 0`; testy S7 na `Odbijanie` i na petli (czas sztuczny) uruchomione |
| D1 | zalatwiona | (a) `tick` przed `kontakt` we wszystkich zadaniach (test); (b) kontakt tylko na poczatku odpytywania (czytane, `program.py:208-211`) |
| D2 | zalatwiona | `utracone_od` / `utracone_do`, `GET /stan` z `potwierdzone` / `wybrane` (test) |
| D3 | b zalatwiona, a znana, c przez decyzje | cyfry wygasaja po 10 s (test); podwojny Enter zostaje (C1) |
| D4 | zalatwiona | `protokol.cyfry()` (ASCII) w kluczach plytek, parametrach i `Content-Length` (test) |
| D5 | opisana | README: `plan_id` i `X-Laptop-Id` wypelnia program |
| D6 | zalatwiona | `MAX_WAZNY_S_ROLI` W 30 s, P 600 s, wartosc w odpowiedzi i `GET /stan` (test) |
| D7 | a, b zalatwione (czytane) | przerwa 2 s po bledzie `grab()`, logi watku klawiatury; c-f do C1 |
| D8 | znana | do C1; dochodzi: tresc czytana przed sprawdzeniem klucza (D-N10) |
| D9 | b, c zalatwione; a znana | `start_id` wymagany (test); `powtorzony` = plan w pamieci (P2) |
| D10 | zalatwiona | K4: mediana < 100 ms + maks < 250 ms w czasie rzeczywistym, kryterium < 100 ms dowiedzione testem z czasem sztucznym, sprawdzenie klatek SILNIEJSZE (kazda klatka po polozeniu plytki 5); uczciwe - ocena w pkt 4 |
| D11 | zalatwiona | `kolejnosc`, `kuwety[].prac`, `plytki[].uklad` = 400 `nieznane_pole` (test) |
| D12 | zalatwiona | rozdzial "Runda 2" w raporcie; drobna nieprecyzyjnosc liczby testow (D-N13) |

Testy: 44 testy rundy 1 -> 63 (43 zostaly, 1 zastapiony: `test_usun_po_zdjeciu_...` -> `test_p3_...`, 1 przemianowany
`test_skanowanie_...`; 20 nowych). Zmiany testow rundy 1 sprawdzone w diffie: kazda wynika z udokumentowanej zmiany
zachowania (Zamknij piec w 2 krokach, `PUT /tryb` usuwa plan, brak `PUT /tryb wynik`, brak `GET /stan.laptop`,
`konflikt_wersji` przeniesiony na koniec, bo teraz gasi); jedyne poluzowanie to K4 (D10, opisane). Po czerwonym
commicie testy zmieniono tylko o usuniecie pol D11 z budowania planow, czekanie na `plytka 0` w K4 i nowy test D11 -
bez oslabien.

## 2. Nowe uwagi

"Uruchomione" = `scen_r19b.py` na PC (numer scenariusza), "czytane" = analiza kodu.

| Nr | Waga | Plik:linia | Scenariusz (wejscie -> zly wynik) | Sprawdzone | Oczekiwane |
|---|---|---|---|---|---|
| P-N1 | P | `ramka/logika.py:326-328` (kasowanie tylko przy planie w pamieci), `:152-155` (wygasniecie nie pamieta zdjec), `:242-244` (sprawdzenie `zdarzenia_do` tylko dla zdarzen klawiatury); `ramka/README.md:156-158` ("laptop wysyla plan ponownie"), `:211-212` (po restarcie), `:274` ("ponowne pokazanie = nowy skan albo nowa wersja") | Decyzja 3 ("wieczorem wynik plytki kasowany przy zdjeciu zawsze") dziala tylko, gdy ramka ma plan w chwili zdjecia i tylko do kolejnej wersji. (a) Ramka W: plan v1 dla plytki 1 swieci; laptop milczy 31 s (Wi-Fi, uspienie) -> `plan_wygasl`; technik zdejmuje plytke 1, naklada nowe prace, kladzie z powrotem (zdarzenia `plytka 0/1` sa, ale planu nie ma, wiec nic sie nie kasuje); laptop wraca i zgodnie z README wysyla plan ponownie -> wynik STARYCH prac swieci pod nowymi. To samo po restarcie ramki (K6: "plan ponownie do 5 s") i po `blad_sprzetu` (README tylko "rozwazyc ponowny skan"). (b) Plan w pamieci, plytka 1 zdjeta i polozona; laptop wysyla v2 zbudowane PRZED zdarzeniem zdjecia (`zdarzenia_do` < nr zdjecia) albo plan kumulowany z wynikiem plytki 1 -> przyjety, swieci. | **Uruchomione (N1, N2):** (a) ponowny PUT v1 po wygasnieciu i zamianie prac -> `przyjety`, 18 px; v2 z aktualnym `zdarzenia_do` -> `przyjety`, 18 px; (b) v2 z `zdarzenia_do` sprzed zdjecia -> `przyjety`, 18 px. | README (kontrakt): ramka W - po zdarzeniu `plytka` z `poprzednia` = p (takze bez planu w pamieci, po `plan_wygasl`, `blad_sprzetu`, restarcie ramki) laptop NIE wysyla juz wyniku plytki p, tylko wynik nowego skanu tej plytki; pkt 6 i regule 5 przepisac odpowiednio; po restarcie ramki W - decyzja wlasciciela (zalecam: tylko plytki zeskanowane po restarcie). Ramka (obrona w glebi, ok. 10 linii): rola W pamieta nr ostatniego zdarzenia zdjecia kazdej plytki niezaleznie od planu; plan z plytka p i `zdarzenia_do` < tego numeru = 409 `zdarzenia_nieodebrane` (bez zmiany obrazu). Test N1/N2. |
| P-N2 | P | `ramka/logika.py:182-183` (`_zgas` zamyka wersje tylko planu w pamieci), `:228-229` (jedyna ochrona przed nowym polaczeniem: czas odbioru); `ramka/README.md:125-128` ("(b) ta sama wersja po zgaszeniu ... nic sie nie zapala"), `:268-271` (`plan_zgaszony` = "nie ponawiaj tej wersji"), `:139-141`; raport wykonawcy, odstepstwo 3 | (a) Plan v1 wygasl (laptop milczal), potem laptop wysyla `DELETE /plan` albo `PUT /tryb skanowanie` (plan juz pusty, wiec wersja v1 NIE zostaje zamknieta), potem ponowienie v1 z nowego polaczenia -> `przyjety`, swieci - wbrew README (b). Tylko `DELETE ?plan_id=` zamyka. (b) Znana luka: realna droga to zachowanie laptopa, nie sama siec - pakiet spozniony w juz przyjetym polaczeniu ochrona lapie (test przez siec), a spozniony SYN po rezygnacji laptopa nie da nowego polaczenia (laptop odpowie RST). Realne drogi: osobny watek / kolejka ponowien PUT /plan obok watku Spacji (wynik analizy skanu N ponawiany po `skanowanie` skanu N+1), biblioteka HTTP z automatycznym ponowieniem (np. `urllib3.Retry` ponawia PUT domyslnie), albo odczytanie `409 plan_zgaszony` jako "wyslij wersje + 1" (README pkt 4 tak brzmi). | **Uruchomione (N3, N4):** (a) po wygasnieciu: DELETE -> `brak_planu`, PUT v1 -> `przyjety`, 18 px; `skanowanie` -> PUT v1 `przyjety`, 18 px; `DELETE ?plan_id=p` -> 409 `plan_zgaszony`. (b) v2 nieprzyjeta, `skanowanie`, v2 z nowego polaczenia -> `przyjety`, tryb `wynik`, 18 px; S1 + ponowienie z `wersja` 2 -> `przyjety`, 18 px. | Kod: `_zgas` zamyka wersje ostatnio przyjetego planu takze po jego wygasnieciu (pamietac `ostatni_plan_id`; po samym `plan_wygasl` ta sama wersja nadal moze wrocic - tak chce README). README pkt 4: "`plan_zgaszony` = obraz zgaszony celowo; NIE wysylaj tej tresci ponownie w zadnej wersji; nowa wersja tylko z nowej decyzji (nowy skan, nowy stan)". Wymagania dla `indicate` (pkt 3). Zamkniecie luki po stronie ramki - do decyzji: (1) polecenie gaszace dodaje zdarzenie (np. `zgaszono`), a plan z `zdarzenia_do` mniejszym niz jego numer = 409 (plan zbudowany przed zgaszeniem nie zapali sie - wykorzystuje istniejacy mechanizm `zdarzenia_do`), albo (2) rosnacy numer polecenia laptopa wspolny dla PUT /plan, PUT /tryb, DELETE (propozycja rundy 1). Test N3/N4. |
| D-N1 | D | `ramka/serwer.py:91-94` | Czas "przyjecia polaczenia" jest brany w `setup()` watku obslugi, nie przy `accept()` w watku serwera; dwa polaczenia przyjete po kolei moga teoretycznie zostac obsluzone w odwrotnej kolejnosci watkow (PUT przyjety przed DELETE dostaje pozniejszy czas). Okno bardzo male (odczyt zadania zwalnia GIL). | Czytane. | Brac czas w watku serwera (`SerwerRamki.process_request` / `get_request`) i przekazac do obslugi. |
| D-N2 | D | `ramka/logika.py:228-233` | Spozniony PUT INNEGO `plan_id` (polaczenie przyjete przed nowszym planem, bez gaszenia pomiedzy) zastepuje nowszy plan - ochrona wersji dziala tylko w obrebie `plan_id`. Ograniczone limitem odczytu 15 s, wiec realne tylko przy dwoch planach w kilka sekund. | **Uruchomione (N15):** `skan-2` przyjety, potem `skan-1` (polaczenie wczesniej) -> `przyjety`, w pamieci `skan-1`. | Ochrona czasu odbioru wzgledem ostatniej zmiany planu (takze przyjecia), nie tylko gaszenia; albo README: laptop zmienia `plan_id` tylko po DELETE. |
| D-N3 | D | `ramka/logika.py:152-155`, `:469`; `ramka/README.md:83-85` | Po `plan_wygasl` tryb zostaje `wynik` (bez planu); `GET /stan` = `tryb: wynik`, `plan_id: null` - wbrew zdaniu "plan w pamieci i stan wynik to jedno". To samo dla planu W bez plytek (wszystkie zdjete). | **Uruchomione (N8).** | Wygasniecie ustawia `gotowa`; albo README opisuje `wynik` bez planu. |
| D-N4 | D | `ramka/logika.py:109-110`, `:541-547`; `ramka/README.md:156-158` | Pierscien "brak lacznosci" liczy kontakt DOWOLNEGO laptopa: rano wlasciciel planu milczy 300 s, drugi laptop odpytuje -> pierscien zielony, choc ramka pracuje na planie bez kontaktu z wlascicielem (README: "[cytat usuniety]"). | **Uruchomione (N7):** z laptopem B pierscien (0,255,0) w obu fazach; bez B miga (255,0,0) / (0,0,0). | Gdy jest plan - pierscien wg kontaktu z `plan_laptop`. |
| D-N5 | D | `ramka/logika.py:394-408`, `:160-162`; `ramka/README.md:198` | "Zamknij piec": (a) bez plytki na ramce daje zdarzenie (`plytka` 0), a README mowi "bez plytki klawisze nie daja zdarzen"; (b) Enter 5,01 s po `*` (napis "PIEC?" juz zniknal) jest zwyklym Enterem i POTWIERDZA biezaca kuwete - technik chcial zamknac piec, a kuweta zostaje odhaczona (kierunek ryzykowny: gniazda tej kuwety gasna). Anulowanie innym klawiszem i uplywem czasu, brak drogi jednym klawiszem - poprawne (test decyzji uruchomiony). | **Uruchomione (N9):** (a) `[('zamknij_piec', 0)]`; (b) `[('potwierdzenie', '3263')]`. | (a) poprawic README albo wymagac plytki; (b) po wygasnieciu pytania pomijac Enter przez ok. 1 s (albo do puszczenia klawisza). |
| D-N6 | D | `ramka/serwer.py:164-168` (405, `zly_parametr` przed tresc), `:175-181` (gasi tylko blad tresci), `:187-190` (500); `ramka/README.md:173` | Odrzucenia PUT /plan od wlasciciela, ktore NIE gasza: 400 `zly_parametr` (nieznany parametr w adresie), 405 (np. POST /plan), 500 `blad_wewnetrzny` (nieoczekiwany wyjatek w przyjmowaniu planu) - README mowi "400 ... = jak po DELETE". Odpowiedz gaszaca nie mowi wprost, ze zgaszono (laptop musi znac liste kodow; N14 - poprawny kod i sciezka pola). | **Uruchomione (N11, N14):** `PUT /plan?x=1` -> 400, plan zostaje; `POST /plan` -> 405, plan zostaje. 500 czytane. | Kazde odrzucenie PUT /plan i PUT /tryb od wlasciciela poza lista = zgas (takze 400 z adresu, 405, 500); w tresci bledu pole `"zgaszono": true/false`. |
| D-N7 | D | `ramka/program.py:118-123`, `:177-186` | Awaria przerywana (np. co drugi odczyt czujnikow wyjatek): `sprzet_dziala` po JEDNYM udanym obiegu, wiec ok. 1 para zdarzen na sekunde; laptop po kazdym `sprzet_dziala` wysyla plan, ktory gasnie przy nastepnym bledzie; dziennik 2000 przepelnia sie w ok. 17 min. Kierunek bezpieczny. | **Uruchomione (N12):** w ok. 60 s: 60 x `blad_sprzetu`, 59 x `sprzet_dziala`. | Histereza: `sprzet_dziala` po np. 2 s udanych obiegow; ograniczenie tempa zdarzen. |
| D-N8 | D | `ramka/logika.py:232-233`; `ramka/README.md:102-103` | Martwy stan po restarcie programu laptopa: ten sam `plan_id` (README: "data, rola, numer"), wersje od 1, ramka zna wersje 7 (zgaszona) -> zawsze 409 `plan_starszy`, a ani odpowiedz, ani `GET /stan` (po zgaszeniu `plan_wersja` = null) nie podaja wersji ramki. Ciemno (bezpiecznie), ale laptop nie wie, jak wyjsc. | **Uruchomione (N13).** | W odpowiedzi 409 `plan_starszy` / `plan_zgaszony` podac najwyzsza znana wersje; albo README: `plan_id` unikalny dla kazdego startu programu laptopa / licznik wersji trwaly. |
| D-N9 | D | `ramka/protokol.py:63-66` (`re.match` z `$`) | `$` dopuszcza koncowy znak nowej linii: `plan_id` "abc\n", kuweta "3263\n" (inna niz "3263", ale `int()` ja dopasuje), `start_id`, klucz w pliku z "\n" (wtedy kazde zadanie = 401 - bezpieczne). Liter nie przepuszcza (I7 bez zmian). | **Uruchomione (N10):** plan przyjety; `sprawdz_klucz` przyjmuje klucz z "\n". | `fullmatch` albo `\Z`. |
| D-N10 | D | `ramka/README.md:50-51`, `:316-318`; `ramka/serwer.py:151-156`; `ramka/program.py:177-186` | Dla C1: (a) `host` = konkretny adres IP przy DHCP albo starcie przed Wi-Fi = blad `bind` -> petla restartow systemd; przy `RestartSec=2` domyslny limit startow systemd (5 w 10 s) moze wylaczyc usluge na stale; (b) tresc zadania (do 64 KiB, przy zbyt duzej do 1 MiB) jest czytana PRZED sprawdzeniem klucza (rozszerza D8); (c) zawieszenie (nie wyjatek) `pokaz` / odczytu zatrzymuje petle z ostatnia klatka - P4 tego nie obejmuje. | Czytane. | (a) README: `After=network-online.target` + `Wants=`, `StartLimitIntervalSec=0`, albo `0.0.0.0` + zapora; (b) klucz przed odczytem tresci; (c) watchdog systemd (`WatchdogSec`, sygnal z petli). |
| D-N11 | D | `ramka/logika.py:116-121`, `:267-294` | Dwa laptopy: pozostawiony laptop A (wlasciciel), ktory dalej odpytuje, utrzymuje swoj plan bez konca, a laptop B nie moze nawet ZGASIC (DELETE i `PUT /tryb` = 409 `inny_laptop`). Zgaszenie jest zawsze bezpieczne. | **Uruchomione (N6):** B DELETE i `skanowanie` -> 409, 18 px swieci dalej. | DELETE i `PUT /tryb` od kazdego laptopa z kluczem dozwolone (ograniczac tylko PUT /plan); albo jasny komunikat w `indicate`. |
| D-N12 | D | `ramka/protokol.py:28` (`KASUJ_PO_ZDJECIU_ROLI["P"] = False`); `ramka/README.md:275-276` | Rano plan zyje, dopoki laptop odpytuje: gdy technik zaladuje te same plytki praca z nastepnego wsadu bez "Zamknij piec", ramka pokaze kuwety poprzedniego wsadu (bledna kuweta). Ramka tego nie odrozni. | Czytane. | README dla `indicate`: nowy wsad pieca = najpierw DELETE / nowa sesja; do decyzji wlasciciela - gorny wiek planu porannego niezalezny od kontaktu. |
| D-N13 | D | `ramka/czcionka.py:35`; `raporty/E3-A8-ramka_2026-11-17.md:106`; `ramka/README.md:178`; `ramka/protokol.py:18`; `ramka/logika.py:138-147, 245` | Drobiazgi: `"R":(` bez spacji (przypadkowa zmiana stylu); raport "44 z rundy 1 + 19 nowych" = faktycznie 43 + 20; README "odczyt drgajacy dluzej niz 30 ms = zdjecie" dotyczy tylko odczytu bez powrotu do numeru lezacej plytki (drganie 2 / 0 nie zdejmuje, tylko gasi); `protokol` zostaje 1 mimo niezgodnych zmian (laptop starszej wersji dostanie stale 400 = ciemno, kierunek bezpieczny); kazda nowa wersja planu kasuje wpisywane cyfry i pytanie "PIEC?". | Czytane; liczby testow policzone. | Poprawic przy okazji; `protokol` 2 albo zdanie "v1 = stan po rundzie 2". |

## 3. Maszyna stanow - odpowiedz na glowne pytanie

Gniazda swieca tylko przy: `tryb == wynik` (ustawia wylacznie przyjety plan), plan wazny (kontakt `plan_laptop`
w `plan_wazny_s`), plytka pewna i bez awarii, numer w `plan.plytki` (+ regula kuwet rano). Przeszedlem wszystkie
przejscia:

| Przejscie | Wynik | Ocena |
|---|---|---|
| DELETE, kazdy PUT /tryb, odrzucenie od wlasciciela, awaria | plan usuniety, wersja zamknieta, `zgaszenie` = teraz | dobrze; wyjatek: plan juz wygasly - wersja niezamknieta (P-N2 a) |
| spozniony PUT z polaczenia przyjetego przed zgaszeniem | 409 `plan_zgaszony` | dobrze (test przez siec); czas brany w watku obslugi (D-N1) |
| nowe polaczenie po zgaszeniu z wersja nigdy nieprzyjeta | przyjety | znana luka (P-N2 b) |
| wygasniecie `wazny_s` (W 30 s, P 600 s) | plan usuniety, `plan_wygasl`; ta sama wersja moze wrocic | zgodnie z README; tryb zostaje `wynik` (D-N3) |
| zdjecie plytki W | wynik plytki skasowany, wersja zamknieta | dobrze, ale nie bez planu w pamieci i nie wobec nowej wersji (P-N1) |
| zdjecie plytki P | plan zostaje | decyzja; ryzyko nowego wsadu (D-N12) |
| `blad_sprzetu` -> `sprzet_dziala` | plan usuniety, plany 409 do powrotu, potem tylko nowa wersja | dobrze; migotanie (D-N7), zawieszenie (D-N10 c) |
| restart (`start_id`) | plan tylko w RAM, stary plan 409 `inny_start` | dobrze; wznowienie W po restarcie (P-N1) |
| dwa laptopy | inny laptop 409 przy aktywnym wlascicielu, bez zmiany obrazu | dobrze; nie moze zgasic (D-N11); pierscien (D-N4) |
| drgajacy czujnik | gasi w tym samym obiegu, zapala po 30 ms; drganie bez powrotu > 30 ms = `plytka 0` | dobrze (testy) |
| odrzucenie tresci od wlasciciela | jak DELETE | dobrze; luki 405 / `zly_parametr` / 500 (D-N6) |

Wniosek: bez nowego `PUT /plan` nic sie nie zapala ponownie. Wszystkie znalezione drogi do starego obrazu
wymagaja `PUT /plan` od laptopa, ktory albo postepuje zgodnie z obecnym README (P-N1), albo ma typowa logike
ponowien (P-N2). Strona laptopa nie istnieje, wiec teraz jest najtanszy moment, zeby kontrakt to wykluczal.

## 4. Pozostale punkty zlecenia

- **Znana luka P1 (ocena):** realna, ale nie przez opoznienie w sieci - przez logike laptopa (watek ponowien,
  automatyczne ponowienie PUT w bibliotece HTTP, "409 plan_zgaszony -> wersja + 1"). Zamkniecie: minimum README
  (wymagania 3-5 w pkt 5) + test na `indicate`; trwale po stronie ramki: zdarzenie gaszenia + `zdarzenia_do`
  (bez nowego pola, laptop musi tylko odpytac zdarzenia po zgaszeniu przed zbudowaniem nowego planu) albo rosnacy
  numer polecenia. Przy okazji P-N2 (a) - jednolinijkowa zmiana w `_zgas`.
- **P2 skutki uboczne:** komplet srodkow jest: `skanowanie` / `analiza` / `blad` / `gotowa` + nowy plan wyzszej
  wersji; nowy plan ustawiany atomowo (bez mrugania). Martwy stan tylko przy restarcie laptopa z tym samym
  `plan_id` (D-N8).
- **P4 rano:** technik traci plan pieca na czas awarii; laptop po `sprzet_dziala` wysyla nowa wersje z
  `potwierdzone` / `wybrane` z WLASNEGO stanu (`GET /stan` po awarii ma puste listy - plan usuniety); N21: ta sama
  wersja 409 `plan_zgaszony`, v2 z `potwierdzone` przyjeta, biezaca kuweta poprawna. README pkt 4 mowi to tylko
  posrednio ("plan dopiero po `sprzet_dziala`") - dopisac jawnie (wymaganie 10).
- **P5 jednoznacznosc:** odpowiedz ma kod i sciezke pola (`plan.plytki.5.gniazda[0].px`), regula "ktore kody gasza"
  jest w README; brak jawnego pola `zgaszono` (D-N6).
- **P6:** pkt 1 tabeli. Dodatkowo strona laptopa potrzebuje miejsca na klucz - `[ramki]` w
  `ustawienia.przyklad.toml` go nie ma (zmiana modelu ustawien = opis dla czlowieka; klucz poza repo).
- **"Zamknij piec":** `*`, potem Enter w 5 s; inny klawisz (takze drugie `*`) i uplyw czasu anuluja, klawisz
  anulujacy nie dziala jak zwykly, bez planu nic, jednym klawiszem sie nie da (test uruchomiony). Uwagi D-N5.
- **Protokol README <-> kod <-> testy:** pola `GET /stan`, `/zdarzenia`, odpowiedzi PUT / DELETE / PUT /tryb,
  kody 400 / 401 / 409 i zdarzenia `blad_sprzetu` / `sprzet_dziala` zgodne z kodem i testami; niezgodnosci tylko
  D-N3, D-N5 a, D-N6, D-N13. Scisla walidacja wobec laptopa starszej wersji = stale 400 i ciemno (bezpiecznie).
- **K4:** uczciwe. Test z czasem sztucznym dowodzi logiki (gaszenie w 1. obiegu <= 15 ms, nowy obraz <= 45 ms,
  zadna klatka planu 4 pod plytka 5); test w czasie rzeczywistym mierzy mediane i maks z zapasem na pelny pytest,
  a sprawdzenie klatek jest silniejsze niz w rundzie 1. Na Pi czas `pokaz` (D7 c) dochodzi do I5 - raport to
  wpisuje do C1.
- **Higiena:** 12 zmienionych plikow + raport rundy 1; ASCII 100 %, koncowki LF (`git ls-files --eol`: i/lf w/lf);
  tryb atrapy - nowe importy tylko `hmac` (stdlib), test K9 przeszedl; skladnia 3.11: brak `match`, `type`,
  `except*`, f-napisow z zagniezdzonymi tymi samymi cudzyslowami; `modele_plytek/*/uklad.json` i `parametry.json`
  bez zmian (diff pusty); nazwiska: tylko 6 fikcyjnych do K8 (bez zmian z rundy 1), 0 w kodzie, README i raporcie.

## 5. Wymagania dla strony laptopa (`indicate`)

1. `X-Ramka-Klucz` w KAZDYM zadaniu, gdy ramka ma klucz; klucz w lokalnych ustawieniach laptopa (nowe pole w
   `[ramki]`, poza repo, bez wartosci w pliku przykladowym); 401 = blad konfiguracji, nie ponawiac w petli.
2. `X-Laptop-Id` staly, losowy przy instalacji, nigdy nazwa osoby; `plan_id` generowany przez program.
3. Jedna, szeregowa kolejka polecen na ramke (PUT /plan, PUT /tryb, DELETE) - zadnych rownoleglych watkow
   wysylajacych plan i tryb; przed poleceniem gaszacym anulowac wszystkie oczekujace i ponawiane PUT /plan.
4. Po decyzji o zgaszeniu NIE wysylac juz zadnego planu zbudowanego przed nia - takze z wyzsza wersja; biblioteka
   HTTP bez automatycznych ponowien PUT (np. `urllib3.Retry` domyslnie ponawia PUT).
5. `409 plan_zgaszony` = obraz zgaszony celowo: nie ponawiac tej tresci w zadnej wersji; nowa wersja tylko z nowej
   decyzji (nowy skan, nowy stan potwierdzen).
6. Wersja + 1 przy kazdej zmianie i po kazdym zgaszeniu; licznik wersji trwaly albo `plan_id` unikalny dla kazdego
   startu programu laptopa (D-N8).
7. Ramka W: po zdarzeniu `plytka` z `poprzednia` = p (takze w czasie bez planu, po `plan_wygasl`, `blad_sprzetu`,
   po restarcie ramki) nie wysylac juz wyniku plytki p - tylko wynik nowego skanu p; plan W bez `kuweta` i pol
   porannych; `wazny_s` W 30 s, P 600 s.
8. Spacja = `PUT /tryb skanowanie`; skan zablokowany / nieprzyjety = `PUT /tryb blad` albo `DELETE /plan`;
   polecenie gaszace ponawiac do skutku (200) - jest bezpieczne do powtorzenia.
9. Kody PUT /plan od wlasciciela: 400 / 411 / 413 / `plan_innej_ramki` / `konflikt_wersji` / `pole_tylko_rano` =
   ramka ZGASZONA (komunikat dla technika); `plan_starszy` / `plan_zgaszony` / `inny_start` / `inny_laptop` /
   `zdarzenia_nieodebrane` / `blad_sprzetu` = obraz bez zmian; `zdarzenia_nieodebrane` -> odpytac, przeliczyc,
   wyslac nowa wersje; `inny_start` -> `GET /stan`, kursor od zera.
10. `blad_sprzetu` -> komunikat; po `sprzet_dziala`: rano nowa wersja planu z `potwierdzone` / `wybrane` z
    wlasnego stanu laptopa (z `GET /stan` po awarii nie - listy sa puste); wieczorem ponowny skan.
11. `start_id` w kazdym `/zdarzenia`; `restart: true` / zmiana `start_id` -> kursor od zera; `utracone` > 0 ->
    `GET /stan` (`potwierdzone`, `wybrane`, gdy plan wazny).
12. `zamknij_piec` -> zamkniecie sesji pieca i `DELETE /plan`; nowy wsad pieca na tych samych plytkach = najpierw
    DELETE (D-N12).
13. Odpytywanie co najwyzej co min(25 s, `wazny_s` / 3); `409 inny_laptop` pokazac jasno (drugi laptop na
    stanowisku), nie zostawiac uruchomionego `indicate` na nieuzywanym laptopie.
14. Do sprawdzenia na `indicate`: K6 (ponowny plan po restarcie ramki - z zastrzezeniem pkt 7 dla W) i K8 na calym
    ruchu.

## 6. Czego NIE sprawdzilem

- Niczego na prawdziwym sprzecie (`sprzet_rpi.py` tylko diff, `wygas()` przez `Clear()` - czy gasi przy awarii
  biblioteki, nie wiem); Pythona 3.11 w dzialaniu (tylko przeglad skladni i test `ast` z paczki).
- Pelnego pytest (wynik wykonawcy 743 / 8 / 0) - zgodnie z ograniczeniem; `test_ramka.py` uruchomiony na `fe7dac1`
  i na `45f959f`.
- Scenariuszy przez prawdziwa siec z opoznieniami: N1-N21 na logice z czasem sztucznym (kolejnosc wywolan jak przy
  spoznionym pakiecie, `t_odbioru` podawany jawnie), przez serwer tylko N11. Wyscigu watkow D-N1 nie odtwarzalem.
- Obciazenia serwera, wolnych klientow i limitu polaczen (D8), zachowania systemd (D-N10 a) - tylko czytanie.
- `kalibracja.py`, `test_led.py`, `obraz.py` (bez zmian w rundzie 2) - nie przegladalem ponownie; wygladu marginesu
  ("PIEC?", nowe litery C, E, I, P) nie ocenialem wizualnie.
- Strony laptopa nie ma - wymagania z pkt 5 sa do potwierdzenia przez wykonawce 2 i wlasciciela (szczegolnie
  zachowanie ramki W po restarcie i wiek planu porannego).
