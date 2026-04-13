import type {
  HealthResponse,
  PatientCase,
  PatientCaseCreate,
  ReferralExportResponse,
  TriageAssessment
} from "./types";

const API_BASE = "http://127.0.0.1:8011";

export async function fetchHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE}/health`);
  if (!response.ok) throw new Error("Failed to fetch health");
  return response.json();
}

export async function startRuntime() {
  const response = await fetch(`${API_BASE}/runtime/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      runtime: "llama_cpp",
      preferred_profile: "balanced"
    })
  });
  if (!response.ok) throw new Error("Failed to start runtime");
  return response.json();
}

export async function createCase(payload: PatientCaseCreate): Promise<PatientCase> {
  const response = await fetch(`${API_BASE}/cases`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!response.ok) throw new Error("Failed to create case");
  return response.json();
}

export async function runTriage(caseId: string, patient: PatientCaseCreate): Promise<TriageAssessment> {
  const response = await fetch(`${API_BASE}/triage/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ case_id: caseId, patient })
  });
  if (!response.ok) throw new Error("Failed to run triage");
  return response.json();
}

export async function importKnowledge(files: File[], packId = "user-upload") {
  const formData = new FormData();
  formData.append("pack_id", packId);
  files.forEach((file) => formData.append("files", file));
  const response = await fetch(`${API_BASE}/knowledge/import`, { method: "POST", body: formData });
  if (!response.ok) throw new Error("Failed to import knowledge");
  return response.json();
}

export async function streamChat(
  caseId: string,
  question: string,
  onChunk: (text: string) => void,
  onMeta: (payload: { triage: TriageAssessment; citations: unknown[] }) => void
) {
  const response = await fetch(`${API_BASE}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ case_id: caseId, question })
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
  const response = await fetch(`${API_BASE}/export/referral`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ case_id: caseId, triage, extra_notes: "" })
  });
  if (!response.ok) throw new Error("Failed to export referral");
  return response.json();
}
