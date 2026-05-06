# CareBridge Local v1.0.0

## Major Updates
- Added in-app runtime setup wizard for llama.cpp runtime install and model setup.
- Added Model Manager APIs: catalog, download task, progress polling, and model import.
- Extended runtime API with auto profile selection, hardware-aware fallback, and status endpoint.
- Tuned llama.cpp launch presets for E4B/E2B with parameterized start options and readiness probing.
- Added Windows packaging pipeline for desktop bundle with sidecar backend and runtime resources.

## Distribution Model
- Installer includes app shell, local-core sidecar, seed knowledge packs, and llama.cpp runtime.
- Gemma model is not hard-bundled (size control); users can download in app or import local GGUF.
- No Ollama dependency for end users.

## Safety and Workflow
- Rule-based emergency triage remains mandatory and model-independent.
- RAG citations remain visible in triage and chat outputs.
- Referral export pipeline retained for operational handoff.
