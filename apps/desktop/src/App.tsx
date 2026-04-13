import { useEffect, useMemo, useState } from "react";
import {
  createCase,
  exportReferral,
  fetchHealth,
  importKnowledge,
  runTriage,
  startRuntime,
  streamChat
} from "./api";
import type { HealthResponse, PatientCase, PatientCaseCreate, TriageAssessment } from "./types";

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

export default function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [patient, setPatient] = useState<PatientCaseCreate>(initialPatient);
  const [caseRecord, setCaseRecord] = useState<PatientCase | null>(null);
  const [triage, setTriage] = useState<TriageAssessment | null>(null);
  const [question, setQuestion] = useState("");
  const [chatText, setChatText] = useState("");
  const [status, setStatus] = useState("Initializing...");
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);

  useEffect(() => {
    fetchHealth()
      .then(setHealth)
      .catch(() => setStatus("Cannot reach local-core API at 127.0.0.1:8011"));
  }, []);

  const urgencyClass = useMemo(() => {
    if (!triage) return "chip chip-neutral";
    if (triage.urgency === "emergency_referral") return "chip chip-danger";
    if (triage.urgency === "urgent_visit") return "chip chip-warning";
    return "chip chip-safe";
  }, [triage]);

  async function handleStartRuntime() {
    setStatus("Starting runtime...");
    try {
      const response = await startRuntime();
      setStatus(response.message ?? "Runtime started.");
      const latest = await fetchHealth();
      setHealth(latest);
    } catch (error) {
      setStatus(`Runtime start failed: ${(error as Error).message}`);
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
      const latest = await fetchHealth();
      setHealth(latest);
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
        <p>Offline community health worker copilot for triage, grounded chat, and referral export.</p>
        <div className="hero-row">
          <button onClick={handleStartRuntime}>Start Runtime</button>
          <span className="muted">
            {health ? `Chunks: ${health.knowledge_chunk_count} | Cases: ${health.case_count}` : "No health data yet"}
          </span>
        </div>
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
                  symptoms: event.target.value.split(",").map((item) => item.trim()).filter(Boolean)
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
                  risk_factors: event.target.value.split(",").map((item) => item.trim()).filter(Boolean)
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

      <footer className="status">{status}</footer>
    </main>
  );
}
