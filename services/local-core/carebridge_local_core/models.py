from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class UrgencyLevel(str, Enum):
    emergency_referral = "emergency_referral"
    urgent_visit = "urgent_visit"
    home_observation = "home_observation"


class RuntimeKind(str, Enum):
    llama_cpp = "llama_cpp"
    ollama = "ollama"
    mock = "mock"


class ModelProfile(BaseModel):
    runtime: RuntimeKind
    profile_name: str
    model_name: str
    quantization: str
    estimated_memory_gb: float
    status: str = "not_started"


class EvidenceCitation(BaseModel):
    citation_id: str
    source_title: str
    source_path: str
    knowledge_pack_id: str
    score: float
    snippet: str


class AttachmentRef(BaseModel):
    filename: str
    content_type: str | None = None
    local_path: str | None = None


class PatientCaseCreate(BaseModel):
    patient_label: str
    age_years: int | None = None
    is_pregnant: bool = False
    gestational_weeks: int | None = None
    symptoms: list[str] = Field(default_factory=list)
    risk_factors: list[str] = Field(default_factory=list)
    vitals: dict[str, float | int | str] = Field(default_factory=dict)
    notes: str = ""
    attachments: list[AttachmentRef] = Field(default_factory=list)


class PatientCase(PatientCaseCreate):
    case_id: str
    created_at: datetime
    updated_at: datetime


class TriageRequest(BaseModel):
    case_id: str | None = None
    patient: PatientCaseCreate


class TriageAssessment(BaseModel):
    urgency: UrgencyLevel
    red_flags: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    recommended_next_steps: list[str] = Field(default_factory=list)
    contraindications: list[str] = Field(default_factory=list)
    summary_for_clinician: str
    summary_for_patient: str
    safety_alerts: list[str] = Field(default_factory=list)
    citations: list[EvidenceCitation] = Field(default_factory=list)


class RuntimeStartRequest(BaseModel):
    runtime: RuntimeKind = RuntimeKind.llama_cpp
    preferred_profile: str = "balanced"
    model_path: str | None = None
    endpoint_override: str | None = None


class RuntimeStartResponse(BaseModel):
    active_profile: ModelProfile
    available_profiles: list[ModelProfile]
    message: str


class KnowledgePackManifest(BaseModel):
    id: str
    name: str
    version: str
    language: str
    region: str
    license: str
    updated_at: datetime
    description: str = ""


class HealthResponse(BaseModel):
    service: str
    timestamp: datetime
    runtime_status: str
    active_profile: ModelProfile | None = None
    case_count: int
    knowledge_chunk_count: int
    installed_packs: list[str]
    notes: list[str] = Field(default_factory=list)


class KnowledgeImportResponse(BaseModel):
    imported_documents: int
    imported_chunks: int
    skipped_documents: int
    message: str


class ChatRequest(BaseModel):
    case_id: str | None = None
    question: str
    patient: PatientCaseCreate | None = None
    max_citations: int = 4


class ReferralExportRequest(BaseModel):
    case_id: str
    triage: TriageAssessment
    extra_notes: str = ""


class ReferralExportResponse(BaseModel):
    export_id: str
    case_id: str
    html_path: str
    json_path: str
    created_at: datetime


class RuntimeState(BaseModel):
    active_profile: ModelProfile | None = None
    status: str = "not_started"
    detail: str = ""
    endpoint: str | None = None
    process_id: int | None = None
    meta: dict[str, Any] = Field(default_factory=dict)
