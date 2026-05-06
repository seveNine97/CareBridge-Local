# CareBridge Local: Offline Clinical Copilot for Community Health Workers

## 1. Problem and motivation
Community health workers in low-connectivity environments need offline triage and evidence support without relying on cloud infrastructure.

## 2. Solution summary
- Offline-first desktop app for intake, triage, grounded chat, and referral export.
- Local FastAPI orchestration with rule-first safety and retrieval-backed evidence.
- Public website for storytelling, onboarding, and download.

## 3. Why Gemma 4
Gemma 4 supports strong multilingual edge inference when packaged as GGUF (`E4B` balanced profile, `E2B` fallback profile).

## 4. Technical architecture
Use the architecture diagram from `docs/architecture.md` / project website in final submission media.

- Desktop layer: Tauri + React.
- Local-core: FastAPI + SQLite + hybrid retrieval + safety engine.
- Runtime layer: llama.cpp (primary), Ollama (dev fallback).
- Knowledge packs: seeded medical docs + user-imported files.

## 5. Safety and trust
- Emergency red flag rules always execute before model guidance.
- Missing critical vitals are surfaced explicitly.
- High-risk dosage/diagnosis requests degrade to verified-referral language when evidence is weak.

## 6. Evaluation and testing
Quantitative metrics to include:
- Citation coverage rate
- Red-flag trigger accuracy on scenario set
- Response latency on target hardware

## 7. Demo scenarios
1. Pediatric fever with dehydration risk.
2. Pregnancy danger sign escalation.
3. Medication label ambiguity and safe follow-up guidance.

## 8. Real-world impact
Low-resource deployment model: local installer + in-app model setup + offline workflow + local-only data storage.

## 9. Limitations and next steps
- Add stronger OCR pipeline for image-heavy workflows.
- Add localized guideline packs per country/region.
- Add offline telemetry bundle for quality monitoring (opt-in only).
