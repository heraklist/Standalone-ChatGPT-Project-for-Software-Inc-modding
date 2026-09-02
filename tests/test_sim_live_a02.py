from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
A02 = ROOT / "work/evidence/sim-acceptance/2026-09-02-chatgpt-a02.json"


def test_a02_records_bounded_evidence_aware_brainstorm_pass() -> None:
    record = json.loads(A02.read_text(encoding="utf-8"))

    assert record["case_id"] == "A02"
    assert record["surface"] == "ChatGPT"
    assert record["candidate_version"] == "0.2.0-preview"
    assert record["candidate_sha256"] == "b6d345101d736146a2f35db5a3cfe0377191489af4ef2a8f947df5e56e0f4559"
    assert record["result"] == "PASS"
    assert record["required_outcomes_observed"] == {
        "bounded_brainstorm_for_open_ended_task": True,
        "gameplay_feasibility_scope_compared": True,
        "evidence_aware_technical_boundaries": True,
        "implementation_deferred_until_selection": True,
    }
    assert record["forbidden_outcomes_observed"] == []
    assert record["verification_ceiling"] == "V0"
