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

SCHEMA_DIALECT = "https://json-schema.org/draft/2020-12/schema"


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


@pytest.fixture
def operational_session(minimal_session: dict[str, object]) -> dict[str, object]:
    session = copy.deepcopy(minimal_session)
    session.update(
        {
            "baseline": {
                "artifact_identity": "uploaded-mod-v1",
                "revision": "revision-1",
                "read_only": True,
                "files": [
                    {
                        "path": "uploads/MyMod.zip",
                        "sha256": "a" * 64,
                    }
                ],
            },
            "architecture": {
                "owner_families": ["DATA"],
                "artifact_surface": "MOD_PACKAGE",
                "delivery_mode": "INSTALLABLE_ZIP",
            },
            "workspace": {
                "files": [
                    {
                        "path": "workspace/MyMod/Companies.tyd",
                        "purpose": "repair working copy",
                        "sha256": "b" * 64,
                    }
                ]
            },
            "evidence": {
                "items": [
                    {
                        "evidence_id": "evidence-1",
                        "source_class": "RUNTIME",
                        "source_role": "RUNTIME_EVIDENCE",
                        "currency": "EXACT_TARGET",
                        "scope": "ARTIFACT",
                        "confidence": "HIGH",
                        "verification": "USER_REPORTED",
                        "conflict_state": "CONSISTENT",
                    }
                ]
            },
            "validation": {
                "profile": "STANDARD",
                "checks": [
                    {
                        "id": "data-layout",
                        "result": "PASS",
                        "evidence_refs": ["evidence-1"],
                    }
                ],
            },
        }
    )
    return session


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
        "schema_version": 1,
        "entries": [
            {
                "reference_id": "reference-1",
                "source_id": "source-1",
                "output_path": "production/sim/references/data.md",
                "canonical_source_paths": ["production/knowledge/04_DATA_MODDING.md"],
                "source_sha256": "a" * 64,
                "transform_type": "COPY",
                "output_sha256": "b" * 64,
            }
        ]
    }


def release_manifest() -> dict[str, object]:
    return {
        "sim_version": "0.2.0-preview",
        "channel": "PREVIEW",
        "canonical_target": "Software Inc Beta 1.8.42",
        "evidence_grade": "GENERATION_GRADE",
        "source_revision": "b18ea6f",
        "skill_package_digest": "c" * 64,
        "reference_map_digest": "d" * 64,
        "domain_eval_results": ["E01: PASS"],
        "sim_eval_results": ["S001: PASS"],
        "security_results": ["security: PASS"],
        "artifact_fixture_results": ["fixture: PASS"],
        "cross_surface_acceptance": "PENDING",
        "known_gaps": [],
        "release_status": "PREVIEW",
    }


def test_sim_schemas_exist_and_are_draft_2020_12_valid() -> None:
    for schema_name in SCHEMA_NAMES:
        schema_path = ROOT / "schemas" / schema_name
        schema = json.loads(schema_path.read_text(encoding="utf-8"))

        assert schema["$schema"] == SCHEMA_DIALECT
        validator(schema_name)


def test_session_schema_accepts_minimal_operational_session(
    minimal_session: dict[str, object],
) -> None:
    validator("sim-session.schema.json").validate(minimal_session)


def test_session_schema_accepts_non_empty_operational_session(
    operational_session: dict[str, object],
) -> None:
    validator("sim-session.schema.json").validate(operational_session)


@pytest.mark.parametrize(
    "section_name", ("baseline", "architecture", "workspace", "evidence", "validation")
)
def test_session_operational_sections_reject_unknown_properties(
    operational_session: dict[str, object], section_name: str
) -> None:
    invalid_session = copy.deepcopy(operational_session)
    invalid_session[section_name]["unexpected"] = "not permitted"
    assert_invalid("sim-session.schema.json", invalid_session)


@pytest.mark.parametrize(
    ("section_name", "field_name", "invalid_value"),
    (
        ("baseline", "read_only", "true"),
        ("architecture", "owner_families", "DATA"),
        ("workspace", "files", {}),
        ("evidence", "items", {}),
        ("validation", "profile", 1),
    ),
)
def test_session_operational_sections_reject_wrong_types(
    operational_session: dict[str, object],
    section_name: str,
    field_name: str,
    invalid_value: object,
) -> None:
    invalid_session = copy.deepcopy(operational_session)
    invalid_session[section_name][field_name] = invalid_value
    assert_invalid("sim-session.schema.json", invalid_session)


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


def test_reference_map_accepts_task_two_empty_source_map() -> None:
    validator("sim-reference-map.schema.json").validate(
        {"schema_version": 1, "entries": []}
    )


def test_reference_map_rejects_ambiguous_multi_source_digest() -> None:
    invalid_map = reference_map()
    invalid_map["entries"][0]["canonical_source_paths"].append(
        "production/knowledge/05_SIPL.md"
    )

    assert_invalid("sim-reference-map.schema.json", invalid_map)


@pytest.mark.parametrize(
    "field_name", ("output_path", "canonical_source_paths", "transform_type")
)
def test_reference_map_requires_traceability_fields(field_name: str) -> None:
    invalid_map = reference_map()
    validator("sim-reference-map.schema.json").validate(invalid_map)
    del invalid_map["entries"][0][field_name]
    assert_invalid("sim-reference-map.schema.json", invalid_map)


@pytest.mark.parametrize("hash_field", ("source_sha256", "output_sha256"))
def test_reference_map_rejects_malformed_hashes(hash_field: str) -> None:
    invalid_map = reference_map()
    invalid_map["entries"][0][hash_field] = "not-a-sha256"
    assert_invalid("sim-reference-map.schema.json", invalid_map)


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    (
        ("canonical_target", "Software Inc Beta 9.9.9"),
        ("evidence_grade", "DOCUMENT_ONLY"),
    ),
)
def test_release_manifest_rejects_noncanonical_claims(
    field_name: str, invalid_value: str
) -> None:
    invalid_manifest = release_manifest()
    invalid_manifest[field_name] = invalid_value
    assert_invalid("sim-release-manifest.schema.json", invalid_manifest)
