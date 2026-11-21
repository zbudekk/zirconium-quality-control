# Ramka swietlna: program na Raspberry Pi - od czystej karty SD do dzialajacej ramki

Dla kogo: dla osoby, ktora sklada ramke i nie zna Linuksa. Rob kroki po kolei, niczego nie pomijaj.
Kazde polecenie z szarego pola wpisz dokladnie tak, jak jest (albo skopiuj), i nacisnij Enter.

**WAZNE - [NIE SPRAWDZONE BEZ SPRZETU].** Ta instrukcja i pliki z katalogu `ramka/rpi` powstaly na podstawie kodu
programu ramki i jego opisu (`ramka/README.md`), bez Raspberry Pi i bez matrycy. ZADEN krok nie byl wykonany na
prawdziwym sprzecie. Na komputerze sprawdzono tylko to, co sie dalo: skladnie skryptow, zgodnosc nazw opcji i pol
z programem, dzialanie programu na atrapie sprzetu. Przy pierwszym przejsciu zapisuj w arkuszu (nizej), co zadzialalo,
a co nie - to bedzie podstawa poprawek.

Co jest czym:

| Rzecz | Co to |
|---|---|
| ramka | obudowa z Raspberry Pi, matryca diod 64 x 64, czujnikami plytek; ramka poranna ma tez klawiature numeryczna |
| ramka W / ramka P | W = wieczorna (nazwa w sieci `ramka-w`), P = poranna (nazwa w sieci `ramka-p`) |
| laptop | komputer stanowiska z programem "Stanowisko"; laptop i ramki musza byc w tej samej sieci Wi-Fi |
| program ramki | katalog `ramka` z programu "Stanowisko"; na ramce trafia do `/opt/ramka/ramka` |
| plik konfiguracji ramki | `/etc/ramka/ramka.json` na ramce: ktora to ramka, adres, port, klucz, ustawienia matrycy |
| klucz | haslo wspolne laptopa i OBU ramek; bez niego ramka nie przyjmuje polecen |

Pliki w katalogu `ramka/rpi` (sa w paczce programu, nic nie trzeba pobierac osobno):

| Plik | Do czego |
|---|---|
| `zainstaluj_ramke.sh` | instaluje program na ramce: kopia do `/opt/ramka/ramka`, plik `/etc/ramka/ramka.json`, autostart |
| `sprawdz_ramke.sh` | kontrola: tabela wierszy OK / BRAK i przy kazdym BRAK - co zrobic |
| `ramka.service` | opis uslugi systemu (autostart po wlaczeniu zasilania); instaluje go `zainstaluj_ramke.sh` |
| `ramka.json.wzor` | wzor pliku konfiguracji; `zainstaluj_ramke.sh` robi z niego `/etc/ramka/ramka.json` |

## Arkusz - wypelnij w trakcie (osobno dla kazdej ramki)

Tych rzeczy instrukcja nie zgaduje. Sprawdz i zapisz:

| Co | Ramka W | Ramka P |
|---|---|---|
| Model Raspberry Pi (napis na plytce, np. "Raspberry Pi 4 Model B"; program byl pisany pod Pi 4) | | |
| Nakladka sterujaca matryca (np. Adafruit RGB Matrix Bonnet) i czy zworki sa zlutowane: "E -> 8", "GPIO4-GPIO18" | | |
| Matryca: liczba diod (ma byc 64 x 64) i napis z tylu | | |
| System wgrany na karte (nazwa i wersja z Raspberry Pi Imager) | | |
| Nazwa komputera (`ramka-w` / `ramka-p`) | | |
| Nazwa uzytkownika i haslo ustawione w Raspberry Pi Imager (haslo zapisz w bezpiecznym miejscu, nie tutaj) | | |
| Nazwa sieci Wi-Fi | | |
| Adres IP ramki (z kroku 2) | | |
| Katalog plikow startowych: `/boot/firmware` czy `/boot` (krok 3) | | |
| Wersja Pythona (z kroku 2) | | |
| Jak zainstalowano biblioteke matrycy (krok 5: wariant, data, wersja) | | |
| `obrot` i `lustro` po kroku 10 | | |
| Czas od wlaczenia zasilania do gotowosci (krok 11) | | |

## Krok 1. Karta SD z systemem [NIE SPRAWDZONE BEZ SPRZETU]

Potrzebne: karta microSD, czytnik kart w laptopie, internet na laptopie.

1. Na laptopie zainstaluj program "Raspberry Pi Imager" (ze strony raspberrypi.com) i uruchom go.
2. Urzadzenie: wybierz swoj model Raspberry Pi (zapisz go w arkuszu).
3. System: "Raspberry Pi OS (other)" -> "Raspberry Pi OS Lite (64-bit)". Opis programu ramki zaklada wersje
   "Bookworm" (Python 3.11). Program wymaga Pythona 3.11 albo nowszego. Jesli Imager proponuje nowsza wersje systemu,
   z ta nowsza NIKT programu ramki nie sprawdzal - zapisz w arkuszu, ktora wybrales.
4. Karta: wybierz swoja karte microSD.
5. Imager zapyta o wlasne ustawienia - wybierz "Edytuj ustawienia" i wpisz (nazwy przyciskow moga sie roznic
   miedzy wersjami programu Imager - szukaj tych samych pol):
   - nazwa komputera (hostname): `ramka-w` dla ramki wieczornej albo `ramka-p` dla porannej - DOKLADNIE tak,
   - nazwa uzytkownika i haslo (wymysl, zapisz),
   - siec Wi-Fi: nazwa i haslo TEJ SAMEJ sieci, w ktorej jest laptop; kraj sieci: PL,
   - zakladka "Uslugi": zaznacz "Wlacz SSH" i "Uzyj hasla".
6. Zapisz karte i poczekaj na komunikat o koncu. Wyjmij karte, wloz do Raspberry Pi w ramce.

Uwaga: w obudowie ramki karta jest dostepna dopiero po zdjeciu blatu i panelu - wloz ja przed zlozeniem albo
pracuj na elektronice lezacej na stole.

## Krok 2. Pierwsze wlaczenie i polaczenie z laptopa (SSH) [NIE SPRAWDZONE BEZ SPRZETU]

1. Wlacz zasilanie ramki. Pierwszy start trwa kilka minut.
2. Na laptopie otworz "Wiersz polecenia" (klawisz Windows, wpisz `cmd`, Enter) i wpisz (zamiast `UZYTKOWNIK` -
   nazwa z kroku 1; dla ramki porannej `ramka-p`):

```
ssh UZYTKOWNIK@ramka-w.local
```

3. Przy pierwszym polaczeniu padnie pytanie "Are you sure you want to continue connecting" - wpisz `yes`, Enter.
   Potem haslo z kroku 1 (przy wpisywaniu nic sie nie pokazuje - tak ma byc), Enter.
4. Jestes "na ramce": wiersz zaczyna sie od `UZYTKOWNIK@ramka-w`. Wszystkie polecenia z nastepnych krokow, o ile nie
   napisano "na laptopie", wpisujesz w tym oknie.
5. Sprawdz i zapisz w arkuszu adres IP i wersje Pythona:

```
hostname -I
python3 --version
```

Gdy `ssh` nie laczy ("Could not resolve hostname" albo brak odpowiedzi): patrz "Typowe bledy" na koncu.

## Krok 3. Ustawienia startowe: config.txt i cmdline.txt [NIE SPRAWDZONE BEZ SPRZETU]

Biblioteka matrycy wymaga wylaczonego dzwieku, a jeden z czujnikow plytek uzywa pinu, ktory zajmuje SPI.

1. Sprawdz, gdzie system trzyma pliki startowe:

```
ls /boot/firmware/config.txt /boot/config.txt
```

   Gdy polecenie wypisze `/boot/firmware/config.txt` bez bledu - to jest wlasciwy plik (takze wtedy, gdy wypisze
   oba: w nowszych systemach w `/boot/config.txt` jest tylko informacja, ze plik przeniesiono). Tylko gdy
   `/boot/firmware/config.txt` nie istnieje, wlasciwy jest `/boot/config.txt` - wtedy w poleceniach ponizej wpisuj
   `/boot` zamiast `/boot/firmware`. Plik `cmdline.txt` jest w tym samym katalogu. Zapisz w arkuszu, ktory katalog.
2. Otworz `config.txt` w edytorze:

```
sudo nano /boot/firmware/config.txt
```

3. Znajdz wiersz `dtparam=audio=on` i zmien go na `dtparam=audio=off` (gdy takiego wiersza nie ma - dopisz
   `dtparam=audio=off` na koncu pliku). Gdy jest wiersz `dtparam=spi=on` - zmien go na `dtparam=spi=off`
   (gdy go nie ma albo zaczyna sie od `#` - dopisz na koncu `dtparam=spi=off`).
4. Zapisz: Ctrl+O, Enter. Wyjdz: Ctrl+X.
5. Otworz `cmdline.txt`:

```
sudo nano /boot/firmware/cmdline.txt
```

6. Plik ma JEDEN dlugi wiersz. Przejdz na jego koniec (klawisz End), dopisz spacje i `isolcpus=3`. Nie naciskaj
   Enter, nie rob drugiego wiersza. Zapisz (Ctrl+O, Enter) i wyjdz (Ctrl+X).
7. Uruchom ramke ponownie i po 1-2 minutach polacz sie jeszcze raz jak w kroku 2:

```
sudo reboot
```

## Krok 4. Pakiety systemu [NIE SPRAWDZONE BEZ SPRZETU]

Ramka musi miec w tym kroku internet (przez Wi-Fi).

```
sudo apt update
sudo apt install -y python3-gpiozero python3-evdev
```

`python3-gpiozero` = czujniki plytek, `python3-evdev` = klawiatura ramki porannej (na ramce wieczornej tez zainstaluj -
nie szkodzi). Gdy `apt` zglasza blad sieci - sprawdz Wi-Fi ("Typowe bledy").

## Krok 5. Biblioteka matrycy (rpi-rgb-led-matrix) [NIE SPRAWDZONE BEZ SPRZETU]

Program ramki steruje matryca przez biblioteke `rpi-rgb-led-matrix` (autor: hzeller) z dodatkiem dla Pythona
(modul `rgbmatrix`). Tej biblioteki NIE MA w pakietach systemu - trzeba ja zbudowac na ramce. Skrypt
`zainstaluj_ramke.sh` tego nie robi; tylko sprawdza, czy biblioteka jest.

Sposob budowy zmienial sie miedzy wersjami biblioteki. Obowiazuje opis w pobranej bibliotece: plik
`bindings/python/README.md`. Ponizej wariant zapisany w opisie programu ramki (`make build-python`, instalacja
w Pythonie systemu). Jesli polecenia ponizej koncza sie bledem - zrob to, co mowi `bindings/python/README.md`,
i zapisz w arkuszu, co zadzialalo.

```
sudo apt install -y git python3-dev cython3 build-essential
cd ~
git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
cd rpi-rgb-led-matrix
make build-python
sudo make install-python
```

Wazne: biblioteka ma byc zainstalowana w Pythonie SYSTEMU (`/usr/bin/python3`), bo program ramki dziala jako
administrator (root). Nie instaluj jej w srodowisku wirtualnym (venv).

Kontrola - ma wypisac `OK`:

```
sudo python3 -c "import rgbmatrix; print('OK')"
```

Proba samej matrycy (z planu budowy ramki; matryca i zasilacz podlaczone). Zworki nakladki: "E -> 8" (wymagana dla
matrycy 64 x 64) i "GPIO4-GPIO18" (usuwa migotanie). Polecenie pokazuje obraz probny, konczysz Ctrl+C:

```
cd ~/rpi-rgb-led-matrix
make
sudo ./examples-api-use/demo -D0 --led-rows=64 --led-cols=64 --led-gpio-mapping=adafruit-hat-pwm
```

Gdy zworka "GPIO4-GPIO18" NIE jest zlutowana: zamiast `adafruit-hat-pwm` wpisz `adafruit-hat`, a po kroku 7
zmien w pliku `/etc/ramka/ramka.json` pole `mapowanie` na `"adafruit-hat"` (patrz "Zmiana pliku konfiguracji").

## Krok 6. Kopiowanie programu ramki na ramke [NIE SPRAWDZONE BEZ SPRZETU]

Program ramki to katalog `ramka` w katalogu programu "Stanowisko" na laptopie:
`KATALOG_INSTALACJI\wersje\NUMER_WERSJI\program\ramka` (KATALOG_INSTALACJI = tam, gdzie jest `Stanowisko.cmd`;
NUMER_WERSJI jest w pliku `wersja_biezaca.txt`). Kopiujesz CALY katalog `ramka`, razem z podkatalogiem `rpi`.

Wariant A - przez siec (`scp`), na laptopie w "Wierszu polecenia" (jedno polecenie, w cudzyslowie pelna sciezka):

```
scp -r "KATALOG_INSTALACJI\wersje\NUMER_WERSJI\program\ramka" UZYTKOWNIK@ramka-w.local:
```

Dwukropek na koncu jest potrzebny. Po hasle pliki trafia do katalogu domowego na ramce (`~/ramka`).

Wariant B - pendrive. Na laptopie skopiuj katalog `ramka` na pendrive. Wloz pendrive do portu USB ramki i na ramce:

```
lsblk
```

Znajdz na liscie pendrive (rozmiar jak twoj pendrive, zwykle `sda1`). Potem (zamiast `sda1` - nazwa z listy):

```
sudo mount /dev/sda1 /mnt
cp -r /mnt/ramka ~/
sudo umount /mnt
```

Kontrola (oba warianty) - maja byc widoczne 4 pliki, w tym `zainstaluj_ramke.sh`:

```
ls ~/ramka/rpi
```

## Krok 7. Instalacja programu (jeszcze bez autostartu) [NIE SPRAWDZONE BEZ SPRZETU]

```
cd ~/ramka/rpi
sudo bash zainstaluj_ramke.sh --bez-uslugi
```

Skrypt sam rozpoznaje ramke po nazwie komputera (`ramka-w` = wieczorna, `ramka-p` = poranna). Gdy nazwa jest inna,
dodaj `--rola W` albo `--rola P`.

DRUGA ramka musi dostac TEN SAM klucz co pierwsza (laptop ma jedno pole klucza dla obu ramek). Na pierwszej ramce
odczytaj klucz:

```
sudo grep klucz /etc/ramka/ramka.json
```

i na drugiej ramce zainstaluj tak (zamiast `KLUCZ` - odczytany ciag znakow, bez cudzyslowow):

```
sudo bash zainstaluj_ramke.sh --bez-uslugi --klucz KLUCZ
```

Co skrypt robi: sprawdza Pythona, kopiuje program do `/opt/ramka/ramka`, zaklada `/etc/ramka/ramka.json` z pliku
`ramka.json.wzor` (tylko gdy pliku jeszcze nie ma - istniejacego nie zmienia), sprawdza biblioteki i na koncu wypisuje
tabele kontroli. Wiersze `BRAK` maja pod spodem strzalke `->` i to, co trzeba zrobic. Skrypt mozna uruchamiac wiele razy.

Plik `/etc/ramka/ramka.json` po instalacji: `rola` (W albo P), `sprzet` = "rpi", `host` = "0.0.0.0" (ramka slucha
w calej swojej sieci - dzieki temu laptop ja widzi; bez tego pola program slucha tylko "sam siebie", adres 127.0.0.1),
`port` = 8765, `klucz` (losowy albo podany), oraz ustawienia sprzetu z wartosciami domyslnymi programu: `piny_halla`
[19, 25, 8], `jasnosc` 60, `obrot` 0, `lustro` false, `mapowanie` "adafruit-hat-pwm", `spowolnienie_gpio` 4,
`klawisz_zamknij_piec` "KEY_KPASTERISK".

## Krok 8. Pierwsze uruchomienie reczne [NIE SPRAWDZONE BEZ SPRZETU]

```
cd /opt/ramka
sudo python3 -m ramka --sprzet rpi --konfiguracja /etc/ramka/ramka.json
```

Dobrze: pojawia sie wiersz z tekstem `slucha na 0.0.0.0:8765` i polecenie "wisi" (program dziala). Na matrycy ma byc
widoczna cienka niebieska ramka dookola (stan "gotowa"), a z przodu po lewej maly kwadrat lacznosci z laptopem
(zielony albo czerwony). Poloz plytke - z przodu ma sie pokazac jej numer i napis
"BRAK" (brak planu od laptopa - to normalne). Zostaw program wlaczony na czas kroku 9. Koniec: Ctrl+C.

Zle:
- `sprzet niedostepny: brak biblioteki rgbmatrix` - wroc do kroku 5,
- `sprzet niedostepny: brak biblioteki gpiozero` - wroc do kroku 4,
- `sprzet niedostepny: inicjalizacja sprzetu nie powiodla sie` - sprawdz nakladke, tasme matrycy, zasilanie; czy program
  uruchomiles z `sudo`,
- obraz jest, ale obrocony albo odbity - krok 10,
- obraz migocze - sprawdz krok 3 (`dtparam=audio=off`, `isolcpus=3`) i zworke "GPIO4-GPIO18".

## Krok 9. Kontrola z laptopa [NIE SPRAWDZONE BEZ SPRZETU]

Program ramki dziala (krok 8 albo 11). Na laptopie:

1. Wpisz klucz do ustawien programu "Stanowisko": plik `ustawienia.toml` w katalogu instalacji, sekcja `[ramki]`:
   `klucz` = klucz z ramki (w cudzyslowie), `wieczorna_host` = "ramka-w.local", `poranna_host` = "ramka-p.local",
   `port` = 8765. Gdy nazwy `.local` u ciebie nie dzialaja, wpisz zamiast nich adresy IP z arkusza.
2. Szybka proba w "Wierszu polecenia" (zamiast `KLUCZ` - klucz; dla ramki porannej `ramka-p.local`):

```
curl.exe -H "X-Ramka-Klucz: KLUCZ" http://ramka-w.local:8765/stan
```

   Dobrze: wiersz tekstu zaczynajacy sie od `{"protokol": 1` z polami `"rola"`, `"program"`, `"plytka"`.
   To samo w przegladarce (`http://ramka-w.local:8765/stan`) pokaze blad 401 - przegladarka nie wysyla klucza;
   blad 401 tez oznacza, ze ramka dziala i jest widoczna w sieci.
3. Uruchom `Samokontrola.cmd` w katalogu instalacji: wiersz `ramka_wieczorna` / `ramka_poranna` ma zaczynac sie od `OK`.
4. W programie "Stanowisko" kliknij "Test LED": cala matryca swieci kolejno na czerwono, zielono, niebiesko i bialo,
   po 8 sekundach wraca do stanu "gotowa".

## Krok 10. Test diod wedlug gniazd plytki: test_led [NIE SPRAWDZONE BEZ SPRZETU]

Ten test zapala po kolei diody pod kazdym gniazdem plytki. Potrzebny jest plik kalibracji z laptopa.

1. Na laptopie, w katalogu instalacji (powstanie plik z polozeniami startowymi, policzonymi z ksztaltu plytek):

```
Polecenie.cmd -m ramka.kalibracja --domyslna --modele modele_plytek --wyjscie "%USERPROFILE%\Desktop\kalibracja_ramek.json"
scp "%USERPROFILE%\Desktop\kalibracja_ramek.json" UZYTKOWNIK@ramka-w.local:
```

2. Na ramce zatrzymaj program ramki (matryce moze obslugiwac tylko jeden program naraz): Ctrl+C w oknie z kroku 8,
   a gdy dziala juz autostart z kroku 11:

```
sudo systemctl stop ramka
```

3. Uruchom test. Ramka wieczorna:

```
cd /opt/ramka
sudo python3 -m ramka.test_led --kalibracja ~/kalibracja_ramek.json --uklad wieczorna --konfiguracja /etc/ramka/ramka.json
```

   Ramka poranna:

```
cd /opt/ramka
sudo python3 -m ramka.test_led --kalibracja ~/kalibracja_ramek.json --uklad poranna --konfiguracja /etc/ramka/ramka.json
```

   Nazwy ukladow: `wieczorna`, `wieczorna_r54` (ramka W), `poranna`, `poranna_r54` (ramka P) - wybierz ten, ktory
   odpowiada twojej plytce. Plytek okraglych w pliku kalibracji jeszcze nie ma. Z opcja `--wszystkie` swieca wszystkie
   gniazda naraz przez 10 sekund.
4. Patrz z gory na plytke lezaca na ramce: przy kazdym gniezdzie ma zaswiecic jego otwor, a z przodu pokazuje sie
   numer gniazda. Na koniec program wypisuje `test LED: 19 gniazd ukladu wieczorna (ramka W)` (liczba zalezy od ukladu).
5. Obraz obrocony albo odbity lustrzanie: zmien w `/etc/ramka/ramka.json` pole `obrot` (0, 90, 180 albo 270) albo
   `lustro` (true / false) - patrz "Zmiana pliku konfiguracji" - i powtorz test. Za jasno / za ciemno: `jasnosc`
   (1-100). Wynik zapisz w arkuszu. Swiatlo trafia obok otworow o 1-2 diody: to sprawa pliku kalibracji (osobna
   praca), zapisz, ktore gniazda i w ktora strone.
6. Gdy autostart byl juz wlaczony, uruchom program ramki z powrotem:

```
sudo systemctl start ramka
```

## Krok 11. Autostart [NIE SPRAWDZONE BEZ SPRZETU]

Gdy kroki 8-10 wyszly dobrze, zatrzymaj program uruchomiony recznie (Ctrl+C) i wlacz autostart:

```
cd ~/ramka/rpi
sudo bash zainstaluj_ramke.sh
```

Skrypt instaluje usluge `ramka.service`, wlacza ja i uruchamia. Od teraz program ramki startuje sam po wlaczeniu
zasilania i sam wstaje po awarii. Kontrola:

```
sudo bash sprawdz_ramke.sh
```

Ostatni wiersz ma brzmiec `WYNIK: bez brakow.` Potem proba zasilania: wyjmij wtyk zasilania ramki, odczekaj 10 sekund,
wloz. Zmierz czas do pojawienia sie niebieskiej ramki na matrycy (cel z planu: ponizej 60 sekund) i zapisz w arkuszu.
Powtorz krok 9 (kontrola z laptopa).

Przydatne polecenia (na ramce):

```
sudo systemctl status ramka
sudo systemctl stop ramka
sudo systemctl start ramka
sudo journalctl -u ramka -n 50 --no-pager
```

`status` = czy dziala, `stop` / `start` = zatrzymaj / uruchom, `journalctl` = ostatnie 50 wierszy dziennika programu.

## Krok 12. Druga ramka i wymiana programu na nowszy [NIE SPRAWDZONE BEZ SPRZETU]

Druga ramka: powtorz kroki 1-11 z druga nazwa (`ramka-p` zamiast `ramka-w`) i z opcja `--klucz` z kroku 7.

Nowsza wersja programu ramki (po aktualizacji programu "Stanowisko" na laptopie): powtorz krok 6 (kopia katalogu
`ramka`) i krok 11 (`zainstaluj_ramke.sh`). Plik `/etc/ramka/ramka.json` zostaje bez zmian. Przed kopiowaniem usun
stara kopie z katalogu domowego na ramce: `rm -rf ~/ramka`.

## Zmiana pliku konfiguracji

```
sudo nano /etc/ramka/ramka.json
```

Zmien tylko wartosc po dwukropku, zostaw cudzyslowy i przecinki tak, jak byly. Zapisz: Ctrl+O, Enter; wyjdz: Ctrl+X.
Potem uruchom program ramki ponownie (`sudo systemctl restart ramka`, a przy pracy recznej Ctrl+C i polecenie
z kroku 8). Kontrola pliku: `sudo bash sprawdz_ramke.sh` w katalogu `~/ramka/rpi` (wiersz "konfiguracja").
Program nie przyjmuje pliku z nieznanym polem ani z bledem zapisu - wtedy usluga nie wstaje, a `sprawdz_ramke.sh`
pokazuje w wierszu "konfiguracja", co jest zle.

Adres nasluchu `host`: "0.0.0.0" = ramka slucha w kazdej sieci, do ktorej jest podlaczona (wariant domyslny tej
instrukcji, dziala takze wtedy, gdy siec zmieni ramce adres IP). Mozna wpisac konkretny adres IP ramki - wtedy
ramka slucha tylko na nim, ale gdy siec przydzieli jej inny adres, program nie wystartuje. Klucz chroni przed obcymi
urzadzeniami w sieci, ale polaczenie nie jest szyfrowane - ramki i laptop powinny pracowac w sieci stanowiska,
nie w sieci dla gosci.

## Typowe bledy

| Co widzisz | Co to znaczy | Co zrobic |
|---|---|---|
| `ssh: Could not resolve hostname ramka-w.local` | laptop nie znajduje ramki po nazwie | sprawdz, czy laptop i ramka sa w tej samej sieci Wi-Fi; uzyj adresu IP zamiast nazwy (adres pokaze router albo monitor i klawiatura podlaczone do Raspberry Pi: polecenie `hostname -I`) |
| `ssh` nie odpowiada kilka minut po wlaczeniu | ramka nie weszla do Wi-Fi albo SSH nie jest wlaczone | podlacz monitor i klawiature do Raspberry Pi; siec ustawisz poleceniem `sudo nmtui` (albo `sudo raspi-config`, pozycja z siecia bezprzewodowa); jesli nie da sie zalogowac - wgraj karte od nowa (krok 1) i sprawdz nazwe sieci, haslo i "Wlacz SSH" |
| `Permission denied` przy `ssh` | zla nazwa uzytkownika albo haslo | wpisz dane z arkusza; wielkosc liter ma znaczenie |
| `sudo: ...: command not found` albo `$'\r': command not found` przy skrypcie | plik skryptu zostal zmieniony po drodze (np. otwarty i zapisany w Notatniku) | skopiuj katalog `ramka` jeszcze raz prosto z katalogu programu (krok 6), niczego w nim nie otwieraj |
| `[ramka] BLAD: potrzebne uprawnienia administratora` | skrypt uruchomiony bez `sudo` | wpisz polecenie od `sudo bash ...` |
| `[ramka] BLAD: nie wiem, ktora to ramka` | nazwa komputera nie jest `ramka-w` ani `ramka-p` | dodaj `--rola W` albo `--rola P` |
| wiersz `BRAK rgbmatrix` | nie ma biblioteki matrycy w Pythonie systemu | krok 5; kontrola: `sudo python3 -c "import rgbmatrix; print('OK')"` |
| blad przy `make build-python` albo `sudo make install-python` (np. `externally-managed-environment`, brak pliku, brak polecenia) | pobrana wersja biblioteki matrycy instaluje sie inaczej niz w kroku 5 | zrob to, co mowi plik `bindings/python/README.md` w katalogu `~/rpi-rgb-led-matrix`; biblioteka ma trafic do Pythona systemu; zapisz w arkuszu, co zadzialalo |
| KONIEC z "kod 3" po `zainstaluj_ramke.sh` | program skopiowany, ale brakuje biblioteki; autostart NIE zostal wlaczony | zrob to, co stoi przy wierszach BRAK, i uruchom skrypt jeszcze raz |
| program startuje, w dzienniku `ramka slucha tylko na 127.0.0.1` | w pliku konfiguracji nie ma pola `host` | wpisz `"host": "0.0.0.0"` ("Zmiana pliku konfiguracji") |
| `curl.exe` z laptopa: brak odpowiedzi, a `sprawdz_ramke.sh` na ramce pokazuje `OK port` | laptop i ramka w roznych sieciach albo siec blokuje ruch miedzy urzadzeniami (siec dla gosci) | podlacz oba do tej samej, zwyklej sieci stanowiska; sprobuj adresu IP zamiast nazwy `.local` |
| `curl.exe` zwraca pusta odpowiedz / kod 401 | klucz na laptopie inny niz na ramce | porownaj `klucz` w `ustawienia.toml` z wynikiem `sudo grep klucz /etc/ramka/ramka.json` |
| usluga ciagle startuje od nowa (`journalctl` pokazuje ten sam blad co 2 sekundy) | program konczy sie bledem zaraz po starcie | przeczytaj blad w `sudo journalctl -u ramka -n 50 --no-pager`; najczesciej plik konfiguracji albo biblioteka matrycy |
| matryca ciemna, a `sprawdz_ramke.sh` bez brakow | zasilanie matrycy, tasma, zworka "E -> 8" albo zla wartosc `mapowanie` | proba samej matrycy z kroku 5 (przedtem `sudo systemctl stop ramka`) |
| numer plytki sie nie pokazuje albo jest zly | czujniki plytek albo magnesy | to sprawa montazu (piny 19, 25, 8; magnes = stan niski); zapisz, ktora plytka daje jaki numer - pole `"plytka"` w odpowiedzi z kroku 9 |
| po wylaczeniu i wlaczeniu zasilania zniknely zmiany | karta pracuje w trybie "tylko do odczytu" (nakladka systemu plikow, wlaczana w `raspi-config`) | na czas zmian wylacz nakladke w `sudo raspi-config` (Performance Options -> Overlay File System), zrob zmiany, wlacz ponownie; tej instrukcji NIE trzeba konczyc wlaczeniem nakladki |

## Czego ta instrukcja nie obejmuje

- skladania elektroniki i obudowy (plan budowy ramki),
- kalibracji "gniazdo -> diody" na zlozonej ramce (poprawianie pliku kalibracji) - osobna praca,
- zapory sieciowej na Raspberry Pi i karty w trybie tylko do odczytu - do ustalenia po pierwszych probach.
