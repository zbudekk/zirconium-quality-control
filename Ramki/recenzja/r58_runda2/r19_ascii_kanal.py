import os, numpy as np
D = os.path.dirname(os.path.abspath(__file__))
k = 0.1; x0 = -66.0; y0 = -53.5
for plik, (cx, cy) in (('wkl_kw_spod.npy', (-42, -42)), ('wkl_okr_spod.npy', (-31.82, -31.82))):
    Zb = np.load(os.path.join(D, plik))
    print(plik, 'wokol', (cx, cy), "('#' = pelny spod Z0, '1' = sufit 1.0, '5' = 1.5, 'o' = przelot, '.' = poza)")
    for y in np.arange(cy + 6, cy - 24, -0.5):
        row = ''
        for x in np.arange(cx - 24, cx + 6, 0.5):
            i = int(round((x - x0) / k)); j = int(round((y - y0) / k))
            if not (0 <= i < Zb.shape[1] and 0 <= j < Zb.shape[0]): row += ' '; continue
            z = Zb[j, i]
            row += 'o' if not np.isfinite(z) else ('#' if z < 0.05 else ('1' if z < 1.1 else ('2' if z < 1.3 else ('5' if z < 1.6 else '+'))))
        print('  ' + row)