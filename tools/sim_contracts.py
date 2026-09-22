from __future__ import annotations

import json
from pathlib import Path

ARTIFACT_STATES = (
    "ARTIFACT_UNBUILT",
    "CANDIDATE_ARTIFACT",
    "FINAL_ARTIFACT",
)

VERIFICATION_LABELS = {
    "V0": "DESIGN_READY",
    "V1": "ARTIFACT_GENERATED",
    "V2": "STATICALLY_REVIEWED",
    "V3": "LOAD_OR_NATIVE_OPEN_VERIFIED",
    "V4": "BEHAVIOR_VERIFIED",
    "V5": "REGRESSION_VERIFIED",
}
VERIFICATION_LEVELS = tuple(VERIFICATION_LABELS)
VERIFICATION_EVIDENCE = {
    "V1": {"ARTIFACT_GENERATED"},
    "V2": {"STATIC_REVIEWED"},
    "V3": {"LOAD_VERIFIED", "NATIVE_OPEN_VERIFIED"},
    "V4": {"BEHAVIOR_VERIFIED"},
    "V5": {"REGRESSION_VERIFIED"},
}


def load_finalization_policy(path: Path) -> dict:
    try:
        policy = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid finalization policy: {exc}") from exc
    if not isinstance(policy, dict) or policy.get("schema_version") != 1:
        raise ValueError("invalid finalization policy schema_version")
    if not isinstance(policy.get("rules"), list):
        raise ValueError("invalid finalization policy rules")
    return policy


def _matching_finalization_rules(session: dict, policy: dict) -> list[dict]:
    artifact = session.get("artifact", {})
    architecture = session.get("architecture", {})
    expected = {
        "artifact_family": artifact.get("family"),
        "artifact_surface": architecture.get("artifact_surface"),
        "delivery_mode": architecture.get("delivery_mode"),
        "claim_class": artifact.get("claim_class"),
    }
    rules = policy.get("rules")
    if not isinstance(rules, list):
        return []
    return [
        rule
        for rule in rules
        if isinstance(rule, dict)
        and all(rule.get(key) == value for key, value in expected.items())
    ]


def _has_required_checks(session: dict, required_checks: object) -> bool:
    if not isinstance(required_checks, list):
        return False
    checks = session.get("validation", {}).get("checks", [])
    if not isinstance(checks, list):
        return False
    for required_id in required_checks:
        if not isinstance(required_id, str):
            return False
        if not any(
            isinstance(check, dict)
            and check.get("id") == required_id
            and check.get("result") == "PASS"
            and isinstance(check.get("evidence_refs"), list)
            and bool(check["evidence_refs"])
            for check in checks
        ):
            return False
    return True


def can_advance_artifact(
    old: str,
    new: str,
    session: dict,
    policy: dict | None = None,
) -> bool:
    if old not in ARTIFACT_STATES or new not in ARTIFACT_STATES:
        return False
    artifact = session.get("artifact", {})
    if artifact.get("state") != old:
        return False
    old_index = ARTIFACT_STATES.index(old)
    new_index = ARTIFACT_STATES.index(new)
    if new_index == old_index:
        return True
    if new_index != old_index + 1:
        return False
    if old == "ARTIFACT_UNBUILT" and new == "CANDIDATE_ARTIFACT":
        return True
    if old != "CANDIDATE_ARTIFACT" or new != "FINAL_ARTIFACT":
        return False
    if not isinstance(policy, dict):
        return False

    rules = _matching_finalization_rules(session, policy)
    if len(rules) != 1:
        return False
    rule = rules[0]
    current_level = artifact.get("verification_level")
    minimum_level = rule.get("minimum_verification_level")
    if (
        current_level not in VERIFICATION_LEVELS
        or minimum_level not in VERIFICATION_LEVELS
        or VERIFICATION_LEVELS.index(current_level)
        < VERIFICATION_LEVELS.index(minimum_level)
    ):
        return False
    return _has_required_checks(session, rule.get("required_checks"))


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
