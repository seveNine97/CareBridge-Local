# CareBridge Local

CareBridge Local is a Windows-first, offline community health worker copilot for the [Gemma 4 Good Hackathon](https://www.kaggle.com/competitions/gemma-4-good-hackathon). It is packaged as a real desktop application: reviewers and field users install it once, open directly to an instant Q&A screen, and complete model setup inside the interface when needed. They do not need Python, Node.js, Rust, Ollama, or command-line dependency setup.

## For Reviewers

1. Open the [GitHub repository](https://github.com/seveNine97/CareBridge-Local).
2. Download the Windows installer from [`release/CareBridgeLocal-Setup-1.0.0.exe`](release/CareBridgeLocal-Setup-1.0.0.exe).
3. Run `CareBridgeLocal-Setup-1.0.0.exe`.
4. Open CareBridge Local and ask a question on the first screen.
5. Expand Runtime Setup or Clinical Case Tools only when needed.

If you are reviewing from source instead of a release artifact, use `docs/REVIEWER_QUICKSTART.md`.

## What The App Does

- Chat-first offline Q&A home screen for immediate use.
- Guided intake for patient label, symptoms, risk factors, notes, and local attachments.
- Rule-first triage that flags emergency referral cases before model generation.
- Offline knowledge ingestion for `TXT`, `MD`, and `PDF` files.
- Hybrid retrieval with citations so answers remain grounded in local reference material.
- Local Gemma chat through `llama.cpp`, with an Ollama adapter kept for development.
- Referral export that writes a printable HTML handout and JSON packet to local storage.
- In-app model/runtime setup for downloading or importing GGUF models.

## Architecture

```text
apps/desktop      Tauri 2 + React desktop product
apps/web          Next.js public story/reviewer site
services/local-core
                  FastAPI sidecar, SQLite, triage, retrieval, exports, runtime manager
knowledge-packs   Seeded offline medical reference pack
submission        Kaggle-ready writeup, video script, judging map, release notes
scripts           Build and reviewer-kit packaging scripts
```

The desktop installer bundles the local FastAPI sidecar and seeded knowledge pack. The sidecar is built as a hidden no-console process, so normal users see only the CareBridge desktop app. Model weights are not committed to git because of size and licensing constraints; users can download/import them through the app.

## One-Command Release Build

For maintainers preparing a Windows release:

```powershell
.\scripts\build-desktop.ps1 -LlamaZipPath "C:\path\to\llama.cpp-win-cpu-x64.zip"
.\scripts\package-reviewer-kit.ps1
```

This produces:

- NSIS installer: `artifacts/CareBridgeLocal-Setup-1.0.0.exe`
- MSI installer: `artifacts/CareBridgeLocal_1.0.0_x64_en-US.msi`
- Reviewer kit zip: `artifacts/CareBridge-Local-Reviewer-Kit-v1.0.0.zip`

The reviewer kit includes the installer plus a `START-HERE.txt` file written for non-technical users.

For the Kaggle submission repository, the NSIS installer is also mirrored under `release/` so judges can download it directly from GitHub without building from source.

## Local Development

Only developers need these commands.

```powershell
# Backend
cd services/local-core
python -m venv .venv
.\.venv\Scripts\activate
pip install -e .[dev]
python -m carebridge_local_core
```

```powershell
# Desktop frontend
npm install
npm run desktop:dev
```

```powershell
# Public website
npm run web:dev
```

## Verification

```powershell
cd services/local-core
python -m pytest
cd ..\..
npm run desktop:build
npm run web:build
```

Current expected result: backend tests pass, desktop production build passes, and web production build passes.

## Submission Assets

- Paste-ready Kaggle writeup: `submission/kaggle-writeup-copy.md`
- Final technical writeup: `submission/kaggle-writeup-final.md`
- Demo script: `submission/video-script-final.md`
- Judging map: `submission/judging-mapping-final.md`
- Release notes: `submission/release-notes-v1.0.0.md`
- Resume technical highlights: `docs/RESUME_HIGHLIGHTS.md`

## Safety Note

CareBridge Local is not a diagnosis engine and does not replace clinicians. It is designed to help frontline workers identify red flags, ask missing-information questions, explain next steps, and prepare referral handoffs while keeping data local.
