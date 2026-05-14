from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Iterator

from carebridge_local_core.models import ModelProfile, RuntimeState


@dataclass
class GenerationRequest:
    system_prompt: str
    user_prompt: str


class InferenceProvider:
    runtime_name: str = "mock"

    def start(
        self,
        profile: ModelProfile,
        model_path: str | None = None,
        endpoint_override: str | None = None,
        runtime_params: dict[str, int | float | str] | None = None,
    ) -> RuntimeState:
        return RuntimeState(status="not_started", detail="Provider start not implemented")

    def generate(self, request: GenerationRequest, state: RuntimeState) -> str:
        raise NotImplementedError

    def stream_generate(self, request: GenerationRequest, state: RuntimeState) -> Iterator[str]:
        yield self.generate(request, state)
