# -*- coding: utf-8 -*-
"""R59 testy koncowe koordynatora T3c, T11, T13, T14 (MSI, tylko odczyt worktree).

Uzycie: python t11_t13_t14.py <katalog glowny worktree> <katalog Prace_test (tylko odczyt)> <ZIP calosci>
Nie wypisuje nazw plikow ani folderow z Prace_test - tylko liczby trafien.
"""
import hashlib
import io
import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path

from pypdf import PdfReader

TOP = Path(sys.argv[1])
PRACE = Path(sys.argv[2])
ZIP_CALOSCI = Path(sys.argv[3])
R = TOP / "Ramki"
WYNIKI = []


def zapisz(test, nazwa, ok, opis):
    WYNIKI.append((test, ok))
    print("%-4s %-60s %s  %s" % (test, nazwa, "OK  " if ok else "FAIL", opis), flush=True)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def git(*a):
    return subprocess.run(["git", "-C", str(TOP), *a], capture_output=True, text=True, encoding="utf-8").stdout


# --- T3c: sha256sum -c w Ramki_pakiet -------------------------------------------------------------
pak = R / "Ramki_pakiet"
sumy = sorted(pak.glob("SHA256SUMS_*_R59.txt"))
ok = 0
zle = []
linie = sumy[0].read_text(encoding="utf-8").splitlines() if sumy else []
for l in linie:
    m = re.match(r"^([0-9a-f]{64}) [ *](.+)$", l)   # format sha256sum: "<suma> *<sciezka>" albo "<suma>  <sciezka>"
    h, p = (m.group(1), m.group(2)) if m else ("", l)
    plik = pak / p
    if plik.is_file() and sha(plik) == h:
        ok += 1
    else:
        zle.append(p)
pliki_pakietu = [p for p in pak.rglob("*") if p.is_file()]
zapisz("T3c", "sha256sum -c w Ramki_pakiet", bool(linie) and ok == len(linie) and len(pliki_pakietu) == len(linie) + 1,
       "plik sum %s: %d/%d OK, plikow w pakiecie %d (= sumy + plik sum)" % (sumy[0].name if sumy else "BRAK", ok, len(linie), len(pliki_pakietu)))

# --- T11: dokumenty i PDF --------------------------------------------------------------------------
dok = sorted(R.glob("Stanowisko kontroli cyrkonii*plan wdrozenia v2.md")) + sorted(R.glob("Zakupy i druk*.md")) + sorted(R.glob("Budowa ramki*.md"))
STARE = ["18 + 2", "31 + 2", "7 \u00d7 \u00f89", "18 \u00d7 \u00f87,5", "7 \u00d7 \u00f810", "5 \u00d7 \u00f815", "6 \u00d7 \u00f812,5", "dwie rynienki", "2 rynienki",
         "59,31", "60,87", "49,01", "50,56", "515d32d3", "a8d07cbe", "c4c8a18d", "a87bc6c5"]
HIST = re.compile(r"by\u0142o|By\u0142o|by\u0142 |poprzedni|Poprzedni|dawn|stary|stare|starego|starym|zamiast|R54|R55|R56|R57|\u2192|->|historia|wcze\u015bniej", re.I)
for p in dok + [R / "plan_ramki_v2.md", R / "protokol_weryfikacji_v2.md"]:
    t = p.read_text(encoding="utf-8").splitlines()
    trafien = 0
    biezace = []
    naglowek = ""   # wiersz naglowka biezacej tabeli Markdown (tabela "Bylo | Jest" = historia)
    for i, l in enumerate(t, 1):
        if l.startswith("|"):
            if i >= 2 and not t[i - 2].startswith("|"):
                naglowek = l
        else:
            naglowek = ""
        if any(s in l for s in STARE):
            trafien += 1
            if not HIST.search(l) and not (l.startswith("|") and HIST.search(naglowek)):
                biezace.append(i)
    zapisz("T11", p.name[:60], not biezace, "linii ze starymi liczbami %d, w tym bez znacznika historii %d %s" % (trafien, len(biezace), biezace[:8]))
for md in dok:
    pdf = md.with_suffix(".pdf")
    if not pdf.exists():
        zapisz("T11", pdf.name[:60], False, "brak PDF")
        continue
    r = PdfReader(str(pdf))
    tekst = "\n".join((pg.extract_text() or "") for pg in r.pages)
    nowszy = pdf.stat().st_mtime >= md.stat().st_mtime
    w_git = git("log", "-1", "--format=%h", "--", str(pdf.relative_to(TOP)))
    starych = sum(tekst.count(s) for s in ["31 gniazd:", "18 \u00d7 \u00f87,5, 7 \u00d7 \u00f810"])
    zapisz("T11", pdf.name[:60], nowszy and "R59" in tekst and "23 gniazda" in tekst,
           "stron %d, nowszy niz .md %s, R59 %d, '23 gniazda' %d, '1 rynienka' %d, commit %s" % (
               len(r.pages), nowszy, tekst.count("R59"), tekst.count("23 gniazda"), tekst.count("1 rynienka"), w_git.strip()))

# --- T13: 3 ZIP + ZIP calosci ----------------------------------------------------------------------
fragmenty = set()
TECH = {"crown", "bridge", "korona", "most", "mosty", "projekt", "projekty", "zlecenie", "exocad", "kopia", "nowy", "nowa",
        "dolny", "gorny", "lewy", "prawy", "zeby", "zab", "cyrkon", "cyrkonia"}
for p in PRACE.rglob("*"):
    for s in re.split(r"[^A-Za-z\u00c0-\u017e]+", p.stem if p.is_file() else p.name):
        s = s.lower()
        if len(s) >= 4 and s not in TECH and s not in ("_cad", "cad"):
            fragmenty.add(s)
fragmenty -= {"stl", "html", "txt", "zip"}
dw = TOP / "Ramki_do_wgrania"
czesci = sorted(dw.glob("Ramki_pakiet_*_R59_cz*.zip"))
wpisy_razem = []
for z in czesci + [ZIP_CALOSCI]:
    zf = zipfile.ZipFile(z)
    bad = zf.testzip()
    nazwy = [n for n in zf.namelist() if not n.endswith("/")]
    wpisy_razem += nazwy if z != ZIP_CALOSCI else []
    nieascii = sum(1 for n in nazwy if not n.isascii())
    traf = sum(1 for n in nazwy for f in fragmenty if f in n.lower())
    rozmiar = z.stat().st_size
    limit = 10_000_000 if z != ZIP_CALOSCI else 2 * 1024 ** 3
    zapisz("T13", z.name[:60], bad is None and rozmiar < limit and nieascii == 0 and traf == 0,
           "rozmiar %d B (limit %d), CRC %s, plikow %d, nazw nie-ASCII %d, trafien fragmentow nazw zlecen %d" % (
               rozmiar, limit, "OK" if bad is None else bad, len(nazwy), nieascii, traf))
# zawartosc 3 ZIP = pakiet, sumy zgodne
glowny = {n.split("/", 1)[0] for n in wpisy_razem}
wzgl = sorted(n.split("/", 1)[1] for n in wpisy_razem)
w_pakiecie = sorted(str(p.relative_to(pak)).replace(os.sep, "/") for p in pliki_pakietu)
zgodne = 0
for z in czesci:
    zf = zipfile.ZipFile(z)
    for n in zf.namelist():
        if n.endswith("/"):
            continue
        rel = n.split("/", 1)[1]
        if hashlib.sha256(zf.read(n)).hexdigest() == sha(pak / rel):
            zgodne += 1
zapisz("T13", "3 ZIP razem = Ramki_pakiet", wzgl == w_pakiecie and len(glowny) == 1 and zgodne == len(wzgl),
       "katalog glowny %s, plikow %d (pakiet %d), bajtowo zgodnych %d, kazdy plik w dokladnie 1 ZIP: %s" % (
           sorted(glowny), len(wzgl), len(w_pakiecie), zgodne, len(wzgl) == len(set(wzgl))))
instr = sorted(dw.glob("INSTRUKCJA_PAKIET_*_R59.md"))
t = instr[0].read_text(encoding="utf-8") if instr else ""
zapisz("T13", "instrukcja pakietu", bool(t) and "23 gniazda" in t and "18 gniazd" in t and all(c.name in t for c in czesci),
       "plik %s, nazwy 3 ZIP w tresci %d/3, linii %d" % (instr[0].name if instr else "BRAK", sum(c.name in t for c in czesci), t.count("\n")))
na_serwer = sorted(dw.glob("NA_SERWER_*_R59.md"))
tn = na_serwer[0].read_text(encoding="utf-8") if na_serwer else ""
zapisz("T13", "NA_SERWER vs ZIP calosci", sha(ZIP_CALOSCI) in tn and str(ZIP_CALOSCI.stat().st_size) in tn and ZIP_CALOSCI.name in tn,
       "SHA i rozmiar ZIP calosci w pliku: %s / %s" % (sha(ZIP_CALOSCI) in tn, str(ZIP_CALOSCI.stat().st_size) in tn))
print("T13 fragmentow nazw z Prace_test do porownania: %d (nie wypisywane)" % len(fragmenty))

# --- T14: higiena repo -----------------------------------------------------------------------------
diff = [l.split("\t") for l in git("diff", "--name-status", "origin/main...HEAD").splitlines() if l]
nazwy = [d[-1] for d in diff]
stl_poza = [n for n in nazwy if n.lower().endswith(".stl") and not (n.startswith("Ramki/Ramki_pakiet/") or n.startswith("Ramki/stanowisko/modele_plytek/"))]
krawedz = [n for n in nazwy if "raporty/testy_krawedz" in n]
WYJATKI = ("Ramki/archiwum/", "/modele_plytek/", "Ramki/wyniki_v2/", "Ramki/R59_szkice/parametry_wariant_", "Ramki/Ramki_pakiet/",
           "Ramki_do_wgrania/", "Ramki/wyniki_model_R59/", "Ramki/R59_arkusz_zamowienia", "Ramki/ramka_3d.html", "Ramki/animacja_ramki.html",
           "Stanowisko kontroli", "Zakupy i druk", "Budowa ramki", "Ramki/00_NADZOR_STAN.md", "Ramki/plan_ramki_v2.md",
           "Ramki/protokol_weryfikacji_v2.md", "Ramki/00_PRZEPLYW_I_BRAMKI.md", "Ramki/parametry.json", "Ramki/ramka_generator.py",
           "Ramki/stanowisko/", "Ramki/narzedzia/buduj_plan_wdrozenia.py", "Ramki/narzedzia/zbuduj_pakiet_R59.sh", "Ramki/narzedzia/zbuduj_model_offline.js")
nowe_nieascii = []
sterujace = []
for st, n in [(d[0], d[-1]) for d in diff]:
    p = TOP / n
    if not p.is_file() or p.suffix.lower() in (".stl", ".zip", ".pdf", ".png", ".jpg", ".blend"):
        continue
    b = p.read_bytes()
    if any(c < 32 and c not in (9, 10, 13) for c in b):
        sterujace.append(n)
    if st == "A" and not n.startswith(WYJATKI) and any(c > 127 for c in b):
        nowe_nieascii.append(n)
status = git("status", "--short").strip()
zapisz("T14", "git status czysty", status == "", "zmian niezatwierdzonych: %d" % (len(status.splitlines()) if status else 0))
zapisz("T14", "pliki w diffie origin/main...HEAD", True, "plikow %d (A %d, M %d, D %d)" % (
    len(diff), sum(d[0] == "A" for d in diff), sum(d[0] == "M" for d in diff), sum(d[0] == "D" for d in diff)))
zapisz("T14", "STL poza dozwolonymi katalogami", not stl_poza, "%d %s" % (len(stl_poza), stl_poza[:3]))
zapisz("T14", "nic w raporty/testy_krawedz", not krawedz, "%d" % len(krawedz))
zapisz("T14", "nowe pliki nie-ASCII poza wyjatkami", not nowe_nieascii, "%d %s" % (len(nowe_nieascii), nowe_nieascii[:5]))
zapisz("T14", "znaki sterujace w plikach tekstowych", not sterujace, "%d %s" % (len(sterujace), sterujace[:5]))
print("RAZEM: %d/%d OK" % (sum(1 for _, o in WYNIKI if o), len(WYNIKI)))
sys.exit(0 if all(o for _, o in WYNIKI) else 1)
