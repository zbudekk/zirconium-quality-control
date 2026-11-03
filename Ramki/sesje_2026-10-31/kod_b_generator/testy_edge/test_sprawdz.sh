#!/usr/bin/env bash
# Tryb --etap SPRAWDZ na kopiach kompletu wyników (z przebiegu bazowego w scratchpadzie) z uszkodzeniami.
# Użycie: bash test_sprawdz.sh <katalog_gen_z_kopia_generatora> <katalog_out_bazowy> <katalog_roboczy>
set -u
BL="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"
GEN="$1"; BAZA="$2"; ROB="$3"
mkdir -p "$ROB"
uruchom() {  # nazwa, katalog out
  local W="$1" OUT="$2"
  echo "=== SPRAWDZ $W ($(date +%T))" | tee -a "$ROB/przebiegi.txt"
  ( cd "$GEN" && timeout 600 "$BL" -b --factory-startup -P ramka_generator.py -- --etap SPRAWDZ --iter 9 --out "$(cygpath -w "$OUT")" ) > "$ROB/$W.log" 2>&1
  echo "kod wyjscia $?" | tee -a "$ROB/przebiegi.txt"
  grep -E "\[ramka\] (RAPORT|BLAD)|Traceback|Error:" "$ROB/$W.log" | tail -4 | tee -a "$ROB/przebiegi.txt"
}
# 1. nietknięta kopia: B=0, żaden plik poza raport/ nie zmieniony
rm -rf "$ROB/nietknieta"; cp -r "$BAZA" "$ROB/nietknieta"; (cd "$ROB/nietknieta" && find . -type f -not -path "./raport/*" -exec sha256sum {} \; | sort) > "$ROB/sha_przed.txt"
uruchom nietknieta "$ROB/nietknieta"
(cd "$ROB/nietknieta" && find . -type f -not -path "./raport/*" -exec sha256sum {} \; | sort) > "$ROB/sha_po.txt"
diff "$ROB/sha_przed.txt" "$ROB/sha_po.txt" > /dev/null && echo "pliki poza raport/ bez zmian" | tee -a "$ROB/przebiegi.txt" || echo "UWAGA: pliki zmienione" | tee -a "$ROB/przebiegi.txt"
# 2. brak jednego STL etapu C
rm -rf "$ROB/brak_stl"; cp -r "$BAZA" "$ROB/brak_stl"; rm "$ROB/brak_stl/stl/ramka_tulejka_dc_v2.stl"
uruchom brak_stl "$ROB/brak_stl"
# 3. obcięty STL korpusu W (połowa pliku)
rm -rf "$ROB/obciety"; cp -r "$BAZA" "$ROB/obciety"; F="$ROB/obciety/stl/ramka_korpus_W_v2.stl"; head -c $(( $(stat -c %s "$F") / 2 )) "$F" > "$F.tmp" && mv "$F.tmp" "$F"
uruchom obciety "$ROB/obciety"
# 4. podmiana: płytka n1 zastąpiona płytką n2 (zły plik pod dobrą nazwą)
rm -rf "$ROB/podmiana"; cp -r "$BAZA" "$ROB/podmiana"; cp "$ROB/podmiana/stl/ramka_plytka_wieczorna_n2_v2.stl" "$ROB/podmiana/stl/ramka_plytka_wieczorna_n1_v2.stl"
uruchom podmiana "$ROB/podmiana"
# 5. STL przeskalowany x1000 (błąd jednostek) — korpus P
rm -rf "$ROB/skala"; cp -r "$BAZA" "$ROB/skala"
"/c/Program Files/Blender Foundation/Blender 5.2/5.2/python/bin/python.exe" - "$ROB/skala/stl/ramka_korpus_P_v2.stl" <<'EOF'
import struct, sys
p = sys.argv[1]; d = bytearray(open(p, 'rb').read()); n = struct.unpack_from('<I', d, 80)[0]
for i in range(n):
    o = 84 + 50 * i + 12
    v = struct.unpack_from('<9f', d, o)
    struct.pack_into('<9f', d, o, *[x * 1000 for x in v])
open(p, 'wb').write(d)
EOF
uruchom skala "$ROB/skala"
# 6. brak JSON gniazd (SPRAWDZ nie może go odtworzyć)
rm -rf "$ROB/brak_json"; cp -r "$BAZA" "$ROB/brak_json"; rm "$ROB/brak_json/json/uklad_gniazd_poranna.json"
uruchom brak_json "$ROB/brak_json"
echo "KONIEC $(date +%T)" | tee -a "$ROB/przebiegi.txt"
