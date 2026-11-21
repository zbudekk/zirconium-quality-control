# T9 - dane osobowe: uruchomienie krokow planu (odbior 21.11.2026).
# N (zrodla nazw) = wiersze pliku t9_N.txt (9 x --nazwy-z, 36 x --baza), zamrozone przed pierwszym krokiem.
# Kazde wywolanie dopisuje pelne polecenie do t9_polecenia.txt i kod wyjscia do kody.txt.
# Uzycie: powershell -NoProfile -ExecutionPolicy Bypass -File krok_t9.ps1 -Krok <nazwa> -Wynik <plik .txt> [-Json <plik>] -- <opcje narzedzia poza N>
param(
    [Parameter(Mandatory = $true)][string]$Krok,
    [Parameter(Mandatory = $true)][string]$Wynik,
    [string]$Json = '',
    [string]$PlikCeli = '',
    [string]$PlikN = 't9_N.txt',
    [Parameter(ValueFromRemainingArguments = $true)][string[]]$Opcje
)
$PY = '<PC>\AppData\Local\Programs\Python\Python312\python.exe'
$T9 = '<PC-katalog>\t0\repo\Ramki\etap3\odbior_koncowy\narzedzia\t9_dane_osobowe.py'
$ROB = '<PC-katalog>\koordynator\robocze\odbior\T9'
$N = @(Get-Content "$ROB\$PlikN" | Where-Object { $_ -ne '' })
$argi = @('-I', $T9) + $N
if ($PlikCeli -ne '') { $argi += @(Get-Content $PlikCeli | Where-Object { $_ -ne '' }) }
if ($Opcje) { $argi += $Opcje }
if ($Json -ne '') { $argi += @('--json', $Json) }
$argi += @('--wynik', $Wynik)
$start = Get-Date
& $PY @argi | Out-Null
$kod = $LASTEXITCODE
$koniec = Get-Date
$wiersz = "{0} KOD={1} start {2} koniec {3} ({4:N1} s)" -f $Krok, $kod, $start.ToString('HH:mm:ss'), $koniec.ToString('HH:mm:ss'), ($koniec - $start).TotalSeconds
[IO.File]::AppendAllText("$ROB\kody.txt", $wiersz + "`n", [Text.Encoding]::ASCII)
$pol = "[$Krok] (N z pliku $PlikN) PY " + ($argi -join ' ')
[IO.File]::AppendAllText("$ROB\t9_polecenia.txt", $pol + "`n", [Text.Encoding]::ASCII)
Write-Output $wiersz
exit $kod
