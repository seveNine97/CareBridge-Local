const links = {
  installer: "https://github.com/seveNine97/CareBridge-Local/raw/master/release/CareBridgeLocal-Setup-1.0.0.exe",
  repo: "https://github.com/seveNine97/CareBridge-Local",
  guide: "https://github.com/seveNine97/CareBridge-Local/blob/master/docs/USER_GUIDE.md",
  writeup: "https://github.com/seveNine97/CareBridge-Local/blob/master/submission/kaggle-writeup-copy.md"
};

const strengths = [
  ["Offline inference", "Gemma GGUF profiles run locally through llama.cpp with no cloud dependency."],
  ["Safety first", "Deterministic triage catches emergency red flags before model generation."],
  ["Grounded answers", "Local knowledge packs and uploaded documents provide citation-backed responses."],
  ["Installable product", "Windows installer bundles the desktop shell, hidden sidecar, and runtime setup flow."]
];

const flow = ["Ask a question", "Start local runtime", "Review safety triage", "Export referral"];

export default function HomePage() {
  return (
    <main>
      <section className="hero">
        <nav className="nav">
          <strong>CareBridge Local</strong>
          <a href={links.repo}>GitHub</a>
        </nav>
        <div className="hero-grid">
          <div className="hero-copy">
            <p className="eyebrow">Gemma 4 Good Hackathon</p>
            <h1>Offline clinical Q&A for frontline care.</h1>
            <p>
              A polished Windows desktop assistant for community health workers: ask first, then use local Gemma inference, safety triage, citations, and referral
              export when needed.
            </p>
            <div className="actions">
              <a className="button primary" href={links.installer}>
                Download installer
              </a>
              <a className="button secondary" href={links.writeup}>
                Read writeup
              </a>
            </div>
          </div>
          <div className="product-frame">
            <img src="/carebridge-product-preview.png" alt="CareBridge Local desktop interface preview" />
          </div>
        </div>
      </section>

      <section className="section">
        <div className="section-heading">
          <p className="eyebrow">Why it matters</p>
          <h2>Built as a field-ready product, not a localhost demo.</h2>
        </div>
        <div className="cards">
          {strengths.map(([title, body]) => (
            <article className="card" key={title}>
              <h3>{title}</h3>
              <p>{body}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="section flow-section">
        <div className="section-heading">
          <p className="eyebrow">Reviewer path</p>
          <h2>One install, four clear steps.</h2>
        </div>
        <div className="flow">
          {flow.map((step, index) => (
            <div className="flow-item" key={step}>
              <span>{index + 1}</span>
              <strong>{step}</strong>
            </div>
          ))}
        </div>
      </section>

      <section className="section download-panel">
        <div>
          <p className="eyebrow">Submission assets</p>
          <h2>Everything judges need is one click away.</h2>
        </div>
        <div className="download-actions">
          <a className="button primary" href={links.installer}>
            Windows installer
          </a>
          <a className="button secondary" href={links.guide}>
            User guide
          </a>
          <a className="button secondary" href={links.repo}>
            Source code
          </a>
        </div>
      </section>
    </main>
  );
}
