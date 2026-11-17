# ui_wieczor - ekran trybu "Wieczor" programu "Stanowisko" (paczka E3-A3b, 17.11.2026)

**Co robi.** Pakiet `stanowisko/ui/` to okno, ktore technik widzi wieczorem: mapa zeskanowanej plytki, widok pracy z decyzja "Ukruszona" / "OK", lista "do dofrezowania", pytania i komunikaty. Okno NICZEGO nie liczy: pokazuje `kontroler.stan()` i wysyla polecenia kontrolera (kontrakt: `stanowisko/kontroler_api.py`, opis: `aplikacja.md`). Wejscie: `stanowisko.ui.utworz_okno(kontroler, lacznik)` - wolane z `aplikacja.main()`; pokaz na danych sztucznych: `py -3.12 -m stanowisko.aplikacja --atrapa`.

| Plik | Rola |
|---|---|
| `ui/__init__.py` | `utworz_okno`; bez Qt na poziomie modulu (PySide6 ladowane w calosci dopiero w `utworz_okno`) |
| `ui/okno.py` | `OknoWieczor`: sklada ekran, trzyma wybor technika, obsluguje klawisze, wysyla polecenia |
| `ui/czesci.py` | pasek stanu, wybor osoby, panele pytan i komunikatow, lista plytek, widok pracy, lista "do dofrezowania", legenda |
| `ui/mapa.py` | `MapaPlytki`: gniazda ukladu w kolorach i z podpisami ze stanu; `geometria_ukladu` (ksztalt z `uklad.wczytaj`) |
| `ui/obraz.py` | obraz odchylek pracy liczony w watku pomocniczym (`WczytywaczObrazow`) |
| `ui/napisy.py` | napisy ekranu, ktorych nie ma w `statusy` (UTF-8, polskie znaki) |
| `ui/styl.py` | czcionka, rozmiary, kolory tla i ramek, trzy poziomy komunikatu; ZADNYCH kolorow statusow |

Testy: `testy/test_ui_wieczor.py` (offscreen; okno sterowane kliknieciami i klawiszami na `AtrapaKontrolera` i na prawdziwej `Aplikacja` z plikami zapisywanymi do folderu skanera).

## Uklad ekranu (1600 x 900; minimum 1280 x 760)

- **Pasek stanu (gora):** tryb, doba robocza i zmiana, osoba (+ "Zmien"), napis puli ze stanu (+ "Odswiez pule"; w stanie `liczenie` przycisk nieaktywny i pasek obok), skaner (gotowy / czekam na skan / plik zajety / brak folderu / nie dziala), analiza (procent + pasek, "w kolejce: n", skany wstrzymane jako "czekaja na projekty w puli: n" albo "czekaja na uruchomienie analizy: n" - to nie blad), duzy przycisk "Skanuj (Spacja)".
- **Panele uwag (pod paskiem, nad lista plytek i mapa):** wybor osoby ("Kto teraz pracuje?" z przyciskiem na kazda osobe), tekst odmowy polecenia spoza stanu, reczny numer plytki, otwarte pytania pokazanej plytki (`stan.pytania`), jej komunikaty, komunikaty ogolne od najnowszego (jednakowe jako jeden panel z licznikiem). Najwyzej 3 panele naraz + "i jeszcze n". Zadnych okien modalnych.
- **Lista plytek (lewa):** kafelek na plytke - numer, godzina skanu, status skanu (`Plytka.napis`), liczniki prac wg klasy koloru (`Plytka.liczniki`, kolory ze `statusy`), znaczniki "NOWA" i "czeka na odpowiedz". Domyslnie plytki biezacej zmiany; wczesniejsze zmiany tej doby pod przyciskiem.
- **Mapa (srodek):** wszystkie gniazda ukladu; kolor = `Gniazdo.rgb`, podpis = `Gniazdo.podpis`; wyciecie orientacyjne i napis "PRZOD PLYTKI"; pod mapa prace poza gniazdami i legenda statusow obecnych na tej plytce. Skan, ktory sie nie liczy i nie ma prac (nie pasuje do ukladu, blad analizy) - napis zamiast gniazd.
- **Prawa kolumna (stale miejsce - przyciski decyzji nie przesuwaja sie, gdy przychodzi komunikat):** widok pracy (status i opis ze stanu, kuweta / zab / krazek, najwiekszy ubytek i liczba ubytkow, obraz odchylek, "ten zab jest juz na liscie", zapisana decyzja, duze "Ukruszona" / "OK", "Cofnij decyzje", "Nastepna", "Zamknij") oraz lista "do dofrezowania" (kuweta, zab, krazek, plytka, gniazdo, doba, zmiana; "Ta doba" domyslnie / "Wszystkie otwarte"; klikniecie pozycji pokazuje prace).

## Zasady (kontrakt)

- **Stan.** `lacznik.stan_zmieniony` -> `pokaz_stan(stan)`; stan o nizszej `wersja` niz pokazany jest pomijany. Kazda czesc ekranu ma sygnature swoich danych i przebudowuje sie tylko po ich zmianie; `lacznik.postep` odswieza sam pasek. Wlasny stan okna to wylacznie wybor technika: pokazana plytka, wybrane gniazdo, filtr listy, otwarty panel zmiany osoby / numeru plytki, tekst ostatniej odmowy spoza stanu.
- **Polecenia.** Wylacznie `kontroler.wykonaj(nazwa, *argumenty)` w watku okna. Odmowa to `Odpowiedz`: zwykle jest tez komunikatem w stanie (panel jak kazdy inny); gdy stan jej nie zawiera (np. `zle_argumenty`), okno pokazuje `Odpowiedz.tekst` w panelu "Nie mozna tego zrobic". Wyjatek z polecenia jest logowany, okno dziala dalej.
- **Kolory i napisy statusow.** Tylko pola stanu (`rgb`, `podpis`, `opis`, `napis`) i `statusy` (`STATUSY`, `PRZYCISKI`, `KOMUNIKATY`, `status()` dla klucza nieznanego). Ekran nie zaklada zamknietej listy statusow, rodzajow komunikatow ani stanow puli: nieznany klucz wyglada tak, jak podaje stan. Przyciski "Ukruszona" / "OK" maja kolor gniazda po tej decyzji (`statusy`). `styl.py` nie ma zieleni - zielone na ekranie znaczy tylko "praca sprawdzona" i pochodzi ze stanu.
- **Dane osobowe.** Na ekranie nie ma sciezek ani nazw plikow / folderow: folder puli i skanera (`pula.folder`, `skaner.folder`) nie sa pokazywane, plik podgladu sluzy tylko do wczytania obrazu, po "Zapisz liste" ekran pisze "Lista zapisana." bez nazwy pliku. Test przechodzi po calym drzewie widzetow (takze podpowiedzi i napisy rysowane na mapie).
- **Klawiatura.** Zaden przycisk nie przyjmuje fokusu (`NoFocus`) - klawisze obsluguje okno: Spacja = `start_skanu` (raz na nacisniecie, autopowtarzanie pomijane; nigdy "klikniecie" ostatniego przycisku), U / O / C = decyzje przy otwartej pracy i aktywnym przycisku, N = nastepna praca do obejrzenia, Esc = zamknij widok pracy.
- **Osoba.** Bez wybranej osoby przyciski decyzji i odpowiedzi wymagajace osoby sa nieaktywne, a obok jest wyjasnienie ze `statusy` (`brak_operatora` / `pusta_lista_operatorow`); "Pozniej", "Zeskanuje wlasciwa plytke", "Zamknij", "Odswiez pule" i Spacja dzialaja bez osoby.
- **Plytka.** Polecenia plytki z `Plytka.dozwolone` sa przy naglowku mapy ("Podaj numer plytki" - panel z cyframi, "Dopusc te plytke", "Cofnij zastapienie", "Cofnij dopuszczenie"); te, o ktore pyta otwarte pytanie, sa tylko w panelu pytania. Dzieki temu po "Pozniej" numer i dopuszczenie sa nadal dostepne.
- **Nowa plytka.** Wynik nowej plytki przelacza na nia ekran, chyba ze technik ma otwarta prace - wtedy kafelek dostaje znaczek "NOWA".
- **Watek i czas.** Wszystko w watku okna poza obrazem odchylek: `szczegoly_pracy(praca_id)` (watek okna) podaje plik podgladu, watek pomocniczy czyta plik (`kontroler_api.wczytaj_podglad`, gdy kontrakt ja ma; inaczej wlasny odczyt numpy) i rysuje `QImage`, do okna wraca sygnal. Zmierzone: odswiezenie ekranu po sygnale stanu do 7 ms przy 10 plytkach x 19 prac, najdluzsza przerwa petli okna 48 ms (liczby: raport paczki).

## Kryterium "dziala"

`testy/test_ui_wieczor.py`: (1) kolor (dane i piksel obrazu widzetu) i podpis kazdego gniazda = stan dla 7 rodzajow skanu atrapy, scenariusza pokazowego i prawdziwego kontrolera; (2) widok pracy z rozmiarem ubytku, polecenia decyzji i lista; (3) Spacja = jeden start skanu; (4) kazde pytanie i komunikat: panel, przyciski, nic zielonego, osoba; (5) ponowne otwarcie okna = ten sam obraz co do piksela, restart programu = ta sama mapa, kafelki i lista; (6) przerwy petli okna; (7) pula; (8) 0 sciezek i nazw plikow; (9) piec zadan wieczornych T14 sterowaniem z testu.

## Zalozenia i granice

- Okna na prawdziwym ekranie nie uruchomiono (testy i zrzuty: tryb offscreen); wyglad zatwierdza wlasciciel na pokazie G1. Skalowanie ekranu (DPI) inne niz 100 % i rozdzielczosc ponizej 1280 x 760 - niesprawdzone.
- Geometria mapy: `uklad.wczytaj(nazwa)` z katalogu jak w kontrolerze (atrybut `ust` kontrolera, gdy jest); gdy ukladu nie da sie wczytac, gniazda sa rysowane w kratke.
- Prog kolorowania obrazu odchylek (0,08 mm) jest stala ekranu - stan go nie podaje. Kolka ubytkow sa rysowane we wspolrzednych plytki (jak w `porownaj`); atrapa podaje ubytki wzgledem srodka gniazda, wiec na danych sztucznych kolka nie ma.
- Dwie prace w gniezdzie: widok pokazuje status gniazda i jedna prace naraz (przelacznik "praca 1 z 2").
- "Nastepna do obejrzenia" wybiera gniazdo z praca bez decyzji, z dozwolona decyzja i statusem innym niz zielony - to ulatwienie nawigacji, nie ocena.
- Ekran poranny, ustawienia na ekranie, wybor folderu puli i wspolczynnika (`ustaw_pule`), rozstrzyganie konfliktu projektu - poza paczka.
