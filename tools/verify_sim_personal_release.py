from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.safe_artifacts import safe_source_files
from tools.sim_candidate_identity import aggregate_file_hashes, hash_tree

SCHEMA = ROOT / "schemas/sim-personal-plugin-release-evidence.schema.json"
_COMPAT_PATH = ".codex-plugin/plugin.json"
_COMPAT_CLASS = "OPENAI_COMPATIBILITY_MANIFEST"


def _candidate_hashes(candidate_root: Path) -> dict[str, str]:
    root = Path(candidate_root).resolve(strict=True)
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in safe_source_files(root)
    }


def _read_candidate_json(candidate_root: Path, relative: str) -> dict:
    path = Path(candidate_root) / relative
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{relative} must contain a JSON object")
    return value


def _compatibility_semantics_match(candidate: dict, platform: dict) -> bool:
    required_equal = ("name", "version", "interface")
    if any(platform.get(key) != candidate.get(key) for key in required_equal):
        return False

    candidate_skills = candidate.get("skills")
    platform_skills = platform.get("skills")
    if not isinstance(candidate_skills, str) or not isinstance(platform_skills, str):
        return False
    if candidate_skills.rstrip("/") != platform_skills.rstrip("/"):
        return False

    if "description" in candidate and platform.get("description") != candidate["description"]:
        return False

    candidate_keys = set(candidate)
    platform_keys = set(platform)
    allowed_added = {"author", "keywords", "description"}
    if not platform_keys.issubset(candidate_keys | allowed_added):
        return False
    if not candidate_keys.issubset(platform_keys):
        return False
    return True


def update_is_overlay_safe(current_paths: set[str], desired_paths: set[str]) -> bool:
    return set(current_paths).issubset(set(desired_paths))


def _verify_v2_normalizations(
    candidate_root: Path,
    candidate_files: dict[str, str],
    evidence: dict,
) -> list[str]:
    errors: list[str] = []
    platform_files = evidence["files"]

    if set(platform_files) != set(candidate_files):
        errors.append("PERSONAL_RELEASE_PATH_SET_DRIFT")

    normalizations = evidence.get("platform_normalizations", [])
    normalized_files = dict(platform_files)
    declared_paths: set[str] = set()

    for record in normalizations:
        path = record["path"]
        if path != _COMPAT_PATH:
            errors.append("PERSONAL_RELEASE_NORMALIZATION_PATH_INVALID")
            continue
        if path in declared_paths:
            errors.append("PERSONAL_RELEASE_NORMALIZATION_DUPLICATE")
            continue
        declared_paths.add(path)

        if record["normalization_class"] != _COMPAT_CLASS:
            errors.append("PERSONAL_RELEASE_NORMALIZATION_CLASS_INVALID")
            continue
        if candidate_files.get(path) != record["candidate_sha256"]:
            errors.append("PERSONAL_RELEASE_NORMALIZATION_CANDIDATE_HASH_MISMATCH")
            continue
        if platform_files.get(path) != record["platform_sha256"]:
            errors.append("PERSONAL_RELEASE_NORMALIZATION_PLATFORM_HASH_MISMATCH")
            continue
        content_hash = hashlib.sha256(
            record["platform_content"].encode("utf-8")
        ).hexdigest()
        if content_hash != record["platform_sha256"]:
            errors.append("PERSONAL_RELEASE_NORMALIZATION_CONTENT_HASH_MISMATCH")
            continue

        try:
            candidate_manifest = _read_candidate_json(candidate_root, path)
            platform_manifest = json.loads(record["platform_content"])
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
            errors.append("PERSONAL_RELEASE_NORMALIZATION_CONTENT_INVALID")
            continue
        if not isinstance(platform_manifest, dict):
            errors.append("PERSONAL_RELEASE_NORMALIZATION_CONTENT_INVALID")
            continue
        if not _compatibility_semantics_match(candidate_manifest, platform_manifest):
            errors.append("PERSONAL_RELEASE_NORMALIZATION_SEMANTICS_MISMATCH")
            continue

        normalized_files[path] = record["candidate_sha256"]

    mismatched_paths = {
        path
        for path in set(candidate_files) & set(platform_files)
        if candidate_files[path] != platform_files[path]
    }
    if mismatched_paths != declared_paths:
        errors.append("PERSONAL_RELEASE_FILE_HASH_DRIFT")

    normalized_tree = aggregate_file_hashes(normalized_files)
    if evidence["normalized_platform_tree_sha256"] != normalized_tree:
        errors.append("PERSONAL_RELEASE_NORMALIZED_TREE_INVALID")
    if normalized_tree != evidence["candidate_tree_sha256"]:
        errors.append("PERSONAL_RELEASE_NORMALIZED_TREE_MISMATCH")

    return errors


def verify_personal_release(
    candidate_root: Path,
    evidence: dict,
    schema_path: Path = SCHEMA,
) -> list[str]:
    errors: list[str] = []
    try:
        schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(evidence)
    except (OSError, UnicodeError, json.JSONDecodeError, jsonschema.ValidationError) as exc:
        return [f"PERSONAL_RELEASE_EVIDENCE_INVALID: {exc}"]

    if evidence["scope"] != "USER":
        errors.append("PERSONAL_RELEASE_SCOPE_INVALID")
    if evidence["discoverability"] != "PRIVATE":
        errors.append("PERSONAL_RELEASE_DISCOVERABILITY_INVALID")
    if evidence["current_release_id"] != evidence["release_id"]:
        errors.append("PERSONAL_RELEASE_NOT_CURRENT")

    try:
        candidate_files = _candidate_hashes(candidate_root)
        candidate_tree = hash_tree(candidate_root)
    except (OSError, ValueError) as exc:
        return [f"PERSONAL_RELEASE_CANDIDATE_INVALID: {exc}"]

    if evidence["candidate_tree_sha256"] != candidate_tree:
        errors.append("PERSONAL_RELEASE_CANDIDATE_TREE_MISMATCH")

    platform_tree = aggregate_file_hashes(evidence["files"])
    if evidence["platform_release_tree_sha256"] != platform_tree:
        errors.append("PERSONAL_RELEASE_PLATFORM_TREE_INVALID")

    if evidence["schema_version"] == 1:
        if evidence["files"] != candidate_files:
            errors.append("PERSONAL_RELEASE_FILE_HASH_DRIFT")
        if evidence["platform_release_tree_sha256"] != candidate_tree:
            errors.append("PERSONAL_RELEASE_PLATFORM_TREE_MISMATCH")
    else:
        errors.extend(
            _verify_v2_normalizations(candidate_root, candidate_files, evidence)
        )

    return sorted(set(errors))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args(argv)

    try:
        evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"PERSONAL_RELEASE_EVIDENCE_INVALID: {exc}")
        return 1

    errors = verify_personal_release(args.candidate, evidence)
    if errors:
        for error in errors:
            print(error)
        return 1
    print("SIM_PERSONAL_RELEASE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
