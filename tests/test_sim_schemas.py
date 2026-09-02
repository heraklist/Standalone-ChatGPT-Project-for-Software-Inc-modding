import copy
import json
from pathlib import Path

import jsonschema
import pytest


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_NAMES = (
    "sim-session.schema.json",
    "sim-plan.schema.json",
    "sim-specialist-request.schema.json",
    "sim-specialist-result.schema.json",
    "sim-reference-map.schema.json",
    "sim-release-manifest.schema.json",
    "sim-eval.schema.json",
)


def validator(schema_name: str) -> jsonschema.Draft202012Validator:
    schema_path = ROOT / "schemas" / schema_name
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    return jsonschema.Draft202012Validator(schema)


def assert_invalid(schema_name: str, instance: object) -> None:
    with pytest.raises(jsonschema.ValidationError):
        validator(schema_name).validate(instance)


@pytest.fixture
def minimal_session() -> dict[str, object]:
    return {
        "meta": {"session_id": "session-1"},
        "goal": {"summary": "Create a verified artifact"},
        "target": {"game_version": "Beta 1.8.42"},
        "baseline": {},
        "architecture": {},
        "workspace": {},
        "evidence": {},
        "decisions": [],
        "validation": {},
        "artifact": {
            "state": "ARTIFACT_UNBUILT",
            "verification_level": "V0 DESIGN_READY",
        },
        "risks": [],
        "history": [],
    }


def specialist_result() -> dict[str, object]:
    return {
        "request_id": "request-1",
        "status": "READY",
        "scope": "data",
        "findings": [],
        "decisions": [],
        "proposed_changes": [{"type": "CREATE", "summary": "Add the data file"}],
        "files_touched": [],
        "evidence_used": [],
        "assumptions": [],
        "unresolved_gaps": [],
        "validation": [],
        "requested_followup": [],
        "risk_flags": [{"class": "R1", "summary": "Writes the workspace"}],
        "next_action": "Return the proposal to the orchestrator",
    }


def reference_map() -> dict[str, object]:
    return {
        "references": [
            {
                "reference_id": "reference-1",
                "source_id": "source-1",
                "source_sha256": "a" * 64,
                "output_sha256": "b" * 64,
            }
        ]
    }


def test_sim_schemas_exist_and_are_draft_2020_12_valid() -> None:
    for schema_name in SCHEMA_NAMES:
        validator(schema_name)


def test_session_schema_accepts_minimal_operational_session(
    minimal_session: dict[str, object],
) -> None:
    validator("sim-session.schema.json").validate(minimal_session)


def test_session_schema_rejects_unknown_artifact_state(
    minimal_session: dict[str, object],
) -> None:
    invalid_session = copy.deepcopy(minimal_session)
    invalid_session["artifact"]["state"] = "DONE"
    assert_invalid("sim-session.schema.json", invalid_session)


def test_specialist_result_rejects_unknown_status() -> None:
    invalid_result = specialist_result()
    invalid_result["status"] = "UNKNOWN"
    assert_invalid("sim-specialist-result.schema.json", invalid_result)


def test_specialist_result_rejects_unknown_risk_class() -> None:
    invalid_result = specialist_result()
    invalid_result["risk_flags"][0]["class"] = "R9"
    assert_invalid("sim-specialist-result.schema.json", invalid_result)


@pytest.mark.parametrize("hash_field", ("source_sha256", "output_sha256"))
def test_reference_map_rejects_malformed_hashes(hash_field: str) -> None:
    invalid_map = reference_map()
    invalid_map["references"][0][hash_field] = "not-a-sha256"
    assert_invalid("sim-reference-map.schema.json", invalid_map)
