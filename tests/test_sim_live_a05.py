from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
A05 = ROOT / "work/evidence/sim-acceptance/2026-09-02-chatgpt-a05.json"


def test_a05_records_furniture_materials_live_pass() -> None:
    record = json.loads(A05.read_text(encoding="utf-8"))

    assert record["case_id"] == "A05"
    assert record["surface"] == "ChatGPT"
    assert record["candidate_version"] == "0.2.0-preview"
    assert record["candidate_sha256"] == "b6d345101d736146a2f35db5a3cfe0377191489af4ef2a8f947df5e56e0f4559"
    assert record["result"] == "PASS"
    assert record["required_outcomes_observed"] == {
        "furniture_transformparent_order_scoped_to_hierarchy": True,
        "documented_visit_interaction_point_used": True,
        "materials_loader_and_table_identity_preserved": True,
        "material_presets_and_channel_semantics_preserved": True,
        "synthetic_non_proprietary_assets_stated": True,
        "fresh_placement_runtime_boundary_preserved": True,
    }
    assert record["forbidden_outcomes_observed"] == []
    assert record["verification_ceiling"] == "V2"
    assert record["evaluator_artifact_revalidation"] == "NOT_EXECUTED"
