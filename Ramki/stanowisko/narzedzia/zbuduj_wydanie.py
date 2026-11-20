"""zbuduj_wydanie - paczka wydania programu "Stanowisko" (E3-A11i, wariant B): jeden ZIP + suma SHA-256.

    python narzedzia/zbuduj_wydanie.py --wyjscie <PC-katalog>\\wydania [--wersja X] [--kola KATALOG]
    python narzedzia/zbuduj_wydanie.py --pobierz-kola --kola KATALOG [--python python.exe]     (jedyny krok z internetem)

Zawartosc ``Stanowisko_<wersja>.zip`` (rozpakowac w calosci, potem ``zainstaluj.cmd``)::

    zainstaluj.cmd, CZYTAJ.txt, wydanie.json, SHA256SUMS (kazdy plik paczki)
    program/      stanowisko/, modele_plytek/, narzedzia/, ramka/, instrukcje/, instalacja/, ustawienia.przyklad.toml,
                  requirements.txt, WERSJA, SUMY_PROGRAMU.sha256 (umowa samokontroli A11s); bez testy/, raporty/, danych
    kola/         kola pip (Windows x64, Python 3.12) wszystkich pakietow z instalacja/zamrozone.txt
    kola_testy/   pytest i jego zaleznosci (instalacja/zamrozone_testy.txt) - instalowane tylko przez zainstaluj.cmd /testy

Zrodlo plikow programu: domyslnie commit HEAD repozytorium (tresc z gita, nie z katalogu roboczego - zmiany
niezacommitowane NIE wchodza; ``--rewizja COMMIT`` odtwarza wczesniejsze wydanie); ``--zrodlo KATALOG`` bierze pliki
z katalogu (proby, kopia drzewa) i wymaga ``--data``.
Paczka jest powtarzalna bajtowo: ten sam commit + te same kola = ten sam SHA-256 (stala data wpisow = data commita,
staly porzadek, stale atrybuty; kola bez kompresji, reszta deflate 9). Budowa nie uzywa sieci. Tylko biblioteka standardowa.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

STANOWISKO = Path(__file__).resolve().parent.parent
KATALOGI_PROGRAMU = ("stanowisko", "modele_plytek", "narzedzia", "ramka", "instrukcje", "instalacja")
PLIKI_PROGRAMU = ("ustawienia.przyklad.toml", "requirements.txt", "WERSJA")
POMIJANE = re.compile(r"(^|/)__pycache__/|\.py[co]$|^narzedzia/zbuduj_wydanie\.[A-Za-z0-9]+$")
WYMAGANE = ("stanowisko/aplikacja.py", "stanowisko/ustawienia.py", "stanowisko/baza.py", "ustawienia.przyklad.toml", "requirements.txt",
            "instalacja/instalator.py", "instalacja/zainstaluj.cmd", "instalacja/zamrozone.txt", "instalacja/zamrozone_testy.txt",
            "instalacja/wzory/Stanowisko.cmd", "instalacja/wzory/Samokontrola.cmd", "instalacja/wzory/Wroc_do_poprzedniej.cmd",
            "instalacja/wzory/Wersje.cmd", "instalacja/wzory/Polecenie.cmd")
MODUL_SAMOKONTROLI = "stanowisko/samokontrola.py"
LISTA_PROGRAMU, LISTA_TESTOW = "instalacja/zamrozone.txt", "instalacja/zamrozone_testy.txt"
WZOR_WERSJI = re.compile(r"[0-9A-Za-z][0-9A-Za-z._-]{0,31}")
PYTHON, PLATFORMA = "3.12", "win_amd64"
SKRYPTY_CRLF = (".cmd", ".bat", ".ps1")
FORMAT_WYDANIA = 1


class BladBudowy(Exception):
    pass


def sha256(dane: bytes) -> str:
    return hashlib.sha256(dane).hexdigest()


def normalizuj_nazwe(nazwa: str) -> str:
    return re.sub(r"[-_.]+", "-", nazwa).lower()


def _git(repo: Path, *argumenty: str, wejscie: bytes | None = None) -> bytes:
    wynik = subprocess.run(["git", "-C", str(repo), *argumenty], input=wejscie, capture_output=True, check=False)
    if wynik.returncode != 0:
        raise BladBudowy(f"git {' '.join(argumenty[:2])}: {wynik.stderr.decode('utf-8', 'replace').strip()}")
    return wynik.stdout


def _nalezy(nazwa: str) -> bool:
    return (nazwa in PLIKI_PROGRAMU or nazwa.split("/", 1)[0] in KATALOGI_PROGRAMU and "/" in nazwa) and not POMIJANE.search(nazwa)


def pliki_z_gita(stanowisko: Path, rewizja: str = "HEAD") -> tuple[dict[str, bytes], str, dt.datetime, bool]:
    """Pliki programu z commita (tresc obiektow gita, bez konwersji koncow linii): ({nazwa: bajty}, commit, data, czyste)."""
    repo = Path(_git(stanowisko, "rev-parse", "--show-toplevel").decode("utf-8").strip())
    prefiks = stanowisko.resolve().relative_to(repo.resolve()).as_posix()
    prefiks = prefiks + "/" if prefiks != "." else ""
    commit = _git(repo, "rev-parse", rewizja).decode("ascii").strip()
    data = dt.datetime.fromtimestamp(int(_git(repo, "show", "-s", "--format=%ct", commit).decode("ascii").strip()), dt.timezone.utc)
    sciezki = [s for s in _git(repo, "ls-tree", "-r", "-z", "--name-only", commit, "--", prefiks or ".").decode("utf-8").split("\0") if s]
    nazwy = sorted(s[len(prefiks):] for s in sciezki if _nalezy(s[len(prefiks):]))
    strumien = _git(repo, "cat-file", "--batch", wejscie="".join(f"{commit}:{prefiks}{n}\n" for n in nazwy).encode("utf-8"))
    pliki, pozycja = {}, 0
    for nazwa in nazwy:
        koniec = strumien.index(b"\n", pozycja)
        naglowek = strumien[pozycja:koniec].split()
        if len(naglowek) != 3 or naglowek[1] != b"blob":
            raise BladBudowy(f"git cat-file: {nazwa}: {strumien[pozycja:koniec]!r}")
        rozmiar = int(naglowek[2])
        pliki[nazwa] = strumien[koniec + 1:koniec + 1 + rozmiar]
        pozycja = koniec + 1 + rozmiar + 1
    czyste = not _git(repo, "status", "--porcelain", "--", *[prefiks + k for k in KATALOGI_PROGRAMU + PLIKI_PROGRAMU]).strip()
    return pliki, commit, data, czyste


def pliki_z_katalogu(katalog: Path) -> dict[str, bytes]:
    """Pliki programu z katalogu (kopia drzewa do prob): te same reguly wyboru co dla commita."""
    pliki = {}
    for p in sorted(katalog.rglob("*")):
        nazwa = p.relative_to(katalog).as_posix()
        if p.is_file() and _nalezy(nazwa):
            pliki[nazwa] = p.read_bytes()
    return pliki


def wczytaj_liste(dane: bytes, nazwa: str) -> dict[str, str]:
    pakiety = {}
    for wiersz in dane.decode("utf-8").splitlines():
        wiersz = wiersz.split("#", 1)[0].strip()
        if not wiersz:
            continue
        m = re.fullmatch(r"([A-Za-z0-9][A-Za-z0-9._-]*)==([A-Za-z0-9][A-Za-z0-9._+!-]*)", wiersz)
        if not m:
            raise BladBudowy(f"{nazwa}: wiersz {wiersz!r} nie ma postaci nazwa==wersja")
        pakiety[normalizuj_nazwe(m.group(1))] = m.group(2)
    return pakiety


def kolo_zgodne(nazwa_pliku: str) -> tuple[str, str] | None:
    """(pakiet znormalizowany, wersja), gdy plik jest kolem binarnym dla CPython 3.12 na Windows x64; inaczej None."""
    m = re.fullmatch(r"([^-]+)-([^-]+)(?:-\d[^-]*)?-([^-]+)-([^-]+)-([^-]+)\.whl", nazwa_pliku)
    if not m:
        return None
    pythony, abi, platformy = m.group(3).split("."), m.group(4).split("."), m.group(5).split(".")
    python_ok = any(p in ("py3", "py312", "cp312") or (re.fullmatch(r"cp3(\d+)", p) and int(p[3:]) <= 12 and "abi3" in abi) for p in pythony)
    if python_ok and set(abi) & {"none", "abi3", "cp312"} and set(platformy) & {"any", PLATFORMA}:
        return normalizuj_nazwe(m.group(1)), m.group(2)
    return None


def dobierz_kola(katalog: Path, pakiety: dict[str, str], opis: str) -> list[Path]:
    dostepne: dict[tuple[str, str], Path] = {}
    for p in sorted(katalog.glob("*.whl")) if katalog.is_dir() else []:
        klucz = kolo_zgodne(p.name)
        if klucz is not None:
            dostepne.setdefault(klucz, p)
    brak = [f"{n}=={w}" for n, w in sorted(pakiety.items()) if (n, w) not in dostepne]
    if brak:
        raise BladBudowy(f"brak kola binarnego (Windows x64, Python {PYTHON}) dla {len(brak)} z {len(pakiety)} pakietow {opis} w {katalog}: "
                         + ", ".join(brak) + " - pobierz kola (--pobierz-kola); budowa nie kompiluje pakietow ze zrodel")
    return [dostepne[(n, w)] for n, w in sorted(pakiety.items())]


def zbuduj(wyjscie: Path, kola: Path, *, wersja: str | None = None, zrodlo: Path | None = None, commit: str | None = None,
           data: dt.datetime | None = None, bez_samokontroli: bool = False, stanowisko: Path = STANOWISKO, rewizja: str = "HEAD") -> dict:
    """Buduje ``Stanowisko_<wersja>.zip`` i plik ``.sha256`` obok. Zwraca {plik, sha256, rozmiar, wersja, commit, ...}."""
    ostrzezenia = []
    if zrodlo is not None:
        if data is None:
            raise BladBudowy("--zrodlo wymaga --data (data wpisow paczki, np. 2026-11-20T12:00:00) - inaczej paczka nie bylaby powtarzalna")
        pliki, commit, tryb = pliki_z_katalogu(zrodlo), commit or "kopia-robocza", "katalog"
    else:
        pliki, commit, data, czyste = pliki_z_gita(stanowisko, rewizja)
        tryb = "git"
        if not czyste and rewizja == "HEAD":
            ostrzezenia.append("w katalogu roboczym sa zmiany niezacommitowane - paczka zawiera stan commita HEAD, bez tych zmian")
    brak = [n for n in WYMAGANE if n not in pliki]
    if brak:
        raise BladBudowy("w zrodle brakuje plikow programu: " + ", ".join(brak))
    samokontrola = MODUL_SAMOKONTROLI in pliki
    if not samokontrola and not bez_samokontroli:
        raise BladBudowy(f"w zrodle nie ma modulu samokontroli ({MODUL_SAMOKONTROLI}) - takiej paczki instalator nie zainstaluje "
                         "(blad wydania); do prob budowy: --bez-samokontroli")
    if not samokontrola:
        ostrzezenia.append("paczka BEZ modulu samokontroli - instalator zglosi blad wydania i nie przelaczy wersji")
    if wersja is None:
        if "WERSJA" not in pliki:
            raise BladBudowy("brak pliku WERSJA w zrodle i brak opcji --wersja")
        wersja = pliki["WERSJA"].decode("ascii", "replace").strip()
    if not WZOR_WERSJI.fullmatch(wersja):
        raise BladBudowy(f"niepoprawny numer wersji {wersja!r} (litery, cyfry, kropka, podkreslenie, myslnik; do 32 znakow)")
    pliki["WERSJA"] = (wersja + "\n").encode("ascii")
    for nazwa in pliki:
        if nazwa.lower().endswith(SKRYPTY_CRLF):  # skrypty Windows zawsze z CRLF, niezaleznie od ustawien gita
            pliki[nazwa] = re.sub(rb"\r?\n", b"\r\n", pliki[nazwa])

    kola_programu = dobierz_kola(kola, wczytaj_liste(pliki[LISTA_PROGRAMU], LISTA_PROGRAMU), "programu")
    pakiety_testow = wczytaj_liste(pliki[LISTA_TESTOW], LISTA_TESTOW)
    kola_testow = dobierz_kola(kola, pakiety_testow, "zestawu testowego")

    paczka: dict[str, bytes] = {f"program/{n}": d for n, d in pliki.items()}
    paczka["program/SUMY_PROGRAMU.sha256"] = "".join(f"{sha256(d)}  {n}\n" for n, d in sorted(pliki.items())).encode("utf-8")
    paczka["zainstaluj.cmd"] = pliki["instalacja/zainstaluj.cmd"]
    opis_kol = {}
    for katalog, lista in (("kola", kola_programu), ("kola_testy", kola_testow)):
        opis_kol[katalog] = []
        for p in lista:
            dane = p.read_bytes()
            paczka[f"{katalog}/{p.name}"] = dane
            pakiet, wersja_pakietu = kolo_zgodne(p.name)
            opis_kol[katalog].append({"plik": p.name, "pakiet": pakiet, "wersja": wersja_pakietu, "sha256": sha256(dane), "rozmiar": len(dane)})
    wydanie = {"format": FORMAT_WYDANIA, "nazwa": "Stanowisko", "wersja": wersja, "commit": commit, "data_commita": data.strftime("%Y-%m-%dT%H:%M:%SZ"),
               "zrodlo": tryb, "python": PYTHON, "platforma": PLATFORMA, "samokontrola": samokontrola, "pliki_programu": len(pliki) + 1,
               "kola": opis_kol["kola"], "kola_testy": opis_kol["kola_testy"]}
    paczka["wydanie.json"] = (json.dumps(wydanie, indent=1, sort_keys=True, ensure_ascii=True) + "\n").encode("ascii")
    paczka["CZYTAJ.txt"] = "\r\n".join([
        f'Program "Stanowisko" - paczka wydania {wersja} (commit {commit[:12]}, {data:%Y-%m-%d}).', "",
        f"1. Raz, recznie: Python {PYTHON} (64-bit) z python.org.",
        "2. Rozpakuj CALA paczke do dowolnego katalogu i uruchom zainstaluj.cmd (bez internetu).",
        "3. Instrukcja (instalacja, aktualizacja, powrot, komunikaty bledow): program\\instrukcje\\instalacja_i_aktualizacja.md", "",
        "Sprawdzenie paczki: zainstaluj.cmd sam liczy sumy z pliku SHA256SUMS; niezgodnosc zatrzymuje instalacje.", ""]).encode("ascii")
    paczka["SHA256SUMS"] = "".join(f"{sha256(d)}  {n}\n" for n, d in sorted(paczka.items())).encode("utf-8")

    wyjscie.mkdir(parents=True, exist_ok=True)
    plik = wyjscie / f"Stanowisko_{wersja}.zip"
    czesc = plik.with_name(plik.name + ".czesc")
    znacznik = (max(data.year, 1980), data.month, data.day, data.hour, data.minute, data.second - data.second % 2)
    with zipfile.ZipFile(czesc, "w") as z:
        for nazwa, dane in sorted(paczka.items()):
            wpis = zipfile.ZipInfo(nazwa, date_time=znacznik)
            wpis.create_system = 3
            wpis.external_attr = 0o644 << 16
            if nazwa.endswith(".whl"):  # kolo jest juz skompresowane
                wpis.compress_type = zipfile.ZIP_STORED
                z.writestr(wpis, dane)
            else:
                wpis.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(wpis, dane, compresslevel=9)
    niezgodne = sprawdz_zip(czesc)
    if niezgodne:
        czesc.unlink()
        raise BladBudowy("kontrola wlasna paczki nieudana: " + "; ".join(niezgodne[:10]))
    czesc.replace(plik)
    h = hashlib.sha256()
    with open(plik, "rb") as f:
        for kawalek in iter(lambda: f.read(1 << 20), b""):
            h.update(kawalek)
    plik.with_name(plik.name + ".sha256").write_bytes(f"{h.hexdigest()}  {plik.name}\n".encode("ascii"))
    return {"plik": plik, "sha256": h.hexdigest(), "rozmiar": plik.stat().st_size, "wersja": wersja, "commit": commit, "pliki": len(paczka) - 1,
            "pliki_programu": len(pliki) + 1, "kola": len(kola_programu), "kola_testy": len(kola_testow), "samokontrola": samokontrola,
            "ostrzezenia": ostrzezenia}


def sprawdz_zip(plik: Path) -> list[str]:
    """Kontrola wlasna: kazdy wpis ZIP wobec ``SHA256SUMS`` z tego ZIP-a (i odwrotnie); [] = zgodne."""
    roznice = []
    with zipfile.ZipFile(plik) as z:
        nazwy = set(z.namelist())
        sumy = dict(reversed(w.split("  ", 1)) for w in z.read("SHA256SUMS").decode("utf-8").splitlines() if w)
        for nazwa, suma in sumy.items():
            if nazwa not in nazwy:
                roznice.append(f"brak {nazwa}")
            elif sha256(z.read(nazwa)) != suma:
                roznice.append(f"zmieniony {nazwa}")
        roznice += [f"bez sumy {n}" for n in sorted(nazwy - set(sumy) - {"SHA256SUMS"})]
    return roznice


# ----------------------------------------------------------------------------------- pobranie kol (jedyny krok z siecia)

def pobierz_kola(python: Path, kola: Path, stanowisko: Path = STANOWISKO) -> tuple[int, int]:
    """Pobiera z PyPI kola binarne wersji zamrozonych wg interpretera ``python`` i zapisuje listy zamrozone.

    Filtr: ``pip freeze`` interpretera (na ktorym przechodza testy) sluzy jako ograniczenia wersji (``-c``); do paczki
    trafia to, co pip uznaje za potrzebne dla ``requirements.txt`` bez pytest (program) oraz dla pytest (zestaw testowy
    = pakiety, ktorych nie ma w zestawie programu). Reszta ``pip freeze`` (np. pip, pakiety spoza zaleznosci) odpada."""
    kola.mkdir(parents=True, exist_ok=True)
    wymagania = []
    for wiersz in (stanowisko / "requirements.txt").read_text(encoding="utf-8").splitlines():
        wiersz = wiersz.split("#", 1)[0].strip()
        if wiersz:
            wymagania.append(wiersz)
    testowe = [w for w in wymagania if normalizuj_nazwe(re.split(r"[=<>!~; ]", w, maxsplit=1)[0]) == "pytest"]
    programowe = [w for w in wymagania if w not in testowe]
    ograniczenia = subprocess.run([str(python), "-I", "-m", "pip", "freeze", "--disable-pip-version-check"], capture_output=True, text=True,
                                  check=True).stdout
    (kola / "_ograniczenia.txt").write_text(ograniczenia, encoding="ascii")
    wspolne = ["--isolated", "--disable-pip-version-check", "--no-cache-dir", "--only-binary=:all:", "-c", str(kola / "_ograniczenia.txt")]
    cel = ["--platform", PLATFORMA, "--python-version", PYTHON]
    zestawy = {}
    for nazwa, lista in (("program", programowe), ("testy", testowe)):
        plik = kola / f"_wymagania_{nazwa}.txt"
        plik.write_text("\n".join(lista) + "\n", encoding="ascii")
        subprocess.run([str(python), "-I", "-m", "pip", "download", *wspolne, *cel, "-d", str(kola), "-r", str(plik)], check=True)
        raport = kola / f"_raport_{nazwa}.json"
        subprocess.run([str(python), "-I", "-m", "pip", "install", *wspolne, "--no-index", "--find-links", str(kola), "--dry-run",
                        "--ignore-installed", "--quiet", "--report", str(raport), "-r", str(plik)], check=True)
        zestawy[nazwa] = {normalizuj_nazwe(w["metadata"]["name"]): (w["metadata"]["name"], w["metadata"]["version"])
                          for w in json.loads(raport.read_text(encoding="utf-8"))["install"]}
    zestawy["testy"] = {k: v for k, v in zestawy["testy"].items() if k not in zestawy["program"]}
    naglowki = {"program": "Pakiety PROGRAMU w wersjach zamrozonych (kola w paczce: kola/). Plik generowany: narzedzia/zbuduj_wydanie.py --pobierz-kola.\n"
                           "# Zrodlo wersji: pip freeze interpretera, na ktorym przechodza testy. Filtr: tylko to, co pip dobiera dla requirements.txt\n"
                           "# bez pytest (pakiety wpisane i ich zaleznosci posrednie).",
                "testy": "Zestaw TESTOWY (kola w paczce: kola_testy/): pytest i jego zaleznosci, ktorych nie ma w zamrozone.txt.\n"
                         "# Instalowany tylko na zadanie: zainstaluj.cmd /testy (odbior koncowy), nigdy domyslnie na stanowisku."}
    for nazwa, plik in (("program", LISTA_PROGRAMU), ("testy", LISTA_TESTOW)):
        wiersze = sorted((f"{n}=={w}" for n, w in zestawy[nazwa].values()), key=str.lower)
        (stanowisko / plik).write_bytes(("# " + naglowki[nazwa] + "\n" + "\n".join(wiersze) + "\n").encode("ascii"))
    return len(zestawy["program"]), len(zestawy["testy"])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="zbuduj_wydanie", description='Paczka wydania programu "Stanowisko" (ZIP z kolami pip).')
    parser.add_argument("--wyjscie", type=Path, help="katalog na Stanowisko_<wersja>.zip (poza repozytorium)")
    parser.add_argument("--wersja", default=None, help="numer wersji (domyslnie z pliku WERSJA)")
    parser.add_argument("--kola", type=Path, default=None, help="katalog z kolami pip (domyslnie <wyjscie>/kola)")
    parser.add_argument("--rewizja", default="HEAD", help="commit, z ktorego powstaje paczka (domyslnie HEAD) - odtworzenie wczesniejszego wydania")
    parser.add_argument("--zrodlo", type=Path, default=None, help="katalog z plikami programu zamiast commita (proby)")
    parser.add_argument("--commit", default=None, help="z --zrodlo: opis pochodzenia wpisywany do wydanie.json")
    parser.add_argument("--data", default=None, help="z --zrodlo: data wpisow paczki, RRRR-MM-DDTGG:MM:SS (UTC)")
    parser.add_argument("--bez-samokontroli", action="store_true", help="pozwol zbudowac paczke bez modulu samokontroli (tylko proby)")
    parser.add_argument("--pobierz-kola", action="store_true", help="pobierz kola z PyPI do --kola i zapisz listy zamrozone (wymaga sieci)")
    parser.add_argument("--python", type=Path, default=Path(sys.executable), help="z --pobierz-kola: interpreter, z ktorego pochodza wersje")
    args = parser.parse_args(argv)
    try:
        if args.pobierz_kola:
            if args.kola is None:
                parser.error("--pobierz-kola wymaga --kola KATALOG")
            n_program, n_testy = pobierz_kola(args.python, args.kola)
            print(f"Kola w {args.kola}; listy zamrozone: program {n_program} pakietow, zestaw testowy {n_testy} pakietow")
            return 0
        if args.wyjscie is None:
            parser.error("podaj --wyjscie KATALOG")
        data = dt.datetime.strptime(args.data, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=dt.timezone.utc) if args.data else None
        wynik = zbuduj(args.wyjscie, args.kola or args.wyjscie / "kola", wersja=args.wersja, zrodlo=args.zrodlo, commit=args.commit, data=data,
                       bez_samokontroli=args.bez_samokontroli, rewizja=args.rewizja)
    except (BladBudowy, subprocess.CalledProcessError, ValueError) as e:
        print(f"BLAD: {e}", file=sys.stderr)
        return 1
    for ostrzezenie in wynik["ostrzezenia"]:
        print(f"OSTRZEZENIE: {ostrzezenie}")
    print(f"{wynik['plik']}: wersja {wynik['wersja']}, commit {wynik['commit'][:12]}, {wynik['pliki']} plikow + SHA256SUMS "
          f"(program {wynik['pliki_programu']}, kola {wynik['kola']}, kola testowe {wynik['kola_testy']}), "
          f"{wynik['rozmiar']} bajtow ({wynik['rozmiar'] / 2**20:.1f} MB), kontrola wlasna sum: zgodne")
    print(f"SHA-256 {wynik['sha256']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
