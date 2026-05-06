from __future__ import annotations

import asyncio
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import AsyncGenerator
from uuid import uuid4

import uvicorn
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from carebridge_local_core.config import settings
from carebridge_local_core.exporter import ReferralExporter
from carebridge_local_core.knowledge import KnowledgeService
from carebridge_local_core.model_manager import ModelManager
from carebridge_local_core.models import (
    ChatRequest,
    HealthResponse,
    KnowledgeImportResponse,
    ModelCatalogResponse,
    ModelDownloadRequest,
    ModelDownloadResponse,
    ModelDownloadStatus,
    ModelImportResponse,
    PatientCase,
    PatientCaseCreate,
    ReferralExportRequest,
    ReferralExportResponse,
    RuntimeStartRequest,
    RuntimeStartResponse,
    TriageAssessment,
    TriageRequest,
)
from carebridge_local_core.retrieval import HybridRetriever
from carebridge_local_core.runtime import RuntimeManager
from carebridge_local_core.storage import Storage
from carebridge_local_core.triage import evaluate_triage

storage = Storage(settings.db_path)
retriever = HybridRetriever(storage)
knowledge = KnowledgeService(storage)
model_manager = ModelManager()
runtime_manager = RuntimeManager(model_manager=model_manager)
exporter = ReferralExporter(storage)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _build_case(payload: PatientCaseCreate, case_id: str | None = None) -> PatientCase:
    now = _utcnow()
    return PatientCase(
        case_id=case_id or str(uuid4()),
        created_at=now,
        updated_at=now,
        **payload.model_dump(),
    )


app = FastAPI(
    title="CareBridge Local Core API",
    version="0.1.0",
    description="Offline-first local orchestration API for CareBridge Local.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event() -> None:
    settings.home_dir.mkdir(parents=True, exist_ok=True)
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    settings.exports_dir.mkdir(parents=True, exist_ok=True)
    settings.models_dir.mkdir(parents=True, exist_ok=True)
    settings.runtime_dir.mkdir(parents=True, exist_ok=True)
    settings.llama_dir.mkdir(parents=True, exist_ok=True)
    runtime_bundle = os.getenv("CAREBRIDGE_RUNTIME_BUNDLE")
    if runtime_bundle:
        bundle_dir = Path(runtime_bundle)
        target_binary = settings.llama_dir / "llama-server.exe"
        if bundle_dir.exists() and not target_binary.exists():
            for item in bundle_dir.glob("*"):
                if item.is_file():
                    shutil.copy2(item, settings.llama_dir / item.name)
    knowledge.bootstrap_seed_pack()


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(
        service="carebridge-local-core",
        timestamp=_utcnow(),
        runtime_status=runtime_manager.state.status,
        active_profile=runtime_manager.state.active_profile,
        case_count=storage.count_cases(),
        knowledge_chunk_count=storage.count_chunks(),
        installed_packs=storage.list_pack_ids(),
        notes=[runtime_manager.state.detail] if runtime_manager.state.detail else [],
    )


@app.post("/runtime/start", response_model=RuntimeStartResponse)
async def runtime_start(request: RuntimeStartRequest) -> RuntimeStartResponse:
    state = runtime_manager.start(
        runtime=request.runtime,
        preferred_profile=request.preferred_profile,
        model_path=request.model_path,
        endpoint_override=request.endpoint_override,
        runtime_params=request.runtime_params,
    )
    if state.active_profile is None:
        raise HTTPException(status_code=500, detail="No active profile after runtime start.")
    return RuntimeStartResponse(
        active_profile=state.active_profile,
        available_profiles=runtime_manager.profiles,
        message=state.detail or "Runtime started.",
    )


@app.get("/runtime/status")
async def runtime_status() -> dict:
    return runtime_manager.status_payload()


@app.get("/models/catalog", response_model=ModelCatalogResponse)
async def models_catalog() -> ModelCatalogResponse:
    runtime_binary = model_manager.runtime_binary_path()
    return ModelCatalogResponse(
        runtime_binary_present=runtime_binary.exists(),
        runtime_binary_path=str(runtime_binary),
        models=model_manager.catalog(),
    )


@app.post("/models/download", response_model=ModelDownloadResponse)
async def models_download(request: ModelDownloadRequest) -> ModelDownloadResponse:
    try:
        task = model_manager.start_download(model_id=request.model_id, force_redownload=request.force_redownload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ModelDownloadResponse(
        task_id=task.task_id,
        status=task.status,
        message="Download task started." if task.status != "completed" else "Model already available.",
    )


@app.get("/models/download/{task_id}", response_model=ModelDownloadStatus)
async def models_download_status(task_id: str) -> ModelDownloadStatus:
    task = model_manager.status(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Download task not found: {task_id}")
    return task


@app.post("/models/import", response_model=ModelImportResponse)
async def models_import(file: UploadFile = File(...)) -> ModelImportResponse:
    destination = settings.models_dir / file.filename
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as handle:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)
    model_id = next((item.model_id for item in model_manager.catalog() if item.filename == file.filename), None)
    return ModelImportResponse(
        model_id=model_id,
        filename=file.filename,
        destination_path=str(destination),
        bytes_written=destination.stat().st_size,
        message="Model imported successfully.",
    )


@app.post("/runtime/install-llama")
async def runtime_install_llama(file: UploadFile = File(...)) -> dict:
    runtime_zip = settings.llama_dir / file.filename
    with runtime_zip.open("wb") as handle:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)

    extract_root = settings.llama_dir / "bundle"
    if extract_root.exists():
        shutil.rmtree(extract_root)
    extract_root.mkdir(parents=True, exist_ok=True)
    shutil.unpack_archive(str(runtime_zip), str(extract_root))
    runtime_zip.unlink(missing_ok=True)

    binary = next((path for path in extract_root.rglob("llama-server.exe")), None)
    if binary is None:
        raise HTTPException(status_code=400, detail="llama-server.exe not found in uploaded archive.")

    target_binary = settings.llama_dir / "llama-server.exe"
    shutil.copy2(binary, target_binary)
    for dll in binary.parent.glob("*.dll"):
        shutil.copy2(dll, settings.llama_dir / dll.name)

    return {"status": "ready", "binary_path": str(target_binary)}


@app.post("/cases", response_model=PatientCase)
async def create_case(payload: PatientCaseCreate) -> PatientCase:
    patient_case = _build_case(payload)
    storage.upsert_case(patient_case)
    return patient_case


@app.post("/triage/run", response_model=TriageAssessment)
async def run_triage(payload: TriageRequest) -> TriageAssessment:
    if payload.case_id:
        existing = storage.get_case(payload.case_id)
        if existing is None:
            raise HTTPException(status_code=404, detail=f"Case not found: {payload.case_id}")
        patient_input = PatientCaseCreate(**existing.model_dump(exclude={"case_id", "created_at", "updated_at"}))
    else:
        patient_input = payload.patient
    triage = evaluate_triage(patient_input)
    evidence = retriever.retrieve(" ".join(patient_input.symptoms + patient_input.risk_factors), max_results=4)
    triage.citations = [hit.citation for hit in evidence]
    return triage


@app.post("/knowledge/import", response_model=KnowledgeImportResponse)
async def import_knowledge(
    files: list[UploadFile] = File(default=[]),
    pack_id: str = Form(default="user-upload"),
) -> KnowledgeImportResponse:
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")
    imported_docs, imported_chunks, skipped_docs = await knowledge.ingest_uploads(files=files, pack_id=pack_id)
    return KnowledgeImportResponse(
        imported_documents=imported_docs,
        imported_chunks=imported_chunks,
        skipped_documents=skipped_docs,
        message="Knowledge import completed.",
    )


def _compose_grounded_prompt(question: str, triage: TriageAssessment, citations: list[str]) -> tuple[str, str]:
    system_prompt = (
        "You are CareBridge Local, an offline community health worker assistant. "
        "Never claim to replace a clinician. Use concise, practical steps. "
        "If emergency signs are present, prioritize referral language."
    )
    evidence_text = "\n".join(citations) if citations else "No retrieval evidence available."
    user_prompt = (
        f"Question: {question}\n"
        f"Triage urgency: {triage.urgency.value}\n"
        f"Red flags: {triage.red_flags}\n"
        f"Missing info: {triage.missing_information}\n"
        f"Evidence snippets:\n{evidence_text}\n"
        "Respond with: 1) clinician summary 2) patient explanation 3) next steps."
    )
    return system_prompt, user_prompt


@app.post("/chat/stream")
async def chat_stream(payload: ChatRequest) -> StreamingResponse:
    patient_case: PatientCase | None = None
    if payload.case_id:
        patient_case = storage.get_case(payload.case_id)
        if patient_case is None:
            raise HTTPException(status_code=404, detail=f"Case not found: {payload.case_id}")
    elif payload.patient:
        patient_case = _build_case(payload.patient)
    else:
        raise HTTPException(status_code=400, detail="Either case_id or patient payload is required.")

    patient_input = PatientCaseCreate(**patient_case.model_dump(exclude={"case_id", "created_at", "updated_at"}))
    triage = evaluate_triage(patient_input, payload.question)
    retrieval_hits = retriever.retrieve(payload.question, max_results=payload.max_citations)
    triage.citations = [hit.citation for hit in retrieval_hits]
    citations_for_prompt = [f"[{hit.citation.source_title}] {hit.citation.snippet}" for hit in retrieval_hits]
    system_prompt, user_prompt = _compose_grounded_prompt(payload.question, triage, citations_for_prompt)
    model_text = runtime_manager.generate(system_prompt=system_prompt, user_prompt=user_prompt)

    async def event_stream() -> AsyncGenerator[str, None]:
        metadata = {
            "type": "metadata",
            "triage": triage.model_dump(mode="json"),
            "citations": [citation.model_dump(mode="json") for citation in triage.citations],
            "runtime": runtime_manager.status_payload(),
        }
        yield f"data: {json.dumps(metadata, ensure_ascii=True)}\n\n"
        for token in model_text.split():
            yield f"data: {json.dumps({'type': 'chunk', 'text': token + ' '}, ensure_ascii=True)}\n\n"
            await asyncio.sleep(0.005)
        yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=True)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/export/referral", response_model=ReferralExportResponse)
async def export_referral(payload: ReferralExportRequest) -> ReferralExportResponse:
    patient_case = storage.get_case(payload.case_id)
    if patient_case is None:
        raise HTTPException(status_code=404, detail=f"Case not found: {payload.case_id}")
    return exporter.export_referral(patient_case=patient_case, triage=payload.triage, extra_notes=payload.extra_notes)


def run() -> None:
    uvicorn.run("carebridge_local_core.app:app", host=settings.host, port=settings.port, reload=False)
