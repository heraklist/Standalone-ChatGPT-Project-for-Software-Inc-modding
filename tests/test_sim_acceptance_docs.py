from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/governance/sim-live-acceptance.md"
EVIDENCE = ROOT / "work/evidence/sim-acceptance/README.md"
SNAPSHOT = ROOT / "work/evidence/sim-acceptance/2026-09-02-agent-checkpoint.json"
MATRIX = ROOT / "production/sim/manifests/compatibility-matrix.json"


def test_acceptance_protocol_defines_a01_a12_and_fail_closed_statuses() -> None:
    text = DOC.read_text(encoding="utf-8")
    for index in range(1, 13):
        assert f"A{index:02d}" in text
    assert "@Sim" in text
    assert "PASS" in text
    assert "FAIL" in text
    assert "PLATFORM_LIMITATION" in text
    assert "NOT_TESTED" in text
    assert "forbidden outcomes" in text.lower()
    assert "evidence capture" in text.lower()


def test_acceptance_protocol_covers_exact_task_20_cases() -> None:
    text = DOC.read_text(encoding="utf-8")
    required = (
        "cold activation",
        "brainstorm",
        "Data + SIPL",
        "Code repair",
        "Furniture / Materials",
        "Building no-fabrication",
        "broken ZIP repair",
        "collision",
        "limited capability",
        "multi-turn",
        "yield/resume",
        "artifact + V honesty",
    )
    for phrase in required:
        assert phrase in text


def test_evidence_readme_forbids_synthetic_live_passes() -> None:
    text = EVIDENCE.read_text(encoding="utf-8")
    assert "non-sensitive" in text
    assert "Do not record PASS" in text
    assert "PLATFORM_LIMITATION" in text
    assert "NOT_TESTED" in text


def test_compatibility_matrix_uses_observation_status_vocabulary() -> None:
    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    allowed = {"SUPPORTED", "PLATFORM_LIMITATION", "CAPABILITY_DEPENDENT", "NOT_TESTED"}
    for capabilities in matrix["surfaces"].values():
        assert set(capabilities) == {
            "explicit_invocation",
            "thread_persistence",
            "script_execution",
            "artifact_creation",
        }
        assert set(capabilities.values()) <= allowed


def test_cross_surface_section_matches_v022_certification_profile() -> None:
    text = DOC.read_text(encoding="utf-8")
    for phrase in (
        "ChatGPT",
        "A01–A12",
        "Codex",
        "A01, A03, A09, A10, A12",
        "ChatGPT Project",
        "non-blocking",
        "NOT_EXECUTED",
        "lower verification ceiling",
    ):
        assert phrase in text


def test_v022_protocol_documents_candidate_bound_fresh_sequence() -> None:
    text = DOC.read_text(encoding="utf-8")
    for phrase in (
        "candidate_tree_sha256",
        "exact_target_manifest_sha256",
        "certification_protocol_version",
        "installation_evidence_id",
        "A06 first",
        "fresh A01–A05",
        "A01–A12",
    ):
        assert phrase in text
    assert "candidate_sha256" not in text


def test_agent_checkpoint_records_no_synthetic_live_passes() -> None:
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    assert snapshot["candidate_version"] == "0.2.0-preview"
    assert snapshot["execution_boundary"] == "NO_SKILL_INSTALL_ACTION_AVAILABLE"
    assert set(snapshot["surfaces"]) == {"ChatGPT", "ChatGPT Project", "Codex"}
    assert all(value == "NOT_TESTED" for value in snapshot["surfaces"].values())
    assert [case["case_id"] for case in snapshot["cases"]] == [f"A{i:02d}" for i in range(1, 13)]
    assert all(case["result"] == "NOT_TESTED" for case in snapshot["cases"])
    assert not any(case["result"] == "PASS" for case in snapshot["cases"])
