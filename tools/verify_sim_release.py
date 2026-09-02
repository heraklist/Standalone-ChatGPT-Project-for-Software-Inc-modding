from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import BadZipFile, ZipFile

REQUIRED_ENTRIES = {
    "production/sim/SKILL.md",
    "production/sim/manifests/reference-source-map.json",
}
FORBIDDEN_PREFIXES = ("work/corpus/", "archive/raw/")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def verify_sim_release(zip_path: Path, report_path: Path, expected_version: str) -> list[str]:
    if not zip_path.is_file():
        return [f"SIM release ZIP not found: {zip_path}"]
    if not report_path.is_file():
        return [f"SIM release report not found: {report_path}"]

    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"invalid SIM release report: {exc}"]
    if not isinstance(report, dict):
        return ["SIM release report must be a JSON object"]

    errors: list[str] = []
    if report.get("sim_version") != expected_version:
        errors.append(f"SIM version does not match expected version {expected_version}")
    if report.get("channel") != "PREVIEW":
        errors.append("SIM release channel is not PREVIEW")
    if report.get("target") != "Beta 1.8.42":
        errors.append("SIM release target is not Beta 1.8.42")
    if report.get("evidence_grade") != "GENERATION_GRADE":
        errors.append("SIM release evidence grade is not GENERATION_GRADE")
    if report.get("release_status") not in {"PREVIEW_CANDIDATE", "PREVIEW_ACCEPTED"}:
        errors.append("SIM release status is not a Preview state")

    if report.get("bundle_sha256") != _sha256_file(zip_path):
        errors.append("bundle SHA-256 mismatch")

    reported_files = report.get("files")
    if not isinstance(reported_files, dict):
        errors.append("release report files must be an object")
        reported_files = {}

    try:
        with ZipFile(zip_path) as archive:
            bad_member = archive.testzip()
            if bad_member:
                errors.append(f"corrupt ZIP member: {bad_member}")
                return errors

            names = archive.namelist()
            name_set = set(names)
            if len(names) != len(name_set):
                errors.append("duplicate ZIP entries are not allowed")

            for required in sorted(REQUIRED_ENTRIES - name_set):
                errors.append(f"missing required SIM bundle entry: {required}")

            for name in sorted(name_set):
                if not name.startswith("production/sim/") or name.startswith(FORBIDDEN_PREFIXES):
                    errors.append(f"forbidden bundle path: {name}")

            if set(reported_files) != name_set:
                errors.append("reported file set does not match ZIP entries")

            for name, expected_hash in sorted(reported_files.items()):
                if name not in name_set:
                    continue
                actual_hash = _sha256_bytes(archive.read(name))
                if expected_hash != actual_hash:
                    errors.append(f"file SHA-256 mismatch: {name}")

            map_name = "production/sim/manifests/reference-source-map.json"
            if map_name in name_set:
                map_bytes = archive.read(map_name)
                if report.get("reference_map_sha256") != _sha256_bytes(map_bytes):
                    errors.append("reference map SHA-256 mismatch")
                try:
                    reference_map = json.loads(map_bytes)
                except json.JSONDecodeError as exc:
                    errors.append(f"invalid packed reference map: {exc}")
                else:
                    entries = reference_map.get("entries") if isinstance(reference_map, dict) else None
                    if not isinstance(entries, list):
                        errors.append("packed reference map entries must be an array")
                    else:
                        for entry in entries:
                            if not isinstance(entry, dict):
                                errors.append("packed reference entry must be an object")
                                continue
                            output_path = entry.get("output_path")
                            output_hash = entry.get("output_sha256")
                            if not isinstance(output_path, str) or output_path not in name_set:
                                errors.append(f"mapped reference output missing: {output_path}")
                                continue
                            if output_hash != _sha256_bytes(archive.read(output_path)):
                                errors.append(f"mapped reference SHA-256 mismatch: {output_path}")
    except (BadZipFile, OSError) as exc:
        errors.append(f"invalid SIM release ZIP: {exc}")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("zip_path", type=Path)
    parser.add_argument("report_path", type=Path)
    parser.add_argument("--expected-version", required=True)
    args = parser.parse_args(argv)
    errors = verify_sim_release(args.zip_path, args.report_path, args.expected_version)
    if errors:
        for error in errors:
            print(f"SIM_RELEASE_ERROR: {error}")
        return 1
    print(f"SIM_RELEASE_OK: {args.zip_path}")
    print(f"SHA256: {_sha256_file(args.zip_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
