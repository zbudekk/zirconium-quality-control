import sys, os, json, struct, glob
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from siatka import STL_NEW
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
J = os.path.join(R, 'wyniki_v2', 'json')
P = json.load(open(os.path.join(R, 'parametry.json'), encoding='utf-8'))
def val(k):
    for s, z in P.items():
        if isinstance(z, dict) and k in z:
            return z[k]['value'] if isinstance(z[k], dict) and 'value' in z[k] else z[k]
for typ in ('wieczorna', 'poranna'):
    a = json.load(open(os.path.join(J, 'uklad_gniazd_okragla_ramkowa_%s.json' % typ), encoding='utf-8'))
    b = json.load(open(os.path.join(J, 'uklad_gniazd_okragla_%s.json' % typ), encoding='utf-8'))
    kw = json.load(open(os.path.join(J, 'uklad_gniazd_%s.json' % typ), encoding='utf-8'))
    print('===', typ, 'klucze ramkowa:', sorted(a.keys()))
    for k in sorted(set(a) | set(b)):
        if a.get(k) != b.get(k):
            print('  rozni sie od okraglej:', k, ':', json.dumps(a.get(k), ensure_ascii=True)[:400], '| stara:', json.dumps(b.get(k), ensure_ascii=True)[:200])
    print('  sockets == kwadrat:', a['sockets'] == kw['sockets'], ' markers == okragla:', a.get('markers') == b.get('markers'), ' code_dimples == okragla:', a.get('code_dimples') == b.get('code_dimples'))
print('parametry R58:', {k: val(k) for k in ['round_magnet_r', 'round_key_slot_w', 'round_key_slot_r0', 'round_key_slot_h', 'plate_numbers_round_frame', 'round_cover_snap_angles', 'round_insert_clearance', 'round_insert_ledge_r', 'round_insert_shelf', 'round_key_pin_d', 'round_key_pin_h', 'round_key_pin_chamfer', 'magnet_pocket_d', 'magnet_pocket_depth', 'cover_groove_w', 'cover_groove_depth', 'cover_groove_z', 'cover_clearance', 'cover_skirt_t', 'cover_snap_bump', 'cover_snap_hgt', 'cover_snap_w', 'cover_snap_z', 'cover_snap_r', 'insert_shelf_h', 'insert_h', 'insert_chamfer', 'hall_pocket_w', 'hall_pocket_l', 'hall_lead_channel_w', 'hall_lead_channel_h', 'hall_wall_pass_h', 'finger_cut_w', 'round_flat_w', 'round_flat_angle', 'plate_round_d', 'orient_post', 'orient_post_h', 'tab_t', 'insert_wall_w', 'insert_opening']})
print('quantities_r58:', val('quantities_r58')); print('materials_r58:', val('materials_r58'))
# -0.0 w nowych STL
for f in sorted(glob.glob(os.path.join(STL_NEW, '*.stl'))):
    d = open(f, 'rb').read(); n = struct.unpack('<I', d[80:84])[0]
    a = np.frombuffer(d, dtype=np.dtype([('f', '<u4', 12), ('a', '<u2')]), count=n, offset=84)['f']
    print(os.path.basename(f), 'liczb -0.0:', int((a == 0x80000000).sum()))