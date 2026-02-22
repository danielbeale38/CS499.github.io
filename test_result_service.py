from services.result_service import sanitize_record

def test_sanitize_record_adds_required_fields():
    r = {"breed": "X"}
    out = sanitize_record(r)
    assert "sex_upon_outcome" in out
    assert "age_upon_outcome_in_weeks" in out

def test_sanitize_record_coerces_age_or_sets_none():
    out1 = sanitize_record({"age_upon_outcome_in_weeks": "12"})
    assert out1["age_upon_outcome_in_weeks"] == 12.0

    out2 = sanitize_record({"age_upon_outcome_in_weeks": "bad"})
    assert out2["age_upon_outcome_in_weeks"] is None
