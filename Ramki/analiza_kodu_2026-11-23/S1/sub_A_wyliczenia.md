# S1 / sub_A - wyliczenia T1-T4 (tylko odczyt kodu)

Data: 2026-11-23. Worktree: `<PC-katalog>\qc-wt\analiza-s1` (galaz analiza/s1), kod: `Ramki\stanowisko\stanowisko\`.
Metoda: kazdy plik przeczytany w calosci narzedziem Read; listy `except`, literalow statusu i `.get(` uzupelnione Grep.
Kodu nie uruchamiano. Numery linii z narzedzia. Tylko fakty z kodu, bez oceny wagi i bez propozycji poprawek.

Przeczytane w calosci (ostatnia linia pliku): uklad.py (360), plate.py (877), match.py (1345), inspect.py (797),
krawedz.py (990), porownaj.py (712), wspolczynniki.py (537), metryki.py (602), synth.py (1302), katalog.py (169);
dodatkowo ustawienia.py (379) i `Ramki\stanowisko\ustawienia.przyklad.toml` (125).
`Ramki\stanowisko\ustawienia.toml` - BRAK w worktree (Glob `Ramki/stanowisko/*.toml` zwraca tylko ustawienia.przyklad.toml).

Oznaczenia ukladu mm (kolumna "uklad" w T4):
- S = mm skanu (uklad plytki po sztywnym wyrownaniu w plate).
- P = mm ukladu puli projektu (projekt x wspolczynnik w, brzeg na z = 0). W inspect punkty skanu przechodza transformacja
  z match: inspect.py:168 `T = pr.T0 @ inv(transformacja)`, a po zastosowanej korekcie skali match.py:972
  `transformacja = inv(Ts) @ pr.T0`, czyli w inspect T = Ts (plytka -> pula, podobienstwo o skali s). Odchylki d w inspect
  (inspect.py:687, 690) NIE sa dzielone przez s (inaczej niz match.py:607 `d = pr.odleglosci(P) / s`). Zatem P = mm skanu x s;
  bez korekty skali s = 1 i P = S. Zakres s: okno korekta_skali_okno_proc + SKALA_DOKLADNOSC_PROC (match.py:962).
- R = mm skali odniesienia modulu krawedz (projekt x 1,22: krawedz.py:54, 951, 959); dla projektu o wspolczynniku w
  stala R odpowiada (w / 1,22) x stala w mm ukladu puli.
- U = udzial / bezwymiarowe, N = liczba punktow / komorek, cos = cosinus kata, deg = stopnie, % = procent.
- "bibl." w kolumnie "ostre" = granica w wywolaniu biblioteki (cKDTree `distance_upper_bound`, `query_pairs`,
  `query_ball_point`); scislosci (< czy <=) nie ustalano bez uruchamiania.

---------------------------------------------------------------------------------------------------------------------

## T1. Wszystkie `except` (40 w 10 plikach + 1 w ustawienia.py)

`*` = szeroki wyjatek I wynik wygladajacy dalej na "brak problemu". `(*)` = szeroki, pusta lista ubytkow, ale status nie zielony.

| # | plik:linia | funkcja | tresc (skrot linii) | cialo -> wartosc dalej | uwaga |
|---|---|---|---|---|---|
| T1-01 | krawedz.py:921 | wczytaj_npz | `except (OSError, KeyError, ValueError, EOFError, zipfile.BadZipFile):` | `return None` -> linie_siatki (957-959): wz None -> `wyznacz(...)` liczy linie od nowa | waski |
| T1-02 | krawedz.py:968 | linie_siatki | `except OSError as e:` | `warnings.warn(...)`; dalej `return wz.przeksztalc(...)` (970) | waski; linie zwrocone normalnie, bez zapisu na dysk |
| T1-03 | match.py:303 | Projekt.lekki | `except (QhullError, ValueError):` | `hull, H = 0.0, P` -> profil `(a, b, 0.0)` | waski; hull 0 -> filtr match.py:582 pomija kontrole objetosci |
| T1-04 * | match.py:340 | Projekt.cechy_do_glebokosci | `except Exception:  # noqa: BLE001` | `hull = 0.0` -> `self._profil[k] = (obrys, 0.0)`, zwrocone | SZEROKI. Zwraca 0 -> match.py:582 `if hull > 0 and ...` nie odrzuca kandydata za objetosc otoczki (filtr "przechodzi"). Dotyczy identyfikacji (match), nie listy ubytkow |
| T1-05 | match.py:430 | Pula.__init__ | `except ValueError:` | `self.pominiete += 1; continue` | waski; projekt poza pula (Projekt rzuca ValueError gdy synth.wczytaj_projekt -> None, match.py:207-208) |
| T1-06 | match.py:488 | Pula.z_wpisow | `except OSError:` | `lz["brak_pliku"] += 1; continue` | waski |
| T1-07 | match.py:502 | Pula.z_wpisow | `except ValueError:` | `lz["pominiete"] += len(g["wpisy"]); continue` | waski |
| T1-08 | match.py:860 | _dopasuj_podobienstwo | `except np.linalg.LinAlgError:` | `return {"ok": False, "powod": "uklad rownan osobliwy ...", "iteracje": it}` -> skala_ze_skanu ok False -> koryguj_skale: `kor.powod = "skali nie wyznaczono: ..."` (948-951), korekta niezastosowana | waski |
| T1-09 | match.py:1003 | _pelne_dopasowanie | `except (ValueError, OSError) as e:` | `uwagi.append(...)`; `return _kandydat_puli(pula, kl, metoda="blad")` -> kandydat: pokrycie 0.0, transformacja None | waski |
| T1-10 | match.py:1014 | _koryguj_bezpiecznie | `except (ValueError, OSError) as e:` | `k.skala = KorektaSkali(powod=..., pokrycie_przed=k.pokrycie)`; uwaga; `return` | waski; kandydat bez korekty skali, status liczony dalej |
| T1-11 | metryki.py:126 | sprawdz_okres | `except ValueError:` | `raise ValueError(...) from None` | re-raise |
| T1-12 | metryki.py:181 | migawka | `except BaseException:` | `pamiec.close(); raise` | szeroki, ale re-raise (bez *) |
| T1-13 | metryki.py:244 | _dane | `except ValueError:` | `return {}` | waski; dalej `.get("zastany")` / `.get("poprzedni_id")` -> None |
| T1-14 | plate.py:640 | _wyrownaj_do_ukladu | `except NiezgodnyUklad as e:` | `e.jakosc = {...}; raise` | re-raise |
| T1-15 | plate.py:795 | rozpoznaj_uklad | `except NiezgodnyUklad as e:` | `wpis["odrzucony"] = e.powod; wpis.update(...); continue` | uklad odrzucony; gdy zaden nie przejdzie: raise BladWyrownania / NierozpoznanyUklad (811-824) |
| T1-16 | plate.py:799 | rozpoznaj_uklad | `except BladWyrownania as e:` | `wpis["odrzucony"] = f"blad: {e}"; continue` | jw. |
| T1-17 | porownaj.py:125 | uklady_pasujace | `except (OSError, ValueError):` | `continue` | uklad pominiety w podpowiedzi (wczytanie pod `warnings.simplefilter("ignore")`, 122-124) |
| T1-18 | porownaj.py:152 | uklady_z_ustawien | `except (OSError, ValueError):` | `continue` | uklad pominiety jako kandydat `--plytka auto` (ostrzezenia wyciszone, 149-151) |
| T1-19 | porownaj.py:220 | dopasuj_fragmenty | `except MemoryError:` | `raise` | re-raise |
| T1-20 (*) | porownaj.py:222 | dopasuj_fragmenty | `except Exception as e:  # noqa: BLE001` | `wi = None`; `wpis["inspekcja"] = inspekcja_z_bledem(...)`: status "nie_sprawdzono", ubytki [], plamy [], wciecia [], brzeg {}, pole "blad"; `warnings.warn(...)` | SZEROKI. Pusta lista ubytkow, ale status "nie_sprawdzono" -> status_gniazda "zolty" (porownaj.py:64, 92), nie zielony. Licznik "ubytki" plytki (344) dostaje 0 z tego gniazda. Wyjatek z `M.dopasuj` (201, 206) i `M.ratuj_plytke` (202) NIE jest w tym try |
| T1-21 | porownaj.py:288 | porownaj | `except PL.NiezgodnyUklad as e:` | `return {..."uklad_zgodny": False, "gniazda": [], "statusy_gniazd": {s: 0 ...}, "ubytki": 0}` (306-318) | waski; lapie tez NierozpoznanyUklad (podklasa, plate.py:726); BladWyrownania i bledy `trimesh.load` (277) nie sa lapane |
| T1-22 | porownaj.py:595 | wczytaj_wpisy | `except UnicodeDecodeError:` | `tekst = dane.decode("cp1250")` | waski |
| T1-23 | porownaj.py:613 | wczytaj_wpisy | `except ValueError:` | `raise ValueError(...) from None` | re-raise |
| T1-24 | porownaj.py:654 | main | `except (OSError, ValueError) as e:` | `ap.error(...)` (SystemExit) | waski |
| T1-25 | synth.py:139 | wczytaj_projekt | `except Exception as e:  # noqa: BLE001` | `powod = ...`; po bloku `warnings.warn(...)`; `return None` (151-152) | SZEROKI; None -> match.Projekt ValueError (match.py:207-208) -> projekt pominiety w puli (match.py:430) i w katalogu (katalog.py:120-123). Bez * (nie daje wyniku "brak ubytku") |
| T1-26 | synth.py:874 | Opcje._waliduj.zakres | `except (TypeError, ValueError):` | `raise ValueError(...) from None` | re-raise |
| T1-27 | synth.py:894 | Opcje._waliduj | `except (TypeError, ValueError):` | `raise ValueError(...) from None` | re-raise |
| T1-28 | synth.py:1156 | _liczba.parsuj | `except ValueError:` | `raise argparse.ArgumentTypeError(...)` | re-raise |
| T1-29 | synth.py:1172 | _zakres.parsuj | `except ValueError:` | `raise argparse.ArgumentTypeError(...)` | re-raise |
| T1-30 | synth.py:1185 | _lista.parsuj | `except ValueError:` | `raise argparse.ArgumentTypeError(...)` | re-raise |
| T1-31 | synth.py:1268 | main | `except ValueError as e:` | `ap.error(str(e))` | waski |
| T1-32 | uklad.py:324 | wczytaj | `except json.JSONDecodeError as e:` | `raise BladUkladu(...) from e` | re-raise |
| T1-33 | wspolczynniki.py:125 | _dekoduj | `except UnicodeDecodeError:` | `continue` (nastepne kodowanie); po petli `raise BladWspolczynnikow` (127) | waski |
| T1-34 | wspolczynniki.py:137 | wspolczynnik_z_tekstu | `except ValueError:` | `raise ValueError(...) from None` | re-raise |
| T1-35 | wspolczynniki.py:159 | data_z_tekstu | `except ValueError:` | `pass` -> `raise ValueError(...)` (161) | blad i tak zglaszany |
| T1-36 | wspolczynniki.py:193 | _wczytaj_csv | `except FileNotFoundError:` | `raise BladWspolczynnikow(...) from None` | re-raise |
| T1-37 | wspolczynniki.py:195 | _wczytaj_csv | `except OSError as e:` | `raise BladWspolczynnikow(...) from None` | re-raise |
| T1-38 | wspolczynniki.py:239 | _wczytaj_csv | `except ValueError as e:` | `bledy.append((linia, str(e))); continue` -> na koncu `raise BladWspolczynnikow` (263-269) | blad zglaszany po calym pliku |
| T1-39 | wspolczynniki.py:503 | wpisz_reczny | `except ValueError as e:` | `raise BladWspolczynnikow(...) from None` | re-raise |
| T1-40 | wspolczynniki.py:511 | wpisz_reczny | `except ValueError:` | `raise BladWspolczynnikow(...) from None` | re-raise |
| T1-41 | ustawienia.py:358 | wczytaj_ustawienia | `except tomllib.TOMLDecodeError as e:` | `raise BladUstawien(...) from e` | spoza listy 10 plikow; re-raise |

Uwagi do T1:
- katalog.py: brak `except`. metryki.py:475 `try:` ma tylko `finally:` (490), bez `except`.
- Golego `except:` nie ma w zadnym z 10 plikow.
- Wyciszanie ostrzezen (nie wyjatki): porownaj.py:122-123, 149-150; match.py:211-212; synth.py:136-137;
  katalog.py:67-68, 95-96; krawedz.py:608-609; plate.py:792-793 (rozpoznaj_uklad zapisuje ostrzezenia kazdego ukladu,
  ponownie emituje tylko ostrzezenia wybranego, 852-853).

---------------------------------------------------------------------------------------------------------------------

## T2. Nadawanie / mapowanie statusu i koloru

| # | plik:linia | funkcja | tresc (skrot linii) | warunek prowadzacy do linii | uwaga |
|---|---|---|---|---|---|
| T2-01 | inspect.py:70 | (modul) | `STATUSY = ("ok", "ubytek", "sprawdz", "sprawdz_ulozenie", "poprawka", "skan_ponownie", "popraw_ulozenie", "nie_sprawdzono", "pominieto")` | definicja | "pominieto" nie jest nadawany w zadnym z 10 plikow (Grep) |
| T2-02 | inspect.py:345 | plamy_pod_powierzchnia | `rodzaj = "brak_danych"` | pierscien wokol plamy ma mniej niz min_punktow_plamy punktow (`n_pier < ...`, 344) | nie ubytek; liczony tylko w uwadze (746-748) |
| T2-03 | inspect.py:347 | jw | `rodzaj = "poprawka"` | srednica > poprawka_min_mm i krawedz nieostra | sprawdzane przed srednica_max |
| T2-04 | inspect.py:349 | jw | `rodzaj = "sprawdz_ulozenie"` | srednica > srednica_max_mm (i nie spelnia warunku poprawki) | |
| T2-05 | inspect.py:351 | jw | `rodzaj = "lagodna"` | krawedz nieostra (`ostra` False, 330), srednica <= srednica_max_mm | status sie nie zmienia, brak uwagi |
| T2-06 | inspect.py:353 | jw | `rodzaj = "za_mala"` | ostra i srednica < srednica_min_mm / 2 | status sie nie zmienia, brak uwagi |
| T2-07 | inspect.py:355 | jw | `rodzaj = "poza_pasem"` | ostra, srednica w zakresie, odl_brzegu > pas_brzegu_mm i nie na ostrej krawedzi projektu | status sie nie zmienia, brak uwagi |
| T2-08 | inspect.py:357 | jw | `rodzaj = "ubytek"` | else (zaden z warunkow 344-354) | jedyny rodzaj plamy brany do `polacz` (653) |
| T2-09 | inspect.py:500 | _linia_brzegu | `rodzaj = "za_male"` | szer < srednica_min_mm albo len(idx) < min_punktow_plamy | |
| T2-10 | inspect.py:502 | jw | `rodzaj = "brak_danych"` | udzial otoczenia z ciaglym skanem `udz < 0.5` (takze `udz = 0.0` gdy brak sasiadow, 498) | |
| T2-11 | inspect.py:504 | jw | `rodzaj = "wciecie"` | else | jedyny rodzaj wciecia brany do `polacz` (654) |
| T2-12 | inspect.py:517 | jw | `w.rodzaj = "brak_danych"` (z "wciecie") | `udzial_ciagly < linia_min_udzial` (514) | metoda B wylaczona dla calej pracy; tylko uwaga (518) |
| T2-13 | inspect.py:582 | ocena_brzegu | `{"sprawdzony": True, "stan_linii": "brak", ...}` | projekt bez filarow z linia i `tylko_dane` (tryb linia_i_plaszczyzna) | |
| T2-14 | inspect.py:584 | jw | `{"sprawdzony": False, "stan_linii": "brak", ...}` | projekt bez linii, tryb "linia" | |
| T2-15 | inspect.py:635 | jw | `"sprawdzony": not zle` | zle = filary niespelniajace `_kryterium_brzegu`; filary_bez_linii dopisywane do zle tylko w trybie "linia" (627-630) | |
| T2-16 | inspect.py:653-654 | polacz | `A = [... rodzaj == "ubytek"]`, `B = [... rodzaj == "wciecie"]` | zawsze | inne rodzaje nie staja sie Ubytek |
| T2-17 | inspect.py:669 | polacz | `Ubytek(..., "A+B", "czerwony", ...)` | plama A ma wciecie B w odleglosci <= max(srednica, szerokosc)/2 + 0.3 (662) | |
| T2-18 | inspect.py:671 | polacz | `Ubytek(..., "A", "zolty", ...)` | plama A bez pary B | |
| T2-19 | inspect.py:676 | polacz | `kolor = "czerwony" if w.wciecie_mm >= ust_i["wciecie_pewne_mm"] else "zolty"` | wciecie B bez pary A | |
| T2-20 | inspect.py:691 | sprawdz | `WynikInspekcji(gniazdo, pr.id, "ok", ...)` | zawsze na poczatku | wartosc domyslna "ok" (T2-D1) |
| T2-21 | inspect.py:697 | sprawdz | `w.status = "skan_ponownie"` | `wykryj_drgniecie(...)["wykryte"]` True | return (700), ubytki nieliczone |
| T2-22 | inspect.py:713 | sprawdz | `w.status = "popraw_ulozenie"` | pokrycie < prog_akceptacji_pokrycie i (brak plam "poprawka" albo pokrycie + w_poprawkach/len(P) < prog) | return (716), ubytki nieliczone |
| T2-23 | inspect.py:733 | sprawdz | `w.status = "ubytek"` | jakikolwiek Ubytek o kolorze "czerwony" | |
| T2-24 | inspect.py:735 | sprawdz | `w.status = "sprawdz"` | ubytki niepuste, wszystkie "zolty" | |
| T2-25 | inspect.py:737 | sprawdz | `w.status = "poprawka"` | brak ubytkow, jest plama rodzaj "poprawka" | |
| T2-26 | inspect.py:739 | sprawdz | `w.status = "sprawdz_ulozenie"` | brak ubytkow i poprawek, jest plama "sprawdz_ulozenie" | |
| T2-27 | inspect.py:741 | sprawdz | `w.status = "nie_sprawdzono"` | brak powyzszych, `brzeg is not None and not w.brzeg["sprawdzony"]` | przy pas_brzegu_od = "plaszczyzna" brzeg = None (701-706) -> galaz niedostepna |
| T2-28 | inspect.py:732-741 | sprawdz | lancuch if/elif bez `else` | zaden warunek nie spelniony | status zostaje "ok" z 691 (T2-D1) |
| T2-29 | porownaj.py:60-61 | (modul) | `KOLORY = {"zielony", "zolty", "szary", "czerwony", "pomaranczowy", "pusty", "podwojny", "poza"}` | mapa RGB do PNG | |
| T2-30 | porownaj.py:62 | (modul) | `STATUSY_GNIAZDA = ("zielony", "czerwony", "zolty", "szary", "pomaranczowy")` | liczniki 317, 343 | |
| T2-31 | porownaj.py:63-64 | (modul) | `INSPECT_NA_STATUS = {"ok": "zielony", "ubytek": "czerwony", "sprawdz"/"sprawdz_ulozenie"/"popraw_ulozenie"/"skan_ponownie"/"nie_sprawdzono": "zolty", "poprawka": "pomaranczowy", "pominieto": None}` | slownik mapujacy inspect -> kolor | "pominieto" -> None -> fallback (T2-34) |
| T2-32 | porownaj.py:65, 67-68 | (modul) | `OPISY_STATUSU`, `OPISY_INSPEKCJI` | podpisy | tylko tekst |
| T2-33 | porownaj.py:90-91 | status_gniazda | `if status_match == "szary" or not inspekcja: return status_match` | match "szary" albo inspekcja None / {} | inspekcja None gdy: `inspekcja=False` (parametr 173, 234; `--bez-inspekcji` 634, 667), k None albo k.transformacja None (216) -> kolor = status match, takze "zielony" |
| T2-34 | porownaj.py:92 | status_gniazda | `return INSPECT_NA_STATUS.get(inspekcja["status"]) or status_match` | match nie "szary" i inspekcja jest | status spoza slownika albo "pominieto" -> status match; match "zolty" + inspect "ok" -> "zielony" |
| T2-35 | porownaj.py:95, 111 | inspekcja_z_bledem | `STATUS_BLEDU_INSPEKCJI = "nie_sprawdzono"` | wyjatek w `I.sprawdz` (222) | -> "zolty" |
| T2-36 | porownaj.py:197 | dopasuj_fragmenty | `fragmenty = [f for f in wyr.fragmenty if f.status != "drobny"]` | zawsze | fragment "drobny" nie dostaje wpisu; gniazdo z samym okruchem jest w gniazda_puste (plate.py:700-702) |
| T2-37 | porownaj.py:216 | dopasuj_fragmenty | `if inspekcja and r.status != "szary" and k is not None and k.transformacja is not None:` | warunek wywolania inspekcji | inaczej `"inspekcja": None` (213) |
| T2-38 | porownaj.py:228 | dopasuj_fragmenty | `wpis["status_gniazda"] = status_gniazda(r.status, wpis["inspekcja"])` | kazdy fragment niedrobny, takze "poza_gniazdem" (gniazdo None) | |
| T2-39 | porownaj.py:317 | porownaj | `"statusy_gniazd": {s: 0 for s in STATUSY_GNIAZDA}` | NiezgodnyUklad / NierozpoznanyUklad | `"gniazda": []` |
| T2-40 | porownaj.py:333 | porownaj | `"uklad_zgodny": wyr.jakosc.get("uklad_zgodny")` | straznik=False (`--bez-straznika`) -> None | gniazda oceniane normalnie |
| T2-41 | porownaj.py:343 | porownaj | `"statusy_gniazd": {s: sum(... g["status_gniazda"] == s ...)}` | wszystkie wpisy, w tym gniazdo None (poza_gniazdem) | |
| T2-42 | porownaj.py:552 | mapa_png | `KOLORY[stan[g.id].get("status_gniazda", stan[g.id]["status"])]` | gniazdo z wpisem | default = status match (tylko PNG) |
| T2-43 | porownaj.py:558 | mapa_png | podpis statusu `if ins and ins["status"] != "ok"` | | tylko PNG |
| T2-44 | match.py:60 | (modul) | `STATUSY = ("zielony", "zolty", "szary")` | | |
| T2-45 | match.py:1147 | dopasuj | `WynikDopasowania(gniazdo, [], 0.0, "szary", ...)` | len(P) < 50 albo pusta pula | |
| T2-46 | match.py:1215 | _zakoncz | `status = "zielony"` | p1 >= prog_akceptacji_pokrycie i pewnosc >= pewnosc_min | |
| T2-47 | match.py:1217 | _zakoncz | `status = "zolty"` | p1 >= prog_ostrzezenia_pokrycie i pewnosc >= pewnosc_min (nie zielony) | |
| T2-48 | match.py:1219 | _zakoncz | `status = "szary"` | else (takze pewnosc < pewnosc_min przy dowolnym p1) | |
| T2-49 | match.py:1221 | _zakoncz | zielony -> `status = "zolty"` | `ograniczenie` niepuste (`_ograniczenie` 1181-1185, ratunek 1296) | p1 >= prog_akceptacji pozostaje |
| T2-50 | match.py:1225 | _zakoncz | zielony -> `status = "zolty"` | ratunek: zwyciezca w `bez_zielonego` (fragment wyzszy niz projekt, D6) | p1 >= prog_akceptacji pozostaje |
| T2-51 | match.py:1242, 1315 | ratuj / ratuj_plytke | `wynik.status == "zielony"` -> bez ratunku | | |
| T2-52 | plate.py:108 | Fragment | `status: str = "praca"` (default pola) | | |
| T2-53 | plate.py:543 | potnij_na_fragmenty | `f.status = "drobny"` | max(rozmiar x, y) < 3.0 albo rozmiar z < 1.5 mm (535) | |
| T2-54 | plate.py:545 | jw | `f.status = "poza_gniazdem"; f.gniazdo = None` | g None albo udzial < 0.6 | |
| T2-55 | plate.py:555 | jw | `f.status = "podwojny"` | > 1 fragment "praca" w gniezdzie | |
| T2-56 | plate.py:850 | rozpoznaj_uklad | `wybrany, powod, pewny = ..., "domyslny", False` | numer, dolki i ksztalt nie rozstrzygaja | tylko ostrzezenie (856-859); porownaj liczy gniazda dalej |
| T2-57 | krawedz.py:835 | wyznacz | `werdykt = "wiarygodna" / "czesciowa" / "niepewna"` | udzial zweryfikowanych przekrojow, najdluzszy ciag | w inspect tylko do raportu (inspect.py:610); decyzje uzywaja `zweryf` stacji (inspect.py:597) |
| T2-58 | krawedz.py:157-159 | LinieProjektu.stan | `"brak"` / `"wiarygodne"` / `"czesciowe"` | | tylko raport (inspect.py:635 "stan_linii") |
| T2-59 | metryki.py:58 | (modul) | `KOLOR_ALARMU = "czerwony"` | | |
| T2-60 | metryki.py:299-302 | _wieczor | `if p["status_gniazda"] == KOLOR_ALARMU: ... if decyzja == "ok": falszywe += 1` | praca czerwona z decyzja technika "ok" | |
| T2-61 | metryki.py:307-308 | _wieczor | `elif decyzja in SE.DECYZJE_UKRUSZENIA: niewykryte += 1` | praca nieczerwona (takze zielona) z decyzja ukruszenia | |

Pliki bez nadawania statusu: uklad.py, katalog.py, wspolczynniki.py, synth.py (synth ma tylko `ulozenie` "dobrze"/"bokiem").

### T2-D. Kazde miejsce, gdzie WARTOSCIA DOMYSLNA (default pola, default `.get`, galaz else) jest "ok" / "zielony" (lub ich odpowiednik)

| # | plik:linia | tresc | kiedy dziala |
|---|---|---|---|
| T2-D1 | inspect.py:691 (+ 732-741 bez `else`) | `WynikInspekcji(gniazdo, pr.id, "ok", ...)` | brak drgniecia, pokrycie >= prog, zero Ubytek, zero plam "poprawka" / "sprawdz_ulozenie", oraz (brzeg None albo `w.brzeg["sprawdzony"]` True) |
| T2-D2 | porownaj.py:90-91 | `if status_match == "szary" or not inspekcja: return status_match` | inspekcja None / {} -> kolor = status match bez zmian ("zielony" z match przechodzi jako "zielony") |
| T2-D3 | porownaj.py:92 | `INSPECT_NA_STATUS.get(...) or status_match` | status inspekcji "pominieto" (mapowany na None) albo spoza slownika -> status match ("zielony" mozliwy) |
| T2-D4 | porownaj.py:552 | `.get("status_gniazda", stan[g.id]["status"])` | brak klucza status_gniazda -> status match (tylko PNG; w porownaj klucz zawsze ustawiany, 228) |
| T2-D5 | porownaj.py:524 | `brzeg.get("sprawdzony", True)` | brak klucza -> traktowany jako sprawdzony (tylko tekst tabeli) |
| T2-D6 | inspect.py:582 | `{"sprawdzony": True, ...}` | projekt bez linii w trybie linia_i_plaszczyzna -> nie blokuje "ok" (T2-27) |
| T2-D7 | inspect.py:622-626 + 635 | filary_bez_linii tylko do `uwagi_linii` (tryb sumy), `"sprawdzony": not zle` | filar z niecka bez linii nie trafia do zle -> sprawdzony True |
| T2-D8 | inspect.py:150 | `brzeg: dict = field(default_factory=dict)` | {} gdy brzeg None (tryb plaszczyzna) i przy wczesnym return (697-700, 713-716); porownaj.py:523-524 `if brzeg and ...` -> brak komunikatu |

Pokrewne domyslne "brak problemu" (nie literal ok/zielony): match.py:143 `filtr_ok: bool = True`; plate.py:110 `udzial_w_gniezdzie: float = 1.0`.

### T2-I. Inne sciezki w kodzie konczace sie kolorem "zielony" (fakty z kodu)

1. match "zolty" z p1 >= prog_akceptacji_pokrycie (tylko przez match.py:1221 albo 1225) + inspect "ok" -> porownaj.py:92 -> "zielony".
   (match "zolty" z p1 w [prog_ostrzezenia, prog_akceptacji) -> inspect.py:707-716 daje "popraw_ulozenie" albo, przy plamie poprawka, "poprawka" / ubytek.)
2. Inspekcja wylaczona albo niewywolana (porownaj.py:213, 216) -> kolor = status match.
3. `pas_brzegu_od = "plaszczyzna"`: brzeg = None (inspect.py:701-706) -> "nie_sprawdzono" niedostepne; braki danych tylko w uwagach.
4. Fragment "poza_gniazdem" (gniazdo None) dostaje status_gniazda (porownaj.py:228) i jest liczony w statusy_gniazd (343).
5. Uklad rozpoznany "domyslny" z `pewny = False` (plate.py:850) i `uklad_zgodny = None` przy straznik=False (porownaj.py:333) nie blokuja oceny gniazd.

---------------------------------------------------------------------------------------------------------------------

## T3. Puste dane i NaN

| # | plik:linia | funkcja | tresc (skrot linii) | sprawdza? | wynik przy pustych danych / NaN (dokladnie) |
|---|---|---|---|---|---|
| T3-01 | inspect.py:240-241 | wykryj_drgniecie | `if len(P) == 0: return {...}` | tak | `{"wykryte": False, "udzial_obszaru": 0.0, "komorek": 0}` |
| T3-02 | inspect.py:248-250 | jw | `if not ok.any(): return {...}` (zadna komorka >= 20 pkt) | tak | ten sam slownik, wykryte False |
| T3-03 | inspect.py:257 | jw | `... if (n_nad + n_pod) > 0 else False` | tak | obie_strony False |
| T3-04 | inspect.py:270 | jw | `n_nad / max(1.0, n_nad + n_pod)` | tak | udzial_nad 0.0 |
| T3-05 | inspect.py:278-282 | _skupiska | `len(Q) == 0` -> `np.zeros(0)`; brak par -> `np.arange(len(Q))` | tak | pusta tablica / kazdy punkt osobnym skupiskiem |
| T3-06 | inspect.py:290-291 | _rozmiar | `if len(Q) < 2: return 0.0` | tak | 0.0 |
| T3-07 | inspect.py:307-309 | plamy_pod_powierzchnia | `rdzen = flatnonzero(d <= -prog)`; `if len(rdzen) == 0: return []` | tak | `[]`; punkt z d = NaN nie wchodzi do rdzenia (NaN <= -prog -> False) |
| T3-08 | inspect.py:317-318 | jw | `if len(idx) < ust_i["min_punktow_plamy"]: continue` | tak | skupisko pominiete bez wpisu (ani plama, ani brak_danych) |
| T3-09 | inspect.py:329 | jw | `med_pier = ... median(...) if n_pier else math.inf` | tak | inf -> ostra False; w JSON -1.0 (359) |
| T3-10 | inspect.py:344-345 | jw | `if n_pier < min_punktow_plamy: rodzaj = "brak_danych"` | tak | plama nie jest ubytkiem; tylko licznik w uwadze (746-748) |
| T3-11 | inspect.py:335-337 | jw | `brzeg.drzewo is None` -> `odl_plaszcz if z_plaszczyzna else math.inf` | tak | tryb "linia": inf -> "poza_pasem" (354), chyba ze na ostrej krawedzi |
| T3-12 | inspect.py:373-374 | probka_brzegu | `if len(sel) == 0:` | tak | `(pas, zeros((0,3)), zeros((0,3)))` |
| T3-13 | inspect.py:390-392, 396 | probka_od_linii | drzewo None / `len(sel)` 0 -> `puste` | tak | 5 pustych tablic |
| T3-14 | inspect.py:418, 421 | probka_suma | `if brzeg.drzewo is not None and len(L2)`; `vstack ... if len(L2) else L1` | tak | gdy L2 puste: L = L1 |
| T3-15 | inspect.py:462-463 | _linia_brzegu | `if len(L) == 0 or len(P_pula) == 0: return [], {...}, None` | tak | `([], {"punktow_linii": 0, "brak_danych": 0, "udzial_brak_danych": 0.0, "wciec": 0, "uwaga": "projekt bez pasa brzegu"}, None)` |
| T3-16 | inspect.py:466-472, 480 | jw | `kk = min(SASIADOW_LINII, len(P_pula))`; `zgodne &= np.isfinite(odl_k)`; `brak = ~ma` | tak | punkt linii bez wierzcholka skanu o zgodnej normalnej w BRAK_DANYCH_MM = brak (nie wciecie) |
| T3-17 | inspect.py:489 | jw | `if len(idx_w):` | tak | brak punktow wciecia -> wciecia [] |
| T3-18 | inspect.py:498 | jw | `udz = float(np.mean(~daleko[sas])) if len(sas) else 0.0` | tak | 0.0 -> "brak_danych" (501-502) |
| T3-19 | inspect.py:512, 519 | jw | `(~daleko).mean()`, `brak.mean()` | nie wprost (L niepuste po 462) | - |
| T3-20 | inspect.py:514-518 | jw | `udzial_ciagly < linia_min_udzial` -> wciecia "brak_danych" | tak | metoda B pominieta; tylko `info["uwaga"]` |
| T3-21 | inspect.py:528-529 | _kryterium_brzegu | `udzial = ok.mean() if len(ok) else 0.0`; `przerwa = ... if len(ok) else 0.0` | tak | (False, 0.0, 0.0) przy brzeg_min_sprawdzony 0.9; przy brzeg_min_sprawdzony = 0 (dozwolone, ustawienia.py:290) -> True |
| T3-22 | inspect.py:537-538 | _odcinki_bez_sprawdzenia | `if n == 0 or spr.all(): return []` | tak | `[]` |
| T3-23 | inspect.py:579-584 | ocena_brzegu | `if not linie.filary:` | tak | tryb sumy: `{"sprawdzony": True, "stan_linii": "brak", "filarow": 0, "nie_sprawdzono": [], "filary": [], "opis": "", "uwagi_linii": ...}`; tryb linia: `"sprawdzony": False` |
| T3-24 | inspect.py:586-591 | jw | `dane = zeros(n)`; `if st_O is not None and ma_dane is not None and len(st_O):` | tak | brak ma_dane / stacji -> zadna stacja z danymi -> filary niesprawdzone ("nie_sprawdzono") |
| T3-25 | inspect.py:622-626 | jw | tryb sumy: filar z `filary_bez_linii` -> tylko `uwagi_linii.append` | tak | filar bez linii nie blokuje "sprawdzony" |
| T3-26 | inspect.py:692-693 | sprawdz | `np.mean(d <= -prog)`, `np.mean(d >= prog)` | NIE (brak len) | pusty d -> NaN w `odchylki["udzial_pod"/"udzial_nad"]` (tylko informacja) |
| T3-27 | inspect.py:693-694 | jw | `rms_mm`, `mediana_mm` `... if len(d) else 0.0` | tak | 0.0 |
| T3-28 | inspect.py:690 (uzycie 246-247, 307) | sprawdz | `d = odchylki(P_pula, pr)` | NIE (brak isnan / isfinite na d w calym inspect.py) | d = NaN: nie wchodzi do rdzenia plamy ani do rozmytych komorek drgniecia |
| T3-29 | inspect.py:707 | sprawdz | `if pokrycie < um["prog_akceptacji_pokrycie"]:` | NIE (brak isfinite) | pokrycie NaN -> warunek False -> inspekcja jak przy pokryciu >= prog (w lancuchu porownaj match z NaN p1 daje "szary", T3-48, i inspect nie jest wolany) |
| T3-30 | inspect.py:712 | jw | `w_poprawkach and len(P) and pokrycie + w_poprawkach / len(P) >= ...` | tak | brak dzielenia przez 0 |
| T3-31 | inspect.py:732-741 | jw | brak Ubytek, poprawek, sprawdz_ulozenie i (brzeg None albo sprawdzony) | - | status "ok" |
| T3-32 | inspect.py:751 | jw | `w.linia_brzegu.get("udzial_brak_danych", 0) > 0.2` | tak (default 0) | tylko uwaga |
| T3-33 | inspect.py:796 | polozenie_ubytku_prawdy | `min(..., default=math.inf)` | tak | inf (metryki) |
| T3-34 | porownaj.py:90-91 | status_gniazda | `not inspekcja` -> `return status_match` | tak | kolor = status match (mozliwy "zielony") |
| T3-35 | porownaj.py:197 | dopasuj_fragmenty | fragmenty bez "drobny" | tak | brak fragmentow -> `gniazda = []` -> statusy_gniazd same 0, "ubytki" 0 |
| T3-36 | porownaj.py:213, 216 | jw | `"inspekcja": None`; warunek wywolania | tak | inspekcja None -> T3-34 |
| T3-37 | porownaj.py:268-271 | pula_gotowa | `if len(p) == 0: raise SystemExit(...)` | tak | przerwanie |
| T3-38 | porownaj.py:341, 344 | porownaj | sumy `... for g in gniazda if g["inspekcja"]` | tak | 0.0 / 0 |
| T3-39 | porownaj.py:380-381 | metryki | `max(..., default=None)` | tak | None |
| T3-40 | porownaj.py:438-443 | metryki_inspekcji | `not g["kandydaci"]` -> top1_bledny; `ins is None` -> bez_inspekcji | tak | praca poza licznikami wykryc / falszywych |
| T3-41 | porownaj.py:477-482 | jw | `if not p.ubytki:` praca cala | tak | - |
| T3-42 | porownaj.py:504, 509-510, 515 | tabela | `k = ... if g["kandydaci"] else None`; `if not sk or sk["poprawka_proc"] is None` | tak | tekst: myslnik (znak spoza ASCII w kodzie) / 0 |
| T3-43 | porownaj.py:598-599, 615 | wczytaj_wpisy | `if not linie: raise ValueError`; `not math.isfinite(w)` -> ValueError | tak | wyjatek |
| T3-44 | match.py:1146-1147 | dopasuj | `if len(P) < 50 or len(pula) == 0:` | tak | `WynikDopasowania(gniazdo, [], 0.0, "szary", 0.0, len(P), ["za malo punktow" albo "pusta pula"])` |
| T3-45 | match.py:609 | ocena | `pok = float(w.mean())` | NIE (brak len) | pusty fr.P -> NaN (w lancuchu fr.P niepuste po T3-44) |
| T3-46 | match.py:610 | jw | `rms = ... if w.any() else math.inf` | tak | inf (w JSON None, porownaj.py:210) |
| T3-47 | match.py:1210, 1212 | _zakoncz | `p2 = max(..., default=0.0)` / `... if len(kandydaci) > 1 else 0.0` | tak | brak innego kandydata (innego STL) -> p2 = 0.0 -> pewnosc = p1 |
| T3-48 | match.py:1208, 1214-1219 | jw | p1 NaN | NIE | NaN >= prog -> False -> "szary" |
| T3-49 | match.py:582 | filtr | `if hull > 0 and abs(fr.hull - hull) > ...` | tak | hull 0 (T1-03, T1-04, 296, 335, 554) -> kontrola objetosci pominieta |
| T3-50 | match.py:295-296, 334-335 | lekki / cechy_do_glebokosci | < 4 punktow -> `(0.0, 0.0, 0.0)` / `([0.0, 0.0], 0.0)` | tak | obrys 0, hull 0 |
| T3-51 | match.py:554 | FragmentDoDopasowania.z_punktow | `hull = ... if len(Pd) >= 4 else 0.0` | tak | 0.0 |
| T3-52 | match.py:759-760 | ocena_wstepna | `if len(X) < 12 or len(lk.punkty) < 12: return 0.0` | tak | 0.0 |
| T3-53 | match.py:787-794 | ocena_fpfh | `len(A) == 0` -> inf; `B is None or len(B) == 0` -> continue | tak | inf (pomijane w ratunku, 1255) |
| T3-54 | match.py:806-807 | _usrednij_w_siatce | `if len(P) == 0: return np.zeros((0, 3))` | tak | |
| T3-55 | match.py:848-849, 900-902 | _dopasuj_podobienstwo / skala_ze_skanu | `< SKALA_MIN_PUNKTOW` | tak | `ok: False` -> korekta niezastosowana |
| T3-56 | match.py:911 | skala_ze_skanu | `np.maximum(jest.sum(axis=1), 1)` | tak | |
| T3-57 | match.py:1091-1092 | _wybierz_wariant | `if k1.transformacja is None: return` | tak | |
| T3-58 | match.py:1247-1249, 1291-1292 | ratuj | brak pozostalych / `zrobione == 0` -> `return wynik, 0, ...` | tak | wynik bez zmian |
| T3-59 | match.py:1260, 1316 | ratuj / ratuj_plytke | `max(..., default=0.0)`; `najlepszy ... else 0.0` | tak | 0.0 |
| T3-60 | plate.py:157-158 | plaszczyzna_wierzchu | `if len(P) < 1000: raise BladWyrownania` | tak | wyjatek (porownaj go nie lapie, T1-21) |
| T3-61 | plate.py:172-173 | jw | `if bl.sum() < 500: raise BladWyrownania` | tak | wyjatek |
| T3-62 | plate.py:220-221 | kandydaci_znacznikow | `if n == 0: return []` | tak | `[]` |
| T3-63 | plate.py:243-244, 258-259 | dopasuj_stozek | < 100 punktow -> `return None` | tak | None |
| T3-64 | plate.py:305-306 | przypisz_znaczniki | `len(srodki) < 3` -> BladWyrownania | tak | wyjatek |
| T3-65 | plate.py:436-440 | zgodnosc_ukladu | `Z = full(-inf)`; `dane = np.isfinite(Z)` | tak | piksel bez punktow nie liczy sie jako niezgodnosc |
| T3-66 | plate.py:459-461 | odczytaj_bity | `bl.sum() < MIN_PUNKTOW_DOLKA` -> `None` | tak | numer nieznany (659-674) - tylko ostrzezenie |
| T3-67 | plate.py:518-519 | potnij_na_fragmenty | `if len(W) == 0 or len(Ws) == 0: return [], {...}` | tak | `([], {"punkty_prac": 0, "punkty_plytki": ..., "fragmenty_drobne": 0, "skupiska_pominiete": 0})` -> wszystkie gniazda puste |
| T3-68 | plate.py:531-532 | jw | `if sel.sum() < MIN_PUNKTOW_FRAGMENTU: continue` | tak | skupisko < 300 pkt: ani fragment, ani "drobny"; gniazdo puste |
| T3-69 | plate.py:538-540 | jw | `udzial = 0.0` gdy g None | tak | -> "poza_gniazdem" |
| T3-70 | plate.py:599 (uzycie 494-495) | _przygotuj / punkty_plytki | `N0 = np.where(np.isfinite(N0), N0, 0.0)`; `brak_normalnej = norm(N) < 0.5` | tak | normalna NaN -> 0 -> punkt blizej modelu niz PROG_PLYTKI uznany za plytke |
| T3-71 | plate.py:620 | _przygotuj | `max(len(Ps), 1)` | tak | |
| T3-72 | plate.py:747-748 | ksztalt_plytki | `if not m.any(): return {...}` | tak | `{"ksztalt_strefa_mm2": 0.0, "ksztalt_niewyjasnione_mm2": 0.0}` |
| T3-73 | krawedz.py:777-778 | wyznacz | `if not np.isfinite(Z).any():` | tak | `LinieProjektu([], [], ["pusta mapa wysokosci"], ...)` -> filary [] (inspect: T3-23) |
| T3-74 | krawedz.py:781 | jw | `if k == 0:` | tak | `LinieProjektu([], niecki, ["brak niecki filaru ..."], ...)` |
| T3-75 | krawedz.py:799, 813-815 | jw | < 8 waznych przekrojow -> None; `if L is None: ... continue` | tak | filar bez linii -> `filary_bez_linii` (inspect: T3-25) |
| T3-76 | krawedz.py:855-856 | jw | `if not filary: uwagi.append(...)` | tak | filary [] |
| T3-77 | krawedz.py:420-421 | fourier_odporny | `ok.sum() < 2 * rzad + 4` -> `np.full_like(th, np.nan)` | tak | NaN -> wariant odrzucony (688-690) |
| T3-78 | krawedz.py:435-438 | najdluzsza_przerwa | `ok.all()` -> 0; `not ok.any()` -> len(ok) | tak | pusta tablica -> 0 (ok.all() True); inspect strzeze len (529) |
| T3-79 | krawedz.py:645-646 | zbuduj_linie | `if not np.isfinite(X).all(): return None` | tak | None |
| T3-80 | krawedz.py:610, 851 | _med_kolowa / wyznacz | `nanmedian` z wyciszonym RuntimeWarning; `... if np.isfinite(szer).any() else None` | tak | |
| T3-81 | krawedz.py:987-989 | stacje | `if not X:` -> puste tablice | tak | inspect.brzeg_projektu: drzewo None (218-219) |
| T3-82 | synth.py:168-169 | strona_brzegu | `if len(e) == 0: return 0.0, 0.0` | tak | `brzeg_z_heurystyki` -> "niejasny" (181-182) -> orientacja: brzeg na dole + ostrzezenie (212-218); uzywane w match.Projekt (match.py:213) dla plikow nie-exocad |
| T3-83 | synth.py:242-243, 453-454 | wytnij_ubytek(_v1) | `if len(kand) == 0: kand = np.arange(...)` | tak | wszystkie wierzcholki |
| T3-84 | synth.py:368-369 | _wytnij_kule | `if not w.any(): return None` | tak | None |
| T3-85 | synth.py:498-500, 518-519 | wytnij_ukruszenie | brak filarow / kandydatow -> `return m, None` | tak | ukruszenie pominiete (licznik ukruszenia_pominiete) |
| T3-86 | synth.py:620, 1023 | usun_plamy / generuj_plytke | `... if A0 > 0 else 0.0` | tak | 0.0 |
| T3-87 | metryki.py:96-97 | _udzial | `return a / b if b else None` | tak | None -> ocena "brak danych" (90-91) |
| T3-88 | metryki.py:150 | bez_kandydata | `(kandydaci[0][1] or 0.0) < prog_kandydata` | tak | pokrycie None -> 0.0 -> praca nieznana |
| T3-89 | metryki.py:260, 370-371, 447 | _czas / _rano / _wiersze | `... if z_czasem else None` itd. | tak | None |
| T3-90 | wspolczynniki.py:245-248 | _wczytaj_csv | `if wsp is None and krazek is None:` -> blad linii | tak | blad |
| T3-91 | wspolczynniki.py:261-262 | jw | `if not naglowek_ok: raise` | tak | wyjatek |
| T3-92 | wspolczynniki.py:442, 454-456 | _stan | `max(..., default=None)`; brak wartosci -> wspolczynnik None | tak | None |
| T3-93 | uklad.py:172-173 | najblizsze_gniazdo | `if not zaw: return None` | tak | plate: "poza_gniazdem" |
| T3-94 | uklad.py:257-258 | _waliduj | `if not isinstance(d["sockets"], list) or not d["sockets"]:` | tak | BladUkladu |
| T3-95 | katalog.py:56-57 | typ_i_zeby_z_nazwy | `if m is None: return TYP_NIEZNANY, []` | tak | `("nieznany", [])` |

### T3-B. Miejsca, gdzie puste dane / NaN daja wynik "brak ubytku" (bez czerwonego / zoltego z ubytku)

- inspect.py:307-309 - brak punktow >= prog pod powierzchnia (takze d = NaN) -> plamy [].
- inspect.py:317-318 - skupisko mniejsze niz min_punktow_plamy -> pominiete bez wpisu.
- inspect.py:344-345 - plama bez pierscienia danych -> "brak_danych", nie ubytek.
- inspect.py:462-463 - brak probki pasa albo punktow -> wciecia [].
- inspect.py:466-472, 480 - punkt linii bez wierzcholka skanu w 0,8 mm -> brak, nie wciecie.
- inspect.py:498, 501-502 - otoczenie odcinka bez danych -> "brak_danych".
- inspect.py:514-517 - linia widoczna < linia_min_udzial -> wszystkie wciecia "brak_danych" (B pominieta).
- inspect.py:579-583 - projekt bez linii w trybie linia_i_plaszczyzna -> brzeg "sprawdzony" True -> mozliwy "ok".
- inspect.py:622-626 - filar bez linii w trybie sumy -> nie blokuje "ok".
- inspect.py:707 - pokrycie NaN -> brak "popraw_ulozenie".
- inspect.py:240-250 - brak danych do drgniecia -> drgniecie False.
- porownaj.py:90-91 - inspekcja None -> kolor = status match (zielony z match zostaje zielony).

---------------------------------------------------------------------------------------------------------------------

## T4. Porownania z progami decyzji

Kolumny: plik:linia | lewa strona | op | prog (klucz / stala = wartosc) | jednostka | uklad | ostre.
Wartosci kluczy `ust[...]` z ustawienia.przyklad.toml (brak ustawienia.toml w worktree; `ust.get(...)` w 10 plikach nie wystepuje).

| # | plik:linia | lewa strona | op | prog | jednostka | uklad | ostre |
|---|---|---|---|---|---|---|---|
| T4-001 | inspect.py:183 | `face_adjacency_angles` | > | `radians(KAT_KRAWEDZI_DEG)` = 40 st. | rad | - | tak |
| T4-002 | inspect.py:246 | d | > | [inspect] drgniecie_odchylka_mm = 0.07 | mm | P | tak |
| T4-003 | inspect.py:247 | d | < | -drgniecie_odchylka_mm = -0.07 | mm | P | tak |
| T4-004 | inspect.py:248 | n (punkty w komorce KOMORKA_DRGNIECIA_MM = 1.0) | >= | MIN_PUNKTOW_DRGNIECIA = 20 | N | - | nie |
| T4-005 | inspect.py:252 | zle / n | >= | drgniecie_udzial_w_komorce = 0.10 | U | - | nie |
| T4-006 | inspect.py:257 | min(n_nad, n_pod) | >= | UDZIAL_DRUGIEJ_STRONY = 0.2 x (n_nad + n_pod) | N | - | nie |
| T4-007 | inspect.py:268 | najwieksza (skupisko komorek) | <= | NAJWIEKSZA_PLAMA_DRGNIECIA = 0.6 | U | - | nie |
| T4-008 | inspect.py:269 | udzial rozmytych komorek | >= | drgniecie_udzial_obszaru = 0.10 | U | - | nie |
| T4-009 | inspect.py:307 | d | <= | -prog_glebokosci_mm = -0.08 | mm | P | nie |
| T4-010 | inspect.py:311 (280) | odleglosc par punktow rdzenia | query_pairs | EPS_PLAMY_MM = 0.25 | mm | P | bibl. |
| T4-011 | inspect.py:317 | len(idx) | < | min_punktow_plamy = 6 | N | - | tak |
| T4-012 | inspect.py:321 | odleglosc od rdzenia (pierscien) | query_ball_point | krawedz_pas_mm = 0.15 | mm | P | bibl. |
| T4-013 | inspect.py:330 | n_pier / med_pier | >= / <= | min_punktow_plamy = 6 / prog_glebokosci_mm / 2 = 0.04 | N / mm | P | nie |
| T4-014 | inspect.py:343 | odl. srodka plamy od ostrej krawedzi | <= | ODLEGLOSC_KRAWEDZI_MM = 0.5 | mm | P | nie |
| T4-015 | inspect.py:344 | n_pier | < | min_punktow_plamy = 6 | N | - | tak |
| T4-016 | inspect.py:346 | srednica (rozpietosc 2-98 percentyl rdzenia, 287-296) | > | poprawka_min_mm = 2.0 | mm | P | tak |
| T4-017 | inspect.py:348 | srednica | > | srednica_max_mm = 1.5 | mm | P | tak |
| T4-018 | inspect.py:352 | srednica | < | srednica_min_mm / 2 = 0.1 | mm | P | tak |
| T4-019 | inspect.py:354 | odl_brzegu | > | pas_brzegu_mm = 1.5 | mm | P | tak |
| T4-020 | inspect.py:372 | zmax trojkata | > | -(pas_brzegu_mm + 0.3) | mm | P | tak |
| T4-021 | inspect.py:380 | z punktu probki | >= | -pas_brzegu_mm | mm | P | nie |
| T4-022 | inspect.py:394 | odl. wierzcholka od linii | distance_upper_bound | pas_brzegu_mm + 0.3 | mm | P | bibl. |
| T4-023 | inspect.py:402 | odl. probki od linii | <= | pas_brzegu_mm | mm | P | nie |
| T4-024 | inspect.py:419 | odl. probki plaszczyzny od linii | > | pas_brzegu_mm | mm | P | tak |
| T4-025 | inspect.py:467 | odl. do wierzcholka skanu | distance_upper_bound | BRAK_DANYCH_MM = 0.8 | mm | P | bibl. |
| T4-026 | inspect.py:471 | N_skanu . N_linii | > | ZGODNOSC_NORMALNEJ = 0.2 | cos | - | tak |
| T4-027 | inspect.py:484 | pod (cofniecie wzdluz normalnej) | >= / >= | wciecie_min_mm = 0.2 / UDZIAL_POD = 0.7 x dl | mm | P | nie |
| T4-028 | inspect.py:490 | odleglosc par punktow wciecia | query_pairs | EPS_PLAMY_MM = 0.25 | mm | P | bibl. |
| T4-029 | inspect.py:496 | otoczenie odcinka | query_ball_point | krawedz_pas_mm = 0.15 | mm | P | bibl. |
| T4-030 | inspect.py:499 | szer / len(idx) | < / < | srednica_min_mm = 0.2 / min_punktow_plamy = 6 | mm / N | P | tak |
| T4-031 | inspect.py:501 | udz | < | 0.5 (literal) | U | - | tak |
| T4-032 | inspect.py:514 | udzial_ciagly | < | linia_min_udzial = 0.9 | U | - | tak |
| T4-033 | inspect.py:530 | udzial / przerwa | >= / <= | brzeg_min_sprawdzony = 0.9 / brzeg_max_przerwa_mm = 1.5 | U / mm | P | nie |
| T4-034 | inspect.py:547 | dl odcinka | < | ODCINEK_MIN_MM = 0.2 | mm | P | tak (tylko raport) |
| T4-035 | inspect.py:588 | odl_O (probka -> stacja O) | <= | OTOCZENIE_STACJI_MM = 0.3 | mm | P | nie |
| T4-036 | inspect.py:591 | z_danymi | >= | UDZIAL_DANYCH_STACJI = 0.5 x wszystkie | N | - | nie |
| T4-037 | inspect.py:662 | odleglosc A-B | <= | max(srednica, szerokosc)/2 + 0.3 (literal) | mm | P | nie |
| T4-038 | inspect.py:676 | w.wciecie_mm | >= | wciecie_pewne_mm = 0.4 | mm | P | nie |
| T4-039 | inspect.py:707 | pokrycie (z match) | < | [match] prog_akceptacji_pokrycie = 0.85 | U | (liczone w S, match.py:607-609) | tak |
| T4-040 | inspect.py:712 | pokrycie + w_poprawkach / len(P) | >= | prog_akceptacji_pokrycie = 0.85 | U | - | nie |
| T4-041 | inspect.py:751 | udzial_brak_danych | > | 0.2 (literal) | U | - | tak (tylko uwaga) |
| T4-042 | match.py:574 | fr.wysokosc - pr.wysokosc | > | tol = max(filtr_wymiar_mm = 1.5, filtr_wymiar_udzial = 0.15 x pr.wysokosc) | mm | fr: S, pr: P (bez s) | tak |
| T4-043 | match.py:576 | fr.wysokosc | < | min(pr.wysokosc - tol, filtr_wysokosc_min_udzial = 0.5 x pr.wysokosc) | mm | S vs P | tak |
| T4-044 | match.py:580 | abs(obrys fr - obrys pr) | > | tol(b) jw. | mm | S vs P | tak |
| T4-045 | match.py:582 | abs(fr.hull - hull) (tylko gdy hull > 0) | > | filtr_objetosc_udzial = 0.35 x hull | mm3 | S vs P | tak |
| T4-046 | match.py:608 | d = odleglosc / s | <= | odleglosc_max_mm = 0.05 | mm | S | nie |
| T4-047 | match.py:611 | odl. punktow projektu od fragmentu | distance_upper_bound | 2 x odleglosc_max_mm x s | mm | P | bibl. |
| T4-048 | match.py:624 | RANSAC fitness | < | 0.2 (literal) | U | - | tak |
| T4-049 | match.py:642 | d (przeglad obrotow, T sztywna) | <= | 4 x odleglosc_max_mm = 0.2 | mm | S | nie |
| T4-050 | match.py:643-644 | pokrycie zgrubne | >= | max - REMIS_OBROTU (0.02) | U | - | nie |
| T4-051 | match.py:645 | len(remis) | > | KANDYDATOW_OBROTU = 4 | N | - | tak |
| T4-052 | match.py:675 | pokrycie po RANSAC | < | prog_akceptacji_pokrycie = 0.85 | U | - | tak |
| T4-053 | match.py:696 | len(X) | > | WSTEPNY_PUNKTOW = 300 | N | - | tak |
| T4-054 | match.py:743, 747 | odl. do chmury / r | distance_upper_bound / <= | WSTEPNY_ODL_SASIADA = 0.35 / WSTEPNY_PROG_MM = 0.1 | mm | S vs P | bibl. / nie |
| T4-055 | match.py:847 | odl / s | < | SKALA_ODL_MAX = 0.5 | mm | S | tak |
| T4-056 | match.py:848 | blisko.sum() | < | SKALA_MIN_PUNKTOW = 300 | N | - | tak |
| T4-057 | match.py:852 | abs(r) | < | c = max(4,685 x sigma, SKALA_C_MIN = 0.03) | mm | S | tak |
| T4-058 | match.py:865 | abs(s - 1) | > | SKALA_GRANICA = 0.05 | U | - | tak |
| T4-059 | match.py:897 | z punktu w ukladzie puli | <= | -korekta_skali_pas_brzegu_mm = -2.0 | mm | P | nie |
| T4-060 | match.py:900 | len(Qp) | < | SKALA_MIN_PUNKTOW = 300 | N | - | tak |
| T4-061 | match.py:912 | abs(srednia reszta otoczenia) | <= | max(SKALA_OBSZAR_MM = 0.03, sigma) | mm | S | nie |
| T4-062 | match.py:960 | pok po korekcie | < | prog_akceptacji_pokrycie = 0.85 -> `niepewna` | U | - | tak |
| T4-063 | match.py:961 | abs(e) | > | korekta_skali_ostrzezenie_proc = 0.3 | % | - | tak |
| T4-064 | match.py:962 | abs(e) | > | korekta_skali_okno_proc = 1.0 + SKALA_DOKLADNOSC_PROC = 0.05 | % | - | tak |
| T4-065 | match.py:966 | pok | < | prog_ostrzezenia_pokrycie = 0.6 | U | - | tak |
| T4-066 | match.py:968 | pok | < | k.pokrycie - SKALA_SPADEK_POKRYCIA (0.02) | U | - | tak |
| T4-067 | match.py:1045 | len(zbior) | > / <= | WSTEPNY_PELNYCH = 4 / WSTEPNY_RATUNEK_WSZYSTKIE = 24 | N | - | tak / nie |
| T4-068 | match.py:1058-1059, 1062, 1071 | ocena wstepna | >= | najlepsza - WSTEPNY_MARGINES (0.15) | U | - | nie |
| T4-069 | match.py:1060 | w_marg | <= | WSTEPNY_TUR x WSTEPNY_PELNYCH = 12 | N | - | nie |
| T4-070 | match.py:1103, 1116 | k.pokrycie | >= | k1.pokrycie - WARIANT_REMIS_POKRYCIA (0.02) | U | - | nie |
| T4-071 | match.py:1123 | roznica odleglosci od estymaty | < | WARIANT_ROZROZNIENIE_PROC = 0.2 | % | - | tak |
| T4-072 | match.py:1146 | len(P) | < | 50 (literal) | N | - | tak |
| T4-073 | match.py:1177 | fr.wysokosc - lk.wysokosc | > | max(filtr_wymiar_mm, filtr_wymiar_udzial x lk.wysokosc) | mm | S vs P | tak |
| T4-074 | match.py:1198 | k.pokrycie (2. kandydat) | >= | SKALA_REMIS = 0.5 x pokrycie 1. | U | - | nie |
| T4-075 | match.py:1214 | p1 / pewnosc | >= / >= | prog_akceptacji_pokrycie = 0.85 / pewnosc_min = 0.1 -> "zielony" | U | - | nie |
| T4-076 | match.py:1216 | p1 / pewnosc | >= / >= | prog_ostrzezenia_pokrycie = 0.6 / pewnosc_min = 0.1 -> "zolty" | U | - | nie |
| T4-077 | match.py:1252, 1266, 1272 | time.monotonic() | >= | termin = start + RATUNEK_LIMIT_CZASU_S (38.0) - RATUNEK_ZAPAS_INSPEKCJI_S (0.25) x len(wyniki) (1314) | s | - | nie |
| T4-078 | match.py:1263, 1272 | zrobione | >= | limit (RATUNEK_PLYTKA_MAX = 60 minus zuzyte, 1322) | N | - | nie |
| T4-079 | match.py:1261 | najl | >= | prog_ostrzezenia_pokrycie = 0.6 | U | - | nie |
| T4-080 | match.py:1284 | nowe | >= | prog_akceptacji_pokrycie = 0.85 | U | - | nie |
| T4-081 | match.py:1286 | nowe / najl | >= / < | prog_ostrzezenia_pokrycie = 0.6 | U | - | nie / tak |
| T4-082 | match.py:1316 | pokrycie najlepszego (klucz sortowania) | >= | prog_ostrzezenia_pokrycie = 0.6 | U | - | nie |
| T4-083 | plate.py:157 | len(P) | < | 1000 (literal) | N | - | tak |
| T4-084 | plate.py:171 | abs(odl) / abs(N . n) | < / > | PROG_PLASZCZYZNY = 0.1 / cos 8 st. | mm / cos | S | tak |
| T4-085 | plate.py:172 | bl.sum() | < | 500 (literal) | N | - | tak |
| T4-086 | plate.py:296, 311 | reszta Kabscha rms | <= / > | RESZTA_ZNACZNIKOW_MAX = 0.3 | mm | S | nie / tak |
| T4-087 | plate.py:439 | abs(Z - thickness) | <= | PROG_WIERZCHU_SKANU = 0.15 | mm | S | nie |
| T4-088 | plate.py:440 | Z | < | thickness - GLEBOKOSC_DZIURY_MIN (1.5) | mm | S | tak |
| T4-089 | plate.py:445 | gniazdo_nad_pelnym / dziura_w_pelnym | < / < | PROG_GNIAZDO_NAD_PELNYM_MM2 = 150 / PROG_DZIURA_W_PELNYM_MM2 = 50 | mm2 | S | tak |
| T4-090 | plate.py:459 | bl.sum() | < | MIN_PUNKTOW_DOLKA = 15 | N | - | tak |
| T4-091 | plate.py:463 | z5 | < | thickness - GLEBOKOSC_DOLKA_MIN (0.4) | mm | S | tak |
| T4-092 | plate.py:495 | odl / zgodne | <= / > | PROG_PLYTKI = 0.12 / PROG_NORMALNEJ = -0.3 | mm / cos | S | nie / tak |
| T4-093 | plate.py:499 | z | < | zt + 0.7 (literal) | mm | S | tak |
| T4-094 | plate.py:524 | odl. do punktu probki | < | 1.0 (literal) | mm | S | tak |
| T4-095 | plate.py:531 | sel.sum() | < | MIN_PUNKTOW_FRAGMENTU = 300 | N | - | tak |
| T4-096 | plate.py:535 | max(rozm x, y) / rozm z | < / < | MIN_ROZMIAR_FRAGMENTU_XY = 3.0 / MIN_ROZMIAR_FRAGMENTU_Z = 1.5 | mm | S | tak |
| T4-097 | plate.py:537 -> uklad.py:92 | odleglosc_do_obrysu | <= | MARGINES_GNIAZDA = 1.0 | mm | S | nie |
| T4-098 | plate.py:540 -> uklad.py:92 | odleglosc_do_obrysu | <= | MARGINES_GNIAZDA + 0.5 | mm | S | nie |
| T4-099 | plate.py:544 | udzial w gniezdzie | < | 0.6 (literal) | U | - | tak |
| T4-100 | plate.py:614 | rms stozka / abs(z_wierzcholka - oczekiwane) | <= / < | RESZTA_STOZKA_MAX = 0.08 / 0.3 (literal) | mm | S | nie / tak |
| T4-101 | plate.py:746 | r / z | >= <= / <= >= | R_KSZTALTU_MIN = 47.5, R_KSZTALTU_MAX = 75.0 / PROG_WIERZCHU_SKANU = 0.15, PAS_KSZTALTU_Z = 3.0 | mm | S | nie |
| T4-102 | plate.py:751 | odl. od modelu | > | PROG_KSZTALTU_ODL = 0.3 | mm | S | tak |
| T4-103 | plate.py:831 | roznica pol niewyjasnionych | >= | PROG_KSZTALTU_MM2 = 40 | mm2 | S | nie |
| T4-104 | krawedz.py:317 | gl (glebokosc niecki) | > | GLEB_RDZENIA = 0.3 | mm | R | tak |
| T4-105 | krawedz.py:325 | pole / gmax | >= / >= | POLE_MIN = 2.0 / GLEB_MAX_MIN = 1.0 | mm2 / mm | R | nie |
| T4-106 | krawedz.py:406, 460 | nz / n2[:, 1] | > | COS_GORA = 0.64 | cos | - | tak |
| T4-107 | krawedz.py:482 | R.min(1) | > | R_MIN_PRZEKROJU = 0.2 | mm | R | tak |
| T4-108 | krawedz.py:509 | abs(r - rb) / z | <= / >= | OKNO_STARTU = 0.6 | mm | R | nie |
| T4-109 | krawedz.py:536, 566 | przeb | > / < | DROGA_MAX = 2.0 | mm | R | tak |
| T4-110 | krawedz.py:540 | n2 . rn | < | cos(ANG_ROG_DEG = 25 st.) | cos | - | tak |
| T4-111 | krawedz.py:552 | d2 | < | DL_SCIANY = 0.10 | mm | R | tak |
| T4-112 | krawedz.py:568, 571 | n2[nxt2, 1] / z | <= / < | W_NZ = 0.7 / ztop - W_DZ (0.1) | cos / mm | R | nie / tak |
| T4-113 | krawedz.py:629 | odstep od mediany sasiadow | <= | ODST_MED = 0.15 | mm | R | nie |
| T4-114 | krawedz.py:692 | abs(rb - rbf) | > | ODST_GRZBIETU = 0.4 | mm | R | tak |
| T4-115 | krawedz.py:715, 734 | odstep O od krzywej | > / < | ODST_O = 0.25 | mm | R | tak |
| T4-116 | krawedz.py:723, 824, 827 | dd | <= | ZGODA_MM = 0.10 | mm | R | nie |
| T4-117 | krawedz.py:727 | zg.sum() | >= | ZGODNYCH_MIN = 40 | N | - | nie |
| T4-118 | krawedz.py:810 | przerwa / skok | <= / <= | PRZERWA_DOBRA_ST = 5.0 / SKOK_DOBRY_MM = 0.6 | deg / mm | R | nie |
| T4-119 | krawedz.py:830 | szerokosc O-I | >= / <= | SZER_MIN = 0.10 / SZER_MAX = 1.50 | mm | R | nie |
| T4-120 | krawedz.py:831 | zg (liczba zgodnych zrodel) | >= | 2 (literal) | N | - | nie |
| T4-121 | krawedz.py:835 | udzial / ciag | >= / <= / >= | UDZIAL_WIARYGODNA = 0.9, CIAG_WIARYGODNA_ST = 10.0, UDZIAL_CZESCIOWA = 0.6 | U / deg | - | nie (werdykt tylko raport) |
| T4-122 | synth.py:181 | max(dol, gora) | < / < | 1.0 i 1.5 x min(dol, gora) (literal) | mm | plik projektu | tak ("niejasny" -> brzeg na dole; uzywane w match.Projekt, match.py:213) |
| T4-123 | synth.py:241, 452 | z wierzcholka | > | z_max - pas_brzegu ([inspect] pas_brzegu_mm = 1.5) | mm | projekt x w | tak |
| T4-124 | synth.py:450 | odl. od pewnej stacji linii | distance_upper_bound | pas_brzegu = 1.5 | mm | projekt x w | bibl. |
| T4-125 | synth.py:503 | odleglosc od innych kul | >= | ODSTEP_UKRUSZEN_MM = 2.0 + rozmiar + r | mm | projekt x w | nie |
| T4-126 | synth.py:514 | odl. od linii O/S/I | distance_upper_bound | rozmiar + SCIANA_OD_KRAWEDZI_MM (0.15) | mm | projekt x w | bibl. |
| T4-127 | synth.py:587 | normalna z | >= | NORMALNA_NIEWIDOCZNA = -0.15 | cos | - | nie |
| T4-128 | synth.py:710, 960 | szerokosc pracy | > | PROG_MOSTU_MM = 20.0 | mm | projekt x w | tak |
| T4-129 | synth.py:764, 767 | uniesienie | > | MAKS_UNIESIENIE = 1.5 | mm | plytka | tak |
| T4-130 | synth.py:772 | przenikanie | > | TOLERANCJA_PRZENIKANIA = 1e-6 | mm | plytka | tak |
| T4-131 | synth.py:928 | glebokosc (nominalna: 0,7 r albo rozmiar) / srednica | >= / <= <= | prog_glebokosci_mm = 0.08 / srednica_min_mm = 0.2, srednica_max_mm = 1.5 -> `wykrywalny` w prawdzie | mm | projekt x w | nie |
| T4-132 | metryki.py:92 | wartosc metryki | >= (min) / <= (max) | PROGI (68-78) | U / min / dni | - | nie |
| T4-133 | metryki.py:108, 234 | minuty przerwy | <= | PRZERWA_MIN = 10 | min | - | nie |
| T4-134 | metryki.py:150 | pokrycie 1. kandydata (None -> 0.0) | < | prog_kandydata = [match] prog_ostrzezenia_pokrycie = 0.6 (143) albo SR.PROG_KANDYDATA = 0.6 | U | - | tak |
| T4-135 | metryki.py:261 | minuty na zmiane | > | PROGI["czas_wieczor"] = 20.0 | min | - | tak |
| T4-136 | metryki.py:449 | seria / dni_historii | < | PROGI["dni_bez_awarii"] = 5 | dni | - | tak |
| T4-137 | wspolczynniki.py:145 | w | <= <= | WSPOLCZYNNIK_MIN = 1.0 / WSPOLCZYNNIK_MAX = 1.6 | - | - | nie |
| T4-138 | wspolczynniki.py:242 | dni w przyszlosc | > | PRZYSZLOSC_DNI = 2 | dni | - | tak |
| T4-139 | wspolczynniki.py:250 | wiek wiersza | > | OKNO_DAT_DNI = 60 | dni | - | tak |
| T4-140 | porownaj.py:263 | p.wspolczynnik vs w_ | isclose | abs_tol 1e-9 (literal) | - | - | - |
| T4-141 | porownaj.py:372 | max_przesuniecie_mm | < | 0.05 (literal; metryka) | mm | S | tak |
| T4-142 | porownaj.py:615 | wspolczynnik z CSV wpisow | <= <= | 0.5 / 2.0 (literal) | - | - | nie |

Pominiete jako czysta pamiec podreczna: inspect.py:220 (`_BRZEGI_MAX` = 256), krawedz.py:961 (`_PAMIEC_MAX` = 512).
katalog.py: brak porownan z progami. uklad.py: tylko walidacja pliku (np. 284 `> 0.01`, 306 zakres numeru) i T4-097/098.

Uwagi faktograficzne do T4 (z kodu, bez oceny):
- Wciecie metody B jest mierzalne tylko, gdy najblizszy wierzcholek skanu o zgodnej normalnej lezy w BRAK_DANYCH_MM = 0.8 mm
  (inspect.py:467, 476); wciecie >= wciecie_min_mm (0.2) i >= 0.7 x dl (484).
- Dolna granica srednicy: metoda A `srednica_min_mm / 2` = 0.1 na rozpietosci rdzenia (inspect.py:352); metoda B `srednica_min_mm`
  = 0.2 (499); generator `wykrywalny` `srednica_min_mm` = 0.2 na srednicy nominalnej (synth.py:928).
- Pokrycie z match jest udzialem punktow fragmentu po voxelizacji 0.15 mm (match.py:546, 606-609); w inspect.py:712 do pokrycia
  dodawany jest `w_poprawkach / len(P)` liczony na surowych punktach fragmentu (P z plate).
- W ocena_brzegu tryb sumy (`tylko_dane`) stacja jest "sprawdzona" tylko na podstawie `ma_dane` (wierzcholek skanu o zgodnej normalnej
  w 0.8 mm, inspect.py:473, 597); weryfikacja linii projektu (`zweryf`) wtedy nie blokuje (inspect.py:597, 601-607).

### T4-B. Wartosci kluczy: ustawienia.przyklad.toml vs wartosci domyslne w kodzie (ustawienia.py)

ustawienia.toml: brak w worktree. ustawienia.py nie ma wartosci domyslnych dla kluczy wymaganych - jedyne domyslne to
`DOMYSLNE_NOWYCH` (ustawienia.py:156-192). Walidacja: ustawienia.py:263-267 (typ, NaN/inf) i 277-300 (zakresy).

| sekcja.klucz | przyklad.toml (linia) | DOMYSLNE_NOWYCH (linia) | walidacja ustawienia.py | uzycie (plik:linia) | ROZNICA |
|---|---|---|---|---|---|
| match.prog_akceptacji_pokrycie | 0.85 (39) | brak (wymagany) | 292: 0 < x <= 1 | match 675, 960, 1214, 1284; inspect 707, 712 | - |
| match.odleglosc_max_mm | 0.05 (40) | brak | 293: > 0 | match 608, 611, 642, 956 | - |
| match.prog_ostrzezenia_pokrycie | 0.6 (41) | brak | 294: 0 < x <= prog_akceptacji | match 966, 1216, 1261, 1286, 1316; metryki 143 | - (session_rano.py:79 PROG_KANDYDATA = 0.6, rowne) |
| match.pewnosc_min | 0.1 (42) | brak | 295: [0, 1] | match 1214, 1216 | - |
| match.filtr_wymiar_mm | 1.5 (43) | brak | 296: >= 0 | match 573, 1176; nadpisywany 1e9: porownaj 85, match 1038, 1163, 1256 | - |
| match.filtr_wymiar_udzial | 0.15 (44) | brak | 296: >= 0 | match 573, 1176 | - |
| match.filtr_objetosc_udzial | 0.35 (45) | brak | 296: >= 0 | match 582 (nadpisywany 1e9 jw.) | - |
| match.filtr_wysokosc_min_udzial | 0.5 (46) | 0.5 (157) | 297: [0, 1] | match 576 | brak |
| match.korekta_skali | true (47) | True (157) | typ bool | match 942 | brak |
| match.korekta_skali_okno_proc | 1.0 (48) | 1.0 (157) | 298: (0, 5] | match 962 | brak |
| match.korekta_skali_ostrzezenie_proc | 0.3 (49) | 0.3 (157) | 299: [0, okno] | match 961 | brak |
| match.korekta_skali_pas_brzegu_mm | 2.0 (50) | 2.0 (158) | 300: >= 0 | match 946 -> 897 | brak |
| inspect.prog_glebokosci_mm | 0.08 (56) | brak | 282: > 0 | inspect 306-307, 330, 692-693; synth 817, 928 | - |
| inspect.srednica_min_mm | 0.2 (57) | brak | 281: 0 < min <= max | inspect 352 (/2), 499; synth 814-815, 928 | - |
| inspect.srednica_max_mm | 1.5 (58) | brak | 281, 284 | inspect 348; synth 814-815, 928 | - |
| inspect.pas_brzegu_mm | 1.5 (59) | brak | 283: > 0 | inspect 354, 455 (-> 372, 380, 394, 402, 419), 723; synth 238, 442, 493, 816 | - |
| inspect.poprawka_min_mm | 2.0 (60) | brak | 284: >= srednica_max_mm | inspect 346 | - |
| inspect.krawedz_pas_mm | 0.15 (61) | brak | BRAK warunku zakresu (tylko typ i skonczonosc, 263-267) | inspect 321, 496 | - |
| inspect.min_punktow_plamy | 6 (62) | brak | 285: >= 1 | inspect 317, 330, 344, 499 | - |
| inspect.drgniecie_odchylka_mm | 0.07 (63) | brak | 286: > 0 | inspect 246-247 | - |
| inspect.drgniecie_udzial_w_komorce | 0.10 (64) | brak | 286: (0, 1] | inspect 252 | - |
| inspect.drgniecie_udzial_obszaru | 0.10 (65) | brak | 286: (0, 1] | inspect 269 | - |
| inspect.wciecie_min_mm | 0.2 (66) | brak | 287: 0 < min <= pewne | inspect 455 -> 484 | - |
| inspect.wciecie_pewne_mm | 0.4 (67) | brak | 287 | inspect 676 | - |
| inspect.linia_min_udzial | 0.9 (68) | brak | 288: [0, 1] | inspect 514 | - |
| inspect.pas_brzegu_od | "linia_i_plaszczyzna" (69) | "linia_i_plaszczyzna" (159) | 289: jedna z 3 nazw | inspect 702-703 | brak |
| inspect.brzeg_min_sprawdzony | 0.9 (70) | 0.9 (159) | 290: [0, 1] | inspect 530 | brak |
| inspect.brzeg_max_przerwa_mm | 1.5 (71) | 1.5 (159) | 291: >= 0 | inspect 530 | brak |
| synth.szum_sigma_mm | 0.03 (74) | brak | 277: >= 0 | synth 812 | - |
| synth.wspolczynnik_min / _max | 1.20 / 1.25 (75-76) | brak | 278: 0 < min <= max | synth 813; porownaj 81 (srodek = 1.225) | - (patrz nizej: inne zakresy wspolczynnika w kodzie) |
| synth.odstep_ubytku_mm | 0.05 (77) | 0.05 (160) | 279: > 0 | synth 444, 495, 818 | brak |
| synth.krawedz_rozmiar_min_mm | 0.08 (78) | 0.08 (160) | 280 | synth 819 | brak |
| synth.krawedz_rozmiar_max_mm | 0.40 (79) | 0.40 (160) | 280 | synth 819 | brak |

Porownane wszystkie 43 klucze `DOMYSLNE_NOWYCH` (match 5, inspect 3, synth 3, excel 7, sciezki 5, ramki 2, sesja 6,
scanner 6, silnik 6) z ustawienia.przyklad.toml: ROZNIC BRAK.

Stale w kodzie odpowiadajace wartosciom ustawien (porownanie, bez oceny):
- session_rano.py:79 PROG_KANDYDATA = 0.6 = przyklad [match] prog_ostrzezenia_pokrycie 0.6 - rowne.
- session.py:56-57, wspolczynniki.py:59, pula.py:48 GRANICA_DOBY_GODZ = 6, ZMIANY_START_GODZ = (6, 14, 22) = przyklad [sesja] - rowne.
- Zakres wspolczynnika skurczu w kodzie: [synth] 1.20-1.25 (przyklad), wspolczynniki.py:50-51 1.0-1.6, porownaj.py:615 0.5-2.0,
  krawedz.py:54 SKALA_ODNIESIENIA 1.22, porownaj.py:81 domyslny wieczorny 1.225, synth.py:42 poranny 1.0 - rozne wartosci.
- synth.UST.domyslne() (synth.py:238, 442, 444, 493, 495, 853, 865) czyta ustawienia.toml (ustawienia.py:20, 370-372);
  w tym worktree pliku nie ma, wiec wczytaj_ustawienia rzuca FileNotFoundError (ustawienia.py:351-354), gdy synth jest wolany bez `ust`.

---------------------------------------------------------------------------------------------------------------------

## Nie przejrzane / ograniczenia

- Nie przejrzane: statusy.py (ma `INSPEKCJE_NIESPRAWDZONE = (None, "pominieto", "nie_sprawdzono")`, statusy.py:127 - mozliwe dalsze
  mapowanie statusu gniazda), session.py, session_rano.py, silnik.py, aplikacja.py, kontroler_api.py (np. kontroler_api.py:4122
  "zielony_pominieto"), pamiec_puli.py, pula.py, ui/*, testy. Nie sprawdzono, jak te moduly wolaja `porownaj` (np. parametr `inspekcja`).
- Bez uruchamiania nie ustalono: zachowania Open3D dla pustego tensora (inspect.odchylki, match.ocena), scislosci granic w
  cKDTree (`distance_upper_bound`, `query_pairs`, `query_ball_point`), czy trimesh.load usuwa NaN ze skanu.
- W T4 nie wypisano porownan czysto wewnetrznych bez progu (np. porownania indeksow, dlugosci list przy budowie tablic) ani walidacji
  pliku uklad.json poza T4-097/098.
