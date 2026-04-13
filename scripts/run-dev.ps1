$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot

Write-Host "Starting CareBridge Local dev stack..."
Write-Host "Backend: http://127.0.0.1:8011"
Write-Host "Desktop web shell: http://127.0.0.1:5174"
Write-Host "Public web demo: http://127.0.0.1:5180"

Start-Process -FilePath powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$repoRoot\\services\\local-core'; python -m carebridge_local_core"
Start-Process -FilePath powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$repoRoot\\apps\\desktop'; npm run dev"
Start-Process -FilePath powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$repoRoot\\apps\\web'; npm run dev"
