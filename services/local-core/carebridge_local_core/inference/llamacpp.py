from __future__ import annotations

import os
import platform
import subprocess
from pathlib import Path

import httpx

from carebridge_local_core.config import settings
from carebridge_local_core.inference.base import GenerationRequest, InferenceProvider
from carebridge_local_core.models import ModelProfile, RuntimeState


class LlamaCppProvider(InferenceProvider):
    runtime_name = "llama_cpp"

    def __init__(self) -> None:
        self._process: subprocess.Popen[str] | None = None

    def _binary_path(self) -> Path:
        file_name = "llama-server.exe" if platform.system().lower().startswith("win") else "llama-server"
        return Path(os.getenv("CAREBRIDGE_LLAMA_SERVER", settings.llama_dir / file_name))

    def start(self, profile: ModelProfile, model_path: str | None = None, endpoint_override: str | None = None) -> RuntimeState:
        endpoint = endpoint_override or "http://127.0.0.1:8012"
        if endpoint_override:
            return RuntimeState(
                active_profile=profile,
                status="ready",
                detail="Connected to externally managed llama.cpp endpoint.",
                endpoint=endpoint,
            )

        binary = self._binary_path()
        if not binary.exists():
            return RuntimeState(
                active_profile=profile,
                status="degraded",
                detail=f"llama-server not found at {binary}",
                endpoint=endpoint,
            )

        resolved_model = Path(model_path) if model_path else settings.models_dir / f"{profile.model_name}.gguf"
        if not resolved_model.exists():
            return RuntimeState(
                active_profile=profile,
                status="degraded",
                detail=f"Model file not found at {resolved_model}",
                endpoint=endpoint,
            )

        if self._process and self._process.poll() is None:
            return RuntimeState(
                active_profile=profile,
                status="ready",
                detail="llama.cpp process already running.",
                endpoint=endpoint,
                process_id=self._process.pid,
            )

        host = "127.0.0.1"
        port = "8012"
        cmd = [
            str(binary),
            "-m",
            str(resolved_model),
            "--host",
            host,
            "--port",
            port,
            "--ctx-size",
            "4096",
        ]
        self._process = subprocess.Popen(cmd, cwd=str(settings.llama_dir), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return RuntimeState(
            active_profile=profile,
            status="ready",
            detail="llama.cpp launched.",
            endpoint=endpoint,
            process_id=self._process.pid,
        )

    def generate(self, request: GenerationRequest, state: RuntimeState) -> str:
        if state.endpoint is None:
            raise RuntimeError("llama.cpp endpoint is not configured")
        url = f"{state.endpoint.rstrip('/')}/v1/chat/completions"
        payload = {
            "model": (state.active_profile.model_name if state.active_profile else "gemma"),
            "messages": [
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_prompt},
            ],
            "temperature": 0.2,
        }
        with httpx.Client(timeout=40) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
        return str(data["choices"][0]["message"]["content"])
