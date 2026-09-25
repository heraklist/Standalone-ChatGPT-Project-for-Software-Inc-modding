from __future__ import annotations

import argparse
import hashlib
import json
import stat
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from tools.safe_artifacts import safe_source_files
from tools.sim_candidate_identity import hash_tree

FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def _candidate_files(candidate_root: Path) -> dict[str, bytes]:
    root = Path(candidate_root).resolve(strict=True)
    files = {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in safe_source_files(root)
    }
    if "plugin.json" not in files:
        raise ValueError("candidate must contain plugin.json at archive root")
    if "skills/sim/SKILL.md" not in files:
        raise ValueError("candidate must contain skills/sim/SKILL.md")
    return files


def build_plugin_bundle(
    candidate_root: Path,
    output_zip: Path,
    report_out: Path | None = None,
) -> dict:
    candidate_root = Path(candidate_root)
    output_zip = Path(output_zip)
    files = _candidate_files(candidate_root)

    output_zip.parent.mkdir(parents=True, exist_ok=True)
    if output_zip.exists():
        output_zip.unlink()

    with ZipFile(
        output_zip,
        "w",
        compression=ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for relative in sorted(files):
            info = ZipInfo(relative, FIXED_ZIP_TIME)
            info.create_system = 3
            info.compress_type = ZIP_DEFLATED
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(
                info,
                files[relative],
                compress_type=ZIP_DEFLATED,
                compresslevel=9,
            )

    bundle_sha256 = _sha256_bytes(output_zip.read_bytes())
    report = {
        "schema_version": 1,
        "candidate_tree_sha256": hash_tree(candidate_root),
        "bundle_sha256": bundle_sha256,
        "files": {
            path: _sha256_bytes(data)
            for path, data in sorted(files.items())
        },
    }

    if report_out is not None:
        report_path = Path(report_out)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_bytes(_json_bytes(report))
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report-out", type=Path, required=True)
    args = parser.parse_args(argv)

    try:
        report = build_plugin_bundle(
            args.candidate,
            args.output,
            args.report_out,
        )
    except (OSError, ValueError) as exc:
        print(f"SIM_PLUGIN_BUNDLE_BUILD_FAILED: {exc}")
        return 1

    print(f"SIM_PLUGIN_BUNDLE_OK: {report['bundle_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
