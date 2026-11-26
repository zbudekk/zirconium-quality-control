# Jak pracowac nad programem stanowiska na MSI i PC - dla nowego konta (stan 23.11.2026)

Ten plik zbiera zasady, ktore dotad byly rozrzucone po `CLAUDE.md`, pamieci poprzednich sesji i skryptach na PC.
Polecenia z sekcji 3 i 4 sprawdzone 23.11.2026 z MSI (konto PC `<konto-PC>`).

## 0. Wariant obowiazujacy w rundzie analizy 23.11.2026: sesje dzialaja NA PC

[usunieto w kopii: opis dostepu ssh]

- Katalog roboczy `<PC-katalog>` (konto `<konto-PC>`). Zasady z sekcji 3 o zapisie ("tylko `<PC-katalog>`",
  "nic nie instaluj, nie kasuj cudzych plikow", "nie obchodz bariery") obowiazuja takze lokalnie.
- Repo: klon `<PC-katalog>\qc` (`main`). `git fetch` i `git push` z PC dzialaja (23.11: `gh` zalogowany).
  Katalogu roboczego klonu nie zmieniaj; kazda sesja ma wlasny worktree `<PC-katalog>\qc-wt\analiza-s<n>` na
  galezi `analiza/s<n>` od `origin/analiza/plan`.
- [usunieto w kopii: opis dostepu ssh]
  `<PC-katalog>\koordynator\narz\py.cmd -m pytest testy\<plik> -q -p no:cacheprovider`.
- Powloka na PC to `cmd.exe` albo PowerShell 5.1 (bez `&&` w PowerShell).
- Czesci tego pliku o MSI (sekcja 2 - klon MSI i droga przez bundle, sekcja 3 - dostep przez ssh, sekcja 7)
  zostaja jako tlo i na wypadek pracy z MSI.

## 1. Co przeczytac i w jakiej kolejnosci

| Plik | Po co |
|---|---|
| `CLAUDE.md` (korzen repo) | stos, konwencje. UWAGA: sekcja "Testy i Blender na PC" jest nieaktualna (konto `<uzytkownik>`, klucz `<klucz-ssh>`) - obowiazuje sekcja 3 tego pliku |
| `Ramki/00_NADZOR_STAN.md` - KONIEC pliku | stan projektu, decyzje wlasciciela i koordynatora, sprawy otwarte. Plik jest dlugi i ma bardzo dlugie wiersze - czytaj od konca, fragmentami |
| `Ramki/stanowisko/README.md` | co robi program, jak sie go uruchamia, uklady plytek |
| `Ramki/stanowisko/opisy_modulow/*.md` | jeden plik na modul: wejscie, wyjscie, kryterium "dziala" - czytac przed kodem modulu |
| `Ramki/plan_etap3_pelna_aplikacja_2026-11-16.md` | plan etapu 3 (paczki A*, testy T0-T14) |
| `Ramki/etap3/plan_plytki_okragle_n1-n6_2026-11-21.md`, `propozycja_wariant_C_regula_ksztaltu_2026-11-21.md` | plytki okragle ramkowe i testowe, rozpoznanie kolo / kwadrat |
| `Ramki/etap3/odbior_koncowy/RAPORT.md` | wyniki testow T0-T13 na wydaniu 0.3.3 |
| `Ramki/etap3/testy_sprzet_2026-11-28/` | dokument pierwszych testow na sprzecie 28-29.11 |
| `Ramki/stanowisko/raporty/` | raporty paczek - liczby, czasy, sposob pomiaru |

Nazwy w projekcie: MSI = laptop-serwer, na ktorym dzialaja sesje Claude (malo RAM, WDAC blokuje czesc pakietow
Python); PC = komputer wlasciciela (32 watki; 23.11 `ram.cmd` pokazal 95 652 MB RAM, 77 040 MB wolne), jedyne miejsce, gdzie uruchamia sie testy i pomiary.
Wlasciciel = czlowiek; pisze z telefonu, krotko - odpowiadaj krotko, wynik na poczatku.

## 2. Repozytorium

- GitHub `mbuasm/qc` (prywatne). Glowna galaz `main`; 23.11 `origin/main` = b856b9e.
- MSI: klon `<MSI>\kod\qc`; sesje dostaja wlasne worktree w `.claude\worktrees\`. Worktree bywa
  w tyle za `origin/main` - zawsze najpierw `git fetch origin main` i sprawdz `git log -1 origin/main`.
- 23.11 na MSI `gh auth status` = token niewazny: `git fetch` i `git push` padaja ("could not read Password for
  https://mbuas@github.com"). Naprawia to tylko wlasciciel (`gh auth login -h github.com`); do tego czasu commity
  zostaja lokalnie na galezi, a w raporcie koncowym napisz, ze galaz nie jest wypchnieta.
- Plan i ta instrukcja sa na galezi `analiza/plan` (od `main` b856b9e; wypchnieta na GitHub z PC 23.11) -
  galezie sesji `analiza/s<n>` zakladaj od niej.
- Gdy `git fetch` nie dziala, aktualny `main` jest w klonie PC. Sprawdzona droga (tylko roznica od znanego commitu):
  ```
  [usunieto w kopii: opis dostepu ssh]
  git bundle verify main_pc.bundle
  git fetch main_pc.bundle main:refs/remotes/pc/main
  ```
  [usunieto w kopii: opis dostepu ssh]
- Praca zawsze na galezi od `origin/main` (analiza: `analiza/s<n>`; paczki kodu: `e3/<kod>`), potem PR.
  Paczki kodu scala sie po recenzji "do scalenia" i pelnym pytest 0 failed (zgoda wlasciciela 18.11); gdy tryb
  Auto odmowi `gh pr merge` albo rejestracji zadania Harmonogramu - nie ponawiaj, zostaw wlascicielowi.
  Raportow analizy sie nie scala.

## [usunieto w kopii: opis dostepu ssh]

- [usunieto w kopii: opis dostepu ssh]
  [usunieto w kopii: opis dostepu ssh]
- Zapis tylko w `<PC-katalog>` i we wlasnym profilu. Reszta dysku tylko do odczytu; odmowa zapisu to zamierzona
  bariera, nie blad. Nie obchodz jej (zadnych innych kont, kluczy, SMB, RDP, Tailscale). Potrzeba czegos wiecej
  na PC = zadanie dla wlasciciela w raporcie.
- Tylko zadania projektu qc. Nic nie instaluj i nie kasuj cudzych plikow na PC. Konto nie wylaczy PC.
- [usunieto w kopii: opis dostepu ssh]
  dluzszy skrypt wyslij jako plik. W poleceniu ssh pisanym w Bash znak `$` w cudzyslowie rozwija sie lokalnie.
- [usunieto w kopii: opis dostepu ssh]
- PC musi byc wlaczony i nie spac. Gdy nie odpowiada: sprawdz, czy MSI ma adres `<adres-IP>`
  (`Start-ScheduledTask serwer-siec-adres` po resecie karty), a gdy to nie pomaga - popros wlasciciela o wlaczenie
  przyciskiem (budzenie przez siec nie dziala po zwyklym zamknieciu).
- Dane z nazwiskami pacjentow (`Prace_test`, foldery zlecen) nigdy nie trafiaja do repo ani do raportow; w
  raportach projekt = 16 znakow SHA-256.

## 4. Testy programu na PC

Na koncie `<konto-PC>` nie ma `python` ani `py` w PATH. Uzywaj gotowego skryptu
`<PC-katalog>\koordynator\narz\py.cmd` (Python 3.12 wlasciciela + pakiety z jego `.venv` tylko do odczytu,
`PYTHONUTF8=1`, Qt bez okna, 2 watki na proces). Uruchamiac z katalogu `<kopia>\Ramki\stanowisko`.

```
[usunieto w kopii: opis dostepu ssh]
```
Wynik 23.11: `71 passed in 0.52s`.

- [usunieto w kopii: opis dostepu ssh]
- `<PC-katalog>\qc` to wspolny klon na `main` - w nim tylko odczyt i testy z `-p no:cacheprovider`; niczego tam nie
  zmieniaj i nie przelaczaj galezi. Do pracy na galezi: wlasne worktree
  `git -C <PC-katalog>\qc worktree add <PC-katalog>\qc-wt\<kod> <galaz>`, po pracy `git worktree remove`.
- Wlasne skrypty prob i logi: `<PC-katalog>\analiza\s<n>\` (zaloz), wyniki zabierz `tar` na MSI do
  `Ramki/analiza_kodu_2026-11-23/S<n>/`.
- Pelny pytest: 2506 testow (21.11), 1 proces; przy 1829 testach trwal 17-21 min, dzis dluzej. Niektore testy (silnik, pomiar czasu) padaja pod
  obciazeniem PC - przed uznaniem bledu powtorz sam plik na spokojnym PC. W tej rundzie analizy pelnego pytest
  nie uruchamiamy.
- Testy pomijane poza Windows (`skipif os.name != "nt"`) i testy wymagajace `Prace_test` - 9 pominiec to stan zwykly.

## 5. Limity zasobow

- PC (zasady po przeciazeniu 17.11: 0,4 GB wolnego RAM, 88 st. C - wtedy PC mial 32 GB; zasady zostaja do
  odwolania przez wlasciciela): sesje zwykle (pytest, recenzja, analiza) - 1 proces
  python naraz na sesje. Jedna sesja pomiarowa naraz moze liczyc w 6 procesach; dwie sesje pomiarowe naraz
  tylko po zgodzie wlasciciela. Proces pomiarowy bierze 1,5-4 GB.
- MSI: zadnych testow programu. Gdy cos musi sie policzyc na MSI: najwyzej 2 procesy python i tylko przy co
  najmniej 3 GB wolnego RAM.
- Limit konta Claude: sesja po kazdym dlugim poleceniu czyta caly swoj kontekst od nowa - dlugie testy uruchamiaj
  w tle z logiem do pliku i czytaj tylko koniec logu; prace mechaniczne zlecaj subagentom Opus 5.5 (`PLAN.md` p. 3).

## 6. Konwencje

- Pliki po polsku bez znakow diakrytycznych; skrypty PowerShell 5.1: ASCII, CRLF, bez `&&`.
- Zmiana stosu, modelu danych albo dystrybucji = najpierw opis dla wlasciciela.
- Progi `match` / `inspect` stroi sie w `ustawienia.toml`, nie w kodzie, i dopiero na prawdziwych skanach.
- Wagi w recenzjach i raportach: B (blokujace) / P (powazne) / D (drobne). Liczby zawsze z mianownikiem ("18 z 18").
- Rzeczy niesprawdzone bez sprzetu oznaczaj `[NIE SPRAWDZONE BEZ SPRZETU]`.
- Decyzja wlasciciela 15.11: nie zbieramy danych przed dostawa skanera (surowy STL od producenta, mikroskop,
  inny skaner) - nie proponowac.

## 7. Pulapki narzedzi na MSI

- Narzedzie Write moze nie dzialac na sciezce worktree z zamaskowana nazwa katalogu - pisz do katalogu
  roboczego sesji (scratchpad) i kopiuj przez Bash sciezka wzgledna.
- W Bash: `>nul` jest podmieniane na `>/dev/null`; `\b`, `\c` w `printf` / `sed` psuja sciezki Windows; dlugi
  heredoc z odwrotnymi apostrofami potrafi sie nie sparsowac - wtedy plik przez Write i `cp`.
- `git stash` jest wspolny dla wszystkich worktree - nie uzywaj; zamiast tego commit roboczy na wlasnej galezi.
- Nie dotykaj katalogow i worktree innych sesji w `<MSI>\kod` ani zadania `claude-rc`.
