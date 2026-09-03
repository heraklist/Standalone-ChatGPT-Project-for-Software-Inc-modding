from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RETEST3 = ROOT / "work/evidence/sim-acceptance/2026-09-03-chatgpt-a06-retest3.json"


def test_a06_retest3_records_repeated_authoring_kit_failure() -> None:
    record = json.loads(RETEST3.read_text(encoding="utf-8"))

    assert record["case_id"] == "A06"
    assert record["surface"] == "ChatGPT"
    assert record["candidate_version"] == "0.2.0-preview"
    assert record["candidate_sha256"] == "aa1f50a0c1605c203f233d6b8870e7ba219ca8a637ef6e57888445c56335d234"
    assert record["result"] == "FAIL"
    assert record["failure_code"] == "EDITOR_NATIVE_AUTHORING_KIT_FABRICATION"
    assert record["required_outcomes_observed"]["implicit_beta_1_8_42_default"] is True
    assert record["required_outcomes_observed"]["editor_native_boundary_explained"] is True
    assert record["required_outcomes_observed"]["refused_generic_filesystem_schema"] is False
    assert record["required_outcomes_observed"]["tooling_blocked_without_substitute_artifact"] is False
    assert "Mods/MyBuilding/Buildings/Building.tyd" in record["forbidden_outcomes_observed"]
    assert "installer/verifier/release-builder around unverified Building package contract" in record["forbidden_outcomes_observed"]
    assert record["verification_ceiling"] == "V0"
