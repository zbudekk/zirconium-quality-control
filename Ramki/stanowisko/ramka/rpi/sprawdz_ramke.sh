#!/bin/bash
# sprawdz_ramke.sh - kontrola instalacji programu ramki swietlnej na Raspberry Pi (E3-O4).
#
# [NIE SPRAWDZONE BEZ SPRZETU] - skrypt napisany wg kodu i README programu ramki. NIE byl uruchomiony na
# Raspberry Pi. Na komputerze PC sprawdzono tylko: skladnie (bash -n), konce linii i fragmenty Pythona.
#
# Uzycie (na Raspberry Pi):
#   sudo bash sprawdz_ramke.sh [--bez-uslugi]
#
#   --bez-uslugi   nie oceniaj uslugi (autostartu) ani odpowiedzi programu - do kontroli przed pierwszym
#                  uruchomieniem recznym.
#
# Wypisuje tabele: kazdy wiersz zaczyna sie od OK albo BRAK (albo POMIN), pod wierszem BRAK jest "-> co zrobic".
# Niczego nie zmienia. Klucza nie wypisuje. Kody wyjscia: 0 = bez brakow, 1 = sa braki, 2 = zle uruchomienie.

set -u

KATALOG_PROGRAMU="/opt/ramka"
PLIK_KONFIGURACJI="/etc/ramka/ramka.json"
PLIK_USLUGI="/etc/systemd/system/ramka.service"
KLUCZ_WZORU="ZMIEN-TEN-KLUCZ-skrypt-instalacji-wstawia-losowy"
PYTHON="/usr/bin/python3"
INSTRUKCJA="instrukcje/ramka_raspberry_pi.md"

BRAKI=0
# wiersz STAN NAZWA OPIS [CO_ZROBIC]
wiersz() {
    printf '%-5s %-14s %s\n' "$1" "$2" "$3"
    if [ "$1" = "BRAK" ]; then
        BRAKI=$((BRAKI + 1))
        if [ -n "${4:-}" ]; then
            printf '%-5s %-14s -> %s\n' "" "" "$4"
        fi
    fi
}

BEZ_USLUGI=0
while [ $# -gt 0 ]; do
    case "$1" in
        --bez-uslugi)
            BEZ_USLUGI=1
            shift
            ;;
        --help)
            echo "Uzycie: sudo bash sprawdz_ramke.sh [--bez-uslugi]"
            echo "Tabela OK / BRAK instalacji programu ramki. Opis: $INSTRUKCJA"
            exit 0
            ;;
        *)
            echo "BLAD: nieznana opcja: $1 (dozwolone: --bez-uslugi, --help)" >&2
            exit 2
            ;;
    esac
done

if [ "$(id -u)" != "0" ]; then
    echo "BLAD: potrzebne uprawnienia administratora (plik z kluczem czyta tylko root) - uruchom: sudo bash sprawdz_ramke.sh" >&2
    exit 2
fi

echo "Kontrola ramki ($(date '+%Y-%m-%d %H:%M:%S')). UWAGA: skrypt NIE SPRAWDZONE BEZ SPRZETU."
echo

# ---------------------------------------------------------------- Python
if [ -x "$PYTHON" ]; then
    WERSJA_PYTHONA="$("$PYTHON" -V 2>&1)"
    if "$PYTHON" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)'; then
        wiersz OK "Python" "$WERSJA_PYTHONA"
    else
        wiersz BRAK "Python" "$WERSJA_PYTHONA - za stary" "potrzebny Python 3.11 albo nowszy: wgraj na karte Raspberry Pi OS Bookworm albo nowszy"
    fi
else
    wiersz BRAK "Python" "nie ma $PYTHON" "wgraj na karte Raspberry Pi OS (64-bit, Lite) - krok 1 instrukcji"
    echo
    echo "WYNIK: bez Pythona dalsza kontrola nie ma sensu."
    exit 1
fi

# ---------------------------------------------------------------- biblioteki sprzetu
if "$PYTHON" -c "import gpiozero" >/dev/null 2>&1; then
    wiersz OK "gpiozero" "pakiet czujnikow plytek jest"
else
    wiersz BRAK "gpiozero" "brak pakietu czujnikow plytek" "sudo apt install python3-gpiozero"
fi
if "$PYTHON" -c "import evdev" >/dev/null 2>&1; then
    wiersz OK "evdev" "pakiet klawiatury jest"
else
    wiersz BRAK "evdev" "brak pakietu klawiatury (potrzebny ramce porannej)" "sudo apt install python3-evdev"
fi
if "$PYTHON" -c "import rgbmatrix" >/dev/null 2>&1; then
    wiersz OK "rgbmatrix" "biblioteka matrycy diod jest"
else
    wiersz BRAK "rgbmatrix" "brak biblioteki matrycy diod (rpi-rgb-led-matrix z powiazaniem Python)" "krok 'Biblioteka matrycy' z instrukcji $INSTRUKCJA"
fi

# ---------------------------------------------------------------- program
PROGRAM_JEST=0
if [ -f "$KATALOG_PROGRAMU/ramka/__main__.py" ]; then
    WERSJA_PROGRAMU="$(cd "$KATALOG_PROGRAMU" && "$PYTHON" -c 'import ramka; print(ramka.WERSJA)' 2>/dev/null)"
    if [ -n "$WERSJA_PROGRAMU" ]; then
        wiersz OK "program" "program ramki $WERSJA_PROGRAMU w $KATALOG_PROGRAMU/ramka"
        PROGRAM_JEST=1
    else
        wiersz BRAK "program" "katalog $KATALOG_PROGRAMU/ramka jest, ale program sie nie wczytuje" "skopiuj katalog 'ramka' jeszcze raz i uruchom: sudo bash zainstaluj_ramke.sh"
    fi
else
    wiersz BRAK "program" "nie ma $KATALOG_PROGRAMU/ramka" "uruchom: sudo bash zainstaluj_ramke.sh"
fi

# ---------------------------------------------------------------- plik konfiguracji
HOST=""
PORT=""
KONFIGURACJA_DOBRA=0
if [ ! -f "$PLIK_KONFIGURACJI" ]; then
    wiersz BRAK "konfiguracja" "nie ma pliku $PLIK_KONFIGURACJI" "uruchom: sudo bash zainstaluj_ramke.sh"
elif [ "$PROGRAM_JEST" != "1" ]; then
    wiersz BRAK "konfiguracja" "plik $PLIK_KONFIGURACJI jest, ale bez programu nie da sie go sprawdzic" "najpierw wiersz 'program'"
else
    # argumenty: plik konfiguracji, katalog nad pakietem ramka, klucz zastepczy ze wzoru
    # wyjscie: wiersz 1 = opis (bez klucza), wiersz 2 = co zrobic (pusty = nic), wiersz 3 = host i port
    WYNIK="$("$PYTHON" - "$PLIK_KONFIGURACJI" "$KATALOG_PROGRAMU" "$KLUCZ_WZORU" <<'PY_SPRAWDZ_KONFIGURACJE'
import sys

plik, katalog, klucz_wzoru = sys.argv[1:4]
sys.path.insert(0, katalog)
try:
    from ramka.program import wczytaj_konfiguracje
    konf = wczytaj_konfiguracje(plik)
    if konf.rola not in ("W", "P"):
        raise ValueError("rola ma byc W albo P")
    if not isinstance(konf.port, int) or not 1 <= konf.port <= 65535:
        raise ValueError("port ma byc liczba 1-65535")
    if not isinstance(konf.host, str) or " " in konf.host:
        raise ValueError("host ma byc adresem bez odstepow")
except Exception as e:  # kazdy blad pliku = jeden wiersz dla czlowieka, bez sladu wyjatku
    print("program nie przyjmuje pliku: " + type(e).__name__ + ": " + " ".join(str(e).split()))
    print("popraw plik (sudo nano " + plik + ") albo usun go i uruchom ponownie: sudo bash zainstaluj_ramke.sh")
    print("- -")
    sys.exit(1)
opis = "rola %s, sprzet %s, adres nasluchu %s, port %d, klucz %s" % (
    konf.rola, konf.sprzet, konf.host, konf.port, "jest (%d znakow)" % len(konf.klucz) if konf.klucz else "PUSTY")
rady = []
if konf.host in ("127.0.0.1", "localhost", ""):
    rady.append('adres nasluchu %s: laptop NIE zobaczy ramki - wpisz "host": "0.0.0.0" albo adres ramki w sieci' % (konf.host or "pusty"))
if not konf.klucz:
    rady.append('brak klucza: kazde urzadzenie w sieci moze sterowac ramka - wpisz "klucz" (16-256 znakow, ten sam co w ustawieniach laptopa)')
elif konf.klucz == klucz_wzoru:
    rady.append("klucz jest kluczem zastepczym ze wzoru (znany kazdemu) - wpisz wlasny albo usun plik i uruchom ponownie zainstaluj_ramke.sh")
print(opis)
print("; ".join(rady))
print("%s %d" % (konf.host, konf.port))
sys.exit(1 if rady else 0)
PY_SPRAWDZ_KONFIGURACJE
    )"
    KOD_KONFIGURACJI=$?
    OPIS="$(printf '%s\n' "$WYNIK" | sed -n '1p')"
    RADA="$(printf '%s\n' "$WYNIK" | sed -n '2p')"
    read -r HOST PORT <<<"$(printf '%s\n' "$WYNIK" | sed -n '3p')"
    if [ "$KOD_KONFIGURACJI" = "0" ]; then
        wiersz OK "konfiguracja" "$OPIS"
        KONFIGURACJA_DOBRA=1
    else
        wiersz BRAK "konfiguracja" "$OPIS" "${RADA:-sprawdz plik: sudo nano $PLIK_KONFIGURACJI}"
        if [ "$HOST" = "-" ]; then
            HOST=""
            PORT=""
        else
            KONFIGURACJA_DOBRA=1
        fi
    fi
    PRAWA="$(stat -c '%a %U' "$PLIK_KONFIGURACJI" 2>/dev/null)"
    if [ "$PRAWA" = "600 root" ]; then
        wiersz OK "prawa pliku" "plik z kluczem czyta tylko administrator (600 root)"
    else
        wiersz BRAK "prawa pliku" "plik z kluczem ma prawa '$PRAWA', a ma miec '600 root'" "sudo chown root:root $PLIK_KONFIGURACJI && sudo chmod 600 $PLIK_KONFIGURACJI"
    fi
fi

# ---------------------------------------------------------------- config.txt i cmdline.txt
KATALOG_STARTU=""
for KANDYDAT in /boot/firmware /boot; do
    if [ -f "$KANDYDAT/config.txt" ]; then
        KATALOG_STARTU="$KANDYDAT"
        break
    fi
done
if [ -z "$KATALOG_STARTU" ]; then
    wiersz BRAK "config.txt" "nie znaleziono pliku config.txt w /boot/firmware ani w /boot" "sprawdz, gdzie system trzyma config.txt (krok 3 instrukcji)"
else
    if grep -Eq '^[[:space:]]*dtparam=audio=off' "$KATALOG_STARTU/config.txt" && ! grep -Eq '^[[:space:]]*dtparam=audio=on' "$KATALOG_STARTU/config.txt"; then
        wiersz OK "dzwiek" "wylaczony w $KATALOG_STARTU/config.txt (dtparam=audio=off)"
    else
        wiersz BRAK "dzwiek" "dzwiek nie jest wylaczony w $KATALOG_STARTU/config.txt (psuje obraz matrycy)" "zmien wiersz dtparam=audio=on na dtparam=audio=off, potem: sudo reboot"
    fi
    if grep -Eq '^[[:space:]]*dtparam=spi=on' "$KATALOG_STARTU/config.txt"; then
        wiersz BRAK "SPI" "SPI wlaczone w $KATALOG_STARTU/config.txt (zajmuje pin czujnika plytek)" "zmien wiersz dtparam=spi=on na dtparam=spi=off, potem: sudo reboot"
    else
        wiersz OK "SPI" "nie jest wlaczone w $KATALOG_STARTU/config.txt"
    fi
    if [ -f "$KATALOG_STARTU/cmdline.txt" ] && grep -q 'isolcpus=3' "$KATALOG_STARTU/cmdline.txt"; then
        wiersz OK "cmdline.txt" "isolcpus=3 jest w $KATALOG_STARTU/cmdline.txt"
    else
        wiersz BRAK "cmdline.txt" "brak isolcpus=3 w $KATALOG_STARTU/cmdline.txt (obraz matrycy moze migotac)" "dopisz na koncu JEDYNEGO wiersza pliku: spacja i isolcpus=3, potem: sudo reboot"
    fi
fi

# ---------------------------------------------------------------- usluga
if [ "$BEZ_USLUGI" = "1" ]; then
    wiersz POMIN "usluga" "nie oceniana (--bez-uslugi)"
elif ! command -v systemctl >/dev/null 2>&1; then
    wiersz BRAK "usluga" "nie ma polecenia systemctl" "to nie jest Raspberry Pi OS z systemd - wgraj wlasciwy system"
elif [ ! -f "$PLIK_USLUGI" ]; then
    wiersz BRAK "usluga" "nie ma pliku $PLIK_USLUGI" "uruchom: sudo bash zainstaluj_ramke.sh"
else
    WLACZONA="$(systemctl is-enabled ramka.service 2>/dev/null)"
    DZIALA="$(systemctl is-active ramka.service 2>/dev/null)"
    if [ "$WLACZONA" = "enabled" ]; then
        wiersz OK "autostart" "usluga startuje sama po wlaczeniu zasilania"
    else
        wiersz BRAK "autostart" "usluga nie jest wlaczona (stan: ${WLACZONA:-nieznany})" "sudo systemctl enable ramka"
    fi
    if [ "$DZIALA" = "active" ]; then
        wiersz OK "usluga" "program ramki dziala jako usluga"
    else
        wiersz BRAK "usluga" "usluga nie dziala (stan: ${DZIALA:-nieznany})" "sudo systemctl restart ramka ; logi: sudo journalctl -u ramka -n 30 --no-pager"
    fi
fi

# ---------------------------------------------------------------- siec
NAZWA="$(hostname 2>/dev/null)"
ADRESY="$(hostname -I 2>/dev/null | xargs)"
if [ -n "$ADRESY" ]; then
    wiersz OK "adres IP" "nazwa $NAZWA, adresy: $ADRESY"
else
    wiersz BRAK "adres IP" "nazwa $NAZWA, ramka nie ma adresu w sieci" "sprawdz Wi-Fi: sudo nmtui (albo ustawienia karty w Raspberry Pi Imager - krok 1 instrukcji)"
fi

# ---------------------------------------------------------------- port: czy program odpowiada
if [ "$BEZ_USLUGI" = "1" ]; then
    wiersz POMIN "port" "nie oceniany (--bez-uslugi)"
elif [ "$KONFIGURACJA_DOBRA" != "1" ] || [ -z "$PORT" ]; then
    wiersz BRAK "port" "nie znam portu - plik konfiguracji nieczytelny" "najpierw wiersz 'konfiguracja'"
else
    # argument: plik konfiguracji; wyjscie: jeden wiersz opisu
    ODPOWIEDZ="$("$PYTHON" - "$PLIK_KONFIGURACJI" <<'PY_STAN'
import http.client
import json
import sys

with open(sys.argv[1], encoding="utf-8") as f:
    konf = json.load(f)
host = konf.get("host", "127.0.0.1")
port = int(konf.get("port", 8765))
klucz = konf.get("klucz", "")
adres = "127.0.0.1" if host in ("0.0.0.0", "", "localhost") else host
naglowki = {"X-Ramka-Klucz": klucz} if klucz else {}
try:
    polaczenie = http.client.HTTPConnection(adres, port, timeout=5)
    polaczenie.request("GET", "/stan", headers=naglowki)
    odpowiedz = polaczenie.getresponse()
    tresc = odpowiedz.read()
    polaczenie.close()
except (OSError, http.client.HTTPException) as e:
    print("nikt nie odpowiada na %s:%d (%s)" % (adres, port, type(e).__name__))
    sys.exit(1)
if odpowiedz.status != 200:
    print("program na %s:%d odpowiada kodem %d zamiast 200" % (adres, port, odpowiedz.status))
    sys.exit(1)
try:
    stan = json.loads(tresc.decode("utf-8"))
    opis = "port %d: odpowiada program ramki %s, rola %s, plytka %s" % (port, stan["program"], stan["rola"], stan["plytka"])
    awaria = bool(stan.get("blad_sprzetu"))
except (ValueError, KeyError, TypeError):
    print("na %s:%d odpowiada cos innego niz program ramki" % (adres, port))
    sys.exit(1)
if awaria:
    print(opis + " - ale program zglasza AWARIE SPRZETU")
    sys.exit(1)
print(opis)
PY_STAN
    )"
    if [ $? = 0 ]; then
        wiersz OK "port" "$ODPOWIEDZ"
    else
        wiersz BRAK "port" "$ODPOWIEDZ" "sudo systemctl restart ramka ; logi: sudo journalctl -u ramka -n 30 --no-pager"
    fi
fi

# ---------------------------------------------------------------- wynik
echo
if [ "$BRAKI" = "0" ]; then
    echo "WYNIK: bez brakow."
else
    echo "WYNIK: wierszy BRAK: $BRAKI - zrob to, co stoi po strzalce '->', i uruchom kontrole jeszcze raz."
fi
if [ -n "$PORT" ] && [ -n "$ADRESY" ]; then
    echo "Z laptopa (ta sama siec): http://$NAZWA.local:$PORT/stan albo http://${ADRESY%% *}:$PORT/stan"
    echo "(z kluczem w konfiguracji przegladarka pokaze blad 401 - to tez znak, ze ramka dziala; pelna kontrola: instrukcja, krok 9)"
fi
[ "$BRAKI" = "0" ]
