# CareBridge Local v0.1.0

## Highlights
- Migrated from single-file prototype to production-oriented monorepo structure.
- Added local-core API with triage, retrieval, streaming chat, and referral export.
- Added desktop UI workflow for intake, triage, import, chat, and export.
- Added public website for competition storytelling and distribution.
- Added seeded health knowledge pack and submission assets.

## Runtime
- Primary: `llama.cpp` via local `llama-server`.
- Secondary: Ollama development fallback.

## Known limitations
- OCR is placeholder-only for image-heavy inputs.
- Tauri binary packaging requires local Rust toolchain installation.
