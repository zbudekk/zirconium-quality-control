# indicate - klient ramek swietlnych po stronie laptopa (E3-A8, czesc "indicate", 18.11.2026)

**Zamowienie (plan etapu 3, 3.6 i 4.1 E3-A8).** Laptop wysyla ramce porannej plan plytek pieca (gniazdo -> kuweta, kolory),
ramce wieczornej stan (Spacja) i kolory gniazd po analizie, odbiera zdarzenia ramek (numer plytki, potwierdzenia kuwet,
"Zamknij piec") - bez gubienia i bez powtorek, takze po przerwie w sieci i po restarcie ramki. Protokol = kontrakt
`ramka/README.md` ("Protokol v1", "Wymagania dla strony laptopa" 1-11). Podpiecie do programu (okno, `session`) robi A12.

**Pliki.** `stanowisko/indicate.py` (klient: watki, kolejka polecen, stan), `stanowisko/ramka_protokol.py` (budowa planow
z `SesjaRano.plan_plytek` i z wyniku skanu wieczornego, walidacja kodem ramki `ramka.protokol.sprawdz_plan`, walidacja
odpowiedzi, kolor ramki z `statusy.py`), `testy/test_indicate.py`. Tylko biblioteka standardowa + pakiet `ramka`.

## API dla A12 (w skrocie)

1. `ind = Indicate.z_ustawien(ust, na_zdarzenie=None)`; `ind.uruchom()` przy starcie programu, `ind.zatrzymaj()` przy
   zamknieciu; `ind.wieczorna`, `ind.poranna` = `KlientRamki`; brak ramki = `stan()["komunikat"]`, program dziala dalej.
2. Wieczor: Spacja -> `z = ind.wieczorna.skanowanie()` (zapamietac `z` przy skanie); start analizy -> `analiza()`;
   wynik -> `ind.wieczorna.wynik(numer_plytki, uklad, {gniazdo: ramka_protokol.kolor_ramki(status)}, z)`; blad / skan
   zablokowany -> `blad()` albo `zgas()`.
3. Rano: po kazdej zmianie sesji pieca `ind.poranna.ustaw_plan_rano(rano.plan_plytek(kolejnosc))` (ta sama tresc = nic nie
   wysyla, nowy `plan_id` = najpierw `DELETE /plan`); "Zamknij piec" przyjete przez `session_rano.zamknij_piec` -> `zgas()`.
4. Zdarzenia: `klient.odbierz_zdarzenia()` z `QTimer` (albo `na_zdarzenie` - wolane w watku klienta, nie w watku Qt):
   `potwierdzenie` / `cofniecie` / `kuweta_wybrana` -> dziennik `zdarzenia`, `zamknij_piec` -> `session_rano.zamknij_piec()`.
5. Ekran: `klient.stan()` - `polaczona`, `blad` + `komunikat` (np. drugi laptop, zly klucz, awaria sprzetu ramki),
   `ostrzezenia` (kalibracja), `plytka`, `tryb_ramki`, `potwierdzone`, `plan_przyjety`, `pominiete` (plytki bez kalibracji).

## Klient jednej ramki - `KlientRamki(rola, host, port, *, laptop_id, kalibracja, klucz="", ...)`

- Dwa watki. **Odpytywanie**: `GET /stan` przy pierwszym kontakcie (migawka: start ramki, plytka, plan, potwierdzenia,
  numer ostatniego zdarzenia N), potem `GET /zdarzenia?od=<nr>&czekaj=<s>&start_id=<id>`. Kursor (start_id, nr) przesuwany
  tylko po udanej odpowiedzi - kazde zdarzenie dostarczone raz i w kolejnosci. Zdarzenia sprzed startu klienta (do N)
  nie sa dostarczane programowi (sa w migawce); `kursor=(start_id, nr)` zapamietany przez program = dostarcz te powyzej
  `nr` tego startu. **Polecenia**: jedna szeregowa kolejka; polecenie gaszace (`PUT /tryb`, `DELETE /plan`) zastepuje
  oczekujace polecenie i anuluje oczekujacy plan i ponowienie; gaszace ponawiane do skutku (200); plan budowany tuz przed
  wyslaniem (`zdarzenia_do` = ostatnie ODEBRANE zdarzenie, dopiero po odebraniu zdarzenia wlasnego poprzedniego polecenia),
  `wersja` + 1 przy kazdym wyslaniu; ta sama wersja i tresc tylko po zgubionej odpowiedzi; `http.client` bez ponowien.
- Odpowiedzi na `PUT /plan`: 409 `zdarzenia_nieodebrane` -> odpytanie, przeliczenie (nowe potwierdzenia, zdjete plytki),
  nowa wersja; `plan_starszy` / `konflikt_wersji` -> wersja powyzej `wersja_ramki`; `plan_zgaszony` -> tej tresci nie
  wysyla nigdy (w zadnej wersji; nowa tresc albo restart / `sprzet_dziala` / `plan_wygasl` rano / utracone zdarzenia
  zdejmuja blokade); `inny_start` -> migawka; `inny_laptop` -> `blad` "inny_laptop", proba co 2 s; `blad_sprzetu` ->
  plan dopiero po zdarzeniu `sprzet_dziala`; 400 / 411 / 413 / 500 / `plan_innej_ramki` -> ramka zgaszona, `blad`
  "plan_odrzucony" (ta tresc zablokowana); 401 (takze na GET) -> `blad` "zly_klucz", klient przestaje pytac do `wznow()`.
- Restart ramki (inny `start_id`): kursor od zera; rano plan ponownie (nowy `start_id`, potwierdzenia laptopa) - do 5 s;
  wieczorem wyniki sprzed restartu znikaja (wraca tylko stan `skanowanie` / `analiza` / `blad`, jesli byl ostatni).
- Utracone zdarzenia (`utracone` > 0 w odpowiedzi): rano migawka `GET /stan` (potwierdzenia, wybrane) i nowa wersja planu;
  wieczorem wyniki ze znacznikiem sprzed utraconego zakresu niewazne; licznik `stan()["utracone"]`.
- Metody: `uruchom()`, `zatrzymaj()`, `wznow()`, `stan()`, `odbierz_zdarzenia()`, `czekaj(warunek, timeout)`, `kursor`,
  `znacznik()`, `potwierdzone()`; P: `ustaw_plan_rano(plan_plytek, potwierdzone=None, wybrane=None) -> pominiete`, `zgas()`,
  `tryb(stan)` (np. `test_led` - rano zdejmuje plan jak `zgas`); W: `skanowanie()`, `analiza()`, `blad()`, `tryb(stan)`,
  `zgas()`, `wynik(numer, uklad, kolory, znacznik) -> "wyslany" | "bez_numeru" | "zla_plytka" | "brak_kalibracji" |
  "niewazny"`. Zle wywolanie (plan rano do ramki W, zly `plan_id`) = wyjatek; bledy ramki i sieci - tylko w `stan()`.

**Zdarzenie dla programu** = slownik zdarzenia z protokolu (`nr`, `typ`, `czas_s`, pola typu) + `rola` ("W" / "P") +
`start_id`. Typy: `start`, `plytka` (`plytka`, `poprzednia`), `potwierdzenie` / `cofniecie` / `kuweta_wybrana` (`plan_id`,
`plytka`, `kuweta`), `kuweta_nieznana` (`wpisano`), `zamknij_piec` (`plan_id`, `plytka`), `plan_przyjety`, `plan_wygasl`,
`zgaszono`, `blad_sprzetu`, `sprzet_dziala`. Para (`start_id`, `nr`) jest unikalna - po restarcie ramki numery ida od 1.

**`stan()`**: `rola`, `adres`, `polaczona`, `start_id`, `kursor`, `plytka`, `tryb_ramki`, `plan_ramki` (plan_id na ramce),
`plan_id` / `wersja` (plan laptopa), `plan_przyjety`, `awaria`, `oczekuje`, `blad` (`brak_polaczenia` jako komunikat,
`zly_klucz`, `inny_laptop`, `blad_sprzetu`, `plan_odrzucony`, `plan_innej_ramki`, `zla_rola`, `zla_odpowiedz`,
`polecenie_odrzucone`, `brak_kalibracji`), `kod_bledu` (kod ramki), `komunikat` (tekst roboczy - ostateczny ustala A12 w
`statusy.py`), `ostrzezenia`, `potwierdzone`, `wybrane`, `utracone`, `pominiete`, `wyslane_plany`, `przyjete_plany`,
`bledy_sieci`, `wyniki` (W: numery plytek z waznym wynikiem).

## Ramka W - wynik nowego skanu, nigdy stary (wymaganie 7, recenzja PR #19)

Wynik plytki ma znacznik skanu `Znacznik(start_id, nr)` = start ramki i numer ostatniego zdarzenia odebranego przez laptop
w chwili Spacji (`skanowanie()` zwraca go przed wyslaniem polecenia). Wynik jest wysylany tylko, gdy: ten sam start ramki,
po znaczniku NIE przyszlo zdjecie tej plytki (`plytka` z `poprzednia` = numer), `plan_wygasl`, `blad_sprzetu` ani utrata
zdarzen. Sprawdzane przy `wynik()` i przy KAZDYM budowaniu planu (takze po 409 `zdarzenia_nieodebrane` - plan wysylany
wtedy juz bez zdjetej plytki). Plan wieczorny zawiera wszystkie wazne wyniki (plytki 1-3); po Spacji ramka gasi, a kolejny
wynik wysyla nowa wersje z waznymi wynikami. Plytka bez numeru, spoza rodziny W albo bez kalibracji ukladu (np. okragla):
nic nie swieci, a gdy nic waznego nie zostalo, ramka przechodzi z "analiza" do "gotowa". Znacznik wziety bez polaczenia
(`start_id` None) jest niewazny - lepiej ciemno niz stary wynik. Ramka wieczorna nie zna kuwet (plan bez `kuweta`).

## Ramka P - plan pieca i potwierdzenia

`ustaw_plan_rano` bierze z `plan_plytek` tylko `plan_id`, `plytki`, `kuwety`, `braki`, `uklady`; `ramka_protokol.plan_rano`
dodaje `px` z kalibracji (rola P, uklad z `uklady`), `protokol`, `wersja`, `start_id`, `zdarzenia_do`, `wazny_s` 600,
`potwierdzone` i `wybrane` ze stanu laptopa (zdarzenia klawiatury + migawka `GET /stan`; filtrowane do plytek planu
i kuwet z listy), sprawdza plan kodem ramki. Pomija: plytki spoza 4-6, plytki bez kalibracji, kuwety niezgodne z `#?[0-9]{1,6}`
(gniazdo swieci wtedy "sprawdz" na czerwono, jak w `session_rano`), nieznane pola. Potwierdzen z klawiatury laptop nie
odsyla (ramka stosuje je sama); nowa wersja planu tylko przy wlasnej zmianie: inna tresc z sesji, restart ramki,
`plan_wygasl` tego planu, `sprzet_dziala`, utracone zdarzenia. Restart programu laptopa w trakcie pieca: migawka podaje
potwierdzenia ramki (gdy plan na ramce jest wazny) - nowy klient wysyla je dalej (test `restart_programu_laptopa`).

## Ustawienia, kalibracja, identyfikator

- `[ramki] port, wieczorna_host, poranna_host` (bez zmian) oraz nowe OPCJONALNE (plik bez nich wczytuje sie jak dotad):
  `[ramki] klucz = ""` (wspolny klucz z plikiem konfiguracji ramki, tylko w lokalnym `ustawienia.toml`; walidacja jak ramka,
  wartosc nie trafia do komunikatow), `[ramki] odpytywanie_s = 25.0` (0,5-25), `[sciezki] kalibracja_ramek =
  "dane/kalibracja_ramek.json"`.
- Kalibracja: plik lokalny (format `ramka/kalibracja.py`, `python -m ramka.kalibracja --domyslna ...`). Brak pliku =
  wartosci startowe z geometrii `modele_plytek/*/uklad.json` (w pamieci, plik nie jest zapisywany) + ostrzezenie; zly plik =
  ramki bez planow (ciemno) + ostrzezenie - program dziala dalej.
- `X-Laptop-Id`: losowy `lap-<16 hex>`, zapisany raz w `ramki_laptop_id.txt` obok pliku kalibracji (`dane/`), staly dla
  instalacji; nigdy nazwa osoby ani komputera. W ruchu sieciowym tylko numery plytek, gniazd, kuwet i kolory (K8).

## Kryterium "dziala" (`testy/test_indicate.py`, atrapa ramki w osobnym procesie albo w procesie testu, HTTP 127.0.0.1)

| Kryterium planu 4.1 E3-A8 | Test | Wynik (PC, 18.11.2026) |
|---|---|---|
| K1 plan plytki porannej 23 gniazda -> matryca 64 x 64 piksel po pikselu | `test_k1_...` (osobny proces) | 23 z 23 gniazd, w 6 krokach (5 kuwet + reszta), 0 roznych pikseli; nowy piec 23 naraz |
| K2 margines: kuweta i liczba prac | `test_k2_...` (osobny proces) | 5 z 5 napisow "kuweta liczba" + prawy margines, potem "-5120" |
| K5 5 potwierdzen bez sieci, 100 powtorzen | `test_k5_...` (osobny proces + posrednik TCP, 30 % zgubionych odpowiedzi) | 500 z 500, 0 powtorek, 0 luk, 0 planow po zdarzeniach klawiatury |
| K6 restart ramki -> plan ponownie do 5 s | `test_k6_...` (3 restarty procesu ramki) | ponizej 0,1 s od startu ramki (szczegoly w raporcie) |
| K7 Spacja -> stan ramki W < 1 s, dwa procesy | `test_k7_...` | 10 z 10, maks ok. 10 ms; kolory gniazd = mapa (statusy.py) |
| K8 caly ruch testow bez nazw folderow i nazwisk | `test_zz_k8_...` (ostatni test pliku) | 0 trafien, 0 kluczy w ok. 3,5 tys. zapisow |
| PR #19: stary wynik po zdjeciu plytki | `test_w1_...`-`test_w5_...` | zdjecie, `plan_wygasl`, restart ramki, 409 w trakcie wysylki: 0 starych wynikow na ramce |

Plus: poranek (nowy piec = DELETE przed planem, "Zamknij piec" raz + `zgas`, aktualizacja z zachowaniem potwierdzen, ta
sama tresc bez wysylki, restart programu laptopa, utracone zdarzenia), jedna kolejka polecen, klucz 401 bez petli, drugi
laptop, ustawienia, plan z prawdziwej `SesjaRano.plan_plytek`, walidacja komunikatow, pliki ASCII i biblioteka standardowa.

## Zalozenia i granice

- Kolory ramki wieczornej: kolumna `ramka` w `statusy.py` (A12 przekazuje status gniazda -> `kolor_ramki`); nowy status =
  nowy wiersz w `statusy.py`, nie stala w `indicate`.
- Potwierdzenia rano sa dziennikiem `indicate` (sesja ich nie przechowuje); zapis do bazy (`zdarzenia`) robi A12 z
  `odbierz_zdarzenia()`. Gdy plan na ramce juz wygasl, a program laptopa wystartowal od nowa, potwierdzenia sprzed restartu
  zna tylko baza A12 - mozna je podac w `ustaw_plan_rano(..., potwierdzone=...)`.
- Stan `wybrane` laptopa jest lustrem zdarzen; Enter na wybranej, juz potwierdzonej kuwecie nie daje zdarzenia - wybor
  znika tylko na ramce (przy ponownym planie laptop pomija wybory kuwet juz potwierdzonych).
- Dwa laptopy: drugi dostaje `blad` "inny_laptop" (nie moze tez zgasic ramki, dopoki pierwszy odpytuje) - nieuzywany
  laptop nie powinien miec uruchomionego `indicate`.
- Nie sprawdzone bez sprzetu: Wi-Fi firmowe, `.local`, opoznienia prawdziwej sieci (T15, paczka C1).
