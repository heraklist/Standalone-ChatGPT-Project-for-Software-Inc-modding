from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
A04 = ROOT / "work/evidence/sim-acceptance/2026-09-02-chatgpt-a04.json"


def test_a04_records_static_first_code_repair_pass() -> None:
    record = json.loads(A04.read_text(encoding="utf-8"))

    assert record["case_id"] == "A04"
    assert record["surface"] == "ChatGPT"
    assert record["candidate_version"] == "0.2.0-preview"
    assert record["candidate_sha256"] == "b6d345101d736146a2f35db5a3cfe0377191489af4ef2a8f947df5e56e0f4559"
    assert record["result"] == "PASS"
    assert record["required_outcomes_observed"] == {
        "game_compiled_csharp3_profile_selected": True,
        "static_first_analysis": True,
        "expression_bodied_member_blocker_identified": True,
        "enum_caveat_identified": True,
        "playerprefs_blocker_identified": True,
        "documented_persistence_api_used": True,
        "compile_runtime_proof_not_fabricated": True,
    }
    assert record["forbidden_outcomes_observed"] == []
    assert record["verification_ceiling"] == "V0"
