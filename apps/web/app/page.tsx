import { BookOpen, CheckCircle2, Database, Folder, Settings, ShieldCheck, Stethoscope, WifiOff } from "lucide-react";

const links = {
  installer: "https://github.com/seveNine97/CareBridge-Local/raw/master/release/CareBridgeLocal-Setup-1.0.0.exe",
  repo: "https://github.com/seveNine97/CareBridge-Local",
  guide: "https://github.com/seveNine97/CareBridge-Local/blob/master/docs/USER_GUIDE.md"
};

const libraries = ["pediatric_care_base.rag", "medication_safety_base.rag"];

export default function HomePage() {
  return (
    <main>
      <section className="hero">
        <nav className="nav">
          <strong>CareBridge Pro</strong>
          <div>
            <a href={links.guide}>User guide</a>
            <a href={links.repo}>GitHub</a>
          </div>
        </nav>

        <div className="hero-copy">
          <p className="eyebrow">Secure local clinical support</p>
          <h1>CareBridge Pro keeps frontline triage private, offline, and clinically readable.</h1>
          <p>
            A Windows desktop medical AI assistant for local patient triage, evidence citations, and referral preparation without exposing runtime setup on the
            clinical workspace.
          </p>
          <div className="actions">
            <a className="button primary" href={links.installer}>
              Download Windows installer
            </a>
            <a className="button secondary" href={links.repo}>
              View source
            </a>
          </div>
        </div>
      </section>

      <section className="product-shell">
        <aside className="rail">
          <ShieldCheck className="brand-mark" />
          <div className="rail-item active">
            <Stethoscope />
            <span>New Case</span>
          </div>
          <div className="rail-item">
            <BookOpen />
            <span>Knowledge Base</span>
          </div>
          <div className="rail-item">
            <Folder />
            <span>Patient Records</span>
          </div>
          <div className="rail-item">
            <Settings />
            <span>Settings</span>
          </div>
        </aside>

        <div className="workspace-preview">
          <header className="workspace-top">
            <h2>
              CareBridge Pro <span>| Secure Local Assistant - 100% Private</span>
            </h2>
            <a className="save-button" href={links.installer}>
              Save Patient Case
            </a>
            <span className="offline-badge">
              <WifiOff size={18} />
              Offline
            </span>
          </header>

          <div className="preview-grid">
            <section className="clinical-main">
              <div className="input-card">
                <div className="patient-line">
                  <strong>Patient ID:</strong> A001
                </div>
                <div className="structure-row">
                  <strong>Structure:</strong>
                  <span>Symptom</span>
                  <span>Risk Factor</span>
                  <span>Medication</span>
                </div>
                <div className="symptom-box">
                  <strong>Symptom:</strong> A child has a persistent fever and vomiting. No other severe signs reported.
                  <em>[Add Symptom] [Add Risk Factor]</em>
                </div>
                <div className="input-action">
                  <div>fever</div>
                  <button>Analyze & Triage</button>
                </div>
              </div>

              <div className="response-row">
                <article className="response-card recommendation">
                  <div>
                    <ShieldCheck />
                    <h3>Immediate Medical Recommendation</h3>
                  </div>
                  <p>Start supportive care and monitor the child's condition closely.</p>
                </article>

                <article className="response-card triage">
                  <span className="triage-badge">Low Triage (Non-Urgent)</span>
                  <p>This case presents a low risk of immediate severe illness.</p>
                  <strong>Observe for red flags.</strong>
                  <div className="red-flags">
                    <b>Observe for Red Flags</b>
                    <span>High fever</span>
                    <span>Shallow breath</span>
                    <span>Energy change</span>
                  </div>
                </article>

                <article className="response-card citations">
                  <h3>Knowledge Base Citation Card</h3>
                  <div className="citation-box">
                    <b>Reference & Citation</b>
                    <ol>
                      <li>[PDF] pediatric_fever.pdf - "Fever in children under 5..."</li>
                      <li>[PDF] medication_safety.pdf - "Fever management guidelines"</li>
                    </ol>
                    <button>Show all</button>
                  </div>
                </article>
              </div>
            </section>

            <aside className="context-panel">
              <h3>System Status & Knowledge</h3>
              <div className="context-card status-card">
                <CheckCircle2 />
                <div>
                  <strong>Ready</strong>
                  <span>OFFLINE Gemma-2b-it Model</span>
                </div>
                <dl>
                  <dt>RAM Usage:</dt>
                  <dd>3.1 GB / 8 GB</dd>
                  <dt>Inference:</dt>
                  <dd>14 t/s</dd>
                  <dt>Memory Profile:</dt>
                  <dd>Standard</dd>
                </dl>
              </div>
              <div className="context-card">
                <h4>Loaded Knowledge Libraries</h4>
                <p>Active local knowledge bases</p>
                {libraries.map((library) => (
                  <span key={library}>{library}</span>
                ))}
                <button>Manage Libraries</button>
              </div>
              <div className="context-card">
                <h4>Local Data Summary Panel</h4>
                <p>Records Stored: <strong>145 cases</strong></p>
                <p>Exported Referrals: <strong>12</strong></p>
              </div>
            </aside>
          </div>
        </div>
      </section>

      <section className="screenshot-section">
        <div>
          <p className="eyebrow">Desktop preview</p>
          <h2>Designed around clinical clarity, not technical setup.</h2>
        </div>
        <img src="/carebridge-product-preview.png" alt="CareBridge Pro desktop interface preview" />
      </section>
    </main>
  );
}
