import math, numpy as np
R_PL, FL_PL, R_OT, FL_OT = 50.0, 49.3559, 50.3966, 49.7558
RM, R_KIE, R_KOL, R0, W2 = 45.0, 2.598, 1.5, 43.0, 1.8
u = np.array([math.cos(math.radians(-45)), math.sin(math.radians(-45))]); t = np.array([-u[1], u[0]])
pin = RM * u
g = np.arange(-0.4, 0.4001, 0.005); DX, DY = np.meshgrid(g, g); D = np.c_[DX.ravel(), DY.ravel()]; D = D[np.hypot(D[:, 0], D[:, 1]) <= 0.4]
phi = np.radians(np.arange(0, 360, 0.2)); beta = math.acos(FL_PL / R_PL)
def obrys(th):
    a = phi; dp = np.abs(((np.degrees(a) + 45) + 180) % 360 - 180)
    r = np.where(np.radians(dp) < beta, FL_PL / np.cos(np.radians(dp)), R_PL)
    a2 = a + math.radians(th)
    return np.c_[r * np.cos(a2), r * np.sin(a2)]
def ok_d(th):
    P = obrys(th)[::3]
    c1 = (P @ u).max() + D @ u <= FL_OT
    rr = np.hypot(P[None, :, 0] + D[:, None, 0], P[None, :, 1] + D[:, None, 1]).max(axis=1) <= R_OT
    return c1 & rr
def okno(cel_fn, srodek, zakres=4.0, krok=0.05):
    w = []
    for th in np.arange(srodek - zakres, srodek + zakres + 1e-9, krok):
        m = ok_d(th)
        if m.any() and cel_fn(th, D[m]).any():
            w.append(th)
    return (min(w), max(w)) if w else None
def w_kieszeni(alfa):
    def f(th, Dd):
        c = Dd + RM * np.array([math.cos(math.radians(alfa + th)), math.sin(math.radians(alfa + th))])
        return np.hypot(*(c - pin).T) <= R_KIE - R_KOL
    return f
def w_rowku(th, Dd):
    c, s = math.cos(math.radians(-th)), math.sin(math.radians(-th))
    q = (pin - Dd) @ np.array([[c, s], [-s, c]])
    return (q @ u - R_KOL >= R0) & (np.abs(q @ t) <= W2 - R_KOL)
print('rowek (poprawne):', okno(w_rowku, 0.0))
for alfa, nom in ((225, 90), (135, 180), (45, 270)):
    print('kieszen %d nad kolkiem:' % alfa, okno(w_kieszeni(alfa), nom))