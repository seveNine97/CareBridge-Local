from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass

from carebridge_local_core.models import EvidenceCitation
from carebridge_local_core.storage import Storage

TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9]+")
EMBED_DIM = 128


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_PATTERN.findall(text)]


def text_to_embedding(text: str, dim: int = EMBED_DIM) -> list[float]:
    vec = [0.0] * dim
    tokens = tokenize(text)
    if not tokens:
        return vec
    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
        index = int(digest[:8], 16) % dim
        vec[index] += 1.0
    norm = math.sqrt(sum(v * v for v in vec))
    if norm == 0:
        return vec
    return [v / norm for v in vec]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0
    return float(sum(a * b for a, b in zip(left, right)))


def keyword_overlap_score(query_tokens: set[str], doc_tokens: set[str]) -> float:
    if not query_tokens or not doc_tokens:
        return 0.0
    intersection = len(query_tokens.intersection(doc_tokens))
    union = len(query_tokens.union(doc_tokens))
    return intersection / max(union, 1)


@dataclass
class RetrievalHit:
    citation: EvidenceCitation
    chunk_text: str


class HybridRetriever:
    def __init__(self, storage: Storage) -> None:
        self.storage = storage

    def retrieve(self, query: str, max_results: int = 4) -> list[RetrievalHit]:
        query_embedding = text_to_embedding(query)
        query_tokens = set(tokenize(query))

        scored: list[tuple[float, dict]] = []
        for chunk in self.storage.iter_chunks():
            dense = cosine_similarity(query_embedding, chunk["embedding"])
            lexical = keyword_overlap_score(query_tokens, set(chunk["keywords"]))
            score = (0.7 * dense) + (0.3 * lexical)
            scored.append((score, chunk))

        scored.sort(key=lambda item: item[0], reverse=True)
        top = scored[: max(max_results, 1)]

        output: list[RetrievalHit] = []
        for score, chunk in top:
            snippet = chunk["content"].strip().replace("\n", " ")
            citation = EvidenceCitation(
                citation_id=f"chunk-{chunk['chunk_id']}",
                source_title=chunk["source_title"],
                source_path=chunk["source_path"],
                knowledge_pack_id=chunk["pack_id"],
                score=round(score, 4),
                snippet=snippet[:220],
            )
            output.append(RetrievalHit(citation=citation, chunk_text=chunk["content"]))
        return output
