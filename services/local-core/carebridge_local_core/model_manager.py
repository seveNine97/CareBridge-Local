from __future__ import annotations

import hashlib
import shutil
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import httpx

from carebridge_local_core.config import settings
from carebridge_local_core.models import ModelCatalogItem, ModelDownloadStatus


@dataclass(frozen=True)
class CatalogEntry:
    model_id: str
    profile_name: str
    model_name: str
    filename: str
    file_size_bytes: int
    sha256: str | None
    recommended_memory_gb: float
    download_url: str


class ModelManager:
    def __init__(self) -> None:
        self._catalog: dict[str, CatalogEntry] = {
            "gemma4-e4b-q4km": CatalogEntry(
                model_id="gemma4-e4b-q4km",
                profile_name="balanced",
                model_name="gemma-4-E4B-it-Q4_K_M",
                filename="gemma-4-E4B-it-Q4_K_M.gguf",
                file_size_bytes=5_335_289_824,
                sha256=None,
                recommended_memory_gb=16.0,
                download_url=(
                    "https://huggingface.co/ggml-org/gemma-4-E4B-it-GGUF/resolve/main/"
                    "gemma-4-E4B-it-Q4_K_M.gguf?download=true"
                ),
            ),
            "gemma4-e2b-q4km": CatalogEntry(
                model_id="gemma4-e2b-q4km",
                profile_name="compatibility",
                model_name="gemma-4-E2B-it-Q4_K_M",
                filename="gemma-4-E2B-it-Q4_K_M.gguf",
                file_size_bytes=3_003_148_288,
                sha256=None,
                recommended_memory_gb=8.0,
                download_url=(
                    "https://huggingface.co/ggml-org/gemma-4-E2B-it-GGUF/resolve/main/"
                    "gemma-4-E2B-it-Q4_K_M.gguf?download=true"
                ),
            ),
        }
        self._tasks: dict[str, ModelDownloadStatus] = {}
        self._lock = threading.Lock()

    def runtime_binary_path(self) -> Path:
        return settings.llama_dir / "llama-server.exe"

    def catalog(self) -> list[ModelCatalogItem]:
        items: list[ModelCatalogItem] = []
        for entry in self._catalog.values():
            installed_path = settings.models_dir / entry.filename
            items.append(
                ModelCatalogItem(
                    model_id=entry.model_id,
                    profile_name=entry.profile_name,
                    model_name=entry.model_name,
                    filename=entry.filename,
                    file_size_bytes=entry.file_size_bytes,
                    sha256=entry.sha256,
                    recommended_memory_gb=entry.recommended_memory_gb,
                    download_url=entry.download_url,
                    installed=installed_path.exists(),
                    installed_path=str(installed_path) if installed_path.exists() else None,
                )
            )
        return items

    def resolve_model_path(self, profile_name: str) -> Path | None:
        entry = next((entry for entry in self._catalog.values() if entry.profile_name == profile_name), None)
        if entry is None:
            return None
        candidate = settings.models_dir / entry.filename
        return candidate if candidate.exists() else None

    def status(self, task_id: str) -> ModelDownloadStatus | None:
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return None
            return task.model_copy(deep=True)

    def start_download(self, model_id: str, force_redownload: bool = False) -> ModelDownloadStatus:
        if model_id not in self._catalog:
            raise ValueError(f"Unknown model id: {model_id}")

        entry = self._catalog[model_id]
        target_path = settings.models_dir / entry.filename
        if target_path.exists() and not force_redownload:
            done = ModelDownloadStatus(
                task_id=str(uuid4()),
                model_id=model_id,
                status="completed",
                progress=1.0,
                downloaded_bytes=target_path.stat().st_size,
                total_bytes=target_path.stat().st_size,
                file_path=str(target_path),
                sha256_verified=True if entry.sha256 else None,
            )
            with self._lock:
                self._tasks[done.task_id] = done
            return done

        task = ModelDownloadStatus(task_id=str(uuid4()), model_id=model_id, status="queued")
        with self._lock:
            self._tasks[task.task_id] = task
        worker = threading.Thread(
            target=self._download_worker,
            args=(task.task_id, entry, target_path, force_redownload),
            daemon=True,
        )
        worker.start()
        return task

    def import_model_file(self, source_file: Path) -> tuple[str | None, Path]:
        if not source_file.exists():
            raise FileNotFoundError(f"Model file not found: {source_file}")
        destination = settings.models_dir / source_file.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source_file.resolve() != destination.resolve():
            with source_file.open("rb") as src, destination.open("wb") as dst:
                shutil.copyfileobj(src, dst, length=1024 * 1024)
        model_id = next((entry.model_id for entry in self._catalog.values() if entry.filename == destination.name), None)
        return model_id, destination

    def _set_task(self, task_id: str, **updates: object) -> None:
        with self._lock:
            task = self._tasks[task_id]
            self._tasks[task_id] = task.model_copy(update=updates)

    def _download_worker(self, task_id: str, entry: CatalogEntry, target_path: Path, force_redownload: bool) -> None:
        part_path = target_path.with_suffix(target_path.suffix + ".part")
        try:
            self._set_task(task_id, status="downloading", file_path=str(target_path))
            if force_redownload:
                if target_path.exists():
                    target_path.unlink()
                if part_path.exists():
                    part_path.unlink()

            downloaded = part_path.stat().st_size if part_path.exists() else 0
            headers: dict[str, str] = {}
            if downloaded > 0:
                headers["Range"] = f"bytes={downloaded}-"

            started_at = time.perf_counter()
            with httpx.stream("GET", entry.download_url, headers=headers, follow_redirects=True, timeout=60) as response:
                response.raise_for_status()
                append_mode = response.status_code == 206 and downloaded > 0
                if not append_mode:
                    downloaded = 0
                total = self._resolve_total_bytes(response, downloaded if append_mode else 0, entry.file_size_bytes)
                write_mode = "ab" if append_mode else "wb"
                with part_path.open(write_mode) as handle:
                    for chunk in response.iter_bytes(chunk_size=1024 * 1024):
                        if not chunk:
                            continue
                        handle.write(chunk)
                        downloaded += len(chunk)
                        elapsed = max(time.perf_counter() - started_at, 0.001)
                        speed = downloaded / elapsed
                        eta = ((total - downloaded) / speed) if (total and speed > 0) else None
                        progress = (downloaded / total) if total else 0.0
                        self._set_task(
                            task_id,
                            downloaded_bytes=downloaded,
                            total_bytes=total,
                            progress=min(progress, 1.0),
                            speed_bps=speed,
                            eta_seconds=eta,
                        )

            part_path.replace(target_path)
            verified = None
            if entry.sha256:
                verified = self._verify_sha256(target_path, entry.sha256)
                if not verified:
                    raise RuntimeError("SHA256 verification failed.")
            self._set_task(
                task_id,
                status="completed",
                progress=1.0,
                downloaded_bytes=target_path.stat().st_size,
                total_bytes=target_path.stat().st_size,
                sha256_verified=verified,
            )
        except Exception as exc:  # noqa: BLE001
            self._set_task(task_id, status="failed", error=str(exc))

    @staticmethod
    def _resolve_total_bytes(response: httpx.Response, existing_bytes: int, fallback: int | None) -> int:
        content_range = response.headers.get("content-range")
        if content_range and "/" in content_range:
            _, total_text = content_range.split("/", maxsplit=1)
            if total_text.isdigit():
                return int(total_text)
        content_length = response.headers.get("content-length")
        if content_length and content_length.isdigit():
            return int(content_length) + existing_bytes
        if fallback is not None:
            return fallback
        return existing_bytes

    @staticmethod
    def _verify_sha256(path: Path, expected: str) -> bool:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest().lower() == expected.lower()
