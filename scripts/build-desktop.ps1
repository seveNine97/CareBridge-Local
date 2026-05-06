param(
  [string]$RepoRoot = "",
  [string]$LlamaZipPath = "C:\Users\seveNine\Downloads\llama-b8814-bin-win-cpu-x64.zip",
  [switch]$UseLocalProxy = $false,
  [string]$ProxyUrl = "http://127.0.0.1:7890"
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
  $RepoRoot = Split-Path -Parent $PSScriptRoot
}

& (Join-Path $PSScriptRoot "build-backend.ps1") -RepoRoot $RepoRoot
& (Join-Path $PSScriptRoot "prepare-runtime-bundle.ps1") -RepoRoot $RepoRoot -LlamaZipPath $LlamaZipPath

$cargoBin = Join-Path $env:USERPROFILE ".cargo\bin"
if (Test-Path $cargoBin) {
  $env:PATH = "$cargoBin;$env:PATH"
}

if (!(Get-Command cargo -ErrorAction SilentlyContinue)) {
  throw "cargo not found. Install Rust toolchain first: https://rustup.rs/"
}

Push-Location (Join-Path $RepoRoot "apps\desktop")
try {
  if ($UseLocalProxy) {
    $env:HTTP_PROXY = $ProxyUrl
    $env:HTTPS_PROXY = $ProxyUrl
    $env:ALL_PROXY = $ProxyUrl
  }
  npm run build
  if ($LASTEXITCODE -ne 0) { throw "npm run build failed with exit code $LASTEXITCODE" }
  npm run tauri:build
  if ($LASTEXITCODE -ne 0) { throw "npm run tauri:build failed with exit code $LASTEXITCODE" }
} finally {
  Pop-Location
}

$bundleDir = Join-Path $RepoRoot "apps\desktop\src-tauri\target\release\bundle"
Write-Host "Desktop bundle generated under: $bundleDir"
