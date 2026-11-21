WERDYKT T13 (pierwszy przebieg, commit paczki 571e186): ZAL z odstepstwem O11 i O10 (naruszen 0; 7 plikow napisow ekranu nie-ASCII z 7 na liscie; kontrola na poziomie katalogow paczek)

# T13 - Higiena repo - pierwszy przebieg (odbior 21.11.2026)

Wykonawca: sesja wykonawcy testow koncowych (T12, T7, T13). Godzina: 03:07:24-03:07:27 (polecenia planu), 03:13-03:16 (kontrola
reczna i niezalezna). Krok lekki - bez blokady. Repo: `<REPO>` = `<PC-katalog>\t0\repo`, `HEAD` =
571e186cb8178209da670dde244dfc56bba5e300 (detached), `core.autocrlf` = false, `git status --short` = 0 wierszy przed i po
(`t13_repo_stan.txt`) - niczego w repo nie zmieniono. Wykonane w przerwie testu T7 (czekanie na koniec proby B2), przed koncem T7 -
T13 jest tylko do odczytu i od T7 nie zalezy. Drugi przebieg (po dodaniu dowodow do repo) wykona kto inny.

## Kryterium (plan etapu, sekcja 7): diff wzgledem poczatku etapu - tylko pliki z list paczek; nowe pliki ASCII; brak STL i danych

Poczatek etapu 3: commit 2537f6f (ostatni wiersz `git log --follow ... -- Ramki/plan_etap3_pelna_aplikacja_2026-11-16.md`:
"2537f6f 2026-11-16 00:05:05 +0100 Plan etapu 3: pelna aplikacja stanowiska (do akceptacji wlasciciela, bramka G0)" -
`t13_poczatek_etapu.txt`); `git merge-base --is-ancestor 2537f6f 571e186...`: kod 0 (jest przodkiem).

## Polecenia (plik `krok_T13.cmd`; `PY` = `<PC>\AppData\Local\Programs\Python\Python312\python.exe`, `<ODB>` = `<REPO>\Ramki\etap3\odbior_koncowy`, `<ROB>` = `<PC-katalog>\koordynator\robocze\odbior\T13`)

| Polecenie | Kod | Czas | Wynik |
|---|---|---|---|
| `PY -I <ODB>\narzedzia\t13_higiena.py --repo <REPO> --od 2537f6f --do 571e186cb8178209da670dde244dfc56bba5e300 --json <ROB>\t13_wynik.json > <ROB>\t13_wynik.txt` | 0 | 1,1 s | `NARUSZENIA (grupa E3 i sciezki poza listami): 0`; ostatni wiersz: `WYNIK T13: ZAL z odstepstwem O11 (0 naruszen; 7 plikow napisow ekranu nie-ASCII)`; stderr pusty |
| `git -C <REPO> diff --stat 2537f6f 571e186cb8178209da670dde244dfc56bba5e300 > <ROB>\t13_diff_stat.txt` | 0 | - | `646 files changed, 192291 insertions(+), 1268 deletions(-)` |

## Liczby

- Zmienionych plikow 662, w tym nowych 584 (lista `git diff --name-status --no-renames`: A 584, M 62, D 16). `git diff --stat` podaje
  646 plikow, bo laczy w pary zmiany nazw (662 - 16 = 646); skrypt liczy bez wykrywania zmian nazw.

| Grupa | Nowe | Zmienione | Usuniete |
|---|---|---|---|
| E3 (paczki etapu 3) | 245 | 24 | 0 |
| R58 (praca wlasciciela spoza etapu 3) | 242 | 4 | 0 |
| R59 (praca wlasciciela spoza etapu 3) | 97 | 34 | 16 |

- Sciezek poza listami (`t13_dozwolone.txt`): **0**.
- **Naruszen: 0** (nie ASCII poza lista O11: 0; konce linii: 0; STL / dane: 0; duze pliki: 0).
- Odstepstwo O11 (napisy ekranu nie-ASCII): **7 plikow z 7 na liscie** `t13_wyjatki_ascii.txt`, razem 807 wierszy / 6452 bajty nie-ASCII:
  `stanowisko/dzien_skanera.py` 109 wierszy (859 B), `stanowisko/dzien_skanera_kroki.toml` 134 (1783 B),
  `stanowisko/dzien_skanera_rdzen.py` 102 (946 B), `stanowisko/statusy.py` 240 (1665 B), `stanowisko/ui/napisy.py` 66 (318 B),
  `stanowisko/ui/napisy_rano.py` 111 (710 B), `testy/test_dzien_skanera.py` 45 (171 B) - liczby wierszy takie same jak w probie
  na kopii integracyjnej a2236c1 (`RAPORT.md`, O11). Wyjatkow z listy bez trafienia: 0.
- Uwagi w grupach spoza etapu 3 (NIE licza sie do wyniku T13, do oceny koordynatora): 126 - R58: nie ASCII 23, konce linii 23,
  plik danych 2, duzy plik 1; R59: nie ASCII 43, konce linii 17, duzy plik 10, plik danych 5, STL poza `modele_plytek` 2.

## Kryterium - werdykt kazdej czesci

| Czesc kryterium | Werdykt | Liczba |
|---|---|---|
| diff tylko z plikow z list paczek | ZAL z odstepstwem O10 | 0 sciezek poza listami z 662; kontrola na poziomie KATALOGOW paczek (6 przedrostkow E3), nie list pojedynczych plikow; pliki nietykalne niewyroznione |
| nowe pliki ASCII | ZAL z odstepstwem O11 | 238 z 245 nowych plikow E3 bez bajtu nie-ASCII; 7 z 245 nie-ASCII = dokladnie 7 plikow z listy O11; innych 0 |
| brak STL i danych | ZAL | w grupie E3: STL poza `modele_plytek` 0, pliki danych 0, pliki > 1024 KB 0 (STL i dane grup R58 / R59: 9 uwag - poza wynikiem) |
| konce linii nowych plikow E3 (LF; `.cmd` / `.bat` / `.ps1` CRLF) | ZAL | naruszen 0 |

## Kontrola reczna 3 losowych pozycji wyniku (`t13_kontrola_reczna.txt`)

Losowanie `System.Random(13)`: po 1 pozycji z listy O11, z listy nowych plikow E3 i z listy uwag poza etapem. Bajty plikow liczone
niezaleznie od skryptu (PowerShell), zgodnosc pliku z obiektem commita: `git hash-object` = `git rev-parse 571e186:<sciezka>` (3 z 3).

| Pozycja | Wynik skryptu | Policzone recznie | Zgodne |
|---|---|---|---|
| `Ramki/stanowisko/stanowisko/statusy.py` | A, O11: 240 wierszy nie-ASCII (1665 bajtow) | status A (nie istnial w 2537f6f); 1665 bajtow nie-ASCII w 240 wierszach; CR 0, LF 600; 43903 B | tak |
| `Ramki/stanowisko/raporty/PR13_poprawki_dzien_skanera_2026-11-17.md` | nowy plik E3 bez naruszenia | status A; 0 bajtow nie-ASCII; CR 0, LF 210; 20268 B (<= 1024 KB); rozszerzenie `.md` | tak |
| `Ramki/wyniki_v2/raport/raport_wykonawcy_SPRAWDZ_iter13.md` | uwaga poza etapem (R58): "konce linii: 2666 x CRLF (ma byc LF)" | status A; CRLF 2666 (CR 2666, LF 2666); przedrostek `R58 Ramki/wyniki_v2/` | tak |

Zgodne 3 z 3.

## Kontrola niezalezna calej grupy E3 (`t13_kontrola_niezalezna.txt`, wlasne liczenie wykonawcy)

E3: 269 plikow (245 nowych, 24 zmienione, 0 usunietych) - jak w wyniku skryptu. Nowe pliki E3: z bajtem nie-ASCII 7 (te same 7
sciezek, co lista O11); tekstowe ze znakiem CR 0; `.cmd` / `.bat` / `.ps1` z koncami innymi niz CRLF 0; z rozszerzeniem danych 0;
`.stl` poza `modele_plytek` 0; wieksze niz 1024 KB 0; binarne znane / z bajtem 0 (poza kontrola tekstu): 4.

## Odstepstwa

- **O11** (decyzja koordynatora nr 16): 7 plikow napisow ekranu nie-ASCII - stan z commita wydania 571e186 wyzej (do wpisania w
  `RAPORT.md`, wiersz O11: liczby wierszy bez zmian wobec proby a2236c1; plik `ui/kandydaci.py` z tamtej proby nie jest juz zglaszany).
- **O10**: kontrola "tylko pliki z list paczek" na poziomie katalogow. Nowych odstepstw brak.

## Polecenia planu zmienione

Brak. `<commit wydania>` = pelny skrot 571e186cb8178209da670dde244dfc56bba5e300; `<DOW>` = `<ROB>` (w trakcie testow). Dodatkowo
(poza planem): `--json`-owi towarzyszy przekierowanie stderr do `t13_wynik_stderr.txt` (0 bajtow), `t13_repo_stan.txt`,
`t13_poczatek_etapu.txt`.

## Do decyzji koordynatora

1. Uwagi w grupach R58 / R59 (126, w tym 2 STL poza `modele_plytek`, 7 plikow danych, 11 duzych) - poza wynikiem T13 (O10).
2. Dowody T13 (`t13_wynik.txt`, `t13_diff_stat.txt` i inne pliki z przekierowania `cmd >`) maja konce CRLF - przed `git add`
   przepuscic przez `dowody_lf.py --napraw` (plan, "Dowody a T13"); tego kroku ten przebieg nie obejmowal.

## Dowody w tym katalogu

`t13_wynik.txt`, `t13_wynik.json`, `t13_diff_stat.txt` (lista z planu) oraz `t13_wynik_stderr.txt`, `t13_repo_stan.txt`,
`t13_poczatek_etapu.txt`, `t13_kontrola_reczna.txt`, `t13_kontrola_niezalezna.txt`, `krok_T13.cmd`, `kody.txt`, `czasy.txt`.
