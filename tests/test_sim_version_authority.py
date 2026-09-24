from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def _manifest_version() -> str:
    return json.loads(
        (ROOT / "production/sim/manifests/sim-manifest.json").read_text(
            encoding="utf-8"
        )
    )["version"]


def test_sim_manifest_is_only_handwritten_version_authority() -> None:
    assert _manifest_version() == "0.2.3-preview"

    frontmatter = (
        (ROOT / "production/sim/SKILL.md")
        .read_text(encoding="utf-8")
        .split("---", 2)[1]
    )
    assert "version:" not in frontmatter


def test_generated_plugin_versions_follow_sim_manifest(tmp_path: Path) -> None:
    from tools.build_sim_plugin import build_candidate

    out = tmp_path / "candidate"
    build_candidate(ROOT, _head(), out)

    expected = _manifest_version()
    assert json.loads((out / "plugin.json").read_text(encoding="utf-8"))[
        "version"
    ] == expected
    assert json.loads(
        (out / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
    )["version"] == expected
