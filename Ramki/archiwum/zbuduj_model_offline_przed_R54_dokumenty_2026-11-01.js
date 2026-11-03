// Buduje samodzielny model 3D (działa po dwukliku z dysku, bez serwera i bez internetu):
// wkleja three.js r128 + OrbitControls + STLLoader oraz 7 plików STL (base64) do kopii ramka_3d.html.
// R53 (31.10.2026): podmienia wbudowane parametry na aktualny parametry.json, poprawia etykiety z literałami
// sprzed R53 (kołnierz blatu, kieszeń zatrzasku, obrys wkładki, rowki dna), usuwa Google Fonts (zero żądań sieci).
// ramka_3d.html zostaje bez zmian. Kopia poprzedniej wersji: archiwum/zbuduj_model_offline_przed_R53_2026-10-31.js
// Użycie: node narzedzia/zbuduj_model_offline.js <wyjście.html>
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const R=path.join(__dirname,'..'),V=path.join(__dirname,'vendor_three_r128');
const out=process.argv[2]; if(!out){console.error('podaj plik wyjściowy');process.exit(1);}
let h=fs.readFileSync(path.join(R,'ramka_3d.html'),'utf8');
const STL=['ramka_korpus_W_v2','ramka_korpus_P_v2','ramka_blat_v2','ramka_wkladka_v2','ramka_plytka_wieczorna_n1_v2','ramka_plytka_poranna_n4_v2','ramka_pokrywka_v2'];
const emb={},sha={};STL.forEach(n=>{const b=fs.readFileSync(path.join(R,'wyniki_v2','stl',n+'.stl'));emb[n]=b.toString('base64');sha[n]=crypto.createHash('sha256').update(b).digest('hex');});
const lib=f=>fs.readFileSync(path.join(V,f),'utf8').replace(/<\/script/gi,'<\/script');
function rep(a,b){const i=h.indexOf(a);if(i<0||h.indexOf(a,i+1)>=0)throw new Error('kotwica nie jest jednoznaczna: '+a.slice(0,60));h=h.slice(0,i)+b+h.slice(i+a.length);}
// 0) R53: parametry z parametry.json zamiast kopii wbudowanej w ramka_3d.html (była sprzed R53)
const pj=fs.readFileSync(path.join(R,'parametry.json'),'utf8');JSON.parse(pj);if(/<\//.test(pj))throw new Error('parametry.json zawiera "</"');
{const a='<script type="application/json" id="params">',i=h.indexOf(a),j=h.indexOf('</script>',i);if(i<0||h.indexOf(a,i+1)>=0)throw new Error('brak bloku params');
 h=h.slice(0,i+a.length)+'\n'+pj.trim()+'\n'+h.slice(j);}
// 0a) R53: bez Google Fonts (CSS ma czcionki zastępcze), żeby strona nie wykonywała żądań sieciowych
rep('<link rel="preconnect" href="https://fonts.googleapis.com">\n','');
rep('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n','');
rep(/<link rel="stylesheet" href="https:\/\/fonts\.googleapis\.com[^\n]*\n/.exec(h)[0],'');
// 0b) R53: nagłówek i etykiety, które miały liczby wpisane na sztywno
rep('model 3D v3 (po R50)','model 3D v3 (po R53)');
rep('Części drukowane z plików STL (iteracja B3)','Części drukowane z plików STL (po R53, 31.10.2026)');
rep("D.l([-97,-97,H.skirt0],[97,-97,H.skirt0],[0,0,-8],'194','kołnierz: box_outer − 2·(wall_t + blat_skirt_clearance)');D.l([97,0,H.skirt0]",
    "{const sk=v('box_outer')/2-v('wall_t')-v('blat_skirt_clearance');D.l([-sk,-97,H.skirt0],[sk,-97,H.skirt0],[0,0,-8],f(2*sk)+' (luz '+f(v('blat_skirt_clearance'))+')','kołnierz: box_outer − 2·(wall_t + blat_skirt_clearance)');}D.l([97,0,H.skirt0]");
rep("D.p([98,0,v('snap_pocket_z')+1.25],'zatrzask Z '+f(v('snap_pocket_z'))+'…'+f(v('snap_pocket_z')+v('snap_pocket_h')),'snap_pocket_z + snap_pocket_h','l');",
    "D.p([98,0,v('snap_pocket_z')+v('snap_pocket_h')/2],'kieszeń zatrzasku '+f(v('snap_pocket_w'))+' × '+f(v('snap_pocket_h'))+' × '+f(v('snap_pocket_depth'))+', Z '+f(v('snap_pocket_z'))+'…'+f(v('snap_pocket_z')+v('snap_pocket_h')),'snap_pocket_w × snap_pocket_h × snap_pocket_depth, snap_pocket_z','l');");
rep("[0,8,0],'130 × 148,3','obrys z uszami (tabela 1)');","[0,8,0],f(2*(v('tab_pos_x')+v('tab_w')/2))+' × '+f(v('tab_end_y')+fr),'obrys z uszami (tabela 1)');");
rep("Od spodu wkręty przez rowki 3,4 w dnie.'","Od spodu wkręty przez rowki '+f(v('panel_slot_w'))+' w dnie.'");
rep("d:'Rama 104,6 × 6 na dyfuzorze","d:'Rama '+f(v('insert_opening')+2*v('insert_wall_w'))+' × '+f(v('insert_h'))+' na dyfuzorze, otwór '+f(v('insert_opening'))+'");
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
