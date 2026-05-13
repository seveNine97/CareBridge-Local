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

const sampleQuestions = [
  "A child has fever, vomiting, and is very sleepy. What should I do next?",
  "A 28-week pregnant patient reports bleeding and severe headache. How urgent is this?",
  "The medicine label is unclear and the patient feels dizzy. What safe questions should I ask?"
];

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

function quickPatient(question: string): PatientCaseCreate {
  return {
    ...initialPatient,
    patient_label: "Quick chat",
    symptoms: question
      .split(/[,.!?;，。！？；]/)
      .map((item) => item.trim())
      .filter(Boolean)
      .slice(0, 4),
    notes: question
  };
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
  const [status, setStatus] = useState("Starting local service...");
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
      .catch(() => setStatus("Starting local service. Reopen the app if this takes more than a few seconds."));
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
    if (!triage) return "chip neutral";
    if (triage.urgency === "emergency_referral") return "chip danger";
    if (triage.urgency === "urgent_visit") return "chip warning";
    return "chip safe";
  }, [triage]);

  const installedModels = (catalog?.models ?? []).filter((item) => item.installed);
  const balancedModel = (catalog?.models ?? []).find((item) => item.profile_name === "balanced");
  const setupReady = Boolean(catalog?.runtime_binary_present && installedModels.length > 0);
  const runtimeReady = runtimeStatus?.status === "ready" || runtimeStatus?.status === "running";
  const runtimeLabel = runtimeReady ? "Runtime ready" : setupReady ? "Ready to start" : "Setup required";

  async function handleStartRuntime() {
    setStatus("Starting local Gemma runtime. E4B may take a few minutes on first load...");
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
      setStatus(`Case saved: ${created.case_id}`);
    } catch (error) {
      setStatus(`Create case failed: ${(error as Error).message}`);
    }
  }

  async function handleRunTriage() {
    if (!caseRecord) {
      setStatus("Save a case first.");
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
    if (!question.trim()) {
      setStatus("Type a question first.");
      return;
    }
    setChatText("");
    setStatus(runtimeReady ? "Streaming local Gemma response..." : "Using safety and retrieval fallback until runtime is ready...");
    try {
      await streamChat(
        caseRecord?.case_id ?? null,
        question,
        (chunk) => setChatText((prev) => prev + chunk),
        ({ triage: streamTriage }) => setTriage(streamTriage),
        caseRecord ? undefined : quickPatient(question)
      );
      setStatus("Response complete.");
    } catch (error) {
      setStatus(`Ask failed: ${(error as Error).message}`);
    }
  }

  async function handleExport() {
    if (!caseRecord || !triage) {
      setStatus("Save a case and run triage before exporting.");
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
    <main className="shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">CareBridge Local</p>
          <h1>Offline clinical Q&A</h1>
        </div>
        <div className={runtimeReady ? "status-pill ready" : "status-pill"}>{runtimeLabel}</div>
      </header>

      <section className="workspace">
        <div className="assistant-panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Ask first</p>
              <h2>CareBridge Assistant</h2>
            </div>
            <span className={urgencyClass}>{triage ? triage.urgency : "triage pending"}</span>
          </div>
          <textarea
            className="question-input"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            rows={5}
            placeholder="Describe the situation in plain language..."
          />
          <div className="sample-grid">
            {sampleQuestions.map((sample) => (
              <button className="ghost-button" key={sample} onClick={() => setQuestion(sample)}>
                {sample}
              </button>
            ))}
          </div>
          <button className="primary-action" onClick={handleAsk}>
            Ask offline assistant
          </button>
          <pre className="answer-box">{chatText || "The answer will appear here. When the local runtime is not ready, CareBridge still returns safety triage and local citation guidance."}</pre>
        </div>

        <aside className="side-panel">
          <div className="metric-card">
            <span>Knowledge chunks</span>
            <strong>{health?.knowledge_chunk_count ?? 0}</strong>
          </div>
          <div className="metric-card">
            <span>Saved cases</span>
            <strong>{health?.case_count ?? 0}</strong>
          </div>
          <div className="summary-card">
            <span>Patient summary</span>
            <p>{triage?.summary_for_patient ?? "No active answer yet."}</p>
          </div>
        </aside>
      </section>

      <section className="setup-card">
        <div className="section-title">
          <div>
            <p className="eyebrow">Local model</p>
            <h2>Runtime setup</h2>
          </div>
          <p>{runtimeStatus?.status ?? "unknown"}</p>
        </div>
        <div className="setup-grid">
          <label>
            Runtime zip
            <input type="file" accept=".zip" onChange={(event) => setRuntimeArchive(event.target.files?.[0] ?? null)} />
          </label>
          <button onClick={handleInstallRuntimeArchive}>Install runtime</button>
          <label>
            Local GGUF model
            <input type="file" accept=".gguf" onChange={(event) => setModelFile(event.target.files?.[0] ?? null)} />
          </label>
          <button onClick={handleImportModel}>Import model</button>
          <label>
            Runtime profile
            <select value={modelProfile} onChange={(event) => setModelProfile(event.target.value)}>
              <option value="auto">Auto</option>
              <option value="balanced">Balanced E4B</option>
              <option value="compatibility">Compatibility E2B</option>
            </select>
          </label>
          <button disabled={!setupReady} onClick={handleStartRuntime}>
            Start runtime
          </button>
        </div>
        <div className="download-row">
          <button className="secondary-button" onClick={() => handleDownloadModel("gemma4-e4b-q4km")}>
            Download E4B {balancedModel ? `(${formatBytes(balancedModel.file_size_bytes)})` : ""}
          </button>
          <button className="secondary-button" onClick={() => handleDownloadModel("gemma4-e2b-q4km")}>
            Download E2B
          </button>
        </div>
        {downloadStatus ? (
          <div className="progress-card">
            <strong>
              {downloadStatus.status} {Math.round(downloadStatus.progress * 100)}%
            </strong>
            <span>
              {formatBytes(downloadStatus.downloaded_bytes)} / {formatBytes(downloadStatus.total_bytes)}
            </span>
            {downloadStatus.error ? <p className="error-text">{downloadStatus.error}</p> : null}
          </div>
        ) : null}
        <p className="detail-line">
          {runtimeStatus?.detail ?? "Install runtime and import a GGUF model before starting local inference."}
        </p>
      </section>

      <section className="tool-grid">
        <details className="tool-card">
          <summary>Clinical case tools</summary>
          <label>
            Patient label
            <input value={patient.patient_label} onChange={(event) => setPatient({ ...patient, patient_label: event.target.value })} placeholder="Child with fever" />
          </label>
          <label>
            Symptoms
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
              placeholder="fever, vomiting"
            />
          </label>
          <label>
            Risk factors
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
            <textarea value={patient.notes} onChange={(event) => setPatient({ ...patient, notes: event.target.value })} rows={4} />
          </label>
          <div className="button-row">
            <button onClick={handleCreateCase}>Save case</button>
            <button onClick={handleRunTriage}>Run triage</button>
            <button onClick={handleExport}>Export referral</button>
          </div>
        </details>

        <details className="tool-card">
          <summary>Knowledge import</summary>
          <input
            type="file"
            multiple
            onChange={(event) => setSelectedFiles(Array.from(event.target.files ?? []))}
            accept=".txt,.md,.pdf,.png,.jpg,.jpeg,.webp"
          />
          <button onClick={handleImportKnowledge}>Import files</button>
          <p className="muted">{selectedFiles.length ? `${selectedFiles.length} files selected` : "No files selected"}</p>
          <ul className="citation-list">
            {(triage?.citations ?? []).map((citation) => (
              <li key={citation.citation_id}>
                {citation.source_title} <span>{citation.score}</span>
              </li>
            ))}
          </ul>
        </details>
      </section>

      <footer className="footer-status">{status}</footer>
    </main>
  );
}
