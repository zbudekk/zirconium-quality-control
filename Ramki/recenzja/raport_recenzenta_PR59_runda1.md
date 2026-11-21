# Raport recenzenta - PR #59 (galaz `e3/odbior2`), runda 1

- Data: 21.11.2026 (PC, konto `<konto-PC>`), recenzent niezalezny, zlecenie 2 koordynatora.
- Zakres: `main...e3/odbior2` = `1f231d9...a64b69d` (4 commity: 1c43c66, 575a5b5, db329c8, a64b69d); 204 pliki, +12773 / -0.
  Przedmiot: nowa sekcja 10 w `Ramki/etap3/odbior_koncowy/RAPORT.md` (+163 wiersze, w tym 1 zdanie w sekcji 0) i katalog
  `Ramki/etap3/odbior_koncowy/dowody_z2/` (203 pliki). Kodu programu PR nie zmienia - recenzja dokumentu odbioru.
- Miara: `zlecenia\odbior2-koniec.md` (pkt 5 i 6, kryteria 1-4), `zlecenia\odbior2-final.md`, `wspolne.md`, `recenzent.md`.
- Metoda: wlasna kopia `<PC-katalog>\qc-wt\rec-odbior2` (detached a64b69d, tylko odczyt); pliki robocze
  `<PC-katalog>\koordynator\robocze\rec-odbior2\`. Kazda liczba sekcji 10 porownana z plikiem zrodlowym na PC
  (`robocze\odbior2\final\T<nr>\WYNIK.md` + logi, `robocze\odbior2\T2|T10|T11\WYNIK.md`, `dowody/T<nr>/` nocy, sekcje 0-4a raportu);
  T10 i T11 przeliczone z surowych plikow pomocnikami wykonawcow (z `<PC-katalog>\qc-wt\integ\Ramki\stanowisko`, tylko odczyt;
  `git status --short` tej kopii pusty, HEAD 0fedbf6); sumy paczek i sklad ZIP policzone samodzielnie; kopie dowodow porownane
  bajtowo ze zrodlami po przemianie `dowody_lf.py`; T13 i T9 uruchomione samodzielnie. Pelnego pytest nie uruchamialem (PR bez kodu).
  Jeden proces python naraz.

## 0. Werdykt i liczby

WERDYKT: do scalenia (B 0, P 0, D 4).

Liczby sekcji 10 sa prawdziwe: wszystkie liczby i werdykty tabel 10.1-10.4 i 10.7 porownane ze zrodlami (proby 3-25), niezgodnych 0. Noc (sekcje 0-9, `dowody/`)
nietknieta: 0 usunietych wierszy w calym diffie, w `RAPORT.md` tylko 1 dopisane zdanie w sekcji 0 i dopisana sekcja 10 po sekcji 9.
Dowody: 185 z 185 kopii = zrodlo po przemianie `dowody_lf.py`; 0 plikow STL / baz / ZIP / > 1 MB; T13 na HEAD a64b69d: naruszen 0;
dane osobowe: 0 trafien calych nazw (435 nazw). FAIL T2 (e) opisany wprost. Uwagi D dotycza sposobu podania wariantow licznikow i
2 opisow - do poprawki przy okazji, bez blokowania.

## 1. Uwagi

| Nr | Waga | Plik:linia | Scenariusz (stan -> co sie dzieje) | Propozycja |
|---|---|---|---|---|
| 1 | D | `Ramki/etap3/odbior_koncowy/RAPORT.md:387` | Liczniki zlecenia 2 podaja tylko wariant lagodniejszy ("gdy koordynator uzna Z2-N1 i Z2-N2 ... T1, T10, T11 = ZAL"), a nie podaja wariantu doslownego: wg reguly planu T12 ("kod inny niz oczekiwany w ktorymkolwiek kroku = FAIL czesci B") proba 1 czesci B (kod 6 zamiast 0, potem 9 / 9 zamiast 8 / 0) = FAIL czesci B -> T12 FAIL, razem FAIL 2. Noc w sekcji 0 podaje taki wariant dla T9 ("Jesli T9 liczyc doslownie wg planu..."). Do tego: wariant "T11 = ZAL" pomija Z2-N5 (czesc A i B z dwoch przebiegow), a w licznikach T10 ma tylko Z2-N1, choc wiersz tabeli ma tez Z2-N5. Fakty sa w 10.4 (Z2-N3: "wg litery planu ... = FAIL proby") i w K-c, wiec nic nie ukryto - ale wlasciciel czytajacy tylko liczniki widzi FAIL 1. | Dopisac 1 zdanie: "Wg litery planu (proba 1 czesci B T12 = FAIL czesci B, Z2-N3): T12 = FAIL, FAIL 2 - decyzja K-c"; w wariancie lagodniejszym dopisac Z2-N5 przy T11; w licznikach przy T10 dopisac Z2-N5 (albo napisac, ze dla T10 Z2-N5 nie jest odstepstwem, bo przebieg powtorzono w calosci). |
| 2 | D | `Ramki/etap3/odbior_koncowy/RAPORT.md:30` | Zdanie w sekcji 0: "testy T0, T1, T2, T10, T11, T12 i T13 powtorzono na wydaniu 0.3.3 (commit 0fedbf6)". T2, T10, T11 nie biegly na paczce wydania, tylko na kopii repo tego commita (Z2-N1, decyzja nr 30); wyjasnienie jest dopiero w 10.2 / 10.4. Czytelnik samej sekcji 0 moze uznac, ze 7 testow szlo na instalacji z paczki. | "... powtorzono na commicie wydania 0.3.3 (0fedbf6; T0, T1, T12 na paczce, T2, T10, T11 na kopii repo - Z2-N1) ...". |
| 3 | D | `Ramki/etap3/odbior_koncowy/RAPORT.md:383` (i 412) | T11 krok 4 (testy "zly uklad"): w nocy 45 passed z kodu repo I z instalacji (O14: zrodlo kodu INSTALACJA 1 z 1); na 0.3.3 tylko `py.cmd` z kopii repo (`krok_t11_B.cmd`), wariantu z instalacji nie wykonano. Kolumna nocy w wierszu T11 pisze "kod z repo i z instalacji", kolumna 0.3.3 nie mowi, ze wariant z instalacji NIE ZMIERZONO; Z2-N1 pisze tylko "O14 nie dotyczy". | W wierszu T11: "krok 4 tylko z kopii repo; z instalacji: nie wykonano (Z2-N1)". |
| 4 | D | `Ramki/etap3/odbior_koncowy/RAPORT.md:478` | Opis "pliki w kodowaniu cp1250 ... polskie litery z wyjscia polecen konsoli" dla `T12/t12_*_stany.txt` jest nietrafny: to strona kodowa konsoli cp852, ktora `dowody_lf.py` odczytal jako cp1250 - stad nie tylko `?`, ale i zle litery (np. w kopii "Nie molna odnale?? okre?lonego pliku." z "Nie mozna odnalezc okreslonego pliku."). Liczby w tych plikach nie sa dotkniete (sprawdzone: znieksztalcony jest tylko tekst komunikatu `cmd`). | Poprawic opis na "cp852 (konsola) odczytane jako cp1250 - tekst komunikatow znieksztalcony, liczby bez zmian"; ewentualna poprawka `dowody_lf.py` (proba cp852) - osobna paczka, nie ten PR. |

B: brak. P: brak.

## 2. Wlasne proby

| Nr | Polecenie (skrot) | Wynik (liczba) |
|---|---|---|
| 1 | `git diff main...e3/odbior2 --stat` / `--numstat` / `--name-only` | 204 pliki, +12773 / -0; poza `dowody_z2/` tylko `RAPORT.md`; wierszy usunietych 0; `merge-base` = `main` 1f231d9 |
| 2 | diff `RAPORT.md` (hunki) | 2 hunki: +1 wiersz po wierszu 29 (sekcja 0), +162 wiersze po wierszu 342 (po sekcji 9); 0 wierszy `-` |
| 3 | `sha256sum <PC-katalog>\wydania\Stanowisko_0.3.3.zip Stanowisko_0.3.4-t12.zip` | b6049229...05103b1377 i 42d3e33c...ffc70f6a = raport, `.zip.sha256`, zlecenie, wiersz `SHA256SUMS_wydania.txt` w 1f231d9 (w 0fedbf6 wiersza 0.3.3: 0 - jak opisano) |
| 4 | python `zipfile` na obu ZIP | 0.3.3: 228 plikow, 472 631 490 B, `SHA256SUMS` 227 wierszy, program 148 / kola 73 / kola_testy 3 / gora 4 (= 10.1); 0.3.4-t12: 228 plikow, 227 wierszy sum |
| 5 | `git diff --stat 0fedbf6 1f231d9`; `git log --merges 571e186..0fedbf6`; `WERSJA` | 11 plikow (7 nowych dokumentow, 4 zmienione: plik stanu, `wydania/README.md`, `SHA256SUMS_wydania.txt`, `WERSJA` 0.3.3 -> 0.3.4); kod programu i testy bez zmian; scalenia PR #51 8ae6474, #52 3c9a40e, #56 1fce3fe, #55 66893fa, #57 0fedbf6 (= 10.1) |
| 6 | `zestaw_t10.py final\T10\t10\t10_surowe_metryki.json final\T10\t10_surowe.log` (py.cmd, kopia integ) | skanow 40, wyrownanie 40 z 40 (maks. 0,0143 mm), top-1 "dobrze" 276 z 276 (bledne 0), falszywe czerwone 0 z 127, czas 996,2 s (= 16 min 36 s) |
| 7 | `sprawdz_t10.py` teraz vs noc i teraz vs 7ebb5cd | wyniki bajtowo rowne `sprawdz_t10.txt` i `sprawdz_t10_7ebb5cd.txt` wykonawcy: roznice gniazd 2 z 413 (noc), 1 z 413 (7ebb5cd); statusy 116 / 66 / 200 / 27 / 4 (noc i 7ebb5cd 116 / 66 / 201 / 26 / 4) |
| 8 | `zestaw_t11.py final\T11\robocze\t11\dane\stanowisko.sqlite` (tryb `mode=ro`) + `t11_symulator.json` + 2 katalogi skanow | prawda 40, dziennik 40 z 40 dobrych, skany 40, (n) 40 z 40, (a) 40 z 40, auto 40 z 40, (b) zielone 0 (0 skanow), (c) 40 z 40 |
| 9 | `t11_auto_uklad_podsumowanie.json`, `t11_testy.log`, `kody.txt` T11 | A: bez numeru 40 z 40, z numerem 16 z 16, zle_ale_pewny 0; `45 passed, 174 deselected`; kody A 0, B symulator 0, program 0, testy 0 |
| 10 | `diff` `t11_skany_sha16.tsv` (kolumny sha16 ... numer_zrodlo) final vs 7ebb5cd | 40 z 40 identycznych; `t11_statusy.tsv` i `t11_zielone_prace.tsv` identyczne |
| 11 | `t2/t2_wynik.txt` final, pierwsze wiersze `WYNIK.md` 7ebb5cd i nocy | (a) 10 z 10, (b) 0,443 s 9 z 9, (c) 17,85 / 48,66 s, (d) 67,4 ms 0, (e) 19 z 20 (czerwone 7 / zolte 12 / zielone 1), falszywe 0 z 37, `T2 LACZNIE: FAIL (4 z 5...)`; 7ebb5cd 0,435 / 18,63 / 51,60 / 42,3 ms / 19 z 20; noc 0,428 / 15,04 / 39,54 / 34,7 ms / 25 z 26 (= 10.2) |
| 12 | `t1_pytest.log`, `t1_pytest_bazowy.log`, `kody.txt`, `t1_collect.txt` T1 | `2506 passed, 9 skipped, 1 warning in 2246.86s` (kod -1073741819 = 0xC0000005, po podsumowaniu "Fatal Python error: Aborted" + "access violation") i `... in 2225.26s` (kod -1073740791 = 0xC0000409); collect 2515 i 2515 |
| 13 | `kody.txt`, `czasy.txt`, `t12_B_4.log` T12 | aktualizacja 17:50:41,50-17:52:21,97 = 100,5 s kod 0; proba 1 B4 kod 6 ("63 znakow"), B6 / B7 kody 9 / 9; proba 2 kody 10,0,0,0,0,0,8,0,0 (9 z 9; z krokiem 1 11 z 11); dodatek Z kody 9 z 9 (= 10.2, Z2-N3, Z2-N4) |
| 14 | `porownaj_kopie.py` (wlasny; przemiana jak `dowody_lf.py --napraw`, `.cmd` / `.ps1` bez przemiany) | 185 kopii zgodnych, 0 roznych, 0 bez zrodla; 12 plikow powstalych w repo (6 x `dowody_lf.txt`, 6 x `POMINIETE.txt`) |
| 15 | lista plikow najwyzszego poziomu `final\T<nr>\` minus kopie | 6 nieskopiowanych, wszystkie 6 wymienione w `POMINIETE.txt` (`ustawienia_*.toml` x4, `t10_metryki.json`, `t10_surowe.log`) |
| 16 | `find dowody_z2` (liczba, rozmiar, rozszerzenia, > 1024 KB, podkatalogi) | T0 30 / T1 30 / T2 18 / T10 15 / T11 30 / T12 74 / T13 5 + `t9_dowody_z2.txt` = 203; 717 581 B (701 KB) bez T13; > 1 MB: 0; rozszerzenia tylko cmd / json / log / md / ps1 / py / tsv / txt (STL / baz / ZIP: 0); najwiekszy 71 573 B |
| 17 | `git ls-files --eol dowody_z2/`; bajty > 127 w dodanych wierszach `RAPORT.md` | i/lf 171, i/crlf 29 (= 24 `.cmd` + 5 `.ps1`), i/none 3 (puste pliki stderr); dodane wiersze raportu: 33 776 B, nie-ASCII 0, CR 0 |
| 18 | sumy z `dowody_lf.txt` 6 katalogow | naprawionych 17 / 13 / 11 / 5 / 14 / 48 = 108; CR 5982; bajtow nie-ASCII 96; `?` 29 (T1 2, T12 27: 3 / 18 / 3 / 3) - wszystkie = tabela 10.7 |
| 19 | `t13_higiena.py --repo <PC-katalog>/qc-wt/rec-odbior2 --od 2537f6f --do HEAD` | kod 0; 2537f6f..a64b69d: 1355 zmienionych (1272 nowych), E3 933 / 29 / 0, NARUSZENIA 0, O11 7 z 7 (851 wierszy / 6936 B), kopie R58 10 z 10, uwagi R58 / R59 126 |
| 20 | `t9_dane_osobowe.py --nazwy-z` pula `Prace_test` + drzewo A5i + 3 foldery Cyrkon instalacji 0.3.3 / T12, `--baza` T2, T11, T12 K_B, `t0\odbior2`; `--cel dowody_z2 --cel RAPORT.md`, bez `--dozwolone` | samotest 0 nieznalezionych; nazw 435, plikow 204; **trafien calych nazw 0 w 0 plikach**, kod 0; czlony "do wyjasnienia" 100 w 22 plikach - wszystkie od drzewa sztucznego A5i (zwykle slowa, np. czlon w nazwie `t12_P7a_start_atrapa.log`); z sama pula testowa: czlony 1 - w czesci `RAPORT.md` z `main` (sprawdzone osobno: stara wersja 1, dodane wiersze 0) |
| 21 | `ODTWORZONE_2026-11-21.txt` + porownanie 3 plikow nocy z `main:dowody/T0` po LF -> CRLF | 3 z 3 bajtowo rowne (6192 / 80 / 308 B) - Z2-N6 prawdziwe |
| 22 | `git diff 571e186 0fedbf6 -- statusy.py`, wzor `niezgodny_uklad` w 0fedbf6 | wiersz `niezgodny_uklad` niezmieniony, tekst staly bez nazwy ukladu (O6 w 10.4 prawdziwe) |
| 23 | `ciezkie.log` 18:23-21:06 | `START f3-t10` 18:23:31, przejecia blokad 20:14:21, `START f5-t10` 20:14:21, brak `START f5-t11`, `KONIEC f5-t10` 20:30:59 kod 0, `KONIEC f5-t11` 21:06:17 kod 0 (K-i, Z2-N5 prawdziwe) |
| 24 | `diff` `krok_t11.cmd` / `krok_t11_B.cmd` | czesc od `t11 B START` identyczna; roznica = 3 wiersze czesci A (10.8 pkt 5 prawdziwe) |
| 25 | `git rev-parse origin/e3/odbior2`; `git -C qc-wt\odbior2 status --short` | a64b69d (wypchnieta); 0 wierszy |

## 3. Kryteria zlecenia (`odbior2-koniec.md`)

| Kryterium | Ocena | Dowod |
|---|---|---|
| (1) T10 i T11 maja werdykt z liczbami (albo opisany FAIL / przerwanie) | potwierdzone wlasna proba | proby 6-10: T10 40 z 40 / 276 z 276 / 0 z 127; T11 40 z 40 / auto 40 z 40 / zielone 0 / 40 z 40, A 40 z 40 / 16 z 16, 45 passed; przerwanie 18:29 opisane (Z2-N5), dowod przerwania na PC |
| (2) sekcja raportu kompletna, noc nietknieta | potwierdzone wlasna proba + przegladem | proby 1-2 (0 wierszy usunietych, 1 zdanie w sekcji 0); wszystkie elementy pkt 5 zlecenia sa: wydanie (numer, commit, SHA-256, 227 plikow, paczka 0.3.4-t12 i jej SHA, decyzja numeru), tabela T0 / T1 / T2 / T10 / T11 / T12 / T13 z noca i 7ebb5cd, pelny pytest, odstepstwa (O<n> + Z2-N1 ... N8, w tym 5 wymienionych w zleceniu), T2 (e), sprawy wlasciciela (10.6) i koordynatora (K-a ... K-i) |
| (3) T13 na galezi 0 naruszen | potwierdzone wlasna proba | proba 19: HEAD a64b69d, naruszen 0 |
| (4) `git status --short` pusty, galaz wypchnieta | potwierdzone wlasna proba | proba 25 |
| pkt 5: dowody bez STL / baz / ZIP / > 1 MB, tylko `sha16`, `dowody_lf.py` jak w nocy | potwierdzone wlasna proba | proby 14-18, 20 |
| pkt 5: `README.md` - wolno dopisac wiersz | potwierdzone przegladem | pliku `odbior_koncowy/README.md` nie ma; nie zalozono go (10.8 pkt 2) - zgodne z zasada "tylko pliki z listy" |
| pkt 6: pierwszy wiersz `WERDYKT T10/T11`, porownanie z noca i 7ebb5cd, sprzatanie | potwierdzone przegladem + proba | pierwsze wiersze `WYNIK.md`; `T11\robocze\t11\` bez `eksport` i `Cyrkon`, `T10\robocze\` bez `Cyrkon`; kopie przerwanego przebiegu T11 (40 plikow) zostawione i opisane (K-g) |
| Uczciwosc: FAIL T2 (e) wprost, NOWE opisane, "nie zmierzono" | potwierdzone przegladem | 10.5 i wiersz T2; Z2-N1 ... N8; NIE ZMIERZONO: mapa w oknie 6 z 9, ramka W, pierwsza plytka na wolnym PC, `Dzien_skanera.cmd` po powrocie, granica dlugosci sciezki, przebieg na 1f231d9, T3-T9 na 0.3.3; zastrzezenia D1, D3 |

## 4. Zakres plikow i zasady

- Zmienione tylko pliki dozwolone: `RAPORT.md` (dopisane) i nowe `dowody_z2/**`; `dowody/` nocy, narzedzia, kod, plan - 0 zmian.
- Nietykalne (`match.py`, `inspect.py`, `plate.py`, `synth.py`, `uklad.py`, `modele_plytek/**`, progi, `raporty/testy_krawedz/**`): 0 zmian.
- ASCII / LF: dodane wiersze raportu i 171 plikow dowodow LF, 29 plikow `.cmd` / `.ps1` CRLF (zasada), nie-ASCII 0.
- Duze dane: 0 (najwiekszy plik 71,6 KB; `t10_metryki.json` 1585 KB poza repo, opisany).
- Dane osobowe: 0 trafien calych nazw (435 nazw, takze bazy testow 0.3.3); sciezki z kontem Windows `<uzytkownik>` tylko jako sciezka
  interpretera (jak w nocy) - to nie dane zlecen.
- Commity: 4, przedrostek `E3-ODBIOR2:`, po polsku bez diakrytykow, stopka `Co-Authored-By: Claude Opus 5.5`.

## 5. Do decyzji wlasciciela

1. (z uwagi D1 i K-c raportu) Czy proba 1 czesci B T12 (kod 6 przez dlugosc sciezki katalogu wybranego przez wykonawce, wbrew
   `<KB>` = `<ROB>\K_B` z planu) jest proba niewazna (T12 = ZAL z odstepstwem O2 + NOWE), czy FAIL czesci B wg litery planu
   (T12 = FAIL, FAIL 2). Program zachowal sie poprawnie (czytelna odmowa, nic nie zmienione); proba 2 dala 11 z 11.
2. (z 10.6, bez zmian) pozycje 1-5 sekcji 10.6 - fakty sprawdzone, liczby zgodne ze zrodlami.
