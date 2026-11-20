# Wieczor - kontrola prac przed piecem (6 krokow)

Program oglada skan plytki i pokazuje, ktore prace wziac do reki. Decyzja o kazdej pracy nalezy do Ciebie.

<!-- obok 61 -->

![Ekran wieczorny: u gory pasek stanu, z lewej plytki, w srodku mapa plytki, z prawej praca i lista](obrazki/wieczor_ekran.png)

Ekran: u gory pasek stanu, z lewej plytki tej zmiany, w srodku mapa plytki, z prawej wybrana praca, pod nia lista do
dofrezowania. Komunikaty i pytania programu pojawiaja sie nad mapa.

<!-- dalej -->

## Kolory na mapie

| Kolor i podpis gniazda | Co robisz |
|--------------------|--------------------|
| zielony "OK" | nic - praca rozpoznana, bez ubytku |
| czerwony "UBYTEK" | obejrzyj w reku i zdecyduj |
| zolty "sprawdz", "nie sprawdzono", "sprawdz ulozenie" | program nie jest pewny - obejrzyj i zdecyduj |
| szary "bez projektu" | program nie zna tej pracy - obejrzyj golym okiem jak dotad i zdecyduj |
| pomaranczowy "poprawiana recznie" | ksztalt rozni sie gladko od projektu - obejrzyj i zdecyduj |
| zolty "popraw ulozenie", "skan poruszony", "powtorz skan"; fioletowy "dwie prace"; ciemnoczerwony "poza gniazdem" | popraw ulozenie i zeskanuj plytke jeszcze raz |
| po decyzji: czerwony "UKRUSZONA", morski "OK - zatwierdzona" | nic - decyzja zapisana |

<!-- koniec obok -->

<!-- kolumny -->

1. **Zacznij zmiane.** Uruchom program: `Stanowisko.cmd` albo skrot na pulpicie. Na pytanie "Kto teraz pracuje?" kliknij
   swoje nazwisko - bez tego decyzje sie nie zapisza. W pasku u gory sprawdz: tryb "Wieczor", a przy "Folder projektow"
   liczba plikow (np. "plikow projektow: 16"). Gdy jest "brak plikow projektow", kliknij "Odswiez pule".
2. **Uloz prace i zeskanuj plytke.** Prace klad do gniazd brzegiem do gory, jedna praca w jednym gniezdzie; most do
   podluznej rynienki z przodu. Wsun plytke do skanera do oporu i uruchom skan w programie skanera. Plik skanu program
   bierze sam - w pasku przy "Analiza" widac postep. W tym czasie ukladaj nastepna plytke.
3. **Przeczytaj mape.** Po analizie widzisz mape plytki: kazde gniazdo ma kolor i podpis (tabela wyzej). Napis nad mapa,
   np. "do obejrzenia: 4", mowi, ile prac czeka na Twoja decyzje.
4. **Obejrzyj wskazane prace.** Wyjmij plytke. Kliknij czerwone albo zolte gniazdo - z prawej pojawi sie praca: kuweta,
   zab, rozmiar ubytku i obraz z zaznaczonym miejscem. Wez te prace do reki i obejrzyj to miejsce.
5. **Zdecyduj.** "Ukruszona" (klawisz U) - odloz prace na bok; program dopisze ja do listy do dofrezowania.
   "OK" (klawisz O) - praca jest cala i wraca do pozostalych. Pomylka: "Cofnij decyzje" (klawisz C).
   "Nastepna [N]" pokazuje kolejna prace. Gdy napis plytki zmieni sie na "sprawdzona", plytka jest gotowa.
   ![Praca z gniazda 2 i przyciski decyzji](obrazki/wieczor_praca.png)
6. **Zakoncz.** Prace zielone i te z decyzja "OK" ida do pieca jak zwykle. Po ostatniej plytce przeczytaj liste
   w prawym dolnym rogu ("Do dofrezowania: 1" = jedna praca odlozona): kuweta, zab i krazek kazdej odlozonej pracy.
   "Zapisz liste do pliku" zapisuje ja w folderze danych programu. Liste przekaz tak, jak ustalono w pracowni.
   ![Lista do dofrezowania](obrazki/wieczor_lista.png)

## Gdy program prosi o ponowny skan

Komunikat "Skan do powtorzenia" podaje powod i gniazdo, np. "popraw ulozenie pracy (gniazdo 3)". Do ponownego skanu zadna
praca na tej plytce nie jest potwierdzona.

![Komunikat o powtorzeniu skanu](obrazki/wieczor_popraw.png)

Popraw prace w gniezdzie i zeskanuj plytke jeszcze raz. Na pytanie "Ponowny skan tej samej plytki?" odpowiedz
"Tak, to ponowny skan" (te same prace) albo "Nie, to nowy wsad" (na plytce leza juz inne prace).

![Pytanie o ponowny skan](obrazki/wieczor_ponowny.png)

<!-- koniec kolumn -->

<!-- stopka: Dane na obrazkach sa sztuczne. Klopot? Karta: Co robic, gdy nie dziala. Instrukcja E3-A11d, 20.11.2026. -->
