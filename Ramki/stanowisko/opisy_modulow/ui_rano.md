# ui_rano - ekran trybu "Poranek" programu "Stanowisko" (paczka E3-A7, 18.11.2026; na API sesji porannej z rundy 2 A6)

**Co robi.** Strona okna, ktora widzi osoba rozkladajaca piec: plytki poranne jednego pieca z kuweta, zebem i miniatura
w kazdym gniezdzie, rozstrzyganie prac dwuznacznych (podglad dwoch kandydatow), nieznanych (przypisanie reczne po numerze
kuwety albo "Bez projektu") i konfliktow, rozkladanie kuwet wedlug ekranu (kolejnosc od najliczniejszej / wedlug numeru /
numer wpisany recznie; Enter = rozlozona, Backspace = cofnij), "Zamknij piec" z lista zlecen kompletnych (do odhaczenia
w Excelu) i brakow, lista brakow ze wszystkich piecow z recznym zamknieciem braku, ponowne otwarcie pieca. Bez ramki
i bez Excela (A12): komunikaty "Ramka poranna nie jest podlaczona" i "Excel nie jest podlaczony", program dziala dalej.
Ekran NICZEGO nie liczy: pokazuje `stan.rano` (kontrakt `kontroler_api` w wersji 3, opis: `aplikacja.md`) i wysyla polecenia
przez okno (`kontroler.wykonaj`). Pokaz na danych sztucznych: `py -3.12 -m stanowisko.aplikacja --atrapa --rano`.

| Plik | Rola |
|---|---|
| `ui/ekran_rano.py` | `EkranRano` (strona okna): panele (osoba, pytania i komunikaty plytek porannych, bledy programu), naglowek pieca z licznikami klas, blokadami, ostrzezeniami, "Zamknij piec" / "Otworz piec ponownie"; plytki pieca (`KartaPlytki`, do 3 w wierszu) z poleceniami plytki; legenda; prawa kolumna: `PanelKuwet` + widok pracy albo `PanelWyniku` (kompletne, braki, poprawki, lista brakow z recznym zamknieciem) |
| `ui/kandydaci.py` | `WidokPracyRano`: dane pracy (status, kuweta, zab, typ, miniatura, decyzja, konflikt, poprawka), karty dwoch kandydatow (`KartaKandydata`: miniatura, kuweta, zab, pokrycie, "To ten projekt"), "Bez projektu", "Przypisz recznie" (pole numeru kuwety -> `projekty_kuwety` -> lista projektow z miniatura), "Cofnij wybor" (z `decyzja_id`) |
| `ui/mapa_rano.py` | `MapaRano` (`mapa.MapaPlytki` z innym wnetrzem gniazda): kolor ze stanu, w gniezdzie kuweta (`Gniazdo.podpis`), zab i miniatura (`PracaRano`) - co sie miesci; obwodka gniazd biezacej kuwety (jak gniazda z kuweta w planie ramki: pewna / przypisana / poprawka) |
| `ui/napisy_rano.py` | napisy ekranu porannego, ktorych nie ma w `statusy` (UTF-8, polskie znaki) |
| `ui/okno.py`, `ui/czesci.py` (zmiany) | okno: druga strona pod wspolnym paskiem stanu (`QStackedLayout`, strona wg `stan.tryb`), klawisze ramki porannej przekazywane ekranowi; pasek stanu: przycisk "-> Poranek" / "-> Wieczor" obok trybu |

## Uklad (laptop 1920 x 1080)

Okno to samo co wieczorem (startuje zmaksymalizowane; od 1240 x 640 punktow; uklad zwykly / zwarty wg `styl.PROG_ZWARTEGO`).
Lewa czesc: pasek bledow, panele (najwyzej 3), naglowek pieca, plytki pieca obok siebie (3 w wierszu, mapy skaluja sie do
miejsca), skany zastapione jednym wierszem pod plytkami, legenda statusow obecnych na plytkach. Prawa kolumna ma stale
miejsce (540 / 468 punktow): przelacznik "Rozkladanie kuwet" / "Kompletne i braki" (po "Zamknij piec" ekran sam przechodzi
na "Kompletne i braki", po otwarciu nowego pieca - z powrotem). W gniezdzie: promien od 25 px - numer gniazda, miniatura,
kuweta, zab; od 16 px - kuweta i zab; mniej - sama kuweta (albo numer gniazda). Przy 1920 x 1001 (100 %, okno
zmaksymalizowane) promien gniazda 26 px - wszystko w gniezdzie; przy 125 % (1536 x 864 / 784) 18-20 px - kuweta i zab; przy
150 % (1280 x 720 / 642) 14 px - sama kuweta (zab i miniatura w widoku pracy). Rynienka (gniazdo 1): wszystko w jednej linii.

## Zasady

- **Stan i polecenia** jak na ekranie wieczornym (`ui_wieczor.md`): sygnatury czesci, przebudowa tylko zmienionych; polecenia
  przez `okno._polecenie` (odmowa = komunikat albo panel "Nie mozna tego zrobic"); zadnych okien modalnych.
- **Kolory i napisy** tylko ze stanu i `statusy` (wiersze poranne `rano_*`, `nieznana_rano`, `dofrezowany`, `rano_juz_rozpoznany`).
  Z9: zab dofrezowany do zlecenia juz odhaczonego - bursztyn "zab dofrezowany"; przy zleceniu z brakami (A6 D2) - ten sam
  bursztyn, napis "zab juz rozpoznany"; "poprawiana recznie" (pomaranczowy) to inne znaczenie.
- **Klawiatura** (jak ramka poranna): cyfry i "#" = numer kuwety (napis "Wpisany numer kuwety: ..."), Enter = wybierz wpisana
  kuwete albo potwierdz biezaca, Backspace = popraw numer albo cofnij ostatnie potwierdzenie, Esc = wyczysc numer albo zamknij
  widok pracy; Spacja = start skanu (okno). Pole numeru kuwety w przypisaniu recznym zabiera cyfry tylko, gdy ma fokus.
- **Ochrona przed kliknieciem w poprzedni obraz:** po zmianie zestawu plytek (nowa plytka, zastapienie) mapy sa przez 800 ms
  przygaszone i nie przyjmuja klikniec.
- **"Zamknij piec"** zamyka POKAZANY piec (`sesja_pieca_id`), jest nieaktywne, dopoki sa blokady albo trwa analiza skanu
  (napis "Trwa analiza skanu"), i bez wybranej osoby.
- **Dane osobowe:** na ekranie nie ma sciezek ani nazw plikow / folderow (test przechodzi po calym drzewie widzetow).

## Kryterium "dziala"

`testy/test_ui_rano.py` (24 testy, offscreen, atrapa i prawdziwa `Aplikacja`): (1) 3 plytki x 24 gniazda - kolor (dane
i piksel), kuweta, zab i miniatura = tabela oczekiwan i `session_rano.stan_pieca` w 72 z 72 gniazd (atrapa i prawdziwy
kontroler przez folder skanera); (2) zolte gniazdo -> dwie karty kandydatow, wybor = decyzja `wybor_kandydata` i zielony
kolor, cofniecie; (3) kolejnosc kuwet = `plan_plytek` A6 dla "liczba" i "numer", numer wpisany cyframi + Enter, Enter /
Backspace; (4) "Zamknij piec" - tabele kompletne i braki = `wynik_pieca` A6, lista brakow = `braki()`; (5) komunikaty ramki
i Excela, program dziala dalej (nastepny piec); A6 runda 2 (pominiecie skanu, reczne zamkniecie braku, ponowne otwarcie,
"Zamknij piec" w trakcie analizy); nieznana przypisana recznie, konflikt, poprawka (Z9), plytka bez numeru i ponowny skan;
przelacznik trybu i tryb po restarcie; okno zmaksymalizowane; uklad bez obciec przy 1920 x 1080 / 1001, 1536 x 864 / 784,
1280 x 720 / 642 dla 6 scen (takze z `QT_SCALE_FACTOR` 1,25 i 1,5); przerwy petli okna ponizej 200 ms przy 3 plytkach x 23
prace (prawdziwy kontroler); 0 sciezek; szesc zadan porannych T14. Zrzuty: zmienna `E3_ZRZUTY`.

## Zalozenia i granice

- Okna nie uruchomiono na prawdziwym ekranie (tryb offscreen, jak ekran wieczorny); wyglad zatwierdza wlasciciel (G2).
- Potwierdzenia rozlozenia kuwet sa dziennikiem (`kuweta_potwierdzona` / `kuweta_cofnieta`), nie zmieniaja kompletu (komplet
  liczy sie ze skanow - A6); kolejnosc kuwet nie przezywa restartu (domyslnie "od najliczniejszej").
- Pokazywany jest piec otwarty albo ostatni piec biezacej doby; wczesniejszych piecow doby ekran nie pokazuje (lista brakow -
  tak). Odhaczen w Excelu `otworz_piec_ponownie` nie zdejmuje (A6, A9).
- Miniatury z indeksu (`cechy_stl.miniatura`, A4) - projekt bez miniatury: napis "brak miniatury".
