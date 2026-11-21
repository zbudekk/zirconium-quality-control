# Instalacja i aktualizacja programu "Stanowisko" - jedna strona dla osoby instalujacej

Paczka wydania to jeden plik `Stanowisko_<wersja>.zip` (ok. 445 MB). Internet nie jest potrzebny. Instalacja niczego nie
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
3. Instalator liczy 9 krokow (wiersze od `[1/9]` do `[9/9]`): sumy paczki, Python, katalog, ustawienia, katalog wersji
   (pakiety - kilka minut), kopia bazy, samokontrola, przelaczenie wersji, skrot. PIERWSZA instalacja zatrzymuje sie
   zwykle po kroku 7 (samokontrola, punkt 4) - kroki 8 i 9 zobaczysz dopiero przy drugim uruchomieniu. Ostatni wiersz
   mowi wszystko: `INSTALACJA: GOTOWA - wersja biezaca ...`,
   `INSTALACJA: WSTRZYMANA - ...` (punkt 4) albo `INSTALACJA: NIEUDANA (kod N) - ...`, a nad nim `BLAD: ...` i `CO ZROBIC: ...`.
4. PIERWSZA instalacja konczy sie zwykle wierszem `INSTALACJA: WSTRZYMANA - uzupelnij ustawienia.toml i uruchom
   zainstaluj.cmd ponownie` (kod 10). To nie blad: plik `C:\Stanowisko\ustawienia.toml` powstal ze wzoru i nie zna jeszcze
   folderow tej maszyny (nad wierszem koncowym sa wiersze `BLAD ...` samokontroli i pelna sciezka pliku). Otworz plik
   w Notatniku i w sekcji `[sciezki]` wpisz foldery (z ukosnikami `/`):
   - OBOWIAZKOWE sa dwa: `folder_eksportu_skanera` i `folder_cyrkon`. Oba foldery musza ISTNIEC na dysku - inaczej
     samokontrola pokaze `BLAD folder_skanera` / `BLAD folder_cyrkon` i instalacja znowu sie wstrzyma.
   - `folder_prywatne` i `folder_millbox` wpisz, jesli je znasz. Ich brak to tylko `OSTRZEZENIE` - instalacja przejdzie.
   - Nie wiesz jeszcze, gdzie skaner zapisuje pliki (przed dniem skanera nikt tego nie wie)? Zaloz pusty folder
     tymczasowy, np. `C:\Skany_tymczasowe`, i wpisz go jako `folder_eksportu_skanera = "C:/Skany_tymczasowe"`. Gdy
     poznasz wlasciwy folder, popraw ten wiersz i uruchom `Samokontrola.cmd`.

   W `[sesja] operatorzy` wpisz osoby, zapisz plik (kodowanie "UTF-8", nie "UTF-8 z BOM") i uruchom `zainstaluj.cmd`
   JESZCZE RAZ - pakiety nie instaluja sie drugi raz, trwa to kilka sekund. Wierszy `baza`, `wyniki`, `logi`... nie zmieniaj.
   Wiersz koncowy `INSTALACJA: NIEUDANA (kod 1)` zamiast `WSTRZYMANA` znaczy: blad nie lezy (tylko) w ustawieniach - tabela 6.
5. Dopiero po wierszu `INSTALACJA: GOTOWA` w `C:\Stanowisko` leza skrypty: `Stanowisko.cmd` (uruchamia program; mozna
   tez skrotem), `Samokontrola.cmd` (sprawdzenie w kazdej chwili), `Wroc_do_poprzedniej.cmd`, `Wersje.cmd`,
   `Dzien_skanera.cmd` i `Polecenie.cmd` (oba - punkt 7). Po przebiegu zakonczonym wierszem `INSTALACJA: WSTRZYMANA`
   (kod 10) tych skryptow jeszcze NIE ma: w katalogu sa tylko `ustawienia.toml`, `dane\`, `wersje\`,
   `dziennik_instalacji.txt` i `instalator.blokada` - tak ma byc. Dane programu: `C:\Stanowisko\dane\`; zapis
   instalacji: `dziennik_instalacji.txt`. Plik `instalator.blokada` zostaje na stale (pilnuje, zeby naraz dzialal
   jeden instalator) - nie kasuj go, niczemu nie przeszkadza.

## 3. Aktualizacja

Zamknij program. Rozpakuj nowa paczke i uruchom JEJ `zainstaluj.cmd` (z tym samym `/katalog`, jesli byl inny niz domyslny).
Instalator sam: zostawia `ustawienia.toml` i `dane\` bez zmian, robi i sprawdza kopie bazy w `dane\kopie\`, zaklada nowa
wersje obok starej, sprawdza ja samokontrola i dopiero wtedy przelacza. Gdy cos sie nie uda, dziala dalej stara wersja.

## 4. Powrot do poprzedniej wersji

Zamknij program i uruchom `C:\Stanowisko\Wroc_do_poprzedniej.cmd`. Skrypt pokaze, z jakiej wersji na jaka wraca, i zapyta
`[T/N]` - `T` i Enter przelacza; sam Enter i kazda inna odpowiedz niczego nie zmienia (kod 11). Jesli nowsza wersja zmienila baze,
zobaczysz ostrzezenie (kod 8): ktora kopia bazy wroci (najnowsza sprawdzona), ile wpisow i od kiedy przepadnie. Zgoda =
`Wroc_do_poprzedniej.cmd /przywroc-kopie` (wraca kopia bazy sprzed aktualizacji; baza biezaca zostaje w `dane\kopie\`
jako `..._odlozona_...`, nie jest kasowana). Brak zgody = zostajesz przy nowej wersji. W skryptach: `/tak` (bez pytania).

Powrot zmienia tylko wersje programu - skrypty w `C:\Stanowisko` zostaja takie, jakie zapisala ostatnia instalacja.
Po powrocie do wersji 0.3.1 (ktora skryptu `Dzien_skanera.cmd` nie miala) ten skrypt dalej lezy w katalogu i dziala:
otwiera okno "Dzien skanera" wersji 0.3.1, a sesje zapisuje - tak jak w nowej wersji - do `C:\Stanowisko\dane\dzien_skanera\`
(nie do katalogu wersji). Dwie roznice w 0.3.1: proba `--zamknij-po` konczy sie kodem 2 i wierszem po angielsku
`error: unrecognized arguments: --zamknij-po ...` (wersja 0.3.1 nie zna tej opcji - to nie awaria), a przycisk "Pomiar
szczegolowy" i `Polecenie.cmd narzedzia\pomiar_skanu\...` nie dzialaja (bledy wersji 0.3.1, poprawione w nastepnej).
To samo po ponownym uruchomieniu `zainstaluj.cmd` z paczki 0.3.1 na katalogu z nowsza wersja: skrypt zostaje.

## 5. Stare wersje

Nie sa kasowane same (kazda to ok. 1,4 GB w `wersje\`); kopie bazy tez nie. Lista: `Wersje.cmd`. Usuniecie:
`Wersje.cmd /usun <wersja>` - tylko wersji, ktora nie jest ani biezaca, ani poprzednia. Zanim usuniesz wersje 0.3.1
albo starsza, przeczytaj ostatni akapit punktu 7 (sesje "Dnia skanera" w katalogu wersji).

## 6. Komunikaty instalatora i co zrobic

| Kod | Komunikat (`BLAD: ...`) | Co zrobic |
|---|---|---|
| 1 | samokontrola ... zglosila bledy (aktualizacja; pierwsza instalacja - gdy choc jeden blad nie dotyczy ustawien) | pod `Bledy samokontroli` stoja wiersze `BLAD <sprawdzenie>: opis; rada` - zrob to, co mowi rada kazdego wiersza. `folder_...` i `operatorzy` poprawia sie w `ustawienia.toml`; `baza`, `moduly`, `pakiety`, `sumy` i inne (wymienia je `CO ZROBIC`) - NIE: gdy rada nie wystarcza, zglos wiersze `BLAD` z plikiem `dziennik_instalacji.txt`. Potem `zainstaluj.cmd` ponownie |
| 2 | samokontroli ... nie dalo sie wykonac / samokontrola ... zakonczyla sie awaryjnie / samokontrola ... nie podala wyniku | "nie dalo sie wykonac": popraw przyczyne podana nad komunikatem (zwykle plik `ustawienia.toml`) i uruchom ponownie; "awaryjnie" i "nie podala wyniku": to nie blad ustawien - po prostu uruchom ponownie, a gdy wraca, zglos komunikat z plikiem `dziennik_instalacji.txt` |
| 3 | sumy SHA-256 paczki niezgodne / w paczce brakuje ... / blad wydania / wersja juz zainstalowana z INNEJ budowy / numer zapisany inaczej | paczka uszkodzona albo niepelna: pobierz i rozpakuj ja ponownie w calosci; "blad wydania", "inna budowa" i "numer zapisany inaczej" zglos budujacemu paczke (potrzebna paczka z nowym numerem wersji) |
| 4 | `zainstaluj.cmd`: nie znaleziono Pythona 3.12 / zla wersja Pythona / brak Pythona (wiersz koncowy: `... - niczego nie zmieniono.`) | zainstaluj Pythona 3.12 (64-bit) albo wskaz go: `zainstaluj.cmd /python <sciezka>\python.exe` |
| 4 | `Stanowisko.cmd`, `Samokontrola.cmd`, `Wroc_do_poprzedniej.cmd`, `Wersje.cmd`, `Dzien_skanera.cmd`, `Polecenie.cmd`: w tym katalogu nie ma gotowej wersji biezacej programu | instalacja nie doszla do konca albo zostala przerwana w trakcie naprawy: uruchom `zainstaluj.cmd` z rozpakowanej paczki wydania |
| 5 | program "Stanowisko" jest uruchomiony / baza jest zajeta przez inny program (takze: pliku bazy nie da sie zamienic, obok bazy lezy plik `-journal`) | zamknij program (i inne programy z otwarta baza, np. przegladarke bazy), uruchom polecenie ponownie |
| 6 | za malo miejsca / pip zakonczyl sie bledem / instalacja przerwana / katalog synchronizowany / sciezka za dluga albo ze srednikiem / nie mozna pisac / nie mozna usunac albo odlozyc katalogu / srodowisko nie startuje / nie udalo sie zalozyc pip / nie mozna zapisac pliku stanowisko_bez_wmi.pth / srodowisko nie blokuje modulu _wmi / pakiety niezgodne / pliku bazy nie da sie odczytac / nie ma pliku bazy / inna instalacja juz trwa / nieoczekiwany blad | zrob to, co mowi wiersz `CO ZROBIC` na ekranie (kazdy z tych komunikatow ma wlasny), i uruchom ponownie - niedokonczona wersja sprzata sie sama |
| 7 | plik ustawien nie przechodzi kontroli / sciezki wzgledne w [sciezki] / plik zaczyna sie znakiem BOM | popraw `ustawienia.toml` tak, jak podaje komunikat (sciezki danych bezwzgledne, np. `C:/Stanowisko/dane/...`; zapis jako "UTF-8") |
| 8 | powrot ... wymaga przywrocenia kopii bazy / nie ma sprawdzonej kopii bazy | przeczytaj ostrzezenie; zgoda: `Wroc_do_poprzedniej.cmd /przywroc-kopie`; bez kopii zostan przy nowej wersji i zglos sprawe |
| 9 | nie ma poprzedniej wersji / wersja jest biezaca albo poprzednia | zainstaluj potrzebna wersje z jej paczki; usuwac mozna tylko wersje nieuzywane |
| 10 | (bez `BLAD:`) `INSTALACJA: WSTRZYMANA` - pierwsza instalacja, wszystkie bledy samokontroli dotycza ustawien (foldery, osoby) | uzupelnij `ustawienia.toml` (punkt 2.4) i uruchom `zainstaluj.cmd` ponownie |
| 11 | (bez `BLAD:`) `POWROT: ANULOWANY` - odpowiedz inna niz `T` (takze sam Enter) | nic - wersja biezaca bez zmian; odpowiedz `T`, gdy chcesz wrocic |

Ostatni wiersz zawsze mowi, co z wersja biezaca: zwykle `wersja biezaca bez zmian: X` (ustawienia i dane tez zostaja).
Wyjatek: `UWAGA: wersja biezaca X jest niekompletna` (okno zamkniete w trakcie naprawy tej wersji) - uruchom ponownie
`zainstaluj.cmd` z paczki. Gdy komunikat sie powtarza, przekaz plik `C:\Stanowisko\dziennik_instalacji.txt` (bez nazw zlecen i pacjentow).

## 7. "Dzien skanera" i narzedzia z katalogu instalacji

- **Okno "Dzien skanera - krok po kroku":** `C:\Stanowisko\Dzien_skanera.cmd` (dwuklik). Okno czyta
  `C:\Stanowisko\ustawienia.toml` (obserwuje folder z wiersza `folder_eksportu_skanera`) i zapisuje sesje do
  `C:\Stanowisko\dane\dzien_skanera\<data_godzina>\` (skrypt podaje ten katalog oknu wprost, takze po powrocie do
  wersji 0.3.1 - punkt 4). Pliki ZIP do wyslania leza w podfolderze `paczka\` tej sesji.
  Aktualizacja programu i usuwanie starych wersji tych sesji nie ruszaja.
  Proba bez klikania: `Dzien_skanera.cmd --nowa --zamknij-po 5` (okno otwiera sie i samo zamyka po 5 sekundach, kod 0;
  opcja dziala od wersji nastepnej po 0.3.1). Na ekranie ma byc wiersz `DZIEN SKANERA: sesja C:\Stanowisko\dane\dzien_skanera\...;
  ustawienia C:\Stanowisko\ustawienia.toml; foldery obserwowane: <folder skanera>`. Wiersz `UWAGA: ustawienia: ...` pod
  spodem (albo `ustawienia BRAK`, albo `ustawienia ...ustawienia.przyklad.toml`) znaczy: okno NIE pracuje na Twoim pliku
  ustawien - pliku nie ma albo ma blad (np. zapisany jako "UTF-8 z BOM"). Popraw plik i powtorz probe; w oknie ten sam
  powod stoi w dzienniku okna (wiersz "Plik ustawien ma blad ..." albo "Nie wczytano ustawien ...").
  Po probie zostaje pusta, niedokonczona sesja: przy nastepnym uruchomieniu okno zapyta "Znaleziono niedokonczona sesje
  ... (0 plikow). Wznowic ja?" - odpowiedz Tak albo Nie, obie odpowiedzi sa dobre (Tak = praca w tej pustej sesji,
  Nie = nowa sesja).
  Sprawdzenie paczki: `Dzien_skanera.cmd --sprawdz <plik zip albo folder sesji>`.
  Komunikat `BLAD: katalog sesji ... lezy w katalogu wersji programu` (okno sie nie otwiera, kod 1) znaczy: ktos wskazal
  katalog sesji wewnatrz `C:\Stanowisko\wersje\` (opcja `--dane` albo - przy uruchomieniu przez `Polecenie.cmd -m
  stanowisko.dzien_skanera` - wiersz `baza` w `ustawienia.toml` bez pelnej sciezki). Uruchom `Dzien_skanera.cmd` bez `--dane`.
  Pliku `uruchom_dzien_skanera.bat` w instalacji nie ma (jest tylko w kopii roboczej programu).
- **Python biezacej wersji dla narzedzi:** `C:\Stanowisko\Polecenie.cmd <argumenty>`, np. pomiar szczegolowy skanu bez okna:
  `Polecenie.cmd narzedzia\pomiar_skanu\pomiar_skanu.py <plik skanu> --wyj <katalog na wynik>` (zwykle 2-6 minut;
  pierwszy wiersz na ekranie `ustawienia: ...` pokazuje, ktory plik ustawien zostal uzyty). W oknie "Dzien skanera" to samo
  robi przycisk "Pomiar szczegolowy".
- **Program ramki na Raspberry Pi:** instrukcja `C:\Stanowisko\wersje\<wersja>\program\instrukcje\ramka_raspberry_pi.md`,
  pliki do skopiowania na ramke: caly katalog `C:\Stanowisko\wersje\<wersja>\program\ramka` (z podkatalogiem `rpi`).
- **Sesje zapisane wersja 0.3.1** (uruchamiana wtedy przez `Polecenie.cmd -m stanowisko.dzien_skanera`) leza w
  `C:\Stanowisko\wersje\0.3.1\program\dane\dzien_skanera\`. Program ich sam nie przenosi. Zanim usuniesz wersje 0.3.1,
  skopiuj ten folder (cale podfoldery sesji) do `C:\Stanowisko\dane\dzien_skanera\`.
