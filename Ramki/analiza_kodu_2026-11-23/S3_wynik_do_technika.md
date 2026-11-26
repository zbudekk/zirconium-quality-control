# S3 - droga wyniku od silnika do technika (analiza kodu, 23.11.2026)

Podstawa: galaz `analiza/s3` od `origin/analiza/plan` 480359f (= `main` b856b9e + folder planu), program `Ramki/stanowisko`.
Kodu nie zmieniano. Sesja glowna: Fable 5.2; wyliczenia i testy: subagenci Opus 5.5 xhigh (lista na koncu).
Znaleziska: **B 1 / P 6 / D 13**. Czas PC: proba 1 s + testy dowodowe 323 s (limit 30 min).

Odpowiedz na pytanie rundy w jednym akapicie: w tabeli statusow i na drodze status -> kolor ekranu / dioda nie znalazlem
sciezki, ktora status nieznany, pusty albo bledny zamienia w zielone (proba P1: 90 720 kombinacji, 0 wyjatkow; zielone
tylko przy kolorze zielonym z sesji, inspekcji "ok" i znanym numerze plytki). Zielone po zlym wyniku moze powstac inaczej:
przez ponowny skan, ktory zakrywa czerwone bez decyzji (S3-1), i przez numer nadany nie tej plytce (S3-3). Okno moze stanac
na wywolaniach Excela (S3-2); ramki okna nie blokuja.

## 1. Najwazniejsze znaleziska

| id | waga | plik:linia | co jest zle | co zobaczy technik | plytka | dowod | koszt potwierdzenia | sprawdzenie 28-29.11 |
|---|---|---|---|---|---|---|---|---|
| S3-1 | B | `session.py:1206-1211`, `kontroler_api.py:3343-3346`, `statusy.py:550` | Pytanie "Ponowny skan tej samej plytki?" ostrzega tylko o utracie DECYZJI. Praca czerwona bez decyzji w poprzednim skanie, ktora w nowym skanie wyszla zielona, znika po "Tak" bez ostrzezenia i bez wpisu w dzienniku. | Tekst "Poprzedni skan nie ma jeszcze zadnych decyzji", po "Tak" mapa z zielonym gniazdem, licznik czerwonych mniejszy. | kazda | proba P2 (`S3/proba_s3_wynik.txt` wiersze 56-63) | T (zrobione) | TAK: prace z ubytkiem zeskanowac dwa razy, drugi raz ubytkiem w dol / w cien; zanotowac, czy drugi skan jest zielony i co mowi pytanie. |
| S3-2 | P | `excel_com.py:54-142`, `excel.py:650`, `879`, `905`, `896`; wywolujacy `kontroler_api.py:1184-1190`, `2837-2840`, `3022` | Kazde wywolanie COM Excela idzie w watku okna (zegar 30 ms albo klikniecie), bez limitu czasu i bez filtra wiadomosci; przy ponowieniu dochodzi `time.sleep(0,5 s)` do 2 razy i pelny odczyt arkusza do 3 razy. | Po "Zamknij piec" albo "Zatwierdz wiersz" okno nie reaguje tak dlugo, jak Excel nie odpowiada (zajety, zawieszony). [NIE SPRAWDZONE BEZ EXCELA]: zachowanie przy otwartym oknie dialogowym Excela. | kazda (rano) | czytanie + wyliczenie 3 | D (prawdziwy Excel: dialog, edycja komorki, zapis do SharePoint) | TAK, jesli na laptopie jest Excel: otworzyc w Excelu okno "Zapisz jako" i kliknac "Zamknij piec"; zmierzyc, czy okno programu stoi. |
| S3-3 | P | `ui/okno.py:365`, `380-386`, `818`, `840`, `851`, `875`; `ui/czesci.py:216-217`, `707-708` | Plytka bez numeru z samymi zielonymi pracami nie blokuje samoczynnego przelaczenia ekranu na nowy skan. Panel "Podaj numer plytki" zostaje w tym samym miejscu, ale jego przyciski naleza juz do NOWEJ plytki; tytul panelu nie ma nazwy plytki, a ochrona 800 ms nie obejmuje paneli. | Klikniecie cyfry w chwili przyjscia nowego wyniku nadaje numer nowemu skanowi; plytka A zostaje bez numeru, B ma numer A - ramka i lista pokazuja wynik pod zlym numerem. | kwadratowe (numer wpisywany recznie); okragle tylko przy nieczytelnych dolkach | czytanie + wyliczenie 5 (pkt C) | S (test okna bez ekranu: dwa skany bez numeru, klik w panel po drugim stanie) | TAK: dwie plytki kwadratowe skanowane jedna po drugiej bez podania numeru pierwszej; patrzec, czy panel numeru zmienia plytke bez sygnalu. |
| S3-4 | P | `ui/czesci.py:1242-1246`, `ui/napisy.py:119` | Widok pracy pisze "Program nie wskazal ubytku." takze wtedy, gdy liczba ubytkow jest nieznana (praca "nie sprawdzono", "blad kontroli", "bez projektu" - inspekcji nie bylo). | Przy zoltej pracy "nie sprawdzono" obok przyciskow "Ukruszona" / "OK" stoi zdanie, ze program nie wskazal ubytku - zacheta do "OK" na pracy, ktorej nikt nie sprawdzil; po "OK" ramka swieci zielono. | kazda | czytanie + wyliczenie 1 | T (test okna z praca `status_inspekcji = nie_sprawdzono`) | TAK: skan z praca przyslonieta (brak danych brzegu) - przeczytac widok pracy. |
| S3-5 | P | `statusy.py:128`, `177`; `porownaj.py:88-92` | Dopasowanie ZOLTE (program niepewny, ktory to projekt) + inspekcja "ok" daje zwykle zielone "OK": niepewnosc dopasowania nie zostawia sladu ani w kolorze, ani w napisie, ani na ramce. | Zielone gniazdo "OK - praca rozpoznana, program nie widzi ubytku" dla pracy sprawdzonej wzgledem projektu, ktorego program nie byl pewny. | kazda | proba P1 (status_match "zolty" w kombinacjach zielonych) | D po stronie S1: jak czesto match zolty konczy sie inspekcja "ok" przy ZLYM projekcie | NIE wprost (potrzebne dwie podobne korony); zanotowac `status_match` i kolor z pliku wyniku. |
| S3-6 | P | `session_rano.py:576-591`, `770-782`; opis `opisy_modulow/session.md:99` | Rano praca dostaje projekt automatycznie wylacznie po `status_match == "zielony"`; progi 0,85 i 0,1 z opisu klasy "pewna" nie sa w `session_rano` sprawdzane (rozjazd opis - kod). Galaz koncowa klasyfikacji daje zielone "rozpoznana". | Zly projekt z zielonym dopasowaniem = praca w zlej kuwecie, zlecenie "kompletne", propozycja odhaczenia w Excelu. Chroni tylko konflikt (ten sam projekt w dwoch gniazdach). | poranne | czytanie + wyliczenie 4 (pkt A, F7) | D po stronie S1 (czestosc zielonego dopasowania do zlego projektu) | NIE bez prawdziwych prac po piecu. |
| S3-7 | P | `ramka/obraz.py:38`, `ramka/logika.py:576`, `591`; `ramka_protokol.py:122`, `ramka/protokol.py:202` | W stanie "wynik" pierscien na brzegu matrycy jest zawsze zielony (0,255,0) - takze gdy wszystkie gniazda sa czerwone i gdy plan nie ma zadnego swiecacego gniazda. | Zielona obwodka wokol plytki z ubytkami; pusta plytka = zielona obwodka i nic wiecej. [NIE SPRAWDZONE BEZ SPRZETU]: czy pierscien widac spod wkladki. | kwadratowe i okragle ramkowe (R54 nr 8 na ramce nie swieci) | proba P4 (wiersze 85-94) | T (zrobione) | TAK: wynik z czerwonym gniazdem na ramce W - czy zielona obwodka jest widoczna i jak ja czyta technik. |

Uwaga do wagi S3-1: program nie liczy tu niczego zle - drugi skan jest prawdziwym pomiarem. Blokujace jest to, ze po
wykryciu ubytku w pierwszym skanie nic nie zatrzymuje jego znikniecia, a ponowny skan to zwykla czynnosc ("popraw
ulozenie", "skan poruszony"). Czy drugi skan tej samej pracy potrafi wyjsc zielony, rozstrzyga S1 / sprzet.

## 2. Pozostale znaleziska (D)

| id | plik:linia | co jest zle | skutek | plytka | dowod | koszt | 28-29.11 |
|---|---|---|---|---|---|---|---|
| S3-8 | `session.py:847-854`, `388-392`; `kontroler_api.py:131`, `ui/okno.py:848` | Numer plytki wpisany recznie wieczorem: kazde n >= 1 dla kazdego ukladu; numer odczytany z dolkow jest sprawdzany tylko dla okraglych ramkowych; lista zapasowa przyciskow to 1..9. Przyczyna w kodzie znanej sprawy "numer wpisany z bledem" (decyzja 1, wariant 4). | Wynik pod numerem innej plytki. | kazda | czytanie + wyliczenie 2 (niespojnosci 2, 3) | T | TAK: wpisac numer 5 dla plytki wieczornej. |
| S3-9 | `statusy.py:164-179` | `status_pracy` nie sprawdza statusu skanu dla koloru zielonego: 108 kombinacji daje "zielony" takze przy skanie `blad`, `zastapiony`, `do_powtorzenia`. Chroni wylacznie `session._kolor` (`session.py:1117-1124`). | Dzis nieosiagalne; druga linia obrony nie istnieje. | kazda | proba P1 (wiersze 34-41) | T (zrobione) | NIE |
| S3-10 | `ramka/protokol.py:25`, `ramka/logika.py:141-145` | Ramka poranna trzyma plan 600 s bez kontaktu z laptopem (wieczorna 30 s). Decyzja robocza z README ramki - tu tylko pomiar. | Po zamknieciu albo zawieszeniu programu gniazda swieca do 10 min wg ostatniego planu. | ramkowe poranne | proba P4 (wiersze 98-102) | T (zrobione) | TAK: zamknac program przy swiecacej ramce P, zmierzyc czas. |
| S3-11 | `indicate.py:620-657` (por. `923-942`), `1040-1046` | Watek odpytywania ramki nie ma ostatniej ochrony `except Exception` (watek polecen ma): nieprzewidziany wyjatek konczy watek, pasek dalej pokazuje "polaczona". Ramka W: planu, ktorego nie da sie zbudowac, nie gasi poprzedniej wersji (ramka P gasi). | Ramka ciemna albo ze stara wersja wyniku tego samego skanu; brak komunikatu. | ramkowe | czytanie | S (wstrzykniecie wyjatku w tescie) | NIE |
| S3-12 | `indicate.py:973-982`, `1094` | Blad sieci przy poleceniu gaszacym albo nowym planie: ponowienie bez wpisu w logu; do skutku ramka pokazuje poprzedni obraz (W najwyzej 30 s od ostatniego kontaktu). | Po "Ukruszona" na zielonej pracy dioda zostaje zielona do udanego ponowienia. | ramkowe | wyliczenie 3 (tabela B) | S | TAK: odlaczyc siec ramki na 10 s po decyzji. |
| S3-13 | `session.py:523-531`, `1269-1271`; `aplikacja.py:1418-1432` | Zapis `*_wynik.json` wewnatrz transakcji przyjecia skanu i zapis CSV listy - w watku okna, bez limitu; czekanie na baze do 5 s. Szczegoly naleza do S2. | Krotkie zatrzymanie okna przy wolnym dysku albo folderze sieciowym w `[sciezki] wyniki`. | kazda | wyliczenie 3 (tabela A) | S | NIE |
| S3-14 | `ui/okno.py:290-303`, `682-686`; `ui/czesci.py:579-583` | Dopisek do znanej E3-P14: w czasie analizy nowego skanu mapa poprzedniej plytki zostaje w pelnych kolorach i bez oznaczenia "poprzednia" - analize widac tylko na pasku. | Zielona mapa plytki A na ekranie, gdy w skanerze lezy juz plytka B. | kazda | czytanie + wyliczenie 5 (pkt A) | T | TAK: opisac, co widac na ekranie w czasie analizy drugiej plytki. |
| S3-15 | `ui/okno.py:322`, `712-715`, `444-446`, `606-607` | Po powrocie z trybu rano kursor gniazda nie jest zerowany i nie ma ochrony 800 ms; klikniecie pozycji listy "do dofrezowania" otwiera pierwsza prace gniazda z dwiema pracami; klawisz N nie ma ochrony. Decyzje U / O / C sa bezpieczne (`okno.py:546`). | Otwarta inna praca niz zamierzona; decyzja wymaga jeszcze swiadomego klawisza. | kazda | wyliczenie 5 (pkt B, C) | S | NIE |
| S3-16 | `ui/ekran_rano.py:199-272`, `243-244`; `ramka/logika.py:539-543`; `ui/kandydaci.py:219` | Rano: lista kuwet wybierana indeksem wiersza (po nowym stanie wiersz pod kursorem moze byc inna kuweta); napis "Wszystkie kuwety rozlozone - mozesz zamknac piec" bez sprawdzenia blokad; ramka P pisze "OK" takze przy swiecacych gniazdach "sprawdz"; "Przypisanie: program (dopasowanie pewne)" takze przy konflikcie. | Mylace napisy; wybor innej kuwety niz widziana. Zapis decyzji idzie po `praca_id` - bezpieczny. | poranne | wyliczenia 1 i 4 | S | NIE |
| S3-17 | `ramka/logika.py:554-557`, `ramka/sprzet_rpi.py:58-71`, `ramka/program.py:48-49` | Test diod z programu wypelnia cala matryce jednym kolorem - nie wykrywa obrotu ani odbicia panelu (`obrot` / `lustro` domyslnie 0 / nie; `sprzet_rpi` nie byl uruchamiany). Wiaze sie ze znana pozycja "kalibracja na sprzecie przed praca". | Dioda pod innym gniazdem przy zlej orientacji panelu; widac to dopiero po napisie na marginesie. [NIE SPRAWDZONE BEZ SPRZETU] | ramkowe | czytanie | - | TAK: jedna praca w gniezdzie niesymetrycznym (np. skrajne lewe) i wynik na ramce. |
| S3-18 | `kontroler_api.py:2689-2691` | Wynik skanu, ktorego nie ma w stanie doby (np. przyjety tuz przed 6:00, stan zbudowany po 6:00): ramka W zostaje w stanie "analiza" do nastepnego skanu. | Fioletowy pierscien bez wyniku. | ramkowe wieczorne | czytanie | S | NIE |
| S3-19 | `uklad.py:32-38` a `session.py:158-161`; `session_rano.py:470-471`, `842-845`, `869`, `905` | Dwie funkcje `typ_plytki` daja rozny wynik dla `okragla_poranna_r54`; rano "ta sama plytka" ma 5 roznych kluczy (sam numer / numer + rodzina). Przyklad z kodu: `poranna_r54` n4 i `poranna` n4 w jednym piecu sa zdublowane (blokada "Zamknij piec"), ale program nie zaproponuje ponownego skanu i odmowi zastapienia. | Piec z dwiema plytkami o tym samym numerze i roznych ukladach wymaga recznej zmiany numeru albo pominiecia skanu. | R54 / R59 razem | wyliczenie 2 (niespojnosci 1, 7) | S | NIE |
| S3-20 | opisy `session.md`, `ui_rano.md`, `ui_wieczor.md`, `ui.md`; `ramka_protokol.py:187-188`; `session_rano.py:23-24`; `excel.py:827`, `ui/okno_excela.py:67` | 49 rozjazdow opis - kod (18 + 7 + 20 + 4; pelna lista w `S3/wyliczenie_4_poranek.md` pkt F i `S3/wyliczenie_5_ekran_wieczor.md` pkt G) oraz 2 docstringi niezgodne z kodem. Klasa propozycji Excela spoza listy bylaby traktowana jak "jeden wiersz" (dzis nieosiagalne - klasy nadaje ten sam modul). | Opisy nie sa wiarygodnym zrodlem dla testow na sprzecie w tych punktach. | - | wyliczenia 1, 2, 4, 5 | - | NIE |

## 3. Sprawdzone, bez znaleziska

- **Status nieznany / pusty:** `statusy.status(None)`, `status("")`, klucz nieznany -> "nieznany" (zolty, ramka zolta); klasa
  poranna nieznana -> zolty; kolor spoza protokolu ramki -> czerwone "sprawdz" (`ramka_protokol.py:126-128`). Kolory ramki
  ze statusow spoza protokolu: 0 (proba P1).
- **"OK" na czerwonej pracy:** status `zatwierdzona_ok`, na ekranie inny kolor (#009688) i napis "OK - zatwierdzona", na
  ramce zielony jak zwykle "OK" (proba P2). To decyzja wlasciciela 3 - nie zglaszam.
- **Mapa okragla:** `ui/mapa.py:236-237` odwraca tylko os Y (przod plytki na dole), bez obrotu i bez odbicia; sciecie liczone
  z pola `flat` (-45 st., przod-prawo). Zaden `uklad.json` nie ma pola obrotu ani odbicia; uklad poranny nie jest odbiciem
  wieczornego.
- **Gniazda i diody okraglej ramkowej:** gniazda `okragla_ramkowa_*` = kwadrat R59 (0 roznic), bloki diod z geometrii rowne
  blokom kwadratu 19 z 19 i 24 z 24, zaden blok poza kolem plytki, zadne dwa bloki sie nie stykaja, srodek bloku do 1,60 mm
  od srodka gniazda (proba P3). Uklady bez kalibracji (ramka ciemna): 4 okragle testowe, w tym R54 nr 8.
- **Stary wynik na ramce W:** zdjecie plytki kasuje wynik na samej ramce (`ramka/logika.py:368-370`); szybka podmiana dwoch
  plytek o tym samym numerze daje najpierw 0, powrot do numeru najwczesniej po 3 s (`ramka/sprzet.py:101-111`).
- **Czekanie na ramke:** siec tylko w watkach `indicate`, I/O poza zamkiem; okno czeka najwyzej ok. 1 s przy zamykaniu.
- **Zapis do Excela:** jedna komorka, po swiezym odczycie, kontroli wiersza i sasiadow, ponownym policzeniu propozycji
  i kontroli po zapisie (`excel.py:847-914`); Excel nie przelicza gniazd ani plytek - wiersz dobiera po kuwecie i folderze.
- **Testy dowodowe:** 570 z 571 passed w 9 plikach (`S3/testy_dowod.md`); 1 niepowodzenie = brak `ustawienia.toml`
  w swiezym worktree (srodowisko).

## 4. Pytania do wlasciciela

1. **Push:** sesja dziala na koncie Windows `<uzytkownik>`, nie `<konto-PC>` (plan mowi o koncie `<konto-PC>`). `git fetch` konczy
   sie "could not read Username for https://github.com" - pracowalem na lokalnym `origin/analiza/plan` 480359f. `git push -u origin
   analiza/s3` konczy sie tak samo (23.11, kod 128): galaz `analiza/s3` NIE jest wypchnieta, commity sa tylko lokalnie
   w `<PC-katalog>\qc-wt\analiza-s3`. Ustawien nie zmienialem - push z konta z dostepem do GitHub nalezy do wlasciciela.
2. **S3-1:** czy pytanie o ponowny skan ma wymieniac prace czerwone / zolte bez decyzji, ktore w nowym skanie sa zielone?
3. **S3-7:** czy zielony pierscien w stanie "wynik" zostaje, gdy sa czerwone gniazda?
4. **Plytka okragla ramkowa a czujniki:** magnesy plytki okraglej leza na promieniu 45 mm (+-31,8 mm), kwadratowej w +-42 mm.
   Program ramki nie zna wkladki - odczyt numeru plytki okraglej zalezy tylko od polozenia czujnikow w nowej ramce.
   [NIE SPRAWDZONE BEZ SPRZETU]
5. **Zakres testow 28-29.11:** R54 nr 8 na ramce nie swieci (bez magnesow i bez kalibracji), wiec droge do diod da sie
   sprawdzic tylko na plytkach kwadratowych; okraglych ramkowych n1-n6 fizycznie nie ma.
6. **Odstepstwa tej sesji:** subagent testowy wyslal dwa ostatnie pliki testow naraz (ok. 4 s dwoch procesow python);
   `test_ramka.py` zostawil `Ramki/stanowisko/ramka/__pycache__/` (12 plikow, ignorowane przez git, nie usuwane).

## 5. Co przeczytano (liczba linii niepustych)

Sesja glowna, w calosci: `statusy.py` 608, `session.py` 1162, `ramka_protokol.py` 275, `excel_com.py` 113, `ui/mapa.py` 381,
`ramka/logika.py` 551, `ramka/protokol.py` 306, `ramka/kalibracja.py` 256, `ramka/obraz.py` 137, `ramka/program.py` 346,
`ramka/sprzet.py` 96, `ramka/sprzet_rpi.py` 203, `opisy_modulow/indicate.md` 234.
Sesja glowna, czesciowo: `indicate.py` ok. 700 z 1226, `excel.py` ok. 390 z 896, `ui/okno.py` ok. 430 z 860,
`session_rano.py` ok. 90 z 1240, `ui/czesci.py` ok. 80 z 1242, `ui/ekran_rano.py` 16 z 1000, `opisy_modulow/session.md`
92 z 149; poza zakresem dla ustalenia wywolujacych: `kontroler_api.py` ok. 620 z 4251, `aplikacja.py` 30, `porownaj.py` ok. 180.
Tylko przez subagentow (w calosci wg ich raportow): `ui/kandydaci.py` 299, `ui/mapa_rano.py` 174, `ui/napisy.py` 142,
`ui/napisy_rano.py` 195, `ui/obraz.py` 126, `ui/okno_excela.py` 267, `ui/styl.py` 168, `ramka/serwer.py` 279,
`ramka/sprzet_atrapa.py` 82, `ramka/test_led.py` 109, `ramka/czcionka.py` 48, `ramka/README.md` 415, opisy `excel.md`,
`ui_rano.md`, `ui_wieczor.md`, `ui.md`; reszta `session_rano.py`, `ui/czesci.py`, `ui/ekran_rano.py`, `excel.py`, `indicate.py`.
Subagent wyliczenia 3 zaznaczyl, ze `session.py`, `session_rano.py`, `statusy.py`, czesc `ui/*` i `ramka/*` czytal
fragmentami z pelnym przeszukaniem wzorcami.
Nieczytane: testy modulow (uruchamiane jako dowod), `ui/__init__.py`, `ramka/__init__.py`, `ramka/__main__.py`.

## 6. Zlecenia subagentow (Opus 5.5 xhigh)

| nr | zlecenie | wynik | sprawdzenie wyrywkowe sesji glownej |
|---|---|---|---|
| 1 | status -> kolor / tekst, wartosc domyslna | `S3/wyliczenie_1_status_kolor.md` (203 wiersze: TAK 12, NIEJASNE 59, NIE 132) | `czesci.py:225-246`, `1242-1246`, `ekran_rano.py:239-244` - zgodne |
| 2 | rozroznienia ksztaltu / ukladu / numeru | `S3/wyliczenie_2_ksztalt_uklad.md` (tabele A 95, B 36, C 21, D 26) | `session.py:388-392`, pola `uklad.json` 4 ukladow - zgodne |
| 3 | operacje mogace czekac, `except`, zamki, sygnaly | `S3/wyliczenie_3_blokady_except.md` (A 310, B 53, C 28, D 20) | `aplikacja.py:1418-1432`, `kontroler_api.py:1184-1190`, `2837-2840`, `indicate.py:973-982` - zgodne |
| 4 | poranek: opis kontra kod | `S3/wyliczenie_4_poranek.md` (25 rozjazdow) | `session_rano.py:576-591`, `742-782` - zgodne |
| 5 | ekran wieczorny: opis kontra kod | `S3/wyliczenie_5_ekran_wieczor.md` (24 rozjazdy) | `okno.py:354-386`, `541-548`, `805-860`, `875`, `czesci.py:209-217`, `707-708` - zgodne; punkt "komunikat bledu nowej plytki nie jest panelem" doprecyzowany: jest w panelu "nowy wynik" kolumny plytek (`okno.py:676-678`) |
| 6 | testy dowodowe 9 plikow | `S3/testy_dowod.md` (570 passed, 1 failed - srodowisko) | - |

Proby sesji glownej: `S3/proba_s3.py`, wynik `S3/proba_s3_wynik.txt` (P1 statusy, P2 ponowny skan, P3 kalibracja, P4 logika ramki).
