# session - stan wieczoru (E3-A1, 17.11.2026)

**Zamowienie (plan etapu 3).** Stan wieczoru i poranka, decyzje technika, sesja pieca, punkty zlecen, braki, "do dofrezowania". **Stan po E3-A1:** czesc wieczorna - `stanowisko/session.py` na bazie `baza.py`. Poranek (sesja pieca, `plan_plytek`, "Zamknij piec", braki) to paczka A6. Tylko biblioteka standardowa; modul nie importuje silnika ani okna.

**Wejscie.** (1) Wynik analizy skanu: slownik z `porownaj.porownaj` (ten sam co `<skan>_wynik.json`) + zdarzenie skanu - slownik albo obiekt z polami `plik`, `sha16`, `rozmiar`, `czas_pliku` (kontrakt `ZdarzenieSkanu`, plan 3.8; klase tworzy A2). (2) Decyzje technika. (3) Indeks w bazie (`zlecenia`, `projekty`, `frezowania` - wypelni A4): z niego praca dostaje kuwete, zeby i krazek.

**Wyjscie / API (`Sesja(baza, operatorzy=..., katalog_wynikow=...)` albo `Sesja.z_ustawien(ust)`).**
- `przyjmij_wynik(zdarzenie, wynik) -> skan_id`: wiersz `skany`, jedna praca na kazdy wpis `wynik["gniazda"]` (statusy 1:1), caly wynik do pliku `skanNNNNNN_<nazwa skanu>_wynik.json` w `[sciezki] wyniki`, wpis w `zdarzenia`. `przyjmij_blad(zdarzenie, opis)`: analiza bez wyniku -> skan `blad`.
- `decyzja(praca_id, rodzaj, wartosc, operator, skan_id=...)` i skroty: `ukruszona(praca_id)`, `ok(praca_id)`, `cofnij(praca_id)`, `zastap_skan(skan_id)`, `podaj_numer_plytki(skan_id, numer)`; `wybierz_operatora(nazwa)`.
- `stan_wieczoru(data)`: skany wieczoru z pracami (statusy z pliku, `kolor` obowiazujacy, `sha16`, kuweta, zeby, krazek, obowiazujaca decyzja), `liczniki` kolorow, `do_potwierdzenia` (ponowne skany), `do_dofrezowania`, `konflikty`. Zwykle dane (JSON).
- `do_dofrezowania(data)` (pozycja: kuweta, zeby, krazek, plytka, gniazdo, `sha16`, kto i kiedy), `zapisz_do_dofrezowania(data, katalog)` -> `do_dofrezowania_<data>.csv`, `konflikty(data)`, `sciezka_wyniku(skan_id)`.
- Bledy uzycia (nie ma pracy, skan zastapiony, osoba spoza listy, nic do cofniecia): `BladSesji` z komunikatem dla okna; baza bez zmian.

**Reguly.**
- Wieczor = data z `skany.czas_pliku` (gdy brak: z czasu analizy) i tryb `wieczor`. Skan po polnocy nalezy do nastepnej daty.
- Status skanu: `niezgodny_uklad` (wynik z `uklad_zgodny` = false; 0 prac), `do_powtorzenia` (ktorakolwiek praca ma status inspect `skan_ponownie` albo `popraw_ulozenie`, sa dwie prace w gniezdzie albo praca poza gniazdem), inaczej `przyjety`; `zastapiony` po potwierdzeniu ponownego skanu; `blad`. Do stanu i list licza sie skany `przyjety` i `do_powtorzenia` ("aktywne").
- Kolor pracy = `status_gniazda` z wyniku, z jednym wyjatkiem: w skanie `do_powtorzenia` praca zielona jest zolta (taki skan niczego nie potwierdza - 0 zielonych). W bazie statusy zostaja jak w pliku wyniku.
- Praca jest przypisana do projektu pierwszego kandydata, gdy match nie dal statusu `szary`. `projekt_id` = punkt z indeksu o tym `sha16` (gdy jest dokladnie jeden), `frezowanie_id` = wpis wskazany w wyniku (`kandydaci[0].frezowanie_id`, po A5) albo najnowszy wpis frezowania tego projektu.
- Decyzje sa tylko dopisywane. Obowiazuje ostatnia niecofnieta decyzja `ukruszona` / `ok` / `ukruszona_niewykryta` (tryb cienia); `cofnij` dopisuje wiersz `cofniecie` z id cofanej decyzji i przywraca poprzednia. Operator (DW3): osoba wybrana z listy `[sesja] operatorzy` na poczatku zmiany; przy pustej liscie osoba nie jest wymagana.
- "Ukruszona" ustawia `stan_punktow` projektu na `do_dofrezowania`; gdy decyzja przestaje obowiazywac (cofniecie, "OK", skan zastapiony) i nie ma innej ukruszonej pracy tego projektu, punkt wraca do `oczekuje`. Lista "do dofrezowania" obejmuje tez prace bez projektu w indeksie (wtedy bez kuwety i krazka).
- Ponowny skan (Z4): skan o tym samym numerze plytki (albo tej samej zawartosci pliku) z tego samego wieczoru jest tylko wskazywany w `do_potwierdzenia`; dopiero `zastap_skan` daje poprzedniemu status `zastapiony`. Jego decyzje zostaja w bazie, nie licza sie do list i nie przechodza na nowy skan; nowych decyzji na nim podjac sie nie da.
- Konflikt (SE8): ten sam `sha16` przypisany w dwoch roznych gniazdach skanow aktywnych wieczoru; nie licza sie prace szare ani oznaczone "Ukruszona" (ten sam STL drugi raz = zab dofrezowany). Zglaszany w `stan_wieczoru`, `konflikty` i wpisem `konflikt_projektu` w `zdarzenia`; rozstrzyga technik.
- Dane osobowe: modul nie zapisuje i nie zwraca nazw folderow ani plikow zlecen - tylko `sha16`, kuweta, zeby, krazek, numery.

**Import starych decyzji.** `narzedzia/import_decyzji.py [--plik dane/decyzje.csv] [--baza ...]`: wiersz pliku okna testowego = wiersz `decyzje`; skany z importu maja pusty `tryb` (nie naleza do zadnego wieczoru). Zly plik nie jest importowany wcale; ponowny import nie dubluje.

**Kryterium "dziala".** `testy/test_session_wieczor.py` na danych `testy/dane_sesji` (wyniki w formacie `porownaj` zbudowane recznie, fikcyjne nazwy): kryteria 1-6, 8, 9 planu (sekcja 4.1) + test na wyniku prawdziwego `porownaj` ze skanu trzech atrap koron. Docelowo (plan): scenariusz 3 piecow + 1 dofrezowany zab daje wlasciwe listy - po A6.

**Zalozenia i granice.**
- Rodzaje decyzji obslugiwane dzis: `ukruszona`, `ok`, `ukruszona_niewykryta`, `cofniecie`, `powtorz_skan`, `numer_plytki`. `wybor_kandydata`, `przypisanie_reczne`, `uklad` (sekcja 3.4) sa odrzucane z komunikatem - dojda z ekranami (A3, A6); konfliktu nie da sie jeszcze rozstrzygnac w programie.
- `cofniecie` nie ma na liscie rodzajow w sekcji 3.4 (kryterium 2 wymaga czwartego wiersza) - do potwierdzenia przez wlasciciela, patrz raport E3-A1.
- Ten sam plik STL w dwoch zleceniach (dwa punkty o jednym `sha16`): praca zostaje bez `projekt_id` (bez kuwety na liscie). Indeks uzupelniony po skanie nie dopisuje przypisania wstecz.
- Plytka uzyta drugi raz tego samego wieczoru z nowa partia ma ten sam numer co wczesniejszy skan: program pokazuje ja w `do_potwierdzenia`, a technik po prostu nie potwierdza zastapienia (osobnej odpowiedzi "to inna partia" nie ma - okno A3).
- Stan punktow poza `do_dofrezowania` / `oczekuje` (rozpoznany, brak po piecu, zamkniecie reczne) i zamkniecie zlecenia zebem dofrezowanym (SE4): paczka A6.
- Plik listy "do dofrezowania" powstaje na zadanie (`zapisz_do_dofrezowania`); druk i wysylka poza etapem (Z6).
- `skany.plik` = sciezka pliku skanu tak, jak podal ja `scanner` (nazwa ze skanera, nie nazwa zlecenia).
