#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
R58 (19.11.2026): paczka zamowienia kompletu okraglego do ramki - jeden ZIP + plik sum.

Zawartosc (wszystko sprawdzane po SHA-256, niezgodnosc = blad, ZIP nie powstaje):
  01_Drukarnia_PA12/   6 plytek okraglych ramkowych n1-n6 + wkladka okragla (wyniki_v2/stl, sumy z sha256_stl_po_R58.txt)
                       + korpus W, korpus P, blat (Ramki_pakiet, sumy z SHA256SUMS_2026-11-16_R59.txt) + arkusz zamowienia R58
  02_Druk_wlasny_PETG/ pokrywka okragla (R58) + tulejka DC i podkladki panelu (R59)
  03_Zrodla/           2 pliki bazowe plytek, 2 JSON ukladow, R58_wdrozenie_zmiany.md, sha256_stl_po_R58.txt
  CZYTAJ.txt, SHA256SUMS_<data>_R58.txt
ZIP jest powtarzalny bajtowo (stala data wpisow, stala kolejnosc, kompresja deflate poziom 9).

Uruchomienie (z folderu Ramki):  python narzedzia/zbuduj_zamowienie_R58.py <katalog_docelowy> [--data 2026-11-19]
Najpierw: python narzedzia/arkusz_zamowienia_R58.py . --nazwa R58_arkusz_zamowienia
"""
import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
W = ROOT / "wyniki_v2"
PAK = ROOT / "Ramki_pakiet"
SUMY_R58 = W / "raport" / "sha256_stl_po_R58.txt"
SUMY_R59 = PAK / "SHA256SUMS_2026-11-16_R59.txt"
R59_DRUKARNIA = ("ramka_korpus_W_v2.stl", "ramka_korpus_P_v2.stl", "ramka_blat_v2.stl")
R59_WLASNY = ("ramka_tulejka_dc_v2.stl", "ramka_podkladka_panelu_05_v2.stl", "ramka_podkladka_panelu_1_v2.stl", "ramka_podkladka_panelu_2_v2.stl")


def sha(dane):
    return hashlib.sha256(dane).hexdigest()


def sumy(sciezka):
    wynik = {}
    for linia in sciezka.read_text(encoding="utf-8").splitlines():
        if " *" in linia:
            h, n = linia.strip().split(" *", 1)
            wynik[n] = h
    return wynik


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cel")
    ap.add_argument("--data", default="2026-11-19")
    a = ap.parse_args()
    P = json.loads((ROOT / "parametry.json").read_text(encoding="utf-8"))
    il = next(s["quantities_r58"]["value"] for s in P.values() if isinstance(s, dict) and "quantities_r58" in s)
    mat = next(s["materials_r58"]["value"] for s in P.values() if isinstance(s, dict) and "materials_r58" in s)
    s58, s59 = sumy(SUMY_R58), sumy(SUMY_R59)
    bledy, pliki = [], []          # pliki: (nazwa w ZIP, bajty)

    def dodaj(cel, zrodlo, oczekiwana, opis):
        if not zrodlo.exists():
            bledy.append("brak pliku %s" % zrodlo)
            return
        dane = zrodlo.read_bytes()
        if oczekiwana is None:
            bledy.append("brak sumy dla %s (%s)" % (zrodlo.name, opis))
        elif oczekiwana != "-" and sha(dane) != oczekiwana:
            bledy.append("%s: SHA %s != %s (%s)" % (zrodlo.name, sha(dane)[:12], oczekiwana[:12], opis))
        pliki.append((cel + "/" + zrodlo.name if cel else zrodlo.name, dane))

    for rdzen in il:
        n = rdzen + "_v2.stl"
        kat = "01_Drukarnia_PA12" if mat[rdzen].startswith("PA12 drukarnia") else "02_Druk_wlasny_PETG"
        dodaj(kat, W / "stl" / n, s58.get("stl/" + n), SUMY_R58.name)
    for n in R59_DRUKARNIA:
        dodaj("01_Drukarnia_PA12", PAK / "02_Druk_drukarnia_PA12" / n, s59.get("02_Druk_drukarnia_PA12/" + n), SUMY_R59.name)
    for n in R59_WLASNY:
        dodaj("02_Druk_wlasny_PETG", PAK / "03_Druk_wlasny" / "PETG_FDM" / n, s59.get("03_Druk_wlasny/PETG_FDM/" + n), SUMY_R59.name)
    for n in ("R58_arkusz_zamowienia.md", "R58_arkusz_zamowienia.csv"):
        dodaj("01_Drukarnia_PA12", ROOT / n, "-", "arkusz")
    for typ in ("wieczorna", "poranna"):
        n = "ramka_plytka_okragla_ramkowa_%s_v2.stl" % typ
        dodaj("03_Zrodla", W / "stl" / n, s58.get("stl/" + n), SUMY_R58.name)
        n = "uklad_gniazd_okragla_ramkowa_%s.json" % typ
        dodaj("03_Zrodla", W / "json" / n, s58.get("json/" + n), SUMY_R58.name)
    dodaj("03_Zrodla", ROOT / "R58_wdrozenie_zmiany.md", "-", "dokument")
    dodaj("03_Zrodla", SUMY_R58, "-", "sumy")
    if bledy:
        for b in bledy:
            print("BLAD: " + b)
        return 1
    czytaj = "\n".join([
        "Zamowienie - komplet okragly do ramki swietlnej (R58), paczka z %s" % a.data,
        "",
        "01_Drukarnia_PA12    - do drukarni (MJF/SLS PA12): 6 plytek okraglych n1-n6 po 1 szt., wkladka okragla 3 szt.,",
        "                       korpus W 1 szt., korpus P 1 szt., blat 2 szt. Ilosci, wykonczenie i koszty: R58_arkusz_zamowienia.md.",
        "02_Druk_wlasny_PETG  - druk wlasny FDM: pokrywka okragla 4 szt. (najpierw 1 sztuka probna), tulejka DC 2, podkladki po 8.",
        "03_Zrodla            - nie do druku: pliki bazowe plytek (wzorce), uklady gniazd JSON, opis zmiany R58.",
        "",
        "Plytki okragle n1-n6 leza TYLKO we wkladce okraglej z tej paczki (nie w ramka_wkladka_v2.stl) i tylko pod pokrywka okragla.",
        "Korpusy, blat, tulejka i podkladki to te same pliki co w pakiecie R59 (bez zmian).",
        "Tej paczki NIE laczyc z plytkami kwadratowymi n1-n6, ramka_wkladka_v2.stl ani ramka_pokrywka_v2.stl z zamowienia R59.",
        "",
        "Sprawdzenie: sha256sum -c SHA256SUMS_%s_R58.txt  (PowerShell: Get-FileHash <plik> -Algorithm SHA256)." % a.data,
        ""])
    pliki.append(("CZYTAJ.txt", czytaj.encode("ascii")))
    pliki.sort(key=lambda p: p[0])
    lista = "".join("%s *%s\n" % (sha(d), n) for n, d in pliki)
    nazwa_sum = "SHA256SUMS_%s_R58.txt" % a.data
    cel = Path(a.cel)
    cel.mkdir(parents=True, exist_ok=True)
    (cel / nazwa_sum).write_bytes(lista.encode("ascii"))
    zip_nazwa = "Zamowienie_komplet_okragly_R58_%s.zip" % a.data
    r, m, d = (int(x) for x in a.data.split("-"))
    with zipfile.ZipFile(cel / zip_nazwa, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for n, dane in pliki + [(nazwa_sum, lista.encode("ascii"))]:
            zi = zipfile.ZipInfo(n, date_time=(r, m, d, 12, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            z.writestr(zi, dane, compresslevel=9)
    zb = (cel / zip_nazwa).read_bytes()
    print("%s: %d plikow + plik sum, %d bajtow, SHA-256 %s" % (zip_nazwa, len(pliki), len(zb), sha(zb)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
