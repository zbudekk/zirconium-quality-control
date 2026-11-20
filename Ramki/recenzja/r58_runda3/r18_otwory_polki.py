import os, json, math
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
J = os.path.join(R, 'wyniki_v2', 'json')
OSIE = {'A': (-31.8198, -31.8198), 'B': (-31.8198, 31.8198), 'C': (31.8198, 31.8198), 'D': (31.8198, -31.8198)}
def otwory(u):
    w = []
    for g in u['sockets']:
        if g['type'] == 'round':
            w.append((g['x'], g['y'], g['id'], g.get('hole_d', 3)))
        else:
            c, s = math.cos(math.radians(g['angle'])), math.sin(math.radians(g['angle']))
            for i in range(g['hole_count']):
                k = i - (g['hole_count'] - 1) / 2
                w.append((g['x'] + k * g['hole_pitch'] * c, g['y'] + k * g['hole_pitch'] * s, g['id'], g.get('hole_d', 3)))
    return w
def d_kw(x, y, cx, cy, s=5.0):
    return math.hypot(max(abs(x - cx) - s, 0), max(abs(y - cy) - s, 0))
for typ in ('wieczorna', 'poranna'):
    u = json.load(open(os.path.join(J, 'uklad_gniazd_okragla_ramkowa_%s.json' % typ), encoding='utf-8'))
    H = otwory(u)
    dmin_polka = min((d_kw(x, y, cx, cy) - hd / 2, k, gid) for x, y, gid, hd in H for k, (cx, cy) in OSIE.items())
    dmin_wyst = min((47.0 - math.hypot(x, y) - hd / 2, gid) for x, y, gid, hd in H)
    dmin_kolek = min((math.hypot(x - OSIE['D'][0], y - OSIE['D'][1]) - 1.5 - hd / 2, gid) for x, y, gid, hd in H)
    # kieszen Halla vs otwor (rzut)
    print(typ, 'otworow o3:', len(H), '; otwor - polka 10x10 min %.2f (polka %s, gniazdo id %s)' % dmin_polka, '; otwor - wystep r47 min %.2f (id %s)' % dmin_wyst, '; otwor - kolek min %.2f' % dmin_kolek[0])
    # gniazda (obrys gorny) nad polkami? gniazdo w rzucie nad polka - informacyjnie
    for g in u['sockets']:
        pass