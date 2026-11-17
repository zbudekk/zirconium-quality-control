# Plan etapu 3: pelna aplikacja stanowiska kontroli cyrkonii

Data: 2026-11-16 (rozpoznanie 15.11.2026). Autor: planista sesji qc. Stan: ZATWIERDZONY na bramce G0 17.11.2026 (odpowiedzi doslownie: `00_NADZOR_STAN.md`, sekcja "Etap 3").
Adresaci: wlasciciel (sekcje 1, 5, 6, 8, 13) i koordynatorzy paczek etapu 3 (sekcje 3, 4, 9, 11).
Podstawa: decyzja wlasciciela z 15.11.2026 - planowanie pelnej aplikacji stanowiska zaczynamy teraz.
W projekcie nie zmieniono nic poza tym plikiem; zadnego kodu ani testow nie uruchamiano (liczby pochodza z raportow).
"Etap 3" = moduly `session`, `ui`, `indicate`, `excel`, `scanner` i integracja (tak nazywa je wczesniejsza linia kodu,
zrodlo H, oraz PW "Oprogramowanie: moduly i jak powstanie", kroki 3-4).

Spis: 0 skroty zrodel - 1 cel i granice - 2 fakty - 3 architektura - 4 paczki - 5 kolejnosc i sciezka krytyczna -
6 bramki i decyzje - 7 testy koncowe - 8 dystrybucja - 9 zasady wspolne - 10 ryzyka - 11 trzy pierwsze paczki
(prompty) - 12 braki w zrodlach i rzeczy niezweryfikowane - 13 zadania czlowieka przed startem.

## 0. Skroty zrodel i oznaczenia

| Skrot | Zrodlo |
|---|---|
| PW | `Ramki/`, dokument glowny "Stanowisko kontroli cyrkonii - plan wdrozenia v2" (`.md`; w nazwie pliku jest pauza) - z nazwa sekcji |
| OM | `Ramki/stanowisko/opisy_modulow/<plik>.md` |
| RD | `Ramki/stanowisko/README.md` |
| UT | `Ramki/stanowisko/ustawienia.przyklad.toml` i `stanowisko/ustawienia.py` (`SCHEMAT`) |
| P3a | `Ramki/stanowisko/raporty/P3a_przekazanie.md` |
| R59 | `Ramki/stanowisko/raporty/R59_2026-11-14.md` |
| WD | `origin/bp/fable-5-2:Ramki/stanowisko/raporty/testy_krawedz/WNIOSKI_I_DECYZJE_2026-11-09.md` |
| F2 | `<MSI>\kod\qc\Ramki\stanowisko\raporty\testy_krawedz\PODSUMOWANIE_fala2.md` (poza gitem) |
| NS | `Ramki/notatki_dokumentacja_skanera.md` |
| BR | `Ramki/`, dokument "Budowa ramki - decyzje i zamienniki" (`.md`) |
| PR | `Ramki/plan_ramki_v2.md` |
| H | historia git, commit `dff1e78` (`main` przed zastapieniem zawartosci 03.11.2026): wczesniejsza linia programu `qc/` |
| KO | stan podany przez koordynatora w zleceniu tego planu (nie sprawdzany przeze mnie) |

**[BRAK W ZRODLACH - do decyzji]** = zrodla tego nie rozstrzygaja (lista zbiorcza w sekcji 12).
**[PROPOZYCJA]** = projekt autora planu, nie wymaganie ze zrodel.

## 1. Cel i granice etapu 3 (10 zdan)

1. Etap 3 konczy sie aplikacja, w ktorej technik nie wybiera plikow i nie wpisuje polecen: uruchamia skrot
   "Stanowisko" i pracuje spacja, mysza oraz klawiatura ramki porannej.
2. Wieczorem technik uklada prace w gniazdach plytki, wsuwa plytke do skanera i naciska spacje; po 60-90 s widzi mape
   plytki (zielone, czerwone, zolte "popraw ulozenie", szare "bez projektu"), czerwone prace bierze do reki, klika
   gniazdo, oglada miejsce ubytku z rozmiarem i jednym przyciskiem wybiera "Ukruszona" albo "OK" (PW "Przeplyw
   wieczorny krok po kroku", kroki 1-6).
3. Program w tle sam zauwaza nowy plik w folderze skanera, rozpoznaje plytke, bierze pule projektow dnia ze
   wspolczynnikiem skurczu kazdej pracy, zapisuje skan, wynik i decyzje w lokalnej bazie i prowadzi liste
   "do dofrezowania".
4. Rano osoba rozkladajaca piec przeklada prace do plytek porannych, skanuje wszystkie plytki pieca, na ekranie widzi
   kuwete kazdej pracy i rozstrzyga dwuznaczne kliknieciem, a w pokoju rozkladania kladzie plytke na ramce porannej
   i idzie kuweta po kuwecie (Enter, Backspace albo wpisany numer), po czym zamyka piec (PW "Przeplyw poranny krok
   po kroku", kroki 1-8).
5. Po "Zamknij piec" program wskazuje zlecenia kompletne do odhaczenia w Excelu (kolor pola B, z logiem kazdego
   zapisu) i prowadzi liste brakow miedzy piecami i dniami.
6. Ramka wieczorna pokazuje po skanie te same kolory pod plytka, ramka poranna - gniazda biezacej kuwety; bez ramek
   aplikacja dziala wedlug podpisow na ekranie laptopa (PW "Ryzyka i plany B").
7. Zakres etapu: `session`, `ui` (ekran wieczorny i poranny), `scanner`, `indicate`, `excel`, katalog z pula
   i wspolczynnikami (raport MillBox, plik CSV, wpis reczny), program ramki na Raspberry Pi, raport metryk
   odbiorczych, instalacja na laptopie stanowiska i instrukcje jednostronicowe.
8. Etap konczy sie gotowoscia do trybu cienia (PW "Uruchomienie: kolejnosc krokow", kroki 1-5); pomiar metryk
   odbiorczych na produkcji i przejscie na tryb pelny to etap 4 (do potwierdzenia: DW12).
9. Poza etapem: wybor metody i progow wykrywania ukruszen krawedzi od 0,08 mm (tylko paczka B4 "po danych ze skanera"
   z warunkami wejscia), prace w toku u innych wykonawcow (P1-P4, rozpoznawanie ukladu plytki, okno "Dzien skanera" -
   tu sa tylko zaleznosciami), mechanika ramek, plytka okragla na ramce (R58), dwa mosty w rynience, plan B poranka
   z kamera, automat klikajacy w programie skanera ponad "aktywuj okno i nacisnij Spacje", Office Script i Microsoft
   Graph.
10. Bez zgody wlasciciela nie zmieniamy stosu, modelu danych (baza - bramka G0), dystrybucji (bramka G3) ani sposobu
    zapisu do Excela (wylacznie kolor pola B).

## 2. Fakty sprawdzone 15.11.2026 (stan wyjsciowy)

| Nr | Fakt | Zrodlo | Skutek dla planu |
|---|---|---|---|
| 1 | Gotowe: `uklad`, `synth`, `ustawienia`, `plate` (ze straznikiem ukladu), `match` v1, `inspect` v1, `porownaj` (CLI: caly lancuch na jednym STL), `katalog` (czesc: cechy STL bez nazw), okno testowe `ui_test.py`. Testy: 252 passed / 3 skipped / 0 failed | OM README; R59 pkt 2 i 11 | etap 3 buduje na tym lancuchu i go nie zmienia (wyjatek: pula w A5) |
| 2 | Okno testowe: silnik w `QThread` zawisa na `match.Pula` (Open3D pod Qt: 195 s bez wyniku, w watku glownym 3-4 s); 2 testy okna maja `skip` | P3a pkt 5.1; R59 pkt 9.6 | analiza musi isc w osobnym procesie (A2); czy naprawia to paczka "Dzien skanera" - niezweryfikowane |
| 3 | `match.Pula(foldery, wspolczynnik)`: jeden wspolczynnik na cala pule, klucz projektu = SHA-16 pliku, budowa przy kazdym uruchomieniu (17 projektow ok. 3,5 s), brak puli "po dacie" i pamieci podrecznej | OM match "Zalozenia i granice"; kod `match.py` (`Projekt`, `Pula`) | wspolczynnik per praca i dwie wersje tego samego STL wymagaja zmiany `Pula` (A5) |
| 4 | Czas na plytke 11-12 s (plate 2, match 8-9, inspect 0,9) przy puli 17-30 projektow; skan 45-55 MB | P3a pkt 1; R59 pkt 6.1; OM ui | cel: analiza 20-40 s (PW "Przeplyw wieczorny"); przy puli kilkuset projektow czas trzeba zmierzyc (A5) |
| 5 | Klucze przyszlych modulow juz sa w ustawieniach i sa WYMAGANE przez walidator: `[sciezki]` 6, `[match] pula_*` 3, `[excel]` 5, `[ramki]` 3; nieznana sekcja albo klucz = blad | UT | nowe klucze tylko jako opcjonalne z wartoscia domyslna (lekcja R59 pkt 9.1: cztery wiersze `*_r54`) |
| 6 | Decyzje technika trafiaja dzis do `dane/decyzje.csv`; "session (SQLite) przejmie to pozniej" | OM ui | A1 importuje ten plik |
| 7 | Skaner (DentalScan 3.0.4): Spacja startuje skan, folder zapisu "Order Save Path", regula nazw plikow do ustawienia, brak API i SDK, kazdy skan wymaga zlecenia, klucz sprzetowy | NS | `scanner` = obserwacja folderu i opcjonalnie "aktywuj okno + Spacja"; szczegoly eksportu dopiero ze skanera (B2) |
| 8 | Ramka: lacznosc "HTTP/WebSocket" w sieci lokalnej, port 8765, hosty `ramka-w.local` i `ramka-p.local`; czujniki Halla na GPIO 19, 25, 8 (numer n = A + 2B + 4C, 0 = brak plytki); klawiatura tylko w ramce porannej (Enter, Backspace, cyfry, klawisz "Zamknij piec"); pole `leds` w `uklad.json` puste (ma je wypelnic kalibracja) | PW "Oprogramowanie" (tabela technologii); UT `[ramki]`; PR 8.1, 8.2, D11, 9 kroki 4, 11, 13; BR "Czujniki Halla i magnesy", "Klawiatura numeryczna" | format komunikatow trzeba zaprojektowac (3.6) |
| 9 | Pliki `modele_plytek/*/uklad.json` sa przypiete sumami SHA w testach (`test_pliki_modeli_bajtowo_bez_zmian`) | R59 pkt 3 | wyniku kalibracji diod nie da sie dopisac do tych plikow bez zmiany testow (DW9) |
| 10 | W repo i na MSI nie ma przykladowego raportu MillBox ani kopii firmowego Excela (`dane/millbox` i `dane/excel` w glownym katalogu: 0 plikow) | sprawdzone 15.11 | parser MillBox i COM Excela sa w kategorii D |
| 11 | W historii git jest wczesniejsza linia programu `qc/`: `qc/catalog` (`baza.py` - SQLite z tabelami `projekty` i `wspolczynniki`; `nazwy.py` - folder -> kuweta, normalizacja nazw; `indeks.py` - pule rano i wieczor; `wspolczynniki.py` - plik CSV `plik;krazek;wspolczynnik;data` jako plan B do czasu parsera MillBox), `qc/metryki` (raport jednym poleceniem), opisy `session`, `scanner`, `excel`, `indicate`, `ui` z dopiskiem "Nie zaimplementowano (etap 3)". W biezacym drzewie tego kodu nie ma | H | A4 i A10 zaczynaja od oceny przeniesienia tych plikow, nie od zera |
| 12 | Wykrywanie ukruszen krawedzi: praca na danych sztucznych zakonczona; wybor metody (C2 albo G13), progi i wymaganie 0,08 mm czekaja na prawdziwe skany | WD pkt 1 i 4 | tylko paczka B4 z warunkami wejscia |
| 13 | W toku u innych wykonawcow: P1 (filtr wysokosci w `match`), P2 (pas brzegu od linii brzegu filaru, status "nie sprawdzono"), P3 (korekta skali ze skanu), P4 (generator ukruszen krawedzi), automatyczne rozpoznawanie ukladu plytki, okno "Dzien skanera" | KO; WD pkt 4 | zaleznosci w sekcji 5; list plikow tych paczek nie dalo sie sprawdzic (sekcja 12) |
| 14 | R59 nie jest scalone: `origin/main` = `4cc6090`, stan R59 jest na `origin/bp/r59` | `git branch -r` 15.11 | paczki etapu 3 startuja od `main` po scaleniu R59 |
| [usunieto w kopii: opis dostepu ssh]

## 3. Architektura docelowa

### 3.1 Moduly i kto z kim rozmawia

| Modul | Pliki w `Ramki/stanowisko/stanowisko/` [PROPOZYCJA nazw] | Rola | Rozmawia z | Stan |
|---|---|---|---|---|
| scanner | `scanner.py` | obserwuje folder eksportu, sprawdza kompletnosc pliku, zglasza "nowy skan"; akcja "start skanu" (okno skanera + Spacja) | -> silnik; <- ui (Spacja) | nowy |
| silnik | `silnik.py` | osobny proces: kolejka analiz, pula w pamieci, wywolanie `porownaj.porownaj` | <- scanner; -> porownaj, pula; -> session | nowy |
| porownaj, plate, match, inspect, uklad | istniejace | analiza jednego skanu: wyrownanie, numer, ciecie, identyfikacja, ubytki | wolane tylko przez silnik | gotowe; P1-P4 i rozpoznawanie ukladu w toku (KO) |
| katalog i pula | `katalog.py` (jest), `indeks.py`, `nazwy.py`, `pula.py`, `wspolczynniki.py`, `millbox.py` | indeks folderow "Cyrkon" i "Prywatne", nazwa folderu -> kuweta, wspolczynniki (raport, CSV, wpis reczny), pula wieczorna i poranna | <- foldery, raporty; -> baza; -> silnik (lista wpisow puli) | czesc |
| baza | `baza.py` | plik SQLite: schemat, migracje, kopia | <- wszystkie moduly | nowy |
| session | `session.py` | stan wieczoru i poranka, decyzje, sesja pieca, punkty zlecen, braki, "do dofrezowania" | <- silnik, ui, indicate; -> baza, ui, indicate, excel | nowy |
| ui i aplikacja | `ui/` (pakiet), `aplikacja.py` | ekran wieczorny i poranny; spiecie modulow w jeden program | <- session; -> session (decyzje), scanner (Spacja) | jest okno testowe |
| indicate | `indicate.py`, `ramka_protokol.py` | plan plytki i stan do ramek, zdarzenia z ramek | <- session; <-> ramka W i P | nowy |
| program ramki | `Ramki/stanowisko/ramka/` | Raspberry Pi: matryca, czujniki Halla, klawiatura, serwer w sieci lokalnej | <-> indicate | nowy |
| excel | `excel.py`, `excel_com.py` | reguly wyboru wiersza, kolor pola B, log | <- session (zlecenia kompletne); -> Excel przez COM | nowy |
| metryki | `narzedzia/raport_metryk.py` | raport jednej strony z bazy | <- baza | nowy |

### 3.2 Przeplyw danych

```
folder eksportu skanera --nowy plik STL--> scanner --ZdarzenieSkanu--> silnik (osobny proces)
                                                                         | porownaj: plate -> match -> inspect
foldery Cyrkon / Prywatne --> indeks --> baza <-- wspolczynniki          | (pula: projekt x wspolczynnik)
raporty MillBox / CSV / wpis reczny --------^        |                   v
                                                     +--> pula ----> wynik (slownik = <skan>_wynik.json)
                                                                         |
                                                                         v
                                              session --> baza (skany, prace, decyzje, punkty zlecen)
                                                 |
        +----------------------------------------+-------------------------------+
        v                                        v                               v
 ui: ekran wieczorny / poranny            indicate --> ramka W / ramka P        excel (po "Zamknij piec")
 (decyzje technika --> session)           (plan plytki, stan; z ramki:          (zlecenia kompletne --> kolor pola B
                                           numer plytki, potwierdzenia)          --> log)
```

Wieczor: skan -> mapa plytki -> decyzje -> lista "do dofrezowania". Rano: skany plytek jednego pieca -> podpisy
i rozstrzygniecia -> plan plytek do ramki porannej -> potwierdzenia kuwet -> "Zamknij piec" -> Excel i lista brakow.

### 3.3 Wymagania ze zrodel (kazde ze zrodlem; czego nie ma - oznaczone)

| Id | Wymaganie | Zrodlo |
|---|---|---|
| S1 | Reakcja na nowy STL w folderze eksportu; analiza startuje w ciagu 1 s od zapisu; plik niepelny ignorowany | PW "Przeplyw wieczorny" (co robi program w tle); OM README (scanner) |
| S2 | Walidacja pliku: rozmiar, liczba trojkatow | PW "Oprogramowanie: moduly" (scanner) |
| S3 | Folder = "Order Save Path" programu skanera, klucz `folder_eksportu_skanera` | NS "Co potwierdza plan"; UT `[sciezki]` |
| S4 | Start skanu: Spacja; automat opcjonalny = aktywuj okno DentalScan i nacisnij Spacje | PW "Co wybralismy i dlaczego" (start skanu); NS (start skanu); PW "Ryzyka" (automat opcjonalny) |
| S5 | Struktura folderu zlecenia, nazwa i format pliku, czy eksport robi sie sam, czy jedno zlecenie obsluzy wiele skanow, plaszczyzna ciecia | NS "Co dokumentacja NIE rozstrzyga" - **[BRAK W ZRODLACH - rozstrzygnie pierwszy dzien skanera]** |
| S6 | Ktore okno ma fokus przy Spacji i skad nasza aplikacja wie o starcie skanu | **[BRAK W ZRODLACH - do decyzji]** (DW5) |
| SE1 | Zapis: plik skanu, gniazdo, dopasowany projekt, wynik, decyzja technika, czas | PW "Przeplyw wieczorny" (co robi program w tle) |
| SE2 | "Ukruszona": pozycja na liscie "do dofrezowania" (zlecenie, zab, krazek) i brak w zleceniu; "OK" = falszywy alarm | PW "Przeplyw wieczorny" krok 5; "Przeplyw poranny" (pamiec miedzy piecami) |
| SE3 | Sesja pieca: lista plytek jednego pieca, zliczanie punktow kazdego zlecenia; koniec = "Zamknij piec" | PW "Przeplyw poranny" krok 8 i "co robi program w tle" |
| SE4 | Stan zlecen i lista brakow trwale miedzy piecami i dniami; zab dofrezowany rozpoznany po tym samym STL domyka zlecenie | tamze |
| SE5 | Poprawka pojedynczego zeba do zlecenia juz odhaczonego: dopisek, bez czekania na komplet, Excel bez zmian, wpis w logu | PW "Przeplyw wieczorny" (sytuacje szczegolne); "Przeplyw poranny" krok 8 |
| SE6 | Praca bez projektu: szare "sprawdz recznie", proba puli z poprzedniego dnia | PW "Przeplyw wieczorny" (sytuacje szczegolne) |
| SE7 | Dwie prace w gniezdzie albo praca poza gniazdem: zolte "popraw ulozenie", skan do powtorzenia; podwojna powierzchnia: ponowny skan plytki | tamze |
| SE8 | Ten sam projekt w dwoch gniazdach = konflikt do rozstrzygniecia w sesji | OM match "Zalozenia i granice" (ostatni punkt) |
| SE9 | Tryb cienia: technik zaznacza takze prace, ktore sam uznal za ukruszone, a program nie | PW "Uruchomienie" (w trybie cienia) |
| SE10 | Kryterium "dziala": scenariusz 3 piecow + 1 dofrezowany zab daje wlasciwe listy | OM README (session) |
| SE11 | Nie zapisujemy, ktora praca byla w ktorym piecu | PW "Przeplyw wieczorny" krok 6; "Ryzyka" (czego nie da sie obejsc) |
| SE12 | "Kto zatwierdzil" w logu - skad program zna osobe | PW "Dane i integracje" regula 6 - **[BRAK W ZRODLACH - do decyzji]** (DW3) |
| SE13 | Ponowny skan tej samej plytki: kiedy zastepuje poprzedni, co z decyzjami | **[BRAK W ZRODLACH - do decyzji]** (zalozenie Z4) |
| SE14 | Lista "do dofrezowania" po ostatniej plytce "wydrukowana lub wyslana" - forma i adresat | PW zal. D - **[BRAK W ZRODLACH - do decyzji]** (zalozenie Z6) |
| SE15 | Numer plytki ze skanu (dolki kodu); gdy nieczytelny - wskazanie reczne na ekranie. Na plytce kwadratowej dolki leza poza polem fi 100 | PW zal. A i F; RD "Porownanie skanu z projektami" - jak wiazac skan z plytka na ramce bez numeru: **[BRAK W ZRODLACH - do decyzji]** (zalozenie Z3) |
| U1 | Ekran wieczorny: mapa plytki, czerwone gniazda, klik -> widok 3D z mapa odchylek i powiekszeniem ubytku z rozmiarem; "Ukruszona" / "OK" | PW "Przeplyw wieczorny" kroki 3-5; "Oprogramowanie: moduly" (ui) |
| U2 | Ekran poranny: kazda plytka z podpisami (numer kuwety, nazwisko, numer zeba, miniatura projektu); pewne zielone, dwuznaczne zolte, poprawki bursztynowe, nieznane biale; dwuznaczne rozstrzygane kliknieciem z podgladem obu kandydatow | PW "Przeplyw poranny" krok 3 |
| U3 | Duze kafelki; technik rozumie bez instrukcji (przeglad z technikiem na danych sztucznych) | PW "Co przygotowuje, czekajac na dostawe" (ui); OM ui |
| U4 | Ustawienia progow na ekranie | PW "Oprogramowanie: moduly" (ui) - zakres w etapie 3: zalozenie Z7 |
| U5 | Liczba STL w puli dnia na ekranie, "Odswiez pule", "Test LED", reczny numer plytki, tryb "Poranek" | PW zal. D, E, F |
| U6 | "Zamknij piec" jako przycisk na laptopie i klawisz ramki | PW "Przeplyw poranny" krok 8 |
| U7 | Kolejnosc kuwet: od najliczniejszej, wedlug numeru albo numer wpisany recznie | PW "Przeplyw poranny" krok 6 |
| U8 | Podglad 3D: dzis osobny proces Open3D, w oknie tylko obraz 2D; widok wbudowany w Qt "na pozniej" | OM ui "Podglad 3D - decyzja" (DW7) |
| U9 | Skrot "Stanowisko" na pulpicie; komunikaty z tabeli "co robic, gdy nie dziala" | PW zal. F |
| K1 | Indeks folderow "Cyrkon" (OneDrive, zawsze na urzadzeniu) i "Prywatne/#numer" | PW "Dane i integracje" |
| K2 | Nazwa folderu -> numer kuwety (ciag 1-4 cyfr, zera wiodace); cala nazwa do porownania z kolumna H | tamze |
| K3 | Pula poranna: foldery zmienione w ostatnich 3-4 dniach roboczych (piatek obejmuje weekend), takze zlecenia juz odhaczone, plus "Prywatne"; kazdy STL = punkt pracy; numer zeba z nazwy pliku; skala 1:1 | tamze; PW "Przeplyw poranny"; UT `pula_rano_dni_roboczych` |
| K4 | Pula wieczorna: STL z raportow MillBox z dzis i wczoraj, kazdy w skali swojego raportu; zab dofrezowany na innym krazku = dwie wersje | PW "Dane i integracje" (raporty MillBox); UT `pula_wieczor_dni` |
| K5 | Co noc cechy nowych STL (objetosc, wymiary, deskryptor, miniatura); z puli znikaja zlecenia starsze niz 10 dni | tamze; UT `usun_z_puli_po_dniach` |
| K6 | Raport MillBox: nazwy STL w zadaniu, identyfikator krazka, wspolczynnik skurczu, data; HTML albo PDF; folder sieciowy albo kopia raz dziennie | tamze; PW zalozenie 4 - uklad pol raportu: **[BRAK W ZRODLACH - potrzebne prawdziwe raporty]** |
| K7 | Plan B: wspolczynnik wpisywany recznie raz na krazek (lista krazkow dnia) | PW "Ryzyka" (brak dostepu do raportow MillBox) |
| K8 | Korekta skali ze skanu w oknie +-1 %, ostrzezenie powyzej 0,3 %, rano bez korekty (decyzja wlasciciela; P3 w toku) | WD pkt 2; F2 pkt 2 (wniosek 4) |
| K9 | Pula raz dziennie = projekt x wspolczynnik MillBox + linie krawedzi kazdego filaru (+ szablony detektora po danych ze skanera) | F2 pkt 3 |
| K10 | Nazwiska nie wychodza poza laptop; w repo, raportach i logach tylko skrot SHA-16 projektu | RD "Porownanie skanu z projektami"; PW "Dane i integracje" (RODO) |
| K11 | Ile prac i zlecen dziennie (rozmiar puli) | sa tylko liczby posrednie: 7-10 plytek wieczorem po do 19 prac, piec 40-60 prac, 4-6 piecow rano (PW) - **[BRAK W ZRODLACH - do pomiaru na prawdziwym folderze]** |
| K12 | Zlecenia prywatne w Excelu: wiersz po numerze zlecenia w kolumnie B albo H | PW "Dane i integracje" - w zrodle oznaczone jako zalozenie do potwierdzenia |
| I1 | Ramka poranna dostaje plan plytki (gniazdo -> kuweta), odsyla potwierdzenia i wpisane numery; bez sieci trzyma ostatni plan i dosyla potwierdzenia pozniej | PW "Przeplyw poranny" (ramki i plytki) |
| I2 | Kolory: czerwien = sprawdz, zielen = biezaca kuweta, bursztyn = poprawka, biel = praca nieznana; stan ramki = kolor marginesu matrycy | PW "Architektura rozwiazania" pkt 7 |
| I3 | Na marginesie numer biezacej kuwety i liczba prac ("3263 - 4"); informacja, ze prace kuwety leza tez na innej plytce; nieznane na bialo i numery zlecen z brakami | PW "Przeplyw poranny" kroki 5-7 |
| I4 | Klawiatura: Enter potwierdza i przelacza, Backspace cofa, cyfry wybieraja kuwete, osobny klawisz zamyka piec | tamze kroki 5 i 8; BR "Klawiatura numeryczna" |
| I5 | Plytka rozpoznawana po magnesach: 1-6, 0 bez plytki, w 100 % przypadkow w mniej niz 100 ms; po zmianie plytki ramka sama przelacza plan | PW "Testy odbiorcze" (ramki); PR 9 krok 11; PW "Przeplyw poranny" krok 7 |
| I6 | Ramka wieczorna: Spacja na laptopie zmienia jej stan w mniej niz 1 s; po skanie pokazuje czerwone i zielone | PR 9 krok 4; PW "Ramki swietlne" (co to jest i jak dziala) |
| I7 | W sieci tylko numery gniazd i kuwet | PW "Dane i integracje" (RODO) |
| I8 | Port 8765, hosty `ramka-w.local`, `ramka-p.local` | UT `[ramki]` |
| I9 | Transport i pola komunikatow | PW podaje tylko "HTTP/WebSocket" oraz "plytka, gniazdo, kolor", "stan", potwierdzenia - **[BRAK W ZRODLACH - do decyzji]** (DW8, propozycja 3.6) |
| I10 | Gniazdo -> diody z kalibracji (blok 3 x 3 piksele pod gniazdem), wynik w pliku obok plytki, osobno wieczorna i poranna | PR 9 krok 13; PW "Montaz i testy" krok 13 |
| I11 | Skad ramka bierze uklad gniazd dla starych plytek (numery te same w obu ukladach) | PW "Decyzje otwarte" nr 10 - **[BRAK W ZRODLACH - do decyzji]** (DW9) |
| I12 | Kolor gotowosci, ikona Wi-Fi, "Test LED"; uklad napisow na marginesie | PW zal. E, F - szczegoly wygladu: **[BRAK W ZRODLACH - do decyzji]** |
| I13 | Ramka wstaje sama w mniej niz 60 s; karta tylko do odczytu; zapas: hotspot laptopa | PR 9 krok 14; PW zal. B |
| X1 | COM do Excela otwartego z Autozapisem; program nie otwiera pliku drugi raz i nie zapisuje kopii | PW "Dane i integracje" (Excel produkcyjny) |
| X2 | Odczyt kolumn A-I biezacego arkusza co kilka minut; zapis tylko: kolumna B, wypelnienie RGB 198, 239, 206 | tamze; UT `[excel]` |
| X3 | Reguly 1-5 wyboru wiersza; wiecej niz jeden kandydat albo zaden = "Excel: wskaz wiersz" | tamze (reguly znalezienia wiersza) |
| X4 | Zapis tylko po "Zamknij piec" i tylko dla zlecen kompletnych; pole juz zielone = brak zapisu, wpis w logu | PW "Przeplyw poranny" (Excel) |
| X5 | Tryb "pytaj przed zapisem" | PW "Oprogramowanie: moduly" (excel); UT `tryb_pytaj_przed_zapisem` |
| X6 | Log CSV: data, godzina, kuweta, nazwa folderu, numer zlecenia z kolumny B, arkusz, wiersz, kto zatwierdzil | regula 6; UT `log_excel` |
| X7 | Kryterium: 50 kuwet z historii na kopii pliku, 50 z 50 zgodnych z czlowiekiem | OM README (excel); PW "Co przygotowuje" |
| X8 | Nazwa pliku i arkusza, znaczenie kolumn D-G oraz I, zachowanie COM przy pliku z SharePointa | **[BRAK W ZRODLACH - potrzebna kopia pliku i laptop z Excelem]** |
| M1 | Kazda metryke program liczy sam z wlasnego logu; raport = jedno polecenie i jedna strona | PW "Testy odbiorcze i kryteria" |
| M2 | Tabela testow wykrywalnosci (5 prac tygodniowo ze znanymi ubytkami) | tamze (jak liczyc wykrywalnosc uczciwie) |
| DY1 | Na laptopie wersja zamrozona, aktualizacja jednym poleceniem; kod w prywatnym repozytorium | PW "Oprogramowanie: moduly" (ostatni akapit) |
| DY2 | Dzis: kopia folderu + `pip install -r requirements.txt` (wersje przypiete); wariant bez internetu przez `pip download` | RD "Laptop firmowy" pkt 2 |

### 3.4 Model danych sesji - PROPOZYCJA DO AKCEPTACJI WLASCICIELA (bramka G0, DW1 i DW2)

To jest zmiana modelu danych. Plik: `dane/stanowisko.sqlite` (klucz `[sciezki] baza`, UT), poza repo i poza OneDrive.
Wersja schematu: `PRAGMA user_version = 1`; migracje tylko w przod; przed migracja kopia pliku bazy.
Poprzednik: schemat z H (`projekty`, `wspolczynniki`) - w komentarzu kodu opisany jako zatwierdzony przez
wlasciciela; zapisu tej decyzji nie znalazlem (sekcja 12).

| Tabela | Kolumny (PK = klucz glowny, FK = klucz obcy) | Wymaganie |
|---|---|---|
| `zlecenia` | `id` PK; `zrodlo` (cyrkon / prywatne); `folder` (nazwa folderu doslownie - DANE OSOBOWE); `folder_norm`; `kuweta` (tekst: 3263 albo #1234); `mtime`; `dodano`; `usuniety`. Unikat (`zrodlo`, `folder`); indeks `kuweta` | K1, K2 |
| `projekty` | punkt pracy = plik STL w folderze zlecenia: `id` PK; `zlecenie_id` FK; `plik` (nazwa pliku); `sha16` (16 znakow SHA-256 zawartosci - identyfikator uzywany juz przez `match`, generator i `decyzje.csv`); `zeby`; `typ`; `mtime_ns`; `rozmiar`; `zaindeksowano`; `usuniety`. Unikat (`zlecenie_id`, `plik`); indeks `sha16` | K3; OM katalog |
| `cechy_stl` | `sha16` PK; `trojkaty`; `szczelny`; `objetosc_mm3`; `hull_mm3`; `pole_mm2`; `obrys_a_mm`; `obrys_b_mm`; `wysokosc_mm`; `miniatura` (PNG); `wersja_cech`; `policzono` | K5; pola jak `katalog.Projekt` |
| `frezowania` | wiersz raportu MillBox, pliku CSV albo wpis reczny: `id` PK; `projekt_id` FK albo NULL (STL z raportu nieznaleziony w indeksie); `plik_w_raporcie`; `krazek`; `wspolczynnik`; `data`; `zrodlo` (millbox_html / millbox_pdf / csv / reczny); `raport_plik`; `wczytano`. Unikat (`plik_w_raporcie`, `krazek`, `data`) | K4, K6, K7 |
| `skany` | `id` PK; `plik`; `sha16`; `rozmiar`; `czas_pliku`; `czas_analizy`; `czas_s`; `tryb` (wieczor / rano); `uklad`; `uklad_zrodlo` (auto / reczny); `uklad_zgodny`; `numer_plytki`; `numer_zrodlo` (dolki / podany / ramka / nieznany); `sesja_pieca_id` FK albo NULL; `status` (przyjety / do_powtorzenia / zastapiony / niezgodny_uklad / blad); `zastepuje_id` FK; `wynik_json` (sciezka pliku wyniku); `wersja_programu`; `skrot_ustawien` | SE1, SE7, SE13, SE15 |
| `prace` | jedno gniazdo jednego skanu: `id` PK; `skan_id` FK; `gniazdo`; `nr_fragmentu`; `status_fragmentu`; `status_match`; `status_inspekcji`; `status_gniazda`; `kandydat1_sha16`; `kandydat1_pokrycie`; `kandydat2_sha16`; `kandydat2_pokrycie`; `pewnosc`; `frezowanie_id` FK albo NULL; `wspolczynnik`; `korekta_skali`; `ubytki` (liczba); `ubytek_max_mm`; `projekt_id` FK albo NULL (przypisanie obowiazujace: automatyczne albo z decyzji). Unikat (`skan_id`, `gniazdo`, `nr_fragmentu`) | SE1; format wyniku `porownaj` |
| `decyzje` | tylko dopisywanie: `id` PK; `praca_id` FK albo NULL; `skan_id` FK albo NULL; `rodzaj` (ukruszona / ok / wybor_kandydata / przypisanie_reczne / ukruszona_niewykryta / numer_plytki / uklad / powtorz_skan / cofniecie / cofnij_zastapienie); `wartosc`; `operator`; `czas` | SE2, SE9, SE12 |
| `sesje_pieca` | `id` PK; `data`; `nr_w_dniu`; `otwarto`; `zamknieto`; `zamknal`. Bez identyfikatora pieca (SE11) | SE3 |
| `stan_punktow` | `projekt_id` PK i FK; `stan` (oczekuje / rozpoznany / do_dofrezowania / brak_po_piecu / zamkniety_recznie); `praca_id` FK albo NULL; `sesja_pieca_id` FK albo NULL; `czas` | SE2-SE5 |
| `excel_zapisy` | `id` PK; `czas`; `sesja_pieca_id` FK; `zlecenie_id` FK; `kuweta`; `folder` (DANE OSOBOWE - wymaga tego format logu); `numer_zlecenia_b`; `arkusz`; `wiersz`; `regula` (1-5); `wynik` (zapisano / juz_odhaczone / wskazano_recznie / pominieto / tylko_log / blad); `tryb` (pytaj / auto / cien); `operator`. Kazdy wiersz idzie tez do `log_excel.csv` | X3-X6 |
| `zdarzenia` | dziennik, tylko dopisywanie: `id` PK; `czas`; `zrodlo` (scanner / silnik / ui / ramka_w / ramka_p / excel / pula / system); `typ`; `skan_id` albo NULL; `dane` (JSON bez nazwisk) | M1 (czasy, awarie), I1 (potwierdzenia) |

Zasady: (1) nazwy folderow i plikow zlecen wystepuja tylko w `zlecenia`, `projekty`, `frezowania` i `excel_zapisy` (decyzja 17.11.2026 po recenzji PR #16 - rozszerzenie DW2); wszystkie inne tabele, pliki wynikow,
raporty i komunikaty do ramek uzywaja `sha16`, numeru kuwety i numerow wierszy; (2) statusy sa tekstem bez listy
zamknietej w schemacie (P2 doda "nie sprawdzono", paczka B4 moze dodac kolejne); (3) szczegoly ubytkow (polozenie,
srednica, metoda) zostaja w pliku wyniku JSON skanu, w bazie sa liczba i najwiekszy rozmiar; (4) lista brakow, lista
"do dofrezowania" i komplet zlecenia to zapytania po `stan_punktow`, nie osobne tabele; (5) tabela
`testy_wykrywalnosci` (M2) dojdzie w A10 jako migracja do wersji 2 - z opisem dla wlasciciela.

### 3.5 Pula projektow ze wspolczynnikiem per praca [PROPOZYCJA zgodna z K3-K9]

| Temat | Rozwiazanie | Zrodlo wymagania |
|---|---|---|
| Wpis puli | (projekt `sha16`, wspolczynnik, krazek, `frezowanie_id`); ten sam STL w dwoch raportach = dwa wpisy; wynik dopasowania wskazuje wpis | K4 |
| Pula wieczorna | `frezowania` z dzis i wczoraj (`pula_wieczor_dni`) polaczone z indeksem; STL z raportu nieznaleziony w indeksie = licznik "brakujace" na ekranie | K4; PW zal. D |
| Zrodla wspolczynnika, w tej kolejnosci | raport MillBox (D1) -> plik CSV `plik;krazek;wspolczynnik;data` (H) -> wpis reczny na krazek (K7) -> awaryjnie jeden wspolczynnik na cala pule z folderu (tak dziala dzis `porownaj --wspolczynnik`) | K6, K7; H; RD |
| Korekta skali | po scaleniu P3 wspolczynnik z puli jest wartoscia startowa; zmierzona korekta trafia do `prace.korekta_skali`, ostrzezenie powyzej 0,3 % | K8 |
| Pula poranna | projekty z folderow zmienionych w ostatnich N dniach roboczych + "Prywatne", wspolczynnik 1,0, takze zlecenia odhaczone | K3 |
| "Raz dziennie" | odswiezenie przy starcie programu, przyciskiem "Odswiez pule" i po pojawieniu sie nowego pliku albo raportu; cechy i miniatury liczone przy indeksowaniu | K5, K9; zalozenie Z5 |
| Pamiec podreczna | filtr wstepny na cechach z `cechy_stl` (bez wczytywania siatek); ciezkie obiekty `match.Projekt` (siatka w skali, 40 tys. punktow, FPFH, scena promieni) budowane dopiero dla kandydatow po filtrze i trzymane w procesie silnika | fakt 3; PW "Przeplyw wieczorny" (filtr odrzuca 90 % kandydatow) |
| Miejsce na linie krawedzi i szablony | pliki pamieci podrecznej kluczowane (`sha16`, wspolczynnik, wersja) w `dane/pula_cache/`; wypelnia je P2, a pozniej B4 | K9 |
| Zmiana w `match.py` | `Pula` z listy wpisow zamiast (foldery, jeden wspolczynnik); klucz kandydata (`sha16`, wspolczynnik). Dotyka pliku zmienianego przez P1 i P3 - dopiero po ich scaleniu (A5) | fakt 3 i 13 |
| Skala | szacunek z liczb PW: wieczorem 130-190 prac, pula wieczorna 250-400 wpisow, poranna 500-800 projektow - do zmierzenia; kryterium A5: plytka przy puli 400 wpisow w czasie do 40 s | K11; fakt 4 |

### 3.6 Format komunikatow do ramki [PROPOZYCJA - zrodla podaja tylko I1-I13; decyzje DW8 i DW9]

Ramka = serwer HTTP na porcie `[ramki] port` (8765); laptop (`indicate`) jest klientem; tresc JSON; po obu stronach
tylko biblioteka standardowa Pythona (zero nowych zaleznosci).

| Kierunek | Wywolanie | Tresc | Wymaganie |
|---|---|---|---|
| laptop -> ramka | `GET /stan` | `{"protokol":1,"rola":"P","program":"0.1","start_id":"a1b2","plytka":4,"plan_id":"2026-11-16-p2","kuweta":"3263","nr_zdarzenia":57,"temp_c":48}` | I12, I13 |
| laptop -> ramka | `PUT /plan` | plan sesji (przyklad nizej): dla kazdego numeru plytki gniazda z blokiem pikseli, kolorem i kuweta; lista kuwet z liczba prac i numerami plytek; kolejnosc; braki | I1-I3, I7, I10, I11 |
| laptop -> ramka | `PUT /tryb` | `{"stan":"skanowanie"}`; stany: gotowa / skanowanie / analiza / wynik / blad / test_led | I6, I12 |
| laptop -> ramka | `DELETE /plan` | po "Zamknij piec" | SE3 |
| ramka -> laptop | odpowiedz na `GET /zdarzenia?od=57&czekaj=25` | zdarzenia o numerach wiekszych niz 57: `plytka` (numer 0-7), `potwierdzenie` (plan, plytka, kuweta), `cofniecie`, `kuweta_wybrana`, `zamknij_piec`, `start` | I1, I4, I5 |

```
{"protokol": 1, "plan_id": "2026-11-16-p2", "tryb": "rano", "kolejnosc": "liczba",
 "plytki": {"4": {"uklad": "poranna_r54", "gniazda": [
     {"id": 13, "px": [22, 30, 3, 3], "kolor": "zielony", "kuweta": "3263"},
     {"id": 14, "px": [26, 30, 3, 3], "kolor": "bialy", "kuweta": null}]}},
 "kuwety": [{"kuweta": "3263", "prac": 4, "plytki": [4, 5]}],
 "braki": ["3301"]}
```

Zasady: (1) `px` = [x, y, szerokosc, wysokosc] bloku na matrycy 64 x 64, policzone NA LAPTOPIE z ukladu plytki
rozpoznanego na skanie i z kalibracji - ramka nie zna ukladow, wiec nie musi odrozniac starej plytki od nowej (I11);
(2) zdarzenia ramki sa numerowane rosnaco od jej startu, `start_id` zmienia sie po restarcie; laptop pamieta ostatni
odebrany numer, wiec po przerwie w sieci dostaje zalegle potwierdzenia raz i w kolejnosci (I1); po restarcie ramki
wysyla plan ponownie; (3) ramka sama, bez laptopa, przelacza kuwety (Enter, Backspace, cyfry) i plany plytek po
zmianie numeru z czujnikow Halla; (4) plan i dziennik zdarzen sa w pamieci RAM (karta tylko do odczytu, I13);
(5) w sieci sa wylacznie numery gniazd, plytek i kuwet (I7); (6) plytka polozona na ramce bez planu = margines
"brak planu". Kalibracja: wynik w pliku lokalnym `dane/kalibracja_ramek.json` kluczowanym (ramka, uklad), a nie
w przypietych `uklad.json` (fakt 9; DW9).

### 3.7 Ustawienia

| Grupa | Klucze | Stan |
|---|---|---|
| Istniejace klucze "przyszlych modulow" - uzywamy bez zmian | `[sciezki] folder_eksportu_skanera, folder_cyrkon, folder_prywatne, folder_millbox, baza, log_excel`; `[match] pula_wieczor_dni, pula_rano_dni_roboczych, usun_z_puli_po_dniach`; `[excel]` 5 kluczy; `[ramki] port, wieczorna_host, poranna_host` | UT |
| Nowe, OPCJONALNE z wartoscia domyslna [PROPOZYCJA] | `[scanner] stabilizacja_ms, min_rozmiar_mb, min_trojkatow, wzorzec_pliku`; `[sesja] operatorzy, przechowuj_skany_dni`; `[ramki] odpytywanie_s`; `[sciezki] wyniki, kalibracja_ramek, pula_cache` | mechanizm kluczy opcjonalnych dodaje A1 |

Zasada: po etapie 3 stary lokalny `ustawienia.toml` ma dzialac bez recznych poprawek (R59 pkt 9.1 pokazal, ze reczne
dopisywanie wierszy jest pomijane).

### 3.8 Procesy i kontrakty miedzy modulami [PROPOZYCJA]

Procesy: (1) proces okna (Qt, `session`, `indicate`, `excel`); (2) proces silnika (`multiprocessing`, jedna analiza
naraz, Open3D nigdy w watku Qt - fakt 2; H README opisuje tez awarie przy rownoleglym BLAS i Open3D w watkach);
(3) podglad 3D jak dzis w osobnym procesie.

| Kontrakt | Postac |
|---|---|
| `ZdarzenieSkanu` | plik, `sha16`, rozmiar, liczba trojkatow, czas pliku |
| `ZadanieAnalizy` | skan, tryb (wieczor / rano), uklad (albo "rozpoznaj"), numer plytki (albo brak), opis puli |
| Wynik analizy | slownik zwracany dzis przez `porownaj.porownaj` (ten sam, co w `<skan>_wynik.json`: `uklad_zgodny`, `numer`, `numer_zrodlo`, `gniazda[]` z `status`, `pewnosc`, `kandydaci[]`, `inspekcja`, `status_gniazda`, `gniazda_puste`, `gniazda_podwojne`, `czas_s`) + `zadanie_id`, `skan_sha16` |
| `session` | `przyjmij_wynik(zdarzenie, wynik) -> skan_id`; `decyzja(praca_id, rodzaj, wartosc, operator)`; `stan_wieczoru(data)`; `do_dofrezowania(data)`; rano: `otworz_piec()`, `plan_plytek(sesja_pieca_id)`, `zamknij_piec()` -> zlecenia kompletne i braki |
| Slownik statusow i kolorow | jedna tabela w jednym pliku (status -> kolor ekranu, kolor ramki, napis) - ekrany i `indicate` nie maja wlasnych stalych (zalozenie Z8) |

## 4. Podzial na paczki

Paczka = jedna sesja koordynatora z wykonawcami (wzor: `Ramki/plan_sesji_R59_uklad_gniazd_2026-11-14.md`).
Wielkosc [PROPOZYCJA]: S = do pol sesji, jeden wykonawca; M = jedna sesja, 2-3 wykonawcow; L = dluga sesja albo
podzial na dwie. Sciezki plikow wzgledem `Ramki/stanowisko/`. Kazda paczka dodatkowo: `raporty/E3-<kod>_<data>.md`
oraz pliki koordynatora `Ramki/etap3/stan_<kod>.md` i `Ramki/etap3/odbior_<kod>/**`.

### 4.1 (A) Da sie zrobic teraz - bez skanera i bez ramek

**E3-A1 - baza i sesja wieczorna (M).** Cel: trwaly zapis skanow, prac i decyzji; stan wieczoru; lista "do dofrezowania".
- Wejscie -> wyjscie: wynik analizy (3.8), decyzje -> plik bazy i funkcje `session` dla wieczoru.
- Pliki: `stanowisko/baza.py`, `stanowisko/session.py`, `narzedzia/import_decyzji.py`, `testy/test_baza.py`,
  `testy/test_session_wieczor.py`, `testy/dane_sesji/**`, `opisy_modulow/baza.md`, `opisy_modulow/session.md`;
  zmieniane: `stanowisko/ustawienia.py`, `ustawienia.przyklad.toml`, `testy/test_ustawienia.py` (klucze opcjonalne).
- Kryteria (dane sztuczne - wyniki `porownaj` z plytek syntetycznych, bez nazwisk): (1) po przyjeciu 3 wynikow w bazie
  sa 3 skany, a liczba prac i ich statusy zgadzaja sie 1:1 z plikami wynikow; (2) "Ukruszona" na 2 pracach i "OK" na 1
  daje liste "do dofrezowania" z 2 pozycjami (kuweta, zab, krazek); cofniecie jednej = 1 pozycja, a w `decyzje` sa
  4 wiersze; (3) ponowny skan plytki: poprzedni ma status `zastapiony`, jego decyzje nie licza sie do list; (4) skan
  z `uklad_zgodny` = false albo "skan ponownie" ma status `niezgodny_uklad` albo `do_powtorzenia` i 0 prac zielonych;
  (5) zamkniecie i otwarcie bazy daje identyczny zrzut stanu; (6) ten sam `sha16` w dwoch gniazdach jednego wieczoru
  = zgloszony konflikt (SE8); (7) migracja 0 -> 1 z kopia pliku; baza nowsza niz program = odmowa z komunikatem;
  (8) test schematu: nazwa folderu tylko w `zlecenia` i `excel_zapisy`; (9) import `decyzje.csv`: liczba wierszy
  w `decyzje` = liczba wierszy pliku; (10) stary plik ustawien bez nowych kluczy wczytuje sie bez bledu; (11) pytest:
  0 failed, passed nie mniej niz punkt odniesienia + nowe testy; diff nie dotyka plikow spoza listy.
- Zalezy od: G0 (DW1-DW3), R59 w `main`. Ryzyka: P2 zmieni zestaw statusow (dlatego statusy jako tekst); spor o to,
  gdzie trzymac nazwiska (DW2).

**E3-A2 - scanner, silnik w osobnym procesie, symulator folderu skanera (M).** Cel: plik w folderze -> wynik analizy
bez udzialu czlowieka i bez zamrazania okna.
- Wejscie -> wyjscie: folder + pliki STL -> `ZdarzenieSkanu` -> wynik analizy (3.8).
- Pliki: `stanowisko/scanner.py`, `stanowisko/silnik.py`, `narzedzia/symulator_skanera.py`, `testy/test_scanner.py`,
  `testy/test_silnik.py`, `opisy_modulow/scanner.md`, `opisy_modulow/silnik.md`. Zadnych zmian w istniejacych plikach;
  parametry w konstruktorach z wartosciami domyslnymi (podpiecie do ustawien robi A3).
- Kryteria (symulator kopiuje sztuczne skany do folderu tymczasowego): (1) 100 zapisow w kawalkach trwajacych 1-5 s:
  100 zdarzen, 0 przed koncem zapisu, mediana opoznienia od konca zapisu ponizej 1 s (S1); (2) plik uciety, pusty,
  nie-STL albo z niezgodnym naglowkiem (binarny STL: rozmiar = 84 + 50 x liczba trojkatow) = 0 zdarzen i wpis
  z powodem (S2); (3) ten sam plik zapisany ponownie pod ta sama nazwa = nowe zdarzenie; ta sama zawartosc pod inna
  nazwa = zdarzenie z flaga "duplikat"; (4) 20 plikow naraz: analiza po kolei w kolejnosci zapisu, zadnego zgubionego;
  (5) wynik silnika dla sztucznego skanu kazdego z 4 typow plytek jest rowny wynikowi `porownaj` z wiersza polecen
  (pole po polu, poza czasami); (6) silnik wywolany z aplikacji Qt (tryb offscreen) konczy plytke w czasie do 60 s
  (dzis 195 s bez wyniku - fakt 2), a petla okna nie ma przerw dluzszych niz 200 ms; (7) awaria analizy (zly plik,
  zabity proces) = komunikat i podjecie nastepnego zadania; (8) pytest caly: 0 failed.
- Zalezy od: akceptacji planu (zadnej decyzji blokujacej). Ryzyka: paczka "Dzien skanera" mogla juz zrobic silnik
  w osobnym procesie (sprawdzic w etapie 0, nie pisac drugiego); prawdziwy skaner moze zapisywac inaczej niz
  symulator (kilka plikow, pliki tymczasowe) - B2.

**E3-A3 - aplikacja i ekran wieczorny (L).** Cel: jeden program "Stanowisko" w trybie "Wieczor".
- Wejscie -> wyjscie: A1 + A2 -> okno: mapa plytki, widok pracy, decyzje, lista "do dofrezowania", komunikaty.
- Pliki: `stanowisko/aplikacja.py`, `stanowisko/ui/**` (nowy pakiet), `stanowisko/statusy.py` (slownik statusow
  i kolorow), `uruchom_stanowisko.bat`, `testy/test_aplikacja.py`, `testy/test_ui_wieczor.py`,
  `opisy_modulow/aplikacja.md`; zmieniane: `opisy_modulow/README.md`, `README.md` (struktura, uruchomienie).
  `ui_test.py` tylko przez import (`MapaPlytki`), bez edycji.
- Kryteria: (1) test offscreen: symulator wrzuca skan -> mapa ma kolory rowne `status_gniazda` z wyniku w 100 % gniazd;
  (2) klik w czerwone gniazdo pokazuje obraz odchylek i rozmiar ubytku; "Ukruszona" / "OK" zapisuje decyzje w bazie
  i odswieza liste "do dofrezowania"; (3) Spacja wywoluje akcje "start skanu" (w tescie atrapa okna skanera odnotowuje
  jedno wywolanie); (4) plytka niezgodna z ukladem, "skan ponownie", "popraw ulozenie", brak numeru plytki = komunikat
  i przyciski z PW zal. F, nic zielonego; (5) zamkniecie programu w polowie wieczoru i ponowny start odtwarza plytki
  i decyzje dnia; (6) petla okna bez przerw dluzszych niz 200 ms podczas analizy 10 plytek; (7) liczba STL w puli
  i przycisk "Odswiez pule" na ekranie (U5); (8) przeglad z czlowiekiem na danych sztucznych (bramka G1): 5 zadan
  wieczornych z sekcji 7 (T14) bez podpowiedzi.
- Zalezy od: A1, A2; DW5, DW7. Ryzyka: kolizja z oknem "Dzien skanera" (wspolne elementy okna testowego); wyglad
  wymaga 1-2 rund z wlascicielem.

**E3-A4 - katalog: indeks folderow, nazwy, pule, wspolczynniki z CSV i reczne (M).** Cel: pula dnia i pula poranna
z prawdziwej struktury folderow, bez raportow MillBox.
- Wejscie -> wyjscie: drzewo `<zrodlo>/<folder zlecenia>/*.stl`, plik CSV, wpisy reczne -> tabele `zlecenia`,
  `projekty`, `cechy_stl`, `frezowania`; listy wpisow puli (3.5).
- Pliki: `stanowisko/nazwy.py`, `stanowisko/indeks.py`, `stanowisko/pula.py`, `stanowisko/wspolczynniki.py`,
  `narzedzia/drzewo_syntetyczne.py`, `testy/test_nazwy.py`, `testy/test_indeks.py`, `testy/test_pula.py`,
  `opisy_modulow/pula.md`. Bez zmian w `match.py` i `katalog.py` (tylko import). Punkt wyjscia: pliki z H
  (`nazwy.py`, `indeks.py`, `wspolczynniki.py`) - ocenic i przeniesc to, co pasuje.
- Kryteria (drzewo sztuczne: 40 zlecen o fikcyjnych nazwach we wzorach "nazwisko + numer 1-4 cyfry + kod literowy,
  takze sklejony z numerem", "inicjal z kropka przed numerem", zera wiodace, "#1234"; STL = atrapy i projekty testowe
  na PC): (1) kuweta poprawna w 40 z 40; (2) liczba nowych = liczba plikow STL; drugi przebieg: 0 nowych, cechy
  liczone tylko dla nowych i zmienionych; plik usuniety = `usuniety`; brak calego katalogu zrodla = zrodlo pominiete
  bez oznaczania usuniec; (3) pula poranna: tabela 10 dat (piatek obejmuje weekend) zgodna w 10 z 10; zlecenia
  starsze niz 10 dni poza pula; (4) pula wieczorna z CSV i wpisow recznych: STL z dzis i wczoraj; ten sam STL
  z dwoma wspolczynnikami = 2 wpisy; STL z CSV spoza indeksu = licznik "brakujace"; (5) bledny CSV = komunikat
  z numerem linii; (6) w logach i raportach testow 0 nazw folderow; (7) pytest caly: 0 failed.
- Zalezy od: A1 (`baza.py`), DW2, DW6. Ryzyka: wzory prawdziwych nazw folderow szersze niz probka (D3); regula
  "kazdy STL to punkt" moze nie pasowac do folderow z dodatkowymi plikami (sekcja 12).

**E3-A5 - pula per praca w `match` i pamiec podreczna (M).** Cel: dopasowanie na puli kilkuset wpisow z roznymi
wspolczynnikami w czasie z planu.
- Pliki: `stanowisko/match.py`, `stanowisko/porownaj.py` (tylko budowa puli), `testy/test_match.py`,
  `testy/test_pula_match.py`, `narzedzia/metryki_pula.py`, `opisy_modulow/match.md`.
- Kryteria: (1) plytka sztuczna z pracami z dwoch krazkow (1,20 i 1,25): top-1 w scenariuszu "dobrze" 100 %;
  (2) ten sam STL z dwoma wspolczynnikami w puli: wynik wskazuje wlasciwy wpis w 100 % prob; (3) pula 400 wpisow
  (projekty testowe w wariantach + atrapy): czas analizy plytki do 40 s na PC i szczyt pamieci procesu do 8 GB
  [progi - PROPOZYCJA]; (4) regresja na zestawach R59 (40 skanow): wyrownanie 40 z 40, top-1 "dobrze" 276 z 276,
  falszywe czerwone na pracach calych 0 (R59 pkt 6.2); (5) pytest caly: 0 failed.
- Zalezy od: A4; P1 i P3 scalone (ten sam plik). Ryzyka: czasy na laptopie stanowiska inne niz na PC (D4).

**E3-A6 - sesja poranna (M).** Cel: sesja pieca, punkty zlecen, braki, dofrezowania, poprawki.
- Pliki: `stanowisko/session_rano.py` (albo rozszerzenie `session.py` - wtedy ta paczka jest wlascicielem pliku),
  `testy/test_session_rano.py`, `testy/dane_sesji/rano/**`, `opisy_modulow/session.md`.
- Kryteria: scenariusz SE10 zapisany jako tabela oczekiwan i sprawdzony w 100 % wierszy: dzien 1 wieczor - w zleceniu
  X (3 punkty) jeden zab "Ukruszona"; dzien 2, piec 1 - 2 punkty X, komplet Y (2 z 2), 1 z 2 punktow Z -> kompletne:
  Y; braki: X (1 zab), Z (1 zab); piec 2 - drugi punkt Z -> kompletne: Z; dzien 3, piec 3 - dofrezowany zab X
  rozpoznany po tym samym STL -> kompletne: X; poprawka pojedynczego zeba zlecenia juz odhaczonego -> tylko log;
  do tego: dwuznaczna rozstrzygnieta decyzja, nieznana przypisana recznie, ten sam projekt na dwoch plytkach =
  konflikt, plytka zeskanowana ponownie, restart programu miedzy piecami (stan odtworzony).
- Zalezy od: A1, A4. Ryzyka: definicja punktu zlecenia (sekcja 12).

**E3-A7 - ekran poranny (L).** Cel: tryb "Poranek" na laptopie, bez ramek i bez Excela.
- Pliki: `stanowisko/ui/ekran_rano.py`, `stanowisko/ui/kandydaci.py`, `testy/test_ui_rano.py`,
  `opisy_modulow/aplikacja.md`; zmieniane (po A3): `stanowisko/aplikacja.py` i pozostale pliki `stanowisko/ui/**`.
- Kryteria: (1) offscreen: 3 plytki jednego pieca -> podpisy (kuweta, zab, miniatura) i kolory zgodne z wynikiem w 100 %
  gniazd (U2); (2) klik w zolte pokazuje dwoch kandydatow, wybor zapisuje decyzje i zmienia kolor; (3) trzy sposoby
  kolejnosci kuwet (U7); (4) "Zamknij piec" pokazuje zlecenia kompletne i liste brakow rowna wynikowi A6; (5) bez
  ramki i bez Excela program dziala dalej (komunikat, nie awaria); (6) przeglad z czlowiekiem: 6 zadan porannych (T14).
- Zalezy od: A3, A6. Ryzyka: pokazywanie nazwiska na ekranie (DW2); miniatury dla kilkuset projektow.

**E3-A8 - ramka i indicate na atrapach (L; dwoch wykonawcow o rozlacznych plikach).** Cel: protokol 3.6, program ramki
z wymiennym sprzetem, atrapa ramki w sieci lokalnej.
- Pliki: wykonawca 1: `ramka/**` (logika, serwer, `sprzet_atrapa.py`, `sprzet_rpi.py` - ten ostatni bez uruchamiania,
  czcionka, `README.md`), `narzedzia/atrapa_ramki.py`, `testy/test_ramka.py`; wykonawca 2: `stanowisko/indicate.py`,
  `stanowisko/ramka_protokol.py`, `testy/test_indicate.py`, `opisy_modulow/indicate.md`.
  Bez zmian w `aplikacja.py` i `ui/**` - podpiecie do programu robi A12.
- Kryteria: (1) plan plytki porannej (23 gniazda) -> zrzut matrycy 64 x 64 z atrapy: swieca dokladnie bloki z planu,
  reszta ciemna (porownanie piksel po pikselu); (2) margines pokazuje numer kuwety i liczbe prac; (3) sekwencja
  klawiszy Enter x 3, Backspace, cyfry + Enter daje dokladnie oczekiwana liste zdarzen; (4) zmiana plytki 4 -> 0 -> 5
  (atrapa czujnikow) przelacza plan w czasie ponizej 100 ms i daje zdarzenia `plytka`; (5) utrata sieci: 5 potwierdzen
  bez sieci -> po powrocie laptop dostaje dokladnie 5, w kolejnosci, bez powtorek (100 powtorzen z losowymi
  przerwami); (6) restart ramki: laptop sam wysyla plan ponownie w czasie do 5 s; (7) Spacja -> zmiana stanu ramki W
  ponizej 1 s (dwie maszyny w sieci lokalnej albo dwa procesy); (8) zapis calego ruchu sieciowego testow nie zawiera
  nazw folderow ani nazwisk; (9) program ramki w trybie atrapy importuje tylko biblioteke standardowa.
- Zalezy od: A6 (plan plytek), DW8, DW9. Ryzyka: prawdziwa matryca i odbiornik klawiatury zachowaja sie inaczej (C1);
  firmowe Wi-Fi moze blokowac ruch miedzy urzadzeniami (sekcja 10).

**E3-A9 - excel: reguly, log, tryb "pytaj" na sztucznym arkuszu (M).** Cel: wybor wiersza bez Excela; warstwa COM
osobno.
- Pliki: `stanowisko/excel.py` (reguly i log), `stanowisko/excel_com.py` (COM, bez uruchamiania w tej paczce),
  `narzedzia/arkusz_syntetyczny.py`, `testy/test_excel.py`, `opisy_modulow/excel.md`. Bez zmian w `aplikacja.py`
  i `ui/**` - podpiecie do programu robi A12.
- Kryteria: arkusz sztuczny 30 tys. wierszy A-I o fikcyjnych nazwach z pulapkami (ta sama kuweta w roznych datach,
  inicjaly zamiast nazwiska, puste H, pole B juz zielone, zera wiodace, reklamacja z nowym wierszem): (1) 200 zapytan
  o znanej odpowiedzi: 200 z 200 we wlasciwej klasie (jeden wiersz / juz odhaczone / wskaz wiersz z lista
  kandydatow), 0 zapisow w zlym wierszu; (2) wyszukanie ponizej 50 ms na zapytanie; (3) log CSV ma pola z reguly 6;
  (4) domyslnie "pytaj przed zapisem"; tryb "cien" nie zapisuje niczego; (5) zapis dotyka wylacznie koloru jednej
  komorki (sprawdzane na atrapie arkusza: zadna inna komorka sie nie zmienia).
- Zalezy od: A6, DW10. Ryzyka: prawdziwy arkusz ma inna strukture niz zalozona (D2).

**E3-A10 - raport metryk z bazy (S-M).** Cel: jedno polecenie = jedna strona (M1), tabela testow wykrywalnosci (M2).
- Pliki: `narzedzia/raport_metryk.py`, `stanowisko/metryki.py`, `testy/test_metryki.py`, `opisy_modulow/metryki.md`;
  migracja schematu do wersji 2 (`baza.py`) z opisem dla wlasciciela. Punkt wyjscia: `qc/metryki` z H.
- Kryteria: na bazie z sesji sztucznych o znanej prawdzie wartosci raportu = wartosci policzone recznie (tabela
  w tescie) dla: udzialu falszywych alarmow, top-1 i top-2 wzgledem decyzji, udzialu prac nieznanych, czasu przy
  stanowisku, udzialu skanow powtorzonych, dni bez awarii; raport do 60 linii.
- Zalezy od: A1, A6.

**E3-A11 - instalacja, aktualizacja, samokontrola, instrukcje (M).** Cel: wariant dystrybucji wybrany na G3 (sekcja 8).
- Pliki: `instalacja/**`, `narzedzia/zbuduj_wydanie.*`, `stanowisko/samokontrola.py`, `instrukcje/*.md`
  (wieczor - 6 krokow, poranek, "co robic, gdy nie dziala" - z PW zal. D, E, F), `README.md`.
- Kryteria: czyste konto na PC: instalacja jednym poleceniem z paczki bez internetu, start programu, samokontrola
  zielona (foldery, baza, pula, ramki nieobecne = ostrzezenie); aktualizacja N -> N+1 jednym poleceniem z zachowaniem
  ustawien i migracja bazy z kopia; powrot do N; sumy SHA-256 paczki zgodne.
- Zalezy od: G3 (DW11), wszystkich paczek A.

**E3-A12 - spiecie poranka: indicate i excel w aplikacji (S; w kolejnosci przed A11).** Cel: jeden program obsluguje
ramki i Excel.
- Pliki: zmieniane `stanowisko/aplikacja.py` i `stanowisko/ui/**` ("Test LED", stan ramek, okno "Excel: wskaz
  wiersz"), `opisy_modulow/aplikacja.md`; nowe `testy/test_aplikacja_rano.py`.
- Kryteria (offscreen, atrapa ramki, sztuczny arkusz): (1) po skanach 3 plytek plan odebrany przez atrape ramki
  porannej jest rowny planowi z `session` (pole po polu); (2) Enter na atrapie zapisuje potwierdzenie w `zdarzenia`,
  a klawisz "Zamknij piec" zamyka sesje pieca; (3) po "Zamknij piec" w trybie "pytaj" program proponuje dokladnie
  zlecenia kompletne z A6, a po zatwierdzeniu w arkuszu zmienia sie tylko kolor wlasciwych komorek; (4) Spacja
  zmienia stan atrapy ramki wieczornej w czasie ponizej 1 s, a po analizie atrapa dostaje kolory gniazd rowne mapie
  na ekranie; (5) wylaczona ramka albo brak Excela = ostrzezenie i dalsza praca.
- Zalezy od: A7, A8, A9.

### 4.2 (B) Wymaga pierwszych skanow

| Kod | Cel | Warunki wejscia | Kryterium odbioru | Zalezy od | Wielk. | Ryzyka |
|---|---|---|---|---|---|---|
| B1 | Dzien skanera: pierwsze dane (paczka innych wykonawcow - tu zaleznosc) | skaner na miejscu, stare plytki R54 | lista z RD "Laptop firmowy" pkt 6-7: szum, 3 stozki, dolki, pokrycie, czas, miary straznika K1 i K2 | KO | - | pole skanowania i dolki kwadratu |
| B2 | `scanner` na prawdziwym programie skanera: wzorzec nazw, struktura folderu, koniec zapisu, "aktywuj okno + Spacja", fokus | B1; odpowiedzi na S5 i S6 | 30 kolejnych skanow: 30 zdarzen, 0 przedwczesnych, 0 zgubionych; Spacja z naszego okna startuje skan w 30 z 30 prob albo udokumentowany powod przejscia na reczne nacisniecie w programie skanera | A2, A3 | S-M | kazdy skan wymaga zlecenia; licencja i klucz sprzetowy |
| B3 | Progi `match` / `inspect`, pula i czasy na prawdziwych skanach | B1; pliki skanow i projekty tych prac ze wspolczynnikami | PW "Uruchomienie" krok 2: trafnosc dopasowania na 40 pracach co najmniej 85 %, z 10 znanych ubytkow wykryte co najmniej 8; analiza plytki do 40 s na laptopie stanowiska | A5, P1-P3 | M | skan widzi tylko gore pracy (OM match) |
| B4 | Wykrywanie ukruszen krawedzi "po danych ze skanera" (wybor C2 albo G13, progi, tor odporny na roznice systematyczne, mosty) | wszystkie: (1) eksport surowej siatki potwierdzony; (2) pomiar szumu, odstepu i korelacji narzedziem T10 -> klasa W; (3) 30-100 prawdziwych koron calych zeskanowanych; (4) pomiar roznic skan - projekt na brzegu koron calych; (5) korona wzorcowa z ukruszeniami 0,08-0,20 mm zmierzonymi pod mikroskopem; (6) decyzja wlasciciela o progu wymagania wg tabeli z WD pkt 5.2; (7) P2 i P4 scalone | cele z WD: czerwone co najmniej 90 % od progu z pkt (6), falszywe czerwone na koronach calych do 1 %, dowolny alarm do 10 % - liczone na prawdziwych skanach | B1, B3 | L | wymaganie 0,08 mm moze byc nieosiagalne dla tego skanera (WD pkt 1.3-1.4) |
| B5 | Poranek na spieczonych pracach: prog pewnosci, pokrycie | skany 10 spieczonych prac (PW "Test przed zakupem" krok 5) | pokrycie co najmniej 70 % i identyfikacja top-1 na probie; inaczej decyzja o planie B (kamera) - poza etapem | A7, B1 | M | przeziernosc cyrkonii |

### 4.3 (C) Wymaga zlozonej ramki albo Raspberry Pi

| Kod | Cel | Warunki wejscia | Kryterium odbioru | Zalezy od | Wielk. | Ryzyka |
|---|---|---|---|---|---|---|
| C1 | Program ramki na Raspberry Pi: matryca, czujniki Halla, klawiatura, autostart, system tylko do odczytu, Wi-Fi i hotspot | elektronika na stole (PR 9 kroki 2-5) | testy A8 powtorzone na sprzecie; kazdy klawisz daje wlasciwe zdarzenie; start po wlaczeniu pradu ponizej 60 s | A8 | M | biblioteka matrycy, zasieg odbiornika, firmowe Wi-Fi |
| C2 | Kalibracja gniazdo -> diody i narzedzie; odczyt plytek | zlozona ramka z wkladka, plytki z magnesami | kazde gniazdo z praca swieci przez otwor, sasiednie ciemne (PR 9 krok 13); odczyt 1-6 i 0 w 100 %, zmiana ponizej 100 ms (I5) - dla kazdego ukladu w uzyciu | C1, DW9 | S-M | stare i nowe plytki maja inne gniazda przy tych samych numerach |
| C3 | Proba calosci z dwiema ramkami: wieczor i rano, utrata sieci, 8 h | obie ramki zlozone | T15 z sekcji 7 | C2, A12 | S | - |

### 4.4 (D) Wymaga firmowego Excela, SharePointa, raportow albo laptopa stanowiska

| Kod | Cel | Warunki wejscia | Kryterium odbioru | Zalezy od | Wielk. | Ryzyka |
|---|---|---|---|---|---|---|
| D1 | Parser raportow MillBox (`millbox.py`) | 10 prawdziwych raportow (HTML albo PDF) na PC, poza repo; w testach tylko wersje zanonimizowane | 10 z 10 raportow: lista STL, krazek, wspolczynnik i data rowne odczytowi recznemu; STL z raportu polaczony z plikiem w folderze w 100 % probki | A4 | M | nazwy w raporcie inne niz w folderze; raport zawiera nazwiska |
| D2 | `excel_com.py` na kopii pliku produkcyjnego | kopia pliku, komputer z Excelem i sesja interaktywna (COM nie zadziala w sesji ssh - do sprawdzenia) | X7: 50 kuwet z historii, 50 z 50; zmienia sie tylko kolor pola B; COM widzi skoroszyt otwarty z Autozapisem | A9, DW10 | M | wspoledycja; struktura arkusza (X8) |
| D3 | Indeks na prawdziwym folderze "Cyrkon" i "Prywatne" | folder zsynchronizowany albo jego kopia | liczba nowych = liczba STL; kuwety i zeby zgodne na probce 50 folderow sprawdzonej recznie; liczba projektow z 4 dni zapisana (K11) | A4 | S | wzory nazw; pliki dodatkowe w folderach |
| D4 | Instalacja i proba calosci na laptopie stanowiska | laptop firmowy; decyzja G3 | T0, T2, T3 z sekcji 7 na laptopie; czas analizy plytki do 40 s | A11 | M | uprawnienia, antywirus, brak internetu |
| D5 | Zlecenia prywatne w Excelu | pierwsze trzy zlecenia prywatne (K12) | regula potwierdzona albo poprawiona | D2 | S | - |

## 5. Kolejnosc i sciezka krytyczna

```
G0 (plan, DW1-DW6, DW12) ; warunek techniczny: R59 w main
 |
 +--> A1 baza + sesja wieczorna ---+
 |                                 +--> A3 aplikacja + ekran wieczorny --> G1 --> [POZIOM 1 NA DZIEN SKANERA]
 +--> A2 scanner + silnik ---------+                                              |
 |                                                                                +--> B2, B3 (po B1)
 A1 --> A4 katalog + pule --> A5 pula w match (po P1, P3) --> D3 ; D1 (gdy sa raporty)
 A1, A4 --> A6 sesja poranna --> A7 ekran poranny (po A3)
                 A6 --> G2 (DW8-DW10) --> A8 ramka + indicate na atrapach --> C1 --> C2 --> C3
                 A6 --> A9 excel na sztucznym arkuszu --> D2 --> D5
 A7, A8, A9 --> A12 spiecie poranka w aplikacji (indicate + excel) --> C3
 A1, A6 --> A10 metryki
 wszystkie A --> G3 (DW11) --> A11 instalacja --> D4 --> testy koncowe (sekcja 7) --> G4
 B1 --> B3 --> B4 (dopiero po spelnieniu warunkow wejscia) ; B1 --> B5
```

| Fala | Paczki rownolegle | Co daje po zakonczeniu |
|---|---|---|
| 1 | A1, A2 (rozlaczne pliki, brak zaleznosci miedzy nimi) | baza i sesja; plik w folderze -> wynik bez zamrazania okna |
| 2 | A3, A4 | POZIOM 1: obserwacja folderu + sesja + ekran wieczorny na jednym laptopie (pula = folder i wspolczynnik wpisany recznie, jak w oknie testowym); indeks i pule z CSV |
| 3 | A5 (po P1 i P3), A6 | POZIOM 2: pula dnia ze wspolczynnikiem per praca; logika poranka |
| 4 | A7, A8, A9 | POZIOM 3: poranek na ekranie, ramka na atrapie, Excel w trybie "pytaj" na sztucznym arkuszu |
| 5 | A10, A12 | raport metryk; POZIOM 4: ramki (na atrapie) i Excel (tryb "pytaj") w jednym programie |
| 6 | A11 (po G3) | paczka instalacyjna i instrukcje |
| wg zdarzen | B (skaner), C (elektronika ramek), D (raporty, kopia Excela, laptop) | integracja z rzeczywistoscia |

Sciezka krytyczna do dnia skanera: G0 -> A1 i A2 -> A3. Sciezka krytyczna do konca etapu: A6 -> A7, A8, A9 -> A12, dalej
C1-C3 (ramki), D2 (Excel) i A11 -> D4 (laptop); najdluzej czekaja rzeczy zalezne od ludzi i dostaw: raporty
MillBox (D1), kopia Excela (D2), elektronika ramek (C), skaner (B). Dlatego zadania z sekcji 13 warto zlecic od razu.
Zaleznosci od paczek w toku: A3 - okno "Dzien skanera" (rozpoznawanie ukladu jest juz gotowe w PR #13);
A5 - P1 i P3 (ten sam plik `match.py`); A1, A3, A7 - P2 (nowy status "nie sprawdzono"); B4 - P2 i P4.

## 6. Bramki i decyzje wlasciciela

Bramki: **G0** akceptacja planu i decyzje (mozna odpowiedziec na wszystkie 12 naraz) - **G1** pokaz ekranu wieczornego
na danych sztucznych (po A3) - **G2** pokaz poranka i decyzje o ramce i Excelu (przed A8 i A9) - **G3** dystrybucja
(przed A11) - **G4** wynik testow koncowych i zgoda na uruchomienie na laptopie stanowiska. Niezaleznie: zgoda
wlasciciela na scalenie kazdej paczki do `main`.

| Id | Pytanie i odpowiedz w jednym zdaniu | Zalecana odpowiedz domyslna | Skutek | Kiedy |
|---|---|---|---|---|
| DW1 | Czy akceptujesz model danych z sekcji 3.4 (11 tabel, jeden plik bazy na laptopie)? TAK / NIE / zmiana | TAK | A1 tworzy baze; kazda pozniejsza zmiana schematu to migracja z opisem dla wlasciciela | G0 - BLOKUJE A1 |
| DW2 | Gdzie moze byc zapisana nazwa folderu zlecenia (z nazwiskiem): (a) w lokalnej bazie na laptopie stanowiska, (b) tylko w osobnym pliku mapy poza baza | (a), wylacznie w tabelach `zlecenia` i `excel_zapisy` | prostsze laczenie z kolumna H Excela; plik bazy staje sie plikiem z danymi osobowymi (dysk szyfrowany, poza OneDrive i gitem, kopie dla programistow bez tych kolumn) | G0 - BLOKUJE A1 |
| DW3 | Skad program wie, kto pracuje ("kto zatwierdzil" w logu): (a) wybor osoby z listy przy starcie zmiany, (b) nazwa konta Windows, (c) nie zapisujemy osoby | (a) | jedno klikniecie na zmiane; kolumna `operator` w decyzjach i logu | G0 - BLOKUJE A1 |
| DW4 | Jak dlugo trzymac pliki skanow (ok. 50 MB kazdy, 0,5-1 GB dziennie): 30 dni / do konca trybu cienia / bezterminowo | do konca trybu cienia wszystko, potem 30 dni; wyniki i baza bezterminowo | miejsce na dysku; material do strojenia progow | G0 |
| DW5 | Kto lapie Spacje: (a) nasze okno, ktore aktywuje okno skanera i naciska w nim Spacje, (b) technik naciska Spacje w programie skanera, a nasz program tylko czeka na plik | (a), z (b) jako zapasem; ostateczne potwierdzenie na skanerze (B2) | przy (a) ramka wieczorna zmienia stan od razu; przy (b) dopiero po pojawieniu sie pliku | G0 albo G1 |
| DW6 | Wspolczynnik skurczu do czasu parsera raportow MillBox: (a) plik CSV wypelniany przy frezarce, (b) wpis reczny w aplikacji raz na krazek, (c) oba | (c) | pula wieczorna dziala bez raportow; ktos musi podac wspolczynnik krazka | G0 (przed A4) |
| DW7 | Podglad 3D pracy: (a) jak dzis - obraz odchylek w oknie i osobne okno 3D, (b) widok 3D wbudowany w ekran (nowa biblioteka albo wlasny renderer = zmiana stosu) | (a) w etapie 3 | bez zmiany stosu; (b) mozna dodac pozniej | G0 albo G1 |
| DW8 | Lacznosc z ramkami: (a) HTTP i JSON z biblioteki standardowej, laptop odpytuje ramke, (b) WebSocket (nowa biblioteka na Raspberry Pi) | (a), format z sekcji 3.6 | zero nowych zaleznosci; opoznienie zdarzen z ramki do ulamka sekundy | G2 (przed A8) |
| DW9 | Uklad gniazd na ramce (decyzja otwarta nr 10 planu wdrozenia): czy laptop wysyla ramce gotowe piksele dla plytki o danym numerze, a kalibracja lezy w osobnym pliku lokalnym? TAK / NIE | TAK | ramka nie musi odrozniac starej plytki od nowej; plytka polozona bez wczesniejszego skanu pokazuje "brak planu"; pliki `uklad.json` zostaja bajtowo bez zmian | G2 (przed A8) |
| DW10 | Excel w etapie 3: czy program pracuje wylacznie w trybie "pytaj przed zapisem" i w trybie cienia (bez samodzielnego zapisu)? TAK / NIE | TAK | plik produkcyjny bezpieczny; zapis samodzielny dopiero po audycie 50 z 50 (etap 4) | G2 (przed A9) |
| DW11 | Dystrybucja na laptop stanowiska: wariant A / B / C / D / E z sekcji 8 | B (paczka ZIP z kolami pip i skryptem instalacji) | zmiana dystrybucji; instalacja bez internetu, sumy SHA-256, szybki powrot do poprzedniej wersji | G3 (przed A11) |
| DW12 | Czy etap 3 konczy sie gotowoscia do trybu cienia, a metryki odbiorcze z produkcji i tryb pelny to etap 4? TAK / NIE | TAK | definicja konca etapu w sekcji 7 | G0 |

**Blokuja start pierwszej paczki (A1): DW1, DW2, DW3.** A2 nie czeka na zadna decyzje - moze ruszyc po akceptacji planu.
Warunki techniczne startu obu: R59 scalone do `main`; potwierdzone modele i effort wykonawcow (sekcja 9).

Zalozenia przyjete bez pytania (wlasciciel moze je zmienic na G0):

| Id | Zalozenie |
|---|---|
| Z1 | Tryb "Wieczor" / "Poranek" wybiera czlowiek; typ plytki niezgodny z trybem = ostrzezenie, nie samoczynna zmiana trybu |
| Z2 | Uklad plytki z automatycznego rozpoznania: GOTOWE 15.11 w PR #13 (`plate.rozpoznaj_uklad`, `porownaj(..., plytka="auto")`, 80/80 na skanach syntetycznych); silnik wola `porownaj` z `plytka="auto"`, wybor reczny tylko jako zapas |
| Z3 | Numer plytki z dolkow, gdy sa widoczne; inaczej jedno nacisniecie cyfry na ekranie (rano obowiazkowe przed "Zamknij piec"; wieczorem numer moze tez przyjsc z ramki wieczornej, gdy technik polozy na niej plytke) |
| Z4 | Skan plytki o tym samym numerze w tej samej sesji zastepuje poprzedni po potwierdzeniu jednym przyciskiem; decyzje poprzedniego skanu nie przechodza |
| Z5 | Pula odswiezana przy starcie, przyciskiem i po pojawieniu sie nowego pliku; "co noc" tylko gdy laptop jest wlaczony |
| Z6 | Lista "do dofrezowania": na ekranie i jako plik w `dane/`; druk i wysylka poza etapem |
| Z7 | Progi w `ustawienia.toml`; ekran pokazuje je tylko do odczytu |
| Z8 | Statusy i kolory jako jedna tabela danych, bo P2 i B4 dodadza nowe |
| Z9 | Slowo "poprawka" ma dzis dwa znaczenia: gladka poprawka reczna ksztaltu (pomaranczowy, RD) i zab dofrezowany do zlecenia juz odhaczonego (bursztyn, PW) - na ekranie dostana rozne napisy; nazwy do zatwierdzenia na G1 |
| Z10 | Modele: koordynator i wykonawcy jak w paczce R59; recenzje wg zasady D38 (duzy PR, zmiana schematu bazy albo wiele modulow - Fable; ponowne i male - Opus xhigh) - do potwierdzenia w prompcie startowym |

## 7. Testy koncowe etapu i definicja "gotowe"

Wykonuje koordynator ostatniej paczki, sam, na czystej kopii `main` zainstalowanej z paczki wydania; dowody do
`Ramki/etap3/odbior_koncowy/`. Test nieudany = wpis FAIL, poprawka przez wlasciwa paczke, powtorka.

| Nr | Test | Jak | Kryterium |
|---|---|---|---|
| T0 | Czysta instalacja | paczka wydania na czystym koncie PC, wg instrukcji, bez internetu | program startuje; samokontrola zielona; sumy SHA-256 zgodne |
| T1 | Testy programu | pytest caly | 0 failed, 0 errors; pominiete tylko znane z punktu odniesienia |
| T2 | Wieczor od poczatku do konca | symulator wrzuca 10 plytek co 60 s: uklady R59 i R54, okragle, 1 niezgodny uklad, 1 drgniecie, 1 plik uciety | 10 z 10 obsluzonych zgodnie z prawda; start analizy ponizej 1 s od zapisu; mapa do 40 s (mediana); okno bez przerw ponad 200 ms; lista "do dofrezowania" = prawda |
| T3 | Poranek od poczatku do konca | scenariusz SE10 z A6 przez ekran: 3 piece, dofrezowany zab, poprawka, dwuznaczna, nieznana | listy kompletnych i brakow zgodne z tabela oczekiwan w 100 % wierszy |
| T4 | Pula | 400 wpisow, dwa wspolczynniki na plytce, STL w dwoch raportach | top-1 "dobrze" 100 %; plytka do 40 s; pamiec do 8 GB |
| T5 | Ramka na atrapie w sieci lokalnej | plan, kolory, kuweta po kuwecie, zmiana plytki, 5 potwierdzen bez sieci, restart ramki, Spacja | 5 z 5 potwierdzen dostarczonych, 0 powtorek; plan odtworzony do 5 s; stan po Spacji ponizej 1 s |
| T6 | Excel na sztucznym arkuszu | 200 zapytan na 30 tys. wierszy; tryb "pytaj" i "cien" | 200 z 200; 0 zlych wierszy; log zgodny z regula 6 |
| T7 | Odpornosc | zabicie silnika w trakcie analizy; zamkniecie programu w polowie wieczoru; brak folderu "Cyrkon"; brak sieci; brak ramki; baza zajeta | za kazdym razem komunikat z PW zal. F i dalsza praca; stan odtworzony z bazy |
| T8 | Metryki | raport jednym poleceniem na bazie z T2 i T3 | wartosci = policzone recznie |
| T9 | Dane osobowe | wyszukanie nazw folderow zlecen w repo, logach, plikach wynikow, ruchu sieciowym do ramki | 0 trafien; nazwy tylko w `dane/` (baza, log Excela) |
| T10 | Regresja silnika | zestawy R59 (40 skanow) | wyrownanie 40 z 40, top-1 "dobrze" 100 %, falszywe czerwone na pracach calych 0 (R59 pkt 6.2) |
| T11 | Stare plytki | skany `*_r54` przez aplikacje | uklad rozpoznany albo ostrzezenie z nazwa wlasciwego ukladu; 0 zielonych przy zlym ukladzie; uklad zapisany w `skany` |
| T12 | Aktualizacja | wersja N -> N+1 -> powrot do N | jedno polecenie; ustawienia zachowane; baza zmigrowana z kopia |
| T13 | Higiena repo | diff wzgledem poczatku etapu | tylko pliki z list paczek; nowe pliki ASCII; brak STL i danych |
| T14 | Proba "technik obsluguje bez instrukcji" (czlowiek) | osoba, ktora nie widziala programu, dostaje jedna strone z obrazkami i zadnych podpowiedzi; symulator podaje skany. Wieczor: (1) zeskanuj plytke, (2) wskaz prace do obejrzenia, (3) oznacz jedna jako ukruszona i jedna jako OK, (4) poradz sobie z "popraw ulozenie", (5) pokaz liste do dofrezowania. Rano: (1) zeskanuj 2 plytki pieca, (2) rozstrzygnij dwuznaczna, (3) rozloz jedna kuwete wedlug ramki albo ekranu, (4) cofnij pomylke, (5) znajdz kuwete po numerze, (6) zamknij piec i odczytaj braki | 11 z 11 zadan wykonanych, 0 interwencji obserwatora; miejsca zawahania dluzszego niz 10 s spisane i poprawione albo swiadomie zostawione |
| T15 | (C) Ramki na sprzecie | PR 9 kroki 11-14 + T5 na prawdziwych ramkach | odczyt plytki 100 % ponizej 100 ms; 8 h bez restartu; start ponizej 60 s |
| T16 | (B) Prawdziwy skaner | PW "Uruchomienie" kroki 1-2 | skan testowej plytki laduje w folderze i program go rozpoznaje; trafnosc na 40 pracach co najmniej 85 %; z 10 znanych ubytkow co najmniej 8 |
| T17 | (D) Excel i MillBox na prawdziwych danych | D1 i D2 | 10 z 10 raportow; 50 z 50 kuwet |

Definicje:
- **Koniec etapu 3 = gotowe do trybu cienia:** T0-T14 zaliczone; T15-T17 zaliczone albo jawnie odlozone z powodem
  "brak sprzetu / danych" i z nazwanym warunkiem wznowienia; instrukcje jednostronicowe i tabela "co robic, gdy nie
  dziala" gotowe; kroki 1-5 z PW "Uruchomienie" da sie wykonac bez programisty przy klawiaturze.
- **Gotowe do pracy produkcyjnej (tryb pelny, etap 4):** wszystko powyzej oraz: T14 powtorzone na stanowisku
  z prawdziwym skanerem (PW: obserwacja 3 wieczorow, 0 interwencji w ostatni); 5 kolejnych dni bez awarii
  wymagajacej restartu; audyt Excela 50 z 50 w trybie "pytaj"; progi odbioru z tabeli PW "Testy odbiorcze i kryteria"
  spelnione w trybie cienia; druga osoba przeszkolona w restarcie; kopia zapasowa bazy sprawdzona odtworzeniem.

## 8. Dystrybucja na laptop stanowiska (zmiana dystrybucji - decyzja wlasciciela DW11, bramka G3)

Dzis: kopia folderu `stanowisko/` i `py -3.12 -m pip install -r requirements.txt` (DY2). Wymaganie: wersja zamrozona,
aktualizacja jednym poleceniem (DY1).

| Wariant | Opis | Plusy | Minusy |
|---|---|---|---|
| A | jak dzis + skrypt `aktualizuj.cmd` | zero pracy | potrzebny internet i PyPI na firmowym laptopie; kroki reczne latwo pominac (R59 pkt 9.1); brak powrotu do poprzedniej wersji; brak sum |
| B | paczka wydania ZIP: program + kola pip dla Windows i Pythona 3.12 + `zainstaluj.cmd` + `SHA256SUMS`; instalacja do katalogu wersji z wlasnym srodowiskiem; ustawienia i `dane/` poza katalogiem wersji; skrot "Stanowisko" wskazuje wersje biezaca | bez internetu, powtarzalnie, z sumami; powrot = przelaczenie katalogu; pasuje do dotychczasowych pakietow ZIP z sumami i do katalogu wydan (jeden plik na wydanie) | trzeba napisac skrypt paczki; ZIP duzy (szacunek kilkaset MB - niezmierzone); Python 3.12 instalowany raz recznie |
| C | jeden program EXE (PyInstaller albo podobne) | nie trzeba Pythona; dwuklik | nowe narzedzie w stosie; Open3D i PySide6 bywaja klopotliwe w takim pakowaniu; niepodpisany EXE moze zatrzymac antywirus albo polityka firmowa; trudniejsza diagnoza |
| D | `git` na laptopie: `git fetch` i przelaczenie na tag + pip | aktualizacja doslownie jednym poleceniem, pelna historia | git i dostep do prywatnego repo z firmowego laptopa (token w firmie); pip nadal z internetu; repo zawiera tez duze pliki ramek |
| E | jak B, ale z Pythonem w paczce (wersja "embeddable") | nic nie instalujemy w systemie | nietypowa konfiguracja (pywin32, sciezki); wiecej pracy niz B |

Zalecenie: **B**; kanal przekazania - katalog wydan na serwerze, jesli wlasciciel uruchomi go dla projektu qc (sprawa
otwarta w paczce R59), inaczej pendrive albo OneDrive. Program ramki: osobna mala paczka (pliki Pythona + skrypt
instalacji) wgrywana przez siec lokalna; sposob aktualizacji karty "tylko do odczytu" ustala C1.
Nieznane, a wazne dla wyboru: uprawnienia i zabezpieczenia firmowego laptopa (sekcja 12.1, poz. 14).

## 9. Zasady wspolne paczek

Obowiazuje sekcja 2 planu R59 (`Ramki/plan_sesji_R59_uklad_gniazd_2026-11-14.md`: role, galaz, zasady PC, zasady
tresci) z roznicami:

| Temat | Zasada w etapie 3 |
|---|---|
| Galaz i PR | jedna galaz i jeden PR na paczke, od `origin/main`; scalenie tylko za zgoda wlasciciela |
| Etap 0 kazdej paczki | `git fetch`; kontrola kolizji (`git worktree list`, `git branch -r`, `gh pr list`) z paczkami w toku - w szczegolnosci P1-P4, rozpoznawanie ukladu, "Dzien skanera"; punkt odniesienia `pytest` na PC |
| Pliki wspolne | `ustawienia.py`, `ustawienia.przyklad.toml`, `requirements.txt`, `README.md`, `opisy_modulow/README.md`, `baza.py` (po A1), `statusy.py` (po A3) zmienia w danej fali tylko jedna paczka; inna zglasza "POTRZEBUJE: plik, powod" |
| Pliki nietykalne bez osobnej zgody | `match.py`, `inspect.py`, `plate.py`, `synth.py`, `uklad.py` (poza A5), `modele_plytek/**`, progi `[match]` i `[inspect]`, `Ramki/stanowisko/raporty/testy_krawedz/**` |
| [usunieto w kopii: opis dostepu ssh]
| Dane osobowe | w raportach, logach, commitach i odpowiedziach tylko `sha16` projektu i numery kuwet z danych sztucznych; nazwy folderow i plikow zlecen nigdy; dane testowe z fikcyjnymi nazwami |
| Jezyk i pliki | nowe pliki: polski bez znakow diakrytycznych, ASCII, konce linii LF (skrypty `.cmd`, `.bat`, `.ps1`: CRLF); istniejace zostaja w swoim stylu |
| Uczciwosc wynikow | liczniki (np. 43 z 50), nie same procenty; kazde odstepstwo opisane; testu nieudanego nie pomijac |
| Uwaga o instrukcjach | `CLAUDE.md` w repo opisuje jeszcze dostep do PC sprzed 12.11 (konto i klucz); obowiazuja zasady globalne (konto `<konto-PC>`) i poprawka czekajaca w glownym katalogu |

## 10. Ryzyka etapu

| Ryzyko | Skutek | Jak ograniczamy |
|---|---|---|
| Kolizje plikow z paczkami w toku (ich list plikow nie znamy) | konflikty, powtorki | etap 0; paczki A tworza glownie nowe pliki; A5 dopiero po P1 i P3 |
| Open3D z Qt i watkami (zawis 195 s; w H opisana awaria przy rownoleglym BLAS i Open3D) | zamrozone okno, awarie | jeden proces silnika, jedna analiza naraz, kryteria A2 pkt 6 i 7 |
| Pula kilkuset projektow: czas i pamiec | analiza dluzsza niz 40 s | filtr na cechach z bazy, budowa ciezkich obiektow tylko dla kandydatow, pomiar w A5 i D4 |
| Brak wzoru raportu MillBox | pula wieczorna bez automatu | CSV i wpis reczny (DW6); D1 zaraz po dostarczeniu raportow |
| COM Excela: sesja interaktywna, wspoledycja, nieznana struktura arkusza | D2 nie da sie zrobic zdalnie | reguly i log oddzielone od COM (A9); tryb "pytaj" (DW10); D2 na komputerze z Excelem |
| Firmowe Wi-Fi blokuje ruch miedzy urzadzeniami albo nazwy `.local` | laptop nie widzi ramki | hotspot laptopa (PW), adresy stale w ustawieniach; sprawdzenie w C1 |
| Eksport skanera inny niz zakladany (nazwy, kilka plikow, zlecenie na skan, plaszczyzna ciecia) | `scanner` do poprawki | parametry zamiast stalych (wzorzec, stabilizacja); B2 |
| Numer plytki kwadratowej niewidoczny w polu fi 100 | dodatkowe nacisniecie przy kazdym skanie; pomylki | Z3; sprawdzenie pola na dniu skanera (B1) |
| Reczne kroki przy aktualizacji ustawien | program nie startuje albo dziala po staremu (R59 pkt 9.1) | klucze opcjonalne (A1), migracja w instalatorze (A11) |
| Wynik analizy zmieni sie po P2 i B4 (nowe statusy, "nie sprawdzono") | przerobki ekranow | statusy jako dane (Z8); wynik JSON zapisywany w calosci |
| Skany zajmuja dysk; OneDrive moglby synchronizowac `dane/` | brak miejsca, wyciek danych | DW4; `dane/` poza folderami OneDrive; samokontrola sprawdza sciezki |
| Jedna maszyna liczaca (PC), wspoldzielona | kolejki, mylace czasy | pomiary czasu tylko przy wolnym PC; liczby jakosci z przebiegow rownoleglych |
| Dlugie paczki L (A3, A7, A8) | zapelnienie kontekstu wykonawcy | stan w plikach `Ramki/etap3/stan_<kod>.md`; podzial na wykonawcow o rozlacznych plikach |

## 11. Trzy pierwsze paczki - szkice promptow koordynatora

Kolejnosc: A1 i A2 rownolegle (fala 1), potem A3. Przed startem: plan zatwierdzony i zapisany w `main` (albo w galezi
paczki), R59 scalone, odpowiedzi G0 wklejone do promptu. Mechanizm wykonawcow i modele - jak w paczce R59, chyba ze
wlasciciel wskaze inaczej (Z10).

### 11.1 E3-A1 - baza i sesja wieczorna

```
Jestes koordynatorem paczki E3-A1 (baza i sesja wieczorna) projektu qc. Model i effort ustawil wlasciciel -
potwierdz je narzedziem get_session w pierwszej odpowiedzi.
PRZECZYTAJ: Ramki/plan_etap3_pelna_aplikacja_2026-11-16.md sekcje 0-3, 4.1 (E3-A1), 9, 12; wzor pracy koordynatora:
Ramki/plan_sesji_R59_uklad_gniazd_2026-11-14.md sekcje 2, 5, 14, 15, 17; Ramki/stanowisko/opisy_modulow/README.md
i ui.md; Ramki/stanowisko/stanowisko/porownaj.py (format wyniku) i ustawienia.py.
DECYZJE WLASCICIELA (G0): <wklej doslownie odpowiedzi DW1-DW4, DW12 i zmiany zalozen Z1-Z10>.
CEL: modul baza (SQLite wg sekcji 3.4 planu) i modul session dla wieczoru: przyjecie wyniku skanu, prace, decyzje
"Ukruszona" / "OK", ponowny skan, lista "do dofrezowania", odtworzenie stanu po restarcie programu.
ETAP 0: (1) git fetch; R59 musi byc w origin/main - jesli nie jest, stop i pytanie; (2) kolizje: git worktree list,
git branch -r, gh pr list - stop, gdy inna sesja zmienia pliki z listy ponizej; (3) galaz od origin/main;
(4) PC: katalog <PC-katalog>\e3\a1, kopia galezi i run.cmd wg planu R59 pkt 2.4; (5) punkt odniesienia:
pytest testy -q na PC (oczekiwane co najmniej 252 passed, 3 skipped, 0 failed) - liczby do Ramki/etap3/stan_A1.md.
WYKONAWCY (kolejno, kazdy w swiezej subsesji, bez git add / commit / push):
 A1-T testy (najpierw czerwone): testy/test_baza.py, testy/test_session_wieczor.py, testy/dane_sesji/**;
 A1-K kod: stanowisko/baza.py, stanowisko/session.py, narzedzia/import_decyzji.py, stanowisko/ustawienia.py,
   ustawienia.przyklad.toml, testy/test_ustawienia.py, opisy_modulow/baza.md, opisy_modulow/session.md,
   raporty/E3-A1_<data>.md;
 A1-R recenzja w swiezej subsesji (zmiana schematu bazy - dobor modelu wg D38).
PLIKI KOORDYNATORA: Ramki/etap3/stan_A1.md, Ramki/etap3/odbior_A1/**, jedna sekcja "Etap 3" w Ramki/00_NADZOR_STAN.md.
NIE WOLNO: zmieniac match.py, inspect.py, plate.py, porownaj.py, synth.py, uklad.py, katalog.py, ui_test.py,
modele_plytek/**, progow [match] i [inspect], requirements.txt; dodawac kluczy WYMAGANYCH do SCHEMAT (nowe klucze
tylko opcjonalne z wartoscia domyslna); zapisywac nazw folderow i plikow zlecen poza tabelami zlecenia
i excel_zapisy; zmieniac schematu wzgledem sekcji 3.4 bez pytania do wlasciciela; liczyc na MSI; instalowac
czegokolwiek na PC; scalac do main bez zgody wlasciciela.
KRYTERIA ODBIORU: punkty 1-11 z sekcji 4.1 planu (E3-A1) - kazdy jako test na danych sztucznych, wynik liczbami.
TESTY KONCOWE KOORDYNATORA (sam, czysta kopia galezi na PC): pytest caly; wlasny skrypt (nie testy wykonawcy):
3 wyniki porownaj -> baza -> 3 decyzje -> zamkniecie -> otwarcie -> zrzut stanu identyczny; lista zmienionych plikow
zawiera sie w liscie paczki; nowe pliki ASCII; 0 nazw folderow zlecen w diffie, logach i bazie testowej.
KONIEC: PR do main, raport do 40 linii (co zrobione, testy przed -> po, odstepstwa, czego nie zrobiono), prosba
o zgode na scalenie; zadania czlowieka wypisz i dodaj do Todoist. Pisz krotko - wlasciciel czyta z telefonu.
```

### 11.2 E3-A2 - scanner, silnik w osobnym procesie, symulator skanera

```
Jestes koordynatorem paczki E3-A2 (scanner, silnik, symulator folderu skanera) projektu qc. Model i effort ustawil
wlasciciel - potwierdz je narzedziem get_session w pierwszej odpowiedzi.
PRZECZYTAJ: Ramki/plan_etap3_pelna_aplikacja_2026-11-16.md sekcje 0-3, 4.1 (E3-A2), 9, 12; wzor pracy:
Ramki/plan_sesji_R59_uklad_gniazd_2026-11-14.md sekcje 2, 5, 14, 15, 17; Ramki/notatki_dokumentacja_skanera.md;
Ramki/stanowisko/raporty/P3a_przekazanie.md pkt 5.1; Ramki/stanowisko/stanowisko/porownaj.py, ui_test.py (Robotnik),
podglad3d.py; opisy_modulow/README.md (wiersz scanner).
CEL: (1) scanner: obserwacja folderu (watchdog), pewne rozpoznanie konca zapisu, walidacja STL, zdarzenie "nowy skan";
(2) silnik: analiza porownaj.porownaj w OSOBNYM PROCESIE z kolejka zadan, postepem i obsluga awarii - bez Open3D
w watkach Qt; (3) narzedzie symulator_skanera.py: kopiuje sztuczne skany do folderu jak skaner (w kawalkach,
z opoznieniem, z plikami zlymi).
ETAP 0: jak w E3-A1 pkt 1-5 (katalog PC: <PC-katalog>\e3\a2). DODATKOWO: sprawdz, czy paczka "Dzien skanera" nie
dostarczyla juz silnika w osobnym procesie albo obserwacji folderu (pliki w origin/main i otwarte PR) - jesli tak,
uzyj tego i zawez zakres; opisz to wlascicielowi przed startem wykonawcow.
WYKONAWCY (bez git add / commit / push):
 A2-S scanner + symulator: stanowisko/scanner.py, narzedzia/symulator_skanera.py, testy/test_scanner.py,
   opisy_modulow/scanner.md;
 A2-E silnik: stanowisko/silnik.py, testy/test_silnik.py, opisy_modulow/silnik.md, raporty/E3-A2_<data>.md;
 A2-R recenzja w swiezej subsesji (dobor modelu wg D38).
 A2-S i A2-E moga isc rownolegle (pliki rozlaczne; kontrakt ZdarzenieSkanu i ZadanieAnalizy z sekcji 3.8 planu).
PLIKI KOORDYNATORA: Ramki/etap3/stan_A2.md, Ramki/etap3/odbior_A2/**.
NIE WOLNO: zmieniac zadnego istniejacego pliku programu (w szczegolnosci porownaj.py, match.py, plate.py, inspect.py,
ui_test.py, ustawienia.py, ustawienia.przyklad.toml, requirements.txt) - parametry scanner i silnika w konstruktorach
z wartosciami domyslnymi; dodawac bibliotek spoza requirements.txt; pisac automatu klikajacego w programie skanera
(akcja "start skanu" tylko jako interfejs z atrapa); zakladac nazw i struktury plikow prawdziwego skanera (wzorzec
i czasy jako parametry); liczyc na MSI; instalowac czegokolwiek na PC; scalac do main bez zgody wlasciciela.
KRYTERIA ODBIORU: punkty 1-8 z sekcji 4.1 planu (E3-A2); wyniki jako liczniki (np. 100 z 100) i czasy z PC.
TESTY KONCOWE KOORDYNATORA (sam, czysta kopia na PC): pytest caly; wlasny przebieg: symulator wrzuca 12 skanow
(4 typy plytek, seedy inne niz u wykonawcow, 2 pliki zle) -> 10 wynikow rownych wynikom porownaj z wiersza polecen,
2 odrzucenia z powodem; pomiar opoznienia zdarzenia; test z petla Qt offscreen; lista zmienionych plikow = lista
paczki.
KONIEC: PR do main, raport do 40 linii, prosba o zgode na scalenie; zadania czlowieka do Todoist. Pisz krotko.
```

### 11.3 E3-A3 - aplikacja i ekran wieczorny (start po scaleniu A1 i A2)

```
Jestes koordynatorem paczki E3-A3 (aplikacja "Stanowisko" i ekran wieczorny) projektu qc. Model i effort ustawil
wlasciciel - potwierdz je narzedziem get_session w pierwszej odpowiedzi.
PRZECZYTAJ: Ramki/plan_etap3_pelna_aplikacja_2026-11-16.md sekcje 0-3, 4.1 (E3-A3), 6 (zalozenia Z1-Z9), 7 (T14), 9,
12; wzor pracy: Ramki/plan_sesji_R59_uklad_gniazd_2026-11-14.md sekcje 2, 5, 14, 15, 17; dokument glowny planu
wdrozenia v2 w Ramki/ - sekcje "Przeplyw wieczorny krok po kroku" i zalaczniki D, F; opisy_modulow: ui.md, session.md,
scanner.md, silnik.md, baza.md; stanowisko/ui_test.py (MapaPlytki, obraz_odchylek).
DECYZJE WLASCICIELA: <wklej odpowiedzi DW5, DW7 i zmiany zalozen Z1-Z9>.
CEL: jeden program uruchamiany skrotem: tryb "Wieczor" - obserwacja folderu (A2) -> analiza w procesie silnika ->
zapis w sesji (A1) -> mapa plytki, widok pracy z obrazem odchylek i rozmiarem ubytku, decyzje "Ukruszona" / "OK",
lista "do dofrezowania", komunikaty z zalacznika F planu wdrozenia. Pula na tym etapie: folder projektow i jeden
wspolczynnik wpisany recznie (jak w oknie testowym) - pule z indeksu dojda w A4 i A5.
ETAP 0: jak w E3-A1 pkt 1-5 (katalog PC: <PC-katalog>\e3\a3). WARUNEK: A1 i A2 scalone do main. DODATKOWO: sprawdz
stan paczek "Dzien skanera" i "rozpoznawanie ukladu plytki" - jesli sa scalone, uzyj ich (uklad "rozpoznaj"),
jesli nie - wybor ukladu reczny (zalozenie Z2).
WYKONAWCY (bez git add / commit / push):
 A3-U ekran: stanowisko/ui/** (nowy pakiet), stanowisko/statusy.py, testy/test_ui_wieczor.py;
 A3-A spiecie: stanowisko/aplikacja.py, uruchom_stanowisko.bat, testy/test_aplikacja.py, opisy_modulow/aplikacja.md,
   opisy_modulow/README.md, README.md (struktura i uruchomienie), raporty/E3-A3_<data>.md; podpiecie kluczy
   [scanner] i [sesja] z ustawien (mechanizm kluczy opcjonalnych z A1);
 A3-R recenzja w swiezej subsesji (wiele modulow - dobor modelu wg D38).
PLIKI KOORDYNATORA: Ramki/etap3/stan_A3.md, Ramki/etap3/odbior_A3/** (w tym zrzuty ekranu dla wlasciciela).
NIE WOLNO: edytowac ui_test.py (tylko import), porownaj.py, match.py, plate.py, inspect.py, baza.py, session.py,
scanner.py, silnik.py (blad w nich = zgloszenie "POTRZEBUJE", nie cicha poprawka); wpisywac kolorow i napisow
statusow w kodzie ekranow (tylko statusy.py); dodawac bibliotek (widok 3D zostaje jak dzis - DW7); budowac ekranu
porannego, ramek i Excela; pokazywac nazw folderow zlecen w zrzutach i raportach (dane sztuczne z fikcyjnymi
nazwami); liczyc na MSI; scalac do main bez zgody wlasciciela.
KRYTERIA ODBIORU: punkty 1-7 z sekcji 4.1 planu (E3-A3) jako testy offscreen na PC + punkt 8 jako bramka G1.
TESTY KONCOWE KOORDYNATORA (sam, czysta kopia na PC): pytest caly; wlasny scenariusz: symulator wrzuca 10 plytek
(w tym 1 niezgodny uklad, 1 drgniecie, 1 plik uciety) do dzialajacej aplikacji offscreen -> stan bazy i kolory mapy
rowne prawdzie; restart w polowie; zrzuty ekranu 5 stanow (pusta, wynik, widok pracy, komunikat, lista do
dofrezowania) wyslane wlascicielowi jako pliki.
BRAMKA G1: przeglad z wlascicielem albo technikiem - 5 zadan wieczornych z T14 bez podpowiedzi; uwagi -> jedna runda
poprawek. KONIEC: PR do main, raport do 40 linii, prosba o zgode na scalenie; zadania czlowieka do Todoist.
```

## 12. Braki w zrodlach i rzeczy niezweryfikowane

### 12.1 [BRAK W ZRODLACH - do decyzji albo do pomiaru]

| Nr | Czego nie ma | Gdzie rozstrzygamy |
|---|---|---|
| 1 | Format raportu MillBox: uklad pol, HTML czy PDF, czy wspolczynnik jest jeden, jak nazywa pliki STL | D1 (potrzebne raporty) |
| 2 | Struktura firmowego Excela poza kolumnami A, B, C, H: nazwa pliku i arkusza, kolumny D-G i I, zachowanie COM przy pliku z SharePointa | D2 |
| 3 | Eksport skanera: struktura folderu zlecenia, nazwa i format pliku, czy zapis jest samoczynny, czy jedno zlecenie obsluzy wiele skanow, plaszczyzna ciecia | B1, B2 |
| 4 | Ktore okno ma fokus przy Spacji i jak nasz program dowiaduje sie o starcie skanu | DW5, B2 |
| 5 | Kto jest operatorem ("kto zatwierdzil") | DW3 |
| 6 | Jak wiazac skan z plytka, gdy numeru nie widac na skanie (kwadrat w polu fi 100) | Z3, B1 |
| 7 | Reguly ponownego skanu plytki | Z4 |
| 8 | Forma i adresat listy "do dofrezowania" | Z6 |
| 9 | Kto i kiedy uruchamia nocne odswiezenie puli; czy laptop jest wlaczony w nocy | Z5 |
| 10 | Rzeczywista liczba prac i zlecen dziennie, liczba STL w folderze z 4 dni | D3 |
| 11 | Transport i pola komunikatow ramki | DW8, sekcja 3.6 |
| 12 | Skad ramka bierze uklad gniazd dla starych plytek; wyglad marginesu matrycy (czcionka, miejsce numeru, ikona Wi-Fi, kolory stanow) | DW9; A8 i G2 |
| 13 | Firmowe Wi-Fi: adresy, izolacja urzadzen, nazwy `.local` | C1 |
| 14 | Firmowy laptop: uprawnienia administratora, antywirus i polityki uruchamiania, dostep do internetu, konfiguracja OneDrive i Excela | D4, G3 |
| 15 | Jak dlugo trzymac skany; kopia zapasowa bazy | DW4, A11 |
| 16 | Czy kazdy STL w folderze zlecenia jest punktem pracy (pliki dodatkowe, waxupy) | D3, A6 |
| 17 | Nazwy dla dwoch znaczen slowa "poprawka" na ekranie i ramce | Z9, G1 |
| 18 | Jak nazwa STL z raportu MillBox ma sie do nazwy pliku w folderze "Cyrkon" | D1 |
| 19 | Czasy na laptopie stanowiska (dotychczasowe pomiary sa z PC wlasciciela) | D4 |
| 20 | Ekran progow (U4): co technik moze zmieniac | Z7 |

### 12.2 Czego nie udalo sie zweryfikowac

1. Zakres i listy plikow paczek w toku (P1-P4, rozpoznawanie ukladu, "Dzien skanera"): trzy rownolegle katalogi
   robocze (`czesc-a`, `czesc-b`, `czesc-c`) byly w chwili rozpoznania bez zmian. Nie wiem, czy "Dzien skanera"
   obejmuje silnik w osobnym procesie albo obserwacje folderu - A2 i A3 sprawdzaja to w etapie 0.
2. Liczba 252 testow i wszystkie liczby jakosci pochodza z raportow (R59, P3a); niczego nie uruchamialem.
3. "Schemat zatwierdzony przez wlasciciela" w `qc/catalog/baza.py` (H) to zdanie z komentarza w kodzie; zapisu tej
   decyzji nie znalazlem. Nie wiem tez, dlaczego linia `qc/` zostala 03.11 zastapiona w calosci wersja z PC i czy jej
   kod (parser nazw, pule, metryki) byl gdziekolwiek uzywany na prawdziwych danych.
4. F2 lezy poza gitem (glowny katalog); czytalem stan z 15.11.
5. Szacunki bez pomiaru: rozmiar puli (250-800), czas i pamiec przy duzej puli, rozmiar paczki ZIP wydania, 0,5-1 GB
   skanow dziennie (z rozmiaru skanow sztucznych 45-55 MB).
6. [usunieto w kopii: opis dostepu ssh]
   nazwy `.local`.
7. Czy R59 zostanie scalone przed startem etapu 3 i czy `origin/main` nie zmieni sie przez paczki w toku.
8. Sekcje PW cytuje z pliku `.md` w galezi R59 (po poprawkach z 15.11); wersji PDF nie czytalem.
9. Dokumentow "Zakupy i druk", `protokol_weryfikacji_v2.md` i wiekszosci `plan_ramki_v2.md` (poza sekcjami 1, D5, D7,
   D11, D15, 8, 9) nie czytalem - zgodnie z zakresem zlecenia.

## 13. Zadania czlowieka przed startem (wplywaja na sciezke krytyczna)

| Nr | Zadanie | Po co |
|---|---|---|
| 1 | Odpowiedziec na G0: co najmniej DW1, DW2, DW3 (najlepiej wszystkie 12) i ewentualne zmiany zalozen Z1-Z10 | start A1 |
| 2 | Doprowadzic do scalenia R59 do `main` | start wszystkich paczek |
| 3 | Skopiowac 10 prawdziwych raportow MillBox (HTML albo PDF) na PC do katalogu wskazanego przez koordynatora | D1 - pula wieczorna bez wpisywania wspolczynnikow |
| 4 | Przygotowac kopie pliku Excela produkcyjnego i wskazac komputer z Excelem, na ktorym mozna ja otworzyc | D2 |
| 5 | Zapisac, ile folderow i plikow STL przybywa w "Cyrkon" w ciagu 4 dni roboczych (sama liczba) | rozmiar puli, kryteria A5 |
| 6 | Zapytac o firmowe Wi-Fi (czy urzadzenia w sieci widza sie nawzajem) i o uprawnienia na laptopie stanowiska | C1, G3 |
| 7 | Potwierdzic modele i effort koordynatora, wykonawcow i recenzentow dla paczek etapu 3 | prompty z sekcji 11 |
