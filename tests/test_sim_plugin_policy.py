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
