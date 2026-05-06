from __future__ import annotations

import os
import platform
import subprocess
import time
from pathlib import Path

import httpx

from carebridge_local_core.config import settings
from carebridge_local_core.inference.base import GenerationRequest, InferenceProvider
from carebridge_local_core.models import ModelProfile, RuntimeState


class LlamaCppProvider(InferenceProvider):
    runtime_name = "llama_cpp"

    def __init__(self) -> None:
        self._process: subprocess.Popen[str] | None = None
        self._last_command: list[str] = []

    def _binary_path(self) -> Path:
        file_name = "llama-server.exe" if platform.system().lower().startswith("win") else "llama-server"
        return Path(os.getenv("CAREBRIDGE_LLAMA_SERVER", settings.llama_dir / file_name))

    def start(
        self,
        profile: ModelProfile,
        model_path: str | None = None,
        endpoint_override: str | None = None,
        runtime_params: dict[str, int | float | str] | None = None,
    ) -> RuntimeState:
        runtime_params = runtime_params or {}
        endpoint = endpoint_override or "http://127.0.0.1:8012"
        if endpoint_override:
            return RuntimeState(
                active_profile=profile,
                status="ready",
                detail="Connected to externally managed llama.cpp endpoint.",
                endpoint=endpoint,
                meta={"runtime_params": runtime_params},
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

        self.stop()

        host = "127.0.0.1"
        port = "8012"
        command = self._build_command(binary=binary, model_path=resolved_model, profile_name=profile.profile_name, runtime_params=runtime_params)
        self._last_command = command.copy()
        self._process = subprocess.Popen(
            command,
            cwd=str(settings.llama_dir),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        ready, detail = self._wait_until_ready(f"http://{host}:{port}")
        return RuntimeState(
            active_profile=profile,
            status="ready" if ready else "degraded",
            detail=detail,
            endpoint=f"http://{host}:{port}",
            process_id=self._process.pid if self._process else None,
            meta={"runtime_params": runtime_params, "launch_command": command},
        )

    def stop(self) -> None:
        if self._process and self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
        self._process = None

    def status_meta(self) -> dict[str, str | int | bool | list[str] | None]:
        return {
            "process_alive": bool(self._process and self._process.poll() is None),
            "process_id": self._process.pid if self._process else None,
            "launch_command": self._last_command,
        }

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
            "top_p": 0.9,
        }
        with httpx.Client(timeout=80) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
        return str(data["choices"][0]["message"]["content"])

    @staticmethod
    def _build_command(
        binary: Path,
        model_path: Path,
        profile_name: str,
        runtime_params: dict[str, int | float | str],
    ) -> list[str]:
        core_count = max((os.cpu_count() or 4) // 2, 2)
        defaults = {
            "balanced": {"ctx_size": 4096, "threads": core_count, "threads_batch": core_count, "batch_size": 512, "ubatch_size": 256},
            "compatibility": {"ctx_size": 4096, "threads": core_count, "threads_batch": core_count, "batch_size": 768, "ubatch_size": 384},
        }
        selected = defaults.get(profile_name, defaults["compatibility"])
        command = [
            str(binary),
            "-m",
            str(model_path),
            "--host",
            "127.0.0.1",
            "--port",
            "8012",
            "--ctx-size",
            str(int(runtime_params.get("ctx_size", selected["ctx_size"]))),
            "--threads",
            str(int(runtime_params.get("threads", selected["threads"]))),
            "--threads-batch",
            str(int(runtime_params.get("threads_batch", selected["threads_batch"]))),
            "--batch-size",
            str(int(runtime_params.get("batch_size", selected["batch_size"]))),
            "--ubatch-size",
            str(int(runtime_params.get("ubatch_size", selected["ubatch_size"]))),
            "--temp",
            str(float(runtime_params.get("temp", 0.2))),
            "--top-p",
            str(float(runtime_params.get("top_p", 0.9))),
            "--repeat-penalty",
            str(float(runtime_params.get("repeat_penalty", 1.05))),
        ]
        return command

    @staticmethod
    def _wait_until_ready(endpoint: str, timeout_seconds: float = 45.0) -> tuple[bool, str]:
        deadline = time.perf_counter() + timeout_seconds
        last_error = "waiting"
        with httpx.Client(timeout=5) as client:
            while time.perf_counter() < deadline:
                try:
                    response = client.get(f"{endpoint}/health")
                    if response.status_code < 500:
                        return True, "llama.cpp launched and health endpoint is ready."
                except Exception as exc:  # noqa: BLE001
                    last_error = str(exc)
                time.sleep(0.4)
        return False, f"llama.cpp launched but not ready within timeout: {last_error}"
