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
