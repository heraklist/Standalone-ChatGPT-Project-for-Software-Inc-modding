from __future__ import annotations

import argparse
import hashlib
import json
import stat
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from tools.safe_artifacts import safe_source_files, validate_archive_names
from tools.sim_candidate_identity import hash_tree

FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _candidate_files(candidate_root: Path) -> dict[str, bytes]:
    root = Path(candidate_root).resolve(strict=True)
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in safe_source_files(root)
    }


def verify_plugin_bundle(
    candidate_root: Path,
    zip_path: Path,
    report_path: Path,
) -> list[str]:
    errors: list[str] = []
    candidate_root = Path(candidate_root)
    zip_path = Path(zip_path)
    report_path = Path(report_path)

    try:
        candidate = _candidate_files(candidate_root)
    except (OSError, ValueError) as exc:
        return [f"candidate invalid: {exc}"]

    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"bundle report invalid: {exc}"]

    try:
        with ZipFile(zip_path) as archive:
            infos = archive.infolist()
            names = [info.filename for info in infos]
            try:
                normalized = validate_archive_names(
                    names,
                    windows_casefold=True,
                )
            except ValueError as exc:
                errors.append(str(exc))
                normalized = []

            if names != sorted(names):
                errors.append("bundle members are not deterministically sorted")
            if "plugin.json" not in names:
                errors.append("bundle is missing root plugin.json")
            if "skills/sim/SKILL.md" not in names:
                errors.append("bundle is missing skills/sim/SKILL.md")
            if set(normalized) != set(candidate):
                errors.append("bundle path set differs from candidate")

            archive_files: dict[str, bytes] = {}
            for info in infos:
                if info.is_dir():
                    errors.append(f"bundle contains directory member: {info.filename}")
                    continue
                if info.date_time != FIXED_ZIP_TIME:
                    errors.append(f"bundle timestamp drift: {info.filename}")
                mode = info.external_attr >> 16
                if mode and (
                    not stat.S_ISREG(mode) or (mode & 0o777) != 0o644
                ):
                    errors.append(f"bundle mode drift: {info.filename}")
                if info.filename not in archive_files:
                    archive_files[info.filename] = archive.read(info)

            for relative, data in candidate.items():
                if archive_files.get(relative) != data:
                    errors.append(f"bundle byte drift: {relative}")
    except (OSError, BadZipFile) as exc:
        return [f"bundle archive invalid: {exc}"]

    candidate_hash = hash_tree(candidate_root)
    bundle_hash = _sha256_bytes(zip_path.read_bytes())
    file_hashes = {
        path: _sha256_bytes(data)
        for path, data in sorted(candidate.items())
    }

    if report.get("schema_version") != 1:
        errors.append("bundle report schema version invalid")
    if report.get("candidate_tree_sha256") != candidate_hash:
        errors.append("bundle report candidate tree mismatch")
    if report.get("bundle_sha256") != bundle_hash:
        errors.append("bundle report SHA-256 mismatch")
    if report.get("files") != file_hashes:
        errors.append("bundle report file hashes mismatch")

    return sorted(set(errors))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--zip", dest="zip_path", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args(argv)

    errors = verify_plugin_bundle(
        args.candidate,
        args.zip_path,
        args.report,
    )
    if errors:
        for error in errors:
            print(error)
        return 1
    print("SIM_PLUGIN_BUNDLE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
