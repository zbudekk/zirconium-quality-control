# -*- coding: utf-8 -*-
"""Testy walidatora parametry.json (wczytaj_parametry, porownaj_plan_z_json) i funkcji czystych generatora.

Uruchomienie (bez pisania do wyniki_v2/):
    blender -b --factory-startup -P test_walidator.py -- <katalog z kopia ramka_generator.py + parametry.json + plan_ramki_v2.md>

Każdy przypadek: modyfikacja JSON w pamięci -> zapis do pliku tymczasowego -> wczytaj_parametry -> wynik.
"""
import json, os, sys, copy, tempfile, struct, math, hashlib, traceback

argv = sys.argv[sys.argv.index('--') + 1:]
KAT = os.path.abspath(argv[0])
sys.path.insert(0, KAT)
import ramka_generator as G

with open(os.path.join(KAT, 'parametry.json'), encoding='utf-8') as f:
    BAZA = json.load(f)
TMP = tempfile.mkdtemp(prefix='walidator_')


def ustaw(d, klucz, value=None, status=None, usun=False, wzor=None, sekcja_docelowa=None):
    for sekcja, zaw in d.items():
        if sekcja.startswith('_') or klucz not in zaw:
            continue
        if usun:
            del zaw[klucz]
            return
        if value is not None:
            zaw[klucz]['value'] = value
        if status is not None:
            zaw[klucz]['status'] = status
        if wzor is not None:
            zaw[klucz]['wzor'] = wzor
        return
    if sekcja_docelowa:
        d[sekcja_docelowa][klucz] = {'value': value, 'status': status or 'ZALOZENIE'}
        return
    raise KeyError(klucz)


def przypadek(nazwa, mod, tekst=None):
    """mod: funkcja modyfikujaca slownik; tekst: surowy tekst JSON (nadpisuje mod)."""
    sc = os.path.join(TMP, nazwa + '.json')
    if tekst is None:
        d = copy.deepcopy(BAZA)
        mod(d)
        with open(sc, 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
    else:
        with open(sc, 'w', encoding='utf-8') as f:
            f.write(tekst)
    try:
        P, STATUS, liczone = G.wczytaj_parametry(sc)
        wyn = 'PRZESZEDL'
        info = 'LICZONE: ' + ', '.join('%s=%.3f' % (k, v[0]) for k, v in sorted(liczone.items()))
    except G.BladProjektu as e:
        wyn, info = 'BladProjektu', str(e)[:200]
    except Exception as e:
        wyn, info = 'WYJATEK ' + type(e).__name__, str(e)[:200]
    print('[test] %-32s %-14s %s' % (nazwa, wyn, info))
    return wyn


print('=== wczytaj_parametry: przypadki brzegowe ===')
przypadek('baza', lambda d: None)
przypadek('pi_stack_h_31_ZMIERZONE', lambda d: ustaw(d, 'pi_stack_h', 31, 'ZMIERZONE'))
przypadek('pi_stack_h_31_pi_clear_3', lambda d: (ustaw(d, 'pi_stack_h', 31, 'ZMIERZONE'), ustaw(d, 'pi_clearance_top', 3)))
przypadek('pi_stack_h_31_pi_clear_-2', lambda d: (ustaw(d, 'pi_stack_h', 36, 'ZMIERZONE'), ustaw(d, 'pi_clearance_top', -2)))
przypadek('panel_led_h_4_ZMIERZONE', lambda d: ustaw(d, 'panel_led_h', 4, 'ZMIERZONE'))
przypadek('panel_led_h_4_led_gap_3', lambda d: (ustaw(d, 'panel_led_h', 4, 'ZMIERZONE'), ustaw(d, 'led_gap', 3)))
przypadek('wall_t_ujemna', lambda d: ustaw(d, 'wall_t', -2))
przypadek('dc_hole_d_zero', lambda d: ustaw(d, 'dc_hole_d', 0))
przypadek('plate_size_zero', lambda d: ustaw(d, 'plate_size', 0))
przypadek('dc_hole_d_mniejszy_od_tulejki', lambda d: ustaw(d, 'dc_hole_d', 11.5))
przypadek('wall_t_string', lambda d: ustaw(d, 'wall_t', '2.5'))
przypadek('wall_t_bool', lambda d: ustaw(d, 'wall_t', True))
przypadek('wall_t_null', lambda d: ustaw(d, 'wall_t', None) or d['korpus']['wall_t'].__setitem__('value', None))
przypadek('klucz_nieznany', lambda d: ustaw(d, 'nowy_klucz', 1, sekcja_docelowa='korpus'))
przypadek('klucz_brak', lambda d: ustaw(d, 'wall_t', usun=True))
przypadek('status_nieznany', lambda d: ustaw(d, 'wall_t', status='POMIAR'))
przypadek('LICZONE_bez_wzoru', lambda d: d['korpus']['korpus_h'].pop('wzor'))
przypadek('LICZONE_wzor_zly_klucz', lambda d: ustaw(d, 'korpus_h', wzor='blat_top_zz - blat_t'))
przypadek('LICZONE_wzor_cykl', lambda d: (ustaw(d, 'korpus_h', wzor='blat_top_z - blat_t'), ustaw(d, 'blat_top_z', wzor='korpus_h + blat_t')))
przypadek('LICZONE_wzor_kod', lambda d: ustaw(d, 'korpus_h', wzor='__import__("os").getcwd() and 59.6'))
przypadek('LICZONE_wzor_dunder', lambda d: ustaw(d, 'korpus_h', wzor='().__class__.__base__.__subclasses__() and 59.6'))
przypadek('wzor_na_ZALOZENIE', lambda d: ustaw(d, 'wall_t', wzor='999'))
przypadek('ZMIERZONE_na_LICZONE', lambda d: ustaw(d, 'korpus_h', 70, 'ZMIERZONE'))
# surowy tekst: NaN, Infinity, zdublowany klucz w jednej sekcji
baza_txt = json.dumps(BAZA, ensure_ascii=False, indent=1)
przypadek('NaN_w_value', None, baza_txt.replace('"wall_t": {\n   "value": 2.5', '"wall_t": {\n   "value": NaN', 1))
przypadek('Infinity_w_value', None, baza_txt.replace('"wall_t": {\n   "value": 2.5', '"wall_t": {\n   "value": Infinity', 1))
przypadek('NaN_w_LICZONE', None, baza_txt.replace('"korpus_h": {\n   "value": 59.6', '"korpus_h": {\n   "value": NaN', 1))
dup = baza_txt.replace('"wall_t": {', '"wall_t": {"value": 1.0, "status": "SPEC"}, "wall_t": {', 1)
przypadek('zdublowany_klucz_w_sekcji', None, dup)
przypadek('BOM_utf8', None, '﻿' + baza_txt)
przypadek('CRLF', None, baza_txt.replace('\n', '\r\n'))

print('=== porownaj_plan_z_json ===')
try:
    P, _, _ = G.wczytaj_parametry(os.path.join(KAT, 'parametry.json'))
    roz = G.porownaj_plan_z_json(P)
    print('[test] roznice plan<->JSON:', roz)
except Exception as e:
    print('[test] porownaj_plan_z_json WYJATEK', e)

print('=== funkcje czyste ===')
print('[test] rdzenie_podkladek t=[0.5,1,2]:', G.rdzenie_podkladek({'panel_shim_t': [0.5, 1, 2]}))
print('[test] rdzenie_podkladek t=[0.25,1.5,10,0.05]:', G.rdzenie_podkladek({'panel_shim_t': [0.25, 1.5, 10, 0.05]}))
print('[test] rdzenie_podkladek t=[0.5,0.5] (duplikat nazwy?):', G.rdzenie_podkladek({'panel_shim_t': [0.5, 0.5]}))
print('[test] seg_okregu(0)=%s seg_okregu(-1)=%s seg_okregu(1e6)=%s' % (G.seg_okregu(0), G.seg_okregu(-1), G.seg_okregu(1e6)))
print('[test] seg_luku(0, pi/2)=%s' % G.seg_luku(0, math.pi / 2))
print('[test] bity(0)=%s bity(7)=%s bity(8)=%s' % (G.bity(0), G.bity(7), G.bity(8)))

# stl_kanoniczny: znak zera i determinizm
def stl_bin(tr):
    b = bytearray(80) + struct.pack('<I', len(tr))
    for n, v in tr:
        b += struct.pack('<12fH', *(n + v[0] + v[1] + v[2] + (0,)))
    return bytes(b)

t1 = [((0.0, 0.0, 1.0), ((0, 0, 0), (1, 0, 0), (0, 1, 0))), ((-0.0, 0.0, 1.0), ((1, 1, 0), (0, 1, 0), (1, 0, 0)))]
t2 = [t1[1], t1[0]]
a, b = os.path.join(TMP, 'a.stl'), os.path.join(TMP, 'b.stl')
open(a, 'wb').write(stl_bin(t1)); open(b, 'wb').write(stl_bin(t2))
G.stl_kanoniczny(a); G.stl_kanoniczny(b)
print('[test] stl_kanoniczny: ta sama geometria w innej kolejnosci -> identyczne bajty:', open(a, 'rb').read() == open(b, 'rb').read())
t3 = [((0.0, 0.0, 1.0), t1[0][1]), ((0.0, 0.0, 1.0), t1[1][1])]   # jak t1, ale normalna +0.0 zamiast -0.0
c = os.path.join(TMP, 'c.stl'); open(c, 'wb').write(stl_bin(t3)); G.stl_kanoniczny(c)
print('[test] stl_kanoniczny: -0.0 vs +0.0 w normalnej -> identyczne bajty:', open(a, 'rb').read() == open(c, 'rb').read(), '(False = znak zera nie jest normalizowany, do_v3 #9)')
# pusty STL
e = os.path.join(TMP, 'e.stl'); open(e, 'wb').write(stl_bin([]))
try:
    G.stl_kanoniczny(e); print('[test] stl_kanoniczny pusty STL: OK (0 trojkatow)')
except Exception as ex:
    print('[test] stl_kanoniczny pusty STL: WYJATEK', ex)
# Siatka na pustym STL (jak po booleanie, ktory zjadl cala bryle)
from mathutils import Matrix
try:
    G.przygotuj_scene()
    s = G.Siatka(e, Matrix.Identity(4))
    print('[test] Siatka(pusty STL): OK, trojkaty', s.trojkaty_pliku)
except G.BladProjektu as ex:
    print('[test] Siatka(pusty STL): BladProjektu', ex)
except Exception as ex:
    print('[test] Siatka(pusty STL): WYJATEK %s: %s' % (type(ex).__name__, ex))
# STL obciety (zly rozmiar)
tr = os.path.join(TMP, 'tr.stl'); open(tr, 'wb').write(stl_bin(t1)[:-10])
try:
    G.przygotuj_scene()
    s = G.Siatka(tr, Matrix.Identity(4))
    print('[test] Siatka(obciety STL): OK, trojkaty', s.trojkaty_pliku)
except Exception as ex:
    print('[test] Siatka(obciety STL): %s: %s' % (type(ex).__name__, str(ex)[:120]))
# STL ASCII
asc = os.path.join(TMP, 'asc.stl')
open(asc, 'w').write('solid a\nfacet normal 0 0 1\nouter loop\nvertex 0 0 0\nvertex 1 0 0\nvertex 0 1 0\nendloop\nendfacet\nendsolid a\n')
try:
    G.stl_kanoniczny(asc); print('[test] stl_kanoniczny(ASCII STL): OK?!')
except Exception as ex:
    print('[test] stl_kanoniczny(ASCII STL): %s: %s' % (type(ex).__name__, str(ex)[:120]))

# K-53: BVHTree.overlap nie wykrywa bryly calkowicie zanurzonej w drugiej (bez przeciecia powierzchni)
from mathutils.bvhtree import BVHTree
def box(x0, x1):
    v = [(x, y, z) for x in (x0, x1) for y in (x0, x1) for z in (x0, x1)]
    f = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    return BVHTree.FromPolygons(v, f)
print('[test] overlap(szescian 0..10, szescian 2..8 w srodku) = %d par (0 = zanurzenie NIEWYKRYTE)' % len(box(0, 10).overlap(box(2, 8))))
print('[test] overlap(szescian 0..10, szescian 5..15 przecina) = %d par' % len(box(0, 10).overlap(box(5, 15))))
print('[test] overlap(szescian 0..10, szescian 10..20 styk sciana) = %d par' % len(box(0, 10).overlap(box(10, 20))))
print('[test] KONIEC')
