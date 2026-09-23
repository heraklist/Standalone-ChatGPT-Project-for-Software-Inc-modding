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

from tools.sim_acceptance import (
    CertificationContext,
    load_acceptance_records,
    summarize_acceptance,
)
from tools.sim_candidate_identity import hash_tree
from tools.sim_git_source import GitSource
from tools.validate_sim_plugin import validate_candidate

POLICY_PATH = "docs/architecture/plugin/SIM-PLUGIN-PROJECTION-POLICY.json"


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def _candidate_identity(
    repo_root: Path,
    candidate_root: Path,
    source_sha: str,
) -> tuple[dict, list[str]]:
    errors: list[str] = []
    try:
        source = GitSource(repo_root, source_sha)
        full_source = source.full_commit()
    except ValueError as exc:
        return {
            "candidate_tree_sha256": "0" * 64,
            "semantic_aggregate_sha256": "0" * 64,
            "source_commit": "0" * 40,
            "plugin_version": "0.2.2-preview",
        }, [f"source commit invalid: {exc}"]

    findings = validate_candidate(repo_root, candidate_root, full_source)
    for finding in findings:
        location = f" ({finding.path})" if finding.path else ""
        errors.append(f"{finding.code}{location}: {finding.message}")

    try:
        policy = json.loads(source.read_bytes(POLICY_PATH).decode("utf-8"))
        manifest_path = policy["plugin_provenance_path"]
        manifest = _load_json(candidate_root / manifest_path)
        portable = _load_json(candidate_root / policy["portable_manifest_path"])
        candidate_hash = hash_tree(candidate_root)
        semantic = manifest["semantic_aggregate_sha256"]
        plugin_version = portable["version"]
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, ValueError) as exc:
        errors.append(f"candidate identity unreadable: {exc}")
        candidate_hash = "0" * 64
        semantic = "0" * 64
        plugin_version = "0.2.2-preview"

    return {
        "candidate_tree_sha256": candidate_hash,
        "semantic_aggregate_sha256": semantic,
        "source_commit": full_source,
        "plugin_version": plugin_version,
    }, errors


def _installation_records(evidence_root: Path) -> tuple[list[dict], list[str]]:
    records: list[dict] = []
    errors: list[str] = []
    directory = evidence_root / "sim-certification"
    if not directory.is_dir():
        return records, errors

    schema = _load_json(ROOT / "schemas/sim-installation-evidence.schema.json")
    validator = jsonschema.Draft202012Validator(schema)
    for path in sorted(directory.rglob("*.json")):
        try:
            value = _load_json(path)
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"invalid certification evidence {path.name}: {exc}")
            continue
        if "installation_evidence_id" not in value:
            continue
        schema_errors = sorted(
            validator.iter_errors(value),
            key=lambda error: tuple(str(part) for part in error.absolute_path),
        )
        if schema_errors:
            errors.append(
                f"installation evidence schema violation in {path.name}: "
                + schema_errors[0].message
            )
            continue
        records.append(value)
    return records, errors


def _same_context(record: dict, context: CertificationContext) -> bool:
    return (
        record.get("candidate_tree_sha256") == context.candidate_tree_sha256
        and record.get("semantic_aggregate_sha256")
        == context.semantic_aggregate_sha256
        and record.get("candidate_source_commit") == context.source_commit
        and record.get("plugin_version") == context.plugin_version
        and record.get("exact_target_manifest_sha256")
        == context.exact_target_manifest_sha256
        and record.get("certification_protocol_version")
        == context.protocol_version
        and record.get("surface") == context.surface
    )


def _evaluate(
    repo_root: Path,
    candidate_root: Path,
    source_sha: str,
    evidence_root: Path,
) -> tuple[dict, list[str]]:
    repo = Path(repo_root).resolve()
    candidate = Path(candidate_root).resolve()
    evidence = Path(evidence_root).resolve()
    identity, errors = _candidate_identity(repo, candidate, source_sha)

    profile = _load_json(repo / "production/sim/manifests/certification-profile.json")
    target_digest = _sha256_file(
        repo / "work/corpus/beta-1.8.42/capture-manifest.json"
    )
    protocol = profile["protocol_version"]
    install_records, install_errors = _installation_records(evidence)
    errors.extend(install_errors)

    surface_results: dict[str, str] = {}
    known_gaps: list[str] = []
    acceptance_dir = evidence / "sim-acceptance"
    try:
        all_acceptance = load_acceptance_records(acceptance_dir)
    except ValueError as exc:
        all_acceptance = []
        errors.append(str(exc))

    for surface, surface_profile in profile["surfaces"].items():
        if not surface_profile["release_blocking"]:
            surface_results[surface] = "NOT_REQUIRED"
            continue

        context = CertificationContext(
            candidate_tree_sha256=identity["candidate_tree_sha256"],
            semantic_aggregate_sha256=identity["semantic_aggregate_sha256"],
            source_commit=identity["source_commit"],
            plugin_version=identity["plugin_version"],
            exact_target_manifest_sha256=target_digest,
            protocol_version=protocol,
            surface=surface,
        )
        matching_install = [
            record
            for record in install_records
            if record.get("surface") == surface
            and record.get("candidate_tree_sha256")
            == identity["candidate_tree_sha256"]
            and record.get("semantic_aggregate_sha256")
            == identity["semantic_aggregate_sha256"]
            and record.get("source_commit") == identity["source_commit"]
            and record.get("plugin_version") == identity["plugin_version"]
            and record.get("exact_target_manifest_sha256") == target_digest
        ]
        if len(matching_install) != 1:
            state = "INCOMPLETE"
            gap = (
                f"{surface} installation evidence missing"
                if not matching_install
                else f"{surface} installation evidence ambiguous"
            )
            surface_results[surface] = state
            known_gaps.append(gap)
            errors.append(gap)
            continue

        installation = matching_install[0]
        result = installation["result"]
        if result == "PLATFORM_LIMITATION":
            surface_results[surface] = "BLOCKED"
            gap = f"{surface} installation PLATFORM_LIMITATION"
            known_gaps.append(gap)
            errors.append(gap)
            continue
        if result == "FAIL":
            surface_results[surface] = "FAIL"
            gap = f"{surface} installation FAIL"
            known_gaps.append(gap)
            errors.append(gap)
            continue
        if (
            installation["observed_public_skill_count"] != 1
            or installation["observed_public_skill_names"] != ["SIM"]
        ):
            surface_results[surface] = "FAIL"
            gap = f"{surface} installed public Skill topology mismatch"
            known_gaps.append(gap)
            errors.append(gap)
            continue

        matched_acceptance = [
            record
            for record in all_acceptance
            if _same_context(record, context)
            and record.get("case_id") in surface_profile["required_cases"]
        ]
        foreign_install_refs = sorted(
            {
                record.get("installation_evidence_id")
                for record in matched_acceptance
                if record.get("installation_evidence_id")
                != installation["installation_evidence_id"]
            }
        )
        if foreign_install_refs:
            surface_results[surface] = "FAIL"
            gap = f"{surface} acceptance references foreign installation evidence"
            known_gaps.append(gap)
            errors.append(gap)
            continue

        try:
            summary = summarize_acceptance(
                acceptance_dir,
                context,
                tuple(surface_profile["required_cases"]),
            )
        except ValueError as exc:
            surface_results[surface] = "FAIL"
            gap = f"{surface} acceptance invalid: {exc}"
            known_gaps.append(gap)
            errors.append(gap)
            continue

        if summary.status == "PASS":
            surface_results[surface] = "PASS"
        elif summary.status == "FAIL":
            surface_results[surface] = "FAIL"
        elif any(
            result == "PLATFORM_LIMITATION"
            for result in summary.case_results.values()
        ):
            surface_results[surface] = "BLOCKED"
        else:
            surface_results[surface] = "INCOMPLETE"
        known_gaps.extend(summary.known_gaps)
        if surface_results[surface] != "PASS":
            errors.append(
                f"{surface} certification {surface_results[surface]}"
            )

    release_blocking_complete = all(
        surface_results[name] == "PASS"
        for name, spec in profile["surfaces"].items()
        if spec["release_blocking"]
    )
    report = {
        "schema_version": 1,
        "plugin_version": identity["plugin_version"],
        "candidate_tree_sha256": identity["candidate_tree_sha256"],
        "semantic_aggregate_sha256": identity["semantic_aggregate_sha256"],
        "source_commit": identity["source_commit"],
        "exact_target_manifest_sha256": target_digest,
        "certification_protocol_version": protocol,
        "surface_results": surface_results,
        "known_gaps": sorted(set(known_gaps)),
        "release_blocking_complete": release_blocking_complete,
    }
    schema = _load_json(repo / "schemas/sim-certification-report.schema.json")
    schema_errors = list(jsonschema.Draft202012Validator(schema).iter_errors(report))
    if schema_errors:
        errors.append("derived certification report violates schema")
    return report, errors


def build_certification_report(
    repo_root: Path,
    candidate_root: Path,
    source_sha: str,
    evidence_root: Path,
) -> dict:
    report, _ = _evaluate(repo_root, candidate_root, source_sha, evidence_root)
    return report


def verify_certification(
    repo_root: Path,
    candidate_root: Path,
    source_sha: str,
    evidence_root: Path,
) -> list[str]:
    _, errors = _evaluate(repo_root, candidate_root, source_sha, evidence_root)
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    check = subparsers.add_parser("check")
    check.add_argument("--repo-root", type=Path, default=Path("."))
    check.add_argument("--source-sha", required=True)
    check.add_argument("--candidate", type=Path, required=True)
    check.add_argument("--evidence-root", type=Path, required=True)
    check.add_argument("--report-out", type=Path)
    args = parser.parse_args(argv)

    report = build_certification_report(
        args.repo_root,
        args.candidate,
        args.source_sha,
        args.evidence_root,
    )
    errors = verify_certification(
        args.repo_root,
        args.candidate,
        args.source_sha,
        args.evidence_root,
    )
    if args.report_out is not None:
        args.report_out.parent.mkdir(parents=True, exist_ok=True)
        args.report_out.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if errors:
        for error in errors:
            print(f"SIM_CERTIFICATION_ERROR: {error}")
        return 1
    print("SIM_CERTIFICATION_OK")
    print(report["candidate_tree_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
