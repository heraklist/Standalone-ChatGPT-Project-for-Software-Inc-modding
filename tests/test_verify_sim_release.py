from __future__ import annotations

import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from tools.build_sim_release import build_sim_release

ROOT = Path(__file__).resolve().parents[1]


def _report_path(root: Path) -> Path:
    return root / "sim-0.2.3-preview.release-report.json"


def _rewrite_zip(source: Path, destination: Path, *, drop: set[str] | None = None, add: dict[str, bytes] | None = None) -> None:
    drop = drop or set()
    add = add or {}
    with ZipFile(source) as original, ZipFile(destination, "w", compression=ZIP_DEFLATED) as rewritten:
        for name in original.namelist():
            if name not in drop:
                rewritten.writestr(name, original.read(name))
        for name, data in add.items():
            rewritten.writestr(name, data)


def test_independent_verifier_accepts_valid_preview_build(tmp_path: Path) -> None:
    from tools.verify_sim_release import verify_sim_release

    zip_path, _ = build_sim_release(ROOT, out_dir=tmp_path)
    assert verify_sim_release(zip_path, _report_path(tmp_path), "0.2.3-preview") == []


def test_verifier_rejects_bundle_digest_mismatch(tmp_path: Path) -> None:
    from tools.verify_sim_release import verify_sim_release

    zip_path, _ = build_sim_release(ROOT, out_dir=tmp_path)
    report_path = _report_path(tmp_path)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["bundle_sha256"] = "0" * 64
    report_path.write_text(json.dumps(report), encoding="utf-8")
    assert any("bundle SHA-256 mismatch" in error for error in verify_sim_release(zip_path, report_path, "0.2.3-preview"))


def test_verifier_rejects_missing_required_runtime_entries(tmp_path: Path) -> None:
    from tools.verify_sim_release import verify_sim_release

    zip_path, _ = build_sim_release(ROOT, out_dir=tmp_path)
    for missing in ("production/sim/SKILL.md", "production/sim/manifests/reference-source-map.json"):
        altered = tmp_path / (Path(missing).name + ".zip")
        _rewrite_zip(zip_path, altered, drop={missing})
        errors = verify_sim_release(altered, _report_path(tmp_path), "0.2.3-preview")
        assert any("missing required SIM bundle entry" in error for error in errors)


def test_verifier_rejects_forbidden_raw_evidence_path(tmp_path: Path) -> None:
    from tools.verify_sim_release import verify_sim_release

    zip_path, _ = build_sim_release(ROOT, out_dir=tmp_path)
    altered = tmp_path / "forbidden.zip"
    _rewrite_zip(zip_path, altered, add={"work/corpus/private.bin": b"fixture"})
    errors = verify_sim_release(altered, _report_path(tmp_path), "0.2.3-preview")
    assert any("forbidden bundle path" in error for error in errors)


def test_verifier_rejects_reported_file_hash_mismatch(tmp_path: Path) -> None:
    from tools.verify_sim_release import verify_sim_release

    zip_path, _ = build_sim_release(ROOT, out_dir=tmp_path)
    altered = tmp_path / "tampered.zip"
    _rewrite_zip(zip_path, altered, add={"production/sim/SKILL.md": b"tampered"}, drop={"production/sim/SKILL.md"})
    errors = verify_sim_release(altered, _report_path(tmp_path), "0.2.3-preview")
    assert any("file SHA-256 mismatch" in error or "bundle SHA-256 mismatch" in error for error in errors)


def test_verifier_rejects_report_only_preview_certification(tmp_path: Path) -> None:
    from tools.verify_sim_release import verify_sim_release

    zip_path, report = build_sim_release(ROOT, out_dir=tmp_path)
    report_path = _report_path(tmp_path)
    report["surface_acceptance"] = "PASS"
    report["known_gaps"] = []
    report["release_status"] = "PREVIEW_CERTIFIED"
    report_path.write_text(json.dumps(report), encoding="utf-8")

    errors = verify_sim_release(
        zip_path,
        report_path,
        expected_version=report["sim_version"],
    )
    assert any("PREVIEW_CERTIFIED" in error for error in errors)


def _certification_context(*, candidate: str = "a" * 64, target: str, protocol: str = "sim-live-v2"):
    from tools.sim_acceptance import CertificationContext

    return CertificationContext(
        candidate_tree_sha256=candidate,
        semantic_aggregate_sha256="b" * 64,
        source_commit="c" * 40,
        plugin_version="0.2.3-preview",
        exact_target_manifest_sha256=target,
        protocol_version=protocol,
        surface="ChatGPT",
    )


def _write_acceptance_records(
    evidence_dir: Path,
    *,
    candidate: str = "a" * 64,
    target: str,
    protocol: str = "sim-live-v2",
    fail_case: str | None = None,
) -> None:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    for index in range(1, 13):
        case_id = f"A{index:02d}"
        record = {
            "schema_version": 2,
            "case_id": case_id,
            "surface": "ChatGPT",
            "result": "FAIL" if case_id == fail_case else "PASS",
            "candidate_tree_sha256": candidate,
            "semantic_aggregate_sha256": "b" * 64,
            "candidate_source_commit": "c" * 40,
            "plugin_version": "0.2.3-preview",
            "exact_target_manifest_sha256": target,
            "certification_protocol_version": protocol,
            "installation_evidence_id": "install-a",
            "host_observation": {},
            "evidence_refs": [f"obs-{case_id}"],
            "retest_of": None,
            "recorded_at": "2026-09-22T20:00:00+03:00",
        }
        (evidence_dir / f"{case_id}.json").write_text(
            json.dumps(record), encoding="utf-8"
        )


def _target_digest(report: dict) -> str:
    prefix = "exact-target-manifest-sha256:"
    assert report["canonical_source_revision"].startswith(prefix)
    return report["canonical_source_revision"][len(prefix):]


def test_certified_release_rejects_missing_evidence_directory(tmp_path: Path) -> None:
    from tools.verify_sim_release import verify_sim_release

    zip_path, report = build_sim_release(ROOT, out_dir=tmp_path)
    target = _target_digest(report)
    report["release_status"] = "PREVIEW_CERTIFIED"
    report["surface_acceptance"] = "PASS"
    report_path = _report_path(tmp_path)
    report_path.write_text(json.dumps(report), encoding="utf-8")

    errors = verify_sim_release(
        zip_path,
        report_path,
        report["sim_version"],
        certification_context=_certification_context(target=target),
        evidence_dir=tmp_path / "missing-evidence",
    )
    assert any("acceptance" in error.lower() or "certified" in error.lower() for error in errors)


def test_certified_release_rejects_wrong_exact_target_digest(tmp_path: Path) -> None:
    from tools.verify_sim_release import verify_sim_release

    zip_path, report = build_sim_release(ROOT, out_dir=tmp_path)
    target = _target_digest(report)
    evidence_dir = tmp_path / "evidence"
    _write_acceptance_records(evidence_dir, target="d" * 64)
    report["release_status"] = "PREVIEW_CERTIFIED"
    report["surface_acceptance"] = "PASS"
    report_path = _report_path(tmp_path)
    report_path.write_text(json.dumps(report), encoding="utf-8")

    errors = verify_sim_release(
        zip_path,
        report_path,
        report["sim_version"],
        certification_context=_certification_context(target="d" * 64),
        evidence_dir=evidence_dir,
    )
    assert any("exact-target" in error.lower() for error in errors)
    assert target != "d" * 64


def test_certified_release_rejects_wrong_protocol_context(tmp_path: Path) -> None:
    from tools.verify_sim_release import verify_sim_release

    zip_path, report = build_sim_release(ROOT, out_dir=tmp_path)
    target = _target_digest(report)
    evidence_dir = tmp_path / "evidence"
    _write_acceptance_records(evidence_dir, target=target, protocol="sim-live-v2")
    report["release_status"] = "PREVIEW_CERTIFIED"
    report["surface_acceptance"] = "PASS"
    report_path = _report_path(tmp_path)
    report_path.write_text(json.dumps(report), encoding="utf-8")

    errors = verify_sim_release(
        zip_path,
        report_path,
        report["sim_version"],
        certification_context=_certification_context(
            target=target, protocol="sim-live-v9"
        ),
        evidence_dir=evidence_dir,
    )
    assert any("PREVIEW_CERTIFIED" in error or "acceptance" in error.lower() for error in errors)


def test_certified_release_rejects_foreign_candidate_pass_evidence(tmp_path: Path) -> None:
    from tools.verify_sim_release import verify_sim_release

    zip_path, report = build_sim_release(ROOT, out_dir=tmp_path)
    target = _target_digest(report)
    evidence_dir = tmp_path / "evidence"
    _write_acceptance_records(evidence_dir, candidate="e" * 64, target=target)
    report["release_status"] = "PREVIEW_CERTIFIED"
    report["surface_acceptance"] = "PASS"
    report_path = _report_path(tmp_path)
    report_path.write_text(json.dumps(report), encoding="utf-8")

    errors = verify_sim_release(
        zip_path,
        report_path,
        report["sim_version"],
        certification_context=_certification_context(target=target),
        evidence_dir=evidence_dir,
    )
    assert any("PREVIEW_CERTIFIED" in error or "acceptance" in error.lower() for error in errors)


def test_live_failed_release_rejects_manually_cleared_known_gaps(tmp_path: Path) -> None:
    from tools.verify_sim_release import verify_sim_release

    zip_path, report = build_sim_release(ROOT, out_dir=tmp_path)
    target = _target_digest(report)
    evidence_dir = tmp_path / "evidence"
    _write_acceptance_records(evidence_dir, target=target, fail_case="A06")
    report["release_status"] = "PREVIEW_LIVE_FAILED"
    report["surface_acceptance"] = "FAIL"
    report["known_gaps"] = []
    report_path = _report_path(tmp_path)
    report_path.write_text(json.dumps(report), encoding="utf-8")

    errors = verify_sim_release(
        zip_path,
        report_path,
        report["sim_version"],
        certification_context=_certification_context(target=target),
        evidence_dir=evidence_dir,
    )
    assert any("known_gaps" in error for error in errors)


def test_source_release_verifier_rejects_v3_private_plugin_certification_inheritance(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from tools.verify_sim_release import verify_sim_release
    import tools.verify_sim_certification as certification

    zip_path, report = build_sim_release(ROOT, out_dir=tmp_path)
    report["release_status"] = "PREVIEW_CERTIFIED"
    report["surface_acceptance"] = "PASS"
    report["known_gaps"] = []
    report_path = _report_path(tmp_path)
    report_path.write_text(json.dumps(report), encoding="utf-8")

    monkeypatch.setattr(certification, "verify_certification", lambda *args, **kwargs: [])
    monkeypatch.setattr(
        certification,
        "build_certification_report",
        lambda *args, **kwargs: {
            "schema_version": 2,
            "plugin_version": "0.2.3-preview",
            "candidate_tree_sha256": "a" * 64,
            "semantic_aggregate_sha256": "b" * 64,
            "source_commit": "c" * 40,
            "exact_target_manifest_sha256": "d" * 64,
            "certification_protocol_version": "sim-live-v3",
            "transport": "OPENAI_PERSONAL_PLUGIN",
            "plugin_id": "plugins~Plugin_test",
            "release_id": "release_test",
            "distribution_bundle_sha256": "e" * 64,
            "platform_release_tree_sha256": "a" * 64,
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
        },
    )

    errors = verify_sim_release(
        zip_path,
        report_path,
        report["sim_version"],
        candidate_root=tmp_path / "candidate",
        source_sha="c" * 40,
        evidence_root=tmp_path / "evidence",
    )
    assert any(
        "source release cannot inherit personal plugin certification" in error
        for error in errors
    )
