$rob = '<PC-katalog>\koordynator\robocze\odbior2\final\T12'
& powershell -NoProfile -ExecutionPolicy Bypass -File <PC-katalog>\koordynator\narz\ciezki.ps1 -Tor 2 -Kto f2 -Polecenie "$rob\krok_B2.cmd"
$kod = $LASTEXITCODE
$t = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
Add-Content -Path "$rob\kolejka.txt" -Value "$t krok B2 (czesc B proba 2) KONIEC kod $kod" -Encoding ascii