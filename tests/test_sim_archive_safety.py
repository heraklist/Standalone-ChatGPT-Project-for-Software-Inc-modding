from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "production/sim/manifests/archive-safety-policy.json"


def _policy() -> dict:
    return json.loads(POLICY.read_text(encoding="utf-8"))


def test_archive_safety_policy_has_concrete_positive_limits() -> None:
    policy = _policy()
    assert policy["schema_version"] == 1
    for key in (
        "max_archive_bytes",
        "max_entries",
        "max_total_uncompressed_bytes",
        "max_entry_uncompressed_bytes",
        "max_compression_ratio",
        "max_nested_depth",
        "max_cumulative_nested_uncompressed_bytes",
    ):
        assert isinstance(policy[key], (int, float))
        assert policy[key] > 0
    assert policy["windows_casefold_paths"] is True


def test_repository_owned_zip_fixtures_fit_archive_byte_budget() -> None:
    policy = _policy()
    fixtures = [ROOT / "archive/raw/knowledge.zip"]
    for fixture in fixtures:
        assert fixture.is_file()
        assert fixture.stat().st_size <= policy["max_archive_bytes"]
