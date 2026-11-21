# Pokaz G3 "po fakcie": instalacja, aktualizacja i powrot programu "Stanowisko" (wydanie 0.3.1)

Dla wlasciciela. Bramka G3 (plan etapu 3, sekcja 8, wariant B, decyzja DW11) to pytanie: czy program da sie wgrac na laptop
stanowiska z jednej paczki ZIP, bez internetu, i zaktualizowac jednym poleceniem. Ten dokument zastepuje pokaz na zywo:
opisuje to, co 21.11.2026 FAKTYCZNIE zrobiono i zobaczono w testach koncowych T0 (instalacja) i T12 (aktualizacja) na PC,
na koncie `<konto-PC>`. Niczego nie uruchamiano ponownie - kazda liczba i kazdy cytat pochodzi z pliku dowodu (sciezki
`dowody/...` sa wzgledem `Ramki/etap3/odbior_koncowy/`). Wyniki: T0 = ZAL z odstepstwem O1, T12 = ZAL z odstepstwem O2
(`RAPORT.md`, tabela 2). Na laptopie stanowiska nic jeszcze nie instalowano (sekcja 6).

## 1. Co to jest paczka wydania

| | | Zrodlo |
|---|---|---|
| Plik | `Stanowisko_0.3.1.zip`, jeden plik; lezy poza repozytorium (`<PC-katalog>\wydania\`) | `dowody/T0/WYNIK.md` |
| Rozmiar | 444 935 199 bajtow (424,3 MB); po rozpakowaniu 211 plikow, 462 922 182 bajtow | `dowody/T0/t0_sha256.txt`, `t0_kroki.md` |
| Suma SHA-256 | `f5affa81aea9969c6c42bf8e9e56ed6ad564dc948b15e92b8c7989383e24eec8` - ta sama w 4 miejscach: `certutil`, plik `.zip.sha256`, zlecenie testow, `Ramki/etap3/wydania/SHA256SUMS_wydania.txt` (zgodnosc 1 z 1) | `dowody/T0/t0_sha256.txt` |
| Z czego zbudowana | commit `main` 571e186cb8178209da670dde244dfc56bba5e300 | `dowody/T0/t0_zainstaluj_1.log` wiersz 2 |
| Zawartosc | `program\` (131 plikow: program, modele plytek, instrukcje), `kola\` (73 pakiety Pythona), `kola_testy\` (3), `zainstaluj.cmd`, `CZYTAJ.txt` (7 wierszy), `SHA256SUMS` (210 wierszy), `wydanie.json` | `dowody/T0/WYNIK.md` p. 1, `Ramki/etap3/wydania/README.md` |
| Sumy plikow | instalator sam liczy sumy wszystkich plikow paczki przed jakakolwiek zmiana - w T0: `zgodne 210 z 210` | `dowody/T0/t0_zainstaluj_1.log` wiersz 2 |
| Internet | niepotrzebny: pakiety instaluja sie tylko z katalogu `kola\` paczki (dowod w sekcji 6) | `dowody/T0/t0_pip_bez_sieci.txt` |
| Co trzeba miec wczesniej | Python 3.12 zainstalowany raz, recznie (sprawdzona wersja 3.12.10) | `Ramki/stanowisko/instrukcje/instalacja_i_aktualizacja.md` p. 1 |

## 2. Instalacja krok po kroku - tak, jak przebiegla w T0

Katalog instalacji w tescie: `<K>` = `<PC-katalog>\t0\odbior\Stanowisko` (na laptopie domyslnie `C:\Stanowisko`). Osoba
instalujaca trzyma sie jednej strony: `Ramki/stanowisko/instrukcje/instalacja_i_aktualizacja.md` (jest tez w paczce).

| Nr | Co zrobiono (polecenie) | Co bylo widac | Kod, czas | Plik dowodu |
|---|---|---|---|---|
| 1 | sprawdzenie sumy ZIP: `certutil -hashfile ...\Stanowisko_0.3.1.zip SHA256` | suma jak w tabeli wyzej, `CertUtil: -hashfile command completed successfully.` | - | `dowody/T0/t0_2.log` |
| 2 | rozpakowanie CALEJ paczki do `...\paczka_0.3.1` | 211 plikow | 2,9 s | `dowody/T0/t0_kroki.md` |
| 3 | `zainstaluj.cmd /katalog <K> /python <python.exe> /bez-sieci /bez-pauzy` - PIERWSZY raz | 7 z 9 krokow, na koncu `INSTALACJA: WSTRZYMANA ...` | **10**; 65,5 s (w tym pakiety ok. 40 s) | `dowody/T0/t0_zainstaluj_1.log`, `t0_3_czas.txt` |
| 4 | Notatnik: `<K>\ustawienia.toml` - 4 foldery w `[sciezki]` i `operatorzy` | zmienionych 5 wierszy (6-9 i 99) | - | `dowody/T0/t0_4_ustawienia_zmiany.txt` |
| 5 | to samo polecenie `zainstaluj.cmd ...` - DRUGI raz | 9 z 9 krokow, `INSTALACJA: GOTOWA ...` | **0**; 3,3 s | `dowody/T0/t0_zainstaluj_2.log`, `t0_5_czas.txt` |
| 6 | `<K>\Samokontrola.cmd --bez-sieci` | 21 wierszy, ostatni `SAMOKONTROLA: ZIELONA (ok 17, ostrzezenia 4)` | **0**; 2,0 s | `dowody/T0/t0_samokontrola.txt`, `t0_czasy_6_9.txt` |
| 7 | `<K>\Stanowisko.cmd --atrapa --zamknij-po 5`, potem `<K>\Stanowisko.cmd --zamknij-po 20` | okno programu (w tescie bez ekranu); w konsoli 0 wierszy; program zamknal sie sam | **0** i **0**; 6,5 s i 22,5 s | `dowody/T0/t0_start.txt`, `kody.txt` |

Calosc od startu pierwszej instalacji do konca drugiego startu programu: 02:48:30 - 02:51:16 = 2 min 46 s, razem z reczna
edycja ustawien (`dowody/T0/t0_3_czas.txt`, `t0_czasy_6_9.txt`). W tym czasie na PC biegla tez instalacja testu T12.

**Krok 3 - pierwsza instalacja (kod 10).** Doslowne wiersze konsoli z `dowody/T0/t0_zainstaluj_1.log`: wiersze 1-2, 7-8,
14-15, 40-46 (pominiete: Python, katalog, kopia bazy i 21 wierszy samokontroli; `...` = skrot dlugiego wiersza):

```
[1/9] Sumy SHA-256 paczki (<PC-katalog>\t0\odbior\paczka_0.3.1)...
      zgodne 210 z 210; wersja 0.3.1, commit 571e186cb817
[4/9] Ustawienia...
      zalozono ustawienia.toml ze wzoru (sciezki danych: <PC-katalog>/t0/odbior/Stanowisko/dane/...) - UZUPELNIJ foldery pracy w [sciezki] i osoby w [sesja] operatorzy
      instalacja 73 pakietow z kol paczki (bez sieci) - to trwa kilka minut...
      pakiety zgodne z lista zamrozona: 73 z 73
      SAMOKONTROLA: CZERWONA (ok 11, ostrzezenia 8, bledy 2)
Wersja 0.3.1 jest zainstalowana, ale jeszcze NIE jest wersja biezaca - samokontrola wskazala, co uzupelnic:
  BLAD folder_skanera: brak folderu eksportu skanera: C:/Aidite/Scandata - zaden skan nie trafi do programu; otworz plik ustawien ... i popraw klucz [sciezki] folder_eksportu_skanera ...
  BLAD folder_cyrkon: brak folderu projektow Cyrkon: C:/sciezka/do/OneDrive/Cyrkon - pula projektow jest pusta i skany czekaja bez wyniku; otworz plik ustawien ... i popraw klucz [sciezki] folder_cyrkon ...
Plik ustawien: <PC-katalog>\t0\odbior\Stanowisko\ustawienia.toml
CO ZROBIC: otworz plik ustawien w Notatniku, wpisz w [sciezki] foldery tej maszyny (z ukosnikami /) i osoby w [sesja] operatorzy, zapisz (UTF-8) i uruchom zainstaluj.cmd JESZCZE RAZ - pakiety nie instaluja sie drugi raz, to trwa kilka sekund.
INSTALACJA: WSTRZYMANA - uzupelnij ustawienia.toml i uruchom zainstaluj.cmd ponownie (kod 10)
```

To nie awaria: plik ustawien powstal ze wzoru i nie zna folderow tej maszyny. Program jest juz skopiowany, ale nie da
sie go uruchomic - w katalogu instalacji nie ma jeszcze `Stanowisko.cmd` (`dowody/T0/WYNIK.md`, p. 2).

**Krok 4 - uzupelnienie ustawien.** 5 wierszy: `folder_eksportu_skanera`, `folder_cyrkon`, `folder_prywatne`, `folder_millbox`
(np. `folder_cyrkon = "<PC-katalog>/t0/odbior/dane/Cyrkon"`) i `operatorzy = ["Technik A"]` - foldery testowe, osoba fikcyjna.

**Krok 5 - ponowna instalacja (kod 0, 3,3 s).** Wiersze, ktore roznia ja od pierwszej (`dowody/T0/t0_zainstaluj_2.log`,
wiersze 8, 11, 36, 38, 41):

```
      istniejacy ustawienia.toml zostaje bez zmian (SHA-256 4303ec76c74fb4a2...)
      wersja 0.3.1 jest juz zainstalowana i zgodna z paczka - pliki bez zmian
      SAMOKONTROLA: ZIELONA (ok 17, ostrzezenia 4)
      wersja biezaca: 0.3.1; poprzednia: brak
INSTALACJA: GOTOWA - wersja biezaca 0.3.1 (poprzednia: brak). Uruchamianie: <PC-katalog>\t0\odbior\Stanowisko\Stanowisko.cmd
```

**Krok 6 - samokontrola ZIELONA.** 17 x `OK`, 4 x `OSTRZEZENIE`, 0 x `BLAD` (`dowody/T0/t0_samokontrola.txt`). Ostrzezenia
swiezej instalacji: `baza` (powstaje przy pierwszym starcie), `ramka_wieczorna`, `ramka_poranna` (ramek nie ma), `excel`
(nieuruchomiony). Gdy baza juz istniala (po kroku `/testy`): `ok 18, ostrzezenia 3` (`dowody/T0/WYNIK.md`).

**Krok 7 - start programu.** Dwa starty, oba z kodem 0; w logu programu 0 wierszy `Traceback` (`dowody/T0/t0_start.txt`).
Program niczego nie pisze w konsoli - to okno. W tescie okna nikt nie widzial (sesja bez ekranu, zamkniecie samoczynne).

## 3. Aktualizacja 0.3.1 -> 0.3.2 i powrot - tak, jak w T12

Osobna instalacja `<K>` = `<PC-katalog>\t0\odbior_t12\Stanowisko`. Paczka 0.3.2 to ten sam program pod wyzszym numerem,
zbudowana tylko do tego testu (`dowody/T12/t12_sha256_zip.txt`). Kroki, godziny i czasy: `dowody/T12/t12_kroki.md`.

| Co | Polecenie (jedno) | Kod, czas | Ostatni wiersz konsoli | Plik dowodu |
|---|---|---|---|---|
| Aktualizacja | `zainstaluj.cmd /katalog <K> /python <python.exe> /bez-sieci /bez-pauzy` z rozpakowanej paczki 0.3.2 | **0**; 60,4 s | `INSTALACJA: GOTOWA - wersja biezaca 0.3.2 (poprzednia: 0.3.1). Uruchamianie: ...` | `dowody/T12/t12_zainstaluj_N1.log` |
| Powrot, odpowiedz `T` | `<K>\Wroc_do_poprzedniej.cmd /bez-pauzy` | **0**; 2,6 s | `POWROT: GOTOWY - wersja biezaca 0.3.1 (poprzednia: 0.3.2). Ponowne Wroc_do_poprzedniej.cmd wraca do 0.3.2.` | `dowody/T12/t12_wroc.log` |
| Powrot, odpowiedz `N` / brak odpowiedzi | to samo | **11** i **11**; 0,3 s i 0,2 s | `POWROT: ANULOWANY (kod 11) - wersja biezaca bez zmian: 0.3.2. ...` | `dowody/T12/t12_wroc.log` |
| Powrot bez pytania (do skryptow), 2 razy | `<K>\Wroc_do_poprzedniej.cmd /tak /bez-pauzy` | **0** i **0**; 3,1 s i 3,3 s | `POWROT: GOTOWY - ...` | `dowody/T12/t12_wroc_tak.log` |

Pytanie przy powrocie brzmi doslownie: `Powrot z wersji 0.3.2 do wersji 0.3.1. Kontynuowac? [T/N]:`; po odpowiedzi `T`
skrypt wypisuje `schemat zgodny - baza zostaje bez zmian` (`dowody/T12/t12_wroc.log`, wiersze 15 i 17).

Co aktualizacja i powrot ZACHOWALY (liczby: `dowody/T12/WYNIK.md`, tabela kryterium):

- **Ustawienia:** suma SHA-256 pliku `ustawienia.toml` identyczna 4 z 4 razy - przed, po 0.3.2, po powrocie, na koncu
  (`dowody/T12/t12_ustawienia_sumy.txt`); instalator: `istniejacy ustawienia.toml zostaje bez zmian`.
- **Dane:** `user_version` bazy 1 przez caly czas; zdarzenia 2 -> 4 -> 6 -> 8 (po 2 na kazdy start programu, nic nie ubylo);
  powrot nie zmienil pliku bazy (ta sama suma przed i po powrocie).
- **Kopia bazy:** aktualizacja sama zrobila 1 kopie w `dane\kopie\` - `sprawdzona (quick_check ok, schemat bazy 1; program
  0.3.2: 1)` (`dowody/T12/t12_zainstaluj_N1.log`, wiersz 17); 86016 bajtow jak baza, ta sama tresc (porownanie bez naglowka - O2).
- **Stara wersja zostaje obok nowej:** `Wersje.cmd` po aktualizacji: `0.3.1 ... poprzednia`, `0.3.2 ... BIEZACA`; po powrocie
  odwrotnie (`dowody/T12/t12_wersje_przed_po.txt`). **Program dziala po kazdej zmianie:** samokontrola ZIELONA (ok 18,
  ostrzezenia 3) 3 z 3 razy i start programu z kodem 0 3 z 3 razy (po 0.3.2, po powrocie, na koncu).

**Przypadek trudniejszy: nowa wersja zmienia budowe bazy (T12 czesc B).** Wydania 0.3.1 i 0.3.2 maja te sama budowe bazy,
wiec do proby zbudowano paczke PROBNA `0.3.9-migracja` (schemat 1 -> 2) - to jest odstepstwo O2. Przebieg
(`dowody/T12/t12_migracja_B.md`; kody 11 z 11 zgodne z oczekiwanymi):

1. Aktualizacja do wersji probnej: kod 0, 78,7 s. Instalator zrobil kopie bazy sprzed zmiany (86016 bajtow, tresc = baza).
   Baza zostaje nietknieta do pierwszego startu nowej wersji; dopiero program ja zmienia (`user_version` 1 -> 2).
2. `Wroc_do_poprzedniej.cmd /tak /bez-pauzy`: **kod 8, niczego nie zmieniono** (`dowody/T12/t12_B_6.log`, wiersze 3, 6-10):

```
      UWAGA: wersja 0.3.9-migracja zmienila schemat bazy - wersja 0.3.1 tej bazy NIE otworzy.
      Po przywroceniu z bazy roboczej zniknie wszystko, co zapisano po tej chwili: 3 wpisow w 1 tabelach.
        tabela zdarzenia: 4 w kopii, 7 teraz (+3)
BLAD: powrot do 0.3.1 wymaga przywrocenia kopii bazy sprzed aktualizacji
CO ZROBIC: Jesli zgadzasz sie na utrate wpisow wymienionych powyzej, uruchom: Wroc_do_poprzedniej.cmd /przywroc-kopie (biezaca baza zostanie odlozona do dane\kopie, nie skasowana). Niczego nie zmieniono.
POWROT: NIEUDANA (kod 8) - wersja biezaca bez zmian: 0.3.9-migracja
```

3. `Wroc_do_poprzedniej.cmd /przywroc-kopie /bez-pauzy`: kod 0, 3,2 s; `dotychczasowa baza odlozona jako
   kopie/stanowisko_odlozona_v2_20261121_025935.sqlite`; `POWROT: GOTOWY - wersja biezaca 0.3.1 (poprzednia: 0.3.9-migracja)`
   (`dowody/T12/t12_B_7.log`). Baza wrocila do stanu sprzed aktualizacji (zdarzenia 7 -> 4).

Dla technika: po aktualizacji zmieniajacej baze powrot to **2 polecenia** (pierwsze tylko ostrzega), a wszystko, co zapisano po
aktualizacji, **przepada** (w probie 3 wpisy; liczba podana przed zgoda; baza nowej wersji odlozona, nie skasowana) - pytanie 2 w sekcji 7.

## 4. Co robi samokontrola i kiedy instalator NIE przelacza wersji

Samokontrola (`Samokontrola.cmd`, takze krok 7 instalatora i krok 4 powrotu) to 21 sprawdzen; kazde daje wiersz `OK`,
`OSTRZEZENIE` albo `BLAD` z rada, co zrobic (`dowody/T0/t0_samokontrola.txt`): `python`, `pakiety` (11 z 11), `moduly` (27 z
27), `ustawienia`, `operatorzy`, `folder_skanera`, `folder_cyrkon`, `folder_prywatne`, `folder_millbox`, `dane_folder`,
`dane_miejsce`, `dane_polozenie` (dane poza OneDrive / SharePoint), `baza`, `modele` (8 z 8 ukladow plytek), `pula`,
`pamiec_puli`, `ramka_wieczorna`, `ramka_poranna`, `excel`, `egzemplarz` (czy program juz nie dziala), `sumy` (pliki programu
130 z 130). W testach: 0 bledow = ZIELONA (ostrzezenia nie przeszkadzaja), 2 bledy = CZERWONA.
Zasada instalatora: nowa wersja staje OBOK starej i jest przelaczana dopiero po zielonej samokontroli (krok 8 z 9).

| Sytuacja | Co widac | Wersja biezaca | Czy pokazane w testach |
|---|---|---|---|
| pierwsza instalacja, bledy tylko w ustawieniach | `INSTALACJA: WSTRZYMANA ...` (kod 10) | brak - programu nie da sie jeszcze uruchomic | TAK: T0 1 raz, T12 3 razy (`dowody/T0/kody.txt`, `dowody/T12/WYNIK.md`) |
| powrot bez odpowiedzi `T` | `POWROT: ANULOWANY (kod 11)` | bez zmian | TAK: T12 2 razy (`dowody/T12/t12_wroc.log`) |
| powrot po zmianie bazy bez zgody na utrate wpisow | `POWROT: NIEUDANA (kod 8)` | bez zmian | TAK: T12 czesc B 1 raz (`dowody/T12/t12_B_6.log`) |
| czerwona samokontrola przy aktualizacji (kod 1), zle sumy paczki (3), brak Pythona (4), program uruchomiony (5), brak miejsca i inne (6), zly plik ustawien (7) | `INSTALACJA: NIEUDANA (kod N) - ...`, wyzej `BLAD:` i `CO ZROBIC:` | wg instrukcji p. 6: bez zmian, dziala dalej stara wersja | NIE - w T0 i T12 te kody nie wystapily; opis tylko z instrukcji |

## 5. Uklad katalogow po instalacji

Wszystko lezy w jednym katalogu (w tescie `<K>`; na laptopie domyslnie `C:\Stanowisko`), poza folderami OneDrive:

```
<K>\
  Stanowisko.cmd  Samokontrola.cmd  Wroc_do_poprzedniej.cmd  Wersje.cmd  Polecenie.cmd   - powstaja po zielonej instalacji
  wersja_biezaca.txt  wersja_poprzednia.txt     - wskaznik wersji: numer, np. 0.3.2 i 0.3.1
  ustawienia.toml                               - foldery tej maszyny, osoby; aktualizacja go NIE zmienia
  dziennik_instalacji.txt                       - zapis kazdej instalacji i powrotu
  wersje\0.3.1\  wersje\0.3.2\                  - kazda wersja osobno: program\, venv\ (wlasne pakiety), pip.log
  dane\                                         - POZA katalogiem wersji; aktualizacja i powrot ich nie ruszaja
    stanowisko.sqlite  logi\  pula_cache\  do_dofrezowania_biezaca.csv  ramki_laptop_id.txt
    kopie\                                      - kopie bazy robione przy aktualizacji i bazy odlozone przy powrocie
```

Zrodla: `dowody/T0/WYNIK.md` p. 2, 4, 6 i "Uwagi o srodowisku", `dowody/T12/t12_A2_baza_po_aktualizacji.txt` (wskazniki
wersji, `dane\kopie`). Instalator wymaga na wersje ok. 1860 MB wolnego miejsca (`dowody/T0/t0_zainstaluj_1.log`, wiersz
11); wg instrukcji p. 5 wersja zajmuje ok. 1,5 GB. Stare wersje i kopie bazy nie kasuja sie same.

## 6. Czego pokaz NIE obejmuje (ograniczenia)

- **O1 - to nie bylo czyste konto ani komputer bez sieci.** "Czyste konto" = swiezy katalog na koncie `<konto-PC>` tego
  samego PC; sieci fizycznie nie odcinano. Dowod, ze instalator nie siegal do internetu - 2 wiersze `pip.log`:
  `Ignoring indexes: https://pypi.org/simple` i `Looking in links: <PC-katalog>\t0\odbior\paczka_0.3.1\kola`, oraz wiersz dziennika
  `instalacja 73 pakietow z kol paczki (bez sieci)` (`dowody/T0/t0_pip_bez_sieci.txt`); wierszy `Downloading`: 0 (`dowody/T0/WYNIK.md`).
- **Opcja `/python <sciezka>` byla na tym PC obowiazkowa** (Python lezy w profilu innego konta). Nie sprawdzono: szukania
  Pythona przez instalator, instalacji Pythona z python.org, dwukliku w Eksploratorze i pauzy na koncu (uzyto `/bez-pauzy`),
  opcji `/skrot`, rozpakowania przez "Wyodrebnij wszystkie" (rozpakowano poleceniem) - `dowody/T0/WYNIK.md`.
- **Okna programu nikt nie ogladal** (sesja bez ekranu, `offscreen`). **Migracja bazy pokazana na paczce probnej** (O2).
- **Kody bledow instalatora 1-7 i 9 nie wystapily** w T0 i T12 (sekcja 4). Plik testow automatycznych instalatora
  `testy/test_instalacja.py` nalezy do pelnego pytest T1 (2213 passed, 0 failed) - to nie jest pokaz na paczce.
- **Laptop stanowiska:** nic nie instalowano; antywirus i uprawnienia firmowego laptopa, wolniejszy dysk, skalowanie
  ekranu, folder OneDrive "Cyrkon" - nieznane. To wizyta przy laptopie z `ODLOZONE.md` (otwarte 4-6); T15-T17 odlozone.
- **Obrazki:** w dowodach T0 i T12 sa tylko pliki tekstowe - zrzutow ekranu instalacji nie ma i nowych nie robiono. Gotowe
  obrazki ekranow programu (nie instalatora): `Ramki/etap3/t14/obrazki/` (`wieczor_ekran.png`, `wieczor_praca.png`,
  `rano_ekran.png`, `rano_kandydaci.png`) oraz obrazki wpisane w `Ramki/stanowisko/instrukcje/wieczor.html` i `poranek.html`.

## 7. Pytania do wlasciciela wynikajace z G3

1. Czy opisany przebieg (paczka ZIP; 2 uruchomienia `zainstaluj.cmd` z edycja `ustawienia.toml` pomiedzy nimi; ok. 3 minuty)
   przyjmujesz jako sposob wgrywania programu - czyli czy G3 jest zaliczona "po fakcie", czy chcesz zobaczyc ja na zywo / na laptopie?
2. Czy powrot po aktualizacji zmieniajacej baze moze zostac: 2 polecenia i utrata wpisow zrobionych po aktualizacji (`RAPORT.md` 4a poz. 4)?
3. Czy przyjmujesz odstepstwo O1 (swiezy katalog zamiast czystego konta, siec nieodcieta) do czasu instalacji na laptopie
   (`RAPORT.md` 4a poz. 15), czy zlecic probe na nowym koncie Windows z odlaczona siecia?
4. Kto wpisze foldery w `ustawienia.toml` na laptopie (eksport skanera, Cyrkon, Prywatne, MillBox, osoby) i jakie to sciezki?
5. Czy zlecic sprawdzenie tego, czego T0 nie objal: dwuklik i pauza, `/skrot`, Python bez `/python` (`RAPORT.md` 4a poz. 15)?
6. Kanal przekazania paczki (424 MB): pendrive, OneDrive czy katalog wydan na serwerze (plan etapu 3, sekcja 8)?
7. Stare wersje (ok. 1,5 GB kazda) i kopie bazy nie kasuja sie same - czy tak ma zostac (`RAPORT.md` sekcja 8, decyzja nr 8)?
