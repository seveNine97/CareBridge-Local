# CareBridge Local API Contract (MVP)

Base URL: `http://127.0.0.1:8011`

## `GET /health`

Returns service health, runtime status, installed packs, case count, and chunk count.

## `POST /runtime/start`

Request:

```json
{
  "runtime": "llama_cpp",
  "preferred_profile": "auto",
  "model_path": null,
  "endpoint_override": null,
  "runtime_params": {}
}
```

Starts local runtime selection and returns the active model profile.

## `GET /runtime/status`

Returns runtime process health, endpoint, selected profile metadata, and launch diagnostics.

## `GET /models/catalog`

Returns:
- runtime binary presence/path
- available model catalog (`E4B` / `E2B`)
- installed model flags and local paths

## `POST /models/download`

Starts an in-app background model download task.

## `GET /models/download/{task_id}`

Returns task progress (bytes, speed, eta, status, errors).

## `POST /models/import`

Multipart upload for local GGUF import:
- `file` field with `.gguf`

## `POST /runtime/install-llama`

Multipart upload for llama.cpp runtime archive:
- `file` field with `.zip`

## `POST /cases`

Creates a patient case record and persists it in SQLite.

## `POST /triage/run`

Request:

```json
{
  "case_id": "optional",
  "patient": {
    "...": "PatientCaseCreate"
  }
}
```

Returns rule-backed triage assessment with safety alerts and citations.

## `POST /knowledge/import`

Multipart upload:

- `pack_id` as form field
- one or more `files`

Supported file types: `txt`, `md`, `pdf`, `png`, `jpg`, `jpeg`, `webp`.

## `POST /chat/stream`

Streams Server-Sent Events:

- `metadata` event with triage and citations
- repeated `chunk` events with generated text tokens
- final `done` event

## `POST /export/referral`

Writes both HTML and JSON referral artifacts to local export storage and returns absolute output paths.
