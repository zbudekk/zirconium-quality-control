import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from siatka import *
D = os.path.dirname(os.path.abspath(__file__))
k = 0.1; x0 = -66.0; nx = int(round(132 / k)) + 1; y0 = -53.5; ny = int(round(151 / k)) + 1
X = x0 + np.arange(nx) * k; Y = y0 + np.arange(ny) * k
XX, YY = np.meshgrid(X, Y); RR = np.hypot(XX, YY)
Zt = np.load(os.path.join(D, 'wkl_okr_gora.npy'))
m = (RR >= 50.25) & (RR <= 51.85)
print('wkladka pod kolnierzem pokrywki (r 50.25..51.85): max Z %.4f (dol kolnierza 6.5 -> luz %.4f)' % (np.nanmax(Zt[m]), 6.5 - np.nanmax(Zt[m])))
print('  maks Z wkladki ogolnie (strzalki): %.4f przy' % np.nanmax(Zt), XX[np.nanargmax(Zt) // 1 // 1 if False else np.unravel_index(np.nanargmax(Zt), Zt.shape)], YY[np.unravel_index(np.nanargmax(Zt), Zt.shape)])
mm = Zt > 6.01
print('  obszar Z > 6.01 (strzalki): x %.2f..%.2f, y %.2f..%.2f, r min %.2f' % (XX[mm].min(), XX[mm].max(), YY[mm].min(), YY[mm].max(), RR[mm].min()))
# pokrywka obrocona dowolnie: kolnierz zawsze w pierscieniu r 50.3..51.8 - ten sam wynik
# Plytka w wkladce: luz promieniowy w 720 kierunkach (otwor Z 4.75 minus plytka Z 6.5 = lokalnie -4)
W = Siatka(os.path.join(STL_NEW, 'ramka_wkladka_okragla_v2.stl'), shift=(0, 0, -3.5))
for typ in ('wieczorna', 'poranna'):
    P = Siatka(os.path.join(STL_NEW, 'ramka_plytka_okragla_ramkowa_%s_v2.stl' % typ), shift=(0, 0, 2.5))
    luz = []
    for a in np.arange(0, 360, 0.5):
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        ri = W.pierwsze((0, 0, 4.75), (c, s, 0))
        tp = P.pierwsze((60 * c, 60 * s, 6.5), (-c, -s, 0))
        if ri is None or tp is None: continue
        luz.append((a, ri - (60 - tp)))
    L = np.array(luz)
    print(typ, 'luz promieniowy (Z 4.75 / 6.5): %.4f..%.4f; w osi sciecia %.4f' % (L[:, 1].min(), L[:, 1].max(), L[L[:, 0] == 315, 1][0]))
    # spod plytki i wierzch wystepu
    print('   spod plytki Z %.4f; wierzch wystepu (0, 48.7) %.4f' % (P.bbox()[0][2], 10 - W.pierwsze((0, 48.7, 10), (0, 0, -1))))
    # kolek w rowku
    cx, cy = 31.8198, -31.8198
    cu, su = math.cos(math.radians(-45)), math.sin(math.radians(-45))
    for z in (2.7, 3.5, 3.9):
        sp = P.pierwsze((cx, cy, z), (-su, cu, 0)); sm = P.pierwsze((cx, cy, z), (su, -cu, 0))
        kp = W.pierwsze((cx - su * 3, cy + cu * 3, z), (su, -cu, 0)); km = W.pierwsze((cx + su * 3, cy - cu * 3, z), (-su, cu, 0))
        print('   Z %.1f: rowek +v %.4f -v %.4f; kolek +v %.4f -v %.4f -> luz %.4f / %.4f' % (z, sp, sm, 3 - kp, 3 - km, sp - (3 - kp), sm - (3 - km)))
    suf = P.pierwsze((cx, cy, 0), (0, 0, 1)); wk = 10 - W.pierwsze((cx, cy, 10), (0, 0, -1))
    print('   sufit rowka nad kolkiem Z %.4f, wierzch kolka %.4f -> %.4f' % (suf, wk, suf - wk))
    # koniec rowka - kolek wzdluz osi
    e_r = P.pierwsze((45 * cu, 45 * su, 3.5), (-cu, -su, 0)); e_k = W.pierwsze((40 * cu, 40 * su, 3.5), (cu, su, 0))
    print('   koniec rowka r %.4f; kolek od r %.4f -> szczelina %.4f' % (45 - e_r, 40 + e_k, (40 + e_k) - (45 - e_r)))
    # osie kieszeni magnesow vs kieszenie Halla
    for nm, (ax, ay) in (('A', (-31.8198, -31.8198)), ('B', (-31.8198, 31.8198)), ('C', (31.8198, 31.8198))):
        t = [P.pierwsze((ax, ay, 3.6), d) for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0))]
        h = [W.pierwsze((ax, ay, 1.75), d) for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0))]
        mx, my = ax + (t[0] - t[1]) / 2, ay + (t[2] - t[3]) / 2; hx, hy = ax + (h[0] - h[1]) / 2, ay + (h[2] - h[3]) / 2
        print('   %s: os kieszeni (%.4f, %.4f), os Halla (%.4f, %.4f), odchylka %.4f' % (nm, mx, my, hx, hy, math.hypot(mx - hx, my - hy)))
    # odleglosc spod magnesu - czujnik: spod plytki Z 2.5; magnes 2.0 w kieszeni 2.2 -> spod magnesu Z 2.5 + 0.2 = 2.7 (gdy dosuniety do sufitu)
    suf_k = P.pierwsze((-31.8198, -31.8198, 0), (0, 0, 1))
    print('   sufit kieszeni Z %.4f -> spod magnesu 2.0 przy suficie Z %.4f; wierzch czujnika (1.5 nad dyfuzorem Z 0) 1.5 -> szczelina %.4f' % (suf_k, suf_k - 2.0, suf_k - 2.0 - 1.5))