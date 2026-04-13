from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import uuid4

from carebridge_local_core.config import settings
from carebridge_local_core.models import PatientCase, ReferralExportResponse, TriageAssessment
from carebridge_local_core.storage import Storage


class ReferralExporter:
    def __init__(self, storage: Storage) -> None:
        self.storage = storage
        settings.exports_dir.mkdir(parents=True, exist_ok=True)

    def export_referral(self, patient_case: PatientCase, triage: TriageAssessment, extra_notes: str = "") -> ReferralExportResponse:
        timestamp = datetime.now(timezone.utc)
        slug = f"{patient_case.case_id}-{timestamp.strftime('%Y%m%d%H%M%S')}"
        html_path = settings.exports_dir / f"{slug}.html"
        json_path = settings.exports_dir / f"{slug}.json"
        export_id = str(uuid4())

        payload = {
            "case": patient_case.model_dump(mode="json"),
            "triage": triage.model_dump(mode="json"),
            "extra_notes": extra_notes,
            "exported_at": timestamp.isoformat(),
        }
        json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")

        html = f"""
<html>
  <head>
    <meta charset="utf-8" />
    <title>CareBridge Referral - {patient_case.case_id}</title>
    <style>
      body {{ font-family: "Segoe UI", Arial, sans-serif; margin: 24px; color: #111; }}
      h1 {{ color: #0f4c81; }}
      .chip {{ display:inline-block; padding:4px 8px; margin:2px; border-radius:999px; background:#e6f2ff; }}
      .warn {{ color: #8b0000; font-weight: 700; }}
      pre {{ background:#f6f6f6; padding: 12px; border-radius: 8px; white-space: pre-wrap; }}
    </style>
  </head>
  <body>
    <h1>CareBridge Local Referral Summary</h1>
    <p><strong>Case ID:</strong> {patient_case.case_id}</p>
    <p><strong>Patient:</strong> {patient_case.patient_label} | <strong>Age:</strong> {patient_case.age_years or "N/A"}</p>
    <p><strong>Urgency:</strong> <span class="warn">{triage.urgency.value}</span></p>
    <h2>Red Flags</h2>
    <p>{', '.join(triage.red_flags) if triage.red_flags else 'None detected'}</p>
    <h2>Recommended Next Steps</h2>
    <pre>{chr(10).join('- ' + step for step in triage.recommended_next_steps)}</pre>
    <h2>Clinician Summary</h2>
    <pre>{triage.summary_for_clinician}</pre>
    <h2>Patient Explanation</h2>
    <pre>{triage.summary_for_patient}</pre>
    <h2>Extra Notes</h2>
    <pre>{extra_notes or 'No extra notes provided.'}</pre>
    <p>Generated at {timestamp.isoformat()}</p>
  </body>
</html>
        """.strip()
        html_path.write_text(html, encoding="utf-8")

        self.storage.insert_export(
            export_id=export_id,
            case_id=patient_case.case_id,
            export_type="referral",
            payload={"html_path": str(html_path), "json_path": str(json_path)},
        )
        return ReferralExportResponse(
            export_id=export_id,
            case_id=patient_case.case_id,
            html_path=str(html_path.resolve()),
            json_path=str(json_path.resolve()),
            created_at=timestamp,
        )
