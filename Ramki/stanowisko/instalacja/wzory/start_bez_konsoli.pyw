"""Start programu wersji biezacej BEZ okna konsoli - cel ikon "Stanowisko" i "Dzien skanera" na pulpicie (E3-I1).

    pythonw.exe -I -B <KATALOG>\\start_bez_konsoli.pyw stanowisko|dzien_skanera [opcje programu]

Plik zapisany przez instalator (wzor: program\\instalacja\\wzory) - nie zmieniaj; ustawienia sa w ustawienia.toml.
Robi to samo co Stanowisko.cmd / Dzien_skanera.cmd: wersja z wersja_biezaca.txt, jej srodowisko wirtualne, katalog programu
jako biezacy, PYTHONUTF8 / PYTHONDONTWRITEBYTECODE / PYTHONNOUSERSITE, bez PYTHONPATH / PYTHONHOME, --ustawienia tego katalogu
(Dzien skanera: takze --dane <KATALOG>\\dane\\dzien_skanera). Program startuje przez python.exe srodowiska z UKRYTA konsola
(procesy potomne, np. pip albo proces roboczy silnika, nie otwieraja okien). Wyjscie programu trafia do
<KATALOG>\\dane\\ostatni_start_<cel>.txt. Brak gotowej wersji albo blad programu (kod inny niz 0, a dla "stanowisko" takze
inny niz 3 = program juz dziala) = okienko z komunikatem; zmienna STANOWISKO_START_BEZ_OKIENEK=1 (proby) - komunikat na stderr.
Kod wyjscia = kod programu; brak wersji = 4, nieznany cel = 2.
"""
import os
import subprocess
import sys
from pathlib import Path

CELE = {"stanowisko": ("stanowisko.aplikacja", "Stanowisko", (0, 3)), "dzien_skanera": ("stanowisko.dzien_skanera", "Dzien skanera", (0,))}


def komunikat(tekst):
    if os.environ.get("STANOWISKO_START_BEZ_OKIENEK") == "1" or os.name != "nt":
        if sys.stderr is not None:
            print(tekst, file=sys.stderr)
        return
    import ctypes

    ctypes.windll.user32.MessageBoxW(None, tekst, "Stanowisko", 0x10)


def main(argv):
    katalog = Path(__file__).resolve().parent
    if not argv or argv[0] not in CELE:
        komunikat("Nieznany cel startu: %s (znane: %s)." % (argv[0] if argv else "brak", ", ".join(CELE)))
        return 2
    modul, nazwa, kody_ok = CELE[argv[0]]
    try:
        wersja = (katalog / "wersja_biezaca.txt").read_text(encoding="ascii").strip()
    except (OSError, UnicodeDecodeError):
        wersja = ""
    w = katalog / "wersje" / wersja
    python = w / "venv" / "Scripts" / ("python.exe" if os.name == "nt" else "python")
    if not wersja or not python.is_file() or (w / "NIEDOKONCZONA.txt").exists():
        komunikat('W folderze %s nie ma gotowej wersji programu (wersja_biezaca.txt: "%s").\n\n'
                  "Uruchom ponownie instalacje z paczki wydania (Instaluj.cmd)." % (katalog, wersja))
        return 4
    srodowisko = {k: v for k, v in os.environ.items() if k.upper() not in ("PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP", "VIRTUAL_ENV")}
    srodowisko.update(PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1", PYTHONNOUSERSITE="1")
    srodowisko.pop("STANOWISKO_START_BEZ_OKIENEK", None)
    polecenie = [str(python), "-m", modul, "--ustawienia", str(katalog / "ustawienia.toml")]
    if argv[0] == "dzien_skanera":
        polecenie += ["--dane", str(katalog / "dane" / "dzien_skanera")]
    polecenie += list(argv[1:])
    plik_wyjscia = katalog / "dane" / ("ostatni_start_%s.txt" % argv[0])
    try:
        plik_wyjscia.parent.mkdir(parents=True, exist_ok=True)
        wyjscie = open(plik_wyjscia, "wb")
    except OSError:
        plik_wyjscia, wyjscie = None, subprocess.DEVNULL
    try:
        kod = subprocess.run(polecenie, cwd=str(w / "program"), env=srodowisko, stdin=subprocess.DEVNULL, stdout=wyjscie,
                             stderr=subprocess.STDOUT, creationflags=0x08000000 if os.name == "nt" else 0).returncode  # CREATE_NO_WINDOW
    except OSError as e:
        komunikat("Nie mozna uruchomic programu %s (%s: %s)." % (nazwa, type(e).__name__, e))
        return 4
    finally:
        if plik_wyjscia is not None:
            wyjscie.close()
    if kod not in kody_ok:
        komunikat("Program %s zakonczyl sie bledem (kod %d).\n\nSzczegoly: %s\nGdy to sie powtarza, przekaz ten plik razem z "
                  "plikiem dziennik_instalacji.txt." % (nazwa, kod, plik_wyjscia or "brak (nie mozna zapisac pliku)"))
    return kod


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
