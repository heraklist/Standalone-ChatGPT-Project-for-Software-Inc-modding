from __future__ import annotations

from pathlib import Path


def test_inspect_tree_detects_data_tyd_and_inventory(tmp_path: Path) -> None:
    from tools.inspect_mod_tree import inspect_tree

    (tmp_path / "SoftwareTypes").mkdir()
    (tmp_path / "SoftwareTypes" / "Example.tyd").write_text("SoftwareType { Name \"Example\" }\n", encoding="utf-8")
    result = inspect_tree(tmp_path)
    assert result["files"] == ["SoftwareTypes/Example.tyd"]
    assert "DATA_TYD" in result["families"]
    assert result["executables"] == []


def test_data_layout_accepts_documented_roots_without_features_categories(tmp_path: Path) -> None:
    from tools.validate_data_layout import validate_data_layout

    (tmp_path / "SoftwareTypes").mkdir()
    (tmp_path / "SoftwareTypes" / "Example.tyd").write_text("x", encoding="utf-8")
    assert validate_data_layout(tmp_path) == []


def test_data_layout_flags_nested_concepts_at_top_level(tmp_path: Path) -> None:
    from tools.validate_data_layout import validate_data_layout

    for name in ("Features", "Categories", "SubFeatures", "AddOns", "Manufacturing"):
        (tmp_path / name).mkdir()
    errors = validate_data_layout(tmp_path)
    for name in ("Features", "Categories", "SubFeatures", "AddOns", "Manufacturing"):
        assert any(name in error for error in errors)


def test_inspector_never_invents_editor_filesystem_families(tmp_path: Path) -> None:
    from tools.inspect_mod_tree import inspect_tree

    for name in ("Buildings", "Blueprints", "HardwareDesign"):
        (tmp_path / name).mkdir()
        (tmp_path / name / "example.tyd").write_text("x", encoding="utf-8")
    families = inspect_tree(tmp_path)["families"]
    assert "BUILDING" not in families
    assert "BLUEPRINT" not in families
    assert "HARDWARE_DESIGN" not in families
