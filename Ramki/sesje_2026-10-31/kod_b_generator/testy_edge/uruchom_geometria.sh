#!/usr/bin/env bash
# Przebiegi generatora na wariantach parametry.json — WYŁĄCZNIE do folderu w scratchpadzie (nigdy do wyniki_v2/).
# Użycie: bash uruchom_geometria.sh <katalog_bazowy_z_kopia_generatora> <katalog_roboczy> [lista wariantów...]
set -u
BL="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"
PY="/c/Program Files/Blender Foundation/Blender 5.2/5.2/python/bin/python.exe"
BAZA="$1"; ROB="$2"; shift 2
TU="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$ROB/logi"
PYTHONUTF8=1 "$PY" "$TU/warianty.py" "$BAZA" "$ROB" > "$ROB/logi/warianty.txt"
LISTA="$*"
[ -z "$LISTA" ] && LISTA=$(awk '{print $1}' "$ROB/logi/warianty.txt")
for W in $LISTA; do
  KAT="$ROB/gen_$W"
  ETAP=$(sed -n 3p "$KAT/WARIANT.txt"); ARGS=$(sed -n 4p "$KAT/WARIANT.txt")
  OUT="$ROB/out_$W"
  rm -rf "$OUT"; mkdir -p "$OUT"
  if [ "$W" = "socket_depth" ] || [ "$W" = "socket_depth2" ]; then mkdir -p "$OUT/json"; cp "$BAZA/../json_wyniki_v2/"*.json "$OUT/json/"; fi
  echo "=== $W etap $ETAP $ARGS ($(date +%T))" | tee -a "$ROB/logi/przebiegi.txt"
  OUTW=$(cygpath -w "$OUT")
  ( cd "$KAT" && timeout 600 "$BL" -b --factory-startup -P ramka_generator.py -- --etap "$ETAP" --iter 1 --out "$OUTW" $ARGS ) > "$ROB/logi/$W.log" 2>&1
  echo "kod wyjscia $? ($(date +%T))" | tee -a "$ROB/logi/przebiegi.txt"
  grep -E "\[ramka\] (RAPORT|BLAD)|Traceback|Error" "$ROB/logi/$W.log" | tail -5 | tee -a "$ROB/logi/przebiegi.txt"
  if [ -d "$OUT/stl" ]; then (cd "$OUT/stl" && sha256sum *.stl) > "$ROB/logi/sha_$W.txt" 2>/dev/null; fi
done
echo "KONIEC $(date +%T)" | tee -a "$ROB/logi/przebiegi.txt"
