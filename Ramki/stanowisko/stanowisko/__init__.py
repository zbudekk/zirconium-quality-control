"""Program stanowiska kontroli cyrkonii (plan wdrożenia v2)."""
import sys as _sys


def _bez_wmi() -> None:
    """E3-A11w: wylacza zapytania WMI modulu ``platform`` w kazdym procesie programu (okno, proces roboczy silnika, wiersz
    polecen, samokontrola) - wolane przy imporcie pakietu, czyli przed ``import trimesh`` i Open3D.

    Powod (raport E3-A11w): ``import trimesh`` wola ``platform.system()``, a od Pythona 3.12 to zapytanie WMI (modul ``_wmi``)
    w osobnym watku systemowym z limitem czasu. Gdy WMI nie odpowie w limicie (konto bez dostepu do WMI - na PC, konto
    <konto-PC>, kazde wywolanie; wolno startujaca usluga WMI - na dowolnym komputerze), wywolanie wraca z bledem, a porzucony
    watek po ok. 5 s zamyka uchwyt odczytany ze stosu watku wywolujacego (struktura lokalna funkcji, ktora juz wrocila), czyli
    LOSOWY uchwyt procesu: zawieszenia (watki stoja w module ladujacym Windows), naruszenia pamieci, "DLL load failed",
    procesy potomne z kodem 0xC0000142. Bez ``_wmi`` modul ``platform`` bierze te same dane ze sciezek zapasowych
    (``sys.getwindowsversion()``, zmienne srodowiska). Poza Windows i w Pythonie bez ``_wmi`` nic nie zmienia."""
    if _sys.platform != "win32":
        return

    def niedostepne(*_argumenty, **_nazwane):
        raise OSError("not supported")  # ten sam wyjatek, ktory zglasza platform bez modulu _wmi

    if _sys.modules.get("_wmi") is None:
        _sys.modules["_wmi"] = None  # ``import _wmi`` w platform konczy sie ImportError -> sciezki zapasowe
    platforma = _sys.modules.get("platform")
    if platforma is not None and hasattr(platforma, "_wmi_query"):
        platforma._wmi_query = niedostepne  # platform zaladowany wczesniej (np. przez pytest) ma juz prawdziwy _wmi


_bez_wmi()
