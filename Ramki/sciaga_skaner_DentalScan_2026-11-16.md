# Sciaga: program skanera DentalScan - od uruchomienia do pliku STL calej plytki (16.11.2026)

Dla: wlasciciel, dzien dostawy skanera Aidite A-IS Pro. Skanera jeszcze nie widzielismy. Wszystko ponizej pochodzi
z dokumentacji online DentalScan 3.0.4 (odczyt 15-16.11.2026) i z notatek z 27.10 (`notatki_dokumentacja_skanera.md`).
Egzemplarz moze miec inna wersje programu i inny wyglad.

Jak czytac:
- nazwy w cudzyslowach, np. "New Order", sa przepisane doslownie z dokumentacji (po angielsku, tak jak na ekranie),
- **zrodlo:** nazwa strony dokumentacji (adresy na koncu),
- **[DO SPRAWDZENIA NA EGZEMPLARZU]** = dokumentacja tego nie mowi; nie zgadujemy - patrzymy na ekran i robimy zrzut.

Zasada nadrzedna: **szukamy pliku STL z CALA plytka (wierzch plytki, trzy stozki w rogach, prace w gniazdach).**
W razie watpliwosci: zrzut ekranu przyciskiem "Zrzut ekranu" w oknie "Dzien skanera", zapisac wszystko, co program
pozwala zapisac, niczego nie kasowac. Okno samo kopiuje kazdy nowy plik i ocenia, czy to cala plytka.

## 0. Zanim program ruszy (zwykle robi to instalator)

| Co | Jak wg dokumentacji | Zrodlo |
|---|---|---|
| Kabel | skaner do portu USB 3.0; tylko zasilacz i kable z zestawu | connection |
| Klucz USB (dongle) | "If there is a dongle in the parts list, please insert the dongle into the USB port before running the software." Klucza i kabla skanera nie wkladac w sasiednie porty USB | connection |
| Program | skopiowac z nosnika USB na dysk komputera i dopiero uruchomic; wlaczyc skaner przyciskiem z tylu | connection |
| Konto | "New User? Click here to register" -> "Lab" -> dane -> "Sign Up" -> "Return"; logowanie numerem konta i haslem | register |
| Aktywacja | "Online Activation" -> "Activate" (komputer z internetem) albo "Offline Activation": "Export" (plik C2V na pendrive) -> na komputerze z internetem wgrac C2V i pobrac V2C -> "Import" | activation |
| Typ urzadzenia | ikona ustawien -> "About" -> lista typu urzadzenia (bez tego polaczenie sie nie uda) | otheroperation |
| Kalibracja | ikona kalibracji w prawym gornym rogu -> "Calibration" -> "Select Calibration Board File" (numer z tylu plytki kalibracyjnej; brak pliku: "Download" albo "import") -> podstawka "height adaptor" na stolik, na nia plytka kalibracyjna -> "Start" -> komunikat "Calibration successful" | calibration, cali-caution |

- Kalibracja jest wymagana przy pierwszym podlaczeniu; zalecana co 15 dni. Plytki kalibracyjnej nie dotykac od przodu.
- [DO SPRAWDZENIA NA EGZEMPLARZU] czy rejestracja i logowanie wymagaja internetu i czy program dziala bez sieci.
- [DO SPRAWDZENIA NA EGZEMPLARZU] ile dni autoryzacji zostalo: ikona ustawien -> "About" -> "Authorization Remaining Days"
  (przedluzenie: "Request an Authorization Renewal"). Zrzut ekranu tego okna.
- Wymagania komputera wg dokumentacji: Windows 10 64-bit (Windows 11 nie jest wymieniony), Intel Core i7, pamiec
  "16G or higher for A-IS series" / "32G or above for A-IS Pro 3/ASDS-MIX", karta NVIDIA GTX 1060 lub lepsza, USB 3.0,
  ponad 20 GB wolnego miejsca na dysku zlecen. Zrodlo: operatingenviroment.

## 1. Uruchomienie i ustawienia (tylko patrzymy i robimy zrzuty)

1. Uruchom program skanera i zaloguj sie. Ekran glowny ma u gory ikony: "Home", "User", "Calibration",
   "Screen Shot Tool", "Settings", "Help"; po lewej: "New Order", "Import Order". Zrodlo: interface.
   -> zrzut ekranu.
2. Ustawienia zlecen: ikona ustawien -> "Order Setting". Zakladki: "General", "Order File Naming Rule", "Save Format".
   Zrodlo: settingorder. -> zrzut kazdej zakladki.
   - "General" -> **"Order Save Path"** ("Click to modify the saving path.") = folder, w ktorym program trzyma zlecenia.
     Przepisz te sciezke do okna "Dzien skanera" (pole "Folder zapisu zlecen") i sprawdz, czy okno obserwuje ten sam
     folder. Jesli nie - w oknie "Dodaj folder...".
   - "Order File Naming Rule": "Customize the naming rule by selecting its elements." - nie zmieniaj, zrob zrzut.
     [DO SPRAWDZENIA NA EGZEMPLARZU] jakie elementy nazwy sa do wyboru.
   - "Save Format": "Save Exocad order" (domyslnie zaznaczone), "Save third party orders" (dla 3Shape, domyslnie nie).
     [DO SPRAWDZENIA NA EGZEMPLARZU] czy jest wybor formatu pliku (STL / PLY / OBJ) - dokumentacja tego nie podaje.
   - Zamkniecie ustawien: program pyta, "Yes" zapisuje zmiany, "No" je odrzuca. Niczego nie zmieniales -> "No".
3. Ustawienia skanu: ikona ustawien -> "Scan Setting" (prawy gorny rog ekranu glownego) -> "General Setting":
   "AI Detection", "Save Image", "Rotate Upper Jaw 180" (na ekranie ze znakiem stopni), "Pre-design Guideline",
   "Navigation Mode", "Auto Bite Optimization". Zrodlo: settingscan. -> zrzut.
   - "Save Image": "Save the original image captured by the scanner." Wydluza skan; dokumentacja zaleca wylaczone.
     Zostaw wylaczone (wlaczamy tylko w kroku "Zdjecia z kamer").
   - Opcji jakosci skanu, wygladzania ani wypelniania otworow na tej stronie NIE ma. [DO SPRAWDZENIA NA EGZEMPLARZU]
4. Okno "About" (ikona ustawien -> "About"): wersja, typ urzadzenia, "Authorization Remaining Days". -> zrzut.

## 2. Zlecenie do skanu calej plytki

Strona dokumentacji: "Die tray", czesc "Die Order" (druga czesc tej strony, "Waxup Order", nas nie dotyczy).

1. Ekran glowny -> **"New Order"**. Otwiera sie strona nowego zlecenia z zakladkami "Order Information",
   "Tooth selection", "Type Selection". Zrodlo: interface, neworder.
2. "Order Information": "Fill the blanks. Enter the information of the order and the patient." Wpisz **TEST1**
   (bez nazwisk). Lekarza i technika wybiera sie z listy. [DO SPRAWDZENIA NA EGZEMPLARZU] ktore pola sa obowiazkowe.
3. Typ: **"Restoration"**. Zrodlo: dietray ("Create the Order", punkt 1).
4. Tryb: **"Multidie Mode"** (na stronie neworder zakladka nazywa sie "Multidie mode"; druga to "Patient mode").
   "The multidie mode is mainly used for scanning multiple individual dies." Zrodlo: dietray punkt 2, neworder.
5. W trybie Multidie program pokazuje uchwyt producenta z numerowanymi pozycjami: "Click the hole in the fixture of
   the tooth die to select the type of restoration." Prawy przycisk myszy cofa wybor pozycji, "Clear All" czysci
   wszystkie. Zaznacz kilka pozycji z dowolnym typem odbudowy. Zrodlo: neworder.
   - [DO SPRAWDZENIA NA EGZEMPLARZU] ile pozycji trzeba zaznaczyc, zeby program zeskanowal cala nasza plytke,
     i czy wynikiem jest JEDEN plik calej plytki, czy osobne pliki na kazda pozycje. To najwazniejsza niewiadoma.
6. Na dole: **"Scan"** ("Start scanning.") albo **"Save"** ("Save the current order for further scanning.");
   "Explore" ("View the files related to current order.") otwiera folder plikow zlecenia. Zrodlo: neworder, dietray
   punkt 3 ("Click Scan to start or click Save to save the order and scan it later.").
7. Zapisane zlecenie otwiera sie z listy dwuklikiem ("Open a certain order by double-clicking it."). Zrodlo: interface.
   [DO SPRAWDZENIA NA EGZEMPLARZU] czy jedno zlecenie obsluzy wiele skanow, czy kazdy skan potrzebuje nowego (TEST2 ...).

-> zrzut ekranu zlecenia przed kliknieciem "Scan".

## 3. Skan ("Die Scan")

Ekran skanowania ma czesci: 1 "Camera Window", 2 "Guide", 3 "Preset", 4 "Progress Bar", 5 "Preview", 6 "Add Scan",
7 "Operation" (przyciski "Start Scan", "Reset", "Preview", "Save", "Alignment"), 8 "Edit & Import", 9 "Additional
Function". Zrodlo: scaninterface. -> zrzut przed pierwszym skanem.

Kroki wg strony dietray ("Die Scan"):

| Nr | Co robi dokumentacja | Co robimy my |
|---|---|---|
| 1 | polozyc "height adaptor" i model wg wskazowek na ekranie | kladziemy nasza plytke. [DO SPRAWDZENIA NA EGZEMPLARZU] jak plytka stoi na stoliku i czy potrzebna jest podstawka |
| 2 | ustawienia w oknie kamery ("Camera Window") | ikona jasnosci: suwak albo przycisk auto, "until several red spots appearing". Ikona wysokosci ciecia: niebieska linia na dole okna, "Only the range above the cutting line is to be scanned." -> linia ma byc POWYZEJ stolika i co najmniej 3 mm PONIZEJ wierzchu plytki (stolik i podstawka nie moga trafic do skanu - program nie rozpozna wtedy plytki; scianka boczna plytki ma zostac w skanie, o ile sie da). [DO SPRAWDZENIA NA EGZEMPLARZU] czy linie da sie ustawic miedzy stolikiem a wierzchem plytki |
| 3 | (opcjonalnie) funkcje dodatkowe | pierwszy skan BEZ dodatkow |
| 4 | ikona "Add details": skan wysokiej jakosci | dopiero w kroku "zapisany inaczej" |
| 5 | start: ikona startu albo **Spacja** | Spacja ("Space: Start scan or move forward."); Esc = "Quit scanning." |
| 6 | po skanie: "move or rotate the cutting plane to cut the model"; czerwona czesc ("jig data") jest odcinana | plaszczyzna ciecia ma zostac co najmniej 3 mm PONIZEJ wierzchu plytki i POWYZEJ stolika - caly wierzch ze stozkami zostaje, stolik jest odciety. [DO SPRAWDZENIA NA EGZEMPLARZU] czy da sie ja tak ustawic |
| 7 | ikona edycji: edycja modelu | nie edytujemy (patrz "Czego nie klikac") |
| 8 | ikona OK: zapis edycji i powrot | - |
| 9 | ikona podgladu / ikona resetu = skan od nowa / ikona zakonczenia | podglad wolno; reset dopiero, gdy okno "Dzien skanera" ma juz kopie pliku; potem zakonczenie |
| 10 | "After finishing the scanning process, click on Go to Pre-design" | **"Go to Pre-design"** |

Zrodlo: dietray, parameters-scan (okno kamery), shortcut-instruction (Spacja, Esc).

- Opcje z "Additional Function" wg strony dataedit: dodatkowe sciezki skanu, "Add details" (skan wysokiej jakosci),
  AI detection, skan tekstury, HDR (opisany dla artykulatorow i dziasel), obiekty odbijajace. Nazwy tych ikon nie maja
  podpisow w dokumentacji. [DO SPRAWDZENIA NA EGZEMPLARZU]
- Notatki z 27.10 (starszy odczyt dokumentacji i instrukcji PDF) wymieniaja opcje jakosci: "HDR", "Add details /
  High Quality", "Mental tooth" (obiekty odbijajace) i "reduce high brightness" (tryb die tray). W odczycie 15-16.11
  potwierdzilismy "Add details", "High Quality" i HDR; doslownego "reduce high brightness" i "Mental tooth" nie
  znalezlismy na przeczytanych stronach. [DO SPRAWDZENIA NA EGZEMPLARZU] Zasada: pierwszy skan bez tych opcji, potem
  osobny skan z kazda z nich w kroku "zapisany inaczej" - i zrzut ekranu.
- Czas skanu i liczba pozycji stolika: dokumentacja nie podaje -> mierzymy stoperem w oknie.

## 4. Gdzie jest plik STL

Dokumentacja 3.0.4 **nie mowi**, w ktorym momencie i w jakim formacie plik skanu trafia na dysk. Po kolei:

1. Popatrz na okno "Dzien skanera": jesli plik sam pojawil sie na liscie - gotowe.
2. Na zleceniu (lista zlecen albo strona zlecenia) kliknij **"Explore"** - otworzy sie folder plikow zlecenia.
   Jesli to inny folder niz obserwowany - w oknie "Dodaj folder...". Zrodlo: interface, neworder.
3. Na ekranie skanu, czesc "Operation": przycisk **"Save"**. [DO SPRAWDZENIA NA EGZEMPLARZU] co dokladnie zapisuje.
4. Eksport: na liscie zlecen ikona "Send" albo na ekranie pre-design **"Go to Send"** -> **"Export"** -> okno
   "Export Option": "Folder Name" (wpisz TEST1), ikona katalogu = "Export Path" (wybierz folder obserwowany przez
   okno), "CAD Type" (program projektowy) -> **"Confirm"**. Zrodlo: third-party-software.
5. Nadal nic: w oknie "Dzien skanera" przycisk "Nie wiem, gdzie skaner zapisuje - szukaj" (szuka swiezych plikow
   STL / PLY / OBJ na wszystkich dyskach).
6. Stara instrukcja PDF (2020, inna wersja programu): plik STL powstawal w folderze "Scandata" po "Apply" / "Next".
   Zrodlo: notatki z 27.10. [DO SPRAWDZENIA NA EGZEMPLARZU]

Okno ocenia kazdy plik: zielone "skan dobry" = cala plytka rozpoznana. Czerwone "nie widac plaskiego wierzchu" albo
"nie widac trzech stozkow" = plik jest obciety albo to pojedyncza praca -> patrz plan B.

**Plan B, gdy "Multidie Mode" daje osobne pliki na pozycje albo obcina plytke:** nowe zlecenie w trybie
"Patient mode", "Scan Type" = **"Unsectioned Model"** ("For scanning the whole upper / lower jaw.") - plytka skanowana
jak caly model. Zrodlo: neworder. [DO SPRAWDZENIA NA EGZEMPLARZU] czy taki skan daje jeden plik calej plytki.

## 5. Czego NIE klikac

| Nie klikaj | Dlaczego | Zrodlo |
|---|---|---|
| "Delete" na liscie zlecen (z polem "Delete File") | kasuje zlecenie i pliki | interface |
| klawisz Delete w edycji ("Delete the data in red color.") oraz narzedzia zaznaczania do kasowania: "Connected Domain", "Cut Through", "Brush", "Rectangular Selection", "Lasso" | kasuja czesc skanu; ("Eraser" i "Reverse" tylko zmieniaja zaznaczenie) | dataedit, shortcut-instruction |
| "Import" na ekranie skanu | "The newly imported data will cover the original one." | dataedit, scaninterface |
| "Reset" (ikona skanu od nowa), zanim okno ma kopie pliku | [DO SPRAWDZENIA NA EGZEMPLARZU] prawdopodobnie usuwa biezacy skan | dietray, scaninterface |
| plaszczyzna ciecia ("cutting plane") ustawiona powyzej wierzchu plytki; linia wysokosci ciecia w oknie kamery powyzej wierzchu plytki | odcina stozki i wierzch - program nie rozpozna plytki | dietray, parameters-scan |
| wypelnianie otworow, wygladzanie, upraszczanie siatki | w dokumentacji 3.0.4 nie znalezlismy takich przyciskow (stary PDF: reczne wypelnianie otworow, promien 2 / 4 / 6 mm); jesli sa na ekranie - nie uzywac, poza krokiem "zapisany inaczej" | notatki 27.10; [DO SPRAWDZENIA NA EGZEMPLARZU] |
| ikona "machine test" w oknie kamery | "This function should only be conducted by professional technicians." | parameters-scan |
| zamkniecie zlecenia albo programu przed skopiowaniem pliku | plik moze nie zostac zapisany | zasada ostroznosci |
| "Install" przy komunikacie "Please Update the Software" w dniu testu | zmiana wersji w trakcie zbierania danych; najpierw zrzut i pytanie do koordynatora | strony wstepne dokumentacji (connection / otheroperation - odczyt nie zapisal, ktora); zasada ostroznosci |

## 6. Gdy ekran wyglada inaczej niz tutaj

1. Zrzut ekranu przyciskiem "Zrzut ekranu" w oknie "Dzien skanera" (3 sekundy na przelaczenie okna).
2. Szukaj tego, co prowadzi do celu: skan calego przedmiotu jednym skanem -> zapis albo eksport STL.
3. Nie wiesz, ktora opcja - wybierz te, ktora NIE usuwa i NIE zmienia danych, i zapisz wynik jako osobny plik.
4. Mozesz zapisac cos na kilka sposobow - zapisz na wszystkie (rozne nazwy: TEST1, TEST1b ...).
5. Nie da sie - w oknie "Nie udalo sie / pomijam, bo ..." i jedno zdanie, co bylo na ekranie. Idz dalej.

## 7. Pytania do instalatora / szkoleniowca Aidite (w dniu instalacji)

1. Prosze pokazac skan plytki z wieloma malymi pracami ("Multidie Mode") i zapis JEDNEGO pliku STL calej plytki,
   bez zadnej obrobki. (Nagrac telefonem albo robic zrzuty.)
2. W ktorym folderze leza pliki zlecen i skanow ("Order Save Path")? Jaka jest struktura folderu zlecenia i formaty plikow?
3. Czy program przy budowie albo zapisie siatki wygladza, wypelnia otwory lub upraszcza? Jak to wylaczyc?
4. Czy plaszczyzne ciecia po skanie da sie ustawic miedzy stolikiem a wierzchem plytki (co najmniej 3 mm ponizej wierzchu)? Czy da sie to zapamietac w zleceniu?
5. Jaka jest najwyzsza jakosc skanu ("Add details" / "High Quality") i jak ja wlaczyc dla calej plytki? Jaki jest wtedy
   odstep punktow w pliku STL?
6. Licencja: czy jest klucz USB (dongle), ile zostalo "Authorization Remaining Days", czy program dziala bez internetu,
   czy mozna dostac drugi klucz albo licencje na drugi komputer?
7. Gdzie "Save Image" zapisuje zdjecia z kamer, w jakim formacie i rozdzielczosci?
8. Czy jedno zlecenie mozna skanowac wiele razy (plytka po plytce), czy kazdy skan wymaga nowego zlecenia?
9. Jakie sa wymiary pola skanowania i jak mocuje sie wlasna plytke na stoliku?

## 8. Skroty i mysz (strona shortcut-instruction)

- Spacja: "Start scan or move forward." Esc: "Quit scanning."
- Mysz na modelu: przytrzymany lewy albo prawy przycisk i ruch = obrot; oba przyciski i ruch = przesuniecie; kolko = powiekszenie.
- Edycja: Shift + lewy przycisk = gumka, Shift + kolko = rozmiar pedzla, **Delete = kasuje dane zaznaczone na czerwono** (nie uzywac).
- W zaznaczaniu zebow Spacja kasuje wszystkie wybrane typy odbudowy - w trybie Multidie nie naciskaj Spacji na
  stronie zlecenia. [DO SPRAWDZENIA NA EGZEMPLARZU] czy dotyczy to trybu Multidie.

## 9. Czego nie wiemy (uczciwie)

- Czy "Multidie Mode" na naszej plytce (nie na uchwycie producenta) da jeden plik STL calosci.
- W jakim momencie, gdzie i w jakim formacie program zapisuje plik skanu.
- Czy program wygladza albo wypelnia siatke bez pytania.
- Jak wyglada "cutting plane" i czy mozna ja pominac.
- Ile trwa skan i ile ma pozycji; jakie jest pole skanowania.
- Czy egzemplarz ma te sama wersje programu (dokumentacja: 3.0.4).

Kazda z tych rzeczy rozstrzygnie sie w pierwszej godzinie - dlatego zrzuty ekranu i notatki w oknie sa tak wazne.

## 10. Zrodla

Dokumentacja online DentalScan 3.0.4: `https://docs.doc-usermanual.com/aidite/dentalscan/3.0.4/en-us/<strona>`
(strona glowna bez nazwy strony zwraca blad 404; podstrony dzialaja). Strony przeczytane 15-16.11.2026:
interface, neworder, dietray, die-in-one, scannode, scaninterface, settingorder, settingscan, parameters-scan,
shortcut-instruction, workflow-settings, dataedit, addscan, alignment, predesign, third-party-software, fixture,
otheroperation, activation, register, connection, cali-caution, calibration, operatingenviroment, overview.
Nie przeczytane: white-balance, navigationmode, strony pozostalych typow zlecen i pre-design.
Nazwy przyciskow przepisane z tresci stron; czesc przyciskow to ikony bez podpisu w dokumentacji - te sa tu opisane
slowami ("ikona startu", "ikona edycji") i moga wygladac inaczej.
