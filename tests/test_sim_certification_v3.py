from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "production/sim/manifests/certification-profile.json"


def test_v3_profile_freezes_required_surfaces_and_cases() -> None:
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))

    assert profile["protocol_version"] == "sim-live-v3"
    assert profile["plugin_version"] == "0.2.3-preview"
    assert profile["production_transport"] == "OPENAI_PERSONAL_PLUGIN"

    assert profile["surfaces"]["CHATGPT_WEB_NORMAL_CHAT"]["required_cases"] == [
        f"A{i:02d}" for i in range(1, 13)
    ]
    assert profile["surfaces"]["CHATGPT_DESKTOP_NORMAL_CHAT"]["required_cases"] == [
        "A01", "A03", "A06", "A09", "A10", "A12"
    ]
    assert profile["surfaces"]["CODEX"]["required_cases"] == [
        "A01", "A03", "A09", "A10", "A12"
    ]
    assert profile["surfaces"]["CHATGPT_WORK"]["release_blocking"] is False
    assert profile["surfaces"]["LOCAL_MARKETPLACE"]["release_blocking"] is False


def test_acceptance_context_isolates_transport_and_exact_personal_release() -> None:
    from tools.sim_acceptance import CertificationContext, _matches_context

    context = CertificationContext(
        candidate_tree_sha256="a" * 64,
        semantic_aggregate_sha256="b" * 64,
        source_commit="c" * 40,
        plugin_version="0.2.3-preview",
        exact_target_manifest_sha256="d" * 64,
        protocol_version="sim-live-v3",
        surface="CHATGPT_WEB_NORMAL_CHAT",
        transport="OPENAI_PERSONAL_PLUGIN",
        plugin_id="plugins~Plugin_sim",
        release_id="release_exact",
    )
    record = {
        "candidate_tree_sha256": "a" * 64,
        "semantic_aggregate_sha256": "b" * 64,
        "candidate_source_commit": "c" * 40,
        "plugin_version": "0.2.3-preview",
        "exact_target_manifest_sha256": "d" * 64,
        "certification_protocol_version": "sim-live-v3",
        "surface": "CHATGPT_WEB_NORMAL_CHAT",
        "transport": "OPENAI_PERSONAL_PLUGIN",
        "plugin_id": "plugins~Plugin_sim",
        "release_id": "release_exact",
    }
    assert _matches_context(record, context) is True

    record["surface"] = "CHATGPT_DESKTOP_NORMAL_CHAT"
    assert _matches_context(record, context) is False
    record["surface"] = "CHATGPT_WEB_NORMAL_CHAT"
    record["transport"] = "MARKETPLACE_GIT_SUBDIR"
    assert _matches_context(record, context) is False
    record["transport"] = "OPENAI_PERSONAL_PLUGIN"
    record["release_id"] = "release_other"
    assert _matches_context(record, context) is False
