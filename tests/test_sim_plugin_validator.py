from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _head() -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _build(tmp_path: Path):
    from tools.build_sim_plugin import build_candidate

    source_sha = _head()
    candidate = tmp_path / "candidate"
    result = build_candidate(ROOT, source_sha, candidate)
    return candidate, source_sha, result


def _codes(findings) -> set[str]:
    return {finding.code for finding in findings}


def test_validator_accepts_clean_candidate(tmp_path: Path) -> None:
    from tools.validate_sim_plugin import validate_candidate

    candidate, source_sha, _ = _build(tmp_path)
    assert validate_candidate(ROOT, candidate, source_sha) == []


def test_validator_detects_root_skill_projection_byte_tamper(tmp_path: Path) -> None:
    from tools.validate_sim_plugin import validate_candidate

    candidate, source_sha, _ = _build(tmp_path)
    skill = candidate / "skills/sim/SKILL.md"
    skill.write_bytes(skill.read_bytes() + b"\ntampered\n")

    findings = validate_candidate(ROOT, candidate, source_sha)
    assert "SIM_PLUGIN_PROJECTION_BYTE_DRIFT" in _codes(findings)


def test_validator_rejects_undeclared_candidate_file(tmp_path: Path) -> None:
    from tools.validate_sim_plugin import validate_candidate

    candidate, source_sha, _ = _build(tmp_path)
    (candidate / "rogue.txt").write_text("rogue", encoding="utf-8")

    findings = validate_candidate(ROOT, candidate, source_sha)
    assert "SIM_PLUGIN_UNDECLARED_FILE" in _codes(findings)


def test_validator_rejects_second_public_skill(tmp_path: Path) -> None:
    from tools.validate_sim_plugin import validate_candidate

    candidate, source_sha, _ = _build(tmp_path)
    other = candidate / "skills/other/SKILL.md"
    other.parent.mkdir(parents=True)
    other.write_text("---\nname: other\n---\n", encoding="utf-8")

    findings = validate_candidate(ROOT, candidate, source_sha)
    assert "SIM_PLUGIN_PUBLIC_SKILL_COUNT_INVALID" in _codes(findings)


def test_validator_rejects_file_hash_manifest_tamper(tmp_path: Path) -> None:
    from tools.validate_sim_plugin import validate_candidate

    candidate, source_sha, _ = _build(tmp_path)
    path = candidate / "provenance/file_hashes.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    first = sorted(payload["files"])[0]
    payload["files"][first] = "0" * 64
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")

    findings = validate_candidate(ROOT, candidate, source_sha)
    assert "SIM_PLUGIN_FILE_HASH_DRIFT" in _codes(findings)


def test_validator_rejects_plugin_manifest_aggregate_tamper(tmp_path: Path) -> None:
    from tools.validate_sim_plugin import validate_candidate

    candidate, source_sha, _ = _build(tmp_path)
    path = candidate / "provenance/plugin_manifest.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["semantic_aggregate_sha256"] = "0" * 64
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")

    findings = validate_candidate(ROOT, candidate, source_sha)
    assert "SIM_PLUGIN_AGGREGATE_HASH_DRIFT" in _codes(findings)


def test_validator_rejects_duplicate_runtime_source_tree(tmp_path: Path) -> None:
    from tools.validate_sim_plugin import validate_candidate

    candidate, source_sha, _ = _build(tmp_path)
    duplicate = candidate / "production/sim"
    duplicate.mkdir(parents=True)
    (duplicate / "SKILL.md").write_text("duplicate", encoding="utf-8")

    findings = validate_candidate(ROOT, candidate, source_sha)
    assert "SIM_PLUGIN_DUPLICATE_RUNTIME_SOURCE" in _codes(findings)


def test_validator_rejects_unexpected_symlink(tmp_path: Path) -> None:
    from tools.validate_sim_plugin import validate_candidate

    candidate, source_sha, _ = _build(tmp_path)
    target = candidate / "plugin.json"
    link = candidate / "rogue-link"
    try:
        os.symlink(target, link)
    except OSError as exc:
        pytest.skip(f"symlink creation unavailable: {exc}")

    findings = validate_candidate(ROOT, candidate, source_sha)
    assert "SIM_PLUGIN_UNEXPECTED_SYMLINK" in _codes(findings)


def test_validator_fails_when_valid_candidate_checked_against_different_source(
    tmp_path: Path,
) -> None:
    from tools.build_sim_plugin import build_candidate
    from tools.validate_sim_plugin import validate_candidate

    repo = tmp_path / "repo"
    shutil.copytree(
        ROOT,
        repo,
        ignore=shutil.ignore_patterns(".git", "dist", "__pycache__", ".pytest_cache"),
    )
    subprocess.run(["git", "-C", str(repo), "init"], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.email", "sim@example.invalid"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.name", "SIM Test"],
        check=True,
    )
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-m", "source one"],
        check=True,
        capture_output=True,
    )
    first_sha = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    candidate = tmp_path / "candidate"
    build_candidate(repo, first_sha, candidate)

    skill = repo / "production/sim/SKILL.md"
    skill.write_bytes(skill.read_bytes() + b"\nsource two\n")
    subprocess.run(["git", "-C", str(repo), "add", "production/sim/SKILL.md"], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-m", "source two"],
        check=True,
        capture_output=True,
    )
    second_sha = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    findings = validate_candidate(repo, candidate, second_sha)
    codes = _codes(findings)
    assert "SIM_PLUGIN_PROJECTION_BYTE_DRIFT" in codes
    assert first_sha != second_sha


def test_validator_report_returns_final_candidate_tree_identity(
    tmp_path: Path,
) -> None:
    from tools.validate_sim_plugin import validate_candidate_report

    candidate, source_sha, build_result = _build(tmp_path)
    report = validate_candidate_report(ROOT, candidate, source_sha)

    assert report["findings"] == []
    assert report["candidate_tree_sha256"] == build_result.candidate_tree_sha256


def test_validator_cli_prints_pass_only_for_clean_candidate(
    tmp_path: Path,
    capsys,
) -> None:
    from tools.validate_sim_plugin import main

    candidate, source_sha, _ = _build(tmp_path)
    result = main(
        [
            "check",
            "--repo-root",
            str(ROOT),
            "--source-sha",
            source_sha,
            "--candidate",
            str(candidate),
        ]
    )
    captured = capsys.readouterr()
    assert result == 0
    assert captured.out == "PASS\n"


def test_validator_rejects_plugin_provenance_source_commit_tamper(
    tmp_path: Path,
) -> None:
    from tools.validate_sim_plugin import validate_candidate

    candidate, source_sha, _ = _build(tmp_path)
    path = candidate / "provenance/plugin_manifest.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["source_commit"] = "0" * 40
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")

    assert "SIM_PLUGIN_SOURCE_SHA_INVALID" in _codes(
        validate_candidate(ROOT, candidate, source_sha)
    )


def test_validator_rejects_portable_plugin_version_drift(tmp_path: Path) -> None:
    from tools.validate_sim_plugin import validate_candidate

    candidate, source_sha, _ = _build(tmp_path)
    path = candidate / "plugin.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["version"] = "9.9.9"
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")

    assert "SIM_PLUGIN_IDENTITY_INVALID" in _codes(
        validate_candidate(ROOT, candidate, source_sha)
    )


def test_validator_rejects_compatibility_plugin_identity_drift(
    tmp_path: Path,
) -> None:
    from tools.validate_sim_plugin import validate_candidate

    candidate, source_sha, _ = _build(tmp_path)
    path = candidate / ".codex-plugin/plugin.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["name"] = "other"
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")

    assert "SIM_PLUGIN_IDENTITY_INVALID" in _codes(
        validate_candidate(ROOT, candidate, source_sha)
    )



def test_validator_rejects_undeclared_app_requirement(tmp_path: Path) -> None:
    from tools.validate_sim_plugin import validate_candidate

    candidate, source_sha, _ = _build(tmp_path)
    skill = candidate / "skills/sim/SKILL.md"
    skill.write_bytes(skill.read_bytes() + b"\nUNDECLARED_APP\n")

    findings = validate_candidate(ROOT, candidate, source_sha)
    assert "SIM_PLUGIN_FORBIDDEN_REQUIREMENT" in _codes(findings)
