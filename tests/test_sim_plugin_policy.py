from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _runtime() -> dict:
    return json.loads(
        (ROOT / "production/sim/RUNTIME.json").read_text(encoding="utf-8")
    )


def test_runtime_manifest_freezes_one_public_sim_skill() -> None:
    runtime = _runtime()
    assert runtime["schema_version"] == 1
    assert runtime["plugin_identity"] == "sim"
    assert runtime["public_entrypoint"] == "@sim"
    assert runtime["display_invocation"] == "@Sim"
    assert runtime["runtime_skill"] == "sim"
    assert runtime["public_skill_count"] == 1
    assert runtime["canonical_game_target"] == "Beta 1.8.42"
    assert runtime["domain_count"] == len(runtime["domain_ids"]) == 8
    assert runtime["lifecycle_count"] == len(runtime["lifecycle_ids"]) == 5


def test_runtime_manifest_matches_actual_domain_and_lifecycle_ids() -> None:
    runtime = _runtime()
    sim_root = ROOT / "production/sim"
    actual_domains = sorted(
        path.name
        for path in (sim_root / "domains").iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    )
    actual_lifecycle = sorted(
        path.name
        for path in (sim_root / "lifecycle").iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    )
    assert runtime["domain_ids"] == actual_domains
    assert runtime["lifecycle_ids"] == actual_lifecycle


def test_projection_policy_preserves_single_source_authority() -> None:
    policy = json.loads(
        (
            ROOT
            / "docs/architecture/plugin/SIM-PLUGIN-PROJECTION-POLICY.json"
        ).read_text(encoding="utf-8")
    )
    assert policy["schema_version"] == 1
    assert policy["plugin_identity"] == "sim"
    assert policy["runtime_source_path"] == "production/sim"
    assert policy["projection_target_path"] == "skills/sim"
    assert policy["public_skill_count"] == 1
    assert policy["root_skill_relation"] == "EXACT_BYTE_COPY"
    assert policy["internal_skill_relation"] == "REMAP_EXACT_BYTE_COPY"
    assert policy["internal_skill_targets"] == {
        "domains": "references/internal/domains/{id}.md",
        "lifecycle": "references/internal/lifecycle/{id}.md",
    }
    assert "domain_ids" not in policy
    assert "lifecycle_ids" not in policy


def test_projection_policy_declares_closed_world_generated_paths_and_exclusions() -> None:
    policy = json.loads(
        (
            ROOT
            / "docs/architecture/plugin/SIM-PLUGIN-PROJECTION-POLICY.json"
        ).read_text(encoding="utf-8")
    )
    assert policy["portable_manifest_path"] == "plugin.json"
    assert policy["compatibility_manifest_path"] == ".codex-plugin/plugin.json"
    assert set(policy["projection_relations"]) == {
        "EXACT_BYTE_COPY",
        "REMAP_EXACT_BYTE_COPY",
        "GENERATED_METADATA",
        "GENERATED_PROVENANCE",
    }
    assert "provenance/plugin_manifest.json" in policy["semantic_aggregate_exclusions"]
    assert policy["tool_capabilities_source"] == "production/sim/manifests/tool-capabilities.json"
