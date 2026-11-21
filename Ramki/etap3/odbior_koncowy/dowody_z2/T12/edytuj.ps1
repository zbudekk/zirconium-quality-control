param([string]$Plik, [string]$Wej)
# Krok T0-4: 4 foldery [sciezki] i operatorzy w ustawienia.toml (UTF-8 bez BOM); $Wej z ukosnikami /
$ErrorActionPreference = 'Stop'
$enc = New-Object System.Text.UTF8Encoding($false)
$t = [IO.File]::ReadAllText($Plik, $enc)
$t2 = $t.Replace('folder_eksportu_skanera = "C:/Aidite/Scandata"', "folder_eksportu_skanera = `"$Wej/eksport`"").Replace('folder_cyrkon = "C:/sciezka/do/OneDrive/Cyrkon"', "folder_cyrkon = `"$Wej/Cyrkon`"").Replace('folder_prywatne = "C:/sciezka/do/OneDrive/Prywatne"', "folder_prywatne = `"$Wej/Prywatne`"").Replace('folder_millbox = "C:/MillBox/raporty"', "folder_millbox = `"$Wej/millbox`"").Replace('operatorzy = []', 'operatorzy = ["Technik A"]')
[IO.File]::WriteAllText($Plik, $t2, $enc)
$n = (Compare-Object ($t -split "`n") ($t2 -split "`n") | Where-Object SideIndicator -eq '=>').Count
"ustawienia $Plik : zmienionych wierszy $n (oczekiwane 5)"
if ($n -ne 5) { exit 1 }
exit 0
