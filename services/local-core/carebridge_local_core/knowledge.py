from __future__ import annotations

import json
import textwrap
from pathlib import Path

from fastapi import UploadFile
from pypdf import PdfReader

from carebridge_local_core.config import settings
from carebridge_local_core.retrieval import text_to_embedding, tokenize
from carebridge_local_core.storage import Storage


def _chunk_text(text: str, chunk_size: int = 900, overlap: int = 120) -> list[str]:
    cleaned = " ".join(text.split())
    if not cleaned:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(cleaned):
        end = min(start + chunk_size, len(cleaned))
        chunks.append(cleaned[start:end])
        if end == len(cleaned):
            break
        start = max(end - overlap, 0)
    return chunks


def _extract_text_from_path(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore")
    if suffix == ".pdf":
        reader = PdfReader(str(path))
        pages = []
        for page in reader.pages:
            pages.append(page.extract_text() or "")
        return "\n".join(pages)
    if suffix in {".png", ".jpg", ".jpeg", ".webp"}:
        return f"Image attachment captured from {path.name}. OCR not enabled in MVP."
    return ""


class KnowledgeService:
    def __init__(self, storage: Storage) -> None:
        self.storage = storage

    def bootstrap_seed_pack(self) -> None:
        pack_root = settings.knowledge_root / "base-health"
        manifest_path = pack_root / "manifest.json"
        docs_dir = pack_root / "documents"
        if not manifest_path.exists() or not docs_dir.exists():
            return
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        pack_id = str(manifest.get("id", "base-health"))
        self.storage.upsert_pack(pack_id, manifest)
        if self.storage.has_pack_chunks(pack_id):
            return
        for path in sorted(docs_dir.glob("*")):
            if not path.is_file():
                continue
            self._ingest_single_document(path, pack_id=pack_id, source_title=path.stem, source_path=str(path))

    def _ingest_single_document(self, path: Path, pack_id: str, source_title: str, source_path: str) -> int:
        text = _extract_text_from_path(path)
        if not text.strip():
            return 0
        chunks = _chunk_text(text)
        for idx, chunk in enumerate(chunks):
            keywords = list(sorted(set(tokenize(chunk)))[0:40])
            self.storage.insert_chunk(
                pack_id=pack_id,
                source_title=source_title,
                source_path=source_path,
                chunk_index=idx,
                content=chunk,
                keywords=keywords,
                embedding=text_to_embedding(chunk),
                metadata={"chunk_index": idx},
            )
        return len(chunks)

    async def ingest_uploads(self, files: list[UploadFile], pack_id: str = "user-upload") -> tuple[int, int, int]:
        imported_docs = 0
        imported_chunks = 0
        skipped_docs = 0
        settings.uploads_dir.mkdir(parents=True, exist_ok=True)

        for upload in files:
            suffix = Path(upload.filename or "file").suffix.lower()
            if suffix not in {".txt", ".md", ".pdf", ".png", ".jpg", ".jpeg", ".webp"}:
                skipped_docs += 1
                continue

            local_name = f"{upload.filename}"
            destination = settings.uploads_dir / local_name
            content = await upload.read()
            destination.write_bytes(content)
            chunk_count = self._ingest_single_document(
                destination,
                pack_id=pack_id,
                source_title=Path(upload.filename or "upload").stem,
                source_path=str(destination.resolve()),
            )
            if chunk_count == 0:
                skipped_docs += 1
                continue
            imported_docs += 1
            imported_chunks += chunk_count

        manifest = {
            "id": pack_id,
            "name": "User Upload Pack",
            "version": "local",
            "language": "mixed",
            "region": "custom",
            "license": "user-provided",
            "updated_at": "local",
            "description": textwrap.shorten("User imported files for local retrieval.", width=80),
        }
        self.storage.upsert_pack(pack_id, manifest)
        return imported_docs, imported_chunks, skipped_docs
