# CareBridge Local: Offline Clinical Copilot for Community Health Workers

## 1. Problem and motivation
Community health workers in weak-connectivity settings often work without stable internet, specialist support, or trusted digital tools. They need practical support for triage, evidence lookup, and patient communication without sending sensitive data to cloud services.

## 2. Solution summary
CareBridge Local is a Windows-first offline product with two deliverables:
- Desktop app (Tauri + hidden local FastAPI sidecar): chat-first Q&A, intake, triage, grounded chat, referral export.
- Public demo site (Next.js): story, architecture, download, and judging walkthrough.

The key submission upgrade is deployability and usability. Reviewers and field users install a Windows app, open directly to an instant Q&A surface, and can complete model setup in the interface. They do not need Python, Node.js, Rust, Docker, Ollama, or manual dependency installation.

## 3. Why Gemma 4
Gemma 4 provides strong multilingual reasoning while remaining practical for edge deployment through GGUF quantization. We use:
- Balanced profile: `gemma-4-E4B-it-Q4_K_M` for 16GB-class devices.
- Compatibility profile: `gemma-4-E2B-it-Q4_K_M` fallback for lower-resource hardware.

This profile strategy enables a single product UX across mixed field hardware.

## 4. Technical architecture
- Desktop layer: Tauri 2 + React chat-first home screen + runtime setup wizard + intake/triage/export workflow.
- Local-core layer: FastAPI + SQLite + safety rule engine + hybrid retrieval + model manager.
- Runtime layer: `llama.cpp` (`llama-server`) as production runtime with tunable launch parameters.
- Packaging: desktop installer bundles local-core sidecar and llama.cpp runtime binaries; model is downloaded/imported in app.
- The sidecar is packaged without a visible console so users interact only with the CareBridge desktop app.

## 5. Safety and trust
- Rule-first emergency guardrails are executed before model output.
- Red flag scenarios (chest pain, respiratory distress, altered consciousness, pregnancy bleeding, infant high fever) force emergency referral paths.
- Missing critical vitals trigger clarification prompts.
- For high-risk medication/diagnosis questions with weak evidence, responses degrade to referral/verification language instead of freeform certainty.

## 6. Evaluation and testing
We validated four dimensions:
- Installability: clean Windows install with no manual Python/Ollama setup.
- Runtime behavior: E4B launch path, low-memory fallback to E2B, runtime health reporting.
- Clinical flow: case creation -> triage -> grounded chat with citations -> referral export under offline mode.
- Safety/RAG quality: emergency trigger stability, citation coverage presence, and traceable source metadata.

Repository verification also checks that large installers, model weights, runtime bundles, and build caches are excluded from git while the scripts can rebuild the reviewer kit.

## 7. Demo scenarios
1. Pediatric fever with dehydration risk.
2. Pregnancy danger sign escalation.
3. Medication/label ambiguity with safe patient instructions.

## 8. Real-world impact
CareBridge Local is designed for privacy-sensitive field settings where internet reliability is poor and cloud tools are not operationally feasible. It provides practical, evidence-grounded assistance while preserving local data control.

## 9. Limitations and next steps
- Expand OCR/multimodal extraction robustness for noisy image inputs.
- Add localized guideline packs and region-specific medication catalogs.
- Add opt-in offline quality telemetry bundles for NGO or district-level improvement loops.

## 10. Links
- Code repository: https://github.com/seveNine97/CareBridge-Local
- Windows installer: https://github.com/seveNine97/CareBridge-Local/raw/master/release/CareBridgeLocal-Setup-1.0.0.exe
- User guide: https://github.com/seveNine97/CareBridge-Local/blob/master/docs/USER_GUIDE.md
- Paste-ready writeup: https://github.com/seveNine97/CareBridge-Local/blob/master/submission/kaggle-writeup-copy.md
