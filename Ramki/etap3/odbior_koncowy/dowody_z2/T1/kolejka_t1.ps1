param([int]$Przebieg, [int]$Tor, [string]$Krok)
$rob = '<PC-katalog>\koordynator\robocze\odbior2\final\T1'
$log = "$rob\t1_kolejka.log"
function W([string]$t) { Add-Content -Path $log -Value ("{0} {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $t) }
W ("przebieg $Przebieg | w kolejce do toru $Tor | RAM: " + (& <PC-katalog>\koordynator\narz\ram.cmd))
powershell -NoProfile -ExecutionPolicy Bypass -File <PC-katalog>\koordynator\narz\ciezki.ps1 -Tor $Tor -Kto f1 -Polecenie "$rob\$Krok"
W "KONIEC przebieg $Przebieg | tor $Tor | kod $LASTEXITCODE"
