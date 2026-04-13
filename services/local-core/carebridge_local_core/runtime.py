from __future__ import annotations

import ctypes
import platform
from datetime import datetime, timezone
from uuid import uuid4

from carebridge_local_core.inference.base import GenerationRequest
from carebridge_local_core.inference.llamacpp import LlamaCppProvider
from carebridge_local_core.inference.ollama import OllamaProvider
from carebridge_local_core.models import ModelProfile, RuntimeKind, RuntimeState


def _estimate_memory_gb() -> float:
    if platform.system().lower().startswith("win"):
        class MemoryStatus(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        mem_status = MemoryStatus()
        mem_status.dwLength = ctypes.sizeof(MemoryStatus)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem_status))
        return round(mem_status.ullTotalPhys / (1024**3), 1)
    return 8.0


class RuntimeManager:
    def __init__(self) -> None:
        self.llama_provider = LlamaCppProvider()
        self.ollama_provider = OllamaProvider()
        self.state = RuntimeState(status="not_started", detail="Runtime not initialized.")

    @property
    def profiles(self) -> list[ModelProfile]:
        return [
            ModelProfile(
                runtime=RuntimeKind.llama_cpp,
                profile_name="balanced",
                model_name="gemma-4-E4B-it-Q4_K_M",
                quantization="Q4_K_M",
                estimated_memory_gb=8.5,
                status="available",
            ),
            ModelProfile(
                runtime=RuntimeKind.llama_cpp,
                profile_name="compatibility",
                model_name="gemma-4-E2B-it-Q4_K_M",
                quantization="Q4_K_M",
                estimated_memory_gb=5.2,
                status="available",
            ),
            ModelProfile(
                runtime=RuntimeKind.ollama,
                profile_name="dev-ollama",
                model_name="gemma3n:latest",
                quantization="managed-by-ollama",
                estimated_memory_gb=6.0,
                status="available",
            ),
        ]

    def choose_profile(self, preferred: str, runtime: RuntimeKind) -> ModelProfile:
        memory_gb = _estimate_memory_gb()
        candidates = [profile for profile in self.profiles if profile.runtime == runtime]
        if not candidates:
            raise ValueError(f"No profiles available for runtime={runtime}")

        preferred_match = next((profile for profile in candidates if profile.profile_name == preferred), None)
        if preferred_match:
            return preferred_match

        if runtime == RuntimeKind.llama_cpp:
            if memory_gb >= 12:
                return next(profile for profile in candidates if profile.profile_name == "balanced")
            return next(profile for profile in candidates if profile.profile_name == "compatibility")
        return candidates[0]

    def start(self, runtime: RuntimeKind, preferred_profile: str, model_path: str | None, endpoint_override: str | None) -> RuntimeState:
        profile = self.choose_profile(preferred_profile, runtime)
        if runtime == RuntimeKind.llama_cpp:
            self.state = self.llama_provider.start(profile, model_path=model_path, endpoint_override=endpoint_override)
        elif runtime == RuntimeKind.ollama:
            self.state = self.ollama_provider.start(profile, model_path=model_path, endpoint_override=endpoint_override)
        else:
            self.state = RuntimeState(
                active_profile=profile,
                status="ready",
                detail="Mock runtime selected for offline fallback.",
                endpoint=None,
            )
        return self.state

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        request = GenerationRequest(system_prompt=system_prompt, user_prompt=user_prompt)
        runtime = self.state.active_profile.runtime if self.state.active_profile else RuntimeKind.mock
        try:
            if runtime == RuntimeKind.llama_cpp and self.state.status == "ready":
                return self.llama_provider.generate(request, self.state)
            if runtime == RuntimeKind.ollama and self.state.status == "ready":
                return self.ollama_provider.generate(request, self.state)
        except Exception as exc:  # noqa: BLE001
            self.state.status = "degraded"
            self.state.detail = f"Runtime degraded after generation error: {exc}"
        return (
            "CareBridge fallback response: local model runtime is unavailable. "
            "Continue with rule-based triage and evidence citations, then verify at the nearest clinic."
        )

    def status_payload(self) -> dict:
        return {
            "status": self.state.status,
            "detail": self.state.detail,
            "endpoint": self.state.endpoint,
            "active_profile": self.state.active_profile.model_dump() if self.state.active_profile else None,
            "heartbeat": datetime.now(timezone.utc).isoformat(),
            "session_id": str(uuid4()),
        }
