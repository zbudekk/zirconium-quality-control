# Dzien skanera - okno "krok po kroku", sciaga i karta (czesc C paczki "program przed skanerem", 16.11.2026)

Pytanie wlasciciela: "Co jesli nie bede wiedzial co i jak przeklikac w sofcie skanera jak przyjdzie? Jak miec pewnosc,
ze skany i wszystkie pierwsze dane zostana zebrane?" Odpowiedz tej czesci: zebranie kompletu danych nie zalezy juz od
znajomosci programu skanera ani od pamieci - okno samo kopiuje kazdy plik, ktory program skanera zapisze, ocenia kazdy
skan prostym jezykiem, prowadzi przez kroki, dokumentuje ekrany zrzutami i na koniec pakuje wszystko z sumami
kontrolnymi. Tego, czego o programie skanera nie wiemy, nie zgadujemy - jest oznaczone w sciadze.

## 1. Co powstalo

| Plik | Co |
|---|---|
| `stanowisko/dzien_skanera_rdzen.py` | logika bez Qt: sesja i manifest, zbieracz (obserwacja folderow, kopiowanie, kolejka kontroli), szybka kontrola skanu, zrzuty, raport, sumy, ZIP, `sprawdz` |
| `stanowisko/dzien_skanera.py` | okno PySide6 + `--sprawdz` |
| `stanowisko/dzien_skanera_kroki.toml` | 14 krokow dnia (9 wymaganych, 5 opcjonalnych) i definicje pol - dane, nie kod |
| `uruchom_dzien_skanera.bat` | start okna (ASCII, CRLF) |
| `testy/test_dzien_skanera.py` | 53 testy |
| `opisy_modulow/dzien_skanera.md` | opis modulu: co robi, wejscie, wyjscie, zalozenia i granice |
| `narzedzia/pomiar_skanu/` | kopia narzedzia T10 (`pomiar_skanu.py`, `c_wspolne.py` bez zmian; `pomiar_skanu.cmd` - tylko sciezki) + `README.md` |
| `../sciaga_skaner_DentalScan_2026-11-16.md` | sciaga do programu skanera: klikniecia, zrodla, [DO SPRAWDZENIA NA EGZEMPLARZU], czego nie klikac, pytania do instalatora |
| `../dzien_skanera_karta_2026-11-16.md` | karta na jedna strone do druku |

Istniejace pliki programu nie zostaly zmienione.

## 2. Jak to dziala (skrot; pelny opis w `opisy_modulow/dzien_skanera.md`)

- **Sesja** = `dane/dzien_skanera/<RRRR-MM-DD_GGMM>/`, manifest `sesja.json` zapisywany atomowo po kazdej akcji
  (+ `.bak`); po zamknieciu albo awarii okno wznawia sesje, a pliki zapisane przez skaner w przerwie kopiuja sie same.
- **Zbieranie bez wiedzy o programie skanera**: odpytywanie folderow co 1,5 s; kazdy nowy albo zmieniony plik
  dowolnego typu po ustabilizowaniu jest KOPIOWANY do folderu biezacego kroku ze sciezka wzgledna, SHA-256, rozmiarem
  i czasem. Zrodlo jest otwierane tylko do odczytu z pelnym wspoldzieleniem. Do tego "Dodaj plik / folder recznie",
  przeciagniecie na okno, "Nie wiem, gdzie skaner zapisuje - szukaj" (swieze STL / PLY / OBJ na wszystkich dyskach)
  i "Skopiuj caly folder zlecen skanera" w ostatnim kroku.
- **Szybka kontrola** kazdego STL / PLY / OBJ w osobnym procesie (awaria kontroli nie zatrzymuje zbierania): trojkaty,
  obrys, odstep punktow, cala plytka (wierzch + 3 stozki), uklad i numer, szum, liczba prac, a przy powtorce -
  porownanie z poprzednim skanem. Wynik: zielone "SKAN DOBRY", zolte "UWAGA", czerwone "TEN SKAN SIE NIE NADA, bo ...
  ZROB TAK: ...".
- **Zrzuty ekranu** przyciskiem (3 s opoznienia, okno sie chowa) i opcjonalnie przy kazdym nowym pliku.
- **Panel kompletnosci** caly czas po lewej; kazdy krok mozna pominac z powodem; "Zakoncz i spakuj" = raport,
  `SHA256SUMS.txt`, ZIP (dzielony powyzej 1,9 GB danych), ostrzezenie o brakach bez blokady.
- **`--sprawdz <folder sesji albo zip>`**: sumy, zgodnosc z manifestem, kompletnosc; kod 0 / 1 / 3 / 2.

**Jedyna funkcja do podmiany na automatyczne rozpoznawanie ukladu:**
`stanowisko/dzien_skanera_rdzen.py :: rozpoznaj_uklad(siatka, ust, numer=None) -> dict`
(klucze wyniku: `uklad`, `wyrownanie` - `plate.WynikWyrownania`, `obiekt_ukladu` - `uklad.UkladPlytki`, `kandydaci`,
`powod` - "" | `brak_plaszczyzny` | `malo_stozkow` | `zaden_uklad` | `blad`, `komunikat`, `stozki`, `proby`).
Wola ja tylko `_kontrola_siatki`. Dzis: `plate.wyrownaj` po kolei dla ukladow z `[plytki]`, lapanie
`BladWyrownania` / `NiezgodnyUklad`, pomijanie ukladow o innym rozstawie stozkow (`plate.stozki_pasuja`), wybor
miedzy kwadratem i okragla po numerze z dolkow.

## 3. Testy

`testy/test_dzien_skanera.py` - 53 testy (lista w `opisy_modulow/dzien_skanera.md`, "Kryterium dziala"). Wszystkie
uruchamiane wylacznie na PC (MSI: brak RAM-u i WDAC). Wynik koncowy na dole tej sekcji.

PC byl w czasie tej sesji wspoldzielony z innym zadaniem, ktore od ok. 00:20 zajmowalo praktycznie caly procesor
(7, potem 19 procesow Pythona po 1-3,5 GB, kazdy po kilka tysiecy sekund CPU). Wszystkie czasy ponizej sa wiec
gornymi granicami, nie typowymi wartosciami laptopa stanowiska.

- Pierwszy przebieg samego `test_dzien_skanera.py` (pierwsza wersja, PC jeszcze bez obciazenia, ok. polnocy): 47 passed w 68 s,
  w tym kontrola w osobnym procesie 6 s i okno z kontrola w tle 22 s.
- Pelny `pytest testy` po zmianach (PC w pelni obciazony, 16.11 00:50-01:05): **300 passed, 3 skipped, 2 failed**.
  Oba bledy to testy kontroli w osobnym procesie (`test_kontrola_w_osobnym_procesie`,
  `test_okno_z_kontrola_w_tle_na_sztucznym_skanie`) - przekroczony czas oczekiwania 180 s. Przyczyna: proces kontroli
  ma priorytet ponizej normalnego (zeby nie spowalniac programu skanera), a przy procesorze zajetym w calosci przez
  procesy o priorytecie normalnym nie dostaje czasu. Poprawka: priorytet jest stala `NIZSZY_PRIORYTET_KONTROLI`
  (domyslnie wlaczona, osobny test sprawdza flage), oba testy ja wylaczaja i czekaja do `LIMIT_KONTROLI_S` + 60 s.
  Wszystkie 252 dotychczasowe testy przeszly (punkt odniesienia: 252 passed / 3 skipped).
- Te dwa testy jeszcze z priorytetem ponizej normalnego i limitem 660 s (PC w pelni obciazony): proces kontroli zabity
  po 600 s, plik zachowany, ocena zolta "kontrola trwala dluzej niz 600 s i zostala przerwana" - sciezka awaryjna
  dziala tak, jak ma (zbieranie trwa, nic nie ginie).
- **Wynik koncowy - pelny `pytest testy -q` na PC ze stanem galezi `czesc-c` z commita `5ea4d64` (16.11 01:15-01:25, PC nadal obciazony):
  305 passed, 3 skipped, 0 failed w 587 s** (252 dotychczasowe + 53 nowe; skipped jak w punkcie odniesienia).
  Kontrola w osobnym procesie z normalnym priorytetem: okno z kontrola w tle 29 s.

## 4. Proba reczna na prawdziwych rozmiarach (PC, 16.11.2026 00:10-00:36)

Skrypt (poza repozytorium, w `<PC-katalog>\app\c\proba\symulacja.py`) uruchomil okno bez ekranu z prawdziwym watkiem
zbieracza i kontrola w osobnych procesach, udawal program skanera (zapis do folderu eksportu kawalkami po 8 MB
z przerwami 0,25 s, plik otwarty do konca zapisu) i czlowieka (kroki, pola, pominiecia z powodem). Skany: 9 plikow
z `dane_ref\syntetyczne_r54_P2` (45-63 MB, stare plytki: kwadratowe wieczorna n1-n2, poranna n4, okragle n8, n9) oraz
pliki zrobione z nich: pusta plytka n1 zageszczona do 131 MB, "powtorka" (ten sam skan z innym szumem 0,006 mm),
"inny eksport" (wierzcholki zaokraglone do 0,02 mm); do tego pojedyncza korona (nie plytka), STL uciety (3 MB),
plik binarny 150 MB, 40 obrazow BMP po 3 MB naraz, plik `.db` zmieniany 12 razy co 2,5 s, plik projektu XML,
plik zastany w folderze przed startem.

| Co | Wynik |
|---|---|
| Komplet | sesja: 116 plikow, 1,84 GB; kazdy z 55 plikow folderu eksportu ma w sesji kopie o tej samej SHA-256 (54 z obserwacji, 1 zastany - zgodnie z zasada tylko w kopii calego folderu); 116 / 116 kopii na dysku zgodnych z sumami w manifescie; 0 wyjatkow w `log.txt` |
| Awaria w srodku dnia | okno zamkniete bez pakowania, w tym czasie "skaner" zapisal 60 MB; po wznowieniu ta sama sesja i ten sam krok, plik z przerwy skopiowany z uwaga "pojawil sie, gdy program byl zamkniety", ocena zielona |
| Kopia skanow 45-131 MB | 3,5-8,3 s (13-16 MB/s, PC obciazony); plik 150 MB: 9,1 s |
| Szybka kontrola | 7-12 s na skan 60-131 MB przy umiarkowanym obciazeniu; 19-65 s i raz 312 s przy pelnym obciazeniu PC (jedna proba ukladu 91-172 s zamiast ok. 2 s) |
| Oceny | 9 skanow plytek z pracami / drugiej plytki: zielone, uklad zawsze wlasciwy (`wieczorna_r54`, `poranna_r54`, `okragla_wieczorna_r54`, `okragla_poranna_r54`), okragle: numer z dolkow 8 i 9, kwadraty: "wpisz numer plytki"; szum 0,015-0,018 mm; liczba prac 8-11 |
| Powtorka bez ruszania | zielone, te same 9 gniazd, najwieksza roznica polozenia prac 0,004 mm; "inny eksport": 0,22 mm (zielone, informacja) |
| Ukruszone (inny skan) | zielone + informacja "zmiana w gniazdach 5, 6, 17, 18" |
| Pojedyncza korona | czerwone: "nie widac trzech stozkow znacznikow ... ZROB TAK: ..." |
| STL uciety | czekal 30 s, potem skopiowany z uwaga; czerwone "plik STL jest uciety ... wyeksportuj jeszcze raz" |
| Pusta plytka zageszczona | zolte "3 obiekty poza gniazdami" - to byly 3 stozki znacznikow (artefakt mojego zageszczania siatki: stozki dalej niz 0,12 mm od modelu). Poprawka: fragment w miejscu stozka jest teraz informacja "w miejscu stozkow skan rozni sie od modelu (informacja dla koordynatora)", bez zoltego; obiekt poza gniazdem w innym miejscu nadal daje zolte |
| 40 BMP naraz | 166 s (kopia 1,15 s na plik, razem 4,2 s na plik - zapis manifestu i stanu obserwatora z `fsync` po kazdym pliku na zajetym dysku); 29 plikow trafilo do kroku "Zdjecia", 11 do nastepnego, bo "czlowiek" przeszedl dalej po 120 s (nic nie zginelo). Poprawki: plik trafia do kroku, w ktorym sie pojawil; manifest i stan obserwatora zapisywane zbiorczo (najrzadziej co 5 s i zawsze na koncu przegladu). Po poprawce (`seria.py`, PC nadal obciazony): 40 x 3 MB w 3,7 s, 1 zapis manifestu, wszystkie w kroku "Zdjecia" |
| Plik `.db` zmieniany co 2,5 s | skopiowana 1 wersja (przy wolnym dysku plik nie byl stabilny przez dwa odczyty), ostatni stan w kopii calego folderu |
| Kopia calego folderu | 55 plikow, 886 MB w 227 s (sama kopia 101 s), PC obciazony |
| Zakoncz i spakuj | start 00:36:06; pod pelnym obciazeniem PC proces dostal ok. 35 s procesora w 45 min i archiwum roslo ok. 60 kB/s - pomiaru do konca nie bylo. Proces dziala dalej w moim folderze na PC (nie mam zgody na jego zatrzymanie); gdy skonczy, zapisze `<PC-katalog>\app\c\proba\dzien\wynik.json` (pakowanie, `--sprawdz` folderu i ZIP, ZIP dzielony 600 MB, uszkodzenie 1 bajtu). Pakowanie, ZIP dzielony i `--sprawdz` (takze uszkodzony plik i brak czesci) sa sprawdzone testami na malych danych |

Sprzatanie PC: usuniete `proba\dzien\zrodla` i `proba\dzien\Scandata` (1,2 GB). Zostaly: `proba\dzien\sesje`
(ok. 1,8 GB + niedokonczone archiwum, uzywane przez proces symulacji, ktorego nie moglem zatrzymac), kopie kodu
`Ramki\` i `v2\` (kilkadziesiat MB), skrypty `proba\*.py`, `run.cmd`, `run2.cmd`, `pytest_*.txt`. Zaraz po
[usunieto w kopii: opis dostepu ssh]
unreachable" - lacze do PC nieaktywne, PC prawdopodobnie uspiony albo wylaczony), wiec reszty nie usunalem.
Do zrobienia, gdy PC wroci: `rmdir /s /q <PC-katalog>\app\c\proba\dzien` (po zakonczeniu procesu symulacji).

## 5. Sciaga i karta

- `../sciaga_skaner_DentalScan_2026-11-16.md`: od uruchomienia programu do pliku STL calej plytki - pierwsze
  uruchomienie (klucz USB, konto, aktywacja online / offline, typ urzadzenia, kalibracja), ustawienia ("Order Setting":
  "General" / "Order Save Path", "Order File Naming Rule", "Save Format"; "Scan Setting": "Save Image" i inne), zlecenie
  ("New Order" -> "Restoration" -> "Multidie Mode" -> "Scan" / "Save"), skan wg strony "Die tray" (okno kamery, Spacja,
  "cutting plane" ponizej wierzchu plytki, "Go to Pre-design"), gdzie szukac pliku ("Explore", "Go to Send" -> "Export"
  -> "Export Option" -> "Confirm", szukanie w oknie), plan B ("Patient mode" + "Unsectioned Model"), czego nie klikac,
  co robic, gdy ekran wyglada inaczej, 9 pytan do instalatora, skroty, lista niewiadomych. Przy kazdym kroku zrodlo
  (strona dokumentacji) albo [DO SPRAWDZENIA NA EGZEMPLARZU].
- `../dzien_skanera_karta_2026-11-16.md`: co przygotowac dzien wczesniej, kolejnosc krokow taka jak w oknie,
  5 zasad bezpieczenstwa danych, co robic, gdy cos nie dziala, co wyslac po tescie.
- Zrodla: dokumentacja online DentalScan 3.0.4 czytana 15-16.11 (25 podstron; strona glowna zwraca 404, podstrony
  dzialaja), notatki z 27.10. Nie przeczytane: white-balance, navigationmode, pozostale typy zlecen, pre-design.

## 6. Niezweryfikowane (uczciwie)

O programie skanera (wszystko pochodzi z dokumentacji 3.0.4, zadnej rzeczy nie widzielismy na ekranie):
- czy egzemplarz ma te sama wersje programu i te same nazwy przyciskow; czesc przyciskow to w dokumentacji ikony bez
  podpisu (start skanu, edycja, podglad, reset, zakonczenie, "Add details") - sa opisane slowami;
- czy "Multidie Mode" na naszej plytce (nie na uchwycie producenta) da JEDEN plik STL calej plytki, czy osobne pliki
  na pozycje; czy plan B ("Unsectioned Model") daje cala plytke;
- kiedy, gdzie i w jakim formacie program zapisuje plik skanu (dokumentacja nie mowi; "Save" na ekranie skanu nie jest
  opisany; eksport opisany tylko jako "Go to Send" -> "Export" dla programow CAD);
- czy program wygladza / wypelnia / upraszcza siatke bez pytania; czy plaszczyzne ciecia mozna pominac;
- czy rejestracja, logowanie i aktywacja wymagaja internetu; ile dni autoryzacji; czy jest klucz USB;
- gdzie "Save Image" zapisuje zdjecia i w jakim formacie; czas skanu; pole skanowania;
- opcje "reduce high brightness" i "Mental tooth" z notatek 27.10 - nie znalezione na stronach czytanych 15-16.11.

O programie stanowiska:
- szybka kontrola i jej progi sprawdzone tylko na skanach sztucznych (uklad R54 i R59); prawdziwy skan moze miec dziury,
  inny szum, odbicia - progi to wskazowka;
- zrzut ekranu `PIL.ImageGrab` na prawdziwym pulpicie laptopa (w sesji ssh bez pulpitu nie dziala - wtedy komunikat
  i zbieranie trwa); wyglad okna na ekranie laptopa (sprawdzone tylko offscreen);
- przeciaganie pliku z Eksploratora na okno (test wola obsluge upuszczenia bezposrednio);
- "Nie wiem, gdzie skaner zapisuje - szukaj" na calych dyskach laptopa (test na katalogu tymczasowym; czas przegladu
  calego dysku nieznany);
- czas pakowania kilku GB na laptopie (na PC pomiar przerwany przez obciazenie); polskie napisy przyciskow okien
  dialogowych Qt ("Tak" / "Nie") zaleza od pliku tlumaczen w instalacji PySide6;
- pomiar szczegolowy (`narzedzia/pomiar_skanu`): przycisk sprawdzony testem z podstawionym `subprocess.Popen` (polecenie,
  sciezki, `--powtorka`, wynik w sesji); samo narzedzie T10 nie bylo uruchamiane w tej sesji (pliki skopiowane bajtowo,
  SHA-256 zgodne z T10);
- `uruchom_dzien_skanera.bat` i `pomiar_skanu.cmd` nie byly uruchamiane dwuklikiem (sprawdzone: ASCII, CRLF).

## 7. Zadania dla czlowieka

1. Przed dniem testu: na laptopie uruchomic `uruchom_dzien_skanera.bat`, kliknac "Zrzut ekranu" i "Zakoncz i spakuj"
   na probe (sprawdza Pythona, PySide6, zrzut ekranu na prawdziwym pulpicie i polskie napisy); potem zamknac okno -
   sesje probna mozna zostawic albo usunac recznie z `dane\dzien_skanera\`.
2. Wydrukowac karte i sciage; przygotowac plytki, prace, etykiety blokow, pendrive (karta, "Dzien wczesniej").
3. W dniu instalacji zadac instalatorowi pytania ze sciagi (pkt 7) - zwlaszcza pokaz skanu plytki wieloelementowej
   i zapisu jednego pliku STL bez obrobki.
4. Po tescie wyslac koordynatorowi pliki ZIP z `dane\dzien_skanera\<sesja>\paczka\`; folderu sesji nie kasowac do
   potwierdzenia odbioru.

## 8. Potrzeby zmian w istniejacych plikach (nie zmienialem ich)

- `README.md` (stanowisko): dopisac okno dnia skanera - tekst w sekcji "Do README" ponizej.
- `opisy_modulow/README.md`: wiersz tabeli modulow dla `dzien_skanera` (np. "gotowy (16.11): okno zbierania danych
  w dniu dostawy skanera | folder eksportu -> sesja z manifestem, kontrola, ZIP | test_dzien_skanera").
- `plate.py` (informacja, bez prosby o zmiane): gdy stozek znacznika w skanie odbiega od modelu o wiecej niz 0,12 mm,
  `potnij_na_fragmenty` uznaje go za prace "poza gniazdem". Okno dnia skanera pokazuje to jako informacje dla
  koordynatora; `porownaj` / `ui_test` pokaza czerwone kolko poza gniazdem. Do obejrzenia na pierwszym prawdziwym skanie.
- Automatyczne rozpoznawanie ukladu (czesc innego wykonawcy): podmienic tylko `dzien_skanera_rdzen.rozpoznaj_uklad`
  (sygnatura i klucze wyniku w sekcji 2); `test_kontrola_*` w `test_dzien_skanera.py` sprawdzaja wynik na ukladach R54.

## 9. Do README (tekst do wklejenia w `stanowisko/README.md`, np. po sekcji "Laptop firmowy")

```
## Dzien skanera - zbieranie pierwszych skanow (16.11.2026)

Okno "Dzien skanera - krok po kroku": dwuklik `uruchom_dzien_skanera.bat` (albo `py -3.12 -m stanowisko.dzien_skanera`).
Prowadzi przez 14 krokow testu skanera (lista w `stanowisko/dzien_skanera_kroki.toml`) i samo kopiuje KAZDY nowy albo
zmieniony plik z folderu eksportu skanera (`[sciezki] folder_eksportu_skanera`; w oknie "Dodaj folder..." albo
"Nie wiem, gdzie skaner zapisuje - szukaj") do sesji `dane/dzien_skanera/<data_godzina>/` - oryginalow nie zmienia.
Kazdy skan STL dostaje ocene prostym jezykiem (zielone / zolte / czerwone "zrob tak: ..."), "Zrzut ekranu" dokumentuje
ekrany programu skanera, kazdy krok mozna pominac z powodem. Po awarii albo zamknieciu okno wznawia sesje bez strat.
"Zakoncz i spakuj" tworzy `RAPORT_dzien_skanera.md`, `SHA256SUMS.txt` i archiwum ZIP w `paczka/` (bez projektow
`*_cad.stl`). Sprawdzenie otrzymanej paczki: `py -3.12 -m stanowisko.dzien_skanera --sprawdz <folder sesji albo zip>`
(kod 0 = komplet, 3 = sumy zgodne, ale brakuje wymaganych krokow, 1 = blad integralnosci).
Instrukcje dla czlowieka: `../sciaga_skaner_DentalScan_2026-11-16.md`, `../dzien_skanera_karta_2026-11-16.md`.
Opis modulu: `opisy_modulow/dzien_skanera.md`. Pomiar szczegolowy skanu (narzedzie T10): `narzedzia/pomiar_skanu/`.
```
