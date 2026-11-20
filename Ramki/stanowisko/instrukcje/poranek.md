# Poranek - rozkladanie pieca do kuwet

Program rozpoznaje prace po skanie plytek i pokazuje, ktore prace ida do ktorej kuwety.

<!-- obok 61 -->

![Ekran poranny: z lewej piec i jego plytki, z prawej kuwety do rozlozenia](obrazki/rano_ekran.png)

Ekran: z lewej piec i jego plytki (w gniezdzie numer kuwety i zab), z prawej kuwety do rozlozenia i wybrana praca.

<!-- dalej -->

## Kolory rano

| Kolor i podpis gniazda | Co robisz |
|--------------------|--------------------|
| zielony z numerem kuwety | nic - praca rozpoznana |
| zolty "wybierz" | kliknij gniazdo i wybierz jeden z dwoch projektow |
| bialy "nieznana" | przymierz na modelach, potem "Przypisz recznie" albo "Bez projektu" |
| czerwony "konflikt" | ten sam projekt w dwoch gniazdach - dla jednej z prac wybierz inny projekt albo "Bez projektu" |
| bursztynowy "zab dofrezowany" | zab do zlecenia juz odhaczonego - idzie do kuwety, Excel bez zmian |
| zolty "powtorz skan" | zeskanuj te plytke jeszcze raz |

<!-- koniec obok -->

<!-- kolumny -->

1. **Wlacz tryb poranny.** W pasku u gory, obok napisu trybu, kliknij przycisk ze strzalka i napisem "Poranek".
   Na pytanie "Kto teraz pracuje?" kliknij swoje nazwisko.
2. **Zeskanuj wszystkie plytki pieca.** Prace z pieca przeloz do gniazd plytek porannych, brzegiem do gory. Skanuj plytki
   po kolei: plytka do skanera, skan w programie skanera, w tym czasie ukladaj nastepna. Piec otwiera sie sam po
   pierwszym skanie; na ekranie przybywa plytka po plytce.
3. **Rozstrzygnij zolte i biale.** Kliknij zolte gniazdo. Porownaj prace z dwoma obrazkami pod "Ktory to projekt?"
   i kliknij "To ten projekt". Pomylka: "Cofnij wybor". Praca biala: "Przypisz recznie", wpisz numer kuwety,
   "Pokaz projekty" i wybierz projekt.
   ![Dwaj kandydaci](obrazki/rano_kandydaci.png)
4. **Rozkladaj kuwete po kuwecie.** Z prawej, w "Rozkladanie kuwet", jest duzy numer, np. "Kuweta 3228", a jej gniazda sa
   obwiedzione na plytkach (z ramka: zielone diody pod pracami). Przeloz te prace do kuwety i nacisnij Enter
   ("Rozlozona [Enter]") - program pokaze nastepna kuwete. Kolejnosc: "Od najliczniejszej" albo "Wedlug numeru".
5. **Pomylka i szukanie kuwety.** Enter za wczesnie: Backspace ("Cofnij [Backspace]") cofa ostatnia kuwete. Masz w reku
   inna kuwete: wpisz jej numer cyframi (program pokaze "Wpisany numer kuwety: ...") i nacisnij Enter - obwiedzione
   zostana jej prace.
6. **Zamknij piec.** Po ostatniej plytce kliknij "Zamknij piec". Program przejdzie na "Kompletne i braki":
   "Zlecenia kompletne - do odhaczenia w Excelu: 3" oraz "Braki w tym piecu: 1" - kuweta i zeby, ktorych brakuje (sa
   w innym piecu, w dofrezowaniu albo zaginely). Kuwete z brakami odstaw do nastepnego pieca.
   "Lista brakow (wszystkie piece): 1" pamieta braki miedzy piecami i dniami. Gdy przycisk jest szary, nad plytkami jest
   napisane, co trzeba zrobic najpierw.
   ![Kompletne i braki](obrazki/rano_braki.png)
7. **Excel (tryb pytaj).** Po zamknieciu pieca pojawia sie "Excel: wskaz wiersz". Kliknij zlecenie na liscie, porownaj
   wiersz z folderem zlecenia i kliknij "Zatwierdz wiersz 9" - dopiero wtedy pole B w Excelu robi sie zielone. Przy
   "wskaz wiersz (3 kand.)" najpierw kliknij wlasciwy wiersz na liscie kandydatow. Nie masz pewnosci:
   "Pomin - zaznacze recznie". "Pozniej" chowa liste; wraca po kliknieciu "Excel: wskaz wiersz". Komunikat
   "Excel nie jest podlaczony" znaczy: odhacz zlecenia kompletne w Excelu recznie.
   ![Excel: wskaz wiersz](obrazki/rano_excel.png)

## Bez ramki i z ramka

Komunikat "Ramka poranna nie jest podlaczona" znaczy: rozkladasz wedlug ekranu, wszystko inne dziala tak samo.
Z ramka: Enter, Backspace, cyfry i klawisz zamkniecia pieca na klawiaturze ramki dzialaja jak na laptopie. Po zdjeciu
plytki i polozeniu nastepnej ramka sama pokazuje jej prace.

<!-- koniec kolumn -->

<!-- stopka: Dane na obrazkach sa sztuczne. Klopot? Karta: Co robic, gdy nie dziala. Instrukcja E3-A11d, 20.11.2026. -->
