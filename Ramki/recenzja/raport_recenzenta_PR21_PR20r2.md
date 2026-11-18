# Raport recenzenta: PR #21 (E3-A3b, ekran wieczorny) - runda 1 oraz PR #20 (E3-A3a, rdzen) - runda 2

Data: 2026-11-18. Recenzent: swieza subsesja (Fable 5.2), niezalezna od wykonawcow i koordynatora; werdyktu innych nie znam.
Stan recenzowany: HEAD `e580101` (`origin/e3/a3b`), zawiera rdzen `dbac5a7` (`origin/e3/a3a`).
(A) ekran: `git diff origin/e3/a3a...origin/e3/a3b -- Ramki/stanowisko` (10 plikow, +3 757). (B) rdzen, runda 2:
`git diff c2f10c2..origin/e3/a3a -- Ramki/stanowisko` (13 plikow, +1 964 / -233).

Metoda. Czytanie w calosci: `ui/okno.py`, `ui/czesci.py`, `ui/mapa.py`, `ui/obraz.py`, `ui/napisy.py`, `ui/styl.py`, `ui/__init__.py`,
`statusy.py`, `aplikacja.py`; z `kontroler_api.py` czesc wspolna kontrolera (linie 546-1345) i atrapa (1640-1789); z
`test_ui_wieczor.py` narzedzia testu, testy (3), (9) i kontraktu pakietu; z `test_aplikacja.py` testy B1 i P1; linie USUNIETE z testow
w rundzie 2; opisy `aplikacja.md`, `ui_wieczor.md`, oba raporty wykonawcow, raport rundy 1; 9 zrzutow wykonawcy (1600 x 900).
Z modulow spoza zakresu tylko miejsca potrzebne do oceny (`silnik._robotnik`, `_uruchom_proces`, `_dolacz_do_obiektu_zadania`,
`session.przyjmij_wynik` - czas przyjecia, teksty `BladSesji`).

Uruchomienia - tylko PC wlasciciela (`<PC-katalog>\e3\r21`, kod z `git archive e580101`, konto `<konto-PC>`, jeden przebieg naraz,
18-19 GB wolnego RAM przed kazdym startem, `QT_QPA_PLATFORM=offscreen`, limity watkow jak u wykonawcow):
1. `testy\test_kontroler_api.py`: **53 passed** (12 s). `testy\test_aplikacja.py`: **28 passed, 1 skipped** (48 s; pominiety = wariant
   na skanach odniesienia). `testy\test_ui_wieczor.py`: **64 passed, 1 failed** (26 s) - pada
   `test_4_pula_liczenie_i_skany_wstrzymane_czekaja` (uwaga A-P4; ten sam test osobno: 25 z 25 przeszlo).
2. Powtorki pod katem bledu natywnego (z `-X faulthandler`): 12 x (4 testy startujace silnik zaraz po oknie) i 30 x (pierwsze 15
   testow pliku - dokladnie odcinek, w ktorym urwal sie przebieg wykonawcy): 42 z 42 przebiegow kod 0, 0 komunikatow
   "access violation" (84 starty procesu analizy z procesu z zaladowanym Qt).
3. Wlasny skrypt `<PC-katalog>\e3\r21\rec21.py` (atrapa, okno sterowane `QTest`; 5 prob, 15 zrzutow 1280 x 760) - wyniki przy
   uwagach ("uruchomione"). Skrypt i zrzuty zostaly na PC i w katalogu roboczym recenzenta na MSI (poza repozytorium).
Po sobie: 0 moich procesow `python.exe` na PC (w chwili kontroli dzialalo 5 procesow `python.exe` INNEGO konta - z konta
`<konto-PC>` bez dostepu; nie moje, mogly wplywac na czasy). Na MSI nie uruchamialem pytest ani okna. Pelnego pytest nie uruchamialem.

## 0. Werdykty

**(A) PR #21, ekran wieczorny: do scalenia po poprawkach - B 0 / P 5 / D 14.**
Ekran jest porzadnie zbudowany na kontrakcie: wszystkie polecenia ida przez `kontroler.wykonaj` w watku okna, kolory i podpisy
statusow pochodza wylacznie ze stanu i `statusy`, status nieznany jest zolty, nie ma okien modalnych, zaden przycisk nie przyjmuje
klawiatury (Enter / Spacja nie potwierdza pytania - sprawdzone uruchomieniem), decyzja idzie zawsze do pracy pokazanej w widoku,
a podwojne nacisniecie nie daje drugiego polecenia. Nie znalazlem sciezki, na ktorej gniazdo jest zielone wbrew stanowi.
Przed scaleniem i przed pokazem trzeba jednak poprawic trzy rzeczy potwierdzone uruchomieniem: (P1) przy deklarowanym minimum
1280 x 760 ekran sie nie miesci - przyciski "Cofnij decyzje / Nastepna / Zamknij" sa zasloniete, imiona osob i napisy przyciskow
uciete; (P2) wynik nowej plytki podmienia mape pod kursorem - klikniecie i klawisz U trafiaja w prace INNEJ plytki; (P3) trwaly
blad zapisu chowa sie pod "... i jeszcze n". **Pokaz wlascicielowi: tak, ale na ekranie co najmniej 1600 x 900 punktow przy
skalowaniu 100 % (albo po poprawce P1) i po poprawkach napisow z pkt 3.**

**(B) PR #20, rdzen po rundzie 2: do scalenia - B 0 / P 0 / D 9.**
B1 i P1-P9 z rundy 1 sa zalatwione (tabela w pkt 2.1), kazda ma test odtwarzajacy scenariusz, oba pliki testow rdzenia przechodza
na stanie koncowym. Uwagi D to granice do opisania albo drobne poprawki; zadna nie lamie regul wlasciciela w zwyklej pracy.
Poprawki napisow `statusy.py` (plik rdzenia) sa policzone w (A)-P5, bo dotycza tego, co widzi technik.

Blad natywny "access violation": przyczyny w kodzie nie znalazlem i bledu nie odtworzylem (pkt 4) - ryzyko resztkowe, do
obserwacji z konkretnymi zabezpieczeniami; nie blokuje scalenia.

## 1. (A) Ekran - uwagi (P = poprawic przed scaleniem i przed pokazem, D = drobna / do decyzji na G1)

| Nr | Waga | Plik:linia | Scenariusz (wejscie -> zly wynik) | Sprawdzone | Oczekiwane |
|---|---|---|---|---|---|
| A-P1 | P | `ui/okno.py:50` (`setMinimumSize(1280, 760)`), `:150` (`widok.setMinimumHeight(500)`), `ui/styl.py:31-32` (stale szerokosci 250 i 540), `ui/czesci.py:163-164`, `:286-316` (panele bez zawijania przyciskow), `ui/okno.py:118-125` (naglowek mapy) | Okno na ekranie 1280 x 760 (minimum z opisu) albo na laptopie 1920 x 1080 ze skalowaniem Windows 125 % (= 1536 x 864 punktow, minus pasek zadan) lub 150 % (= 1280 x 720 - mniej niz minimum okna, dol okna poza ekranem). Sam uklad potrzebuje wiecej, niz okno deklaruje: **1373-1608 x 831-844** zaleznie od stanu. Skutki przy 1280 x 760: (1) wiersz "Cofnij decyzje [C] / Nastepna [N] / Zamknij [Esc]" jest ZASLONIETY przez liste "do dofrezowania" - zostaja tylko skroty klawiszowe, ktorych nie widac; (2) w panelu zmiany osoby z przyciskow zostaje "chnik / chnik / chnik" i "dze od stan" - nie widac, kogo sie wybiera; (3) "Tak, to ponowny skan" -> "k, to ponowny ska", "Cofnij dopuszczenie" -> "dopuszc" (czyta sie jak "dopusc"), "Podaj numer plytki" -> "i numer", "Odswiez pule" -> "swiez pu"; (4) naglowek mapy "Plytka 3 - spra" / "Plytka 1 - do p" - status plytki uciety; (5) przy 3 panelach mapa (min. 340) wychodzi 34-52 px poza okno - dolny rzad gniazd i gniazdo 1 pod legenda, podpisy legendy uciete ("IBYTEI", "ij nr p"); w panelu "Podaj numer plytki" tekst nachodzi na cyfry. Przy 1600 x 900 (zrzuty wykonawcy) tych wad nie ma. Rozdzielczosc i skalowanie laptopa stanowiska sa nieznane. | **Uruchomione** (`rec21.py`, proba rozmiarow, 6 stanow x 2 rozmiary): `layout().minimumSize()` = 1373 x 831 (praca otwarta), 1483 x 831 (3 panele plytki), 1524 x 831 (zmiana osoby + 2 bledy), 1608 x 831 (36 plytek + pytanie), 1575 x 844 (bez osoby + bez numeru); lista przyciskow z `sizeHint() > size()` jak wyzej; zrzuty `A..I_1280x760_*.png`. Skalowanie 125 / 150 % - rachunkiem, nie uruchomieniem. | (a) Sprawdzic ekran laptopa stanowiska PRZED pokazem. (b) Minimum okna = to, czego uklad naprawde potrzebuje (nie ustawiac recznie mniejszego niz `minimumSizeHint`), start `showMaximized()`. (c) Uklad, ktory sie kurczy: panele uwag w obszarze przewijanym o ograniczonej wysokosci, przyciski paneli pod tekstem, gdy brakuje szerokosci, naglowek mapy z zawijaniem, widok pracy bez sztywnych 500 px. (d) Test w rozmiarze minimalnym: dla kazdego stanu z zrzutow zaden widoczny przycisk nie ma `sizeHint` wiekszego niz rozmiar, przyciski decyzji i "Cofnij" widoczne i klikalne, mapa w oknie. |
| A-P2 | P | `ui/okno.py:200-204` (`_wybierz_plytke`: nowa plytka przelacza ekran, gdy nie ma otwartej pracy), `:237-239` (`_klik_gniazdo`), `:315-320`, `:345-350` (decyzja klawiszem), `ui/czesci.py:574` (numer plytki w widoku pracy malym szarym napisem) | Technik ma na ekranie mape plytki A (bez otwartej pracy), czyta z niej, ktore prace wziac do reki, albo wlasnie celuje kursorem w czerwone gniazdo 2. W tej chwili przychodzi wynik plytki B (przy skanowaniu serii: co 40-50 s). Ekran bez pytania pokazuje mape B. (1) Klikniecie laduje w gniazdo 2 plytki B; widok pracy pokazuje "Gniazdo 2", status B, a "Plytka 2" tylko malym szarym napisem po prawej. Klawisz U (albo przycisk) zapisuje decyzje na pracy plytki B: **zdrowa praca trafia na liste "do dofrezowania" jako ukruszona, a ukruszona z plytki A zostaje bez decyzji** (wariant z O: czerwona praca plytki B dostaje "OK" za prace z A). (2) Bez klikania: technik czyta z ekranu "czerwone: 5", majac w reku plytke A. Regula wlasciciela "technik oglada czerwone i zolte prace" opiera sie na tym, ze mapa na ekranie jest mapa plytki, ktora technik ma przed soba. Wykonawca zglasza przelaczanie jako decyzje nr 3 do G1; test `test_nowa_plytka_nie_zabiera_otwartej_pracy` to zachowanie utrwala. | **Uruchomione** (`rec21.py`, proba "nowa plytka pod kursorem"): po `symuluj_skan` plytki B klikniecie w punkt gniazda 2 plytki A -> `pokazana = B`, widok "Gniazdo 2 / Plytka 2 / OK"; klawisz U -> `ukruszona(praca plytki B)`, decyzja B/2 = `ukruszona_niewykryta`, A/2 = brak. | Nie przelaczac ekranu, gdy pokazana plytka ma prace do obejrzenia bez decyzji (albo gdy technik dotykal ekranu w ostatnich kilku sekundach): nowa plytka = znaczek "NOWA" i wyrazny pasek "Jest wynik plytki nr X - pokaz". Gdy przelaczenie zostaje: klikniecia w mape pomijane przez ok. 0,5 s po podmianie mapy, a numer plytki w widoku pracy duzy (obok "Gniazdo n"). Test: klikniecie zaraz po nowym stanie nie otwiera pracy innej plytki. |
| A-P3 | P | `ui/okno.py:491-499` (kolejnosc: odmowa, numer, pytania plytki, komunikaty plytki, dopiero potem ogolne; `PANELI = 3`, `:32`), `:463-466` (bledy pierwsze tylko wsrod ogolnych); `opisy_modulow/ui_wieczor.md:20` ("trwaly `blad_zapisu` nie chowa sie pod 'i jeszcze n'") | Pokazana plytka ma 3 wlasne panele (np. pytanie o ponowny skan + "Praca niesprawdzona" + "Skan do powtorzenia" - zwykly stan plytki do powtorzenia skanowanej drugi raz). Wtedy przychodzi blad zapisu wyniku (pelny dysk) i znika folder skanera. Oba komunikaty poziomu "blad" sa schowane pod szarym napisem 14 px "... i jeszcze 2 (zamknij powyzsze, zeby zobaczyc)". Zostaje kafelek "nie zapisano" na liscie plytek i "czekaja na zapis: 1" na pasku (przy 1280 px uciete do "czekaja na zapi"). Opis modulu twierdzi, ze tak sie nie stanie. Wazne PYTANIE nie moze byc schowane przez komunikaty (pytania ida przed nimi) - tylko przez tekst odmowy i trzy pytania jednej plytki naraz (rzadkie). | **Uruchomione** (`rec21.py`, proba "blad zapisu schowany"): panele = `pytanie_ponowny_skan`, `komunikat_blad_inspekcji`, `komunikat_skan_do_powtorzenia`, "... i jeszcze 2"; w stanie `blad_zapisu` (blad) i `folder_skanera_niedostepny` (blad). Zrzut `G_1280x760_blad_zapisu_schowany.png`. | Komunikaty poziomu `blad` (a co najmniej trwale) zawsze widoczne, przed komunikatami plytki poziomu ostrzezenie; limit 3 tylko dla reszty albo obszar paneli przewijany. Poprawic zdanie w `ui_wieczor.md`. Test jak proba. |
| A-P4 | P | `testy/test_ui_wieczor.py:926-927` (asercja "liczenie trwa" po `e.klik`, ktore czeka 5 ms i obsluguje zdarzenia), `:162` (zegar lacznika 30 ms wola `przetworz()` atrapy), `kontroler_api.py:1542-1556` (atrapa konczy liczenie w `przetworz`) | Test zalezy od fazy zegara lacznika: gdy tykniecie 30 ms wypadnie miedzy kliknieciem "Odswiez pule" a asercja, atrapa konczy liczenie i przycisk jest juz aktywny -> `AssertionError`. W pelnym przebiegu pliku u mnie: 1 failed z 65; ten sam test osobno 25 z 25. Falszywy alarm w pelnym pytest (kryterium "0 failed"). To wada testu, nie ekranu. | **Uruchomione**: 1 x caly plik (64 passed, 1 failed, slad w `trzy.log`), 25 x sam test (25 passed). Przyczyna - czytaniem. | Na czas tej asercji zatrzymac zegar lacznika (`e.lacznik.zatrzymaj()` / wlasny krok `przetworz`) albo sprawdzac stan zaraz po poleceniu bez `odczekaj`. Przejrzec pozostale asercje "stan przejsciowy" w pliku pod tym samym katem. |
| A-P5 | P | `statusy.py:172`, `:176`, `:67`, `:260-263`, `:283-285`; `ui/napisy.py:43`, `:99-101`; `ui/okno.py:429-430`; `kontroler_api.py:1138-1139` | Napisy, ktore moga wprowadzic technika w blad albo sa bledne jezykowo - lista "bylo -> ma byc" w pkt 3 (pozycje 1-9 przed pokazem). Najwazniejsze: plytka z nieobejrzanymi czerwonymi pracami ma w naglowku i na kafelku status **"sprawdzona"** ("Plytka 3 - sprawdzona") - czyta sie jak "plytka zalatwiona"; przycisk "Podaj numer plytki" przy plytce, ktora numer MA; plytka poranna po dopuszczeniu niczym sie nie rozni od zwyklej ("sprawdzona", zielone gniazda); "Programu nie udalo sie zapisac" (blad jezykowy); rada "Wskaz wlasciwy folder", choc ekran nie ma jak wskazac folderu. | Zrzuty wykonawcy 1-9 i moje; czytanie `statusy.py`, `napisy.py`. | Pkt 3. |
| A-D1 | D | `ui/okno.py:338-361`, `:315-320` | Jedno nacisniecie U / O / C przy otwartej pracy = zapisana decyzja, bez potwierdzenia, takze gdy na ekranie jest panel pytania (np. "ponowny skan?" - decyzja na nowym skanie zostaje przyjeta przed odpowiedzia). Przypadkowe "O" na czerwonej pracy = "zatwierdzona OK". Slad na ekranie jest (kolor gniazda, "Decyzja: OK - osoba, godzina"), cofniecie jednym klawiszem. Enter, Spacja, T, Y nie odpowiadaja na pytanie; Spacja przy pytaniu = tylko "start skanu"; O dwa razy = jedno polecenie. | **Uruchomione** (proba "klawisze przy pytaniu"). | Do swiadomego zatwierdzenia na G1 (decyzja nr 4 wykonawcy). Rozwazyc: skroty decyzji nieaktywne, gdy pokazana plytka ma otwarte pytanie. |
| A-D2 | D | `ui/mapa.py:29-51` (`geometria_ukladu`: `uklad.wczytaj` i `kontroler.ust` spoza interfejsu), `ui/okno.py:400`, `:487` | Obejscie zgloszone przez wykonawce. Ryzyko: (1) okno i kontroler moga wczytac uklad z roznych katalogow tylko wtedy, gdy kontroler nie ma atrybutu `ust` (atrapa) - wtedy katalog domyslny; skutek najwyzej "mapa w kratke" (bezpieczne: kolory i numery ze stanu); (2) pierwsze wczytanie ukladu dzieje sie w watku okna (plik + numpy; kontroler laduje numpy przy starcie, wiec dziesiatki ms raz na uklad); (3) nieudane wczytanie jest pamietane do konca pracy programu (chwilowy blad dysku = kratka do restartu). Orientacja mapy (x w prawo, y w gore, przod na dole) jest taka sama jak w `ui_test.py:116` i `porownaj.mapa_png` - sprawdzone czytaniem. | Czytaniem. | Docelowo `kontroler.uklad_plytki(nazwa)` w kontrakcie (POTRZEBUJE 1 wykonawcy). Na teraz: nie pamietac wyniku `None`. Zgodnosc mapy z prawdziwa plytka (lustro!) - na G1 z plytka w reku. |
| A-D3 | D | `ui/obraz.py:21` (`PROG_ODCHYLKI_MM = 0.08`), ustawienie `[inspect] prog_glebokosci_mm` (`ustawienia.przyklad.toml:50`) | Prog kolorowania obrazu odchylek jest stala ekranu, a prog wykrywania jest ustawieniem. Po zmianie ustawienia (np. 0,06) praca oznaczona "UBYTEK 0,07 mm" ma obraz caly szary - technik nie widzi wskazanego miejsca i moze uznac alarm za falszywy. Dzis wartosci sa rowne. | Czytaniem. | Prog z ustawien kontrolera albo pole w `SzczegolyPracy` (POTRZEBUJE 4). |
| A-D4 | D | `ui/okno.py:507-509` (panel jednakowych komunikatow: jedno polecenie na komunikat), `kontroler_api.py:1235-1243` | "Zamknij" na panelu "Ten sam projekt w dwoch gniazdach (16 razy)" = 16 polecen, kazde z budowa stanu z bazy i odswiezeniem ekranu: **337 ms** w watku okna przy 37 plytkach (prog paczki 200 ms). Reszta przy 36 plytkach x 18 prac miesci sie w progu: pelne odswiezenie ekranu 48 ms, klikniecie "Ukruszona" 30 ms, nowy stan z bazy + ekran 20 ms. | **Uruchomione** (proba "36 plytek"). | Jedno polecenie na grupe (np. `zamknij_komunikat` z lista albo zamykanie bez odswiezania posredniego). |
| A-D5 | D | `ui/czesci.py:199-201` (przycisk "Odswiez pule" nieaktywny w stanie `liczenie`) | Liczenie puli, ktore zawislo (folder sieciowy nie odpowiada - granica zgloszona w rdzeniu): jedyne wyjscie, czyli nowe "Odswiez pule" (nowy watek, nowy numer liczenia), jest na ekranie nieaktywne bez konca; pomaga tylko restart programu. | Czytaniem. | Przycisk aktywny ponownie po kilkunastu sekundach liczenia. |
| A-D6 | D | `ui/okno.py:459-464` | Komunikaty przypisane do plytki INNEJ niz pokazana nie sa nigdzie widoczne (ani jako ogolne, ani przy plytce); kafelek oznacza tylko pytania ("czeka na odpowiedz"). Status plytki na kafelku ("analiza nie powiodla sie", "do ponownego skanu") czesciowo to ratuje; "Praca niesprawdzona (gniazdo 7)" plytki niepokazanej - nie. | Czytaniem. | Znaczek "ma komunikat" na kafelku albo licznik komunikatow innych plytek. |
| A-D7 | D | `ui/mapa.py:245-252` (podpis od 18 do 8 px, bez skrotu), `ui/styl.py:41-42` (`tekst_na`: prog jasnosci 140) | Czytelnosc gniazd: przy promieniu gniazda ponizej ok. 25 px (plytka poranna 24-31 gniazd z jednym panelem, kazda plytka z 3 panelami, okno 1280 px - zmierzone 17,9-22,3 px) podpis ma 8 px i mimo to bywa uciety ("KRUSZON", "prawian recznie", "blad control"); przy 1600 x 900 z panelem pytania: 8-10 px. Bialy napis na zielonym `#3cb44b` ma kontrast ok. 2,7 : 1 (czarny mialby ok. 7,8 : 1); bialy na morskim `#009688` ok. 3,7 : 1. Rozroznienie czerwone / zielone przy malych gniazdach zostaje wtedy samemu kolorowi (osoby nierozrozniajace czerwieni i zieleni). | **Uruchomione** (promienie z proby rozmiarow, zrzuty); kontrast - rachunkiem. | Gdy podpis sie nie miesci: sam numer + kolor + znak (np. "!" dla czerwonego), pelny napis w legendzie i w widoku pracy; krotsze podpisy w `statusy` (pkt 3); `tekst_na` wg jasnosci wzglednej (czarny na zielonym). |
| A-D8 | D | `ui/okno.py:526-531` (`_bez_obrazu`), `ui/obraz.py:83-95` | Obraz odchylek, ktorego nie udalo sie wczytac raz (plik chwilowo zajety, blad dysku), ma "Brak obrazu tej pracy" do zamkniecia programu - ponownej proby nie ma. | Czytaniem. | Ponowna proba przy kolejnym otwarciu pracy. |
| A-D9 | D | `ui/okno.py:245-251` | Klikniecie pozycji listy "Wszystkie otwarte" z poprzedniej doby nic nie robi i nic nie mowi (plytki nie ma w stanie tej doby). | Czytaniem. | Krotki napis "praca z dnia ... - plytki nie ma na mapie tej doby". |
| A-D10 | D | `ui/czesci.py:384-422`, zrzut 4 | Lista plytek: dwa kafelki "Plytka 1" rozni tylko godzina; liczniki to kolorowe liczby bez opisu; przy 3 numerach plytek i 30+ plytkach na zmiane (ta sama plytka wraca czesciej niz co 60 min) pytanie "ponowny skan?" i znaczek "czeka na odpowiedz" pojawia sie przy PRAWIE KAZDEJ plytce (w probie: 33 pytania na 36 plytek), a przed odpowiedzia dochodzi panel "Ten sam projekt w dwoch gniazdach (n razy)" (POTRZEBUJE 2 wykonawcy). To skutek reguly 60 min, nie wada ekranu - ale wlasciciel powinien to zobaczyc na pokazie. | **Uruchomione** (proba "36 plytek"), zrzut `H_1280x760_36_plytek.png`. | Do decyzji wlasciciela (G1). Konflikty projektu miedzy skanem a skanem, ktory ten proponuje zastapic, nie powinny byc pokazywane przed odpowiedzia. |
| A-D11 | D | `kontroler_api.py:1138-1139` -> panel "Nie mozna tego zrobic" (`ui/czesci.py:356-359`) | Odmowa `session` jest pokazywana technikowi surowym tekstem wyjatku: bez polskich znakow, z numerami wierszy bazy ("praca 20: skan 5 ma status 'zastapiony' - decyzje mozna podejmowac ..."). Nazw plikow w tych tekstach nie ma (przejrzalem wszystkie `raise BladSesji`). Zwykle przyciski sa wtedy nieaktywne, wiec technik zobaczy to rzadko. | Czytaniem. | Kody odmow -> teksty dla czlowieka w `statusy`. |
| A-D12 | D | `ui/czesci.py:186-198`, `ui/napisy.py:20` | "Skaner: gotowy" znaczy tylko "folder skanera jest dostepny i obserwator dziala" - o samym skanerze program nic nie wie. Dopoki akcja "start skanu" jest atrapa (do B2), "Skanuj (Spacja)" pokazuje "czekam na skan..." i niczego w skanerze nie uruchamia. | Czytaniem. | Na pokazie powiedziec to wlascicielowi wprost; napis "czekam na plik skanu". |
| A-D13 | D | `testy/test_ui_wieczor.py` | 9 kryteriow jest sprawdzanych naprawde przez ekran: klikniecia i klawisze `QTest`, kolor czytany z piksela obrazu widzetu, (9) na prawdziwym kontrolerze z plikami w folderze skanera, baza czytana dopiero na koncu. Czego testy nie obejmuja: rozmiaru innego niz 1600 x 900 (A-P1), klikniecia zaraz po przelaczeniu plytki (A-P2 - test utrwala przelaczanie), wiecej niz 3 paneli z bledem ogolnym (A-P3), 30+ plytek, prawdziwej analizy (funkcja sztuczna). (6) mierzy 10 plytek. | Czytaniem + przebieg. | Dopisac testy przy poprawkach P1-P3. |
| A-D14 | D | `ui/okno.py:367-378`, `ui/obraz.py:141-143` | Zamkniecie okna czeka do 3 s na watek obrazu (`waitForDone(3000)`) w watku okna; gdy obraz liczy sie dluzej, watek pomocniczy wysyla sygnal do obiektu w trakcie usuwania (wyjatek `RuntimeError` jest lapany, wyscig z niszczeniem obiektu C++ - nie). Tylko przy zamykaniu programu z obrazem w toku. | Czytaniem. | `waitForDone()` bez limitu albo flaga "koniec" sprawdzana przed `emit`. |

## 2. (B) Rdzen, runda 2

### 2.1 Stan uwag rundy 1

| Uwaga | Stan | Test odtwarza scenariusz | Uwagi recenzenta |
|---|---|---|---|
| B1 drugi egzemplarz | **zalatwiona** | tak: druga `Aplikacja`, drugi proces `main()` (kod 3, 0 wpisow w bazie, log niezalozony), proces zabity -> blokada wolna, wynik tresci juz zapisanej odsiany | blokada zajmowana przed baza, logiem i folderem skanera; odpowiedzi na pytania o blokade: pkt 2.2 |
| P1 blad zapisu inny niz "baza zajeta" | **zalatwiona** | tak: `database or disk is full`, `OSError(28)`, `disk I/O error`; samoczynne ponowienia, `ponow_zapis`, zamkniecie z pozycja niezapisana | zapis podwojny po odzyskaniu bazy: nie znalazlem sciezki (pkt 2.2); R2-D1 |
| P2 plik przemianowany w kolejce | **zalatwiona** (z opisanym wyscigiem) | tak: obie drogi (kolejka silnika i "brak pliku") | wyscig "brak pliku przed zdarzeniem nowej nazwy" = plytka `blad` obok poprawnej - opisany w granicach; akceptowalne do B2 |
| P3 pula oprozniona po policzeniu | **zalatwiona** | tak | koszt i zawieszone liczenie: R2-D3 |
| P4 zielony bez inspekcji "ok" | **zalatwiona** | tak: tabela wszystkich par + oba kontrolery | - |
| P5 nazwy plikow w logu | **zalatwiona** dla `stanowisko.log` | tak: nazwisko w nazwie pliku skanu, caly katalog `dane/` (takze `silnik.log`, ale z funkcja analizy sztuczna) | R2-D2, R2-D4 |
| P6 atrapa inna niz kontroler | **zalatwiona** | tak: sekwencja 40 polecen, te same odpowiedzi | - |
| P7 lista w pliku | **zalatwiona** | tak | plik zapisywany w watku okna przy kazdej zmianie listy (maly) |
| P8 blad analizy przy zajetej bazie | **zalatwiona** | tak | - |
| P9 kopie wynikow i podglady | **zalatwiona** | tak | - |
| D1-D15 | zrobione albo opisane jako znane (D5, D8, D13 f) | D1, D2, D6, D7, D11 maja testy | - |

### 2.2 Odpowiedzi na pytania ze zlecenia

**Blokada jednego egzemplarza** (`aplikacja.py:170-219`, czytaniem). Awaria / zabicie procesu: blokade bajtu zwalnia system razem
z procesem (test). Dwa konta Windows albo dwie sesje pulpitu na jednym komputerze: blokada bajtu pliku dziala miedzy sesjami i kontami;
gdy drugie konto nie ma prawa zapisu do pliku `<baza>.blokada`, `os.open` konczy sie `PermissionError` -> `main()` pokazuje "Nie mozna
przygotowac folderu danych" i kod 2 (program nie startuje - bezpiecznie, komunikat mylacy). Start drugiego egzemplarza w trakcie
startu pierwszego: blokada jest pierwsza czynnoscia po wczytaniu ustawien, przed logiem i baza - okna wyscigu nie ma. Baza na dysku
sieciowym: blokada dziala o tyle, o ile serwer plikow honoruje blokady zakresow bajtow; KAZDY `OSError` z `msvcrt.locking` jest
tlumaczony na "program juz dziala" (R2-D5); sama baza SQLite na udziale sieciowym nie jest bezpieczna niezaleznie od tej paczki -
dopisac do granic "baza tylko na dysku lokalnym". Uchwyt blokady nie jest dziedziczony przez proces analizy (deskryptory Pythona
sa niedziedziczone, `spawn` z `bInheritHandles = False`).
**Kontrola `sha16` w transakcji** (`aplikacja.py:909-934`): odsiewa wynik tylko wtedy, gdy ta sama TRESC pliku (skrot) ma juz skan
ze statusem innym niz `blad`. Ponowny skan tej samej plytki daje inny plik (inny skrot), wiec regula 60 min nie jest blokowana;
blokowany jest tylko ten sam plik skopiowany / zapisany drugi raz - zgodnie z regula "zaden skan dwa razy". Skan `blad` wolno
policzyc ponownie.

**P1 / P8 - zapis dwa razy po odzyskaniu bazy?** Nie znalazlem sciezki: pozycja jest zapisywana w jednej transakcji
`BEGIN IMMEDIATE` razem z kontrola `sha16`; ponowienia (zegar i `ponow_zapis`) ida w jednym watku, pozycja znika z listy dopiero po
udanym zapisie; nieudane zatwierdzenie cofa calosc. Zamkniecie programu z pozycjami niezapisanymi: ostatnia proba, potem zadanie do
pliku zadan i analiza od nowa po starcie (test); gdy i pliku zadan nie da sie zapisac (pelny dysk) - skan wraca przez nadrabianie
folderu, bo nie ma wiersza w bazie. Uboczne: R2-D1.
**P3 - koszt.** Liczenie puli (`rglob` po calym folderze) startuje przy kazdym nowym skanie, wyniku i bledzie analizy, w watku
pomocniczym, najwyzej jedno naraz - okna nie blokuje; na folderze sieciowym z tysiacami plikow to stale obciazenie (plus silnik
listuje folder przy kazdym zadaniu). Do pomiaru na prawdziwym folderze (A4 / A5). Zawieszone liczenie: R2-D3.
**P5 - zasieg filtra.** Filtr jest na uchwycie pliku `stanowisko.log` (obejmuje wpisy WSZYSTKICH loggerow trafiajace do tego pliku)
i dodatkowo na 11 loggerach programu (dla `caplog` / konsoli). `silnik.log` (wyjscie bibliotek z procesu analizy) jest poza filtrem:
ostrzezenia Pythona z analizy sa przechwytywane do wyniku i czyszczone (`silnik.py:659-671`), moduly analizy nie loguja przez `logging`
(przejrzalem `porownaj`, `match`, `synth`, `inspect`, `plate`, `krawedz`, `katalog`), wiec do pliku trafia to, co biblioteki (Open3D,
trimesh) drukuja same - nazw projektow tam nie oczekuje, ale tego nie zmierzylem, a test (i) sprawdza to tylko na funkcji sztucznej. Czy filtr wycina tresc potrzebna do diagnozy: R2-D2.
**Kontrakt.** Nowe pola maja wartosci domyslne, nowe polecenia sa dopisane, `ZamrozonySlownik` czyta sie jak slownik - okno z wersji 1
dziala. "Wszystkie addytywne" jest lekko na wyrost: cztery ZMIANY zachowania (opisane w `aplikacja.md`): `dane` w odpowiedzi
`ustaw_pule` / `odswiez_pule` (stan puli zamiast liczby / None), `wybierz_operatora(None)` (wylogowanie zamiast "bez zmian"), statusy
P4 (czesc dawnych zielonych jest zolta), `odswiez_pule` atrapy przez `liczenie`. Atrapa a prawdziwy kontroler: test sekwencji 40
polecen przechodzi.
**Pole `skan` = `sha16`.** Szukalem czytelnikow pola `skan` wyniku: `porownaj.tabela` / `mapa_png` / `main` (wiersz polecen, wynik
prosto z analizy), `narzedzia/metryki_*`, `auto_uklad` (pliki z wiersza polecen), `import_decyzji` (wlasny format wejscia), testy
`test_silnik` (wynik z silnika, przed podmiana). Plikow wynikow SESJI (`dane/wyniki`) po polu `skan` nie czyta nic (sesja, kontroler,
okno, okno testowe). Zmiana bezpieczna.
**Testy rundy 1.** Przejrzalem wszystkie linie usuniete z trzech plikow testow: zamiany `spij` na plik-brame, test (i) rozszerzony
(nazwisko w nazwie pliku, lista przez kontroler), `test_g_pula` z faza `liczenie`, `pamiec_linii` w tabeli domyslnych, zegar w tescie B1.
Oslabienia nie znalazlem (nie porownywalem kazdej pary linia po linii).

### 2.3 Uwagi D (runda 2)

| Nr | Plik:linia | Scenariusz (wejscie -> zly wynik) | Sprawdzone | Oczekiwane |
|---|---|---|---|---|
| R2-D1 | `aplikacja.py:666-668`, `:872-902`; `session.py:328` (`czas_analizy = teraz` w chwili ZAPISU) | Wynik czekajacy na zapis dostaje czas przyjecia z chwili udanego zapisu, nie skanu. (1) Baza zajeta / dysk przez kilkanascie minut: okno 60 min "ponowny skan" i doba / zmiana skanu licza sie od zapisu (skan z 13:58 zapisany o 14:01 nalezy do zmiany 2; skan z 05:58 zapisany po 06:00 - do nastepnej doby). (2) Gdy pozycja czeka na termin ponowienia (do 30 s), a wynik NASTEPNEJ plytki zapisze sie pierwszy, kolejnosc skanow w bazie jest odwrocona - przy tym samym numerze plytki pytanie "ponowny skan" wskaze starszy skan jako nowszy. Waskie okno (analiza trwa 30-50 s), ale mozliwe. | Czytaniem. | Przed zapisem nowego wyniku sprobowac zapisac pozycje czekajace (kolejnosc FIFO); czas skanu z chwili odebrania wyniku przekazywany do sesji (wymaga parametru w `session` - POTRZEBUJE). |
| R2-D2 | `aplikacja.py:245-255` (`zapamietaj`: takze sam rdzen nazwy pliku, od 3 znakow), `:257-259` (`_jak_plik`: kazdy napis z `/` lub `\` albo konczacy sie kropka i 1-5 znakami), `:269-275` | Filtr bywa za gorliwy: (1) gdy skaner zapisuje pod stala nazwa typu `skan.stl`, rdzen "skan" jest od tej chwili zamieniany na `sha16` w CALYM tekscie kazdego wpisu ("stanowisko: <sha16> <sha16> przyjety...") - log trudny do czytania; (2) argument-napis z ukosnikiem (np. tekst bledu "disk I/O error" przekazany jako napis) albo nazwa z kropka ("stanowisko.baza") staje sie `<plik>`. Wyjatki przekazane jako obiekty i typy bledow zostaja. Bezpieczne dla danych osobowych, kosztem diagnozy. | Czytaniem. | Zamieniac rdzen nazwy tylko jako cale slowo i od ok. 6 znakow; `_jak_plik` dla napisow bez spacji. |
| R2-D3 | `aplikacja.py:502-528`, `:550-565`, `:799-804` | Liczenie puli, ktore nie wraca (folder sieciowy wisi): po pierwszym bledzie analizy wszystkie kolejne skany sa wstrzymane bez komunikatu (pasek: "czekaja na uruchomienie analizy: n" - mylace), do recznego "Odswiez pule" (por. A-D5). Wykonawca zglasza jako znane. Zwykle odlaczony udzial konczy sie bledem po kilkudziesieciu sekundach, wiec przypadek rzadki. | Czytaniem. | Limit czasu liczenia (np. 60 s -> `brak_folderu` + komunikat). |
| R2-D4 | `aplikacja.py:226-227`, `:1055-1073`; `silnik.py:684-692` | `silnik.log` poza `FiltrNazw` (znane). Ryzyko male (pkt 2.2), niezmierzone na prawdziwej analizie z projektem, ktorego nie da sie wczytac. | Czytaniem. | Przy najblizszym przebiegu na danych odniesienia przeszukac `silnik.log` pod katem nazw plikow puli. |
| R2-D5 | `aplikacja.py:195-198`, `:1165-1170` | Kazdy `OSError` blokady (takze "udzial nie obsluguje blokad") = komunikat "program juz dziala"; brak prawa zapisu do pliku blokady = "Nie mozna przygotowac folderu danych". Program nie startuje (bezpiecznie), ale technik szuka drugiego okna, ktorego nie ma. | Czytaniem. | Rozroznic naruszenie blokady od innych bledow. |
| R2-D6 | `aplikacja.py:197-198`, `:1169`, `:1184` | Komunikaty startu pokazywane technikowi w okienku sa bez polskich znakow ("Program "Stanowisko" juz dziala na tym komputerze ... przejdz do otwartego okna programu"). | Czytaniem. | Teksty do `statusy` z polskimi znakami. |
| R2-D7 | `aplikacja.py:925-934` | Wyjatek PO zatwierdzeniu transakcji (np. `threading.Thread.start` w `_policz_pule`, `:934`) trafia do galezi "blad danych": plik podgladu wlasnie zapisanego skanu jest usuwany (`:897`), a proba zapisu bledu konczy sie wpisem `wynik_powtorzony`. Skan zostaje jeden i poprawny; ginie tylko obraz odchylek. Teoretyczne. | Czytaniem. | Czynnosci po zatwierdzeniu poza `try` zapisu. |
| R2-D8 | `opisy_modulow/aplikacja.md:35` | "wszystkie addytywne" - patrz pkt 2.2 (cztery zmiany zachowania). | Czytaniem. | Jedno zdanie w opisie. |
| R2-D9 | `aplikacja.py:89-93` | `_blad_zapisu` uznaje za "blad dysku" kazdy `sqlite3.OperationalError`, takze trwaly (np. niezgodny schemat bazy): pozycja jest ponawiana bez konca z rada "sprawdz dysk". Skan nie ginie. | Czytaniem. | Po N nieudanych probach inny tekst ("zglos awarie"). |

## 3. Napisy - konkretne poprawki (bylo -> ma byc)

Zapis tutaj bez polskich znakow (raport jest ASCII) - w kodzie oczywiscie ze znakami. Pozycje 1-9: przed pokazem.

| Nr | Plik:linia | Bylo | Ma byc | Dlaczego |
|---|---|---|---|---|
| 1 | `statusy.py:172` | status plytki "sprawdzona" | "przeanalizowana" (albo "skan przyjety") | "Plytka 3 - sprawdzona" przy nieobejrzanych czerwonych pracach czyta sie jak "zalatwiona" |
| 2 | `ui/okno.py:429-430` + `statusy.py:195` | przycisk "Podaj numer plytki" przy plytce z numerem | "Zmien numer plytki" (gdy numer jest) | plytka ma numer w naglowku, a przycisk sugeruje, ze nie ma |
| 3 | `ui/napisy.py:99-100` + `statusy.py:302-304` | rada "To plytka poranna - przeloz prace na plytke wieczorna i zeskanuj ponownie." i zaraz pod nia "To plytka poranna - program pracuje w trybie..." | rada: "Przeloz prace na plytke wieczorna i zeskanuj ponownie."; tekst: "To plytka poranna, a program pracuje w trybie "Wieczor". Skan jest zablokowany: nic nie jest zielone i nie mozna zapisywac decyzji." | to samo zdanie dwa razy; "podejmowac decyzji" -> "zapisywac decyzji" |
| 4 | `statusy.py:176` | "zablokowana - plytka nie z tego trybu" | "zablokowana (plytka nie z tego trybu)" | w naglowku wychodzi "Plytka 4 - zablokowana - plytka nie z tego trybu" |
| 5 | `kontroler_api.py:926-937` / naglowek mapy | plytka poranna po "Dopusc te plytke": "Plytka 4 - sprawdzona" | "Plytka 4 - dopuszczona (plytka poranna)" w naglowku i na kafelku | swiadome dopuszczenie powinno zostac widoczne dla nastepnej osoby |
| 6 | `statusy.py:283-285` | "Programu nie udalo sie zapisac wynikow skanow ({ile}) - sprawdz dysk..." | "Program nie mogl zapisac wynikow skanow ({ile}) - sprawdz dysk..." | blad jezykowy |
| 7 | `statusy.py:260-263` | "Wskaz wlasciwy folder i kliknij "Odswiez pule"." | "Sprawdz, czy pliki projektow sa w folderze projektow, i kliknij "Odswiez pule". Jesli folder jest inny - zglos to." | ekran nie ma jak wskazac folderu (`ustaw_pule` poza paczka) |
| 8 | `ui/napisy.py:43`, `:62` | "Plytka ?" i tytul "Plytka ?: Podaj numer plytki" | "Plytka bez numeru"; tytul panelu: "Podaj numer plytki" (bez przedrostka, gdy numeru nie ma) | "?:" wyglada jak blad |
| 9 | `statusy.py:67`, `:66` | podpisy gniazd "po ponownym skanie", "skan ponownie" | "powtorz skan" (dla obu, opis rozroznia) albo "czeka na skan" / "poruszony" | "po ponownym skanie" nie mowi, co zrobic; dlugie podpisy nie mieszcza sie w gniezdzie (A-D7) |
| 10 | `statusy.py:280-281` | "Program dopasowal ten sam projekt do prac w 2 miejscach - sprawdz, ktora praca jest ktora." | "Ten sam projekt pasuje do dwoch prac (gniazda X i Y) - sprawdz, ktora jest ktora." | bez numerow gniazd technik nie wie, co sprawdzic; panel "(15 razy)" bez listy |
| 11 | `ui/napisy.py:61` | "... i jeszcze {n} (zamknij powyzsze, zeby zobaczyc)" | "... i jeszcze {n} - zamknij powyzsze, zeby je zobaczyc" (i wiekszy, wyrazny napis) | szary 14 px napis pod panelami jest latwy do przeoczenia (A-P3) |
| 12 | `ui/napisy.py:96` | "plik listy zapisany o {godzina}" | "Lista zapisana do pliku o {godzina}" | - |
| 13 | `ui/napisy.py:82` | "{decyzja} (program jej nie wskazal)" | "{decyzja} (program tego nie wykryl)" | "jej" nie ma do czego sie odnosic |
| 14 | `statusy.py:343-344`, `ui/napisy.py:18` | "16 STL w puli", "0 STL w puli" | "16 plikow projektow", "brak plikow projektow" | "STL" i "pula" to zargon programisty |
| 15 | `ui/napisy.py:20-21` | "gotowy", "czekam na skan..." | "folder skanera dostepny", "czekam na plik skanu..." | A-D12 |
| 16 | `statusy.py:286-287` | "Okno podalo zle dane do polecenia "{polecenie}"..." | "Blad programu - nic nie zostalo zapisane. Zglos to (polecenie "{polecenie}")." | technik nie wie, co to "okno podalo" |
| 17 | `statusy.py:268` | "Bez tego decyzje nie sa zapisywane." | "Bez tego nie mozna zapisywac decyzji." | strona bierna sugeruje, ze decyzje gina po cichu |
| 18 | `ui/czesci.py:413-418` | liczniki na kafelku: same liczby w kolorach | podpowiedz (tooltip) z nazwa statusu albo legenda nad lista | A-D10 |

## 4. Blad natywny "Windows fatal exception: access violation"

Co wiadomo z logu wykonawcy (`<PC-katalog>\e3\a3b\pytest_ui.log`, czytalem): po 13 zaliczonych testach trzy komunikaty "access
violation" z rzedu; watek zglaszajacy to `silnik-nadzorca` w `multiprocessing/popen_spawn_win32.py:75` (wywolanie
`_winapi.CreateProcess` - kod systemu, nie Pythona), obok watek bez ramek Pythona (dopiero tworzony - `Aplikacja.start()` uruchamia
w tym czasie watki obserwatora i liczenia puli). **Po komunikatach w logu jest jeszcze kropka** - test 14
(`test_3_spacja_prawdziwy_kontroler`) zostal ZALICZONY, a log urywa sie pozniej bez podsumowania; kodu wyjscia procesu nie zapisano.
`faulthandler` (wlaczany przez pytest) wypisuje ten komunikat przy kazdym wyjatku naruszenia dostepu, takze takim, ktory system
obsluguje sam wewnatrz `CreateProcess` - kropka po komunikatach wskazuje, ze te trzy wyjatki zostaly obsluzone i program szedl
dalej. Dlaczego proces potem zniknal, z logu nie wynika (mozliwosci: prawdziwa awaria chwile pozniej, zabicie procesu z zewnatrz,
zerwana sesja ssh).

Ocena czytaniem - kandydaci ze zlecenia:
- **Kolejnosc importow Qt / Open3D:** proces okna w tym tescie nie laduje Open3D ani trimesh (`uklad` - tylko numpy; `scanner`,
  `session`, `baza` - biblioteka standardowa); Qt jest ladowane przed silnikiem w tescie (`_qt_przed_silnikiem`) i w `main()`
  (`aplikacja.py:1137`). Proces analizy nie laduje Qt (`ui/__init__.py` bez Qt; test `test_pakiet_ui_bez_qt...`). Nie tu.
- **Proces potomny dziedziczacy uchwyty Qt:** `spawn` wola `CreateProcess` z `bInheritHandles = False`; uchwyt blokady i pliki
  logu nie sa dziedziczone. Nie tu.
- **Watek uruchamiajacy proces:** `CreateProcess` z watku innego niz glowny jest dozwolone; `multiprocessing` robi tak zawsze,
  gdy `Process.start()` wola watek. Kod `_dolacz_do_obiektu_zadania` (ctypes z zadeklarowanymi typami argumentow) jest wolany PO
  `p.start()` - a wyjatek jest W `CreateProcess`. `stop()` w trakcie `p.start()` jest obsluzony (`silnik.py:948-956`). Zmian
  srodowiska procesu (`os.environ`) w trakcie pracy programu nie ma.
- **Ekran:** jedyny watek pomocniczy ekranu (`ui/obraz.py`) w tescie 14 nie pracuje (nikt nie otwieral pracy); `QImage` jest
  kopiowany przed zwolnieniem bufora (`obraz.py:36`, `:56`). Wyscig przy zamykaniu okna z obrazem w toku: A-D14 (tu nie zaszedl).
Nie odtworzylem: 42 przebiegi z `-X faulthandler` (84 starty procesu analizy), 0 komunikatow, kod 0.

Wniosek: **nie znalazlem przyczyny w kodzie PR #21 ani PR #20; najbardziej prawdopodobne sa wyjatki obslugiwane wewnatrz systemu przy
tworzeniu procesu (srodowisko PC: konto `<konto-PC>` uruchamia `python.exe` z profilu innego konta), widoczne tylko dlatego, ze
pytest wlacza `faulthandler`** - ale tego nie udowodnilem, a urwanego przebiegu nie umiem wyjasnic. Poniewaz w produkcji taka
awaria = zamkniecie programu w trakcie pracy, proponuje (male, poza zakresem obu PR albo w A11):
1. przebiegi testow zapisuja kod wyjscia procesu (`echo %errorlevel%`) - nastepnym razem bedzie wiadomo, czy to awaria (kod
   0xC0000005), czy zabicie z zewnatrz;
2. `faulthandler.enable(plik w dane/logi)` w `main()` i lokalne zrzuty awarii Windows dla `python.exe` na laptopie stanowiska;
3. `uruchom_stanowisko.bat`: po kodzie wyjscia innym niz 0 / 2 / 3 uruchomic program ponownie (skany nie gina - nadrabianie folderu
   i plik zadan to gwarantuja; technik wybiera tylko osobe);
4. proba wytrzymalosciowa na laptopie stanowiska przed wdrozeniem: 200 x start i zamkniecie programu z jednym skanem.

## 5. Odpowiedzi na pytania (A) w skrocie

1. **Wprowadzenie w blad.** Widok nieodswiezony po zmianie stanu: nie znalazlem - kazdy sygnal stanu i kazde polecenie konczy sie
   `_odswiez()`, czesci maja sygnatury z pelnych obiektow stanu, sygnal postepu podmienia sam pasek tylko wtedy, gdy krotka plytek
   jest TA SAMA. Widok pracy A z przyciskami dla pracy B: nie - polecenie bierze prace z biezacego stanu (`_wybor`), przyciski sa
   aktywne wg tej samej pracy. Decyzja dla nie tej pracy: tylko przez A-P2 (podmiana mapy pod kursorem). Podwojne klikniecie /
   klawisz: jedno polecenie (po pierwszym przycisk jest nieaktywny). Skroty przy otwartym pytaniu: dzialaja (A-D1). Pytanie
   potwierdzone Spacja / Enterem: niemozliwe (zaden przycisk nie ma fokusu ani roli domyslnej; uruchomione). Przesuniecie przyciskow
   pod kursorem: panele sa nad lewa i srodkowa kolumna - pojawienie sie panelu przesuwa mape i przyciski pytan w dol (prawa kolumna
   z decyzjami stoi w miejscu - dobrze); o 6 / 14 / 22 panel wyboru osoby wchodzi NAD panel pytania - klikniecie wycelowane w
   "Tak, to ponowny skan" moze trafic w przycisk osoby (raz na zmiane, sekundowe okno; do wiedzy).
2. **Kontrakt.** Spelniony: brak importow `session` / `baza` / `scanner` / `silnik` w `ui/`, `wykonaj` tylko w watku okna, brak
   `exec`, nieznany status / komunikat / stan puli rysowany ze stanu, kazda odmowa pokazana (komunikat stanu albo panel z tekstem
   odpowiedzi). Obejscia: A-D2 (ksztalt plytki), A-D3 (prog 0,08), wlasna mapa i wlasny obraz - uzasadnione (stara mapa bierze
   kolory z wyniku analizy, stary obraz liczy w watku okna); orientacja zgodna ze starymi.
3. **Odpornosc.** Pliki w watku okna: tylko pierwsze wczytanie ukladu (A-D2) i `szczegoly_pracy` (pamiec kontrolera + 1 zapytanie);
   obrazy w watku pomocniczym, pamiec 60 obrazow i 2 plikow - bez wycieku; zbiory `_znane`, `_nr_komunikatow`, `_bez_obrazu` rosna
   o liczby calkowite (pomijalne). 36 plytek: A-D4. 24-31 gniazd: A-D7. Dlugi tekst komunikatu (640 znakow): panel rosnie, mapa
   zostaje przy minimum 340-349 px - przy 1280 x 760 patrz A-P1. Wiele paneli: A-P3. 15-16 konfliktow: jeden panel "(16 razy)",
   "Zamknij" zamyka wszystkie (A-D4).
4. **Czytelnosc.** Pkt 3, A-P1, A-D7. Tabulacja: zaden element nie przyjmuje fokusu - klawisz Tab nic nie robi; z klawiatury
   dzialaja tylko Spacja, U, O, C, N, Esc; wybor osoby, odpowiedzi na pytania i numer plytki - tylko mysza (do wiedzy na G1).
5. **Dane osobowe.** W tekstach widzetow nie ma sciezek ani nazw plikow: folder puli i skanera nie sa pokazywane, tekst odpowiedzi
   `zapisz_liste` (z nazwa pliku listy `do_dofrezowania_biezaca.csv` - to nie dana osobowa) nie trafia na ekran, bo okno pokazuje
   tekst odpowiedzi tylko przy odmowie; teksty odmow `session` nie zawieraja nazw (A-D11). Plik podgladu sluzy tylko do wczytania.

## 6. Czego NIE sprawdzilem

- Pelnego pytest; okna na prawdziwym ekranie, z prawdziwa mysza i klawiatura; skalowania 125 / 150 % uruchomieniem (tylko rachunek
  z rozmiarow ukladu); laptopa stanowiska; zgodnosci mapy z fizyczna plytka (strona lewa / prawa).
- Prawdziwej analizy przez ekran (testy ekranu uzywaja funkcji sztucznej), wariantu na skanach odniesienia (`E3A3_DANE_REF`),
  prawdziwego skanera, prawdziwie pelnego dysku i prawdziwej blokady bazy przez inny program, bazy i puli na dysku sieciowym,
  dwoch kont Windows naraz (blokada - tylko czytaniem).
- Przyczyny bledu natywnego (pkt 4): nie odtworzony, kod systemu i bibliotek poza zasiegiem czytania.
- `kontroler_api.py` linie 1-545 i 1370-1640 (typy stanu, dane sztuczne, wieksza czesc atrapy) - tylko wyrywkowo; `session.py`,
  `baza.py`, `scanner.py`, `silnik.py` poza wskazanymi miejscami; pozostale 55 testow `test_ui_wieczor.py` - tylko nazwy i przebieg.
- Zawartosci `silnik.log` po prawdziwej analizie z projektem, ktorego nie da sie wczytac (R2-D4).
- Podwojnego klikniecia mysza uruchomieniem (`QTest.mouseDClick` w trybie offscreen nie dal zadnego klikniecia - wynik proby
  odrzucilem jako wade proby; ocena z czytania kodu i z proby "O dwa razy").
- Czy liczby z raportow wykonawcow (48 ms, 7 ms, 82 napisy) sa dokladne - nie powtarzalem ich pomiarow.
