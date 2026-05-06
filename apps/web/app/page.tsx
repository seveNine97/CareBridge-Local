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

const links = {
  installer: "https://github.com/seveNine97/CareBridge-Local/raw/master/release/CareBridgeLocal-Setup-1.0.0.exe",
  repo: "https://github.com/seveNine97/CareBridge-Local",
  guide: "https://github.com/seveNine97/CareBridge-Local/blob/master/docs/USER_GUIDE.md",
  writeup: "https://github.com/seveNine97/CareBridge-Local/blob/master/submission/kaggle-writeup-copy.md"
};

export default function HomePage() {
  return (
    <main className="page">
      <section className="hero">
        <div className="hero-copy">
          <p className="kicker">Gemma 4 Good Hackathon Submission</p>
          <h1>CareBridge Local</h1>
          <p className="subtitle">
            An installable offline Gemma copilot for community health workers: intake, red-flag triage, grounded chat, and referral export on one local device.
          </p>
          <div className="hero-actions">
            <a className="btn primary" href={links.installer}>
              Download installer
            </a>
            <a className="btn ghost" href="#demo">
              Review demo flow
            </a>
          </div>
        </div>
        <img className="hero-image" src="/carebridge-product-preview.png" alt="CareBridge Local desktop app preview" />
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
        <h2>Judge-Ready Demo Flow</h2>
        <ol>
          {scenarios.map((scenario) => (
            <li key={scenario}>{scenario}</li>
          ))}
        </ol>
        <p>
          The desktop app covers case intake, rule-first triage, grounded Gemma chat with citations, and a printable referral export without cloud services.
        </p>
      </section>

      <section id="downloads" className="panel">
        <h2>Install, Review, Submit</h2>
        <div className="download-grid">
          <div>
            <h3>One-Click Reviewer Kit</h3>
            <p>Windows installer plus a start-here guide for non-technical reviewers. No developer dependency setup.</p>
            <a className="btn primary" href={links.installer}>
              Download installer
            </a>
          </div>
          <div>
            <h3>Usage Guide</h3>
            <p>Demo scenarios, first-run model setup, offline workflow, and troubleshooting steps.</p>
            <a className="btn secondary" href={links.guide}>
              Read guide
            </a>
          </div>
          <div>
            <h3>Paste-Ready Writeup</h3>
            <p>Kaggle submission text designed to copy directly into the competition form.</p>
            <a className="btn secondary" href={links.writeup}>
              Open writeup
            </a>
          </div>
        </div>
      </section>

      <section className="panel compact">
        <h2>Why It Can Win</h2>
        <p>
          CareBridge Local combines social impact, working local Gemma inference, deterministic medical safety rails, cited retrieval, and a deployment path judges
          can actually try.
        </p>
        <a className="text-link" href={links.repo}>
          View source repository
        </a>
      </section>
    </main>
  );
}
