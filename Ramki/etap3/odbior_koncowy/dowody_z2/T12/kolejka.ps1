$rob = '<PC-katalog>\koordynator\robocze\odbior2\final\T12'
foreach ($k in 'A','Z','B') {
  $wolne = [math]::Round(([System.IO.DriveInfo]'C').AvailableFreeSpace / 1GB, 1)
  $t = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
  Add-Content -Path "$rob\kolejka.txt" -Value "$t przed krokiem $k wolne na C: $wolne GB" -Encoding ascii
  if ($wolne -lt 8) { Add-Content -Path "$rob\kolejka.txt" -Value "$t krok $k NIE WYSTARTOWAL - ponizej 8 GB" -Encoding ascii; continue }
  & powershell -NoProfile -ExecutionPolicy Bypass -File <PC-katalog>\koordynator\narz\ciezki.ps1 -Tor 2 -Kto f2 -Polecenie "$rob\krok_$k.cmd"
  $kod = $LASTEXITCODE
  $t = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
  Add-Content -Path "$rob\kolejka.txt" -Value "$t krok $k KONIEC kod $kod" -Encoding ascii
}
Add-Content -Path "$rob\kolejka.txt" -Value "KOLEJKA KONIEC" -Encoding ascii