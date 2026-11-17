from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTRUCTIONS = (ROOT / "production/project-instructions/PROJECT_INSTRUCTIONS.md").read_text(encoding="utf-8")
QA = (ROOT / "production/knowledge/16_VERIFICATION_AND_QA.md").read_text(encoding="utf-8")


def test_resident_core_declares_reliability_contract():
    assert "## Reliability contract" in INSTRUCTIONS
    for phrase in [
        "Least privilege",
        "Package completeness",
        "Collision preflight",
        "No invented contracts",
        "Secure intake",
        "Verification honesty",
    ]:
        assert phrase in INSTRUCTIONS


def test_qa_has_pre_delivery_reliability_checklist():
    assert "## Pre-delivery reliability checklist" in QA
    # The checklist must downgrade rather than overclaim on failure.
    assert "downgrades the artifact to an accurate blocked state" in QA


def test_reliability_contract_invents_no_engine_facts():
    # Guard against the contract smuggling in forbidden invented surfaces.
    for forbidden in ["Data/Features.tyd", "Data/BuildingBlueprint.tyd", "/Mods/Blueprints/", "LoadAfter"]:
        assert forbidden not in INSTRUCTIONS
