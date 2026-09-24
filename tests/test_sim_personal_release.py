from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema

from tools.sim_candidate_identity import hash_tree

ROOT = Path(__file__).resolve().parents[1]
INSTALL_SCHEMA = ROOT / "schemas/sim-installation-evidence.schema.json"
RELEASE_SCHEMA = ROOT / "schemas/sim-personal-plugin-release-evidence.schema.json"


def _file_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(path for path in root.rglob("*") if path.is_file())
    }


def test_installation_schema_accepts_personal_transport_without_marketplace_fields() -> None:
    schema = json.loads(INSTALL_SCHEMA.read_text(encoding="utf-8"))
    record = {
        "schema_version": 2,
        "installation_evidence_id": "web-personal-install",
        "surface": "CHATGPT_WEB_NORMAL_CHAT",
        "result": "PASS",
        "candidate_tree_sha256": "a" * 64,
        "semantic_aggregate_sha256": "b" * 64,
        "source_commit": "c" * 40,
        "plugin_version": "0.2.3-preview",
        "exact_target_manifest_sha256": "d" * 64,
        "certification_protocol_version": "sim-live-v3",
        "transport": "OPENAI_PERSONAL_PLUGIN",
        "plugin_id": "plugins~Plugin_example",
        "release_id": "release_example",
        "current_release_id": "release_example",
        "latest_release_id": "release_example",
        "scope": "USER",
        "discoverability": "PRIVATE",
        "bundle_sha256": "e" * 64,
        "platform_release_tree_sha256": "a" * 64,
        "observed_public_skill_count": 1,
        "observed_public_skill_names": ["SIM"],
        "recorded_at": "2026-09-24T07:00:00Z"
    }
    jsonschema.Draft202012Validator(schema).validate(record)


def test_installation_schema_requires_marketplace_chain_for_marketplace_transport() -> None:
    schema = json.loads(INSTALL_SCHEMA.read_text(encoding="utf-8"))
    record = {
        "schema_version": 2,
        "installation_evidence_id": "local-marketplace-install",
        "surface": "LOCAL_MARKETPLACE",
        "result": "PASS",
        "candidate_tree_sha256": "a" * 64,
        "semantic_aggregate_sha256": "b" * 64,
        "source_commit": "c" * 40,
        "plugin_version": "0.2.3-preview",
        "exact_target_manifest_sha256": "d" * 64,
        "certification_protocol_version": "sim-live-v3",
        "transport": "MARKETPLACE_GIT_SUBDIR",
        "observed_public_skill_count": 1,
        "observed_public_skill_names": ["SIM"],
        "recorded_at": "2026-09-24T07:00:00Z"
    }
    errors = list(jsonschema.Draft202012Validator(schema).iter_errors(record))
    assert errors


def test_personal_release_verifier_binds_exact_current_release_to_candidate(
    tmp_path: Path,
) -> None:
    from tools.verify_sim_personal_release import verify_personal_release

    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "plugin.json").write_text('{"name":"sim"}\n', encoding="utf-8")
    skill = candidate / "skills/sim/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("---\nname: sim\n---\n", encoding="utf-8")

    tree = hash_tree(candidate)
    evidence = {
        "schema_version": 1,
        "plugin_id": "plugins~Plugin_example",
        "release_id": "release_exact",
        "current_release_id": "release_exact",
        "latest_release_id": "release_exact",
        "scope": "USER",
        "discoverability": "PRIVATE",
        "candidate_tree_sha256": tree,
        "bundle_sha256": "e" * 64,
        "platform_release_tree_sha256": tree,
        "files": _file_hashes(candidate),
        "recorded_at": "2026-09-24T07:00:00Z"
    }
    assert verify_personal_release(candidate, evidence) == []

    evidence["current_release_id"] = "release_other"
    assert "PERSONAL_RELEASE_NOT_CURRENT" in verify_personal_release(candidate, evidence)


def test_personal_plugin_overlay_update_rejects_required_path_deletion() -> None:
    from tools.verify_sim_personal_release import update_is_overlay_safe

    assert update_is_overlay_safe({"plugin.json", "old.txt"}, {"plugin.json"}) is False
    assert update_is_overlay_safe({"plugin.json"}, {"plugin.json", "new.txt"}) is True


def test_personal_release_accepts_only_verified_openai_compatibility_normalization(
    tmp_path: Path,
) -> None:
    from tools.sim_candidate_identity import aggregate_file_hashes
    from tools.verify_sim_personal_release import verify_personal_release

    candidate = tmp_path / "candidate"
    candidate.mkdir()
    root_manifest = candidate / "plugin.json"
    root_manifest.write_text(
        json.dumps(
            {
                "name": "sim",
                "version": "0.2.3-preview",
                "extensions": {
                    "com.openai": {
                        "interface": {
                            "displayName": "SIM",
                            "shortDescription": "Software Inc modding.",
                        }
                    }
                },
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    compat = candidate / ".codex-plugin/plugin.json"
    compat.parent.mkdir(parents=True)
    compat.write_text(
        json.dumps(
            {
                "name": "sim",
                "version": "0.2.3-preview",
                "skills": "./skills/",
                "interface": {
                    "displayName": "SIM",
                    "shortDescription": "Software Inc modding.",
                },
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    skill = candidate / "skills/sim/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("---\nname: sim\n---\n", encoding="utf-8")

    candidate_files = _file_hashes(candidate)
    platform_compat = json.dumps(
        {
            "name": "sim",
            "version": "0.2.3-preview",
            "skills": "./skills",
            "interface": {
                "displayName": "SIM",
                "shortDescription": "Software Inc modding.",
            },
            "description": "SIM compatibility manifest",
            "author": {"name": "Workspace upload"},
            "keywords": [],
        },
        sort_keys=True,
    ) + "\n"
    platform_files = dict(candidate_files)
    platform_files[".codex-plugin/plugin.json"] = hashlib.sha256(
        platform_compat.encode("utf-8")
    ).hexdigest()

    tree = hash_tree(candidate)
    evidence = {
        "schema_version": 2,
        "plugin_id": "plugins~Plugin_example",
        "release_id": "release_exact",
        "current_release_id": "release_exact",
        "latest_release_id": "release_exact",
        "scope": "USER",
        "discoverability": "PRIVATE",
        "candidate_tree_sha256": tree,
        "bundle_sha256": "e" * 64,
        "platform_release_tree_sha256": aggregate_file_hashes(platform_files),
        "normalized_platform_tree_sha256": tree,
        "files": platform_files,
        "platform_normalizations": [
            {
                "path": ".codex-plugin/plugin.json",
                "normalization_class": "OPENAI_COMPATIBILITY_MANIFEST",
                "candidate_sha256": candidate_files[".codex-plugin/plugin.json"],
                "platform_sha256": platform_files[".codex-plugin/plugin.json"],
                "platform_content": platform_compat,
            }
        ],
        "recorded_at": "2026-09-24T10:00:00Z",
    }

    assert verify_personal_release(candidate, evidence) == []

    evidence["platform_normalizations"][0]["path"] = "plugin.json"
    assert "PERSONAL_RELEASE_NORMALIZATION_PATH_INVALID" in verify_personal_release(
        candidate, evidence
    )
