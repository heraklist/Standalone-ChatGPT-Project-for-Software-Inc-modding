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
from tools.verify_sim_personal_release import verify_personal_release

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
            "plugin_version": "0.2.3-preview.1",
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
        plugin_version = "0.2.3-preview.1"

    return {
        "candidate_tree_sha256": candidate_hash,
        "semantic_aggregate_sha256": semantic,
        "source_commit": full_source,
        "plugin_version": plugin_version,
    }, errors


def _personal_release_records(
    evidence_root: Path,
) -> tuple[list[dict], list[str]]:
    records: list[dict] = []
    errors: list[str] = []
    directory = evidence_root / "sim-certification"
    if not directory.is_dir():
        return records, errors

    schema = _load_json(
        ROOT / "schemas/sim-personal-plugin-release-evidence.schema.json"
    )
    validator = jsonschema.Draft202012Validator(schema)
    for path in sorted(directory.rglob("*.json")):
        try:
            value = _load_json(path)
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
            continue
        if not {"plugin_id", "release_id", "files"}.issubset(value):
            continue
        schema_errors = sorted(
            validator.iter_errors(value),
            key=lambda error: tuple(str(part) for part in error.absolute_path),
        )
        if schema_errors:
            errors.append(
                f"personal release evidence schema violation in {path.name}: "
                + schema_errors[0].message
            )
            continue
        records.append(value)
    return records, errors


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


def _verify_marketplace_chain(repo_root: Path, record: dict) -> list[str]:
    errors: list[str] = []
    try:
        marketplace_source = GitSource(repo_root, record["marketplace_commit"])
        marketplace = json.loads(
            marketplace_source.read_bytes(".agents/plugins/marketplace.json").decode(
                "utf-8"
            )
        )
    except (KeyError, ValueError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"marketplace evidence unreadable: {exc}"]

    if marketplace.get("name") != record.get("marketplace_name"):
        errors.append("marketplace name mismatch")

    plugin = next(
        (
            item
            for item in marketplace.get("plugins", [])
            if isinstance(item, dict) and item.get("name") == "sim"
        ),
        None,
    )
    if plugin is None:
        errors.append("marketplace SIM entry missing")
        return errors

    source = plugin.get("source") if isinstance(plugin.get("source"), dict) else {}
    if source.get("sha") != record.get("projection_commit"):
        errors.append("marketplace projection mismatch")
    if source.get("path") != record.get("plugin_locator"):
        errors.append("marketplace plugin locator mismatch")

    try:
        projection_source = GitSource(repo_root, record["projection_commit"])
        provenance = json.loads(
            projection_source.read_bytes(
                "plugins/sim/provenance/plugin_manifest.json"
            ).decode("utf-8")
        )
    except (KeyError, ValueError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append(f"projection provenance unreadable: {exc}")
        return errors

    if provenance.get("source_commit") != record.get("source_commit"):
        errors.append("projection source mismatch")
    return sorted(set(errors))


def _verify_personal_evidence_binding(
    installation: dict,
    release: dict,
) -> list[str]:
    errors: list[str] = []
    if installation.get("plugin_id") != release.get("plugin_id"):
        errors.append("personal plugin id mismatch")
    if installation.get("release_id") != release.get("release_id"):
        errors.append("personal plugin release mismatch")
    if installation.get("bundle_sha256") != release.get("bundle_sha256"):
        errors.append("personal plugin bundle mismatch")
    if (
        installation.get("platform_release_tree_sha256")
        != release.get("platform_release_tree_sha256")
    ):
        errors.append("personal plugin platform tree mismatch")
    release_normalized_tree = release.get(
        "normalized_platform_tree_sha256",
        release.get("platform_release_tree_sha256"),
    )
    if (
        installation.get("normalized_platform_tree_sha256")
        != release_normalized_tree
    ):
        errors.append("personal plugin normalized platform tree mismatch")
    return sorted(set(errors))


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
        and (
            context.protocol_version != "sim-live-v3"
            or (
                record.get("transport") == context.transport
                and record.get("plugin_id") == context.plugin_id
                and record.get("release_id") == context.release_id
            )
        )
    )


def _matching_installations(
    records: list[dict],
    *,
    surface: str,
    identity: dict,
    target_digest: str,
    protocol: str,
    transport: str,
) -> list[dict]:
    return [
        record
        for record in records
        if record.get("schema_version") == 2
        and record.get("surface") == surface
        and record.get("candidate_tree_sha256") == identity["candidate_tree_sha256"]
        and record.get("semantic_aggregate_sha256")
        == identity["semantic_aggregate_sha256"]
        and record.get("source_commit") == identity["source_commit"]
        and record.get("plugin_version") == identity["plugin_version"]
        and record.get("exact_target_manifest_sha256") == target_digest
        and record.get("certification_protocol_version") == protocol
        and record.get("transport") == transport
    ]


def _release_state(
    surface_results: dict[str, str],
    release_blocking_complete: bool,
    plugin_id: str | None,
    *,
    live_surface_observed: bool,
) -> str:
    if release_blocking_complete:
        return "PRIVATE_PLUGIN_CERTIFIED"
    if any(value == "FAIL" for value in surface_results.values()):
        return "PRIVATE_PLUGIN_LIVE_FAILED"
    if plugin_id is not None and live_surface_observed:
        return "PRIVATE_PLUGIN_LIVE_INCOMPLETE"
    if plugin_id is not None:
        return "PERSONAL_PLUGIN_BYTES_VERIFIED"
    return "PLUGIN_CANDIDATE_VALIDATED"


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
    production_transport = profile.get("production_transport", "OPENAI_PERSONAL_PLUGIN")
    install_records, install_errors = _installation_records(evidence)
    errors.extend(install_errors)
    personal_release_records, personal_release_errors = _personal_release_records(
        evidence
    )
    errors.extend(personal_release_errors)

    surface_results: dict[str, str] = {}
    known_gaps: list[str] = []
    acceptance_dir = evidence / "sim-acceptance"
    try:
        all_acceptance = load_acceptance_records(acceptance_dir)
    except ValueError as exc:
        all_acceptance = []
        errors.append(str(exc))

    personal_identity: tuple[str, str] | None = None
    bundle_sha256: str | None = None
    platform_tree_sha256: str | None = None
    normalized_platform_tree_sha256: str | None = None
    live_surface_observed = False

    matching_personal_releases = [
        release
        for release in personal_release_records
        if release.get("candidate_tree_sha256") == identity["candidate_tree_sha256"]
        and release.get("normalized_platform_tree_sha256") == identity["candidate_tree_sha256"]
        and not verify_personal_release(candidate, release)
    ]
    if len(matching_personal_releases) == 1:
        release = matching_personal_releases[0]
        personal_identity = (release["plugin_id"], release["release_id"])
        bundle_sha256 = release.get("bundle_sha256")
        platform_tree_sha256 = release.get("platform_release_tree_sha256")
        normalized_platform_tree_sha256 = release.get(
            "normalized_platform_tree_sha256",
            release.get("platform_release_tree_sha256"),
        )
    elif len(matching_personal_releases) > 1:
        errors.append("personal release evidence ambiguous for candidate")

    for surface, surface_profile in profile["surfaces"].items():
        if not surface_profile["release_blocking"]:
            surface_results[surface] = "NOT_REQUIRED"
            continue

        matching_install = _matching_installations(
            install_records,
            surface=surface,
            identity=identity,
            target_digest=target_digest,
            protocol=protocol,
            transport=production_transport,
        )
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
        live_surface_observed = True
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

        plugin_id = installation.get("plugin_id")
        release_id = installation.get("release_id")
        if not isinstance(plugin_id, str) or not isinstance(release_id, str):
            surface_results[surface] = "FAIL"
            gap = f"{surface} personal plugin identity missing"
            known_gaps.append(gap)
            errors.append(gap)
            continue
        if installation.get("current_release_id") != release_id:
            surface_results[surface] = "FAIL"
            gap = f"{surface} personal plugin release is not current"
            known_gaps.append(gap)
            errors.append(gap)
            continue
        if installation.get("scope") != "USER" or installation.get("discoverability") != "PRIVATE":
            surface_results[surface] = "FAIL"
            gap = f"{surface} personal plugin scope/discoverability mismatch"
            known_gaps.append(gap)
            errors.append(gap)
            continue
        if installation.get("normalized_platform_tree_sha256") != identity["candidate_tree_sha256"]:
            surface_results[surface] = "FAIL"
            gap = f"{surface} normalized platform release tree mismatch"
            known_gaps.append(gap)
            errors.append(gap)
            continue

        matching_releases = [
            release
            for release in personal_release_records
            if release.get("plugin_id") == plugin_id
            and release.get("release_id") == release_id
            and release.get("candidate_tree_sha256")
            == identity["candidate_tree_sha256"]
        ]
        if len(matching_releases) != 1:
            surface_results[surface] = (
                "INCOMPLETE" if not matching_releases else "FAIL"
            )
            gap = (
                f"{surface} personal release evidence missing"
                if not matching_releases
                else f"{surface} personal release evidence ambiguous"
            )
            known_gaps.append(gap)
            errors.append(gap)
            continue

        release_evidence = matching_releases[0]
        binding_errors = _verify_personal_evidence_binding(
            installation, release_evidence
        )
        release_errors = verify_personal_release(candidate, release_evidence)
        if binding_errors or release_errors:
            surface_results[surface] = "FAIL"
            for detail in binding_errors + release_errors:
                gap = f"{surface} {detail}"
                known_gaps.append(gap)
                errors.append(gap)
            continue

        current_identity = (plugin_id, release_id)
        if personal_identity is None:
            personal_identity = current_identity
            bundle_sha256 = release_evidence.get("bundle_sha256")
            platform_tree_sha256 = release_evidence.get(
                "platform_release_tree_sha256"
            )
            normalized_platform_tree_sha256 = release_evidence.get(
                "normalized_platform_tree_sha256",
                release_evidence.get("platform_release_tree_sha256"),
            )
        elif personal_identity != current_identity:
            surface_results[surface] = "FAIL"
            gap = f"{surface} references a different personal plugin release"
            known_gaps.append(gap)
            errors.append(gap)
            continue
        elif (
            bundle_sha256 != release_evidence.get("bundle_sha256")
            or platform_tree_sha256
            != release_evidence.get("platform_release_tree_sha256")
            or normalized_platform_tree_sha256
            != release_evidence.get(
                "normalized_platform_tree_sha256",
                release_evidence.get("platform_release_tree_sha256"),
            )
        ):
            surface_results[surface] = "FAIL"
            gap = f"{surface} personal plugin release identity metadata mismatch"
            known_gaps.append(gap)
            errors.append(gap)
            continue

        context = CertificationContext(
            candidate_tree_sha256=identity["candidate_tree_sha256"],
            semantic_aggregate_sha256=identity["semantic_aggregate_sha256"],
            source_commit=identity["source_commit"],
            plugin_version=identity["plugin_version"],
            exact_target_manifest_sha256=target_digest,
            protocol_version=protocol,
            surface=surface,
            transport=production_transport,
            plugin_id=plugin_id,
            release_id=release_id,
        )

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

        if "A06" in surface_profile["required_cases"] and summary.case_results.get("A06") != "PASS":
            if summary.case_results.get("A06") == "FAIL":
                surface_results[surface] = "FAIL"
            elif summary.case_results.get("A06") == "PLATFORM_LIMITATION":
                surface_results[surface] = "BLOCKED"
            else:
                surface_results[surface] = "INCOMPLETE"
            gap = f"{surface} A06 canary {summary.case_results.get('A06', 'NOT_TESTED')}"
            known_gaps.append(gap)
            errors.append(gap)
            continue

        if summary.status == "PASS":
            surface_results[surface] = "PASS"
        elif summary.status == "FAIL":
            surface_results[surface] = "FAIL"
        elif any(
            case_result == "PLATFORM_LIMITATION"
            for case_result in summary.case_results.values()
        ):
            surface_results[surface] = "BLOCKED"
        else:
            surface_results[surface] = "INCOMPLETE"
        known_gaps.extend(summary.known_gaps)
        if surface_results[surface] != "PASS":
            errors.append(f"{surface} certification {surface_results[surface]}")

    release_blocking_complete = all(
        surface_results[name] == "PASS"
        for name, spec in profile["surfaces"].items()
        if spec["release_blocking"]
    )
    plugin_id = personal_identity[0] if personal_identity else None
    release_id = personal_identity[1] if personal_identity else None
    report = {
        "schema_version": 2,
        "plugin_version": identity["plugin_version"],
        "candidate_tree_sha256": identity["candidate_tree_sha256"],
        "semantic_aggregate_sha256": identity["semantic_aggregate_sha256"],
        "source_commit": identity["source_commit"],
        "exact_target_manifest_sha256": target_digest,
        "certification_protocol_version": protocol,
        "transport": production_transport,
        "plugin_id": plugin_id,
        "release_id": release_id,
        "distribution_bundle_sha256": bundle_sha256,
        "platform_release_tree_sha256": platform_tree_sha256,
        "normalized_platform_tree_sha256": normalized_platform_tree_sha256,
        "surface_results": surface_results,
        "known_gaps": sorted(set(known_gaps)),
        "release_blocking_complete": release_blocking_complete,
        "release_state": _release_state(
            surface_results,
            release_blocking_complete,
            plugin_id,
            live_surface_observed=live_surface_observed,
        ),
    }
    schema = _load_json(repo / "schemas/sim-certification-report.schema.json")
    schema_errors = list(jsonschema.Draft202012Validator(schema).iter_errors(report))
    if schema_errors:
        errors.append(
            "derived certification report violates schema: "
            + schema_errors[0].message
        )
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
