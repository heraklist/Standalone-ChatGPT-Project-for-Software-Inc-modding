from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INITIAL = ROOT / "work/evidence/sim-acceptance/2026-09-02-chatgpt-a01.json"
RETEST = ROOT / "work/evidence/sim-acceptance/2026-09-02-chatgpt-a01-retest.json"


def test_a01_retest_preserves_initial_failure_and_records_repaired_pass() -> None:
    initial = json.loads(INITIAL.read_text(encoding="utf-8"))
    retest = json.loads(RETEST.read_text(encoding="utf-8"))

    assert initial["case_id"] == "A01"
    assert initial["result"] == "FAIL"
    assert initial["failure_code"] == "STALE_GLOBAL_EXACT_TARGET_GAP_CLAIM"

    assert retest["case_id"] == "A01"
    assert retest["surface"] == "ChatGPT"
    assert retest["candidate_version"] == "0.2.0-preview"
    assert retest["candidate_sha256"] == "b6d345101d736146a2f35db5a3cfe0377191489af4ef2a8f947df5e56e0f4559"
    assert retest["result"] == "PASS"
    assert retest["retest_of"] == "2026-09-02-chatgpt-a01.json"
    assert retest["required_outcomes_observed"] == {
        "explicit_sim_activation": True,
        "data_tyd_routing": True,
        "beta_1_8_42_evidence_discipline": True,
    }
    assert retest["forbidden_outcomes_observed"] == []
    assert retest["verification_ceiling"] == "V0"
