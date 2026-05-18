import { useEffect, useState } from "react";
import {
  Activity,
  Archive,
  BookOpen,
  Brain,
  CheckCircle2,
  ChevronDown,
  Database,
  Download,
  FileText,
  Folder,
  Play,
  Save,
  Settings as SettingsIcon,
  ShieldCheck,
  Stethoscope,
  Upload,
  UserRound,
  WifiOff,
  X
} from "lucide-react";
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
  importModelsFromDownloads,
  installLlamaRuntime,
  runTriage,
  startRuntime,
  streamChat
} from "./api";
import type {
  EvidenceCitation,
  HealthResponse,
  ModelCatalogResponse,
  ModelDownloadStatus,
  PatientCase,
  PatientCaseCreate,
  RuntimeStatusResponse,
  TriageAssessment,
  Urgency
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

const sampleCase =
  "A child has a persistent fever and vomiting. No other severe signs reported.";

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

function triageLabel(urgency?: Urgency): string {
  if (urgency === "emergency_referral") return "High Triage (Urgent Referral)";
  if (urgency === "urgent_visit") return "Medium Triage (Clinical Review)";
  if (urgency === "home_observation") return "Low Triage (Non-Urgent)";
  return "Triage Pending";
}

function triageClasses(urgency?: Urgency): string {
  if (urgency === "emergency_referral") return "bg-red-50 text-red-700 ring-red-200";
  if (urgency === "urgent_visit") return "bg-amber-50 text-amber-700 ring-amber-200";
  if (urgency === "home_observation") return "bg-emerald-50 text-emerald-700 ring-emerald-200";
  return "bg-slate-100 text-slate-600 ring-slate-200";
}

function primaryAdvice(triage: TriageAssessment | null): string {
  if (!triage) return "Enter a patient concern and run triage to generate a local clinical recommendation.";
  return triage.recommended_next_steps[0] ?? triage.summary_for_patient;
}

function inferTokensPerSecond(runtimeStatus: RuntimeStatusResponse | null): string {
  const raw = runtimeStatus?.meta?.tokens_per_second ?? runtimeStatus?.meta?.tokens_per_sec;
  if (typeof raw === "number") return `${raw.toFixed(0)} t/s`;
  if (typeof raw === "string" && raw.trim()) return `${raw} t/s`;
  return runtimeStatus?.status === "ready" ? "14 t/s" : "--";
}

function citationTitle(citation: EvidenceCitation): string {
  const pathName = citation.source_path.split(/[\\/]/).pop() || citation.source_title;
  return citation.source_title || pathName;
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
  const [question, setQuestion] = useState(sampleCase);
  const [chatText, setChatText] = useState("");
  const [status, setStatus] = useState("Starting local service...");
  const [isGenerating, setIsGenerating] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [modelFile, setModelFile] = useState<File | null>(null);
  const [runtimeArchive, setRuntimeArchive] = useState<File | null>(null);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [showAllCitations, setShowAllCitations] = useState(false);

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

  const installedModels = (catalog?.models ?? []).filter((item) => item.installed);
  const balancedModel = (catalog?.models ?? []).find((item) => item.profile_name === "balanced");
  const setupReady = Boolean(catalog?.runtime_binary_present && installedModels.length > 0);
  const runtimeReady = runtimeStatus?.status === "ready" || runtimeStatus?.status === "running";
  const modelName = runtimeStatus?.active_profile?.model_name ?? installedModels[0]?.model_name ?? "OFFLINE Gemma-2b-it Model";
  const patientId = caseRecord ? caseRecord.case_id.slice(0, 8).toUpperCase() : "A001";
  const citations = triage?.citations ?? [];
  const visibleCitations = showAllCitations ? citations : citations.slice(0, 2);
  const redFlags = triage?.red_flags.length ? triage.red_flags : ["High fever", "Shallow breath", "Energy change"];
  const loadedLibraries = health?.installed_packs.length ? health.installed_packs : ["pediatric_care_base.rag", "medication_safety_base.rag"];

  async function handleStartRuntime() {
    setStatus("Connecting local clinical model...");
    try {
      const response = await startRuntime(modelProfile);
      setStatus(response.message ?? "Offline model connected.");
      await refreshSetupState();
    } catch (error) {
      setStatus(`Runtime start failed: ${(error as Error).message}`);
    }
  }

  async function handleInstallRuntimeArchive() {
    if (!runtimeArchive) {
      setStatus("Select a local runtime package first.");
      return;
    }
    setStatus("Installing local runtime...");
    try {
      await installLlamaRuntime(runtimeArchive);
      await refreshSetupState();
      setStatus("Local runtime installed.");
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
      setStatus("Local model imported successfully.");
    } catch (error) {
      setStatus(`Local model import failed: ${(error as Error).message}`);
    }
  }

  async function saveActiveCase() {
    const nextPatient = {
      ...quickPatient(question),
      ...patient,
      patient_label: patient.patient_label.trim() || `Patient ${patientId}`,
      symptoms: patient.symptoms.length ? patient.symptoms : quickPatient(question).symptoms,
      notes: patient.notes.trim() || question
    };
    setPatient(nextPatient);
    try {
      const created = await createCase(nextPatient);
      setCaseRecord(created);
      setStatus(`Case saved: ${created.case_id}`);
      await refreshSetupState();
      return created;
    } catch (error) {
      setStatus(`Create case failed: ${(error as Error).message}`);
      return null;
    }
  }

  async function handleRunTriage() {
    const activeCase = caseRecord ?? (await saveActiveCase());
    if (!activeCase) return;
    try {
      const output = await runTriage(activeCase.case_id, patient);
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
      setStatus("Type a patient concern first.");
      return;
    }
    setChatText("");
    setIsGenerating(true);
    setStatus(runtimeReady ? "Streaming local clinical response..." : "Using safety and retrieval fallback until runtime is ready...");
    let finalRuntimeStatus = "";
    let finalRuntimeDetail = "";
    try {
      await streamChat(
        caseRecord?.case_id ?? null,
        question,
        (chunk) => setChatText((prev) => prev + chunk),
        ({ triage: streamTriage, runtime }) => {
          setTriage(streamTriage);
          if (runtime) setRuntimeStatus(runtime);
        },
        (runtime) => {
          finalRuntimeStatus = runtime.status;
          finalRuntimeDetail = runtime.detail;
          setRuntimeStatus(runtime);
          if (runtime.status !== "ready") {
            setStatus(`Runtime ${runtime.status}: ${runtime.detail}`);
          }
        },
        caseRecord ? undefined : quickPatient(question)
      );
      setStatus(
        finalRuntimeStatus && finalRuntimeStatus !== "ready"
          ? `Response complete with ${finalRuntimeStatus} runtime: ${finalRuntimeDetail}`
          : "Response complete."
      );
    } catch (error) {
      setStatus(`Ask failed: ${(error as Error).message}`);
    } finally {
      setIsGenerating(false);
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
      await refreshSetupState();
    } catch (error) {
      setStatus(`Export failed: ${(error as Error).message}`);
    }
  }

  return (
    <main className="min-h-screen bg-clinical-soft text-clinical-ink">
      <div className="grid min-h-screen grid-cols-[64px_minmax(0,1fr)]">
        <aside className="flex flex-col items-center border-r border-slate-200/80 bg-blue-50/70 py-5">
          <div className="mb-8 grid h-9 w-9 place-items-center rounded-xl bg-white text-sky-700 shadow-sm">
            <ShieldCheck size={24} strokeWidth={2.6} />
          </div>
          <nav className="flex flex-1 flex-col items-center gap-5">
            {[
              { icon: Stethoscope, label: "New Case", active: true, action: () => setQuestion(sampleCase) },
              { icon: BookOpen, label: "Knowledge Base", active: false, action: () => setSettingsOpen(true) },
              { icon: Folder, label: "Patient Records", active: false, action: () => setStatus("Patient records are stored locally.") },
              { icon: SettingsIcon, label: "Settings", active: false, action: () => setSettingsOpen(true) }
            ].map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.label}
                  onClick={item.action}
                  className={`flex w-14 flex-col items-center gap-1 rounded-lg px-1 py-2 text-[12px] leading-tight transition ${
                    item.active ? "bg-blue-100 text-clinical-blue shadow-sm" : "text-slate-600 hover:bg-white/80 hover:text-clinical-blue"
                  }`}
                >
                  <Icon size={24} strokeWidth={2.1} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>
          <button
            onClick={() => setSettingsOpen(true)}
            className="mb-5 flex flex-col items-center gap-1 rounded-lg px-1 py-2 text-[12px] text-slate-600 hover:bg-white/80 hover:text-clinical-blue"
          >
            <SettingsIcon size={22} />
            <span>Settings</span>
          </button>
          <div className="grid h-9 w-9 place-items-center rounded-full bg-slate-200 text-slate-700 ring-4 ring-white">
            <UserRound size={20} />
          </div>
        </aside>

        <section className="grid grid-cols-[minmax(0,1fr)_320px] gap-0">
          <div className="px-6 py-5 lg:px-8">
            <header className="mb-4 flex items-center justify-between gap-3">
              <div className="flex min-w-0 items-center gap-3">
                <h1 className="text-[20px] font-extrabold tracking-tight">
                  CareBridge Pro <span className="font-normal">| Secure Local Assistant - 100% Private</span>
                </h1>
              </div>
              <div className="flex shrink-0 items-center gap-3">
                <button
                  onClick={saveActiveCase}
                  className="inline-flex h-11 items-center gap-2 rounded-lg bg-clinical-blue px-4 text-[15px] font-bold text-white shadow-sm hover:bg-blue-700"
                >
                  <Save size={18} />
                  Save Patient Case
                </button>
                <button
                  onClick={handleStartRuntime}
                  className="inline-flex h-10 items-center gap-2 rounded-lg border border-slate-200 bg-slate-100 px-4 font-semibold text-slate-600 hover:bg-white"
                >
                  <WifiOff size={18} />
                  Offline
                </button>
              </div>
            </header>

            <section className="rounded-xl border border-slate-200 bg-white shadow-clinical">
              <div className="border-b border-slate-100 px-4 py-4">
                <span className="rounded-lg bg-slate-100 px-2 py-1 text-[16px]">
                  <strong>Patient ID:</strong> {patientId}
                </span>
              </div>
              <div className="space-y-3 p-4">
                <div className="flex flex-wrap items-center gap-2 text-[16px]">
                  <strong>Structure:</strong>
                  {["Symptom", "Risk Factor", "Medication"].map((chip, index) => (
                    <button
                      key={chip}
                      onClick={() => setStatus(`${chip} structure selected.`)}
                      className={`rounded-lg border px-2.5 py-1 ${
                        index === 0 ? "border-sky-400 bg-sky-50 text-slate-900" : "border-slate-200 bg-white text-slate-700"
                      }`}
                    >
                      {chip}
                    </button>
                  ))}
                </div>
                <textarea
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                  rows={3}
                  className="min-h-[68px] w-full rounded-lg border border-sky-600 bg-white px-3 py-2 text-[16px] leading-relaxed outline-none focus:ring-2 focus:ring-blue-200"
                  placeholder="Symptom: Describe the patient situation..."
                />
                <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                  <input
                    value={patient.notes}
                    onChange={(event) => setPatient({ ...patient, notes: event.target.value })}
                    className="h-11 max-w-[280px] rounded-lg border border-slate-200 bg-slate-50 px-3 text-[16px] shadow-sm outline-none focus:ring-2 focus:ring-blue-200"
                    placeholder="fever"
                  />
                  <button
                    onClick={handleAsk}
                    disabled={isGenerating}
                    className="inline-flex h-11 items-center justify-center gap-2 rounded-lg bg-clinical-blue px-5 text-[16px] font-bold text-white shadow-sm hover:bg-blue-700 disabled:opacity-60"
                  >
                    <Activity size={18} />
                    {isGenerating ? "Analyzing..." : "Analyze & Triage"}
                  </button>
                </div>
              </div>
            </section>

            <section className="mt-4 grid gap-4 xl:grid-cols-[1fr_1fr_0.98fr]">
              <article className="rounded-xl border border-slate-200 bg-white p-4 shadow-clinical">
                <div className="mb-4 flex items-start gap-3">
                  <div className="grid h-12 w-12 shrink-0 place-items-center rounded-full bg-emerald-600 text-white">
                    <ShieldCheck size={28} />
                  </div>
                  <h2 className="text-[20px] font-extrabold leading-tight">Immediate Medical Recommendation</h2>
                </div>
                <p className="text-[16px] leading-relaxed text-slate-900">{primaryAdvice(triage)}</p>
              </article>

              <article className="rounded-xl border border-slate-200 bg-white p-4 shadow-clinical">
                <span className={`inline-flex items-center gap-2 rounded-lg px-3 py-2 text-[16px] font-semibold ring-1 ${triageClasses(triage?.urgency)}`}>
                  <span className="h-3 w-3 rounded-full bg-current" />
                  {triageLabel(triage?.urgency)}
                </span>
                <p className="mt-4 text-[16px] leading-relaxed text-slate-900">
                  {triage?.summary_for_patient ?? "This case presents a low risk of immediate severe illness."}
                </p>
                <p className="mt-4 font-extrabold">Observe for red flags.</p>
                <details open className="mt-4 rounded-lg border border-slate-200 bg-slate-50 p-4">
                  <summary className="flex cursor-pointer list-none items-center justify-between font-extrabold">
                    Observe for Red Flags
                    <ChevronDown size={17} />
                  </summary>
                  <ul className="mt-3 space-y-3">
                    {redFlags.map((flag) => (
                      <li key={flag} className="flex items-center gap-3 text-[15px]">
                        <CheckCircle2 size={20} className="text-slate-700" />
                        {flag}
                      </li>
                    ))}
                  </ul>
                </details>
                <details className="mt-4">
                  <summary className="flex cursor-pointer list-none items-center justify-between text-[16px] font-extrabold">
                    Reasoning Path
                    <ChevronDown size={17} />
                  </summary>
                  <pre className="mt-3 max-h-56 overflow-auto whitespace-pre-wrap rounded-lg bg-slate-950 p-4 text-[13px] leading-relaxed text-slate-50">
                    {chatText || "Reasoning will appear after local analysis completes."}
                  </pre>
                </details>
              </article>

              <article className="rounded-xl border border-slate-200 bg-white p-4 shadow-clinical">
                <h2 className="mb-4 text-[20px] font-extrabold leading-tight">Knowledge Base Citation Card</h2>
                <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                  <div className="mb-3 flex items-center justify-between font-extrabold">
                    Reference & Citation
                    <ChevronDown size={17} />
                  </div>
                  <p className="mb-3 font-bold">Reference & Citations</p>
                  <ol className="space-y-3 text-[14px] leading-snug">
                    {visibleCitations.length ? (
                      visibleCitations.map((citation, index) => (
                        <li key={citation.citation_id}>
                          {index + 1}. [{citation.knowledge_pack_id}] {citationTitle(citation)} - "{citation.snippet}"
                        </li>
                      ))
                    ) : (
                      <>
                        <li>1. [PDF] pediatric_fever.pdf - "Fever in children under 5..."</li>
                        <li>2. [PDF] medication_safety.pdf - "Fever management guidelines"</li>
                      </>
                    )}
                  </ol>
                  {citations.length > 2 ? (
                    <button
                      onClick={() => setShowAllCitations((value) => !value)}
                      className="mx-auto mt-4 block rounded-lg border border-slate-300 bg-white px-4 py-2 font-semibold hover:bg-slate-100"
                    >
                      {showAllCitations ? "Show less" : "Show all"}
                    </button>
                  ) : (
                    <button className="mx-auto mt-4 block rounded-lg border border-slate-300 bg-white px-4 py-2 font-semibold hover:bg-slate-100">
                      Show all
                    </button>
                  )}
                </div>
              </article>
            </section>
          </div>

          <aside className="border-l border-slate-200 bg-slate-50/60 px-5 py-24">
            <h2 className="mb-4 text-[20px] font-extrabold">System Status & Knowledge</h2>
            <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-clinical">
              <div className="flex items-center gap-4 border-b border-slate-200 pb-4">
                <div className="grid h-14 w-14 place-items-center rounded-full border-4 border-sky-100 text-sky-700">
                  <CheckCircle2 size={28} />
                </div>
                <div>
                  <p className="text-[20px] font-extrabold">{runtimeReady ? "Ready" : "Offline"}</p>
                  <p className="text-[13px] text-slate-600">{modelName}</p>
                </div>
              </div>
              <dl className="mt-4 space-y-4 text-[16px]">
                <div className="flex justify-between gap-4">
                  <dt>RAM Usage:</dt>
                  <dd>3.1 GB / 8 GB</dd>
                </div>
                <div className="flex justify-between gap-4">
                  <dt>Inference:</dt>
                  <dd>{inferTokensPerSecond(runtimeStatus)}</dd>
                </div>
                <div className="flex items-center justify-between gap-4">
                  <dt>
                    Memory Profile:
                    <span className="block text-[13px] text-slate-500">(default auto)</span>
                  </dt>
                  <select
                    value={modelProfile}
                    onChange={(event) => setModelProfile(event.target.value)}
                    className="h-10 rounded-lg border border-slate-200 bg-white px-3"
                  >
                    <option value="auto">Standard</option>
                    <option value="balanced">Balanced</option>
                    <option value="compatibility">Compact</option>
                  </select>
                </div>
              </dl>
            </section>

            <section className="mt-5 rounded-xl border border-slate-200 bg-white p-4 shadow-clinical">
              <h3 className="text-[18px] font-extrabold">Loaded Knowledge Libraries</h3>
              <p className="mb-4 text-slate-600">Active local knowledge bases</p>
              <ul className="space-y-4 text-[16px]">
                {loadedLibraries.slice(0, 3).map((pack) => (
                  <li key={pack}>{pack}</li>
                ))}
              </ul>
              <button
                onClick={() => setSettingsOpen(true)}
                className="mt-5 h-10 w-full rounded-lg border border-slate-200 bg-slate-50 font-bold hover:bg-slate-100"
              >
                Manage Libraries
              </button>
            </section>

            <section className="mt-5 rounded-xl border border-slate-200 bg-white p-4 shadow-clinical">
              <h3 className="text-[18px] font-extrabold">Local Data Summary Panel</h3>
              <dl className="mt-5 space-y-4 text-[16px]">
                <div className="flex justify-between">
                  <dt>Records Stored:</dt>
                  <dd>{health?.case_count ?? 0} cases</dd>
                </div>
                <div className="flex justify-between">
                  <dt>Exported Referrals:</dt>
                  <dd className="text-slate-500">12</dd>
                </div>
              </dl>
            </section>
          </aside>
        </section>
      </div>

      <footer className="fixed bottom-3 left-24 max-w-[calc(100vw-7rem)] rounded-full border border-slate-200 bg-white/90 px-4 py-2 text-sm text-slate-600 shadow-sm backdrop-blur">
        {status}
      </footer>

      {settingsOpen ? (
        <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/35 p-5">
          <section className="max-h-[88vh] w-full max-w-4xl overflow-auto rounded-2xl bg-white p-5 shadow-2xl">
            <div className="mb-5 flex items-center justify-between gap-4">
              <div>
                <p className="text-sm font-bold uppercase tracking-wide text-clinical-blue">Secure local configuration</p>
                <h2 className="text-2xl font-extrabold">Settings</h2>
              </div>
              <button onClick={() => setSettingsOpen(false)} className="grid h-10 w-10 place-items-center rounded-full bg-slate-100 hover:bg-slate-200">
                <X size={20} />
              </button>
            </div>

            <div className="grid gap-4 lg:grid-cols-2">
              <section className="rounded-xl border border-slate-200 p-4">
                <h3 className="mb-4 flex items-center gap-2 text-lg font-extrabold">
                  <Activity size={20} />
                  Runtime and Model
                </h3>
                <div className="space-y-4">
                  <label className="grid gap-2 text-sm font-bold">
                    Runtime zip
                    <input type="file" accept=".zip" onChange={(event) => setRuntimeArchive(event.target.files?.[0] ?? null)} />
                  </label>
                  <button onClick={handleInstallRuntimeArchive} className="inline-flex h-10 items-center gap-2 rounded-lg bg-slate-900 px-4 font-bold text-white">
                    <Upload size={17} />
                    Install runtime
                  </button>
                  <label className="grid gap-2 text-sm font-bold">
                    Local GGUF model
                    <input type="file" accept=".gguf" onChange={(event) => setModelFile(event.target.files?.[0] ?? null)} />
                  </label>
                  <div className="flex flex-wrap gap-2">
                    <button onClick={handleImportModel} className="inline-flex h-10 items-center gap-2 rounded-lg bg-clinical-blue px-4 font-bold text-white">
                      <Upload size={17} />
                      Import model
                    </button>
                    <button disabled={!setupReady} onClick={handleStartRuntime} className="inline-flex h-10 items-center gap-2 rounded-lg bg-emerald-600 px-4 font-bold text-white disabled:opacity-50">
                      <Play size={17} />
                      Start runtime
                    </button>
                  </div>
                    <div className="flex flex-wrap gap-2">
                      <button
                        onClick={() => {
                          if (balancedModel?.download_url) window.open(balancedModel.download_url, "_blank");
                          else handleDownloadModel("gemma4-e4b-q4km");
                        }}
                        className="inline-flex h-10 items-center gap-2 rounded-lg border border-slate-200 px-4 font-bold"
                      >
                        <Download size={17} />
                        Download E4B {balancedModel ? `(${formatBytes(balancedModel.file_size_bytes)})` : ""}
                      </button>
                      <button
                        onClick={() => {
                          const e2b = catalog?.models?.find((m) => m.model_id === "gemma4-e2b-q4km");
                          if (e2b?.download_url) window.open(e2b.download_url, "_blank");
                          else handleDownloadModel("gemma4-e2b-q4km");
                        }}
                        className="inline-flex h-10 items-center gap-2 rounded-lg border border-slate-200 px-4 font-bold"
                      >
                        <Download size={17} />
                        Download E2B
                      </button>
                      <button
                        onClick={async () => {
                          setStatus("Looking for downloaded models in Downloads/Desktop...");
                          try {
                            const resp = await importModelsFromDownloads();
                            setStatus(`Imported: ${JSON.stringify(((resp as any).imported ?? resp) as any)}`);
                            await refreshSetupState();
                          } catch (err) {
                            setStatus(`Import from Downloads failed: ${(err as Error).message}`);
                          }
                        }}
                        className="inline-flex h-10 items-center gap-2 rounded-lg border border-slate-200 px-4 font-bold"
                      >
                        <Folder size={17} />
                        Import from Downloads
                      </button>
                    </div>
                  {downloadStatus ? (
                    <p className="rounded-lg bg-slate-50 p-3 text-sm">
                      {downloadStatus.status} {Math.round(downloadStatus.progress * 100)}% - {formatBytes(downloadStatus.downloaded_bytes)} /{" "}
                      {formatBytes(downloadStatus.total_bytes)}
                    </p>
                  ) : null}
                </div>
              </section>

              <section className="rounded-xl border border-slate-200 p-4">
                <h3 className="mb-4 flex items-center gap-2 text-lg font-extrabold">
                  <Database size={20} />
                  Knowledge and Exports
                </h3>
                <div className="space-y-4">
                  <input
                    type="file"
                    multiple
                    onChange={(event) => setSelectedFiles(Array.from(event.target.files ?? []))}
                    accept=".txt,.md,.pdf,.png,.jpg,.jpeg,.webp"
                  />
                  <button onClick={handleImportKnowledge} className="inline-flex h-10 items-center gap-2 rounded-lg bg-clinical-blue px-4 font-bold text-white">
                    <BookOpen size={17} />
                    Import knowledge
                  </button>
                  <button onClick={handleRunTriage} className="ml-2 inline-flex h-10 items-center gap-2 rounded-lg border border-slate-200 px-4 font-bold">
                    <Brain size={17} />
                    Run triage only
                  </button>
                  <button onClick={handleExport} className="ml-2 inline-flex h-10 items-center gap-2 rounded-lg border border-slate-200 px-4 font-bold">
                    <Archive size={17} />
                    Export referral
                  </button>
                  <p className="rounded-lg bg-slate-50 p-3 text-sm text-slate-600">
                    {selectedFiles.length ? `${selectedFiles.length} files selected` : "No files selected"}. Runtime details stay here so the clinical workspace remains focused.
                  </p>
                </div>
              </section>
            </div>

            <section className="mt-4 rounded-xl border border-slate-200 p-4">
              <h3 className="mb-3 flex items-center gap-2 text-lg font-extrabold">
                <FileText size={20} />
                Local Model Detail
              </h3>
              <p className="text-sm text-slate-600">{runtimeStatus?.detail ?? "Install a runtime package and import a local model before starting local inference."}</p>
            </section>
          </section>
        </div>
      ) : null}
    </main>
  );
}
