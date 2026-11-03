# -*- coding: utf-8 -*-
"""
Porównanie .md ↔ PDF dla narzedzia/buduj_plan_wdrozenia.py (audyt, tylko odczyt).
Uruchomienie (z folderu Ramki):
    PYTHONUTF8=1 py -3.14 sesje_2026-10-31/kod_b_generator/testy_edge/buduj_plan/porownaj_md_pdf.py <plik.md> <plik.pdf>
Sprawdza:
  1. czy każdy fragment treści .md (akapit, komórka tabeli, pozycja listy) występuje w tekście PDF,
  2. czy numery stron w spisie treści PDF zgadzają się ze stroną, na której nagłówek faktycznie stoi,
  3. czy nagłówek bieżący (prawy górny) na każdej stronie odpowiada sekcji,
  4. kolejność numerów rysunków „Rys. N.”,
  5. znaki specjalne (×, ≥, →, ‑, −) — czy przeszły do PDF w tej samej liczbie.
Niczego nie zapisuje poza stdout.
"""
import logging
import re
import sys
from pathlib import Path

import pdfplumber

logging.getLogger("pdfminer").setLevel(logging.ERROR)


def norm(s):
    s = s.replace("\u00ad", "")
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def strip_md_inline(s):
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"(?<!\*)\*(?!\*)(.+?)\*", r"\1", s)
    s = re.sub(r"`([^`]*)`", r"\1", s)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    s = s.replace("\\|", "|")
    return s


def md_chunks(md_text):
    """Zwraca listę (nr_linii, rodzaj, tekst) — fragmenty, które powinny być w PDF."""
    out = []
    para = []
    para_line = 0
    for i, raw in enumerate(md_text.splitlines(), 1):
        line = raw.rstrip()
        if not line.strip():
            if para:
                out.append((para_line, "akapit", strip_md_inline(" ".join(para))))
                para = []
            continue
        if line.startswith("#"):
            if para:
                out.append((para_line, "akapit", strip_md_inline(" ".join(para)))); para = []
            m = re.match(r"^(#+)\s*(.*)$", line)
            out.append((i, f"h{len(m.group(1))}", strip_md_inline(m.group(2))))
            continue
        if line.lstrip().startswith("|"):
            if para:
                out.append((para_line, "akapit", strip_md_inline(" ".join(para)))); para = []
            if re.match(r"^\s*\|[\s:\-|]+\|\s*$", line):
                continue
            cells = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
            for c in cells:
                if c:
                    out.append((i, "komórka", strip_md_inline(c)))
            continue
        m = re.match(r"^\s*(?:[-*+]|\d+\.)\s+(.*)$", line)
        if m:
            if para:
                out.append((para_line, "akapit", strip_md_inline(" ".join(para)))); para = []
            out.append((i, "lista", strip_md_inline(m.group(1))))
            continue
        if not para:
            para_line = i
        para.append(line.strip())
    if para:
        out.append((para_line, "akapit", strip_md_inline(" ".join(para))))
    return out


def main(md_path, pdf_path):
    md_text = Path(md_path).read_text(encoding="utf-8")
    with pdfplumber.open(str(pdf_path)) as pdf:
        pages = [(p.extract_text() or "") for p in pdf.pages]
    full = norm(" ".join(pages))
    full_nohyph = full.replace("- ", "")  # na wypadek dzielenia wyrazów na końcu wiersza

    print(f"PDF: {pdf_path}  stron: {len(pages)}")
    print(f"MD:  {md_path}  linii: {md_text.count(chr(10))+1}")

    # --- 1. fragmenty treści: każdy fragment .md musi być podciągiem słów (w kolejności)
    #        tekstu jednej strony lub dwóch sąsiednich stron (pdfplumber przeplata wiersze
    #        sąsiednich kolumn tabeli, ale kolejność słów w obrębie komórki zachowuje)
    def toks(s):
        return [w.strip("„”\"'()[]{}.,;:") for w in norm(s).split(" ")]

    def is_subseq(small, big):
        it = iter(big)
        return all(any(w == x for x in it) for w in small)

    page_toks = [toks(p) for p in pages]
    pair_toks = [page_toks[i] + page_toks[i + 1] for i in range(len(page_toks) - 1)]
    chunks = md_chunks(md_text)
    missing = []
    for ln, kind, txt in chunks:
        t = norm(txt)
        if len(t) < 4:
            continue
        if t in full or t in full_nohyph:
            continue
        small = [w for w in toks(t) if w]
        if any(is_subseq(small, pt) for pt in page_toks) or any(is_subseq(small, pt) for pt in pair_toks):
            continue
        missing.append((ln, kind, txt))
    print(f"\n== 1. Fragmenty .md nieodnalezione w PDF (ani jako podciąg słów na stronie): {len(missing)} z {len(chunks)}")
    for ln, kind, txt in missing:
        print(f"  md:{ln} [{kind}] {txt[:200]}")

    # --- 2. spis treści vs rzeczywiste strony nagłówków
    toc_page_idx = next((i for i, p in enumerate(pages) if p.lstrip().startswith("Spis treści") or "\nSpis treści" in p), None)
    toc_rows = []
    if toc_page_idx is not None:
        for line in pages[toc_page_idx].splitlines():
            m = re.match(r"^(.*\S)\s+(\d+)$", line)
            if m and not line.startswith("Stanowisko kontroli") and not re.match(r"^\d+ / \d+$", line):
                toc_rows.append((m.group(1), int(m.group(2))))
    print(f"\n== 2. Spis treści: {len(toc_rows)} wierszy (strona {toc_page_idx + 1 if toc_page_idx is not None else '?'})")
    bad = 0
    for text, pg in toc_rows:
        if text == "Spis treści":
            continue
        found = None
        for i in range(toc_page_idx + 1, len(pages)):
            lines = [norm(l) for l in pages[i].splitlines()]
            # nagłówek stoi w osobnym wierszu (nie w nagłówku bieżącym, który ma prefiks tytułu)
            if any(l == norm(text) for l in lines[1:]):
                found = i + 1
                break
        if found != pg:
            bad += 1
            print(f"  ROZBIEŻNOŚĆ: „{text}” spis={pg} faktycznie={found}")
    print(f"  rozbieżności: {bad}")

    # --- 3. nagłówek bieżący na każdej stronie
    print("\n== 3. Nagłówek bieżący (pierwszy wiersz strony) vs sekcja")
    h2 = [(pg, t) for t, pg in toc_rows if re.match(r"^\d+\. ", t)]
    odd = 0
    for i in range(2, len(pages)):
        first = pages[i].splitlines()[0] if pages[i].strip() else ""
        cur = None
        for pg, t in h2:
            if pg < i + 1:
                cur = t
        starts_here = [t for pg, t in h2 if pg == i + 1]
        tail = first.split("wersja")[-1] if "wersja" in first else first
        if cur and cur not in first and not (starts_here and starts_here[0] in first):
            odd += 1
            print(f"  str. {i+1}: nagłówek „{tail.strip()[:70]}”, oczekiwano „{cur}” (lub zaczynająca się tu {starts_here})")
        elif starts_here and cur and cur in first:
            print(f"  UWAGA str. {i+1}: sekcja „{starts_here[0]}” zaczyna się na tej stronie, nagłówek bieżący pokazuje poprzednią „{cur}”")
    print(f"  nieoczekiwanych: {odd}")

    # --- 4. kolejność rysunków
    rys = [int(m) for m in re.findall(r"Rys\. (\d+)\.", " ".join(pages))]
    print(f"\n== 4. Kolejność rysunków w PDF: {rys}  -> {'rosnąca' if rys == sorted(rys) else 'NIE rosnąca'}")

    # --- 5. znaki specjalne (bez nagłówka h1 i wiersza metadanych, których w PDF nie ma)
    body = "\n".join(md_text.splitlines()[3:])
    print("\n== 5. Znaki specjalne: md vs PDF (liczba wystąpień)")
    for ch in "×≥≤→‑−±µ³ø·—–…°":
        a = body.count(ch)
        b = " ".join(pages).count(ch)
        flag = "" if a <= b else "  <-- MNIEJ w PDF"
        print(f"  {ch} U+{ord(ch):04X}: md={a} pdf={b}{flag}")
    # znaki zastępcze
    for ch in "\ufffd\u25a1":
        n = " ".join(pages).count(ch)
        if n:
            print(f"  ZNAK ZASTĘPCZY U+{ord(ch):04X} w PDF: {n}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
