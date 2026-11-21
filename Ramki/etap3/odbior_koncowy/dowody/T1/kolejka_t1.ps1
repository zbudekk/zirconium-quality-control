$rob = '<PC-katalog>\koordynator\robocze\odbior\T1'
$log = "$rob\t1_kolejka.log"
function W([string]$t) { Add-Content -Path $log -Value ("{0} {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $t) }
W ("RAM przed przebiegiem 1: " + (& <PC-katalog>\koordynator\narz\ram.cmd))
W "START przebieg 1 (krok 4, interpreter srodowiska wersji)"
powershell -NoProfile -ExecutionPolicy Bypass -File <PC-katalog>\koordynator\narz\ciezki.ps1 -Tor 1 -Kto odb-T1 -Polecenie "$rob\krok_4.cmd"
W "KONIEC przebieg 1 | kod $LASTEXITCODE"
W ("RAM przed przebiegiem 2: " + (& <PC-katalog>\koordynator\narz\ram.cmd))
W "START przebieg 2 (krok 5, interpreter bazowy)"
powershell -NoProfile -ExecutionPolicy Bypass -File <PC-katalog>\koordynator\narz\ciezki.ps1 -Tor 1 -Kto odb-T1 -Polecenie "$rob\krok_5.cmd"
W "KONIEC przebieg 2 | kod $LASTEXITCODE"
W "KOLEJKA KONIEC"