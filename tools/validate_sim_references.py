from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.build_sim_references import ROOT, sha256_file


def validate_references(root: Path) -> list[str]:
    errors: list[str] = []
    manifest_path = root / "production/sim/manifests/reference-source-map.json"
    if not manifest_path.is_file():
        return ["missing SIM reference source map"]

    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return ["SIM reference source map is unreadable or invalid JSON"]

    entries = data.get("entries") if isinstance(data, dict) else None
    if not isinstance(entries, list):
        return ["SIM reference source map entries must be an array"]

    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("SIM reference entry must be an object")
            continue

        output_relative = entry.get("output_path")
        source_relatives = entry.get("canonical_source_paths")
        source_hashes = entry.get("source_sha256")
        output_hash = entry.get("output_sha256")

        if not isinstance(output_relative, str):
            errors.append("SIM reference entry missing output_path")
            continue
        if not isinstance(source_relatives, list) or not all(
            isinstance(value, str) for value in source_relatives
        ):
            errors.append(f"invalid canonical_source_paths for {output_relative}")
            continue
        if not isinstance(source_hashes, dict):
            errors.append(f"invalid source_sha256 map for {output_relative}")
            continue

        if set(source_hashes) != set(source_relatives):
            errors.append(f"source hash key mismatch for {output_relative}")

        for source_relative in source_relatives:
            source_path = root / source_relative
            if not source_path.is_file():
                errors.append(f"missing canonical source: {source_relative}")
                continue
            expected = source_hashes.get(source_relative)
            if expected != sha256_file(source_path):
                errors.append(f"source hash mismatch: {source_relative}")

        output_path = root / output_relative
        if not output_path.is_file():
            errors.append(f"missing reference output: {output_relative}")
        elif output_hash != sha256_file(output_path):
            errors.append(f"output hash mismatch: {output_relative}")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    errors = validate_references(args.root)
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
