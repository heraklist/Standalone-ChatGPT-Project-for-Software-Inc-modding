from __future__ import annotations

import hashlib
from pathlib import Path
import zipfile

import pytest


def tree_digest(root: Path) -> str:
    h = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        h.update(path.relative_to(root).as_posix().encode("utf-8"))
        h.update(path.read_bytes())
    return h.hexdigest()


def test_build_mod_zip_is_non_destructive_sorted_and_reports_sha(tmp_path: Path) -> None:
    from tools.build_mod_zip import build_mod_zip

    source = tmp_path / "mod"
    (source / "SoftwareTypes").mkdir(parents=True)
    (source / "z.txt").write_text("z", encoding="utf-8")
    (source / "SoftwareTypes" / "a.tyd").write_text("a", encoding="utf-8")
    before = tree_digest(source)
    output = tmp_path / "mod.zip"

    report = build_mod_zip(source, output)

    assert output.is_file()
    assert tree_digest(source) == before
    assert report["files"] == ["SoftwareTypes/a.tyd", "z.txt"]
    assert len(report["sha256"]) == 64
    with zipfile.ZipFile(output) as archive:
        assert archive.namelist() == report["files"]


def test_build_mod_zip_rejects_output_inside_source(tmp_path: Path) -> None:
    from tools.build_mod_zip import build_mod_zip

    source = tmp_path / "mod"
    source.mkdir()
    (source / "a.txt").write_text("a", encoding="utf-8")
    with pytest.raises(ValueError):
        build_mod_zip(source, source / "bad.zip")


def test_validate_package_tree_is_family_aware(tmp_path: Path) -> None:
    from tools.validate_mod_package import validate_package_tree

    (tmp_path / "SoftwareTypes").mkdir()
    (tmp_path / "SoftwareTypes" / "x.tyd").write_text("x", encoding="utf-8")
    assert validate_package_tree(tmp_path, ["DATA_TYD"]) == []

    errors = validate_package_tree(tmp_path, ["EDITOR_NATIVE"])
    assert any("no verified generic ZIP schema" in error for error in errors)


def test_build_mod_zip_rejects_symlink_to_outside(tmp_path: Path) -> None:
    from tools.build_mod_zip import build_mod_zip
    import os

    source = tmp_path / "mod"
    source.mkdir()
    outside = tmp_path / "outside-secret.txt"
    outside.write_text("EXTERNAL_SECRET", encoding="utf-8")
    try:
        os.symlink(outside, source / "inside-link.txt")
    except OSError as exc:
        pytest.skip(f"symlink creation unavailable: {exc}")

    with pytest.raises(ValueError):
        build_mod_zip(source, tmp_path / "mod.zip")


def test_build_mod_zip_is_reproducible_across_source_mtimes(tmp_path: Path) -> None:
    from tools.build_mod_zip import build_mod_zip
    import os

    source = tmp_path / "mod"
    source.mkdir()
    payload = source / "payload.txt"
    payload.write_text("same bytes", encoding="utf-8")

    os.utime(payload, (1_000_000_000, 1_000_000_000))
    first = build_mod_zip(source, tmp_path / "first.zip")

    os.utime(payload, (1_700_000_000, 1_700_000_000))
    second = build_mod_zip(source, tmp_path / "second.zip")

    assert first["sha256"] == second["sha256"]



def test_validate_package_report_does_not_imply_full_furniture_validation(
    tmp_path: Path,
) -> None:
    from tools.validate_mod_package import validate_package_tree_report

    result = validate_package_tree_report(tmp_path, ["FURNITURE"])
    assert result["coverage"]["FURNITURE"] in {"PARTIAL_STATIC", "UNSUPPORTED"}
    assert result["coverage"]["FURNITURE"] != "FULL_STATIC"
    assert set(result) == {"families", "coverage", "result", "checks"}


def test_validate_package_report_marks_building_editor_native_required(
    tmp_path: Path,
) -> None:
    from tools.validate_mod_package import validate_package_tree_report

    result = validate_package_tree_report(tmp_path, ["BUILDING"])
    assert result["coverage"]["BUILDING"] == "EDITOR_NATIVE_REQUIRED"
    assert result["result"] == "TOOLING_BLOCKED"


def test_validate_package_report_marks_data_tyd_full_static(
    tmp_path: Path,
) -> None:
    from tools.validate_mod_package import validate_package_tree_report

    (tmp_path / "SoftwareTypes").mkdir()
    (tmp_path / "SoftwareTypes" / "x.tyd").write_text("x", encoding="utf-8")

    result = validate_package_tree_report(tmp_path, ["DATA_TYD"])
    assert result["coverage"]["DATA_TYD"] == "FULL_STATIC"
    assert result["result"] == "PASS"
    assert any(check["id"] == "DATA_LAYOUT" for check in result["checks"])


def test_validation_coverage_is_explicit_for_known_package_families() -> None:
    from tools.validate_mod_package import validation_coverage

    assert validation_coverage("DATA_TYD") == "FULL_STATIC"
    for family in ("BUILDING", "BUILDING_BLUEPRINT", "HARDWARE_DESIGN", "EDITOR_NATIVE"):
        assert validation_coverage(family) == "EDITOR_NATIVE_REQUIRED"
    for family in ("FURNITURE", "MATERIALS", "LOCALIZATION", "CODE"):
        assert validation_coverage(family) != "FULL_STATIC"



def test_packaging_skill_exposes_validation_coverage_ceiling() -> None:
    root = Path(__file__).resolve().parents[1]
    text = (
        root
        / "production/sim/domains/compatibility-packaging/SKILL.md"
    ).read_text(encoding="utf-8")
    for phrase in (
        "FULL_STATIC",
        "UNSUPPORTED",
        "EDITOR_NATIVE_REQUIRED",
        "validate_package_tree_report",
        "must not be presented as fully validated",
    ):
        assert phrase in text
