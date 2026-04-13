# Live Demo Runbook

## Pre-demo checklist
1. Start backend: `cd services/local-core && python -m carebridge_local_core`
2. Start desktop shell: `cd apps/desktop && npm run dev`
3. Start website: `cd apps/web && npm run dev`
4. Verify health endpoint: `http://127.0.0.1:8011/health`
5. Verify model availability and click `Start Runtime`.

## If model runtime fails
- Continue demo with rule-based triage + citations from seeded knowledge pack.
- Explicitly state that runtime fallback keeps safety workflow active offline.

## If network drops
- Use locally cached app and pre-downloaded model files under `.carebridge/models`.
- Continue with desktop demo only; website can be shown from local host.
