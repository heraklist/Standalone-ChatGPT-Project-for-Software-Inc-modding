from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIM = ROOT / "production/sim/SKILL.md"
K15 = ROOT / "production/knowledge/15_BUILD_EDIT_REPAIR_AND_DELIVERY.md"
K16 = ROOT / "production/knowledge/16_VERIFICATION_AND_QA.md"
STATE = ROOT / "production/sim/references/state-vocabulary.md"
VERIFY_LIFECYCLE = ROOT / "production/sim/lifecycle/verification-delivery/SKILL.md"

CANONICAL_LEVELS = (
    "V0 DESIGN_READY",
    "V1 ARTIFACT_GENERATED",
    "V2 STATICALLY_REVIEWED",
    "V3 LOAD_OR_NATIVE_OPEN_VERIFIED",
    "V4 BEHAVIOR_VERIFIED",
    "V5 REGRESSION_VERIFIED",
)

CANONICAL_ARTIFACT_STATES = (
    "ARTIFACT_UNBUILT",
    "CANDIDATE_ARTIFACT",
    "FINAL_ARTIFACT",
)


def test_state_vocabulary_is_explicit_runtime_authority() -> None:
    state = STATE.read_text(encoding="utf-8")
    sim = SIM.read_text(encoding="utf-8")

    assert "# SIM State Vocabulary" in state
    assert "references/state-vocabulary.md" in sim
    for value in (*CANONICAL_LEVELS, *CANONICAL_ARTIFACT_STATES):
        assert value in state


def test_k16_and_lifecycle_use_canonical_verification_labels() -> None:
    k16 = K16.read_text(encoding="utf-8")
    lifecycle = VERIFY_LIFECYCLE.read_text(encoding="utf-8")

    for value in CANONICAL_LEVELS:
        assert value in k16
        assert value in lifecycle

    assert "V1 FILES_GENERATED" not in k16
    assert "V3 LOAD_VERIFIED" not in k16


def test_surface_specific_delivery_labels_are_mapped_not_parallel_state_machines() -> None:
    state = STATE.read_text(encoding="utf-8")
    k15 = K15.read_text(encoding="utf-8")

    assert "FINAL_VERIFIED_ZIP" in k15
    assert "FINAL_VERIFIED_NATIVE_ARTIFACT" in k15
    assert "CANDIDATE_NATIVE_ARTIFACT" in k15

    assert "FINAL_VERIFIED_ZIP" in state
    assert "FINAL_VERIFIED_NATIVE_ARTIFACT" in state
    assert "CANDIDATE_NATIVE_ARTIFACT" in state
    assert "surface-specific delivery labels" in state
    assert "not additional artifact-state enums" in state


def test_blocked_readiness_labels_do_not_advance_artifact_or_verification_state() -> None:
    state = STATE.read_text(encoding="utf-8")

    for value in ("READY_FOR_GAME_TESTING", "TOOLING_BLOCKED", "PARTIAL_BUILD"):
        assert value in state
    assert "do not by themselves advance" in state
