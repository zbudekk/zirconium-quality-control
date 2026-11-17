# silnik - analiza skanu w osobnym procesie (paczka E3-A2, 17.11.2026)

**Co robi.** Wykonuje `porownaj.porownaj` (plate -> match -> inspect) w OSOBNYM PROCESIE: kolejka zadan, jedna
analiza naraz, postep, wynik, obsluga awarii. Powod: Open3D w watku pod Qt zawisa (okno testowe: 195 s bez wyniku,
`raporty/P3a_przekazanie.md` pkt 5.1). Pliki: `stanowisko/silnik.py`, testy `testy/test_silnik.py`. Sam modul uzywa
tylko biblioteki standardowej - numpy, trimesh i Open3D laduje wylacznie proces roboczy (jest na to test).

**Wejscie.** `ZadanieAnalizy` (kontrakt z planu etapu 3, sekcja 3.8):

| Pole | Domyslnie | Znaczenie |
|---|---|---|
| `skan` | - | plik STL skanu |
| `pula` | - | `OpisPuli`: `foldery` projektow, `wspolczynnik` (None = domyslny dla rozpoznanej plytki, jak w wierszu polecen), `orientacja`, `wspolczynniki` (skrot projektu -> wspolczynnik pracy) |
| `tryb` | `wieczor` | wieczor / rano - dla odbiorcy wyniku; analiza od trybu nie zalezy |
| `uklad` | `auto` | `auto` albo `rozpoznaj` = program rozpoznaje uklad plytki (zalozenie Z2); inaczej nazwa z `[plytki]` |
| `numer` | brak | numer plytki, gdy dolki kodu sa poza skanem |
| `skan_sha16` | brak | skrot ze `ZdarzenieSkanu`; bez niego silnik liczy sam |
| `inspekcja`, `bez_filtru`, `straznik` | tak, nie, tak | jak w `porownaj` |
| `wyjscie` | brak | folder na `<skan>_wynik.json` i `<skan>_podglad.npz` |

Parametry `Silnik(...)`: `ust` (slownik ustawien) albo `plik_ustawien` (None = `ustawienia.toml` programu),
`funkcja` (`"modul:funkcja"` analizy; domyslnie `stanowisko.porownaj:porownaj`), `limit_zadania_s` (600),
`limit_startu_s` (180), `pul_w_pamieci` (2), `plik_logu` (wyjscie bibliotek z procesu roboczego), `pamiec_linii`
(katalog pamieci linii brzegu na dysku; domyslnie wylaczona), `na_zdarzenie`.

**Wyjscie.** `ZdarzenieSilnika` do funkcji `na_zdarzenie` (wolanej w watku nadzorcy) albo do kolejki `Silnik.zdarzenia`:

| `typ` | Pola |
|---|---|
| `gotowy` | proces roboczy wystartowal (`czas_s` = czas startu) |
| `start` | zadanie wyslane do procesu (`zadanie_id`, `zadanie`) |
| `postep` | `etap`, `udzial` 0-1 (etapy z `porownaj`) |
| `wynik` | `wynik` = slownik `porownaj` w postaci z pliku `<skan>_wynik.json` (z `ostrzezenia`, jak w wierszu polecen) + `zadanie_id` + `skan_sha16`; `pliki` (sciezki z `wyjscie`); `czas_s` |
| `blad` | `rodzaj`: `analiza` (wyjatek, brak pliku, pusta pula), `proces` (proces zniknal - `kod wyjscia` w komunikacie), `limit_czasu`, `start` (proces nie umie wystartowac); `blad` (jedno zdanie), `szczegoly` (slad wyjatku), `czas_s` |

`<skan>_podglad.npz`: dla kazdego gniazda z inspekcja tablice `g<nr>_P` (punkty w ukladzie plytki) i `g<nr>_d`
(odchylka w mm) - material na obraz odchylek w oknie; odczyt `silnik.wczytaj_podglad(plik)`.

**Jak dziala.** `Silnik.start()` uruchamia watek nadzorcy (zwykly watek Pythona: bez Open3D i bez Qt) i proces roboczy
(`multiprocessing`, metoda `spawn`, lacze `Pipe` - bez wspolnych kolejek, wiec zabity proces niczego nie blokuje).
`zlec(zadanie)` / `zlec_skan(zdarzenie_skanu, pula)` dopisuje do kolejki i zwraca `zadanie_id`; `anuluj(id)` usuwa
zadanie, ktore jeszcze nie ruszylo. Nadzorca wysyla zadania po jednym, w kolejnosci zlecen. Awarie: wyjatek analizy
(takze `SystemExit` z `porownaj` przy pustej puli) = `blad` i nastepne zadanie w tym samym procesie; proces zniknal
(zabity, awaria biblioteki) albo przekroczyl `limit_zadania_s` = `blad` tego zadania, nowy proces, nastepne zadanie
(bez ponawiania zadania, ktore zabilo proces). Proces, ktory nie umie wystartowac (brak pakietu, zly plik ustawien),
oddaje `blad` rodzaju `start` kolejnym zadaniom - jedna proba na zadanie, bez petli restartow. `stop()` konczy proces
(zadania w kolejce przepadaja). Proces roboczy konczy sie sam, gdy zniknie proces okna.

Pula projektow zostaje w pamieci procesu roboczego (`PamiecPul`): budowana raz na (foldery, wspolczynnik, orientacja,
lista plikow w folderach z rozmiarami i czasami) - zmiana plikow w folderze = nowa pula przy nastepnym zadaniu.
Razem z pula zostaja linie brzegu projektow (pamiec modulu `krawedz`), wiec druga i kolejne plytki nie licza ich od
nowa; `pamiec_linii` dodaje zapis tych linii na dysk (przezywaja restart procesu i programu).

W oknie Qt: `lacznik = lacznik_qt(silnik)` - obiekt z sygnalami `gotowy()`, `start(int)`, `postep(int, str, float)`,
`wynik(int, object)`, `blad(int, str, str)`, `zdarzenie(object)`, emitowanymi w watku okna (zegar Qt oproznia kolejke
`silnik.zdarzenia`). PySide6 jest importowane dopiero w `lacznik_qt`.

**Pomiary (PC wlasciciela, 17.11.2026).** Liczby i obciazenie komputera w chwili pomiaru: `raporty/E3-A2_2026-11-17.md`.

**Zalozenia i granice.**
- Wynik silnika a wiersz polecen: te same pola i te same decyzje, ale NIE rownosc bit w bit - `porownaj` nie jest
  powtarzalne nawet miedzy dwoma uruchomieniami wiersza polecen na tym samym skanie (zawsze szum rzedu 1e-15 z
  wielowatkowego ICP Open3D; czasem inna galaz ICP korekty skali jednego gniazda: `skala.iteracje` 20 albo 41,
  transformacja o ok. 1e-5). Testy porownuja pole po polu z tolerancja 1e-3 dla liczb zmiennoprzecinkowych
  (bez 4 licznikow ICP korekty skali); szczegoly w `testy/test_silnik.py` (`roznice`, `_rowne`) i w raporcie paczki.
- Czas plytki to czas `porownaj`; silnik dodaje start procesu (jednorazowo, 3-4 s) i oszczedza budowe puli oraz linii
  brzegu od drugiej plytki. Pierwsza plytka po starcie procesu (takze po awarii) placi za pule i linie brzegu
  dopasowanych projektow - stad `pamiec_linii` i miejsce na "rozgrzewke" puli w A3 / A5.
- Jedna analiza naraz i jeden proces (plan 3.8); rownolegle analizy nie sa przewidziane.
- Program uruchamiajacy silnik musi miec glowny modul chroniony `if __name__ == "__main__":` (wymaganie
  `multiprocessing` na Windows); proces roboczy importuje glowny modul programu.
- Komunikat bledu przechodzi przez `bez_nazw_z_puli`: sciezki plikow z folderow puli (nazwiska w nazwach) sa
  zastepowane znacznikiem. Sciezka samego folderu puli i nazwa pliku skanu zostaja; `foldery_projektow` w wyniku to
  sciezki folderow podane w zadaniu (tak samo jak w `porownaj`).
- Kolejka zadan zyje w pamieci procesu okna: po zamknieciu programu zadania niewykonane przepadaja (ponowne zlecenie
  po starcie to zadanie sesji, A1 / A3).
- Priorytet procesu roboczego jest zwykly (okno "Dzien skanera" obniza priorytet swojej kontroli - tu nie, bo wynik ma
  byc szybko; do decyzji po probach na laptopie stanowiska, D4).
- `zadanie.wyjscie`: pliki sa nadpisywane przy ponownej analizie skanu o tej samej nazwie.
