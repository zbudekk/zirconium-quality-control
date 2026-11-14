// narzedzia/uklad_kolo_R59.js - R59 (14.11.2026): uklady gniazd plytek w kole socket_zone_r z DOKLADNIE jednym rzedem rynienki.
// Rozszerzenie uklad_kolo_R54.js: 1 rynienka (z przodu albo z tylu) albo rynienka podzielona na dwie krotkie w jednym
// rzedzie (D3-b), dowolny zestaw srednic (takze fi 15 w porannej), przesuniecie calego bloku w y, rzedy w szachownice,
// stozki znacznikow z regula trojkata, dolki i cyfra plytki okraglej, zapis pliku wariantu (kopia parametry.json).
// Wszystkie stale (kolo, strefa, scianka, stozki, dolki, sciecie) czytane z parametry.json - nic nie jest wpisane z reki.
//
// Tryby:
//   node narzedzia/uklad_kolo_R59.js front --plytka=wieczorna|poranna [--parametry=parametry.json]
//        [--srednice=9,12,15] [--rynienka=60x15 | --rynienka=2x28.5x15] [--maxrzedow=6] [--maxrz=7.5:2] [--krok=0.1]
//        [--kwant=0.05] [--rozstawy=min|poprzedni|wszystkie] [--t-pierwsza] [--t-ymin=-33]
//        [--min=15:8,12:4] [--minod=12:14] [--max=7.5:8] [--minrazem=18] [--strona=przod|tyl]
//        [--dokladnie=10:2,12.5:2,15:1]  zestaw rzedow zadany z gory (ile rzedow ktorej srednicy + rynienka): narzedzie
//        dobiera kolejnosc rzedow i liczby gniazd, wypisuje wszystkie kolejnosci od najwiekszej liczby gniazd
//        [--mieszane]  dopuszcza rzedy MIESZANE (rozne srednice w jednym rzedzie, wzor symetryczny, np. fi 15 w srodku rzedu
//        fi 12,5); sensowne przy 2 srednicach - przy wiekszej liczbie wzorow jest bardzo duzo
//        [--najlepsze-wg=15]  zamiast zestawow niezdominowanych: dla kazdej liczby gniazd fi 15 jeden najlepszy uklad
//        [--watki=N] [--limit-s=240] [--postep=plik] [--memo=nie] [--top=60] [--wynik=front.json]
//     Przeglad kolejnosci rzedow (rzedy ciasno od przodu, scianka socket_wall_min takze po przekatnej; w rzedzie gniazda
//     w najmniejszym rozstawie d + scianka, liczba parzysta albo nieparzysta - obie galezie), start bloku co --krok mm.
//     Dla kazdego zestawu liczb gniazd zostaje uklad z najwiekszym zapasem do kola / strefy. Wynik: zestawy
//     niezdominowane (zaden inny nie ma >= tyle gniazd o srednicy >= d dla kazdego progu d), dla ktorych jest miejsce
//     na 3 stozki znacznikow. Liczy rownolegle (worker_threads); stany powtorzone (te same 3 ostatnie rzedy osiagniete
//     z nie gorszymi liczbami) sa pomijane. Po --limit-s sekund przeglad konczy sie sam i wypisuje "PRZEGLAD NIEPELNY".
//     UWAGA: poranna z 4 srednicami i 8 rzedami bez ograniczen nie konczy sie w rozsadnym czasie (14.11: przerwane po
//     17 min, brak pamieci) - zawezaj: --maxrzedow=7 --maxrz=7.5:2 --rozstawy=min (51 s na 16 watkach).
//     To przeglad ukladow RZEDOWYCH, nie dowod, ze nie istnieje gestsze upakowanie nieregularne.
//   node narzedzia/uklad_kolo_R59.js uloz spec.json [--parametry=parametry.json] [--wyjscie=parametry_wariant_<id>.json]
//     Z opisu wariantu (spec) liczy dokladne rzedy, stozki znacznikow, dolki i cyfre okraglej, sprawdza je i zapisuje
//     plik wariantu = kopia parametry.json ze zmienionymi tylko kluczami ukladu. Wynik sprawdzic weryfikuj_uklad_R59.js.
//   node narzedzia/uklad_kolo_R59.js uloz spec.json --diagnoza [--kwant=0.001]
//     Nie zapisuje pliku: sprawdza, czy uklad DOKLADNIE ze spec miesci sie przy jakimkolwiek przesunieciu w y,
//     a gdy nie - ile mm wysokosci brakuje i ktore obrysy to ograniczaja (np. dla szkicu przyslanego przez wlasciciela).
//
// Spec (JSON): { "id": "W-b", "plytka": "wieczorna", "nazwa": "...", "y0": -32.4 | "auto",
//   "rzedy": [ {"typ": "T", "l": 60, "w": 15} | {"typ": "T", "l": 28.5, "w": 15, "podzial": true, "hole_count": 2}
//              | {"d": 15} | {"d": 15, "k": 4} | {"d": 12, "k": 6, "p": 15} | {"d": 9, "y": -1.5, "x": [-36, ..., 36]} ],
//              (rzad mieszany: {"mieszany": [12.5, 12.5, 15, 12.5, 12.5]} - w pliku wariantu to osobne wpisy rzedu o roznym y)
//   albo "rows": [ rzedy w formacie parametry.json - brane doslownie ],
//   "znaczniki": "auto" | "zostaw" | {"A": [x, y], "B": [...], "C": [...]},      (domyslnie: zostaw, gdy wazne; inaczej auto)
//   "dolki_okragle": "auto" | "zostaw" | {"A": [..], ...},   "cyfra_okragla": "auto" | "zostaw" | [x, y] | null }
'use strict';
const fs = require('fs'), os = require('os'), path = require('path');
const { Worker, isMainThread, parentPort, workerData } = require('worker_threads');

// ---------------------------------------------------------------- parametry i stale
function wczytajParametry(sciezka) {
  const tekst = fs.readFileSync(sciezka, 'utf8');
  const P0 = JSON.parse(tekst), P = {};
  for (const [sek, zaw] of Object.entries(P0)) if (!sek.startsWith('_') && zaw && typeof zaw === 'object')
    for (const [k, v] of Object.entries(zaw)) if (v && typeof v === 'object' && 'value' in v) P[k] = v.value;
  return { tekst, P0, P };
}
function stale(P) {
  const R = P.scan_field_d / 2 - P.scan_center_tol - P.work_overhang;
  if (Math.abs(R - P.socket_zone_r) > 0.01) throw new Error('socket_zone_r ' + P.socket_zone_r + ' != wzor ' + R);
  const RP = P.plate_round_d / 2, kat = P.round_flat_angle * Math.PI / 180;
  return {
    R, SQ: P.socket_zone / 2, WALL: P.socket_wall_min, ZN: (P.plate_size - 2 * P.plate_corner_zone) / 2, S2: P.plate_size / 2,
    MD: P.marker_cone_d / 2, RM: R - P.marker_cone_d / 2, RD: P.code_dimple_d / 2, RDL: R - P.socket_wall_min,
    RP, FLAT: Math.sqrt(RP * RP - (P.round_flat_w / 2) ** 2), FC: Math.cos(kat), FS: Math.sin(kat),
    TAN: Math.tan(P.socket_wall_angle * Math.PI / 180), DEPTH: P.socket_depth, HOLE: P.socket_hole_d,
    CW: 3.6, CH: P.number_text_h, DPITCH: P.code_dimple_pitch,
  };
}
const EPS = 1e-9;
const zaokr = v => +(+v).toFixed(4);

// ---------------------------------------------------------------- geometria rzedow (odcinki poziome + promien)
function ksztaltyX(typ, xs) {      // bez y
  if (typ.t === 'T') return xs.map(x => ({ ax: x - (typ.l - typ.w) / 2, bx: x + (typ.l - typ.w) / 2, rad: typ.w / 2 }));
  return xs.map(x => ({ ax: x, bx: x, rad: typ.d / 2 }));
}
function minY(rows, SX, C) {       // najmniejsze y nowego rzedu, przy ktorym scianka do poprzednich rzedow >= WALL (takze po przekatnej)
  let y = -Infinity;
  for (let i = Math.max(0, rows.length - 4); i < rows.length; i++) for (const sp of rows[i].S) for (const sn of SX) {
    const need = sp.rad + sn.rad + C.WALL, gx = Math.max(0, sn.ax - sp.bx, sp.ax - sn.bx);
    if (gx < need) { const yy = sp.y + Math.sqrt(need * need - gx * gx); if (yy > y) y = yy; }
  }
  return y;
}
function miesciSie(SX, y, C) {     // strefa +-SQ, kolo R, kwadraty narozne
  for (const s of SX) {
    if (Math.abs(y) + s.rad > C.SQ + EPS) return false;
    const xe = Math.max(Math.abs(s.ax), Math.abs(s.bx));
    if (xe + s.rad > C.SQ + EPS) return false;
    if (Math.hypot(xe, y) + s.rad > C.R + EPS) return false;
    if (Math.hypot(Math.max(C.ZN - xe, 0), Math.max(C.ZN - Math.abs(y), 0)) < s.rad - EPS) return false;
  }
  return true;
}
function wzor(k, p) { const xs = []; for (let i = 0; i < k; i++) xs.push(zaokr((i - (k - 1) / 2) * p)); return xs; }
function doKwantu(y, q) { return zaokr(Math.ceil(y / q - 1e-7) * q); }
function rzad(typ, xs, y, p) {
  const S = ksztaltyX(typ, xs); for (const s of S) s.y = y;
  const r = { t: typ.t, x: xs, y, S };
  if (typ.t === 'T') { r.l = typ.l; r.w = typ.w; if (typ.podzial) r.podzial = true; } else { r.d = typ.d; r.p = p; }
  return r;
}
function xsRynienki(typ, C) { return typ.podzial ? [zaokr(-(typ.l / 2 + C.WALL / 2)), zaokr(typ.l / 2 + C.WALL / 2)] : [0]; }
// Rzad MIESZANY (R59, szkic wlasciciela): gniazda roznych srednic w jednym rzedzie; wzor symetryczny od lewej do prawej,
// np. [12.5, 12.5, 15, 12.5, 12.5]. W rzedzie odstep obrysow = scianka. Gniazda tej samej srednicy maja wspolne y, a kazda
// srednica opada osobno najnizej, jak pozwalaja scianki do poprzednich rzedow. W parametry.json sa to osobne wpisy rzedu
// o roznym y (K-05 g wymaga roznych y), wiec weryfikator i generator czytaja je bez zmian.
function xsMieszane(wz, C) {
  const xs = [0]; for (let i = 1; i < wz.length; i++) xs.push(xs[i - 1] + wz[i - 1] / 2 + wz[i] / 2 + C.WALL);
  const sr = (xs[0] + xs[xs.length - 1]) / 2; return xs.map(x => zaokr(x - sr));
}
function rzadMieszany(rows, wz, C, q, y0, bezKontroli) {
  const xs = xsMieszane(wz, C), ost = rows.length ? rows[rows.length - 1] : null;
  const sred = [...new Set(wz)].sort((a, b) => a - b), grupy = [];
  for (const d of sred) {
    const gx = xs.filter((_, i) => wz[i] === d), SX = gx.map(x => ({ ax: x, bx: x, rad: d / 2 }));
    const y = ost ? doKwantu(Math.max(minY(rows, SX, C), ost.y + q), q) : zaokr(y0 + (d - sred[0]) / 2);     // pierwszy rzad: spody rowno
    grupy.push({ d, x: gx, y, SX });
  }
  for (let i = 1; i < grupy.length; i++) while (grupy.slice(0, i).some(g => Math.abs(g.y - grupy[i].y) < q - 1e-9)) grupy[i].y = zaokr(grupy[i].y + q);
  if (!bezKontroli) for (const g of grupy) if (!miesciSie(g.SX, g.y, C)) return null;
  const S = []; for (const g of grupy) for (const s of g.SX) S.push({ ax: s.ax, bx: s.bx, rad: s.rad, y: g.y });
  return { t: 'M', wz, x: xs, y: Math.max(...grupy.map(g => g.y)), S, grupy: grupy.map(g => ({ d: g.d, x: g.x, y: g.y })) };
}
function splaszcz(rows) {          // rzad mieszany -> osobne rzedy jednej srednicy (kolejnosc po y)
  if (!rows.some(r => r.t === 'M')) return rows;
  const out = []; for (const r of rows) { if (r.t === 'M') for (const g of r.grupy) out.push(rzad({ t: 'r', d: g.d }, g.x, g.y)); else out.push(r); }
  return out.sort((a, b) => a.y - b.y);
}
// mozliwe nastepne rzedy danego typu: rynienka - 1 opcja; gniazda okragle - dla kazdego rozstawu i parzystosci najwieksza liczba, ktora sie miesci
function opcje(rows, typ, C, cfg, y0) {
  const out = [], q = cfg.kwant, ost = rows.length ? rows[rows.length - 1] : null;
  if (typ.t === 'M') { const r = rzadMieszany(rows, typ.wz, C, q, y0); if (r) out.push(r); return out; }
  const yDla = SX => (ost ? doKwantu(Math.max(minY(rows, SX, C), ost.y + q), q) : y0);
  if (typ.t === 'T') {
    const xs = xsRynienki(typ, C), SX = ksztaltyX(typ, xs), y = yDla(SX);
    if (miesciSie(SX, y, C)) out.push(rzad(typ, xs, y));
    return out;
  }
  const pmin = typ.d + C.WALL, rozstawy = [pmin];
  if (cfg.rozstawy === 'poprzedni') { if (ost && ost.t === 'r' && ost.p > pmin + 1e-6) rozstawy.push(ost.p); }
  else if (cfg.rozstawy === 'wszystkie') for (const d2 of cfg.srednice) if (d2 + C.WALL > pmin + 1e-6) rozstawy.push(d2 + C.WALL);
  for (const p of rozstawy) for (const par of [1, 0]) {
    let k = Math.floor((2 * C.SQ - typ.d) / p + 1e-9) + 1;
    if (k % 2 !== par) k--;
    for (; k >= 1; k -= 2) {
      const xs = wzor(k, p), SX = ksztaltyX(typ, xs), y = yDla(SX);
      if (miesciSie(SX, y, C)) { out.push(rzad(typ, xs, y, p)); break; }
    }
  }
  return out;
}
function zapasUkladu(rows, C) {    // najmniejszy zapas obrysu do kola i do strefy
  let z = Infinity;
  for (const r of rows) for (const s of r.S) {
    const xe = Math.max(Math.abs(s.ax), Math.abs(s.bx));
    z = Math.min(z, C.R - Math.hypot(xe, s.y) - s.rad, C.SQ - Math.abs(s.y) - s.rad, C.SQ - xe - s.rad);
  }
  return z;
}
function doParametrow(rows) {      // format ev_rows / mo_rows
  return rows.map(r => {
    if (r.t === 'T') { const o = { y: r.y, type: 'trough', l: r.l, w: r.w, x: r.x }; if (r.hole_count !== undefined) o.hole_count = r.hole_count; if (r.hole_pitch !== undefined) o.hole_pitch = r.hole_pitch; return o; }
    return { y: r.y, type: 'round', d: r.d, x: r.x };
  });
}
function zParametrow(rowsP) {      // rzedy z parametry.json -> postac wewnetrzna
  return rowsP.slice().sort((a, b) => a.y - b.y).map(r => {
    const typ = r.type === 'trough' ? { t: 'T', l: r.l, w: r.w } : { t: 'r', d: r.d };
    const o = rzad(typ, r.x.slice().sort((a, b) => a - b), r.y, r.type === 'round' && r.x.length > 1 ? zaokr(Math.abs(r.x[1] - r.x[0])) : undefined);
    if (r.hole_count !== undefined) o.hole_count = r.hole_count;
    if (r.hole_pitch !== undefined) o.hole_pitch = r.hole_pitch;
    return o;
  });
}
function wszystkieKsztalty(rows) { const S = []; for (const r of rows) for (const s of r.S) S.push(s); return S; }
function dPunkt(x, y, s) { return Math.hypot(Math.max(0, s.ax - x, x - s.bx), y - s.y) - s.rad; }
function sciankaMin(rows) {
  const S = wszystkieKsztalty(rows); let m = Infinity;
  for (let i = 0; i < S.length; i++) for (let j = i + 1; j < S.length; j++) {
    const d = Math.hypot(Math.max(0, S[j].ax - S[i].bx, S[i].ax - S[j].bx), S[i].y - S[j].y) - S[i].rad - S[j].rad; if (d < m) m = d;
  }
  return m;
}

// ---------------------------------------------------------------- stozki znacznikow
function bokiTrojkata(a, b, c) {
  const AB = Math.hypot(a.x - b.x, a.y - b.y), BC = Math.hypot(b.x - c.x, b.y - c.y), AC = Math.hypot(a.x - c.x, a.y - c.y);
  return { AB, BC, AC, min: Math.min(AB, BC, AC), roznica: Math.min(Math.abs(AB - BC), Math.abs(BC - AC), Math.abs(AB - AC)),
    pole: Math.abs((b.x - a.x) * (c.y - a.y) - (c.x - a.x) * (b.y - a.y)) / 2 };
}
function znacznikWazny(x, y, S, C, scianka) {
  if (Math.hypot(x, y) > C.RM + EPS) return false;
  if (Math.max(Math.abs(x), Math.abs(y)) + C.MD > C.SQ + EPS) return false;
  if (C.FLAT - (x * C.FC + y * C.FS) - C.MD < C.WALL - EPS) return false;          // K-61 f: sciecie okraglej
  for (const s of S) if (dPunkt(x, y, s) - C.MD < scianka - EPS) return false;
  return true;
}
// szuka trojki A (przod-lewo), B (tyl-lewo), C (tyl-prawo): najdluzszy najkrotszy bok, boki rozne o >= bokiMin
function szukajZnacznikow(rows, C, opcjeZ) {
  const o = Object.assign({ krok: 0.5, bokiMin: 5, scianka: C.WALL, cwiartki: true }, opcjeZ || {});
  const S = wszystkieKsztalty(rows), lim = C.SQ - C.MD, kand = [];
  for (let x = -lim; x <= lim + EPS; x += o.krok) for (let y = -lim; y <= lim + EPS; y += o.krok) {
    const px = zaokr(x), py = zaokr(y);
    if (znacznikWazny(px, py, S, C, o.scianka)) kand.push({ x: px, y: py });
  }
  if (kand.length < 3) return null;
  // w kazdej cwiartce zostaja punkty najdalsze od srodka: po 3 na kazde 2 stopnie kata (do ok. 135 punktow na cwiartke)
  const skrajne = (sx, sy) => {
    const kosze = new Map();
    for (const p of kand) {
      if (!(p.x * sx > 0 && p.y * sy > 0)) continue;
      const k = Math.floor(Math.atan2(Math.abs(p.y), Math.abs(p.x)) * 180 / Math.PI / 2);
      if (!kosze.has(k)) kosze.set(k, []);
      kosze.get(k).push(p);
    }
    const out = [];
    for (const l of kosze.values()) { l.sort((a, b) => Math.hypot(b.x, b.y) - Math.hypot(a.x, a.y)); out.push(...l.slice(0, 3)); }
    return out;
  };
  const ocen = (QA, QB, QC) => {
    let best = null;
    for (const a of QA) for (const b of QB) for (const c of QC) {
      if (a === b || b === c || a === c) continue;
      const t = bokiTrojkata(a, b, c);
      if (t.roznica < o.bokiMin - EPS || t.pole < 500) continue;
      const wynik = t.min + 1e-4 * t.pole;
      if (!best || wynik > best.wynik) best = { wynik, A: a, B: b, C: c, t };
    }
    return best;
  };
  let best = ocen(skrajne(-1, -1), skrajne(-1, 1), skrajne(1, 1)), konwencja = true;
  if (!best && !o.cwiartki) {      // awaryjnie: dowolne trzy punkty skrajne, etykiety zgodnie z ruchem wskazowek zegara, B naprzeciw najdluzszego boku
    konwencja = false;
    const Q = [].concat(skrajne(-1, -1), skrajne(-1, 1), skrajne(1, 1), skrajne(1, -1));
    let b2 = null;
    for (let i = 0; i < Q.length; i++) for (let j = i + 1; j < Q.length; j++) for (let k = j + 1; k < Q.length; k++) {
      const t = bokiTrojkata(Q[i], Q[j], Q[k]);
      if (t.roznica < o.bokiMin - EPS || t.pole < 500) continue;
      const wynik = t.min + 1e-4 * t.pole;
      if (!b2 || wynik > b2.wynik) b2 = { wynik, pts: [Q[i], Q[j], Q[k]] };
    }
    if (b2) {
      const [p, q, r] = b2.pts, d = [[Math.hypot(q.x - r.x, q.y - r.y), p, q, r], [Math.hypot(p.x - r.x, p.y - r.y), q, p, r], [Math.hypot(p.x - q.x, p.y - q.y), r, p, q]].sort((u, v) => v[0] - u[0])[0];
      let B = d[1], A = d[2], Cc = d[3];
      if ((B.x - A.x) * (Cc.y - B.y) - (B.y - A.y) * (Cc.x - B.x) > 0) { const tmp = A; A = Cc; Cc = tmp; }
      best = { A, B, C: Cc, t: bokiTrojkata(A, B, Cc) };
    }
  }
  if (!best) return null;
  const sc = p => Math.min(...S.map(s => dPunkt(p.x, p.y, s) - C.MD));
  return { A: [best.A.x, best.A.y], B: [best.B.x, best.B.y], C: [best.C.x, best.C.y], trojkat: best.t, konwencja,
    scianki: { A: sc(best.A), B: sc(best.B), C: sc(best.C) }, kandydatow: kand.length };
}
function znacznikiWazne(mk, rows, C, bokiMin) {
  if (!mk) return false;
  const S = wszystkieKsztalty(rows), pts = ['A', 'B', 'C'].map(c => ({ x: mk[c][0], y: mk[c][1] }));
  if (!pts.every(p => znacznikWazny(p.x, p.y, S, C, C.WALL))) return false;
  const t = bokiTrojkata(pts[0], pts[1], pts[2]);
  return t.roznica >= bokiMin - EPS && t.pole >= 500;
}

// ---------------------------------------------------------------- dolki kodu i cyfra plytki okraglej
function dolekWazny(x, y, S, M, C, zapas) {
  const z = zapas || 0;
  if (Math.hypot(x, y) > C.RDL + EPS) return -1;
  let m = Math.min(C.RDL - Math.hypot(x, y) + 1, C.FLAT - (x * C.FC + y * C.FS) - C.RD - C.WALL);       // sciecie K-61 f
  for (const s of S) m = Math.min(m, dPunkt(x, y, s) - C.RD - C.WALL);
  for (const p of M) m = Math.min(m, Math.hypot(x - p[0], y - p[1]) - C.MD - C.RD - 1.5);
  return m >= z - EPS ? m : -1;
}
function szukajDolkow(rows, mk, C, stare) {
  const S = wszystkieKsztalty(rows), M = ['A', 'B', 'C'].map(c => mk[c]);
  const ocen = pts => { let m = Infinity; for (const p of pts) { const v = dolekWazny(p[0], p[1], S, M, C); if (v < 0) return -1; m = Math.min(m, v); } return m; };
  if (stare) { const pts = ['A', 'B', 'C', 'D'].map(b => stare[b]); if (ocen(pts) >= 0) return { dolki: stare, bezZmian: true, zapas: ocen(pts) }; }
  const sx = stare ? (stare.A[0] + stare.D[0]) / 2 : 0, sy = stare ? (stare.A[1] + stare.D[1]) / 2 : -40;
  const p = C.DPITCH;
  // wzorce w kolejnosci od najczytelniejszego: rzad, kolumna, blok 2 x 2; potem dwie pary; na koncu cztery osobne dolki
  const wzorce = [['rzad', [[0, 0], [p, 0], [2 * p, 0], [3 * p, 0]]], ['kolumna', [[0, 0], [0, p], [0, 2 * p], [0, 3 * p]]], ['blok 2 x 2', [[0, 0], [p, 0], [0, p], [p, p]]]];
  const szukajWzorca = wz => {
    let best = null;
    for (let x = -44; x <= 44 + EPS; x += 0.5) for (let y = -44; y <= 44 + EPS; y += 0.5) {
      const pts = wz.map(d => [zaokr(x + d[0]), zaokr(y + d[1])]);
      const v = ocen(pts); if (v < 0) continue;
      const cx = pts.reduce((a, q) => a + q[0], 0) / pts.length, cy = pts.reduce((a, q) => a + q[1], 0) / pts.length;
      const wynik = Math.min(v, 1.0) - 0.002 * Math.hypot(cx - sx, cy - sy);    // zapas liczy sie do 1 mm ponad reguly, potem blisko dawnego miejsca
      if (!best || wynik > best.wynik) best = { wynik, pts, zapas: v };
    }
    return best;
  };
  const wynikZ = (pts, zapas, uklad) => ({ dolki: { A: pts[0], B: pts[1], C: pts[2], D: pts[3] }, bezZmian: false, zapas, uklad });
  let linia = null;
  for (const [nazwa, wz] of wzorce.slice(0, 2)) { const b = szukajWzorca(wz); if (b && (!linia || b.wynik > linia.b.wynik)) linia = { b, nazwa }; }
  if (linia) return wynikZ(linia.b.pts, linia.b.zapas, linia.nazwa);
  const blok = szukajWzorca(wzorce[2][1]); if (blok) return wynikZ(blok.pts, blok.zapas, 'blok 2 x 2');
  // dwie pary (A+B, C+D), kazda w rzedzie albo kolumnie co DPITCH; pary jak najblizej siebie
  const paryD = [];
  for (const wz of [[[0, 0], [p, 0]], [[0, 0], [0, p]]]) for (let x = -44; x <= 44 + EPS; x += 0.5) for (let y = -44; y <= 44 + EPS; y += 0.5) {
    const pts = wz.map(d => [zaokr(x + d[0]), zaokr(y + d[1])]); const v = ocen(pts); if (v >= 0) paryD.push({ pts, v });
  }
  let bp = null;
  for (let i = 0; i < paryD.length; i++) for (let j = i + 1; j < paryD.length; j++) {
    const a = paryD[i], b = paryD[j];
    let dmin = Infinity; for (const u of a.pts) for (const w of b.pts) dmin = Math.min(dmin, Math.hypot(u[0] - w[0], u[1] - w[1]));
    if (dmin < p - EPS) continue;
    const ca = [(a.pts[0][0] + a.pts[1][0]) / 2, (a.pts[0][1] + a.pts[1][1]) / 2], cb = [(b.pts[0][0] + b.pts[1][0]) / 2, (b.pts[0][1] + b.pts[1][1]) / 2];
    const wynik = Math.min(a.v, b.v, 0.5) - 0.01 * Math.hypot(ca[0] - cb[0], ca[1] - cb[1]) - 0.001 * Math.hypot((ca[0] + cb[0]) / 2 - sx, (ca[1] + cb[1]) / 2 - sy);
    if (!bp || wynik > bp.wynik) bp = { wynik, a, b };
  }
  if (bp) { const [pa, pb] = bp.a.pts[0][0] + bp.a.pts[0][1] * 1e-3 <= bp.b.pts[0][0] + bp.b.pts[0][1] * 1e-3 ? [bp.a, bp.b] : [bp.b, bp.a]; return wynikZ(pa.pts.concat(pb.pts), Math.min(pa.v, pb.v), 'dwie pary'); }
  // rzad albo kolumna 4 dolkow w rownych, ale wiekszych odstepach (np. w przerwach miedzy gniazdami); im ciasniej, tym lepiej
  let rozs = null;
  for (let pp = p + 0.5; pp <= 20 + EPS; pp += 0.5) for (const pion of [false, true]) {
    const b = szukajWzorca([0, 1, 2, 3].map(i => (pion ? [0, i * pp] : [i * pp, 0]))); if (!b) continue;
    const wynik = Math.min(b.zapas, 0.5) - 0.02 * pp;
    if (!rozs || wynik > rozs.wynik) rozs = { wynik, b, opis: (pion ? 'kolumna' : 'rzad') + ' co ' + pp };
  }
  if (rozs) return wynikZ(rozs.b.pts, rozs.b.zapas, rozs.opis);
  // cztery osobne dolki: kolejno miejsca o najwiekszym zapasie, co najmniej DPITCH od juz wybranych
  const poj = [];
  for (let x = -44; x <= 44 + EPS; x += 0.5) for (let y = -44; y <= 44 + EPS; y += 0.5) { const v = dolekWazny(zaokr(x), zaokr(y), S, M, C); if (v >= 0) poj.push({ pt: [zaokr(x), zaokr(y)], v }); }
  poj.sort((a, b) => Math.min(b.v, 0.5) - Math.min(a.v, 0.5) || a.pt[0] - b.pt[0] || a.pt[1] - b.pt[1]);
  const wyb = [];
  for (const k of poj) { if (wyb.every(w => Math.hypot(w.pt[0] - k.pt[0], w.pt[1] - k.pt[1]) >= p - EPS)) wyb.push(k); if (wyb.length === 4) break; }
  if (wyb.length < 4) return null;
  wyb.sort((a, b) => a.pt[0] - b.pt[0] || a.pt[1] - b.pt[1]);
  return wynikZ(wyb.map(w => w.pt), Math.min(...wyb.map(w => w.v)), 'cztery osobne');
}
function cyfraOcena(x, y, S, M, D, C, cel) {       // cel: {kolo, gniazdo, dolek, stozek}
  const q = { x0: x - C.CW / 2, x1: x + C.CW / 2, y0: y - C.CH / 2, y1: y + C.CH / 2 };
  const rc = Math.max(Math.hypot(q.x0, q.y0), Math.hypot(q.x0, q.y1), Math.hypot(q.x1, q.y0), Math.hypot(q.x1, q.y1));
  let m = cel.kolo - rc;
  const dp = (px, py) => Math.hypot(Math.max(q.x0 - px, 0, px - q.x1), Math.max(q.y0 - py, 0, py - q.y1));
  for (const s of S) m = Math.min(m, Math.hypot(Math.max(0, q.x0 - s.bx, s.ax - q.x1), Math.max(0, q.y0 - s.y, s.y - q.y1)) - s.rad - cel.gniazdo);
  for (const d of D) m = Math.min(m, dp(d[0], d[1]) - C.RD - cel.dolek);
  for (const p of M) m = Math.min(m, dp(p[0], p[1]) - C.MD - cel.stozek);
  return m;
}
function szukajCyfry(rows, mk, dolki, C, stara) {
  const S = wszystkieKsztalty(rows), M = ['A', 'B', 'C'].map(c => mk[c]), D = ['A', 'B', 'C', 'D'].map(b => dolki[b]);
  const twarde = { kolo: C.R, gniazdo: 3, dolek: 1.5, stozek: 1.5 }, docelowe = { kolo: C.R - 0.1, gniazdo: 3, dolek: 3, stozek: 3 };
  if (stara && cyfraOcena(stara[0], stara[1], S, M, D, C, twarde) >= -EPS) return { cyfra: stara, bezZmian: true };
  const sx = stara ? stara[0] : 35, sy = stara ? stara[1] : -26;
  for (const cel of [docelowe, twarde]) {
    let best = null;
    for (let x = -44; x <= 44 + EPS; x += 0.5) for (let y = -44; y <= 44 + EPS; y += 0.5) {
      const v = cyfraOcena(zaokr(x), zaokr(y), S, M, D, C, cel); if (v < -EPS) continue;
      const wynik = Math.min(v, 0.5) - 0.002 * Math.hypot(x - sx, y - sy);
      if (!best || wynik > best.wynik) best = { wynik, cyfra: [zaokr(x), zaokr(y)], zapas: v };
    }
    if (best) return { cyfra: best.cyfra, bezZmian: false, zapas: best.zapas, cel: cel === docelowe ? 'docelowy' : 'minimalny' };
  }
  return { cyfra: null, bezZmian: false, brak: true };
}

// ---------------------------------------------------------------- tryb "front": przeglad kolejnosci rzedow
function typyZKonfiguracji(cfg, C) {
  const typy = cfg.srednice.map((d, i) => ({ t: 'r', d, i }));
  typy.push(Object.assign({ t: 'T' }, cfg.rynienka));
  if (cfg.mieszane) {              // --mieszane: wszystkie symetryczne wzory 3-7 gniazd z co najmniej dwiema srednicami, ktore mieszcza sie w strefie
    const D = cfg.srednice;
    for (let k = 3; k <= 7; k++) {
      const pol = Math.ceil(k / 2), n = Math.pow(D.length, pol);
      for (let c = 0; c < n; c++) {
        const lewa = []; let v = c; for (let i = 0; i < pol; i++) { lewa.push(D[v % D.length]); v = Math.floor(v / D.length); }
        const wz = lewa.concat(lewa.slice(0, k - pol).reverse());
        if (new Set(wz).size < 2) continue;
        if (wz.reduce((a, b) => a + b, 0) + (k - 1) * C.WALL > 2 * C.SQ + EPS) continue;
        typy.push({ t: 'M', wz });
      }
    }
  }
  return typy;
}
function przegladZadania(C, cfg, zadania, postep) {
  const typy = typyZKonfiguracji(cfg, C), wyniki = new Map(), rows = [], cnt = new Array(cfg.srednice.length).fill(0);
  const rzedowSr = new Array(cfg.srednice.length).fill(0), idx = new Map(cfg.srednice.map((d, i) => [d, i]));
  let wezly = 0, yT = 0, stop = false, pominiete = 0;
  let memo = new Map();
  const dolicz = (o, zn) => {        // liczby gniazd i rzedow po dodaniu (zn = 1) albo zdjeciu (zn = -1) rzedu
    if (o.t === 'r') { const i = idx.get(o.d); cnt[i] += zn * o.x.length; rzedowSr[i] += zn; }
    else if (o.t === 'M') for (const g of o.grupy) { const i = idx.get(g.d); cnt[i] += zn * g.x.length; rzedowSr[i] += zn; }
    else if (zn > 0) yT = o.y;
  };
  const nazwaRzedu = r => (r.t === 'T' ? 'T' : r.t === 'M' ? 'M[' + r.wz.join('/') + ']' : 'fi' + r.d);
  // Ten sam stan (3 ostatnie rzedy, glebokosc, strona rynienki) osiagniety wczesniej z liczbami gniazd nie gorszymi dla
  // kazdego progu srednicy i z nie mniejszym zapasem: dalszy ciag dalby tylko uklady rowne albo zdominowane - pomijany.
  const znany = (jestT) => {
    let k = (jestT ? (yT < 0 ? 'P' : 'T') : 'N') + rows.length;
    for (let i = Math.max(0, rows.length - 3); i < rows.length; i++) { const r = rows[i]; k += '|' + (r.t === 'T' ? 'T' : r.t === 'M' ? 'M' + r.wz.join('/') + ':' + r.grupy.map(g => g.y).join('/') : r.d + ':' + r.x.length + ':' + r.p) + '@' + r.y; }
    const kum = cnt.slice(); for (let i = kum.length - 2; i >= 0; i--) kum[i] += kum[i + 1];
    const z = zapasUkladu(rows, C);
    let l = memo.get(k);
    if (l) { for (const e of l) if (e.z >= z - 1e-9 && e.kum.every((v, i) => v >= kum[i])) return true; }
    else memo.set(k, l = []);
    l.push({ kum, z });
    return false;
  };
  const zapisz = () => {
    // --dokladnie: liczy sie tylko uklad o dokladnie zadanej liczbie rzedow kazdej srednicy; kazda kolejnosc rzedow osobno
    if (cfg.dokladnie) { for (let i = 0; i < cfg.srednice.length; i++) if (rzedowSr[i] !== (cfg.dokladnie[cfg.srednice[i]] || 0)) return; }
    const klucz = cnt.join(',') + '|' + (yT < 0 ? 'przod' : 'tyl') + (cfg.dokladnie ? '|' + rows.map(nazwaRzedu).join(' ') : '');
    const zap = zapasUkladu(rows, C);
    let lista = wyniki.get(klucz); if (!lista) { lista = []; wyniki.set(klucz, lista); }
    if (lista.length >= cfg.alternatywy && zap <= lista[lista.length - 1].zap + 1e-9) return;
    const sig = rows.map(r => r.t === 'T' ? 'T' : r.t === 'M' ? nazwaRzedu(r) : r.d + 'x' + r.x.length + (r.p !== r.d + C.WALL ? 'p' + r.p : '')).join(' ');
    const ist = lista.findIndex(e => e.sig === sig);
    if (ist >= 0) { if (lista[ist].zap >= zap) return; lista.splice(ist, 1); }
    const plaskie = [];              // rzad mieszany zapisany jako osobne rzedy jednej srednicy
    for (const r of rows) { if (r.t === 'M') for (const g of r.grupy) plaskie.push({ t: 'r', d: g.d, x: g.x, y: g.y }); else plaskie.push({ t: r.t, d: r.d, l: r.l, w: r.w, p: r.p, podzial: r.podzial, x: r.x, y: r.y }); }
    lista.push({ zap, sig, rows: plaskie });
    lista.sort((a, b) => b.zap - a.zap); if (lista.length > cfg.alternatywy) lista.length = cfg.alternatywy;
  };
  const rek = (jestT) => {
    if (stop) return;
    if ((++wezly & 2047) === 0 && cfg.limitS && Date.now() - cfg.start > cfg.limitS * 1000) { stop = true; return; }
    if (cfg.memo && znany(jestT)) { pominiete++; return; }
    if (jestT && rows.length >= 2) zapisz();
    if (rows.length >= cfg.maxrzedow) return;
    for (const typ of typy) {
      if (typ.t === 'T' && jestT) continue;
      if (typ.t === 'r' && cfg.maxrz[typ.d] !== undefined && rzedowSr[typ.i] >= cfg.maxrz[typ.d]) continue;
      if (typ.t === 'M' && typ.wz.some(d => cfg.maxrz[d] !== undefined && rzedowSr[idx.get(d)] >= cfg.maxrz[d])) continue;
      for (const o of opcje(rows, typ, C, cfg, null)) {
        rows.push(o); dolicz(o, 1);
        rek(jestT || typ.t === 'T');
        dolicz(o, -1);
        rows.pop();
      }
    }
  };
  let zrobione = 0;
  for (const z of zadania) {
    if (stop) break;
    memo = new Map();
    const typ = typy[z.ti];
    for (const o of opcje([], typ, C, cfg, z.y0)) {
      rows.push(o); dolicz(o, 1);
      rek(typ.t === 'T');
      dolicz(o, -1);
      rows.pop();
    }
    if (!stop) { zrobione++; if (postep) postep(zrobione); }
  }
  return { wyniki: [...wyniki.entries()], wezly, pominiete, zrobione, niepelny: stop };
}
function odtworz(e) {              // wpis z przegladu -> rzedy z ksztaltami
  return e.rows.map(r => { const o = rzad(r.t === 'T' ? { t: 'T', l: r.l, w: r.w, podzial: r.podzial } : { t: 'r', d: r.d }, r.x, r.y, r.p); return o; });
}

// ---------------------------------------------------------------- program glowny
function argumenty(argv) {
  const opt = {}, poz = [];
  for (const a of argv) { const m = /^--([a-z0-9-]+)(?:=(.*))?$/i.exec(a); if (m) opt[m[1]] = m[2] === undefined ? true : m[2]; else poz.push(a); }
  return { opt, poz };
}
function pary(tekst) { const o = {}; if (tekst && tekst !== true) for (const cz of String(tekst).split(',')) { const [a, b] = cz.split(':'); o[+a] = +b; } return o; }

async function main() {
  const { opt, poz } = argumenty(process.argv.slice(2));
  const tryb = poz[0];
  if (tryb === 'front') return trybFront(opt);
  if (tryb === 'uloz') return trybUloz(poz[1], opt);
  console.log('Uzycie: node uklad_kolo_R59.js front --plytka=wieczorna|poranna [...]   albo   node uklad_kolo_R59.js uloz spec.json [...]  (opis w naglowku pliku)');
  process.exit(2);
}

async function trybFront(opt) {
  const { P } = wczytajParametry(opt.parametry || 'parametry.json'), C = stale(P);
  const plytka = opt.plytka; if (!['wieczorna', 'poranna'].includes(plytka)) throw new Error('--plytka=wieczorna|poranna');
  const pre = plytka === 'wieczorna' ? 'ev' : 'mo';
  const dom = plytka === 'wieczorna' ? [9, 12, 15] : [7.5, 10, 12.5, 15];
  const srednice = (opt.srednice ? String(opt.srednice).split(',').map(Number) : dom).sort((a, b) => a - b);
  let rynienka = { l: P[pre + '_trough_l'], w: P[pre + '_trough_w'] };
  if (opt.rynienka) { const cz = String(opt.rynienka).split('x').map(Number); rynienka = cz.length === 3 ? { l: cz[1], w: cz[2], podzial: true } : { l: cz[0], w: cz[1] }; }
  const t0 = Date.now();
  const cfg = { srednice, rynienka, maxrzedow: +(opt.maxrzedow || (plytka === 'wieczorna' ? 6 : 8)), krok: +(opt.krok || 0.1), kwant: +(opt.kwant || 0.05),
    rozstawy: opt.rozstawy || 'poprzedni', alternatywy: +(opt.alternatywy || 3), maxrz: pary(opt.maxrz), memo: opt.memo !== 'nie',
    limitS: opt['limit-s'] !== undefined ? +opt['limit-s'] : 240, start: t0, dokladnie: null, mieszane: !!opt.mieszane };
  // --dokladnie=10:2,12.5:2,15:1 - zestaw rzedow zadany z gory (ile rzedow ktorej srednicy, plus rynienka); narzedzie
  // dobiera kolejnosc rzedow i liczby gniazd; wynik: wszystkie kolejnosci, od najwiekszej liczby gniazd
  if (opt.dokladnie && opt.dokladnie !== true) {
    cfg.dokladnie = pary(opt.dokladnie); cfg.maxrz = Object.assign({}, cfg.dokladnie); cfg.memo = false;
    for (const d of srednice) if (cfg.maxrz[d] === undefined) cfg.maxrz[d] = 0;
    if (!opt.maxrzedow) cfg.maxrzedow = 1 + Object.values(cfg.dokladnie).reduce((a, b) => a + b, 0);
  }
  const typy = typyZKonfiguracji(cfg, C), zadania = [];
  // --t-pierwsza: rynienka jest pierwszym rzedem od przodu; --t-ymin=Y: jej srodek nie blizej przodu niz Y
  // (np. -33 zostawia przed rynienka miejsce na rzad 4 dolkow kodu plytki okraglej w y = -43,5)
  const tPierwsza = !!opt['t-pierwsza'], tYmin = opt['t-ymin'] !== undefined ? +opt['t-ymin'] : -Infinity;
  for (let ti = 0; ti < typy.length; ti++) {
    if (tPierwsza && typy[ti].t !== 'T') continue;
    const h = typy[ti].t === 'T' ? typy[ti].w : typy[ti].t === 'M' ? Math.max(...typy[ti].wz) : typy[ti].d, zakres = +(opt.zakres || 16);
    const yStart = doKwantu(Math.max(-C.SQ + h / 2, typy[ti].t === 'T' ? tYmin : -Infinity), cfg.kwant);
    for (let y0 = yStart; y0 <= -C.SQ + h / 2 + zakres + EPS; y0 += cfg.krok) zadania.push({ ti, y0: zaokr(y0) });
  }
  const nW = Math.max(1, Math.min(+(opt.watki || os.cpus().length), zadania.length));
  const paczki = Array.from({ length: nW }, () => []);
  zadania.forEach((z, i) => paczki[i % nW].push(z));
  const plikPostepu = opt.postep && opt.postep !== true ? opt.postep : 'postep_front_' + plytka + '.txt';
  console.log('front: plytka ' + plytka + ', srednice ' + srednice.join(' / ') + ', rynienka ' + (rynienka.podzial ? '2 x ' : '') + rynienka.l + ' x ' + rynienka.w +
    ', max rzedow ' + cfg.maxrzedow + (Object.keys(cfg.maxrz).length ? ' (max rzedow srednicy: ' + JSON.stringify(cfg.maxrz) + ')' : '') + ', start co ' + cfg.krok + ', kwant y ' + cfg.kwant +
    ', rozstawy: ' + cfg.rozstawy + (cfg.mieszane ? ', rzedy mieszane: ' + typy.filter(t => t.t === 'M').length + ' wzorow' : '') + ', pomijanie stanow powtorzonych: ' + (cfg.memo ? 'tak' : 'nie') + ', limit czasu ' + cfg.limitS + ' s; zadan ' + zadania.length + ', watkow ' + nW + '; postep: ' + plikPostepu);
  const gotowe = new Array(nW).fill(0); let ostatniZapis = 0;
  const czesci = await Promise.all(paczki.map((p, nr) => new Promise((res, rej) => {
    const w = new Worker(__filename, { workerData: { C, cfg, zadania: p } });
    w.on('message', m => {
      if (m && m.postep !== undefined) {
        gotowe[nr] = m.postep;
        if (Date.now() - ostatniZapis > 2000) { ostatniZapis = Date.now(); try { fs.writeFileSync(plikPostepu, 'zadan ' + gotowe.reduce((a, b) => a + b, 0) + ' / ' + zadania.length + ', czas ' + ((Date.now() - t0) / 1000).toFixed(0) + ' s\n'); } catch (e) { /* postep nie jest krytyczny */ } }
      } else res(m);
    });
    w.once('error', rej);
  })));
  const wszystko = new Map(); let wezly = 0, pominiete = 0, zrobione = 0, niepelny = false;
  for (const cz of czesci) {
    wezly += cz.wezly; pominiete += cz.pominiete; zrobione += cz.zrobione; if (cz.niepelny) niepelny = true;
    for (const [k, lista] of cz.wyniki) {
      const cel = wszystko.get(k) || []; for (const e of lista) { const i = cel.findIndex(x => x.sig === e.sig); if (i < 0) cel.push(e); else if (cel[i].zap < e.zap) cel[i] = e; }
      cel.sort((a, b) => b.zap - a.zap); cel.length = Math.min(cel.length, cfg.alternatywy); wszystko.set(k, cel);
    }
  }
  try { fs.writeFileSync(plikPostepu, 'koniec: zadan ' + zrobione + ' / ' + zadania.length + ', czas ' + ((Date.now() - t0) / 1000).toFixed(0) + ' s' + (niepelny ? ', PRZEGLAD NIEPELNY (limit czasu)' : '') + '\n'); } catch (e) { /* jw. */ }
  console.log('przejrzano ' + wezly + ' ukladow czesciowych (w tym ' + pominiete + ' pominietych jako powtorzone), roznych zestawow liczb: ' + wszystko.size + ', czas ' + ((Date.now() - t0) / 1000).toFixed(1) + ' s');
  if (niepelny) console.log('UWAGA: PRZEGLAD NIEPELNY - przekroczony limit czasu ' + cfg.limitS + ' s, ukonczone zadania ' + zrobione + ' / ' + zadania.length + '; wynik NIE jest pelnym przegladem (zawez --maxrz / --maxrzedow / --krok albo podnies --limit-s)');
  // filtry
  const fMin = pary(opt.min), fMax = pary(opt.max), fOd = pary(opt.minod), minRazem = +(opt.minrazem || 0);
  let wpisy = [];
  for (const [k, lista] of wszystko) {
    const [lic, strona, kolejnosc] = k.split('|'), cnt = lic.split(',').map(Number), razem = cnt.reduce((a, b) => a + b, 0);
    if (opt.strona && opt.strona !== strona) continue;
    if (razem < minRazem) continue;
    let ok = true;
    srednice.forEach((d, i) => { if (fMin[d] !== undefined && cnt[i] < fMin[d]) ok = false; if (fMax[d] !== undefined && cnt[i] > fMax[d]) ok = false; });
    for (const d of Object.keys(fOd).map(Number)) { let s = 0; srednice.forEach((dd, i) => { if (dd >= d - 1e-9) s += cnt[i]; }); if (s < fOd[d]) ok = false; }
    if (!ok) continue;
    const kum = cnt.map((_, i) => cnt.slice(i).reduce((a, b) => a + b, 0));        // ile gniazd o srednicy >= d_i
    wpisy.push({ klucz: k, cnt, kum, razem, strona, kolejnosc, lista, stan: null });
  }
  const top = +(opt.top || 60);
  const dominuje = (a, b) => a.kum.every((v, i) => v >= b.kum[i]) && a.kum.some((v, i) => v > b.kum[i]);
  const bokiMin = opt['boki-min'] !== undefined ? +opt['boki-min'] : 5;
  // front niezdominowany wsrod ukladow, dla ktorych istnieja znaczniki (uklad bez miejsca na 3 stozki odpada).
  // Kolejnosc malejaco po sumie progow: kazdy mozliwy dominujacy jest przed zdominowanym, wiec wystarcza jedno przejscie.
  const sumaK = w => w.kum.reduce((a, b) => a + b, 0);
  const front = []; let bezZnacznikow = 0;
  const zeZnacznikami = w => {
    for (const e of w.lista) {
      const rows = odtworz(e), mk = szukajZnacznikow(rows, C, { bokiMin });
      if (mk) { w.wybrany = e; w.rows = rows; w.mk = mk; break; }
    }
    if (w.mk) front.push(w); else bezZnacznikow++;
  };
  if (cfg.dokladnie) {
    // zestaw rzedow zadany: bez odsiewania zdominowanych; kolejnosc: najwiecej gniazd, potem wiecej duzych, potem wiekszy zapas
    const duze = (a, b) => { for (let i = a.kum.length - 1; i >= 0; i--) if (a.kum[i] !== b.kum[i]) return b.kum[i] - a.kum[i]; return 0; };
    wpisy.sort((a, b) => b.razem - a.razem || duze(a, b) || b.lista[0].zap - a.lista[0].zap);
    for (const w of wpisy) { if (front.length >= top) break; zeZnacznikami(w); }
  } else if (opt['najlepsze-wg'] !== undefined && opt['najlepsze-wg'] !== true) {
    // --najlepsze-wg=15: dla kazdej liczby gniazd podanej srednicy jeden uklad - najwiecej gniazd razem, przy remisie wiekszy zapas
    const iWg = srednice.indexOf(+opt['najlepsze-wg']); if (iWg < 0) throw new Error('--najlepsze-wg: srednica spoza --srednice');
    const liczbyWg = [...new Set(wpisy.map(w => w.cnt[iWg]))].sort((a, b) => a - b);
    for (const n of liczbyWg) {
      const kand = wpisy.filter(w => w.cnt[iWg] === n).sort((a, b) => b.razem - a.razem || b.lista[0].zap - a.lista[0].zap);
      const przed = front.length; for (const w of kand) { zeZnacznikami(w); if (front.length > przed) break; }
    }
  } else {
    wpisy.sort((a, b) => sumaK(b) - sumaK(a));
    for (const w of wpisy) { if (front.some(v => dominuje(v, w))) continue; zeZnacznikami(w); }
  }
  if (bezZnacznikow) console.log('odrzucone zestawy bez miejsca na 3 stozki znacznikow: ' + bezZnacznikow);
  const wszystkich = wpisy.length;
  wpisy = front;
  const wg = opt['najlepsze-wg'] !== undefined && opt['najlepsze-wg'] !== true;
  if (!cfg.dokladnie && !wg) wpisy.sort((a, b) => b.kum[b.kum.length - 1] - a.kum[a.kum.length - 1] || b.razem - a.razem || b.kum.join().localeCompare(a.kum.join()));
  if (wg) console.log('\nnajlepszy uklad dla kazdej liczby gniazd fi' + opt['najlepsze-wg'] + ' (najwiecej gniazd razem, przy remisie wiekszy zapas; ze znacznikami): ' + wpisy.length + '   [liczby gniazd: ' + srednice.map(d => 'fi' + d).join(' / ') + ']');
  else if (cfg.dokladnie) console.log('\nuklady o zadanym zestawie rzedow (' + JSON.stringify(cfg.dokladnie) + ' + rynienka): ' + wszystkich + ' par kolejnosc / liczby; pokazuje ' + wpisy.length + ' najlepszych ze znacznikami   [liczby gniazd: ' + srednice.map(d => 'fi' + d).join(' / ') + ']');
  else console.log('\nzestawy niezdominowane ze znacznikami: ' + wpisy.length + (wpisy.length > top ? ' (pokazuje ' + top + ')' : '') + '   [liczby gniazd: ' + srednice.map(d => 'fi' + d).join(' / ') + ']');
  const wynik = [];
  wpisy.slice(0, top).forEach((w, nr) => {
    const e = w.wybrany, t = w.mk.trojkat;
    console.log('#' + (nr + 1) + '  ' + w.cnt.join(' / ') + '  razem ' + w.razem + ' + ' + (rynienka.podzial ? '2 krotkie rynienki' : '1 rynienka') + ' (' + w.strona + ')  zapas do kola/strefy ' + e.zap.toFixed(2) + '  scianka min ' + sciankaMin(w.rows).toFixed(3) + (w.kolejnosc ? '  kolejnosc: ' + w.kolejnosc : ''));
    for (const r of e.rows.slice().sort((a, b) => a.y - b.y)) console.log('      ' + (r.t === 'T' ? 'rynienka ' + r.l + 'x' + r.w : 'fi' + r.d) + '  y=' + r.y + '  x' + r.x.length + ' [' + r.x.join(', ') + ']');
    if (/M\[/.test(e.sig)) console.log('      (rzad mieszany: ' + e.sig + ')');
    console.log('      znaczniki A(' + w.mk.A + ') B(' + w.mk.B + ') C(' + w.mk.C + ')  boki ' + t.AB.toFixed(1) + ' / ' + t.BC.toFixed(1) + ' / ' + t.AC.toFixed(1) + '  roznica ' + t.roznica.toFixed(1));
    wynik.push({ nr: nr + 1, liczby: Object.fromEntries(srednice.map((d, i) => [d, w.cnt[i]])), razem: w.razem, strona: w.strona, kolejnosc: w.kolejnosc, zapas: zaokr(e.zap), sig: e.sig,
      rows: doParametrow(w.rows), znaczniki: { A: w.mk.A, B: w.mk.B, C: w.mk.C } });
  });
  if (opt.wynik && opt.wynik !== true) fs.writeFileSync(opt.wynik, JSON.stringify({ plytka, cfg, wezly, pominiete, niepelny, zestawow: wszystko.size, front: wynik }, null, 1));
}

// ---------------------------------------------------------------- tryb "uloz": opis wariantu -> plik wariantu
// bezKontroli = true (diagnoza): rzedy ukladane ciasno, ale bez sprawdzania kola i strefy - do pomiaru, ile brakuje
function ulozRzedy(spec, P, C, q, bezKontroli) {
  const ok = (SX, y) => bezKontroli || miesciSie(SX, y, C);
  const buduj = y0 => {
    const rows = [];
    for (const rs of spec.rzedy) {
      if (rs.mieszany) {             // rzad mieszany: {"mieszany": [12.5, 12.5, 15, 12.5, 12.5]}
        const r = rzadMieszany(rows, rs.mieszany, C, q, y0, bezKontroli); if (!r) return null;
        rows.push(r); continue;
      }
      const jestT = rs.typ === 'T' || rs.type === 'trough';
      const typ = jestT ? { t: 'T', l: rs.l, w: rs.w, podzial: !!rs.podzial } : { t: 'r', d: rs.d };
      const ost = rows.length ? rows[rows.length - 1] : null;
      const yDla = SX => (rs.y !== undefined ? rs.y : ost ? doKwantu(Math.max(minY(rows, SX, C), ost.y + q), q) : y0);
      let wyb = null;
      if (jestT) { const xs = rs.x || xsRynienki(typ, C), SX = ksztaltyX(typ, xs), y = yDla(SX); if (ok(SX, y)) wyb = rzad(typ, xs, y); }
      else if (rs.x) { const xs = rs.x.slice().sort((a, b) => a - b), SX = ksztaltyX(typ, xs), y = yDla(SX); if (ok(SX, y)) wyb = rzad(typ, xs, y, rs.p); }
      else {
        const p = rs.p || typ.d + C.WALL;
        const proby = rs.k ? [rs.k] : Array.from({ length: 12 }, (_, i) => 12 - i);
        for (const k of proby) {
          const xs = wzor(k, p), SX = ksztaltyX(typ, xs), y = yDla(SX);
          if (!ok(SX, y)) continue;
          if (!wyb || k > wyb.x.length || (k === wyb.x.length && y < wyb.y)) wyb = rzad(typ, xs, y, p);
          if (rs.k || (wyb && k < wyb.x.length - 1)) break;
        }
      }
      if (!wyb) return null;
      if (rs.hole_count !== undefined) wyb.hole_count = rs.hole_count;
      if (rs.hole_pitch !== undefined) wyb.hole_pitch = rs.hole_pitch;
      rows.push(wyb);
    }
    return rows;
  };
  if (bezKontroli) return buduj(0);
  if (spec.y0 !== 'auto' && spec.y0 !== undefined) { const r = buduj(spec.y0); if (!r) throw new Error('rzedy nie mieszcza sie przy y0 = ' + spec.y0); return r; }
  let best = null;
  for (let y0 = -C.SQ; y0 <= 0; y0 = zaokr(y0 + q)) {
    const r = buduj(y0); if (!r) continue;
    const n = r.reduce((a, b) => a + b.x.length, 0), z = zapasUkladu(r, C);
    if (!best || n > best.n || (n === best.n && z > best.z + 1e-9)) best = { n, z, r, y0 };
  }
  if (!best) throw new Error('rzedy nie mieszcza sie przy zadnym y0');
  return best.r;
}

// Diagnoza (uloz --diagnoza): czy uklad DOKLADNIE ze spec (liczby gniazd w rzedach podane, rzedy ciasno) miesci sie przy
// jakimkolwiek przesunieciu calego bloku w y; jesli nie - ile mm wysokosci brakuje i ktore obrysy to ograniczaja.
// Kazdy obrys daje przedzial dozwolonego przesuniecia (strefa +-SQ i kolo R); czesc wspolna pusta = brak miejsca.
function diagnoza(spec, P, C, q) {
  const rows = ulozRzedy(spec, P, C, q, true);
  if (!rows) throw new Error('diagnoza: nie udalo sie ulozyc rzedow (podaj liczbe gniazd k w kazdym rzedzie)');
  let lo = -Infinity, hi = Infinity, ktoLo = '', ktoHi = '', zaSzeroki = null;
  const opis = (r, s) => (r.t === 'T' ? 'rynienka ' + r.l + 'x' + r.w : 'fi' + (2 * s.rad)) + ' (x ' + zaokr(Math.max(Math.abs(s.ax), Math.abs(s.bx))) + ')';
  for (const r of rows) for (const s of r.S) {
    const xe = Math.max(Math.abs(s.ax), Math.abs(s.bx));
    if (xe + s.rad > C.SQ + EPS || xe > C.R - s.rad) { zaSzeroki = opis(r, s); continue; }
    const hK = Math.sqrt((C.R - s.rad) ** 2 - xe * xe), hS = C.SQ - s.rad, h = Math.min(hK, hS), war = hK < hS ? 'kolo' : 'strefa';
    if (-h - s.y > lo) { lo = -h - s.y; ktoLo = opis(r, s) + ' - ' + war; }
    if (h - s.y < hi) { hi = h - s.y; ktoHi = opis(r, s) + ' - ' + war; }
  }
  console.log('diagnoza ' + spec.id + ': uklad doslownie wg spec, rzedy ciasno (scianka ' + C.WALL + '), y liczone od srodka pierwszego rzedu:');
  for (const r of splaszcz(rows)) console.log('  ' + (r.t === 'T' ? 'rynienka ' + r.l + 'x' + r.w : 'fi' + r.d) + '  y = +' + zaokr(r.y - rows[0].y) + '  x' + r.x.length + ' [' + r.x.join(', ') + ']');
  if (zaSzeroki) { console.log('  WERDYKT: NIE - rzad za szeroki: ' + zaSzeroki + ' nie miesci sie w strefie / kole przy zadnym y'); return; }
  const wys = zaokr(hi - lo);
  if (lo <= hi + EPS) console.log('  WERDYKT: TAK - miesci sie; pierwszy rzad moze lezec w y od ' + zaokr(lo + rows[0].y) + ' do ' + zaokr(hi + rows[0].y) + ' (zapas wysokosci ' + wys + ' mm)');
  else console.log('  WERDYKT: NIE - brakuje ' + zaokr(lo - hi) + ' mm wysokosci. Z przodu ogranicza: ' + ktoLo + ' (pierwszy rzad nie nizej niz y ' + zaokr(lo + rows[0].y) + '); z tylu ogranicza: ' + ktoHi + ' (pierwszy rzad nie wyzej niz y ' + zaokr(hi + rows[0].y) + ')');
}

function dopasujNawias(t, i) {
  let gl = 0, wNapisie = false;
  for (let j = i; j < t.length; j++) {
    const ch = t[j];
    if (wNapisie) { if (ch === '\\') j++; else if (ch === '"') wNapisie = false; continue; }
    if (ch === '"') wNapisie = true; else if (ch === '{' || ch === '[') gl++; else if (ch === '}' || ch === ']') { gl--; if (gl === 0) return j; }
  }
  throw new Error('niedomkniety nawias');
}
function podmien(tekst, klucz, wartoscTekst, opis) {       // podmienia "value" (i "opis") wpisu klucza, reszta pliku bez zmian
  const m = new RegExp('"' + klucz + '"\\s*:\\s*\\{').exec(tekst); if (!m) throw new Error('brak klucza ' + klucz);
  const start = m.index + m[0].length - 1, koniec = dopasujNawias(tekst, start);
  let ob = tekst.slice(start, koniec + 1);
  const mv = /"value"\s*:\s*/.exec(ob), vs = mv.index + mv[0].length;
  const ve = (ob[vs] === '{' || ob[vs] === '[') ? dopasujNawias(ob, vs) + 1 : vs + /^[^,}]+/.exec(ob.slice(vs))[0].length;
  ob = ob.slice(0, vs) + wartoscTekst + ob.slice(ve);
  if (opis !== undefined) {
    const zak = opis.replace(/\\/g, '\\\\').replace(/"/g, '\\"'), mo = /"opis"\s*:\s*"/.exec(ob);
    if (mo) { const os_ = mo.index + mo[0].length; let oe = os_; while (ob[oe] !== '"') { if (ob[oe] === '\\') oe++; oe++; } ob = ob.slice(0, os_) + zak + ob.slice(oe); }
    else ob = ob.slice(0, ob.length - 1) + ', "opis": "' + zak + '"}';
  }
  return tekst.slice(0, start) + ob + tekst.slice(koniec + 1);
}
function j1(v) {                 // JSON w jednej linii ze spacjami po przecinkach i dwukropkach (jak w parametry.json)
  if (Array.isArray(v)) return '[' + v.map(j1).join(', ') + ']';
  if (v && typeof v === 'object') return '{' + Object.keys(v).map(k => JSON.stringify(k) + ': ' + j1(v[k])).join(', ') + '}';
  return JSON.stringify(v);
}
function rowneGleboko(a, b) { return JSON.stringify(a) === JSON.stringify(b); }

async function trybUloz(plikSpec, opt) {
  if (!plikSpec) throw new Error('podaj plik spec.json');
  const spec = JSON.parse(fs.readFileSync(plikSpec, 'utf8'));
  const sciezkaP = opt.parametry || 'parametry.json';
  const { tekst, P0, P } = wczytajParametry(sciezkaP), C = stale(P);
  const plytka = spec.plytka; if (!['wieczorna', 'poranna'].includes(plytka)) throw new Error('spec.plytka = wieczorna | poranna');
  const pre = plytka === 'wieczorna' ? 'ev' : 'mo', q = +(opt.kwant || spec.kwant || 0.05), bokiMin = spec.boki_min !== undefined ? spec.boki_min : 5;
  // rzedy
  if (opt.diagnoza) { if (!spec.rzedy) throw new Error('--diagnoza wymaga "rzedy" w spec'); diagnoza(spec, P, C, q); return; }
  let rows;
  if (spec.rows) rows = zParametrow(spec.rows);
  else if (spec.rzedy) rows = splaszcz(ulozRzedy(spec, P, C, q));
  else throw new Error('spec wymaga "rzedy" albo "rows"');
  if (spec.dy) for (const r of rows) { r.y = zaokr(r.y + spec.dy); for (const s of r.S) s.y = r.y; }
  for (const r of rows) if (!miesciSie(r.S.map(s => ({ ax: s.ax, bx: s.bx, rad: s.rad })), r.y, C)) throw new Error('rzad y = ' + r.y + ' nie miesci sie w kole / strefie / narozniku');
  const sc = sciankaMin(rows); if (sc < C.WALL - 1e-6) throw new Error('scianka miedzy obrysami ' + sc.toFixed(3) + ' < ' + C.WALL);
  const nT = rows.filter(r => r.t === 'T').length; if (nT !== 1) throw new Error('uklad musi miec dokladnie 1 rzad z rynienka, ma ' + nT);
  // znaczniki
  const stareMk = P[pre + '_marker_pos']; let mk, zrodloMk;
  const zn = spec.znaczniki;
  if (zn && typeof zn === 'object') { mk = zn; zrodloMk = 'ze spec'; if (!znacznikiWazne(mk, rows, C, bokiMin)) throw new Error('znaczniki ze spec nie spelniaja regul'); }
  else if (zn === 'zostaw') { mk = stareMk; zrodloMk = 'bez zmian'; if (!znacznikiWazne(mk, rows, C, bokiMin)) throw new Error('dzisiejsze znaczniki nie spelniaja regul w tym ukladzie'); }
  else if (zn !== 'auto' && znacznikiWazne(stareMk, rows, C, bokiMin)) { mk = stareMk; zrodloMk = 'bez zmian (nadal wazne)'; }
  else {
    let w = szukajZnacznikow(rows, C, { bokiMin, krok: 0.5 }) || szukajZnacznikow(rows, C, { bokiMin, krok: 0.25 }) || szukajZnacznikow(rows, C, { bokiMin, krok: 0.25, cwiartki: false });
    if (!w) throw new Error('brak miejsca na 3 stozki znacznikow z regula bokow >= ' + bokiMin);
    mk = { A: w.A, B: w.B, C: w.C }; zrodloMk = 'policzone' + (w.konwencja ? '' : ' (POZA konwencja cwiartek A przod-lewo, B tyl-lewo, C tyl-prawo)');
  }
  // dolki okraglej
  const stareD = P.code_dimples_round[plytka]; let dolki, zrodloD;
  const dd = spec.dolki_okragle;
  if (dd && typeof dd === 'object') { dolki = dd; zrodloD = 'ze spec'; }
  else { const w = szukajDolkow(rows, mk, C, dd === 'auto' ? null : stareD); if (!w) throw new Error('brak miejsca na 4 dolki kodu plytki okraglej'); dolki = w.dolki; zrodloD = w.bezZmian ? 'bez zmian (nadal wazne)' : 'policzone (' + w.uklad + ', zapas ponad reguly ' + w.zapas.toFixed(2) + ')'; }
  // cyfra okraglej
  const staraC = P.number_pos_round[plytka]; let cyfra, zrodloC;
  const cc = spec.cyfra_okragla;
  if (cc === null || Array.isArray(cc)) { cyfra = cc; zrodloC = 'ze spec'; }
  else { const w = szukajCyfry(rows, mk, dolki, C, cc === 'auto' ? null : staraC); cyfra = w.cyfra; zrodloC = w.bezZmian ? 'bez zmian (nadal wazna)' : w.brak ? 'BRAK MIEJSCA - null (cyfra pominieta)' : 'policzona (cel ' + w.cel + ')'; }

  // wydruk
  const mix = {}; for (const r of rows) if (r.t === 'r') mix[r.d] = (mix[r.d] || 0) + r.x.length;
  const nOkr = Object.values(mix).reduce((a, b) => a + b, 0), nRyn = rows.filter(r => r.t === 'T').reduce((a, r) => a + r.x.length, 0);
  console.log('wariant ' + spec.id + ' (' + plytka + (spec.nazwa ? ', ' + spec.nazwa : '') + '): ' + nOkr + ' gniazd (' + Object.keys(mix).map(Number).sort((a, b) => a - b).map(d => mix[d] + ' x fi' + d).join(', ') + ') + ' + nRyn + ' rynienka/i; zapas do kola/strefy ' + zapasUkladu(rows, C).toFixed(3) + ', scianka min ' + sc.toFixed(3));
  for (const r of rows) console.log('  ' + (r.t === 'T' ? 'rynienka ' + r.l + 'x' + r.w : 'fi' + r.d) + '  y=' + r.y + '  x' + r.x.length + ' [' + r.x.join(', ') + ']');
  const t = bokiTrojkata(...['A', 'B', 'C'].map(c => ({ x: mk[c][0], y: mk[c][1] })));
  console.log('  znaczniki ' + zrodloMk + ': A(' + mk.A + ') B(' + mk.B + ') C(' + mk.C + '); boki ' + t.AB.toFixed(2) + ' / ' + t.BC.toFixed(2) + ' / ' + t.AC.toFixed(2) + ', roznica ' + t.roznica.toFixed(2));
  console.log('  dolki okraglej ' + zrodloD + ': ' + ['A', 'B', 'C', 'D'].map(b => b + '(' + dolki[b] + ')').join(' '));
  console.log('  cyfra okraglej ' + zrodloC + ': ' + (cyfra ? '(' + cyfra + ')' : 'null'));

  // plik wariantu: kopia parametry.json ze zmienionymi tylko kluczami ukladu
  const wyj = opt.wyjscie || ('parametry_wariant_' + spec.id + '.json');
  const rowsP = doParametrow(rows);
  const rzedyTekst = '[\n' + rowsP.map(r => '        ' + j1(r)).join(',\n') + '\n      ]';
  const opisR = 'R59 wariant ' + spec.id + (spec.nazwa ? ' (' + spec.nazwa + ')' : '') + ': ' + nOkr + ' gniazd (' + Object.keys(mix).map(Number).sort((a, b) => a - b).map(d => mix[d] + ' x fi' + d).join(', ') + ') + ' +
    (nRyn === 1 ? '1 rynienka' : nRyn + ' krotkie rynienki w jednym rzedzie (D3-b)') + '; policzone narzedzia/uklad_kolo_R59.js, sprawdzone narzedzia/weryfikuj_uklad_R59.js; PROPOZYCJA do bramki G0 - nie jest zrodlem prawdy';
  let nowy = podmien(tekst, pre + '_rows', rzedyTekst, opisR);
  const zmienione = [pre + '_rows'];
  if (!rowneGleboko(mk, stareMk)) { nowy = podmien(nowy, pre + '_marker_pos', j1({ A: mk.A, B: mk.B, C: mk.C }), 'R59 wariant ' + spec.id + ': srodki stozkow znacznikow; promien <= socket_zone_r - 2,5; scianka do gniazd >= 3; boki trojkata ' + t.AB.toFixed(2) + ' / ' + t.BC.toFixed(2) + ' / ' + t.AC.toFixed(2)); zmienione.push(pre + '_marker_pos'); }
  if (!rowneGleboko(dolki, stareD)) {
    const ob = Object.assign({}, P.code_dimples_round); ob[plytka] = { A: dolki.A, B: dolki.B, C: dolki.C, D: dolki.D };
    nowy = podmien(nowy, 'code_dimples_round', '{' + Object.keys(ob).map(k => '"' + k + '": ' + j1(ob[k])).join(',\n                                        ') + '}');
    zmienione.push('code_dimples_round.' + plytka);
  }
  if (!rowneGleboko(cyfra, staraC)) {
    const ob = Object.assign({}, P.number_pos_round); ob[plytka] = cyfra;
    nowy = podmien(nowy, 'number_pos_round', j1(ob)); zmienione.push('number_pos_round.' + plytka);
  }
  const ryn = rows.find(r => r.t === 'T');
  if (ryn.l !== P[pre + '_trough_l']) { nowy = podmien(nowy, pre + '_trough_l', String(ryn.l)); zmienione.push(pre + '_trough_l'); }
  if (ryn.w !== P[pre + '_trough_w']) { nowy = podmien(nowy, pre + '_trough_w', String(ryn.w)); zmienione.push(pre + '_trough_w'); }
  const meta = { id: spec.id, plytka, nazwa: spec.nazwa || '', zmienione_klucze: zmienione, zrodlo: 'narzedzia/uklad_kolo_R59.js uloz ' + path.basename(plikSpec), uwaga: 'propozycja R59-U do bramki G0; druga plytka w tym pliku = stan R54' };
  nowy = nowy.replace(/("_meta"\s*:\s*\{)/, '$1\n    "r59_wariant": ' + j1(meta) + ',');
  // kontrola: plik sie czyta i poza kluczami ukladu jest identyczny z parametry.json
  const N0 = JSON.parse(nowy), dozw = new Set([pre + '_rows', pre + '_marker_pos', 'code_dimples_round', 'number_pos_round', pre + '_trough_l', pre + '_trough_w']);
  for (const sek of Object.keys(P0)) {
    if (sek === '_meta') { const kopia = Object.assign({}, N0._meta); delete kopia.r59_wariant; if (!rowneGleboko(kopia, P0._meta)) throw new Error('_meta zmienione poza r59_wariant'); continue; }
    for (const k of Object.keys(P0[sek])) if (!dozw.has(k) && !rowneGleboko(P0[sek][k], N0[sek][k])) throw new Error('klucz ' + k + ' zmieniony, a nie powinien');
    if (Object.keys(P0[sek]).length !== Object.keys(N0[sek]).length) throw new Error('sekcja ' + sek + ': inna liczba kluczy');
  }
  fs.writeFileSync(wyj, nowy);
  console.log('  zapisano ' + wyj + '; zmienione klucze: ' + zmienione.join(', '));
}

// ---------------------------------------------------------------- start (na koncu pliku: wszystkie stale sa juz zainicjowane)
if (!isMainThread) {
  const { C, cfg, zadania } = workerData;
  parentPort.postMessage(przegladZadania(C, cfg, zadania, n => parentPort.postMessage({ postep: n })));
} else main().catch(e => { console.error('BLAD: ' + (e && e.message || e)); process.exit(2); });
