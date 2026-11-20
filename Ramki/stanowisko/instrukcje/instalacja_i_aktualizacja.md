# Instalacja i aktualizacja programu "Stanowisko" - jedna strona dla osoby instalujacej

Paczka wydania to jeden plik `Stanowisko_<wersja>.zip` (ok. 430 MB). Internet nie jest potrzebny. Instalacja niczego nie
zmienia w systemie: wszystko lezy w jednym katalogu (domyslnie `C:\Stanowisko`), poza folderami OneDrive / SharePoint.

## 1. Raz, recznie: Python 3.12

Zainstaluj Pythona 3.12 (64-bit) z python.org - opcje domyslne wystarcza. Sprawdzona wersja to **3.12.10**; inna 3.12.x tez
zostanie przyjeta (instalator wypisze `OSTRZEZENIE: Python ...`). Inne wersje Pythona (3.11, 3.13) nie przeszkadzaja, ale nie zastapia 3.12.

## 2. Instalacja

1. Rozpakuj CALA paczke (prawy klawisz -> "Wyodrebnij wszystkie") do dowolnego katalogu, np. `C:\Paczki\Stanowisko_0.3.1`.
2. Uruchom w rozpakowanym katalogu `zainstaluj.cmd` (dwuklik). Opcje, gdy trzeba - w wierszu polecen:
   `zainstaluj.cmd /katalog D:\Stanowisko` (inny katalog), `/python C:\...\python.exe` (wskazany Python 3.12),
   `/skrot` (skrot "Stanowisko" na pulpicie), `/bez-sieci` (samokontrola bez proby polaczenia z ramkami).
   Na koncu okno czeka na klawisz (`/bez-pauzy` - nie czeka).
3. Zobaczysz 9 krokow: sumy paczki, Python, katalog, ustawienia, katalog wersji (pakiety - kilka minut), kopia bazy,
   samokontrola, przelaczenie wersji, skrot. Ostatni wiersz mowi wszystko: `INSTALACJA: GOTOWA - wersja biezaca ...`,
   `INSTALACJA: WSTRZYMANA - ...` (punkt 4) albo `INSTALACJA: NIEUDANA (kod N) - ...`, a nad nim `BLAD: ...` i `CO ZROBIC: ...`.
4. PIERWSZA instalacja konczy sie zwykle wierszem `INSTALACJA: WSTRZYMANA - uzupelnij ustawienia.toml i uruchom
   zainstaluj.cmd ponownie` (kod 10). To nie blad: plik `C:\Stanowisko\ustawienia.toml` powstal ze wzoru i nie zna jeszcze
   folderow tej maszyny (nad wierszem koncowym sa wiersze `BLAD ...` samokontroli i pelna sciezka pliku). Otworz plik
   w Notatniku, w sekcji `[sciezki]` wpisz foldery (eksport skanera, Cyrkon, Prywatne, MillBox - z ukosnikami `/`),
   w `[sesja] operatorzy` osoby, zapisz (kodowanie "UTF-8", nie "UTF-8 z BOM") i uruchom `zainstaluj.cmd` JESZCZE RAZ -
   pakiety nie instaluja sie drugi raz, trwa to kilka sekund. Wierszy `baza`, `wyniki`, `logi`... nie zmieniaj.
5. Program uruchamia `C:\Stanowisko\Stanowisko.cmd` (albo skrot). Obok: `Samokontrola.cmd` (sprawdzenie w kazdej chwili),
   `Wroc_do_poprzedniej.cmd`, `Wersje.cmd`. Dane programu: `C:\Stanowisko\dane\`; zapis instalacji: `dziennik_instalacji.txt`.

## 3. Aktualizacja

Zamknij program. Rozpakuj nowa paczke i uruchom JEJ `zainstaluj.cmd` (z tym samym `/katalog`, jesli byl inny niz domyslny).
Instalator sam: zostawia `ustawienia.toml` i `dane\` bez zmian, robi i sprawdza kopie bazy w `dane\kopie\`, zaklada nowa
wersje obok starej, sprawdza ja samokontrola i dopiero wtedy przelacza. Gdy cos sie nie uda, dziala dalej stara wersja.

## 4. Powrot do poprzedniej wersji

Zamknij program i uruchom `C:\Stanowisko\Wroc_do_poprzedniej.cmd`. Skrypt pokaze, z jakiej wersji na jaka wraca, i zapyta
`[T/N]` - `T` i Enter przelacza, kazda inna odpowiedz niczego nie zmienia (kod 11). Jesli nowsza wersja zmienila baze,
zobaczysz ostrzezenie (kod 8): ktora kopia bazy wroci (najnowsza sprawdzona), ile wpisow i od kiedy przepadnie. Zgoda =
`Wroc_do_poprzedniej.cmd /przywroc-kopie` (wraca kopia bazy sprzed aktualizacji; baza biezaca zostaje w `dane\kopie\`
jako `..._odlozona_...`, nie jest kasowana). Brak zgody = zostajesz przy nowej wersji. W skryptach: `/tak` (bez pytania).

## 5. Stare wersje

Nie sa kasowane same (kazda to ok. 1,5 GB w `wersje\`); kopie bazy tez nie. Lista: `Wersje.cmd`. Usuniecie:
`Wersje.cmd /usun <wersja>` - tylko wersji, ktora nie jest ani biezaca, ani poprzednia.

## 6. Komunikaty instalatora i co zrobic

| Kod | Komunikat (`BLAD: ...`) | Co zrobic |
|---|---|---|
| 1 | samokontrola ... zglosila bledy (aktualizacja) | popraw to, co wskazuja wiersze `BLAD` (zwykle foldery w `ustawienia.toml`), uruchom `zainstaluj.cmd` ponownie |
| 2 | samokontroli ... nie dalo sie wykonac / samokontrola ... zakonczyla sie awaryjnie | popraw przyczyne podana nad komunikatem (zwykle plik `ustawienia.toml`), uruchom ponownie; "awaryjnie" = po prostu uruchom ponownie |
| 3 | sumy SHA-256 paczki niezgodne / w paczce brakuje ... / blad wydania / wersja juz zainstalowana z INNEJ budowy / numer zapisany inaczej | paczka uszkodzona albo niepelna: pobierz i rozpakuj ja ponownie w calosci; "blad wydania", "inna budowa" i "numer zapisany inaczej" zglos budujacemu paczke (potrzebna paczka z nowym numerem wersji) |
| 4 | nie znaleziono Pythona 3.12 / zla wersja Pythona / brak Pythona (wiersz koncowy: `... - niczego nie zmieniono.`) | zainstaluj Pythona 3.12 (64-bit) albo wskaz go: `zainstaluj.cmd /python <sciezka>\python.exe` |
| 5 | program "Stanowisko" jest uruchomiony / baza jest zajeta przez inny program | zamknij program (i inne programy z otwarta baza), uruchom polecenie ponownie |
| 6 | za malo miejsca / pip zakonczyl sie bledem / instalacja przerwana / katalog synchronizowany / sciezka za dluga albo ze srednikiem / nie mozna pisac / nie mozna usunac albo odlozyc katalogu / srodowisko nie startuje / nie udalo sie zalozyc pip / nie mozna zapisac pliku stanowisko_bez_wmi.pth / srodowisko nie blokuje modulu _wmi / pakiety niezgodne / pliku bazy nie da sie odczytac / nie ma pliku bazy / inna instalacja juz trwa / nieoczekiwany blad | zrob to, co mowi wiersz `CO ZROBIC` na ekranie (kazdy z tych komunikatow ma wlasny), i uruchom ponownie - niedokonczona wersja sprzata sie sama |
| 7 | plik ustawien nie przechodzi kontroli / sciezki wzgledne w [sciezki] / plik zaczyna sie znakiem BOM | popraw `ustawienia.toml` tak, jak podaje komunikat (sciezki danych bezwzgledne, np. `C:/Stanowisko/dane/...`; zapis jako "UTF-8") |
| 8 | powrot ... wymaga przywrocenia kopii bazy / nie ma sprawdzonej kopii bazy | przeczytaj ostrzezenie; zgoda: `Wroc_do_poprzedniej.cmd /przywroc-kopie`; bez kopii zostan przy nowej wersji i zglos sprawe |
| 9 | nie ma poprzedniej wersji / wersja jest biezaca albo poprzednia | zainstaluj potrzebna wersje z jej paczki; usuwac mozna tylko wersje nieuzywane |
| 10 | (bez `BLAD`) `INSTALACJA: WSTRZYMANA` - pierwsza instalacja | uzupelnij `ustawienia.toml` (punkt 2.4) i uruchom `zainstaluj.cmd` ponownie |
| 11 | (bez `BLAD`) `POWROT: ANULOWANY` | nic - wersja biezaca bez zmian; odpowiedz `T`, gdy chcesz wrocic |

Ostatni wiersz zawsze mowi, co z wersja biezaca: zwykle `wersja biezaca bez zmian: X` (ustawienia i dane tez zostaja).
Wyjatek: `UWAGA: wersja biezaca X jest niekompletna` (okno zamkniete w trakcie naprawy tej wersji) - uruchom ponownie
`zainstaluj.cmd` z paczki. Gdy komunikat sie powtarza, przekaz plik `C:\Stanowisko\dziennik_instalacji.txt` (bez nazw zlecen i pacjentow).
