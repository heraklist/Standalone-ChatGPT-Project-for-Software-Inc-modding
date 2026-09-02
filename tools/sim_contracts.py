from __future__ import annotations

ARTIFACT_STATES = (
    "ARTIFACT_UNBUILT",
    "CANDIDATE_ARTIFACT",
    "FINAL_ARTIFACT",
)

VERIFICATION_LEVELS = ("V0", "V1", "V2", "V3", "V4", "V5")
VERIFICATION_EVIDENCE = {
    "V1": {"ARTIFACT_GENERATED"},
    "V2": {"STATIC_REVIEWED"},
    "V3": {"LOAD_VERIFIED", "NATIVE_OPEN_VERIFIED"},
    "V4": {"BEHAVIOR_VERIFIED"},
    "V5": {"REGRESSION_VERIFIED"},
}


def can_advance_artifact(old: str, new: str, session: dict) -> bool:
    if old not in ARTIFACT_STATES or new not in ARTIFACT_STATES:
        return False
    current = session.get("artifact", {}).get("state")
    if current != old:
        return False
    old_index = ARTIFACT_STATES.index(old)
    new_index = ARTIFACT_STATES.index(new)
    if new_index == old_index:
        return True
    return new_index == old_index + 1


def can_advance_verification(old: str, new: str, evidence: set[str]) -> bool:
    if old not in VERIFICATION_LEVELS or new not in VERIFICATION_LEVELS:
        return False
    old_index = VERIFICATION_LEVELS.index(old)
    new_index = VERIFICATION_LEVELS.index(new)
    if new_index == old_index:
        return True
    if new_index != old_index + 1:
        return False
    required = VERIFICATION_EVIDENCE.get(new)
    return bool(required and required.intersection(evidence))
