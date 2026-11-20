# Raport recenzenta - PR #40 (E3-A11d: instrukcje dla technika, tabela "co robic, gdy nie dziala", zestaw proby T14) - runda 1

Data: 20.11.2026. Zakres: `git -C <PC-katalog>\qc diff main...e3/a11d`, HEAD c0c38e7 (5 commitow, 22 pliki, same nowe,
2 680 675 B). Kopia do prob: `<PC-katalog>\qc-wt\rec-a11d` (detached c0c38e7; po probach `git status --short` pusty).
Pliki robocze: `<PC-katalog>\koordynator\robocze\rec-a11d\` (skrypty `proby.py`, `mutacje.py`, `cytaty_analiza.py`,
`druk.py`, `pdf_png.py`; zrzuty `zrzuty1`, `zrzuty2`, `proby_png`, wydruki `pdf`, klon `klon`).

Metoda: (1) wlasny przeglad diffu i kodu ekranow (`statusy.py`, `ui/napisy.py`, `ui/napisy_rano.py`, `ui/okno.py`,
`ui/czesci.py`, `ui/ekran_rano.py`, `ui/kandydaci.py`, `ui/okno_excela.py`, fragmenty `kontroler_api.py`, `aplikacja.py`,
`session.py`); (2) przejscie krokow instrukcji na prawdziwym oknie programu bez ekranu (Qt offscreen, atrapa kontrolera) -
wlasny skrypt `proby.py`, 8 prob, wynik czytany z ekranu i z 12 wlasnych zrzutow; (3) obejrzenie 9 z 9 obrazkow
(wydobytych z `.html` i odtworzonych skryptem) oraz 5 z 5 wydrukow PDF jako obrazow stron; (4) druk `.html` do PDF
przegladarka bez okna i liczenie stron w dwoch orientacjach; (5) wstrzykniecie 14 bledow w kopii (napisy programu,
obrazki, cytaty nieoznaczone); (6) odtworzenie zestawu T14 z czystego `git archive`. Raport wykonawcy czytany na koncu.
Pelnego pytest nie powtarzano (zasada 3). Kazda liczba ponizej jest z mojego pomiaru, chyba ze oznaczono inaczej.

Czego NIE sprawdzilem: okna na prawdziwym ekranie, druku na papierze, ramek i Excela na sprzecie, programu z prawdziwym
skanerem i silnikiem (wszystkie proby na atrapie kontrolera), przegladarek innych niz Chrome (Edge i Firefox nie ma na PC).

## 0. Werdykt

**Do scalenia po poprawkach.** B 1, P 5, D 11.

Instrukcje sa w wiekszosci prawdziwe (kazdy cytowany napis istnieje, kolejnosc krokow porannych i wieczornych da sie
przejsc na oknie programu, kolory i znaczenie decyzji "Ukruszona" / "OK" zgodne z `statusy.py` i `session.py`), narzedzia
sa powtarzalne co do bajta, zestaw T14 odtwarza sie od zera. Do poprawy przed scaleniem: jeden wiersz tabeli, ktory
uspokaja technika w sytuacji, w ktorej decyzja przepada (B1), dwa miejsca, w ktorych instrukcja wieczorna nie zgadza sie
z tym, co program robi codziennie (P1, P2), obrazek z ostrzezeniem programisty (P3), luka w tescie (P4) i podpowiedz
w obrazku jednej strony T14 (P5).

## 1. Uwagi

| Nr | Waga | Plik:linia | Scenariusz (stan -> co sie dzieje) | Propozycja |
|----|------|-----------|-------------------------------------|------------|
| B1 | B | `instrukcje/co_robic_gdy_nie_dziala.md:14` | Baza zajeta w chwili, gdy technik klika "Ukruszona" (sytuacja T7 "baza zajeta"). Proba P2: klikniecie blokuje okno na 14,9 s, potem panel "Nie mozna tego zrobic - Inny program trzyma baze stanowiska - niczego nie zapisano. Sprobuj ponownie za chwile."; po zwolnieniu bazy i 4 s czekania (przycisku "Ponow zapis" w tym panelu nie bylo): decyzja pracy = brak, gniazdo dalej "UBYTEK", "Do dofrezowania: 0". Program decyzji NIE ponawia (`kontroler_api.py:3187` - odmowa `baza_zajeta`, nic w kolejce). Tabela w jedynym wierszu o bazie mowi: "Wynik czeka, nie zginal. Poczekaj - program ponawia zapis sam." - prawda tylko dla wyniku skanu. Technik, ktory uwierzy tabeli, odklada ukruszona prace, a na liscie do dofrezowania jej nie ma. Tytulu "Nie mozna tego zrobic" tabela w ogole nie ma. | Rozdzielic wiersz: (a) przy plytce "nie zapisano - baza zajeta" - jak dzis; (b) komunikat z trescia "... niczego nie zapisano. Sprobuj ponownie za chwile." po kliknieciu decyzji: "decyzja NIE jest zapisana - poczekaj, kliknij ja jeszcze raz i sprawdz, ze gniazdo ma podpis UKRUSZONA / OK - zatwierdzona, a praca jest na liscie". Zmierzyc druk ponownie (D4). Lepsza naprawa po stronie programu - patrz 7, poz. N1. |
| P1 | P | `instrukcje/wieczor.md:33-37` (kroki 2-3); `etap3/t14/jedna_strona.md:14` | Technik skanuje nastepna plytke, zanim zdecydowal o wszystkich pracach poprzedniej (instrukcja sama kaze "w tym czasie ukladaj nastepna plytke"). Proba P1: po 2 decyzjach z 4 i skanie plytki 2 ekran zostaje na "Plytka 1 - do obejrzenia: 2"; mapy plytki 2, komunikatu "Skan do powtorzenia" i pozniej pytania "Ponowny skan tej samej plytki?" NIE widac, dopoki technik nie kliknie "Pokaz nowy wynik: Plytka 2" nad lista plytek (kafelek ma "NOWA" i "ma komunikat"). Instrukcja wieczorna nie wspomina o "Pokaz nowy wynik"; krok 3 mowi "Po analizie widzisz mape plytki". Jedna strona T14 mowi wprost "Mapa plytki pojawi sie sama" - w zadaniu W4 proby to nieprawda (po W3 zostaja 2 prace bez decyzji; `scenariusz_symulatora.md` wiersz W4 sam to przyznaje). | `wieczor.md` krok 3: jedno zdanie ("gdy ogladasz jeszcze poprzednia plytke, nowa czeka pod przyciskiem "Pokaz nowy wynik" - sprawdzaj numer plytki w naglowku mapy"). `jedna_strona.md`: usunac "pojawi sie sama" albo zmienic scenariusz tak, by W4 nie zalezal od tego przycisku (plytka 1 z 2 pracami do obejrzenia); ile podpowiadac - decyzja wlasciciela (sekcja 5 pkt 1). |
| P2 | P | `instrukcje/wieczor.md:30-32` (krok 1) | Program startuje w OSTATNIO wybranym trybie (`kontroler_api.py:1499-1507`; `aplikacja.main` nie podaje trybu). Proba P3: po przelaczeniu na "Poranek" i ponownym uruchomieniu pasek pokazuje "Tryb: Poranek" i przycisk "-> Wieczor". Czyli kazdego wieczoru po poranku technik widzi "Poranek", a krok 1 mowi tylko "sprawdz: tryb "Wieczor"" - bez slowa, co zrobic, gdy jest inny. Skan plytki wieczornej w trybie porannym konczy sie pytaniem "Plytka nie z tego trybu" i telefonem. `poranek.md` ma odpowiedni krok 1, wieczor nie. | Krok 1: "gdy jest "Poranek", kliknij obok przycisk ze strzalka i napisem "Wieczor"". |
| P3 | P | `narzedzia/zrzuty_instrukcji.py:360-379` (`scena_rano_excel`); `instrukcje/poranek.md:54`, `poranek.html` | Obrazek `rano_excel.png` w instrukcji dla technika zawiera wiersz "... [excel] skoroszyt / arkusz nie sa wskazane w ustawieniach - program uzywa aktywnych: skoroszyt 'Zlecenia_atrapa.xlsx' ...; sprawdz przed pierwszym zatwierdzeniem i wpisz nazwy w ustawienia.toml (D2)" - scena buduje Excela z ustawien wzorcowych bez nazw skoroszytu. To polecenie dla programisty na karcie technika. Dodatkowo obrazek 1350 px jest drukowany na szerokosc ok. 83 mm (92 % kolumny): napisy maja ok. 1 mm, przycisku "Zatwierdz wiersz 9" nie da sie odczytac na wydruku (obejrzane w PDF 150 dpi). | W scenie ustawic `ust["excel"]["skoroszyt"]` / `["arkusz"]` (ostrzezenie zniknie) i wyciac z panelu to, co opisuje krok 7 (lista zlecen + wiersz przyciskow) albo pokazac panel w mniejszym oknie, zeby napisy byly czytelne. |
| P4 | P | `testy/test_instrukcje.py:98-130` (`kluczowe`), `:60-64` | Kryterium 2: "test ma padac, gdy ktos zmieni napis w programie". Wstrzyknalem 8 zmian napisow cytowanych w instrukcjach: 5 wykrytych, 3 NIE: podpis gniazda "nie sprawdzono" -> "bez kontroli" (M1), tytul komunikatu "Wybierz osobe" -> "Wskaz osobe" (M4), podpis "sprawdz ulozenie" -> "krzywo lezy" (M7). Przyczyna: cytat pasuje do drugiego literalu programu (`porownaj.py`, napis przycisku) - 32 ze 156 cytatow maja co najmniej 2 pasujace literaly - a tych trzech stalych nie ma na liscie `kluczowe`. Instrukcja zostaje wtedy z napisem, ktorego nie ma na ekranie, przy zielonym tescie. | Dopisac do `kluczowe`: `s["nie_sprawdzono"].napis`, `s["sprawdz_ulozenie"].napis`, `k["brak_operatora"].tytul`; trwalej: test, ktory dla kazdego cytatu z wiecej niz 1 pasujacym literalem wymaga wpisu w `kluczowe` (wtedy lista nie moze sie zestarzec). |
| P5 | P | `etap3/t14/jedna_strona.md:31` + `narzedzia/zrzuty_instrukcji.py:46-47` (`PIEC`) wobec `etap3/t14/scenariusz_t14.json:27-41` | Obrazek `rano_ekran.png` na kartce osoby badanej pokazuje ten sam piec, ktory osoba dostanie w probie: plytki 4 i 5, kuwety 3221, 3228, 3235, 3242, stan "3221 rozlozona, 3228 teraz, 3242 braki" - czyli ekran PO poprawnym wykonaniu R3 i czesc odpowiedzi na R5 ("kuweta 3242") i R6 ("braki 3242"). Plan T14: "zadnych podpowiedzi". Obrazek wieczorny tej wady nie ma (inne gniazda niz w probie). | Rozdzielic dane: w `scenariusz_t14.json` inne projekty / kuwety i numery plytek (np. 5 i 6) niz w `PIEC`, albo odwrotnie; poprawic `oczekiwane`, arkusz (R5, R6) i `scenariusz_symulatora.md`. |
| D1 | D | `instrukcje/poranek.md:43` | "Po ostatniej plytce kliknij "Zamknij piec"" da sie przeczytac jako "po zeskanowaniu ostatniej plytki". Proba P5: piec zamkniety przed rozkladaniem - przycisk "Rozlozona [Enter]" nieaktywny, obwodek 0 (prowadzenie kuweta po kuwecie znika), a nierozstrzygnieta zolta "nie liczy sie" (kompletne 2 zamiast 3). Jedna strona T14 ma lepiej: "Po ostatniej kuwecie". | "Po rozlozeniu ostatniej kuwety (zolte i biale rozstrzygniete) kliknij ...". |
| D2 | D | `instrukcje/poranek.md:20-21` | Kolumna "Kolor i podpis gniazda": dla konfliktu i zeba dofrezowanego podpisem gniazda jest numer kuwety (proba P5: czerwone '3298', bursztynowe '3200'); slowa "konflikt" i "zab dofrezowany" sa w legendzie "Na plytkach:" i w licznikach nad plytkami. Brak drugiego znaczenia bursztynu ("zab juz rozpoznany" - sprawdz, czy to nie pomylka). | "czerwony z numerem kuwety (w legendzie "konflikt")"; dopisac "zab juz rozpoznany" albo "bursztynowy: kliknij i przeczytaj opis". |
| D3 | D | `instrukcje/wieczor.md:20`, `:56-57` | (a) Zoltego podpisu "blad kontroli" nie ma w tabeli kolorow. (b) Brak ostrzezenia, ze "Tak, to ponowny skan" uniewaznia decyzje poprzedniego skanu: proba P4 - "Do dofrezowania: 1" -> po potwierdzeniu "Do dofrezowania: 0" (program ostrzega o tym w pytaniu). | (a) dopisac do wiersza zoltego; (b) pol zdania: "decyzje z poprzedniego skanu trzeba zaznaczyc od nowa". |
| D4 | D | `narzedzia/instrukcje_html.py:245`; `testy/test_instrukcje.py:41` | Tabela "co robic" miesci sie na stronie z zapasem 1,6 mm (pismo 7,3 pt; pomiar: ostatni wiersz tresci 8,6 mm nad krawedzia przy marginesie 7 mm); `poranek` ma 535 slow przy limicie 535. Poprawki B1, P1, P2 dodaja tekst - limit slow w tescie nie gwarantuje jednej strony (test sam to mowi). | Po poprawkach powtorzyc `instrukcje_html.py --pdf` i podac liczbe stron w raporcie; rozwazyc pismo 8 pt i 2 wiersze mniej. |
| D5 | D | `instrukcje/co_robic_gdy_nie_dziala.md:28` | "Zaraz po aktualizacji: `Wroc_do_poprzedniej.cmd`" - wg umowy A11i powrot po migracji bazy pyta o przywrocenie kopii bazy "z ostrzezeniem, ile wpisow przepadnie". Technik sam przed takim pytaniem. | Dopisac: "na pytanie o przywrocenie kopii bazy nie odpowiadaj - dzwon". |
| D6 | D | `instrukcje/co_robic_gdy_nie_dziala.md:25`, `:22` | (a) "Nie ma Cie na liscie ("Brak listy osob")" - komunikat znaczy "lista jest pusta", nie "brak Twojego nazwiska". (b) "w pasku ciagle "czekam na plik skanu..."" pojawia sie tylko po Spacji / przycisku "Skanuj..."; przy skanie uruchomionym w programie skanera pasek pokazuje "dostepny". | (a) rozdzielic dwa przypadki; (b) "skan nie pojawia sie na liscie plytek, a przy "Analiza" jest "nic nie czeka"". |
| D7 | D | odstepstwo O1 (`instrukcje/*.html`, `etap3/t14/*.html`) | Skutki opisane w sekcji 6. W skrocie: 4 obrazki T14 sa w repo 3 razy; test nie wykryje podmienionego ani nieaktualnego obrazka wpisanego w strone instrukcji (proba O3). | Decyzja wlasciciela (sekcja 5 pkt 4). |
| D8 | D | `etap3/t14/README.md:19` | "Komputer z ekranem 1920 x 1080" bez slowa o skalowaniu. Proba P8: przy oknie 1536 x 864 (= 1920 x 1080 ze skalowaniem 125 %) i 1600 x 900 przycisk "To ten projekt" lezy ponizej dolnej krawedzi widoku pracy (dol przycisku 359 px, widok 282 / 318 px) - zadanie R2 wymaga przewiniecia. Przy 1920 x 1080 (100 %) i 1280 x 720 widoczny. | README: "skalowanie ekranu 100 %" (albo poprawka programu przed proba - sekcja 7 poz. 9). |
| D9 | D | `etap3/t14/symulator_t14.py:150` | Podsumowanie poranne po zamknieciu pieca zawsze podaje "kuwety rozlozone: brak" (log `--sprawdz` po R3 z Enterem: "kuwety rozlozone: brak; biezaca: -"). README kaze porownac podsumowanie z arkuszem - dla R3 i R4 wprowadza w blad. Dziennik nie notuje Enter / Backspace / decyzji osoby, tylko Spacje i skany. | Notowac w dzienniku polecenia osoby (potwierdz / cofnij kuwete, wybor kuwety, decyzje) z godzina albo usunac wiersz. |
| D10 | D | `etap3/t14/scenariusz_symulatora.md:13`; `etap3/t14/jedna_strona.md:40` | (a) Sciezka PC koordynatora `<PC-katalog>\koordynator\narz\py.cmd` w dokumencie dla wlasciciela. (b) "Czego brakuje, pokazuje "Braki w tym piecu: 1"" - w probie bedzie "2" (brak "np."). | (a) zostawic samo `py -3.12` z uwaga o pakietach; (b) dopisac "np.". |
| D11 | D | umowa zapisu (`narzedzia/instrukcje_html.py:60`), `instrukcje/wieczor.md:40-42` | Test sprawdza tylko to, co autor wzial w cudzyslow. Proby: bledna nazwa przycisku bez cudzyslowu ("Przycisk Dalej" zamiast "Nastepna [N]") - nie wykryta (C2); zmiana litery skrotu `KLAWISZ_UKRUSZONA` "U" -> "K" przy "klawisz U" w instrukcji - nie wykryta (M9). Przegladem: nieoznaczonych nazw przyciskow w tresci nie znalazlem; nieoznaczone sa klawisze (U, O, C, N, Enter, Backspace, Spacja) i "OK" okienka systemowego. | Bez zmiany umowy; w tescie porownac litery skrotow z `napisy.KLAWISZ_*` (3 stale). |

## 2. Wlasne proby

| Nr | Polecenie (skrot; `PY` = `<PC-katalog>\koordynator\narz\py.cmd`, katalog `rec-a11d\Ramki\stanowisko`) | Wynik |
|----|------------------------------------------|-------|
| 1 | `PY -m pytest -q -p no:cacheprovider testy/test_instrukcje.py` | 32 passed, 8,3 s (bez `ustawienia.toml`) |
| 2 | `PY narzedzia\zrzuty_instrukcji.py --wyjscie <robocze>` dwa razy | 9 PNG, 777 462 B; sha256 9 z 9 rowne miedzy uruchomieniami, 9 z 9 rowne obrazkom wpisanym w `.html`, 4 z 4 rowne plikom `etap3/t14/obrazki` |
| 3 | `PY narzedzia\instrukcje_html.py --sprawdz` | 5 z 5 stron aktualnych; cytatow 33 / 32 / 49 / 14 / 2, brakujacych 0 |
| 4 | zrzuty + `--t14` + `instrukcje_html.py` w kopii, potem `git status --short` | 0 zmienionych plikow (strony odtwarzaja sie co do bajta, takze bez PNG na dysku) |
| 5 | `druk.py`: Chrome `--headless=new --print-to-pdf`, liczba stron liczona dwoma sposobami (wzorzec `/Type /Page` i QtPdf) | uklad projektowy: wieczor 1, poranek 1, co_robic 1, jedna_strona 1, arkusz 1 (takze z naglowkami przegladarki: 5 x 1). Uklad obrocony o 90 st.: wieczor 2, poranek 2, arkusz 2, co_robic 1, jedna_strona 1 |
| 6 | `pdf_png.py`: strony PDF jako obraz 150 dpi, odleglosc ostatniego wiersza tresci od dolnej krawedzi | wieczor 23,7 mm, poranek 18,5 mm, co_robic 8,6 mm (margines 7 mm), jedna_strona 29,6 mm, arkusz 59,9 mm; 5 z 5 stron obejrzanych |
| 7 | `proby.py p1` - T14 wieczor: 2 decyzje z 4, potem skany plytki 2 | ekran zostaje na plytce 1; komunikat i pytanie plytki 2 niewidoczne; przycisk "Pokaz nowy wynik: Plytka 2", po trzecim skanie "Pokaz nowe wyniki (2)" (P1) |
| 8 | `proby.py p2` - obce polaczenie `BEGIN EXCLUSIVE` na bazie, klik "Ukruszona" | 14,9 s blokady okna; decyzja nie zapisana i nie ponowiona (B1) |
| 9 | `proby.py p3` - ponowne uruchomienie na tej samej bazie po przelaczeniu trybu | tryb "Poranek" (P2) |
| 10 | `proby.py p4` - szare, pomaranczowe, "blad kontroli": decyzje; ponowny skan po "Ukruszona" | decyzje dozwolone dla 3 z 3 (szare + "OK" = "OK - zatwierdzona"); "Tak, to ponowny skan": lista 1 -> 0; na plytce "do ponownego skanu" decyzje niedostepne (zgodne z instrukcja) |
| 11 | `proby.py p5`, `p6` - poranek: podpisy konfliktu / poprawki, blokada "Zamknij piec", zamkniecie za wczesnie, wybor kandydata 1 i 2 | blokada z tekstem nad plytkami (zgodne z krokiem 6); kandydat 1: kompletne 3221, 3228, 3235, braki 3242, 3249 (= arkusz); kandydat 2: brak 3256 dochodzi (= scenariusz) |
| 12 | `proby.py p7`, `p8` - pozycje 8 i 9 listy wykonawcy | potwierdzone (sekcja 7) |
| 13 | `mutacje.py` - 8 zmian napisow programu w kopii | 5 wykrytych (M2, M3, M5, M6, M8), 3 nie (M1, M4, M7) |
| 14 | `mutacje.py` - obrazki: usuniety PNG T14; usuniety `<img>` z `wieczor.html`; usuniete wskazanie w `.md`; podmieniony obrazek w `poranek.html` | 3 wykryte, 1 nie (podmiana) |
| 15 | `mutacje.py` - cytat bez cudzyslowu (C1, C2), litera skrotu (M9) | C1 wykryty (napis kluczowy), C2 i M9 nie |
| 16 | `cytaty_analiza.py` | 12 888 literalow programu; 156 cytatow w 7 dokumentach; 32 z co najmniej 2 pasujacymi literalami; 3 stale bez ochrony w `kluczowe` |
| 17 | `git archive c0c38e7` -> `klon`; w `klon\Ramki\etap3\t14`: `PY symulator_t14.py --sprawdz` | kod 0, "zgodne 18 z 18 krokow" |
| 18 | tamze: `PY symulator_t14.py wieczor --dziennik t14_wieczor.log --zamknij-po 3` i `rano` | kod 0 i 0; dzienniki 250 B i 280 B, ASCII; bez trybu - blad argumentow; zly `--program` - komunikat BLAD |
| 19 | `PY -m stanowisko.aplikacja --atrapa --zamknij-po 2` i `--atrapa --rano` | kod 0 i 0 |
| 20 | pliki galezi: bajty z `git cat-file` | 18 plikow tekstowych: CR 0, znakow spoza ASCII 0, kazdy konczy sie LF; 4 PNG: fragmenty IHDR, pHYs, IDAT, IEND (bez tekstu); szukanie "<uzytkownik>", "C:\Users", "Desktop": 0 trafien |

## 3. Kryteria zlecenia

| Nr | Kryterium | Ocena |
|----|-----------|-------|
| 1 | Trzy instrukcje i jedna strona T14 na 1 stronie A4 | **potwierdzone wlasna proba** (druk do PDF w Chrome: 4 z 4 po 1 stronie w ukladzie zaprojektowanym; arkusz 1). Zastrzezenia: w ukladzie obroconym wieczor i poranek maja 2 strony (`@page` wymusza wlasciwy uklad w Chrome; innej przegladarki nie bylo); zapas tabeli 1,6 mm (D4); druku na papierze nie zmierzono. |
| 2 | `test_instrukcje.py`: cytaty istnieja, obrazki istnieja, ASCII; pada po zmianie napisu | **niepotwierdzone w czesci**: istnienie cytatow i ASCII potwierdzone (proby 1, 3, 20); "pada po zmianie napisu" - 5 z 8 (P4); obrazek - 3 z 4 (D7). |
| 3 | Tabela "co robic": wiersz na kazda sytuacje | **potwierdzone przegladem i proba**: 22 wiersze, 4 kolumny; 13 z 13 sytuacji ze zlecenia ma wiersz; 49 z 49 cytatow istnieje w kodzie (sprawdzone wlasnym indeksem i czytaniem `statusy.py`). Tresc jednego wiersza bledna (B1). Kody samokontroli nie sa cytowane (O2 wykonawcy) - slowa wiersza zgodne z `samokontrola.py` galezi `e3/a11s` (c67fbe5: 5 z 5 slow obecnych, format "poziom kod: opis; rada"). Rozbieznosci z PW zal. F - sekcja 4. |
| 4 | Zrzuty: polecenie odtwarza komplet; kazdy obejrzany | **potwierdzone wlasna proba** (proba 2; 9 z 9 obejrzanych przeze mnie). |
| 5 | Scenariusz T14 odtworzony od zera | **potwierdzone wlasna proba** w czesci automatycznej (proby 17, 18); przebieg z czlowiekiem i na ekranie niesprawdzony. `scenariusz_symulatora` obejmuje 11 z 11 zadan planu (W1-W5, R1-R6), `arkusz_obserwacji` ma 11 zadan, pola "wykonane", "interwencja", "zawahanie ponad 10 s", podsumowanie "z 11" i kryterium zaliczenia doslownie z planu. |
| 6 | Pelny pytest: 0 failed | **nie powtarzano**; wg wykonawcy 1861 passed, 9 skipped, 0 failed w przebiegu 2 (niesprawdzone - log sprawdza koordynator). |

Prawdziwosc krokow (przeglad + proby): `wieczor.md` - 6 krokow i sekcja o ponownym skanie: wszystkie przyciski i napisy
istnieja; niezgodnosci P1, P2, D3. `poranek.md` - 7 krokow: wszystkie przyciski i napisy istnieja; kolejnosc wykonalna;
niezgodnosci D1, D2; zdania o ramce (zielone diody, klawisze ramki) zgodne z PW (wiersze 123, 183) - bez sprzetu
niesprawdzone. Znaczenie kolorow: zielone tylko dla pracy rozpoznanej bez ubytku; czerwone, zolte, szare i pomaranczowe
czekaja na decyzje (licznik "do obejrzenia" liczy wszystkie cztery); "Ukruszona" dopisuje do listy, "OK" daje
"OK - zatwierdzona" - zgodne z programem.

## 4. Zakres plikow i zasady

- Zmienione pliki: 22, wszystkie z listy zlecenia; `.gitignore`, kod programu, `README.md`, `opisy_modulow/**` nietkniete.
  Katalogu `instrukcje/obrazki/` w repo nie ma (O1).
- ASCII, LF, bez znakow diakrytycznych: 18 z 18 plikow tekstowych. Commity: 5, przedrostek "E3-A11d:", stopka
  Co-Authored-By w 5 z 5.
- Dane osobowe: na obrazkach "Technik A", kuwety 9002 i 32xx, "3221 Fikcja Rano", "Starsza Osoba 3221",
  'Zlecenia_atrapa.xlsx' - dane sztuczne; sciezek z nazwa uzytkownika na obrazkach i w plikach brak.
- Duze dane: razem 2 680 675 B (strony `.html` 1 910 518 B, PNG T14 629 556 B) - ponizej ok. 3 MB ze zlecenia; bez STL.
- Tabela a PW zal. F (12 wierszy PW): 8 ma odpowiednik (skan sie nie pojawia, szare gniazda, drgniecie, numer plytki,
  diody, ramka poranna bez sieci, Excel, program nie startuje); "plytka nie pasuje do wybranego ukladu" - program nie ma
  wyboru ukladu, wiersz mowi o ponownym skanie (rozbieznosc opisana przez wykonawce, zgodna z kodem); "klawiatura" -
  skrocone do "wymien baterie"; "ramka nie widzi plytki" i "ramka nie wstaje" - pominiete (sprzet). Rady: zadna nie kaze
  kasowac bazy ani plikow; uwagi do bezpieczenstwa: B1, D5.

## 5. Do decyzji wlasciciela (nie blokuje)

1. **Ile moze mowic jedna strona T14.** Plan: "jedna strona z obrazkami i zadnych podpowiedzi". Kartka ma 12 punktow, ktore
   w tej samej kolejnosci odpowiadaja na 11 zadan (lacznie z nazwa przycisku odpowiedzi "Tak, to ponowny skan", klawiszami
   Enter / Backspace i "wpisz numer cyframi"). To skrot instrukcji, nie sama orientacja po ekranie - proba sprawdzi wtedy
   "czy czlowiek umie isc za kartka", a nie "czy ekran tlumaczy sie sam". Moim zdaniem miesci sie w literze planu
   (kartka jest jedyna pomoca), ale warto to potwierdzic przed proba; niezaleznie od decyzji P1 i P5 wymagaja poprawki.
2. **O3 - czy proba na atrapie kontrolera wystarcza do zaliczenia T14 w etapie 3** (ocena w sekcji 6).
3. **Pula z folderu czy pula per praca** (`[silnik] pula_wpisow`): instrukcje cytuja napisy puli z folderu ("plikow
   projektow: n", "Brak projektow w puli"); przy puli per praca pasek i komunikaty sa inne ("wpisow puli: n", "Brak wpisow
   puli dnia", "Katalog zlecen niedostepny", "Plytka bez swojej puli", "Prace bez wspolczynnika w puli") i nie maja
   wierszy w tabeli. Wzor ustawien ma `pula_wpisow = false`; jesli stanowisko ruszy z `true`, krok 1 wieczoru i 2 wiersze
   tabeli trzeba zmienic przed drukiem.
4. **O1 - obrazki instrukcji jako pliki w repo** (wyjatek w `.gitignore` i w `test_ustawienia.py`) czy tylko w stronach.
5. **B1 po stronie programu**: czy decyzja odrzucona przez zajeta baze ma byc ponawiana / wyrazniej zgloszona (N1).
6. Telefon i progi "kiedy dzwonic" (przyjete przez wykonawce); pisownia wydrukow bez polskich znakow przy cytatach z polskimi.
7. Ktore pozycje z sekcji 7 poprawic przed proba T14 (moja lista: 6, 8, 9, N2).

## 6. Odstepstwa O1 i O3 - ocena

**O1 (PNG wpisane w `.html`).** Uzasadnienie wykonawcy sprawdzilem: `test_ustawienia.py` wymaga, by git nie sledzil zadnego
`.png` w `Ramki/stanowisko` - bez zmiany pliku spoza zakresu inaczej sie nie dalo. Skutki: (a) rozmiar - strony `.html` to
1 910 518 B z 2 680 675 B paczki; 4 obrazki T14 sa w repo trzy razy (PNG 629 556 B + base64 w `jedna_strona.html` + base64
w `wieczor.html` / `poranek.html`); kazda zmiana wygladu okna = nowe ok. 1,9 MB w historii (base64 PNG nie delta-kompresuje
sie). (b) Odtwarzalnosc - dobra: trzy polecenia (`zrzuty_instrukcji.py`, `zrzuty_instrukcji.py --t14`,
`instrukcje_html.py`) daja pliki rowne co do bajta (proby 2 i 4); na innym komputerze (inne czcionki, inna wersja Qt)
bajty moga sie roznic - wtedy `test_strona_do_druku_jest_aktualna` pada tylko, gdy PNG leza na dysku. (c) Slabosc: na
czystej kopii strona jest zrodlem samej siebie - test nie wykryje obrazka podmienionego ani nieaktualnego po zmianie
wygladu okna (proba 14: 1 z 4 nie wykryta); pilnuje tego tylko czlowiek ("OBEJRZYJ kazdy PNG"). Do przyjecia na teraz;
docelowo wariant z POTRZEBUJE 1 wykonawcy (PNG jako pliki, strona wskazuje pliki albo jest budowana przy wydaniu).

**O3 (symulator T14 = atrapa kontrolera, skaner udawany Spacja).** Okno i reguly sesji sa prawdziwe (ta sama `Sesja`,
te same polecenia), wiec proba uczciwie sprawdza to, o co pyta T14: czy czlowiek rozumie mape, kolory, decyzje, komunikat
o ponownym skanie, liste, wybor kandydata, rozkladanie, cofanie, szukanie kuwety, zamkniecie pieca i braki (11 z 11
zadan osiagalnych - proby 17, 7, 11). Czego osoba w takiej probie NIE przecwiczy: (1) prawdziwego startu skanu - w pracy
skan uruchamia sie w programie skanera, a przycisk programu mowi "Skanuj w programie skanera / Spacja: program czeka na
plik"; proba uczy "Spacja = skan"; (2) czekania 60-90 s na skan i analize i pracy rownoleglej (tu 8 s), kolejki skanow;
(3) prawdziwych obrazow odchylek i miniatur projektow (tu losowe punkty i plamy), czyli samej oceny "ukruszona czy cala";
(4) komunikatow sciezki skanera i puli (plik zajety, plik uciety, brak projektow); (5) ramek (R3 tylko "wedlug ekranu")
i Excela - zamiast nich osoba widzi dwa komunikaty o braku ramki i Excela; (6) przekladania prac (opcjonalne w README).
Czy da sie uruchomic T14 na prawdziwym potoku: wieczor - tak, rozsadnym kosztem, na danych testu T2 (`synth` generuje
plytki z ubytkami i drgnieciem, `atrapy_koron.py` projekty, `symulator_skanera.py` wrzuca pliki; "skan poruszony" zastapi
"popraw ulozenie"); poranek - trudniej (praca dwuznaczna wymaga dwoch bardzo podobnych projektow w puli; nie sprawdzalem,
czy `synth` da to powtarzalnie), a skan trwa wtedy ok. 40 s na plytke. Rekomendacja: atrapa wystarcza na etap 3 (plan i tak
wymaga powtorki T14 z prawdziwym skanerem przed praca produkcyjna), pod warunkiem poprawek P1 i P5 i ekranu 100 % (D8);
wynik zapisac w raporcie odbioru jako "T14 na atrapie".

## 7. Lista wykonawcy "zauwazone w programie" (12 pozycji) - potwierdzenie i waga dla T14

| Nr | Pozycja wykonawcy | Moja ocena | Dowod | Przeszkadza w T14 |
|----|-------------------|------------|-------|-------------------|
| 1 | Panel Excela: ostrzezenie "[excel] skoroszyt / arkusz ... ustawienia.toml (D2)" | potwierdzam | `rano_excel.png` (obejrzany); pojawia sie, gdy ustawienia nie maja nazw skoroszytu | nie (Excel poza T14); jest na obrazku instrukcji - P3 |
| 2 | Panel Excela: "regula 2: nazwa w H zgodna z nazwa folderu ..." | potwierdzam | `rano_excel.png` | nie |
| 3 | "Lista brakow (wszystkie piece)": kolumna "Stan" ucieta ("nie wyszedl z ...") | potwierdzam | `rano_braki.png`; pierwsza tabela "Braki w tym piecu" ma pelny napis | nie (R6 czyta pierwsza tabele) |
| 4 | Pusta lista: "Lista jest pusta. Lista zapisana do pliku o 19:00" | potwierdzam | `wieczor_ekran.png`, zrzut `p7` | nie |
| 5 | Napisy puli per praca i "Krazek do wyboru" bez polskich znakow | potwierdzam | `statusy.py:341-352`, `:517-541`; `ui/napisy.py:100-103` | nie (atrapa pokazuje napisy puli z folderu) |
| 6 | Przycisk "Skanuj w programie skanera / Spacja: program czeka na plik" wyglada jak start skanu | potwierdzam | `ui/czesci.py:42`, `:472`; widoczny na 2 obrazkach kartki T14 | **tak** (W1, R1: kartka mowi "skan uruchamiasz klawiszem Spacja", przycisk mowi o programie skanera; klikniecie przycisku dziala w symulatorze jak Spacja) |
| 7 | Widok zoltej pracy rano: "kliknij gniazdo i wybierz ..." po kliknieciu gniazda | potwierdzam | `rano_kandydaci.png` | nie (drobne, R2) |
| 8 | Pytanie o ponowny skan przed odpowiedzia: nowy skan "Plytka 2 - sprawdzona", dwa kafelki "Plytka 2" | potwierdzam | proba P7: naglowek "Plytka 2 - sprawdzona", podpisy 4 x "OK", kafelki "do ponownego skanu" i "przeanalizowana / czeka na odpowiedz" | **tak** (W4) |
| 9 | Rano przy 1600 x 900 przycisk "To ten projekt" ponizej widoku pracy | potwierdzam i rozszerzam | proba P8: niewidoczny takze przy 1536 x 864 (laptop 1920 x 1080 ze skalowaniem 125 %); widoczny przy 1920 x 1080 i 1280 x 720 | **tak** przy skalowaniu 125 % (R2) |
| 10 | Przelacznik trybu "-> Poranek" obok "Tryb: Wieczor" | potwierdzam | zrzuty; `ui/napisy_rano.py:10` | nie (przelaczanie nie jest zadaniem T14); wazne dla P2 |
| 11 | Okienka startowe bez polskich znakow | potwierdzam | `aplikacja.py:285`, `:1691`, `:1709` (okienek nie ogladalem na ekranie) | nie |
| 12 | Lista do dofrezowania: tylko zapis pliku, bez druku / wysylki | potwierdzam | `statusy.py:385` ("Lista ... zapisana do pliku {plik} w folderze danych programu") | nie |

Dodatkowe obserwacje recenzenta (program, poza zakresem paczki):

| Nr | Ekran | Co widac | Przeszkadza w T14 |
|----|-------|----------|-------------------|
| N1 | Wieczor, decyzja przy zajetej bazie | okno nie reaguje 14,9 s; potem panel "Nie mozna tego zrobic" z trescia o bazie; decyzja przepada bez ponowienia; gdy stan da sie odswiezyc, komunikat `baza_zajeta` dostaje przycisk "Ponow zapis" (`ui/czesci.py:767`), ktory ponawia zapis wynikow skanow, nie decyzji | nie (dotyczy T7 i B1) |
| N2 | Wieczor, nowa plytka przy niedokonczonej poprzedniej | komunikat i pytanie nowej plytki sa niewidoczne do klikniecia "Pokaz nowy wynik"; jedyne sygnaly: przycisk nad lista, znaczki "NOWA" / "ma komunikat", blysk paska 1,5 s | **tak** (W4 - najbardziej prawdopodobne miejsce zawahania) |
| N3 | Poranek, "Zamknij piec" przy nierozstrzygnietej zoltej pracy | zamkniecie dozwolone; praca "nie liczy sie", zlecenia nie ma ani w kompletnych, ani w brakach pieca (napis "Nierozstrzygniete (nie licza sie): wybierz 1") | tak, gdy osoba pominie R2 (wtedy R6 da inne listy niz w arkuszu) |
