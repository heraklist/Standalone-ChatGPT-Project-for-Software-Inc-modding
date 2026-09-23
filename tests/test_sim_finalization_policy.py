from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]


def _policy() -> dict:
    return {
        "rules": [{
            "artifact_family": "DATA_TYD",
            "artifact_surface": "MOD_PACKAGE",
            "delivery_mode": "INSTALLABLE_ZIP",
            "claim_class": "STATIC_DELIVERY",
            "minimum_verification_level": "V2",
            "required_checks": ["DATA_LAYOUT", "STATIC_REVIEW"],
        }]
    }


def _candidate(level: str, checks: list[dict]) -> dict:
    return {
        "architecture": {
            "artifact_surface": "MOD_PACKAGE",
            "delivery_mode": "INSTALLABLE_ZIP",
        },
        "artifact": {
            "state": "CANDIDATE_ARTIFACT",
            "family": "DATA_TYD",
            "claim_class": "STATIC_DELIVERY",
            "verification_level": level,
        },
        "validation": {"checks": checks},
    }


def test_candidate_to_final_requires_policy_evidence() -> None:
    from tools.sim_contracts import can_advance_artifact

    session = _candidate(
        "V1",
        [{"id": "DATA_LAYOUT", "result": "PASS", "evidence_refs": ["e1"]}],
    )
    assert (
        can_advance_artifact(
            "CANDIDATE_ARTIFACT", "FINAL_ARTIFACT", session, _policy()
        )
        is False
    )


def test_candidate_to_final_allows_v2_with_all_required_evidence() -> None:
    from tools.sim_contracts import can_advance_artifact

    session = _candidate(
        "V2",
        [
            {"id": "DATA_LAYOUT", "result": "PASS", "evidence_refs": ["e1"]},
            {"id": "STATIC_REVIEW", "result": "PASS", "evidence_refs": ["e2"]},
        ],
    )
    assert (
        can_advance_artifact(
            "CANDIDATE_ARTIFACT", "FINAL_ARTIFACT", session, _policy()
        )
        is True
    )


def test_candidate_to_final_rejects_pass_check_without_evidence_ref() -> None:
    from tools.sim_contracts import can_advance_artifact

    session = _candidate(
        "V2",
        [
            {"id": "DATA_LAYOUT", "result": "PASS", "evidence_refs": ["e1"]},
            {"id": "STATIC_REVIEW", "result": "PASS", "evidence_refs": []},
        ],
    )
    assert (
        can_advance_artifact(
            "CANDIDATE_ARTIFACT", "FINAL_ARTIFACT", session, _policy()
        )
        is False
    )


def test_candidate_to_final_rejects_missing_matching_rule() -> None:
    from tools.sim_contracts import can_advance_artifact

    session = _candidate(
        "V2",
        [
            {"id": "DATA_LAYOUT", "result": "PASS", "evidence_refs": ["e1"]},
            {"id": "STATIC_REVIEW", "result": "PASS", "evidence_refs": ["e2"]},
        ],
    )
    session["artifact"]["family"] = "BUILDING"
    assert (
        can_advance_artifact(
            "CANDIDATE_ARTIFACT", "FINAL_ARTIFACT", session, _policy()
        )
        is False
    )


def test_finalization_policy_file_is_versioned_and_editor_native_fail_closed() -> None:
    from tools.sim_contracts import load_finalization_policy

    path = ROOT / "production/sim/manifests/finalization-policy.json"
    policy = load_finalization_policy(path)
    assert policy["schema_version"] == 1
    assert any(
        rule["artifact_family"] == "DATA_TYD"
        and rule["minimum_verification_level"] == "V2"
        for rule in policy["rules"]
    )
    assert not any(
        rule["artifact_family"] == "BUILDING"
        and rule["artifact_surface"] == "MOD_PACKAGE"
        for rule in policy["rules"]
    )


def test_session_schema_accepts_finalization_policy_inputs() -> None:
    schema = json.loads(
        (ROOT / "schemas/sim-session.schema.json").read_text(encoding="utf-8")
    )
    artifact = schema["properties"]["artifact"]["properties"]
    assert artifact["family"]["enum"] == [
        "DATA_TYD",
        "SIPL",
        "CODE",
        "FURNITURE",
        "MATERIALS",
        "LOCALIZATION",
        "HARDWARE_DESIGN",
        "BUILDING_BLUEPRINT",
        "BUILDING",
    ]
    assert artifact["claim_class"]["enum"] == [
        "STATIC_DELIVERY",
        "NATIVE_OPEN_DELIVERY",
        "BEHAVIOR_VERIFIED_DELIVERY",
        "REGRESSION_VERIFIED_DELIVERY",
    ]


def test_session_schema_rejects_unknown_family_and_claim_class() -> None:
    schema = json.loads(
        (ROOT / "schemas/sim-session.schema.json").read_text(encoding="utf-8")
    )
    validator = jsonschema.Draft202012Validator(schema)
    base = {
        "meta": {"session_id": "s"},
        "goal": {"summary": "x"},
        "target": {"game_version": "Beta 1.8.42"},
        "baseline": {},
        "architecture": {
            "artifact_surface": "MOD_PACKAGE",
            "delivery_mode": "INSTALLABLE_ZIP",
        },
        "workspace": {},
        "evidence": {},
        "decisions": [],
        "validation": {"checks": []},
        "artifact": {
            "state": "CANDIDATE_ARTIFACT",
            "verification_level": "V2",
            "family": "NOT_REAL",
            "claim_class": "NOT_REAL",
        },
        "risks": [],
        "history": [],
    }
    assert list(validator.iter_errors(base))
