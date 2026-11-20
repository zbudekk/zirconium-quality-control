# Instalacja i aktualizacja programu "Stanowisko" - jedna strona dla osoby instalujacej

Paczka wydania to jeden plik `Stanowisko_<wersja>.zip` (ok. 430 MB). Internet nie jest potrzebny. Instalacja niczego nie
zmienia w systemie: wszystko lezy w jednym katalogu (domyslnie `C:\Stanowisko`), poza folderami OneDrive / SharePoint.

## 1. Raz, recznie: Python 3.12

Zainstaluj Pythona 3.12 (64-bit) z python.org - opcje domyslne wystarcza. Inne wersje Pythona nie przeszkadzaja.

## 2. Instalacja

1. Rozpakuj CALA paczke (prawy klawisz -> "Wyodrebnij wszystkie") do dowolnego katalogu, np. `C:\Paczki\Stanowisko_0.3.0`.
2. Uruchom w rozpakowanym katalogu `zainstaluj.cmd` (dwuklik). Opcje, gdy trzeba - w wierszu polecen:
   `zainstaluj.cmd /katalog D:\Stanowisko` (inny katalog), `/python C:\...\python.exe` (wskazany Python 3.12),
   `/skrot` (skrot "Stanowisko" na pulpicie), `/bez-sieci` (samokontrola bez proby polaczenia z ramkami).
3. Zobaczysz 9 krokow: sumy paczki, Python, katalog, ustawienia, katalog wersji (pakiety - kilka minut), kopia bazy,
   samokontrola, przelaczenie wersji, skrot. Ostatni wiersz mowi wszystko: `INSTALACJA: GOTOWA - wersja biezaca ...`
   albo `INSTALACJA: NIEUDANA (kod N) - wersja biezaca bez zmian`, a nad nim `BLAD: ...` i `CO ZROBIC: ...`.
4. PIERWSZA instalacja konczy sie zwykle `SAMOKONTROLA: CZERWONA` (kod 1): plik `C:\Stanowisko\ustawienia.toml` powstal ze
   wzoru i nie zna jeszcze folderow tej maszyny. Otworz go w Notatniku, w sekcji `[sciezki]` wpisz foldery (eksport skanera,
   Cyrkon, Prywatne, MillBox - z ukosnikami `/`), w `[sesja] operatorzy` osoby, zapisz i uruchom `zainstaluj.cmd` JESZCZE RAZ
   - pakiety nie instaluja sie drugi raz, trwa to kilka sekund. Wierszy `baza`, `wyniki`, `logi`... nie zmieniaj.
5. Program uruchamia `C:\Stanowisko\Stanowisko.cmd` (albo skrot). Obok: `Samokontrola.cmd` (sprawdzenie w kazdej chwili),
   `Wroc_do_poprzedniej.cmd`, `Wersje.cmd`. Dane programu: `C:\Stanowisko\dane\`; zapis instalacji: `dziennik_instalacji.txt`.

## 3. Aktualizacja

Zamknij program. Rozpakuj nowa paczke i uruchom JEJ `zainstaluj.cmd` (z tym samym `/katalog`, jesli byl inny niz domyslny).
Instalator sam: zostawia `ustawienia.toml` i `dane\` bez zmian, robi kopie bazy w `dane\kopie\`, zaklada nowa wersje obok
starej, sprawdza ja samokontrola i dopiero wtedy przelacza. Gdy cos sie nie uda, dziala dalej stara wersja.

## 4. Powrot do poprzedniej wersji

Zamknij program i uruchom `C:\Stanowisko\Wroc_do_poprzedniej.cmd`. Jesli nowsza wersja zmienila baze, zobaczysz ostrzezenie
(kod 8): ile wpisow i od kiedy przepadnie. Zgoda = `Wroc_do_poprzedniej.cmd /przywroc-kopie` (wraca kopia bazy sprzed
aktualizacji; baza biezaca jest odkladana do `dane\kopie\`, nie kasowana). Brak zgody = zostajesz przy nowej wersji.

## 5. Stare wersje

Nie sa kasowane same (kazda to ok. 1,5 GB w `wersje\`). Lista: `Wersje.cmd`. Usuniecie: `Wersje.cmd /usun <wersja>` -
tylko wersji, ktora nie jest ani biezaca, ani poprzednia.

## 6. Komunikaty instalatora i co zrobic

| Kod | Komunikat (`BLAD: ...`) | Co zrobic |
|---|---|---|
| 1 | samokontrola ... zglosila bledy | popraw to, co wskazuja wiersze `BLAD` (zwykle foldery w `ustawienia.toml`), uruchom `zainstaluj.cmd` ponownie |
| 2 | samokontroli ... nie dalo sie wykonac | popraw przyczyne podana nad komunikatem (zwykle plik `ustawienia.toml`), uruchom ponownie |
| 3 | sumy SHA-256 paczki niezgodne / w paczce brakuje ... / blad wydania / wersja juz zainstalowana z INNEJ budowy | paczka uszkodzona albo niepelna: pobierz i rozpakuj ja ponownie w calosci; "blad wydania" i "inna budowa" zglos budujacemu paczke (potrzebna paczka z nowym numerem wersji) |
| 4 | nie znaleziono Pythona 3.12 / zla wersja Pythona / brak Pythona | zainstaluj Pythona 3.12 (64-bit) albo wskaz go: `zainstaluj.cmd /python <sciezka>\python.exe` |
| 5 | program "Stanowisko" jest uruchomiony | zamknij program i uruchom polecenie ponownie |
| 6 | za malo miejsca na dysku / pip zakonczyl sie bledem / instalacja przerwana / katalog w folderze synchronizowanym / sciezka za dluga / nie mozna pisac | zwolnij miejsce albo wybierz inny katalog (`/katalog`, krotki, poza OneDrive) i uruchom ponownie - niedokonczona wersja sprzata sie sama |
| 7 | plik ustawien nie przechodzi kontroli / sciezki wzgledne w [sciezki] | popraw `ustawienia.toml` tak, jak podaje komunikat (sciezki danych musza byc bezwzgledne, np. `C:/Stanowisko/dane/...`) |
| 8 | powrot ... wymaga przywrocenia kopii bazy / nie ma kopii bazy | przeczytaj ostrzezenie; zgoda: `Wroc_do_poprzedniej.cmd /przywroc-kopie`; bez kopii zostan przy nowej wersji i zglos sprawe |
| 9 | nie ma poprzedniej wersji / wersja jest biezaca albo poprzednia | zainstaluj potrzebna wersje z jej paczki; usuwac mozna tylko wersje nieuzywane |

W kazdym z tych przypadkow wersja biezaca programu, ustawienia i dane zostaja bez zmian. Gdy komunikat sie powtarza, przekaz
plik `C:\Stanowisko\dziennik_instalacji.txt` (nie zawiera nazw zlecen ani pacjentow).
