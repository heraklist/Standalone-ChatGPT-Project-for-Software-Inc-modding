from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import BadZipFile, ZipFile


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_release_artifacts(zip_path: Path, report_path: Path, *, expected_version: str) -> list[str]:
    errors: list[str] = []

    if not zip_path.is_file():
        return [f"release ZIP not found: {zip_path}"]
    if not report_path.is_file():
        return [f"release report not found: {report_path}"]

    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"invalid release report: {exc}"]

    if report.get("release_status") != "GENERATION_GRADE":
        errors.append("release status is not GENERATION_GRADE")
    if report.get("generation_grade") is not True:
        errors.append("release report generation_grade is not true")
    if report.get("exact_target_gate_errors") != []:
        errors.append("release report contains exact-target gate errors")

    actual_digest = _sha256(zip_path)
    if report.get("bundle_sha256") != actual_digest:
        errors.append("bundle SHA-256 mismatch")

    try:
        with ZipFile(zip_path) as zf:
            bad_member = zf.testzip()
            if bad_member:
                errors.append(f"corrupt ZIP member: {bad_member}")
                return errors

            names = set(zf.namelist())
            if len(names) != 21:
                errors.append(f"bundle must contain exactly 21 entries, found {len(names)}")

            required_fixed = {
                "project-instructions/PROJECT_INSTRUCTIONS.md",
                "manifests/knowledge-pack-manifest.json",
                "manifests/release-manifest.json",
            }
            missing_fixed = sorted(required_fixed - names)
            if missing_fixed:
                errors.append("missing required bundle entries: " + ", ".join(missing_fixed))

            knowledge_entries = sorted(name for name in names if name.startswith("knowledge/"))
            if len(knowledge_entries) != 18:
                errors.append(f"bundle must contain exactly 18 knowledge files, found {len(knowledge_entries)}")

            if "manifests/knowledge-pack-manifest.json" in names:
                kp = json.loads(zf.read("manifests/knowledge-pack-manifest.json"))
                if kp.get("pack_version") != expected_version:
                    errors.append(f"knowledge-pack version does not match expected version {expected_version}")
                if kp.get("exact_target_generation_grade") is not True:
                    errors.append("packed knowledge manifest is not exact-target generation-grade")
                mandatory = kp.get("mandatory_knowledge_files")
                if not isinstance(mandatory, list) or len(mandatory) != 18:
                    errors.append("packed knowledge manifest must enumerate exactly 18 knowledge files")
                elif {f"knowledge/{name}" for name in mandatory} != set(knowledge_entries):
                    errors.append("packed knowledge manifest does not match ZIP knowledge entries")
    except (BadZipFile, KeyError, json.JSONDecodeError) as exc:
        errors.append(f"invalid release ZIP metadata: {exc}")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("zip_path", type=Path)
    parser.add_argument("report_path", type=Path)
    parser.add_argument("--expected-version", required=True)
    args = parser.parse_args(argv)

    errors = verify_release_artifacts(
        args.zip_path,
        args.report_path,
        expected_version=args.expected_version,
    )
    if errors:
        for error in errors:
            print(f"RELEASE_ARTIFACT_ERROR: {error}")
        return 1

    print(f"RELEASE_ARTIFACT_OK: {args.zip_path}")
    print(f"SHA256: {_sha256(args.zip_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
