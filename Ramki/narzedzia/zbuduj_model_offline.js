// Buduje samodzielny model 3D (działa po dwukliku z dysku, bez serwera i bez internetu):
// wkleja three.js r128 + OrbitControls + STLLoader oraz 7 plików STL (base64) do kopii ramka_3d.html.
// R54 (1.11.2026): ramka_3d.html ma już aktualny parametry.json i etykiety liczone z parametrów (poprawki R53 przeniesione
// do źródła), więc builder tylko: podmienia blok params na bieżący parametry.json (kontrola spójności), usuwa Google Fonts
// (zero żądań sieci), wkleja biblioteki i STL. Kopia poprzedniej wersji: archiwum/zbuduj_model_offline_przed_R54_dokumenty_2026-11-01.js
// R59 (14.11.2026): nowy układ gniazd płytek (jedna rynienka) — kontrola nagłówka „po R59”; płytki n1 / n4 z wyniki_v2/stl po R59.
// Opcjonalny drugi argument = kopia animacja_ramki.html, zapisywana po kontroli, że jej blok „uklad” jest równy parametry.json
// i że plik nie odwołuje się do zasobów zewnętrznych. Poprzednia wersja buildera: git, commit 8acb5d3.
// Użycie: node narzedzia/zbuduj_model_offline.js <wyjście.html> [<wyjście_animacji.html>]
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const R=path.join(__dirname,'..'),V=path.join(__dirname,'vendor_three_r128');
const out=process.argv[2]; if(!out){console.error('podaj plik wyjściowy');process.exit(1);}
let h=fs.readFileSync(path.join(R,'ramka_3d.html'),'utf8');
const STL=['ramka_korpus_W_v2','ramka_korpus_P_v2','ramka_blat_v2','ramka_wkladka_v2','ramka_plytka_wieczorna_n1_v2','ramka_plytka_poranna_n4_v2','ramka_pokrywka_v2'];
const emb={},sha={};STL.forEach(n=>{const b=fs.readFileSync(path.join(R,'wyniki_v2','stl',n+'.stl'));emb[n]=b.toString('base64');sha[n]=crypto.createHash('sha256').update(b).digest('hex');});
const lib=f=>fs.readFileSync(path.join(V,f),'utf8').replace(/<\/script/gi,'<\/script');
function rep(a,b){const i=h.indexOf(a);if(i<0||h.indexOf(a,i+1)>=0)throw new Error('kotwica nie jest jednoznaczna: '+a.slice(0,60));h=h.slice(0,i)+b+h.slice(i+a.length);}
// 0) parametry z parametry.json (ramka_3d.html ma tę samą kopię po R54; podmiana gwarantuje aktualność)
const pj=fs.readFileSync(path.join(R,'parametry.json'),'utf8');JSON.parse(pj);if(/<\//.test(pj))throw new Error('parametry.json zawiera "</"');
{const a='<script type="application/json" id="params">',i=h.indexOf(a),j=h.indexOf('</script>',i);if(i<0||h.indexOf(a,i+1)>=0)throw new Error('brak bloku params');
 h=h.slice(0,i+a.length)+'\n'+pj.trim()+'\n'+h.slice(j);}
// 0a) bez Google Fonts (CSS ma czcionki zastępcze), żeby strona nie wykonywała żądań sieciowych
rep('<link rel="preconnect" href="https://fonts.googleapis.com">\n','');
rep('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n','');
rep(/<link rel="stylesheet" href="https:\/\/fonts\.googleapis\.com[^\n]*\n/.exec(h)[0],'');
// 0b) kontrola: nagłówek musi być po R59
if(!h.includes('model 3D v3 (po R59'))throw new Error('ramka_3d.html nie jest w wersji R59');
// 1) biblioteki i STL przed skryptem ładującym
const loaderStart='<script>\n/* Biblioteki: jedno wydanie three.js r128';
rep(loaderStart,'<script>\n'+lib('three.min.js')+'\n</script>\n<script>\n'+lib('OrbitControls.js')+'\n</script>\n<script>\n'+lib('STLLoader.js')+'\n</script>\n<script>\nwindow.STL_B64='+JSON.stringify(emb)+';\nwindow.STL_SHA256='+JSON.stringify(sha)+';\n</script>\n'+loaderStart);
// 2) biblioteki już są: pomiń pobieranie z CDN
rep('  function seq(k){','  if(window.THREE&&THREE.OrbitControls&&THREE.STLLoader)LIBS.length=0;\n  function seq(k){');
// 3) STL z osadzonych danych zamiast fetch
rep('function fetchSTL(name){','function fetchSTL(name){if(window.STL_B64&&STL_B64[name]){const s=atob(STL_B64[name]),u8=new Uint8Array(s.length);for(let i=0;i<s.length;i++)u8[i]=s.charCodeAt(i);const g=loader.parse(u8.buffer);g.computeBoundingBox();return Promise.resolve(g);}\n');
fs.writeFileSync(out,h);
console.log('zapisano',out,(fs.statSync(out).size/1e6).toFixed(1)+' MB');
STL.forEach(n=>console.log(' ',sha[n],n+'.stl'));
// 4) R59: animacja (drugi argument) — blok „uklad” w animacja_ramki.html musi być równy parametry.json; bez zasobów zewnętrznych; kopia obok modelu
const outA=process.argv[3];
if(outA){const a=fs.readFileSync(path.join(R,'animacja_ramki.html'),'utf8'),m=/<script type="application\/json" id="uklad">([\s\S]*?)<\/script>/.exec(a);
 if(!m)throw new Error('animacja_ramki.html: brak bloku uklad');
 const U=JSON.parse(m[1]),PJ=JSON.parse(pj),flat={};Object.keys(PJ).forEach(g=>{if(g!=='_meta')Object.keys(PJ[g]).forEach(k=>{flat[k]=PJ[g][k].value;});});
 const keys=Object.keys(U).filter(k=>k!=='zrodlo'),bad=keys.filter(k=>JSON.stringify(U[k])!==JSON.stringify(flat[k]));
 if(bad.length)throw new Error('animacja_ramki.html: blok uklad ≠ parametry.json: '+bad.join(', '));
 if(/(href|src)\s*=|https?:\/\/(?!www\.w3\.org\/2000\/svg)/.test(a))throw new Error('animacja_ramki.html: odwołanie do zasobu zewnętrznego');
 fs.writeFileSync(outA,a);console.log('zapisano',outA,(fs.statSync(outA).size/1e3).toFixed(1)+' kB; układ = parametry.json ('+keys.length+' kluczy)');}
