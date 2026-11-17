"""symulator_skanera - wrzuca sztuczne skany do folderu tak, jak robilby to program skanera (paczka E3-A2).

Po co: skanera jeszcze nie ma, a modul ``scanner`` (obserwacja folderu) i ``silnik`` (analiza w osobnym procesie) trzeba
zbudowac i zmierzyc. Symulator zapisuje pliki W KAWALKACH z przerwami (zapis trwa np. 1-5 s), kilka naraz albo co zadany
odstep, i dorzuca pliki zle: uciety, pusty, nie-STL, z niezgodnym naglowkiem, za krotki, STL tekstowy, inne rozszerzenie.
To NIE jest opis prawdziwego skanera: nazwy plikow (``--wzor-nazwy``), sposob zapisu (``--tryb``) i czasy sa parametrami.

Uzycie (z katalogu stanowisko/):
    py -3.12 narzedzia/symulator_skanera.py --folder FOLDER [--zrodla SKAN.stl|KATALOG ...] [--ile N] [--czas 1 5]
        [--kawalki 5 20] [--rownolegle 4] [--odstep 0] [--zle uciety pusty ...] [--seed 0] [--wzor-nazwy "skan_{nr:04d}.stl"]
        [--tryb wprost|dopisywanie|tymczasowy] [--dziennik PLIK.json]
        [--pomiar [--stabilizacja-ms 300] [--odrzuc-po 5]]                 obserwuj folder modulem scanner i policz opoznienia
        [--analiza --projekty FOLDER ... [--wyjscie FOLDER] [--ustawienia PLIK]]   dodatkowo analizuj kazdy skan silnikiem

Bez ``--zrodla`` symulator sam tworzy male poprawne pliki binarnego STL (losowe trojkaty - dobre do proby obserwatora,
nie do analizy). Z ``--pomiar`` wypisuje liczniki (zdarzen / zapisow, ile zdarzen przed koncem zapisu, mediana opoznienia,
odrzucenia z powodami) i konczy kodem 0 tylko wtedy, gdy kazdy dobry plik dal dokladnie jedno zdarzenie po koncu zapisu,
a kazdy zly - zero zdarzen i wpis z powodem. Z ``--analiza`` dochodza wyniki silnika (czas od konca zapisu do startu
analizy, czas plytki, statusy gniazd) i pliki ``<skan>_wynik.json`` w ``--wyjscie``.

Funkcje dla testow: ``sztuczny_stl``, ``zly_plik``, ``zapisz_jak_skaner``, ``symuluj``, ``statystyki``.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import random
import statistics
import struct
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

RODZAJE_ZLYCH = ("uciety", "pusty", "nie_stl", "zly_naglowek", "za_krotki", "stl_tekstowy", "inne_rozszerzenie")
TRYBY = ("wprost", "dopisywanie", "tymczasowy")
BLOK = 1024 * 1024


def skrot16(dane: bytes) -> str:
    return hashlib.sha256(dane).hexdigest()[:16]


def sztuczny_stl(trojkaty: int = 500, seed: int = 0) -> bytes:
    """Poprawny binarny STL z losowymi trojkatami (rozmiar = 84 + 50 x liczba trojkatow). Naglowek nie zaczyna sie od "solid"."""
    rng = random.Random(seed)
    cz = [f"sztuczny skan symulatora, seed {seed}".encode("ascii").ljust(80, b" ")[:80], struct.pack("<I", trojkaty)]
    for _ in range(trojkaty):
        x, y, z = rng.uniform(-50, 50), rng.uniform(-50, 50), rng.uniform(0, 10)
        w = [(x + rng.uniform(-0.2, 0.2), y + rng.uniform(-0.2, 0.2), z + rng.uniform(-0.2, 0.2)) for _ in range(3)]
        cz.append(struct.pack("<12fH", 0.0, 0.0, 1.0, *w[0], *w[1], *w[2], 0))
    return b"".join(cz)


def zly_plik(rodzaj: str, dobry: bytes) -> bytes:
    """Zawartosc pliku zlego danego rodzaju, zrobiona z poprawnego binarnego STL ``dobry``."""
    if rodzaj == "uciety":
        return dobry[: max(85, int(len(dobry) * 0.6))]
    if rodzaj == "pusty":
        return b""
    if rodzaj == "nie_stl":
        return b"To nie jest plik STL, tylko zwykly tekst zapisany z rozszerzeniem stl.\r\n" * 8
    if rodzaj == "zly_naglowek":
        n = struct.unpack("<I", dobry[80:84])[0]
        return dobry[:80] + struct.pack("<I", n + 7) + dobry[84:]
    if rodzaj == "za_krotki":
        return dobry[:40]
    if rodzaj == "stl_tekstowy":
        sciana = "facet normal 0 0 1\n outer loop\n  vertex 0 0 0\n  vertex 1 0 0\n  vertex 0 1 0\n endloop\nendfacet\n"
        return ("solid symulator\n" + sciana * 6 + "endsolid symulator\n").encode("ascii")
    if rodzaj == "inne_rozszerzenie":
        return dobry
    raise ValueError(f"rodzaj pliku zlego: {rodzaj!r} (dozwolone: {', '.join(RODZAJE_ZLYCH)})")


def _kawalki(zrodlo, ile: int):
    """Kolejne kawalki zawartosci (``bytes`` albo plik) - ``ile`` mniej wiecej rownych czesci."""
    if isinstance(zrodlo, (bytes, bytearray)):
        n = len(zrodlo)
        krok = max(1, -(-n // ile))
        for i in range(0, n, krok):
            yield bytes(zrodlo[i:i + krok])
        return
    n = os.stat(zrodlo).st_size
    krok = max(1, -(-n // ile))
    with open(zrodlo, "rb") as f:
        while True:
            blok = f.read(krok)
            if not blok:
                return
            yield blok


def zapisz_jak_skaner(zrodlo, cel, czas_s: float = 1.0, kawalki: int = 10, tryb: str = "wprost", trzymaj_s: float = 0.0) -> dict:
    """Zapisuje ``zrodlo`` (``bytes`` albo sciezka pliku) do ``cel`` w ``kawalki`` czesciach rozlozonych na ``czas_s`` sekund.

    ``tryb``: ``wprost`` - plik otwarty przez caly zapis; ``dopisywanie`` - plik zamykany po kazdym kawalku;
    ``tymczasowy`` - zapis do ``<cel>.tmp`` i zmiana nazwy na koncu. ``trzymaj_s``: tyle po ostatnim kawalku plik jest
    jeszcze trzymany otwarty. Zwraca opis zapisu: ``plik``, ``start``, ``koniec`` (time.time() PO zamknieciu pliku), ``rozmiar``,
    ``sha16``, ``mtime_ns``.
    """
    if tryb not in TRYBY:
        raise ValueError(f"tryb: {tryb!r} (dozwolone: {', '.join(TRYBY)})")
    cel = Path(cel)
    cel.parent.mkdir(parents=True, exist_ok=True)
    kawalki = max(1, int(kawalki))
    przerwa = czas_s / (kawalki - 1) if kawalki > 1 else czas_s
    h = hashlib.sha256()
    rozmiar = 0
    t0 = time.time()
    czesci = _kawalki(zrodlo, kawalki)
    if tryb == "dopisywanie":
        for i, blok in enumerate(czesci):
            if i:
                time.sleep(przerwa)
            with open(cel, "ab" if i else "wb") as f:
                f.write(blok)
            h.update(blok)
            rozmiar += len(blok)
        if rozmiar == 0:
            cel.write_bytes(b"")
    else:
        roboczy = cel.with_name(cel.name + ".tmp") if tryb == "tymczasowy" else cel
        with open(roboczy, "wb") as f:
            if kawalki == 1:
                time.sleep(przerwa)
            for i, blok in enumerate(czesci):
                if i:
                    time.sleep(przerwa)
                f.write(blok)
                f.flush()
                h.update(blok)
                rozmiar += len(blok)
            if trzymaj_s > 0:
                time.sleep(trzymaj_s)
        if tryb == "tymczasowy":
            os.replace(roboczy, cel)
    koniec = time.time()
    return {"plik": str(cel), "start": t0, "koniec": koniec, "rozmiar": rozmiar, "sha16": h.hexdigest()[:16], "mtime_ns": os.stat(cel).st_mtime_ns}


def symuluj(folder, zrodla: list, ile: int | None = None, czas: tuple = (1.0, 5.0), kawalki: tuple = (5, 20), rownolegle: int = 4,
            odstep_s: float = 0.0, zle: tuple | list = (), seed: int = 0, wzor_nazwy: str = "skan_{nr:04d}.stl", tryb: str = "wprost",
            czasy: list | None = None) -> list[dict]:
    """Wrzuca do ``folder`` ``ile`` dobrych plikow (kolejno z ``zrodla``: ``bytes`` albo sciezki) i po jednym pliku zlym na
    kazdy wpis ``zle``. Do ``rownolegle`` zapisow naraz; ``odstep_s`` - przerwa miedzy rozpoczeciem kolejnych plikow.
    Czas zapisu pliku losowany z ``czas`` (albo ``czasy[i]`` dla i-tego dobrego pliku), liczba kawalkow z ``kawalki``.
    Zwraca liste opisow zapisow (jak ``zapisz_jak_skaner``) z polami ``nr``, ``rodzaj`` (``dobry`` albo rodzaj pliku zlego)
    i ``zrodlo``; kolejnosc listy = kolejnosc rozpoczynania zapisow.
    """
    if not zrodla:
        raise ValueError("symuluj: brak plikow zrodlowych")
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    ile = len(zrodla) if ile is None else ile
    plan = []
    for i in range(ile):
        z = zrodla[i % len(zrodla)]
        nazwa = wzor_nazwy.format(nr=i + 1, zrodlo=Path(z).stem if not isinstance(z, (bytes, bytearray)) else f"dane{i % len(zrodla)}")
        plan.append({"nr": i + 1, "rodzaj": "dobry", "zrodlo": i % len(zrodla), "dane": z, "cel": folder / nazwa,
                     "czas": float(czasy[i]) if czasy is not None else rng.uniform(*czas), "kawalki": rng.randint(*kawalki), "tryb": tryb})
    if zle:
        z0 = zrodla[0]
        dobry = bytes(z0) if isinstance(z0, (bytes, bytearray)) else Path(z0).read_bytes()
        for j, rodzaj in enumerate(zle):
            dane = zly_plik(rodzaj, dobry)
            nazwa = f"zly_{j + 1:02d}_{rodzaj}" + (".txt" if rodzaj == "inne_rozszerzenie" else ".stl")
            wpis = {"nr": ile + j + 1, "rodzaj": rodzaj, "zrodlo": 0, "dane": dane, "cel": folder / nazwa, "czas": rng.uniform(*czas),
                    "kawalki": rng.randint(*kawalki), "tryb": "wprost"}
            plan.insert(min(len(plan), (j + 1) * max(1, ile // (len(zle) + 1)) + j), wpis)  # zle pliki rozlozone miedzy dobrymi

    def jeden(p: dict) -> dict:
        w = zapisz_jak_skaner(p["dane"], p["cel"], p["czas"], p["kawalki"], p["tryb"])
        return {"nr": p["nr"], "rodzaj": p["rodzaj"], "zrodlo": p["zrodlo"], **w}

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, rownolegle), thread_name_prefix="symulator") as pula:
        przyszle = []
        for i, p in enumerate(plan):
            if i and odstep_s > 0:
                time.sleep(odstep_s)
            przyszle.append(pula.submit(jeden, p))
        return [f.result() for f in przyszle]


def _klucz(sciezka) -> str:
    return os.path.normcase(os.path.abspath(str(sciezka)))


def statystyki(zapisy: list[dict], skany: list, odrzucone: list) -> dict:
    """Porownanie zapisow symulatora ze zdarzeniami obserwatora (``scanner.ZdarzenieSkanu``) i odrzuceniami (``scanner.Odrzucenie``)."""
    wolne = list(skany)
    opoznienia, bez_zdarzenia, przed_koncem, zly_skrot = [], [], 0, 0
    dobre = [z for z in zapisy if z["rodzaj"] == "dobry"]
    for z in sorted(dobre, key=lambda z: z["koniec"]):
        moje = [s for s in wolne if _klucz(s.plik) == _klucz(z["plik"])]
        if not moje:
            bez_zdarzenia.append(Path(z["plik"]).name)
            continue
        s = moje[0]
        wolne.remove(s)
        if (s.sha16, s.rozmiar) != (z["sha16"], z["rozmiar"]) or 84 + 50 * s.trojkaty != z["rozmiar"]:
            zly_skrot += 1
        if s.czas_zdarzenia < z["koniec"]:
            przed_koncem += 1
        opoznienia.append(s.czas_zdarzenia - z["koniec"])
    zle = [z for z in zapisy if z["rodzaj"] != "dobry"]
    powody = {_klucz(o.plik): o.powod for o in odrzucone}
    ze_zdarzeniem = [Path(z["plik"]).name for z in zle if any(_klucz(s.plik) == _klucz(z["plik"]) for s in skany)]
    opoznienia.sort()
    return {
        "dobrych": len(dobre), "zdarzen": len(skany), "bez_zdarzenia": bez_zdarzenia, "nadmiarowe": len(wolne) - len(ze_zdarzeniem),
        "przed_koncem": przed_koncem, "zly_skrot": zly_skrot,
        "opoznienie_mediana_s": statistics.median(opoznienia) if opoznienia else None,
        "opoznienie_p95_s": opoznienia[min(len(opoznienia) - 1, int(0.95 * len(opoznienia)))] if opoznienia else None,
        "opoznienie_max_s": opoznienia[-1] if opoznienia else None,
        "opoznienie_min_s": opoznienia[0] if opoznienia else None,
        "zlych": len(zle), "odrzucen": len(odrzucone),
        "powody_zlych": {Path(z["plik"]).name: powody.get(_klucz(z["plik"])) for z in zle},
        "zle_bez_powodu": [Path(z["plik"]).name for z in zle if _klucz(z["plik"]) not in powody],
        "zle_ze_zdarzeniem": ze_zdarzeniem,
    }


def _zrodla_z_argumentow(sciezki: list, ile: int | None, trojkaty: int, seed: int) -> list:
    if not sciezki:
        return [sztuczny_stl(trojkaty + 13 * i, seed=seed * 1000 + i) for i in range(ile or 10)]
    pliki = []
    for s in sciezki:
        p = Path(s)
        if p.is_dir():
            pliki += sorted(q for q in p.iterdir() if q.is_file() and q.suffix.lower() == ".stl")
        elif p.is_file():
            pliki.append(p)
        else:
            raise SystemExit(f"--zrodla: brak pliku albo katalogu {p}")
    if not pliki:
        raise SystemExit("--zrodla: nie znaleziono plikow .stl")
    return pliki


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--folder", type=Path, required=True, help="folder, do ktorego trafiaja pliki (jak folder eksportu skanera)")
    ap.add_argument("--zrodla", nargs="*", default=[], help="pliki STL albo katalogi z plikami STL; brak = male pliki sztuczne")
    ap.add_argument("--ile", type=int, default=None, help="ile dobrych plikow zapisac (domyslnie: tyle, ile zrodel)")
    ap.add_argument("--czas", type=float, nargs=2, default=(1.0, 5.0), metavar=("MIN", "MAX"), help="czas zapisu jednego pliku, s")
    ap.add_argument("--kawalki", type=int, nargs=2, default=(5, 20), metavar=("MIN", "MAX"))
    ap.add_argument("--rownolegle", type=int, default=4, help="ile zapisow naraz")
    ap.add_argument("--odstep", type=float, default=0.0, help="przerwa miedzy rozpoczeciem kolejnych plikow, s")
    ap.add_argument("--zle", nargs="*", default=[], choices=RODZAJE_ZLYCH, help="pliki zle do dorzucenia (po jednym na wpis)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--trojkaty", type=int, default=2000, help="wielkosc plikow sztucznych (gdy brak --zrodla)")
    ap.add_argument("--wzor-nazwy", default="skan_{nr:04d}.stl", help="nazwa pliku: pola {nr} i {zrodlo}; moze zawierac podfolder")
    ap.add_argument("--tryb", choices=TRYBY, default="wprost")
    ap.add_argument("--dziennik", type=Path, default=None, help="zapisz opis zapisow i statystyki do pliku JSON")
    ap.add_argument("--pomiar", action="store_true", help="obserwuj folder modulem scanner i policz zdarzenia oraz opoznienia")
    ap.add_argument("--stabilizacja-ms", type=float, default=None, help="parametr obserwatora (domyslnie wartosc modulu scanner)")
    ap.add_argument("--odrzuc-po", type=float, default=None, help="parametr obserwatora: po ilu sekundach plik zly jest odrzucany")
    ap.add_argument("--czekaj", type=float, default=60.0, help="ile najdluzej czekac na zdarzenia po ostatnim zapisie, s")
    ap.add_argument("--analiza", action="store_true", help="analizuj kazdy zgloszony skan silnikiem (wymaga --projekty)")
    ap.add_argument("--projekty", type=Path, nargs="+", default=[], help="folder(y) puli projektow dla --analiza")
    ap.add_argument("--wyjscie", type=Path, default=None, help="folder na <skan>_wynik.json z silnika")
    ap.add_argument("--ustawienia", type=Path, default=None)
    ap.add_argument("--limit-analizy", type=float, default=3600.0, help="ile najdluzej czekac na wszystkie analizy, s")
    a = ap.parse_args(argv)
    if a.analiza and not a.projekty:
        ap.error("--analiza wymaga --projekty")
    zrodla = _zrodla_z_argumentow(a.zrodla, a.ile, a.trojkaty, a.seed)
    obserwuj = a.pomiar or a.analiza
    skany, odrzucone, zdarzenia_silnika = [], [], []
    zmiana = threading.Condition()
    sc = silnik = None
    if a.analiza:
        from stanowisko import silnik as SI

        def na_zdarzenie(z) -> None:
            with zmiana:
                zdarzenia_silnika.append(z)
                zmiana.notify_all()

        silnik = SI.Silnik(plik_ustawien=a.ustawienia, na_zdarzenie=na_zdarzenie)
        silnik.start()
        pula = SI.OpisPuli(foldery=tuple(str(p) for p in a.projekty))
    if obserwuj:
        from stanowisko import scanner as SC

        def na_skan(z) -> None:
            with zmiana:
                skany.append(z)
                zmiana.notify_all()
            if silnik is not None:
                silnik.zlec_skan(z, pula, wyjscie=a.wyjscie)

        def na_odrzucenie(o) -> None:
            with zmiana:
                odrzucone.append(o)
                zmiana.notify_all()

        parametry = {}
        if a.stabilizacja_ms is not None:
            parametry["stabilizacja_ms"] = a.stabilizacja_ms
        if a.odrzuc_po is not None:
            parametry["odrzuc_po_s"] = a.odrzuc_po
        a.folder.mkdir(parents=True, exist_ok=True)
        sc = SC.Scanner(a.folder, na_skan=na_skan, na_odrzucenie=na_odrzucenie, **parametry)
        sc.start()
    kod = 0
    wynik: dict = {}
    try:
        zapisy = symuluj(a.folder, zrodla, a.ile, tuple(a.czas), tuple(a.kawalki), a.rownolegle, a.odstep, a.zle, a.seed, a.wzor_nazwy, a.tryb)
        wynik["zapisy"] = zapisy
        dobrych = sum(1 for z in zapisy if z["rodzaj"] == "dobry")
        print(f"zapisano plikow: {len(zapisy)} (dobrych {dobrych}, zlych {len(zapisy) - dobrych}) w {a.folder}")
        if sc is not None:
            limit = a.czekaj + sc.odrzuc_po_s
            with zmiana:
                zmiana.wait_for(lambda: len(skany) >= dobrych and len(odrzucone) >= len(zapisy) - dobrych, limit)
            time.sleep(min(1.0, sc.stabilizacja_s * 3))  # zdarzenia nadmiarowe, gdyby byly
            st = statystyki(zapisy, skany, odrzucone)
            wynik["statystyki"] = st
            wynik["zdarzenia"] = [{"plik": Path(z.plik).name, "sha16": z.sha16, "rozmiar": z.rozmiar, "trojkaty": z.trojkaty, "czas_zdarzenia": z.czas_zdarzenia,
                                   "nr": z.nr, "ponowny": z.ponowny, "duplikat": z.duplikat} for z in skany]
            wynik["odrzucone"] = [{"plik": Path(o.plik).name, "powod": o.powod, "opis": o.opis, "rozmiar": o.rozmiar} for o in odrzucone]
            print(f"zdarzen {st['zdarzen']} / {st['dobrych']}, przed koncem zapisu {st['przed_koncem']}, bez zdarzenia {len(st['bez_zdarzenia'])}, "
                  f"nadmiarowych {st['nadmiarowe']}, zly skrot {st['zly_skrot']}")
            if st["opoznienie_mediana_s"] is not None:
                print(f"opoznienie zdarzenia od konca zapisu: mediana {st['opoznienie_mediana_s']:.3f} s, p95 {st['opoznienie_p95_s']:.3f} s, "
                      f"min {st['opoznienie_min_s']:.3f} s, max {st['opoznienie_max_s']:.3f} s")
            print(f"pliki zle: {st['zlych']}, odrzucen z powodem {st['zlych'] - len(st['zle_bez_powodu'])} / {st['zlych']}, ze zdarzeniem {len(st['zle_ze_zdarzeniem'])}"
                  + "".join(f"\n  {n}: {p}" for n, p in st["powody_zlych"].items()))
            dobrze = (st["zdarzen"] == st["dobrych"] and not st["bez_zdarzenia"] and st["nadmiarowe"] == 0 and st["przed_koncem"] == 0 and st["zly_skrot"] == 0
                      and not st["zle_bez_powodu"] and not st["zle_ze_zdarzeniem"])
            kod = 0 if dobrze else 1
        if silnik is not None:
            with zmiana:
                zmiana.wait_for(lambda: sum(1 for z in zdarzenia_silnika if z.typ in ("wynik", "blad")) >= len(skany), a.limit_analizy)
            koniec_zapisu = {_klucz(z["plik"]): z["koniec"] for z in zapisy}
            analizy = []
            for z in [z for z in zdarzenia_silnika if z.typ in ("wynik", "blad")]:
                start = next((s.czas for s in zdarzenia_silnika if s.typ == "start" and s.zadanie_id == z.zadanie_id), None)
                kz = koniec_zapisu.get(_klucz(z.zadanie.skan))
                w = z.wynik or {}
                analizy.append({"plik": Path(z.zadanie.skan).name, "sha16": z.zadanie.skan_sha16, "typ": z.typ, "rodzaj": z.rodzaj, "blad": z.blad,
                                "start_od_konca_zapisu_s": round(start - kz, 3) if start is not None and kz is not None else None,
                                "wynik_od_konca_zapisu_s": round(z.czas - kz, 3) if kz is not None else None, "czas_s": z.czas_s,
                                "plytka": w.get("plytka"), "numer": w.get("numer"), "uklad_zgodny": w.get("uklad_zgodny"),
                                "gniazd": len(w.get("gniazda", [])), "statusy_gniazd": w.get("statusy_gniazd"), "ubytki": w.get("ubytki")})
                x = analizy[-1]
                print(f"analiza {x['plik']} sha16={x['sha16']}: {x['typ']}{' (' + x['rodzaj'] + ': ' + x['blad'] + ')' if z.typ == 'blad' else ''} "
                      f"plytka={x['plytka']} nr={x['numer']} gniazd={x['gniazd']} statusy={x['statusy_gniazd']} czas={x['czas_s']} s, "
                      f"start po {x['start_od_konca_zapisu_s']} s od konca zapisu, wynik po {x['wynik_od_konca_zapisu_s']} s")
            wynik["analizy"] = analizy
            if len(analizy) < len(skany):
                print(f"UWAGA: analiz {len(analizy)} / {len(skany)} w limicie {a.limit_analizy} s")
                kod = 1
            print(f"analizy: {sum(1 for x in analizy if x['typ'] == 'wynik')} wynikow, {sum(1 for x in analizy if x['typ'] == 'blad')} bledow / {len(skany)} skanow")
    finally:
        if sc is not None:
            sc.stop()
        if silnik is not None:
            silnik.stop()
    if a.dziennik is not None:
        a.dziennik.parent.mkdir(parents=True, exist_ok=True)
        a.dziennik.write_text(json.dumps(wynik, ensure_ascii=False, indent=1), encoding="utf-8")
        print(a.dziennik)
    return kod


if __name__ == "__main__":
    sys.exit(main())
