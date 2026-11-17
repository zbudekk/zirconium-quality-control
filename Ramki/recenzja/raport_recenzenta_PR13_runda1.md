# Raport recenzenta PR #13 - runda 1

Data: 2026-11-17. Recenzent: swieza subsesja (Fable 5.2), niezalezna od wykonawcow i koordynatora.
Stan recenzowany: HEAD `fe66217`, PR #13 (`przed-skanerem` -> `main`), zakres `git diff origin/main...HEAD`
(45 plikow, +13 673 / -197, wszystko pod `Ramki/`, bez plikow binarnych). W trakcie recenzji na galezi pojawily sie
dwa commity (`f6cfcd3`, `5ef199e`: plik stanu, 1 linia planu etapu 3, poprawka testu `test_ustawienia.py`) - nie
zmieniaja kodu obliczen; uwzglednione tylko w uwadze D2.
Metoda: czytanie diffu i plikow w HEAD (`plate`, `match`, `inspect`, `krawedz`, `porownaj`, `ustawienia` w calosci
zmian; `synth` w czesci; testy zmienione w starych plikach w calosci). Okno "Dzien skanera" (`dzien_skanera*.py`,
kroki, testy, `pomiar_skanu`) przeczytal pomocniczy recenzent (subagent, tylko czytanie); uwagi P2-P6 pochodza od
niego, linie cytowane w P2-P5 obejrzalem sam w kodzie. Uruchomienia: 2 male proby na PC (`<PC-katalog>\app\r13`, kod z
`git archive HEAD`), skan higieny diffu na MSI (tekst), odczyt logu `k2\pytest_fe66217.log`. Na MSI nie uruchamiano
pytest ani obliczen. Cytaty bez znakow diakrytycznych.

## 0. Werdykt

**do scalenia po poprawkach** - B 1 / P 7 / D 12.

Jedna uwaga blokujaca (B1): w domyslnym trybie pasa brzegu program konczy sie wyjatkiem dla projektu bez linii
brzegu, gdy metoda B znajdzie wciecie - czyli dokladnie wtedy, gdy przed PR byl alarm. Poprawka to kilka linii + test.
Poza tym nie znalazlem sciezki, ktora dawalaby falszywie ZIELONA prace w trybie domyslnym w porownaniu ze stanem
`main` (pas w trybie sumy jest nadzbiorem pasa sprzed P2 - sprawdzone czytaniem i testem
`test_tryb_sumy_pasow_obejmuje_brzeg_gleboki_i_stary_pas`). Tryb domyslny `linia_i_plaszczyzna` nie ma jeszcze
pomiaru koncowego (licza inne sesje) - scalenie dopiero po nim (patrz D5 i pkt 4).

## 1. Uwagi (B = blokujaca, P = poprawic przed scaleniem, D = drobna / moze zostac jako znana)

| Nr | Waga | Plik:linia | Scenariusz (wejscie -> zly wynik) | Sprawdzone | Oczekiwane |
|---|---|---|---|---|---|
| B1 | B | `Ramki/stanowisko/stanowisko/inspect.py:502-504` (wywolanie: `porownaj.py:165`, bez `try`) | Tryb domyslny `pas_brzegu_od = "linia_i_plaszczyzna"`, projekt, dla ktorego `krawedz` nie wyznaczyl zadnej linii (`brzeg.drzewo is None`: bryla bez wneki - np. wklad, licowka, samo przeslo - albo nieudane wyznaczenie). Proba pasa pochodzi wtedy z `probka_brzegu` (pas sprzed P2), wiec metoda B moze znalezc skupisko wciec; dla kazdego skupiska (takze `za_male` i `brak_danych`) kod wola `brzeg.drzewo.query(c)` -> `AttributeError: 'NoneType' object has no attribute 'query'`. `porownaj.dopasuj_fragmenty` nie lapie wyjatku, wiec przepada wynik CALEJ plytki, a nie jednego gniazda. Na `main` (i w trybie `plaszczyzna`) ten sam skan daje `ubytek` (A+B czerwony) / `sprawdz`. Test `test_linia_projektu_niepewna_albo_brak_linii_to_nie_sprawdzono` obejmuje bryle bez wneki w trybie sumy tylko dla skanu BEZ odchylek (zero wciec), wiec bledu nie widzi. | **Uruchomieniem na PC** (`r13\proba2.py`): pudelko 8 x 6 x 5 bez wneki, skan z wglebieniem 0,3 mm o plaskim dnie (r 0,6 na scianie 0,7 mm pod wierzchem; r 0,8 na wierzchu): `plaszczyzna` -> `ubytek` A+B czerwony / `sprawdz` B zolty; `linia` -> `nie_sprawdzono`; `linia_i_plaszczyzna` -> WYJATEK w linii 503 (oba przypadki). Bez wglebienia: `ok`. | W `_linia_brzegu`: gdy `brzeg is None or brzeg.drzewo is None` - odleglosc od plaszczyzny i `filar = 0` (jak w `plamy_pod_powierzchnia:330-332`). Test: bryla bez wneki + wciecie w trybie sumy = ten sam status co `plaszczyzna`. Warto tez objac `I.sprawdz` w `porownaj.py:165` obsluga wyjatku na gniazdo (gniazdo zolte "blad inspekcji", reszta plytki policzona). |
| P1 | P | `Ramki/stanowisko/stanowisko/krawedz.py:805-807, 847-849`; `inspect.py:565-570, 579-606` (`ocena_brzegu`) | Most z 3 filarami; dla jednego filaru niecka jest przyjeta, ale zaden wariant nie daje linii (`L is None` -> tylko wpis w `linie.uwagi`, filaru nie ma w `linie.filary`). `ocena_brzegu` ocenia wylacznie filary z listy, a `linie.uwagi` dolacza tylko, gdy lista jest pusta. Skutek: (a) tryb `linia`: brzeg tego filaru nie ma pasa od linii i nie jest liczony do "nie sprawdzono" -> praca moze byc `ok` (zielona) z niesprawdzonym brzegiem filaru, wbrew opisowi "takze: projekt bez wyznaczonej linii daje nie_sprawdzono" (`inspect.py:14-16`, `ustawienia.przyklad.toml:59`); (b) tryb domyslny: dziala tam tylko pas sprzed P2 (bez regresji wzgledem `main`), ale wynik nie ma zadnej uwagi, ze linii filaru nie wyznaczono. | Czytaniem (nie mam projektu, ktory to wywoluje; w puli 17 projektow raport podaje 23 petle z 23). | Filar z przyjeta niecka bez linii: w trybie `linia` -> `nie_sprawdzono` (powod `linia`), w trybie sumy -> wpis w `uwagi_linii`. Test jednostkowy na `LinieProjektu` z niepusta lista i wpisem "linii nie wyznaczono". |
| P2 | P | `Ramki/stanowisko/stanowisko/dzien_skanera_rdzen.py:1324-1331, 1647-1649` (oraz 596-598, 1629) | Plik A skopiowany: `dodaj_plik(pilne=False)` odklada zapis manifestu do konca przegladu, a `_zapisz_znane(pilne=False)` ma WLASNY licznik 5 s i moze zapisac `obserwator.json` od razu (A = "znany"). Ten sam przeglad kopiuje potem duzy plik B (minuty); awaria / zabicie procesu w tym czasie. Po wznowieniu A jest "znany" (nie bedzie kopiowany ponownie), a w manifescie go nie ma: kopia lezy w folderze sesji bez wpisu, krok pokazuje brak. Opis modulu (`opisy_modulow/dzien_skanera.md:32-35`) twierdzi odwrotnie. | Czytaniem (pomocniczy recenzent; linie 1324-1331 i 1647-1649 obejrzalem sam). | Przed kazdym zapisem `obserwator.json` wymusic zapis zaleglego manifestu (albo zapisywac oba razem). Test: awaria miedzy kopia a zapisem manifestu. |
| P3 | P | `dzien_skanera_rdzen.py:1869` (`_pliki_sesji`), 2234-2235, 2252-2254 | Folder skanera / zlecenia zawiera plik `*.bak` albo `*.tmp` (kopia calego folderu bierze wszystko). Plik jest w sesji i w manifescie, ale filtr `endswith((".czesc", ".tmp", ".bak"))` usuwa go z `SHA256SUMS` i z ZIP. `--sprawdz <folder>` nic nie zglasza (te rozszerzenia sa odfiltrowane takze z listy "dodatkowe"); `--sprawdz <zip>` daje "plik z manifestu nie istnieje" i kod 1, ponowne pakowanie tego nie naprawia. Dane zostaja w folderze sesji - dlatego P, nie B. | Czytaniem (linia 1869 obejrzana przeze mnie). | Filtr tylko dla wlasnych plikow programu (`sesja.json.bak/.tmp`, `obserwator.json.bak/.tmp`, `kontrole/*.tmp`, `*.czesc` spoza manifestu). |
| P4 | P | `dzien_skanera_rdzen.py:1980-1986, 2051-2053`; `dzien_skanera.py:793-799, 817-823` | `zakonczono`, `spakowano` i `zmieniono_po_spakowaniu = False` sa zapisywane na dysk PRZED pakowaniem, a stare ZIP-y sesji sa kasowane przed zbudowaniem nowych. (a) Brak miejsca / wyjatek w trakcie: stan mowi "Spakowano: <czas>", przy starcie pytanie "ostatnia sesja jest zakonczona i spakowana"; (b) zamkniecie okna w trakcie pakowania (`closeEvent` nie ostrzega): starych ZIP juz nie ma, nowego nie ma, stan mowi "spakowana". Technik moze wyslac / zarchiwizowac niekompletna paczke albo uznac dzien za zamkniety. | Czytaniem (linie 1978-1990 i 2046-2060 obejrzane przeze mnie). | Znaczniki dopiero po sukcesie (albo przywracane w `except` / `finally`); stare ZIP kasowac po `os.replace` nowych; test nieudanego pakowania. |
| P5 | P | `dzien_skanera_rdzen.py:63` (`WZOR_PROJEKTU_EXOCAD = r"_cad\.stl$"`), 781, 1609, 1990 | Projekt exocad `X_cad.stl` (nazwisko w nazwie) zapisany ponownie w tym samym kroku dostaje w sesji nazwe `X_cad__zmiana2.stl`, dodany drugi raz - `X_cad__2.stl`. Wzor zakotwiczony na koncu nazwy zadnej z nich nie lapie -> plik i jego nazwa (dane osobowe) trafiaja do ZIP, raportu i manifestu paczki, ktora wychodzi poza pracownie. Test (ok. linii 609-641 `test_dzien_skanera.py`) sprawdza tylko pierwsza wersje. | Czytaniem (wzor w linii 63 obejrzany przeze mnie; nazwy wersji wg pomocniczego recenzenta). | Wzor `_cad(__\w+)?\.stl$` albo decyzja po nazwie zrodla zapisanej w manifescie; test z druga wersja i duplikatem. |
| P6 | P | `dzien_skanera_rdzen.py:1244-1245, 1254-1255, 1485-1510, 460`; `dzien_skanera_kroki.toml:349` | Krok "kopia calego folderu": zdarzenie w manifescie zapisuje `plikow = len(lista)` PRZED kopiowaniem; przerwanie (brak miejsca, zamkniecie okna, plik zablokowany, podkatalog bez uprawnien pomijany przez `except OSError: continue`) nie zostawia sladu w manifescie. Krok ma `ile_plikow = 1`, wiec jest "zrobiony" po pierwszym pliku, `--sprawdz` zwraca 0 ("komplet"), po restarcie kopia nie jest wznawiana. Zrodlo zostaje nietkniete, ale paczka z dnia skanera jest niepelna bez ostrzezenia. | Czytaniem (pomocniczy recenzent). | Liczby skopiowanych / bledow / pominietych w manifescie po zakonczeniu; `--sprawdz` porownuje z lista; wznowienie niedokonczonej kopii. |
| D1 | D | `dzien_skanera_rdzen.py:342, 2058, 2068` | Plik zrodlowy z data modyfikacji sprzed 1980 (kopia zachowuje mtime): `ZipFile` bez `strict_timestamps=False` rzuca `ValueError` przy kazdej probie pakowania. | Czytaniem; zachowanie biblioteki znane, nie uruchamiane. | `strict_timestamps=False`. |
| D2 | D | `Ramki/stanowisko/testy/test_ustawienia.py` (`test_nowe_klucze_maja_domyslne_ze_wzoru`) | Na `fe66217` test jest czerwony zawsze: `stary.replace("[inspect]", ...)` trafia tez w komentarz naglowka `[synth] ... bierze z [inspect]` (`ustawienia.przyklad.toml:63`) -> "[synth] pas_brzegu_od: nieznany klucz". Koordynator poprawil to w `5ef199e` w trakcie recenzji - poprawki nie uruchamialem. Drugi czerwony test w logu (`test_repo_nie_sledzi_danych_ani_ustawien_maszyny`: `git ls-files` kod 128) to srodowisko (katalog z `git archive` nie jest repozytorium), nie blad kodu. | Log PC `k2\pytest_fe66217.log`: 2 failed, 406 passed, 3 skipped (434 s). | Powtorzyc ten jeden test na `5ef199e`; w opisie PR wpisac wynik koncowy. |
| D3 | D | `Ramki/stanowisko/testy/test_edge_synth.py:262-270`; `test_match.py:44-45` | Dwa stare testy zmienione: (a) asercja polozenia ubytku poluzowana z `max - pas - 0,05` do `max - pas - 1,0` (dodana w zamian asercja `odleglosc_od_linii <= pas`) i `przenikanie_okr` -> okragle / rynienka; (b) fixtura `fragmenty` przelaczona na `wersja_ubytkow=1`. Obie zmiany maja uzasadnienie w komentarzu (P4 zmienia definicje pasa i strumien losowy) i nie oslabiaja kontroli kodu produkcyjnego; (b) oznacza jednak, ze testy `match` nie cwicza nowego generatora. Innych oslabien starych testow nie znalazlem. | Czytaniem calego diffu starych plikow testow. | Zostaje jako znane. |
| D4 | D | `Ramki/stanowisko/stanowisko/match.py:487` (`poza_pasem = ... [:, 2] <= -pas_brzegu_mm`) | Korekta skali wylacza strefe brzegu tylko jako pas od plaszczyzny z = 0 (2 mm). Dla filarow mostu z brzegiem glebiej (dokladnie przypadek, ktory naprawia P2) punkty przy krawedzi brzegu BIORA udzial w estymacji skali. Wplyw ograniczaja wagi Tukeya i wylaczanie "obszarow odbiegajacych", wiec nie oczekuje bledu statusu - ale zasada "ukruszenie brzegu nie zmienia skali" nie jest spelniona dla glebokich brzegow. | Czytaniem. | Dopisac do granic w `match.md`; docelowo pas od linii z `krawedz`. |
| D5 | D | `inspect.py:579-590` (`tylko_dane`), `ustawienia.py:110` | Tryb domyslny: filar z linia `niepewna` (polozenie linii moze byc bledne) i gleboki brzeg -> stacje "maja dane", praca zielona z uwaga "tam pas brzegu takze od plaszczyzny" - uwaga jest mylaca, bo pas od plaszczyzny glebokiego brzegu nie obejmuje. To swiadomy kompromis koordynatora (opis PR: "tryb sumy niezmierzony"); wzgledem `main` nie jest to regresja. | Czytaniem; test `test_linia_projektu_niepewna...` potwierdza zachowanie. | Scalac po pomiarze trybu sumy (r54 / R59, K6); doprecyzowac tresc uwagi. |
| D6 | D | `Ramki/stanowisko/stanowisko/synth.py` (`wytnij_ubytek`: kandydaci w pasie od ZWERYFIKOWANYCH stacji; `wytnij_ukruszenie`: tylko zweryfikowane przekroje) | Generator stawia ubytki tam, gdzie inspect ma pewna linie; ubytki przy niezweryfikowanych odcinkach linii (lacznik mostu) nie wystepuja w zestawach. Wykrywalnosc z metryk P2 / P4 / K6 jest wiec gorna granica, nie srednia po calym brzegu. | Czytaniem. | Jedno zdanie w raporcie czesci B / `synth.md`. |
| D7 | D | `Ramki/stanowisko/opisy_modulow/dzien_skanera.md:60-62`; `raporty/dzien_skanera_2026-11-16.md:43-49, 174-175`; `opisy_modulow/inspect.md` | (a) Opis i raport mowia, ze okno rozpoznaje uklad petla po `plate.wyrownaj` "do podmiany na automatyczne"; kod od `502212e` wola `plate.rozpoznaj_uklad`. (b) `inspect.md` nie zawiera nazwy trybu domyslnego `linia_i_plaszczyzna` (0 wystapien) - punkty 5 i 7 opisuja tryb `linia`. | Czytaniem / wyszukaniem. | Poprawic opisy. |
| D8 | D | `Ramki/stanowisko/narzedzia/pomiar_skanu/c_wspolne.py:18`; jeden z raportow (wiersz tabeli "F2") | Sciezki z nazwa konta: `<PC>\Desktop\Prace_test` (stala nieuzywana) i `<MSI>\kod\qc\...`. Nazwisk, nazw folderow zlecen, sekretow, znakow sterujacych, plikow STL / binarnych w diffie: 0 (pkt 2). | Skan diffu. | Usunac stala; sciezke w raporcie mozna zostawic. |
| D9 | D | `Ramki/stanowisko/stanowisko/plate.py:742-744` (galaz `domyslny`) | Dwa uklady tej samej rodziny (kwadrat / kolo) przechodza, brak numeru, ksztalt nie rozstrzyga: wybierany jest uklad bez widocznych dolkow z `pewny = False` i ostrzezeniem. Gniazda i stozki sa te same, wiec statusy prac nie zaleza od wyboru; rozni sie model brzegu plytki i numer. Zachowanie opisane i jawne - zostaje. | Czytaniem. | - |
| D10 | D | `dzien_skanera.py:751-764`; `dzien_skanera_rdzen.py:1350, 1398, 1569-1571, 250, 266-271, 469-476, 2084-2086, 2173-2176, 1469` | Drobne uwagi do okna (pomocniczy recenzent): pakowanie nie czeka na pliki w drodze; "dwa stabilne odczyty" to licznik, nie czas; sonda `ktos_pisze` otwiera zrodlo bez wspoldzielenia zapisu; STL z bajtami za danymi = "uciety" bez proby wczytania; `--sprawdz` = 0 dla kroku z samym watpliwym skanem; `zmieniono_po_spakowaniu = True` tylko w pamieci; `--sprawdz` na folderze z kilkoma paczkami sprawdza pierwsza; dwa foldery obserwowane o tej samej nazwie mieszaja sie w kopii. | Czytaniem (pomocniczy recenzent). | Lista do nastepnej paczki okna; nic z tego nie niszczy zrodel. |
| D11 | D | `Ramki/stanowisko/testy/test_dzien_skanera.py` | Luki testow wzgledem opisu: brak testu zrodla zmienionego w trakcie kopii, awarii miedzy kopia a manifestem (P2), nieudanego pakowania (P4), plikow `.bak` / `.tmp` ze skanera (P3), drugiej wersji `_cad` (P5), wznowienia z `.tmp`. Pustych asercji ani mockow zastepujacych sprawdzana logike nie ma; liczba testow (53) zgodna z raportem. | Czytaniem (pomocniczy recenzent). | Dodac przy poprawkach P2-P5. |
| D12 | D | opis PR #13 | Liczby pytest w opisie (285 / 276 / 305) sa z galezi czesciowych; pole "pelny pytest" niezaznaczone. Stan faktyczny `fe66217`: 406 / 3 / 2 (D2). | Log PC. | Uzupelnic po `5ef199e`. |
| P7 | P | `Ramki/stanowisko/stanowisko/porownaj.py:165` | Kazdy wyjatek z `inspect.sprawdz` (B1 jest pierwszym znalezionym; nowy kod P2 ma kilka sciezek z drzewami `None` / pustymi tablicami) konczy `porownaj` dla calej plytki bez wyniku JSON. Przed PR inspekcja nie miala modulu `krawedz` (ok. 1000 linii geometrii liczonej na dowolnym projekcie klienta), wiec ryzyko wyjatku na jednym nietypowym projekcie bylo mniejsze. | Czytaniem + B1 uruchomieniem. | `try` na gniazdo: status inspect np. `sprawdz` z uwaga "blad inspekcji: ...", gniazdo zolte, nigdy zielone; reszta plytki policzona. |

## 2. Co sprawdzilem i nie budzi zastrzezen

- `plate.rozpoznaj_uklad`: kolejnosc rozstrzygania (numer podany, numer z dolkow, ksztalt, wykluczenie, domyslny),
  `pewny = False` przy sprzecznosci ksztaltu z numerem, wyjatki `NierozpoznanyUklad` / `BladWyrownania`, odtworzenie
  stanu generatora dla kolejnych ukladow; `wyrownaj` = te same kroki co przed zmiana (czytaniem).
- `match.filtr` (P1): regula wysokosci nigdy nie jest ostrzejsza niz przed zmiana (`min(projekt - tol, udzial x projekt)`),
  ratunek "dopasuj wszystkie" dziala takze z nowa regula; `cechy_do_glebokosci` z pamiecia na projekt (czytaniem).
- Korekta skali (P3): pochodne Gaussa-Newtona, jednostki odleglosci w `ocena` (dzielenie przez skale), okno + 0,05,
  brak korekty dla plytki porannej, dla pokrycia ponizej progu ostrzezenia i przy spadku pokrycia > 0,02; `inspect`
  normalizuje normalne (czytaniem). Praca z bledem skali do 1 % jest zielona z ostrzezeniem powyzej 0,3 % - to
  decyzja wlasciciela z 06.11, nie blad.
- Tryb sumy: pas = nadzbior pasa sprzed P2 (plamy: `min(odl. od linii, odl. od plaszczyzny)`; proba B: czesc od
  linii + punkty pasa od plaszczyzny), `ma_dane[:len(st_O)]` zgodne z kolejnoscia `probka_suma` (czytaniem).
- Zgodnosc wstecz: `uzupelnij_domyslne` (brakujace klucze z `DOMYSLNE_NOWYCH` = wartosci wzoru, test zgodnosci),
  `uzupelnij_uklady_wbudowane` (`*_r54` dopisywane, gdy katalog istnieje), `--plytka` reczne dziala jak dotad,
  `auto` jako nowa wartosc domyslna, pula budowana po rozpoznaniu typu plytki (czytaniem).
- Wartosci w `README.md`, `match.md`, `ustawienia.przyklad.toml` = `DOMYSLNE_NOWYCH` (0,5 / 1,0 / 0,3 / 2,0 /
  0,9 / 1,5 / 0,05 / 0,08 / 0,40) - zgodne.
- Higiena (skan 13 726 dodanych linii): 37 slow z nazw plikow / folderow `Prace_test` (>= 5 liter) - trafienia tylko
  3 slowa ogolne (nazwy typow prac), 0 nazwisk; znaki sterujace 0; wzorce sekretow 0; pliki binarne / STL / ZIP 0;
  pliki spoza `Ramki/` 0.

## 3. Liczniki

- B: 1 (B1). P: 7 (P1-P7). D: 12 (D1-D12).
- Uruchomione: 2 proby na PC (9 przebiegow `inspect.sprawdz` kazda), 1 skan higieny, 1 odczyt logu pytest.
- Pliki obejrzane w calosci zmian: `plate.py`, `match.py`, `inspect.py`, `krawedz.py`, `porownaj.py`,
  `ustawienia.py`, `ustawienia.przyklad.toml`, diff starych plikow testow (6 plikow).

## 4. Czego NIE sprawdzilem

- Pomiarow koncowych czesci A i B (tryb `linia_i_plaszczyzna` na r54 / R59, K6) - licza inne sesje; werdykt zaklada,
  ze nie pokaza regresji wykrywalnosci ani wzrostu "nie sprawdzono" na pracach calych.
- Liczb w raportach wykonawcow (`raporty/*2026-11-1[56]*.md`): 80/80, 382 -> 388/397, 293/680 -> 25/680 itd. - nie
  odtwarzalem; sprawdzilem tylko wartosci ustawien i liczbe testow okna.
- Poprawki `5ef199e` (test) uruchomieniem; pelnego pytest na HEAD po niej.
- `synth.py`: przeczytane funkcje `_wytnij_kule`, `wytnij_ubytek`, `wytnij_ukruszenie`, `polozenie_wzgledem_brzegu`,
  `ubytek_widoczny`; reszta diffu (`Material`, `_przytnij`, CLI, `generuj_plytke`) nie.
- `ui_test.py` (zmiany okna glownego), `narzedzia/auto_uklad.py`, `metryki_krawedz.py`, `metryki_skala.py`,
  `metryki_P3a.py`, `pomiar_skanu.py` (poza koncowka), `c_wspolne.py` (poza poczatkiem), nowe pliki testow
  `test_auto_uklad.py`, `test_krawedz.py`, `test_skala.py` - nie czytane.
- Okna "Dzien skanera" nie uruchamialem (ani ja, ani pomocniczy recenzent); P2-P6 i D1, D10 wynikaja z czytania.
- `plan_etap3_pelna_aplikacja_2026-11-16.md`: tylko wyszukanie nazw kluczy i `--plytka`; sprzecznosci z kodem nie
  znalazlem, ale dokumentu nie czytalem w calosci. `sciaga_skaner_DentalScan`, karta dnia - nie czytane.
- Scenariusza P1 (filar z niecka bez linii) i odbicia lustrzanego w `skala_macierzy` (wyznacznik ujemny) nie
  probowalem wywolac.
- Prawdziwych skanow nie bylo (zgodnie z decyzja z 15.11) - wszystko na geometrii sztucznej.
