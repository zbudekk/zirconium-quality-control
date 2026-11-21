# Program ramki swietlnej (E3-A8, czesc "ramka")

Program, ktory dziala w ramce swietlnej (Raspberry Pi 4 + matryca 64 x 64) albo na atrapie
sprzetu (bez elektroniki). Laptop stanowiska wysyla ramce plan diod, ramka zapala gniazda pod
plytka, czyta numer plytki z czujnikow Halla i (ramka poranna) klawisze klawiatury numerycznej.
Strona laptopa (`stanowisko/indicate.py`, `stanowisko/ramka_protokol.py`) jest w innej paczce;
ten plik jest dla niej kontraktem (rozdzial "Protokol v1").

Decyzje wlasciciela (17.11.2026): DW8 = HTTP + JSON z biblioteki standardowej, laptop odpytuje
ramke, bez WebSocket; DW9 = laptop wysyla gotowe bloki pikseli dla plytki o danym numerze,
kalibracja diod w osobnym pliku lokalnym, `modele_plytek/*/uklad.json` bez zmian; skan
zablokowany albo nieprzyjety nie moze zostawic swiecacych gniazd (jednoznaczne "zgas",
limit waznosci planu). W sieci i w logach ramki tylko numery gniazd, plytek i kuwet, kolory.
Runda 2 (recenzja PR #19): kazde odrzucenie i kazda niepewnosc = gniazda ciemne - rozdzial
"Zasady bezpieczenstwa wskazan"; decyzje robocze koordynatora - rozdzial "Decyzje robocze".
Runda 3 (rozstrzygniecie koordynatora - ramka nie polega na poprawnym zachowaniu laptopa): kazde
zdarzenie, ktore gasi albo uniewaznia obraz, ma numer w dzienniku ramki, a plan jest przyjmowany TYLKO
z `zdarzenia_do` rownym numerowi ostatniego zdarzenia ramki - regula `zdarzenia_do` w "Zasadach
bezpieczenstwa wskazan"; wymagania dla laptopa - rozdzial "Wymagania dla strony laptopa".

Zgodnosc: kod pakietu nie uzywa skladni ani modulow nowszych niz **Python 3.11** (Raspberry Pi
OS Bookworm). Poza `sprzet_rpi.py` importuje tylko biblioteke standardowa (sprawdza test K9).

## Pliki

| Plik | Rola |
|---|---|
| `logika.py` | stan ramki, plan, dziennik zdarzen, klawiatura, reguly "co swieci", klatka 64 x 64 (bez sprzetu i sieci) |
| `protokol.py` | stale, limity, walidacja tresci zadan, kody bledow |
| `serwer.py` | serwer HTTP (`http.server`), zasoby `/stan`, `/zdarzenia`, `/plan`, `/tryb` |
| `program.py` | petla sprzetu (10 ms), odbijanie czujnikow, awaria sprzetu, start / stop, konfiguracja, wiersz polecen |
| `obraz.py`, `czcionka.py` | klatka RGB, pierscien stanu, napisy 5 x 7 na marginesie |
| `sprzet.py` | interfejs sprzetu (z `wygas` - wygaszenie awaryjne), odbijanie odczytu czujnikow (niesymetryczne) |
| `sprzet_atrapa.py` | sprzet w pamieci: `poloz_plytke(n)`, `nacisnij(k)`, `klatka`, `historia` |
| `sprzet_rpi.py` | Raspberry Pi: rgbmatrix, gpiozero (Hall GPIO 19 / 25 / 8), evdev - NIE uruchamiany w E3-A8 |
| `kalibracja.py` | plik kalibracji diod (format, walidacja, wartosci startowe z `uklad.json`) |
| `test_led.py` | narzedzie "test LED" wg pliku kalibracji |
| `../narzedzia/atrapa_ramki.py` | atrapa ramki w sieci lokalnej (osobny proces albo z kodu) |
| `../testy/test_ramka.py` | testy (atrapa, serwer na 127.0.0.1) |

## Uruchomienie

```
python -m ramka --rola P --sprzet atrapa                  # atrapa, 127.0.0.1:8765
python narzedzia/atrapa_ramki.py --rola W --port 0 --sterowanie   # atrapa sterowana przez HTTP
python -m ramka --sprzet rpi --konfiguracja /etc/ramka/ramka.json   # Raspberry Pi: rola, host, klucz z pliku
```
Wiersz polecen: `--rola W|P`, `--sprzet atrapa|rpi`, `--host`, `--port`, `--konfiguracja plik.json`,
`--sterowanie-atrapy` (zasoby `/atrapa/*`, tylko atrapa), `--gadatliwie`. Plik konfiguracji (JSON,
LOKALNY, poza repo; klucze jak pola `program.Konfiguracja`): `rola`, `host`, `port`, `klucz`, `sprzet`,
`limit_lacznosci_s` (30), `stabilnosc_s` (0,03), `odstep_drgan_s` (3 - drgania czujnikow, "Zasady
bezpieczenstwa"), `powrot_sprzetu_s` (3 - koniec awarii), `rodzina` (W: [1, 2, 3], P: [4, 5, 6]),
`piny_halla` ([19, 25, 8]), `jasnosc` (60), `obrot` (0/90/180/270), `lustro`, `mapowanie`
("adafruit-hat-pwm"), `spowolnienie_gpio` (4), `klawisz_zamknij_piec` ("KEY_KPASTERISK"). Nieznany
klucz = blad.
- `host`: adres nasluchu. Domyslnie **127.0.0.1 takze na Raspberry Pi** - ramka slucha w sieci tylko
  na adresie podanym w konfiguracji (np. adres ramki w sieci stanowiska; "0.0.0.0" = wszystkie).
- `klucz`: wspolny klucz laptopa i ramki (16-256 drukowalnych znakow ASCII bez odstepu, np. losowy
  `python -c "import secrets; print(secrets.token_hex(24))"`). Klucza nie wpisuje sie do repo ani do
  testow (testy losuja klucz). Ten sam klucz w ustawieniach laptopa.

## Protokol v1 (kontrakt dla strony laptopa)

Ramka = serwer HTTP/1.0 na porcie `[ramki] port` (8765) ustawien stanowiska; host `ramka-w.local`
albo `ramka-p.local`. Tresci JSON w UTF-8, odpowiedzi JSON z polem `"protokol": 1` (poza 401).
`"protokol": 1` = stan po rundzie 3 recenzji; zmiany rund 2 i 3 sa niezgodne z wczesniejszymi (strona
laptopa jeszcze nie istnieje; laptop wedlug starszego opisu dostaje 400 / 409 = ciemno).
Naglowki zadan laptopa:
- `X-Ramka-Klucz: <klucz>` - gdy ramka ma `klucz` w konfiguracji, wymagany w KAZDYM zadaniu (takze
  GET i `/atrapa/*`); brak albo inny klucz = **401 bez tresci**, zadanie nic nie zmienia i nie jest
  kontaktem laptopa (porownanie `hmac.compare_digest`; klucz sprawdzany z naglowkow PRZED odczytem
  tresci). Bez klucza w konfiguracji naglowek jest pomijany.
- `X-Laptop-Id: <id>` (1-40 znakow `[A-Za-z0-9._-]`, staly dla jednego programu laptopa, np. losowy
  przy instalacji - NIE nazwa osoby). Dla PUT i DELETE wymagany, dla GET zalecany (zapisuje kontakt
  laptopa). To porzadkuje dwa laptopy, NIE jest zabezpieczeniem (patrz "Siec i klucz").

### Zasoby

| Zadanie | Tresc / parametry | Odpowiedz 200 |
|---|---|---|
| `GET /stan` | - | `rola`, `program`, `start_id`, `czas_s`, `plytka` (0-7, ustalona), `plytka_pewna`, `tryb`, `plan_id`, `plan_wersja`, `plan_wazny_s` (po przycieciu), `plan_pozostalo_s`, `plytki_planu`, `wlasciciel` (true / false - czy ramke obsluguje teraz jakis laptop; bez jego identyfikatora), `kuweta` (biezaca, rano), `potwierdzone` ([[plytka, kuweta], ...] w kolejnosci), `wybrane` ({plytka: kuweta}), `wpisywane`, `nr_zdarzenia`, `najstarsze_zdarzenie`, `lacznosc`, `blad_sprzetu`, `temp_c` |
| `GET /zdarzenia?od=N&czekaj=S&limit=L&start_id=X` | `od` = ostatni odebrany numer (0 na poczatku), `czekaj` = dlugie odpytywanie w s, `limit` 1-500 (100), `start_id` = znany start ramki - **wymagany** (bez = 400) | `start_id`, `restart` (true = inny start niz podany, zdarzenia od 1), `od`, `zdarzenia` [...], `nr_zdarzenia`, `najstarsze_zdarzenie`, `utracone`, `utracone_od`, `utracone_do` (zakres numerow wypchnietych z dziennika albo null) |
| `PUT /plan` | plan (nizej) | `wynik`: `przyjety` albo `powtorzony`, `plan_id`, `wersja`, `wazny_s` (po przycieciu do granicy roli), `start_id`, `nr_zdarzenia` (przy `przyjety` = numer zdarzenia `plan_przyjety`) |
| `DELETE /plan[?plan_id=X]` | - | `wynik`: `usuniety` albo `brak_planu`, `start_id`, `nr_zdarzenia` (= numer zdarzenia `zgaszono` tego polecenia); zgas: brak planu, stan `gotowa`, wersja ostatnio przyjetego planu (i planu X) zamknieta |
| `PUT /tryb` | `{"protokol": 1, "stan": "skanowanie"}`; stany: `gotowa`, `skanowanie`, `analiza`, `blad`, `test_led` (bez `wynik`) | `wynik`: `przyjety`, `stan`, `start_id`, `nr_zdarzenia` (= numer zdarzenia `zgaszono` tego polecenia); KAZDY `PUT /tryb` usuwa plan z pamieci i zamyka wersje ostatnio przyjetego planu |

`czekaj` ramka skraca do min(25 s, limit_lacznosci_s / 3, wazny_s / 3), zeby laptop odzywal sie
dosc czesto dla waznosci planu. Ramka odpowiada od razu, gdy `od` jest wiekszy niz `nr_zdarzenia`.
Kontakt laptopa liczy sie od POCZATKU zadania (laptop, ktory zniknal w trakcie czekania, nie
przedluza waznosci planu).

Stanu `wynik` nie ustawia sie przez `PUT /tryb` (usuniety w rundzie 2): stan `wynik` ma ramka tylko
z przyjetym, waznym planem - "plan w pamieci" i "stan wynik" to jedno (po wygasnieciu planu stan wraca
do `gotowa`). Pokazanie obrazu po raz drugi = nowa wersja planu.

### Plan (`PUT /plan`)

```
{"protokol": 1, "plan_id": "2026-11-17-p2", "wersja": 3, "start_id": "a1b2c3d4", "zdarzenia_do": 57,
 "wazny_s": 600, "tryb": "rano",
 "plytki": {"4": {"gniazda": [
     {"id": 2, "px": [43, 38, 3, 3], "kolor": "zielony", "kuweta": "3263"},
     {"id": 1, "px": [25, 45, 14, 3], "kolor": "bialy"}]}},
 "kuwety": [{"kuweta": "3263", "plytki": [4, 5]}],
 "potwierdzone": [[5, "3263"]], "wybrane": {"4": "3263"}, "braki": ["5120"]}
```
Plan wieczorny: tylko pola wspolne (`protokol` ... `tryb`: "wieczor", `plytki` z gniazdami BEZ `kuweta`).

| Pole | Znaczenie |
|---|---|
| `plan_id` | identyfikator planu (sesja pieca rano, wieczor), `[A-Za-z0-9._-]{1,40}`; wypelnia go program laptopa (data, rola, numer) - nigdy czlowiek, nigdy nazwa folderu ani nazwisko |
| `wersja` | liczba rosnaca w obrebie `plan_id`; kazda zmiana planu = nowa wersja; po kazdym zgaszeniu (DELETE, PUT /tryb, odrzucone polecenie - takze 409 `zdarzenia_nieodebrane`, awaria, zdjecie plytki wieczorem) kolejny obraz wymaga wyzszej wersji; najprosciej: kazde nowe wyslanie = wersja + 1 (ta sama wersja tylko przy ponowieniu po zgubionej odpowiedzi) |
| `start_id` | `start_id` ramki z `GET /stan` albo `/zdarzenia` (inny = 409 `inny_start`) |
| `zdarzenia_do` | numer ostatniego zdarzenia, ktore laptop ODEBRAL przez `/zdarzenia` i uwzglednil w planie; ramka przyjmuje plan tylko, gdy jest ROWNY numerowi jej ostatniego zdarzenia (mniejszy = 409 `zdarzenia_nieodebrane`, wiekszy = 400 `zle_pole`); nie przepisywac `nr_zdarzenia` z odpowiedzi ani z `GET /stan` |
| `wazny_s` | 1-3600 s: plan obowiazuje, dopoki laptop-wlasciciel odezwal sie w ciagu `wazny_s`; ramka przycina do granicy roli (W 30 s, P 600 s - "Decyzje robocze") i podaje wartosc w odpowiedzi |
| `tryb` | `wieczor` (ramka W) albo `rano` (ramka P); inny = 409 `plan_innej_ramki` |
| `plytki` | numer plytki (W: 1-3, P: 4-6) -> `{"gniazda": [...]}` |
| `gniazda[]` | `id` 1-64 (unikalne), `px` = [x, y, szer., wys.] z pliku kalibracji, cale w obszarze plytki (x, y 12..51), bez nakladania, najwyzej 48 gniazd i 800 pikseli na plytke; `kolor` z listy; `kuweta` - TYLKO rano (wieczorem = 400 `pole_tylko_rano`) |
| `kolor` | `czerwony` (sprawdz), `zielony` (bez uwag / biezaca kuweta), `zolty` (popraw ulozenie), `bursztyn` (poprawka), `bialy` (praca nieznana), `szary` (bez projektu), `niebieski`, `fioletowy` |
| `kuwety` | TYLKO rano: kolejnosc kuwet do rozkladania (ramka idzie po tej liscie): `kuweta` (`#?[0-9]{1,6}`), `plytki` (numery plytek z pracami kuwety - prawy margines) |
| `potwierdzone` | TYLKO rano: pary [plytka, kuweta] juz potwierdzone (w kolejnosci) - stan po restarcie / ponownym planie |
| `wybrane` | TYLKO rano: plytka -> kuweta wybrana recznie (numer z klawiatury) |
| `braki` | TYLKO rano: numery kuwet ze zleceniami z brakami (pokazywane po rozlozeniu plytki) |

Pola usuniete w rundzie 2 (= 400 `nieznane_pole`): `kolejnosc` (kolejnosc wynika z listy `kuwety`),
`kuwety[].prac` (liczba prac na marginesie liczona z gniazd lezacej plytki), `plytki[].uklad` (ramka
nie zna ukladow - DW9), `plytki[].usun_po_zdjeciu` (wieczorem kasowanie jest stale - P3).

Wynik przyjecia planu (kolejnosc sprawdzania; "gasi" = odrzucenie od laptopa-wlasciciela usuwa plan,
zamyka wersje i daje zdarzenie `zgaszono` - "Zasady bezpieczenstwa wskazan"):
1. blad tresci (400, w tym `pole_tylko_rano`), `plan_innej_ramki` (409) - gasi;
2. `brak_laptopa` / `zly_laptop` (400), `inny_start` (409) - bez zmiany obrazu;
3. `zdarzenia_do` wieksze niz numer ostatniego zdarzenia ramki - 400 `zle_pole`, gasi;
4. `inny_laptop` (409) - bez zmiany obrazu;
5. 409 `blad_sprzetu`: awaria sprzetu ramki (obraz juz zgaszony) - plan dopiero po zdarzeniu `sprzet_dziala`;
6. 409 `plan_zgaszony` - bez zmiany obrazu: (a) zadanie odebrane przez ramke (polaczenie przyjete) PRZED
   ostatnim poleceniem gaszacym, a przetworzone po nim (spozniony pakiet, wolne Wi-Fi), albo (b) wersja
   zamknieta przez zgaszenie (DELETE, PUT /tryb, odrzucenie, awaria, zdjecie plytki wieczorem - takze
   gdy plan juz wczesniej wygasl);
7. starsza `wersja` = 409 `plan_starszy` (bez zmiany obrazu); ta sama wersja, inna tresc = 409
   `konflikt_wersji` (gasi); odpowiedz 409 `plan_zgaszony` / `plan_starszy` / `konflikt_wersji` podaje
   `wersja_ramki` - najwyzsza wersje tego `plan_id` znana ramce (laptop po restarcie wie, od czego zaczac);
8. ta sama `plan_id` i `wersja` i ta sama tresc (bez `start_id` i `zdarzenia_do`), plan nietkniety
   w pamieci = 200 `powtorzony` (nic sie nie zmienia - bezpieczne ponowienie po zgubionej odpowiedzi,
   niezaleznie od `zdarzenia_do`);
9. `zdarzenia_do` mniejsze niz numer ostatniego zdarzenia ramki = 409 `zdarzenia_nieodebrane`, gasi
   (runda 3): laptop nie odebral czegos, co ramka zglosila (zdjecie plytki, zgaszenie, wygasniecie,
   przyjecie innego planu, klawisz) - odpytuje `/zdarzenia`, przelicza i wysyla nowa wersje;
10. przyjety plan ustawia stan `wynik` i daje zdarzenie `plan_przyjety`.

Plan zbudowany przed poleceniem gaszacym (DELETE, PUT /tryb) nie zapali sie nigdy - takze z NOWEGO
polaczenia, z wyzsza wersja i z automatycznego ponowienia biblioteki HTTP: polecenie dalo zdarzenie
`zgaszono`, a plan ma mniejsze `zdarzenia_do`. To samo dla planu sprzed zdjecia plytki, sprzed
wygasniecia, sprzed restartu ramki i sprzed przyjecia innego planu (spozniony PUT innego `plan_id`).

### Reguly "co swieci"

1. Gniazda swieca tylko w stanie `wynik` (= przyjety, wazny plan), gdy na ramce lezy plytka, ktorej
   numer jest w `plytki`, odczyt czujnikow jest ustalony (`plytka_pewna`) i sprzet dziala. Plytka
   spoza planu = zadne gniazdo + napis "<n> BRAK" + pomaranczowy pierscien ("brak planu").
2. Ramka wieczorna swieci WSZYSTKIE gniazda planu lezacej plytki (kolor z planu). Ramka poranna:
   gniazdo z `kuweta` swieci tylko, gdy to biezaca kuweta tej plytki i nie jest na niej potwierdzona;
   gniazdo bez `kuweta` (nieznana, sprawdz) swieci zawsze.
3. Biezaca kuweta plytki (rano) = wybrana recznie, a jesli brak - pierwsza z listy `kuwety`, ktora ma
   gniazda na tej plytce i nie jest na niej potwierdzona.
4. Stany ustawiane `PUT /tryb`: `skanowanie` (zolty pierscien), `analiza` (fioletowy), `gotowa`
   (niebieski; z lezaca plytka - "<n> BRAK"), `blad` (czerwony + "BLAD"), `test_led` (cala matryca
   kolejno czerwona, zielona, niebieska, biala co 1 s, po 8 s sam wraca do `gotowa`) - plan USUNIETY.
5. Waznosc: gdy laptop-wlasciciel planu nie odezwie sie przez `wazny_s` sekund (po przycieciu), ramka
   usuwa plan (zdarzenie `plan_wygasl`), stan wraca do `gotowa` i nic nie swieci. Rano laptop moze
   wyslac plan ponownie (po odebraniu `plan_wygasl`); wieczorem tylko wynik NOWEGO skanu (wymaganie 7
   dla laptopa). Rano (do 600 s) ramka bez sieci pracuje dalej na ostatnim planie (I1), pierscien miga
   na czerwono.
6. Margines: pierscien 1 px = stan ramki; ikona 3 x 3 z przodu po lewej = lacznosc z laptopem-
   wlascicielem (planu, a bez planu - ostatniego polecenia; bez wlasciciela - z dowolnym laptopem;
   zielona / czerwona); napis z przodu: rano "3263 3" (kuweta, liczba jej prac na tej plytce), wpisywane
   cyfry "32_", "?7777" (numer spoza planu, 3 s), "OK" albo "-5120" (braki) po rozlozeniu, "PIEC?"
   (czeka na Enter po "Zamknij piec"); wieczorem numer plytki; prawy margines = inne plytki biezacej
   kuwety; awaria sprzetu = czerwony pierscien + "BLAD".

### Zasady bezpieczenstwa wskazan (kiedy ramka gasi sama)

Zasada: KAZDE ODRZUCENIE I KAZDA NIEPEWNOSC = GNIAZDA CIEMNE. Bledne swiecenie moze skierowac
ukruszona prace do dalszej produkcji, ciemna ramka najwyzej kaze poczekac.

**Regula `zdarzenia_do` (runda 3).** Kazde zdarzenie, ktore gasi albo uniewaznia obraz, ma numer
w dzienniku ramki: `plytka` (zdjecie / zmiana plytki), `zgaszono` (DELETE, kazdy PUT /tryb, odrzucone
polecenie od wlasciciela), `plan_wygasl`, `blad_sprzetu`, `start` (restart - nowy `start_id`) oraz
`plan_przyjety` (nowy obraz zastepuje poprzedni). Plan jest przyjmowany TYLKO wtedy, gdy jego
`zdarzenia_do` jest rowne numerowi ostatniego zdarzenia ramki w chwili przyjecia - laptop potwierdza
w ten sposob, ze odebral wszystko, co ramka zglosila (takze zdjecie plytki i kazde zgaszenie). Plan
ze starszym `zdarzenia_do` = 409 `zdarzenia_nieodebrane` i gniazda ciemne. Ramka nie polega wiec na
tym, ze laptop pamieta o zgaszeniu: plan zbudowany przed nim nie przejdzie z zadnego polaczenia,
w zadnej wersji. Normalny przeplyw zbiega: laptop odpytuje, buduje plan z aktualnym `zdarzenia_do`,
plan przyjety; gdy w miedzyczasie zaszlo zdarzenie - 409, laptop odpytuje i wysyla ponownie (test:
pojedyncze zdarzenie = 2 proby). Zeby seria zdarzen nie zablokowala przyjecia planu na stale, ramka
ogranicza zdarzenia z drgan czujnikow i awarii przerywanej do 1 pary na `odstep_drgan_s` /
`powrot_sprzetu_s` (3 s).

Ramka gasi gniazda sama:

| Sytuacja | Co robi ramka | Jak wraca obraz |
|---|---|---|
| `DELETE /plan`, kazdy `PUT /tryb` | plan usuniety, wersja ostatnio przyjetego planu zamknieta (takze juz wygaslego), zdarzenie `zgaszono` | nowy plan, wyzsza `wersja`, aktualne `zdarzenia_do` |
| odrzucone polecenie od wlasciciela albo laptopa, ktory moglby nim zostac (PUT /plan, PUT /tryb, DELETE - kazda metoda poza GET / HEAD, bez `/atrapa/*`: 400 w tym `zly_parametr`, 404, 405, 411, 413, `plan_innej_ramki`, `konflikt_wersji`, `pole_tylko_rano`, `zly_stan`, `zdarzenia_nieodebrane`, 500) | plan usuniety, wersja zamknieta (jak po `DELETE`), stan `wynik` -> `gotowa`, inne stany bez zmian (np. `skanowanie` zostaje), zdarzenie `zgaszono` (`przyczyna` odrzucenie, `kod`), w odpowiedzi `zgaszono: true` | nowy plan, wyzsza `wersja` |
| plan zbudowany przed ostatnim zdarzeniem ramki (`zdarzenia_do` za male) | 409 `zdarzenia_nieodebrane`, gasi | laptop odpytuje i wysyla nowa wersje |
| spozniony `PUT /plan` (polaczenie przyjete przed zgaszeniem albo wersja zamknieta) | 409 `plan_zgaszony`, nic nie zapala | nowy plan (nowa decyzja), wyzsza `wersja` |
| laptop milczy dluzej niz `wazny_s` (W najwyzej 30 s, P 600 s) | plan usuniety, stan `gotowa`, zdarzenie `plan_wygasl` | rano plan ponownie; wieczorem tylko wynik nowego skanu |
| plytka zdjeta z ramki WIECZORNEJ (odczyt inny przez 30 ms) | wynik tej plytki skasowany na zawsze, wersja zamknieta | tylko wynik NOWEGO skanu (plan z `zdarzenia_do` >= numer zdjecia) |
| pierwszy odczyt czujnikow inny niz lezaca plytka (takze "brak plytki", drgania) | gniazda ciemne od razu (w tym samym obiegu petli 10 ms) | odczyt staly przez 30 ms |
| odczyt drgajacy (bez powrotu do numeru lezacej plytki) dluzej niz 30 ms | plytka uznana za zdjeta (zdarzenie `plytka` 0); takze gdy w tym samym obiegu petli ustalil sie juz nowy numer, ktory pojawil sie po pierwszym innym odczycie (4 -> 0 -> 5 przy rzadszym obiegu: zegar Windows, obciazenie) - najpierw 0, nowy numer w nastepnym obiegu (E3-A8p) | odczyt staly przez 30 ms |
| drgania wolniejsze niz 30 ms: powrot do numeru sprzed ostatniej zmiany (A -> 0 -> A, A -> B -> A) | powrot ustalany najwczesniej 3 s (`odstep_drgan_s`) po tej zmianie, do tego czasu ciemno | odczyt staly; zmiana na inny numer i zdjecie bez opoznienia |
| wyjatek w petli sprzetu (czujniki, klawiatura, matryca) | matryca od razu bez gniazd (czerwony pierscien + "BLAD", a gdy matryca zawodzi - wygaszenie), plan usuniety, zdarzenie `blad_sprzetu` (raz na awarie), plany 409 `blad_sprzetu` | po 3 s (`powrot_sprzetu_s`) obiegow bez wyjatku zdarzenie `sprzet_dziala`, potem nowy plan |
| restart programu ramki | plan tylko w RAM - brak planu, nowy `start_id`, zdarzenie `start` | rano plan z nowym `start_id`; wieczorem tylko plytki zeskanowane po restarcie |
| plytka spoza planu | "<n> BRAK", zadne gniazdo | - |
| `test_led` bez konca (zerwana siec) | po 8 s sam wraca do `gotowa` | - |

Bez zmiany obrazu zostaja tylko odrzucenia polecen starszych niz obraz tego samego planu, nie od
wlasciciela albo nie do tej ramki / tego startu: `plan_starszy`, `plan_zgaszony`, `inny_laptop`,
`inny_start`, `blad_sprzetu` (obraz juz zgaszony), `DELETE ?plan_id=` innego planu (409 `inny_plan`),
zadanie bez / ze zlym `X-Laptop-Id`, 401 (bez klucza) oraz odrzucony odczyt (GET).

### Klawiatura (ramka poranna) i zdarzenia

Enter = potwierdz biezaca kuwete na tej plytce (`potwierdzenie`) i przejdz do nastepnej;
Backspace = usun ostatnia wpisana cyfre, a bez cyfr cofnij ostatnie potwierdzenie na tej plytce
(`cofniecie`, kuweta znow biezaca); cyfry + Enter = wybierz kuwete (`kuweta_wybrana`; numer
dopasowany doslownie, potem z "#", potem bez zer wiodacych) albo `kuweta_nieznana`; wpisane cyfry
znikaja po 10 s od ostatniego klawisza. "Zamknij piec" w dwoch krokach: klawisz (domyslnie `*` na
klawiaturze numerycznej) pokazuje "PIEC?", Enter w ciagu 5 s = zdarzenie `zamknij_piec`; kazdy inny
klawisz anuluje (klawisz anulujacy nie dziala jak zwykly); po uplywie 5 s pytanie znika, a PIERWSZY
klawisz po tym czasie tylko kasuje stan `*` - Enter spozniony o chwile nie zamyka pieca i nie potwierdza
kuwety (nastepny klawisz dziala zwykle; stan `*` kasuje tez zmiana plytki i nowy plan). Bez planu albo
bez (pewnej) plytki klawisz `*` nic nie robi i nie ma zdarzenia `zamknij_piec`. Bez planu, bez plytki
albo przy niepewnym odczycie klawisze nie daja zdarzen. Ramka wieczorna ignoruje klawisze.

Zdarzenie: `{"nr": 57, "typ": "...", "czas_s": 12.345, ...pola}`; typy i pola: `start` (`rola`,
`program`), `plytka` (`plytka`, `poprzednia`; 0 = brak plytki albo odczyt drgajacy dluzej niz 30 ms),
`potwierdzenie` / `cofniecie` / `kuweta_wybrana` (`plan_id`, `plytka`, `kuweta`), `kuweta_nieznana`
(`plan_id`, `plytka`, `wpisano`), `zamknij_piec` (`plan_id`, `plytka`), `plan_wygasl` (`plan_id`),
`blad_sprzetu` (-), `sprzet_dziala` (-), `zgaszono` (`przyczyna`: `usuniecie` = DELETE, `tryb` = PUT
/tryb z polem `stan`, `odrzucenie` = odrzucone polecenie od wlasciciela z polem `kod`; `plan_id` planu,
ktory byl w pamieci, albo null), `plan_przyjety` (`plan_id`, `wersja`). Wieczorem zdarzenie `plytka`
z `poprzednia` = p (p w planie) oznacza, ze wynik plytki p zostal skasowany (`plytki_planu` w `GET /stan`).

Numeracja: `nr` rosnie o 1 od startu programu ramki (`start` = 1); `start_id` (8 znakow hex)
zmienia sie przy kazdym starcie. Laptop pamieta (`start_id`, ostatni `nr`) i pyta `od=nr` z
`start_id` - dostaje kazde zdarzenie dokladnie raz i w kolejnosci, takze po zgubionej odpowiedzi
(pyta ponownie o to samo `od`). Gdy ramka wystartowala ponownie, odpowiedz ma `restart: true`
i zdarzenia od 1; plan w RAM zniknal - rano laptop wysyla go ponownie z nowym `start_id` (i
`zdarzenia_do` nowego startu), wieczorem tylko wyniki plytek zeskanowanych po restarcie. Dziennik
trzyma 2000 ostatnich zdarzen. Gdy laptop pyta o numery juz wypchniete, odpowiedz podaje jawnie
`utracone` oraz zakres `utracone_od` .. `utracone_do`; laptop odczytuje wtedy `GET /stan`
(`potwierdzone`, `wybrane`), dobiera zdarzenia do konca i z tego buduje nastepna wersje planu.

### Dwa laptopy, ponowienia, bledy

Wlasciciel ramki = laptop ostatniego udanego PUT / DELETE / PUT /tryb. Inny laptop dostaje 409
`inny_laptop` na PUT i DELETE, dopoki wlasciciel odzywa sie co najwyzej `limit_lacznosci_s` (30 s);
potem moze przejac ramke. GET wolno kazdemu laptopowi (z kluczem, jesli ustawiony); kazdy laptop
odbiera wszystkie zdarzenia; `GET /stan` nie podaje identyfikatora wlasciciela (tylko `wlasciciel`
true / false). `DELETE /plan?plan_id=X` usuwa tylko plan X (inny = 409 `inny_plan`, obraz zostaje) -
spozniony DELETE nie skasuje nowszego planu. Znane: inny laptop nie moze tez ZGASIC ramki (DELETE /
PUT /tryb = 409 `inny_laptop`), dopoki pozostawiony laptop-wlasciciel odpytuje - `indicate` pokazuje
to jasno ("drugi laptop na stanowisku"), a nieuzywany laptop nie zostawia uruchomionego `indicate`.

| Status | Kod | Kiedy |
|---|---|---|
| 400 | `zly_json` | tresc nie jest obiektem JSON w UTF-8 (takze zbyt gleboko zagniezdzona) |
| 400 | `brak_pola`, `nieznane_pole`, `zle_pole`, `zly_protokol` | schemat planu / trybu |
| 400 | `pole_tylko_rano` | plan wieczorny z `kuweta` przy gniezdzie albo z `kuwety` / `potwierdzone` / `wybrane` / `braki` |
| 400 | `nieznane_gniazdo` | id gniazda nie 1-64, nie liczba albo powtorzone |
| 400 | `px_poza_plytka`, `px_nakladanie`, `za_duzo_pikseli`, `za_duzo_gniazd` | bloki pikseli |
| 400 | `zly_kolor`, `zla_kuweta`, `nieznana_kuweta`, `zla_plytka` | wartosci |
| 400 | `zly_stan`, `zly_parametr`, `brak_laptopa`, `zly_laptop`, `zla_dlugosc` | tryb (takze `wynik`), zapytanie (takze brak `start_id`), naglowki |
| 401 | (bez tresci) | ramka ma klucz, a zadanie nie ma zgodnego `X-Ramka-Klucz` |
| 404 / 405 | `nieznany_zasob` / `zla_metoda` | zasob, metoda |
| 409 | `inny_start`, `zdarzenia_nieodebrane`, `plan_starszy`, `plan_zgaszony`, `konflikt_wersji`, `inny_laptop`, `inny_plan`, `plan_innej_ramki`, `blad_sprzetu` | konflikty stanu |
| 411 / 413 | `brak_dlugosci` / `za_duza_tresc` | PUT bez Content-Length / ponad 64 KiB |
| 500 | `blad_wewnetrzny` | blad programu ramki (ramka dziala dalej; polecenie od wlasciciela gasi) |

Odpowiedz bledu: `{"protokol": 1, "blad": {"kod": "...", "opis": "...", "zgaszono": true|false}}`
(+ `wersja_ramki` przy `plan_starszy` / `plan_zgaszony` / `konflikt_wersji`, gdy ramka zna ten plan);
`zgaszono: true` = to odrzucenie zgasilo obraz (plan usuniety, zdarzenie `zgaszono`). Opis nigdy nie
powtarza wartosci z zadania. Nieznane pola sa odrzucane, a kuweta musi byc numerem - nazwa
folderu ani nazwisko nie przejdzie walidacji. Pola `plan_id` i `X-Laptop-Id` przyjmuja tez litery
(wracaja w `GET /stan` i zdarzeniach) - wypelnia je wylacznie program laptopa (np. "2026-11-17-p1",
losowy identyfikator instalacji), nigdy czlowiek. Wzorce dopasowuja caly napis - koncowy znak nowej
linii jest odrzucany. Log ramki: adres, metoda, zasob, status (bez tresci zadan i bez klucza).

### Siec i klucz (ograniczenie)

Bez klucza ramka NIE uwierzytelnia laptopa: kazde urzadzenie w tej samej sieci moze odczytac stan,
podmienic plan (np. czerwone na zielone), zgasic ramke albo zablokowac ja odpytywaniem (409
`inny_laptop`). `X-Laptop-Id` nie jest zabezpieczeniem. **Bez klucza wolno uzywac ramki tylko w sieci,
w ktorej sa wylacznie laptop stanowiska i ramki** (osobna siec albo hotspot laptopa, I13). W zwyklej
sieci firmowej: klucz w lokalnym pliku konfiguracji ramki i w ustawieniach laptopa, `host` = adres
ramki w tej sieci, zapora Raspberry Pi przepuszczajaca tylko adres laptopa (paczka C1). Klucz
chroni przed podmiana i odczytem przez obcych w sieci, ale ruch nie jest szyfrowany (HTTP): podsluch
widzi numery gniazd, plytek i kuwet (nie ma w nim danych osobowych) i sam klucz - dlatego siec
stanowiska ma byc zamknieta.

### Wymagania dla strony laptopa (`indicate`)

Ramka sama odrzuca plan zbudowany na starszym stanie (regula `zdarzenia_do`). Ponizsze wymagania
sa po to, zeby laptop nie wpadal w odrzucenia i zeby nigdy - takze zgodnie z protokolem - nie wyslal
starego wyniku jako nowego.

1. Start: `GET /stan` (z `X-Ramka-Klucz`, gdy ustawiony), potem w petli
   `GET /zdarzenia?od=<nr>&czekaj=<s>&start_id=<id>` z `X-Laptop-Id` (`start_id` zawsze); kursor
   (`start_id`, `nr`) przesuwany tylko po udanej odpowiedzi; odpytywanie co najwyzej co
   min(25 s, `wazny_s` / 3).
2. Klucz: `X-Ramka-Klucz` w KAZDYM zadaniu, gdy ramka ma klucz; klucz w lokalnych ustawieniach
   laptopa - nowe pole w `[ramki]` ustawien stanowiska (poza repo, bez wartosci w pliku przykladowym;
   zmiana modelu ustawien - do opisania wlascicielowi przed wdrozeniem); 401 = blad konfiguracji, nie
   ponawiac w petli. `X-Laptop-Id` staly, losowy przy instalacji (nigdy nazwa osoby); `plan_id`
   generuje program.
3. JEDNA szeregowa kolejka polecen do ramki (PUT /plan, PUT /tryb, DELETE) - zadnych rownoleglych
   watkow wysylajacych plan i tryb; przed poleceniem gaszacym anulowac wszystkie oczekujace PUT /plan.
4. ZADNYCH automatycznych ponowien PUT przez biblioteke HTTP (np. `urllib3.Retry` domyslnie ponawia
   PUT). Ponowienie tylko swiadome, po zgubionej odpowiedzi: ta sama tresc i wersja = 200 `powtorzony`,
   gdy plan dalej jest w pamieci. Polecenia gaszace (DELETE, PUT /tryb) ponawiac do skutku (200) - sa
   bezpieczne.
5. Plan: `zdarzenia_do` = numer ostatniego zdarzenia ODEBRANEGO przez `/zdarzenia` (nie `nr_zdarzenia`
   z odpowiedzi ani z `GET /stan`); po kazdym wlasnym poleceniu (PUT /plan, PUT /tryb, DELETE) odpytac
   `/zdarzenia` co najmniej do `nr_zdarzenia` z jego odpowiedzi, zanim powstanie nastepny plan; px
   z pliku kalibracji (`ramka.kalibracja.gniazda_planu`); `wazny_s` W 30 s, P 600 s (wiecej ramka
   przytnie); wieczorem gniazda BEZ `kuweta` i bez pol porannych; `wersja` + 1 przy kazdym nowym
   wyslaniu.
6. Odpowiedzi PUT /plan:
   - `zgaszono: true` w odpowiedzi bledu (400, 411, 413, `plan_innej_ramki`, `konflikt_wersji`,
     `pole_tylko_rano`, `zdarzenia_nieodebrane`, 500) = ramka ZGASZONA - komunikat dla technika albo
     nowa wersja;
   - 409 `zdarzenia_nieodebrane` = odpytac, przeliczyc plan (nowe potwierdzenia, zdjete plytki,
     zgaszenia) i wyslac nowa wersje; przy pojedynczym zdarzeniu wystarcza 1 ponowienie;
   - 409 `plan_zgaszony` = obraz zgaszony celowo: tej tresci NIE wysylac nigdy wiecej, w zadnej wersji
     (to nie jest "wyslij wersje + 1"); nowa wersja tylko z nowej decyzji (nowy skan, nowy stan
     potwierdzen);
   - 409 `plan_starszy` = ramka zna wyzsza wersje tego `plan_id` (`wersja_ramki` w odpowiedzi): po
     restarcie programu laptopa z tym samym `plan_id` nastepny plan ma `wersja_ramki` + 1 (i aktualne
     `zdarzenia_do`);
   - 409 `inny_start` = `GET /stan`, kursor od zera; `inny_laptop` = jasny komunikat "drugi laptop na
     stanowisku"; `blad_sprzetu` (409 albo zdarzenie) = komunikat dla technika, plan dopiero po
     `sprzet_dziala`.
7. Ramka W (wieczor): po zdarzeniu `plytka` z `poprzednia` = p (zdjecie plytki p - takze w czasie bez
   planu, po `plan_wygasl`, po `blad_sprzetu`) laptop wysyla dla plytki p tylko wynik NOWEGO skanu,
   nigdy ponownie stary; po `plan_wygasl` i po restarcie ramki W laptop NIE wznawia wyniku plytki
   zeskanowanej przed przerwa. Ramka przyjmie plan dopiero z `zdarzenia_do` >= numer zdjecia, ale nie
   wie, czy wynik jest nowy - to wymaganie jest po stronie laptopa.
8. Spacja = `PUT /tryb skanowanie` (usuwa poprzedni wynik); analiza = `analiza`; wynik = nowy plan
   (wyzsza wersja, `zdarzenia_do` po odebraniu zdarzen `zgaszono` tych polecen); skan zablokowany /
   nieprzyjety / blad = `PUT /tryb blad` albo `DELETE /plan`.
9. Rano: `zamknij_piec` (technik nacisnal `*` i Enter) -> zamkniecie sesji pieca i `DELETE /plan`;
   NOWY wsad pieca (nowa sesja pieca, takze na tych samych plytkach i bez "Zamknij piec") = najpierw
   `DELETE /plan` przy otwarciu sesji - inaczej ramka pokaze kuwety poprzedniego wsadu (ramka tego nie
   odrozni); `utracone` > 0 -> `GET /stan` (`potwierdzone`, `wybrane`); po `sprzet_dziala` nowa wersja
   z `potwierdzone` / `wybrane` z WLASNEGO stanu laptopa. Potwierdzenia z klawiatury ramka stosuje sama -
   laptop NIE wysyla nowej wersji po kazdym zdarzeniu klawiatury (tylko przy wlasnej zmianie: nowa sesja,
   braki, awaria, utracone zdarzenia); inaczej wyscig z kolejnym klawiszem = 409 i chwila ciemnosci.
10. Restart ramki (`restart: true`, inny `start_id`): kursor od zera; rano plan ponownie (nowy
    `start_id`, `zdarzenia_do` nowego startu); wieczorem pkt 7.
11. Do sprawdzenia na `indicate`: K6 (z zastrzezeniem pkt 7 dla W), K8 na calym ruchu, kolejka polecen
    (pkt 3-4).

### Decyzje robocze (do zmiany przez wlasciciela)

Przyjete przez koordynatora 17.11.2026 w rundzie 2; wszystkie w jednym miejscu: blok "DECYZJE
ROBOCZE" na poczatku `protokol.py`.

| Decyzja | Wartosc robocza | Stala |
|---|---|---|
| Najdluzszy czas trzymania planu bez kontaktu z laptopem (twarda granica ramki, wieksze `wazny_s` przycinane) | rano (P) 600 s, wieczorem (W) 30 s | `MAX_WAZNY_S_ROLI` |
| "Zamknij piec" | dwa kroki: `*`, potem Enter w ciagu 5 s; inny klawisz / uplyw czasu anuluje; bez planu nic | `CZAS_POTWIERDZENIA_ZAMKNIECIA_S` |
| Ta sama plytka z nowymi pracami | wieczorem wynik plytki kasowany przy jej zdjeciu zawsze; rano plan zostaje (plytki sa odkladane i brane ponownie) | `KASUJ_PO_ZDJECIU_ROLI` |
| Wpisane cyfry (wybor kuwety) | znikaja po 10 s od ostatniego klawisza | `CZAS_WPISYWANIA_S` |
| Wyglad marginesu ("3263 3", "PIEC?", prawy margines) | roboczy, ocena na zlozonej ramce (bramka G2) | `logika._tekst_przod_rano`, `obraz.py` |

Runda 3 (wartosci wykonawcy, w konfiguracji ramki): `odstep_drgan_s` = 3 s (powrot do numeru plytki
sprzed ostatniej zmiany najwczesniej po tym czasie - drgania czujnikow) i `powrot_sprzetu_s` = 3 s
(`sprzet_dziala` po tylu sekundach obiegow bez wyjatku) - "najwyzej 1 para zdarzen na kilka sekund".

## Kalibracja diod i "test LED"

Plik lokalny `dane/kalibracja_ramek.json` na laptopie (format w `kalibracja.py`): dla ramki W / P
i ukladu (np. `poranna`, `poranna_r54`, `okragla_ramkowa_poranna`) blok [x, y, w, h] pod kazdym
gniazdem. Wartosci startowe z geometrii `uklad.json` (blok 3 x 3 pod gniazdem okraglym, pas pod
otworami rynienki) dla ukladow plytek, ktore leza na ramkach - kwadratowych (R59 i R54) i okraglych
ramkowych n1-n6 (nizej); plytki okragle testowe n8 / n9 (`okragla_wieczorna`, `okragla_poranna`:
bez magnesow i rowka klucza, tylko do skanera) sa pomijane:
```
python -m ramka.kalibracja --domyslna --modele modele_plytek --wyjscie dane/kalibracja_ramek.json
python -m ramka.kalibracja --sprawdz dane/kalibracja_ramek.json
python -m ramka.kalibracja --uzupelnij dane/kalibracja_ramek.json --modele modele_plytek
python -m ramka.test_led --kalibracja dane/kalibracja_ramek.json --rola P --uklad poranna --sprzet rpi
```
Kalibracja na zlozonej ramce (przesuniecia blokow, `"zrodlo": "kalibracja"`) - paczka C2.

### Plytki okragle ramkowe n1-n6 (E3-O2)

Plytki okragle do ramek (R58): uklady `okragla_ramkowa_wieczorna` (plytki n1-n3, ramka W)
i `okragla_ramkowa_poranna` (n4-n6, ramka P). Maja te same gniazda, stozki znacznikow i srodek co
plytka kwadratowa R59 tego samego typu oraz te same numery (magnesy = ten sam kod), wiec:
- ramka nie odroznia plytki okraglej ramkowej od kwadratowej o tym samym numerze - uklad zna tylko
  laptop (ze skanu) i to on wysyla bloki pikseli wlasciwego ukladu;
- kalibracja startowa ukladu okraglego ramkowego = geometria jego `uklad.json`, `"zrodlo":
  "geometria"`; bloki sa ROWNE blokom kwadratu (19 z 19 i 24 z 24 gniazd - test
  `testy/test_okragle_ramka.py`). Polozenia diod pod wkladka okragla na zlozonej ramce nie mierzono:
  przed praca z plytkami okraglymi kalibracja na ramce jest obowiazkowa, tak samo jak dla kwadratow;
- uklady sa osobnymi wpisami pliku kalibracji (`ramki.W.okragla_ramkowa_wieczorna`,
  `ramki.P.okragla_ramkowa_poranna`) - kalibruje sie je osobno od kwadratow;
- plik kalibracji sprzed E3-O2 (same kwadraty) program stanowiska uzupelnia sam przy starcie
  (`indicate.wczytaj_kalibracje`): dopisuje TYLKO brakujace uklady z geometrii, wpisow istniejacych
  (takze `"zrodlo": "kalibracja"`) nie zmienia, kopie starego pliku zostawia obok
  (`kalibracja_ramek.json.przed_uzupelnieniem`) i pokazuje ostrzezenie w podpowiedzi paska ramek.
  To samo bez programu stanowiska (np. plik trzymany na Raspberry Pi dla `test_led`): polecenie
  `--uzupelnij` wyzej;
- test diod: `python -m ramka.test_led --kalibracja <plik> --rola W --uklad okragla_ramkowa_wieczorna`
  (19 gniazd), `--rola P --uklad okragla_ramkowa_poranna` (24 gniazda); uklad spoza pliku
  kalibracji tej ramki = "brak ukladu w kalibracji tej ramki", kod 1.

Numer plytki a ramka (program stanowiska, decyzja z 21.11.2026 - komunikat na ekranie, ramka ciemna,
skan przyjety, bez blokady): plytka o numerze spoza roli ramki (n4-n6 na W, n1-n3 na P), plytka inna
niz ta, ktorej wynik ma swiecic, oraz numer podany recznie inny niz odczytany z dolkow kodu -
opis w `opisy_modulow/indicate.md` ("Plytki okragle ramkowe").

## Instalacja na Raspberry Pi (opis - w E3-A8 nic nie wykonano)

Instrukcja krok po kroku dla czlowieka: `instrukcje/ramka_raspberry_pi.md`; gotowe pliki instalacji
(skrypt instalacji i kontroli, plik uslugi, wzor konfiguracji): katalog `ramka/rpi/` (oba z paczki
E3-O4). Ponizej skrot; przy roznicy obowiazuje instrukcja i pliki z `ramka/rpi/`.

1. Raspberry Pi Imager: Raspberry Pi OS Lite 64-bit (Bookworm, Python 3.11), SSH, Wi-Fi firmowe,
   nazwa hosta `ramka-w` albo `ramka-p` (dla `.local`).
2. `config.txt`: `dtparam=spi=off`, `dtparam=audio=off`; `cmdline.txt`: `isolcpus=3`; zworki
   Bonnetu E -> 8 i GPIO4-GPIO18 (plan_ramki_v2 8.1, 8.2).
3. Biblioteki sprzetu: `sudo apt install python3-gpiozero python3-evdev` oraz rpi-rgb-led-matrix
   skompilowana z powiazaniem Python (`make build-python`, instalacja w systemowym Pythonie).
4. Kopia katalogu `ramka/` do `/opt/ramka/ramka/`, plik `/etc/ramka/ramka.json` (lokalny, poza repo;
   np. `{"rola": "P", "sprzet": "rpi", "host": "<adres ramki w sieci stanowiska>", "klucz": "<losowy>"}`),
   prawa `chmod 600` (klucz). Bez `host` ramka slucha tylko na 127.0.0.1; bez `klucz` - patrz
   "Siec i klucz" (tylko siec z samym laptopem i ramkami).
5. Usluga systemd `/etc/systemd/system/ramka.service` (plik: `ramka/rpi/ramka.service`):
   `ExecStart=/usr/bin/python3 -m ramka --sprzet rpi --konfiguracja /etc/ramka/ramka.json`
   (`--sprzet rpi` jawnie: bez niego i bez pola `sprzet` w pliku ramka startuje z atrapa sprzetu),
   `WorkingDirectory=/opt/ramka`, `User=root` (rgbmatrix),
   `Restart=always`, `RestartSec=2`; `systemctl enable ramka`. Logi: journald (w RAM).
6. Karta tylko do odczytu (I13): `raspi-config` -> Performance -> Overlay File System; zmiana
   programu = wylaczenie nakladki, kopia plikow, wlaczenie. Plan i zdarzenia sa tylko w RAM.
7. Kontrola: `curl -H "X-Ramka-Klucz: <klucz>" http://ramka-p.local:8765/stan`; test LED: zatrzymac
   usluge, `python3 -m ramka.test_led ... --sprzet rpi`, uruchomic usluge. Od paczki E3-O4 `test_led`
   ma opcje `--konfiguracja <plik>` (ten sam plik co usluga: rola, obrot, lustro, jasnosc, piny) -
   opis w `instrukcje/ramka_raspberry_pi.md`.

Znane, do paczki sprzetowej C1 (recenzja rundy 2, D-N10 / D8): `host` = konkretny adres IP przy DHCP
albo przy starcie przed Wi-Fi konczy sie bledem `bind` i petla restartow, a domyslny limit startow
systemd (5 w 10 s) moze wylaczyc usluge na stale - w C1 `After=network-online.target` +
`Wants=network-online.target` i `StartLimitIntervalSec=0`, albo `0.0.0.0` + zapora przepuszczajaca
tylko adres laptopa; zawieszenie (nie wyjatek) `pokaz` / odczytu zatrzymuje petle z ostatnia klatka -
watchdog systemd (`WatchdogSec`, sygnal z petli); limit jednoczesnych polaczen i calkowity czas
odczytu zadania; zapora i prawa 600 pliku z kluczem.

## Czego nie sprawdzono bez sprzetu (paczka C1 / C2)

Matryca (rgbmatrix: orientacja `obrot` / `lustro`, jasnosc, migotanie, czas `pokaz` ok. 4096
`SetPixel`), czujniki A3144 przez gpiozero (polaryzacja, odbijanie przy zdejmowaniu plytki
po skosie, I5 < 100 ms na Pi, czestosc drgan i `odstep_drgan_s`), wspolpraca gpiozero z rgbmatrix na jednym GPIO, klawiatura evdev
(kody klawiszy konkretnej klawiatury, NumLock, klawisz "Zamknij piec", wypiecie odbiornika),
start po wlaczeniu < 60 s, praca 8 h, temperatura, karta tylko do odczytu, Wi-Fi firmowe i `.local`.
