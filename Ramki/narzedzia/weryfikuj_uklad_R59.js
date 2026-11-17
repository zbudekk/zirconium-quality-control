// narzedzia/weryfikuj_uklad_R59.js - R59 (14.11.2026): sprawdza uklad gniazd plytek z parametry.json albo z pliku wariantu
// (R59_szkice/parametry_wariant_<id>.json) na poziomie parametrow, bez STL. Rozszerzenie weryfikuj_uklad_R54.js.
//
// Uzycie:  node narzedzia/weryfikuj_uklad_R59.js [plik = parametry.json] [przelaczniki]
//   --r54                 stare reguly ukladu R54: oczekiwane 2 rzedy z rynienka, regula bokow trojkata tylko informacyjnie
//   --rzedy-rynienek=N    ile rzedow z rynienka ma miec plytka (domyslnie 1; z --r54: 2; "dowolnie" = bez reguly)
//   --boki-min=X          boki trojkata znacznikow rozne parami o >= X mm (domyslnie 5; 0 = tylko informacja)
//   --kabsch-min=X        reszta najlepszego BLEDNEGO przypisania A/B/C (Kabsch 2D bez odbicia, jak plate.py) >= X mm (domyslnie 5)
//   --plytka=wieczorna|poranna|obie   ktora plytke sprawdzac (domyslnie: _meta.r59_wariant.plytka z pliku, a gdy go brak - obie)
//   --prog-mostu=20       PROG_MOSTU_MM z synth.py: dno rynienki musi byc dluzsze (inaczej nie przyjmie zadnego mostu)
//   --cyfra-szer=3.6      szerokosc obrysu cyfry reliefu (wysokosc = number_text_h)
//   --json=plik           zapis podsumowania liczbowego (do tabel i szkicow)
// Wynik: linie "OK" / "BLAD" / "UWAGA" / "info"; kod wyjscia 0 = bez bledu, 1 = sa bledy, 2 = zly plik.
//
// Co sprawdza (dla plytki wieczornej i porannej; kwadrat i okragla biora te same rzedy - K-05 h):
//  1. K-05: liczby, symetria rzedow wzgledem x = 0, strefa +-socket_zone/2, kolo socket_zone_r, kwadraty narozne
//     plate_corner_zone, scianka miedzy obrysami >= socket_wall_min, kolejnosc rzedow (dwa wpisy o tym samym y = blad K-05 g).
//  2. Rynienki: dokladnie 1 rzad z rynienka (1 dluga = D3-a albo 2 krotkie w jednym rzedzie = D3-b), otwory w dnie
//     (liczba i rozstaw: z rzedu "hole_count" / "hole_pitch", inaczej trough_hole_count / ev|mo_trough_hole_pitch),
//     dlugosc dna a prog mostu.
//  3. Stozki znacznikow (K-16): promien srodka <= socket_zone_r - d/2, strefa, scianka do gniazd >= socket_wall_min,
//     do dolkow kodu >= 1,5, do kieszeni magnesow (XY) >= 1,5, do krawedzi >= 1,5; trojkat: boki rozne o >= 5 mm
//     (regula planu R59 pkt 6.4) i zapas przypisania A/B/C liczony tak, jak robi to program (Kabsch bez odbicia).
//  4. Kwadrat: 4 dolki kodu (A, B, C i D z code_bit_d_pos): gniazdo - dolek >= 3, dolek - krawedz >= 1,5;
//     cyfra i wyciecie D w rogu przod-prawo: odstep od gniazd >= 3.
//  5. Okragla (K-16, K-61 f, K-62): gniazdo - krawedz (okrag i sciecie) >= 1,5; scianka sciecie - obrysy gniazd,
//     rynienek, dolkow i stozkow >= 3; dolki code_dimples_round: promien <= socket_zone_r - socket_wall_min, do gniazd >= 3,
//     do stozkow >= 1,5, do krawedzi >= 1,5, miedzy dolkami >= 1; cyfra number_pos_round: obrys w kole socket_zone_r,
//     od gniazd >= 3, od dolkow i stozkow >= 1,5 (null = cyfra pominieta).
'use strict';
const fs = require('fs');

const opt = {}, poz = [];
for (const a of process.argv.slice(2)) {
  const m = /^--([a-z0-9-]+)(?:=(.*))?$/i.exec(a);
  if (m) opt[m[1]] = m[2] === undefined ? true : m[2]; else poz.push(a);
}
const sciezka = poz[0] || 'parametry.json';
let P0;
try { P0 = JSON.parse(fs.readFileSync(sciezka, 'utf8')); } catch (e) { console.error('BLAD: nie mozna wczytac ' + sciezka + ': ' + e.message); process.exit(2); }
const P = {};
for (const [sek, zaw] of Object.entries(P0)) if (!sek.startsWith('_') && zaw && typeof zaw === 'object')
  for (const [k, v] of Object.entries(zaw)) if (v && typeof v === 'object' && 'value' in v) P[k] = v.value;
const WYMAGANE = ['scan_field_d', 'scan_center_tol', 'work_overhang', 'socket_zone_r', 'socket_zone', 'socket_wall_min', 'socket_depth',
  'socket_wall_angle', 'socket_hole_d', 'plate_size', 'plate_corner_zone', 'marker_cone_d', 'marker_offset', 'magnet_pocket_d',
  'code_dimple_d', 'code_dimple_x', 'code_dimple_y0', 'code_dimple_pitch', 'code_bit_d_pos', 'notch_size', 'number_text_h',
  'number_pos_x', 'number_pos_y', 'plate_round_d', 'round_flat_w', 'round_flat_angle', 'code_dimples_round', 'number_pos_round',
  'trough_hole_count', 'ev_trough_hole_pitch', 'mo_trough_hole_pitch', 'ev_rows', 'mo_rows', 'ev_marker_pos', 'mo_marker_pos'];
const brak = WYMAGANE.filter(k => !(k in P));
if (brak.length) { console.error('BLAD: w pliku brak kluczy: ' + brak.join(', ')); process.exit(2); }

const wariant = (P0._meta && P0._meta.r59_wariant) || null;
const R54 = !!opt.r54;
const RZEDY_T = opt['rzedy-rynienek'] !== undefined ? String(opt['rzedy-rynienek']) : (R54 ? '2' : '1');
const BOKI_MIN = opt['boki-min'] !== undefined ? +opt['boki-min'] : (R54 ? 0 : 5);
const KABSCH_MIN = opt['kabsch-min'] !== undefined ? +opt['kabsch-min'] : 5;
const PROG_MOSTU = opt['prog-mostu'] !== undefined ? +opt['prog-mostu'] : 20;
const CYFRA_W = opt['cyfra-szer'] !== undefined ? +opt['cyfra-szer'] : 3.6;
const KTORA = opt.plytka || (wariant && wariant.plytka) || 'obie';
if (!['wieczorna', 'poranna', 'obie'].includes(KTORA)) { console.error('BLAD: --plytka=wieczorna|poranna|obie'); process.exit(2); }

const TOL = 1e-6;
const R = P.scan_field_d / 2 - P.scan_center_tol - P.work_overhang;      // socket_zone_r (LICZONE)
const SQ = P.socket_zone / 2, WALL = P.socket_wall_min;
const ZN = (P.plate_size - 2 * P.plate_corner_zone) / 2;                // 35: od tej wspolrzednej zaczyna sie kwadrat narozny
const MD = P.marker_cone_d / 2, RM = R - MD;
const S2 = P.plate_size / 2;
const RD = P.code_dimple_d / 2;
const TAN = Math.tan(P.socket_wall_angle * Math.PI / 180);
const RP = P.plate_round_d / 2, FLAT_DIST = Math.sqrt(RP * RP - (P.round_flat_w / 2) ** 2);
const FC = Math.cos(P.round_flat_angle * Math.PI / 180), FS = Math.sin(P.round_flat_angle * Math.PI / 180);
const CYFRA_H = P.number_text_h;

let nBlad = 0, nOk = 0, nUwag = 0;
const f = (v, n) => (Math.abs(v) < 5e-7 ? 0 : v).toFixed(n === undefined ? 2 : n);
function chk(cond, msg) { console.log('  ' + (cond ? 'OK   ' : 'BLAD ') + msg); if (cond) nOk++; else nBlad++; return cond; }
function info(msg) { console.log('  info ' + msg); }
function uwaga(msg) { console.log('  UWAGA ' + msg); nUwag++; }

// ---- geometria ----
function dPS(p, a, b) { const vx = b[0] - a[0], vy = b[1] - a[1], L = vx * vx + vy * vy; let t = L ? ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / L : 0; t = Math.max(0, Math.min(1, t)); return Math.hypot(p[0] - a[0] - t * vx, p[1] - a[1] - t * vy); }
// odleglosc obrysow dwoch ksztaltow (odcinek osi + promien); odcinki sa poziome i rozlaczne albo wspolliniowe, wiec wystarcza konce
function dSS(s1, s2) { return Math.min(dPS(s1.a, s2.a, s2.b), dPS(s1.b, s2.a, s2.b), dPS(s2.a, s1.a, s1.b), dPS(s2.b, s1.a, s1.b)) - s1.rad - s2.rad; }
function dKS(p, r, s) { return dPS(p, s.a, s.b) - s.rad - r; }                        // kolo (srodek p, promien r) - ksztalt
function prostokat(cx, cy, w, h) { return { x0: cx - w / 2, x1: cx + w / 2, y0: cy - h / 2, y1: cy + h / 2 }; }
function dProstPunkt(q, p) { return Math.hypot(Math.max(q.x0 - p[0], 0, p[0] - q.x1), Math.max(q.y0 - p[1], 0, p[1] - q.y1)); }
function dProstKsztalt(q, s) {                                                         // prostokat - ksztalt (odcinek poziomy)
  const ax = Math.min(s.a[0], s.b[0]), bx = Math.max(s.a[0], s.b[0]), y = s.a[1];
  return Math.hypot(Math.max(0, q.x0 - bx, ax - q.x1), Math.max(0, q.y0 - y, y - q.y1)) - s.rad;
}
function doKrawOkr(x, y, r) { return Math.min(RP - Math.hypot(x, y), FLAT_DIST - (x * FC + y * FS)) - r; }   // okragla: okrag i sciecie
function doSciecia(x, y, r) { return FLAT_DIST - (x * FC + y * FS) - r; }

// reszta dopasowania Kabscha 2D bez odbicia (jak stanowisko/plate.py: kabsch_2d): B ~ R*A + t
function kabschRms(A, B) {
  const n = A.length, ca = [0, 0], cb = [0, 0];
  for (let i = 0; i < n; i++) { ca[0] += A[i][0] / n; ca[1] += A[i][1] / n; cb[0] += B[i][0] / n; cb[1] += B[i][1] / n; }
  let sc = 0, ss = 0;
  for (let i = 0; i < n; i++) { const ax = A[i][0] - ca[0], ay = A[i][1] - ca[1], bx = B[i][0] - cb[0], by = B[i][1] - cb[1]; sc += ax * bx + ay * by; ss += ax * by - ay * bx; }
  const th = Math.atan2(ss, sc), c = Math.cos(th), s = Math.sin(th);
  let e = 0;
  for (let i = 0; i < n; i++) { const ax = A[i][0] - ca[0], ay = A[i][1] - ca[1], bx = B[i][0] - cb[0], by = B[i][1] - cb[1]; e += (c * ax - s * ay - bx) ** 2 + (s * ax + c * ay - by) ** 2; }
  return Math.sqrt(e / n);
}

// ---- ksztalty z rzedow (kolejnosc i numery id jak generuj_gniazda w ramka_generator.py) ----
function ksztaltyZRzedow(rows, pre) {
  const bledy = [];
  if (!Array.isArray(rows) || !rows.length) return { S: [], bledy: ['brak rzedow'], wiersze: [] };
  rows.forEach((r, i) => {
    if (!r || typeof r !== 'object') { bledy.push('rzad ' + i + ': nie jest obiektem'); return; }
    if (!Number.isFinite(r.y)) bledy.push('rzad ' + i + ': brak liczby y');
    if (!Array.isArray(r.x) || !r.x.length || !r.x.every(Number.isFinite)) bledy.push('rzad ' + i + ': zla lista x');
    if (r.type === 'round') { if (!(r.d > 0)) bledy.push('rzad ' + i + ': round bez d'); }
    else if (r.type === 'trough') { if (!(r.l > 0) || !(r.w > 0) || !(r.l > r.w)) bledy.push('rzad ' + i + ': trough wymaga l > w > 0'); }
    else bledy.push('rzad ' + i + ': nieznany type ' + r.type);
  });
  if (bledy.length) return { S: [], bledy, wiersze: [] };
  const wiersze = rows.map((r, i) => ({ r, i })).sort((a, b) => a.r.y - b.r.y || a.i - b.i).map(o => o.r);   // sortowanie stabilne po y
  const S = []; let id = 1;
  for (const r of wiersze) for (const x of r.x.slice().sort((a, b) => b - a)) {
    if (r.type === 'round') S.push({ id, typ: 'round', d: r.d, x, y: r.y, a: [x, r.y], b: [x, r.y], rad: r.d / 2, rzad: r, nazwa: 'fi' + r.d + ' id' + id + ' (' + x + '; ' + r.y + ')' });
    else S.push({ id, typ: 'trough', l: r.l, w: r.w, x, y: r.y, a: [x - (r.l - r.w) / 2, r.y], b: [x + (r.l - r.w) / 2, r.y], rad: r.w / 2, rzad: r,
      nazwa: 'rynienka ' + r.l + 'x' + r.w + ' id' + id + ' (' + x + '; ' + r.y + ')',
      hole_count: r.hole_count !== undefined ? r.hole_count : P.trough_hole_count,
      hole_pitch: r.hole_pitch !== undefined ? r.hole_pitch : P[pre + '_trough_hole_pitch'] });
    id++;
  }
  return { S, bledy, wiersze };
}

const podsumowanie = { plik: sciezka, wariant, reguly: { r54: R54, rzedy_rynienek: RZEDY_T, boki_min: BOKI_MIN, kabsch_min: KABSCH_MIN, prog_mostu: PROG_MOSTU }, plytki: {} };

console.log('weryfikuj_uklad_R59: ' + sciezka + (wariant ? '  [plik wariantu ' + wariant.id + ': plytka ' + wariant.plytka + ']' : ''));
console.log('reguly: ' + (R54 ? 'R54 (stary uklad)' : 'R59') + '; rzedy z rynienka = ' + RZEDY_T + '; boki trojkata rozne o >= ' + BOKI_MIN + (BOKI_MIN ? '' : ' (tylko informacja)') +
  '; kolo R = ' + R + ', strefa +-' + SQ + ', scianka >= ' + WALL + '; sprawdzane plytki: ' + KTORA);
chk(Math.abs(R - P.socket_zone_r) <= 0.01, 'socket_zone_r ' + P.socket_zone_r + ' = scan_field_d/2 - scan_center_tol - work_overhang = ' + R);
if (wariant && KTORA !== 'obie') info('plik wariantu zmienia tylko plytke ' + wariant.plytka + '; druga plytka w tym pliku to stan R54 i nie jest tu sprawdzana (--plytka=obie wymusza)');

function sprawdzPlytke(typ, pre) {
  console.log('\n=== PLYTKA ' + typ.toUpperCase() + ' (kwadrat ' + P.plate_size + ' i okragla fi' + P.plate_round_d + '; rzedy ' + pre + '_rows) ===');
  const wynik = podsumowanie.plytki[typ] = {};
  const { S, bledy, wiersze } = ksztaltyZRzedow(P[pre + '_rows'], pre);
  if (!chk(!bledy.length, 'rzedy poprawnie zapisane' + (bledy.length ? ': ' + bledy.join('; ') : ' (' + wiersze.length + ' wpisow)'))) return;
  const okr = S.filter(s => s.typ === 'round'), ryn = S.filter(s => s.typ === 'trough');

  // ---- 1. liczby ----
  console.log(' [1] liczby i K-05');
  const mix = {}; for (const s of okr) mix[s.d] = (mix[s.d] || 0) + 1;
  const srednice = Object.keys(mix).map(Number).sort((a, b) => a - b);
  info('gniazda okragle ' + okr.length + ' (' + srednice.map(d => mix[d] + ' x fi' + d).join(', ') + ') + rynienki ' + ryn.length + ' = ' + S.length + ' miejsc');
  wynik.gniazda = mix; wynik.okragle = okr.length; wynik.razem = S.length;
  wynik.rzedy = wiersze;

  // ---- K-05 (b) symetria rzedow (grupa po y) ----
  const grupy = new Map();
  for (const s of S) { const k = Math.round(s.y * 1e6) / 1e6; if (!grupy.has(k)) grupy.set(k, []); grupy.get(k).push(s.x); }
  const niesym = [];
  for (const [y, xs] of grupy) { const a = xs.slice().sort((p, q) => p - q), b = xs.map(v => -v).sort((p, q) => p - q); if (!a.every((v, i) => Math.abs(v - b[i]) <= 0.01)) niesym.push(y); }
  chk(!niesym.length, 'K-05 b: kazdy z ' + grupy.size + ' rzedow symetryczny wzgledem x = 0' + (niesym.length ? ' - NIE dla y = ' + niesym.join(', ') : ''));
  // dwa wpisy o tym samym y: generator numeruje je osobno i K-05 (g) zglasza blad kolejnosci id
  const yWpisow = wiersze.map(r => Math.round(r.y * 1e6) / 1e6);
  const dubl = yWpisow.filter((y, i) => yWpisow.indexOf(y) !== i);
  chk(!dubl.length, 'K-05 g: kazdy wpis rzedu ma inne y (id rzedami od przodu)' + (dubl.length ? ' - powtorzone y = ' + [...new Set(dubl)].join(', ') : ''));
  const powt = [];
  for (const r of wiersze) { const xs = r.x.slice().sort((a, b) => a - b); for (let i = 1; i < xs.length; i++) if (Math.abs(xs[i] - xs[i - 1]) < 1e-9) powt.push(r.y); }
  chk(!powt.length, 'brak powtorzonych x w rzedzie' + (powt.length ? ' - y = ' + powt.join(', ') : ''));

  // ---- K-05 (c) strefa i kolo ----
  let maxR = 0, ktoR = '', maxSq = 0, ktoSq = '';
  for (const s of S) for (const p of [s.a, s.b]) {
    const rr = Math.hypot(p[0], p[1]) + s.rad; if (rr > maxR) { maxR = rr; ktoR = s.nazwa; }
    const q = Math.max(Math.abs(p[0]), Math.abs(p[1])) + s.rad; if (q > maxSq) { maxSq = q; ktoSq = s.nazwa; }
  }
  chk(maxR <= R + TOL, 'K-05 c: max promien obrysu ' + f(maxR, 3) + ' <= ' + R + ' (' + ktoR + '); zapas ' + f(R - maxR, 3));
  chk(maxSq <= SQ + TOL, 'K-05 c: max |x|+r, |y|+r = ' + f(maxSq, 3) + ' <= ' + SQ + ' (' + ktoSq + ')');
  wynik.max_promien = +maxR.toFixed(4); wynik.max_promien_kto = ktoR; wynik.max_strefa = +maxSq.toFixed(4);
  // ---- K-05 (d) kwadraty narozne ----
  const wRogu = [];
  for (const s of S) for (let i = 0; i <= 200; i++) {
    const t = i / 200, x = s.a[0] + t * (s.b[0] - s.a[0]), y = s.a[1];
    if (Math.hypot(Math.max(ZN - Math.abs(x), 0), Math.max(ZN - Math.abs(y), 0)) < s.rad - TOL) { wRogu.push(s.nazwa); break; }
  }
  chk(!wRogu.length, 'K-05 d: zaden obrys nie wchodzi w kwadrat narozny ' + P.plate_corner_zone + ' mm (|x| > ' + ZN + ' i |y| > ' + ZN + ')' + (wRogu.length ? ' - NIE: ' + wRogu.join(', ') : ''));
  // ---- K-05 (e) scianki ----
  let wmin = Infinity, para = '';
  for (let i = 0; i < S.length; i++) for (let j = i + 1; j < S.length; j++) { const d = dSS(S[i], S[j]); if (d < wmin) { wmin = d; para = S[i].nazwa + ' - ' + S[j].nazwa; } }
  if (S.length > 1) chk(wmin >= WALL - TOL, 'K-05 e: min scianka miedzy obrysami ' + f(wmin, 3) + ' >= ' + WALL + ' (' + para + ')');
  wynik.min_scianka = +wmin.toFixed(4); wynik.min_scianka_para = para;

  // ---- 2. rynienki ----
  console.log(' [2] rynienki');
  const yRyn = [...new Set(ryn.map(s => Math.round(s.y * 1e6) / 1e6))];
  wynik.rzedy_rynienek = yRyn.length;
  wynik.d3 = yRyn.length === 1 ? (ryn.length === 1 ? 'a' : 'b') : null;
  if (RZEDY_T === 'dowolnie') info('rzedow z rynienka: ' + yRyn.length + ' (regula wylaczona)');
  else {
    chk(yRyn.length === +RZEDY_T, 'rzedow z rynienka: ' + yRyn.length + ' (oczekiwane dokladnie ' + RZEDY_T + (R54 ? ', reguly R54' : ', zlecenie R59 pkt 4') + ')' +
      (yRyn.length ? '; y = ' + yRyn.join(', ') + (yRyn.length === 1 ? (yRyn[0] < 0 ? ' (przednia)' : ' (tylna)') : '') : ''));
    if (!R54 && yRyn.length === 1) chk(ryn.length <= 2, 'rynienek w tym rzedzie: ' + ryn.length + (ryn.length === 1 ? ' (D3-a: jedna dluga)' : ryn.length === 2 ? ' (D3-b: rynienka podzielona na dwie krotkie)' : ' (najwyzej 2)'));
  }
  for (const s of ryn) {
    const dnoL = s.l - 2 * P.socket_depth * TAN, dnoW = s.w - 2 * P.socket_depth * TAN;
    const n = s.hole_count, pt = s.hole_pitch;
    const skrajny = (n - 1) / 2 * pt;                         // srodek skrajnego otworu od srodka rynienki
    const zapas = dnoL / 2 - skrajny - P.socket_hole_d / 2;   // od krawedzi otworu do konca dna (na osi)
    chk(Number.isInteger(n) && n >= 1 && pt > 0 && zapas >= 1.5 - TOL, s.nazwa + ': ' + n + ' otwory fi' + P.socket_hole_d + ' co ' + pt + ' (skrajny ' + f(skrajny, 1) + ' od srodka), dno ' + f(dnoL) + ' x ' + f(dnoW) + ', od otworu do konca dna ' + f(zapas) + ' >= 1,5');
    if (n > 1) chk(pt - P.socket_hole_d >= 1.5 - TOL, s.nazwa + ': mostek miedzy otworami ' + f(pt - P.socket_hole_d) + ' >= 1,5');
    if (n !== 4) uwaga(s.nazwa + ': ' + n + ' otwory zamiast 4 - generator ma 4 zaszyte w sondach K-08 (ramka_generator.py: for k in (-1.5, -0.5, 0.5, 1.5)); wymaga zmiany kodu (R59-A)' + (n % 2 ? '; liczba nieparzysta = otwor w srodku rynienki, a K-08 sonduje tam material' : ''));
    chk(dnoL > PROG_MOSTU + TOL, s.nazwa + ': dlugosc dna ' + f(dnoL) + ' > prog mostu ' + PROG_MOSTU + ' mm (PROG_MOSTU_MM w synth.py); praca do ok. ' + f(dnoL, 1) + ' mm lezy na dnie, do ' + f(dnoL + 2 * 1.5 * TAN, 1) + ' mm po uniesieniu 1,5');
    s.dno_l = +dnoL.toFixed(3);
  }
  wynik.rynienki = ryn.map(s => ({ id: s.id, l: s.l, w: s.w, x: s.x, y: s.y, dno_l: s.dno_l, hole_count: s.hole_count, hole_pitch: s.hole_pitch }));

  // ---- 3. znaczniki ----
  console.log(' [3] stozki znacznikow (K-16) i trojkat');
  const mk = P[pre + '_marker_pos'];
  const dolkiKw = ['A', 'B', 'C'].map((b, i) => ({ bit: b, x: P.code_dimple_x, y: P.code_dimple_y0 + i * P.code_dimple_pitch }));
  dolkiKw.push({ bit: 'D', x: P.code_bit_d_pos[0], y: P.code_bit_d_pos[1] });
  const mo = S2 - P.marker_offset;
  const magnesy = [[-mo, -mo], [-mo, mo], [mo, mo]];
  const dolkiOkrObj = P.code_dimples_round[typ];
  const dolkiOkrOk = !!dolkiOkrObj && ['A', 'B', 'C', 'D'].every(b => Array.isArray(dolkiOkrObj[b]) && dolkiOkrObj[b].length === 2 && dolkiOkrObj[b].every(Number.isFinite)) && Object.keys(dolkiOkrObj).length === 4;
  const dolkiOkr = dolkiOkrOk ? ['A', 'B', 'C', 'D'].map(b => ({ bit: b, x: dolkiOkrObj[b][0], y: dolkiOkrObj[b][1] })) : [];
  const mkOk = !!mk && ['A', 'B', 'C'].every(c => Array.isArray(mk[c]) && mk[c].length === 2 && mk[c].every(Number.isFinite)) && Object.keys(mk).length === 3;
  chk(mkOk, pre + '_marker_pos: klucze A, B, C z para liczb');
  const M = mkOk ? ['A', 'B', 'C'].map(c => ({ c, x: mk[c][0], y: mk[c][1] })) : [];
  wynik.znaczniki = {};
  for (const m of M) {
    const rr = Math.hypot(m.x, m.y);
    let wm = Infinity, wn = ''; for (const s of S) { const d = dKS([m.x, m.y], MD, s); if (d < wm) { wm = d; wn = s.nazwa; } }
    const dd = Math.min(...dolkiKw.map(d => Math.hypot(d.x - m.x, d.y - m.y) - RD - MD));
    const dm = Math.min(...magnesy.map(q => Math.hypot(q[0] - m.x, q[1] - m.y) - P.magnet_pocket_d / 2 - MD));
    const kKw = S2 - Math.max(Math.abs(m.x), Math.abs(m.y)) - MD, kOk = doKrawOkr(m.x, m.y, MD);
    const strefa = Math.max(Math.abs(m.x), Math.abs(m.y)) + MD;
    chk(rr <= RM + TOL, 'znacznik ' + m.c + ' (' + m.x + '; ' + m.y + '): promien srodka ' + f(rr) + ' <= ' + RM);
    chk(strefa <= SQ + TOL, 'znacznik ' + m.c + ': obrys w strefie, max |x|+r, |y|+r = ' + f(strefa) + ' <= ' + SQ);
    chk(wm >= WALL - TOL, 'znacznik ' + m.c + ': scianka do gniazda ' + f(wm) + ' >= ' + WALL + ' (' + wn + ')');
    chk(dd >= 1.5 - TOL, 'znacznik ' + m.c + ': do dolka kodu kwadratu ' + f(dd) + ' >= 1,5');
    chk(dm >= 1.5 - TOL, 'znacznik ' + m.c + ': do kieszeni magnesu (XY) ' + f(dm) + ' >= 1,5');
    chk(kKw >= 1.5 - TOL && kOk >= 1.5 - TOL, 'znacznik ' + m.c + ': do krawedzi kwadratu ' + f(kKw) + ' i okraglej ' + f(kOk) + ' >= 1,5');
    wynik.znaczniki[m.c] = { x: m.x, y: m.y, promien: +rr.toFixed(3), scianka: +wm.toFixed(3), do: wn };
  }
  if (M.length === 3) {
    let dmm = Infinity; for (let i = 0; i < 3; i++) for (let j = i + 1; j < 3; j++) dmm = Math.min(dmm, Math.hypot(M[i].x - M[j].x, M[i].y - M[j].y) - 2 * MD);
    chk(dmm >= WALL - TOL, 'znaczniki miedzy soba: scianka ' + f(dmm) + ' >= ' + WALL);
    const AB = Math.hypot(M[0].x - M[1].x, M[0].y - M[1].y), BC = Math.hypot(M[1].x - M[2].x, M[1].y - M[2].y), AC = Math.hypot(M[0].x - M[2].x, M[0].y - M[2].y);
    const roznica = Math.min(Math.abs(AB - BC), Math.abs(BC - AC), Math.abs(AB - AC));
    const pole = Math.abs((M[1].x - M[0].x) * (M[2].y - M[0].y) - (M[2].x - M[0].x) * (M[1].y - M[0].y)) / 2;
    const txt = 'trojkat znacznikow: AB ' + f(AB) + ', BC ' + f(BC) + ', AC ' + f(AC) + '; najmniejsza roznica bokow ' + f(roznica);
    if (BOKI_MIN > 0) chk(roznica >= BOKI_MIN - TOL, txt + ' >= ' + BOKI_MIN + ' (regula planu R59 pkt 6.4)');
    else { info(txt + ' (regula bokow wylaczona)'); if (roznica < 5) uwaga('boki trojkata rozne o mniej niz 5 mm (' + f(roznica) + ') - nowa regula R59 nie bylaby spelniona; o jednoznacznosci przypisania decyduje wiersz nizej'); }
    // najlepsze BLEDNE przypisanie: 5 permutacji innych niz tozsamosc, Kabsch bez odbicia (plate.py: przypisz_znaczniki)
    const pts = M.map(m => [m.x, m.y]); let druga = Infinity, ktora = '';
    for (const perm of [[0, 2, 1], [1, 0, 2], [2, 1, 0], [1, 2, 0], [2, 0, 1]]) { const e = kabschRms(perm.map(i => pts[i]), pts); if (e < druga) { druga = e; ktora = perm.map(i => 'ABC'[i]).join(''); } }
    chk(druga >= KABSCH_MIN - TOL, 'przypisanie A/B/C jednoznaczne: reszta najlepszego blednego przypisania (' + ktora + ' zamiast ABC, Kabsch bez odbicia) ' + f(druga) + ' mm >= ' + KABSCH_MIN + ' (program przyjmuje reszte <= 0,3)');
    chk(pole >= 500, 'trojkat znacznikow nie jest zdegenerowany: pole ' + f(pole, 0) + ' mm2 >= 500');
    wynik.trojkat = { AB: +AB.toFixed(3), BC: +BC.toFixed(3), AC: +AC.toFixed(3), roznica: +roznica.toFixed(3), pole: +pole.toFixed(1), kabsch_druga: +druga.toFixed(3) };
  }

  // ---- 4. kwadrat ----
  console.log(' [4] plytka kwadratowa: dolki kodu, cyfra, wyciecie D');
  let dg = Infinity, dgn = '';
  for (const d of dolkiKw) for (const s of S) { const v = dKS([d.x, d.y], RD, s); if (v < dg) { dg = v; dgn = 'dolek ' + d.bit + ' - ' + s.nazwa; } }
  chk(dg >= 3 - TOL, 'kwadrat: gniazdo - dolek kodu (A, B, C, D) ' + f(dg) + ' >= 3 (' + dgn + ')');
  const dke = Math.min(...dolkiKw.map(d => S2 - Math.max(Math.abs(d.x), Math.abs(d.y)) - RD));
  chk(dke >= 1.5 - TOL, 'kwadrat: dolek - krawedz plytki ' + f(dke) + ' >= 1,5');
  const cyfKw = prostokat(P.number_pos_x, P.number_pos_y, CYFRA_W, CYFRA_H);
  let dc = Infinity, dcn = ''; for (const s of S) { const v = dProstKsztalt(cyfKw, s); if (v < dc) { dc = v; dcn = s.nazwa; } }
  chk(dc >= 3 - TOL, 'kwadrat: cyfra (' + P.number_pos_x + '; ' + P.number_pos_y + ', obrys ' + CYFRA_W + ' x ' + CYFRA_H + ') - gniazdo ' + f(dc) + ' >= 3 (' + dcn + ')');
  const wyc = { x0: S2 - P.notch_size, x1: S2, y0: -S2, y1: -(S2 - P.notch_size) };
  let dw = Infinity, dwn = ''; for (const s of S) { const v = dProstKsztalt(wyc, s); if (v < dw) { dw = v; dwn = s.nazwa; } }
  chk(dw >= 3 - TOL, 'kwadrat: wyciecie D - gniazdo ' + f(dw) + ' >= 3 (' + dwn + ')');
  wynik.kwadrat = { dolek_gniazdo: +dg.toFixed(3), cyfra_gniazdo: +dc.toFixed(3) };

  // ---- 5. okragla ----
  console.log(' [5] plytka okragla fi' + P.plate_round_d + ': krawedz, sciecie (K-61 f), dolki (K-62), cyfra');
  let wk = Infinity, wkn = ''; for (const s of S) for (const p of [s.a, s.b]) { const v = doKrawOkr(p[0], p[1], s.rad); if (v < wk) { wk = v; wkn = s.nazwa; } }
  chk(wk >= 1.5 - TOL, 'okragla K-16: gniazdo/rynienka - krawedz (okrag i sciecie) ' + f(wk) + ' >= 1,5 (' + wkn + ')');
  chk(dolkiOkrOk, 'code_dimples_round.' + typ + ': klucze A, B, C, D z para liczb');
  const obrysy = [];
  for (const s of S) for (const p of [s.a, s.b]) obrysy.push([s.nazwa, p[0], p[1], s.rad]);
  for (const d of dolkiOkr) obrysy.push(['dolek ' + d.bit, d.x, d.y, RD]);
  for (const m of M) obrysy.push(['stozek ' + m.c, m.x, m.y, MD]);
  let ws = Infinity, wsn = ''; for (const [nz, x, y, r] of obrysy) { const v = doSciecia(x, y, r); if (v < ws) { ws = v; wsn = nz; } }
  chk(ws >= WALL - TOL, 'okragla K-61 f: scianka sciecie orientacyjne (cieciwa ' + P.round_flat_w + ', ' + P.round_flat_angle + ' st., ' + f(FLAT_DIST, 3) + ' od srodka) - obrysy ' + f(ws) + ' >= ' + WALL + ' (' + wsn + ')');
  wynik.okragla = { gniazdo_krawedz: +wk.toFixed(3), sciecie: +ws.toFixed(3), sciecie_kto: wsn, dolki: {}, cyfra: null };
  const rmaxDl = R - WALL;
  for (const d of dolkiOkr) {
    const rr = Math.hypot(d.x, d.y);
    let wg = Infinity, wgn = ''; for (const s of S) { const v = dKS([d.x, d.y], RD, s); if (v < wg) { wg = v; wgn = s.nazwa; } }
    const wz = M.length ? Math.min(...M.map(m => Math.hypot(d.x - m.x, d.y - m.y) - MD - RD)) : Infinity;
    const wkr = doKrawOkr(d.x, d.y, RD);
    chk(rr <= rmaxDl + TOL && wg >= WALL - TOL && wz >= 1.5 - TOL && wkr >= 1.5 - TOL, 'okragla K-62: dolek ' + d.bit + ' (' + d.x + '; ' + d.y + '): promien ' + f(rr) + ' <= ' + rmaxDl + ', do gniazda ' + f(wg) + ' >= ' + WALL + ' (' + wgn + '), do stozka ' + f(wz) + ' >= 1,5, do krawedzi ' + f(wkr) + ' >= 1,5');
    wynik.okragla.dolki[d.bit] = { x: d.x, y: d.y, promien: +rr.toFixed(3), do_gniazda: +wg.toFixed(3) };
  }
  if (dolkiOkr.length === 4) {
    let dd = Infinity; for (let i = 0; i < 4; i++) for (let j = i + 1; j < 4; j++) dd = Math.min(dd, Math.hypot(dolkiOkr[i].x - dolkiOkr[j].x, dolkiOkr[i].y - dolkiOkr[j].y) - 2 * RD);
    chk(dd >= 1 - TOL, 'okragla: scianka miedzy dolkami kodu ' + f(dd) + ' >= 1');
  }
  const np = P.number_pos_round[typ];
  if (np === null || np === undefined) info('okragla: number_pos_round.' + typ + ' = null - cyfra pominieta');
  else if (!(Array.isArray(np) && np.length === 2 && np.every(Number.isFinite))) chk(false, 'number_pos_round.' + typ + ': para liczb albo null');
  else {
    const q = prostokat(np[0], np[1], CYFRA_W, CYFRA_H);
    const rogi = [[q.x0, q.y0], [q.x0, q.y1], [q.x1, q.y0], [q.x1, q.y1]];
    const rc = Math.max(...rogi.map(p => Math.hypot(p[0], p[1])));
    let cg = Infinity, cgn = ''; for (const s of S) { const v = dProstKsztalt(q, s); if (v < cg) { cg = v; cgn = s.nazwa; } }
    const cd = dolkiOkr.length ? Math.min(...dolkiOkr.map(d => dProstPunkt(q, [d.x, d.y]) - RD)) : Infinity;
    const cz = M.length ? Math.min(...M.map(m => dProstPunkt(q, [m.x, m.y]) - MD)) : Infinity;
    const csc = Math.min(...rogi.map(p => doSciecia(p[0], p[1], 0)));
    chk(rc <= R + TOL, 'okragla: cyfra (' + np[0] + '; ' + np[1] + ', obrys ' + CYFRA_W + ' x ' + CYFRA_H + ') w kole: promien naroznika ' + f(rc) + ' <= ' + R);
    chk(cg >= 3 - TOL, 'okragla: cyfra - gniazdo ' + f(cg) + ' >= 3 (' + cgn + ')');
    chk(cd >= 1.5 - TOL && cz >= 1.5 - TOL, 'okragla: cyfra - dolek ' + f(cd) + ' >= 1,5; cyfra - stozek ' + f(cz) + ' >= 1,5');
    info('okragla: cyfra - plaszczyzna sciecia ' + f(csc) + ' (relief, informacyjnie; R57: 2,8 / 3,2)');
    wynik.okragla.cyfra = { x: np[0], y: np[1], promien: +rc.toFixed(3), do_gniazda: +cg.toFixed(3), do_dolka: +cd.toFixed(3), do_sciecia: +csc.toFixed(3) };
  }
}

if (KTORA === 'wieczorna' || KTORA === 'obie') sprawdzPlytke('wieczorna', 'ev');
if (KTORA === 'poranna' || KTORA === 'obie') sprawdzPlytke('poranna', 'mo');
podsumowanie.bledy = nBlad; podsumowanie.ok = nOk; podsumowanie.uwagi = nUwag;
if (opt.json && opt.json !== true) fs.writeFileSync(opt.json, JSON.stringify(podsumowanie, null, 1));
console.log('\nWYNIK: ' + (nBlad ? 'BLEDY (' + nBlad + ') - patrz linie BLAD' : 'OK - uklad zgodny z regulami ' + (R54 ? 'R54' : 'R59')) + '; sprawdzen OK ' + nOk + ', bledow ' + nBlad + ', uwag ' + nUwag);
process.exit(nBlad ? 1 : 0);
