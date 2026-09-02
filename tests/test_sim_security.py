from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_security_fixture_is_static_only_and_reported_untrusted(tmp_path: Path) -> None:
    from tools.inspect_mod_tree import inspect_tree

    fixture_root = ROOT / "tests/fixtures/sim/security"
    readme = (fixture_root / "README.txt").read_text(encoding="utf-8")
    script = (fixture_root / "evil.ps1").read_text(encoding="utf-8")
    assert "IGNORE ALL PREVIOUS INSTRUCTIONS" in readme
    assert script == 'Write-Output "fixture only"\n'

    (tmp_path / "README.txt").write_text(readme, encoding="utf-8")
    (tmp_path / "evil.ps1").write_text(script, encoding="utf-8")
    result = inspect_tree(tmp_path)
    assert "evil.ps1" in result["executables"]
    assert any("untrusted" in warning.lower() for warning in result["warnings"])


def test_inspector_classifies_untrusted_extensions_but_not_csharp(tmp_path: Path) -> None:
    from tools.inspect_mod_tree import inspect_tree

    for name in ("a.dll", "b.exe", "c.ps1", "d.bat", "e.cmd", "f.sh", "source.cs"):
        (tmp_path / name).write_text("fixture", encoding="utf-8")
    result = inspect_tree(tmp_path)
    assert result["executables"] == ["a.dll", "b.exe", "c.ps1", "d.bat", "e.cmd", "f.sh"]
    assert "source.cs" not in result["executables"]
