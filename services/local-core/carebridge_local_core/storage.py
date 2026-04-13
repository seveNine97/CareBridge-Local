from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from carebridge_local_core.models import PatientCase


class Storage:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        with self._conn:
            self._conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS cases (
                    case_id TEXT PRIMARY KEY,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS knowledge_packs (
                    pack_id TEXT PRIMARY KEY,
                    manifest_json TEXT NOT NULL,
                    installed_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS knowledge_chunks (
                    chunk_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pack_id TEXT NOT NULL,
                    source_title TEXT NOT NULL,
                    source_path TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    keywords_json TEXT NOT NULL,
                    embedding_json TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS exports (
                    export_id TEXT PRIMARY KEY,
                    case_id TEXT NOT NULL,
                    export_type TEXT NOT NULL,
                    path_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def upsert_case(self, case: PatientCase) -> None:
        payload_json = case.model_dump_json()
        with self._lock, self._conn:
            self._conn.execute(
                """
                INSERT INTO cases(case_id, payload_json, created_at, updated_at)
                VALUES(?, ?, ?, ?)
                ON CONFLICT(case_id) DO UPDATE SET
                  payload_json = excluded.payload_json,
                  updated_at = excluded.updated_at
                """,
                (case.case_id, payload_json, case.created_at.isoformat(), case.updated_at.isoformat()),
            )

    def get_case(self, case_id: str) -> PatientCase | None:
        row = self._conn.execute("SELECT payload_json FROM cases WHERE case_id = ?", (case_id,)).fetchone()
        if row is None:
            return None
        return PatientCase.model_validate_json(row["payload_json"])

    def count_cases(self) -> int:
        row = self._conn.execute("SELECT COUNT(*) AS c FROM cases").fetchone()
        return int(row["c"]) if row else 0

    def upsert_pack(self, pack_id: str, manifest: dict[str, Any]) -> None:
        with self._lock, self._conn:
            self._conn.execute(
                """
                INSERT INTO knowledge_packs(pack_id, manifest_json, installed_at)
                VALUES(?, ?, ?)
                ON CONFLICT(pack_id) DO UPDATE SET
                  manifest_json = excluded.manifest_json,
                  installed_at = excluded.installed_at
                """,
                (pack_id, json.dumps(manifest, ensure_ascii=True), self._now()),
            )

    def list_pack_ids(self) -> list[str]:
        rows = self._conn.execute("SELECT pack_id FROM knowledge_packs ORDER BY pack_id ASC").fetchall()
        return [str(row["pack_id"]) for row in rows]

    def insert_chunk(
        self,
        pack_id: str,
        source_title: str,
        source_path: str,
        chunk_index: int,
        content: str,
        keywords: list[str],
        embedding: list[float],
        metadata: dict[str, Any],
    ) -> None:
        with self._lock, self._conn:
            self._conn.execute(
                """
                INSERT INTO knowledge_chunks(
                    pack_id, source_title, source_path, chunk_index, content,
                    keywords_json, embedding_json, metadata_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    pack_id,
                    source_title,
                    source_path,
                    chunk_index,
                    content,
                    json.dumps(keywords, ensure_ascii=True),
                    json.dumps(embedding, ensure_ascii=True),
                    json.dumps(metadata, ensure_ascii=True),
                    self._now(),
                ),
            )

    def count_chunks(self) -> int:
        row = self._conn.execute("SELECT COUNT(*) AS c FROM knowledge_chunks").fetchone()
        return int(row["c"]) if row else 0

    def has_pack_chunks(self, pack_id: str) -> bool:
        row = self._conn.execute(
            "SELECT COUNT(*) AS c FROM knowledge_chunks WHERE pack_id = ?",
            (pack_id,),
        ).fetchone()
        return bool(row and int(row["c"]) > 0)

    def iter_chunks(self) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            """
            SELECT chunk_id, pack_id, source_title, source_path, chunk_index, content,
                   keywords_json, embedding_json, metadata_json
            FROM knowledge_chunks
            """
        ).fetchall()
        output: list[dict[str, Any]] = []
        for row in rows:
            output.append(
                {
                    "chunk_id": int(row["chunk_id"]),
                    "pack_id": str(row["pack_id"]),
                    "source_title": str(row["source_title"]),
                    "source_path": str(row["source_path"]),
                    "chunk_index": int(row["chunk_index"]),
                    "content": str(row["content"]),
                    "keywords": json.loads(row["keywords_json"]),
                    "embedding": json.loads(row["embedding_json"]),
                    "metadata": json.loads(row["metadata_json"]),
                }
            )
        return output

    def insert_export(self, export_id: str, case_id: str, export_type: str, payload: dict[str, Any]) -> None:
        with self._lock, self._conn:
            self._conn.execute(
                """
                INSERT INTO exports(export_id, case_id, export_type, path_json, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    export_id,
                    case_id,
                    export_type,
                    json.dumps(payload, ensure_ascii=True),
                    self._now(),
                ),
            )
