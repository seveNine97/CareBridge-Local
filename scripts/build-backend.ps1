param(
  [string]$RepoRoot = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
  $RepoRoot = Split-Path -Parent $PSScriptRoot
}

$serviceDir = Join-Path $RepoRoot "services\local-core"
$distDir = Join-Path $RepoRoot "scripts\dist"
$resourceLocalCore = Join-Path $RepoRoot "apps\desktop\src-tauri\resources\local-core"
$resourceKnowledge = Join-Path $RepoRoot "apps\desktop\src-tauri\resources\knowledge-packs"

if (!(Test-Path $distDir)) { New-Item -ItemType Directory -Path $distDir | Out-Null }
if (!(Test-Path $resourceLocalCore)) { New-Item -ItemType Directory -Path $resourceLocalCore -Force | Out-Null }
if (!(Test-Path $resourceKnowledge)) { New-Item -ItemType Directory -Path $resourceKnowledge -Force | Out-Null }

Push-Location $serviceDir
try {
  python -m pip install pyinstaller
  if ($LASTEXITCODE -ne 0) { throw "pip install pyinstaller failed with exit code $LASTEXITCODE" }
  python -m PyInstaller --noconfirm --clean `
    --name carebridge-local-core `
    --onefile `
    --noconsole `
    --collect-all uvicorn `
    --collect-all fastapi `
    --collect-all pydantic `
    --collect-all pypdf `
    carebridge_local_core\__main__.py
  if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed with exit code $LASTEXITCODE" }
} finally {
  Pop-Location
}

$builtExe = Join-Path $serviceDir "dist\carebridge-local-core.exe"
if (!(Test-Path $builtExe)) {
  throw "PyInstaller output not found: $builtExe"
}

Copy-Item -LiteralPath $builtExe -Destination (Join-Path $distDir "carebridge-local-core.exe") -Force
Copy-Item -LiteralPath $builtExe -Destination (Join-Path $resourceLocalCore "carebridge-local-core.exe") -Force

if (Test-Path $resourceKnowledge) {
  Get-ChildItem -LiteralPath $resourceKnowledge -Force | Remove-Item -Recurse -Force
}
Copy-Item -Path (Join-Path $RepoRoot "knowledge-packs\*") -Destination $resourceKnowledge -Recurse -Force

Write-Host "Backend sidecar built and staged."
