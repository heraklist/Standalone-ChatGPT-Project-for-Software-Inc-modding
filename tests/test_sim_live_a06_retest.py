from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EDITOR = ROOT / "production/sim/domains/editor-native/SKILL.md"
SIM = ROOT / "production/sim/SKILL.md"
RETEST = ROOT / "work/evidence/sim-acceptance/2026-09-03-chatgpt-a06-retest.json"


def test_editor_native_guardrail_rejects_storage_path_install_promotion() -> None:
    editor = EDITOR.read_text(encoding="utf-8")
    sim = SIM.read_text(encoding="utf-8")

    assert "Cloud-save, save-game, cache, or observed storage paths are not install contracts" in editor
    assert "Do not generate Buildings/ or Blueprints/ filesystem kits" in editor
    assert "Storage or cloud-sync observations must never be promoted to verified install paths" in sim
    assert "report TOOLING_BLOCKED instead of manufacturing a filesystem kit" in sim


def test_a06_retest_records_storage_path_promotion_failure() -> None:
    record = json.loads(RETEST.read_text(encoding="utf-8"))

    assert record["case_id"] == "A06"
    assert record["surface"] == "ChatGPT"
    assert record["candidate_version"] == "0.2.0-preview"
    assert record["candidate_sha256"] == "4e9933874d7e897f3719f9a47d541dac0dbebd55afa1464f213236048ba30466"
    assert record["result"] == "FAIL"
    assert record["failure_code"] == "STORAGE_PATH_PROMOTED_TO_INSTALL_CONTRACT"
    assert record["retest_of"] == "2026-09-03-chatgpt-a06.json"
    assert "Buildings/MyBuilding/MyBuilding.build presented as installable structure" in record["forbidden_outcomes_observed"]
    assert "Blueprints/MyBuilding/MyBuilding.xml presented as installable structure" in record["forbidden_outcomes_observed"]
    assert "source/Building.tyd.example placeholder" in record["forbidden_outcomes_observed"]
    assert record["verification_ceiling"] == "V0"
