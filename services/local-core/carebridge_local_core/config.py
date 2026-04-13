from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _default_home() -> Path:
    return Path(os.getenv("CAREBRIDGE_HOME", Path.cwd() / ".carebridge")).resolve()


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
        repo_root = Path(__file__).resolve().parents[3]
        return repo_root / "knowledge-packs"


settings = Settings()

