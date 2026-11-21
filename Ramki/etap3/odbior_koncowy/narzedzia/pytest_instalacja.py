"""pytest_instalacja.py - testy z repo uruchomione na kodzie programu ZAINSTALOWANYM z paczki (uwaga 5 recenzji PR #44).

Problem: ``<K>\\Polecenie.cmd -m pytest <ST>\\testy\\...`` bierze z paczki tylko interpreter i pakiety - plik
``testy/conftest.py`` wstawia katalog ``<ST>`` (repo) na poczatek ``sys.path``, wiec ``import stanowisko`` w testach laduje
kod z REPO, nie z instalacji. Ten skrypt laduje pakiety programu z katalogu programu wersji (katalog biezacy ustawiony przez
``Polecenie.cmd``) ZANIM wystartuje pytest - testy dostaja wtedy moduly juz zaladowane z instalacji - a po testach liczy,
skad pochodzi kazdy zaladowany modul, i porownuje pliki ``*.py`` instalacji z plikami repo (SHA-256).

Uzycie (jedna linia; wszystko po ``--`` to zwykle argumenty pytest):
    <K>\\Polecenie.cmd <ODB>\\narzedzia\\pytest_instalacja.py --st <ST> --wynik <ROB>\\t6_zrodlo_kodu.txt -- <ST>\\testy\\test_excel.py -q -rA -p no:cacheprovider --rootdir <ST>

Ostatnie wiersze wyjscia (i plik ``--wynik``, ASCII + LF):
    KOD PROGRAMU W TESTACH: z instalacji n modulow, z repo poza testami k modulow (lista), pliki instalacji = repo: a z b
    WERDYKT ZRODLA KODU: INSTALACJA / REPO (k modulow programu zaladowanych z repo) / NIE ZMIERZONO

Kody wyjscia: kod pytest (0 = testy przeszly), gdy caly kod programu pochodzil z instalacji; 3 = testy przeszly, ale co
najmniej 1 modul programu zostal zaladowany z repo (wynik testow nie dotyczy wtedy w calosci programu z paczki); 2 = blad
uzycia (katalog biezacy nie jest katalogiem programu, brak pytest).

Ograniczenie (zapisane w wyniku): procesy potomne zakladane przez testy (ramka w osobnym procesie, proces roboczy silnika
zakladany przez ``multiprocessing``) importuja kod sami - gdy test podaje im katalog ``<ST>``, biora kod z repo. Skrypt tego
nie widzi; dla takich testow zgodnosc kodu potwierdza tylko wiersz "pliki instalacji = repo".
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.abc
import importlib.util
import sys
from pathlib import Path

PAKIETY = ("stanowisko", "ramka")


def skrot(plik: Path) -> str:
    return hashlib.sha256(plik.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    reszta = argv[argv.index("--") + 1:] if "--" in argv else []
    swoje = argv[:argv.index("--")] if "--" in argv else argv
    ap = argparse.ArgumentParser(prog="pytest_instalacja.py", description="pytest z repo na kodzie programu z instalacji; "
                                 "argumenty pytest po '--'. Uruchamiac przez <K>\\Polecenie.cmd (katalog biezacy = katalog programu wersji).")
    ap.add_argument("--st", type=Path, required=True, help="katalog Ramki\\stanowisko repo (ten sam commit co paczka) - zrodlo testow")
    ap.add_argument("--wynik", type=Path, default=None, help="plik z wierszami podsumowania (ASCII, LF)")
    a = ap.parse_args(swoje)
    program, st = Path.cwd().resolve(), a.st.resolve()
    if not (program / "stanowisko" / "__init__.py").is_file():
        print(f"BLAD: katalog biezacy nie jest katalogiem programu (brak stanowisko\\__init__.py) - uruchom przez Polecenie.cmd", file=sys.stderr)
        return 2
    if program == st or st in program.parents:
        print("BLAD: katalog biezacy lezy w repo - to nie jest instalacja z paczki", file=sys.stderr)
        return 2
    if not reszta:
        print("BLAD: brak argumentow pytest po '--'", file=sys.stderr)
        return 2
    try:
        import pytest
    except ImportError:
        print("BLAD: w srodowisku wersji nie ma pytest (zainstaluj.cmd /testy)", file=sys.stderr)
        return 2
    sys.path.insert(0, str(program))

    class ZInstalacji(importlib.abc.MetaPathFinder):
        """Skrypty ``narzedzia/<nazwa>.py`` programu (testy importuja je po nazwie, wstawiajac katalog repo na ``sys.path``)
        sa ladowane z katalogu programu wersji, nie z repo."""

        def find_spec(self, nazwa, sciezka=None, cel=None):
            if sciezka is None and "." not in nazwa:
                plik = program / "narzedzia" / (nazwa + ".py")
                if plik.is_file():
                    return importlib.util.spec_from_file_location(nazwa, plik)
            return None

    sys.meta_path.insert(0, ZInstalacji())
    for nazwa in PAKIETY:  # zaladowane przed pytest: conftest testow nie podmieni ich juz na kod z repo
        if (program / nazwa / "__init__.py").is_file():
            importlib.import_module(nazwa)
    kod = int(pytest.main(reszta))

    z_instalacji, z_repo, testy = [], [], 0
    for nazwa, modul in sorted(sys.modules.items()):
        plik = getattr(modul, "__file__", None)
        if not plik:
            continue
        sciezka = Path(plik).resolve()
        if program in sciezka.parents:
            z_instalacji.append(nazwa)
        elif st in sciezka.parents:
            if (st / "testy") in sciezka.parents:
                testy += 1
            else:
                z_repo.append(sciezka.relative_to(st).as_posix())
    rowne = rozne = brak = 0
    rozne_lista = []
    for plik in sorted(program.rglob("*.py")):
        wzgl = plik.relative_to(program)
        if wzgl.parts[0] not in ("stanowisko", "ramka", "narzedzia"):
            continue
        odp = st / wzgl
        if not odp.is_file():
            brak += 1
        elif skrot(odp) == skrot(plik):
            rowne += 1
        else:
            rozne += 1
            rozne_lista.append(wzgl.as_posix())
    wersja = program.parent.name
    werdykt = ("NIE ZMIERZONO (zaden modul programu nie zostal zaladowany z instalacji)" if not z_instalacji
               else f"REPO ({len(z_repo)} modulow programu zaladowanych z repo)" if z_repo else "INSTALACJA")
    linie = [f"pytest_instalacja.py: wersja programu (katalog) {wersja}; interpreter {Path(sys.executable).parent.parent.name}\\Scripts; kod pytest {kod}",
             f"KOD PROGRAMU W TESTACH: z instalacji {len(z_instalacji)} modulow, z repo poza testami {len(z_repo)} modulow"
             + (f" ({', '.join(z_repo[:20])})" if z_repo else "") + f", modulow testow z repo {testy}; "
             f"pliki *.py instalacji (stanowisko, ramka, narzedzia) = repo: {rowne} z {rowne + rozne + brak}"
             + (f"; ROZNE {rozne}: {', '.join(rozne_lista[:10])}" if rozne else "") + (f"; bez odpowiednika w repo {brak}" if brak else ""),
             "ograniczenie: procesy potomne testow (ramka, proces silnika) importuja kod sami - tego wiersza nie obejmuje licznik modulow",
             f"WERDYKT ZRODLA KODU: {werdykt}"]
    tekst = "\n".join(linie) + "\n"
    print(tekst, end="")
    if a.wynik is not None:
        a.wynik.parent.mkdir(parents=True, exist_ok=True)
        a.wynik.write_bytes(tekst.encode("ascii", errors="replace"))
    if kod == 0 and werdykt != "INSTALACJA":
        return 3
    return kod


if __name__ == "__main__":
    raise SystemExit(main())
