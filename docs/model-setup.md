# Model and Runtime Setup

This project runs with `llama.cpp` by default and keeps Ollama as an optional development fallback.

## Required artifacts

1. `llama-server.exe` binary from llama.cpp releases  
Link: [https://github.com/ggml-org/llama.cpp/releases](https://github.com/ggml-org/llama.cpp/releases)

2. One Gemma 4 GGUF model:
- Balanced profile (recommended): [gemma-4-E4B-it-Q4_K_M.gguf](https://huggingface.co/ggml-org/gemma-4-E4B-it-GGUF/resolve/main/gemma-4-E4B-it-Q4_K_M.gguf?download=true)
- Compatibility profile: [gemma-4-E2B-it-Q4_K_M.gguf](https://huggingface.co/ggml-org/gemma-4-E2B-it-GGUF/resolve/main/gemma-4-E2B-it-Q4_K_M.gguf?download=true)

## Automatic setup script

```powershell
cd scripts
.\setup-models.ps1 -Profile balanced -LlamaServerPath "C:\path\to\llama-server.exe"
```

If your network is unstable, open the direct links in a browser/download manager and place files manually:

- Model path: `.carebridge/models/`
- Runtime path: `.carebridge/runtime/llama.cpp/llama-server.exe`

## Runtime start

After files are placed:

1. Start backend `python -m carebridge_local_core` from `services/local-core`.
2. Call `POST /runtime/start` or click `Start Runtime` in desktop UI.

## Optional Ollama dev fallback

Ollama runtime is still supported for development:

```json
{
  "runtime": "ollama",
  "preferred_profile": "dev-ollama",
  "endpoint_override": "http://127.0.0.1:11434"
}
```
