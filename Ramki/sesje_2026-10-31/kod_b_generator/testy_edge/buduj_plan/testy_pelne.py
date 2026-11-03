# -*- coding: utf-8 -*-
"""
Pełne przebiegi narzedzia/buduj_plan_wdrozenia.py (z Chromium) na sztucznych .md w scratchpadzie.
Każdy przebieg dostaje --pdf i --html w scratchpadzie, więc NIC nie jest zapisywane w projekcie
(wyjątek: przypadek „bez --pdf” — uruchamiany na KOPII .md w scratchpadzie, PDF powstaje obok kopii).
Uruchomienie (z folderu Ramki):
    PYTHONUTF8=1 py -3.14 sesje_2026-10-31/kod_b_generator/testy_edge/buduj_plan/testy_pelne.py <katalog_scratchpad>
"""
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SCRIPT = ROOT / "narzedzia" / "buduj_plan_wdrozenia.py"
OUT = Path(sys.argv[1]).resolve()
OUT.mkdir(parents=True, exist_ok=True)
PY = ["py", "-3.14"]
ENV = dict(os.environ, PYTHONUTF8="1")


def run(name, md_text, extra=(), env=None, cwd=None, md_name=None, no_pdf_arg=False):
    d = OUT / name
    if d.exists():
        shutil.rmtree(d)
    d.mkdir()
    md = d / (md_name or "wejście — test ąęś.md")
    md.write_text(md_text, encoding="utf-8")
    args = PY + [str(SCRIPT), "--md", str(md)]
    if not no_pdf_arg:
        args += ["--pdf", str(d / "wyj.pdf"), "--html", str(d / "wyj.html")]
    args += list(extra)
    t0 = time.time()
    p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       env=env or ENV, cwd=cwd or str(d))
    dt = time.time() - t0
    files = sorted(f.name for f in d.iterdir())
    print(f"\n### {name}  (exit={p.returncode}, {dt:.1f}s)")
    print("pliki po przebiegu:", files)
    if p.stdout.strip():
        print("stdout:", p.stdout.strip()[:1500])
    if p.stderr.strip():
        err = p.stderr.strip().splitlines()
        print("stderr (ostatnie 6 linii):", "\n   ".join(err[-6:]))
    return p, d


BASE = "# Tytuł testowy\n\n27 października 2026 · Michał · wersja 9\n\n"

# A. pusty plik
run("A_pusty", "")

# B. plik spoza PROFILE — jaki tytuł/data na stronie tytułowej
run("B_spoza_profile", BASE + "## Jedyna sekcja\n\nTreść.\n")

# C. długi spis treści (> 1 strona) — czy numery stron są poprawne
md = BASE
for i in range(1, 46):
    md += f"## Sekcja numer {i}\n\n" + ("Akapit treści sekcji. " * 40) + "\n\n"
    md += f"### Podsekcja {i}.a\n\nTreść podsekcji.\n\n"
run("C_dlugi_spis", md)

# D. 'Przepływ poranny' bez akapitu (oczekiwany wyjątek w build_html)
run("D_poranny_bez_p", BASE + "## Przepływ poranny\n\n- lista\n")

# E. nagłówek z & i <
run("E_naglowek_znaki", BASE + "## Zakupy & druk <wersja>\n\nTreść.\n")

# F. uruchomienie z innego katalogu (cwd = C:\\) ze względną ścieżką --md
# (ścieżka względna liczona od cwd, nie od Ramki)
dF = OUT / "F_inny_cwd"
if dF.exists():
    shutil.rmtree(dF)
dF.mkdir()
(dF / "x.md").write_text(BASE + "## S\n\nT.\n", encoding="utf-8")
p = subprocess.run(PY + [str(SCRIPT), "--md", "x.md", "--pdf", str(dF / "x.pdf"), "--html", str(dF / "x.html")],
                   capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENV, cwd="C:\\")
print(f"\n### F_inny_cwd (cwd=C:\\, --md x.md względne)  exit={p.returncode}")
print("stderr:", "\n   ".join(p.stderr.strip().splitlines()[-3:]))

# G. brak Chromium (PLAYWRIGHT_BROWSERS_PATH wskazuje pusty katalog)
emp = OUT / "G_pusty_browsers"
emp.mkdir(exist_ok=True)
run("G_bez_chromium", BASE + "## S\n\nT.\n", env=dict(ENV, PLAYWRIGHT_BROWSERS_PATH=str(emp)))

# H. bez --pdf i --html na kopii .md o nazwie z „—” i polskimi znakami: gdzie ląduje PDF, czy zostaje .tmp.html
run("H_bez_pdf_arg", BASE + "## S\n\nT.\n", md_name="Zakupy i druk — kopia próbna ąż.md", no_pdf_arg=True)

# I. tabela z komórką > 600 znaków i komórką z | w backtickach, znaki specjalne
cell = "x" * 650
md = BASE + "## S\n\n| k | w |\n|---|---|\n| `a|b` | " + cell + " |\n| −5 ‑ ×3 ≥2 → | b |\n"
run("I_tabela_edge", md)

# J. nieistniejący plik --md
d = OUT / "J_brak_md"; d.mkdir(exist_ok=True)
p = subprocess.run(PY + [str(SCRIPT), "--md", str(d / "nie_ma.md"), "--pdf", str(d / "x.pdf")],
                   capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENV)
print(f"\n### J_brak_md exit={p.returncode}\nstderr: ", "\n   ".join(p.stderr.strip().splitlines()[-2:]))
print("pliki:", sorted(f.name for f in d.iterdir()))
