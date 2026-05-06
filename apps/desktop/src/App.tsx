import { useEffect, useMemo, useState } from "react";
import {
  createCase,
  downloadModel,
  exportReferral,
  fetchHealth,
  fetchModelCatalog,
  fetchRuntimeStatus,
  getModelDownloadStatus,
  importKnowledge,
  importModelFile,
  installLlamaRuntime,
  runTriage,
  startRuntime,
  streamChat
} from "./api";
import type {
  HealthResponse,
  ModelCatalogResponse,
  ModelDownloadStatus,
  PatientCase,
  PatientCaseCreate,
  RuntimeStatusResponse,
  TriageAssessment
} from "./types";

const initialPatient: PatientCaseCreate = {
  patient_label: "",
  age_years: undefined,
  is_pregnant: false,
  gestational_weeks: undefined,
  symptoms: [],
  risk_factors: [],
  vitals: {},
  notes: "",
  attachments: []
};

function formatBytes(bytes?: number): string {
  if (!bytes || bytes <= 0) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  let value = bytes;
  let index = 0;
  while (value >= 1024 && index < units.length - 1) {
    value /= 1024;
    index += 1;
  }
  return `${value.toFixed(index === 0 ? 0 : 1)} ${units[index]}`;
}

export default function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [runtimeStatus, setRuntimeStatus] = useState<RuntimeStatusResponse | null>(null);
  const [catalog, setCatalog] = useState<ModelCatalogResponse | null>(null);
  const [downloadStatus, setDownloadStatus] = useState<ModelDownloadStatus | null>(null);
  const [modelProfile, setModelProfile] = useState("auto");
  const [patient, setPatient] = useState<PatientCaseCreate>(initialPatient);
  const [caseRecord, setCaseRecord] = useState<PatientCase | null>(null);
  const [triage, setTriage] = useState<TriageAssessment | null>(null);
  const [question, setQuestion] = useState("");
  const [chatText, setChatText] = useState("");
  const [status, setStatus] = useState("Initializing...");
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [modelFile, setModelFile] = useState<File | null>(null);
  const [runtimeArchive, setRuntimeArchive] = useState<File | null>(null);

  async function refreshSetupState() {
    const [latestHealth, latestRuntime, latestCatalog] = await Promise.all([fetchHealth(), fetchRuntimeStatus(), fetchModelCatalog()]);
    setHealth(latestHealth);
    setRuntimeStatus(latestRuntime);
    setCatalog(latestCatalog);
  }

  useEffect(() => {
    refreshSetupState()
      .then(() => setStatus("Ready"))
      .catch(() => setStatus("Cannot reach local-core API at 127.0.0.1:8011"));
  }, []);

  useEffect(() => {
    if (!downloadStatus || downloadStatus.status === "completed" || downloadStatus.status === "failed") {
      return undefined;
    }
    const timer = setInterval(async () => {
      const latest = await getModelDownloadStatus(downloadStatus.task_id);
      setDownloadStatus(latest);
      if (latest.status === "completed" || latest.status === "failed") {
        await refreshSetupState();
      }
    }, 1000);
    return () => clearInterval(timer);
  }, [downloadStatus]);

  const urgencyClass = useMemo(() => {
    if (!triage) return "chip chip-neutral";
    if (triage.urgency === "emergency_referral") return "chip chip-danger";
    if (triage.urgency === "urgent_visit") return "chip chip-warning";
    return "chip chip-safe";
  }, [triage]);

  const installedModels = (catalog?.models ?? []).filter((item) => item.installed);
  const balancedModel = (catalog?.models ?? []).find((item) => item.profile_name === "balanced");
  const setupReady = Boolean(catalog?.runtime_binary_present && installedModels.length > 0);

  async function handleStartRuntime() {
    setStatus("Starting runtime...");
    try {
      const response = await startRuntime(modelProfile);
      setStatus(response.message ?? "Runtime started.");
      await refreshSetupState();
    } catch (error) {
      setStatus(`Runtime start failed: ${(error as Error).message}`);
    }
  }

  async function handleInstallRuntimeArchive() {
    if (!runtimeArchive) {
      setStatus("Select a llama.cpp zip first.");
      return;
    }
    setStatus("Installing llama.cpp runtime...");
    try {
      await installLlamaRuntime(runtimeArchive);
      await refreshSetupState();
      setStatus("llama.cpp runtime installed.");
    } catch (error) {
      setStatus(`Runtime install failed: ${(error as Error).message}`);
    }
  }

  async function handleDownloadModel(modelId: string) {
    setStatus("Starting model download...");
    try {
      const response = await downloadModel(modelId);
      const task = await getModelDownloadStatus(response.task_id);
      setDownloadStatus(task);
      setStatus("Model download task running.");
    } catch (error) {
      setStatus(`Model download failed: ${(error as Error).message}`);
    }
  }

  async function handleImportModel() {
    if (!modelFile) {
      setStatus("Select a .gguf file first.");
      return;
    }
    setStatus("Importing local model...");
    try {
      await importModelFile(modelFile);
      await refreshSetupState();
      setStatus("Model imported successfully.");
    } catch (error) {
      setStatus(`Model import failed: ${(error as Error).message}`);
    }
  }

  async function handleCreateCase() {
    if (!patient.patient_label.trim()) {
      setStatus("Patient label is required.");
      return;
    }
    try {
      const created = await createCase(patient);
      setCaseRecord(created);
      setStatus(`Case created: ${created.case_id}`);
    } catch (error) {
      setStatus(`Create case failed: ${(error as Error).message}`);
    }
  }

  async function handleRunTriage() {
    if (!caseRecord) {
      setStatus("Create a case first.");
      return;
    }
    try {
      const output = await runTriage(caseRecord.case_id, patient);
      setTriage(output);
      setStatus("Triage completed.");
    } catch (error) {
      setStatus(`Triage failed: ${(error as Error).message}`);
    }
  }

  async function handleImportKnowledge() {
    if (!selectedFiles.length) {
      setStatus("Select files before import.");
      return;
    }
    try {
      const response = await importKnowledge(selectedFiles);
      setStatus(`Imported ${response.imported_documents} docs / ${response.imported_chunks} chunks.`);
      await refreshSetupState();
    } catch (error) {
      setStatus(`Knowledge import failed: ${(error as Error).message}`);
    }
  }

  async function handleAsk() {
    if (!caseRecord) {
      setStatus("Create a case first.");
      return;
    }
    if (!question.trim()) {
      setStatus("Enter a question.");
      return;
    }
    setChatText("");
    setStatus("Streaming response...");
    await streamChat(
      caseRecord.case_id,
      question,
      (chunk) => setChatText((prev) => prev + chunk),
      ({ triage: streamTriage }) => setTriage(streamTriage)
    );
    setStatus("Response complete.");
  }

  async function handleExport() {
    if (!caseRecord || !triage) {
      setStatus("Run triage before exporting.");
      return;
    }
    try {
      const result = await exportReferral(caseRecord.case_id, triage);
      setStatus(`Export generated: ${result.html_path}`);
    } catch (error) {
      setStatus(`Export failed: ${(error as Error).message}`);
    }
  }

  return (
    <main className="layout">
      <section className="hero">
        <h1>CareBridge Local</h1>
        <p>Offline community health worker copilot with in-app runtime setup and local Gemma model management.</p>
      </section>

      <section className="panel">
        <h2>Runtime Setup Wizard</h2>
        <p className="muted">
          Runtime binary: {catalog?.runtime_binary_present ? "installed" : "missing"} | Models installed: {installedModels.length}
        </p>
        <div className="wizard-row">
          <label className="file-picker">
            Install llama.cpp (zip)
            <input type="file" accept=".zip" onChange={(event) => setRuntimeArchive(event.target.files?.[0] ?? null)} />
          </label>
          <button onClick={handleInstallRuntimeArchive}>Install Runtime</button>
        </div>
        <div className="wizard-row">
          <button onClick={() => handleDownloadModel("gemma4-e4b-q4km")}>
            Download E4B ({balancedModel ? formatBytes(balancedModel.file_size_bytes) : "unknown"})
          </button>
          <button onClick={() => handleDownloadModel("gemma4-e2b-q4km")}>Download E2B</button>
        </div>
        <div className="wizard-row">
          <label className="file-picker">
            Import local GGUF
            <input type="file" accept=".gguf" onChange={(event) => setModelFile(event.target.files?.[0] ?? null)} />
          </label>
          <button onClick={handleImportModel}>Import Model</button>
        </div>
        {downloadStatus ? (
          <div className="download-card">
            <p>
              Download status: {downloadStatus.status} {Math.round(downloadStatus.progress * 100)}%
            </p>
            <p className="muted">
              {formatBytes(downloadStatus.downloaded_bytes)} / {formatBytes(downloadStatus.total_bytes)} | Speed:{" "}
              {formatBytes(downloadStatus.speed_bps)} /s
            </p>
            {downloadStatus.error ? <p className="error-text">{downloadStatus.error}</p> : null}
          </div>
        ) : null}
        <div className="wizard-row">
          <label>
            Runtime profile
            <select value={modelProfile} onChange={(event) => setModelProfile(event.target.value)}>
              <option value="auto">Auto</option>
              <option value="balanced">Balanced (E4B)</option>
              <option value="compatibility">Compatibility (E2B)</option>
            </select>
          </label>
          <button disabled={!setupReady} onClick={handleStartRuntime}>
            Start Runtime
          </button>
        </div>
        <p className="muted">
          Runtime status: {runtimeStatus?.status ?? "unknown"} {runtimeStatus?.detail ? `| ${runtimeStatus.detail}` : ""}
        </p>
      </section>

      <section className="grid">
        <article className="panel">
          <h2>Intake Wizard</h2>
          <label>
            Patient label
            <input
              value={patient.patient_label}
              onChange={(event) => setPatient({ ...patient, patient_label: event.target.value })}
              placeholder="e.g. Child with fever"
            />
          </label>
          <label>
            Symptoms (comma separated)
            <input
              value={patient.symptoms.join(", ")}
              onChange={(event) =>
                setPatient({
                  ...patient,
                  symptoms: event.target.value
                    .split(",")
                    .map((item) => item.trim())
                    .filter(Boolean)
                })
              }
              placeholder="fever, shortness of breath"
            />
          </label>
          <label>
            Risk factors (comma separated)
            <input
              value={patient.risk_factors.join(", ")}
              onChange={(event) =>
                setPatient({
                  ...patient,
                  risk_factors: event.target.value
                    .split(",")
                    .map((item) => item.trim())
                    .filter(Boolean)
                })
              }
              placeholder="pregnancy, infant"
            />
          </label>
          <label>
            Notes
            <textarea
              value={patient.notes}
              onChange={(event) => setPatient({ ...patient, notes: event.target.value })}
              rows={4}
              placeholder="Observations from field worker"
            />
          </label>
          <div className="button-row">
            <button onClick={handleCreateCase}>Create Case</button>
            <button onClick={handleRunTriage}>Run Triage</button>
          </div>
          <p className="muted">{caseRecord ? `Case ID: ${caseRecord.case_id}` : "No case created yet."}</p>
        </article>

        <article className="panel">
          <h2>Triage Output</h2>
          <p className={urgencyClass}>{triage ? triage.urgency : "pending"}</p>
          <h3>Red Flags</h3>
          <ul>
            {(triage?.red_flags ?? ["No red flags yet"]).map((flag) => (
              <li key={flag}>{flag}</li>
            ))}
          </ul>
          <h3>Missing Information</h3>
          <ul>
            {(triage?.missing_information ?? ["No gaps flagged"]).map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
          <h3>Citations</h3>
          <ul>
            {(triage?.citations ?? []).map((citation) => (
              <li key={citation.citation_id}>
                {citation.source_title} ({citation.score})
              </li>
            ))}
          </ul>
          <button onClick={handleExport}>Export Referral Pack</button>
        </article>
      </section>

      <section className="grid">
        <article className="panel">
          <h2>Knowledge Import</h2>
          <input
            type="file"
            multiple
            onChange={(event) => setSelectedFiles(Array.from(event.target.files ?? []))}
            accept=".txt,.md,.pdf,.png,.jpg,.jpeg,.webp"
          />
          <button onClick={handleImportKnowledge}>Import Files</button>
          <p className="muted">{selectedFiles.length ? `${selectedFiles.length} files selected` : "No files selected"}</p>
        </article>

        <article className="panel">
          <h2>Grounded Chat</h2>
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            rows={3}
            placeholder="What should I do next for this patient?"
          />
          <button onClick={handleAsk}>Ask CareBridge</button>
          <pre className="chat-box">{chatText || "Streamed answer appears here."}</pre>
        </article>
      </section>

      <footer className="status">
        {status}
        {health ? ` | Chunks: ${health.knowledge_chunk_count} | Cases: ${health.case_count}` : ""}
      </footer>
    </main>
  );
}
