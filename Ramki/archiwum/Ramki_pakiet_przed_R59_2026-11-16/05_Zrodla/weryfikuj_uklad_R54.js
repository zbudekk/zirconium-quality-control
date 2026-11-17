// narzedzia/weryfikuj_uklad_R54.js — R54 (1.11.2026): sprawdza układ gniazd z parametry.json (ev_rows / mo_rows / *_marker_pos)
// względem koła socket_zone_r, kwadratu socket_zone, ścianek ≥ 3 i cech narożnych (dołki kodu). Odpowiada K‑05 (c), K‑16 [R54] na poziomie parametrów (bez STL).
// Użycie: node narzedzia/weryfikuj_uklad_R54.js [ścieżka parametry.json = ./parametry.json]
const fs = require('fs');
const P0 = JSON.parse(fs.readFileSync(process.argv[2] || 'parametry.json', 'utf8'));
const P = {}; for (const sek of Object.values(P0)) if (sek && typeof sek === 'object') for (const [k, v] of Object.entries(sek)) if (v && typeof v === 'object' && 'value' in v) P[k] = v.value;
const R = P.scan_field_d / 2 - P.scan_center_tol - P.work_overhang;
if (Math.abs(R - P.socket_zone_r) > 0.01) { console.error(`BŁĄD: socket_zone_r ${P.socket_zone_r} ≠ wzór ${R}`); process.exit(1); }
const SQ = P.socket_zone / 2, WALL = P.socket_wall_min, MD = P.marker_cone_d / 2, RM = R - MD;
const dimples = ['A', 'B', 'C'].map((b, i) => [P.code_dimple_x, P.code_dimple_y0 + i * P.code_dimple_pitch]);
const magnets = [[-(P.plate_size / 2 - P.marker_offset), -(P.plate_size / 2 - P.marker_offset)], [-(P.plate_size / 2 - P.marker_offset), P.plate_size / 2 - P.marker_offset], [P.plate_size / 2 - P.marker_offset, P.plate_size / 2 - P.marker_offset]];
function shapes(rows) { const s = []; for (const r of rows) for (const x of r.x) s.push(r.type === 'round' ? { a: [x, r.y], b: [x, r.y], rad: r.d / 2, name: `ø${r.d}@(${x}, ${r.y})` } : { a: [x - (r.l - r.w) / 2, r.y], b: [x + (r.l - r.w) / 2, r.y], rad: r.w / 2, name: `rynienka ${r.l}x${r.w}@(${x}, ${r.y})` }); return s; }
function dPS(p, a, b) { const vx = b[0] - a[0], vy = b[1] - a[1], L = vx * vx + vy * vy; let t = L ? ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / L : 0; t = Math.max(0, Math.min(1, t)); return Math.hypot(p[0] - a[0] - t * vx, p[1] - a[1] - t * vy); }
function dSS(s1, s2) { return Math.min(dPS(s1.a, s2.a, s2.b), dPS(s1.b, s2.a, s2.b), dPS(s2.a, s1.a, s1.b), dPS(s2.b, s1.a, s1.b)) - s1.rad - s2.rad; }
let ok = true;
function chk(cond, msg) { console.log(`  ${cond ? '✓' : '✗'} ${msg}`); if (!cond) ok = false; }
for (const [typ, rows, mk] of [['wieczorna', P.ev_rows, P.ev_marker_pos], ['poranna', P.mo_rows, P.mo_marker_pos]]) {
  console.log(`\n${typ.toUpperCase()} (R = ${R}, kwadrat ±${SQ})`);
  const S = shapes(rows);
  const nR = S.filter(s => !s.name.startsWith('ryn')).length, nT = S.length - nR;
  const mix = {}; for (const r of rows) if (r.type === 'round') mix[r.d] = (mix[r.d] || 0) + r.x.length;
  console.log(`  gniazda ${nR} + rynienki ${nT}; mieszanka ${JSON.stringify(mix)}`);
  let maxR = 0, worst = ''; let maxSq = 0;
  for (const s of S) for (const p of [s.a, s.b]) { const rr = Math.hypot(p[0], p[1]) + s.rad; if (rr > maxR) { maxR = rr; worst = s.name; } maxSq = Math.max(maxSq, Math.abs(p[0]) + s.rad, Math.abs(p[1]) + s.rad); }
  chk(maxR <= R + 1e-9, `max promień obrysu ${maxR.toFixed(3)} ≤ ${R} (${worst})`);
  chk(maxSq <= SQ + 1e-9, `max |x|+r, |y|+r ${maxSq.toFixed(2)} ≤ ${SQ}`);
  let wmin = 1e9, pair = '';
  for (let i = 0; i < S.length; i++) for (let j = i + 1; j < S.length; j++) { const d = dSS(S[i], S[j]); if (d < wmin) { wmin = d; pair = `${S[i].name} – ${S[j].name}`; } }
  chk(wmin >= WALL - 1e-6, `min ścianka gniazdo–gniazdo ${wmin.toFixed(3)} ≥ ${WALL} (${pair})`);
  for (const r of rows) { const a = r.x.slice().sort((p, q) => p - q), b = r.x.map(v => -v).sort((p, q) => p - q); chk(a.every((v, i) => Math.abs(v - b[i]) < 0.01), `rząd y=${r.y} symetryczny`); }
  for (const [nm, [mx, my]] of Object.entries(mk)) {
    const rr = Math.hypot(mx, my);
    let wm = 1e9, wn = ''; for (const s of S) { const d = dPS([mx, my], s.a, s.b) - s.rad - MD; if (d < wm) { wm = d; wn = s.name; } }
    const dd = Math.min(...dimples.map(d => Math.hypot(d[0] - mx, d[1] - my) - P.code_dimple_d / 2 - MD));
    const dm = Math.min(...magnets.map(m => Math.hypot(m[0] - mx, m[1] - my) - P.magnet_pocket_d / 2 - MD));
    chk(rr <= RM + 1e-9, `znacznik ${nm} (${mx}, ${my}): promień ${rr.toFixed(2)} ≤ ${RM}`);
    chk(wm >= WALL - 1e-6, `znacznik ${nm}: ścianka do gniazda ${wm.toFixed(2)} ≥ ${WALL} (${wn})`);
    chk(dd >= 1.5, `znacznik ${nm}: do dołka kodu ${dd.toFixed(2)} ≥ 1,5`);
    chk(dm >= 1.5, `znacznik ${nm}: do kieszeni magnesu (XY) ${dm.toFixed(2)} ≥ 1,5`);
  }
  let dg = 1e9; for (const d of dimples) for (const s of S) dg = Math.min(dg, dPS(d, s.a, s.b) - s.rad - P.code_dimple_d / 2);
  chk(dg >= 3, `dołek kodu–gniazdo ${dg.toFixed(2)} ≥ 3`);
}
console.log(ok ? '\nWYNIK: układ zgodny z R54 (K‑05 c, K‑16 na poziomie parametrów)' : '\nWYNIK: BŁĘDY — patrz ✗');
process.exit(ok ? 0 : 1);
