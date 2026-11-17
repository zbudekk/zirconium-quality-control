// narzedzia/uklad_kolo_R54.js — R54 (1.11.2026): przegląd układów gniazd w rzędach przyciętych do koła o promieniu R (socket_zone_r).
// Użycie: node narzedzia/uklad_kolo_R54.js [R=47] [minEv="4,5" = min ø15,ø12] [minMo="5,6" = min ø12,5,ø10] [ścianka znacznika=3]
// Wynik: 6 najlepszych układów na typ (liczba gniazd, mieszanka, rzędy y/x, pozycje znaczników A/B/C). Rzędy sąsiednie mogą być przesunięte (szachownica), ścianka 3 liczona po przekątnej.
// Wybrany układ (R = 47) jest wpisany w plan_ramki_v2.md D6 i parametry.json (ev_rows / mo_rows / ev_marker_pos / mo_marker_pos).

// Układ kołowy gniazd z przesunięciem rzędów (stagger) i wyszukaniem pozycji 3 znaczników.
const WALL = 3, SQ = 45;
const R = +(process.argv[2] || 47);
const RM = R - 2.5;            // promień środka znacznika ø5
const MW = +(process.argv[5] || 3); // ścianka znacznik–gniazdo
function pattern(k, p, odd) { const xs = []; for (let i = 0; i < k; i++) xs.push(odd ? (i - (k - 1) / 2) * p : (i - (k - 1) / 2) * p); return xs; }
function fits(t, xs, yc) {
  if (Math.abs(yc) + t.h / 2 > SQ + 1e-9) return false;
  if (t.t === 'T') { const a = (t.l - t.w) / 2; return Math.hypot(a, yc) + t.w / 2 <= R + 1e-9; }
  return xs.every(x => Math.abs(x) + t.d / 2 <= SQ + 1e-9 && Math.hypot(x, yc) + t.d / 2 <= R + 1e-9);
}
function minYc(prev, t, xs) {
  if (!prev) return -Infinity;
  const full = prev.yc + prev.t.h / 2 + t.h / 2 + WALL;
  if (prev.t.t === 'T' || t.t === 'T') return full;
  const need = prev.t.d / 2 + t.d / 2 + WALL;
  let dy = 0;
  for (const a of prev.x) for (const b of xs) { const dx = Math.abs(a - b); if (dx < need) dy = Math.max(dy, Math.sqrt(need * need - dx * dx)); }
  return prev.yc + dy;
}
function build(seq, y0) {
  const rows = []; let prev = null;
  for (const t of seq) {
    let best = null;
    if (t.t === 'T') {
      const yc = Math.max(y0, minYc(prev, t, [0]));
      if (!fits(t, [0], yc)) return null;
      best = { t, x: [0], yc };
    } else {
      const p = t.d + WALL;
      for (let k = 9; k >= 1; k--) {
        const xs = pattern(k, p, k % 2 === 1);
        const yc = Math.max(y0, minYc(prev, t, xs));
        if (fits(t, xs, yc)) { if (!best || k > best.x.length || (k === best.x.length && yc < best.yc)) best = { t, x: xs, yc }; break; }
      }
      if (!best) return null;
    }
    rows.push(best); prev = best; y0 = -Infinity;
  }
  return rows;
}
function shape(r, x) { return r.t.t === 'T' ? { a: [x - (r.t.l - r.t.w) / 2, r.yc], b: [x + (r.t.l - r.t.w) / 2, r.yc], rad: r.t.w / 2 } : { a: [x, r.yc], b: [x, r.yc], rad: r.t.d / 2 }; }
function dPS(p, a, b) { const vx = b[0] - a[0], vy = b[1] - a[1], L = vx * vx + vy * vy; let t = L ? ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / L : 0; t = Math.max(0, Math.min(1, t)); return Math.hypot(p[0] - a[0] - t * vx, p[1] - a[1] - t * vy); }
function markers(rows) {
  const shapes = []; for (const r of rows) for (const x of r.x) shapes.push(shape(r, x));
  const out = {};
  for (const [name, sx, sy] of [['A', -1, -1], ['B', -1, 1], ['C', 1, 1]]) {
    let best = null;
    for (let x = 2.5; x <= SQ - 2.5; x += 0.5) for (let y = 2.5; y <= SQ - 2.5; y += 0.5) {
      const px = sx * x, py = sy * y, rr = Math.hypot(px, py);
      if (rr > RM + 1e-9) continue;
      let ok = true;
      for (const s of shapes) if (dPS([px, py], s.a, s.b) - s.rad - 2.5 < MW - 1e-9) { ok = false; break; }
      if (ok && (!best || rr > best.r)) best = { x: px, y: py, r: rr };
    }
    if (!best) return null; out[name] = best;
  }
  return out;
}
function* seqs(types, nT, maxLen) {
  const rnd = types.filter(t => t.t !== 'T'), T = types.find(t => t.t === 'T');
  function* rec(cur) { const nt = cur.filter(t => t.t === 'T').length; if (cur.length && nt === nT) yield cur; if (cur.length >= maxLen) return; for (const t of rnd) yield* rec([...cur, t]); if (nt < nT) yield* rec([...cur, T]); }
  yield* rec([]);
}
function run(name, types, nT, maxLen, mixOk) {
  const res = []; const seen = new Set();
  for (const s of seqs(types, nT, maxLen)) {
    let best = null;
    for (let y0 = -R + s[0].h / 2; y0 <= 0; y0 += 0.25) {
      const rows = build(s, y0); if (!rows) continue;
      const n = rows.reduce((q, r) => q + (r.t.t === 'T' ? 0 : r.x.length), 0);
      if (!best || n > best.n) best = { n, rows };
    }
    if (!best) continue;
    const mix = {}; for (const r of best.rows) if (r.t.t !== 'T') mix[r.t.d] = (mix[r.t.d] || 0) + r.x.length;
    const bonus = mixOk(mix); if (bonus === null) continue;
    const key = best.rows.map(r => `${r.t.t}${r.t.d || ''}@${r.yc.toFixed(2)}:${r.x.length}`).join('|');
    if (seen.has(key)) continue; seen.add(key);
    const mk = markers(best.rows);
    res.push({ score: best.n + bonus + (mk ? 0 : -100), n: best.n, mix, mk, rows: best.rows });
  }
  res.sort((a, b) => b.score - a.score);
  console.log(`\n=== ${name} R=${R} (znacznik r≤${RM}, ścianka ≥${MW}) ===`);
  for (const r of res.slice(0, 6)) {
    console.log(`${r.n} ${JSON.stringify(r.mix)} wys. ${(r.rows[0].yc - r.rows[0].t.h / 2).toFixed(2)}…${(r.rows.at(-1).yc + r.rows.at(-1).t.h / 2).toFixed(2)}`);
    for (const w of r.rows) console.log(`   ${w.t.t === 'T' ? 'T' + w.t.l + 'x' + w.t.w : 'ø' + w.t.d} y=${w.yc.toFixed(2)} ×${w.x.length} x=[${w.x.map(v => +v.toFixed(2)).join(', ')}]`);
    console.log('   znaczniki: ' + (r.mk ? Object.entries(r.mk).map(([k, v]) => `${k}(${v.x},${v.y}) r=${v.r.toFixed(1)}`).join(' ') : 'BRAK MIEJSCA'));
  }
}
const EV = [{ t: 'r', d: 9, h: 9 }, { t: 'r', d: 12, h: 12 }, { t: 'r', d: 15, h: 15 }, { t: 'T', l: 60, w: 15, h: 15 }];
const MO = [{ t: 'r', d: 7.5, h: 7.5 }, { t: 'r', d: 10, h: 10 }, { t: 'r', d: 12.5, h: 12.5 }, { t: 'T', l: 50, w: 13, h: 13 }];
const minEv = (process.argv[3] || '4,5').split(',').map(Number), minMo = (process.argv[4] || '5,6').split(',').map(Number);
run('WIECZORNA', EV, 2, 7, m => ((m[15] || 0) >= minEv[0] && (m[12] || 0) >= minEv[1]) ? 0.2 * Math.min(m[15] || 0, 5) + 0.1 * Math.min(m[12] || 0, 9) : null);
run('PORANNA', MO, 2, 8, m => ((m[12.5] || 0) >= minMo[0] && (m[10] || 0) >= minMo[1]) ? 0.2 * Math.min(m[12.5] || 0, 6) + 0.1 * Math.min(m[10] || 0, 7) : null);
