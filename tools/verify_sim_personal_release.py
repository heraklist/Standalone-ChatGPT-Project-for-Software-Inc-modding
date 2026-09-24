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


def _candidate_hashes(candidate_root: Path) -> dict[str, str]:
    root = Path(candidate_root).resolve(strict=True)
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in safe_source_files(root)
    }


def update_is_overlay_safe(current_paths: set[str], desired_paths: set[str]) -> bool:
    return set(current_paths).issubset(set(desired_paths))


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
        actual_files = _candidate_hashes(candidate_root)
        candidate_tree = hash_tree(candidate_root)
    except (OSError, ValueError) as exc:
        return [f"PERSONAL_RELEASE_CANDIDATE_INVALID: {exc}"]

    if evidence["files"] != actual_files:
        errors.append("PERSONAL_RELEASE_FILE_HASH_DRIFT")
    if evidence["candidate_tree_sha256"] != candidate_tree:
        errors.append("PERSONAL_RELEASE_CANDIDATE_TREE_MISMATCH")

    platform_tree = aggregate_file_hashes(evidence["files"])
    if evidence["platform_release_tree_sha256"] != platform_tree:
        errors.append("PERSONAL_RELEASE_PLATFORM_TREE_INVALID")
    if evidence["platform_release_tree_sha256"] != candidate_tree:
        errors.append("PERSONAL_RELEASE_PLATFORM_TREE_MISMATCH")

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
