# Raport recenzenta PR R59 - runda 3 (recenzja przyrostowa, subsesja R59-R)

Data: 2026-11-16. Recenzent: R59-R (Opus 5.5), tylko odczyt. Zakres: jeden commit `dbd348e..6be6c92` (R59-K: D1 i D2 z rundy 2).
Pliki: `Ramki/narzedzia/zbuduj_pakiet_R59.sh` (712 -> 763 linii, SHA 15b1133a = log) i `Ramki/R59_odbior/logi/R59K_poprawka_D1_D2.txt` (nowy).
Metoda: diff i plik w HEAD przez `git show`. Testy w scratchpadzie: (a) harness = linie 1-190 skryptu HEAD (bez zapisow na dysk; tylko `cd`
podmienione na prawdziwy `Ramki` worktree albo sztuczny `Ramki` bez gita) - 60 przypadkow + 7 dodatkowych; (b) blok zamiany (linie 723-734)
na sztucznych katalogach - 4 przypadki + semantyka `mv -T`; (c) trap EXIT przy SIGINT/SIGTERM na skrypcie zabawce; (d) mechaniczne porownanie
heredokow i linii base/head (Python). Calego `zbuduj_pakiet_R59.sh` nie uruchamialem.

## 0. Werdykt

**do scalenia** - B 0 / P 0 / D 1 (D1 moze poczekac do wzoru R6x; nie jest potrzebna przed G2).

D1 i D2 z rundy 2 sa zalatwione. Straznik odrzuca wszystkie przypadki z karty przed jakakolwiek zmiana na dysku, porownanie jest w obie
strony, zamiana idzie przez przemianowanie z przywroceniem, nowych drog do `rm -rf` prawdziwych katalogow nie ma. Udokumentowane wywolania
(tryb wlasciwy, `--calosc` w scratchpadzie, `--proba` poza repo) przechodza. Tresc plikow pakietu i plikow do wgrania nie zmienila sie ani o bajt.

## 1. Uwagi

| Nr | Waga | Plik:linia | Co | Dlaczego | Poprawka |
|---|---|---|---|---|---|
| 1 | D (moze poczekac, wzor R6x) | `zbuduj_pakiet_R59.sh:315`, `:734`; `.gitignore:2` | Komunikat odzysku i pozostalosci po zamianie. (a) :315 przy istniejacym `<cel>.stary_R59` kaze "sprawdz go i usun recznie". Po przerwaniu miedzy :731 a :732 (Ctrl+C, zamkniete okno) albo po nieudanym `mv` w `przywroc` (:728) `D` nie istnieje, a `STARY` to jedyna kopia poprzedniego pakietu na dysku - doslowne wykonanie komunikatu ja kasuje. (b) Po nieudanym `rm -rf "$STARY"` (:734, galaz UWAGA, kod wyjscia 0) w trybie wlasciwym zostaje `Ramki/Ramki_pakiet.stary_R59/`, a przy bledzie zamiany `Ramki/Ramki_pakiet.budowa_R59*/`; `.gitignore` obejmuje tam tylko `*.stl`, wiec `git add -A` wciagnie README, PDF i JSON do commita. | Nic nie ginie naprawde (Ramki_pakiet jest w gicie, R57 w `archiwum`, pakiet jest powtarzalny), wiec tylko drobna. Ryzyko: reczne sprzatanie wedlug komunikatu i przypadkowy commit pozostalosci. | (a) :315: "jesli brak $D - przywroc: mv -T $STARY $D; jesli $D jest - usun $STARY"; (b) w UWAGA :734 dopisac "nie commitowac", albo przy najblizszej edycji wzorca dodac do `.gitignore` `Ramki/Ramki_pakiet.stary_R*/` i `Ramki/Ramki_pakiet.budowa_R*/`. |

## 2. Pkt 1 - D1 (straznik, zamiana)

Kolejnosc: caly straznik (:141-190) dziala przed szukaniem Pythona (:192) i przed krokiem 0 (:309). Pierwsza zmiana na dysku to `mkdir -p "$W"`
(:316, tylko proba) albo `mkdir -p "$CALOSC"` (:318). `--proba`: katalog i policzone cele `D`, `W`, `T`, `TW`, `STARY` sa porownane z
`ZAKAZANE` = `Ramki_pakiet`, `../Ramki_do_wgrania`, `archiwum`, `..`, `--show-toplevel`, glowna kopia z `--git-common-dir`, w obie strony
(`straznik`, :119-125); do tego katalog proby musi byc poza drzewem git. Tryb wlasciwy przyjmuje tylko `Ramki_pakiet` (sprawdzone w obie strony,
:153), wiec `D` zawsze = `Ramki_pakiet`; `D/T/TW/STARY` porownane z `archiwum` i `../Ramki_do_wgrania`. `--calosc`: `ZAKAZANE` w obie strony,
nie w `D/W/T/TW/STARY`, poza drzewem git, a w probie w katalogu proby.

Wyniki harnessu (prawdziwy worktree; REPO = `..`, worktree, `<kod>/qc`) - 65 z 67 zgodnie z oczekiwaniem; 2 rozjazdy po mojej
stronie: harness nie przekazal `PROBA=1` (powtorzone poprawnie - zgodne) i bledne oczekiwanie przy zlaczu do `Ramki_pakiet` (pkt 6).
Bledu w skrypcie zaden przypadek nie pokazal:
- odmowa (41): `--proba` `.`, `./`, `..`, `../`, `../..` (worktrees w glownej kopii), glowna kopia `/c/` i `C:/x`, katalog `<kod>` (zawiera repo),
  `C:\...\Ramki`, `C:\...\worktree\tmp`, `C:/`, `/`, `/c/Users`, `Ramki_pakiet`, `archiwum/x`, `../Ramki_do_wgrania`, `Ramki_pakiet/..`;
  zlacze (junction) -> `Ramki` i podkatalog przez zlacze; `<proba>/Ramki_pakiet` = zlacze -> prawdziwy `Ramki_pakiet` (cel D);
  `<proba>/Ramki_pakiet.stary_R59` = zlacze -> `archiwum` (cel STARY); `<proba>/Ramki_do_wgrania` = zlacze -> prawdziwy (cel W); inne repo git;
  `PROBA=1` z `.`. Tryb wlasciwy z `archiwum/Ramki_pakiet_przed_R59_2026-11-16`, `.`, katalogiem w scratchpadzie. `--calosc` `../x`,
  `<kod>/qc/x`, `<kod>`, inne repo git, przez zlacze do `Ramki`, `/`, `C:/` i `C:` (po `${2%/}`); w probie: poza katalogiem proby,
  w `<proba>/Ramki_pakiet`, w `<proba>/Ramki_do_wgrania`, w repo. Brak katalogu proby, dwa katalogi.
- przepuszcza (18 + 1 z pkt 6): `--proba` w scratchpadzie w postaci `/c/` krotkiej (8.3), `C:/` z koncowym `/`, dlugiej, z `\`, wzglednej `../../..` od `Ramki`,
  `PROBA=1`; wlasciwy bez argumentu, `Ramki_pakiet`, `Ramki_pakiet/`, `./Ramki_pakiet`, `C:\...\Ramki_pakiet`; `--calosc` w scratchpadzie
  (4 postaci) i `C:\serwer\wydania-przychodzace\qc`; proba z `--calosc` w katalogu proby i rownym katalogowi proby.
  Sztuczny `Ramki` bez gita: `git rev-parse` poza repo nie przerywa skryptu (`if`), REPO = `..`; 6 z 6 zgodnie.
- `set -euo pipefail`: `w_katalogu` i `w_drzewie_git` sa wolane tylko w `if` / po lewej stronie `||`; bloki `git rev-parse` (:145-146) tez w `if`.
  W glownej kopii `--git-common-dir` z `Ramki` daje `../.git` (wzgledne do katalogu biezacego) - `cd` dziala, wynik = toplevel.
- Zamiana (blok :723-734 wyciety, sztuczne katalogi): poprzedni jest / brak x nowy dobry / zly - 4 z 4 zgodnie (dobry: D = nowy, STARY skasowany;
  zly: poprzedni wraca do D, nowy w T, STARY brak). `mv -T` w Git Bash: brak celu = przemianowanie; cel niepusty = "Directory not empty", nic nie
  trafia do srodka; cel pusty = zastapiony. Pod `cmd || przywroc` `set -e` nie przerywa przed przywroceniem.
- Przerwanie: trap EXIT dziala przy SIGINT do grupy procesow (jak Ctrl+C, kod 130) i przy SIGTERM (143). Przed :723 Ctrl+C sprzata `T`/`TW`,
  pakiet i katalog do wgrania nietkniete. Od :723 (`SPRZATAJ=0`): okno :731-:732 zostawia `D` brak, `STARY` = poprzedni, `T` = nowy - nastepny
  przebieg odmawia na :315 przed `rm -rf "$T"` (:335), wiec nic nie kasuje; komunikat - uwaga 1. Okno po :732 / w trakcie :734 i :735: stan spojny
  (nowy w D), kolejny przebieg odmawia albo wymaga `--nadpisz`.
- Kasowanie: nowe `rm -rf` tylko `"$STARY"` (:734), ktory nie moze istniec przed przebiegiem (:315) i powstaje wylacznie z `mv -T "$D"` (:731);
  `STARY` w probie przechodzi przez straznik (zlacze do `archiwum` odrzucone). `rm -rf "$D"` usuniete. `rm -rf "$T" "$TW"` bez zmian.
- Istniejacy `<cel>.stary_R59` (takze zepsute dowiazanie, `-L`): odmowa w kroku 0 przed `mkdir`.

## 3. Pkt 2 - udokumentowane wywolania

- `bash narzedzia/zbuduj_pakiet_R59.sh [--nadpisz] [--calosc <scratchpad>/r59_serwer]` z `Ramki` i `bash Ramki/narzedzia/...` z katalogu glownego
  (skrypt sam przechodzi do `Ramki`): straznik przepuszcza; scratchpad i `C:\serwer` nie sa w zadnym drzewie git (`git rev-parse` = 128),
  katalog domowy tez nie. Planowana droga (ZIP w scratchpadzie, potem kopia do skrzynki innym krokiem) nie jest zablokowana; bezposrednie
  `--calosc C:\serwer\wydania-przychodzace\qc` tez by przeszlo.
- `--proba <katalog poza repo> [--calosc <katalog w probie>]`: przechodzi.
- Usuniety argument `[katalog_pakietu]` trybu wlasciwego: `git grep` - poza logiem i raportem rundy 2 nikt go nie uzywa.
- Pelne przebiegi (a) proba i (b) wlasciwy `--nadpisz --calosc` oraz sym1-sym3 - tylko z logu wykonawcy (kopia worktree), nie powtarzalem.

## 4. Pkt 3 - D2 (ASCII)

- Heredoki: 6 w base i 6 w head (`PYEOF`, README.txt, INSTRUKCJA_PAKIET, DO_WGRANIA x2, NA_SERWER) - ciala identyczne bajtowo (0 roznic).
- Linie z tresca poza heredokami, nadal nie-ASCII i niezmienione: :85 (`PDFY`, nazwy plikow z pauza), :490-491 (wiersze plytek), :496, :498
  (`ZNAK_TXT`, `ZNAK_MD`), :648 (domyslny `FOLDER`). Linie nie-ASCII: 126 -> 49 (43 w heredokach + 6) = log.
- 77 zmienionych linii D2: 61 samych komentarzy, 10 linii kod + komentarz (zmieniona tylko czesc po `#`, kod ASCII bez zmian), 1 komunikat
  na ekran (:755 `echo "Pakiet gotowy..."`, bez przekierowania), 5 linii naglowka zmienionych razem z opisem D1. Dodane linie nie-ASCII: 0.

## 5. Pkt 4 - zakres i higiena

- Commit = 2 pliki (A log, M skrypt); wszystkie zmiany w skrypcie to straznik, zamiana, naglowek / `--help` i komunikaty - pracy obok brak.
- LF (`i/lf w/lf`), 0 CR, 0 znakow sterujacych w obu plikach; `bash -n` OK; log w ASCII.
- Log: sciezki tylko jako `<P>`, `<kod>`, `<worktree>`. Slowa >= 4 liter z nazw w `Prace_test` (44): w logu, skrypcie, opisie commita i liniach
  dodanych 1 trafienie - slowo pospolite; nazwisk / nazw zlecen 0.
- Worktree: `git status` czysty, brak `Ramki_pakiet.budowa_R59*` / `.stary_R59`.

## 6. Informacje (nie liczone)

- `w_drzewie_git`: repo, ktore git odrzuca jako "dubious ownership" (`safe.directory`), daje kod != 0, czyli "poza git". Repo qc chroni i tak
  jawna lista `ZAKAZANE` (`..` zawsze). Gdyby skrypt uruchomilo konto inne niz wlasciciel worktree, z REPO wypadlaby glowna kopia `<kod>/qc`
  (zostaje `..`). Na MSI tak nie jest.
- Tryb wlasciwy z celem bedacym zlaczem do `Ramki_pakiet` przechodzi (to ten sam katalog), a `D` i tak = `Ramki_pakiet` - bez skutku.
- Straznik kosztuje okolo 6 s na MSI (wiele wywolan `cygpath` / `realpath` / `git`) - przy przebiegu 1-2 min bez znaczenia.

## 7. Czego nie sprawdzilem

- Calego `zbuduj_pakiet_R59.sh` (zmienia repo); pelne przebiegi i sym1-3 tylko z logu. Nie wiem, czy kopia w przebiegach pozytywnych a/b miala `.git`;
  moj harness sprawdzil straznik z prawdziwym gitem dla tych samych wywolan.
- Galaz nieudanego `rm -rf "$STARY"` - tylko czytanie (blokady pliku z FILE_SHARE_DELETE nie odtwarzalem).
- Ctrl+C w prawdziwym przebiegu - tylko trap na skrypcie zabawce i analiza okien w kodzie.
- PC (inny uklad katalogow, `..` = katalog nad `Ramki`), git < 2.5, "dubious ownership" - nie symulowane.
- Dane osobowe - tylko slowa >= 4 liter z nazw w `Prace_test`.
