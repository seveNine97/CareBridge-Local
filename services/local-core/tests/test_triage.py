from carebridge_local_core.models import PatientCaseCreate, UrgencyLevel
from carebridge_local_core.triage import evaluate_triage


def test_emergency_flag_for_chest_pain() -> None:
    patient = PatientCaseCreate(
        patient_label="test",
        symptoms=["chest pain", "shortness of breath"],
        vitals={"temperature_c": 37.8, "respiratory_rate": 30},
    )
    result = evaluate_triage(patient)
    assert result.urgency == UrgencyLevel.emergency_referral
    assert result.red_flags


def test_missing_data_triggers_urgent() -> None:
    patient = PatientCaseCreate(patient_label="test", symptoms=["fever"])
    result = evaluate_triage(patient)
    assert result.urgency == UrgencyLevel.urgent_visit
    assert len(result.missing_information) >= 2
