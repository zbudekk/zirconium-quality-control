"""Posrednik TCP z zapisem ruchu - do T5 i T9 (ruch sieciowy programu do ramki).

Program laczy sie z posrednikiem (``--sluchaj``), posrednik przekazuje wszystko bez zmian do ramki (``--cel``) i dopisuje
surowe bajty obu kierunkow do pliku ``--zapis``. Kazdy kawalek poprzedza wiersz ``#RUCH <nr polaczenia> <kierunek> <bajtow>``
(kierunek: ``>`` program -> ramka, ``<`` ramka -> program). Plik zapisu przeszukuje potem ``t9_dane_osobowe.py --cel``.

Przyklad (ramka na porcie 8765, program ma w ustawieniach port 8766 i host posrednika):
  python posrednik_ruchu.py --sluchaj 127.0.0.1:8766 --cel <adres-IP>:8765 --zapis C:\\...\\T5\\ruch_ramka_w.bin

Koniec: Ctrl+C albo ``--czas S``. Na koniec wypisuje liczbe polaczen i bajtow w obu kierunkach.
Zapis ruchu moze zawierac dane - NIE dodawaj go do repozytorium; do dowodow idzie tylko wynik ``t9_dane_osobowe.py``.
"""
from __future__ import annotations

import argparse
import socket
import sys
import threading
import time
from pathlib import Path


def adres(tekst: str) -> tuple[str, int]:
    host, _, port = tekst.rpartition(":")
    return host or "127.0.0.1", int(port)


class Posrednik:
    def __init__(self, sluchaj: tuple[str, int], cel: tuple[str, int], zapis: Path) -> None:
        self.cel = cel
        self.plik = zapis.open("ab")
        self.zamek = threading.Lock()
        self.polaczen = 0
        self.bajtow = {">": 0, "<": 0}
        self.bledow_celu = 0
        self.gniazdo = socket.create_server(sluchaj)
        self.gniazdo.settimeout(0.2)
        self.port = self.gniazdo.getsockname()[1]
        self.koniec = threading.Event()

    def _zapisz(self, numer: int, kierunek: str, dane: bytes) -> None:
        with self.zamek:
            self.bajtow[kierunek] += len(dane)
            self.plik.write(f"#RUCH {numer} {kierunek} {len(dane)}\n".encode("ascii") + dane + b"\n")
            self.plik.flush()

    def _pompa(self, numer: int, kierunek: str, zrodlo: socket.socket, ujscie: socket.socket) -> None:
        try:
            while True:
                dane = zrodlo.recv(65536)
                if not dane:
                    break
                self._zapisz(numer, kierunek, dane)
                ujscie.sendall(dane)
        except OSError:
            pass
        finally:
            for gniazdo in (ujscie, zrodlo):
                try:
                    gniazdo.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                gniazdo.close()

    def petla(self, czas_s: float | None = None) -> None:
        start = time.monotonic()
        while not self.koniec.is_set() and (czas_s is None or time.monotonic() - start < czas_s):
            try:
                klient, _ = self.gniazdo.accept()
            except TimeoutError:
                continue
            except OSError:
                break
            self.polaczen += 1
            numer = self.polaczen
            try:
                serwer = socket.create_connection(self.cel, timeout=5.0)
                serwer.settimeout(None)
            except OSError:
                self.bledow_celu += 1  # ramka wylaczona: program dostaje zerwane polaczenie, jak bez posrednika
                klient.close()
                continue
            threading.Thread(target=self._pompa, args=(numer, ">", klient, serwer), daemon=True).start()
            threading.Thread(target=self._pompa, args=(numer, "<", serwer, klient), daemon=True).start()
        self.gniazdo.close()

    def zamknij(self) -> None:
        self.koniec.set()
        time.sleep(0.3)
        with self.zamek:
            self.plik.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Posrednik TCP z zapisem ruchu program <-> ramka (T5, T9)")
    parser.add_argument("--sluchaj", required=True, metavar="HOST:PORT", help="adres, z ktorym laczy sie program")
    parser.add_argument("--cel", required=True, metavar="HOST:PORT", help="adres ramki (albo atrapy ramki)")
    parser.add_argument("--zapis", required=True, type=Path, help="plik zapisu ruchu (dopisywany)")
    parser.add_argument("--czas", type=float, default=None, metavar="S", help="zakoncz po S sekundach (domyslnie do Ctrl+C)")
    args = parser.parse_args(argv)
    posrednik = Posrednik(adres(args.sluchaj), adres(args.cel), args.zapis)
    print(f"POSREDNIK port={posrednik.port} cel={args.cel} zapis={args.zapis}", flush=True)
    try:
        posrednik.petla(args.czas)
    except KeyboardInterrupt:
        pass
    posrednik.zamknij()
    print(f"POSREDNIK koniec: polaczen {posrednik.polaczen}, nieudanych polaczen z celem {posrednik.bledow_celu}, "
          f"bajtow do ramki {posrednik.bajtow['>']}, bajtow z ramki {posrednik.bajtow['<']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
