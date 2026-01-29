function Draw-Line {
    param([string]$char, [int]$len)
    return ($char * $len)
}

$width = 50

# Draw static frame once
Clear-Host
Write-Host "+" (Draw-Line "-" $width) "+"
Write-Host ("| GPU WATCH".PadRight($width + 1) + "|")
Write-Host "+" (Draw-Line "-" $width) "+"
Write-Host ("| GPU:".PadRight($width + 1) + "|")
Write-Host ("| Usage:".PadRight($width + 1) + "|")
Write-Host ("| Power:".PadRight($width + 1) + "|")
Write-Host ("| Memory:".PadRight($width + 1) + "|")
Write-Host ("| Temp:".PadRight($width + 1) + "|")
Write-Host "+" (Draw-Line "-" $width) "+"

while ($true) {
    $gpu = nvidia-smi --query-gpu=name,utilization.gpu,power.draw,memory.used,memory.total,temperature.gpu --format=csv,noheader,nounits
    $parts = $gpu.Split(",")

    $name  = $parts[0].Trim()
    $usage = $parts[1].Trim()
    $power = $parts[2].Trim()
    $memU  = $parts[3].Trim()
    $memT  = $parts[4].Trim()
    $temp  = $parts[5].Trim()

    # Move cursor and overwrite only values
    [Console]::SetCursorPosition(7,3)
    Write-Host $name.PadRight($width-6)

    [Console]::SetCursorPosition(9,4)
    Write-Host ($usage + " %").PadRight($width-8) -ForegroundColor Yellow

    [Console]::SetCursorPosition(9,5)
    Write-Host ($power + " W").PadRight($width-8) -ForegroundColor Green

    [Console]::SetCursorPosition(9,6)
    Write-Host ("$memU / $memT MiB").PadRight($width-8) -ForegroundColor Magenta

    [Console]::SetCursorPosition(9,7)
    Write-Host ($temp + " C").PadRight($width-8) -ForegroundColor Red

    Start-Sleep -Milliseconds 700
}
