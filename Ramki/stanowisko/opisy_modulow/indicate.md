# indicate - klient ramek swietlnych po stronie laptopa (E3-A8, czesc "indicate", 18.11.2026; rundy 2 i 3 po recenzji PR #28)

**Zamowienie (plan etapu 3, 3.6 i 4.1 E3-A8).** Laptop wysyla ramce porannej plan plytek pieca (gniazdo -> kuweta, kolory),
ramce wieczornej stan (Spacja) i kolory gniazd po analizie, odbiera zdarzenia ramek (numer plytki, potwierdzenia kuwet,
"Zamknij piec") - bez gubienia i bez powtorek, takze po przerwie w sieci i po restarcie ramki. Protokol = kontrakt
`ramka/README.md` ("Protokol v1", "Wymagania dla strony laptopa" 1-11). Podpiecie do programu (okno, `session`) robi A12.

**Pliki.** `stanowisko/indicate.py` (klient: watki, kolejka polecen, stan), `stanowisko/ramka_protokol.py` (budowa planow
z `SesjaRano.plan_plytek` i z wyniku skanu wieczornego, walidacja kodem ramki `ramka.protokol.sprawdz_plan`, walidacja
odpowiedzi, kolor ramki z `statusy.py`), `testy/test_indicate.py`. Tylko biblioteka standardowa + pakiet `ramka`.

## API dla A12 (w skrocie)

1. `ind = Indicate.z_ustawien(ust, na_zdarzenie=None)`; `ind.uruchom()` przy starcie programu, `ind.zatrzymaj()` przy
   zamknieciu (najwyzej ok. 1 s dla obu ramek; wysyla jeszcze oczekujace zgaszenie i zwraca {rola: czy doszlo} - False =
   ramka moze swiecic do konca waznosci planu, np. komunikat "nie kladz plytek"); brak ramki = `stan()["komunikat"]`.
2. Wieczor: Spacja -> `z = ind.wieczorna.skanowanie()` (zapamietac `z` przy skanie; skan bez Spacji: `z = znacznik()` -
   dziala jak Spacja: ramka gasi poprzedni wynik); start analizy (raz na skan) -> `analiza()`; wynik -> `wynik(numer_plytki,
   uklad, {gniazdo: ramka_protokol.kolor_ramki(status)}, z)`; skan zablokowany / blad -> `blad()`. Ramka W pokazuje TYLKO
   wynik ostatniego skanu; `znacznik()` w roli W NIE jest odczytem bez skutku (r2 D-N1).
3. Rano: po kazdej zmianie sesji pieca `ind.poranna.ustaw_plan_rano(rano.plan_plytek(kolejnosc))` (ta sama tresc = nic nie
   wysyla, nowy `plan_id` = najpierw `DELETE /plan`); "Zamknij piec" przyjete przez `session_rano.zamknij_piec` -> `zgas()`.
   Przy starcie programu: jest otwarty piec -> `ustaw_plan_rano(...)`; nie ma -> nic (plan zastany na ramce `indicate` gasi sam;
   `plan_plytek` bez otwartego pieca rzuca `BladSesji` - wtedy `zgas()`).
4. Zdarzenia: `klient.odbierz_zdarzenia()` z `QTimer` (albo `na_zdarzenie` - wolane w watku klienta, nie w watku Qt):
   `potwierdzenie` / `cofniecie` / `kuweta_wybrana` -> dziennik `zdarzenia` (gdy `plan_id` zdarzenia = otwarty piec),
   `zamknij_piec` -> `session_rano.zamknij_piec(plan_id=z["plan_id"])` **tylko gdy `z["nieaktualne"]` jest False**
   (`z_historii` False i `plan_id` = biezacy plan klienta; sesja i tak odmowi, gdy `plan_id` nie wskazuje otwartego pieca).
   `zamknij_piec` z `nieaktualne: True` (historia po restarcie programu albo inny piec) - tylko do dziennika, najwyzej
   pytanie do technika (r3 B-N1). **WYMAGANIE dla A12:** klucz unikalny `klucz_zdarzenia(z)` = (`start_id`, `nr`)
   zapisywany dla KAZDEGO odebranego zdarzenia (takze pominietego albo odrzuconego przez sesje), w tej samej transakcji
   co jego skutek; ponowna dostawa (historia, `z_historii: True`) = bez duplikatu i bez ponownego skutku.
5. Ekran: `klient.stan()` - `polaczona`, `blad` + `komunikat` (drugi laptop, zly klucz, awaria sprzetu ramki), `ostrzezenia`
   (kalibracja), `plytka`, `tryb_ramki`, `potwierdzone`, `plan_przyjety`, `pominiete`, `wstrzymane`. Po `inny_laptop`
   (drugi laptop na stanowisku) plan idzie dopiero po `klient.wznow()` - przycisk "przejmij ramke" po decyzji czlowieka.

## Klient jednej ramki - `KlientRamki(rola, host, port, *, laptop_id, kalibracja, klucz="", kursor=None, ...)`

- Dwa watki daemon. **Odpytywanie**: `GET /stan` przy pierwszym kontakcie (migawka: start ramki, plytka, plan,
  potwierdzenia, numer ostatniego zdarzenia N), potem `GET /zdarzenia?od=<nr>&czekaj=<s>&start_id=<id>`. Kursor (start_id,
  nr) przesuwany tylko po udanej odpowiedzi - w jednym uruchomieniu kazde zdarzenie dostarczone raz i w kolejnosci.
  **Po restarcie programu** (nowy klient) dostarczana jest cala historia biezacego startu ramki (dziennik ramki: 2000
  ostatnich), zdarzenia do N z `z_historii: True`; `kursor=(start_id, nr)` (ostatnie zdarzenie zapisane przez program) =
  tylko zdarzenia powyzej `nr` tego startu; duplikaty usuwa program po `klucz_zdarzenia`. **Polecenia**: jedna szeregowa
  kolejka; polecenie gaszace (`PUT /tryb`, `DELETE /plan`) zastepuje oczekujace polecenie i anuluje oczekujacy plan
  i ponowienie; gaszace ponawiane do skutku (200); plan budowany tuz przed wyslaniem (`zdarzenia_do` = ostatnie ODEBRANE
  zdarzenie, dopiero po odebraniu zdarzenia wlasnego poprzedniego polecenia), `wersja` + 1 przy kazdym wyslaniu; ta sama
  wersja i tresc tylko po zgubionej odpowiedzi; klient HTTP bez ponowien (wlasny, na gniezdzie: `Connection: close`).
- **Start (B2):** przy pierwszym kontakcie uruchomienia plan zastany na ramce, ktorego to uruchomienie nie ustawilo, jest
  gaszony (P: `DELETE /plan`, chyba ze program juz podal ten sam `plan_id`; W: `PUT /tryb gotowa`) - poprzednie uruchomienie
  z tym samym `X-Laptop-Id` nie podtrzymuje juz starego planu. **Stop (B2, P1):** `zatrzymaj(timeout=1.0)` probuje wyslac
  oczekujace polecenie gaszace (do 0,6 s, w watku daemon - takze rozwiazywanie nazwy hosta; wynik True / False), zamyka
  gniazda zadan w toku (na Windows `shutdown` nie przerywa `recv`; klient HTTP na zwyklym gniezdzie bez `makefile`, wiec
  `close()` zamyka je od razu - bez prywatnego API) i nie czeka dluzej niz `timeout`; kazde `uruchom()` ma wlasny sygnal
  stopu (watek poprzedniego uruchomienia niczego juz nie zmienia).
- Odpowiedzi na `PUT /plan`: 409 `zdarzenia_nieodebrane` -> zaraz `GET /stan` (numer ostatniego zdarzenia ramki po odmowie,
  z jej `zgaszono`), nowa wersja (przeliczone potwierdzenia, zdjete plytki), gdy kursor dojdzie do tego numeru - jedno
  ponowienie na zdarzenie, bez czekania na nowe dlugie odpytanie (r3 P-N1; bez `GET /stan`: dwa zdarzenia nowsze niz
  odrzucony plan); `plan_starszy` / `konflikt_wersji` -> wersja powyzej
  `wersja_ramki`; `plan_zgaszony` -> obraz tego uruchomienia zgaszony celowo: tej tresci nie wysyla (w zadnej wersji; nowa
  tresc albo restart / `sprzet_dziala` / `plan_wygasl` rano / utracone zdarzenia zdejmuja blokade), a zamknieta wersja
  z poprzedniego uruchomienia programu = jak `plan_starszy`; `inny_start` -> migawka; `inny_laptop` -> `blad` "inny_laptop",
  `wstrzymane` - BEZ ponawiania planu do `wznow()` (zgaszenia ponawiane co 2 s); `blad_sprzetu` -> migawka, plan po
  `sprzet_dziala`; 400 / 411 / 413 / 500 / `plan_innej_ramki` -> ramka zgaszona, `blad` "plan_odrzucony" (ta tresc
  zablokowana); 401 (takze na GET) -> `blad` "zly_klucz", klient przestaje pytac do `wznow()`. Gdy planu pieca nie da sie
  zbudowac (brak kalibracji, blad protokolu), poprzednia wersja na ramce jest gaszona.
- Restart ramki (inny `start_id`): kursor od zera; rano plan ponownie (nowy `start_id`, potwierdzenia laptopa) - do 5 s;
  wieczorem wyniki sprzed restartu znikaja (wraca tylko stan `skanowanie` / `analiza` / `blad`, jesli byl ostatni).
- Utracone zdarzenia (`utracone` > 0 w odpowiedzi): rano migawka `GET /stan` (potwierdzenia, wybrane) i nowa wersja planu;
  wieczorem wyniki ze znacznikiem sprzed utraconego zakresu niewazne; licznik `stan()["utracone"]` liczony wzgledem pozycji
  programu (kursor programu albo migawka pierwszego kontaktu).
- Metody: `uruchom()`, `zatrzymaj(timeout=1.0)`, `wznow()`, `stan()`, `odbierz_zdarzenia()`, `czekaj(warunek, timeout)`,
  `kursor`, `znacznik()`, `potwierdzone()`; P: `ustaw_plan_rano(plan_plytek, potwierdzone=None, wybrane=None) ->
  pominiete`, `zgas()`, `tryb(stan)` (np. `test_led` - rano zdejmuje plan jak `zgas`); W: `skanowanie()`, `analiza()`,
  `blad()`, `tryb(stan)`, `zgas()`, `znacznik()`, `wynik(numer, uklad, kolory, znacznik) -> "wyslany" | "bez_numeru" |
  "zla_plytka" | "brak_kalibracji" | "niewazny"`. Funkcja modulu `klucz_zdarzenia(z)`. Zle wywolanie (plan rano do ramki W,
  zly `plan_id`) = wyjatek; bledy ramki i sieci - tylko w `stan()`.

**Zdarzenie dla programu** = slownik zdarzenia z protokolu (`nr`, `typ`, `czas_s`, pola typu) + `rola` ("W" / "P") +
`start_id` + `z_historii` + `nieaktualne` (True tylko dla `zamknij_piec` z historii albo z `plan_id` innym niz biezacy
plan klienta - nie wykonywac). Typy: `start`, `plytka` (`plytka`, `poprzednia`), `potwierdzenie` / `cofniecie` /
`kuweta_wybrana` (`plan_id`, `plytka`, `kuweta`), `kuweta_nieznana` (`wpisano`), `zamknij_piec` (`plan_id`, `plytka`),
`plan_przyjety`, `plan_wygasl`, `zgaszono`, `blad_sprzetu`, `sprzet_dziala`. Para (`start_id`, `nr`) jest unikalna - po
restarcie ramki numery ida od 1. Kolejka dla `odbierz_zdarzenia()` ma najwyzej 10 000 zdarzen (nadmiar: `przepelnienie`).

**`stan()`**: `rola`, `adres`, `polaczona`, `start_id`, `kursor`, `plytka`, `tryb_ramki`, `plan_ramki` (plan_id na ramce),
`plan_id` / `wersja` (plan laptopa), `plan_przyjety`, `awaria`, `oczekuje`, `blad` (`brak_polaczenia` jako komunikat,
`zly_klucz`, `inny_laptop`, `blad_sprzetu` - takze po zdarzeniu ramki, `plan_odrzucony`, `plan_innej_ramki`, `zla_rola`,
`zla_odpowiedz`, `polecenie_odrzucone`, `brak_kalibracji`), `kod_bledu` (kod ramki), `komunikat` (tekst roboczy -
ostateczny ustala A12 w `statusy.py`), `ostrzezenia`, `potwierdzone`, `wybrane`, `utracone`, `pominiete`, `wyslane_plany`,
`przyjete_plany`, `bledy_sieci`, `wyniki` (W: numer plytki z waznym wynikiem - najwyzej jeden), `wstrzymane`,
`przepelnienie`.

## Ramka W - tylko ostatni skan, nigdy stary wynik (wymaganie 7, recenzja PR #19, runda 2 B1)

Ramka W pokazuje wylacznie wynik OSTATNIEGO skanu (rozstrzygniecie koordynatora po recenzji PR #28): `skanowanie()`,
`znacznik()` (= Spacja: `PUT /tryb skanowanie`, r3 P-N2), `blad()`, `zgas()`, `tryb()` poza "analiza" i "analiza" bez
poprzedzajacej Spacji / `znacznik()` zaczynaja nowy skan - poprzedni wynik jest kasowany, ramka gasnie od razu i wynik nie
wraca z kolejnym planem. Skan bez numeru, zablokowany, spoza rodziny W albo bez kalibracji ukladu (np. okragla testowa n8;
okragla ramkowa n1-n3 MA kalibracje i swieci - E3-O2, nizej) = ramka ciemna
i stan "gotowa" (nie zostaje "analiza"). Znacznik `Znacznik(start_id, nr, skan)` = start ramki, numer ostatniego zdarzenia
odebranego przez laptop w chwili Spacji i numer skanu; wynik jest wysylany tylko, gdy: to ostatni skan, ten sam start
ramki, po znaczniku NIE przyszlo zdjecie tej plytki (`plytka` z `poprzednia` = numer), `plan_wygasl`, `blad_sprzetu` ani
utrata zdarzen. Sprawdzane przy `wynik()` i przy KAZDYM budowaniu planu (takze po 409 `zdarzenia_nieodebrane` - wtedy
nic nie idzie, ramka "gotowa"). Znacznik bez polaczenia (`start_id` None) jest niewazny. Ramka W nie zna kuwet.

## Ramka P - plan pieca i potwierdzenia

`ustaw_plan_rano` bierze z `plan_plytek` tylko `plan_id`, `plytki`, `kuwety`, `braki`, `uklady`; `ramka_protokol.plan_rano`
dodaje `px` z kalibracji (rola P, uklad z `uklady`), `protokol`, `wersja`, `start_id`, `zdarzenia_do`, `wazny_s` 600,
`potwierdzone` i `wybrane` ze stanu laptopa (zdarzenia klawiatury + migawka `GET /stan`; filtrowane do plytek planu
i kuwet z listy), sprawdza plan kodem ramki. Pomija: plytki spoza 4-6, plytki bez kalibracji, kuwety niezgodne z `#?[0-9]{1,6}`
(gniazdo swieci wtedy "sprawdz" na czerwono, jak w `session_rano`), nieznane pola. Potwierdzen z klawiatury laptop nie
odsyla (ramka stosuje je sama); nowa wersja planu tylko przy wlasnej zmianie: inna tresc z sesji, restart ramki,
`plan_wygasl` tego planu, `sprzet_dziala`, utracone zdarzenia, zgaszenie przyjetego planu nie z biezacego polecenia.
Restart programu laptopa w trakcie pieca: migawka podaje potwierdzenia ramki (gdy plan na ramce jest wazny) - nowy klient
wysyla je dalej (gdy program poda ten sam piec po migawce, ramka gasnie na chwile i dostaje plan ponownie).

## Ustawienia, kalibracja, identyfikator

- `[ramki] port, wieczorna_host, poranna_host` (bez zmian) oraz nowe OPCJONALNE (plik bez nich wczytuje sie jak dotad):
  `[ramki] klucz = ""` (wspolny klucz z plikiem konfiguracji ramki, tylko w lokalnym `ustawienia.toml`; walidacja jak ramka,
  wartosc nie trafia do komunikatow), `[ramki] odpytywanie_s = 25.0` (0,5-25), `[sciezki] kalibracja_ramek =
  "dane/kalibracja_ramek.json"`.
- Kalibracja: plik lokalny (format `ramka/kalibracja.py`, `python -m ramka.kalibracja --domyslna ...`). Brak pliku =
  wartosci startowe z geometrii `modele_plytek/*/uklad.json` (w pamieci, plik nie jest zapisywany) + ostrzezenie; zly plik =
  ramki bez planow (ciemno; plan zastany gaszony przy pierwszym kontakcie) + ostrzezenie - program dziala dalej.
  E3-O2: plik poprawny, w ktorym brakuje ukladow majacych kalibracje startowa (plik sprzed E3-O2 nie ma
  `okragla_ramkowa_*`), jest przy starcie UZUPELNIANY - nizej "Plytki okragle ramkowe".
- `X-Laptop-Id`: losowy `lap-<16 hex>`, zapisany raz w `dane/ramki_laptop_id.txt` programu (niezaleznie od miejsca pliku
  kalibracji; `z_ustawien(..., katalog_danych=...)`), zapisywany trwale przy pierwszym uruchomieniu, staly dla instalacji -
  nie kopiowac do paczek ani obrazow dysku; nigdy nazwa osoby ani komputera. Gdy zapis sie nie uda (katalog tylko do
  odczytu) - `ostrzezenia` (samokontrola A11), bo identyfikator tylko na czas programu daje po szybkim restarcie
  "drugi laptop" na 30 s (r3 D-N3). W ruchu sieciowym tylko numery plytek, gniazd, kuwet i kolory (K8).

## Kryterium "dziala" (`testy/test_indicate.py`, atrapa ramki w osobnym procesie albo w procesie testu, HTTP 127.0.0.1)

| Kryterium | Test | Wynik (PC, 18.11.2026) |
|---|---|---|
| K1 plan plytki porannej 23 gniazda -> matryca 64 x 64 piksel po pikselu | `test_k1_...` (osobny proces) | 23 z 23 gniazd, w 6 krokach (5 kuwet + reszta), 0 roznych pikseli; nowy piec 23 naraz |
| K2 margines: kuweta i liczba prac | `test_k2_...` (osobny proces) | 5 z 5 napisow "kuweta liczba" + prawy margines, potem "-5120" |
| K5 5 potwierdzen bez sieci, 100 powtorzen | `test_k5_...` (osobny proces + posrednik TCP, 30 % zgubionych odpowiedzi) | 500 z 500, 0 powtorek, 0 luk, 0 planow po zdarzeniach klawiatury |
| K6 restart ramki -> plan ponownie do 5 s | `test_k6_...` (3 restarty procesu ramki) | ok. 0,1 s od startu ramki, 0,22 s od zabicia poprzedniego procesu ramki (prog 5 s) |
| K7 Spacja -> stan ramki W < 1 s, dwa procesy | `test_k7_...` | 10 z 10, maks ok. 10 ms; kolory gniazd = mapa (statusy.py) |
| K8 caly ruch testow bez nazw folderow i nazwisk | `test_zz_k8_...` (wlasny ruch + caly zapis pliku) | 0 trafien nazw; klucz tylko w naglowku X-Ramka-Klucz surowych zadan |
| PR #19 / B1: stary wynik na ramce W | `test_w1`-`test_w5`, `test_b1_*` (2) | zdjecie, `plan_wygasl`, restart ramki, 409, skan bez numeru, skan zablokowany: 0 starych wynikow |
| B2 plan po zamknieciu / restarcie programu | `test_b2_...` | `zgas()` + `zatrzymaj()` gasi ramke; nowe uruchomienie gasi zastany plan (P i W) |
| B3 potwierdzenia z czasu restartu programu | `test_b3_...`, `test_poranek_restart_programu_*` | historia z `z_historii`, po kluczu dokladnie 2 nowe potwierdzenia; z kursorem tylko nowsze |
| P1 zatrzymanie | `test_p1_...` | ponizej 1 s (odpytywanie w toku, gluchy host z oczekujacym zgaszeniem, `Indicate`) |
| P2 drugi laptop | `test_p2_...` | brak przejecia ramki przez 4 s ciszy wlasciciela; plan B dopiero po `wznow()` |
| r3 B-N1 "Zamknij piec" z historii / innego pieca | `test_bn1_...` | historia: `nieaktualne` True; biezacy piec: False |
| r3 P-N1 jedno ponowienie po 409 | `test_pn1_...` (25 powtorzen) | 2 PUT na zmiane w 25 z 25, maks ok. 30 ms do przyjecia |
| r3 P-N2 skan bez Spacji | `test_pn2_...` | `znacznik()` gasi ramke W od razu, stary wynik nie swieci |

Plus: poranek (nowy piec = DELETE przed planem, "Zamknij piec" raz + `zgas`, aktualizacja z zachowaniem potwierdzen, ta
sama tresc bez wysylki, zmiana pieca w trakcie wysylki, utracone zdarzenia), jedna kolejka polecen, klucz 401 bez petli,
drugi laptop, ustawienia, plan z prawdziwej `SesjaRano.plan_plytek`, walidacja komunikatow, pliki ASCII.

## Zalozenia i granice

- Kolory ramki wieczornej: kolumna `ramka` w `statusy.py` (A12 przekazuje status gniazda -> `kolor_ramki`).
- Potwierdzenia rano sa dziennikiem `indicate` (sesja ich nie przechowuje); zapis do bazy robi A12 (wymaganie z pkt 4 API).
  Gdy plan na ramce juz wygasl, a program laptopa wystartowal od nowa, stan potwierdzen zna tylko baza A12 - mozna go
  podac w `ustaw_plan_rano(..., potwierdzone=...)`.
- Stan `wybrane` laptopa jest lustrem zdarzen; Enter na wybranej, juz potwierdzonej kuwecie nie daje zdarzenia - wybor
  znika tylko na ramce (przy ponownym planie laptop pomija wybory kuwet juz potwierdzonych).
- Dwa laptopy: drugi (B) dostaje `blad` "inny_laptop" i nie wysyla planu do `wznow()`; nie moze tez zgasic ramki, dopoki
  pierwszy (A) odpytuje (zgaszenie ponawia co 2 s). Gdy A zamilknie na 30 s (np. przerwa Wi-Fi), B gasi ramke i staje sie
  wlascicielem; A po powrocie dostaje `inny_laptop` i tez czeka na `wznow()` - obie ramki ciemne, oba laptopy z komunikatem
  "drugi laptop", dopoki czlowiek nie wybierze laptopa (r3 D-N5; kierunek bezpieczny).
- Kalibracja (recenzja D6): brak pliku = geometria takze po C2 (bez sprawdzenia `zrodlo`); klucz kalibracji = nazwa
  katalogu modelu, `uklad` z sesji = nazwa z `[plytki]` - przy niestandardowym przypisaniu nazwa -> inny katalog px innego
  ukladu. Do decyzji wlasciciela / C2.
- Nazwa hosta ramki (`ramka-*.local`) rozwiazywana przy kazdym zadaniu (recenzja D14) - do sprawdzenia w C1 / T15.
- Nie sprawdzone bez sprzetu: Wi-Fi firmowe, `.local`, opoznienia prawdziwej sieci (T15, paczka C1).

## Plytki okragle ramkowe n1-n6 (E3-O2, 21.11.2026)

Uklady `okragla_ramkowa_wieczorna` (n1-n3, ramka W) i `okragla_ramkowa_poranna` (n4-n6, ramka P): te same gniazda, stozki,
srodek i numery co kwadrat R59 (R58). Ramka ich nie odroznia od kwadratu o tym samym numerze (zna tylko numer z magnesow);
uklad zna laptop ze skanu i wysyla bloki pikseli tego ukladu. Plytki okragle testowe n8 / n9 - bez zmian (bez kalibracji,
ramka ciemna).

**Kalibracja.** `ramka.kalibracja.domyslna` liczy wartosci startowe takze dla ukladow okraglych ramkowych
(`rola_ukladu`: pole `plate` = `okragla_ramkowa_wieczorna` -> W, `okragla_ramkowa_poranna` -> P, `shape` = `round`),
`zrodlo` = "geometria"; bloki sa rowne blokom kwadratu (19 z 19 i 24 z 24 gniazd). `indicate.wczytaj_kalibracje`: plik
poprawny, w ktorym brakuje ktoregos ukladu z kalibracji startowej, jest uzupelniany (`ramka_protokol.uzupelnij_kalibracje` ->
`ramka.kalibracja.uzupelnij_plik`): dopisywane sa TYLKO brakujace uklady, wpisy istniejace (takze `zrodlo` = "kalibracja")
zostaja bajtowo bez zmian, obok zostaje kopia starego pliku (`<nazwa>.przed_uzupelnieniem`, istniejacej kopii nie
nadpisuje), zapis przez plik tymczasowy i podmiane. Klient dostaje ostrzezenie ("Do pliku kalibracji ramek dopisano
uklady ... - przed praca z tymi plytkami skalibruj diody na ramce") - widac je w podpowiedzi paska ramek. Pliku nie da sie
zapisac = uklady dopisane tylko w pamieci programu + ostrzezenie ("plik kalibracji ramek nie zostal zapisany"). Brak
pliku i zly plik - jak dotad. Kalibracja na zlozonej ramce jest obowiazkowa przed praca (decyzja domyslna 6 z 21.11.2026) -
tak samo jak dla kwadratow; polozenia diod pod wkladka okragla nie mierzono.

**Wynik i plan.** `KlientRamki.wynik(n, "okragla_ramkowa_wieczorna", ...)` = "wyslany" dla n z 1-3 (przed E3-O2:
"brak_kalibracji"); plan poranny z `SesjaRano.plan_plytek` niesie plytki okragle ramkowe n4-n6 z `px` jak kwadrat (72 z 72
blokow rownych; wieczorem 57 z 57).

**Numer plytki a ramka - komunikaty kontrolera (decyzja domyslna 5 z 21.11.2026: komunikat na ekranie + ramka ciemna,
skan PRZYJETY, bez twardej blokady).** Robi to `kontroler_api.KontrolerSesji` (teksty: `statusy.KOMUNIKATY`), `indicate`
bez zmian zachowania:
- `plytka_nie_z_ramki` (id `plytka_nie_z_ramki:W` / `:P`): ramka podaje numer plytki (`stan()["plytka"]`) spoza swojej
  roli - n4-n6 (albo 7) na ramce W, n1-n3 (albo 7) na ramce P. Ramka i tak nie ma dla niej planu (ciemna).
- `plytka_inna_niz_skan` (ramka W): na ramce lezy plytka z 1-3 o numerze innym niz numer plytki z ostatniego skanu,
  ktorego wynik poszedl do ramki ("wyslany"). Ramka swieci tylko pod plytka z planu, wiec jest ciemna.
- `plytka_bez_skanu` (ramka P): na ramce lezy plytka z 4-6, ktorej nie ma w planie pieca wyslanym do ramki (nie byla
  skanowana albo ma w programie inny numer). Nie w czasie analizy / skanowania i nie dla plytki, ktora czeka na
  potwierdzenie ponownego skanu albo ma komunikat `numer_niezgodny`.
- `numer_niezgodny` (id `numer_niezgodny:<skan>`, przy plytce): numer podany recznie (`numer_zrodlo` = `podany`) inny niz
  WAZNY numer odczytany z dolkow kodu (`numer_z_dolkow` z pliku wyniku skanu, nalezacy do numerow ukladu). Wieczorem
  kontroler wola `wynik(None, ...)` (ramka ciemna jak dla skanu bez numeru), rano plytka nie idzie do planu
  (`plan_plytek(wstrzymane=...)`, `pominiete.numer_niezgodny`). `Plytka.numer_niezgodny` / `Plytka.numer_z_dolkow`.
  Numer z dolkow spoza numerow ukladu (np. 0 przy zaslonietych dolkach) to numer nieznany (pytanie o numer), nie niezgodnosc.
Komunikaty o plytce lezacej na ramce znikaja same, gdy przyczyna mija; zamkniety przez technika wraca dopiero przy innej
plytce / innym skanie. Skany, wyniki i "Zamknij piec" - bez zmian.

**Skad program zna numer plytki (stan faktyczny).** Numer z ramki (magnesy) NIE trafia do analizy skanu ani do
`skany.numer_plytki`: analiza dostaje `numer` = None (`aplikacja.Zlecenie.numer` nie jest nigdzie ustawiany), numer skanu
pochodzi z dolkow kodu (plytki okragle) albo z odpowiedzi technika na pytanie (kwadraty - dolki poza polem skanu). Numer
z ramki program zna dopiero, gdy plytka lezy na ramce (`StanRamki.plytka`), i uzywa go tylko do paska ramek oraz - od
E3-O2 - do komunikatow wyzej.

**Kryterium "dziala".** `testy/test_okragle_ramka.py` (atrapa ramki w procesie testu, obraz piksel po pikselu): bloki
72 z 72 i 57 z 57, stary plik kalibracji + 2 uklady, `test_led` na atrapie, komunikaty w 6 z 6 przypadkow (po 2 na
kazdy rodzaj), ramka ciemna i skan w bazie w kazdym.
