# Resume Highlights

Use CareBridge Local as an end-to-end local AI product project, not as a simple model wrapper.

## Strong Resume Bullets

- Built an offline-first Windows clinical copilot with Tauri, React, FastAPI, SQLite, and local Gemma inference through `llama.cpp`.
- Designed a chat-first product UX for non-technical frontline users, with hidden case creation, triage, knowledge import, and referral export flows behind the primary Q&A surface.
- Implemented rule-first medical safety gating that escalates emergency red flags before LLM generation and returns structured urgency, missing-information prompts, and referral guidance.
- Built a hybrid retrieval pipeline over local knowledge packs, surfacing citation metadata in both triage and chat responses.
- Implemented local model lifecycle management: model catalog, GGUF download/import, progress polling, runtime status checks, hardware-aware E4B/E2B profile selection, and runtime launch presets.
- Packaged a Python FastAPI sidecar as a hidden Windows executable and bundled it into a Tauri installer for one-click end-user deployment.
- Created a release/reviewer workflow with installer mirroring, SHA256 checksum, user guide, paste-ready Kaggle writeup, and build verification.

## Technical Depth To Emphasize

- Local AI systems: `llama.cpp`, GGUF quantization profiles, runtime readiness probing, fallback generation path.
- Full-stack desktop architecture: Tauri shell, React UX, FastAPI sidecar, SQLite persistence, local file exports.
- Safety architecture: deterministic triage before model response, structured safety metadata, emergency referral guardrails.
- Retrieval-Augmented Generation: local document ingestion, chunking, hybrid ranking, citation rendering.
- Productization: PyInstaller sidecar, Tauri installer, artifact hygiene, release packaging, non-technical user onboarding.

## Suggested One-Line Project Description

CareBridge Local: an offline Windows healthcare copilot that packages Gemma local inference, deterministic triage safety rules, RAG citations, and referral export into a one-click desktop application for low-connectivity field care.
