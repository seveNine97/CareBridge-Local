# Reviewer Quickstart

## Best Path: Release Installer

Use the installer in the repository `release/` folder. This is the intended experience and does not require developer dependencies.

1. Download `CareBridgeLocal-Setup-1.0.0.exe`.
2. Install and open CareBridge Local.
3. Ask a question immediately on the first screen.
4. Expand Runtime Setup or Clinical Case Tools only if you want to test model setup, case saving, triage, or referral export.

## Source Verification Path

Use this only if you want to inspect or build from source.

```powershell
git clone https://github.com/seveNine97/CareBridge-Local.git
cd CareBridge-Local
npm install
cd services/local-core
python -m venv .venv
.\.venv\Scripts\activate
pip install -e .[dev]
python -m pytest
cd ..\..
npm run desktop:build
npm run web:build
```

## Build Release Artifacts

```powershell
.\scripts\build-desktop.ps1 -LlamaZipPath "C:\path\to\llama.cpp-win-cpu-x64.zip"
.\scripts\package-reviewer-kit.ps1
```

The generated reviewer kit is safe to share with non-technical judges because it includes a start-here guide and installer path.
