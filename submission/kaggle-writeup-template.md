# CareBridge Local: Offline Clinical Copilot for Community Health Workers

## 1. Problem and motivation
TODO: Describe target users (rural clinics, NGO outreach, low-connectivity health workers) and current pain points.

## 2. Solution summary
- Offline-first desktop app for intake, triage, grounded chat, and referral export.
- Local FastAPI orchestration with rule-first safety and retrieval-backed evidence.
- Public website for storytelling, onboarding, and download.

## 3. Why Gemma 4
TODO: Explain selected Gemma profile (`E4B` or `E2B`) and why it fits local hardware.
TODO: Explain how Gemma 4 contributes to multilingual and edge deployment goals.

## 4. Technical architecture
TODO: Insert architecture diagram.

- Desktop layer: Tauri + React.
- Local-core: FastAPI + SQLite + hybrid retrieval + safety engine.
- Runtime layer: llama.cpp (primary), Ollama (dev fallback).
- Knowledge packs: seeded medical docs + user-imported files.

## 5. Safety and trust
- Emergency red flag rules always execute before model guidance.
- Missing critical vitals are surfaced explicitly.
- High-risk dosage/diagnosis requests degrade to verified-referral language when evidence is weak.

## 6. Evaluation and testing
TODO: Add quantitative metrics:
- Citation coverage rate
- Red-flag trigger accuracy on scenario set
- Response latency on target hardware

## 7. Demo scenarios
1. Pediatric fever with dehydration risk.
2. Pregnancy danger sign escalation.
3. Medication label ambiguity and safe follow-up guidance.

## 8. Real-world impact
TODO: Describe deployment model for low-resource clinics and data privacy benefits.

## 9. Limitations and next steps
- Add stronger OCR pipeline for image-heavy workflows.
- Add localized guideline packs per country/region.
- Add offline telemetry bundle for quality monitoring (opt-in only).
