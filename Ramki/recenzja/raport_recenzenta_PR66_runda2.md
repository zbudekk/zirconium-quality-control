# Raport recenzenta - paczka E3-D1 (dokument dnia testu 28.11, laptop i skaner), PR #66, runda 2

- Data: 26.11.2026 (05:00-05:30), recenzent: konto 3 na PC (zlecenie `rec-d1-r2`), tor ciezkich krokow 4.
- Zakres: commity `90ad932..origin/e3/d1` (HEAD `e08c311`, 3 commity: 475478d, 86a4808, e08c311; 6 plikow) oraz katalog
  `<PC-katalog>\konto3\DLA_WLASCICIELA_2026-11-28\` (2 x PDF, 2 x HTML, `CZYTAJ.txt`, `Pokaz_na_danych_probnych.cmd`,
  `narzedzia_dnia\`).
- Miara: zlecenie poprawek `<PC-katalog>\konto3\zlecenia\d1-r2.md` (decyzje koordynatora: dokument samowystarczalny,
  6 + 2 strony, 2.4 i 2.5a obowiazkowe, `narzedzia_dnia`, plan B na danych probnych) i uwagi P1-P5 rundy 1.
- Metoda: dokument czytany sam (bez starego), jak wlasciciel z 2 wydrukami, pendrive'em i laptopem bez Pythona. Proby na
  mojej instalacji z `Stanowisko_0.3.9-rc2.zip` z rundy 1 (`robocze\rec-d1-r1\proba`), dwa procesy odlaczone z przynet
  `robocze\rec-d1-r2\przyneta\proba.cmd` i `proba2.cmd` przez `ciezki.ps1 -Tor 4` (05:09:22-05:11:52 i 05:12:40-05:13:09),
  PATH tylko katalogi Windows, Qt offscreen. Napisy okien z drzewa widzetow (JSON + PNG w `robocze\rec-d1-r2\logi\`),
  skrypty w `robocze\rec-d1-r2\skrypty\`. Kod programu czytany tylko po to, zeby sprawdzic zdania dokumentu. Raport wykonawcy
  (sekcja "Runda 2") przeczytany na koncu.
- Uruchomiono: prawdziwy `Pokaz_na_danych_probnych.cmd` (kopia z katalogu wlasciciela) + migawki danych instalacji przed / po,
  program `--atrapa` w procesie z klikaniem sciezki C6 (2 przebiegi), zwykly start po pokazie (start bez konsoli jak ikona
  i w procesie), `pole_skanu.cmd` z kopii `narzedzia_dnia` (bez pliku, karton, syntetyczny skan plytki nr 8), QtPdf na
  2 PDF (strony, tekst), porownanie PDF / HTML z MD, kontrola cytatow, T13, ASCII / konce linii, dane osobowe.

## 0. Werdykt

**Do scalenia po poprawkach.** B 0 / P 1 / D 3.

Uwagi P rundy 1: zamkniete 5 z 5 (dowody w p. 1a). Dokument czytany sam wystarcza na caly dzien: 0 odeslan do tresci
starego dokumentu, narzedzie `pole_skanu.cmd` dziala z `narzedzia_dnia` na laptopie bez Pythona, pokaz na danych probnych
startuje, nie zostawia danych w bazie ani w folderach pracy, a zwykla ikona startuje po nim normalnie. Jedyna uwaga P (15)
dotyczy opisu planu B przed szefem: wskazana "Plytka 1" ma czerwone gniazdo z juz zapisana decyzja, wiec ekran wyglada
inaczej niz punkt 2, do ktorego dokument odsyla (przycisk "Ukruszona" jest szary).

## 1a. Uwagi P rundy 1 - stan

| Nr | Stan | Dowod |
|---|---|---|
| P1 (folder `testy_sprzet` / `pole_skanu.cmd` nie do zdobycia) | zamknieta | `DLA_WLASCICIELA_2026-11-28\narzedzia_dnia\pole_skanu.cmd` i `.py` = pliki z `origin/e3/d1` (cmp, 0 roznic); A2 (DZIEN:27-37) i `CZYTAJ.txt` mowia, skad wziac i ze na laptopie ma byc `C:\Sprzet_testy\narzedzia_dnia`. Moja proba z kopii (`laptop\Sprzet_testy\narzedzia_dnia`, PATH bez Pythona): bez pliku kod 1 + "Przeciagnij plik skanu plytki (STL) na ten plik."; karton kod 3 w 2,3 s; plytka nr 8 kod 0 w 6,5 s; 5 plikow wyniku w `laptop\Sprzet_testy\wyniki\pole_skanu` (D2 "C:\Sprzet_testy\wyniki" - zgodne) |
| P2 (odeslania do starego dokumentu; 2.4 / 2.5a "gdy jest czas") | zamknieta | odeslania do tresci starego dokumentu: 0 (zostaje tylko zdanie "nie trzeba drukowac" i numery w nawiasach, DZIEN:3-4); B2 = 2.3 z procedura skanow A/B, B3 = 2.4 (karton + narzedzie), B5 = 2.5a (i)-(iii) + kwadratowa - "obowiazkowo"; tresc zgodna ze starym dokumentem (porownanie krokow 2.3, 2.4, 2.5a: ciecie A/B, karton > 15 x 15 cm, numer "SAM ENTER", "okragla testowa (poza ramka)" + "stary rozstaw R54", 30 minut) |
| P3 (tabela "Ten sam projekt w dwoch gniazdach") | zamknieta | DZIEN:172: najpierw sprawdzic na plytce, przy roznych pracach zdjecie + oba gniazda do arkusza, potem "Zamknij"; tytul i tresc zgodne z `statusy.py:399-400` paczki ("Ten sam projekt w dwoch gniazdach", "... sprawdz, ktora praca jest ktora."); arkusz B6 ma wiersz |
| P4 (pola wymagane okna "Dzien skanera") | zamknieta | akapit "Pola z gwiazdka" (DZIEN:81-86), B1 "Folder zapisu zlecen ...", B2, tabela B4, B8 "nie wpisano: ..." -> "Nie"; porownanie z `dzien_skanera_kroki.toml` paczki: wszystkie `wymagane_pola` krokow wymaganych sa w dokumencie (krok 2 `folder_zapisu`, 5 `numer_plytki`, 6 `numer_plytki` / `wspolczynnik` / `czas_skanu`, 9 `gniazda_ukruszone`, 11 `gniazda_z_pracami`; krok 12 opcjonalny: `rodzaj_plytki`, `numer_plytki`); etykiety pol zgodne; tekst braku "nie wpisano: <etykieta>" (`dzien_skanera_rdzen.py:535`); arkusz B4 ma kolumne "wspolczynnik" |
| P5 (brak planu, gdy skan nie da mapy) | zamknieta (z nowa uwaga 15 o opisie) | C6 + A6 + `Pokaz_na_danych_probnych.cmd`. Prawdziwy plik z kopii: kod 0 od razu, po 15 s 3 procesy instalacji (`pythonw` start bez konsoli, `python` bazowy, `python` venv), po 60 s 0; folder TEMP `qc_atrapa_0ymw4nz8` byl po 15 s, po 60 s go nie ma. Migawka przed / po (sha256 kazdego pliku `proba` bez `wersje`/`python` + foldery skanow i projektow, liczby wierszy tabel bazy): 36 -> 37 plikow, nowy tylko `dane\ostatni_start_stanowisko.txt` (82 B, dziennik startu), zmienionych 0, baza 11 tabel / 8 wierszy bez zmian. Po pokazie zwykly start (start bez konsoli jak ikona) kod 0; w oknie wlasna plytka instalacji, "Kto teraz pracuje?" + "Tester", "plikow projektow: 3" - bez sladu danych probnych |

## 1b. Nowe uwagi (tylko w czesciach zmienionych)

Plik `DZIEN` = `Ramki/etap3/testy_sprzet_2026-11-28/DZIEN_TESTU_LAPTOP_I_SKANER.md`, `ARKUSZ` = `ARKUSZ_LAPTOP_I_SKANER.md` tego
katalogu (oba na `e08c311`).

| Nr | Waga | Plik:linia | Scenariusz | Propozycja |
|---|---|---|---|---|
| 15 | P | DZIEN:214-216 (C6) | Plan B przed szefem: "Kliknij kafelek 'Plytka 1' (ma prace czerwona 'UBYTEK') i dalej punkty 2-5 jak wyzej". W danych probnych jedyne czerwone gniazdo plytki 1 (gniazdo 2) ma juz zapisana decyzje (`kontroler_api.scenariusz_pokazowy`: `ukruszona(gniazdo 2)`, `ok(gniazdo 9)`). Moja proba (klik kafelka, klik gniazda 2): po prawej "UKRUSZONA", "Oznaczona jako ukruszona - jest na liscie 'do dofrezowania'.", "Decyzja: Ukruszona - Technik A, 05:10", przycisk "Ukruszona [U]" WYLACZONY; w legendzie mapy nie ma "UBYTEK" (jest "UKRUSZONA 1", "OK - zatwierdzona 1"); na gorze komunikat "Plytka 1, skan z ...: Praca niesprawdzona" / "Gniazdo 7: kontrola zakonczyla sie bledem programu ...". Punkt 2 mowi "UBYTEK", "kliknij 'Ukruszona'", "Decyzja: Ukruszona - Tester" - wlasciciel przy szefie klika szary przycisk i nie wie, co dalej. Wykonawca tej sciezki nie klikal (raport, "Odstepstwo"). | W C6 zamiast "dalej punkty 2-5 jak wyzej": "Kliknij czerwone gniazdo 2: po prawej 'UKRUSZONA' i 'Decyzja: Ukruszona - Technik A, ...' (decyzja jest juz w danych probnych, 'Ukruszona' jest szare). Pokaz 'Cofnij decyzje' (C): wraca 'UBYTEK', 'Brak decyzji dla tej pracy', 'Do dofrezowania: 0'; potem 'Ukruszona' (U): 'Do dofrezowania: 1'. Dalej punkty 3 i 5 jak wyzej." - te stany sprawdzilem (przebieg 2: Cofnij wlaczony, po nim 0, po "Ukruszona" 1). |
| 16 | D | DZIEN:139, 145-147 (B4 krok 12, B5) | Okno "Dzien skanera" podaje do oceny pliku numer z pola "Numer plytki" kroku (`_numer_z_pola` -> `--numer`), a numer 8 istnieje tylko w ukladach okraglych - podany numer wybiera uklad (`plate.rozpoznaj_uklad`, "numer_podany"). B5 kaze wpisac w kroku 12 `8`, potem "Gdy jest kwadratowa - jeden skan pustej" w tym samym kroku: okno oceni kwadratowa jako plytke okragla nr 8. Kolumna arkusza B5 "ocena w oknie" dla (i)-(iii) tez jest z podpowiedzia (pomiar B5 robi narzedzie z "SAM ENTER", wiec dane nie gina). | B5: "Przed skanem kwadratowej wpisz w 'Numer plytki' jej numer (okno podaje ten numer programowi)". |
| 17 | D | DZIEN:120-122 (B3 p. 1) | Karton idzie do kroku 12 okna; okno oceni go na czerwono (plik bez stozkow - jak model w mojej probie r1: "TEN SKAN SIE NIE NADA, bo na plytce nie widac trzech stozkow ..."), a tabela B2 mowi przy czerwonej ocenie "zrob to, co po 'ZROB TAK'". Dokument nie mowi, ze czerwien kartonu w oknie jest w porzadku (wykonawca przyjal to domyslnie w raporcie). | B3 p. 1: "W oknie karton dostanie czerwona ocene - to dobrze, nic nie poprawiaj." |
| 18 | D | ARKUSZ:32-36, 49-56 | Kolumna "program mowi" tabeli B3 jest ostatnia i na wydruku ma ok. 2,5 cm (obraz strony 1), a wiersz narzedzia to np. "PLYTKA NIE ROZPOZNANA (powod wg programu: malo_stozkow)"; naglowek tabeli B5 jest na stronie 1, wiersze na stronie 2. | Kolumne "program mowi" przeniesc pod tabele jako osobne linie albo skrocic inne kolumny; tabele B5 nie dzielic miedzy stronami. |

## 2. Wlasne proby

| # | Polecenie / proba | Wynik |
|---|---|---|
| 1 | `migawka.py` (sha256 plikow instalacji bez `wersje` i `python`, folderow skanow i projektow; liczby wierszy tabel `stanowisko.sqlite`; TEMP `qc_atrapa_*`) przed pokazem, po pokazie z pliku, po pokazie w procesie, po zwyklym starcie | m1 -> m2: 36 -> 37 plikow, 1 nowy (`dane\ostatni_start_stanowisko.txt`, 82 B), 0 zmienionych, tabele 11 / wierszy 8 -> 8; m2 -> m3: 0 roznic; m3 -> m4 (zwykly start): zmienione `stanowisko.log`, `ostatni_start_stanowisko.txt`, baza (`zdarzenia` 7 -> 11) - zwykla praca programu |
| 2 | `cmd /c "<pulpit>\Pokaz_na_danych_probnych.cmd" --zamknij-po 40 < nul` (kopia z katalogu wlasciciela; `--zamknij-po` tylko w probie; `STANOWISKO_KATALOG` na moja instalacje) | kod 0 od razu; po 15 s 3 procesy z instalacji (pythonw + 2 x python, start 05:09:25), po 60 s 0; TEMP: przed 1 cudzy folder, po 15 s +1 (`qc_atrapa_0ymw4nz8`), po 60 s znow tylko cudzy; dziennik startu: "stanowisko --atrapa --zamknij-po 40", bez bledow |
| 3 | `rec_pokaz.py` - `aplikacja.main(["--ustawienia", <instalacja>\ustawienia.toml, "--atrapa"])` (te same argumenty co plik pokazu), 9 stanow, na koncu `okno.close()` jak krzyzyk | 93 napisy na starcie: "Plytki tej zmiany", "5", kafelki "Plytka bez numeru", "Plytka 4", "Plytka 3", "Plytka 2", "Plytka 1" (z "UBYTEK 1"), "Technik A", "Podaj numer plytki - skan z 05:10", "Program nie odczytal numeru plytki ze skanu. ...", "Pozniej", "Do dofrezowania: 1", pasek "dostepny", "nic nie czeka", "plikow projektow: 16", "wylaczone", "wersja 0.3.9-rc2" - zgodne z A6 / C6; "Pozniej" -> "Brak pytan i komunikatow."; Plytka 1 gniazdo 2 - patrz uwaga 15; Plytka 3 gniazdo 4: "Decyzji nie mozna teraz zapisac - plytka do ponownego skanu."; "Poranek" -> "Jeszcze nie ma pieca - zeskanuj pierwsza plytke poranna (piec otworzy sie sam).", "Rozkladanie kuwet", "Kompletne i braki"; "Wieczor" wraca; po zamknieciu kod 0, katalog atrapy usuniety |
| 4 | `rec_pokaz2.py` (przebieg 2): Plytka 1 gniazdo 2 -> "Cofnij decyzje" -> "Ukruszona"; "Plytka bez numeru" gniazdo 2 -> "Ukruszona" | przed: "Ukruszona [U]" wylaczony, "Cofnij decyzje [C]" wlaczony; po cofnieciu "UBYTEK", "Brak decyzji dla tej pracy", "Do dofrezowania: 0"; po "Ukruszona" "UKRUSZONA", "Decyzja: Ukruszona - Technik A, 05:13", "Do dofrezowania: 1"; "Plytka bez numeru" gniazdo 2: "Ukruszona" wlaczony, po nim "Do dofrezowania: 2" (w liscie "Plytka" = "-"); katalog atrapy usuniety |
| 5 | zwykly start po pokazie: `python.exe -I -B start_bez_konsoli.pyw stanowisko --zamknij-po 25` (jak ikona, python zamiast pythonw - kod wyjscia), potem `rec_program.py` w procesie | kod 0; 53 napisy: "Plytka bez numeru" 04:25 "analiza nie powiodla sie" (skan z rundy 1), "Kto teraz pracuje?", "Tester", "plikow projektow: 3", "Do dofrezowania: 0" - zadnych danych probnych; klik "Tester" -> "Tester", "Zmien" |
| 6 | `pole_skanu.cmd` z kopii `narzedzia_dnia` bez pliku (`cmd /c ... < nul`) | kod 1, "Przeciagnij plik skanu plytki (STL) na ten plik." + pauza |
| 7 | jak przeciagniecie: `cmd /c ""...\pole_skanu.cmd" "...\karton.stl""`, odpowiedzi: Enter, `karton` (plaski arkusz 150 x 150 mm, 45 000 trojkatow, `syntetyczne.py`) | kod 3 w 2,3 s: "1. Program mowi: PLYTKA NIE ROZPOZNANA.", "DANE NIE SA KOLEM: 150,0 x 150,0 mm. Do arkusza wpisz OBIE liczby ...", "Dane sa PLASKIE: ...", "DO ARKUSZA (przepisz):", "Zapisano: ...\narzedzia_dnia\..\wyniki\pole_skanu\karton_..._pole.txt"; obie pytania jak w B3 ("Numer wybity na plytce, cyfra 1-9 (sam Enter = nie wiem):", "Co lezy na stoliku? Np. ...") |
| 8 | to samo z syntetycznym skanem z gory plytki okraglej R54 nr 8 (`synth.siatka_plytki` + `widok_z_gory`), opis `okr-test 8, pusta` | kod 0 w 6,5 s: "program mowi: okragla testowa (poza ramka), wieczorna, stary rozstaw R54 [okragla_wieczorna_r54], PEWNIE", "numer z dolkow: 8" - napisy B5 "Dobrze: ..." zgodne |
| 9 | (przebieg 1) pole_skanu z plikiem przez `cmd /c "<cmd>" "<plik>"` | kod 1 "Nazwa pliku ... jest niepoprawna" - blad mojego wywolania (cudzyslowy `cmd /c`), nie narzedzia; powtorzone poprawnie w p. 7-8 |
| 10 | `pdf_tekst.py` (QtPdf) na 2 PDF z katalogu wlasciciela | DZIEN 5 stron, ARKUSZ 2 strony, kazda 595 x 842 pt (A4); metadane: tytul, Chrome bez okna, autor pusty; obrazy stron 3 DZIEN i 1 ARKUSZ obejrzane - czytelne (patrz uwaga 18) |
| 11 | tekst PDF / HTML wobec MD (ciag slow) | PDF: 3365 = 3365 i 557 = 557 slow, zgodnosc 1,0; HTML: arkusz 557 = 557, dokument 3351 z 3365 (14 roznic = numery list zamienione na liste HTML) |
| 12 | `cytaty_r2.py` - cytaty "..." dokumentu (pary cudzyslowow takze przez koniec linii) nowe / zmienione wobec 90ad932 | 158 cytatow, 48 nowych / zmienionych: 41 w zrzutach i wydrukach narzedzia z moich prob (r1 + r2), 7 tylko w plikach napisow paczki / `narzedzia_dnia` ("Skan dobry", "Dane mieszcza sie w kole o srednicy ok. ... mm", "UWAGA: w skanie jest prawdopodobnie PODLOZE", "Uwaga", "nie odczytany", "... sprawdz, ktora praca jest ktora", "Sesja spakowana"), nie znalezionych 0. Niezgodnosci tresci cytatow: 0; niezgodnosc stanu ekranu: uwaga 15 |
| 13 | `dzien_skanera_kroki.toml` paczki wobec B1-B5 (ile plikow, pola, wymagane) | krok 2: 4 zrzuty, krok 4: 2 (zgodne z B1); pola i wymagane - p. 1a P4; krok 12 `ile_plikow = 1` to minimum (`dzien_skanera_rdzen.py:528`), wiec kilka plikow w kroku 12 nie robi braku |
| 14 | T13: `t13_higiena.py --repo <PC-katalog>\qc --od 90ad932 --do origin/e3/d1` i `--od origin/e3/r1` (kopia skryptu z galezi) | oba "WYNIK T13: ZAL (0 naruszen)" |
| 15 | ASCII i konce linii z blobow `e08c311` | 6 plikow: 0 linii spoza ASCII; `.md` 0 bajtow CR; `Pokaz_na_danych_probnych.cmd` 32 CR na 32 linie (CRLF); kopia w repo = plik w katalogu wlasciciela (cmp) |
| 16 | `Ramki/recenzja/raport_recenzenta_PR66_runda1.md` wobec mojego raportu rundy 1 | identyczne (cmp) |
| 17 | dane osobowe: grep diffu, HTML, PDF, `CZYTAJ.txt`, pliku pokazu | nazwisk, e-maili, nazw zlecen, sciezek kont: 0 |
| 18 | program ochronny | przynety 2 z 2 na miejscu po obu przebiegach, sesja nie zabita, `ciezkie.log`: oba przebiegi kod 0 |

## 3. Kryteria zlecenia d1-r2

| Nr | Kryterium | Ocena |
|---|---|---|
| D-1 | dokument samowystarczalny, druk tylko 2 plikow, limit 6 + 2 strony | potwierdzone wlasna proba: 0 odeslan do tresci starego dokumentu, 5 + 2 strony A4 |
| D-2 | 2.4 i 2.5a obowiazkowe | potwierdzone przegladem (B3, B5 "obowiazkowo"; arkusz B3, B5) |
| D-3 | `narzedzia_dnia` w katalogu wlasciciela, bez testow i `ramka*`; dziala po dwukliku bez Pythona w PATH | potwierdzone wlasna proba (2 pliki = repo; p. 6-8) |
| D-4 | plan B: plik pokazu, kiedy go uzyc, co widac doslownie, zdanie dla szefa, powrot; dane nie trafiaja do bazy / folderow | potwierdzone wlasna proba z odstepstwem: plik, zdanie, powrot i brak danych - tak (p. 1-5); "co widac" dla Plytki 1 niezgodne ze stanem ekranu (uwaga 15) |
| 1 | kopia raportu r1 bez zmian tresci | potwierdzone (cmp) |
| 2 | P1-P5 poprawione (P3 i P4 wg zlecenia) | potwierdzone: 5 z 5 zamkniete (p. 1a) |
| 3 | D tanie zrobione, reszta z powodem; ramka "Zapytaj przed sobota" (do 3 pytan z odpowiedzia domyslna) | potwierdzone przegladem: D6-D14 wykonane wg mojego odczytu dokumentu (9 z 9); ramka: 3 pytania, kazde z odpowiedzia domyslna |
| 4 | kazdy nowy / zmieniony cytat sprawdzony na 0.3.9-rc2, niezgodnosci 0 | potwierdzone wlasna proba dla tresci (48 z 48); wg wykonawcy 183 z 183 (inny sposob liczenia, niesprawdzone) |
| 5 | katalog wlasciciela: 2 PDF, 2 HTML, `CZYTAJ.txt` (co wydrukowac, gdzie paczka, co na pendrive), strony w raporcie; T13 | potwierdzone (zawartosc, 5 + 2 strony, `CZYTAJ.txt` 3 punkty pendrive'a; T13 0 naruszen) |
| 6 | raport "Runda 2", push, PR roboczy | potwierdzone przegladem (sekcja jest; `origin/e3/d1` = `e08c311`); PR #66 w wersji roboczej - wg wykonawcy, `gh` nie sprawdzalem |

## 4. Zakres plikow i zasady

- Zmienione w rundzie: `DZIEN_TESTU_LAPTOP_I_SKANER.md`, `ARKUSZ_LAPTOP_I_SKANER.md`, `README.md`, nowy
  `Pokaz_na_danych_probnych.cmd` (wszystkie w `Ramki/etap3/testy_sprzet_2026-11-28/`, dozwolone przez d1.md p. 6), raport
  `Ramki/stanowisko/raporty/E3-D1_2026-11-26.md` i zlecona kopia `Ramki/recenzja/raport_recenzenta_PR66_runda1.md`.
  `narzedzia/`, kod programu, pliki nietykalne - 0 zmian.
- ASCII, LF dla `.md`, CRLF dla `.cmd` - zgodne; 3 commity z przedrostkiem `E3-D1 r2:` i stopka Opus 5.5; duzych danych 0;
  danych osobowych 0.

## 5. Do decyzji wlasciciela

Brak nowych. Trzy sprawy z rundy 1 sa w dokumencie w ramce "Zapytaj przed sobota" z odpowiedziami domyslnymi.
