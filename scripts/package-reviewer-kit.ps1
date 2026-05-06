param(
  [string]$RepoRoot = "",
  [string]$Version = "1.0.0"
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
  $RepoRoot = Split-Path -Parent $PSScriptRoot
}

$artifactsDir = Join-Path $RepoRoot "artifacts"
$kitRoot = Join-Path $artifactsDir "reviewer-kit"
$installer = Join-Path $artifactsDir "CareBridgeLocal-Setup-$Version.exe"
$msi = Join-Path $artifactsDir "CareBridgeLocal_${Version}_x64_en-US.msi"
$zipOut = Join-Path $artifactsDir "CareBridge-Local-Reviewer-Kit-v$Version.zip"

if (!(Test-Path $installer)) {
  throw "Installer not found: $installer. Run scripts\build-desktop.ps1 first."
}

if (Test-Path $kitRoot) {
  Remove-Item -LiteralPath $kitRoot -Recurse -Force
}
New-Item -ItemType Directory -Path $kitRoot | Out-Null

Copy-Item -LiteralPath $installer -Destination (Join-Path $kitRoot (Split-Path $installer -Leaf)) -Force
if (Test-Path $msi) {
  Copy-Item -LiteralPath $msi -Destination (Join-Path $kitRoot (Split-Path $msi -Leaf)) -Force
}
Copy-Item -LiteralPath (Join-Path $RepoRoot "docs\USER_GUIDE.md") -Destination (Join-Path $kitRoot "USER_GUIDE.md") -Force
Copy-Item -LiteralPath (Join-Path $RepoRoot "submission\kaggle-writeup-copy.md") -Destination (Join-Path $kitRoot "KAGGLE_WRITEUP_COPY.md") -Force

$startHere = @"
CareBridge Local Reviewer Kit
=============================

1. Double-click CareBridgeLocal-Setup-$Version.exe.
2. Open CareBridge Local from the Start Menu.
3. Follow the Runtime Setup Wizard in the app.
4. Try the demo cases in USER_GUIDE.md.

No Python, Node.js, Rust, Docker, or Ollama setup is required for normal users.

Repository:
https://github.com/seveNine97/CareBridge-Local
"@

Set-Content -LiteralPath (Join-Path $kitRoot "START-HERE.txt") -Value $startHere -Encoding UTF8

if (Test-Path $zipOut) {
  Remove-Item -LiteralPath $zipOut -Force
}
Compress-Archive -Path (Join-Path $kitRoot "*") -DestinationPath $zipOut -Force

Write-Host "Reviewer kit created: $zipOut"
