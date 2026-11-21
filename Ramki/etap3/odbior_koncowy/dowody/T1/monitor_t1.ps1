$rob = '<PC-katalog>\koordynator\robocze\odbior\T1'
$out = "$rob\t1_co_liczylo.txt"
$kol = "$rob\t1_kolejka.log"
$t0 = Get-Date
while (((Get-Date) - $t0).TotalMinutes -lt 150) {
    $p = Get-Process python -ErrorAction SilentlyContinue
    $g = $p | Group-Object { if ($_.Path) { $_.Path -replace '^<PC-katalog>\\', '' -replace '\\venv\\Scripts\\python.exe$', '' -replace '^<PC>\\AppData\\Local\\Programs\\Python\\Python312\\python.exe$', 'bazowy' } else { 'bez-sciezki' } } | ForEach-Object { "{0} x{1}" -f $_.Name, $_.Count }
    $ram = & <PC-katalog>\koordynator\narz\ram.cmd
    $blok = (Get-ChildItem <PC-katalog>\koordynator\robocze -Directory -Filter 'CIEZKI*.lock' -ErrorAction SilentlyContinue | ForEach-Object { $k = Join-Path $_.FullName 'kto.txt'; if (Test-Path $k) { $_.Name + '=' + ((Get-Content $k -TotalCount 1) -split ' ')[0] } else { $_.Name } }) -join ', '
    Add-Content -Path $out -Value ("{0} | RAM {1} | python: {2} | {3} | blokady: {4}" -f (Get-Date -Format 'HH:mm:ss'), $ram, @($p).Count, ($g -join '; '), $blok)
    if ((Test-Path $kol) -and (Select-String -Path $kol -Pattern 'KOLEJKA KONIEC' -Quiet)) { break }
    Start-Sleep -Seconds 120
}