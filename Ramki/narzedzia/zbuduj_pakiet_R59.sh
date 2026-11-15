#!/bin/bash
# Buduje pakiet R59 (R59‑K): nowy układ gniazd płytek — wieczorna 18 gniazd + 1 rynienka (6 × ø12, 12 × ø15), poranna 23 + 1 (20 × ø12,5, 3 × ø15),
# płytki okrągłe n8 / n9 z tymi samymi gniazdami. Zmieniły się TYLKO pliki płytek: te same nazwy co w pakietach R54–R57, nowe SHA‑256.
# Na wzór zbuduj_pakiet_R57.sh; różnice:
#  - dokumenty 01–04 z sufiksem _<data>_R59; 02_Druk_drukarnia_PA12: 8 plików płytek w nowym układzie, arkusz z narzedzia/arkusz_zamowienia_R59.py;
#    03_Druk_wlasny: …_n1_v2_TEST_SKANERA.stl = kopia NOWEGO n1 (ta sama reguła co w R57);
#  - 04_Model_i_animacje: wyniki_model_R59 (ramka_3d_v3_R59.html, animacja_ramki_R59.html — animacja pokazuje układ gniazd, 12 JPG) + 3 rendery Blendera;
#  - 05_Zrodla: + R59_wdrozenie_zmiany.md, R59_propozycja_ukladu.md, raport wykonawcy R59 iter2, raport recenzenta R59 iter1, raport recenzji PR runda 1,
#    uklad_kolo_R59.js i weryfikuj_uklad_R59.js (zamiast …_R54.js), arkusz_zamowienia_R59.py (zamiast …_R57.py), bazowe STL wszystkich 4 typów płytek
#    (R57: tylko 2 okrągłe), opis programu stanowiska i jego raport R59 (dwa układy płytek, strażnik układu);
#  - pakiet powstaje w katalogu roboczym obok celu i zastępuje poprzedni dopiero po przejściu WSZYSTKICH kontroli (R57: rm -rf na początku);
#  - skrypt robi też pliki na Dysk (w R56 / R57 robione ręcznie): 3 ZIP‑y, SHA256SUMS, INSTRUKCJA_PAKIET, DO_WGRANIA_NA_DRIVE, 3 PDF;
#    ZIP‑y modułem zipfile Pythona (stała kolejność i czas wpisów — ten sam Python daje bajtowo te same ZIP‑y);
#  - tryb próbny (--proba <katalog>): pisze WYŁĄCZNIE do <katalog>, dopuszcza PDF sprzed R59 (tylko do sprawdzenia mechaniki — nie do wgrania).
# Kontrole (niezgodność = stop; poprzedni pakiet i katalog do wgrania zostają nietknięte):
#   1. przypięte SHA‑256 12 STL płytek i 4 JSON układu = tabela w R59_wdrozenie_zmiany.md = pliki w wyniki_v2/;
#   2. 9 plików niepłytkowych bajtowo jak w SHA256SUMS_2026-11-02_R57.txt (źródła i pakiet); wkładka = f4196fbc… (wariant z innym znakiem
#      zera normalnych, K‑59 = stop z podpowiedzią, skąd przywrócić plik zweryfikowany);
#   3. 3 PDF: istnieją; w trybie właściwym nie są plikami z pakietu R57, nie są starsze niż ich .md, a ich tekst (pypdf) zawiera „R59”
#      i „23 gniazda” (nowy układ płytki porannej); kopia z git archive ma równe czasy plików — wtedy rozstrzyga treść;
#   4. model 3D zawiera płytki n1 / n4 o przypiętych SHA i żadnego pliku starego układu;
#   5. w pakiecie: każdy plik płytki i JSON układu ma przypiętą sumę; żaden plik nie ma sumy pliku płytki / JSON układu sprzed R59;
#      liczba plików, nazwy tylko ASCII bez spacji; sha256sum -c;
#   6. ZIP‑y: każdy < 10 MB, test CRC, każdy plik pakietu w dokładnie jednym ZIP‑ie, sumy plików w ZIP‑ach = SHA256SUMS;
#   7. katalog do wgrania: istniejące pliki *_<data>_R59* nadpisuje tylko z --nadpisz; żaden inny plik nie może się zmienić ani zniknąć.
# Uruchom z folderu Ramki:
#   bash narzedzia/zbuduj_pakiet_R59.sh [--nadpisz] [katalog_pakietu]   właściwy pakiet: Ramki_pakiet/ (albo katalog_pakietu) + ../Ramki_do_wgrania/
#   bash narzedzia/zbuduj_pakiet_R59.sh --proba <katalog> [--nadpisz]   przebieg próbny: <katalog>/Ramki_pakiet + <katalog>/Ramki_do_wgrania
# Zmienne: DATA=RRRR-MM-DD (domyślnie dziś = dzień budowy), PY=<python.exe> (domyślnie pierwszy z: py -3, python3, python, znane ścieżki PC / MSI —
#   z pierwszeństwem dla tego, który ma pypdf); PROBA=1 i NADPISZ=1 działają jak przełączniki. Ścieżki względne liczą się od folderu Ramki.
# Kopia pakietu R57 sprzed przebudowy: archiwum/Ramki_pakiet_przed_R59_<data>/ — robi ją ten skrypt (tylko tryb właściwy, cel = Ramki_pakiet).
set -euo pipefail
SKRYPT="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
cd "$(dirname "$SKRYPT")/.."

R=R59
DATA="${DATA:-$(date +%F)}"   # data pakietu = dzień właściwej budowy; inna: DATA=2026-11-16 bash narzedzia/zbuduj_pakiet_R59.sh
PROBA="${PROBA:-0}"
NADPISZ="${NADPISZ:-0}"
LIMIT_ZIP=10000000            # każdy ZIP < 10 MB (ostrożnie: 10 000 000 bajtów)
LICZBA_PLIKOW=81              # pliki pakietu bez pliku sum (pakiet R57: 63)
SUMY_R57_NAZWA=SHA256SUMS_2026-11-02_R57.txt
WGRANIE_REPO=../Ramki_do_wgrania
FRAZA_PDF="23 gniazda"        # liczba gniazd płytki porannej po R59: jest w każdym z trzech .md, więc musi być w tekście każdego PDF

# Przypięte SHA‑256 plików płytek i JSON układu: R59_wdrozenie_zmiany.md pkt 0 (= raport recenzenta R59 iter1 pkt 1, 12 / 12 i 4 / 4)
SHA_PLYTEK="ramka_plytka_wieczorna_v2.stl 604ef8f2079184460c3e059edde4849e9feeefeab39a755c18d0079ea1e561a9
ramka_plytka_wieczorna_n1_v2.stl 3b0db5452a0cd9533464772c10b67c05fa7a006fcdb3d140a74af275e79946f7
ramka_plytka_wieczorna_n2_v2.stl b87026134b25cf32a84a231b73d5c4eb9fde4dfeb5b16b627cf09ccc3f29c999
ramka_plytka_wieczorna_n3_v2.stl 59e615d596771c6c0351284c710e94e406a965afef423ffeae5cd18ffa2c4dd3
ramka_plytka_poranna_v2.stl a306032651bbdb0c77693aa27f6314e8c5ede874d1e99b1fa73e158a1a83bc9f
ramka_plytka_poranna_n4_v2.stl 20f15f2214f6c9a9baf2b4701e7f99bfbc5f739b6379398294e9f931b8763237
ramka_plytka_poranna_n5_v2.stl a275775b9c9b5ddd015b68659f213505bdd28b9476cad5e13405bef2df5b64d1
ramka_plytka_poranna_n6_v2.stl c44be370c8b9ad2b70f9e486c3f6f9d2b227b91f2a6544bfe14bf7e66bd65b21
ramka_plytka_okragla_wieczorna_v2.stl aad8033e6c1d1f34b43825861d18e82b45599a76ebb453c294400a7713ebbd83
ramka_plytka_okragla_wieczorna_n8_v2.stl d5591f652ea1b6b23825abb5ad05ac12b78d17f6abb52946bd1a010ef5e4ff54
ramka_plytka_okragla_poranna_v2.stl e35835d7618e6665fdda84cbe2d65a3c7b46d7f9cef1e99141b42af2eb9e22c7
ramka_plytka_okragla_poranna_n9_v2.stl f9444e6f14e37d9d0bcc8ae84cfec5249146bce20420c53a86a73965727fd4c4"
SHA_JSON="uklad_gniazd_wieczorna.json 7ae07ba861950724cf68ce9de0b45f3a05436089df8f73b3b4fc07bf2cc05869
uklad_gniazd_poranna.json 46e474b759c4b78b7975fc8c5580c9916a4cc64c6a88cd4711b2207e3978b98b
uklad_gniazd_okragla_wieczorna.json c07791f4bb976be2ad5eddaaeefe011b2384ea71e3fabd25cf55da690eb14a33
uklad_gniazd_okragla_poranna.json b943e6c5dd54a8b3b35974908a3910bd654062bb659284a649ee68679174268e"
SHA_WKLADKI=f4196fbc640450998634f50caa86051f89df2cbb2c218e317f5c2b193e3ef92b
PLYTKI_DO_DRUKU="ramka_plytka_wieczorna_n1_v2 ramka_plytka_wieczorna_n2_v2 ramka_plytka_wieczorna_n3_v2 ramka_plytka_poranna_n4_v2 ramka_plytka_poranna_n5_v2 ramka_plytka_poranna_n6_v2 ramka_plytka_okragla_wieczorna_n8_v2 ramka_plytka_okragla_poranna_n9_v2"
PLYTKI_BAZOWE="ramka_plytka_wieczorna_v2 ramka_plytka_poranna_v2 ramka_plytka_okragla_wieczorna_v2 ramka_plytka_okragla_poranna_v2"
# dokument źródłowy (bez rozszerzenia) | nazwa w pakiecie (bez sufiksu daty)
PDFY=("Stanowisko kontroli cyrkonii — plan wdrozenia v2|01_Plan_wdrozenia_v2" "Zakupy i druk — stanowisko kontroli cyrkonii|02_Zakupy_i_druk" "Budowa ramki — decyzje i zamienniki|03_Budowa_ramki_decyzje_i_zamienniki")

blad() { echo "BLAD: $*" >&2; exit 1; }
uwaga() { echo "UWAGA: $*"; }
sha() { sha256sum -b "$1" | cut -c1-64; }
suma_plytki() { awk -v p="$1" '$1==p{print $2}' <<< "$SHA_PLYTEK"; }
tys() { echo "$1" | sed ':a;s/^\([0-9]\+\)\([0-9]\{3\}\)/\1 \2/;ta'; }   # 4516613 -> 4 516 613

CEL=""
while [ $# -gt 0 ]; do
  case "$1" in
    --proba) PROBA=1;;
    --nadpisz) NADPISZ=1;;
    -h|--help) sed -n '2,/^set -euo pipefail/p' "$SKRYPT" | sed '$d'; exit 0;;
    -*) blad "nieznany przelacznik $1 (znane: --proba, --nadpisz)";;
    *) [ -z "$CEL" ] || blad "podano dwa katalogi docelowe: $CEL i $1"; CEL="$1";;
  esac
  shift
done
[[ "$DATA" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]] || blad "DATA ma byc w postaci RRRR-MM-DD, jest: $DATA"

if [ "$PROBA" = 1 ]; then
  [ -n "$CEL" ] || blad "przebieg probny wymaga katalogu docelowego: --proba <katalog>"
  case "$(realpath -m "$CEL")/" in
    "$(realpath -m Ramki_pakiet)/"*|"$(realpath -m "$WGRANIE_REPO")/"*|"$(realpath -m archiwum)/"*) blad "przebieg probny nie moze pisac do Ramki_pakiet, Ramki_do_wgrania ani archiwum";;
  esac
  D="${CEL%/}/Ramki_pakiet"; W="${CEL%/}/Ramki_do_wgrania"; TRYB=PROBNY
else
  D="${CEL:-Ramki_pakiet}"; D="${D%/}"; W="$WGRANIE_REPO"; TRYB=WLASCIWY
fi
T="$D.budowa_$R"              # katalog roboczy pakietu (znika po udanej budowie)
TW="$D.budowa_${R}_wgranie"   # katalog roboczy plików na Dysk
SUMY="SHA256SUMS_${DATA}_${R}.txt"
KATALOG_ZIP="Ramki_pakiet_${DATA}_${R}"
ZIP1="${KATALOG_ZIP}_cz1_dokumenty_druk.zip"; ZIP2="${KATALOG_ZIP}_cz2_model.zip"; ZIP3="${KATALOG_ZIP}_cz3_zrodla.zip"
INSTR="INSTRUKCJA_PAKIET_${DATA}_${R}.md"; LISTA="DO_WGRANIA_NA_DRIVE_${DATA}_${R}.md"
NAZWY_DYSK=("$ZIP1" "$ZIP2" "$ZIP3" "$SUMY" "$INSTR")
for p in "${PDFY[@]}"; do NAZWY_DYSK+=("${p##*|}_${DATA}_${R}.pdf"); done
NAZWY_W=("${NAZWY_DYSK[@]}" "$LISTA")   # wszystko, co ten skrypt pisze do katalogu do wgrania (9 plików)

# --- Python (ZIP‑y, arkusz zamówienia, tekst PDF)
PYCMD=(); PYPDF=0
if [ -n "${PY:-}" ]; then KAND=("$PY"); else KAND=("py -3" python3 python "<PC>/AppData/Local/Programs/Python/Python312/python.exe" "/c/Program Files/Python312/python.exe"); fi
for wymog in pypdf dowolny; do
  for k in "${KAND[@]}"; do
    if [ "$k" = "py -3" ]; then c=(py -3); else c=("$k"); fi
    "${c[@]}" -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" >/dev/null 2>&1 || continue
    if [ "$wymog" = pypdf ]; then "${c[@]}" -c "import pypdf" >/dev/null 2>&1 || continue; PYPDF=1; fi
    PYCMD=("${c[@]}" -X utf8); break 2
  done
done
[ "${#PYCMD[@]}" -gt 0 ] || blad "brak Pythona 3 - podaj interpreter: PY=<sciezka do python.exe> bash narzedzia/zbuduj_pakiet_${R}.sh"

py_narzedzie() { "${PYCMD[@]}" - "$@" <<'PYEOF'
import hashlib, os, sys, zipfile
sys.stdout.reconfigure(encoding="utf-8", newline="\n")

def blad(tekst):
    print("BLAD: " + tekst)
    sys.exit(1)

def pdf(sciezka, fraza):
    # wypisuje "<stron> <wystapien R59> <wystapien frazy>"; kod 3 = w tekscie brak R59 albo frazy nowego ukladu
    import pypdf
    czytnik = pypdf.PdfReader(sciezka)
    tekst = " ".join("\n".join((s.extract_text() or "") for s in czytnik.pages).split())
    a, b = tekst.count("R59"), tekst.count(fraza)
    print("%d %d %d" % (len(czytnik.pages), a, b))
    sys.exit(0 if a and b else 3)

def zbuduj(pakiet, katalog, wyjscie, data, lista):
    # ZIP powtarzalny: kolejnosc z listy, staly czas wpisow (poludnie dnia pakietu), stale atrybuty
    r, m, d = (int(t) for t in data.split("-"))
    with open(lista, encoding="utf-8") as f:
        nazwy = [w.strip() for w in f if w.strip()]
    with zipfile.ZipFile(wyjscie, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for n in nazwy:
            wpis = zipfile.ZipInfo(katalog + "/" + n, date_time=(r, m, d, 12, 0, 0))
            wpis.compress_type = zipfile.ZIP_DEFLATED
            wpis.create_system = 0
            wpis.external_attr = 0
            with open(os.path.join(pakiet, n), "rb") as f:
                z.writestr(wpis, f.read(), compresslevel=9)
    print("  %s: %d plikow" % (os.path.basename(wyjscie), len(nazwy)))

def sprawdz(plik_sum, katalog, zipy):
    # kazdy plik z sum (i sam plik sum) w dokladnie jednym ZIP-ie, CRC dobre, SHA-256 = plik sum
    nazwa_sum = os.path.basename(plik_sum)
    oczekiwane = {}
    with open(plik_sum, encoding="utf-8") as f:
        for w in f:
            w = w.rstrip("\r\n")
            if w:
                oczekiwane[w[66:]] = w[:64]
    with open(plik_sum, "rb") as f:
        bajty_sum = f.read()
    widziane = {}
    for sciezka in zipy:
        with zipfile.ZipFile(sciezka) as z:
            zly = z.testzip()
            if zly:
                blad("%s: blad CRC w %s" % (os.path.basename(sciezka), zly))
            for wpis in z.infolist():
                if not wpis.filename.startswith(katalog + "/"):
                    blad("%s: wpis poza katalogiem %s: %s" % (os.path.basename(sciezka), katalog, wpis.filename))
                n = wpis.filename[len(katalog) + 1:]
                if n in widziane:
                    blad("%s jest w dwoch ZIP-ach" % n)
                widziane[n] = sciezka
                dane = z.read(wpis)
                if n == nazwa_sum:
                    if dane != bajty_sum:
                        blad("plik sum w ZIP-ie rozni sie od %s" % nazwa_sum)
                elif n not in oczekiwane:
                    blad("%s: plik spoza %s" % (n, nazwa_sum))
                elif hashlib.sha256(dane).hexdigest() != oczekiwane[n]:
                    blad("%s: SHA-256 w ZIP-ie inne niz w %s" % (n, nazwa_sum))
    brak = sorted((set(oczekiwane) | {nazwa_sum}) - set(widziane))
    if brak:
        blad("brak w ZIP-ach: " + ", ".join(brak))
    print("  po zlozeniu %d ZIP-ow: %d z %d plikow = %s, plik sum identyczny, kazdy plik w dokladnie jednym ZIP-ie"
          % (len(zipy), len(oczekiwane), len(oczekiwane), nazwa_sum))

polecenie = sys.argv[1]
if polecenie == "pdf":
    pdf(sys.argv[2], sys.argv[3])
elif polecenie == "zip":
    zbuduj(*sys.argv[2:7])
elif polecenie == "sprawdz":
    sprawdz(sys.argv[2], sys.argv[3], sys.argv[4:])
else:
    blad("nieznane polecenie " + polecenie)
PYEOF
}

echo "== zbuduj_pakiet_${R}.sh: przebieg $TRYB, data $DATA"
echo "   pakiet: $D   pliki na Dysk: $W   Python: ${PYCMD[*]} (pypdf: $PYPDF)"

# --- 0. Cele: nic nie kasuję na ślepo, nic starego nie nadpisuję
if [ -e "$D" ]; then
  [ -d "$D" ] || blad "$D istnieje i nie jest katalogiem"
  if [ -n "$(ls -A "$D")" ]; then
    { [ -f "$D/README.txt" ] && ls "$D"/SHA256SUMS_*.txt >/dev/null 2>&1; } || blad "katalog $D nie jest pusty i nie wyglada na pakiet (brak README.txt albo SHA256SUMS_*.txt) - nie kasuje"
  fi
fi
if [ "$PROBA" = 1 ]; then mkdir -p "$W"; else [ -d "$W" ] || blad "brak katalogu $W"; fi
ISTN=()
for n in "${NAZWY_W[@]}"; do if [ -e "$W/$n" ]; then ISTN+=("$n"); fi; done
if [ "${#ISTN[@]}" -gt 0 ] && [ "$NADPISZ" != 1 ]; then blad "w $W juz sa pliki tego pakietu (${ISTN[*]}) - nie nadpisuje; swiadoma przebudowa: --nadpisz"; fi
INNE_R59=$(cd "$W" && find . -type f -name "*_${R}*" ! -name "*_${DATA}_${R}*" | sed 's|^\./||' | LC_ALL=C sort | tr '\n' ' ')
[ -z "$INNE_R59" ] || uwaga "w $W sa pliki $R z inna data (zostaja nietkniete): $INNE_R59"
migawka() {  # sumy plików katalogu do wgrania, których ten skrypt nie pisze
  ( cd "$W" && find . -type f | sed 's|^\./||' | LC_ALL=C sort | while IFS= read -r n; do
      case " ${NAZWY_W[*]} " in *" $n "*) ;; *) sha256sum -b "$n";; esac
    done )
}
PRZED=$(migawka)

SPRZATAJ=1
trap 'if [ "$SPRZATAJ" = 1 ]; then rm -rf "$T" "$TW"; fi' EXIT
rm -rf "$T" "$TW"
mkdir -p "$T/01_Dokumenty" "$T/02_Druk_drukarnia_PA12" "$T/03_Druk_wlasny/PETG_FDM" "$T/04_Model_i_animacje/rendery" "$T/05_Zrodla" "$TW"

# --- 1. Źródła: sumy przypięte = dokument wdrożenia = pliki w wyniki_v2
echo "== 1. Zrodla"
SUMY_R57=""
for k in "$WGRANIE_REPO/$SUMY_R57_NAZWA" "Ramki_pakiet/$SUMY_R57_NAZWA" archiwum/Ramki_pakiet_przed_${R}_*/"$SUMY_R57_NAZWA"; do
  if [ -f "$k" ]; then SUMY_R57="$k"; break; fi
done
[ -n "$SUMY_R57" ] || blad "brak $SUMY_R57_NAZWA (szukane w $WGRANIE_REPO, Ramki_pakiet, archiwum/Ramki_pakiet_przed_${R}_*)"
N=0
while read -r plik suma; do
  grep -F "\`$plik\`" R59_wdrozenie_zmiany.md | grep -F "$suma" >/dev/null || blad "$plik: przypieta suma ${suma:0:12}... nie zgadza sie z tabela w R59_wdrozenie_zmiany.md"
  case "$plik" in *.stl) zr="wyniki_v2/stl/$plik";; *) zr="wyniki_v2/json/$plik";; esac
  [ -f "$zr" ] || blad "brak $zr (STL nie sa w gicie: skopiuj 21 plikow do wyniki_v2/stl)"
  [ "$(sha "$zr")" = "$suma" ] || blad "$zr ma inne SHA-256 niz zatwierdzone (${suma:0:12}...)"
  N=$((N+1))
done <<< "$SHA_PLYTEK
$SHA_JSON"
[ "$N" = 16 ] || blad "lista przypietych sum: oczekiwane 16 pozycji, jest $N"
echo "  12 z 12 STL plytek i 4 z 4 JSON ukladu: suma przypieta = R59_wdrozenie_zmiany.md = plik w wyniki_v2"

# wkładka: do zamówienia idzie plik zweryfikowany w R53/R54 (f4196fbc…). Znana pułapka (K‑59): po przebiegu generatora plik miewa inny znak zera
# normalnych (siatka identyczna, inna suma). W R57 skrypt pakietu sam brał wtedy plik z archiwum; tu to STOP z podpowiedzią, bo arkusz zamówienia R59
# porównuje wyniki_v2/stl z raportem generatora i z takim wariantem i tak by się zatrzymał — plik trzeba przywrócić w wyniki_v2/stl.
[ -f wyniki_v2/stl/ramka_wkladka_v2.stl ] || blad "brak wyniki_v2/stl/ramka_wkladka_v2.stl (STL nie sa w gicie: skopiuj 21 plikow do wyniki_v2/stl)"
if [ "$(sha wyniki_v2/stl/ramka_wkladka_v2.stl)" != "$SHA_WKLADKI" ]; then
  DOBRA=""
  for k in Ramki_pakiet/02_Druk_drukarnia_PA12/ramka_wkladka_v2.stl archiwum/Ramki_pakiet_przed_${R}_*/02_Druk_drukarnia_PA12/ramka_wkladka_v2.stl archiwum/Ramki_pakiet_przed_R55_2026-11-01/02_Druk_drukarnia_PA12/ramka_wkladka_v2.stl archiwum/wyniki_v2_przed_R59_2026-11-14/stl/ramka_wkladka_v2.stl; do
    if [ -f "$k" ] && [ "$(sha "$k")" = "$SHA_WKLADKI" ]; then DOBRA="$k"; break; fi
  done
  blad "wyniki_v2/stl/ramka_wkladka_v2.stl nie ma sumy f4196fbc... (znana pulapka: inny znak zera normalnych po przebiegu generatora). Przywroc plik zweryfikowany: cp ${DOBRA:-<plik o sumie f4196fbc z archiwum>} wyniki_v2/stl/ramka_wkladka_v2.stl"
fi

# 9 plików niepłytkowych: źródło bajtowo jak w pakiecie R57
N=0
while read -r suma sciezka; do
  case "$sciezka" in *plytka*) continue;; *.stl) ;; *) continue;; esac
  plik="${sciezka##*/}"; zr="wyniki_v2/stl/$plik"
  [ -f "$zr" ] || blad "brak $zr"
  [ "$(sha "$zr")" = "$suma" ] || blad "$zr rozni sie od pliku z pakietu R57 (${suma:0:12}...) - pliki nieplytkowe maja zostac bajtowo bez zmian"
  N=$((N+1))
done < "$SUMY_R57"
[ "$N" = 9 ] || blad "$SUMY_R57: oczekiwane 9 plikow nieplytkowych STL, jest $N"
echo "  9 z 9 plikow nieplytkowych (korpus W, korpus P, blat, wkladka, pokrywka, tulejka DC, 3 podkladki) bajtowo jak w $SUMY_R57_NAZWA"

# sumy plików płytek i JSON układu sprzed R59 — żadna nie może trafić do nowego pakietu ani modelu
STARE="$TW/sumy_sprzed_R59.txt"
{ awk '$2 ~ /plytka.*\.stl$/ || $2 ~ /uklad_gniazd_.*\.json$/ {print $1}' "$SUMY_R57"
  if [ -f archiwum/wyniki_v2_przed_R59_2026-11-14/sha256_stl_przed_R59.txt ]; then awk '$2 ~ /plytka/ {print $1}' archiwum/wyniki_v2_przed_R59_2026-11-14/sha256_stl_przed_R59.txt; fi
} | LC_ALL=C sort -u > "$STARE"
N_STARE=$(wc -l < "$STARE" | tr -d ' ')
[ "$N_STARE" -ge 14 ] || blad "lista sum sprzed R59 za krotka ($N_STARE, oczekiwane co najmniej 14)"

ZRODLA=(dostawcy_druk_i_pleksi.md narzedzia/buduj_plan_wdrozenia.py plan_ramki_v2.md sesje_2026-10-31/poprawki_pasowan/R53_projekt.md sesje_2026-10-31/poprawki_pasowan/weryfikacja_R53.md
  R54_wdrozenie_zmiany.md recenzja/raport_recenzenta_R54_iter1.md narzedzia/arkusz_zamowienia_R59.py wyniki_model_R59/ramka_3d_v3_R59.html wyniki_model_R59/animacja_ramki_R59.html
  parametry.json protokol_weryfikacji_v2.md ramka_generator.py wyniki_v2/ramka_v2.blend wyniki_v2/README.md wyniki_v2/arkusze/arkusz_wymiarow.md wyniki_v2/arkusze/kody_plytek.md
  wyniki_v2/arkusze/arkusz_zamowienia.csv wyniki_v2/arkusze/arkusz_zamowienia.md wyniki_v2/raport/raport_wykonawcy_R54_iter1.md wyniki_v2/raport/raport_wykonawcy_R55_iter1.md
  wyniki_v2/raport/raport_wykonawcy_R57_iter2.md recenzja/raport_recenzenta_R57_iter1.md R57_wdrozenie_zmiany.md
  R59_wdrozenie_zmiany.md R59_propozycja_ukladu.md wyniki_v2/raport/raport_wykonawcy_R59_iter2.md recenzja/raport_recenzenta_R59_iter1.md recenzja/raport_recenzenta_PR_R59_runda1.md
  narzedzia/uklad_kolo_R59.js narzedzia/weryfikuj_uklad_R59.js stanowisko/README.md stanowisko/raporty/R59_2026-11-14.md)
BRAK=()
for f in "${ZRODLA[@]}"; do if [ ! -f "$f" ]; then BRAK+=("$f"); fi; done
[ "${#BRAK[@]}" = 0 ] || blad "brak plikow zrodlowych: ${BRAK[*]}"
N_JPG=$(find wyniki_model_R59 -maxdepth 1 -name '*.jpg' | wc -l | tr -d ' '); N_PNG=$(find wyniki_v2/render -maxdepth 1 -name '*.png' | wc -l | tr -d ' ')
[ "$N_JPG" = 12 ] || blad "wyniki_model_R59: oczekiwane 12 JPG, jest $N_JPG"
[ "$N_PNG" = 3 ] || blad "wyniki_v2/render: oczekiwane 3 PNG, sa $N_PNG"

# model 3D: wklejone płytki n1 / n4 mają przypięte sumy, żadnej sumy sprzed R59
for plik in ramka_plytka_wieczorna_n1_v2.stl ramka_plytka_poranna_n4_v2.stl; do
  grep -c -F "$(suma_plytki "$plik")" wyniki_model_R59/ramka_3d_v3_R59.html >/dev/null || blad "model 3D (ramka_3d_v3_R59.html) nie zawiera $plik w ukladzie R59"
done
if grep -c -F -f "$STARE" wyniki_model_R59/ramka_3d_v3_R59.html >/dev/null; then blad "model 3D (ramka_3d_v3_R59.html) zawiera plik plytki sprzed R59"; fi
echo "  model 3D R59: plytki n1 i n4 o przypietych sumach, 0 z $N_STARE sum sprzed R59"

# --- 2. PDF: w przebiegu właściwym muszą być zbudowane po R59 (narzedzia/buduj_pdf_R59.cmd)
echo "== 2. Dokumenty PDF"
PDF_UWAGI=0
pdf_zle() {
  if [ "$PROBA" = 1 ]; then uwaga "(dozwolone tylko w przebiegu probnym) $*"; PDF_UWAGI=$((PDF_UWAGI+1))
  else blad "$* - wlasciwy pakiet wymaga PDF zbudowanych po R59 (narzedzia/buduj_pdf_R59.cmd); sama mechanike sprawdza --proba <katalog>"; fi
}
for p in "${PDFY[@]}"; do
  zr="${p%%|*}"; cel="${p##*|}"
  [ -f "$zr.md" ] || blad "brak $zr.md"
  [ -s "$zr.pdf" ] || blad "brak $zr.pdf"
  [ "$(head -c 5 "$zr.pdf")" = "%PDF-" ] || blad "$zr.pdf nie jest plikiem PDF"
  h57=$(awk -v p="*01_Dokumenty/${cel}_2026-11-02_R57.pdf" '$2==p{print $1}' "$SUMY_R57")
  [ -n "$h57" ] || blad "$SUMY_R57: brak wpisu 01_Dokumenty/${cel}_2026-11-02_R57.pdf"
  if [ "$(sha "$zr.pdf")" = "$h57" ]; then pdf_zle "$zr.pdf to bajtowo plik z pakietu R57 (sprzed R59)"; fi
  if [ "$zr.pdf" -ot "$zr.md" ]; then pdf_zle "$zr.pdf jest starszy niz $zr.md"; fi
  grep -F "$FRAZA_PDF" "$zr.md" >/dev/null || blad "$zr.md nie zawiera \"$FRAZA_PDF\" - dokument nie opisuje ukladu R59?"
  if [ "$PYPDF" = 1 ]; then
    kod=0; wynik=$(py_narzedzie pdf "$zr.pdf" "$FRAZA_PDF") || kod=$?
    strony="?"; ile_r59="?"; ile_frazy="?"; read -r strony ile_r59 ile_frazy <<< "$wynik" || true
    case "$kod" in
      0) echo "  $cel: stron $strony, w tekscie \"R59\" $ile_r59 razy, \"$FRAZA_PDF\" $ile_frazy razy";;
      3) pdf_zle "$zr.pdf: w tekscie \"R59\" $ile_r59 razy, \"$FRAZA_PDF\" $ile_frazy razy (stron $strony) - to nie jest dokument po R59";;
      *) blad "pypdf nie odczytal $zr.pdf (kod $kod): $wynik";;
    esac
  else
    pdf_zle "brak modulu pypdf - tresc $zr.pdf niesprawdzona"
  fi
done
[ "$PDF_UWAGI" = 0 ] || uwaga "PRZEBIEG PROBNY: $PDF_UWAGI zastrzezen do PDF - ten wynik NIE jest pakietem do wgrania"

# --- 3. Pakiet w katalogu roboczym
echo "== 3. Pakiet"
for p in "${PDFY[@]}"; do
  zr="${p%%|*}"; cel="${p##*|}"
  cp "$zr.pdf" "$T/01_Dokumenty/${cel}_${DATA}_${R}.pdf"
  cp "$zr.md" "$T/01_Dokumenty/${cel}_${DATA}_${R}.md"
done
cp plan_ramki_v2.md "$T/01_Dokumenty/04_Plan_budowy_ramek_v2_${DATA}_${R}.md"
cp sesje_2026-10-31/poprawki_pasowan/R53_projekt.md "$T/01_Dokumenty/05_R53_projekt_poprawek_pasowan_2026-10-31.md"
cp sesje_2026-10-31/poprawki_pasowan/weryfikacja_R53.md "$T/01_Dokumenty/06_R53_weryfikacja_2026-10-31.md"
cp R54_wdrozenie_zmiany.md "$T/01_Dokumenty/07_R54_gniazda_w_kole_pola_skanowania_2026-11-01.md"
cp recenzja/raport_recenzenta_R54_iter1.md "$T/01_Dokumenty/08_R54_recenzja_plytek_2026-11-01.md"
for f in ramka_korpus_W_v2 ramka_korpus_P_v2 ramka_blat_v2 ramka_wkladka_v2 $PLYTKI_DO_DRUKU; do cp "wyniki_v2/stl/$f.stl" "$T/02_Druk_drukarnia_PA12/"; done
# R59: arkusz generatora (15 pozycji) + 2 płytki okrągłe — tylko w pakiecie, wyniki_v2/arkusze bez zmian; skrypt sam sprawdza objętości i sumy z raportem
"${PYCMD[@]}" narzedzia/arkusz_zamowienia_R59.py "$T/02_Druk_drukarnia_PA12" | tr -d '\r' | sed 's/^/  /'
for f in ramka_pokrywka_v2 ramka_tulejka_dc_v2 ramka_podkladka_panelu_05_v2 ramka_podkladka_panelu_1_v2 ramka_podkladka_panelu_2_v2; do cp "wyniki_v2/stl/$f.stl" "$T/03_Druk_wlasny/PETG_FDM/"; done
# płytka do własnego druku testowego = kopia NOWEGO n1 (wersja ze starym układem R54 jest w pakiecie R57)
cp wyniki_v2/stl/ramka_plytka_wieczorna_n1_v2.stl "$T/03_Druk_wlasny/PETG_FDM/ramka_plytka_wieczorna_n1_v2_TEST_SKANERA.stl"
cp wyniki_model_R59/ramka_3d_v3_R59.html wyniki_model_R59/animacja_ramki_R59.html "$T/04_Model_i_animacje/"
cp wyniki_model_R59/*.jpg wyniki_v2/render/*.png "$T/04_Model_i_animacje/rendery/"
cp dostawcy_druk_i_pleksi.md narzedzia/buduj_plan_wdrozenia.py parametry.json protokol_weryfikacji_v2.md ramka_generator.py wyniki_v2/ramka_v2.blend "$T/05_Zrodla/"
cp wyniki_v2/README.md "$T/05_Zrodla/README_wyniki_v2.md"
cp wyniki_v2/arkusze/arkusz_wymiarow.md wyniki_v2/arkusze/kody_plytek.md "$T/05_Zrodla/"
cp wyniki_v2/json/uklad_gniazd_wieczorna.json wyniki_v2/json/uklad_gniazd_poranna.json wyniki_v2/json/uklad_gniazd_okragla_wieczorna.json wyniki_v2/json/uklad_gniazd_okragla_poranna.json "$T/05_Zrodla/"
for f in $PLYTKI_BAZOWE; do cp "wyniki_v2/stl/$f.stl" "$T/05_Zrodla/"; done
# starsze raporty: opisują poprzedni układ (stare płytki fizyczne zostają w użyciu) i płytkę okrągłą
cp wyniki_v2/raport/raport_wykonawcy_R54_iter1.md wyniki_v2/raport/raport_wykonawcy_R55_iter1.md wyniki_v2/raport/raport_wykonawcy_R57_iter2.md recenzja/raport_recenzenta_R57_iter1.md R57_wdrozenie_zmiany.md "$T/05_Zrodla/"
# R59: opis zmiany, studium wariantów, raport generatora, recenzja płytek z siatek, recenzja całości zmian, narzędzia układu i arkusza
cp R59_wdrozenie_zmiany.md R59_propozycja_ukladu.md wyniki_v2/raport/raport_wykonawcy_R59_iter2.md recenzja/raport_recenzenta_R59_iter1.md recenzja/raport_recenzenta_PR_R59_runda1.md "$T/05_Zrodla/"
cp narzedzia/uklad_kolo_R59.js narzedzia/weryfikuj_uklad_R59.js narzedzia/arkusz_zamowienia_R59.py "$T/05_Zrodla/"
# R59: program stanowiska — dwa układy płytek (nowy i *_r54) i strażnik układu
cp stanowisko/README.md "$T/05_Zrodla/stanowisko_README.md"
cp stanowisko/raporty/R59_2026-11-14.md "$T/05_Zrodla/stanowisko_raport_R59_2026-11-14.md"

# liczby do README i instrukcji — z arkusza zbudowanego przed chwilą (nic z ręki)
ARK_MD="$T/02_Druk_drukarnia_PA12/arkusz_zamowienia.md"; ARK_CSV="$T/02_Druk_drukarnia_PA12/arkusz_zamowienia.csv"
grep -F "17 pozycji: 12 do drukarni" "$ARK_MD" >/dev/null || blad "arkusz zamowienia: brak zdania '17 pozycji: 12 do drukarni'"
pole() { awk -F'|' -v n="$2" '{gsub(/^ +| +$/, "", $n); print $n; exit}' <<< "$1"; }
W10=$(grep -m1 '^| 10 pozycji' "$ARK_MD") || blad "arkusz zamowienia: brak wiersza sum 10 pozycji"
W12=$(grep -m1 '^| 12 pozycji' "$ARK_MD") || blad "arkusz zamowienia: brak wiersza sum 12 pozycji"
K10_MIN=$(pole "$W10" 4); K10_POK=$(pole "$W10" 5); K12_MIN=$(pole "$W12" 4); K12_POK=$(pole "$W12" 5)
{ [ -n "$K10_MIN" ] && [ -n "$K10_POK" ] && [ -n "$K12_MIN" ] && [ -n "$K12_POK" ]; } || blad "arkusz zamowienia: nie odczytano kosztow z wierszy sum"
wiersze_plytek() {  # $1 = txt (README) albo md (instrukcja): 8 plików płytek do zamówienia z sumą, objętością i gabarytem
  local f plik suma obj gab
  for f in $PLYTKI_DO_DRUKU; do
    plik="$f.stl"; suma=$(suma_plytki "$plik")
    obj=$(tr -d '\r' < "$ARK_CSV" | awk -F';' -v p="$plik" '$1==p{print $8}')
    gab=$(tr -d '\r' < "$ARK_CSV" | awk -F';' -v p="$plik" '$1==p{print $9}' | sed 's/,0\( \|$\)/\1/g')
    { [ -n "$suma" ] && [ -n "$obj" ] && [ -n "$gab" ]; } || blad "arkusz zamowienia: brak danych pliku $plik"
    if [ "$1" = txt ]; then printf '    %-42s SHA-256 %s  %s cm3  %s\n' "$plik" "$suma" "$obj" "${gab// × / x }"
    else printf '  - `%s` — SHA-256 `%s`, %s cm³, %s mm\n' "$plik" "$suma" "$obj" "$gab"; fi
  done
}
PLYTKI_TXT=$(wiersze_plytek txt); PLYTKI_MD=$(wiersze_plytek md)
if [ "$PROBA" = 1 ]; then
  ZNAK_TXT="PRZEBIEG PROBNY (sprawdzenie mechaniki skryptu) — NIE WGRYWAC I NIE ZAMAWIAC Z TEGO KATALOGU; dokumenty PDF moga byc sprzed R59.
"
  ZNAK_MD="**PRZEBIEG PRÓBNY (sprawdzenie mechaniki skryptu) — NIE WGRYWAĆ; dokumenty PDF mogą być sprzed R59.**

"
else ZNAK_TXT=""; ZNAK_MD=""; fi

cat > "$T/README.txt" <<TXT
${ZNAK_TXT}Ramki swietlne i plytki 96x96 + plytki okragle o100 — pakiet wynikowy v2 po R59, ${DATA}
Zastepuje pakiet Ramki_pakiet_2026-11-02_R57 (nie usuwac starego; nowsze wersje maja date i numer R w nazwie).

R59 — NOWY UKLAD GNIAZD PLYTEK (zlecenie wlasciciela; wykonawca R59-A; recenzja z siatek R59-B: ZALICZONA):
- Wieksze gniazda w miejscu malych i jedna rynienka zamiast dwoch:
    plytka wieczorna: 18 gniazd (6 x o12, 12 x o15) + 1 rynienka 60 x 15   — bylo 18 gniazd (7 x o9, 6 x o12, 5 x o15) + 2 rynienki
    plytka poranna:   23 gniazda (20 x o12,5, 3 x o15) + 1 rynienka 50 x 13 — bylo 31 gniazd (18 x o7,5, 7 x o10, 6 x o12,5) + 2 rynienki
  Plytki okragle n8 / n9 maja te same gniazda co kwadratowe tego samego typu. Numery plytek (n1-n6, n8, n9) i ilosci bez zmian.
- Zmienily sie TYLKO pliki plytek. Do zamowienia w drukarni (PA12 bialy mat, bez wygladzania, +-0,3 mm) — 8 plikow w 02_Druk_drukarnia_PA12:
${PLYTKI_TXT}
- UWAGA — TE SAME NAZWY, INNY UKLAD: w pakietach R54, R55, R56 i R57 pliki plytek nazywaja sie tak samo, ale maja poprzedni uklad gniazd.
  Nie mieszac plikow z roznych pakietow. Plik rozpoznaje sie po sumie SHA-256, nie po nazwie. Jesli drukarnia dostala wczesniej pliki plytek — zastapic.
- Stare plytki fizyczne (poprzedni uklad) zostaja w uzyciu. Numer na plytce jest w obu ukladach ten sam, wiec stare plytki trzeba opisac
  trwalym napisem (np. "R54") i trzymac osobno od nowych.
- Program stanowiska zna oba uklady (nowy pod dotychczasowymi nazwami, poprzedni z dopiskiem _r54) i ostrzega, gdy zeskanowana plytka
  nie pasuje do wybranego ukladu (opis: 05_Zrodla/stanowisko_README.md, liczby: 05_Zrodla/stanowisko_raport_R59_2026-11-14.md).
- Korpus W, korpus P, blat, wkladka, pokrywka, tulejka DC i 3 podkladki: bajtowo bez zmian — te same SHA-256 co w pakiecie R57 (9 plikow).
- Arkusz zamowienia: 17 pozycji (12 do drukarni z n8 / n9; drukarnia razem ${K12_MIN} zl najtanszy / ${K12_POK} zl pokazowy;
  bez plytek okraglych ${K10_MIN} / ${K10_POK} zl).
- Dokumenty 01–03 opisuja nowy uklad (sekcja "Nowy uklad gniazd plytek [R59]"); plan budowy (04) i protokol maja liczby R59;
  model 3D i animacja pokazuja nowy uklad.

STAN GEOMETRII: gniazda, rynienka i stozki znacznikow plytek w kole o promieniu 47 mm (pole skanowania o100 przy obrocie — zalozenie, pomiar #12
makieta z okregami o90/94/100). Plytka okragla o100 x 8: sciecie orientacyjne na obwodzie — NIE WYGLADZAC; tylko do skanera (bez kieszeni magnesow,
wkladka i pokrywka ramki jej nie obsluguja — przyszla zmiana R58). Ramka bez zmian od R53–R55: obudowa 200x200x63,6, luzy R53.
Druk wlasny wylacznie FDM PETG u kolegi (pokrywka x4, tulejka DC x2, podkladki 3x8, plytka testowa n1, prototypy); z zywicy nic.
02_Druk_drukarnia_PA12/ramka_wkladka_v2.stl = plik zweryfikowany w R53/R54 (SHA f4196fbc...).
Zamawiac TYLKO pliki z tego pakietu (SHA-256 w ${SUMY} i w dokumencie 02_Zakupy_i_druk, sekcja "Specyfikacja zamowienia").

01_Dokumenty            01 plan wdrozenia stanowiska (PDF+MD), 02 zakupy i druk z lista firm (PDF+MD), 03 budowa ramki — decyzje i zamienniki (PDF+MD),
                        04 plan budowy ramek (MD, zrodlo prawdy, rejestr R1–R59), 05–06 projekt i weryfikacja R53 (pasowania),
                        07 opis zmiany R54 i 08 recenzja plytek R54 (poprzedni uklad gniazd — dotycza starych plytek fizycznych)
02_Druk_drukarnia_PA12  STL do zamowienia w drukarni MJF/SLS PA12 + arkusz zamowienia (ilosci, objetosci, materialy)
                        od razu: ramka_korpus_W, ramka_korpus_P, ramka_blat (x2);
                        po decyzji wlasciciela (kwadratowe, okragle czy obie): plytki okragle n8 i n9;
                        po potwierdzeniu pola skanowania (#12): ramka_wkladka (x3), plytki n1-n6
03_Druk_wlasny          PETG_FDM (wszystko FDM PETG u kolegi): pokrywka (x4); tulejka DC (x2, tylko przy gniezdzie z gwintem o8, drukowana
                        PO pomiarze otworu, skalowanie XY w slicerze), podkladki panelu 0,5/1/2 (po 8), plytka n1 do testu skanera (PETG bialy matowy).
                        ramka_plytka_wieczorna_n1_v2_TEST_SKANERA.stl = kopia NOWEGO pliku n1 (uklad R59); wersja z poprzednim ukladem (R54) jest w pakiecie R57.
04_Model_i_animacje     model 3D v3 R59 (ramka_3d_v3_R59.html — otworz dwuklikiem, dziala z dysku bez internetu; nowy uklad gniazd; bez plytki okraglej;
                        wersja online podana w pakiecie R57 pokazuje poprzedni uklad); animacja_ramki_R59.html (pokazuje nowy uklad gniazd);
                        rendery: zrzuty modelu i animacji R59 (12 JPG) i rendery Blendera po R59 (3 PNG)
05_Zrodla               parametry.json (jedyne zrodlo liczb), uklad_gniazd_*.json (4 pliki: wspolrzedne gniazd i znacznikow nowego ukladu),
                        model Blendera ramka_v2.blend, protokol weryfikacji, generator Blendera, README wynikow (SHA-256 plikow), arkusz wymiarow, kody plytek,
                        R59: R59_wdrozenie_zmiany.md (co zmieniono, sumy plikow), R59_propozycja_ukladu.md (policzone warianty), raport wykonawcy R59 iter2,
                        raport recenzenta R59 iter1 (plytki sprawdzone z siatek), raport_recenzenta_PR_R59_runda1.md (recenzja calosci zmian),
                        bazowe STL 4 typow plytek (tylko do sprawdzen — NIE do zamowienia), skrypty ukladu (uklad_kolo_R59.js, weryfikuj_uklad_R59.js),
                        arkusz_zamowienia_R59.py (dopisuje n8 / n9 do arkusza generatora), stanowisko_README.md i stanowisko_raport_R59_2026-11-14.md
                        (program stanowiska: dwa uklady plytek i straznik ukladu),
                        starsze (poprzedni uklad i plytka okragla): raporty wykonawcy R54, R55, R57 iter2, recenzja R57 iter1, R57_wdrozenie_zmiany.md;
                        dostawcy_druk_i_pleksi.md, buduj_plan_wdrozenia.py (buduje PDF dokumentow 01–03)
Nie usuwac starszych plikow na Dysku; nowsze wersje maja date w nazwie.
TXT

# --- 4. Sumy i kontrole pakietu
echo "== 4. Sumy i kontrole pakietu"
( cd "$T" && find . -type f ! -name "SHA256SUMS_*" | sed 's|^\./||' | LC_ALL=C sort | xargs -d '\n' sha256sum -b > "$SUMY" )
N_PLIKOW=$(wc -l < "$T/$SUMY" | tr -d ' ')
[ "$N_PLIKOW" = "$LICZBA_PLIKOW" ] || blad "pakiet ma $N_PLIKOW plikow, oczekiwane $LICZBA_PLIKOW (zmienila sie lista? popraw LICZBA_PLIKOW swiadomie)"
ZLE_NAZWY=$(cut -c67- "$T/$SUMY" | LC_ALL=C grep -v '^[A-Za-z0-9._/-]*$' || true)
[ -z "$ZLE_NAZWY" ] || blad "nazwy plikow pakietu spoza ASCII albo ze spacja: $ZLE_NAZWY"
# każdy plik płytki i JSON układu w pakiecie ma przypiętą sumę (po nazwie)
N=0
while read -r suma sciezka; do
  plik="${sciezka##*/}"; plik="${plik/_TEST_SKANERA/}"
  case "$plik" in
    ramka_plytka_*.stl) ocz=$(suma_plytki "$plik");;
    uklad_gniazd_*.json) ocz=$(awk -v p="$plik" '$1==p{print $2}' <<< "$SHA_JSON");;
    *) continue;;
  esac
  [ "$suma" = "$ocz" ] || blad "${sciezka#\*}: suma inna niz przypieta dla $plik"
  N=$((N+1))
done < "$T/$SUMY"
[ "$N" = 17 ] || blad "pliki plytek i JSON ukladu w pakiecie: oczekiwane 17 (8 do druku + kopia n1 + 4 bazowe + 4 JSON), jest $N"
echo "  17 z 17 plikow plytek i JSON ukladu w pakiecie ma sume przypieta (12 roznych STL: 8 do druku + kopia n1 do testu + 4 bazowe; 4 JSON)"
# żadnej sumy sprzed R59
if cut -c1-64 "$T/$SUMY" | grep -F -x -f "$STARE" >/dev/null; then blad "w pakiecie jest plik plytki albo JSON ukladu sprzed R59 (suma z listy $N_STARE sum starego ukladu)"; fi
echo "  0 z $N_PLIKOW plikow pakietu ma sume pliku plytki / JSON ukladu sprzed R59 (lista $N_STARE sum)"
# 9 plików niepłytkowych: ta sama ścieżka i suma co w pakiecie R57
ZLE=0; N=0
while read -r suma sciezka; do
  case "$sciezka" in *plytka*) continue;; *.stl) ;; *) continue;; esac
  N=$((N+1))
  if ! grep -x -F "$suma $sciezka" "$T/$SUMY" >/dev/null; then echo "ROZNICA: ${sciezka#\*}"; ZLE=$((ZLE+1)); fi
done < "$SUMY_R57"
echo "  pliki nieplytkowe STL z pakietu R57: $N, identyczne w $R (sciezka i suma): $((N-ZLE))"
{ [ "$N" = 9 ] && [ "$ZLE" = 0 ]; } || blad "pliki nieplytkowe rozne od pakietu R57"
( cd "$T" && sha256sum -c --quiet "$SUMY" ) || blad "sha256sum -c w katalogu roboczym pakietu"
echo "  sha256sum -c: $N_PLIKOW z $N_PLIKOW OK"

# --- 5. Pliki na Dysk: 3 ZIP‑y (podział jak R57), sumy, instrukcja, lista, 3 PDF
echo "== 5. Pliki na Dysk"
( cd "$T" && { find 01_Dokumenty 02_Druk_drukarnia_PA12 03_Druk_wlasny -type f | LC_ALL=C sort; echo README.txt; echo "$SUMY"; } ) > "$TW/cz1.lista"
( cd "$T" && find 04_Model_i_animacje -type f | LC_ALL=C sort ) > "$TW/cz2.lista"
( cd "$T" && find 05_Zrodla -type f | LC_ALL=C sort ) > "$TW/cz3.lista"
py_narzedzie zip "$T" "$KATALOG_ZIP" "$TW/$ZIP1" "$DATA" "$TW/cz1.lista"
py_narzedzie zip "$T" "$KATALOG_ZIP" "$TW/$ZIP2" "$DATA" "$TW/cz2.lista"
py_narzedzie zip "$T" "$KATALOG_ZIP" "$TW/$ZIP3" "$DATA" "$TW/cz3.lista"
py_narzedzie sprawdz "$T/$SUMY" "$KATALOG_ZIP" "$TW/$ZIP1" "$TW/$ZIP2" "$TW/$ZIP3"
for z in "$ZIP1" "$ZIP2" "$ZIP3"; do
  b=$(stat -c %s "$TW/$z")
  [ "$b" -lt "$LIMIT_ZIP" ] || blad "$z ma $(tys "$b") bajtow - limit $(tys "$LIMIT_ZIP") (10 MB na plik)"
done
N1=$(wc -l < "$TW/cz1.lista" | tr -d ' '); N2=$(wc -l < "$TW/cz2.lista" | tr -d ' '); N3=$(wc -l < "$TW/cz3.lista" | tr -d ' ')
rm -f "$TW"/cz?.lista "$STARE"
cp "$T/$SUMY" "$TW/$SUMY"
for p in "${PDFY[@]}"; do cel="${p##*|}"; cp "$T/01_Dokumenty/${cel}_${DATA}_${R}.pdf" "$TW/"; done

cat > "$TW/$INSTR" <<TXT
# Pakiet Ramki R59 — ${DATA} — jak rozpakować i co jest nowe

${ZNAK_MD}Ten pakiet ZASTĘPUJE Ramki_pakiet_2026-11-02_R57 (starszych plików na Dysku nie usuwamy; obowiązuje najnowszy numer R).

## Pliki
- ${ZIP1} — 01_Dokumenty (3 PDF + MD: plan wdrożenia, Zakupy i druk, Budowa ramki — decyzje i zamienniki; plan budowy ramek; R53/R54), 02_Druk_drukarnia_PA12 (12 STL, w tym 8 plików płytek w nowym układzie gniazd, + arkusz zamówienia), 03_Druk_wlasny (PETG FDM), README.txt, SHA256SUMS.
- ${ZIP2} — 04_Model_i_animacje (model 3D v3 R59 offline i animacja — oba z nowym układem gniazd; zrzuty i rendery; bez płytki okrągłej).
- ${ZIP3} — 05_Zrodla (parametry.json, generator, protokół, blend, arkusze, 4 JSON układów gniazd, bazowe STL 4 typów płytek, R59_wdrozenie_zmiany.md, R59_propozycja_ukladu.md, raport wykonawcy R59, recenzja płytek R59, recenzja całości zmian R59, opis programu stanowiska i jego raport R59; starsze raporty R54–R57).
- ${SUMY} — sumy wszystkich ${N_PLIKOW} plików pakietu (ścieżki względem folderu ${KATALOG_ZIP}/).
- Osobno (do otwarcia bez rozpakowywania, identyczne z cz1): 01_Plan_wdrozenia_v2_${DATA}_${R}.pdf, 02_Zakupy_i_druk_${DATA}_${R}.pdf, 03_Budowa_ramki_decyzje_i_zamienniki_${DATA}_${R}.pdf.

Rozpakować wszystkie trzy ZIP-y do jednego folderu — każdy zawiera ten sam katalog nadrzędny \`${KATALOG_ZIP}/\`, więc podfoldery 01–05 złożą się w całość.

## Co nowego w R59
- Nowy układ gniazd płytek: większe gniazda w miejscu małych i jedna rynienka zamiast dwóch.
  - Płytka wieczorna: 18 gniazd (6 × ø12, 12 × ø15) i 1 rynienka 60 × 15 mm. Było: 18 gniazd (7 × ø9, 6 × ø12, 5 × ø15) i 2 rynienki.
  - Płytka poranna: 23 gniazda (20 × ø12,5, 3 × ø15) i 1 rynienka 50 × 13 mm. Było: 31 gniazd (18 × ø7,5, 7 × ø10, 6 × ø12,5) i 2 rynienki.
  - Płytki okrągłe nr 8 i 9 mają te same gniazda co kwadratowe tego samego typu.
- Zmieniły się tylko pliki płytek. Do zamówienia w drukarni (PA12 biały mat, bez wygładzania, ±0,3 mm) jest 8 plików z folderu 02_Druk_drukarnia_PA12:
${PLYTKI_MD}
- Korpusy, blat, wkładka, pokrywka, tulejka i podkładki to bajtowo te same pliki co w pakiecie R57 (9 plików, te same sumy SHA-256).
- Uwaga na starsze pakiety: w pakietach R54, R55, R56 i R57 pliki płytek mają TE SAME NAZWY, ale poprzedni układ gniazd. Nie mieszać plików z różnych pakietów. Plik rozpoznaje się po sumie SHA-256, nie po nazwie. Jeśli drukarnia dostała wcześniej pliki płytek, trzeba je zastąpić plikami z tego pakietu.
- Stare płytki fizyczne (poprzedni układ) zostają w użyciu. Numer na płytce jest w obu układach ten sam, więc stare płytki trzeba opisać trwałym napisem (np. „R54”) i trzymać osobno od nowych.
- Program stanowiska zna oba układy (nowy pod dotychczasowymi nazwami, poprzedni z dopiskiem \`_r54\`) i ostrzega, gdy zeskanowana płytka nie pasuje do wybranego układu.
- Numery płytek (1–3 wieczorne, 4–6 poranne, 8 i 9 okrągłe) i ilości bez zmian. Arkusz zamówienia: 17 pozycji; drukarnia z płytkami okrągłymi ${K12_MIN} zł (najtańszy) / ${K12_POK} zł (pokazowy), bez okrągłych ${K10_MIN} / ${K10_POK} zł.
- Dokumenty 01–03 opisują nowy układ (sekcja „Nowy układ gniazd płytek [R59]”); model 3D i animacja pokazują nowy układ.

Zamawiać w drukarni wyłącznie pliki z sumami SHA-256 z dokumentu 02 („Specyfikacja zamówienia”).
TXT

FOLDER=""
if [ -f "$WGRANIE_REPO/DO_WGRANIA_NA_DRIVE_2026-11-02_R57.md" ]; then FOLDER=$(grep -m1 '^Folder: ' "$WGRANIE_REPO/DO_WGRANIA_NA_DRIVE_2026-11-02_R57.md" | tr -d '\r' || true); fi
[ -n "$FOLDER" ] || FOLDER="Folder: QC (Mój dysk > QC)"
{
  cat <<TXT
# Pakiet R59 — DO WGRANIA na Google Drive (folder QC) — pakiet z ${DATA}, jeszcze NIE wgrany

${ZNAK_MD}Wgranie dopiero po zgodzie właściciela. Po wgraniu zapisać potwierdzenie w \`WGRANE_NA_DRIVE_${DATA}_${R}.md\` (wzór: \`WGRANE_NA_DRIVE_2026-11-01_R56.md\`).

${FOLDER}
Zasady: tylko „Nowy → Prześlij plik”, nic nie usuwać, nic nie nadpisywać; każda nazwa poniżej jest nowa (R57 i starsze zostają).
Metoda (jak R56): JS nadpisuje \`HTMLInputElement.prototype.click\` (przechwycenie input), Nowy → Prześlij plik, \`find\` „upload-input”, \`file_upload\` jeden plik na raz; po wgraniu odświeżyć listę i potwierdzić nazwy.

| Plik (ten folder) | Bajty | SHA‑256 (pierwsze 16) |
|---|---|---|
TXT
  for n in "${NAZWY_DYSK[@]}"; do printf '| %s | %s | %s |\n' "$n" "$(tys "$(stat -c %s "$TW/$n")")" "$(sha "$TW/$n" | cut -c1-16)"; done
  cat <<TXT

ZIP‑y zbudowane i sprawdzone skryptem \`Ramki/narzedzia/zbuduj_pakiet_${R}.sh\`: po złożeniu trzech ZIP‑ów w jeden folder ${N_PLIKOW} z ${N_PLIKOW} plików zgodnych z ${SUMY} (cz1 ${N1} plików razem z README i plikiem sum, cz2 ${N2}, cz3 ${N3}); każdy ZIP < 10 MB. PDF‑y identyczne z \`Ramki_pakiet/01_Dokumenty/\`.
TXT
} > "$TW/$LISTA"

# --- 6. Zamiana: dopiero teraz zmieniam cel (wszystkie kontrole przeszły)
echo "== 6. Zapis"
if [ "$PROBA" != 1 ] && [ "$D" = Ramki_pakiet ] && [ -d "$D" ] && [ -n "$(ls -A "$D")" ]; then
  if ls "$D"/SHA256SUMS_*_"$R".txt >/dev/null 2>&1; then
    echo "  poprzedni pakiet w $D to juz $R (przebudowa) - bez kopii do archiwum"
  else
    ARCH="archiwum/Ramki_pakiet_przed_${R}_${DATA}"
    if [ -e "$ARCH" ]; then diff -r "$D" "$ARCH" >/dev/null || blad "$ARCH juz istnieje i rozni sie od $D - nie nadpisuje archiwum"
    else mkdir -p archiwum; cp -r "$D" "$ARCH"; fi
    for s in "$ARCH"/SHA256SUMS_*.txt; do ( cd "$ARCH" && sha256sum -c --quiet "${s##*/}" ) || blad "kopia w $ARCH: sha256sum -c"; done
    echo "  poprzedni pakiet odlozony do $ARCH (sha256sum -c OK)"
  fi
fi
SPRZATAJ=0   # gdyby zamiana się nie udała, nowy pakiet zostaje w katalogu roboczym
rm -rf "$D"
mv "$T" "$D" || blad "nie udalo sie przeniesc $T do $D - nowy pakiet zostal w $T"
( cd "$D" && sha256sum -c --quiet "$SUMY" ) || blad "sha256sum -c w $D"
for n in "${NAZWY_W[@]}"; do cp "$TW/$n" "$W/$n"; done
for n in "${NAZWY_W[@]}"; do cmp -s "$TW/$n" "$W/$n" || blad "$W/$n rozni sie od zbudowanego"; done
for p in "${PDFY[@]}"; do cel="${p##*|}"; cmp -s "$D/01_Dokumenty/${cel}_${DATA}_${R}.pdf" "$W/${cel}_${DATA}_${R}.pdf" || blad "PDF $cel w $W rozni sie od pakietu"; done
cmp -s "$D/$SUMY" "$W/$SUMY" || blad "$SUMY w $W rozni sie od pakietu"
[ "$PRZED" = "$(migawka)" ] || blad "w $W zmienil sie albo zniknal plik spoza pakietu $R - sprawdz git status"
N_INNE=$(printf '%s' "$PRZED" | grep -c . || true)
echo "  $W: zapisane ${#NAZWY_W[@]} plikow $R; pozostale pliki bez zmian: $N_INNE z $N_INNE (sumy przed = po)"
rm -rf "$TW"; SPRZATAJ=1
if [ "$PROBA" = 1 ]; then
  printf 'PRZEBIEG PROBNY zbuduj_pakiet_%s.sh, data %s.\nSprawdzenie mechaniki skryptu. NIE WGRYWAC na Dysk i NIE ZAMAWIAC z tego katalogu.\nZastrzezenia do PDF w tym przebiegu: %s (PDF moga byc sprzed R59).\n' "$R" "$DATA" "$PDF_UWAGI" > "${CEL%/}/PRZEBIEG_PROBNY.txt"
fi

echo "== Wynik ($TRYB)"
echo "Pakiet gotowy: $D — $N_PLIKOW plikow + plik sum (pakiet R57: 63 + 1); sha256sum -c OK"
du -sh "$D" | sed 's/^/  /'
echo "Pliki na Dysk: $W"
for n in "${NAZWY_W[@]}"; do printf '  %-62s %12s B  %s\n' "$n" "$(tys "$(stat -c %s "$W/$n")")" "$(sha "$W/$n" | cut -c1-16)"; done
[ "$PROBA" != 1 ] || echo "PRZEBIEG PROBNY - wynik nie jest pakietem do wgrania (zastrzezen do PDF: $PDF_UWAGI)"
