# CareBridge Local: Offline Gemma Copilot for Community Health Workers

CareBridge Local is an offline-first Windows desktop application for community health workers who operate in low-connectivity clinics, outreach routes, and emergency referral settings. The latest version opens directly into a chat-first assistant, similar in spirit to a lightweight field-care version of an instant medical Q&A product: the user asks a question first, while case creation, triage, knowledge import, model setup, and referral export remain available as supporting tools.

The main design decision was to ship this as a product, not a notebook or localhost demo. A reviewer can install the Windows app, open it, and ask a question immediately. They do not need Python, Node.js, Rust, Docker, Ollama, or command-line dependency setup. The local FastAPI sidecar is packaged as a hidden background process so normal users see the CareBridge application rather than backend terminals.

## Why This Matters

Many community health workers are asked to make high-stakes triage decisions with intermittent internet, limited specialist access, and paper-heavy workflows. Cloud-only AI assistants are often unusable in those environments. CareBridge Local keeps the workflow on the device and focuses on practical outputs: urgency level, red flags, missing information, cited guidance, patient explanation, and referral export.

## How Gemma Is Used

CareBridge Local uses Gemma through local GGUF profiles:

- Balanced profile: `gemma-4-E4B-it-Q4_K_M` for 16GB-class devices.
- Compatibility profile: `gemma-4-E2B-it-Q4_K_M` for lower-resource machines.

The app is designed so a field worker can download or import the model inside the desktop interface. The local runtime path uses `llama.cpp`; an Ollama adapter remains available for development and comparison.

## Product Flow

1. Install CareBridge Local from the Windows installer.
2. Open the app and ask a medical workflow question on the first screen.
3. Optionally complete runtime/model setup in the app for local Gemma generation.
4. Optionally save a case, run structured triage, import local guidance, and export a referral packet.

Demo scenarios:

- Pediatric fever with dehydration risk.
- Pregnancy danger signs requiring escalation.
- Medication-label uncertainty with safe verification language.

## Technical Architecture

- Desktop app: Tauri 2 + React + TypeScript.
- Local core: FastAPI sidecar with SQLite persistence.
- Safety layer: deterministic triage rules run before model output.
- Retrieval layer: hybrid lexical/dense-style retrieval over local knowledge packs.
- Runtime layer: `llama.cpp` model manager with download/import/status flows.
- Packaging: Windows installer bundles the desktop app, local core sidecar, and seeded knowledge pack; model weights remain outside git and are imported or downloaded by the user.

## Safety And Trust

CareBridge Local is deliberately rule-first. Emergency signs such as chest pain, breathing distress, altered consciousness, pregnancy bleeding, infant high fever, and severe dehydration escalate to referral language even when model inference is unavailable. Missing vital information is surfaced before advice is finalized. High-risk medication or diagnostic uncertainty degrades to verification and referral language instead of confident unsupported answers.

The model is used as a grounded communication and reasoning assistant, while deterministic safeguards own the highest-risk routing decisions.

## What Was Built

- Full desktop app workflow: intake, triage, knowledge import, grounded chat, referral export.
- Chat-first home screen so instant offline Q&A is the primary user path.
- Local FastAPI core with SQLite, retrieval, model runtime manager, and export APIs.
- In-app runtime setup wizard for `llama.cpp` and GGUF model import/download.
- Hidden no-console local-core sidecar for normal installer use.
- Public web story page for judging and reviewer onboarding.
- Paste-ready submission materials, video script, judging map, and release notes.
- Reviewer kit packaging script for non-technical installation.

## Evaluation

The project was validated with:

- Backend tests for triage and retrieval.
- Desktop production build.
- Web production build.
- Git hygiene checks to ensure large installers and build caches are excluded from source control.

Expected commands:

```powershell
cd services/local-core
python -m pytest
cd ../..
npm run desktop:build
npm run web:build
```

## Limitations And Next Steps

The next most valuable improvements are more regional guideline packs, better OCR for noisy field documents, localized medication catalogs, and opt-in offline quality review bundles for NGOs or district health teams. The current version focuses on the highest-value submission slice: a complete installable offline workflow, local Gemma runtime, safety-first triage, cited answers, and referral export.

## Links

- Code repository: https://github.com/seveNine97/CareBridge-Local
- Windows installer: https://github.com/seveNine97/CareBridge-Local/raw/master/release/CareBridgeLocal-Setup-1.0.0.exe
- Competition: https://www.kaggle.com/competitions/gemma-4-good-hackathon
