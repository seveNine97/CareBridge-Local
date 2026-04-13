# CareBridge Local

CareBridge Local is an offline-first community health worker copilot built for the [Gemma 4 Good Hackathon](https://www.kaggle.com/competitions/gemma-4-good-hackathon). The repository now ships as a real product workspace instead of a single localhost demo: a desktop app shell, a public landing/demo site, and a local FastAPI service that handles triage, knowledge import, retrieval, and referral exports.

## What Changed

- `apps/desktop`: Tauri 2 + React + TypeScript shell for the offline desktop product.
- `apps/web`: Next.js public demo and story site for the competition submission.
- `services/local-core`: FastAPI service with SQLite persistence, hybrid retrieval, triage rules, runtime abstraction, and export endpoints.
- `knowledge-packs/base-health`: seeded medical reference pack used for out-of-the-box citations.
- `legacy/streamlit`: the original Streamlit prototype source preserved for reference.

## Product Slice Implemented Here

- Guided intake flow for patient details, symptoms, vitals, and risk factors.
- Rule-backed triage output with emergency referral detection, missing-information prompts, and next steps.
- Knowledge ingestion for `TXT`, `MD`, and `PDF` files plus a seeded offline health pack.
- Hybrid retrieval using dense-style hashed vectors plus keyword overlap, with citation metadata surfaced to clients.
- Streaming chat endpoint that returns answer chunks, safety alerts, and citations.
- Referral export endpoint that writes a printable HTML handout and JSON packet to local storage.
- Runtime abstraction for `llama.cpp` and `Ollama`, with `llama.cpp` as the production-first provider.

## Repository Layout

```text
repo/
├─ apps/
│  ├─ desktop/
│  └─ web/
├─ docs/
├─ knowledge-packs/
│  └─ base-health/
├─ legacy/
│  └─ streamlit/
└─ services/
   └─ local-core/
```

## Local Development

### 1. Python service

Create a virtual environment, install the service dependencies, and run the API:

```bash
cd services/local-core
python -m venv .venv
.venv\Scripts\activate
pip install -e .
python -m carebridge_local_core
```

The API defaults to `http://127.0.0.1:8011`.

### 2. Desktop app

```bash
cd apps/desktop
npm install
npm run dev
```

For the full Tauri shell you will also need Rust and the Tauri CLI installed locally.

### 3. Public web app

```bash
cd apps/web
npm install
npm run dev
```

### 4. Optional one-command local dev startup

```powershell
cd scripts
.\run-dev.ps1
```

### 5. Model and runtime setup

Use the model helper script:

```powershell
cd scripts
.\setup-models.ps1 -Profile balanced -LlamaServerPath "C:\path\to\llama-server.exe"
```

Manual links and fallback flow are documented in `docs/model-setup.md`.

## Data and Runtime Notes

- Runtime data is stored under `.carebridge/`.
- SQLite state lives in `.carebridge/carebridge.db`.
- Imported uploads and export packets are written beneath `.carebridge/uploads` and `.carebridge/exports`.
- `llama.cpp` is expected under `.carebridge/runtime/llama.cpp/llama-server(.exe)` unless overridden by environment variables.
- Model files are expected under `.carebridge/models/`.

## Known Constraints In This Workspace

- Rust is not installed in the current environment, so the Tauri shell cannot be built here yet.
- Python service dependencies such as `fastapi` are not installed in the current environment.
- The runtime providers are implemented, but no Gemma model weights or `llama.cpp` binaries are bundled in this repository.

## Legacy Prototype

The original Streamlit project is preserved under `legacy/streamlit`. It remains useful as a reference for the previous hackathon submission, but it is no longer the primary application path.

## Submission Assets

- Editable pack: `submission/`
- Ready zip: `artifacts/carebridge-submission-pack.zip`
