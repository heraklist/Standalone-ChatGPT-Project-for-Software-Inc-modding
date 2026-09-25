from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas/vendor/agent-plugins/1.0.0/plugin.schema.json"
CHECKSUM = ROOT / "schemas/vendor/agent-plugins/1.0.0/SHA256SUM"


def test_agent_plugins_schema_is_vendored_and_checksum_bound() -> None:
    assert SCHEMA.is_file()
    assert CHECKSUM.is_file()
    expected = CHECKSUM.read_text(encoding="utf-8").split()[0]
    actual = hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    assert actual == expected


def test_official_schema_cli_rejects_unknown_root_field(tmp_path: Path) -> None:
    manifest = tmp_path / "plugin.json"
    manifest.write_text(
        json.dumps(
            {
                "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
                "name": "sim",
                "unknown": True,
            }
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools/validate_agent_plugin_schema.py"),
            str(manifest),
            "--schema",
            str(SCHEMA),
            "--checksum",
            str(CHECKSUM),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "Additional properties are not allowed" in result.stdout
