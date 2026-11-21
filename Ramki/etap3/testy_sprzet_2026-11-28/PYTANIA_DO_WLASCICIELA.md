# Pytania do wlasciciela przed testami na sprzecie 28-29.11.2026

Odpowiedz najpozniej do srody 25.11.2026: dopisz odpowiedzi tutaj i przekaz sesji prowadzacej projekt.
Najpilniejsze: P3, P1, P6, P8, P9 - od nich zalezy, co przygotowac PRZED weekendem. "Nie wiem" to tez odpowiedz.

**P1. 21.11 odpowiedziales: "Obie kwadratowe oraz jedna okragla" - nie wiemy, czy to ramki, czy plytki.
Ile ramek przyszlo: jedna czy dwie? Jaki otwor ma wkladka ramki: kwadratowy czy okragly? Jedna ramka:
wieczorna czy poranna?**
Od tego zalezy: wieczorna = plytki 1-3; poranna = plytki 4-6 i proba klawiatury (krok 3.9). Wkladka
okragla: kwadratowa do niej nie wejdzie - bez plytki okraglej ramkowej z czesci 3 zostaja kroki 3.1-3.4.
Odpowiedz: ......................................................................................

**P2. 21.11: zdjecie pliku `ramka_plytka_okragla_wieczorna_n8_v2.stl` = plytka okragla nr 8 starego ukladu
R54 (20 gniazd) - to plytka TESTOWA, nie do ramki. Na kazdej plytce policz dlugie rynienki (1 = uklad R59,
2 = stary R54; kwadratowa wieczorna ma 19 albo 20 gniazd, poranna 24 albo 33) i przepisz numer wybity.
Czy plytki kwadratowe maja wklejone magnesy?**
Od tego zalezy: program zna oba uklady; plytka R54 w kroku 3.7: `wieczorna_r54` / `poranna_r54`. Plytka nr 8
nie ma magnesow - na ramce nie swieci. Plytka bez magnesow: ramka nie odczyta jej numeru (krok 3.5 odpada).
Odpowiedz: ......................................................................................

**P3. Czy Raspberry Pi w ramce jest zlozone z matryca diod i czujnikami, ma karte SD i czy ktos wgral na
nia "program ramki"?**
Od tego zalezy: cala czesc 3. Programu nie ma albo nie wiesz: ktos musi go wgrac PRZED sobota (instrukcja
`ramka_raspberry_pi.md`, 12 krokow, kilka godzin) - napisz, kto i kiedy. Inaczej zostaja ogledziny (3.1).
Odpowiedz: ......................................................................................

**P4. Na jakim komputerze uruchomisz program?** Potrzebny Windows 10 albo 11 i 30 GB wolnego miejsca.
Od tego zalezy: na laptopie stanowiska dochodzi kilka odczytow (czesc 4); na innym komputerze odpadaja.
Odpowiedz: ......................................................................................

**P5. Czy skaner stoi przy tym samym komputerze? Do jakiego folderu program skanera zapisuje skany?**
Od tego zalezy: przy innym komputerze instalujesz nasz program takze tam albo przenosisz pliki skanow
pendrivem - wtedy odpada proba "program sam zauwaza skan" (krok 2.7).
Odpowiedz: ......................................................................................

**P6. Jaka siec laczy komputer z ramka (router w pracowni, hotspot)? Jaka siec Wi-Fi jest wpisana w ramce?**
Od tego zalezy: komputer i ramka musza byc w TEJ SAMEJ sieci. Bez tego komputer nie zobaczy ramki
i z czesci 3 zostaja kroki 3.1 i 3.2.
Odpowiedz: ......................................................................................

**P7. Czy masz projekty STL (z exocad) prac probnych?**
Od tego zalezy: z projektami program porowna prace z projektem (krok 2.7); bez nich beda szare.
Odpowiedz: ......................................................................................

**P8. Czy ramka ma ustawiony "klucz" (haslo ramki) i czy go znasz?** Klucz losuje skrypt, ktorym wgrywa
sie program ramki; zna go osoba, ktora wgrywala. Dwie ramki musza miec TEN SAM klucz.
Od tego zalezy: bez klucza (gdy ramka go wymaga) odpadaja kroki 3.4-3.9; klucz przywiez na kartce, tu NIE wpisuj.
Odpowiedz (znam / nie znam / ramka bez klucza / nie wiem): ........................................

**P9. Czy w programie skanera sa juz zlecenia pacjentow? Gdzie mozna zalozyc osobny folder na skany
testowe z tego dnia?**
Od tego zalezy: sa albo nie wiesz - skany testowe ida do osobnego folderu (krok 2.1), a kopie calego
folderu zlecen (krok 2.6) pomijamy: dane pacjentow nie moga wyjechac z laboratorium.
Odpowiedz: ......................................................................................
