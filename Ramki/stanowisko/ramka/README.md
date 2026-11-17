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

Zgodnosc: kod pakietu nie uzywa skladni ani modulow nowszych niz **Python 3.11** (Raspberry Pi
OS Bookworm). Poza `sprzet_rpi.py` importuje tylko biblioteke standardowa (sprawdza test K9).

## Pliki

| Plik | Rola |
|---|---|
| `logika.py` | stan ramki, plan, dziennik zdarzen, klawiatura, reguly "co swieci", klatka 64 x 64 (bez sprzetu i sieci) |
| `protokol.py` | stale, limity, walidacja tresci zadan, kody bledow |
| `serwer.py` | serwer HTTP (`http.server`), zasoby `/stan`, `/zdarzenia`, `/plan`, `/tryb` |
| `program.py` | petla sprzetu (10 ms), odbijanie czujnikow, start / stop, wiersz polecen |
| `obraz.py`, `czcionka.py` | klatka RGB, pierscien stanu, napisy 5 x 7 na marginesie |
| `sprzet.py` | interfejs sprzetu, odbijanie odczytu czujnikow |
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
python -m ramka --rola P --sprzet rpi --konfiguracja /etc/ramka/ramka.json   # Raspberry Pi, 0.0.0.0:8765
```
Wiersz polecen: `--rola W|P`, `--sprzet atrapa|rpi`, `--host`, `--port`, `--konfiguracja plik.json`,
`--sterowanie-atrapy` (zasoby `/atrapa/*`, tylko atrapa), `--gadatliwie`. Plik konfiguracji (JSON,
klucze jak pola `program.Konfiguracja`): `rola`, `host`, `port`, `sprzet`, `limit_lacznosci_s` (30),
`stabilnosc_s` (0,03), `rodzina` (W: [1, 2, 3], P: [4, 5, 6]), `piny_halla` ([19, 25, 8]),
`jasnosc` (60), `obrot` (0/90/180/270), `lustro`, `mapowanie` ("adafruit-hat-pwm"),
`spowolnienie_gpio` (4), `klawisz_zamknij_piec` ("KEY_KPASTERISK"). Nieznany klucz = blad.

## Protokol v1 (kontrakt dla strony laptopa)

Ramka = serwer HTTP/1.0 na porcie `[ramki] port` (8765) ustawien stanowiska; host `ramka-w.local`
albo `ramka-p.local`. Tresci JSON w UTF-8, odpowiedzi zawsze JSON z polem `"protokol": 1`.
Kazde zadanie laptopa ma naglowek `X-Laptop-Id: <id>` (1-40 znakow `[A-Za-z0-9._-]`, staly dla
jednego programu laptopa, np. losowy przy instalacji - NIE nazwa osoby). Dla PUT i DELETE jest
wymagany, dla GET zalecany (zapisuje kontakt laptopa).

### Zasoby

| Zadanie | Tresc / parametry | Odpowiedz 200 |
|---|---|---|
| `GET /stan` | - | `rola`, `program`, `start_id`, `czas_s`, `plytka` (0-7), `tryb`, `plan_id`, `plan_wersja`, `plan_wazny_s`, `plan_pozostalo_s`, `plytki_planu`, `laptop` (wlasciciel), `kuweta` (biezaca), `wpisywane`, `nr_zdarzenia`, `najstarsze_zdarzenie`, `lacznosc`, `temp_c` |
| `GET /zdarzenia?od=N&czekaj=S&limit=L&start_id=X` | `od` = ostatni odebrany numer (0 na poczatku), `czekaj` = dlugie odpytywanie w s, `limit` 1-500 (100), `start_id` = znany start ramki | `start_id`, `restart` (true = inny start niz podany, zdarzenia od 1), `od`, `zdarzenia` [...], `nr_zdarzenia`, `najstarsze_zdarzenie`, `utracone` |
| `PUT /plan` | plan (nizej) | `wynik`: `przyjety` albo `powtorzony`, `plan_id`, `wersja`, `start_id`, `nr_zdarzenia` |
| `DELETE /plan[?plan_id=X]` | - | `wynik`: `usuniety` albo `brak_planu`; stan ramki = `gotowa` (zgas) |
| `PUT /tryb` | `{"protokol": 1, "stan": "skanowanie"}`; stany: `gotowa`, `skanowanie`, `analiza`, `wynik`, `blad`, `test_led` | `wynik`: `przyjety`, `stan` |

`czekaj` ramka skraca do min(25 s, limit_lacznosci_s / 3, wazny_s / 3), zeby laptop odzywal sie
dosc czesto dla waznosci planu. Ramka odpowiada od razu, gdy `od` jest wiekszy niz `nr_zdarzenia`.

### Plan (`PUT /plan`)

```
{"protokol": 1, "plan_id": "2026-11-17-p2", "wersja": 3, "start_id": "a1b2c3d4", "zdarzenia_do": 57,
 "wazny_s": 600, "tryb": "rano", "kolejnosc": "liczba",
 "plytki": {"4": {"uklad": "poranna", "usun_po_zdjeciu": false, "gniazda": [
     {"id": 2, "px": [43, 38, 3, 3], "kolor": "zielony", "kuweta": "3263"},
     {"id": 1, "px": [25, 45, 14, 3], "kolor": "bialy"}]}},
 "kuwety": [{"kuweta": "3263", "prac": 5, "plytki": [4, 5]}],
 "potwierdzone": [[5, "3263"]], "wybrane": {"4": "3263"}, "braki": ["5120"]}
```
| Pole | Znaczenie |
|---|---|
| `plan_id` | identyfikator planu (sesja pieca rano, wieczor), `[A-Za-z0-9._-]{1,40}` |
| `wersja` | liczba rosnaca w obrebie `plan_id`; kazda zmiana planu = nowa wersja |
| `start_id` | `start_id` ramki z `GET /stan` albo `/zdarzenia` (inny = 409 `inny_start`) |
| `zdarzenia_do` | numer ostatniego zdarzenia ramki, ktore laptop przetworzyl i uwzglednil w planie |
| `wazny_s` | 1-3600 s: plan obowiazuje, dopoki laptop-wlasciciel odezwal sie w ciagu `wazny_s` |
| `tryb` | `wieczor` (ramka W) albo `rano` (ramka P); inny = 409 `plan_innej_ramki` |
| `plytki` | numer plytki (W: 1-3, P: 4-6) -> `uklad` (informacyjnie), `gniazda`, `usun_po_zdjeciu` (domyslnie false: true = wpis plytki znika z planu, gdy plytke zdjeto) |
| `gniazda[]` | `id` 1-64 (unikalne), `px` = [x, y, szer., wys.] z pliku kalibracji, cale w obszarze plytki (x, y 12..51), bez nakladania, najwyzej 48 gniazd i 800 pikseli na plytke; `kolor` z listy; `kuweta` opcjonalnie |
| `kolor` | `czerwony` (sprawdz), `zielony` (bez uwag / biezaca kuweta), `zolty` (popraw ulozenie), `bursztyn` (poprawka), `bialy` (praca nieznana), `szary` (bez projektu), `niebieski`, `fioletowy` |
| `kuwety` | kolejnosc kuwet do rozkladania (ramka idzie po tej liscie): `kuweta` (`#?[0-9]{1,6}`), `prac`, `plytki` |
| `potwierdzone` | pary [plytka, kuweta] juz potwierdzone (w kolejnosci) - stan po restarcie / ponownym planie |
| `wybrane` | plytka -> kuweta wybrana recznie (numer z klawiatury) |
| `braki` | numery kuwet ze zleceniami z brakami (pokazywane po rozlozeniu plytki) |

Wynik przyjecia planu:
- ta sama `plan_id` i `wersja` i ta sama tresc (bez `start_id` i `zdarzenia_do`) = 200 `powtorzony`
  (nic sie nie zmienia - bezpieczne ponowienie po zgubionej odpowiedzi);
- starsza `wersja` = 409 `plan_starszy` (spozniony plan); ta sama wersja, inna tresc = 409
  `konflikt_wersji`;
- `zdarzenia_do` mniejsze niz numer ostatniego zdarzenia klawiatury tego `plan_id` na ramce =
  409 `zdarzenia_nieodebrane`: laptop odpytuje `/zdarzenia`, uwzglednia je i wysyla nowa wersje
  (ramka nie nadpisze potwierdzen, o ktorych laptop nie wie);
- przyjety plan ustawia stan `wynik`.

### Reguly "co swieci"

1. Gniazda swieca tylko w stanie `wynik`, przy waznym planie, gdy na ramce lezy plytka, ktorej
   numer jest w `plytki`. Plytka spoza planu = zadne gniazdo + napis "<n> BRAK" + pomaranczowy
   pierscien ("brak planu"). Zmiana plytki przelacza obraz od razu (odbijanie czujnikow 30 ms).
2. Gniazdo z `kuweta` swieci tylko, gdy to biezaca kuweta tej plytki i nie jest na niej
   potwierdzona; gniazdo bez `kuweta` (nieznana, sprawdz, wszystkie gniazda wieczorem) swieci zawsze.
3. Biezaca kuweta plytki = wybrana recznie, a jesli brak - pierwsza z listy `kuwety`, ktora ma
   gniazda na tej plytce i nie jest na niej potwierdzona.
4. Stany `skanowanie` (zolty pierscien), `analiza` (fioletowy), `gotowa` (niebieski), `blad`
   (czerwony + "BLAD") = zadne gniazdo nie swieci, plan zostaje. `test_led` = cala matryca
   kolejno czerwona, zielona, niebieska, biala (co 1 s). `DELETE /plan` = zgas.
5. Waznosc: gdy laptop-wlasciciel planu nie odezwie sie przez `wazny_s` sekund, ramka usuwa plan
   (zdarzenie `plan_wygasl`) i nic nie swieci. Laptop dostaje to zdarzenie i wysyla plan ponownie.
   Ramka poranna moze dostac dluzsze `wazny_s` (np. 600 s) - wtedy bez sieci pracuje dalej na
   ostatnim planie (I1), a pierscien miga na czerwono (brak lacznosci).
6. Margines: pierscien 1 px = stan ramki; ikona 3 x 3 z przodu po lewej = lacznosc (zielona /
   czerwona); napis z przodu: rano "3263 3" (kuweta, liczba jej prac na tej plytce), wpisywane
   cyfry "32_", "?7777" (numer spoza planu, 3 s), "OK" albo "-5120" (braki) po rozlozeniu;
   wieczorem numer plytki; prawy margines = inne plytki biezacej kuwety.

### Klawiatura (ramka poranna) i zdarzenia

Enter = potwierdz biezaca kuwete na tej plytce (`potwierdzenie`) i przejdz do nastepnej;
Backspace = usun ostatnia wpisana cyfre, a bez cyfr cofnij ostatnie potwierdzenie na tej plytce
(`cofniecie`, kuweta znow biezaca); cyfry + Enter = wybierz kuwete (`kuweta_wybrana`; numer
dopasowany doslownie, potem z "#", potem bez zer wiodacych) albo `kuweta_nieznana`; klawisz
"Zamknij piec" (domyslnie `*` na klawiaturze numerycznej) = `zamknij_piec` (zawsze). Bez planu
albo bez plytki klawisze poza "Zamknij piec" nie daja zdarzen. Ramka wieczorna ignoruje klawisze.

Zdarzenie: `{"nr": 57, "typ": "...", "czas_s": 12.345, ...pola}`; typy i pola: `start` (`rola`,
`program`), `plytka` (`plytka`, `poprzednia`), `potwierdzenie` / `cofniecie` / `kuweta_wybrana`
(`plan_id`, `plytka`, `kuweta`), `kuweta_nieznana` (`plan_id`, `plytka`, `wpisano`), `zamknij_piec`
(`plan_id` albo null, `plytka`), `plan_wygasl` (`plan_id`).

Numeracja: `nr` rosnie o 1 od startu programu ramki (`start` = 1); `start_id` (8 znakow hex)
zmienia sie przy kazdym starcie. Laptop pamieta (`start_id`, ostatni `nr`) i pyta `od=nr` z
`start_id` - dostaje kazde zdarzenie dokladnie raz i w kolejnosci, takze po zgubionej odpowiedzi
(pyta ponownie o to samo `od`). Gdy ramka wystartowala ponownie, odpowiedz ma `restart: true`
i zdarzenia od 1; plan w RAM zniknal - laptop wysyla go ponownie z nowym `start_id`. Dziennik
trzyma 2000 ostatnich zdarzen; starsze niz `najstarsze_zdarzenie` = licznik `utracone`.

### Dwa laptopy, ponowienia, bledy

Wlasciciel ramki = laptop ostatniego udanego PUT / DELETE. Inny laptop dostaje 409 `inny_laptop`
na PUT i DELETE, dopoki wlasciciel odzywa sie co najwyzej `limit_lacznosci_s` (30 s); potem
moze przejac ramke. GET wolno kazdemu; kazdy laptop odbiera wszystkie zdarzenia. `DELETE
/plan?plan_id=X` usuwa tylko plan X (inny = 409 `inny_plan`) - spozniony DELETE nie skasuje
nowszego planu.

| Status | Kod | Kiedy |
|---|---|---|
| 400 | `zly_json` | tresc nie jest obiektem JSON w UTF-8 (takze zbyt gleboko zagniezdzona) |
| 400 | `brak_pola`, `nieznane_pole`, `zle_pole`, `zly_protokol` | schemat planu / trybu |
| 400 | `nieznane_gniazdo` | id gniazda nie 1-64, nie liczba albo powtorzone |
| 400 | `px_poza_plytka`, `px_nakladanie`, `za_duzo_pikseli`, `za_duzo_gniazd` | bloki pikseli |
| 400 | `zly_kolor`, `zla_kuweta`, `nieznana_kuweta`, `zla_plytka` | wartosci |
| 400 | `zly_stan`, `zly_parametr`, `brak_laptopa`, `zly_laptop`, `zla_dlugosc` | tryb, zapytanie, naglowki |
| 404 / 405 | `nieznany_zasob` / `zla_metoda` | zasob, metoda |
| 409 | `inny_start`, `zdarzenia_nieodebrane`, `plan_starszy`, `konflikt_wersji`, `inny_laptop`, `inny_plan`, `plan_innej_ramki` | konflikty stanu |
| 411 / 413 | `brak_dlugosci` / `za_duza_tresc` | PUT bez Content-Length / ponad 64 KiB |
| 500 | `blad_wewnetrzny` | blad programu ramki (ramka dziala dalej) |

Odpowiedz bledu: `{"protokol": 1, "blad": {"kod": "...", "opis": "..."}}`; opis nigdy nie
powtarza wartosci z zadania. Nieznane pola sa odrzucane, a kuweta musi byc numerem - nazwa
folderu ani nazwisko nie przejdzie walidacji. Log ramki: adres, metoda, zasob, status.

### Kontrakt w skrocie (dla `indicate`)

1. Na starcie i w petli: `GET /zdarzenia?od=<nr>&czekaj=<s>&start_id=<id>` z `X-Laptop-Id`.
2. Zmiana `start_id` / `restart: true` = ramka wstala od nowa: kursor od zera, wyslij plan.
3. Plan: px z pliku kalibracji (`ramka.kalibracja.gniazda_planu`), `zdarzenia_do` = ostatni
   przetworzony `nr`, `wersja` + 1 przy kazdej zmianie, `wazny_s` W ok. 30 s, P do potwierdzenia.
4. 409 `zdarzenia_nieodebrane` / `inny_start` = odpytaj, przelicz, wyslij ponownie.
5. Skan zablokowany / nieprzyjety / blad = `PUT /tryb blad` albo `DELETE /plan`; Spacja =
   `PUT /tryb skanowanie`, analiza = `analiza`, wynik = nowy plan.
6. "Zamknij piec": zdarzenie `zamknij_piec`, laptop zamyka sesje pieca i wysyla `DELETE /plan`.

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
4. Kopia katalogu `ramka/` do `/opt/ramka/ramka/`, plik `/etc/ramka/ramka.json` (np. `{"rola": "P",
   "sprzet": "rpi"}`).
5. Usluga systemd `/etc/systemd/system/ramka.service`: `ExecStart=/usr/bin/python3 -m ramka
   --konfiguracja /etc/ramka/ramka.json`, `WorkingDirectory=/opt/ramka`, `User=root` (rgbmatrix),
   `Restart=always`, `RestartSec=2`; `systemctl enable ramka`. Logi: journald (w RAM).
6. Karta tylko do odczytu (I13): `raspi-config` -> Performance -> Overlay File System; zmiana
   programu = wylaczenie nakladki, kopia plikow, wlaczenie. Plan i zdarzenia sa tylko w RAM.
7. Kontrola: `curl http://ramka-p.local:8765/stan`; test LED: zatrzymac usluge, `python3 -m
   ramka.test_led ... --sprzet rpi`, uruchomic usluge.

## Czego nie sprawdzono bez sprzetu (paczka C1 / C2)

Matryca (rgbmatrix: orientacja `obrot` / `lustro`, jasnosc, migotanie, czas `pokaz` ok. 4096
`SetPixel`), czujniki A3144 przez gpiozero (polaryzacja, odbijanie przy zdejmowaniu plytki
po skosie, I5 < 100 ms na Pi), wspolpraca gpiozero z rgbmatrix na jednym GPIO, klawiatura evdev
(kody klawiszy konkretnej klawiatury, NumLock, klawisz "Zamknij piec", wypiecie odbiornika),
start po wlaczeniu < 60 s, praca 8 h, temperatura, karta tylko do odczytu, Wi-Fi firmowe i `.local`.
