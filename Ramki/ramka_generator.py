# -*- coding: utf-8 -*-
"""
ramka_generator.py - generator czesci ramek swietlnych (plan_ramki_v2.md, protokol_weryfikacji_v2.md).

Uruchomienie (Blender 5.2.3 LTS w trybie wsadowym):
    cd <PC>\\Desktop\\Ramki
    "C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe" -b -P ramka_generator.py -- --etap A --iter 1

Argumenty po "--":
    --etap A|B|C|ALL|SPRAWDZ   etap budowy (buduje wszystko do etapu wlacznie) albo same sprawdzenia
    --etap R58|R58_SPRAWDZ     R58: tylko komplet okragly do ramki (8 plytek okraglych ramkowych, wkladka i pokrywka okragla,
                               2 JSON) - budowa i sprawdzenia K-64...K-67 albo same sprawdzenia; pliki etapow A-C tylko czytane
    --out wyniki_v2            folder wynikow (wzgledem polozenia skryptu)
    --iter n                   numer iteracji raportu
    --raport ETYKIETA          etykieta w nazwie raportu zamiast etapu (R54: raport_wykonawcy_R54_iter1.md)

Zasady (prompt_wykonawca.md):
  - jedyne zrodlo liczb: parametry.json (R14); w kodzie tylko stale narzedziowe ponizej,
  - kazda czesc modelowana w ukladzie montazowym (D3), eksport KOPII obroconej do orientacji druku,
  - sprawdzenia K-xx liczone na STL wczytanym z powrotem i przeksztalconym do ukladu montazowego.
"""

import bpy
import bmesh
import json
import math
import os
import sys
import time
import hashlib
import argparse
import datetime
import re
from mathutils import Vector, Matrix, Euler
from mathutils.bvhtree import BVHTree

KATALOG = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Stale narzedziowe (nie sa wymiarami czesci)
# ---------------------------------------------------------------------------
NADDATEK = 0.1          # bryly tnace wystaja, bryly dodatnie zanurzone o tyle (prompt: >= 0,1 mm)
SCALANIE = 0.001        # remove_doubles po booleanie (prompt)
SPAW_IMPORT = 1e-5      # spawanie wierzcholkow STL po imporcie (STL nie ma topologii)
KROK_PROMIENIA = 1e-4   # przesuniecie za trafieniem przy liczeniu przeciec promienia
DL_CIECIWY = 0.25       # maks. dlugosc boku wieloboku przyblizajacego luk [mm]
MIN_SEG = 32            # min. liczba bokow okregu
MAX_SEG = 256           # maks. liczba bokow okregu
ROZDZ_TEKSTU = 8        # resolution_u krzywych tekstu
KROK_TEKSTU = 0.04      # krok siatki pola odleglosci przy pogrubianiu napisow [mm]
TRZON_MIN = 1.0         # R22: litery bez elementow cienszych niz 1 mm
ZAPAS_TRZONU = 0.01     # zapas przy doborze offsetu fontu
TOL_LICZONE = 0.01      # R14: roznica LICZONE > 0,01 = blad
TOL_WYM = 0.1           # protokol 0.5: wymiar liniowy / gabaryt +-0,1
SONDA_BLISKO = 0.1      # protokol 0.4: sonda >= 0,1 mm od sciany
SKURCZ_K53 = 0.05       # K-53: kopie zmniejszone o 0,05 mm wzdluz normalnych
POLE_ZDEG = 1e-6        # trojkat o mniejszym polu [mm2] = zdegenerowany (naprawa przed eksportem, licznik w K-03)
ODSUNIECIE_WARIANTOW = 260   # R47: czesci wariantowe w .blend odsuniete >= 250 mm od zlozenia
ODSTEP_PLYTEK = 110     # odstep plytek wariantowych w rzedzie w .blend

# Objetosci orientacyjne z tabeli 1 protokolu (K-04b, +-30 %), cm3
OBJ_ORIENT = {
    'plytka_wieczorna': 60, 'plytka_poranna': 60, 'pokrywka': 30, 'wkladka': 16, 'blat': 83, 'korpus': 225,      # R59: plytki 59,6 / 59,9 z siatki (uklad W-b / P-e; dawniej 62 / 61)
    'plytka_okragla_wieczorna': 49, 'plytka_okragla_poranna': 50,      # R57: walec pi*50^2*8 = 62,8 minus gniazda; R59: 49,3 / 49,6 z siatki (R57: 49,0 / 50,6, wtedy 49 / 51)
    'tulejka_dc': 0.30, 'podkladka_panelu_05': 0.03, 'podkladka_panelu_1': 0.05, 'podkladka_panelu_2': 0.11,
    # R58 (komplet okragly do ramki): objetosci z siatek pierwszego przebiegu (iter1), zaokraglone
    'plytka_okragla_ramkowa_wieczorna': 49, 'plytka_okragla_ramkowa_poranna': 49, 'wkladka_okragla': 22, 'pokrywka_okragla': 25,   # R58 iter1: 48,90 / 49,19 / 22,42 / 25,26 z siatki
}

# Lista kluczy parametry.json (R14: brak klucza albo nieznany klucz = blad)
WYMAGANE_KLUCZE = {
    'blat_corner_r', 'blat_magnet_pocket_d', 'blat_magnet_pocket_depth', 'blat_pin_hole_d', 'blat_pin_hole_depth',
    'blat_post_hole_depth', 'blat_post_size', 'blat_post_w', 'blat_post_y0', 'blat_rib', 'blat_screw_csink_d',
    'blat_screw_hole_d', 'blat_screw_pitch', 'blat_screw_z', 'blat_skirt_clearance', 'blat_skirt_h', 'blat_skirt_t',
    'blat_t', 'blat_top_edge_r', 'blat_top_z', 'bonnet_dc_dir', 'bonnet_dc_plug_h', 'bonnet_dc_plug_len',
    'bonnet_dc_plug_w', 'bonnet_dc_pos_x', 'bonnet_dc_pos_y', 'box_corner_r', 'box_edge_r', 'box_outer',
    'code_bit_d_pos', 'code_dimple_d', 'code_dimple_depth', 'code_dimple_pitch', 'code_dimple_x', 'code_dimple_y0', 'code_dimples_round', 'color_brass',
    'color_graphite', 'color_pcb', 'color_plexi', 'color_white', 'cost_dye_factor', 'cost_rate_max', 'cost_rate_min',
    'cost_smooth_factor', 'cover_clearance', 'cover_corner_r', 'cover_finger_h', 'cover_finger_w',
    'cover_groove_depth', 'cover_groove_w', 'cover_groove_z', 'cover_inner_h', 'cover_skirt_below', 'cover_skirt_t',
    'cover_snap_bump', 'cover_snap_count', 'cover_snap_front_x', 'cover_snap_hgt', 'cover_snap_r', 'cover_snap_w',
    'cover_snap_z', 'cover_top_t', 'dc_bush_flange_d', 'dc_bush_flange_t', 'dc_bush_inner_d', 'dc_bush_outer_d',
    'dc_bush_t', 'dc_hole_d', 'dc_nut_d', 'dc_pocket_corner_r', 'dc_pocket_depth', 'dc_pocket_h', 'dc_pocket_w',
    'dc_pocket_wall', 'dc_pocket_x_window', 'dc_pocket_z0', 'dc_pos_x', 'dc_pos_y', 'dc_pos_z', 'dc_socket_axis',
    'dc_socket_body_d', 'dc_socket_body_l', 'diffuser_pocket', 'diffuser_pocket_r', 'diffuser_size', 'diffuser_t',
    'ev_marker_pos', 'ev_rows', 'ev_socket_d_l', 'ev_socket_d_m', 'ev_socket_d_s', 'ev_trough_hole_pitch', 'ev_trough_l',
    'ev_trough_w', 'file_suffix', 'fillet_inner_default', 'fillet_outer_default', 'finger_cut_w', 'floor_t',
    'floor_vent_l', 'floor_vent_w', 'floor_vent_x', 'floor_vent_y', 'font_name', 'font_offset', 'foot_d',
    'foot_edge_offset', 'foot_h', 'hall_lead_channel_h', 'hall_lead_channel_w', 'hall_pocket_l', 'hall_pocket_w',
    'hall_sensor_size', 'hall_wall_pass_h', 'insert_arrow_l', 'insert_arrow_w', 'insert_arrow_x', 'insert_chamfer',
    'insert_depth_m25', 'insert_depth_m3', 'insert_h', 'insert_hole_m25', 'insert_hole_m3', 'insert_label_h',
    'insert_label_text', 'insert_label_x', 'insert_label_y', 'insert_opening', 'insert_opening_r', 'insert_shelf',
    'insert_shelf_h', 'insert_wall_w', 'korpus_h', 'label_pos_z', 'label_relief_h', 'label_text_P', 'label_text_W',
    'label_text_h', 'led_gap', 'led_pitch', 'magnet_d', 'magnet_h', 'magnet_pocket_d', 'magnet_pocket_depth',
    'marker_cone_d', 'marker_cone_depth', 'marker_offset', 'materials', 'max_work_height', 'mo_marker_pos', 'mo_rows', 'mo_socket_d_l',
    'mo_socket_d_m', 'mo_socket_d_s', 'mo_trough_hole_pitch', 'mo_trough_l', 'mo_trough_w', 'notch_size',
    'number_pos_round', 'number_pos_x', 'number_pos_y', 'number_relief_h', 'number_text_h', 'orient_post', 'orient_post_chamfer',
    'orient_post_gap', 'orient_post_h', 'panel_bottom_parts_h', 'panel_conn_zone_h', 'panel_conn_zone_w',
    'panel_conn_zone_x', 'panel_conn_zone_y', 'panel_hole_offset_x', 'panel_hole_offset_y', 'panel_hole_pitch_x',
    'panel_hole_pitch_y', 'panel_hole_threaded', 'panel_led_h', 'panel_pad_d', 'panel_pad_h', 'panel_pcb_t',
    'panel_pcb_z', 'panel_screw_hole_d', 'panel_shim_d', 'panel_shim_hole_d', 'panel_shim_t', 'panel_size',
    'panel_slot_pitch_max', 'panel_slot_pitch_min', 'panel_slot_w', 'panel_standoff_l', 'pi_boss_d',
    'pi_clearance_top', 'pi_hole_d', 'pi_hole_edge', 'pi_hole_pitch_l', 'pi_hole_pitch_w', 'pi_l', 'pi_pos_x',
    'pi_pos_y', 'pi_stack_h', 'pi_standoff_h', 'pi_w', 'plate_corner_zone', 'plate_edge_r', 'plate_numbers_ev',
    'plate_numbers_mo', 'plate_numbers_round', 'plate_round_d', 'plate_size', 'plate_thickness', 'plate_top_chamfer', 'quantities', 'receiver_h',
    'receiver_l', 'receiver_w', 'round_flat_angle', 'round_flat_depth_min', 'round_flat_w', 'scan_center_tol', 'scan_field_d', 'snap_front_x', 'snap_hook_arm_l', 'snap_hook_h', 'snap_hook_hgt', 'snap_hook_t',
    'snap_hook_w', 'snap_hook_z', 'snap_notch_w', 'snap_pocket_depth', 'snap_pocket_h', 'snap_pocket_w',
    'snap_pocket_z', 'snap_rear_x', 'snap_side_y', 'socket_depth', 'socket_hole_d', 'socket_wall_angle',
    'socket_wall_min', 'socket_zone', 'socket_zone_r', 'standoff_d', 'tab_cable_channel_h', 'tab_cable_channel_w',
    'tab_cable_channel_x', 'tab_end_y', 'tab_magnet_hole_d', 'tab_magnet_y', 'tab_pin_chamfer', 'tab_pin_d',
    'tab_pin_h', 'tab_pin_y', 'tab_pos_x', 'tab_root_x_in', 'tab_root_x_out', 'tab_root_y0', 'tab_root_y1', 'tab_t',
    'tab_w', 'trough_hole_count', 'usb_body_depth', 'usb_body_h', 'usb_body_w', 'usb_cut_h', 'usb_cut_w',
    'usb_hole_d', 'usb_hole_pitch', 'usb_pos_x', 'usb_pos_z', 'usb_slot_pitch_max', 'usb_slot_pitch_min',
    'usb_slot_w', 'vent_slot_h', 'vent_slot_w', 'vent_slot_z', 'vent_slots_rear_x', 'vent_slots_side_y', 'wall_t',
    'window_through', 'wire_rabbet', 'work_overhang', 'wire_rabbet_w', 'wire_slot_l', 'wire_slot_w', 'wire_slot_x', 'wire_slot_y',
}

# R58 (komplet okragly do ramki): klucze dopisane do parametry.json. Pliki etapow A-C ich nie czytaja; K-60 przy --etap SPRAWDZ
# toleruje ich brak w zrzucie arkusz_wymiarow.md sprzed R58 (arkusze R59 bez zmian do przebiegu ALL koordynatora).
KLUCZE_R58 = {
    'round_magnet_r', 'round_key_slot_w', 'round_key_slot_r0', 'round_key_slot_h', 'plate_numbers_round_frame',
    'round_cover_snap_angles', 'round_insert_clearance', 'round_insert_ledge_r', 'round_insert_shelf',
    'round_key_rib_w', 'round_key_rib_r0', 'round_key_rib_h', 'round_key_rib_chamfer', 'round_cover_slit_w', 'round_cover_slit_h',
    'round_cover_slit_offset', 'quantities_r58', 'materials_r58', 'round_key_rib_top_r1', 'round_cover_slit_end_d',
}
WYMAGANE_KLUCZE |= KLUCZE_R58

# Klucze proponowane nadzorowi do dopisania do parametry.json (etap C). Walidator je przyjmuje, jesli sa w pliku;
# dopoki ich nie ma, skrypt bierze wartosc z planu (zrodlo w drugim polu) i wpisuje to do rejestru odstepstw.
KLUCZE_PROPONOWANE = {}      # po R50 wszystkie klucze etapu C sa w parametry.json (kolory R27, tulejka, podkladki; materialy per czesc)
_UZYTE_PROPONOWANE = set()


def proponowany(P, klucz):
    """Wartosc klucza proponowanego: z parametry.json, a gdy go nie ma - z planu (wpis do rejestru odstepstw)."""
    if klucz in P:
        return P[klucz]
    wartosc, zrodlo = KLUCZE_PROPONOWANE[klucz]
    if klucz not in _UZYTE_PROPONOWANE:
        _UZYTE_PROPONOWANE.add(klucz)
        opis = json.dumps(wartosc, ensure_ascii=False) if not isinstance(wartosc, dict) else 'tabela %d pozycji' % len(wartosc)
        DZIENNIK['odstepstwa'].append((
            '`parametry.json` / brak klucza `%s`' % klucz, 'przyjęto %s (%s)' % (opis, zrodlo),
            'wartość potrzebna w etapie C nie ma klucza; nadzór dopisuje klucze (polecenie po G3)',
            'tak — klucz do dopisania do `parametry.json` (lista w notatkach wykonawcy)'))
    return wartosc


# Klucze z tabeli 3 planu, ktore w JSON sa zapisane jako listy (liczba = dlugosc listy)
PLAN_LICZNOSCI = {'vent_slots_rear': 'vent_slots_rear_x', 'vent_slots_side': 'vent_slots_side_y'}


class BladProjektu(Exception):
    pass


# Dziennik przebiegu (ostrzezenia trafiaja do raportu)
DZIENNIK = {'ostrzezenia': [], 'odstepstwa': [], 'napisy': [], 'uklad': [], 'plan_json': [], 'stl': {}, 'ilosci_r58': []}


def log(*a):
    print('[ramka]', *a)
    sys.stdout.flush()


def ostrzez(tekst):
    DZIENNIK['ostrzezenia'].append(tekst)
    log('OSTRZEZENIE:', tekst)


# ===========================================================================
# (1) Parametry
# ===========================================================================

def wczytaj_parametry(sciezka):
    """Wczytuje parametry.json do plaskiego slownika P, waliduje klucze, liczy LICZONE (R14)."""
    with open(sciezka, encoding='utf-8') as f:
        dane = json.load(f)
    P, STATUS, WZORY = {}, {}, {}
    for sekcja, zaw in dane.items():
        if sekcja.startswith('_'):
            continue
        for k, v in zaw.items():
            if k in P:
                raise BladProjektu('parametry.json: zdublowany klucz %s' % k)
            if not isinstance(v, dict) or 'value' not in v or 'status' not in v:
                raise BladProjektu('parametry.json: klucz %s bez pola value/status' % k)
            P[k] = v['value']
            STATUS[k] = v['status']
            if 'wzor' in v:
                WZORY[k] = v['wzor']
    brak = sorted(WYMAGANE_KLUCZE - set(P))
    nadmiar = sorted(set(P) - WYMAGANE_KLUCZE - set(KLUCZE_PROPONOWANE))
    if brak:
        raise BladProjektu('parametry.json: brak kluczy %s' % brak)
    if nadmiar:
        raise BladProjektu('parametry.json: nieznane klucze %s' % nadmiar)
    # wartosci LICZONE: ze wzorow pola "wzor" (kolejne przejscia rozwiazuja zaleznosci)
    liczone = {k: w for k, w in WZORY.items() if STATUS[k] == 'LICZONE'}
    for k in STATUS:
        if STATUS[k] == 'LICZONE' and k not in liczone:
            raise BladProjektu('parametry.json: %s ma status LICZONE bez wzoru' % k)
    srodowisko = dict(P)
    for _ in range(len(liczone) + 1):
        for k, w in liczone.items():
            srodowisko[k] = eval(w, {'__builtins__': {}}, srodowisko)
    wyniki = {}
    for k in liczone:
        roznica = abs(srodowisko[k] - P[k])
        wyniki[k] = (srodowisko[k], P[k], roznica)
        if roznica > TOL_LICZONE:
            raise BladProjektu('LICZONE %s: wzor "%s" daje %.4f, plik %.4f' % (k, liczone[k], srodowisko[k], P[k]))
    return P, STATUS, wyniki


def porownaj_plan_z_json(P):
    """Klucze tabeli 3 planu musza istniec w JSON; wartosci liczbowe porownane (rejestr odstepstw)."""
    sciezka = os.path.join(KATALOG, 'plan_ramki_v2.md')
    with open(sciezka, encoding='utf-8') as f:
        tekst = f.read()
    try:
        sekcja = tekst.split('## 3. Tabela parametrów')[1].split('\n## 4.')[0]
    except IndexError:
        raise BladProjektu('plan_ramki_v2.md: nie znaleziono sekcji 3')
    wynik = []
    for linia in sekcja.splitlines():
        m = re.match(r'^\| ([a-zA-Z_0-9]+) \| ([^|]+) \|', linia)
        if not m or m.group(1) == 'Parametr':
            continue
        klucz, wartosc = m.group(1), m.group(2).strip()
        if klucz in PLAN_LICZNOSCI:
            lista = P[PLAN_LICZNOSCI[klucz]]
            if str(len(lista)) != wartosc:
                raise BladProjektu('plan %s = %s, JSON %s ma %d pozycji' % (klucz, wartosc, PLAN_LICZNOSCI[klucz], len(lista)))
            continue
        if klucz not in P:
            raise BladProjektu('klucz %s z tabeli 3 planu nie istnieje w parametry.json' % klucz)
        v = P[klucz]
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            continue
        try:
            wp = float(wartosc.replace('−', '-').replace(',', '.'))
        except ValueError:
            continue
        if abs(wp - v) > 1e-9:
            wynik.append((klucz, wp, v))
    return wynik


# ===========================================================================
# (2) Funkcje pomocnicze: profile, bryly, booleany
# ===========================================================================

def seg_okregu(r):
    return max(MIN_SEG, min(MAX_SEG, int(math.ceil(2 * math.pi * r / DL_CIECIWY))))


def seg_luku(r, kat):
    return max(2, int(math.ceil(r * kat / DL_CIECIWY)))


def okrag(r, cx=0.0, cy=0.0, n=None):
    n = n or seg_okregu(r)
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def prostokat(sx, sy, cx=0.0, cy=0.0):
    return [(cx + sx / 2, cy - sy / 2), (cx + sx / 2, cy + sy / 2), (cx - sx / 2, cy + sy / 2), (cx - sx / 2, cy - sy / 2)]


def prostokat_zaokr(sx, sy, r, cx=0.0, cy=0.0, n_luk=None):
    """Prostokat z zaokraglonymi narozami, CCW; ta sama liczba wierzcholkow dla tego samego n_luk."""
    if r <= 1e-9:
        raise BladProjektu('prostokat_zaokr: promien %.4f <= 0' % r)
    n = n_luk or seg_luku(r, math.pi / 2)
    ax, ay = sx / 2 - r, sy / 2 - r
    if ax < -1e-9 or ay < -1e-9:
        raise BladProjektu('prostokat_zaokr: promien %.3f za duzy dla %.3f x %.3f' % (r, sx, sy))
    srodki = [(ax, -ay, -90.0), (ax, ay, 0.0), (-ax, ay, 90.0), (-ax, -ay, 180.0)]
    pkt = []
    for ox, oy, a0 in srodki:
        for i in range(n + 1):
            a = math.radians(a0 + 90.0 * i / n)
            pkt.append((cx + ox + r * math.cos(a), cy + oy + r * math.sin(a)))
    return pkt


def prostokat_r(sx, sy, r, cx=0.0, cy=0.0, n_luk=None):
    """Prostokat z narozami R r albo ostry, gdy r = 0 (R50-U15: promienie wyzerowane w parametry.json)."""
    return prostokat(sx, sy, cx, cy) if r <= 1e-9 else prostokat_zaokr(sx, sy, r, cx, cy, n_luk)


def stadion(l, w, cx=0.0, cy=0.0, kat=0.0, n_pol=None, delta=0.0):
    """Stadion l x w (os dluga wzdluz X przed obrotem), odsuniety o delta na zewnatrz, CCW."""
    r = w / 2 + delta
    a = l / 2 - w / 2
    n = n_pol or max(16, int(math.ceil(math.pi * (w / 2) / DL_CIECIWY)))
    pkt = []
    for i in range(n + 1):
        t = math.radians(-90.0 + 180.0 * i / n)
        pkt.append((a + r * math.cos(t), r * math.sin(t)))
    for i in range(n + 1):
        t = math.radians(90.0 + 180.0 * i / n)
        pkt.append((-a + r * math.cos(t), r * math.sin(t)))
    c, s = math.cos(math.radians(kat)), math.sin(math.radians(kat))
    return [(cx + x * c - y * s, cy + x * s + y * c) for x, y in pkt]


def bm_z_pierscieni(pierscienie):
    """Bryla z pierscieni (lista punktow 2D albo pojedynczy punkt = wierzcholek stozka, z), od dolu do gory."""
    bm = bmesh.new()
    rings = []
    for pts, z in pierscienie:
        rings.append([bm.verts.new((x, y, z)) for (x, y) in pts])
    for a, b in zip(rings, rings[1:]):
        if len(a) == len(b):
            n = len(a)
            for i in range(n):
                j = (i + 1) % n
                bm.faces.new((a[i], a[j], b[j], b[i]))
        elif len(b) == 1:
            n = len(a)
            for i in range(n):
                bm.faces.new((a[i], a[(i + 1) % n], b[0]))
        elif len(a) == 1:
            n = len(b)
            for i in range(n):
                bm.faces.new((a[0], b[(i + 1) % n], b[i]))
        else:
            raise BladProjektu('bm_z_pierscieni: rozne liczby wierzcholkow %d / %d' % (len(a), len(b)))
    if len(rings[0]) > 2:
        bm.faces.new(list(reversed(rings[0])))
    if len(rings[-1]) > 2:
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


def bm_pryzmat(pts, z0, z1):
    return bm_z_pierscieni([(pts, z0), (pts, z1)])


def bm_walec(r, z0, z1, cx=0.0, cy=0.0):
    return bm_pryzmat(okrag(r, cx, cy), z0, z1)


def bm_prostopadloscian(x0, x1, y0, y1, z0, z1):
    return bm_pryzmat(prostokat(x1 - x0, y1 - y0, (x0 + x1) / 2, (y0 + y1) / 2), z0, z1)


def bm_pierscien(zew, wew, z0, z1):
    """Pierscien miedzy profilami zew i wew (ta sama liczba wierzcholkow, odpowiadajace sobie katy)."""
    if len(zew) != len(wew):
        raise BladProjektu('bm_pierscien: rozne liczby wierzcholkow')
    bm = bmesh.new()
    n = len(zew)
    zd = [bm.verts.new((x, y, z0)) for x, y in zew]
    zg = [bm.verts.new((x, y, z1)) for x, y in zew]
    wd = [bm.verts.new((x, y, z0)) for x, y in wew]
    wg = [bm.verts.new((x, y, z1)) for x, y in wew]
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((zd[i], zd[j], zg[j], zg[i]))
        bm.faces.new((wd[j], wd[i], wg[i], wg[j]))
        bm.faces.new((zg[i], zg[j], wg[j], wg[i]))
        bm.faces.new((zd[j], zd[i], wd[i], wd[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


def bm_skorupa(zew, wew, z_otw, z_dno_zew, z_dno_wew):
    """Skorupa otwarta z jednej strony: sciana miedzy z_otw a dnem; dno zewn. na z_dno_zew, wewn. na z_dno_wew.
    Dziala dla otwarcia u dolu (pokrywka: z_otw < z_dno) i u gory (korpus: z_otw > z_dno)."""
    if len(zew) != len(wew):
        raise BladProjektu('bm_skorupa: rozne liczby wierzcholkow')
    bm = bmesh.new()
    n = len(zew)
    zo = [bm.verts.new((x, y, z_otw)) for x, y in zew]
    zd = [bm.verts.new((x, y, z_dno_zew)) for x, y in zew]
    wo = [bm.verts.new((x, y, z_otw)) for x, y in wew]
    wd = [bm.verts.new((x, y, z_dno_wew)) for x, y in wew]
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((zo[i], zo[j], zd[j], zd[i]))
        bm.faces.new((wo[j], wo[i], wd[i], wd[j]))
        bm.faces.new((zo[j], zo[i], wo[i], wo[j]))
    bm.faces.new(zd)
    bm.faces.new(list(reversed(wd)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


def bm_profil_wyciagniety(pts2d, d0, d1, M):
    """Profil 2D (a, b) wyciagniety wzdluz lokalnej osi c od d0 do d1, przeksztalcony macierza M (lokalne -> swiat)."""
    bm = bm_z_pierscieni([(pts2d, d0), (pts2d, d1)])
    bmesh.ops.transform(bm, matrix=M, verts=bm.verts[:])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


def bm_przesun(bm, v):
    bmesh.ops.translate(bm, vec=Vector(v), verts=bm.verts[:])
    return bm


def rozdziel_wyspy(bm):
    """Dzieli bmesh na spojne skladowe (osobne bmesh)."""
    bm.verts.ensure_lookup_table()
    rodzic = list(range(len(bm.verts)))

    def znajdz(i):
        while rodzic[i] != i:
            rodzic[i] = rodzic[rodzic[i]]
            i = rodzic[i]
        return i
    for e in bm.edges:
        a, b = znajdz(e.verts[0].index), znajdz(e.verts[1].index)
        if a != b:
            rodzic[a] = b
    grupy = {}
    for f in bm.faces:
        grupy.setdefault(znajdz(f.verts[0].index), []).append(f)
    wyspy = []
    for faces in grupy.values():
        nb = bmesh.new()
        mapa = {}
        for f in faces:
            vs = []
            for v in f.verts:
                if v.index not in mapa:
                    mapa[v.index] = nb.verts.new(v.co)
                vs.append(mapa[v.index])
            nb.faces.new(vs)
        wyspy.append(nb)
    bm.free()
    return wyspy


def obiekt_z_bm(bm, nazwa, kolekcja=None):
    me = bpy.data.meshes.new(nazwa)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(nazwa, me)
    (kolekcja or bpy.context.scene.collection).objects.link(ob)
    return ob


def usun_obiekt(ob):
    me = ob.data if ob.type == 'MESH' else None
    bpy.data.objects.remove(ob, do_unlink=True)
    if me is not None and me.users == 0:
        bpy.data.meshes.remove(me)


def oczysc_siatke(ob):
    """Po booleanie: scalenie wierzcholkow, normalne na zewnatrz, validate (prompt)."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=SCALANIE)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.validate(verbose=False)
    ob.data.update()


def boolean(baza, bryly, operacja):
    """Jedna operacja EXACT bazy z suma wszystkich bryl (operand = kolekcja)."""
    if not bryly:
        return baza
    kol = bpy.data.collections.new('operand_' + operacja.lower())
    bpy.context.scene.collection.children.link(kol)
    for b in bryly:
        for c in list(b.users_collection):
            c.objects.unlink(b)
        kol.objects.link(b)
    mod = baza.modifiers.new('bool', 'BOOLEAN')
    mod.operation = operacja
    mod.operand_type = 'COLLECTION'
    mod.collection = kol
    mod.solver = 'EXACT'
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    nowa = bpy.data.meshes.new_from_object(baza.evaluated_get(dg))
    stara = baza.data
    baza.modifiers.remove(mod)
    baza.data = nowa
    bpy.data.meshes.remove(stara)
    for b in bryly:
        usun_obiekt(b)
    bpy.data.collections.remove(kol)
    oczysc_siatke(baza)
    return baza


def zbuduj_z_operacji(nazwa, bm_baza, dodatnie, tnace, dodatnie_po=None, tnace_po=None):
    """Kolejnosc z promptu: baza -> suma bryl dodatnich -> jedna roznica z suma bryl tnacych.
    dodatnie_po: bryly zewnetrzne, ktorych zadna bryla tnaca nie moze naruszyc (daszki szczelin korpusu).
    tnace_po (R57, plytki okragle): druga roznica osobno (otwory przelotowe o3) - jedna roznica ze wszystkimi bryłami zostawiala
    w bazowej plytce okraglej wieczornej 3 zbedne sciany na dnie otworow (przeciecia K-03)."""
    baza = obiekt_z_bm(bm_baza, nazwa)
    t0 = time.time()
    boolean(baza, [obiekt_z_bm(b, nazwa + '_plus%d' % i) for i, b in enumerate(dodatnie)], 'UNION')
    boolean(baza, [obiekt_z_bm(b, nazwa + '_minus%d' % i) for i, b in enumerate(tnace)], 'DIFFERENCE')
    if tnace_po:
        boolean(baza, [obiekt_z_bm(b, nazwa + '_minus_po%d' % i) for i, b in enumerate(tnace_po)], 'DIFFERENCE')
    if dodatnie_po:
        boolean(baza, [obiekt_z_bm(b, nazwa + '_po%d' % i) for i, b in enumerate(dodatnie_po)], 'UNION')
    log('%s: %d dodatnich, %d tnacych, %d po roznicy, %.1f s, %d scian' % (nazwa, len(dodatnie), len(tnace), len(dodatnie_po or []),
                                                                           time.time() - t0, len(baza.data.polygons)))
    return baza


# ---------------------------------------------------------------------------
# Napisy (R22: font z instalacji Blendera, offset dobrany tak, by trzon >= 1,0 mm)
# ---------------------------------------------------------------------------
_FONT = {}


def font(P):
    if 'f' not in _FONT:
        kat = os.path.join(bpy.utils.resource_path('LOCAL'), 'datafiles', 'fonts')
        pliki = [f for f in sorted(os.listdir(kat)) if os.path.splitext(f)[0] == P['font_name']]
        if not pliki:
            raise BladProjektu('font %s nie istnieje w %s' % (P['font_name'], kat))
        _FONT['f'] = bpy.data.fonts.load(os.path.join(kat, pliki[0]))
        _FONT['plik'] = pliki[0]
    return _FONT['f']


def kontury_fontu(P, tresc, rozmiar):
    """Kontury znakow (bez offsetu) jako lista petli [(x, y), ...]; linia bazowa y = 0.
    Font zmienny Inter ma nakladajace sie kontury skladowych (np. '1', '4'), wiec wnetrze liczone jest
    regula niezerowego nawiniecia, a nie z wypelnienia Blendera."""
    cu = bpy.data.curves.new('tekst', 'FONT')
    cu.body = tresc
    cu.font = font(P)
    cu.size = rozmiar
    cu.offset = 0.0
    cu.extrude = 0.0
    cu.resolution_u = ROZDZ_TEKSTU
    cu.fill_mode = 'NONE'
    ob = bpy.data.objects.new('tekst', cu)
    bpy.context.scene.collection.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.curves.remove(cu)
    bm = bmesh.new()
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=SPAW_IMPORT)
    petle = []
    odwiedzone = set()
    for v0 in bm.verts:
        if v0.index in odwiedzone or len(v0.link_edges) != 2:
            continue
        petla = []
        poprz, v = None, v0
        while True:
            odwiedzone.add(v.index)
            petla.append((v.co.x, v.co.y))
            nast = [e.other_vert(v) for e in v.link_edges if e.other_vert(v) is not poprz]
            if not nast:
                break
            poprz, v = v, nast[0]
            if v is v0:
                break
        if len(petla) >= 3:
            petle.append(petla)
    bm.free()
    return petle


def _krawedzie(petle):
    for p in petle:
        for i in range(len(p)):
            yield p[i], p[(i + 1) % len(p)]


def _przedzialy_wnetrza(petle, y):
    """Przedzialy x wnetrza (nawiniecie != 0) na prostej y."""
    traf = []
    for (ax, ay), (bx, by) in _krawedzie(petle):
        if (ay <= y < by) or (by <= y < ay):
            traf.append((ax + (y - ay) * (bx - ax) / (by - ay), 1 if by > ay else -1))
    traf.sort()
    przedzialy = []
    naw = 0
    start = None
    for x, s in traf:
        przed = naw
        naw += s
        if przed == 0 and naw != 0:
            start = x
        elif przed != 0 and naw == 0:
            przedzialy.append((start, x))
    return przedzialy


def _rdp(pts, tol):
    """Upraszczanie Douglasa-Peuckera petli zamknietej."""
    n = len(pts)
    if n < 8:
        return pts
    # punkt najdalszy od pts[0] dzieli petle na dwie lamane
    k = max(range(n), key=lambda i: (pts[i][0] - pts[0][0]) ** 2 + (pts[i][1] - pts[0][1]) ** 2)

    def lamana(seq):
        zostaw = [False] * len(seq)
        zostaw[0] = zostaw[-1] = True
        stos = [(0, len(seq) - 1)]
        while stos:
            a, b = stos.pop()
            if b <= a + 1:
                continue
            ax, ay = seq[a]
            bx, by = seq[b]
            dmax, imax = -1.0, a
            for i in range(a + 1, b):
                d = odl_punkt_odcinek(seq[i], (ax, ay), (bx, by))
                if d > dmax:
                    dmax, imax = d, i
            if dmax > tol:
                zostaw[imax] = True
                stos += [(a, imax), (imax, b)]
        return [p for p, z in zip(seq, zostaw) if z]
    l1 = lamana(pts[:k + 1])
    l2 = lamana(pts[k:] + [pts[0]])
    return l1[:-1] + l2[:-1]


def kontur_pogrubiony(petle, off, krok):
    """Kontur zbioru {nawiniecie != 0} powiekszonego o off (suma Minkowskiego z kolem),
    z pola odleglosci na siatce krok i marching squares; wynik bez samoprzeciec."""
    from mathutils.kdtree import KDTree
    xs = [x for p in petle for x, _ in p]
    ys = [y for p in petle for _, y in p]
    marg = off + 3 * krok
    x0, y0 = min(xs) - marg, min(ys) - marg
    nx = int(math.ceil((max(xs) + marg - x0) / krok)) + 1
    ny = int(math.ceil((max(ys) + marg - y0) / krok)) + 1
    # probki konturu do drzewa KD (odleglosc do krawedzi)
    probki = []
    for (ax, ay), (bx, by) in _krawedzie(petle):
        L = math.hypot(bx - ax, by - ay)
        m = max(1, int(math.ceil(L / (krok / 4))))
        for i in range(m):
            t = i / m
            probki.append((ax + t * (bx - ax), ay + t * (by - ay), 0.0))
    kd = KDTree(len(probki))
    for i, p in enumerate(probki):
        kd.insert(p, i)
    kd.balance()
    pole = []
    for j in range(ny):
        y = y0 + j * krok + 1e-7
        przedzialy = _przedzialy_wnetrza(petle, y)
        wiersz = []
        for i in range(nx):
            x = x0 + i * krok
            if any(a <= x <= b for a, b in przedzialy):
                wiersz.append(0.0)
            else:
                wiersz.append(kd.find((x, y, 0.0))[2])
        pole.append(wiersz)
    # marching squares, poziom off (wnetrze: wartosc <= off)

    def punkt(klucz):
        typ, i, j = klucz
        if typ == 'h':
            va, vb = pole[j][i], pole[j][i + 1]
            t = (off - va) / (vb - va)
            return (x0 + (i + t) * krok, y0 + j * krok)
        va, vb = pole[j][i], pole[j + 1][i]
        t = (off - va) / (vb - va)
        return (x0 + i * krok, y0 + (j + t) * krok)
    sasiedzi = {}

    def odcinek(a, b):
        sasiedzi.setdefault(a, []).append(b)
        sasiedzi.setdefault(b, []).append(a)
    for j in range(ny - 1):
        for i in range(nx - 1):
            v00, v10, v11, v01 = pole[j][i], pole[j][i + 1], pole[j + 1][i + 1], pole[j + 1][i]
            kod = (v00 <= off) | ((v10 <= off) << 1) | ((v11 <= off) << 2) | ((v01 <= off) << 3)
            if kod in (0, 15):
                continue
            D, Pr, G, L = ('h', i, j), ('v', i + 1, j), ('h', i, j + 1), ('v', i, j)
            srodek = (v00 + v10 + v11 + v01) / 4 <= off
            if kod in (1, 14):
                odcinek(L, D)
            elif kod in (2, 13):
                odcinek(D, Pr)
            elif kod in (3, 12):
                odcinek(L, Pr)
            elif kod in (4, 11):
                odcinek(Pr, G)
            elif kod in (6, 9):
                odcinek(D, G)
            elif kod in (7, 8):
                odcinek(L, G)
            elif kod == 5:
                if srodek:
                    odcinek(D, Pr)
                    odcinek(G, L)
                else:
                    odcinek(L, D)
                    odcinek(Pr, G)
            elif kod == 10:
                if srodek:
                    odcinek(L, D)
                    odcinek(Pr, G)
                else:
                    odcinek(D, Pr)
                    odcinek(G, L)
    for k, s in sasiedzi.items():
        if len(s) != 2:
            raise BladProjektu('kontur napisu: wezel o stopniu %d' % len(s))
    wynik = []
    uzyte = set()
    for start in sasiedzi:
        if start in uzyte:
            continue
        petla = [start]
        uzyte.add(start)
        poprz, akt = None, start
        while True:
            a, b = sasiedzi[akt]
            nast = a if a != poprz else b
            if nast == start:
                break
            poprz, akt = akt, nast
            uzyte.add(akt)
            petla.append(akt)
        pts = [punkt(k) for k in petla]
        # usun punkty zdublowane (kontur przechodzi przez wezel siatki)
        czyste = [pts[0]]
        for p in pts[1:]:
            if (p[0] - czyste[-1][0]) ** 2 + (p[1] - czyste[-1][1]) ** 2 > 1e-12:
                czyste.append(p)
        if len(czyste) >= 3:
            uproszczone = _rdp(czyste, krok / 10)
            # bez odcinkow krotszych niz krok/10 (EXACT tworzy z nich niemanifoldowe drzazgi na scianach liter)
            pr = [uproszczone[0]]
            for p in uproszczone[1:]:
                if math.hypot(p[0] - pr[-1][0], p[1] - pr[-1][1]) >= krok / 10:
                    pr.append(p)
            if len(pr) > 3 and math.hypot(pr[0][0] - pr[-1][0], pr[0][1] - pr[-1][1]) < krok / 10:
                pr.pop()
            if len(pr) >= 3:
                wynik.append(pr)
    return wynik


def bm_z_konturow(petle, z0, z1):
    """Wypelnia petle (z otworami) trojkatami i wyciaga od z0 do z1."""
    bm = bmesh.new()
    krawedzie = []
    for p in petle:
        vs = [bm.verts.new((x, y, z0)) for x, y in p]
        for i in range(len(vs)):
            krawedzie.append(bm.edges.new((vs[i], vs[(i + 1) % len(vs)])))
    bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=krawedzie)
    for e in krawedzie:
        if len(e.link_faces) != 1:
            raise BladProjektu('wypelnienie napisu: krawedz konturu z %d scianami' % len(e.link_faces))
    wyn = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
    nowe = [g for g in wyn['geom'] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=Vector((0, 0, z1 - z0)), verts=nowe)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


def szerokosci_trzonu(petle, y):
    return [b - a for a, b in _przedzialy_wnetrza(petle, y)]


def metryka_fontu(P):
    """Wysokosc wersalika c i trzon k fontu przy rozmiarze 1 (litera H, bez pogrubienia)."""
    if 'metryka' not in _FONT:
        petle = kontury_fontu(P, 'H', 1.0)
        ys = [y for p in petle for _, y in p]
        c = max(ys) - min(ys)
        k = min(szerokosci_trzonu(petle, min(ys) + 0.3 * c))
        _FONT['metryka'] = (c, k)
    return _FONT['metryka']


def parametry_tekstu(P, wys, c_wys=None):
    """Rozmiar fontu i pogrubienie off dla liter o wysokosci wys (z pogrubieniem), trzon >= TRZON_MIN.
    Pogrubienie = font_offset z parametry.json albo wieksze, jesli trzon by nie wystarczyl (R22, R47).
    c_wys: wysokosc odniesienia przy rozmiarze 1 (domyslnie wersalik H; dla napisow 'pelnych' caly obrys)."""
    c, k = metryka_fontu(P)
    if c_wys is not None:
        c = c_wys
    q = k / c
    off_min = (TRZON_MIN - q * wys) / (2 * (1 - q)) + ZAPAS_TRZONU
    off = max(P['font_offset'], off_min)
    rozmiar = (wys - 2 * off) / c
    if rozmiar <= 0:
        raise BladProjektu('napis %.2f mm: trzon %.2f mm wymaga pogrubienia %.3f, litery znikaja' % (wys, TRZON_MIN, off))
    krok = min(off / 4, KROK_TEKSTU)
    return rozmiar, off, krok


def bryly_tekstu(P, tresc, wys, relief, cx, cy, opis, pelna=False):
    """Napis w plaszczyznie XY, czytelny od +Z, wersaliki o wysokosci wys wysrodkowane na (cx, cy);
    pelna=True: caly obrys napisu (ze znakami diakrytycznymi) ma wysokosc wys i jest wysrodkowany na cy
    (napis w waskim pasie, np. PRZOD na wkladce). Z od -NADDATEK do relief. Zwraca liste bmesh (osobne wyspy)."""
    c, _k = metryka_fontu(P)
    c_wys = None
    if pelna:
        ys1 = [y for p in kontury_fontu(P, tresc, 1.0) for _, y in p]
        c_wys = max(ys1) - min(ys1)
    rozmiar, off, krok = parametry_tekstu(P, wys, c_wys)
    # weryfikacja: litera H z tym samym pogrubieniem
    ph = kontur_pogrubiony(kontury_fontu(P, 'H', rozmiar), off, krok)
    ysh = [y for p in ph for _, y in p]
    h = max(ysh) - min(ysh)
    trzon = min(szerokosci_trzonu(ph, min(ysh) + 0.3 * h))
    petle = kontur_pogrubiony(kontury_fontu(P, tresc, rozmiar), off, krok)
    xs = [x for p in petle for x, _ in p]
    dx = cx - (min(xs) + max(xs)) / 2
    if pelna:
        ys0 = [y for p in petle for _, y in p]
        dy = cy - (min(ys0) + max(ys0)) / 2
    else:
        dy = cy - (c * rozmiar) / 2       # linia bazowa w y = 0; wersalik od -off do c*rozmiar + off
    petle = [[(x + dx, y + dy) for x, y in p] for p in petle]
    xs = [x for p in petle for x, _ in p]
    ys = [y for p in petle for _, y in p]
    DZIENNIK['napisy'].append({
        'opis': opis, 'tresc': tresc, 'wys_zadana': wys, 'rozmiar_fontu': rozmiar, 'offset': off, 'krok': krok,
        'wys_H': h, 'trzon_H': trzon, 'szer': max(xs) - min(xs), 'y_min': min(ys), 'y_max': max(ys),
        'x_min': min(xs), 'x_max': max(xs), 'petle': len(petle)})
    return rozdziel_wyspy(bm_z_konturow(petle, -NADDATEK, relief))


def obrot_z(kat_st):
    return Matrix.Rotation(math.radians(kat_st), 4, 'Z')


# ===========================================================================
# (3) Czesci w ukladzie montazowym
# ===========================================================================

# ---- uklad gniazd (R13) ----

# R57: typy plytek. Okragle ('okragla_<typ>') maja ten sam uklad gniazd, rynienek i stozkow co kwadratowe tego samego typu bazowego.
TYPY_PLYTEK = ('wieczorna', 'poranna', 'okragla_wieczorna', 'okragla_poranna')
BITY = 'ABCD'            # R57: kod 4-bitowy n = A + 2B + 4C + 8D (D nie wystepuje na n1-n6)
# R58: plytki okragle do ramki (kieszenie magnesow, rowek pokrywki, rowek klucza); osobna krotka, zeby etapy A-C i --etap SPRAWDZ
# (petle po TYPY_PLYTEK) ich nie budowaly ani nie szukaly; buduje je tylko --etap R58
TYPY_PLYTEK_R58 = ('okragla_ramkowa_wieczorna', 'okragla_ramkowa_poranna')
NAROZA_CCW = 'DCBA'      # R58: kolejnosc narozy co cwierc obrotu od kierunku sciecia (D = round_flat_angle, C +90, B +180, A +270)


def typ_bazowy(typ):
    """'okragla_wieczorna' -> 'wieczorna' (uklad gniazd, znaczniki, rzedy D6 z tego samego typu bazowego). R58: 'okragla_ramkowa_<typ>' -> typ."""
    if typ not in TYPY_PLYTEK and typ not in TYPY_PLYTEK_R58:
        raise BladProjektu('nieznany typ plytki %s' % typ)
    return typ.replace('okragla_ramkowa_', '').replace('okragla_', '')


def plytka_okragla(typ):
    return typ.startswith('okragla_')


def plytka_ramkowa(typ):
    """R58: plytka okragla do ramki (kieszenie magnesow, rowek pokrywki, rowek klucza)."""
    return typ.startswith('okragla_ramkowa_')


def osie_okragle(P):
    """R58: osie cech kompletu okraglego na promieniu round_magnet_r: naroze -> (kat [deg], x, y). D = kierunek sciecia (round_flat_angle),
    C, B, A kolejno co cwierc obrotu przeciwnie do wskazowek zegara (jak narozniki kwadratu: A przod-lewy, B tyl-lewy, C tyl-prawy, D przod-prawy)."""
    rm, f0 = P['round_magnet_r'], float(P['round_flat_angle'])
    wyn = {}
    for i, c in enumerate(NAROZA_CCW):
        kat = f0 + 90.0 * i
        wyn[c] = (kat, rm * math.cos(math.radians(kat)), rm * math.sin(math.radians(kat)))
    return wyn


def pozycje_znacznikow(P, typ):
    """R54: srodki stozkow znacznikow per typ plytki (ev_marker_pos / mo_marker_pos), nie rogi. R57: okragla = typ bazowy."""
    baz = typ_bazowy(typ)
    poz = P['ev_marker_pos'] if baz == 'wieczorna' else P['mo_marker_pos']
    if sorted(poz) != ['A', 'B', 'C']:
        raise BladProjektu('%s_marker_pos: oczekiwane klucze A, B, C' % ('ev' if baz == 'wieczorna' else 'mo'))
    return {c: (float(poz[c][0]), float(poz[c][1])) for c in 'ABC'}


def sciecie_okraglej(P):
    """R57: sciecie orientacyjne plytki okraglej: cieciwa round_flat_w na kierunku round_flat_angle (od +X, stopnie; -45 = przod-prawo, jak dawny narożnik D).
    Zwraca (promien plytki, odleglosc cieciwy od srodka, kat, cieciwa)."""
    R = P['plate_round_d'] / 2
    w = P['round_flat_w']
    if not (0 < w < 2 * R):
        raise BladProjektu('round_flat_w %g poza (0, %g)' % (w, 2 * R))
    return R, math.sqrt(R * R - (w / 2) ** 2), float(P['round_flat_angle']), w


def dolki_kodu(P, typ):
    """R57: pozycje dolkow kodu per typ. Kwadrat: kolumna x = code_dimple_x, y = y0 + i*pitch (A, B, C) + bit D z code_bit_d_pos.
    Okragla: code_dimples_round[typ bazowy][bit] (wewnatrz kola, K-62)."""
    if plytka_okragla(typ):
        poz = P['code_dimples_round'].get(typ_bazowy(typ))
        if poz is None or sorted(poz) != sorted(BITY):
            raise BladProjektu('code_dimples_round[%s]: oczekiwane klucze %s' % (typ_bazowy(typ), ', '.join(BITY)))
        xy = {c: (float(poz[c][0]), float(poz[c][1])) for c in BITY}
    else:
        xy = {c: (P['code_dimple_x'], P['code_dimple_y0'] + i * P['code_dimple_pitch']) for i, c in enumerate('ABC')}
        xy['D'] = (float(P['code_bit_d_pos'][0]), float(P['code_bit_d_pos'][1]))
    return [{'bit': c, 'x': xy[c][0], 'y': xy[c][1], 'd': P['code_dimple_d'], 'depth': P['code_dimple_depth']} for c in BITY]


def uklad_pochodne(P, typ):
    """Pola JSON ukladu wynikajace z parametrow (wszystko poza 'sockets' i 'leds').
    R54: 'markers' z ev_marker_pos / mo_marker_pos (zaleznie od typu), 'magnet_pockets' nadal z marker_offset (rogi).
    R57: 'shape' square/round; okragla: 'd', 'flat' (sciecie), dolki z code_dimples_round, bez wyciecia D, bez kieszeni magnesow,
    cyfra z number_pos_round (null = pominieta); kwadrat: 4. dolek D (code_bit_d_pos)."""
    zn = pozycje_znacznikow(P, typ)
    wspolne = {
        'thickness': P['plate_thickness'],
        'markers': [{'corner': c, 'x': zn[c][0], 'y': zn[c][1], 'd': P['marker_cone_d'], 'depth': P['marker_cone_depth']} for c in 'ABC'],
        'code_dimples': dolki_kodu(P, typ),
    }
    if plytka_okragla(typ):
        R, dist, kat, w = sciecie_okraglej(P)
        npos = P['number_pos_round'].get(typ_bazowy(typ))
        wspolne.update({
            'shape': 'round', 'size': 2 * R, 'd': 2 * R,
            'flat': {'corner': 'D', 'angle_deg': kat, 'chord_w': w, 'dist': round(dist, 4),
                     'opis': 'ścięcie pionowe na całej grubości: płaszczyzna prostopadła do kierunku angle_deg (od +X), w odległości dist od środka'},
            'magnet_pockets': [],
            'number_relief': None if npos is None else {'x': float(npos[0]), 'y': float(npos[1]), 'text_h': P['number_text_h'], 'relief_h': P['number_relief_h']},
        })
        if plytka_ramkowa(typ):
            # R58: kieszenie magnesow A/B/C od spodu w osiach na promieniu round_magnet_r, rowek pokrywki na calym obwodzie, rowek klucza od spodu
            osie = osie_okragle(P)
            wspolne.update({
                'magnet_pockets': [{'corner': c, 'angle_deg': osie[c][0], 'x': round(osie[c][1], 4), 'y': round(osie[c][2], 4),
                                    'd': P['magnet_pocket_d'], 'depth': P['magnet_pocket_depth']} for c in 'ABC'],
                'cover_groove': {'z': P['cover_groove_z'], 'w': P['cover_groove_w'], 'depth': P['cover_groove_depth'],
                                 'opis': 'rowek na całym obwodzie (także przez ścięcie): od walca R do R − depth, środek z pod wierzchem, wysokość w'},
                'key_slot': {'angle_deg': osie['D'][0], 'r0': P['round_key_slot_r0'], 'w': P['round_key_slot_w'], 'h': P['round_key_slot_h'],
                             'opis': 'rowek klucza od spodu: szerokość w, oś na kierunku angle_deg, od promienia r0 na zewnątrz przez krawędź, wysokość h od spodu'},
            })
        return wspolne
    S = P['plate_size']
    h = S / 2
    m = P['marker_offset']
    rogi = {'A': (-(h - m), -(h - m)), 'B': (-(h - m), h - m), 'C': (h - m, h - m)}
    n = P['notch_size']
    wspolne.update({
        'shape': 'square', 'size': S,
        'notch': {'corner': 'D', 'x_min': h - n, 'x_max': h, 'y_min': -h, 'y_max': -(h - n)},
        'magnet_pockets': [{'corner': c, 'x': rogi[c][0], 'y': rogi[c][1], 'd': P['magnet_pocket_d'], 'depth': P['magnet_pocket_depth']} for c in 'ABC'],
        'number_relief': {'x': P['number_pos_x'], 'y': P['number_pos_y'], 'text_h': P['number_text_h'], 'relief_h': P['number_relief_h']},
    })
    return wspolne


def numery_plytek(P, typ):
    """Numery wariantow danego typu: kwadrat z plate_numbers_ev/mo, okragla z plate_numbers_round[typ bazowy] (R57),
    okragla ramkowa z plate_numbers_round_frame[typ bazowy] (R58)."""
    if plytka_ramkowa(typ):
        return list(P['plate_numbers_round_frame'][typ_bazowy(typ)])
    if plytka_okragla(typ):
        return list(P['plate_numbers_round'][typ_bazowy(typ)])
    return list(P['plate_numbers_ev'] if typ == 'wieczorna' else P['plate_numbers_mo'])


def generuj_gniazda(P, typ):
    """Gniazda z D6 (ev_rows / mo_rows): id rzedami od przodu, w rzedzie od prawej (R13). R57: okragla z rzedow typu bazowego.
    R59: rzad mieszany (dwie srednice obok siebie) = dwa wpisy o roznym y; id ida po y wpisu (sortowanie po y), potem od prawej."""
    typ = typ_bazowy(typ)
    wiersze = sorted(P['ev_rows'] if typ == 'wieczorna' else P['mo_rows'], key=lambda r: r['y'])
    pitch = P['ev_trough_hole_pitch'] if typ == 'wieczorna' else P['mo_trough_hole_pitch']
    t = math.tan(math.radians(P['socket_wall_angle']))
    gniazda = []
    nr = 1
    for w in wiersze:
        for x in sorted(w['x'], reverse=True):
            if w['type'] == 'round':
                gniazda.append({'id': nr, 'type': 'round', 'x': x, 'y': w['y'], 'd_top': w['d'],
                                'd_bottom': round(w['d'] - 2 * P['socket_depth'] * t, 2),
                                'depth': P['socket_depth'], 'hole_d': P['socket_hole_d']})
            else:
                gniazda.append({'id': nr, 'type': 'trough', 'x': x, 'y': w['y'], 'l': w['l'], 'w': w['w'], 'angle': 0,
                                'depth': P['socket_depth'], 'hole_d': P['socket_hole_d'],
                                'hole_pitch': pitch, 'hole_count': P['trough_hole_count']})
            nr += 1
    return gniazda


def wczytaj_uklad(P, typ, katalog_json, zapisuj=True, opis_odczytu='SPRAWDZ'):
    """Czyta json/uklad_gniazd_<typ>.json (zrodlo prawdy gniazd); tworzy go z D6, gdy nie istnieje.
    Pola wynikajace z parametrow sa aktualizowane z parametry.json. zapisuj=False (--etap SPRAWDZ): tylko odczyt.
    R58: --etap R58 czyta uklady kwadratowe i okragle tylko do porownan (zapisuj=False, opis_odczytu w dzienniku)."""
    sciezka = os.path.join(katalog_json, 'uklad_gniazd_%s.json' % typ)
    pochodne = uklad_pochodne(P, typ)
    if not zapisuj:
        if not os.path.exists(sciezka):
            raise BladProjektu('SPRAWDZ: brak pliku %s' % sciezka)
        with open(sciezka, encoding='utf-8') as f:
            uklad = json.load(f)
        zmiany = [k for k, v in pochodne.items() if uklad.get(k) != v]
        DZIENNIK['uklad'].append('%s: tylko odczyt (%s)%s' % (os.path.basename(sciezka), opis_odczytu,
                                 '; pola %s różnią się od parametry.json — przebieg budujący je zaktualizuje' % zmiany if zmiany else ', zgodny z parametry.json'))
        return uklad, sciezka
    os.makedirs(katalog_json, exist_ok=True)
    if os.path.exists(sciezka):
        with open(sciezka, encoding='utf-8') as f:
            uklad = json.load(f)
        zmiany = [k for k, v in pochodne.items() if uklad.get(k) != v]
        if zmiany:
            uklad.update(pochodne)
            DZIENNIK['uklad'].append('%s: pola %s zaktualizowane z parametry.json' % (os.path.basename(sciezka), zmiany))
            zapisz = True
        else:
            DZIENNIK['uklad'].append('%s: istnial, wczytany bez zmian' % os.path.basename(sciezka))
            zapisz = False
    else:
        uklad = {'plate': typ, 'version': P['file_suffix'], 'units': 'mm',
                 'coords': {'origin': 'środek górnej powierzchni płytki', 'x': 'w prawo (od użytkownika)', 'y': 'do tyłu'}}
        if plytka_okragla(typ):
            uklad['coords']['flat'] = 'ścięcie orientacyjne na kierunku %g° od +X (przód-prawo, jak dawny narożnik D); patrz pole flat' % P['round_flat_angle']
        else:
            uklad['coords']['notch_corner'] = 'D = (+48, -48), przód-prawy'
        uklad.update(pochodne)
        uklad['sockets'] = generuj_gniazda(P, typ)
        uklad['leds'] = {}
        DZIENNIK['uklad'].append('%s: utworzony z D6 (ev_rows/mo_rows)' % os.path.basename(sciezka))
        zapisz = True
    if zapisz:
        with open(sciezka, 'w', encoding='utf-8') as f:
            json.dump(uklad, f, ensure_ascii=False, indent=1)
    return uklad, sciezka


def bity(n):
    """R57: kod 4-bitowy n = A + 2B + 4C + 8D. None (plik bazowy) = wszystkie bity."""
    if n is None:
        return {c: True for c in BITY}
    return {'A': bool(n & 1), 'B': bool(n & 2), 'C': bool(n & 4), 'D': bool(n & 8)}


def bity_tekst(n):
    return '+'.join(c for c in BITY if bity(n)[c])


# ---- plytka ----

def zbuduj_plytke(P, uklad, numer, nazwa):
    """Plytka w ukladzie lokalnym: wierzch Z = 0, spod Z = -T. numer None = plik bazowy (wszystkie dolki, bez cyfry).
    R57: uklad['shape'] == 'round' -> walec o plate_round_d z faza plate_top_chamfer, sciecie orientacyjne (flat),
    bez wyciecia D, bez kieszeni magnesow, bez rowka pokrywki; gniazda, rynienki, stozki znacznikow jak kwadrat.
    R58: okragla ramkowa (JSON z polami cover_groove, key_slot i 3 kieszeniami magnet_pockets) - ta sama bryla co okragla plus
    kieszenie magnesow od spodu, rowek pokrywki na calym obwodzie i rowek klucza od spodu; bryly dopisane na koncu listy tnacej,
    wiec plytki okragle R57/R59 (bez tych pol) buduja sie bez zmian."""
    okragla = uklad.get('shape') == 'round'
    S, T = P['plate_size'], P['plate_thickness']
    r, f = P['plate_edge_r'], P['plate_top_chamfer']
    nl = seg_luku(r, math.pi / 2)
    if okragla:
        R = uklad['d'] / 2
        n_ok = seg_okregu(R)
        baza = bm_z_pierscieni([(okrag(R, n=n_ok), -T), (okrag(R, n=n_ok), -f), (okrag(R - f, n=n_ok), 0.0)])
    else:
        baza = bm_z_pierscieni([
            (prostokat_zaokr(S, S, r, n_luk=nl), -T),
            (prostokat_zaokr(S, S, r, n_luk=nl), -f),
            (prostokat_zaokr(S - 2 * f, S - 2 * f, r - f, n_luk=nl), 0.0)])
    dodatnie, tnace, otwory = [], [], []        # otwory: o3 osobno tylko dla okraglej (R57); kwadrat trzyma je w tnace w dawnej kolejnosci
    # relief numeru (tylko warianty; okragla: number_relief None = cyfra pominieta)
    if numer is not None and uklad['number_relief'] is not None:
        nr = uklad['number_relief']
        dodatnie += bryly_tekstu(P, str(numer), nr['text_h'], nr['relief_h'], nr['x'], nr['y'], 'cyfra n%d' % numer)
    t_kat = math.tan(math.radians(P['socket_wall_angle']))
    for g in uklad['sockets']:
        dep = g['depth']
        if g['type'] == 'round':
            r0, r1 = g['d_top'] / 2, g['d_bottom'] / 2
            nach = (r0 - r1) / dep
            n = seg_okregu(r0)
            tnace.append(bm_z_pierscieni([(okrag(r1, g['x'], g['y'], n), -dep),
                                           (okrag(r0 + nach * NADDATEK, g['x'], g['y'], n), NADDATEK)]))
            (otwory if okragla else tnace).append(bm_walec(g['hole_d'] / 2, -T - NADDATEK, -dep + NADDATEK, g['x'], g['y']))
        elif g['type'] == 'trough':
            n_pol = max(16, int(math.ceil(math.pi * (g['w'] / 2) / DL_CIECIWY)))
            tnace.append(bm_z_pierscieni([
                (stadion(g['l'], g['w'], g['x'], g['y'], g['angle'], n_pol, -dep * t_kat), -dep),
                (stadion(g['l'], g['w'], g['x'], g['y'], g['angle'], n_pol, NADDATEK * t_kat), NADDATEK)]))
            c, s = math.cos(math.radians(g['angle'])), math.sin(math.radians(g['angle']))
            for i in range(g['hole_count']):
                k = i - (g['hole_count'] - 1) / 2
                (otwory if okragla else tnace).append(bm_walec(g['hole_d'] / 2, -T - NADDATEK, -dep + NADDATEK,
                                                               g['x'] + k * g['hole_pitch'] * c, g['y'] + k * g['hole_pitch'] * s))
        else:
            raise BladProjektu('nieznany typ gniazda %s' % g['type'])
    for m in uklad['markers']:
        rr = m['d'] / 2
        tnace.append(bm_z_pierscieni([(okrag(rr * (1 + NADDATEK / m['depth']), m['x'], m['y']), NADDATEK),
                                       ([(m['x'], m['y'])], -m['depth'])]))
    if okragla:
        # sciecie orientacyjne (R57): polprzestrzen za cieciwa, w ukladzie lokalnym (u wzdluz kierunku angle_deg), obrocona o kat
        fl = uklad['flat']
        R = uklad['d'] / 2
        box = bm_prostopadloscian(fl['dist'], R + NADDATEK, -(R + NADDATEK), R + NADDATEK, -T - NADDATEK, NADDATEK)
        tnace.append(bm_transformuj(box, obrot_z(fl['angle_deg'])))
    else:
        nt = uklad['notch']
        tnace.append(bm_prostopadloscian(nt['x_min'], nt['x_max'] + NADDATEK, nt['y_min'] - NADDATEK, nt['y_max'],
                                         -T - NADDATEK, NADDATEK))
    b = bity(numer)
    for dl in uklad['code_dimples']:
        if b[dl['bit']]:
            tnace.append(bm_walec(dl['d'] / 2, -dl['depth'], NADDATEK, dl['x'], dl['y']))
    for mp in uklad['magnet_pockets']:          # okragla: lista pusta (R57, bez kieszeni magnesow)
        tnace.append(bm_walec(mp['d'] / 2, -T - NADDATEK, -T + mp['depth'], mp['x'], mp['y']))
    if not okragla:
        # rowek pokrywki wokol 4 bokow (przerywa go wyciecie D); okragla bez rowka (R57)
        gd, gw, gz = P['cover_groove_depth'], P['cover_groove_w'], P['cover_groove_z']
        tnace.append(bm_pierscien(prostokat_zaokr(S + 2 * NADDATEK, S + 2 * NADDATEK, r + NADDATEK, n_luk=nl),
                                  prostokat_zaokr(S - 2 * gd, S - 2 * gd, r - gd, n_luk=nl),
                                  -gz - gw / 2, -gz + gw / 2))
    if okragla and uklad.get('cover_groove'):
        # R58: rowek pokrywki na calym obwodzie (tez przez sciecie: w srodku cieciwy zostaje dist - (R - depth)); pierscien tnacy
        # od R + 2*NADDATEK (nie w plaszczyznie konca bryly sciecia R + NADDATEK) do R - depth, te same katy wierzcholkow co walec
        cg = uklad['cover_groove']
        R = uklad['d'] / 2
        n_ok = seg_okregu(R)
        tnace.append(bm_pierscien(okrag(R + 2 * NADDATEK, n=n_ok), okrag(R - cg['depth'], n=n_ok), -cg['z'] - cg['w'] / 2, -cg['z'] + cg['w'] / 2))
    if okragla and uklad.get('key_slot'):
        # R58: rowek klucza od spodu: u (wzdluz angle_deg) od r0 na zewnatrz poza krawedz, v +-w/2, Z od spodu do -T + h;
        # konce poza plytka odsuniete od plaszczyzn bryly sciecia (R + 3*NADDATEK, -T - 2*NADDATEK)
        ks = uklad['key_slot']
        R = uklad['d'] / 2
        box = bm_prostopadloscian(ks['r0'], R + 3 * NADDATEK, -ks['w'] / 2, ks['w'] / 2, -T - 2 * NADDATEK, -T + ks['h'])
        tnace.append(bm_transformuj(box, obrot_z(ks['angle_deg'])))
    if okragla:
        ob = zbuduj_z_operacji(nazwa, baza, dodatnie, tnace, tnace_po=otwory)     # R57: otwory o3 w drugiej roznicy
    else:
        ob = zbuduj_z_operacji(nazwa, baza, dodatnie, tnace)                      # kwadrat: jak dotad (jedna roznica, ta sama kolejnosc bryl; otwory w tnace)
    if okragla:
        # R57: wielokaty wierzchu i spodu po booleanie (setki wierzcholkow, wklesle, z otworami polaczonymi przecieciami) tesseluja sie
        # w Blenderze blednie dla plytki okraglej (trojkaty wchodzace w otwory -> K-03 przeciecia); triangulacja Delaunaya z ograniczeniami
        # (mathutils.geometry.delaunay_2d_cdt) na tych samych wierzcholkach - geometria bez zmian. Tylko okragle (pliki kwadratowe bez zmian bajtow).
        triangulacja_cdt(ob)
    return ob


def triangulacja_cdt(ob, min_wierzcholkow=16, tol_z=1e-5):
    """Odbudowuje poziome sciany (|n_z| > 0,999) plytki: dla kazdej plaszczyzny Z zbiera krawedzie brzegowe grupy scian
    (krawedz nalezaca do jednej sciany grupy; krawedzie laczace otwory z obrysem naleza do dwoch i znikaja), sklada z nich petle
    (obrys + otwory) i trianguluje je Delaunayem z ograniczeniami z otworami (mathutils.geometry.delaunay_2d_cdt, tryb 4).
    Wierzcholki bez zmian (sprawdzane), pole grupy zachowane (sprawdzane), normalne odtworzone. Grupy bez duzych scian pomijane."""
    from mathutils.geometry import delaunay_2d_cdt
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.faces.ensure_lookup_table()
    grupy = {}
    for f in bm.faces:
        if abs(f.normal.z) > 0.999:
            z = f.verts[0].co.z
            if all(abs(v.co.z - z) <= tol_z for v in f.verts):
                grupy.setdefault((round(z, 4), f.normal.z > 0), []).append(f)
    odbudowane = 0
    for (z, w_gore), sciany in grupy.items():
        if max(len(f.verts) for f in sciany) < min_wierzcholkow:
            continue
        uzycie = {}
        for f in sciany:
            for e in f.edges:
                uzycie[e] = uzycie.get(e, 0) + 1
        brzeg = [e for e, n in uzycie.items() if n == 1]
        sasiedzi = {}
        for e in brzeg:
            a, b = e.verts
            sasiedzi.setdefault(a, []).append(b)
            sasiedzi.setdefault(b, []).append(a)
        if any(len(l) != 2 for l in sasiedzi.values()):
            raise BladProjektu('%s: brzeg plaszczyzny Z %g nie sklada sie z petli' % (ob.name, z))
        petle, odwiedzone = [], set()
        for start in sasiedzi:
            if start in odwiedzone:
                continue
            petla, prev, cur = [start], None, start
            while True:
                odwiedzone.add(cur)
                nxt = [n for n in sasiedzi[cur] if n is not prev]
                nxt = nxt[0] if prev is None else (nxt[0] if nxt else None)
                if nxt is None or nxt is start:
                    break
                petla.append(nxt)
                prev, cur = cur, nxt
            petle.append(petla)
        wierz = [v for petla in petle for v in petla]
        if len(set(wierz)) != len(wierz):
            raise BladProjektu('%s: petle plaszczyzny Z %g dziela wierzcholek' % (ob.name, z))
        pts = [Vector((v.co.x, v.co.y)) for v in wierz]
        idx, k = [], 0
        for petla in petle:
            idx.append(list(range(k, k + len(petla))))
            k += len(petla)
        # tryb 1 (CDT_INSIDE) trianguluje wnetrze wszystkich petli (otwory tez); trojkaty w otworach odrzucane regula parzystosci:
        # srodek trojkata lezy wewnatrz nieparzystej liczby petli = material
        wyn = delaunay_2d_cdt(pts, [], idx, 1, 1e-7, True)
        w_out, f_out, orig_v = wyn[0], wyn[2], wyn[3]
        if len(w_out) != len(pts) or any(len(ov) != 1 for ov in orig_v):
            raise BladProjektu('%s: CDT (Z %g) dodal/scalil wierzcholki (%d -> %d)' % (ob.name, z, len(pts), len(w_out)))
        mapa = {i: wierz[ov[0]] for i, ov in enumerate(orig_v)}
        if any(len(t) != 3 for t in f_out):
            raise BladProjektu('%s: CDT (Z %g) zwrocil nie-trojkat' % (ob.name, z))
        petle2d = []
        for petla in petle:
            xy = [(v.co.x, v.co.y) for v in petla]
            petle2d.append((xy, min(x for x, _ in xy), max(x for x, _ in xy), min(y for _, y in xy), max(y for _, y in xy)))

        def w_petli(px, py, xy):
            wewn = False
            n = len(xy)
            for i in range(n):
                x0, y0 = xy[i]
                x1, y1 = xy[(i + 1) % n]
                if (y0 > py) != (y1 > py):
                    xs = x0 + (py - y0) * (x1 - x0) / (y1 - y0)
                    if px < xs:
                        wewn = not wewn
            return wewn
        pole_s = sum(f.calc_area() for f in sciany)
        pole_t = 0.0
        trojkaty = []
        for t in f_out:
            p0, p1, p2 = (mapa[i].co for i in t)
            cx, cy = (p0.x + p1.x + p2.x) / 3, (p0.y + p1.y + p2.y) / 3
            licz = sum(1 for xy, x0, x1, y0, y1 in petle2d if x0 <= cx <= x1 and y0 <= cy <= y1 and w_petli(cx, cy, xy))
            if licz % 2 == 0:
                continue
            pole_t += (p1 - p0).cross(p2 - p0).length / 2
            trojkaty.append(tuple(mapa[i] for i in t))
        if abs(pole_t - pole_s) > 1e-4 * max(pole_s, 1.0):
            raise BladProjektu('%s: CDT (Z %g) pole %.5f vs sciany %.5f' % (ob.name, z, pole_t, pole_s))
        bmesh.ops.delete(bm, geom=sciany, context='FACES_ONLY')
        for tr in trojkaty:
            try:
                bm.faces.new(tr)
            except ValueError:
                raise BladProjektu('%s: CDT (Z %g) zdublowany trojkat' % (ob.name, z))
        odbudowane += 1
        log('%s: plaszczyzna Z %g: %d scian (%d petli, %d wierzcholkow) -> %d trojkatow CDT, pole %.3f' % (ob.name, z, len(sciany), len(petle), len(wierz), len(trojkaty), pole_t))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.validate(verbose=False)
    ob.data.update()
    log('%s: triangulacja CDT %d plaszczyzn' % (ob.name, odbudowane))


# ---- pokrywka ----

def wymiary_pokrywki(P):
    wew = P['plate_size'] + 2 * P['cover_clearance']
    zew = wew + 2 * P['cover_skirt_t']
    wys = P['cover_inner_h'] + P['cover_top_t'] + P['cover_skirt_below']
    return wew, zew, wys


def polozenia_garbow(P):
    """(kat obrotu boku, przesuniecie wzdluz boku): prawy 0, tyl 90, lewy 180, przod 270 (R42)."""
    fx = P['cover_snap_front_x']
    return [(0.0, 0.0), (90.0, fx), (180.0, 0.0), (270.0, fx)]


def zbuduj_pokrywke(P, nazwa):
    """Uklad pokrywki: wierzch zewnetrzny Z = 0, kolnierz w dol do -wys, srodek XY."""
    wew, zew, wys = wymiary_pokrywki(P)
    r = P['cover_corner_r']
    rw = r - P['cover_skirt_t']
    nl = seg_luku(r, math.pi / 2)
    baza = bm_skorupa(prostokat_zaokr(zew, zew, r, n_luk=nl), prostokat_zaokr(wew, wew, rw, n_luk=nl),
                      -wys, 0.0, -P['cover_top_t'])
    dodatnie, tnace = [], []
    # garby zatrzaskowe: przekroj (a = wysiegniecie do srodka od lica kolnierza, b = Z), wyciagniety wzdluz boku
    wy, hg = P['cover_snap_bump'], P['cover_snap_hgt']
    rt = min(P['cover_snap_r'], hg / 2)
    if rt < P['cover_snap_r']:
        DZIENNIK['odstepstwa'].append((
            '4.2 / cover_snap_r', 'zaokrąglenie czubka garbu %.2f zamiast %.2f' % (rt, P['cover_snap_r']),
            'garb ma %.2f wysokości w Z; dwa naroża czubka R %.2f nie mieszczą się (2·R > wysokość), czubek jest pełnym półokręgiem' % (hg, P['cover_snap_r']),
            'nie (geometrycznie wymuszone; informacyjnie)'))
    przekroj = [(-NADDATEK, -hg / 2)]
    nl_g = seg_luku(rt, math.pi / 2)
    for i in range(nl_g + 1):
        a = math.radians(-90 + 90 * i / nl_g)
        przekroj.append((wy - rt + rt * math.cos(a), -hg / 2 + rt + rt * math.sin(a)))
    for i in range(nl_g + 1):
        a = math.radians(0 + 90 * i / nl_g)
        p = (wy - rt + rt * math.cos(a), hg / 2 - rt + rt * math.sin(a))
        if (p[0] - przekroj[-1][0]) ** 2 + (p[1] - przekroj[-1][1]) ** 2 > 1e-12:
            przekroj.append(p)
    przekroj.append((-NADDATEK, hg / 2))
    # orientacja CCW w ukladzie (a, b)
    pole = sum(przekroj[i][0] * przekroj[(i + 1) % len(przekroj)][1] - przekroj[(i + 1) % len(przekroj)][0] * przekroj[i][1] for i in range(len(przekroj)))
    if pole < 0:
        przekroj.reverse()
    for kat, wzdluz in polozenia_garbow(P):
        # lokalnie: a -> -X (do srodka od prawego boku), b -> +Z, c -> +Y; potem obrot o kat wokol Z
        M = Matrix(((-1, 0, 0, wew / 2), (0, 0, 1, wzdluz), (0, 1, 0, P['cover_snap_z']), (0, 0, 0, 1)))
        M = obrot_z(kat) @ M
        dodatnie.append(bm_profil_wyciagniety(przekroj, -P['cover_snap_w'] / 2, P['cover_snap_w'] / 2, M))
    # wierzch pelny: bez otworow (R50-U17) i bez napisu GORA (R50-U14)
    # wyciecia palcowe na dolnej krawedzi przodu i tylu
    fw, fh = P['cover_finger_w'], P['cover_finger_h']
    for zn in (-1, 1):
        y0, y1 = sorted((zn * (zew / 2 + NADDATEK), zn * (wew / 2 - NADDATEK)))
        tnace.append(bm_prostopadloscian(-fw / 2, fw / 2, y0, y1, -wys - NADDATEK, -wys + fh))
    return zbuduj_z_operacji(nazwa, baza, dodatnie, tnace)


# ---- pokrywka okragla (R58): uklad jak pokrywka - wierzch zewnetrzny Z = 0, kolnierz w dol, srodek XY ----

def wymiary_pokrywki_okraglej(P):
    """R58: (promien wewnetrzny, promien zewnetrzny, wysokosc) kubka: plate_round_d + 2*cover_clearance, scianka cover_skirt_t."""
    rw = P['plate_round_d'] / 2 + P['cover_clearance']
    rz = rw + P['cover_skirt_t']
    wys = P['cover_inner_h'] + P['cover_top_t'] + P['cover_skirt_below']
    return rw, rz, wys


def przekroj_garbu(P):
    """Przekroj garbu zatrzaskowego (a = wysiegniecie do srodka od lica kolnierza, b = Z wzgledem srodka garbu), CCW.
    Ta sama konstrukcja co w zbuduj_pokrywke (R47: czubek polokrag cover_snap_hgt/2); zbuduj_pokrywke bez zmian (plik R59)."""
    wy, hg = P['cover_snap_bump'], P['cover_snap_hgt']
    rt = min(P['cover_snap_r'], hg / 2)
    przekroj = [(-NADDATEK, -hg / 2)]
    nl_g = seg_luku(rt, math.pi / 2)
    for i in range(nl_g + 1):
        a = math.radians(-90 + 90 * i / nl_g)
        przekroj.append((wy - rt + rt * math.cos(a), -hg / 2 + rt + rt * math.sin(a)))
    for i in range(nl_g + 1):
        a = math.radians(0 + 90 * i / nl_g)
        p = (wy - rt + rt * math.cos(a), hg / 2 - rt + rt * math.sin(a))
        if (p[0] - przekroj[-1][0]) ** 2 + (p[1] - przekroj[-1][1]) ** 2 > 1e-12:
            przekroj.append(p)
    przekroj.append((-NADDATEK, hg / 2))
    pole = sum(przekroj[i][0] * przekroj[(i + 1) % len(przekroj)][1] - przekroj[(i + 1) % len(przekroj)][0] * przekroj[i][1] for i in range(len(przekroj)))
    if pole < 0:
        przekroj.reverse()
    return przekroj, rt


def bm_profil_po_luku(przekroj, r_lica, kat_st, dl_luku, z_srodka):
    """R58: przekroj (a, b) wyciagniety po luku o stalym przekroju: punkt (a, b) -> promien r_lica - a, Z z_srodka + b;
    luk o dlugosci dl_luku mierzonej po licu r_lica, srodek na kacie kat_st (od +X). Sciany boczne + dwa denka."""
    d_kat = dl_luku / r_lica
    n = seg_luku(r_lica, d_kat)
    bm = bmesh.new()
    pierscienie = []
    for k in range(n + 1):
        t = math.radians(kat_st) - d_kat / 2 + d_kat * k / n
        c, s = math.cos(t), math.sin(t)
        pierscienie.append([bm.verts.new(((r_lica - a) * c, (r_lica - a) * s, z_srodka + b)) for a, b in przekroj])
    m = len(przekroj)
    for p0, p1 in zip(pierscienie, pierscienie[1:]):
        for i in range(m):
            j = (i + 1) % m
            bm.faces.new((p0[i], p0[j], p1[j], p1[i]))
    bm.faces.new(list(reversed(pierscienie[0])))
    bm.faces.new(pierscienie[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


def zbuduj_pokrywke_okragla(P, nazwa):
    """R58 (4.2a): kubek o srednicy wewnetrznej plate_round_d + 2*cover_clearance, scianka cover_skirt_t, wysokosc jak pokrywka
    kwadratowa, wierzch pelny cover_top_t; 4 garby (przekroj jak kwadratowa) wyciagniete po luku cover_snap_w na katach
    round_cover_snap_angles, srodek Z cover_snap_z; wyciecia palcowe cover_finger_w x cover_finger_h z przodu i z tylu."""
    rw, rz, wys = wymiary_pokrywki_okraglej(P)
    n = seg_okregu(rz)
    baza = bm_skorupa(okrag(rz, n=n), okrag(rw, n=n), -wys, 0.0, -P['cover_top_t'])
    przekroj, _rt = przekroj_garbu(P)
    dodatnie = [bm_profil_po_luku(przekroj, rw, float(kat), P['cover_snap_w'], P['cover_snap_z']) for kat in P['round_cover_snap_angles']]
    tnace = []
    fw, fh = P['cover_finger_w'], P['cover_finger_h']
    if fw / 2 >= rw:
        raise BladProjektu('cover_finger_w %g >= srednica wewnetrzna pokrywki okraglej %g' % (fw, 2 * rw))
    y_wew = math.sqrt(rw * rw - (fw / 2) ** 2) - NADDATEK          # wyciecie siega za lico wewnetrzne na calej szerokosci
    for zn in (-1, 1):
        y0, y1 = sorted((zn * (rz + NADDATEK), zn * y_wew))
        tnace.append(bm_prostopadloscian(-fw / 2, fw / 2, y0, y1, -wys - NADDATEK, -wys + fh))
    # R58 runda 2 (P2 recenzji): pionowe szczeliny odciazajace przez scianke po obu stronach kazdego garbu (garb na jezyku);
    # srodek szczeliny round_cover_slit_offset po licu wewnetrznym od srodka garbu, szerokosc stala (bryla rownolegloscienna wzdluz promienia).
    # Runda 3 (P2 recenzji rundy 2): szczelina round_cover_slit_h od dolnej krawedzi, na gornym koncu otwor przelotowy o round_cover_slit_end_d
    # (walec wzdluz promienia, srodek na osi szczeliny na Z -wys + round_cover_slit_h) - zaokraglony koniec zamiast ostrego naroza
    sw, sl, dk = P['round_cover_slit_w'], P['round_cover_slit_h'], P['round_cover_slit_end_d']
    z_k = -wys + sl
    if not (dk >= sw and z_k + dk / 2 < -P['cover_top_t'] and z_k - dk / 2 > -wys):
        raise BladProjektu('szczeliny pokrywki okraglej: otwor koncowy o%g na Z %.2f poza zakresem (szczelina %g, spod wierzchu Z %g, dol Z %g)'
                           % (dk, z_k, sw, -P['cover_top_t'], -wys))
    for kat, zn in polozenia_szczelin_pokrywki(P):
        box = bm_prostopadloscian(rw - 2 * NADDATEK, rz + 2 * NADDATEK, -sw / 2, sw / 2, -wys - 2 * NADDATEK, z_k)
        tnace.append(bm_transformuj(box, obrot_z(kat)))
        tnace.append(bm_transformuj(bm_stozek_os('X', dk / 2, dk / 2, rw - 2 * NADDATEK, rz + 2 * NADDATEK, (0.0, 0.0, z_k)), obrot_z(kat)))
    return zbuduj_z_operacji(nazwa, baza, dodatnie, tnace)


def polozenia_szczelin_pokrywki(P):
    """R58 runda 2: (kat srodka szczeliny [deg], strona -1/+1) - po dwie na garb, round_cover_slit_offset po licu wewnetrznym."""
    rw, _rz, _wys = wymiary_pokrywki_okraglej(P)
    d = math.degrees(P['round_cover_slit_offset'] / rw)
    return [(float(k) + zn * d, zn) for k in P['round_cover_snap_angles'] for zn in (-1, 1)]


# ===========================================================================
# (3b) Czesci etapu B: wkladka, rama dyfuzora, blat, korpus; bryly zastepcze
# ===========================================================================

def bm_transformuj(bm, M):
    bmesh.ops.transform(bm, matrix=M, verts=bm.verts[:])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


def M_os(os_, srodek):
    """Uklad lokalny (u, v, w) -> swiat; w = os bryly ('X', 'Y' albo 'Z'), srodek = punkt na osi."""
    cx, cy, cz = srodek
    if os_ == 'Z':
        return Matrix(((1, 0, 0, cx), (0, 1, 0, cy), (0, 0, 1, cz), (0, 0, 0, 1)))
    if os_ == 'Y':      # u -> X, v -> Z, w -> Y
        return Matrix(((1, 0, 0, cx), (0, 0, 1, cy), (0, 1, 0, cz), (0, 0, 0, 1)))
    if os_ == 'X':      # u -> Y, v -> Z, w -> X
        return Matrix(((0, 0, 1, cx), (1, 0, 0, cy), (0, 1, 0, cz), (0, 0, 0, 1)))
    raise BladProjektu('os %s' % os_)


def bm_stozek_os(os_, r0, r1, t0, t1, srodek):
    """Walec (r0 = r1) albo stozek sciety wzdluz osi, od t0 do t1 (wspolrzedna wzdluz osi)."""
    n = seg_okregu(max(r0, r1))
    return bm_transformuj(bm_z_pierscieni([(okrag(r0, n=n), t0), (okrag(r1, n=n), t1)]), M_os(os_, srodek))


def bm_profil_os(os_, pts, t0, t1, srodek):
    return bm_transformuj(bm_pryzmat(pts, t0, t1), M_os(os_, srodek))


def bm_belka(p0, p1, szer, z0, z1):
    """Prostopadloscian wzdluz odcinka p0-p1 (w XY), szerokosc szer, Z od z0 do z1."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    nx, ny = -dy / L * szer / 2, dx / L * szer / 2
    return bm_pryzmat([(p0[0] - nx, p0[1] - ny), (p1[0] - nx, p1[1] - ny), (p1[0] + nx, p1[1] + ny), (p0[0] + nx, p0[1] + ny)], z0, z1)


def bm_pierscien_poziomy(poziomy):
    """Pierscien o profilach zmiennych z wysokoscia: lista (zew, wew, z) od dolu, rowne liczby wierzcholkow."""
    bm = bmesh.new()
    Z = [[bm.verts.new((x, y, z)) for x, y in zew] for zew, _w, z in poziomy]
    Wn = [[bm.verts.new((x, y, z)) for x, y in wew] for _z, wew, z in poziomy]
    n = len(Z[0])
    for a, b in zip(Z, Z[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((a[i], a[j], b[j], b[i]))
    for a, b in zip(Wn, Wn[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((a[j], a[i], b[i], b[j]))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((Z[0][j], Z[0][i], Wn[0][i], Wn[0][j]))
        bm.faces.new((Z[-1][i], Z[-1][j], Wn[-1][j], Wn[-1][i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


def bm_polacz(lista):
    """Laczy kilka bmesh w jeden (bez booleana; do bryl zastepczych)."""
    bm = bmesh.new()
    for b in lista:
        me = bpy.data.meshes.new('tmp')
        b.to_mesh(me)
        b.free()
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
    return bm


def pozycje_scian(P):
    """(kat boku, polozenie wzdluz boku) dla kieszeni/haczykow R6: prawy 0, tylny 90, lewy 180, przedni 270.
    Lokalny kierunek wzdluz boku = obrot (0, 1) o kat."""
    return [(0.0, P['snap_side_y']), (90.0, -P['snap_rear_x']), (180.0, -P['snap_side_y']), (270.0, P['snap_front_x'])]


def M_sciana(kat, odl):
    """Lokalne (u = na zewnatrz od lica w odl., v = Z, c = wzdluz boku) -> swiat, bok obrocony o kat."""
    return obrot_z(kat) @ Matrix(((1, 0, 0, odl), (0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))


def bm_lokalny_box(u0, u1, v0, v1, c0, c1, M):
    """Prostopadloscian w ukladzie (u, v, c) sciany, przeksztalcony macierza M_sciana."""
    return bm_transformuj(bm_prostopadloscian(u0, u1, v0, v1, c0, c1), M)


# ---- wkladka (uklad: srodek otworu, spod ramy Z = 0) ----

def zbuduj_wkladke(P, nazwa):
    h = P['insert_opening'] / 2
    zw = h + P['insert_wall_w']
    H, sh, s, tt = P['insert_h'], P['insert_shelf_h'], P['insert_shelf'], P['tab_t']
    ro = P['insert_opening_r']           # R50-U15: 0 = naroza otworu ostre
    nl = seg_luku(ro, math.pi / 2) if ro > 0 else None
    ex_in, ex_out = P['tab_pos_x'] - P['tab_w'] / 2, P['tab_pos_x'] + P['tab_w'] / 2
    rxi, ry0, ry1, ty1 = P['tab_root_x_in'], P['tab_root_y0'], P['tab_root_y1'], P['tab_end_y']
    # obrys ramy + nasad + uszu (CCW)
    # nasada L (R51): czesc x (rxi...tab_root_x_out) od y ry0 lezy w obrysie ramy (zakladka ze scianka tylna);
    # czesc x (tab_root_x_out...ex_out) dopiero od tylnej krawedzi ramy, nic poza rama dla y < zw (K-56)
    rxo = P['tab_root_x_out']
    if rxo > zw + 1e-9 or ry0 > zw:
        raise BladProjektu('nasada ucha: tab_root_x_out %.2f > krawedz ramy %.2f albo tab_root_y0 > %.2f' % (rxo, zw, zw))
    prawa = [(zw, -zw), (zw, zw), (ex_out, zw), (ex_out, ty1), (ex_in, ty1), (ex_in, ry1), (rxi, ry1), (rxi, zw)]
    obrys = prawa + [(-x, y) for x, y in reversed(prawa)]
    q = h - s
    krzyz = [(-q, -h), (q, -h), (q, -q), (h, -q), (h, q), (q, q), (q, h), (-q, h), (-q, q), (-h, q), (-h, -q), (-q, -q)]
    otwor = prostokat_r(2 * h, 2 * h, ro, n_luk=nl)
    # baza: spod ramy, nasad i uszu z polkami (otwor bez narozy) do wysokosci polki
    baza = bm_z_konturow([obrys, krzyz], 0.0, sh)
    dodatnie = [bm_z_konturow([obrys, otwor], sh - NADDATEK, tt),
                bm_z_konturow([prostokat(2 * zw, 2 * zw), otwor], tt - NADDATEK, H)]
    # kolek orientacyjny na polce D (przod-prawy), faza wierzcholka
    op, oh, og, oc = P['orient_post'], P['orient_post_h'], P['orient_post_gap'], P['orient_post_chamfer']
    pc = h - og - op / 2
    dodatnie.append(bm_z_pierscieni([(prostokat(op, op, pc, -pc), sh - NADDATEK), (prostokat(op, op, pc, -pc), sh + oh - oc),
                                      (prostokat(op - 2 * oc, op - 2 * oc, pc, -pc), sh + oh)]))
    # kolki ustalajace pod uszami, faza na koncu
    rp, hp, cp = P['tab_pin_d'] / 2, P['tab_pin_h'], P['tab_pin_chamfer']
    n = seg_okregu(rp)
    for zx in (-1, 1):
        x, y = zx * P['tab_pos_x'], P['tab_pin_y']
        dodatnie.append(bm_z_pierscieni([(okrag(rp - cp, x, y, n), -hp), (okrag(rp, x, y, n), -hp + cp), (okrag(rp, x, y, n), NADDATEK)]))
    # napis PRZOD i strzalka na gornej powierzchni przedniego boku
    rel = P['label_relief_h']
    if P['insert_label_h'] > 0:          # R51: insert_label_h = 0 -> bez napisu, tylko strzalki
        for wyspa in bryly_tekstu(P, P['insert_label_text'], P['insert_label_h'], rel, P['insert_label_x'], P['insert_label_y'],
                                  'wkładka PRZÓD', pelna=True):
            dodatnie.append(bm_przesun(wyspa, (0, 0, H)))
    ay, al, aw = P['insert_label_y'], P['insert_arrow_l'], P['insert_arrow_w']
    for ax in P['insert_arrow_x']:
        dodatnie.append(bm_pryzmat([(ax - aw / 2, ay + al / 2), (ax, ay - al / 2), (ax + aw / 2, ay + al / 2)], H - NADDATEK, H + rel))
    tnace = []
    # faza 1 x 45 na gornej wewnetrznej krawedzi (pierscien tnacy, nie siega kolka ani polek)
    c = P['insert_chamfer']
    wew_f = prostokat_r(2 * h - 2 * NADDATEK, 2 * h - 2 * NADDATEK, ro - NADDATEK, n_luk=nl)
    zew_f = prostokat_r(2 * h + 2 * (c + NADDATEK), 2 * h + 2 * (c + NADDATEK), ro + c + NADDATEK if ro > 0 else 0.0, n_luk=nl)
    tnace.append(bm_pierscien_poziomy([(otwor, wew_f, H - c), (zew_f, wew_f, H + NADDATEK)]))
    # kieszenie Halla, kanaly pod polkami i przeloty w sciance (A, B, C)
    m = P['plate_size'] / 2 - P['marker_offset']
    hw, hl = P['hall_pocket_w'], P['hall_pocket_l']
    cw, chh, ph = P['hall_lead_channel_w'], P['hall_lead_channel_h'], P['hall_wall_pass_h']
    for sx, sy in ((-1, -1), (-1, 1), (1, 1)):
        px, py = sx * m, sy * m
        tnace.append(bm_prostopadloscian(px - hw / 2, px + hw / 2, py - hl / 2, py + hl / 2, -NADDATEK, sh + NADDATEK))
        # kanal (wys. chh) od kieszeni do naroza otworu i przelot w sciance (wys. ph) do naroza zewnetrznego:
        # jeden profil wzdluz przekatnej (dwie belki tej samej szerokosci mialyby wspolplaszczyznowe boki)
        d = Vector((sx, sy, 0)).normalized()
        t_h = (h - m) * math.sqrt(2)
        t_k = (zw - m) * math.sqrt(2) + 5 * NADDATEK
        profil = [(0.0, -NADDATEK), (t_k, -NADDATEK), (t_k, ph), (t_h, ph), (t_h, chh), (0.0, chh)]
        M = Matrix(((d.x, 0, -d.y, px), (d.y, 0, d.x, py), (0, 1, 0, 0), (0, 0, 0, 1)))
        tnace.append(bm_transformuj(bm_pryzmat(profil, -cw / 2, cw / 2), M))
    # rowek kablowy 2,5 szer. x 1,5 wys. (R50-U9) na zewnetrznej dolnej krawedzi: lewy, prawy, tylny bok; przeloty w narozach
    # (profil wyzej) maja ten sam przekroj i wychodza poza naroze zewnetrzne, wiec z rowkami tworza jedna ciagla pustke
    rh, rw = P['wire_rabbet'], P['wire_rabbet_w']
    tnace.append(bm_prostopadloscian(-zw - NADDATEK, -zw + rw, -zw - NADDATEK, zw + NADDATEK, -NADDATEK, rh))
    tnace.append(bm_prostopadloscian(zw - rw, zw + NADDATEK, -zw - NADDATEK, zw + NADDATEK, -NADDATEK, rh))
    tnace.append(bm_prostopadloscian(-zw - NADDATEK, zw + NADDATEK, zw - rw, zw + NADDATEK, -NADDATEK, rh))
    # kanaly 2 x 1,2: pod nasada od rowka do x = +-64 i pod uchem wzdluz x = +-64 do szczeliny blatu
    kw, kh, kx = P['tab_cable_channel_w'], P['tab_cable_channel_h'], P['tab_cable_channel_x']
    # (B) z rowka tylnego przy x = tab_root_x_in do kanalu pod nasada L; (C) pod nasada w polowie jej czesci tylnej
    # (y zw...ry1) do x = ex_out; (D) pod uchem wzdluz x = kx. Dawny odcinek (A) w dnie scianki zbedny: rowek 2,5 siega do y zw - 2,5.
    yc = (zw + ry1) / 2
    yb0, yb1 = yc - kw / 2, yc + kw / 2
    for zx in (-1, 1):
        xa, xb = sorted((zx * rxi, zx * (rxi + kw)))
        tnace.append(bm_prostopadloscian(xa, xb, zw - rw + NADDATEK, yb0 + NADDATEK, -NADDATEK, kh))
        xa, xb = sorted((zx * rxi, zx * (ex_out + NADDATEK)))
        tnace.append(bm_prostopadloscian(xa, xb, yb0, yb1, -NADDATEK, kh))
        xa, xb = sorted((zx * (kx - kw / 2), zx * (ex_out + NADDATEK)))
        tnace.append(bm_prostopadloscian(xa, xb, yb0 + NADDATEK, P['wire_slot_y'], -NADDATEK, kh))
        # otwor magnesu w uchu
        tnace.append(bm_walec(P['tab_magnet_hole_d'] / 2, -NADDATEK, tt + NADDATEK, zx * P['tab_pos_x'], P['tab_magnet_y']))
    # wyciecie palcowe w przednim boku, pelna wysokosc
    fw = P['finger_cut_w']
    tnace.append(bm_prostopadloscian(-fw / 2, fw / 2, -zw - NADDATEK, -h + NADDATEK, -NADDATEK, H + NADDATEK))
    return zbuduj_z_operacji(nazwa, baza, dodatnie, tnace)


# ---- wkladka okragla (R58, 4.6a): uklad jak wkladka - srodek otworu, spod ramy Z = 0 ----
# Obrys zewnetrzny ramy, uszy, kolki, magnesy uszu, rowek kablowy, kanaly pod uszami i strzalki = wkladka kwadratowa (kopie logiki
# zbuduj_wkladke w funkcjach _wkl_*; zbuduj_wkladke bez zmian, bo ramka_wkladka_v2.stl R59 nie odtwarza sie bajtowo).

def _wkl_obrys(P):
    """Obrys ramy + nasad L + uszu (CCW), jak w zbuduj_wkladke."""
    h = P['insert_opening'] / 2
    zw = h + P['insert_wall_w']
    ex_in, ex_out = P['tab_pos_x'] - P['tab_w'] / 2, P['tab_pos_x'] + P['tab_w'] / 2
    rxi, ry1, ty1 = P['tab_root_x_in'], P['tab_root_y1'], P['tab_end_y']
    rxo = P['tab_root_x_out']
    if rxo > zw + 1e-9 or P['tab_root_y0'] > zw:
        raise BladProjektu('nasada ucha: tab_root_x_out %.2f > krawedz ramy %.2f albo tab_root_y0 > %.2f' % (rxo, zw, zw))
    prawa = [(zw, -zw), (zw, zw), (ex_out, zw), (ex_out, ty1), (ex_in, ty1), (ex_in, ry1), (rxi, ry1), (rxi, zw)]
    return prawa + [(-x, y) for x, y in reversed(prawa)]


def _wkl_dodatnie_wspolne(P):
    """Kolki ustalajace pod uszami, napis (gdy insert_label_h > 0) i strzalki - jak w zbuduj_wkladke."""
    H = P['insert_h']
    wyn = []
    rp, hp, cp = P['tab_pin_d'] / 2, P['tab_pin_h'], P['tab_pin_chamfer']
    n = seg_okregu(rp)
    for zx in (-1, 1):
        x, y = zx * P['tab_pos_x'], P['tab_pin_y']
        wyn.append(bm_z_pierscieni([(okrag(rp - cp, x, y, n), -hp), (okrag(rp, x, y, n), -hp + cp), (okrag(rp, x, y, n), NADDATEK)]))
    rel = P['label_relief_h']
    if P['insert_label_h'] > 0:
        for wyspa in bryly_tekstu(P, P['insert_label_text'], P['insert_label_h'], rel, P['insert_label_x'], P['insert_label_y'],
                                  'wkladka okragla PRZOD', pelna=True):
            wyn.append(bm_przesun(wyspa, (0, 0, H)))
    ay, al, aw = P['insert_label_y'], P['insert_arrow_l'], P['insert_arrow_w']
    for ax in P['insert_arrow_x']:
        wyn.append(bm_pryzmat([(ax - aw / 2, ay + al / 2), (ax, ay - al / 2), (ax + aw / 2, ay + al / 2)], H - NADDATEK, H + rel))
    return wyn


def _wkl_tnace_wspolne(P):
    """Rowek kablowy (lewy, prawy, tylny bok), kanaly pod nasada i uchem, otwory magnesow uszu - jak w zbuduj_wkladke."""
    h = P['insert_opening'] / 2
    zw = h + P['insert_wall_w']
    tt = P['tab_t']
    ex_out = P['tab_pos_x'] + P['tab_w'] / 2
    rxi, ry1 = P['tab_root_x_in'], P['tab_root_y1']
    rh, rw = P['wire_rabbet'], P['wire_rabbet_w']
    wyn = [bm_prostopadloscian(-zw - NADDATEK, -zw + rw, -zw - NADDATEK, zw + NADDATEK, -NADDATEK, rh),
           bm_prostopadloscian(zw - rw, zw + NADDATEK, -zw - NADDATEK, zw + NADDATEK, -NADDATEK, rh),
           bm_prostopadloscian(-zw - NADDATEK, zw + NADDATEK, zw - rw, zw + NADDATEK, -NADDATEK, rh)]
    kw, kh, kx = P['tab_cable_channel_w'], P['tab_cable_channel_h'], P['tab_cable_channel_x']
    yc = (zw + ry1) / 2
    yb0, yb1 = yc - kw / 2, yc + kw / 2
    for zx in (-1, 1):
        xa, xb = sorted((zx * rxi, zx * (rxi + kw)))
        wyn.append(bm_prostopadloscian(xa, xb, zw - rw + NADDATEK, yb0 + NADDATEK, -NADDATEK, kh))
        xa, xb = sorted((zx * rxi, zx * (ex_out + NADDATEK)))
        wyn.append(bm_prostopadloscian(xa, xb, yb0, yb1, -NADDATEK, kh))
        xa, xb = sorted((zx * (kx - kw / 2), zx * (ex_out + NADDATEK)))
        wyn.append(bm_prostopadloscian(xa, xb, yb0 + NADDATEK, P['wire_slot_y'], -NADDATEK, kh))
        wyn.append(bm_walec(P['tab_magnet_hole_d'] / 2, -NADDATEK, tt + NADDATEK, zx * P['tab_pos_x'], P['tab_magnet_y']))
    return wyn


def otwor_wkladki_okraglej(P, delta=0.0):
    """R58: obrys otworu wkladki okraglej: kolo plate_round_d/2 + round_insert_clearance ze scieciem na kierunku round_flat_angle
    w odleglosci (odleglosc sciecia plytki + luz); odsuniety o delta na zewnatrz; CCW, luk od konca do konca cieciwy.
    Ta sama liczba wierzcholkow dla kazdego delta (pierscien fazy z odpowiadajacymi sobie wierzcholkami)."""
    R, dist, kat, _w = sciecie_okraglej(P)
    luz = P['round_insert_clearance']
    ro, do = R + luz + delta, dist + luz + delta
    if not (0 < do < ro):
        raise BladProjektu('otwor wkladki okraglej: sciecie %.3f poza (0, %.3f)' % (do, ro))
    beta = math.acos(do / ro)
    n = seg_okregu(R + luz)
    a0 = math.radians(kat) + beta
    a1 = math.radians(kat) + 2 * math.pi - beta
    return [(ro * math.cos(a0 + (a1 - a0) * i / (n - 1)), ro * math.sin(a0 + (a1 - a0) * i / (n - 1))) for i in range(n)]


def _przeciecie_z_okregiem(p0, p1, r):
    """Punkt odcinka p0 (wewnatrz kola r) -> p1 (poza kolem) lezacy na okregu r."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    a = dx * dx + dy * dy
    b = 2 * (p0[0] * dx + p0[1] * dy)
    c = p0[0] ** 2 + p0[1] ** 2 - r * r
    t = (-b + math.sqrt(b * b - 4 * a * c)) / (2 * a)
    return (p0[0] + t * dx, p0[1] + t * dy)


def kontur_polek_okraglych(P):
    """R58: obrys wolnego otworu na wysokosci polki (Z 0...insert_shelf_h): kolo round_insert_ledge_r minus 4 kwadraty round_insert_shelf
    (boki rownolegle do osi X/Y) o srodkach w osiach A, B, C, D (osie_okragle). Kazdy kwadrat musi wystawac poza kolo dokladnie
    jednym naroznikiem (najdalszym od srodka) - wtedy obrys idzie po luku do przeciecia z bokiem kwadratu, po 3 naroznikach w kole
    i wraca na luk. CCW."""
    rl, s = P['round_insert_ledge_r'], P['round_insert_shelf'] / 2
    pelny = 2 * math.pi
    krok = pelny / seg_okregu(rl)
    wyciecia = []
    for c, (_kat, cx, cy) in osie_okragle(P).items():
        rogi = [(cx + s, cy - s), (cx + s, cy + s), (cx - s, cy + s), (cx - s, cy - s)]
        wew = [math.hypot(x, y) < rl - 1e-6 for x, y in rogi]
        if sum(wew) != 3:
            raise BladProjektu('polka %s wkladki okraglej: %d naroznikow w kole r %g (obslugiwane: 3)' % (c, sum(wew), rl))
        k = wew.index(False)
        pa = _przeciecie_z_okregiem(rogi[(k - 1) % 4], rogi[k], rl)
        pb = _przeciecie_z_okregiem(rogi[(k + 1) % 4], rogi[k], rl)
        droga = [pa, rogi[(k - 1) % 4], rogi[(k - 2) % 4], rogi[(k - 3) % 4], pb]
        wyciecia.append((math.atan2(pa[1], pa[0]) % pelny, math.atan2(pb[1], pb[0]) % pelny, droga))
    wyciecia.sort(key=lambda w: w[0])
    pkt = []
    for i, (aa, ab, droga) in enumerate(wyciecia):
        szer = (ab - aa) % pelny
        if not (0 < szer < math.pi):
            raise BladProjektu('polki wkladki okraglej: kolejnosc przeciec z okregiem')
        pkt += droga
        a_nast = wyciecia[(i + 1) % len(wyciecia)][0]
        luk = (a_nast - ab) % pelny
        if luk <= 0 or luk >= pelny - szer:
            raise BladProjektu('polki wkladki okraglej nachodza na siebie')
        n = max(1, int(math.ceil(luk / krok)))
        for j in range(1, n):
            t = ab + luk * j / n
            pkt.append((rl * math.cos(t), rl * math.sin(t)))
    pole = sum(pkt[i][0] * pkt[(i + 1) % len(pkt)][1] - pkt[(i + 1) % len(pkt)][0] * pkt[i][1] for i in range(len(pkt)))
    if pole <= 0:
        raise BladProjektu('obrys polek wkladki okraglej nie jest CCW')
    return pkt


def zbuduj_wkladke_okragla(P, nazwa):
    """R58 (4.6a): wkladka pod plytke okragla. Obrys zewnetrzny ramy, wysokosc, uszy, kolki, magnesy, rowek kablowy, kanaly pod uszami
    i strzalki jak wkladka kwadratowa. Otwor: kolo plytki + 2*luz ze scieciem (odleglosc sciecia plytki + luz), faza insert_chamfer
    na gornej krawedzi calego obrysu; polka (Z 0...insert_shelf_h): wystep od otworu do round_insert_ledge_r + 4 kwadratowe polki
    round_insert_shelf w osiach A-D; kieszenie Halla przelotowe w osiach A, B, C, kanal pod polka do okregu otworu i przelot przez
    pelny naroznik do naroza zewnetrznego (jedna bryla, ciagla z rowkiem kablowym); zebro klucza na osi D (runda 2, zamiast kolka);
    wyciecie palcowe z przodu na pelnej wysokosci, takze przez wystep."""
    h = P['insert_opening'] / 2
    zw = h + P['insert_wall_w']
    H, sh, tt = P['insert_h'], P['insert_shelf_h'], P['tab_t']
    R = P['plate_round_d'] / 2
    ro = R + P['round_insert_clearance']
    rm = P['round_magnet_r']
    obrys = _wkl_obrys(P)
    otwor = otwor_wkladki_okraglej(P)
    polki = kontur_polek_okraglych(P)
    baza = bm_z_konturow([obrys, polki], 0.0, sh)
    dodatnie = [bm_z_konturow([obrys, otwor], sh - NADDATEK, tt),
                bm_z_konturow([prostokat(2 * zw, 2 * zw), otwor], tt - NADDATEK, H)]
    osie = osie_okragle(P)
    dodatnie += _wkl_dodatnie_wspolne(P)
    # R58 runda 2 (B1 recenzji): zebro klucza na osi D zamiast kolka - doklejane PO roznicach (dodatnie_po), zeby faza otworu go nie ciela
    dodatnie_po = bryly_zebra_klucza(P)
    tnace = []
    # faza 1 x 45 na gornej krawedzi calego obrysu otworu (kolo + sciecie)
    c = P['insert_chamfer']
    wew_f = otwor_wkladki_okraglej(P, -NADDATEK)
    tnace.append(bm_pierscien_poziomy([(otwor, wew_f, H - c), (otwor_wkladki_okraglej(P, c + NADDATEK), wew_f, H + NADDATEK)]))
    # kieszenie Halla (X x Y, rownolegle do osi) w osiach A, B, C; kanal po przekatnej: pod polka (wys. hall_lead_channel_h) od osi
    # do okregu otworu, dalej przelot (wys. hall_wall_pass_h) przez pelny naroznik poza naroze zewnetrzne - jeden profil
    hw, hl = P['hall_pocket_w'], P['hall_pocket_l']
    cw, chh, ph = P['hall_lead_channel_w'], P['hall_lead_channel_h'], P['hall_wall_pass_h']
    for naroze in 'ABC':
        _k, px, py = osie[naroze]
        if abs(abs(px) - abs(py)) > 1e-6:
            raise BladProjektu('wkladka okragla: os %s nie lezy na przekatnej ramy (kanal do naroza zewnetrznego)' % naroze)
        tnace.append(bm_prostopadloscian(px - hw / 2, px + hw / 2, py - hl / 2, py + hl / 2, -NADDATEK, sh + NADDATEK))
        d = Vector((px, py, 0)).normalized()
        t_h = ro - rm
        t_k = zw * math.sqrt(2) - rm + 5 * NADDATEK
        profil = [(0.0, -NADDATEK), (t_k, -NADDATEK), (t_k, ph), (t_h, ph), (t_h, chh), (0.0, chh)]
        M = Matrix(((d.x, 0, -d.y, px), (d.y, 0, d.x, py), (0, 1, 0, 0), (0, 0, 0, 1)))
        tnace.append(bm_transformuj(bm_pryzmat(profil, -cw / 2, cw / 2), M))
    tnace += _wkl_tnace_wspolne(P)
    # wyciecie palcowe w przednim boku, pelna wysokosc, przez rame i wystep: od krawedzi przedniej do okregu wystepu na x = +-fw/2
    # (+5 x NADDATEK w wolny otwor; dalej jest tylko otwor, wiec bryla wyniku nie zalezy od tej wartosci)
    fw, rl = P['finger_cut_w'], P['round_insert_ledge_r']
    y_kon = -math.sqrt(rl * rl - (fw / 2) ** 2) + 5 * NADDATEK
    tnace.append(bm_prostopadloscian(-fw / 2, fw / 2, -zw - NADDATEK, y_kon, -NADDATEK, H + NADDATEK))
    return zbuduj_z_operacji(nazwa, baza, dodatnie, tnace, dodatnie_po=dodatnie_po)


def bryly_zebra_klucza(P):
    """R58 runda 2/3: zebro klucza wkladki okraglej na osi D (kierunek round_flat_angle). Uklad lokalny: u wzdluz osi D, v prostopadle.
    Czesc dolna (Z polka...wierzch wkladki): u od round_key_rib_r0 do lica sciecia + faza otworu + 2 x NADDATEK (wypelnia faze otworu
    za zebrem - ponizej wierzchu jedna bryla ze sciana), v +-w/2. Czesc gorna (nad wierzchem): u od r0 do round_key_rib_top_r1 (runda 3,
    P1 recenzji rundy 2: kolnierz pokrywki w skrajnym ustawieniu plytki i pokrywki schodzi do r 49,6 - przed lico sciecia 49,756),
    faza round_key_rib_chamfer na obu bokach, czole wewnetrznym i (runda 3) krawedzi zewnetrznej; wierzch na polka + round_key_rib_h."""
    H, sh, c_otw = P['insert_h'], P['insert_shelf_h'], P['insert_chamfer']
    w, r0, h, c = P['round_key_rib_w'], P['round_key_rib_r0'], P['round_key_rib_h'], P['round_key_rib_chamfer']
    r1 = P['round_key_rib_top_r1']
    _R, dist, kat, _cw = sciecie_okraglej(P)
    do = dist + P['round_insert_clearance']
    z_faz = sh + h - c                    # poczatek fazy zebra
    if not (sh + h > H and z_faz >= H - 1e-9 and w - 2 * c > 0 and r0 + 2 * c < r1 <= do + 1e-9):
        raise BladProjektu('zebro klucza: geometria poza obslugiwanym zakresem (wierzch %.2f, poczatek fazy %.2f, wierzch wkladki %.2f, szerokosc gora %.2f, '
                           'wierzch u %.2f...%.2f, koniec czesci gornej r %.3f, lico sciecia %.3f)' % (sh + h, z_faz, H, w - 2 * c, r0 + c, r1 - c, r1, do))
    M = obrot_z(kat)
    dolna = bm_prostopadloscian(r0, do + c_otw + 2 * NADDATEK, -w / 2, w / 2, sh - NADDATEK, H)
    pr = lambda u0, u1, v: [(u1, -v), (u1, v), (u0, v), (u0, -v)]
    gorna = bm_z_pierscieni([(pr(r0, r1, w / 2), H - NADDATEK), (pr(r0, r1, w / 2), z_faz), (pr(r0 + c, r1 - c, w / 2 - c), sh + h)])
    return [bm_transformuj(dolna, M), bm_transformuj(gorna, M)]


# ---- blat (uklad: srodek, wierzch Z = 0, w dol ujemne) ----

def wymiary_blatu(P):
    so = P['box_outer'] / 2 - P['wall_t'] - P['blat_skirt_clearance']     # lico zewn. kolnierza
    rs = P['blat_corner_r'] - P['blat_skirt_clearance']                     # promien kolnierza (4.4: R 4,5)
    z0 = -(P['blat_t'] + P['blat_skirt_h'])
    return so, rs, z0


def zbuduj_blat(P, nazwa):
    B, r, re, t = P['box_outer'], P['blat_corner_r'], P['blat_top_edge_r'], P['blat_t']
    nl = seg_luku(r, math.pi / 2)
    nf = seg_luku(re, math.pi / 2)
    pier = [(prostokat_zaokr(B, B, r, n_luk=nl), -t)]
    for k in range(nf + 1):
        th = math.pi / 2 * k / nf
        ins = re - re * math.cos(th)
        pier.append((prostokat_zaokr(B - 2 * ins, B - 2 * ins, r - ins, n_luk=nl), -re + re * math.sin(th)))
    baza = bm_z_pierscieni(pier)
    so, rs, z0 = wymiary_blatu(P)
    st = P['blat_skirt_t']
    nls = seg_luku(rs, math.pi / 2)
    dodatnie = [bm_pierscien(prostokat_zaokr(2 * so, 2 * so, rs, n_luk=nls),
                             prostokat_zaokr(2 * (so - st), 2 * (so - st), rs - st, n_luk=nls), z0, -t + NADDATEK)]
    tnace = []
    # haczyki zatrzaskowe (R6, R47, R48): wystep z plaska powierzchnia zaczepu u gory i rampa od dolu
    zt = P['snap_hook_z'] - P['blat_top_z'] + P['snap_hook_hgt']
    zb = P['snap_hook_z'] - P['blat_top_z']
    hh, hw, nw = P['snap_hook_h'], P['snap_hook_w'], P['snap_notch_w']
    ramie = z0 + P['snap_hook_arm_l']
    profil = [(-NADDATEK, zt), (hh, zt), (hh, (zt + zb) / 2), (0.0, zb), (-NADDATEK, zb)]
    for kat, a in pozycje_scian(P):
        M = M_sciana(kat, so)
        dodatnie.append(bm_transformuj(bm_pryzmat(profil, a - hw / 2, a + hw / 2), M))
        # ramie 1,5 (snap_hook_t): pocienienie kolnierza od wewnatrz miedzy nacieciami
        tnace.append(bm_lokalny_box(-st - NADDATEK, -P['snap_hook_t'], z0 - NADDATEK, ramie, a - hw / 2 - NADDATEK / 2, a + hw / 2 + NADDATEK / 2, M))
        for zn in (-1, 1):
            c0, c1 = sorted((a + zn * hw / 2, a + zn * (hw / 2 + nw)))
            tnace.append(bm_lokalny_box(-st - NADDATEK, NADDATEK, z0 - NADDATEK, ramie, c0, c1, M))
    # slupki pod wkrety tylne (R7, R47, R48) z otworami wzdluz Y pod wkret M3 formujacy gwint w PA12 (R49, R49a)
    zs = P['blat_screw_z'] - P['blat_top_z']
    for zx in (-1, 1):
        xc = zx * P['blat_screw_pitch'] / 2
        dodatnie.append(bm_prostopadloscian(xc - P['blat_post_w'] / 2, xc + P['blat_post_w'] / 2, P['blat_post_y0'],
                                            P['blat_post_y0'] + P['blat_post_size'], z0, -t + NADDATEK))
        tnace.append(bm_stozek_os('Y', P['insert_hole_m3'] / 2, P['insert_hole_m3'] / 2, so + NADDATEK, so - P['blat_post_hole_depth'], (xc, 0, zs)))
    # bez bossow ramy dyfuzora (R50-U1); kieszen dyfuzora (naroza ostre przy diffuser_pocket_r = 0, R50-U15) i okno
    dp = P['diffuser_pocket']
    tnace.append(bm_pryzmat(prostokat_r(dp, dp, P['diffuser_pocket_r']), -P['diffuser_t'], NADDATEK))
    tnace.append(bm_pryzmat(prostokat(P['window_through'], P['window_through']), -t - NADDATEK, -P['diffuser_t'] + NADDATEK))
    # kolki, magnesy, szczeliny kabli wkladki
    for zx in (-1, 1):
        x = zx * P['tab_pos_x']
        tnace.append(bm_walec(P['blat_pin_hole_d'] / 2, -P['blat_pin_hole_depth'], NADDATEK, x, P['tab_pin_y']))
        tnace.append(bm_walec(P['blat_magnet_pocket_d'] / 2, -P['blat_magnet_pocket_depth'], NADDATEK, x, P['tab_magnet_y']))
        xs = zx * P['wire_slot_x']
        tnace.append(bm_prostopadloscian(xs - P['wire_slot_w'] / 2, xs + P['wire_slot_w'] / 2, P['wire_slot_y'] - P['wire_slot_l'] / 2,
                                         P['wire_slot_y'] + P['wire_slot_l'] / 2, -t - NADDATEK, NADDATEK))
    return zbuduj_z_operacji(nazwa, baza, dodatnie, tnace)


# ---- korpus (uklad globalny D3) ----

def pozycje_podkladek(P):
    return [(sx * P['panel_hole_pitch_x'] / 2 + P['panel_hole_offset_x'], sy * P['panel_hole_pitch_y'] / 2 + P['panel_hole_offset_y'], sx, sy)
            for sx in (-1, 1) for sy in (-1, 1)]


def os_rowka(P, sx, sy):
    """Os podkladki-stadionu i rowka wkretu panelu w dnie (R50-2): po przekatnej od (sx, sy)*pitch_min/2 do (sx, sy)*pitch_max/2."""
    p0, p1 = P['panel_slot_pitch_min'] / 2, P['panel_slot_pitch_max'] / 2
    return (sx * p0, sy * p0), (sx * p1, sy * p1)


def bm_stadion_os(a, b, szer, z0, z1):
    """Stadion o szerokosci szer wokol odcinka a-b (XY), Z od z0 do z1."""
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    kat = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    return bm_pryzmat(stadion(L + szer, szer, (a[0] + b[0]) / 2, (a[1] + b[1]) / 2, kat), z0, z1)


def pozycje_bossow_pi(P):
    x0 = P['pi_pos_x'] + P['pi_hole_edge']
    y0 = P['pi_pos_y'] + P['pi_hole_edge']
    return [(x0 + i * P['pi_hole_pitch_l'], y0 + j * P['pi_hole_pitch_w']) for i in (0, 1) for j in (0, 1)]


def zbuduj_korpus(P, napis, nazwa):
    B, r, e, w, ft, Hk = P['box_outer'], P['box_corner_r'], P['box_edge_r'], P['wall_t'], P['floor_t'], P['korpus_h']
    nl = seg_luku(r, math.pi / 2)
    nf = seg_luku(e, math.pi / 2)
    pier = []
    for k in range(nf + 1):
        th = math.pi / 2 * k / nf
        ins = e - e * math.sin(th)
        pier.append((prostokat_zaokr(B - 2 * ins, B - 2 * ins, r - ins, n_luk=nl), e - e * math.cos(th)))
    pier.append((prostokat_zaokr(B, B, r, n_luk=nl), Hk))
    pier.append((prostokat_zaokr(B - 2 * w, B - 2 * w, r - w, n_luk=nl), Hk))
    pier.append((prostokat_zaokr(B - 2 * w, B - 2 * w, r - w, n_luk=nl), ft))
    baza = bm_z_pierscieni(pier)
    dodatnie, tnace = [], []
    # podkladki-stadiony panelu i rowki wkretow w dnie po przekatnych (R50-2), bez pogłebien (R50-U20); bez zeber (R50-U5)
    for sx in (-1, 1):
        for sy in (-1, 1):
            a, b = os_rowka(P, sx, sy)
            dodatnie.append(bm_stadion_os(a, b, P['panel_pad_d'], ft - NADDATEK, ft + P['panel_pad_h']))
            tnace.append(bm_stadion_os(a, b, P['panel_slot_w'], -NADDATEK, ft + P['panel_pad_h'] + NADDATEK))
    # bossy Pi (R48, R50-6) z otworami pod wkret M2,5 formujacy gwint w PA12 (R49, bez wkladek)
    for x, y in pozycje_bossow_pi(P):
        dodatnie.append(bm_walec(P['pi_boss_d'] / 2, ft - NADDATEK, ft + P['pi_standoff_h'], x, y))
        tnace.append(bm_walec(P['insert_hole_m25'] / 2, ft + P['pi_standoff_h'] - P['insert_depth_m25'], ft + P['pi_standoff_h'] + NADDATEK, x, y))
    # kieszen DC (Z27, R50-3, R50-4): skrzynka od lewej sciany korpusu do x = dc_pos_x (prawa sciana skrzynki), sciany dc_pocket_wall,
    # wnetrze i okno w tylnej scianie jednym profilem (okno konczy sie na wewnetrznym licu prawej sciany skrzynki)
    dw, dh, dd, dwl = P['dc_pocket_w'], P['dc_pocket_h'], P['dc_pocket_depth'], P['dc_pocket_wall']
    z0d, xd, xo = P['dc_pocket_z0'], P['dc_pos_x'], P['dc_pocket_x_window']
    if P['dc_socket_axis'] != 'X':
        raise BladProjektu('dc_socket_axis = %s: zaimplementowana tylko os X (R50-3)' % P['dc_socket_axis'])
    xl = -(B / 2 - w)                                  # lewa sciana skrzynki = lico wewn. lewej sciany korpusu
    xw0, xw1 = xo - dw / 2, xo + dw / 2
    if abs(xw1 - (xd - dwl)) > 1e-6 or xw0 < xl + dwl:
        raise BladProjektu('kieszen DC: okno x %.2f…%.2f nie konczy sie na scianie gniazda %.2f albo wchodzi w lewa sciane skrzynki' % (xw0, xw1, xd - dwl))
    dodatnie.append(bm_prostopadloscian(xl - NADDATEK, xd, B / 2 - dd, B / 2 - w + NADDATEK, z0d - dwl, z0d + dh + dwl))
    wnetrze = [(xl + dwl, B / 2 - dd + dwl), (xd - dwl, B / 2 - dd + dwl), (xd - dwl, B / 2 + NADDATEK), (xw0, B / 2 + NADDATEK),
               (xw0, B / 2 - w), (xl + dwl, B / 2 - w)]
    tnace.append(bm_pryzmat(wnetrze, z0d, z0d + dh))
    # gniazdo DC w prawej scianie skrzynki, os wzdluz X (y dc_pos_y, Z dc_pos_z)
    tnace.append(bm_stozek_os('X', P['dc_hole_d'] / 2, P['dc_hole_d'] / 2, xd - dwl - NADDATEK, xd + NADDATEK, (0, P['dc_pos_y'], P['dc_pos_z'])))
    # napis na przedniej sciance (D15): plaszczyzna XZ, czytelny od przodu
    Rx = Matrix(((1, 0, 0, 0), (0, 0, -1, -B / 2), (0, 1, 0, 0), (0, 0, 0, 1)))
    for wyspa in bryly_tekstu(P, napis, P['label_text_h'], P['label_relief_h'], 0.0, P['label_pos_z'], 'korpus %s' % napis):
        dodatnie.append(bm_transformuj(wyspa, Rx))
    # dno: wloty pod Pi (R50-U19); bez szczeliny SD (R50-U6) i bez gniazd stopek (R50-U16)
    for y in P['floor_vent_y']:
        tnace.append(bm_prostopadloscian(P['floor_vent_x'] - P['floor_vent_l'] / 2, P['floor_vent_x'] + P['floor_vent_l'] / 2,
                                         y - P['floor_vent_w'] / 2, y + P['floor_vent_w'] / 2, -NADDATEK, ft + NADDATEK))
    # szczeliny wylotowe (tyl, boki), bez daszkow (R50-U4)
    vw, vh, vz = P['vent_slot_w'], P['vent_slot_h'], P['vent_slot_z']
    sciany = [(90.0, [-x for x in P['vent_slots_rear_x']]), (0.0, list(P['vent_slots_side_y'])), (180.0, [-y for y in P['vent_slots_side_y']])]
    for kat, pozycje in sciany:
        M = M_sciana(kat, B / 2)
        for c in pozycje:
            tnace.append(bm_lokalny_box(-w - NADDATEK, NADDATEK, vz - vh / 2, vz + vh / 2, c - vw / 2, c + vw / 2, M))
    # tylna scianka: okno USB, 2 rowki poziome flanszy (R50-5), otwory wkretow blatu z pogłebieniem stozkowym 90 st.
    ux, uz = P['usb_pos_x'], P['usb_pos_z']
    tnace.append(bm_prostopadloscian(ux - P['usb_cut_w'] / 2, ux + P['usb_cut_w'] / 2, B / 2 - w - NADDATEK, B / 2 + NADDATEK,
                                     uz - P['usb_cut_h'] / 2, uz + P['usb_cut_h'] / 2))
    a0, a1, sw = P['usb_slot_pitch_min'] / 2, P['usb_slot_pitch_max'] / 2, P['usb_slot_w']
    for zx in (-1, 1):
        tnace.append(bm_profil_os('Y', stadion(a1 - a0 + sw, sw), B / 2 - w - NADDATEK, B / 2 + NADDATEK, (ux + zx * (a0 + a1) / 2, 0, uz)))
        xb = zx * P['blat_screw_pitch'] / 2
        rd, rc = P['blat_screw_hole_d'] / 2, P['blat_screw_csink_d'] / 2
        tnace.append(bm_stozek_os('Y', rd, rd, B / 2 - w - NADDATEK, B / 2 + NADDATEK, (xb, 0, P['blat_screw_z'])))
        tnace.append(bm_stozek_os('Y', rd, rc + NADDATEK, B / 2 - (rc - rd), B / 2 + NADDATEK, (xb, 0, P['blat_screw_z'])))
    # kieszenie zatrzaskow blatu od wewnatrz (R6, Z z korpus_h, R50-1)
    pw, ph_, pd, pz = P['snap_pocket_w'], P['snap_pocket_h'], P['snap_pocket_depth'], P['snap_pocket_z']
    for kat, a in pozycje_scian(P):
        tnace.append(bm_lokalny_box(-NADDATEK, pd, pz, pz + ph_, a - pw / 2, a + pw / 2, M_sciana(kat, B / 2 - w)))
    return zbuduj_z_operacji(nazwa, baza, dodatnie, tnace)


# ---- bryly zastepcze (uklad globalny, zestaw zlozony) ----

def bm_wtyk_bonnet(P, kierunek):
    """Wtyk DC Bonnetu: bonnet_dc_plug_len x _w x _h od bonnet_dc_pos w kierunku -X/+X/-Y/+Y, gorna krawedz na szczycie stosu Pi."""
    bx, by, L, ww, hh = P['bonnet_dc_pos_x'], P['bonnet_dc_pos_y'], P['bonnet_dc_plug_len'], P['bonnet_dc_plug_w'], P['bonnet_dc_plug_h']
    z_top = P['floor_t'] + P['pi_standoff_h'] + P['pi_stack_h']
    kier = kierunek.replace('−', '-')
    if kier not in ('-X', '+X', '-Y', '+Y'):
        raise BladProjektu('bonnet_dc_dir = %s' % kierunek)
    s = -1 if kier[0] == '-' else 1
    if kier[1] == 'Y':
        y0, y1 = sorted((by, by + s * L))
        return bm_prostopadloscian(bx - ww / 2, bx + ww / 2, y0, y1, z_top - hh, z_top)
    x0, x1 = sorted((bx, bx + s * L))
    return bm_prostopadloscian(x0, x1, by - ww / 2, by + ww / 2, z_top - hh, z_top)


def bryly_zastepcze(P):
    """Slownik nazwa -> bmesh w ukladzie globalnym (zestaw zlozony)."""
    B, ft, w = P['box_outer'], P['floor_t'], P['wall_t']
    z_pi = ft + P['pi_standoff_h']
    z_top_pi = z_pi + P['pi_stack_h']
    pz = P['panel_pcb_z']
    zb = {}
    ps = P['panel_size']
    zb['proxy_panel'] = bm_polacz([
        bm_prostopadloscian(-ps / 2, ps / 2, -ps / 2, ps / 2, pz, pz + P['panel_pcb_t']),
        bm_prostopadloscian(P['panel_conn_zone_x'] - P['panel_conn_zone_w'] / 2, P['panel_conn_zone_x'] + P['panel_conn_zone_w'] / 2,
                            P['panel_conn_zone_y'] - P['panel_conn_zone_h'] / 2, P['panel_conn_zone_y'] + P['panel_conn_zone_h'] / 2,
                            pz - P['panel_bottom_parts_h'], pz)])
    zb['proxy_pi_bonnet'] = bm_prostopadloscian(P['pi_pos_x'], P['pi_pos_x'] + P['pi_l'], P['pi_pos_y'], P['pi_pos_y'] + P['pi_w'], z_pi, z_top_pi)
    zb['proxy_wtyk_bonnet'] = bm_wtyk_bonnet(P, P['bonnet_dc_dir'])
    for i, (x, y, sx, sy) in enumerate(pozycje_podkladek(P), 1):
        zb['proxy_dystans_%d' % i] = bm_walec(P['standoff_d'] / 2, ft + P['panel_pad_h'], pz, x, y)
    ds = P['diffuser_size']
    zb['proxy_dyfuzor'] = bm_prostopadloscian(-ds / 2, ds / 2, -ds / 2, ds / 2, P['blat_top_z'] - P['diffuser_t'], P['blat_top_z'])
    # gniazdo DC osia X (R50-3): korpus ø dc_socket_body_d x dc_socket_body_l od zewn. lica prawej sciany skrzynki (x = dc_pos_x) w +X,
    # nakretka ø dc_nut_d o grubosci dc_pocket_wall (liczbowo = 2) na tej scianie od wnetrza obudowy
    xd, srodek_dc = P['dc_pos_x'], (0, P['dc_pos_y'], P['dc_pos_z'])
    czesci_dc = [bm_stozek_os('X', P['dc_socket_body_d'] / 2, P['dc_socket_body_d'] / 2, xd, xd + P['dc_socket_body_l'], srodek_dc),
                 bm_stozek_os('X', P['dc_nut_d'] / 2, P['dc_nut_d'] / 2, xd, xd + P['dc_pocket_wall'], srodek_dc)]
    # gwintu gniazda ø8 w tulejce nie modeluje sie: srednica gwintu nie ma klucza (pomiar #16); tulejka ma otwor dc_bush_inner_d
    zb['proxy_gniazdo_dc'] = bm_polacz(czesci_dc)
    zb['proxy_gniazdo_usb'] = bm_prostopadloscian(P['usb_pos_x'] - P['usb_body_w'] / 2, P['usb_pos_x'] + P['usb_body_w'] / 2,
                                                  B / 2 - w - P['usb_body_depth'], B / 2 - w,
                                                  P['usb_pos_z'] - P['usb_body_h'] / 2, P['usb_pos_z'] + P['usb_body_h'] / 2)
    m = P['plate_size'] / 2 - P['marker_offset']
    hx, hy, hz = P['hall_sensor_size']
    for nazwa, (sx, sy) in (('A', (-1, -1)), ('B', (-1, 1)), ('C', (1, 1))):
        zb['proxy_hall_%s' % nazwa] = bm_prostopadloscian(sx * m - hx / 2, sx * m + hx / 2, sy * m - hy / 2, sy * m + hy / 2,
                                                          P['blat_top_z'], P['blat_top_z'] + hz)
    z_spod_plytki = P['blat_top_z'] + P['insert_shelf_h']
    zm = z_spod_plytki + P['magnet_pocket_depth'] - P['magnet_h']
    zb['proxy_magnes_A'] = bm_walec(P['magnet_d'] / 2, zm, zm + P['magnet_h'], -m, -m)
    fo = B / 2 - P['foot_edge_offset']
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1)), 1):
        zb['proxy_stopka_%d' % i] = bm_walec(P['foot_d'] / 2, -P['foot_h'], 0.0, sx * fo, sy * fo)
    return zb


def bryly_zastepcze_boczne(P, przes_P, przes_n6):
    """Bryly poza zestawem: odbiornik USB w korpusie P, magnesy B i C w plytce n6 (R47)."""
    zb = {}
    z_pi = P['floor_t'] + P['pi_standoff_h']
    x0 = P['pi_pos_x'] + P['pi_l']
    yc = P['pi_pos_y'] + P['pi_w'] / 2
    zb['proxy_odbiornik_usb'] = bm_przesun(bm_prostopadloscian(x0, x0 + P['receiver_l'], yc - P['receiver_w'] / 2, yc + P['receiver_w'] / 2,
                                                               z_pi, z_pi + P['receiver_h']), przes_P)
    m = P['plate_size'] / 2 - P['marker_offset']
    z_spod = -P['plate_thickness']
    zm = z_spod + P['magnet_pocket_depth'] - P['magnet_h']
    zb['proxy_magnes_B'] = bm_przesun(bm_walec(P['magnet_d'] / 2, zm, zm + P['magnet_h'], -m, m), przes_n6)
    zb['proxy_magnes_C'] = bm_przesun(bm_walec(P['magnet_d'] / 2, zm, zm + P['magnet_h'], m, m), przes_n6)
    return zb


# ---- male czesci etapu C (R50-3, R50-8): tulejka DC (kolnierz na Z = 0, os Z) i podkladki panelu (plasko, os Z) ----

def zbuduj_tulejke_dc(P, nazwa):
    """Tulejka redukcyjna gniazda DC: kolnierz ø dc_bush_flange_d x dc_bush_flange_t + walec ø dc_bush_outer_d x dc_bush_t,
    otwor ø dc_bush_inner_d przelotowy."""
    ft, fd = P['dc_bush_flange_t'], P['dc_bush_flange_d']
    return zbuduj_z_operacji(nazwa, bm_walec(fd / 2, 0.0, ft),
                             [bm_walec(P['dc_bush_outer_d'] / 2, ft - NADDATEK, ft + P['dc_bush_t'])],
                             [bm_walec(P['dc_bush_inner_d'] / 2, -NADDATEK, ft + P['dc_bush_t'] + NADDATEK)])


def rdzenie_podkladek(P):
    """(rdzen pliku, grubosc): 0.5 -> podkladka_panelu_05, 1 -> _1, 2 -> _2 (nazwy z plan 12.1)."""
    return [('podkladka_panelu_%s' % ('%g' % t).replace('0.', '0').replace('.', ''), t) for t in P['panel_shim_t']]


def zbuduj_podkladke(P, t, nazwa):
    return zbuduj_z_operacji(nazwa, bm_walec(P['panel_shim_d'] / 2, 0.0, t), [],
                             [bm_walec(P['panel_shim_hole_d'] / 2, -NADDATEK, t + NADDATEK)])


# ===========================================================================
# (4) Eksport STL (kopia obrocona do orientacji druku, tabela 1 protokolu)
# ===========================================================================

def M_druk(P, czesc, relief=0.0):
    """Macierz uklad montazowy -> STL (orientacja druku)."""
    if czesc.startswith('plytka'):
        return Matrix.Translation((0, 0, P['plate_thickness']))
    if czesc in ('pokrywka', 'pokrywka_okragla'):
        return Matrix(((1, 0, 0, 0), (0, -1, 0, 0), (0, 0, -1, 0), (0, 0, 0, 1)))   # 180 st. wokol X; wierzch pelny na Z = 0 (R50-U14); R58: okragla tak samo
    if czesc in ('wkladka', 'wkladka_okragla'):
        return Matrix.Translation((0, 0, P['tab_pin_h']))           # STL lezy na koncach kolkow (R58: wkladka okragla tak samo)
    if czesc in ('korpus', 'tulejka_dc') or czesc.startswith('podkladka_panelu'):
        return Matrix.Identity(4)                                    # tulejka: kolnierz na Z = 0; podkladki plasko
    if czesc == 'blat':
        return Matrix(((1, 0, 0, 0), (0, -1, 0, 0), (0, 0, -1, 0), (0, 0, 0, 1)))   # dokladnie 180 st. wokol X
    raise BladProjektu('brak transformacji druku dla %s' % czesc)


def stl_kanoniczny(sciezka, zero_dodatnie=False):
    """Jednoznaczna kolejnosc trojkatow w pliku STL (powtarzalnosc SHA, K-59). Boolean EXACT liczy
    wielowatkowo i zwraca te sama geometrie w roznej kolejnosci; trojkaty zapisane przez eksporter
    Blendera sa tylko przestawiane (kazdy obrocony tak, by zaczynal sie od najmniejszego wierzcholka,
    z zachowaniem kierunku obiegu), geometria i triangulacja eksportera bez zmian."""
    import struct
    # R58: zero_dodatnie=True (tylko pliki --etap R58) zapisuje -0,0 jako +0,0 (normalne i wierzcholki) - znak zera w normalnych eksportera
    # zmienia sie miedzy przebiegami (ramka_wkladka_v2, do_v3 #9; ramka_wkladka_okragla_v2 tak samo); pliki etapow A-C bez zmian (domyslnie False)
    with open(sciezka, 'rb') as f:
        dane = f.read()
    n = struct.unpack_from('<I', dane, 80)[0]
    if len(dane) != 84 + 50 * n:
        raise BladProjektu('STL %s: rozmiar niezgodny z liczba trojkatow' % sciezka)
    rek = []
    for i in range(n):
        v = struct.unpack_from('<12fH', dane, 84 + 50 * i)
        w = [v[3:6], v[6:9], v[9:12]]
        k = w.index(min(w))
        w = w[k:] + w[:k]
        rek.append((w, v[0:3]))
    rek.sort()
    wyj = bytearray(dane[:84])
    for w, nrm in rek:
        liczby = tuple(nrm) + w[0] + w[1] + w[2]
        if zero_dodatnie:
            liczby = tuple(x + 0.0 for x in liczby)          # -0,0 + 0,0 = +0,0 (IEEE 754); inne wartosci bez zmian
        wyj += struct.pack('<12fH', *(liczby + (0,)))
    with open(sciezka, 'wb') as f:
        f.write(bytes(wyj))


def eksportuj_stl(ob, sciezka, M, zero_dodatnie=False):
    me = ob.data.copy()
    me.transform(M)
    # triangulacja BEAUTY: eksporter STL tnie wielokaty z wierzcholkami wspolliniowymi (mostki EXACT)
    # na trojkaty o zerowym polu, ktore K-03 widzi jako stykajace sie trojkaty
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="BEAUTY", ngon_method="BEAUTY")
    # trojkaty o zerowym polu (3 wierzcholki wspolliniowe, np. krawedz szczeliny pod daszkiem):
    # obrot najdluzszej krawedzi daje dwa poprawne trojkaty
    for _ in range(10):
        zdeg = [f for f in bm.faces if f.calc_area() < POLE_ZDEG]
        if not zdeg:
            break
        kraw = set()
        for f in zdeg:
            e = max(f.edges, key=lambda e: e.calc_length())
            if len(e.link_faces) == 2:
                kraw.add(e)
        if not kraw:
            break
        bmesh.ops.rotate_edges(bm, edges=list(kraw), use_ccw=False)
    bm.to_mesh(me)
    bm.free()
    tmp = bpy.data.objects.new(os.path.splitext(os.path.basename(sciezka))[0], me)
    bpy.context.scene.collection.objects.link(tmp)
    for o in bpy.context.scene.objects:
        if o is not None:
            o.select_set(False)
    tmp.select_set(True)
    bpy.context.view_layer.objects.active = tmp
    bpy.ops.wm.stl_export(filepath=sciezka, check_existing=False, export_selected_objects=True,
                          global_scale=1.0, use_scene_unit=False, ascii_format=False, apply_modifiers=True,
                          forward_axis='Y', up_axis='Z')
    usun_obiekt(tmp)
    stl_kanoniczny(sciezka, zero_dodatnie)
    log('eksport', os.path.basename(sciezka))


# ===========================================================================
# (5) Sprawdzenia na STL wczytanym z powrotem
# ===========================================================================

KIERUNKI = [Vector((1.0, 0.00131, 0.00071)).normalized(),
            Vector((0.00113, 1.0, 0.00171)).normalized(),
            Vector((0.00191, 0.00053, 1.0)).normalized()]


class Siatka:
    """STL wczytany z dysku, przeksztalcony do ukladu montazowego."""

    def __init__(self, sciezka, M_montaz):
        self.sciezka = sciezka
        przed = set(bpy.data.objects)
        bpy.ops.wm.stl_import(filepath=sciezka, global_scale=1.0, use_scene_unit=False,
                              forward_axis='Y', up_axis='Z')
        nowe = [o for o in bpy.data.objects if o not in przed]
        if len(nowe) != 1:
            raise BladProjektu('import %s: %d obiektow' % (sciezka, len(nowe)))
        ob = nowe[0]
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        self.trojkaty_pliku = len(bm.faces)
        self.nan = any(any(math.isnan(c) or math.isinf(c) for c in v.co) for v in bm.verts)
        self.bbox_stl = self._bbox(bm)
        bmesh.ops.transform(bm, matrix=M_montaz, verts=bm.verts[:])
        bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=SPAW_IMPORT)
        bm.verts.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        self.bm = bm
        self.bvh = BVHTree.FromBMesh(bm)
        self.bbox = self._bbox(bm)
        usun_obiekt(ob)

    @staticmethod
    def _bbox(bm):
        xs = [v.co.x for v in bm.verts]
        ys = [v.co.y for v in bm.verts]
        zs = [v.co.z for v in bm.verts]
        return (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))

    def zwolnij(self):
        self.bm.free()

    # -- K-03 / K-04 / K-04b --
    def manifold(self):
        zle_krawedzie = sum(1 for e in self.bm.edges if len(e.link_faces) != 2)
        luzne = sum(1 for v in self.bm.verts if not v.link_faces)
        wierz = [frozenset(v.index for v in f.verts) for f in self.bm.faces]
        pary = self.bvh.overlap(self.bvh)
        przeciecia = 0
        for i, j in pary:
            if i != j and not (wierz[i] & wierz[j]):
                przeciecia += 1
        self.zdegenerowane = sum(1 for f in self.bm.faces if f.calc_area() < POLE_ZDEG)
        return zle_krawedzie, luzne, przeciecia

    def skladowe(self):
        rodzic = list(range(len(self.bm.verts)))

        def znajdz(i):
            while rodzic[i] != i:
                rodzic[i] = rodzic[rodzic[i]]
                i = rodzic[i]
            return i
        for e in self.bm.edges:
            a, b = znajdz(e.verts[0].index), znajdz(e.verts[1].index)
            if a != b:
                rodzic[a] = b
        return len({znajdz(f.verts[0].index) for f in self.bm.faces})

    def objetosc_cm3(self):
        s = 0.0
        for f in self.bm.faces:
            vs = [v.co for v in f.verts]
            for k in range(1, len(vs) - 1):
                s += vs[0].dot(vs[k].cross(vs[k + 1]))
        return s / 6.0 / 1000.0

    # -- sondy --
    def _przeciecia(self, p, d):
        n = 0
        o = p.copy()
        for _ in range(100000):
            loc, _nor, _i, _dist = self.bvh.ray_cast(o, d)
            if loc is None:
                break
            n += 1
            o = loc + d * KROK_PROMIENIA
        return n

    def w_bryle(self, p):
        p = Vector(p)
        glosy = sum(self._przeciecia(p, d) % 2 for d in KIERUNKI)
        return glosy >= 2, glosy

    def odleglosc(self, p):
        loc, _n, _i, d = self.bvh.find_nearest(Vector(p))
        return d

    def max_z_w_obszarze(self, x0, x1, y0, y1):
        zs = [v.co.z for v in self.bm.verts if x0 <= v.co.x <= x1 and y0 <= v.co.y <= y1]
        return max(zs) if zs else None

    def mapa_wysokosci(self, x0, x1, y0, y1, krok, z_start, pomin=None):
        """Promienie z gory (-Z) na siatce; zwraca macierz wysokosci (None = brak trafienia)."""
        nx = int(round((x1 - x0) / krok)) + 1
        ny = int(round((y1 - y0) / krok)) + 1
        mapa = []
        for j in range(ny):
            wiersz = []
            for i in range(nx):
                x, y = x0 + i * krok, y0 + j * krok
                if pomin and pomin(x, y):
                    wiersz.append(None)
                    continue
                loc, _n, _i, _d = self.bvh.ray_cast(Vector((x, y, z_start)), Vector((0, 0, -1)))
                wiersz.append(loc.z if loc is not None else None)
            mapa.append(wiersz)
        return mapa


def zapisz_png(sciezka, mapa, z_lo, z_hi):
    """Mapa wysokosci -> PNG w skali szarosci (biale = z_hi, czarne = z_lo, czerwone = brak trafienia)."""
    ny, nx = len(mapa), len(mapa[0])
    img = bpy.data.images.new('rzut', width=nx, height=ny, alpha=False)
    px = []
    for wiersz in mapa:
        for z in wiersz:
            if z is None:
                px += [1.0, 0.0, 0.0, 1.0]
            else:
                t = max(0.0, min(1.0, (z - z_lo) / (z_hi - z_lo)))
                px += [t, t, t, 1.0]
    img.pixels = px
    img.filepath_raw = sciezka
    img.file_format = 'PNG'
    img.save()
    bpy.data.images.remove(img)


class Wyniki:
    """Zbior wynikow K-xx i sond."""

    def __init__(self):
        self.k = {}        # id -> dict(wynik, zmierzone, oczekiwane, uwaga, waga)
        self.sondy = []    # (K, plik, punkt, oczekiwane, wynik, glosy, odleglosc)

    def dodaj(self, kid, ok, zmierzone, oczekiwane, waga, uwaga=''):
        if kid in self.k:
            st = self.k[kid]
            st['ok'] = st['ok'] and ok
            st['zmierzone'].append(zmierzone)
            if uwaga:
                st['uwaga'].append(uwaga)
        else:
            self.k[kid] = {'ok': ok, 'zmierzone': [zmierzone], 'oczekiwane': oczekiwane, 'waga': waga,
                           'uwaga': [uwaga] if uwaga else [], 'nd': False}

    def nd(self, kid, oczekiwane, waga, uwaga):
        self.k[kid] = {'ok': True, 'zmierzone': ['—'], 'oczekiwane': oczekiwane, 'waga': waga, 'uwaga': [uwaga], 'nd': True}

    def sondy_k(self, kid, siatka, plik, lista):
        """lista: [(punkt, True=W BRYLE / False=POZA)]; zwraca (zgodne, wszystkie, blisko)."""
        zg = 0
        blisko = 0
        for p, ocz in lista:
            w, glosy = siatka.w_bryle(p)
            d = siatka.odleglosc(p)
            if d < SONDA_BLISKO - 1e-4:
                blisko += 1
            if w == ocz:
                zg += 1
            self.sondy.append((kid, plik, p, ocz, w, glosy, d))
        return zg, len(lista), blisko


def ogolne_stl(W, plik, siatka, oczek_gab, oczek_zakres, klucz_obj):
    """K-01 ... K-04b dla jednego STL."""
    ok1 = siatka.trojkaty_pliku > 100 and not siatka.nan
    W.dodaj('K-01', ok1, '%s: %d trójkątów, NaN: %s' % (plik, siatka.trojkaty_pliku, 'tak' if siatka.nan else 'nie'), '> 100, bez NaN', 'B')
    bb = siatka.bbox
    gab = (bb[1] - bb[0], bb[3] - bb[2], bb[5] - bb[4])
    ok2 = all(abs(a - b) <= TOL_WYM for a, b in zip(gab, oczek_gab))
    ok2z = all(abs(a - b) <= TOL_WYM for a, b in zip(bb, oczek_zakres))
    W.dodaj('K-02', ok2 and ok2z, '%s: %.3f × %.3f × %.3f; X %.3f…%.3f, Y %.3f…%.3f, Z %.3f…%.3f' % ((plik,) + gab + bb),
            'tabela 1 ± 0,1', 'B', '' if ok2z else '%s: położenie bbox poza oczekiwanym zakresem %s' % (plik, oczek_zakres))
    zk, lz, prz = siatka.manifold()
    W.dodaj('K-03', zk == 0 and lz == 0 and prz == 0, '%s: %d / %d / %d (trójkąty o polu < 1e-6 mm²: %d)' % (plik, zk, lz, prz, siatka.zdegenerowane), '0 / 0 / 0', 'B')
    sk = siatka.skladowe()
    W.dodaj('K-04', sk == 1, '%s: %d' % (plik, sk), '1', 'B')
    obj = siatka.objetosc_cm3()
    ref = OBJ_ORIENT[klucz_obj]
    ok = obj > 0 and 0.7 * ref <= obj <= 1.3 * ref
    W.dodaj('K-04b', ok, '%s: %.2f cm³ (orient. %d → %.1f…%.1f)' % (plik, obj, ref, 0.7 * ref, 1.3 * ref), 'objętość > 0 i orient. z tab. 1 ± 30 %', 'B')
    return obj, gab


# ---- sprawdzenia plytek (K-05 ... K-16) ----

def odl_punkt_odcinek(p, a, b):
    ax, ay = a
    bx, by = b
    px, py = p
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def ksztalt(g):
    """(odcinek osi, promien) obrysu gornego: okrag = odcinek zerowy."""
    if g['type'] == 'round':
        return ((g['x'], g['y']), (g['x'], g['y'])), g['d_top'] / 2
    a = g['l'] / 2 - g['w'] / 2
    c, s = math.cos(math.radians(g['angle'])), math.sin(math.radians(g['angle']))
    return ((g['x'] - a * c, g['y'] - a * s), (g['x'] + a * c, g['y'] + a * s)), g['w'] / 2


def odl_odcinkow(o1, o2):
    (a, b), (c, d) = o1, o2
    # odcinki w 2D: minimum z odleglosci koncow (brak przeciec dla rozlacznych obrysow)
    return min(odl_punkt_odcinek(a, c, d), odl_punkt_odcinek(b, c, d), odl_punkt_odcinek(c, a, b), odl_punkt_odcinek(d, a, b))


def sprawdz_uklad_json(W, P, uklad, typ, wzorzec=None):
    """K-05 na pliku JSON. R57: okragla — rzedy z typu bazowego; wzorzec = uklad kwadratowy tego typu: 'sockets' musza byc identyczne (h)."""
    g = uklad['sockets']
    plik = 'uklad_gniazd_%s.json' % typ
    baz = typ_bazowy(typ)
    nr = sum(1 for s in g if s['type'] == 'round')
    nt = sum(1 for s in g if s['type'] == 'trough')
    wiersze = P['ev_rows'] if baz == 'wieczorna' else P['mo_rows']     # R54: oczekiwane liczby z parametry.json, nie stale
    oczek = (sum(len(w['x']) for w in wiersze if w['type'] == 'round'), sum(len(w['x']) for w in wiersze if w['type'] == 'trough'))
    bledy = []
    if (nr, nt) != oczek:
        bledy.append('(a) liczba %d/%d (oczekiwane %d/%d z %s_rows)' % (nr, nt, oczek[0], oczek[1], 'ev' if baz == 'wieczorna' else 'mo'))
    if wzorzec is not None and g != wzorzec['sockets']:
        bledy.append('(h) sockets różnią się od uklad_gniazd_%s.json' % baz)
    rzedy = {}
    for s in g:
        rzedy.setdefault(round(s['y'], 6), []).append(s['x'])
    for y, xs in rzedy.items():
        a = sorted(xs)
        b = sorted(-x for x in xs)
        if any(abs(p - q) > 0.01 for p, q in zip(a, b)):
            bledy.append('(b) rząd y=%g niesymetryczny' % y)
    h = P['socket_zone'] / 2
    rk = P['socket_zone_r']                                  # R54: kolo pola skanowania (Z29)
    zn = (P['plate_size'] - 2 * P['plate_corner_zone']) / 2  # 35
    rmax, id_rmax = 0.0, None
    for s in g:
        (a, b), r = ksztalt(s)
        for (x, y) in (a, b):
            if abs(x) + r > h + 1e-6 or abs(y) + r > h + 1e-6:
                bledy.append('(c) id %d poza strefą' % s['id'])
            rr = math.hypot(x, y) + r
            if rr > rmax:
                rmax, id_rmax = rr, s['id']
            if rr > rk + 1e-6:
                bledy.append('(c) id %d poza kołem: %.3f > %g' % (s['id'], rr, rk))
        # (d) kwadraty narozne |x| > zn i |y| > zn
        for i in range(201):
            t = i / 200
            x, y = a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])
            dx, dy = max(zn - abs(x), 0.0), max(zn - abs(y), 0.0)
            if math.hypot(dx, dy) < r - 1e-6:
                bledy.append('(d) id %d w narożniku' % s['id'])
                break
    dmin = 1e9
    para = None
    for i in range(len(g)):
        for j in range(i + 1, len(g)):
            o1, r1 = ksztalt(g[i])
            o2, r2 = ksztalt(g[j])
            d = odl_odcinkow(o1, o2) - r1 - r2
            if d < dmin:
                dmin, para = d, (g[i]['id'], g[j]['id'])
    if dmin < P['socket_wall_min'] - 1e-6:
        bledy.append('(e) ścianka %.3f < %.1f (id %s)' % (dmin, P['socket_wall_min'], para))
    t = math.tan(math.radians(P['socket_wall_angle']))
    for s in g:
        if s['type'] == 'round' and abs(s['d_bottom'] - (s['d_top'] - 2 * s['depth'] * t)) > 0.01:
            bledy.append('(f) id %d d_bottom' % s['id'])
    ids = [s['id'] for s in g]
    if ids != list(range(1, len(g) + 1)):
        bledy.append('(g) id nieciągłe')
    for s1, s2 in zip(g, g[1:]):
        if s2['y'] < s1['y'] - 1e-9 or (abs(s2['y'] - s1['y']) < 1e-9 and s2['x'] >= s1['x']):
            bledy.append('(g) kolejność id %d→%d' % (s1['id'], s2['id']))
    W.dodaj('K-05', not bledy, '%s: round/trough %d/%d (oczekiwane %d/%d z %s_rows); wpisów rzędów (różnych y) %d; max promień obrysu %.3f (id %s) ≤ %g; min ścianka %.3f (id %d–%d)%s; błędy: %s'
            % (plik, nr, nt, oczek[0], oczek[1], 'ev' if baz == 'wieczorna' else 'mo', len(rzedy), rmax, id_rmax, rk, dmin, para[0], para[1],
               '; (h) sockets identyczne z uklad_gniazd_%s.json: %s' % (baz, 'tak' if g == wzorzec['sockets'] else 'NIE') if wzorzec is not None else '',
               '; '.join(bledy) if bledy else 'brak'),
            '(a)–(g) wszystkie; (c) także koło socket_zone_r %g [R54]; okrągłe: (h) sockets = kwadrat tego typu [R57]' % rk, 'B')
    return dmin


def sprawdz_plytke(W, P, siatka, plik, uklad, numer):
    """K-06 ... K-15 na jednej plytce (uklad: srodek wierzchu, Z w dol ujemne).
    R57: plytka okragla (uklad['shape'] == 'round'): K-06...K-09, K-11, K-13 wspolne; zamiast K-10/K-12/K-14/K-15 sprawdzenia K-61, K-62, K-63."""
    T = P['plate_thickness']
    okragla = uklad.get('shape') == 'round'
    # K-06
    lista = []
    for g in uklad['sockets']:
        if g['type'] != 'round':
            continue
        x, y, d = g['x'], g['y'], g['d_top']
        lista += [((x, y, -2), False), ((x, y, -3.9), False), ((x, y, -6), False), ((x + 2.0, y, -6), True),
                  ((x + d / 2 + 1.6, y, -2), True)]
    zg, n, bl = W.sondy_k('K-06', siatka, plik, lista)
    W.dodaj('K-06', zg == n, '%s: %d/%d sond zgodnych' % (plik, zg, n), 'wszystkie', 'B', '%s: %d sond < 0,1 od ściany' % (plik, bl) if bl else '')
    # K-07: po 3 gniazda kazdego rozmiaru
    lista = []
    licz = {}
    for g in uklad['sockets']:
        if g['type'] != 'round':
            continue
        d = g['d_top']
        if licz.get(d, 0) >= 3:
            continue
        licz[d] = licz.get(d, 0) + 1
        rr = (d - 1.07) / 2
        lista += [((g['x'] + rr - 0.15, g['y'], -2), False), ((g['x'] + rr + 0.15, g['y'], -2), True)]
    zg, n, bl = W.sondy_k('K-07', siatka, plik, lista)
    W.dodaj('K-07', zg == n, '%s: %d/%d (rozmiary %s)' % (plik, zg, n, sorted(licz)), 'tak', 'B')
    # K-08
    lista = []
    for g in uklad['sockets']:
        if g['type'] != 'trough':
            continue
        x, y, l, w, pt = g['x'], g['y'], g['l'], g['w'], g['hole_pitch']
        if okragla:
            # R57: narożnik prostokąta (x + l/2 − 0,5, y + w/2 − 0,5) lezy poza kolem o96/98 (promien 48,5); zaokraglony koniec sprawdzany
            # punktem na 45° od srodka polokregu w odleglosci w/2 + 0,6 (w prostokatnym koncu bylby wyciety, w zaokraglonym jest materialem)
            # R59: rynienka jest tylko z przodu (naroznik prostokata lezy juz w obrysie), sonda na 45 st. zostaje - jedna metoda dla okraglych (protokol K-08)
            u = (w / 2 + 0.6) * math.sqrt(0.5)
            narozny = ((x + (l - w) / 2 + u, y + u, -2), True)
        else:
            narozny = ((x + l / 2 - 0.5, y + w / 2 - 0.5, -2), True)
        lista += [((x, y, -2), False), ((x + l / 2 - 1, y, -2), False), ((x - l / 2 + 1, y, -2), False),
                  narozny, ((x + l / 2 + 1.6, y, -2), True),
                  ((x, y, -6), True)]
        for k in (-1.5, -0.5, 0.5, 1.5):
            lista.append(((x + k * pt, y, -6), False))
    zg, n, bl = W.sondy_k('K-08', siatka, plik, lista)
    W.dodaj('K-08', zg == n, '%s: %d/%d%s' % (plik, zg, n, ' (okrągła: zaokrąglony koniec sondą na 45°, w/2 + 0,6 od środka półokręgu [R57])' if okragla else ''), 'tak', 'B')
    # K-09 [R54]: pozycje z 'markers' JSON (= ev_/mo_marker_pos); kontrola odwrotna: dawne rogi (+-42, +-42, -1) W BRYLE
    lista = []
    for m in uklad['markers']:
        x, y = m['x'], m['y']
        lista += [((x, y, -1), False), ((x, y, -3.3), True), ((x + 1.5, y, -1), False), ((x + 2.7, y, -1), True)]
    n_zn = len(lista)
    rogi = [(mp['x'], mp['y']) for mp in uklad['magnet_pockets']] if not okragla else []      # R58: ramkowa ma kieszenie w r 45 (K-64), nie dawne rogi
    for x, y in rogi:
        lista.append(((x, y, -1), True))
    zg, n, bl = W.sondy_k('K-09', siatka, plik, lista)
    W.dodaj('K-09', zg == n, '%s: %d/%d (znaczniki %s: %d sond; %s)'
            % (plik, zg, n, ', '.join('%s (%g, %g)' % (m['corner'], m['x'], m['y']) for m in uklad['markers']), n_zn,
               'kontrola odwrotna dawnych rogów %s na Z −1: %d sond W' % (', '.join('(%g, %g)' % r for r in rogi), len(rogi)) if rogi
               else 'okrągła: dawne rogi (±42, ±42) poza obrysem ø%g — kontrola odwrotna bezprzedmiotowa [R57]' % uklad['d']),
            'tak; kwadrat: dawne rogi W BRYLE', 'B')
    if not okragla:
        # K-10
        lista = [((45.5, -45.0, -4), False), ((45.5, -45.0, -7.9), False), ((41.5, -45.0, -4), True), ((45.5, -41.5, -4), True)]
        zg, n, bl = W.sondy_k('K-10', siatka, plik, lista)
        W.dodaj('K-10', zg == n, '%s: %d/%d' % (plik, zg, n), 'tak', 'B')
    # K-11 [R57: 4 bity A, B, C, D; bazowy = wszystkie dolki]
    b = bity(numer)
    lista = []
    for dl in uklad['code_dimples']:
        lista.append(((dl['x'], dl['y'], -0.5), not b[dl['bit']]))
        if numer is None:
            lista.append(((dl['x'], dl['y'], -1.3), True))
    zg, n, bl = W.sondy_k('K-11', siatka, plik, lista)
    obecne = []
    for dl in uklad['code_dimples']:
        if not siatka.w_bryle((dl['x'], dl['y'], -0.5))[0]:
            obecne.append(dl['bit'])
    W.dodaj('K-11', zg == n, '%s: %d/%d; dołki zmierzone: %s (oczekiwane %s)' % (plik, zg, n, '+'.join(obecne) or 'brak', bity_tekst(numer) or 'brak'),
            'bazowy A+B+C+D; n1 A, n2 B, n3 A+B, n4 C, n5 A+C, n6 B+C; okrągłe [R57]: n8 D, n9 A+D', 'B')
    if not okragla:
        # K-12
        lista = []
        for mp in uklad['magnet_pockets']:
            x, y = mp['x'], mp['y']
            lista += [((x, y, -7), False), ((x, y, -5.6), True), ((x + 2.45, y, -7), False), ((x + 2.8, y, -7), True)]
        lista.append(((42, -42, -7), True))
        zg, n, bl = W.sondy_k('K-12', siatka, plik, lista)
        W.dodaj('K-12', zg == n, '%s: %d/%d' % (plik, zg, n), 'tak', 'B')
    # K-13 [R57: okragla — obszar wokol number_relief z JSON; cyfra pominieta (null) -> max Z calej plytki = 0]
    nr = uklad['number_relief']
    if nr is None:
        zmax = siatka.bbox[5]
        oczek, tol, opis_obsz = 0.0, 0.02, 'cała płytka (cyfra pominięta, R57)'
    else:
        zmax = siatka.max_z_w_obszarze(nr['x'] - 3.5, nr['x'] + 3.5, nr['y'] - 3.5, nr['y'] + 3.5)
        if zmax is None or zmax < -0.02:
            # plaska plytka bez cyfry: w obszarze moze nie byc zadnego wierzcholka (trojkaty wierzchu go przykrywaja) -> promienie z gory co 0,5;
            # R58: albo sa tam tylko wierzcholki cech od spodu (koniec rowka klucza plytki ramkowej, Z -5,5) - tez promienie z gory
            mapa = siatka.mapa_wysokosci(nr['x'] - 3.5, nr['x'] + 3.5, nr['y'] - 3.5, nr['y'] + 3.5, 0.5, 5.0)
            trafienia = [z for w in mapa for z in w if z is not None]
            zmax = max(trafienia) if trafienia else None
        oczek = 0.0 if numer is None else P['number_relief_h']
        tol = 0.02 if numer is None else 0.05
        opis_obsz = 'x %g…%g, y %g…%g' % (nr['x'] - 3.5, nr['x'] + 3.5, nr['y'] - 3.5, nr['y'] + 3.5)
    W.dodaj('K-13', zmax is not None and abs(zmax - oczek) <= tol, '%s: max Z = %.3f (%s)' % (plik, zmax, opis_obsz),
            'bazowy 0,00 ± 0,02; warianty 0,60 ± 0,05 (okrągła bez cyfry: 0,00 ± 0,02)', 'B')
    if okragla:
        sprawdz_okragla(W, P, siatka, plik, uklad, numer, obecne)
        return
    # K-14 na 4 bokach
    lista = []
    for kat in (0, 90, 180, 270):
        c, s = round(math.cos(math.radians(kat))), round(math.sin(math.radians(kat)))
        for (u, z, ocz) in ((47.5, -2, False), (46.9, -2, True), (47.5, -0.8, True), (47.5, -3.2, True)):
            lista.append(((u * c, u * s, z), ocz))
    zg, n, bl = W.sondy_k('K-14', siatka, plik, lista)
    W.dodaj('K-14', zg == n, '%s: %d/%d' % (plik, zg, n), 'tak', 'B')
    # K-15
    lista = [((47.8, 47.8, -4), False), ((47.9, 0, -0.05), False), ((47.9, 0, -1), True)]
    zg, n, bl = W.sondy_k('K-15', siatka, plik, lista)
    W.dodaj('K-15', zg == n, '%s: %d/%d' % (plik, zg, n), 'tak', 'D', '%s: %d sond < 0,1 od ściany' % (plik, bl) if bl else '')


def sprawdz_scianki_naroznikow(W, P, uklad, typ):
    """K-16: rachunek 4.11 z JSON i parametrow. [R54] dodatkowo dla kazdego znacznika: promien srodka <= socket_zone_r - d/2,
    znacznik-gniazdo >= 3, znacznik-dolek >= 1,5, znacznik-kieszen magnesu (XY) >= 1,5; dawne 'stozek-kieszen magnesu (Z)' usuniete (Z4 uchylone)."""
    okragla = uklad.get('shape') == 'round'
    S = P['plate_size'] / 2
    dl = uklad['code_dimples']
    zn = uklad['markers']
    wyniki = []
    rd = dl[0]['d'] / 2
    if okragla:
        # R57: odleglosc do obrysu = min(okrag R, sciecie): R - hypot - r; dist - rzut na kierunek sciecia - r
        R = uklad['d'] / 2
        fl = uklad['flat']
        c, s = math.cos(math.radians(fl['angle_deg'])), math.sin(math.radians(fl['angle_deg']))
        do_kraw = lambda x, y, r: min(R - math.hypot(x, y), fl['dist'] - (x * c + y * s)) - r
        wyniki.append(('dołek–krawędź płytki (okrąg/ścięcie)', min(do_kraw(d['x'], d['y'], rd) for d in dl), 1.5))
        # R57: obrys gorny gniazda/rynienki do krawedzi okraglej (okrag i sciecie): dla obu koncow osi obrysu
        wg_kr, id_kr = 1e9, None
        for g in uklad['sockets']:
            (a, b), r = ksztalt(g)
            for (x, y) in (a, b):
                v = do_kraw(x, y, r)
                if v < wg_kr:
                    wg_kr, id_kr = v, g['id']
        wyniki.append(('gniazdo/rynienka–krawędź płytki (id %s; do ściany pionowej, faza %g wyżej o tyle płycej)' % (id_kr, P['plate_top_chamfer']), wg_kr, 1.5))
    else:
        do_kraw = lambda x, y, r: S - max(abs(x), abs(y)) - r
        wyniki.append(('dołek–krawędź płytki', min(S - abs(d['x']) - rd for d in dl), 1.5))
    wyniki.append(('dołek–znacznik', min(math.hypot(d['x'] - m['x'], d['y'] - m['y']) - rd - m['d'] / 2 for d in dl for m in zn), 1.5))
    dmin = 1e9
    for d in dl:
        for g in uklad['sockets']:
            (a, b), r = ksztalt(g)
            dmin = min(dmin, odl_punkt_odcinek((d['x'], d['y']), a, b) - r - rd)
    wyniki.append(('dołek–gniazdo', dmin, 3.0))
    wyniki.append(('stożek znacznika–krawędź', min(do_kraw(m['x'], m['y'], m['d'] / 2) for m in zn), 1.5))
    if not okragla:
        wyniki.append(('kieszeń magnesu–krawędź', min(S - max(abs(m['x']), abs(m['y'])) - m['d'] / 2 for m in uklad['magnet_pockets']), 1.5))
    # [R54] znaczniki w kole gniazd
    rk = P['socket_zone_r']
    per = []
    for m in zn:
        rr = math.hypot(m['x'], m['y'])
        wg, id_g = 1e9, None
        for g in uklad['sockets']:
            (a, b), r = ksztalt(g)
            d = odl_punkt_odcinek((m['x'], m['y']), a, b) - r - m['d'] / 2
            if d < wg:
                wg, id_g = d, g['id']
        wm = min([math.hypot(m['x'] - mp['x'], m['y'] - mp['y']) - mp['d'] / 2 - m['d'] / 2 for mp in uklad['magnet_pockets']] or [float('inf')])
        per.append((m['corner'], rr, wg, id_g, wm))
    wyniki.append(('promień znacznika (max)', -max(rr for _c, rr, _w, _i, _m in per), -(rk - zn[0]['d'] / 2)))   # ujemnie: v >= lim <=> rr <= rk - d/2
    wyniki.append(('znacznik–gniazdo', min(wg for _c, _r, wg, _i, _m in per), P['socket_wall_min']))
    if not okragla:
        wyniki.append(('znacznik–kieszeń magnesu (XY)', min(wm for _c, _r, _w, _i, wm in per), 1.5))
    ok = all(v >= lim - 1e-6 for _, v, lim in wyniki)
    info = []
    info.append('znaczniki: ' + '; '.join('%s (%g, %g) promień %.2f ≤ %.1f, do gniazda %.2f (id %s)%s'
                                          % (c, m['x'], m['y'], rr, rk - m['d'] / 2, wg, ig, '' if okragla else ', do kieszeni magnesu %.2f' % wm)
                                          for (c, rr, wg, ig, wm), m in zip(per, zn)))
    dd = min(math.hypot(a['x'] - b['x'], a['y'] - b['y']) - 2 * rd for a in dl for b in dl if a['bit'] < b['bit'])
    info.append('dołek–dołek min %.2f (ø%.1f; ścianka 1 mm głęb., informacyjnie)' % (dd, 2 * rd))
    if okragla:
        if uklad.get('key_slot'):
            info.append('okrągła ramkowa [R58]: kieszenie magnesów, rowek pokrywki i rowek klucza — ścianki w K‑64; ścięcie: cięciwa %g na kierunku %g°, odległość od środka %.3f' % (fl['chord_w'], fl['angle_deg'], fl['dist']))
        else:
            info.append('okrągła: bez kieszeni magnesów i rowka pokrywki (R57); ścięcie: cięciwa %g na kierunku %g°, odległość od środka %.3f' % (fl['chord_w'], fl['angle_deg'], fl['dist']))
    else:
        gr = S - P['cover_groove_depth']
        dz = P['cover_groove_z'] - P['cover_groove_w'] / 2 - dl[0]['depth']
        dx = gr - (max(abs(d['x']) for d in dl) + rd)
        info.append('dołek–rowek pokrywki: w poziomie %.2f, w pionie %.2f, po przekątnej %.2f (R47: 1,3 lokalnie)' % (dx, dz, math.hypot(dx, dz)))
    W.dodaj('K-16', ok, '%s: ' % typ + '; '.join(('%s %.2f (≤ %.1f)' % (n, -v, -l)) if l < 0 else ('%s %.2f (≥ %.1f)' % (n, v, l)) for n, v, l in wyniki),
            '≥ 1,5 / ≥ 3,0 / promień znacznika ≤ socket_zone_r − d/2 [R54]; okrągła: krawędź = okrąg i ścięcie [R57]', 'B', '%s: ' % typ + '; '.join(info))


# ---- sprawdzenia plytki okraglej (K-61 ... K-63, R57) ----

def sprawdz_okragla(W, P, siatka, plik, uklad, numer, bity_zmierzone):
    """K-61 obrys okragly (promien z sond promieniowych +-0,05, sciecie w zadanym miejscu, faza wierzchu);
    K-62 dolki kodu w polu (promien <= socket_zone_r - socket_wall_min, odleglosci, bity = numer);
    K-63 brak kieszeni magnesow i rowka pokrywki, spod plaski na Z = -T."""
    T = P['plate_thickness']
    R = uklad['d'] / 2
    fl = uklad['flat']
    kat = fl['angle_deg']
    f = P['plate_top_chamfer']
    pol = asin_st = math.degrees(math.asin(fl['chord_w'] / 2 / R))      # polowa kata sciecia

    def promien_w_kierunku(kat_st, z):
        """Odleglosc od osi do pierwszego trafienia promienia biegnacego z zewnatrz do srodka na wysokosci z."""
        c, s = math.cos(math.radians(kat_st)), math.sin(math.radians(kat_st))
        start = Vector((c * (R + 5), s * (R + 5), z))
        loc = pierwsze_trafienie(siatka.bvh, start, Vector((-c, -s, 0)))
        return None if loc is None else loc.x * c + loc.y * s
    # K-61 (a): promien na 36 kierunkach poza sektorem sciecia, na Z -4 i -7,5
    bledy, info = [], []
    pr = []
    for z in (-4.0, -7.5):
        for i in range(36):
            a = i * 10.0 + 5.0
            if abs(((a - kat) + 180) % 360 - 180) <= pol + 2.0:
                continue
            v = promien_w_kierunku(a, z)
            pr.append(v if v is not None else float('nan'))
    pr_ok = [v for v in pr if not math.isnan(v)]
    if len(pr_ok) != len(pr) or not pr_ok:
        bledy.append('(a) brak trafienia promienia')
    rmin, rmax = (min(pr_ok), max(pr_ok)) if pr_ok else (float('nan'), float('nan'))
    if pr_ok and (abs(rmin - R) > 0.05 or abs(rmax - R) > 0.05):
        bledy.append('(a) promień %.3f…%.3f poza %g ± 0,05' % (rmin, rmax, R))
    info.append('(a) promień z %d sond: %.3f…%.3f (ø %.3f…%.3f)' % (len(pr), rmin, rmax, 2 * rmin, 2 * rmax))
    # (b) sciecie: promien na kierunku kat = dist (+-0,05), na Z -4 i -7,5; 10 st. obok sciecia = R
    ks = uklad.get('key_slot')          # R58: plytka ramkowa - rowek klucza od spodu w osi sciecia
    if ks is None:
        sc = [promien_w_kierunku(kat, z) for z in (-4.0, -7.5)]
    else:
        # na Z -4 w osi; na Z -7,5 (w wysokosci rowka klucza) promienie rownolegle do osi sciecia, odsuniete o +-voff w polowie
        # pasa cieciwy poza rowkiem: trafienie w plaszczyzne sciecia, odleglosc = wspolrzedna wzdluz osi
        voff = (ks['w'] / 2 + fl['chord_w'] / 2) / 2
        cu, su = math.cos(math.radians(kat)), math.sin(math.radians(kat))

        def u_przesuniety(v, z):
            start = Vector((cu * (R + 5) - su * v, su * (R + 5) + cu * v, z))
            loc = pierwsze_trafienie(siatka.bvh, start, Vector((-cu, -su, 0)))
            return None if loc is None else loc.x * cu + loc.y * su
        sc = [u_przesuniety(voff, -4.0), u_przesuniety(-voff, -4.0), u_przesuniety(voff, -7.5), u_przesuniety(-voff, -7.5)]   # runda 2: rowek do Z -3
    ob = [promien_w_kierunku(kat + pol + 3.0, -4.0), promien_w_kierunku(kat - pol - 3.0, -4.0)]
    if any(v is None for v in sc + ob):
        bledy.append('(b) brak trafienia przy ścięciu')
    else:
        if any(abs(v - fl['dist']) > 0.05 for v in sc):
            bledy.append('(b) ścięcie: odległość %s zamiast %.3f' % (', '.join('%.3f' % v for v in sc), fl['dist']))
        if any(abs(v - R) > 0.05 for v in ob):
            bledy.append('(b) obok ścięcia promień %s zamiast %g' % (', '.join('%.3f' % v for v in ob), R))
        if ks is None:
            info.append('(b) ścięcie na kierunku %g°: odległość %.3f / %.3f (zadane %.3f, cięciwa %g); %g° obok: %.3f / %.3f'
                        % (kat, sc[0], sc[1], fl['dist'], fl['chord_w'], pol + 3.0, ob[0], ob[1]))
        else:
            info.append('(b) ścięcie na kierunku %g° (w osi rowek klucza do Z %g) promieniami równoległymi odsuniętymi o ±%.1f: Z −4 %.3f / %.3f, Z −7,5 %.3f / %.3f '
                        '(zadane %.3f, cięciwa %g) [R58]; %g° obok: %.3f / %.3f'
                        % (kat, -T + ks['h'], voff, sc[0], sc[1], sc[2], sc[3], fl['dist'], fl['chord_w'], pol + 3.0, ob[0], ob[1]))
    # (c) faza wierzchu i pelna grubosc: sondy jak K-15 na kierunku 90 st. (z dala od sciecia)
    lista = [((0.0, R - 0.1, -0.05), False), ((0.0, R - f - 0.1, -0.15), True), ((0.0, R - 0.1, -1.0), True),
             ((0.0, R - 0.1, -T + 0.1), True), ((0.0, R + 0.1, -4.0), False)]
    zg, n, bl = W.sondy_k('K-61', siatka, plik, lista)
    if zg != n:
        bledy.append('(c) faza/krawędź: %d/%d sond' % (zg, n))
    bb = siatka.bbox
    if abs(bb[4] + T) > 0.01 or abs(bb[0] + R) > 0.01 or abs(bb[1] - R) > 0.01 or abs(bb[2] + R) > 0.01 or abs(bb[3] - R) > 0.01:
        bledy.append('(d) bbox X %.3f…%.3f Y %.3f…%.3f Z min %.3f' % (bb[0], bb[1], bb[2], bb[3], bb[4]))
    info.append('(c) faza/krawędź %d/%d sond; (d) bbox X %.3f…%.3f, Y %.3f…%.3f, Z %.3f…%.3f' % (zg, n, bb[0], bb[1], bb[2], bb[3], bb[4], bb[5]))
    # (e) glebokosc sciecia z STL (max promien zmierzony − odleglosc sciecia zmierzona) >= round_flat_depth_min;
    # (f) scianka od plaszczyzny sciecia (JSON) do kazdego obrysu gniazda, rynienki, dolka i stozka >= socket_wall_min (decyzja nadzoru 2.11)
    sc_ok = [v for v in sc if v is not None]
    gl = (max(pr_ok) if pr_ok else R) - (min(sc_ok) if sc_ok else fl['dist'])
    if gl < P['round_flat_depth_min'] - 1e-6:
        bledy.append('(e) głębokość ścięcia %.3f < %g' % (gl, P['round_flat_depth_min']))
    c, s = math.cos(math.radians(kat)), math.sin(math.radians(kat))
    obrysy = []
    for g in uklad['sockets']:
        (a, b), r = ksztalt(g)
        for (x, y) in (a, b):
            obrysy.append(('gniazdo id %d' % g['id'], x, y, r))
    obrysy += [('dołek %s' % d['bit'], d['x'], d['y'], d['d'] / 2) for d in uklad['code_dimples']]
    obrysy += [('stożek %s' % m['corner'], m['x'], m['y'], m['d'] / 2) for m in uklad['markers']]
    ws, nazwa_w = min((fl['dist'] - (x * c + y * s) - r, nz) for nz, x, y, r in obrysy)
    if ws < P['socket_wall_min'] - 1e-6:
        bledy.append('(f) ścianka ścięcie–%s %.2f < %g' % (nazwa_w, ws, P['socket_wall_min']))
    info.append('(e) głębokość ścięcia %.3f ≥ %g; (f) ścianka ścięcie–obrysy min %.2f (%s) ≥ %g' % (gl, P['round_flat_depth_min'], ws, nazwa_w, P['socket_wall_min']))
    W.dodaj('K-61', not bledy, '%s: %s; błędy: %s' % (plik, '; '.join(info), '; '.join(bledy) or 'brak'),
            'ø%g ± 0,05 (sondy promieniowe); ścięcie: odległość %.3f ± 0,05 na %g°, głębokość ≥ %g, ścianka do obrysów ≥ %g; faza %g; bbox ±%g, Z −%g'
            % (2 * R, fl['dist'], kat, P['round_flat_depth_min'], P['socket_wall_min'], f, R, T), 'B')
    # K-62: dolki kodu w polu (z JSON) + bity zmierzone (K-11) = numer
    dl = uklad['code_dimples']
    rd = dl[0]['d'] / 2
    rmax_dl = P['socket_zone_r'] - P['socket_wall_min']           # 47 - 3 = 44: srodek dolka w polu z zapasem scianki
    bledy, per = [], []
    c, s = math.cos(math.radians(kat)), math.sin(math.radians(kat))
    for d in dl:
        rr = math.hypot(d['x'], d['y'])
        wg, id_g = 1e9, None
        for g in uklad['sockets']:
            (a, b), r = ksztalt(g)
            v = odl_punkt_odcinek((d['x'], d['y']), a, b) - r - rd
            if v < wg:
                wg, id_g = v, g['id']
        wz = min(math.hypot(d['x'] - m['x'], d['y'] - m['y']) - m['d'] / 2 - rd for m in uklad['markers'])
        wk = min(R - rr, fl['dist'] - (d['x'] * c + d['y'] * s)) - rd
        per.append((d['bit'], d['x'], d['y'], rr, wg, id_g, wz, wk))
        if rr > rmax_dl + 1e-6:
            bledy.append('%s promień %.2f > %g' % (d['bit'], rr, rmax_dl))
        if wg < P['socket_wall_min'] - 1e-6:
            bledy.append('%s do gniazda %.2f < %g' % (d['bit'], wg, P['socket_wall_min']))
        if wz < 1.5 - 1e-6:
            bledy.append('%s do znacznika %.2f < 1,5' % (d['bit'], wz))
        if wk < 1.5 - 1e-6:
            bledy.append('%s do krawędzi %.2f < 1,5' % (d['bit'], wk))
    oczek = bity_tekst(numer)
    zm = '+'.join(bity_zmierzone)
    if zm != oczek:
        bledy.append('bity w STL %s ≠ %s (n%s)' % (zm or 'brak', oczek or 'brak', numer if numer is not None else ' bazowy'))
    W.dodaj('K-62', not bledy, '%s: %s; bity w STL %s = oczekiwane %s (n%s); błędy: %s'
            % (plik, '; '.join('%s (%g, %g) promień %.2f, do gniazda %.2f (id %s), do znacznika %.2f, do krawędzi %.2f' % p for p in per),
               zm or 'brak', oczek or 'brak', numer if numer is not None else ' bazowy', '; '.join(bledy) or 'brak'),
            'promień środka ≤ socket_zone_r − socket_wall_min = %g; do gniazd ≥ %g; do stożków ≥ 1,5; do krawędzi ≥ 1,5; bity = n = A + 2B + 4C + 8D' % (rmax_dl, P['socket_wall_min']), 'B')
    # K-63: spod plaski (wszystkie sciany skierowane w dol leza na Z = -T), bez kieszeni magnesow, bez rowka pokrywki
    if ks is not None:
        return                          # R58: plytka ramkowa - zamiast K-63 sprawdzenie K-64 (sprawdz_ramkowa)
    bledy, info = [], []
    dolne = [fc for fc in siatka.bm.faces if fc.normal.z < -0.9]
    z_dol = [v.co.z for fc in dolne for v in fc.verts]
    zmax_d, zmin_d = (max(z_dol), min(z_dol)) if z_dol else (float('nan'), float('nan'))
    if not z_dol or abs(zmax_d + T) > 0.01 or abs(zmin_d + T) > 0.01:
        bledy.append('ściany skierowane w dół na Z %.3f…%.3f (oczekiwane −%g)' % (zmin_d, zmax_d, T))
    info.append('%d ścian skierowanych w dół (n_z < −0,9), Z %.3f…%.3f' % (len(dolne), zmin_d, zmax_d))
    lista = []
    for i in range(12):
        a = math.radians(i * 30.0 + 15.0)
        lista += [((45.5 * math.cos(a), 45.5 * math.sin(a), -7.0), True), ((45.5 * math.cos(a), 45.5 * math.sin(a), -T + 0.1), True)]
    for a_st in (0.0, 90.0, 180.0):      # rowek pokrywki kwadratu lezy na Z -gz (R57: brak); kierunki z dala od sciecia
        a = math.radians(a_st)
        lista.append((((R - 0.5) * math.cos(a), (R - 0.5) * math.sin(a), -P['cover_groove_z']), True))
    zg, n, bl = W.sondy_k('K-63', siatka, plik, lista)
    if zg != n:
        bledy.append('sondy kieszeni/rowka %d/%d' % (zg, n))
    info.append('sondy od spodu (r 45,5, Z −7 i −%.1f) i w miejscu rowka (r %.1f, Z −%g): %d/%d W BRYLE' % (T - 0.1, R - 0.5, P['cover_groove_z'], zg, n))
    W.dodaj('K-63', not bledy, '%s: %s; błędy: %s' % (plik, '; '.join(info), '; '.join(bledy) or 'brak'),
            'spód płaski na Z = −%g (± 0,01); bez kieszeni magnesów; bez rowka pokrywki' % T, 'B')


# ---- sprawdzenia pokrywki (K-17 ... K-22) ----

def sprawdz_pokrywke(W, P, siatka, plik, katalog_rzutow, iter_):
    # K-17 z kontrola odwrotna K-19 (R50-U17: wierzch pelny w miejscach dawnych otworow) i K-21 (R50-U14: wierzch plaski 0,00)
    lista = [((0, 0, -1), True), ((0, 0, -2.5), False), ((48.1, 0, -10), False), ((48.5, 0, -10), True),
             ((50, 0, -10), False), ((0, 0, -19.9), False)]
    kontrola19 = [((15, 0, -1), True), ((15, 30, -1), True), ((-15, -30, -1), True)]
    zg, n, bl = W.sondy_k('K-17', siatka, plik, lista)
    zg19, n19, _bl = W.sondy_k('K-17', siatka, plik, kontrola19)
    mapa = siatka.mapa_wysokosci(-40, 40, -40, 40, 0.5, 5.0)
    zs = [z for w in mapa for z in w if z is not None]
    zmax, zmin = max(zs), min(zs)
    ok21 = abs(zmax) <= 0.02 and abs(zmin) <= 0.02 and len(zs) == len(mapa) * len(mapa[0])
    W.dodaj('K-17', zg == n and zg19 == n19 and ok21, '%s: %d/%d; kontrola K‑19 (dawne otwory) %d/%d W; kontrola K‑21: wierzch z promieni '
            '(|x|, |y| ≤ 40, krok 0,5, %d punktów) Z %.3f…%.3f' % (plik, zg, n, zg19, n19, len(zs), zmin, zmax),
            'tak; kontrola K‑19 W; wierzch 0,00 ± 0,02', 'B')
    lista = [((47.8, 0, -18), True), ((47.8, 20, -18), False), ((-47.8, 0, -18), True), ((25, -47.8, -18), True),
             ((0, -47.8, -18), False), ((-25, 47.8, -18), True), ((25, 47.8, -18), False), ((47.8, 0, -16.5), False)]
    zg, n, bl = W.sondy_k('K-18', siatka, plik, lista)
    W.dodaj('K-18', zg == n, '%s: %d/%d' % (plik, zg, n), 'tak', 'B')
    W.nd('K-19', '—', 'P', 'uchylone R50‑U17 (pokrywka bez otworów); kontrola odwrotna w K‑17: %d/%d sond W' % (zg19, n19))
    lista = [((0, -49, -19), False), ((20, -49, -19), True), ((0, 49, -19), False), ((0, -49, -16), True)]
    zg, n, bl = W.sondy_k('K-20', siatka, plik, lista)
    W.dodaj('K-20', zg == n, '%s: %d/%d' % (plik, zg, n), 'tak', 'P')
    W.nd('K-21', '—', 'D', 'uchylone R50‑U14 (bez napisu GÓRA); kontrola odwrotna w K‑17: max Z wierzchu %.3f' % zmax)
    # K-22
    a = siatka.w_bryle((48.1, 0, -10))[0]
    b = siatka.w_bryle((48.5, 0, -10))[0]
    W.dodaj('K-22', (not a) and b, '%s: (48,1) %s, (48,5) %s → wnęka 96,6 ± 0,2' % (plik, 'W' if a else 'POZA', 'W' if b else 'POZA'),
            '48,1 POZA / 48,5 W', 'B', 'część złożeniowa (pokrywka–wkładka, K-53) N/D w etapie A')


def rzut_cyfry(P, siatka, plik, katalog_rzutow, iter_, nr=None):
    """Rzut XY reliefu cyfry (K-13). R57: obszar wokol number_relief z JSON (nr), domyslnie dawny obszar kwadratu (39,5; -44,5) +- 3,5."""
    os.makedirs(katalog_rzutow, exist_ok=True)
    cx, cy = (nr['x'], nr['y']) if nr else (39.5, -44.5)
    mapa = siatka.mapa_wysokosci(cx - 3.5, cx + 3.5, cy - 3.5, cy + 3.5, 0.05, 5.0)
    png = os.path.join(katalog_rzutow, 'rzut_%s_%s.png' % (os.path.splitext(plik)[0], iter_))
    zapisz_png(png, mapa, 0.0, P['number_relief_h'])
    return png


# ---- sprawdzenia etapu B (K-23 ... K-49) ----

def _sondy(W, kid, siatka, plik, lista, waga, opis=''):
    zg, n, bl = W.sondy_k(kid, siatka, plik, lista)
    W.dodaj(kid, zg == n, '%s: %d/%d%s' % (plik, zg, n, opis), 'tak', waga, '%s: %d sond < 0,1 od ściany' % (plik, bl) if bl else '')


def pierwsze_trafienie(bvh, o, d):
    loc, _n, _i, _dd = bvh.ray_cast(Vector(o), Vector(d))
    return loc


# Sondy K-29 (uszy, nasady, kolki, otwory magnesow, kanaly pod uszami) i K-30 (rowek kablowy): wspolne dla wkladki kwadratowej
# i okraglej (R58, K-65: obrys zewnetrzny, uszy, kolki i magnesy jak kwadratowa); listy bez zmian wzgledem R59
SONDY_K29 = [((58, 80, 1.5), True), ((58, 80, 4), False), ((-58, 80, 1.5), True), ((47, 55, 1.5), True), ((47, 55, 3.5), False),
             ((62, 55, 1.5), True), ((62, 50, 1.5), False), ((47, 59, 1.5), False), ((56, 55, 0.5), False), ((56, 55, 2), True),
             ((48, 50.5, 0.5), False),
             ((58, 93.5, -2), True), ((58, 93.5, -3.8), False), ((58, 86, 1.5), False), ((58, 89, 1.5), True),
             ((64, 70, 0.5), False), ((64, 70, 2), True), ((64, 89, 0.5), False), ((58, 95.5, 1.5), True), ((58, 96.5, 1.5), False)]
SONDY_K30 = [((51.5, 0, 0.7), False), ((50.2, 0, 0.7), False), ((49.4, 0, 0.7), True), ((51.5, 0, 2.0), True),
             ((-51.5, 0, 0.7), False), ((0, 51.5, 0.7), False), ((20, -51.5, 0.7), True)]


def sprawdz_wkladke(W, P, siatka, plik, katalog_rzutow, iter_):
    # R53 (T6): otwor 96,8 -> sciana 48,4...52,4; sondy 48,2 POZA / 48,6 W / 52,6 POZA (margines 0,2 jak w protokole)
    _sondy(W, 'K-23', siatka, plik, [((48.2, 0, 3), False), ((48.6, 0, 3), True), ((52.6, 0, 3), False), ((48.6, 0, 5.9), False),
                                     ((49.5, 0, 5.9), True), ((0, 0, 3), False)], 'B')
    _sondy(W, 'K-24', siatka, plik, [((-38, -38, 1.5), True), ((-38, -38, 3), False), ((38, 38, 1.5), True), ((-38, 38, 1.5), True),
                                     ((38, -38, 1.5), True), ((-30, -30, 1.5), False), ((-35.5, -35.5, 1.5), False)], 'B')
    _sondy(W, 'K-25', siatka, plik, [((-42, -42, 1.5), False), ((-42, 42, 1.5), False), ((42, 42, 1.5), False), ((42, -42, 1.5), True),
                                     ((-45, -45, 0.5), False), ((-45, -45, 1.8), True), ((-50, -50, 0.7), False), ((-50, -50, 2.2), True),
                                     ((-51.5, -51.5, 0.7), False)], 'B')
    _sondy(W, 'K-27', siatka, plik, [((45.6, -45.6, 5), True), ((45.6, -45.6, 8), False), ((45.6, -45.6, 7.2), True), ((48.15, -45.6, 5), False)], 'B')   # R53: szczelina 47,9...48,4
    _sondy(W, 'K-28', siatka, plik, [((0, -50.3, 3), False), ((0, -50.3, 0.3), False), ((20, -50.3, 3), True), ((-20, -50.3, 3), True)], 'B')
    _sondy(W, 'K-29', siatka, plik, SONDY_K29, 'B')
    _sondy(W, 'K-30', siatka, plik, SONDY_K30, 'P')
    # K-31: mapa wysokosci z gory; pas napisu i pas pod kolnierzem pokrywki
    H = P['insert_h']
    m1 = siatka.mapa_wysokosci(30, 34, -52.3, -50.0, 0.05, 20.0)
    m2 = siatka.mapa_wysokosci(-34, -30, -52.3, -50.0, 0.05, 20.0)
    m3 = siatka.mapa_wysokosci(-40, 42, -49.95, -48.35, 0.05, 20.0, lambda x, y: -P["finger_cut_w"] / 2 - 1 < x < P["finger_cut_w"] / 2 + 1)
    z1 = max(z for w in m1 + m2 for z in w if z is not None)
    z3 = max(z for w in m3 for z in w if z is not None)
    os.makedirs(katalog_rzutow, exist_ok=True)
    png = os.path.join(katalog_rzutow, 'rzut_wkladka_strzalki_%s.png' % iter_)
    zapisz_png(png, siatka.mapa_wysokosci(-42, 42, -52.3, -48.3, 0.05, 20.0), H - 1.0, H + P['label_relief_h'])
    ok = abs(z1 - (H + P['label_relief_h'])) <= 0.05 and abs(z3 - H) <= 0.05
    W.dodaj('K-31', ok, '%s: max w obszarach strzałek %.3f; max w pasie y −49,95…−48,35 %.3f' % (plik, z1, z3),
            '6,6 ± 0,05 / 6,0 ± 0,05; kształt z rzutu PNG', 'P', 'rzut: %s' % os.path.relpath(png, KATALOG).replace('\\', '/'))
    a = siatka.w_bryle((48.2, 0, 3))[0]     # R53 (T6): otwor 96,8
    b = siatka.w_bryle((48.6, 0, 3))[0]
    W.dodaj('K-32', (not a) and b, '%s: (48,2) %s, (48,6) %s → otwór 96,8 ± 0,2 (R53)' % (plik, 'W' if a else 'POZA', 'W' if b else 'POZA'),
            '48,2 POZA / 48,6 W; złożenie płytka–wkładka = 0 (K‑53)', 'B', 'część złożeniowa: K‑53, para wkladka–plytka_wieczorna_n1')


def sprawdz_korpus(W, P, siatka, plik):
    # sondy z protokolu po R50 (K-34...K-44)
    _sondy(W, 'K-34', siatka, plik, [((0, 0, 1.5), True), ((0, 0, 10), False), ((98.75, 0, 20), True), ((96, 0, 20), False), ((0, 98.75, 20), True),
                                     ((99, 99, 20), False), ((0, 0, 59.5), False), ((98.75, 0, 59.4), True), ((98.75, 0, 59.7), False),
                                     ((99.9, 0, 0.3), False)], 'B')
    _sondy(W, 'K-35', siatka, plik, [((60, 60, 1.5), False), ((55, 55, 1.5), False), ((65, 65, 1.5), False), ((-60, 60, 1.5), False),
                                     ((-60, -60, 1.5), False), ((60, -60, 1.5), False), ((52, 52, 1.5), True), ((68, 68, 1.5), True),
                                     ((58, 62, 1.5), True), ((63, 60, 0.5), True), ((-91, 0, 1.5), True), ((-49, 0, 1.5), True),
                                     ((-8, 10, 1.5), False), ((-8, -10, 1.5), False), ((-8, 13, 1.5), True), ((-25, 10, 1.5), True),
                                     ((-60, 10, 1.5), True)], 'B')
    _sondy(W, 'K-36', siatka, plik, [((64, 60, 3.5), True), ((64, 60, 4.5), False), ((-64, 60, 3.5), True), ((64, -60, 3.5), True),
                                     ((-64, -60, 3.5), True), ((53, 53, 3.5), True), ((69, 69, 3.5), False), ((60, 60, 3.5), False),
                                     ((-43.5, -24.5, 6), True), ((-46.5, -24.5, 6), False), ((-46.5, -24.5, 8.5), False), ((14.5, 24.5, 6), True),
                                     ((11.5, 24.5, 6), False), ((-88.5, -24.5, 6), False), ((23, 75, 6), False), ((-17, 75, 6), False)], 'B')
    _sondy(W, 'K-37', siatka, plik, [((-54, 98.75, 8), False), ((-54, 98.75, 6.2), True), ((-54, 98.75, 9.8), True), ((-36, 98.75, 8), True),
                                     ((-63, 98.75, 8), True), ((-54, 101, 9.6), False), ((98.75, -36, 8), False), ((-98.75, 36, 8), False),
                                     ((98.75, 0, 8), False), ((98.75, -45, 8), True), ((101, 0, 9.6), False), ((0, -98.75, 8), True)], 'B')
    _sondy(W, 'K-38', siatka, plik, [((-60, 90, 26), False), ((-85, 90, 26), False), ((-79, 85, 26), False), ((-60, 99, 15), False),
                                     ((-60, 99, 13), True), ((-43, 99, 26), False), ((-40.5, 99, 26), True), ((-90, 99, 26), False),
                                     ((-95, 99, 26), True), ((-92.5, 99, 14.5), False), ((-96, 85, 26), True), ((-60, 85, 13), True),
                                     ((-60, 85, 10), False), ((-60, 85, 39), True), ((-60, 85, 41), False), ((-60, 79, 30), True),
                                     ((-60, 77, 30), False), ((-41, 89, 30), False), ((-41, 89, 37), True), ((-41, 81.5, 30), True),
                                     ((-41, 96.5, 30), True), ((-41, 89, 23), True), ((-39, 89, 30), False), ((-43, 89, 30), False)], 'B')
    _sondy(W, 'K-39', siatka, plik, [((60, 98.75, 24), False), ((60, 98.75, 29.5), True), ((60, 98.75, 18.5), True), ((67, 98.75, 24), False),
                                     ((69, 98.75, 24), True), ((51, 98.75, 24), True), ((47, 98.75, 24), False), ((73, 98.75, 24), False),
                                     ((47, 98.75, 26.5), True), ((43, 98.75, 24), True), ((75, 98.75, 55), False), ((-75, 98.75, 55), False),
                                     ((75, 98.75, 52), True)], 'B')
    # K-40: sondy + siatka promieni wzdluz +Y z y = -110
    lista = [((30, -98.75, 22), True), ((-70, -98.75, 38), True), ((-82, -98.75, 38), True), ((-58, -98.75, 38), True),
             ((0, -98.75, 20), True), ((60, -98.75, 30), True), ((-60, -98.75, 30), True)]
    zg, n, bl = W.sondy_k('K-40', siatka, plik, lista)
    zle, ile, ymin, ymax = 0, 0, 1e9, -1e9
    for x in range(-95, 96, 5):
        for z in range(5, 58, 5):          # Z 5...55 (siatka co 5 w [5, 57], R50-1)
            loc = pierwsze_trafienie(siatka.bvh, (x, -110, z), (0, 1, 0))
            ile += 1
            if loc is None or not (-100.6 - 0.01 <= loc.y <= -100.0 + 0.01):
                zle += 1
            else:
                ymin, ymax = min(ymin, loc.y), max(ymax, loc.y)
    W.dodaj('K-40', zg == n and zle == 0, '%s: sondy %d/%d; promienie %d/%d trafiają w ścianę, y %.3f…%.3f' % (plik, zg, n, ile - zle, ile, ymin, ymax),
            'tak; każdy promień y ∈ [−100,6; −100,0]', 'B')
    # R53 (T2b/T3): kieszen 11 x 3,5 x 1,3, Z 52,1...55,6, scianka 98,8...100 -> sondy 51,6 W / 56,1 W / 99,2 W
    _sondy(W, 'K-42', siatka, plik, [((98.0, 0, 53.8), False), ((98.0, 4.5, 53.8), False), ((98.0, 6, 53.8), True), ((98.0, 0, 51.6), True),
                                     ((98.0, 0, 56.1), True), ((99.2, 0, 53.8), True), ((-98.0, 0, 53.8), False), ((50, -98.0, 53.8), False),
                                     ((0, -98.0, 53.8), True), ((-50, 98.0, 53.8), False), ((50, 98.0, 53.8), True), ((98.0, 0, 48.8), True)], 'B')
    _sondy(W, 'K-44', siatka, plik, [((75, 75, 6), False), ((70, 70, 6), False), ((88, 88, 0.2), True), ((88, 88, 0.8), True)], 'P')


def napis_korpusu(W, P, siatki, katalog_rzutow, iter_):
    """K-43 dla korpusu W i P: relief, polozenie, roznica plikow, rzut XZ."""
    wyn = {}
    for wariant, (siatka, plik, sha, obj) in siatki.items():
        # min Y promieniami wzdluz +Y (siatka 0,1 mm); plaska sciana nie ma wierzcholkow w obszarze (R47 p. 15)
        def min_y(z0, z1):
            ys = []
            for i in range(int(round(90 / 0.1)) + 1):
                for j in range(int(round((z1 - z0) / 0.1)) + 1):
                    loc = pierwsze_trafienie(siatka.bvh, (-45 + i * 0.1, -110, z0 + j * 0.1), (0, 1, 0))
                    if loc is not None:
                        ys.append(loc.y)
            return min(ys)
        zn = P['label_pos_z']                       # obszary K-43 wokol srodka napisu: Z +-5 (relief) i Z -16...-10 (bez reliefu)
        y1, y2 = min_y(zn - 5, zn + 5), min_y(zn - 16, zn - 10)
        # rzut XZ: wysokosc reliefu = -(y trafienia) - 100
        nx, nz = int(round(110 / 0.1)) + 1, int(round(12 / 0.1)) + 1
        mapa = []
        for j in range(nz):
            wiersz = []
            for i in range(nx):
                loc = pierwsze_trafienie(siatka.bvh, (-55 + i * 0.1, -110, zn - 6 + j * 0.1), (0, 1, 0))
                wiersz.append(-loc.y if loc is not None else None)
            mapa.append(wiersz)
        png = os.path.join(katalog_rzutow, 'rzut_korpus_%s_napis_%s.png' % (wariant, iter_))
        zapisz_png(png, mapa, P['box_outer'] / 2, P['box_outer'] / 2 + P['label_relief_h'])
        wyn[wariant] = (y1, y2, sha, obj, png)
    (y1w, y2w, shaw, objw, pngw), (y1p, y2p, shap, objp, pngp) = wyn['W'], wyn['P']
    rel = P['box_outer'] / 2 + P['label_relief_h']
    ok = (abs(y1w + rel) <= 0.05 and abs(y1p + rel) <= 0.05 and abs(y2w + P['box_outer'] / 2) <= 0.01 and abs(y2p + P['box_outer'] / 2) <= 0.01
          and shaw != shap and 0 < objw - objp < 0.5)
    W.dodaj('K-43', ok, 'W: min Y (Z %g…%g) %.3f, (Z %g…%g) %.3f; P: %.3f, %.3f; SHA różne: %s; obj. W − P = %.3f cm³'
            % (P['label_pos_z'] - 5, P['label_pos_z'] + 5, y1w, P['label_pos_z'] - 16, P['label_pos_z'] - 10, y2w, y1p, y2p,
               'tak' if shaw != shap else 'NIE', objw - objp),
            '−100,6 ± 0,05 / −100,0; SHA ≠; 0 < ΔV < 0,5', 'B',
            'rzuty: %s, %s' % (os.path.relpath(pngw, KATALOG).replace('\\', '/'), os.path.relpath(pngp, KATALOG).replace('\\', '/')))


def sprawdz_blat(W, P, siatka, plik):
    _sondy(W, 'K-45', siatka, plik, [((80.5, 0, -1), False), ((80.5, 0, -3), True), ((81.5, 0, -1), True), ((0, 0, -3), False), ((78, 0, -3), False),
                                     ((80.5, 80.5, -1), False), ((81.5, 81.5, -1), True)], 'B')
    _sondy(W, 'K-46', siatka, plik, [((96.0, 0, -9), True), ((94, 0, -9), False), ((97.8, 20, -9), False), ((97.8, 0, -9.75), True),
                                     ((97.8, 20, -9.75), False), ((97.8, 0, -12.5), False), ((0, -97.8, -9.75), False), ((50, -97.8, -9.75), True),
                                     ((-50, 97.8, -9.75), True), ((50, 97.8, -9.75), False), ((-97.8, 0, -9.75), True), ((96.0, 4.5, -9), False),
                                     ((96.0, 7, -9), True), ((96.0, 4.5, -4.5), True)], 'B')
    # (75, 89,6) = sonda z protokolu (slupek przed dnem otworu); (75, 90,5) = sonda poprzednich iteracji, zostaje jako druga
    lista = [((75, 93, -8.6), False), ((75, 89.6, -8.6), True), ((75, 90.5, -8.6), True), ((75, 88, -8.6), False), ((75, 93, -6), True), ((75, 93, -12), True),
             ((78, 92, -8.6), True), ((70, 96.0, -9), True), ((58, 93.5, -2), False), ((58, 93.5, -4.2), False), ((58, 86, -1), False),
             ((58, 86, -3), True), ((66, 90, -2), False), ((66, 90, -3.95), False), ((66, 90, -4.3), False), ((90, 90, -6), False),
             ((92.5, 90, -6), False), ((90, 90, -3), True), ((84, 0, -7), False)]       # bez bossow ramy (R50-U1)
    zg, n, bl = W.sondy_k('K-47', siatka, plik, lista)
    g = pierwsze_trafienie(siatka.bvh, (58, 93.5, 5), (0, 0, -1))
    d = pierwsze_trafienie(siatka.bvh, (58, 93.5, -30), (0, 0, 1))
    ok_dno = g is not None and d is not None and abs(g.z + P['blat_pin_hole_depth']) <= 0.05 and abs(d.z + P['blat_t']) <= 0.05
    W.dodaj('K-47', zg == n and ok_dno, '%s: %d/%d; dno otworu kołka: z góry %.3f, z dołu %.3f' % (plik, zg, n, g.z if g else float('nan'), d.z if d else float('nan')),
            'tak; −3,8 ± 0,05 / −4,0 ± 0,05', 'B', '%s: %d sond < 0,1 od ściany' % (plik, bl) if bl else '')


def sprawdz_tulejke(W, P, siatka, plik):
    """K-52b (R50-3): uklad - kolnierz na Z = 0, os Z."""
    _sondy(W, 'K-52b', siatka, plik, [((0, 0, 1.5), False), ((3.5, 0, 1.5), False), ((4.8, 0, 1.5), True), ((5.5, 0, 2), True),
                                       ((6.8, 0, 2), False), ((6.8, 0, 0.5), True), ((8, 0, 0.5), False)], 'P')
    # srednice walca, otworu i kolnierza z promieni w 4 kierunkach (R52: walec dc_bush_outer_d, wcisk wg 4.8)
    zw, zk = P['dc_bush_flange_t'] + P['dc_bush_t'] / 2, P['dc_bush_flange_t'] / 2
    for opis, nom, z, zewn in (('walec ø', P['dc_bush_outer_d'], zw, True), ('otwór ø', P['dc_bush_inner_d'], zw, False),
                               ('kołnierz ø', P['dc_bush_flange_d'], zk, True)):
        r = []
        for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            o = (d[0] * 20, d[1] * 20, z) if zewn else (0, 0, z)
            loc = pierwsze_trafienie(siatka.bvh, o, (-d[0], -d[1], 0) if zewn else (d[0], d[1], 0))
            r.append(math.hypot(loc.x, loc.y) if loc is not None else float('nan'))
        sr = 2 * sum(r) / len(r)
        W.dodaj('K-52b', abs(sr - nom) <= 0.05, '%s: %s %s (4 promienie)' % (plik, opis, liczba_pl(sr, 3)), '%s ± 0,05' % liczba_pl(nom, 2), 'P')


def sprawdz_podkladke(W, P, siatka, plik, t):
    """K-52c (R50-8): uklad - plasko, Z = 0; gabaryt d x d x t +-0,05."""
    zg, n, bl = W.sondy_k('K-52c', siatka, plik, [((0, 0, t / 2), False), ((1.5, 0, t / 2), False), ((3, 0, t / 2), True), ((4.7, 0, t / 2), False)])
    bb = siatka.bbox
    gab = (bb[1] - bb[0], bb[3] - bb[2], bb[5] - bb[4])
    ok_gab = all(abs(a - b) <= 0.05 for a, b in zip(gab, (P['panel_shim_d'], P['panel_shim_d'], t)))
    W.dodaj('K-52c', zg == n and ok_gab, '%s: %d/%d; gabaryt %.3f × %.3f × %.3f' % ((plik, zg, n) + gab),
            'tak; gabaryt %g × %g × t ± 0,05' % (P['panel_shim_d'], P['panel_shim_d']), 'P')


# ---- zlozenie (.blend) i sprawdzenia K-33, K-44b, K-49, K-53 ... K-56 ----

class ObiektZlozenia:
    """Siatka w ukladzie globalnym (z pliku STL albo bryly zastepczej) + BVH, do sprawdzen zlozenia."""

    def __init__(self, nazwa, ob):
        self.nazwa = nazwa
        self.ob = ob
        me = ob.data
        M = ob.matrix_world
        self.v = [M @ v.co for v in me.vertices]
        self.f = [tuple(p.vertices) for p in me.polygons]
        self.bvh = BVHTree.FromPolygons(self.v, self.f)
        R = M.to_3x3()
        nrm = [(R @ v.normal).normalized() for v in me.vertices]
        self.bvh_skurcz = BVHTree.FromPolygons([p - n * SKURCZ_K53 for p, n in zip(self.v, nrm)], self.f)
        xs, ys, zs = [p.x for p in self.v], [p.y for p in self.v], [p.z for p in self.v]
        self.bbox = (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))

    def promien(self, o, d):
        return pierwsze_trafienie(self.bvh, o, d)


def obiekt_ze_stl(sciezka, M, nazwa, kolekcja):
    przed = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=sciezka, global_scale=1.0, use_scene_unit=False, forward_axis='Y', up_axis='Z')
    ob = [o for o in bpy.data.objects if o not in przed][0]
    ob.data.transform(M)
    ob.data.update()
    ob.name = nazwa
    ob.data.name = nazwa
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    kolekcja.objects.link(ob)
    return ob


def zbuduj_zlozenie(P, stl):
    """Tworzy kolekcje, wczytuje STL do polozen zlozenia i bryly zastepcze (zapis .blend: zapisz_blend).
    stl: rdzen -> (sciezka, M_druk). Zwraca (ObiektZlozenia zestawu zlozonego, wszystkie obiekty bpy)."""
    sc = bpy.context.scene
    kol = {}
    for n in ('plytki', 'obudowa', 'akcesoria', 'elementy_kupowane'):
        kol[n] = bpy.data.collections.new(n)
        sc.collection.children.link(kol[n])
    zt = P['blat_top_z']
    z_plytki = zt + P['insert_shelf_h'] + P['plate_thickness']
    z_pokr = z_plytki + P['cover_inner_h'] + P['cover_top_t']
    T = Matrix.Translation
    # tulejka DC (etap C): kolnierz w kieszeni na licu prawej sciany skrzynki, walec w otworze, os lokalna Z -> globalna +X
    x_tul = P['dc_pos_x'] - P['dc_pocket_wall'] - P['dc_bush_flange_t']
    M_tul = T((x_tul, P['dc_pos_y'], P['dc_pos_z'])) @ Matrix.Rotation(math.pi / 2, 4, 'Y')
    zestaw = {'korpus_W': ('obudowa', T((0, 0, 0))), 'blat': ('obudowa', T((0, 0, zt))),
              'wkladka': ('obudowa', T((0, 0, zt))), 'plytka_wieczorna_n1': ('plytki', T((0, 0, z_plytki))), 'pokrywka': ('akcesoria', T((0, 0, z_pokr))),
              'tulejka_dc': ('akcesoria', M_tul)}
    przes_P = (ODSUNIECIE_WARIANTOW, 0, 0)
    boczne = {'korpus_P': ('obudowa', T(przes_P))}
    # podkladki panelu (etap C): przy domyslnych wymiarach nieuzywane -> obok, poza zestawem (K-53)
    for i, (r, _t) in enumerate(rdzenie_podkladek(P)):
        boczne[r] = ('akcesoria', T(((i - 1) * 2 * P['panel_shim_d'], -ODSUNIECIE_WARIANTOW - 2 * ODSTEP_PLYTEK, 0)))
    plytki_boczne = [r for r in stl if r.startswith('plytka') and r != 'plytka_wieczorna_n1']
    przes_n6 = None
    for i, r in enumerate(plytki_boczne):
        p = (-3.5 * ODSTEP_PLYTEK + i * ODSTEP_PLYTEK, -ODSUNIECIE_WARIANTOW, P['plate_thickness'])
        boczne[r] = ('plytki', T(p))
        if r.endswith('_n6'):
            przes_n6 = p
    obiekty, wszystkie = {}, {}
    for slownik, do_zestawu in ((zestaw, True), (boczne, False)):
        for r, (k, Mz) in slownik.items():
            if r not in stl:
                continue
            sciezka, Md = stl[r]
            ob = obiekt_ze_stl(sciezka, Mz @ Md.inverted(), r, kol[k])
            wszystkie[r] = ob
            if do_zestawu:
                obiekty[r] = ob
    for n, bm in bryly_zastepcze(P).items():
        ob = obiekt_z_bm(bm, n, kol['elementy_kupowane'])
        obiekty[n] = ob
        wszystkie[n] = ob
    if przes_n6 is not None:
        for n, bm in bryly_zastepcze_boczne(P, przes_P, przes_n6).items():
            wszystkie[n] = obiekt_z_bm(bm, n, kol['elementy_kupowane'])
    return {n: ObiektZlozenia(n, ob) for n, ob in obiekty.items()}, wszystkie


def zapisz_blend(out):
    sciezka_blend = os.path.join(out, 'ramka_v2.blend')
    bpy.ops.wm.save_as_mainfile(filepath=sciezka_blend, check_existing=False, compress=False)
    log('zapisano', sciezka_blend)
    return sciezka_blend


def sprawdz_zlozenie(W, P, Z):
    """K-33, K-44b, K-49, K-53, K-54, K-55, K-56 na obiektach zestawu zlozonego."""
    nazwy = sorted(Z)
    # K-53
    kolizje = []
    par = 0
    for i in range(len(nazwy)):
        for j in range(i + 1, len(nazwy)):
            a, b = Z[nazwy[i]], Z[nazwy[j]]
            if a.bbox[0] > b.bbox[1] or b.bbox[0] > a.bbox[1] or a.bbox[2] > b.bbox[3] or b.bbox[2] > a.bbox[3] or a.bbox[4] > b.bbox[5] or b.bbox[4] > a.bbox[5]:
                par += 1
                continue
            par += 1
            n = len(a.bvh_skurcz.overlap(b.bvh_skurcz))
            if n:
                kolizje.append((nazwy[i], nazwy[j], n))
    W.dodaj('K-53', not kolizje, '%d obiektów, %d par; pary z przecięciami: %s' % (len(nazwy), par,
            '; '.join('%s–%s: %d' % k for k in kolizje) if kolizje else 'brak'), '0 dla każdej pary', 'B',
            'skurcz −%.2f mm wzdłuż normalnych wierzchołków; zestaw: %s' % (SKURCZ_K53, ', '.join(nazwy)))
    # kontrola czulosci testu: pary stykowe bez skurczu musza dawac przeciecia (styk), ze skurczem 0
    styki = [('proxy_dystans_1', 'korpus_W'), ('proxy_dystans_1', 'proxy_panel'), ('wkladka', 'proxy_dyfuzor'), ('plytka_wieczorna_n1', 'wkladka'),
             ('proxy_pi_bonnet', 'korpus_W')]
    styki += [('tulejka_dc', b) for b in ('korpus_W', 'proxy_gniazdo_dc') if 'tulejka_dc' in Z]
    W.k['K-53']['uwaga'].append('kontrola czułości (bez skurczu, pary stykowe): ' + '; '.join(
        '%s–%s %d' % (a, b, len(Z[a].bvh.overlap(Z[b].bvh))) for a, b in styki))
    para = lambda a, b: next((k[2] for k in kolizje if {k[0], k[1]} == {a, b}), 0)
    zt = P['blat_top_z']
    # K-33
    wk, bl, dy = Z['wkladka'], Z['blat'], Z['proxy_dyfuzor']
    xp, yp = P['tab_pos_x'], P['tab_pin_y']
    zmin = min(p.z for p in wk.v if min(math.hypot(p.x - s * xp, p.y - yp) for s in (-1, 1)) > P['tab_pin_d'])
    pin_w = all(Siatka_w(wk, (s * xp, yp, zt - P['tab_pin_h'] / 2)) and not Siatka_w(bl, (s * xp, yp, zt - P['tab_pin_h'] / 2)) for s in (-1, 1))
    ok = abs(zmin - zt) <= 0.02 and abs(dy.bbox[5] - zt) <= 0.02 and abs(bl.bbox[5] - zt) <= 0.02 and para('wkladka', 'blat') == 0 \
        and para('wkladka', 'proxy_dyfuzor') == 0 and pin_w
    W.dodaj('K-33', ok, 'spód wkładki (poza kołkami) %.3f; wierzch dyfuzora %.3f; wierzch blatu %.3f; przecięcia wkładka–blat %d, wkładka–dyfuzor %d; kołki w otworach blatu: %s'
            % (zmin, dy.bbox[5], bl.bbox[5], para('wkladka', 'blat'), para('wkladka', 'proxy_dyfuzor'), 'tak' if pin_w else 'NIE'),
            '%s ± 0,02; 0 przecięć; kołki w otworach' % liczba_pl(zt, 1), 'B')
    # K-44b: Pi + wtyk Bonnetu; dodatkowo wtyk w 3 kierunkach (-X, -Y, +Y) od bonnet_dc_pos (R50-6) - przeciecia z korpusem,
    # dystansami i panelem (z samym Pi nie: gniazdo wtyku stoi na Bonnecie)
    pi, pan = Z['proxy_pi_bonnet'], Z['proxy_panel']
    luz = pan.bbox[4] - pi.bbox[5]
    cele = ['korpus_W', 'proxy_panel'] + [n for n in nazwy if n.startswith('proxy_dystans')]
    kol = [(a, b, para(a, b)) for a in ('proxy_pi_bonnet', 'proxy_wtyk_bonnet') for b in cele if para(a, b)]
    testy = []
    for kier in ('-X', '-Y', '+Y'):
        ob = obiekt_z_bm(bm_wtyk_bonnet(P, kier), 'test_wtyk_%s' % kier)
        oz = ObiektZlozenia(ob.name, ob)
        testy.append((kier, sum(len(oz.bvh_skurcz.overlap(Z[c].bvh_skurcz)) for c in cele), oz.bbox))
        usun_obiekt(ob)
    W.dodaj('K-44b', not kol and luz >= P['pi_clearance_top'] - 1e-6 and all(n == 0 for _k, n, _b in testy),
            'przecięcia Pi/wtyk (%s) z korpusem, dystansami i panelem: %s; luz Z = %.3f − %.3f = %.3f; test 3 kierunków wtyku %g mm: %s'
            % (P['bonnet_dc_dir'], 'brak' if not kol else kol, pan.bbox[4], pi.bbox[5], luz, P['bonnet_dc_plug_len'],
               '; '.join('%s (x %.1f…%.1f, y %.1f…%.1f) %d przecięć' % (k, b[0], b[1], b[2], b[3], n) for k, n, b in testy)),
            '0 / ≥ %s; 3 kierunki 0' % liczba_pl(P['pi_clearance_top'], 0), 'B')
    # K-49: blat-korpus, dyfuzor-kieszen, panel pod blatem i oknem, dystanse na stadionach
    kr = Z['korpus_W']
    zs = zt - P['blat_t'] - P['blat_skirt_h'] / 2
    t1 = pierwsze_trafienie(bl.bvh, (90, 20, zs), (1, 0, 0))
    t2 = pierwsze_trafienie(bl.bvh, (t1.x + KROK_PROMIENIA, 20, zs), (1, 0, 0)) if t1 else None
    tk = pierwsze_trafienie(kr.bvh, (90, 20, zs), (1, 0, 0))
    luz_bk = tk.x - t2.x
    td = pierwsze_trafienie(bl.bvh, (0, 20, zt - P['diffuser_t'] / 2), (1, 0, 0))
    luz_dk = td.x - dy.bbox[1]
    xo = (P['window_through'] + P['panel_size']) / 4                 # miedzy krawedzia okna a krawedzia PCB
    spod_blatu = pierwsze_trafienie(bl.bvh, (xo, 0, 0), (0, 0, 1)).z
    luz_pb = spod_blatu - pan.bbox[5]
    okno = pierwsze_trafienie(bl.bvh, (0, 0, zt - P['blat_t'] / 2 - P['diffuser_t'] / 2), (1, 0, 0)).x
    nakl = pan.bbox[1] - okno
    dyst = []
    for (x, y, sx, sy), n in zip(pozycje_podkladek(P), sorted(c for c in nazwy if c.startswith('proxy_dystans'))):
        p = Vector((x, y, 0)) + Vector((sx, -sy, 0)).normalized() * (P['standoff_d'] / 2 - 0.7)   # w podstawie dystansu, poza osia rowka
        traf = pierwsze_trafienie(kr.bvh, (p.x, p.y, 100), (0, 0, -1))
        dyst.append((n, Z[n].bbox[4], traf.z if traf else float('nan'), para(n, 'korpus_W')))
    zpad = P['floor_t'] + P['panel_pad_h']
    ok_d = all(abs(a - zpad) <= 0.02 and abs(b - zpad) <= 0.02 and c == 0 for _n, a, b, c in dyst)
    ok = (abs(luz_bk - P['blat_skirt_clearance']) <= 0.05 and abs(luz_dk - (P['diffuser_pocket'] - P['diffuser_size']) / 2) <= 0.05
          and luz_pb >= 2 - 1e-6 and abs(nakl - (P['panel_size'] - P['window_through']) / 2) <= 0.05 and ok_d
          and para('proxy_panel', 'blat') == 0 and para('blat', 'korpus_W') == 0)
    W.dodaj('K-49', ok, 'kołnierz blatu–ściana korpusu %.3f (x %.3f → %.3f); dyfuzor–kieszeń %.3f; spód blatu %.3f − PCB %.3f = %.3f; PCB pod oknem: nakładka %.3f/stronę (okno %.3f, PCB %.3f); '
            'dystanse (spód / wierzch stadionu pod nim / przecięcia z korpusem): %s; przecięcia panel–blat %d, blat–korpus %d'
            % (luz_bk, t2.x, tk.x, luz_dk, spod_blatu, pan.bbox[5], luz_pb, nakl, okno, pan.bbox[1],
               ', '.join('%s %.3f/%.3f/%d' % d for d in dyst), para('proxy_panel', 'blat'), para('blat', 'korpus_W')),
            '0,5 / 1,0; panel–blat ≥ 2 (4,0); nakładka 1,0; dystanse na stadionach Z %s; 0 przecięć' % liczba_pl(zpad, 0), 'B')
    # K-54
    pk, pl = Z['pokrywka'], Z['plytka_wieczorna_n1']
    pomiary = [('blat (90, 0)', bl.promien((90, 0, 200), (0, 0, -1)).z, zt),
               ('dyfuzor (0, 70)', dy.promien((0, 70, 200), (0, 0, -1)).z, zt),
               ('rama wkładki (0, 50,3)', wk.promien((0, 50.3, 200), (0, 0, -1)).z, zt + P['insert_h']),
               ('płytka n1 (0, −46,5)', pl.promien((0, -46.5, 200), (0, 0, -1)).z, zt + P['insert_shelf_h'] + P['plate_thickness']),
               ('pokrywka (40, 40)', pk.promien((40, 40, 200), (0, 0, -1)).z, zt + P['insert_shelf_h'] + P['plate_thickness'] + P['cover_inner_h'] + P['cover_top_t']),
               ('min Z pokrywki', pk.bbox[4], zt + P['insert_shelf_h'] + P['plate_thickness'] - P['cover_skirt_below']),
               ('max Z proxy_pi_bonnet', pi.bbox[5], P['floor_t'] + P['pi_standoff_h'] + P['pi_stack_h']),
               ('min Z proxy_panel', pan.bbox[4], P['panel_pcb_z'] - P['panel_bottom_parts_h']),
               ('PCB panelu spód (70, 70)', pan.promien((70, 70, -200), (0, 0, 1)).z, P['panel_pcb_z']),
               ('PCB panelu wierzch (70, 70)', pan.promien((70, 70, 200), (0, 0, -1)).z, P['panel_pcb_z'] + P['panel_pcb_t']),
               ('szczyt dystansów', max(Z[n].bbox[5] for n in nazwy if n.startswith('proxy_dystans')), P['panel_pcb_z']),
               ('stadion: wierzch (−64, 60)', kr.promien((-64, 60, 100), (0, 0, -1)).z, P['floor_t'] + P['panel_pad_h']),
               ('dno obok stadionu (−70, 50)', kr.promien((-70, 50, 100), (0, 0, -1)).z, P['floor_t']),
               ('korpus wierzch', kr.bbox[5], P['korpus_h'])]
    st = [Z[n] for n in nazwy if n.startswith('proxy_stopka')]
    pomiary.append(('stopki min Z', min(s.bbox[4] for s in st), -P['foot_h']))
    pomiary.append(('stopki max Z', max(s.bbox[5] for s in st), 0.0))
    ok = all(abs(a - b) <= 0.05 for _, a, b in pomiary)
    W.dodaj('K-54', ok, '; '.join('%s %.3f (%.2f)' % (n, a, b) for n, a, b in pomiary), '± 0,05', 'B')
    # K-55
    mg, hl = Z['proxy_magnes_A'], Z['proxy_hall_A']
    odl = mg.bbox[4] - hl.bbox[5]
    W.dodaj('K-55', abs(odl - 1.2) <= 0.05, 'spód magnesu A %.3f − wierzch czujnika A %.3f = %.3f; + 0,5 (struktura TO‑92) = %.3f ≤ 4' % (mg.bbox[4], hl.bbox[5], odl, odl + 0.5),
            '1,2 ± 0,05', 'B')
    # K-56: promienie z gory nad pasem przednim i prawym (do krawedzi panelu)
    ps = P['panel_size'] / 2
    krok = 0.5
    zle = []
    for (x0, x1, y0, y1) in ((-ps, ps, -ps, -P['insert_opening'] / 2 - P['insert_wall_w']),
                             (P['insert_opening'] / 2 + P['insert_wall_w'], ps, -ps, P['insert_opening'] / 2 + P['insert_wall_w'])):
        nx, ny = int(round((x1 - x0) / krok)), int(round((y1 - y0) / krok))
        for i in range(1, nx):
            for j in range(1, ny):
                x, y = x0 + i * krok, y0 + j * krok
                naj, kto = -1e9, None
                for n in nazwy:
                    loc = Z[n].promien((x, y, 300), (0, 0, -1))
                    if loc is not None and loc.z > naj:
                        naj, kto = loc.z, n
                if kto != 'proxy_dyfuzor' or abs(naj - zt) > 0.01:
                    zle.append((x, y, kto, naj))
    # szerokosc odslonietego pasa z promieni wzdluz y przy x = 30 (przod) i wzdluz x przy y = 0 (prawy)
    def pierwszy_nad(punkty):
        for x, y in punkty:
            naj = max((Z[n].promien((x, y, 300), (0, 0, -1)) or Vector((0, 0, -1e9))).z for n in nazwy if n != 'proxy_dyfuzor')
            if naj > zt + 0.01:
                return x, y
        return None
    pf = pierwszy_nad([(30, -ps + k * 0.01) for k in range(int(ps * 100))])
    pp = pierwszy_nad([(ps - k * 0.01, 0) for k in range(int(ps * 100))])
    szer_f = pf[1] + ps if pf else float('nan')
    szer_p = ps - pp[0] if pp else float('nan')
    piks = int(math.floor(min(szer_f, szer_p) / P['led_pitch'] + 1e-9))
    marg = P['panel_size'] / 2 - (P['insert_opening'] / 2 + P['insert_wall_w'])   # R53: 80 - 52,4 = 27,6 (bylo literalnie 27,7)
    W.dodaj('K-56', not zle and abs(szer_f - marg) <= 0.05 and abs(szer_p - marg) <= 0.05 and piks >= 11,
            'pas przedni %.2f mm, prawy %.2f mm → %d pełnych pikseli; punktów nad pasem zasłoniętych przez inne części: %d%s'
            % (szer_f, szer_p, piks, len(zle), (' (np. %s)' % (zle[:3],)) if zle else ''), '%s / 11' % liczba_pl(marg, 1), 'B')
    # uwaga D recenzenta B iter3 (6.1): odbiornik USB (tylko korpus P) w polozeniu hipotetycznym w zestawie W - informacyjnie przy K-53
    boczne = bryly_zastepcze_boczne(P, (0, 0, 0), (0, 0, 0))
    for n in ('proxy_magnes_B', 'proxy_magnes_C'):
        boczne.pop(n).free()
    ob = obiekt_z_bm(boczne['proxy_odbiornik_usb'], 'test_odbiornik')
    oz = ObiektZlozenia(ob.name, ob)
    cele = ['korpus_W', 'proxy_panel', 'proxy_gniazdo_usb', 'proxy_wtyk_bonnet'] + [n for n in nazwy if n.startswith('proxy_dystans')]
    nprz = {c: len(oz.bvh_skurcz.overlap(Z[c].bvh_skurcz)) for c in cele if c in Z}
    odl = {c: min(Z[c].bvh.find_nearest(p)[3] for p in oz.v) for c in ('korpus_W', 'proxy_dystans_4') if c in Z}
    usun_obiekt(ob)
    W.k['K-53']['uwaga'].append('informacyjnie (recenzja B iter3 §6.1): odbiornik USB w położeniu hipotetycznym w zestawie W (x %.1f…%.1f, Z %.1f…%.1f): '
                                'przecięcia %s; najmniejsza odległość wierzchołków odbiornika: %s'
                                % (oz.bbox[0], oz.bbox[1], oz.bbox[4], oz.bbox[5], ', '.join('%s %d' % kv for kv in nprz.items()),
                                   ', '.join('%s %.2f mm' % kv for kv in odl.items())))
    if any(nprz.values()):
        ostrzez('odbiornik USB (położenie hipotetyczne) przecina: %s' % [c for c, n in nprz.items() if n])


def Siatka_w(oz, p):
    """Sonda parzystosci na obiekcie zlozenia (globalnie)."""
    glosy = 0
    for d in KIERUNKI:
        n = 0
        o = Vector(p)
        for _ in range(100000):
            loc, _nn, _i, _dd = oz.bvh.ray_cast(o, d)
            if loc is None:
                break
            n += 1
            o = loc + d * KROK_PROMIENIA
        glosy += n % 2
    return glosy >= 2


# ===========================================================================
# (5a) R58: sprawdzenia kompletu okraglego do ramki (K-64 ... K-67) na STL wczytanych z powrotem
# ===========================================================================

KROK_MAPY_R58 = 0.25     # krok siatki promieni map wysokosci K-64 (narzedziowe, nie wymiar czesci)


def trafienia(bvh, o, d, maks=64):
    """Kolejne przeciecia promienia o + t*d z siatka: lista t (odleglosci od o), rosnaco."""
    o, d = Vector(o), Vector(d).normalized()
    wyn, p = [], o.copy()
    for _ in range(maks):
        loc, _n, _i, _dd = bvh.ray_cast(p, d)
        if loc is None:
            break
        wyn.append((loc - o).dot(d))
        p = loc + d * KROK_PROMIENIA
    return wyn


def promien_z_zewnatrz(bvh, kat_st, z, r_start):
    """Odleglosc od osi Z (rzut na kierunek kat_st) pierwszego trafienia promienia biegnacego z r_start do srodka na wysokosci z."""
    c, s = math.cos(math.radians(kat_st)), math.sin(math.radians(kat_st))
    loc = pierwsze_trafienie(bvh, (c * r_start, s * r_start, z), (-c, -s, 0))
    return None if loc is None else loc.x * c + loc.y * s


def promien_od_srodka(bvh, kat_st, z, x0=0.0, y0=0.0):
    """Pierwsze trafienie promienia z punktu (x0, y0, z) w kierunku kat_st; zwraca odleglosc od tego punktu."""
    c, s = math.cos(math.radians(kat_st)), math.sin(math.radians(kat_st))
    loc = pierwsze_trafienie(bvh, (x0, y0, z), (c, s, 0))
    return None if loc is None else (loc.x - x0) * c + (loc.y - y0) * s


def srodek_wneki(bvh, cx, cy, z):
    """Wneka (otwor) wokol (cx, cy) na wysokosci z: promienie +-X i +-Y z punktu. Zwraca (sx, sy, szer_x, szer_y) albo None."""
    t = []
    for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0)):
        loc = pierwsze_trafienie(bvh, (cx, cy, z), d)
        if loc is None:
            return None
        t.append(math.hypot(loc.x - cx, loc.y - cy))
    return cx + (t[0] - t[1]) / 2, cy + (t[2] - t[3]) / 2, t[0] + t[1], t[2] + t[3]


def srodek_bryly(bvh, cx, cy, z, odl):
    """Bryla (kolek) wokol (cx, cy) na wysokosci z: promienie z punktow odleglych o odl, w strone srodka. Zwraca (sx, sy, szer_x, szer_y) albo None."""
    k = []
    for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        loc = pierwsze_trafienie(bvh, (cx + dx * odl, cy + dy * odl, z), (-dx, -dy, 0))
        if loc is None:
            return None
        k.append(loc.x if dx else loc.y)
    return (k[0] + k[1]) / 2, (k[2] + k[3]) / 2, k[0] - k[1], k[2] - k[3]


def mapa_promieni(bvh, punkty, z_start, kierunek):
    """Z pierwszego trafienia promieni pionowych (kierunek -1: z gory, +1: od spodu) w punktach (x, y); None = brak trafienia."""
    d = Vector((0, 0, kierunek))
    wyn = []
    for x, y in punkty:
        loc, _n, _i, _dd = bvh.ray_cast(Vector((x, y, z_start)), d)
        wyn.append(None if loc is None else loc.z)
    return wyn


def porownaj_mapy(m1, m2, tol=0.01):
    """(liczba punktow, punkty z trafieniem w jednej siatce i bez w drugiej, max |dz| dla wspolnych trafien)."""
    niezg, dz = 0, 0.0
    for a, b in zip(m1, m2):
        if (a is None) != (b is None):
            niezg += 1
        elif a is not None:
            dz = max(dz, abs(a - b))
    return len(m1), niezg, dz


def punkty_kola(R, krok, przesuniecie=0.0371):
    """Siatka punktow (x, y) w kole o promieniu R (krok, przesuniecie od zera, zeby nie trafiac w osie symetrii)."""
    n = int(math.ceil(R / krok)) + 1
    pkt = []
    for j in range(-n, n + 1):
        for i in range(-n, n + 1):
            x, y = i * krok + przesuniecie, j * krok + przesuniecie
            if x * x + y * y <= R * R:
                pkt.append((x, y))
    return pkt


def odl_punkt_prostokat(p, x0, x1, y0, y1):
    return math.hypot(max(x0 - p[0], 0.0, p[0] - x1), max(y0 - p[1], 0.0, p[1] - y1))


def otwory_o3(uklad):
    """Srodki otworow o3 z JSON (gniazda okragle: os; rynienki: hole_count otworow na osi)."""
    wyn = []
    for g in uklad['sockets']:
        if g['type'] == 'round':
            wyn.append((g['x'], g['y']))
        else:
            c, s = math.cos(math.radians(g['angle'])), math.sin(math.radians(g['angle']))
            for i in range(g['hole_count']):
                k = i - (g['hole_count'] - 1) / 2
                wyn.append((g['x'] + k * g['hole_pitch'] * c, g['y'] + k * g['hole_pitch'] * s))
    return wyn


def klasy_scian_plytki(siatka, uklad, P):
    """R58 runda 2: klasa kazdej sciany siatki plytki ramkowej (uklad montazowy) z geometrii JSON: 'zew' (wierzch z cyfra, faza, walec,
    sciecie, spod), 'rowek_klucza', 'rowek_pokrywki', 'kieszen_<naroze>'; wnetrze: 'otwor', 'stozek', 'dolek', 'gniazdo' (gniazda i rynienka)."""
    T, R, f = P['plate_thickness'], uklad['d'] / 2, P['plate_top_chamfer']
    fl, cg, ks = uklad['flat'], uklad['cover_groove'], uklad['key_slot']
    cf, sf = math.cos(math.radians(fl['angle_deg'])), math.sin(math.radians(fl['angle_deg']))
    ck, sk = math.cos(math.radians(ks['angle_deg'])), math.sin(math.radians(ks['angle_deg']))
    E = 1e-3
    otw = otwory_o3(uklad)
    rh = uklad['sockets'][0]['hole_d'] / 2
    dep = max(g['depth'] for g in uklad['sockets'])
    klasy = []
    for fc in siatka.bm.faces:
        vs = [v.co for v in fc.verts]
        zs = [v.z for v in vs]
        rs = [math.hypot(v.x, v.y) for v in vs]
        # promienie z tolerancja 0,01 > strzalka wieloboku 256 bokow (R (1 - cos(pi/256)) = 0,004): wierzcholki z przeciec na bokach wieloboku
        if min(zs) >= -E or max(zs) <= -T + E or min(rs) >= R - 0.01 or (min(rs) >= R - f - 0.01 and min(zs) >= -f - E) \
                or min(v.x * cf + v.y * sf for v in vs) >= fl['dist'] - E:
            klasy.append('zew')
            continue
        if all(v.x * ck + v.y * sk >= ks['r0'] - E and abs(-v.x * sk + v.y * ck) <= ks['w'] / 2 + E and v.z <= -T + ks['h'] + E for v in vs):
            klasy.append('rowek_klucza')
            continue
        if all(-cg['z'] - cg['w'] / 2 - E <= z <= -cg['z'] + cg['w'] / 2 + E for z in zs) and min(rs) >= R - cg['depth'] - 0.01:
            klasy.append('rowek_pokrywki')
            continue
        k = next((mp['corner'] for mp in uklad['magnet_pockets']
                  if all(math.hypot(v.x - mp['x'], v.y - mp['y']) <= mp['d'] / 2 + E and v.z <= -T + mp['depth'] + E for v in vs)), None)
        if k:
            klasy.append('kieszen_%s' % k)
            continue
        c = sum(vs, Vector((0, 0, 0))) / len(vs)
        if c.z <= -dep + E and any(math.hypot(c.x - ox, c.y - oy) <= rh + E for ox, oy in otw):
            klasy.append('otwor')
        elif any(math.hypot(c.x - m['x'], c.y - m['y']) <= m['d'] / 2 + E and c.z >= -m['depth'] - E for m in uklad['markers']):
            klasy.append('stozek')
        elif any(math.hypot(c.x - d['x'], c.y - d['y']) <= d['d'] / 2 + E and c.z >= -d['depth'] - E for d in uklad['code_dimples']):
            klasy.append('dolek')
        else:
            klasy.append('gniazdo')
    return klasy


def probki_scian(siatka, indeksy, krok=0.2):
    """Punkty na trojkatach siatki (indeksy scian) w siatce barycentrycznej co <= krok."""
    pkt = []
    for i in indeksy:
        vs = [v.co for v in siatka.bm.faces[i].verts]
        for k in range(1, len(vs) - 1):
            a, b, c = vs[0], vs[k], vs[k + 1]
            n = max(1, int(math.ceil(max((b - a).length, (c - a).length, (c - b).length) / krok)))
            for p in range(n + 1):
                for q in range(n + 1 - p):
                    pkt.append(a + (b - a) * (p / n) + (c - a) * (q / n))
    return pkt


def scianki_3d_plytki(siatka, uklad, P):
    """R58 runda 2 (D2, D3 recenzji): scianki 3D plytki ramkowej z siatki. Dla rowka klucza, rowka pokrywki i kazdej kieszeni magnesu:
    najmniejsza odleglosc probek ich powierzchni od powierzchni wnetrza (klasy 'gniazdo', 'otwor', 'stozek', 'dolek', inne kieszenie i rowki);
    pasek rowek klucza - rowek pokrywki przy scieciu osobno (informacyjnie). Zwraca nazwa -> (min, klasa, punkt, {klasa: min}, prog albo None)."""
    klasy = klasy_scian_plytki(siatka, uklad, P)
    wsp = [v.co.copy() for v in siatka.bm.verts]
    sciany = [[v.index for v in fc.verts] for fc in siatka.bm.faces]
    wnetrze = ('gniazdo', 'otwor', 'stozek', 'dolek')

    def odl(zrodlo, cele, prog):
        idx = [i for i, k in enumerate(klasy) if k in cele]
        if not idx:
            return None
        bvh = BVHTree.FromPolygons(wsp, [sciany[i] for i in idx])
        per, best = {}, (float('inf'), None, (0.0, 0.0, 0.0))
        for p in probki_scian(siatka, [i for i, k in enumerate(klasy) if k == zrodlo]):
            loc, _n, j, d = bvh.find_nearest(p)
            if loc is None:
                continue
            k = klasy[idx[j]]
            per[k] = min(per.get(k, float('inf')), d)
            if d < best[0]:
                best = (d, k, (loc.x, loc.y, loc.z))
        return best[0], best[1], best[2], per, prog
    kiesz = sorted({k for k in klasy if k.startswith('kieszen_')})
    wyn = {}
    wyn['rowek klucza–wnętrze'] = odl('rowek_klucza', wnetrze + tuple(kiesz), 1.5)
    wyn['rowek pokrywki–wnętrze'] = odl('rowek_pokrywki', wnetrze + tuple(kiesz), 1.5)
    for k in kiesz:
        wyn['%s–wnętrze' % k.replace('kieszen_', 'kieszeń ')] = odl(k, wnetrze + tuple(x for x in kiesz if x != k) + ('rowek_klucza', 'rowek_pokrywki'), 1.5)
    wyn['rowek klucza–rowek pokrywki (pasek przy ścięciu, informacyjnie)'] = odl('rowek_klucza', ('rowek_pokrywki',), None)
    return {k: v for k, v in wyn.items() if v is not None}


def sprawdz_ramkowa(W, P, siatka, plik, uklad, numer, uklad_kw, punkty_mapy, mapa_ref, plik_ref, katalog_rzutow, iter_):
    """K-64 (R58): plytka okragla ramkowa - kieszenie magnesow, rowek pokrywki, rowek klucza (sondy i pomiary promieniami), scianki
    (z JSON, parametrow i pomiarow), sockets = kwadrat typu, obrys cyfry (z siatki), mapa wysokosci wierzchu = okragla tego typu."""
    T = P['plate_thickness']
    R = uklad['d'] / 2
    fl, cg, ks = uklad['flat'], uklad['cover_groove'], uklad['key_slot']
    t15 = math.tan(math.radians(P['socket_wall_angle']))
    bvh = siatka.bvh
    bledy, info, lista = [], [], []
    # (a) kieszenie magnesow A, B, C
    pom_k = []
    for mp in uklad['magnet_pockets']:
        x, y, rr = mp['x'], mp['y'], mp['d'] / 2
        zk = -T + mp['depth'] / 2
        lista += [((x, y, zk), False), ((x, y, -T + mp['depth'] + 0.2), True),
                  ((x + rr - 0.15, y, zk), False), ((x - rr + 0.15, y, zk), False), ((x, y + rr - 0.15, zk), False), ((x, y - rr + 0.15, zk), False),
                  ((x + rr + 0.2, y, zk), True), ((x - rr - 0.2, y, zk), True), ((x, y + rr + 0.2, zk), True), ((x, y - rr - 0.2, zk), True)]
        sw = srodek_wneki(bvh, x, y, zk)
        dno = pierwsze_trafienie(bvh, (x, y, -T - 1.0), (0, 0, 1))
        r_os = math.hypot(x, y)
        tr = trafienia(bvh, (x, y, zk), (x / r_os, y / r_os, 0))
        if sw is None or dno is None or len(tr) < 2:
            bledy.append('(a) kieszeń %s: brak trafień' % mp['corner'])
            continue
        sx, sy, wx, wy = sw
        gl = dno.z + T
        scianka = tr[1] - tr[0]
        pom_k.append((mp['corner'], sx, sy, wx, wy, gl, scianka, r_os + tr[1]))
        if math.hypot(sx - x, sy - y) > 0.05:
            bledy.append('(a) kieszeń %s: środek (%.3f, %.3f) zamiast (%.3f, %.3f)' % (mp['corner'], sx, sy, x, y))
        if abs(wx - mp['d']) > 0.05 or abs(wy - mp['d']) > 0.05:
            bledy.append('(a) kieszeń %s: ø %.3f × %.3f zamiast %g' % (mp['corner'], wx, wy, mp['d']))
        if abs(gl - mp['depth']) > 0.05:
            bledy.append('(a) kieszeń %s: głębokość %.3f zamiast %g' % (mp['corner'], gl, mp['depth']))
        if scianka < 1.5 - 1e-6:
            bledy.append('(d) ścianka kieszeń %s – krawędź %.3f < 1,5' % (mp['corner'], scianka))
    info.append('(a) kieszenie (środek, ø X × Y, głębokość, ścianka do krawędzi z promienia od osi kieszeni): ' + '; '.join(
        '%s (%.3f, %.3f) ø %.3f × %.3f, gł. %.3f, ścianka %.3f (krawędź r %.3f)' % p for p in pom_k))
    # (b) rowek pokrywki: sondy promieniowe na Z -cover_groove_z poza sciecem, nad i pod rowkiem promien R
    pol = math.degrees(math.asin(fl['chord_w'] / 2 / R))
    zg_s, zg_g, zg_d = -cg['z'], -cg['z'] + cg['w'] / 2 + 0.5, -cg['z'] - cg['w'] / 2 - 0.5
    gl_r, obok = [], []
    for i in range(16):
        a = 11.25 + 22.5 * i
        if abs(((a - fl['angle_deg']) + 180) % 360 - 180) <= pol + 2.0:
            continue
        v = promien_z_zewnatrz(bvh, a, zg_s, R + 5)
        vg, vd = promien_z_zewnatrz(bvh, a, zg_g, R + 5), promien_z_zewnatrz(bvh, a, zg_d, R + 5)
        if v is None or vg is None or vd is None:
            bledy.append('(b) rowek: brak trafienia na %g°' % a)
            continue
        gl_r.append((a, R - v))
        obok += [vg, vd]
    if len(gl_r) < 8:
        bledy.append('(b) rowek: %d kierunków (< 8)' % len(gl_r))
    if any(abs(g - cg['depth']) > 0.1 for _a, g in gl_r):
        bledy.append('(b) rowek: głębokość poza %g ± 0,1' % cg['depth'])
    if any(abs(v - R) > 0.05 for v in obok):
        bledy.append('(b) nad/pod rowkiem promień poza %g ± 0,05' % R)
    v_sc = promien_z_zewnatrz(bvh, fl['angle_deg'], zg_s, R + 5)
    if v_sc is None or abs(v_sc - (R - cg['depth'])) > 0.1:
        bledy.append('(b) rowek w ścięciu: dno %s zamiast %.3f' % ('brak' if v_sc is None else '%.3f' % v_sc, R - cg['depth']))
    rg = R - cg['depth'] / 2
    wys_r = []
    for a in (0.0, 90.0, 180.0, 270.0):
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        lista += [((rg * c, rg * s, zg_s), False), ((rg * c, rg * s, -cg['z'] + cg['w'] / 2 + 0.15), True),
                  ((rg * c, rg * s, -cg['z'] - cg['w'] / 2 - 0.15), True), (((R - cg['depth'] - 0.2) * c, (R - cg['depth'] - 0.2) * s, zg_s), True)]
        g = pierwsze_trafienie(bvh, (rg * c, rg * s, zg_s), (0, 0, 1))
        d = pierwsze_trafienie(bvh, (rg * c, rg * s, zg_s), (0, 0, -1))
        if g is None or d is None:
            bledy.append('(b) rowek: brak trafienia w pionie na %g°' % a)
            continue
        wys_r.append((a, g.z - d.z, (g.z + d.z) / 2))
    if any(abs(w - cg['w']) > 0.05 or abs(zs + cg['z']) > 0.05 for _a, w, zs in wys_r):
        bledy.append('(b) rowek: wysokość / środek Z poza %g / −%g ± 0,05' % (cg['w'], cg['z']))
    info.append('(b) rowek pokrywki: głębokość z %d sond promieniowych na Z %g: %.3f…%.3f (zadane %g ± 0,1); nad i pod rowkiem (Z %g, %g) promień %.3f…%.3f; '
                'w osi ścięcia dno r %s (głębokość w ścięciu %s); wysokość / środek Z (r %.1f, 0/90/180/270°): %s'
                % (len(gl_r), zg_s, min(g for _a, g in gl_r) if gl_r else float('nan'), max(g for _a, g in gl_r) if gl_r else float('nan'), cg['depth'],
                   zg_g, zg_d, min(obok) if obok else float('nan'), max(obok) if obok else float('nan'),
                   '—' if v_sc is None else '%.3f' % v_sc, '—' if v_sc is None else '%.3f' % (fl['dist'] - v_sc), rg,
                   ', '.join('%.3f / %.3f' % (w, zs) for _a, w, zs in wys_r)))
    # (c) rowek klucza (uklad u wzdluz angle_deg, v prostopadle)
    cu, su = math.cos(math.radians(ks['angle_deg'])), math.sin(math.radians(ks['angle_deg']))
    uv = lambda u, v, z: (u * cu - v * su, u * su + v * cu, z)
    um = (ks['r0'] + fl['dist']) / 2
    zs_k = -T + ks['h'] / 2
    lista += [(uv(um, 0, zs_k), False), (uv(um, ks['w'] / 2 - 0.15, zs_k), False), (uv(um, -ks['w'] / 2 + 0.15, zs_k), False),
              (uv(um, ks['w'] / 2 + 0.2, zs_k), True), (uv(um, -ks['w'] / 2 - 0.2, zs_k), True),
              (uv(um, 0, -T + ks['h'] - 0.15), False), (uv(um, 0, -T + ks['h'] + 0.2), True),
              (uv(ks['r0'] + 0.15, 0, zs_k), False), (uv(ks['r0'] - 0.2, 0, zs_k), True)]
    p0 = uv(um, 0, zs_k)
    tp = pierwsze_trafienie(bvh, p0, (-su, cu, 0))
    tm = pierwsze_trafienie(bvh, p0, (su, -cu, 0))
    tz = pierwsze_trafienie(bvh, uv(um, 0, -T - 1.0), (0, 0, 1))
    tr0 = pierwsze_trafienie(bvh, p0, (-cu, -su, 0))
    if None in (tp, tm, tz, tr0):
        bledy.append('(c) rowek klucza: brak trafień')
        szer_k = h_k = r0_k = off_k = float('nan')
    else:
        vp, vm = -(tp.x * su) + tp.y * cu, -(tm.x * su) + tm.y * cu
        szer_k, off_k = vp - vm, (vp + vm) / 2
        h_k = tz.z + T
        r0_k = tr0.x * cu + tr0.y * su
        if abs(szer_k - ks['w']) > 0.05 or abs(off_k) > 0.05:
            bledy.append('(c) rowek klucza: szerokość %.3f (oś przesunięta o %.3f) zamiast %g' % (szer_k, off_k, ks['w']))
        if abs(h_k - ks['h']) > 0.05:
            bledy.append('(c) rowek klucza: wysokość %.3f zamiast %g' % (h_k, ks['h']))
        if abs(r0_k - ks['r0']) > 0.05:
            bledy.append('(c) rowek klucza: początek r %.3f zamiast %g' % (r0_k, ks['r0']))
    info.append('(c) rowek klucza na %g°: szerokość %.3f (oś %.3f od zadanej), wysokość od spodu %.3f, początek r %.3f (zadane %g / %g / %g)'
                % (ks['angle_deg'], szer_k, off_k, h_k, r0_k, ks['w'], ks['h'], ks['r0']))
    # (d) [runda 2: D2/D3 recenzji] scianki 3D z siatki: odleglosc najblizszej powierzchni wnetrza (gniazda, rynienka, otwory, stozki, dolki,
    # inne cechy) od probek co <= 0,2 mm na powierzchniach rowka klucza, rowka pokrywki i kieszeni magnesow (bez powierzchni zewnetrznych)
    sc3 = scianki_3d_plytki(siatka, uklad, P)
    for nz, (v, kto, gdzie, per, lim) in sc3.items():
        if lim is not None and v < lim - 1e-6:
            bledy.append('(d) ścianka 3D %s %.3f < %g (%s)' % (nz, v, lim, kto))
    info.append('(d) ścianki 3D z siatki (min po próbkach co ≤ 0,2 mm): ' + '; '.join(
        '%s %.3f%s (najbliżej: %s w (%.2f; %.2f; %.2f); wg klas: %s)' % (nz, v, '' if lim is None else ' ≥ %g' % lim, kto, gdzie[0], gdzie[1], gdzie[2],
                                                                   ', '.join('%s %.2f' % kv for kv in sorted(per.items(), key=lambda kv: kv[1])))
        for nz, (v, kto, gdzie, per, lim) in sc3.items()))
    # (e) sockets = kwadrat typu
    rowne = uklad['sockets'] == uklad_kw['sockets']
    if not rowne:
        bledy.append('(e) sockets różnią się od uklad_gniazd_%s.json' % typ_bazowy(uklad['plate']))
    info.append('(e) sockets identyczne z uklad_gniazd_%s.json: %s (%d wpisów)' % (typ_bazowy(uklad['plate']), 'tak' if rowne else 'NIE', len(uklad['sockets'])))
    # (f) obrys cyfry (warianty): wierzcholki reliefu z siatki -> prostokat; odstepy do gniazd >= socket_wall_min, stozkow i dolkow >= 1,5,
    # narozniki w kole socket_zone_r (regula R59, dotad liczona tylko narzedziem weryfikuj_uklad_R59.js)
    nr = uklad['number_relief']
    if numer is not None and nr is not None:
        vs = [v.co for v in siatka.bm.verts if v.co.z > nr['relief_h'] / 2 and abs(v.co.x - nr['x']) <= nr['text_h'] and abs(v.co.y - nr['y']) <= nr['text_h']]
        if not vs:
            bledy.append('(f) brak wierzchołków reliefu cyfry')
        else:
            x0, x1 = min(v.x for v in vs), max(v.x for v in vs)
            y0, y1 = min(v.y for v in vs), max(v.y for v in vs)
            dg, idg = 1e9, None
            for g in uklad['sockets']:
                (a, b), r = ksztalt(g)
                for i in range(201):
                    t = i / 200
                    d = odl_punkt_prostokat((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])), x0, x1, y0, y1) - r
                    if d < dg:
                        dg, idg = d, g['id']
            dz = min(odl_punkt_prostokat((m['x'], m['y']), x0, x1, y0, y1) - m['d'] / 2 for m in uklad['markers'])
            dd = min(odl_punkt_prostokat((d['x'], d['y']), x0, x1, y0, y1) - d['d'] / 2 for d in uklad['code_dimples'])
            rn = max(math.hypot(x, y) for x in (x0, x1) for y in (y0, y1))
            if dg < P['socket_wall_min'] - 1e-6 or dz < 1.5 - 1e-6 or dd < 1.5 - 1e-6 or rn > P['socket_zone_r'] + 1e-6:
                bledy.append('(f) obrys cyfry: do gniazda %.2f, do stożka %.2f, do dołka %.2f, narożnik r %.2f' % (dg, dz, dd, rn))
            info.append('(f) obrys cyfry n%d z siatki x %.2f…%.2f, y %.2f…%.2f (%.2f × %.2f): do gniazda %.2f (id %s) ≥ %g, do stożka %.2f ≥ 1,5, do dołka %.2f ≥ 1,5, narożnik r %.2f ≤ %g'
                        % (numer, x0, x1, y0, y1, x1 - x0, y1 - y0, dg, idg, P['socket_wall_min'], dz, dd, rn, P['socket_zone_r']))
    # (g) mapa wysokosci wierzchu = plytka okragla tego typu (bazowa); warianty: bez otoczenia dolkow i cyfry
    pomin = []
    if numer is not None:
        pomin += [(dl['x'], dl['y'], dl['d'] / 2 + 0.3) for dl in uklad['code_dimples']]
    prost = (nr['x'] - 3.5, nr['x'] + 3.5, nr['y'] - 3.5, nr['y'] + 3.5) if (numer is not None and nr is not None) else None
    idx = [i for i, (x, y) in enumerate(punkty_mapy)
           if not any((x - px) ** 2 + (y - py) ** 2 <= pr * pr for px, py, pr in pomin)
           and not (prost and prost[0] <= x <= prost[1] and prost[2] <= y <= prost[3])]
    m1 = mapa_promieni(bvh, [punkty_mapy[i] for i in idx], 5.0, -1)
    n_p, niezg, dzmax = porownaj_mapy(m1, [mapa_ref[i] for i in idx])
    if niezg or dzmax > 0.01:
        bledy.append('(g) mapa wierzchu: %d punktów z trafieniem tylko w jednej siatce, max |Δz| %.4f' % (niezg, dzmax))
    info.append('(g) mapa wysokości wierzchu (promienie z góry co %.2f w kole r %.1f%s) = `%s`: %d punktów, niezgodnych trafień %d, max |Δz| %.4f (≤ 0,01)'
                % (KROK_MAPY_R58, R + 0.5, '; bez otoczenia 4 dołków i cyfry' if numer is not None else '', plik_ref, n_p, niezg, dzmax))
    zg_n, n_n, bl = W.sondy_k('K-64', siatka, plik, lista)
    if zg_n != n_n:
        bledy.append('sondy %d/%d' % (zg_n, n_n))
    W.dodaj('K-64', not bledy, '%s: sondy %d/%d; %s; błędy: %s' % (plik, zg_n, n_n, '; '.join(info), '; '.join(bledy) or 'brak'),
            'kieszenie ø%g × %g w osiach A/B/C (środek ≤ 0,05, ø i głębokość ± 0,05); rowek pokrywki %g × %g na Z −%g (± 0,1; ≥ 8 kierunków); rowek klucza %g × %g od r %g (± 0,05); '
            'ścianki ≥ 1,5; sockets = kwadrat; obrys cyfry ≥ 3 od gniazd, w kole %g; wierzch = płytka okrągła tego typu [R58]'
            % (P['magnet_pocket_d'], P['magnet_pocket_depth'], cg['w'], cg['depth'], cg['z'], ks['w'], ks['h'], ks['r0'], P['socket_zone_r']), 'B',
            '%s: %d sond < 0,1 od ściany' % (plik, bl) if bl else '')
    # rzut od spodu (kieszenie, rowek klucza) do wgladu
    if numer is None:
        os.makedirs(katalog_rzutow, exist_ok=True)
        png = os.path.join(katalog_rzutow, 'rzut_spod_%s_%s.png' % (os.path.splitext(plik)[0], iter_))
        krok = 0.25
        nx = int(round(2 * (R + 1) / krok)) + 1
        pk = [(-(R + 1) + i * krok, -(R + 1) + j * krok) for j in range(nx) for i in range(nx)]
        zs = mapa_promieni(bvh, pk, -T - 5.0, 1)
        zapisz_png(png, [zs[j * nx:(j + 1) * nx] for j in range(nx)], -T, -T + max(ks['h'], max(mp['depth'] for mp in uklad['magnet_pockets'])))
        W.k['K-64']['uwaga'].append('rzut od spodu: %s' % os.path.relpath(png, KATALOG).replace('\\', '/'))


def sprawdz_wkladke_okragla(W, P, siatka, plik, siatka_kw, plik_kw, katalog_rzutow, iter_):
    """K-65 (R58): wkladka okragla - otwor i sciecie, wystep, polki, kieszenie Halla, zebro klucza (runda 2), scianka w osiach, wyciecie palcowe,
    K-56, zgodnosc obrysu zewnetrznego / uszu / kolkow / magnesow z wkladka kwadratowa, ciaglosc kanalow kablowych."""
    H, sh, c = P['insert_h'], P['insert_shelf_h'], P['insert_chamfer']
    zw = P['insert_opening'] / 2 + P['insert_wall_w']
    R, dist, kat, _w = sciecie_okraglej(P)
    luz = P['round_insert_clearance']
    ro, do = R + luz, dist + luz
    rl, s = P['round_insert_ledge_r'], P['round_insert_shelf'] / 2
    hw, hl, chh, ph = P['hall_pocket_w'], P['hall_pocket_l'], P['hall_lead_channel_h'], P['hall_wall_pass_h']
    zb_w, zb_r0, zb_h, zb_c = P['round_key_rib_w'], P['round_key_rib_r0'], P['round_key_rib_h'], P['round_key_rib_chamfer']
    fw, rw, rh = P['finger_cut_w'], P['wire_rabbet_w'], P['wire_rabbet']
    osie = osie_okragle(P)
    bvh = siatka.bvh
    beta = math.degrees(math.acos(do / ro))
    bledy, info, lista = [], [], []
    roznica_kat = lambda a, b: abs(((a - b) + 180) % 360 - 180)
    # (a) otwor o(2 ro) i sciecie
    z_o = (sh + H - c) / 2                # miedzy polka a faza otworu (w osi D stoi zebro klucza - sciecie mierzone obok)
    przod = math.degrees(math.asin(fw / 2 / ro)) + 2.0
    pr = []
    for i in range(36):
        a = 5.0 + 10.0 * i
        if roznica_kat(a, kat) <= beta + 2.0 or roznica_kat(a, -90.0) <= przod:
            continue
        pr.append(promien_od_srodka(bvh, a, z_o))
    if not pr or any(v is None for v in pr):
        bledy.append('(a) otwór: brak trafienia')
        pr = [v for v in pr if v is not None] or [float('nan')]
    elif any(abs(v - ro) > 0.05 for v in pr):
        bledy.append('(a) otwór: promień %.3f…%.3f poza %g ± 0,05' % (min(pr), max(pr), ro))
    sr = 2 * sum(pr) / len(pr)
    if abs(sr - 2 * ro) > 0.1:
        bledy.append('(a) średnica %.3f poza %g ± 0,1' % (sr, 2 * ro))
    cu, su = math.cos(math.radians(kat)), math.sin(math.radians(kat))
    voff = do * math.tan(math.radians(beta)) / 2
    scs = []
    for zz in (z_o, sh + 0.5):
        for v in (voff, -voff):
            loc = pierwsze_trafienie(bvh, (-su * v, cu * v, zz), (cu, su, 0))
            scs.append(None if loc is None else loc.x * cu + loc.y * su)
    if any(v is None for v in scs) or any(abs(v - do) > 0.05 for v in scs):
        bledy.append('(a) ścięcie: %s zamiast %.3f' % (', '.join('—' if v is None else '%.3f' % v for v in scs), do))
    lista += [((0, 0, z_o), False), (((ro - 0.2), 0, z_o), False), (((ro + 0.2), 0, z_o), True), ((ro - 0.15, 0, H - 0.2), False), ((ro + c + 0.2, 0, H - 0.2), True)]
    info.append('(a) otwór na Z %.2f z %d promieni: r %.3f…%.3f, ø %.3f (zadane %g ± 0,1); ścięcie na %g° promieniami odsuniętymi o ±%.1f od osi (w osi żebro klucza), Z %.2f i %.2f: %s (zadane %.3f)'
                % (z_o, len(pr), min(pr), max(pr), sr, 2 * ro, kat, voff, z_o, sh + 0.5, ' / '.join('—' if v is None else '%.3f' % v for v in scs), do))
    # (b) wystep r = round_insert_ledge_r na polowie wysokosci polki (kierunki poza polkami w osiach i poza wycieciem palcowym)
    pw = []
    przod_w = math.degrees(math.asin(fw / 2 / rl)) + 3.0
    for a in range(0, 360, 10):
        if any(roznica_kat(a, osie[k][0]) <= 15.0 for k in 'ABCD') or roznica_kat(a, -90.0) <= przod_w:
            continue
        pw.append((a, promien_od_srodka(bvh, float(a), sh / 2)))
    if any(v is None or abs(v - rl) > 0.05 for _a, v in pw):
        bledy.append('(b) występ: r %s poza %g ± 0,05' % (', '.join('—' if v is None else '%.3f' % v for _a, v in pw), rl))
    pw_v = [v for _a, v in pw if v is not None] or [float('nan')]
    info.append('(b) występ na Z %.2f z %d promieni: r %.3f…%.3f (zadane %g)' % (sh / 2, len(pw), min(pw_v), max(pw_v), rl))
    # (c) wysokosc polki: promienie z gory na wystepie (lewo, prawo, tyl) i na 4 polkach (miedzy kieszenia/kolkiem a bokiem, od strony srodka)
    rs = (rl + ro) / 2
    pk = [('występ +X', rs, 0.0), ('występ −X', -rs, 0.0), ('występ +Y', 0.0, rs)]
    dk = hw / 2 + (s - hw / 2) / 2
    for k in 'ABCD':
        _a, cx, cy = osie[k]
        pk.append(('półka %s' % k, cx - math.copysign(dk, cx), cy))
        lista += [((cx - math.copysign(s - 0.5, cx), cy - math.copysign(s - 0.5, cy), sh / 2), True),
                  ((cx - math.copysign(s + 0.5, cx), cy - math.copysign(s + 0.5, cy), sh / 2), False),
                  ((cx - math.copysign(dk, cx), cy, sh - 0.2), True), ((cx - math.copysign(dk, cx), cy, sh + 0.2), False)]
    hz = []
    for nz, x, y in pk:
        loc = pierwsze_trafienie(bvh, (x, y, H + 5.0), (0, 0, -1))
        hz.append((nz, None if loc is None else loc.z))
    if any(z is None or abs(z - sh) > 0.02 for _n, z in hz):
        bledy.append('(c) półka: Z %s zamiast %g' % (', '.join('%s %s' % (n, '—' if z is None else '%.3f' % z) for n, z in hz), sh))
    info.append('(c) górna powierzchnia półki z promieni z góry: ' + ', '.join('%s %s' % (n, '—' if z is None else '%.3f' % z) for n, z in hz) + ' (zadane %g ± 0,02)' % sh)
    # (d) kieszenie Halla pod osiami A, B, C + kanal pod polka i przelot
    z_k = (chh + sh) / 2
    pom_h = []
    for k in 'ABC':
        _a, cx, cy = osie[k]
        lista += [((cx, cy, sh / 2), False), ((cx, cy, chh / 2), False),
                  ((cx + hw / 2 - 0.15, cy, z_k), False), ((cx - hw / 2 + 0.15, cy, z_k), False), ((cx, cy + hl / 2 - 0.15, z_k), False), ((cx, cy - hl / 2 + 0.15, z_k), False),
                  ((cx + hw / 2 + 0.2, cy, z_k), True), ((cx - hw / 2 - 0.2, cy, z_k), True), ((cx, cy + hl / 2 + 0.2, z_k), True), ((cx, cy - hl / 2 - 0.2, z_k), True)]
        d = Vector((cx, cy, 0)).normalized()
        t1 = ro - P['round_magnet_r'] - 0.5
        t2 = ro - P['round_magnet_r'] + 1.0
        lista += [((cx + d.x * t1, cy + d.y * t1, chh / 2), False), ((cx + d.x * t1, cy + d.y * t1, (chh + sh) / 2), True),
                  ((cx + d.x * t2, cy + d.y * t2, (chh + ph) / 2), False), ((cx + d.x * t2, cy + d.y * t2, ph + 0.25), True)]
        sw = srodek_wneki(bvh, cx, cy, z_k)
        if sw is None:
            bledy.append('(d) kieszeń Halla %s: brak trafień' % k)
            continue
        pom_h.append((k, sw[0], sw[1], sw[2], sw[3]))
        if math.hypot(sw[0] - cx, sw[1] - cy) > 0.05 or abs(sw[2] - hw) > 0.05 or abs(sw[3] - hl) > 0.05:
            bledy.append('(d) kieszeń Halla %s: środek (%.3f, %.3f), %.3f × %.3f' % (k, sw[0], sw[1], sw[2], sw[3]))
    info.append('(d) kieszenie Halla (Z %.2f; środek, X × Y): ' % z_k + '; '.join('%s (%.3f, %.3f) %.3f × %.3f' % p for p in pom_h)
                + ' (osie A/B/C = osie magnesów płytki, %g × %g ± 0,05)' % (hw, hl))
    # (e) [runda 2/3] zebro klucza na osi D: szerokosc, poczatek, wierzch, czesc nad wierzchem wkladki konczy sie na round_key_rib_top_r1
    # z faza zewnetrzna (runda 3, P1 recenzji rundy 2: promienie poziome z zewnatrz na 2 wysokosciach -> koniec i nachylenie fazy),
    # zrosniecie ze sciana ponizej wierzchu (faza otworu za zebrem wypelniona), fazy gornych krawedzi; brak kolka kwadratowego
    r1 = P['round_key_rib_top_r1']
    uv = lambda u, v, z: (u * cu - v * su, u * su + v * cu, z)
    vv = lambda q: -q[0] * su + q[1] * cu
    uu = lambda q: q[0] * cu + q[1] * su
    um, zm = (zb_r0 + do) / 2, sh + (zb_h - zb_c) / 2
    zt = sh + zb_h
    z_fz = zt - zb_c                                   # poczatek fazy gornych krawedzi
    z_lo = max(H, z_fz)
    u_zew = lambda z: r1 - max(0.0, z - z_fz)          # zewnetrzny koniec czesci gornej na wysokosci z (faza 45 st.)
    ut = (zb_r0 + r1) / 2                              # srodek wierzchu (u r0 + c ... r1 - c)
    zz = (z_lo + 0.25 * (zt - z_lo), z_lo + 0.75 * (zt - z_lo))
    tp = pierwsze_trafienie(bvh, uv(um, zb_w / 2 + 1.5, zm), (su, -cu, 0))
    tm = pierwsze_trafienie(bvh, uv(um, -zb_w / 2 - 1.5, zm), (-su, cu, 0))
    t0 = pierwsze_trafienie(bvh, uv(zb_r0 - 2.0, 0, zm), (cu, su, 0))
    tg = pierwsze_trafienie(bvh, uv(ut, 0, H + 5.0), (0, 0, -1))
    tz = [pierwsze_trafienie(bvh, uv(do + 2.0, 0, z_), (-cu, -su, 0)) for z_ in zz]
    pc = P['insert_opening'] / 2 - P['orient_post_gap'] - P['orient_post'] / 2
    zs_ = (H + zt) / 2
    lista += [(uv(um, 0, zm), True), (uv(um, zb_w / 2 - 0.2, zm), True), (uv(um, -zb_w / 2 + 0.2, zm), True),
              (uv(um, zb_w / 2 + 0.2, zm), False), (uv(um, -zb_w / 2 - 0.2, zm), False),
              (uv(zb_r0 - 0.2, 0, zm), False), (uv(zb_r0 + 0.2, 0, zm), True),
              (uv(ut, 0, zt - 0.15), True), (uv(ut, 0, zt + 0.15), False),
              (uv(ut, zb_w / 2 - zb_c + 0.35, zt - 0.15), False), (uv(ut, zb_w / 2 - zb_c - 0.2, zt - 0.15), True),
              (uv(zb_r0 + zb_c - 0.35, 0, zt - 0.15), False), (uv(r1 - zb_c + 0.35, 0, zt - 0.15), False),
              (uv(u_zew(zs_) + 0.2, 0, zs_), False), (uv(u_zew(zs_) - 0.2, 0, zs_), True),
              (uv(r1 + 0.15, 0, H + 0.15), False), (uv(do - 0.15, 0, H + 0.15), False),
              (uv(do + c / 2, 0, H - c / 4), True), (uv(do + c / 2, zb_w / 2 + 1.0, H - c / 4), False),
              ((pc, -pc, sh + P['orient_post_h'] - 0.5), False)]
    if None in [tp, tm, t0, tg] + tz:
        bledy.append('(e) żebro klucza: brak trafień')
        szer_z = off_z = r0_z = zt_z = r1_z = nach = float('nan')
        zew_z = (float('nan'), float('nan'))
    else:
        szer_z, off_z = vv(tp) - vv(tm), (vv(tp) + vv(tm)) / 2
        r0_z, zt_z = uu(t0), tg.z
        zew_z = tuple(uu(t) for t in tz)
        r1_z = zew_z[0] + max(0.0, zz[0] - z_fz)
        nach = (zew_z[1] - zew_z[0]) / (zz[1] - zz[0])
        if (abs(szer_z - zb_w) > 0.05 or abs(off_z) > 0.05 or abs(r0_z - zb_r0) > 0.05 or abs(zt_z - zt) > 0.02
                or any(abs(u_ - u_zew(z_)) > 0.05 for u_, z_ in zip(zew_z, zz))):
            bledy.append('(e) żebro klucza: szerokość %.3f (oś %.3f), początek r %.3f, wierzch %.3f, koniec nad wierzchem u %.3f / %.3f na Z %.2f / %.2f'
                         % (szer_z, off_z, r0_z, zt_z, zew_z[0], zew_z[1], zz[0], zz[1]))
    info.append('(e) żebro klucza na %g°: szerokość %.3f (oś przesunięta o %.3f), początek r %.3f, wierzch Z %.3f (zadane %g / %g / %g); [runda 3] część nad wierzchem '
                'wkładki (Z %g…%g): koniec zewnętrzny u %.3f / %.3f na Z %.2f / %.2f (zadane %.3f / %.3f) → koniec r %.3f (zadane `round_key_rib_top_r1` %g; lico ścięcia %.3f), '
                'nachylenie fazy zewnętrznej %.2f (zadane −1, 45°); poniżej Z %g zrośnięte ze ścianą do lica ścięcia (faza otworu za żebrem wypełniona — sonda), fazy %g na bokach, '
                'czole i krawędzi zewnętrznej (sondy); nad wierzchem przy licu ścięcia pusto (sonda); dawny kołek kwadratowy (%.1f, %.1f) — brak'
                % (kat, szer_z, off_z, r0_z, zt_z, zb_w, zb_r0, zt, H, zt, zew_z[0], zew_z[1], zz[0], zz[1], u_zew(zz[0]), u_zew(zz[1]), r1_z, r1, do, nach,
                   H, zb_c, pc, -pc))
    # (f) scianka ramy w osiach (lewo, prawo, tyl) i dno w osi po rowku kablowym
    z_s = (sh + H - c) / 2
    sc_o, dno_o = [], []
    for a in (0.0, 90.0, 180.0):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        t = trafienia(bvh, (0, 0, z_s), (ca, sa, 0))
        t2 = trafienia(bvh, (0, 0, rh / 2), (ca, sa, 0))
        sc_o.append(t[1] - t[0] if len(t) >= 2 else float('nan'))
        dno_o.append(t2[1] - t2[0] if len(t2) >= 2 else float('nan'))
    if any(not (v >= 1.5 - 1e-6) for v in sc_o + dno_o) or any(abs(v - (zw - ro)) > 0.05 for v in sc_o):
        bledy.append('(f) ścianka w osiach %s, dno po rowku %s' % (sc_o, dno_o))
    info.append('(f) ścianka ramy w osiach +X / +Y / −X (Z %.2f): %s (zadane %.2f ≥ 1,5); dno w osi po rowku kablowym (Z %.2f): %s (≥ 1,5)'
                % (z_s, ' / '.join('%.3f' % v for v in sc_o), zw - ro, rh / 2, ' / '.join('%.3f' % v for v in dno_o)))
    # (g) wyciecie palcowe przez rame i wystep
    yw = -(rl + ro) / 2
    lista += [((0, -(ro + zw) / 2, (sh + H) / 2), False), ((0, -(ro + zw) / 2, 0.3), False), ((0, yw, sh / 2), False),
              ((fw / 2 - 0.2, -math.sqrt(rl * rl - (fw / 2 - 0.2) ** 2) - 0.2, sh / 2), False),
              ((fw / 2 + 0.3, -(rl + 0.5), sh / 2), True), ((fw / 2 + 5, -(ro + zw) / 2, (sh + H) / 2), True), ((-fw / 2 - 5, -(ro + zw) / 2, (sh + H) / 2), True)]
    tp = pierwsze_trafienie(bvh, (0, yw, sh / 2), (1, 0, 0))
    tm = pierwsze_trafienie(bvh, (0, yw, sh / 2), (-1, 0, 0))
    szer = (tp.x - tm.x) if (tp and tm) else float('nan')
    if not abs(szer - fw) <= 0.05:
        bledy.append('(g) wycięcie palcowe %.3f zamiast %g' % (szer, fw))
    info.append('(g) wycięcie palcowe przez występ (y %.2f): szerokość %.3f (zadane %g)' % (yw, szer, fw))
    # (h) K-56: nic poza obrysem ramy dla y < krawedz tylna ramy
    zle = sum(1 for v in siatka.bm.verts if v.co.y < zw - 1e-3 and (abs(v.co.x) > zw + 1e-3 or v.co.y < -zw - 1e-3))     # 1e-3: float32 STL (52,4 -> 52,39999771)
    if zle:
        bledy.append('(h) %d wierzchołków poza obrysem ramy dla y < %g' % (zle, zw))
    info.append('(h) K‑56: wierzchołki poza obrysem ramy ±%g dla y < %g: %d' % (zw, zw, zle))
    # (i) obrys zewnetrzny, uszy, kolki, magnesy = wkladka kwadratowa: sondy K-29 i K-30 + mapy wysokosci z gory i od spodu poza ramka |x|, |y| < zw - 0,9
    zg29, n29, _b = W.sondy_k('K-65', siatka, plik, SONDY_K29)
    zg30, n30, _b = W.sondy_k('K-65', siatka, plik, SONDY_K30)
    if zg29 != n29 or zg30 != n30:
        bledy.append('(i) sondy K‑29 %d/%d, K‑30 %d/%d' % (zg29, n29, zg30, n30))
    g = zw - 0.9
    ex = P['tab_pos_x'] + P['tab_w'] / 2 + 1.0
    krok = 0.5
    pkt = []
    y = -zw - 1.0 + 0.13
    while y <= P['tab_end_y'] + 1.0:
        x = -ex + 0.13
        while x <= ex:
            if abs(x) >= g or abs(y) >= g:
                pkt.append((x, y))
            x += krok
        y += krok
    wyn_m = []
    for z0, kier in ((H + 10.0, -1), (-P['tab_pin_h'] - 5.0, 1)):
        wyn_m.append(porownaj_mapy(mapa_promieni(bvh, pkt, z0, kier), mapa_promieni(siatka_kw.bvh, pkt, z0, kier)))
    if any(nz or dz > 0.01 for _n, nz, dz in wyn_m):
        bledy.append('(i) mapy wysokości różne od wkładki kwadratowej: %s' % wyn_m)
    info.append('(i) zgodność z `%s`: sondy K‑29 %d/%d, K‑30 %d/%d; mapy wysokości z góry / od spodu poza kwadratem |x|, |y| < %.1f (krok %g, %d punktów): '
                'niezgodnych trafień %d / %d, max |Δz| %.4f / %.4f (≤ 0,01)'
                % (plik_kw, zg29, n29, zg30, n30, g, krok, len(pkt), wyn_m[0][1], wyn_m[1][1], wyn_m[0][2], wyn_m[1][2]))
    # (j) ciaglosc kanalow kablowych: sondy co <= 0,5 mm na Z rowka/2 wzdluz drogi od kazdej kieszeni do szczeliny przy uchu
    rxi, kw, kx_c = P['tab_root_x_in'], P['tab_cable_channel_w'], P['tab_cable_channel_x']
    yc = (zw + P['tab_root_y1']) / 2
    xr = zw - rw / 2
    z_j = min(chh, P['tab_cable_channel_h'], rh) / 2

    def droga(punkty):
        wyn = []
        for (x0, y0), (x1, y1) in zip(punkty, punkty[1:]):
            n = max(1, int(math.ceil(math.hypot(x1 - x0, y1 - y0) / 0.5)))
            wyn += [(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n, z_j) for i in range(n)]
        return wyn + [(punkty[-1][0], punkty[-1][1], z_j)]
    drogi = {}
    for k in 'ABC':
        _a, cx, cy = osie[k]
        sx = math.copysign(1.0, cx)
        pts = [(cx, cy), (sx * xr, math.copysign(xr, cy))]
        if cy < 0:
            pts.append((sx * xr, xr))              # wzdluz rowka bocznego do naroza tylnego
        pts += [(sx * (rxi + kw / 2), xr), (sx * (rxi + kw / 2), yc), (sx * kx_c, yc), (sx * kx_c, P['wire_slot_y'] - 0.5)]
        drogi[k] = droga(pts)
    wyn_j = {}
    for k, pts in drogi.items():
        zle_j = [p for p in pts if siatka.w_bryle(p)[0]]
        wyn_j[k] = (len(pts), len(zle_j), zle_j[:2])
        if zle_j:
            bledy.append('(j) kanał od kieszeni %s: %d punktów w bryle, np. %s' % (k, len(zle_j), zle_j[:2]))
    info.append('(j) ciągłość kanału kablowego (sondy co ≤ 0,5 na Z %.2f: przekątna → rowek → kanał pod nasadą → pod uchem do y %g): %s'
                % (z_j, P['wire_slot_y'] - 0.5, '; '.join('%s %d punktów, w bryle %d' % (k, n, z) for k, (n, z, _p) in wyn_j.items())))
    zg_n, n_n, bl = W.sondy_k('K-65', siatka, plik, lista)
    if zg_n != n_n:
        bledy.append('sondy %d/%d' % (zg_n, n_n))
    W.dodaj('K-65', not bledy, '%s: sondy %d/%d; %s; błędy: %s' % (plik, zg_n, n_n, '; '.join(info), '; '.join(bledy) or 'brak'),
            'otwór ø%g ± 0,1, ścięcie %.3f ± 0,05; występ r %g; półka Z %g; kieszenie Halla w osiach A/B/C; żebro klucza %g od r %g (poniżej Z %g do lica ścięcia, nad nim do r %g '
            'z fazą 45° ± 0,05), wierzch Z %g; ścianka w osiach ≥ 1,5; wycięcie %g; K‑56; obrys/uszy/kołki/magnesy = wkładka kwadratowa; kanały ciągłe [R58]'
            % (2 * ro, do, rl, sh, zb_w, zb_r0, H, P['round_key_rib_top_r1'], sh + zb_h, fw), 'B',
            '%s: %d sond < 0,1 od ściany' % (plik, bl) if bl else '')
    os.makedirs(katalog_rzutow, exist_ok=True)
    for nz, z0, kier, lo, hi in (('gora', H + 10.0, -1, 0.0, H + P['label_relief_h']), ('spod', -P['tab_pin_h'] - 5.0, 1, -P['tab_pin_h'], ph)):
        png = os.path.join(katalog_rzutow, 'rzut_%s_%s_%s.png' % (nz, os.path.splitext(plik)[0], iter_))
        krok_r = 0.25
        nx, ny = int(round(2 * ex / krok_r)) + 1, int(round((P['tab_end_y'] + zw + 2) / krok_r)) + 1
        pr_ = [(-ex + i * krok_r, -zw - 1.0 + j * krok_r) for j in range(ny) for i in range(nx)]
        zs = mapa_promieni(bvh, pr_, z0, kier)
        zapisz_png(png, [zs[j * nx:(j + 1) * nx] for j in range(ny)], lo, hi)
        W.k['K-65']['uwaga'].append('rzut %s: %s' % ('z góry' if nz == 'gora' else 'od spodu', os.path.relpath(png, KATALOG).replace('\\', '/')))


def sprawdz_pokrywke_okragla(W, P, siatka, plik):
    """K-66 (R58): pokrywka okragla - srednice, wysokosc, wierzch, 4 garby (kat, wystep, Z), wyciecia palcowe, 8 szczelin odciazajacych
    (runda 2) zakonczonych otworem przelotowym (runda 3)."""
    rw, rz, wys = wymiary_pokrywki_okraglej(P)
    tw = P['cover_top_t']
    bvh = siatka.bvh
    bledy, info, lista = [], [], []
    rm = (rw + rz) / 2
    z_m = -wys / 2
    # srednice z promieni na Z -wys/2 (24 kierunki)
    rwew, rzew = [], []
    for i in range(24):
        a = 7.5 + 15.0 * i
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        t = trafienia(bvh, (0, 0, z_m), (ca, sa, 0))
        if len(t) < 2:
            bledy.append('brak trafień na %g°' % a)
            continue
        rwew.append(t[0])
        rzew.append(t[1])
    if any(abs(v - rw) > 0.05 for v in rwew) or any(abs(v - rz) > 0.05 for v in rzew):
        bledy.append('średnice: wewn. r %.3f…%.3f, zewn. r %.3f…%.3f' % (min(rwew), max(rwew), min(rzew), max(rzew)))
    info.append('średnica wewn. %.3f…%.3f, zewn. %.3f…%.3f z %d promieni na Z %g (zadane %g / %g ± 0,1)'
                % (2 * min(rwew), 2 * max(rwew), 2 * min(rzew), 2 * max(rzew), len(rwew), z_m, 2 * rw, 2 * rz))
    # wysokosc i wierzch
    g = pierwsze_trafienie(bvh, (0, 0, z_m), (0, 0, 1))
    bb = siatka.bbox
    mapa = siatka.mapa_wysokosci(-rw * 0.8, rw * 0.8, -rw * 0.8, rw * 0.8, 0.5, 5.0)
    zs = [z for w in mapa for z in w if z is not None]
    if g is None or abs(g.z + tw) > 0.02 or abs(bb[4] + wys) > 0.02 or abs(bb[5]) > 0.02 or max(zs) > 0.02 or min(zs) < -0.02:
        bledy.append('wierzch/wysokość: spód wierzchu %s, Z %.3f…%.3f, wierzch %.3f…%.3f' % ('—' if g is None else '%.3f' % g.z, bb[4], bb[5], min(zs), max(zs)))
    info.append('grubość wierzchu %.3f (zadane %g); Z %.3f…%.3f (wysokość %.3f, zadane %g); wierzch z promieni (|x|, |y| ≤ %.1f, %d punktów) Z %.3f…%.3f'
                % (-g.z if g else float('nan'), tw, bb[4], bb[5], bb[5] - bb[4], wys, rw * 0.8, len(zs), min(zs), max(zs)))
    lista += [((0, 0, -tw / 2), True), ((0, 0, -tw - 0.5), False), ((0, 0, -wys + 0.1), False)]
    for a in (0.0, 90.0, 180.0, 270.0):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        lista += [((rm * ca, rm * sa, z_m), True), (((rw - 0.2) * ca, (rw - 0.2) * sa, z_m), False), (((rz + 0.2) * ca, (rz + 0.2) * sa, z_m), False)]
    # garby: wystep na kacie i +-3 st., brak obok luku; Z z promieni pionowych przy licu; liczba sektorow przy przegladzie co 1 st.
    zsn, wy, hg = P['cover_snap_z'], P['cover_snap_bump'], P['cover_snap_hgt']
    pol_luku = math.degrees(P['cover_snap_w'] / rw / 2)
    garby = []
    for kat in P['round_cover_snap_angles']:
        v = [promien_od_srodka(bvh, kat + d, zsn) for d in (0.0, -3.0, 3.0)]
        # obok luku: w polowie przerwy miedzy koncem garbu a szczelina odciazajaca (runda 2)
        d_obok = (pol_luku + math.degrees(P['round_cover_slit_offset'] / rw) - math.degrees(math.asin(P['round_cover_slit_w'] / 2 / rw))) / 2
        vo = [promien_od_srodka(bvh, kat + d, zsn) for d in (-d_obok, d_obok)]
        ca, sa = math.cos(math.radians(kat)), math.sin(math.radians(kat))
        rr = rw - wy / 4
        gz = pierwsze_trafienie(bvh, (rr * ca, rr * sa, zsn + hg + 0.5), (0, 0, -1))
        dz = pierwsze_trafienie(bvh, (rr * ca, rr * sa, zsn - hg - 0.5), (0, 0, 1))
        if None in v + vo or gz is None or dz is None:
            bledy.append('garb %g°: brak trafień' % kat)
            continue
        garby.append((kat, rw - v[0], rw - min(v[1:]), rw - max(v[1:]), vo[0], vo[1], (gz.z + dz.z) / 2, gz.z - dz.z))
        if any(abs(rw - x - wy) > 0.05 for x in v) or any(abs(x - rw) > 0.05 for x in vo):
            bledy.append('garb %g°: występ %s, obok łuku r %s' % (kat, ['%.3f' % (rw - x) for x in v], ['%.3f' % x for x in vo]))
        if abs((gz.z + dz.z) / 2 - zsn) > 0.05:
            bledy.append('garb %g°: środek Z %.3f zamiast %g' % (kat, (gz.z + dz.z) / 2, zsn))
        lista += [(((rw - wy / 2) * ca, (rw - wy / 2) * sa, zsn), True), (((rw - wy - 0.15) * ca, (rw - wy - 0.15) * sa, zsn), False)]
    sektory, w_garbie = [], False
    for i in range(360):
        v = promien_od_srodka(bvh, float(i) + 0.5, zsn)
        jest = v is not None and v < rw - wy / 2
        if jest and not w_garbie:
            sektory.append([i, i])
        if jest:
            sektory[-1][1] = i
        w_garbie = jest
    if len(sektory) > 1 and sektory[0][0] == 0 and sektory[-1][1] == 359:
        sektory[0][0] = sektory[-1][0] - 360
        sektory.pop()
    srodki = sorted(((a + b + 1) / 2.0) % 360 for a, b in sektory)
    ocz = sorted(float(k) % 360 for k in P['round_cover_snap_angles'])
    if len(srodki) != len(ocz) or any(roznica > 1.0 for roznica in (abs(((a - b) + 180) % 360 - 180) for a, b in zip(srodki, ocz))):
        bledy.append('przegląd co 1°: sektory garbów %s (oczekiwane %s)' % (srodki, ocz))
    info.append('garby (kąt: występ w osi / ±3° min…max, r obok łuku ±%.2f° — między końcem garbu a szczeliną, środek Z, wysokość Z): ' % d_obok
                + '; '.join('%g°: %.3f / %.3f…%.3f, %.3f / %.3f, %.3f, %.3f' % (k, a, b, c_, d, e, f, h) for k, a, b, c_, d, e, f, h in garby)
                + '; przegląd co 1° na Z %g: %d sektorów, środki %s (zadane %s)' % (zsn, len(srodki), ', '.join('%.1f' % a for a in srodki), ', '.join('%g' % a for a in ocz)))
    # wyciecia palcowe z przodu i z tylu
    fw, fh = P['cover_finger_w'], P['cover_finger_h']
    yk = math.sqrt(rm * rm - (fw / 2) ** 2)
    wyc = []
    for zn in (-1, 1):
        lista += [((0, zn * rm, -wys + fh / 2), False), ((0, zn * rm, -wys + fh + 0.5), True),
                  ((rm * math.sin(math.radians(25.0)), zn * rm * math.cos(math.radians(25.0)), -wys + fh / 2), True)]
        tp = pierwsze_trafienie(bvh, (0, zn * yk, -wys + fh / 2), (1, 0, 0))
        tm = pierwsze_trafienie(bvh, (0, zn * yk, -wys + fh / 2), (-1, 0, 0))
        tg = pierwsze_trafienie(bvh, (0, zn * rm, -wys - 1.0), (0, 0, 1))
        szer = (tp.x - tm.x) if (tp and tm) else float('nan')
        wys_w = (tg.z + wys) if tg else float('nan')
        wyc.append((szer, wys_w))
        if not (abs(szer - fw) <= 0.05 and abs(wys_w - fh) <= 0.05):
            bledy.append('wycięcie %s: %.3f × %.3f' % ('tył' if zn > 0 else 'przód', szer, wys_w))
    info.append('wycięcia palcowe przód / tył: %s (zadane %g × %g)' % (' / '.join('%.3f × %.3f' % w for w in wyc), fw, fh))
    # runda 2/3 (P2 recenzji): szczeliny odciazajace - 8 szt.: szerokosc czesci prostej (promienie styczne na r srodka scianki, w polowie
    # czesci prostej); [runda 3] otwor koncowy o round_cover_slit_end_d: srodek Z i srednica z promieni pionowych z wnetrza otworu przy
    # v = +-(sw/2 + dk/2)/2 (obok szczeliny), szerokosc na Z srodka, gorny koniec (promien od dolu w osi szczeliny) i jego odstep od spodu
    # wierzchu; przelotowosc (sondy przy obu licach); przeglad co 0,1 st. na polowie czesci prostej i na Z srodka otworu; odstepy katowe
    # szczelin i otworow od siebie, od wyciec palcowych i od garbow (wlasna szczelina i jej otwor - pomijane)
    sw, sl, dk = P['round_cover_slit_w'], P['round_cover_slit_h'], P['round_cover_slit_end_d']
    zk = -wys + sl                                      # srodek otworu koncowego
    z_s = (-wys + zk - dk / 2) / 2                      # polowa czesci prostej (pod otworem)
    vo = (sw / 2 + dk / 2) / 2                          # przesuniecie styczne pomiaru otworu (w otworze, poza szczelina)
    spod_w = g.z if g is not None else -tw              # spod wierzchu pokrywki (z promienia na poczatku K-66)
    pom_s = []
    for kat, zn in polozenia_szczelin_pokrywki(P):
        ca, sa = math.cos(math.radians(kat)), math.sin(math.radians(kat))
        t_ = Vector((-sa, ca, 0))
        p = Vector((rm * ca, rm * sa, z_s))
        a1 = pierwsze_trafienie(bvh, p, t_)
        a2 = pierwsze_trafienie(bvh, p, -t_)
        go = pierwsze_trafienie(bvh, (rm * ca, rm * sa, -wys - 1.0), (0, 0, 1))
        po = Vector((rm * ca, rm * sa, zk))
        b1 = pierwsze_trafienie(bvh, po, t_)
        b2 = pierwsze_trafienie(bvh, po, -t_)
        pion = []
        for zn_v in (1, -1):
            q = po + t_ * (zn_v * vo)
            pion += [pierwsze_trafienie(bvh, q, (0, 0, 1)), pierwsze_trafienie(bvh, q, (0, 0, -1))]
        if None in [a1, a2, go, b1, b2] + pion:
            bledy.append('szczelina %.2f°: brak trafień' % kat)
            continue
        szer = (a1 - p).length + (a2 - p).length
        szer_o = (b1 - po).length + (b2 - po).length
        zc = sum(t.z for t in pion) / 4
        d_o = sum(2 * math.sqrt(((pion[i].z - pion[i + 1].z) / 2) ** 2 + vo * vo) for i in (0, 2)) / 2
        gora = go.z
        pom_s.append((kat, szer, zc + wys, d_o, szer_o, gora, spod_w - gora))
        if (abs(szer - sw) > 0.05 or abs(zc - zk) > 0.05 or abs(d_o - dk) > 0.05 or abs(szer_o - dk) > 0.05 or abs(gora - (zk + dk / 2)) > 0.05
                or spod_w - gora < 1.5 - 1e-6):
            bledy.append('szczelina %.2f°: szerokość %.3f, środek otworu Z %.3f, otwór ø%.3f / szerokość %.3f, górny koniec Z %.3f (do spodu wierzchu %.3f)'
                         % (kat, szer, zc, d_o, szer_o, gora, spod_w - gora))
        db = math.degrees((sw / 2 + 0.25) / rm)
        lista += [(((rw + 0.15) * ca, (rw + 0.15) * sa, z_s), False), (((rz - 0.15) * ca, (rz - 0.15) * sa, z_s), False), ((rm * ca, rm * sa, z_s), False),
                  ((rm * math.cos(math.radians(kat + db)), rm * math.sin(math.radians(kat + db)), z_s), True),
                  ((rm * math.cos(math.radians(kat - db)), rm * math.sin(math.radians(kat - db)), z_s), True),
                  ((rm * ca, rm * sa, zk + dk / 2 + 0.2), True), ((rm * ca, rm * sa, zk + dk / 2 - 0.2), False),
                  (tuple(po + t_ * vo), False), (tuple(po - t_ * vo), False),
                  (((rw + 0.15) * ca, (rw + 0.15) * sa, zk), False), (((rz - 0.15) * ca, (rz - 0.15) * sa, zk), False),
                  (tuple(po + t_ * vo - Vector((0, 0, dk / 2 + 0.3))), True), (tuple(po - t_ * vo - Vector((0, 0, dk / 2 + 0.3))), True)]

    def przeglad(z_p):
        sekt, w_s = [], False
        for i in range(3600):
            a = math.radians(i * 0.1 + 0.05)
            jest = pierwsze_trafienie(bvh, (0, 0, z_p), (math.cos(a), math.sin(a), 0)) is None
            if jest and not w_s:
                sekt.append([i, i])
            if jest:
                sekt[-1][1] = i
            w_s = jest
        if len(sekt) > 1 and sekt[0][0] == 0 and sekt[-1][1] == 3599:
            sekt[0][0] = sekt[-1][0] - 3600
            sekt.pop()
        return sorted((((a + b + 1) / 20.0) % 360, (b - a + 1) / 10.0) for a, b in sekt)
    ocz_s = sorted(k % 360 for k, _z in polozenia_szczelin_pokrywki(P))
    prz_s, prz_o = przeglad(z_s), przeglad(zk)
    sr_s, sr_o = [a for a, _w in prz_s], [a for a, _w in prz_o]
    for nz_p, sr_ in (('szczelin', sr_s), ('otworów', sr_o)):
        if len(sr_) != len(ocz_s) or any(abs(((a - b) + 180) % 360 - 180) > 0.2 for a, b in zip(sr_, ocz_s)):
            bledy.append('przegląd %s: %s (oczekiwane %s)' % (nz_p, sr_, ocz_s))
    sz_o = 2 * math.degrees(math.asin(dk / 2 / rz))     # promien od osi przechodzi przez otwor, gdy mija oba lica: do 2 asin(r / rz)
    if any(abs(w_ - sz_o) > 0.25 for _a, w_ in prz_o):
        bledy.append('przegląd otworów: szerokości %s° (oczekiwane %.2f°)' % (['%.1f' % w_ for _a, w_ in prz_o], sz_o))
    pol_s = math.degrees(math.asin(sw / 2 / rw))
    pol_o = math.degrees(math.asin(dk / 2 / rw))
    zakresy = [('szczelina', k - pol_s, k + pol_s, i) for i, (k, _z) in enumerate(polozenia_szczelin_pokrywki(P))]
    zakresy += [('otwór', k - pol_o, k + pol_o, i) for i, (k, _z) in enumerate(polozenia_szczelin_pokrywki(P))]
    zakresy += [('wycięcie', c_ - math.degrees(math.asin(fw / 2 / rw)), c_ + math.degrees(math.asin(fw / 2 / rw)), None) for c_ in (-90.0, 90.0)]
    zakresy += [('garb', float(k) - pol_luku, float(k) + pol_luku, None) for k in P['round_cover_snap_angles']]
    odst = []
    for i, (n1, a1_, b1_, i1) in enumerate(zakresy):
        for n2, a2_, b2_, i2 in zakresy[i + 1:]:
            if not ({'szczelina', 'otwór'} & {n1, n2}) or (i1 is not None and i1 == i2):
                continue
            c1, c2 = (a1_ + b1_) / 2, (a2_ + b2_) / 2
            dc = abs(((c1 - c2) + 180) % 360 - 180)
            odst.append((dc - (b1_ - a1_) / 2 - (b2_ - a2_) / 2, '%s–%s' % tuple(sorted((n1, n2)))))
    min_odst = {}
    for v, nz in odst:
        min_odst[nz] = min(min_odst.get(nz, 1e9), v)
    if any(v <= 0 for v in min_odst.values()):
        bledy.append('szczeliny / otwory nachodzą: %s' % min_odst)
    info.append('szczeliny odciążające [runda 2, runda 3: wysokość %g + otwór końcowy ø%g]: %d szt. (kąt: szerokość części prostej na Z %g / środek otworu od dołu kołnierza / '
                'ø otworu z promieni pionowych przy v ±%.2f / szerokość otworu na Z %g / górny koniec Z / odstęp do spodu wierzchu Z %.3f) %s (zadane %g / %g / %g / %g / %g / ≥ 1,5); '
                'przegląd co 0,1°: na Z %g %d przelotowych sektorów, środki %s; na Z %g (środek otworów) %d sektorów, środki %s, szerokości %s° (oczekiwane %.2f°) (zadane środki %s); '
                'najmniejsze odstępy kątowe po licu r %.1f (otwór i jego szczelina pominięte; otwory leżą na Z %g…%g, garby na Z %g, wycięcia na Z %g…%g): %s'
                % (sl, dk, len(pom_s), z_s, vo, zk, spod_w, '; '.join('%.2f°: %.3f / %.3f / %.3f / %.3f / %.3f / %.3f' % p for p in pom_s), sw, sl, dk, dk, zk + dk / 2,
                   z_s, len(sr_s), ', '.join('%.2f' % a for a in sr_s), zk, len(sr_o), ', '.join('%.2f' % a for a in sr_o), ', '.join('%.1f' % w_ for _a, w_ in prz_o), sz_o,
                   ', '.join('%.2f' % a for a in ocz_s), rw, zk - dk / 2, zk + dk / 2, zsn, -wys, -wys + fh,
                   ', '.join('%s %.2f° (%.2f mm)' % (k, v, math.radians(v) * rw) for k, v in sorted(min_odst.items()))))
    zg_n, n_n, bl = W.sondy_k('K-66', siatka, plik, lista)
    if zg_n != n_n:
        bledy.append('sondy %d/%d' % (zg_n, n_n))
    W.dodaj('K-66', not bledy, '%s: sondy %d/%d; %s; błędy: %s' % (plik, zg_n, n_n, '; '.join(info), '; '.join(bledy) or 'brak'),
            'ø%g / ø%g ± 0,1; wysokość %g; wierzch %g; 4 garby %s° (występ %g, środek Z %g ± 0,05); wycięcia %g × %g; 8 szczelin %g × %g przelotowych zakończonych otworem '
            'ø%g (środek na końcu szczeliny, ± 0,05), górny koniec otworu ≥ 1,5 pod spodem wierzchu; szczeliny i otwory rozłączne, z dala od wycięć i garbów [R58, runda 3]'
            % (2 * rw, 2 * rz, wys, tw, '/'.join('%g' % a for a in P['round_cover_snap_angles']), wy, zsn, fw, fh, P['round_cover_slit_w'], P['round_cover_slit_h'],
               P['round_cover_slit_end_d']), 'B',
            '%s: %d sond < 0,1 od ściany' % (plik, bl) if bl else '')


KROK_ULOZEN = 0.1        # R58 runda 2, K-67: krok siatki map wysokosci i przesuniec w szukaniu ulozen plaskich [mm] (narzedziowe)
KROK_KATA_ULOZEN = 0.25  # krok obrotu [deg] (narzedziowe)
TOL_STYKU = 0.02         # styk spod plytki - wierzch polki (2,5 = 2,5) nie jest kolizja (narzedziowe)


def mapa_przeszkod_wkladki(siatka_wk, r_max, krok=KROK_ULOZEN, przes=0.0137):
    """R58 runda 2: mapa wysokosci wierzchu wkladki (uklad wkladki) w kole r_max: tablice numpy (x, y, z) wezlow z trafieniem promienia z gory."""
    import numpy as np
    n = int(math.ceil(r_max / krok)) + 1
    xs, ys, zs = [], [], []
    d = Vector((0, 0, -1))
    z0 = siatka_wk.bbox[5] + 5.0
    for j in range(-n, n + 1):
        y = j * krok + przes
        for i in range(-n, n + 1):
            x = i * krok + przes
            if x * x + y * y > r_max * r_max:
                continue
            loc, _n, _i, _dd = siatka_wk.bvh.ray_cast(Vector((x, y, z0)), d)
            if loc is not None:
                xs.append(x)
                ys.append(y)
                zs.append(loc.z)
    return np.array(xs), np.array(ys), np.array(zs)


def mapa_spodu_plytki(siatka_pl, T, r_in, r_out, krok=KROK_ULOZEN, przes=0.0371):
    """R58 runda 2: mapa wysokosci spodu plytki (uklad plytki, spod Z = -T) w pierscieniu r_in...r_out: z_wzgl = trafienie promienia od spodu + T
    (0 = pelny spod, kieszen 2,2, rowek klucza 5,0); NaN = brak materialu w kolumnie (poza plytka, otwor przelotowy) albo poza pierscieniem.
    Erozja brakow o 1 wezel (krawedz i otwory o krok mniejsze - bez falszywych styków z krawedzia otworu wkladki przy przesunieciu = luz)."""
    import numpy as np
    n = int(math.ceil(r_out / krok)) + 1
    m = np.full((2 * n + 1, 2 * n + 1), np.nan)
    licz = np.zeros(m.shape, dtype=bool)
    d = Vector((0, 0, 1))
    for j in range(2 * n + 1):
        y = (j - n) * krok + przes
        for i in range(2 * n + 1):
            x = (i - n) * krok + przes
            r2 = x * x + y * y
            if r2 < r_in * r_in or r2 > r_out * r_out:
                continue
            licz[j, i] = True
            loc, _n, _i, _dd = siatka_pl.bvh.ray_cast(Vector((x, y, -T - 5.0)), d)
            if loc is not None:
                m[j, i] = loc.z + T
    brak = licz & np.isnan(m)
    er = brak.copy()
    er[1:, :] |= brak[:-1, :]
    er[:-1, :] |= brak[1:, :]
    er[:, 1:] |= brak[:, :-1]
    er[:, :-1] |= brak[:, 1:]
    m[er] = np.nan
    return m, n, przes


def unoszenie(mapa, n, przes, prz, sh, katy, przes_xy, krok=KROK_ULOZEN, tol=TOL_STYKU):
    """Dla kazdego kata (deg): najmniejsze po przesunieciach uniesienie plytki potrzebne, zeby nie kolidowala z przeszkodami prz = (x, y, z)
    przy spodzie na polce Z sh (0 = lezy plasko). Zwraca (uniesienia, promien punktu styku, przesuniecie)."""
    import numpy as np
    X, Y, H = prz
    dx = np.array([p[0] for p in przes_xy])[:, None]
    dy = np.array([p[1] for p in przes_xy])[:, None]
    qx, qy = X[None, :] - dx, Y[None, :] - dy
    rr = np.hypot(X, Y)
    wyn_l, wyn_r, wyn_d = [], [], []
    size = mapa.shape[0]
    for a in katy:
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        px, py = c * qx + s * qy, -s * qx + c * qy
        ii = np.rint((px - przes) / krok).astype(np.int64) + n
        jj = np.rint((py - przes) / krok).astype(np.int64) + n
        ok = (ii >= 0) & (ii < size) & (jj >= 0) & (jj < size)
        z = np.full(px.shape, np.nan)
        z[ok] = mapa[jj[ok], ii[ok]]
        lift = H[None, :] - (sh + z) - tol
        lift = np.where(np.isnan(lift), -np.inf, lift)
        kmax = lift.argmax(axis=1)
        lmax = lift[np.arange(lift.shape[0]), kmax]
        lmax = np.maximum(lmax, 0.0)
        s_best = int(lmax.argmin())
        wyn_l.append(float(lmax[s_best]))
        wyn_r.append(float(rr[kmax[s_best]]))
        wyn_d.append(przes_xy[s_best])
    return wyn_l, wyn_r, wyn_d


def przedzialy(katy, maska):
    """Ciagle przedzialy katow (deg) z maska True, z zawinieciem 360."""
    n = len(katy)
    if all(maska):
        return [(0.0, 360.0)]
    start = next(i for i in range(n) if not maska[i])
    wyn, bie = [], None
    for k in range(1, n + 1):
        i = (start + k) % n
        if maska[i] and bie is None:
            bie = katy[i]
        if not maska[i] and bie is not None:
            kon = katy[(i - 1) % n]
            wyn.append((bie if bie <= kon else bie - 360.0, kon))
            bie = None
    if bie is not None:
        wyn.append((bie, katy[(start - 1) % n] + (360.0 if katy[(start - 1) % n] < bie else 0.0)))
    return wyn


KIERUNKI_KOLNIERZA = 8          # R58 runda 3, K-67: kierunki przesuniec plytki i pokrywki (od osi D co 360/8) (narzedziowe)
KROK_PROBEK_KRAWEDZI = 0.05     # probki na krawedziach siatek do odleglosci kolnierz-zebro [mm] (narzedziowe)
NADMIAR_CZULOSCI = 0.12         # kontrola czulosci przesuwow: swobodny przesuw + 2 x SKURCZ_K53 + 0,02 musi dac kolizje (narzedziowe)


def wierzcholki_skurczone(oz):
    """Wierzcholki ObiektZlozenia przesuniete do srodka o SKURCZ_K53 wzdluz normalnych (jak bvh_skurcz)."""
    M = oz.ob.matrix_world
    R = M.to_3x3()
    return [p - (R @ v.normal).normalized() * SKURCZ_K53 for p, v in zip(oz.v, oz.ob.data.vertices)]


def swobodny_przesuw(A, B, d, maks, z0, z1, r_min):
    """R58 runda 3: o ile obiekt A moze sie przesunac w poziomym kierunku d (wersor) do styku z B: promienie z wierzcholkow A (kierunek d)
    w BVH B i z wierzcholkow B (kierunek -d) w BVH A; tylko wierzcholki z Z w (z0, z1) i promieniem od osi Z >= r_min. Wynik <= maks."""
    dv = Vector((d[0], d[1], 0.0))
    best = maks
    for zrodlo, cel, kier in ((A.v, B.bvh, dv), (B.v, A.bvh, -dv)):
        for p in zrodlo:
            if not (z0 < p.z < z1) or p.x * p.x + p.y * p.y < r_min * r_min:
                continue
            loc, _n, _i, dl = cel.ray_cast(p, kier, best)
            if loc is not None and dl < best:
                best = dl
    return best


def probki_krawedzi(v, f, maska, krok=KROK_PROBEK_KRAWEDZI):
    """Wierzcholki z maska i punkty co <= krok na krawedziach scian, ktorych wszystkie wierzcholki sa w masce."""
    kraw = set()
    for fc in f:
        if all(maska[i] for i in fc):
            for a, b in zip(fc, fc[1:] + fc[:1]):
                kraw.add((a, b) if a < b else (b, a))
    pts = [v[i] for i in range(len(v)) if maska[i]]
    for a, b in sorted(kraw):
        n = int((v[b] - v[a]).length / krok)
        pts += [v[a].lerp(v[b], k / (n + 1)) for k in range(1, n + 1)]
    return pts


def kolnierz_w_skrajnych(P, sc_wkl, sc_pokr, plyty):
    """R58 runda 3 (P1 recenzji rundy 2): kolnierz pokrywki nad wkladka i zebrem klucza w ustawieniach skrajnych (uklad montazowy K-67).
    Plytka przesunieta w KIERUNKI_KOLNIERZA kierunkach (od osi D co 360/n) o min(round_insert_clearance, swobodny przesuw z siatek - zebro
    w rowku ogranicza kierunki styczne), pokrywka przesunieta wzgledem plytki w tych samych kierunkach o min(cover_clearance, swobodny
    przesuw z siatek). Dla kazdego ustawienia: kolizje metoda K-53 (wkladka-plytka, plytka-pokrywka, wkladka-pokrywka), najmniejsza
    odleglosc 3D kolnierz-zebro (zebro = sciany wkladki nad wierzchem insert_h w obszarze zebra; wierzcholki + probki krawedzi obu siatek,
    find_nearest w obie strony), luz w rzucie (promien lica wewnetrznego kolnierza od osi pokrywki w kierunku kazdego wierzcholka zebra nad
    wierzchem minus odleglosc tego wierzcholka od osi pokrywki) i odleglosc kolnierz-wkladka (wierzcholki dolnej krawedzi kolnierza).
    Kontrola czulosci (pierwsza plytka): swobodny przesuw + NADMIAR_CZULOSCI w kazdym kierunku musi dac kolizje. plyty: (rdzen, sciezka, M_druk)."""
    sh, T, H = P['insert_shelf_h'], P['plate_thickness'], P['insert_h']
    z_pl = sh + T
    z_pk = z_pl + P['cover_inner_h'] + P['cover_top_t']
    luz, luz_pk = P['round_insert_clearance'], P['cover_clearance']
    R, dist, kat, _cw = sciecie_okraglej(P)
    do = dist + luz
    cu, su = math.cos(math.radians(kat)), math.sin(math.radians(kat))
    uu = lambda p: p.x * cu + p.y * su
    vv = lambda p: -p.x * su + p.y * cu
    kol = bpy.data.collections.new('R58_kolnierz')
    bpy.context.scene.collection.children.link(kol)
    utworzone = []

    def oz(sciezka, M, nazwa):
        ob = obiekt_ze_stl(sciezka, M, nazwa, kol)
        utworzone.append(ob)
        return ObiektZlozenia(nazwa, ob)
    TR = Matrix.Translation
    wk = oz(sc_wkl, M_druk(P, 'wkladka_okragla').inverted(), 'wkladka_kolnierz')
    pk = oz(sc_pokr, TR((0, 0, z_pk)) @ M_druk(P, 'pokrywka_okragla').inverted(), 'pokrywka_kolnierz')
    pk_sk = wierzcholki_skurczone(pk)
    z_kol = pk.bbox[4]
    # zebro nad wierzchem wkladki: sciany wkladki w obszarze zebra, wszystkie wierzcholki na Z >= H, srodek powyzej H
    w_z, r0_z = P['round_key_rib_w'], P['round_key_rib_r0']
    w_obsz = lambda p: r0_z - 1.0 <= uu(p) <= do + P['insert_chamfer'] + 1.0 and abs(vv(p)) <= w_z / 2 + 1.0 and p.z >= H - 1e-4
    zf = [fc for fc in wk.f if all(w_obsz(wk.v[i]) for i in fc) and sum(wk.v[i].z for i in fc) / len(fc) > H + 1e-3]
    if not zf:
        raise BladProjektu('K-67 kołnierz: brak części żebra nad wierzchem wkładki w %s' % sc_wkl)
    idx = sorted({i for fc in zf for i in fc})
    nr = {i: k for k, i in enumerate(idx)}
    zv = [wk.v[i] for i in idx]
    zf2 = [tuple(nr[i] for i in fc) for fc in zf]
    zeb_bvh = BVHTree.FromPolygons(zv, zf2)
    zeb_pts = probki_krawedzi(zv, zf2, [True] * len(zv))
    u_zeb = max(uu(p) for p in zv)
    # kolnierz przy zebrze: sciany pokrywki do 3 mm nad dolna krawedzia, +-20 st. od osi zebra; dolna krawedz kolnierza (caly obwod)
    blisko = [abs(((math.degrees(math.atan2(p.y, p.x)) - kat) + 180) % 360 - 180) <= 20.0 and p.z <= z_kol + 3.0 for p in pk.v]
    pk_pts = probki_krawedzi(pk.v, pk.f, blisko)
    pk_dol = [p for p in pk.v if p.z <= z_kol + 1e-3]
    z_ray = z_kol + 0.5
    kier = [kat + 360.0 / KIERUNKI_KOLNIERZA * i for i in range(KIERUNKI_KOLNIERZA)]
    dk = [(math.cos(math.radians(a)), math.sin(math.radians(a))) for a in kier]
    i_od = KIERUNKI_KOLNIERZA // 2              # kierunek od zebra (kat + 180): lico kolnierza po stronie zebra najblizej zebra
    cache_abs, cache_rel = {}, {}

    def ocen_pokrywke(o):
        """(kolizje wkladka-pokrywka, odleglosc 3D kolnierz-zebro, luz w rzucie, odleglosc kolnierz-wkladka) dla przesuniecia pokrywki o."""
        k_ = (round(o.x, 4), round(o.y, 4))
        if k_ not in cache_abs:
            bv = BVHTree.FromPolygons([p + o for p in pk_sk], pk.f)
            n_wk = len(bv.overlap(wk.bvh_skurcz))
            d1 = min(zeb_bvh.find_nearest(p + o)[3] for p in pk_pts)
            d2 = min(pk.bvh.find_nearest(q - o)[3] for q in zeb_pts)
            rz_ = []
            for q in zv:
                dq = Vector((q.x - o.x, q.y - o.y, 0.0))
                if dq.length < 1e-9:
                    continue
                hit = pk.bvh.ray_cast(Vector((0.0, 0.0, z_ray)), dq.normalized())
                if hit[0] is not None:
                    rz_.append(hit[3] - dq.length)
            d_w = min(wk.bvh.find_nearest(p + o)[3] for p in pk_dol)
            cache_abs[k_] = (n_wk, min(d1, d2), min(rz_) if rz_ else float('nan'), d_w)
        return cache_abs[k_]

    ust, pl_wyn, czul = [], [], []
    for n_pl, (rdzen, sciezka, Md) in enumerate(plyty):
        pl = oz(sciezka, TR((0, 0, z_pl)) @ Md.inverted(), rdzen + '_kolnierz')
        pl_sk = wierzcholki_skurczone(pl)
        sw_pl = [swobodny_przesuw(pl, wk, d, 1.0, sh + TOL_STYKU, z_pl + 1.0, R - 6.0) for d in dk]
        sw_pk = [swobodny_przesuw(pk, pl, d, 1.0, z_pl - T - 1.0, z_pl + 1.0, R - 6.0) for d in dk]
        s_pl = [min(luz, s) for s in sw_pl]
        s_pk = [min(luz_pk, s) for s in sw_pk]
        pl_wyn.append((rdzen, s_pl, s_pk, sw_pl, sw_pk))
        if n_pl == 0:
            for i, d in enumerate(dk):
                o = Vector((d[0], d[1], 0.0)) * (sw_pl[i] + NADMIAR_CZULOSCI)
                n1 = len(BVHTree.FromPolygons([p + o for p in pl_sk], pl.f).overlap(wk.bvh_skurcz))
                o = Vector((d[0], d[1], 0.0)) * (sw_pk[i] + NADMIAR_CZULOSCI)
                n2 = len(BVHTree.FromPolygons([p + o for p in pk_sk], pk.f).overlap(pl.bvh_skurcz))
                czul.append((kier[i], n1, n2))
        for i, d1_ in enumerate(dk):
            o_pl = Vector((d1_[0], d1_[1], 0.0)) * s_pl[i]
            n_wp = len(BVHTree.FromPolygons([p + o_pl for p in pl_sk], pl.f).overlap(wk.bvh_skurcz))
            for j, d2_ in enumerate(dk):
                o_rel = Vector((d2_[0], d2_[1], 0.0)) * s_pk[j]
                kr = (round(o_rel.x, 4), round(o_rel.y, 4))
                if kr not in cache_rel:
                    cache_rel[kr] = BVHTree.FromPolygons([p + o_rel for p in pk_sk], pk.f)
                n_pp = len(cache_rel[kr].overlap(pl.bvh_skurcz))
                n_wk, d_z, l_r, d_w = ocen_pokrywke(o_pl + o_rel)
                ust.append((rdzen, kier[i], kier[j], n_wp, n_pp, n_wk, d_z, l_r, d_w, s_pl[i], s_pk[j], i, j))
        usun_obiekt(pl.ob)
        utworzone.remove(pl.ob)
    for ob in utworzone:
        usun_obiekt(ob)
    bpy.data.collections.remove(kol)
    bledy = []
    kolid = [u for u in ust if u[3] or u[4] or u[5]]
    if kolid:
        bledy.append('kołnierz w ustawieniach skrajnych: %d ustawień z kolizją, np. %s' % (len(kolid), ['%s płytka %.0f° + pokrywka %.0f°: %d/%d/%d' % u[:6] for u in kolid[:3]]))
    m_z = min(ust, key=lambda u: u[6])
    m_r = min(ust, key=lambda u: u[7])
    m_w = min(ust, key=lambda u: u[8])
    if m_z[6] < 2 * SKURCZ_K53 - 1e-9:
        bledy.append('odstęp kołnierz–żebro %.3f < %.2f (%s, płytka %.0f°, pokrywka %.0f°)' % (m_z[6], 2 * SKURCZ_K53, m_z[0], m_z[1], m_z[2]))
    if not m_r[7] > 0:
        bledy.append('luz w rzucie lico kołnierza–żebro %.3f ≤ 0 (%s, płytka %.0f°, pokrywka %.0f°)' % (m_r[7], m_r[0], m_r[1], m_r[2]))
    zle_cz = [c for c in czul if not (c[1] > 0 and c[2] > 0)]
    if zle_cz:
        bledy.append('kontrola czułości przesuwów (swobodny + %.2f bez kolizji): %s' % (NADMIAR_CZULOSCI, zle_cz))
    od = [u for u in ust if u[11] == i_od and u[12] == i_od]
    return {'bledy': bledy, 'ust': ust, 'plytki': pl_wyn, 'czul': czul, 'kier': kier, 'min_zeb': m_z, 'min_rzut': (m_r[7], m_r), 'min_wkl': m_w,
            'n_kol': len(kolid), 'n_kol_wk': sum(1 for v_ in cache_abs.values() if v_[0] > 0), 'luz': (luz, luz_pk, H),
            'n_ust_unik': len(cache_abs), 'u_zeb': u_zeb, 'z_kol': z_kol, 'najgorsze_od_zebra': od[0] if od else None,
            's_od': (od[0][9], od[0][10]) if od else (float('nan'), float('nan')), 'kat_od': kier[i_od], 'n_zeb': (len(zv), len(zeb_pts), len(pk_pts))}


def opis_kolnierza(kw, tytul):
    """Tekst do raportu K-67 z wyniku kolnierz_w_skrajnych."""
    f3 = lambda x: '%.3f' % x
    s_wsp = {}
    for rdzen, s_pl, s_pk, _a, _b in kw['plytki']:
        s_wsp.setdefault((tuple(round(x, 3) for x in s_pl), tuple(round(x, 3) for x in s_pk)), []).append(rdzen)
    m_z, (lr, m_r), m_w = kw['min_zeb'], kw['min_rzut'], kw['min_wkl']
    u_od = kw['najgorsze_od_zebra']
    return ('%s: %d kierunków od osi D (%s°); przesuw płytki = min(luz %g, swobodny przesuw z siatek), pokrywki względem płytki = min(luz %g, swobodny przesuw); '
            'przesuwy [płytka | pokrywka] w kierunkach: %s; %d płytek × %d ustawień = %d (%d różnych położeń pokrywki); kolizje (skurcz %.2f) wkładka–płytka / płytka–pokrywka / '
            'wkładka–pokrywka: %d / %d / %d ustawień; żebro nad wierzchem wkładki (Z > %g): koniec w rzucie u %.3f, dolna krawędź kołnierza Z %.3f; '
            'najmniejszy odstęp 3D kołnierz–żebro %.3f (%s, płytka %.0f° %.3f + pokrywka %.0f° %.3f); luz w rzucie lico kołnierza–żebro min %.3f (płytka %.0f° %.3f + pokrywka %.0f° %.3f); '
            'w ustawieniu od żebra (płytka %.3f + pokrywka %.3f w kierunku %.0f°) odstęp 3D %.3f, luz w rzucie %.3f; kołnierz–wkładka (dolna krawędź, cała wkładka) min %.3f; '
            'kontrola czułości przesuwów (%s; swobodny przesuw + %.2f → kolizje płytka–wkładka / pokrywka–płytka): %s; próbki: %d wierzchołków żebra, %d punktów żebra, %d punktów kołnierza'
            % (tytul, len(kw['kier']), '/'.join('%.0f' % a for a in kw['kier']), kw['luz'][0], kw['luz'][1],
               '; '.join('%s: %s' % (', '.join(r_ for r_ in rr) if len(rr) < len(kw['plytki']) else 'wszystkie płytki',
                                     ' '.join('%.3f|%.3f' % (a, b) for a, b in zip(k_[0], k_[1]))) for k_, rr in s_wsp.items()),
               len(kw['plytki']), len(kw['kier']) ** 2, len(kw['ust']), kw['n_ust_unik'], SKURCZ_K53,
               sum(1 for u in kw['ust'] if u[3]), sum(1 for u in kw['ust'] if u[4]), sum(1 for u in kw['ust'] if u[5]),
               kw['luz'][2], kw['u_zeb'], kw['z_kol'],
               m_z[6], m_z[0], m_z[1], m_z[9], m_z[2], m_z[10], lr, m_r[1], m_r[9], m_r[2], m_r[10],
               u_od[9] if u_od else float('nan'), u_od[10] if u_od else float('nan'), kw['kat_od'], u_od[6] if u_od else float('nan'), u_od[7] if u_od else float('nan'),
               m_w[8], kw['plytki'][0][0], NADMIAR_CZULOSCI, ', '.join('%.0f° %d/%d' % c for c in kw['czul']), kw['n_zeb'][0], kw['n_zeb'][1], kw['n_zeb'][2]))


def ulozenia_plaskie(P, sc_wkl, plyty, sh, opis_zestawu):
    """R58 runda 2 (B1 recenzji): czy plytka da sie polozyc plasko na polce wkladki w innym obrocie niz nominalny. Z siatek: mapa wierzchu
    wkladki (przeszkody = material powyzej polki + TOL_STYKU w kole R + luz + krok) i mapa spodu kazdej plytki; obrot 0...360 co KROK_KATA_ULOZEN,
    przesuniecie w kole luzu round_insert_clearance co KROK_ULOZEN. Zwraca liste (rdzen, katy, uniesienia, promienie styku) i dane kontroli."""
    R = P['plate_round_d'] / 2
    luz = P['round_insert_clearance']
    T = P['plate_thickness']
    s_wk = Siatka(sc_wkl, M_druk(P, 'wkladka_okragla').inverted())
    X, Y, Z = mapa_przeszkod_wkladki(s_wk, R + luz + KROK_ULOZEN)
    s_wk.zwolnij()
    import numpy as np
    prz_m = Z > sh + TOL_STYKU
    prz = (X[prz_m], Y[prz_m], Z[prz_m])
    pelne = (X, Y, Z)
    r_in = max(0.0, float(np.hypot(prz[0], prz[1]).min()) - luz - 2 * KROK_ULOZEN)
    k = int(round(luz / KROK_ULOZEN))
    przes_xy = [(i * KROK_ULOZEN, j * KROK_ULOZEN) for i in range(-k, k + 1) for j in range(-k, k + 1)
                if (i * KROK_ULOZEN) ** 2 + (j * KROK_ULOZEN) ** 2 <= luz * luz + 1e-9]
    katy = [i * KROK_KATA_ULOZEN for i in range(int(round(360.0 / KROK_KATA_ULOZEN)))]
    wyn = []
    kontrola = None
    for rdzen, sciezka, Md in plyty:
        s_pl = Siatka(sciezka, Md.inverted())
        mapa, n, przes = mapa_spodu_plytki(s_pl, T, r_in, R + 2 * KROK_ULOZEN)
        s_pl.zwolnij()
        L, rc, dd = unoszenie(mapa, n, przes, prz, sh, katy, przes_xy)
        wyn.append((rdzen, katy, L, rc, dd))
        if kontrola is None:
            # kontrola czulosci na pierwszej plytce: nominal (0 st., bez przesuniecia) = 0; plytka opuszczona o 0,05 (wszystkie wezly wkladki
            # w pierscieniu, takze polka) > 0; przesuniecie o luz + 0,2 w strone sciecia > 0
            kat_d = osie_okragle(P)['D'][0]
            sd = ((luz + 2 * KROK_ULOZEN) * math.cos(math.radians(kat_d)), (luz + 2 * KROK_ULOZEN) * math.sin(math.radians(kat_d)))
            pel_m = np.hypot(pelne[0], pelne[1]) >= r_in + luz + 2 * KROK_ULOZEN
            pel = (pelne[0][pel_m], pelne[1][pel_m], pelne[2][pel_m])
            kontrola = (rdzen, unoszenie(mapa, n, przes, prz, sh, [0.0], [(0.0, 0.0)])[0][0],
                        unoszenie(mapa, n, przes, pel, sh - 0.05, [0.0], [(0.0, 0.0)])[0][0],
                        unoszenie(mapa, n, przes, prz, sh, [0.0], [sd])[0][0], len(prz[0]), len(przes_xy), len(katy))
    return wyn, kontrola


def opis_ulozen(P, wyn, sh):
    """Okno wejscia (uniesienie 0) wokol 0 st., inne kąty z uniesieniem 0, strefa naprowadzenia (krawedz rowka plytki na fazie zebra:
    0 < uniesienie < wysokosc zebra - TOL_STYKU) i uniesienie poza nia (plytka lezy na wierzchu zebra)."""
    R = P['plate_round_d'] / 2
    c = P['round_key_rib_h'] - TOL_STYKU - 0.01        # ponizej: styk na fazie zebra (naprowadzenie), powyzej: plytka na wierzchu zebra
    opisy, bledy = [], []
    for rdzen, katy, L, rc, dd in wyn:
        zero = [l <= 1e-9 for l in L]
        prz = przedzialy(katy, zero)
        okno = [p for p in prz if p[0] <= 0.0 + 1e-9 <= p[1] + 1e-9 or (p[0] <= 360.0 <= p[1])]
        inne = [p for p in prz if p not in okno]
        nap = [l <= c + 1e-9 for l in L]
        prz_nap = [p for p in przedzialy(katy, nap) if p[0] <= 1e-9 <= p[1] + 1e-9]
        poza = [(l, a, r) for l, a, r, z, n_ in zip(L, katy, rc, zero, nap) if not n_]
        if poza:
            lmin, amin, rmin = min(poza)
            lmax = max(p[0] for p in poza)
            alfa = math.degrees(math.atan2(lmin, rmin + R))
            kraw = 2 * R * math.tan(math.radians(alfa))
        else:
            lmin = lmax = amin = rmin = alfa = kraw = float('nan')
        opisy.append((rdzen, okno, inne, prz_nap, lmin, amin, lmax, alfa, kraw))
    return opisy


def sprawdz_pasowania_R58(W, P, plyty, sc_wkl, sc_pokr, stare_okragle=(), poprzednie=None, runda2=None):
    """K-67 (R58): pasowania w ukladzie montazowym wkladki (spod ramy Z = 0): plytka okragla ramkowa we wkladce okraglej, pokrywka okragla
    na plytce. plyty: lista (rdzen, sciezka, M_druk, uklad). Kolizje metoda K-53 (kopie zmniejszone o SKURCZ_K53). Runda 2: zebro klucza
    w rowku; szukanie ulozen plaskich (obrot 0...360 x przesuniecie w luzie) dla kazdej plytki; informacyjnie stare plytki okragle n8/n9
    (stare_okragle: (rdzen, sciezka, M)) i geometria rundy 1 (poprzednie: (sciezka wkladki, [(rdzen, sciezka, M)])). Runda 3: kolnierz
    pokrywki w ustawieniach skrajnych (kolnierz_w_skrajnych) i kontrola czulosci na geometrii rundy 2 (runda2: (sciezka wkladki, sciezka pokrywki))."""
    sh, T = P['insert_shelf_h'], P['plate_thickness']
    z_pl = sh + T
    z_pk = z_pl + P['cover_inner_h'] + P['cover_top_t']
    R, dist, kat, cw = sciecie_okraglej(P)
    luz = P['round_insert_clearance']
    zb_w, zb_r0, zb_h = P['round_key_rib_w'], P['round_key_rib_r0'], P['round_key_rib_h']
    do = dist + luz
    rw_p, rz_p, _wys_p = wymiary_pokrywki_okraglej(P)
    osie = osie_okragle(P)
    zw = P['insert_opening'] / 2 + P['insert_wall_w']
    bledy, info = [], []
    kol = bpy.data.collections.new('R58_zlozenie')
    bpy.context.scene.collection.children.link(kol)
    utworzone = []

    def oz(sciezka, M, nazwa):
        ob = obiekt_ze_stl(sciezka, M, nazwa, kol)
        utworzone.append(ob)
        return ObiektZlozenia(nazwa, ob)
    TR = Matrix.Translation
    wk = oz(sc_wkl, M_druk(P, 'wkladka_okragla').inverted(), 'wkladka_okragla')
    pk = oz(sc_pokr, TR((0, 0, z_pk)) @ M_druk(P, 'pokrywka_okragla').inverted(), 'pokrywka_okragla')
    n_par = lambda a, b: len(a.bvh_skurcz.overlap(b.bvh_skurcz))
    kolizje, styk = [], []
    if n_par(wk, pk):
        kolizje.append(('wkladka_okragla', 'pokrywka_okragla', n_par(wk, pk)))
    cu, su = math.cos(math.radians(kat)), math.sin(math.radians(kat))
    uv = lambda u, v, z: (u * cu - v * su, u * su + v * cu, z)
    vv = lambda q: -q.x * su + q.y * cu
    uu = lambda q: q.x * cu + q.y * su
    zt = lambda o, x, y: (lambda l: None if l is None else l.z)(o.promien((x, y, 100), (0, 0, -1)))
    zp = lambda o, x, y: (lambda l: None if l is None else l.z)(o.promien((x, y, -100), (0, 0, 1)))
    # D2: kolnierz pokrywki nad wkladka - max Z wierzchu wkladki w calym pierscieniu pod kolnierzem (promienie co 0,25 mm / 0,5 st.)
    zmax_k, gdzie_k = -1e9, None
    r_k = rw_p - KROK_ULOZEN
    while r_k <= rz_p + KROK_ULOZEN + 1e-9:
        for i in range(720):
            a = math.radians(i * 0.5)
            z = zt(wk, r_k * math.cos(a), r_k * math.sin(a))
            if z is not None and z > zmax_k:
                zmax_k, gdzie_k = z, (r_k, i * 0.5)
        r_k += 0.25
    kolnierz = pk.bbox[4] - zmax_k
    zmierzone = {}
    for rdzen, sciezka, Md, uklad in plyty:
        pl = oz(sciezka, TR((0, 0, z_pl)) @ Md.inverted(), rdzen)
        for a, nb in ((wk, 'wkladka_okragla'), (pk, 'pokrywka_okragla')):
            n = n_par(pl, a)
            if n:
                kolizje.append((rdzen, nb, n))
        styk.append((rdzen, len(pl.bvh.overlap(wk.bvh))))
        if re.search(r'_n\d+$', rdzen):
            continue
        typ = uklad['plate']
        ks = uklad['key_slot']
        # pomiary na plytce bazowej typu
        z_o = (sh + P['insert_h'] - P['insert_chamfer']) / 2
        luzy = []
        for a in (0.0, 30.0, 90.0, 150.0, 180.0, 210.0, 240.0, 300.0):
            ri = promien_od_srodka(wk.bvh, a, z_o)
            rpl = promien_z_zewnatrz(pl.bvh, a, z_pl - T / 2, R + 5)
            luzy.append(None if ri is None or rpl is None else ri - rpl)
        voff = (zb_w / 2 + cw / 2) / 2 + 1.0
        luz_sc = []
        for v in (voff, -voff):
            a_ = pierwsze_trafienie(wk.bvh, uv(0, v, z_o), (cu, su, 0))
            b_ = pierwsze_trafienie(pl.bvh, uv(R + 5, v, z_pl - T / 2), (-cu, -su, 0))
            luz_sc.append(None if (a_ is None or b_ is None) else uu(a_) - uu(b_))
        rs = (P['round_insert_ledge_r'] + R + luz) / 2
        z_polki = zt(wk, 0.0, rs)
        spod = pl.bbox[4]
        osi = []
        for k in 'ABC':
            _a, cx, cy = osie[k]
            m = srodek_wneki(pl.bvh, cx, cy, z_pl - T + P['magnet_pocket_depth'] / 2)
            hh = srodek_wneki(wk.bvh, cx, cy, (P['hall_lead_channel_h'] + sh) / 2)
            osi.append((k, None if (m is None or hh is None) else math.hypot(m[0] - hh[0], m[1] - hh[1])))
        # zebro klucza w rowku: boki (promienie +-v w siatce plytki z osi zebra i z zewnatrz w siatce wkladki), czolo, nad zebrem
        um, zr = (max(zb_r0, ks['r0']) + dist) / 2, sh + (zb_h - P['round_key_rib_chamfer']) / 2
        sp = pierwsze_trafienie(pl.bvh, uv(um, 0, zr), (-su, cu, 0))
        sm = pierwsze_trafienie(pl.bvh, uv(um, 0, zr), (su, -cu, 0))
        kp = pierwsze_trafienie(wk.bvh, uv(um, zb_w / 2 + 1.0, zr), (su, -cu, 0))
        km = pierwsze_trafienie(wk.bvh, uv(um, -zb_w / 2 - 1.0, zr), (-su, cu, 0))
        czp = pierwsze_trafienie(pl.bvh, uv(um, 0, zr), (-cu, -su, 0))
        czw = pierwsze_trafienie(wk.bvh, uv(ks['r0'] - 2.0, 0, zr), (cu, su, 0))
        uz = (zb_r0 + P['round_key_rib_top_r1']) / 2           # srodek wierzchu zebra (runda 3: u r0 + c ... r1 - c)
        sufit = zp(pl, *uv(uz, 0, 0)[:2])
        wierzch_z = zt(wk, *uv(uz, 0, 0)[:2])
        if None in (sp, sm, kp, km, czp, czw):
            luz_l = luz_p = czolo = None
        else:
            luz_l, luz_p = vv(sp) - vv(kp), vv(km) - vv(sm)
            czolo = uu(czw) - uu(czp)
        nad = None if (sufit is None or wierzch_z is None) else sufit - wierzch_z
        # pokrywka na plytce
        z_pm = z_pk - (P['cover_inner_h'] + P['cover_top_t'] + P['cover_skirt_below']) / 2
        luz_pk = []
        for a in (0.0, 90.0, 180.0, 270.0):
            ri = promien_od_srodka(pk.bvh, a, z_pm)
            rpl = promien_z_zewnatrz(pl.bvh, a, z_pl - T / 2, R + 5)
            luz_pk.append(None if ri is None or rpl is None else ri - rpl)
        z_g = z_pk + P['cover_snap_z']
        garby = []
        for kg in P['round_cover_snap_angles']:
            czub = promien_od_srodka(pk.bvh, kg, z_g)
            dno_r = promien_z_zewnatrz(pl.bvh, kg, z_g, R + 5)
            rr = R - uklad['cover_groove']['depth'] / 2
            ca, sa = math.cos(math.radians(kg)), math.sin(math.radians(kg))
            gg = pierwsze_trafienie(pl.bvh, (rr * ca, rr * sa, z_g), (0, 0, 1))
            gd = pierwsze_trafienie(pl.bvh, (rr * ca, rr * sa, z_g), (0, 0, -1))
            rg = rw_p - P['cover_snap_bump'] / 4
            bg = pierwsze_trafienie(pk.bvh, (rg * ca, rg * sa, z_g + 2.0), (0, 0, -1))
            bd = pierwsze_trafienie(pk.bvh, (rg * ca, rg * sa, z_g - 2.0), (0, 0, 1))
            if None in (czub, dno_r, gg, gd, bg, bd):
                garby.append((kg, None, None, None))
                continue
            garby.append((kg, R - czub, czub - dno_r, (bg.z + bd.z) / 2 - (gg.z + gd.z) / 2))
        zmierzone[typ] = (luzy, luz_sc, z_polki, spod, osi, luz_l, luz_p, czolo, nad, luz_pk, garby)
    # ocena
    if kolizje:
        bledy.append('kolizje: %s' % '; '.join('%s–%s %d' % k for k in kolizje))
    l_bok = P['round_key_slot_w'] / 2 - zb_w / 2
    f = lambda v, n=3: '—' if v is None else ('%.' + str(n) + 'f') % v
    for typ, (luzy, luz_sc, z_polki, spod, osi, luz_l, luz_p, czolo, nad, luz_pk, garby) in zmierzone.items():
        e = []
        if any(v is None or abs(v - luz) > 0.05 for v in luzy + luz_sc):
            e.append('luz promieniowy')
        if z_polki is None or abs(spod - z_polki) > 0.02 or abs(spod - sh) > 0.02:
            e.append('spód płytki na półce')
        if any(d is None or d > 0.1 for _k, d in osi):
            e.append('oś magnesu nad osią kieszeni Halla')
        if luz_l is None or abs(luz_l - l_bok) > 0.05 or abs(luz_p - l_bok) > 0.05:
            e.append('luz żebra w rowku')
        if czolo is None or abs(czolo - (P['round_key_rib_r0'] - P['round_key_slot_r0'])) > 0.05:
            e.append('czoło żebra – koniec rowka')
        if nad is None or nad < 0.4 - 1e-6:
            e.append('luz nad żebrem')
        if any(v is None or abs(v - P['cover_clearance']) > 0.05 for v in luz_pk):
            e.append('luz pokrywka–płytka')
        if any(z is None or abs(z - (R - (rw_p - P['cover_snap_bump']))) > 0.05 or abs(dz) > 0.05 for _k, z, _g, dz in garby):
            e.append('garb w rowku')
        if e:
            bledy.append('%s: %s' % (typ, ', '.join(e)))
        info.append('%s: luz promieniowy %s (8 kierunków), na ścięciu (promienie ±%.1f od osi) %s (zadane %g); spód płytki Z %s, półka Z %s (zadane %g); '
                    'oś magnesu–oś kieszeni Halla %s (≤ 0,1); żebro klucza w rowku: luz %s / %s na stronę (zadane %g), czoło żebra – koniec rowka %s (zadane %g), nad żebrem %s (≥ 0,4); '
                    'pokrywka–płytka luz %s (zadane %g); garby: zagłębienie w rowek / szczelina do dna / ΔZ do środka rowka %s'
                    % (typ, ' / '.join(f(v) for v in luzy), (zb_w / 2 + cw / 2) / 2 + 1.0, ' / '.join(f(v) for v in luz_sc), luz, f(spod), f(z_polki), sh,
                       ', '.join('%s %s' % (k, f(d)) for k, d in osi), f(luz_l), f(luz_p), l_bok, f(czolo), P['round_key_rib_r0'] - P['round_key_slot_r0'], f(nad),
                       ' / '.join(f(v) for v in luz_pk), P['cover_clearance'], '; '.join('%g° %s / %s / %s' % (k, f(z), f(g), f(dz)) for k, z, g, dz in garby)))
    if kolnierz < 0.4 - 1e-6:
        bledy.append('kołnierz nad wkładką %.3f' % kolnierz)
    info.append('dół kołnierza pokrywki (Z %.3f) nad wierzchem wkładki: max Z wkładki w pierścieniu r %.2f…%.2f (co 0,25 mm × 0,5°) %.3f w r %.2f, %.1f° → %.3f (≥ 0,4)'
                % (pk.bbox[4], rw_p - KROK_ULOZEN, rz_p + KROK_ULOZEN, zmax_k, gdzie_k[0], gdzie_k[1], kolnierz))
    info.append('kolizje w położeniu nominalnym (skurcz −%.2f): %s' % (SKURCZ_K53, '; '.join('%s–%s %d' % k for k in kolizje) if kolizje else 'brak (%d par)' % (2 * len(plyty) + 1)))
    info.append('kontrola czułości (bez skurczu, płytka na półce = styk): ' + ', '.join('%s %d' % s_ for s_ in styk))
    for ob in utworzone:
        usun_obiekt(ob)
    bpy.data.collections.remove(kol)
    # runda 3 (P1 recenzji rundy 2): kolnierz pokrywki nad wkladka i zebrem w ustawieniach skrajnych (plytka w luzie x pokrywka o luz)
    t1 = time.time()
    kw = kolnierz_w_skrajnych(P, sc_wkl, sc_pokr, [(r, s, M) for r, s, M, _u in plyty])
    bledy += kw['bledy']
    info.append(opis_kolnierza(kw, 'kołnierz w ustawieniach skrajnych [runda 3, P1 recenzji rundy 2]'))
    if runda2:
        kw2 = kolnierz_w_skrajnych(P, runda2[0], runda2[1], [(r, s, M) for r, s, M, _u in plyty[:1]])
        u2 = kw2['najgorsze_od_zebra']
        if not (u2 and u2[5] > 0 and u2[7] < 0):
            bledy.append('kontrola czułości kołnierza na geometrii rundy 2: brak kolizji w ustawieniu płytka %s + pokrywka %s od żebra (%s)'
                         % (kw2['s_od'][0], kw2['s_od'][1], u2))
        info.append('kontrola czułości kołnierza — geometria rundy 2 (%s, %s; żebro nad wierzchem do lica ścięcia) tą samą metodą: w ustawieniu płytka %.3f + pokrywka %.3f '
                    'od żebra (kierunek %.0f°, lico kołnierza po stronie żebra dosunięte do żebra) kolizje wkładka–pokrywka %d par (skurcz), luz w rzucie %.3f (zadane: kolizja, luz < 0); '
                    'ustawienia z kolizją wkładka–pokrywka %d / %d; luz w rzucie min %.3f; %s'
                    % (os.path.basename(os.path.dirname(runda2[0])), ', '.join(os.path.basename(x) for x in runda2), kw2['s_od'][0], kw2['s_od'][1], kw2['kat_od'],
                       u2[5] if u2 else -1, u2[7] if u2 else float('nan'), kw2['n_kol_wk'], kw2['n_ust_unik'], kw2['min_rzut'][0],
                       'zgodnie z P1 recenzji rundy 2 (wnikanie 0,16)' if (u2 and u2[5] > 0 and u2[7] < 0) else 'NIEZGODNIE z P1'))
    else:
        info.append('kontrola czułości kołnierza na geometrii rundy 2: nie wykonana (brak --r58-runda2)')
    info.append('czas sprawdzenia kołnierza %.0f s' % (time.time() - t1))
    # runda 2 (B1): szukanie ulozen plaskich - kazda plytka R58, obrot 0...360 co KROK_KATA_ULOZEN, przesuniecie w kole luzu co KROK_ULOZEN
    t0 = time.time()
    wyn, kontr = ulozenia_plaskie(P, sc_wkl, [(r, s, M) for r, s, M, _u in plyty], sh, 'R58')
    opisy = opis_ulozen(P, wyn, sh)
    szer = []
    for rdzen, okno, inne, prz_nap, lmin, amin, lmax, alfa, kraw in opisy:
        if len(okno) != 1 or inne:
            bledy.append('%s: płytka leży płasko poza jednym oknem wokół 0° (okno %s, inne %s)' % (rdzen, okno, inne))
        if okno:
            szer.append(okno[0][1] - okno[0][0])
    info.append('ułożenia płaskie [runda 2, B1] (mapa spodu płytki vs mapa wierzchu wkładki co %g mm; obrót 0…360° co %g°; przesunięcie w kole luzu %g co %g mm, %d położeń; '
                'pustych kieszeni nie zaklejano; %d węzłów przeszkód wkładki powyżej półki): ' % (KROK_ULOZEN, KROK_KATA_ULOZEN, luz, KROK_ULOZEN, kontr[5], kontr[4])
                + '; '.join('%s: okno %s, inne kąty bez kolizji: %s; strefa naprowadzenia (krawędź rowka na fazie żebra, uniesienie < %s) %s; poza nią płytka leży na żebrze: '
                            'uniesienie min %s (przy %s°), max %s, przechył %s°, krawędź +%s'
                            % (r, ' i '.join('%.2f…%.2f° (%.2f°)' % (a, b, b - a) for a, b in o) or 'BRAK', ' '.join('%.2f…%.2f°' % p for p in i_) or 'brak',
                               f(P['round_key_rib_h'] - TOL_STYKU, 2), ' '.join('%.2f…%.2f°' % p for p in n_) or '—', f(lmin, 2), f(amin, 2), f(lmax, 2), f(alfa, 2), f(kraw, 2))
                               for r, o, i_, n_, lmin, amin, lmax, alfa, kraw in opisy))
    ok_k = kontr[1] <= 1e-9 and kontr[2] > 0 and kontr[3] > 0
    if not ok_k:
        bledy.append('kontrola czułości szukania ułożeń: nominal %.3f, opuszczona 0,05 %.3f, przesunięta poza luz %.3f' % kontr[1:4])
    info.append('kontrola czułości szukania (%s): nominal 0° bez przesunięcia uniesienie %.3f (= 0); płytka opuszczona o 0,05 w półkę (wszystkie węzły wkładki) %.3f (> 0); '
                'przesunięta o luz + %g w stronę ścięcia %.3f (> 0)' % (kontr[0], kontr[1], kontr[2], 2 * KROK_ULOZEN, kontr[3]))
    if stare_okragle:
        w2, _k2 = ulozenia_plaskie(P, sc_wkl, list(stare_okragle), sh, 'n8/n9')
        info.append('informacyjnie — stare płytki okrągłe (bez kieszeni i rowka) w nowej wkładce: ' + '; '.join(
            '%s: kąty bez kolizji %s; uniesienie min %s / max %s (leży na żebrze: przechył %s°, krawędź +%s)'
            % (r, ' '.join('%.2f…%.2f°' % p for p in i_ + o) or 'brak', f(lmin, 2), f(lmax, 2), f(alfa, 2), f(kraw, 2))
            for r, o, i_, _n, lmin, _a, lmax, alfa, kraw in opis_ulozen(P, w2, sh)))
    if poprzednie:
        w3, k3 = ulozenia_plaskie(P, poprzednie[0], poprzednie[1], sh, 'runda 1')
        info.append('kontrola czułości — geometria rundy 1 (kołek ø3 × 2, rowek r0 43 / h 2,5) tą samą metodą: ' + '; '.join(
            '%s: kąty bez kolizji %s' % (r, ' '.join('%.2f…%.2f°' % p for p in o + i_) or 'brak') for r, o, i_, _n, *_x in opis_ulozen(P, w3, sh))
            + ' (B1 recenzji: okna przy 90/180/270°)')
    info.append('czas szukania %.0f s' % (time.time() - t0))
    W.dodaj('K-67', not bledy, '; '.join(info) + '; błędy: %s' % ('; '.join(bledy) or 'brak'),
            'luz promieniowy %g ± 0,05; spód na półce ± 0,02; oś magnesu nad osią Halla ≤ 0,1; żebro w rowku %g/stronę ± 0,05, czoło %g ± 0,05, nad żebrem ≥ 0,4; pokrywka %g ± 0,05; '
            'garb w rowku (zagłębienie %g ± 0,05, ΔZ ≤ 0,05); kołnierz ≥ 0,4 nad wkładką (cały pierścień); 0 kolizji; płytka leży płasko tylko w jednym oknie wokół 0° '
            '(obrót × przesunięcie w luzie, każda z 8 płytek) [R58 runda 2]; kołnierz w ustawieniach skrajnych (płytka w luzie × pokrywka o luz, 8 × 8 kierunków, każda płytka): '
            '0 kolizji, odstęp 3D kołnierz–żebro ≥ 0,1 (2 × skurcz K‑53), luz w rzucie lico kołnierza–żebro nad wierzchem > 0; czułość: przesuw swobodny + 0,12 → kolizja, '
            'geometria rundy 2 → kolizja przy 0,4 + 0,3 od żebra [R58 runda 3]'
            % (luz, l_bok, P['round_key_rib_r0'] - P['round_key_slot_r0'], P['cover_clearance'], R - (rw_p - P['cover_snap_bump'])), 'B')


# ===========================================================================
# (5b) Materialy, kamera, rendery (etap C)
# ===========================================================================

# Ustawienia renderu z promptu wykonawcy (nie sa wymiarami czesci)
RENDER_PROBKI = 64
RENDER_ROZDZ = (1600, 1200)
# Rozsuniecie wzdluz Z w kolejnosci montazu (prompt; rama dyfuzora usunieta, R50-U1) [mm]; 'wnetrze' = czesci wewnatrz korpusu,
# ktore w rzucie zaslaniaja sciany i warstwy wyzej - wysuniete w lewo ekranu o WYSUNIECIE_WNETRZA, zeby byly widoczne (K-60, lista 11)
ROZSUNIECIE = {'korpus': 0, 'wnetrze': 0, 'pi': 30, 'dystanse': 45, 'panel': 70, 'blat': 120, 'dyfuzor': 135,
               'wkladka': 160, 'plytka': 185, 'pokrywka': 215}
WYSUNIECIE_WNETRZA = 280
WIDOK_ROZSTRZELONY = (22.0, 45.0)    # (wysokosc, azymut) kamery ortogonalnej [st.]: z przodu z prawej, napis widoczny
WIDOK_ZLOZONY = (28.0, 30.0)         # kamera perspektywiczna 3/4 od przodu
PODPIS_ROZMIAR = 10.0                # wysokosc podpisow na renderze rozstrzelonym [mm sceny]
ODSTEP_PLYTEK_RENDER = 116           # rozstaw srodkow plytek na renderze plytek [mm sceny]


def grupa_rozsuniecia(n):
    if n in ('proxy_gniazdo_dc', 'proxy_gniazdo_usb', 'tulejka_dc'):
        return 'wnetrze'
    for prefiks, g in (('korpus', 'korpus'), ('proxy_stopka', 'korpus'), ('proxy_pi_bonnet', 'pi'), ('proxy_wtyk_bonnet', 'pi'),
                       ('proxy_dystans', 'dystanse'), ('proxy_panel', 'panel'), ('blat', 'blat'),
                       ('proxy_dyfuzor', 'dyfuzor'), ('proxy_hall', 'dyfuzor'), ('wkladka', 'wkladka'), ('plytka', 'plytka'),
                       ('proxy_magnes', 'plytka'), ('pokrywka', 'pokrywka')):
        if n.startswith(prefiks):
            return g
    return None


# Podpisy renderu rozstrzelonego = lista kontrolna K-60 (protokol, sekcja 11, R50): (tekst, obiekty, strona)
PODPISY = [('korpus W (napis RAMKA WIECZORNA)', ['korpus_W'], 'P'),
           ('Pi 4 + Bonnet z wtykiem DC (zastępcze)', ['proxy_pi_bonnet', 'proxy_wtyk_bonnet'], 'P'),
           ('dystanse M3 F-F 50 ×4 na stadionach (zastępcze)', ['proxy_dystans_1', 'proxy_dystans_2', 'proxy_dystans_3', 'proxy_dystans_4'], 'P'),
           ('panel HUB75 (zastępczy)', ['proxy_panel'], 'P'), ('blat', ['blat'], 'P'),
           ('dyfuzor (zastępczy)', ['proxy_dyfuzor'], 'P'), ('wkładka', ['wkladka'], 'P'), ('płytka wieczorna n1', ['plytka_wieczorna_n1'], 'P'),
           ('pokrywka', ['pokrywka'], 'P'), ('gniazdo DC (zastępcze)', ['proxy_gniazdo_dc'], 'L'), ('tulejka DC', ['tulejka_dc'], 'L'),
           ('gniazdo USB (zastępcze)', ['proxy_gniazdo_usb'], 'L')]


def kolor_liniowy(hexs):
    h = hexs.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c) + (1.0,)


def material(nazwa, hexs, metal=0.0, szorstkosc=0.6, alfa=1.0):
    m = bpy.data.materials.new(nazwa)
    kol = kolor_liniowy(hexs)
    m.diffuse_color = kol
    try:
        m.use_nodes = True
    except Exception:
        pass
    b = m.node_tree.nodes.get('Principled BSDF') if m.node_tree else None
    if b is not None:
        for wej, wart in (('Base Color', kol), ('Metallic', metal), ('Roughness', szorstkosc), ('Alpha', alfa)):
            if b.inputs.get(wej) is not None:
                b.inputs[wej].default_value = wart
    return m


def materialy(P):
    """Kolory R27 z parametry.json (`color_*`)."""
    return {'grafit': material('PA12_grafit', P['color_graphite'], szorstkosc=0.55),
            'bialy': material('PA12_bialy', P['color_white'], szorstkosc=0.7),
            'pleksi': material('pleksi_opal', P['color_plexi'], szorstkosc=0.5, alfa=0.55),
            'pcb': material('PCB', P['color_pcb'], szorstkosc=0.4),
            'mosiadz': material('mosiadz', P['color_brass'], metal=1.0, szorstkosc=0.35)}


def czesc_grafitowa(rdzen):
    """Z19 (po R50): grafit = korpus i blat; reszta naturalna biala."""
    return rdzen.startswith(('korpus', 'blat', 'ramka_korpus', 'ramka_blat'))


def material_obiektu(n):
    if czesc_grafitowa(n) or n.startswith(('proxy_stopka', 'proxy_hall', 'proxy_odbiornik')):
        return 'grafit'
    if n.startswith(('plytka', 'pokrywka', 'wkladka', 'tulejka', 'podkladka')):
        return 'bialy'
    if n == 'proxy_dyfuzor':
        return 'pleksi'
    if n in ('proxy_panel', 'proxy_pi_bonnet'):
        return 'pcb'
    return 'mosiadz'      # dystanse, gniazda DC/USB, wtyk Bonnetu, magnesy


def przygotuj_scene_renderu(P, wszystkie, zestaw):
    """Materialy na obiektach, swiat, slonce, ustawienia Cycles i kamera zlozonego widoku (zapisywane w .blend)."""
    sc = bpy.context.scene
    mat = materialy(P)
    for n, ob in wszystkie.items():
        ob.data.materials.clear()
        ob.data.materials.append(mat[material_obiektu(n)])
    swiat = bpy.data.worlds.new('swiat')
    sc.world = swiat
    try:
        swiat.use_nodes = True
        swiat.node_tree.nodes['Background'].inputs[0].default_value = (0.82, 0.84, 0.86, 1.0)
        swiat.node_tree.nodes['Background'].inputs[1].default_value = 0.6
    except Exception:
        swiat.color = (0.82, 0.84, 0.86)
    sl = bpy.data.lights.new('slonce', 'SUN')
    sl.energy = 2.5
    sl.angle = math.radians(8)
    ob_sl = bpy.data.objects.new('slonce', sl)
    sc.collection.objects.link(ob_sl)
    ob_sl.rotation_euler = (math.radians(38), 0.0, math.radians(25))
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = RENDER_PROBKI
    sc.cycles.use_denoising = True
    try:
        sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    except Exception:
        pass
    sc.render.resolution_x, sc.render.resolution_y = RENDER_ROZDZ
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    sc.render.image_settings.file_format = 'PNG'
    try:
        sc.view_settings.view_transform = 'Standard'
    except Exception:
        pass
    sc.camera = kamera_widoku('kamera_zlozony', 'PERSP', WIDOK_ZLOZONY, Vector((0, 0, P['korpus_h'] * 0.65)), wszystkie, zestaw_zlozony(zestaw))
    return mat


def baza_kamery(widok):
    e, a = widok
    R = Euler((math.radians(90 - e), 0.0, math.radians(a)), 'XYZ').to_matrix()
    return R, R @ Vector((1, 0, 0)), R @ Vector((0, 1, 0)), R @ Vector((0, 0, 1))


def zestaw_zlozony(zestaw):
    """Nazwy obiektow zestawu zlozonego (K-53) bez pokrywki (render zlozony: z plytka wieczorna)."""
    return [n for n in zestaw if grupa_rozsuniecia(n) is not None and n != 'pokrywka']


def wierzcholki_swiat(ob):
    M = ob.matrix_world
    return [M @ v.co for v in ob.data.vertices]


def kamera_widoku(nazwa, typ, widok, cel, wszystkie, widoczne, R_wlasny=None):
    """Kamera skierowana wg widoku (wysokosc, azymut) albo R_wlasny; kadr dopasowany do obiektow 'widoczne'."""
    if R_wlasny is not None:
        R = R_wlasny
        prawo, gora, tyl = R @ Vector((1, 0, 0)), R @ Vector((0, 1, 0)), R @ Vector((0, 0, 1))
    else:
        R, prawo, gora, tyl = baza_kamery(widok)
    pts = [p for n in widoczne for p in wierzcholki_swiat(wszystkie[n])]
    cam = bpy.data.cameras.new(nazwa)
    cam.clip_start, cam.clip_end = 1.0, 10000.0
    ob = bpy.data.objects.new(nazwa, cam)
    bpy.context.scene.collection.objects.link(ob)
    asp = RENDER_ROZDZ[0] / RENDER_ROZDZ[1]
    if typ == 'ORTHO':
        us = [p.dot(prawo) for p in pts]
        vs = [p.dot(gora) for p in pts]
        cam.type = 'ORTHO'
        cam.ortho_scale = max(max(us) - min(us), (max(vs) - min(vs)) * asp) * 1.08
        srodek = prawo * (max(us) + min(us)) / 2 + gora * (max(vs) + min(vs)) / 2
        ob.location = srodek + tyl * (max(p.dot(tyl) for p in pts) + 500)
    else:
        cam.type = 'PERSP'
        cam.lens = 50.0
        cam.sensor_width = 36.0
        r = max((p - cel).length for p in pts)
        pol_kata = math.atan((cam.sensor_width / asp / 2) / cam.lens)
        ob.location = cel + tyl * (r / math.sin(pol_kata) * 1.02)
    ob.rotation_euler = R.to_euler('XYZ')
    return ob


def bm_linia(p0, p1, r):
    d = p1 - p0
    bm = bm_z_pierscieni([(okrag(r, n=8), 0.0), (okrag(r, n=8), d.length)])
    M = Matrix.Translation(p0) @ Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
    return bm_transformuj(bm, M)


def font_podpisow():
    """Podpisy renderu: DejaVuSansMono z instalacji Blendera (font statyczny; Inter ma nakladajace sie kontury)."""
    if 'podpisy' not in _FONT:
        kat = os.path.join(bpy.utils.resource_path('LOCAL'), 'datafiles', 'fonts')
        pliki = [f for f in sorted(os.listdir(kat)) if f.startswith('DejaVuSansMono')]
        _FONT['podpisy'] = bpy.data.fonts.load(os.path.join(kat, pliki[0])) if pliki else bpy.data.fonts.load('<builtin>')
    return _FONT['podpisy']


def obiekt_podpisu(tresc, rozmiar, M, wyrownanie, mat):
    cu = bpy.data.curves.new('podpis', 'FONT')
    cu.body = tresc
    cu.font = font_podpisow()
    cu.size = rozmiar
    cu.align_x = wyrownanie
    cu.align_y = 'CENTER'
    cu.fill_mode = 'FRONT'
    cu.materials.append(mat)
    ob = bpy.data.objects.new('podpis', cu)
    bpy.context.scene.collection.objects.link(ob)
    ob.matrix_world = M
    return ob


def widocznosc(nazwy_obiektow, wszystkie, tyl, maks=400):
    """Liczba probek wierzcholkow obiektow, z ktorych promien w strone kamery (ortogonalnej) nie trafia w nic."""
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    sc = bpy.context.scene
    pts = [p for n in nazwy_obiektow for p in wierzcholki_swiat(wszystkie[n])]
    krok = max(1, len(pts) // maks)
    wid = 0
    for p in pts[::krok]:
        traf = sc.ray_cast(dg, p + tyl * 0.02, tyl)[0]
        if not traf:
            wid += 1
    return wid, len(pts[::krok])


def renderuj(sciezka):
    bpy.context.scene.render.filepath = sciezka
    bpy.ops.render.render(write_still=True)
    log('render', os.path.basename(sciezka))


def rendery(P, out, wszystkie, mat, zestaw):
    """Trzy rendery (R15, K-60). Polozenia obiektow zmieniane tylko na czas renderu (.blend jest juz zapisany w pozycji zlozonej).
    Zwraca opis widocznosci podpisow renderu rozstrzelonego (K-60)."""
    kat = os.path.join(out, 'render')
    os.makedirs(kat, exist_ok=True)
    sc = bpy.context.scene
    tymczasowe = []
    mat_podpis = material('podpis', '#1e1f22', szorstkosc=1.0)

    def pokaz_tylko(nazwy):
        for n, ob in wszystkie.items():
            ukryj = n not in nazwy
            ob.hide_render = ukryj
            ob.hide_viewport = ukryj

    # 1. zlozony 3/4 od przodu, z plytka wieczorna n1 (bez pokrywki)
    pokaz_tylko(zestaw_zlozony(zestaw))
    renderuj(os.path.join(kat, 'render_zlozony.png'))
    # 2. rozstrzelony: izometria (ortogonalna), rozsuniecie wzdluz Z, czesci z wnetrza korpusu wysuniete w lewo ekranu
    R, prawo, gora, tyl = baza_kamery(WIDOK_ROZSTRZELONY)
    wysun = -prawo * WYSUNIECIE_WNETRZA
    widoczne = [n for n in zestaw if grupa_rozsuniecia(n) is not None]
    for n in widoczne:
        g = grupa_rozsuniecia(n)
        wszystkie[n].matrix_world = Matrix.Translation(Vector((0, 0, ROZSUNIECIE[g])) + (wysun if g == 'wnetrze' else Vector()))
    pokaz_tylko(widoczne)
    wid = {}
    for tekst, obiekty, _s in PODPISY:
        wid[tekst] = widocznosc([o for o in obiekty if o in wszystkie], wszystkie, tyl)
    # podpisy w dwoch kolumnach (prawej i lewej) przed wszystkimi czesciami, z liniami odniesienia
    pts = {n: wierzcholki_swiat(wszystkie[n]) for n in widoczne}
    w_przod = max(p.dot(tyl) for l in pts.values() for p in l) + 20
    u_max = max(p.dot(prawo) for n, l in pts.items() if grupa_rozsuniecia(n) != 'wnetrze' for p in l)
    u_min = min(p.dot(prawo) for n, l in pts.items() if grupa_rozsuniecia(n) == 'wnetrze' for p in l)
    for strona in ('P', 'L'):
        lista = []
        for tekst, obiekty, s in PODPISY:
            if s != strona or not all(o in wszystkie for o in obiekty):
                continue
            kand = [p for o in obiekty for p in pts[o]]
            kotwica = max(kand, key=lambda p: p.dot(prawo)) if strona == 'P' else min(kand, key=lambda p: p.dot(prawo))
            lista.append([kotwica.dot(gora), tekst, kotwica])
        lista.sort(key=lambda x: x[0])
        for i in range(1, len(lista)):
            lista[i][0] = max(lista[i][0], lista[i - 1][0] + 1.8 * PODPIS_ROZMIAR)
        u_kol = u_max + 30 if strona == 'P' else u_min - 30
        for v, tekst, kotwica in lista:
            p_tekst = prawo * u_kol + gora * v + tyl * w_przod
            M = Matrix.Translation(p_tekst) @ R.to_4x4()
            tymczasowe.append(obiekt_podpisu(tekst, PODPIS_ROZMIAR, M, 'LEFT' if strona == 'P' else 'RIGHT', mat_podpis))
            koniec = p_tekst - prawo * (4 if strona == 'P' else -4)
            tymczasowe.append(obiekt_z_bm(bm_linia(kotwica, koniec, 0.4), 'linia_podpisu'))
            tymczasowe[-1].data.materials.append(mat_podpis)
    bpy.context.view_layer.update()
    # kadr: czesci + podpisy (szerokosc tekstu z bbox krzywej)
    kadr = {n: wszystkie[n] for n in widoczne}
    for i, ob in enumerate(tymczasowe):
        kadr['_t%d' % i] = ob
    cam = kamera_widoku_ob('kamera_rozstrzelony', R, prawo, gora, tyl, kadr)
    sc.camera = cam
    renderuj(os.path.join(kat, 'render_rozstrzelony.png'))
    for ob in tymczasowe:
        usun_obiekt_dowolny(ob)
    tymczasowe = []
    for n in widoczne:
        wszystkie[n].matrix_world = Matrix.Identity(4)
    # 3. plytki z gory: wieczorna n1 i poranna n4 obok siebie
    plytki = [n for n in ('plytka_wieczorna_n1', 'plytka_poranna_n4') if n in wszystkie]
    for i, n in enumerate(plytki):
        ob = wszystkie[n]
        v = wierzcholki_swiat(ob)
        c = Vector(((min(p.x for p in v) + max(p.x for p in v)) / 2, (min(p.y for p in v) + max(p.y for p in v)) / 2, max(p.z for p in v)))
        cel = Vector(((i - (len(plytki) - 1) / 2) * ODSTEP_PLYTEK_RENDER, 0, 0))
        ob.matrix_world = Matrix.Translation(cel - c)
        opis = n.replace('plytka_', 'płytka ').replace('_n', ' n')
        tymczasowe.append(obiekt_podpisu(opis, 5.0, Matrix.Translation(cel + Vector((0, -P['plate_size'] / 2 - 7, 0))), 'CENTER', mat_podpis))
    pokaz_tylko(plytki)
    slonce = bpy.data.objects.get('slonce')
    obrot_slonca = tuple(slonce.rotation_euler) if slonce else None
    if slonce:
        slonce.rotation_euler = (math.radians(55), 0.0, math.radians(30))     # nisko: cienie w gniazdach widoczne z gory
    kadr = {n: wszystkie[n] for n in plytki}
    for i, ob in enumerate(tymczasowe):
        kadr['_t%d' % i] = ob
    bpy.context.view_layer.update()
    R0 = Matrix.Identity(3)
    sc.camera = kamera_widoku_ob('kamera_plytki', R0, Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1)), kadr)
    renderuj(os.path.join(kat, 'render_plytki.png'))
    if slonce:
        slonce.rotation_euler = obrot_slonca
    for ob in tymczasowe:
        usun_obiekt_dowolny(ob)
    for n, ob in wszystkie.items():
        ob.matrix_world = Matrix.Identity(4)
        ob.hide_render = False
        ob.hide_viewport = False
    return wid


def usun_obiekt_dowolny(ob):
    dane = ob.data
    bpy.data.objects.remove(ob, do_unlink=True)
    if dane is not None and dane.users == 0:
        if isinstance(dane, bpy.types.Mesh):
            bpy.data.meshes.remove(dane)
        elif isinstance(dane, bpy.types.Curve):
            bpy.data.curves.remove(dane)


def kamera_widoku_ob(nazwa, R, prawo, gora, tyl, obiekty):
    """Kamera ortogonalna o bazie R, kadr z bbox obiektow (siatki i krzywe tekstu, przez depsgraph)."""
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for ob in obiekty.values():
        oe = ob.evaluated_get(dg)
        pts += [ob.matrix_world @ Vector(c) for c in oe.bound_box]
    cam = bpy.data.cameras.new(nazwa)
    cam.clip_start, cam.clip_end = 1.0, 10000.0
    cam.type = 'ORTHO'
    ob = bpy.data.objects.new(nazwa, cam)
    bpy.context.scene.collection.objects.link(ob)
    asp = RENDER_ROZDZ[0] / RENDER_ROZDZ[1]
    us = [p.dot(prawo) for p in pts]
    vs = [p.dot(gora) for p in pts]
    cam.ortho_scale = max(max(us) - min(us), (max(vs) - min(vs)) * asp) * 1.06
    ob.location = prawo * (max(us) + min(us)) / 2 + gora * (max(vs) + min(vs)) / 2 + tyl * (max(p.dot(tyl) for p in pts) + 500)
    ob.rotation_euler = R.to_euler('XYZ')
    return ob


# ===========================================================================
# (6) Arkusze i raport
# ===========================================================================

def sha256(sciezka):
    h = hashlib.sha256()
    with open(sciezka, 'rb') as f:
        for blok in iter(lambda: f.read(1 << 20), b''):
            h.update(blok)
    return h.hexdigest()


def zapisz_kody_plytek(P, sciezka, nazwy_plikow, uklady):
    wiersze = []
    for typ in TYPY_PLYTEK:
        for n in numery_plytek(P, typ):
            b = bity(n)
            dol = [c for c in BITY if b[c]]
            mag = [c for c in 'ABC' if b[c]] if not plytka_okragla(typ) else None      # R57: okragla bez kieszeni magnesow
            wiersze.append((n, typ, mag, dol, nazwy_plikow[n]))
    dk = {typ: ', '.join('%s (%g, %g)' % (d['bit'], d['x'], d['y']) for d in uklady[typ]['code_dimples']) for typ in TYPY_PLYTEK}
    lin = ['# Kody płytek (D11, R4, R57)', '',
           'Numer płytki n = A + 2·B + 4·C + 8·D [R57: 4. bit D]. Na płytkach kwadratowych bit = 1 oznacza magnes wklejony w kieszeni narożnika (A przód‑lewy, B tył‑lewy, C tył‑prawy; '
           'narożnik D z wycięciem bez kieszeni; bit D nie ma kieszeni i na n1–n6 nie występuje). '
           'Ten sam numer kodują dołki ø%g × %g na wierzchu — dołek jest tylko dla bitu = 1; pozycje (x, y) z `uklad_gniazd_<typ>.json → code_dimples`: '
           'kwadrat wieczorna %s; kwadrat poranna %s; okrągła wieczorna %s; okrągła poranna %s. '
           'Płytki okrągłe (R57, tylko do skanera) nie mają kieszeni magnesów — numer tylko w dołkach. 7 = rezerwa, 0 = brak płytki.'
           % (P['code_dimple_d'], P['code_dimple_depth'], dk['wieczorna'], dk['poranna'], dk['okragla_wieczorna'], dk['okragla_poranna']), '',
           '| n | Typ płytki | Magnesy w kieszeniach | Dołki kodu (bity) | Plik STL |', '|---|---|---|---|---|']
    for n, typ, mag, dol, plik in wiersze:
        lin.append('| %d | %s | %s | %s | `%s` |' % (n, typ.replace('_', ' '), ' + '.join(mag) if mag is not None else 'brak kieszeni (okrągła, R57)', ' + '.join(dol), plik))
    lin += ['', '## Klejenie magnesów (ø%g × %g N35)' % (P['magnet_d'], P['magnet_h']), '',
            '1. Biegun: we wszystkich płytkach biegun **S** skierowany w dół (do czujnika Halla). Biegun musi być jednakowy we wszystkich płytkach.',
            '2. Wzorzec: jeden magnes oznacz raz (biegun S flamastrem) według kompasu lub czujnika A3144 (reaguje tylko na biegun S). Każdy kolejny magnes przyłóż do wzorca: strona przyciągana przez oznaczoną stronę S wzorca to biegun N — tę stronę kieruj do góry (do dna kieszeni), a stronę S w dół.',
            '3. Przed klejeniem sprawdź płytkę na wkładce ramki: odczyt numeru musi być równy n z tabeli; dopiero potem kropla kleju CA żelowego w kieszeń (od spodu płytki), magnes cofnięty 0,2 mm w kieszeni %g mm.' % P['magnet_pocket_depth'],
            '4. Kontrola po klejeniu: płytka położona na wkładce daje n w < 100 ms; bez płytki 0.', '']
    with open(sciezka, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lin))
    return wiersze


def sprawdz_kody(W, P, sciezka, wyniki_k11):
    """K-58: kody_plytek.md <-> warianty STL (K-11) <-> D11."""
    with open(sciezka, encoding='utf-8') as f:
        tekst = f.read()
    bledy = []
    tab = re.findall(r'^\| (\d+) \| ([\wą-ż ]+) \| ([^|]*) \| ([A-D + ]*) \| `([^`]+)` \|', tekst, re.M)
    numery = sorted(int(t[0]) for t in tab)
    oczek_numery = sorted(n for typ in TYPY_PLYTEK for n in numery_plytek(P, typ))
    if numery != oczek_numery:
        bledy.append('numery %s ≠ %s' % (numery, oczek_numery))
    for n_s, typ, mag, doł, plik in tab:
        n = int(n_s)
        typ = typ.strip().replace(' ', '_')
        b = bity(n)
        oczek = bity_tekst(n)
        okr = typ.startswith('okragla_')
        oczek_mag = 'brak' if okr else '+'.join(c for c in 'ABC' if b[c])
        mag_t = 'brak' if 'brak' in mag else mag.replace(' ', '')
        if mag_t != oczek_mag or doł.replace(' ', '') != oczek:
            bledy.append('n%d: tabela %s/%s, D11 %s/%s' % (n, mag, doł, oczek_mag, oczek))
        zm = wyniki_k11.get(n)
        if zm != oczek:
            bledy.append('n%d: STL (K-11) %s ≠ %s' % (n, zm, oczek))
        if typ not in TYPY_PLYTEK or n not in numery_plytek(P, typ):
            bledy.append('n%d: typ %s' % (n, typ))
    slowa = [s for s in ('biegun', 'S', 'jednakowy') if s not in tekst]
    if slowa:
        bledy.append('brak słów %s' % slowa)
    W.dodaj('K-58', not bledy, 'kody_plytek.md: %d wierszy; zgodność z K-11 i D11; słowa biegun/S/jednakowy: %s; błędy: %s'
            % (len(tab), 'są' if not slowa else 'brak', '; '.join(bledy) if bledy else 'brak'), 'tak', 'P')


def liczba_pl(x, n=2):
    if abs(x) < 0.5 * 10 ** -n:
        x = 0.0                      # bez „-0,000”
    return ('%.*f' % (n, x)).replace('.', ',')


def opis_czesci(P, rdzen):
    m = re.match(r'plytka_(wieczorna|poranna)_n(\d)', rdzen)
    if m:
        return 'płytka %s n%s' % (m.group(1), m.group(2))
    m = re.match(r'podkladka_panelu_(\d+)', rdzen)
    if m:
        return 'podkładka panelu %s mm' % ('0,5' if m.group(1) == '05' else m.group(1))
    return {'pokrywka': 'pokrywka płytki', 'korpus_W': 'korpus W (napis „%s”)' % P['label_text_W'],
            'korpus_P': 'korpus P (napis „%s”)' % P['label_text_P'], 'blat': 'blat', 'wkladka': 'wkładka gniazda płytki',
            'tulejka_dc': 'tulejka redukcyjna gniazda DC'}.get(rdzen, rdzen)


DRUKARNIA = 'PA12 drukarnia'      # K-57 (R50): koszt liczony tylko dla pozycji, ktorych material zaczyna sie od tego tekstu

KOLUMNY_ZAMOWIENIA = ['plik STL', 'część', 'ilość', 'technologia', 'materiał', 'kolor', 'wykończenie', 'objętość [cm³]',
                      'gabaryt X × Y × Z [mm]', 'koszt najtańszy min [zł]', 'koszt najtańszy max [zł]', 'koszt pokazowy min [zł]',
                      'koszt pokazowy max [zł]', 'uwagi']


def technologia(mat):
    if mat.startswith(DRUKARNIA):
        return 'MJF/SLS (D2)'
    if 'FDM' in mat:
        return 'FDM (druk własny)'
    return 'FDM PETG (druk własny, R55)'


def wiersze_zamowienia(P):
    """Pozycje z quantities (R50: 10 drukarnia + 5 druk własny, bez plytek bazowych); liczby z siatek STL i z parametry.json."""
    wiersze = []
    for klucz, q in P['quantities'].items():
        rdzen = klucz[len('ramka_'):]
        obj, bb = DZIENNIK['stl'][rdzen]
        obj = round(obj, 2)          # koszty z objetosci w postaci wpisanej do arkusza (K-57 przelicza z CSV)
        mat = P['materials'][klucz]
        grafit = czesc_grafitowa(rdzen)
        drukarnia = mat.startswith(DRUKARNIA)
        if drukarnia:
            nmin, nmax = obj * q * P['cost_rate_min'], obj * q * P['cost_rate_max']
            f = P['cost_dye_factor'] * P['cost_smooth_factor'] if grafit else 1.0
            koszty = (nmin, nmax, nmin * f, nmax * f)
        else:
            koszty = None
        if rdzen.startswith('plytka') or rdzen == 'pokrywka':
            wyk = 'mat, bez wygładzania wierzchu'
        elif grafit:
            wyk = 'barwienie na grafit; pokazowy: + wygładzanie parowe'
        else:
            wyk = 'surowe (naturalne)'
        uwagi = []
        if rdzen.startswith('plytka'):
            uwagi.append('alternatywa CNC PMMA opal: STEP przez FreeCAD (D2)')
        if rdzen.startswith('korpus'):
            uwagi.append('geometria W i P identyczna poza napisem (Z18)')
        if rdzen == 'tulejka_dc':
            uwagi.append('tylko gdy pomiar #16 da gniazdo ø8 (R50-3)')
        if rdzen.startswith('podkladka'):
            uwagi.append('do wyrównania dystansu po pomiarach #4/#9 (R50-8)')
        wiersze.append({'plik': nazwa_stl(P, rdzen), 'rdzen': rdzen, 'czesc': opis_czesci(P, rdzen), 'q': q, 'tech': technologia(mat),
                        'mat': mat, 'kolor': 'grafit' if grafit else 'biały (naturalny)', 'wyk': wyk, 'obj': obj,
                        'gab': (bb[1] - bb[0], bb[3] - bb[2], bb[5] - bb[4]), 'koszty': koszty, 'uwagi': '; '.join(uwagi)})
    return wiersze


def zapisz_arkusz_zamowienia(P, out):
    w = wiersze_zamowienia(P)
    kat = os.path.join(out, 'arkusze')
    os.makedirs(kat, exist_ok=True)
    sc_csv, sc_md = os.path.join(kat, 'arkusz_zamowienia.csv'), os.path.join(kat, 'arkusz_zamowienia.md')
    rmin, rmax, fd, fs = P['cost_rate_min'], P['cost_rate_max'], P['cost_dye_factor'], P['cost_smooth_factor']
    lin = [';'.join(KOLUMNY_ZAMOWIENIA)]
    for r in w:
        koszty = [liczba_pl(k) for k in r['koszty']] if r['koszty'] else ['', '', '', '']
        pola = [r['plik'], r['czesc'], str(r['q']), r['tech'], r['mat'], r['kolor'], r['wyk'], liczba_pl(r['obj']),
                '%s × %s × %s' % tuple(liczba_pl(g, 1) for g in r['gab'])] + koszty + [r['uwagi']]
        lin.append(';'.join(p.replace(';', ',') for p in pola))      # separator CSV nie moze wystapic w polu
    with open(sc_csv, 'w', encoding='utf-8-sig', newline='') as f:
        f.write('\r\n'.join(lin) + '\r\n')
    wd = [r for r in w if r['koszty']]
    ww = [r for r in w if not r['koszty']]
    s = lambda i: sum(r['koszty'][i] for r in wd)
    L = ['# Arkusz zamówienia — części drukowane (v%s)' % P['file_suffix'][1:], '',
         'Wygenerowany przez `ramka_generator.py`. Objętości i gabaryty zmierzone na siatkach STL (gabaryt w orientacji druku). '
         'Ilości z `parametry.json → quantities`, materiały per część z `materials` (R50). %d pozycji: %d do drukarni, %d druku własnego '
         '(bez płytek bazowych, Z28). Ten sam arkusz w `arkusz_zamowienia.csv` (separator `;`, przecinek dziesiętny, UTF‑8; koszty puste = druk własny).'
         % (len(w), len(wd), len(ww)), '', '## A. Do zamówienia w drukarni (materiał „%s…”)' % DRUKARNIA, '',
         '| Plik STL | Część | Szt. | Technologia | Materiał | Kolor | Wykończenie | Obj. [cm³] | Gabaryt X × Y × Z [mm] | Najtańszy [zł] | Pokazowy [zł] | Uwagi |',
         '|---|---|---|---|---|---|---|---|---|---|---|---|']
    for r in wd:
        k = r['koszty']
        L.append('| `%s` | %s | %d | %s | %s | %s | %s | %s | %s | %s–%s | %s–%s | %s |' % (
            r['plik'], r['czesc'], r['q'], r['tech'], r['mat'], r['kolor'], r['wyk'], liczba_pl(r['obj']),
            ' × '.join(liczba_pl(g, 1) for g in r['gab']), liczba_pl(k[0], 0), liczba_pl(k[1], 0), liczba_pl(k[2], 0), liczba_pl(k[3], 0), r['uwagi'] or '—'))
    L += ['', '## B. Druk własny (bez kosztu drukarni)', '',
          '| Plik STL | Część | Szt. | Technologia | Materiał | Obj. [cm³] | Gabaryt X × Y × Z [mm] | Uwagi |', '|---|---|---|---|---|---|---|---|']
    for r in ww:
        L.append('| `%s` | %s | %d | %s | %s | %s | %s | %s |' % (r['plik'], r['czesc'], r['q'], r['tech'], r['mat'], liczba_pl(r['obj'], 3),
                                                           ' × '.join(liczba_pl(g, 1) for g in r['gab']), r['uwagi'] or '—'))
    L += ['', '## Sumy (tylko drukarnia)', '',
          '| Zakres | Objętość [cm³] | Najtańszy [zł] | Pokazowy [zł] |', '|---|---|---|---|',
          '| %d pozycji × ilości | %s | %s–%s | %s–%s |' % (len(wd), liczba_pl(sum(r['obj'] * r['q'] for r in wd)), liczba_pl(s(0), 0), liczba_pl(s(1), 0),
                                                         liczba_pl(s(2), 0), liczba_pl(s(3), 0)),
          '', 'Druk własny: %s cm³ (%s).' % (liczba_pl(sum(r['obj'] * r['q'] for r in ww), 1), ', '.join('%s × %d' % (r['czesc'], r['q']) for r in ww)),
          '', '## Stawki i wzory (z `parametry.json`)', '',
          '- Stawka PA12: `cost_rate_min` %s – `cost_rate_max` %s zł/cm³; barwienie `cost_dye_factor` ×%s; wygładzanie `cost_smooth_factor` ×%s.'
          % (liczba_pl(rmin), liczba_pl(rmax), liczba_pl(fd), liczba_pl(fs)),
          '- Koszt tylko dla pozycji z materiałem zaczynającym się od „%s” (K‑57, R50); druk własny bez kosztu.' % DRUKARNIA,
          '- Wariant najtańszy (PA12 naturalne, bez barwienia): koszt = objętość × ilość × stawka (min…max).',
          '- Wariant pokazowy: części grafitowe (korpus, blat — Z19) = objętość × ilość × stawka × %s × %s; części białe bez mnożników.' % (liczba_pl(fd), liczba_pl(fs)),
          '- Płytki wieczorne n1–n3 liczone do drukarni (R55: bez alternatywy żywicznej).',
          '', '## Uwaga dla CNC (STEP / FreeCAD)', '',
          'Usługodawca CNC (płytki z PMMA opal, D2) potrzebuje pliku STEP: FreeCAD → Part → „Utwórz kształt z siatki” (tolerancja 0,01) → '
          '„Przekształć w bryłę” → Eksport `.step`. STL pozostaje plikiem wzorcowym; STEP nie jest generowany przez skrypt.', '']
    with open(sc_md, 'w', encoding='utf-8') as f:
        f.write('\n'.join(L))
    return sc_csv, sc_md


def sprawdz_arkusz_zamowienia(W, P, out):
    """K-57 (R50): CSV <-> STL (wlasny pomiar w tym przebiegu), quantities, materials per czesc, koszt tylko dla drukarni,
    15 wierszy (10 + 5), brak bazowych, uwaga STEP/FreeCAD."""
    sc_csv = os.path.join(out, 'arkusze', 'arkusz_zamowienia.csv')
    sc_md = os.path.join(out, 'arkusze', 'arkusz_zamowienia.md')
    bledy = []
    if not (os.path.isfile(sc_csv) and os.path.isfile(sc_md)):
        W.dodaj('K-57', False, 'brak arkusza zamówienia', 'wszystko', 'P')
        return
    with open(sc_csv, encoding='utf-8-sig') as f:
        rows = [l.split(';') for l in f.read().splitlines() if l.strip()]
    nag, rows = rows[0], rows[1:]
    if nag != KOLUMNY_ZAMOWIENIA:
        bledy.append('nagłówek CSV')
    num = lambda s: float(s.replace(',', '.'))
    n_druk = sum(1 for k in P['quantities'] if P['materials'][k].startswith(DRUKARNIA))
    if len(rows) != len(P['quantities']):
        bledy.append('wierszy %d (quantities %d)' % (len(rows), len(P['quantities'])))
    dmax_obj = dmax_gab = dmax_k = 0.0
    licz_d = 0
    kol_k = ['koszt najtańszy min [zł]', 'koszt najtańszy max [zł]', 'koszt pokazowy min [zł]', 'koszt pokazowy max [zł]']
    for r in rows:
        d = dict(zip(nag, r))
        plik = d['plik STL']
        rdzen = plik[len('ramka_'):-len('_%s.stl' % P['file_suffix'])]
        klucz = 'ramka_' + rdzen
        if not re.search(r'_n\d_', plik) and rdzen.startswith('plytka'):
            bledy.append('płytka bazowa %s' % plik)
        if not os.path.isfile(os.path.join(out, 'stl', plik)):
            bledy.append('brak pliku %s' % plik)
            continue
        if klucz not in P['quantities']:
            bledy.append('%s poza quantities' % plik)
            continue
        obj, bb = DZIENNIK['stl'][rdzen]
        dmax_obj = max(dmax_obj, abs(num(d['objętość [cm³]']) - obj))
        gab = [num(g) for g in d['gabaryt X × Y × Z [mm]'].split(' × ')]
        dmax_gab = max(dmax_gab, max(abs(a - b) for a, b in zip(gab, (bb[1] - bb[0], bb[3] - bb[2], bb[5] - bb[4]))))
        q = int(d['ilość'])
        if q != P['quantities'][klucz]:
            bledy.append('%s: ilość %d ≠ %d' % (plik, q, P['quantities'][klucz]))
        mat = P['materials'][klucz]
        if d['materiał'] != mat:
            bledy.append('%s: materiał' % plik)
        if mat.startswith(DRUKARNIA):
            licz_d += 1
            o = num(d['objętość [cm³]'])
            f = P['cost_dye_factor'] * P['cost_smooth_factor'] if czesc_grafitowa(rdzen) else 1.0
            for kol, oczek in zip(kol_k, (o * q * P['cost_rate_min'], o * q * P['cost_rate_max'], o * q * P['cost_rate_min'] * f, o * q * P['cost_rate_max'] * f)):
                dmax_k = max(dmax_k, abs(num(d[kol]) - oczek))
        elif any(d[kol] for kol in kol_k):
            bledy.append('%s: koszt przy druku własnym' % plik)
    if licz_d != n_druk:
        bledy.append('pozycji drukarni %d ≠ %d' % (licz_d, n_druk))
    if dmax_obj > 0.01:
        bledy.append('objętość różni się o %.3f' % dmax_obj)
    if dmax_gab > TOL_WYM:
        bledy.append('gabaryt różni się o %.3f' % dmax_gab)
    if dmax_k > 0.01:
        bledy.append('koszt różni się od wzoru o %.3f' % dmax_k)
    with open(sc_md, encoding='utf-8') as f:
        md = f.read()
    if 'STEP' not in md or 'FreeCAD' not in md:
        bledy.append('brak uwagi STEP/FreeCAD')
    W.dodaj('K-57', not bledy, 'arkusz_zamowienia.csv: %d wierszy (%d drukarnia + %d druk własny); max różnica objętości %.3f cm³, gabarytu %.3f mm, '
            'kosztu względem wzoru %.3f zł; uwaga STEP/FreeCAD: %s; błędy: %s'
            % (len(rows), licz_d, len(rows) - licz_d, dmax_obj, dmax_gab, dmax_k, 'jest' if 'FreeCAD' in md else 'brak', '; '.join(bledy) or 'brak'),
            '%d wierszy (= quantities); obj. ± 0,01; gabaryt ± 0,1; materiały per część; koszt tylko drukarnia' % len(P['quantities']), 'P')


# ---- arkusz wymiarow: pomiary promieniami na siatkach STL (uklad montazowy) i w zlozeniu ----

def _os(d):
    return Vector({'X': (1, 0, 0), 'Y': (0, 1, 0), 'Z': (0, 0, 1), '-X': (-1, 0, 0), '-Y': (0, -1, 0), '-Z': (0, 0, -1)}[d])


def pomiar(bvh, typ, p, d):
    """'z' - wymiar zewnetrzny przez punkt p wzdluz osi d (skrajne sciany z zewnatrz); 'w' - cieciwa od punktu p do scian
    w obu kierunkach (otwor, gdy p w powietrzu; scianka, gdy p w materiale); 'p' - wspolrzedna pierwszego trafienia z p wzdluz d."""
    p, d = Vector(p), _os(d)
    if typ == 'z':
        a, b = pierwsze_trafienie(bvh, p - d * 2000, d), pierwsze_trafienie(bvh, p + d * 2000, -d)
        return None if a is None or b is None else (b - a).dot(d)
    if typ == 'w':
        a, b = pierwsze_trafienie(bvh, p, d), pierwsze_trafienie(bvh, p, -d)
        return None if a is None or b is None else (a - b).dot(d)
    a = pierwsze_trafienie(bvh, p, d)
    return None if a is None else a.dot(Vector([abs(c) for c in d]))


def lista_wymiarow(P, uklady):
    """(rdzen, [(opis, typ, punkt, os, wartosc nominalna z parametry.json)]) - uklady montazowe czesci (protokol 0.3)."""
    S, T = P['plate_size'], P['plate_thickness']
    tg = math.tan(math.radians(P['socket_wall_angle']))
    wyn = []
    # R57: plytki okragle n8/n9 — pierwsze gniazdo, dolek, znacznik A jak kwadrat; obrys: cieciwa zewnetrzna 2*sqrt(R^2 - 20^2) na y = 20, grubosc na (0, -46,5)
    for rdzen, typ in (('plytka_wieczorna_n1', 'wieczorna'), ('plytka_poranna_n4', 'poranna'),
                       ('plytka_okragla_wieczorna_n%d' % P['plate_numbers_round']['wieczorna'][0], 'okragla_wieczorna'),
                       ('plytka_okragla_poranna_n%d' % P['plate_numbers_round']['poranna'][0], 'okragla_poranna')):
        numer = int(rdzen.rsplit('_n', 1)[1])
        g = next(s for s in uklady[typ]['sockets'] if s['type'] == 'round')      # R54: id 1 wieczornej to rynienka; mierzone pierwsze gniazdo okragle
        dl = [d for d in uklady[typ]['code_dimples'] if bity(numer)[d['bit']]][0]
        mA = [m for m in uklady[typ]['markers'] if m['corner'] == 'A'][0]      # R54: znacznik A z JSON (ev_/mo_marker_pos)
        zA = (mA['x'], mA['y'])
        if plytka_okragla(typ):
            R = uklady[typ]['d'] / 2
            fl = uklady[typ]['flat']
            c, s_ = math.cos(math.radians(fl['angle_deg'])), math.sin(math.radians(fl['angle_deg']))
            wyn.append((rdzen, [
                ('cięciwa zewn. na y = 20 (2·√(R² − 20²))', 'z', (0, 20, -4), 'X', 2 * math.sqrt(R * R - 400)),
                ('cięciwa zewn. na x = −20', 'z', (-20, 0, -4), 'Y', 2 * math.sqrt(R * R - 400)),
                ('grubość', 'z', (0, -46.5, -4), 'Z', T),
                ('ścięcie (K‑61 mierzy promieniowo; tu: grubość przy ścięciu, punkt %.1f od środka na %g°)' % (fl['dist'] - 0.3, fl['angle_deg']), 'z',
                 (c * (fl['dist'] - 0.3), s_ * (fl['dist'] - 0.3), -4), 'Z', T),
                ('gniazdo id %d: ø na Z −2 (d − 2·2·tan 15°)' % g['id'], 'w', (g['x'], g['y'], -2), 'X', g['d_top'] - 2 * 2 * tg),
                ('gniazdo id %d: otwór w dnie ø' % g['id'], 'w', (g['x'], g['y'], -6), 'X', P['socket_hole_d']),
                ('gniazdo id %d: dno (Z)' % g['id'], 'p', (g['x'] + 2, g['y'], 1), '-Z', -P['socket_depth']),
                ('dołek kodu %s ø' % dl['bit'], 'w', (dl['x'], dl['y'], -0.5), 'X', P['code_dimple_d']),
                ('stożek znacznika A (%g, %g) ø na wierzchu (R54)' % zA, 'w', (zA[0], zA[1], -0.05), 'X', P['marker_cone_d'] * (1 - 0.05 / P['marker_cone_depth']))]))
            continue
        wyn.append((rdzen, [
            ('bok X', 'z', (0, 20, -4), 'X', S), ('bok Y', 'z', (20, 0, -4), 'Y', S), ('grubość', 'z', (0, -46.5, -4), 'Z', T),
            ('gniazdo id %d: ø na Z −2 (d − 2·2·tan 15°)' % g['id'], 'w', (g['x'], g['y'], -2), 'X', g['d_top'] - 2 * 2 * tg),
            ('gniazdo id %d: otwór w dnie ø' % g['id'], 'w', (g['x'], g['y'], -6), 'X', P['socket_hole_d']),
            ('gniazdo id %d: dno (Z)' % g['id'], 'p', (g['x'] + 2, g['y'], 1), '-Z', -P['socket_depth']),
            ('dołek kodu %s ø' % dl['bit'], 'w', (dl['x'], dl['y'], -0.5), 'X', P['code_dimple_d']),
            ('kieszeń magnesu A ø', 'w', (-42, -42, -7), 'X', P['magnet_pocket_d']),
            ('kieszeń magnesu A: sufit (Z)', 'p', (-42, -42, -7), 'Z', -T + P['magnet_pocket_depth']),
            ('rowek pokrywki: dno (x)', 'p', (60, 20, -P['cover_groove_z']), '-X', S / 2 - P['cover_groove_depth']),
            ('stożek znacznika A (%g, %g) ø na wierzchu (R54)' % zA, 'w', (zA[0], zA[1], -0.05), 'X', P['marker_cone_d'] * (1 - 0.05 / P['marker_cone_depth']))]))
    wew, zew, wys = wymiary_pokrywki(P)
    wyn.append(('pokrywka', [('bok X', 'z', (0, 20, -10), 'X', zew), ('wnęka X', 'w', (0, 20, -10), 'X', wew),
                             ('wnęka Y', 'w', (20, 0, -10), 'Y', wew), ('wysokość kołnierza', 'z', (49, 20, -10), 'Z', wys),
                             ('grubość wierzchu (pełny, R50‑U17)', 'z', (15, 0, -1), 'Z', P['cover_top_t']),
                             ('wierzch płaski (R50‑U14)', 'p', (0, 0, 5), '-Z', 0.0),
                             ('garb prawy: czubek (x)', 'p', (0, 0, P['cover_snap_z']), 'X', wew / 2 - P['cover_snap_bump'])]))
    h = P['insert_opening'] / 2
    zw = h + P['insert_wall_w']
    pc = h - P['orient_post_gap'] - P['orient_post'] / 2
    m = S / 2 - P['marker_offset']
    wyn.append(('wkladka', [('rama zewn. X', 'z', (0, 0, 4), 'X', P['insert_opening'] + 2 * P['insert_wall_w']),
                            ('otwór X', 'w', (0, 0, 4), 'X', P['insert_opening']), ('otwór Y (x = 20, poza wycięciem palcowym)', 'w', (20, 0, 4), 'Y', P['insert_opening']),
                            ('otwór: naroże ostre (x przy y = 48,1)', 'p', (0, h - 0.2, 4), 'X', h),
                            ('wysokość ramy', 'z', (-40, -50.3, 3), 'Z', P['insert_h']), ('półka A: grubość', 'z', (-38, -38, 1), 'Z', P['insert_shelf_h']),
                            ('rowek kablowy prawy: dno (x)', 'p', (zw + 5, 0, P['wire_rabbet'] / 2), '-X', zw - P['wire_rabbet_w']),
                            ('rowek kablowy prawy: sufit (Z)', 'p', (zw - P['wire_rabbet_w'] / 2, 0, -5), 'Z', P['wire_rabbet']),
                            ('kołek orientacyjny X', 'w', (pc, -pc, 5), 'X', P['orient_post']),
                            ('kołek orientacyjny: szczyt (Z)', 'p', (pc, -pc, 5), 'Z', P['insert_shelf_h'] + P['orient_post_h']),
                            ('kieszeń Halla A X', 'w', (-m, -m, 1.5), 'X', P['hall_pocket_w']), ('kieszeń Halla A Y', 'w', (-m, -m, 1.5), 'Y', P['hall_pocket_l']),
                            ('wycięcie palcowe X', 'w', (0, -50.3, 3), 'X', P['finger_cut_w']),
                            ('ucho: grubość', 'z', (P['tab_pos_x'], 80, 1), 'Z', P['tab_t']),
                            ('kołek ustalający ø', 'w', (P['tab_pos_x'], P['tab_pin_y'], -2), 'X', P['tab_pin_d']),
                            ('kołek ustalający: koniec (Z)', 'p', (P['tab_pos_x'], P['tab_pin_y'], -1), '-Z', -P['tab_pin_h']),
                            ('otwór magnesu ucha ø', 'w', (P['tab_pos_x'], P['tab_magnet_y'], 1.5), 'X', P['tab_magnet_hole_d'])]))
    so, rs, z0 = wymiary_blatu(P)
    zs = P['blat_screw_z'] - P['blat_top_z']
    xp = P['blat_screw_pitch'] / 2
    dp = P['diffuser_pocket'] / 2
    wyn.append(('blat', [('bok X', 'z', (0, 20, -2), 'X', P['box_outer']), ('kieszeń dyfuzora X', 'w', (0, 20, -1), 'X', P['diffuser_pocket']),
                         ('kieszeń dyfuzora: naroże ostre (x przy y = 80,8)', 'p', (0, dp - 0.2, -1), 'X', dp),
                         ('okno X', 'w', (0, 20, -3), 'X', P['window_through']), ('grubość płyty', 'z', (90, 0, -2), 'Z', P['blat_t']),
                         ('płyta pod dawnym bossem ramy (R50‑U1): spód (Z)', 'p', (90, 90, -20), 'Z', -P['blat_t']),
                         ('kołnierz zewn. X', 'z', (0, 20, -9), 'X', 2 * so), ('kołnierz + płyta: wysokość', 'z', (96, 20, -9), 'Z', P['blat_t'] + P['blat_skirt_h']),
                         ('haczyk prawy: czubek (x)', 'p', (110, 0, -9.5), '-X', so + P['snap_hook_h']),
                         ('otwór słupka ø', 'w', (xp, 94, zs), 'X', P['insert_hole_m3']),
                         ('otwór słupka: dno (y)', 'p', (xp, 94, zs), '-Y', so - P['blat_post_hole_depth']),
                         ('otwór kołka ø', 'w', (P['tab_pos_x'], P['tab_pin_y'], -2), 'X', P['blat_pin_hole_d']),
                         ('otwór kołka: dno (Z)', 'p', (P['tab_pos_x'], P['tab_pin_y'], -1), '-Z', -P['blat_pin_hole_depth']),
                         ('kieszeń magnesu ø', 'w', (P['tab_pos_x'], P['tab_magnet_y'], -1), 'X', P['blat_magnet_pocket_d']),
                         ('szczelina kabla X', 'w', (P['wire_slot_x'], P['wire_slot_y'], -2), 'X', P['wire_slot_w']),
                         ('szczelina kabla Y', 'w', (P['wire_slot_x'], P['wire_slot_y'], -2), 'Y', P['wire_slot_l'])]))
    B, w, ft = P['box_outer'], P['wall_t'], P['floor_t']
    bx, by = pozycje_bossow_pi(P)[0]
    ux, uz = P['usb_pos_x'], P['usb_pos_z']
    zd = P['dc_pocket_z0'] + P['dc_pocket_h'] / 2
    xo, xd, dwl = P['dc_pocket_x_window'], P['dc_pos_x'], P['dc_pocket_wall']
    a0, a1 = P['usb_slot_pitch_min'] / 2, P['usb_slot_pitch_max'] / 2
    wyn.append(('korpus_W', [('bok X', 'z', (0, 20, 20), 'X', B), ('bok Y', 'z', (20, 0, 20), 'Y', B),
                             ('wnętrze X', 'w', (0, 20, 20), 'X', B - 2 * w), ('wnętrze Y', 'w', (20, 0, 20), 'Y', B - 2 * w),
                             ('ściana: wierzch (Z)', 'p', (B / 2 - w / 2, 20, 200), '-Z', P['korpus_h']), ('dno', 'z', (20, -20, 1), 'Z', ft),
                             ('stadion panelu: wierzch (Z)', 'p', (64, 60, 20), '-Z', ft + P['panel_pad_h']),
                             ('rowek wkrętu panelu: cięciwa wzdłuż X (= szer. × √2)', 'w', (60, 60, 1.5), 'X', P['panel_slot_w'] * math.sqrt(2)),
                             ('boss Pi: wierzch (Z)', 'p', (bx + 3, by, 20), '-Z', ft + P['pi_standoff_h']),
                             ('boss Pi: otwór ø', 'w', (bx, by, ft + 4), 'X', P['insert_hole_m25']),
                             ('boss Pi: krawędź (y)', 'p', (bx, by + 15, ft + 2), '-Y', by + P['pi_boss_d'] / 2),
                             ('wlot w dnie X', 'w', (P['floor_vent_x'], P['floor_vent_y'][0], 1.5), 'X', P['floor_vent_l']),
                             ('wlot w dnie Y', 'w', (P['floor_vent_x'], P['floor_vent_y'][0], 1.5), 'Y', P['floor_vent_w']),
                             ('kieszeń DC: okno X', 'w', (xo, B / 2 - w / 2, zd), 'X', P['dc_pocket_w']),
                             ('kieszeń DC: okno Z', 'w', (xo, B / 2 - w / 2, zd), 'Z', P['dc_pocket_h']),
                             ('kieszeń DC: wnętrze X (lewa ściana skrzynki → prawa)', 'w', (xo, (B / 2 - P['dc_pocket_depth'] + B / 2 - w) / 2, P['dc_pocket_z0'] + 2), 'X',
                              (xd - dwl) - (-(B / 2 - w) + dwl)),
                             ('kieszeń DC: dno w świetle (y)', 'p', (xo, B / 2 + 10, P['dc_pocket_z0'] + 2), '-Y', B / 2 - P['dc_pocket_depth'] + dwl),
                             ('gniazdo DC: otwór ø w prawej ścianie skrzynki (oś X)', 'w', (xd - dwl / 2, P['dc_pos_y'], P['dc_pos_z']), 'Y', P['dc_hole_d']),
                             ('okno USB X', 'w', (ux, B / 2 - w / 2, uz), 'X', P['usb_cut_w']), ('okno USB Z', 'w', (ux, B / 2 - w / 2, uz), 'Z', P['usb_cut_h']),
                             ('rowek flanszy USB prawy X', 'w', (ux + (a0 + a1) / 2, B / 2 - w / 2, uz), 'X', a1 - a0 + P['usb_slot_w']),
                             ('rowek flanszy USB prawy Z', 'w', (ux + (a0 + a1) / 2, B / 2 - w / 2, uz), 'Z', P['usb_slot_w']),
                             ('kieszeń zatrzasku prawa Y', 'w', (B / 2 - w + 0.5, P['snap_side_y'], P['snap_pocket_z'] + 1.2), 'Y', P['snap_pocket_w']),
                             ('kieszeń zatrzasku prawa Z', 'w', (B / 2 - w + 0.5, P['snap_side_y'], P['snap_pocket_z'] + 1.2), 'Z', P['snap_pocket_h']),
                             ('kieszeń zatrzasku: dno (x)', 'p', (80, P['snap_side_y'], P['snap_pocket_z'] + 1.2), 'X', B / 2 - w + P['snap_pocket_depth']),
                             ('szczelina tylna X', 'w', (P['vent_slots_rear_x'][0], B / 2 - w / 2, P['vent_slot_z']), 'X', P['vent_slot_w']),
                             ('szczelina tylna Z', 'w', (P['vent_slots_rear_x'][0], B / 2 - w / 2, P['vent_slot_z']), 'Z', P['vent_slot_h']),
                             ('otwór wkrętu blatu ø (w ścianie)', 'w', (xp, B / 2 - w + 0.3, P['blat_screw_z']), 'X', P['blat_screw_hole_d'])]))
    wyn.append(('tulejka_dc', [('kołnierz ø', 'z', (0, 0, P['dc_bush_flange_t'] / 2), 'X', P['dc_bush_flange_d']),
                               ('walec: promień zewn. (x)', 'p', (10, 0, P['dc_bush_flange_t'] + P['dc_bush_t'] / 2), '-X', P['dc_bush_outer_d'] / 2),
                               ('otwór ø', 'w', (0, 0, 1), 'X', P['dc_bush_inner_d']),
                               ('wysokość', 'z', ((P['dc_bush_inner_d'] + P['dc_bush_outer_d']) / 4, 0, 1), 'Z', P['dc_bush_flange_t'] + P['dc_bush_t']),
                               ('kołnierz: grubość', 'z', ((P['dc_bush_outer_d'] + P['dc_bush_flange_d']) / 4, 0, 0.5), 'Z', P['dc_bush_flange_t'])]))
    for r, t in rdzenie_podkladek(P):
        rr = (P['panel_shim_d'] + P['panel_shim_hole_d']) / 4
        wyn.append((r, [('ø zewn.', 'z', (0, 0, t / 2), 'X', P['panel_shim_d']), ('otwór ø', 'w', (0, 0, t / 2), 'X', P['panel_shim_hole_d']),
                        ('grubość', 'z', (rr, 0, t / 2), 'Z', t)]))
    return wyn


def lista_pasowan(P):
    """Pasowania (4.11, 4.8) mierzone promieniami w zlozeniu: (opis, (obiekt A, punkt, kierunek promienia), (obiekt B, punkt, kierunek),
    os e, luz nominalny, regula). Luz = trafienie B . e - trafienie A . e (dodatni = szczelina, ujemny = zahaczenie zatrzasku).
    Punkt z Z = 0 przy kierunku 'Z' = pomiar pionowy: wierzch A (promien z gory) i spod B (promien z dolu) w danym (x, y)."""
    zt = P['blat_top_z']
    zp = zt + P['insert_shelf_h']            # spod plytki
    h = P['insert_opening'] / 2
    so, rs, z0 = wymiary_blatu(P)
    pc = h - P['orient_post_gap'] - P['orient_post'] / 2
    m = P['plate_size'] / 2 - P['marker_offset']
    zm = zp + P['magnet_pocket_depth'] - P['magnet_h'] / 2
    xp, yp = P['tab_pos_x'], P['tab_pin_y']
    zg = zp + P['plate_thickness'] - P['cover_groove_z']     # os rowka plytki = os garbow pokrywki
    zh = P['snap_hook_z'] + P['snap_hook_hgt'] * 0.75         # plaska czesc wystepu haczyka
    zk = zt - P['blat_t'] - P['blat_skirt_h'] / 2
    pl, wk, pk, bl, kr = 'plytka_wieczorna_n1', 'wkladka', 'pokrywka', 'blat', 'korpus_W'
    ww = P['snap_pocket_w'] / 2 + 1                           # y poza kieszenia zatrzasku
    xo = (P['window_through'] + P['panel_size']) / 4         # miedzy krawedzia okna blatu a krawedzia PCB
    x4, y4, sx4, sy4 = pozycje_podkladek(P)[3]               # proxy_dystans_4
    p4 = Vector((x4, y4, 0)) + Vector((sx4, -sy4, 0)).normalized() * (P['standoff_d'] / 2 - 0.7)
    pd = (p4.x, p4.y, 0)                                      # w podstawie dystansu, poza osia rowka w dnie
    xd, dwl = P['dc_pos_x'], P['dc_pocket_wall']
    rkol = (P['dc_bush_outer_d'] + P['dc_bush_flange_d']) / 4
    zw_b = P['floor_t'] + P['pi_standoff_h'] + P['pi_stack_h'] - P['bonnet_dc_plug_h'] / 2
    lista = [
        ('płytka w otworze wkładki (x)', (pl, (60, 20, zp + 2), '-X'), (wk, (0, 20, zp + 2), 'X'), 'X', h - P['plate_size'] / 2, 'ruchome 0,4 (R53; było 0,2–0,3)'),   # R53
        ('płytka w otworze wkładki (y, przód)', (wk, (20, 0, zp + 2), '-Y'), (pl, (20, -60, zp + 2), 'Y'), 'Y', h - P['plate_size'] / 2, 'ruchome 0,4 (R53; było 0,2–0,3)'),
        ('pokrywka na płytce (x)', (pl, (60, 20, zg - 1), '-X'), (pk, (0, 20, zg - 1), 'X'), 'X', P['cover_clearance'], 'ruchome 0,2–0,3'),
        ('garb pokrywki: zahaczenie w rowku płytki (x)', (pk, (0, 0, zg), 'X'), (pl, (60, 0, zg + 1), '-X'), '-X',
         -(P['cover_snap_bump'] - P['cover_clearance']), 'zatrzask (ujemny = zahaczenie)'),
        ('garb pokrywki: luz do dna rowka (x)', (pl, (60, 0, zg), '-X'), (pk, (0, 0, zg), 'X'), 'X',
         P['cover_groove_depth'] - P['cover_snap_bump'] + P['cover_clearance'], 'zatrzask'),
        ('kołek orientacyjny w wycięciu płytki (x)', (pl, (pc, -pc, zp + 2), '-X'), (wk, (pc, -pc, zp + 2), '-X'), 'X',
         pc - P['orient_post'] / 2 - (P['plate_size'] / 2 - P['notch_size']), 'ruchome (4.11: wycięcie 5, kołek 4,4)'),
        ('kołek orientacyjny w wycięciu płytki (y)', (wk, (pc, -pc, zp + 2), 'Y'), (pl, (pc, -pc, zp + 2), 'Y'), 'Y',
         -(P['plate_size'] / 2 - P['notch_size']) + pc - P['orient_post'] / 2, 'ruchome (4.11: wycięcie 5, kołek 4,4)'),
        ('magnes A w kieszeni płytki (x)', ('proxy_magnes_A', (-m, -m, zm), 'X'), (pl, (-m, -m, zm), 'X'), 'X',
         (P['magnet_pocket_d'] - P['magnet_d']) / 2, 'magnesy 0,1–0,2 (klejone)'),
        ('kołek wkładki w otworze blatu (x)', (wk, (xp, yp, zt - 2), 'X'), (bl, (xp, yp, zt - 2), 'X'), 'X',
         (P['blat_pin_hole_d'] - P['tab_pin_d']) / 2, 'ruchome 0,2 (R53: było wciskane 0,1–0,15)'),
        ('kołnierz blatu – ściana korpusu (x)', (bl, (so - 1, 20, zk), 'X'), (kr, (so - 1, 20, zk), 'X'), 'X',
         P['blat_skirt_clearance'], 'ruchome 0,7 = ±0,3 + ±0,3 MJF (R48/R53)'),
        ('haczyk blatu: zahaczenie w kieszeni korpusu (x)', (kr, (90, ww, zh), 'X'), (bl, (110, 0, zh), '-X'), '-X',
         -(P['snap_hook_h'] - P['blat_skirt_clearance']), 'zatrzask (ujemny = zahaczenie)'),
        ('haczyk blatu: luz do dna kieszeni (x)', (bl, (110, 0, zh), '-X'), (kr, (90, 0, zh), 'X'), 'X',
         P['blat_skirt_clearance'] + P['snap_pocket_depth'] - P['snap_hook_h'], 'zatrzask (R53: 0,5)'),
        ('haczyk blatu: luz nad występem (z)', (bl, (so + 0.8, 0, zt - P['blat_t'] - 0.6), '-Z'), (kr, (so + 0.8, 0, P['snap_pocket_z'] + 1), 'Z'), 'Z',
         P['snap_pocket_z'] + P['snap_pocket_h'] - P['snap_hook_z'] - P['snap_hook_hgt'], 'zatrzask (R53: 0,75; było R47: 0,25)'),
        ('dyfuzor w kieszeni blatu (x)', ('proxy_dyfuzor', (0, 20, zt - P['diffuser_t'] / 2), 'X'), (bl, (0, 20, zt - P['diffuser_t'] / 2), 'X'), 'X',
         (P['diffuser_pocket'] - P['diffuser_size']) / 2, 'luz 1,0 (D13)'),
        ('PCB panelu – spód blatu przy oknie (z)', ('proxy_panel', (xo, 0, 0), 'Z'), (bl, (xo, 0, 0), 'Z'), 'Z',
         P['blat_top_z'] - P['blat_t'] - P['panel_pcb_z'] - P['panel_pcb_t'], 'K‑49: ≥ 2 (R50‑1)'),
        ('wkładka na dyfuzorze (z)', ('proxy_dyfuzor', (0, 49.0, 0), 'Z'), (wk, (0, 49.0, 0), 'Z'), 'Z', 0.0, 'styk (R30)'),
        ('płytka na półce wkładki (z)', (wk, (-38, -38, 0), 'Z'), (pl, (-38, -38, 0), 'Z'), 'Z', 0.0, 'styk (D5)'),
        ('kołnierz pokrywki nad ramą wkładki (z)', (wk, (-40, -50.3, 0), 'Z'), (pk, (-40, -49.0, 0), 'Z'), 'Z',
         P['insert_shelf_h'] + P['plate_thickness'] - P['cover_skirt_below'] - P['insert_h'], 'bez styku'),
        ('Pi + Bonnet – spód elementów panelu (z)', ('proxy_pi_bonnet', (-20, 0, 0), 'Z'), ('proxy_panel', (-20, 0, 0), 'Z'), 'Z',
         P['pi_clearance_top'], 'D4/R50‑1: ≥ 8'),
        ('dystans na stadionie korpusu (z)', (kr, pd, 'Z'), ('proxy_dystans_4', pd, 'Z'), 'Z', 0.0, 'styk (R5, R50‑2)'),
        ('PCB panelu na dystansie (z)', ('proxy_dystans_4', pd, 'Z'), ('proxy_panel', pd, 'Z'), 'Z', 0.0, 'styk (R50‑7)'),
        ('tulejka DC w otworze ściany skrzynki (y)', ('tulejka_dc', (xd - dwl / 2, P['dc_pos_y'] + (P['dc_bush_inner_d'] + P['dc_bush_outer_d']) / 4, P['dc_pos_z']), 'Y'),
         (kr, (xd - dwl / 2, P['dc_pos_y'], P['dc_pos_z']), 'Y'), 'Y', (P['dc_hole_d'] - P['dc_bush_outer_d']) / 2, 'wciskane 0,075/stronę (R52, 4.8)'),
        ('tulejka DC: kołnierz na ścianie skrzynki (x)', ('tulejka_dc', (xd - dwl - P['dc_bush_flange_t'] / 2, P['dc_pos_y'] + rkol, P['dc_pos_z']), 'X'),
         (kr, (xd - dwl - P['dc_bush_flange_t'] / 2, P['dc_pos_y'] + rkol, P['dc_pos_z']), 'X'), 'X', 0.0, 'styk (R50‑3)'),
        ('wtyk DC Bonnetu (−X) – lewa ściana korpusu (x)', ('proxy_wtyk_bonnet', (P['bonnet_dc_pos_x'] - 1, P['bonnet_dc_pos_y'], zw_b), '-X'),
         (kr, (P['bonnet_dc_pos_x'] - 1, P['bonnet_dc_pos_y'], zw_b), '-X'), '-X',
         P['bonnet_dc_pos_x'] - P['bonnet_dc_plug_len'] + P['box_outer'] / 2 - P['wall_t'], 'D10/R50‑6: zapas 7,5 (tylko kierunek −X)'),
    ]
    if P['bonnet_dc_dir'].replace('−', '-') != '-X':
        lista.pop()
    return lista


def zmierz_pasowania(P, Z):
    wyn = []
    for opis, (na, pa, da), (nb, pb, db), e, nom, regula in lista_pasowan(P):
        if na not in Z or nb not in Z:
            continue
        if da == 'Z' and pa[2] == 0:
            ta = pierwsze_trafienie(Z[na].bvh, Vector((pa[0], pa[1], 1000)), Vector((0, 0, -1)))
            tb = pierwsze_trafienie(Z[nb].bvh, Vector((pb[0], pb[1], -1000)), Vector((0, 0, 1)))
        else:
            ta = pierwsze_trafienie(Z[na].bvh, Vector(pa), _os(da))
            tb = pierwsze_trafienie(Z[nb].bvh, Vector(pb), _os(db))
        luz = None if ta is None or tb is None else tb.dot(_os(e)) - ta.dot(_os(e))
        wyn.append((opis, luz, nom, regula))
    return wyn


def zapisz_arkusz_wymiarow(P, out, stl, Z, sc_param):
    uklady = {}
    for typ in TYPY_PLYTEK:
        with open(os.path.join(out, 'json', 'uklad_gniazd_%s.json' % typ), encoding='utf-8') as f:
            uklady[typ] = json.load(f)
    L = ['# Arkusz wymiarów (v%s)' % P['file_suffix'][1:], '',
         'Wygenerowany przez `ramka_generator.py`. Wszystkie wartości zmierzone promieniami na siatkach STL wczytanych z `stl/` '
         '(układy montażowe części jak w protokole 0.3) albo w złożeniu (`ramka_v2.blend`, układ D3). Nominał = wartość z `parametry.json`. '
         '„✓” = |różnica| ≤ 0,05 mm.', '', '## 1. Gabaryty i objętości (orientacja druku)', '',
         '| Plik STL | Gabaryt X × Y × Z [mm] | Objętość [cm³] |', '|---|---|---|']
    for rdzen, (obj, bb) in DZIENNIK['stl'].items():
        L.append('| `%s` | %s | %s |' % (nazwa_stl(P, rdzen), ' × '.join(liczba_pl(v, 3) for v in (bb[1] - bb[0], bb[3] - bb[2], bb[5] - bb[4])), liczba_pl(obj)))
    L += ['', '## 2. Wymiary główne części (z siatek)', '']
    odch = 0
    for rdzen, lista in lista_wymiarow(P, uklady):
        if rdzen not in stl:
            continue
        sciezka, M = stl[rdzen]
        s = Siatka(sciezka, M.inverted())
        L += ['### `%s`' % os.path.basename(sciezka), '', '| Wymiar | Metoda (punkt, oś) | Zmierzone [mm] | Nominał [mm] | Różnica |', '|---|---|---|---|---|']
        for opis, typ, p, d, nom in lista:
            v = pomiar(s.bvh, typ, p, d)
            met = {'z': 'zewn.', 'w': 'cięciwa', 'p': 'trafienie'}[typ] + ' (%g, %g, %g) %s' % (p[0], p[1], p[2], d)
            if v is None:
                odch += 1
                L.append('| %s | %s | brak trafienia | %s | ✗ |' % (opis, met, liczba_pl(nom, 3)))
            else:
                ok = abs(v - nom) <= 0.05
                odch += 0 if ok else 1
                L.append('| %s | %s | %s | %s | %s %s |' % (opis, met, liczba_pl(v, 3), liczba_pl(nom, 3), liczba_pl(v - nom, 3), '✓' if ok else '✗'))
        L.append('')
        s.zwolnij()
    L += ['## 3. Pasowania (tabela 4.11, zasady 4.8) zmierzone w złożeniu', '',
          'Luz dodatni = szczelina; ujemny = zahaczenie zatrzasku; 0 = styk. Pomiar: pierwsze trafienie promienia w każdą z dwóch części wzdłuż osi.', '',
          '| Pasowanie | Zmierzone [mm] | Nominał [mm] | Różnica | Reguła |', '|---|---|---|---|---|']
    for opis, luz, nom, regula in zmierz_pasowania(P, Z):
        if luz is None:
            odch += 1
            L.append('| %s | brak trafienia | %s | ✗ | %s |' % (opis, liczba_pl(nom, 3), regula))
        else:
            ok = abs(luz - nom) <= 0.05
            odch += 0 if ok else 1
            L.append('| %s | %s | %s | %s %s | %s |' % (opis, liczba_pl(luz, 3), liczba_pl(nom, 3), liczba_pl(luz - nom, 3), '✓' if ok else '✗', regula))
    L += ['', '## 4. Małe części druku własnego (R50‑3, R50‑8)', '',
          '- Tulejka DC: kołnierz ø%s × %s (strona kieszeni) + walec ø%s × %s, otwór ø%s; w złożeniu kołnierz na licu x = %s prawej ściany skrzynki, walec w otworze ø%s (oś y %s, Z %s wzdłuż X). Sondy K‑52b z protokołu.'
          % (liczba_pl(P['dc_bush_flange_d'], 0), liczba_pl(P['dc_bush_flange_t'], 0), liczba_pl(P['dc_bush_outer_d'], 2), liczba_pl(P['dc_bush_t'], 0),
             liczba_pl(P['dc_bush_inner_d'], 1), liczba_pl(P['dc_pos_x'] - P['dc_pocket_wall'], 0), liczba_pl(P['dc_hole_d'], 0),
             liczba_pl(P['dc_pos_y'], 0), liczba_pl(P['dc_pos_z'], 0)),
          '- Podkładki panelu: krążki ø%s z otworem ø%s, grubości %s mm (pliki %s); przy domyślnych wymiarach nieużywane — w `.blend` obok zestawu. Sondy K‑52c z protokołu.'
          % (liczba_pl(P['panel_shim_d'], 0), liczba_pl(P['panel_shim_hole_d'], 1), ' / '.join(liczba_pl(t, 1) for t in P['panel_shim_t']),
             ', '.join('`%s`' % nazwa_stl(P, r) for r, _t in rdzenie_podkladek(P))), '']
    if _UZYTE_PROPONOWANE:
        L += ['## 5. Wartości bez klucza w `parametry.json` (klucze proponowane nadzorowi)', '', '| Klucz | Przyjęta wartość | Źródło |', '|---|---|---|']
        for k in sorted(_UZYTE_PROPONOWANE):
            v, z = KLUCZE_PROPONOWANE[k]
            L.append('| `%s` | %s | %s |' % (k, json.dumps(v, ensure_ascii=False) if not isinstance(v, dict) else 'tabela (arkusz zamówienia, kolumna „Wykonanie”)', z))
        L.append('')
    with open(sc_param, encoding='utf-8') as f:
        tekst = f.read()
    L += ['## 6. Pełny zrzut `parametry.json` użytego w tym przebiegu', '', 'SHA‑256: `%s`' % sha256(sc_param), '', '```json', tekst.rstrip('\n'), '```', '']
    sc = os.path.join(out, 'arkusze', 'arkusz_wymiarow.md')
    with open(sc, 'w', encoding='utf-8') as f:
        f.write('\n'.join(L))
    return sc, odch


_ZRZUT_UWAGA = []      # R58: opis tolerancji zrzutu (K-60)


def zrzut_parametrow_zgodny(sc_wym, sc_param):
    """Zrzut parametry.json w arkusz_wymiarow.md = plik. R58: zrzut sprzed R58 jest zgodny, gdy rozni sie TYLKO brakiem kluczy KLUCZE_R58
    (pliki etapow A-C ich nie czytaja; arkusze R59 bez zmian do przebiegu ALL koordynatora) - wtedy uwaga w K-60."""
    with open(sc_wym, encoding='utf-8') as f:
        tekst = f.read()
    m = re.search(r'## 6\. Pełny zrzut[^\n]*\n.*?```json\n(.*?)\n```', tekst, re.S)
    if not m:
        return False
    with open(sc_param, encoding='utf-8') as f:
        biez = json.load(f)
    zrzut = json.loads(m.group(1))
    if zrzut == biez:
        return True
    # runda 2 (D1 recenzji): wyjatek tylko dla zrzutu, w ktorym nie ma ZADNEGO klucza R58, przy wszystkich kluczach R58 w parametry.json
    w_zrzucie = [k for s, z in zrzut.items() if not s.startswith('_') and isinstance(z, dict) for k in z if k in KLUCZE_R58]
    brak = sorted(k for s, z in biez.items() if not s.startswith('_') and isinstance(z, dict) for k in z if k in KLUCZE_R58)

    def bez_r58(d):
        return {s: ({k: v for k, v in z.items() if k not in KLUCZE_R58} if (isinstance(z, dict) and not s.startswith('_')) else z) for s, z in d.items()}
    if not w_zrzucie and set(brak) == KLUCZE_R58 and bez_r58(zrzut) == bez_r58(biez):
        _ZRZUT_UWAGA[:] = ['zrzut sprzed R58: brak %d kluczy R58 (%s), pozostałe klucze identyczne' % (len(brak), ', '.join(brak))]
        return True
    return False


# K-xx, ktore musza byc w raporcie danego etapu (K-60: raport ma wszystkie K-xx etapu); K-59 wykonuje recenzent
def k_raportu(etap):
    return {'A': ['K-01', 'K-02', 'K-03', 'K-04', 'K-04b'] + ['K-%02d' % i for i in range(5, 23)] + ['K-58', 'K-61', 'K-62', 'K-63'],
            'B': K_ETAPU['B'], 'C': ['K-52b', 'K-52c', 'K-53', 'K-57']}.get(etap, [])


def sprawdz_K60(W, P, out, etapy, wid, sc_param, liczone):
    bledy, info = [], []
    for n in ('render_rozstrzelony.png', 'render_zlozony.png', 'render_plytki.png'):
        s = os.path.join(out, 'render', n)
        if not os.path.isfile(s):
            bledy.append('brak %s' % n)
            continue
        img = bpy.data.images.load(s)
        sx, sy = img.size[0], img.size[1]
        bpy.data.images.remove(img)
        info.append('%s %d × %d' % (n, sx, sy))
        if sx < RENDER_ROZDZ[0] or sy < RENDER_ROZDZ[1]:
            bledy.append('%s %d × %d' % (n, sx, sy))
    if wid is None:
        info.append('widoczność podpisanych części: nie mierzona (rendery nie powstały w tym przebiegu)')
    else:
        niewid = [t for t, (w, n) in wid.items() if w == 0]
        info.append('podpisy %d/%d z widocznymi częściami (lista kontrolna §11; widoczne próbki: %s)'
                    % (len(wid) - len(niewid), len(PODPISY), ', '.join('%s %d/%d' % (t, w, n) for t, (w, n) in wid.items())))
        if niewid or len(wid) != len(PODPISY):
            bledy.append('niewidoczne lub brak: %s' % niewid)
    brak_k = [k for e in etapy for k in k_raportu(e) if k not in W.k]
    if brak_k:
        bledy.append('w raporcie brak %s' % brak_k)
    sc_wym = os.path.join(out, 'arkusze', 'arkusz_wymiarow.md')
    zrzut = os.path.isfile(sc_wym) and zrzut_parametrow_zgodny(sc_wym, sc_param)
    if not zrzut:
        bledy.append('arkusz_wymiarow.md bez pełnego zrzutu parametry.json')
    lic = max(d for _a, _b, d in liczone.values())
    if lic > TOL_LICZONE:
        bledy.append('LICZONE różnica %.4f' % lic)
    W.dodaj('K-60', not bledy, '%s; K‑xx etapów %s w raporcie: %s; zrzut parametry.json w arkusz_wymiarow.md: %s; LICZONE max różnica %.4f; błędy: %s'
            % ('; '.join(info), '+'.join(etapy), 'wszystkie' if not brak_k else 'brak %d' % len(brak_k),
               ('zgodny' + (' (%s)' % _ZRZUT_UWAGA[0] if _ZRZUT_UWAGA else '')) if zrzut else 'NIE', lic, '; '.join(bledy) or 'brak'),
            '3 PNG ≥ 1600 × 1200; podpisane części z §11 widoczne; raport kompletny; zrzut JSON; LICZONE zgodne', 'P')


# Lista D do v3 (G4): uwagi drobne recenzenta i nieścisłości dokumentów znalezione przez wykonawcę
DO_V3 = [
    ('recenzja A §6.1', 'Dołek kodu a rowek pokrywki: 1,3 mm materiału po przekątnej (< 1,5 z zasady 4.8), przyjęte w R47(10). Do rozważenia: dołki na x = −44,5 (1,7) albo rowek przerwany na odcinku y −38…−28 lewego boku.'),
    ('recenzja A §6.2', 'Ścianka 1,0 mm między dołkami ø2 w rozstawie 3 (głębokość 1, bez wpływu na odczyt).'),
    ('recenzja A §6.3', 'Tabela 3.1 (`code_dimple_x`) i sekcja 11 (objętość pokrywki) — poprawione w planie przez nadzór (stan obecny: −45,0 i 30 cm³).'),
    ('recenzja B §6.1', 'Odbiornik USB klawiatury (tylko P) poza testem K‑53 (korpus P odsunięty); propozycja: proxy w zestawie złożonym jako pozycja hipotetyczna albo osobna para w K‑53.'),
    ('recenzja B §6.2', 'Klucze `rama_ear_d` / `rama_ear_t` obok `rama_tab_size` — nieaktualne: rama dyfuzora i jej klucze usunięte (R50‑U1).'),
    ('recenzja B iter3 §6.1', 'Odbiornik USB (korpus P) poza zestawem K‑53; w etapie C dodany test informacyjny w położeniu hipotetycznym w zestawie W (uwaga przy K‑53 w raporcie C). Do v3: para w K‑53 w protokole.'),
    ('recenzja B iter3 §6.2', '`insert_depth_m3` 7 w `parametry.json` opisany jako nieużywany po R50 — do usunięcia w v3.'),
    ('wykonawca (B3)', 'Plan 4.4 p. 3: słupki „zrośnięte z kołnierzem 95,2…97,2” i 4.11 „wnętrze kołnierza 97,2” — po R48 kołnierz blatu leży na 95,0…97,0 (194,0 zewn.); liczby w skrypcie z `parametry.json`, STL bez zmian.'),
    ('wykonawca (B3)', '`ramka_wkladka_v2.stl`: SHA różni się między przebiegami — w B iter2 wybór przekątnej w 2 płaskich prostokątach fazy (remis BEAUTY), w B iter3 znak zera (−0,0 / +0,0) w składowych zapisanych normalnych; wierzchołki i trójkąty identyczne. Propozycja: w `stl_kanoniczny` zamiana −0,0 na +0,0 i kanoniczna przekątna w remisach (zmienia bajty wszystkich STL, także zatwierdzonych płytek — tylko z decyzją nadzoru).'),
    ('wykonawca (B3)', 'Bryła zastępcza gniazda DC bez gwintu ø8 w tulejce: średnica gwintu nie ma klucza (wynik pomiaru #16).'),
]


def zapisz_do_v3(out, W):
    L = ['# Lista drobnych (D) do v3', '', 'Wygenerowana przez `ramka_generator.py` na bramce G4 (plan, `00_PRZEPLYW_I_BRAMKI.md` §8). Nie blokuje zamówienia.', '',
         '| # | Źródło | Uwaga |', '|---|---|---|']
    i = 0
    for i, (zr, t) in enumerate(DO_V3, 1):
        L.append('| %d | %s | %s |' % (i, zr, t))
    for kid, st in sorted(W.k.items()):
        if st['waga'] == 'D' and not st['ok'] and not st['nd']:
            i += 1
            L.append('| %d | własne sprawdzenie %s | wynik NIE: %s |' % (i, kid.replace('-', '‑'), '; '.join(st['zmierzone'])))
    sc = os.path.join(out, 'do_v3.md')
    with open(sc, 'w', encoding='utf-8') as f:
        f.write('\n'.join(L) + '\n')
    return sc


def zapisz_readme(P, out, etap, iter_, pliki):
    L = ['# Ramki świetlne — pliki v%s' % P['file_suffix'][1:], '',
         'Wszystko w tym folderze generuje `ramka_generator.py` z `parametry.json` i `plan_ramki_v2.md` (R14). Plików nie edytuje się ręcznie (R28). '
         'Ostatni przebieg: %s, iteracja %d, raport `raport/raport_wykonawcy_%s_iter%d.md` (sumy SHA‑256 wszystkich plików).' % (etap if etap in ETAPY else 'etap C (%s)' % etap, iter_, etap, iter_), '',
         '## Jak uruchomić', '', 'Pełny przebieg (części, sprawdzenia, `.blend`, rendery, arkusze; kilka minut — rendery Cycles):', '', '```',
         'cd <PC>\\Desktop\\Ramki',
         '"C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe" -b -P ramka_generator.py -- --etap ALL --iter 1', '```', '',
         '- `--etap A|B|C|ALL` buduje wszystko do etapu włącznie (A: płytki kwadratowe n1–n6, płytki okrągłe n8/n9 [R57] i pokrywka; B: + wkładka, blat, korpusy W i P; C/ALL: + tulejka DC, 3 podkładki panelu, `.blend` z materiałami, rendery, arkusze, README).',
         '- `--etap SPRAWDZ --iter n` — tylko sprawdzenia K‑xx na plikach, które już są w `wyniki_v2/` (nic nie generuje poza raportem `raport_wykonawcy_SPRAWDZ_itern.md` i rzutami kontrolnymi).',
         '- Wynik w logu: linia `[ramka] RAPORT … B=0 P=0 D=0`. Kod wyjścia 1 = błąd projektu (komunikat `[ramka] BLAD: …`).',
         '- Powtarzalność (K‑59): w czystej kopii folderu (bez `wyniki_v2/`) to samo polecenie odtwarza wszystkie pliki; STL są bajtowo identyczne (kanoniczna kolejność trójkątów), '
         'z wyjątkiem `ramka_wkladka_v2.stl`: zależnie od przebiegu różni się znak zera w zapisanych normalnych albo przekątna w dwóch płaskich prostokątach fazy (te same wierzchołki, objętość i gabaryt). '
         'JSON gniazd powstaje z D6, gdy go nie ma.', '',
         '## Jak zmienić parametr (R14, R28)', '',
         '1. W `parametry.json` zmień `"value"` i ustaw `"status": "ZMIERZONE"` (pomiary: plan, sekcja 10). Nie dodawaj ani nie zmieniaj nazw kluczy — nieznany albo brakujący klucz zatrzymuje skrypt.',
         '2. Wartości `LICZONE` (`panel_pcb_z`, `blat_top_z`, `korpus_h`, `panel_standoff_l`, `cover_inner_h`, `snap_pocket_z`, `snap_hook_z`, `blat_screw_z`, '
         '`label_pos_z`, `socket_zone_r` [R54]) przelicz ze wzoru w polu `wzor` i wpisz — skrypt porównuje (różnica > 0,01 = błąd).',
         '3. Uruchom pełny przebieg (`--etap ALL`), potem recenzja. Żadnej ręcznej edycji STL.', '',
         '## Pliki (SHA‑256 z chwili zapisu README; README, `do_v3.md` i raport — w raporcie, sekcja 2)', '',
         '| Plik | Rozmiar [B] | SHA‑256 |', '|---|---|---|']
    for p in pliki:
        if os.path.isfile(p['sciezka']):
            L.append('| `%s` | %d | `%s` |' % (p['plik'], os.path.getsize(p['sciezka']), sha256(p['sciezka'])))
    L += ['', 'Dodatkowo: `raport/` (raporty wykonawcy, notatki, rzuty kontrolne), `do_v3.md` (lista drobnych).', '',
          '## Rejestr odstępstw (z raportu tego przebiegu)', '', '| # | Czego dotyczy | Co zrobiono inaczej | Dlaczego | Wymaga zatwierdzenia? |', '|---|---|---|---|---|']
    for i, (a, b, c, d) in enumerate(DZIENNIK['odstepstwa'], 1):
        L.append('| %d | %s | %s | %s | %s |' % (i, a, b, c, d))
    sc = os.path.join(out, 'README.md')
    with open(sc, 'w', encoding='utf-8') as f:
        f.write('\n'.join(L) + '\n')
    return sc


def zapisz_raport(sciezka, kontekst, W, pliki):
    k = kontekst
    L = ['# Raport wykonawcy — etap %s, iteracja %d%s' % (k['etap'], k['iter'], ' (%s)' % k['raport'] if k.get('raport') else ''), '',
         'Plik: `%s`. Wypełniony automatycznie przez `ramka_generator.py` po pełnym przebiegu. Wszystkie liczby w sekcjach 2–3 pochodzą z plików w `wyniki_v2/` (STL wczytane z powrotem), nie z kodu.' % os.path.relpath(sciezka, KATALOG).replace('\\', '/'), '',
         '## 1. Przebieg',
         '- Polecenie uruchomienia (dosłownie, z `cd`): `cd <PC>\\Desktop\\Ramki && "C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe" -b -P ramka_generator.py -- --etap %s --iter %d%s`' % (k['etap'], k['iter'], ' --raport %s' % k['raport'] if k.get('raport') else ''),
         '- Wersja Blendera (`blender --version`): %s' % k['blender'],
         '- Data: %s' % k['data'],
         '- Czas przebiegu: %.0f s; błędy/ostrzeżenia w konsoli: %s' % (k['czas'], ('; '.join(DZIENNIK['ostrzezenia'])) if DZIENNIK['ostrzezenia'] else 'brak'),
         '- Suma SHA‑256 `parametry.json` użytego w tym przebiegu: `%s`' % k['sha_param'],
         '- Suma SHA‑256 `ramka_generator.py`: `%s`' % k['sha_gen'],
         '- Wartości LICZONE (wzór z `parametry.json` → plik, różnica): %s' % '; '.join('%s %.3f → %.3f (%.4f)' % (n, a, b, d) for n, (a, b, d) in sorted(k['liczone'].items())),
         '- Plik ukladu gniazd: %s' % '; '.join(DZIENNIK['uklad']),
         '- Font: `%s` z instalacji Blendera (R22, R47); napisy:' % k['font'], '']
    L += ['| Napis | Treść | Wys. zadana [mm] | Rozmiar fontu | Pogrubienie konturu [mm] | Wys. litery H zmierzona | Trzon H zmierzony [mm] | Szerokość napisu [mm] |', '|---|---|---|---|---|---|---|---|']
    for n in DZIENNIK['napisy']:
        L.append('| %s | %s | %.2f | %.3f | %.3f | %.3f | %.3f | %.2f |' % (n['opis'], n['tresc'], n['wys_zadana'], n['rozmiar_fontu'], n['offset'], n['wys_H'], n['trzon_H'], n['szer']))
    L += ['', '## 2. Pliki wytworzone w tym etapie', '',
          '| Plik | Rozmiar [B] | SHA‑256 | Gabaryt X × Y × Z [mm] (STL) | Objętość [cm³] (STL) |', '|---|---|---|---|---|']
    for p in pliki:
        L.append('| `%s` | %d | `%s` | %s | %s |' % (p['plik'], p['rozmiar'], p['sha'], p.get('gab', '—'), p.get('obj', '—')))
    L += ['', '## 3. Wyniki sprawdzeń (protokół v2) — wszystkie K‑xx etapu', '',
          '| Id | Wynik (ZAL/NIE/N/D) | Wartość zmierzona | Oczekiwane | Uwaga |', '|---|---|---|---|---|']
    licz = {'B': 0, 'P': 0, 'D': 0}

    def klucz_k(s):
        m = re.match(r'K-(\d+)([a-z]?)', s)
        return (int(m.group(1)), m.group(2))
    for kid in sorted(W.k, key=klucz_k):
        st = W.k[kid]
        wynik = 'N/D' if st['nd'] else ('ZAL' if st['ok'] else 'NIE')
        if wynik == 'NIE':
            licz[st['waga']] += 1
        L.append('| %s (%s) | %s | %s | %s | %s |' % (kid.replace('-', '‑'), st['waga'], wynik, '<br>'.join(st['zmierzone']), st['oczekiwane'], '<br>'.join(st['uwaga'])))
    L += ['', 'Podsumowanie: B = %d, P = %d, D = %d (liczba sprawdzeń z wynikiem NIE w każdej wadze).' % (licz['B'], licz['P'], licz['D']), '',
          '## 4. Rejestr odstępstw od planu v2 (puste = brak)', '',
          '| # | Czego dotyczy (sekcja/parametr) | Co zrobiono inaczej | Dlaczego (błąd wykryty przez K‑xx / niemożność) | Wymaga zatwierdzenia na bramce? |', '|---|---|---|---|---|']
    for i, (a, b, c, d) in enumerate(DZIENNIK['odstepstwa'], 1):
        L.append('| %d | %s | %s | %s | %s |' % (i, a, b, c, d))
    L += ['', '## 5. Odpowiedź na recenzję poprzedniej iteracji (od iteracji 2)', '',
          '| Id uwagi recenzenta | Co poprawiono | Które K‑xx teraz ZAL |', '|---|---|---|']
    for w in k.get('odpowiedzi', []):
        L.append('| %s | %s | %s |' % w)
    L += ['', '## 6. Co nie zostało zrobione i dlaczego (puste = wszystko)', '']
    L += k.get('niezrobione', [])
    L += k.get('dodatek', [])           # R58: ilosci kompletu okraglego (tylko --etap R58)
    L += ['', '## Załącznik A. Wszystkie sondy (układ montażowy części)', '',
          'Metoda `w_bryle`: parzystość przecięć promienia w 3 kierunkach (+X, +Y, +Z, każdy odchylony o ~0,1° od osi, żeby nie trafiać w krawędzie siatki), wynik większościowy; „głosy” = liczba kierunków z nieparzystą liczbą przecięć. Odległość = `BVHTree.find_nearest` do siatki; < 0,1 mm oznaczone *.', '',
          '| K | Plik | Punkt (x, y, z) | Oczekiwane | Wynik | Głosy | Odl. [mm] | Zgodna |', '|---|---|---|---|---|---|---|---|']
    for kid, plik, p, ocz, w, glosy, d in W.sondy:
        L.append('| %s | %s | (%g, %g, %g) | %s | %s | %d/3 | %.3f%s | %s |' % (kid.replace('-', '‑'), plik, p[0], p[1], p[2], 'W' if ocz else 'POZA', 'W' if w else 'POZA', glosy, d, '*' if d < SONDA_BLISKO - 1e-4 else '', 'tak' if w == ocz else '**NIE**'))
    os.makedirs(os.path.dirname(sciezka), exist_ok=True)
    with open(sciezka, 'w', encoding='utf-8') as f:
        f.write('\n'.join(L) + '\n')
    return licz


# ===========================================================================
# (7) Przebieg
# ===========================================================================

def przygotuj_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    us = bpy.context.scene.unit_settings
    us.system = 'METRIC'
    us.scale_length = 0.001
    us.length_unit = 'MILLIMETERS'
    _FONT.clear()


def rdzenie_R58(P):
    """R58: rdzenie nazw plikow kompletu okraglego (z parametrow: typy TYPY_PLYTEK_R58, numery plate_numbers_round_frame, wkladka
    i pokrywka okragla)."""
    wyn = []
    for typ in TYPY_PLYTEK_R58:
        wyn.append('plytka_%s' % typ)
        wyn += ['plytka_%s_n%d' % (typ, n) for n in numery_plytek(P, typ)]
    return wyn + ['wkladka_okragla', 'pokrywka_okragla']


def wyczysc_wyniki(out, P=None):
    """Usuwa pliki generowane (STL, arkusze, rendery, .blend, README); raporty i JSON gniazd zostaja.
    R58 runda 2 (P3 recenzji): z P pomija STL kompletu okraglego (rdzenie_R58) - przebiegi A/B/C/ALL ich nie buduja, wiec nie moga ich kasowac
    (JSON ukladow i raporty i tak zostaja). Zwraca liste pominietych plikow."""
    chronione = {nazwa_stl(P, r) for r in rdzenie_R58(P)} if P is not None else set()
    pominiete = []
    for pod in ('stl', 'arkusze', 'render'):
        k = os.path.join(out, pod)
        if os.path.isdir(k):
            for f in os.listdir(k):
                p = os.path.join(k, f)
                if os.path.isfile(p):
                    if pod == 'stl' and f in chronione:
                        pominiete.append(f)
                        continue
                    os.remove(p)
    for f in ('ramka_v2.blend', 'ramka_v2.blend1', 'README.md', 'do_v3.md'):
        p = os.path.join(out, f)
        if os.path.isfile(p):
            os.remove(p)
    return pominiete


def nazwa_stl(P, rdzen):
    return 'ramka_%s_%s.stl' % (rdzen, P['file_suffix'])


def sciezka_stl_istniejaca(P, kat_stl, rdzen):
    """--etap SPRAWDZ: sciezka STL, ktory musi juz istniec."""
    s = os.path.join(kat_stl, nazwa_stl(P, rdzen))
    if not os.path.isfile(s):
        raise BladProjektu('SPRAWDZ: brak pliku %s' % s)
    return s


def etap_A(P, out, W, iter_, buduj=True):
    """Plytki bazowe + 6 wariantow kwadratowych + okragle (bazowe + n8/n9, R57), pokrywka, JSON gniazd, kody_plytek.md,
    sprawdzenia K-01..K-22, K-58, K-61..K-63.
    iter_: znacznik w nazwach rzutow ('iter2', 'SPRAWDZ_iter1'); buduj=False: tylko sprawdzenia istniejacych plikow."""
    kat_stl = os.path.join(out, 'stl')
    kat_rz = os.path.join(out, 'raport', 'rzuty')
    os.makedirs(kat_stl, exist_ok=True)
    pliki = []
    uklady = {}
    for typ in TYPY_PLYTEK:          # R57: + okragla_wieczorna, okragla_poranna
        uklady[typ], sciezka_json = wczytaj_uklad(P, typ, os.path.join(out, 'json'), zapisuj=buduj)
        pliki.append({'plik': os.path.relpath(sciezka_json, out).replace('\\', '/'), 'sciezka': sciezka_json})
    # budowa i eksport
    czesci = []   # (rdzen, typ czesci, numer, uklad)
    for typ in TYPY_PLYTEK:
        czesci.append(('plytka_%s' % typ, 'plytka_%s' % typ, None, uklady[typ]))
        for n in numery_plytek(P, typ):
            czesci.append(('plytka_%s_n%d' % (typ, n), 'plytka_%s' % typ, n, uklady[typ]))
    czesci.append(('pokrywka', 'pokrywka', None, None))
    eksport = []
    for rdzen, rodzaj, numer, uklad in czesci:
        M = M_druk(P, rodzaj)
        if buduj:
            if rodzaj == 'pokrywka':
                ob = zbuduj_pokrywke(P, rdzen)
            else:
                ob = zbuduj_plytke(P, uklad, numer, rdzen)
            sciezka = os.path.join(kat_stl, nazwa_stl(P, rdzen))
            eksportuj_stl(ob, sciezka, M)
            usun_obiekt(ob)
        else:
            sciezka = sciezka_stl_istniejaca(P, kat_stl, rdzen)
        eksport.append((rdzen, rodzaj, numer, uklad, sciezka, M))
    # sprawdzenia na STL
    for typ in TYPY_PLYTEK:
        sprawdz_uklad_json(W, P, uklady[typ], typ, uklady[typ_bazowy(typ)] if plytka_okragla(typ) else None)
        sprawdz_scianki_naroznikow(W, P, uklady[typ], typ)
    k11 = {}
    S = P['plate_size']
    for rdzen, rodzaj, numer, uklad, sciezka, M in eksport:
        plik = os.path.basename(sciezka)
        siatka = Siatka(sciezka, M.inverted())
        if rodzaj == 'pokrywka':
            wew, zew, wys = wymiary_pokrywki(P)       # bez reliefu GORA (R50-U14): gabaryt 99,6 x 99,6 x 20,0
            obj, gab = ogolne_stl(W, plik, siatka, (zew, zew, wys), (-zew / 2, zew / 2, -zew / 2, zew / 2, -wys, 0.0), 'pokrywka')
            sprawdz_pokrywke(W, P, siatka, plik, kat_rz, iter_)
            ref = OBJ_ORIENT['pokrywka']
            if not (0.7 * ref <= obj <= 1.3 * ref):
                # rachunek z wymiarow planu 4.2 (bez zaokraglen, otworow, garbow i napisu)
                nominal = (zew ** 2 * P['cover_top_t'] + (zew ** 2 - wew ** 2) * (wys - P['cover_top_t'])) / 1000.0
                DZIENNIK['odstepstwa'].append((
                    'protokół, tabela 1 (K‑04b) / plan 4.2 i sekcja 11: objętość pokrywki', 'brak zmian geometrii; K‑04b pokrywki = NIE',
                    'objętość z STL %.2f cm³; rachunek z wymiarów 4.2: %.1f² × %.1f + (%.1f² − %.1f²) × %.1f = %.1f cm³ — wartość orientacyjna 22 cm³ w tabeli 1 (i 22 w sekcji 11) jest za niska; geometria zgodna z planem (K‑17…K‑22 ZAL)'
                    % (obj, zew, P['cover_top_t'], zew, wew, wys - P['cover_top_t'], nominal),
                    'tak — poprawić tabelę 1 protokołu na ~%.0f cm³ (i sekcję 11 planu)' % nominal))
        else:
            T = P['plate_thickness']
            rel = P['number_relief_h'] if (numer is not None and uklad['number_relief'] is not None) else 0.0
            B = uklad['d'] if uklad.get('shape') == 'round' else S       # R57: okragla — gabaryt = srednica (sciecie nie siega osi X/Y)
            obj, gab = ogolne_stl(W, plik, siatka, (B, B, T + rel), (-B / 2, B / 2, -B / 2, B / 2, -T, rel), rodzaj)
            sprawdz_plytke(W, P, siatka, plik, uklad, numer)
            if numer is not None:
                obecne = [dl['bit'] for dl in uklad['code_dimples'] if not siatka.w_bryle((dl['x'], dl['y'], -0.5))[0]]
                k11[numer] = '+'.join(obecne)
                if uklad['number_relief'] is not None:
                    rzut_cyfry(P, siatka, plik, kat_rz, iter_, uklad['number_relief'])
        bb = siatka.bbox_stl
        DZIENNIK['stl'][rdzen] = (obj, bb)
        pliki.append({'plik': os.path.relpath(sciezka, out).replace('\\', '/'), 'sciezka': sciezka,
                      'gab': '%.3f × %.3f × %.3f' % (bb[1] - bb[0], bb[3] - bb[2], bb[5] - bb[4]),
                      'obj': '%.2f' % obj})
        siatka.zwolnij()
    # kody plytek
    kat_ark = os.path.join(out, 'arkusze')
    os.makedirs(kat_ark, exist_ok=True)
    sc_kody = os.path.join(kat_ark, 'kody_plytek.md')
    nazwy = {}
    for typ in TYPY_PLYTEK:
        for n in numery_plytek(P, typ):
            if n in nazwy:
                raise BladProjektu('numer plytki n%d uzyty dwa razy' % n)
            nazwy[n] = nazwa_stl(P, 'plytka_%s_n%d' % (typ, n))
    if buduj:
        zapisz_kody_plytek(P, sc_kody, nazwy, uklady)
    elif not os.path.isfile(sc_kody):
        raise BladProjektu('SPRAWDZ: brak pliku %s' % sc_kody)
    sprawdz_kody(W, P, sc_kody, k11)
    pliki.append({'plik': 'arkusze/kody_plytek.md', 'sciezka': sc_kody})
    stl = {rdzen: (sciezka, M) for rdzen, _r, _n, _u, sciezka, M in eksport}
    return pliki, stl


def wpis_pliku(sciezka, out, siatka=None, obj=None):
    p = {'plik': os.path.relpath(sciezka, out).replace('\\', '/'), 'sciezka': sciezka}
    if siatka is not None:
        bb = siatka.bbox_stl
        p['gab'] = '%.3f × %.3f × %.3f' % (bb[1] - bb[0], bb[3] - bb[2], bb[5] - bb[4])
        p['obj'] = '%.2f' % obj
    return p


def etap_B(P, out, W, iter_, stl, buduj=True):
    """Wkladka, blat, korpus W i P (rama dyfuzora usunieta, R50-U1); K-01..K-04b, K-23..K-47, K-43
    (zlozenie i K-33, K-44b, K-49, K-53...K-56: main)."""
    kat_stl = os.path.join(out, 'stl')
    kat_rz = os.path.join(out, 'raport', 'rzuty')
    pliki = []
    czesci = [('wkladka', 'wkladka', lambda n: zbuduj_wkladke(P, n)),
              ('blat', 'blat', lambda n: zbuduj_blat(P, n)),
              ('korpus_W', 'korpus', lambda n: zbuduj_korpus(P, P['label_text_W'], n)),
              ('korpus_P', 'korpus', lambda n: zbuduj_korpus(P, P['label_text_P'], n))]
    for rdzen, rodzaj, fn in czesci:
        M = M_druk(P, rodzaj)
        if buduj:
            ob = fn(rdzen)
            sciezka = os.path.join(kat_stl, nazwa_stl(P, rdzen))
            eksportuj_stl(ob, sciezka, M)
            usun_obiekt(ob)
        else:
            sciezka = sciezka_stl_istniejaca(P, kat_stl, rdzen)
        stl[rdzen] = (sciezka, M)
    B = P['box_outer']
    so, rs, z0 = wymiary_blatu(P)
    zakresy = {
        'wkladka': (-(P['tab_pos_x'] + P['tab_w'] / 2), P['tab_pos_x'] + P['tab_w'] / 2, -(P['insert_opening'] / 2 + P['insert_wall_w']),
                    P['tab_end_y'], -P['tab_pin_h'], P['insert_shelf_h'] + P['orient_post_h']),
        'blat': (-B / 2, B / 2, -B / 2, B / 2, z0, 0.0),
        'korpus': (-B / 2, B / 2, -B / 2 - P['label_relief_h'], B / 2, 0.0, P['korpus_h']),      # bez daszkow (R50-U4)
    }
    korpusy = {}
    for rdzen, rodzaj, _fn in czesci:
        sciezka, M = stl[rdzen]
        plik = os.path.basename(sciezka)
        siatka = Siatka(sciezka, M.inverted())
        z = zakresy[rodzaj]
        obj, gab = ogolne_stl(W, plik, siatka, (z[1] - z[0], z[3] - z[2], z[5] - z[4]), z, rodzaj)
        if rodzaj == 'wkladka':
            sprawdz_wkladke(W, P, siatka, plik, kat_rz, iter_)
        elif rodzaj == 'blat':
            sprawdz_blat(W, P, siatka, plik)
        else:
            sprawdz_korpus(W, P, siatka, plik)
        pliki.append(wpis_pliku(sciezka, out, siatka, obj))
        DZIENNIK['stl'][rdzen] = (obj, siatka.bbox_stl)
        if rodzaj == 'korpus':
            korpusy[rdzen[-1]] = (siatka, plik, sha256(sciezka), obj)
        else:
            siatka.zwolnij()
    os.makedirs(kat_rz, exist_ok=True)
    napis_korpusu(W, P, korpusy, kat_rz, iter_)
    for s in korpusy.values():
        s[0].zwolnij()
    W.nd('K-48', '—', 'B', 'uchylone R50‑U1 (rama dyfuzora usunięta; plik nie powstaje)')
    return pliki


def odstepstwa_informacyjne_B(P):
    """Odstepstwa przyjete przez wlasciciela informacyjnie (raport B iter1 #3, #4; R51)."""
    DZIENNIK['odstepstwa'].append((
        'R47 / bryła zastępcza gniazda DC: grubość nakrętki', 'grubość nakrętki = `dc_pocket_wall` (%.1f)' % P['dc_pocket_wall'],
        'plan podaje „nakrętka ø15 × 2”, grubość bez własnego klucza; wartość liczbowo równa', 'nie — przyjęte informacyjnie (R51)'))
    DZIENNIK['odstepstwa'].append((
        'bryła zastępcza `proxy_odbiornik_usb` (tylko korpus P)', 'położenie przyjęte: wystaje %.0f mm w +X od krawędzi portów Pi (x = %.0f), oś y = %.0f, Z %.0f…%.0f'
        % (P['receiver_l'], P['pi_pos_x'] + P['pi_l'], P['pi_pos_y'] + P['pi_w'] / 2, P['floor_t'] + P['pi_standoff_h'], P['floor_t'] + P['pi_standoff_h'] + P['receiver_h']),
        'plan mówi tylko „dolny port USB Pi”; pozycji portu nie ma w parametrach', 'nie — przyjęte informacyjnie (R51)'))


def odstepstwa_informacyjne_R57(P):
    """R57 (plytki okragle): zalozenia wykonawcy do zatwierdzenia przez wlasciciela / nadzor (rejestr odstepstw)."""
    D = DZIENNIK['odstepstwa']
    R, dist, kat, w = sciecie_okraglej(P)
    dk, nc = P['code_dimples_round'], P['number_pos_round']      # R59: pozycje w tekstach z parametry.json (nie stale)
    D.append(('R57 / `plate_round_d` (zadanie: 96; decyzja nadzoru 2.11: 100)', 'płytka okrągła ø%g = granica pola skanowania; gniazda jak płytka kwadratowa tego typu, w kole 47' % (2 * R),
              'decyzja 2.11 na układzie R54: przy ø96 ścianka obrys górny rynienki tylnej porannej (r 46,93) i stożków znaczników (r 44,43 + 2,5) do krawędzi = 1,07 (do początku fazy 0,57) < 1,5 (reguła 4.8, K‑16); '
              'ø98 dawało 1,57–2,07; przy ø100 ścianka do krawędzi 2,57; po R59 (jedna rynienka przednia, układ W‑b / P‑e) ścianki do krawędzi są większe — liczby w K‑16 tego raportu; kwadrat ma rogi na promieniu 67,9, więc ø100 mieści się w skanerze wszędzie tam, gdzie kwadrat',
              'tak — właściciel (ZAŁOŻENIE nadzoru)'))
    D.append(('R57 / `round_flat_w` (zadanie: 8; decyzja nadzoru 2.11: 16)', 'ścięcie o cięciwie %g: płaszczyzna %.3f od środka, głębokość %.3f' % (w, dist, R - dist),
              'cięciwa 8 dawała głębokość 0,16 (mniej niż faza 0,5 i tolerancja ±0,3 — niewidoczne); 16 daje %.2f ≥ `round_flat_depth_min` %g przy ściance od płaszczyzny ścięcia do obrysów ≥ 3 (K‑61 e, f; liczba po R59 w K‑61 tego raportu); w decyzji 2.11 (układ R54) 20 odpadało (ścianka 1,3)' % (R - dist, P['round_flat_depth_min']),
              'tak — właściciel (ZAŁOŻENIE nadzoru)'))
    D.append(('R57 / `code_dimples_round` (zadanie: wzdłuż lewej krawędzi; nadzór 2.11: zaakceptowane per typ)', 'pozycje per typ z `parametry.json`: wieczorna %s; poranna %s' % tuple(', '.join('%s (%g, %g)' % (b, dk[tb][b][0], dk[tb][b][1]) for b in BITY) for tb in ('wieczorna', 'poranna')),
              'R57 (układ R54): przegląd siatki 0,5 mm — żadna linia 4 dołków o rozstawie 3 nie mieściła się w kole r 44 wspólnie dla obu układów gniazd ani przy lewej krawędzi (gniazda sięgają x −45); '
              'R59: wieczorna bez zmian (rząd przed rynienką przednią); poranna przeniesiona z kolumny x 30,5 (y −31…−22) — rynienka układu P‑e leży w y −35,3 i rząd przed nią się nie mieści, więc dwie pary z prawej strony '
              '(policzone `narzedzia/uklad_kolo_R59.js`); promienie i ścianki do gniazd, stożków i krawędzi: K‑62 tego raportu; program czyta pozycje z JSON `code_dimples`',
              'nie — ZAŁOŻENIE zaakceptowane przez nadzór 2.11; pozycje porannej zmienione decyzją właściciela G0 14.11.2026 (R59, wariant P‑e)'))
    D.append(('R57 / `number_pos_round` (nadzór 2.11: zaakceptowane)', 'cyfra reliefu na okrągłych w kole 47 (z `parametry.json`): wieczorna %s, poranna %s' % tuple('bez cyfry (null)' if nc[tb] is None else '(%g, %g)' % (nc[tb][0], nc[tb][1]) for tb in ('wieczorna', 'poranna')),
              'dawne miejsce kwadratu (39,5, −44,5) leży poza kołem (promień 59,6); obrys cyfry 5 × 3,6 w kole 47 i ≥ 3 od gniazd; R59: wieczorna bez zmian, poranna przeniesiona z (36,5, −24,5) na lewą stronę '
              '(dawne miejsce koliduje z gniazdem ø12,5 układu P‑e w (31; −19,55)); odstępy obrysu cyfry od gniazd, dołków, stożków i koła 47 liczy `narzedzia/weryfikuj_uklad_R59.js` (generator sprawdza tylko wysokość reliefu, K‑13)',
              'nie — ZAŁOŻENIE zaakceptowane przez nadzór 2.11; pozycja porannej zmieniona decyzją właściciela G0 14.11.2026 (R59, wariant P‑e); `null` = bez cyfry'))
    D.append(('R57 / K‑08 na okrągłych', 'sonda zaokrąglonego końca rynienki na 45° od środka półokręgu (w/2 + 0,6) zamiast narożnika prostokąta',
              'R57: sonda wprowadzona przy ø96/98, gdy narożnik (x + l/2 − 0,5, y + w/2 − 0,5) rynienek tylnych układu R54 (promień 48,5–48,6) leżał poza obrysem; przy ø100 narożnik leży w płytce (recenzja R57‑B D1, zapis w protokole K‑08), a po R59 rynienka jest tylko z przodu (narożnik w promieniu 37,5 / 38,2); '
              'protokół K‑08 wymienia dla płytek okrągłych obie sondy, generator wykonuje na nich nadal tylko sondę na 45° (kod sprawdzeń bez zmian w R59); rozróżnia ona koniec prostokątny od zaokrąglonego tak samo',
              'nie — informacyjnie (zapis w protokole K‑08)'))
    D.append(('R57 / pliki bazowe kwadratowe (`ramka_plytka_wieczorna_v2.stl`, `ramka_plytka_poranna_v2.stl`)', 'plik bazowy = wszystkie 4 dołki (A+B+C+D), więc bazowe kwadratowe dostały dołek D (−45, −27) i zmieniły bajty',
              'zasada „bazowy = wszystkie dołki” (4.1 p. 5, K‑11) rozszerzona o bit D; pliki bazowe nie są drukowane ani w pakiecie; n1–n6 bez bitu D (w R57 bajtowo identyczne z R56; po R59 wszystkie pliki płytek mają nowy układ gniazd i nowe SHA)',
              'tak — albo bazowe bez D (wtedy K‑11 bazowy A+B+C)'))
    D.append(('R57 / boolean i triangulacja płytek okrągłych', 'otwory ø3 cięte w drugiej różnicy; ściany poziome triangulowane Delaunayem z ograniczeniami (CDT)',
              'jedna różnica ze wszystkimi bryłami zostawiała w bazowej okrągłej wieczornej 3 zbędne ściany na dnie otworów (K‑03: 514 przecięć); kwadratowe bez zmian w kolejności brył i triangulacji (w R57 SHA płytek kwadratowych = R56; po R59 nowe SHA wynikają tylko z nowego układu gniazd)',
              'nie — informacyjnie'))


def odstepstwa_informacyjne_R59(P):
    """R59 (nowy uklad gniazd, decyzja wlasciciela G0 14.11.2026): wpis informacyjny rejestru - liczby gniazd z ev_rows / mo_rows
    i regula numeracji id w rzedach mieszanych (dwa wpisy o roznym y)."""
    def opis(rows):
        licz = {}
        for w in rows:
            klucz = ('ø%s' % liczba_pl(w['d'], 1).replace(',0', '')) if w['type'] == 'round' else 'rynienka %g × %g' % (w['l'], w['w'])
            licz[klucz] = licz.get(klucz, 0) + len(w['x'])
        return ' + '.join('%d × %s' % (n, k) for k, n in licz.items())
    DZIENNIK['odstepstwa'].append((
        'R59 / `ev_rows`, `mo_rows` (decyzja właściciela G0 14.11.2026: warianty W‑b i P‑e)',
        'układ gniazd z `parametry.json`: wieczorna %s; poranna %s; na każdej płytce jedna rynienka (przednia)' % (opis(P['ev_rows']), opis(P['mo_rows'])),
        'rząd mieszany płytki porannej (ø12,5 i ø15 obok siebie) jest zapisany jako dwa wpisy o różnym y; numery id (R13: rzędami od przodu, w rzędzie od prawej) idą wtedy po y wpisu — '
        'najpierw gniazda wpisu o mniejszym y, potem drugiego; id całego układu są inne niż w R54 (wyniki programu ze starego układu nie są porównywalne po numerze gniazda)',
        'nie — informacyjnie (plan D6 i Z20 [R59])'))


def odstepstwa_informacyjne_C(P):
    """Interpretacje i nieścisłości zauważone w etapie C (rejestr odstępstw, informacyjnie lub do decyzji nadzoru)."""
    D = DZIENNIK['odstepstwa']
    D.append(('protokół K‑57 / arkusz zamówienia: wzór kosztu pokazowego',
              'najtańszy = obj × szt × `cost_rate_min`…`cost_rate_max`; pokazowy = najtańszy × `cost_dye_factor` × `cost_smooth_factor` dla korpusu i blatu (Z19), części białe bez mnożników',
              'opis K‑57 („koszt_max … × dye dla grafitu × smooth dla korpusu/blatu”) jest niejednoznaczny; przyjęto wzór z planu 12.1 i sekcji 11, zapisany pod tabelą arkusza',
              'nie — informacyjnie'))
    D.append(('render rozstrzelony (prompt: rozsunięcie wzdłuż Z)', 'gniazda DC i USB oraz tulejka wysunięte w lewo ekranu (%d mm) przy Z korpusu' % WYSUNIECIE_WNETRZA,
              'w izometrii części wewnątrz korpusu zasłaniają ściany i warstwy wyżej; lista §11 wymaga ich widoczności (K‑60 mierzy widoczność)',
              'nie — informacyjnie'))
    D.append(('bryła zastępcza gniazda DC z tulejką (K‑53)', 'bez gwintu ø8 w otworze tulejki', 'średnica gwintu gniazda nie ma klucza (wynik pomiaru #16)',
              'nie — informacyjnie (do_v3)'))
    D.append(('plan 4.4 p. 3 i 4.11 (opis)', 'kołnierz blatu na 95,0…97,0 (z `parametry.json`, R48)', 'tekst planu: „zrośnięte z kołnierzem 95,2…97,2”, „wnętrze kołnierza 97,2” — opis sprzed R48; STL bez wpływu',
              'nie — do poprawy opisu w planie (do_v3)'))
    D.append(('K‑59 / `ramka_wkladka_v2.stl`', 'brak zmian; SHA wkładki może się różnić między przebiegami',
              'różnica tylko w znaku zera (−0,0 / +0,0) zapisanych normalnych (wierzchołki i trójkąty identyczne); normalizacja w `stl_kanoniczny` zmieniłaby bajty wszystkich STL, także zatwierdzonych płytek',
              'nie — rozstrzygnięte przez nadzór po C iter1 (K‑59 kanonicznie; normalizacja w v3, `do_v3.md` #9)'))
    D.append(('protokół K‑52b, plan 4.x (tulejka DC) — opis', 'walec ø%s z `parametry.json` (R52: `dc_hole_d` − 0,15, luz %s/stronę w otworze ø%s, reguła 4.8 „wciskane”)'
              % (liczba_pl(P['dc_bush_outer_d'], 2), liczba_pl((P['dc_hole_d'] - P['dc_bush_outer_d']) / 2, 3), liczba_pl(P['dc_hole_d'], 0)),
              'tekst K‑52b („walec ø12 × 2”, „walec r 6”) i opis pliku w planie („walec ø`dc_bush_outer_d` 12”) sprzed R52; sondy K‑52b (r 5,5 W, r 6,8 POZA) bez zmian; '
              'w złożeniu walec nie przenika ściany (luz geometryczny 0,075/stronę, K‑53 bez przecięcia)',
              'nie — do poprawy opisu w protokole i planie'))


# Sprawdzenia etapow B i C (K-xx z wynikiem NIE trafiaja do rejestru odstepstw: geometria bez zmian, decyzja wlasciciela)
K_ETAPU = {
    'B': ['K-23', 'K-24', 'K-25', 'K-27', 'K-28', 'K-29', 'K-30', 'K-31', 'K-32', 'K-33', 'K-34', 'K-35', 'K-36', 'K-37', 'K-38',
          'K-39', 'K-40', 'K-42', 'K-43', 'K-44', 'K-44b', 'K-45', 'K-46', 'K-47', 'K-49', 'K-53', 'K-54', 'K-55', 'K-56'],
    'C': ['K-52b', 'K-52c', 'K-57', 'K-60'],
}


def wyniki_nie_do_rejestru(W, etapy):
    for e in etapy:
        for kid in K_ETAPU.get(e, []):
            if kid in W.k and not W.k[kid]['ok'] and not W.k[kid]['nd']:
                DZIENNIK['odstepstwa'].append((kid.replace('-', '‑'), 'brak zmian geometrii; wynik NIE',
                                               'szczegóły w sekcji 3 i w Załączniku A', 'tak'))


def etap_C(P, out, W, iter_, stl, buduj=True):
    """Male czesci druku wlasnego (R50-3, R50-8): tulejka DC i 3 podkladki panelu; K-01..K-04b, K-52b, K-52c
    (tulejka w zlozeniu: zbuduj_zlozenie, K-53)."""
    kat_stl = os.path.join(out, 'stl')
    czesci = [('tulejka_dc', 'tulejka_dc', None, lambda n: zbuduj_tulejke_dc(P, n))]
    czesci += [(r, r, t, (lambda n, t=t: zbuduj_podkladke(P, t, n))) for r, t in rdzenie_podkladek(P)]
    pliki = []
    for rdzen, rodzaj, t, fn in czesci:
        M = M_druk(P, rodzaj)
        if buduj:
            ob = fn(rdzen)
            sciezka = os.path.join(kat_stl, nazwa_stl(P, rdzen))
            eksportuj_stl(ob, sciezka, M)
            usun_obiekt(ob)
        else:
            sciezka = sciezka_stl_istniejaca(P, kat_stl, rdzen)
        stl[rdzen] = (sciezka, M)
        plik = os.path.basename(sciezka)
        siatka = Siatka(sciezka, M.inverted())
        if t is None:
            rf, h = P['dc_bush_flange_d'] / 2, P['dc_bush_flange_t'] + P['dc_bush_t']
            obj, gab = ogolne_stl(W, plik, siatka, (2 * rf, 2 * rf, h), (-rf, rf, -rf, rf, 0.0, h), rdzen)
            sprawdz_tulejke(W, P, siatka, plik)
        else:
            rs = P['panel_shim_d'] / 2
            obj, gab = ogolne_stl(W, plik, siatka, (2 * rs, 2 * rs, t), (-rs, rs, -rs, rs, 0.0, t), rdzen)
            sprawdz_podkladke(W, P, siatka, plik, t)
        DZIENNIK['stl'][rdzen] = (obj, siatka.bbox_stl)
        pliki.append(wpis_pliku(sciezka, out, siatka, obj))
        siatka.zwolnij()
    W.nd('K-52', '—', 'P', 'uchylone R50‑U8 (uchwyt kabli usunięty); w zamian K‑52b, K‑52c')
    return pliki


def rzut_konturow_png(petle, sciezka, krok):
    """Rzut napisu (kontury 2D, regula niezerowego nawiniecia) do PNG: bialy = material."""
    xs = [x for p in petle for x, _ in p]
    ys = [y for p in petle for _, y in p]
    x0, y0 = min(xs) - 0.3, min(ys) - 0.3
    nx, ny = int((max(xs) + 0.3 - x0) / krok) + 1, int((max(ys) + 0.3 - y0) / krok) + 1
    mapa = []
    for j in range(ny):
        y = y0 + j * krok
        prz = _przedzialy_wnetrza(petle, y)
        mapa.append([1.0 if any(a <= x0 + i * krok <= b for a, b in prz) else 0.0 for i in range(nx)])
    zapisz_png(sciezka, mapa, 0.0, 1.0)


# Sekcja 5 raportu: odpowiedzi na uwagi / decyzje wlasciciela z poprzedniej iteracji (etap, iteracja) -> wiersze
ODPOWIEDZI = {
    ('B', 2): [
        ('#6 raportu B iter1 (K‑56), R51 (3)', 'nasada ucha wkładki w kształcie L: x ±(tab_root_x_in…tab_root_x_out) w obrysie ramy od y tab_root_y0, '
         'x ±(tab_root_x_out…ucho) dopiero od tylnej krawędzi ramy; kanał kablowy: w dnie ścianki tylnej przy rowku, łącznik przy x = ±44, '
         'pod nasadą w połowie jej części tylnej do x = ±65, pod uchem wzdłuż x = ±64', 'K‑56, K‑29 (nowe sondy R51)'),
        ('#1 raportu B iter1 (PRZÓD), R51 (1)', 'bez napisu (`insert_label_h` = 0); strzałki ▼ 2 × 3 na obu segmentach (±32, −51,15)', 'K‑31 (sprawdza strzałki)'),
        ('#2 raportu B iter1 (żebra), R51 (2)', 'początek żebra z klucza `rib_start_r` (4,5); dopisany do walidatora', 'K‑44'),
        ('#5 raportu B iter1 (otwór słupka), R49a', 'otwór ø2,5 × `blat_post_hole_depth` 6 od lica 97,0 do 91,0, dno 1,8 — zatwierdzone; klucz dopisany do walidatora', 'K‑47'),
        ('#3, #4 raportu B iter1', 'przyjęte informacyjnie; wpisy zostają w rejestrze z adnotacją R51', '—'),
        ('`tab_root_x_out` (R51)', 'nowy klucz dopisany do walidatora; skrypt sprawdza, że nie wystaje poza obrys ramy', '—'),
    ],
    ('B', 3): [
        ('recenzja B iter2: ZALICZONY (G3), brak uwag B/P/D do poprawy', 'brak uwag w B iter2; zmiany z R50 (polecenie nadzoru „R50 WPISANE”, iteracja B3): '
         'walidator −49/+21 kluczy i 4 nowe LICZONE; korpus 59,6 ze stadionami i rowkami, bez daszków, żeber, SD, gniazd stopek, bossów uchwytów, '
         'kieszeń DC do lewej ściany z gniazdem w prawej ścianie skrzynki osią X, USB 16 × 9 + rowki; blat bez bossów ramy, naroża ostre; '
         'wkładka: naroża ostre, rowek 2,5 × 1,5 z przelotem; pokrywka bez otworów i GÓRA; rama dyfuzora i uchwyt kabli usunięte z kodu', 'wszystkie K‑xx etapów A i B'),
        ('uwagi D recenzenta B iter2 (§6.1, §6.2)', 'na listę do v3 (`do_v3.md` w etapie C); #2 (`rama_ear_d`) nieaktualne po R50‑U1', '—'),
        ('polecenie nadzoru po G3: sonda K‑47', '(75, 89,6, −8,6) z protokołu + (75, 90,5, −8,6) jako druga (protokół po R50 wymaga obu)', 'K‑47'),
        ('polecenie nadzoru po G3: komentarze R49', 'komentarze o wkładkach M3/M2,5 zastąpione opisem otworów pod wkręty formujące gwint; geometria bez zmian', '—'),
    ],
    ('C', 1): [
        ('recenzja B iter3: ZALICZONY (G3′), uwag B/P brak', 'D §6.1: test informacyjny odbiornika USB w położeniu hipotetycznym w zestawie W (uwaga przy K‑53); '
         'D §6.1 i §6.2 wpisane do `do_v3.md`', 'K‑53 (uwaga)'),
        ('etap C po R50 (polecenie „R50 WPISANE”, pkt 6)', 'bez uchwytu kabli i ramy dyfuzora; tulejka DC i 3 podkładki panelu (K‑52b, K‑52c); tulejka w zestawie złożonym (K‑53); '
         'arkusz zamówienia 15 wierszy, koszt tylko „PA12 drukarnia”, druk własny w osobnym bloku; rendery i lista podpisów wg protokołu §11 po R50', 'K‑52b, K‑52c, K‑53, K‑57, K‑60'),
    ],
    ('C', 2): [
        ('recenzja C iter1: ZALICZONY (G4), uwag B/P brak; trzecie oko G4b: 0 blokujących', 'D §6.1 (SHA wkładki) i §6.2 (SHA `.blend`/renderów) — na listę v3 (`do_v3.md` #9); '
         'rejestr #7 rozstrzygnięty przez nadzór (K‑59 kanonicznie)', 'K‑59 (uwaga)'),
        ('R52 / trzecie oko U1: `dc_bush_outer_d` 12 → 11,85', 'tulejka DC przebudowana z `parametry.json`; walec ø11,85 w otworze ø12 (luz 0,075/stronę, „wciskane” wg 4.8); '
         'K‑52b mierzy średnice walca, otworu i kołnierza z 4 promieni; w złożeniu tulejka w położeniu montażowym (bez przecięcia, styk kołnierza z licem ściany)', 'K‑52b, K‑53'),
        ('R52: pozostałe pozycje (opisy 4.11, 9, 5/10)', 'tylko tekst planu; STL i parametry bez zmian', '—'),
    ],
}

ETAPY = {'A': ['A'], 'B': ['A', 'B'], 'C': ['A', 'B', 'C'], 'ALL': ['A', 'B', 'C']}
RDZENIE_ETAPU = {'A': ['plytka_%s' % t for t in TYPY_PLYTEK] + ['pokrywka'],
                 'B': ['wkladka', 'blat', 'korpus_W', 'korpus_P'], 'C': ['tulejka_dc', 'podkladka_panelu_05', 'podkladka_panelu_1', 'podkladka_panelu_2']}


def etapy_istniejace(P, out):
    """--etap SPRAWDZ: etapy, ktorych wszystkie STL sa w out/stl (kolejno A, B, C); niepelny etap = blad."""
    wyn = []
    for e in ('A', 'B', 'C'):
        rdz = list(RDZENIE_ETAPU[e])
        if e == 'A':
            rdz += ['plytka_%s_n%d' % (t, n) for t in TYPY_PLYTEK for n in numery_plytek(P, t)]
        jest = [os.path.isfile(os.path.join(out, 'stl', nazwa_stl(P, r))) for r in rdz]
        if all(jest):
            wyn.append(e)
        elif any(jest):
            raise BladProjektu('SPRAWDZ: niepełny etap %s, brak %s' % (e, [r for r, j in zip(rdz, jest) if not j]))
        else:
            break
    if not wyn:
        raise BladProjektu('SPRAWDZ: brak plików STL w %s' % os.path.join(out, 'stl'))
    return wyn


def etap_R58(P, out, W, iter_, buduj=True, poprzednie=None, runda2=None):
    """R58: komplet okragly do ramki - 8 plytek okraglych ramkowych (2 bazowe + n1-n6), wkladka okragla, pokrywka okragla, 2 JSON ukladu.
    Buduje i sprawdza TYLKO te pliki (K-01...K-04b, K-05, K-06...K-09, K-11, K-13, K-16, K-61, K-62, K-64...K-67); pliki etapow A-C
    (21 STL, 4 JSON) tylko czyta jako odniesienie (uklady kwadratowe i okragle, plytki okragle bazowe, wkladka kwadratowa) - nic
    w nich nie zapisuje i nic nie kasuje. buduj=False (--etap R58_SPRAWDZ): tylko sprawdzenia istniejacych plikow R58."""
    kat_stl = os.path.join(out, 'stl')
    kat_json = os.path.join(out, 'json')
    kat_rz = os.path.join(out, 'raport', 'rzuty')
    os.makedirs(kat_stl, exist_ok=True)
    pliki = []
    ref = {}
    for typ in TYPY_PLYTEK:
        ref[typ], _s = wczytaj_uklad(P, typ, kat_json, zapisuj=False, opis_odczytu='odniesienie R58')
    uklady = {}
    for typ in TYPY_PLYTEK_R58:
        uklady[typ], sc = wczytaj_uklad(P, typ, kat_json, zapisuj=buduj, opis_odczytu='R58_SPRAWDZ')
        pliki.append({'plik': os.path.relpath(sc, out).replace('\\', '/'), 'sciezka': sc})
    czesci = []
    for typ in TYPY_PLYTEK_R58:
        czesci.append(('plytka_%s' % typ, 'plytka_%s' % typ, None, uklady[typ]))
        for n in numery_plytek(P, typ):
            czesci.append(('plytka_%s_n%d' % (typ, n), 'plytka_%s' % typ, n, uklady[typ]))
    czesci.append(('wkladka_okragla', 'wkladka_okragla', None, None))
    czesci.append(('pokrywka_okragla', 'pokrywka_okragla', None, None))
    # quantities_r58 / materials_r58: dokladnie czesci do zamowienia kompletu (bez plytek bazowych)
    do_zam = {'ramka_' + r for r, _rd, n, _u in czesci if n is not None or not r.startswith('plytka')}
    if set(P['quantities_r58']) != do_zam or set(P['materials_r58']) != do_zam:
        raise BladProjektu('quantities_r58 / materials_r58: różnica kluczy %s (oczekiwane %s)'
                           % (sorted((set(P['quantities_r58']) | set(P['materials_r58'])) ^ do_zam), sorted(do_zam)))
    nr_r58 = [n for typ in TYPY_PLYTEK_R58 for n in numery_plytek(P, typ)]
    if len(set(nr_r58)) != len(nr_r58):
        raise BladProjektu('plate_numbers_round_frame: numer użyty dwa razy %s' % nr_r58)
    eksport = []
    for rdzen, rodzaj, numer, uklad in czesci:
        M = M_druk(P, rodzaj)
        sciezka = os.path.join(kat_stl, nazwa_stl(P, rdzen))
        if buduj:
            if rodzaj == 'wkladka_okragla':
                ob = zbuduj_wkladke_okragla(P, rdzen)
            elif rodzaj == 'pokrywka_okragla':
                ob = zbuduj_pokrywke_okragla(P, rdzen)
            else:
                ob = zbuduj_plytke(P, uklad, numer, rdzen)
            eksportuj_stl(ob, sciezka, M, zero_dodatnie=True)
            usun_obiekt(ob)
        elif not os.path.isfile(sciezka):
            raise BladProjektu('R58_SPRAWDZ: brak pliku %s' % sciezka)
        eksport.append((rdzen, rodzaj, numer, uklad, sciezka, M))
    # uklady JSON: K-05 (h: sockets = kwadrat typu), K-16
    for typ in TYPY_PLYTEK_R58:
        sprawdz_uklad_json(W, P, uklady[typ], typ, ref[typ_bazowy(typ)])
        sprawdz_scianki_naroznikow(W, P, uklady[typ], typ)
    # odniesienia (pliki R59, tylko odczyt): mapy wierzchu plytek okraglych bazowych; wkladka kwadratowa
    punkty = punkty_kola(P['plate_round_d'] / 2 + 0.5, KROK_MAPY_R58)
    mapy_ref = {}
    for typ in TYPY_PLYTEK_R58:
        rr = 'plytka_okragla_%s' % typ_bazowy(typ)
        sc_ref = sciezka_stl_istniejaca(P, kat_stl, rr)
        s_ref = Siatka(sc_ref, M_druk(P, rr).inverted())
        mapy_ref[typ] = (mapa_promieni(s_ref.bvh, punkty, 5.0, -1), os.path.basename(sc_ref))
        s_ref.zwolnij()
    sc_wkl_kw = sciezka_stl_istniejaca(P, kat_stl, 'wkladka')
    T = P['plate_thickness']
    plyty, stl = [], {}
    for rdzen, rodzaj, numer, uklad, sciezka, M in eksport:
        plik = os.path.basename(sciezka)
        siatka = Siatka(sciezka, M.inverted())
        if rodzaj == 'wkladka_okragla':
            zw = P['insert_opening'] / 2 + P['insert_wall_w']
            ex = P['tab_pos_x'] + P['tab_w'] / 2
            zakres = (-ex, ex, -zw, P['tab_end_y'], -P['tab_pin_h'], max(P['insert_h'] + P['label_relief_h'], P['insert_shelf_h'] + P['round_key_rib_h']))
            obj, gab = ogolne_stl(W, plik, siatka, (zakres[1] - zakres[0], zakres[3] - zakres[2], zakres[5] - zakres[4]), zakres, rodzaj)
            s_kw = Siatka(sc_wkl_kw, M_druk(P, 'wkladka').inverted())
            sprawdz_wkladke_okragla(W, P, siatka, plik, s_kw, os.path.basename(sc_wkl_kw), kat_rz, iter_)
            s_kw.zwolnij()
        elif rodzaj == 'pokrywka_okragla':
            rw, rz, wys = wymiary_pokrywki_okraglej(P)
            obj, gab = ogolne_stl(W, plik, siatka, (2 * rz, 2 * rz, wys), (-rz, rz, -rz, rz, -wys, 0.0), rodzaj)
            sprawdz_pokrywke_okragla(W, P, siatka, plik)
        else:
            rel = P['number_relief_h'] if (numer is not None and uklad['number_relief'] is not None) else 0.0
            B = uklad['d']
            obj, gab = ogolne_stl(W, plik, siatka, (B, B, T + rel), (-B / 2, B / 2, -B / 2, B / 2, -T, rel), rodzaj)
            sprawdz_plytke(W, P, siatka, plik, uklad, numer)
            typ = uklad['plate']
            sprawdz_ramkowa(W, P, siatka, plik, uklad, numer, ref[typ_bazowy(typ)], punkty, mapy_ref[typ][0], mapy_ref[typ][1], kat_rz, iter_)
            if numer is not None and uklad['number_relief'] is not None:
                rzut_cyfry(P, siatka, plik, kat_rz, iter_, uklad['number_relief'])
            plyty.append((rdzen, sciezka, M, uklad))
        bb = siatka.bbox_stl
        DZIENNIK['stl'][rdzen] = (obj, bb)
        pliki.append({'plik': os.path.relpath(sciezka, out).replace('\\', '/'), 'sciezka': sciezka,
                      'gab': '%.3f × %.3f × %.3f' % (bb[1] - bb[0], bb[3] - bb[2], bb[5] - bb[4]), 'obj': '%.2f' % obj})
        stl[rdzen] = (sciezka, M)
        siatka.zwolnij()
    # runda 2: informacyjnie stare plytki okragle n8/n9 (pliki R59, tylko odczyt) i - gdy podano --r58-poprzednie - geometria rundy 1
    stare = []
    for typ in ('okragla_wieczorna', 'okragla_poranna'):
        for n in numery_plytek(P, typ):
            r = 'plytka_%s_n%d' % (typ, n)
            stare.append((r, sciezka_stl_istniejaca(P, kat_stl, r), M_druk(P, 'plytka_%s' % typ)))
    pop = None
    if poprzednie:
        kp = os.path.join(out, poprzednie)
        sw = os.path.join(kp, nazwa_stl(P, 'wkladka_okragla'))
        pl = [('%s (runda 1)' % r, os.path.join(kp, nazwa_stl(P, r)), M_druk(P, r)) for r in ('plytka_%s' % t for t in TYPY_PLYTEK_R58)]
        if not all(os.path.isfile(p) for p in [sw] + [x[1] for x in pl]):
            raise BladProjektu('--r58-poprzednie: brak plików rundy 1 w %s' % kp)
        pop = (sw, pl)
    r2 = None
    if runda2:
        k2 = os.path.join(out, runda2)
        r2 = (os.path.join(k2, nazwa_stl(P, 'wkladka_okragla')), os.path.join(k2, nazwa_stl(P, 'pokrywka_okragla')))
        if not all(os.path.isfile(p) for p in r2):
            raise BladProjektu('--r58-runda2: brak wkładki lub pokrywki rundy 2 w %s' % k2)
    sprawdz_pasowania_R58(W, P, plyty, stl['wkladka_okragla'][0], stl['pokrywka_okragla'][0], stare, pop, r2)
    # ilosci kompletu (quantities_r58 / materials_r58) z objetosciami z siatek - do raportu (arkusz zamowienia R59 bez zmian)
    for klucz in sorted(P['quantities_r58']):
        obj, _bb = DZIENNIK['stl'][klucz[len('ramka_'):]]
        DZIENNIK['ilosci_r58'].append((nazwa_stl(P, klucz[len('ramka_'):]), P['quantities_r58'][klucz], P['materials_r58'][klucz], obj))
    return pliki


def odstepstwa_informacyjne_R58(P):
    """R58 (komplet okragly do ramki): interpretacje i swiadome roznice wzgledem zlecenia / dotychczasowych zasad (rejestr odstepstw)."""
    D = DZIENNIK['odstepstwa']
    fw, rl = P['finger_cut_w'], P['round_insert_ledge_r']
    D.append(('R58 / wycięcie palcowe wkładki okrągłej (zlecenie: do y = −44,0)',
              'koniec bryły tnącej liczony z parametrów: −√(%g² − %g²) + 5 × 0,1 = %s' % (rl, fw / 2, liczba_pl(-math.sqrt(rl * rl - (fw / 2) ** 2) + 5 * NADDATEK, 3)),
              'za okręgiem występu (y −%s przy x ±%g) jest już tylko wolny otwór, więc bryła wyniku jest identyczna jak przy −44,0; bez nowego klucza w `parametry.json`'
              % (liczba_pl(math.sqrt(rl * rl - (fw / 2) ** 2), 3), fw / 2), 'nie — informacyjnie'))
    D.append(('R58 / ilości i materiały kompletu okrągłego', 'osobne klucze `quantities_r58` i `materials_r58` (nie w `quantities` / `materials`)',
              'dopisanie do `quantities` zmieniłoby arkusz zamówienia R59 (`wyniki_v2/arkusze`) i sprawdzenie K‑57 starych plików; włączenie do arkusza = krok koordynatora (przebieg ALL)',
              'tak — koordynator (arkusz zamówienia)'))
    D.append(('R58 / K‑60 przy `--etap SPRAWDZ` (zrzut `parametry.json` w `arkusz_wymiarow.md`)',
              'zrzut sprzed R58 uznany za zgodny tylko wtedy, gdy nie ma w nim żadnego z %d kluczy R58 (`KLUCZE_R58`; wszystkie są w `parametry.json`) i poza tym nie ma różnic [runda 2, D1]' % len(KLUCZE_R58),
              'arkusze R59 zostają bez zmian (zlecenie), a nowe klucze nie wpływają na żaden plik etapów A–C; każda inna różnica zrzutu nadal daje NIE; przebieg ALL koordynatora zapisze pełny zrzut',
              'tak — koordynator (protokół K‑60)'))
    D.append(('R58 / sprawdzenia płytki okrągłej ramkowej', 'K‑61 (b) na Z −4 i −7,5 promieniami równoległymi do osi ścięcia, odsuniętymi o ±(w rowka/2 + cięciwa/2)/2; K‑63 nie dotyczy (zastępuje go K‑64); K‑09 bez kontroli odwrotnej dawnych rogów',
              'w osi ścięcia leży rowek klucza (Z −8…%s), więc promień w osi trafiałby w jego koniec r %s; kieszenie, rowek pokrywki i rowek klucza są cechami płytki ramkowej; dawne rogi (±42, ±42) leżą poza ø100'
              % (liczba_pl(-P['plate_thickness'] + P['round_key_slot_h'], 1), liczba_pl(P['round_key_slot_r0'], 1)),
              'nie — informacyjnie (zapis w protokole)'))
    D.append(('R58 / numery n1–n6 płytek okrągłych ramkowych', 'te same numery i bity co płytki kwadratowe (decyzja właściciela); `kody_plytek.md` (arkusze R59) nie był generowany na nowo',
              'program stanowiska rozpoznaje dziś płytkę po numerze — przy n1–n6 nie odróżni okrągłej od kwadratowej bez zmiany programu (osobna paczka); tabela kodów R58 w `R58_wdrozenie_zmiany.md`',
              'tak — koordynator (program stanowiska, arkusz kodów)'))
    D.append(('R58 / pokrywka okrągła bez klucza', 'kubek obrotowo symetryczny poza garbami, szczelinami odciążającymi (runda 2) i wycięciami palcowymi; położenie nominalne (wycięcia z przodu i z tyłu) sprawdzone w K‑67',
              'pokrywkę można założyć w dowolnym obrocie; garb nad ścięciem płytki (cięciwa %g) nie zahacza (czubek r %s > ścięcie %s), zostają 3 garby; siła zatrzasku do sprawdzenia na pierwszym wydruku FDM'
              % (P['round_flat_w'], liczba_pl(P['plate_round_d'] / 2 + P['cover_clearance'] - P['cover_snap_bump'], 2), liczba_pl(sciecie_okraglej(P)[1], 3)),
              'nie — informacyjnie (ryzyko w `R58_wdrozenie_zmiany.md`)'))
    D.append(('R58 / zapis STL kompletu okrągłego (K‑59)', '`stl_kanoniczny(zero_dodatnie=True)`: liczby −0,0 zapisywane jako +0,0 (normalne i wierzchołki) — tylko pliki `--etap R58`',
              'eksporter zapisuje znak zera w kilku normalnych różnie w kolejnych przebiegach (`ramka_wkladka_v2`, `do_v3.md` #9; w R58 tak samo wkładka okrągła: 3 normalne, wierzchołki i trójkąty identyczne); '
              'po zmianie 10 STL i 2 JSON odtwarzają się bajtowo w czystej kopii folderu; pliki etapów A–C zapisywane bez zmian (domyślnie False), więc ich SHA nie zależą od R58',
              'nie — informacyjnie (normalizacja dla wszystkich plików nadal w v3)'))
    D.append(('R58 runda 2 / K‑67 szukanie ułożeń płaskich (B1)', 'mapa spodu płytki (od spodu) i mapa wierzchu wkładki (z góry) z siatek co %s mm; braki materiału płytki poszerzone o 1 węzeł '
              '(krawędź i otwory o %s mm mniejsze); styk spodu z półką: tolerancja %s' % (liczba_pl(KROK_ULOZEN, 1), liczba_pl(KROK_ULOZEN, 1), liczba_pl(TOL_STYKU, 2)),
              'bez poszerzenia przy przesunięciu równym luzowi węzły ściany otworu wkładki trafiałyby w węzły krawędzi płytki (fałszywy styk); granice okna wejścia są dokładne do ok. ±0,15° '
              '(siatka 0,1 mm na promieniu ok. 47); metoda 2,5D (jedna kolumna materiału na węzeł) wystarcza, bo płytka leży płasko na Z %s, a nad półką wkładki są tylko ściana otworu i żebro'
              % liczba_pl(P['insert_shelf_h'], 1), 'nie — informacyjnie'))


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    ap = argparse.ArgumentParser(prog='ramka_generator.py')
    ap.add_argument('--etap', required=True, choices=['A', 'B', 'C', 'ALL', 'SPRAWDZ', 'R58', 'R58_SPRAWDZ'])
    ap.add_argument('--out', default='wyniki_v2')
    ap.add_argument('--iter', type=int, default=1)
    ap.add_argument('--bez-renderow', action='store_true', help='przebieg probny bez renderow Cycles (K-60 = NIE)')
    ap.add_argument('--raport', default=None, help='etykieta w nazwie raportu zamiast etapu (np. R54 -> raport_wykonawcy_R54_iter1.md)')
    ap.add_argument('--r58-poprzednie', default=None, help='R58: katalog (wzgledem --out) z plikami rundy 1 (wkladka i plytki bazowe) - kontrola czulosci K-67')
    ap.add_argument('--r58-runda2', default=None, help='R58: katalog (wzgledem --out) z wkladka i pokrywka rundy 2 - kontrola czulosci kolnierza K-67 (runda 3)')
    a = ap.parse_args(argv)
    t0 = time.time()
    out = os.path.join(KATALOG, a.out)
    sc_param = os.path.join(KATALOG, 'parametry.json')
    P, STATUS, liczone = wczytaj_parametry(sc_param)
    for klucz, wp, wj in porownaj_plan_z_json(P):
        DZIENNIK['odstepstwa'].append((
            'tabela 3 planu / `%s`' % klucz, 'przyjęto %g (parametry.json) zamiast %g z tabeli 3' % (wj, wp),
            'sprzeczność wewnątrz planu: tekst 4.1, D11 i R47 (10) podają %g, tabela 3.1 nie została poprawiona; prompt każe brać plan — rozstrzygnięcie R47 jest planem' % wj if klucz == 'code_dimple_x' else 'sprzeczność plan ↔ JSON',
            'nie — do poprawy tabeli 3.1 przez sesję 1' if klucz == 'code_dimple_x' else 'tak'))
    if a.etap in ('R58', 'R58_SPRAWDZ'):
        main_R58(a, P, liczone, out, sc_param, t0)
        return
    buduj = a.etap != 'SPRAWDZ'
    etapy = ETAPY[a.etap] if buduj else etapy_istniejace(P, out)
    znacz = 'iter%d' % a.iter if buduj else 'SPRAWDZ_iter%d' % a.iter
    przygotuj_scene()
    if buduj:
        pominiete = wyczysc_wyniki(out, P)
        if pominiete:
            DZIENNIK['uklad'].append('czyszczenie wyników: pominięto %d STL kompletu R58 (%s)' % (len(pominiete), ', '.join(sorted(pominiete))))
    W = Wyniki()
    pliki, stl = etap_A(P, out, W, znacz, buduj)
    odstepstwa_informacyjne_R57(P)
    odstepstwa_informacyjne_R59(P)
    wid = None
    if 'B' in etapy:
        pliki += etap_B(P, out, W, znacz, stl, buduj)
    if 'C' in etapy:
        pliki += etap_C(P, out, W, znacz, stl, buduj)
    if 'B' in etapy:
        Z, wszystkie = zbuduj_zlozenie(P, stl)
        sprawdz_zlozenie(W, P, Z)
        odstepstwa_informacyjne_B(P)
        if 'C' in etapy:
            odstepstwa_informacyjne_C(P)
        if 'C' in etapy and buduj:
            mat = przygotuj_scene_renderu(P, wszystkie, sorted(Z))
        if buduj:
            sc_blend = zapisz_blend(out)
            pliki.append({'plik': os.path.relpath(sc_blend, out).replace('\\', '/'), 'sciezka': sc_blend})
        if 'C' in etapy:
            if buduj:
                if not a.bez_renderow:
                    wid = rendery(P, out, wszystkie, mat, sorted(Z))
                    for n in ('render_rozstrzelony.png', 'render_zlozony.png', 'render_plytki.png'):
                        pliki.append({'plik': 'render/' + n, 'sciezka': os.path.join(out, 'render', n)})
                for sc in zapisz_arkusz_zamowienia(P, out):
                    pliki.append({'plik': os.path.relpath(sc, out).replace('\\', '/'), 'sciezka': sc})
                sc, odch = zapisz_arkusz_wymiarow(P, out, stl, Z, sc_param)
                pliki.append({'plik': os.path.relpath(sc, out).replace('\\', '/'), 'sciezka': sc})
                if odch:
                    ostrzez('arkusz_wymiarow.md: %d wymiarów / pasowań poza ± 0,05 od nominału (oznaczone ✗)' % odch)
            sprawdz_arkusz_zamowienia(W, P, out)
            W.nd('K-59', 'SHA każdego STL = raport po przebiegu w czystej kopii', 'B',
                 'wykonuje recenzent (prompt wykonawcy, etap C); kolejność trójkątów w STL kanoniczna (`stl_kanoniczny`)')
            sprawdz_K60(W, P, out, etapy, wid, sc_param, liczone)
    wyniki_nie_do_rejestru(W, [e for e in etapy if e != 'A'])
    if 'C' in etapy and buduj:
        for sc in (zapisz_do_v3(out, W), zapisz_readme(P, out, a.raport or a.etap, a.iter, pliki)):
            pliki.append({'plik': os.path.relpath(sc, out).replace('\\', '/'), 'sciezka': sc})
    for p in pliki:
        p['rozmiar'] = os.path.getsize(p['sciezka'])
        p['sha'] = sha256(p['sciezka'])
    if not buduj:
        niezrobione = ['- Tryb SPRAWDZ: pliki nie były generowane; sprawdzenia etapów %s na plikach istniejących w `%s` (SHA w sekcji 2).'
                       % ('+'.join(etapy), os.path.relpath(out, KATALOG).replace('\\', '/')),
                       '- Rzuty kontrolne zapisane z przyrostkiem `_%s`; `.blend`, arkusze, rendery i README nie były zmieniane.' % znacz]
        if 'C' in etapy:
            niezrobione.append('- K‑60: widoczność podpisanych części nie mierzona (rendery nie powstały w tym przebiegu); rozmiary PNG sprawdzone.')
    elif etapy[-1] == 'A':
        niezrobione = ['- Sprawdzenia etapów B i C (K‑23…K‑57, K‑59, K‑60) — poza zakresem etapu A.',
                       '- K‑22, część złożeniowa (przecięcie pokrywka–wkładka, K‑53): N/D w etapie A (wkładka powstaje w etapie B); część sondowa wykonana.']
    elif etapy[-1] == 'B':
        niezrobione = ['- Etap C (tulejka DC, podkładki panelu, rendery, arkusze, README; K‑52b, K‑52c, K‑57, K‑59, K‑60) — poza zakresem etapu B.',
                       '- `ramka_v2.blend` z etapu B: części i bryły zastępcze w kolekcjach, w pozycji złożonej, bez materiałów i kamer (dochodzą w etapie C).',
                       '- K‑53 w etapie B obejmuje części z etapów A i B (bez tulejki DC z etapu C).']
    else:
        niezrobione = ['- K‑59 (powtarzalność) wykonuje recenzent (prompt); wynik w raporcie = N/D.',
                       '- Bramka G4b (trzecie oko) — osobna sesja; `arkusz_wymiarow.md` §2–§3 zawiera wymiary i pasowania zmierzone z siatek jako punkt wyjścia.']
        if a.bez_renderow:
            niezrobione.append('- Przebieg z `--bez-renderow` (próbny): rendery nie powstały, K‑60 = NIE.')
    kontekst = {
        'etap': a.etap, 'iter': a.iter, 'blender': bpy.app.version_string,
        'data': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), 'czas': time.time() - t0,
        'sha_param': sha256(sc_param), 'sha_gen': sha256(os.path.abspath(__file__)),
        'liczone': liczone, 'font': _FONT.get('plik', '?'), 'odpowiedzi': ODPOWIEDZI.get((a.etap, a.iter), []),
        'niezrobione': niezrobione, 'raport': a.raport,
    }
    sc_rap = os.path.join(out, 'raport', 'raport_wykonawcy_%s_iter%d.md' % (a.raport or a.etap, a.iter))
    licz = zapisz_raport(sc_rap, kontekst, W, pliki)
    log('RAPORT', sc_rap, 'B=%d P=%d D=%d' % (licz['B'], licz['P'], licz['D']), 'czas %.0f s' % (time.time() - t0))


def main_R58(a, P, liczone, out, sc_param, t0):
    """R58: --etap R58 buduje i sprawdza tylko komplet okragly do ramki (10 STL + 2 JSON); --etap R58_SPRAWDZ tylko sprawdza.
    Bez czyszczenia wynikow (wyczysc_wyniki) i bez etapow A-C: 21 STL, 4 JSON, arkusze, rendery i .blend R59 zostaja nietkniete."""
    buduj = a.etap == 'R58'
    znacz = ('R58_iter%d' if buduj else 'R58_SPRAWDZ_iter%d') % a.iter
    przygotuj_scene()
    W = Wyniki()
    pliki = etap_R58(P, out, W, znacz, buduj, a.r58_poprzednie, a.r58_runda2)
    odstepstwa_informacyjne_R58(P)
    for p in pliki:
        p['rozmiar'] = os.path.getsize(p['sciezka'])
        p['sha'] = sha256(p['sciezka'])
    niezrobione = ['- Tryb %s: tylko komplet okrągły do ramki (R58); pliki etapów A–C (21 STL, 4 JSON, arkusze, rendery, `.blend`) nie były budowane ani zmieniane — '
                   'czytane tylko jako odniesienie (układy kwadratowe i okrągłe, płytki okrągłe bazowe, wkładka kwadratowa).' % a.etap,
                   '- Arkusze (`kody_plytek.md`, arkusz zamówienia, `arkusz_wymiarow.md`), rendery i `ramka_v2.blend` bez nowych części — krok koordynatora (przebieg ALL).',
                   '- Program stanowiska nie zna płytek okrągłych n1–n6 — osobna paczka.']
    if not buduj:
        niezrobione.append('- R58_SPRAWDZ: pliki nie były generowane; sprawdzenia na plikach istniejących w `%s`.' % os.path.relpath(out, KATALOG).replace('\\', '/'))
    dodatek = ['', '## 7. Komplet do zamówienia (`quantities_r58`, `materials_r58`; objętości z siatek tego przebiegu)', '',
               '| Plik STL | Szt. | Materiał | Objętość [cm³] | Objętość × szt. [cm³] |', '|---|---|---|---|---|']
    for plik, q, mat, obj in DZIENNIK['ilosci_r58']:
        dodatek.append('| `%s` | %d | %s | %s | %s |' % (plik, q, mat, liczba_pl(obj), liczba_pl(obj * q)))
    dr = [(q, obj) for _p, q, mat, obj in DZIENNIK['ilosci_r58'] if mat.startswith(DRUKARNIA)]
    sobj = sum(q * o for q, o in dr)
    dodatek += ['', 'Drukarnia (%s…): %d pozycji, %s cm³ × stawka `cost_rate_min`…`cost_rate_max` %s…%s zł/cm³ = %s…%s zł (wariant najtańszy, bez mnożników — części białe).'
                % (DRUKARNIA, len(dr), liczba_pl(sobj), liczba_pl(P['cost_rate_min']), liczba_pl(P['cost_rate_max']), liczba_pl(sobj * P['cost_rate_min'], 0), liczba_pl(sobj * P['cost_rate_max'], 0))]
    kontekst = {
        'etap': a.etap, 'iter': a.iter, 'blender': bpy.app.version_string,
        'data': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), 'czas': time.time() - t0,
        'sha_param': sha256(sc_param), 'sha_gen': sha256(os.path.abspath(__file__)),
        'liczone': liczone, 'font': _FONT.get('plik', '?'), 'odpowiedzi': [],
        'niezrobione': niezrobione, 'raport': a.raport, 'dodatek': dodatek,
    }
    sc_rap = os.path.join(out, 'raport', 'raport_wykonawcy_%s_iter%d.md' % (a.raport or a.etap, a.iter))
    licz = zapisz_raport(sc_rap, kontekst, W, pliki)
    log('RAPORT', sc_rap, 'B=%d P=%d D=%d' % (licz['B'], licz['P'], licz['D']), 'czas %.0f s' % (time.time() - t0))


if __name__ == '__main__':
    try:
        main()
    except BladProjektu as e:
        log('BLAD:', e)
        sys.exit(1)
    except Exception:
        import traceback
        traceback.print_exc()
        log('BLAD: wyjatek w skrypcie')
        sys.exit(1)
