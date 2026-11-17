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
`limit_lacznosci_s` (30), `stabilnosc_s` (0,03), `rodzina` (W: [1, 2, 3], P: [4, 5, 6]), `piny_halla`
([19, 25, 8]), `jasnosc` (60), `obrot` (0/90/180/270), `lustro`, `mapowanie` ("adafruit-hat-pwm"),
`spowolnienie_gpio` (4), `klawisz_zamknij_piec` ("KEY_KPASTERISK"). Nieznany klucz = blad.
- `host`: adres nasluchu. Domyslnie **127.0.0.1 takze na Raspberry Pi** - ramka slucha w sieci tylko
  na adresie podanym w konfiguracji (np. adres ramki w sieci stanowiska; "0.0.0.0" = wszystkie).
- `klucz`: wspolny klucz laptopa i ramki (16-256 drukowalnych znakow ASCII bez odstepu, np. losowy
  `python -c "import secrets; print(secrets.token_hex(24))"`). Klucza nie wpisuje sie do repo ani do
  testow (testy losuja klucz). Ten sam klucz w ustawieniach laptopa.

## Protokol v1 (kontrakt dla strony laptopa)

Ramka = serwer HTTP/1.0 na porcie `[ramki] port` (8765) ustawien stanowiska; host `ramka-w.local`
albo `ramka-p.local`. Tresci JSON w UTF-8, odpowiedzi JSON z polem `"protokol": 1` (poza 401).
Naglowki zadan laptopa:
- `X-Ramka-Klucz: <klucz>` - gdy ramka ma `klucz` w konfiguracji, wymagany w KAZDYM zadaniu (takze
  GET i `/atrapa/*`); brak albo inny klucz = **401 bez tresci**, zadanie nic nie zmienia (porownanie
  `hmac.compare_digest`). Bez klucza w konfiguracji naglowek jest pomijany.
- `X-Laptop-Id: <id>` (1-40 znakow `[A-Za-z0-9._-]`, staly dla jednego programu laptopa, np. losowy
  przy instalacji - NIE nazwa osoby). Dla PUT i DELETE wymagany, dla GET zalecany (zapisuje kontakt
  laptopa). To porzadkuje dwa laptopy, NIE jest zabezpieczeniem (patrz "Siec i klucz").

### Zasoby

| Zadanie | Tresc / parametry | Odpowiedz 200 |
|---|---|---|
| `GET /stan` | - | `rola`, `program`, `start_id`, `czas_s`, `plytka` (0-7, ustalona), `plytka_pewna`, `tryb`, `plan_id`, `plan_wersja`, `plan_wazny_s` (po przycieciu), `plan_pozostalo_s`, `plytki_planu`, `wlasciciel` (true / false - czy ramke obsluguje teraz jakis laptop; bez jego identyfikatora), `kuweta` (biezaca, rano), `potwierdzone` ([[plytka, kuweta], ...] w kolejnosci), `wybrane` ({plytka: kuweta}), `wpisywane`, `nr_zdarzenia`, `najstarsze_zdarzenie`, `lacznosc`, `blad_sprzetu`, `temp_c` |
| `GET /zdarzenia?od=N&czekaj=S&limit=L&start_id=X` | `od` = ostatni odebrany numer (0 na poczatku), `czekaj` = dlugie odpytywanie w s, `limit` 1-500 (100), `start_id` = znany start ramki - **wymagany** (bez = 400) | `start_id`, `restart` (true = inny start niz podany, zdarzenia od 1), `od`, `zdarzenia` [...], `nr_zdarzenia`, `najstarsze_zdarzenie`, `utracone`, `utracone_od`, `utracone_do` (zakres numerow wypchnietych z dziennika albo null) |
| `PUT /plan` | plan (nizej) | `wynik`: `przyjety` albo `powtorzony`, `plan_id`, `wersja`, `wazny_s` (po przycieciu do granicy roli), `start_id`, `nr_zdarzenia` |
| `DELETE /plan[?plan_id=X]` | - | `wynik`: `usuniety` albo `brak_planu`; zgas: brak planu, stan `gotowa`, wersja planu (i planu X) zamknieta |
| `PUT /tryb` | `{"protokol": 1, "stan": "skanowanie"}`; stany: `gotowa`, `skanowanie`, `analiza`, `blad`, `test_led` (bez `wynik`) | `wynik`: `przyjety`, `stan`; KAZDY `PUT /tryb` usuwa plan z pamieci i zamyka jego wersje |

`czekaj` ramka skraca do min(25 s, limit_lacznosci_s / 3, wazny_s / 3), zeby laptop odzywal sie
dosc czesto dla waznosci planu. Ramka odpowiada od razu, gdy `od` jest wiekszy niz `nr_zdarzenia`.
Kontakt laptopa liczy sie od POCZATKU zadania (laptop, ktory zniknal w trakcie czekania, nie
przedluza waznosci planu).

Stanu `wynik` nie ustawia sie przez `PUT /tryb` (usuniety w rundzie 2): stan `wynik` ma ramka tylko
z przyjetym, waznym planem - "plan w pamieci" i "stan wynik" to jedno. Pokazanie obrazu po raz drugi
= nowa wersja planu.

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
| `wersja` | liczba rosnaca w obrebie `plan_id`; kazda zmiana planu = nowa wersja; po kazdym zgaszeniu (DELETE, PUT /tryb, odrzucony plan, awaria, zdjecie plytki wieczorem) kolejny obraz wymaga wyzszej wersji |
| `start_id` | `start_id` ramki z `GET /stan` albo `/zdarzenia` (inny = 409 `inny_start`) |
| `zdarzenia_do` | numer ostatniego zdarzenia ramki, ktore laptop przetworzyl i uwzglednil w planie |
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

Wynik przyjecia planu (kolejnosc sprawdzania):
- blad tresci (400, w tym `pole_tylko_rano`), `plan_innej_ramki`, `konflikt_wersji` = odrzucenie,
  ktore od laptopa-wlasciciela GASI obraz (stan jak po DELETE - "Zasady bezpieczenstwa wskazan");
- `inny_start` (409), `inny_laptop` (409) - bez zmiany obrazu;
- 409 `blad_sprzetu`: awaria sprzetu ramki - plan przyjmowany dopiero po zdarzeniu `sprzet_dziala`;
- 409 `plan_zgaszony`: (a) zadanie odebrane przez ramke (polaczenie przyjete) PRZED ostatnim
  poleceniem gaszacym, a przetworzone po nim (spozniony pakiet, wolne Wi-Fi), albo (b) ta sama wersja
  po zgaszeniu (DELETE, PUT /tryb, zdjecie plytki wieczorem) - nic sie nie zapala, nowy obraz = wyzsza
  `wersja`;
- starsza `wersja` = 409 `plan_starszy` (spozniony plan); ta sama wersja, inna tresc = 409
  `konflikt_wersji`;
- ta sama `plan_id` i `wersja` i ta sama tresc (bez `start_id` i `zdarzenia_do`), plan nietkniety
  w pamieci = 200 `powtorzony` (nic sie nie zmienia - bezpieczne ponowienie po zgubionej odpowiedzi;
  po wygasnieciu planu ta sama wersja jest przyjmowana od nowa);
- `zdarzenia_do` mniejsze niz numer ostatniego zdarzenia klawiatury tego `plan_id` na ramce =
  409 `zdarzenia_nieodebrane` (bez zmiany obrazu): laptop odpytuje `/zdarzenia`, uwzglednia je i
  wysyla nowa wersje (ramka nie nadpisze potwierdzen, o ktorych laptop nie wie);
- przyjety plan ustawia stan `wynik`.

Laptop NIE ponawia planu po wlasnym poleceniu gaszacym (DELETE, PUT /tryb): ramka odrzuca spoznione
kopie, ktore zastaly zgaszenie w drodze, ale zupelnie nowego polaczenia z dawnym planem (wersja nigdy
nieprzyjeta) nie odrozni od nowego polecenia.

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
   usuwa plan (zdarzenie `plan_wygasl`) i nic nie swieci; laptop wysyla plan ponownie. Rano (do
   600 s) ramka bez sieci pracuje dalej na ostatnim planie (I1), pierscien miga na czerwono.
6. Margines: pierscien 1 px = stan ramki; ikona 3 x 3 z przodu po lewej = lacznosc (zielona /
   czerwona); napis z przodu: rano "3263 3" (kuweta, liczba jej prac na tej plytce), wpisywane
   cyfry "32_", "?7777" (numer spoza planu, 3 s), "OK" albo "-5120" (braki) po rozlozeniu, "PIEC?"
   (czeka na Enter po "Zamknij piec"); wieczorem numer plytki; prawy margines = inne plytki biezacej
   kuwety; awaria sprzetu = czerwony pierscien + "BLAD".

### Zasady bezpieczenstwa wskazan (kiedy ramka gasi sama)

Zasada: KAZDE ODRZUCENIE I KAZDA NIEPEWNOSC = GNIAZDA CIEMNE. Bledne swiecenie moze skierowac
ukruszona prace do dalszej produkcji, ciemna ramka najwyzej kaze poczekac. Ramka gasi gniazda sama:

| Sytuacja | Co robi ramka | Jak wraca obraz |
|---|---|---|
| `DELETE /plan`, kazdy `PUT /tryb` | plan usuniety, wersja zamknieta | nowy plan, wyzsza `wersja` |
| odrzucony `PUT /plan` albo `PUT /tryb` od wlasciciela (400, 411, 413, `plan_innej_ramki`, `konflikt_wersji`, `pole_tylko_rano`, `zly_stan`) | jak po `DELETE` | nowy plan, wyzsza `wersja` |
| spozniony `PUT /plan` (odebrany przed zgaszeniem albo ta sama wersja po zgaszeniu) | 409 `plan_zgaszony`, nic nie zapala | nowy plan, wyzsza `wersja` |
| laptop milczy dluzej niz `wazny_s` (W najwyzej 30 s, P 600 s) | plan usuniety, zdarzenie `plan_wygasl` | laptop wysyla plan ponownie |
| plytka zdjeta z ramki WIECZORNEJ (odczyt inny przez 30 ms) | wynik tej plytki skasowany na zawsze, wersja zamknieta | nowy skan / nowa wersja planu |
| pierwszy odczyt czujnikow inny niz lezaca plytka (takze "brak plytki", drgania) | gniazda ciemne od razu (w tym samym obiegu petli 10 ms) | odczyt staly przez 30 ms |
| odczyt drgajacy dluzej niz 30 ms | plytka uznana za zdjeta (zdarzenie `plytka` 0) | odczyt staly przez 30 ms |
| wyjatek w petli sprzetu (czujniki, klawiatura, matryca) | matryca od razu bez gniazd (czerwony pierscien + "BLAD", a gdy matryca zawodzi - wygaszenie), plan usuniety, zdarzenie `blad_sprzetu`, plany 409 `blad_sprzetu` | po pierwszym udanym obiegu zdarzenie `sprzet_dziala`, potem nowy plan |
| restart programu ramki | plan tylko w RAM - brak planu, nowy `start_id` | laptop wysyla plan z nowym `start_id` |
| plytka spoza planu | "<n> BRAK", zadne gniazdo | - |
| `test_led` bez konca (zerwana siec) | po 8 s sam wraca do `gotowa` | - |

Bez zmiany obrazu zostaja tylko odrzucenia polecen starszych niz obraz, nie od wlasciciela albo nie do
tej ramki / tego startu: `plan_starszy`, `plan_zgaszony`, `zdarzenia_nieodebrane`, `inny_laptop`,
`inny_start`, `blad_sprzetu`, `DELETE ?plan_id=` innego planu (409 `inny_plan`), zadanie bez /
ze zlym `X-Laptop-Id` oraz 401 (bez klucza).

### Klawiatura (ramka poranna) i zdarzenia

Enter = potwierdz biezaca kuwete na tej plytce (`potwierdzenie`) i przejdz do nastepnej;
Backspace = usun ostatnia wpisana cyfre, a bez cyfr cofnij ostatnie potwierdzenie na tej plytce
(`cofniecie`, kuweta znow biezaca); cyfry + Enter = wybierz kuwete (`kuweta_wybrana`; numer
dopasowany doslownie, potem z "#", potem bez zer wiodacych) albo `kuweta_nieznana`; wpisane cyfry
znikaja po 10 s od ostatniego klawisza. "Zamknij piec" w dwoch krokach: klawisz (domyslnie `*` na
klawiaturze numerycznej) pokazuje "PIEC?", Enter w ciagu 5 s = zdarzenie `zamknij_piec`; kazdy inny
klawisz albo uplyw 5 s anuluje (klawisz anulujacy nie dziala jak zwykly); bez planu klawisz nic nie
robi. Bez planu, bez plytki albo przy niepewnym odczycie klawisze nie daja zdarzen. Ramka wieczorna
ignoruje klawisze.

Zdarzenie: `{"nr": 57, "typ": "...", "czas_s": 12.345, ...pola}`; typy i pola: `start` (`rola`,
`program`), `plytka` (`plytka`, `poprzednia`; 0 = brak plytki albo odczyt drgajacy dluzej niz 30 ms),
`potwierdzenie` / `cofniecie` / `kuweta_wybrana` (`plan_id`, `plytka`, `kuweta`), `kuweta_nieznana`
(`plan_id`, `plytka`, `wpisano`), `zamknij_piec` (`plan_id`, `plytka`), `plan_wygasl` (`plan_id`),
`blad_sprzetu` (-), `sprzet_dziala` (-). Wieczorem zdarzenie `plytka` z `poprzednia` = p (p w planie)
oznacza, ze wynik plytki p zostal skasowany (`plytki_planu` w `GET /stan`).

Numeracja: `nr` rosnie o 1 od startu programu ramki (`start` = 1); `start_id` (8 znakow hex)
zmienia sie przy kazdym starcie. Laptop pamieta (`start_id`, ostatni `nr`) i pyta `od=nr` z
`start_id` - dostaje kazde zdarzenie dokladnie raz i w kolejnosci, takze po zgubionej odpowiedzi
(pyta ponownie o to samo `od`). Gdy ramka wystartowala ponownie, odpowiedz ma `restart: true`
i zdarzenia od 1; plan w RAM zniknal - laptop wysyla go ponownie z nowym `start_id`. Dziennik
trzyma 2000 ostatnich zdarzen. Gdy laptop pyta o numery juz wypchniete, odpowiedz podaje jawnie
`utracone` oraz zakres `utracone_od` .. `utracone_do`; laptop odczytuje wtedy `GET /stan`
(`potwierdzone`, `wybrane`) i z tego buduje nastepna wersje planu.

### Dwa laptopy, ponowienia, bledy

Wlasciciel ramki = laptop ostatniego udanego PUT / DELETE / PUT /tryb. Inny laptop dostaje 409
`inny_laptop` na PUT i DELETE, dopoki wlasciciel odzywa sie co najwyzej `limit_lacznosci_s` (30 s);
potem moze przejac ramke. GET wolno kazdemu laptopowi (z kluczem, jesli ustawiony); kazdy laptop
odbiera wszystkie zdarzenia; `GET /stan` nie podaje identyfikatora wlasciciela (tylko `wlasciciel`
true / false). `DELETE /plan?plan_id=X` usuwa tylko plan X (inny = 409 `inny_plan`, obraz zostaje) -
spozniony DELETE nie skasuje nowszego planu.

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
| 500 | `blad_wewnetrzny` | blad programu ramki (ramka dziala dalej) |

Odpowiedz bledu: `{"protokol": 1, "blad": {"kod": "...", "opis": "..."}}`; opis nigdy nie
powtarza wartosci z zadania. Nieznane pola sa odrzucane, a kuweta musi byc numerem - nazwa
folderu ani nazwisko nie przejdzie walidacji. Pola `plan_id` i `X-Laptop-Id` przyjmuja tez litery
(wracaja w `GET /stan` i zdarzeniach) - wypelnia je wylacznie program laptopa (np. "2026-11-17-p1",
losowy identyfikator instalacji), nigdy czlowiek. Log ramki: adres, metoda, zasob, status (bez
tresci zadan i bez klucza).

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

### Kontrakt w skrocie (dla `indicate`)

1. Na starcie `GET /stan` (z `X-Ramka-Klucz`, jesli ustawiony), potem w petli
   `GET /zdarzenia?od=<nr>&czekaj=<s>&start_id=<id>` z `X-Laptop-Id` (`start_id` zawsze).
2. Zmiana `start_id` / `restart: true` = ramka wstala od nowa: kursor od zera, wyslij plan.
3. Plan: px z pliku kalibracji (`ramka.kalibracja.gniazda_planu`), `zdarzenia_do` = ostatni
   przetworzony `nr`, `wersja` + 1 przy kazdej zmianie i po kazdym zgaszeniu, `wazny_s` W 30 s, P
   600 s (wiecej ramka przytnie). Wieczorem gniazda BEZ `kuweta` i bez pol porannych.
4. 409 `zdarzenia_nieodebrane` / `inny_start` = odpytaj, przelicz, wyslij ponownie; `utracone` > 0 =
   odtworz potwierdzenia z `GET /stan`; `plan_zgaszony` = nie ponawiaj tej wersji (obraz zgaszony
   celowo); `blad_sprzetu` (zdarzenie albo 409) = komunikat dla technika, plan dopiero po
   `sprzet_dziala` (wieczorem rozwazyc ponowny skan - plytki mogly zmienic sie w czasie awarii).
5. Spacja = `PUT /tryb skanowanie` (usuwa poprzedni wynik), analiza = `analiza`, wynik = nowy plan
   (wyzsza wersja); skan zablokowany / nieprzyjety / blad = `PUT /tryb blad` albo `DELETE /plan`.
6. Wieczorem zdjecie plytki kasuje jej wynik na ramce; ponowne pokazanie = nowy skan albo nowa wersja.
7. "Zamknij piec": zdarzenie `zamknij_piec` (technik nacisnal `*` i Enter), laptop zamyka sesje pieca
   i wysyla `DELETE /plan`.

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

## Kalibracja diod i "test LED"

Plik lokalny `dane/kalibracja_ramek.json` na laptopie (format w `kalibracja.py`): dla ramki W / P
i ukladu (np. `poranna`, `poranna_r54`) blok [x, y, w, h] pod kazdym gniazdem. Wartosci startowe
z geometrii `uklad.json` (blok 3 x 3 pod gniazdem okraglym, pas pod otworami rynienki; plytki
okragle pomijane - nie pasuja do wkladki):
```
python -m ramka.kalibracja --domyslna --modele modele_plytek --wyjscie dane/kalibracja_ramek.json
python -m ramka.kalibracja --sprawdz dane/kalibracja_ramek.json
python -m ramka.test_led --kalibracja dane/kalibracja_ramek.json --rola P --uklad poranna --sprzet rpi
```
Kalibracja na zlozonej ramce (przesuniecia blokow, `"zrodlo": "kalibracja"`) - paczka C2.

## Instalacja na Raspberry Pi (opis - w E3-A8 nic nie wykonano)

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
5. Usluga systemd `/etc/systemd/system/ramka.service`: `ExecStart=/usr/bin/python3 -m ramka
   --konfiguracja /etc/ramka/ramka.json`, `WorkingDirectory=/opt/ramka`, `User=root` (rgbmatrix),
   `Restart=always`, `RestartSec=2`; `systemctl enable ramka`. Logi: journald (w RAM).
6. Karta tylko do odczytu (I13): `raspi-config` -> Performance -> Overlay File System; zmiana
   programu = wylaczenie nakladki, kopia plikow, wlaczenie. Plan i zdarzenia sa tylko w RAM.
7. Kontrola: `curl -H "X-Ramka-Klucz: <klucz>" http://ramka-p.local:8765/stan`; test LED: zatrzymac
   usluge, `python3 -m ramka.test_led ... --sprzet rpi`, uruchomic usluge.

## Czego nie sprawdzono bez sprzetu (paczka C1 / C2)

Matryca (rgbmatrix: orientacja `obrot` / `lustro`, jasnosc, migotanie, czas `pokaz` ok. 4096
`SetPixel`), czujniki A3144 przez gpiozero (polaryzacja, odbijanie przy zdejmowaniu plytki
po skosie, I5 < 100 ms na Pi), wspolpraca gpiozero z rgbmatrix na jednym GPIO, klawiatura evdev
(kody klawiszy konkretnej klawiatury, NumLock, klawisz "Zamknij piec", wypiecie odbiornika),
start po wlaczeniu < 60 s, praca 8 h, temperatura, karta tylko do odczytu, Wi-Fi firmowe i `.local`.
