"""Serwer HTTP + JSON ramki (http.server z biblioteki standardowej).

Zasoby (szczegoly i kody bledow: README.md, "Protokol v1"):
  GET    /stan                                   stan ramki
  GET    /zdarzenia?od=N&czekaj=S&limit=L&start_id=X   zdarzenia o numerach > N (dlugie odpytywanie)
  PUT    /plan                                   plan diod (tresc JSON)
  DELETE /plan[?plan_id=X]                       zgas: brak planu
  PUT    /tryb                                   stan ramki (gotowa, skanowanie, ...)
Tylko atrapa uruchomiona z flaga sterowania (nigdy na Raspberry Pi):
  GET /atrapa/klatka, PUT /atrapa/plytka, PUT /atrapa/klawisz

Logi: metoda, nazwa zasobu (znanego) i status - nigdy tresc zadania ani nieznana sciezka.
"""
from __future__ import annotations

import json
import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

from . import WERSJA, protokol
from .protokol import BladProtokolu

log = logging.getLogger("ramka.serwer")

TRASY = {
    "/stan": ("GET",),
    "/zdarzenia": ("GET",),
    "/plan": ("PUT", "DELETE"),
    "/tryb": ("PUT",),
}
TRASY_ATRAPY = {
    "/atrapa/klatka": ("GET",),
    "/atrapa/plytka": ("PUT",),
    "/atrapa/klawisz": ("PUT",),
}
PARAMETRY = {"od", "czekaj", "limit", "start_id", "plan_id"}


def _parametr(q: dict, nazwa: str):
    v = q.get(nazwa)
    if not v:
        return None
    if len(v) != 1:
        raise BladProtokolu(400, "zly_parametr", f"parametr {nazwa} podany wiecej niz raz")
    return v[0]


def _int_param(q: dict, nazwa: str, domyslna: int, lo: int, hi: int) -> int:
    v = _parametr(q, nazwa)
    if v is None:
        return domyslna
    if not v.isdigit() or len(v) > 15:
        raise BladProtokolu(400, "zly_parametr", f"parametr {nazwa}: liczba calkowita {lo}..{hi}")
    n = int(v)
    if not (lo <= n <= hi):
        raise BladProtokolu(400, "zly_parametr", f"parametr {nazwa}: liczba calkowita {lo}..{hi}")
    return n


def _float_param(q: dict, nazwa: str, domyslna: float) -> float:
    v = _parametr(q, nazwa)
    if v is None:
        return domyslna
    try:
        x = float(v)
    except ValueError:
        raise BladProtokolu(400, "zly_parametr", f"parametr {nazwa}: liczba") from None
    if not (0.0 <= x <= 3600.0):
        raise BladProtokolu(400, "zly_parametr", f"parametr {nazwa}: 0..3600")
    return x


class ObslugaRamki(BaseHTTPRequestHandler):
    server_version = "ramka/" + WERSJA
    sys_version = ""
    protocol_version = "HTTP/1.0"
    timeout = 15  # sekundy na odczyt naglowkow i tresci (socket timeout)

    def log_message(self, format, *args):  # noqa: A002 - podpis z BaseHTTPRequestHandler
        pass  # wlasny log w _obsluz (bez sciezki od klienta)

    def log_error(self, format, *args):  # noqa: A002
        log.warning("blad polaczenia HTTP od %s", self.client_address[0])

    def do_GET(self):
        self._obsluz("GET")

    def do_PUT(self):
        self._obsluz("PUT")

    def do_DELETE(self):
        self._obsluz("DELETE")

    def do_POST(self):
        self._obsluz("POST")

    def do_PATCH(self):
        self._obsluz("PATCH")

    def do_HEAD(self):
        self._obsluz("HEAD")

    def _czytaj_tresc(self):
        """Czyta tresc wg Content-Length. Zwraca (bajty albo None, blad albo None)."""
        dl = self.headers.get("Content-Length")
        if dl is None:
            return None, None
        dl = dl.strip()
        if not dl.isdigit():
            return None, BladProtokolu(400, "zla_dlugosc", "naglowek Content-Length")
        n = int(dl)
        if n > protokol.MAX_TRESC:
            if n <= protokol.MAX_TRESC_ODCZYT:
                reszta = n
                while reszta > 0:
                    b = self.rfile.read(min(65536, reszta))
                    if not b:
                        break
                    reszta -= len(b)
            self.close_connection = True
            return None, BladProtokolu(413, "za_duza_tresc", f"tresc ponad {protokol.MAX_TRESC} bajtow")
        dane = self.rfile.read(n) if n else b""
        if len(dane) != n:
            return None, BladProtokolu(400, "zla_dlugosc", "tresc krotsza niz Content-Length")
        return dane, None

    def _obsluz(self, metoda: str):
        program = self.server.program
        trasa = "?"
        status, odp = 500, None
        try:
            tresc, blad_tresci = self._czytaj_tresc()
            url = urlsplit(self.path)
            trasy = dict(TRASY)
            if program.konf.sterowanie_atrapy:
                trasy.update(TRASY_ATRAPY)
            if url.path not in trasy:
                raise BladProtokolu(404, "nieznany_zasob", "nieznany zasob")
            trasa = url.path
            if metoda not in trasy[url.path]:
                raise BladProtokolu(405, "zla_metoda", "metoda niedozwolona dla zasobu")
            q = parse_qs(url.query, keep_blank_values=True)
            if set(q) - PARAMETRY:
                raise BladProtokolu(400, "zly_parametr", "nieznany parametr")
            laptop = self.headers.get("X-Laptop-Id")
            if laptop is not None:
                laptop = protokol.sprawdz_id_laptopa(laptop)
            elif metoda != "GET":
                raise BladProtokolu(400, "brak_laptopa", "naglowek X-Laptop-Id jest wymagany")
            dane = None
            if metoda == "PUT":
                if blad_tresci is not None:
                    raise blad_tresci
                if tresc is None:
                    raise BladProtokolu(411, "brak_dlugosci", "naglowek Content-Length jest wymagany")
                try:
                    dane = json.loads(tresc.decode("utf-8"))
                except (UnicodeDecodeError, ValueError, RecursionError):
                    raise BladProtokolu(400, "zly_json", "tresc nie jest poprawnym JSON (UTF-8)") from None
                if not isinstance(dane, dict):
                    raise BladProtokolu(400, "zly_json", "tresc nie jest obiektem JSON")
            elif blad_tresci is not None and blad_tresci.status == 413:
                raise blad_tresci
            status, odp = self._wykonaj(program, metoda, trasa, q, laptop, dane)
        except BladProtokolu as b:
            status, odp = b.status, b.jako_json()
        except Exception:  # noqa: BLE001 - serwer ma dzialac dalej
            log.exception("blad wewnetrzny przy %s %s", metoda, trasa)
            status, odp = 500, {"protokol": protokol.PROTOKOL,
                                "blad": {"kod": "blad_wewnetrzny", "opis": "blad wewnetrzny ramki"}}
        # odpytywanie (GET) co kilka sekund tylko na poziomie DEBUG - log w RAM ramki nie puchnie
        log.log(logging.DEBUG if metoda == "GET" and status == 200 else logging.INFO,
                "%s %s %s -> %d", self.client_address[0], metoda, trasa, status)
        self._odpowiedz(status, odp)

    def _wykonaj(self, program, metoda, trasa, q, laptop, dane):
        if trasa == "/stan":
            return 200, program.stan(laptop)
        if trasa == "/zdarzenia":
            od = _int_param(q, "od", 0, 0, 10 ** 12)
            czekaj = _float_param(q, "czekaj", 0.0)
            limit = _int_param(q, "limit", 100, 1, protokol.LIMIT_ZDARZEN_MAX)
            start_id = _parametr(q, "start_id")
            return 200, program.zdarzenia(laptop, od, czekaj, limit, start_id)
        if trasa == "/plan" and metoda == "PUT":
            return 200, program.plan(laptop, dane)
        if trasa == "/plan" and metoda == "DELETE":
            plan_id = _parametr(q, "plan_id")
            if plan_id is not None and not protokol.WZOR_ID.match(plan_id):
                raise BladProtokolu(400, "zly_parametr", "parametr plan_id")
            return 200, program.usun_plan(laptop, plan_id)
        if trasa == "/tryb":
            return 200, program.tryb(laptop, dane)
        if trasa == "/atrapa/klatka":
            return 200, program.atrapa_klatka()
        if trasa == "/atrapa/plytka":
            return 200, program.atrapa_plytka(dane)
        if trasa == "/atrapa/klawisz":
            return 200, program.atrapa_klawisz(dane)
        raise BladProtokolu(404, "nieznany_zasob", "nieznany zasob")

    def _odpowiedz(self, status: int, odp) -> None:
        cialo = json.dumps(odp, ensure_ascii=True, separators=(",", ":")).encode("ascii") if odp is not None else b""
        try:
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(cialo)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Connection", "close")
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(cialo)
        except OSError:
            log.info("klient rozlaczyl sie przed odpowiedzia (%s)", self.client_address[0])


class SerwerRamki(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True
    request_queue_size = 32

    def __init__(self, adres, program):
        self.program = program
        super().__init__(adres, ObslugaRamki)
