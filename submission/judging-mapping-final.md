# CareBridge Local vs Judging Criteria

## Impact & Vision
- Purpose-built for low-connectivity frontline care workflows, not generic chat.
- Offline-first architecture with local inference and local data persistence.
- Clear outputs used in field practice: triage class, red-flag prompts, referral handoff.

## Video Pitch & Storytelling
- Demonstrates real user path: setup -> triage -> grounded dialogue -> export.
- Uses three high-signal medical scenarios with different safety stakes.
- Shows usability and deployment practicality, not only model demos.

## Technical Depth & Execution
- Production runtime path on `llama.cpp`, with tunable launch parameters and readiness checks.
- In-app model lifecycle: catalog, download task, progress polling, local import.
- Safety architecture: rule-first gating + retrieval-grounded generation + citation surfacing.
- Installer-oriented packaging: Tauri desktop bundle + local-core sidecar + runtime binaries.
