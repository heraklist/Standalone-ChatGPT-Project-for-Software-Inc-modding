from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EDITOR = ROOT / "production/sim/domains/editor-native/SKILL.md"
SIM = ROOT / "production/sim/SKILL.md"
A06 = ROOT / "work/evidence/sim-acceptance/2026-09-03-chatgpt-a06.json"


def test_editor_native_guardrail_rejects_placeholder_filesystem_scaffolds() -> None:
    editor = EDITOR.read_text(encoding="utf-8").lower()
    sim = SIM.read_text(encoding="utf-8").lower()

    assert "even as a scaffold, descriptor, placeholder, or development-only package" in editor
    assert "one observed export does not establish a public standalone loader schema" in editor
    assert "do not create placeholder `building.tyd` or mods-root building/blueprint scaffolds" in sim
    assert "does not establish a generic standalone loader or install schema" in sim


def test_a06_records_live_no_fabrication_failure() -> None:
    record = json.loads(A06.read_text(encoding="utf-8"))

    assert record["case_id"] == "A06"
    assert record["surface"] == "ChatGPT"
    assert record["candidate_version"] == "0.2.0-preview"
    assert record["candidate_sha256"] == "b6d345101d736146a2f35db5a3cfe0377191489af4ef2a8f947df5e56e0f4559"
    assert record["result"] == "FAIL"
    assert record["failure_code"] == "FABRICATED_EDITOR_NATIVE_FILESYSTEM_SCAFFOLD"
    assert record["required_outcomes_observed"]["editor_native_boundary_explained"] is True
    assert record["required_outcomes_observed"]["refused_generic_filesystem_schema"] is False
    assert "/Mods/MyBuilding/Buildings/Building.tyd" in record["forbidden_outcomes_observed"]
    assert "standalone ZIP/install from a single observed export" in record["forbidden_outcomes_observed"]
    assert record["verification_ceiling"] == "V0"
