import type {
  HealthResponse,
  ModelCatalogResponse,
  ModelDownloadStatus,
  PatientCase,
  PatientCaseCreate,
  ReferralExportResponse,
  RuntimeStatusResponse,
  TriageAssessment
} from "./types";

const API_BASE = "http://127.0.0.1:8011";

type RuntimeStartResponse = {
  message: string;
};

type KnowledgeImportResult = {
  imported_documents: number;
  imported_chunks: number;
};

async function ensureOk<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with status ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function fetchHealth(): Promise<HealthResponse> {
  return ensureOk(await fetch(`${API_BASE}/health`));
}

export async function fetchRuntimeStatus(): Promise<RuntimeStatusResponse> {
  return ensureOk(await fetch(`${API_BASE}/runtime/status`));
}

export async function fetchModelCatalog(): Promise<ModelCatalogResponse> {
  return ensureOk(await fetch(`${API_BASE}/models/catalog`));
}

export async function startRuntime(preferredProfile = "auto"): Promise<RuntimeStartResponse> {
  return ensureOk<RuntimeStartResponse>(
    await fetch(`${API_BASE}/runtime/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        runtime: "llama_cpp",
        preferred_profile: preferredProfile
      })
    })
  );
}

export async function createCase(payload: PatientCaseCreate): Promise<PatientCase> {
  return ensureOk(
    await fetch(`${API_BASE}/cases`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    })
  );
}

export async function runTriage(caseId: string, patient: PatientCaseCreate): Promise<TriageAssessment> {
  return ensureOk(
    await fetch(`${API_BASE}/triage/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ case_id: caseId, patient })
    })
  );
}

export async function importKnowledge(files: File[], packId = "user-upload") {
  const formData = new FormData();
  formData.append("pack_id", packId);
  files.forEach((file) => formData.append("files", file));
  return ensureOk<KnowledgeImportResult>(await fetch(`${API_BASE}/knowledge/import`, { method: "POST", body: formData }));
}

export async function downloadModel(modelId: string) {
  return ensureOk<{ task_id: string; status: string; message: string }>(
    await fetch(`${API_BASE}/models/download`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model_id: modelId, force_redownload: false })
    })
  );
}

export async function getModelDownloadStatus(taskId: string): Promise<ModelDownloadStatus> {
  return ensureOk(await fetch(`${API_BASE}/models/download/${taskId}`));
}

export async function importModelFile(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  return ensureOk(
    await fetch(`${API_BASE}/models/import`, {
      method: "POST",
      body: formData
    })
  );
}

export async function installLlamaRuntime(archive: File) {
  const formData = new FormData();
  formData.append("file", archive);
  return ensureOk(
    await fetch(`${API_BASE}/runtime/install-llama`, {
      method: "POST",
      body: formData
    })
  );
}

export async function streamChat(
  caseId: string | null,
  question: string,
  onChunk: (text: string) => void,
  onMeta: (payload: { triage: TriageAssessment; citations: unknown[] }) => void,
  patient?: PatientCaseCreate
) {
  const body = caseId ? { case_id: caseId, question } : { patient, question };
  const response = await fetch(`${API_BASE}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  if (!response.ok || !response.body) throw new Error("Failed to stream chat");

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split("\n\n");
    buffer = parts.pop() ?? "";

    for (const part of parts) {
      if (!part.startsWith("data: ")) continue;
      const jsonText = part.replace(/^data:\s*/, "");
      const payload = JSON.parse(jsonText) as { type: string; text?: string; triage?: TriageAssessment; citations?: unknown[] };
      if (payload.type === "metadata" && payload.triage) {
        onMeta({ triage: payload.triage, citations: payload.citations ?? [] });
      }
      if (payload.type === "chunk" && payload.text) {
        onChunk(payload.text);
      }
    }
  }
}

export async function exportReferral(caseId: string, triage: TriageAssessment): Promise<ReferralExportResponse> {
  return ensureOk(
    await fetch(`${API_BASE}/export/referral`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ case_id: caseId, triage, extra_notes: "" })
    })
  );
}
