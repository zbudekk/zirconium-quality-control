"""T12 czesc B - paczka PROBNA z dodatkowa migracja bazy (do proby "aktualizacja z migracja i powrot").

Co robi (repo zrodlowe zostaje bez zmian - sprawdzane ``git status --short`` przed i po):
  1. ``git archive <commit> Ramki/stanowisko`` -> ``<--roboczy>\\drzewo_M`` (katalog roboczy poza repo; drzewo_M nie moze istniec);
  2. w KOPII ``drzewo_M\\stanowisko\\baza.py``: ``WERSJA_SCHEMATU`` + 1 i dodatkowa pozycja ``MIGRACJE[n + 1]`` =
     ``CREATE TABLE proba_migracji_odbior (id INTEGER PRIMARY KEY, opis TEXT)``; gdy ktorys z 2 wierszy nie pasuje do
     wzorca dokladnie 1 raz - kod 2, niczego nie buduje;
  3. ``drzewo_M\\narzedzia\\zbuduj_wydanie.py --zrodlo drzewo_M --data <data commita UTC> --wersja <--wersja>
     --commit <skrot>+MIGRACJE --wyjscie <--wyjscie> --kola <--kola>``.

Wypisuje: commit, stary i nowy numer schematu, sciezke ZIP i SHA-256. Paczki probnej NIE publikowac i nie dopisywac do
listy wydan - sluzy tylko do proby T12 czesc B w katalogu roboczym.

Kod wyjscia: 0 = paczka zbudowana; 2 = blad wywolania / wzorzec nie pasuje / repo zmienione; inny = kod budowy paczki.
Uruchomienie: ``PY -I t12_paczka_migracja.py --repo <REPO> --roboczy <ROB>\\t12 --wersja 0.3.9-migracja --wyjscie <ROB>\\t12\\paczki
--kola <PC-katalog>\\wydania\\kola``.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import os
import re
import subprocess
import sys
import tarfile
from pathlib import Path

PRZEDROSTEK = "Ramki/stanowisko/"
TABELA = "CREATE TABLE proba_migracji_odbior (id INTEGER PRIMARY KEY, opis TEXT)"
WZOR_WERSJI = re.compile(rb"^WERSJA_SCHEMATU = (\d+)(\r?)$", re.M)
WZOR_MIGRACJI = re.compile(rb"^(MIGRACJE: dict\[int, tuple\[str, \.\.\.\]\] = \{[^\r\n{}]*)\}(\r?)$", re.M)


def git(repo: Path, *argumenty: str, srodowisko: dict | None = None) -> bytes:
    return subprocess.run(["git", "-C", str(repo), *argumenty], capture_output=True, check=True, env=srodowisko).stdout


def zmien_baze(tresc: bytes) -> tuple[bytes, int, int] | str:
    """Zwraca (nowa tresc, stary numer, nowy numer) albo opis bledu."""
    wersje = WZOR_WERSJI.findall(tresc)
    migracje = WZOR_MIGRACJI.findall(tresc)
    if len(wersje) != 1 or len(migracje) != 1:
        return f"wiersz WERSJA_SCHEMATU pasuje {len(wersje)} razy, wiersz MIGRACJE pasuje {len(migracje)} razy (wymagane 1 i 1)"
    stary = int(wersje[0][0])
    nowy = stary + 1
    dopisek = f', {nowy}: ("{TABELA}",)}}  # PROBA T12 czesc B - tylko w kopii roboczej'.encode("ascii")
    tresc = WZOR_MIGRACJI.sub(lambda d: d.group(1) + dopisek + d.group(2), tresc)
    tresc = WZOR_WERSJI.sub(lambda d: b"WERSJA_SCHEMATU = " + str(nowy).encode("ascii") + d.group(2), tresc)
    return tresc, stary, nowy


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", type=Path, required=True, help="repo git z katalogiem Ramki/stanowisko (tylko odczyt)")
    parser.add_argument("--commit", default="HEAD", help="commit zrodlowy (domyslnie HEAD)")
    parser.add_argument("--roboczy", type=Path, required=True, help="katalog roboczy poza repo; powstanie w nim drzewo_M")
    parser.add_argument("--wersja", required=True, help="numer wersji paczki probnej, np. 0.3.9-migracja")
    parser.add_argument("--wyjscie", type=Path, required=True, help="katalog na Stanowisko_<wersja>.zip (poza repo)")
    parser.add_argument("--kola", type=Path, required=True, help="katalog z kolami pip (np. <PC-katalog>\\wydania\\kola)")
    args = parser.parse_args(argv)

    try:
        repo = Path(git(args.repo, "rev-parse", "--show-toplevel").decode("utf-8").strip()).resolve()
        commit = git(repo, "rev-parse", "--verify", args.commit + "^{commit}").decode("ascii").strip()
        stan_przed = git(repo, "status", "--short")
        utc = dict(os.environ, TZ="UTC")
        data = git(repo, "log", "-1", "--date=format-local:%Y-%m-%dT%H:%M:%S", "--format=%cd", commit, srodowisko=utc).decode("ascii").strip()
    except (OSError, subprocess.CalledProcessError) as blad:
        print(f"BLAD: git nie odczytal repo albo commita ({type(blad).__name__})")
        return 2
    roboczy = args.roboczy.resolve()
    drzewo = roboczy / "drzewo_M"
    for sciezka in (roboczy, args.wyjscie.resolve()):
        if sciezka == repo or repo in sciezka.parents:
            print("BLAD: --roboczy i --wyjscie musza lezec poza repo")
            return 2
    if drzewo.exists():
        print(f"BLAD: {drzewo} juz istnieje - podaj nowy katalog roboczy albo usun drzewo_M")
        return 2

    archiwum = git(repo, "-c", "core.autocrlf=false", "archive", "--format=tar", commit, PRZEDROSTEK.rstrip("/"))
    plikow = 0
    with tarfile.open(fileobj=io.BytesIO(archiwum)) as tar:
        for pozycja in tar:
            if not pozycja.isfile() or not pozycja.name.startswith(PRZEDROSTEK):
                continue
            cel = drzewo / pozycja.name[len(PRZEDROSTEK):]
            cel.parent.mkdir(parents=True, exist_ok=True)
            zrodlo = tar.extractfile(pozycja)
            assert zrodlo is not None
            cel.write_bytes(zrodlo.read())
            plikow += 1
    baza = drzewo / "stanowisko" / "baza.py"
    budowa = drzewo / "narzedzia" / "zbuduj_wydanie.py"
    if not baza.is_file() or not budowa.is_file():
        print("BLAD: w commicie nie ma Ramki/stanowisko/stanowisko/baza.py albo narzedzia/zbuduj_wydanie.py")
        return 2
    zmiana = zmien_baze(baza.read_bytes())
    if isinstance(zmiana, str):
        print(f"BLAD: baza.py ma inna postac niz oczekiwana - {zmiana}; paczki nie zbudowano")
        return 2
    tresc, stary, nowy = zmiana
    baza.write_bytes(tresc)
    print(f"commit zrodlowy: {commit} (data {data} UTC); plikow w drzewo_M: {plikow}")
    print(f"schemat bazy w kopii: {stary} -> {nowy} (MIGRACJE[{nowy}] = {TABELA})")

    polecenie = [sys.executable, "-I", str(budowa), "--zrodlo", str(drzewo), "--data", data, "--wersja", args.wersja,
                 "--commit", f"{commit[:12]}+MIGRACJE", "--wyjscie", str(args.wyjscie), "--kola", str(args.kola)]
    print("budowa: " + " ".join(polecenie), flush=True)
    kod = subprocess.run(polecenie, cwd=str(drzewo)).returncode
    if git(repo, "status", "--short") != stan_przed:
        print("BLAD: stan repo zrodlowego zmienil sie w trakcie budowy (git status --short przed != po)")
        return 2
    print(f"repo zrodlowe bez zmian (git status --short: {len(stan_przed.splitlines())} wierszy przed i po)")
    if kod != 0:
        print(f"BLAD: budowa paczki zakonczona kodem {kod}")
        return kod
    paczka = args.wyjscie / f"Stanowisko_{args.wersja}.zip"
    if not paczka.is_file():
        print(f"BLAD: nie ma pliku {paczka}")
        return 2
    skrot = hashlib.sha256(paczka.read_bytes()).hexdigest()
    print(f"paczka probna: {paczka} ({paczka.stat().st_size} B)")
    print(f"SHA-256: {skrot}")
    print("UWAGA: paczki probnej NIE publikowac i nie dopisywac do listy wydan (zawiera probna migracje bazy).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
