from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ID = "plugins~Plugin_sim_test"
RELEASE_ID = "release_sim_test"
BUNDLE_SHA = "f" * 64


def _head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def _target_digest() -> str:
    return hashlib.sha256(
        (ROOT / "work/corpus/beta-1.8.42/capture-manifest.json").read_bytes()
    ).hexdigest()


def _installation_schema() -> dict:
    return json.loads(
        (ROOT / "schemas/sim-installation-evidence.schema.json").read_text(
            encoding="utf-8"
        )
    )


def _certification_schema() -> dict:
    return json.loads(
        (ROOT / "schemas/sim-certification-report.schema.json").read_text(
            encoding="utf-8"
        )
    )


def _personal_install_record(
    *,
    surface: str = "CHATGPT_WEB_NORMAL_CHAT",
    result: str = "PASS",
    candidate_tree_sha256: str = "a" * 64,
    semantic_aggregate_sha256: str = "b" * 64,
    source_commit: str = "c" * 40,
    target_digest: str = "e" * 64,
) -> dict:
    return {
        "schema_version": 2,
        "installation_evidence_id": f"{surface.lower()}-install-a",
        "surface": surface,
        "result": result,
        "candidate_tree_sha256": candidate_tree_sha256,
        "semantic_aggregate_sha256": semantic_aggregate_sha256,
        "source_commit": source_commit,
        "plugin_version": "0.2.3-preview",
        "exact_target_manifest_sha256": target_digest,
        "certification_protocol_version": "sim-live-v3",
        "transport": "OPENAI_PERSONAL_PLUGIN",
        "plugin_id": PLUGIN_ID,
        "release_id": RELEASE_ID,
        "current_release_id": RELEASE_ID,
        "latest_release_id": RELEASE_ID,
        "scope": "USER",
        "discoverability": "PRIVATE",
        "bundle_sha256": BUNDLE_SHA,
        "platform_release_tree_sha256": candidate_tree_sha256,
        "normalized_platform_tree_sha256": candidate_tree_sha256,
        "observed_public_skill_count": 1,
        "observed_public_skill_names": ["SIM"],
        "recorded_at": "2026-09-24T09:00:00Z",
    }


def test_installation_schema_requires_candidate_tree_identity() -> None:
    record = _personal_install_record()
    validator = jsonschema.Draft202012Validator(_installation_schema())
    validator.validate(record)
    invalid = dict(record)
    del invalid["candidate_tree_sha256"]
    assert list(validator.iter_errors(invalid))


def test_certification_report_schema_requires_all_surface_states() -> None:
    report = {
        "schema_version": 2,
        "plugin_version": "0.2.3-preview",
        "candidate_tree_sha256": "a" * 64,
        "semantic_aggregate_sha256": "b" * 64,
        "source_commit": "c" * 40,
        "exact_target_manifest_sha256": "d" * 64,
        "certification_protocol_version": "sim-live-v3",
        "transport": "OPENAI_PERSONAL_PLUGIN",
        "plugin_id": PLUGIN_ID,
        "release_id": RELEASE_ID,
        "distribution_bundle_sha256": BUNDLE_SHA,
        "platform_release_tree_sha256": "a" * 64,
        "normalized_platform_tree_sha256": "a" * 64,
        "surface_results": {
            "CHATGPT_WEB_NORMAL_CHAT": "PASS",
            "CHATGPT_DESKTOP_NORMAL_CHAT": "PASS",
            "CODEX": "PASS",
            "CHATGPT_WORK": "NOT_REQUIRED",
            "LOCAL_MARKETPLACE": "NOT_REQUIRED",
        },
        "known_gaps": [],
        "release_blocking_complete": True,
        "release_state": "PRIVATE_PLUGIN_CERTIFIED",
    }
    validator = jsonschema.Draft202012Validator(_certification_schema())
    validator.validate(report)
    invalid = json.loads(json.dumps(report))
    del invalid["surface_results"]["CODEX"]
    assert list(validator.iter_errors(invalid))


def _write_personal_release(
    evidence_root: Path,
    *,
    candidate_root: Path,
    candidate_tree_sha256: str,
) -> None:
    from tools.safe_artifacts import safe_source_files

    cert_dir = evidence_root / "sim-certification" / candidate_tree_sha256[:12]
    cert_dir.mkdir(parents=True, exist_ok=True)
    root = candidate_root.resolve()
    files = {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in safe_source_files(root)
    }
    record = {
        "schema_version": 1,
        "plugin_id": PLUGIN_ID,
        "release_id": RELEASE_ID,
        "current_release_id": RELEASE_ID,
        "latest_release_id": RELEASE_ID,
        "scope": "USER",
        "discoverability": "PRIVATE",
        "candidate_tree_sha256": candidate_tree_sha256,
        "bundle_sha256": BUNDLE_SHA,
        "platform_release_tree_sha256": candidate_tree_sha256,
        "files": files,
        "recorded_at": "2026-09-24T09:00:00Z",
    }
    (cert_dir / "personal-plugin-release.json").write_text(
        json.dumps(record), encoding="utf-8"
    )


def _write_installation(
    evidence_root: Path,
    *,
    surface: str,
    candidate_tree_sha256: str,
    semantic_aggregate_sha256: str,
    source_commit: str,
    target_digest: str,
    result: str = "PASS",
) -> None:
    cert_dir = evidence_root / "sim-certification" / candidate_tree_sha256[:12]
    cert_dir.mkdir(parents=True, exist_ok=True)
    record = _personal_install_record(
        surface=surface,
        result=result,
        candidate_tree_sha256=candidate_tree_sha256,
        semantic_aggregate_sha256=semantic_aggregate_sha256,
        source_commit=source_commit,
        target_digest=target_digest,
    )
    (cert_dir / f"{surface.lower()}-installation.json").write_text(
        json.dumps(record), encoding="utf-8"
    )


def _write_acceptance(
    evidence_root: Path,
    *,
    surface: str,
    cases: tuple[str, ...],
    candidate_tree_sha256: str,
    semantic_aggregate_sha256: str,
    source_commit: str,
    target_digest: str,
) -> None:
    acceptance = evidence_root / "sim-acceptance"
    acceptance.mkdir(parents=True, exist_ok=True)
    install_id = f"{surface.lower()}-install-a"
    for case_id in cases:
        record = {
            "schema_version": 3,
            "case_id": case_id,
            "surface": surface,
            "result": "PASS",
            "candidate_tree_sha256": candidate_tree_sha256,
            "semantic_aggregate_sha256": semantic_aggregate_sha256,
            "candidate_source_commit": source_commit,
            "plugin_version": "0.2.3-preview",
            "exact_target_manifest_sha256": target_digest,
            "certification_protocol_version": "sim-live-v3",
            "transport": "OPENAI_PERSONAL_PLUGIN",
            "plugin_id": PLUGIN_ID,
            "release_id": RELEASE_ID,
            "installation_evidence_id": install_id,
            "host_observation": {"synthetic": True},
            "evidence_refs": [f"synthetic-{surface}-{case_id}"],
            "retest_of": None,
            "recorded_at": "2026-09-24T09:01:00Z",
        }
        path = acceptance / f"{surface.lower()}-{case_id}.json"
        path.write_text(json.dumps(record), encoding="utf-8")


def test_certification_blocks_when_required_codex_evidence_is_absent(
    tmp_path: Path,
) -> None:
    from tools.build_sim_plugin import build_candidate
    from tools.verify_sim_certification import (
        build_certification_report,
        verify_certification,
    )

    source_sha = _head()
    candidate = tmp_path / "candidate"
    built = build_candidate(ROOT, source_sha, candidate)
    target = _target_digest()
    evidence = tmp_path / "evidence"

    _write_installation(
        evidence,
        surface="CHATGPT_WEB_NORMAL_CHAT",
        candidate_tree_sha256=built.candidate_tree_sha256,
        semantic_aggregate_sha256=built.semantic_aggregate_sha256,
        source_commit=built.source_commit,
        target_digest=target,
    )
    _write_acceptance(
        evidence,
        surface="CHATGPT_WEB_NORMAL_CHAT",
        cases=tuple(f"A{i:02d}" for i in range(1, 13)),
        candidate_tree_sha256=built.candidate_tree_sha256,
        semantic_aggregate_sha256=built.semantic_aggregate_sha256,
        source_commit=built.source_commit,
        target_digest=target,
    )
    _write_personal_release(
        evidence,
        candidate_root=candidate,
        candidate_tree_sha256=built.candidate_tree_sha256,
    )

    errors = verify_certification(ROOT, candidate, source_sha, evidence)
    report = build_certification_report(ROOT, candidate, source_sha, evidence)
    assert any("CODEX" in error for error in errors)
    assert report["surface_results"]["CHATGPT_WEB_NORMAL_CHAT"] == "PASS"
    assert report["surface_results"]["CODEX"] == "INCOMPLETE"
    assert report["release_blocking_complete"] is False


def test_certification_passes_only_same_candidate_across_required_surfaces(
    tmp_path: Path,
) -> None:
    from tools.build_sim_plugin import build_candidate
    from tools.verify_sim_certification import verify_certification

    source_sha = _head()
    candidate = tmp_path / "candidate"
    built = build_candidate(ROOT, source_sha, candidate)
    target = _target_digest()
    evidence = tmp_path / "evidence"

    requirements = {
        "CHATGPT_WEB_NORMAL_CHAT": tuple(f"A{i:02d}" for i in range(1, 13)),
        "CHATGPT_DESKTOP_NORMAL_CHAT": ("A01", "A03", "A06", "A09", "A10", "A12"),
        "CODEX": ("A01", "A03", "A09", "A10", "A12"),
    }
    for surface, cases in requirements.items():
        _write_installation(
            evidence,
            surface=surface,
            candidate_tree_sha256=built.candidate_tree_sha256,
            semantic_aggregate_sha256=built.semantic_aggregate_sha256,
            source_commit=built.source_commit,
            target_digest=target,
        )
        _write_acceptance(
            evidence,
            surface=surface,
            cases=cases,
            candidate_tree_sha256=built.candidate_tree_sha256,
            semantic_aggregate_sha256=built.semantic_aggregate_sha256,
            source_commit=built.source_commit,
            target_digest=target,
        )
    _write_personal_release(
        evidence,
        candidate_root=candidate,
        candidate_tree_sha256=built.candidate_tree_sha256,
    )

    assert verify_certification(ROOT, candidate, source_sha, evidence) == []


def test_installation_schema_accepts_platform_limitation_as_observation() -> None:
    record = _personal_install_record(
        surface="CODEX",
        result="PLATFORM_LIMITATION",
    )
    jsonschema.Draft202012Validator(_installation_schema()).validate(record)


def test_release_builder_accepts_legacy_certification_report_for_composition(
    tmp_path: Path,
) -> None:
    from tools.build_sim_release import build_sim_release

    certification = {
        "schema_version": 1,
        "plugin_version": "0.2.3-preview",
        "candidate_tree_sha256": "a" * 64,
        "semantic_aggregate_sha256": "b" * 64,
        "source_commit": "c" * 40,
        "exact_target_manifest_sha256": _target_digest(),
        "certification_protocol_version": "sim-live-v2",
        "surface_results": {
            "ChatGPT": "PASS",
            "Codex": "PASS",
            "ChatGPT Project": "NOT_REQUIRED",
        },
        "known_gaps": [],
        "release_blocking_complete": True,
    }
    report_path = tmp_path / "certification-report.json"
    report_path.write_text(json.dumps(certification), encoding="utf-8")
    _, report = build_sim_release(
        ROOT,
        out_dir=tmp_path / "release",
        certification_report=report_path,
    )
    assert report["surface_acceptance"] == "PASS"
    assert report["release_status"] == "PREVIEW_CERTIFIED"


def test_release_verifier_accepts_global_certification_inputs(
    tmp_path: Path,
) -> None:
    from tools.build_sim_plugin import build_candidate
    from tools.build_sim_release import build_sim_release
    from tools.verify_sim_release import verify_sim_release

    source_sha = _head()
    candidate = tmp_path / "candidate"
    build_candidate(ROOT, source_sha, candidate)
    zip_path, report = build_sim_release(ROOT, out_dir=tmp_path / "release")
    report_path = tmp_path / "release" / f"sim-{report['sim_version']}.release-report.json"

    errors = verify_sim_release(
        zip_path,
        report_path,
        report["sim_version"],
        candidate_root=candidate,
        source_sha=source_sha,
        evidence_root=tmp_path / "evidence",
    )
    assert isinstance(errors, list)


def test_certification_requires_exact_personal_release_evidence(
    tmp_path: Path,
) -> None:
    from tools.build_sim_plugin import build_candidate
    from tools.verify_sim_certification import verify_certification

    source_sha = _head()
    candidate = tmp_path / "candidate"
    built = build_candidate(ROOT, source_sha, candidate)
    target = _target_digest()
    evidence = tmp_path / "evidence"

    requirements = {
        "CHATGPT_WEB_NORMAL_CHAT": tuple(f"A{i:02d}" for i in range(1, 13)),
        "CHATGPT_DESKTOP_NORMAL_CHAT": ("A01", "A03", "A06", "A09", "A10", "A12"),
        "CODEX": ("A01", "A03", "A09", "A10", "A12"),
    }
    for surface, cases in requirements.items():
        _write_installation(
            evidence,
            surface=surface,
            candidate_tree_sha256=built.candidate_tree_sha256,
            semantic_aggregate_sha256=built.semantic_aggregate_sha256,
            source_commit=built.source_commit,
            target_digest=target,
        )
        _write_acceptance(
            evidence,
            surface=surface,
            cases=cases,
            candidate_tree_sha256=built.candidate_tree_sha256,
            semantic_aggregate_sha256=built.semantic_aggregate_sha256,
            source_commit=built.source_commit,
            target_digest=target,
        )

    errors = verify_certification(ROOT, candidate, source_sha, evidence)
    assert any("personal release evidence missing" in error for error in errors)
