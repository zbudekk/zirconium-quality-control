// Buduje samodzielny model 3D (działa po dwukliku z dysku, bez serwera i bez internetu):
// wkleja three.js r128 + OrbitControls + STLLoader oraz 7 plików STL (base64) do kopii ramka_3d.html.
// Użycie: node narzedzia/zbuduj_model_offline.js <wyjście.html>
const fs=require('fs'),path=require('path');
const R=path.join(__dirname,'..'),V=path.join(__dirname,'vendor_three_r128');
const out=process.argv[2]; if(!out){console.error('podaj plik wyjściowy');process.exit(1);}
let h=fs.readFileSync(path.join(R,'ramka_3d.html'),'utf8');
const STL=['ramka_korpus_W_v2','ramka_korpus_P_v2','ramka_blat_v2','ramka_wkladka_v2','ramka_plytka_wieczorna_n1_v2','ramka_plytka_poranna_n4_v2','ramka_pokrywka_v2'];
const emb={};STL.forEach(n=>{emb[n]=fs.readFileSync(path.join(R,'wyniki_v2','stl',n+'.stl')).toString('base64');});
const lib=f=>fs.readFileSync(path.join(V,f),'utf8').replace(/<\/script/gi,'<\/script');
function rep(a,b){const i=h.indexOf(a);if(i<0||h.indexOf(a,i+1)>=0)throw new Error('kotwica nie jest jednoznaczna: '+a.slice(0,60));h=h.slice(0,i)+b+h.slice(i+a.length);}
// 1) biblioteki i STL przed skryptem ładującym
const loaderStart='<script>\n/* Biblioteki: jedno wydanie three.js r128';
rep(loaderStart,'<script>\n'+lib('three.min.js')+'\n</script>\n<script>\n'+lib('OrbitControls.js')+'\n</script>\n<script>\n'+lib('STLLoader.js')+'\n</script>\n<script>\nwindow.STL_B64='+JSON.stringify(emb)+';\n</script>\n'+loaderStart);
// 2) biblioteki już są: pomiń pobieranie z CDN
rep('  function seq(k){','  if(window.THREE&&THREE.OrbitControls&&THREE.STLLoader)LIBS.length=0;\n  function seq(k){');
// 3) STL z osadzonych danych zamiast fetch
rep('function fetchSTL(name){','function fetchSTL(name){if(window.STL_B64&&STL_B64[name]){const s=atob(STL_B64[name]),u8=new Uint8Array(s.length);for(let i=0;i<s.length;i++)u8[i]=s.charCodeAt(i);const g=loader.parse(u8.buffer);g.computeBoundingBox();return Promise.resolve(g);}\n');
fs.writeFileSync(out,h);
console.log('zapisano',out,(fs.statSync(out).size/1e6).toFixed(1)+' MB');
