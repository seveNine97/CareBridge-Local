export type Urgency = "emergency_referral" | "urgent_visit" | "home_observation";

export interface AttachmentRef {
  filename: string;
  content_type?: string;
  local_path?: string;
}

export interface PatientCaseCreate {
  patient_label: string;
  age_years?: number;
  is_pregnant: boolean;
  gestational_weeks?: number;
  symptoms: string[];
  risk_factors: string[];
  vitals: Record<string, string | number>;
  notes: string;
  attachments: AttachmentRef[];
}

export interface PatientCase extends PatientCaseCreate {
  case_id: string;
  created_at: string;
  updated_at: string;
}

export interface EvidenceCitation {
  citation_id: string;
  source_title: string;
  source_path: string;
  knowledge_pack_id: string;
  score: number;
  snippet: string;
}

export interface TriageAssessment {
  urgency: Urgency;
  red_flags: string[];
  missing_information: string[];
  recommended_next_steps: string[];
  contraindications: string[];
  summary_for_clinician: string;
  summary_for_patient: string;
  safety_alerts: string[];
  citations: EvidenceCitation[];
}

export interface HealthResponse {
  service: string;
  timestamp: string;
  runtime_status: string;
  case_count: number;
  knowledge_chunk_count: number;
  installed_packs: string[];
  notes: string[];
}

export interface ReferralExportResponse {
  export_id: string;
  case_id: string;
  html_path: string;
  json_path: string;
  created_at: string;
}
