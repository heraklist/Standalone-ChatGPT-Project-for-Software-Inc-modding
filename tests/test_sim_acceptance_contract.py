from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

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


def _context():
    from tools.sim_acceptance import CertificationContext

    return CertificationContext(
        candidate_tree_sha256="a" * 64,
        semantic_aggregate_sha256="b" * 64,
        source_commit="c" * 40,
        plugin_version="0.2.2-preview",
        exact_target_manifest_sha256="d" * 64,
        protocol_version="sim-live-v2",
        surface="ChatGPT",
    )


def _write_record(path: Path, **overrides: object) -> None:
    record = _valid_record()
    record.update(overrides)
    path.write_text(json.dumps(record), encoding="utf-8")


def test_acceptance_summary_never_mixes_candidate_tree_hashes(tmp_path: Path) -> None:
    from tools.sim_acceptance import summarize_acceptance

    _write_record(tmp_path / "A01-a.json", case_id="A01")
    _write_record(tmp_path / "A02-a.json", case_id="A02")
    _write_record(
        tmp_path / "A03-foreign.json",
        case_id="A03",
        candidate_tree_sha256="e" * 64,
    )

    summary = summarize_acceptance(
        tmp_path,
        _context(),
        required_cases=("A01", "A02", "A03"),
    )
    assert summary.status == "INCOMPLETE"
    assert summary.case_results["A03"] == "NOT_TESTED"


def test_acceptance_summary_uses_terminal_retest_only_inside_same_context(
    tmp_path: Path,
) -> None:
    from tools.sim_acceptance import summarize_acceptance

    _write_record(
        tmp_path / "a06-first.json",
        result="FAIL",
        evidence_refs=["a06-first"],
    )
    _write_record(
        tmp_path / "a06-second.json",
        result="PASS",
        retest_of="a06-first",
        evidence_refs=["a06-second"],
    )

    summary = summarize_acceptance(tmp_path, _context(), required_cases=("A06",))
    assert summary.status == "PASS"
    assert summary.case_results == {"A06": "PASS"}


def test_acceptance_summary_rejects_ambiguous_terminal_retests(tmp_path: Path) -> None:
    from tools.sim_acceptance import summarize_acceptance

    _write_record(tmp_path / "a06-one.json")
    _write_record(tmp_path / "a06-two.json")

    with pytest.raises(ValueError, match="ambiguous terminal"):
        summarize_acceptance(tmp_path, _context(), required_cases=("A06",))


def test_installation_evidence_id_does_not_split_behavioral_candidate(
    tmp_path: Path,
) -> None:
    from tools.sim_acceptance import summarize_acceptance

    _write_record(
        tmp_path / "A01-install-a.json",
        case_id="A01",
        installation_evidence_id="install-a",
    )
    _write_record(
        tmp_path / "A02-install-b.json",
        case_id="A02",
        installation_evidence_id="install-b",
    )

    summary = summarize_acceptance(
        tmp_path,
        _context(),
        required_cases=("A01", "A02"),
    )
    assert summary.status == "PASS"
    assert summary.known_gaps == ()
