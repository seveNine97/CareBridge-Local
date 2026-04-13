from pathlib import Path
import uuid

from carebridge_local_core.retrieval import HybridRetriever
from carebridge_local_core.storage import Storage


def test_hybrid_retrieval_returns_relevant_hit() -> None:
    local_tmp = Path(".tmp_testdata")
    local_tmp.mkdir(exist_ok=True)
    db_path = local_tmp / f"retrieval-{uuid.uuid4().hex}.db"
    storage = Storage(db_path)
    storage.insert_chunk(
        pack_id="base-health",
        source_title="respiratory",
        source_path="respiratory.md",
        chunk_index=0,
        content="Shortness of breath with blue lips requires urgent referral.",
        keywords=["shortness", "breath", "blue", "lips", "urgent", "referral"],
        embedding=[0.0] * 128,
        metadata={},
    )
    storage.insert_chunk(
        pack_id="base-health",
        source_title="general",
        source_path="general.md",
        chunk_index=0,
        content="Drink fluids and rest for mild symptoms.",
        keywords=["drink", "fluids", "rest"],
        embedding=[0.0] * 128,
        metadata={},
    )
    retriever = HybridRetriever(storage)
    hits = retriever.retrieve("patient has shortness of breath and blue lips", max_results=1)
    assert hits
    assert hits[0].citation.source_title == "respiratory"
