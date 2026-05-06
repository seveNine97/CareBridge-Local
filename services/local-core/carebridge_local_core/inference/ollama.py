from __future__ import annotations

import httpx

from carebridge_local_core.inference.base import GenerationRequest, InferenceProvider
from carebridge_local_core.models import ModelProfile, RuntimeState


class OllamaProvider(InferenceProvider):
    runtime_name = "ollama"

    def start(
        self,
        profile: ModelProfile,
        model_path: str | None = None,
        endpoint_override: str | None = None,
        runtime_params: dict[str, int | float | str] | None = None,
    ) -> RuntimeState:
        endpoint = endpoint_override or "http://127.0.0.1:11434"
        return RuntimeState(
            active_profile=profile,
            status="ready",
            detail="Using Ollama endpoint.",
            endpoint=endpoint,
        )

    def generate(self, request: GenerationRequest, state: RuntimeState) -> str:
        if state.endpoint is None or state.active_profile is None:
            raise RuntimeError("Ollama runtime is not initialized")
        url = f"{state.endpoint.rstrip('/')}/api/chat"
        payload = {
            "model": state.active_profile.model_name,
            "messages": [
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_prompt},
            ],
            "stream": False,
            "options": {"temperature": 0.2},
        }
        with httpx.Client(timeout=40) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
        return str(data.get("message", {}).get("content", ""))
