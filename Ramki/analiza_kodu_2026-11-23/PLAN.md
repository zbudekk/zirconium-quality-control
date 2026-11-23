# Analiza kodu programu stanowiska - plan 3 sesji (23.11.2026)

Podstawa: `origin/main` b856b9e (21.11.2026, wydanie 0.3.3 = commit 0fedbf6), program `Ramki/stanowisko`.
Kod sie NIE zmienia - wynikiem sa tylko raporty. Sposob pracy na MSI i PC: `JAK_PRACOWAC_MSI_PC.md` (obok).
Termin, ktoremu to sluzy: pierwsze testy na sprzecie 28-29.11.2026 (`Ramki/etap3/testy_sprzet_2026-11-28/`).

## Uzgodnienia z wlascicielem (23.11.2026)

- Priorytety: (1) FALSZYWE ZIELONE - ukruszona praca dostaje zielone; (2) ZAWIESZENIE programu albo okna w trakcie pracy.
- Plytki: zamowiony jest komplet pod OKRAGLE ramki z nowym ukladem (plytki "okragle ramkowe" n1-n6, wkladka
  i pokrywka okragla; uklady `okragla_ramkowa_wieczorna` / `okragla_ramkowa_poranna`). Testy beda na PIERWOTNEJ
  plytce okraglej (uklad R54: `okragla_wieczorna_r54` / `okragla_poranna_r54`, numery 8 / 9; fizycznie jest R54 nr 8).
  Analiza patrzy najpierw na sciezki tych dwoch rodzin; kwadratowe i okragle R59 n8 / n9 tylko tam, gdzie kod
  jest wspolny.
- Budzet testow: czytanie kodu + proby do 3 min. Bez pelnego pytest, bez kampanii pomiarowych, bez petli powtorzen.
- Wynik: tylko raport znalezisk. Bez poprawek i bez PR z kodem.
- Modele: sesja glowna Fable 5.2; prace monotonne, mechaniczne i proste zleca subagentom Opus 5.5.
- Sesje prowadzi nowe konto Claude - nie ma pamieci poprzednich sesji; wszystko, czego potrzebuje, jest w tym
  folderze i w plikach wskazanych w `JAK_PRACOWAC_MSI_PC.md`.
- Poza ta runda: zgubiony skan / decyzja jako osobny temat, nazwiska pacjentow w plikach, `dzien_skanera*`,
  instalator i paczka wydania, generator Blendera `ramka_generator.py`.

## Sprawy znane - NIE zglaszaj ponownie, najwyzej dopisz przyczyne w kodzie

Zrodlo: `Ramki/00_NADZOR_STAN.md`, koniec pliku ("Lista decyzji wlasciciela" 1-20, zlecenie 2), oraz
`Ramki/etap3/odbior_koncowy/RAPORT.md`, `Ramki/etap3/plan_plytki_okragle_n1-n6_2026-11-21.md`,
`Ramki/etap3/propozycja_wariant_C_regula_ksztaltu_2026-11-21.md`. Najwazniejsze:

- T2 (e) "pozycja 8": praca z ubytkiem wychodzi na zielono - znane falszywe zielone, czeka na decyzje wlasciciela.
  S1 zaczyna od niej: jaka sciezka w kodzie daje to zielone i czy sa inne sciezki tego samego rodzaju.
- Ramka wieczorna moze zaswiecic wynik INNEJ plytki o tym samym numerze (decyzja 1); ramka ciemna przy otwartym
  pytaniu o ponowny skan i po recznej poprawce numeru (decyzje 28, 29).
- Plytka okragla bez czytelnych dolkow i bez scianki bocznej w skanie: testowej n8 / n9 nie da sie odroznic od
  ramkowej; wynik "niepewny", a program glowny flagi `pewny` nie czyta (W12); wariant C tylko zmierzony, nie wdrozony.
- Silnik w srodowisku wersji: kody 0xC0000409 i 0xC0000005 przy koncu procesu, zawieszenia (E3-A11w).
- Pierwsza plytka po zimnym starcie 48,66 s (pula zimna).
- E3-P14: decyzja kliknieta przy zajetej bazie przepada, okno stoi ok. 15 s; przycisk niewidoczny przy 1536 x 864;
  wynik nowej plytki ukryty do klikniecia; "Zamknij piec" gubi zlecenie. Sprawdz w STAN, co z tego juz naprawiono.

## Zasady wspolne (kazda sesja)

1. Sesja pisze TYLKO: swoj plik `Ramki/analiza_kodu_2026-11-23/S<n>_*.md` i podkatalog `S<n>/` (skrypty prob, logi).
   Osobna galaz `analiza/s<n>` od `origin/main`. Zadnych zmian w `Ramki/stanowisko`.
2. Przed czytaniem kodu modulu przeczytaj jego opis w `Ramki/stanowisko/opisy_modulow/` - znalezisko to takze
   rozjazd miedzy opisem a kodem.
3. Podzial pracy. Sesja glowna (Fable 5.2): czyta kod krytyczny, stawia hipotezy, ocenia wage, pisze raport.
   Subagenci (narzedzie Agent, model `opus`, effort `xhigh`) dostaja prace monotonne, mechaniczne i proste:
   - uruchomienie wskazanych testow / skryptu proby na PC i odpisanie wyniku,
   - wyliczenia po calym zakresie (np. wszystkie `except`, `join` / `get` / `recv` bez limitu czasu, wszystkie
     miejsca nadania statusu, wszystkie uzycia numeru plytki i ksztaltu) w postaci tabeli `plik:linia`,
   - porownanie opisu modulu z kodem punkt po punkcie, porownanie plikow `uklad.json`.
   Zlecenie subagenta: cel, lista plikow, format wyniku, zakaz zmian w kodzie, zasady PC z `JAK_PRACOWAC_MSI_PC.md`.
   Sesja glowna sprawdza wyrywkowo wynik subagenta, zanim trafi do raportu. Oceny wagi subagent nie robi.
4. Testy: tylko na PC. Na sesje najwyzej JEDEN subagent testowy naraz i 1 proces python; pojedyncze polecenie do
   3 min, lacznie do ok. 30 min czasu PC na sesje. Tylko pliki testow wlasnych modulow albo wlasny maly skrypt
   proby. Na MSI zadnych testow.
5. Nie proponuj zbierania danych przed dostawa skanera (decyzja wlasciciela 15.11).
6. Format znaleziska (tabela + opis):
   - id `S<n>-<nr>`, `plik:linia`, co jest zle (1-2 zdania), skutek na stanowisku (co zobaczy technik),
   - ktorej plytki dotyczy: okragla ramkowa (zamowiona) / okragla R54 (testy) / inna / kazda,
   - waga: B (grozi falszywym zielonym albo zawieszeniem w zwyklej pracy) / P (w rzadkiej sytuacji) / D (drobne),
   - dowod: `proba` (polecenie + wynik w `S<n>/`) albo `czytanie`,
   - koszt potwierdzenia: T (do 3 min, zrobione) / S (3-30 min) / D (ponad 30 min, powtorzenia albo pomiar) + co
     dokladnie trzeba by uruchomic,
   - czy da sie to sprawdzic na sprzecie 28-29.11 i jak (jedno zdanie).
7. Raport zaczyna sie od 5-10 najwazniejszych znalezisk; na koncu lista "przeczytane w calosci / przejrzane /
   nieczytane" z liczba linii oraz lista zlecen subagentow.
8. Koniec sesji: commit raportu na galezi `analiza/s<n>`, bez scalania. W odpowiedzi koncowej: liczba B / P / D
   i trzy najwazniejsze znaleziska.

## S1 - lancuch analizy skanu: skad bierze sie zielone

Plik: `S1_lancuch_analizy.md`.
Zakres (`Ramki/stanowisko/stanowisko/`): `uklad.py`, `plate.py`, `match.py`, `inspect.py`, `krawedz.py`,
`porownaj.py`, `wspolczynniki.py`, `metryki.py`, `synth.py`, `katalog.py`, `modele_plytek/okragla_*`; testy tych
modulow tylko jako dowod.

Szukaj:
- Pozycja 8 z T2 (e): sciezka, ktora daje zielone pracy z ubytkiem; inne ubytki tej samej klasy (rozmiar,
  polozenie, typ pracy), ktore przejda tak samo.
- Wszystkie sciezki, ktorymi gniazdo konczy jako zielone: wypisz kazda i warunki. Ktora z nich nie wymaga
  faktycznego sprawdzenia brzegu (brak danych skanu, pusta maska, zero punktow w pasie, NaN, wyjatek zlapany szeroko)?
- Plytka testowa okragla R54 i ramkowa n1-n6: rozpoznanie ukladu i numeru; co sie dzieje dalej, gdy rozpoznanie
  jest "niepewne" albo zle (zielone przy zlym ukladzie - T11 mierzylo 0 na skanach sztucznych; szukaj przypadkow,
  ktorych ten pomiar nie obejmowal); kieszenie magnesow, rowek pokrywki i sciecie a wyrownanie i straznik.
- `match`: zly projekt rozpoznany z wysoka pewnoscia (podobne korony, te same zeby, most) i inspekcja wzgledem
  zlego wzorca; filtr wysokosci i przyciecie projektu.
- Korekta skali (okno +-1 %): czy moze "wchlonac" realny ubytek albo przesuniecie i dac zielone.
- `krawedz`: niepewna linia brzegu trafia tylko do uwag (tryb domyslny) - czy to moze ukryc brak kontroli filaru.
- Progi i jednostki: mm kontra skala x wspolczynnik, porownania ostre i nieostre, wartosci domyslne z `ustawienia`.
- `synth` kontra detektor: zalozenia wspolne (ksztalt ubytku, szum, brak zaslon) - lista "pomiar sam siebie
  potwierdza" = rzeczy do sprawdzenia 28-29.11 na okraglej R54. To wynik z czytania, bez pomiarow.
- Testy, ktore niczego nie pilnuja (asercja "nie pada", prog dobrany pod dane).

## S2 - procesy, baza, kolejki: gdzie program moze stanac

Plik: `S2_zawieszenia.md`.
Zakres: `silnik.py`, `aplikacja.py`, `kontroler_api.py`, `scanner.py`, `baza.py`, `pula.py`, `pamiec_puli.py`,
`indeks.py`, `ustawienia.py`, `samokontrola.py`, `__init__.py`.

Szukaj:
- `silnik`: start procesow (spawn), potoki i kolejki (zakleszczenie przy pelnym potoku), czekanie bez limitu czasu
  (`join`, `get`, `recv` - wyliczenie zlec subagentowi), smierc i restart procesu, watki numpy / open3d w procesie
  potomnym; co widzi technik, gdy proces analizy konczy sie kodem 0xC0000005 / 0xC0000409.
- Co wykonuje sie w watku okna: zapisy SQLite, kopiowanie pliku skanu, liczenie puli (zimny start 48 s),
  dostep do folderu sieciowego (SharePoint, MillBox). Dla kazdego: najdluzsza mozliwa blokada i co widzi technik.
- Zamki: lista, kolejnosc brania, miejsca z dwoma zamkami naraz; sygnaly Qt miedzy watkami.
- `baza`: tryb dziennika, `busy_timeout`, dlugie transakcje, migracja i kopia, plik `.blokada`.
- `scanner`: plik zajety przez program skanera, petle czekania bez limitu, folder niedostepny; pierwszy start
  analizuje wszystkie zastane pliki `.stl` (decyzja 25) - co przy setkach plikow.
- `pula` / `pamiec_puli` / `indeks`: czas i pamiec przy kilkuset projektach, uszkodzona pamiec podreczna.
- `samokontrola`: limity czasu sprawdzen, czy sama moze zawiesic start programu.
- Zamkniecie i awaria: czy procesy potomne koncza sie zawsze (proces-sierota trzymajacy baze albo blokade).

## S3 - droga wyniku od silnika do technika: zielone po analizie, zamrozenie okna

Plik: `S3_wynik_do_technika.md`.
Zakres: `statusy.py`, `session.py`, `session_rano.py`, `ui/*`, `indicate.py`, `ramka_protokol.py`, `excel.py`,
`excel_com.py` oraz `Ramki/stanowisko/ramka/` (program ramki na RPi, w tym `kalibracja.py`).

Szukaj:
- `statusy`: mapowanie status na kolor; co dostaje status nieznany albo pusty (czy moze wyjsc zielony).
- `session` / `session_rano`: ponowny skan nadpisuje czerwone; decyzja "OK" na czerwonym; wynik poprzedniej
  plytki pokazany jako biezacy; laczenie gniazd miedzy skanami; rano przypisanie zlego projektu.
- Plytki okragle: kazde miejsce, ktore rozroznia kwadrat / kolo / ramkowa / testowa po numerze albo nazwie ukladu
  (wyliczenie zlec subagentowi); mapa okragla ze scieciem - czy obrot / odbicie mapy wzgledem plytki jest mozliwy;
  numeracja gniazd i diod dla wkladki okraglej; kalibracja ramki "z geometrii" dla ukladow okraglych.
- `ui`: mapa i legenda zgodne z baza po kazdej zmianie (stary obraz po nowym wyniku); operacje blokujace w watku
  okna. Bez zrzutow ekranu - tylko czytanie i testy bez okna.
- `indicate` + `ramka_protokol` + `ramka/`: dioda nie tego gniazda, stary komunikat po zerwaniu polaczenia
  (zielone swieci dalej), czekanie na ramke blokujace okno. Znana sprawa "wynik innej plytki" - tylko nowe warianty.
- `excel` / `excel_com`: zly wiersz albo status w arkuszu; wywolanie COM wiszace na oknie dialogowym Excela -
  czy ma limit czasu i w ktorym watku idzie. Bez uruchamiania prawdziwego Excela.

## Czego ta runda nie potwierdzi (dlugie testy - decyzja wlasciciela po raportach)

| Co | Dlaczego dlugo | Skala wg raportow |
|---|---|---|
| progi `match` / `inspect` / `krawedz` | wynik to odsetek: setki skanow x uklady plytek x wspolczynnik x rozmiar ubytku | ok. 12-18 s na plytke; kampanie 17.11: 90-135 min i 4 h 25 min |
| `silnik`, testy czasowe | bledy rzadkie: 30-200 powtorzen, takze pod obciazeniem | E3-A11w 5 z 10 nieudanych; E3-T0d 10 na 1000 |
| `baza` / `session` przy zajetej bazie | wstrzykiwanie bledow + powtorzenia | dziesiatki przebiegow |
| `pula` na kilkuset projektach | 1,5-4 GB na proces, na PC po kolei | proba T4: 400 projektow; zimny start 48 s |
| wyglad `ui` | zrzuty ekranu w kilku rozdzielczosciach | - |
| `excel_com` | prawdziwy Excel przez COM, tylko PC | - |
| pelny pytest | 2506 testow (21.11), 1 proces, tylko PC | 17-21 min przy 1829 testach, dzis dluzej |

Gdyby po raportach potwierdzac progi pomiarem: tylko uklady okragle (R54 testowy i ramkowy), nie wszystkie
dziesiec - to skraca kampanie kilkukrotnie.

## Start sesji (tekst dla nowego konta)

"Przeczytaj `Ramki/analiza_kodu_2026-11-23/JAK_PRACOWAC_MSI_PC.md` i `PLAN.md` w tym samym folderze. Wykonaj
sesje S<n> z planu. Kodu nie zmieniaj; wynik to plik raportu sesji."
