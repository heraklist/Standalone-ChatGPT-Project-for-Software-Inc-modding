from __future__ import annotations

import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

import jsonschema

ROOT = Path(__file__).resolve().parents[1]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_preview_builder_emits_canonical_identity_and_schema_valid_report(tmp_path: Path) -> None:
    from tools.build_sim_release import build_sim_release

    zip_path, report = build_sim_release(ROOT, channel="preview", out_dir=tmp_path)

    assert zip_path.name == "sim-0.2.3-preview.1.zip"
    assert report["sim_version"] == "0.2.3-preview.1"
    assert report["channel"] == "PREVIEW"
    assert report["target"] == "Beta 1.8.42"
    assert report["evidence_grade"] == "GENERATION_GRADE"
    assert report["release_status"] == "PREVIEW_VALIDATED"
    assert report["bundle_sha256"] == _sha256(zip_path)

    schema = json.loads((ROOT / "schemas/sim-release-manifest.schema.json").read_text(encoding="utf-8"))
    jsonschema.validate(report, schema)

    report_path = tmp_path / "sim-0.2.3-preview.1.release-report.json"
    assert json.loads(report_path.read_text(encoding="utf-8")) == report


def test_preview_report_keeps_repository_build_separate_from_live_acceptance(
    tmp_path: Path,
) -> None:
    from tools.build_sim_release import build_sim_release

    _, report = build_sim_release(ROOT, channel="preview", out_dir=tmp_path)

    assert report["surface_acceptance"] == "NOT_EVALUATED"
    assert report["known_gaps"] == []
    assert report["release_status"] == "PREVIEW_VALIDATED"
    assert report["security_results"] == ["NOT_EXECUTED_BY_RELEASE_BUILDER"]
    assert report["artifact_fixture_results"] == ["NOT_EXECUTED_BY_RELEASE_BUILDER"]


def test_release_builder_never_marks_certified_without_complete_candidate_context(
    tmp_path: Path,
) -> None:
    from tools.build_sim_release import build_sim_release

    _, report = build_sim_release(ROOT, out_dir=tmp_path)
    assert report["release_status"] != "PREVIEW_CERTIFIED"
    assert report["surface_acceptance"] in {
        "NOT_EVALUATED",
        "INCOMPLETE",
        "FAIL",
    }


def test_preview_bundle_contains_only_runtime_sim_payload(tmp_path: Path) -> None:
    from tools.build_sim_release import build_sim_release

    zip_path, report = build_sim_release(ROOT, out_dir=tmp_path)
    with ZipFile(zip_path) as archive:
        names = archive.namelist()

    assert names == sorted(names)
    assert "production/sim/SKILL.md" in names
    assert "production/sim/manifests/reference-source-map.json" in names
    assert all(name.startswith("production/sim/") for name in names)
    assert not any(name.startswith("work/corpus/") for name in names)
    assert not any(name.startswith("archive/raw/") for name in names)
    assert set(report["files"]) == set(names)


def test_preview_bundle_is_byte_reproducible_across_output_directories(tmp_path: Path) -> None:
    from tools.build_sim_release import build_sim_release

    first, first_report = build_sim_release(ROOT, out_dir=tmp_path / "first")
    second, second_report = build_sim_release(ROOT, out_dir=tmp_path / "second")

    assert _sha256(first) == _sha256(second)
    assert first_report["bundle_sha256"] == second_report["bundle_sha256"]
    assert first_report["files"] == second_report["files"]

    with ZipFile(first) as archive:
        assert all(info.date_time == (1980, 1, 1, 0, 0, 0) for info in archive.infolist())


def test_source_release_cannot_inherit_private_plugin_certification(
    tmp_path: Path,
) -> None:
    import json
    from tools.build_sim_release import build_sim_release

    certification = {
        "schema_version": 2,
        "plugin_version": "0.2.3-preview.1",
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
    cert_path = tmp_path / "certification.json"
    cert_path.write_text(json.dumps(certification), encoding="utf-8")

    _, report = build_sim_release(
        ROOT,
        out_dir=tmp_path / "source-release",
        certification_report=cert_path,
    )

    assert report["release_status"] == "PREVIEW_VALIDATED"
    assert report["surface_acceptance"] == "NOT_EVALUATED"
