# S3 / wyliczenie 5 - ekran wieczorny: czy ekran moze pokazac stary albo cudzy wynik jako biezacy

Data: 2026-11-23. Worktree: <PC-katalog>\qc-wt\analiza-s3. Kod tylko czytany (bez uruchamiania, bez testow).
Sciezki kodu wzgledem `Ramki/stanowisko/stanowisko/` (np. `ui/okno.py:354`); opisy: `Ramki/stanowisko/opisy_modulow/`.
Pakiet ui lezy w `Ramki\stanowisko\stanowisko\ui\` (w zleceniu: `Ramki\stanowisko\ui\`). Numery linii sprawdzone Read-em.
Cytaty napisow z `ui/napisy.py` przepisane bez polskich znakow (w pliku sa z diakrytykami).
Poza zakresem (nie czytane): `ui/ekran_rano.py`, `ui/kandydaci.py`, `ui/mapa_rano.py`, `ui/napisy_rano.py` (ekran poranny w tym samym oknie).

---------------------------------------------------------------------------------------------------------------------
## A. Ktora plytka / ktory skan jest pokazywany jako "biezacy"

A1. Skad plytki. Plytka = jeden skan doby roboczej ze `stan.plytki`. Wiersz skanu powstaje w bazie dopiero z wynikiem albo
z bledem analizy: `session.py:399-404` (`skan_id = self.baza.wstaw("skany", ... status=status ...)`) i `session.py:450-452`
(`przyjmij_blad`, status `blad`). Kontroler bierze WSZYSTKIE skany wieczorne doby, w kolejnosci id (`session.py:1085-1092`
`ORDER BY id`; `kontroler_api.py:1508-1510`), dowolnego statusu. `biezaca_plytka` = ostatni skan doby dowolnego statusu:
`kontroler_api.py:1544` `aktywne = [p.skan_id for p in plytki]` (mimo nazwy - wszystkie plytki) i `kontroler_api.py:1553`
`biezaca_plytka=aktywne[-1] if aktywne else None`.

A2. Regula wyboru w oknie: `ui/okno.py:354-378` (`_wybierz_plytke`), wolana z `pokaz_stan` (`ui/okno.py:315`) przy kazdym
stanie - takze w trybie "rano" i w serii polecen z `_wstrzymaj`. Wybor = pole `self._plytka_id` (skan_id).
- pokazana plytka zniknela ze stanu (np. nowa doba): `:359-362`
  `self._plytka_id, self._gniazdo, self._poza, self._podaj_numer, self._praca_widoku = None, None, None, False, None`;
  gdy byla otwarta praca - informacja `N.PRACA_ZNIKNELA` (`:360-361`).
- nowe skany (skan_id nieznane oknu - `_znane`, `:356-357`), nie pierwszy stan - `:363-369`:
  `if self._mozna_przelaczyc(stan): self._plytka_id, self._podaj_numer = nowe[-1], False` (reszta nowych do `_nieobejrzane`,
  `:366`); inaczej `self._nieobejrzane.update(nowe)` i `self._blysk_nowej = True` (`:368-369`).
- brak pokazanej plytki: `:371-372` `self._plytka_id = stan.biezaca_plytka if stan.biezaca_plytka in numery else numery[-1]`.
  Przy starcie programu (`_pierwszy_stan`, `:110`, `:363`, `:370`) ekran pokazuje wiec ostatni skan doby - takze skan `blad`,
  `niezgodny_uklad` albo skan z wczesniejszej zmiany.
- warunek samoczynnego przelaczenia `:380-386` (`_mozna_przelaczyc`):
  `if self._gniazdo is not None or self._poza is not None or self._podaj_numer: return False` /
  `return plytka is None or not do_obejrzenia(plytka)`.
  `do_obejrzenia` (`ui/czesci.py:209-217`): prace z `p.decyzja is None and "ukruszona" in p.dozwolone and p.kolor is not None
  and p.kolor not in (ST.KOLOR_ZIELONY, ST.KOLOR_ZATWIERDZONA_OK)`. "ukruszona" jest w `dozwolone` tylko dla skanu `przyjety`
  w trybie wieczor (`kontroler_api.py:3159-3165`).
- Fakty wynikajace z reguly:
  (a) plytka `do_powtorzenia`, `zastapiony`, `plytka_nie_z_trybu`, `blad`, `niezgodny_uklad` nie ma prac "do obejrzenia"
      (puste `dozwolone`) - ekran przechodzi z niej sam na nowa plytke, takze gdy ma zolte prace bez decyzji;
  (b) regula nie patrzy na: kursor klawiatury (`_kursor`), otwarte pytanie / komunikat pokazanej plytki (np. pytanie
      "Podaj numer plytki" - to nie jest panel `_podaj_numer`), otwarty panel zmiany osoby, panel informacji / odmowy,
      ani na to, ze technik sam wybral pokazana plytke kliknieciem kafelka (`_pokaz_plytke` nie ustawia zadnej blokady);
  (c) kilka nowych naraz - pokazana zostaje ostatnia (`nowe[-1]`);
  (d) status nowego skanu nie ma znaczenia - wynik z bledem, niezgodny uklad i plytka nie z trybu ida ta sama regula.

A3. Po przelaczeniu albo po wyborze innej plytki: ochrona 800 ms (`OCHRONA_MS`, `ui/okno.py:52`), tylko gdy poprzednia mapa
miala gniazda albo prace poza gniazdem (`ui/okno.py:716-718`); mapa przygaszona i nie przyjmuje klikniec (`ui/mapa.py:421`);
kursor zerowany przy zmianie skan_id mapy (`ui/okno.py:714-715`).

A4. Gdy ekran sie NIE przelacza: mapa poprzedniej plytki zostaje w pelnych kolorach, na samej mapie bez zadnego oznaczenia.
Sygnaly nowego wyniku sa obok mapy: "NOWA" na kafelku (`ui/czesci.py:855-856`), przycisk "Pokaz nowy wynik:\n<Plytka n>"
w kolumnie plytek (`ui/okno.py:672-673`, `ui/czesci.py:980-988`), trwaly panel "Nowy wynik czeka: ..." w kolumnie plytek
(`ui/okno.py:676-678`, `ui/czesci.py:782-796`), blysk paska 1500 ms (`ui/okno.py:679-681`, `ui/czesci.py:45`, `:523-526`).
Naglowek mapy dalej "Plytka n - <stan>" i "skan z GG:MM" pokazanej plytki (`ui/okno.py:742-748`). Przelacza technik:
kafelek (`ui/okno.py:181`), "Pokaz nowy wynik" (`:416-422`, najnowsza nieobejrzana), wiersz listy (`:434-446`).

A5. W czasie analizy nowego skanu: skanu nie ma w `stan.plytki` (A1), `_wybierz_plytke` nic nie zmienia; mapa pokazanej
plytki zostaje bez zmian, bez przygaszenia i bez oznaczenia "poprzednia". Analiza widoczna tylko na pasku stanu:
"Analiza: trwa: n %" + pasek postepu (`ui/czesci.py:579-583`) i kolejka (`ui/czesci.py:586-594`). Sygnal `postep` odswieza
sam pasek, chyba ze zmienil sie obiekt `stan.plytki` (`ui/okno.py:298-303`). Skan policzony, a niezapisany
(`stan.niezapisane`) jest kafelkiem "nie zapisano", ktorego nie da sie otworzyc (`ui/czesci.py:902-920`, `:1000-1003`), nie
plytka; po udanym zapisie staje sie plytka i podlega A2 - takze gdy zapis nastapi w trakcie polecenia `ponow_zapis`
(`aplikacja.py:1453-1459`).

A6. Skan zakonczony bledem / niezgodnym ukladem / plytka nie z trybu:
- ekran sie przelaczyl (A2): `ui/mapa.py:119`
  `gniazda = tuple(plytka.gniazda) if plytka is not None and (plytka.aktywna or plytka.prace) else ()` - skan nieaktywny bez
  prac (blad; niezgodny uklad, gdy wynik nie ma gniazd) = napis `N.MAPA_BEZ_GNIAZD` "Plytka {napis}." zamiast gniazd
  (`ui/mapa.py:124-125`), np. "Plytka analiza nie powiodla sie."; plytka nie z trybu z pracami - gniazda rysowane, prace
  w kolorze statusu `plytka_nie_z_trybu` (120,120,140) "zablokowana" (`statusy.py:89`, `statusy.py:164-165`). Komunikat
  plytki (`blad_analizy:<skan_id>` / `niezgodny_uklad:<skan_id>`, trwaly - `kontroler_api.py:3245-3256`) i pytanie
  `plytka_nie_z_trybu` - w panelach nad mapa (`ui/okno.py:818-819`).
- ekran sie nie przelaczyl: mapa poprzedniej plytki z kolorami zostaje (A4). Komunikat bledu nowego skanu NIE jest panelem
  (panele tylko dla pokazanej plytki albo komunikaty bez plytki / plytki spoza stanu: `ui/okno.py:818-823`) i nie trafia na
  pasek bledow (ten bierze tylko `ogolne`, `ui/okno.py:825`). Widac go jako znacznik "ma komunikat" na kafelku
  (`ui/okno.py:667`, `ui/czesci.py:861-862`), "NOWA" i tytul w panelu "Nowy wynik czeka" (`ui/czesci.py:776-777`, `:792`).

---------------------------------------------------------------------------------------------------------------------
## B. Stan trzymany w oknie miedzy odswiezeniami

Format: pole - plik:linia - klucz - kiedy czyszczone / uzgadniane - czy po nowym stanie moze wskazac inna prace / skan.

OknoWieczor (`ui/okno.py`):
B1. `_stan` :94 - ostatni pokazany StanAplikacji; podmieniany :312 i :302; starsza `wersja` odrzucana :310. Nie.
B2. `_plytka_id` :95 - skan_id. Czyszczony :362; zmieniany :365 (sam, nowa plytka), :372 (domyslna), :409 (technik). Klucz
    unikalny - nie wskaze innego skanu; moze zostac zmieniony samoczynnie na nowa plytke (A2), takze po recznym wyborze.
B3. `_gniazdo` :96 - NUMER gniazda w obrebie `_plytka_id`. Czyszczony :362, :409, :451, :662-663 (wybor zniknal ze stanu);
    ustawiany :425. Samoczynna zmiana plytki zablokowana, gdy ustawiony (:383), kazda inna zmiana plytki go zeruje - numer
    nie przechodzi na inny skan. W tym samym skanie numer -> praca sprawdzany przez `_praca_widoku` (:658-661).
B4. `_poza` :97 - praca_id pracy poza gniazdem; jak B3; wybor `next(... p.praca_id == self._poza ...)` :403. Nie.
B5. `_nr_pracy` :98 - INDEKS w `g.prace` (dwie prace w gniezdzie). Zerowany :409, :425, :431, :451; przycinany :400;
    zmieniany :457. Przy zmianie listy prac gniazda moze wskazac inna prace - wtedy `_odswiez` porownuje z `_praca_widoku`
    i zamyka widok z `N.PRACA_ZMIENIONA` (:658-661).
B6. `_praca_widoku` :99 - praca_id pokazana w widoku (cel decyzji). Ustawiany przy kazdym `_odswiez` z biezacego wyboru
    :664; zerowany :362, :409, :425, :431, :451, :458. Gdy biezacy wybor wskazuje inna prace -> widok zamkniety :658-663.
    Nie przenosi decyzji na inna prace.
B7. `_kursor` :100 - NUMER gniazda (kursor klawiatury). Zerowany: zmiana skan_id mapy :714-715, numer spoza gniazd plytki
    :684-685, klik gniazda :425, Esc :613-615. Po powrocie z trybu "rano" `_mapa_podpis = None` (:322), wiec
    `_sprawdz_zmiane_mapy` konczy w :712-713 bez zerowania kursora; jesli w trybie rano zmienila sie `_plytka_id` (A2 dziala
    tez w trybie rano, :315), kursor o tym samym numerze zostaje na innej plytce (plytki jednego ukladu maja te same numery,
    zostaje o ile numer jest na nowej plytce :684-685); Enter (`_wybierz_kursor` :493-496) otwiera to gniazdo nowej plytki,
    bez ochrony 800 ms (G16).
B8. `_lista_wszystkie` :101 - filtr listy (bool); tylko klik :498-500. Nie.
B9. `_zmiana_osoby` :102 - panel zmiany osoby (bool); czyszczony :377-378, :565, :569; toggle :507. Nie dotyczy prac.
B10. `_pokaz_wczesniejsze` :103 - bool; toggle :503. Nie.
B11. `_podaj_numer` :104 - panel recznego numeru, bool BEZ skan_id. Czyszczony :362, :365, :409, :527; toggle :576. Panel
    budowany dla biezacej plytki (:820-821, :850; przyciski `(skan_id, n)` - `ui/czesci.py:752`). Blokuje samoczynna zmiane
    plytki (:383), kazda inna zmiana plytki go zeruje - nie.
B12. `_odmowa` :105 - tekst odmowy spoza stanu; czyszczony przy kazdym poleceniu :524 i "Zamknij" :882. Nie kluczowany
    plytka - po zmianie plytki zostaje do nastepnego polecenia.
B13. `_informacja` :106 - tekst informacji ekranu (PRACA_ZNIKNELA / PRACA_ZMIENIONA / POZYCJA_Z_INNEJ_DOBY); czyszczony przy
    kazdym poleceniu :525 (takze Spacja) i "Zamknij" :885. Zmiana plytki (`_pokaz_plytke` :406-414) go nie czysci -
    informacja o pracy z poprzedniej plytki moze stac nad mapa innej plytki.
B14. `_znane` :107 - zbior skan_id kiedykolwiek widzianych; nigdy nie czyszczony.
B15. `_nieobejrzane` :108 - zbior skan_id ze znaczkiem "NOWA"; uzgadniany :358 (`&= set(numery)`); zdejmowany :373, :376,
    :411, :413. Nie.
B16. `_blysk_nowej` :109 (zerowany :681), `_pierwszy_stan` :110 - flagi.
B17. `_nr_komunikatow` :111 - slownik komunikat.id -> numer kolejnosci (`setdefault` :313-314), nigdy nie czyszczony.
    Komunikat o stalym id (np. `odmowa:<kod>`, `pula`, `lista_nie_zapisana`, `blad_zapisu`), ktory zniknal i wrocil, ma
    stary numer - sortowanie "od najnowszego" (:824) stawia go jak stary.
B18. `_obraz_dla` :112 - praca_id obrazu zleconego / pokazanego; zerowany :693, :910; odpowiedz watku z innym kluczem
    pomijana :929. Nie.
B19. `_sygnatury` :113 - slownik czesc -> sygnatura (akcje :757, poza :770, uwagi :827-830, bledy :866, nowy_wynik :677);
    czyszczony :266 (zwykly / zwarty), :321 (zmiana trybu). Sygnatury zawieraja skan_id / obiekty stanu. Nie.
B20. `_mapa_podpis` :114 - (skan_id, krotka (nr, status, rgb, podpis) gniazd, praca_id poza gniazdem) :705-707; zerowany :322.
B21. `_tab_podpis` :115 - krotka id() widzetow (kolejnosc Tab).
B22. `_w_poleceniu` :116, `_wstrzymaj` :117, `_zamkniete` :118 - flagi; `_ochrona` :119-122 - QTimer 800 ms.

Widzety i moduly:
B23. `MapaPlytki._plytka/_gniazda/_geometria` `ui/mapa.py:101-103`; porownanie
    `plytka == self._plytka and geometria is self._geometria and wybrane == self._wybrane` (:116); ustawiane w kazdym
    `_odswiez` (`ui/okno.py:686`). Nie.
B24. `MapaPlytki._wybrane` `ui/mapa.py:104` - numer gniazda (= B3); `_kursor` :105 - numer (= B7, `ui/okno.py:687`);
    `_przygaszona` :106 (wlaczane `ui/okno.py:339`, `:718`; wylaczane `:721`).
B25. `MapaPlytki._ksztalty` `ui/mapa.py:107` - slownik numer gniazda -> (sciezka, srodek, promien, szerokosc) w pikselach;
    liczone od nowa po zmianie rozmiaru, obiektu geometrii albo listy numerow (:120, :128-129, :215-217, :291-293). Inna
    plytka z ta sama geometria i numerami - te same ksztalty (ten sam uklad). Klik zamieniany na numer wg ksztaltow plytki
    pokazanej w chwili klikniecia (:405-415). `_rozmiar_ksztaltow, _obrys, _sciezka_plytki, _sciecie, _napis` :108-112 -
    pochodne.
B26. modul `ui/mapa.py:39-40` `_GEOMETRIE`, `_BLEDY_UKLADU` - klucz `(nazwa ukladu, id(kontroler.ust))` (:50); uklad trzymany do
    konca programu, nieudany - ponawiany po 60 s (:38, :51-53). Nie dotyczy prac.
B27. `PasekStanu` `ui/czesci.py`: `_sygnatura` :492, `_liczenie_od` :493, `_blysk` :494-496, `_do_przejecia` :456 / :619 -
    rola ramki z ostatniego `ustaw`, czytana w chwili klikniecia "Przejmij ramke" (:454).
B28. `KafelekPlytki._skan_id` :839, `_liczniki` :840 - kafelek budowany od nowa przy zmianie sygnatury listy (:993-999). Nie.
B29. `ListaPlytek._nowe` :945 (nazwa, ile), `_sygnatura` :963, `_r` :964.
B30. `ObrazPracy._oryginal` :1030 - QPixmap BEZ klucza; podmieniany przy kazdej nowej pracy (`ui/okno.py:912-926`: obraz
    z pamieci albo napis "Wczytuje obraz pracy..." / "Brak obrazu tej pracy."), przy pustym gniezdzie schowany
    (`ui/czesci.py:1277`); spozniony obraz innej pracy pomijany (`ui/okno.py:929`). Nie pokaze obrazu innej pracy.
B31. `WidokPracy.praca_id` `ui/czesci.py:1068` - ustawiany :1225, zerowany :1218; porownywany przy decyzji (`ui/okno.py:546`).
    `_sygnatura` :1157 (praca w sygnaturze :1223), `_wpisy_przyciski` :1115 (frezowanie_id w lambdzie :1203-1204).
B32. `ListaDofrezowania._pozycje` `ui/czesci.py:1332` - krotka PozycjaListy; klik = INDEKS wiersza -> `self._pozycje[wiersz]`
    (:1368-1370); tabela i `_pozycje` wypelniane razem (:1348-1362) - zgodne. Pozycja niesie praca_id, ale okno otwiera ja po
    numerze gniazda z `_nr_pracy = 0` (`ui/okno.py:444-446`, `:409`): przy dwoch pracach w gniezdzie widok pokazuje pierwsza
    prace gniazda, niekoniecznie te z listy.
B33. `Legenda._sygnatura` `ui/czesci.py:1384`.
B34. `WczytywaczObrazow` `ui/obraz.py:110-112`: `_pliki` (klucz str(plik podgladu), najwyzej 2 - :23), `_obrazy` (klucz
    praca_id, najwyzej 60 - :24), `_zlecone` (zbior praca_id); bez czyszczenia wg skanu; klucz praca_id unikalny. Nie.
B35. `PanelExcela` (`ui/okno_excela.py`, ekran poranny): `_zalogowane` :76, `_klucz` :80 (sesja_pieca_id, zlecenie_id),
    `_wybrana` :81, `_wiersz` :82 (numer wiersza kandydata, uzgadniany z nowymi kandydatami :264-265), `_kandydaci` :83,
    `_sygnatura` :84, `_stan` :85. Polecenia po tozsamosci pozycji; `_rozbroj` po zapisie (:184-188). Nie.
B36. Panele `PanelUwagi` (`ui/czesci.py:707-708`) i przyciski akcji plytki (`ui/okno.py:766`) trzymaja argumenty polecenia
    w lambdzie z chwili budowy - patrz C8, C16.

---------------------------------------------------------------------------------------------------------------------
## C. Polecenia z okna (klik -> kontroler)

Wszystkie przez `OknoWieczor._polecenie` `ui/okno.py:511-536` -> `self.k.wykonaj(nazwa, *argumenty)` (:519). `_polecenie` NIE
sprawdza ochrony 800 ms. Ochrone sprawdzaja tylko: mapa (`ui/mapa.py:421`), `_klik_poza` (`ui/okno.py:429`), `_wybierz_kursor`
(:495), klawisze U / O / C (:604).

Pasek stanu:
C1. "Czekam na plik skanu [Spacja]..." (`ui/czesci.py:483`, `ui/okno.py:146`) i Spacja (`ui/okno.py:601-602`; rano :585-588)
    -> `start_skanu()` (:538-539). Nie dotyczy prac.
C2. "Odswiez pule" (:147) -> `odswiez_pule()`.
C3. przycisk trybu (`ui/czesci.py:446`, `ui/okno.py:149`) -> `przelacz_tryb(tryb)`, tryb liczony w chwili klikniecia
    z `self._stan.tryb` (`ui/okno.py:284-287`).
C4. "Test LED" (:150) -> `test_led()`.
C5. "Przejmij ramke" (:151) -> `przejmij_ramke(rola)`, rola z `PasekStanu._do_przejecia` (`ui/czesci.py:454`).
C6. "Zmien" osoba (:148) - lokalne. Panel osoby: przycisk osoby -> `wybierz_operatora(osoba)` (`ui/czesci.py:664`,
    `ui/okno.py:564-566`); "Odchodze od stanowiska" -> `wybierz_operatora(None)` (:568-570); "Bez zmian" - lokalne.

Panele uwag nad mapa i pasek bledow (`PanelUwagi`; lambda `self.polecenie.emit(p, a)` z argumentami z chwili budowy -
`ui/czesci.py:707-708`; `_polecenie_panelu` `ui/okno.py:875-905`):
C7. Panel recznego numeru: cyfry -> `podaj_numer_plytki(skan_id, n)` (`ui/czesci.py:752`); "Bez zmian" lokalne. Otwarty panel
    blokuje samoczynna zmiane plytki (`ui/okno.py:383`). Nie.
C8. Pytanie (przyciski z `Pytanie.odpowiedzi`, argumenty z kontrolera): `potwierdz_ponowny_skan(skan_id)`,
    `odrzuc_ponowny_skan(skan_id)` (`kontroler_api.py:3355-3356`), `zamknij_pytanie(pytanie_id)` / `dopusc_plytke(skan_id)`
    (`kontroler_api.py:3364`), cyfry `podaj_numer_plytki(skan_id, n)` + `zamknij_pytanie(id)` (`kontroler_api.py:3370-3371`).
    Panele pytan sa tylko dla pokazanej plytki (`ui/okno.py:818`) i sa budowane od nowa w tym samym odswiezeniu, w ktorym
    zmienia sie plytka (`ui/okno.py:827-831`). Samoczynna zmiana plytki jest dozwolona przy otwartym pytaniu pokazanej
    plytki (A2 b) - np. "Podaj numer plytki" na plytce bez numeru z samymi zielonymi pracami (te maja `kolor` None,
    `statusy.py:196-197`, i nie wchodza do `do_obejrzenia`). Wtedy w miejscu paneli starej plytki staja panele NOWEJ plytki
    z jej skan_id, bez ochrony 800 ms. Panel "Podaj numer plytki" plytki bez numeru nie ma w tytule nazwy plytki
    (`ui/okno.py:840` `nazwa_pytan = ... else ""`, `:851`) - dwie plytki bez numeru maja identyczny panel. Polecenie trafia
    w plytke, ktorej panel jest na ekranie w chwili klikniecia.
C9. Komunikat: "Odswiez pule" `odswiez_pule()`, "Ponow zapis" `ponow_zapis()`, "Zapisz liste do pliku" `zapisz_liste()`,
    "Ponow teraz" `ponow_polecenie(komunikat.id)`, "Zamknij" / "Rezygnuje - nie zapisuj" `zamknij_komunikat(id)` - jedno
    polecenie na kazde id grupy (`ui/czesci.py:804-814`, `ui/okno.py:889-903`). "Ponow teraz": kontroler wykonuje ponownie
    zapamietane polecenie z argumentami z chwili PIERWSZEGO klikniecia (np. `ukruszona(praca_id)`), niezaleznie od ekranu
    (`kontroler_api.py:3578-3582`); miejsce pracy jest w tekscie komunikatu (`kontroler_api.py:3535-3545`).
C10. Panel odmowy / informacji: "Zamknij" - lokalne (`ui/okno.py:881-886`).

Lista plytek:
C11. Kafelek (klik i Enter, `ui/czesci.py:886-899`) -> lokalne `_pokaz_plytke(skan_id)` przez `QTimer.singleShot(0, ...)`
    (`ui/okno.py:181`). skan_id kafelka. Nie.
C12. "Pokaz nowy wynik" (:184) -> lokalne `_pokaz_nowa` (:416-422): najnowsza nieobejrzana liczona w chwili klikniecia.
C13. "Ponow zapis" w liscie (:183) -> `ponow_zapis()`. C14. "Pokaz / Ukryj wczesniejsze zmiany" (:182) - lokalne.

Naglowek mapy:
C15. "Podaj numer plytki" / "Zmien numer" -> lokalne `_przelacz_numer` (`ui/okno.py:760-764`).
C16. "Dopusc te plytke", "Cofnij zastapienie", "Cofnij dopuszczenie" -> `_polecenie(a, s)`, `s = plytka.skan_id` w lambdzie
    z chwili budowy (`ui/okno.py:766`); przyciski budowane od nowa przy zmianie skan_id / numeru / akcji / osoby (:757-758).
    Bez ochrony 800 ms: po samoczynnej zmianie plytki w tym miejscu moze stac przycisk nowej plytki z jej skan_id.

Mapa i prace poza gniazdem:
C18. Klik w gniazdo -> lokalne `_klik_gniazdo(nr)` (`ui/okno.py:212`, `:424-426`); numer z ksztaltow plytki pokazanej w chwili
    klikniecia; pomijany przy przygaszonej mapie (`ui/mapa.py:421`).
C19. Przycisk pracy poza gniazdem -> lokalne `_klik_poza(praca_id)` (praca_id w lambdzie `ui/okno.py:775`), ochrona :429.

Widok pracy:
C20. "Ukruszona" / "OK" / "Cofnij decyzje" (`ui/czesci.py:1137-1149`) i klawisze U / O / C (`ui/okno.py:603-605`) -> `_decyzja`
    (:541-548) -> `ukruszona|ok|cofnij(self._praca_widoku)`. W chwili klikniecia: `widok.aktywny(nazwa)` (widok otwarty
    i przycisk aktywny, `ui/czesci.py:1186-1187`) oraz praca z BIEZACEGO wyboru == `_praca_widoku` == `widok.praca_id`
    (`ui/okno.py:546`). Klawisze pomijane w czasie ochrony (:604), przyciski mysza - nie. Decyzja nie trafi w prace inna niz
    pokazana w widoku.
C21. Krazek do wyboru -> `wybierz_wpis(praca_id, frezowanie_id)` (:550-555): praca_id = `_praca_widoku` z kontrola jak C20;
    frezowanie_id z lambdy przycisku (`ui/czesci.py:1203-1204`), w oknie nie sprawdzane z biezacym stanem.
C22. "Cofnij wybor krazka" -> `cofnij_wpis(praca_id, praca.wybor_wpisu_id)` (:557-562); decyzja_id z biezacego stanu.
C23. "Nastepna" i klawisz N -> lokalne `_idz_do_nastepnej` (:472-475) - gniazdo z praca do obejrzenia na pokazanej plytce.
    Bez ochrony. Po samoczynnej zmianie plytki N otwiera prace NOWEJ plytki; nastepne U / O (po 800 ms) decyduje o tej pracy
    (widok pokazuje wtedy naglowek nowej plytki).
C24. "praca 1 z 2" -> lokalne `_inna_praca` (:454-459). C25. "Zamknij [Esc]" - lokalne (:448-452).

Lista "do dofrezowania":
C26. "Ta doba" / "Wszystkie otwarte" - lokalne (:498-500).
C27. Wiersz -> lokalne `_klik_pozycja` (:434-446): skan_id, gniazdo, praca_id z pozycji; otwarcie po numerze gniazda z
    `_nr_pracy = 0` (B32).
C28. "Zapisz liste do pliku" -> `zapisz_liste()` (:572-573).

Ekran poranny (Excel, `ui/okno_excela.py`): "Zatwierdz" `excel_zatwierdz(sesja_pieca_id, zlecenie_id[, wiersz])`, "Pomin"
`excel_pomin(sesja_pieca_id, zlecenie_id)` - pozycja z `_pozycja()` po tozsamosci, tylko po wyborze kliknieciem (:190-207);
"Odswiez z Excela" `excel_odswiez()`, "Pozniej" `excel_zamknij()` (:128-129), zalegly piec `excel_pokaz(sid)` (:246).

Skroty klawiszowe (tryb wieczor, `ui/okno.py:580-621`):
- strzalki (takze z autopowtarzaniem) - kursor na mapie `_ruch_kursora` (:592-597, :477-491);
- autopowtarzanie pozostalych klawiszy pomijane (:598-600);
- Spacja - `start_skanu` (:601-602);
- U / O / C - `ukruszona` / `ok` / `cofnij` dla `_praca_widoku`, pomijane w czasie ochrony (:603-605);
- N - nastepna praca do obejrzenia, lokalne, bez ochrony (:606-607);
- Enter / Return - `_wybierz_kursor`: otwiera gniazdo pod kursorem, pomijane w czasie ochrony (:608-609, :493-496);
- Esc - zamyka panel zmiany osoby, albo kursor, albo widok pracy (:610-617);
- Enter na przycisku z fokusem (Tab) - `click()` bez ochrony (`ui/czesci.py:94-98`); Enter na kafelku z fokusem - pokaz plytke
  (`ui/czesci.py:894-897`);
- Spacja, U, O, C, N, Esc, strzalki z przyciskow i kafelkow przekazywane do okna (`ui/czesci.py:64-78`);
- Tab - kolejnosc: pasek, bledy, panele, plytki, kolumna mapy, widok, lista (`ui/okno.py:723-734`);
- tryb rano: najpierw `ekran_rano.klawisz` (poza zakresem), Spacja = `start_skanu` (`ui/okno.py:582-591`).
- Fokus: `wyczysc` oddaje fokus oknu, gdy usuwa widzet z fokusem (`ui/czesci.py:145-149`); przyciski krazkow usuwane bez tego
  (`ui/czesci.py:1196-1198`), zamkniecie widoku pracy chowa przyciski decyzji bez oddania fokusu oknu (`ui/czesci.py:1213-1216`)
  - dokad przechodzi fokus, decyduje Qt (nie sprawdzano).

---------------------------------------------------------------------------------------------------------------------
## D. Mapa (`ui/mapa.py`, `ui/obraz.py`)

D1. Geometria: `geometria_ukladu(kontroler, plytka.uklad)` (`ui/mapa.py:43-70`) -> `U.wczytaj(nazwa, katalog)` (:65), katalog
z `kontroler.ust["plytki"]` (:59-62) albo domyslny `modele_plytek/<nazwa>/uklad.json` (`uklad.py:1`, `:22`). Wolana tylko dla
plytki z gniazdami i (aktywnej albo z pracami) (`ui/okno.py:682`). Gniazda: `uk.sockets` - obrys `g.obrys(64)` (kolo albo
stadion obrocony o `g.angle`, `uklad.py:104-117`), srodek `g.x, g.y`, promien `g.promien_gorny`, szerokosc `g.d_top` / `g.l`
(`ui/mapa.py:241-248`). Obrys plytki: `uk.shape`, `uk.size` / `uk.d`, `uk.notch`, `uk.flat` (`ui/mapa.py:231`, `:251-277`).
Pozycji gniazd w kodzie nie ma. Ktore gniazda i jakie kolory - ze stanu (`Plytka.gniazda`: wszystkie gniazda ukladu + gniazda
z pracami, `kontroler_api.py:3193-3205`). Kratka (`ui/mapa.py:279-289`): gdy ukladu nie da sie wczytac albo gdy ktorykolwiek
numer gniazda ze stanu nie istnieje w ukladzie (`ui/mapa.py:227-230`) - 5 kolumn w kolejnosci numerow, bez obrysu plytki
i bez napisu "PRZOD PLYTKI".

D2. Przeksztalcenie wspolrzednych (`ui/mapa.py:231-237`):
  `pol = (uk.d if uk.shape == "round" else uk.size) / 2`
  `w, h = self.width() - 2 * MARGINES_PX, self.height() - 2 * MARGINES_PX - MIEJSCE_NA_PODPIS_PX`
  `s = max(1.0, min(w, h) / (2 * pol))`
  `cx, cy = self.width() / 2, MARGINES_PX + h / 2`
  `return QPointF(cx + x * s, cy - y * s)  # y plytki "do tylu" = w gore ekranu; przod plytki na dole`
Uklad pliku: "poczatek w srodku GORNEJ powierzchni plytki, x w prawo, y do tylu (od uzytkownika)" (`uklad.py:4-5`). Mapa = jedna
skala + przesuniecie + odwrocenie samej osi Y (os Y ekranu w dol): widok z gory, przod plytki na dole ekranu; bez obrotu, bez
odbicia lewo-prawo. Zalozenie: srodek plytki w (0, 0) ukladu (prostokat plytki `QRectF(px(-pol, pol), px(pol, -pol))`, :239).
"PRZOD PLYTKI" pod dolna krawedzia prostokata plytki (:359-360). Obraz odchylek (`ui/obraz.py:45-46`):
`ix = (ox + (P[:, 0] - lo[0]) * skala)`, `iy = (oy + (hi[1] - P[:, 1]) * skala)` - ta sama orientacja; kolka ubytkow tak samo
(`ui/obraz.py:67`). Strzalki: sasiad liczony ze srodkow gniazd na ekranie (`ui/mapa.py:150-171`).

D3. Obrys (`ui/mapa.py:251-277`):
- kwadrat: prostokat z rogami 6 px (:256) minus prostokat `notch`, poszerzony o 2 mm w strone +x i -y:
  `naroznik.addRect(QRectF(px(wyciecie["x_min"], wyciecie["y_max"]), px(wyciecie["x_max"] + 2, wyciecie["y_min"] - 2)))` (:260);
  poszerzenie wychodzi poza plytke tylko dla naroznika przod-prawo; `modele_plytek/wieczorna/uklad.json:67-73` notch x 43..48,
  y -48..-43 (przod-prawo).
- kolo bez `flat`: elipsa (:265, rysowana :345-346).
- kolo z `flat` (`sciecie_mm` :73-89): cieciwa prostopadla do kierunku `angle_deg` (stopnie od +X), w odleglosci `dist` od
  srodka; `h = math.sqrt(pol * pol - odl * odl)`; konce `(odl * nx - h * ny, odl * ny + h * nx)`, `(odl * nx + h * ny,
  odl * ny - h * nx)` (:87-89). Obrys = dluzszy luk z 360 odcinkow (:36, :269-276) zamkniety cieciwa; cieciwa dodatkowo kreska
  5 px (:37, :349-353). Uklady okragle: `angle_deg: -45.0`, `dist: 49.3559`, `d: 100.0`
  (np. `modele_plytek/okragla_ramkowa_wieczorna/uklad.json:65-72`) - cieciwa ok. 16 mm po stronie przod-prawo.

D4. Co rysuje (`ui/mapa.py:296-402`). Kolor i podpis WYLACZNIE `g.rgb` / `g.podpis` ze stanu; mapa nie wola `statusy`.
- gniazdo bez pracy: kontroler daje status `pusty`, rgb (235,235,235), podpis "" (`kontroler_api.py:3197-3199`, `statusy.py:84`);
  mapa: wypelnienie `g.rgb`, sam numer w kolorze `#8a929c` (`ui/mapa.py:364`, `:367`, `:380-383`).
- praca poza gniazdem: NIE na mapie; pod mapa "Poza gniazdami: n" i przycisk na prace, tlo `p.rgb`, napis `p.podpis` (status
  `poza_gniazdem` (160,0,0) "poza gniazdem": `kontroler_api.py:3188-3190`, `statusy.py:86`); wybrana - ramka 4 px
  (`ui/okno.py:769-780`).
- dwie prace w gniezdzie: skan aktywny - status `podwojny` (170,80,200) "dwie prace" (`kontroler_api.py:3200-3202`,
  `statusy.py:85`); skan nieaktywny - status / kolor / podpis pierwszej pracy, `prace` = obie (`kontroler_api.py:3203-3205`).
  Mapa rysuje jedno gniazdo.
- status nieznany: kontroler mapuje klucz przez `ST.status(klucz)`; nieznany = wiersz `nieznany`, zolty (240,200,40) "sprawdz"
  (`statusy.py:140-143`, `:91`); praca `rgb=st.hex, podpis=st.napis` (`kontroler_api.py:3150`, `:3172`); mapa rysuje `g.rgb`.
- skad kolor i podpis: `ST.status_pracy(...)` -> klucz, `ST.status(klucz).hex` / `.napis` (`kontroler_api.py:3147-3151`); gniazdo
  przejmuje `p.status, p.kolor, p.rgb, p.podpis` (`kontroler_api.py:3205`).
- podpis: numer + podpis, czcionka od 18 do 8 px, najwieksza mieszczaca sie; gdy zadna - sam numer (`ui/mapa.py:384-402`);
  rynienka - numer i podpis w jednej linii (:371-377); kolor napisu `styl.tekst_na(g.rgb)` (:367).
- zaznaczenie - obrys bialy 9 px + ciemny 5 px; kursor - przerywany obrys akcentu (:316-331); przygaszenie - `styl.TLO` alfa 150
  (:335-339).
- plytka nieaktywna bez prac - napis "Plytka {napis}." (:119, :124-125, :299-308); brak plytki - "Tu pojawi sie mapa plytki po
  pierwszym skanie." (:122-123).
- trafienie klikniecia: wnetrze sciezki gniazda albo do 8 px poza kolem promienia gornego (:405-415).
- legenda (`ui/czesci.py:1391-1408`): gniazda z pracami i niepustym podpisem; podpowiedz `ST.status(g.status).opis`; prace poza
  gniazdem nie wchodza.

---------------------------------------------------------------------------------------------------------------------
## E. Liczniki i legenda

E1. Skad liczby:
- liczniki na kafelku: `Plytka.liczniki` z kontrolera (`ui/czesci.py:840`, `:865-880`), liczone na plytke z `p.kolor` wszystkich
  prac (takze poza gniazdem): `kontroler_api.py:3206-3209`. Kolor znaczka `ST.status(ST.STATUS_WG_KOLORU[klasa]).hex`
  (`ui/czesci.py:868-869`), klasa nieznana - `ST.status(None)` (:873-876).
- "do obejrzenia: n" / "sprawdzona": liczone w oknie, na jedna plytke (`ui/czesci.py:209-217`, `:225-241`).
- legenda: liczona w oknie z gniazd pokazanej plytki (`ui/czesci.py:1391-1398`).
- "Do dofrezowania: n": `len(pozycje)` listy ze stanu (`ui/czesci.py:1349`); "Ta doba" = `stan.do_dofrezowania`, "Wszystkie
  otwarte" = `stan.do_dofrezowania_biezaca` (`ui/okno.py:697`).
- pasek: kolejka / wstrzymane ze `stan.kolejka` (`ui/czesci.py:586-594`).
- `stan.liczniki` i `stan.prac` (cala doba, tylko skany aktywne - `kontroler_api.py:1545-1549`): okno ich nie czyta (brak uzyc
  w `ui/`). Podsumowania calej doby na ekranie nie ma.

E2. "Wszystko zielone" / "0 do sprawdzenia" przy problemach:
- skan `blad` / `niezgodny_uklad` / `plytka_nie_z_trybu` / `zastapiony`: prace maja `kolor` None (`session.py:1117-1118`,
  `statusy.py:164-167`) -> liczniki puste; kafelek bez licznikow i bez "brak prac" (`aktywna` False, `ui/czesci.py:877`); stan
  plytki = napis ze stanu, np. "analiza nie powiodla sie" (`ui/czesci.py:234-235`, `statusy.py:207-218`). Nic zielonego.
- `do_powtorzenia`: zielone z programu sa zolte (`session.py:1123-1124`); stan plytki "do ponownego skanu" (`ui/czesci.py:234-235`);
  "do obejrzenia" nie liczone (puste `dozwolone`).
- plytka bez numeru: prace zielone maja status `czeka_na_numer`, `kolor` None (`statusy.py:179`, `:196-197`) i nie wchodza do
  licznikow. Gdy wszystkie prace sa takie, kafelek pokazuje "brak prac" (`ui/czesci.py:877-878`, `N.PLYTKA_BEZ_PRAC`), stan
  "przeanalizowana" (`ui/czesci.py:239-240`); gniazda (176,196,222) "podaj nr plytki" (`statusy.py:87-88`).
- "sprawdzona" (`ui/czesci.py:225-241`): skan przyjety, brak otwartego pytania o ponowny skan, 0 prac do obejrzenia, numer znany,
  jakakolwiek praca z dozwolonym poleceniem. Komunikaty plytki (np. `numer_niezgodny`, `konflikt_projektu`, `skan_juz_jest`)
  nie wplywaja - plytka moze byc "sprawdzona" z otwartym komunikatem.
- liczby dotycza jednej plytki; plytki wczesniejszych zmian tej doby sa domyslnie ukryte (`ui/okno.py:665-666`, przycisk "Pokaz
  wczesniejsze zmiany (n)"), a ich pytania i komunikaty nie sa panelami (F1).

---------------------------------------------------------------------------------------------------------------------
## F. Komunikaty i pytania

F1. Miejsca i limity:
- pasek bledow programu: komunikaty bez plytki albo plytki spoza stanu, poziom "blad" albo trwale (`ui/okno.py:70-72`,
  `:822-825`); bez limitu; 2 pierwsze w calosci w granicy 25 % wysokosci okna (`ui/okno.py:54`, `:167`, `:271`), reszta
  przewijana; jednakowe jako grupa z licznikiem (`ui/okno.py:75-80`).
- obszar uwag: panel osoby (gdy `wymaga_operatora` albo zmiana osoby; poza limitem, `ui/okno.py:833-838`), potem najwyzej
  `PANELI = 3` (`ui/okno.py:51`, `:854-857`) w kolejnosci: informacja ekranu, odmowa spoza stanu, panel numeru, pytania pokazanej
  plytki, komunikaty pokazanej plytki, pozostale ogolne (nie bledy, nie trwale) od najnowszego; reszta jako "... i jeszcze n -
  zamknij powyzsze, zeby je zobaczyc" (`ui/okno.py:858-859`).
- panel "Nowy wynik czeka" - w kolumnie plytek, poza limitem (`ui/okno.py:676-678`).
- pytania i komunikaty INNYCH plytek ze stanu nie sa panelami nigdzie (`ui/okno.py:818-819`, `:822-823`): tylko znaczniki
  kafelka "czeka na odpowiedz" / "ma komunikat" (`ui/okno.py:667`, `:670`) i tytuly w panelu "Nowy wynik czeka" (gdy plytka
  jest "nowa"). Dotyczy tez ulotnych komunikatow z skan_id, np. `skan_juz_jest` z skan_id istniejacego skanu (`aplikacja.py:1261`).
- nic nie zaslania mapy (brak okien modalnych i nakladek); panele nad lista plytek i mapa zabieraja jej miejsce (mapa sie
  przesuwa / zmniejsza - ochrona E3-P15, `ui/okno.py:331-339`). Jedyna nakladka na mapie - przygaszenie 800 ms.

F2. Co znika samo i kiedy:
- zegary w oknie: blysk paska 1500 ms (`ui/czesci.py:45`, `:523-526`); przygaszenie / ochrona mapy 800 ms (`ui/okno.py:52`,
  `:119-122`, `:720-721`); "Odswiez pule" znow aktywne po 15 s (`ui/czesci.py:44`, `:553-558`, `:623-627`). Panele nie maja
  zegarow.
- `_odmowa` i `_informacja` znikaja przy KAZDYM nastepnym poleceniu (`ui/okno.py:524-525`), np. Spacja.
- ulotne komunikaty kontrolera - gdy kontroler je usunie: ponad 50 (najstarsze nietrwale; `kontroler_api.py:130`, `:3404-3408`),
  odmowy po udanym poleceniu (`kontroler_api.py:3493-3495`), `pula` po gotowej puli (`kontroler_api.py:4058-4059`),
  `lista_nie_zapisana` po udanym zapisie (`kontroler_api.py:3132-3133`), `plik_niedostepny:<sha16>` po zapisie skanu
  (`aplikacja.py:1441`). Bez zegara czasu.
- trwale komunikaty plytki (`blad_analizy:<skan_id>`, `niezgodny_uklad:<skan_id>`, `skan_do_powtorzenia:<skan_id>`,
  `blad_inspekcji`, `numer_niezgodny` - `kontroler_api.py:3241-3286`) powstaja przy kazdym zbudowaniu stanu ze statusu skanu;
  znikaja po "Zamknij" (`_ukryte`, `kontroler_api.py:3984-3993`) albo gdy skan wypadnie z doby.

F3. Blad analizy nowego skanu a mapa poprzedniej plytki: `blad_analizy:<skan_id>` jest trwaly i nie znika sam. Gdy ekran sie
nie przelaczyl (A2), ten komunikat nie jest ani panelem, ani wpisem paska bledow, bo ma skan_id plytki obecnej w stanie
(`ui/okno.py:819`, `:822-823`). Widac tylko "NOWA" + "ma komunikat" na kafelku i tytul w panelu "Nowy wynik czeka"
(`ui/czesci.py:777`, `:792`); te znikaja dopiero po obejrzeniu plytki albo po zmianie doby (`ui/okno.py:358`, `:373`, `:411`).
Po obejrzeniu plytki z bledem i powrocie kafelkiem do poprzedniej panel bledu znika (jest przypiety do plytki), zostaje
znacznik "ma komunikat". Pasek stanu po zakonczonej analizie pokazuje "Analiza: nic nie czeka" (`ui/czesci.py:585`), bez wzmianki
o bledzie.

---------------------------------------------------------------------------------------------------------------------
## G. Rozjazdy opis - kod (tylko niezgodne albo spelnione inaczej)

ui_wieczor.md:
G1. :3 "kontrakt: `stanowisko/kontroler_api.py` w wersji 2 ... pola wersji 2 czytane wprost" - `kontroler_api.py:87`
    `WERSJA_KONTRAKTU = 6`; okno czyta pola pozniejszych wersji: `stan.tryb` / `stan.rano` (`ui/okno.py:318`; wersja 3 -
    `kontroler_api.py:893`), `stan.ramki` (wersja 4 - `kontroler_api.py:894`; `ui/czesci.py:537`, `:595`), `Praca.wpisy_do_wyboru`
    (wersja 5 - `kontroler_api.py:313-315`; `ui/czesci.py:1195`).
G2. :3 "Jedyne wyliczenia ekranu to liczenie po stanie: prace do obejrzenia ... - do napisu stanu plytki, klawisza N i reguly
    przelaczania" - `do_obejrzenia` uzywa tez kursor strzalek (`ui/okno.py:485-487`); okno liczy tez legende (grupowanie po
    podpisie i kolorze, `ui/czesci.py:1391-1398`) i liczbe plytek wczesniejszych zmian (`ui/okno.py:666`).
G3. :12 "`ui/napisy.py` | napisy ekranu ... (UTF-8, polskie znaki)" - `ui/napisy.py:112-115` bez polskich znakow ("Krazek do
    wyboru:", "{krazek} (wybrany)", "wspolczynnik {wspolczynnik} - kliknij, jesli praca pochodzi z tego krazka", "Cofnij wybor
    krazka").
G4. :21 'Po prawej "Skanuj w programie skanera / Spacja: program czeka na plik"' oraz :88-89 'napis "Program czeka na plik skanu
    [Spacja] / Skan uruchamiasz w programie skanera"' - kod: `ui/napisy.py:38`
    `SKANUJ_ATRAPA = "Czekam na plik skanu  [Spacja]\nSkanujesz w programie skanera"`.
G5. :23 "`Plytka.pytania` / `Plytka.komunikaty` nie sa czytane" - `Plytka.pytania` jest czytane: `ui/czesci.py:220-222`
    (`czeka_na_odpowiedz_o_ponowny_skan`), uzyte w napisie stanu plytki `ui/czesci.py:232-233`.
G6. :23 "Najwyzej 3 panele naraz" - panel wyboru osoby jest poza limitem (`ui/okno.py:833-838`; limit dotyczy listy `budowa`,
    `ui/okno.py:854`): do 4 paneli + "... i jeszcze n".
G7. :25 "legenda statusow obecnych na tej plytce" - legenda tylko z gniazd (`ui/czesci.py:1393-1394`); status prac poza gniazdem
    do niej nie wchodzi.
G8. :26 "klikniecie pozycji pokazuje prace" - otwierane jest gniazdo pozycji z `_nr_pracy = 0` (`ui/okno.py:444-446`, `:409`);
    przy dwoch pracach w gniezdzie widok pokazuje pierwsza prace gniazda, nie praca_id pozycji.
G9. :30 "`lacznik.postep` odswieza sam pasek" - gdy w stanie z sygnalem postepu zmienil sie obiekt `stan.plytki`, okno robi pelne
    `pokaz_stan` (`ui/okno.py:299-300`).
G10. :30 "Wlasny stan okna to wylacznie wybor technika: ..." - okno trzyma tez m.in. `_poza`, `_nr_pracy`, `_praca_widoku`,
    `_pokaz_wczesniejsze`, `_znane`, `_nieobejrzane`, `_blysk_nowej`, `_nr_komunikatow` (`ui/okno.py:97-111`) i pamiec obrazow
    (`ui/obraz.py:110-112`).
G11. :34 "strzalki = kursor ... (pierwsze nacisniecie - otwarte gniazdo albo pierwsza praca do obejrzenia)" - przy otwartym
    gniezdzie pierwsze nacisniecie od razu przesuwa kursor na sasiada otwartego gniazda w kierunku strzalki
    (`ui/okno.py:483`, `:488-490`); na pierwsza prace do obejrzenia - tylko bez kursora i bez otwartego gniazda (`:484-487`).
G12. :34 "gdy przycisk z fokusem znika (nowe panele), fokus wraca do okna" - spelnione dla widzetow usuwanych przez `wyczysc`
    (`ui/czesci.py:145-149`); przyciski krazkow usuwane `removeWidget` + `deleteLater` bez oddania fokusu (`ui/czesci.py:1196-1198`);
    zamkniecie widoku pracy chowa przyciski decyzji bez oddania fokusu (`ui/czesci.py:1213-1216`).
G13. :35 "Bez wybranej osoby przyciski decyzji i odpowiedzi wymagajace osoby sa nieaktywne, a obok jest wyjasnienie" - przyciski
    akcji plytki przy naglowku (Dopusc / Cofnij zastapienie / Cofnij dopuszczenie) sa nieaktywne bez wyjasnienia
    (`ui/okno.py:766-767`); "Ponow teraz" (ponowienie decyzji) zawsze aktywny (`ui/czesci.py:811-812`, aktywny `True`).
G14. :36 (i :25) "Polecenia plytki z `Plytka.dozwolone` sa przy naglowku mapy" - naglowek pokazuje tylko 4 polecenia
    (`ui/okno.py:755-756`); `potwierdz_ponowny_skan` / `odrzuc_ponowny_skan` z `dozwolone` (`kontroler_api.py:3215-3216`) sa tylko
    w panelu pytania - po "Pozniej" na pytaniu o ponowny skan nie ma ich na ekranie.
G15. :37 "przelacza ekran TYLKO, gdy na pokazanej plytce nie ma pracy do obejrzenia (czerwonej / zoltej bez decyzji)" - kod liczy
    tylko prace z "ukruszona" w `dozwolone` (`ui/czesci.py:216-217`), tj. prace skanu `przyjety` w trybie wieczor
    (`kontroler_api.py:3159-3165`): plytka `do_powtorzenia` z zoltymi bez decyzji i plytki nieaktywne nie blokuja przelaczenia;
    blokuja za to takze prace szare, pomaranczowe i nieznane.
G16. :38 "Po kazdej zmianie zawartosci mapy ... sa pomijane przez 800 ms" - po przelaczeniu trybu rano -> wieczor
    `_mapa_podpis = None` (`ui/okno.py:322`), pierwsze odswiezenie mapy wieczornej nie wlacza ochrony (`ui/okno.py:712-713`), takze
    gdy plytka zmienila sie w trybie rano (`_wybierz_plytke` dziala w obu trybach, `ui/okno.py:315`); kursor nie jest wtedy
    zerowany (`ui/okno.py:714-715` pominiete).
G17. :54 '"Nastepna do obejrzenia" i stan "do obejrzenia: n" licza prace ...' - "do obejrzenia: n" liczy tez prace poza gniazdem
    (`ui/czesci.py:216`; `Plytka.prace` = gniazda + poza, `kontroler_api.py:428-430`), a "Nastepna" / N szuka tylko w gniazdach
    (`ui/okno.py:466`): przy samych pracach poza gniazdem N nic nie robi, choc "do obejrzenia: n" > 0.
G18. :83 'Pokazanie plytki z pytaniem o ponowny skan zdejmuje z "nowych" takze jej poprzedni skan' - kod zdejmuje `moze_zastapic`
    bez sprawdzania, czy pytanie jest otwarte (`ui/okno.py:374-376`, `:413`); `moze_zastapic` jest w stanie takze po "Nie, to nowy
    wsad" (odrzucenie filtruje tylko pytanie: `kontroler_api.py:3343`; pole: `kontroler_api.py:3231`, `session.py:1190`).
G19. :86-87 'kafelek skanu, ktory pytanie proponuje zastapic - napis "poprzedni skan tej plytki"' - `ui/napisy.py:72`
    `PLYTKA_POPRZEDNI_SKAN = "poprzedni skan"`.
G20. :33 "Na ekranie nie ma sciezek ani nazw plikow / folderow" - (zastrzezenie: ekran poranny w tym samym oknie, wg :57 poza
    paczka) panel Excela pokazuje `szczegoly.folder` (`ui/okno_excela.py:266`) i nazwe z kolumny H (`ui/okno_excela.py:280`).

ui.md (opisuje `ui_test.py`):
G21. :1 "ui - okno programu (dzis: `ui_test.py` ...)", :3, :19 "pelne `ui` (plan v2)" jako modul przyszly - pakiet
    `stanowisko/ui/` istnieje (`ui/__init__.py:21-27` `utworz_okno`, `ui/okno.py:83` `OknoWieczor`); `ui_test.py` to osobne okno
    testowe.
G22. :7 "male kolka = ubytki (czarne = czerwone, szare = zolte)" - mapa okna testowego rysuje wszystkie kolka ubytkow tym samym
    czarnym piorem (`ui_test.py:167-173`); czarne / szare rozroznia tylko obraz odchylek (`ui_test.py:226`).
G23. :9 "Pod polem numeru okno podpisuje wynik" - etykieta w siatce (4, 2), obok pola numeru (4, 1) (`ui_test.py:294`, `:298`).
G24. :9 'Pole wspolczynnika pokazuje wtedy "auto (wieczorna 1,225 / poranna 1,000)"' - format z kropka:
    `f"auto (wieczorna {wiecz:.3f} / poranna {S.WSPOLCZYNNIK_PORANNA[0]:.3f})"` (`ui_test.py:362`).

Zgodne (nie wypisane): ui_wieczor.md - ok. 147 sprawdzonych twierdzen; ui.md - ok. 39 (liczone po twierdzeniach w zdaniach,
liczba przyblizona). Niesprawdzane z kodu (wyniki testow, pomiary, wyglad na prawdziwym ekranie): ui_wieczor.md :10 (czesc
"Do testow"), :15, :19 (wyniki A-P1 / E3-A1p), :41 (pomiary), :45, :49; ui.md :11 (kolory i tabela przy strazniku zaleza od
wyniku `porownaj`), :15, :18 (czasy).
