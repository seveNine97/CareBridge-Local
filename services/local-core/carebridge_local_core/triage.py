from __future__ import annotations

from typing import Iterable

from carebridge_local_core.models import PatientCaseCreate, TriageAssessment, UrgencyLevel


RED_FLAG_KEYWORDS = {
    "chest pain": "Possible cardiac emergency",
    "shortness of breath": "Potential respiratory compromise",
    "difficulty breathing": "Potential respiratory compromise",
    "unconscious": "Altered mental status requires immediate transfer",
    "confusion": "Acute neurologic warning sign",
    "seizure": "Potential neurologic emergency",
    "severe bleeding": "Hemorrhage risk requires urgent referral",
    "vaginal bleeding": "Pregnancy-related or severe bleeding warning",
    "blue lips": "Likely oxygen compromise",
}

HIGH_RISK_PHRASES = {"dose", "diagnose", "antibiotic", "prescription", "mg"}


def _normalize_items(items: Iterable[str]) -> str:
    return " ".join(item.strip().lower() for item in items if item and item.strip())


def evaluate_triage(patient: PatientCaseCreate, user_question: str | None = None) -> TriageAssessment:
    searchable_text = " ".join(
        [
            _normalize_items(patient.symptoms),
            _normalize_items(patient.risk_factors),
            patient.notes.strip().lower(),
            (user_question or "").strip().lower(),
        ]
    )

    red_flags: list[str] = []
    safety_alerts: list[str] = []
    missing_information: list[str] = []
    next_steps: list[str] = []
    contraindications: list[str] = []

    for phrase, explanation in RED_FLAG_KEYWORDS.items():
        if phrase in searchable_text:
            red_flags.append(f"{phrase}: {explanation}")

    if patient.is_pregnant and ("bleeding" in searchable_text or "severe pain" in searchable_text):
        red_flags.append("pregnancy danger sign: urgent obstetric assessment recommended")

    if "temperature_c" not in patient.vitals:
        missing_information.append("Body temperature is missing.")
    if "respiratory_rate" not in patient.vitals:
        missing_information.append("Respiratory rate is missing.")
    if "oxygen_saturation" not in patient.vitals and (
        "shortness of breath" in searchable_text or "difficulty breathing" in searchable_text
    ):
        missing_information.append("Oxygen saturation is missing for respiratory complaint.")

    if any(flag in searchable_text for flag in HIGH_RISK_PHRASES):
        contraindications.append("Avoid giving exact dose or diagnosis without verified guideline evidence.")

    if red_flags:
        urgency = UrgencyLevel.emergency_referral
        next_steps.extend(
            [
                "Initiate emergency referral now.",
                "Keep monitoring airway, breathing, and circulation while arranging transport.",
                "Send a concise referral summary with red flags and observed vitals.",
            ]
        )
        safety_alerts.append("Emergency red flag detected. Do not delay referral.")
    elif len(missing_information) >= 2:
        urgency = UrgencyLevel.urgent_visit
        next_steps.extend(
            [
                "Collect missing vitals immediately.",
                "Arrange urgent in-person assessment within the same day.",
            ]
        )
    else:
        urgency = UrgencyLevel.home_observation
        next_steps.extend(
            [
                "Provide home observation guidance with clear return precautions.",
                "Schedule follow-up check within 24-48 hours.",
            ]
        )

    clinician_summary = (
        f"Urgency={urgency.value}. Red flags: {len(red_flags)}. "
        f"Missing key data: {len(missing_information)}. "
        "Prioritize guideline-backed actions and referral documentation."
    )
    patient_summary = (
        "Based on current information, this assistant recommends your next safest step. "
        "If breathing worsens, chest pain appears, or consciousness changes, seek emergency care immediately."
    )

    return TriageAssessment(
        urgency=urgency,
        red_flags=red_flags,
        missing_information=missing_information,
        recommended_next_steps=next_steps,
        contraindications=contraindications,
        summary_for_clinician=clinician_summary,
        summary_for_patient=patient_summary,
        safety_alerts=safety_alerts,
        citations=[],
    )
