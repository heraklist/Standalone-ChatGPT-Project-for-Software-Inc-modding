from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from zipfile import BadZipFile, ZipFile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.sim_acceptance import summarize_acceptance

REQUIRED_ENTRIES = {
    "production/sim/SKILL.md",
    "production/sim/manifests/reference-source-map.json",
}
FORBIDDEN_PREFIXES = ("work/corpus/", "archive/raw/")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def verify_sim_release(
    zip_path: Path,
    report_path: Path,
    expected_version: str,
    *,
    certification_context=None,
    evidence_dir: Path | None = None,
    required_cases: tuple[str, ...] | None = None,
    candidate_root: Path | None = None,
    source_sha: str | None = None,
    evidence_root: Path | None = None,
) -> list[str]:
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
    if report.get("release_status") not in {
        "PREVIEW_BUILD",
        "PREVIEW_VALIDATED",
        "PREVIEW_LIVE_INCOMPLETE",
        "PREVIEW_LIVE_FAILED",
        "PREVIEW_CERTIFIED",
    }:
        errors.append("SIM release status is not a Preview state")

    release_status = report.get("release_status")
    live_states = {
        "PREVIEW_LIVE_INCOMPLETE",
        "PREVIEW_LIVE_FAILED",
        "PREVIEW_CERTIFIED",
    }
    if release_status in {"PREVIEW_BUILD", "PREVIEW_VALIDATED"}:
        if report.get("surface_acceptance") != "NOT_EVALUATED":
            errors.append(
                f"{release_status} requires surface_acceptance NOT_EVALUATED"
            )
        if report.get("known_gaps") != []:
            errors.append(f"{release_status} requires empty known_gaps")
    elif release_status in live_states:
        global_inputs = (candidate_root, source_sha, evidence_root)
        if any(value is not None for value in global_inputs):
            if not all(value is not None for value in global_inputs):
                errors.append(
                    f"{release_status} requires candidate_root, source_sha, and evidence_root together"
                )
            else:
                from tools.verify_sim_certification import (
                    build_certification_report,
                    verify_certification,
                )

                assert candidate_root is not None
                assert source_sha is not None
                assert evidence_root is not None
                certification_errors = verify_certification(
                    ROOT,
                    candidate_root,
                    source_sha,
                    evidence_root,
                )
                derived = build_certification_report(
                    ROOT,
                    candidate_root,
                    source_sha,
                    evidence_root,
                )
                errors.extend(
                    f"global certification: {error}"
                    for error in certification_errors
                )
                if (
                    derived.get("certification_protocol_version") == "sim-live-v3"
                    and release_status in live_states
                ):
                    errors.append(
                        "source release cannot inherit personal plugin certification"
                    )
                    expected_state = "PREVIEW_VALIDATED"
                    expected_acceptance = "NOT_EVALUATED"
                elif derived["release_blocking_complete"]:
                    expected_state = "PREVIEW_CERTIFIED"
                    expected_acceptance = "PASS"
                elif any(
                    value == "FAIL"
                    for value in derived["surface_results"].values()
                ):
                    expected_state = "PREVIEW_LIVE_FAILED"
                    expected_acceptance = "FAIL"
                else:
                    expected_state = "PREVIEW_LIVE_INCOMPLETE"
                    expected_acceptance = "INCOMPLETE"
                if release_status != expected_state:
                    errors.append(
                        f"{release_status} does not match global certification; expected {expected_state}"
                    )
                if report.get("surface_acceptance") != expected_acceptance:
                    errors.append(
                        "surface_acceptance does not match global certification"
                    )
                if report.get("known_gaps") != list(derived["known_gaps"]):
                    errors.append(
                        "known_gaps do not match global certification"
                    )
        elif certification_context is None or evidence_dir is None:
            errors.append(
                f"{release_status} requires certification context and acceptance evidence"
            )
        else:
            expected_source_revision = (
                "exact-target-manifest-sha256:"
                + certification_context.exact_target_manifest_sha256
            )
            if report.get("canonical_source_revision") != expected_source_revision:
                errors.append(
                    "exact-target certification context does not match release report"
                )
            cases = required_cases or tuple(
                f"A{index:02d}" for index in range(1, 13)
            )
            try:
                summary = summarize_acceptance(
                    evidence_dir, certification_context, cases
                )
            except ValueError as exc:
                errors.append(f"invalid acceptance evidence: {exc}")
            else:
                expected_state = {
                    "PASS": "PREVIEW_CERTIFIED",
                    "FAIL": "PREVIEW_LIVE_FAILED",
                    "INCOMPLETE": "PREVIEW_LIVE_INCOMPLETE",
                }[summary.status]
                if release_status != expected_state:
                    errors.append(
                        f"{release_status} does not match acceptance state "
                        f"{summary.status}; expected {expected_state}"
                    )
                if report.get("surface_acceptance") != summary.status:
                    errors.append(
                        "surface_acceptance does not match independently "
                        "recomputed acceptance state"
                    )
                if report.get("known_gaps") != list(summary.known_gaps):
                    errors.append(
                        "known_gaps do not match independently recomputed "
                        "acceptance gaps"
                    )

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
    parser.add_argument("--candidate-root", type=Path)
    parser.add_argument("--source-sha")
    parser.add_argument("--evidence-root", type=Path)
    args = parser.parse_args(argv)
    errors = verify_sim_release(
        args.zip_path,
        args.report_path,
        args.expected_version,
        candidate_root=args.candidate_root,
        source_sha=args.source_sha,
        evidence_root=args.evidence_root,
    )
    if errors:
        for error in errors:
            print(f"SIM_RELEASE_ERROR: {error}")
        return 1
    print(f"SIM_RELEASE_OK: {args.zip_path}")
    print(f"SHA256: {_sha256_file(args.zip_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
