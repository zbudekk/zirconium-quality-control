"""T13 - higiena repozytorium: pliki zmienione od poczatku etapu 3 z kontrola.

Tylko odczyt repozytorium (polecenia ``git diff`` i ``git cat-file``); niczego nie zmienia.

Kontrole:
  1. sciezka: kazdy zmieniony plik musi pasowac do przedrostka z pliku listy (``t13_dozwolone.txt``);
     grupa ``E3`` = paczki etapu 3, inne grupy = prace spoza etapu 3 (liczone osobno), brak dopasowania = NARUSZENIE;
  2. nowe pliki tekstowe grupy E3: same bajty ASCII;
  3. konce linii nowych plikow tekstowych grupy E3: LF, a w ``.cmd`` / ``.bat`` / ``.ps1`` CRLF;
  4. brak STL (poza ``modele_plytek/``), brak plikow danych (rozszerzenia z ``DANE``) i plikow wiekszych niz ``--maks-kb``.

Odstepstwo O11 (decyzja koordynatora 20.11 nr 5): pliki z listy ``t13_wyjatki_ascii.txt`` (napisy ekranu po polsku ze znakami
diakrytycznymi - styl programu przyjety przez wlasciciela w paczkach A3 / A6) nie sa naruszeniem kontroli 2; sa wypisywane
OSOBNO ("nie-ASCII: napisy ekranu, odstepstwo O11") z liczba wierszy i bajtow nie-ASCII w kazdym. Kazdy INNY nowy plik ze
znakiem spoza ASCII jest nadal naruszeniem; pozostale kontrole (konce linii, dane, rozmiar) obejmuja takze pliki z listy.

Odstepstwo "kopie bajtowe R58" (decyzja wlasciciela nr 1 z 21.11.2026: 10 nowych plikow w ``modele_plytek/okragla_ramkowa_*``
to kopie bajtowe plikow R58 - 8 STL wiekszych niz 1024 KB i 2 ``uklad.json`` nie-ASCII z CRLF; plikow nie wolno zmieniac):
wyjatek WASKI - tylko sciezki z wierszy ``KOPIA_R58 <sciezka> <sha256> <nazwa na liscie R58>`` pliku listy i tylko wtedy,
gdy suma SHA-256 pliku z commita ``--do`` = suma z wiersza = suma tej nazwy na liscie R58 z tego samego commita
(``Ramki/wyniki_v2/raport/sha256_stl_po_R58.txt``). Wtedy powody kontroli 2-4 tego pliku sa wypisywane OSOBNO jako odstepstwo
z nazwa decyzji i nie licza sie do naruszen. Plik z listy o innej sumie (zmieniony choc o 1 bajt - takze juz po dodaniu,
status "zmieniony"), brak listy R58 albo inna suma na niej: wyjatek nie obowiazuje - wracaja zwykle naruszenia i dochodzi
naruszenie "kopia bajtowa R58: suma ...". Inne pliki w tych katalogach i te same pliki pod inna sciezka wyjatku nie maja.

Wynik: tabela licznikow i lista naruszen (sciezka + powod). Kod wyjscia 0 = brak naruszen w grupie E3 i brak plikow
poza listami, 1 = sa naruszenia, 2 = blad wywolania.

Przyklad:
  python t13_higiena.py --repo <PC-katalog>\\qc --od 2537f6f --do main --json C:\\...\\T13\\t13_wynik.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

POCZATEK_ETAPU_3 = "2537f6f"  # pierwszy commit pliku Ramki/plan_etap3_pelna_aplikacja_2026-11-16.md (16.11.2026 00:05)
CRLF = {".cmd", ".bat", ".ps1"}
DANE = {".stl", ".ply", ".obj", ".npz", ".npy", ".sqlite", ".db", ".zip", ".7z", ".whl", ".blend", ".xlsx", ".xlsm", ".csv"}
BINARNE_ZNANE = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".ico"}
GRUPA_KOPII = "KOPIA_R58"  # wiersz listy: KOPIA_R58 <sciezka w repo> <sha256> <nazwa na liscie sum R58>
LISTA_R58 = "Ramki/wyniki_v2/raport/sha256_stl_po_R58.txt"  # lista sum R58 (czytana z commita --do)
DECYZJA_KOPII = "decyzja wlasciciela nr 1 z 21.11.2026"


def git(repo: Path, *argumenty: str, wejscie: bytes | None = None) -> bytes:
    wynik = subprocess.run(["git", "-C", str(repo), *argumenty], input=wejscie, capture_output=True)
    if wynik.returncode != 0:
        raise SystemExit(f"BLAD git {' '.join(argumenty[:3])}: {wynik.stderr.decode('utf-8', 'replace').strip()}")
    return wynik.stdout


def wczytaj_liste(plik: Path) -> list[tuple[str, str]]:
    lista = []
    for wiersz in plik.read_text(encoding="utf-8").splitlines():
        wiersz = wiersz.split("#", 1)[0].rstrip()
        if not wiersz.strip():
            continue
        grupa, _, przedrostek = wiersz.partition(" ")
        if grupa.strip() == GRUPA_KOPII:  # wiersz wyjatku dla jednego pliku (wczytaj_kopie), nie przedrostek sciezki
            continue
        lista.append((przedrostek.strip(), grupa.strip()))
    return sorted(lista, key=lambda para: -len(para[0]))  # najdluzszy przedrostek wygrywa


def wczytaj_kopie(plik: Path) -> dict[str, tuple[str, str]]:
    """Wiersze ``KOPIA_R58 <sciezka> <sha256> <nazwa na liscie R58>`` pliku listy: sciezka -> (sha256, nazwa na liscie R58)."""
    kopie = {}
    for wiersz in plik.read_text(encoding="utf-8").splitlines():
        pola = wiersz.split("#", 1)[0].split()
        if not pola or pola[0] != GRUPA_KOPII:
            continue
        if len(pola) != 4 or len(pola[2]) != 64 or any(z not in "0123456789abcdef" for z in pola[2]):
            raise SystemExit(f"BLAD listy {plik.name}: wiersz {GRUPA_KOPII} ma miec postac '{GRUPA_KOPII} <sciezka> <sha256> <nazwa na liscie R58>'")
        kopie[pola[1]] = (pola[2], pola[3])
    return kopie


def sumy_r58(tresc: bytes) -> dict[str, str]:
    """Lista sum R58 (wiersze ``<sha256> *<nazwa>``): nazwa -> suma; pusta tresc (brak pliku w commicie) = pusty slownik."""
    sumy = {}
    for wiersz in tresc.decode("utf-8", "replace").splitlines():
        suma, znak, nazwa = wiersz.partition(" *")
        if znak and len(suma.strip()) == 64:
            sumy[nazwa.strip()] = suma.strip().lower()
    return sumy


def kopia_zgodna(sciezka: str, tresc: bytes, kopie: dict[str, tuple[str, str]], r58: dict[str, str]) -> tuple[bool, str]:
    """(czy plik z listy wyjatkow jest kopia bajtowa R58, suma pliku): suma pliku = suma z wiersza listy = suma na liscie R58."""
    suma = hashlib.sha256(tresc).hexdigest()
    oczekiwana, nazwa = kopie[sciezka]
    return suma == oczekiwana == r58.get(nazwa), suma


def grupa_sciezki(sciezka: str, lista: list[tuple[str, str]]) -> str | None:
    for przedrostek, grupa in lista:
        if sciezka.startswith(przedrostek):
            return grupa
    return None


def zmienione(repo: Path, od: str, do: str) -> list[tuple[str, str]]:
    surowe = git(repo, "diff", "--name-status", "--no-renames", "-z", od, do).split(b"\0")
    pary = []
    for i in range(0, len(surowe) - 1, 2):
        pary.append((surowe[i].decode("ascii"), surowe[i + 1].decode("utf-8", "replace")))
    return pary


def tresci(repo: Path, do: str, sciezki: list[str]) -> dict[str, bytes]:
    """Tresc plikow z commita ``do`` jednym procesem ``git cat-file --batch``."""
    if not sciezki:
        return {}
    wejscie = "".join(f"{do}:{s}\n" for s in sciezki).encode("utf-8")
    dane = git(repo, "cat-file", "--batch", wejscie=wejscie)
    wynik, pozycja = {}, 0
    for sciezka in sciezki:
        koniec = dane.index(b"\n", pozycja)
        naglowek = dane[pozycja:koniec].split()
        pozycja = koniec + 1
        if naglowek[-1] == b"missing":
            wynik[sciezka] = b""
            continue
        rozmiar = int(naglowek[2])
        wynik[sciezka] = dane[pozycja:pozycja + rozmiar]
        pozycja += rozmiar + 1
    return wynik


def wczytaj_wyjatki(plik: Path | None) -> set[str]:
    """Sciezki plikow z napisami ekranu (odstepstwo O11); brak pliku listy = brak wyjatkow."""
    if plik is None or not plik.is_file():
        return set()
    return {w.split("#", 1)[0].strip() for w in plik.read_text(encoding="utf-8").splitlines() if w.split("#", 1)[0].strip()}


def wiersze_nie_ascii(tresc: bytes) -> int:
    return sum(1 for wiersz in tresc.split(b"\n") if any(bajt > 127 for bajt in wiersz))


def ocen_nowy(sciezka: str, tresc: bytes, maks_kb: int) -> list[str]:
    powody = []
    rozszerzenie = Path(sciezka).suffix.lower()
    if rozszerzenie == ".stl" and "/modele_plytek/" not in sciezka:
        powody.append("STL poza modele_plytek")
    elif rozszerzenie in DANE and rozszerzenie != ".stl":
        powody.append(f"plik danych ({rozszerzenie})")
    if len(tresc) > maks_kb * 1024:
        powody.append(f"duzy plik ({len(tresc) // 1024} KB > {maks_kb} KB)")
    if rozszerzenie in BINARNE_ZNANE or rozszerzenie in DANE:  # pliki danych ocenia regula wyzej (STL, plik danych)
        return powody
    if b"\0" in tresc[:8000]:  # uwaga 22 recenzji: plik tekstowy UTF-16 (bajty NUL) nie moze przejsc jako "binarny"
        powody.append(f"bajty NUL w pliku {rozszerzenie or 'bez rozszerzenia'} spoza listy binarnych (np. tekst UTF-16)")
        return powody
    nie_ascii = sum(1 for bajt in tresc if bajt > 127)
    if nie_ascii:
        powody.append(f"nie ASCII ({nie_ascii} bajtow)")
    crlf = tresc.count(b"\r\n")
    lf = tresc.count(b"\n") - crlf
    samotne_cr = tresc.count(b"\r") - crlf
    if samotne_cr:
        powody.append(f"konce linii: {samotne_cr} x samotne CR")
    if rozszerzenie in CRLF:
        if lf:
            powody.append(f"konce linii: {lf} x LF w pliku {rozszerzenie} (ma byc CRLF)")
    elif crlf:
        powody.append(f"konce linii: {crlf} x CRLF (ma byc LF)")
    return powody


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="T13: pliki zmienione od poczatku etapu 3 z kontrola sciezek, ASCII, koncow linii i danych")
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="katalog repozytorium (domyslnie biezacy)")
    parser.add_argument("--od", default=POCZATEK_ETAPU_3, help=f"commit poczatku etapu (domyslnie {POCZATEK_ETAPU_3})")
    parser.add_argument("--do", default="main", help="commit koncowy (domyslnie main)")
    parser.add_argument("--dozwolone", type=Path, default=Path(__file__).with_name("t13_dozwolone.txt"), help="plik listy przedrostkow sciezek")
    parser.add_argument("--wyjatki-ascii", type=Path, default=Path(__file__).with_name("t13_wyjatki_ascii.txt"),
                        help="plik listy sciezek z napisami ekranu (odstepstwo O11: nie-ASCII raportowane osobno)")
    parser.add_argument("--maks-kb", type=int, default=1024, help="prog duzego pliku w KB (domyslnie 1024)")
    parser.add_argument("--json", type=Path, default=None, help="zapisz pelny wynik do pliku JSON")
    parser.add_argument("--pokaz", type=int, default=60, help="ile naruszen wypisac na ekran (domyslnie 60; wszystkie sa w --json)")
    args = parser.parse_args(argv)

    lista = wczytaj_liste(args.dozwolone)
    pary = zmienione(args.repo, args.od, args.do)
    nowe = [s for status, s in pary if status == "A"]
    kopie = wczytaj_kopie(args.dozwolone)
    zmienione_kopie = [s for status, s in pary if status == "M" and s in kopie]
    zawartosc = tresci(args.repo, args.do, nowe + zmienione_kopie + [LISTA_R58])
    r58 = sumy_r58(zawartosc.get(LISTA_R58, b""))
    liczniki: dict[str, dict[str, int]] = {}
    naruszenia, poza_etapem, odstepstwo_ascii, odstepstwo_kopie = [], [], [], []
    wyjatki = wczytaj_wyjatki(args.wyjatki_ascii)
    for status, sciezka in pary:
        grupa = grupa_sciezki(sciezka, lista)
        nazwa_grupy = grupa or "POZA_LISTAMI"
        licznik = liczniki.setdefault(nazwa_grupy, {"A": 0, "M": 0, "D": 0, "inne": 0})
        licznik[status if status in licznik else "inne"] += 1
        if grupa is None:
            naruszenia.append({"sciezka": sciezka, "status": status, "powod": "sciezka poza listami paczek"})
        if sciezka in kopie and status in ("A", "M"):  # kopia bajtowa R58: wyjatek tylko przy zgodnej sumie
            zgodna, suma = kopia_zgodna(sciezka, zawartosc.get(sciezka, b""), kopie, r58)
            if zgodna and grupa == "E3":
                if status == "A":
                    odstepstwo_kopie.append({"sciezka": sciezka, "status": status, "sha256": suma, "grupa": nazwa_grupy,
                                             "powody": ocen_nowy(sciezka, zawartosc.get(sciezka, b""), args.maks_kb)})
                continue
            naruszenia.append({"sciezka": sciezka, "status": status, "grupa": nazwa_grupy,
                               "powod": f"kopia bajtowa R58: suma SHA-256 pliku ({suma[:16]}...) inna niz w wierszu {GRUPA_KOPII} listy albo "
                                        f"na liscie sum R58 - wyjatek ({DECYZJA_KOPII}) nie obowiazuje"})
        if status != "A":
            continue
        for powod in ocen_nowy(sciezka, zawartosc.get(sciezka, b""), args.maks_kb):
            wpis = {"sciezka": sciezka, "status": status, "powod": powod, "grupa": nazwa_grupy}
            if grupa == "E3" and sciezka in wyjatki and powod.startswith("nie ASCII"):
                wpis["wierszy_nie_ascii"] = wiersze_nie_ascii(zawartosc.get(sciezka, b""))
                odstepstwo_ascii.append(wpis)
                continue
            (naruszenia if grupa in ("E3", None) else poza_etapem).append(wpis)
    nieuzyte = sorted(wyjatki - {w["sciezka"] for w in odstepstwo_ascii})
    kopie_bez_trafienia = sorted(set(kopie) - {s for _, s in pary})

    hash_od = git(args.repo, "rev-parse", "--short", args.od).decode().strip()
    hash_do = git(args.repo, "rev-parse", "--short", args.do).decode().strip()
    print(f"T13 higiena repo: {hash_od}..{hash_do}, zmienionych plikow {len(pary)}, w tym nowych {len(nowe)}")
    print(f"{'grupa':<16}{'nowe':>6}{'zmien.':>8}{'usun.':>7}")
    for nazwa in sorted(liczniki):
        licznik = liczniki[nazwa]
        print(f"{nazwa:<16}{licznik['A']:>6}{licznik['M']:>8}{licznik['D']:>7}")
    print(f"NARUSZENIA (grupa E3 i sciezki poza listami): {len(naruszenia)}")
    for wpis in naruszenia[:args.pokaz]:
        print(f"  {wpis['status']} {wpis['sciezka'].encode('ascii', 'backslashreplace').decode()} -> {wpis['powod']}")
    if len(naruszenia) > args.pokaz:
        print(f"  ... i {len(naruszenia) - args.pokaz} dalszych (pelna lista w --json)")
    print(f"nie-ASCII: napisy ekranu, odstepstwo O11 (nie licza sie do naruszen): {len(odstepstwo_ascii)} plikow z {len(wyjatki)} na liscie")
    for wpis in odstepstwo_ascii:
        print(f"  {wpis['status']} {wpis['sciezka']} -> {wpis['wierszy_nie_ascii']} wierszy nie-ASCII ({wpis['powod'].split('(')[1].rstrip(')')})")
    for sciezka in nieuzyte:
        print(f"  (pozycja listy wyjatkow bez trafienia - plik nie jest nowy albo jest juz ASCII: {sciezka})")
    print(f"kopie bajtowe R58 w modele_plytek, odstepstwo: {DECYZJA_KOPII} (nie licza sie do naruszen; suma SHA-256 = lista R58): "
          f"{len(odstepstwo_kopie)} plikow z {len(kopie)} na liscie")
    for wpis in odstepstwo_kopie:
        print(f"  {wpis['status']} {wpis['sciezka']} -> suma zgodna ({wpis['sha256'][:16]}); pominiete: {', '.join(wpis['powody']) or 'nic'}")
    for sciezka in kopie_bez_trafienia:
        print(f"  (pozycja listy kopii R58 bez trafienia - pliku nie ma wsrod zmienionych: {sciezka})")
    print(f"UWAGI w grupach spoza etapu 3 (nie licza sie do wyniku T13, do oceny koordynatora): {len(poza_etapem)}")
    powody: dict[str, int] = {}
    for wpis in poza_etapem:
        klucz = f"{wpis['grupa']}: {wpis['powod'].split(' (')[0].split(': ')[0]}"
        powody[klucz] = powody.get(klucz, 0) + 1
    for klucz in sorted(powody):
        print(f"  {klucz}: {powody[klucz]}")
    if args.json:
        args.json.write_text(json.dumps({"od": hash_od, "do": hash_do, "zmienionych": len(pary), "nowych": len(nowe), "liczniki": liczniki,
                                         "naruszenia": naruszenia, "odstepstwo_o11_napisy_ekranu": odstepstwo_ascii,
                                         "wyjatki_bez_trafienia": nieuzyte, "decyzja_kopie_r58": DECYZJA_KOPII,
                                         "odstepstwo_kopie_r58": odstepstwo_kopie, "kopie_r58_bez_trafienia": kopie_bez_trafienia,
                                         "uwagi_poza_etapem": poza_etapem}, ensure_ascii=True, indent=1) + "\n",
                             encoding="ascii", newline="\n")
    odstepstwa = ([f"{len(odstepstwo_ascii)} plikow napisow ekranu nie-ASCII"] if odstepstwo_ascii else []) + (
        [f"{len(odstepstwo_kopie)} kopii bajtowych R58 - {DECYZJA_KOPII}"] if odstepstwo_kopie else [])
    if naruszenia:
        werdykt = f"FAIL ({len(naruszenia)} naruszen)"
    elif odstepstwo_ascii:
        werdykt = f"ZAL z odstepstwem O11 (0 naruszen; {'; '.join(odstepstwa)})"
    elif odstepstwo_kopie:
        werdykt = f"ZAL z odstepstwem (0 naruszen; {'; '.join(odstepstwa)})"
    else:
        werdykt = "ZAL (0 naruszen)"
    print("WYNIK T13:", werdykt)
    return 0 if not naruszenia else 1


if __name__ == "__main__":
    sys.exit(main())
