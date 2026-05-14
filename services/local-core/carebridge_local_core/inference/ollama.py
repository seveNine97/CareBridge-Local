from __future__ import annotations

import json
from collections.abc import Iterator

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
        return "".join(self.stream_generate(request, state))

    def stream_generate(self, request: GenerationRequest, state: RuntimeState) -> Iterator[str]:
        if state.endpoint is None or state.active_profile is None:
            raise RuntimeError("Ollama runtime is not initialized")
        url = f"{state.endpoint.rstrip('/')}/api/chat"
        payload = {
            "model": state.active_profile.model_name,
            "messages": [
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_prompt},
            ],
            "stream": True,
            "options": {"temperature": 0.2},
        }
        with httpx.Client(timeout=40) as client:
            with client.stream("POST", url, json=payload) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if not line:
                        continue
                    data = json.loads(line)
                    token = data.get("message", {}).get("content", "")
                    if token:
                        yield str(token)
                    if data.get("done"):
                        break
