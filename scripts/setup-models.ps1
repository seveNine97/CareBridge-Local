param(
  [ValidateSet("balanced", "compatibility")]
  [string]$Profile = "balanced",
  [string]$ModelDir = "",
  [string]$LlamaServerPath = ""
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$defaultHome = Join-Path $repoRoot ".carebridge"
if (!(Test-Path $defaultHome)) {
  New-Item -ItemType Directory -Path $defaultHome | Out-Null
}

if ([string]::IsNullOrWhiteSpace($ModelDir)) {
  $ModelDir = Join-Path $defaultHome "models"
}
if (!(Test-Path $ModelDir)) {
  New-Item -ItemType Directory -Path $ModelDir -Force | Out-Null
}

$runtimeDir = Join-Path $defaultHome "runtime\\llama.cpp"
if (!(Test-Path $runtimeDir)) {
  New-Item -ItemType Directory -Path $runtimeDir -Force | Out-Null
}

$modelMap = @{
  balanced = @{
    FileName = "gemma-4-E4B-it-Q4_K_M.gguf"
    Url = "https://huggingface.co/ggml-org/gemma-4-E4B-it-GGUF/resolve/main/gemma-4-E4B-it-Q4_K_M.gguf?download=true"
    Info = "Recommended for >=16GB RAM"
  }
  compatibility = @{
    FileName = "gemma-4-E2B-it-Q4_K_M.gguf"
    Url = "https://huggingface.co/ggml-org/gemma-4-E2B-it-GGUF/resolve/main/gemma-4-E2B-it-Q4_K_M.gguf?download=true"
    Info = "Recommended for lower-memory devices"
  }
}

$selected = $modelMap[$Profile]
$targetFile = Join-Path $ModelDir $selected.FileName

Write-Host "Profile: $Profile ($($selected.Info))"
Write-Host "Model target: $targetFile"

if (Test-Path $targetFile) {
  Write-Host "Model already exists. Skipping download."
} else {
  Write-Host "Attempting direct download..."
  try {
    Invoke-WebRequest -Uri $selected.Url -OutFile $targetFile
    Write-Host "Model downloaded successfully."
  } catch {
    Write-Warning "Automatic download failed. Use manual browser download:"
    Write-Host $selected.Url
    throw
  }
}

if (![string]::IsNullOrWhiteSpace($LlamaServerPath)) {
  if (!(Test-Path $LlamaServerPath)) {
    throw "Provided llama-server path does not exist: $LlamaServerPath"
  }
  $targetBinary = Join-Path $runtimeDir "llama-server.exe"
  Copy-Item -LiteralPath $LlamaServerPath -Destination $targetBinary -Force
  Write-Host "llama-server copied to $targetBinary"
} else {
  Write-Host "No llama-server path provided."
  Write-Host "Download prebuilt binaries from:"
  Write-Host "https://github.com/ggml-org/llama.cpp/releases"
  Write-Host "Then copy llama-server.exe into $runtimeDir"
}

Write-Host ""
Write-Host "Next steps:"
Write-Host "1) Start local-core: python -m carebridge_local_core"
Write-Host "2) In desktop app, click 'Start Runtime'"
