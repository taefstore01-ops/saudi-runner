# Google Play screenshots (1080x1920) of the game's ?shot= mode, using headless Chrome.
# Usage: start the local server (port 8812), then:  powershell -File tools\store_shots.ps1
$out = Join-Path (Split-Path $PSScriptRoot -Parent) 'store'
New-Item -ItemType Directory -Force $out | Out-Null
$chrome = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
$shots = [ordered]@{
  '1-lobby'   = 'shot=riyadh&hero=saif'
  '2-tabuk'   = 'shot=tabuk&hero=saif&run=2.5&cans=37'
  '3-neom'    = 'shot=neom&hero=sadeem&run=3&cans=64'
  '4-abha'    = 'shot=abha&hero=sadeem&run=2.2&cans=21&jump=1'
  '5-madinah' = 'shot=madinah&hero=saif&run=2.8&cans=45'
  '6-regions' = 'shot=jeddah&hero=saif&screen=regions'
  '7-shop'    = 'shot=alula&hero=sadeem&screen=shop'
}
foreach ($name in $shots.Keys) {
  $file = Join-Path $out "$name.png"
  Remove-Item $file -ErrorAction SilentlyContinue
  # Chrome is a GUI program: Start-Process -Wait makes PowerShell wait until the picture is written
  $chromeArgs = @('--headless=new', '--disable-gpu-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader',
    "--user-data-dir=$env:TEMP\sr-chrome-$name", '--hide-scrollbars', '--window-size=540,960', '--force-device-scale-factor=2',
    '--virtual-time-budget=25000', "--screenshot=`"$file`"", "`"http://localhost:8812/?$($shots[$name])`"")
  Start-Process -FilePath $chrome -ArgumentList $chromeArgs -Wait -WindowStyle Hidden
  $size = if (Test-Path $file) { (Get-Item $file).Length } else { 0 }
  Write-Output "$name -> $size bytes"
}
