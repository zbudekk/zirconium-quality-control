# -*- coding: utf-8 -*-
"""Tworzy warianty parametry.json do testów edge-case generatora (poza wyniki_v2/).

Użycie (Python Blendera albo dowolny Python 3.10+, bez bpy):
    python warianty.py <katalog_bazowy_z_kopia_generatora> <katalog_docelowy>

Katalog bazowy musi zawierać: ramka_generator.py, parametry.json, plan_ramki_v2.md, szablon_raport_wykonawcy.md.
Dla każdego wariantu powstaje <docelowy>/gen_<nazwa>/ z kopią tych plików i zmodyfikowanym parametry.json.
"""
import json, os, shutil, sys, copy

PLIKI = ['ramka_generator.py', 'parametry.json', 'plan_ramki_v2.md', 'szablon_raport_wykonawcy.md']


def ustaw(dane, klucz, value=None, status=None, usun=False):
    for sekcja, zaw in dane.items():
        if sekcja.startswith('_') or klucz not in zaw:
            continue
        if usun:
            del zaw[klucz]
            return
        if value is not None:
            zaw[klucz]['value'] = value
        if status is not None:
            zaw[klucz]['status'] = status
        return
    raise KeyError(klucz)


# nazwa -> (opis, funkcja modyfikująca dane, etap do uruchomienia, dodatkowe argumenty)
WARIANTY = {
    'base': ('bez zmian (baza, determinizm)', lambda d: None, 'C', '--bez-renderow'),
    'base2': ('bez zmian, drugi przebieg (K-59 bajtowo)', lambda d: None, 'C', '--bez-renderow'),
    'pomiar_bez_korekty': ('pi_stack_h 26->31 ZMIERZONE, nic więcej (jak zrobi to właściciel wg sekcji 10 planu)',
                           lambda d: ustaw(d, 'pi_stack_h', 31, 'ZMIERZONE'), 'C', '--bez-renderow'),
    'pomiar_frozen': ('pi_stack_h 31 ZMIERZONE + pi_clearance_top 8->3 (zamrożone 54/59,6/63,6 wg planu §10)',
                      lambda d: (ustaw(d, 'pi_stack_h', 31, 'ZMIERZONE'), ustaw(d, 'pi_clearance_top', 3)), 'C', '--bez-renderow'),
    'pomiar_readme': ('pi_stack_h 31 ZMIERZONE + LICZONE przeliczone wg README krok 2 (panel_pcb_z 59, korpus_h 64,6 ...)',
                      lambda d: (ustaw(d, 'pi_stack_h', 31, 'ZMIERZONE'), ustaw(d, 'panel_pcb_z', 59), ustaw(d, 'blat_top_z', 68.6),
                                 ustaw(d, 'korpus_h', 64.6), ustaw(d, 'panel_standoff_l', 55), ustaw(d, 'snap_pocket_z', 57.6),
                                 ustaw(d, 'snap_hook_z', 57.85), ustaw(d, 'blat_screw_z', 60), ustaw(d, 'label_pos_z', 56)), 'B', ''),
    'dc_hole_maly': ('dc_hole_d 12->11,5 ZMIERZONE (otwór mniejszy niż tulejka 11,85: wcisk niemożliwy)',
                     lambda d: ustaw(d, 'dc_hole_d', 11.5, 'ZMIERZONE'), 'C', '--bez-renderow'),
    'pusta_tulejka': ('dc_bush_inner_d 8,2->20 (otwór większy niż kołnierz 15: tulejka znika po różnicy)',
                      lambda d: ustaw(d, 'dc_bush_inner_d', 20), 'C', '--bez-renderow'),
    'boss_otwor': ('insert_hole_m25 2,1->9 (otwór większy niż boss Pi ø8)', lambda d: ustaw(d, 'insert_hole_m25', 9), 'B', ''),
    'pitch_140': ('panel_hole_pitch_x/y 120->140 ZMIERZONE (poza 110–130 z R50-2)',
                  lambda d: (ustaw(d, 'panel_hole_pitch_x', 140, 'ZMIERZONE'), ustaw(d, 'panel_hole_pitch_y', 140, 'ZMIERZONE')), 'C', '--bez-renderow'),
    'socket_depth': ('socket_depth 4->5 przy istniejącym JSON gniazd (kopia wyniki_v2/json) — bez korekty cover_inner_h', lambda d: ustaw(d, 'socket_depth', 5), 'A', ''),
    'socket_depth2': ('socket_depth 4->5 + cover_inner_h 14->13 (LICZONE) przy istniejącym JSON gniazd (kopia wyniki_v2/json)',
                      lambda d: (ustaw(d, 'socket_depth', 5), ustaw(d, 'cover_inner_h', 13)), 'A', ''),
    'wall_ujemna': ('wall_t 2,5->-2 (ujemna grubość ścianki)', lambda d: ustaw(d, 'wall_t', -2), 'B', ''),
    'dc_hole_zero': ('dc_hole_d 0 (zerowa średnica otworu)', lambda d: ustaw(d, 'dc_hole_d', 0, 'ZMIERZONE'), 'B', ''),
    'kierunek_plusX': ('bonnet_dc_dir +X (wtyk w stronę środka korpusu, R50-6 mówi tylko o -X/-Y/+Y)',
                       lambda d: ustaw(d, 'bonnet_dc_dir', '+X', 'ZMIERZONE'), 'C', '--bez-renderow'),
    'conn_zone_pod_pi': ('panel_conn_zone_h 60->100 i panel_bottom_parts_h 12->20 ZMIERZONE (złącza panelu nad Pi, luz Z 0)',
                         lambda d: (ustaw(d, 'panel_conn_zone_h', 100, 'ZMIERZONE'), ustaw(d, 'panel_bottom_parts_h', 20, 'ZMIERZONE'),
                                    ustaw(d, 'pi_clearance_top', 0)), 'C', '--bez-renderow'),
}


def main():
    baza, cel = sys.argv[1], sys.argv[2]
    os.makedirs(cel, exist_ok=True)
    with open(os.path.join(baza, 'parametry.json'), encoding='utf-8') as f:
        wzor = json.load(f)
    for nazwa, (opis, fn, etap, args) in WARIANTY.items():
        kat = os.path.join(cel, 'gen_' + nazwa)
        os.makedirs(kat, exist_ok=True)
        for p in PLIKI:
            shutil.copy(os.path.join(baza, p), kat)
        dane = copy.deepcopy(wzor)
        fn(dane)
        with open(os.path.join(kat, 'parametry.json'), 'w', encoding='utf-8') as f:
            json.dump(dane, f, ensure_ascii=False, indent=1)
        with open(os.path.join(kat, 'WARIANT.txt'), 'w', encoding='utf-8') as f:
            f.write('%s\n%s\n%s\n%s\n' % (nazwa, opis, etap, args))
        print('%-22s %-3s %s' % (nazwa, etap, opis))


if __name__ == '__main__':
    main()
