# -*- coding: utf-8 -*-
"""
Edge case'y parsera narzedzia/buduj_plan_wdrozenia.py — bez Chromium.
Importuje moduł i woła build_html() na sztucznych fragmentach Markdown.
Uruchomienie (z folderu Ramki):
    PYTHONUTF8=1 py -3.14 sesje_2026-10-31/kod_b_generator/testy_edge/buduj_plan/testy_parsera.py
Niczego nie zapisuje w projekcie (tylko stdout). Nie modyfikuje skryptu — podmienia
wyłącznie atrybuty zaimportowanego modułu w pamięci (JSON_DIR), by zasymulować brak JSON.
"""
import importlib.util
import io
import sys
import traceback
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]  # .../Ramki
SCRIPT = ROOT / "narzedzia" / "buduj_plan_wdrozenia.py"
spec = importlib.util.spec_from_file_location("bpw", SCRIPT)
bpw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bpw)

from bs4 import BeautifulSoup  # noqa: E402

results = []


def case(name, md, check=None, **kw):
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            html, toc = bpw.build_html(md, **kw)
        soup = BeautifulSoup(html, "html.parser")
        content = soup.find("section", class_="content")
        info = check(soup, content, toc, html) if check else "ok"
        status = "OK"
    except Exception as e:  # noqa: BLE001
        info = f"WYJĄTEK {type(e).__name__}: {e}"
        status = "BŁĄD"
    out = buf.getvalue().strip()
    results.append((name, status, info, out))
    print(f"[{status}] {name}: {info}" + (f"  | stdout: {out}" if out else ""))


# 1. pusty plik
case("pusty .md", "", lambda s, c, t, h: f"toc={len(t)} content='{c.get_text(strip=True)[:40]}'")

# 2. tylko h1 i metadane
case("tylko h1 + metadane", "# Tytuł\n\n27 października 2026 · Michał · wersja 2\n",
     lambda s, c, t, h: f"toc={len(t)}, treść='{c.get_text(strip=True)}'")

# 3. nagłówek bez spacji
case("nagłówek bez spacji ##Tytuł", "# T\n\n##Bez spacji\n\ntekst\n",
     lambda s, c, t, h: f"toc={len(t)}, h2={[x.get_text() for x in c.find_all('h2')]}, p={[x.get_text() for x in c.find_all('p')]}")

# 4. h3 przed pierwszym h2
case("h3 przed h2", "# T\n\n### Pod\n\ntekst\n\n## Sekcja\n",
     lambda s, c, t, h: f"toc={t}")

# 5. tabela bez wiersza separatora
case("tabela bez separatora", "# T\n\n## S\n\n| a | b |\n| 1 | 2 |\n",
     lambda s, c, t, h: f"tabel={len(c.find_all('table'))}, p={[x.get_text() for x in c.find_all('p')]}")

# 6. komórka z | w backtickach
case("komórka z `a|b`", "# T\n\n## S\n\n| k | w |\n|---|---|\n| x | `a|b` |\n",
     lambda s, c, t, h: f"komórki wiersza 2: {[td.get_text() for td in c.find_all('tr')[1].find_all('td')]}")

# 6b. komórka z \| (zalecane w GFM)
case("komórka z `a\\|b`", "# T\n\n## S\n\n| k | w |\n|---|---|\n| x | `a\\|b` |\n",
     lambda s, c, t, h: f"komórki wiersza 2: {[td.get_text() for td in c.find_all('tr')[1].find_all('td')]}")

# 7. wiersz tabeli z mniejszą liczbą komórek niż nagłówek
case("wiersz krótszy niż nagłówek", "# T\n\n## S\n\n| a | b | c |\n|---|---|---|\n| 1 |\n| 1 | 2 | 3 | 4 |\n",
     lambda s, c, t, h: f"colgroup={[col['style'] for col in c.find_all('col')]}, wiersze={[len(r.find_all('td')) for r in c.find_all('tr')[1:]]}")

# 8. tabela tylko z nagłówkiem
case("tabela tylko nagłówek", "# T\n\n## S\n\n| a | b | c |\n|---|---|---|\n",
     lambda s, c, t, h: f"tabel={len(c.find_all('table'))}, class={c.find('table').get('class')}")

# 9. lista zagnieżdżona w ramce
case("lista zagnieżdżona po 'Uwaga:'", "# T\n\n## S\n\nUwaga: lista poniżej:\n\n- a\n  - a1\n  - a2\n- b\n\nAkapit po.\n",
     lambda s, c, t, h: f"callout zawiera ul={c.find('div', class_='callout').find('ul') is not None}, li={len(c.find('div', class_='callout').find_all('li'))}, akapit po w callout={'Akapit po' in c.find('div', class_='callout').get_text()}")

# 10. 'Uwaga:' wewnątrz luźnej listy (p w li)
case("'Uwaga:' w luźnej liście", "# T\n\n## S\n\n- pierwszy\n\n- Uwaga: drugi\n\n- trzeci\n",
     lambda s, c, t, h: f"callout w li={c.find('li').find_next('div', class_='callout') is not None and c.find('div', class_='callout').parent.name == 'li'}")

# 11. nagłówek z formatowaniem inline
case("nagłówek z **bold** i `kod`", "# T\n\n## Sekcja **ważna** `kod`\n\ntekst\n",
     lambda s, c, t, h: f"h2 html={str(c.find('h2'))}")

# 12. nagłówek ze znakami < & >
case("nagłówek z < & >", "# T\n\n## A < B & C > D\n\ntekst\n",
     lambda s, c, t, h: f"toc wiersz={s.find('span', class_='toc-text')}, h2={c.find('h2')}")

# 13. akapit '(schemat w wersji PDF)' z linkiem (p.string = ... niszczy markup)
case("'(schemat w wersji PDF)' z linkiem w akapicie", "# T\n\n## S\n\nZobacz [link](http://x) i **bold** (schemat w wersji PDF)\n",
     lambda s, c, t, h: f"p={str(c.find('p'))}")

# 14. 'Przepływ poranny' bez akapitu po nagłówku
case("h2 'Przepływ poranny' bez akapitu", "# T\n\n## Przepływ poranny\n\n- lista\n",
     lambda s, c, t, h: f"figure={c.find('figure') is not None}")

# 15. 'B. Ramka świetlna' bez akapitu po nagłówku
case("h3 'B. Ramka świetlna' bez akapitu", "# T\n\n## Załączniki\n\n### B. Ramka świetlna\n\n| a |\n|---|\n| 1 |\n",
     lambda s, c, t, h: f"figure={c.find('figure') is not None}")

# 16. 'Układ gniazd (rysunki w wersji PDF;' bez JSON — podmiana JSON_DIR
_orig = bpw.JSON_DIR
bpw.JSON_DIR = Path("C:/nie_ma_takiego_katalogu")
case("brak JSON gniazd (JSON_DIR nieistniejący)", "# T\n\n## Załączniki\n\n### A. Płytka\n\nUkład gniazd (rysunki w wersji PDF; reszta):\n\n- a\n",
     lambda s, c, t, h: f"figure={len(c.find_all('figure'))}, akapit='{c.find('p').get_text()}'")
bpw.JSON_DIR = _orig

# 17. JSON jest, ale bez klucza (symulacja: plik w scratchpadzie)
import json, tempfile  # noqa: E402
tmpd = Path(tempfile.mkdtemp(prefix="bpw_json_"))
(tmpd / "uklad_gniazd_wieczorna.json").write_text(json.dumps({"sockets": []}), encoding="utf-8")
(tmpd / "uklad_gniazd_poranna.json").write_text(json.dumps({"sockets": []}), encoding="utf-8")
bpw.JSON_DIR = tmpd
case("JSON gniazd bez kluczy notch/markers", "# T\n\n## Załączniki\n\n### A. Płytka\n\nUkład gniazd (rysunki w wersji PDF; reszta):\n\n- a\n",
     lambda s, c, t, h: f"figure={len(c.find_all('figure'))}")
bpw.JSON_DIR = _orig

# 18. checklista D z zagnieżdżoną listą i formatowaniem
case("checklista D z bold i podlistą", "# T\n\n## Załączniki\n\n### D. Checklista dnia (wieczór)\n\n- **Krok** jeden\n  - pod\n- dwa\n",
     lambda s, c, t, h: f"table.checklist={c.find('table', class_='checklist') is not None}, wiersze={len(c.find('table', class_='checklist').find_all('tr'))-1}, td2={str(c.find('table', class_='checklist').find_all('td')[1])}")

# 19. checklista D, ale po nagłówku akapit zamiast listy
case("checklista D z akapitem przed listą", "# T\n\n## Załączniki\n\n### D. Checklista dnia (wieczór)\n\nWstęp.\n\n- a\n- b\n",
     lambda s, c, t, h: f"table.checklist={c.find('table', class_='checklist') is not None}")

# 20. h2 bezpośrednio po h2 (sieroty / keep)
case("h2 po h2, h3 po h2", "# T\n\n## A\n\n## B\n\n### B1\n\ntekst\n",
     lambda s, c, t, h: f"keep divs={[k.get_text(' ', strip=True)[:30] for k in c.find_all('div', class_='keep')]}")

# 21. nagłówek na końcu pliku
case("nagłówek na końcu pliku", "# T\n\n## A\n\ntekst\n\n## B\n",
     lambda s, c, t, h: f"toc={len(t)}")

# 22. komórka liczbowa — NUM_RE
import re  # noqa: E402
samples = ["2026", "ok. 20–25 tys. zł", "3 × 2 (M3 × 8)", "≥ 100 cm", "1.", "12/2026", "40–70 °C", "—", "5 V / 4 A", "0,3", "R50-1", "A4", "2 szt. (opcja)", "24 gniazda"]
print("[INFO] NUM_RE:", {s: bool(bpw.NUM_RE.match(s)) for s in samples})

# 23. akapit-zapowiedź z dwukropkiem + tabela > 6 wierszy
case("zapowiedź ':' + duża tabela", "# T\n\n## S\n\nDecyzje:\n\n| a | b |\n|---|---|\n" + "| 1 | 2 |\n" * 8,
     lambda s, c, t, h: f"p.lead={c.find('p', class_='lead') is not None}, keep={len(c.find_all('div', class_='keep'))}")

# 24. 'Rozstrzygnięte' bez dwukropka jako prefiks zwykłego zdania
case("'Rozstrzygnięte' prefiks zdania", "# T\n\n## S\n\nRozstrzygnięte sprawy nie wracają.\n",
     lambda s, c, t, h: f"callout={c.find('div', class_='callout') is not None}, label={c.find('div', class_='callout-label').get_text() if c.find('div', class_='callout-label') else None}")

# 25. HTML inline w md (commonmark html: true)
case("HTML inline <b>, <script>", "# T\n\n## S\n\n<b>pogrubione</b> i <script>alert(1)</script>\n",
     lambda s, c, t, h: f"script w HTML={'<script>' in h}")

# 26. obrazek względny
case("obrazek ![](rys.png)", "# T\n\n## S\n\n![opis](rys.png)\n",
     lambda s, c, t, h: f"img src={c.find('img')['src'] if c.find('img') else None} (względem HTML tymczasowego, nie .md)")

# 27. blok kodu — czy jest CSS dla pre/code
case("blok kodu ```", "# T\n\n## S\n\n```\nC:\\Windows\\Fonts\\segoeui.ttf\n```\n",
     lambda s, c, t, h: f"pre={c.find('pre') is not None}, css pre/code={'pre' in h.split('<style>')[1].split('</style>')[0]}")

# 28. długi nagłówek (nowrap w spisie treści)
long_h = "## " + "Bardzo długi nagłówek sekcji, który na pewno nie zmieści się w jednym wierszu spisu treści na stronie A4 " * 2
case("nagłówek 200+ znaków", "# T\n\n" + long_h + "\n\ntekst\n",
     lambda s, c, t, h: f"toc-text nowrap w CSS={'.toc-text {{ white-space: nowrap' in h or 'white-space: nowrap' in h}, dł={len(t[0][1])}")

# 29. tabela 'wide' (landscape nigdy nie przekazywane)
big = "| a | b | c | d | e |\n|---|---|---|---|---|\n" + ("| " + " | ".join(["x" * 200] * 5) + " |\n") * 5
case("tabela 5 kolumn > 4000 znaków (landscape=False domyślnie)", "# T\n\n## S\n\n" + big,
     lambda s, c, t, h: f"class={c.find('table').get('class')}")

print("\nPodsumowanie:", sum(1 for r in results if r[1] == "BŁĄD"), "wyjątków z", len(results), "przypadków")
