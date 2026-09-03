from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRUTH = ROOT / "production/knowledge/01_EVIDENCE_VERSION_AND_TRUTH.md"
SIM_SKILL = ROOT / "production/sim/SKILL.md"
SIM_TRUTH = ROOT / "production/sim/references/evidence-truth.md"
MATRIX = ROOT / "production/sim/manifests/compatibility-matrix.json"
A01 = ROOT / "work/evidence/sim-acceptance/2026-09-02-chatgpt-a01.json"


def test_canonical_truth_declares_exact_target_gate_resolved() -> None:
    text = TRUTH.read_text(encoding="utf-8")
    assert "currency_summary: EXACT_TARGET" in text
    assert "Beta 1.8.42 exact environment corpus pending" not in text
    assert "exact-target generation gate is resolved" in text.lower()


def test_sim_truth_copy_and_orchestrator_do_not_globalize_claim_specific_gaps() -> None:
    truth = SIM_TRUTH.read_text(encoding="utf-8")
    skill = SIM_SKILL.read_text(encoding="utf-8")
    assert "currency_summary: EXACT_TARGET" in truth
    assert "Beta 1.8.42 exact environment corpus pending" not in truth
    assert "GENERATION_GRADE_EXACT_TARGET" in skill
    assert "claim-specific" in skill.lower()
    assert "do not describe the canonical Beta 1.8.42 target as pending" in skill


def test_a01_records_observed_failure_and_supported_explicit_invocation() -> None:
    record = json.loads(A01.read_text(encoding="utf-8"))
    assert record["case_id"] == "A01"
    assert record["surface"] == "ChatGPT"
    assert record["result"] == "FAIL"
    assert record["failure_code"] == "STALE_GLOBAL_EXACT_TARGET_GAP_CLAIM"
    assert record["required_outcomes_observed"]["explicit_sim_activation"] is True
    assert record["required_outcomes_observed"]["data_tyd_routing"] is True
    assert record["forbidden_outcomes_observed"] == []

    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    assert matrix["surfaces"]["ChatGPT"]["explicit_invocation"] == "SUPPORTED"
