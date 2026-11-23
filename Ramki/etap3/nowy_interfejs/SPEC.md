# Nowe okno programu "Stanowisko" - specyfikacja (paczka E3-U1, 23.11.2026)

Decyzja wlasciciela 23.11.2026: okno budujemy OD NOWA, bez wzorowania sie na starym ukladzie. Ma wygladac
profesjonalnie, byc proste, intuicyjne, logicznie i schludnie pogrupowane. Glowne kolory programu: trzy kolory
wskazane przez wlasciciela. Makieta (zrodlo ukladu): `makieta/Main.dc.html` (wieczor), `makieta/Rano.dc.html`
(poranek), `makieta/Instalator.dc.html` (okno instalatora - paczka I1); podglad:
https://claude.ai/artifact/GjGLeby7cvMnwRrKx12xU7 (prywatny, konto wlasciciela). Makieta to HTML - odczytaj z niej
uklad, odstepy i kolory; dane w niej sa przykladowe.

## 1. Co sie NIE zmienia

- Kontrakt okna: `stanowisko/kontroler_api.py` i `stanowisko/aplikacja.py` - bez zmian. Okno dalej dostaje stan
  i wola polecenia przez `kontroler.wykonaj`. Brak czegos w kontrakcie = wpis w raporcie, nie zmiana kontraktu.
- KAZDA funkcja starego okna zostaje (dane, akcje, pytania, komunikaty, stany szczegolne, skroty klawiszowe).
  Zrodla: `opisy_modulow/ui_wieczor.md`, `ui_rano.md`, `aplikacja.md`, `ui/napisy*.py`, `statusy.py`, stary kod
  `ui/*.py`. W raporcie tabela "funkcja -> gdzie jest w nowym oknie" (zadna pozycja nie moze zostac pusta).
- Wymagania techniczne: zadnych okien modalnych; watek okna nigdy nie czeka; kolory i napisy statusow wylacznie
  ze stanu; zero sciezek i nazw plikow na ekranie; Spacja nigdy nie klika przycisku; ochrona 800 ms po zmianie
  zawartosci; odswiezanie tylko zmienionych czesci; wejscie `stanowisko.ui.utworz_okno(kontroler, lacznik)`.
- Rozdzielczosci: 1920x1080, 1536x864 (125 %), 1280x720 (150 %), takze z `QT_SCALE_FACTOR` 1,25 / 1,5; nic
  ucietego, bez przewijania poziomego, przyciski decyzji i pytan zawsze widoczne.

## 2. Kolory i typografia (jedno miejsce w kodzie: `ui/motyw.py`)

| Rola | Kolor |
|---|---|
| tlo okna | `#191919` |
| powierzchnia (paski, panel pracy) | `#303030` |
| powierzchnia wglebiona (kafelki, pola, pasek stanu) | `#242424` |
| akcent (wybor, glowna akcja, fokus) | `#338CED`; napis NA akcencie `#0F1720` |
| akcent jako tekst na `#303030` | `#9CC9F9` / `#6FB0F5` |
| tlo wybranej pozycji i pytania | `#1D2733` z obwodka `#338CED` |
| linie | `#3F3F3F` na powierzchni, `#2B2B2B` na tle, obwodki pol `#4A4A4A` |
| tekst | glowny `#F2F2F2`, pomocniczy `#B8B8B8`, przygaszony `#9E9E9E` (tylko na `#191919` / `#242424`) |

- Statusy prac na ciemnym tle (wartosci RGB ekranu w `statusy.py` - wolno zmienic TYLKO te liczby): OK `#3FB46A`,
  ubytek / ukruszona `#E5484D`, sprawdz `#E2B93B`, OK zatwierdzona `#2BA89A`, bez projektu `#8C8C8C`, poprawiana
  recznie `#E8833A`, dofrezowany `#F0B429`, dwie prace `#A678D9`; pozostale dobierz w tej samej jasnosci. Napis na
  kolorze statusu zawsze `#111111`. Kolory diod ramki bez zmian.
- Status nie moze byc rozpoznawalny tylko po barwie: gniazdo z ubytkiem ma jasna obwodke 2 px, puste gniazdo
  obwodke przerywana bez wypelnienia, wybrane gniazdo pierscien akcentu; w legendzie i na kafelkach zawsze napis.
- Kontrast tekstu co najmniej 4,5:1 (test automatyczny na wszystkich parach z `motyw.py`).
- Czcionka: "Segoe UI Variable Text", zapas "Segoe UI"; cyfry tabelaryczne. Rozmiary: 12 (pomocniczy), 13-14
  (tresc), 15 (przyciski decyzji, numer plytki), 18-20 (naglowek plytki / pieca), 64 (numer biezacej kuwety).
- Ksztalt: promien 4 px (znaczniki 3 px), obwodki 1 px, bez cieni, bez gradientow, bez ikon-emoji, bez
  kolorowych paskow z lewej strony kafelka. Siatka odstepow 4 / 8 / 12 / 16 / 20 px. Cel klikniecia min. 44 px.
- Przyciski: glowna akcja = wypelnienie akcentem; zwykla = obwodka `#4A4A4A`; "Ukruszona" = wypelnienie
  czerwonym statusu; "OK" = neutralny (zielen jest zastrzezona dla statusu ze stanu). Skrot klawiszowy pokazany
  w ramce po prawej stronie przycisku.

## 3. Uklad (wspolny szkielet obu trybow)

1. PASEK GORNY (52 px, `#303030`): nazwa programu; przelacznik trybu Wieczor / Poranek; doba i zmiana; po prawej
   osoba z przyciskiem zmiany (lista osob rozwija sie pod paskiem, bez okna modalnego).
2. LEWA KOLUMNA (ok. 280 px): wieczorem "Plytki tej zmiany" (kafelek: numer, godzina, stan, liczniki ubytek /
   sprawdz / OK; nowy wynik na gorze; "Wczesniejsze zmiany (n)"); rano "Piec n" (plytki pieca, na dole lista
   "Do zamkniecia pieca brakuje" i przycisk "Zamknij piec").
3. SRODEK: strefa pytan i komunikatow o STALEJ wysokosci nad mapa (jedno pytanie naraz, reszta w liczniku
   "i jeszcze n"; mapa nigdy sie nie przesuwa); naglowek plytki; mapa plytki z legenda obok; na dole lista
   "Do dofrezowania" (tabela, filtr Ta doba / Wszystkie otwarte). Rano: zakladki "Rozkladanie kuwet",
   "Kompletne i braki", "Ostatni zamkniety piec", "Excel"; biezaca kuweta duza cyfra, pole numeru kuwety,
   tabela kuwet.
4. PRAWA KOLUMNA (ok. 340-360 px, `#303030`) = "Praca": gniazdo i status, Kuweta / Zab / Krazek, ubytki, obraz
   odchylek; decyzje na STALYM miejscu na dole kolumny (Ukruszona U, OK O, Cofnij decyzje C, Nastepna N).
   Rano: "Ktory to projekt?" z kandydatami, na dole "Przypisz recznie" / "Bez projektu".
5. PASEK STANU (32 px, `#242424`, na dole): skaner, analiza (postep / kolejka), projekty (+ "Odswiez"), ramki
   W / P, Excel (rano), wersja programu. Bledy programu: licznik w pasku stanu + rozwijana lista.
Ponizej 1500 px szerokosci kolumny boczne zwezaja sie (240 / 320), odstepy 12 px; nic nie znika.

## 4. Znaleziska analizy, ktore nowe okno ma zamknac

- S3-3: panel "Podaj numer plytki" ma w tytule numer / godzine skanu plytki, ktorej dotyczy, i jest zwiazany
  z jej `skan_id`; przyjscie nowego wyniku nie podmienia jego przyciskow; ochrona 800 ms obejmuje takze panele.
- S3-4: "Program nie wskazal ubytku" tylko, gdy inspekcja byla i dala wynik "ok"; przy "nie sprawdzono",
  "blad kontroli", "bez projektu" napis "Tej pracy program nie sprawdzil".
- S3-14: w czasie analizy nowego skanu mapa poprzedniej plytki jest oznaczona "poprzednia plytka" i przygaszona.
- S3-15: po powrocie z trybu rano kursor gniazda wyzerowany, ochrona 800 ms; pozycja listy "do dofrezowania"
  otwiera dokladnie te prace (`praca_id`), klawisz N pod ochrona.
- S3-16: lista kuwet wybierana po numerze kuwety, nie po indeksie wiersza; "Wszystkie kuwety rozlozone - mozesz
  zamknac piec" tylko bez blokad; "Przypisanie: program (dopasowanie pewne)" nie przy konflikcie.
- Pytanie o ponowny skan pokazuje prace czerwone / zolte bez decyzji, ktore zostaja do decyzji technika
  (logika: paczka N2; okno pokazuje to, co da stan).

## 5. Zakres paczki E3-U1 i kolejnosc

1. `ui/motyw.py` (kolory, czcionki, arkusz Qt, test kontrastu) i czesci wspolne (przycisk, kafelek, tabela,
   znacznik statusu, strefa komunikatow).
2. Szkielet okna + tryb wieczorny w calosci. 3. Tryb poranny + panel Excela. 4. Usuniecie starego kodu `ui/`.
5. Testy nowego okna (bez ekranu): kazda akcja i skrot, pytania, stany szczegolne, rozdzielczosci, zakaz sciezek,
   ochrona 800 ms, znaleziska z p. 4. Stare testy okna zastapione; lista "stary test -> nowy test" w raporcie.
6. Zrzuty nowego okna z atrapy (`--atrapa`, `--atrapa --rano`) w 1920x1080 i 1536x864 do `zrzuty/` - wlasciciel
   oglada je na telefonie.
Poza paczka (osobno): okno "Dzien skanera" i okno ustawien folderow w tym samym motywie (U2), instalator (I1),
opisy `ui_*.md`, instrukcje z obrazkami i dokumenty dnia sprzetu (teksty ekranu sie zmienia - spisz liste roznic).
