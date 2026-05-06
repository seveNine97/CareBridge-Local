param(
  [string]$RepoRoot = "",
  [string]$LlamaZipPath = "C:\Users\seveNine\Downloads\llama-b8814-bin-win-cpu-x64.zip"
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
  $RepoRoot = Split-Path -Parent $PSScriptRoot
}

if (!(Test-Path $LlamaZipPath)) {
  throw "llama.cpp archive not found: $LlamaZipPath"
}

$runtimeResourceDir = Join-Path $RepoRoot "apps\desktop\src-tauri\resources\runtime\llama.cpp"
if (!(Test-Path $runtimeResourceDir)) {
  New-Item -ItemType Directory -Path $runtimeResourceDir -Force | Out-Null
}
Get-ChildItem -LiteralPath $runtimeResourceDir -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force

tar -xf $LlamaZipPath -C $runtimeResourceDir
Write-Host "llama.cpp runtime bundled to $runtimeResourceDir"
