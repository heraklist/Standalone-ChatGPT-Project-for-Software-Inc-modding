from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "production/sim/SKILL.md"


def skill_text() -> str:
    return SKILL.read_text(encoding="utf-8")


def test_sim_skill_is_explicit_public_entry_and_central_orchestrator() -> None:
    text = skill_text()
    lowered = text.lower()
    assert "name: sim" in lowered
    assert "@sim" in lowered
    assert "explicit" in lowered
    assert "automatic activation" in lowered
    assert "must not" in lowered
    assert "orchestrator" in lowered
    assert "only the sim orchestrator" in lowered


def test_sim_skill_encodes_high_autonomy_with_material_fork_boundary() -> None:
    lowered = skill_text().lower()
    assert "high autonomy" in lowered
    assert "material" in lowered
    assert "fork" in lowered
    assert "missing input" in lowered
    assert "protected" in lowered


def test_sim_skill_encodes_zero_fabrication_and_evidence_routing() -> None:
    lowered = skill_text().lower()
    assert "canonical evidence" in lowered
    assert "research" in lowered
    assert "must not invent" in lowered or "never fabricate" in lowered
    assert "research_required" in lowered


def test_sim_skill_preserves_non_destructive_security_contract() -> None:
    lowered = skill_text().lower()
    assert "read-only baseline" in lowered
    assert "working copy" in lowered
    for risk_class in ("r0", "r1", "r2", "r3"):
        assert risk_class in lowered
    assert "explicit approval" in lowered


def test_sim_skill_preserves_artifact_verification_and_capability_contract() -> None:
    text = skill_text()
    for token in (
        "ARTIFACT_UNBUILT",
        "CANDIDATE_ARTIFACT",
        "FINAL_ARTIFACT",
        "V0 DESIGN_READY",
        "V1 ARTIFACT_GENERATED",
        "V2 STATICALLY_REVIEWED",
        "V3 LOAD_OR_NATIVE_OPEN_VERIFIED",
        "V4 BEHAVIOR_VERIFIED",
        "V5 REGRESSION_VERIFIED",
        "NOT_EXECUTED",
    ):
        assert token in text
    lowered = text.lower()
    assert "verification before delivery" in lowered
    assert "runtime" in lowered
    assert "static" in lowered


def test_sim_skill_keeps_specialists_internal_and_session_operational_only() -> None:
    lowered = skill_text().lower()
    assert "silent by default" in lowered
    assert "do not dispatch" in lowered
    assert "do not mutate" in lowered
    assert "chain-of-thought" in lowered
    assert "operational" in lowered
