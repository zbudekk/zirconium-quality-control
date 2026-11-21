#!/bin/bash
# zainstaluj_ramke.sh - instalacja programu ramki swietlnej na Raspberry Pi (E3-O4).
#
# [NIE SPRAWDZONE BEZ SPRZETU] - skrypt napisany wg kodu i README programu ramki. NIE byl uruchomiony na
# Raspberry Pi. Na komputerze PC sprawdzono tylko: skladnie (bash -n), konce linii i fragmenty Pythona.
#
# Uzycie (na Raspberry Pi, w katalogu ramka/rpi skopiowanego programu):
#   sudo bash zainstaluj_ramke.sh [--rola W|P] [--klucz KLUCZ] [--bez-uslugi]
#
#   --rola W|P     W = ramka wieczorna, P = ramka poranna (z klawiatura). Bez opcji: z nazwy komputera
#                  (ramka-w... = W, ramka-p... = P). Potrzebna tylko wtedy, gdy powstaje nowy plik konfiguracji.
#   --klucz KLUCZ  klucz wspolny laptopa i ramek (16-256 znakow bez odstepu). Bez opcji: losowy.
#                  Druga ramka ma dostac TEN SAM klucz co pierwsza (laptop ma jedno pole klucza).
#   --bez-uslugi   tylko kopia programu i plik konfiguracji; uslugi (autostartu) skrypt nie rusza.
#
# Co robi (mozna uruchamiac wiele razy):
#   1. sprawdza Pythona (3.11 albo nowszy),
#   2. kopiuje katalog programu "ramka" do /opt/ramka/ramka (stara kopia jest zastepowana),
#   3. zaklada /etc/ramka/ramka.json z pliku ramka.json.wzor - TYLKO gdy pliku jeszcze nie ma,
#   4. sprawdza biblioteki sprzetu (gpiozero, evdev, rgbmatrix) - NICZEGO nie instaluje i nie kompiluje,
#   5. instaluje usluge ramka.service; wlacza ja i uruchamia tylko wtedy, gdy biblioteki sa,
#   6. na koniec uruchamia sprawdz_ramke.sh (tabela OK / BRAK).
# Kody wyjscia: 0 = zrobione, 1 = blad (nic wiecej nie zrobiono), 3 = program skopiowany, ale brakuje biblioteki
# sprzetu - usluga nie zostala wlaczona.

set -u

KATALOG_PROGRAMU="/opt/ramka"
PLIK_KONFIGURACJI="/etc/ramka/ramka.json"
PLIK_USLUGI="/etc/systemd/system/ramka.service"
KLUCZ_WZORU="ZMIEN-TEN-KLUCZ-skrypt-instalacji-wstawia-losowy"
PYTHON="/usr/bin/python3"
INSTRUKCJA="instrukcje/ramka_raspberry_pi.md"

info() { echo "[ramka] $*"; }
brak() { echo "[ramka] BRAK: $*"; }
rada() { echo "[ramka]       -> $*"; }
blad() { echo "[ramka] BLAD: $*" >&2; exit 1; }

pomoc() {
    echo "Uzycie: sudo bash zainstaluj_ramke.sh [--rola W|P] [--klucz KLUCZ] [--bez-uslugi]"
    echo "  --rola W|P     W = ramka wieczorna, P = ramka poranna; bez opcji: z nazwy komputera (ramka-w / ramka-p)"
    echo "  --klucz KLUCZ  klucz wspolny laptopa i ramek (druga ramka: ten sam co pierwsza); bez opcji: losowy"
    echo "  --bez-uslugi   tylko kopia programu i plik konfiguracji, bez autostartu"
    echo "Opis krok po kroku: $INSTRUKCJA"
}

ROLA=""
KLUCZ=""
BEZ_USLUGI=0
while [ $# -gt 0 ]; do
    case "$1" in
        --rola)
            [ $# -ge 2 ] || blad "po --rola podaj W albo P"
            ROLA="$2"
            shift 2
            ;;
        --klucz)
            [ $# -ge 2 ] || blad "po --klucz podaj klucz (16-256 znakow bez odstepu)"
            KLUCZ="$2"
            shift 2
            ;;
        --bez-uslugi)
            BEZ_USLUGI=1
            shift
            ;;
        --help)
            pomoc
            exit 0
            ;;
        *)
            blad "nieznana opcja: $1 (dozwolone: --rola W|P, --klucz KLUCZ, --bez-uslugi, --help)"
            ;;
    esac
done

echo "[ramka] Instalacja programu ramki. UWAGA: skrypt NIE SPRAWDZONE BEZ SPRZETU - czytaj komunikaty."

[ "$(id -u)" = "0" ] || blad "potrzebne uprawnienia administratora - uruchom: sudo bash zainstaluj_ramke.sh"

TU="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)" || blad "nie moge ustalic katalogu skryptu"
ZRODLO="$(dirname "$TU")"
CEL="$KATALOG_PROGRAMU/ramka"

for PLIK in __init__.py __main__.py program.py serwer.py sprzet_rpi.py test_led.py; do
    [ -f "$ZRODLO/$PLIK" ] || blad "w $ZRODLO nie ma pliku $PLIK - skopiuj na ramke CALY katalog 'ramka' (z podkatalogiem rpi) i uruchom skrypt z ramka/rpi"
done
for PLIK in ramka.service ramka.json.wzor sprawdz_ramke.sh; do
    [ -f "$TU/$PLIK" ] || blad "obok skryptu nie ma pliku $PLIK - skopiuj na ramke caly katalog 'ramka'"
done

# ---------------------------------------------------------------- rola
if [ -z "$ROLA" ]; then
    case "$(hostname 2>/dev/null)" in
        ramka-w*|RAMKA-W*) ROLA="W" ;;
        ramka-p*|RAMKA-P*) ROLA="P" ;;
    esac
fi
case "$ROLA" in
    w) ROLA="W" ;;
    p) ROLA="P" ;;
esac
case "$ROLA" in
    W|P|"") ;;
    *) blad "rola ma byc W (wieczorna) albo P (poranna), a jest: $ROLA" ;;
esac

# ---------------------------------------------------------------- 1. Python
info "1/5 Python"
[ -x "$PYTHON" ] || blad "nie ma $PYTHON - potrzebny system Raspberry Pi OS z Pythonem 3.11 albo nowszym"
if ! "$PYTHON" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)'; then
    blad "$("$PYTHON" -V 2>&1) jest za stary: program ramki wymaga Pythona 3.11 albo nowszego (Raspberry Pi OS Bookworm albo nowszy)"
fi
info "    $("$PYTHON" -V 2>&1) - OK"

# ---------------------------------------------------------------- 2. kopia programu
info "2/5 Program do $CEL"
if [ "$ZRODLO" = "$CEL" ]; then
    info "    skrypt uruchomiony z $CEL - program juz jest na miejscu, nie kopiuje"
else
    mkdir -p "$KATALOG_PROGRAMU" || blad "nie moge zalozyc $KATALOG_PROGRAMU (karta tylko do odczytu? - patrz instrukcja, typowe bledy)"
    rm -rf "$CEL.nowy" "$CEL.stary"
    cp -r "$ZRODLO" "$CEL.nowy" || blad "kopiowanie $ZRODLO do $CEL.nowy nie powiodlo sie"
    find "$CEL.nowy" -type d -name "__pycache__" -prune -exec rm -rf {} +
    if [ -d "$CEL" ]; then
        mv "$CEL" "$CEL.stary" || blad "nie moge odsunac starej kopii $CEL"
    fi
    if ! mv "$CEL.nowy" "$CEL"; then
        [ -d "$CEL.stary" ] && mv "$CEL.stary" "$CEL"
        blad "nie moge wstawic nowej kopii do $CEL (stara kopia przywrocona)"
    fi
    rm -rf "$CEL.stary"
    chown -R root:root "$KATALOG_PROGRAMU"
    chmod -R u+rwX,go+rX,go-w "$KATALOG_PROGRAMU"
    info "    skopiowano"
fi
if ! (cd "$KATALOG_PROGRAMU" && "$PYTHON" -m ramka --help >/dev/null); then
    blad "program w $CEL nie startuje (polecenie: cd $KATALOG_PROGRAMU && $PYTHON -m ramka --help)"
fi
WERSJA_PROGRAMU="$(cd "$KATALOG_PROGRAMU" && "$PYTHON" -c 'import ramka; print(ramka.WERSJA)' 2>/dev/null)"
info "    program ramki $WERSJA_PROGRAMU - OK"

# ---------------------------------------------------------------- 3. plik konfiguracji
info "3/5 Plik konfiguracji $PLIK_KONFIGURACJI"
if [ -e "$PLIK_KONFIGURACJI" ]; then
    info "    plik juz jest - zostaje BEZ ZMIAN (opcje --rola i --klucz go nie zmieniaja)"
    chown root:root "$PLIK_KONFIGURACJI"
    chmod 600 "$PLIK_KONFIGURACJI"
else
    [ -n "$ROLA" ] || blad "nie wiem, ktora to ramka (nazwa komputera to nie ramka-w ani ramka-p) - dodaj opcje: --rola W (wieczorna) albo --rola P (poranna)"
    mkdir -p "$(dirname "$PLIK_KONFIGURACJI")" || blad "nie moge zalozyc katalogu $(dirname "$PLIK_KONFIGURACJI")"
    chmod 755 "$(dirname "$PLIK_KONFIGURACJI")"
    # argumenty: wzor, plik docelowy, rola, klucz zastepczy ze wzoru, klucz podany (pusty = losowy)
    if ! (umask 077 && "$PYTHON" - "$TU/ramka.json.wzor" "$PLIK_KONFIGURACJI" "$ROLA" "$KLUCZ_WZORU" "$KLUCZ" <<'PY_KONFIGURACJA'
import json
import os
import re
import secrets
import sys

wzor, cel, rola, klucz_wzoru, klucz = sys.argv[1:6]
with open(wzor, encoding="utf-8") as f:
    dane = json.load(f)
if dane.get("klucz") != klucz_wzoru:
    sys.exit("BLAD: plik wzoru ma inny klucz zastepczy niz skrypt - pliki z roznych wersji programu")
if rola not in ("W", "P"):
    sys.exit("BLAD: rola ma byc W albo P")
if not klucz:
    klucz = secrets.token_hex(24)
elif klucz == klucz_wzoru or not re.fullmatch(r"[!-~]{16,256}", klucz):
    sys.exit("BLAD: klucz ma miec 16-256 znakow (litery, cyfry, znaki) bez odstepu i nie moze byc kluczem zastepczym ze wzoru")
dane["rola"] = rola
dane["klucz"] = klucz
uchwyt = os.open(cel, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)  # istniejacego pliku nie nadpisuje
with os.fdopen(uchwyt, "w", encoding="ascii") as f:
    json.dump(dane, f, indent=2)
    f.write("\n")
PY_KONFIGURACJA
    ); then
        blad "nie udalo sie zalozyc $PLIK_KONFIGURACJI z pliku ramka.json.wzor"
    fi
    chown root:root "$PLIK_KONFIGURACJI"
    chmod 600 "$PLIK_KONFIGURACJI"
    info "    zalozono z wzoru: rola $ROLA, adres nasluchu i ustawienia matrycy jak we wzorze, klucz wpisany"
    info "    klucz dla laptopa odczytasz poleceniem: sudo grep klucz $PLIK_KONFIGURACJI"
fi

# ---------------------------------------------------------------- 4. biblioteki sprzetu
info "4/5 Biblioteki sprzetu (skrypt niczego nie instaluje)"
BRAK_BIBLIOTEK=0
if "$PYTHON" -c "import gpiozero" >/dev/null 2>&1; then
    info "    gpiozero (czujniki plytek) - OK"
else
    brak "gpiozero (czujniki plytek)"
    rada "sudo apt install python3-gpiozero"
    BRAK_BIBLIOTEK=1
fi
if "$PYTHON" -c "import evdev" >/dev/null 2>&1; then
    info "    evdev (klawiatura ramki porannej) - OK"
else
    brak "evdev (klawiatura ramki porannej; ramka wieczorna dziala bez niej)"
    rada "sudo apt install python3-evdev"
fi
if "$PYTHON" -c "import rgbmatrix" >/dev/null 2>&1; then
    info "    rgbmatrix (matryca diod) - OK"
else
    brak "rgbmatrix (biblioteka matrycy diod rpi-rgb-led-matrix z powiazaniem Python)"
    rada "tego skrypt NIE robi sam: wykonaj krok 'Biblioteka matrycy' z instrukcji $INSTRUKCJA,"
    rada "potem uruchom ten skrypt jeszcze raz"
    BRAK_BIBLIOTEK=1
fi

# ---------------------------------------------------------------- 5. usluga (autostart)
KOD=0
if [ "$BEZ_USLUGI" = "1" ]; then
    info "5/5 Usluga - pominieta (--bez-uslugi). Program uruchomisz recznie:"
    info "    cd $KATALOG_PROGRAMU && sudo python3 -m ramka --sprzet rpi --konfiguracja $PLIK_KONFIGURACJI"
    [ "$BRAK_BIBLIOTEK" = "1" ] && KOD=3
else
    info "5/5 Usluga ramka.service (autostart)"
    command -v systemctl >/dev/null 2>&1 || blad "nie ma polecenia systemctl - to nie jest Raspberry Pi OS z systemd"
    install -m 644 -o root -g root "$TU/ramka.service" "$PLIK_USLUGI" || blad "nie moge zapisac $PLIK_USLUGI"
    systemctl daemon-reload || blad "systemctl daemon-reload nie powiodlo sie"
    if [ "$BRAK_BIBLIOTEK" = "1" ]; then
        info "    plik uslugi zapisany, ale usluga NIE zostala wlaczona - brakuje biblioteki sprzetu (wiersze BRAK wyzej)"
        info "    po doinstalowaniu uruchom ten skrypt jeszcze raz"
        KOD=3
    else
        systemctl enable ramka.service || blad "systemctl enable ramka.service nie powiodlo sie"
        systemctl restart ramka.service || blad "usluga nie wystartowala - logi: sudo journalctl -u ramka -n 30 --no-pager"
        info "    usluga wlaczona (startuje sama po wlaczeniu zasilania) i uruchomiona"
        sleep 3
    fi
fi

# ---------------------------------------------------------------- kontrola
echo
if [ "$BEZ_USLUGI" = "1" ]; then
    bash "$TU/sprawdz_ramke.sh" --bez-uslugi
else
    bash "$TU/sprawdz_ramke.sh"
fi
KOD_KONTROLI=$?
echo
if [ "$KOD" = "3" ]; then
    info "KONIEC: program skopiowany, ale BRAKUJE biblioteki sprzetu - patrz wiersze BRAK (kod 3)."
elif [ "$KOD_KONTROLI" != "0" ]; then
    info "KONIEC: instalacja zrobiona, ale kontrola pokazala braki - patrz wiersze BRAK w tabeli wyzej."
else
    info "KONIEC: instalacja zrobiona, kontrola bez brakow."
fi
exit "$KOD"
