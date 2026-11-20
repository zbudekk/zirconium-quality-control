# Raport recenzenta - PR #40 (E3-A11d: instrukcje dla technika, tabela "co robic, gdy nie dziala", zestaw proby T14) - runda 2

Data: 20-21.11.2026. Zakres: `git -C <PC-katalog>\qc diff main origin/e3/a11d` (main 2d1e010, HEAD 6e75c6c); zakres
przyrostowy rundy 2: wlasne commity po c0c38e7 (3cfa1c4, 4b0abea, f720c40, 94960b8, 6e75c6c - 5 commitow bez scalen).
Kopia do prob: `<PC-katalog>\qc-wt\rec-a11d` (detached 6e75c6c; stan po probach - proba 12).
Pliki robocze: `<PC-katalog>\koordynator\robocze\rec-a11d\runda2\` (`druk2.py`, `proby2.py`, `proby3.py`, `mutacje2.py`,
logi `*.log`, wydruki `pdf\`, obrazki `z_html\`, zrzuty `proby_png\`, klon z `git archive` w `klon\`).

Metoda: (1) przeczytane zdanie po zdaniu 4 strony `.md` i 3 pliki T14, porownane z kodem (`statusy.py`, `ui/napisy*.py`,
`kontroler_api.py`, `samokontrola.py`, `instalacja/instalator.py`, wzory `.cmd`); (2) okno programu bez ekranu (Qt offscreen,
atrapa kontrolera) na kodzie 6e75c6c: B1 w 3 wariantach, P1, P2, pytanie przed "Zamknij piec"; (3) druk 5 stron `.html` do
PDF (Chrome `--headless=new --print-to-pdf`), liczba stron 2 sposobami, obraz 150 dpi obejrzany; (4) 9 z 9 obrazkow
wydobytych z `.html` obejrzanych; (5) 12 wstrzykniec + 7 dodatkowych + 6 prob kruchosci testu zrodel; (6) `--sprawdz` T14
z czystego `git archive`; (7) raport wykonawcy (sekcja 14) czytany na koncu. Pelnego pytest nie powtarzano.

Czego NIE sprawdzilem: okna na prawdziwym ekranie, druku na papierze, instalatora i `Polecenie.cmd` na programie
zainstalowanym z paczki (czytalem kod i wzory), ramek, Excela, rozmiarow okna z D8 (liczby wykonawcy), komunikatu
"Baza jest zajeta" po poleceniach Excela na oknie (tylko przeglad kodu - D12).

## 0. Werdykt

**Do scalenia.** B 0, P 0, D 7 (nowe D12-D17 i otwarta D7 rundy 1; D11 rundy 1 zamknieta czesciowo).

B1 i P1-P5 rundy 1 sa zamkniete - kazda potwierdzona wlasna proba na programie koncowym. Cztery strony opisuja to, co program
pokazuje po paczkach P14, A11s, A11i, A11w: kazdy cytowany napis istnieje, kolejnosc krokow jest wykonalna, zadna rada nie
kaze kasowac ani nadpisywac danych, a wiersze o decyzji niezapisanej, samokontroli i instalatorze kieruja do telefonu tam,
gdzie technik nie powinien dzialac sam. Uwagi D mozna poprawic przy okazji (tresc poprawek podana doslownie).

## 1. Uwagi

### 1.1 Uwagi B i P rundy 1 - stan

| Nr | Stan | Dowod (wlasna proba) |
|----|------|----------------------|
| B1 | zamknieta | `co_robic_gdy_nie_dziala.md:14-15` rozdziela wynik skanu ("Baza jest zajeta", program ponawia sam) i decyzje ("Decyzja NIE zostala zapisana", "Polecenie NIE zostalo wykonane - baza zajeta": "Kliknij "Ponow teraz"", sprawdz podpis gniazda i liste). Proba `proby2.py b1`: klik "Ukruszona" przy bazie zajetej obcym `BEGIN EXCLUSIVE` - okno wraca po 0,7 s (runda 1: 14,9 s), komunikat "Decyzja NIE zostala zapisana" z przyciskami "Ponow teraz" i "Rezygnuje - nie zapisuj" (bez "Zamknij"), gniazdo "UBYTEK", "Do dofrezowania: 0". "Ponow teraz" przy nadal zajetej bazie: komunikat zostaje. Po zwolnieniu bazy bez klikniecia (2,5 s): decyzji nadal nie ma. "Ponow teraz": gniazdo "UKRUSZONA", "Do dofrezowania: 1", komunikat znika. "Rezygnuje - nie zapisuj": "UBYTEK", lista 0. Zamkniecie programu z wiszacym komunikatem i ponowny start: decyzji nie ma i komunikatu nie ma - instrukcja mowi o tym w zdaniu wstepnym (`:3` "wyjatek: komunikat z przyciskiem "Ponow teraz""). "Zamknij piec" przy zajetej bazie (`proby3.py`): "Polecenie NIE zostalo wykonane - baza zajeta" z tymi samymi przyciskami. |
| P1 | zamknieta | `wieczor.md:38-41`. Proba `proby2.py p1` (2 decyzje z 4, skan plytki 2): naglowek zostaje "Plytka 1 - do obejrzenia: 2"; w lewej kolumnie, nad kafelkami plytek, przycisk "Pokaz nowy wynik: / Plytka 2" (y 143 px), pod nim zolte pole "Nowy wynik czeka: Plytka 2" (y 201 px); komunikat "Skan do powtorzenia" niewidoczny do klikniecia przycisku, po kliknieciu widoczny; pytanie o ponowny skan: naglowek "Plytka 2 - nowy skan, czeka na odpowiedz". Zrzut `proby_png\p1_nowy_wynik.png` obejrzany - zgodny z opisem. `jedna_strona.md:14`: zdanie "pojawi sie sama" usuniete ("Po chwili plytka jest na liscie z lewej" - prawda). |
| P2 | zamknieta | `wieczor.md:31-32`. Proba `proby2.py p2`: drugi start na tej samej bazie po przelaczeniu trybu - pasek "Tryb: Poranek", obok przycisk "-> Wieczor"; klikniecie przelacza na wieczor (przycisk zmienia sie na "-> Poranek"), pasek "Folder projektow: plikow projektow: 16". |
| P3 | zamknieta | `rano_excel.png` (wydobyty z `poranek.html`, 794 x 510, 44 878 B) obejrzany: brak wiersza o `ustawienia.toml`; pod tytulem jedno zdanie "Kolor pola B zmienia sie dopiero po "Zatwierdz" (tryb "pytaj")"; przycisk "Zatwierdz wiersz 9" czytelny. |
| P4 | zamknieta | 12 z 12 wstrzykniec wykrytych (8 z rundy 1, w tym M1, M4, M7 niewykrywane w rundzie 1, + 4 nowe) - sekcja 2, proba 9. |
| P5 | zamknieta | Obrazki kartki (obejrzane): wieczor - gniazda czerwone 2 i 9, zolte 7, szare 4; rano - plytki 4 i 5, kuwety 3221, 3228, 3235, 3242, kandydaci 3221 / 3256 na plytce 4 gniazdo 3. Proba (`scenariusz_t14.json`, log `--sprawdz`): wieczor - czerwone 3 i 11, zolte 6, szare 15, popraw ulozenie w gniezdzie 4; rano - plytki 6 i 5, zolte gniazdo 7 plytki 6, kuwety 3277, 3284, 3291, 3298, 3305, kandydaci 3291 / 3312. Zbiory kuwet rozlaczne; tekst kartki nie wymienia zadnej kuwety proby ("Kuweta 3228", "Braki w tym piecu: 1" z "np."). |

### 1.2 Uwagi nowe (wszystkie D - mozna scalic bez poprawki)

| Nr | Waga | Plik:linia | Scenariusz (stan -> co sie dzieje) | Propozycja (stare -> nowe) |
|----|------|-----------|-------------------------------------|----------------------------|
| D12 | D | `instrukcje/co_robic_gdy_nie_dziala.md:14` | Przeglad kodu (nie proba): polecenia bez listy do ponowienia - `excel_zatwierdz`, `excel_pomin` (`kontroler_api.py:3288`, `:3360-3362`) - przy zajetej bazie daja zwykly komunikat "Baza jest zajeta" z trescia "niczego nie zapisano. Sprobuj ponownie za chwile." Wiersz tabeli dla tego tytulu mowi "Poczekaj - zapis wyniku program ponawia sam" - prawda dla wyniku skanu, nie dla kliknietego "Zatwierdz wiersz 9". Skutek maly: wiersz zostaje w oknie Excela jako "do zatwierdzenia", a komunikat sam kaze sprobowac ponownie; danych nie gubi. | Kolumna "Co zrobic": "Poczekaj - zapis wyniku program ponawia sam; mozesz kliknac "Ponow zapis"." -> "Poczekaj - zapis wyniku program ponawia sam; mozesz kliknac "Ponow zapis". Komunikat zaraz po Twoim kliknieciu (np. w oknie Excela): kliknij to samo jeszcze raz." (zmierzyc druk - zapas ok. 5 mm). |
| D13 | D | `instrukcje/co_robic_gdy_nie_dziala.md:26` | Lista nazw w wierszu "`BLAD` innego sprawdzenia" jest zamknieta (10 nazw), a `BLAD` moze dostac kazde sprawdzenie, ktore nie skonczy sie w limicie czasu albo gdy folder danych nie odpowiada (`samokontrola.py:1296-1310`, `opisy_modulow/samokontrola.md:79`: np. `pamiec_puli`, `egzemplarz`). Technik z wierszem `BLAD pamiec_puli` nie znajdzie nazwy ani w wierszu 25, ani 26; sens wiersza ("innego") i tak prowadzi do telefonu. | "`BLAD` innego sprawdzenia: `dane_folder`, ..." -> "`BLAD` kazdego innego sprawdzenia, np. `dane_folder`, ...". |
| D14 | D | `instrukcje/co_robic_gdy_nie_dziala.md:27` | "do tego czasu pracuj na wersji dotychczasowej" - nieprawda w dwoch rzadkich przypadkach instalatora: pierwsza instalacja (`wersja biezaca bez zmian: brak`) i wiersz "UWAGA: wersja biezaca ... jest niekompletna (przerwana naprawa) i program nie wystartuje" (`instalator.py:1467-1469`). Technik trafia wtedy do wiersza "Program nie startuje" (dzwonic od razu) - bez szkody. | "do tego czasu pracuj na wersji dotychczasowej." -> "do tego czasu pracuj na wersji dotychczasowej (gdy `Stanowisko.cmd` jej nie uruchamia - dzwon)." |
| D15 | D | `instrukcje/poranek.md:28` | Krok 1 kaze kliknac "przycisk ze strzalka i napisem "Poranek"" bez warunku. Gdy program wstal juz w trybie "Poranek" (ponowne uruchomienie w trakcie poranka; proba P2), obok trybu jest przycisk "-> Wieczor" - technik idacy za kartka moze przelaczyc na wieczor; skan plytki porannej konczy sie wtedy pytaniem "Plytka nie z tego trybu" (tabela ma wiersz - da sie wrocic). Lustrzane odbicie P2, ale rzadsze. | "W pasku u gory, obok napisu trybu, kliknij przycisk ze strzalka i napisem "Poranek"." -> "W pasku u gory sprawdz tryb. Gdy jest "Wieczor", kliknij obok przycisk ze strzalka i napisem "Poranek"; gdy jest juz "Poranek", niczego nie przelaczaj." |
| D16 | D | `testy/test_instrukcje.py:266-279` (`ZRODLA_CYTATOW`), `narzedzia/instrukcje_html.py:226-234` | Test zrodel pada nie tylko po zmianie napisu, ale tez gdy w `statusy.py` / `ui/` ktos doda napis rowny cytatowi albo przeniesie staly napis do innego pliku `ui/` (proby F3, F4 - sekcja 2). To zamierzone i opisane w tescie; naprawa jednym poleceniem (`--zapisz-zrodla`, proba F6). Dla paczek programu oznacza to obowiazek uruchomienia `test_instrukcje.py` po kazdej zmianie w `ui/`. Ocena dla E3-P15 - sekcja 2.1. | Bez zmiany kodu. W komunikacie asercji (`:276`) dopisac polecenie naprawy: "... po przejrzeniu instrukcji: narzedzia/instrukcje_html.py --zapisz-zrodla". |
| D17 | D | `etap3/t14/README.md:26-29`, `scenariusz_symulatora.md:86-87` | Uruchomienie symulatora przez `C:\Stanowisko\Polecenie.cmd` na programie zainstalowanym z paczki nie bylo wykonane (wykonawca pisze to wprost; ja tez nie). Przegladem: `Polecenie.cmd` przechodzi do `wersje\<n>\program` i uruchamia Pythona wersji z argumentami; paczka zawiera `narzedzia/` (potrzebne `zrzuty_instrukcji.py` dla `--sprawdz`; `zbuduj_wydanie.py:33`); `PYTHONDONTWRITEBYTECODE=1` - katalog programu bez nowych plikow. Krok 3 README sam jest bramka ("Inny wynik = nie zaczynaj proby"). | Bez zmiany. Wykonac przy odbiorze koncowym (sekcja 5 pkt 2). |

### 1.3 Uwagi D rundy 1 - stan

| Nr | Stan | Gdzie |
|----|------|-------|
| D1 | zamknieta | `poranek.md:43-45` (+ proba pytania "Zamknac piec mimo prac bez rozstrzygniecia?") |
| D2 | zamknieta | `poranek.md:20-21` (kolory zgodne ze `statusy.py:78`, `:107`, `:110`) |
| D3 | zamknieta | `wieczor.md:20`, `:61-62` |
| D4 | zamknieta | zmierzone ponownie: 1 strona, ostatni wiersz 12,0 mm nad krawedzia (margines 7 mm, zapas ok. 5 mm) |
| D5 | zamknieta | `co_robic_gdy_nie_dziala.md:28` |
| D6 | zamknieta | `co_robic_gdy_nie_dziala.md:23`, `:21` |
| D7 | otwarta (opisana, decyzja wlasciciela) | obrazki nadal tylko w `.html`; 4 PNG T14 w repo 3 razy |
| D8 | zamknieta | `README.md:19-23`; 4 rozmiary okna - wg wykonawcy, niesprawdzone |
| D9 | zamknieta | log `--sprawdz`: wiersze `osoba: ...`, "kuwety rozlozone przed zamknieciem pieca (wg dziennika): 3277" |
| D10 | zamknieta | 0 trafien `<PC-katalog>` w plikach `etap3/t14`; `jedna_strona.md:40` ma "np." |
| D11 | czesciowo | litery U / O / C sprawdzane (`test_instrukcje.py:296-305`); zdanie bez cudzyslowu nadal niewykrywane (proba X5) |

## 2. Wlasne proby

`PY` = `<PC-katalog>\koordynator\narz\py.cmd`, katalog `rec-a11d\Ramki\stanowisko` (proby okna: klon z `git archive 6e75c6c`).

| Nr | Polecenie (skrot) | Wynik |
|----|-------------------|-------|
| 1 | `PY -m pytest -q -p no:cacheprovider testy/test_instrukcje.py` x 3 | 36 passed x 3 (18,8 s / 27,2 s / 17,2 s), 0 failed |
| 2 | `druk2.py`: Chrome bez okna -> PDF, strony liczone wzorcem `/Type /Page` i QtPdf | wieczor 1 strona (ostatni wiersz 20,5 mm nad krawedzia), poranek 1 (35,4 mm), co_robic 1 (12,0 mm; A4 poziomo), jedna_strona 1 (29,6 mm; A4 poziomo), arkusz_obserwacji 1 (59,9 mm) |
| 3 | obraz stron 150 dpi (Read): co_robic (2 cwiartki z 4), wieczor (dolna polowa), jedna_strona (cala); poranka i gornej polowy wieczoru nie ogladalem jako wydruku (tylko obrazki i `.md`) | nic nie uciete w czesciach obejrzanych; tabela "co robic" pismem 7,3 pt czytelna na obrazie w skali 100 % (cytaty pogrubione, nazwy z okna polecen w ramkach); pismo male - ocena na papierze nalezy do wlasciciela |
| 4 | obrazki wydobyte z `.html` (9 roznych PNG; wieczor 5, poranek 4; jedna_strona 4 = te same bajty co pliki `etap3/t14/obrazki`) | 9 z 9 obejrzanych: program po P14 (przycisk "Czekam na plik skanu [Spacja] / Skanujesz w programie skanera"), dane sztuczne ("Technik A", kuwety 9002 i 32xx, "3221 Fikcja Rano", "Starsza Osoba ..."), zgodne z opisem obok |
| 5 | `proby2.py b1`, `b1r`, `b1x` | B1 - sekcja 1.1 |
| 6 | `proby2.py p1`, `p2`, `zamknij` | P1, P2, D1 - sekcja 1.1; pytanie przed zamknieciem pieca: "Zamknij piec mimo to" / "Wroc do rozstrzygania", po "Wroc" piec otwarty |
| 7 | `proby3.py` (zajeta baza, inne polecenia) | "Zamknij piec": "Polecenie NIE zostalo wykonane - baza zajeta" + "Ponow teraz" / "Rezygnuje - nie zapisuj"; wybor osoby, kolejnosc i wybor kuwety: wykonane mimo zajetej bazy; przelaczenie trybu: komunikat "Polecenie nie zostalo wykonane" (sekcja 6, N4). Wywolania `wybierz_kandydata` i `potwierdz_kuwete` w tej probie mialy zle argumenty - bez wniosku |
| 8 | `git archive 6e75c6c` -> `klon`; `PY symulator_t14.py --sprawdz` | kod 0, "SPRAWDZENIE T14 BEZ EKRANU: zgodne 22 z 22 krokow", 8 s |
| 9 | `mutacje2.py`: 12 wstrzykniec (M1-M8 rundy 1; N1 przycisk P14 "Pokaz nowy wynik:" w `ui/napisy.py`; N2 nazwa sprawdzenia `dane_polozenie` w `samokontrola.py`; N3 "INSTALACJA: WSTRZYMANA" w `instalator.py`; N4 wiersz decyzji w `co_robic` zmieniony na "Poczekaj - program ponawia zapis sam.") | **12 z 12 wykrytych** (test pada) |
| 10 | `mutacje2.py`: dodatkowe X1-X7 | 6 z 7 wykrytych: X1 "Wroc do rozstrzygania", X2 "Ponow teraz", X3 "Nowy wynik czeka", X4 instrukcja "wpisz `tak` i Enter" zamiast `T`, X6 pytanie `[T/N]` w instalatorze, X7 wiersz `SAMOKONTROLA: CZERWONA`. NIE wykryte: X5 - zdanie bez cytatu w `wieczor.md` zmienione na falszywe ("ekran sam przechodzi na nowa plytke") - granica metody (D11) |
| 11 | `mutacje2.py`: kruchosc testu zrodel F1-F6 | F1 (+40 wierszy komentarza w kazdym z 11 plikow `ui/*.py`): test zielony, 36 passed. F2 (nowy napis w `ui/czesci.py`, nierowny zadnemu cytatowi): zielony. F3 (nowy literal "Analiza" w `ui/okno.py` - rowny cytatowi): test pada (1 test: zrodla). F4 (stala `NASTEPNA` przeniesiona z `ui/napisy.py` do nowego pliku `ui/`, tresc bez zmiany): test pada (1 test: zrodla). F5 (ten sam literal "Analiza" dopisany w `kontroler_api.py`, poza plikami ekranu): zielony. F6 (F3 + `instrukcje_html.py --zapisz-zrodla`): kod 0, zmienil sie 1 wiersz w `test_instrukcje.py`, test zielony |
| 12 | `git -C rec-a11d status --short` po probach | pusty (kopia czysta, detached 6e75c6c) |
| 13 | bajty 18 plikow tekstowych galezi (`git show`) | CR 0, znakow spoza ASCII 0, kazdy konczy sie LF (18 z 18) |
| 14 | `tail` logu `robocze\a11d\pytest_r2_0cb883b.log`; `git diff --stat 0cb883b origin/e3/a11d` | "2192 passed, 9 skipped, 1 warning in 1506.20s"; po 0cb883b zmienil sie 1 plik (raport paczki) |

### 2.1 Test zrodel cytatow a paczka E3-P15 (zmiana ukladu w `ui/*.py` bez zmiany tresci napisow)

`ZRODLA_CYTATOW` zapisuje dla kazdego cytatu slownik "plik programu -> liczba pasujacych napisow" (dla cytatu z napisem
w `statusy.py` / `ui/` licza sie tylko te pliki). Numerow wierszy nie ma.

- Przesuniecie wierszy, zmiana kolejnosci, nowe funkcje i nowe napisy nierowne cytatom w `ui/*.py`: test **przezyje**
  (F1, F2 - zielony).
- Test **padnie**, gdy P15: (a) przeniesie staly napis cytowany w instrukcji do innego pliku (F4), (b) powtorzy taki napis
  jako drugi literal w `ui/` albo `statusy.py`, np. nowy podpis "Analiza" wpisany wprost zamiast stalej z `napisy.py` (F3),
  (c) usunie jedno z dwoch wystapien. Wtedy pada dokladnie 1 test (`test_kazdy_cytat_ma_te_same_zrodla_...`), komunikat
  podaje cytat i oba slowniki, a naprawa to jedno polecenie bez zmiany instrukcji (F6: 1 zmieniony wiersz). Ten krok wolno
  jednak wykonac dopiero po sprawdzeniu, ze instrukcja dalej mowi prawde - i lezy on w pliku paczki A11d, wiec paczka
  programu, ktora go potrzebuje, musi miec `testy/test_instrukcje.py` na liscie plikow albo zglosic POTRZEBUJE.
- Ocena: bezpieczne dla nastepnych paczek (falszywy alarm jest glosny, tani w naprawie i nie przepuszcza zmiany napisu);
  nie jest kruchy ponad potrzebe wobec zmian ukladu. Dla E3-P15 wystarczy zasada: napisy zostaja w tych samych plikach,
  a nowe podpisy biora tekst ze stalych `napisy.py` / `statusy.py`.

## 3. Kryteria zlecenia

| Nr | Kryterium (a11d.md / a11d-r2.md) | Ocena |
|----|----------------------------------|-------|
| 1 | Trzy instrukcje + jedna strona T14 na 1 stronie A4 | **potwierdzone wlasna proba** (druk do PDF w Chrome: 4 z 4 po 1 stronie; arkusz 1). Druku na papierze nie zmierzono. |
| 2 | `test_instrukcje.py`: cytaty istnieja, obrazki istnieja, ASCII; pada po zmianie napisu | **potwierdzone wlasna proba**: 36 passed x 3; 12 z 12 wstrzykniec. Granice (znane, D7 / D11): obrazek podmieniony w stronie i zdanie bez cudzyslowu nie sa wykrywane. |
| 3 | Tabela "co robic": wiersz na kazda sytuacje | **potwierdzone przegladem i proba**: 23 wiersze; wiersze samokontroli - nazwy sprawdzen doslownie z `samokontrola.KODY` (13 nazw cytowanych, wszystkie istnieja; format wiersza "poziom nazwa: opis; rada" zgodny); instalator - `INSTALACJA: WSTRZYMANA` (kod 10, tylko pierwsza instalacja i tylko bledy ustawien - `instalator.py:1398-1409`), `INSTALACJA: NIEUDANA` z `(kod ...)` (`:1468-1471`), powrot: zgoda wylacznie `T` / `t` (`:1487`), przy bazie o nowszym schemacie skrypt niczego nie zmienia bez `/przywroc-kopie` (`:1544-1547`) - rada "niczego nie wpisuj i nie uruchamiaj `/przywroc-kopie`, dzwon" jest bezpieczna; "Decyzja NIE zostala zapisana" - B1. Rady falszywej albo niebezpiecznej nie znalazlem (drobne nieostrosci: D12-D14). |
| 4 | Zrzuty: komplet odtworzony z kodu po P14; kazdy obejrzany | **potwierdzone wlasna proba** co do tresci (9 z 9 obejrzanych, 4 z 4 plikow T14 rowne bajtom w stronach); odtwarzalnosc co do bajta - wg testu `test_strona_do_druku_jest_aktualna` (przechodzi), osobno nie powtarzano. |
| 5 | Scenariusz T14 odtworzony od zera | **potwierdzone wlasna proba**: 22 z 22 krokow bez ekranu. Uruchomienie przez `Polecenie.cmd` z programu zainstalowanego: **niepotwierdzone** (D17). |
| 6 | Pelny pytest: 0 failed | **nie powtarzano**; log wykonawcy: 2192 passed, 9 skipped, 0 failed na 0cb883b; po nim zmienial sie tylko raport. |
| r2-1 | Raport: sekcja "Runda 2", lista cytatow zmienionych przez P14, 8 + 3, pomiar A4 | **potwierdzone przegladem** (sekcje 14.2, 14.4, 14.5, 14.9); liczby zgodne z moimi (36 passed; 1 strona x 5; 22 z 22). |
| r2-2 | Zakres plikow | **potwierdzone wlasna proba** - sekcja 4. |
| r2-3 | Bez zmian w kodzie programu, README, opisach, `instalacja_i_aktualizacja.md` | **potwierdzone wlasna proba**: wlasne commity rundy 2 nie dotykaja zadnego pliku spoza listy. |

Zestaw T14: komplet dla wlasciciela jest (`jedna_strona.html` z 4 obrazkami, `scenariusz_symulatora.md` + `symulator_t14.py`
+ `scenariusz_t14.json`, `arkusz_obserwacji.html`, `README.md` z przygotowaniem na programie zainstalowanym: `Stanowisko.cmd`
zamkniety, `Polecenie.cmd`, ekran co najmniej 1280 x 720 po skalowaniu, okno zmaksymalizowane). Arkusz ma 11 zadan (W1-W5,
R1-R6) zgodnych z planem (sekcja 7, T14), pola "wykonane", "interwencja", "zawahanie ponad 10 s: gdzie, ile", podsumowanie
"z 11", kryterium zaliczenia doslownie z planu i tabele decyzji "poprawic / zostawic" - pozwala zapisac wynik wg kryterium.
Czy osoba przejdzie probe tylko z kartka: 10 z 11 zadan ma na kartce bezposredni punkt; W4 wymaga zauwazenia przycisku
"Pokaz nowy wynik: Plytka 2" i pola "Nowy wynik czeka" (kartka o nich nie mowi - swiadomie, plan: "zadnych podpowiedzi";
pole programu samo podaje, co kliknac). To najbardziej prawdopodobne miejsce zawahania - sekcja 5 pkt 1. Przebiegu
z czlowiekiem nie da sie ocenic bez proby.

## 4. Zakres plikow i zasady

- `git diff --stat main origin/e3/a11d`: 23 pliki = 22 pliki paczki (wszystkie z listy `a11d.md`) + `raporty/E3-A11w_2026-11-20.md`
  (roznica 39 wierszy wynika z nowszej wersji tego raportu w `main`, nie ze zmiany a11d). Uwaga: polecenie z trzema kropkami
  (`main...origin/e3/a11d`) pokazuje 53 pliki, bo galezie maja 4 wspolne bazy - do oceny zakresu sluzy porownanie koncow.
- Wlasne commity rundy 2 (5, bez scalen): pliki tylko z listy; `instalacja_i_aktualizacja.md`, kod programu, `README.md`,
  `opisy_modulow/**`, `.gitignore` nietkniete. Stopka Co-Authored-By w 5 z 5.
- ASCII, LF: 18 z 18 plikow tekstowych (CR 0, spoza ASCII 0). PNG: 4 pliki, 624 794 B.
- Rozmiar: 22 pliki = 2 705 946 B (strony `.html` 1 874 229 B: wieczor 469 398, poranek 549 082, co_robic 13 125, jedna_strona
  837 404, arkusz 5 220) - ponizej ok. 3 MB ze zlecenia; bez STL.
- Dane osobowe: na obrazkach i w plikach tylko dane sztuczne; `<PC-katalog>` wystepuje w raporcie paczki (sciezki logow)
  i w jednej asercji testu - konto robocze, nie dane osobowe; nazw zlecen brak.

## 5. Do decyzji wlasciciela (nie blokuje)

1. Czy kartka T14 ma wspomniec o przycisku "Pokaz nowy wynik" (wykonawca: nie; W4 sprawdzi wtedy, czy pole programu
   wystarcza). Pozostaje tez pytanie z rundy 1: kartka jest skrotem instrukcji (12 punktow na 11 zadan).
2. Przed proba T14 na laptopie stanowiska wykonac raz `C:\Stanowisko\Polecenie.cmd C:\T14\symulator_t14.py --sprawdz --program .`
   (D17) - to jedyna czesc zestawu niesprawdzona na programie z paczki.
3. Czy technik sam odpowiada `T` w `Wroc_do_poprzedniej.cmd` (tabela: tak, a przy napisie o kopii bazy dzwoni).
4. Pismo 7,3 pt tabeli "co robic" - ocena po wydruku na papierze.
5. Z rundy 1 bez zmian: pula per praca (instrukcje opisuja pule z folderu), O1 / D7 (obrazki jako pliki), telefon i progi
   "kiedy dzwonic".

## 6. Zauwazone w programie (poza zakresem paczki - nie sa uwagami do PR #40)

| Nr | Ekran | Co widac | Co powinno byc |
|----|-------|----------|----------------|
| N4 | Pasek, przelacznik trybu przy zajetej bazie (proba 7) | komunikat "Polecenie nie zostalo wykonane" z trescia "Blad programu albo dysku - nic nie zostalo zapisane..." (`sqlite3.OperationalError: database is locked` z `kontroler_api.py:3549` nie jest zamieniany na odmowe bazy) - inny napis niz przy pozostalych poleceniach | jak "Polecenie NIE zostalo wykonane - baza zajeta" z "Ponow teraz" |
| N5 | Okno Excela przy zajetej bazie (przeglad kodu) | `excel_zatwierdz` / `excel_pomin` daja zwykly "Baza jest zajeta" bez "Ponow teraz" (D12) | komunikat z ponowieniem jak dla decyzji |
| N6 | Poranek, program wstal w trybie "Poranek" | przycisk "-> Wieczor" obok "Tryb: Poranek" wyglada jak nastepny krok (D15; pozycja 3 listy wykonawcy) | napis mowiacy, co robi przycisk |

Lista wykonawcy "zauwazone w programie (runda 2)" (7 pozycji, raport sekcja 14.10): pozycje 1, 3, 5, 7 widzialem na swoich
zrzutach ("Lista jest pusta. Zapisano do pliku o 19:00"; "-> Poranek"; rada "kliknij "Pokaz nowy wynik"" przy przycisku
dwuwierszowym; "(tryb "pytaj")"); pozycji 2, 4, 6 nie sprawdzalem.

WERDYKT: do scalenia (B 0, P 0, D 7)
