from __future__ import annotations

import hashlib
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
