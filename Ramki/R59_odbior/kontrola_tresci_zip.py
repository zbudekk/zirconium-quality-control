# -*- coding: utf-8 -*-
"""Kontrola tresci ZIP-a pakietu przed publikacja (lista z przegladu bezpieczenstwa, 16.11.2026).

Uzycie: python kontrola_tresci_zip.py <ZIP> <katalog Prace_test (tylko odczyt)>
Nie wypisuje nazw z Prace_test ani znalezionych wartosci osobowych - tylko plik, rodzaj i liczbe.
"""
import io
import re
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

ZIP = Path(sys.argv[1])
PRACE = Path(sys.argv[2])
zf = zipfile.ZipFile(ZIP)
nazwy = [n for n in zf.namelist() if not n.endswith("/")]

# 1. struktura
gora = Counter(n.split("/")[1] if n.count("/") >= 2 else "(plik) " + n.split("/")[-1] for n in nazwy)
print("1. STRUKTURA:", dict(gora))
zakazane = [n for n in nazwy if re.search(r"(Prace_test|/\.git/|\.env$|/dane/|skan_|mapa_sciezek|mapa_projektow)", n)]
print("   zakazane wzorce w nazwach:", len(zakazane), zakazane[:5])

# fragmenty nazw zlecen (bez wypisywania)
TECH = {"crown", "bridge", "korona", "most", "mosty", "projekt", "projekty", "zlecenie", "exocad", "kopia", "nowy",
        "nowa", "dolny", "gorny", "lewy", "prawy", "zeby", "cyrkon", "cyrkonia", "html", "txt", "zip", "stl"}
frag = set()
for p in PRACE.rglob("*"):
    for s in re.split(r"[^A-Za-zÀ-ž]+", p.stem if p.is_file() else p.name):
        s = s.lower()
        if len(s) >= 4 and s not in TECH:
            frag.add(s)

TEKST = (".md", ".txt", ".json", ".py", ".js", ".sh", ".cmd", ".csv", ".html", ".toml")
wyniki = defaultdict(Counter)
for n in nazwy:
    b = zf.read(n)
    ext = Path(n).suffix.lower()
    if ext in TEKST:
        t = b.decode("utf-8", errors="replace")
        low = t.lower()
        for f in frag:
            if re.search(r"(?<![a-zà-ž])" + re.escape(f) + r"(?![a-zà-ž])", low):
                wyniki[n]["fragment nazwy zlecenia"] += 1
        wyniki[n]["sciezka Users\\<konto>"] += len(re.findall(r"[A-Za-z]:[\\/]+Users[\\/]+[A-Za-z0-9_.~-]+", t))
        wyniki[n]["e-mail"] += len(re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}", t))
        wyniki[n]["telefon"] += len(re.findall(r"(?<![\d.,])(?:\+48[ -]?)?\d{3}[ -]\d{3}[ -]\d{3}(?![\d.,])", t))
        wyniki[n]["11 cyfr (PESEL?)"] += len(re.findall(r"(?<![\d.,])\d{11}(?![\d.,])", t))
    elif ext == ".pdf":
        from pypdf import PdfReader
        r = PdfReader(io.BytesIO(b))
        meta = {k: str(v) for k, v in (r.metadata or {}).items()}
        print("3. PDF", n.split("/")[-1], "metadane:", meta)
        t = "\n".join((pg.extract_text() or "") for pg in r.pages)
        low = t.lower()
        for f in frag:
            if re.search(r"(?<![a-zà-ž])" + re.escape(f) + r"(?![a-zà-ž])", low):
                wyniki[n]["fragment nazwy zlecenia"] += 1
        wyniki[n]["sciezka Users\\<konto>"] += len(re.findall(r"[A-Za-z]:[\\/]+Users[\\/]+[A-Za-z0-9_.~-]+", t))
        wyniki[n]["e-mail"] += len(re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}", t))
    elif ext in (".jpg", ".jpeg", ".png"):
        try:
            from PIL import Image
            im = Image.open(io.BytesIO(b))
            ex = im.getexif()
            info = {k: v for k, v in im.info.items() if k not in ("dpi", "gamma", "srgb", "transparency")}
            if len(ex) or info:
                wyniki[n]["metadane obrazu (EXIF/tekst)"] += len(ex) + len(info)
        except Exception as e:  # noqa: BLE001
            wyniki[n]["obraz nieczytelny: " + type(e).__name__] += 1
    elif ext == ".blend":
        poczatek = b[:16]
        sciezki = re.findall(rb"[A-Za-z]:[\\/][^\x00\n\r\"<>|]{3,200}", b)
        users = [s for s in sciezki if re.search(rb"Users[\\/]", s)]
        print("4. BLEND", n.split("/")[-1], "naglowek:", poczatek[:12], "rozmiar", len(b), "sciezek bezwzglednych:", len(sciezki),
              "z Users\\:", len(users), "(skompresowany zstd - sciezki nieczytelne)" if poczatek[:4] == b"\x28\xb5\x2f\xfd" else "")

print("2./5. TRAFIENIA (plik: rodzaj = liczba; wartosci nie wypisywane):")
suma = Counter()
for n, c in sorted(wyniki.items()):
    c = {k: v for k, v in c.items() if v}
    if c:
        print("  ", n.split("/", 1)[1], c)
        suma.update(c)
print("RAZEM:", dict(suma), "| fragmentow nazw zlecen w porownaniu:", len(frag))
