from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]


def _schema() -> dict:
    return json.loads(
        (ROOT / "schemas/sim-acceptance-evidence.schema.json").read_text(
            encoding="utf-8"
        )
    )


def _valid_record() -> dict:
    return {
        "schema_version": 2,
        "case_id": "A06",
        "surface": "ChatGPT",
        "result": "PASS",
        "candidate_tree_sha256": "a" * 64,
        "semantic_aggregate_sha256": "b" * 64,
        "candidate_source_commit": "c" * 40,
        "plugin_version": "0.2.2-preview",
        "exact_target_manifest_sha256": "d" * 64,
        "certification_protocol_version": "sim-live-v2",
        "installation_evidence_id": "install-chatgpt-a",
        "host_observation": {"resolver": "@sim"},
        "evidence_refs": ["obs-a06"],
        "retest_of": None,
        "recorded_at": "2026-09-22T20:00:00+03:00",
    }


def test_acceptance_schema_accepts_complete_candidate_bound_record() -> None:
    jsonschema.Draft202012Validator(_schema()).validate(_valid_record())


def test_acceptance_schema_rejects_missing_candidate_tree_identity() -> None:
    record = _valid_record()
    del record["candidate_tree_sha256"]
    errors = list(jsonschema.Draft202012Validator(_schema()).iter_errors(record))
    assert errors


def test_acceptance_schema_rejects_non_a01_a12_case() -> None:
    record = _valid_record()
    record["case_id"] = "A13"
    errors = list(jsonschema.Draft202012Validator(_schema()).iter_errors(record))
    assert errors
