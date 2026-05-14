from __future__ import annotations

import ctypes
import os
import platform
from collections.abc import Iterator
from datetime import datetime, timezone
from uuid import uuid4

from carebridge_local_core.inference.base import GenerationRequest
from carebridge_local_core.inference.llamacpp import LlamaCppProvider
from carebridge_local_core.inference.ollama import OllamaProvider
from carebridge_local_core.model_manager import ModelManager
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


def _estimate_physical_cores() -> int:
    cpu_count = os.cpu_count() or 4
    return max(cpu_count // 2, 2)


class RuntimeManager:
    def __init__(self, model_manager: ModelManager) -> None:
        self.model_manager = model_manager
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

    def choose_profile(self, preferred: str, runtime: RuntimeKind) -> tuple[ModelProfile, str | None]:
        memory_gb = _estimate_memory_gb()
        cores = _estimate_physical_cores()
        candidates = [profile for profile in self.profiles if profile.runtime == runtime]
        if not candidates:
            raise ValueError(f"No profiles available for runtime={runtime}")

        if preferred != "auto":
            preferred_match = next((profile for profile in candidates if profile.profile_name == preferred), None)
            if preferred_match:
                return preferred_match, None

        if runtime == RuntimeKind.llama_cpp:
            balanced = next(profile for profile in candidates if profile.profile_name == "balanced")
            compatibility = next(profile for profile in candidates if profile.profile_name == "compatibility")
            if memory_gb >= 12 and cores >= 4:
                return balanced, None
            reason = f"auto fallback to compatibility profile (memory={memory_gb}GB, physical_cores={cores})."
            return compatibility, reason
        return candidates[0], None

    def start(
        self,
        runtime: RuntimeKind,
        preferred_profile: str,
        model_path: str | None,
        endpoint_override: str | None,
        runtime_params: dict[str, int | float | str] | None = None,
    ) -> RuntimeState:
        profile, fallback_reason = self.choose_profile(preferred_profile, runtime)
        resolved_model_path = model_path
        if runtime == RuntimeKind.llama_cpp and not resolved_model_path:
            local_model = self.model_manager.resolve_model_path(profile.profile_name)
            resolved_model_path = str(local_model) if local_model else None
        if runtime == RuntimeKind.llama_cpp:
            self.state = self.llama_provider.start(
                profile,
                model_path=resolved_model_path,
                endpoint_override=endpoint_override,
                runtime_params=runtime_params,
            )
        elif runtime == RuntimeKind.ollama:
            self.state = self.ollama_provider.start(
                profile,
                model_path=resolved_model_path,
                endpoint_override=endpoint_override,
                runtime_params=runtime_params,
            )
        else:
            self.state = RuntimeState(
                active_profile=profile,
                status="ready",
                detail="Mock runtime selected for offline fallback.",
                endpoint=None,
            )
        if fallback_reason:
            self.state.meta["profile_fallback_reason"] = fallback_reason
        self.state.meta["detected_memory_gb"] = _estimate_memory_gb()
        self.state.meta["detected_physical_cores"] = _estimate_physical_cores()
        return self.state

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        return "".join(self.stream_generate(system_prompt=system_prompt, user_prompt=user_prompt))

    def stream_generate(self, system_prompt: str, user_prompt: str) -> Iterator[str]:
        request = GenerationRequest(system_prompt=system_prompt, user_prompt=user_prompt)
        runtime = self.state.active_profile.runtime if self.state.active_profile else RuntimeKind.mock
        try:
            if runtime == RuntimeKind.llama_cpp and self.state.status == "ready":
                yield from self.llama_provider.stream_generate(request, self.state)
                return
            if runtime == RuntimeKind.ollama and self.state.status == "ready":
                yield from self.ollama_provider.stream_generate(request, self.state)
                return
        except Exception as exc:  # noqa: BLE001
            self.state.status = "degraded"
            self.state.detail = f"Runtime degraded after generation error: {exc}"
        reason = self.state.detail or "Runtime is not ready. Start runtime after installing llama.cpp and a GGUF model."
        yield (
            "CareBridge safety response: local model generation is not available right now. "
            f"Reason: {reason} "
            "Use the rule-based triage, red flags, and cited guidance below, then verify at the nearest clinic."
        )

    def status_payload(self) -> dict:
        status = {
            "status": self.state.status,
            "detail": self.state.detail,
            "endpoint": self.state.endpoint,
            "active_profile": self.state.active_profile.model_dump() if self.state.active_profile else None,
            "heartbeat": datetime.now(timezone.utc).isoformat(),
            "session_id": str(uuid4()),
            "runtime_binary_path": str(self.model_manager.runtime_binary_path()),
            "runtime_binary_present": self.model_manager.runtime_binary_path().exists(),
        }
        if self.state.active_profile and self.state.active_profile.runtime == RuntimeKind.llama_cpp:
            status["llama_process"] = self.llama_provider.status_meta()
        status["meta"] = self.state.meta
        return status
