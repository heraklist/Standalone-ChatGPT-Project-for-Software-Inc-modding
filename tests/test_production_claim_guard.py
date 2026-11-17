import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.guard_production_claims import (
    ALLOWLIST_PATH,
    current_hits,
    diff,
    load_allowlist,
)


def test_allowlist_snapshot_is_committed():
    assert ALLOWLIST_PATH.is_file(), "run: python tools/guard_production_claims.py --update"


def test_production_matches_reviewed_allowlist():
    assert diff(current_hits(), load_allowlist()) == []


def test_guard_detects_reintroduced_myth():
    allowed = load_allowlist()
    poisoned = {path: list(codes) for path, codes in current_hits().items()}
    poisoned.setdefault("knowledge/99_FAKE.md", []).append("INVENTED_BUILDINGS")
    errors = diff(poisoned, allowed)
    assert any("UNEXPECTED" in e and "INVENTED_BUILDINGS" in e for e in errors)


def test_guard_detects_stale_allowlist_entry():
    current = current_hits()
    inflated = {path: list(codes) for path, codes in load_allowlist().items()}
    inflated.setdefault("project-instructions/PROJECT_INSTRUCTIONS.md", []).append("GREEK_SEMICOLON")
    errors = diff(current, inflated)
    assert any("STALE" in e and "GREEK_SEMICOLON" in e for e in errors)
