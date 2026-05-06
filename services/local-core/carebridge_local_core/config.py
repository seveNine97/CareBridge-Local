from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _default_home() -> Path:
    configured = os.getenv("CAREBRIDGE_HOME")
    if configured:
        return Path(configured).resolve()
    local_app_data = os.getenv("LOCALAPPDATA")
    if local_app_data:
        candidate = (Path(local_app_data) / "CareBridgeLocal").resolve()
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            return candidate
        except OSError:
            pass
    return (Path.cwd() / ".carebridge").resolve()


@dataclass(frozen=True)
class Settings:
    host: str = os.getenv("CAREBRIDGE_HOST", "127.0.0.1")
    port: int = int(os.getenv("CAREBRIDGE_PORT", "8011"))
    home_dir: Path = _default_home()

    @property
    def db_path(self) -> Path:
        return self.home_dir / "carebridge.db"

    @property
    def uploads_dir(self) -> Path:
        return self.home_dir / "uploads"

    @property
    def exports_dir(self) -> Path:
        return self.home_dir / "exports"

    @property
    def models_dir(self) -> Path:
        return self.home_dir / "models"

    @property
    def runtime_dir(self) -> Path:
        return self.home_dir / "runtime"

    @property
    def llama_dir(self) -> Path:
        return self.runtime_dir / "llama.cpp"

    @property
    def knowledge_root(self) -> Path:
        configured = os.getenv("CAREBRIDGE_KNOWLEDGE_ROOT")
        if configured:
            return Path(configured).resolve()
        repo_root = Path(__file__).resolve().parents[3]
        candidate = repo_root / "knowledge-packs"
        if candidate.exists():
            return candidate
        return self.home_dir / "knowledge-packs"


settings = Settings()
