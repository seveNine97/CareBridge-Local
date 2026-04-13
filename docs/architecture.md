# CareBridge Local Architecture

## Runtime shape

CareBridge Local is split into three layers:

1. `apps/desktop`: the offline-first user experience for intake, triage, chat, knowledge import, and exports.
2. `services/local-core`: the local orchestration service that owns persistence, triage rules, retrieval, and model runtime selection.
3. `apps/web`: the public-facing demo and competition story surface.

## Local-core responsibilities

- Bootstrap the seeded `base-health` knowledge pack.
- Persist cases, chunks, pack manifests, and exports in SQLite.
- Run deterministic red-flag triage before any model generation.
- Execute hybrid retrieval over chunk content.
- Stream grounded answers with citations and safety metadata.
- Start and monitor `llama.cpp` or connect to Ollama during development.

## Retrieval strategy

The MVP uses a hybrid scorer:

- Dense-style hashed vectors to preserve ranking behavior without a hard runtime dependency during development.
- Keyword overlap for lexical precision on medical guidance and dosage terms.
- Citation metadata includes the source document, knowledge pack, and score so the desktop app can render evidence chips.

The `EmbeddingGemma` migration point is isolated behind the retrieval interface so the fallback dense encoder can later be swapped for a real local embedding provider.

## Safety model

Safety is rule-first:

- Emergency red flags escalate to `emergency_referral` even if the model is unavailable.
- Missing critical vitals are surfaced before advice is finalized.
- High-risk medication or diagnosis requests degrade into verification language when evidence is weak.
- The chat endpoint always returns machine-readable safety alerts alongside streamed answer text.

## Packaging model

- Desktop distribution targets Windows first.
- Public website is deployment-friendly and documents the product story, architecture, and download paths.
- `Lite Installer` and `Field Bundle` are represented in the docs and UI copy; the repository structure supports both paths by separating runtime state from source code.
