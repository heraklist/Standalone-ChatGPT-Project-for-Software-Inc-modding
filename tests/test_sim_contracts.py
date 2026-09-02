from __future__ import annotations


def test_artifact_cannot_skip_unbuilt_to_final() -> None:
    from tools.sim_contracts import can_advance_artifact

    session = {"artifact": {"state": "ARTIFACT_UNBUILT"}}
    assert can_advance_artifact("ARTIFACT_UNBUILT", "FINAL_ARTIFACT", session) is False


def test_artifact_allows_adjacent_forward_and_noop_but_rejects_downgrade() -> None:
    from tools.sim_contracts import can_advance_artifact

    session = {"artifact": {"state": "ARTIFACT_UNBUILT"}}
    assert can_advance_artifact("ARTIFACT_UNBUILT", "ARTIFACT_UNBUILT", session) is True
    assert can_advance_artifact("ARTIFACT_UNBUILT", "CANDIDATE_ARTIFACT", session) is True

    candidate = {"artifact": {"state": "CANDIDATE_ARTIFACT"}}
    assert can_advance_artifact("CANDIDATE_ARTIFACT", "ARTIFACT_UNBUILT", candidate) is False
    assert can_advance_artifact("CANDIDATE_ARTIFACT", "FINAL_ARTIFACT", candidate) is True


def test_artifact_rejects_session_state_mismatch() -> None:
    from tools.sim_contracts import can_advance_artifact

    session = {"artifact": {"state": "CANDIDATE_ARTIFACT"}}
    assert can_advance_artifact("ARTIFACT_UNBUILT", "CANDIDATE_ARTIFACT", session) is False


def test_v2_to_v3_requires_load_or_native_open_evidence() -> None:
    from tools.sim_contracts import can_advance_verification

    assert can_advance_verification("V2", "V3", set()) is False
    assert can_advance_verification("V2", "V3", {"LOAD_VERIFIED"}) is True
    assert can_advance_verification("V2", "V3", {"NATIVE_OPEN_VERIFIED"}) is True


def test_verification_levels_require_exact_adjacent_evidence() -> None:
    from tools.sim_contracts import can_advance_verification

    assert can_advance_verification("V0", "V1", {"ARTIFACT_GENERATED"}) is True
    assert can_advance_verification("V1", "V2", {"STATIC_REVIEWED"}) is True
    assert can_advance_verification("V3", "V4", {"BEHAVIOR_VERIFIED"}) is True
    assert can_advance_verification("V4", "V5", {"REGRESSION_VERIFIED"}) is True
    assert can_advance_verification("V1", "V3", {"LOAD_VERIFIED"}) is False


def test_verification_noop_allowed_and_downgrade_rejected() -> None:
    from tools.sim_contracts import can_advance_verification

    assert can_advance_verification("V2", "V2", set()) is True
    assert can_advance_verification("V3", "V2", {"STATIC_REVIEWED"}) is False
