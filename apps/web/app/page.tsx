const tracks = [
  {
    title: "Health & Sciences Impact",
    body: "Built for community health workers in low-connectivity settings: triage, referral, and patient education workflows that function fully offline."
  },
  {
    title: "Technical Depth",
    body: "Real local stack: desktop shell, FastAPI sidecar, SQLite persistence, hybrid retrieval with citations, runtime abstraction for llama.cpp and Ollama."
  },
  {
    title: "Safety & Trust",
    body: "Rule-first emergency guardrails for chest pain, breathing distress, pregnancy danger signs, severe dehydration, and altered consciousness."
  }
];

const scenarios = [
  "Pediatric fever with dehydration signs and referral thresholds",
  "Pregnancy danger signs screening and immediate escalation guidance",
  "Medication label ambiguity with safe-response fallback and follow-up checklist"
];

export default function HomePage() {
  return (
    <main className="page">
      <section className="hero">
        <p className="kicker">Gemma 4 Good Hackathon Submission</p>
        <h1>CareBridge Local</h1>
        <p className="subtitle">
          Offline-first community health worker copilot designed for clinics and outreach teams operating in weak or no-network environments.
        </p>
        <div className="hero-actions">
          <a className="btn primary" href="#downloads">
            Download Desktop Build
          </a>
          <a className="btn ghost" href="#demo">
            Watch Demo Flow
          </a>
        </div>
      </section>

      <section className="cards">
        {tracks.map((track) => (
          <article key={track.title} className="card">
            <h2>{track.title}</h2>
            <p>{track.body}</p>
          </article>
        ))}
      </section>

      <section id="demo" className="panel">
        <h2>1-Minute Demo Storyboard</h2>
        <ol>
          {scenarios.map((scenario) => (
            <li key={scenario}>{scenario}</li>
          ))}
        </ol>
        <p>
          The desktop app covers intake, triage, grounded chat, and referral export with visible citations. Public site remains lightweight and focused on
          storytelling plus reviewer onboarding.
        </p>
      </section>

      <section id="downloads" className="panel">
        <h2>Downloads</h2>
        <div className="download-grid">
          <div>
            <h3>Lite Installer</h3>
            <p>Desktop shell + local core runtime. Prompts user to fetch model package on first launch.</p>
            <a className="btn primary" href="#">
              Coming Soon
            </a>
          </div>
          <div>
            <h3>Field Bundle</h3>
            <p>Desktop shell + model + seed knowledge pack for USB or LAN transfer in fully offline deployments.</p>
            <a className="btn ghost" href="#">
              Bundle Guide
            </a>
          </div>
        </div>
      </section>
    </main>
  );
}
