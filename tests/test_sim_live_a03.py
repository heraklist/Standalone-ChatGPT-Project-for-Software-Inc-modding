from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
A03 = ROOT / "work/evidence/sim-acceptance/2026-09-02-chatgpt-a03.json"


def test_a03_records_data_sipl_boundary_and_entrypoint_pass() -> None:
    record = json.loads(A03.read_text(encoding="utf-8"))

    assert record["case_id"] == "A03"
    assert record["surface"] == "ChatGPT"
    assert record["candidate_version"] == "0.2.0-preview"
    assert record["candidate_sha256"] == "b6d345101d736146a2f35db5a3cfe0377191489af4ef2a8f947df5e56e0f4559"
    assert record["result"] == "PASS"
    assert record["required_outcomes_observed"] == {
        "data_ownership_before_sipl": True,
        "tyd_list_and_sipl_array_distinct": True,
        "script_end_of_day_product_scope": True,
        "runtype_constraints_preserved": True,
        "external_script_binding_supported": True,
        "runtime_verification_not_fabricated": True,
    }
    assert record["forbidden_outcomes_observed"] == []
    assert record["verification_ceiling"] == "V0"
