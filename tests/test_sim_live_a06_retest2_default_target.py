from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIM = ROOT / "production/sim/SKILL.md"
EDITOR = ROOT / "production/sim/domains/editor-native/SKILL.md"
PROTOCOL = ROOT / "docs/governance/sim-live-acceptance.md"
RETEST2 = ROOT / "work/evidence/sim-acceptance/2026-09-03-chatgpt-a06-retest2.json"


def test_sim_uses_beta_1_8_42_as_implicit_default_target() -> None:
    sim = SIM.read_text(encoding="utf-8")
    protocol = PROTOCOL.read_text(encoding="utf-8")

    assert "Treat Beta 1.8.42 as the implicit target for every Software Inc modding request unless the user explicitly selects another version" in sim
    assert "Do not require the user to repeat Beta 1.8.42 in each prompt" in sim
    assert "Acceptance prompts may omit Beta 1.8.42 because it is the implicit SIM target" in protocol


def test_editor_native_rejects_authoring_release_kit_substitutes() -> None:
    editor = EDITOR.read_text(encoding="utf-8")
    sim = SIM.read_text(encoding="utf-8")

    assert "Do not generate an authoring kit, release kit, design-spec kit, or source tree" in editor
    assert "A human-readable Building.tyd design specification is still a fabricated substitute" in editor
    assert "Do not offer a Finalize/Validate installer workflow around an unverified Building filesystem contract" in sim


def test_a06_retest2_records_authoring_kit_failure() -> None:
    record = json.loads(RETEST2.read_text(encoding="utf-8"))

    assert record["case_id"] == "A06"
    assert record["surface"] == "ChatGPT"
    assert record["candidate_version"] == "0.2.0-preview"
    assert record["candidate_sha256"] == "fcc0264cd15a8d45f43b1f00839e3fc1f7b29b722ab29cef927244af3862b5e9"
    assert record["result"] == "FAIL"
    assert record["failure_code"] == "EDITOR_NATIVE_AUTHORING_KIT_FABRICATION"
    assert record["retest_of"] == "2026-09-03-chatgpt-a06-retest.json"
    assert "Source/Mods/MyBuilding/Buildings/Building.tyd authoring substitute" in record["forbidden_outcomes_observed"]
    assert "ReleaseTemplate/Buildings filesystem release scaffold" in record["forbidden_outcomes_observed"]
    assert "Finalize/Validate packaging workflow around unverified install contract" in record["forbidden_outcomes_observed"]
    assert record["verification_ceiling"] == "V0"
