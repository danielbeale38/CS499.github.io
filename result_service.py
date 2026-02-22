from typing import Any

REQUIRED_FIELDS = [
    "breed",
    "sex_upon_outcome",
    "age_upon_outcome_in_weeks",
]

OPTIONAL_FIELDS_WITH_DEFAULTS = {
    "name": "",
    "location_lat": None,
    "location_long": None,
}

def sanitize_record(r: dict) -> dict:
    out = dict(r)
    out.pop("_id", None)

    # Ensure required keys exist (even if None) so downstream logic is stable.
    for k in REQUIRED_FIELDS:
        out.setdefault(k, None)

    for k, default in OPTIONAL_FIELDS_WITH_DEFAULTS.items():
        out.setdefault(k, default)

    # Coerce age to number when possible; otherwise keep None
    age = out.get("age_upon_outcome_in_weeks")
    try:
        if age is None:
            out["age_upon_outcome_in_weeks"] = None
        else:
            out["age_upon_outcome_in_weeks"] = float(age)
    except (TypeError, ValueError):
        out["age_upon_outcome_in_weeks"] = None

    return out

def sanitize_rows(rows: list[dict]) -> list[dict]:
    return [sanitize_record(r) for r in rows]
