# Proba T14 - technik obsluguje program bez instrukcji (zestaw E3-A11d)

Plan etapu 3, sekcja 7, test T14: osoba, ktora nie widziala programu, dostaje jedna strone z obrazkami i zadnych
podpowiedzi; symulator podaje skany. Wieczor 5 zadan, rano 6 zadan. Zaliczenie: 11 z 11 zadan wykonanych, 0 interwencji
obserwatora; miejsca zawahania dluzszego niz 10 s spisane i poprawione albo swiadomie zostawione.

Probe prowadzi wlasciciel. Ten katalog daje wszystko, co trzeba przygotowac; samej proby nikt jeszcze nie wykonal.

| Plik | Do czego |
|------|----------|
| `jedna_strona.html` | jedyna pomoc dla osoby badanej - wydrukowac (1 strona A4 poziomo, kolor) |
| `arkusz_obserwacji.html` | arkusz obserwatora - wydrukowac (1 strona A4 pionowo) |
| `scenariusz_symulatora.md` | polecenia i przebieg: co podaje symulator, co ma byc na ekranie |
| `symulator_t14.py`, `scenariusz_t14.json` | program z udawanym skanerem i dane proby (wylacznie sztuczne) |
| `jedna_strona.md`, `arkusz_obserwacji.md`, `obrazki/` | zrodla stron do druku |

## Przygotowanie (ok. 15 minut)

1. Komputer z ekranem 1920 x 1080, mysz i klawiatura. Najlepiej laptop stanowiska; moze byc PC.
2. Wydrukuj `jedna_strona.html` i `arkusz_obserwacji.html`: otworz w przegladarce, Drukuj, A4, skala 100 %, bez
   naglowkow i stopek przegladarki, z grafika tla. Kazdy plik ma dac jedna strone.
3. W oknie polecen, w tym katalogu, uruchom sprawdzenie: `PY symulator_t14.py --sprawdz` (co to jest `PY` - patrz
   `scenariusz_symulatora.md`). Ostatni wiersz: `SPRAWDZENIE T14 BEZ EKRANU: zgodne 18 z 18 krokow`. Inny wynik = nie
   zaczynaj proby, zglos.
4. Przygotuj stoper (telefon) i dlugopis. Opcjonalnie: plytka wieczorna i poranna z kilkoma starymi pracami oraz dwie
   kuwety - osoba moze wtedy naprawde przekladac prace. Bez nich osoba mowi glosno, co by przelozyla.
5. Osoba badana nie moze wczesniej widziec programu ani instrukcji `wieczor` i `poranek`.

## Przebieg

1. Powiedz osobie tylko to: program pomaga kontrolowac prace przed piecem i rozkladac je po piecu; skanera tu nie ma -
   skan uruchamia klawisz Spacja; ta kartka to cala pomoc; prosze mowic glosno, co robisz i czego szukasz.
2. Daj kartke `jedna_strona`. Uruchom czesc wieczorna: `PY symulator_t14.py wieczor --dziennik t14_wieczor.log`.
3. Czytaj polecenia W1-W5 z arkusza, po jednym. Po kazdym zapisz: wykonane, interwencja, zawahanie ponad 10 s (gdzie, ile).
4. Zamknij okno programu. Uruchom czesc poranna: `PY symulator_t14.py rano --dziennik t14_rano.log`. Polecenia R1-R6.
5. Zamknij okno. Podsumowanie z okna polecen (albo z plikow dziennika) porownaj z arkuszem.

## Czego nie mowic i nie robic

- Nie nazywaj przyciskow, kolorow ani miejsc na ekranie. Nie pokazuj palcem. Nie kiwaj glowa.
- Na pytanie odpowiadaj: zrob tak, jak uwazasz. Jesli osoba utknie na dluzej niz 60 s i prosi o pomoc - pomoz, zapisz
  interwencje i idz dalej (zadanie jest wtedy niezaliczone, ale reszta proby ma sens).
- Nie tlumacz komunikatow programu. To, czy osoba je rozumie, jest przedmiotem proby.
- Nie poprawiaj bledow osoby (np. zly kandydat w R2) - zapisz je.

## Co zrobic z wynikiem

1. Wypelnij podsumowanie arkusza: n z 11, liczba interwencji, lista zawahan.
2. Dla kazdego zawahania i kazdej interwencji zapisz decyzje: poprawic (napis, uklad ekranu albo jedna strone) albo
   zostawic (z powodem).
3. Arkusz (skan albo zdjecie bez nazwiska osoby - same inicjaly) i dwa pliki dziennika zapisz w
   `Ramki/etap3/odbior_koncowy/` jako dowod T14; wynik wpisz do raportu odbioru koncowego.
4. Wynik inny niz 11 z 11 i 0 interwencji: T14 niezaliczony - poprawki przez wlasciwa paczke (napisy i ekran: paczki
   okna; jedna strona i instrukcje: `Ramki/stanowisko/instrukcje` i ten katalog), potem powtorka z INNA osoba.

## Po zmianie programu

Zrzuty i strony do druku odtwarza sie z katalogu `Ramki/stanowisko`:
`PY narzedzia/zrzuty_instrukcji.py --t14`, potem `PY narzedzia/instrukcje_html.py`; zgodnosc napisow z programem
pilnuje `testy/test_instrukcje.py`.
