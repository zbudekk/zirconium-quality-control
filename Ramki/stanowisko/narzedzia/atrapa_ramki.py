"""Atrapa ramki swietlnej w sieci lokalnej - program ramki z atrapa sprzetu (bez elektroniki).

Do testow strony laptopa (indicate, A12) i do pracy bez ramek:
  python narzedzia/atrapa_ramki.py --rola P [--port 8765] [--host 127.0.0.1] [--sterowanie]
Wypisuje jedna linie "ATRAPA_RAMKI port=<port> start_id=<id> rola=<W|P>" i czyta polecenia
ze standardowego wejscia: "plytka <n>", "klawisz <nazwa>", "stan", "koniec". Koniec wejscia
(EOF) = koniec programu (proces potomny testu nie zostaje po tescie). --bez-konsoli: dziala do
Ctrl+C. --sterowanie wlacza zasoby /atrapa/klatka, /atrapa/plytka, /atrapa/klawisz (zdalne
sterowanie atrapa z innego procesu). Domyslnie slucha tylko na 127.0.0.1.

Z kodu (ten sam proces):
  from atrapa_ramki import uruchom_atrape
  program, atrapa = uruchom_atrape("P", port=0); ...; program.zatrzymaj()
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import threading
from pathlib import Path

STANOWISKO = Path(__file__).resolve().parent.parent
if str(STANOWISKO) not in sys.path:
    sys.path.insert(0, str(STANOWISKO))

from ramka.program import Konfiguracja, ProgramRamki  # noqa: E402
from ramka.protokol import KLAWISZE  # noqa: E402
from ramka.sprzet_atrapa import SprzetAtrapa  # noqa: E402


def uruchom_atrape(rola: str = "P", port: int = 0, host: str = "127.0.0.1", sterowanie: bool = False, **konf):
    """Startuje program ramki z atrapa sprzetu; zwraca (program, atrapa). Port 0 = losowy wolny."""
    atrapa = SprzetAtrapa()
    k = Konfiguracja(rola=rola, host=host, port=port, sprzet="atrapa", sterowanie_atrapy=sterowanie, **konf)
    program = ProgramRamki(k, sprzet=atrapa)
    program.uruchom()
    return program, atrapa


def _polecenie(linia: str, program, atrapa) -> bool:
    czesci = linia.split()
    if not czesci:
        return True
    if czesci[0] == "koniec":
        return False
    if czesci[0] == "plytka" and len(czesci) == 2 and czesci[1].isdigit() and int(czesci[1]) <= 7:
        atrapa.poloz_plytke(int(czesci[1]))
    elif czesci[0] == "klawisz" and len(czesci) == 2 and czesci[1] in KLAWISZE:
        atrapa.nacisnij(czesci[1])
    elif czesci[0] == "stan":
        print(json.dumps(program.stan(None), sort_keys=True), flush=True)
    else:
        print("polecenia: plytka <0-7> | klawisz <" + "|".join(KLAWISZE) + "> | stan | koniec", flush=True)
    return True


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Atrapa ramki swietlnej (program ramki bez elektroniki).")
    p.add_argument("--rola", choices=("W", "P"), default="P")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--sterowanie", action="store_true", help="zasoby /atrapa/* do sterowania z innego procesu")
    p.add_argument("--bez-konsoli", action="store_true", help="nie czytaj polecen; dzialaj do Ctrl+C")
    p.add_argument("--limit-lacznosci", type=float, default=30.0)
    a = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    program, atrapa = uruchom_atrape(a.rola, a.port, a.host, a.sterowanie, limit_lacznosci_s=a.limit_lacznosci)
    _, port = program.serwer.server_address[:2]
    print(f"ATRAPA_RAMKI port={port} start_id={program.logika.start_id} rola={a.rola}", flush=True)
    koniec = threading.Event()
    try:
        if a.bez_konsoli:
            while not koniec.wait(0.5):
                pass
        else:
            for linia in sys.stdin:
                if not _polecenie(linia, program, atrapa):
                    break
    except KeyboardInterrupt:
        pass
    finally:
        program.zatrzymaj()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
