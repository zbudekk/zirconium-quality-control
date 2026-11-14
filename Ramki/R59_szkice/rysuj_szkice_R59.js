// R59_szkice/rysuj_szkice_R59.js - R59 (14.11.2026): szkice ukladu gniazd plytek, widok z gory w skali (wymiary w mm z plikow).
// Dla kazdego pliku parametry_wariant_<id>.json rysuje szkic_<id>.svg: na gorze uklad dzisiejszy (R54), pod nim wariant.
// Dodatkowo szkic_przeglad_<plytka>.svg: dzis + warianty a / b / c obok siebie (siatka 2 x 2).
// Na rysunku: plytka kwadratowa 96 (linia ciagla), plytka okragla fi 100 ze scieciem (linia przerywana), kolo pola skanowania
// r 47 (kropki), gniazda ze srednica, rynienka, stozki znacznikow A / B / C, dolki kodu i miejsce cyfry (kwadrat: granatowe,
// okragla: zielone), wyciecie D. Os y do tylu (PRZOD na dole rysunku).
// Uzycie: node R59_szkice/rysuj_szkice_R59.js <parametry.json = stan dzisiejszy> <katalog z parametry_wariant_*.json> [katalog wyjsciowy]
// PNG: Chrome bez okna, np. chrome.exe --headless=new --screenshot=szkic_W-b.png --window-size=1080,2760 szkic_W-b.svg
'use strict';
const fs = require('fs'), path = require('path');

function wczytaj(sciezka) {
  const P0 = JSON.parse(fs.readFileSync(sciezka, 'utf8')), P = {};
  for (const [sek, zaw] of Object.entries(P0)) if (!sek.startsWith('_') && zaw && typeof zaw === 'object')
    for (const [k, v] of Object.entries(zaw)) if (v && typeof v === 'object' && 'value' in v) P[k] = v.value;
  return { P, wariant: (P0._meta && P0._meta.r59_wariant) || null };
}
const KOLOR = { 7.5: '#b7d7f0', 9: '#8fc1e8', 10: '#bfe3b4', 12: '#9ad48c', 12.5: '#6cc070', 15: '#ffb066', 18: '#ff8a50' };
const kolor = d => KOLOR[d] || '#dddddd';
const pl = v => String(v).replace('.', ',');
const esc = t => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;');

function liczby(P, pre) {
  const mix = {}; let ryn = 0;
  for (const r of P[pre + '_rows']) { if (r.type === 'round') mix[r.d] = (mix[r.d] || 0) + r.x.length; else ryn += r.x.length; }
  const sred = Object.keys(mix).map(Number).sort((a, b) => a - b);
  return { mix, sred, ryn, razem: sred.reduce((a, d) => a + mix[d], 0) };
}

// rysunek jednej plytki: srodek (cx, cy) w px, skala s px/mm; f = mnoznik wielkosci napisow
function rysunek(P, typ, cx, cy, s, f) {
  const pre = typ === 'wieczorna' ? 'ev' : 'mo';
  const X = x => (cx + x * s).toFixed(1), Y = y => (cy - y * s).toFixed(1), L = v => (v * s).toFixed(1);
  const o = [];
  const S2 = P.plate_size / 2, RP = P.plate_round_d / 2, R = P.socket_zone_r;
  // plytka kwadratowa i wyciecie D
  o.push(`<rect x="${X(-S2)}" y="${Y(S2)}" width="${L(P.plate_size)}" height="${L(P.plate_size)}" rx="${L(P.plate_edge_r)}" fill="#fbfbf8" stroke="#222" stroke-width="2.5"/>`);
  o.push(`<rect x="${X(S2 - P.notch_size)}" y="${Y(-S2 + P.notch_size)}" width="${L(P.notch_size)}" height="${L(P.notch_size)}" fill="#bbb" stroke="#222" stroke-width="1.5"/>`);
  // plytka okragla ze scieciem
  const kat = P.round_flat_angle * Math.PI / 180, dist = Math.sqrt(RP * RP - (P.round_flat_w / 2) ** 2), pol = Math.asin(P.round_flat_w / 2 / RP);
  const p1 = [RP * Math.cos(kat + pol), RP * Math.sin(kat + pol)], p2 = [RP * Math.cos(kat - pol), RP * Math.sin(kat - pol)];
  o.push(`<path d="M ${X(p1[0])} ${Y(p1[1])} A ${L(RP)} ${L(RP)} 0 1 0 ${X(p2[0])} ${Y(p2[1])} Z" fill="none" stroke="#666" stroke-width="2.5" stroke-dasharray="${L(2.2)} ${L(1.3)}"/>`);
  // kolo pola skanowania
  o.push(`<circle cx="${X(0)}" cy="${Y(0)}" r="${L(R)}" fill="none" stroke="#d22" stroke-width="2.5" stroke-dasharray="${L(0.5)} ${L(1.1)}"/>`);
  // gniazda i rynienki
  for (const r of P[pre + '_rows']) for (const x of r.x) {
    if (r.type === 'round') {
      o.push(`<circle cx="${X(x)}" cy="${Y(r.y)}" r="${L(r.d / 2)}" fill="${kolor(r.d)}" stroke="#333" stroke-width="2"/>`);
      const fs_ = Math.min(r.d * 0.50, 6.2) * s * f * (String(r.d).length > 2 ? 0.82 : 1);
      o.push(`<text x="${X(x)}" y="${(cy - r.y * s + fs_ * 0.36).toFixed(1)}" font-size="${fs_.toFixed(1)}" text-anchor="middle" font-weight="700" fill="#111">${pl(r.d)}</text>`);
    } else {
      o.push(`<rect x="${X(x - r.l / 2)}" y="${Y(r.y + r.w / 2)}" width="${L(r.l)}" height="${L(r.w)}" rx="${L(r.w / 2)}" fill="#f3dc9a" stroke="#333" stroke-width="2"/>`);
      const fs_ = Math.min(r.w * 0.42, r.l * 0.16) * s * f, opis = r.l >= 40 ? 'rynienka ' + pl(r.l) + ' x ' + pl(r.w) : pl(r.l) + ' x ' + pl(r.w);
      o.push(`<text x="${X(x)}" y="${(cy - r.y * s + fs_ * 0.36).toFixed(1)}" font-size="${fs_.toFixed(1)}" text-anchor="middle" font-weight="700" fill="#111">${opis}</text>`);
    }
  }
  // stozki znacznikow
  const mk = P[pre + '_marker_pos'];
  for (const c of ['A', 'B', 'C']) {
    const fs_ = 3.6 * s * f;
    o.push(`<circle cx="${X(mk[c][0])}" cy="${Y(mk[c][1])}" r="${L(P.marker_cone_d / 2)}" fill="#333" stroke="#000" stroke-width="1"/>`);
    o.push(`<text x="${X(mk[c][0])}" y="${(cy - mk[c][1] * s + fs_ * 0.36).toFixed(1)}" font-size="${fs_.toFixed(1)}" text-anchor="middle" font-weight="700" fill="#fff">${c}</text>`);
  }
  // dolki kodu i cyfra: kwadrat (granatowe)
  const dk = ['A', 'B', 'C'].map((b, i) => [P.code_dimple_x, P.code_dimple_y0 + i * P.code_dimple_pitch]).concat([P.code_bit_d_pos]);
  for (const d of dk) o.push(`<circle cx="${X(d[0])}" cy="${Y(d[1])}" r="${L(P.code_dimple_d / 2)}" fill="#1f3a93" stroke="none"/>`);
  o.push(`<rect x="${X(P.number_pos_x - 1.8)}" y="${Y(P.number_pos_y + P.number_text_h / 2)}" width="${L(3.6)}" height="${L(P.number_text_h)}" fill="none" stroke="#1f3a93" stroke-width="2"/>`);
  // dolki kodu i cyfra: okragla (zielone)
  const dr = P.code_dimples_round[typ];
  for (const b of ['A', 'B', 'C', 'D']) o.push(`<circle cx="${X(dr[b][0])}" cy="${Y(dr[b][1])}" r="${L(P.code_dimple_d / 2)}" fill="#0a7d2c" stroke="none"/>`);
  const np = P.number_pos_round[typ];
  if (np) o.push(`<rect x="${X(np[0] - 1.8)}" y="${Y(np[1] + P.number_text_h / 2)}" width="${L(3.6)}" height="${L(P.number_text_h)}" fill="none" stroke="#0a7d2c" stroke-width="2"/>`);
  // PRZOD / TYL
  const fs_ = 3.4 * s * f;
  o.push(`<text x="${X(0)}" y="${(cy + (RP + 1.2) * s + fs_).toFixed(1)}" font-size="${fs_.toFixed(1)}" text-anchor="middle" fill="#555">PRZOD (strona technika)</text>`);
  o.push(`<text x="${X(-S2 + 1)}" y="${(cy - (S2 + 1.0) * s).toFixed(1)}" font-size="${fs_.toFixed(1)}" text-anchor="start" fill="#555">TYL</text>`);
  return o.join('\n');
}

function wierszLiczb(P, pre, x, y, fs_, dzis) {
  const l = liczby(P, pre), o = []; let px = x;
  for (const d of l.sred) {
    o.push(`<circle cx="${px + fs_ * 0.45}" cy="${y - fs_ * 0.33}" r="${fs_ * 0.45}" fill="${kolor(d)}" stroke="#333" stroke-width="1.5"/>`);
    const t = l.mix[d] + ' x fi ' + pl(d);
    o.push(`<text x="${px + fs_ * 1.1}" y="${y}" font-size="${fs_}" font-weight="700" fill="#111">${t}</text>`);
    px += fs_ * 1.1 + t.length * fs_ * 0.56 + fs_ * 0.7;
  }
  let t2 = '';
  const podzial = P[pre + '_rows'].some(r => r.type === 'trough' && r.x.length > 1);      // D3-b: dwie krotkie rynienki w jednym rzedzie
  const opisRyn = podzial ? l.ryn + ' krotkie rynienki (1 rzad)' : l.ryn + (l.ryn === 1 ? ' rynienka' : ' rynienki');
  if (dzis) { const ld = liczby(dzis, pre); const wsz = [...new Set(l.sred.concat(ld.sred))].sort((a, b) => a - b); t2 = 'zmiana: ' + wsz.map(d => 'fi ' + pl(d) + ': ' + (ld.mix[d] || 0) + ' -> ' + (l.mix[d] || 0)).join(';  ') + ';  rynienki: ' + ld.ryn + (podzial ? ' dlugie -> ' + l.ryn + ' krotkie' : ' -> ' + l.ryn); }
  return { svg: o.join('\n'), opis: l.razem + ' gniazd + ' + opisRyn, zmiana: t2 };
}

function legenda(x, y, fs_) {
  const o = [], w = 70, dy = fs_ * 1.45; let yy = y;
  const linia = (styl, opis) => { o.push(`<line x1="${x}" y1="${yy - fs_ * 0.3}" x2="${x + w}" y2="${yy - fs_ * 0.3}" ${styl}/>`); o.push(`<text x="${x + w + 14}" y="${yy}" font-size="${fs_}" fill="#222">${esc(opis)}</text>`); yy += dy; };
  linia('stroke="#222" stroke-width="3"', 'plytka kwadratowa 96 x 96 (szare pole w rogu = wyciecie D)');
  linia('stroke="#666" stroke-width="3" stroke-dasharray="14 8"', 'plytka okragla fi 100 ze scieciem (te same gniazda)');
  linia('stroke="#d22" stroke-width="3" stroke-dasharray="4 8"', 'kolo pola skanowania r 47 - gniazda musza lezec w srodku');
  o.push(`<circle cx="${x + 18}" cy="${yy - fs_ * 0.3}" r="13" fill="#333"/><text x="${x + 18}" y="${yy - fs_ * 0.3 + 7}" font-size="20" text-anchor="middle" fill="#fff" font-weight="700">A</text>`);
  o.push(`<text x="${x + w + 14}" y="${yy}" font-size="${fs_}" fill="#222">stozki znacznikow A, B, C (program ustawia po nich skan)</text>`); yy += dy;
  o.push(`<circle cx="${x + 12}" cy="${yy - fs_ * 0.3}" r="7" fill="#1f3a93"/><circle cx="${x + 46}" cy="${yy - fs_ * 0.3}" r="7" fill="#0a7d2c"/>`);
  o.push(`<text x="${x + w + 14}" y="${yy}" font-size="${fs_}" fill="#222">dolki kodu i ramka cyfry: granatowe = kwadrat, zielone = okragla</text>`);
  return o.join('\n');
}

// rozmiar pisma zmniejszony tak, zeby napis zmiescil sie w szerokosci maxW (szerokosc znaku szacowana z zapasem)
function wSzerokosci(t, fs_, maxW, waga) {
  const szac = String(t).length * fs_ * ((waga || 400) >= 700 ? 0.62 : 0.56);
  return szac > maxW ? +(fs_ * maxW / szac).toFixed(1) : fs_;
}
// dluga linia "a;  b;  c" dzielona na dwie mniej wiecej rowne czesci
function naDwieLinie(t, sep) {
  const cz = String(t).split(sep); if (cz.length < 2) return [t];
  let best = 1, roznica = Infinity;
  for (let i = 1; i < cz.length; i++) { const r = Math.abs(cz.slice(0, i).join(sep).length - cz.slice(i).join(sep).length); if (r < roznica) { roznica = r; best = i; } }
  return [cz.slice(0, best).join(sep) + sep.trim(), cz.slice(best).join(sep)];
}

function szkicWariantu(dzis, wariant, meta, plikWy) {
  const typ = meta.plytka, pre = typ === 'wieczorna' ? 'ev' : 'mo';
  const W = 1080, s = 9.6, box = 104 * s, x0 = (W - box) / 2, o = [];
  let y = 0;
  const tekst = (t, yy, fs0, waga, kol, anchor, xx) => { const fs_ = wSzerokosci(t, fs0, W - 70, waga); o.push(`<text x="${xx !== undefined ? xx : 40}" y="${yy}" font-size="${fs_}" font-weight="${waga || 400}" fill="${kol || '#111'}" text-anchor="${anchor || 'start'}">${esc(t)}</text>`); };
  y += 66; tekst('Plytka ' + typ + ' - wariant ' + meta.id, y, 50, 700);
  y += 46; tekst('(' + meta.nazwa + ')', y, 32, 400, '#333');
  y += 36; tekst('R59, propozycja do wyboru na bramce G0. Wymiary w mm, widok z gory.', y, 26, 400, '#555');
  // dzis
  y += 70; const wl1 = wierszLiczb(dzis, pre, 40, 0, 32, null);
  tekst('DZIS (uklad R54): ' + wl1.opis, y, 40, 700, '#7a1f1f');
  let cy = y + 22 + box / 2; o.push(rysunek(dzis, typ, W / 2, cy, s, 1)); y = cy + box / 2 + 84;
  o.push(`<g transform="translate(0 ${y})">${wl1.svg}</g>`);
  // wariant
  y += 86; const wl2 = wierszLiczb(wariant, pre, 40, 0, 32, dzis);
  tekst('WARIANT ' + meta.id + ': ' + wl2.opis, y, 40, 700, '#0b4f8a');
  cy = y + 22 + box / 2; o.push(rysunek(wariant, typ, W / 2, cy, s, 1)); y = cy + box / 2 + 84;
  o.push(`<g transform="translate(0 ${y})">${wl2.svg}</g>`);
  const linieZmiany = String(wl2.zmiana).length * 27 * 0.56 > W - 70 ? naDwieLinie(wl2.zmiana, ';  ') : [wl2.zmiana];
  y += 48; tekst(linieZmiany[0], y, 27, 400, '#222');
  if (linieZmiany[1]) { y += 36; tekst(linieZmiany[1], y, 27, 400, '#222', 'start', 40 + 27 * 4.1); }
  y += 56; o.push(legenda(40, y, 26));
  y += 26 * 1.45 * 4 + 40;
  const svg = `<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${Math.ceil(y)}" viewBox="0 0 ${W} ${Math.ceil(y)}" font-family="Arial, Helvetica, sans-serif">\n<rect width="100%" height="100%" fill="#ffffff"/>\n${o.join('\n')}\n</svg>\n`;
  fs.writeFileSync(plikWy, svg);
  return { W, H: Math.ceil(y) };
}

// tytul = null: przeglad domyslny (dzis + a / b / c, uklad jak w pierwszych szkicach R59); tytul podany (przeglad na zadanie,
// --przeglad): napisy sa dopasowane do szerokosci pola, a dluga lista srednic idzie w dwoch liniach
function szkicPrzegladu(dzis, warianty, typ, plikWy, tytul) {
  const pre = typ === 'wieczorna' ? 'ev' : 'mo', W = 1080, s = 4.85, box = 104 * s, kol = [20 + box / 2, W - 20 - box / 2], o = [];
  const dop = tytul !== undefined && tytul !== null, skok = dop ? 196 : 162;
  const tekst = (t, xx, yy, fs0, waga, kolr, maxW) => { const fs_ = dop && maxW ? wSzerokosci(t, fs0, maxW, waga) : fs0; o.push(`<text x="${xx}" y="${yy}" font-size="${fs_}" font-weight="${waga || 400}" fill="${kolr || '#111'}" text-anchor="start">${esc(t)}</text>`); };
  let y = 58; tekst(dop ? tytul : 'Plytka ' + typ + ': dzis i 3 warianty (R59)', 30, y, 42, 700, '#111', W - 60);
  const pola = [{ P: dzis, tytul: 'DZIS (R54)', kolr: '#7a1f1f' }].concat(warianty.map(w => ({ P: w.P, tytul: w.meta.id + ' ' + w.meta.nazwa, kolr: '#0b4f8a' })));
  let yRz = y + 30;
  pola.forEach((p, i) => {
    const c = i % 2, cx = kol[c], xl = cx - box / 2 + 6;
    if (i && c === 0) yRz += box + skok;
    const l = liczby(p.P, pre), lista = l.sred.map(d => l.mix[d] + ' x fi ' + pl(d));
    tekst(p.tytul, xl, yRz + 34, 30, 700, p.kolr, box - 12);
    o.push(rysunek(p.P, typ, cx, yRz + 46 + box / 2, s, 1.12));
    let yy = yRz + 46 + box + 54;
    if (dop && lista.length > 3) { const pol = Math.ceil(lista.length / 2); tekst(lista.slice(0, pol).join(', ') + ',', xl, yy, 25, 700, '#111', box - 12); yy += 32; tekst(lista.slice(pol).join(', '), xl, yy, 25, 700, '#111', box - 12); }
    else tekst(lista.join(', '), xl, yy, 25, 700, '#111', box - 12);
    tekst('= ' + l.razem + ' gniazd + ' + l.ryn + (l.ryn === 1 ? ' rynienka' : ' rynienki'), xl, yy + 34, 25, 400, '#111', box - 12);
  });
  const H = Math.ceil(yRz + box + skok);
  fs.writeFileSync(plikWy, `<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" font-family="Arial, Helvetica, sans-serif">\n<rect width="100%" height="100%" fill="#ffffff"/>\n${o.join('\n')}\n</svg>\n`);
  return { W, H };
}

// Przelaczniki (dopisane po G0, zeby nie przerysowywac szkicow juz zatwierdzonych):
//   --tylko=P-d,P-d1              rysuje tylko szkice podanych wariantow (i zadnego przegladu domyslnego)
//   --przeglad=nazwa:P-b,P-d,...  dodatkowo szkic_przeglad_<nazwa>.svg: DZIS i podane warianty w podanej kolejnosci
const opcje = {}, pozycyjne = [];
for (const a of process.argv.slice(2)) { const m = /^--([a-z0-9-]+)(?:=(.*))?$/i.exec(a); if (m) opcje[m[1]] = m[2] === undefined ? true : m[2]; else pozycyjne.push(a); }
const [plikDzis, katWar, katWy0] = pozycyjne;
if (!plikDzis || !katWar) { console.error('Uzycie: node rysuj_szkice_R59.js <parametry.json> <katalog z parametry_wariant_*.json> [katalog wyjsciowy] [--tylko=id,id] [--przeglad=nazwa:id,id]'); process.exit(2); }
const katWy = katWy0 || katWar, dzis = wczytaj(plikDzis).P, wszystkie = [], rozmiary = [];
const tylko = opcje.tylko && opcje.tylko !== true ? String(opcje.tylko).split(',') : null;
for (const n of fs.readdirSync(katWar).filter(n => /^parametry_wariant_.+\.json$/.test(n)).sort()) {
  const { P, wariant } = wczytaj(path.join(katWar, n));
  if (!wariant) { console.log('pomijam ' + n + ' (brak _meta.r59_wariant)'); continue; }
  wszystkie.push({ P, meta: wariant });
  if (tylko && !tylko.includes(wariant.id)) continue;
  const r = szkicWariantu(dzis, P, wariant, path.join(katWy, 'szkic_' + wariant.id + '.svg'));
  rozmiary.push('szkic_' + wariant.id + ' ' + r.W + ' ' + r.H);
  console.log('szkic_' + wariant.id + '.svg  ' + r.W + ' x ' + r.H);
}
if (!tylko && !opcje.przeglad) for (const typ of ['wieczorna', 'poranna']) {
  const w = wszystkie.filter(v => v.meta.plytka === typ && /^[WP]-[abc]$/.test(v.meta.id));
  if (!w.length) continue;
  const r = szkicPrzegladu(dzis, w, typ, path.join(katWy, 'szkic_przeglad_' + typ + '.svg'));
  rozmiary.push('szkic_przeglad_' + typ + ' ' + r.W + ' ' + r.H);
  console.log('szkic_przeglad_' + typ + '.svg  ' + r.W + ' x ' + r.H);
}
if (opcje.przeglad && opcje.przeglad !== true) {
  const [nazwa, lista] = String(opcje.przeglad).split(':'), ids = (lista || '').split(',').filter(Boolean);
  const w = ids.map(id => wszystkie.find(v => v.meta.id === id));
  if (!nazwa || !ids.length || w.some(v => !v)) { console.error('--przeglad=nazwa:id,id - nieznany wariant w ' + opcje.przeglad); process.exit(2); }
  const typ = w[0].meta.plytka;
  const r = szkicPrzegladu(dzis, w, typ, path.join(katWy, 'szkic_przeglad_' + nazwa + '.svg'), 'Plytka ' + typ + ': dzis i warianty ' + ids.join(', ') + ' (R59)');
  rozmiary.push('szkic_przeglad_' + nazwa + ' ' + r.W + ' ' + r.H);
  console.log('szkic_przeglad_' + nazwa + '.svg  ' + r.W + ' x ' + r.H);
}
fs.writeFileSync(path.join(katWy, 'rozmiary_szkicow.txt'), rozmiary.join('\n') + '\n');
